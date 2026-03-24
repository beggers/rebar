from __future__ import annotations

from functools import partial
import pathlib
from types import SimpleNamespace
from typing import Any

import pytest

from tests.benchmarks import source_tree_benchmark_anchor_support as support
from tests.conftest import records_by_string_id


@pytest.fixture
def anchor_support_cache_guard() -> None:
    for cached_function in (
        support._manifest_workloads,
        support.published_case_ids_by_signature,
        support.published_cases_by_id,
    ):
        cache_clear = getattr(cached_function, "cache_clear", None)
        if cache_clear is not None:
            cache_clear()
    yield
    for cached_function in (
        support._manifest_workloads,
        support.published_case_ids_by_signature,
        support.published_cases_by_id,
    ):
        cache_clear = getattr(cached_function, "cache_clear", None)
        if cache_clear is not None:
            cache_clear()


def _synthetic_manifest(
    *,
    cases: tuple[object, ...] = (),
    workloads: tuple[object, ...] = (),
) -> SimpleNamespace:
    return SimpleNamespace(cases=list(cases), workloads=list(workloads))


def _synthetic_case(
    case_id: str,
    signature: tuple[object, ...] | None,
) -> SimpleNamespace:
    return SimpleNamespace(case_id=case_id, signature=signature)


def _synthetic_workload(
    workload_id: str,
    signature: tuple[object, ...],
    *,
    include: bool = True,
) -> SimpleNamespace:
    return SimpleNamespace(workload_id=workload_id, signature=signature, include=include)


def _synthetic_manifest_loader(
    _: pathlib.Path,
    *,
    workloads: tuple[object, ...],
) -> SimpleNamespace:
    return _synthetic_manifest(workloads=workloads)


def _single_manifest_tuple(manifest: Any) -> tuple[Any, ...]:
    return (manifest,)


def _synthetic_workload_signature(workload: Any) -> tuple[Any, ...]:
    return workload.signature


def _synthetic_workload_is_included(workload: Any) -> bool:
    return workload.include


def test_freeze_signature_value_canonicalizes_nested_mappings_and_lists() -> None:
    value = {
        "b": [2, {"d": 4, "c": [5, 6]}],
        "a": {"y": 1, "x": 0},
    }

    assert support.freeze_signature_value(value) == (
        ("a", (("x", 0), ("y", 1))),
        ("b", (2, (("c", (5, 6)), ("d", 4)))),
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
        partial(_single_manifest_tuple, manifest),
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
