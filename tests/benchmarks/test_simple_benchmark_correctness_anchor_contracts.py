from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import pathlib
from typing import Any

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

from rebar_harness.benchmarks import load_manifest
from tests.benchmarks.correctness_anchor_support import (
    anchored_workload_case_ids,
    assert_anchored_workload_case_result_parity,
    expected_anchored_workload_case_pairs,
    freeze_signature_value,
    published_case_ids_by_signature,
    unanchored_workload_ids,
)


@dataclass(frozen=True, slots=True)
class SimpleBenchmarkAnchorContractDefinition:
    name: str
    manifest_paths: tuple[pathlib.Path, ...]
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    include_workload: Callable[[Any], bool]
    correctness_case_signature: Callable[[Any], tuple[Any, ...] | None]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    run_callback_result_parity: bool = False
    expected_excluded_workload_ids: frozenset[str] = frozenset()


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
    raise AssertionError(
        f"unexpected nested-group workload operation {workload.operation!r}"
    )


def _is_measured_nested_group_workload(workload: Any) -> bool:
    return workload.workload_id not in EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS


SIMPLE_BENCHMARK_DEFINITIONS = (
    SimpleBenchmarkAnchorContractDefinition(
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
    SimpleBenchmarkAnchorContractDefinition(
        name="optional-group-conditional",
        manifest_paths=(OPTIONAL_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS,
        include_workload=_is_optional_group_conditional_workload,
        correctness_case_signature=_optional_group_correctness_case_signature,
        workload_signature=_optional_group_workload_signature,
        run_callback_result_parity=True,
    ),
    SimpleBenchmarkAnchorContractDefinition(
        name="nested-group",
        manifest_paths=(NESTED_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS,
        include_workload=_is_measured_nested_group_workload,
        correctness_case_signature=_nested_group_correctness_case_signature,
        workload_signature=_nested_group_workload_signature,
        run_callback_result_parity=True,
        expected_excluded_workload_ids=EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS,
    ),
)

SIMPLE_BENCHMARK_MANIFEST_DEFINITIONS = tuple(
    (definition, manifest_path)
    for definition in SIMPLE_BENCHMARK_DEFINITIONS
    for manifest_path in definition.manifest_paths
)
SIMPLE_BENCHMARK_MANIFEST_IDS = [
    f"{definition.name}:{manifest_path.name}"
    for definition, manifest_path in SIMPLE_BENCHMARK_MANIFEST_DEFINITIONS
]
SIMPLE_BENCHMARK_CALLBACK_PARITY_DEFINITIONS = tuple(
    definition
    for definition in SIMPLE_BENCHMARK_DEFINITIONS
    if definition.run_callback_result_parity
)


def _expected_workload_ids(
    definition: SimpleBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return tuple(
        workload_id
        for (manifest_name, workload_id), _ in definition.expected_anchor_case_ids.items()
        if manifest_name == manifest_path.name
    )


def _expected_anchor_case_ids_for_manifest(
    definition: SimpleBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> dict[tuple[str, str], tuple[str, ...]]:
    return {
        (manifest_name, workload_id): case_ids
        for (manifest_name, workload_id), case_ids in definition.expected_anchor_case_ids.items()
        if manifest_name == manifest_path.name
    }


def _anchored_case_ids_for_manifest(
    definition: SimpleBenchmarkAnchorContractDefinition,
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
    definition: SimpleBenchmarkAnchorContractDefinition,
) -> dict[tuple[str, str], tuple[str, ...]]:
    anchored_case_ids: dict[tuple[str, str], tuple[str, ...]] = {}
    for manifest_path in definition.manifest_paths:
        anchored_case_ids.update(
            _anchored_case_ids_for_manifest(definition, manifest_path)
        )
    return anchored_case_ids


def _unanchored_case_ids(
    definition: SimpleBenchmarkAnchorContractDefinition,
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


def _expected_anchored_pairs(
    definition: SimpleBenchmarkAnchorContractDefinition,
) -> tuple[Any, ...]:
    anchored_pairs = []
    for manifest_path in definition.manifest_paths:
        anchored_pairs.extend(
            expected_anchored_workload_case_pairs(
                manifest_path,
                expected_anchor_case_ids=_expected_anchor_case_ids_for_manifest(
                    definition,
                    manifest_path,
                ),
                include_workload=definition.include_workload,
            )
        )
    return tuple(anchored_pairs)


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    SIMPLE_BENCHMARK_MANIFEST_DEFINITIONS,
    ids=SIMPLE_BENCHMARK_MANIFEST_IDS,
)
def test_simple_benchmark_manifest_keeps_expected_workloads_in_scope(
    definition: SimpleBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    workloads = load_manifest(manifest_path).workloads
    assert {
        workload.workload_id
        for workload in workloads
        if workload.workload_id in definition.expected_excluded_workload_ids
    } == definition.expected_excluded_workload_ids
    assert tuple(
        workload.workload_id
        for workload in workloads
        if definition.include_workload(workload)
    ) == _expected_workload_ids(definition, manifest_path)


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    SIMPLE_BENCHMARK_MANIFEST_DEFINITIONS,
    ids=SIMPLE_BENCHMARK_MANIFEST_IDS,
)
def test_simple_benchmark_workloads_stay_anchored_to_published_correctness_cases(
    definition: SimpleBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    assert _unanchored_case_ids(definition, manifest_path) == ()


@pytest.mark.parametrize(
    "definition",
    SIMPLE_BENCHMARK_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_simple_benchmark_workloads_stay_pinned_to_exact_case_ids(
    definition: SimpleBenchmarkAnchorContractDefinition,
) -> None:
    assert _anchored_case_ids(definition) == definition.expected_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    SIMPLE_BENCHMARK_CALLBACK_PARITY_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_simple_benchmark_workload_callbacks_match_anchor_case_results(
    definition: SimpleBenchmarkAnchorContractDefinition,
) -> None:
    assert_anchored_workload_case_result_parity(_expected_anchored_pairs(definition))
