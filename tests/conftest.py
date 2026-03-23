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


def manifest_records_by_id(manifests: Iterable[Any]) -> dict[str, Any]:
    manifest_records = tuple(manifests)
    duplicate_manifest_ids = duplicate_string_ids(
        manifest.manifest_id for manifest in manifest_records
    )
    if duplicate_manifest_ids:
        raise AssertionError(
            "manifest ids must be unique; duplicate ids: "
            f"{list(duplicate_manifest_ids)}"
        )
    return {manifest.manifest_id: manifest for manifest in manifest_records}


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


def assert_declared_string_selector_registry_contract(
    module: ModuleType,
    *,
    name_suffix: str,
    selector_registry: dict[str, object],
) -> dict[str, str]:
    declared_selectors = declared_string_constants_by_suffix(
        module,
        name_suffix=name_suffix,
    )

    assert declared_selectors
    assert len(declared_selectors) == len(set(declared_selectors.values()))
    assert set(declared_selectors.values()) == set(selector_registry)
    return declared_selectors


def assert_published_selector_subset_paths_contract(
    published_full_suite_paths: tuple[pathlib.Path, ...],
    resolved_paths: tuple[pathlib.Path, ...],
    *,
    root_path: pathlib.Path,
    expected_filenames: tuple[str, ...] | None = None,
) -> None:
    assert resolved_paths
    assert len(resolved_paths) == len(set(resolved_paths))

    if expected_filenames is None:
        expected_ordered_subset = tuple(
            path for path in published_full_suite_paths if path in set(resolved_paths)
        )
    else:
        expected_filename_set = set(expected_filenames)
        assert len(expected_filenames) == len(expected_filename_set)
        expected_ordered_subset = tuple(
            path
            for path in published_full_suite_paths
            if path.name in expected_filename_set
        )
        assert tuple(path.name for path in expected_ordered_subset) == expected_filenames
        assert tuple(path.name for path in resolved_paths) == expected_filenames

    assert expected_ordered_subset
    assert len(expected_ordered_subset) == len(resolved_paths)
    assert resolved_paths == expected_ordered_subset

    for path in resolved_paths:
        assert path.is_relative_to(root_path)
        assert path.is_file()
        assert path.suffix == ".py"
        assert path in published_full_suite_paths


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


def _resolve_inventory_value(
    record: Any,
    accessor: str | Callable[[Any], Any],
) -> Any:
    if callable(accessor):
        return accessor(record)
    return getattr(record, accessor)


def assert_published_manifest_inventory_contract(
    manifests: Iterable[Any],
    *,
    child_records: str | Callable[[Any], Iterable[Any]],
    child_id: str | Callable[[Any], str],
    extra_manifest_unique_fields: Iterable[str | Callable[[Any], str]] = (),
    manifest_id: str | Callable[[Any], str] = "manifest_id",
    child_manifest_id: str | Callable[[Any], str] = "manifest_id",
) -> tuple[Any, ...]:
    manifest_records = tuple(manifests)
    assert manifest_records

    manifest_ids = tuple(
        _resolve_inventory_value(manifest, manifest_id)
        for manifest in manifest_records
    )
    assert duplicate_string_ids(manifest_ids) == ()

    for field in extra_manifest_unique_fields:
        assert duplicate_string_ids(
            _resolve_inventory_value(manifest, field) for manifest in manifest_records
        ) == ()

    child_entries = tuple(
        child
        for manifest in manifest_records
        for child in _resolve_inventory_value(manifest, child_records)
    )
    assert duplicate_string_ids(
        _resolve_inventory_value(child, child_id) for child in child_entries
    ) == ()

    manifest_ids_set = set(manifest_ids)
    child_counts_by_manifest = Counter(
        _resolve_inventory_value(child, child_manifest_id) for child in child_entries
    )

    for current_manifest_id in manifest_ids:
        assert child_counts_by_manifest[current_manifest_id] > 0

    for child in child_entries:
        assert _resolve_inventory_value(child, child_manifest_id) in manifest_ids_set

    return child_entries


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
