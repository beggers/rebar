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


class RebarLiteralAlternationParityTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def _assert_match_parity(self, observed: rebar.Match, expected: re.Match[str]) -> None:
        self.assertIs(type(observed), rebar.Match)
        self.assertEqual(observed.group(0), expected.group(0))
        self.assertEqual(observed.groups(), expected.groups())
        self.assertEqual(observed.groupdict(), expected.groupdict())
        self.assertEqual(observed.span(), expected.span())
        self.assertEqual(observed.start(), expected.start())
        self.assertEqual(observed.end(), expected.end())
        self.assertEqual(observed.lastindex, expected.lastindex)
        self.assertEqual(observed.lastgroup, expected.lastgroup)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "literal-alternation parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_literal_alternation_metadata(self) -> None:
        observed = rebar.compile("ab|ac")
        expected = re.compile("ab|ac")

        self.assertIs(observed, rebar.compile("ab|ac"))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "literal-alternation parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_literal_alternation_behavior(self) -> None:
        observed = rebar.search("ab|ac", "zzaczz")
        expected = re.search("ab|ac", "zzaczz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "literal-alternation parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_literal_alternation_behavior(self) -> None:
        observed_pattern = rebar.compile("ab|ac")
        expected_pattern = re.compile("ab|ac")

        observed = observed_pattern.fullmatch("ac")
        expected = expected_pattern.fullmatch("ac")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)


if __name__ == "__main__":
    unittest.main()
