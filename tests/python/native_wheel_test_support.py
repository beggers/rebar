from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import os
import pathlib
import shutil
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

from rebar_harness import benchmarks

MATURIN = shutil.which("maturin")


@contextmanager
def built_native_runtime(
    testcase: unittest.TestCase,
) -> Iterator[tuple[pathlib.Path, dict[str, str]]]:
    provisioned, temp_dir, error = benchmarks.provision_built_native_runtime()
    testcase.assertIsNotNone(provisioned, error)
    testcase.assertIsNotNone(temp_dir, error)
    assert provisioned is not None
    assert temp_dir is not None

    # Keep the installed wheel ahead of the source tree so probe subprocesses
    # exercise the built native artifact instead of the checkout shim.
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        str(path) for path in (provisioned["install_root"], PYTHON_SOURCE)
    )

    try:
        yield pathlib.Path(sys.executable), env
    finally:
        temp_dir.cleanup()
