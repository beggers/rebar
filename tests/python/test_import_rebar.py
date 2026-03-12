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
        self.assertIsInstance(rebar.native_module_loaded(), bool)
        if rebar.native_module_loaded():
            self.assertEqual(rebar.native_scaffold_status(), "scaffold-only")
            self.assertEqual(rebar.native_target_cpython_series(), "3.12.x")
        else:
            self.assertIsNone(rebar.native_scaffold_status())
            self.assertIsNone(rebar.native_target_cpython_series())

    def test_compile_returns_pattern_scaffold(self) -> None:
        compiled = rebar.compile("abc")

        self.assertIs(type(compiled), rebar.Pattern)
        self.assertEqual(compiled.pattern, "abc")
        self.assertEqual(compiled.flags, int(rebar.UNICODE))
        self.assertEqual(compiled.groups, 0)
        self.assertEqual(compiled.groupindex, {})


if __name__ == "__main__":
    unittest.main()
