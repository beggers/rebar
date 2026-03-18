from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
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
EXACT_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "exact_repeat_quantified_group_boundary.py"
)
RANGED_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "ranged_repeat_quantified_group_boundary.py"
)
GROUPED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py"
)
GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_replacement_boundary.py"
)

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
class StandardBenchmarkAnchorContractDefinition:
    name: str
    manifest_paths: tuple[pathlib.Path, ...]
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    include_workload: Callable[[Any], bool]
    correctness_case_signature: Callable[[Any], tuple[Any, ...] | None]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    run_callback_result_parity: bool = False
    expected_excluded_workload_ids: frozenset[str] = frozenset()
    expected_legacy_workload_ids: frozenset[str] = frozenset()
    expected_legacy_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] = field(
        default_factory=dict
    )
    callback_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] = field(
        default_factory=dict
    )


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
    ): (
        "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
    ),
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
    ): (
        "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
    ),
}

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
        return (
            "module.compile",
            workload.pattern,
            (),
            (),
            workload.flags,
            workload.text_model,
        )
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


def _counted_repeat_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
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


def _counted_repeat_workload_signature(workload: Any) -> tuple[Any, ...]:
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
        return (
            "module.compile",
            workload.pattern,
            (),
            (),
            workload.flags,
            workload.text_model,
        )
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


def _include_all_workloads(_: Any) -> bool:
    return True


