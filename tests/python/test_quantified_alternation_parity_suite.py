from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product
import re

import pytest

from rebar_harness.correctness import (
    FixtureCase,
    FixtureManifest,
    load_fixture_manifest,
)
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    assert_match_convenience_api_parity,
    assert_match_parity,
    case_pattern,
    compile_with_cpython_parity,
    select_published_fixture_paths,
)


EXPECTED_PUBLISHED_FIXTURE_NAMES = (
    "exact_repeat_quantified_group_alternation_workflows.py",
    "quantified_alternation_workflows.py",
    "quantified_alternation_backtracking_heavy_workflows.py",
    "quantified_alternation_broader_range_workflows.py",
    "quantified_alternation_conditional_workflows.py",
    "quantified_nested_group_alternation_workflows.py",
    "quantified_alternation_open_ended_workflows.py",
    "quantified_alternation_nested_branch_workflows.py",
)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    sorted(
        (FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES),
        key=lambda path: path.name,
    )
)
PUBLISHED_QUANTIFIED_ALTERNATION_FIXTURE_PATHS = select_published_fixture_paths(
    EXPECTED_PUBLISHED_FIXTURE_PATHS
)
BACKTRACKING_BRANCH_TEXT = {
    "short": "b",
    "long": "bc",
}
ZERO_REPETITION_NO_MATCH_TEXT = "ad"
OVERLAP_TAIL_NO_MATCH_TEXT = "abccd"


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_case_ids: frozenset[str]
    expected_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]


@dataclass(frozen=True)
class BacktrackingTraceCase:
    id: str
    pattern: str
    search_text: str
    fullmatch_text: str


@dataclass(frozen=True)
class SupplementalNoMatchCase:
    id: str
    target: str
    pattern: str
    text: str


