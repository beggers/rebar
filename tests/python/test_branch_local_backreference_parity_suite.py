from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import pathlib
import re

import pytest

import rebar
from rebar_harness.correctness import (
    DEFAULT_FIXTURE_PATHS,
    FixtureCase,
    FixtureManifest,
    load_fixture_manifest,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "conformance" / "fixtures"
MISSING_GROUP_DEFAULT = object()
EXPECTED_PUBLISHED_FIXTURE_NAMES = (
    "branch_local_backreference_workflows.py",
    "quantified_branch_local_backreference_workflows.py",
    "optional_group_alternation_branch_local_backreference_workflows.py",
    "conditional_group_exists_branch_local_backreference_workflows.py",
    "nested_group_alternation_branch_local_backreference_workflows.py",
    "quantified_alternation_branch_local_backreference_workflows.py",
    "quantified_nested_group_alternation_branch_local_backreference_workflows.py",
    "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py",
)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    sorted(
        (FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES),
        key=lambda path: path.name,
    )
)
PUBLISHED_BRANCH_LOCAL_BACKREFERENCE_FIXTURE_PATHS = tuple(
    sorted(
        (path for path in DEFAULT_FIXTURE_PATHS if path in EXPECTED_PUBLISHED_FIXTURE_PATHS),
        key=lambda path: path.name,
    )
)


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_case_ids: frozenset[str]
    expected_compile_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]
    assert_match_convenience_api: bool = False


@dataclass(frozen=True)
class SupplementalMissCase:
    id: str
    target: str
    pattern: str
    helper: str
    text: str


