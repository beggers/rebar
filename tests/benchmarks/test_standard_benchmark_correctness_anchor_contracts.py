from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from functools import cache
import json
import pathlib
import re
import shutil
import sys
import textwrap
from types import SimpleNamespace
from typing import Any
from unittest import mock

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
REGRESSION_MATRIX_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"
)
OPTIONAL_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.py"
)
NESTED_GROUP_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py"
EXACT_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "exact_repeat_quantified_group_boundary.py"
)
RANGED_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "ranged_repeat_quantified_group_boundary.py"
)
GROUPED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py"
)
GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_replacement_boundary.py"
)
NESTED_GROUP_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_replacement_boundary.py"
)
OPEN_ENDED_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "open_ended_quantified_group_boundary.py"
)

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR,
    COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR,
    PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
    build_callable,
    load_manifest,
    load_manifests,
    published_benchmark_manifests,
    run_internal_workload_probe,
    select_benchmark_manifest_path,
    select_benchmark_manifest_paths,
    workload_to_payload,
)
from rebar_harness.correctness import published_fixture_manifests
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    assert_match_result_parity,
    assert_pattern_parity,
)

support = sys.modules[__name__]
MATURIN = shutil.which("maturin")
COMPILE_SMOKE_PROVENANCE_MANIFEST_PATH = select_benchmark_manifest_path(
    COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR
)
_MISSING_MATURIN_REASON = (
    "built-native mode unavailable because no `maturin` executable was found on PATH"
)
_MISSING_MATURIN_PATTERN = "no `maturin` executable was found on PATH"


@pytest.fixture
def anchor_support_cache_guard() -> None:
    _clear_anchor_support_caches()
    yield
    _clear_anchor_support_caches()


def _clear_anchor_support_caches() -> None:
    for cached_function in (
        support._manifest_workloads,
        support.published_case_ids_by_signature,
        support.published_cases_by_id,
    ):
        cache_clear = getattr(cached_function, "cache_clear", None)
        if cache_clear is not None:
            cache_clear()


def _synthetic_manifest(
    *,
    cases: tuple[object, ...] = (),
    workloads: tuple[object, ...] = (),
) -> SimpleNamespace:
    return SimpleNamespace(cases=list(cases), workloads=list(workloads))


def _synthetic_case(
    case_id: str,
    signature: tuple[object, ...] | None,
) -> SimpleNamespace:
    return SimpleNamespace(case_id=case_id, signature=signature)


def _synthetic_workload(
    workload_id: str,
    signature: tuple[object, ...],
    *,
    include: bool = True,
) -> SimpleNamespace:
    return SimpleNamespace(workload_id=workload_id, signature=signature, include=include)


def _duplicate_items(counter: Counter[str]) -> list[str]:
    return sorted(item for item, count in counter.items() if count > 1)


def _tracked_benchmark_manifest_paths() -> tuple[pathlib.Path, ...]:
    return tuple(sorted(BENCHMARK_WORKLOADS_ROOT.glob("*.py"), key=lambda path: path.name))


def _write_test_manifest(
    tmp_path: pathlib.Path,
    filename: str,
    source: str,
) -> pathlib.Path:
    path = tmp_path / filename
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


def _build_minimal_built_native_scorecard() -> dict[str, object]:
    return {
        "summary": {
            "total_workloads": 0,
            "parser_workloads": 0,
            "module_workloads": 0,
            "regression_workloads": 0,
            "measured_workloads": 0,
            "known_gap_count": 0,
        }
    }


def _assert_built_native_runner_uses_optional_report_path(
    *,
    runner: Callable[..., dict[str, object]],
    expected_manifest_selector: str,
    expected_smoke_only: bool,
) -> None:
    expected_manifest_paths = select_benchmark_manifest_paths(expected_manifest_selector)
    scorecard = _build_minimal_built_native_scorecard()
    explicit_report_path = (
        REPO_ROOT / "reports" / "benchmarks" / "explicit-native-check.json"
    )

    with mock.patch.object(benchmarks, "run_benchmarks", return_value=scorecard) as mocked_run:
        returned = runner()

    assert returned is scorecard
    mocked_run.assert_called_once_with(
        manifest_paths=list(expected_manifest_paths),
        report_path=None,
        smoke_only=expected_smoke_only,
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        allow_fallback=False,
    )

    with mock.patch.object(benchmarks, "run_benchmarks", return_value=scorecard) as mocked_run:
        returned = runner(report_path=explicit_report_path)

    assert returned is scorecard
    mocked_run.assert_called_once_with(
        manifest_paths=list(expected_manifest_paths),
        report_path=explicit_report_path,
        smoke_only=expected_smoke_only,
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        allow_fallback=False,
    )


def _assert_built_native_cli_uses_optional_report_path(
    tmp_path: pathlib.Path,
    *,
    flag: str,
    runner_name: str,
    report_name: str,
) -> None:
    scorecard = _build_minimal_built_native_scorecard()

    with (
        mock.patch.object(benchmarks, runner_name, return_value=scorecard) as mocked_runner,
        mock.patch("builtins.print"),
    ):
        exit_code = benchmarks.main([flag])

    assert exit_code == 0
    mocked_runner.assert_called_once_with(report_path=None)

    report_path = tmp_path / report_name
    with (
        mock.patch.object(benchmarks, runner_name, return_value=scorecard) as mocked_runner,
        mock.patch("builtins.print"),
    ):
        exit_code = benchmarks.main([flag, "--report", str(report_path)])

    assert exit_code == 0
    mocked_runner.assert_called_once_with(report_path=report_path)


def _assert_built_native_mode_requires_real_built_runtime(
    report_path: pathlib.Path,
    *,
    runner: Callable[..., dict[str, object]],
) -> None:
    with mock.patch.object(
        benchmarks,
        "provision_built_native_runtime",
        return_value=(None, None, _MISSING_MATURIN_REASON),
    ):
        with pytest.raises(
            benchmarks.NativeBenchmarkProvisionError,
            match=_MISSING_MATURIN_PATTERN,
        ):
            runner(report_path=report_path)

    assert not report_path.exists()


def _assert_built_native_combined_scorecard_fields(
    scorecard: dict[str, object],
    *,
    expected_phase: str,
    expected_selection_mode: str,
    expected_manifest_count: int,
) -> None:
    implementation = scorecard["implementation"]
    environment = scorecard["environment"]
    artifacts = scorecard["artifacts"]

    assert scorecard["schema_version"] == "1.0"
    assert scorecard["phase"] == expected_phase
    assert implementation["module_name"] == "rebar"
    assert implementation["adapter_mode_requested"] == "built-native"
    assert implementation["adapter_mode_resolved"] == "built-native"
    assert implementation["build_mode"] == "built-native"
    assert implementation["timing_path"] == "built-native"
    assert implementation["native_module_loaded"] is True
    assert implementation["native_module_name"] == "rebar._rebar"
    assert implementation["native_build_tool"] == "maturin"
    assert str(implementation["native_wheel"]).startswith("rebar-")
    assert implementation["native_unavailable_reason"] is None
    assert (
        environment["execution_model"]
        == "single-interpreter subprocess workload probes against a built native wheel"
    )
    assert artifacts["manifest"] is None
    assert artifacts["manifest_id"] == "combined-benchmark-suite"
    assert artifacts["selection_mode"] == expected_selection_mode
    assert len(artifacts["manifests"]) == expected_manifest_count


# Local anchor helpers stay in this file because this test module is their only consumer.
@dataclass(frozen=True, slots=True)
class AnchoredWorkloadCasePair:
    manifest_name: str
    workload_id: str
    case_id: str
    workload: Any
    case: Any


