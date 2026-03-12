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
        if pattern == "boom":
            raise stdlib_re.error("native compile failure", pattern, 2)
        return ("compiled", 4098 if isinstance(pattern, str) else 2050, True)

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
        if pattern == "unsupported":
            return ("unsupported", 0, len(string), None)
        return ("matched", 1, len(string) - 1, (1, 4))

    def boundary_escape(self, pattern: str | bytes) -> str | bytes:
        self.calls.append(("escape", pattern))
        if isinstance(pattern, bytes):
            return b"native:" + pattern
        return f"native:{pattern}"

    def scaffold_raise(self, helper_name: str) -> object:
        raise NotImplementedError(f"native helper placeholder {helper_name}")

    def scaffold_pattern_raise(self, method_name: str) -> object:
        raise NotImplementedError(f"native pattern placeholder {method_name}")

    def scaffold_purge(self) -> None:
        self.calls.append(("purge",))


class RebarRustCompileMatchBoundaryTest(unittest.TestCase):
    def tearDown(self) -> None:
        rebar.purge()

    def test_compile_match_and_escape_use_native_boundary_hooks(self) -> None:
        fake_native = _FakeNativeBoundary()

        with mock.patch.object(rebar, "_native", fake_native):
            rebar.purge()

            compiled = rebar.compile("abc", rebar.IGNORECASE)
            self.assertEqual(compiled.flags, 4098)

            match = compiled.search("zabczz")
            self.assertIs(type(match), rebar.Match)
            self.assertEqual(match.span(), (1, 4))
            self.assertEqual(match.pos, 1)
            self.assertEqual(match.endpos, 5)
            self.assertEqual(match.group(0), "abc")

            self.assertEqual(rebar.escape("a-b"), "native:a-b")
            self.assertEqual(rebar.escape(b"a-b"), b"native:a-b")

        self.assertEqual(
            fake_native.calls,
            [
                ("purge",),
                ("compile", "abc", int(rebar.IGNORECASE)),
                ("match", "abc", 4098, "search", "zabczz", 0, None),
                ("escape", "a-b"),
                ("escape", b"a-b"),
            ],
        )

    def test_compile_surfaces_native_re_error(self) -> None:
        fake_native = _FakeNativeBoundary()

        with mock.patch.object(rebar, "_native", fake_native):
            with self.assertRaises(rebar.error) as raised:
                rebar.compile("boom")

        self.assertEqual(type(raised.exception), stdlib_re.error)
        self.assertEqual(str(raised.exception), "native compile failure at position 2")
        self.assertEqual(fake_native.calls, [("compile", "boom", 0)])

    def test_pattern_placeholder_comes_from_native_boundary(self) -> None:
        fake_native = _FakeNativeBoundary()

        with mock.patch.object(rebar, "_native", fake_native):
            compiled = rebar.compile("unsupported")
            with self.assertRaises(NotImplementedError) as raised:
                compiled.search("unsupported")

        self.assertEqual(str(raised.exception), "native pattern placeholder search")
        self.assertEqual(
            fake_native.calls,
            [
                ("compile", "unsupported", 0),
                ("match", "unsupported", 4098, "search", "unsupported", 0, None),
            ],
        )


if __name__ == "__main__":
    unittest.main()
