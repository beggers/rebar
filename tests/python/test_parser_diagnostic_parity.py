from __future__ import annotations

import pathlib
import re as stdlib_re
import sys
import unittest
import warnings


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar


class RebarParserDiagnosticParityTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_compile_matches_cpython_for_bounded_error_cases(self) -> None:
        for pattern in ("*abc", "a(?i)b", "(?L:a)", b"(?u:a)", b"\\u1234"):
            with self.subTest(pattern=pattern):
                with self.assertRaises(stdlib_re.error) as expected:
                    stdlib_re.compile(pattern)

                with self.assertRaises(rebar.error) as actual:
                    rebar.compile(pattern)

                self.assertEqual(type(actual.exception), type(expected.exception))
                self.assertEqual(str(actual.exception), str(expected.exception))
                self.assertEqual(actual.exception.pos, expected.exception.pos)
                self.assertEqual(actual.exception.lineno, expected.exception.lineno)
                self.assertEqual(actual.exception.colno, expected.exception.colno)

    def test_nested_set_warning_matches_cpython_and_stays_compile_only(self) -> None:
        with warnings.catch_warnings(record=True) as expected_warnings:
            warnings.simplefilter("always")
            expected = stdlib_re.compile("[[a]")

        with warnings.catch_warnings(record=True) as actual_warnings:
            warnings.simplefilter("always")
            compiled = rebar.compile("[[a]")

        self.assertEqual(
            [(warning.category, str(warning.message)) for warning in actual_warnings],
            [(warning.category, str(warning.message)) for warning in expected_warnings],
        )
        self.assertIs(type(compiled), rebar.Pattern)
        self.assertEqual(compiled.pattern, expected.pattern)
        self.assertEqual(compiled.flags, expected.flags)
        with self.assertRaises(NotImplementedError) as raised:
            compiled.search("[[a]")
        self.assertIn("rebar.Pattern.search() is a scaffold placeholder", str(raised.exception))

    def test_nested_set_warning_respects_cache_and_purge(self) -> None:
        with warnings.catch_warnings(record=True) as first_warnings:
            warnings.simplefilter("always")
            first = rebar.compile("[[a]")

        with warnings.catch_warnings(record=True) as second_warnings:
            warnings.simplefilter("always")
            second = rebar.compile("[[a]")

        self.assertIs(first, second)
        self.assertEqual(len(first_warnings), 1)
        self.assertEqual(first_warnings[0].category, FutureWarning)
        self.assertEqual(str(first_warnings[0].message), "Possible nested set at position 1")
        self.assertEqual(second_warnings, [])

        rebar.purge()

        with warnings.catch_warnings(record=True) as refreshed_warnings:
            warnings.simplefilter("always")
            refreshed = rebar.compile("[[a]")

        self.assertIsNot(first, refreshed)
        self.assertEqual(len(refreshed_warnings), 1)
        self.assertEqual(refreshed_warnings[0].category, FutureWarning)
        self.assertEqual(str(refreshed_warnings[0].message), "Possible nested set at position 1")


if __name__ == "__main__":
    unittest.main()
