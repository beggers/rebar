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

    def _normalize_match(self, match: object) -> dict[str, object]:
        return {
            "group0": match.group(0),
            "groups": match.groups(),
            "groupdict": match.groupdict(),
            "span": match.span(),
            "pos": match.pos,
            "endpos": match.endpos,
            "lastindex": match.lastindex,
            "lastgroup": match.lastgroup,
        }

    def _assert_finditer_parity(self, observed_iter: object, expected_iter: object) -> None:
        observed_matches = list(observed_iter)
        expected_matches = list(expected_iter)

        self.assertEqual([type(match) for match in observed_matches], [rebar.Match] * len(observed_matches))
        self.assertEqual(
            [self._normalize_match(match) for match in observed_matches],
            [self._normalize_match(match) for match in expected_matches],
        )
        self.assertIsNone(next(observed_iter, None))
        self.assertIsNone(next(expected_iter, None))

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
        cases = [
            ("abc", "zzabczz", 0),
            ("abc", "abcabc", 0),
            ("abc", "abcabc", 1),
            ("abc", "abcabc", -1),
            (b"abc", b"zzabczz", 0),
            (b"abc", b"zzabczzabc", 1),
        ]

        for pattern, string, maxsplit in cases:
            with self.subTest(pattern=pattern, string=string, maxsplit=maxsplit):
                observed_pattern = rebar.compile(pattern)
                expected_pattern = re.compile(pattern)
                self.assertEqual(
                    observed_pattern.split(string, maxsplit),
                    expected_pattern.split(string, maxsplit),
                )

    def test_findall_returns_whole_match_results_for_supported_cases(self) -> None:
        module_cases = [
            ("abc", "abcabc"),
            (b"abc", b"zabcabc"),
        ]
        pattern_cases = [
            ("abc", "zabcabcz", 1, 7),
            (b"abc", b"zabcabcz", 1, 7),
        ]

        for pattern, string in module_cases:
            with self.subTest(pattern=pattern, string=string, helper="module"):
                self.assertEqual(
                    rebar.findall(pattern, string),
                    re.findall(pattern, string),
                )

        for pattern, string, pos, endpos in pattern_cases:
            with self.subTest(pattern=pattern, string=string, pos=pos, endpos=endpos, helper="pattern"):
                observed_pattern = rebar.compile(pattern)
                expected_pattern = re.compile(pattern)
                self.assertEqual(
                    observed_pattern.findall(string, pos, endpos),
                    expected_pattern.findall(string, pos, endpos),
                )

    def test_finditer_yields_ordered_match_objects_and_exhausts_normally(self) -> None:
        module_cases = [
            ("abc", "zabcabc"),
            (b"abc", b"zabcabc"),
        ]
        pattern_cases = [
            ("abc", "zabcabcx", 1, 7),
            (b"abc", b"zabcabcx", 1, 7),
        ]

        for pattern, string in module_cases:
            with self.subTest(pattern=pattern, string=string, helper="module"):
                self._assert_finditer_parity(
                    rebar.finditer(pattern, string),
                    re.finditer(pattern, string),
                )

        for pattern, string, pos, endpos in pattern_cases:
            with self.subTest(pattern=pattern, string=string, pos=pos, endpos=endpos, helper="pattern"):
                observed_pattern = rebar.compile(pattern)
                expected_pattern = re.compile(pattern)
                self._assert_finditer_parity(
                    observed_pattern.finditer(string, pos, endpos),
                    expected_pattern.finditer(string, pos, endpos),
                )

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
            rebar.finditer("[ab]c", "abc")
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
