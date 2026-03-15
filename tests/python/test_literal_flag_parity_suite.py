from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

import rebar
from rebar_harness.correctness import (
    FixtureCase,
    FixtureManifest,
    load_fixture_manifest,
)
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    assert_match_convenience_api_parity,
    assert_match_result_parity,
    assert_pattern_parity,
    case_pattern,
    compile_with_cpython_parity,
    select_published_fixture_paths,
)


IGNORECASE_FLAGS = int(rebar.IGNORECASE)
UNICODE_FLAGS = int(rebar.UNICODE)
ASCII_FLAGS = int(rebar.ASCII)
LOCALE_FLAGS = int(rebar.LOCALE)
IGNORECASE_UNICODE_FLAGS = IGNORECASE_FLAGS | UNICODE_FLAGS

EXPECTED_PUBLISHED_FIXTURE_NAMES = ("literal_flag_workflows.py",)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    sorted(
        (FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES),
        key=lambda path: path.name,
    )
)
PUBLISHED_LITERAL_FLAG_FIXTURE_PATHS = select_published_fixture_paths(
    EXPECTED_PUBLISHED_FIXTURE_PATHS
)


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_case_ids: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]


@dataclass(frozen=True)
class ModuleCallCase:
    id: str
    helper: str
    pattern: str | bytes
    string: str | bytes
    flags: int = 0


@dataclass(frozen=True)
class PatternCallCase:
    id: str
    helper: str
    pattern: str | bytes
    string: str | bytes
    flags: int = 0
    pos: int = 0
    endpos: int | None = None


@dataclass(frozen=True)
class FakeBoundaryCase:
    id: str
    pattern: str | bytes
    string: str | bytes
    flags: int
    compiled_flags: int
    expected_calls: tuple[tuple[object, ...], ...]