def _fixture_bundle(
    fixture_name: str,
    *,
    expected_manifest_id: str,
    expected_case_ids: frozenset[str],
    expected_patterns: frozenset[str],
    expected_operation_helper_counts: Counter[tuple[str, str | None]],
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    return FixtureBundle(
        manifest=manifest,
        cases=tuple(cases),
        expected_manifest_id=expected_manifest_id,
        expected_case_ids=expected_case_ids,
        expected_patterns=expected_patterns,
        expected_operation_helper_counts=expected_operation_helper_counts,
    )


FIXTURE_BUNDLES = (
    _fixture_bundle(
        "exact_repeat_quantified_group_alternation_workflows.py",
        expected_manifest_id="exact-repeat-quantified-group-alternation-workflows",
        expected_case_ids=frozenset(
            {
                "exact-repeat-quantified-group-alternation-numbered-compile-metadata-str",
                "exact-repeat-quantified-group-alternation-numbered-module-search-bc-bc-str",
                "exact-repeat-quantified-group-alternation-numbered-module-search-bc-de-str",
                "exact-repeat-quantified-group-alternation-numbered-pattern-fullmatch-de-de-str",
                "exact-repeat-quantified-group-alternation-numbered-pattern-fullmatch-no-match-short-str",
                "exact-repeat-quantified-group-alternation-named-compile-metadata-str",
                "exact-repeat-quantified-group-alternation-named-module-search-bc-bc-str",
                "exact-repeat-quantified-group-alternation-named-module-search-bc-de-str",
                "exact-repeat-quantified-group-alternation-named-pattern-fullmatch-de-de-str",
                "exact-repeat-quantified-group-alternation-named-pattern-fullmatch-no-match-extra-repetition-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(bc|de){2}d",
                r"a(?P<word>bc|de){2}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 4,
            }
        ),
    ),
    _fixture_bundle(
        "quantified_alternation_workflows.py",
        expected_manifest_id="quantified-alternation-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-numbered-compile-metadata-str",
                "quantified-alternation-numbered-module-search-lower-bound-str",
                "quantified-alternation-numbered-pattern-fullmatch-second-repetition-str",
                "quantified-alternation-named-compile-metadata-str",
                "quantified-alternation-named-module-search-second-repetition-str",
                "quantified-alternation-named-pattern-fullmatch-lower-bound-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b|c){1,2}d",
                r"a(?P<word>b|c){1,2}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    _fixture_bundle(
        "quantified_nested_group_alternation_workflows.py",
        expected_manifest_id="quantified-nested-group-alternation-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-nested-group-alternation-numbered-compile-metadata-str",
                "quantified-nested-group-alternation-numbered-module-search-lower-bound-b-str",
                "quantified-nested-group-alternation-numbered-pattern-fullmatch-repeated-mixed-str",
                "quantified-nested-group-alternation-named-compile-metadata-str",
                "quantified-nested-group-alternation-named-module-search-lower-bound-c-str",
                "quantified-nested-group-alternation-named-pattern-fullmatch-repeated-mixed-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c)+)d",
                r"a(?P<outer>(?P<inner>b|c)+)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    _fixture_bundle(
        "quantified_alternation_backtracking_heavy_workflows.py",
        expected_manifest_id="quantified-alternation-backtracking-heavy-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-backtracking-heavy-numbered-compile-metadata-str",
                "quantified-alternation-backtracking-heavy-numbered-module-search-lower-bound-b-branch-str",
                "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-lower-bound-bc-branch-str",
                "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-b-then-bc-str",
                "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-bc-then-b-str",
                "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-bc-then-bc-str",
                "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-str",
                "quantified-alternation-backtracking-heavy-named-compile-metadata-str",
                "quantified-alternation-backtracking-heavy-named-module-search-lower-bound-bc-branch-str",
                "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-b-then-b-str",
                "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-bc-then-b-str",
                "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b|bc){1,2}d",
                r"a(?P<word>b|bc){1,2}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 8,
            }
        ),
    ),
    _fixture_bundle(
        "quantified_alternation_broader_range_workflows.py",
        expected_manifest_id="quantified-alternation-broader-range-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-broader-range-numbered-compile-metadata-str",
                "quantified-alternation-broader-range-numbered-module-search-lower-bound-b-str",
                "quantified-alternation-broader-range-numbered-module-search-lower-bound-c-str",
                "quantified-alternation-broader-range-numbered-pattern-fullmatch-third-repetition-bbb-str",
                "quantified-alternation-broader-range-numbered-pattern-fullmatch-third-repetition-bcc-str",
                "quantified-alternation-broader-range-numbered-pattern-fullmatch-third-repetition-bcb-str",
                "quantified-alternation-broader-range-numbered-pattern-fullmatch-no-match-below-lower-bound-str",
                "quantified-alternation-broader-range-numbered-pattern-fullmatch-no-match-overflow-str",
                "quantified-alternation-broader-range-named-compile-metadata-str",
                "quantified-alternation-broader-range-named-module-search-lower-bound-b-str",
                "quantified-alternation-broader-range-named-module-search-lower-bound-c-str",
                "quantified-alternation-broader-range-named-pattern-fullmatch-third-repetition-bbb-str",
                "quantified-alternation-broader-range-named-pattern-fullmatch-third-repetition-bcc-str",
                "quantified-alternation-broader-range-named-pattern-fullmatch-third-repetition-bcb-str",
                "quantified-alternation-broader-range-named-pattern-fullmatch-no-match-below-lower-bound-str",
                "quantified-alternation-broader-range-named-pattern-fullmatch-no-match-overflow-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b|c){1,3}d",
                r"a(?P<word>b|c){1,3}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
    ),
    _fixture_bundle(
        "quantified_alternation_conditional_workflows.py",
        expected_manifest_id="quantified-alternation-conditional-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-conditional-numbered-compile-metadata-str",
                "quantified-alternation-conditional-numbered-module-search-absent-workflow-str",
                "quantified-alternation-conditional-numbered-module-search-lower-bound-b-workflow-str",
                "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-b-workflow-str",
                "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-mixed-workflow-str",
                "quantified-alternation-conditional-numbered-pattern-fullmatch-no-match-workflow-str",
                "quantified-alternation-conditional-named-compile-metadata-str",
                "quantified-alternation-conditional-named-module-search-absent-workflow-str",
                "quantified-alternation-conditional-named-module-search-lower-bound-c-workflow-str",
                "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-c-workflow-str",
                "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-mixed-workflow-str",
                "quantified-alternation-conditional-named-pattern-fullmatch-no-match-workflow-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c){1,2})?(?(1)d|e)",
                r"a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
    ),
    _fixture_bundle(
        "quantified_alternation_open_ended_workflows.py",
        expected_manifest_id="quantified-alternation-open-ended-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-open-ended-numbered-compile-metadata-str",
                "quantified-alternation-open-ended-numbered-module-search-lower-bound-b-str",
                "quantified-alternation-open-ended-numbered-module-search-lower-bound-c-str",
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-second-repetition-str",
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-third-repetition-bcc-str",
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-fourth-repetition-bcbc-str",
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-below-lower-bound-str",
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-invalid-branch-str",
                "quantified-alternation-open-ended-named-compile-metadata-str",
                "quantified-alternation-open-ended-named-module-search-lower-bound-b-str",
                "quantified-alternation-open-ended-named-module-search-lower-bound-c-str",
                "quantified-alternation-open-ended-named-pattern-fullmatch-second-repetition-str",
                "quantified-alternation-open-ended-named-pattern-fullmatch-third-repetition-bcc-str",
                "quantified-alternation-open-ended-named-pattern-fullmatch-fourth-repetition-bcbc-str",
                "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-below-lower-bound-str",
                "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-invalid-branch-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b|c){1,}d",
                r"a(?P<word>b|c){1,}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 10,
            }
        ),
    ),
    _fixture_bundle(
        "quantified_alternation_nested_branch_workflows.py",
        expected_manifest_id="quantified-alternation-nested-branch-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-nested-branch-numbered-compile-metadata-str",
                "quantified-alternation-nested-branch-numbered-module-search-lower-bound-inner-branch-str",
                "quantified-alternation-nested-branch-numbered-pattern-fullmatch-lower-bound-literal-branch-str",
                "quantified-alternation-nested-branch-numbered-pattern-fullmatch-second-repetition-mixed-branches-str",
                "quantified-alternation-nested-branch-numbered-pattern-fullmatch-no-match-str",
                "quantified-alternation-nested-branch-named-compile-metadata-str",
                "quantified-alternation-nested-branch-named-module-search-lower-bound-literal-branch-str",
                "quantified-alternation-nested-branch-named-pattern-fullmatch-lower-bound-inner-branch-str",
                "quantified-alternation-nested-branch-named-pattern-fullmatch-second-repetition-mixed-branches-str",
                "quantified-alternation-nested-branch-named-pattern-fullmatch-no-match-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a((b|c)|de){1,2}d",
                r"a(?P<word>(b|c)|de){1,2}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
    ),
)
PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
COMPILE_CASES = tuple(
    case
    for case in PUBLISHED_CASES
    if case.operation == "compile"
)
MODULE_CASES = tuple(
    case
    for case in PUBLISHED_CASES
    if case.operation == "module_call"
)
PATTERN_CASES = tuple(
    case
    for case in PUBLISHED_CASES
    if case.operation == "pattern_call"
)
COMPILE_CASES_BY_ID = {case.case_id: case for case in COMPILE_CASES}
REGS_PARITY_CASE_IDS = frozenset(
    {
        "quantified-nested-group-alternation-numbered-module-search-lower-bound-b-str",
        "quantified-nested-group-alternation-numbered-pattern-fullmatch-repeated-mixed-str",
        "quantified-nested-group-alternation-named-module-search-lower-bound-c-str",
        "quantified-nested-group-alternation-named-pattern-fullmatch-repeated-mixed-str",
    }
)
BACKTRACKING_HEAVY_BUNDLE = next(
    bundle
    for bundle in FIXTURE_BUNDLES
    if bundle.expected_manifest_id == "quantified-alternation-backtracking-heavy-workflows"
)
BACKTRACKING_HEAVY_COMPILE_CASES = tuple(
    case for case in BACKTRACKING_HEAVY_BUNDLE.cases if case.operation == "compile"
)


