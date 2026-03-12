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


PRIMARY_FLAG_EXPORTS = [
    "NOFLAG",
    "ASCII",
    "A",
    "IGNORECASE",
    "I",
    "LOCALE",
    "L",
    "MULTILINE",
    "M",
    "DOTALL",
    "S",
    "VERBOSE",
    "X",
    "UNICODE",
    "U",
    "DEBUG",
    "TEMPLATE",
    "T",
]


class RebarExportedSymbolSurfaceTest(unittest.TestCase):
    def test_stdlib_style_exports_are_present(self) -> None:
        exported = set(rebar.__all__)

        self.assertTrue(set(re.__all__).issubset(exported))
        self.assertIs(rebar.RegexFlag, rebar.ASCII.__class__)
        self.assertIs(rebar.error, re.error)
        self.assertIsInstance(rebar.Pattern, type)
        self.assertIsInstance(rebar.Match, type)
        self.assertEqual(rebar.Pattern.__module__, "rebar")
        self.assertEqual(rebar.Match.__module__, "rebar")

    def test_primary_flag_values_match_cpython(self) -> None:
        for name in PRIMARY_FLAG_EXPORTS:
            with self.subTest(name=name):
                self.assertTrue(hasattr(rebar, name))
                self.assertEqual(int(getattr(rebar, name)), int(getattr(re, name)))

        for short_name, long_name in [
            ("A", "ASCII"),
            ("I", "IGNORECASE"),
            ("L", "LOCALE"),
            ("M", "MULTILINE"),
            ("S", "DOTALL"),
            ("X", "VERBOSE"),
            ("U", "UNICODE"),
            ("T", "TEMPLATE"),
        ]:
            with self.subTest(alias=short_name):
                self.assertIs(getattr(rebar, short_name), getattr(rebar, long_name))

    def test_regexflag_members_match_cpython(self) -> None:
        self.assertEqual(
            {member.name: int(member) for member in rebar.RegexFlag},
            {member.name: int(member) for member in re.RegexFlag},
        )

    def test_pattern_and_match_are_non_instantiable_placeholders(self) -> None:
        with self.assertRaisesRegex(TypeError, "cannot create 'rebar.Pattern' instances"):
            rebar.Pattern()
        with self.assertRaisesRegex(TypeError, "cannot create 'rebar.Match' instances"):
            rebar.Match()

    def test_compile_returns_the_exported_pattern_type(self) -> None:
        compiled = rebar.compile("abc")

        self.assertIs(type(compiled), rebar.Pattern)
        self.assertIsInstance(compiled, rebar.Pattern)
        with self.assertRaisesRegex(NotImplementedError, "scaffold placeholder"):
            rebar.search("abc", "abc")


if __name__ == "__main__":
    unittest.main()
