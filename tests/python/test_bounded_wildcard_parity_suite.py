from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

import rebar
from rebar_harness.correctness import (
    BOUNDED_WILDCARD_FIXTURE_SELECTOR,
    FixtureCase,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    assert_expected_fixture_bundle_contract,
    assert_match_convenience_api_parity,
    assert_match_result_parity,
    case_pattern,
    compile_with_cpython_parity,
    load_expected_fixture_bundle,
    published_fixture_paths_from_bundles,
)
PUBLISHED_BOUNDED_WILDCARD_FIXTURE_PATHS = select_correctness_fixture_paths(
    BOUNDED_WILDCARD_FIXTURE_SELECTOR
)


@dataclass(frozen=True)
class CompileCase:
    id: str
    pattern: str
    flags: int = 0


@dataclass(frozen=True)
class PatternCase:
    id: str
    helper: str
    pattern: str
    string: str
    flags: int = 0
    pos: int = 0
    endpos: int | None = None


class _FakeNativeBoundary:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def boundary_compile(self, pattern: str | bytes, flags: int) -> tuple[str, int, bool]:
        self.calls.append(("compile", pattern, flags))
        return ("compiled", 34, False)

    def boundary_literal_match(
        self,
        pattern: str | bytes,
        flags: int,
        mode: str,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, int, int, tuple[int, int] | None]:
        self.calls.append(("match", pattern, flags, mode, string, pos, endpos))
        return ("matched", 0, len(string), (0, 3))

    def boundary_literal_findall(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, list[str] | list[bytes]]:
        self.calls.append(("findall", pattern, flags, string, pos, endpos))
        return ("supported", ["abc"])

    def scaffold_raise(self, helper_name: str) -> object:
        raise NotImplementedError(rebar._placeholder_message(helper_name))

    def scaffold_pattern_raise(self, method_name: str) -> object:
        raise NotImplementedError(rebar._pattern_placeholder_message(method_name))

    def scaffold_purge(self) -> None:
        self.calls.append(("purge",))


FIXTURE_BUNDLES = (
    load_expected_fixture_bundle(
        "literal_flag_workflows.py",
        expected_manifest_id="literal-flag-workflows",
        selected_case_ids=("flag-unsupported-nonliteral-ignorecase-search",),
        expected_case_ids=frozenset({"flag-unsupported-nonliteral-ignorecase-search"}),
        expected_patterns=frozenset({"a.c"}),
        expected_operation_helper_counts=Counter({("module_call", "search"): 1}),
    ),
    load_expected_fixture_bundle(
        "collection_replacement_workflows.py",
        expected_manifest_id="collection-replacement-workflows",
        selected_case_ids=("module-findall-nonliteral-str",),
        expected_case_ids=frozenset({"module-findall-nonliteral-str"}),
        expected_patterns=frozenset({"a.c"}),
        expected_operation_helper_counts=Counter({("module_call", "findall"): 1}),
    ),
)
PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
MODULE_SEARCH_CASES = tuple(case for case in PUBLISHED_CASES if case.helper == "search")
MODULE_FINDALL_CASES = tuple(case for case in PUBLISHED_CASES if case.helper == "findall")

COMPILE_CASES = (
    CompileCase(id="bounded-wildcard-compile-default", pattern="a.c"),
    CompileCase(id="bounded-wildcard-compile-ignorecase", pattern="a.c", flags=re.IGNORECASE),
)

PATTERN_MATCH_CASES = (
    PatternCase(
        id="pattern-search-ignorecase-bounded-hit",
        helper="search",
        pattern="a.c",
        flags=re.IGNORECASE,
        string="zaBczz",
        pos=1,
        endpos=5,
    ),
    PatternCase(
        id="pattern-match-bounded-hit",
        helper="match",
        pattern="a.c",
        string="zabcaxc",
        pos=1,
        endpos=4,
    ),
    PatternCase(
        id="pattern-fullmatch-bounded-hit",
        helper="fullmatch",
        pattern="a.c",
        string="zaxcz",
        pos=1,
        endpos=4,
    ),
    PatternCase(
        id="pattern-search-bounded-endpos-miss",
        helper="search",
        pattern="a.c",
        string="zabc",
        pos=1,
        endpos=3,
    ),
)

PATTERN_COLLECTION_CASES = (
    PatternCase(
        id="pattern-findall-bounded-default",
        helper="findall",
        pattern="a.c",
        string="zabcaxcz",
        pos=1,
        endpos=7,
    ),
    PatternCase(
        id="pattern-finditer-bounded-default",
        helper="finditer",
        pattern="a.c",
        string="zabcaxcx",
        pos=1,
        endpos=7,
    ),
)


