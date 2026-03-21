from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import re

import pytest

from rebar_harness.correctness import (
    CONDITIONAL_GROUP_EXISTS_FIXTURE_SELECTOR,
    FixtureCase,
    select_correctness_fixture_paths,
)
from tests.python.fixture_parity_support import (
    FixtureBundle,
    assert_fixture_bundle_contract,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    invoke_bounded_pattern_case,
    load_published_fixture_bundles,
    published_fixture_bundle_by_manifest_id,
    record_generated_match_failure,
    str_case_pattern,
    workflow_result_with_cpython_parity,
)


@dataclass(frozen=True)
class BoundedPatternCase:
    id: str
    pattern_case_id: str
    helper: str
    string: str
    bounds: tuple[int, int]


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


@dataclass(frozen=True)
class GeneratedQuantifiedConditionalParitySpec:
    bundle: FixtureBundle
    expected_compile_case_ids: tuple[str, ...]
    expected_patterns: frozenset[str]
    branch_choices: tuple[str, ...]
    failure_prefix: str


HELPERS = ("search", "match", "fullmatch")
WRAPPER_PAIRS = (
    ("", ""),
    ("zz", ""),
    ("", "zz"),
    ("zz", "zz"),
)
FAILURE_PREVIEW_LIMIT = 20

QUANTIFIED_ALTERNATION_NUMBERED_PATTERN = r"a(b)?c(?(1)(de|df)|(eg|eh)){2}"
QUANTIFIED_ALTERNATION_NAMED_PATTERN = (
    r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}"
)

FIXTURE_BUNDLES = load_published_fixture_bundles(
    select_correctness_fixture_paths(CONDITIONAL_GROUP_EXISTS_FIXTURE_SELECTOR),
    pattern_extractor=str_case_pattern,
)
PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
COMPILE_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "compile")
MODULE_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "module_call")
PATTERN_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "pattern_call")
QUANTIFIED_CONDITIONAL_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "conditional-group-exists-quantified-workflows",
)
QUANTIFIED_CONDITIONAL_ALTERNATION_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "conditional-group-exists-quantified-alternation-workflows",
)
CASES_BY_ID = {case.case_id: case for case in PUBLISHED_CASES}
BASE_BUNDLES = FIXTURE_BUNDLES[:6]
QUANTIFIED_BUNDLES = FIXTURE_BUNDLES[6:12]
NESTED_ALTERNATION_BUNDLES = FIXTURE_BUNDLES[12:]
CORE_CONDITIONAL_COMPILE_CASES = fixture_cases_for_operation(
    BASE_BUNDLES + QUANTIFIED_BUNDLES,
    "compile",
)
NESTED_ALTERNATION_COMPILE_CASES = fixture_cases_for_operation(
    NESTED_ALTERNATION_BUNDLES,
    "compile",
)
BASE_MODULE_CASES = fixture_cases_for_operation(BASE_BUNDLES, "module_call")
QUANTIFIED_MODULE_CASES = fixture_cases_for_operation(
    QUANTIFIED_BUNDLES,
    "module_call",
)
NESTED_ALTERNATION_MODULE_CASES = fixture_cases_for_operation(
    NESTED_ALTERNATION_BUNDLES,
    "module_call",
)
BASE_PATTERN_CASES = fixture_cases_for_operation(BASE_BUNDLES, "pattern_call")
QUANTIFIED_PATTERN_CASES = fixture_cases_for_operation(
    QUANTIFIED_BUNDLES,
    "pattern_call",
)
NESTED_ALTERNATION_PATTERN_CASES = fixture_cases_for_operation(
    NESTED_ALTERNATION_BUNDLES,
    "pattern_call",
)
GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPECS = (
    GeneratedQuantifiedConditionalParitySpec(
        bundle=QUANTIFIED_CONDITIONAL_BUNDLE,
        expected_compile_case_ids=(
            "conditional-group-exists-quantified-compile-metadata-str",
            "named-conditional-group-exists-quantified-compile-metadata-str",
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|e){2}",
                r"a(?P<word>b)?c(?(word)d|e){2}",
            }
        ),
        branch_choices=("d", "e"),
        failure_prefix="quantified conditional generated parity drifted",
    ),
    GeneratedQuantifiedConditionalParitySpec(
        bundle=QUANTIFIED_CONDITIONAL_ALTERNATION_BUNDLE,
        expected_compile_case_ids=(
            "conditional-group-exists-quantified-alternation-compile-metadata-str",
            "named-conditional-group-exists-quantified-alternation-compile-metadata-str",
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)(de|df)|(eg|eh)){2}",
                r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
            }
        ),
        branch_choices=("de", "df", "eg", "eh"),
        failure_prefix="quantified conditional alternation generated parity drifted",
    ),
)