def _fixture_bundle(
    fixture_name: str,
    *,
    selected_case_ids: tuple[str, ...],
    expected_manifest_id: str,
    expected_operation_helper_counts: Counter[tuple[str, str | None]],
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    case_by_id = {case.case_id: case for case in cases}
    missing_case_ids = tuple(
        case_id for case_id in selected_case_ids if case_id not in case_by_id
    )
    if missing_case_ids:
        raise ValueError(
            f"{fixture_name} is missing expected literal-flag fixture rows: {missing_case_ids}"
        )

    return FixtureBundle(
        manifest=manifest,
        cases=tuple(case_by_id[case_id] for case_id in selected_case_ids),
        expected_manifest_id=expected_manifest_id,
        expected_case_ids=frozenset(selected_case_ids),
        expected_operation_helper_counts=expected_operation_helper_counts,
    )


def _module_case_from_fixture(case: FixtureCase) -> ModuleCallCase:
    assert case.operation == "module_call"
    assert case.helper is not None
    assert not case.kwargs
    assert len(case.args) in (2, 3)

    pattern = case.args[0]
    string = case.args[1]
    flags = int(case.args[2]) if len(case.args) == 3 else 0

    assert isinstance(pattern, (str, bytes))
    assert isinstance(string, (str, bytes))
    return ModuleCallCase(
        id=case.case_id,
        helper=case.helper,
        pattern=pattern,
        string=string,
        flags=flags,
    )


def _pattern_case_from_fixture(case: FixtureCase) -> PatternCallCase:
    assert case.operation == "pattern_call"
    assert case.helper is not None
    assert not case.kwargs
    assert 1 <= len(case.args) <= 3

    string = case.args[0]
    pos = int(case.args[1]) if len(case.args) >= 2 else 0
    endpos = int(case.args[2]) if len(case.args) >= 3 else None

    assert isinstance(string, (str, bytes))
    return PatternCallCase(
        id=case.case_id,
        helper=case.helper,
        pattern=case_pattern(case),
        string=string,
        flags=case.flags or 0,
        pos=pos,
        endpos=endpos,
    )


def _call_module_helper(regex_api: object, case: ModuleCallCase) -> object:
    return getattr(regex_api, case.helper)(case.pattern, case.string, case.flags)


def _call_pattern_helper(pattern: object, case: PatternCallCase) -> object:
    args: list[object] = [case.string]
    if case.pos or case.endpos is not None:
        args.append(case.pos)
        if case.endpos is not None:
            args.append(case.endpos)
    return getattr(pattern, case.helper)(*args)


def _require_native_module() -> None:
    if not rebar.native_module_loaded():
        pytest.skip("native extension not available in source-tree test mode")


class _FakeNativeBoundary:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def boundary_compile(self, pattern: str | bytes, flags: int) -> tuple[str, int, bool]:
        self.calls.append(("compile", pattern, flags))
        if pattern == "(?i)abc":
            return ("compiled", IGNORECASE_UNICODE_FLAGS, False)
        return ("compiled", flags, True)

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
        if (
            pattern == "(?i)abc"
            and flags == IGNORECASE_UNICODE_FLAGS
            and mode == "search"
            and string == "ABC"
        ):
            return ("matched", 0, len(string), (0, 3))
        if (
            pattern == b"abc"
            and flags == LOCALE_FLAGS
            and mode == "search"
            and string == b"abc"
        ):
            return ("matched", 0, len(string), (0, 3))
        return ("unsupported", 0, len(string), None)

    def scaffold_raise(self, helper_name: str) -> object:
        raise NotImplementedError(rebar._placeholder_message(helper_name))

    def scaffold_pattern_raise(self, method_name: str) -> object:
        raise NotImplementedError(rebar._pattern_placeholder_message(method_name))

    def scaffold_purge(self) -> None:
        self.calls.append(("purge",))


TARGET_FIXTURE_CASE_IDS = (
    "flag-module-search-ignorecase-str-hit",
    "flag-module-search-ignorecase-str-miss",
    "flag-module-fullmatch-ignorecase-bytes-hit",
    "flag-pattern-search-ignorecase-str-hit",
    "flag-pattern-match-ignorecase-bytes-hit",
    "flag-pattern-fullmatch-ignorecase-str-miss",
    "flag-cache-hit-bytes-ignorecase",
    "flag-cache-distinct-str-normalized",
    "flag-unsupported-inline-flag-search",
    "flag-unsupported-locale-bytes-search",
)
LITERAL_FLAG_FIXTURE_BUNDLE = _fixture_bundle(
    "literal_flag_workflows.py",
    selected_case_ids=TARGET_FIXTURE_CASE_IDS,
    expected_manifest_id="literal-flag-workflows",
    expected_operation_helper_counts=Counter(
        {
            ("module_call", "search"): 4,
            ("module_call", "fullmatch"): 1,
            ("pattern_call", "search"): 1,
            ("pattern_call", "match"): 1,
            ("pattern_call", "fullmatch"): 1,
            ("cache_workflow", None): 1,
            ("cache_distinct_workflow", None): 1,
        }
    ),
)
LITERAL_FLAG_CASES_BY_ID = {
    case.case_id: case for case in LITERAL_FLAG_FIXTURE_BUNDLE.cases
}

MODULE_IGNORECASE_CASES = (
    _module_case_from_fixture(
        LITERAL_FLAG_CASES_BY_ID["flag-module-search-ignorecase-str-hit"]
    ),
    _module_case_from_fixture(
        LITERAL_FLAG_CASES_BY_ID["flag-module-search-ignorecase-str-miss"]
    ),
    _module_case_from_fixture(
        LITERAL_FLAG_CASES_BY_ID["flag-module-fullmatch-ignorecase-bytes-hit"]
    ),
    ModuleCallCase(
        id="module-match-ignorecase-str-hit",
        helper="match",
        pattern="AbC",
        string="aBcdef",
        flags=IGNORECASE_FLAGS,
    ),
    ModuleCallCase(
        id="module-fullmatch-ignorecase-str-hit",
        helper="fullmatch",
        pattern="AbC",
        string="aBc",
        flags=IGNORECASE_FLAGS,
    ),
    ModuleCallCase(
        id="module-search-ignorecase-bytes-hit",
        helper="search",
        pattern=b"AbC",
        string=b"zzaBczz",
        flags=IGNORECASE_FLAGS,
    ),
    ModuleCallCase(
        id="module-match-ignorecase-bytes-hit",
        helper="match",
        pattern=b"AbC",
        string=b"aBcdef",
        flags=IGNORECASE_FLAGS,
    ),
    ModuleCallCase(
        id="module-match-ignorecase-bytes-miss",
        helper="match",
        pattern=b"AbC",
        string=b"zaBc",
        flags=IGNORECASE_FLAGS,
    ),
)

PATTERN_IGNORECASE_CASES = (
    _pattern_case_from_fixture(
        LITERAL_FLAG_CASES_BY_ID["flag-pattern-search-ignorecase-str-hit"]
    ),
    _pattern_case_from_fixture(
        LITERAL_FLAG_CASES_BY_ID["flag-pattern-match-ignorecase-bytes-hit"]
    ),
    _pattern_case_from_fixture(
        LITERAL_FLAG_CASES_BY_ID["flag-pattern-fullmatch-ignorecase-str-miss"]
    ),
    PatternCallCase(
        id="pattern-match-ignorecase-str-hit",
        helper="match",
        pattern="AbC",
        string="aBcdef",
        flags=IGNORECASE_FLAGS,
    ),
    PatternCallCase(
        id="pattern-fullmatch-ignorecase-str-hit",
        helper="fullmatch",
        pattern="AbC",
        string="aBc",
        flags=IGNORECASE_FLAGS,
    ),
    PatternCallCase(
        id="pattern-search-ignorecase-str-miss",
        helper="search",
        pattern="AbC",
        string="zzz",
        flags=IGNORECASE_FLAGS,
    ),
    PatternCallCase(
        id="pattern-search-ignorecase-bytes-hit",
        helper="search",
        pattern=b"AbC",
        string=b"zzaBczz",
        flags=IGNORECASE_FLAGS,
    ),
    PatternCallCase(
        id="pattern-fullmatch-ignorecase-bytes-hit",
        helper="fullmatch",
        pattern=b"AbC",
        string=b"aBc",
        flags=IGNORECASE_FLAGS,
    ),
    PatternCallCase(
        id="pattern-fullmatch-ignorecase-bytes-miss",
        helper="fullmatch",
        pattern=b"AbC",
        string=b"aBcd",
        flags=IGNORECASE_FLAGS,
    ),
)

INLINE_NATIVE_MODULE_CASE = _module_case_from_fixture(
    LITERAL_FLAG_CASES_BY_ID["flag-unsupported-inline-flag-search"]
)
LOCALE_NATIVE_MODULE_CASE = _module_case_from_fixture(
    LITERAL_FLAG_CASES_BY_ID["flag-unsupported-locale-bytes-search"]
)
NATIVE_MODULE_PARITY_CASES = (
    INLINE_NATIVE_MODULE_CASE,
    LOCALE_NATIVE_MODULE_CASE,
)
NATIVE_PATTERN_PARITY_CASES = (
    PatternCallCase(
        id="inline-flag-pattern-search",
        helper="search",
        pattern="(?i)abc",
        string="ABC",
    ),
    PatternCallCase(
        id="locale-bytes-pattern-search",
        helper="search",
        pattern=b"abc",
        string=b"abc",
        flags=LOCALE_FLAGS,
    ),
)

CACHE_HIT_BYTES_IGNORECASE_CASE = LITERAL_FLAG_CASES_BY_ID[
    "flag-cache-hit-bytes-ignorecase"
]
CACHE_DISTINCT_STR_NORMALIZED_CASE = LITERAL_FLAG_CASES_BY_ID[
    "flag-cache-distinct-str-normalized"
]

FAKE_BOUNDARY_CASES = (
    FakeBoundaryCase(
        id="inline-flag-native-boundary-search",
        pattern=INLINE_NATIVE_MODULE_CASE.pattern,
        string=INLINE_NATIVE_MODULE_CASE.string,
        flags=INLINE_NATIVE_MODULE_CASE.flags,
        compiled_flags=IGNORECASE_UNICODE_FLAGS,
        expected_calls=(
            ("purge",),
            ("compile", "(?i)abc", 0),
            ("match", "(?i)abc", IGNORECASE_UNICODE_FLAGS, "search", "ABC", 0, None),
            ("compile", "(?i)abc", 0),
            ("match", "(?i)abc", IGNORECASE_UNICODE_FLAGS, "search", "ABC", 0, None),
        ),
    ),
    FakeBoundaryCase(
        id="locale-bytes-native-boundary-search",
        pattern=LOCALE_NATIVE_MODULE_CASE.pattern,
        string=LOCALE_NATIVE_MODULE_CASE.string,
        flags=LOCALE_NATIVE_MODULE_CASE.flags,
        compiled_flags=LOCALE_FLAGS,
        expected_calls=(
            ("purge",),
            ("compile", b"abc", LOCALE_FLAGS),
            ("match", b"abc", LOCALE_FLAGS, "search", b"abc", 0, None),
            ("match", b"abc", LOCALE_FLAGS, "search", b"abc", 0, None),
        ),
    ),
)


def test_literal_flag_suite_stays_aligned_with_published_correctness_fixture() -> None:
    bundle = LITERAL_FLAG_FIXTURE_BUNDLE

    assert PUBLISHED_LITERAL_FLAG_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS
    assert bundle.manifest.path == FIXTURES_DIR / "literal_flag_workflows.py"
    assert bundle.manifest.manifest_id == bundle.expected_manifest_id
    assert len(bundle.cases) == len(bundle.expected_case_ids)
    assert {case.case_id for case in bundle.cases} == bundle.expected_case_ids
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        bundle.expected_operation_helper_counts
    )


