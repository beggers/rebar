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


class RebarGroupedLiteralCaptureParityTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def _assert_match_parity(self, observed: rebar.Match, expected: re.Match[str]) -> None:
        self.assertIs(type(observed), rebar.Match)
        self.assertEqual(observed.group(0), expected.group(0))
        self.assertEqual(observed.group(1), expected.group(1))
        self.assertEqual(observed.group(2), expected.group(2))
        self.assertEqual(observed.group(0, 1, 2), expected.group(0, 1, 2))
        self.assertEqual(observed.groups(), expected.groups())
        self.assertEqual(observed.groupdict(), expected.groupdict())
        self.assertEqual(observed.span(), expected.span())
        self.assertEqual(observed.span(1), expected.span(1))
        self.assertEqual(observed.span(2), expected.span(2))
        self.assertEqual(observed.start(1), expected.start(1))
        self.assertEqual(observed.end(2), expected.end(2))
        self.assertEqual(observed.lastindex, expected.lastindex)
        self.assertEqual(observed.lastgroup, expected.lastgroup)

    @unittest.skipUnless(rebar.native_module_loaded(), "grouped numbered-capture parity requires rebar._rebar")
    def test_module_fullmatch_matches_cpython_for_two_captures(self) -> None:
        observed = rebar.fullmatch("(ab)(c)", "abc")
        expected = re.fullmatch("(ab)(c)", "abc")

        self.assertEqual(rebar.compile("(ab)(c)").groups, 2)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(rebar.native_module_loaded(), "grouped numbered-capture parity requires rebar._rebar")
    def test_compiled_pattern_fullmatch_matches_cpython_for_two_captures(self) -> None:
        compiled = rebar.compile("(ab)(c)")
        expected_compiled = re.compile("(ab)(c)")

        self.assertIs(compiled, rebar.compile("(ab)(c)"))
        self.assertEqual(compiled.pattern, "(ab)(c)")
        self.assertEqual(compiled.flags, expected_compiled.flags)
        self.assertEqual(compiled.groups, expected_compiled.groups)
        self.assertEqual(compiled.groupindex, expected_compiled.groupindex)

        observed = compiled.fullmatch("abc")
        expected = expected_compiled.fullmatch("abc")
        self._assert_match_parity(observed, expected)


if __name__ == "__main__":
    unittest.main()
