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


class RebarParserConstructCompileParityTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_compile_matches_cpython_for_bounded_possessive_and_atomic_cases(self) -> None:
        for pattern, subject in (("a*+", "aaaa"), ("(?>ab|a)b", "ab")):
            with self.subTest(pattern=pattern):
                expected = stdlib_re.compile(pattern)
                compiled = rebar.compile(pattern)

                self.assertIs(type(compiled), rebar.Pattern)
                self.assertEqual(compiled.pattern, expected.pattern)
                self.assertEqual(compiled.flags, expected.flags)
                self.assertEqual(compiled.groups, expected.groups)
                self.assertEqual(compiled.groupindex, expected.groupindex)

                with self.assertRaises(NotImplementedError) as raised:
                    compiled.search(subject)
                self.assertIn("rebar.Pattern.search() is a scaffold placeholder", str(raised.exception))

    def test_compile_respects_cache_and_purge_for_bounded_possessive_and_atomic_cases(self) -> None:
        for pattern in ("a*+", "(?>ab|a)b"):
            with self.subTest(pattern=pattern):
                first = rebar.compile(pattern)
                second = rebar.compile(pattern)
                self.assertIs(first, second)

                rebar.purge()

                refreshed = rebar.compile(pattern)
                self.assertIsNot(first, refreshed)

    def test_compile_does_not_delegate_to_stdlib_for_bounded_possessive_and_atomic_cases(self) -> None:
        with mock.patch.object(
            rebar._stdlib_re,
            "compile",
            side_effect=AssertionError("stdlib re.compile() should not be used"),
        ):
            possessive = rebar.compile("a*+")
            atomic = rebar.compile("(?>ab|a)b")

        self.assertEqual(possessive.pattern, "a*+")
        self.assertEqual(possessive.flags, int(rebar.UNICODE))
        self.assertEqual(atomic.pattern, "(?>ab|a)b")
        self.assertEqual(atomic.flags, int(rebar.UNICODE))


if __name__ == "__main__":
    unittest.main()