def _fixture_bundle(
    fixture_name: str,
    *,
    expected_manifest_id: str,
    expected_case_ids: frozenset[str],
    expected_compile_patterns: frozenset[str],
    expected_operation_helper_counts: Counter[tuple[str, str | None]],
    assert_match_convenience_api: bool = False,
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    return FixtureBundle(
        manifest=manifest,
        cases=tuple(cases),
        expected_manifest_id=expected_manifest_id,
        expected_case_ids=expected_case_ids,
        expected_compile_patterns=expected_compile_patterns,
        expected_operation_helper_counts=expected_operation_helper_counts,
        assert_match_convenience_api=assert_match_convenience_api,
    )


FIXTURE_BUNDLES = (
    _fixture_bundle(
        "branch_local_backreference_workflows.py",
        expected_manifest_id="branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "branch-local-numbered-backreference-compile-metadata-str",
                "branch-local-numbered-backreference-module-search-str",
                "branch-local-numbered-backreference-pattern-fullmatch-str",
                "branch-local-named-backreference-compile-metadata-str",
                "branch-local-named-backreference-module-search-str",
                "branch-local-named-backreference-pattern-fullmatch-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b)|c)\2d",
                r"a(?P<outer>(?P<inner>b)|c)(?P=inner)d",
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
        "quantified_branch_local_backreference_workflows.py",
        expected_manifest_id="quantified-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-branch-local-numbered-backreference-compile-metadata-str",
                "quantified-branch-local-numbered-backreference-module-search-lower-bound-str",
                "quantified-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-str",
                "quantified-branch-local-numbered-backreference-pattern-fullmatch-absent-branch-str",
                "quantified-branch-local-named-backreference-compile-metadata-str",
                "quantified-branch-local-named-backreference-module-search-lower-bound-str",
                "quantified-branch-local-named-backreference-pattern-fullmatch-second-iteration-str",
                "quantified-branch-local-named-backreference-pattern-fullmatch-absent-branch-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b)+|c)\2d",
                r"a(?P<outer>(?P<inner>b)+|c)(?P=inner)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 4,
            }
        ),
        assert_match_convenience_api=True,
    ),
    _fixture_bundle(
        "optional_group_alternation_branch_local_backreference_workflows.py",
        expected_manifest_id="optional-group-alternation-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "optional-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
                "optional-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str",
                "optional-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str",
                "optional-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-absent-group-str",
                "optional-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
                "optional-group-alternation-branch-local-named-backreference-compile-metadata-str",
                "optional-group-alternation-branch-local-named-backreference-module-search-c-branch-str",
                "optional-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str",
                "optional-group-alternation-branch-local-named-backreference-pattern-fullmatch-absent-group-str",
                "optional-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c)\2)?d",
                r"a(?P<outer>(?P<inner>b|c)(?P=inner))?d",
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
    _fixture_bundle(
        "conditional_group_exists_branch_local_backreference_workflows.py",
        expected_manifest_id="conditional-group-exists-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-branch-local-numbered-backreference-compile-metadata-str",
                "conditional-group-exists-branch-local-numbered-backreference-module-search-present-str",
                "conditional-group-exists-branch-local-numbered-backreference-pattern-fullmatch-absent-str",
                "conditional-group-exists-branch-local-named-backreference-compile-metadata-str",
                "conditional-group-exists-branch-local-named-backreference-module-search-present-str",
                "conditional-group-exists-branch-local-named-backreference-pattern-fullmatch-absent-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b)|c)\2(?(2)d|e)",
                r"a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)",
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
        "nested_group_alternation_branch_local_backreference_workflows.py",
        expected_manifest_id="nested-group-alternation-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "nested-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
                "nested-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str",
                "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str",
                "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
                "nested-group-alternation-branch-local-named-backreference-compile-metadata-str",
                "nested-group-alternation-branch-local-named-backreference-module-search-c-branch-str",
                "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str",
                "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c))\2d",
                r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 4,
            }
        ),
        assert_match_convenience_api=True,
    ),
    _fixture_bundle(
        "quantified_alternation_branch_local_backreference_workflows.py",
        expected_manifest_id="quantified-alternation-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
                "quantified-alternation-branch-local-numbered-backreference-compile-metadata-str",
                "quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
                "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str",
                "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-str",
                "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
                "quantified-alternation-branch-local-named-backreference-compile-metadata-str",
                "quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
                "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-c-branch-str",
                "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-str",
                "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c)\2){1,2}d",
                r"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        assert_match_convenience_api=True,
    ),
    _fixture_bundle(
        "quantified_nested_group_alternation_branch_local_backreference_workflows.py",
        expected_manifest_id="quantified-nested-group-alternation-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
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
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c)+)\2d",
                r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
        assert_match_convenience_api=True,
    ),
    _fixture_bundle(
        "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py",
        expected_manifest_id="nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows",
        expected_case_ids=frozenset(
            {
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
        ),
        expected_compile_patterns=frozenset(
            {
                r"a((b|c){1,4})\2d",
                r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 8,
            }
        ),
        assert_match_convenience_api=True,
    ),
)
PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
COMPILE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "compile")
WORKFLOW_CASES = tuple(case for case in PUBLISHED_CASES if case.operation != "compile")
MATCH_CONVENIENCE_CASE_IDS = frozenset(
    case.case_id
    for bundle in FIXTURE_BUNDLES
    if bundle.assert_match_convenience_api
    for case in bundle.cases
    if case.operation != "compile"
)
SUPPLEMENTAL_MISS_CASES = (
    SupplementalMissCase(
        id="module-numbered-search-miss-mismatched-replay",
        target="module",
        pattern=r"a((b)+|c)\2d",
        helper="search",
        text="zzabcdzz",
    ),
    SupplementalMissCase(
        id="pattern-numbered-fullmatch-miss-mismatched-replay",
        target="pattern",
        pattern=r"a((b)+|c)\2d",
        helper="fullmatch",
        text="abcd",
    ),
    SupplementalMissCase(
        id="module-named-search-miss-mismatched-replay",
        target="module",
        pattern=r"a(?P<outer>(?P<inner>b)+|c)(?P=inner)d",
        helper="search",
        text="zzabcdzz",
    ),
    SupplementalMissCase(
        id="pattern-named-fullmatch-miss-mismatched-replay",
        target="pattern",
        pattern=r"a(?P<outer>(?P<inner>b)+|c)(?P=inner)d",
        helper="fullmatch",
        text="abcd",
    ),
    SupplementalMissCase(
        id="module-numbered-search-miss-mismatched-replay-nested",
        target="module",
        pattern=r"a((b|c))\2d",
        helper="search",
        text="zzabcdzz",
    ),
    SupplementalMissCase(
        id="pattern-numbered-fullmatch-miss-mismatched-replay-nested",
        target="pattern",
        pattern=r"a((b|c))\2d",
        helper="fullmatch",
        text="acbd",
    ),
    SupplementalMissCase(
        id="module-named-search-miss-mismatched-replay-nested",
        target="module",
        pattern=r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        helper="search",
        text="zzacbdzz",
    ),
    SupplementalMissCase(
        id="pattern-named-fullmatch-miss-mismatched-replay-nested",
        target="pattern",
        pattern=r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        helper="fullmatch",
        text="abcd",
    ),
    SupplementalMissCase(
        id="module-numbered-search-miss-mixed-branch-repetition",
        target="module",
        pattern=r"a((b|c)\2){1,2}d",
        helper="search",
        text="zzabccdzz",
    ),
    SupplementalMissCase(
        id="pattern-numbered-fullmatch-miss-mixed-branch-repetition",
        target="pattern",
        pattern=r"a((b|c)\2){1,2}d",
        helper="fullmatch",
        text="abccd",
    ),
    SupplementalMissCase(
        id="module-named-search-miss-cross-branch-replay",
        target="module",
        pattern=r"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
        helper="search",
        text="zzacbbdzz",
    ),
    SupplementalMissCase(
        id="pattern-named-fullmatch-miss-cross-branch-replay",
        target="pattern",
        pattern=r"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
        helper="fullmatch",
        text="acbbd",
    ),
    SupplementalMissCase(
        id="module-numbered-search-miss-mismatched-replay-quantified-nested",
        target="module",
        pattern=r"a((b|c)+)\2d",
        helper="search",
        text="zzabcdzz",
    ),
    SupplementalMissCase(
        id="pattern-numbered-fullmatch-miss-short-replay",
        target="pattern",
        pattern=r"a((b|c)+)\2d",
        helper="fullmatch",
        text="acbd",
    ),
    SupplementalMissCase(
        id="module-named-search-miss-short-replay",
        target="module",
        pattern=r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        helper="search",
        text="zzacbdzz",
    ),
    SupplementalMissCase(
        id="pattern-named-fullmatch-miss-mismatched-replay-quantified-nested",
        target="pattern",
        pattern=r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        helper="fullmatch",
        text="abcd",
    ),
    SupplementalMissCase(
        id="module-broader-range-numbered-search-miss-missing-replay",
        target="module",
        pattern=r"a((b|c){1,4})\2d",
        helper="search",
        text="zzabcbcdzz",
    ),
    SupplementalMissCase(
        id="pattern-broader-range-numbered-fullmatch-miss-overflow",
        target="pattern",
        pattern=r"a((b|c){1,4})\2d",
        helper="fullmatch",
        text="abbbbbbd",
    ),
    SupplementalMissCase(
        id="module-broader-range-named-search-miss-missing-replay",
        target="module",
        pattern=r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        helper="search",
        text="zzabcbcdzz",
    ),
    SupplementalMissCase(
        id="pattern-broader-range-named-fullmatch-miss-overflow",
        target="pattern",
        pattern=r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        helper="fullmatch",
        text="accccccd",
    ),
)


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