def _compile_case_prefix(case: FixtureCase) -> str:
    suffix = "-compile-metadata-str"
    assert case.case_id.endswith(suffix)
    return case.case_id.removesuffix(suffix)


def _build_backtracking_trace_cases() -> tuple[BacktrackingTraceCase, ...]:
    cases: list[BacktrackingTraceCase] = []
    for case in BACKTRACKING_HEAVY_COMPILE_CASES:
        pattern = case_pattern(case)
        assert isinstance(pattern, str)
        prefix = _compile_case_prefix(case)
        for repetition_count in range(1, 3):
            for branch_order in product(("short", "long"), repeat=repetition_count):
                body = "".join(BACKTRACKING_BRANCH_TEXT[branch] for branch in branch_order)
                branch_id = "-".join(branch_order)
                fullmatch_text = f"a{body}d"
                cases.append(
                    BacktrackingTraceCase(
                        id=f"{prefix}-{branch_id}",
                        pattern=pattern,
                        search_text=f"zz{fullmatch_text}zz",
                        fullmatch_text=fullmatch_text,
                    )
                )
    return tuple(cases)


def _compile_pattern(case_id: str) -> str:
    pattern = case_pattern(COMPILE_CASES_BY_ID[case_id])
    assert isinstance(pattern, str)
    return pattern


