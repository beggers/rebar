from __future__ import annotations

import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar


STR_CASES = [
    ("", ""),
    ("abc_123", "abc_123"),
    (".^$*+?{}[]\\|()", "\\.\\^\\$\\*\\+\\?\\{\\}\\[\\]\\\\\\|\\(\\)"),
    (' !"#%&,/:;<=>@`~', '\\ !"\\#%\\&,/:;<=>@`\\~'),
    (" \t\n\r\x0b\x0c", "\\ \\\t\\\n\\\r\\\x0b\\\x0c"),
    ("a-b", "a\\-b"),
]

BYTES_CASES = [
    (b"", b""),
    (b"abc_123", b"abc_123"),
    (br".^$*+?{}[]\|()", b"\\.\\^\\$\\*\\+\\?\\{\\}\\[\\]\\\\\\|\\(\\)"),
    (b' !"#%&,/:;<=>@`~', b'\\ !"\\#%\\&,/:;<=>@`\\~'),
    (b" \t\n\r\x0b\x0c", b"\\ \\\t\\\n\\\r\\\x0b\\\x0c"),
    (b"a-b", b"a\\-b"),
]


class RebarEscapeSurfaceTest(unittest.TestCase):
    def test_escape_preserves_cpython_str_cases(self) -> None:
        for raw, expected in STR_CASES:
            with self.subTest(raw=raw):
                escaped = rebar.escape(raw)
                self.assertIs(type(escaped), str)
                self.assertEqual(escaped, expected)

    def test_escape_preserves_cpython_bytes_cases(self) -> None:
        for raw, expected in BYTES_CASES:
            with self.subTest(raw=raw):
                escaped = rebar.escape(raw)
                self.assertIs(type(escaped), bytes)
                self.assertEqual(escaped, expected)


if __name__ == "__main__":
    unittest.main()
