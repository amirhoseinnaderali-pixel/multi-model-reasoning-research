from .protocols import StrategySpec

class CollaborationEngine:
    """Execute an explicit collaboration protocol under a hard inference budget."""

    def __init__(self, adapters, budget):
        self.adapters = adapters
        self.budget = budget
        self.last_trace = []

    def _prompt_for_role(self, condition, semantic_role, generation_kwargs, fallback_system_prompt):
        by_condition = generation_kwargs.get("role_prompts_by_condition", {})
        specs = by_condition.get(condition, generation_kwargs.get("role_prompts", {}))
        spec = specs.get(semantic_role)
        if spec is None:
            return fallback_system_prompt, "legacy-system-prompt", None
        return spec["text"], spec["version"], spec.get("path")

    def _generate(
        self, condition, role, semantic_role, prompt, fallback_system_prompt,
        generation_kwargs, seed_override=None, round_index=1
    ):
        role_cfg = dict(generation_kwargs.get("model_configs", {}).get(role, generation_kwargs))
        max_tokens = int(role_cfg["max_tokens"])
        price_in = float(role_cfg.get("usd_per_1k_input_tokens", 0.0))
        price_out = float(role_cfg.get("usd_per_1k_output_tokens", 0.0))
        worst_case_cost = (
            max_tokens * price_out / 1000.0
            + float(role_cfg.get("max_input_tokens", 0)) * price_in / 1000.0
        )
        worst_case_seconds = float(generation_kwargs.get("worst_case_seconds", 0.0))

        if seed_override is not None:
            role_cfg["seed"] = int(seed_override)

        self.budget.reserve_call(
            requested_output_tokens=max_tokens,
            worst_case_seconds=worst_case_seconds,
            estimated_cost_usd=worst_case_cost,
        )
        system_prompt, prompt_version, prompt_path = self._prompt_for_role(
            condition, semantic_role, generation_kwargs, fallback_system_prompt
        )
        try:
            call_kwargs = {
                k: v for k, v in role_cfg.items()
                if k in {"model_id", "temperature", "top_p", "max_tokens", "seed"}
            }
            res = self.adapters[role].generate(
                prompt=prompt,
                system_prompt=system_prompt,
                **call_kwargs,
            )
            actual_cost = (
                res.input_tokens * price_in / 1000.0
                + res.output_tokens * price_out / 1000.0
            )
            self.budget.settle_call(
                actual_output_tokens=res.output_tokens,
                actual_cost_usd=actual_cost,
                actual_wall_seconds=res.latency_seconds,
                reserved_output_tokens=max_tokens,
                reserved_wall_seconds=worst_case_seconds,
                reserved_cost_usd=worst_case_cost,
            )
            self.last_trace.append({
                "event": "model_call",
                "condition": condition,
                "model_role": role,
                "semantic_role": semantic_role,
                "model_id": res.model_id,
                "seed": int(role_cfg["seed"]),
                "round": int(round_index),
                "order": len([e for e in self.last_trace if e.get("event")=="model_call"]) + 1,
                "prompt_version": prompt_version,
                "prompt_path": prompt_path,
                "input_tokens": res.input_tokens,
                "output_tokens": res.output_tokens,
                "latency_seconds": res.latency_seconds,
                "estimated_cost_usd": actual_cost,
            })
            return res
        except Exception:
            self.budget.settle_call(
                actual_output_tokens=0,
                actual_cost_usd=0.0,
                reserved_output_tokens=max_tokens,
                reserved_wall_seconds=worst_case_seconds,
                reserved_cost_usd=worst_case_cost,
            )
            raise

    def run(self, *, spec: StrategySpec, problem, system_prompt, generation_kwargs, verifier=None):
        outputs = []
        self.last_trace = []

        if spec.condition == "C5":
            required = {"solver", "critic", "verifier", "synthesizer"}
            missing = required - set(generation_kwargs.get("role_prompts", {}))
            if missing:
                raise RuntimeError(f"C5 requires versioned prompts for semantic roles: {sorted(missing)}")
            if any(role not in generation_kwargs.get("model_configs", {}) for role in ("A", "B", "C", "D")):
                raise RuntimeError("C5 requires explicit model configuration for A/B/C/D")

        if spec.condition in {"C0", "C1", "C2"}:
            roles = (
                list(spec.model_pool)
                if spec.condition == "C2"
                else [spec.model_pool[0]] * spec.calls_per_task
            )
            for index, role in enumerate(roles):
                semantic_role = spec.semantic_roles[index] if index < len(spec.semantic_roles) else "solver"
                seed_override = None
                if spec.condition == "C1":
                    # Distinct deterministic seeds preserve independence within one task/run.
                    base_seed = int(generation_kwargs["model_configs"][role]["seed"])
                    seed_override = base_seed + index
                outputs.append(
                    self._generate(
                        spec.condition, role, semantic_role, problem, system_prompt,
                        generation_kwargs, seed_override=seed_override, round_index=1
                    )
                )

            if spec.condition == "C0":
                final = outputs[0].text
            else:
                if verifier is None or not hasattr(verifier, "select_visible"):
                    raise RuntimeError(f"{spec.condition} requires independent objective visible-test selection")
                final = verifier.select_visible([x.text for x in outputs])
                self.last_trace.append({
                    "event": "objective_selection",
                    "condition": spec.condition,
                    "selection_split": "visible",
                    "candidate_count": len(outputs),
                })

        elif spec.condition == "C3":
            a = self._generate(spec.condition, "A", "solver", problem, system_prompt, generation_kwargs, round_index=1)
            b = self._generate(
                spec.condition, "B",
                "critic",
                problem + "\n\nCANDIDATE:\n" + a.text,
                system_prompt,
                generation_kwargs,
            )
            c = self._generate(
                spec.condition, "A",
                "solver",
                problem + "\n\nCANDIDATE:\n" + a.text
                + "\n\nCRITIQUE:\n" + b.text,
                system_prompt,
                generation_kwargs,
            )
            outputs = [a, b, c]
            final = c.text

        elif spec.condition == "C4":
            context = problem
            for role, semantic_role in zip(spec.model_pool, spec.semantic_roles):
                res = self._generate(spec.condition, role, semantic_role, context, system_prompt, generation_kwargs, round_index=len(outputs)+1)
                outputs.append(res)
                context += "\n\nPREVIOUS OUTPUT:\n" + res.text
            final = outputs[-1].text

        elif spec.condition == "C5":
            solver = self._generate(spec.condition, "A", "solver", problem, system_prompt, generation_kwargs, round_index=1)
            critic = self._generate(
                spec.condition, "B", "critic",
                problem
                + "\n\nCANDIDATE SOLUTION:\n" + solver.text,
                system_prompt, generation_kwargs,
            )
            verifier = self._generate(
                spec.condition, "C", "verifier",
                problem
                + "\n\nCANDIDATE SOLUTION:\n" + solver.text
                + "\n\nCRITIQUE:\n" + critic.text,
                system_prompt, generation_kwargs,
            )
            synthesizer = self._generate(
                spec.condition, "D", "synthesizer",
                problem
                + "\n\nCANDIDATE SOLUTION:\n" + solver.text
                + "\n\nCRITIQUE:\n" + critic.text
                + "\n\nVERIFICATION NOTES:\n" + verifier.text,
                system_prompt, generation_kwargs,
            )
            outputs = [solver, critic, verifier, synthesizer]
            final = synthesizer.text

        elif spec.condition == "C6":
            required = {"solver", "critic", "synthesizer"}
            specs = generation_kwargs.get("role_prompts_by_condition", {}).get("C6", {})
            missing = required - set(specs)
            if missing:
                raise RuntimeError(f"C6 requires versioned prompts for semantic roles: {sorted(missing)}")
            if any(role not in generation_kwargs.get("model_configs", {}) for role in ("A", "B", "C")):
                raise RuntimeError("C6 requires explicit model configuration for A/B/C")

            initial = self._generate(
                spec.condition, "A", "solver", problem, system_prompt,
                generation_kwargs, round_index=1
            )
            critique_prompt = (
                problem
                + "\n\nCANDIDATE FROM MODEL A:\n" + initial.text
            )
            critique = self._generate(
                spec.condition, "B", "critic", critique_prompt, system_prompt,
                generation_kwargs, round_index=2
            )
            synthesis_prompt = (
                problem
                + "\n\nINITIAL CANDIDATE FROM MODEL A:\n" + initial.text
                + "\n\nCRITIQUE/REFINEMENT FROM MODEL B:\n" + critique.text
            )
            revised = self._generate(
                spec.condition, "C", "synthesizer", synthesis_prompt, system_prompt,
                generation_kwargs, round_index=3
            )
            outputs = [initial, critique, revised]

            if verifier is None or not hasattr(verifier, "select_visible"):
                raise RuntimeError("C6 requires independent objective visible-test selection")

            # B is critique, not a candidate artifact. Selection compares the
            # initial executable candidate A with the revised executable candidate C.
            final = verifier.select_visible([initial.text, revised.text])
            self.last_trace.append({
                "event": "objective_selection",
                "condition": spec.condition,
                "selection_split": "visible",
                "candidate_count": 2,
                "candidate_sources": ["A:initial", "C:revised"],
            })

        else:
            raise ValueError(spec.condition)

        return final, outputs
