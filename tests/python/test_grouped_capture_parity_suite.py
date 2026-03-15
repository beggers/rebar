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
EXPECTED_PUBLISHED_FIXTURE_NAMES = (
    "grouped_match_workflows.py",
    "named_group_workflows.py",
    "optional_group_workflows.py",
    "nested_group_workflows.py",
)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    sorted(
        (FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES),
        key=lambda path: path.name,
    )
)
PUBLISHED_GROUPED_CAPTURE_FIXTURE_PATHS = tuple(
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
        "optional_group_workflows.py",
        selected_case_ids=(
            "optional-group-compile-metadata-str",
            "optional-group-module-search-present-str",
            "optional-group-pattern-fullmatch-absent-str",
            "named-optional-group-compile-metadata-str",
            "named-optional-group-module-search-absent-str",
            "named-optional-group-pattern-fullmatch-present-str",
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


def _case_pattern(case: FixtureCase) -> str:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, str)
    return pattern


def _compile_cases(cases: tuple[FixtureCase, ...]) -> tuple[CompileCase, ...]:
    grouped_cases: dict[tuple[str, int], list[FixtureCase]] = {}
    for case in cases:
        key = (_case_pattern(case), case.flags or 0)
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


def _module_call_with_text(regex_api: object, case: FixtureCase, text: str) -> object:
    assert case.operation == "module_call"
    assert case.helper is not None

    return getattr(regex_api, case.helper)(
        _case_pattern(case),
        text,
        *case.args[2:],
        **case.kwargs,
    )


def _pattern_call_with_text(compiled_pattern: object, case: FixtureCase, text: str) -> object:
    assert case.operation == "pattern_call"
    assert case.helper is not None

    return getattr(compiled_pattern, case.helper)(text, *case.args[1:], **case.kwargs)


def _match_api_templates(
    *,
    group_count: int,
    group_names: tuple[str, ...],
) -> tuple[str, ...]:
    templates = [r"<\g<0>>"]
    if group_count >= 1:
        templates.append(r"<\1>")
    if group_count >= 2:
        templates.append(r"<\2:\1>")
    for group_name in group_names:
        templates.append(fr"<\g<{group_name}>>")
    return tuple(templates)


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
    group_names = tuple(expected.re.groupindex)

    assert observed.group(0) == expected.group(0)
    assert observed.group(*group_indexes) == expected.group(*group_indexes)
    for group_index in range(1, expected.re.groups + 1):
        assert observed.group(group_index) == expected.group(group_index)
        assert observed.span(group_index) == expected.span(group_index)
        assert observed.start(group_index) == expected.start(group_index)
        assert observed.end(group_index) == expected.end(group_index)

    assert observed.groups() == expected.groups()
    assert observed.groupdict() == expected.groupdict()
    assert observed.span() == expected.span()
    assert observed.start() == expected.start()
    assert observed.end() == expected.end()
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup
    _assert_pattern_parity(backend_name, observed.re, expected.re)

    for group_name in group_names:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)
        assert observed.start(group_name) == expected.start(group_name)
        assert observed.end(group_name) == expected.end(group_name)


def _assert_match_convenience_api_parity(
    observed: object,
    expected: re.Match[str],
) -> None:
    group_names = tuple(expected.re.groupindex)

    for group_index in range(expected.re.groups + 1):
        assert observed[group_index] == expected[group_index]

    for group_name in group_names:
        assert observed[group_name] == expected[group_name]

    for template in _match_api_templates(
        group_count=expected.re.groups,
        group_names=group_names,
    ):
        assert observed.expand(template) == expected.expand(template)


def test_grouped_capture_parity_suite_uses_expected_published_fixture_paths() -> None:
    assert PUBLISHED_GROUPED_CAPTURE_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS
    assert len({case.case_id for case in PUBLISHED_CASES}) == len(PUBLISHED_CASES)


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
    assert {_case_pattern(case) for case in bundle.cases} == bundle.expected_patterns
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

    _compile_with_cpython_parity(backend_name, backend, case.pattern, case.flags)


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
    _assert_match_parity(backend_name, observed, expected)


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

    observed_pattern, expected_pattern = _compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern_payload(),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    _assert_match_parity(backend_name, observed, expected)


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
    _assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_helper_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed_pattern, expected_pattern = _compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern_payload(),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    _assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", SUPPLEMENTAL_MISS_CASES, ids=lambda case: case.id)
def test_pattern_helper_misses_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalMissCase,
) -> None:
    backend_name, backend = regex_backend
    pattern_case = CASES_BY_ID[case.pattern_case_id]
    observed_pattern, expected_pattern = _compile_with_cpython_parity(
        backend_name,
        backend,
        pattern_case.pattern_payload(),
        pattern_case.flags or 0,
    )

    for text in case.pattern_misses:
        assert _pattern_call_with_text(observed_pattern, pattern_case, text) is None
        assert _pattern_call_with_text(expected_pattern, pattern_case, text) is None