def freeze_signature_value(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(
            (str(key), freeze_signature_value(nested_value))
            for key, nested_value in sorted(value.items())
        )
    if isinstance(value, list):
        return tuple(freeze_signature_value(item) for item in value)
    return value


@cache
def published_case_ids_by_signature(
    case_signature: Callable[[Any], tuple[Any, ...] | None],
) -> dict[tuple[Any, ...], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[Any, ...], list[str]] = {}

    for case in published_cases_by_id().values():
        signature = case_signature(case)
        if signature is None:
            continue
        case_ids_by_signature.setdefault(signature, []).append(case.case_id)

    return {
        signature: tuple(sorted(case_ids))
        for signature, case_ids in case_ids_by_signature.items()
    }


@cache
def published_cases_by_id() -> dict[str, Any]:
    cases_by_id: dict[str, Any] = {}

    for manifest in published_fixture_manifests():
        for case in manifest.cases:
            if case.case_id in cases_by_id:
                raise AssertionError(
                    f"duplicate published correctness case id {case.case_id!r}"
                )
            cases_by_id[case.case_id] = case

    return cases_by_id


@cache
def _manifest_workloads(manifest_path: pathlib.Path) -> tuple[Any, ...]:
    return tuple(load_manifest(manifest_path).workloads)


def _selected_manifest_workloads(
    manifest_path: pathlib.Path,
    *,
    include_workload: Callable[[Any], bool] | None = None,
) -> tuple[Any, ...]:
    workloads = _manifest_workloads(manifest_path)
    if include_workload is None:
        return workloads

    return tuple(workload for workload in workloads if include_workload(workload))


def anchored_workload_case_ids(
    manifest_path: pathlib.Path,
    *,
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]],
    workload_signature: Callable[[Any], tuple[Any, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> dict[tuple[str, str], tuple[str, ...]]:
    workloads = _selected_manifest_workloads(
        manifest_path,
        include_workload=include_workload,
    )

    return {
        (manifest_path.name, workload.workload_id): anchor_case_ids.get(
            workload_signature(workload),
            (),
        )
        for workload in workloads
    }


def unanchored_workload_ids(
    manifest_path: pathlib.Path,
    *,
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]],
    workload_signature: Callable[[Any], tuple[Any, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> tuple[str, ...]:
    workloads = _selected_manifest_workloads(
        manifest_path,
        include_workload=include_workload,
    )

    return tuple(
        workload.workload_id
        for workload in workloads
        if workload_signature(workload) not in anchor_case_ids
    )


def expected_anchored_workload_case_pairs(
    manifest_path: pathlib.Path,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> tuple[AnchoredWorkloadCasePair, ...]:
    manifest_name = manifest_path.name
    workloads_by_id = {
        workload.workload_id: workload
        for workload in _selected_manifest_workloads(
            manifest_path,
            include_workload=include_workload,
        )
    }
    published_cases = published_cases_by_id()
    anchored_pairs: list[AnchoredWorkloadCasePair] = []

    for (expected_manifest_name, workload_id), case_ids in expected_anchor_case_ids.items():
        if expected_manifest_name != manifest_name:
            raise AssertionError(
                f"expected anchored manifest {expected_manifest_name!r} "
                f"does not match {manifest_name!r}"
            )
        if len(case_ids) != 1:
            raise AssertionError(
                "expected exactly one published correctness case for "
                f"{(expected_manifest_name, workload_id)!r}, got {case_ids!r}"
            )

        case_id = case_ids[0]
        if workload_id not in workloads_by_id:
            raise AssertionError(
                f"expected anchored workload {workload_id!r} to be in scope for "
                f"{manifest_name!r}"
            )
        if case_id not in published_cases:
            raise AssertionError(
                f"expected anchored correctness case {case_id!r} to be published"
            )

        anchored_pairs.append(
            AnchoredWorkloadCasePair(
                manifest_name=manifest_name,
                workload_id=workload_id,
                case_id=case_id,
                workload=workloads_by_id[workload_id],
                case=published_cases[case_id],
            )
        )

    return tuple(anchored_pairs)


def assert_anchored_workload_case_result_parity(
    anchored_pairs: Iterable[AnchoredWorkloadCasePair],
) -> None:
    for anchored_pair in anchored_pairs:
        expected = run_correctness_case_with_cpython(anchored_pair.case)
        assert_benchmark_workload_matches_expected_result(
            anchored_pair.workload,
            expected,
        )


def assert_benchmark_workload_matches_expected_result(
    workload: Any,
    expected: object,
) -> None:
    observed = run_benchmark_workload_with_cpython(workload)

    if workload.operation == "module.compile":
        assert_pattern_parity("stdlib", observed, expected)
        return

    if workload.operation in {"module.search", "pattern.fullmatch"}:
        assert_match_result_parity(
            "stdlib",
            observed,
            expected,
            check_regs=True,
        )
        return

    if workload.operation in {
        "module.sub",
        "module.subn",
        "pattern.sub",
        "pattern.subn",
    }:
        assert observed == expected
        return

    raise AssertionError(
        "unexpected anchored benchmark workload operation "
        f"{workload.operation!r}"
    )


def run_benchmark_workload_with_cpython(workload: Any) -> object:
    re.purge()
    callback = build_callable(re, "re", workload)
    result = callback()
    re.purge()
    return result


def run_correctness_case_with_cpython(case: Any) -> object:
    if case.operation == "compile":
        return re.compile(case.pattern_payload(), case.flags or 0)

    if case.operation == "module_call":
        if case.helper is None:
            raise AssertionError(f"expected helper for {case.case_id!r}")
        return getattr(re, case.helper)(*case.args, **case.kwargs)

    if case.operation == "pattern_call":
        if case.helper is None:
            raise AssertionError(f"expected helper for {case.case_id!r}")
        compiled = re.compile(case.pattern_payload(), case.flags or 0)
        return getattr(compiled, case.helper)(*case.args, **case.kwargs)

    raise AssertionError(f"unexpected correctness operation {case.operation!r}")


@dataclass(frozen=True, slots=True)
class StandardBenchmarkAnchorContractDefinition:
    name: str
    manifest_paths: tuple[pathlib.Path, ...]
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    include_workload: Callable[[Any], bool]
    correctness_case_signature: Callable[[Any], tuple[Any, ...] | None]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    run_callback_result_parity: bool = False
    expected_excluded_workload_ids: frozenset[str] = frozenset()
    expected_legacy_workload_ids: frozenset[str] = frozenset()
    expected_legacy_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] = field(
        default_factory=dict
    )
    callback_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] = field(
        default_factory=dict
    )
    expected_special_unanchored_workload_ids: tuple[str, ...] = ()
    direct_parity_supplemental_cases: tuple[Any, ...] = ()
    run_special_unanchored_result_parity: bool = False


EXPECTED_COMPILE_ANCHOR_CASE_IDS = {
    ("compile_matrix.py", "compile-inline-locale-bytes-warm"): (
        "bytes-inline-locale-flag-success",
    ),
    ("compile_matrix.py", "compile-lookbehind-cold"): (
        "str-fixed-width-lookbehind-success",
    ),
    ("compile_matrix.py", "compile-character-class-ignorecase-warm"): (
        "str-character-class-ignorecase-success",
    ),
    ("compile_matrix.py", "compile-possessive-quantifier-cold"): (
        "str-possessive-quantifier-success",
    ),
    ("compile_matrix.py", "compile-atomic-group-purged"): (
        "str-atomic-group-success",
    ),
    ("compile_matrix.py", "compile-parser-stress-cold"): (
        "str-parser-stress-compile-proxy-success",
    ),
    ("regression_matrix.py", "regression-parser-atomic-lookbehind-cold"): (
        "str-parser-stress-compile-proxy-success",
    ),
    ("regression_matrix.py", "regression-parser-bytes-backreference-purged"): (
        "bytes-named-backreference-compile-proxy-success",
    ),
    ("regression_matrix.py", "regression-module-compile-verbose-purged"): (
        "workflow-compile-str-verbose-regression",
    ),
}

OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID = (
    "module-search-numbered-optional-group-conditional-cold-gap"
)
EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS = {
    (
        "optional_group_boundary.py",
        OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID,
    ): ("optional-group-conditional-module-search-present-str",),
}

EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS = frozenset(
    {
        "module-search-triple-nested-group-cold-gap",
        "pattern-fullmatch-named-quantified-nested-group-purged-gap",
    }
)
EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS = {
    ("nested_group_boundary.py", "module-compile-nested-group-cold-str"): (
        "nested-group-compile-metadata-str",
    ),
    ("nested_group_boundary.py", "module-search-nested-group-warm-str"): (
        "nested-group-module-search-str",
    ),
    ("nested_group_boundary.py", "pattern-fullmatch-nested-group-purged-str"): (
        "nested-group-pattern-fullmatch-str",
    ),
    ("nested_group_boundary.py", "module-compile-named-nested-group-warm-str"): (
        "named-nested-group-compile-metadata-str",
    ),
    ("nested_group_boundary.py", "module-search-named-nested-group-warm-str"): (
        "named-nested-group-module-search-str",
    ),
    ("nested_group_boundary.py", "pattern-fullmatch-named-nested-group-purged-str"): (
        "named-nested-group-pattern-fullmatch-str",
    ),
}

EXACT_REPEAT_EXPECTED_ANCHOR_CASE_IDS = {
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-compile-numbered-exact-repeat-group-cold-str",
    ): ("exact-repeat-numbered-group-compile-metadata-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-search-numbered-exact-repeat-group-warm-str",
    ): ("exact-repeat-numbered-group-module-search-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-exact-repeat-group-purged-str",
    ): ("exact-repeat-numbered-group-pattern-fullmatch-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-compile-named-exact-repeat-group-warm-str",
    ): ("exact-repeat-named-group-compile-metadata-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-search-named-exact-repeat-group-warm-str",
    ): ("exact-repeat-named-group-module-search-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "pattern-fullmatch-named-exact-repeat-group-purged-str",
    ): ("exact-repeat-named-group-pattern-fullmatch-str",),
    (
        "exact_repeat_quantified_group_boundary.py",
        "module-search-numbered-broader-ranged-repeat-group-cold-gap",
    ): (
        "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
    ),
}

RANGED_REPEAT_EXPECTED_ANCHOR_CASE_IDS = {
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-compile-numbered-ranged-repeat-group-cold-str",
    ): ("ranged-repeat-numbered-group-compile-metadata-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-search-numbered-ranged-repeat-group-lower-bound-warm-str",
    ): ("ranged-repeat-numbered-group-module-search-lower-bound-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-ranged-repeat-group-upper-bound-purged-str",
    ): ("ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-compile-named-ranged-repeat-group-warm-str",
    ): ("ranged-repeat-named-group-compile-metadata-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-search-named-ranged-repeat-group-upper-bound-warm-str",
    ): ("ranged-repeat-named-group-module-search-upper-bound-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "pattern-fullmatch-named-ranged-repeat-group-lower-bound-purged-str",
    ): ("ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",),
    (
        "ranged_repeat_quantified_group_boundary.py",
        "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
    ): (
        "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
    ),
}

EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS = frozenset(
    {
        "module-sub-template-nested-grouped-alternation-warm-gap",
        "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
    }
)
EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS = {
    (
        "grouped_alternation_boundary.py",
        "module-compile-grouped-alternation-cold-str",
    ): ("grouped-alternation-compile-metadata-str",),
    (
        "grouped_alternation_boundary.py",
        "module-search-grouped-alternation-warm-str",
    ): ("grouped-alternation-module-search-str",),
    (
        "grouped_alternation_boundary.py",
        "pattern-fullmatch-grouped-alternation-purged-str",
    ): ("grouped-alternation-pattern-fullmatch-str",),
    (
        "grouped_alternation_boundary.py",
        "module-compile-named-grouped-alternation-warm-str",
    ): ("named-grouped-alternation-compile-metadata-str",),
    (
        "grouped_alternation_boundary.py",
        "module-search-named-grouped-alternation-warm-str",
    ): ("named-grouped-alternation-module-search-str",),
    (
        "grouped_alternation_boundary.py",
        "pattern-fullmatch-named-grouped-alternation-purged-str",
    ): ("named-grouped-alternation-pattern-fullmatch-str",),
    (
        "grouped_alternation_boundary.py",
        "module-sub-template-nested-grouped-alternation-warm-gap",
    ): ("module-sub-template-nested-group-alternation-numbered-wrapper-str",),
    (
        "grouped_alternation_boundary.py",
        "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
    ): (
        "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
    ),
}
EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS = {
    (
        "grouped_alternation_boundary.py",
        "module-sub-template-nested-grouped-alternation-warm-gap",
    ): ("module-sub-template-nested-group-alternation-numbered-wrapper-str",),
    (
        "grouped_alternation_boundary.py",
        "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
    ): (
        "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
    ),
}

EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_WORKLOAD_IDS = frozenset(
    {
        "module-sub-template-nested-grouped-alternation-cold-gap",
        "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
    }
)
EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS = {
    (
        "grouped_alternation_replacement_boundary.py",
        "module-sub-template-grouped-alternation-warm-str",
    ): ("module-sub-template-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "module-subn-template-grouped-alternation-warm-str",
    ): ("module-subn-template-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-sub-template-grouped-alternation-purged-str",
    ): ("pattern-sub-template-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-subn-template-grouped-alternation-purged-str",
    ): ("pattern-subn-template-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "module-sub-template-named-grouped-alternation-warm-str",
    ): ("module-sub-template-named-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "module-subn-template-named-grouped-alternation-warm-str",
    ): ("module-subn-template-named-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-sub-template-named-grouped-alternation-purged-str",
    ): ("pattern-sub-template-named-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-subn-template-named-grouped-alternation-purged-str",
    ): ("pattern-subn-template-named-grouped-alternation-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "module-sub-template-nested-grouped-alternation-cold-gap",
    ): ("module-sub-template-nested-group-alternation-numbered-outer-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
    ): (
        "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
    ),
}
EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_ANCHOR_CASE_IDS = {
    (
        "grouped_alternation_replacement_boundary.py",
        "module-sub-template-nested-grouped-alternation-cold-gap",
    ): ("module-sub-template-nested-group-alternation-numbered-outer-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
    ): (
        "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
    ),
}
EXPECTED_NESTED_GROUP_REPLACEMENT_ANCHOR_CASE_IDS = {
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-nested-group-numbered-warm-str",
    ): ("module-sub-template-nested-group-numbered-str",),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-nested-group-numbered-warm-str",
    ): ("module-subn-template-nested-group-numbered-str",),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-nested-group-numbered-purged-str",
    ): ("pattern-sub-template-nested-group-numbered-str",),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-nested-group-numbered-purged-str",
    ): ("pattern-subn-template-nested-group-numbered-str",),
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-nested-group-named-warm-str",
    ): ("module-sub-template-nested-group-named-str",),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-nested-group-named-warm-str",
    ): ("module-subn-template-nested-group-named-str",),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-nested-group-named-purged-str",
    ): ("pattern-sub-template-nested-group-named-str",),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-nested-group-named-purged-str",
    ): ("pattern-subn-template-nested-group-named-str",),
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-numbered-quantified-nested-group-replacement-lower-bound-warm-str",
    ): ("module-sub-template-quantified-nested-group-numbered-lower-bound-str",),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-numbered-quantified-nested-group-replacement-first-match-only-warm-str",
    ): ("module-subn-template-quantified-nested-group-numbered-first-match-only-str",),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-named-quantified-nested-group-replacement-repeated-outer-purged-str",
    ): ("pattern-sub-template-quantified-nested-group-named-repeated-outer-capture-str",),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap",
    ): ("pattern-subn-template-quantified-nested-group-named-first-match-only-str",),
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
    ): (
        "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
    ): (
        "module-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
    ): (
        "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
    ): (
        "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
    ): (
        "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
    ): (
        "module-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str",
    ): (
        "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
    ): (
        "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
    ): (
        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str",
    ): (
        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
    ): (
        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str",
    ): (
        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
    ): (
        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str",
    ): (
        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str",
    ): (
        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-str",
    ),
    (
        "nested_group_replacement_boundary.py",
        "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str",
    ): (
        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
    ),
}
EXPECTED_NESTED_GROUP_REPLACEMENT_SPECIAL_UNANCHORED_WORKLOAD_IDS = (
    "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
    "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
    "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
    "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
    "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
    "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
    "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
    "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
)

EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS = (
    "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
    "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
    "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
    "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
    "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
    "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
    "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
    "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
    "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
    "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
    "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes",
    "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
    "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
    "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
    "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
    "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
    "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
    "module-search-numbered-open-ended-group-conditional-warm-gap",
    "module-search-numbered-open-ended-group-conditional-second-repetition-bc-warm-bytes",
    "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
    "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-bytes",
    "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
    "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
    "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
    "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
    "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
)

EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS = {
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-alternation-cold-str",
    ): ("open-ended-quantified-group-alternation-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-str",
    ): ("open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-str",
    ): ("open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-alternation-warm-str",
    ): ("open-ended-quantified-group-alternation-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-alternation-lower-bound-de-warm-str",
    ): ("open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-str",
    ): ("open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-alternation-cold-bytes",
    ): ("open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-alternation-warm-bytes",
    ): ("open-ended-quantified-group-alternation-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-conditional-cold-str",
    ): ("open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-cold-str",
    ): ("broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-broader-range-cold-gap",
    ): (
        "broader-range-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-str",
    ): ("broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-warm-str",
    ): ("broader-range-open-ended-quantified-group-alternation-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-str",
    ): ("broader-range-open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-str",
    ): ("broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-cold-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-warm-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-conditional-cold-str",
    ): ("broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap",
    ): (
        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-conditional-warm-str",
    ): ("broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-str",
    ): ("broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-str",
    ): ("broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-str",
    ): (
        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes",
    ): ("broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-str",
    ): ("open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-conditional-warm-str",
    ): ("open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-str",
    ): ("open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-str",
    ): ("open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-conditional-cold-bytes",
    ): ("open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-conditional-warm-bytes",
    ): ("open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-backtracking-heavy-cold-str",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-str",
    ): (
        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-str",
    ): (
        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
    ),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-backtracking-heavy-warm-str",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-str",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-gap",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-fourth-repetition-short-only-str",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",),
    (
        "open_ended_quantified_group_boundary.py",
        "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes",
    ): ("open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",),
}

OPEN_ENDED_DIRECT_PARITY_BYTES_CASES = (
    *OPEN_ENDED_ALTERNATION_BYTES_CASES,
    *OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    *OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    *BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    *BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    *BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
)


def _compile_proxy_signature(
    pattern: str | bytes,
    *,
    flags: int,
    text_model: str,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str]:
    return ("module.compile", pattern, (), (), flags, text_model)


def _compile_proxy_correctness_case_signature(
    case: Any,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str] | None:
    if case.operation != "compile":
        return None
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, (str, bytes))
    return _compile_proxy_signature(
        pattern,
        flags=case.flags or 0,
        text_model=case.text_model or "str",
    )


def _compile_proxy_workload_signature(
    workload: Any,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str]:
    pattern = workload.pattern_payload()
    assert isinstance(pattern, (str, bytes))
    return _compile_proxy_signature(
        pattern,
        flags=workload.flags,
        text_model=workload.text_model,
    )


def _is_compile_proxy_workload(workload: Any) -> bool:
    return workload.operation in {"compile", "module.compile"}


def _optional_group_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.helper != "search":
        return None

    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"
    return (
        "module.search",
        None,
        freeze_signature_value(case.serialized_args()),
        kwargs_signature,
        flags,
        text_model,
    )


