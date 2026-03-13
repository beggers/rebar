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


class RebarQuantifiedAlternationOpenEndedParityTest(unittest.TestCase):
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
        "quantified alternation open-ended parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_numbered_open_ended_metadata(self) -> None:
        pattern = "a(b|c){1,}d"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation open-ended parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_lower_bound_branches(self) -> None:
        pattern = "a(b|c){1,}d"

        observed_b = rebar.search(pattern, "zzabdzz")
        expected_b = re.search(pattern, "zzabdzz")
        self.assertIsNotNone(observed_b)
        self.assertIsNotNone(expected_b)
        self._assert_match_parity(observed_b, expected_b)

        observed_c = rebar.search(pattern, "zzacdzz")
        expected_c = re.search(pattern, "zzacdzz")
        self.assertIsNotNone(observed_c)
        self.assertIsNotNone(expected_c)
        self._assert_match_parity(observed_c, expected_c)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation open-ended parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_repetition_and_no_match_paths(
        self,
    ) -> None:
        observed_pattern = rebar.compile("a(b|c){1,}d")
        expected_pattern = re.compile("a(b|c){1,}d")

        observed = observed_pattern.fullmatch("abcbcd")
        expected = expected_pattern.fullmatch("abcbcd")
        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

        self.assertIsNone(observed_pattern.fullmatch("ad"))
        self.assertIsNone(expected_pattern.fullmatch("ad"))
        self.assertIsNone(observed_pattern.fullmatch("abed"))
        self.assertIsNone(expected_pattern.fullmatch("abed"))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation open-ended parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_named_open_ended_metadata(self) -> None:
        pattern = "a(?P<word>b|c){1,}d"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation open-ended parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_lower_bound_branches(self) -> None:
        pattern = "a(?P<word>b|c){1,}d"

        observed_b = rebar.search(pattern, "zzabdzz")
        expected_b = re.search(pattern, "zzabdzz")
        self.assertIsNotNone(observed_b)
        self.assertIsNotNone(expected_b)
        self._assert_match_parity(observed_b, expected_b, group_names=("word",))

        observed_c = rebar.search(pattern, "zzacdzz")
        expected_c = re.search(pattern, "zzacdzz")
        self.assertIsNotNone(observed_c)
        self.assertIsNotNone(expected_c)
        self._assert_match_parity(observed_c, expected_c, group_names=("word",))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation open-ended parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_repetition_and_no_match_paths(
        self,
    ) -> None:
        observed_pattern = rebar.compile("a(?P<word>b|c){1,}d")
        expected_pattern = re.compile("a(?P<word>b|c){1,}d")

        observed = observed_pattern.fullmatch("abccd")
        expected = expected_pattern.fullmatch("abccd")
        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("word",))

        observed_fourth = observed_pattern.fullmatch("abcbcd")
        expected_fourth = expected_pattern.fullmatch("abcbcd")
        self.assertIsNotNone(observed_fourth)
        self.assertIsNotNone(expected_fourth)
        self._assert_match_parity(
            observed_fourth,
            expected_fourth,
            group_names=("word",),
        )

        self.assertIsNone(observed_pattern.fullmatch("ad"))
        self.assertIsNone(expected_pattern.fullmatch("ad"))
        self.assertIsNone(observed_pattern.fullmatch("abed"))
        self.assertIsNone(expected_pattern.fullmatch("abed"))


if __name__ == "__main__":
    unittest.main()
