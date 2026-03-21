from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
import importlib
import json
import pathlib
import subprocess
import sys
import tempfile
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


def duplicate_items(counter: Counter[str]) -> list[str]:
    return sorted(item for item, count in counter.items() if count > 1)


def duplicate_string_ids(items: Iterable[str]) -> tuple[str, ...]:
    return tuple(duplicate_items(Counter(items)))


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
        if report_path.suffix == ".json":
            scorecard = json.loads(report_path.read_text(encoding="utf-8"))
        else:
            try:
                module = importlib.import_module(module_name)
                load_report = module.SCORECARD_REPORT.load
            except (ImportError, AttributeError) as exc:
                raise ValueError(
                    f"run_harness_scorecard cannot load a non-JSON report for {module_name!r}"
                ) from exc
            scorecard = load_report(report_path)

    return summary, scorecard
