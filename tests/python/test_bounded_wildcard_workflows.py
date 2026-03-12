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


class _FakeNativeBoundary:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def boundary_compile(self, pattern: str | bytes, flags: int) -> tuple[str, int, bool]:
        self.calls.append(("compile", pattern, flags))
        return ("compiled", 34, False)

    def boundary_literal_match(
        self,
        pattern: str | bytes,
        flags: int,
        mode: str,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, int, int, tuple[int, int] | None]:
        self.calls.append(("match", pattern, flags, mode, string, pos, endpos))
        return ("matched", 0, len(string), (0, 3))

    def boundary_literal_findall(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, list[str] | list[bytes]]:
        self.calls.append(("findall", pattern, flags, string, pos, endpos))
        return ("supported", ["abc"])

    def scaffold_raise(self, helper_name: str) -> object:
        raise NotImplementedError(rebar._placeholder_message(helper_name))

    def scaffold_pattern_raise(self, method_name: str) -> object:
        raise NotImplementedError(rebar._pattern_placeholder_message(method_name))

    def scaffold_purge(self) -> None:
        self.calls.append(("purge",))


class RebarBoundedWildcardWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_bounded_single_dot_matches_published_module_cases(self) -> None:
        findall_result = rebar.findall("a.c", "abc")
        self.assertEqual(findall_result, stdlib_re.findall("a.c", "abc"))

        search_result = rebar.search("a.c", "ABC", rebar.IGNORECASE)
        expected_search = stdlib_re.search("a.c", "ABC", stdlib_re.IGNORECASE)
        self.assertIs(type(search_result), rebar.Match)
        self.assertEqual(search_result.group(0), expected_search.group(0))
        self.assertEqual(search_result.span(), expected_search.span())

        compiled = rebar.compile("a.c")
        self.assertIs(compiled, rebar.compile("a.c"))
        self.assertEqual(compiled.findall("zabcaxc"), ["abc", "axc"])

    def test_other_nonliteral_patterns_stay_unsupported(self) -> None:
        with self.assertRaises(NotImplementedError) as module_raised:
            rebar.search("[ab]c", "abc")
        self.assertIn("rebar.compile() is a scaffold placeholder", str(module_raised.exception))

        compiled = rebar.compile("a.c")
        unsupported = rebar.compile("abc", rebar.IGNORECASE)
        with self.assertRaises(NotImplementedError) as pattern_raised:
            unsupported.findall("ABC")
        self.assertIn("rebar.Pattern.findall() is a scaffold placeholder", str(pattern_raised.exception))

        self.assertIs(compiled, rebar.compile("a.c"))

    def test_native_boundary_handles_bounded_single_dot_wrappers(self) -> None:
        fake_native = _FakeNativeBoundary()

        with mock.patch.object(rebar, "_native", fake_native):
            rebar.purge()

            search_match = rebar.search("a.c", "ABC", rebar.IGNORECASE)
            self.assertEqual(search_match.span(), (0, 3))
            self.assertEqual(rebar.findall("a.c", "abc"), ["abc"])

        self.assertEqual(
            fake_native.calls,
            [
                ("purge",),
                ("compile", "a.c", int(rebar.IGNORECASE)),
                ("match", "a.c", 34, "search", "ABC", 0, None),
                ("compile", "a.c", 0),
                ("findall", "a.c", 34, "abc", 0, None),
            ],
        )


if __name__ == "__main__":
    unittest.main()
