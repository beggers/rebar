from __future__ import annotations

import pathlib
import re
import unittest
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
NESTED_GROUP_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py"

from rebar_harness.benchmarks import build_callable, load_manifest
from tests.benchmarks.correctness_anchor_support import (
    anchored_workload_case_ids,
    freeze_signature_value,
    published_case_ids_by_signature,
    published_cases_by_id,
    unanchored_workload_ids,
)
from tests.python.fixture_parity_support import (
    assert_match_result_parity,
    assert_pattern_parity,
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


def _run_correctness_case_with_cpython(case: Any) -> object:
    if case.operation == "compile":
        return re.compile(case.pattern_payload(), case.flags or 0)

    if case.operation == "module_call":
        if case.helper is None:
            raise AssertionError(f"expected nested-group helper for {case.case_id!r}")
        return getattr(re, case.helper)(*case.args, **case.kwargs)

    if case.operation == "pattern_call":
        if case.helper is None:
            raise AssertionError(f"expected nested-group helper for {case.case_id!r}")
        compiled = re.compile(case.pattern_payload(), case.flags or 0)
        return getattr(compiled, case.helper)(*case.args, **case.kwargs)

    raise AssertionError(
        f"unexpected nested-group correctness operation {case.operation!r}"
    )


def _run_benchmark_workload_with_cpython(workload: Any) -> object:
    re.purge()
    callback = build_callable(re, "re", workload)
    result = callback()
    re.purge()
    return result


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

    def test_measured_nested_group_workload_callbacks_match_anchor_case_results(
        self,
    ) -> None:
        manifest = load_manifest(NESTED_GROUP_MANIFEST_PATH)
        workloads_by_id = {
            workload.workload_id: workload
            for workload in manifest.workloads
            if workload.workload_id not in EXPECTED_NESTED_GROUP_KNOWN_GAP_WORKLOAD_IDS
        }
        published_cases = published_cases_by_id()

        for (_, workload_id), case_ids in EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS.items():
            self.assertEqual(len(case_ids), 1)
            case_id = case_ids[0]

            with self.subTest(workload_id=workload_id, case_id=case_id):
                self.assertIn(workload_id, workloads_by_id)
                self.assertIn(case_id, published_cases)
                workload = workloads_by_id[workload_id]
                case = published_cases[case_id]
                observed = _run_benchmark_workload_with_cpython(workload)
                expected = _run_correctness_case_with_cpython(case)

                if workload.operation == "module.compile":
                    assert_pattern_parity("stdlib", observed, expected)
                else:
                    assert_match_result_parity(
                        "stdlib",
                        observed,
                        expected,
                        check_regs=True,
                    )


if __name__ == "__main__":
    unittest.main()
