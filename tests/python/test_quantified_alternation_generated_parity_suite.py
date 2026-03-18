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


@dataclass(frozen=True)
class GeneratedParitySpec:
    fixture_name: str
    expected_manifest_id: str
    expected_compile_case_ids: tuple[str, ...]
    expected_patterns: frozenset[str | bytes]
    candidate_lengths: range
    expected_candidate_count: int
    failure_prefix: str


HELPERS = ("search", "match", "fullmatch")
BODY_ATOMS = ("b", "c", "e")
WRAPPER_PAIRS = (
    ("", ""),
    ("zz", ""),
    ("", "zz"),
    ("zz", "zz"),
)
EXPECTED_OPERATION_HELPER_COUNTS = Counter({("compile", None): 4})
EXPECTED_TEXT_MODELS = frozenset({"bytes", "str"})

GENERATED_PARITY_SPECS = (
    GeneratedParitySpec(
        fixture_name="quantified_alternation_workflows.py",
        expected_manifest_id="quantified-alternation-workflows",
        expected_compile_case_ids=(
            "quantified-alternation-numbered-compile-metadata-str",
            "quantified-alternation-named-compile-metadata-str",
            "quantified-alternation-numbered-compile-metadata-bytes",
            "quantified-alternation-named-compile-metadata-bytes",
        ),
        expected_patterns=frozenset(
            {
                r"a(b|c){1,2}d",
                r"a(?P<word>b|c){1,2}d",
                rb"a(b|c){1,2}d",
                rb"a(?P<word>b|c){1,2}d",
            }
        ),
        candidate_lengths=range(4),
        expected_candidate_count=160,
        failure_prefix="bounded quantified alternation generated parity drifted",
    ),
    GeneratedParitySpec(
        fixture_name="quantified_alternation_broader_range_workflows.py",
        expected_manifest_id="quantified-alternation-broader-range-workflows",
        expected_compile_case_ids=(
            "quantified-alternation-broader-range-numbered-compile-metadata-str",
            "quantified-alternation-broader-range-named-compile-metadata-str",
            "quantified-alternation-broader-range-numbered-compile-metadata-bytes",
            "quantified-alternation-broader-range-named-compile-metadata-bytes",
        ),
        expected_patterns=frozenset(
            {
                r"a(b|c){1,3}d",
                r"a(?P<word>b|c){1,3}d",
                rb"a(b|c){1,3}d",
                rb"a(?P<word>b|c){1,3}d",
            }
        ),
        candidate_lengths=range(5),
        expected_candidate_count=484,
        failure_prefix="broader-range quantified alternation generated parity drifted",
    ),
    GeneratedParitySpec(
        fixture_name="quantified_alternation_backtracking_heavy_workflows.py",
        expected_manifest_id="quantified-alternation-backtracking-heavy-workflows",
        expected_compile_case_ids=(
            "quantified-alternation-backtracking-heavy-numbered-compile-metadata-str",
            "quantified-alternation-backtracking-heavy-named-compile-metadata-str",
            "quantified-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
            "quantified-alternation-backtracking-heavy-named-compile-metadata-bytes",
        ),
        expected_patterns=frozenset(
            {
                r"a(b|bc){1,2}d",
                r"a(?P<word>b|bc){1,2}d",
                rb"a(b|bc){1,2}d",
                rb"a(?P<word>b|bc){1,2}d",
            }
        ),
        candidate_lengths=range(5),
        expected_candidate_count=484,
        failure_prefix="backtracking-heavy quantified alternation generated parity drifted",
    ),
)

FIXTURE_BUNDLES = load_fixture_bundles(
    tuple(
        FixtureBundleSpec(
            fixture_name=spec.fixture_name,
            expected_manifest_id=spec.expected_manifest_id,
            selected_case_ids=spec.expected_compile_case_ids,
            expected_patterns=spec.expected_patterns,
            expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            expected_text_models=EXPECTED_TEXT_MODELS,
        )
        for spec in GENERATED_PARITY_SPECS
    )
)
SPEC_BY_MANIFEST_ID = {
    spec.expected_manifest_id: spec for spec in GENERATED_PARITY_SPECS
}
ASCII_CANDIDATE_TEXTS_BY_MANIFEST_ID = {
    spec.expected_manifest_id: tuple(
        f"{prefix}a{''.join(body)}d{suffix}"
        for length in spec.candidate_lengths
        for body in product(BODY_ATOMS, repeat=length)
        for prefix, suffix in WRAPPER_PAIRS
    )
    for spec in GENERATED_PARITY_SPECS
}
BYTES_CANDIDATE_TEXTS_BY_MANIFEST_ID = {
    manifest_id: tuple(text.encode("ascii") for text in texts)
    for manifest_id, texts in ASCII_CANDIDATE_TEXTS_BY_MANIFEST_ID.items()
}
COMPILE_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)


def _candidate_texts(
    spec: GeneratedParitySpec,
    case: FixtureCase,
) -> tuple[str | bytes, ...]:
    if case.text_model == "bytes":
        return BYTES_CANDIDATE_TEXTS_BY_MANIFEST_ID[spec.expected_manifest_id]
    return ASCII_CANDIDATE_TEXTS_BY_MANIFEST_ID[spec.expected_manifest_id]


def _record_match_failure(
    failures: list[str],
    *,
    label: str,
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes] | None,
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
    assert (
        len(ASCII_CANDIDATE_TEXTS_BY_MANIFEST_ID[spec.expected_manifest_id])
        == spec.expected_candidate_count
    )


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
    for text in _candidate_texts(spec, case):
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
