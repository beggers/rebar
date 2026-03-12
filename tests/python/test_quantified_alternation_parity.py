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


class RebarQuantifiedAlternationParityTest(unittest.TestCase):
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
        self.assertEqual(observed.groups(), expected.groups())
        self.assertEqual(observed.groupdict(), expected.groupdict())
        self.assertEqual(observed.span(), expected.span())
        self.assertEqual(observed.span(1), expected.span(1))
        self.assertEqual(observed.start(1), expected.start(1))
        self.assertEqual(observed.end(1), expected.end(1))
        self.assertEqual(observed.lastindex, expected.lastindex)
        self.assertEqual(observed.lastgroup, expected.lastgroup)
        for group_name in group_names:
            self.assertEqual(observed.group(group_name), expected.group(group_name))
            self.assertEqual(observed.span(group_name), expected.span(group_name))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified-alternation parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_numbered_quantified_alternation_metadata(self) -> None:
        pattern = "a(b|c){1,2}d"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified-alternation parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_quantified_alternation_lower_bound_behavior(
        self,
    ) -> None:
        pattern = "a(b|c){1,2}d"
        observed = rebar.search(pattern, "zzacdz")
        expected = re.search(pattern, "zzacdz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified-alternation parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_quantified_alternation_second_repetition_behavior(
        self,
    ) -> None:
        pattern = "a(b|c){1,2}d"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abcd")
        expected = expected_pattern.fullmatch("abcd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified-alternation parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_named_quantified_alternation_metadata(self) -> None:
        pattern = "a(?P<word>b|c){1,2}d"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified-alternation parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_quantified_alternation_second_repetition_behavior(
        self,
    ) -> None:
        pattern = "a(?P<word>b|c){1,2}d"
        observed = rebar.search(pattern, "zzacbdzz")
        expected = re.search(pattern, "zzacbdzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified-alternation parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_quantified_alternation_lower_bound_behavior(
        self,
    ) -> None:
        pattern = "a(?P<word>b|c){1,2}d"
        observed_pattern = rebar.compile(pattern)
        expected_pattern = re.compile(pattern)

        observed = observed_pattern.fullmatch("abd")
        expected = expected_pattern.fullmatch("abd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))


if __name__ == "__main__":
    unittest.main()
