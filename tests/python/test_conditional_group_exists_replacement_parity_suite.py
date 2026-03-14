from __future__ import annotations

from dataclasses import dataclass
import re

import pytest
import rebar


REPLACEMENT = "X"
pytestmark = pytest.mark.skipif(
    not rebar.native_module_loaded(),
    reason="conditional group-exists replacement parity requires rebar._rebar",
)


@dataclass(frozen=True)
class ProbeSpec:
    id: str
    string: str
    count: int
    helpers: tuple[str, ...] = ("sub", "subn")


@dataclass(frozen=True)
class Scenario:
    id: str
    numbered_pattern: str
    named_pattern: str
    probes: tuple[ProbeSpec, ...]


@dataclass(frozen=True)
class ReplacementCase:
    id: str
    pattern: str
    helper: str
    string: str
    count: int


SCENARIOS = (
    Scenario(
        id="conditional-group-exists-replacement",
        numbered_pattern=r"a(b)?c(?(1)d|e)",
        named_pattern=r"a(?P<word>b)?c(?(word)d|e)",
        probes=(
            ProbeSpec(id="present", string="zzabcdzz", count=0),
            ProbeSpec(id="absent", string="zzacezz", count=1),
        ),
    ),
    Scenario(
        id="conditional-group-exists-no-else-replacement",
        numbered_pattern=r"a(b)?c(?(1)d)",
        named_pattern=r"a(?P<word>b)?c(?(word)d)",
        probes=(
            ProbeSpec(id="present", string="zzabcdzz", count=0),
            ProbeSpec(id="absent", string="zzaczz", count=1),
        ),
    ),
    Scenario(
        id="conditional-group-exists-empty-else-replacement",
        numbered_pattern=r"a(b)?c(?(1)d|)",
        named_pattern=r"a(?P<word>b)?c(?(word)d|)",
        probes=(
            ProbeSpec(id="present", string="zzabcdzz", count=0),
            ProbeSpec(id="absent", string="zzaczz", count=1),
        ),
    ),
    Scenario(
        id="conditional-group-exists-empty-yes-else-replacement",
        numbered_pattern=r"a(b)?c(?(1)|e)",
        named_pattern=r"a(?P<word>b)?c(?(word)|e)",
        probes=(
            ProbeSpec(id="present", string="zzabczz", count=0),
            ProbeSpec(id="absent", string="zzacezz", count=1),
        ),
    ),
    Scenario(
        id="conditional-group-exists-fully-empty-replacement",
        numbered_pattern=r"a(b)?c(?(1)|)",
        named_pattern=r"a(?P<word>b)?c(?(word)|)",
        probes=(
            ProbeSpec(id="present", string="zzabczz", count=0),
            ProbeSpec(id="absent", string="zzaczz", count=1),
        ),
    ),
    Scenario(
        id="conditional-group-exists-alternation-replacement",
        numbered_pattern=r"a(b)?c(?(1)(de|df)|(eg|eh))",
        named_pattern=r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
        probes=(
            ProbeSpec(id="yes-arm-first", string="zzabcdezz", count=0, helpers=("sub",)),
            ProbeSpec(id="yes-arm-second", string="zzabcdfzz", count=1, helpers=("subn",)),
            ProbeSpec(id="no-arm-first", string="zzacegzz", count=0, helpers=("sub",)),
            ProbeSpec(id="no-arm-second", string="zzacehzz", count=1, helpers=("subn",)),
        ),
    ),
    Scenario(
        id="conditional-group-exists-nested-replacement",
        numbered_pattern=r"a(b)?c(?(1)(?(1)d|e)|f)",
        named_pattern=r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
        probes=(
            ProbeSpec(id="present", string="zzabcdzz", count=0, helpers=("sub",)),
            ProbeSpec(id="absent", string="zzacfzz", count=1, helpers=("subn",)),
        ),
    ),
    Scenario(
        id="conditional-group-exists-quantified-replacement",
        numbered_pattern=r"a(b)?c(?(1)d|e){2}",
        named_pattern=r"a(?P<word>b)?c(?(word)d|e){2}",
        probes=(
            ProbeSpec(id="present", string="zzabcddzz", count=0, helpers=("sub",)),
            ProbeSpec(id="absent", string="zzaceezz", count=1, helpers=("subn",)),
        ),
    ),
)


def _build_cases() -> tuple[ReplacementCase, ...]:
    return tuple(
        ReplacementCase(
            id=f"{scenario.id}-{variant}-{probe.id}-{helper}",
            pattern=pattern,
            helper=helper,
            string=probe.string,
            count=probe.count,
        )
        for scenario in SCENARIOS
        for variant, pattern in (
            ("numbered", scenario.numbered_pattern),
            ("named", scenario.named_pattern),
        )
        for probe in scenario.probes
        for helper in probe.helpers
    )


CASES = _build_cases()


def _replacement_result(
    backend: object,
    case: ReplacementCase,
    *,
    compiled_pattern: bool,
) -> object:
    if compiled_pattern:
        compiled = backend.compile(case.pattern)
        return getattr(compiled, case.helper)(
            REPLACEMENT,
            case.string,
            count=case.count,
        )

    return getattr(backend, case.helper)(
        case.pattern,
        REPLACEMENT,
        case.string,
        count=case.count,
    )


@pytest.mark.parametrize("compiled_pattern", (False, True), ids=("module", "pattern"))
@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_replacement_matches_cpython(
    case: ReplacementCase,
    compiled_pattern: bool,
) -> None:
    observed = _replacement_result(
        rebar,
        case,
        compiled_pattern=compiled_pattern,
    )
    expected = _replacement_result(
        re,
        case,
        compiled_pattern=compiled_pattern,
    )
    assert observed == expected
