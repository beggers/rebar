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


class RebarGroupedLiteralReplacementTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_grouped_literal_template_sub_matches_cpython(self) -> None:
        self.assertTrue(rebar.native_module_loaded(), "grouped literal template parity requires rebar._rebar")

        cases = [
            ("(abc)", r"\1x", "abc", 0),
            ("(abc)", r"\1x", "abcabc", 0),
            ("(abc)", r"\1x", "abcabc", 1),
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

                compiled = rebar.compile(pattern)
                cpython_compiled = re.compile(pattern)
                self.assertEqual(compiled.sub(repl, string, count=count), cpython_compiled.sub(repl, string, count=count))
                self.assertEqual(
                    compiled.subn(repl, string, count=count),
                    cpython_compiled.subn(repl, string, count=count),
                )

    def test_grouped_literal_compile_and_match_expose_capture_metadata(self) -> None:
        self.assertTrue(rebar.native_module_loaded(), "grouped literal template parity requires rebar._rebar")

        compiled = rebar.compile("(abc)")

        self.assertIs(compiled, rebar.compile("(abc)"))
        self.assertEqual(compiled.pattern, "(abc)")
        self.assertEqual(compiled.flags, int(rebar.UNICODE))
        self.assertEqual(compiled.groups, 1)
        self.assertEqual(compiled.groupindex, {})

        match = compiled.search("zzabczz")
        self.assertIs(type(match), rebar.Match)
        self.assertEqual(match.group(0), "abc")
        self.assertEqual(match.group(1), "abc")
        self.assertEqual(match.group(0, 1), ("abc", "abc"))
        self.assertEqual(match.groups(), ("abc",))
        self.assertEqual(match.groupdict(), {})
        self.assertEqual(match.span(), (2, 5))
        self.assertEqual(match.span(1), (2, 5))
        self.assertEqual(match.start(1), 2)
        self.assertEqual(match.end(1), 5)
        self.assertEqual(match.lastindex, 1)
        self.assertIsNone(match.lastgroup)


if __name__ == "__main__":
    unittest.main()
