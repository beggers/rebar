from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import FixtureCase, FixtureManifest, load_fixture_manifest
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    assert_match_convenience_api_parity,
    assert_match_parity,
    case_pattern,
    compile_with_cpython_parity,
    select_published_fixture_paths,
)


EXPECTED_PUBLISHED_FIXTURE_NAMES = (
    "nested_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
    "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    sorted(
        (FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES),
        key=lambda path: path.name,
    )
)
PUBLISHED_FIXTURE_PATHS = select_published_fixture_paths(EXPECTED_PUBLISHED_FIXTURE_PATHS)
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 2,
        ("module_call", "subn"): 2,
        ("pattern_call", "sub"): 2,
        ("pattern_call", "subn"): 2,
    }
)


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_case_ids: frozenset[str]
    expected_patterns: frozenset[str]


def _fixture_bundle(
    fixture_name: str,
    *,
    expected_manifest_id: str,
    expected_case_ids: frozenset[str],
    expected_patterns: frozenset[str],
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    return FixtureBundle(
        manifest=manifest,
        cases=tuple(cases),
        expected_manifest_id=expected_manifest_id,
        expected_case_ids=expected_case_ids,
        expected_patterns=expected_patterns,
    )


FIXTURE_BUNDLES = (
    _fixture_bundle(
        "nested_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
        expected_manifest_id=(
            "nested-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows"
        ),
        expected_case_ids=frozenset(
            {
                "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                "module-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
                "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
                "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
                "module-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
                "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c){1,})\2d",
                r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
            }
        ),
    ),
    _fixture_bundle(
        "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
        expected_manifest_id=(
            "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows"
        ),
        expected_case_ids=frozenset(
            {
                "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-mixed-branches-str",
                "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-c-branch-first-match-only-str",
                "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-mixed-branches-str",
                "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-first-match-only-b-branch-str",
                "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c){2,})\2d",
                r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
            }
        ),
    ),
)
PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
COMPILE_PATTERNS = tuple(sorted({case_pattern(case) for case in PUBLISHED_CASES}))
MODULE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "module_call")
PATTERN_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "pattern_call")


def _case_template_and_string(case: FixtureCase) -> tuple[str, str]:
    if case.operation == "module_call":
        template = case.args[1]
        string = case.args[2]
    else:
        template = case.args[0]
        string = case.args[1]

    assert isinstance(template, str)
    assert isinstance(string, str)
    return template, string


def _search_match_for_case(
    backend_name: str,
    backend: object,
    case: FixtureCase,
) -> tuple[object, re.Match[str]]:
    pattern = case_pattern(case)
    assert isinstance(pattern, str)
    _, string = _case_template_and_string(case)

    if case.operation == "module_call":
        observed = backend.search(pattern, string, case.flags or 0)
        expected = re.search(pattern, string, case.flags or 0)
    else:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
            case.flags or 0,
        )
        observed = observed_pattern.search(string)
        expected = expected_pattern.search(string)

    assert expected is not None
    assert observed is not None
    return observed, expected


def test_replacement_template_parity_suite_uses_expected_published_fixture_paths() -> None:
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
    assert {case_pattern(case) for case in bundle.cases} == bundle.expected_patterns
    assert {case.text_model for case in bundle.cases} == {"str"}
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
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


@pytest.mark.parametrize("case", PUBLISHED_CASES, ids=lambda case: case.case_id)
def test_replacement_match_capture_and_expand_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    template, _ = _case_template_and_string(case)
    observed_match, expected_match = _search_match_for_case(
        backend_name,
        backend,
        case,
    )

    assert_match_parity(
        backend_name,
        observed_match,
        expected_match,
        check_regs=True,
    )
    assert_match_convenience_api_parity(observed_match, expected_match)

    observed = observed_match.expand(template)
    expected = expected_match.expand(template)

    assert type(observed) is type(expected)
    assert observed == expected
