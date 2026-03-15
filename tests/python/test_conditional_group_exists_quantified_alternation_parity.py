from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import pathlib
import re

import pytest

import rebar
from rebar_harness.correctness import FixtureCase, load_fixture_manifest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_quantified_alternation_workflows.py"
)
NUMBERED_PATTERN = r"a(b)?c(?(1)(de|df)|(eg|eh)){2}"
NAMED_PATTERN = r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}"

FIXTURE_MANIFEST, PUBLISHED_CASES = load_fixture_manifest(FIXTURE_PATH)
EXPECTED_CASE_IDS = frozenset(
    {
        "conditional-group-exists-quantified-alternation-compile-metadata-str",
        "conditional-group-exists-quantified-alternation-module-search-present-first-arm-str",
        "conditional-group-exists-quantified-alternation-pattern-fullmatch-present-second-arm-str",
        "conditional-group-exists-quantified-alternation-module-search-absent-first-arm-str",
        "conditional-group-exists-quantified-alternation-pattern-fullmatch-absent-second-arm-str",
        "named-conditional-group-exists-quantified-alternation-compile-metadata-str",
        "named-conditional-group-exists-quantified-alternation-module-search-present-first-arm-str",
        "named-conditional-group-exists-quantified-alternation-pattern-fullmatch-present-second-arm-str",
        "named-conditional-group-exists-quantified-alternation-module-search-absent-first-arm-str",
        "named-conditional-group-exists-quantified-alternation-pattern-fullmatch-absent-second-arm-str",
    }
)
EXPECTED_PATTERNS = frozenset({NUMBERED_PATTERN, NAMED_PATTERN})
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 2,
        ("module_call", "search"): 4,
        ("pattern_call", "fullmatch"): 4,
    }
)
COMPILE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "compile")
WORKFLOW_CASES = tuple(case for case in PUBLISHED_CASES if case.operation != "compile")
MISSING_GROUP_DEFAULT = object()


@dataclass(frozen=True)
class MatchTraceCase:
    id: str
    pattern: str
    text: str


def _case_pattern(case: FixtureCase) -> str:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, str)
    return pattern


def _assert_pattern_parity(
    backend_name: str,
    observed: object,
    expected: re.Pattern[str],
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Pattern
    else:
        assert type(observed) is type(expected)

    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


def _assert_match_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str],
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Match
    else:
        assert type(observed) is type(expected)

    group_indexes = tuple(range(expected.re.groups + 1))

    assert observed.group(0) == expected.group(0)
    assert observed.group(*group_indexes) == expected.group(*group_indexes)

    for group_index in range(1, expected.re.groups + 1):
        assert observed.group(group_index) == expected.group(group_index)
        assert observed.span(group_index) == expected.span(group_index)
        assert observed.start(group_index) == expected.start(group_index)
        assert observed.end(group_index) == expected.end(group_index)

    assert observed.groups() == expected.groups()
    assert observed.groups(MISSING_GROUP_DEFAULT) == expected.groups(MISSING_GROUP_DEFAULT)
    assert observed.groupdict() == expected.groupdict()
    assert observed.groupdict(MISSING_GROUP_DEFAULT) == expected.groupdict(
        MISSING_GROUP_DEFAULT
    )
    assert observed.string == expected.string
    assert observed.pos == expected.pos
    assert observed.endpos == expected.endpos
    assert observed.span() == expected.span()
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup
    assert hasattr(observed, "regs") == hasattr(expected, "regs")
    if hasattr(expected, "regs"):
        assert tuple(observed.regs) == tuple(expected.regs)

    _assert_pattern_parity(backend_name, observed.re, expected.re)

    for group_name in expected.re.groupindex:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)
        assert observed.start(group_name) == expected.start(group_name)
        assert observed.end(group_name) == expected.end(group_name)


def _build_extra_fullmatch_cases() -> tuple[MatchTraceCase, ...]:
    return (
        MatchTraceCase(
            id="numbered-pattern-fullmatch-present-mixed-arms",
            pattern=NUMBERED_PATTERN,
            text="abcdedf",
        ),
        MatchTraceCase(
            id="numbered-pattern-fullmatch-absent-mixed-arms",
            pattern=NUMBERED_PATTERN,
            text="acegeh",
        ),
        MatchTraceCase(
            id="named-pattern-fullmatch-present-mixed-arms",
            pattern=NAMED_PATTERN,
            text="abcdedf",
        ),
        MatchTraceCase(
            id="named-pattern-fullmatch-absent-mixed-arms",
            pattern=NAMED_PATTERN,
            text="acegeh",
        ),
    )


