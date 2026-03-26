from __future__ import annotations

import ast
import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import cache
from functools import partial
import importlib
import pathlib
import re
from types import SimpleNamespace
from typing import Any

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    BenchmarkManifest,
    Workload,
    determine_phase,
    determine_runner_version,
    published_benchmark_manifests,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks import benchmark_test_support
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    case_pattern,
    case_replacement_argument,
    case_text_argument,
    callable_match_group_signature,
    module_workflow_keyword_kwargs_signature,
    module_workflow_positional_args_signature,
)

_OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID = (
    "module-search-numbered-optional-group-conditional-cold-gap"
)


@dataclass(frozen=True, slots=True)
class _SourceTreeContractBuilderSpec:
    manifest_id: str
    excluded_fields: frozenset[str]
    manifest_timed_samples: int = 2
    timing_scope: str | None = None
    notes: tuple[str, ...] = ()


def _source_tree_contract_workload(
    source_workload: Workload,
    *,
    spec: _SourceTreeContractBuilderSpec,
) -> Workload:
    manifest_payload = _source_tree_contract_manifest((source_workload,), spec=spec)[
        "workloads"
    ][0]
    return workload_from_payload(
        {
            "manifest_id": spec.manifest_id,
            "workload_id": str(manifest_payload["id"]),
            **{key: value for key, value in manifest_payload.items() if key != "id"},
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


def _source_tree_contract_manifest(
    source_workloads: tuple[Workload, ...],
    *,
    spec: _SourceTreeContractBuilderSpec,
) -> dict[str, object]:
    workloads: list[dict[str, object]] = []
    for source_workload in source_workloads:
        payload = workload_to_payload(source_workload)
        manifest_payload: dict[str, object] = {
            "id": f"{source_workload.workload_id}-contract",
            **{
                key: value
                for key, value in payload.items()
                if key not in spec.excluded_fields
            },
        }
        if spec.timing_scope is not None:
            manifest_payload["timing_scope"] = spec.timing_scope
        if spec.notes:
            manifest_payload["notes"] = list(spec.notes)
        workloads.append(manifest_payload)
    return {
        "schema_version": 1,
        "manifest_id": spec.manifest_id,
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": spec.manifest_timed_samples,
        },
        "workloads": workloads,
    }


@cache
def _source_tree_combined_suite() -> object:
    return importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )


_PATTERN_BOUNDARY_OPERATIONS = frozenset(
    {"pattern.search", "pattern.match", "pattern.fullmatch"}
)

PATTERN_BOUNDARY_MANIFEST_PATH = BENCHMARK_WORKLOADS_ROOT / "pattern_boundary.py"

_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS = frozenset(
    {
        "manifest_id",
        "workload_id",
        "warmup_iterations",
        "sample_iterations",
        "timed_samples",
        "smoke",
    }
)

_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC = _SourceTreeContractBuilderSpec(
    manifest_id="pattern-boundary",
    excluded_fields=_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS,
    timing_scope="pattern-helper-call",
)

_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS = (
    "pattern-search-on-bytes-string-warm-str",
    "pattern-match-on-str-string-purged-bytes",
    "pattern-fullmatch-on-bytes-string-warm-str",
)


def _pattern_boundary_wrong_text_model_source_workloads() -> tuple[Any, ...]:
    return benchmark_test_support._contract_source_workloads(
        manifest_path=PATTERN_BOUNDARY_MANIFEST_PATH,
        include_workload_selectors=(_is_pattern_boundary_wrong_text_model_workload,),
        expected_source_workload_ids=_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS,
        drift_message=(
            "direct Pattern pattern-boundary wrong-text-model surface drifted "
            "from the live source workload surface"
        ),
    )


def _pattern_boundary_wrong_text_model_expected_callback_call(
    source_workload: Any,
) -> tuple[object, ...]:
    if source_workload.operation in _PATTERN_BOUNDARY_OPERATIONS:
        return (
            source_workload.operation,
            source_workload.haystack_payload(),
            (),
            {},
        )
    raise AssertionError(
        "unexpected direct Pattern pattern-boundary wrong-text-model "
        f"workload operation {source_workload.operation!r}"
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
        benchmark_test_support.case_pattern(case),
        benchmark_test_support.freeze_signature_value(case_args),
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
        benchmark_test_support.freeze_signature_value([workload.haystack_payload()]),
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


def _pattern_window_positional_indexlike_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch", "findall", "finditer"}:
        return None
    if not any(hasattr(argument, "__index__") for argument in case.args):
        return None
    return (
        case.helper,
        benchmark_test_support.case_pattern(case),
        benchmark_test_support.module_workflow_positional_args_signature(case.args),
        case.text_model or "str",
    )


def _pattern_window_positional_indexlike_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation not in {
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
        "pattern.findall",
        "pattern.finditer",
    }:
        raise AssertionError(
            "unexpected pattern positional-indexlike workload operation "
            f"{workload.operation!r}"
        )

    args: list[object] = [workload.haystack_payload()]
    if workload.pos is not None or workload.endpos is not None:
        args.append(0 if workload.pos is None else workload.pos)
    if workload.endpos is not None:
        args.append(workload.endpos)
    return tuple(args)


def _pattern_window_positional_indexlike_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_window_positional_indexlike_workload(workload):
        raise AssertionError(
            "unexpected pattern positional-indexlike workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation.removeprefix("pattern."),
        workload.pattern_payload(),
        benchmark_test_support.module_workflow_positional_args_signature(
            _pattern_window_positional_indexlike_workload_args(workload)
        ),
        workload.text_model,
    )


def _is_pattern_window_positional_indexlike_workload(workload: Any) -> bool:
    categories = set(workload.categories)
    return (
        workload.operation in {
            "pattern.search",
            "pattern.match",
            "pattern.fullmatch",
            "pattern.findall",
            "pattern.finditer",
        }
        and workload.expected_exception is None
        and not workload.kwargs
        and {"positional-window", "indexlike"}.issubset(categories)
        and (
            benchmark_test_support._is_encoded_indexlike_payload(workload.pos)
            or benchmark_test_support._is_encoded_indexlike_payload(workload.endpos)
        )
    )


def _pattern_keyword_window_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or not case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch", "findall", "finditer"}:
        return None
    return (
        f"pattern.{case.helper}",
        benchmark_test_support.case_pattern(case),
        benchmark_test_support.freeze_signature_value(list(case.args)),
        benchmark_test_support.module_workflow_keyword_kwargs_signature(case.kwargs),
        case.flags or 0,
        case.text_model or "str",
    )


def _pattern_keyword_window_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_keyword_window_workload(workload):
        raise AssertionError(
            "unexpected pattern keyword-window workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value([workload.haystack_payload()]),
        benchmark_test_support.module_workflow_keyword_kwargs_signature(
            workload.kwargs
        ),
        workload.flags,
        workload.text_model,
    )


def _is_pattern_keyword_window_workload(workload: Any) -> bool:
    categories = set(workload.categories)
    return (
        workload.operation in {
            "pattern.search",
            "pattern.match",
            "pattern.fullmatch",
            "pattern.findall",
            "pattern.finditer",
        }
        and workload.expected_exception is None
        and workload.pos is None
        and workload.endpos is None
        and bool(workload.kwargs)
        and set(workload.kwargs).issubset({"pos", "endpos"})
        and "keyword" in categories
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
        benchmark_test_support.case_pattern(case),
        benchmark_test_support.freeze_signature_value(case.serialized_args()),
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
        benchmark_test_support.freeze_signature_value(
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
        benchmark_test_support.case_pattern(case),
        benchmark_test_support.freeze_signature_value(list(case.args)),
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
        benchmark_test_support.freeze_signature_value([workload.haystack_payload()]),
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


PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS = (
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="pattern-window-positional-indexlike",
        manifest_paths=(PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-pos-indexlike-positional-warm-str": (
                    "workflow-pattern-search-str-pos-indexlike-positional",
                ),
                "pattern-search-endpos-indexlike-positional-purged-bytes": (
                    "workflow-pattern-search-bytes-endpos-indexlike-positional",
                ),
                "pattern-match-window-indexlike-positional-purged-bytes": (
                    "workflow-pattern-match-bytes-window-indexlike-positional",
                ),
                "pattern-fullmatch-window-indexlike-positional-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-window-indexlike-positional",
                ),
                "pattern-findall-window-indexlike-positional-warm-str": (
                    "workflow-pattern-findall-str-window-indexlike-positional",
                ),
                "pattern-finditer-window-indexlike-positional-purged-bytes": (
                    "workflow-pattern-finditer-bytes-window-indexlike-positional",
                ),
            },
        ),
        include_workload=_is_pattern_window_positional_indexlike_workload,
        correctness_case_signature=(
            _pattern_window_positional_indexlike_correctness_case_signature
        ),
        workload_signature=_pattern_window_positional_indexlike_workload_signature,
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="pattern-window-keyword",
        manifest_paths=(PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-pos-keyword-warm-str": (
                    "workflow-pattern-search-str-pos-keyword",
                ),
                "pattern-search-bool-endpos-keyword-warm-str": (
                    "workflow-pattern-search-str-bool-endpos-keyword",
                ),
                "pattern-search-endpos-keyword-purged-bytes": (
                    "workflow-pattern-search-bytes-endpos-keyword",
                ),
                "pattern-search-pos-indexlike-keyword-warm-str": (
                    "workflow-pattern-search-str-pos-indexlike",
                ),
                "pattern-search-endpos-indexlike-keyword-purged-bytes": (
                    "workflow-pattern-search-bytes-endpos-indexlike",
                ),
                "pattern-match-pos-keyword-purged-str": (
                    "workflow-pattern-match-str-pos-keyword",
                ),
                "pattern-match-bool-pos-keyword-purged-str": (
                    "workflow-pattern-match-str-bool-pos-keyword",
                ),
                "pattern-match-window-indexlike-purged-bytes": (
                    "workflow-pattern-match-bytes-window-indexlike",
                ),
                "pattern-fullmatch-window-keyword-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-window-keyword",
                ),
                "pattern-fullmatch-window-indexlike-keyword-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-window-indexlike",
                ),
                "pattern-findall-window-keyword-warm-str": (
                    "workflow-pattern-findall-str-window-keyword",
                ),
                "pattern-findall-window-indexlike-keyword-warm-str": (
                    "workflow-pattern-findall-str-window-indexlike",
                ),
                "pattern-findall-bool-window-keyword-warm-str": (
                    "workflow-pattern-findall-str-bool-window-keyword",
                ),
                "pattern-finditer-window-keyword-purged-bytes": (
                    "workflow-pattern-finditer-bytes-window-keyword",
                ),
                "pattern-finditer-window-indexlike-purged-bytes": (
                    "workflow-pattern-finditer-bytes-window-indexlike",
                ),
                "pattern-finditer-bool-window-keyword-purged-bytes": (
                    "workflow-pattern-finditer-bytes-bool-window-keyword",
                ),
            },
        ),
        include_workload=_is_pattern_keyword_window_workload,
        correctness_case_signature=_pattern_keyword_window_correctness_case_signature,
        workload_signature=_pattern_keyword_window_workload_signature,
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="pattern-boundary-bounded-wildcard",
        manifest_paths=(PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-bounded-wildcard-ignorecase-warm-str": (
                    "workflow-pattern-search-str-bounded-wildcard-ignorecase",
                ),
                "pattern-match-bounded-wildcard-warm-str": (
                    "workflow-pattern-match-str-bounded-wildcard",
                ),
                "pattern-fullmatch-bounded-wildcard-purged-str": (
                    "workflow-pattern-fullmatch-str-bounded-wildcard",
                ),
                "pattern-findall-bounded-wildcard-warm-str": (
                    "workflow-pattern-findall-str-bounded-wildcard",
                ),
                "pattern-finditer-bounded-wildcard-purged-str": (
                    "workflow-pattern-finditer-str-bounded-wildcard",
                ),
                "pattern-search-bounded-wildcard-endpos-miss-purged-str": (
                    "workflow-pattern-search-str-bounded-wildcard-endpos-miss",
                ),
            },
        ),
        include_workload=_is_pattern_bounded_wildcard_workload,
        correctness_case_signature=_pattern_bounded_wildcard_correctness_case_signature,
        workload_signature=_pattern_bounded_wildcard_workload_signature,
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="pattern-boundary-verbose-regression",
        manifest_paths=(PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-verbose-regression-warm-str": (
                    "workflow-pattern-search-str-verbose-regression",
                ),
                "pattern-search-verbose-regression-digits-warm-str": (
                    "workflow-pattern-search-str-verbose-regression-digits",
                ),
                "pattern-search-verbose-regression-too-many-digits-purged-str": (
                    "workflow-pattern-search-str-verbose-regression-too-many-digits",
                ),
                "pattern-search-verbose-regression-warm-bytes": (
                    "workflow-pattern-search-bytes-verbose-regression",
                ),
                "pattern-search-verbose-regression-digits-warm-bytes": (
                    "workflow-pattern-search-bytes-verbose-regression-digits",
                ),
                "pattern-search-verbose-regression-too-many-digits-purged-bytes": (
                    "workflow-pattern-search-bytes-verbose-regression-too-many-digits",
                ),
                "pattern-fullmatch-verbose-regression-warm-str": (
                    "workflow-pattern-fullmatch-str-verbose-regression",
                ),
                "pattern-fullmatch-verbose-regression-alpha-warm-str": (
                    "workflow-pattern-fullmatch-str-verbose-regression-alpha",
                ),
                "pattern-fullmatch-verbose-regression-lowercase-key-purged-str": (
                    "workflow-pattern-fullmatch-str-verbose-regression-lowercase-key",
                ),
                "pattern-fullmatch-verbose-regression-warm-bytes": (
                    "workflow-pattern-fullmatch-bytes-verbose-regression",
                ),
                "pattern-fullmatch-verbose-regression-alpha-warm-bytes": (
                    "workflow-pattern-fullmatch-bytes-verbose-regression-alpha",
                ),
                "pattern-fullmatch-verbose-regression-lowercase-key-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key",
                ),
            },
        ),
        include_workload=_is_pattern_verbose_regression_workload,
        correctness_case_signature=(
            _pattern_verbose_regression_correctness_case_signature
        ),
        workload_signature=_pattern_verbose_regression_workload_signature,
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="pattern-boundary-wrong-text-model",
        manifest_paths=(PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-on-bytes-string-warm-str": (
                    "workflow-pattern-search-str-pattern-on-bytes-string",
                ),
                "pattern-match-on-str-string-purged-bytes": (
                    "workflow-pattern-match-bytes-pattern-on-str-string",
                ),
                "pattern-fullmatch-on-bytes-string-warm-str": (
                    "workflow-pattern-fullmatch-str-pattern-on-bytes-string",
                ),
            },
        ),
        include_workload=_is_pattern_boundary_wrong_text_model_workload,
        correctness_case_signature=(
            _pattern_boundary_wrong_text_model_correctness_case_signature
        ),
        workload_signature=_pattern_boundary_wrong_text_model_workload_signature,
    ),
)


def _assert_source_tree_combined_routes_owner_names_through_module_alias(
    *,
    alias_name: str,
    owner_module: object,
    owner_names: tuple[str, ...],
    expected_direct_benchmark_test_support_refs: frozenset[str] = frozenset(),
) -> object:
    combined_suite = _source_tree_combined_suite()
    combined_suite_ast = benchmark_test_support._parsed_module_ast(combined_suite)
    _, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            combined_suite
        )
    )
    owner_module_name = owner_module.__name__
    owner_import_name = owner_module_name.rsplit(".", 1)[-1]
    benchmark_test_support_alias_names = benchmark_test_support._module_alias_names(
        combined_suite_ast,
        import_from_module="tests.benchmarks",
        import_name="benchmark_test_support",
        dotted_import_name="tests.benchmarks.benchmark_test_support",
    )
    owner_alias_names = benchmark_test_support._module_alias_names(
        combined_suite_ast,
        import_from_module="tests.benchmarks",
        import_name=owner_import_name,
        dotted_import_name=owner_module_name,
    )

    assert alias_name in owner_alias_names
    assert getattr(combined_suite, alias_name) is owner_module

    direct_import_names = {
        alias.name
        for node in ast.walk(combined_suite_ast)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    local_alias_names: set[str] = set()
    for node in combined_suite_ast.body:
        if isinstance(node, ast.Assign):
            targets = tuple(
                target.id for target in node.targets if isinstance(target, ast.Name)
            )
            value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = (node.target.id,)
            value = node.value
        else:
            continue

        if isinstance(value, ast.Name) and value.id in owner_names:
            local_alias_names.update(targets)
            continue

        if (
            isinstance(value, ast.Attribute)
            and isinstance(value.value, ast.Name)
            and value.value.id
            in (owner_alias_names | benchmark_test_support_alias_names)
            and value.attr in owner_names
        ):
            local_alias_names.update(targets)

    local_name_loads = {
        node.id
        for node in ast.walk(combined_suite_ast)
        if isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
        and node.id in owner_names
    }
    direct_benchmark_test_support_refs = {
        node.attr
        for node in ast.walk(combined_suite_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in benchmark_test_support_alias_names
        and node.attr in owner_names
    }
    aliased_owner_refs = {
        node.attr
        for node in ast.walk(combined_suite_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in (owner_alias_names - {alias_name})
        and node.attr in owner_names
    }
    owner_alias = getattr(combined_suite, alias_name)
    for name in owner_names:
        assert getattr(owner_alias, name) is getattr(owner_module, name)
        assert name not in direct_import_names
        assert name not in local_assignment_names
        assert name not in local_name_loads
    assert local_alias_names == set()
    assert (
        direct_benchmark_test_support_refs
        == expected_direct_benchmark_test_support_refs
    )
    assert aliased_owner_refs == set()
    return combined_suite


def assert_source_tree_benchmark_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    summary: dict[str, Any],
    *,
    expected_phase: str,
    expected_runner_version: str,
    expected_adapter: str,
    expected_manifests: list[BenchmarkManifest],
    expected_manifest_paths: list[str],
    expected_selection_mode: str,
    tracked_report_path: pathlib.Path | None = None,
) -> None:
    expected_manifest_records = [
        benchmark_test_support._artifact_manifest_record(manifest_path, manifest)
        for manifest_path, manifest in zip(
            expected_manifest_paths,
            expected_manifests,
            strict=True,
        )
    ]

    benchmark_test_support._assert_benchmark_summary_consistent(
        testcase,
        scorecard,
        summary,
    )
    testcase.assertEqual(scorecard["schema_version"], "1.0")
    testcase.assertEqual(scorecard["suite"], "benchmarks")
    testcase.assertEqual(scorecard["phase"], expected_phase)
    expected_baseline = {
        **benchmark_test_support.build_cpython_baseline(version_family="3.12.x"),
        "re_module": "re",
    }
    for key, expected_value in expected_baseline.items():
        testcase.assertEqual(scorecard["baseline"][key], expected_value)
    testcase.assertEqual(scorecard["implementation"]["module_name"], "rebar")
    testcase.assertEqual(scorecard["implementation"]["adapter"], expected_adapter)
    testcase.assertEqual(
        scorecard["implementation"]["adapter_mode_requested"],
        "source-tree-shim",
    )
    testcase.assertEqual(
        scorecard["implementation"]["adapter_mode_resolved"],
        "source-tree-shim",
    )
    testcase.assertEqual(scorecard["implementation"]["build_mode"], "source-tree-shim")
    testcase.assertEqual(scorecard["implementation"]["timing_path"], "source-tree-shim")
    testcase.assertIsNone(scorecard["implementation"]["native_build_tool"])
    testcase.assertIsNone(scorecard["implementation"]["native_wheel"])
    testcase.assertIsInstance(scorecard["implementation"]["native_module_loaded"], bool)
    testcase.assertEqual(scorecard["implementation"]["native_module_name"], "rebar._rebar")
    if scorecard["implementation"]["native_module_loaded"]:
        testcase.assertEqual(
            scorecard["implementation"]["native_scaffold_status"],
            "scaffold-only",
        )
        testcase.assertEqual(
            scorecard["implementation"]["native_target_cpython_series"],
            "3.12.x",
        )
    else:
        testcase.assertIsNone(scorecard["implementation"]["native_scaffold_status"])
        testcase.assertIsNone(
            scorecard["implementation"]["native_target_cpython_series"]
        )
    testcase.assertIn(
        "not requested",
        scorecard["implementation"]["native_unavailable_reason"],
    )
    testcase.assertEqual(
        scorecard["environment"]["runner_version"],
        expected_runner_version,
    )
    testcase.assertEqual(
        scorecard["environment"]["execution_model"],
        "single-process in-process adapter comparison",
    )
    testcase.assertEqual(
        scorecard["artifacts"]["selection_mode"],
        expected_selection_mode,
    )
    testcase.assertIsNone(scorecard["artifacts"]["raw_samples"])
    testcase.assertEqual(scorecard["artifacts"]["manifests"], expected_manifest_records)
    if len(expected_manifest_records) == 1:
        testcase.assertEqual(
            scorecard["artifacts"]["manifest"],
            expected_manifest_records[0]["manifest"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["manifest_id"],
            expected_manifest_records[0]["manifest_id"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["manifest_schema_version"],
            expected_manifest_records[0]["manifest_schema_version"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["workload_count"],
            expected_manifest_records[0]["workload_count"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["smoke_workload_ids"],
            expected_manifest_records[0]["smoke_workload_ids"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["spec_refs"],
            expected_manifest_records[0]["spec_refs"],
        )
    else:
        testcase.assertEqual(scorecard["artifacts"]["manifest"], None)
        testcase.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        testcase.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
    if tracked_report_path is not None:
        testcase.assertTrue(tracked_report_path.is_file())


_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS = {
    "collection-replacement-boundary": _SourceTreeContractBuilderSpec(
        manifest_id="collection-replacement-boundary",
        excluded_fields=(
            benchmark_test_support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
        ),
        timing_scope="module-helper-call",
        notes=(
            "Ensures benchmark manifests keep the bounded "
            "compiled-pattern-first-argument wrong-text-model "
            "collection/replacement rows unresolved until helper invocation.",
        ),
    ),
    "module-boundary": _SourceTreeContractBuilderSpec(
        manifest_id="module-boundary",
        excluded_fields=(
            benchmark_test_support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
        ),
        timing_scope="module-helper-call",
        notes=(
            "Ensures benchmark manifests keep the bounded "
            "compiled-pattern-first-argument wrong-text-model "
            "module-boundary rows unresolved until helper invocation.",
        ),
    ),
}

_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS = (
    "module-split-on-bytes-string-purged-str-compiled-pattern",
    "module-findall-on-str-string-purged-bytes-compiled-pattern",
    "module-finditer-on-bytes-string-warm-str-compiled-pattern",
    "module-sub-on-bytes-string-warm-str-compiled-pattern",
    "module-subn-on-str-string-purged-bytes-compiled-pattern",
)
_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS = (
    "module-search-on-bytes-string-warm-str-compiled-pattern",
    "module-match-on-str-string-purged-bytes-compiled-pattern",
    "module-fullmatch-on-bytes-string-warm-str-compiled-pattern",
)
_COMPILED_PATTERN_MODULE_HELPER_OPERATIONS = frozenset(
    {"module.search", "module.match", "module.fullmatch"}
)
_VERBOSE_REGRESSION_PATTERN = (
    r"^ (?P<key>[A-Z_]+) \s* = \s* (?:[A-Z]{2,4}+|\d{2,3}) $"
)
_VERBOSE_REGRESSION_FLAGS = int(re.VERBOSE | re.MULTILINE)


def _compiled_pattern_module_helper_route(
    workload: Workload,
    *,
    collection_replacement_callback_flags: int,
) -> tuple[object, tuple[object, ...], tuple[object, ...], bool]:
    if workload.operation in _COMPILED_PATTERN_MODULE_HELPER_OPERATIONS:
        return (
            "module-result",
            (workload.operation, workload.haystack_payload(), 0, {}),
            (workload.haystack_payload(), workload.flags),
            False,
        )
    if workload.operation == "module.split":
        return (
            "module-result",
            (
                workload.operation,
                workload.haystack_payload(),
                workload.maxsplit_argument(),
                collection_replacement_callback_flags,
                {},
            ),
            (workload.haystack_payload(), workload.maxsplit_argument()),
            False,
        )
    if workload.operation == "module.findall":
        return (
            "module-result",
            (
                workload.operation,
                workload.haystack_payload(),
                collection_replacement_callback_flags,
            ),
            (workload.haystack_payload(), workload.flags),
            False,
        )
    if workload.operation == "module.finditer":
        return (
            ["module-finditer-result"],
            (
                workload.operation,
                workload.haystack_payload(),
                collection_replacement_callback_flags,
            ),
            (workload.haystack_payload(), workload.flags),
            True,
        )
    if workload.operation == "module.sub":
        return (
            "module-result",
            (
                workload.operation,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
                collection_replacement_callback_flags,
                {},
            ),
            (
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
            ),
            False,
        )
    if workload.operation == "module.subn":
        return (
            ("module-result", 0),
            (
                workload.operation,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
                collection_replacement_callback_flags,
                {},
            ),
            (
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
            ),
            False,
        )
    raise AssertionError(
        "unexpected compiled-pattern module helper workload operation "
        f"{workload.operation!r}"
    )


def _module_workflow_compiled_pattern_success_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"search", "match", "fullmatch"}:
        return None
    if not case.args:
        return None
    case_text_model = case.text_model or "str"
    return (
        f"module.{case.helper}",
        case_pattern(case),
        benchmark_test_support.freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_workload_args(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern workload "
            f"{workload.workload_id!r}"
        )
    return (workload.haystack_payload(),)


def _module_workflow_compiled_pattern_success_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(
            list(_module_workflow_compiled_pattern_workload_args(workload))
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_compiled_pattern_workload(workload: Any) -> bool:
    return (
        not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation in _COMPILED_PATTERN_MODULE_HELPER_OPERATIONS
    )


def _is_module_workflow_compiled_pattern_literal_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is None
        and workload.expected_exception is None
        and workload.pattern == "abc"
    )


def _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is None
        and workload.expected_exception is None
        and workload.pattern == "a.c"
        and workload.text_model in {"str", "bytes"}
    )


def _is_module_workflow_compiled_pattern_verbose_bytes_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is None
        and workload.expected_exception is None
        and workload.pattern == _VERBOSE_REGRESSION_PATTERN
        and workload.flags == _VERBOSE_REGRESSION_FLAGS
        and workload.text_model == "bytes"
    )


def _is_collection_replacement_compiled_pattern_success_workload(
    workload: Any,
) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is None
        and not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation
        in {
            "module.split",
            "module.findall",
            "module.finditer",
            "module.sub",
            "module.subn",
        }
        and workload.expected_exception is None
        and workload.pattern == "abc"
    )


COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS = (
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-literal-success",
        manifest_paths=(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-literal-warm-hit-str-compiled-pattern": (
                    "workflow-module-search-str-compiled-pattern",
                ),
                "module-match-literal-warm-hit-str-compiled-pattern": (
                    "workflow-module-match-str-compiled-pattern",
                ),
                "module-fullmatch-literal-purged-hit-bytes-compiled-pattern": (
                    "workflow-module-fullmatch-bytes-compiled-pattern",
                ),
            },
        ),
        include_workload=_is_module_workflow_compiled_pattern_literal_success_workload,
        correctness_case_signature=(
            _module_workflow_compiled_pattern_success_correctness_case_signature
        ),
        workload_signature=_module_workflow_compiled_pattern_success_workload_signature,
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-bounded-wildcard-success",
        manifest_paths=(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern": (
                    "workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern",
                ),
                "module-match-bounded-wildcard-warm-hit-str-compiled-pattern": (
                    "workflow-module-match-str-bounded-wildcard-compiled-pattern",
                ),
                "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern": (
                    "workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern",
                ),
            },
        ),
        include_workload=(
            _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload
        ),
        correctness_case_signature=(
            _module_workflow_compiled_pattern_success_correctness_case_signature
        ),
        workload_signature=_module_workflow_compiled_pattern_success_workload_signature,
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-verbose-bytes-success",
        manifest_paths=(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-verbose-regression-warm-hit-bytes-compiled-pattern": (
                    "workflow-module-search-bytes-verbose-regression-compiled-pattern",
                ),
                "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern": (
                    "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
                ),
            },
        ),
        include_workload=_is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
        correctness_case_signature=(
            _module_workflow_compiled_pattern_success_correctness_case_signature
        ),
        workload_signature=_module_workflow_compiled_pattern_success_workload_signature,
        run_callback_result_parity=True,
    ),
)