def _build_generated_quantified_conditional_candidate_texts(
    branch_choices: tuple[str, ...],
) -> tuple[str, ...]:
    cores = tuple(
        ("abc" if present else "ac") + "".join(branches)
        for present in (False, True)
        for branches in product(branch_choices, repeat=2)
    )
    return tuple(
        f"{wrapper_prefix}{core}{wrapper_suffix}"
        for core in cores
        for wrapper_prefix, wrapper_suffix in WRAPPER_PAIRS
    )


GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPEC_BY_MANIFEST_ID = {
    spec.bundle.expected_manifest_id: spec
    for spec in GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPECS
}
GENERATED_CONDITIONAL_CANDIDATE_TEXTS_BY_MANIFEST_ID = {
    spec.bundle.expected_manifest_id: _build_generated_quantified_conditional_candidate_texts(
        spec.branch_choices
    )
    for spec in GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPECS
}
GENERATED_QUANTIFIED_CONDITIONAL_COMPILE_CASES = tuple(
    case
    for spec in GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPECS
    for case in fixture_cases_for_operation((spec.bundle,), "compile")
)


PATTERN_BOUNDS_MATCH_CASES = (
    BoundedPatternCase(
        id="optional-group-conditional-search-normalizes-negative-and-oversized-bounds",
        pattern_case_id="optional-group-conditional-compile-metadata-str",
        helper="search",
        string="zzabcezz",
        bounds=(-100, 999),
    ),
    BoundedPatternCase(
        id="named-optional-group-conditional-fullmatch-preserves-absent-group-metadata-in-window",
        pattern_case_id="named-optional-group-conditional-compile-metadata-str",
        helper="fullmatch",
        string="zzadezz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="conditional-group-exists-search-normalizes-negative-and-oversized-bounds",
        pattern_case_id="conditional-group-exists-compile-metadata-str",
        helper="search",
        string="zzabcdzz",
        bounds=(-100, 999),
    ),
    BoundedPatternCase(
        id="named-conditional-group-exists-no-else-fullmatch-preserves-absent-group-metadata-in-window",
        pattern_case_id="named-conditional-group-exists-no-else-compile-metadata-str",
        helper="fullmatch",
        string="zzaczz",
        bounds=(2, 4),
    ),
    BoundedPatternCase(
        id="conditional-group-exists-empty-else-match-honors-narrowed-window",
        pattern_case_id="conditional-group-exists-empty-else-compile-metadata-str",
        helper="match",
        string="zzabcdzz",
        bounds=(2, 6),
    ),
    BoundedPatternCase(
        id="named-conditional-group-exists-empty-yes-else-fullmatch-preserves-absent-group-metadata-in-window",
        pattern_case_id="named-conditional-group-exists-empty-yes-else-compile-metadata-str",
        helper="fullmatch",
        string="zzacezz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="named-conditional-group-exists-fully-empty-fullmatch-preserves-present-group-metadata-in-window",
        pattern_case_id="named-conditional-group-exists-fully-empty-compile-metadata-str",
        helper="fullmatch",
        string="zzabczz",
        bounds=(2, 5),
    ),
)

