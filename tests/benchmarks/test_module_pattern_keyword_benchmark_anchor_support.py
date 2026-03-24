from __future__ import annotations

import pathlib
import re
from types import SimpleNamespace
from typing import Any

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    build_callable,
    load_manifest,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks.benchmark_test_support import (
    _record_numeric_materialization_fields,
    _write_test_manifest,
    synthetic_workload,
)
from tests.benchmarks import (
    module_pattern_keyword_benchmark_anchor_support as support,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    run_benchmark_workload_with_cpython,
)
from tests.python.fixture_parity_support import IndexLike
from tests.python.fixture_parity_support import assert_match_result_parity


def _module_pattern_case(
    *,
    helper: str,
    operation: str,
    args: tuple[object, ...],
    kwargs: dict[str, object] | None = None,
    pattern: str = "abc",
    flags: int = 0,
    text_model: str | None = "str",
    use_compiled_pattern: bool = False,
) -> object:
    pattern_value = pattern.encode() if text_model == "bytes" else pattern
    return SimpleNamespace(
        helper=helper,
        operation=operation,
        args=args,
        kwargs={} if kwargs is None else kwargs,
        pattern=pattern,
        flags=flags,
        text_model=text_model,
        use_compiled_pattern=use_compiled_pattern,
        pattern_payload=lambda: pattern_value,
    )


def test_module_keyword_success_workload_and_case_signatures_stay_pinned() -> None:
    workload = synthetic_workload(
        manifest_id="module-pattern-boundary",
        workload_id="module-search-flags-keyword",
        operation="module.search",
        haystack="zabc",
        kwargs={"flags": {"type": "indexlike", "value": 2}},
        flags=2,
    )
    case = _module_pattern_case(
        helper="search",
        operation="module_call",
        args=("zabc",),
        kwargs={"flags": IndexLike(2)},
        flags=2,
    )

    assert support._is_module_workflow_keyword_flags_workload(workload)
    assert support._module_workflow_keyword_workload_args(workload) == ("zabc",)
    assert support._module_workflow_keyword_workload_signature(workload) == (
        "module.search",
        "abc",
        ("zabc",),
        (("flags", "indexlike", 2),),
        2,
        "str",
    )
    assert support._module_workflow_keyword_correctness_case_signature(case) == (
        "module.search",
        "abc",
        ("zabc",),
        (("flags", "indexlike", 2),),
        2,
        "str",
    )


def test_module_keyword_error_workload_stays_pinned() -> None:
    workload = synthetic_workload(
        manifest_id="module-pattern-boundary",
        workload_id="module-search-duplicate-flags-keyword",
        operation="module.search",
        haystack="zabc",
        kwargs={"flags": {"type": "indexlike", "value": 4}},
        expected_exception={
            "type": "TypeError",
            "message_substring": "multiple values for argument 'flags'",
        },
        flags=4,
    )

    assert support._is_module_workflow_keyword_error_workload(workload)
    assert support._module_workflow_keyword_workload_args(workload) == ("zabc", 4)
    assert support._module_workflow_keyword_workload_signature(workload) == (
        "module.search",
        "abc",
        ("zabc", 4),
        (("flags", "indexlike", 4),),
        4,
        "str",
    )


def test_pattern_window_positional_indexlike_workload_and_case_signatures_stay_pinned() -> None:
    workload = synthetic_workload(
        manifest_id="module-pattern-boundary",
        workload_id="pattern-finditer-window-indexlike",
        operation="pattern.finditer",
        haystack="zabcabc",
        categories=["positional-window", "indexlike"],
        pos={"type": "indexlike", "value": 1},
        endpos={"type": "indexlike", "value": 6},
    )
    case = _module_pattern_case(
        helper="finditer",
        operation="pattern_call",
        args=("zabcabc", IndexLike(1), IndexLike(6)),
    )

    assert support._is_pattern_window_positional_indexlike_workload(workload)
    assert support._pattern_window_positional_indexlike_workload_args(workload) == (
        "zabcabc",
        {"type": "indexlike", "value": 1},
        {"type": "indexlike", "value": 6},
    )
    assert support._pattern_window_positional_indexlike_workload_signature(
        workload
    ) == (
        "finditer",
        "abc",
        (("str", "zabcabc"), ("indexlike", 1), ("indexlike", 6)),
        "str",
    )
    assert support._pattern_window_positional_indexlike_correctness_case_signature(
        case
    ) == (
        "finditer",
        "abc",
        (("str", "zabcabc"), ("indexlike", 1), ("indexlike", 6)),
        "str",
    )


def test_pattern_keyword_window_workload_and_case_signatures_stay_pinned() -> None:
    workload = synthetic_workload(
        manifest_id="module-pattern-boundary",
        workload_id="pattern-findall-bool-window-keyword",
        operation="pattern.findall",
        haystack="zabcabc",
        kwargs={"endpos": True},
        categories=["keyword"],
    )
    case = _module_pattern_case(
        helper="findall",
        operation="pattern_call",
        args=("zabcabc",),
        kwargs={"endpos": True},
    )

    assert support._is_pattern_keyword_window_workload(workload)
    assert support._pattern_keyword_window_workload_signature(workload) == (
        "pattern.findall",
        "abc",
        ("zabcabc",),
        (("endpos", "bool", True),),
        0,
        "str",
    )
    assert support._pattern_keyword_window_correctness_case_signature(case) == (
        "pattern.findall",
        "abc",
        ("zabcabc",),
        (("endpos", "bool", True),),
        0,
        "str",
    )


