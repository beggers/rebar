from __future__ import annotations

import pathlib
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
        normalized_flags = 4096 if isinstance(pattern, bytes) else 8192
        return ("compiled", normalized_flags, True)

    def boundary_literal_split(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        maxsplit: int,
    ) -> tuple[str, list[str] | list[bytes] | None]:
        self.calls.append(("split", pattern, flags, string, maxsplit))
        if isinstance(pattern, bytes):
            return ("supported", [b"native-bytes-split"])
        return ("supported", ["native-split"])

    def boundary_literal_findall(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, list[str] | list[bytes] | None]:
        self.calls.append(("findall", pattern, flags, string, pos, endpos))
        if pattern == "unsupported" or flags == int(rebar.IGNORECASE):
            return ("unsupported", None)
        if isinstance(pattern, bytes):
            return ("supported", [b"native-bytes-findall"])
        return ("supported", ["native-findall"])

    def boundary_literal_finditer(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, int, int, list[tuple[int, int]]]:
        self.calls.append(("finditer", pattern, flags, string, pos, endpos))
        if pattern == "unsupported":
            return ("unsupported", 0, 0, [])
        return ("supported", 1, 6, [(2, 5)])

    def boundary_literal_subn(
        self,
        pattern: str | bytes,
        flags: int,
        repl: str | bytes,
        string: str | bytes,
        count: int,
    ) -> tuple[str, str | bytes | None, int]:
        self.calls.append(("subn", pattern, flags, repl, string, count))
        if pattern == "unsupported":
            return ("unsupported", None, 0)
        if isinstance(pattern, bytes):
            return ("supported", b"native-bytes-subn", 7)
        return ("supported", "native-subn", 9)

    def scaffold_raise(self, helper_name: str) -> object:
        raise NotImplementedError(rebar._placeholder_message(helper_name))

    def scaffold_pattern_raise(self, method_name: str) -> object:
        raise NotImplementedError(rebar._pattern_placeholder_message(method_name))

    def scaffold_purge(self) -> None:
        self.calls.append(("purge",))


class RebarRustCollectionReplacementBoundaryTest(unittest.TestCase):
    def tearDown(self) -> None:
        rebar.purge()

    def test_collection_and_replacement_helpers_use_native_boundary_hooks(self) -> None:
        fake_native = _FakeNativeBoundary()

        with mock.patch.object(rebar, "_native", fake_native):
            rebar.purge()

            self.assertEqual(rebar.split("abc", "zzabczz", maxsplit=1), ["native-split"])

            pattern = rebar.compile("abc")
            self.assertEqual(pattern.flags, 8192)
            self.assertEqual(pattern.findall("zzabczz", 2, 5), ["native-findall"])

            iterator = rebar.finditer("abc", "zzabczz")
            matches = list(iterator)
            self.assertEqual([match.group(0) for match in matches], ["abc"])
            self.assertEqual([match.span() for match in matches], [(2, 5)])
            self.assertEqual([match.pos for match in matches], [1])
            self.assertEqual([match.endpos for match in matches], [6])

            self.assertEqual(pattern.sub("x", "abcabc"), "native-subn")
            self.assertEqual(rebar.subn("abc", "x", "abcabc", count=1), ("native-subn", 9))

            bytes_pattern = rebar.compile(b"abc")
            self.assertEqual(bytes_pattern.split(b"zzabczz"), [b"native-bytes-split"])
            self.assertEqual(rebar.subn(b"abc", b"x", b"abcabc"), (b"native-bytes-subn", 7))

        self.assertEqual(
            fake_native.calls,
            [
                ("purge",),
                ("compile", "abc", 0),
                ("split", "abc", 8192, "zzabczz", 1),
                ("compile", "abc", 0),
                ("findall", "abc", 8192, "zzabczz", 2, 5),
                ("compile", "abc", 0),
                ("finditer", "abc", 8192, "zzabczz", 0, None),
                ("subn", "abc", 8192, "x", "abcabc", 0),
                ("compile", "abc", 0),
                ("subn", "abc", 8192, "x", "abcabc", 1),
                ("compile", b"abc", 0),
                ("split", b"abc", 4096, b"zzabczz", 0),
                ("compile", b"abc", 0),
                ("subn", b"abc", 4096, b"x", b"abcabc", 0),
            ],
        )

    def test_module_and_pattern_placeholders_still_surface_for_unsupported_native_results(self) -> None:
        fake_native = _FakeNativeBoundary()

        with mock.patch.object(rebar, "_native", fake_native):
            with self.assertRaises(NotImplementedError) as module_raised:
                rebar.findall("unsupported", "unsupported")
            self.assertIn("rebar.findall() is a scaffold placeholder", str(module_raised.exception))

            pattern = rebar.compile("unsupported")
            with self.assertRaises(NotImplementedError) as pattern_raised:
                list(pattern.finditer("unsupported"))
            self.assertIn(
                "rebar.Pattern.finditer() is a scaffold placeholder",
                str(pattern_raised.exception),
            )


if __name__ == "__main__":
    unittest.main()