PATTERN_BOUNDS_NO_MATCH_CASES = (
    BoundedPatternCase(
        id="named-optional-group-conditional-search-skips-match-before-pos",
        pattern_case_id="named-optional-group-conditional-compile-metadata-str",
        helper="search",
        string="zzadezz",
        bounds=(3, 7),
    ),
    BoundedPatternCase(
        id="optional-group-conditional-match-fails-when-endpos-truncates-suffix",
        pattern_case_id="optional-group-conditional-compile-metadata-str",
        helper="match",
        string="zzabcezz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="named-conditional-group-exists-search-skips-match-before-pos",
        pattern_case_id="named-conditional-group-exists-compile-metadata-str",
        helper="search",
        string="zzacezz",
        bounds=(3, 7),
    ),
    BoundedPatternCase(
        id="conditional-group-exists-no-else-match-fails-when-endpos-truncates-yes-branch",
        pattern_case_id="conditional-group-exists-no-else-compile-metadata-str",
        helper="match",
        string="zzabcdzz",
        bounds=(2, 5),
    ),
    BoundedPatternCase(
        id="named-conditional-group-exists-empty-else-fullmatch-does-not-expand-to-whole-string",
        pattern_case_id="named-conditional-group-exists-empty-else-compile-metadata-str",
        helper="fullmatch",
        string="zzaczz",
        bounds=(-100, 999),
    ),
    BoundedPatternCase(
        id="conditional-group-exists-empty-yes-else-search-skips-match-before-pos",
        pattern_case_id="conditional-group-exists-empty-yes-else-compile-metadata-str",
        helper="search",
        string="zzabczz",
        bounds=(3, 7),
    ),
    BoundedPatternCase(
        id="named-conditional-group-exists-fully-empty-fullmatch-fails-when-endpos-includes-extra-suffix",
        pattern_case_id="named-conditional-group-exists-fully-empty-compile-metadata-str",
        helper="fullmatch",
        string="zzaczz",
        bounds=(2, 5),
    ),
)

OPTIONAL_GROUP_CONDITIONAL_BRANCH_CASE_SPECS = (
    ("search-present-wrapper-hit", "search", "zzabcezz", (0, 999)),
    ("search-absent-wrapper-hit", "search", "zzadezz", (0, 999)),
    ("search-present-wrapper-miss-on-else-arm", "search", "zzabdezz", (0, 999)),
    ("search-absent-wrapper-miss-on-yes-arm", "search", "zzacezz", (0, 999)),
    ("match-present-window-hit", "match", "zzabcezz", (2, 6)),
    ("match-absent-window-hit", "match", "zzadezz", (2, 5)),
    ("match-present-window-miss-on-else-arm", "match", "zzabdezz", (2, 6)),
    ("match-absent-window-miss-on-yes-arm", "match", "zzacezz", (2, 5)),
    ("fullmatch-present-window-hit", "fullmatch", "zzabcezz", (2, 6)),
    ("fullmatch-absent-window-hit", "fullmatch", "zzadezz", (2, 5)),
    ("fullmatch-present-window-miss-on-else-arm", "fullmatch", "zzabdezz", (2, 6)),
    ("fullmatch-absent-window-miss-on-yes-arm", "fullmatch", "zzacezz", (2, 5)),
)


def _build_optional_group_conditional_branch_cases() -> (
    tuple[BoundedPatternCase, ...]
):
    cases: list[BoundedPatternCase] = []
    for case_prefix, pattern_case_id in (
        (
            "optional-group-conditional",
            "optional-group-conditional-compile-metadata-str",
        ),
        (
            "named-optional-group-conditional",
            "named-optional-group-conditional-compile-metadata-str",
        ),
    ):
        for scenario_suffix, helper, string, bounds in (
            OPTIONAL_GROUP_CONDITIONAL_BRANCH_CASE_SPECS
        ):
            cases.append(
                BoundedPatternCase(
                    id=f"{case_prefix}-{scenario_suffix}",
                    pattern_case_id=pattern_case_id,
                    helper=helper,
                    string=string,
                    bounds=bounds,
                )
            )
    return tuple(cases)


OPTIONAL_GROUP_CONDITIONAL_BRANCH_CASES = _build_optional_group_conditional_branch_cases()

MATCH_API_CASE_IDS = (
    "conditional-group-exists-quantified-module-search-present-str",
    "conditional-group-exists-quantified-module-fullmatch-absent-str",
    "named-conditional-group-exists-quantified-module-search-present-str",
    "named-conditional-group-exists-quantified-module-fullmatch-absent-str",
    "conditional-group-exists-quantified-alternation-pattern-fullmatch-present-second-arm-str",
    "conditional-group-exists-quantified-alternation-pattern-fullmatch-absent-second-arm-str",
    "named-conditional-group-exists-quantified-alternation-pattern-fullmatch-present-second-arm-str",
    "named-conditional-group-exists-quantified-alternation-pattern-fullmatch-absent-second-arm-str",
)
MATCH_API_CASES = tuple(CASES_BY_ID[case_id] for case_id in MATCH_API_CASE_IDS)

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
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=str_case_pattern,
    )


