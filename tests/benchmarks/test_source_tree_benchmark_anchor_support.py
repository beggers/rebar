from __future__ import annotations

from functools import partial
import pathlib
from types import SimpleNamespace

import pytest

from tests.benchmarks.benchmark_anchor_support_test_helpers import (
    _synthetic_case,
    _synthetic_manifest,
    _synthetic_manifest_loader,
    _synthetic_workload,
    _synthetic_workload_is_included,
    _synthetic_workload_signature,
    anchor_support_cache_guard,
)
from tests.benchmarks import benchmark_test_support as benchmark_support
from tests.benchmarks.benchmark_test_support import (
    live_manifest_workload,
    synthetic_workload,
)
from tests.benchmarks import source_tree_benchmark_anchor_support as support
from tests.conftest import REPO_ROOT, records_by_string_id
from tests.python.fixture_parity_support import IndexLike

GROUPED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py"
)
GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT
    / "benchmarks"
    / "workloads"
    / "grouped_alternation_replacement_boundary.py"
)
OPTIONAL_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.py"
)
NESTED_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py"
)
EXACT_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "exact_repeat_quantified_group_boundary.py"
)
RANGED_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "ranged_repeat_quantified_group_boundary.py"
)
OPEN_ENDED_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "open_ended_quantified_group_boundary.py"
)


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


