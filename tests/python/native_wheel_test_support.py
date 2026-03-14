from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
MATURIN = shutil.which("maturin")


def _venv_bin(venv_root: pathlib.Path, executable: str) -> pathlib.Path:
    return venv_root / "bin" / executable


def build_and_install_rebar_wheel(
    testcase: unittest.TestCase,
    *,
    temp_root: pathlib.Path,
) -> pathlib.Path:
    if MATURIN is None:
        raise AssertionError("maturin executable required to build the native wheel")

    venv_root = temp_root / "venv"
    wheelhouse = temp_root / "wheelhouse"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_root)],
        cwd=REPO_ROOT,
        check=True,
    )

    python_bin = _venv_bin(venv_root, "python")
    pip_bin = _venv_bin(venv_root, "pip")
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
    testcase.assertEqual(len(wheels), 1, f"expected one built wheel, found {wheels}")

    subprocess.run(
        [str(pip_bin), "install", str(wheels[0])],
        cwd=REPO_ROOT,
        check=True,
    )

    return python_bin
