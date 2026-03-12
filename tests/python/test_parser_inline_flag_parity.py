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


class RebarParserInlineFlagParityTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_compile_matches_cpython_for_bounded_inline_flag_success_cases(self) -> None:
        for pattern, subject in (("(?u:a)", "a"), (b"(?L:a)", b"a")):
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

    def test_compile_respects_cache_and_purge_for_supported_inline_flag_cases(self) -> None:
        for pattern in ("(?u:a)", b"(?L:a)"):
            with self.subTest(pattern=pattern):
                first = rebar.compile(pattern)
                second = rebar.compile(pattern)
                self.assertIs(first, second)

                rebar.purge()

                refreshed = rebar.compile(pattern)
                self.assertIsNot(first, refreshed)

    def test_compile_does_not_delegate_to_stdlib_for_supported_inline_flag_cases(self) -> None:
        with mock.patch.object(
            rebar._stdlib_re,
            "compile",
            side_effect=AssertionError("stdlib re.compile() should not be used"),
        ):
            str_compiled = rebar.compile("(?u:a)")
            bytes_compiled = rebar.compile(b"(?L:a)")

        self.assertEqual(str_compiled.pattern, "(?u:a)")
        self.assertEqual(str_compiled.flags, int(rebar.UNICODE))
        self.assertEqual(bytes_compiled.pattern, b"(?L:a)")
        self.assertEqual(bytes_compiled.flags, 0)


if __name__ == "__main__":
    unittest.main()