def test_freeze_signature_value_canonicalizes_nested_mappings_and_lists() -> None:
    value = {
        "b": [2, {"d": 4, "c": [5, 6]}],
        "a": {"y": 1, "x": 0},
    }

    assert support.freeze_signature_value(value) == (
        ("a", (("x", 0), ("y", 1))),
        ("b", (2, (("c", (5, 6)), ("d", 4)))),
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


def test_optional_group_conditional_helpers_stay_on_the_search_anchor() -> None:
    cases = support.published_cases_by_id()
    workload = live_manifest_workload(
        OPTIONAL_GROUP_MANIFEST_PATH,
        support._OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID,
    )
    non_conditional_workload = live_manifest_workload(
        OPTIONAL_GROUP_MANIFEST_PATH,
        "module-search-named-optional-group-absent-warm-str",
    )

    assert support._is_optional_group_conditional_workload(workload)
    assert not support._is_optional_group_conditional_workload(non_conditional_workload)
    assert support._optional_group_correctness_case_signature(
        cases["optional-group-conditional-module-search-present-str"]
    ) == (
        "module.search",
        None,
        ("a(b)?(?(1)c|d)e", "zzabcezz"),
        (),
        0,
        "str",
    )
    assert support._optional_group_workload_signature(workload) == (
        "module.search",
        None,
        ("a(b)?(?(1)c|d)e", "zzabcezz"),
        (),
        0,
        "str",
    )
    assert (
        support._optional_group_correctness_case_signature(
            _module_pattern_case(
                helper="fullmatch",
                operation="pattern_call",
                args=("abce",),
                pattern="a(b)?(?(1)c|d)e",
            )
        )
        is None
    )
    with pytest.raises(
        AssertionError,
        match="unexpected optional-group benchmark workload operation",
    ):
        support._optional_group_workload_signature(
            synthetic_workload(
                manifest_id="optional-group-boundary",
                workload_id="optional-group-compile-unsupported",
                operation="module.compile",
                pattern="a(b)?(?(1)c|d)e",
            )
        )


def test_nested_group_live_signatures_cover_numbered_and_named_routes() -> None:
    cases = support.published_cases_by_id()

    assert support._nested_group_correctness_case_signature(
        cases["nested-group-compile-metadata-str"]
    ) == ("module.compile", "a((b))d", (), (), 0, "str")
    assert support._nested_group_workload_signature(
        live_manifest_workload(
            NESTED_GROUP_MANIFEST_PATH,
            "module-compile-nested-group-cold-str",
        )
    ) == ("module.compile", "a((b))d", (), (), 0, "str")

    assert support._nested_group_correctness_case_signature(
        cases["nested-group-module-search-str"]
    ) == (
        "module.search",
        None,
        ("a((b))d", "zzabdzz"),
        (),
        0,
        "str",
    )
    assert support._nested_group_workload_signature(
        live_manifest_workload(
            NESTED_GROUP_MANIFEST_PATH,
            "module-search-nested-group-warm-str",
        )
    ) == (
        "module.search",
        None,
        ("a((b))d", "zzabdzz"),
        (),
        0,
        "str",
    )

    assert support._nested_group_correctness_case_signature(
        cases["nested-group-pattern-fullmatch-str"]
    ) == (
        "pattern.fullmatch",
        "a((b))d",
        ("abd",),
        (),
        0,
        "str",
    )
    assert support._nested_group_workload_signature(
        live_manifest_workload(
            NESTED_GROUP_MANIFEST_PATH,
            "pattern-fullmatch-nested-group-purged-str",
        )
    ) == (
        "pattern.fullmatch",
        "a((b))d",
        ("abd",),
        (),
        0,
        "str",
    )

    assert support._nested_group_correctness_case_signature(
        cases["named-nested-group-compile-metadata-str"]
    ) == ("module.compile", "a(?P<outer>(?P<inner>b))d", (), (), 0, "str")
    assert support._nested_group_workload_signature(
        live_manifest_workload(
            NESTED_GROUP_MANIFEST_PATH,
            "module-compile-named-nested-group-warm-str",
        )
    ) == ("module.compile", "a(?P<outer>(?P<inner>b))d", (), (), 0, "str")

    assert support._nested_group_correctness_case_signature(
        cases["named-nested-group-module-search-str"]
    ) == (
        "module.search",
        None,
        ("a(?P<outer>(?P<inner>b))d", "zzabdzz"),
        (),
        0,
        "str",
    )
    assert support._nested_group_workload_signature(
        live_manifest_workload(
            NESTED_GROUP_MANIFEST_PATH,
            "module-search-named-nested-group-warm-str",
        )
    ) == (
        "module.search",
        None,
        ("a(?P<outer>(?P<inner>b))d", "zzabdzz"),
        (),
        0,
        "str",
    )

    assert support._nested_group_correctness_case_signature(
        cases["named-nested-group-pattern-fullmatch-str"]
    ) == (
        "pattern.fullmatch",
        "a(?P<outer>(?P<inner>b))d",
        ("abd",),
        (),
        0,
        "str",
    )
    assert support._nested_group_workload_signature(
        live_manifest_workload(
            NESTED_GROUP_MANIFEST_PATH,
            "pattern-fullmatch-named-nested-group-purged-str",
        )
    ) == (
        "pattern.fullmatch",
        "a(?P<outer>(?P<inner>b))d",
        ("abd",),
        (),
        0,
        "str",
    )


def test_counted_repeat_live_signatures_cover_exact_ranged_and_open_ended_routes() -> None:
    cases = support.published_cases_by_id()

    assert support._counted_repeat_correctness_case_signature(
        cases["exact-repeat-numbered-group-compile-metadata-str"]
    ) == ("module.compile", "a(bc){2}d", (), (), 0, "str")
    assert support._counted_repeat_workload_signature(
        live_manifest_workload(
            EXACT_REPEAT_MANIFEST_PATH,
            "module-compile-numbered-exact-repeat-group-cold-str",
        )
    ) == ("module.compile", "a(bc){2}d", (), (), 0, "str")

    assert support._counted_repeat_correctness_case_signature(
        cases["exact-repeat-named-group-module-search-str"]
    ) == (
        "module.search",
        None,
        ("a(?P<word>bc){2}d", "zzabcbcdzz"),
        (),
        0,
        "str",
    )
    assert support._counted_repeat_workload_signature(
        live_manifest_workload(
            EXACT_REPEAT_MANIFEST_PATH,
            "module-search-named-exact-repeat-group-warm-str",
        )
    ) == (
        "module.search",
        None,
        ("a(?P<word>bc){2}d", "zzabcbcdzz"),
        (),
        0,
        "str",
    )

    assert support._counted_repeat_correctness_case_signature(
        cases["ranged-repeat-numbered-group-module-search-lower-bound-str"]
    ) == (
        "module.search",
        None,
        ("a(bc){1,2}d", "zzabcdzz"),
        (),
        0,
        "str",
    )
    assert support._counted_repeat_workload_signature(
        live_manifest_workload(
            RANGED_REPEAT_MANIFEST_PATH,
            "module-search-numbered-ranged-repeat-group-lower-bound-warm-str",
        )
    ) == (
        "module.search",
        None,
        ("a(bc){1,2}d", "zzabcdzz"),
        (),
        0,
        "str",
    )

    assert support._counted_repeat_correctness_case_signature(
        cases["ranged-repeat-named-group-pattern-fullmatch-lower-bound-str"]
    ) == (
        "pattern.fullmatch",
        "a(?P<word>bc){1,2}d",
        ("abcd",),
        (),
        0,
        "str",
    )
    assert support._counted_repeat_workload_signature(
        live_manifest_workload(
            RANGED_REPEAT_MANIFEST_PATH,
            "pattern-fullmatch-named-ranged-repeat-group-lower-bound-purged-str",
        )
    ) == (
        "pattern.fullmatch",
        "a(?P<word>bc){1,2}d",
        ("abcd",),
        (),
        0,
        "str",
    )

    assert support._counted_repeat_correctness_case_signature(
        cases["open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str"]
    ) == (
        "module.search",
        None,
        ("a(bc|de){1,}d", "zzabcdzz"),
        (),
        0,
        "str",
    )
    assert support._counted_repeat_workload_signature(
        live_manifest_workload(
            OPEN_ENDED_MANIFEST_PATH,
            "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-str",
        )
    ) == (
        "module.search",
        None,
        ("a(bc|de){1,}d", "zzabcdzz"),
        (),
        0,
        "str",
    )

    assert support._counted_repeat_correctness_case_signature(
        cases["open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str"]
    ) == (
        "pattern.fullmatch",
        "a(?P<word>bc|de){1,}d",
        ("adededed",),
        (),
        0,
        "str",
    )
    assert support._counted_repeat_workload_signature(
        live_manifest_workload(
            OPEN_ENDED_MANIFEST_PATH,
            "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-str",
        )
    ) == (
        "pattern.fullmatch",
        "a(?P<word>bc|de){1,}d",
        ("adededed",),
        (),
        0,
        "str",
    )


def test_non_alternation_counted_repeat_selector_excludes_alternation_workloads() -> None:
    assert support._is_non_alternation_counted_repeat_workload(
        live_manifest_workload(
            EXACT_REPEAT_MANIFEST_PATH,
            "module-compile-numbered-exact-repeat-group-cold-str",
        )
    )
    assert support._is_non_alternation_counted_repeat_workload(
        live_manifest_workload(
            RANGED_REPEAT_MANIFEST_PATH,
            "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
        )
    )
    assert not support._is_non_alternation_counted_repeat_workload(
        live_manifest_workload(
            EXACT_REPEAT_MANIFEST_PATH,
            "module-search-numbered-exact-repeat-group-alternation-bc-bc-warm-str",
        )
    )
    assert not support._is_non_alternation_counted_repeat_workload(
        live_manifest_workload(
            OPEN_ENDED_MANIFEST_PATH,
            "module-search-numbered-open-ended-group-broader-range-cold-gap",
        )
    )


def test_published_case_ids_by_signature_groups_duplicate_case_ids(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest = _synthetic_manifest(
        cases=(
            _synthetic_case("case-b", ("shared",)),
            _synthetic_case("case-a", ("shared",)),
            _synthetic_case("case-c", ("unique",)),
            _synthetic_case("ignored", None),
        )
    )
    monkeypatch.setattr(
        support,
        "published_fixture_manifests",
        lambda: (manifest,),
    )

    observed = support.published_case_ids_by_signature(lambda case: case.signature)

    assert observed == {
        ("shared",): ("case-a", "case-b"),
        ("unique",): ("case-c",),
    }


def test_anchored_and_unanchored_workload_helpers_follow_signatures_and_filters(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",)),
        _synthetic_workload("excluded", ("shared",), include=False),
    )
    monkeypatch.setattr(
        benchmark_support,
        "load_manifest",
        partial(_synthetic_manifest_loader, workloads=workloads),
    )

    anchor_case_ids = {("shared",): ("case-a", "case-b")}

    assert support.anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
    ) == {
        ("synthetic_boundary.py", "anchored"): ("case-a", "case-b"),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert support.unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
    ) == ("unanchored",)


def test_expected_anchored_workload_case_pairs_return_matching_objects(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workload = _synthetic_workload("anchored", ("shared",))
    case = SimpleNamespace(case_id="case-1")
    monkeypatch.setattr(
        benchmark_support,
        "load_manifest",
        partial(_synthetic_manifest_loader, workloads=(workload,)),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        partial(records_by_string_id, (case,), id_attr="case_id"),
    )

    anchored_pairs = support.expected_anchored_workload_case_pairs(
        manifest_path,
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
        },
    )

    assert len(anchored_pairs) == 1
    anchored_pair = anchored_pairs[0]
    assert anchored_pair.manifest_name == "synthetic_boundary.py"
    assert anchored_pair.workload_id == "anchored"
    assert anchored_pair.case_id == "case-1"
    assert anchored_pair.workload is workload
    assert anchored_pair.case is case


def test_expected_anchored_workload_case_pairs_rejects_manifest_name_drift(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    monkeypatch.setattr(
        benchmark_support,
        "load_manifest",
        partial(
            _synthetic_manifest_loader,
            workloads=(_synthetic_workload("anchored", ("shared",)),),
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        partial(
            records_by_string_id,
            (SimpleNamespace(case_id="case-1"),),
            id_attr="case_id",
        ),
    )

    with pytest.raises(AssertionError, match="does not match"):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("other_boundary.py", "anchored"): ("case-1",),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_multiple_case_ids(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    monkeypatch.setattr(
        benchmark_support,
        "load_manifest",
        partial(
            _synthetic_manifest_loader,
            workloads=(_synthetic_workload("anchored", ("shared",)),),
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        partial(
            records_by_string_id,
            (
                SimpleNamespace(case_id="case-1"),
                SimpleNamespace(case_id="case-2"),
            ),
            id_attr="case_id",
        ),
    )

    with pytest.raises(
        AssertionError,
        match="expected exactly one published correctness case",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "anchored"): ("case-1", "case-2"),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_missing_workload(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    monkeypatch.setattr(
        benchmark_support,
        "load_manifest",
        partial(
            _synthetic_manifest_loader,
            workloads=(_synthetic_workload("anchored", ("shared",)),),
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        partial(
            records_by_string_id,
            (SimpleNamespace(case_id="case-1"),),
            id_attr="case_id",
        ),
    )

    with pytest.raises(
        AssertionError,
        match=r"expected anchored workload 'missing' to be in scope",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "missing"): ("case-1",),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_unpublished_case(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    monkeypatch.setattr(
        benchmark_support,
        "load_manifest",
        partial(
            _synthetic_manifest_loader,
            workloads=(_synthetic_workload("anchored", ("shared",)),),
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        partial(records_by_string_id, (), id_attr="case_id"),
    )

    with pytest.raises(
        AssertionError,
        match=r"expected anchored correctness case 'case-1' to be published",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "anchored"): ("case-1",),
            },
        )


def test_assert_anchored_workload_case_result_parity_delegates_expected_values(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    workload = _synthetic_workload("anchored", ("shared",))
    pair = support.AnchoredWorkloadCasePair(
        manifest_name="synthetic_boundary.py",
        workload_id="anchored",
        case_id="case-1",
        workload=workload,
        case=SimpleNamespace(case_id="case-1"),
    )
    calls: list[tuple[object, object]] = []
    monkeypatch.setattr(
        support,
        "run_correctness_case_with_cpython",
        lambda case: f"expected:{case.case_id}",
    )
    monkeypatch.setattr(
        support,
        "assert_benchmark_workload_matches_expected_result",
        lambda workload, expected: calls.append((workload, expected)),
    )

    support.assert_anchored_workload_case_result_parity((pair,))

    assert calls == [(workload, "expected:case-1")]


def test_assert_anchored_workload_case_result_parity_accepts_matching_exceptions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workload = _synthetic_workload("anchored", ("shared",))
    pair = support.AnchoredWorkloadCasePair(
        manifest_name="synthetic_boundary.py",
        workload_id="anchored",
        case_id="case-1",
        workload=workload,
        case=SimpleNamespace(case_id="case-1"),
    )
    benchmark_calls: list[object] = []

    def _raise_expected(_: object) -> object:
        raise ValueError("shared boom")

    def _raise_observed(observed_workload: object) -> object:
        benchmark_calls.append(observed_workload)
        raise ValueError("shared boom")

    monkeypatch.setattr(support, "run_correctness_case_with_cpython", _raise_expected)
    monkeypatch.setattr(support, "run_benchmark_workload_with_cpython", _raise_observed)

    support.assert_anchored_workload_case_result_parity((pair,))

    assert benchmark_calls == [workload]


def test_assert_anchored_workload_case_result_parity_rejects_exception_message_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workload = _synthetic_workload("anchored", ("shared",))
    pair = support.AnchoredWorkloadCasePair(
        manifest_name="synthetic_boundary.py",
        workload_id="anchored",
        case_id="case-1",
        workload=workload,
        case=SimpleNamespace(case_id="case-1"),
    )

    def _raise_expected(_: object) -> object:
        raise ValueError("expected boom")

    def _raise_observed(_: object) -> object:
        raise ValueError("observed boom")

    monkeypatch.setattr(support, "run_correctness_case_with_cpython", _raise_expected)
    monkeypatch.setattr(support, "run_benchmark_workload_with_cpython", _raise_observed)

    with pytest.raises(AssertionError):
        support.assert_anchored_workload_case_result_parity((pair,))


def test_grouped_alternation_live_signatures_cover_non_replacement_routes() -> None:
    cases = support.published_cases_by_id()

    compile_workload = live_manifest_workload(
        GROUPED_ALTERNATION_MANIFEST_PATH,
        "module-compile-grouped-alternation-cold-str",
    )
    search_workload = live_manifest_workload(
        GROUPED_ALTERNATION_MANIFEST_PATH,
        "module-search-grouped-alternation-warm-str",
    )
    fullmatch_workload = live_manifest_workload(
        GROUPED_ALTERNATION_MANIFEST_PATH,
        "pattern-fullmatch-grouped-alternation-purged-str",
    )
    legacy_module_sub_workload = live_manifest_workload(
        GROUPED_ALTERNATION_MANIFEST_PATH,
        "module-sub-template-nested-grouped-alternation-warm-gap",
    )
    legacy_pattern_subn_workload = live_manifest_workload(
        GROUPED_ALTERNATION_MANIFEST_PATH,
        "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
    )

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
    cases = support.published_cases_by_id()

    module_sub_workload = live_manifest_workload(
        GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        "module-sub-template-grouped-alternation-warm-str",
    )
    module_subn_workload = live_manifest_workload(
        GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        "module-subn-template-named-grouped-alternation-warm-str",
    )
    pattern_sub_workload = live_manifest_workload(
        GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        "pattern-sub-template-grouped-alternation-purged-str",
    )
    pattern_subn_workload = live_manifest_workload(
        GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        "pattern-subn-template-named-grouped-alternation-purged-str",
    )

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
    assert support._grouped_alternation_workload_args(module_sub_workload) == (
        "a(b|c)d",
        "\\1x",
        "abdacd",
    )
    assert support._grouped_alternation_workload_signature(module_sub_workload) == (
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
    assert support._grouped_alternation_workload_args(module_subn_workload) == (
        "a(?P<word>b|c)d",
        "\\g<word>x",
        "abdacd",
        1,
    )
    assert support._grouped_alternation_workload_signature(
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
    assert support._grouped_alternation_workload_args(pattern_sub_workload) == (
        "\\1x",
        "acdabd",
    )
    assert support._grouped_alternation_workload_signature(pattern_sub_workload) == (
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
    assert support._grouped_alternation_workload_args(pattern_subn_workload) == (
        "\\g<word>x",
        "acdabd",
        1,
    )
    assert support._grouped_alternation_workload_signature(
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
    unsupported_workload = synthetic_workload(
        manifest_id="grouped-alternation-boundary",
        workload_id="module-match-grouped-alternation-unsupported",
        operation="module.match",
        pattern="a(b|c)d",
        haystack="abdacd",
        replacement="\\1x",
    )

    with pytest.raises(AssertionError, match="unexpected grouped-alternation"):
        support._grouped_alternation_workload_args(unsupported_workload)
    with pytest.raises(AssertionError, match="unexpected grouped-alternation"):
        support._grouped_alternation_workload_signature(unsupported_workload)
