from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import pathlib
import re

import pytest

from rebar_harness.correctness import FixtureCase, FixtureManifest, load_fixture_manifest
from tests.python.fixture_parity_support import (
    assert_match_parity,
    assert_match_result_parity,
    compile_with_cpython_parity,
    str_case_pattern,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "conformance" / "fixtures"
QUANTIFIED_ALTERNATION_NUMBERED_PATTERN = r"a(b)?c(?(1)(de|df)|(eg|eh)){2}"
QUANTIFIED_ALTERNATION_NAMED_PATTERN = (
    r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}"
)


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_case_ids: frozenset[str]
    expected_compile_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]


@dataclass(frozen=True)
class SupplementalModuleFullmatchCase:
    id: str
    pattern: str
    text: str


@dataclass(frozen=True)
class SupplementalPatternFullmatchCase:
    id: str
    pattern: str
    text: str


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
        "conditional_group_exists_quantified_workflows.py",
        expected_manifest_id="conditional-group-exists-quantified-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-quantified-compile-metadata-str",
                "conditional-group-exists-quantified-module-search-present-str",
                "conditional-group-exists-quantified-module-fullmatch-absent-str",
                "conditional-group-exists-quantified-pattern-fullmatch-missing-repeat-str",
                "named-conditional-group-exists-quantified-compile-metadata-str",
                "named-conditional-group-exists-quantified-module-search-present-str",
                "named-conditional-group-exists-quantified-module-fullmatch-absent-str",
                "named-conditional-group-exists-quantified-pattern-fullmatch-missing-repeat-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|e){2}",
                r"a(?P<word>b)?c(?(word)d|e){2}",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("module_call", "fullmatch"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    _fixture_bundle(
        "conditional_group_exists_quantified_alternation_workflows.py",
        expected_manifest_id="conditional-group-exists-quantified-alternation-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-quantified-alternation-compile-metadata-str",
                "conditional-group-exists-quantified-alternation-module-search-present-first-arm-str",
                "conditional-group-exists-quantified-alternation-pattern-fullmatch-present-second-arm-str",
                "conditional-group-exists-quantified-alternation-module-search-absent-first-arm-str",
                "conditional-group-exists-quantified-alternation-pattern-fullmatch-absent-second-arm-str",
                "named-conditional-group-exists-quantified-alternation-compile-metadata-str",
                "named-conditional-group-exists-quantified-alternation-module-search-present-first-arm-str",
                "named-conditional-group-exists-quantified-alternation-pattern-fullmatch-present-second-arm-str",
                "named-conditional-group-exists-quantified-alternation-module-search-absent-first-arm-str",
                "named-conditional-group-exists-quantified-alternation-pattern-fullmatch-absent-second-arm-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                QUANTIFIED_ALTERNATION_NUMBERED_PATTERN,
                QUANTIFIED_ALTERNATION_NAMED_PATTERN,
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
        "conditional_group_exists_no_else_quantified_workflows.py",
        expected_manifest_id="conditional-group-exists-no-else-quantified-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-no-else-quantified-compile-metadata-str",
                "conditional-group-exists-no-else-quantified-module-search-present-str",
                "conditional-group-exists-no-else-quantified-module-fullmatch-absent-str",
                "conditional-group-exists-no-else-quantified-pattern-fullmatch-missing-repeat-str",
                "named-conditional-group-exists-no-else-quantified-compile-metadata-str",
                "named-conditional-group-exists-no-else-quantified-module-search-present-str",
                "named-conditional-group-exists-no-else-quantified-module-fullmatch-absent-str",
                "named-conditional-group-exists-no-else-quantified-pattern-fullmatch-missing-repeat-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)d){2}",
                r"a(?P<word>b)?c(?(word)d){2}",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("module_call", "fullmatch"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    _fixture_bundle(
        "conditional_group_exists_empty_else_quantified_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-else-quantified-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-empty-else-quantified-compile-metadata-str",
                "conditional-group-exists-empty-else-quantified-module-search-present-str",
                "conditional-group-exists-empty-else-quantified-module-fullmatch-absent-str",
                "conditional-group-exists-empty-else-quantified-pattern-fullmatch-missing-repeat-str",
                "named-conditional-group-exists-empty-else-quantified-compile-metadata-str",
                "named-conditional-group-exists-empty-else-quantified-module-search-present-str",
                "named-conditional-group-exists-empty-else-quantified-module-fullmatch-absent-str",
                "named-conditional-group-exists-empty-else-quantified-pattern-fullmatch-missing-repeat-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|){2}",
                r"a(?P<word>b)?c(?(word)d|){2}",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 2,
                ("module_call", "fullmatch"): 2,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    _fixture_bundle(
        "conditional_group_exists_empty_yes_else_quantified_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-yes-else-quantified-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-empty-yes-else-quantified-compile-metadata-str",
                "conditional-group-exists-empty-yes-else-quantified-module-fullmatch-present-str",
                "conditional-group-exists-empty-yes-else-quantified-module-fullmatch-absent-str",
                "conditional-group-exists-empty-yes-else-quantified-pattern-fullmatch-mixed-str",
                "named-conditional-group-exists-empty-yes-else-quantified-compile-metadata-str",
                "named-conditional-group-exists-empty-yes-else-quantified-module-fullmatch-present-str",
                "named-conditional-group-exists-empty-yes-else-quantified-module-fullmatch-absent-str",
                "named-conditional-group-exists-empty-yes-else-quantified-pattern-fullmatch-mixed-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"(?:a(b)?c(?(1)|e)){2}",
                r"(?:a(?P<word>b)?c(?(word)|e)){2}",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "fullmatch"): 4,
                ("pattern_call", "fullmatch"): 2,
            }
        ),
    ),
    _fixture_bundle(
        "conditional_group_exists_fully_empty_quantified_workflows.py",
        expected_manifest_id="conditional-group-exists-fully-empty-quantified-workflows",
        expected_case_ids=frozenset(
            {
                "conditional-group-exists-fully-empty-quantified-compile-metadata-str",
                "conditional-group-exists-fully-empty-quantified-module-fullmatch-present-str",
                "conditional-group-exists-fully-empty-quantified-module-fullmatch-absent-str",
                "conditional-group-exists-fully-empty-quantified-pattern-fullmatch-mixed-str",
                "conditional-group-exists-fully-empty-quantified-pattern-fullmatch-extra-suffix-failure-str",
                "named-conditional-group-exists-fully-empty-quantified-compile-metadata-str",
                "named-conditional-group-exists-fully-empty-quantified-module-fullmatch-present-str",
                "named-conditional-group-exists-fully-empty-quantified-module-fullmatch-absent-str",
                "named-conditional-group-exists-fully-empty-quantified-pattern-fullmatch-mixed-str",
                "named-conditional-group-exists-fully-empty-quantified-pattern-fullmatch-extra-suffix-failure-str",
            }
        ),
        expected_compile_patterns=frozenset(
            {
                r"(?:a(b)?c(?(1)|)){2}",
                r"(?:a(?P<word>b)?c(?(word)|)){2}",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "fullmatch"): 4,
                ("pattern_call", "fullmatch"): 4,
            }
        ),
    ),
)
PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
COMPILE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "compile")
MODULE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "module_call")
PATTERN_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "pattern_call")

