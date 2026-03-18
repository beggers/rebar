from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product
import re

import pytest

from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    FixtureBundle,
    FixtureBundleSpec,
    assert_fixture_bundle_contract,
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_result_parity,
    assert_valid_match_group_access_parity,
    case_pattern,
    compile_with_cpython_parity,
    load_fixture_bundles,
)


HELPERS = ("search", "match", "fullmatch")
WRAPPER_PAIRS = (
    ("", ""),
    ("zz", ""),
    ("", "zz"),
    ("zz", "zz"),
)


@dataclass(frozen=True)
class GeneratedParitySpec:
    fixture_name: str
    expected_manifest_id: str
    expected_compile_case_ids: tuple[str, ...]
    expected_patterns: frozenset[str]
    candidate_texts: tuple[str, ...]
    expected_candidate_count: int
    failure_prefix: str


def _build_quantified_conditional_candidate_texts() -> tuple[str, ...]:
    cores = tuple(
        ("abc" if present else "ac") + "".join(branches)
        for present in (False, True)
        for branches in product(("d", "e"), repeat=2)
    )
    return tuple(
        f"{wrapper_prefix}{core}{wrapper_suffix}"
        for core in cores
        for wrapper_prefix, wrapper_suffix in WRAPPER_PAIRS
    )


def _build_quantified_alternation_candidate_texts() -> tuple[str, ...]:
    cores = tuple(
        ("abc" if present else "ac") + "".join(branches)
        for present in (False, True)
        for branches in product(("de", "df", "eg", "eh"), repeat=2)
    )
    return tuple(
        f"{wrapper_prefix}{core}{wrapper_suffix}"
        for core in cores
        for wrapper_prefix, wrapper_suffix in WRAPPER_PAIRS
    )


GENERATED_PARITY_SPECS = (
    GeneratedParitySpec(
        fixture_name="conditional_group_exists_quantified_workflows.py",
        expected_manifest_id="conditional-group-exists-quantified-workflows",
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
        candidate_texts=_build_quantified_conditional_candidate_texts(),
        expected_candidate_count=32,
        failure_prefix="quantified conditional generated parity drifted",
    ),
    GeneratedParitySpec(
        fixture_name="conditional_group_exists_quantified_alternation_workflows.py",
        expected_manifest_id="conditional-group-exists-quantified-alternation-workflows",
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
        candidate_texts=_build_quantified_alternation_candidate_texts(),
        expected_candidate_count=128,
        failure_prefix="quantified conditional alternation generated parity drifted",
    ),
)

FIXTURE_BUNDLES = load_fixture_bundles(
    tuple(
        FixtureBundleSpec(
            fixture_name=spec.fixture_name,
            expected_manifest_id=spec.expected_manifest_id,
            selected_case_ids=spec.expected_compile_case_ids,
            expected_patterns=spec.expected_patterns,
            expected_operation_helper_counts=Counter({("compile", None): 2}),
        )
        for spec in GENERATED_PARITY_SPECS
    )
)
SPEC_BY_MANIFEST_ID = {
    spec.expected_manifest_id: spec for spec in GENERATED_PARITY_SPECS
}
COMPILE_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)


def _record_match_failure(
    failures: list[str],
    *,
    label: str,
    backend_name: str,
    observed: object,
    expected: re.Match[str] | None,
) -> None:
    try:
        assert_match_result_parity(
            backend_name,
            observed,
            expected,
            check_regs=True,
        )
        if expected is None:
            return

        assert_match_convenience_api_parity(observed, expected)
        assert_valid_match_group_access_parity(observed, expected)
        assert_invalid_match_group_access_parity(observed, expected)
    except AssertionError as exc:
        failures.append(f"{label}: {exc}")


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_generated_parity_suite_stays_anchored_to_published_compile_cases(
    bundle: FixtureBundle,
) -> None:
    spec = SPEC_BY_MANIFEST_ID[bundle.expected_manifest_id]

    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=case_pattern,
        expected_fixture_path=FIXTURES_DIR / spec.fixture_name,
        expected_ordered_case_ids=spec.expected_compile_case_ids,
    )
    assert len(spec.candidate_texts) == spec.expected_candidate_count


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_generated_text_matrix_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    spec = SPEC_BY_MANIFEST_ID[case.manifest_id]
    backend_name, backend = regex_backend
    pattern = case_pattern(case)
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        case.flags or 0,
    )

    failures: list[str] = []
    for text in spec.candidate_texts:
        for helper in HELPERS:
            _record_match_failure(
                failures,
                label=f"module.{helper}({pattern!r}, {text!r})",
                backend_name=backend_name,
                observed=getattr(backend, helper)(pattern, text),
                expected=getattr(re, helper)(pattern, text),
            )
            _record_match_failure(
                failures,
                label=f"pattern.{helper}({pattern!r}, {text!r})",
                backend_name=backend_name,
                observed=getattr(observed_pattern, helper)(text),
                expected=getattr(expected_pattern, helper)(text),
            )

    failure_preview = "\n".join(failures[:20])
    if len(failures) > 20:
        failure_preview += f"\n... {len(failures) - 20} more"
    assert not failures, f"{spec.failure_prefix}:\n{failure_preview}"
