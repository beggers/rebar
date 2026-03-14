from __future__ import annotations

from collections import Counter
import pathlib
import re
import sys

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
QUANTIFIED_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_nested_group_alternation_branch_local_backreference_workflows.py"
)
BROADER_RANGE_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py"
)

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar
from rebar_harness.correctness import FixtureCase, load_fixture_manifest


QUANTIFIED_FIXTURE_MANIFEST, QUANTIFIED_PUBLISHED_CASES = load_fixture_manifest(
    QUANTIFIED_FIXTURE_PATH
)
BROADER_RANGE_FIXTURE_MANIFEST, BROADER_RANGE_PUBLISHED_CASES = load_fixture_manifest(
    BROADER_RANGE_FIXTURE_PATH
)
QUANTIFIED_EXPECTED_CASE_IDS = {
    "quantified-nested-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
    "quantified-nested-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
    "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str",
    "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-str",
    "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
    "quantified-nested-group-alternation-branch-local-named-backreference-compile-metadata-str",
    "quantified-nested-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
    "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-str",
    "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-str",
    "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
}
QUANTIFIED_EXPECTED_COMPILE_PATTERNS = {
    r"a((b|c)+)\2d",
    r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
}
QUANTIFIED_EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 2,
        ("module_call", "search"): 2,
        ("pattern_call", "fullmatch"): 6,
    }
)
BROADER_RANGE_EXPECTED_CASE_IDS = {
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-c-branch-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-missing-replay-lower-bound-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-overflow-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-compile-metadata-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-b-branch-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-upper-bound-all-c-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-missing-replay-mixed-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-overflow-str",
}
BROADER_RANGE_EXPECTED_COMPILE_PATTERNS = {
    r"a((b|c){1,4})\2d",
    r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
}
BROADER_RANGE_EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 2,
        ("module_call", "search"): 4,
        ("pattern_call", "fullmatch"): 8,
    }
)
FIXTURE_CASE_SETS = (
    (
        QUANTIFIED_FIXTURE_MANIFEST,
        tuple(QUANTIFIED_PUBLISHED_CASES),
        "quantified-nested-group-alternation-branch-local-backreference-workflows",
        QUANTIFIED_EXPECTED_CASE_IDS,
        QUANTIFIED_EXPECTED_COMPILE_PATTERNS,
        QUANTIFIED_EXPECTED_OPERATION_HELPER_COUNTS,
    ),
    (
        BROADER_RANGE_FIXTURE_MANIFEST,
        tuple(BROADER_RANGE_PUBLISHED_CASES),
        "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows",
        BROADER_RANGE_EXPECTED_CASE_IDS,
        BROADER_RANGE_EXPECTED_COMPILE_PATTERNS,
        BROADER_RANGE_EXPECTED_OPERATION_HELPER_COUNTS,
    ),
)
PUBLISHED_CASES = tuple(
    case
    for _manifest, cases, _manifest_id, _expected_case_ids, _expected_patterns, _expected_counts in FIXTURE_CASE_SETS
    for case in cases
)
COMPILE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "compile")
WORKFLOW_CASES = tuple(case for case in PUBLISHED_CASES if case.operation != "compile")
NEGATIVE_CASES = (
    pytest.param(
        "module",
        r"a((b|c)+)\2d",
        "search",
        "zzabcdzz",
        id="module-numbered-search-miss-mismatched-replay",
    ),
    pytest.param(
        "pattern",
        r"a((b|c)+)\2d",
        "fullmatch",
        "acbd",
        id="pattern-numbered-fullmatch-miss-short-replay",
    ),
    pytest.param(
        "module",
        r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        "search",
        "zzacbdzz",
        id="module-named-search-miss-short-replay",
    ),
    pytest.param(
        "pattern",
        r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        "fullmatch",
        "abcd",
        id="pattern-named-fullmatch-miss-mismatched-replay",
    ),
    pytest.param(
        "module",
        r"a((b|c){1,4})\2d",
        "search",
        "zzabcbcdzz",
        id="module-broader-range-numbered-search-miss-missing-replay",
    ),
    pytest.param(
        "pattern",
        r"a((b|c){1,4})\2d",
        "fullmatch",
        "abbbbbbd",
        id="pattern-broader-range-numbered-fullmatch-miss-overflow",
    ),
    pytest.param(
        "module",
        r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        "search",
        "zzabcbcdzz",
        id="module-broader-range-named-search-miss-missing-replay",
    ),
    pytest.param(
        "pattern",
        r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        "fullmatch",
        "accccccd",
        id="pattern-broader-range-named-fullmatch-miss-overflow",
    ),
)
MISSING_GROUP_DEFAULT = object()


def _case_pattern(case: FixtureCase) -> str | bytes:
    if case.pattern is not None:
        return case.pattern_payload()
    return case.args[0]


def _assert_pattern_parity(
    backend_name: str,
    observed: object,
    expected: re.Pattern[str] | re.Pattern[bytes],
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
    expected: re.Match[str] | re.Match[bytes],
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


def _assert_match_convenience_api_parity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    for group_index in range(expected.re.groups + 1):
        assert observed[group_index] == expected[group_index]

    ordered_group_names = tuple(expected.re.groupindex)
    for group_name in ordered_group_names:
        assert observed[group_name] == expected[group_name]

    templates = [r"<\g<0>>"]
    if expected.re.groups >= 1:
        templates.append(r"<\1>")
    if expected.re.groups >= 2:
        templates.append(r"<\1:\2>")
    if ordered_group_names:
        templates.append(
            "<" + ":".join(fr"\g<{group_name}>" for group_name in ordered_group_names) + ">"
        )

    for template in templates:
        assert observed.expand(template) == expected.expand(template)


def test_parity_suite_stays_aligned_with_published_correctness_fixture() -> None:
    for (
        manifest,
        cases,
        expected_manifest_id,
        expected_case_ids,
        expected_compile_patterns,
        expected_operation_helper_counts,
    ) in FIXTURE_CASE_SETS:
        assert manifest.manifest_id == expected_manifest_id
        assert len(cases) == len(expected_case_ids)
        assert {case.case_id for case in cases} == expected_case_ids
        assert {_case_pattern(case) for case in cases} == expected_compile_patterns
        assert Counter((case.operation, case.helper) for case in cases) == (
            expected_operation_helper_counts
        )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.compile(case.pattern_payload(), case.flags or 0)
    expected = re.compile(case.pattern_payload(), case.flags or 0)

    assert observed is backend.compile(case.pattern_payload(), case.flags or 0)
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
        observed_pattern = backend.compile(case.pattern_payload(), case.flags or 0)
        expected_pattern = re.compile(case.pattern_payload(), case.flags or 0)
        _assert_pattern_parity(backend_name, observed_pattern, expected_pattern)
        observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
        expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    _assert_match_parity(backend_name, observed, expected)
    _assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize(("target", "pattern", "helper", "text"), NEGATIVE_CASES)
def test_mismatched_replay_paths_match_cpython(
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