def _optional_group_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation != "module.search":
        raise AssertionError(
            "unexpected optional-group benchmark workload operation "
            f"{workload.operation!r}"
        )

    return (
        "module.search",
        None,
        freeze_signature_value([workload.pattern, workload.haystack]),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_optional_group_conditional_workload(workload: Any) -> bool:
    return workload.workload_id == OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID


def _nested_group_correctness_case_signature(case: Any) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", case.pattern, (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper == "search":
        return (
            "module.search",
            None,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper == "fullmatch":
        return (
            "pattern.fullmatch",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _nested_group_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            workload.pattern,
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "module.search":
        return (
            "module.search",
            None,
            (workload.pattern, workload.haystack),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "pattern.fullmatch":
        return (
            "pattern.fullmatch",
            workload.pattern,
            (workload.haystack,),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected nested-group workload operation {workload.operation!r}"
    )


def _is_measured_nested_group_workload(workload: Any) -> bool:
    return workload.workload_id not in EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS


def _counted_repeat_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return (
            "module.compile",
            case.pattern_payload(),
            (),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "module_call" and case.helper == "search":
        return (
            "module.search",
            None,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper == "fullmatch":
        return (
            "pattern.fullmatch",
            case.pattern_payload(),
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _counted_repeat_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            workload.pattern_payload(),
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "module.search":
        return (
            "module.search",
            None,
            freeze_signature_value(
                [
                    workload.pattern_payload(),
                    workload.haystack_payload(),
                ]
            ),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "pattern.fullmatch":
        return (
            "pattern.fullmatch",
            workload.pattern_payload(),
            freeze_signature_value([workload.haystack_payload()]),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected counted-repeat benchmark workload operation {workload.operation!r}"
    )


def _is_non_alternation_counted_repeat_workload(workload: Any) -> bool:
    return workload.operation in {
        "module.compile",
        "module.search",
        "pattern.fullmatch",
    } and "|" not in workload.pattern


def _is_non_special_open_ended_workload(workload: Any) -> bool:
    return workload.workload_id not in EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS


def _is_non_special_nested_group_replacement_workload(workload: Any) -> bool:
    return (
        workload.workload_id
        not in EXPECTED_NESTED_GROUP_REPLACEMENT_SPECIAL_UNANCHORED_WORKLOAD_IDS
    )


def _grouped_alternation_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", case.pattern, (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper in {"search", "sub", "subn"}:
        return (
            f"module.{case.helper}",
            None,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"fullmatch", "sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _grouped_alternation_workload_args(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return ()
    if workload.operation == "module.search":
        return freeze_signature_value([workload.pattern, workload.haystack])
    if workload.operation == "pattern.fullmatch":
        return freeze_signature_value([workload.haystack])
    if workload.operation in {"module.sub", "module.subn"}:
        args = [workload.pattern, workload.replacement, workload.haystack]
        if workload.count:
            args.append(workload.count)
        return freeze_signature_value(args)
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [workload.replacement, workload.haystack]
        if workload.count:
            args.append(workload.count)
        return freeze_signature_value(args)
    raise AssertionError(
        f"unexpected grouped-alternation benchmark workload operation {workload.operation!r}"
    )


def _grouped_alternation_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            workload.pattern,
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"module.search", "module.sub", "module.subn"}:
        return (
            workload.operation,
            None,
            _grouped_alternation_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"pattern.fullmatch", "pattern.sub", "pattern.subn"}:
        return (
            workload.operation,
            workload.pattern,
            _grouped_alternation_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected grouped-alternation benchmark workload operation {workload.operation!r}"
    )


def _grouped_alternation_replacement_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "module_call" and case.helper in {"sub", "subn"}:
        return (
            f"module.{case.helper}",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _grouped_alternation_replacement_workload_args(workload: Any) -> tuple[Any, ...]:
    if workload.operation in {"module.sub", "module.subn"}:
        args = [workload.pattern, workload.replacement, workload.haystack]
    elif workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [workload.replacement, workload.haystack]
    else:
        raise AssertionError(
            "unexpected grouped-alternation replacement workload operation "
            f"{workload.operation!r}"
        )

    if workload.count:
        args.append(workload.count)
    return freeze_signature_value(args)


def _grouped_alternation_replacement_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if workload.operation in {"module.sub", "module.subn"}:
        return (
            workload.operation,
            None,
            _grouped_alternation_replacement_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        return (
            workload.operation,
            workload.pattern,
            _grouped_alternation_replacement_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        "unexpected grouped-alternation replacement workload operation "
        f"{workload.operation!r}"
    )


def _include_all_workloads(_: Any) -> bool:
    return True


@cache
def _manifest_workloads_by_id(manifest_path: pathlib.Path) -> dict[str, Any]:
    return {
        workload.workload_id: workload for workload in load_manifest(manifest_path).workloads
    }


def _definition_workloads_by_id(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[str, Any]:
    workloads_by_id: dict[str, Any] = {}
    for manifest_path in definition.manifest_paths:
        workloads_by_id.update(_manifest_workloads_by_id(manifest_path))
    return workloads_by_id


@cache
def _direct_parity_case_ids_by_signature(
    supplemental_cases: tuple[Any, ...],
) -> dict[tuple[str, bytes, bytes], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[str, bytes, bytes], list[str]] = {}

    for case in supplemental_cases:
        for haystack in case.search_matches + case.search_misses:
            case_ids_by_signature.setdefault(
                ("module.search", case.pattern, haystack),
                [],
            ).append(case.id)
        for haystack in case.fullmatch_matches + case.fullmatch_misses:
            case_ids_by_signature.setdefault(
                ("pattern.fullmatch", case.pattern, haystack),
                [],
            ).append(case.id)

    return {
        signature: tuple(case_ids)
        for signature, case_ids in case_ids_by_signature.items()
    }


def _manual_expected_result(workload: Any) -> object:
    pattern = workload.pattern_payload()
    re.purge()
    try:
        if workload.operation == "module.compile":
            return re.compile(pattern, workload.flags)
        if workload.operation == "module.search":
            return re.search(pattern, workload.haystack_payload(), workload.flags)
        if workload.operation == "pattern.fullmatch":
            compiled = re.compile(pattern, workload.flags)
            return compiled.fullmatch(workload.haystack_payload())
        if workload.operation == "module.sub":
            return re.sub(
                pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
                workload.flags,
            )
        if workload.operation == "module.subn":
            return re.subn(
                pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
                workload.flags,
            )
        if workload.operation == "pattern.sub":
            compiled = re.compile(pattern, workload.flags)
            return compiled.sub(
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
            )
        if workload.operation == "pattern.subn":
            compiled = re.compile(pattern, workload.flags)
            return compiled.subn(
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
            )
    finally:
        re.purge()

    raise AssertionError(
        f"unexpected special-unanchored benchmark workload operation {workload.operation!r}"
    )


STANDARD_BENCHMARK_DEFINITIONS = (
    StandardBenchmarkAnchorContractDefinition(
        name="compile-proxy",
        manifest_paths=(
            COMPILE_MATRIX_MANIFEST_PATH,
            REGRESSION_MATRIX_MANIFEST_PATH,
        ),
        expected_anchor_case_ids=EXPECTED_COMPILE_ANCHOR_CASE_IDS,
        include_workload=_is_compile_proxy_workload,
        correctness_case_signature=_compile_proxy_correctness_case_signature,
        workload_signature=_compile_proxy_workload_signature,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="optional-group-conditional",
        manifest_paths=(OPTIONAL_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS,
        include_workload=_is_optional_group_conditional_workload,
        correctness_case_signature=_optional_group_correctness_case_signature,
        workload_signature=_optional_group_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="nested-group",
        manifest_paths=(NESTED_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS,
        include_workload=_is_measured_nested_group_workload,
        correctness_case_signature=_nested_group_correctness_case_signature,
        workload_signature=_nested_group_workload_signature,
        run_callback_result_parity=True,
        expected_excluded_workload_ids=EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="exact-repeat",
        manifest_paths=(EXACT_REPEAT_MANIFEST_PATH,),
        expected_anchor_case_ids=EXACT_REPEAT_EXPECTED_ANCHOR_CASE_IDS,
        include_workload=_is_non_alternation_counted_repeat_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="ranged-repeat",
        manifest_paths=(RANGED_REPEAT_MANIFEST_PATH,),
        expected_anchor_case_ids=RANGED_REPEAT_EXPECTED_ANCHOR_CASE_IDS,
        include_workload=_is_non_alternation_counted_repeat_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="grouped-alternation",
        manifest_paths=(GROUPED_ALTERNATION_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS,
        include_workload=_include_all_workloads,
        correctness_case_signature=_grouped_alternation_correctness_case_signature,
        workload_signature=_grouped_alternation_workload_signature,
        run_callback_result_parity=True,
        expected_legacy_workload_ids=EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS,
        expected_legacy_anchor_case_ids=(
            EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS
        ),
        callback_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="grouped-alternation-replacement",
        manifest_paths=(GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS,
        include_workload=_include_all_workloads,
        correctness_case_signature=(
            _grouped_alternation_replacement_correctness_case_signature
        ),
        workload_signature=_grouped_alternation_replacement_workload_signature,
        run_callback_result_parity=True,
        expected_legacy_workload_ids=(
            EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_WORKLOAD_IDS
        ),
        expected_legacy_anchor_case_ids=(
            EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_ANCHOR_CASE_IDS
        ),
        callback_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="nested-group-replacement",
        manifest_paths=(NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_NESTED_GROUP_REPLACEMENT_ANCHOR_CASE_IDS,
        include_workload=_is_non_special_nested_group_replacement_workload,
        correctness_case_signature=(
            _grouped_alternation_replacement_correctness_case_signature
        ),
        workload_signature=_grouped_alternation_replacement_workload_signature,
        run_callback_result_parity=True,
        expected_special_unanchored_workload_ids=(
            EXPECTED_NESTED_GROUP_REPLACEMENT_SPECIAL_UNANCHORED_WORKLOAD_IDS
        ),
        run_special_unanchored_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="open-ended-grouped-alternation",
        manifest_paths=(OPEN_ENDED_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS,
        include_workload=_is_non_special_open_ended_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
        expected_special_unanchored_workload_ids=(
            EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS
        ),
        direct_parity_supplemental_cases=OPEN_ENDED_DIRECT_PARITY_BYTES_CASES,
        run_special_unanchored_result_parity=True,
    ),
)

STANDARD_BENCHMARK_MANIFEST_DEFINITIONS = tuple(
    (definition, manifest_path)
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    for manifest_path in definition.manifest_paths
)
STANDARD_BENCHMARK_MANIFEST_IDS = [
    f"{definition.name}:{manifest_path.name}"
    for definition, manifest_path in STANDARD_BENCHMARK_MANIFEST_DEFINITIONS
]
STANDARD_BENCHMARK_LEGACY_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.expected_legacy_anchor_case_ids
)
STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.run_callback_result_parity
)
STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.expected_special_unanchored_workload_ids
)
STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DIRECT_PARITY_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS
    if definition.direct_parity_supplemental_cases
)
STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES = tuple(
    (definition, workload_id)
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.run_special_unanchored_result_parity
    for workload_id in definition.expected_special_unanchored_workload_ids
)
STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_IDS = [
    f"{definition.name}:{workload_id}"
    for definition, workload_id in STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES
]


def _expected_workload_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return tuple(
        workload_id
        for (manifest_name, workload_id), _ in definition.expected_anchor_case_ids.items()
        if manifest_name == manifest_path.name
    )


def _expected_anchor_case_ids_for_manifest(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] | None = None,
) -> dict[tuple[str, str], tuple[str, ...]]:
    anchor_case_ids = (
        definition.expected_anchor_case_ids
        if expected_anchor_case_ids is None
        else expected_anchor_case_ids
    )
    return {
        (manifest_name, workload_id): case_ids
        for (manifest_name, workload_id), case_ids in anchor_case_ids.items()
        if manifest_name == manifest_path.name
    }


def _anchored_case_ids_for_manifest(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> dict[tuple[str, str], tuple[str, ...]]:
    return anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
        include_workload=definition.include_workload,
    )


def _anchored_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[tuple[str, str], tuple[str, ...]]:
    anchored_case_ids: dict[tuple[str, str], tuple[str, ...]] = {}
    for manifest_path in definition.manifest_paths:
        anchored_case_ids.update(
            _anchored_case_ids_for_manifest(definition, manifest_path)
        )
    return anchored_case_ids


def _unanchored_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
        include_workload=definition.include_workload,
    )


def _all_unanchored_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
    )


def _expected_callback_anchor_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[tuple[str, str], tuple[str, ...]]:
    if definition.callback_anchor_case_ids:
        return definition.callback_anchor_case_ids
    return definition.expected_anchor_case_ids


def _expected_anchored_pairs(
    definition: StandardBenchmarkAnchorContractDefinition,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] | None = None,
) -> tuple[Any, ...]:
    anchored_pairs = []
    for manifest_path in definition.manifest_paths:
        manifest_anchor_case_ids = _expected_anchor_case_ids_for_manifest(
            definition,
            manifest_path,
            expected_anchor_case_ids=expected_anchor_case_ids,
        )
        if not manifest_anchor_case_ids:
            continue
        anchored_pairs.extend(
            expected_anchored_workload_case_pairs(
                manifest_path,
                expected_anchor_case_ids=manifest_anchor_case_ids,
                include_workload=definition.include_workload,
            )
        )
    return tuple(anchored_pairs)


def test_default_benchmark_manifest_selector_rejects_unknown_selector() -> None:
    with pytest.raises(ValueError, match="unknown benchmark manifest selector"):
        select_benchmark_manifest_paths("missing-selector")


def test_default_benchmark_single_manifest_selector_helper_rejects_full_suite_selector() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "benchmark manifest selector 'published-full-suite' "
            "does not resolve to exactly one path"
        ),
    ):
        select_benchmark_manifest_path(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR)


def test_default_benchmark_published_full_suite_selector_covers_tracked_manifests_except_compile_smoke() -> None:
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )
    tracked_manifest_paths = _tracked_benchmark_manifest_paths()
    compile_smoke_manifest_path = select_benchmark_manifest_path(
        COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR
    )

    assert set(published_manifest_paths) == set(tracked_manifest_paths) - {
        compile_smoke_manifest_path
    }
    assert len(published_manifest_paths) == len(set(published_manifest_paths))

    for path in published_manifest_paths:
        assert path.is_relative_to(BENCHMARK_WORKLOADS_ROOT)
        assert path.is_file()
        assert path.suffix == ".py"


def test_default_benchmark_shared_selectors_keep_expected_inventory_shapes() -> None:
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )
    native_smoke_manifest_paths = select_benchmark_manifest_paths(
        BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR
    )
    compile_smoke_manifest_path = select_benchmark_manifest_path(
        COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR
    )

    assert tuple(path.name for path in native_smoke_manifest_paths) == (
        "pattern_boundary.py",
        "collection_replacement_boundary.py",
        "literal_flag_boundary.py",
    )
    assert set(native_smoke_manifest_paths).issubset(set(published_manifest_paths))
    assert compile_smoke_manifest_path.name == "compile_smoke.py"
    assert compile_smoke_manifest_path.is_relative_to(BENCHMARK_WORKLOADS_ROOT)
    assert compile_smoke_manifest_path not in published_manifest_paths


def test_default_benchmark_published_manifest_helper_is_cached_and_preserves_selector_order() -> None:
    manifests = published_benchmark_manifests()
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )

    assert published_benchmark_manifests() is manifests
    assert tuple(manifest.path for manifest in manifests) == published_manifest_paths


def test_default_benchmark_published_manifest_inventory_has_unique_manifest_and_workload_ids() -> None:
    manifests = published_benchmark_manifests()
    manifest_ids = [manifest.manifest_id for manifest in manifests]
    workloads = [workload for manifest in manifests for workload in manifest.workloads]

    assert _duplicate_items(Counter(manifest_ids)) == []
    assert _duplicate_items(Counter(workload.workload_id for workload in workloads)) == []

    workloads_by_manifest = Counter(workload.manifest_id for workload in workloads)
    published_manifest_ids = set(manifest_ids)
    for manifest_id in published_manifest_ids:
        assert workloads_by_manifest[manifest_id] > 0

    for workload in workloads:
        assert workload.manifest_id in published_manifest_ids


def test_built_native_smoke_runner_uses_explicit_report_paths_only() -> None:
    _assert_built_native_runner_uses_optional_report_path(
        runner=benchmarks.run_built_native_smoke_benchmarks,
        expected_manifest_selector=benchmarks.BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR,
        expected_smoke_only=True,
    )


def test_built_native_smoke_cli_uses_explicit_report_paths_only(
    tmp_path: pathlib.Path,
) -> None:
    _assert_built_native_cli_uses_optional_report_path(
        tmp_path,
        flag="--native-smoke",
        runner_name="run_built_native_smoke_benchmarks",
        report_name="benchmarks-native-smoke.json",
    )


def test_built_native_smoke_mode_requires_real_built_runtime(
    tmp_path: pathlib.Path,
) -> None:
    _assert_built_native_mode_requires_real_built_runtime(
        tmp_path / "benchmarks-native-smoke.json",
        runner=benchmarks.run_built_native_smoke_benchmarks,
    )


@pytest.mark.skipif(
    MATURIN is None,
    reason="built-native benchmark smoke requires a maturin executable on PATH",
)
def test_built_native_smoke_mode_writes_built_native_report(
    tmp_path: pathlib.Path,
) -> None:
    report_path = tmp_path / "benchmarks-native-smoke.json"
    scorecard = benchmarks.run_built_native_smoke_benchmarks(
        report_path=report_path,
    )
    assert report_path.is_file()
    _assert_built_native_combined_scorecard_fields(
        scorecard,
        expected_phase="phase2-module-boundary-suite",
        expected_selection_mode="smoke",
        expected_manifest_count=3,
    )
    assert scorecard["implementation"]["adapter"] == "rebar.module-surface"
    assert scorecard["summary"]["total_workloads"] == 6
    assert scorecard["summary"]["parser_workloads"] == 0
    assert scorecard["summary"]["module_workloads"] == 6
    assert scorecard["summary"]["regression_workloads"] == 0
    assert scorecard["summary"]["measured_workloads"] == 6
    assert scorecard["summary"]["known_gap_count"] == 0
    assert [workload["id"] for workload in scorecard["workloads"]] == [
        "pattern-search-literal-warm-hit",
        "pattern-fullmatch-bytes-purged-hit",
        "module-split-literal-warm-str",
        "pattern-subn-literal-purged-bytes",
        "module-search-inline-flag-warm-str-hit",
        "pattern-fullmatch-ignorecase-purged-bytes-hit",
    ]


def test_run_benchmarks_falls_back_to_source_shim_when_build_tooling_is_unavailable(
    tmp_path: pathlib.Path,
) -> None:
    report_path = tmp_path / "benchmarks.json"
    with mock.patch.object(
        benchmarks,
        "provision_built_native_runtime",
        return_value=(None, None, _MISSING_MATURIN_REASON),
    ):
        scorecard = benchmarks.run_benchmarks(
            manifest_paths=[COMPILE_SMOKE_PROVENANCE_MANIFEST_PATH],
            report_path=report_path,
            adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        )

    implementation = scorecard["implementation"]
    assert implementation["adapter_mode_requested"] == "built-native"
    assert implementation["adapter_mode_resolved"] == "source-tree-shim"
    assert implementation["build_mode"] == "source-tree-shim"
    assert implementation["timing_path"] == "source-tree-shim"
    assert isinstance(implementation["native_module_loaded"], bool)
    assert "maturin" in implementation["native_unavailable_reason"]
    assert implementation["native_build_tool"] is None
    assert implementation["native_wheel"] is None


@pytest.mark.skipif(
    MATURIN is None,
    reason="built-native benchmark provenance smoke requires a maturin executable on PATH",
)
def test_run_benchmarks_reports_built_native_provenance_when_available(
    tmp_path: pathlib.Path,
) -> None:
    scorecard = benchmarks.run_benchmarks(
        manifest_paths=[COMPILE_SMOKE_PROVENANCE_MANIFEST_PATH],
        report_path=tmp_path / "benchmarks-native.json",
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
    )

    implementation = scorecard["implementation"]
    assert implementation["adapter_mode_requested"] == "built-native"
    assert implementation["adapter_mode_resolved"] == "built-native"
    assert implementation["build_mode"] == "built-native"
    assert implementation["timing_path"] == "built-native"
    assert implementation["native_module_loaded"] is True
    assert implementation["native_module_name"] == "rebar._rebar"
    assert implementation["native_scaffold_status"] == "scaffold-only"
    assert implementation["native_target_cpython_series"] == "3.12.x"
    assert implementation["native_unavailable_reason"] is None
    assert implementation["native_build_tool"] == "maturin"
    assert str(implementation["native_wheel"]).startswith("rebar-")
    assert (
        scorecard["environment"]["execution_model"]
        == "single-interpreter subprocess workload probes against a built native wheel"
    )


def test_built_native_full_runner_uses_explicit_report_paths_only() -> None:
    _assert_built_native_runner_uses_optional_report_path(
        runner=benchmarks.run_built_native_full_benchmarks,
        expected_manifest_selector=benchmarks.PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
        expected_smoke_only=False,
    )


def test_built_native_full_cli_uses_explicit_report_paths_only(
    tmp_path: pathlib.Path,
) -> None:
    _assert_built_native_cli_uses_optional_report_path(
        tmp_path,
        flag="--native-full",
        runner_name="run_built_native_full_benchmarks",
        report_name="benchmarks-native-full.json",
    )


def test_built_native_full_mode_requires_real_built_runtime(
    tmp_path: pathlib.Path,
) -> None:
    _assert_built_native_mode_requires_real_built_runtime(
        tmp_path / "benchmarks-native-full.json",
        runner=benchmarks.run_built_native_full_benchmarks,
    )


@pytest.mark.skipif(
    MATURIN is None,
    reason="built-native full-suite benchmark requires a maturin executable on PATH",
)
def test_built_native_full_mode_writes_built_native_report_with_known_gaps(
    tmp_path: pathlib.Path,
) -> None:
    published_manifests = benchmarks.published_benchmark_manifests()
    selected_workloads = [
        workload
        for manifest in published_manifests
        for workload in manifest.workloads
    ]
    expected_total = len(selected_workloads)
    expected_parser = sum(1 for workload in selected_workloads if workload.family == "parser")
    expected_module = sum(1 for workload in selected_workloads if workload.family == "module")
    expected_regression = sum(
        1 for workload in selected_workloads if workload.manifest_id == "regression-matrix"
    )

    report_path = tmp_path / "benchmarks-native-full.json"
    scorecard = benchmarks.run_built_native_full_benchmarks(
        report_path=report_path,
    )
    assert report_path.is_file()
    _assert_built_native_combined_scorecard_fields(
        scorecard,
        expected_phase="phase3-regression-stability-suite",
        expected_selection_mode="full",
        expected_manifest_count=len(published_manifests),
    )
    assert scorecard["summary"]["total_workloads"] == expected_total
    assert scorecard["summary"]["parser_workloads"] == expected_parser
    assert scorecard["summary"]["module_workloads"] == expected_module
    assert scorecard["summary"]["regression_workloads"] == expected_regression

    unimplemented_workloads = [
        workload
        for workload in scorecard["workloads"]
        if workload["implementation_timing"]["status"] == "unimplemented"
    ]
    measured_workloads = [
        workload
        for workload in scorecard["workloads"]
        if workload["implementation_timing"]["status"] == "measured"
    ]
    assert len(unimplemented_workloads) > 0
    assert scorecard["summary"]["known_gap_count"] == len(unimplemented_workloads)
    assert scorecard["summary"]["measured_workloads"] == len(measured_workloads)
    assert len(measured_workloads) + len(unimplemented_workloads) == expected_total


def test_standard_benchmark_manifest_materializes_callable_replacement_descriptors(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-loader-contract",
        "defaults": {
            "warmup_iterations": 2,
            "sample_iterations": 3,
            "timed_samples": 4,
            "text_model": "str",
            "cache_mode": "warm",
            "timing_scope": "module-helper-call",
        },
        "workloads": [
            {
                "id": "module-sub-callable-numbered-contract-str",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": r"a((bc)+)d",
                "replacement": {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "haystack": "zzabcbcdzz",
                "count": 0,
                "categories": ["replacement", "callable", "numbered-group", "str"],
                "notes": [
                    "Ensures Python-backed benchmark manifests materialize numbered callable replacement descriptors."
                ],
            },
            {
                "id": "pattern-subn-callable-named-contract-str",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": r"a(?P<outer>(?P<inner>bc)+)d",
                "replacement": {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": "<",
                    "suffix": ">",
                },
                "haystack": "zzabcbcdabcbcdzz",
                "count": 1,
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "categories": ["replacement", "callable", "named-group", "str"],
                "notes": [
                    "Ensures Python-backed benchmark manifests materialize named callable replacement descriptors."
                ],
            },
            {
                "id": "module-sub-callable-constant-contract-bytes",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": r"a((bc)+)d",
                "replacement": {
                    "type": "callable_constant",
                    "value": {
                        "type": "bytes",
                        "value": "CONST",
                        "encoding": "ascii",
                    },
                },
                "haystack": "zzabcbcdzz",
                "text_model": "bytes",
                "categories": ["replacement", "callable", "constant", "bytes"],
                "notes": [
                    "Ensures Python-backed benchmark manifests keep bytes-aware callable constants available for subprocess serialization and runtime materialization."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_loader_contract.py",
        manifest_source,
    )
    manifest = load_manifest(manifest_path)
    workloads = manifest.workloads

    assert manifest.manifest_id == "python-benchmark-loader-contract"
    assert not hasattr(manifest, "defaults")
    assert [workload.workload_id for workload in workloads] == [
        "module-sub-callable-numbered-contract-str",
        "pattern-subn-callable-named-contract-str",
        "module-sub-callable-constant-contract-bytes",
    ]

    numbered_workload = workloads[0]
    assert numbered_workload.warmup_iterations == 2
    assert numbered_workload.sample_iterations == 3
    assert numbered_workload.timed_samples == 4
    assert numbered_workload.pattern_payload() == r"a((bc)+)d"
    assert numbered_workload.haystack_payload() == "zzabcbcdzz"
    numbered_replacement = numbered_workload.replacement_payload()
    assert callable(numbered_replacement)
    assert numbered_replacement.__module__ == "rebar_harness.benchmarks"
    assert numbered_replacement.__qualname__ == "callable_match_group"
    numbered_match = re.search(
        numbered_workload.pattern_payload(),
        numbered_workload.haystack_payload(),
    )
    assert numbered_match is not None
    assert numbered_replacement(numbered_match) == "bcbcx"
    assert workload_to_payload(numbered_workload)["replacement"] == {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x",
    }

    named_workload = workloads[1]
    assert named_workload.cache_mode == "purged"
    assert named_workload.timing_scope == "pattern-helper-call"
    named_replacement = named_workload.replacement_payload()
    assert callable(named_replacement)
    assert named_replacement.__module__ == "rebar_harness.benchmarks"
    assert named_replacement.__qualname__ == "callable_match_group"
    named_match = re.search(
        named_workload.pattern_payload(),
        named_workload.haystack_payload(),
    )
    assert named_match is not None
    assert named_replacement(named_match) == "<bc>"
    assert workload_to_payload(named_workload)["replacement"] == {
        "type": "callable_match_group",
        "group": "inner",
        "prefix": "<",
        "suffix": ">",
    }

    constant_bytes_workload = workloads[2]
    assert constant_bytes_workload.text_model == "bytes"
    assert constant_bytes_workload.pattern_payload() == rb"a((bc)+)d"
    assert constant_bytes_workload.haystack_payload() == b"zzabcbcdzz"
    constant_bytes_replacement = constant_bytes_workload.replacement_payload()
    assert callable(constant_bytes_replacement)
    assert constant_bytes_replacement.__module__ == "rebar_harness.benchmarks"
    assert constant_bytes_replacement.__qualname__ == "callable_constant"
    constant_bytes_match = re.search(
        constant_bytes_workload.pattern_payload(),
        constant_bytes_workload.haystack_payload(),
    )
    assert constant_bytes_match is not None
    assert constant_bytes_replacement(constant_bytes_match) == b"CONST"
    assert workload_to_payload(constant_bytes_workload)["replacement"] == {
        "type": "callable_constant",
        "value": {
            "type": "bytes",
            "value": "CONST",
            "encoding": "ascii",
        },
    }


def test_standard_benchmark_manifest_selected_workloads_preserves_filters_and_order(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-selection-contract",
        "workloads": [
            {
                "id": "compile-literal-cold",
                "operation": "compile",
                "pattern": "abc",
            },
            {
                "id": "compile-smoke-flagged",
                "operation": "compile",
                "pattern": "def",
                "smoke": True,
            },
            {
                "id": "compile-smoke-categorized",
                "operation": "compile",
                "pattern": "ghi",
                "categories": ["smoke"],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_selection_contract.py",
        manifest_source,
    )
    manifest = load_manifest(manifest_path)

    assert [workload.workload_id for workload in manifest.selected_workloads()] == [
        "compile-literal-cold",
        "compile-smoke-flagged",
        "compile-smoke-categorized",
    ]
    assert manifest.smoke_workload_ids() == [
        "compile-smoke-flagged",
        "compile-smoke-categorized",
    ]
    assert [
        workload.workload_id
        for workload in manifest.selected_workloads(
            selected_workload_ids=(
                "compile-smoke-categorized",
                "compile-literal-cold",
            )
        )
    ] == ["compile-smoke-categorized", "compile-literal-cold"]
    assert [
        workload.workload_id
        for workload in manifest.selected_workloads(
            selection_mode="smoke",
            selected_workload_ids=(
                "compile-smoke-categorized",
                "compile-literal-cold",
                "compile-smoke-flagged",
            ),
        )
    ] == ["compile-smoke-categorized", "compile-smoke-flagged"]

    with pytest.raises(
        AssertionError,
        match=(
            "missing workload definition 'missing-workload' in "
            "'python-benchmark-selection-contract'"
        ),
    ):
        manifest.selected_workloads(selected_workload_ids=("missing-workload",))

    with pytest.raises(
        AssertionError,
        match="unknown benchmark selection mode 'unknown'",
    ):
        manifest.selected_workloads(selection_mode="unknown")


def test_standard_benchmark_manifest_measures_expected_exception_workloads(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-exception-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
            "text_model": "str",
            "cache_mode": "warm",
            "timing_scope": "module-helper-call",
        },
        "workloads": [
            {
                "id": "module-subn-callable-numbered-conditional-expected-exception-contract-str",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": r"a(b)?c(?(1)d|e)",
                "replacement": {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "NoneType",
                },
                "haystack": "zzacezz",
                "count": 1,
                "categories": [
                    "replacement",
                    "callable",
                    "conditional",
                    "exception",
                    "str",
                ],
                "notes": [
                    "Ensures Python-backed benchmark manifests can measure expected callable replacement exceptions instead of failing the run."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_exception_contract.py",
        manifest_source,
    )
    workloads = load_manifest(manifest_path).workloads

    workload = workloads[0]
    payload = workload_to_payload(workload)
    assert payload["expected_exception"] == {
        "type": "TypeError",
        "message_substring": "NoneType",
    }

    baseline_probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name="re",
        adapter_name="cpython.re",
    )
    assert baseline_probe["status"] == "measured"
    assert baseline_probe["median_ns"] > 0

    implementation_probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name="rebar",
        adapter_name="rebar",
    )
    assert implementation_probe["status"] == "measured"
    assert implementation_probe["median_ns"] > 0


def test_standard_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-bytes-template-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            {
                "id": "module-sub-template-numbered-conditional-contract-bytes",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": r"a((b|c){2,})\\2(?(2)d|e)",
                "replacement": r"\\1x",
                "haystack": "abbbd",
                "text_model": "bytes",
                "cache_mode": "warm",
                "timing_scope": "module-helper-call",
                "categories": [
                    "replacement",
                    "template",
                    "numbered-group",
                    "bytes",
                ],
                "notes": [
                    "Ensures bytes benchmark manifests materialize numbered template replacements through the same published nested-group helper path."
                ],
            },
            {
                "id": "pattern-subn-template-named-conditional-contract-bytes",
                "bucket": "pattern-subn",
                "family": "module",
                "operation": "pattern.subn",
                "pattern": r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
                "replacement": r"\\g<inner>x",
                "haystack": "zzacccdabcbccdzz",
                "count": 1,
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "categories": [
                    "replacement",
                    "template",
                    "named-group",
                    "bytes",
                ],
                "notes": [
                    "Ensures bytes benchmark manifests materialize named template replacements through the same published nested-group helper path."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_bytes_template_contract.py",
        manifest_source,
    )
    manifest = load_manifest(manifest_path)
    workloads = manifest.workloads

    assert manifest.manifest_id == "python-benchmark-bytes-template-contract"
    assert [workload.workload_id for workload in workloads] == [
        "module-sub-template-numbered-conditional-contract-bytes",
        "pattern-subn-template-named-conditional-contract-bytes",
    ]

    expected_payloads = {
        "module-sub-template-numbered-conditional-contract-bytes": {
            "pattern": rb"a((b|c){2,})\2(?(2)d|e)",
            "haystack": b"abbbd",
            "replacement": b"\\1x",
            "serialized_replacement": "\\1x",
            "expected_result": b"bbx",
        },
        "pattern-subn-template-named-conditional-contract-bytes": {
            "pattern": rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
            "haystack": b"zzacccdabcbccdzz",
            "replacement": b"\\g<inner>x",
            "serialized_replacement": "\\g<inner>x",
            "expected_result": (b"zzcxabcbccdzz", 1),
        },
    }

    for workload in workloads:
        expected = expected_payloads[workload.workload_id]
        assert workload.text_model == "bytes"
        assert workload.pattern_payload() == expected["pattern"]
        assert workload.haystack_payload() == expected["haystack"]
        assert workload.replacement_payload() == expected["replacement"]
        assert workload_to_payload(workload)["replacement"] == expected[
            "serialized_replacement"
        ]

        if workload.operation == "module.sub":
            result = re.sub(
                workload.pattern_payload(),
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
                workload.flags,
            )
        else:
            result = re.compile(
                workload.pattern_payload(),
                workload.flags,
            ).subn(
                workload.replacement_payload(),
                workload.haystack_payload(),
                count=workload.count,
            )
        assert result == expected["expected_result"]

        baseline_probe = run_internal_workload_probe(
            workload_payload=json.dumps(workload_to_payload(workload), sort_keys=True),
            import_name="re",
            adapter_name="cpython.re",
        )
        assert baseline_probe["status"] == "measured"
        assert baseline_probe["median_ns"] > 0


def test_standard_benchmark_manifest_materializes_nested_constant_bytes_without_aliasing(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-nested-constant-contract",
        "defaults": {
            "warmup_iterations": 2,
            "sample_iterations": 3,
            "timed_samples": 4,
            "text_model": "bytes",
        },
        "workloads": [
            {
                "id": "module-sub-callable-nested-constant-contract-bytes",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": r"(abc)",
                "text_model": "bytes",
                "replacement": {
                    "type": "callable_constant",
                    "value": {
                        "literal": "literal",
                        "sequence": [
                            "inner",
                            {
                                "type": "bytes",
                                "value": "XYZ",
                                "encoding": "ascii",
                            },
                            {"nested": "value"},
                        ],
                    },
                },
                "haystack": "abc",
                "categories": ["replacement", "callable", "constant", "bytes"],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_nested_constant_contract.py",
        manifest_source,
    )
    manifest = load_manifest(manifest_path)
    workloads = manifest.workloads

    assert manifest.manifest_id == "python-benchmark-nested-constant-contract"
    assert [workload.workload_id for workload in workloads] == [
        "module-sub-callable-nested-constant-contract-bytes",
    ]

    workload = workloads[0]
    assert workload.text_model == "bytes"
    assert workload_to_payload(workload)["replacement"] == {
        "type": "callable_constant",
        "value": {
            "literal": "literal",
            "sequence": [
                "inner",
                {
                    "type": "bytes",
                    "value": "XYZ",
                    "encoding": "ascii",
                },
                {"nested": "value"},
            ],
        },
    }

    replacement = workload.replacement_payload()
    assert callable(replacement)
    assert replacement.__module__ == "rebar_harness.benchmarks"
    assert replacement.__qualname__ == "callable_constant"

    raw_replacement = workload.replacement
    assert isinstance(raw_replacement, dict)
    raw_value = raw_replacement["value"]
    assert isinstance(raw_value, dict)
    raw_sequence = raw_value["sequence"]
    assert isinstance(raw_sequence, list)
    raw_bytes_descriptor = raw_sequence[1]
    assert isinstance(raw_bytes_descriptor, dict)
    raw_nested_mapping = raw_sequence[2]
    assert isinstance(raw_nested_mapping, dict)

    raw_value["literal"] = "mutated"
    raw_sequence[0] = "changed"
    raw_bytes_descriptor["value"] = "CHANGED"
    raw_nested_mapping["nested"] = "changed"

    match = re.search(workload.pattern_payload(), workload.haystack_payload())
    assert match is not None
    assert replacement(match) == {
        "literal": b"literal",
        "sequence": [
            b"inner",
            b"XYZ",
            {"nested": b"value"},
        ],
    }


def test_standard_benchmark_manifest_replacement_payload_rejects_unsupported_text_model(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-invalid-text-model-contract",
        "workloads": [
            {
                "id": "module-sub-callable-invalid-text-model",
                "bucket": "module-sub",
                "family": "module",
                "operation": "module.sub",
                "pattern": "abc",
                "replacement": {
                    "type": "callable_constant",
                    "value": "CONST",
                },
                "haystack": "abc",
                "text_model": "utf-16",
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_text_model_contract.py",
        manifest_source,
    )
    workloads = load_manifest(manifest_path).workloads

    with pytest.raises(ValueError, match=r"unsupported text model 'utf-16'"):
        workloads[0].replacement_payload()


def test_standard_benchmark_manifest_rejects_missing_and_non_dict_manifest_values(
    tmp_path: pathlib.Path,
) -> None:
    invalid_modules = (
        (
            "missing_manifest.py",
            "WORKLOADS = []",
            r"is missing a MANIFEST value",
        ),
        (
            "non_dict_manifest.py",
            "MANIFEST = ['not-a-dict']",
            r"must be a dict",
        ),
    )

    for filename, source, error_pattern in invalid_modules:
        manifest_path = _write_test_manifest(tmp_path, filename, source)
        with pytest.raises(ValueError, match=error_pattern):
            load_manifest(manifest_path)


def test_standard_benchmark_manifest_loader_rejects_duplicate_ids(
    tmp_path: pathlib.Path,
) -> None:
    duplicate_modules = (
        (
            (
                "duplicate_benchmark_manifest_a.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-manifest-id",
                    "workloads": [
                        {
                            "id": "benchmark-workload-a",
                            "operation": "module.search",
                            "pattern": "abc",
                            "haystack": "abc",
                        },
                    ],
                }
                """,
            ),
            (
                "duplicate_benchmark_manifest_b.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-manifest-id",
                    "workloads": [
                        {
                            "id": "benchmark-workload-b",
                            "operation": "module.search",
                            "pattern": "def",
                            "haystack": "def",
                        },
                    ],
                }
                """,
            ),
            r"duplicate benchmark manifest id .*duplicate-benchmark-manifest-id",
        ),
        (
            (
                "duplicate_benchmark_workload_a.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-workload-a",
                    "workloads": [
                        {
                            "id": "duplicate-benchmark-workload-id",
                            "operation": "module.search",
                            "pattern": "abc",
                            "haystack": "abc",
                        },
                    ],
                }
                """,
            ),
            (
                "duplicate_benchmark_workload_b.py",
                """
                MANIFEST = {
                    "schema_version": 1,
                    "manifest_id": "duplicate-benchmark-workload-b",
                    "workloads": [
                        {
                            "id": "duplicate-benchmark-workload-id",
                            "operation": "module.search",
                            "pattern": "def",
                            "haystack": "def",
                        },
                    ],
                }
                """,
            ),
            r"duplicate benchmark workload id .*duplicate-benchmark-workload-id",
        ),
    )

    for first_module, second_module, error_pattern in duplicate_modules:
        first_path = _write_test_manifest(tmp_path, *first_module)
        second_path = _write_test_manifest(tmp_path, *second_module)
        with pytest.raises(ValueError, match=error_pattern):
            load_manifests([first_path, second_path])


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    STANDARD_BENCHMARK_MANIFEST_DEFINITIONS,
    ids=STANDARD_BENCHMARK_MANIFEST_IDS,
)
def test_standard_benchmark_manifest_keeps_expected_workloads_in_scope(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    workloads = load_manifest(manifest_path).workloads
    assert {
        workload.workload_id
        for workload in workloads
        if workload.workload_id in definition.expected_excluded_workload_ids
    } == definition.expected_excluded_workload_ids
    assert {
        workload.workload_id
        for workload in workloads
        if workload.workload_id in definition.expected_legacy_workload_ids
    } == definition.expected_legacy_workload_ids
    assert tuple(
        workload.workload_id
        for workload in workloads
        if definition.include_workload(workload)
    ) == _expected_workload_ids(definition, manifest_path)


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    STANDARD_BENCHMARK_MANIFEST_DEFINITIONS,
    ids=STANDARD_BENCHMARK_MANIFEST_IDS,
)
def test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    assert _unanchored_case_ids(definition, manifest_path) == ()


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert _anchored_case_ids(definition) == definition.expected_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_special_unanchored_workloads_stay_explicit(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert tuple(
        workload_id
        for manifest_path in definition.manifest_paths
        for workload_id in _all_unanchored_case_ids(definition, manifest_path)
    ) == definition.expected_special_unanchored_workload_ids


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DIRECT_PARITY_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    workloads_by_id = _definition_workloads_by_id(definition)
    direct_parity_case_ids = _direct_parity_case_ids_by_signature(
        definition.direct_parity_supplemental_cases
    )
    uncovered_workload_ids: list[str] = []

    for workload_id in definition.expected_special_unanchored_workload_ids:
        workload = workloads_by_id[workload_id]
        if workload.text_model != "bytes":
            continue
        if workload.operation not in {"module.search", "pattern.fullmatch"}:
            raise AssertionError(
                "expected bytes special-unanchored workload to stay on a direct-parity "
                f"search/fullmatch path, got {workload.operation!r}"
            )

        signature = (
            workload.operation,
            workload.pattern_payload(),
            workload.haystack_payload(),
        )
        case_ids = direct_parity_case_ids.get(signature)
        if case_ids is None:
            uncovered_workload_ids.append(workload_id)
            continue

        assert len(case_ids) == 1

    assert uncovered_workload_ids == []


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_LEGACY_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert {
        key: case_ids
        for key, case_ids in _anchored_case_ids(definition).items()
        if key[1] in definition.expected_legacy_workload_ids
    } == definition.expected_legacy_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_workload_callbacks_match_anchor_case_results(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert_anchored_workload_case_result_parity(
        _expected_anchored_pairs(
            definition,
            expected_anchor_case_ids=_expected_callback_anchor_case_ids(definition),
        )
    )


@pytest.mark.parametrize(
    ("definition", "workload_id"),
    STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES,
    ids=STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_IDS,
)
def test_standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch(
    definition: StandardBenchmarkAnchorContractDefinition,
    workload_id: str,
) -> None:
    workload = _definition_workloads_by_id(definition)[workload_id]
    assert_benchmark_workload_matches_expected_result(
        workload,
        _manual_expected_result(workload),
    )


def test_freeze_signature_value_canonicalizes_nested_mappings_and_lists() -> None:
    value = {
        "b": [2, {"d": 4, "c": [5, 6]}],
        "a": {"y": 1, "x": 0},
    }

    assert support.freeze_signature_value(value) == (
        ("a", (("x", 0), ("y", 1))),
        ("b", (2, (("c", (5, 6)), ("d", 4)))),
    )


def test_published_case_ids_by_signature_groups_duplicate_case_ids(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    manifest = _synthetic_manifest(
        cases=(
            _synthetic_case("case-b", ("shared",)),
            _synthetic_case("case-a", ("shared",)),
            _synthetic_case("case-c", ("unique",)),
            _synthetic_case("ignored", None),
        )
    )
    monkeypatch.setattr(support, "published_fixture_manifests", lambda: (manifest,))

    observed = support.published_case_ids_by_signature(lambda case: case.signature)

    assert observed == {
        ("shared",): ("case-a", "case-b"),
        ("unique",): ("case-c",),
    }


def test_anchored_and_unanchored_workload_helpers_follow_signatures_and_filters(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",)),
        _synthetic_workload("excluded", ("shared",), include=False),
    )
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(workloads=workloads),
    )

    anchor_case_ids = {("shared",): ("case-a", "case-b")}
    workload_signature = lambda workload: workload.signature
    include_workload = lambda workload: workload.include

    assert support.anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=workload_signature,
        include_workload=include_workload,
    ) == {
        ("synthetic_boundary.py", "anchored"): ("case-a", "case-b"),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert support.unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=workload_signature,
        include_workload=include_workload,
    ) == ("unanchored",)


def test_expected_anchored_workload_case_pairs_return_matching_objects(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workload = _synthetic_workload("anchored", ("shared",))
    case = SimpleNamespace(case_id="case-1")
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(workloads=(workload,)),
    )
    monkeypatch.setattr(support, "published_cases_by_id", lambda: {"case-1": case})

    anchored_pairs = support.expected_anchored_workload_case_pairs(
        manifest_path,
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
        },
    )

    assert len(anchored_pairs) == 1
    anchored_pair = anchored_pairs[0]
    assert anchored_pair.manifest_name == "synthetic_boundary.py"
    assert anchored_pair.workload_id == "anchored"
    assert anchored_pair.case_id == "case-1"
    assert anchored_pair.workload is workload
    assert anchored_pair.case is case


def test_manifest_workload_cache_reuses_one_load_for_repeated_anchor_queries(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",)),
    )
    case = SimpleNamespace(case_id="case-1")
    load_calls: list[pathlib.Path] = []

    def _load_manifest(path: pathlib.Path) -> SimpleNamespace:
        load_calls.append(path)
        return _synthetic_manifest(workloads=workloads)

    monkeypatch.setattr(support, "load_manifest", _load_manifest)
    monkeypatch.setattr(support, "published_cases_by_id", lambda: {"case-1": case})

    anchor_case_ids = {("shared",): ("case-1",)}
    workload_signature = lambda workload: workload.signature

    assert support.anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=workload_signature,
    ) == {
        ("synthetic_boundary.py", "anchored"): ("case-1",),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert support.unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=workload_signature,
    ) == ("unanchored",)
    assert support.expected_anchored_workload_case_pairs(
        manifest_path,
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
        },
    ) == (
        support.AnchoredWorkloadCasePair(
            manifest_name="synthetic_boundary.py",
            workload_id="anchored",
            case_id="case-1",
            workload=workloads[0],
            case=case,
        ),
    )
    assert load_calls == [manifest_path]


def test_expected_anchored_workload_case_pairs_rejects_manifest_name_drift(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(
            workloads=(_synthetic_workload("anchored", ("shared",)),)
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: {"case-1": SimpleNamespace(case_id="case-1")},
    )

    with pytest.raises(AssertionError, match="does not match"):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("other_boundary.py", "anchored"): ("case-1",),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_multiple_case_ids(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(
            workloads=(_synthetic_workload("anchored", ("shared",)),)
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: {
            "case-1": SimpleNamespace(case_id="case-1"),
            "case-2": SimpleNamespace(case_id="case-2"),
        },
    )

    with pytest.raises(
        AssertionError,
        match="expected exactly one published correctness case",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "anchored"): ("case-1", "case-2"),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_missing_workload(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(
            workloads=(_synthetic_workload("anchored", ("shared",)),)
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: {"case-1": SimpleNamespace(case_id="case-1")},
    )

    with pytest.raises(
        AssertionError,
        match=r"expected anchored workload 'missing' to be in scope",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "missing"): ("case-1",),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_unpublished_case(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest(
            workloads=(_synthetic_workload("anchored", ("shared",)),)
        ),
    )
    monkeypatch.setattr(support, "published_cases_by_id", lambda: {})

    with pytest.raises(
        AssertionError,
        match=r"expected anchored correctness case 'case-1' to be published",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "anchored"): ("case-1",),
            },
        )


def test_assert_anchored_workload_case_result_parity_delegates_expected_values(
    monkeypatch,
    anchor_support_cache_guard,
) -> None:
    workload = _synthetic_workload("anchored", ("shared",))
    pair = support.AnchoredWorkloadCasePair(
        manifest_name="synthetic_boundary.py",
        workload_id="anchored",
        case_id="case-1",
        workload=workload,
        case=SimpleNamespace(case_id="case-1"),
    )
    calls: list[tuple[object, object]] = []
    monkeypatch.setattr(
        support,
        "run_correctness_case_with_cpython",
        lambda case: f"expected:{case.case_id}",
    )
    monkeypatch.setattr(
        support,
        "assert_benchmark_workload_matches_expected_result",
        lambda workload, expected: calls.append((workload, expected)),
    )

    support.assert_anchored_workload_case_result_parity((pair,))

    assert calls == [(workload, "expected:case-1")]
