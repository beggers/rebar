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
    "open_ended_quantified_group_alternation_workflows.py",
    "open_ended_quantified_group_alternation_conditional_workflows.py",
    "open_ended_quantified_group_alternation_backtracking_heavy_workflows.py",
    "broader_range_open_ended_quantified_group_alternation_workflows.py",
    "broader_range_open_ended_quantified_group_alternation_conditional_workflows.py",
    "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py",
    "nested_open_ended_quantified_group_alternation_workflows.py",
)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    sorted(
        (FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES),
        key=lambda path: path.name,
    )
)
PUBLISHED_OPEN_ENDED_FIXTURE_PATHS = tuple(
    sorted(
        (
            path
            for path in DEFAULT_FIXTURE_PATHS
            if path in EXPECTED_PUBLISHED_FIXTURE_PATHS
        ),
        key=lambda path: path.name,
    )
)
MISSING_GROUP_DEFAULT = object()


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]


def _fixture_bundle(
    fixture_name: str,
    *,
    expected_manifest_id: str,
    expected_patterns: frozenset[str],
    expected_operation_helper_counts: Counter[tuple[str, str | None]],
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    return FixtureBundle(
        manifest=manifest,
        cases=tuple(cases),
        expected_manifest_id=expected_manifest_id,
        expected_patterns=expected_patterns,
        expected_operation_helper_counts=expected_operation_helper_counts,
    )


FIXTURE_BUNDLES = (
    _fixture_bundle(
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
    _fixture_bundle(
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
    _fixture_bundle(
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
    _fixture_bundle(
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
    _fixture_bundle(
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
    _fixture_bundle(
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
    _fixture_bundle(
        "nested_open_ended_quantified_group_alternation_workflows.py",
        expected_manifest_id="nested-open-ended-quantified-group-alternation-workflows",
        expected_patterns=frozenset(
            {
                r"a((bc|de){1,})d",
                r"a(?P<outer>(bc|de){1,})d",
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
)
PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
COMPILE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "compile")
MODULE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "module_call")
PATTERN_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "pattern_call")


def _case_pattern(case: FixtureCase) -> str:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, str)
    return pattern


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


def _match_api_templates(
    *,
    group_count: int,
    group_names: tuple[str, ...],
) -> tuple[str, ...]:
    templates = [r"<\g<0>>"]
    if group_count >= 1:
        templates.append(
            "<"
            + "|".join(
                f"\\{group_index}" for group_index in range(1, group_count + 1)
            )
            + ">"
        )
        templates.append(
            "<"
            + "|".join(f"\\g<{group_index}>" for group_index in range(group_count + 1))
            + ">"
        )
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
    assert observed.groups(MISSING_GROUP_DEFAULT) == expected.groups(MISSING_GROUP_DEFAULT)
    assert observed.groupdict() == expected.groupdict()
    assert observed.groupdict(MISSING_GROUP_DEFAULT) == expected.groupdict(
        MISSING_GROUP_DEFAULT
    )
    assert observed.string == expected.string
    assert observed.pos == expected.pos
    assert observed.endpos == expected.endpos
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


def test_open_ended_quantified_group_suite_uses_expected_published_fixture_paths() -> None:
    assert PUBLISHED_OPEN_ENDED_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS
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
    assert len(bundle.cases) == sum(bundle.expected_operation_helper_counts.values())
    assert {_case_pattern(case) for case in bundle.cases} == bundle.expected_patterns
    assert {case.text_model for case in bundle.cases} == {"str"}
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        bundle.expected_operation_helper_counts
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    pattern = case.pattern_payload()
    assert isinstance(pattern, str)

    _compile_with_cpython_parity(backend_name, backend, pattern, case.flags or 0)


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

    _assert_match_parity(backend_name, observed, expected)


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

    _assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "fullmatch"

    observed_pattern, expected_pattern = _compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern_payload(),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    _assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_fullmatch_match_convenience_api_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "fullmatch"

    observed_pattern, expected_pattern = _compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern_payload(),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    _assert_match_convenience_api_parity(observed, expected)