@pytest.mark.parametrize(
    "spec",
    GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPECS,
    ids=lambda spec: spec.bundle.expected_manifest_id,
)
def test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests(
    spec: GeneratedQuantifiedConditionalParitySpec,
) -> None:
    compile_cases = fixture_cases_for_operation((spec.bundle,), "compile")
    candidate_texts = GENERATED_CONDITIONAL_CANDIDATE_TEXTS_BY_MANIFEST_ID[
        spec.bundle.expected_manifest_id
    ]

    assert tuple(
        generated_spec.bundle.manifest.path
        for generated_spec in GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPECS
    ) == (
        QUANTIFIED_CONDITIONAL_BUNDLE.manifest.path,
        QUANTIFIED_CONDITIONAL_ALTERNATION_BUNDLE.manifest.path,
    )
    assert spec.bundle.manifest.path == published_fixture_bundle_by_manifest_id(
        FIXTURE_BUNDLES,
        spec.bundle.expected_manifest_id,
    ).manifest.path
    assert tuple(case.case_id for case in compile_cases) == spec.expected_compile_case_ids
    assert {str_case_pattern(case) for case in compile_cases} == spec.expected_patterns
    assert {case.text_model for case in compile_cases} == {"str"}
    assert len(candidate_texts) == len(
        _build_generated_quantified_conditional_candidate_texts(spec.branch_choices)
    )


def test_pattern_bounds_cases_stay_anchored_to_published_conditional_patterns() -> None:
    assert str_case_pattern(
        CASES_BY_ID["optional-group-conditional-compile-metadata-str"]
    ) == r"a(b)?(?(1)c|d)e"
    assert str_case_pattern(
        CASES_BY_ID["named-optional-group-conditional-compile-metadata-str"]
    ) == r"a(?P<word>b)?(?(word)c|d)e"
    assert str_case_pattern(CASES_BY_ID["conditional-group-exists-compile-metadata-str"]) == (
        r"a(b)?c(?(1)d|e)"
    )
    assert str_case_pattern(
        CASES_BY_ID["named-conditional-group-exists-no-else-compile-metadata-str"]
    ) == r"a(?P<word>b)?c(?(word)d)"
    assert str_case_pattern(
        CASES_BY_ID["conditional-group-exists-empty-else-compile-metadata-str"]
    ) == r"a(b)?c(?(1)d|)"
    assert str_case_pattern(
        CASES_BY_ID["named-conditional-group-exists-empty-else-compile-metadata-str"]
    ) == r"a(?P<word>b)?c(?(word)d|)"
    assert str_case_pattern(
        CASES_BY_ID["conditional-group-exists-empty-yes-else-compile-metadata-str"]
    ) == r"a(b)?c(?(1)|e)"
    assert str_case_pattern(
        CASES_BY_ID["named-conditional-group-exists-empty-yes-else-compile-metadata-str"]
    ) == r"a(?P<word>b)?c(?(word)|e)"
    assert str_case_pattern(
        CASES_BY_ID["named-conditional-group-exists-fully-empty-compile-metadata-str"]
    ) == r"a(?P<word>b)?c(?(word)|)"


def test_match_api_cases_remain_published_quantified_conditional_matches() -> None:
    assert tuple(case.case_id for case in MATCH_API_CASES) == MATCH_API_CASE_IDS
    assert {case.text_model for case in MATCH_API_CASES} == {"str"}


@pytest.mark.parametrize(
    "case",
    CORE_CONDITIONAL_COMPILE_CASES,
    ids=lambda case: case.case_id,
)
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


