from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass
import pathlib
import re

import rebar
from rebar_harness.correctness import (
    CORRECTNESS_FIXTURES_ROOT,
    FixtureCase,
    FixtureManifest,
    load_fixture_manifest,
)


FIXTURES_DIR = CORRECTNESS_FIXTURES_ROOT

_MISSING_GROUP_DEFAULT = object()
_MATCH_ACCESSOR_NAMES = ("group", "span", "start", "end", "getitem")


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_manifest_id: str
    expected_patterns: frozenset[str | bytes]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]
    expected_case_ids: frozenset[str] | None = None
    expected_text_models: frozenset[str] | None = None


def load_fixture_bundle(
    fixture_name: str,
    *,
    expected_manifest_id: str,
    expected_patterns: frozenset[str | bytes],
    expected_operation_helper_counts: Counter[tuple[str, str | None]],
    selected_case_ids: tuple[str, ...] | None = None,
    expected_case_ids: frozenset[str] | None = None,
    expected_text_models: frozenset[str] | None = None,
) -> FixtureBundle:
    manifest, cases = load_fixture_manifest(FIXTURES_DIR / fixture_name)
    loaded_cases = tuple(cases)
    if selected_case_ids is None:
        bundle_cases = loaded_cases
    else:
        case_by_id = {case.case_id: case for case in loaded_cases}
        missing_case_ids = tuple(
            case_id for case_id in selected_case_ids if case_id not in case_by_id
        )
        if missing_case_ids:
            raise ValueError(
                f"{fixture_name} is missing expected fixture rows: {missing_case_ids}"
            )
        bundle_cases = tuple(case_by_id[case_id] for case_id in selected_case_ids)

    return FixtureBundle(
        manifest=manifest,
        cases=bundle_cases,
        expected_manifest_id=expected_manifest_id,
        expected_patterns=expected_patterns,
        expected_operation_helper_counts=expected_operation_helper_counts,
        expected_case_ids=expected_case_ids,
        expected_text_models=(
            frozenset({"str"}) if selected_case_ids is None else expected_text_models
        ),
    )


def assert_fixture_bundle_contract(
    bundle: FixtureBundle,
    *,
    pattern_extractor: Callable[[FixtureCase], str | bytes],
) -> None:
    assert bundle.manifest.manifest_id == bundle.expected_manifest_id
    if bundle.expected_case_ids is None:
        assert len(bundle.cases) == sum(bundle.expected_operation_helper_counts.values())
    else:
        assert len(bundle.cases) == len(bundle.expected_case_ids)
        assert {case.case_id for case in bundle.cases} == bundle.expected_case_ids
    assert {pattern_extractor(case) for case in bundle.cases} == bundle.expected_patterns
    if bundle.expected_text_models is not None:
        assert {case.text_model for case in bundle.cases} == bundle.expected_text_models
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        bundle.expected_operation_helper_counts
    )


def published_fixture_paths_from_bundles(
    bundles: Iterable[FixtureBundle],
) -> tuple[pathlib.Path, ...]:
    return tuple(sorted((bundle.manifest.path for bundle in bundles), key=lambda path: path.name))


def bundle_patterns(
    bundle: FixtureBundle,
    *,
    pattern_extractor: Callable[[FixtureCase], str | bytes],
) -> frozenset[str | bytes]:
    return frozenset(pattern_extractor(case) for case in bundle.cases)


def raw_fixture_cases_by_id(bundle: FixtureBundle) -> dict[str, dict[str, object]]:
    raw_cases = bundle.manifest.raw.get("cases", [])
    if not isinstance(raw_cases, list):
        raise ValueError(
            f"fixture manifest {bundle.manifest.manifest_id!r} raw cases must be a list"
        )
    selected_case_ids = {case.case_id for case in bundle.cases}

    return {
        str(raw_case["id"]): raw_case
        for raw_case in raw_cases
        if (
            isinstance(raw_case, dict)
            and "id" in raw_case
            and str(raw_case["id"]) in selected_case_ids
        )
    }


def case_pattern(case: FixtureCase) -> str | bytes:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, (str, bytes))
    return pattern


def str_case_pattern(case: FixtureCase) -> str:
    pattern = case_pattern(case)
    assert isinstance(pattern, str)
    return pattern


def compile_with_cpython_parity(
    backend_name: str,
    backend: object,
    pattern: str | bytes,
    flags: int = 0,
) -> tuple[object, re.Pattern[str] | re.Pattern[bytes]]:
    observed = backend.compile(pattern, flags)
    expected = re.compile(pattern, flags)

    assert observed is backend.compile(pattern, flags)
    assert_pattern_parity(backend_name, observed, expected)
    return observed, expected


