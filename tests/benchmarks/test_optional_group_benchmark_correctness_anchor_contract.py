from __future__ import annotations

import pathlib
import re
import unittest
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
OPTIONAL_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.py"
)
OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID = (
    "module-search-numbered-optional-group-conditional-cold-gap"
)

from rebar_harness.benchmarks import load_manifest
from tests.benchmarks.correctness_anchor_support import (
    anchored_workload_case_ids,
    freeze_signature_value,
    published_case_ids_by_signature,
    published_cases_by_id,
    run_benchmark_workload_with_cpython,
    unanchored_workload_ids,
)
from tests.python.fixture_parity_support import assert_match_result_parity


EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS = {
    (
        "optional_group_boundary.py",
        OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID,
    ): ("optional-group-conditional-module-search-present-str",),
}


def _correctness_case_signature(case: Any) -> tuple[Any, ...] | None:
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


def _benchmark_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation != "module.search":
        raise AssertionError(
            f"unexpected optional-group benchmark workload operation {workload.operation!r}"
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


def _unanchored_optional_group_conditional_workload_ids(
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(_correctness_case_signature),
        workload_signature=_benchmark_workload_signature,
        include_workload=_is_optional_group_conditional_workload,
    )


def _anchored_optional_group_conditional_workload_case_ids(
    manifest_path: pathlib.Path,
) -> dict[tuple[str, str], tuple[str, ...]]:
    return anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(_correctness_case_signature),
        workload_signature=_benchmark_workload_signature,
        include_workload=_is_optional_group_conditional_workload,
    )


def _run_correctness_case_with_cpython(case: Any) -> object:
    if case.operation != "module_call" or case.helper != "search":
        raise AssertionError(
            f"unexpected optional-group correctness operation {case.operation!r}"
        )

    return getattr(re, case.helper)(*case.args, **case.kwargs)


class OptionalGroupBenchmarkCorrectnessAnchorContractTest(unittest.TestCase):
    maxDiff = None

    def test_conditional_anchor_row_stays_anchored_to_published_correctness_case(
        self,
    ) -> None:
        self.assertEqual(
            _unanchored_optional_group_conditional_workload_ids(
                OPTIONAL_GROUP_MANIFEST_PATH
            ),
            (),
        )

    def test_conditional_anchor_row_stays_pinned_to_exact_case_id(self) -> None:
        self.assertEqual(
            _anchored_optional_group_conditional_workload_case_ids(
                OPTIONAL_GROUP_MANIFEST_PATH
            ),
            EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS,
        )

    def test_conditional_anchor_row_matches_anchored_cpython_search_result(
        self,
    ) -> None:
        manifest = load_manifest(OPTIONAL_GROUP_MANIFEST_PATH)
        workloads_by_id = {
            workload.workload_id: workload
            for workload in manifest.workloads
            if _is_optional_group_conditional_workload(workload)
        }
        published_cases = published_cases_by_id()
        case_id = EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS[
            ("optional_group_boundary.py", OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID)
        ][0]

        self.assertIn(OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID, workloads_by_id)
        self.assertIn(case_id, published_cases)

        observed = run_benchmark_workload_with_cpython(
            workloads_by_id[OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID]
        )
        expected = _run_correctness_case_with_cpython(published_cases[case_id])
        assert_match_result_parity(
            "stdlib",
            observed,
            expected,
            check_regs=True,
        )


if __name__ == "__main__":
    unittest.main()
