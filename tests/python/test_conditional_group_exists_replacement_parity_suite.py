from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

from rebar_harness.correctness import (
    FixtureCase,
    FixtureManifest,
    load_fixture_manifest,
)
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    select_published_fixture_paths,
    str_case_pattern,
)


EXPECTED_PUBLISHED_FIXTURE_NAMES = (
    "conditional_group_exists_alternation_replacement_workflows.py",
    "conditional_group_exists_empty_else_replacement_workflows.py",
    "conditional_group_exists_empty_yes_else_replacement_workflows.py",
    "conditional_group_exists_fully_empty_replacement_workflows.py",
    "conditional_group_exists_nested_replacement_workflows.py",
    "conditional_group_exists_no_else_replacement_workflows.py",
    "conditional_group_exists_quantified_replacement_workflows.py",
    "conditional_group_exists_replacement_workflows.py",
)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    sorted(
        (FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES),
        key=lambda path: path.name,
    )
)
PUBLISHED_CONDITIONAL_REPLACEMENT_FIXTURE_PATHS = select_published_fixture_paths(
    EXPECTED_PUBLISHED_FIXTURE_PATHS
)
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
        "conditional_group_exists_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-replacement-present-str",
                "module-subn-conditional-group-exists-replacement-absent-str",
                "pattern-sub-conditional-group-exists-replacement-present-str",
                "pattern-subn-conditional-group-exists-replacement-absent-str",
                "module-sub-named-conditional-group-exists-replacement-present-str",
                "module-subn-named-conditional-group-exists-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|e)",
                r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
    ),
    _fixture_bundle(
        "conditional_group_exists_no_else_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-no-else-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-no-else-replacement-present-str",
                "module-subn-conditional-group-exists-no-else-replacement-absent-str",
                "pattern-sub-conditional-group-exists-no-else-replacement-present-str",
                "pattern-subn-conditional-group-exists-no-else-replacement-absent-str",
                "module-sub-named-conditional-group-exists-no-else-replacement-present-str",
                "module-subn-named-conditional-group-exists-no-else-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-no-else-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-no-else-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)d)",
                r"a(?P<word>b)?c(?(word)d)",
            }
        ),
    ),
    _fixture_bundle(
        "conditional_group_exists_empty_else_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-else-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-empty-else-replacement-present-str",
                "module-subn-conditional-group-exists-empty-else-replacement-absent-str",
                "pattern-sub-conditional-group-exists-empty-else-replacement-present-str",
                "pattern-subn-conditional-group-exists-empty-else-replacement-absent-str",
                "module-sub-named-conditional-group-exists-empty-else-replacement-present-str",
                "module-subn-named-conditional-group-exists-empty-else-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-empty-else-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-empty-else-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|)",
                r"a(?P<word>b)?c(?(word)d|)",
            }
        ),
    ),
    _fixture_bundle(
        "conditional_group_exists_empty_yes_else_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-empty-yes-else-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-empty-yes-else-replacement-present-str",
                "module-subn-conditional-group-exists-empty-yes-else-replacement-absent-str",
                "pattern-sub-conditional-group-exists-empty-yes-else-replacement-present-str",
                "pattern-subn-conditional-group-exists-empty-yes-else-replacement-absent-str",
                "module-sub-named-conditional-group-exists-empty-yes-else-replacement-present-str",
                "module-subn-named-conditional-group-exists-empty-yes-else-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-empty-yes-else-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-empty-yes-else-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)|e)",
                r"a(?P<word>b)?c(?(word)|e)",
            }
        ),
    ),
    _fixture_bundle(
        "conditional_group_exists_fully_empty_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-fully-empty-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-fully-empty-replacement-present-str",
                "module-subn-conditional-group-exists-fully-empty-replacement-absent-str",
                "pattern-sub-conditional-group-exists-fully-empty-replacement-present-str",
                "pattern-subn-conditional-group-exists-fully-empty-replacement-absent-str",
                "module-sub-named-conditional-group-exists-fully-empty-replacement-present-str",
                "module-subn-named-conditional-group-exists-fully-empty-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-fully-empty-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-fully-empty-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)|)",
                r"a(?P<word>b)?c(?(word)|)",
            }
        ),
    ),
    _fixture_bundle(
        "conditional_group_exists_alternation_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-alternation-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-alternation-replacement-present-first-arm-str",
                "module-subn-conditional-group-exists-alternation-replacement-present-second-arm-str",
                "pattern-sub-conditional-group-exists-alternation-replacement-absent-first-arm-str",
                "pattern-subn-conditional-group-exists-alternation-replacement-absent-second-arm-str",
                "module-sub-named-conditional-group-exists-alternation-replacement-present-first-arm-str",
                "module-subn-named-conditional-group-exists-alternation-replacement-present-second-arm-str",
                "pattern-sub-named-conditional-group-exists-alternation-replacement-absent-first-arm-str",
                "pattern-subn-named-conditional-group-exists-alternation-replacement-absent-second-arm-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)(de|df)|(eg|eh))",
                r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
            }
        ),
    ),
    _fixture_bundle(
        "conditional_group_exists_nested_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-nested-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-nested-replacement-present-str",
                "module-subn-conditional-group-exists-nested-replacement-absent-str",
                "pattern-sub-conditional-group-exists-nested-replacement-present-str",
                "pattern-subn-conditional-group-exists-nested-replacement-absent-str",
                "module-sub-named-conditional-group-exists-nested-replacement-present-str",
                "module-subn-named-conditional-group-exists-nested-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-nested-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-nested-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)(?(1)d|e)|f)",
                r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            }
        ),
    ),
    _fixture_bundle(
        "conditional_group_exists_quantified_replacement_workflows.py",
        expected_manifest_id="conditional-group-exists-quantified-replacement-workflows",
        expected_case_ids=frozenset(
            {
                "module-sub-conditional-group-exists-quantified-replacement-present-str",
                "module-subn-conditional-group-exists-quantified-replacement-absent-str",
                "pattern-sub-conditional-group-exists-quantified-replacement-present-str",
                "pattern-subn-conditional-group-exists-quantified-replacement-absent-str",
                "module-sub-named-conditional-group-exists-quantified-replacement-present-str",
                "module-subn-named-conditional-group-exists-quantified-replacement-absent-str",
                "pattern-sub-named-conditional-group-exists-quantified-replacement-present-str",
                "pattern-subn-named-conditional-group-exists-quantified-replacement-absent-str",
            }
        ),
        expected_patterns=frozenset(
            {
                r"a(b)?c(?(1)d|e){2}",
                r"a(?P<word>b)?c(?(word)d|e){2}",
            }
        ),
    ),
)

REPLACEMENT_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)


def _run_replacement_case(backend: object, case: FixtureCase) -> object:
    if case.helper is None:
        raise ValueError(f"case {case.case_id!r} requires a helper name")

    if case.operation == "module_call":
        return getattr(backend, case.helper)(*case.args, **case.kwargs)

    if case.operation == "pattern_call":
        compiled = backend.compile(case.pattern_payload(), case.flags or 0)
        return getattr(compiled, case.helper)(*case.args, **case.kwargs)

    raise ValueError(f"unsupported replacement parity operation {case.operation!r}")


def test_replacement_parity_suite_discovers_all_published_correctness_fixtures() -> None:
    assert PUBLISHED_CONDITIONAL_REPLACEMENT_FIXTURE_PATHS
    assert PUBLISHED_CONDITIONAL_REPLACEMENT_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS


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
    assert {str_case_pattern(case) for case in bundle.cases} == bundle.expected_patterns
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        EXPECTED_OPERATION_HELPER_COUNTS
    )


@pytest.mark.parametrize("case", REPLACEMENT_CASES, ids=lambda case: case.case_id)
def test_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    observed = _run_replacement_case(backend, case)
    expected = _run_replacement_case(re, case)
    assert observed == expected
