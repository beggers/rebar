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
    / "quantified_nested_group_callable_replacement_workflows.py"
)

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

from rebar_harness.correctness import FixtureCase, load_fixture_manifest


FIXTURE_MANIFEST, PUBLISHED_CASES = load_fixture_manifest(FIXTURE_PATH)
EXPECTED_CASE_IDS = {
    "module-sub-callable-quantified-nested-group-numbered-lower-bound-str",
    "module-subn-callable-quantified-nested-group-numbered-first-match-only-str",
    "pattern-sub-callable-quantified-nested-group-numbered-repeated-outer-capture-str",
    "pattern-subn-callable-quantified-nested-group-numbered-first-match-only-str",
    "module-sub-callable-quantified-nested-group-named-lower-bound-str",
    "module-subn-callable-quantified-nested-group-named-first-match-only-str",
    "pattern-sub-callable-quantified-nested-group-named-repeated-outer-capture-str",
    "pattern-subn-callable-quantified-nested-group-named-first-match-only-str",
}
EXPECTED_COMPILE_PATTERNS = {
    r"a((bc)+)d",
    r"a(?P<outer>(?P<inner>bc)+)d",
}
EXPECTED_OPERATION_HELPER_COUNTS = Counter({
    ("module_call", "sub"): 2,
    ("module_call", "subn"): 2,
    ("pattern_call", "sub"): 2,
    ("pattern_call", "subn"): 2,
})
MODULE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "module_call")
PATTERN_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "pattern_call")


def _case_pattern(case: FixtureCase) -> str:
    if case.pattern is not None:
        return case.pattern_payload()
    return case.args[0]


def test_parity_suite_stays_aligned_with_published_correctness_fixture() -> None:
    assert FIXTURE_MANIFEST.manifest_id == (
        "quantified-nested-group-callable-replacement-workflows"
    )
    assert len(PUBLISHED_CASES) == len(EXPECTED_CASE_IDS)
    assert {case.case_id for case in PUBLISHED_CASES} == EXPECTED_CASE_IDS
    assert {_case_pattern(case) for case in PUBLISHED_CASES} == EXPECTED_COMPILE_PATTERNS
    assert Counter((case.operation, case.helper) for case in PUBLISHED_CASES) == (
        EXPECTED_OPERATION_HELPER_COUNTS
    )


@pytest.mark.parametrize(
    "pattern",
    sorted(EXPECTED_COMPILE_PATTERNS),
)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: str,
) -> None:
    _, backend = regex_backend

    observed = backend.compile(pattern)
    expected = re.compile(pattern)

    assert observed is backend.compile(pattern)
    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


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
    _, backend = regex_backend
    assert case.helper is not None

    observed_pattern = backend.compile(case.pattern_payload(), case.flags or 0)
    expected_pattern = re.compile(case.pattern_payload(), case.flags or 0)

    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed == expected
