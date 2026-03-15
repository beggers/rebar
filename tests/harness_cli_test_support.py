from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PYTHON_SOURCE = REPO_ROOT / "python"
REBAR_OPS_MODULE_PATH = REPO_ROOT / "scripts" / "rebar_ops.py"


def load_rebar_ops_module(module_name: str = "rebar_ops_for_tests") -> object:
    spec = importlib.util.spec_from_file_location(module_name, REBAR_OPS_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {REBAR_OPS_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_harness_cli(
    module_name: str,
    cli_args: Iterable[str],
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, "-m", module_name, *cli_args]
    return subprocess.run(
        command,
        check=check,
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(PYTHON_SOURCE)},
        capture_output=True,
        text=True,
    )


def run_harness_scorecard(
    module_name: str,
    cli_args: Iterable[str],
    *,
    report_name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = pathlib.Path(temp_dir) / report_name
        result = run_harness_cli(
            module_name,
            [*cli_args, "--report", str(report_path)],
        )
        summary = json.loads(result.stdout.strip())
        scorecard = json.loads(report_path.read_text(encoding="utf-8"))

    return summary, scorecard
