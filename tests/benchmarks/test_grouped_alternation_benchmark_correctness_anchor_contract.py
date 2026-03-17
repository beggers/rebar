from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import pathlib
from typing import Any

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
GROUPED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py"
)
GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_replacement_boundary.py"
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


@dataclass(frozen=True, slots=True)
class GroupedAlternationBenchmarkAnchorContractDefinition:
    name: str
    manifest_path: pathlib.Path
    legacy_workload_ids: frozenset[str]
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    expected_legacy_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    callback_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    correctness_case_signature: Callable[[Any], tuple[Any, ...] | None]
    workload_signature: Callable[[Any], tuple[Any, ...]]


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
        return ("module.compile", workload.pattern, (), (), workload.flags, workload.text_model)
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


def _anchored_case_ids(
    definition: GroupedAlternationBenchmarkAnchorContractDefinition,
) -> dict[tuple[str, str], tuple[str, ...]]:
    return anchored_workload_case_ids(
        definition.manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
    )


def _unanchored_case_ids(
    definition: GroupedAlternationBenchmarkAnchorContractDefinition,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        definition.manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
    )


def _expected_measured_workload_ids(
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]],
) -> tuple[str, ...]:
    return tuple(workload_id for _, workload_id in expected_anchor_case_ids)


GROUPED_ALTERNATION_DEFINITIONS = (
    GroupedAlternationBenchmarkAnchorContractDefinition(
        name="grouped-alternation",
        manifest_path=GROUPED_ALTERNATION_MANIFEST_PATH,
        legacy_workload_ids=EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS,
        expected_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS,
        expected_legacy_anchor_case_ids=(
            EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS
        ),
        callback_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS,
        correctness_case_signature=_grouped_alternation_correctness_case_signature,
        workload_signature=_grouped_alternation_workload_signature,
    ),
    GroupedAlternationBenchmarkAnchorContractDefinition(
        name="grouped-alternation-replacement",
        manifest_path=GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        legacy_workload_ids=(
            EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_WORKLOAD_IDS
        ),
        expected_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS,
        expected_legacy_anchor_case_ids=(
            EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_ANCHOR_CASE_IDS
        ),
        callback_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS,
        correctness_case_signature=(
            _grouped_alternation_replacement_correctness_case_signature
        ),
        workload_signature=_grouped_alternation_replacement_workload_signature,
    ),
)


@pytest.mark.parametrize(
    "definition",
    GROUPED_ALTERNATION_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_grouped_alternation_manifest_keeps_expected_legacy_workloads_on_measured_surface(
    definition: GroupedAlternationBenchmarkAnchorContractDefinition,
) -> None:
    workloads = load_manifest(definition.manifest_path).workloads
    assert {
        workload.workload_id
        for workload in workloads
        if workload.workload_id in definition.legacy_workload_ids
    } == definition.legacy_workload_ids
    assert tuple(workload.workload_id for workload in workloads) == (
        _expected_measured_workload_ids(definition.expected_anchor_case_ids)
    )


@pytest.mark.parametrize(
    "definition",
    GROUPED_ALTERNATION_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_grouped_alternation_workloads_stay_anchored_to_published_correctness_cases(
    definition: GroupedAlternationBenchmarkAnchorContractDefinition,
) -> None:
    assert _unanchored_case_ids(definition) == ()


@pytest.mark.parametrize(
    "definition",
    GROUPED_ALTERNATION_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_grouped_alternation_workloads_stay_pinned_to_exact_case_ids(
    definition: GroupedAlternationBenchmarkAnchorContractDefinition,
) -> None:
    assert _anchored_case_ids(definition) == definition.expected_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    GROUPED_ALTERNATION_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_grouped_alternation_legacy_workloads_stay_pinned_to_published_case_ids(
    definition: GroupedAlternationBenchmarkAnchorContractDefinition,
) -> None:
    assert {
        key: case_ids
        for key, case_ids in _anchored_case_ids(definition).items()
        if key[1] in definition.legacy_workload_ids
    } == definition.expected_legacy_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    GROUPED_ALTERNATION_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_grouped_alternation_workload_callbacks_match_anchor_case_results(
    definition: GroupedAlternationBenchmarkAnchorContractDefinition,
) -> None:
    manifest = load_manifest(definition.manifest_path)
    workloads_by_id = {
        workload.workload_id: workload for workload in manifest.workloads
    }
    published_cases = published_cases_by_id()

    for (_, workload_id), case_ids in definition.callback_anchor_case_ids.items():
        assert len(case_ids) == 1
        case_id = case_ids[0]

        assert workload_id in workloads_by_id
        assert case_id in published_cases
        assert run_benchmark_workload_with_cpython(workloads_by_id[workload_id]) == (
            run_correctness_case_with_cpython(published_cases[case_id])
        )
