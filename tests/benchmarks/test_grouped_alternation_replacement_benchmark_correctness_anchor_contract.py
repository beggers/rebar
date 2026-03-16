from __future__ import annotations

from functools import cache
import pathlib
import unittest
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_replacement_boundary.py"
)

from rebar_harness.benchmarks import load_manifest
from rebar_harness.correctness import DEFAULT_FIXTURE_PATHS, load_fixture_manifest


EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_KNOWN_GAP_WORKLOAD_IDS = frozenset(
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
}
EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_KNOWN_GAP_ANCHOR_CASE_IDS = {
    (
        "grouped_alternation_replacement_boundary.py",
        "module-sub-template-nested-grouped-alternation-cold-gap",
    ): ("module-sub-template-nested-group-alternation-numbered-outer-str",),
    (
        "grouped_alternation_replacement_boundary.py",
        "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
    ): ("pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",),
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

    if case.operation == "module_call" and case.helper in {"sub", "subn"}:
        return (
            f"module.{case.helper}",
            case.pattern,
            _freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            _freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _benchmark_workload_args(workload: Any) -> tuple[Any, ...]:
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
    return _freeze_signature_value(args)


def _benchmark_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation in {"module.sub", "module.subn"}:
        return (
            workload.operation,
            None,
            _benchmark_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        return (
            workload.operation,
            workload.pattern,
            _benchmark_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        "unexpected grouped-alternation replacement workload operation "
        f"{workload.operation!r}"
    )


@cache
def _published_anchor_case_ids_by_signature() -> dict[tuple[Any, ...], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[Any, ...], list[str]] = {}

    for fixture_path in DEFAULT_FIXTURE_PATHS:
        for case in load_fixture_manifest(fixture_path).cases:
            signature = _correctness_case_signature(case)
            if signature is None:
                continue
            case_ids_by_signature.setdefault(signature, []).append(case.case_id)

    return {
        signature: tuple(sorted(case_ids))
        for signature, case_ids in case_ids_by_signature.items()
    }


def _measured_grouped_alternation_replacement_workload_ids(
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    workloads = load_manifest(manifest_path).workloads
    return tuple(
        workload.workload_id
        for workload in workloads
        if workload.workload_id
        not in EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_KNOWN_GAP_WORKLOAD_IDS
    )


def _unanchored_measured_grouped_alternation_replacement_workload_ids(
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    workloads = load_manifest(manifest_path).workloads
    anchor_case_ids = _published_anchor_case_ids_by_signature()

    return tuple(
        workload.workload_id
        for workload in workloads
        if workload.workload_id
        not in EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_KNOWN_GAP_WORKLOAD_IDS
        and _benchmark_workload_signature(workload) not in anchor_case_ids
    )


def _anchored_grouped_alternation_replacement_workload_case_ids(
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
        if workload.workload_id
        not in EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_KNOWN_GAP_WORKLOAD_IDS
    }


def _known_gap_grouped_alternation_replacement_workload_case_ids(
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
        if workload.workload_id
        in EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_KNOWN_GAP_WORKLOAD_IDS
    }


class GroupedAlternationReplacementBenchmarkCorrectnessAnchorContractTest(
    unittest.TestCase
):
    maxDiff = None

    def test_grouped_alternation_replacement_manifest_keeps_expected_nested_gap_pair_out_of_scope(
        self,
    ) -> None:
        workloads = load_manifest(GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH).workloads
        self.assertEqual(
            {
                workload.workload_id
                for workload in workloads
                if workload.workload_id
                in EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_KNOWN_GAP_WORKLOAD_IDS
            },
            EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_KNOWN_GAP_WORKLOAD_IDS,
        )
        self.assertEqual(
            _measured_grouped_alternation_replacement_workload_ids(
                GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH
            ),
            tuple(
                workload_id
                for _, workload_id in (
                    EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS
                )
            ),
        )

    def test_measured_grouped_alternation_replacement_workloads_stay_anchored_to_published_correctness_cases(
        self,
    ) -> None:
        self.assertEqual(
            _unanchored_measured_grouped_alternation_replacement_workload_ids(
                GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH
            ),
            (),
        )

    def test_measured_grouped_alternation_replacement_workloads_stay_pinned_to_exact_case_ids(
        self,
    ) -> None:
        self.assertEqual(
            _anchored_grouped_alternation_replacement_workload_case_ids(
                GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH
            ),
            EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS,
        )

    def test_known_gap_grouped_alternation_replacement_workloads_stay_pinned_to_published_nested_case_ids(
        self,
    ) -> None:
        self.assertEqual(
            _known_gap_grouped_alternation_replacement_workload_case_ids(
                GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH
            ),
            EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_KNOWN_GAP_ANCHOR_CASE_IDS,
        )


if __name__ == "__main__":
    unittest.main()
