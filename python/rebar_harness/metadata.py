"""Shared runtime metadata helpers for rebar harness reports."""

from __future__ import annotations

import platform
import sys
from typing import Any


def build_cpython_baseline(*, version_family: str) -> dict[str, Any]:
    """Collect exact interpreter provenance for scorecard baselines."""

    build_name, build_date = platform.python_build()
    return {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "python_version_family": version_family,
        "python_build": {
            "name": build_name,
            "date": build_date,
        },
        "python_compiler": platform.python_compiler(),
        "platform": platform.platform(),
        "executable": sys.executable,
        "re_module": "re",
    }