def _build_supplemental_no_match_cases() -> tuple[SupplementalNoMatchCase, ...]:
    cases: list[SupplementalNoMatchCase] = []
    for case in BACKTRACKING_HEAVY_COMPILE_CASES:
        pattern = case_pattern(case)
        assert isinstance(pattern, str)
        prefix = _compile_case_prefix(case)
        cases.extend(
            [
                SupplementalNoMatchCase(
                    id=f"{prefix}-module-search-miss-zero-repetition",
                    target="module",
                    pattern=pattern,
                    text=f"zz{ZERO_REPETITION_NO_MATCH_TEXT}zz",
                ),
                SupplementalNoMatchCase(
                    id=f"{prefix}-module-search-miss-overlap-tail",
                    target="module",
                    pattern=pattern,
                    text=f"zz{OVERLAP_TAIL_NO_MATCH_TEXT}zz",
                ),
                SupplementalNoMatchCase(
                    id=f"{prefix}-pattern-fullmatch-miss-zero-repetition",
                    target="pattern",
                    pattern=pattern,
                    text=ZERO_REPETITION_NO_MATCH_TEXT,
                ),
            ]
        )

    numbered_pattern = _compile_pattern(
        "quantified-nested-group-alternation-numbered-compile-metadata-str"
    )
    named_pattern = _compile_pattern(
        "quantified-nested-group-alternation-named-compile-metadata-str"
    )
    cases.extend(
        [
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-numbered-module-search-miss-too-short",
                target="module",
                pattern=numbered_pattern,
                text="zzadzz",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-numbered-module-search-miss-invalid-branch",
                target="module",
                pattern=numbered_pattern,
                text="zzabedzz",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-numbered-pattern-fullmatch-miss-too-short",
                target="pattern",
                pattern=numbered_pattern,
                text="ad",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-numbered-pattern-fullmatch-miss-invalid-branch",
                target="pattern",
                pattern=numbered_pattern,
                text="abed",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-named-module-search-miss-too-short",
                target="module",
                pattern=named_pattern,
                text="zzadzz",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-named-module-search-miss-invalid-branch",
                target="module",
                pattern=named_pattern,
                text="zzabedzz",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-named-pattern-fullmatch-miss-too-short",
                target="pattern",
                pattern=named_pattern,
                text="ad",
            ),
            SupplementalNoMatchCase(
                id="quantified-nested-group-alternation-named-pattern-fullmatch-miss-invalid-branch",
                target="pattern",
                pattern=named_pattern,
                text="abed",
            ),
        ]
    )
    return tuple(cases)


BACKTRACKING_TRACE_CASES = _build_backtracking_trace_cases()
SUPPLEMENTAL_NO_MATCH_CASES = _build_supplemental_no_match_cases()


def test_quantified_alternation_suite_uses_expected_published_fixtures() -> None:
    assert PUBLISHED_QUANTIFIED_ALTERNATION_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS
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
        bundle.expected_operation_helper_counts
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(backend_name, backend, case_pattern(case), case.flags or 0)


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_search_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "search"

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=case.case_id in REGS_PARITY_CASE_IDS,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_search_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper == "search"

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "fullmatch"

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=case.case_id in REGS_PARITY_CASE_IDS,
    )


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "fullmatch"

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", BACKTRACKING_TRACE_CASES, ids=lambda case: case.id)
def test_backtracking_heavy_module_search_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: BacktrackingTraceCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.search(case.pattern, case.search_text)
    expected = re.search(case.pattern, case.search_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", BACKTRACKING_TRACE_CASES, ids=lambda case: case.id)
def test_backtracking_heavy_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: BacktrackingTraceCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    observed = observed_pattern.fullmatch(case.fullmatch_text)
    expected = expected_pattern.fullmatch(case.fullmatch_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", SUPPLEMENTAL_NO_MATCH_CASES, ids=lambda case: case.id)
def test_supplemental_no_match_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalNoMatchCase,
) -> None:
    backend_name, backend = regex_backend

    if case.target == "module":
        observed = backend.search(case.pattern, case.text)
        expected = re.search(case.pattern, case.text)
    else:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            case.pattern,
        )
        observed = observed_pattern.fullmatch(case.text)
        expected = expected_pattern.fullmatch(case.text)

    assert observed is None
    assert expected is None
