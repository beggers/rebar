from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

import rebar
from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    SelectedCaseBundleSpec,
    assert_fixture_bundle_contract,
    assert_match_convenience_api_parity,
    assert_match_result_parity,
    assert_pattern_parity,
    case_pattern,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    load_selected_case_fixture_bundles,
)


MODULE_WORKFLOW_FIXTURE_PATH = FIXTURES_DIR / "module_workflow_surface.py"
EXPECTED_CASE_IDS = (
    "workflow-compile-str-literal",
    "workflow-compile-str-anchored-literal",
    "workflow-compile-str-verbose-regression",
    "workflow-compile-bytes-literal",
    "workflow-pattern-search-str",
    "workflow-pattern-match-str",
    "workflow-pattern-fullmatch-bytes",
    "workflow-cache-hit-str",
    "workflow-cache-hit-bytes",
    "workflow-purge-reset-str",
    "workflow-escape-str",
    "workflow-escape-bytes",
)
EXPECTED_PATTERNS = frozenset(
    {
        "abc",
        "^abc$",
        "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
        b"abc",
        b"123",
        "cache-me",
        b"cache-me",
        "purge-me",
        "a-b.c",
        b"a-b.c",
    }
)
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 4,
        ("pattern_call", "search"): 1,
        ("pattern_call", "match"): 1,
        ("pattern_call", "fullmatch"): 1,
        ("cache_workflow", None): 2,
        ("purge_workflow", None): 1,
        ("module_call", "escape"): 2,
    }
)
SELECTED_CASE_BUNDLE_SPECS = (
    SelectedCaseBundleSpec(
        fixture_name="module_workflow_surface.py",
        expected_manifest_id="module-workflow-surface",
        selected_case_ids=EXPECTED_CASE_IDS,
        expected_patterns=EXPECTED_PATTERNS,
        expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
        expected_text_models=frozenset({"bytes", "str"}),
    ),
)
(MODULE_WORKFLOW_BUNDLE,) = load_selected_case_fixture_bundles(
    SELECTED_CASE_BUNDLE_SPECS
)

COMPILE_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "compile")
VERBOSE_COMPILE_CASE_ID = "workflow-compile-str-verbose-regression"
(VERBOSE_COMPILE_CASE,) = tuple(
    case for case in COMPILE_CASES if case.case_id == VERBOSE_COMPILE_CASE_ID
)
PATTERN_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "pattern_call")
CACHE_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "cache_workflow")
PURGE_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "purge_workflow")
ESCAPE_CASES = tuple(
    case
    for case in fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "module_call")
    if case.helper == "escape"
)


@dataclass(frozen=True)
class VerboseCompileWorkflowCase:
    case_id: str
    helper: str
    text: str
    expected_group0: str | None
    expected_key: str | None
    expected_span: tuple[int, int] | None


VERBOSE_COMPILE_WORKFLOW_CASES = (
    VerboseCompileWorkflowCase(
        case_id="fullmatch-digits-without-literal-spaces",
        helper="fullmatch",
        text="ENV_VAR=123",
        expected_group0="ENV_VAR=123",
        expected_key="ENV_VAR",
        expected_span=(0, 11),
    ),
    VerboseCompileWorkflowCase(
        case_id="fullmatch-alpha-with-extra-whitespace",
        helper="fullmatch",
        text="ENV_VAR   =   ABCD",
        expected_group0="ENV_VAR   =   ABCD",
        expected_key="ENV_VAR",
        expected_span=(0, 18),
    ),
    VerboseCompileWorkflowCase(
        case_id="search-multiline-middle-line-digits",
        helper="search",
        text="prefix\nENV_VAR = 123\nsuffix",
        expected_group0="ENV_VAR = 123",
        expected_key="ENV_VAR",
        expected_span=(7, 20),
    ),
    VerboseCompileWorkflowCase(
        case_id="search-multiline-middle-line-alpha",
        helper="search",
        text="prefix\nENV_VAR=ABCD\nsuffix",
        expected_group0="ENV_VAR=ABCD",
        expected_key="ENV_VAR",
        expected_span=(7, 19),
    ),
    VerboseCompileWorkflowCase(
        case_id="fullmatch-rejects-lowercase-key",
        helper="fullmatch",
        text="env_var = 123",
        expected_group0=None,
        expected_key=None,
        expected_span=None,
    ),
    VerboseCompileWorkflowCase(
        case_id="search-rejects-too-many-digits",
        helper="search",
        text="prefix\nENV_VAR = 12345\nsuffix",
        expected_group0=None,
        expected_key=None,
        expected_span=None,
    ),
)


