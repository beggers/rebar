from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
MATURIN = shutil.which("maturin")

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


def _venv_python(venv_root: pathlib.Path) -> pathlib.Path:
    return venv_root / "bin" / "python"


def _venv_pip(venv_root: pathlib.Path) -> pathlib.Path:
    return venv_root / "bin" / "pip"


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
            venv_root = temp_root / "venv"
            wheelhouse = temp_root / "wheelhouse"

            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_root)],
                cwd=REPO_ROOT,
                check=True,
            )

            python_bin = _venv_python(venv_root)
            pip_bin = _venv_pip(venv_root)
            wheelhouse.mkdir()

            build_env = os.environ.copy()
            build_env["PATH"] = f"{pathlib.Path(MATURIN).parent}{os.pathsep}{build_env['PATH']}"

            subprocess.run(
                [
                    MATURIN,
                    "build",
                    "--manifest-path",
                    "crates/rebar-cpython/Cargo.toml",
                    "--interpreter",
                    str(python_bin),
                    "--out",
                    str(wheelhouse),
                ],
                cwd=REPO_ROOT,
                check=True,
                env=build_env,
            )

            wheels = sorted(wheelhouse.glob("rebar-*.whl"))
            self.assertEqual(len(wheels), 1, f"expected one built wheel, found {wheels}")

            subprocess.run(
                [str(pip_bin), "install", str(wheels[0])],
                cwd=REPO_ROOT,
                check=True,
            )

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
