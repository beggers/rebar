from __future__ import annotations

import pathlib
import re as stdlib_re
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar


class RebarConditionalGroupExistsAssertionDiagnosticParityTest(unittest.TestCase):
    def setUp(self) -> None:
        rebar.purge()

    def tearDown(self) -> None:
        rebar.purge()

    @unittest.skipUnless(
        rebar.native_module_loaded(),
        "conditional group-exists assertion diagnostics require rebar._rebar",
    )
    def test_compile_matches_cpython_for_published_assertion_condition_diagnostics(self) -> None:
        for pattern in ("a(?(?=b)b|c)d", "a(?(?!b)b|c)d"):
            with self.subTest(pattern=pattern):
                with self.assertRaises(stdlib_re.error) as expected:
                    stdlib_re.compile(pattern)

                with self.assertRaises(rebar.error) as actual:
                    rebar.compile(pattern)

                self.assertEqual(type(actual.exception), type(expected.exception))
                self.assertEqual(str(actual.exception), str(expected.exception))
                self.assertEqual(actual.exception.pos, expected.exception.pos)
                self.assertEqual(actual.exception.lineno, expected.exception.lineno)
                self.assertEqual(actual.exception.colno, expected.exception.colno)


if __name__ == "__main__":
    unittest.main()
