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


PLACEHOLDER_CASES = [
    ("compile", ("abc",), {}),
    ("search", ("abc", "abc"), {}),
    ("match", ("abc", "abc"), {}),
    ("fullmatch", ("abc", "abc"), {}),
    ("split", ("abc", "abc"), {}),
    ("findall", ("abc", "abc"), {}),
    ("finditer", ("abc", "abc"), {}),
    ("sub", ("abc", "x", "abc"), {}),
    ("subn", ("abc", "x", "abc"), {}),
    ("escape", ("abc",), {}),
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
    "escape",
    "purge",
}


def _venv_python(venv_root: pathlib.Path) -> pathlib.Path:
    return venv_root / "bin" / "python"


def _venv_pip(venv_root: pathlib.Path) -> pathlib.Path:
    return venv_root / "bin" / "pip"


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

    def test_source_package_purge_is_safe_noop(self) -> None:
        self.assertIsNone(rebar.purge())
        self.assertIsNone(rebar.purge())

    @unittest.skipUnless(
        MATURIN is not None,
        "native extension surface smoke requires a maturin executable on PATH",
    )
    def test_built_wheel_keeps_surface_and_native_signal(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rebar-module-surface-") as temp_dir:
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

cases = {
    "compile": [["abc"], {}],
    "search": [["abc", "abc"], {}],
    "match": [["abc", "abc"], {}],
    "fullmatch": [["abc", "abc"], {}],
    "split": [["abc", "abc"], {}],
    "findall": [["abc", "abc"], {}],
    "finditer": [["abc", "abc"], {}],
    "sub": [["abc", "x", "abc"], {}],
    "subn": [["abc", "x", "abc"], {}],
    "escape": [["abc"], {}],
}

result = {
    "native_module_loaded": rebar.native_module_loaded(),
    "native_scaffold_status": rebar.native_scaffold_status(),
    "exported_helpers_present": all(hasattr(rebar, name) for name in sorted(cases) + ["purge"]),
    "purge_result": rebar.purge(),
}

exceptions = {}
for name, (args, kwargs) in cases.items():
    helper = getattr(rebar, name)
    try:
        helper(*args, **kwargs)
    except Exception as exc:
        exceptions[name] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
    else:
        exceptions[name] = None

result["exceptions"] = exceptions
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
            self.assertTrue(result["exported_helpers_present"])
            self.assertIsNone(result["purge_result"])

            for helper_name in EXPECTED_HELPERS - {"purge"}:
                with self.subTest(helper=helper_name):
                    exception_payload = result["exceptions"][helper_name]
                    self.assertEqual(exception_payload["type"], "NotImplementedError")
                    self.assertIn(
                        f"rebar.{helper_name}() is a scaffold placeholder",
                        exception_payload["message"],
                    )


if __name__ == "__main__":
    unittest.main()
