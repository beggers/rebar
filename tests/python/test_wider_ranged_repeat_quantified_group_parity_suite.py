from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product
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
    "wider_ranged_repeat_quantified_group_workflows.py",
    "wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
    "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
    "broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py",
    "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
    "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
    "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py",
    "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
    "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py",
)
EXPECTED_PUBLISHED_FIXTURE_PATHS = tuple(
    sorted(
        (FIXTURES_DIR / fixture_name for fixture_name in EXPECTED_PUBLISHED_FIXTURE_NAMES),
        key=lambda path: path.name,
    )
)
PUBLISHED_WIDER_RANGED_REPEAT_FIXTURE_PATHS = tuple(
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
BROADER_RANGE_BYTES_SKIP_REASON = (
    "rebar does not yet support broader-range wider-ranged-repeat "
    "grouped-conditional bytes parity"
)
BACKTRACKING_BRANCH_TEXT = {
    "short": "bc",
    "long": "bcc",
}


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_patterns: frozenset[str]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]


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
    _fixture_bundle(
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
    _fixture_bundle(
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
    _fixture_bundle(
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
    _fixture_bundle(
        "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py",
        expected_manifest_id=(
            "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows"
        ),
        expected_patterns=frozenset(
            {
                r"a((bc|de){1,4})?(?(1)d|e)",
                r"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
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
    _fixture_bundle(
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
    _fixture_bundle(
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
    _fixture_bundle(
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
PUBLISHED_CASES = tuple(case for bundle in FIXTURE_BUNDLES for case in bundle.cases)
COMPILE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "compile")
MODULE_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "module_call")
PATTERN_CASES = tuple(case for case in PUBLISHED_CASES if case.operation == "pattern_call")
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


def _case_pattern(case: FixtureCase) -> str | bytes:
    if case.pattern is not None:
        return case.pattern_payload()
    return case.args[0]


def _assert_pattern_parity(
    backend_name: str,
    observed: object,
    expected: re.Pattern[str] | re.Pattern[bytes],
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Pattern
    else:
        assert type(observed) is type(expected)

    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


def _compile_with_cpython_parity(
    backend_name: str,
    backend: object,
    pattern: str | bytes,
    flags: int = 0,
) -> tuple[object, re.Pattern[str] | re.Pattern[bytes]]:
    observed = backend.compile(pattern, flags)
    expected = re.compile(pattern, flags)
    assert observed is backend.compile(pattern, flags)
    _assert_pattern_parity(backend_name, observed, expected)
    return observed, expected


def _match_api_templates(
    pattern: str | bytes,
    *,
    group_count: int,
    group_names: tuple[str, ...],
) -> tuple[str | bytes, ...]:
    templates = [r"<\g<0>>"]
    if group_count >= 1:
        templates.append(
            "<" + "|".join(f"\\{group_index}" for group_index in range(1, group_count + 1)) + ">"
        )
        templates.append(
            "<"
            + "|".join(f"\\g<{group_index}>" for group_index in range(group_count + 1))
            + ">"
        )
    for group_name in group_names:
        templates.append(fr"<\g<{group_name}>>")

    if isinstance(pattern, bytes):
        return tuple(template.encode("ascii") for template in templates)
    return tuple(templates)


def _assert_match_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Match
    else:
        assert type(observed) is type(expected)

    group_indexes = tuple(range(expected.re.groups + 1))

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

    for group_name in expected.re.groupindex:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)
        assert observed.start(group_name) == expected.start(group_name)
        assert observed.end(group_name) == expected.end(group_name)


def _assert_match_convenience_api_parity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    for group_index in range(expected.re.groups + 1):
        assert observed[group_index] == expected[group_index]

    group_names = tuple(expected.re.groupindex)
    for group_name in group_names:
        assert observed[group_name] == expected[group_name]

    for template in _match_api_templates(
        expected.re.pattern,
        group_count=expected.re.groups,
        group_names=group_names,
    ):
        assert observed.expand(template) == expected.expand(template)


def test_parity_suite_uses_expected_published_fixture_paths() -> None:
    assert PUBLISHED_WIDER_RANGED_REPEAT_FIXTURE_PATHS == EXPECTED_PUBLISHED_FIXTURE_PATHS
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

    _compile_with_cpython_parity(backend_name, backend, case.pattern)


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
        _assert_match_parity(backend_name, observed, expected)

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
        _assert_match_convenience_api_parity(observed, expected)


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
    observed_pattern, expected_pattern = _compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    for text in case.fullmatch_matches:
        observed = observed_pattern.fullmatch(text)
        expected = expected_pattern.fullmatch(text)

        assert observed is not None
        assert expected is not None
        _assert_match_parity(backend_name, observed, expected)

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
    observed_pattern, expected_pattern = _compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    for text in case.fullmatch_matches:
        observed = observed_pattern.fullmatch(text)
        expected = expected_pattern.fullmatch(text)

        assert observed is not None
        assert expected is not None
        _assert_match_convenience_api_parity(observed, expected)


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
    _assert_match_parity(backend_name, observed, expected)


@pytest.mark.parametrize("case", BACKTRACKING_TRACE_CASES, ids=lambda case: case.id)
def test_backtracking_pattern_fullmatch_branch_traces_match_cpython(
    regex_backend: tuple[str, object],
    case: BacktrackingTraceCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = _compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    observed = observed_pattern.fullmatch(case.fullmatch_text)
    expected = expected_pattern.fullmatch(case.fullmatch_text)

    assert observed is not None
    assert expected is not None
    _assert_match_parity(backend_name, observed, expected)
