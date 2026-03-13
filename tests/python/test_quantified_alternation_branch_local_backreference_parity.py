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


class RebarQuantifiedAlternationBranchLocalBackreferenceParityTest(unittest.TestCase):
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
        "quantified alternation branch-local backreference parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_numbered_metadata(self) -> None:
        pattern = r"a((b|c)\2){1,2}d"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation branch-local backreference parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_lower_bound_b_branch(self) -> None:
        pattern = r"a((b|c)\2){1,2}d"
        observed = rebar.search(pattern, "zzabbdzz")
        expected = re.search(pattern, "zzabbdzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation branch-local backreference parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_lower_bound_c_branch(self) -> None:
        observed_pattern = rebar.compile(r"a((b|c)\2){1,2}d")
        expected_pattern = re.compile(r"a((b|c)\2){1,2}d")

        observed = observed_pattern.fullmatch("accd")
        expected = expected_pattern.fullmatch("accd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation branch-local backreference parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_second_repetition_b_branch(
        self,
    ) -> None:
        observed_pattern = rebar.compile(r"a((b|c)\2){1,2}d")
        expected_pattern = re.compile(r"a((b|c)\2){1,2}d")

        observed = observed_pattern.fullmatch("abbbbd")
        expected = expected_pattern.fullmatch("abbbbd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation branch-local backreference parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_numbered_no_match(self) -> None:
        pattern = rebar.compile(r"a((b|c)\2){1,2}d")
        expected_pattern = re.compile(r"a((b|c)\2){1,2}d")

        self.assertIsNone(pattern.fullmatch("abcd"))
        self.assertIsNone(expected_pattern.fullmatch("abcd"))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation branch-local backreference parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_named_metadata(self) -> None:
        pattern = "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d"
        observed = rebar.compile(pattern)
        expected = re.compile(pattern)

        self.assertIs(observed, rebar.compile(pattern))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation branch-local backreference parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_named_lower_bound_c_branch(self) -> None:
        pattern = "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d"
        observed = rebar.search(pattern, "zzaccdzz")
        expected = re.search(pattern, "zzaccdzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer", "inner"))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation branch-local backreference parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_second_repetition_c_branch(self) -> None:
        pattern_text = "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d"
        observed_pattern = rebar.compile(pattern_text)
        expected_pattern = re.compile(pattern_text)

        observed = observed_pattern.fullmatch("accccd")
        expected = expected_pattern.fullmatch("accccd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer", "inner"))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation branch-local backreference parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_second_repetition_mixed_branches(
        self,
    ) -> None:
        pattern_text = "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d"
        observed_pattern = rebar.compile(pattern_text)
        expected_pattern = re.compile(pattern_text)

        observed = observed_pattern.fullmatch("abbccd")
        expected = expected_pattern.fullmatch("abbccd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer", "inner"))

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "quantified alternation branch-local backreference parity requires rebar._rebar",
    )
    def test_pattern_fullmatch_matches_cpython_named_no_match(self) -> None:
        pattern_text = "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d"
        observed_pattern = rebar.compile(pattern_text)
        expected_pattern = re.compile(pattern_text)

        self.assertIsNone(observed_pattern.fullmatch("abcd"))
        self.assertIsNone(expected_pattern.fullmatch("abcd"))


if __name__ == "__main__":
    unittest.main()
