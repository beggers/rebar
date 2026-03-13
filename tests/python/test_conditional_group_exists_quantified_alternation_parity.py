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


class RebarConditionalGroupExistsQuantifiedAlternationParityTest(unittest.TestCase):
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
        self.assertEqual(observed.group(3), expected.group(3))
        self.assertEqual(observed.groups(), expected.groups())
        self.assertEqual(observed.groupdict(), expected.groupdict())
        self.assertEqual(observed.span(), expected.span())
        self.assertEqual(observed.span(1), expected.span(1))
        self.assertEqual(observed.span(2), expected.span(2))
        self.assertEqual(observed.span(3), expected.span(3))
        self.assertEqual(observed.start(1), expected.start(1))
        self.assertEqual(observed.start(2), expected.start(2))
        self.assertEqual(observed.start(3), expected.start(3))
        self.assertEqual(observed.end(1), expected.end(1))
        self.assertEqual(observed.end(2), expected.end(2))
        self.assertEqual(observed.end(3), expected.end(3))
        self.assertEqual(observed.lastindex, expected.lastindex)
        self.assertEqual(observed.lastgroup, expected.lastgroup)
        for group_name in group_names:
            self.assertEqual(observed.group(group_name), expected.group(group_name))
            self.assertEqual(observed.span(group_name), expected.span(group_name))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_numbered_conditional_group_exists_quantified_alternation_metadata(
        self,
    ) -> None:
        pattern = "a(b)?c(?(1)(de|df)|(eg|eh)){2}"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_present_first_arm_behavior(self) -> None:
        pattern = "a(b)?c(?(1)(de|df)|(eg|eh)){2}"
        observed = rebar.search(pattern, "zzabcdedezz")
        expected = re.search(pattern, "zzabcdedezz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_present_second_arm_behavior(
        self,
    ) -> None:
        pattern = "a(b)?c(?(1)(de|df)|(eg|eh)){2}"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abcdfdf")
        expected = expected_pattern.fullmatch("abcdfdf")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_mixed_yes_arm_behavior(self) -> None:
        pattern = "a(b)?c(?(1)(de|df)|(eg|eh)){2}"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abcdedf")
        expected = expected_pattern.fullmatch("abcdedf")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_absent_first_arm_behavior(self) -> None:
        pattern = "a(b)?c(?(1)(de|df)|(eg|eh)){2}"
        observed = rebar.search(pattern, "zzacegegzz")
        expected = re.search(pattern, "zzacegegzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_absent_second_arm_behavior(
        self,
    ) -> None:
        pattern = "a(b)?c(?(1)(de|df)|(eg|eh)){2}"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("aceheh")
        expected = expected_pattern.fullmatch("aceheh")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_mixed_no_arm_behavior(self) -> None:
        pattern = "a(b)?c(?(1)(de|df)|(eg|eh)){2}"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("acegeh")
        expected = expected_pattern.fullmatch("acegeh")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_named_conditional_group_exists_quantified_alternation_metadata(
        self,
    ) -> None:
        pattern = "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_present_first_arm_behavior(self) -> None:
        pattern = "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}"
        observed = rebar.search(pattern, "zzabcdedezz")
        expected = re.search(pattern, "zzabcdedezz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_present_second_arm_behavior(self) -> None:
        pattern = "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abcdfdf")
        expected = expected_pattern.fullmatch("abcdfdf")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_mixed_yes_arm_behavior(self) -> None:
        pattern = "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abcdedf")
        expected = expected_pattern.fullmatch("abcdedf")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_absent_first_arm_behavior(self) -> None:
        pattern = "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}"
        observed = rebar.search(pattern, "zzacegegzz")
        expected = re.search(pattern, "zzacegegzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_absent_second_arm_behavior(self) -> None:
        pattern = "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("aceheh")
        expected = expected_pattern.fullmatch("aceheh")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists quantified alternation parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_mixed_no_arm_behavior(self) -> None:
        pattern = "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("acegeh")
        expected = expected_pattern.fullmatch("acegeh")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))


if __name__ == "__main__":
    unittest.main()