def assert_pattern_parity(
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


def assert_match_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
    *,
    check_regs: bool = False,
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
    assert observed.groups(_MISSING_GROUP_DEFAULT) == expected.groups(
        _MISSING_GROUP_DEFAULT
    )
    assert observed.groupdict() == expected.groupdict()
    assert observed.groupdict(_MISSING_GROUP_DEFAULT) == expected.groupdict(
        _MISSING_GROUP_DEFAULT
    )
    assert observed.string == expected.string
    assert observed.pos == expected.pos
    assert observed.endpos == expected.endpos
    assert observed.span() == expected.span()
    assert observed.start() == expected.start()
    assert observed.end() == expected.end()
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup
    if check_regs:
        assert hasattr(observed, "regs") == hasattr(expected, "regs")
        if hasattr(expected, "regs"):
            assert tuple(observed.regs) == tuple(expected.regs)
    assert_pattern_parity(backend_name, observed.re, expected.re)

    for group_name in expected.re.groupindex:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)
        assert observed.start(group_name) == expected.start(group_name)
        assert observed.end(group_name) == expected.end(group_name)


def assert_match_result_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes] | None,
    *,
    check_regs: bool = False,
) -> None:
    if expected is None:
        assert observed is None
        return

    assert observed is not None
    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=check_regs,
    )


def assert_finditer_parity(
    backend_name: str,
    observed_iter: object,
    expected_iter: object,
    *,
    check_regs: bool = False,
) -> None:
    observed_matches = list(observed_iter)
    expected_matches = list(expected_iter)

    assert len(observed_matches) == len(expected_matches)
    for observed, expected in zip(observed_matches, expected_matches):
        assert_match_result_parity(
            backend_name,
            observed,
            expected,
            check_regs=check_regs,
        )

    assert next(observed_iter, None) is None
    assert next(expected_iter, None) is None


def assert_match_convenience_api_parity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    group_names = tuple(expected.re.groupindex)

    for group_index in range(expected.re.groups + 1):
        assert observed[group_index] == expected[group_index]

    for group_name in group_names:
        assert observed[group_name] == expected[group_name]

    for template in _match_api_templates(
        expected.re.pattern,
        group_count=expected.re.groups,
        group_names=group_names,
    ):
        assert observed.expand(template) == expected.expand(template)


def assert_valid_match_group_access_parity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    for reference in _valid_match_group_references(expected):
        for accessor_name in _MATCH_ACCESSOR_NAMES:
            assert _apply_match_accessor(observed, accessor_name, reference) == (
                _apply_match_accessor(expected, accessor_name, reference)
            )


def assert_invalid_match_group_access_parity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    for reference in _invalid_match_group_references(expected):
        for accessor_name in _MATCH_ACCESSOR_NAMES:
            expected_error = _capture_match_accessor_error(expected, accessor_name, reference)
            observed_error = _capture_match_accessor_error(observed, accessor_name, reference)

            assert type(observed_error) is type(expected_error)
            assert observed_error.args == expected_error.args


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
    if len(group_names) >= 2:
        templates.append(
            "<" + "|".join(fr"\g<{group_name}>" for group_name in group_names) + ">"
        )
    for group_name in group_names:
        templates.append(fr"<\g<{group_name}>>")

    if isinstance(pattern, bytes):
        return tuple(template.encode("ascii") for template in templates)
    return tuple(templates)


def _valid_match_group_references(
    expected: re.Match[str] | re.Match[bytes],
) -> tuple[object, ...]:
    references: list[object] = list(range(expected.re.groups + 1))
    # CPython accepts bools here because they are int subclasses.
    references.append(False)
    if expected.re.groups >= 1:
        references.append(True)
    references.extend(expected.re.groupindex)
    return tuple(references)


def _invalid_match_group_references(
    expected: re.Match[str] | re.Match[bytes],
) -> tuple[object, ...]:
    missing_name = "missing"
    while missing_name in expected.re.groupindex:
        missing_name += "_group"
    return (-1, expected.re.groups + 1, None, (1,), 1.0, b"missing", missing_name)


def _apply_match_accessor(
    match: object,
    accessor_name: str,
    reference: object,
) -> object:
    if accessor_name == "group":
        return match.group(reference)
    if accessor_name == "span":
        return match.span(reference)
    if accessor_name == "start":
        return match.start(reference)
    if accessor_name == "end":
        return match.end(reference)
    if accessor_name == "getitem":
        return match[reference]
    raise AssertionError(f"unknown accessor {accessor_name!r}")


def _capture_match_accessor_error(
    match: object,
    accessor_name: str,
    reference: object,
) -> BaseException:
    try:
        _apply_match_accessor(match, accessor_name, reference)
    except BaseException as error:  # noqa: BLE001 - parity helper compares exception details.
        return error
    raise AssertionError(
        f"expected {accessor_name}({reference!r}) to raise for {match.re.pattern!r}"
    )
