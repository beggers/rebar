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


class RebarWiderRangedRepeatQuantifiedGroupAlternationConditionalBroaderRangeParityTest(
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
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_numbered_metadata(self) -> None:
        pattern = "a((bc|de){1,4})?(?(1)d|e)"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_absent_behavior(self) -> None:
        pattern = "a((bc|de){1,4})?(?(1)d|e)"
        observed = rebar.search(pattern, "zzaezz")
        expected = re.search(pattern, "zzaezz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_lower_bound_bc_behavior(self) -> None:
        pattern = "a((bc|de){1,4})?(?(1)d|e)"
        observed = rebar.search(pattern, "zzabcdzz")
        expected = re.search(pattern, "zzabcdzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_lower_bound_de_behavior(self) -> None:
        pattern = "a((bc|de){1,4})?(?(1)d|e)"
        observed = rebar.search(pattern, "zzadedzz")
        expected = re.search(pattern, "zzadedzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_third_repetition_mixed_behavior(
        self,
    ) -> None:
        pattern = "a((bc|de){1,4})?(?(1)d|e)"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abcbcded")
        expected = expected_pattern.fullmatch("abcbcded")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_no_match_missing_trailing_d_behavior(
        self,
    ) -> None:
        observed_pattern = rebar.compile("a((bc|de){1,4})?(?(1)d|e)")
        expected_pattern = re.compile("a((bc|de){1,4})?(?(1)d|e)")

        self.assertIsNone(observed_pattern.fullmatch("abcdede"))
        self.assertIsNone(expected_pattern.fullmatch("abcdede"))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_no_match_short_behavior(self) -> None:
        observed_pattern = rebar.compile("a((bc|de){1,4})?(?(1)d|e)")
        expected_pattern = re.compile("a((bc|de){1,4})?(?(1)d|e)")

        self.assertIsNone(observed_pattern.fullmatch("ad"))
        self.assertIsNone(expected_pattern.fullmatch("ad"))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_named_metadata(self) -> None:
        pattern = "a(?P<outer>(bc|de){1,4})?(?(outer)d|e)"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_absent_behavior(self) -> None:
        pattern = "a(?P<outer>(bc|de){1,4})?(?(outer)d|e)"
        observed = rebar.search(pattern, "zzaezz")
        expected = re.search(pattern, "zzaezz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_lower_bound_de_behavior(self) -> None:
        pattern = "a(?P<outer>(bc|de){1,4})?(?(outer)d|e)"
        observed = rebar.search(pattern, "zzadedzz")
        expected = re.search(pattern, "zzadedzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_upper_bound_mixed_behavior(self) -> None:
        pattern = "a(?P<outer>(bc|de){1,4})?(?(outer)d|e)"
        observed = rebar.search(pattern, "zzabcdedededzz")
        expected = re.search(pattern, "zzabcdedededzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_third_repetition_mixed_behavior(
        self,
    ) -> None:
        pattern = "a(?P<outer>(bc|de){1,4})?(?(outer)d|e)"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abcbcded")
        expected = expected_pattern.fullmatch("abcbcded")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_no_match_short_behavior(self) -> None:
        observed_pattern = rebar.compile("a(?P<outer>(bc|de){1,4})?(?(outer)d|e)")
        expected_pattern = re.compile("a(?P<outer>(bc|de){1,4})?(?(outer)d|e)")

        self.assertIsNone(observed_pattern.fullmatch("ad"))
        self.assertIsNone(expected_pattern.fullmatch("ad"))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "broader-range wider ranged-repeat quantified-group alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_no_match_overflow_behavior(
        self,
    ) -> None:
        observed_pattern = rebar.compile("a(?P<outer>(bc|de){1,4})?(?(outer)d|e)")
        expected_pattern = re.compile("a(?P<outer>(bc|de){1,4})?(?(outer)d|e)")

        self.assertIsNone(observed_pattern.fullmatch("abcbcbcbcbcd"))
        self.assertIsNone(expected_pattern.fullmatch("abcbcbcbcbcd"))


if __name__ == "__main__":
    unittest.main()
