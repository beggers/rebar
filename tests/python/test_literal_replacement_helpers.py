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


class RebarLiteralReplacementHelpersTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_module_sub_and_subn_match_cpython_for_supported_literal_cases(self) -> None:
        cases = [
            ("abc", "x", "zzz", 0),
            ("abc", "x", "zabczz", 0),
            ("abc", "x", "abcabc", 0),
            ("abc", "x", "abcabc", 1),
            ("abc", "x", "abcabc", -1),
            (b"abc", b"x", b"zzz", 0),
            (b"abc", b"x", b"zabcabc", 0),
            (b"abc", b"x", b"abcabc", 1),
        ]

        for pattern, repl, string, count in cases:
            with self.subTest(pattern=pattern, repl=repl, string=string, count=count):
                self.assertEqual(
                    rebar.sub(pattern, repl, string, count=count),
                    re.sub(pattern, repl, string, count=count),
                )
                self.assertEqual(
                    rebar.subn(pattern, repl, string, count=count),
                    re.subn(pattern, repl, string, count=count),
                )

    def test_pattern_sub_and_subn_support_supported_subset(self) -> None:
        pattern = rebar.compile("abc")
        self.assertEqual(pattern.sub("x", "zzz"), "zzz")
        self.assertEqual(pattern.sub("x", "zabczz"), "zxzz")
        self.assertEqual(pattern.sub("x", "abcabc"), "xx")
        self.assertEqual(pattern.sub("x", "abcabc", 1), "xabc")
        self.assertEqual(pattern.sub("x", "abcabc", -1), "abcabc")
        self.assertEqual(pattern.subn("x", "abcabc"), ("xx", 2))
        self.assertEqual(pattern.subn("x", "abcabc", 1), ("xabc", 1))

        bytes_pattern = rebar.compile(b"abc")
        self.assertEqual(bytes_pattern.sub(b"x", b"abcabc"), b"xx")
        self.assertEqual(bytes_pattern.subn(b"x", b"zabczz"), (b"zxzz", 1))

    def test_replacement_helpers_reject_type_mismatch(self) -> None:
        with self.assertRaisesRegex(TypeError, "cannot use a string pattern on a bytes-like object"):
            rebar.sub("abc", "x", b"abc")

        with self.assertRaisesRegex(TypeError, "cannot use a bytes pattern on a string-like object"):
            rebar.sub(b"abc", b"x", "abc")

        with self.assertRaisesRegex(TypeError, "expected str instance, bytes found"):
            rebar.sub("abc", b"x", "abc")

        pattern = rebar.compile(b"abc")
        with self.assertRaisesRegex(TypeError, "expected a bytes-like object, str found"):
            pattern.sub("x", b"abc")

    def test_replacement_helpers_stay_loud_for_unsupported_cases_without_cache_mutation(self) -> None:
        with self.assertRaises(NotImplementedError) as module_callable:
            rebar.sub("abc", lambda match: "x", "abc")
        self.assertIn("rebar.sub() is a scaffold placeholder", str(module_callable.exception))
        self.assertEqual(rebar._COMPILE_CACHE, {})

        with self.assertRaises(NotImplementedError) as module_template:
            rebar.sub("abc", r"\\1", "abc")
        self.assertIn("rebar.sub() is a scaffold placeholder", str(module_template.exception))
        self.assertEqual(rebar._COMPILE_CACHE, {})

        with self.assertRaises(NotImplementedError) as module_flags:
            rebar.subn("abc", "x", "abc", flags=rebar.IGNORECASE)
        self.assertIn("rebar.subn() is a scaffold placeholder", str(module_flags.exception))
        self.assertEqual(rebar._COMPILE_CACHE, {})

        with self.assertRaises(NotImplementedError) as module_meta:
            rebar.sub("a.c", "x", "abc")
        self.assertIn("rebar.compile() is a scaffold placeholder", str(module_meta.exception))
        self.assertEqual(rebar._COMPILE_CACHE, {})

        with self.assertRaises(NotImplementedError) as module_empty:
            rebar.sub("", "x", "abc")
        self.assertIn("rebar.sub() is a scaffold placeholder", str(module_empty.exception))
        self.assertEqual(rebar._COMPILE_CACHE, {})

        flagged_pattern = rebar.compile("abc", rebar.IGNORECASE)
        with self.assertRaises(NotImplementedError) as bound_flags:
            flagged_pattern.sub("x", "abc")
        self.assertIn("rebar.Pattern.sub() is a scaffold placeholder", str(bound_flags.exception))

        empty_pattern = rebar.compile("")
        with self.assertRaises(NotImplementedError) as bound_empty:
            empty_pattern.subn("x", "abc")
        self.assertIn("rebar.Pattern.subn() is a scaffold placeholder", str(bound_empty.exception))

        with self.assertRaises(NotImplementedError) as bound_template:
            rebar.compile("abc").sub(r"\\1", "abc")
        self.assertIn("rebar.Pattern.sub() is a scaffold placeholder", str(bound_template.exception))


if __name__ == "__main__":
    unittest.main()