def _is_module_workflow_compiled_pattern_wrong_text_model_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is not None
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )


def _is_collection_replacement_wrong_text_model_workload(workload: Any) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is not None
        and not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation
        in {
            "module.split",
            "module.findall",
            "module.finditer",
            "module.sub",
            "module.subn",
        }
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )


def _compiled_pattern_wrong_text_model_specs() -> tuple[dict[str, object], ...]:
    return (
        {
            "case_id": "compiled_pattern_module_helper_wrong_text_model",
            "manifest_path": "collection_replacement_boundary.py",
            "include_workload": _is_collection_replacement_wrong_text_model_workload,
            "contract_manifest_id": "collection-replacement-boundary",
            "contract_filename": (
                "python_benchmark_compiled_pattern_collection_replacement_wrong_text_model_contract.py"
            ),
            "expected_source_workload_ids": (
                _COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
            ),
        },
        {
            "case_id": "compiled_pattern_module_boundary_wrong_text_model",
            "manifest_path": "module_boundary.py",
            "include_workload": (
                _is_module_workflow_compiled_pattern_wrong_text_model_workload
            ),
            "contract_manifest_id": "module-boundary",
            "contract_filename": (
                "python_benchmark_compiled_pattern_module_boundary_wrong_text_model_contract.py"
            ),
            "expected_source_workload_ids": (
                _COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
            ),
        },
    )


def _compiled_pattern_wrong_text_model_source_workloads(
    spec: dict[str, object],
) -> tuple[Workload, ...]:
    return benchmark_test_support.selected_manifest_workloads(
        spec["manifest_path"],
        include_workload=spec["include_workload"],
    )


def _run_cpython_compiled_pattern_module_helper_workload(
    workload: Workload,
    *,
    collection_replacement_callback_flags: int,
) -> object:
    compiled_pattern = re.compile(
        workload.pattern_payload(),
        workload.flags,
    )
    _, _, cpython_call_args, materialize_cpython_result = (
        _compiled_pattern_module_helper_route(
            workload,
            collection_replacement_callback_flags=collection_replacement_callback_flags,
        )
    )
    helper = getattr(re, workload.operation.removeprefix("module."))
    result = helper(compiled_pattern, *cpython_call_args)
    if materialize_cpython_result:
        return list(result)
    return result


def _module_workflow_compiled_pattern_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"search", "match", "fullmatch"}:
        return None
    if not case.args:
        return None
    case_text_model = case.text_model or "str"
    return (
        f"module.{case.helper}",
        case_pattern(case),
        benchmark_test_support.freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(
            [workload.haystack_payload()]
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _assert_wrong_text_model_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes
    expected_haystack_type = (
        str if source_workload.haystack_text_model == "str" else bytes
    )

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["timing_scope"] == "module-helper-call"
    assert round_tripped.timing_scope == "module-helper-call"
    assert payload["haystack_text_model"] == source_workload.haystack_text_model
    assert round_tripped.haystack_text_model == source_workload.haystack_text_model
    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_haystack_type)
    if source_workload.replacement is not None:
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


@dataclass(frozen=True, slots=True)
class CompiledPatternModuleSuccessOwnerSpec:
    case_id: str
    manifest_path: Any
    include_workload_selectors: tuple[Callable[[Any], bool], ...]
    contract_manifest_id: str
    contract_filename: str
    note_surface: str
    expected_source_workload_ids: tuple[str, ...]
    preserved_payload_fields: tuple[str, ...]
    preserve_replacement_payload_typing: bool

    def source_workloads(self) -> tuple[Workload, ...]:
        return benchmark_test_support._contract_source_workloads(
            manifest_path=self.manifest_path,
            include_workload_selectors=self.include_workload_selectors,
            expected_source_workload_ids=self.expected_source_workload_ids,
            drift_message=(
                "compiled-pattern module contract source workloads drifted from the "
                f"{self.case_id} owner-spec surface"
            ),
        )

    def expected_build_calls(
        self,
        source_workload: Workload,
    ) -> list[tuple[object, ...]]:
        return benchmark_test_support.compiled_pattern_contract_expected_build_calls(
            source_workload,
            label=f"{self.case_id} success",
        )

    def expected_callback_result(self, source_workload: Workload) -> object:
        callback_result, _, _, _ = _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=source_workload.flags,
        )
        return callback_result

    def expected_callback_call(
        self,
        source_workload: Workload,
    ) -> tuple[object, ...]:
        _, callback_call, _, _ = _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=source_workload.flags,
        )
        return callback_call

    def contract_builder_spec(self) -> _SourceTreeContractBuilderSpec:
        return _SourceTreeContractBuilderSpec(
            manifest_id=self.contract_manifest_id,
            excluded_fields=(
                benchmark_test_support.COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS
            ),
            timing_scope="module-helper-call",
            notes=(
                "Ensures benchmark manifests keep the bounded "
                "compiled-pattern-first-argument successful "
                f"{self.note_surface} rows unresolved until helper invocation.",
            ),
        )


def _assert_compiled_pattern_module_success_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
    *,
    owner_spec: CompiledPatternModuleSuccessOwnerSpec,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload.get("expected_exception") is None
    assert round_tripped.expected_exception is None
    assert payload.get("haystack_text_model") is None
    assert round_tripped.haystack_text_model is None
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_text_type)
    for field_name in owner_spec.preserved_payload_fields:
        assert payload[field_name] == getattr(source_workload, field_name)
        assert getattr(round_tripped, field_name) == getattr(
            source_workload,
            field_name,
        )
    if (
        owner_spec.preserve_replacement_payload_typing
        and source_workload.replacement is not None
    ):
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


def _assert_compiled_pattern_success_rows_measured_in_combined_manifest(
    owner_spec: CompiledPatternModuleSuccessOwnerSpec,
    *,
    include_workload: Callable[[Any], bool],
) -> None:
    testcase = benchmark_test_support.unittest.TestCase()
    manifest = benchmark_test_support.load_manifest(owner_spec.manifest_path)
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in owner_spec.source_workloads()
        if include_workload(workload)
    )
    selected_measured_workload_ids = benchmark_test_support.manifest_workload_ids_matching(
        manifest,
        include_workload,
    )

    assert selected_measured_workload_ids == expected_measured_workload_ids

    _, scorecard = benchmark_test_support.run_harness_scorecard(
        "rebar_harness.benchmarks",
        ["--manifest", str(owner_spec.manifest_path)],
        report_name="benchmarks.json",
    )
    manifest_summary = scorecard["manifests"][owner_spec.contract_manifest_id]
    expected_workload_count = len(manifest.workloads)

    assert manifest_summary["known_gap_count"] == 0
    assert manifest_summary["measured_workloads"] == expected_workload_count
    assert manifest_summary["workload_count"] == expected_workload_count

    for workload_id in expected_measured_workload_ids:
        benchmark_test_support.assert_benchmark_workload_contract(
            testcase,
            benchmark_test_support.find_workload_record(scorecard, workload_id),
            manifest_id=owner_spec.contract_manifest_id,
            workload_document=benchmark_test_support.find_workload_document(
                manifest,
                workload_id,
            ),
            expected_status="measured",
        )


def include_live_compiled_pattern_module_success_workload(workload: Workload) -> bool:
    return (
        workload.use_compiled_pattern
        and workload.expected_exception is None
        and getattr(workload, "haystack_text_model", None) is None
        and workload.operation.startswith("module.")
        and workload.operation != "module.compile"
        and not workload.kwargs
    )


_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC = (
    CompiledPatternModuleSuccessOwnerSpec(
        case_id="collection-replacement",
        manifest_path=benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload_selectors=(
            _is_collection_replacement_compiled_pattern_success_workload,
        ),
        contract_manifest_id="collection-replacement-boundary",
        contract_filename=(
            "python_benchmark_compiled_pattern_collection_replacement_success_contract.py"
        ),
        note_surface="collection/replacement",
        expected_source_workload_ids=(
            "module-split-literal-warm-str-compiled-pattern",
            "module-findall-literal-purged-bytes-compiled-pattern",
            "module-finditer-literal-warm-str-compiled-pattern",
            "module-sub-literal-warm-str-compiled-pattern",
            "module-subn-literal-purged-bytes-compiled-pattern",
        ),
        preserved_payload_fields=("count", "maxsplit"),
        preserve_replacement_payload_typing=True,
    )
)
_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC = (
    CompiledPatternModuleSuccessOwnerSpec(
        case_id="module-boundary",
        manifest_path=benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload_selectors=(
            _is_module_workflow_compiled_pattern_literal_success_workload,
            _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
            _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
        ),
        contract_manifest_id="module-boundary",
        contract_filename=(
            "python_benchmark_compiled_pattern_module_boundary_success_contract.py"
        ),
        note_surface="module-boundary",
        expected_source_workload_ids=(
            "module-search-literal-warm-hit-str-compiled-pattern",
            "module-match-literal-warm-hit-str-compiled-pattern",
            "module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
            "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern",
            "module-match-bounded-wildcard-warm-hit-str-compiled-pattern",
            "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern",
            "module-search-verbose-regression-warm-hit-bytes-compiled-pattern",
            "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern",
        ),
        preserved_payload_fields=("flags",),
        preserve_replacement_payload_typing=False,
    )
)
_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS = (
    _COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC,
    _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
)
_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS = tuple(
    pytest.param(
        owner_spec,
        source_workload,
        id=f"{owner_spec.case_id}-{source_workload.workload_id}",
    )
    for owner_spec in _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
    for source_workload in owner_spec.source_workloads()
)

_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE = (
    ("flags", "int", 0),
)
_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE = (
    ("flags", "bool", False),
)
_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE = (
    ("flags", "int", int(re.IGNORECASE)),
)
_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS = ("abc",)
_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS = (
    "(?P<word>abc)",
)
_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION = {
    "type": "ValueError",
    "message_substring": "cannot process flags argument with a compiled pattern",
}


def _compiled_pattern_module_compile_keyword_kwargs_signature(
    kwargs: dict[str, object],
) -> tuple[tuple[str, str, object], ...]:
    signature: list[tuple[str, str, object]] = []
    for name, value in sorted(kwargs.items()):
        if isinstance(value, bool):
            signature.append((name, "bool", value))
            continue
        if isinstance(value, re.RegexFlag) and int(value) == 0:
            signature.append((name, "noflag", 0))
            continue
        if isinstance(value, int):
            signature.append((name, "int", int(value)))
            continue
        signature.append((name, type(value).__name__, repr(value)))
    return tuple(signature)


def _module_workflow_compiled_pattern_compile_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper != "compile" or case.args:
        return None
    case_text_model = case.text_model or "str"
    return (
        "module.compile",
        case_pattern(case),
        (),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_compile_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_compile_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern module.compile workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        (),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_compiled_pattern_compile_workload(workload: Any) -> bool:
    return (
        not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation == "module.compile"
    )


def _is_module_workflow_compiled_pattern_compile_success_workload(
    workload: Any,
    *,
    allowed_patterns: tuple[str, ...],
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_compile_workload(workload)
        and workload.expected_exception is None
        and workload.pattern in allowed_patterns
        and workload.flags == 0
    )


def _workload_matches_expected_exception(
    workload: Any,
    *,
    expected_exception: dict[str, str] | None,
) -> bool:
    if expected_exception is None:
        return workload.expected_exception is None
    return workload.expected_exception == expected_exception


def _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
    case: Any,
    *,
    keyword_signature: tuple[tuple[str, str, object], ...],
    allowed_patterns: tuple[str, ...],
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or not case.use_compiled_pattern:
        return None
    if case.helper != "compile" or case.args:
        return None
    if (
        _compiled_pattern_module_compile_keyword_kwargs_signature(case.kwargs)
        != keyword_signature
    ):
        return None
    if case.pattern not in allowed_patterns:
        return None
    case_text_model = case.text_model or "str"
    return (
        "module.compile",
        case_pattern(case),
        (),
        keyword_signature,
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_compile_keyword_workload_signature(
    workload: Any,
    *,
    keyword_label: str,
    keyword_signature: tuple[tuple[str, str, object], ...],
    allowed_patterns: tuple[str, ...],
    expected_exception: dict[str, str] | None = None,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_compile_keyword_workload(
        workload,
        keyword_signature=keyword_signature,
        allowed_patterns=allowed_patterns,
        expected_exception=expected_exception,
    ):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern module.compile "
            f"{keyword_label} keyword workload {workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        (),
        keyword_signature,
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_compiled_pattern_compile_keyword_workload(
    workload: Any,
    *,
    keyword_signature: tuple[tuple[str, str, object], ...],
    allowed_patterns: tuple[str, ...],
    expected_exception: dict[str, str] | None = None,
) -> bool:
    return (
        workload.use_compiled_pattern
        and workload.operation == "module.compile"
        and _workload_matches_expected_exception(
            workload,
            expected_exception=expected_exception,
        )
        and workload.pattern in allowed_patterns
        and workload.flags == 0
        and _compiled_pattern_module_compile_keyword_kwargs_signature(workload.kwargs)
        == keyword_signature
    )


def _assert_compiled_pattern_module_compile_contract_payload_round_trip_common(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["flags"] == source_workload.flags
    assert round_tripped.flags == source_workload.flags
    assert payload.get("expected_exception") == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)


def _assert_compiled_pattern_module_compile_success_payload_round_trip(
    contract_case: Any,
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    del contract_case
    _assert_compiled_pattern_module_compile_contract_payload_round_trip_common(
        source_workload,
        payload,
        round_tripped,
    )
    assert payload.get("haystack_text_model") == source_workload.haystack_text_model
    assert round_tripped.haystack_text_model == source_workload.haystack_text_model


def _assert_compiled_pattern_module_compile_keyword_payload_round_trip(
    contract_case: Any,
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    del contract_case
    _assert_compiled_pattern_module_compile_contract_payload_round_trip_common(
        source_workload,
        payload,
        round_tripped,
    )
    expected_keyword_value = source_workload.keyword_arguments()["flags"]

    assert payload["kwargs"] == source_workload.kwargs
    assert round_tripped.kwargs == source_workload.kwargs
    assert type(payload["kwargs"]["flags"]) is type(expected_keyword_value)
    assert type(round_tripped.kwargs["flags"]) is type(expected_keyword_value)
    assert payload.get("haystack_text_model") is None
    assert round_tripped.haystack_text_model is None


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleCompileContractRoute:
    surface_label: str
    excluded_fields: frozenset[str]
    note: str
    correctness_case_signature_builder: Callable[
        [CompiledPatternModuleCompileContractCase, Any],
        tuple[Any, ...] | None,
    ]
    workload_signature_builder: Callable[
        [CompiledPatternModuleCompileContractCase, Any],
        tuple[Any, ...],
    ]
    include_workload_selector: Callable[
        [CompiledPatternModuleCompileContractCase, Any],
        bool,
    ]
    payload_round_trip_assertion: Callable[
        [CompiledPatternModuleCompileContractCase, Workload, dict[str, object], Workload],
        None,
    ]
    cpython_dispatch: Callable[
        [CompiledPatternModuleCompileContractCase, Workload],
        object,
    ]
    callback_flags_selector: Callable[
        [CompiledPatternModuleCompileContractCase, Workload],
        object,
    ]

    def drift_message(
        self,
        contract_case: CompiledPatternModuleCompileContractCase,
    ) -> str:
        return (
            f"compiled-pattern module.compile {self.surface_label} rows drifted from the "
            f"{contract_case.case_id} contract surface"
        )


@dataclass(frozen=True)
class CompiledPatternModuleCompileContractCase:
    route: _CompiledPatternModuleCompileContractRoute
    case_id: str
    manifest_path: pathlib.Path
    source_selectors: tuple[Callable[[Any], bool], ...]
    contract_filename: str
    anchor_contract_filename: str
    expected_anchor_pairs: tuple[tuple[str, str], ...]
    expected_build_calls_builder: Callable[[Workload], list[tuple[object, ...]]]
    keyword_signature: tuple[tuple[str, str, object], ...] | None = None
    allowed_patterns: tuple[str, ...] = ()
    expected_exception: dict[str, str] | None = None

    def required_keyword_signature(self) -> tuple[tuple[str, str, object], ...]:
        if self.keyword_signature is None:
            raise AssertionError(
                "missing compiled-pattern module.compile keyword signature for "
                f"{self.case_id!r}"
            )
        return self.keyword_signature

    def expected_source_workload_ids(self) -> tuple[str, ...]:
        return tuple(
            workload_id.removesuffix("-contract")
            for workload_id, _case_id in self.expected_anchor_pairs
        )

    def source_workloads(self) -> tuple[Workload, ...]:
        return benchmark_test_support._contract_source_workloads(
            manifest_path=self.manifest_path,
            include_workload_selectors=self.source_selectors,
            expected_source_workload_ids=self.expected_source_workload_ids(),
            drift_message=self.route.drift_message(self),
        )

    def manifest_excluded_fields(self) -> frozenset[str]:
        return self.route.excluded_fields

    def note(self) -> str:
        return self.route.note

    def correctness_case_signature(self, case: Any) -> tuple[Any, ...] | None:
        return self.route.correctness_case_signature_builder(self, case)

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        return self.route.workload_signature_builder(self, workload)

    def include_workload(self, workload: Any) -> bool:
        return self.route.include_workload_selector(self, workload)

    def assert_payload_round_trip(
        self,
        source_workload: Workload,
        payload: dict[str, object],
        round_tripped: Workload,
    ) -> None:
        self.route.payload_round_trip_assertion(
            self,
            source_workload,
            payload,
            round_tripped,
        )

    def run_cpython_workload(self, workload: Workload) -> object:
        return self.route.cpython_dispatch(self, workload)

    def callback_flags(self, source_workload: Workload) -> object:
        return self.route.callback_flags_selector(self, source_workload)

    def expected_anchor_case_ids(
        self,
        manifest_path: pathlib.Path,
    ) -> dict[tuple[str, str], tuple[str, ...]]:
        return benchmark_test_support._workload_case_pair_anchor_expectations(
            manifest_path,
            self.expected_anchor_pairs,
        )

    def expected_build_calls(
        self,
        source_workload: Workload,
    ) -> list[tuple[object, ...]]:
        return self.expected_build_calls_builder(source_workload)

    def contract_builder_spec(self) -> _SourceTreeContractBuilderSpec:
        return _SourceTreeContractBuilderSpec(
            manifest_id="module-boundary",
            excluded_fields=self.manifest_excluded_fields(),
            manifest_timed_samples=2,
            timing_scope="module-helper-call",
            notes=(self.note(),),
        )


_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_ROUTE = (
    _CompiledPatternModuleCompileContractRoute(
        surface_label="success",
        excluded_fields=(
            benchmark_test_support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
        ),
        note=(
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            "module.compile rows unresolved until helper invocation."
        ),
        correctness_case_signature_builder=(
            lambda _contract_case, case: _module_workflow_compiled_pattern_compile_correctness_case_signature(
                case
            )
        ),
        workload_signature_builder=(
            lambda _contract_case, workload: _module_workflow_compiled_pattern_compile_workload_signature(
                workload
            )
        ),
        include_workload_selector=(
            lambda _contract_case, workload: _is_module_workflow_compiled_pattern_compile_workload(
                workload
            )
        ),
        payload_round_trip_assertion=(
            _assert_compiled_pattern_module_compile_success_payload_round_trip
        ),
        cpython_dispatch=(
            lambda _contract_case, workload: re.compile(
                re.compile(workload.pattern_payload(), workload.flags),
                workload.flags,
            )
        ),
        callback_flags_selector=(lambda _contract_case, source_workload: source_workload.flags),
    )
)

_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CONTRACT_ROUTE = (
    _CompiledPatternModuleCompileContractRoute(
        surface_label="keyword",
        excluded_fields=(
            benchmark_test_support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
            | {"categories", "syntax_features"}
        ),
        note=(
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            "module.compile flags= keyword rows unresolved until helper invocation."
        ),
        correctness_case_signature_builder=(
            lambda contract_case, case: _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
                case,
                keyword_signature=contract_case.required_keyword_signature(),
                allowed_patterns=contract_case.allowed_patterns,
            )
        ),
        workload_signature_builder=(
            lambda contract_case, workload: _module_workflow_compiled_pattern_compile_keyword_workload_signature(
                workload,
                keyword_label=contract_case.case_id,
                keyword_signature=contract_case.required_keyword_signature(),
                allowed_patterns=contract_case.allowed_patterns,
                expected_exception=contract_case.expected_exception,
            )
        ),
        include_workload_selector=(
            lambda contract_case, workload: _is_module_workflow_compiled_pattern_compile_keyword_workload(
                workload,
                keyword_signature=contract_case.required_keyword_signature(),
                allowed_patterns=contract_case.allowed_patterns,
                expected_exception=contract_case.expected_exception,
            )
        ),
        payload_round_trip_assertion=(
            _assert_compiled_pattern_module_compile_keyword_payload_round_trip
        ),
        cpython_dispatch=(
            lambda _contract_case, workload: re.compile(
                re.compile(workload.pattern_payload(), workload.flags),
                **workload.keyword_arguments(),
            )
        ),
        callback_flags_selector=(
            lambda _contract_case, source_workload: source_workload.keyword_arguments()["flags"]
        ),
    )
)


@dataclass(frozen=True)
class _CompiledPatternModuleContractAnchorLane:
    case_id: str
    contract_filename: str
    source_workloads: tuple[Workload, ...]
    contract_builder_spec: Callable[[], Any]
    expected_anchor_case_ids: Callable[
        [pathlib.Path],
        dict[tuple[str, str], tuple[str, ...]],
    ]
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    include_workload: Callable[[Any], bool]
    expected_anchor_pairs: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleCompileKeywordOwnerSpec:
    case_id: str
    anchor_definition_name: str
    keyword_signature: tuple[tuple[str, str, object], ...]
    allowed_patterns: tuple[str, ...]
    anchor_expectations: tuple[tuple[str, tuple[str, ...]], ...]
    contract_filename: str
    anchor_contract_filename: str
    expected_anchor_pairs: tuple[tuple[str, str], ...]
    expected_exception: dict[str, str] | None = None

    def correctness_case_signature(self, case: Any) -> tuple[Any, ...] | None:
        return _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
            case,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
        )

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        return _module_workflow_compiled_pattern_compile_keyword_workload_signature(
            workload,
            keyword_label=self.case_id,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            expected_exception=self.expected_exception,
        )

    def includes_workload(self, workload: Any) -> bool:
        return _is_module_workflow_compiled_pattern_compile_keyword_workload(
            workload,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            expected_exception=self.expected_exception,
        )

    def expected_anchor_case_ids(self) -> dict[tuple[str, str], tuple[str, ...]]:
        return benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            dict(self.anchor_expectations),
        )

    def expected_anchor_workload_ids(self) -> tuple[str, ...]:
        return tuple(workload_id for workload_id, _ in self.anchor_expectations)

    def anchor_definition(
        self,
    ) -> benchmark_test_support.StandardBenchmarkAnchorContractDefinition:
        return benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name=self.anchor_definition_name,
            manifest_paths=(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=self.expected_anchor_case_ids(),
            include_workload=self.includes_workload,
            correctness_case_signature=self.correctness_case_signature,
            workload_signature=self.workload_signature,
            run_callback_result_parity=True,
        )

    def contract_case(self) -> CompiledPatternModuleCompileContractCase:
        return CompiledPatternModuleCompileContractCase(
            route=_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CONTRACT_ROUTE,
            case_id=self.case_id,
            manifest_path=benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            source_selectors=(self.includes_workload,),
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            contract_filename=self.contract_filename,
            anchor_contract_filename=self.anchor_contract_filename,
            expected_anchor_pairs=self.expected_anchor_pairs,
            expected_build_calls_builder=partial(
                benchmark_test_support.compiled_pattern_contract_expected_build_calls,
                label="module.compile contract",
            ),
            expected_exception=self.expected_exception,
        )


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleCompileSuccessOwnerSpec:
    anchor_definition_name: str
    allowed_patterns: tuple[str, ...]
    anchor_expectations: tuple[tuple[str, tuple[str, ...]], ...]
    expected_anchor_pairs: tuple[tuple[str, str], ...]

    def correctness_case_signature(self, case: Any) -> tuple[Any, ...] | None:
        return _module_workflow_compiled_pattern_compile_correctness_case_signature(case)

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        return _module_workflow_compiled_pattern_compile_workload_signature(workload)

    def includes_workload(self, workload: Any) -> bool:
        return _is_module_workflow_compiled_pattern_compile_success_workload(
            workload,
            allowed_patterns=self.allowed_patterns,
        )

    def expected_anchor_case_ids(self) -> dict[tuple[str, str], tuple[str, ...]]:
        return benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            dict(self.anchor_expectations),
        )

    def expected_anchor_workload_ids(self) -> tuple[str, ...]:
        return tuple(workload_id for workload_id, _ in self.anchor_expectations)

    def anchor_definition(
        self,
    ) -> benchmark_test_support.StandardBenchmarkAnchorContractDefinition:
        return benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name=self.anchor_definition_name,
            manifest_paths=(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=self.expected_anchor_case_ids(),
            include_workload=self.includes_workload,
            correctness_case_signature=self.correctness_case_signature,
            workload_signature=self.workload_signature,
            run_callback_result_parity=True,
        )


def build_compiled_pattern_module_compile_contract_cases(
    *,
    manifest_path: pathlib.Path,
    expected_build_calls_builder: Callable[[Workload], list[tuple[object, ...]]],
    success_owner_specs: Iterable[Any],
    keyword_owner_specs: Iterable[Any],
) -> tuple[CompiledPatternModuleCompileContractCase, ...]:
    success_owner_specs = tuple(success_owner_specs)
    keyword_owner_specs = tuple(keyword_owner_specs)
    keyword_case_groups = tuple(
        owner_spec.contract_case() for owner_spec in keyword_owner_specs
    )
    return (
        CompiledPatternModuleCompileContractCase(
            route=_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_ROUTE,
            case_id="success",
            manifest_path=manifest_path,
            source_selectors=tuple(
                owner_spec.includes_workload for owner_spec in success_owner_specs
            ),
            contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_contract.py"
            ),
            anchor_contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_anchor_contract.py"
            ),
            expected_anchor_pairs=tuple(
                anchor_pair
                for owner_spec in success_owner_specs
                for anchor_pair in owner_spec.expected_anchor_pairs
            ),
            expected_build_calls_builder=expected_build_calls_builder,
        ),
        *keyword_case_groups,
    )


