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


class RebarGroupedSegmentParityTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def _assert_match_parity(
        self,
        observed: rebar.Match,
        expected: re.Match[str],
        *,
        group_name: str | None = None,
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
        if group_name is not None:
            self.assertEqual(observed.group(group_name), expected.group(group_name))
            self.assertEqual(observed.span(group_name), expected.span(group_name))

    @unittest.skipUnless(rebar.native_module_loaded(), "grouped-segment parity requires rebar._rebar")
    def test_compile_matches_cpython_grouped_segment_metadata(self) -> None:
        observed = rebar.compile("a(b)c")
        expected = re.compile("a(b)c")

        self.assertIs(observed, rebar.compile("a(b)c"))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(rebar.native_module_loaded(), "grouped-segment parity requires rebar._rebar")
    def test_module_search_matches_cpython_grouped_segment_workflow(self) -> None:
        observed = rebar.search("a(b)c", "zabcz")
        expected = re.search("a(b)c", "zabcz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(rebar.native_module_loaded(), "grouped-segment parity requires rebar._rebar")
    def test_compile_matches_cpython_named_grouped_segment_metadata(self) -> None:
        observed = rebar.compile("a(?P<word>b)c")
        expected = re.compile("a(?P<word>b)c")

        self.assertIs(observed, rebar.compile("a(?P<word>b)c"))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(rebar.native_module_loaded(), "grouped-segment parity requires rebar._rebar")
    def test_compiled_pattern_fullmatch_matches_cpython_named_grouped_segment_workflow(self) -> None:
        observed_pattern = rebar.compile("a(?P<word>b)c")
        expected_pattern = re.compile("a(?P<word>b)c")

        self.assertEqual(observed_pattern.groupindex, expected_pattern.groupindex)

        observed = observed_pattern.fullmatch("abc")
        expected = expected_pattern.fullmatch("abc")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected, group_name="word")


if __name__ == "__main__":
    unittest.main()
