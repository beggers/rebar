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


class RebarNestedGroupAlternationParityTest(unittest.TestCase):
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
        "nested-group alternation parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_nested_group_alternation_metadata(self) -> None:
        observed = rebar.compile("a((b|c))d")
        expected = re.compile("a((b|c))d")

        self.assertIs(observed, rebar.compile("a((b|c))d"))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "nested-group alternation parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_nested_group_alternation_behavior(self) -> None:
        observed = rebar.search("a((b|c))d", "zzacdzz")
        expected = re.search("a((b|c))d", "zzacdzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "nested-group alternation parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_named_nested_group_alternation_metadata(self) -> None:
        observed = rebar.compile("a(?P<outer>(?P<inner>b|c))d")
        expected = re.compile("a(?P<outer>(?P<inner>b|c))d")

        self.assertIs(observed, rebar.compile("a(?P<outer>(?P<inner>b|c))d"))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "nested-group alternation parity requires rebar._rebar",
    )
    def test_compiled_pattern_fullmatch_matches_cpython_named_nested_group_alternation_behavior(
        self,
    ) -> None:
        observed_pattern = rebar.compile("a(?P<outer>(?P<inner>b|c))d")
        expected_pattern = re.compile("a(?P<outer>(?P<inner>b|c))d")

        self.assertEqual(observed_pattern.groupindex, expected_pattern.groupindex)

        observed = observed_pattern.fullmatch("acd")
        expected = expected_pattern.fullmatch("acd")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_names=("outer", "inner"))


if __name__ == "__main__":
    unittest.main()