def build_compiled_pattern_module_compile_contract_source_workload_params(
    contract_cases: Iterable[CompiledPatternModuleCompileContractCase],
) -> tuple[Any, ...]:
    return tuple(
        pytest.param(
            contract_case,
            source_workload,
            id=f"{contract_case.case_id}-{source_workload.workload_id}",
        )
        for contract_case in contract_cases
        for source_workload in contract_case.source_workloads()
    )


def build_compiled_pattern_module_contract_anchor_lanes(
    *,
    contract_cases: Iterable[CompiledPatternModuleCompileContractCase],
    published_case_ids_by_signature: Callable[
        [Callable[[Any], tuple[Any, ...] | None]],
        dict[tuple[Any, ...], tuple[str, ...]],
    ],
) -> tuple[_CompiledPatternModuleContractAnchorLane, ...]:
    contract_cases = tuple(contract_cases)
    return tuple(
        _CompiledPatternModuleContractAnchorLane(
            case_id=contract_case.case_id,
            contract_filename=contract_case.anchor_contract_filename,
            source_workloads=source_workloads,
            contract_builder_spec=contract_case.contract_builder_spec,
            expected_anchor_case_ids=contract_case.expected_anchor_case_ids,
            anchor_case_ids=published_case_ids_by_signature(
                contract_case.correctness_case_signature
            ),
            workload_signature=contract_case.workload_signature,
            include_workload=contract_case.include_workload,
            expected_anchor_pairs=contract_case.expected_anchor_pairs,
        )
        for contract_case in contract_cases
        for source_workloads in (contract_case.source_workloads(),)
    )


@cache
def _compiled_pattern_module_compile_success_owner_specs(
) -> tuple[_CompiledPatternModuleCompileSuccessOwnerSpec, ...]:
    return (
        _CompiledPatternModuleCompileSuccessOwnerSpec(
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-literal-success"
            ),
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
            anchor_expectations=(
                (
                    "module-compile-literal-warm-str-compiled-pattern",
                    ("workflow-module-compile-str-compiled-pattern",),
                ),
                (
                    "module-compile-literal-purged-bytes-compiled-pattern",
                    ("workflow-module-compile-bytes-compiled-pattern",),
                ),
            ),
            expected_anchor_pairs=(
                (
                    "module-compile-literal-warm-str-compiled-pattern-contract",
                    "workflow-module-compile-str-compiled-pattern",
                ),
                (
                    "module-compile-literal-purged-bytes-compiled-pattern-contract",
                    "workflow-module-compile-bytes-compiled-pattern",
                ),
            ),
        ),
        _CompiledPatternModuleCompileSuccessOwnerSpec(
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-named-group-success"
            ),
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
            anchor_expectations=(
                (
                    "module-compile-named-group-warm-str-compiled-pattern",
                    ("workflow-module-compile-str-compiled-pattern-named-group",),
                ),
                (
                    "module-compile-named-group-purged-bytes-compiled-pattern",
                    ("workflow-module-compile-bytes-compiled-pattern-named-group",),
                ),
            ),
            expected_anchor_pairs=(
                (
                    "module-compile-named-group-warm-str-compiled-pattern-contract",
                    "workflow-module-compile-str-compiled-pattern-named-group",
                ),
                (
                    "module-compile-named-group-purged-bytes-compiled-pattern-contract",
                    "workflow-module-compile-bytes-compiled-pattern-named-group",
                ),
            ),
        ),
    )


@cache
def _compiled_pattern_module_compile_keyword_owner_specs(
) -> tuple[_CompiledPatternModuleCompileKeywordOwnerSpec, ...]:
    return (
        _CompiledPatternModuleCompileKeywordOwnerSpec(
            case_id="int-zero",
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword"
            ),
            keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
            anchor_expectations=(
                (
                    "module-compile-flags-int-zero-warm-str-compiled-pattern",
                    ("workflow-module-compile-flags-int-zero-str-compiled-pattern",),
                ),
                (
                    "module-compile-flags-int-zero-purged-bytes-compiled-pattern",
                    ("workflow-module-compile-flags-int-zero-bytes-compiled-pattern",),
                ),
            ),
            contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_keyword_contract.py"
            ),
            anchor_contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_keyword_anchor_contract.py"
            ),
            expected_anchor_pairs=(
                (
                    "module-compile-flags-int-zero-warm-str-compiled-pattern-contract",
                    "workflow-module-compile-flags-int-zero-str-compiled-pattern",
                ),
                (
                    "module-compile-flags-int-zero-purged-bytes-compiled-pattern-contract",
                    "workflow-module-compile-flags-int-zero-bytes-compiled-pattern",
                ),
            ),
        ),
        _CompiledPatternModuleCompileKeywordOwnerSpec(
            case_id="int-zero-named-group",
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-flags-int-zero-"
                "keyword-named-group"
            ),
            keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
            anchor_expectations=(
                (
                    "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group",
                    (
                        "workflow-module-compile-flags-int-zero-str-compiled-pattern-"
                        "named-group",
                    ),
                ),
                (
                    "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group",
                    (
                        "workflow-module-compile-flags-int-zero-bytes-compiled-pattern-"
                        "named-group",
                    ),
                ),
            ),
            contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_named_group_keyword_contract.py"
            ),
            anchor_contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_named_group_keyword_anchor_contract.py"
            ),
            expected_anchor_pairs=(
                (
                    "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group-contract",
                    "workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group",
                ),
                (
                    "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group-contract",
                    "workflow-module-compile-flags-int-zero-bytes-compiled-pattern-named-group",
                ),
            ),
        ),
        _CompiledPatternModuleCompileKeywordOwnerSpec(
            case_id="bool-false",
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword"
            ),
            keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
            anchor_expectations=(
                (
                    "module-compile-flags-bool-false-warm-str-compiled-pattern",
                    ("workflow-module-compile-flags-bool-false-str-compiled-pattern",),
                ),
                (
                    "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
                    ("workflow-module-compile-flags-bool-false-bytes-compiled-pattern",),
                ),
            ),
            contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_bool_false_keyword_contract.py"
            ),
            anchor_contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_bool_false_keyword_anchor_contract.py"
            ),
            expected_anchor_pairs=(
                (
                    "module-compile-flags-bool-false-warm-str-compiled-pattern-contract",
                    "workflow-module-compile-flags-bool-false-str-compiled-pattern",
                ),
                (
                    "module-compile-flags-bool-false-purged-bytes-compiled-pattern-contract",
                    "workflow-module-compile-flags-bool-false-bytes-compiled-pattern",
                ),
            ),
        ),
        _CompiledPatternModuleCompileKeywordOwnerSpec(
            case_id="bool-false-named-group",
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-flags-bool-false-"
                "keyword-named-group"
            ),
            keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
            anchor_expectations=(
                (
                    "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group",
                    (
                        "workflow-module-compile-flags-bool-false-str-compiled-pattern-"
                        "named-group",
                    ),
                ),
                (
                    "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group",
                    (
                        "workflow-module-compile-flags-bool-false-bytes-compiled-pattern-"
                        "named-group",
                    ),
                ),
            ),
            contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_bool_false_named_group_keyword_contract.py"
            ),
            anchor_contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_bool_false_named_group_keyword_anchor_contract.py"
            ),
            expected_anchor_pairs=(
                (
                    "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group-contract",
                    "workflow-module-compile-flags-bool-false-str-compiled-pattern-named-group",
                ),
                (
                    "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group-contract",
                    "workflow-module-compile-flags-bool-false-bytes-compiled-pattern-named-group",
                ),
            ),
        ),
        _CompiledPatternModuleCompileKeywordOwnerSpec(
            case_id="ignorecase",
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-flags-ignorecase-"
                "keyword-rejection"
            ),
            keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
            anchor_expectations=(
                (
                    "module-compile-flags-ignorecase-warm-str-compiled-pattern",
                    ("workflow-module-compile-flags-ignorecase-str-compiled-pattern",),
                ),
                (
                    "module-compile-flags-ignorecase-purged-bytes-compiled-pattern",
                    ("workflow-module-compile-flags-ignorecase-bytes-compiled-pattern",),
                ),
            ),
            contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_ignorecase_keyword_contract.py"
            ),
            anchor_contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_ignorecase_keyword_anchor_contract.py"
            ),
            expected_anchor_pairs=(
                (
                    "module-compile-flags-ignorecase-warm-str-compiled-pattern-contract",
                    "workflow-module-compile-flags-ignorecase-str-compiled-pattern",
                ),
                (
                    "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-contract",
                    "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern",
                ),
            ),
            expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
        ),
        _CompiledPatternModuleCompileKeywordOwnerSpec(
            case_id="ignorecase-named-group",
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-flags-ignorecase-"
                "keyword-rejection-named-group"
            ),
            keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
            anchor_expectations=(
                (
                    "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group",
                    (
                        "workflow-module-compile-flags-ignorecase-str-compiled-pattern-"
                        "named-group",
                    ),
                ),
                (
                    "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group",
                    (
                        "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-"
                        "named-group",
                    ),
                ),
            ),
            contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_ignorecase_named_group_keyword_contract.py"
            ),
            anchor_contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_ignorecase_named_group_keyword_anchor_contract.py"
            ),
            expected_anchor_pairs=(
                (
                    "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group-contract",
                    "workflow-module-compile-flags-ignorecase-str-compiled-pattern-named-group",
                ),
                (
                    "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group-contract",
                    "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group",
                ),
            ),
            expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
        ),
    )


_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS = (
    _compiled_pattern_module_compile_success_owner_specs()
)

_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS = (
    _compiled_pattern_module_compile_keyword_owner_specs()
)


def _build_compiled_pattern_module_compile_standard_benchmark_definitions(
    *,
    success_owner_specs: Iterable[object] | None = None,
    keyword_owner_specs: Iterable[object] | None = None,
) -> tuple[benchmark_test_support.StandardBenchmarkAnchorContractDefinition, ...]:
    if success_owner_specs is None:
        success_owner_specs = _COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS
    if keyword_owner_specs is None:
        keyword_owner_specs = _COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS
    return tuple(
        owner_spec.anchor_definition()
        for owner_spec in (
            *success_owner_specs,
            *keyword_owner_specs,
        )
    )


COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS = (
    _build_compiled_pattern_module_compile_standard_benchmark_definitions()
)

_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES = (
    build_compiled_pattern_module_compile_contract_cases(
        manifest_path=benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
        expected_build_calls_builder=partial(
            benchmark_test_support.compiled_pattern_contract_expected_build_calls,
            label="module.compile contract",
        ),
        success_owner_specs=_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
        keyword_owner_specs=_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
    )
)

_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS = (
    build_compiled_pattern_module_compile_contract_source_workload_params(
        _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
    )
)

_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES = (
    build_compiled_pattern_module_contract_anchor_lanes(
        contract_cases=_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES,
        published_case_ids_by_signature=benchmark_test_support.published_case_ids_by_signature,
    )
)


@cache
def _source_tree_standard_benchmark_definitions() -> tuple[object, ...]:
    return (
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="module-workflow-compiled-pattern-wrong-text-model",
            manifest_paths=(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
                {
                    "module-search-on-bytes-string-warm-str-compiled-pattern": (
                        "workflow-module-search-str-compiled-pattern-on-bytes-string",
                    ),
                    "module-match-on-str-string-purged-bytes-compiled-pattern": (
                        "workflow-module-match-bytes-compiled-pattern-on-str-string",
                    ),
                    "module-fullmatch-on-bytes-string-warm-str-compiled-pattern": (
                        "workflow-module-fullmatch-str-compiled-pattern-on-bytes-string",
                    ),
                },
            ),
            include_workload=(
                _is_module_workflow_compiled_pattern_wrong_text_model_workload
            ),
            correctness_case_signature=(
                _module_workflow_compiled_pattern_correctness_case_signature
            ),
            workload_signature=(
                _module_workflow_compiled_pattern_workload_signature
            ),
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="optional-group-conditional",
            manifest_paths=(benchmark_test_support.OPTIONAL_GROUP_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.OPTIONAL_GROUP_MANIFEST_PATH,
                {
                    _OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID: (
                        "optional-group-conditional-module-search-present-str",
                    ),
                },
            ),
            include_workload=_is_optional_group_conditional_workload,
            correctness_case_signature=_optional_group_correctness_case_signature,
            workload_signature=_optional_group_workload_signature,
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="nested-group",
            manifest_paths=(benchmark_test_support.NESTED_GROUP_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.NESTED_GROUP_MANIFEST_PATH,
                {
                    "module-compile-nested-group-cold-str": (
                        "nested-group-compile-metadata-str",
                    ),
                    "module-search-nested-group-warm-str": (
                        "nested-group-module-search-str",
                    ),
                    "pattern-fullmatch-nested-group-purged-str": (
                        "nested-group-pattern-fullmatch-str",
                    ),
                    "module-compile-named-nested-group-warm-str": (
                        "named-nested-group-compile-metadata-str",
                    ),
                    "module-search-named-nested-group-warm-str": (
                        "named-nested-group-module-search-str",
                    ),
                    "pattern-fullmatch-named-nested-group-purged-str": (
                        "named-nested-group-pattern-fullmatch-str",
                    ),
                },
            ),
            include_workload=lambda _: True,
            correctness_case_signature=_nested_group_correctness_case_signature,
            workload_signature=_nested_group_workload_signature,
            run_callback_result_parity=True,
            expected_excluded_workload_ids=frozenset(
                {
                    "module-search-triple-nested-group-cold-gap",
                    "pattern-fullmatch-named-quantified-nested-group-purged-gap",
                }
            ),
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="exact-repeat",
            manifest_paths=(benchmark_test_support.EXACT_REPEAT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.EXACT_REPEAT_MANIFEST_PATH,
                {
                    "module-compile-numbered-exact-repeat-group-cold-str": (
                        "exact-repeat-numbered-group-compile-metadata-str",
                    ),
                    "module-search-numbered-exact-repeat-group-warm-str": (
                        "exact-repeat-numbered-group-module-search-str",
                    ),
                    "pattern-fullmatch-numbered-exact-repeat-group-purged-str": (
                        "exact-repeat-numbered-group-pattern-fullmatch-str",
                    ),
                    "module-compile-named-exact-repeat-group-warm-str": (
                        "exact-repeat-named-group-compile-metadata-str",
                    ),
                    "module-search-named-exact-repeat-group-warm-str": (
                        "exact-repeat-named-group-module-search-str",
                    ),
                    "pattern-fullmatch-named-exact-repeat-group-purged-str": (
                        "exact-repeat-named-group-pattern-fullmatch-str",
                    ),
                    "module-search-numbered-broader-ranged-repeat-group-cold-gap": (
                        "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
                    ),
                },
            ),
            include_workload=_is_non_alternation_counted_repeat_workload,
            correctness_case_signature=_counted_repeat_correctness_case_signature,
            workload_signature=_counted_repeat_workload_signature,
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="ranged-repeat",
            manifest_paths=(benchmark_test_support.RANGED_REPEAT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.RANGED_REPEAT_MANIFEST_PATH,
                {
                    "module-compile-numbered-ranged-repeat-group-cold-str": (
                        "ranged-repeat-numbered-group-compile-metadata-str",
                    ),
                    "module-search-numbered-ranged-repeat-group-lower-bound-warm-str": (
                        "ranged-repeat-numbered-group-module-search-lower-bound-str",
                    ),
                    "pattern-fullmatch-numbered-ranged-repeat-group-upper-bound-purged-str": (
                        "ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",
                    ),
                    "module-compile-named-ranged-repeat-group-warm-str": (
                        "ranged-repeat-named-group-compile-metadata-str",
                    ),
                    "module-search-named-ranged-repeat-group-upper-bound-warm-str": (
                        "ranged-repeat-named-group-module-search-upper-bound-str",
                    ),
                    "pattern-fullmatch-named-ranged-repeat-group-lower-bound-purged-str": (
                        "ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
                    ),
                    "module-search-numbered-ranged-repeat-group-wider-range-cold-gap": (
                        "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
                    ),
                },
            ),
            include_workload=_is_non_alternation_counted_repeat_workload,
            correctness_case_signature=_counted_repeat_correctness_case_signature,
            workload_signature=_counted_repeat_workload_signature,
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="grouped-alternation",
            manifest_paths=(benchmark_test_support.GROUPED_ALTERNATION_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.GROUPED_ALTERNATION_MANIFEST_PATH,
                {
                    "module-compile-grouped-alternation-cold-str": (
                        "grouped-alternation-compile-metadata-str",
                    ),
                    "module-search-grouped-alternation-warm-str": (
                        "grouped-alternation-module-search-str",
                    ),
                    "pattern-fullmatch-grouped-alternation-purged-str": (
                        "grouped-alternation-pattern-fullmatch-str",
                    ),
                    "module-compile-named-grouped-alternation-warm-str": (
                        "named-grouped-alternation-compile-metadata-str",
                    ),
                    "module-search-named-grouped-alternation-warm-str": (
                        "named-grouped-alternation-module-search-str",
                    ),
                    "pattern-fullmatch-named-grouped-alternation-purged-str": (
                        "named-grouped-alternation-pattern-fullmatch-str",
                    ),
                    "module-sub-template-nested-grouped-alternation-warm-gap": (
                        "module-sub-template-nested-group-alternation-numbered-wrapper-str",
                    ),
                    "pattern-subn-template-named-nested-grouped-alternation-purged-gap": (
                        "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
                    ),
                },
            ),
            include_workload=lambda _: True,
            correctness_case_signature=_grouped_alternation_correctness_case_signature,
            workload_signature=_grouped_alternation_workload_signature,
            run_callback_result_parity=True,
            expected_legacy_workload_ids=frozenset(
                {
                    "module-sub-template-nested-grouped-alternation-warm-gap",
                    "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
                }
            ),
            callback_anchor_workload_ids=frozenset(
                {
                    "module-sub-template-nested-grouped-alternation-warm-gap",
                    "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
                }
            ),
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="grouped-alternation-replacement",
            manifest_paths=(benchmark_test_support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-sub-template-grouped-alternation-warm-str": (
                        "module-sub-template-grouped-alternation-str",
                    ),
                    "module-subn-template-grouped-alternation-warm-str": (
                        "module-subn-template-grouped-alternation-str",
                    ),
                    "pattern-sub-template-grouped-alternation-purged-str": (
                        "pattern-sub-template-grouped-alternation-str",
                    ),
                    "pattern-subn-template-grouped-alternation-purged-str": (
                        "pattern-subn-template-grouped-alternation-str",
                    ),
                    "module-sub-template-named-grouped-alternation-warm-str": (
                        "module-sub-template-named-grouped-alternation-str",
                    ),
                    "module-subn-template-named-grouped-alternation-warm-str": (
                        "module-subn-template-named-grouped-alternation-str",
                    ),
                    "pattern-sub-template-named-grouped-alternation-purged-str": (
                        "pattern-sub-template-named-grouped-alternation-str",
                    ),
                    "pattern-subn-template-named-grouped-alternation-purged-str": (
                        "pattern-subn-template-named-grouped-alternation-str",
                    ),
                    "module-sub-template-nested-grouped-alternation-cold-gap": (
                        "module-sub-template-nested-group-alternation-numbered-outer-str",
                    ),
                    "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap": (
                        "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
                    ),
                },
            ),
            include_workload=lambda _: True,
            correctness_case_signature=(
                _grouped_alternation_replacement_correctness_case_signature
            ),
            workload_signature=_grouped_alternation_workload_signature,
            run_callback_result_parity=True,
            expected_legacy_workload_ids=frozenset(
                {
                    "module-sub-template-nested-grouped-alternation-cold-gap",
                    "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
                }
            ),
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="nested-group-replacement",
            manifest_paths=(benchmark_test_support.NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-sub-template-nested-group-numbered-warm-str": (
                        "module-sub-template-nested-group-numbered-str",
                    ),
                    "module-subn-template-nested-group-numbered-warm-str": (
                        "module-subn-template-nested-group-numbered-str",
                    ),
                    "pattern-sub-template-nested-group-numbered-purged-str": (
                        "pattern-sub-template-nested-group-numbered-str",
                    ),
                    "pattern-subn-template-nested-group-numbered-purged-str": (
                        "pattern-subn-template-nested-group-numbered-str",
                    ),
                    "module-sub-template-nested-group-named-warm-str": (
                        "module-sub-template-nested-group-named-str",
                    ),
                    "module-subn-template-nested-group-named-warm-str": (
                        "module-subn-template-nested-group-named-str",
                    ),
                    "pattern-sub-template-nested-group-named-purged-str": (
                        "pattern-sub-template-nested-group-named-str",
                    ),
                    "pattern-subn-template-nested-group-named-purged-str": (
                        "pattern-subn-template-nested-group-named-str",
                    ),
                    "module-sub-template-numbered-quantified-nested-group-replacement-lower-bound-warm-str": (
                        "module-sub-template-quantified-nested-group-numbered-lower-bound-str",
                    ),
                    "module-subn-template-numbered-quantified-nested-group-replacement-first-match-only-warm-str": (
                        "module-subn-template-quantified-nested-group-numbered-first-match-only-str",
                    ),
                    "pattern-sub-template-named-quantified-nested-group-replacement-repeated-outer-purged-str": (
                        "pattern-sub-template-quantified-nested-group-named-repeated-outer-capture-str",
                    ),
                    "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap": (
                        "pattern-subn-template-quantified-nested-group-named-first-match-only-str",
                    ),
                    "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str": (
                        "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                    ),
                    "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str": (
                        "module-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                    ),
                    "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str": (
                        "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-str",
                    ),
                    "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str": (
                        "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                    ),
                    "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str": (
                        "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                    ),
                    "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str": (
                        "module-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                    ),
                    "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str": (
                        "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                    ),
                    "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str": (
                        "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                    ),
                    "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str": (
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                    ),
                    "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str": (
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                    ),
                    "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str": (
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                    ),
                    "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str": (
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                    ),
                    "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str": (
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
                    ),
                    "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str": (
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
                    ),
                    "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str": (
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-str",
                    ),
                    "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str": (
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
                    ),
                },
            ),
            include_workload=lambda _: True,
            correctness_case_signature=(
                _grouped_alternation_replacement_correctness_case_signature
            ),
            workload_signature=_grouped_alternation_workload_signature,
            run_callback_result_parity=True,
            expected_special_unanchored_workload_ids=(
                "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
                "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
                "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
                "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
                "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
                "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
                "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
                "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
                "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
                "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
                "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
                "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
            ),
            run_special_unanchored_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="open-ended-grouped-alternation",
            manifest_paths=(benchmark_test_support.OPEN_ENDED_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.OPEN_ENDED_MANIFEST_PATH,
                {
                    "module-compile-numbered-open-ended-group-alternation-cold-str": (
                        "open-ended-quantified-group-alternation-numbered-compile-metadata-str",
                    ),
                    "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-str": (
                        "open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
                    ),
                    "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-str": (
                        "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
                    ),
                    "module-compile-named-open-ended-group-alternation-warm-str": (
                        "open-ended-quantified-group-alternation-named-compile-metadata-str",
                    ),
                    "module-search-named-open-ended-group-alternation-lower-bound-de-warm-str": (
                        "open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",
                    ),
                    "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-str": (
                        "open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",
                    ),
                    "module-compile-numbered-open-ended-group-alternation-cold-bytes": (
                        "open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",
                    ),
                    "module-compile-named-open-ended-group-alternation-warm-bytes": (
                        "open-ended-quantified-group-alternation-named-compile-metadata-bytes",
                    ),
                    "module-compile-numbered-open-ended-group-conditional-cold-str": (
                        "open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",
                    ),
                    "module-compile-numbered-open-ended-group-broader-range-cold-str": (
                        "broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-str",
                    ),
                    "module-search-numbered-open-ended-group-broader-range-cold-gap": (
                        "broader-range-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
                    ),
                    "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-str": (
                        "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
                    ),
                    "module-compile-named-open-ended-group-broader-range-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-named-compile-metadata-str",
                    ),
                    "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",
                    ),
                    "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-str": (
                        "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",
                    ),
                    "module-compile-numbered-open-ended-group-broader-range-cold-bytes": (
                        "broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",
                    ),
                    "module-compile-named-open-ended-group-broader-range-warm-bytes": (
                        "broader-range-open-ended-quantified-group-alternation-named-compile-metadata-bytes",
                    ),
                    "module-compile-numbered-open-ended-group-broader-range-conditional-cold-str": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",
                    ),
                    "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
                    ),
                    "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
                    ),
                    "module-compile-named-open-ended-group-broader-range-conditional-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",
                    ),
                    "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
                    ),
                    "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
                    ),
                    "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",
                    ),
                    "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",
                    ),
                    "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-str": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
                    ),
                    "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
                    ),
                    "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-str": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
                    ),
                    "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
                    ),
                    "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-str",
                    ),
                    "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
                    ),
                    "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",
                    ),
                    "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-str": (
                        "open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
                    ),
                    "module-compile-named-open-ended-group-conditional-warm-str": (
                        "open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",
                    ),
                    "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-str": (
                        "open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
                    ),
                    "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-str": (
                        "open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
                    ),
                    "module-compile-numbered-open-ended-group-conditional-cold-bytes": (
                        "open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",
                    ),
                    "module-compile-named-open-ended-group-conditional-warm-bytes": (
                        "open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",
                    ),
                    "module-compile-numbered-open-ended-group-backtracking-heavy-cold-str": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
                    ),
                    "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-str": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
                    ),
                    "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-str": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
                    ),
                    "module-compile-named-open-ended-group-backtracking-heavy-warm-str": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
                    ),
                    "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-str": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-str",
                    ),
                    "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-gap": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-fourth-repetition-short-only-str",
                    ),
                    "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
                    ),
                    "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",
                    ),
                },
            ),
            include_workload=lambda _: True,
            correctness_case_signature=_counted_repeat_correctness_case_signature,
            workload_signature=_counted_repeat_workload_signature,
            run_callback_result_parity=True,
            expected_special_unanchored_workload_ids=(
                "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
                "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
                "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
                "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
                "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
                "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
                "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
                "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
                "module-search-numbered-open-ended-group-conditional-warm-gap",
                "module-search-numbered-open-ended-group-conditional-second-repetition-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
                "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
                "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
                "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
            ),
            direct_parity_supplemental_cases=(
                *OPEN_ENDED_ALTERNATION_BYTES_CASES,
                *OPEN_ENDED_CONDITIONAL_BYTES_CASES,
                *OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
                *BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
                *BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
                *BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
            ),
            run_special_unanchored_result_parity=True,
        ),
    )




