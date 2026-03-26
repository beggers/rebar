from __future__ import annotations

import re
from typing import Any

from rebar_harness import benchmarks
from tests.benchmarks import benchmark_test_support

_PATTERN_BOUNDARY_OPERATIONS = frozenset(
    {"pattern.search", "pattern.match", "pattern.fullmatch"}
)

PATTERN_BOUNDARY_MANIFEST_PATH = (
    benchmarks.BENCHMARK_WORKLOADS_ROOT / "pattern_boundary.py"
)

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

_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC = (
    benchmark_test_support._SourceTreeContractBuilderSpec(
        manifest_id="pattern-boundary",
        excluded_fields=_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS,
        timing_scope="pattern-helper-call",
    )
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


def _run_cpython_pattern_boundary_wrong_text_model_workload(
    workload: Any,
) -> object:
    helper_name = workload.operation.removeprefix("pattern.")
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    return getattr(compiled_pattern, helper_name)(workload.haystack_payload())


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


PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITION_NAMES = (
    "pattern-window-positional-indexlike",
    "pattern-window-keyword",
    "pattern-boundary-bounded-wildcard",
    "pattern-boundary-verbose-regression",
    "pattern-boundary-wrong-text-model",
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
        include_workload=(
            benchmark_test_support._is_pattern_window_positional_indexlike_workload
        ),
        correctness_case_signature=(
            benchmark_test_support._pattern_window_positional_indexlike_correctness_case_signature
        ),
        workload_signature=(
            benchmark_test_support._pattern_window_positional_indexlike_workload_signature
        ),
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
        include_workload=benchmark_test_support._is_pattern_keyword_window_workload,
        correctness_case_signature=(
            benchmark_test_support._pattern_keyword_window_correctness_case_signature
        ),
        workload_signature=benchmark_test_support._pattern_keyword_window_workload_signature,
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
        include_workload=benchmark_test_support._is_pattern_bounded_wildcard_workload,
        correctness_case_signature=(
            benchmark_test_support._pattern_bounded_wildcard_correctness_case_signature
        ),
        workload_signature=benchmark_test_support._pattern_bounded_wildcard_workload_signature,
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
        include_workload=benchmark_test_support._is_pattern_verbose_regression_workload,
        correctness_case_signature=(
            benchmark_test_support._pattern_verbose_regression_correctness_case_signature
        ),
        workload_signature=benchmark_test_support._pattern_verbose_regression_workload_signature,
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
