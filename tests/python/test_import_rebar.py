from __future__ import annotations

import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar


class RebarImportSmokeTest(unittest.TestCase):
    def test_import_exposes_scaffold_metadata(self) -> None:
        self.assertEqual(rebar.TARGET_CPYTHON_SERIES, "3.12.x")
        self.assertEqual(rebar.SCAFFOLD_STATUS, "scaffold-only")
        self.assertEqual(rebar.NATIVE_MODULE_NAME, "rebar._rebar")
        self.assertFalse(rebar.native_module_loaded())

    def test_placeholder_compile_fails_loudly(self) -> None:
        with self.assertRaisesRegex(NotImplementedError, "scaffold placeholder"):
            rebar.compile("abc")


if __name__ == "__main__":
    unittest.main()
