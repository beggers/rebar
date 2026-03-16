from __future__ import annotations

import pathlib
import re
import unittest
from typing import Any


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
GROUPED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py"
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
    ): ("pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",),
}

EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS = {
    (
        "grouped_alternation_boundary.py",
        "module-sub-template-nested-grouped-alternation-warm-gap",
    ): ("module-sub-template-nested-group-alternation-numbered-wrapper-str",),
    (
        "grouped_alternation_boundary.py",
        "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
    ): ("pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",),
}

EXPECTED_GROUPED_ALTERNATION_MEASURED_WORKLOAD_IDS = tuple(
    workload_id for _, workload_id in EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS
)


def _correctness_case_signature(case: Any) -> tuple[Any, ...] | None:
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


def _benchmark_workload_args(workload: Any) -> tuple[Any, ...]:
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


def _benchmark_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return ("module.compile", workload.pattern, (), (), workload.flags, workload.text_model)
    if workload.operation in {"module.search", "module.sub", "module.subn"}:
        return (
            workload.operation,
            None,
            _benchmark_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"pattern.fullmatch", "pattern.sub", "pattern.subn"}:
        return (
            workload.operation,
            workload.pattern,
            _benchmark_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected grouped-alternation benchmark workload operation {workload.operation!r}"
    )


def _run_correctness_case_with_cpython(case: Any) -> object:
    if case.operation == "module_call":
        if case.helper is None:
            raise AssertionError(
                f"expected grouped-alternation helper for {case.case_id!r}"
            )
        return getattr(re, case.helper)(*case.args, **case.kwargs)

    if case.operation == "pattern_call":
        if case.helper is None:
            raise AssertionError(
                f"expected grouped-alternation helper for {case.case_id!r}"
            )
        compiled = re.compile(case.pattern_payload(), case.flags or 0)
        return getattr(compiled, case.helper)(*case.args, **case.kwargs)

    raise AssertionError(
        "unexpected grouped-alternation correctness operation "
        f"{case.operation!r}"
    )


def _measured_grouped_alternation_workload_ids(
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    workloads = load_manifest(manifest_path).workloads
    return tuple(workload.workload_id for workload in workloads)


def _unanchored_measured_grouped_alternation_workload_ids(
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(_correctness_case_signature),
        workload_signature=_benchmark_workload_signature,
        include_workload=lambda workload: True,
    )


def _anchored_grouped_alternation_workload_case_ids(
    manifest_path: pathlib.Path,
) -> dict[tuple[str, str], tuple[str, ...]]:
    return anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(_correctness_case_signature),
        workload_signature=_benchmark_workload_signature,
        include_workload=lambda workload: True,
    )


class GroupedAlternationBenchmarkCorrectnessAnchorContractTest(unittest.TestCase):
    maxDiff = None

    def test_grouped_alternation_manifest_keeps_legacy_wrapper_pair_on_measured_surface(
        self,
    ) -> None:
        workloads = load_manifest(GROUPED_ALTERNATION_MANIFEST_PATH).workloads
        self.assertEqual(
            {
                workload.workload_id
                for workload in workloads
                if workload.workload_id
                in EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS
            },
            EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS,
        )
        self.assertEqual(
            _measured_grouped_alternation_workload_ids(
                GROUPED_ALTERNATION_MANIFEST_PATH
            ),
            EXPECTED_GROUPED_ALTERNATION_MEASURED_WORKLOAD_IDS,
        )

    def test_measured_grouped_alternation_workloads_stay_anchored_to_published_correctness_cases(
        self,
    ) -> None:
        self.assertEqual(
            _unanchored_measured_grouped_alternation_workload_ids(
                GROUPED_ALTERNATION_MANIFEST_PATH
            ),
            (),
        )

    def test_measured_grouped_alternation_workloads_stay_pinned_to_exact_case_ids(
        self,
    ) -> None:
        self.assertEqual(
            _anchored_grouped_alternation_workload_case_ids(
                GROUPED_ALTERNATION_MANIFEST_PATH
            ),
            EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS,
        )

    def test_legacy_wrapper_workloads_stay_pinned_to_published_wrapper_case_ids(
        self,
    ) -> None:
        self.assertEqual(
            {
                key: case_ids
                for key, case_ids in _anchored_grouped_alternation_workload_case_ids(
                    GROUPED_ALTERNATION_MANIFEST_PATH
                ).items()
                if key[1] in EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS
            },
            EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS,
        )

    def test_legacy_wrapper_workload_callbacks_match_anchor_case_results(self) -> None:
        manifest = load_manifest(GROUPED_ALTERNATION_MANIFEST_PATH)
        workloads_by_id = {
            workload.workload_id: workload for workload in manifest.workloads
        }
        published_cases = published_cases_by_id()

        for (_, workload_id), case_ids in (
            EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS.items()
        ):
            self.assertEqual(len(case_ids), 1)
            case_id = case_ids[0]

            with self.subTest(workload_id=workload_id, case_id=case_id):
                self.assertIn(workload_id, workloads_by_id)
                self.assertIn(case_id, published_cases)
                self.assertEqual(
                    run_benchmark_workload_with_cpython(workloads_by_id[workload_id]),
                    _run_correctness_case_with_cpython(published_cases[case_id]),
                )


if __name__ == "__main__":
    unittest.main()
