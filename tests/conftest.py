from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
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


def records_by_string_id(
    records: Iterable[Any],
    *,
    id_attr: str,
    duplicate_error: Callable[[tuple[str, ...]], Exception] | None = None,
) -> dict[str, Any]:
    record_entries = tuple(records)
    duplicate_ids = duplicate_string_ids(getattr(record, id_attr) for record in record_entries)
    if duplicate_ids:
        if duplicate_error is not None:
            raise duplicate_error(duplicate_ids)
        raise AssertionError(f"{id_attr} values must be unique; duplicate ids: {list(duplicate_ids)}")
    return {getattr(record, id_attr): record for record in record_entries}


def manifest_records_by_id(manifests: Iterable[Any]) -> dict[str, Any]:
    return records_by_string_id(
        manifests,
        id_attr="manifest_id",
        duplicate_error=lambda duplicate_ids: AssertionError(
            "manifest ids must be unique; duplicate ids: "
            f"{list(duplicate_ids)}"
        ),
    )


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


def completed_process(
    *args: str,
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=args,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def report_path_from_cli_args(cli_args: list[str] | tuple[str, ...]) -> pathlib.Path:
    report_indexes = [
        index for index, argument in enumerate(cli_args) if argument == "--report"
    ]
    if len(report_indexes) != 1:
        raise ValueError("cli args must include exactly one --report argument")

    report_index = report_indexes[0]
    if report_index + 1 >= len(cli_args):
        raise ValueError("--report must be followed by a path")

    return pathlib.Path(cli_args[report_index + 1])


def fake_harness_cli_scorecard_result(
    module_name: str,
    cli_args: list[str] | tuple[str, ...],
    *,
    summary: dict[str, Any],
    report_text: str,
    process_args: tuple[str, ...] | None = None,
) -> subprocess.CompletedProcess[str]:
    report_path = report_path_from_cli_args(cli_args)
    report_path.write_text(report_text, encoding="utf-8")
    if process_args is None:
        process_args = ("python", "-m", module_name)
    return completed_process(*process_args, stdout=json.dumps(summary))


def run_harness_scorecard(
    module_name: str,
    cli_args: Iterable[str],
    *,
    report_name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    cli_args_list = list(cli_args)
    if "--report" in cli_args_list:
        raise ValueError(
            "run_harness_scorecard manages its own --report argument; "
            "omit it from cli_args"
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = pathlib.Path(temp_dir) / report_name
        result = run_harness_cli(
            module_name,
            [*cli_args_list, "--report", str(report_path)],
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
