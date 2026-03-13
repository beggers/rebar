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


class RebarOpenEndedQuantifiedGroupAlternationConditionalParityTest(unittest.TestCase):
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
        "open-ended quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_numbered_metadata(self) -> None:
        pattern = "a((bc|de){1,})?(?(1)d|e)"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "open-ended quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_absent_behavior(self) -> None:
        pattern = "a((bc|de){1,})?(?(1)d|e)"
        observed = rebar.search(pattern, "zzaezz")
        expected = re.search(pattern, "zzaezz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "open-ended quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_lower_bound_branches(self) -> None:
        pattern = "a((bc|de){1,})?(?(1)d|e)"

        observed_bc = rebar.search(pattern, "zzabcdzz")
        expected_bc = re.search(pattern, "zzabcdzz")
        self.assertIsNotNone(observed_bc)
        self.assertIsNotNone(expected_bc)
        self._assert_match_parity(observed_bc, expected_bc)

        observed_de = rebar.search(pattern, "zzadedzz")
        expected_de = re.search(pattern, "zzadedzz")
        self.assertIsNotNone(observed_de)
        self.assertIsNotNone(expected_de)
        self._assert_match_parity(observed_de, expected_de)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "open-ended quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_repetition_and_no_match_paths(
        self,
    ) -> None:
        observed_pattern = rebar.compile("a((bc|de){1,})?(?(1)d|e)")
        expected_pattern = re.compile("a((bc|de){1,})?(?(1)d|e)")

        observed_second = observed_pattern.fullmatch("abcded")
        expected_second = expected_pattern.fullmatch("abcded")
        self.assertIsNotNone(observed_second)
        self.assertIsNotNone(expected_second)
        self._assert_match_parity(observed_second, expected_second)

        observed_third = observed_pattern.fullmatch("abcbcded")
        expected_third = expected_pattern.fullmatch("abcbcded")
        self.assertIsNotNone(observed_third)
        self.assertIsNotNone(expected_third)
        self._assert_match_parity(observed_third, expected_third)

        self.assertIsNone(observed_pattern.fullmatch("abcde"))
        self.assertIsNone(expected_pattern.fullmatch("abcde"))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "open-ended quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_named_metadata(self) -> None:
        pattern = "a(?P<outer>(bc|de){1,})?(?(outer)d|e)"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "open-ended quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_absent_behavior(self) -> None:
        pattern = "a(?P<outer>(bc|de){1,})?(?(outer)d|e)"
        observed = rebar.search(pattern, "zzaezz")
        expected = re.search(pattern, "zzaezz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "open-ended quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_present_behavior(self) -> None:
        pattern = "a(?P<outer>(bc|de){1,})?(?(outer)d|e)"

        observed_de = rebar.search(pattern, "zzadedzz")
        expected_de = re.search(pattern, "zzadedzz")
        self.assertIsNotNone(observed_de)
        self.assertIsNotNone(expected_de)
        self._assert_match_parity(observed_de, expected_de, group_names=("outer",))

        observed_fourth = rebar.search(pattern, "zzadedededzz")
        expected_fourth = re.search(pattern, "zzadedededzz")
        self.assertIsNotNone(observed_fourth)
        self.assertIsNotNone(expected_fourth)
        self._assert_match_parity(observed_fourth, expected_fourth, group_names=("outer",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "open-ended quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_repetition_and_no_match_paths(
        self,
    ) -> None:
        observed_pattern = rebar.compile("a(?P<outer>(bc|de){1,})?(?(outer)d|e)")
        expected_pattern = re.compile("a(?P<outer>(bc|de){1,})?(?(outer)d|e)")

        observed_third = observed_pattern.fullmatch("abcbcded")
        expected_third = expected_pattern.fullmatch("abcbcded")
        self.assertIsNotNone(observed_third)
        self.assertIsNotNone(expected_third)
        self._assert_match_parity(observed_third, expected_third, group_names=("outer",))

        self.assertIsNone(observed_pattern.fullmatch("ad"))
        self.assertIsNone(expected_pattern.fullmatch("ad"))


if __name__ == "__main__":
    unittest.main()
