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


class RebarNumberedBackreferenceParityTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def _assert_match_parity(self, observed: rebar.Match, expected: re.Match[str]) -> None:
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

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "numbered-backreference parity requires rebar._rebar",
    )
    def test_compile_matches_cpython_numbered_backreference_metadata(self) -> None:
        observed = rebar.compile(r"(ab)\1")
        expected = re.compile(r"(ab)\1")

        self.assertIs(observed, rebar.compile(r"(ab)\1"))
        self.assertEqual(observed.pattern, expected.pattern)
        self.assertEqual(observed.flags, expected.flags)
        self.assertEqual(observed.groups, expected.groups)
        self.assertEqual(observed.groupindex, expected.groupindex)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "numbered-backreference parity requires rebar._rebar",
    )
    def test_module_search_matches_cpython_numbered_backreference_behavior(self) -> None:
        observed = rebar.search(r"(ab)\1", "zzababzz")
        expected = re.search(r"(ab)\1", "zzababzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "numbered-backreference parity requires rebar._rebar",
    )
    def test_pattern_search_matches_cpython_numbered_backreference_behavior(self) -> None:
        observed_pattern = rebar.compile(r"(ab)\1")
        expected_pattern = re.compile(r"(ab)\1")

        self.assertEqual(observed_pattern.groupindex, expected_pattern.groupindex)

        observed = observed_pattern.search("zzababzz")
        expected = expected_pattern.search("zzababzz")

        self.assertIsNotNone(observed)
        self.assertIsNotNone(expected)
        self._assert_match_parity(observed, expected)