@dataclass(frozen=True, slots=True)
class SourceTreeBenchmarkCommonCase:
    expected_adapter: str
    expected_phase: str
    expected_runner_version: str
    expected_summary: dict[str, int]
    manifests: list[BenchmarkManifest]
    selection_mode: str

    def manifest_for_id(self, manifest_id: str) -> BenchmarkManifest:
        for manifest in self.manifests:
            if manifest.manifest_id == manifest_id:
                return manifest
        raise AssertionError(f"unknown source-tree benchmark manifest {manifest_id!r}")

    def selected_workload_ids_for_manifest(self, manifest_id: str) -> tuple[str, ...]:
        return tuple(
            workload.workload_id
            for workload in self.manifest_for_id(manifest_id).selected_workloads(
                selection_mode=self.selection_mode
            )
        )


@dataclass(frozen=True, slots=True)
class SourceTreeManifestExpectation:
    known_gap_count: int
    representative_measured_workload_ids: tuple[str, ...] = ()
    representative_known_gap_workload_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SourceTreeDeferredExpectation:
    area: str
    follow_up: str


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedCase(SourceTreeBenchmarkCommonCase):
    manifest_expectation: SourceTreeManifestExpectation
    manifest_id: str
    target_manifest: BenchmarkManifest


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedPatternGroupExpectation:
    slice_id: str
    patterns: tuple[str, ...]
    minimum_rows: int
    required_operations: tuple[str, ...]
    required_categories: tuple[str, ...]
    search_haystacks: tuple[str, ...]
    search_haystack_substrings: tuple[str, ...]
    pattern_haystacks: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedManifestShapeExpectation:
    representative_measured_workload_ids: tuple[str, ...]
    pattern_groups: tuple[SourceTreeCombinedPatternGroupExpectation, ...] = ()


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedFullyMeasuredManifestExpectation:
    coverage_group: str
    representative_measured_workload_ids: tuple[str, ...]
    expected_measured_workload_count: int
    expected_total_workload_count: int | None = None


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedManifestExpectationDefinition:
    exclude_from_combined_targets: bool = False
    promote_zero_gap_representatives: bool = False
    known_gap_workload_ids: tuple[str, ...] | None = None
    representative_measured_workload_ids: tuple[str, ...] | None = None
    representative_known_gap_workload_ids: tuple[str, ...] | None = None
    fully_measured_expectation: SourceTreeCombinedFullyMeasuredManifestExpectation | None = None
    shape_expectation: SourceTreeCombinedManifestShapeExpectation | None = None
    zero_gap_bytes_representative_subsets: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedSliceExpectation:
    manifest_id: str
    slice_id: str
    required_syntax_features: tuple[str, ...] = ()
    excluded_syntax_features: tuple[str, ...] = ()
    required_categories: tuple[str, ...] = ()
    excluded_categories: tuple[str, ...] = ()
    required_id_suffix: str | None = None
    expected_workload_ids: tuple[str, ...] = ()
    expected_patterns: frozenset[str] = frozenset()
    expected_operations: frozenset[str] = frozenset()
    expected_haystacks: frozenset[str] = frozenset()
    required_row_categories: tuple[str, ...] = ()
    expected_status: str = "measured"

def _combined_manifest_definition(
    *,
    exclude_from_combined_targets: bool = False,
    promote_zero_gap_representatives: bool = False,
    known_gap_workload_ids: tuple[str, ...] | None = None,
    representative_measured_workload_ids: tuple[str, ...] | None = None,
    representative_known_gap_workload_ids: tuple[str, ...] | None = None,
    fully_measured_expectation: SourceTreeCombinedFullyMeasuredManifestExpectation
    | None = None,
    shape_expectation: SourceTreeCombinedManifestShapeExpectation | None = None,
    zero_gap_bytes_representative_subsets: tuple[tuple[str, ...], ...] = (),
) -> SourceTreeCombinedManifestExpectationDefinition:
    if fully_measured_expectation is not None:
        if representative_measured_workload_ids is None:
            representative_measured_workload_ids = (
                fully_measured_expectation.representative_measured_workload_ids
            )
        elif (
            representative_measured_workload_ids
            != fully_measured_expectation.representative_measured_workload_ids
        ):
            raise AssertionError(
                "fully measured manifest definitions must keep their "
                "representative rows on the shared definition-owned contract"
            )
    return SourceTreeCombinedManifestExpectationDefinition(
        exclude_from_combined_targets=exclude_from_combined_targets,
        promote_zero_gap_representatives=promote_zero_gap_representatives,
        known_gap_workload_ids=known_gap_workload_ids,
        representative_measured_workload_ids=representative_measured_workload_ids,
        representative_known_gap_workload_ids=representative_known_gap_workload_ids,
        fully_measured_expectation=fully_measured_expectation,
        shape_expectation=shape_expectation,
        zero_gap_bytes_representative_subsets=tuple(
            tuple(str(workload_id) for workload_id in workload_ids)
            for workload_ids in zero_gap_bytes_representative_subsets
        ),
    )


def _combined_fully_measured_manifest_expectation(
    *,
    coverage_group: str,
    representative_measured_workload_ids: tuple[str, ...],
    expected_measured_workload_count: int,
    expected_total_workload_count: int | None = None,
) -> SourceTreeCombinedFullyMeasuredManifestExpectation:
    return SourceTreeCombinedFullyMeasuredManifestExpectation(
        coverage_group=coverage_group,
        representative_measured_workload_ids=tuple(
            str(workload_id) for workload_id in representative_measured_workload_ids
        ),
        expected_measured_workload_count=expected_measured_workload_count,
        expected_total_workload_count=expected_total_workload_count,
    )


@cache
def _published_benchmark_manifest_ids() -> frozenset[str]:
    return frozenset(
        manifest.manifest_id for manifest in published_benchmark_manifests()
    )


_SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION = _combined_manifest_definition()


class _SourceTreeCombinedManifestExpectations(
    dict[str, SourceTreeCombinedManifestExpectationDefinition]
):
    def _supports_fallback(self, manifest_id: object) -> bool:
        return (
            isinstance(manifest_id, str)
            and manifest_id in _published_benchmark_manifest_ids()
        )

    def __missing__(
        self,
        manifest_id: str,
    ) -> SourceTreeCombinedManifestExpectationDefinition:
        if self._supports_fallback(manifest_id):
            return _SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION
        raise KeyError(manifest_id)

    def get(
        self,
        manifest_id: str,
        default: SourceTreeCombinedManifestExpectationDefinition | None = None,
    ) -> SourceTreeCombinedManifestExpectationDefinition | None:
        if self._supports_fallback(manifest_id):
            return self[manifest_id]
        return default

    def __contains__(self, manifest_id: object) -> bool:
        return super().__contains__(manifest_id) or self._supports_fallback(
            manifest_id
        )


SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS = _SourceTreeCombinedManifestExpectations({
    "compile-matrix": _combined_manifest_definition(
        exclude_from_combined_targets=True,
    ),
    "module-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
            "import-module-cold",
            "module-search-grouped-literal-cold-hit",
            "module-search-literal-warm-hit",
            "module-search-flags-keyword-warm-str",
            "module-search-duplicate-flags-keyword-warm-str",
            "module-match-flags-keyword-purged-bytes",
            "module-fullmatch-flags-keyword-warm-str",
            "module-fullmatch-unexpected-keyword-purged-str",
            "module-search-bytes-cold-miss",
        ),
    ),
    "pattern-boundary": _combined_manifest_definition(
        shape_expectation=SourceTreeCombinedManifestShapeExpectation(
            representative_measured_workload_ids=(
                "pattern-search-literal-warm-hit",
                "pattern-fullmatch-bytes-purged-hit",
            ),
        ),
    ),
    "grouped-named-boundary": _combined_manifest_definition(
        promote_zero_gap_representatives=True,
        representative_measured_workload_ids=(
            "module-search-grouped-segment-cold-gap",
            "pattern-search-grouped-segment-warm-gap",
        ),
    ),
    "numbered-backreference-boundary": _combined_manifest_definition(
        promote_zero_gap_representatives=True,
        representative_measured_workload_ids=(
            "module-search-numbered-backreference-segment-cold-gap",
            "pattern-search-numbered-backreference-prefix-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "grouped-alternation-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-sub-template-nested-grouped-alternation-warm-gap",
            "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "grouped-alternation-replacement-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-sub-template-nested-grouped-alternation-cold-gap",
            "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "nested-group-boundary": _combined_manifest_definition(
        promote_zero_gap_representatives=True,
        representative_measured_workload_ids=(
            "module-search-triple-nested-group-cold-gap",
            "pattern-fullmatch-named-quantified-nested-group-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "branch-local-backreference-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-str",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-str",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-str",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-str",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-str",
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-bytes",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-bytes",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-bytes",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-bytes",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-bytes",
        ),
        zero_gap_bytes_representative_subsets=(
            (
                "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-bytes",
                "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-bytes",
                "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-bytes",
                "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-bytes",
                "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-bytes",
            ),
        ),
    ),
    "optional-group-boundary": _combined_manifest_definition(
        promote_zero_gap_representatives=True,
        representative_measured_workload_ids=(
            "module-search-numbered-optional-group-conditional-cold-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "exact-repeat-quantified-group-boundary": _combined_manifest_definition(
        fully_measured_expectation=_combined_fully_measured_manifest_expectation(
            coverage_group="counted-repeat",
            representative_measured_workload_ids=(
                "module-search-numbered-broader-ranged-repeat-group-cold-gap",
            ),
            expected_measured_workload_count=13,
        ),
        representative_known_gap_workload_ids=(),
    ),
    "ranged-repeat-quantified-group-boundary": _combined_manifest_definition(
        fully_measured_expectation=_combined_fully_measured_manifest_expectation(
            coverage_group="counted-repeat",
            representative_measured_workload_ids=(
                "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
            ),
            expected_measured_workload_count=8,
        ),
        representative_known_gap_workload_ids=(),
    ),
    "wider-ranged-repeat-quantified-group-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-third-repetition-mixed-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-str",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-str",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-conditional-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-bytes",
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-third-repetition-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-upper-bound-all-de-purged-bytes",
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-str",
            "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-conditional-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-broader-range-conditional-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-bytes",
            "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
            "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-open-ended-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-open-ended-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-open-ended-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-bytes",
        ),
        zero_gap_bytes_representative_subsets=(
            (
                "module-compile-numbered-wider-ranged-repeat-group-broader-range-conditional-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-broader-range-conditional-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-third-repetition-mixed-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-nested-broader-range-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-nested-broader-range-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-upper-bound-all-de-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-bytes",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-nested-broader-range-conditional-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-open-ended-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-open-ended-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-open-ended-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-bytes",
            ),
        ),
        shape_expectation=SourceTreeCombinedManifestShapeExpectation(
            representative_measured_workload_ids=(
                "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-str",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-str",
            ),
            pattern_groups=(
                SourceTreeCombinedPatternGroupExpectation(
                    slice_id="broader-range-grouped-backtracking-heavy",
                    patterns=(
                        "a((bc|b)c){1,4}d",
                        "a(?P<word>(bc|b)c){1,4}d",
                    ),
                    minimum_rows=12,
                    required_operations=(
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    required_categories=(
                        "grouped",
                        "alternation",
                        "backtracking-heavy",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    search_haystacks=(
                        "zzabcdzz",
                        "zzabccdzz",
                    ),
                    search_haystack_substrings=(),
                    pattern_haystacks=(
                        "abcbccd",
                        "abcbccbccbcd",
                    ),
                ),
                SourceTreeCombinedPatternGroupExpectation(
                    slice_id="nested-broader-range-grouped-alternation",
                    patterns=(
                        "a((bc|de){1,4})d",
                        "a(?P<outer>(bc|de){1,4})d",
                    ),
                    minimum_rows=12,
                    required_operations=(
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    required_categories=(
                        "nested-group",
                        "alternation",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    search_haystacks=(),
                    search_haystack_substrings=(
                        "abcd",
                        "aded",
                    ),
                    pattern_haystacks=(
                        "abcbcded",
                        "adedededed",
                    ),
                ),
                SourceTreeCombinedPatternGroupExpectation(
                    slice_id="nested-broader-range-grouped-conditional",
                    patterns=(
                        "a(((bc|de){1,4})d)?(?(1)e|f)",
                        "a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)",
                    ),
                    minimum_rows=14,
                    required_operations=(
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    required_categories=(
                        "nested-group",
                        "alternation",
                        "conditional",
                        "optional-group",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    search_haystacks=(
                        "zzafzz",
                        "zzabcdezz",
                        "zzadedezz",
                    ),
                    search_haystack_substrings=(),
                    pattern_haystacks=(
                        "abcbcdede",
                        "adedededede",
                    ),
                ),
                SourceTreeCombinedPatternGroupExpectation(
                    slice_id="nested-broader-range-grouped-backtracking-heavy",
                    patterns=(
                        "a(((bc|b)c){1,4})d",
                        "a(?P<outer>((bc|b)c){1,4})d",
                    ),
                    minimum_rows=14,
                    required_operations=(
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    required_categories=(
                        "grouped",
                        "nested-group",
                        "alternation",
                        "backtracking-heavy",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    search_haystacks=(
                        "zzabcdzz",
                        "zzabccdzz",
                    ),
                    search_haystack_substrings=(),
                    pattern_haystacks=(
                        "abcbccd",
                        "abccbcd",
                        "abcbccbccbcd",
                    ),
                ),
            ),
        ),
    ),
    "open-ended-quantified-group-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-compile-numbered-open-ended-group-alternation-cold-bytes",
            "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-alternation-warm-bytes",
            "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
            "module-compile-numbered-open-ended-group-conditional-cold-bytes",
            "module-search-numbered-open-ended-group-conditional-second-repetition-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-conditional-warm-bytes",
            "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
            "module-compile-numbered-open-ended-group-broader-range-cold-bytes",
            "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-broader-range-warm-bytes",
            "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
            "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes",
            "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes",
            "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
            "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes",
            "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes",
            "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
        ),
        zero_gap_bytes_representative_subsets=(
            (
                "module-compile-numbered-open-ended-group-conditional-cold-bytes",
                "module-search-numbered-open-ended-group-conditional-second-repetition-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
                "module-compile-named-open-ended-group-conditional-warm-bytes",
                "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
                "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes",
                "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
                "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes",
                "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            ),
            (
                "module-compile-numbered-open-ended-group-alternation-cold-bytes",
                "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
                "module-compile-named-open-ended-group-alternation-warm-bytes",
                "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
            ),
            (
                "module-compile-numbered-open-ended-group-broader-range-cold-bytes",
                "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
                "module-compile-named-open-ended-group-broader-range-warm-bytes",
                "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
            ),
            (
                "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes",
                "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
                "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes",
                "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
            ),
            (
                "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes",
                "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
                "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes",
                "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
            ),
        ),
    ),
    "quantified-alternation-boundary": _combined_manifest_definition(
        fully_measured_expectation=_combined_fully_measured_manifest_expectation(
            coverage_group="quantified-alternation",
            representative_measured_workload_ids=(
                "module-compile-numbered-quantified-alternation-cold-bytes",
                "module-search-numbered-quantified-alternation-lower-bound-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-second-repetition-purged-bytes",
                "module-compile-named-quantified-alternation-warm-bytes",
                "module-search-named-quantified-alternation-second-repetition-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-lower-bound-purged-bytes",
                "module-compile-numbered-quantified-alternation-nested-branch-cold-bytes",
                "module-search-numbered-quantified-alternation-nested-branch-lower-bound-inner-branch-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-nested-branch-lower-bound-literal-branch-purged-bytes",
                "module-compile-named-quantified-alternation-nested-branch-warm-bytes",
                "module-search-named-quantified-alternation-nested-branch-lower-bound-literal-branch-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-nested-branch-second-repetition-mixed-purged-bytes",
                "module-search-numbered-quantified-alternation-branch-backref-cold-bytes",
                "module-compile-numbered-quantified-alternation-branch-backref-cold-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-branch-backref-second-repetition-purged-bytes",
                "module-compile-named-quantified-alternation-branch-backref-warm-bytes",
                "module-search-named-quantified-alternation-branch-backref-lower-bound-c-branch-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-branch-backref-second-repetition-purged-bytes",
                "module-compile-numbered-quantified-alternation-broader-range-cold-bytes",
                "module-search-numbered-quantified-alternation-broader-range-third-repetition-cold-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-broader-range-third-repetition-bcb-purged-bytes",
                "module-compile-named-quantified-alternation-broader-range-warm-bytes",
                "module-search-named-quantified-alternation-broader-range-third-repetition-bcc-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-broader-range-third-repetition-bbb-purged-bytes",
                "module-compile-numbered-quantified-alternation-open-ended-cold-bytes",
                "module-search-numbered-quantified-alternation-open-ended-lower-bound-b-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-open-ended-fourth-repetition-bcbc-purged-bytes",
                "module-compile-named-quantified-alternation-open-ended-warm-bytes",
                "module-search-named-quantified-alternation-open-ended-lower-bound-c-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-open-ended-fourth-repetition-bcbc-purged-bytes",
                "module-compile-numbered-quantified-alternation-conditional-cold-bytes",
                "module-search-numbered-quantified-alternation-conditional-lower-bound-b-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-conditional-second-repetition-mixed-purged-bytes",
                "module-compile-named-quantified-alternation-conditional-warm-bytes",
                "module-search-named-quantified-alternation-conditional-absent-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-conditional-second-repetition-c-purged-bytes",
                "module-compile-numbered-quantified-alternation-backtracking-heavy-cold-bytes",
                "module-search-numbered-quantified-alternation-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-backtracking-heavy-lower-bound-bc-branch-purged-bytes",
                "module-compile-named-quantified-alternation-backtracking-heavy-warm-bytes",
                "module-search-named-quantified-alternation-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            ),
            expected_measured_workload_count=84,
            expected_total_workload_count=84,
        ),
    ),
    "conditional-group-exists-boundary": _combined_manifest_definition(
        zero_gap_bytes_representative_subsets=(
            (
                "module-sub-template-numbered-conditional-group-exists-replacement-warm-bytes",
                "module-subn-template-numbered-conditional-group-exists-replacement-warm-bytes",
                "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-bytes",
                "module-sub-template-named-conditional-group-exists-replacement-warm-bytes",
                "module-subn-template-named-conditional-group-exists-replacement-warm-bytes",
                "pattern-sub-template-named-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-template-named-conditional-group-exists-replacement-purged-bytes",
                "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-bytes",
                "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-bytes",
            ),
            (
                "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged-bytes",
                "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm-bytes",
                "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged-bytes",
                "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
                "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
                "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
                "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
                "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
                "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
            ),
            (
                "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-bytes",
                "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
                "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
                "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-bytes",
                "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
                "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
                "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
                "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
                "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
                "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
                "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
                "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
                "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
                "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
                "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
                "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
                "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
                "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
            ),
            (
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm-bytes",
                "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-purged-bytes",
                "module-sub-callable-named-quantified-conditional-group-exists-replacement-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-warm-bytes",
                "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-purged-bytes",
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
                "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
                "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
                "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
                "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
                "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
                "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
                "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
                "module-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
                "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
            ),
            (
                "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
                "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
                "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
                "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
                "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
                "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
                "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
            ),
        ),
    ),
    "regression-matrix": _combined_manifest_definition(
        exclude_from_combined_targets=True,
        representative_measured_workload_ids=(
            "regression-parser-bytes-backreference-purged",
        ),
    ),
})



SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS = (
    SourceTreeCombinedSliceExpectation(
        manifest_id="module-boundary",
        slice_id="anchored-module-compile-cluster",
        required_syntax_features=("module-compile", "literal-text"),
        excluded_syntax_features=("compiled-pattern-first-argument",),
        required_categories=("compile", "literal"),
        expected_workload_ids=(
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
        ),
        expected_patterns=frozenset({r"^abc$"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=("compile", "literal"),
        expected_status="measured",
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-literal-success",
        required_syntax_features=(
            "module-compile",
            "literal-text",
            "compiled-pattern-first-argument",
        ),
        excluded_syntax_features=("keyword-flags",),
        required_categories=("compile", "literal", "compiled-pattern"),
        excluded_categories=("keyword", "flags"),
        expected_workload_ids=(
            "module-compile-literal-warm-str-compiled-pattern",
            "module-compile-literal-purged-bytes-compiled-pattern",
        ),
        expected_patterns=frozenset({"abc"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=("compile", "literal", "compiled-pattern"),
        expected_status="measured",
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-named-group-success",
        required_syntax_features=(
            "module-compile",
            "grouping-forms",
            "named-groups",
            "compiled-pattern-first-argument",
        ),
        required_categories=("compile", "named-group", "compiled-pattern"),
        excluded_syntax_features=("keyword-flags",),
        excluded_categories=("keyword", "flags"),
        expected_workload_ids=(
            "module-compile-named-group-warm-str-compiled-pattern",
            "module-compile-named-group-purged-bytes-compiled-pattern",
        ),
        expected_patterns=frozenset({"(?P<word>abc)"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=("compile", "named-group", "compiled-pattern"),
        expected_status="measured",
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-int-zero-keyword-named-group",
        required_syntax_features=(
            "module-compile",
            "grouping-forms",
            "named-groups",
            "compiled-pattern-first-argument",
            "keyword-flags",
        ),
        required_categories=("compile", "named-group", "compiled-pattern", "keyword", "flags"),
        excluded_categories=("bool", "ignorecase", "exception"),
        expected_workload_ids=(
            "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group",
            "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group",
        ),
        expected_patterns=frozenset({"(?P<word>abc)"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
        ),
        expected_status="measured",
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-bool-false-keyword-named-group",
        required_syntax_features=(
            "module-compile",
            "grouping-forms",
            "named-groups",
            "compiled-pattern-first-argument",
            "keyword-flags",
        ),
        required_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
            "bool",
        ),
        expected_workload_ids=(
            "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group",
            "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group",
        ),
        expected_patterns=frozenset({"(?P<word>abc)"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
            "bool",
        ),
        expected_status="measured",
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-ignorecase-keyword-rejection-named-group",
        required_syntax_features=(
            "module-compile",
            "grouping-forms",
            "named-groups",
            "compiled-pattern-first-argument",
            "keyword-flags",
            "ignorecase-flag",
        ),
        required_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
            "ignorecase",
            "exception",
        ),
        expected_workload_ids=(
            "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group",
            "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group",
        ),
        expected_patterns=frozenset({"(?P<word>abc)"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
            "ignorecase",
            "exception",
        ),
        expected_status="measured",
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-int-zero-keyword",
        required_syntax_features=(
            "module-compile",
            "literal-text",
            "compiled-pattern-first-argument",
            "keyword-flags",
        ),
        required_categories=("compile", "literal", "compiled-pattern", "keyword", "flags"),
        excluded_categories=("bool", "ignorecase", "exception"),
        expected_workload_ids=(
            "module-compile-flags-int-zero-warm-str-compiled-pattern",
            "module-compile-flags-int-zero-purged-bytes-compiled-pattern",
        ),
        expected_patterns=frozenset({"abc"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=("compile", "literal", "compiled-pattern", "keyword", "flags"),
        expected_status="measured",
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-bool-false-keyword",
        required_syntax_features=(
            "module-compile",
            "literal-text",
            "compiled-pattern-first-argument",
            "keyword-flags",
        ),
        required_categories=(
            "compile",
            "literal",
            "compiled-pattern",
            "keyword",
            "flags",
            "bool",
        ),
        expected_workload_ids=(
            "module-compile-flags-bool-false-warm-str-compiled-pattern",
            "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
        ),
        expected_patterns=frozenset({"abc"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=(
            "compile",
            "literal",
            "compiled-pattern",
            "keyword",
            "flags",
            "bool",
        ),
        expected_status="measured",
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-ignorecase-keyword-rejection",
        required_syntax_features=(
            "module-compile",
            "literal-text",
            "compiled-pattern-first-argument",
            "keyword-flags",
            "ignorecase-flag",
        ),
        required_categories=(
            "compile",
            "literal",
            "compiled-pattern",
            "keyword",
            "flags",
            "ignorecase",
            "exception",
        ),
        expected_workload_ids=(
            "module-compile-flags-ignorecase-warm-str-compiled-pattern",
            "module-compile-flags-ignorecase-purged-bytes-compiled-pattern",
        ),
        expected_patterns=frozenset({"abc"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=(
            "compile",
            "literal",
            "compiled-pattern",
            "keyword",
            "flags",
            "ignorecase",
            "exception",
        ),
        expected_status="measured",
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="branch-local-backreference-boundary",
        slice_id="broader-range-open-ended-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "conditionals",
            "nested-groups",
            "counted-repeats",
        ),
        required_categories=("open-ended-repeat", "broader-range"),
        expected_workload_ids=(
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-str",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-str",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-str",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-str",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-str",
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-bytes",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-bytes",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-bytes",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-bytes",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        }),
        expected_operations=frozenset({"module.compile", "module.search", "pattern.fullmatch"}),
        expected_haystacks=frozenset({"zzabbbdzz", "abcbccd", "zzacccdzz", "abbbd"}),
        required_row_categories=(
            "grouped",
            "nested-group",
            "alternation",
            "branch-local",
            "conditional",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="quantified-nested-alternation",
        required_syntax_features=("alternation", "quantifiers"),
        excluded_syntax_features=("branch-local-backreferences",),
        expected_workload_ids=(
            "module-search-nested-group-quantified-alternation-cold-gap",
            "pattern-fullmatch-numbered-quantified-nested-group-alternation-repeated-mixed-purged-str",
            "module-search-named-quantified-nested-group-alternation-lower-bound-c-warm-str",
            "pattern-fullmatch-named-quantified-nested-group-alternation-repeated-mixed-purged-str",
        ),
        expected_patterns=frozenset({
            r"a((b|c)+)d",
            r"a(?P<outer>(?P<inner>b|c)+)d",
        }),
        expected_operations=frozenset({"module.search", "pattern.fullmatch"}),
        expected_haystacks=frozenset({"zzabdzz", "acbbd", "zzacdzz", "abccd"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "quantified",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="non-quantified-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences",),
        excluded_syntax_features=("quantifiers",),
        expected_workload_ids=(
            "module-search-numbered-nested-group-branch-local-backreference-b-branch-warm-str",
            "module-compile-named-nested-group-branch-local-backreference-warm-str",
            "pattern-fullmatch-named-nested-group-branch-local-backreference-purged-gap",
        ),
        expected_patterns=frozenset({
            r"a((b|c))\2d",
            r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        }),
        expected_operations=frozenset({"module.compile", "module.search", "pattern.fullmatch"}),
        expected_haystacks=frozenset({"zzabbdzz", "accd"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="quantified-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences", "quantifiers"),
        excluded_syntax_features=("counted-repeats",),
        expected_workload_ids=(
            "module-search-numbered-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-search-numbered-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-compile-named-quantified-nested-group-branch-local-backreference-warm-str",
            "module-compile-named-quantified-nested-group-branch-local-backreference-warm-bytes",
            "pattern-fullmatch-named-quantified-nested-group-branch-local-backreference-repeated-mixed-purged-str",
            "pattern-fullmatch-named-quantified-nested-group-branch-local-backreference-repeated-mixed-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c)+)\2d",
            r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        }),
        expected_operations=frozenset({"module.compile", "module.search", "pattern.fullmatch"}),
        expected_haystacks=frozenset({"zzabbdzz", "abccd"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="broader-range-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "counted-repeats",
            "ranged-repeats",
        ),
        expected_workload_ids=(
            "module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-str",
            "module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.compile", "module.search", "pattern.fullmatch"}),
        expected_haystacks=frozenset({"zzabbdzz", "acccccd"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="broader-range-open-ended-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences", "counted-repeats"),
        excluded_syntax_features=("ranged-repeats",),
        required_categories=("open-ended-repeat", "broader-range"),
        expected_workload_ids=(
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-str",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-bytes",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.compile", "module.search", "pattern.fullmatch"}),
        expected_haystacks=frozenset({"zzabbbdzz", "acccd"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-group-bytes",
        required_syntax_features=("callable-replacement", "pattern-text-model"),
        excluded_syntax_features=(
            "alternation",
            "branch-local-backreferences",
            "quantifiers",
        ),
        expected_workload_ids=(
            "module-sub-callable-nested-group-numbered-warm-bytes",
            "module-subn-callable-nested-group-numbered-warm-bytes",
            "pattern-sub-callable-nested-group-numbered-purged-bytes",
            "pattern-subn-callable-nested-group-numbered-purged-bytes",
            "module-sub-callable-nested-group-named-warm-bytes",
            "module-subn-callable-nested-group-named-warm-bytes",
            "pattern-sub-callable-nested-group-named-purged-bytes",
            "pattern-subn-callable-nested-group-named-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b))d",
            r"a(?P<outer>(?P<inner>b))d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abdabd"}),
        required_row_categories=(
            "nested-group",
            "replacement",
            "callable",
            "bytes",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-alternation",
        required_syntax_features=("alternation", "callable-replacement"),
        excluded_syntax_features=("branch-local-backreferences", "quantifiers"),
        expected_workload_ids=(
            "module-sub-callable-nested-group-alternation-cold-gap",
            "pattern-subn-callable-numbered-nested-group-alternation-c-branch-first-match-only-purged-str",
            "module-sub-callable-named-nested-group-alternation-c-branch-warm-str",
            "pattern-subn-callable-named-nested-group-alternation-b-branch-first-match-only-purged-str",
        ),
        expected_patterns=frozenset({
            r"a((b|c))d",
            r"a(?P<outer>(?P<inner>b|c))d",
        }),
        expected_operations=frozenset({"module.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abdacd", "acdabd", "acd"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="quantified-nested-group",
        required_syntax_features=(
            "callable-replacement",
            "quantifiers",
        ),
        excluded_syntax_features=("alternation", "branch-local-backreferences"),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-lower-bound-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-repeated-outer-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-purged-gap",
            "module-sub-callable-numbered-quantified-nested-group-lower-bound-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-repeated-outer-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((bc)+)d",
            r"a(?P<outer>(?P<inner>bc)+)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"zzabcdzz", "zzabcbcdabcbcdzz", "zzabcbcdzz"}),
        required_row_categories=(
            "nested-group",
            "replacement",
            "callable",
            "quantified",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="quantified-nested-alternation",
        required_syntax_features=("alternation", "callable-replacement", "quantifiers"),
        excluded_syntax_features=("branch-local-backreferences",),
        excluded_categories=("counted-repeat",),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-alternation-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-alternation-c-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-alternation-repeated-mixed-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-alternation-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-quantified-nested-group-alternation-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-alternation-c-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-alternation-repeated-mixed-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-alternation-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c)+)d",
            r"a(?P<outer>(?P<inner>b|c)+)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"zzabdzz", "zzabccdacbbdzz", "zzabccdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "quantified",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-broader-range-backtracking-heavy-callable-replacement",
        required_syntax_features=(
            "alternation",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
        ),
        excluded_syntax_features=("branch-local-backreferences", "conditionals"),
        required_categories=("broader-range", "backtracking-heavy"),
        expected_workload_ids=(
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a(((bc|b)c){1,4})d",
            r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({
            "abcd",
            "abccdabcbccd",
            "zzabcbccbccbcdzz",
            "zzabccbcdabccdzz",
        }),
        required_row_categories=(
            "grouped",
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
            "backtracking-heavy",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-broader-range-open-ended-backtracking-heavy-callable-replacement",
        required_syntax_features=(
            "alternation",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=(
            "branch-local-backreferences",
            "conditionals",
            "ranged-repeats",
        ),
        required_categories=("open-ended-repeat", "broader-range", "backtracking-heavy"),
        expected_workload_ids=(
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a(((bc|b)c){2,})d",
            r"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({
            "abcbcd",
            "abccbccdabcbcd",
            "zzabcbcbcbcdzz",
            "zzabcbcbcbcdabccbccdzz",
        }),
        required_row_categories=(
            "grouped",
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
            "backtracking-heavy",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="branch-local-backreference",
        required_syntax_features=("branch-local-backreferences", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        expected_workload_ids=(
            "module-sub-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-warm-str",
            "module-subn-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-nested-group-alternation-branch-local-backreference-c-branch-purged-str",
            "pattern-subn-callable-named-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-warm-bytes",
            "module-subn-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-nested-group-alternation-branch-local-backreference-c-branch-purged-bytes",
            "pattern-subn-callable-named-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c))\2d",
            r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abbdaccd", "accd", "accdabbd"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="quantified-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
        ),
        excluded_syntax_features=("counted-repeats", "ranged-repeats"),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c)+)\2d",
            r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abbbdaccd", "zzabccdzz", "zzaccdabbbdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
        ),
        excluded_syntax_features=("conditionals",),
        expected_workload_ids=(
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-str",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abcbccdabbd", "zzacccccdzz", "zzacccccdabbbdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
            "conditionals",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-str",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c){1,4})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abbbdaccd", "zzacccccdzz", "zzacccccdabbbdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "conditional",
            "group-exists",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        excluded_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
        ),
        expected_patterns=frozenset({
            r"a((b|c){1,})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abbbdaccd", "zzaccdzz", "zzaccdabcbccdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-open-ended-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "conditionals",
        ),
        excluded_syntax_features=("ranged-repeats",),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "conditional",
            "group-exists",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="quantified-nested-group",
        required_syntax_features=("quantifiers", "replacement-template"),
        excluded_syntax_features=("branch-local-backreferences",),
        expected_workload_ids=(
            "module-sub-template-numbered-quantified-nested-group-replacement-lower-bound-warm-str",
            "module-subn-template-numbered-quantified-nested-group-replacement-first-match-only-warm-str",
            "pattern-sub-template-named-quantified-nested-group-replacement-repeated-outer-purged-str",
            "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap",
        ),
        expected_patterns=frozenset({
            r"a((bc)+)d",
            r"a(?P<outer>(?P<inner>bc)+)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"zzabcdzz", "zzabcbcdabcbcdzz", "zzabcbcdzz"}),
        required_row_categories=(
            "nested-group",
            "replacement",
            "template",
            "quantified",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="broader-range-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
        ),
        excluded_syntax_features=("conditionals",),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abbbdaccd", "zzacccccdzz", "zzacccccdabbbdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        excluded_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
        ),
        expected_patterns=frozenset({
            r"a((b|c){1,})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abbbdaccd", "zzaccdzz", "zzaccdabcbccdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="broader-range-open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str",
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="broader-range-open-ended-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
            "conditionals",
        ),
        excluded_syntax_features=("ranged-repeats",),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str",
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns=frozenset({
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "conditional",
            "group-exists",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="open-ended-quantified-group-boundary",
        slice_id="broader-range-group-alternation",
        required_syntax_features=("module-search",),
        excluded_syntax_features=("conditionals", "named-groups"),
        required_categories=(
            "broader-range",
            "search",
            "module",
            "lower-bound",
            "bc-bc",
        ),
        excluded_categories=("backtracking-heavy",),
        expected_workload_ids=(
            "module-search-numbered-open-ended-group-broader-range-cold-gap",
            "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
        ),
        expected_patterns=frozenset({r"a(bc|de){2,}d"}),
        expected_operations=frozenset({"module.search"}),
        expected_haystacks=frozenset({"zzabcbcdzz"}),
        required_row_categories=(
            "grouped",
            "alternation",
            "quantifier",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
            "search",
            "module",
            "lower-bound",
            "bc-bc",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="open-ended-quantified-group-boundary",
        slice_id="broader-range-group-conditional",
        required_syntax_features=("module-search", "conditionals"),
        excluded_syntax_features=("named-groups",),
        required_categories=(
            "broader-range",
            "conditional",
            "search",
            "module",
            "present",
            "second-repetition",
            "bc-branch",
        ),
        excluded_categories=("backtracking-heavy",),
        expected_workload_ids=(
            "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap",
            "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
        ),
        expected_patterns=frozenset({r"a((bc|de){2,})?(?(1)d|e)"}),
        expected_operations=frozenset({"module.search"}),
        expected_haystacks=frozenset({"zzabcbcdzz"}),
        required_row_categories=(
            "grouped",
            "alternation",
            "quantifier",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
            "conditional",
            "optional-group",
            "search",
            "module",
            "present",
            "second-repetition",
            "bc-branch",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="open-ended-quantified-group-boundary",
        slice_id="broader-range-group-backtracking-heavy",
        required_syntax_features=("pattern-fullmatch", "named-groups"),
        excluded_syntax_features=("conditionals",),
        required_categories=(
            "broader-range",
            "backtracking-heavy",
            "pattern",
            "fullmatch",
            "named-group",
            "fourth-repetition",
            "b-branch",
        ),
        expected_workload_ids=(
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
        ),
        expected_patterns=frozenset({r"a(?P<word>(bc|b)c){2,}d"}),
        expected_operations=frozenset({"pattern.fullmatch"}),
        expected_haystacks=frozenset({"abcbcbcbcd"}),
        required_row_categories=(
            "grouped",
            "alternation",
            "quantifier",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
            "backtracking-heavy",
            "pattern",
            "fullmatch",
            "named-group",
            "fourth-repetition",
            "b-branch",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="grouped-alternation-callable-replacement-boundary",
        slice_id="former-gap-callable-replacement-rows",
        required_syntax_features=("callable-replacement",),
        required_id_suffix="gap",
        expected_workload_ids=(
            "module-sub-callable-nested-grouped-alternation-cold-gap",
            "pattern-subn-callable-named-nested-grouped-alternation-purged-gap",
        ),
        expected_patterns=frozenset({
            r"a((b|c))d",
            r"a(?P<outer>(b|c))d",
        }),
        expected_operations=frozenset({"module.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abdacd", "acdabd"}),
        required_row_categories=(
            "alternation",
            "replacement",
            "callable",
            "gap",
        ),
    ),
    SourceTreeCombinedSliceExpectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="quantified-alternation-heavy-constant-replacement-rows",
        required_syntax_features=("conditionals", "alternation", "quantifiers"),
        required_categories=("alternation-heavy", "replacement", "quantified"),
        expected_workload_ids=(
            "module-sub-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "module-subn-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "pattern-sub-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
            "pattern-subn-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
            "module-sub-named-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "module-subn-named-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "pattern-sub-named-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
            "pattern-subn-named-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
        ),
        expected_patterns=frozenset({
            r"a(b)?c(?(1)(de|df)|(eg|eh)){2}",
            r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({
            "zzabcdedezz",
            "zzabcdfdfzz",
            "zzacegegzz",
            "zzacehehzz",
        }),
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "alternation-heavy",
            "quantified",
            "replacement",
        ),
    ),
)

_COLLECTION_REPLACEMENT_SPLIT_OPERATIONS = frozenset(
    {"module.split", "pattern.split"}
)
_COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS = frozenset(
    {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
)


def _collection_replacement_keyword_parameter_name(
    workload: Any,
) -> str | None:
    if workload.operation in {"module.split", "pattern.split"}:
        return "maxsplit"
    if workload.operation in {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}:
        return "count"
    return None


def _collection_replacement_positional_keyword_field(
    workload: Any,
) -> str | None:
    if workload.operation.startswith("module."):
        expected_keyword_field = (
            benchmarks._expected_duplicate_module_helper_keyword_field(workload)
            or benchmarks._expected_positional_module_helper_keyword_field(workload)
        )
    elif workload.operation.startswith("pattern."):
        expected_keyword_field = (
            benchmarks._expected_pattern_helper_positional_keyword_field(workload)
        )
    else:
        expected_keyword_field = None
    if expected_keyword_field is None:
        return None
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if expected_keyword_field != keyword_parameter:
        return None
    return expected_keyword_field


def _is_collection_replacement_keyword_workload(workload: Any) -> bool:
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if keyword_parameter is None or not workload.kwargs:
        return False
    keyword_names = tuple(workload.kwargs)
    if len(keyword_names) != 1:
        return False
    if keyword_names[0] == keyword_parameter:
        return True
    if _collection_replacement_positional_keyword_field(workload) is not None:
        return True
    expected_exception = workload.expected_exception
    if expected_exception is None or expected_exception.get("type") != "TypeError":
        return False
    keyword_name = keyword_names[0]
    message_substring = expected_exception.get("message_substring")
    if not isinstance(message_substring, str):
        return False
    if f"unexpected keyword argument '{keyword_name}'" in message_substring:
        return True
    if workload.operation.startswith("pattern."):
        helper_name = workload.operation.removeprefix("pattern.")
        return (
            message_substring
            == f"'{keyword_name}' is an invalid keyword argument for {helper_name}()"
        )
    return False


def _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
    monkeypatch: pytest.MonkeyPatch,
    workload: benchmarks.Workload,
    *,
    expected_result: object | None,
    expected_exception_message: str | None = None,
    expected_field_names: list[str] | tuple[str, ...],
) -> None:
    observed_field_names = benchmark_test_support._record_numeric_materialization_fields(
        monkeypatch
    )

    re.purge()
    try:
        callback = benchmarks.build_callable(re, "re", workload)
        assert observed_field_names == []

        if expected_exception_message is None:
            assert callback() == expected_result
            assert callback() == expected_result
        else:
            with pytest.raises(TypeError, match=re.escape(expected_exception_message)):
                callback()
            with pytest.raises(TypeError, match=re.escape(expected_exception_message)):
                callback()

        assert observed_field_names == list(expected_field_names) * 2
    finally:
        re.purge()


def _is_collection_replacement_compiled_pattern_module_helper_keyword_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and workload.use_compiled_pattern
        and workload.operation in {"module.split", "module.sub", "module.subn"}
        and workload.expected_exception is None
        and getattr(workload, "haystack_text_model", None) is None
    )


def _is_collection_replacement_compiled_pattern_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and workload.use_compiled_pattern
        and workload.operation in {"module.split", "module.sub", "module.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
    )


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleHelperKeywordContractSpec:
    contract_filename: str
    expected_source_workload_ids: tuple[str, ...]
    manifest_timed_samples: int
    preserve_expected_exception: bool
    materializes_positional_keyword_field: bool
    notes: tuple[str, ...] = ()
    precompile_anchor_ids: tuple[str, ...] = ()

    def expected_materialized_field_names(
        self,
        source_workload: benchmarks.Workload,
    ) -> tuple[str, ...]:
        if self.materializes_positional_keyword_field:
            field_names: list[str] = []
            positional_keyword_field = _collection_replacement_positional_keyword_field(
                source_workload
            )
            if positional_keyword_field is not None:
                field_names.append(positional_keyword_field)
            field_names.extend(f"kwargs.{name}" for name in source_workload.kwargs)
            return tuple(field_names)

        keyword_parameter = _collection_replacement_keyword_parameter_name(
            source_workload
        )
        if keyword_parameter is None:
            raise AssertionError(
                "unexpected compiled-pattern module helper keyword workload "
                f"{source_workload.workload_id!r}"
            )
        return (f"kwargs.{keyword_parameter}",)

    def contract_builder_spec(self) -> object:
        excluded_fields = (
            benchmark_test_support.COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS
        )
        if not self.preserve_expected_exception:
            excluded_fields = excluded_fields | {"expected_exception"}
        return _SourceTreeContractBuilderSpec(
            manifest_id="collection-replacement-boundary",
            excluded_fields=excluded_fields,
            manifest_timed_samples=self.manifest_timed_samples,
            timing_scope="module-helper-call",
            notes=self.notes,
        )


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleHelperKeywordContractSurface:
    case_id: str
    spec: _CompiledPatternModuleHelperKeywordContractSpec
    source_workloads_value: tuple[benchmarks.Workload, ...]
    precompile_source_workloads_value: tuple[benchmarks.Workload, ...] | None = None

    def source_workloads(self) -> tuple[benchmarks.Workload, ...]:
        return self.source_workloads_value

    def precompile_source_workloads(self) -> tuple[benchmarks.Workload, ...]:
        return self.precompile_source_workloads_value or self.source_workloads_value

    def expected_build_calls(
        self,
        source_workload: benchmarks.Workload,
    ) -> list[tuple[object, ...]]:
        return benchmark_test_support.compiled_pattern_contract_expected_build_calls(
            source_workload,
            label="module helper keyword",
        )

    def expected_callback_call(
        self,
        source_workload: benchmarks.Workload,
    ) -> tuple[object, ...]:
        if source_workload.operation == "module.split":
            return (
                source_workload.operation,
                source_workload.haystack_payload(),
                source_workload.maxsplit,
                source_workload.flags,
                source_workload.kwargs,
            )
        if source_workload.operation in {"module.sub", "module.subn"}:
            return (
                source_workload.operation,
                source_workload.replacement_payload(),
                source_workload.haystack_payload(),
                source_workload.count,
                source_workload.flags,
                source_workload.kwargs,
            )
        raise AssertionError(
            "unexpected compiled-pattern module helper keyword workload operation "
            f"{source_workload.operation!r}"
        )

    def expected_callback_result(self, source_workload: benchmarks.Workload) -> object:
        if source_workload.operation == "module.subn":
            return ("module-result", 0)
        return "module-result"

    def run_cpython_helper_workload(
        self,
        workload: benchmarks.Workload,
    ) -> object:
        compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
        helper_name = workload.operation.removeprefix("module.")
        helper = getattr(re, helper_name)
        kwargs = dict(workload.kwargs)
        positional_keyword_field = _collection_replacement_positional_keyword_field(
            workload
        )

        if workload.operation == "module.split":
            args: list[object] = [compiled_pattern, workload.haystack_payload()]
            if positional_keyword_field == "maxsplit":
                args.append(workload.maxsplit)
            return helper(*args, **kwargs)

        if workload.operation in {"module.sub", "module.subn"}:
            args = [
                compiled_pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
            ]
            if positional_keyword_field == "count":
                args.append(workload.count)
            return helper(*args, **kwargs)

        raise AssertionError(
            "unexpected compiled-pattern module helper keyword workload operation "
            f"{workload.operation!r}"
        )

    def assert_outcome(
        self,
        source_workload: benchmarks.Workload,
        workload: benchmarks.Workload,
        round_tripped: benchmarks.Workload,
    ) -> None:
        if self.case_id == "success":
            benchmark_test_support.assert_benchmark_workload_matches_expected_result(
                round_tripped,
                benchmark_test_support.run_benchmark_workload_with_cpython(
                    source_workload
                ),
            )
            return

        if self.case_id == "keyword-error":
            with pytest.raises(TypeError) as expected_error:
                self.run_cpython_helper_workload(workload)
            with pytest.raises(TypeError) as observed_error:
                benchmark_test_support.run_benchmark_workload_with_cpython(
                    round_tripped
                )
            assert str(observed_error.value) == str(expected_error.value)
            return

        raise AssertionError(
            "unexpected compiled-pattern module helper keyword contract surface "
            f"{self.case_id!r}"
        )

    def assert_payload_round_trip(
        self,
        source_workload: benchmarks.Workload,
        payload: dict[str, object],
        round_tripped: benchmarks.Workload,
    ) -> None:
        expected_text_type = str if source_workload.text_model == "str" else bytes
        expected_exception = (
            source_workload.expected_exception
            if self.spec.preserve_expected_exception
            else None
        )
        assert payload["use_compiled_pattern"] is True
        assert round_tripped.use_compiled_pattern is True
        assert payload["count"] == source_workload.count
        assert round_tripped.count == source_workload.count
        assert payload["maxsplit"] == source_workload.maxsplit
        assert round_tripped.maxsplit == source_workload.maxsplit
        assert payload["kwargs"] == source_workload.kwargs
        assert round_tripped.kwargs == source_workload.kwargs
        assert payload.get("expected_exception") == expected_exception
        assert round_tripped.expected_exception == expected_exception
        assert payload.get("haystack_text_model") is None
        assert round_tripped.haystack_text_model is None
        assert round_tripped.text_model == source_workload.text_model
        assert isinstance(round_tripped.pattern_payload(), expected_text_type)
        assert isinstance(round_tripped.haystack_payload(), expected_text_type)
        if source_workload.replacement is not None:
            assert isinstance(
                round_tripped.replacement_payload(),
                expected_text_type,
            )
        for name, value in source_workload.kwargs.items():
            if type(value) is bool:
                assert type(payload["kwargs"][name]) is bool
                assert type(round_tripped.kwargs[name]) is bool


_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC = (
    _CompiledPatternModuleHelperKeywordContractSpec(
        contract_filename=(
            "python_benchmark_compiled_pattern_collection_replacement_keyword_contract.py"
        ),
        expected_source_workload_ids=(
            "module-split-maxsplit-keyword-purged-str-compiled-pattern",
            "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern",
            "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern",
            "module-sub-count-keyword-warm-str-compiled-pattern",
            "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern",
            "module-sub-count-bool-keyword-warm-str-compiled-pattern",
            "module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
            "module-subn-count-keyword-purged-bytes-compiled-pattern",
            "module-subn-count-indexlike-keyword-purged-str-compiled-pattern",
            "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
            "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
        ),
        manifest_timed_samples=2,
        preserve_expected_exception=False,
        materializes_positional_keyword_field=False,
        notes=(
            "Ensures benchmark manifests keep compiled-pattern-first-argument "
            "collection/replacement keyword carriers unresolved until helper "
            "invocation.",
        ),
        precompile_anchor_ids=(
            "module-split-maxsplit-keyword-purged-str-compiled-pattern",
            "module-sub-count-keyword-warm-str-compiled-pattern",
            "module-subn-count-keyword-purged-bytes-compiled-pattern",
        ),
    )
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC = (
    _CompiledPatternModuleHelperKeywordContractSpec(
        contract_filename=(
            "python_benchmark_compiled_pattern_collection_replacement_keyword_error_contract.py"
        ),
        expected_source_workload_ids=(
            "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern",
            "module-split-unexpected-keyword-purged-bytes-compiled-pattern",
            "module-sub-duplicate-count-keyword-warm-str-compiled-pattern",
            "module-sub-unexpected-keyword-purged-str-compiled-pattern",
            "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern",
            "module-sub-count-alias-keyword-purged-str-compiled-pattern",
            "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern",
            "module-subn-unexpected-keyword-purged-bytes-compiled-pattern",
            "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern",
            "module-subn-count-alias-keyword-purged-bytes-compiled-pattern",
        ),
        manifest_timed_samples=1,
        preserve_expected_exception=True,
        materializes_positional_keyword_field=True,
    )
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS = (
    benchmark_test_support.selected_manifest_workloads(
        benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=(
            _is_collection_replacement_compiled_pattern_module_helper_keyword_workload
        ),
    )
)
if (
    tuple(
        workload.workload_id
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
    )
    != _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.expected_source_workload_ids
):
    raise AssertionError(
        "compiled-pattern module-helper keyword contract source workloads drifted "
        "from the live source workload surface"
    )

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS = tuple(
    workload
    for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
    if workload.workload_id
    in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.precompile_anchor_ids
)
if (
    tuple(
        workload.workload_id
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS
    )
    != _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.precompile_anchor_ids
):
    raise AssertionError(
        "compiled-pattern module-helper keyword precompile anchors drifted "
        "from the live source workload surface"
    )

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS = (
    benchmark_test_support.selected_manifest_workloads(
        benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=(
            _is_collection_replacement_compiled_pattern_keyword_error_workload
        ),
    )
)
if (
    tuple(
        workload.workload_id
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
    )
    != _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.expected_source_workload_ids
):
    raise AssertionError(
        "compiled-pattern module-helper keyword-error source workloads drifted "
        "from the live source workload surface"
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES = (
    _CompiledPatternModuleHelperKeywordContractSurface(
        case_id="success",
        spec=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC,
        source_workloads_value=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS,
        precompile_source_workloads_value=(
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS
        ),
    ),
    _CompiledPatternModuleHelperKeywordContractSurface(
        case_id="keyword-error",
        spec=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC,
        source_workloads_value=(
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        ),
    ),
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS = tuple(
    pytest.param(surface, id=surface.case_id)
    for surface in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS = tuple(
    pytest.param(
        surface,
        source_workload,
        id=f"{surface.case_id}-{source_workload.workload_id}",
    )
    for surface in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
    for source_workload in surface.source_workloads()
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS = tuple(
    pytest.param(
        surface,
        source_workload,
        id=f"{surface.case_id}-{source_workload.workload_id}",
    )
    for surface in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
    for source_workload in surface.precompile_source_workloads()
)


def _collection_replacement_pattern_collection_correctness_case_signature(
    case: Any,
    *,
    case_ids: tuple[str, ...],
    expected_operation: str,
) -> tuple[Any, ...] | None:
    if case.case_id not in case_ids:
        return None
    if (
        case.operation != "pattern_call"
        or case.kwargs
        or case.helper != expected_operation.removeprefix("pattern.")
    ):
        return None
    return (
        expected_operation,
        case_pattern(case),
        benchmark_test_support.freeze_signature_value(list(case.args)),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def _is_collection_replacement_pattern_collection_workload(
    workload: Any,
    *,
    workload_ids: tuple[str, ...],
    expected_operation: str,
    requires_window_bounds: bool,
) -> bool:
    return (
        workload.workload_id in workload_ids
        and workload.operation == expected_operation
        and workload.pattern == "abc"
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
        and workload.text_model in {"str", "bytes"}
        and not workload.kwargs
        and (workload.pos is not None) is requires_window_bounds
        and (workload.endpos is not None) is requires_window_bounds
    )


def _collection_replacement_pattern_collection_workload_signature(
    workload: Any,
    *,
    workload_ids: tuple[str, ...],
    expected_operation: str,
    requires_window_bounds: bool,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_pattern_collection_workload(
        workload,
        workload_ids=workload_ids,
        expected_operation=expected_operation,
        requires_window_bounds=requires_window_bounds,
    ):
        raise AssertionError(
            "unexpected collection/replacement bounded "
            f"{expected_operation} workload {workload.workload_id!r}"
        )
    if requires_window_bounds:
        args: list[object] = [workload.haystack_payload()]
        if workload.pos is not None or workload.endpos is not None:
            args.append(0 if workload.pos is None else workload.pos)
        if workload.endpos is not None:
            args.append(workload.endpos)
    else:
        args = [workload.haystack_payload()]
        if workload.maxsplit is not None and not (
            type(workload.maxsplit) is int and workload.maxsplit == 0
        ):
            args.append(workload.maxsplit_argument())
    return (
        expected_operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(list(args)),
        (),
        workload.flags,
        workload.text_model,
    )


@dataclass(frozen=True, slots=True)
class _CollectionReplacementCombinedSliceExpectation:
    manifest_id: str
    slice_id: str
    required_syntax_features: tuple[str, ...] = ()
    excluded_syntax_features: tuple[str, ...] = ()
    required_categories: tuple[str, ...] = ()
    excluded_categories: tuple[str, ...] = ()
    required_id_suffix: str | None = None
    expected_workload_ids: tuple[str, ...] = ()
    expected_patterns: frozenset[str] = frozenset()
    expected_operations: frozenset[str] = frozenset()
    expected_haystacks: frozenset[str] = frozenset()
    required_row_categories: tuple[str, ...] = ()
    expected_status: str = "measured"

_COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_CASE_PAIRS = (
    ("pattern-findall-bounded-warm-str", "pattern-findall-str-bounded"),
    (
        "pattern-findall-bounded-no-match-warm-str",
        "pattern-findall-str-bounded-no-match",
    ),
    ("pattern-findall-bounded-purged-bytes", "pattern-findall-bytes-bounded"),
)
_COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_IDS = tuple(
    workload_id
    for workload_id, _ in _COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_FINDALL_CASE_IDS = tuple(
    case_id
    for _, case_id in _COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_CASE_PAIRS = (
    ("pattern-finditer-bounded-warm-str", "pattern-finditer-str-bounded"),
    (
        "pattern-finditer-bounded-no-match-warm-str",
        "pattern-finditer-str-bounded-no-match",
    ),
    (
        "pattern-finditer-bounded-purged-bytes",
        "pattern-finditer-bytes-bounded",
    ),
)
_COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_IDS = tuple(
    workload_id
    for workload_id, _ in _COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_FINDITER_CASE_IDS = tuple(
    case_id
    for _, case_id in _COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_CASE_PAIRS = (
    ("pattern-split-no-match-warm-str", "pattern-split-str-no-match"),
    ("pattern-split-repeated-warm-str", "pattern-split-str-repeated"),
    ("pattern-split-maxsplit-purged-bytes", "pattern-split-bytes-maxsplit"),
)
_COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_IDS = tuple(
    workload_id
    for workload_id, _ in _COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_SPLIT_CASE_IDS = tuple(
    case_id
    for _, case_id in _COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_CASE_PAIRS
)

_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS = (
    ("pattern-sub-no-match-warm-str", "pattern-sub-str-no-match"),
    ("pattern-sub-single-match-warm-str", "pattern-sub-str-single-match"),
    ("pattern-sub-repeated-warm-str", "pattern-sub-str-repeated"),
    ("pattern-sub-count-one-warm-str", "pattern-sub-str-count-one"),
    ("pattern-sub-negative-count-warm-str", "pattern-sub-str-negative-count"),
    ("pattern-sub-bytes-no-match-purged-bytes", "pattern-sub-bytes-no-match"),
    (
        "pattern-sub-bytes-single-match-purged-bytes",
        "pattern-sub-bytes-single-match",
    ),
    (
        "pattern-sub-bytes-repeated-purged-bytes",
        "pattern-sub-bytes-repeated",
    ),
    (
        "pattern-sub-bytes-count-one-purged-bytes",
        "pattern-sub-bytes-count-one",
    ),
    (
        "pattern-sub-bytes-negative-count-purged-bytes",
        "pattern-sub-bytes-negative-count",
    ),
    ("pattern-subn-count-warm-str", "pattern-subn-str-count"),
    ("pattern-subn-single-match-warm-str", "pattern-subn-str-single-match"),
    ("pattern-subn-repeated-warm-str", "pattern-subn-str-repeated"),
    ("pattern-subn-negative-count-warm-str", "pattern-subn-str-negative-count"),
    ("pattern-subn-no-match-warm-str", "pattern-subn-str-no-match"),
    ("pattern-subn-bytes-count-purged-bytes", "pattern-subn-bytes-count"),
    (
        "pattern-subn-bytes-single-match-purged-bytes",
        "pattern-subn-bytes-single-match",
    ),
    (
        "pattern-subn-bytes-repeated-purged-bytes",
        "pattern-subn-bytes-repeated",
    ),
    (
        "pattern-subn-bytes-negative-count-purged-bytes",
        "pattern-subn-bytes-negative-count",
    ),
    (
        "pattern-subn-bytes-no-match-purged-bytes",
        "pattern-subn-bytes-no-match",
    ),
)
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_IDS = tuple(
    workload_id
    for workload_id, _ in _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_CASE_IDS = tuple(
    case_id
    for _, case_id in _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_OPERATIONS = (
    "pattern.sub",
    "pattern.subn",
)
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_TEXT_MODELS = ("str", "bytes")
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_EXPECTED_OPERATION = (
    "pattern_call"
)
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_OPERATION_PREFIX = "pattern"
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_ARGS_OFFSET = 0

_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS = (
    ("module-sub-str-no-match-purged-str", "module-sub-str-no-match"),
    ("module-sub-str-single-match-purged-str", "module-sub-str-single-match"),
    ("module-sub-str-repeated-purged-str", "module-sub-str-repeated"),
    ("module-sub-str-count-one-purged-str", "module-sub-str-count-one"),
    ("module-sub-str-negative-count-purged-str", "module-sub-str-negative-count"),
    ("module-subn-str-count-purged-str", "module-subn-str-count"),
    (
        "module-subn-str-single-match-purged-str",
        "module-subn-str-single-match",
    ),
    ("module-subn-str-repeated-purged-str", "module-subn-str-repeated"),
    (
        "module-subn-str-negative-count-purged-str",
        "module-subn-str-negative-count",
    ),
    ("module-subn-str-no-match-purged-str", "module-subn-str-no-match"),
    ("module-sub-bytes-no-match-purged-bytes", "module-sub-bytes-no-match"),
    (
        "module-sub-bytes-single-match-purged-bytes",
        "module-sub-bytes-single-match",
    ),
    ("module-sub-bytes-repeated-purged-bytes", "module-sub-bytes-repeated"),
    ("module-sub-bytes-count-one-purged-bytes", "module-sub-bytes-count-one"),
    ("module-subn-bytes-count-purged-bytes", "module-subn-bytes-count"),
    (
        "module-subn-bytes-single-match-purged-bytes",
        "module-subn-bytes-single-match",
    ),
    ("module-subn-bytes-repeated-purged-bytes", "module-subn-bytes-repeated"),
    ("module-subn-bytes-no-match-purged-bytes", "module-subn-bytes-no-match"),
)
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_IDS = tuple(
    workload_id
    for workload_id, _ in _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_CASE_IDS = tuple(
    case_id
    for _, case_id in _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_OPERATIONS = (
    "module.sub",
    "module.subn",
)
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_TEXT_MODELS = ("str", "bytes")
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_EXPECTED_OPERATION = "module_call"
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_OPERATION_PREFIX = "module"
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_ARGS_OFFSET = 1
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_ALLOWED_COUNTS = (-1, 0, 1)


def _collection_replacement_standard_benchmark_definitions() -> tuple[object, ...]:
    return (
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-module-positional-indexlike",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-split-maxsplit-indexlike-positional-purged-bytes": (
                        "workflow-module-split-maxsplit-indexlike-positional-bytes",
                    ),
                    "module-sub-count-indexlike-positional-warm-str": (
                        "workflow-module-sub-count-indexlike-positional-str",
                    ),
                    "module-subn-count-indexlike-positional-purged-bytes": (
                        "workflow-module-subn-count-indexlike-positional-bytes",
                    ),
                    "pattern-split-maxsplit-indexlike-positional-warm-str": (
                        "workflow-pattern-split-str-maxsplit-indexlike-positional",
                    ),
                    "pattern-sub-count-indexlike-positional-purged-bytes": (
                        "workflow-pattern-sub-count-indexlike-positional-bytes",
                    ),
                    "pattern-subn-count-indexlike-positional-warm-str": (
                        "workflow-pattern-subn-count-indexlike-positional-str",
                    ),
                },
            ),
            include_workload=_is_collection_replacement_positional_indexlike_workload,
            correctness_case_signature=(
                _module_workflow_positional_indexlike_correctness_case_signature
            ),
            workload_signature=_collection_replacement_positional_indexlike_workload_signature,
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-keyword",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-split-maxsplit-keyword-purged-bytes": (
                        "workflow-module-split-maxsplit-keyword-bytes",
                    ),
                    "module-split-maxsplit-bool-keyword-purged-bytes": (
                        "workflow-module-split-maxsplit-bool-false-bytes",
                    ),
                    "module-split-maxsplit-indexlike-keyword-purged-bytes": (
                        "workflow-module-split-maxsplit-indexlike-bytes",
                    ),
                    "module-split-maxsplit-keyword-purged-str-compiled-pattern": (
                        "workflow-module-split-maxsplit-keyword-str-compiled-pattern",
                    ),
                    "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern",
                    ),
                    "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-split-maxsplit-bool-false-bytes-compiled-pattern",
                    ),
                    "module-split-duplicate-maxsplit-keyword-purged-str": (
                        "workflow-module-split-duplicate-maxsplit-keyword",
                    ),
                    "module-split-unexpected-keyword-purged-str": (
                        "workflow-module-split-unexpected-keyword",
                    ),
                    "module-split-unexpected-keyword-purged-bytes": (
                        "workflow-module-split-unexpected-keyword-bytes",
                    ),
                    "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern": (
                        "workflow-module-split-duplicate-maxsplit-keyword-str-compiled-pattern",
                    ),
                    "module-split-unexpected-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-split-unexpected-keyword-bytes-compiled-pattern",
                    ),
                    "module-sub-count-keyword-warm-str": (
                        "workflow-module-sub-count-keyword-str",
                    ),
                    "module-sub-count-bool-keyword-warm-str": (
                        "workflow-module-sub-count-bool-true-str",
                    ),
                    "module-sub-count-bool-false-keyword-warm-str": (
                        "workflow-module-sub-count-bool-false-str",
                    ),
                    "module-sub-count-indexlike-keyword-warm-str": (
                        "workflow-module-sub-count-indexlike-str",
                    ),
                    "module-sub-count-keyword-warm-str-compiled-pattern": (
                        "workflow-module-sub-count-keyword-str-compiled-pattern",
                    ),
                    "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern": (
                        "workflow-module-sub-count-indexlike-bytes-compiled-pattern",
                    ),
                    "module-sub-count-bool-keyword-warm-str-compiled-pattern": (
                        "workflow-module-sub-count-bool-true-str-compiled-pattern",
                    ),
                    "module-sub-count-bool-false-keyword-warm-str-compiled-pattern": (
                        "workflow-module-sub-count-bool-false-str-compiled-pattern",
                    ),
                    "module-sub-duplicate-count-keyword-warm-str": (
                        "workflow-module-sub-duplicate-count-keyword",
                    ),
                    "module-sub-unexpected-keyword-purged-str": (
                        "workflow-module-sub-unexpected-keyword",
                    ),
                    "module-sub-unexpected-keyword-after-positional-count-purged-str": (
                        "workflow-module-sub-unexpected-keyword-after-positional-count",
                    ),
                    "module-sub-count-alias-keyword-purged-str": (
                        "workflow-module-sub-count-alias-keyword",
                    ),
                    "module-sub-duplicate-count-keyword-warm-str-compiled-pattern": (
                        "workflow-module-sub-duplicate-count-keyword-str-compiled-pattern",
                    ),
                    "module-sub-unexpected-keyword-purged-str-compiled-pattern": (
                        "workflow-module-sub-unexpected-keyword-str-compiled-pattern",
                    ),
                    "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern": (
                        "workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern",
                    ),
                    "module-sub-count-alias-keyword-purged-str-compiled-pattern": (
                        "workflow-module-sub-count-alias-keyword-str-compiled-pattern",
                    ),
                    "module-subn-count-keyword-purged-bytes": (
                        "workflow-module-subn-count-keyword-bytes",
                    ),
                    "module-subn-count-bool-keyword-purged-bytes": (
                        "workflow-module-subn-count-bool-false-bytes",
                    ),
                    "module-subn-count-bool-true-keyword-purged-bytes": (
                        "workflow-module-subn-count-bool-true-bytes",
                    ),
                    "module-subn-count-indexlike-keyword-purged-bytes": (
                        "workflow-module-subn-count-indexlike-bytes",
                    ),
                    "module-subn-duplicate-count-keyword-warm-bytes": (
                        "workflow-module-subn-duplicate-count-keyword-bytes",
                    ),
                    "module-subn-unexpected-keyword-purged-bytes": (
                        "workflow-module-subn-unexpected-keyword-bytes",
                    ),
                    "module-subn-unexpected-keyword-after-positional-count-purged-bytes": (
                        "workflow-module-subn-unexpected-keyword-after-positional-count-bytes",
                    ),
                    "module-subn-count-alias-keyword-purged-bytes": (
                        "workflow-module-subn-count-alias-keyword-bytes",
                    ),
                    "module-subn-count-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-count-keyword-bytes-compiled-pattern",
                    ),
                    "module-subn-count-indexlike-keyword-purged-str-compiled-pattern": (
                        "workflow-module-subn-count-indexlike-str-compiled-pattern",
                    ),
                    "module-subn-count-bool-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-count-bool-false-bytes-compiled-pattern",
                    ),
                    "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-count-bool-true-bytes-compiled-pattern",
                    ),
                    "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern": (
                        "workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern",
                    ),
                    "module-subn-unexpected-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-unexpected-keyword-bytes-compiled-pattern",
                    ),
                    "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern",
                    ),
                    "module-subn-count-alias-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-count-alias-keyword-bytes-compiled-pattern",
                    ),
                    "pattern-split-maxsplit-keyword-warm-str": (
                        "workflow-pattern-split-str-maxsplit-keyword",
                    ),
                    "pattern-split-maxsplit-bool-keyword-warm-str": (
                        "workflow-pattern-split-str-maxsplit-bool-true",
                    ),
                    "pattern-split-maxsplit-indexlike-keyword-warm-str": (
                        "workflow-pattern-split-str-maxsplit-indexlike",
                    ),
                    "pattern-split-duplicate-maxsplit-keyword-warm-str": (
                        "workflow-pattern-split-duplicate-maxsplit-keyword-str",
                    ),
                    "pattern-split-unexpected-keyword-warm-bytes": (
                        "workflow-pattern-split-unexpected-keyword-bytes",
                    ),
                    "pattern-sub-count-keyword-purged-bytes": (
                        "workflow-pattern-sub-count-keyword-bytes",
                    ),
                    "pattern-sub-count-bool-keyword-purged-bytes": (
                        "workflow-pattern-sub-count-bool-false-bytes",
                    ),
                    "pattern-sub-count-bool-true-keyword-purged-bytes": (
                        "workflow-pattern-sub-count-bool-true-bytes",
                    ),
                    "pattern-sub-count-indexlike-keyword-purged-bytes": (
                        "workflow-pattern-sub-count-indexlike-bytes",
                    ),
                    "pattern-sub-duplicate-count-keyword-warm-str": (
                        "workflow-pattern-sub-duplicate-count-keyword-str",
                    ),
                    "pattern-sub-unexpected-keyword-warm-str": (
                        "workflow-pattern-sub-unexpected-keyword-str",
                    ),
                    "pattern-sub-unexpected-keyword-after-positional-count-warm-str": (
                        "workflow-pattern-sub-unexpected-keyword-after-positional-count-str",
                    ),
                    "pattern-sub-count-alias-keyword-warm-str": (
                        "workflow-pattern-sub-count-alias-keyword-str",
                    ),
                    "pattern-subn-count-keyword-warm-str": (
                        "workflow-pattern-subn-count-keyword-str",
                    ),
                    "pattern-subn-count-bool-keyword-warm-str": (
                        "workflow-pattern-subn-count-bool-true-str",
                    ),
                    "pattern-subn-count-bool-false-keyword-warm-str": (
                        "workflow-pattern-subn-count-bool-false-str",
                    ),
                    "pattern-subn-count-indexlike-keyword-warm-str": (
                        "workflow-pattern-subn-count-indexlike-str",
                    ),
                    "pattern-subn-duplicate-count-keyword-warm-bytes": (
                        "workflow-pattern-subn-duplicate-count-keyword-bytes",
                    ),
                    "pattern-subn-unexpected-keyword-warm-bytes": (
                        "workflow-pattern-subn-unexpected-keyword-bytes",
                    ),
                    "pattern-subn-unexpected-keyword-after-positional-count-warm-bytes": (
                        "workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes",
                    ),
                    "pattern-subn-count-alias-keyword-warm-bytes": (
                        "workflow-pattern-subn-count-alias-keyword-bytes",
                    ),
                },
            ),
            include_workload=_is_collection_replacement_keyword_workload,
            correctness_case_signature=(
                _collection_replacement_keyword_correctness_case_signature
            ),
            workload_signature=_collection_replacement_keyword_workload_signature,
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-compiled-pattern-literal-success",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-split-literal-warm-str-compiled-pattern": (
                        "workflow-module-split-str-compiled-pattern",
                    ),
                    "module-findall-literal-purged-bytes-compiled-pattern": (
                        "workflow-module-findall-bytes-compiled-pattern",
                    ),
                    "module-finditer-literal-warm-str-compiled-pattern": (
                        "workflow-module-finditer-str-compiled-pattern",
                    ),
                    "module-sub-literal-warm-str-compiled-pattern": (
                        "workflow-module-sub-str-compiled-pattern",
                    ),
                    "module-subn-literal-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-bytes-compiled-pattern",
                    ),
                },
            ),
            include_workload=(
                _is_collection_replacement_compiled_pattern_success_workload
            ),
            correctness_case_signature=(
                _collection_replacement_compiled_pattern_success_correctness_case_signature
            ),
            workload_signature=(
                _collection_replacement_compiled_pattern_success_workload_signature
            ),
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-compiled-pattern-wrong-text-model",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-split-on-bytes-string-purged-str-compiled-pattern": (
                        "workflow-module-split-str-compiled-pattern-on-bytes-string",
                    ),
                    "module-findall-on-str-string-purged-bytes-compiled-pattern": (
                        "workflow-module-findall-bytes-compiled-pattern-on-str-string",
                    ),
                    "module-finditer-on-bytes-string-warm-str-compiled-pattern": (
                        "workflow-module-finditer-str-compiled-pattern-on-bytes-string",
                    ),
                    "module-sub-on-bytes-string-warm-str-compiled-pattern": (
                        "workflow-module-sub-str-compiled-pattern-on-bytes-string",
                    ),
                    "module-subn-on-str-string-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-bytes-compiled-pattern-on-str-string",
                    ),
                },
            ),
            include_workload=_is_collection_replacement_wrong_text_model_workload,
            correctness_case_signature=(
                _collection_replacement_wrong_text_model_correctness_case_signature
            ),
            workload_signature=_collection_replacement_wrong_text_model_workload_signature,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="pattern-helper-collection-replacement-wrong-text-model",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "pattern-split-on-bytes-string-warm-str": (
                        "workflow-pattern-split-str-pattern-on-bytes-string",
                    ),
                    "pattern-sub-on-bytes-string-warm-str": (
                        "workflow-pattern-sub-str-pattern-on-bytes-string",
                    ),
                    "pattern-subn-on-str-string-purged-bytes": (
                        "workflow-pattern-subn-bytes-pattern-on-str-string",
                    ),
                },
            ),
            include_workload=_is_collection_replacement_pattern_wrong_text_model_workload,
            correctness_case_signature=(
                _collection_replacement_pattern_wrong_text_model_correctness_case_signature
            ),
            workload_signature=(
                _collection_replacement_pattern_wrong_text_model_workload_signature
            ),
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-pattern-findall-bounded",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._workload_case_pair_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=partial(
                _is_collection_replacement_pattern_collection_workload,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_IDS,
                expected_operation="pattern.findall",
                requires_window_bounds=True,
            ),
            correctness_case_signature=partial(
                _collection_replacement_pattern_collection_correctness_case_signature,
                case_ids=_COLLECTION_REPLACEMENT_PATTERN_FINDALL_CASE_IDS,
                expected_operation="pattern.findall",
            ),
            workload_signature=partial(
                _collection_replacement_pattern_collection_workload_signature,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_IDS,
                expected_operation="pattern.findall",
                requires_window_bounds=True,
            ),
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-pattern-finditer-bounded",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._workload_case_pair_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=partial(
                _is_collection_replacement_pattern_collection_workload,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_IDS,
                expected_operation="pattern.finditer",
                requires_window_bounds=True,
            ),
            correctness_case_signature=partial(
                _collection_replacement_pattern_collection_correctness_case_signature,
                case_ids=_COLLECTION_REPLACEMENT_PATTERN_FINDITER_CASE_IDS,
                expected_operation="pattern.finditer",
            ),
            workload_signature=partial(
                _collection_replacement_pattern_collection_workload_signature,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_IDS,
                expected_operation="pattern.finditer",
                requires_window_bounds=True,
            ),
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-pattern-split",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._workload_case_pair_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=partial(
                _is_collection_replacement_pattern_collection_workload,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_IDS,
                expected_operation="pattern.split",
                requires_window_bounds=False,
            ),
            correctness_case_signature=partial(
                _collection_replacement_pattern_collection_correctness_case_signature,
                case_ids=_COLLECTION_REPLACEMENT_PATTERN_SPLIT_CASE_IDS,
                expected_operation="pattern.split",
            ),
            workload_signature=partial(
                _collection_replacement_pattern_collection_workload_signature,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_IDS,
                expected_operation="pattern.split",
                requires_window_bounds=False,
            ),
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-module-literal-replacement",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._workload_case_pair_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=partial(
                _is_collection_replacement_literal_replacement_workload,
                workload_ids=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_IDS,
                operations=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_OPERATIONS,
                text_models=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_TEXT_MODELS,
                allowed_counts=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_ALLOWED_COUNTS,
            ),
            correctness_case_signature=partial(
                _collection_replacement_literal_replacement_correctness_case_signature,
                case_ids=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_CASE_IDS,
                expected_operation=(
                    _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_EXPECTED_OPERATION
                ),
                operation_prefix=(
                    _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_OPERATION_PREFIX
                ),
                args_offset=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_ARGS_OFFSET,
            ),
            workload_signature=partial(
                _collection_replacement_literal_replacement_workload_signature,
                include_workload=partial(
                    _is_collection_replacement_literal_replacement_workload,
                    workload_ids=(
                        _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_IDS
                    ),
                    operations=(
                        _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_OPERATIONS
                    ),
                    text_models=(
                        _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_TEXT_MODELS
                    ),
                    allowed_counts=(
                        _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_ALLOWED_COUNTS
                    ),
                ),
                workload_kind="module",
            ),
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-pattern-literal-replacement",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._workload_case_pair_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=partial(
                _is_collection_replacement_literal_replacement_workload,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_IDS,
                operations=_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_OPERATIONS,
                text_models=_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_TEXT_MODELS,
            ),
            correctness_case_signature=partial(
                _collection_replacement_literal_replacement_correctness_case_signature,
                case_ids=_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_CASE_IDS,
                expected_operation=(
                    _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_EXPECTED_OPERATION
                ),
                operation_prefix=(
                    _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_OPERATION_PREFIX
                ),
                args_offset=(
                    _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_ARGS_OFFSET
                ),
            ),
            workload_signature=partial(
                _collection_replacement_literal_replacement_workload_signature,
                include_workload=partial(
                    _is_collection_replacement_literal_replacement_workload,
                    workload_ids=(
                        _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_IDS
                    ),
                    operations=(
                        _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_OPERATIONS
                    ),
                    text_models=(
                        _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_TEXT_MODELS
                    ),
                ),
                workload_kind="direct Pattern",
            ),
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-grouped-callable-replacement",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._workload_case_pair_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=_is_collection_replacement_grouped_callable_workload,
            correctness_case_signature=(
                _collection_replacement_grouped_callable_correctness_case_signature
            ),
            workload_signature=_collection_replacement_grouped_callable_workload_signature,
            run_callback_result_parity=True,
        ),
    )


def _collection_replacement_literal_replacement_correctness_case_signature(
    case: Any,
    *,
    case_ids: tuple[str, ...] | None = None,
    expected_operation: str | None = None,
    operation_prefix: str | None = None,
    args_offset: int | None = None,
) -> tuple[Any, ...] | None:
    if expected_operation is None or operation_prefix is None or args_offset is None:
        raise AssertionError(
            "literal replacement correctness signatures require explicit "
            "operation metadata"
        )
    if case.manifest_id != "collection-replacement-workflows":
        return None
    if case_ids is not None and case.case_id not in case_ids:
        return None
    if case.operation != expected_operation or case.kwargs:
        return None
    if case.helper not in {"sub", "subn"}:
        return None
    if case.use_compiled_pattern:
        return None
    pattern = case_pattern(case)
    if pattern not in {"abc", b"abc"}:
        return None
    if len(case.args) <= args_offset:
        return None
    if case.args[args_offset] not in {"x", b"x"}:
        return None
    trailing_args = case.args[args_offset:]
    if len(trailing_args) not in {2, 3}:
        return None
    if len(trailing_args) == 3 and type(trailing_args[2]) is not int:
        return None
    return (
        f"{operation_prefix}.{case.helper}",
        pattern,
        benchmark_test_support.freeze_signature_value(list(trailing_args)),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def _collection_replacement_literal_replacement_workload_signature(
    workload: Any,
    *,
    include_workload: Callable[[Any], bool],
    workload_kind: str,
) -> tuple[Any, ...]:
    if not include_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement "
            f"{workload_kind} literal replacement workload {workload.workload_id!r}"
        )
    args = [
        workload.replacement_payload(),
        workload.haystack_payload(),
    ]
    if workload.count:
        args.append(workload.count_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(args),
        (),
        workload.flags,
        workload.text_model,
    )
def _module_workflow_positional_indexlike_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.helper not in {"split", "sub", "subn"} or case.kwargs:
        return None
    if case.operation == "module_call":
        if case.use_compiled_pattern or not case.include_pattern_arg:
            return None
    elif case.operation != "pattern_call":
        return None
    if not any(hasattr(argument, "__index__") for argument in case.args):
        return None
    return (
        case.helper,
        case_pattern(case),
        module_workflow_positional_args_signature(case.args),
        case.text_model or "str",
    )


def _collection_replacement_positional_indexlike_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation in {"module.split", "pattern.split"}:
        return (
            workload.haystack_payload(),
            workload.maxsplit,
        )
    if workload.operation in _COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS:
        return (
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count,
        )
    raise AssertionError(
        "unexpected collection/replacement positional-indexlike workload operation "
        f"{workload.operation!r}"
    )


def _collection_replacement_positional_indexlike_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_positional_indexlike_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement positional-indexlike workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation.removeprefix("module.").removeprefix("pattern."),
        workload.pattern_payload(),
        module_workflow_positional_args_signature(
            _collection_replacement_positional_indexlike_workload_args(workload)
        ),
        workload.text_model,
    )


def _is_collection_replacement_positional_indexlike_workload(workload: Any) -> bool:
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if keyword_parameter == "maxsplit":
        parameter_payload = workload.maxsplit
    elif keyword_parameter == "count":
        parameter_payload = workload.count
    else:
        parameter_payload = None
    return (
        not workload.kwargs
        and workload.expected_exception is None
        and benchmark_test_support._is_encoded_indexlike_payload(parameter_payload)
    )

def _collection_replacement_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if not case.kwargs:
        return None
    if case.helper not in {"split", "sub", "subn"}:
        return None
    use_compiled_pattern = False
    if case.operation == "module_call":
        use_compiled_pattern = case.use_compiled_pattern
    elif case.operation != "pattern_call":
        return None
    return (
        f"{'module' if case.operation == 'module_call' else 'pattern'}.{case.helper}",
        case_pattern(case),
        benchmark_test_support.freeze_signature_value(list(case.args)),
        module_workflow_keyword_kwargs_signature(case.kwargs),
        use_compiled_pattern,
        case.flags or 0,
        case.text_model or "str",
    )


def _collection_replacement_keyword_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    positional_keyword_field = _collection_replacement_positional_keyword_field(
        workload
    )
    if workload.operation in {"module.split", "pattern.split"}:
        args: list[object] = [workload.haystack_payload()]
        if positional_keyword_field == "maxsplit":
            args.append(workload.maxsplit)
        return tuple(args)
    if workload.operation in _COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS:
        args: list[object] = [
            workload.replacement_payload(),
            workload.haystack_payload(),
        ]
        if positional_keyword_field == "count":
            args.append(workload.count)
        return tuple(args)
    raise AssertionError(
        "unexpected collection/replacement keyword workload operation "
        f"{workload.operation!r}"
    )


def _collection_replacement_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_keyword_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement keyword workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(
            list(_collection_replacement_keyword_workload_args(workload))
        ),
        module_workflow_keyword_kwargs_signature(workload.kwargs),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _collection_replacement_compiled_pattern_success_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"split", "findall", "finditer", "sub", "subn"}:
        return None
    operation = f"module.{case.helper}"
    haystack_index = _collection_replacement_wrong_text_model_haystack_index(operation)
    if len(case.args) <= haystack_index:
        return None
    haystack = case.args[haystack_index]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, str):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, bytes):
        return None
    return (
        operation,
        case_pattern(case),
        benchmark_test_support.freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_compiled_pattern_success_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_compiled_pattern_success_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement compiled-pattern success workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(
            list(_collection_replacement_wrong_text_model_workload_args(workload))
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _pattern_helper_collection_replacement_keyword_error_workload(
    *,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    expected_exception: dict[str, str],
    text_model: str,
) -> benchmarks.Workload:
    return benchmarks.workload_from_payload(
        {
            "manifest_id": "python-benchmark-pattern-collection-replacement-keyword-contract",
            "workload_id": f"{operation}-keyword-error-materialization-contract",
            "bucket": operation.replace("pattern.", "pattern-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "expected_exception": expected_exception,
            "flags": 0,
            "count": count,
            "maxsplit": maxsplit,
            "kwargs": kwargs_payload,
            "text_model": text_model,
            "cache_mode": "warm",
            "timing_scope": "pattern-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


_PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS = (
    "pattern-split-duplicate-maxsplit-keyword-warm-str",
    "pattern-split-unexpected-keyword-warm-bytes",
    "pattern-sub-duplicate-count-keyword-warm-str",
    "pattern-sub-unexpected-keyword-warm-str",
    "pattern-sub-unexpected-keyword-after-positional-count-warm-str",
    "pattern-sub-count-alias-keyword-warm-str",
    "pattern-subn-duplicate-count-keyword-warm-bytes",
    "pattern-subn-unexpected-keyword-warm-bytes",
    "pattern-subn-unexpected-keyword-after-positional-count-warm-bytes",
    "pattern-subn-count-alias-keyword-warm-bytes",
)


def _is_collection_replacement_pattern_helper_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and not workload.use_compiled_pattern
        and workload.operation in {"pattern.split", "pattern.sub", "pattern.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
        and workload.workload_id
        in _PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    )


_PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS = benchmark_test_support._contract_source_workloads(
    manifest_path=benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
    include_workload_selectors=(
        _is_collection_replacement_pattern_helper_keyword_error_workload,
    ),
    expected_source_workload_ids=(
        _PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    ),
    drift_message=(
        "pattern helper collection/replacement keyword-error surface drifted "
        "from the live source workload surface"
    ),
)


_MODULE_HELPER_BOUNDARY_KEYWORD_ERROR_WORKLOAD_IDS = (
    "module-search-duplicate-flags-keyword-warm-str",
    "module-fullmatch-unexpected-keyword-purged-str",
)

_MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS = (
    "module-split-duplicate-maxsplit-keyword-purged-str",
    "module-split-unexpected-keyword-purged-str",
    "module-split-unexpected-keyword-purged-bytes",
    "module-sub-duplicate-count-keyword-warm-str",
    "module-sub-unexpected-keyword-purged-str",
    "module-sub-unexpected-keyword-after-positional-count-purged-str",
    "module-sub-count-alias-keyword-purged-str",
    "module-subn-unexpected-keyword-after-positional-count-purged-bytes",
    "module-subn-count-alias-keyword-purged-bytes",
)


def _is_collection_replacement_module_helper_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and not workload.use_compiled_pattern
        and workload.operation in {"module.split", "module.sub", "module.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
        and workload.workload_id
        in _MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    )


_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS = benchmark_test_support._contract_source_workloads(
    manifest_path=benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
    include_workload_selectors=(
        benchmark_test_support._is_module_workflow_keyword_error_workload,
    ),
    expected_source_workload_ids=_MODULE_HELPER_BOUNDARY_KEYWORD_ERROR_WORKLOAD_IDS,
    drift_message=(
        "module helper keyword-error surface drifted from the live source "
        "workload surface"
    ),
) + benchmark_test_support._contract_source_workloads(
    manifest_path=benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
    include_workload_selectors=(
        _is_collection_replacement_module_helper_keyword_error_workload,
    ),
    expected_source_workload_ids=(
        _MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    ),
    drift_message=(
        "module helper collection/replacement keyword-error surface drifted "
        "from the live source workload surface"
    ),
)


def _assert_keyword_error_workload_probe_measured(
    source_workload: Any,
    *,
    import_name: str,
    adapter_name: str,
) -> None:
    payload = benchmarks.workload_to_payload(source_workload)
    round_tripped = benchmarks.workload_from_payload(payload)

    assert payload["workload_id"] == source_workload.workload_id
    assert round_tripped.workload_id == source_workload.workload_id
    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert payload["kwargs"] == source_workload.kwargs
    assert round_tripped.kwargs == source_workload.kwargs

    probe = benchmarks.run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS = frozenset(
    {
        "manifest_id",
        "workload_id",
        "warmup_iterations",
        "sample_iterations",
        "timed_samples",
        "smoke",
    }
)
_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS = (
    "pattern-split-on-bytes-string-warm-str",
    "pattern-sub-on-bytes-string-warm-str",
    "pattern-subn-on-str-string-purged-bytes",
)
_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC = (
    SimpleNamespace(
        manifest_id="collection-replacement-boundary",
        excluded_fields=_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS,
        manifest_timed_samples=2,
        timing_scope="pattern-helper-call",
        notes=(),
    )
)

def _collection_replacement_wrong_text_model_expected_callback_call(
    source_workload: Any,
) -> tuple[object, ...]:
    if source_workload.operation == "pattern.split":
        return (
            "pattern.split",
            source_workload.haystack_payload(),
            (source_workload.maxsplit_argument(),),
            {},
        )
    if source_workload.operation in {"pattern.sub", "pattern.subn"}:
        return (
            source_workload.operation,
            source_workload.replacement_payload(),
            source_workload.haystack_payload(),
            (source_workload.count_argument(),),
            {},
        )
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {source_workload.operation!r}"
    )


def _collection_replacement_wrong_text_model_expected_callback_result(
    source_workload: Any,
) -> object:
    if source_workload.operation == "pattern.subn":
        return ("pattern-result", 0)
    if source_workload.operation in {"pattern.split", "pattern.sub"}:
        return "pattern-result"
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {source_workload.operation!r}"
    )


def _run_cpython_collection_replacement_wrong_text_model_workload(
    workload: Any,
) -> object:
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    helper_name = workload.operation.removeprefix("pattern.")
    if workload.operation == "pattern.split":
        return getattr(compiled_pattern, helper_name)(
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        return getattr(compiled_pattern, helper_name)(
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {workload.operation!r}"
    )


def _collection_replacement_wrong_text_model_haystack_index(operation: str) -> int:
    if operation in {"module.split", "module.findall", "module.finditer"}:
        return 0
    if operation in {"module.sub", "module.subn"}:
        return 1
    raise AssertionError(
        "unexpected collection/replacement wrong-text-model workload operation "
        f"{operation!r}"
    )


def _collection_replacement_wrong_text_model_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"split", "findall", "finditer", "sub", "subn"}:
        return None
    operation = f"module.{case.helper}"
    haystack_index = _collection_replacement_wrong_text_model_haystack_index(operation)
    if len(case.args) <= haystack_index:
        return None
    haystack = case.args[haystack_index]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, bytes):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, str):
        return None
    return (
        operation,
        case_pattern(case),
        benchmark_test_support.freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_wrong_text_model_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation == "module.split":
        return (
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )
    if workload.operation in {"module.findall", "module.finditer"}:
        return (workload.haystack_payload(),)
    if workload.operation in {"module.sub", "module.subn"}:
        return (
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
    raise AssertionError(
        "unexpected collection/replacement wrong-text-model workload operation "
        f"{workload.operation!r}"
    )


def _collection_replacement_wrong_text_model_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_wrong_text_model_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement wrong-text-model workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(
            list(_collection_replacement_wrong_text_model_workload_args(workload))
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )
def _pattern_collection_replacement_wrong_text_model_haystack_index(
    operation: str,
) -> int:
    if operation == "pattern.split":
        return 0
    if operation in {"pattern.sub", "pattern.subn"}:
        return 1
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {operation!r}"
    )


def _collection_replacement_pattern_wrong_text_model_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"split", "sub", "subn"}:
        return None
    operation = f"pattern.{case.helper}"
    haystack_index = _pattern_collection_replacement_wrong_text_model_haystack_index(
        operation
    )
    case_args = list(case.args)
    if len(case_args) <= haystack_index:
        return None
    haystack = case_args[haystack_index]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, bytes):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, str):
        return None
    return (
        operation,
        case_pattern(case),
        benchmark_test_support.freeze_signature_value(case_args),
        (),
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_pattern_wrong_text_model_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation == "pattern.split":
        args: list[object] = [workload.haystack_payload()]
        if workload.maxsplit:
            args.append(workload.maxsplit_argument())
        return tuple(args)
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [
            workload.replacement_payload(),
            workload.haystack_payload(),
        ]
        if workload.count:
            args.append(workload.count_argument())
        return tuple(args)
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {workload.operation!r}"
    )


def _collection_replacement_pattern_wrong_text_model_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_pattern_wrong_text_model_workload(workload):
        raise AssertionError(
            "unexpected direct Pattern collection/replacement wrong-text-model "
            f"workload {workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(
            list(
                _collection_replacement_pattern_wrong_text_model_workload_args(
                    workload
                )
            )
        ),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_collection_replacement_pattern_wrong_text_model_workload(
    workload: Any,
) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is not None
        and not workload.kwargs
        and not workload.use_compiled_pattern
        and workload.operation in {"pattern.split", "pattern.sub", "pattern.subn"}
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )


_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOADS = (
    benchmark_test_support._contract_source_workloads(
        manifest_path=benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload_selectors=(
            _is_collection_replacement_pattern_wrong_text_model_workload,
        ),
        expected_source_workload_ids=(
            _COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
        ),
        drift_message=(
            "direct Pattern collection/replacement wrong-text-model surface "
            "drifted from the live source workload surface"
        ),
    )
)


def _is_collection_replacement_literal_replacement_workload(
    workload: Any,
    *,
    workload_ids: tuple[str, ...],
    operations: tuple[str, ...],
    text_models: tuple[str, ...],
    allowed_counts: tuple[int, ...] | None = None,
) -> bool:
    return (
        workload.workload_id in workload_ids
        and workload.operation in operations
        and workload.pattern == "abc"
        and workload.replacement == "x"
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
        and workload.text_model in text_models
        and (allowed_counts is None or workload.count in allowed_counts)
        and workload.pos is None
        and workload.endpos is None
        and not workload.kwargs
    )


_COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS = (
    ("module-sub-callable-grouped-warm-str", "module-sub-callable-grouped-str"),
    ("module-sub-callable-grouped-warm-bytes", "module-sub-callable-grouped-bytes"),
    (
        "pattern-subn-callable-named-grouped-warm-str",
        "pattern-subn-callable-named-grouped-str",
    ),
    (
        "pattern-subn-callable-named-grouped-purged-bytes",
        "pattern-subn-callable-named-grouped-bytes",
    ),
)


def _is_collection_replacement_grouped_callable_workload(workload: Any) -> bool:
    return (
        workload.workload_id
        in tuple(
            workload_id
            for workload_id, _ in _COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS
        )
        and workload.operation in {"module.sub", "pattern.subn"}
        and workload.pattern in {
            "(abc)",
            b"(abc)",
            "(?P<word>abc)",
            b"(?P<word>abc)",
        }
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
        and workload.text_model in {"str", "bytes"}
        and workload.pos is None
        and workload.endpos is None
        and not workload.kwargs
    )


def _collection_replacement_grouped_callable_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.case_id not in tuple(
        case_id
        for _, case_id in _COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS
    ):
        return None
    if case.kwargs or case.use_compiled_pattern:
        return None
    if case.operation not in {"module_call", "pattern_call"}:
        return None
    if case.helper not in {"sub", "subn"}:
        return None
    replacement_signature = callable_match_group_signature(
        case_replacement_argument(case)
    )
    if replacement_signature is None:
        return None
    args = [case_text_argument(case)]
    if case.helper == "subn":
        count = case.args[-1]
        if type(count) is not int:
            return None
        args.append(count)
    operation_prefix = "module" if case.operation == "module_call" else "pattern"
    return (
        f"{operation_prefix}.{case.helper}",
        case_pattern(case),
        replacement_signature,
        benchmark_test_support.freeze_signature_value(args),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def _collection_replacement_grouped_callable_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_grouped_callable_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement grouped callable workload "
            f"{workload.workload_id!r}"
        )
    replacement_signature = callable_match_group_signature(
        workload.replacement_payload()
    )
    if replacement_signature is None:
        raise AssertionError(
            "expected callable_match_group replacement for grouped callable workload "
            f"{workload.workload_id!r}"
        )
    args = [workload.haystack_payload()]
    if workload.count:
        args.append(workload.count_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        replacement_signature,
        benchmark_test_support.freeze_signature_value(args),
        (),
        workload.flags,
        workload.text_model,
    )


def _text_model_agnostic_callable_match_group_signature(
    replacement: object,
) -> tuple[object, ...] | None:
    signature = callable_match_group_signature(replacement)
    if signature is None:
        return None
    return tuple(
        value.decode("utf-8") if isinstance(value, bytes) else value
        for value in signature
    )


def _workload_ids_for_text_model(
    workload_stems: tuple[str, ...],
    *,
    text_model: str,
) -> tuple[str, ...]:
    suffix = "-bytes" if text_model == "bytes" else "-str"
    return tuple(f"{stem}{suffix}" for stem in workload_stems)


CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-replacement-warm-bytes",
    "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-bytes",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-bytes",
    "module-sub-callable-named-conditional-group-exists-replacement-warm-bytes",
    "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-bytes",
    "pattern-sub-callable-named-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-callable-named-conditional-group-exists-replacement-purged-bytes",
    "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-bytes",
    "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-bytes",
    "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-bytes",
    "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-bytes",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-str",
    "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-str",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-str",
    "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-str",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
    "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-bytes",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
    "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-bytes",
)
_CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS = (
    "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged",
    "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm",
    "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged",
    "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm",
    "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged",
    "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm",
    "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged",
    "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm",
    "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged",
    "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS = _workload_ids_for_text_model(
    _CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS,
    text_model="str",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS = _workload_ids_for_text_model(
    _CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS,
    text_model="bytes",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS = (
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS
    + CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-gap",
    "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-str",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
    "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
    "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
    "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-str",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-str",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-str",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-str",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
    "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
    "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
    "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
    "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS = (
    CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS[:8]
    + CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS[:8]
    + CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS[8:]
    + CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS[8:]
)
CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS = (
    "module-sub-template-numbered-conditional-group-exists-replacement-warm-bytes",
    "module-subn-template-numbered-conditional-group-exists-replacement-warm-bytes",
    "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-bytes",
    "module-sub-template-named-conditional-group-exists-replacement-warm-bytes",
    "module-subn-template-named-conditional-group-exists-replacement-warm-bytes",
    "pattern-sub-template-named-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-template-named-conditional-group-exists-replacement-purged-bytes",
    "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
    "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-bytes",
    "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
    "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-bytes",
)
CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS = (
    "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-str",
    "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-str",
    "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-str",
    "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-str",
)
CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS = (
    CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS[:8]
    + CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
    + CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS[8:]
)


CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS = (
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-str",
    "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-str",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-str",
    "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-str",
    "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-str",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-str",
    "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-str",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-str",
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-str",
    "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-str",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-str",
    "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-str",
    "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-str",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-str",
    "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-str",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-str",
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-str",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-str",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-str",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-str",
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-str",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-str",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-str",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-str",
)
CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-bytes",
    "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
    "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-bytes",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
    "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
    "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
    "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
    "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
    "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
)
CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
)
_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS = (
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm",
    "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-purged",
    "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-purged",
    "module-sub-callable-named-quantified-conditional-group-exists-replacement-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-warm",
    "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-purged",
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-purged",
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm",
    "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged",
    "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged",
    "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm",
    "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged",
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm",
    "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged",
    "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged",
    "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm",
    "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged",
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm",
    "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged",
    "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged",
    "module-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-warm",
    "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-purged",
)
CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS = _workload_ids_for_text_model(
    _CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS,
    text_model="str",
)
CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS = _workload_ids_for_text_model(
    _CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS,
    text_model="bytes",
)

COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS = (
    _CollectionReplacementCombinedSliceExpectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-template-replacement-rows",
        required_syntax_features=("conditionals", "replacement-template"),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation-heavy",
            "nested-group",
            "quantified",
            "unsupported",
            "callable",
        ),
        expected_workload_ids=(
            "module-sub-template-numbered-conditional-group-exists-replacement-warm-gap",
            "module-subn-template-numbered-conditional-group-exists-replacement-warm-str",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-str",
            "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-str",
            "module-sub-template-numbered-conditional-group-exists-replacement-warm-bytes",
            "module-subn-template-numbered-conditional-group-exists-replacement-warm-bytes",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-bytes",
            "module-sub-template-named-conditional-group-exists-replacement-warm-str",
            "module-subn-template-named-conditional-group-exists-replacement-warm-str",
            "pattern-sub-template-named-conditional-group-exists-replacement-purged-str",
            "pattern-subn-template-named-conditional-group-exists-replacement-purged-str",
            "module-sub-template-named-conditional-group-exists-replacement-warm-bytes",
            "module-subn-template-named-conditional-group-exists-replacement-warm-bytes",
            "pattern-sub-template-named-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-template-named-conditional-group-exists-replacement-purged-bytes",
            "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-str",
            "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-str",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-str",
            "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
            "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-bytes",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
            "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-bytes",
        ),
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcdzz", "zzacezz", "abcdaceabcd"}),
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "template",
        ),
    ),
    _CollectionReplacementCombinedSliceExpectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-callable-replacement-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "exception",
            "nested-conditional",
            "nested-group",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-conditional-group-exists-replacement-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-replacement-warm-bytes",
            "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-str",
            "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-bytes",
            "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
            "module-sub-callable-named-conditional-group-exists-replacement-warm-str",
            "module-sub-callable-named-conditional-group-exists-replacement-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-bytes",
            "pattern-sub-callable-named-conditional-group-exists-replacement-purged-str",
            "pattern-sub-callable-named-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-purged-gap",
            "pattern-subn-callable-named-conditional-group-exists-replacement-purged-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-bytes",
        ),
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcdzz", "zzabcdacezz", "abcdaceabcd"}),
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "callable",
        ),
    ),
    _CollectionReplacementCombinedSliceExpectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-callable-replacement-exception-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        required_categories=("exception",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "nested-conditional",
            "nested-group",
            "none-count",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-str",
            "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-bytes",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-bytes",
        ),
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
        expected_operations=frozenset({"module.subn", "pattern.subn"}),
        expected_haystacks=frozenset({"zzacezz"}),
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "callable",
            "absent",
            "count",
            "exception",
        ),
    ),
    _CollectionReplacementCombinedSliceExpectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-callable-replacement-none-count-exception-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        required_categories=("none-count", "exception"),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "nested-conditional",
            "nested-group",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged-bytes",
            "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm-str",
            "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm-bytes",
            "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged-str",
            "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged-bytes",
            "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm-str",
            "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
            "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
        ),
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcdzz", "zzacezz", "abcdaceabcd"}),
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "callable",
            "count",
            "none-count",
            "exception",
        ),
    ),
    _CollectionReplacementCombinedSliceExpectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="alternation-heavy-callable-replacement-rows",
        required_syntax_features=("conditionals", "alternation", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        required_categories=("alternation-heavy", "replacement", "callable"),
        expected_workload_ids=CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS,
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)(de|df)|(eg|eh))",
            r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset(
            {"zzabcdezz", "zzabcdfzz", "zzacegzz", "zzacehzz"}
        ),
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "alternation-heavy",
            "replacement",
            "callable",
        ),
    ),
    _CollectionReplacementCombinedSliceExpectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="nested-callable-replacement-str-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        required_categories=("nested-conditional",),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "bytes",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS,
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)(?(1)d|e)|f)",
            r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcdzz", "zzabcezz", "zzacezz", "zzacfzz"}),
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "nested-conditional",
            "replacement",
            "callable",
        ),
    ),
    _CollectionReplacementCombinedSliceExpectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="nested-callable-replacement-bytes-rows",
        required_syntax_features=(
            "pattern-text-model",
            "conditionals",
            "callable-replacement",
        ),
        required_categories=("nested-conditional", "bytes"),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "nested-group",
            "unsupported",
        ),
        expected_workload_ids=CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS,
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)(?(1)d|e)|f)",
            r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcdzz", "zzabcezz", "zzacezz", "zzacfzz"}),
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "nested-conditional",
            "replacement",
            "callable",
            "bytes",
        ),
    ),
    _CollectionReplacementCombinedSliceExpectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="quantified-callable-replacement-str-rows",
        required_syntax_features=(
            "conditionals",
            "quantifiers",
            "callable-replacement",
        ),
        required_categories=("quantified",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "bytes",
            "nested-conditional",
            "nested-group",
            "unsupported",
        ),
        expected_workload_ids=CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)d|e){2}",
            r"a(?P<word>b)?c(?(word)d|e){2}",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcddzz", "zzaceezz", "zzabcdezz", "zzacedzz"}),
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "quantified",
            "replacement",
            "callable",
        ),
    ),
    _CollectionReplacementCombinedSliceExpectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="quantified-callable-replacement-bytes-rows",
        required_syntax_features=(
            "pattern-text-model",
            "conditionals",
            "quantifiers",
            "callable-replacement",
        ),
        required_categories=("quantified", "bytes"),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "nested-conditional",
            "nested-group",
            "unsupported",
        ),
        expected_workload_ids=CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)d|e){2}",
            r"a(?P<word>b)?c(?(word)d|e){2}",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcddzz", "zzaceezz", "zzabcdezz", "zzacedzz"}),
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "quantified",
            "replacement",
            "callable",
            "bytes",
        ),
    ),
)
_CONDITIONAL_GROUP_EXISTS_TEMPLATE_REPLACEMENT_EXPECTATION = next(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id == "minimal-template-replacement-rows"
)
_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTED_SLICE_IDS = (
    "minimal-callable-replacement-rows",
    "minimal-callable-replacement-exception-rows",
    "minimal-callable-replacement-none-count-exception-rows",
    "alternation-heavy-callable-replacement-rows",
)
_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS = tuple(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id
    in _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTED_SLICE_IDS
)
_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_ACTUAL_SLICE_IDS = tuple(
    expectation.slice_id
    for expectation in _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
)
if (
    _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_ACTUAL_SLICE_IDS
    != _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTED_SLICE_IDS
):
    raise AssertionError(
        "conditional callable replacement slice expectations drifted: "
        "expected "
        f"{_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTED_SLICE_IDS!r}, got "
        f"{_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_ACTUAL_SLICE_IDS!r}"
    )