STANDARD_BENCHMARK_DEFINITIONS = (
    StandardBenchmarkAnchorContractDefinition(
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
    StandardBenchmarkAnchorContractDefinition(
        name="optional-group-conditional",
        manifest_paths=(OPTIONAL_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS,
        include_workload=_is_optional_group_conditional_workload,
        correctness_case_signature=_optional_group_correctness_case_signature,
        workload_signature=_optional_group_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="nested-group",
        manifest_paths=(NESTED_GROUP_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS,
        include_workload=_is_measured_nested_group_workload,
        correctness_case_signature=_nested_group_correctness_case_signature,
        workload_signature=_nested_group_workload_signature,
        run_callback_result_parity=True,
        expected_excluded_workload_ids=EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="exact-repeat",
        manifest_paths=(EXACT_REPEAT_MANIFEST_PATH,),
        expected_anchor_case_ids=EXACT_REPEAT_EXPECTED_ANCHOR_CASE_IDS,
        include_workload=_is_non_alternation_counted_repeat_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="ranged-repeat",
        manifest_paths=(RANGED_REPEAT_MANIFEST_PATH,),
        expected_anchor_case_ids=RANGED_REPEAT_EXPECTED_ANCHOR_CASE_IDS,
        include_workload=_is_non_alternation_counted_repeat_workload,
        correctness_case_signature=_counted_repeat_correctness_case_signature,
        workload_signature=_counted_repeat_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="grouped-alternation",
        manifest_paths=(GROUPED_ALTERNATION_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS,
        include_workload=_include_all_workloads,
        correctness_case_signature=_grouped_alternation_correctness_case_signature,
        workload_signature=_grouped_alternation_workload_signature,
        run_callback_result_parity=True,
        expected_legacy_workload_ids=EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS,
        expected_legacy_anchor_case_ids=(
            EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS
        ),
        callback_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_ANCHOR_CASE_IDS,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="grouped-alternation-replacement",
        manifest_paths=(GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,),
        expected_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS,
        include_workload=_include_all_workloads,
        correctness_case_signature=(
            _grouped_alternation_replacement_correctness_case_signature
        ),
        workload_signature=_grouped_alternation_replacement_workload_signature,
        run_callback_result_parity=True,
        expected_legacy_workload_ids=(
            EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_WORKLOAD_IDS
        ),
        expected_legacy_anchor_case_ids=(
            EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_ANCHOR_CASE_IDS
        ),
        callback_anchor_case_ids=EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS,
    ),
)

STANDARD_BENCHMARK_MANIFEST_DEFINITIONS = tuple(
    (definition, manifest_path)
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    for manifest_path in definition.manifest_paths
)
STANDARD_BENCHMARK_MANIFEST_IDS = [
    f"{definition.name}:{manifest_path.name}"
    for definition, manifest_path in STANDARD_BENCHMARK_MANIFEST_DEFINITIONS
]
STANDARD_BENCHMARK_LEGACY_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.expected_legacy_anchor_case_ids
)
STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS = tuple(
    definition
    for definition in STANDARD_BENCHMARK_DEFINITIONS
    if definition.run_callback_result_parity
)


def _expected_workload_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> tuple[str, ...]:
    return tuple(
        workload_id
        for (manifest_name, workload_id), _ in definition.expected_anchor_case_ids.items()
        if manifest_name == manifest_path.name
    )


def _expected_anchor_case_ids_for_manifest(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] | None = None,
) -> dict[tuple[str, str], tuple[str, ...]]:
    anchor_case_ids = (
        definition.expected_anchor_case_ids
        if expected_anchor_case_ids is None
        else expected_anchor_case_ids
    )
    return {
        (manifest_name, workload_id): case_ids
        for (manifest_name, workload_id), case_ids in anchor_case_ids.items()
        if manifest_name == manifest_path.name
    }


def _anchored_case_ids_for_manifest(
    definition: StandardBenchmarkAnchorContractDefinition,
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
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[tuple[str, str], tuple[str, ...]]:
    anchored_case_ids: dict[tuple[str, str], tuple[str, ...]] = {}
    for manifest_path in definition.manifest_paths:
        anchored_case_ids.update(
            _anchored_case_ids_for_manifest(definition, manifest_path)
        )
    return anchored_case_ids


def _unanchored_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
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


def _expected_callback_anchor_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> dict[tuple[str, str], tuple[str, ...]]:
    if definition.callback_anchor_case_ids:
        return definition.callback_anchor_case_ids
    return definition.expected_anchor_case_ids


def _expected_anchored_pairs(
    definition: StandardBenchmarkAnchorContractDefinition,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]] | None = None,
) -> tuple[Any, ...]:
    anchored_pairs = []
    for manifest_path in definition.manifest_paths:
        manifest_anchor_case_ids = _expected_anchor_case_ids_for_manifest(
            definition,
            manifest_path,
            expected_anchor_case_ids=expected_anchor_case_ids,
        )
        if not manifest_anchor_case_ids:
            continue
        anchored_pairs.extend(
            expected_anchored_workload_case_pairs(
                manifest_path,
                expected_anchor_case_ids=manifest_anchor_case_ids,
                include_workload=definition.include_workload,
            )
        )
    return tuple(anchored_pairs)


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    STANDARD_BENCHMARK_MANIFEST_DEFINITIONS,
    ids=STANDARD_BENCHMARK_MANIFEST_IDS,
)
def test_standard_benchmark_manifest_keeps_expected_workloads_in_scope(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    workloads = load_manifest(manifest_path).workloads
    assert {
        workload.workload_id
        for workload in workloads
        if workload.workload_id in definition.expected_excluded_workload_ids
    } == definition.expected_excluded_workload_ids
    assert {
        workload.workload_id
        for workload in workloads
        if workload.workload_id in definition.expected_legacy_workload_ids
    } == definition.expected_legacy_workload_ids
    assert tuple(
        workload.workload_id
        for workload in workloads
        if definition.include_workload(workload)
    ) == _expected_workload_ids(definition, manifest_path)


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    STANDARD_BENCHMARK_MANIFEST_DEFINITIONS,
    ids=STANDARD_BENCHMARK_MANIFEST_IDS,
)
def test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases(
    definition: StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    assert _unanchored_case_ids(definition, manifest_path) == ()


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert _anchored_case_ids(definition) == definition.expected_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_LEGACY_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert {
        key: case_ids
        for key, case_ids in _anchored_case_ids(definition).items()
        if key[1] in definition.expected_legacy_workload_ids
    } == definition.expected_legacy_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS,
    ids=lambda definition: definition.name,
)
def test_standard_benchmark_workload_callbacks_match_anchor_case_results(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert_anchored_workload_case_result_parity(
        _expected_anchored_pairs(
            definition,
            expected_anchor_case_ids=_expected_callback_anchor_case_ids(definition),
        )
    )
