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


class RebarNestedGroupCallableReplacementParityTest(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def _callback_match_snapshot(
        self,
        match: re.Match[str],
        *,
        group_names: tuple[str, ...] = (),
    ) -> dict[str, object]:
        snapshot: dict[str, object] = {
            "string": match.string,
            "pattern": match.re.pattern,
            "group0": match.group(0),
            "groups": match.groups(),
            "groupdict": match.groupdict(),
            "span": match.span(),
            "span1": match.span(1),
            "span2": match.span(2),
            "start1": match.start(1),
            "end1": match.end(1),
            "start2": match.start(2),
            "end2": match.end(2),
            "lastindex": match.lastindex,
            "lastgroup": match.lastgroup,
            "pos": match.pos,
            "endpos": match.endpos,
            "has_regs": hasattr(match, "regs"),
            "regs": tuple(match.regs) if hasattr(match, "regs") else None,
        }

        for group_name in group_names:
            snapshot[f"group:{group_name}"] = match.group(group_name)
            snapshot[f"span:{group_name}"] = match.span(group_name)
            snapshot[f"start:{group_name}"] = match.start(group_name)
            snapshot[f"end:{group_name}"] = match.end(group_name)

        return snapshot

    def _assert_callback_match_parity(
        self,
        *,
        helper: str,
        pattern: str,
        string: str,
        count: int,
        group_names: tuple[str, ...] = (),
        use_compiled_pattern: bool = False,
    ) -> None:
        observed_matches: list[dict[str, object]] = []
        expected_matches: list[dict[str, object]] = []

        def observed_replacement(match: rebar.Match) -> str:
            self.assertIs(type(match), rebar.Match)
            observed_matches.append(
                self._callback_match_snapshot(match, group_names=group_names)
            )
            return "X"

        def expected_replacement(match: re.Match[str]) -> str:
            self.assertIs(type(match), re.Match)
            expected_matches.append(
                self._callback_match_snapshot(match, group_names=group_names)
            )
            return "X"

        if use_compiled_pattern:
            observed_target = rebar.compile(pattern)
            expected_target = re.compile(pattern)
            observed = getattr(observed_target, helper)(
                observed_replacement,
                string,
                count=count,
            )
            expected = getattr(expected_target, helper)(
                expected_replacement,
                string,
                count=count,
            )
        else:
            observed = getattr(rebar, helper)(
                pattern,
                observed_replacement,
                string,
                count=count,
            )
            expected = getattr(re, helper)(
                pattern,
                expected_replacement,
                string,
                count=count,
            )

        self.assertEqual(observed, expected)
        self.assertEqual(observed_matches, expected_matches)

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
                self._assert_callback_match_parity(
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
                self._assert_callback_match_parity(
                    helper=helper,
                    pattern=pattern,
                    string=string,
                    count=count,
                    group_names=group_names,
                    use_compiled_pattern=True,
                )


if __name__ == "__main__":
    unittest.main()
