from __future__ import annotations

import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar


class RebarCompileCacheScaffoldTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_compile_reuses_cached_pattern_for_supported_inputs(self) -> None:
        first = rebar.compile("abc")
        second = rebar.compile("abc")
        flagged = rebar.compile("abc", rebar.IGNORECASE)
        flagged_again = rebar.compile("abc", rebar.IGNORECASE)
        bytes_pattern = rebar.compile(b"abc")
        bytes_pattern_again = rebar.compile(b"abc")

        self.assertIs(first, second)
        self.assertIs(flagged, flagged_again)
        self.assertIs(bytes_pattern, bytes_pattern_again)
        self.assertIsNot(first, flagged)
        self.assertIsNot(first, bytes_pattern)

    def test_purge_clears_cached_patterns_and_returns_none(self) -> None:
        original = rebar.compile("abc")

        self.assertIsNone(rebar.purge())
        refreshed = rebar.compile("abc")
        self.assertIsNot(original, refreshed)
        self.assertIs(refreshed, rebar.compile("abc"))

    def test_unsupported_compile_requests_do_not_mutate_cache(self) -> None:
        cached = rebar.compile("abc")

        with self.assertRaises(NotImplementedError):
            rebar.compile("[ab]c")
        self.assertIs(rebar.compile("abc"), cached)

        with self.assertRaisesRegex(TypeError, "first argument must be string or compiled pattern"):
            rebar.compile(123)
        self.assertIs(rebar.compile("abc"), cached)

        with self.assertRaisesRegex(ValueError, "cannot process flags argument with a compiled pattern"):
            rebar.compile(cached, rebar.IGNORECASE)
        self.assertIs(rebar.compile("abc"), cached)

    def test_cache_keys_distinguish_normalized_flags(self) -> None:
        default_pattern = rebar.compile("abc")
        unicode_pattern = rebar.compile("abc", rebar.UNICODE)
        ascii_pattern = rebar.compile("abc", rebar.ASCII)

        self.assertIs(default_pattern, unicode_pattern)
        self.assertIsNot(default_pattern, ascii_pattern)


if __name__ == "__main__":
    unittest.main()
