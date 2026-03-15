from __future__ import annotations

from collections import Counter
import re

import pytest

from rebar_harness.correctness import FixtureCase, load_fixture_manifest
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    compile_with_cpython_parity,
    select_published_fixture_paths,
)


FIXTURE_PATH = FIXTURES_DIR / "nested_group_replacement_workflows.py"
EXPECTED_PUBLISHED_FIXTURE_PATHS = (FIXTURE_PATH,)
PUBLISHED_FIXTURE_PATHS = select_published_fixture_paths(EXPECTED_PUBLISHED_FIXTURE_PATHS)
FIXTURE_MANIFEST, PUBLISHED_CASES = load_fixture_manifest(FIXTURE_PATH)
EXPECTED_CASE_IDS = {
    "module-sub-template-nested-group-numbered-str",
    "module-subn-template-nested-group-numbered-str",
    "pattern-sub-template-nested-group-numbered-str",
    "pattern-subn-template-nested-group-numbered-str",
    "module-sub-template-nested-group-named-str",
    "module-subn-template-nested-group-named-str",
    "pattern-sub-template-nested-group-named-str",
    "pattern-subn-template-nested-group-named-str",
}
EXPECTED_COMPILE_PATTERNS = {
    r"a((b))d",
    r"a(?P<outer>(?P<inner>b))d",
}
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 2,
        ("module_call", "subn"): 2,
        ("pattern_call", "sub"): 2,
        ("pattern_call", "subn"): 2,
    }
)
SUPPLEMENTAL_NO_MATCH_CASES = (
    pytest.param(
        False,
        "sub",
        r"a((b))d",
        r"\1x",
        "zzadzz",
        0,
        id="module-numbered-sub-no-match",
    ),
    pytest.param(
        False,
        "subn",
        r"a((b))d",
        r"\2x",
        "zzadzz",
        1,
        id="module-numbered-subn-no-match",
    ),
    pytest.param(
        True,
        "sub",
        r"a((b))d",
        r"\1x",
        "zzadzz",
        0,
        id="pattern-numbered-sub-no-match",
    ),
    pytest.param(
        True,
        "subn",
        r"a((b))d",
        r"\2x",
        "zzadzz",
        1,
        id="pattern-numbered-subn-no-match",
    ),
    pytest.param(
        False,
        "sub",
        r"a(?P<outer>(?P<inner>b))d",
        r"\g<outer>x",
        "zzadzz",
        0,
        id="module-named-sub-no-match",
    ),
    pytest.param(
        False,
        "subn",
        r"a(?P<outer>(?P<inner>b))d",
        r"\g<inner>x",
        "zzadzz",
        1,
        id="module-named-subn-no-match",
    ),
    pytest.param(
        True,
        "sub",
        r"a(?P<outer>(?P<inner>b))d",
        r"\g<outer>x",
        "zzadzz",
        0,
        id="pattern-named-sub-no-match",
    ),
    pytest.param(
        True,
        "subn",
        r"a(?P<outer>(?P<inner>b))d",
        r"\g<inner>x",
        "zzadzz",
        1,
        id="pattern-named-subn-no-match",
    ),
)


def _case_pattern(case: FixtureCase) -> str:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, str)
    return pattern


COMPILE_PATTERNS = tuple(sorted({_case_pattern(case) for case in PUBLISHED_CASES}))
MODULE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "module_call")
PATTERN_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "pattern_call")


def test_parity_suite_stays_aligned_with_published_correctness_fixture() -> None:
    assert PUBLISHED_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS
    assert FIXTURE_MANIFEST.manifest_id == "nested-group-replacement-workflows"
    assert len(PUBLISHED_CASES) == len(EXPECTED_CASE_IDS)
    assert {case.case_id for case in PUBLISHED_CASES} == EXPECTED_CASE_IDS
    assert set(COMPILE_PATTERNS) == EXPECTED_COMPILE_PATTERNS
    assert Counter((case.operation, case.helper) for case in PUBLISHED_CASES) == (
        EXPECTED_OPERATION_HELPER_COUNTS
    )


@pytest.mark.parametrize("pattern", COMPILE_PATTERNS)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: str,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, pattern)


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern_payload(),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


@pytest.mark.parametrize(
    ("use_compiled_pattern", "helper", "pattern", "replacement", "string", "count"),
    SUPPLEMENTAL_NO_MATCH_CASES,
)
def test_no_match_replacement_paths_match_cpython(
    regex_backend: tuple[str, object],
    use_compiled_pattern: bool,
    helper: str,
    pattern: str,
    replacement: str,
    string: str,
    count: int,
) -> None:
    backend_name, backend = regex_backend

    if use_compiled_pattern:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        observed = getattr(observed_pattern, helper)(replacement, string, count=count)
        expected = getattr(expected_pattern, helper)(replacement, string, count=count)
    else:
        observed = getattr(backend, helper)(pattern, replacement, string, count=count)
        expected = getattr(re, helper)(pattern, replacement, string, count=count)

    assert observed == expected