@pytest.mark.parametrize(
    "case",
    NESTED_ALTERNATION_COMPILE_CASES,
    ids=lambda case: case.case_id,
)
def test_nested_and_alternation_compile_metadata_matches_cpython(
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


@pytest.mark.parametrize(
    "case",
    GENERATED_QUANTIFIED_CONDITIONAL_COMPILE_CASES,
    ids=lambda case: case.case_id,
)
def test_generated_quantified_conditional_text_matrix_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    spec = GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPEC_BY_MANIFEST_ID[case.manifest_id]
    backend_name, backend = regex_backend
    pattern = str_case_pattern(case)
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        case.flags or 0,
    )

    failures: list[str] = []
    for text in GENERATED_CONDITIONAL_CANDIDATE_TEXTS_BY_MANIFEST_ID[
        spec.bundle.expected_manifest_id
    ]:
        for helper in HELPERS:
            record_generated_match_failure(
                failures,
                label=f"module.{helper}({pattern!r}, {text!r})",
                backend_name=backend_name,
                observed=getattr(backend, helper)(pattern, text),
                expected=getattr(re, helper)(pattern, text),
            )
            record_generated_match_failure(
                failures,
                label=f"pattern.{helper}({pattern!r}, {text!r})",
                backend_name=backend_name,
                observed=getattr(observed_pattern, helper)(text),
                expected=getattr(expected_pattern, helper)(text),
            )

    failure_preview = "\n".join(failures[:FAILURE_PREVIEW_LIMIT])
    if len(failures) > FAILURE_PREVIEW_LIMIT:
        failure_preview += f"\n... {len(failures) - FAILURE_PREVIEW_LIMIT} more"
    assert not failures, f"{spec.failure_prefix}:\n{failure_preview}"


@pytest.mark.parametrize("case", BASE_MODULE_CASES, ids=lambda case: case.case_id)
def test_module_search_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "search"

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", QUANTIFIED_MODULE_CASES, ids=lambda case: case.case_id)
def test_quantified_module_workflows_match_cpython(
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


@pytest.mark.parametrize(
    "case",
    NESTED_ALTERNATION_MODULE_CASES,
    ids=lambda case: case.case_id,
)
def test_nested_and_alternation_module_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert_match_result_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", PATTERN_BOUNDS_MATCH_CASES, ids=lambda case: case.id)
def test_pattern_helper_bounds_matches_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        str_case_pattern(CASES_BY_ID[case.pattern_case_id]),
    )

    observed = invoke_bounded_pattern_case(observed_pattern, case)
    expected = invoke_bounded_pattern_case(expected_pattern, case)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected, check_regs=True)
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", PATTERN_BOUNDS_NO_MATCH_CASES, ids=lambda case: case.id)
def test_pattern_helper_bounds_no_match_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        str_case_pattern(CASES_BY_ID[case.pattern_case_id]),
    )

    observed = invoke_bounded_pattern_case(observed_pattern, case)
    expected = invoke_bounded_pattern_case(expected_pattern, case)

    assert observed is None
    assert expected is None
    assert_match_result_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", BASE_PATTERN_CASES, ids=lambda case: case.case_id)
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

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", QUANTIFIED_PATTERN_CASES, ids=lambda case: case.case_id)
def test_quantified_pattern_fullmatch_matches_cpython(
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
    NESTED_ALTERNATION_PATTERN_CASES,
    ids=lambda case: case.case_id,
)
def test_nested_and_alternation_pattern_fullmatch_matches_cpython(
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

    assert_match_result_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    "case",
    OPTIONAL_GROUP_CONDITIONAL_BRANCH_CASES,
    ids=lambda case: case.id,
)
def test_optional_group_conditional_branch_selection_matches_cpython(
    regex_backend: tuple[str, object],
    case: BoundedPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        str_case_pattern(CASES_BY_ID[case.pattern_case_id]),
    )

    observed = getattr(observed_pattern, case.helper)(case.string, *case.bounds)
    expected = getattr(expected_pattern, case.helper)(case.string, *case.bounds)

    assert_match_result_parity(
        backend_name,
        observed,
        expected,
        check_regs=expected is not None,
    )
    if expected is None:
        return

    assert_match_convenience_api_parity(observed, expected)
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", MATCH_API_CASES, ids=lambda case: case.case_id)
def test_match_convenience_and_group_access_apis_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = workflow_result_with_cpython_parity(
        backend_name,
        backend,
        case,
    )

    assert observed is not None
    assert expected is not None
    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=True,
    )
    assert_match_convenience_api_parity(observed, expected)
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


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