@pytest.mark.parametrize("case", MODULE_IGNORECASE_CASES, ids=lambda case: case.id)
def test_literal_ignorecase_module_helpers_match_cpython(
    case: ModuleCallCase,
) -> None:
    observed = _call_module_helper(rebar, case)
    expected = _call_module_helper(re, case)

    assert_match_result_parity("rebar", observed, expected)
    if expected is not None:
        assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", PATTERN_IGNORECASE_CASES, ids=lambda case: case.id)
def test_literal_ignorecase_compiled_helpers_match_cpython(
    case: PatternCallCase,
) -> None:
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        "rebar",
        rebar,
        case.pattern,
        case.flags,
    )

    observed = _call_pattern_helper(observed_pattern, case)
    expected = _call_pattern_helper(expected_pattern, case)

    assert_match_result_parity("rebar", observed, expected)
    if expected is not None:
        assert_match_convenience_api_parity(observed, expected)


def test_literal_flag_compile_cache_reuse_and_distinct_entries_stay_explicit() -> None:
    distinct_pattern = case_pattern(CACHE_DISTINCT_STR_NORMALIZED_CASE)
    distinct_flags = int(
        CACHE_DISTINCT_STR_NORMALIZED_CASE.kwargs.get("distinct_flags", 0)
    )
    flagged_flags = CACHE_DISTINCT_STR_NORMALIZED_CASE.flags or 0
    alias_flags = flagged_flags | UNICODE_FLAGS

    bytes_pattern = case_pattern(CACHE_HIT_BYTES_IGNORECASE_CASE)
    bytes_flagged_flags = CACHE_HIT_BYTES_IGNORECASE_CASE.flags or 0

    default_pattern = rebar.compile(distinct_pattern, distinct_flags)
    default_again = rebar.compile(distinct_pattern, distinct_flags)
    flagged_pattern = rebar.compile(distinct_pattern, flagged_flags)
    flagged_again = rebar.compile(distinct_pattern, alias_flags)
    bytes_default_pattern = rebar.compile(bytes_pattern)
    bytes_flagged_pattern = rebar.compile(bytes_pattern, bytes_flagged_flags)
    bytes_flagged_again = rebar.compile(bytes_pattern, bytes_flagged_flags)

    assert default_pattern is default_again
    assert default_pattern is not flagged_pattern
    assert flagged_pattern is flagged_again
    assert bytes_default_pattern is not bytes_flagged_pattern
    assert bytes_flagged_pattern is bytes_flagged_again


