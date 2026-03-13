from __future__ import annotations

import pathlib
import re
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar


class RebarConditionalGroupExistsNestedReplacementParityTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists nested replacement parity requires rebar._rebar",
    )
    def test_module_sub_and_subn_match_cpython(self) -> None:
        cases = [
            ("sub", "a(b)?c(?(1)(?(1)d|e)|f)", "X", "zzabcdzz", 0),
            ("subn", "a(b)?c(?(1)(?(1)d|e)|f)", "X", "zzacfzz", 1),
            ("sub", "a(?P<word>b)?c(?(word)(?(word)d|e)|f)", "X", "zzabcdzz", 0),
            ("subn", "a(?P<word>b)?c(?(word)(?(word)d|e)|f)", "X", "zzacfzz", 1),
        ]

        for helper, pattern, repl, string, count in cases:
            with self.subTest(
                helper=helper,
                pattern=pattern,
                repl=repl,
                string=string,
                count=count,
            ):
                observed = getattr(rebar, helper)(pattern, repl, string, count=count)
                expected = getattr(re, helper)(pattern, repl, string, count=count)
                self.assertEqual(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists nested replacement parity requires rebar._rebar",
    )
    def test_pattern_sub_and_subn_match_cpython(self) -> None:
        cases = [
            ("sub", "a(b)?c(?(1)(?(1)d|e)|f)", "X", "zzabcdzz", 0),
            ("subn", "a(b)?c(?(1)(?(1)d|e)|f)", "X", "zzacfzz", 1),
            ("sub", "a(?P<word>b)?c(?(word)(?(word)d|e)|f)", "X", "zzabcdzz", 0),
            ("subn", "a(?P<word>b)?c(?(word)(?(word)d|e)|f)", "X", "zzacfzz", 1),
        ]

        for helper, pattern, repl, string, count in cases:
            with self.subTest(
                helper=helper,
                pattern=pattern,
                repl=repl,
                string=string,
                count=count,
            ):
                observed_pattern = rebar.compile(pattern)
                expected_pattern = re.compile(pattern)
                observed = getattr(observed_pattern, helper)(repl, string, count=count)
                expected = getattr(expected_pattern, helper)(repl, string, count=count)
                self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