def _build_no_match_cases() -> tuple[object, ...]:
    case_templates = (
        (
            "module",
            "search",
            "zzabcdehzz",
            "miss-partial-present-second-arm",
        ),
        (
            "module",
            "search",
            "zzacegedzz",
            "miss-partial-absent-second-arm",
        ),
        (
            "module",
            "search",
            "zzadzz",
            "miss-too-short",
        ),
        (
            "module",
            "search",
            "zzabcegzz",
            "miss-else-arm-while-capture-present",
        ),
        (
            "pattern",
            "fullmatch",
            "abcdeh",
            "miss-partial-present-second-arm",
        ),
        (
            "pattern",
            "fullmatch",
            "aceged",
            "miss-partial-absent-second-arm",
        ),
        (
            "pattern",
            "fullmatch",
            "ad",
            "miss-too-short",
        ),
        (
            "pattern",
            "fullmatch",
            "abceg",
            "miss-else-arm-while-capture-present",
        ),
    )
    pattern_variants = (
        ("numbered", NUMBERED_PATTERN),
        ("named", NAMED_PATTERN),
    )

    cases: list[object] = []
    for variant_name, pattern in pattern_variants:
        for target, helper, text, case_suffix in case_templates:
            cases.append(
                pytest.param(
                    target,
                    pattern,
                    helper,
                    text,
                    id=f"{target}-{variant_name}-{helper}-{case_suffix}",
                )
            )
    return tuple(cases)


EXTRA_FULLMATCH_CASES = _build_extra_fullmatch_cases()
NO_MATCH_CASES = _build_no_match_cases()


def test_parity_suite_stays_aligned_with_published_correctness_fixture() -> None:
    assert FIXTURE_MANIFEST.manifest_id == (
        "conditional-group-exists-quantified-alternation-workflows"
    )
    assert len(PUBLISHED_CASES) == len(EXPECTED_CASE_IDS)
    assert {case.case_id for case in PUBLISHED_CASES} == EXPECTED_CASE_IDS
    assert {_case_pattern(case) for case in PUBLISHED_CASES} == EXPECTED_PATTERNS
    assert Counter((case.operation, case.helper) for case in PUBLISHED_CASES) == (
        EXPECTED_OPERATION_HELPER_COUNTS
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    pattern = case.pattern_payload()
    assert isinstance(pattern, str)

    observed = backend.compile(pattern, case.flags or 0)
    expected = re.compile(pattern, case.flags or 0)

    assert observed is backend.compile(pattern, case.flags or 0)
    _assert_pattern_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", WORKFLOW_CASES, ids=lambda case: case.case_id)
def test_published_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    if case.operation == "module_call":
        observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
        expected = getattr(re, case.helper)(*case.args, **case.kwargs)
    else:
        pattern = case.pattern_payload()
        assert isinstance(pattern, str)
        observed_pattern = backend.compile(pattern, case.flags or 0)
        expected_pattern = re.compile(pattern, case.flags or 0)
        _assert_pattern_parity(backend_name, observed_pattern, expected_pattern)
        observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
        expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    _assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", EXTRA_FULLMATCH_CASES, ids=lambda case: case.id)
def test_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: MatchTraceCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern = backend.compile(case.pattern)
    expected_pattern = re.compile(case.pattern)

    _assert_pattern_parity(backend_name, observed_pattern, expected_pattern)

    observed = observed_pattern.fullmatch(case.text)
    expected = expected_pattern.fullmatch(case.text)

    assert observed is not None
    assert expected is not None
    _assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize(("target", "pattern", "helper", "text"), NO_MATCH_CASES)
def test_no_match_paths_match_cpython(
    regex_backend: tuple[str, object],
    target: str,
    pattern: str,
    helper: str,
    text: str,
) -> None:
    backend_name, backend = regex_backend

    if target == "module":
        observed = getattr(backend, helper)(pattern, text)
        expected = getattr(re, helper)(pattern, text)
    else:
        observed_pattern = backend.compile(pattern)
        expected_pattern = re.compile(pattern)
        _assert_pattern_parity(backend_name, observed_pattern, expected_pattern)
        observed = getattr(observed_pattern, helper)(text)
        expected = getattr(expected_pattern, helper)(text)

    assert observed is None
    assert expected is None
