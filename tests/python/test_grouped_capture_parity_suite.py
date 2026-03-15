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
    assert_invalid_match_group_access_parity,
    assert_match_convenience_api_parity,
    assert_match_parity,
    assert_valid_match_group_access_parity,
    compile_with_cpython_parity,
    select_published_fixture_paths,
    str_case_pattern,
)


EXPECTED_PUBLISHED_FIXTURE_NAMES = (
    "grouped_alternation_workflows.py",
    "grouped_match_workflows.py",
    "grouped_segment_workflows.py",
    "named_group_workflows.py",
    "optional_group_alternation_workflows.py",
    "optional_group_workflows.py",
    "nested_group_workflows.py",
)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    sorted(
        (FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES),
        key=lambda path: path.name,
    )
)
PUBLISHED_GROUPED_CAPTURE_FIXTURE_PATHS = select_published_fixture_paths(
    EXPECTED_PUBLISHED_FIXTURE_PATHS
)


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_case_ids: frozenset[str]
    expected_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]


@dataclass(frozen=True)
class CompileCase:
    id: str
    pattern: str
    flags: int = 0


@dataclass(frozen=True)
class SupplementalMissCase:
    id: str
    module_case_id: str
    module_misses: tuple[str, ...]
    pattern_case_id: str
    pattern_misses: tuple[str, ...]


