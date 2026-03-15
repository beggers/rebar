from __future__ import annotations

from collections import Counter
import pathlib
import re
import sys

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_nested_group_alternation_callable_replacement_workflows.py"
)

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar
from rebar_harness.correctness import FixtureCase, load_fixture_manifest
from tests.python.callable_replacement_support import (
    assert_callable_replacement_match_parity,
)


FIXTURE_MANIFEST, PUBLISHED_CASES = load_fixture_manifest(FIXTURE_PATH)
EXPECTED_CASE_IDS = {
    "module-sub-callable-quantified-nested-group-alternation-numbered-lower-bound-b-branch-str",
    "module-subn-callable-quantified-nested-group-alternation-numbered-first-match-only-c-branch-str",
    "pattern-sub-callable-quantified-nested-group-alternation-numbered-mixed-branches-str",
    "pattern-subn-callable-quantified-nested-group-alternation-numbered-first-match-only-b-branch-str",
    "module-sub-callable-quantified-nested-group-alternation-named-lower-bound-c-branch-str",
    "module-subn-callable-quantified-nested-group-alternation-named-first-match-only-b-branch-str",
    "pattern-sub-callable-quantified-nested-group-alternation-named-mixed-branches-str",
    "pattern-subn-callable-quantified-nested-group-alternation-named-first-match-only-c-branch-str",
}
EXPECTED_COMPILE_PATTERNS = {
    r"a((b|c)+)d",
    r"a(?P<outer>(?P<inner>b|c)+)d",
}
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 2,
        ("module_call", "subn"): 2,
        ("pattern_call", "sub"): 2,
        ("pattern_call", "subn"): 2,
    }
)
MODULE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "module_call")
PATTERN_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "pattern_call")
NEGATIVE_CASES = (
    pytest.param(
        "module",
        r"a((b|c)+)d",
        "sub",
        "zzadzz",
        0,
        "zzadzz",
        id="module-numbered-sub-no-match-too-short",
    ),
    pytest.param(
        "module",
        r"a((b|c)+)d",
        "subn",
        "zzabedzz",
        0,
        ("zzabedzz", 0),
        id="module-numbered-subn-no-match-invalid-branch",
    ),
    pytest.param(
        "pattern",
        r"a(?P<outer>(?P<inner>b|c)+)d",
        "sub",
        "zzadzz",
        0,
        "zzadzz",
        id="pattern-named-sub-no-match-too-short",
    ),
    pytest.param(
        "pattern",
        r"a(?P<outer>(?P<inner>b|c)+)d",
        "subn",
        "zzabedzz",
        0,
        ("zzabedzz", 0),
        id="pattern-named-subn-no-match-invalid-branch",
    ),
)


def _case_pattern(case: FixtureCase) -> str:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, str)
    return pattern


def _case_string(case: FixtureCase) -> str:
    string_index = 2 if case.operation == "module_call" else 1
    string = case.args[string_index]
    assert isinstance(string, str)
    return string


def _case_count(case: FixtureCase) -> int:
    count_index = 3 if case.operation == "module_call" else 2
    if len(case.args) > count_index:
        return int(case.args[count_index])
    return 0


def _case_group_names(case: FixtureCase) -> tuple[str, ...]:
    return tuple(re.compile(_case_pattern(case), case.flags or 0).groupindex)


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


def test_parity_suite_stays_aligned_with_published_correctness_fixture() -> None:
    assert FIXTURE_MANIFEST.manifest_id == (
        "quantified-nested-group-alternation-callable-replacement-workflows"
    )
    assert len(PUBLISHED_CASES) == len(EXPECTED_CASE_IDS)
    assert {case.case_id for case in PUBLISHED_CASES} == EXPECTED_CASE_IDS
    assert {_case_pattern(case) for case in PUBLISHED_CASES} == EXPECTED_COMPILE_PATTERNS
    assert Counter((case.operation, case.helper) for case in PUBLISHED_CASES) == (
        EXPECTED_OPERATION_HELPER_COUNTS
    )


@pytest.mark.parametrize("pattern", sorted(EXPECTED_COMPILE_PATTERNS))
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: str,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.compile(pattern)
    expected = re.compile(pattern)

    assert observed is backend.compile(pattern)
    _assert_pattern_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed_pattern = backend.compile(case.pattern_payload(), case.flags or 0)
    expected_pattern = re.compile(case.pattern_payload(), case.flags or 0)
    _assert_pattern_parity(backend_name, observed_pattern, expected_pattern)

    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


@pytest.mark.parametrize("case", PUBLISHED_CASES, ids=lambda case: case.case_id)
def test_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=_case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
        use_compiled_pattern=case.operation == "pattern_call",
    )


@pytest.mark.parametrize(
    ("target", "pattern", "helper", "text", "count", "expected_result"),
    NEGATIVE_CASES,
)
def test_no_match_paths_leave_input_unchanged(
    regex_backend: tuple[str, object],
    target: str,
    pattern: str,
    helper: str,
    text: str,
    count: int,
    expected_result: str | tuple[str, int],
) -> None:
    _, backend = regex_backend
    callback_calls: list[object] = []

    def replacement(match: object) -> str:
        callback_calls.append(match)
        return "X"

    if target == "module":
        observed = getattr(backend, helper)(pattern, replacement, text, count=count)
        expected = getattr(re, helper)(pattern, lambda _match: "X", text, count=count)
    else:
        observed_pattern = backend.compile(pattern)
        expected_pattern = re.compile(pattern)
        observed = getattr(observed_pattern, helper)(replacement, text, count=count)
        expected = getattr(expected_pattern, helper)(lambda _match: "X", text, count=count)

    assert observed == expected == expected_result
    assert callback_calls == []
