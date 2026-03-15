from __future__ import annotations

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
    / "collection_replacement_workflows.py"
)

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


from rebar_harness.correctness import FixtureCase, load_fixture_manifest
from tests.python.test_callable_replacement_parity_suite import (
    assert_callable_replacement_match_parity,
)


FIXTURE_MANIFEST, PUBLISHED_CASES = load_fixture_manifest(FIXTURE_PATH)
PARITY_VARIANTS = (
    pytest.param("sub", 0, False, id="module-sub-replace-all"),
    pytest.param("subn", 1, False, id="module-subn-first-match-only"),
    pytest.param("sub", 0, True, id="pattern-sub-replace-all"),
    pytest.param("subn", 1, True, id="pattern-subn-first-match-only"),
)


def _raw_cases_by_id() -> dict[str, dict[str, object]]:
    raw_cases = FIXTURE_MANIFEST.raw.get("cases", [])
    assert isinstance(raw_cases, list)
    return {
        str(raw_case["id"]): raw_case
        for raw_case in raw_cases
        if isinstance(raw_case, dict) and "id" in raw_case
    }


def _callable_case() -> FixtureCase:
    cases = [case for case in PUBLISHED_CASES if case.case_id == "module-sub-callable-str"]
    assert len(cases) == 1
    return cases[0]


def _pattern(case: FixtureCase) -> str:
    pattern = case.args[0]
    assert isinstance(pattern, str)
    return pattern


def _string(case: FixtureCase) -> str:
    string = case.args[2]
    assert isinstance(string, str)
    return string


def test_literal_callable_case_stays_aligned_with_published_collection_fixture() -> None:
    case = _callable_case()
    raw_case = _raw_cases_by_id()[case.case_id]
    raw_args = raw_case.get("args", [])

    assert FIXTURE_MANIFEST.manifest_id == "collection-replacement-workflows"
    assert case.operation == "module_call"
    assert case.helper == "sub"
    assert _pattern(case) == "abc"
    assert _string(case) == "abcabc"
    assert callable(case.args[1])
    assert "callable-replacement" in case.categories
    assert "str" in case.categories
    assert isinstance(raw_args, list)
    assert raw_args[1] == {"type": "callable_constant", "value": "x"}


@pytest.mark.parametrize(
    ("helper", "count", "use_compiled_pattern"),
    PARITY_VARIANTS,
)
def test_literal_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    _, backend = regex_backend
    case = _callable_case()

    def replacement(_match: object) -> str:
        return "x"

    if use_compiled_pattern:
        observed_target = backend.compile(_pattern(case))
        expected_target = re.compile(_pattern(case))
        observed = getattr(observed_target, helper)(replacement, _string(case), count=count)
        expected = getattr(expected_target, helper)(replacement, _string(case), count=count)
    else:
        observed = getattr(backend, helper)(
            _pattern(case),
            replacement,
            _string(case),
            count=count,
        )
        expected = getattr(re, helper)(
            _pattern(case),
            replacement,
            _string(case),
            count=count,
        )

    assert observed == expected


@pytest.mark.parametrize(
    ("helper", "count", "use_compiled_pattern"),
    PARITY_VARIANTS,
)
def test_literal_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    count: int,
    use_compiled_pattern: bool,
) -> None:
    backend_name, backend = regex_backend
    case = _callable_case()

    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=helper,
        pattern=_pattern(case),
        string=_string(case),
        count=count,
        use_compiled_pattern=use_compiled_pattern,
    )