_CONDITIONAL_GROUP_EXISTS_ALTERNATION_CALLABLE_REPLACEMENT_EXPECTATION = next(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id == "alternation-heavy-callable-replacement-rows"
)
_CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_REPLACEMENT_EXPECTATION = next(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id == "nested-callable-replacement-str-rows"
)
_CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION = next(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id == "nested-callable-replacement-bytes-rows"
)
_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_REPLACEMENT_EXPECTATION = next(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id == "quantified-callable-replacement-str-rows"
)
_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION = next(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id == "quantified-callable-replacement-bytes-rows"
)


def _conditional_group_exists_quantified_callable_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.manifest_id != "conditional-group-exists-callable-replacement-workflows":
        return None
    if "quantified" not in case.categories:
        return None
    if any(category in case.categories for category in ("alternation", "nested")):
        return None
    if case.operation not in {"module_call", "pattern_call"}:
        return None
    if case.helper not in {"sub", "subn"}:
        return None
    if case.kwargs or case.use_compiled_pattern:
        return None
    replacement_signature = callable_match_group_signature(
        case_replacement_argument(case)
    )
    if replacement_signature is None:
        return None
    count_index = 3 if case.operation == "module_call" else 2
    args = [case_text_argument(case)]
    if len(case.args) > count_index:
        count = case.args[count_index]
        if count is None:
            pass
        elif type(count) is int:
            args.append(count)
        else:
            return None
    operation_prefix = "module" if case.operation == "module_call" else "pattern"
    return (
        f"{operation_prefix}.{case.helper}",
        case_pattern(case),
        replacement_signature,
        benchmark_test_support.freeze_signature_value(args),
        "exception" in case.categories,
        "no-match" in case.categories,
        case.flags or 0,
        case.text_model or "str",
    )