def test_standard_benchmark_manifest_preserves_pattern_window_indexlike_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-pattern-window-indexlike-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
        },
        "workloads": [
            {
                "id": "pattern-search-pos-indexlike-contract-str",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "abc",
                "haystack": "zabcabc",
                "pos": {
                    "type": "indexlike",
                    "value": 2,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.search positional indexlike descriptors unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-search-endpos-indexlike-contract-bytes",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "abc",
                "haystack": "zabcabc",
                "pos": 0,
                "endpos": {
                    "type": "indexlike",
                    "value": 4,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.search endpos indexlike descriptors unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-match-window-indexlike-positional-contract-bytes",
                "bucket": "pattern-match",
                "family": "module",
                "operation": "pattern.match",
                "pattern": "abc",
                "haystack": "zabc",
                "pos": {
                    "type": "indexlike",
                    "value": 1,
                },
                "endpos": {
                    "type": "indexlike",
                    "value": 4,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.match positional pos/endpos indexlike descriptors unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-fullmatch-window-indexlike-contract-bytes",
                "bucket": "pattern-fullmatch",
                "family": "module",
                "operation": "pattern.fullmatch",
                "pattern": "abc",
                "haystack": "zabc",
                "pos": {
                    "type": "indexlike",
                    "value": 1,
                },
                "endpos": {
                    "type": "indexlike",
                    "value": 4,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.fullmatch window indexlike descriptors unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-findall-window-indexlike-contract-str",
                "bucket": "pattern-findall",
                "family": "module",
                "operation": "pattern.findall",
                "pattern": "abc",
                "haystack": "zabcabcabcz",
                "pos": {
                    "type": "indexlike",
                    "value": 1,
                },
                "endpos": {
                    "type": "indexlike",
                    "value": 7,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.findall window indexlike descriptors unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-finditer-window-indexlike-contract-bytes",
                "bucket": "pattern-finditer",
                "family": "module",
                "operation": "pattern.finditer",
                "pattern": "abc",
                "haystack": "zabcabcabcz",
                "pos": {
                    "type": "indexlike",
                    "value": 1,
                },
                "endpos": {
                    "type": "indexlike",
                    "value": 7,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.finditer window indexlike descriptors unresolved until helper invocation."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_pattern_window_indexlike_contract.py",
        manifest_source,
    )
    (
        search_pos_workload,
        search_endpos_workload,
        match_window_workload,
        fullmatch_window_workload,
        findall_window_workload,
        finditer_window_workload,
    ) = load_manifest(manifest_path).workloads

    assert search_pos_workload.pos == {
        "type": "indexlike",
        "value": 2,
    }
    assert search_pos_workload.endpos is None
    round_tripped_search_pos = workload_from_payload(
        workload_to_payload(search_pos_workload)
    )
    assert round_tripped_search_pos.pos_argument().__index__() == 2
    assert round_tripped_search_pos.endpos_argument() is None
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_search_pos),
        re.compile("abc").search("zabcabc", 2),
        check_regs=True,
    )

    assert search_endpos_workload.pos == 0
    assert search_endpos_workload.endpos == {
        "type": "indexlike",
        "value": 4,
    }
    round_tripped_search_endpos = workload_from_payload(
        workload_to_payload(search_endpos_workload)
    )
    assert round_tripped_search_endpos.pos_argument() == 0
    assert round_tripped_search_endpos.endpos_argument().__index__() == 4
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_search_endpos),
        re.compile(b"abc").search(b"zabcabc", 0, 4),
        check_regs=True,
    )

    assert match_window_workload.pos == {
        "type": "indexlike",
        "value": 1,
    }
    assert match_window_workload.endpos == {
        "type": "indexlike",
        "value": 4,
    }
    round_tripped_match = workload_from_payload(
        workload_to_payload(match_window_workload)
    )
    assert round_tripped_match.pos_argument().__index__() == 1
    assert round_tripped_match.endpos_argument().__index__() == 4
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_match),
        re.compile(b"abc").match(b"zabc", 1, 4),
        check_regs=True,
    )

    assert fullmatch_window_workload.pos == {
        "type": "indexlike",
        "value": 1,
    }
    assert fullmatch_window_workload.endpos == {
        "type": "indexlike",
        "value": 4,
    }
    round_tripped_fullmatch = workload_from_payload(
        workload_to_payload(fullmatch_window_workload)
    )
    assert round_tripped_fullmatch.pos_argument().__index__() == 1
    assert round_tripped_fullmatch.endpos_argument().__index__() == 4
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_fullmatch),
        re.compile(b"abc").fullmatch(b"zabc", 1, 4),
        check_regs=True,
    )

    assert findall_window_workload.pos == {
        "type": "indexlike",
        "value": 1,
    }
    assert findall_window_workload.endpos == {
        "type": "indexlike",
        "value": 7,
    }
    round_tripped_findall = workload_from_payload(
        workload_to_payload(findall_window_workload)
    )
    assert round_tripped_findall.pos_argument().__index__() == 1
    assert round_tripped_findall.endpos_argument().__index__() == 7
    assert run_benchmark_workload_with_cpython(round_tripped_findall) == [
        "abc",
        "abc",
    ]

    assert finditer_window_workload.pos == {
        "type": "indexlike",
        "value": 1,
    }
    assert finditer_window_workload.endpos == {
        "type": "indexlike",
        "value": 7,
    }
    round_tripped_finditer = workload_from_payload(
        workload_to_payload(finditer_window_workload)
    )
    assert round_tripped_finditer.pos_argument().__index__() == 1
    assert round_tripped_finditer.endpos_argument().__index__() == 7
    observed_finditer = run_benchmark_workload_with_cpython(round_tripped_finditer)
    expected_finditer = list(re.compile(b"abc").finditer(b"zabcabcabcz", 1, 7))
    assert len(observed_finditer) == len(expected_finditer) == 2
    for observed_match, expected_match in zip(
        observed_finditer,
        expected_finditer,
        strict=True,
    ):
        assert_match_result_parity(
            "stdlib",
            observed_match,
            expected_match,
            check_regs=True,
        )


