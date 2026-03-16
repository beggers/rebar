from __future__ import annotations

from functools import cache
import pathlib
import unittest
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
NESTED_GROUP_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py"

from rebar_harness.benchmarks import load_manifest
from rebar_harness.correctness import DEFAULT_FIXTURE_PATHS, load_fixture_manifest


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


def _freeze_signature_value(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(
            (str(key), _freeze_signature_value(nested_value))
            for key, nested_value in sorted(value.items())
        )
    if isinstance(value, list):
        return tuple(_freeze_signature_value(item) for item in value)
    return value


def _correctness_case_signature(case: Any) -> tuple[Any, ...] | None:
    kwargs_signature = _freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", case.pattern, (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper == "search":
        return (
            "module.search",
            None,
            _freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper == "fullmatch":
        return (
            "pattern.fullmatch",
            case.pattern,
            _freeze_signature_value(case.serialized_args()),
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


@cache
def _published_anchor_case_ids_by_signature() -> dict[tuple[Any, ...], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[Any, ...], list[str]] = {}

    for fixture_path in DEFAULT_FIXTURE_PATHS:
        _, cases = load_fixture_manifest(fixture_path)
        for case in cases:
            signature = _correctness_case_signature(case)
            if signature is None:
                continue
            case_ids_by_signature.setdefault(signature, []).append(case.case_id)

    return {
        signature: tuple(sorted(case_ids))
        for signature, case_ids in case_ids_by_signature.items()
    }


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
    workloads = load_manifest(manifest_path).workloads
    anchor_case_ids = _published_anchor_case_ids_by_signature()

    return tuple(
        workload.workload_id
        for workload in workloads
        if workload.workload_id not in EXPECTED_NESTED_GROUP_KNOWN_GAP_WORKLOAD_IDS
        and _benchmark_workload_signature(workload) not in anchor_case_ids
    )


def _anchored_nested_group_workload_case_ids(
    manifest_path: pathlib.Path,
) -> dict[tuple[str, str], tuple[str, ...]]:
    workloads = load_manifest(manifest_path).workloads
    anchor_case_ids = _published_anchor_case_ids_by_signature()

    return {
        (manifest_path.name, workload.workload_id): anchor_case_ids.get(
            _benchmark_workload_signature(workload),
            (),
        )
        for workload in workloads
        if workload.workload_id not in EXPECTED_NESTED_GROUP_KNOWN_GAP_WORKLOAD_IDS
    }


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