def _conditional_group_exists_nested_callable_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.manifest_id != "conditional-group-exists-callable-replacement-workflows":
        return None
    if "nested" not in case.categories:
        return None
    if any(category in case.categories for category in ("quantified", "alternation")):
        return None
    if case.operation not in {"module_call", "pattern_call"}:
        return None
    if case.helper not in {"sub", "subn"}:
        return None
    if case.kwargs or case.use_compiled_pattern:
        return None
    replacement_signature = callable_match_group_signature(
        case_replacement_argument(case)
    )
    if replacement_signature is None:
        return None
    count_index = 3 if case.operation == "module_call" else 2
    args = [case_text_argument(case)]
    if len(case.args) > count_index:
        args.append(case.args[count_index])
    operation_prefix = "module" if case.operation == "module_call" else "pattern"
    return (
        f"{operation_prefix}.{case.helper}",
        case_pattern(case),
        replacement_signature,
        benchmark_test_support.freeze_signature_value(args),
        "exception" in case.categories,
        "no-match" in case.categories,
        case.flags or 0,
        case.text_model or "str",
    )


def _conditional_group_exists_nested_callable_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    expected_workload_ids = (
        CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
        + CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
    )
    if workload.workload_id not in expected_workload_ids:
        raise AssertionError(
            "unexpected conditional nested callable workload "
            f"{workload.workload_id!r}"
        )
    replacement_signature = callable_match_group_signature(
        workload.replacement_payload()
    )
    if replacement_signature is None:
        raise AssertionError(
            "expected callable_match_group replacement for nested "
            f"conditional workload {workload.workload_id!r}"
        )
    args: list[object] = [workload.haystack_payload()]
    if workload.count != 0:
        args.append(workload.count_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        replacement_signature,
        benchmark_test_support.freeze_signature_value(args),
        workload.expected_exception is not None,
        "no-match" in workload.categories,
        workload.flags,
        workload.text_model,
    )


