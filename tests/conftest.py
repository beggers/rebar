from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
import importlib
import json
import pathlib
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


def duplicate_items(counter: Counter[str]) -> list[str]:
    return sorted(item for item, count in counter.items() if count > 1)


def duplicate_string_ids(items: Iterable[str]) -> tuple[str, ...]:
    return tuple(duplicate_items(Counter(items)))


def declared_string_constants_by_suffix(
    module: ModuleType,
    *,
    name_suffix: str,
) -> dict[str, str]:
    return {
        name: value
        for name, value in vars(module).items()
        if name.endswith(name_suffix) and isinstance(value, str)
    }


def assert_published_manifest_helper_contract(
    published_loader: Callable[[], object],
    *,
    expected_paths: tuple[pathlib.Path, ...],
    expected_manifest_ids: tuple[str, ...] | None = None,
    observed_load_calls: list[tuple[pathlib.Path, ...]] | None = None,
) -> object:
    manifests = published_loader()

    assert published_loader() is manifests
    assert tuple(manifest.path for manifest in manifests) == expected_paths

    if expected_manifest_ids is not None:
        assert tuple(manifest.manifest_id for manifest in manifests) == expected_manifest_ids

    if observed_load_calls is not None:
        assert observed_load_calls == [expected_paths]

    return manifests


def assert_published_manifest_helper_reload_contract(
    published_loader: Callable[[], object],
    *,
    clear_cache: Callable[[], None],
    expected_paths: tuple[pathlib.Path, ...],
    expected_manifest_ids: tuple[str, ...] | None = None,
    observed_load_calls: list[tuple[pathlib.Path, ...]] | None = None,
) -> object:
    clear_cache()
    try:
        return assert_published_manifest_helper_contract(
            published_loader,
            expected_paths=expected_paths,
            expected_manifest_ids=expected_manifest_ids,
            observed_load_calls=observed_load_calls,
        )
    finally:
        clear_cache()


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
    report_index = cli_args.index("--report")
    return pathlib.Path(cli_args[report_index + 1])


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
