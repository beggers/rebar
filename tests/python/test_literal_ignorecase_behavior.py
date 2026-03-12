from __future__ import annotations

import pathlib
import re as stdlib_re
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar


class RebarLiteralIgnorecaseBehaviorTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_module_helpers_support_literal_ignorecase_for_str_and_bytes(self) -> None:
        str_search = rebar.search("AbC", "zzaBczz", rebar.IGNORECASE)
        expected_str_search = stdlib_re.search("AbC", "zzaBczz", stdlib_re.IGNORECASE)
        self.assertIs(type(str_search), rebar.Match)
        self.assertEqual(str_search.group(0), expected_str_search.group(0))
        self.assertEqual(str_search.span(), expected_str_search.span())

        str_match = rebar.match("AbC", "aBcdef", rebar.IGNORECASE)
        expected_str_match = stdlib_re.match("AbC", "aBcdef", stdlib_re.IGNORECASE)
        self.assertIs(type(str_match), rebar.Match)
        self.assertEqual(str_match.group(0), expected_str_match.group(0))
        self.assertEqual(str_match.span(), expected_str_match.span())

        str_fullmatch = rebar.fullmatch("AbC", "aBc", rebar.IGNORECASE)
        expected_str_fullmatch = stdlib_re.fullmatch("AbC", "aBc", stdlib_re.IGNORECASE)
        self.assertIs(type(str_fullmatch), rebar.Match)
        self.assertEqual(str_fullmatch.group(0), expected_str_fullmatch.group(0))
        self.assertEqual(str_fullmatch.span(), expected_str_fullmatch.span())
        self.assertIsNone(rebar.search("AbC", "zzz", rebar.IGNORECASE))

        bytes_search = rebar.search(b"AbC", b"zzaBczz", rebar.IGNORECASE)
        expected_bytes_search = stdlib_re.search(b"AbC", b"zzaBczz", stdlib_re.IGNORECASE)
        self.assertIs(type(bytes_search), rebar.Match)
        self.assertEqual(bytes_search.group(0), expected_bytes_search.group(0))
        self.assertEqual(bytes_search.span(), expected_bytes_search.span())

        bytes_match = rebar.match(b"AbC", b"aBcdef", rebar.IGNORECASE)
        expected_bytes_match = stdlib_re.match(b"AbC", b"aBcdef", stdlib_re.IGNORECASE)
        self.assertIs(type(bytes_match), rebar.Match)
        self.assertEqual(bytes_match.group(0), expected_bytes_match.group(0))
        self.assertEqual(bytes_match.span(), expected_bytes_match.span())

        bytes_fullmatch = rebar.fullmatch(b"AbC", b"aBc", rebar.IGNORECASE)
        expected_bytes_fullmatch = stdlib_re.fullmatch(b"AbC", b"aBc", stdlib_re.IGNORECASE)
        self.assertIs(type(bytes_fullmatch), rebar.Match)
        self.assertEqual(bytes_fullmatch.group(0), expected_bytes_fullmatch.group(0))
        self.assertEqual(bytes_fullmatch.span(), expected_bytes_fullmatch.span())
        self.assertIsNone(rebar.match(b"AbC", b"zaBc", rebar.IGNORECASE))

    def test_compiled_pattern_methods_support_literal_ignorecase(self) -> None:
        str_pattern = rebar.compile("AbC", rebar.IGNORECASE)
        self.assertEqual(str_pattern.flags, int(rebar.IGNORECASE | rebar.UNICODE))
        self.assertEqual(str_pattern.search("zzaBczz").span(), (2, 5))
        self.assertEqual(str_pattern.match("aBcdef").span(), (0, 3))
        self.assertEqual(str_pattern.fullmatch("aBc").span(), (0, 3))
        self.assertIsNone(str_pattern.search("zzz"))

        bytes_pattern = rebar.compile(b"AbC", rebar.IGNORECASE)
        self.assertEqual(bytes_pattern.flags, int(rebar.IGNORECASE))
        self.assertEqual(bytes_pattern.search(b"zzaBczz").span(), (2, 5))
        self.assertEqual(bytes_pattern.match(b"aBcdef").span(), (0, 3))
        self.assertEqual(bytes_pattern.fullmatch(b"aBc").span(), (0, 3))
        self.assertIsNone(bytes_pattern.fullmatch(b"aBcd"))

    def test_compile_cache_distinguishes_ignorecase_patterns_without_breaking_normalization(self) -> None:
        default_pattern = rebar.compile("abc")
        flagged_pattern = rebar.compile("abc", rebar.IGNORECASE)
        flagged_again = rebar.compile("abc", rebar.IGNORECASE | rebar.UNICODE)
        bytes_default_pattern = rebar.compile(b"abc")
        bytes_flagged_pattern = rebar.compile(b"abc", rebar.IGNORECASE)

        self.assertIsNot(default_pattern, flagged_pattern)
        self.assertIs(flagged_pattern, flagged_again)
        self.assertIsNot(bytes_default_pattern, bytes_flagged_pattern)

    def test_ignorecase_support_stays_bounded_to_match_helpers(self) -> None:
        with self.assertRaises(NotImplementedError) as unsupported_combo:
            rebar.search("abc", "ABC", rebar.IGNORECASE | rebar.ASCII)
        self.assertIn("rebar.search() is a scaffold placeholder", str(unsupported_combo.exception))

        with self.assertRaises(NotImplementedError) as unsupported_inline:
            rebar.search("(?i)abc", "ABC")
        self.assertIn("rebar.compile() is a scaffold placeholder", str(unsupported_inline.exception))

        with self.assertRaises(NotImplementedError) as unsupported_collection:
            rebar.findall("abc", "ABC", rebar.IGNORECASE)
        self.assertIn("rebar.findall() is a scaffold placeholder", str(unsupported_collection.exception))

        pattern = rebar.compile("abc", rebar.IGNORECASE | rebar.ASCII)
        with self.assertRaises(NotImplementedError) as unsupported_bound:
            pattern.search("ABC")
        self.assertIn("rebar.Pattern.search() is a scaffold placeholder", str(unsupported_bound.exception))


if __name__ == "__main__":
    unittest.main()
