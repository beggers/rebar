from __future__ import annotations

from dataclasses import dataclass
import pathlib
from typing import Any

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
EXACT_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "exact_repeat_quantified_group_boundary.py"
)
RANGED_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "ranged_repeat_quantified_group_boundary.py"
)

from rebar_harness.benchmarks import load_manifest
from tests.benchmarks.correctness_anchor_support import (
    anchored_workload_case_ids,
    freeze_signature_value,
    published_case_ids_by_signature,
    published_cases_by_id,
    run_benchmark_workload_with_cpython,
    run_correctness_case_with_cpython,
    unanchored_workload_ids,
)
from tests.python.fixture_parity_support import (
    assert_match_result_parity,
    assert_pattern_parity,
)


@dataclass(frozen=True, slots=True)
class CountedRepeatBenchmarkAnchorContractDefinition:
    name: str
    manifest_path: pathlib.Path
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]


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
    ): ("broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",),
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
    ): ("broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",),
}


COUNTED_REPEAT_DEFINITIONS = (
    CountedRepeatBenchmarkAnchorContractDefinition(
        name="exact-repeat",
        manifest_path=EXACT_REPEAT_MANIFEST_PATH,
        expected_anchor_case_ids=EXACT_REPEAT_EXPECTED_ANCHOR_CASE_IDS,
    ),
    CountedRepeatBenchmarkAnchorContractDefinition(
        name="ranged-repeat",
        manifest_path=RANGED_REPEAT_MANIFEST_PATH,
        expected_anchor_case_ids=RANGED_REPEAT_EXPECTED_ANCHOR_CASE_IDS,
    ),
)


def _correctness_case_signature(case: Any) -> tuple[Any, ...] | None:
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


def _workload_signature(workload: Any) -> tuple[Any, ...]:
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


def _expected_workload_ids(
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]],
) -> tuple[str, ...]:
    return tuple(workload_id for _, workload_id in expected_anchor_case_ids)


def _anchored_case_ids(
    definition: CountedRepeatBenchmarkAnchorContractDefinition,
) -> dict[tuple[str, str], tuple[str, ...]]:
    return anchored_workload_case_ids(
        definition.manifest_path,
        anchor_case_ids=published_case_ids_by_signature(_correctness_case_signature),
        workload_signature=_workload_signature,
        include_workload=_is_non_alternation_counted_repeat_workload,
    )


def _unanchored_case_ids(
    definition: CountedRepeatBenchmarkAnchorContractDefinition,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        definition.manifest_path,
        anchor_case_ids=published_case_ids_by_signature(_correctness_case_signature),
        workload_signature=_workload_signature,
        include_workload=_is_non_alternation_counted_repeat_workload,
    )


@pytest.mark.parametrize(
    "definition",
    COUNTED_REPEAT_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_counted_repeat_manifest_keeps_expected_non_alternation_rows_in_scope(
    definition: CountedRepeatBenchmarkAnchorContractDefinition,
) -> None:
    workloads = load_manifest(definition.manifest_path).workloads
    assert tuple(
        workload.workload_id
        for workload in workloads
        if _is_non_alternation_counted_repeat_workload(workload)
    ) == _expected_workload_ids(definition.expected_anchor_case_ids)


@pytest.mark.parametrize(
    "definition",
    COUNTED_REPEAT_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_counted_repeat_workloads_stay_anchored_to_published_correctness_cases(
    definition: CountedRepeatBenchmarkAnchorContractDefinition,
) -> None:
    assert _unanchored_case_ids(definition) == ()


@pytest.mark.parametrize(
    "definition",
    COUNTED_REPEAT_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_counted_repeat_workloads_stay_pinned_to_exact_case_ids(
    definition: CountedRepeatBenchmarkAnchorContractDefinition,
) -> None:
    assert _anchored_case_ids(definition) == definition.expected_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    COUNTED_REPEAT_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_counted_repeat_workload_callbacks_match_anchor_case_results(
    definition: CountedRepeatBenchmarkAnchorContractDefinition,
) -> None:
    manifest = load_manifest(definition.manifest_path)
    workloads_by_id = {
        workload.workload_id: workload
        for workload in manifest.workloads
        if _is_non_alternation_counted_repeat_workload(workload)
    }
    published_cases = published_cases_by_id()

    for (_, workload_id), case_ids in definition.expected_anchor_case_ids.items():
        assert len(case_ids) == 1
        case_id = case_ids[0]

        assert workload_id in workloads_by_id
        assert case_id in published_cases

        workload = workloads_by_id[workload_id]
        case = published_cases[case_id]
        observed = run_benchmark_workload_with_cpython(workload)
        expected = run_correctness_case_with_cpython(case)

        if workload.operation == "module.compile":
            assert_pattern_parity("stdlib", observed, expected)
        else:
            assert_match_result_parity(
                "stdlib",
                observed,
                expected,
                check_regs=True,
            )