def _conditional_group_exists_quantified_callable_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    expected_workload_ids = (
        CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
        + CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
    )
    if workload.workload_id not in expected_workload_ids:
        raise AssertionError(
            "unexpected conditional quantified callable workload "
            f"{workload.workload_id!r}"
        )
    replacement_signature = callable_match_group_signature(
        workload.replacement_payload()
    )
    if replacement_signature is None:
        raise AssertionError(
            "expected callable_match_group replacement for quantified "
            f"conditional workload {workload.workload_id!r}"
        )
    args = [workload.haystack_payload()]
    if workload.count:
        args.append(workload.count_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        replacement_signature,
        benchmark_test_support.freeze_signature_value(args),
        workload.expected_exception is not None,
        "no-match" in workload.categories,
        workload.flags,
        workload.text_model,
    )
COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS = (
    _collection_replacement_standard_benchmark_definitions()
)

SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS = (
    SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS
    + COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
)


def ordered_operations(workloads: list[Workload]) -> list[str]:
    operations: list[str] = []
    for workload in workloads:
        operation = workload.operation
        if operation not in operations:
            operations.append(operation)
    return operations


def _filter_manifest_workload_ids(
    workload_ids: tuple[str, ...] | None,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> tuple[str, ...]:
    if workload_ids is None:
        return ()
    if selected_workload_ids is None or not workload_ids:
        return workload_ids

    selected_workload_id_set = {
        str(workload_id) for workload_id in selected_workload_ids
    }
    return tuple(
        workload_id
        for workload_id in workload_ids
        if workload_id in selected_workload_id_set
    )


def source_tree_combined_manifest_representative_measured_workload_ids(
    manifest_id: str,
) -> tuple[str, ...]:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )

    explicit_workload_ids = manifest_expectation.representative_measured_workload_ids
    if explicit_workload_ids is not None:
        return explicit_workload_ids

    representative_ids: list[str] = []
    shape_expectation = manifest_expectation.shape_expectation
    if shape_expectation is not None:
        for workload_id in shape_expectation.representative_measured_workload_ids:
            normalized_workload_id = str(workload_id)
            if normalized_workload_id not in representative_ids:
                representative_ids.append(normalized_workload_id)
    for expectation in SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS:
        if expectation.manifest_id != manifest_id:
            continue
        for workload_id in expectation.expected_workload_ids:
            normalized_workload_id = str(workload_id)
            if normalized_workload_id not in representative_ids:
                representative_ids.append(normalized_workload_id)
    return tuple(representative_ids)


def _public_source_tree_manifest_expectation(
    manifest_id: str,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> SourceTreeManifestExpectation:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )
    return SourceTreeManifestExpectation(
        known_gap_count=len(
            _filter_manifest_workload_ids(
                manifest_expectation.known_gap_workload_ids,
                selected_workload_ids=selected_workload_ids,
            )
        ),
        representative_measured_workload_ids=_filter_manifest_workload_ids(
            manifest_expectation.representative_measured_workload_ids,
            selected_workload_ids=selected_workload_ids,
        ),
        representative_known_gap_workload_ids=_filter_manifest_workload_ids(
            manifest_expectation.representative_known_gap_workload_ids,
            selected_workload_ids=selected_workload_ids,
        ),
    )

def source_tree_combined_target_manifest_ids() -> tuple[str, ...]:
    target_manifest_ids: list[str] = []
    missing_expectations: list[str] = []
    for manifest in published_benchmark_manifests():
        manifest_id = manifest.manifest_id
        manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(
            manifest_id
        )
        if manifest_expectation is None:
            missing_expectations.append(manifest_id)
            continue
        if manifest_expectation.exclude_from_combined_targets:
            continue
        target_manifest_ids.append(manifest_id)
    if missing_expectations:
        raise AssertionError(
            "source-tree combined manifest expectations drifted from the published full-suite selector: "
            f"missing {sorted(missing_expectations)}"
        )
    return tuple(target_manifest_ids)


def expected_summary_for_manifests(
    manifests: list[BenchmarkManifest],
    *,
    selection_mode: str,
    manifest_known_gap_counts: dict[str, int] | None = None,
) -> dict[str, int]:
    workloads: list[Workload] = []
    regression_workloads = 0
    selected_manifest_ids: list[str] = []
    for manifest in manifests:
        manifest_id = manifest.manifest_id
        selected_manifest_workloads = manifest.selected_workloads(
            selection_mode=selection_mode
        )
        if selected_manifest_workloads:
            selected_manifest_ids.append(manifest_id)
        if manifest_id == "regression-matrix":
            regression_workloads += len(selected_manifest_workloads)
        workloads.extend(selected_manifest_workloads)
    known_gap_counts = (
        manifest_known_gap_counts
        if manifest_known_gap_counts is not None
        else {
            manifest.manifest_id: len(
                _filter_manifest_workload_ids(
                    SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                        manifest.manifest_id
                    ].known_gap_workload_ids,
                    selected_workload_ids=(
                        workload.workload_id
                        for workload in manifest.selected_workloads(
                            selection_mode=selection_mode
                        )
                    ),
                )
            )
            for manifest in manifests
            if manifest.manifest_id in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
        }
    )
    known_gap_count = sum(
        known_gap_counts.get(manifest_id, 0) for manifest_id in selected_manifest_ids
    )
    return {
        "known_gap_count": known_gap_count,
        "measured_workloads": len(workloads) - known_gap_count,
        "module_workloads": sum(1 for workload in workloads if workload.family == "module"),
        "parser_workloads": sum(1 for workload in workloads if workload.family == "parser"),
        "regression_workloads": regression_workloads,
        "total_workloads": len(workloads),
    }


def source_tree_combined_case(target_manifest_id: str) -> SourceTreeCombinedCase:
    manifests: list[BenchmarkManifest] = []
    published_manifests = published_benchmark_manifests()
    regression_manifest = next(
        (
            manifest
            for manifest in published_manifests
            if manifest.manifest_id == "regression-matrix"
        ),
        None,
    )
    for manifest in published_manifests:
        manifest_id = manifest.manifest_id
        if manifest_id == "regression-matrix":
            continue
        manifests.append(manifest)
        if manifest_id == target_manifest_id:
            break
    else:
        raise AssertionError(
            f"target manifest {target_manifest_id!r} is not in the published full-suite selector"
        )
    if target_manifest_id != "module-boundary":
        if regression_manifest is None:
            raise AssertionError(
                "the published full-suite selector is missing the regression-matrix manifest"
            )
        manifests.append(regression_manifest)
    workloads = [workload for manifest in manifests for workload in manifest.workloads]
    target_manifest = next(
        manifest for manifest in manifests if manifest.manifest_id == target_manifest_id
    )
    workload_payloads = [workload_to_payload(workload) for workload in workloads]
    return SourceTreeCombinedCase(
        expected_adapter=(
            "rebar.module-surface"
            if any(workload.family == "module" for workload in workloads)
            else "rebar.compile"
        ),
        expected_phase=determine_phase(workload_payloads),
        expected_runner_version=determine_runner_version(workload_payloads),
        expected_summary=expected_summary_for_manifests(
            manifests,
            selection_mode="full",
        ),
        manifests=manifests,
        selection_mode="full",
        manifest_expectation=_public_source_tree_manifest_expectation(target_manifest_id),
        manifest_id=target_manifest_id,
        target_manifest=target_manifest,
    )

def _workload_matches_source_tree_combined_slice(
    workload: Workload,
    expectation: SourceTreeCombinedSliceExpectation,
) -> bool:
    workload_id = workload.workload_id
    required_id_suffix = expectation.required_id_suffix
    if required_id_suffix is not None and not workload_id.endswith(required_id_suffix):
        return False

    syntax_features = set(workload.syntax_features)
    categories = set(workload.categories)
    return (
        set(expectation.required_syntax_features).issubset(syntax_features)
        and syntax_features.isdisjoint(expectation.excluded_syntax_features)
        and set(expectation.required_categories).issubset(categories)
        and categories.isdisjoint(expectation.excluded_categories)
    )


def select_source_tree_combined_slice_rows(
    manifest: BenchmarkManifest,
    expectation: SourceTreeCombinedSliceExpectation,
) -> list[Workload]:
    return [
        workload
        for workload in manifest.workloads
        if _workload_matches_source_tree_combined_slice(workload, expectation)
    ]


def _compile_search_fullmatch_case_signature(
    case: Any,
    *,
    pattern: Callable[[], Any],
) -> tuple[Any, ...] | None:
    kwargs_signature = benchmark_test_support.freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", pattern(), (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper == "search":
        return (
            "module.search",
            None,
            benchmark_test_support.freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper == "fullmatch":
        return (
            "pattern.fullmatch",
            pattern(),
            benchmark_test_support.freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _compile_search_fullmatch_workload_signature(
    workload: Any,
    *,
    pattern: Callable[[], Any],
    module_search_args: Callable[[], tuple[Any, ...]],
    pattern_fullmatch_args: Callable[[], tuple[Any, ...]],
    error_label: str,
) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            pattern(),
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "module.search":
        return (
            "module.search",
            None,
            module_search_args(),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "pattern.fullmatch":
        return (
            "pattern.fullmatch",
            pattern(),
            pattern_fullmatch_args(),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected {error_label} workload operation {workload.operation!r}"
    )


def _optional_group_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.helper != "search":
        return None

    kwargs_signature = benchmark_test_support.freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"
    return (
        "module.search",
        None,
        benchmark_test_support.freeze_signature_value(case.serialized_args()),
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
        benchmark_test_support.freeze_signature_value([workload.pattern, workload.haystack]),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_optional_group_conditional_workload(workload: Any) -> bool:
    return workload.workload_id == _OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID


def _nested_group_correctness_case_signature(case: Any) -> tuple[Any, ...] | None:
    return _compile_search_fullmatch_case_signature(
        case,
        pattern=lambda: case.pattern,
    )


def _nested_group_workload_signature(workload: Any) -> tuple[Any, ...]:
    return _compile_search_fullmatch_workload_signature(
        workload,
        pattern=lambda: workload.pattern,
        module_search_args=lambda: (workload.pattern, workload.haystack),
        pattern_fullmatch_args=lambda: (workload.haystack,),
        error_label="nested-group benchmark",
    )


def _counted_repeat_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    return _compile_search_fullmatch_case_signature(
        case,
        pattern=lambda: case.pattern_payload(),
    )


def _counted_repeat_workload_signature(workload: Any) -> tuple[Any, ...]:
    return _compile_search_fullmatch_workload_signature(
        workload,
        pattern=lambda: workload.pattern_payload(),
        module_search_args=lambda: benchmark_test_support.freeze_signature_value(
            [
                workload.pattern_payload(),
                workload.haystack_payload(),
            ]
        ),
        pattern_fullmatch_args=lambda: benchmark_test_support.freeze_signature_value(
            [workload.haystack_payload()]
        ),
        error_label="counted-repeat benchmark",
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
    kwargs_signature = benchmark_test_support.freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", case.pattern, (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper in {"search", "sub", "subn"}:
        return (
            f"module.{case.helper}",
            None,
            benchmark_test_support.freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"fullmatch", "sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            benchmark_test_support.freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _grouped_alternation_workload_args(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return ()
    if workload.operation == "module.search":
        return benchmark_test_support.freeze_signature_value([workload.pattern, workload.haystack])
    if workload.operation == "pattern.fullmatch":
        return benchmark_test_support.freeze_signature_value([workload.haystack])
    if workload.operation in {"module.sub", "module.subn"}:
        args = [workload.pattern, workload.replacement, workload.haystack]
        if workload.count:
            args.append(workload.count)
        return benchmark_test_support.freeze_signature_value(args)
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [workload.replacement, workload.haystack]
        if workload.count:
            args.append(workload.count)
        return benchmark_test_support.freeze_signature_value(args)
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
    kwargs_signature = benchmark_test_support.freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "module_call" and case.helper in {"sub", "subn"}:
        return (
            f"module.{case.helper}",
            case.pattern,
            benchmark_test_support.freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            benchmark_test_support.freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None

SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS = (
    _source_tree_standard_benchmark_definitions()
)
