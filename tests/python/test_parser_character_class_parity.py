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


class RebarParserCharacterClassParityTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_compile_matches_cpython_for_bounded_character_class_ignorecase_case(self) -> None:
        expected = stdlib_re.compile("[A-Z_][a-z0-9_]+", stdlib_re.IGNORECASE)
        compiled = rebar.compile("[A-Z_][a-z0-9_]+", rebar.IGNORECASE)

        self.assertIs(type(compiled), rebar.Pattern)
        self.assertEqual(compiled.pattern, expected.pattern)
        self.assertEqual(compiled.flags, expected.flags)
        self.assertEqual(compiled.groups, expected.groups)
        self.assertEqual(compiled.groupindex, expected.groupindex)

        with self.assertRaises(NotImplementedError) as raised:
            compiled.search("Token_123")
        self.assertIn("rebar.Pattern.search() is a scaffold placeholder", str(raised.exception))

    def test_compile_respects_cache_and_purge_for_bounded_character_class_ignorecase_case(self) -> None:
        first = rebar.compile("[A-Z_][a-z0-9_]+", rebar.IGNORECASE)
        second = rebar.compile("[A-Z_][a-z0-9_]+", rebar.IGNORECASE | rebar.UNICODE)
        self.assertIs(first, second)

        rebar.purge()

        refreshed = rebar.compile("[A-Z_][a-z0-9_]+", rebar.IGNORECASE)
        self.assertIsNot(first, refreshed)

    def test_compile_does_not_delegate_to_stdlib_for_bounded_character_class_ignorecase_case(self) -> None:
        with mock.patch.object(
            rebar._stdlib_re,
            "compile",
            side_effect=AssertionError("stdlib re.compile() should not be used"),
        ):
            compiled = rebar.compile("[A-Z_][a-z0-9_]+", rebar.IGNORECASE)

        self.assertEqual(compiled.pattern, "[A-Z_][a-z0-9_]+")
        self.assertEqual(compiled.flags, int(rebar.IGNORECASE | rebar.UNICODE))


if __name__ == "__main__":
    unittest.main()
