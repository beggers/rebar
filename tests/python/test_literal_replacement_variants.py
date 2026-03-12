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


class RebarLiteralReplacementVariantsTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_template_replacement_matches_cpython_for_supported_whole_match_case(self) -> None:
        cases = [
            ("abc", r"\g<0>x", "abc", 0),
            ("abc", r"\g<0>x", "abcabc", 0),
            ("abc", r"\g<0>x", "abcabc", 1),
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

                compiled = rebar.compile(pattern)
                cpython_compiled = re.compile(pattern)
                self.assertEqual(
                    compiled.sub(repl, string, count=count),
                    cpython_compiled.sub(repl, string, count=count),
                )
                self.assertEqual(
                    compiled.subn(repl, string, count=count),
                    cpython_compiled.subn(repl, string, count=count),
                )

    def test_callable_replacement_matches_cpython_and_receives_rebar_match_objects(self) -> None:
        seen_matches: list[tuple[str, tuple[int, int], str, str]] = []

        def replacement(match: rebar.Match) -> str:
            seen_matches.append(
                (
                    type(match).__module__,
                    match.span(),
                    match.group(0),
                    match.re.pattern,
                )
            )
            return "x"

        result = rebar.sub("abc", replacement, "abcabc")
        result_with_count = rebar.subn("abc", replacement, "abcabc", count=1)
        pattern = rebar.compile("abc")
        pattern_result = pattern.sub(replacement, "abcabc")
        pattern_result_with_count = pattern.subn(replacement, "abcabc", count=1)

        def cpython_replacement(match: re.Match[str]) -> str:
            return "x"

        self.assertEqual(result, re.sub("abc", cpython_replacement, "abcabc"))
        self.assertEqual(result_with_count, re.subn("abc", cpython_replacement, "abcabc", count=1))
        self.assertEqual(pattern_result, re.compile("abc").sub(cpython_replacement, "abcabc"))
        self.assertEqual(
            pattern_result_with_count,
            re.compile("abc").subn(cpython_replacement, "abcabc", count=1),
        )
        self.assertEqual(
            seen_matches,
            [
                ("re", (0, 3), "abc", "abc"),
                ("re", (3, 6), "abc", "abc"),
                ("re", (0, 3), "abc", "abc"),
                ("re", (0, 3), "abc", "abc"),
                ("re", (3, 6), "abc", "abc"),
                ("re", (0, 3), "abc", "abc"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
