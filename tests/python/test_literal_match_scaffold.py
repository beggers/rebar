from __future__ import annotations

import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar


class RebarLiteralMatchScaffoldTest(unittest.TestCase):
    def test_module_helpers_support_literal_str_matches(self) -> None:
        search_match = rebar.search("abc", "zzabczz")
        self.assertIs(type(search_match), rebar.Match)
        self.assertTrue(search_match)
        self.assertEqual(search_match.group(), "abc")
        self.assertEqual(search_match.group(0), "abc")
        self.assertEqual(search_match.group(0, 0), ("abc", "abc"))
        self.assertEqual(search_match.groups(), ())
        self.assertEqual(search_match.groupdict(), {})
        self.assertEqual(search_match.span(), (2, 5))
        self.assertEqual(search_match.start(), 2)
        self.assertEqual(search_match.end(), 5)
        self.assertEqual(search_match.pos, 0)
        self.assertEqual(search_match.endpos, 7)
        self.assertIsNone(search_match.lastindex)
        self.assertIsNone(search_match.lastgroup)

        anchored_match = rebar.match("abc", "abcdef")
        self.assertIs(type(anchored_match), rebar.Match)
        self.assertEqual(anchored_match.span(), (0, 3))

        full_match = rebar.fullmatch("abc", "abc")
        self.assertIs(type(full_match), rebar.Match)
        self.assertEqual(full_match.span(), (0, 3))

        self.assertIsNone(rebar.search("abc", "zzz"))
        self.assertIsNone(rebar.match("abc", "zabc"))
        self.assertIsNone(rebar.fullmatch("abc", "abcz"))

    def test_pattern_methods_support_literal_bytes_matches(self) -> None:
        pattern = rebar.compile(b"abc")

        search_match = pattern.search(b"zzabczz")
        self.assertIs(type(search_match), rebar.Match)
        self.assertEqual(search_match.group(0), b"abc")
        self.assertEqual(search_match.groups(), ())
        self.assertEqual(search_match.groupdict(), {})
        self.assertEqual(search_match.span(), (2, 5))
        self.assertEqual(search_match.pos, 0)
        self.assertEqual(search_match.endpos, 7)

        anchored_match = pattern.match(b"abcdef")
        self.assertEqual(anchored_match.span(), (0, 3))

        full_match = pattern.fullmatch(b"abc")
        self.assertEqual(full_match.span(), (0, 3))

        self.assertIsNone(pattern.search(b"zzz"))
        self.assertIsNone(pattern.match(b"zabc"))
        self.assertIsNone(pattern.fullmatch(b"abcz"))

    def test_match_methods_reject_missing_groups(self) -> None:
        match = rebar.search("abc", "abc")

        for method_name in ("group", "span", "start", "end"):
            with self.subTest(method=method_name):
                with self.assertRaisesRegex(IndexError, "no such group"):
                    getattr(match, method_name)(1)

        with self.assertRaisesRegex(IndexError, "no such group"):
            match.group("name")

    def test_matching_rejects_type_mismatch(self) -> None:
        with self.assertRaisesRegex(TypeError, "cannot use a string pattern on a bytes-like object"):
            rebar.search("abc", b"abc")

        with self.assertRaisesRegex(TypeError, "cannot use a bytes pattern on a string-like object"):
            rebar.search(b"abc", "abc")

    def test_module_and_pattern_helpers_stay_loud_for_unsupported_cases(self) -> None:
        with self.assertRaises(NotImplementedError) as module_flags:
            rebar.search("abc", "abc", rebar.IGNORECASE | rebar.ASCII)
        self.assertIn("rebar.search() is a scaffold placeholder", str(module_flags.exception))

        with self.assertRaises(NotImplementedError) as module_meta:
            rebar.search("[ab]c", "abc")
        self.assertIn("rebar.compile() is a scaffold placeholder", str(module_meta.exception))

        pattern = rebar.compile("abc", rebar.IGNORECASE | rebar.ASCII)
        with self.assertRaises(NotImplementedError) as bound_flags:
            pattern.search("abc")
        self.assertIn("rebar.Pattern.search() is a scaffold placeholder", str(bound_flags.exception))


if __name__ == "__main__":
    unittest.main()
