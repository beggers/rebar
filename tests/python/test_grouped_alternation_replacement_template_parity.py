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


class RebarGroupedAlternationReplacementTemplateParityTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "grouped-alternation replacement-template parity requires rebar._rebar",
    )
    def test_module_sub_and_subn_match_cpython(self) -> None:
        cases = [
            ("a(b|c)d", r"\1x", "abdacd", 0),
            ("a(b|c)d", r"\1x", "abdacd", 1),
            ("a(?P<word>b|c)d", r"\g<word>x", "abdacd", 0),
            ("a(?P<word>b|c)d", r"\g<word>x", "abdacd", 1),
        ]

        for pattern, repl, string, count in cases:
            with self.subTest(pattern=pattern, repl=repl, string=string, count=count):
                self.assertEqual(
                    rebar.sub(pattern, repl, string, count=count),
                    re.sub(pattern, repl, string, count=count),
                )
                self.assertEqual(
                    rebar.subn(pattern, repl, string, count=count),
                    re.subn(pattern, repl, string, count=count),
                )

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "grouped-alternation replacement-template parity requires rebar._rebar",
    )
    def test_pattern_sub_and_subn_match_cpython(self) -> None:
        cases = [
            ("a(b|c)d", r"\1x", "acdabd", 0),
            ("a(b|c)d", r"\1x", "acdabd", 1),
            ("a(?P<word>b|c)d", r"\g<word>x", "acdabd", 0),
            ("a(?P<word>b|c)d", r"\g<word>x", "acdabd", 1),
        ]

        for pattern, repl, string, count in cases:
            with self.subTest(pattern=pattern, repl=repl, string=string, count=count):
                observed_pattern = rebar.compile(pattern)
                expected_pattern = re.compile(pattern)
                self.assertEqual(
                    observed_pattern.sub(repl, string, count=count),
                    expected_pattern.sub(repl, string, count=count),
                )
                self.assertEqual(
                    observed_pattern.subn(repl, string, count=count),
                    expected_pattern.subn(repl, string, count=count),
                )


if __name__ == "__main__":
    unittest.main()
