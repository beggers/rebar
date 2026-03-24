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
        support,
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
        support,
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


def test_manifest_workload_cache_reuses_one_load_for_repeated_anchor_queries(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",)),
    )
    case = SimpleNamespace(case_id="case-1")
    load_calls: list[pathlib.Path] = []

    def _load_manifest(path: pathlib.Path) -> SimpleNamespace:
        load_calls.append(path)
        return _synthetic_manifest(workloads=workloads)

    monkeypatch.setattr(support, "load_manifest", _load_manifest)
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        partial(records_by_string_id, (case,), id_attr="case_id"),
    )

    anchor_case_ids = {("shared",): ("case-1",)}

    assert support.anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=_synthetic_workload_signature,
    ) == {
        ("synthetic_boundary.py", "anchored"): ("case-1",),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert support.unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=_synthetic_workload_signature,
    ) == ("unanchored",)
    assert support.expected_anchored_workload_case_pairs(
        manifest_path,
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
        },
    ) == (
        support.AnchoredWorkloadCasePair(
            manifest_name="synthetic_boundary.py",
            workload_id="anchored",
            case_id="case-1",
            workload=workloads[0],
            case=case,
        ),
    )
    assert load_calls == [manifest_path]


def test_expected_anchored_workload_case_pairs_rejects_manifest_name_drift(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    monkeypatch.setattr(
        support,
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
        support,
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
        support,
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
        support,
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


def test_grouped_alternation_replacement_workload_helpers_reject_unsupported_operations() -> None:
    unsupported_workload = synthetic_workload(
        manifest_id="grouped-alternation-boundary",
        workload_id="module-search-grouped-alternation-replacement-unsupported",
        operation="module.search",
        pattern="a(b|c)d",
        haystack="abdacd",
        replacement="\\1x",
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
