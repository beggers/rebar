from __future__ import annotations

import pytest

from rebar_harness.benchmarks import load_manifest, workload_from_payload
from tests.benchmarks import grouped_alternation_benchmark_anchor_support as support
from tests.benchmarks.source_tree_benchmark_anchor_support import published_cases_by_id
from tests.conftest import REPO_ROOT

GROUPED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py"
)
GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT
    / "benchmarks"
    / "workloads"
    / "grouped_alternation_replacement_boundary.py"
)


def _manifest_workloads_by_id(manifest_path: object) -> dict[str, object]:
    return {
        workload.workload_id: workload
        for workload in load_manifest(manifest_path).workloads
    }


def _synthetic_workload(*, workload_id: str, operation: str) -> object:
    return workload_from_payload(
        {
            "manifest_id": "grouped-alternation-boundary",
            "workload_id": workload_id,
            "bucket": operation.replace(".", "-"),
            "family": "module",
            "operation": operation,
            "pattern": "a(b|c)d",
            "haystack": "abdacd",
            "replacement": "\\1x",
            "expected_exception": None,
            "flags": 0,
            "use_compiled_pattern": False,
            "count": 0,
            "maxsplit": 0,
            "kwargs": {},
            "text_model": "str",
            "haystack_text_model": None,
            "cache_mode": "warm",
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


def test_grouped_alternation_live_signatures_cover_non_replacement_routes() -> None:
    workloads = _manifest_workloads_by_id(GROUPED_ALTERNATION_MANIFEST_PATH)
    cases = published_cases_by_id()

    compile_workload = workloads["module-compile-grouped-alternation-cold-str"]
    search_workload = workloads["module-search-grouped-alternation-warm-str"]
    fullmatch_workload = workloads["pattern-fullmatch-grouped-alternation-purged-str"]
    legacy_module_sub_workload = workloads[
        "module-sub-template-nested-grouped-alternation-warm-gap"
    ]
    legacy_pattern_subn_workload = workloads[
        "pattern-subn-template-named-nested-grouped-alternation-purged-gap"
    ]

    assert support._grouped_alternation_correctness_case_signature(
        cases["grouped-alternation-compile-metadata-str"]
    ) == ("module.compile", "a(b|c)d", (), (), 0, "str")
    assert support._grouped_alternation_workload_signature(compile_workload) == (
        "module.compile",
        "a(b|c)d",
        (),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_correctness_case_signature(
        cases["grouped-alternation-module-search-str"]
    ) == (
        "module.search",
        None,
        ("a(b|c)d", "zzacdzz"),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_workload_args(search_workload) == (
        "a(b|c)d",
        "zzacdzz",
    )
    assert support._grouped_alternation_workload_signature(search_workload) == (
        "module.search",
        None,
        ("a(b|c)d", "zzacdzz"),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_correctness_case_signature(
        cases["grouped-alternation-pattern-fullmatch-str"]
    ) == (
        "pattern.fullmatch",
        "a(b|c)d",
        ("abd",),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_workload_args(fullmatch_workload) == ("abd",)
    assert support._grouped_alternation_workload_signature(fullmatch_workload) == (
        "pattern.fullmatch",
        "a(b|c)d",
        ("abd",),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_correctness_case_signature(
        cases["module-sub-template-nested-group-alternation-numbered-wrapper-str"]
    ) == (
        "module.sub",
        None,
        ("a((b|c))d", "<\\1>", "abdacd"),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_workload_args(legacy_module_sub_workload) == (
        "a((b|c))d",
        "<\\1>",
        "abdacd",
    )
    assert support._grouped_alternation_workload_signature(
        legacy_module_sub_workload
    ) == (
        "module.sub",
        None,
        ("a((b|c))d", "<\\1>", "abdacd"),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_correctness_case_signature(
        cases["pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str"]
    ) == (
        "pattern.subn",
        "a(?P<outer>(b|c))d",
        ("<\\g<outer>>", "abdacd", 1),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_workload_args(
        legacy_pattern_subn_workload
    ) == ("<\\g<outer>>", "abdacd", 1)
    assert support._grouped_alternation_workload_signature(
        legacy_pattern_subn_workload
    ) == (
        "pattern.subn",
        "a(?P<outer>(b|c))d",
        ("<\\g<outer>>", "abdacd", 1),
        (),
        0,
        "str",
    )


def test_grouped_alternation_replacement_live_signatures_cover_module_and_pattern_routes() -> None:
    workloads = _manifest_workloads_by_id(GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH)
    cases = published_cases_by_id()

    module_sub_workload = workloads["module-sub-template-grouped-alternation-warm-str"]
    module_subn_workload = workloads[
        "module-subn-template-named-grouped-alternation-warm-str"
    ]
    pattern_sub_workload = workloads[
        "pattern-sub-template-grouped-alternation-purged-str"
    ]
    pattern_subn_workload = workloads[
        "pattern-subn-template-named-grouped-alternation-purged-str"
    ]

    assert support._grouped_alternation_replacement_correctness_case_signature(
        cases["module-sub-template-grouped-alternation-str"]
    ) == (
        "module.sub",
        None,
        ("a(b|c)d", "\\1x", "abdacd"),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_replacement_workload_args(
        module_sub_workload
    ) == ("a(b|c)d", "\\1x", "abdacd")
    assert support._grouped_alternation_replacement_workload_signature(
        module_sub_workload
    ) == (
        "module.sub",
        None,
        ("a(b|c)d", "\\1x", "abdacd"),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_replacement_correctness_case_signature(
        cases["module-subn-template-named-grouped-alternation-str"]
    ) == (
        "module.subn",
        None,
        ("a(?P<word>b|c)d", "\\g<word>x", "abdacd", 1),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_replacement_workload_args(
        module_subn_workload
    ) == ("a(?P<word>b|c)d", "\\g<word>x", "abdacd", 1)
    assert support._grouped_alternation_replacement_workload_signature(
        module_subn_workload
    ) == (
        "module.subn",
        None,
        ("a(?P<word>b|c)d", "\\g<word>x", "abdacd", 1),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_replacement_correctness_case_signature(
        cases["pattern-sub-template-grouped-alternation-str"]
    ) == (
        "pattern.sub",
        "a(b|c)d",
        ("\\1x", "acdabd"),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_replacement_workload_args(
        pattern_sub_workload
    ) == ("\\1x", "acdabd")
    assert support._grouped_alternation_replacement_workload_signature(
        pattern_sub_workload
    ) == (
        "pattern.sub",
        "a(b|c)d",
        ("\\1x", "acdabd"),
        (),
        0,
        "str",
    )

    assert support._grouped_alternation_replacement_correctness_case_signature(
        cases["pattern-subn-template-named-grouped-alternation-str"]
    ) == (
        "pattern.subn",
        "a(?P<word>b|c)d",
        ("\\g<word>x", "acdabd", 1),
        (),
        0,
        "str",
    )
    assert support._grouped_alternation_replacement_workload_args(
        pattern_subn_workload
    ) == ("\\g<word>x", "acdabd", 1)
    assert support._grouped_alternation_replacement_workload_signature(
        pattern_subn_workload
    ) == (
        "pattern.subn",
        "a(?P<word>b|c)d",
        ("\\g<word>x", "acdabd", 1),
        (),
        0,
        "str",
    )


def test_grouped_alternation_workload_helpers_reject_unsupported_operations() -> None:
    unsupported_workload = _synthetic_workload(
        workload_id="module-match-grouped-alternation-unsupported",
        operation="module.match",
    )

    with pytest.raises(AssertionError, match="unexpected grouped-alternation"):
        support._grouped_alternation_workload_args(unsupported_workload)
    with pytest.raises(AssertionError, match="unexpected grouped-alternation"):
        support._grouped_alternation_workload_signature(unsupported_workload)


def test_grouped_alternation_replacement_workload_helpers_reject_unsupported_operations() -> None:
    unsupported_workload = _synthetic_workload(
        workload_id="module-search-grouped-alternation-replacement-unsupported",
        operation="module.search",
    )

    with pytest.raises(
        AssertionError,
        match="unexpected grouped-alternation replacement",
    ):
        support._grouped_alternation_replacement_workload_args(unsupported_workload)
    with pytest.raises(
        AssertionError,
        match="unexpected grouped-alternation replacement",
    ):
        support._grouped_alternation_replacement_workload_signature(unsupported_workload)