@pytest.mark.parametrize(
    ("kwargs_payload", "operation", "pos", "endpos", "error_pattern"),
    (
        pytest.param(
            ["pos"],
            "pattern.search",
            None,
            None,
            "benchmark workload kwargs must be an object",
            id="non-object",
        ),
        pytest.param(
            {"pos": 1},
            "module.split",
            None,
            None,
            re.escape(
                "benchmark workload kwargs for module.split only supports the "
                "`maxsplit` key; got unsupported keys ['pos']"
            ),
            id="unsupported-module-key",
        ),
        pytest.param(
            {"count": 1},
            "module.search",
            None,
            None,
            re.escape(
                "benchmark workload kwargs for module.search only supports the "
                "`flags` key; got unsupported keys ['count']"
            ),
            id="unsupported-module-search-key",
        ),
        pytest.param(
            {"flags": 1},
            "module.findall",
            None,
            None,
            re.escape(
                "benchmark workload kwargs are only supported for pattern.search, "
                "pattern.match, pattern.fullmatch, pattern.findall, "
                "pattern.finditer, pattern.split, pattern.sub, pattern.subn, "
                "module.search, module.match, module.fullmatch, module.split, "
                "module.sub, and module.subn"
            ),
            id="unsupported-operation",
        ),
        pytest.param(
            {"endpos": 4},
            "pattern.search",
            0,
            None,
            re.escape(
                "benchmark workload cannot mix top-level pos/endpos fields with "
                "keyword kwargs carriers"
            ),
            id="mixed-carriers",
        ),
    ),
)
def test_standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points(
    tmp_path: pathlib.Path,
    kwargs_payload: object,
    operation: str,
    pos: object,
    endpos: object,
    error_pattern: str,
) -> None:
    manifest_source = f"""
    MANIFEST = {{
        "schema_version": 1,
        "manifest_id": "python-benchmark-invalid-pattern-keyword-window-contract",
        "workloads": [
            {{
                "id": "pattern-invalid-keyword-window-contract",
                "bucket": "pattern-search",
                "family": "module",
                "operation": {operation!r},
                "pattern": "abc",
                "haystack": "zabcabc",
                "pos": {pos!r},
                "endpos": {endpos!r},
                "kwargs": {kwargs_payload!r},
            }},
        ],
    }}
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_invalid_pattern_keyword_window_contract.py",
        manifest_source,
    )

    with pytest.raises(ValueError, match=error_pattern):
        load_manifest(manifest_path)

    with pytest.raises(ValueError, match=error_pattern):
        workload_from_payload(
            {
                "manifest_id": "python-benchmark-invalid-pattern-keyword-window-contract",
                "workload_id": "pattern-invalid-keyword-window-contract",
                "bucket": "pattern-search",
                "family": "module",
                "operation": operation,
                "pattern": "abc",
                "haystack": "zabcabc",
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "pos": pos,
                "endpos": endpos,
                "kwargs": kwargs_payload,
                "text_model": "str",
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


@pytest.mark.parametrize(
    ("operation", "kwargs_payload", "expected_kwargs"),
    (
        pytest.param(
            "module.subn",
            {
                "missing": 1,
                "count": {"type": "indexlike", "value": 2},
            },
            {
                "count": {"type": "indexlike", "value": 2},
                "missing": 1,
            },
            id="module-subn-unexpected-keyword-passthrough",
        ),
        pytest.param(
            "pattern.split",
            {
                "missing": {"type": "indexlike", "value": 1},
                "maxsplit": False,
            },
            {
                "maxsplit": False,
                "missing": {"type": "indexlike", "value": 1},
            },
            id="pattern-split-unexpected-keyword-passthrough",
        ),
    ),
)
def test_benchmark_keyword_kwargs_normalization_preserves_expected_exception_passthrough_rows(
    operation: str,
    kwargs_payload: dict[str, object],
    expected_kwargs: dict[str, object],
) -> None:
    assert benchmarks.normalize_keyword_workload_arguments(
        kwargs_payload,
        operation=operation,
        expected_exception={
            "type": "TypeError",
            "message_substring": "unexpected keyword argument 'missing'",
        },
    ) == expected_kwargs


@pytest.mark.parametrize(
    ("operation", "kwargs_payload", "error_pattern"),
    (
        pytest.param(
            "pattern.search",
            {"missing": 1},
            re.escape(
                "benchmark workload kwargs for pattern.search only supports the "
                "`endpos` and `pos` keys; got unsupported keys ['missing']"
            ),
            id="pattern-search-still-rejects-unexpected-keyword",
        ),
        pytest.param(
            "module.compile",
            {"missing": 1},
            re.escape(
                "benchmark workload kwargs are only supported for pattern.search, "
                "pattern.match, pattern.fullmatch, pattern.findall, "
                "pattern.finditer, pattern.split, pattern.sub, pattern.subn, "
                "module.search, module.match, module.fullmatch, module.split, "
                "module.sub, and module.subn"
            ),
            id="module-compile-still-rejects-generic-kwargs",
        ),
    ),
)
def test_benchmark_keyword_kwargs_normalization_does_not_expand_expected_exception_passthrough(
    operation: str,
    kwargs_payload: dict[str, object],
    error_pattern: str,
) -> None:
    with pytest.raises(ValueError, match=error_pattern):
        benchmarks.normalize_keyword_workload_arguments(
            kwargs_payload,
            operation=operation,
            expected_exception={
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
        )


@pytest.mark.parametrize(
    (
        "workload_payload",
        "expected_field_names",
        "expected_index_calls",
        "expected_result",
    ),
    (
        pytest.param(
            {
                "manifest_id": "python-benchmark-pattern-keyword-window-contract",
                "workload_id": "pattern-findall-window-keyword-contract-str",
                "bucket": "pattern-findall",
                "family": "module",
                "operation": "pattern.findall",
                "pattern": "abc",
                "haystack": "zabcabcz",
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "kwargs": {
                    "pos": 1,
                    "endpos": 7,
                },
                "text_model": "str",
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            },
            ["kwargs.endpos", "kwargs.pos"],
            [],
            ["abc", "abc"],
            id="pattern-findall-window-keyword-str",
        ),
        pytest.param(
            {
                "manifest_id": "python-benchmark-pattern-keyword-window-contract",
                "workload_id": "pattern-findall-window-indexlike-keyword-contract-str",
                "bucket": "pattern-findall",
                "family": "module",
                "operation": "pattern.findall",
                "pattern": "abc",
                "haystack": "zabcabcabcz",
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "kwargs": {
                    "pos": {"type": "indexlike", "value": 1},
                    "endpos": {"type": "indexlike", "value": 7},
                },
                "text_model": "str",
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            },
            ["kwargs.endpos", "kwargs.pos"],
            [("kwargs.pos", 1), ("kwargs.endpos", 7)],
            re.compile("abc").findall("zabcabcabcz", pos=1, endpos=7),
            id="pattern-findall-window-indexlike-keyword-str",
        ),
        pytest.param(
            {
                "manifest_id": "python-benchmark-pattern-keyword-window-contract",
                "workload_id": "pattern-fullmatch-window-indexlike-keyword-contract-bytes",
                "bucket": "pattern-fullmatch",
                "family": "module",
                "operation": "pattern.fullmatch",
                "pattern": "abc",
                "haystack": "zabc",
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "kwargs": {
                    "pos": {"type": "indexlike", "value": 1},
                    "endpos": {"type": "indexlike", "value": 4},
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            },
            ["kwargs.endpos", "kwargs.pos"],
            [("kwargs.pos", 1), ("kwargs.endpos", 4)],
            re.compile(b"abc").fullmatch(b"zabc", pos=1, endpos=4),
            id="pattern-fullmatch-window-indexlike-keyword-bytes",
        ),
        pytest.param(
            {
                "manifest_id": "python-benchmark-pattern-keyword-window-contract",
                "workload_id": "pattern-finditer-window-keyword-contract-bytes",
                "bucket": "pattern-finditer",
                "family": "module",
                "operation": "pattern.finditer",
                "pattern": "abc",
                "haystack": "zabcabcz",
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "kwargs": {
                    "pos": 1,
                    "endpos": 7,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            },
            ["kwargs.endpos", "kwargs.pos"],
            [],
            list(re.compile(b"abc").finditer(b"zabcabcz", pos=1, endpos=7)),
            id="pattern-finditer-window-keyword-bytes",
        ),
        pytest.param(
            {
                "manifest_id": "python-benchmark-pattern-keyword-window-contract",
                "workload_id": "pattern-finditer-window-indexlike-keyword-contract-bytes",
                "bucket": "pattern-finditer",
                "family": "module",
                "operation": "pattern.finditer",
                "pattern": "abc",
                "haystack": "zabcabcabcz",
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "kwargs": {
                    "pos": {"type": "indexlike", "value": 1},
                    "endpos": {"type": "indexlike", "value": 7},
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            },
            ["kwargs.endpos", "kwargs.pos"],
            [("kwargs.pos", 1), ("kwargs.endpos", 7)],
            list(re.compile(b"abc").finditer(b"zabcabcabcz", pos=1, endpos=7)),
            id="pattern-finditer-window-indexlike-keyword-bytes",
        ),
        pytest.param(
            {
                "manifest_id": "python-benchmark-pattern-keyword-window-contract",
                "workload_id": "pattern-finditer-bool-window-keyword-contract-bytes",
                "bucket": "pattern-finditer",
                "family": "module",
                "operation": "pattern.finditer",
                "pattern": "abc",
                "haystack": "zabcabcz",
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "kwargs": {
                    "pos": True,
                    "endpos": 7,
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            },
            ["kwargs.endpos", "kwargs.pos"],
            [],
            list(re.compile(b"abc").finditer(b"zabcabcz", pos=True, endpos=7)),
            id="pattern-finditer-bool-window-keyword-bytes",
        ),
    ),
)
def test_pattern_helper_keyword_kwargs_materialize_at_callback_time(
    monkeypatch,
    workload_payload,
    expected_field_names,
    expected_index_calls,
    expected_result,
) -> None:
    workload = workload_from_payload(workload_payload)
    observed_field_names: list[str] = []
    index_calls: list[tuple[str, int]] = []
    original_materialize = benchmarks.materialize_numeric_workload_argument

    class _RecordingIndexLike:
        def __init__(self, field_name: str, value: int) -> None:
            self.field_name = field_name
            self.value = value

        def __index__(self) -> int:
            index_calls.append((self.field_name, self.value))
            return self.value

    def record_numeric_materialization(value: Any, *, field_name: str) -> Any:
        observed_field_names.append(field_name)
        normalized = benchmarks.normalize_numeric_workload_argument(
            value,
            field_name=field_name,
        )
        if isinstance(normalized, dict) and normalized.get("type") == "indexlike":
            return _RecordingIndexLike(field_name, int(normalized["value"]))
        return original_materialize(value, field_name=field_name)

    monkeypatch.setattr(
        benchmarks,
        "materialize_numeric_workload_argument",
        record_numeric_materialization,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        observed_result = callback()

        assert observed_field_names == expected_field_names
        assert index_calls == expected_index_calls
        if workload.operation == "pattern.finditer":
            assert len(observed_result) == len(expected_result) == 2
            for observed_match, expected_match in zip(
                observed_result,
                expected_result,
                strict=True,
            ):
                assert_match_result_parity(
                    "stdlib",
                    observed_match,
                    expected_match,
                    check_regs=True,
                )
        elif workload.operation == "pattern.findall":
            assert observed_result == expected_result
        else:
            assert_match_result_parity(
                "stdlib",
                observed_result,
                expected_result,
                check_regs=True,
            )
    finally:
        re.purge()


@pytest.mark.parametrize(
    ("workload_payload", "expected_match", "expected_field_names", "expected_index_calls"),
    (
        pytest.param(
            {
                "manifest_id": "python-benchmark-pattern-keyword-window-contract",
                "workload_id": "pattern-search-bool-endpos-keyword-contract-str",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "z",
                "haystack": "zabcabc",
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "kwargs": {"endpos": True},
                "text_model": "str",
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            },
            re.compile("z").search("zabcabc", endpos=True),
            ["kwargs.endpos"],
            [],
            id="pattern-search-bool-endpos-keyword-str",
        ),
        pytest.param(
            {
                "manifest_id": "python-benchmark-pattern-keyword-window-contract",
                "workload_id": "pattern-search-endpos-keyword-contract-bytes",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "abc",
                "haystack": "zabcabc",
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "kwargs": {"endpos": 4},
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            },
            re.compile(b"abc").search(b"zabcabc", endpos=4),
            ["kwargs.endpos"],
            [],
            id="pattern-search-endpos-keyword-bytes",
        ),
        pytest.param(
            {
                "manifest_id": "python-benchmark-pattern-keyword-window-contract",
                "workload_id": "pattern-search-pos-indexlike-keyword-contract-str",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "abc",
                "haystack": "zabcabc",
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "kwargs": {
                    "pos": {"type": "indexlike", "value": 2},
                },
                "text_model": "str",
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            },
            re.compile("abc").search("zabcabc", pos=2),
            ["kwargs.pos"],
            [2],
            id="pattern-search-pos-indexlike-keyword-str",
        ),
        pytest.param(
            {
                "manifest_id": "python-benchmark-pattern-keyword-window-contract",
                "workload_id": "pattern-search-endpos-indexlike-keyword-contract-bytes",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "abc",
                "haystack": "zabcabc",
                "flags": 0,
                "count": 0,
                "maxsplit": 0,
                "kwargs": {
                    "endpos": {"type": "indexlike", "value": 4},
                },
                "text_model": "bytes",
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "warmup_iterations": 1,
                "sample_iterations": 1,
                "timed_samples": 1,
                "notes": [],
                "categories": [],
                "syntax_features": [],
                "smoke": False,
            },
            re.compile(b"abc").search(b"zabcabc", endpos=4),
            ["kwargs.endpos"],
            [4],
            id="pattern-search-endpos-indexlike-bytes",
        ),
    ),
)
def test_pattern_helper_keyword_kwargs_materialize_at_callback_time_for_search_endpos_rows(
    monkeypatch,
    workload_payload,
    expected_match,
    expected_field_names,
    expected_index_calls,
) -> None:
    workload = workload_from_payload(workload_payload)
    observed_field_names: list[str] = []
    index_calls: list[int] = []
    original_materialize = benchmarks.materialize_numeric_workload_argument

    class _RecordingIndexLike:
        def __init__(self, value: int) -> None:
            self.value = value

        def __index__(self) -> int:
            index_calls.append(self.value)
            return self.value

    def record_numeric_materialization(value: Any, *, field_name: str) -> Any:
        observed_field_names.append(field_name)
        normalized = benchmarks.normalize_numeric_workload_argument(
            value,
            field_name=field_name,
        )
        if isinstance(normalized, dict) and normalized.get("type") == "indexlike":
            return _RecordingIndexLike(int(normalized["value"]))
        return original_materialize(value, field_name=field_name)

    monkeypatch.setattr(
        benchmarks,
        "materialize_numeric_workload_argument",
        record_numeric_materialization,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        observed_match = callback()

        assert observed_field_names == expected_field_names
        assert index_calls == expected_index_calls
        assert_match_result_parity(
            "stdlib",
            observed_match,
            expected_match,
            check_regs=True,
        )
    finally:
        re.purge()


@pytest.mark.parametrize(
    ("operation", "haystack", "text_model"),
    (
        pytest.param(
            "module.search",
            "zAbc",
            "str",
            id="module-search-flags-keyword",
        ),
        pytest.param(
            "module.match",
            "Abc",
            "bytes",
            id="module-match-flags-keyword",
        ),
        pytest.param(
            "module.fullmatch",
            "Abc",
            "str",
            id="module-fullmatch-flags-keyword",
        ),
    ),
)
def test_module_helper_workflow_keyword_flags_materialize_at_callback_time(
    monkeypatch,
    operation: str,
    haystack: str,
    text_model: str,
) -> None:
    workload = workload_from_payload(
        {
            "manifest_id": "python-benchmark-module-workflow-keyword-flags-contract",
            "workload_id": f"{operation}-keyword-flags-materialization-contract",
            "bucket": operation.replace("module.", "module-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "flags": 0,
            "count": 0,
            "maxsplit": 0,
            "kwargs": {"flags": 2},
            "text_model": text_model,
            "cache_mode": "purged",
            "timing_scope": "module-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)

    helper_name = operation.removeprefix("module.")
    expected_result = getattr(re, helper_name)(
        workload.pattern_payload(),
        workload.haystack_payload(),
        flags=re.IGNORECASE,
    )

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        observed_result = callback()

        assert observed_field_names == ["kwargs.flags"]
        assert_match_result_parity(
            "stdlib",
            observed_result,
            expected_result,
            check_regs=True,
        )
    finally:
        re.purge()


def test_standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-pattern-keyword-window-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
        },
        "workloads": [
            {
                "id": "pattern-search-pos-keyword-contract-str",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "abc",
                "haystack": "zabcabc",
                "kwargs": {
                    "pos": 2,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.search keyword pos carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-search-bool-endpos-keyword-contract-str",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "z",
                "haystack": "zabcabc",
                "text_model": "str",
                "kwargs": {
                    "endpos": True,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.search bool-backed endpos= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-search-endpos-keyword-contract-bytes",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "abc",
                "haystack": "zabcabc",
                "text_model": "bytes",
                "kwargs": {
                    "endpos": 4,
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.search endpos= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-search-pos-indexlike-keyword-contract-str",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "abc",
                "haystack": "zabcabc",
                "text_model": "str",
                "kwargs": {
                    "pos": {
                        "type": "indexlike",
                        "value": 2,
                    },
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.search pos= __index__ keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-search-endpos-indexlike-keyword-contract-bytes",
                "bucket": "pattern-search",
                "family": "module",
                "operation": "pattern.search",
                "pattern": "abc",
                "haystack": "zabcabc",
                "text_model": "bytes",
                "kwargs": {
                    "endpos": {
                        "type": "indexlike",
                        "value": 4,
                    },
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.search endpos= __index__ keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-match-pos-keyword-contract-str",
                "bucket": "pattern-match",
                "family": "module",
                "operation": "pattern.match",
                "pattern": "abc",
                "haystack": "zabcabc",
                "kwargs": {
                    "pos": 1,
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.match keyword pos carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-match-bool-pos-keyword-contract-str",
                "bucket": "pattern-match",
                "family": "module",
                "operation": "pattern.match",
                "pattern": "abc",
                "haystack": "zabcabc",
                "text_model": "str",
                "kwargs": {
                    "pos": True,
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.match bool-backed pos= keyword carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-match-window-indexlike-keyword-contract-bytes",
                "bucket": "pattern-match",
                "family": "module",
                "operation": "pattern.match",
                "pattern": "abc",
                "haystack": "zabc",
                "text_model": "bytes",
                "kwargs": {
                    "pos": {
                        "type": "indexlike",
                        "value": 1,
                    },
                    "endpos": {
                        "type": "indexlike",
                        "value": 4,
                    },
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.match keyword pos/endpos indexlike carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-fullmatch-window-keyword-contract-bytes",
                "bucket": "pattern-fullmatch",
                "family": "module",
                "operation": "pattern.fullmatch",
                "pattern": "abc",
                "haystack": "zabc",
                "text_model": "bytes",
                "kwargs": {
                    "pos": 1,
                    "endpos": 4,
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.fullmatch keyword pos/endpos carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-fullmatch-window-indexlike-keyword-contract-bytes",
                "bucket": "pattern-fullmatch",
                "family": "module",
                "operation": "pattern.fullmatch",
                "pattern": "abc",
                "haystack": "zabc",
                "text_model": "bytes",
                "kwargs": {
                    "pos": {
                        "type": "indexlike",
                        "value": 1,
                    },
                    "endpos": {
                        "type": "indexlike",
                        "value": 4,
                    },
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.fullmatch keyword pos/endpos indexlike carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-findall-window-keyword-contract-str",
                "bucket": "pattern-findall",
                "family": "module",
                "operation": "pattern.findall",
                "pattern": "abc",
                "haystack": "zabcabcz",
                "kwargs": {
                    "pos": 1,
                    "endpos": 7,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.findall keyword pos/endpos carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-findall-window-indexlike-keyword-contract-str",
                "bucket": "pattern-findall",
                "family": "module",
                "operation": "pattern.findall",
                "pattern": "abc",
                "haystack": "zabcabcabcz",
                "kwargs": {
                    "pos": {
                        "type": "indexlike",
                        "value": 1,
                    },
                    "endpos": {
                        "type": "indexlike",
                        "value": 7,
                    },
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.findall keyword pos/endpos indexlike carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-findall-bool-window-keyword-contract-str",
                "bucket": "pattern-findall",
                "family": "module",
                "operation": "pattern.findall",
                "pattern": "abc",
                "haystack": "zabcabcz",
                "kwargs": {
                    "pos": True,
                    "endpos": 7,
                },
                "cache_mode": "warm",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.findall keyword bool/int carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-finditer-window-keyword-contract-bytes",
                "bucket": "pattern-finditer",
                "family": "module",
                "operation": "pattern.finditer",
                "pattern": "abc",
                "haystack": "zabcabcz",
                "text_model": "bytes",
                "kwargs": {
                    "pos": 1,
                    "endpos": 7,
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.finditer keyword pos/endpos carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-finditer-window-indexlike-keyword-contract-bytes",
                "bucket": "pattern-finditer",
                "family": "module",
                "operation": "pattern.finditer",
                "pattern": "abc",
                "haystack": "zabcabcabcz",
                "text_model": "bytes",
                "kwargs": {
                    "pos": {
                        "type": "indexlike",
                        "value": 1,
                    },
                    "endpos": {
                        "type": "indexlike",
                        "value": 7,
                    },
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.finditer keyword indexlike carriers unresolved until helper invocation."
                ],
            },
            {
                "id": "pattern-finditer-bool-window-keyword-contract-bytes",
                "bucket": "pattern-finditer",
                "family": "module",
                "operation": "pattern.finditer",
                "pattern": "abc",
                "haystack": "zabcabcz",
                "text_model": "bytes",
                "kwargs": {
                    "pos": True,
                    "endpos": 7,
                },
                "cache_mode": "purged",
                "timing_scope": "pattern-helper-call",
                "notes": [
                    "Ensures benchmark manifests keep Pattern.finditer bool-backed keyword carriers unresolved until helper invocation."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_pattern_keyword_window_contract.py",
        manifest_source,
    )
    (
        search_pos_workload,
        search_bool_endpos_workload,
        search_endpos_workload,
        search_pos_indexlike_workload,
        search_endpos_indexlike_workload,
        match_pos_workload,
        match_bool_pos_workload,
        match_window_workload,
        fullmatch_window_workload,
        fullmatch_window_indexlike_workload,
        findall_window_keyword_workload,
        findall_window_indexlike_workload,
        findall_window_bool_workload,
        finditer_window_keyword_workload,
        finditer_window_indexlike_workload,
        finditer_window_bool_workload,
    ) = load_manifest(manifest_path).workloads

    assert search_pos_workload.pos is None
    assert search_pos_workload.endpos is None
    assert search_pos_workload.kwargs == {"pos": 2}
    round_tripped_search_pos = workload_from_payload(
        workload_to_payload(search_pos_workload)
    )
    assert round_tripped_search_pos.kwargs == {"pos": 2}
    assert round_tripped_search_pos.keyword_arguments() == {"pos": 2}
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_search_pos),
        re.compile("abc").search("zabcabc", pos=2),
        check_regs=True,
    )

    assert search_bool_endpos_workload.pos is None
    assert search_bool_endpos_workload.endpos is None
    assert search_bool_endpos_workload.kwargs == {"endpos": True}
    assert type(search_bool_endpos_workload.kwargs["endpos"]) is bool
    round_tripped_search_bool_endpos = workload_from_payload(
        workload_to_payload(search_bool_endpos_workload)
    )
    assert round_tripped_search_bool_endpos.kwargs == {"endpos": True}
    assert type(round_tripped_search_bool_endpos.kwargs["endpos"]) is bool
    materialized_search_bool_endpos_kwargs = (
        round_tripped_search_bool_endpos.keyword_arguments()
    )
    assert materialized_search_bool_endpos_kwargs == {"endpos": True}
    assert materialized_search_bool_endpos_kwargs["endpos"] is True
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_search_bool_endpos),
        re.compile("z").search("zabcabc", endpos=True),
        check_regs=True,
    )

    assert search_endpos_workload.pos is None
    assert search_endpos_workload.endpos is None
    assert search_endpos_workload.kwargs == {"endpos": 4}
    round_tripped_search_endpos = workload_from_payload(
        workload_to_payload(search_endpos_workload)
    )
    assert round_tripped_search_endpos.kwargs == {"endpos": 4}
    assert round_tripped_search_endpos.keyword_arguments() == {"endpos": 4}
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_search_endpos),
        re.compile(b"abc").search(b"zabcabc", endpos=4),
        check_regs=True,
    )

    assert search_pos_indexlike_workload.pos is None
    assert search_pos_indexlike_workload.endpos is None
    assert search_pos_indexlike_workload.kwargs == {
        "pos": {"type": "indexlike", "value": 2}
    }
    round_tripped_search_pos_indexlike = workload_from_payload(
        workload_to_payload(search_pos_indexlike_workload)
    )
    assert round_tripped_search_pos_indexlike.kwargs == {
        "pos": {"type": "indexlike", "value": 2}
    }
    materialized_search_pos_indexlike_kwargs = (
        round_tripped_search_pos_indexlike.keyword_arguments()
    )
    assert materialized_search_pos_indexlike_kwargs["pos"].__index__() == 2
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_search_pos_indexlike),
        re.compile("abc").search(
            "zabcabc",
            pos=materialized_search_pos_indexlike_kwargs["pos"],
        ),
        check_regs=True,
    )

    assert search_endpos_indexlike_workload.pos is None
    assert search_endpos_indexlike_workload.endpos is None
    assert search_endpos_indexlike_workload.kwargs == {
        "endpos": {"type": "indexlike", "value": 4}
    }
    round_tripped_search_endpos_indexlike = workload_from_payload(
        workload_to_payload(search_endpos_indexlike_workload)
    )
    assert round_tripped_search_endpos_indexlike.kwargs == {
        "endpos": {"type": "indexlike", "value": 4}
    }
    materialized_search_endpos_indexlike_kwargs = (
        round_tripped_search_endpos_indexlike.keyword_arguments()
    )
    assert materialized_search_endpos_indexlike_kwargs["endpos"].__index__() == 4
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_search_endpos_indexlike),
        re.compile(b"abc").search(
            b"zabcabc",
            endpos=materialized_search_endpos_indexlike_kwargs["endpos"],
        ),
        check_regs=True,
    )

    assert match_pos_workload.pos is None
    assert match_pos_workload.endpos is None
    assert match_pos_workload.kwargs == {"pos": 1}
    round_tripped_match_pos = workload_from_payload(
        workload_to_payload(match_pos_workload)
    )
    assert round_tripped_match_pos.kwargs == {"pos": 1}
    assert round_tripped_match_pos.keyword_arguments() == {"pos": 1}
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_match_pos),
        re.compile("abc").match("zabcabc", pos=1),
        check_regs=True,
    )

    assert match_bool_pos_workload.pos is None
    assert match_bool_pos_workload.endpos is None
    assert match_bool_pos_workload.kwargs == {"pos": True}
    assert type(match_bool_pos_workload.kwargs["pos"]) is bool
    round_tripped_match_bool_pos = workload_from_payload(
        workload_to_payload(match_bool_pos_workload)
    )
    assert round_tripped_match_bool_pos.kwargs == {"pos": True}
    assert type(round_tripped_match_bool_pos.kwargs["pos"]) is bool
    materialized_match_bool_pos_kwargs = (
        round_tripped_match_bool_pos.keyword_arguments()
    )
    assert materialized_match_bool_pos_kwargs == {"pos": True}
    assert materialized_match_bool_pos_kwargs["pos"] is True
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_match_bool_pos),
        re.compile("abc").match("zabcabc", pos=True),
        check_regs=True,
    )

    assert match_window_workload.pos is None
    assert match_window_workload.endpos is None
    assert match_window_workload.kwargs == {
        "endpos": {"type": "indexlike", "value": 4},
        "pos": {"type": "indexlike", "value": 1},
    }
    round_tripped_match_window = workload_from_payload(
        workload_to_payload(match_window_workload)
    )
    assert round_tripped_match_window.kwargs == {
        "endpos": {"type": "indexlike", "value": 4},
        "pos": {"type": "indexlike", "value": 1},
    }
    materialized_match_window_kwargs = round_tripped_match_window.keyword_arguments()
    assert materialized_match_window_kwargs["pos"].__index__() == 1
    assert materialized_match_window_kwargs["endpos"].__index__() == 4
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_match_window),
        re.compile(b"abc").match(b"zabc", pos=1, endpos=4),
        check_regs=True,
    )

    assert fullmatch_window_workload.pos is None
    assert fullmatch_window_workload.endpos is None
    assert fullmatch_window_workload.kwargs == {"endpos": 4, "pos": 1}
    round_tripped_fullmatch = workload_from_payload(
        workload_to_payload(fullmatch_window_workload)
    )
    assert round_tripped_fullmatch.kwargs == {"endpos": 4, "pos": 1}
    assert round_tripped_fullmatch.keyword_arguments() == {"endpos": 4, "pos": 1}
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(round_tripped_fullmatch),
        re.compile(b"abc").fullmatch(b"zabc", pos=1, endpos=4),
        check_regs=True,
    )

    assert fullmatch_window_indexlike_workload.pos is None
    assert fullmatch_window_indexlike_workload.endpos is None
    assert fullmatch_window_indexlike_workload.kwargs == {
        "endpos": {"type": "indexlike", "value": 4},
        "pos": {"type": "indexlike", "value": 1},
    }
    round_tripped_fullmatch_window_indexlike = workload_from_payload(
        workload_to_payload(fullmatch_window_indexlike_workload)
    )
    assert round_tripped_fullmatch_window_indexlike.kwargs == {
        "endpos": {"type": "indexlike", "value": 4},
        "pos": {"type": "indexlike", "value": 1},
    }
    materialized_fullmatch_window_indexlike_kwargs = (
        round_tripped_fullmatch_window_indexlike.keyword_arguments()
    )
    assert materialized_fullmatch_window_indexlike_kwargs["pos"].__index__() == 1
    assert materialized_fullmatch_window_indexlike_kwargs["endpos"].__index__() == 4
    assert_match_result_parity(
        "stdlib",
        run_benchmark_workload_with_cpython(
            round_tripped_fullmatch_window_indexlike
        ),
        re.compile(b"abc").fullmatch(
            b"zabc",
            pos=materialized_fullmatch_window_indexlike_kwargs["pos"],
            endpos=materialized_fullmatch_window_indexlike_kwargs["endpos"],
        ),
        check_regs=True,
    )

    assert findall_window_keyword_workload.pos is None
    assert findall_window_keyword_workload.endpos is None
    assert findall_window_keyword_workload.kwargs == {"endpos": 7, "pos": 1}
    round_tripped_findall_window_keyword = workload_from_payload(
        workload_to_payload(findall_window_keyword_workload)
    )
    assert round_tripped_findall_window_keyword.kwargs == {"endpos": 7, "pos": 1}
    assert round_tripped_findall_window_keyword.keyword_arguments() == {
        "endpos": 7,
        "pos": 1,
    }
    assert run_benchmark_workload_with_cpython(
        round_tripped_findall_window_keyword
    ) == ["abc", "abc"]

    assert findall_window_indexlike_workload.pos is None
    assert findall_window_indexlike_workload.endpos is None
    assert findall_window_indexlike_workload.kwargs == {
        "endpos": {"type": "indexlike", "value": 7},
        "pos": {"type": "indexlike", "value": 1},
    }
    round_tripped_findall_window_indexlike = workload_from_payload(
        workload_to_payload(findall_window_indexlike_workload)
    )
    assert round_tripped_findall_window_indexlike.kwargs == {
        "endpos": {"type": "indexlike", "value": 7},
        "pos": {"type": "indexlike", "value": 1},
    }
    materialized_findall_window_indexlike_kwargs = (
        round_tripped_findall_window_indexlike.keyword_arguments()
    )
    assert materialized_findall_window_indexlike_kwargs["pos"].__index__() == 1
    assert materialized_findall_window_indexlike_kwargs["endpos"].__index__() == 7
    assert run_benchmark_workload_with_cpython(
        round_tripped_findall_window_indexlike
    ) == re.compile("abc").findall(
        "zabcabcabcz",
        pos=materialized_findall_window_indexlike_kwargs["pos"],
        endpos=materialized_findall_window_indexlike_kwargs["endpos"],
    )

    assert findall_window_bool_workload.pos is None
    assert findall_window_bool_workload.endpos is None
    assert findall_window_bool_workload.kwargs == {"endpos": 7, "pos": True}
    assert type(findall_window_bool_workload.kwargs["pos"]) is bool
    round_tripped_findall_window_bool = workload_from_payload(
        workload_to_payload(findall_window_bool_workload)
    )
    assert round_tripped_findall_window_bool.kwargs == {"endpos": 7, "pos": True}
    assert type(round_tripped_findall_window_bool.kwargs["pos"]) is bool
    materialized_findall_bool_kwargs = (
        round_tripped_findall_window_bool.keyword_arguments()
    )
    assert materialized_findall_bool_kwargs == {"endpos": 7, "pos": True}
    assert materialized_findall_bool_kwargs["pos"] is True
    assert run_benchmark_workload_with_cpython(round_tripped_findall_window_bool) == [
        "abc",
        "abc",
    ]

    assert finditer_window_keyword_workload.pos is None
    assert finditer_window_keyword_workload.endpos is None
    assert finditer_window_keyword_workload.kwargs == {"endpos": 7, "pos": 1}
    round_tripped_finditer_window_keyword = workload_from_payload(
        workload_to_payload(finditer_window_keyword_workload)
    )
    assert round_tripped_finditer_window_keyword.kwargs == {"endpos": 7, "pos": 1}
    assert round_tripped_finditer_window_keyword.keyword_arguments() == {
        "endpos": 7,
        "pos": 1,
    }
    observed_finditer_window_keyword = run_benchmark_workload_with_cpython(
        round_tripped_finditer_window_keyword
    )
    expected_finditer_window_keyword = list(
        re.compile(b"abc").finditer(b"zabcabcz", pos=1, endpos=7)
    )
    assert (
        len(observed_finditer_window_keyword)
        == len(expected_finditer_window_keyword)
        == 2
    )
    for observed_match, expected_match in zip(
        observed_finditer_window_keyword,
        expected_finditer_window_keyword,
        strict=True,
    ):
        assert_match_result_parity(
            "stdlib",
            observed_match,
            expected_match,
            check_regs=True,
        )

    assert finditer_window_indexlike_workload.pos is None
    assert finditer_window_indexlike_workload.endpos is None
    assert finditer_window_indexlike_workload.kwargs == {
        "endpos": {"type": "indexlike", "value": 7},
        "pos": {"type": "indexlike", "value": 1},
    }
    round_tripped_finditer_window_indexlike = workload_from_payload(
        workload_to_payload(finditer_window_indexlike_workload)
    )
    assert round_tripped_finditer_window_indexlike.kwargs == {
        "endpos": {"type": "indexlike", "value": 7},
        "pos": {"type": "indexlike", "value": 1},
    }
    materialized_finditer_window_indexlike_kwargs = (
        round_tripped_finditer_window_indexlike.keyword_arguments()
    )
    assert materialized_finditer_window_indexlike_kwargs["pos"].__index__() == 1
    assert materialized_finditer_window_indexlike_kwargs["endpos"].__index__() == 7
    observed_finditer_window_indexlike = run_benchmark_workload_with_cpython(
        round_tripped_finditer_window_indexlike
    )
    expected_finditer_window_indexlike = list(
        re.compile(b"abc").finditer(b"zabcabcabcz", pos=1, endpos=7)
    )
    assert (
        len(observed_finditer_window_indexlike)
        == len(expected_finditer_window_indexlike)
        == 2
    )
    for observed_match, expected_match in zip(
        observed_finditer_window_indexlike,
        expected_finditer_window_indexlike,
        strict=True,
    ):
        assert_match_result_parity(
            "stdlib",
            observed_match,
            expected_match,
            check_regs=True,
        )

    assert finditer_window_bool_workload.pos is None
    assert finditer_window_bool_workload.endpos is None
    assert finditer_window_bool_workload.kwargs == {"endpos": 7, "pos": True}
    assert type(finditer_window_bool_workload.kwargs["pos"]) is bool
    round_tripped_finditer_window_bool = workload_from_payload(
        workload_to_payload(finditer_window_bool_workload)
    )
    assert round_tripped_finditer_window_bool.kwargs == {"endpos": 7, "pos": True}
    assert type(round_tripped_finditer_window_bool.kwargs["pos"]) is bool
    materialized_finditer_window_bool_kwargs = (
        round_tripped_finditer_window_bool.keyword_arguments()
    )
    assert materialized_finditer_window_bool_kwargs == {"endpos": 7, "pos": True}
    assert materialized_finditer_window_bool_kwargs["pos"] is True
    observed_finditer_window_bool = run_benchmark_workload_with_cpython(
        round_tripped_finditer_window_bool
    )
    expected_finditer_window_bool = list(
        re.compile(b"abc").finditer(b"zabcabcz", pos=True, endpos=7)
    )
    assert len(observed_finditer_window_bool) == len(expected_finditer_window_bool) == 2
    for observed_match, expected_match in zip(
        observed_finditer_window_bool,
        expected_finditer_window_bool,
        strict=True,
    ):
        assert_match_result_parity(
            "stdlib",
            observed_match,
            expected_match,
            check_regs=True,
        )
