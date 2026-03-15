from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import FixtureCase, FixtureManifest, load_fixture_manifest
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    compile_with_cpython_parity,
    select_published_fixture_paths,
    str_case_pattern,
)


EXPECTED_PUBLISHED_FIXTURE_PATHS = (
    FIXTURES_DIR / "nested_group_replacement_workflows.py",
    FIXTURES_DIR / "quantified_nested_group_replacement_workflows.py",
)
PUBLISHED_FIXTURE_PATHS = select_published_fixture_paths(EXPECTED_PUBLISHED_FIXTURE_PATHS)


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_case_ids: frozenset[str]
    expected_compile_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]


def _fixture_bundle(
    fixture_name: str,
    *,
    expected_manifest_id: str,
    expected_case_ids: frozenset[str],
    expected_compile_patterns: frozenset[str],
    expected_operation_helper_counts: Counter[tuple[str, str | None]],
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    return FixtureBundle(
        manifest=manifest,
        cases=tuple(cases),
        expected_manifest_id=expected_manifest_id,
        expected_case_ids=expected_case_ids,
        expected_compile_patterns=expected_compile_patterns,
        expected_operation_helper_counts=expected_operation_helper_counts,
    )


FIXTURE_BUNDLES = (
    _fixture_bundle(
        "nested_group_replacement_workflows.py",
        expected_manifest_id="nested-group-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-template-nested-group-numbered-str",
                "module-subn-template-nested-group-numbered-str",
                "pattern-sub-template-nested-group-numbered-str",
                "pattern-subn-template-nested-group-numbered-str",
                "module-sub-template-nested-group-named-str",
                "module-subn-template-nested-group-named-str",
                "pattern-sub-template-nested-group-named-str",
                "pattern-subn-template-nested-group-named-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b))d",
                r"a(?P<outer>(?P<inner>b))d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "sub"): 2,
                ("module_call", "subn"): 2,
                ("pattern_call", "sub"): 2,
                ("pattern_call", "subn"): 2,
            }
        ),
    ),
    _fixture_bundle(
        "quantified_nested_group_replacement_workflows.py",
        expected_manifest_id="quantified-nested-group-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-template-quantified-nested-group-numbered-lower-bound-str",
                "module-subn-template-quantified-nested-group-numbered-first-match-only-str",
                "pattern-sub-template-quantified-nested-group-numbered-repeated-outer-capture-str",
                "pattern-subn-template-quantified-nested-group-numbered-first-match-only-str",
                "module-sub-template-quantified-nested-group-named-lower-bound-str",
                "module-subn-template-quantified-nested-group-named-first-match-only-str",
                "pattern-sub-template-quantified-nested-group-named-repeated-outer-capture-str",
                "pattern-subn-template-quantified-nested-group-named-first-match-only-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((bc)+)d",
                r"a(?P<outer>(?P<inner>bc)+)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "sub"): 2,
                ("module_call", "subn"): 2,
                ("pattern_call", "sub"): 2,
                ("pattern_call", "subn"): 2,
            }
        ),
    ),
)
PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
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
COMPILE_PATTERNS = tuple(sorted({str_case_pattern(case) for case in PUBLISHED_CASES}))
MODULE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "module_call")
PATTERN_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "pattern_call")


def test_nested_group_replacement_suite_uses_expected_published_fixture_paths() -> None:
    assert PUBLISHED_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS
    assert len({case.case_id for case in PUBLISHED_CASES}) == len(PUBLISHED_CASES)


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(
    bundle: FixtureBundle,
) -> None:
    assert bundle.manifest.manifest_id == bundle.expected_manifest_id
    assert len(bundle.cases) == len(bundle.expected_case_ids)
    assert {case.case_id for case in bundle.cases} == bundle.expected_case_ids
    assert {str_case_pattern(case) for case in bundle.cases} == bundle.expected_compile_patterns
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        bundle.expected_operation_helper_counts
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
