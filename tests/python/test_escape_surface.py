from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar
from tests.python.native_wheel_test_support import MATURIN, build_and_install_rebar_wheel


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

    @unittest.skipUnless(
        MATURIN is not None,
        "native extension surface smoke requires a maturin executable on PATH",
    )
    def test_built_wheel_keeps_escape_behavior(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rebar-escape-surface-") as temp_dir:
            temp_root = pathlib.Path(temp_dir)
            python_bin = build_and_install_rebar_wheel(self, temp_root=temp_root)

            probe = r"""
import json
import rebar

result = {
    "native_module_loaded": rebar.native_module_loaded(),
    "escaped_str": rebar.escape(' !"#%&,/:;<=>@`~'),
    "escaped_bytes": rebar.escape(b'a-b.c'),
}

print(json.dumps(result))
"""
            completed = subprocess.run(
                [str(python_bin), "-c", probe],
                cwd=temp_root,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)

            self.assertTrue(result["native_module_loaded"])
            self.assertEqual(result["escaped_str"], '\\ !"\\#%\\&,/:;<=>@`\\~')
            self.assertEqual(result["escaped_bytes"], "a\\-b\\.c")


if __name__ == "__main__":
    unittest.main()
