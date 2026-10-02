.PHONY: test dry-run audit preflight

test:
	python -m pytest

dry-run:
	python scripts/run_experiment.py --config configs/experiments/exp001_fixed_budget.json --mode validation_only

audit:
	python scripts/scientific_audit.py

preflight:
	python scripts/preflight.py --config configs/experiments/exp001_fixed_budget.json
