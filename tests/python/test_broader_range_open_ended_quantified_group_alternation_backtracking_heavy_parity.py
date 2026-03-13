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


class RebarBroaderRangeOpenEndedQuantifiedGroupAlternationBacktrackingHeavyParityTest(
    unittest.TestCase
):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def _assert_match_parity(
        self,
        observed: rebar.Match,
        expected: re.Match[str],
        *,
        group_names: tuple[str, ...] = (),
    ) -> None:
        self.assertIs(type(observed), rebar.Match)
        self.assertEqual(observed.group(0), expected.group(0))
        self.assertEqual(observed.group(1), expected.group(1))
        self.assertEqual(observed.group(2), expected.group(2))
        self.assertEqual(observed.groups(), expected.groups())
        self.assertEqual(observed.groupdict(), expected.groupdict())
        self.assertEqual(observed.span(), expected.span())
        self.assertEqual(observed.span(1), expected.span(1))
        self.assertEqual(observed.span(2), expected.span(2))
        self.assertEqual(observed.start(1), expected.start(1))
        self.assertEqual(observed.end(1), expected.end(1))
        self.assertEqual(observed.start(2), expected.start(2))
        self.assertEqual(observed.end(2), expected.end(2))
        self.assertEqual(observed.lastindex, expected.lastindex)
        self.assertEqual(observed.lastgroup, expected.lastgroup)
        for group_name in group_names:
            self.assertEqual(observed.group(group_name), expected.group(group_name))
            self.assertEqual(observed.span(group_name), expected.span(group_name))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range open-ended quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_numbered_metadata(self) -> None:
        pattern = "a((bc|b)c){2,}d"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range open-ended quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_lower_bound_paths(self) -> None:
        pattern = "a((bc|b)c){2,}d"

        observed_short = rebar.search(pattern, "zzabcbcdzz")
        expected_short = re.search(pattern, "zzabcbcdzz")
        self.assertIsNotNone(observed_short)
        self.assertIsNotNone(expected_short)
        self._assert_match_parity(observed_short, expected_short)

        observed_long = rebar.search(pattern, "zzabcbccdzz")
        expected_long = re.search(pattern, "zzabcbccdzz")
        self.assertIsNotNone(observed_long)
        self.assertIsNotNone(expected_long)
        self._assert_match_parity(observed_long, expected_long)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range open-ended quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_repetition_and_no_match_paths(
        self,
    ) -> None:
        observed_pattern = rebar.compile("a((bc|b)c){2,}d")
        expected_pattern = re.compile("a((bc|b)c){2,}d")

        observed_mixed = observed_pattern.fullmatch("abccbcd")
        expected_mixed = expected_pattern.fullmatch("abccbcd")
        self.assertIsNotNone(observed_mixed)
        self.assertIsNotNone(expected_mixed)
        self._assert_match_parity(observed_mixed, expected_mixed)

        observed_fourth = observed_pattern.fullmatch("abcbcbcbcd")
        expected_fourth = expected_pattern.fullmatch("abcbcbcbcd")
        self.assertIsNotNone(observed_fourth)
        self.assertIsNotNone(expected_fourth)
        self._assert_match_parity(observed_fourth, expected_fourth)

        self.assertIsNone(observed_pattern.fullmatch("abcd"))
        self.assertIsNone(expected_pattern.fullmatch("abcd"))
        self.assertIsNone(observed_pattern.fullmatch("abccbd"))
        self.assertIsNone(expected_pattern.fullmatch("abccbd"))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range open-ended quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_named_metadata(self) -> None:
        pattern = "a(?P<word>(bc|b)c){2,}d"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range open-ended quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_paths(self) -> None:
        pattern = "a(?P<word>(bc|b)c){2,}d"

        observed_mixed = rebar.search(pattern, "zzabccbcdzz")
        expected_mixed = re.search(pattern, "zzabccbcdzz")
        self.assertIsNotNone(observed_mixed)
        self.assertIsNotNone(expected_mixed)
        self._assert_match_parity(observed_mixed, expected_mixed, group_names=("word",))

        observed_fourth = rebar.search(pattern, "zzabcbcbcbcdzz")
        expected_fourth = re.search(pattern, "zzabcbcbcbcdzz")
        self.assertIsNotNone(observed_fourth)
        self.assertIsNotNone(expected_fourth)
        self._assert_match_parity(observed_fourth, expected_fourth, group_names=("word",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range open-ended quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_repetition_and_no_match_paths(
        self,
    ) -> None:
        observed_pattern = rebar.compile("a(?P<word>(bc|b)c){2,}d")
        expected_pattern = re.compile("a(?P<word>(bc|b)c){2,}d")

        observed_mixed = observed_pattern.fullmatch("abcbccd")
        expected_mixed = expected_pattern.fullmatch("abcbccd")
        self.assertIsNotNone(observed_mixed)
        self.assertIsNotNone(expected_mixed)
        self._assert_match_parity(observed_mixed, expected_mixed, group_names=("word",))

        self.assertIsNone(observed_pattern.fullmatch("abcd"))
        self.assertIsNone(expected_pattern.fullmatch("abcd"))

        self.assertIsNone(observed_pattern.search("zzabccbdzz"))
        self.assertIsNone(expected_pattern.search("zzabccbdzz"))


if __name__ == "__main__":
    unittest.main()
