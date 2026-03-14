from __future__ import annotations

from dataclasses import dataclass
import re
import unittest

import rebar


@dataclass(frozen=True)
class ReplacementCase:
    id: str
    pattern: str
    helper: str
    repl: str
    string: str
    count: int


CASES = (
    ReplacementCase(
        id="module-numbered-lower-bound-sub",
        pattern=r"a((bc)+)d",
        helper="sub",
        repl=r"\1x",
        string="zzabcdzz",
        count=0,
    ),
    ReplacementCase(
        id="module-numbered-first-match-only-subn",
        pattern=r"a((bc)+)d",
        helper="subn",
        repl=r"\2x",
        string="zzabcbcdabcbcdzz",
        count=1,
    ),
    ReplacementCase(
        id="pattern-numbered-repeated-outer-sub",
        pattern=r"a((bc)+)d",
        helper="sub",
        repl=r"\1x",
        string="zzabcbcdzz",
        count=0,
    ),
    ReplacementCase(
        id="pattern-numbered-first-match-only-subn",
        pattern=r"a((bc)+)d",
        helper="subn",
        repl=r"\2x",
        string="zzabcbcdabcbcdzz",
        count=1,
    ),
    ReplacementCase(
        id="module-named-lower-bound-sub",
        pattern=r"a(?P<outer>(?P<inner>bc)+)d",
        helper="sub",
        repl=r"\g<outer>x",
        string="zzabcdzz",
        count=0,
    ),
    ReplacementCase(
        id="module-named-first-match-only-subn",
        pattern=r"a(?P<outer>(?P<inner>bc)+)d",
        helper="subn",
        repl=r"\g<inner>x",
        string="zzabcbcdabcbcdzz",
        count=1,
    ),
    ReplacementCase(
        id="pattern-named-repeated-outer-sub",
        pattern=r"a(?P<outer>(?P<inner>bc)+)d",
        helper="sub",
        repl=r"\g<outer>x",
        string="zzabcbcdzz",
        count=0,
    ),
    ReplacementCase(
        id="pattern-named-first-match-only-subn",
        pattern=r"a(?P<outer>(?P<inner>bc)+)d",
        helper="subn",
        repl=r"\g<inner>x",
        string="zzabcbcdabcbcdzz",
        count=1,
    ),
)


class RebarQuantifiedNestedGroupReplacementTemplateParityTest(unittest.TestCase):
    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified nested-group replacement-template parity requires rebar._rebar",
    )
    def test_compile_metadata_matches_cpython(self) -> None:
        for pattern in sorted({case.pattern for case in CASES}):
            with self.subTest(pattern=pattern):
                observed = rebar.compile(pattern)
                expected = re.compile(pattern)

                self.assertEqual(observed.pattern, expected.pattern)
                self.assertEqual(observed.flags, expected.flags)
                self.assertEqual(observed.groups, expected.groups)
                self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified nested-group replacement-template parity requires rebar._rebar",
    )
    def test_module_replacement_matches_cpython(self) -> None:
        for case in CASES:
            with self.subTest(case=case.id):
                observed = getattr(rebar, case.helper)(
                    case.pattern,
                    case.repl,
                    case.string,
                    count=case.count,
                )
                expected = getattr(re, case.helper)(
                    case.pattern,
                    case.repl,
                    case.string,
                    count=case.count,
                )

                self.assertEqual(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified nested-group replacement-template parity requires rebar._rebar",
    )
    def test_pattern_replacement_matches_cpython(self) -> None:
        for case in CASES:
            with self.subTest(case=case.id):
                observed_pattern = rebar.compile(case.pattern)
                expected_pattern = re.compile(case.pattern)

                observed = getattr(observed_pattern, case.helper)(
                    case.repl,
                    case.string,
                    count=case.count,
                )
                expected = getattr(expected_pattern, case.helper)(
                    case.repl,
                    case.string,
                    count=case.count,
                )

                self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
