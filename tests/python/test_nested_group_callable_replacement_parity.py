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
from tests.python.callable_replacement_callback_support import (
    assert_callable_replacement_match_parity,
)


class RebarNestedGroupCallableReplacementParityTest(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "nested-group callable-replacement parity requires rebar._rebar",
    )
    def test_module_sub_and_subn_match_cpython(self) -> None:
        cases = [
            ("a((b))d", lambda match: match.group(1) + "x", "abdabd", 0),
            ("a((b))d", lambda match: match.group(2) + "x", "abdabd", 1),
            ("a(?P<outer>(?P<inner>b))d", lambda match: match.group("outer") + "x", "abdabd", 0),
            ("a(?P<outer>(?P<inner>b))d", lambda match: match.group("inner") + "x", "abdabd", 1),
        ]

        for pattern, repl, string, count in cases:
            with self.subTest(pattern=pattern, string=string, count=count):
                self.assertEqual(
                    rebar.sub(pattern, repl, string, count=count),
                    re.sub(pattern, repl, string, count=count),
                )
                self.assertEqual(
                    rebar.subn(pattern, repl, string, count=count),
                    re.subn(pattern, repl, string, count=count),
                )

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "nested-group callable-replacement parity requires rebar._rebar",
    )
    def test_pattern_sub_and_subn_match_cpython(self) -> None:
        cases = [
            ("a((b))d", lambda match: match.group(1) + "x", "abdabd", 0),
            ("a((b))d", lambda match: match.group(2) + "x", "abdabd", 1),
            ("a(?P<outer>(?P<inner>b))d", lambda match: match.group("outer") + "x", "abdabd", 0),
            ("a(?P<outer>(?P<inner>b))d", lambda match: match.group("inner") + "x", "abdabd", 1),
        ]

        for pattern, repl, string, count in cases:
            with self.subTest(pattern=pattern, string=string, count=count):
                observed_pattern = rebar.compile(pattern)
                expected_pattern = re.compile(pattern)
                self.assertEqual(
                    observed_pattern.sub(repl, string, count=count),
                    expected_pattern.sub(repl, string, count=count),
                )
                self.assertEqual(
                    observed_pattern.subn(repl, string, count=count),
                    expected_pattern.subn(repl, string, count=count),
                )

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "nested-group callable-replacement parity requires rebar._rebar",
    )
    def test_module_callable_replacement_callback_match_objects_match_cpython(self) -> None:
        cases = [
            ("sub", "a((b))d", "abdabd", 0, ()),
            ("subn", "a((b))d", "abdabd", 1, ()),
            ("sub", "a(?P<outer>(?P<inner>b))d", "abdabd", 0, ("outer", "inner")),
            ("subn", "a(?P<outer>(?P<inner>b))d", "abdabd", 1, ("outer", "inner")),
        ]

        for helper, pattern, string, count, group_names in cases:
            with self.subTest(
                helper=helper,
                pattern=pattern,
                string=string,
                count=count,
            ):
                assert_callable_replacement_match_parity(
                    backend_name="rebar",
                    backend=rebar,
                    helper=helper,
                    pattern=pattern,
                    string=string,
                    count=count,
                    group_names=group_names,
                )

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "nested-group callable-replacement parity requires rebar._rebar",
    )
    def test_pattern_callable_replacement_callback_match_objects_match_cpython(self) -> None:
        cases = [
            ("sub", "a((b))d", "abdabd", 0, ()),
            ("subn", "a((b))d", "abdabd", 1, ()),
            ("sub", "a(?P<outer>(?P<inner>b))d", "abdabd", 0, ("outer", "inner")),
            ("subn", "a(?P<outer>(?P<inner>b))d", "abdabd", 1, ("outer", "inner")),
        ]

        for helper, pattern, string, count, group_names in cases:
            with self.subTest(
                helper=helper,
                pattern=pattern,
                string=string,
                count=count,
            ):
                assert_callable_replacement_match_parity(
                    backend_name="rebar",
                    backend=rebar,
                    helper=helper,
                    pattern=pattern,
                    string=string,
                    count=count,
                    group_names=group_names,
                    use_compiled_pattern=True,
                )


if __name__ == "__main__":
    unittest.main()
