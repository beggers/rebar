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
        return ("compiled", int(rebar.IGNORECASE | rebar.UNICODE), False)

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
        if pattern == "(?i)abc" and mode == "search" and string == "ABC":
            return ("matched", 0, len(string), (0, 3))
        return ("unsupported", 0, len(string), None)

    def scaffold_raise(self, helper_name: str) -> object:
        raise NotImplementedError(rebar._placeholder_message(helper_name))

    def scaffold_pattern_raise(self, method_name: str) -> object:
        raise NotImplementedError(rebar._pattern_placeholder_message(method_name))

    def scaffold_purge(self) -> None:
        self.calls.append(("purge",))


class RebarInlineFlagLiteralWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_native_boundary_handles_bounded_inline_flag_search_wrappers(self) -> None:
        fake_native = _FakeNativeBoundary()

        with mock.patch.object(rebar, "_native", fake_native):
            rebar.purge()

            match = rebar.search("(?i)abc", "ABC")
            self.assertIs(type(match), rebar.Match)
            self.assertEqual(match.group(0), "ABC")
            self.assertEqual(match.span(), (0, 3))

            compiled = rebar.compile("(?i)abc")
            self.assertEqual(compiled.flags, int(rebar.IGNORECASE | rebar.UNICODE))
            self.assertEqual(compiled.search("ABC").span(), (0, 3))

        self.assertEqual(
            fake_native.calls,
            [
                ("purge",),
                ("compile", "(?i)abc", 0),
                ("match", "(?i)abc", int(rebar.IGNORECASE | rebar.UNICODE), "search", "ABC", 0, None),
                ("compile", "(?i)abc", 0),
                ("match", "(?i)abc", int(rebar.IGNORECASE | rebar.UNICODE), "search", "ABC", 0, None),
            ],
        )

    @unittest.skipUnless(rebar.native_module_loaded(), "native extension not available in source-tree test mode")
    def test_built_native_inline_flag_search_matches_cpython(self) -> None:
        expected = stdlib_re.search("(?i)abc", "ABC")
        observed = rebar.search("(?i)abc", "ABC")

        self.assertIs(type(observed), rebar.Match)
        self.assertEqual(observed.group(0), expected.group(0))
        self.assertEqual(observed.span(), expected.span())

        compiled = rebar.compile("(?i)abc")
        self.assertEqual(compiled.flags, expected.re.flags)
        self.assertEqual(compiled.search("ABC").span(), expected.span())


if __name__ == "__main__":
    unittest.main()