# Preserve the extra module.fullmatch mixed-iteration checks that only lived in
# the superseded singleton files and were never promoted into scorecard fixtures.
SUPPLEMENTAL_MODULE_FULLMATCH_CASES = (
    SupplementalModuleFullmatchCase(
        id="conditional-group-exists-empty-yes-else-quantified-numbered-module-fullmatch-mixed-present-then-absent-failure",
        pattern=r"(?:a(b)?c(?(1)|e)){2}",
        text="abcace",
    ),
    SupplementalModuleFullmatchCase(
        id="conditional-group-exists-empty-yes-else-quantified-named-module-fullmatch-mixed-present-then-absent-failure",
        pattern=r"(?:a(?P<word>b)?c(?(word)|e)){2}",
        text="abcace",
    ),
    SupplementalModuleFullmatchCase(
        id="conditional-group-exists-fully-empty-quantified-numbered-module-fullmatch-mixed-present-then-absent",
        pattern=r"(?:a(b)?c(?(1)|)){2}",
        text="abcac",
    ),
    SupplementalModuleFullmatchCase(
        id="conditional-group-exists-fully-empty-quantified-named-module-fullmatch-mixed-present-then-absent",
        pattern=r"(?:a(?P<word>b)?c(?(word)|)){2}",
        text="abcac",
    ),
)
SUPPLEMENTAL_PATTERN_FULLMATCH_CASES = (
    SupplementalPatternFullmatchCase(
        id="conditional-group-exists-quantified-alternation-numbered-pattern-fullmatch-mixed-arms",
        pattern=QUANTIFIED_ALTERNATION_NUMBERED_PATTERN,
        text="abcdedf",
    ),
    SupplementalPatternFullmatchCase(
        id="conditional-group-exists-quantified-alternation-numbered-pattern-fullmatch-mixed-else-arms",
        pattern=QUANTIFIED_ALTERNATION_NUMBERED_PATTERN,
        text="acegeh",
    ),
    SupplementalPatternFullmatchCase(
        id="conditional-group-exists-quantified-alternation-named-pattern-fullmatch-mixed-arms",
        pattern=QUANTIFIED_ALTERNATION_NAMED_PATTERN,
        text="abcdedf",
    ),
    SupplementalPatternFullmatchCase(
        id="conditional-group-exists-quantified-alternation-named-pattern-fullmatch-mixed-else-arms",
        pattern=QUANTIFIED_ALTERNATION_NAMED_PATTERN,
        text="acegeh",
    ),
)
SUPPLEMENTAL_MISS_CASES = (
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-module-numbered-search-miss-partial-present-second-arm",
        target="module",
        pattern=QUANTIFIED_ALTERNATION_NUMBERED_PATTERN,
        helper="search",
        text="zzabcdehzz",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-module-numbered-search-miss-partial-absent-second-arm",
        target="module",
        pattern=QUANTIFIED_ALTERNATION_NUMBERED_PATTERN,
        helper="search",
        text="zzacegedzz",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-module-numbered-search-miss-too-short",
        target="module",
        pattern=QUANTIFIED_ALTERNATION_NUMBERED_PATTERN,
        helper="search",
        text="zzadzz",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-module-numbered-search-miss-wrong-arm",
        target="module",
        pattern=QUANTIFIED_ALTERNATION_NUMBERED_PATTERN,
        helper="search",
        text="zzabcegzz",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-pattern-numbered-fullmatch-miss-partial-present-second-arm",
        target="pattern",
        pattern=QUANTIFIED_ALTERNATION_NUMBERED_PATTERN,
        helper="fullmatch",
        text="abcdeh",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-pattern-numbered-fullmatch-miss-partial-absent-second-arm",
        target="pattern",
        pattern=QUANTIFIED_ALTERNATION_NUMBERED_PATTERN,
        helper="fullmatch",
        text="aceged",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-pattern-numbered-fullmatch-miss-too-short",
        target="pattern",
        pattern=QUANTIFIED_ALTERNATION_NUMBERED_PATTERN,
        helper="fullmatch",
        text="ad",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-pattern-numbered-fullmatch-miss-wrong-arm",
        target="pattern",
        pattern=QUANTIFIED_ALTERNATION_NUMBERED_PATTERN,
        helper="fullmatch",
        text="abceg",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-module-named-search-miss-partial-present-second-arm",
        target="module",
        pattern=QUANTIFIED_ALTERNATION_NAMED_PATTERN,
        helper="search",
        text="zzabcdehzz",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-module-named-search-miss-partial-absent-second-arm",
        target="module",
        pattern=QUANTIFIED_ALTERNATION_NAMED_PATTERN,
        helper="search",
        text="zzacegedzz",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-module-named-search-miss-too-short",
        target="module",
        pattern=QUANTIFIED_ALTERNATION_NAMED_PATTERN,
        helper="search",
        text="zzadzz",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-module-named-search-miss-wrong-arm",
        target="module",
        pattern=QUANTIFIED_ALTERNATION_NAMED_PATTERN,
        helper="search",
        text="zzabcegzz",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-pattern-named-fullmatch-miss-partial-present-second-arm",
        target="pattern",
        pattern=QUANTIFIED_ALTERNATION_NAMED_PATTERN,
        helper="fullmatch",
        text="abcdeh",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-pattern-named-fullmatch-miss-partial-absent-second-arm",
        target="pattern",
        pattern=QUANTIFIED_ALTERNATION_NAMED_PATTERN,
        helper="fullmatch",
        text="aceged",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-pattern-named-fullmatch-miss-too-short",
        target="pattern",
        pattern=QUANTIFIED_ALTERNATION_NAMED_PATTERN,
        helper="fullmatch",
        text="ad",
    ),
    SupplementalMissCase(
        id="conditional-group-exists-quantified-alternation-pattern-named-fullmatch-miss-wrong-arm",
        target="pattern",
        pattern=QUANTIFIED_ALTERNATION_NAMED_PATTERN,
        helper="fullmatch",
        text="abceg",
    ),
)


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


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(
        backend_name,
        backend,
        str_case_pattern(case),
        case.flags or 0,
    )


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert_match_result_parity(
        backend_name,
        observed,
        expected,
        check_regs=True,
    )


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
        str_case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert_match_result_parity(
        backend_name,
        observed,
        expected,
        check_regs=True,
    )


