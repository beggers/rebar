from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import pathlib
import re

import pytest

from rebar_harness.correctness import (
    DEFAULT_FIXTURE_PATHS,
    FixtureCase,
    FixtureManifest,
    load_fixture_manifest,
)
from tests.python.callable_replacement_callback_support import (
    assert_callable_replacement_match_parity,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "conformance" / "fixtures"


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    raw_cases_by_id: dict[str, dict[str, object]]

    @property
    def compile_patterns(self) -> frozenset[str]:
        patterns: set[str] = set()
        for case in self.cases:
            pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
            assert isinstance(pattern, str)
            patterns.add(pattern)
        return frozenset(patterns)


CALLABLE_FIXTURE_PATHS = tuple(
    sorted(
        FIXTURES_DIR.glob("*callable_replacement_workflows.py"),
        key=lambda path: path.name,
    )
)
PUBLISHED_CALLABLE_FIXTURE_PATHS = tuple(
    sorted(
        (
            path
            for path in DEFAULT_FIXTURE_PATHS
            if path.parent == FIXTURES_DIR
            and path.name.endswith("callable_replacement_workflows.py")
        ),
        key=lambda path: path.name,
    )
)
EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "sub"): 2,
        ("module_call", "subn"): 2,
        ("pattern_call", "sub"): 2,
        ("pattern_call", "subn"): 2,
    }
)


def _fixture_bundle(path: pathlib.Path) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(path)
    raw_cases = manifest.raw.get("cases", [])
    assert isinstance(raw_cases, list)
    return FixtureBundle(
        manifest=manifest,
        cases=tuple(cases),
        raw_cases_by_id={
            str(raw_case["id"]): raw_case
            for raw_case in raw_cases
            if isinstance(raw_case, dict) and "id" in raw_case
        },
    )


FIXTURE_BUNDLES = (
    *(_fixture_bundle(path) for path in CALLABLE_FIXTURE_PATHS),
)

COMPILE_PATTERNS = tuple(
    sorted(
        {
            compile_pattern
            for bundle in FIXTURE_BUNDLES
            for compile_pattern in bundle.compile_patterns
        }
    )
)
MODULE_CASES = tuple(
    case
    for bundle in FIXTURE_BUNDLES
    for case in bundle.cases
    if case.operation == "module_call"
)
PATTERN_CASES = tuple(
    case
    for bundle in FIXTURE_BUNDLES
    for case in bundle.cases
    if case.operation == "pattern_call"
)


def _case_pattern(case: FixtureCase) -> str:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, str)
    return pattern


def _case_string(case: FixtureCase) -> str:
    string_index = 2 if case.operation == "module_call" else 1
    string = case.args[string_index]
    assert isinstance(string, str)
    return string


def _case_count(case: FixtureCase) -> int:
    if "count" in case.kwargs:
        return int(case.kwargs["count"])

    count_index = 3 if case.operation == "module_call" else 2
    if len(case.args) > count_index:
        return int(case.args[count_index])
    return 0


def _case_group_names(case: FixtureCase) -> tuple[str, ...]:
    return tuple(re.compile(_case_pattern(case), case.flags or 0).groupindex)


def _raw_callable_replacement(bundle: FixtureBundle, case: FixtureCase) -> dict[str, object]:
    raw_case = bundle.raw_cases_by_id[case.case_id]
    raw_args = raw_case.get("args", [])
    assert isinstance(raw_args, list)
    replacement_index = 1 if case.operation == "module_call" else 0
    replacement = raw_args[replacement_index]
    assert isinstance(replacement, dict)
    return replacement


def _assert_raw_callable_replacement_reference_is_valid(
    bundle: FixtureBundle,
    case: FixtureCase,
) -> None:
    replacement = _raw_callable_replacement(bundle, case)
    assert replacement.get("type") == "callable_match_group"

    prefix = replacement.get("prefix", "")
    suffix = replacement.get("suffix", "")
    assert isinstance(prefix, str)
    assert isinstance(suffix, str)

    compiled = re.compile(_case_pattern(case), case.flags or 0)
    group_reference = replacement.get("group", 0)
    if isinstance(group_reference, int):
        assert 0 <= group_reference <= compiled.groups
    else:
        assert isinstance(group_reference, str)
        assert group_reference in compiled.groupindex


def test_callable_replacement_suite_discovers_all_published_callable_fixtures() -> None:
    assert CALLABLE_FIXTURE_PATHS
    assert CALLABLE_FIXTURE_PATHS == PUBLISHED_CALLABLE_FIXTURE_PATHS


@pytest.mark.parametrize(
    "bundle",
    FIXTURE_BUNDLES,
    ids=lambda bundle: bundle.manifest.manifest_id,
)
def test_callable_replacement_fixture_shape_contract(
    bundle: FixtureBundle,
) -> None:
    assert bundle.manifest.manifest_id.endswith("-callable-replacement-workflows")
    assert bundle.manifest.layer == "module_workflow"
    assert bundle.manifest.defaults.get("text_model") == "str"
    assert len(bundle.cases) == 8
    assert len(bundle.raw_cases_by_id) == len(bundle.cases)
    assert {case.case_id for case in bundle.cases} == set(bundle.raw_cases_by_id)
    assert {case.text_model for case in bundle.cases} == {"str"}
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        EXPECTED_OPERATION_HELPER_COUNTS
    )
    assert len(bundle.compile_patterns) == 2

    has_named_pattern = False
    has_numbered_pattern = False
    for pattern in bundle.compile_patterns:
        compiled = re.compile(pattern)
        if compiled.groupindex:
            has_named_pattern = True
        else:
            has_numbered_pattern = True

    assert has_named_pattern
    assert has_numbered_pattern

    for case in bundle.cases:
        assert "callable-replacement" in case.categories
        assert "str" in case.categories
        _assert_raw_callable_replacement_reference_is_valid(bundle, case)


@pytest.mark.parametrize("pattern", COMPILE_PATTERNS)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    pattern: str,
) -> None:
    _, backend = regex_backend

    observed = backend.compile(pattern)
    expected = re.compile(pattern)

    assert observed is backend.compile(pattern)
    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed_pattern = backend.compile(case.pattern_payload(), case.flags or 0)
    expected_pattern = re.compile(case.pattern_payload(), case.flags or 0)

    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed == expected


@pytest.mark.parametrize("case", MODULE_CASES, ids=lambda case: case.case_id)
def test_module_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=_case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
    )


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
def test_pattern_callable_replacement_callback_match_objects_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    assert_callable_replacement_match_parity(
        backend_name=backend_name,
        backend=backend,
        helper=case.helper,
        pattern=_case_pattern(case),
        string=_case_string(case),
        count=_case_count(case),
        group_names=_case_group_names(case),
        use_compiled_pattern=True,
    )