def _call_pattern_helper(pattern: object, case: PatternCase) -> object:
    args: list[object] = [case.string]
    if case.pos or case.endpos is not None:
        args.append(case.pos)
        if case.endpos is not None:
            args.append(case.endpos)
    return getattr(pattern, case.helper)(*args)


def _assert_finditer_parity(
    backend_name: str,
    observed_iter: object,
    expected_iter: object,
) -> None:
    observed_matches = list(observed_iter)
    expected_matches = list(expected_iter)

    assert len(observed_matches) == len(expected_matches)
    for observed, expected in zip(observed_matches, expected_matches):
        assert_match_result_parity(backend_name, observed, expected)

    assert next(observed_iter, None) is None
    assert next(expected_iter, None) is None


def test_bounded_wildcard_suite_uses_expected_published_fixture_paths() -> None:
    assert PUBLISHED_BOUNDED_WILDCARD_FIXTURE_PATHS == published_fixture_paths_from_bundles(
        FIXTURE_BUNDLES
    )
    assert len({case.case_id for case in PUBLISHED_CASES}) == len(PUBLISHED_CASES)


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(bundle) -> None:
    assert_expected_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)
    assert {case.text_model for case in bundle.cases} == {"str"}
    assert all("bounded-wildcard" in case.categories for case in bundle.cases)


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: CompileCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, case.pattern, case.flags)


@pytest.mark.parametrize("case", MODULE_SEARCH_CASES, ids=lambda case: case.case_id)
def test_module_search_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert_match_result_parity(backend_name, observed, expected)
    if expected is not None:
        assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", MODULE_FINDALL_CASES, ids=lambda case: case.case_id)
def test_module_findall_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


def test_rebar_bounded_wildcard_direct_workflow_matches_cpython() -> None:
    assert rebar.findall("a.c", "abc") == re.findall("a.c", "abc")

    observed = rebar.search("a.c", "ABC", rebar.IGNORECASE)
    expected = re.search("a.c", "ABC", re.IGNORECASE)

    assert expected is not None
    assert observed is not None
    assert type(observed) is rebar.Match
    assert observed.group(0) == expected.group(0)
    assert observed.span() == expected.span()

    compiled = rebar.compile("a.c")
    assert compiled is rebar.compile("a.c")
    assert compiled.findall("zabcaxc") == ["abc", "axc"]


def test_rebar_bounded_wildcard_unsupported_paths_keep_placeholder_messages() -> None:
    with pytest.raises(
        NotImplementedError,
        match=r"rebar\.compile\(\) is a scaffold placeholder",
    ):
        rebar.search("[ab]c", "abc")

    unsupported = rebar.compile("abc", rebar.IGNORECASE)
    with pytest.raises(
        NotImplementedError,
        match=r"rebar\.Pattern\.findall\(\) is a scaffold placeholder",
    ):
        unsupported.findall("ABC")


@pytest.mark.parametrize("case", PATTERN_MATCH_CASES, ids=lambda case: case.id)
def test_pattern_match_helpers_match_cpython(
    regex_backend: tuple[str, object],
    case: PatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
        case.flags,
    )

    observed = _call_pattern_helper(observed_pattern, case)
    expected = _call_pattern_helper(expected_pattern, case)

    assert_match_result_parity(backend_name, observed, expected)
    if expected is not None:
        assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", PATTERN_COLLECTION_CASES, ids=lambda case: case.id)
def test_pattern_collection_helpers_match_cpython(
    regex_backend: tuple[str, object],
    case: PatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
        case.flags,
    )

    observed = _call_pattern_helper(observed_pattern, case)
    expected = _call_pattern_helper(expected_pattern, case)

    if case.helper == "finditer":
        _assert_finditer_parity(backend_name, observed, expected)
        return

    assert observed == expected


def test_fake_native_boundary_handles_bounded_wildcard_wrappers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_native = _FakeNativeBoundary()
    monkeypatch.setattr(rebar, "_native", fake_native)

    rebar.purge()

    search_match = rebar.search("a.c", "ABC", rebar.IGNORECASE)

    assert search_match is not None
    assert type(search_match) is rebar.Match
    assert search_match.group(0) == "ABC"
    assert search_match.span() == (0, 3)
    assert rebar.findall("a.c", "abc") == ["abc"]

    assert fake_native.calls == [
        ("purge",),
        ("compile", "a.c", int(rebar.IGNORECASE)),
        ("match", "a.c", 34, "search", "ABC", 0, None),
        ("compile", "a.c", 0),
        ("findall", "a.c", 34, "abc", 0, None),
    ]
