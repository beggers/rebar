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


class RebarLiteralCollectionHelpersTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_module_split_matches_cpython_for_supported_literal_cases(self) -> None:
        cases = [
            ("abc", "zzz", 0),
            ("abc", "zzabczz", 0),
            ("abc", "abcabc", 0),
            ("abc", "abczzz", 0),
            ("abc", "zzzabc", 0),
            ("abc", "abcabc", 1),
            ("abc", "abcabc", -1),
            (b"abc", b"zzabczzabc", 1),
        ]

        for pattern, string, maxsplit in cases:
            with self.subTest(pattern=pattern, string=string, maxsplit=maxsplit):
                self.assertEqual(
                    rebar.split(pattern, string, maxsplit=maxsplit),
                    re.split(pattern, string, maxsplit=maxsplit),
                )

    def test_pattern_split_supports_supported_subset(self) -> None:
        pattern = rebar.compile("abc")

        self.assertEqual(pattern.split("zzabczz"), ["zz", "zz"])
        self.assertEqual(pattern.split("abcabc"), ["", "", ""])
        self.assertEqual(pattern.split("abcabc", 1), ["", "abc"])
        self.assertEqual(pattern.split("abcabc", -1), ["abcabc"])

        bytes_pattern = rebar.compile(b"abc")
        self.assertEqual(bytes_pattern.split(b"zzabczz"), [b"zz", b"zz"])

    def test_findall_returns_whole_match_results_for_supported_cases(self) -> None:
        self.assertEqual(rebar.findall("abc", "abcabc"), ["abc", "abc"])
        self.assertEqual(rebar.findall(b"abc", b"zabcabc"), [b"abc", b"abc"])

        pattern = rebar.compile("abc")
        self.assertEqual(pattern.findall("zabcabcz", 1, 7), ["abc", "abc"])

        bytes_pattern = rebar.compile(b"abc")
        self.assertEqual(bytes_pattern.findall(b"zabcabcz", 1, 7), [b"abc", b"abc"])

    def test_finditer_yields_ordered_match_objects_and_exhausts_normally(self) -> None:
        iterator = rebar.finditer("abc", "zabcabc")
        matches = list(iterator)

        self.assertEqual([type(match) for match in matches], [rebar.Match, rebar.Match])
        self.assertEqual([match.group(0) for match in matches], ["abc", "abc"])
        self.assertEqual([match.span() for match in matches], [(1, 4), (4, 7)])
        self.assertEqual(next(iterator, None), None)

        pattern = rebar.compile(b"abc")
        bounded = pattern.finditer(b"zabcabcx", 1, 7)
        bounded_matches = list(bounded)
        self.assertEqual([match.group(0) for match in bounded_matches], [b"abc", b"abc"])
        self.assertEqual([match.span() for match in bounded_matches], [(1, 4), (4, 7)])
        self.assertEqual(next(bounded, None), None)

    def test_collection_helpers_reject_type_mismatch(self) -> None:
        with self.assertRaisesRegex(TypeError, "cannot use a string pattern on a bytes-like object"):
            rebar.split("abc", b"abc")

        pattern = rebar.compile(b"abc")
        with self.assertRaisesRegex(TypeError, "cannot use a bytes pattern on a string-like object"):
            list(pattern.finditer("abc"))

    def test_collection_helpers_stay_loud_for_unsupported_cases(self) -> None:
        with self.assertRaises(NotImplementedError) as module_flags:
            rebar.findall("abc", "abc", rebar.IGNORECASE)
        self.assertIn("rebar.findall() is a scaffold placeholder", str(module_flags.exception))

        with self.assertRaises(NotImplementedError) as module_meta:
            rebar.finditer("a.c", "abc")
        self.assertIn("rebar.compile() is a scaffold placeholder", str(module_meta.exception))

        with self.assertRaises(NotImplementedError) as module_empty:
            rebar.split("", "abc")
        self.assertIn("rebar.split() is a scaffold placeholder", str(module_empty.exception))

        flagged_pattern = rebar.compile("abc", rebar.IGNORECASE)
        with self.assertRaises(NotImplementedError) as bound_flags:
            flagged_pattern.finditer("abc")
        self.assertIn("rebar.Pattern.finditer() is a scaffold placeholder", str(bound_flags.exception))

        empty_pattern = rebar.compile("")
        with self.assertRaises(NotImplementedError) as bound_empty:
            empty_pattern.findall("abc")
        self.assertIn("rebar.Pattern.findall() is a scaffold placeholder", str(bound_empty.exception))


if __name__ == "__main__":
    unittest.main()
