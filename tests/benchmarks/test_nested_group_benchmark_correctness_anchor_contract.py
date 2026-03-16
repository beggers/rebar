from __future__ import annotations

import pathlib
import unittest
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
NESTED_GROUP_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py"

from rebar_harness.benchmarks import load_manifest
from tests.benchmarks.correctness_anchor_support import (
    anchored_workload_case_ids,
    freeze_signature_value,
    published_case_ids_by_signature,
    unanchored_workload_ids,
)


EXPECTED_NESTED_GROUP_KNOWN_GAP_WORKLOAD_IDS = frozenset(
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


def _correctness_case_signature(case: Any) -> tuple[Any, ...] | None:
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


def _benchmark_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return ("module.compile", workload.pattern, (), (), workload.flags, workload.text_model)
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
    raise AssertionError(f"unexpected nested-group workload operation {workload.operation!r}")


def _measured_nested_group_workload_ids(manifest_path: pathlib.Path) -> tuple[str, ...]:
    workloads = load_manifest(manifest_path).workloads
    return tuple(
        workload.workload_id
        for workload in workloads
        if workload.workload_id not in EXPECTED_NESTED_GROUP_KNOWN_GAP_WORKLOAD_IDS
    )


def _unanchored_measured_nested_group_workload_ids(
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(_correctness_case_signature),
        workload_signature=_benchmark_workload_signature,
        include_workload=lambda workload: (
            workload.workload_id not in EXPECTED_NESTED_GROUP_KNOWN_GAP_WORKLOAD_IDS
        ),
    )


def _anchored_nested_group_workload_case_ids(
    manifest_path: pathlib.Path,
) -> dict[tuple[str, str], tuple[str, ...]]:
    return anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(_correctness_case_signature),
        workload_signature=_benchmark_workload_signature,
        include_workload=lambda workload: (
            workload.workload_id not in EXPECTED_NESTED_GROUP_KNOWN_GAP_WORKLOAD_IDS
        ),
    )


class NestedGroupBenchmarkCorrectnessAnchorContractTest(unittest.TestCase):
    maxDiff = None

    def test_nested_group_manifest_keeps_the_expected_gap_pair_out_of_scope(self) -> None:
        workloads = load_manifest(NESTED_GROUP_MANIFEST_PATH).workloads
        self.assertEqual(
            {
                workload.workload_id
                for workload in workloads
                if workload.workload_id in EXPECTED_NESTED_GROUP_KNOWN_GAP_WORKLOAD_IDS
            },
            EXPECTED_NESTED_GROUP_KNOWN_GAP_WORKLOAD_IDS,
        )
        self.assertEqual(
            _measured_nested_group_workload_ids(NESTED_GROUP_MANIFEST_PATH),
            tuple(
                workload_id
                for _, workload_id in EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS
            ),
        )

    def test_measured_nested_group_workloads_stay_anchored_to_published_correctness_cases(
        self,
    ) -> None:
        self.assertEqual(
            _unanchored_measured_nested_group_workload_ids(NESTED_GROUP_MANIFEST_PATH),
            (),
        )

    def test_measured_nested_group_workloads_stay_pinned_to_exact_case_ids(self) -> None:
        self.assertEqual(
            _anchored_nested_group_workload_case_ids(NESTED_GROUP_MANIFEST_PATH),
            EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS,
        )


if __name__ == "__main__":
    unittest.main()