def _compile_verbose_regression_pattern(
    backend_name: str,
    backend: object,
) -> tuple[object, re.Pattern[str]]:
    pattern = case_pattern(VERBOSE_COMPILE_CASE)
    assert isinstance(pattern, str)

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        VERBOSE_COMPILE_CASE.flags or 0,
    )

    assert expected_pattern.flags == int(re.MULTILINE | re.VERBOSE | re.UNICODE)
    assert expected_pattern.groupindex == {"key": 1}
    return observed_pattern, expected_pattern


def _assert_verbose_compile_case_matches_cpython(
    backend_name: str,
    observed_pattern: object,
    expected_pattern: re.Pattern[str],
    case: VerboseCompileWorkflowCase,
) -> None:
    observed = getattr(observed_pattern, case.helper)(case.text)
    expected = getattr(expected_pattern, case.helper)(case.text)

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)

    if case.expected_group0 is None:
        assert observed is None
        assert expected is None
        return

    assert observed is not None
    assert expected is not None
    assert observed.group(0) == expected.group(0) == case.expected_group0
    assert observed.group("key") == expected.group("key") == case.expected_key
    assert observed.groupdict() == expected.groupdict() == {"key": case.expected_key}
    assert observed.span() == expected.span() == case.expected_span
    assert_match_convenience_api_parity(observed, expected)


def test_module_workflow_parity_suite_stays_aligned_with_published_fixture() -> None:
    bundle = MODULE_WORKFLOW_BUNDLE

    assert bundle.manifest.path == MODULE_WORKFLOW_FIXTURE_PATH
    assert bundle.manifest.manifest_id == "module-workflow-surface"
    assert_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)
    assert tuple(case.case_id for case in bundle.cases) == EXPECTED_CASE_IDS
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        EXPECTED_OPERATION_HELPER_COUNTS
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend

    compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )

@pytest.mark.parametrize(
    "case", VERBOSE_COMPILE_WORKFLOW_CASES, ids=lambda case: case.case_id
)
def test_verbose_compile_workflow_contract_matches_cpython(
    regex_backend: tuple[str, object],
    case: VerboseCompileWorkflowCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = _compile_verbose_regression_pattern(
        backend_name,
        backend,
    )

    _assert_verbose_compile_case_matches_cpython(
        backend_name,
        observed_pattern,
        expected_pattern,
        case,
    )


@pytest.mark.parametrize(
    "case", VERBOSE_COMPILE_WORKFLOW_CASES, ids=lambda case: case.case_id
)
def test_verbose_compile_purge_workflow_contract_matches_cpython(
    regex_backend: tuple[str, object],
    case: VerboseCompileWorkflowCase,
) -> None:
    backend_name, backend = regex_backend
    observed_before, expected_before = _compile_verbose_regression_pattern(
        backend_name,
        backend,
    )

    observed_purge_result = backend.purge()
    expected_purge_result = re.purge()

    assert observed_purge_result is None
    assert observed_purge_result == expected_purge_result

    observed_after, expected_after = _compile_verbose_regression_pattern(
        backend_name,
        backend,
    )

    assert observed_before is not observed_after
    assert expected_before is not expected_after
    _assert_verbose_compile_case_matches_cpython(
        backend_name,
        observed_after,
        expected_after,
        case,
    )


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_compiled_pattern_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert_match_result_parity(backend_name, observed, expected)
    assert expected is not None
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", CACHE_CASES, ids=lambda case: case.case_id)
def test_compile_cache_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    pattern = case_pattern(case)
    flags = case.flags or 0

    observed_first, expected_first = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        flags,
    )
    observed_second = backend.compile(pattern, flags)
    expected_second = re.compile(pattern, flags)

    assert observed_first is observed_second
    assert expected_first is expected_second
    assert_pattern_parity(backend_name, observed_second, expected_second)


@pytest.mark.parametrize("case", PURGE_CASES, ids=lambda case: case.case_id)
def test_purge_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    pattern = case_pattern(case)
    flags = case.flags or 0

    observed_before, expected_before = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        flags,
    )
    assert observed_before is backend.compile(pattern, flags)
    assert expected_before is re.compile(pattern, flags)

    observed_purge_result = backend.purge()
    expected_purge_result = re.purge()
    assert observed_purge_result is None
    assert observed_purge_result == expected_purge_result

    observed_after = backend.compile(pattern, flags)
    expected_after = re.compile(pattern, flags)

    assert observed_before is not observed_after
    assert expected_before is not expected_after
    assert observed_after is backend.compile(pattern, flags)
    assert expected_after is re.compile(pattern, flags)
    assert_pattern_parity(backend_name, observed_after, expected_after)


@pytest.mark.parametrize("case", ESCAPE_CASES, ids=lambda case: case.case_id)
def test_escape_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper == "escape"

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = re.escape(*case.args, **case.kwargs)

    assert type(observed) is type(expected)
    assert observed == expected
