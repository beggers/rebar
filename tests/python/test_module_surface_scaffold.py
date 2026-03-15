from __future__ import annotations

import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar


PLACEHOLDER_CASES = [
    ("template", ("abc",), {}),
]

EXPECTED_HELPERS = {
    "compile",
    "search",
    "match",
    "fullmatch",
    "split",
    "findall",
    "finditer",
    "sub",
    "subn",
    "template",
    "escape",
    "purge",
}


class RebarModuleSurfaceScaffoldTest(unittest.TestCase):
    def test_source_package_exports_helper_surface(self) -> None:
        exported = set(rebar.__all__)

        self.assertTrue(EXPECTED_HELPERS.issubset(exported))
        for helper_name in EXPECTED_HELPERS:
            self.assertTrue(callable(getattr(rebar, helper_name)))

    def test_source_package_placeholders_fail_loudly(self) -> None:
        for helper_name, args, kwargs in PLACEHOLDER_CASES:
            with self.subTest(helper=helper_name):
                helper = getattr(rebar, helper_name)
                with self.assertRaises(NotImplementedError) as raised:
                    helper(*args, **kwargs)
                self.assertIn(
                    f"rebar.{helper_name}() is a scaffold placeholder",
                    str(raised.exception),
                )

    def test_source_package_compile_returns_pattern_scaffold(self) -> None:
        compiled = rebar.compile("abc", rebar.IGNORECASE)

        self.assertIs(type(compiled), rebar.Pattern)
        self.assertEqual(compiled.pattern, "abc")
        self.assertEqual(compiled.flags, int(rebar.IGNORECASE | rebar.UNICODE))
        self.assertEqual(compiled.groups, 0)
        self.assertEqual(compiled.groupindex, {})

    def test_source_package_literal_helpers_return_match_objects(self) -> None:
        search_match = rebar.search("abc", "zzabczz")
        self.assertIs(type(search_match), rebar.Match)
        self.assertEqual(search_match.group(0), "abc")
        self.assertEqual(search_match.span(), (2, 5))

        anchored_match = rebar.match("abc", "abcdef")
        self.assertIs(type(anchored_match), rebar.Match)
        self.assertEqual(anchored_match.group(0), "abc")
        self.assertEqual(anchored_match.span(), (0, 3))

        full_match = rebar.fullmatch("abc", "abc")
        self.assertIs(type(full_match), rebar.Match)
        self.assertEqual(full_match.group(0), "abc")
        self.assertEqual(full_match.span(), (0, 3))

        self.assertIsNone(rebar.search("abc", "zzz"))
        self.assertIsNone(rebar.match("abc", "zabc"))
        self.assertIsNone(rebar.fullmatch("abc", "abcz"))

    def test_source_package_escape_returns_escaped_payload(self) -> None:
        self.assertEqual(rebar.escape("a-b.c"), "a\\-b\\.c")
        self.assertEqual(rebar.escape(b"a-b.c"), b"a\\-b\\.c")

    def test_source_package_purge_is_safe_noop(self) -> None:
        self.assertIsNone(rebar.purge())
        self.assertIsNone(rebar.purge())


if __name__ == "__main__":
    unittest.main()
