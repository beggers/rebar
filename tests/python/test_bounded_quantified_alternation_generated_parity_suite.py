from __future__ import annotations

from collections import Counter
from itertools import product
import re

import pytest

from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
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


QUANTIFIED_ALTERNATION_FIXTURE_PATH = FIXTURES_DIR / "quantified_alternation_workflows.py"
EXPECTED_COMPILE_CASE_IDS = (
    "quantified-alternation-numbered-compile-metadata-str",
    "quantified-alternation-named-compile-metadata-str",
    "quantified-alternation-numbered-compile-metadata-bytes",
    "quantified-alternation-named-compile-metadata-bytes",
)
EXPECTED_PATTERNS = frozenset(
    {
        r"a(b|c){1,2}d",
        r"a(?P<word>b|c){1,2}d",
        rb"a(b|c){1,2}d",
        rb"a(?P<word>b|c){1,2}d",
    }
)
EXPECTED_OPERATION_HELPER_COUNTS = Counter({("compile", None): 4})
HELPERS = ("search", "match", "fullmatch")
BODY_ATOMS = ("b", "c", "e")
WRAPPER_PAIRS = (
    ("", ""),
    ("zz", ""),
    ("", "zz"),
    ("zz", "zz"),
)

(BOUNDED_QUANTIFIED_ALTERNATION_BUNDLE,) = load_fixture_bundles(
    (
        FixtureBundleSpec(
            fixture_name="quantified_alternation_workflows.py",
            expected_manifest_id="quantified-alternation-workflows",
            selected_case_ids=EXPECTED_COMPILE_CASE_IDS,
            expected_patterns=EXPECTED_PATTERNS,
            expected_operation_helper_counts=EXPECTED_OPERATION_HELPER_COUNTS,
            expected_text_models=frozenset({"bytes", "str"}),
        ),
    )
)
COMPILE_CASES = tuple(BOUNDED_QUANTIFIED_ALTERNATION_BUNDLE.cases)
ASCII_CANDIDATE_TEXTS = tuple(
    f"{prefix}a{''.join(body)}d{suffix}"
    for length in range(4)
    for body in product(BODY_ATOMS, repeat=length)
    for prefix, suffix in WRAPPER_PAIRS
)


def _candidate_texts(case: FixtureCase) -> tuple[str | bytes, ...]:
    if case.text_model == "bytes":
        return tuple(text.encode("ascii") for text in ASCII_CANDIDATE_TEXTS)
    return ASCII_CANDIDATE_TEXTS


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


def test_bounded_quantified_alternation_generated_parity_suite_stays_anchored_to_published_compile_cases(
) -> None:
    assert_fixture_bundle_contract(
        BOUNDED_QUANTIFIED_ALTERNATION_BUNDLE,
        pattern_extractor=case_pattern,
        expected_fixture_path=QUANTIFIED_ALTERNATION_FIXTURE_PATH,
        expected_ordered_case_ids=EXPECTED_COMPILE_CASE_IDS,
    )
    assert len(ASCII_CANDIDATE_TEXTS) == 160


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_bounded_quantified_alternation_generated_text_matrix_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    pattern = case_pattern(case)
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        case.flags or 0,
    )

    failures: list[str] = []
    for text in _candidate_texts(case):
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
    assert not failures, (
        "bounded quantified alternation generated parity drifted:\n"
        f"{failure_preview}"
    )