def test_literal_flag_unsupported_paths_keep_placeholder_messages() -> None:
    with pytest.raises(
        NotImplementedError,
        match=r"rebar\.search\(\) is a scaffold placeholder",
    ):
        rebar.search("abc", "ABC", IGNORECASE_FLAGS | ASCII_FLAGS)

    with pytest.raises(
        NotImplementedError,
        match=r"rebar\.findall\(\) is a scaffold placeholder",
    ):
        rebar.findall("abc", "ABC", IGNORECASE_FLAGS)

    unsupported_pattern = rebar.compile("abc", IGNORECASE_FLAGS | ASCII_FLAGS)
    with pytest.raises(
        NotImplementedError,
        match=r"rebar\.Pattern\.search\(\) is a scaffold placeholder",
    ):
        unsupported_pattern.search("ABC")


@pytest.mark.parametrize("case", NATIVE_MODULE_PARITY_CASES, ids=lambda case: case.id)
def test_native_literal_flag_module_workflows_match_cpython(
    case: ModuleCallCase,
) -> None:
    _require_native_module()

    observed = _call_module_helper(rebar, case)
    expected = _call_module_helper(re, case)

    assert_match_result_parity("rebar", observed, expected)
    assert expected is not None
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", NATIVE_PATTERN_PARITY_CASES, ids=lambda case: case.id)
def test_native_literal_flag_compiled_workflows_match_cpython(
    case: PatternCallCase,
) -> None:
    _require_native_module()

    observed_pattern = rebar.compile(case.pattern, case.flags)
    expected_pattern = re.compile(case.pattern, case.flags)
    assert_pattern_parity("rebar", observed_pattern, expected_pattern)

    observed = _call_pattern_helper(observed_pattern, case)
    expected = _call_pattern_helper(expected_pattern, case)

    assert_match_result_parity("rebar", observed, expected)
    assert expected is not None
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", FAKE_BOUNDARY_CASES, ids=lambda case: case.id)
def test_fake_native_boundary_preserves_literal_flag_search_sequences(
    monkeypatch: pytest.MonkeyPatch,
    case: FakeBoundaryCase,
) -> None:
    fake_native = _FakeNativeBoundary()
    monkeypatch.setattr(rebar, "_native", fake_native)

    rebar.purge()

    match = rebar.search(case.pattern, case.string, case.flags)
    assert match is not None
    assert type(match) is rebar.Match
    assert match.group(0) == case.string
    assert match.span() == (0, len(case.string))

    compiled = rebar.compile(case.pattern, case.flags)
    assert type(compiled) is rebar.Pattern
    assert compiled.flags == case.compiled_flags
    assert compiled.search(case.string).span() == (0, len(case.string))

    assert fake_native.calls == list(case.expected_calls)
