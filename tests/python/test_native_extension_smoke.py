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
MATURIN = shutil.which("maturin")


def _venv_python(venv_root: pathlib.Path) -> pathlib.Path:
    return venv_root / "bin" / "python"


def _venv_pip(venv_root: pathlib.Path) -> pathlib.Path:
    return venv_root / "bin" / "pip"


class RebarNativeExtensionSmokeTest(unittest.TestCase):
    @unittest.skipUnless(
        MATURIN is not None,
        "native extension smoke requires a maturin executable on PATH",
    )
    def test_built_wheel_imports_native_extension(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rebar-native-smoke-") as temp_dir:
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

            probe = """
import json
import rebar
import rebar._rebar as native

result = {
    "native_module_loaded": rebar.native_module_loaded(),
    "native_scaffold_status": rebar.native_scaffold_status(),
    "native_target_cpython_series": rebar.native_target_cpython_series(),
    "native_private_flag": getattr(native, "__rebar_scaffold__", False),
    "native_module_name": native.__name__,
}

try:
    rebar.compile("abc")
except Exception as exc:
    result["compile_exception_type"] = type(exc).__name__
    result["compile_exception_message"] = str(exc)
else:
    result["compile_exception_type"] = None
    result["compile_exception_message"] = None

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
            self.assertEqual(result["native_scaffold_status"], "scaffold-only")
            self.assertEqual(result["native_target_cpython_series"], "3.12.x")
            self.assertTrue(result["native_private_flag"])
            self.assertEqual(result["native_module_name"], "rebar._rebar")
            self.assertEqual(result["compile_exception_type"], "NotImplementedError")
            self.assertIn("not implemented yet", result["compile_exception_message"])


if __name__ == "__main__":
    unittest.main()
