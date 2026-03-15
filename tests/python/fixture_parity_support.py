from __future__ import annotations

import pathlib
import re

import rebar
from rebar_harness.correctness import DEFAULT_FIXTURE_PATHS, FixtureCase


FIXTURES_DIR = pathlib.Path(__file__).resolve().parents[1] / "conformance" / "fixtures"

_MISSING_GROUP_DEFAULT = object()


def select_published_fixture_paths(
    expected_paths: tuple[pathlib.Path, ...],
) -> tuple[pathlib.Path, ...]:
    expected_path_set = frozenset(expected_paths)
    return tuple(
        sorted(
            (path for path in DEFAULT_FIXTURE_PATHS if path in expected_path_set),
            key=lambda path: path.name,
        )
    )


def case_pattern(case: FixtureCase) -> str | bytes:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, (str, bytes))
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
    assert_pattern_parity(backend_name, observed.re, expected.re)

    for group_name in expected.re.groupindex:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)
        assert observed.start(group_name) == expected.start(group_name)
        assert observed.end(group_name) == expected.end(group_name)


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
