from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product
import re

import pytest

from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FixtureBundle,
    FixtureBundleSpec,
    assert_fixture_bundle_contract,
    assert_match_convenience_api_parity,
    assert_match_parity,
    case_pattern,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    load_fixture_bundles,
)
BROADER_RANGE_BYTES_SKIP_REASON = (
    "rebar does not yet support broader-range wider-ranged-repeat "
    "grouped-conditional bytes parity"
)
BACKTRACKING_BRANCH_TEXT = {
    "short": "bc",
    "long": "bcc",
}


@dataclass(frozen=True)
class SupplementalCase:
    id: str
    pattern: bytes
    search_matches: tuple[bytes, ...] = ()
    search_misses: tuple[bytes, ...] = ()
    fullmatch_matches: tuple[bytes, ...] = ()
    fullmatch_misses: tuple[bytes, ...] = ()
    unsupported_backends: tuple[str, ...] = ()
    unsupported_backend_reason: str | None = None


@dataclass(frozen=True)
class BacktrackingTraceCase:
    id: str
    pattern: str
    search_text: str
    fullmatch_text: str

FIXTURE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        "wider_ranged_repeat_quantified_group_workflows.py",
        expected_manifest_id="wider-ranged-repeat-quantified-group-workflows",
        expected_patterns=frozenset(
            {
                r"a(bc){1,3}d",
                r"a(?P<word>bc){1,3}d",
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
    FixtureBundleSpec(
        "broader_range_wider_ranged_repeat_quantified_group_workflows.py",
        expected_manifest_id=(
            "broader-range-wider-ranged-repeat-quantified-group-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a(bc){1,4}d",
                r"a(?P<word>bc){1,4}d",
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
    FixtureBundleSpec(
        "wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
        expected_manifest_id=(
            "wider-ranged-repeat-quantified-group-alternation-conditional-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a((bc|de){1,3})?(?(1)d|e)",
                r"a(?P<outer>(bc|de){1,3})?(?(outer)d|e)",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 6,
                ("pattern_call", "fullmatch"): 4,
            }
        ),
    ),
    FixtureBundleSpec(
        "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
        expected_manifest_id=(
            "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a((bc|b)c){1,3}d",
                r"a(?P<word>(bc|b)c){1,3}d",
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
    FixtureBundleSpec(
        "broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py",
        expected_manifest_id=(
            "broader-range-wider-ranged-repeat-quantified-group-alternation-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a(bc|de){1,4}d",
                r"a(?P<word>bc|de){1,4}d",
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
    FixtureBundleSpec(
        "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
        expected_manifest_id=(
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a((bc|de){1,4})?(?(1)d|e)",
                r"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
                rb"a((bc|de){1,4})?(?(1)d|e)",
                rb"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 4,
                ("module_call", "search"): 12,
                ("pattern_call", "fullmatch"): 12,
            }
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    ),
    FixtureBundleSpec(
        "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
        expected_manifest_id=(
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a((bc|b)c){1,4}d",
                r"a(?P<word>(bc|b)c){1,4}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 5,
                ("pattern_call", "fullmatch"): 7,
            }
        ),
    ),
    FixtureBundleSpec(
        "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py",
        expected_manifest_id=(
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a((bc|de){1,4})d",
                r"a(?P<outer>(bc|de){1,4})d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 4,
                ("pattern_call", "fullmatch"): 8,
            }
        ),
    ),
    FixtureBundleSpec(
        "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
        expected_manifest_id=(
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a(((bc|de){1,4})d)?(?(1)e|f)",
                r"a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 6,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
    ),
    FixtureBundleSpec(
        "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
        expected_manifest_id=(
            "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a(((bc|b)c){1,4})d",
                r"a(?P<outer>((bc|b)c){1,4})d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 5,
                ("pattern_call", "fullmatch"): 7,
            }
        ),
    ),
)
FIXTURE_BUNDLES = load_fixture_bundles(FIXTURE_BUNDLE_SPECS)
FIXTURE_BUNDLES_BY_MANIFEST_ID = {
    bundle.manifest.manifest_id: bundle for bundle in FIXTURE_BUNDLES
}
BROADER_RANGE_CONDITIONAL_BUNDLE = FIXTURE_BUNDLES_BY_MANIFEST_ID[
    "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows"
]
BACKTRACKING_TRACE_BUNDLES = (
    FIXTURE_BUNDLES_BY_MANIFEST_ID[
        "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows"
    ],
    FIXTURE_BUNDLES_BY_MANIFEST_ID[
        "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows"
    ],
)
BROADER_RANGE_CONDITIONAL_BYTES_CASES = (
    SupplementalCase(
        id="broader-range-wider-ranged-repeat-conditional-numbered-bytes",
        pattern=rb"a((bc|de){1,4})?(?(1)d|e)",
        search_matches=(b"zzaezz", b"zzabcdzz", b"zzadedzz", b"zzabcdedededzz"),
        search_misses=(b"zzadzz", b"zzabcbcbcbcbcdzz"),
        fullmatch_matches=(b"ae", b"abcded", b"abcbcded", b"abcdededed"),
        fullmatch_misses=(b"ad", b"abcdede", b"abcbcbcbcbcd"),
        unsupported_backends=("rebar",),
        unsupported_backend_reason=BROADER_RANGE_BYTES_SKIP_REASON,
    ),
    SupplementalCase(
        id="broader-range-wider-ranged-repeat-conditional-named-bytes",
        pattern=rb"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
        search_matches=(b"zzaezz", b"zzabcdzz", b"zzadedzz", b"zzabcdedededzz"),
        search_misses=(b"zzadzz", b"zzabcbcbcbcbcdzz"),
        fullmatch_matches=(b"ae", b"abcded", b"abcbcded", b"abcdededed"),
        fullmatch_misses=(b"ad", b"abcdede", b"abcbcbcbcbcd"),
        unsupported_backends=("rebar",),
        unsupported_backend_reason=BROADER_RANGE_BYTES_SKIP_REASON,
    ),
)


def _uses_direct_bytes_follow_on(case: FixtureCase) -> bool:
    return (
        case.manifest_id
        == "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows"
        and case.text_model == "bytes"
    )


# Keep the shared manifest contract honest, but route the published bytes slice
# through the explicit supplemental parity anchor until Rust-backed bytes support
# lands for these patterns.
COMPILE_CASES = tuple(
    case
    for case in fixture_cases_for_operation(FIXTURE_BUNDLES, "compile")
    if not _uses_direct_bytes_follow_on(case)
)
MODULE_CASES = tuple(
    case
    for case in fixture_cases_for_operation(FIXTURE_BUNDLES, "module_call")
    if not _uses_direct_bytes_follow_on(case)
)
PATTERN_CASES = tuple(
    case
    for case in fixture_cases_for_operation(FIXTURE_BUNDLES, "pattern_call")
    if not _uses_direct_bytes_follow_on(case)
)


def _build_backtracking_trace_cases(
    *,
    prefix: str,
    numbered_pattern: str,
    named_pattern: str,
) -> tuple[BacktrackingTraceCase, ...]:
    cases: list[BacktrackingTraceCase] = []
    for variant, pattern in (
        ("numbered", numbered_pattern),
        ("named", named_pattern),
    ):
        for repetition_count in range(1, 5):
            for branch_order in product(("short", "long"), repeat=repetition_count):
                body = "".join(BACKTRACKING_BRANCH_TEXT[branch] for branch in branch_order)
                branch_id = "-".join(branch_order)
                fullmatch_text = f"a{body}d"
                cases.append(
                    BacktrackingTraceCase(
                        id=f"{prefix}-{variant}-{branch_id}",
                        pattern=pattern,
                        search_text=f"zz{fullmatch_text}zz",
                        fullmatch_text=fullmatch_text,
                    )
                )
    return tuple(cases)


BACKTRACKING_TRACE_CASES = (
    *_build_backtracking_trace_cases(
        prefix="broader-range-wider-ranged-repeat-backtracking",
        numbered_pattern=r"a((bc|b)c){1,4}d",
        named_pattern=r"a(?P<word>(bc|b)c){1,4}d",
    ),
    *_build_backtracking_trace_cases(
        prefix="nested-broader-range-wider-ranged-repeat-backtracking",
        numbered_pattern=r"a(((bc|b)c){1,4})d",
        named_pattern=r"a(?P<outer>((bc|b)c){1,4})d",
    ),
)
EXPECTED_BACKTRACKING_FULLMATCH_TEXTS = frozenset(
    f"a{''.join(BACKTRACKING_BRANCH_TEXT[branch] for branch in branch_order)}d"
    for repetition_count in range(1, 5)
    for branch_order in product(("short", "long"), repeat=repetition_count)
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
        pattern_extractor=case_pattern,
    )


def test_broader_range_conditional_bytes_cases_stay_explicit_and_rebar_gated() -> None:
    bundle_str_cases = tuple(
        case for case in BROADER_RANGE_CONDITIONAL_BUNDLE.cases if case.text_model == "str"
    )
    bundle_bytes_cases = tuple(
        case for case in BROADER_RANGE_CONDITIONAL_BUNDLE.cases if case.text_model == "bytes"
    )
    expected_compile_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation((BROADER_RANGE_CONDITIONAL_BUNDLE,), "compile")
        if case.text_model == "bytes"
    )

    assert len(BROADER_RANGE_CONDITIONAL_BYTES_CASES) == 2
    assert {case.id for case in BROADER_RANGE_CONDITIONAL_BYTES_CASES} == {
        "broader-range-wider-ranged-repeat-conditional-numbered-bytes",
        "broader-range-wider-ranged-repeat-conditional-named-bytes",
    }
    assert {case.pattern for case in BROADER_RANGE_CONDITIONAL_BYTES_CASES} == (
        expected_compile_patterns
    )
    assert len(bundle_str_cases) == len(bundle_bytes_cases) == 14
    assert {case.case_id for case in bundle_bytes_cases} == {
        f"{case.case_id.removesuffix('-str')}-bytes" for case in bundle_str_cases
    }
    assert Counter((case.operation, case.helper) for case in bundle_bytes_cases) == Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 6,
            ("pattern_call", "fullmatch"): 6,
        }
    )

    for case in BROADER_RANGE_CONDITIONAL_BYTES_CASES:
        assert case.unsupported_backends == ("rebar",)
        assert case.unsupported_backend_reason == BROADER_RANGE_BYTES_SKIP_REASON
        assert len(case.search_matches) == 4
        assert len(case.search_misses) == 2
        assert len(case.fullmatch_matches) == 4
        assert len(case.fullmatch_misses) == 3
        assert b"zzaezz" in case.search_matches
        assert b"zzabcdedededzz" in case.search_matches
        assert b"zzadzz" in case.search_misses
        assert b"zzabcbcbcbcbcdzz" in case.search_misses
        assert b"ae" in case.fullmatch_matches
        assert b"abcdededed" in case.fullmatch_matches
        assert b"ad" in case.fullmatch_misses
        assert b"abcbcbcbcbcd" in case.fullmatch_misses
        assert set(case.search_matches).isdisjoint(case.search_misses)
        assert set(case.fullmatch_matches).isdisjoint(case.fullmatch_misses)
        assert all(
            isinstance(text, bytes)
            for text in (
                *case.search_matches,
                *case.search_misses,
                *case.fullmatch_matches,
                *case.fullmatch_misses,
            )
        )

    published_module_texts_by_pattern: dict[bytes, set[bytes]] = {}
    published_fullmatch_texts_by_pattern: dict[bytes, set[bytes]] = {}
    for case in bundle_bytes_cases:
        pattern = case_pattern(case)
        assert isinstance(pattern, bytes)
        if case.operation == "module_call":
            text = case.args[1]
            assert isinstance(text, bytes)
            published_module_texts_by_pattern.setdefault(pattern, set()).add(text)
        elif case.operation == "pattern_call":
            text = case.args[0]
            assert isinstance(text, bytes)
            published_fullmatch_texts_by_pattern.setdefault(pattern, set()).add(text)

    numbered_case, named_case = BROADER_RANGE_CONDITIONAL_BYTES_CASES
    assert published_module_texts_by_pattern == {
        numbered_case.pattern: {b"zzaezz", b"zzabcdzz", b"zzadedzz"},
        named_case.pattern: {b"zzaezz", b"zzadedzz", b"zzabcdedededzz"},
    }
    assert published_fullmatch_texts_by_pattern == {
        numbered_case.pattern: {b"abcbcded", b"abcdede", b"ad"},
        named_case.pattern: {b"abcbcded", b"abcbcbcbcbcd", b"ad"},
    }


def test_backtracking_trace_cases_cover_all_declared_branch_orders() -> None:
    expected_patterns = frozenset(
        case_pattern(case)
        for bundle in BACKTRACKING_TRACE_BUNDLES
        for case in fixture_cases_for_operation((bundle,), "compile")
    )

    assert len(EXPECTED_BACKTRACKING_FULLMATCH_TEXTS) == 30
    assert len(BACKTRACKING_TRACE_CASES) == (
        len(expected_patterns) * len(EXPECTED_BACKTRACKING_FULLMATCH_TEXTS)
    )
    assert len({case.id for case in BACKTRACKING_TRACE_CASES}) == len(
        BACKTRACKING_TRACE_CASES
    )
    assert {case.pattern for case in BACKTRACKING_TRACE_CASES} == expected_patterns

    for pattern in expected_patterns:
        matching_cases = tuple(
            case for case in BACKTRACKING_TRACE_CASES if case.pattern == pattern
        )
        assert len(matching_cases) == len(EXPECTED_BACKTRACKING_FULLMATCH_TEXTS)
        assert {case.fullmatch_text for case in matching_cases} == (
            EXPECTED_BACKTRACKING_FULLMATCH_TEXTS
        )
        assert {case.search_text for case in matching_cases} == {
            f"zz{text}zz" for text in EXPECTED_BACKTRACKING_FULLMATCH_TEXTS
        }


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

    assert_match_parity(backend_name, observed, expected)


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

    assert_match_parity(backend_name, observed, expected)


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


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_conditional_bytes_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend

    compile_with_cpython_parity(backend_name, backend, case.pattern)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_conditional_bytes_module_search_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        assert_match_parity(backend_name, observed, expected)

    for text in case.search_misses:
        assert backend.search(case.pattern, text) is None
        assert re.search(case.pattern, text) is None


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_conditional_bytes_module_search_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_conditional_bytes_pattern_fullmatch_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    for text in case.fullmatch_matches:
        observed = observed_pattern.fullmatch(text)
        expected = expected_pattern.fullmatch(text)

        assert observed is not None
        assert expected is not None
        assert_match_parity(backend_name, observed, expected)

    for text in case.fullmatch_misses:
        assert observed_pattern.fullmatch(text) is None
        assert expected_pattern.fullmatch(text) is None


@pytest.mark.parametrize(
    "case",
    BROADER_RANGE_CONDITIONAL_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_broader_range_conditional_bytes_pattern_fullmatch_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    for text in case.fullmatch_matches:
        observed = observed_pattern.fullmatch(text)
        expected = expected_pattern.fullmatch(text)

        assert observed is not None
        assert expected is not None
        assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", BACKTRACKING_TRACE_CASES, ids=lambda case: case.id)
def test_backtracking_module_search_branch_traces_match_cpython(
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
def test_backtracking_pattern_fullmatch_branch_traces_match_cpython(
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
