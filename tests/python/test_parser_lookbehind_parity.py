from __future__ import annotations

import pathlib
import re as stdlib_re
import sys
import unittest
from unittest import mock


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar


class RebarParserLookbehindParityTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_compile_matches_cpython_for_bounded_lookbehind_cases(self) -> None:
        expected = stdlib_re.compile("(?<=ab)c")
        compiled = rebar.compile("(?<=ab)c")

        self.assertIs(type(compiled), rebar.Pattern)
        self.assertEqual(compiled.pattern, expected.pattern)
        self.assertEqual(compiled.flags, expected.flags)
        self.assertEqual(compiled.groups, expected.groups)
        self.assertEqual(compiled.groupindex, expected.groupindex)

        with self.assertRaises(NotImplementedError) as raised:
            compiled.search("abc")
        self.assertIn("rebar.Pattern.search() is a scaffold placeholder", str(raised.exception))

        with self.assertRaises(rebar.error) as variable_width:
            rebar.compile("(?<=a+)b")

        self.assertEqual(type(variable_width.exception), stdlib_re.error)
        self.assertEqual(str(variable_width.exception), "look-behind requires fixed-width pattern")
        self.assertIsNone(variable_width.exception.pos)
        self.assertIsNone(variable_width.exception.lineno)
        self.assertIsNone(variable_width.exception.colno)

    def test_compile_respects_cache_and_purge_for_supported_lookbehind_case(self) -> None:
        first = rebar.compile("(?<=ab)c")
        second = rebar.compile("(?<=ab)c")
        self.assertIs(first, second)

        rebar.purge()

        refreshed = rebar.compile("(?<=ab)c")
        self.assertIsNot(first, refreshed)

    def test_compile_does_not_delegate_to_stdlib_for_bounded_lookbehind_cases(self) -> None:
        with mock.patch.object(
            rebar._stdlib_re,
            "compile",
            side_effect=AssertionError("stdlib re.compile() should not be used"),
        ):
            compiled = rebar.compile("(?<=ab)c")
            self.assertEqual(compiled.pattern, "(?<=ab)c")
            self.assertEqual(compiled.flags, int(rebar.UNICODE))

            with self.assertRaises(rebar.error) as raised:
                rebar.compile("(?<=a+)b")

        self.assertEqual(str(raised.exception), "look-behind requires fixed-width pattern")


if __name__ == "__main__":
    unittest.main()
