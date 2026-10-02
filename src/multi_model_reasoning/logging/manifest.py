from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass(frozen=True)
class RunManifest:
    experiment_id: str
    run_id: str
    git_sha: str
    config_hash: str
    benchmark_hash: str
    model_config_hash: str
    strategy: str
    seed: int
    budget: dict
    timestamp_utc: str
    python_version: str
    platform: str
    package_versions: dict
    docker_digest: str
    run_scope: str

    @classmethod
    def create(cls, **kwargs):
        return cls(
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            python_version=sys.version,
            platform=platform.platform(),
            package_versions=installed_package_versions(),
            **kwargs,
        )

    def to_dict(self):
        return asdict(self)


def installed_package_versions():
    names = ("openai", "pytest")
    result = {}
    for name in names:
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = "NOT_INSTALLED"
    return result


def hash_json(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def git_sha():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        return "UNKNOWN"
