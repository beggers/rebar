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


class RebarQuantifiedAlternationConditionalParityTest(unittest.TestCase):
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
        "quantified alternation conditional parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_numbered_metadata(self) -> None:
        pattern = "a((b|c){1,2})?(?(1)d|e)"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_absent_behavior(self) -> None:
        pattern = "a((b|c){1,2})?(?(1)d|e)"
        observed = rebar.search(pattern, "zzaezz")
        expected = re.search(pattern, "zzaezz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_lower_bound_b_behavior(self) -> None:
        pattern = "a((b|c){1,2})?(?(1)d|e)"
        observed = rebar.search(pattern, "zzabdzz")
        expected = re.search(pattern, "zzabdzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_second_repetition_b_behavior(self) -> None:
        pattern = "a((b|c){1,2})?(?(1)d|e)"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abbd")
        expected = expected_pattern.fullmatch("abbd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_second_repetition_mixed_behavior(
        self,
    ) -> None:
        pattern = "a((b|c){1,2})?(?(1)d|e)"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abcd")
        expected = expected_pattern.fullmatch("abcd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_no_match(self) -> None:
        observed_pattern = rebar.compile("a((b|c){1,2})?(?(1)d|e)")
        expected_pattern = re.compile("a((b|c){1,2})?(?(1)d|e)")

        self.assertIsNone(observed_pattern.fullmatch("abe"))
        self.assertIsNone(expected_pattern.fullmatch("abe"))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation conditional parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_named_metadata(self) -> None:
        pattern = "a(?P<outer>(b|c){1,2})?(?(outer)d|e)"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_absent_behavior(self) -> None:
        pattern = "a(?P<outer>(b|c){1,2})?(?(outer)d|e)"
        observed = rebar.search(pattern, "zzaezz")
        expected = re.search(pattern, "zzaezz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation conditional parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_lower_bound_c_behavior(self) -> None:
        pattern = "a(?P<outer>(b|c){1,2})?(?(outer)d|e)"
        observed = rebar.search(pattern, "zzacdzz")
        expected = re.search(pattern, "zzacdzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_second_repetition_c_behavior(self) -> None:
        pattern = "a(?P<outer>(b|c){1,2})?(?(outer)d|e)"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("accd")
        expected = expected_pattern.fullmatch("accd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_second_repetition_mixed_behavior(
        self,
    ) -> None:
        pattern = "a(?P<outer>(b|c){1,2})?(?(outer)d|e)"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abcd")
        expected = expected_pattern.fullmatch("abcd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation conditional parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_no_match(self) -> None:
        observed_pattern = rebar.compile("a(?P<outer>(b|c){1,2})?(?(outer)d|e)")
        expected_pattern = re.compile("a(?P<outer>(b|c){1,2})?(?(outer)d|e)")

        self.assertIsNone(observed_pattern.fullmatch("acce"))
        self.assertIsNone(expected_pattern.fullmatch("acce"))


if __name__ == "__main__":
    unittest.main()