@pytest.mark.parametrize(
    "case",
    SUPPLEMENTAL_MODULE_FULLMATCH_CASES,
    ids=lambda case: case.id,
)
def test_supplemental_module_fullmatch_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalModuleFullmatchCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.fullmatch(case.pattern, case.text)
    expected = re.fullmatch(case.pattern, case.text)

    assert_match_result_parity(
        backend_name,
        observed,
        expected,
        check_regs=True,
    )


@pytest.mark.parametrize(
    "case",
    SUPPLEMENTAL_PATTERN_FULLMATCH_CASES,
    ids=lambda case: case.id,
)
def test_supplemental_pattern_fullmatch_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalPatternFullmatchCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    observed = observed_pattern.fullmatch(case.text)
    expected = expected_pattern.fullmatch(case.text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=True,
    )


@pytest.mark.parametrize("case", SUPPLEMENTAL_MISS_CASES, ids=lambda case: case.id)
def test_supplemental_negative_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalMissCase,
) -> None:
    backend_name, backend = regex_backend

    if case.target == "module":
        observed = getattr(backend, case.helper)(case.pattern, case.text)
        expected = getattr(re, case.helper)(case.pattern, case.text)
    else:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            case.pattern,
        )
        observed = getattr(observed_pattern, case.helper)(case.text)
        expected = getattr(expected_pattern, case.helper)(case.text)

    assert_match_result_parity(
        backend_name,
        observed,
        expected,
        check_regs=True,
    )
