from __future__ import annotations

from functools import cache
import pathlib
import re
from typing import Any

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
OPEN_ENDED_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "open_ended_quantified_group_boundary.py"
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
from tests.python.test_open_ended_quantified_group_parity_suite import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
)


# These rows intentionally do not anchor to the published correctness fixtures yet:
# twenty-four bytes follow-on workloads are covered through direct parity cases in the
# Python suite, and two str rows are benchmark-specific follow-ons that still need
# explicit benchmark-side pinning.
EXPECTED_SPECIAL_UNANCHORED_WORKLOAD_IDS = (
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
    ): ("broader-range-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",),
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

DIRECT_PARITY_BYTES_CASES = (
    *OPEN_ENDED_ALTERNATION_BYTES_CASES,
    *OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    *OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    *BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    *BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    *BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
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


def _benchmark_workload_signature(workload: Any) -> tuple[Any, ...]:
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
                [workload.pattern_payload(), workload.haystack_payload()]
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
        f"unexpected open-ended benchmark workload operation {workload.operation!r}"
    )


@cache
def _manifest_workloads_by_id() -> dict[str, Any]:
    return {
        workload.workload_id: workload
        for workload in load_manifest(OPEN_ENDED_MANIFEST_PATH).workloads
    }


@cache
def _direct_parity_bytes_case_ids_by_signature(
) -> dict[tuple[str, bytes, bytes], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[str, bytes, bytes], list[str]] = {}

    for case in DIRECT_PARITY_BYTES_CASES:
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


def _anchored_workload_case_ids() -> dict[tuple[str, str], tuple[str, ...]]:
    return anchored_workload_case_ids(
        OPEN_ENDED_MANIFEST_PATH,
        anchor_case_ids=published_case_ids_by_signature(_correctness_case_signature),
        workload_signature=_benchmark_workload_signature,
        include_workload=lambda workload: (
            workload.workload_id not in EXPECTED_SPECIAL_UNANCHORED_WORKLOAD_IDS
        ),
    )


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
    finally:
        re.purge()

    raise AssertionError(
        f"unexpected open-ended benchmark workload operation {workload.operation!r}"
    )


def test_open_ended_manifest_keeps_expected_special_unanchored_workloads_explicit() -> None:
    assert unanchored_workload_ids(
        OPEN_ENDED_MANIFEST_PATH,
        anchor_case_ids=published_case_ids_by_signature(_correctness_case_signature),
        workload_signature=_benchmark_workload_signature,
    ) == EXPECTED_SPECIAL_UNANCHORED_WORKLOAD_IDS

    assert tuple(
        workload_id for _, workload_id in EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS
    ) == tuple(
        workload_id
        for workload_id in _manifest_workloads_by_id()
        if workload_id not in EXPECTED_SPECIAL_UNANCHORED_WORKLOAD_IDS
    )


def test_open_ended_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases() -> None:
    workloads_by_id = _manifest_workloads_by_id()
    direct_parity_case_ids = _direct_parity_bytes_case_ids_by_signature()
    uncovered_workload_ids: list[str] = []

    for workload_id in EXPECTED_SPECIAL_UNANCHORED_WORKLOAD_IDS:
        workload = workloads_by_id[workload_id]
        if workload.text_model != "bytes":
            continue

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


def test_open_ended_anchored_workloads_stay_pinned_to_exact_case_ids() -> None:
    assert _anchored_workload_case_ids() == EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS


def test_open_ended_anchored_workloads_match_anchor_case_results() -> None:
    workloads_by_id = {
        workload_id: workload
        for workload_id, workload in _manifest_workloads_by_id().items()
        if workload_id not in EXPECTED_SPECIAL_UNANCHORED_WORKLOAD_IDS
    }
    published_cases = published_cases_by_id()

    for (_, workload_id), case_ids in EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS.items():
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


@pytest.mark.parametrize(
    "workload_id",
    EXPECTED_SPECIAL_UNANCHORED_WORKLOAD_IDS,
)
def test_open_ended_special_unanchored_workloads_match_manual_cpython_dispatch(
    workload_id: str,
) -> None:
    workload = _manifest_workloads_by_id()[workload_id]

    observed = run_benchmark_workload_with_cpython(workload)
    expected = _manual_expected_result(workload)

    if workload.operation == "module.compile":
        assert_pattern_parity("stdlib", observed, expected)
    else:
        assert_match_result_parity(
            "stdlib",
            observed,
            expected,
            check_regs=True,
        )