def _fixture_bundle(
    fixture_name: str,
    *,
    selected_case_ids: tuple[str, ...],
    expected_manifest_id: str,
    expected_patterns: frozenset[str],
    expected_operation_helper_counts: Counter[tuple[str, str | None]],
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    case_by_id = {case.case_id: case for case in cases}
    missing_case_ids = tuple(case_id for case_id in selected_case_ids if case_id not in case_by_id)
    if missing_case_ids:
        raise ValueError(
            f"{fixture_name} is missing expected grouped-capture fixture rows: {missing_case_ids}"
        )

    return FixtureBundle(
        manifest=manifest,
        cases=tuple(case_by_id[case_id] for case_id in selected_case_ids),
        expected_manifest_id=expected_manifest_id,
        expected_case_ids=frozenset(selected_case_ids),
        expected_patterns=expected_patterns,
        expected_operation_helper_counts=expected_operation_helper_counts,
    )


FIXTURE_BUNDLES = (
    _fixture_bundle(
        "grouped_match_workflows.py",
        selected_case_ids=(
            "grouped-module-fullmatch-two-capture-gap-str",
            "grouped-pattern-fullmatch-two-capture-gap-str",
        ),
        expected_manifest_id="grouped-match-workflows",
        expected_patterns=frozenset({r"(ab)(c)"}),
        expected_operation_helper_counts=Counter(
            {
                ("module_call", "fullmatch"): 1,
                ("pattern_call", "fullmatch"): 1,
            }
        ),
    ),
    _fixture_bundle(
        "named_group_workflows.py",
        selected_case_ids=(
            "named-group-compile-metadata-str",
            "named-group-module-search-metadata-str",
            "named-group-pattern-search-metadata-str",
        ),
        expected_manifest_id="named-group-workflows",
        expected_patterns=frozenset({r"(?P<word>abc)"}),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 1,
                ("module_call", "search"): 1,
                ("pattern_call", "search"): 1,
            }
        ),
    ),
    _fixture_bundle(
        "grouped_segment_workflows.py",
        selected_case_ids=(
            "grouped-segment-compile-metadata-str",
            "grouped-segment-module-search-str",
            "grouped-segment-pattern-fullmatch-str",
            "named-grouped-segment-compile-metadata-str",
            "named-grouped-segment-module-search-str",
            "named-grouped-segment-pattern-fullmatch-str",
        ),
        expected_manifest_id="grouped-segment-workflows",
        expected_patterns=frozenset(
            {
                r"a(b)c",
                r"a(?P<word>b)c",
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
        "grouped_alternation_workflows.py",
        selected_case_ids=(
            "grouped-alternation-compile-metadata-str",
            "grouped-alternation-module-search-str",
            "grouped-alternation-pattern-fullmatch-str",
            "named-grouped-alternation-compile-metadata-str",
            "named-grouped-alternation-module-search-str",
            "named-grouped-alternation-pattern-fullmatch-str",
        ),
        expected_manifest_id="grouped-alternation-workflows",
        expected_patterns=frozenset(
            {
                r"a(b|c)d",
                r"a(?P<word>b|c)d",
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
        "optional_group_workflows.py",
        selected_case_ids=(
            "optional-group-compile-metadata-str",
            "optional-group-module-search-present-str",
            "optional-group-pattern-fullmatch-absent-str",
            "named-optional-group-compile-metadata-str",
            "named-optional-group-module-search-absent-str",
            "named-optional-group-pattern-fullmatch-present-str",
            "systematic-optional-group-numbered-compile-metadata-str",
            "systematic-optional-group-numbered-module-search-present-str",
            "systematic-optional-group-numbered-module-search-absent-str",
            "systematic-optional-group-numbered-pattern-fullmatch-present-str",
            "systematic-optional-group-numbered-pattern-fullmatch-absent-str",
            "systematic-optional-group-named-compile-metadata-str",
            "systematic-optional-group-named-module-search-present-str",
            "systematic-optional-group-named-module-search-absent-str",
            "systematic-optional-group-named-pattern-fullmatch-present-str",
            "systematic-optional-group-named-pattern-fullmatch-absent-str",
        ),
        expected_manifest_id="optional-group-workflows",
        expected_patterns=frozenset(
            {
                r"a(b)?d",
                r"a(?P<word>b)?d",
            }
        ),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 4,
                ("module_call", "search"): 6,
                ("pattern_call", "fullmatch"): 6,
            }
        ),
    ),
    _fixture_bundle(
        "optional_group_alternation_workflows.py",
        selected_case_ids=(
            "optional-group-alternation-compile-metadata-str",
            "optional-group-alternation-module-search-present-str",
            "optional-group-alternation-pattern-fullmatch-absent-str",
            "named-optional-group-alternation-compile-metadata-str",
            "named-optional-group-alternation-module-search-present-str",
            "named-optional-group-alternation-pattern-fullmatch-absent-str",
        ),
        expected_manifest_id="optional-group-alternation-workflows",
        expected_patterns=frozenset(
            {
                r"a(b|c)?d",
                r"a(?P<word>b|c)?d",
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
        "nested_group_workflows.py",
        selected_case_ids=(
            "nested-group-compile-metadata-str",
            "nested-group-module-search-str",
            "nested-group-pattern-fullmatch-str",
            "named-nested-group-compile-metadata-str",
            "named-nested-group-module-search-str",
            "named-nested-group-pattern-fullmatch-str",
        ),
        expected_manifest_id="nested-group-workflows",
        expected_patterns=frozenset(
            {
                r"a((b))d",
                r"a(?P<outer>(?P<inner>b))d",
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
)


def _compile_cases(cases: tuple[FixtureCase, ...]) -> tuple[CompileCase, ...]:
    grouped_cases: dict[tuple[str, int], list[FixtureCase]] = {}
    for case in cases:
        key = (str_case_pattern(case), case.flags or 0)
        grouped_cases.setdefault(key, []).append(case)

    compile_cases: list[CompileCase] = []
    for (pattern, flags), cases_for_pattern in grouped_cases.items():
        source_case = next((case for case in cases_for_pattern if case.operation == "compile"), None)
        if source_case is None:
            source_case = cases_for_pattern[0]
            case_id = f"{source_case.case_id}-compile-metadata"
        else:
            case_id = source_case.case_id
        compile_cases.append(CompileCase(id=case_id, pattern=pattern, flags=flags))
    return tuple(compile_cases)


PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
COMPILE_CASES = _compile_cases(PUBLISHED_CASES)
MODULE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "module_call")
PATTERN_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "pattern_call")
CASES_BY_ID = {case.case_id: case for case in PUBLISHED_CASES}
SUPPLEMENTAL_MISS_CASES = (
    SupplementalMissCase(
        id="numbered-two-capture-fullmatch",
        module_case_id="grouped-module-fullmatch-two-capture-gap-str",
        module_misses=("ab", "abcz"),
        pattern_case_id="grouped-pattern-fullmatch-two-capture-gap-str",
        pattern_misses=("ab", "abcz"),
    ),
    SupplementalMissCase(
        id="numbered-grouped-segment-search-and-fullmatch",
        module_case_id="grouped-segment-module-search-str",
        module_misses=("zzz",),
        pattern_case_id="grouped-segment-pattern-fullmatch-str",
        pattern_misses=("abcz",),
    ),
    SupplementalMissCase(
        id="named-grouped-segment-search-and-fullmatch",
        module_case_id="named-grouped-segment-module-search-str",
        module_misses=("zzz",),
        pattern_case_id="named-grouped-segment-pattern-fullmatch-str",
        pattern_misses=("abcz",),
    ),
    SupplementalMissCase(
        id="numbered-grouped-alternation-search-and-fullmatch",
        module_case_id="grouped-alternation-module-search-str",
        module_misses=("zzz",),
        pattern_case_id="grouped-alternation-pattern-fullmatch-str",
        pattern_misses=("abdd",),
    ),
    SupplementalMissCase(
        id="named-grouped-alternation-search-and-fullmatch",
        module_case_id="named-grouped-alternation-module-search-str",
        module_misses=("zzz",),
        pattern_case_id="named-grouped-alternation-pattern-fullmatch-str",
        pattern_misses=("acdd",),
    ),
    SupplementalMissCase(
        id="named-single-capture-search",
        module_case_id="named-group-module-search-metadata-str",
        module_misses=("zzz",),
        pattern_case_id="named-group-pattern-search-metadata-str",
        pattern_misses=("zzz",),
    ),
    SupplementalMissCase(
        id="numbered-optional-group-search-and-fullmatch",
        module_case_id="optional-group-module-search-present-str",
        module_misses=("zzz",),
        pattern_case_id="optional-group-pattern-fullmatch-absent-str",
        pattern_misses=("abdd",),
    ),
    SupplementalMissCase(
        id="named-optional-group-search-and-fullmatch",
        module_case_id="named-optional-group-module-search-absent-str",
        module_misses=("zzz",),
        pattern_case_id="named-optional-group-pattern-fullmatch-present-str",
        pattern_misses=("abdd",),
    ),
    SupplementalMissCase(
        id="numbered-optional-group-alternation-search-and-fullmatch",
        module_case_id="optional-group-alternation-module-search-present-str",
        module_misses=("zzaedzz",),
        pattern_case_id="optional-group-alternation-pattern-fullmatch-absent-str",
        pattern_misses=("ae",),
    ),
    SupplementalMissCase(
        id="named-optional-group-alternation-search-and-fullmatch",
        module_case_id="named-optional-group-alternation-module-search-present-str",
        module_misses=("zzaedzz",),
        pattern_case_id="named-optional-group-alternation-pattern-fullmatch-absent-str",
        pattern_misses=("ae",),
    ),
    SupplementalMissCase(
        id="numbered-nested-group-search-and-fullmatch",
        module_case_id="nested-group-module-search-str",
        module_misses=("zzz",),
        pattern_case_id="nested-group-pattern-fullmatch-str",
        pattern_misses=("abdd",),
    ),
    SupplementalMissCase(
        id="named-nested-group-search-and-fullmatch",
        module_case_id="named-nested-group-module-search-str",
        module_misses=("zzz",),
        pattern_case_id="named-nested-group-pattern-fullmatch-str",
        pattern_misses=("abdd",),
    ),
)
MATCH_GROUP_ACCESS_CASE_IDS = (
    "grouped-module-search-single-capture-str",
    "grouped-pattern-search-single-capture-str",
    "grouped-segment-module-search-str",
    "grouped-segment-pattern-fullmatch-str",
    "grouped-alternation-module-search-str",
    "grouped-alternation-pattern-fullmatch-str",
    "named-group-module-search-metadata-str",
    "named-group-pattern-search-metadata-str",
    "named-grouped-segment-module-search-str",
    "named-grouped-segment-pattern-fullmatch-str",
    "named-grouped-alternation-module-search-str",
    "named-grouped-alternation-pattern-fullmatch-str",
    "systematic-optional-group-numbered-module-search-absent-str",
    "systematic-optional-group-numbered-pattern-fullmatch-absent-str",
    "systematic-optional-group-named-module-search-absent-str",
    "systematic-optional-group-named-pattern-fullmatch-absent-str",
    "optional-group-alternation-module-search-present-str",
    "optional-group-alternation-pattern-fullmatch-absent-str",
    "named-optional-group-alternation-module-search-present-str",
    "named-optional-group-alternation-pattern-fullmatch-absent-str",
    "nested-group-module-search-str",
    "nested-group-pattern-fullmatch-str",
    "named-nested-group-module-search-str",
    "named-nested-group-pattern-fullmatch-str",
)
REGS_PARITY_CASE_IDS = frozenset(
    {
        "optional-group-alternation-module-search-present-str",
        "optional-group-alternation-pattern-fullmatch-absent-str",
        "named-optional-group-alternation-module-search-present-str",
        "named-optional-group-alternation-pattern-fullmatch-absent-str",
    }
)


def _load_match_group_access_cases() -> tuple[FixtureCase, ...]:
    expected_case_ids = frozenset(MATCH_GROUP_ACCESS_CASE_IDS)
    case_by_id: dict[str, FixtureCase] = {}

    for path in PUBLISHED_GROUPED_CAPTURE_FIXTURE_PATHS:
        _, cases = load_fixture_manifest(path)
        for case in cases:
            if case.case_id in expected_case_ids:
                case_by_id.setdefault(case.case_id, case)

    missing_case_ids = tuple(
        case_id for case_id in MATCH_GROUP_ACCESS_CASE_IDS if case_id not in case_by_id
    )
    if missing_case_ids:
        raise ValueError(
            "grouped-capture match-group-access coverage is missing expected fixture rows: "
            f"{missing_case_ids}"
        )

    return tuple(case_by_id[case_id] for case_id in MATCH_GROUP_ACCESS_CASE_IDS)


MATCH_GROUP_ACCESS_CASES = _load_match_group_access_cases()


def _module_call_with_text(regex_api: object, case: FixtureCase, text: str) -> object:
    assert case.operation == "module_call"
    assert case.helper is not None

    return getattr(regex_api, case.helper)(
        str_case_pattern(case),
        text,
        *case.args[2:],
        **case.kwargs,
    )


def _pattern_call_with_text(compiled_pattern: object, case: FixtureCase, text: str) -> object:
    assert case.operation == "pattern_call"
    assert case.helper is not None

    return getattr(compiled_pattern, case.helper)(text, *case.args[1:], **case.kwargs)


def _match_for_case(
    backend_name: str,
    backend: object,
    case: FixtureCase,
) -> tuple[object, re.Match[str]]:
    assert case.helper is not None

    if case.operation == "module_call":
        observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
        expected = getattr(re, case.helper)(*case.args, **case.kwargs)
    else:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            case.pattern_payload(),
            case.flags or 0,
        )
        observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
        expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    return observed, expected


def test_grouped_capture_parity_suite_uses_expected_published_fixture_paths() -> None:
    assert PUBLISHED_GROUPED_CAPTURE_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS
    assert len({case.case_id for case in PUBLISHED_CASES}) == len(PUBLISHED_CASES)


def test_match_group_access_rows_remain_on_grouped_capture_fixture_paths() -> None:
    assert tuple(case.case_id for case in MATCH_GROUP_ACCESS_CASES) == MATCH_GROUP_ACCESS_CASE_IDS
    assert {case.text_model for case in MATCH_GROUP_ACCESS_CASES} == {"str"}


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
    assert {case.text_model for case in bundle.cases} == {"str"}
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        bundle.expected_operation_helper_counts
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: CompileCase,
) -> None:
    backend_name, backend = regex_backend

    compile_with_cpython_parity(backend_name, backend, case.pattern, case.flags)


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_helper_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=case.case_id in REGS_PARITY_CASE_IDS,
    )


@pytest.mark.parametrize("case", SUPPLEMENTAL_MISS_CASES, ids=lambda case: case.id)
def test_module_helper_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalMissCase,
) -> None:
    _, backend = regex_backend
    module_case = CASES_BY_ID[case.module_case_id]

    for text in case.module_misses:
        assert _module_call_with_text(backend, module_case, text) is None
        assert _module_call_with_text(re, module_case, text) is None


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_helper_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern_payload(),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=case.case_id in REGS_PARITY_CASE_IDS,
    )


@pytest.mark.parametrize("case", MATCH_GROUP_ACCESS_CASES, ids=lambda case: case.case_id)
def test_match_group_accessors_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _match_for_case(backend_name, backend, case)

    assert_match_parity(backend_name, observed, expected)
    assert_valid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", MATCH_GROUP_ACCESS_CASES, ids=lambda case: case.case_id)
def test_invalid_match_group_access_errors_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed, expected = _match_for_case(backend_name, backend, case)

    assert_match_parity(backend_name, observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_helper_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_helper_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern_payload(),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", SUPPLEMENTAL_MISS_CASES, ids=lambda case: case.id)
def test_pattern_helper_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalMissCase,
) -> None:
    backend_name, backend = regex_backend
    pattern_case = CASES_BY_ID[case.pattern_case_id]
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern_case.pattern_payload(),
        pattern_case.flags or 0,
    )

    for text in case.pattern_misses:
        assert _pattern_call_with_text(observed_pattern, pattern_case, text) is None
        assert _pattern_call_with_text(expected_pattern, pattern_case, text) is None
