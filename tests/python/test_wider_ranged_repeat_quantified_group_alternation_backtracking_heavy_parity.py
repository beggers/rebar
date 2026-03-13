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


class RebarWiderRangedRepeatQuantifiedGroupAlternationBacktrackingHeavyParityTest(
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
        "wider ranged-repeat quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_numbered_metadata(self) -> None:
        pattern = "a((bc|b)c){1,3}d"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "wider ranged-repeat quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_lower_bound_short_branch(self) -> None:
        pattern = "a((bc|b)c){1,3}d"
        observed = rebar.search(pattern, "zzabcdzz")
        expected = re.search(pattern, "zzabcdzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "wider ranged-repeat quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_lower_bound_long_branch(self) -> None:
        pattern = "a((bc|b)c){1,3}d"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abccd")
        expected = expected_pattern.fullmatch("abccd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "wider ranged-repeat quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_second_repetition_short_then_short(
        self,
    ) -> None:
        pattern = "a((bc|b)c){1,3}d"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abcbcd")
        expected = expected_pattern.fullmatch("abcbcd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "wider ranged-repeat quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_second_repetition_short_then_long(
        self,
    ) -> None:
        pattern = "a((bc|b)c){1,3}d"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abcbccd")
        expected = expected_pattern.fullmatch("abcbccd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "wider ranged-repeat quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_no_match(self) -> None:
        observed_pattern = rebar.compile("a((bc|b)c){1,3}d")
        expected_pattern = re.compile("a((bc|b)c){1,3}d")

        self.assertIsNone(observed_pattern.fullmatch("abcccd"))
        self.assertIsNone(expected_pattern.fullmatch("abcccd"))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "wider ranged-repeat quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_named_metadata(self) -> None:
        pattern = "a(?P<word>(bc|b)c){1,3}d"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "wider ranged-repeat quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_lower_bound_long_branch(self) -> None:
        pattern = "a(?P<word>(bc|b)c){1,3}d"
        observed = rebar.search(pattern, "zzabccdzz")
        expected = re.search(pattern, "zzabccdzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "wider ranged-repeat quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_third_repetition_mixed(self) -> None:
        pattern = "a(?P<word>(bc|b)c){1,3}d"
        observed = rebar.search(pattern, "zzabcbccbccdzz")
        expected = re.search(pattern, "zzabcbccbccdzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "wider ranged-repeat quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_second_repetition_long_then_short(
        self,
    ) -> None:
        pattern = "a(?P<word>(bc|b)c){1,3}d"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abccbcd")
        expected = expected_pattern.fullmatch("abccbcd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "wider ranged-repeat quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_third_repetition_short_short_long(
        self,
    ) -> None:
        pattern = "a(?P<word>(bc|b)c){1,3}d"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abcbcbccd")
        expected = expected_pattern.fullmatch("abcbcbccd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "wider ranged-repeat quantified-group alternation backtracking-heavy parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_no_match(self) -> None:
        pattern = "a(?P<word>(bc|b)c){1,3}d"
        observed = rebar.search(pattern, "zzabcccezz")
        expected = re.search(pattern, "zzabcccezz")

        self.assertIsNone(observed)
        self.assertIsNone(expected)


if __name__ == "__main__":
    unittest.main()
