from __future__ import annotations

from dataclasses import dataclass
import re

import pytest


CaptureRef = int | str


@dataclass(frozen=True)
class ProbeSpec:
    id: str
    string: str
    count: int
    callback_kind: str
    helpers: tuple[str, ...] = ("sub", "subn")


@dataclass(frozen=True)
class Scenario:
    id: str
    pattern: str
    outer_ref: CaptureRef
    inner_ref: CaptureRef
    probes: tuple[ProbeSpec, ...]


@dataclass(frozen=True)
class ReplacementCase:
    id: str
    pattern: str
    outer_ref: CaptureRef
    inner_ref: CaptureRef
    helper: str
    string: str
    count: int
    callback_kind: str


SCENARIOS = (
    Scenario(
        id="quantified-nested-group-callable-replacement-numbered",
        pattern=r"a((bc)+)d",
        outer_ref=1,
        inner_ref=2,
        probes=(
            ProbeSpec(
                id="single-repeat-all-matches",
                string="zzabcdzz",
                count=0,
                callback_kind="capture_summary",
            ),
            ProbeSpec(
                id="double-repeat-all-matches",
                string="zzabcbcdabcbcdzz",
                count=0,
                callback_kind="capture_summary",
            ),
            ProbeSpec(
                id="double-repeat-first-match-only",
                string="zzabcbcdabcbcdzz",
                count=1,
                callback_kind="span_summary",
            ),
        ),
    ),
    Scenario(
        id="quantified-nested-group-callable-replacement-named",
        pattern=r"a(?P<outer>(?P<inner>bc)+)d",
        outer_ref="outer",
        inner_ref="inner",
        probes=(
            ProbeSpec(
                id="single-repeat-all-matches",
                string="zzabcdzz",
                count=0,
                callback_kind="capture_summary",
            ),
            ProbeSpec(
                id="double-repeat-all-matches",
                string="zzabcbcdabcbcdzz",
                count=0,
                callback_kind="capture_summary",
            ),
            ProbeSpec(
                id="double-repeat-first-match-only",
                string="zzabcbcdabcbcdzz",
                count=1,
                callback_kind="span_summary",
            ),
        ),
    ),
)


def _build_cases() -> tuple[ReplacementCase, ...]:
    cases: list[ReplacementCase] = []
    for scenario in SCENARIOS:
        for probe in scenario.probes:
            for helper in probe.helpers:
                cases.append(
                    ReplacementCase(
                        id=f"{scenario.id}-{probe.id}-{helper}",
                        pattern=scenario.pattern,
                        outer_ref=scenario.outer_ref,
                        inner_ref=scenario.inner_ref,
                        helper=helper,
                        string=probe.string,
                        count=probe.count,
                        callback_kind=probe.callback_kind,
                    )
                )
    return tuple(cases)


CASES = _build_cases()


def _named_group_summary(
    match: re.Match[str],
    *,
    outer_ref: CaptureRef,
    inner_ref: CaptureRef,
) -> str:
    if not isinstance(outer_ref, str) or not isinstance(inner_ref, str):
        return ""
    return (
        f"|outer={match.groupdict()[outer_ref]}"
        f"|inner={match.groupdict()[inner_ref]}"
        f"|outer-index={match.re.groupindex[outer_ref]}"
        f"|inner-index={match.re.groupindex[inner_ref]}"
    )


def _build_replacement(case: ReplacementCase):
    if case.callback_kind == "capture_summary":

        def _replacement(match: re.Match[str]) -> str:
            return (
                f"<{match.group(0)}|{match.group(case.outer_ref)}|{match.group(case.inner_ref)}"
                f"{_named_group_summary(match, outer_ref=case.outer_ref, inner_ref=case.inner_ref)}"
                f"|{match.lastindex}:{match.re.groups}>"
            )

        return _replacement

    if case.callback_kind == "span_summary":

        def _replacement(match: re.Match[str]) -> str:
            return (
                f"[{match.start()}:{match.end()}|"
                f"{match.start(case.outer_ref)}:{match.end(case.outer_ref)}|"
                f"{match.start(case.inner_ref)}:{match.end(case.inner_ref)}]"
            )

        return _replacement

    raise AssertionError(f"unknown callback kind: {case.callback_kind}")


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda scenario: scenario.id)
def test_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    scenario: Scenario,
) -> None:
    _, backend = regex_backend

    observed = backend.compile(scenario.pattern)
    expected = re.compile(scenario.pattern)

    assert observed is backend.compile(scenario.pattern)
    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_module_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: ReplacementCase,
) -> None:
    _, backend = regex_backend

    observed = getattr(backend, case.helper)(
        case.pattern,
        _build_replacement(case),
        case.string,
        count=case.count,
    )
    expected = getattr(re, case.helper)(
        case.pattern,
        _build_replacement(case),
        case.string,
        count=case.count,
    )

    assert observed == expected


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_pattern_callable_replacement_matches_cpython(
    regex_backend: tuple[str, object],
    case: ReplacementCase,
) -> None:
    _, backend = regex_backend

    observed_pattern = backend.compile(case.pattern)
    expected_pattern = re.compile(case.pattern)

    observed = getattr(observed_pattern, case.helper)(
        _build_replacement(case),
        case.string,
        count=case.count,
    )
    expected = getattr(expected_pattern, case.helper)(
        _build_replacement(case),
        case.string,
        count=case.count,
    )

    assert observed == expected