def _assert_match_convenience_api_parity(
    observed: object,
    expected: re.Match[str],
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


def _compile_with_cpython_parity(
    backend_name: str,
    backend: object,
    pattern: str,
    flags: int = 0,
) -> tuple[object, re.Pattern[str]]:
    observed = backend.compile(pattern, flags)
    expected = re.compile(pattern, flags)

    assert observed is backend.compile(pattern, flags)
    _assert_pattern_parity(backend_name, observed, expected)
    return observed, expected


def test_expected_branch_local_backreference_fixtures_remain_published() -> None:
    assert PUBLISHED_BRANCH_LOCAL_BACKREFERENCE_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS


@pytest.mark.parametrize("bundle", FIXTURE_BUNDLES, ids=lambda bundle: bundle.expected_manifest_id)
def test_parity_suite_stays_aligned_with_published_correctness_fixture(
    bundle: FixtureBundle,
) -> None:
    assert bundle.manifest.path in PUBLISHED_BRANCH_LOCAL_BACKREFERENCE_FIXTURE_PATHS
    assert bundle.manifest.manifest_id == bundle.expected_manifest_id
    assert len(bundle.cases) == len(bundle.expected_case_ids)
    assert {case.case_id for case in bundle.cases} == bundle.expected_case_ids
    assert {_case_pattern(case) for case in bundle.cases} == bundle.expected_compile_patterns
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        bundle.expected_operation_helper_counts
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    _compile_with_cpython_parity(
        backend_name,
        backend,
        _case_pattern(case),
        case.flags or 0,
    )


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
        observed_pattern, expected_pattern = _compile_with_cpython_parity(
            backend_name,
            backend,
            case.pattern_payload(),
            case.flags or 0,
        )
        observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
        expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    _assert_match_parity(backend_name, observed, expected)
    if case.case_id in MATCH_CONVENIENCE_CASE_IDS:
        _assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("miss_case", SUPPLEMENTAL_MISS_CASES, ids=lambda case: case.id)
def test_supplemental_negative_paths_match_cpython(
    regex_backend: tuple[str, object],
    miss_case: SupplementalMissCase,
) -> None:
    backend_name, backend = regex_backend

    if miss_case.target == "module":
        observed = getattr(backend, miss_case.helper)(miss_case.pattern, miss_case.text)
        expected = getattr(re, miss_case.helper)(miss_case.pattern, miss_case.text)
    else:
        observed_pattern, expected_pattern = _compile_with_cpython_parity(
            backend_name,
            backend,
            miss_case.pattern,
        )
        observed = getattr(observed_pattern, miss_case.helper)(miss_case.text)
        expected = getattr(expected_pattern, miss_case.helper)(miss_case.text)

    assert observed is None
    assert expected is None
