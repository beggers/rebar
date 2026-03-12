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
        return ("compiled", flags, True)

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
        if pattern == b"abc" and flags == int(rebar.LOCALE) and string == b"abc":
            return ("matched", 0, len(string), (0, 3))
        return ("unsupported", 0, len(string), None)

    def scaffold_raise(self, helper_name: str) -> object:
        raise NotImplementedError(rebar._placeholder_message(helper_name))

    def scaffold_pattern_raise(self, method_name: str) -> object:
        raise NotImplementedError(rebar._pattern_placeholder_message(method_name))

    def scaffold_purge(self) -> None:
        self.calls.append(("purge",))


class RebarLocaleBytesLiteralWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    def test_native_boundary_handles_bytes_locale_literal_search_wrappers(self) -> None:
        fake_native = _FakeNativeBoundary()

        with mock.patch.object(rebar, "_native", fake_native):
            rebar.purge()

            match = rebar.search(b"abc", b"abc", rebar.LOCALE)
            self.assertIs(type(match), rebar.Match)
            self.assertEqual(match.group(0), b"abc")
            self.assertEqual(match.span(), (0, 3))

            compiled = rebar.compile(b"abc", rebar.LOCALE)
            self.assertEqual(compiled.flags, int(rebar.LOCALE))
            self.assertEqual(compiled.search(b"abc").span(), (0, 3))

        self.assertEqual(
            fake_native.calls,
            [
                ("purge",),
                ("compile", b"abc", int(rebar.LOCALE)),
                ("match", b"abc", int(rebar.LOCALE), "search", b"abc", 0, None),
                ("match", b"abc", int(rebar.LOCALE), "search", b"abc", 0, None),
            ],
        )

    @unittest.skipUnless(rebar.native_module_loaded(), "native extension not available in source-tree test mode")
    def test_built_native_locale_bytes_search_matches_cpython(self) -> None:
        expected = stdlib_re.search(b"abc", b"abc", stdlib_re.LOCALE)
        observed = rebar.search(b"abc", b"abc", rebar.LOCALE)

        self.assertIs(type(observed), rebar.Match)
        self.assertEqual(observed.group(0), expected.group(0))
        self.assertEqual(observed.span(), expected.span())

        compiled = rebar.compile(b"abc", rebar.LOCALE)
        self.assertEqual(compiled.flags, expected.re.flags)
        self.assertEqual(compiled.search(b"abc").span(), expected.span())

    @unittest.skipUnless(rebar.native_module_loaded(), "native extension not available in source-tree test mode")
    def test_locale_bytes_workflow_does_not_regress_inline_flag_parser_diagnostics(self) -> None:
        with self.assertRaises(stdlib_re.error) as expected:
            stdlib_re.compile("(?L:a)")

        with self.assertRaises(rebar.error) as observed:
            rebar.compile("(?L:a)")

        self.assertEqual(type(observed.exception), type(expected.exception))
        self.assertEqual(str(observed.exception), str(expected.exception))
        self.assertEqual(observed.exception.pos, expected.exception.pos)


if __name__ == "__main__":
    unittest.main()
