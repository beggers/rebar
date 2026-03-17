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
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_valid_match_group_access_parity,
    case_pattern,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    load_fixture_bundles,
    published_fixture_bundle_by_manifest_id,
)


OPEN_ENDED_BRANCH_TEXT = {
    "bc": "bc",
    "de": "de",
}


@dataclass(frozen=True)
class SupplementalCase:
    id: str
    pattern: bytes
    search_matches: tuple[bytes, ...] = ()
    search_misses: tuple[bytes, ...] = ()
    fullmatch_matches: tuple[bytes, ...] = ()
    fullmatch_misses: tuple[bytes, ...] = ()


@dataclass(frozen=True)
class OpenEndedTraceCase:
    id: str
    pattern: str
    search_text: str
    fullmatch_text: str


FIXTURE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        "open_ended_quantified_group_alternation_workflows.py",
        expected_manifest_id="open-ended-quantified-group-alternation-workflows",
        expected_patterns=frozenset(
            {
                r"a(bc|de){1,}d",
                r"a(?P<word>bc|de){1,}d",
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
    FixtureBundleSpec(
        "open_ended_quantified_group_alternation_conditional_workflows.py",
        expected_manifest_id="open-ended-quantified-group-alternation-conditional-workflows",
        expected_patterns=frozenset(
            {
                r"a((bc|de){1,})?(?(1)d|e)",
                r"a(?P<outer>(bc|de){1,})?(?(outer)d|e)",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 6,
                ("pattern_call", "fullmatch"): 5,
            }
        ),
    ),
    FixtureBundleSpec(
        "open_ended_quantified_group_alternation_backtracking_heavy_workflows.py",
        expected_manifest_id="open-ended-quantified-group-alternation-backtracking-heavy-workflows",
        expected_patterns=frozenset(
            {
                r"a((bc|b)c){1,}d",
                r"a(?P<word>(bc|b)c){1,}d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 2,
                ("module_call", "search"): 5,
                ("pattern_call", "fullmatch"): 5,
            }
        ),
    ),
    FixtureBundleSpec(
        "broader_range_open_ended_quantified_group_alternation_workflows.py",
        expected_manifest_id="broader-range-open-ended-quantified-group-alternation-workflows",
        expected_patterns=frozenset(
            {
                r"a(bc|de){2,}d",
                r"a(?P<word>bc|de){2,}d",
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
    FixtureBundleSpec(
        "broader_range_open_ended_quantified_group_alternation_conditional_workflows.py",
        expected_manifest_id=(
            "broader-range-open-ended-quantified-group-alternation-conditional-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a((bc|de){2,})?(?(1)d|e)",
                r"a(?P<outer>(bc|de){2,})?(?(outer)d|e)",
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
        "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py",
        expected_manifest_id=(
            "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a((bc|b)c){2,}d",
                r"a(?P<word>(bc|b)c){2,}d",
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
        "nested_open_ended_quantified_group_alternation_workflows.py",
        expected_manifest_id="nested-open-ended-quantified-group-alternation-workflows",
        expected_patterns=frozenset(
            {
                r"a((bc|de){1,})d",
                r"a(?P<outer>(bc|de){1,})d",
                rb"a((bc|de){1,})d",
                rb"a(?P<outer>(bc|de){1,})d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 4,
                ("module_call", "search"): 8,
                ("pattern_call", "fullmatch"): 16,
            }
        ),
        expected_text_models=frozenset({"bytes", "str"}),
    ),
)
FIXTURE_BUNDLES = load_fixture_bundles(FIXTURE_BUNDLE_SPECS)
OPEN_ENDED_ALTERNATION_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "open-ended-quantified-group-alternation-workflows",
)
NESTED_OPEN_ENDED_ALTERNATION_BUNDLE = published_fixture_bundle_by_manifest_id(
    FIXTURE_BUNDLES,
    "nested-open-ended-quantified-group-alternation-workflows",
)
OPEN_ENDED_TRACE_BUNDLES = (
    OPEN_ENDED_ALTERNATION_BUNDLE,
    NESTED_OPEN_ENDED_ALTERNATION_BUNDLE,
)
NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES = (
    SupplementalCase(
        id="nested-open-ended-grouped-alternation-numbered-bytes",
        pattern=rb"a((bc|de){1,})d",
        search_matches=(b"zzabcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcbcded", b"adededed"),
        fullmatch_misses=(b"ae", b"abcbcdede"),
    ),
    SupplementalCase(
        id="nested-open-ended-grouped-alternation-named-bytes",
        pattern=rb"a(?P<outer>(bc|de){1,})d",
        search_matches=(b"zzabcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcbcded", b"adededed"),
        fullmatch_misses=(b"ae", b"abcbcdede"),
    ),
)


COMPILE_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "compile")
MODULE_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "module_call")
PATTERN_CASES = fixture_cases_for_operation(FIXTURE_BUNDLES, "pattern_call")


def _assert_match_group_access_apis_match_cpython(
    observed: object,
    expected: re.Match[str],
) -> None:
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


def _compile_case_prefix(case: FixtureCase) -> str:
    suffix = "-compile-metadata-str"
    assert case.case_id.endswith(suffix)
    return case.case_id.removesuffix(suffix)


def _build_open_ended_trace_cases() -> tuple[OpenEndedTraceCase, ...]:
    cases: list[OpenEndedTraceCase] = []
    for bundle in OPEN_ENDED_TRACE_BUNDLES:
        for case in fixture_cases_for_operation((bundle,), "compile"):
            if case.text_model != "str":
                continue
            pattern = case_pattern(case)
            assert isinstance(pattern, str)
            prefix = _compile_case_prefix(case)
            for repetition_count in range(1, 5):
                for branch_order in product(OPEN_ENDED_BRANCH_TEXT, repeat=repetition_count):
                    body = "".join(OPEN_ENDED_BRANCH_TEXT[branch] for branch in branch_order)
                    branch_id = "-".join(branch_order)
                    fullmatch_text = f"a{body}d"
                    cases.append(
                        OpenEndedTraceCase(
                            id=f"{prefix}-{branch_id}",
                            pattern=pattern,
                            search_text=f"zz{fullmatch_text}zz",
                            fullmatch_text=fullmatch_text,
                        )
                    )
    return tuple(cases)


OPEN_ENDED_TRACE_CASES = _build_open_ended_trace_cases()
EXPECTED_OPEN_ENDED_FULLMATCH_TEXTS = frozenset(
    f"a{''.join(OPEN_ENDED_BRANCH_TEXT[branch] for branch in branch_order)}d"
    for repetition_count in range(1, 5)
    for branch_order in product(OPEN_ENDED_BRANCH_TEXT, repeat=repetition_count)
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


def test_nested_open_ended_alternation_bytes_cases_stay_explicit_with_one_direct_follow_on_anchor(
) -> None:
    bundle_str_cases = tuple(
        case
        for case in NESTED_OPEN_ENDED_ALTERNATION_BUNDLE.cases
        if case.text_model == "str"
    )
    bundle_bytes_cases = tuple(
        case
        for case in NESTED_OPEN_ENDED_ALTERNATION_BUNDLE.cases
        if case.text_model == "bytes"
    )
    expected_compile_patterns = frozenset(
        case_pattern(case)
        for case in fixture_cases_for_operation(
            (NESTED_OPEN_ENDED_ALTERNATION_BUNDLE,),
            "compile",
        )
        if case.text_model == "bytes"
    )

    assert len(NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES) == 2
    assert {case.id for case in NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES} == {
        "nested-open-ended-grouped-alternation-numbered-bytes",
        "nested-open-ended-grouped-alternation-named-bytes",
    }
    assert {case.pattern for case in NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES} == (
        expected_compile_patterns
    )
    assert len(bundle_str_cases) == len(bundle_bytes_cases) == 14
    assert {case.case_id for case in bundle_bytes_cases} == {
        f"{case.case_id.removesuffix('-str')}-bytes" for case in bundle_str_cases
    }
    assert Counter((case.operation, case.helper) for case in bundle_bytes_cases) == Counter(
        {
            ("compile", None): 2,
            ("module_call", "search"): 4,
            ("pattern_call", "fullmatch"): 8,
        }
    )

    for case in NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES:
        assert case.search_misses == ()
        assert len(case.search_matches) == 2
        assert len(case.fullmatch_matches) == 2
        assert len(case.fullmatch_misses) == 2
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

    numbered_case, named_case = NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES
    assert published_module_texts_by_pattern == {
        numbered_case.pattern: {b"zzabcdzz", b"zzadedzz"},
        named_case.pattern: {b"zzabcdzz", b"zzadedzz"},
    }
    assert published_fullmatch_texts_by_pattern == {
        numbered_case.pattern: {b"abcbcded", b"adededed", b"ae", b"abcbcdede"},
        named_case.pattern: {b"abcbcded", b"adededed", b"ae", b"abcbcdede"},
    }


def test_open_ended_trace_cases_cover_all_declared_branch_orders() -> None:
    expected_patterns = frozenset(
        case_pattern(case)
        for bundle in OPEN_ENDED_TRACE_BUNDLES
        for case in fixture_cases_for_operation((bundle,), "compile")
        if case.text_model == "str"
    )

    assert len(EXPECTED_OPEN_ENDED_FULLMATCH_TEXTS) == 30
    assert len(OPEN_ENDED_TRACE_CASES) == (
        len(expected_patterns) * len(EXPECTED_OPEN_ENDED_FULLMATCH_TEXTS)
    )
    assert len({case.id for case in OPEN_ENDED_TRACE_CASES}) == len(
        OPEN_ENDED_TRACE_CASES
    )
    assert {case.pattern for case in OPEN_ENDED_TRACE_CASES} == expected_patterns

    for pattern in expected_patterns:
        matching_cases = tuple(
            case for case in OPEN_ENDED_TRACE_CASES if case.pattern == pattern
        )
        assert len(matching_cases) == len(EXPECTED_OPEN_ENDED_FULLMATCH_TEXTS)
        assert {case.fullmatch_text for case in matching_cases} == (
            EXPECTED_OPEN_ENDED_FULLMATCH_TEXTS
        )
        assert {case.search_text for case in matching_cases} == {
            f"zz{text}zz" for text in EXPECTED_OPEN_ENDED_FULLMATCH_TEXTS
        }


@pytest.mark.parametrize(
    "case",
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend

    compile_with_cpython_parity(backend_name, backend, case.pattern)


@pytest.mark.parametrize(
    "case",
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_module_search_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    backend_name, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        assert_match_parity(backend_name, observed, expected, check_regs=True)

    for text in case.search_misses:
        assert backend.search(case.pattern, text) is None
        assert re.search(case.pattern, text) is None


@pytest.mark.parametrize(
    "case",
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_module_search_convenience_api_matches_cpython(
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
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_module_search_match_group_access_matches_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalCase,
) -> None:
    _, backend = regex_backend

    for text in case.search_matches:
        observed = backend.search(case.pattern, text)
        expected = re.search(case.pattern, text)

        assert observed is not None
        assert expected is not None
        _assert_match_group_access_apis_match_cpython(observed, expected)


@pytest.mark.parametrize(
    "case",
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_pattern_fullmatch_matches_cpython(
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
        assert_match_parity(backend_name, observed, expected, check_regs=True)

    for text in case.fullmatch_misses:
        assert observed_pattern.fullmatch(text) is None
        assert expected_pattern.fullmatch(text) is None


@pytest.mark.parametrize(
    "case",
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_pattern_fullmatch_convenience_api_matches_cpython(
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


@pytest.mark.parametrize(
    "case",
    NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    ids=lambda case: case.id,
)
def test_nested_open_ended_alternation_bytes_pattern_fullmatch_match_group_access_matches_cpython(
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
        _assert_match_group_access_apis_match_cpython(observed, expected)

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


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_search_match_group_access_matches_cpython(
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

    _assert_match_group_access_apis_match_cpython(observed, expected)


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


@pytest.mark.parametrize("case", OPEN_ENDED_TRACE_CASES, ids=lambda case: case.id)
def test_open_ended_module_search_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
) -> None:
    backend_name, backend = regex_backend

    observed = backend.search(case.pattern, case.search_text)
    expected = re.search(case.pattern, case.search_text)

    assert observed is not None
    assert expected is not None
    assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", OPEN_ENDED_TRACE_CASES, ids=lambda case: case.id)
def test_open_ended_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: OpenEndedTraceCase,
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


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_match_group_access_matches_cpython(
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

    _assert_match_group_access_apis_match_cpython(observed, expected)
