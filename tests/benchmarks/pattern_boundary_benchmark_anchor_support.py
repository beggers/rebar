from __future__ import annotations

from typing import Any

from tests.benchmarks.module_pattern_keyword_benchmark_anchor_support import (
    _pattern_window_positional_indexlike_workload_args,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    freeze_signature_value,
)
from tests.python.fixture_parity_support import case_pattern

_PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS = (
    "pattern-search-bounded-wildcard-ignorecase-warm-str",
    "pattern-match-bounded-wildcard-warm-str",
    "pattern-fullmatch-bounded-wildcard-purged-str",
    "pattern-findall-bounded-wildcard-warm-str",
    "pattern-finditer-bounded-wildcard-purged-str",
    "pattern-search-bounded-wildcard-endpos-miss-purged-str",
)

_PATTERN_BOUNDED_WILDCARD_CASE_IDS = (
    "workflow-pattern-search-str-bounded-wildcard-ignorecase",
    "workflow-pattern-match-str-bounded-wildcard",
    "workflow-pattern-fullmatch-str-bounded-wildcard",
    "workflow-pattern-findall-str-bounded-wildcard",
    "workflow-pattern-finditer-str-bounded-wildcard",
    "workflow-pattern-search-str-bounded-wildcard-endpos-miss",
)

_PATTERN_SEARCH_VERBOSE_REGRESSION_WORKLOAD_IDS = (
    "pattern-search-verbose-regression-warm-str",
    "pattern-search-verbose-regression-digits-warm-str",
    "pattern-search-verbose-regression-too-many-digits-purged-str",
    "pattern-search-verbose-regression-warm-bytes",
    "pattern-search-verbose-regression-digits-warm-bytes",
    "pattern-search-verbose-regression-too-many-digits-purged-bytes",
)

_PATTERN_FULLMATCH_VERBOSE_REGRESSION_WORKLOAD_IDS = (
    "pattern-fullmatch-verbose-regression-warm-str",
    "pattern-fullmatch-verbose-regression-alpha-warm-str",
    "pattern-fullmatch-verbose-regression-lowercase-key-purged-str",
    "pattern-fullmatch-verbose-regression-warm-bytes",
    "pattern-fullmatch-verbose-regression-alpha-warm-bytes",
    "pattern-fullmatch-verbose-regression-lowercase-key-purged-bytes",
)

_PATTERN_VERBOSE_REGRESSION_WORKLOAD_IDS = (
    *_PATTERN_SEARCH_VERBOSE_REGRESSION_WORKLOAD_IDS,
    *_PATTERN_FULLMATCH_VERBOSE_REGRESSION_WORKLOAD_IDS,
)

_PATTERN_SEARCH_VERBOSE_REGRESSION_CASE_IDS = (
    "workflow-pattern-search-str-verbose-regression",
    "workflow-pattern-search-str-verbose-regression-digits",
    "workflow-pattern-search-str-verbose-regression-too-many-digits",
    "workflow-pattern-search-bytes-verbose-regression",
    "workflow-pattern-search-bytes-verbose-regression-digits",
    "workflow-pattern-search-bytes-verbose-regression-too-many-digits",
)

_PATTERN_FULLMATCH_VERBOSE_REGRESSION_CASE_IDS = (
    "workflow-pattern-fullmatch-str-verbose-regression",
    "workflow-pattern-fullmatch-str-verbose-regression-alpha",
    "workflow-pattern-fullmatch-str-verbose-regression-lowercase-key",
    "workflow-pattern-fullmatch-bytes-verbose-regression",
    "workflow-pattern-fullmatch-bytes-verbose-regression-alpha",
    "workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key",
)

_PATTERN_VERBOSE_REGRESSION_CASE_IDS = (
    *_PATTERN_SEARCH_VERBOSE_REGRESSION_CASE_IDS,
    *_PATTERN_FULLMATCH_VERBOSE_REGRESSION_CASE_IDS,
)

_PATTERN_VERBOSE_REGRESSION_PATTERN = (
    "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"
)
_PATTERN_BOUNDARY_OPERATIONS = frozenset(
    {"pattern.search", "pattern.match", "pattern.fullmatch"}
)


def _pattern_bounded_wildcard_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.case_id not in _PATTERN_BOUNDED_WILDCARD_CASE_IDS:
        return None
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch", "findall", "finditer"}:
        return None
    return (
        f"pattern.{case.helper}",
        case_pattern(case),
        freeze_signature_value(case.serialized_args()),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def _pattern_bounded_wildcard_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_bounded_wildcard_workload(workload):
        raise AssertionError(
            "unexpected pattern bounded-wildcard workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(
            list(_pattern_window_positional_indexlike_workload_args(workload))
        ),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_pattern_bounded_wildcard_workload(workload: Any) -> bool:
    return (
        workload.workload_id in _PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS
        and workload.operation in {
            "pattern.search",
            "pattern.match",
            "pattern.fullmatch",
            "pattern.findall",
            "pattern.finditer",
        }
        and workload.pattern == "a.c"
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
        and workload.text_model in {"str", "bytes"}
        and workload.pos is not None
        and workload.endpos is not None
        and not workload.kwargs
    )


def _pattern_verbose_regression_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.case_id not in _PATTERN_VERBOSE_REGRESSION_CASE_IDS:
        return None
    if (
        case.operation != "pattern_call"
        or case.kwargs
        or case.helper not in {"search", "fullmatch"}
    ):
        return None
    return (
        f"pattern.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def _pattern_verbose_regression_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_verbose_regression_workload(workload):
        raise AssertionError(
            "unexpected pattern verbose-regression workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value([workload.haystack_payload()]),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_pattern_verbose_regression_workload(workload: Any) -> bool:
    return (
        workload.workload_id in _PATTERN_VERBOSE_REGRESSION_WORKLOAD_IDS
        and workload.operation in {"pattern.search", "pattern.fullmatch"}
        and workload.pattern == _PATTERN_VERBOSE_REGRESSION_PATTERN
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
        and workload.text_model in {"str", "bytes"}
        and workload.flags == 72
        and workload.pos is None
        and workload.endpos is None
        and not workload.kwargs
    )


def _pattern_boundary_wrong_text_model_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch"}:
        return None
    case_args = list(case.args)
    if len(case_args) != 1:
        return None
    haystack = case_args[0]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, bytes):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, str):
        return None
    return (
        f"pattern.{case.helper}",
        case_pattern(case),
        freeze_signature_value(case_args),
        (),
        case.flags or 0,
        case_text_model,
    )


def _pattern_boundary_wrong_text_model_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_boundary_wrong_text_model_workload(workload):
        raise AssertionError(
            "unexpected pattern-boundary wrong-text-model workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value([workload.haystack_payload()]),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_pattern_boundary_wrong_text_model_workload(workload: Any) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is not None
        and not workload.use_compiled_pattern
        and workload.operation in _PATTERN_BOUNDARY_OPERATIONS
        and workload.pos is None
        and workload.endpos is None
        and not workload.kwargs
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )
