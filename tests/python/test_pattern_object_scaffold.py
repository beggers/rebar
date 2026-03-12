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


def _venv_python(venv_root: pathlib.Path) -> pathlib.Path:
    return venv_root / "bin" / "python"


def _venv_pip(venv_root: pathlib.Path) -> pathlib.Path:
    return venv_root / "bin" / "pip"


class RebarPatternObjectScaffoldTest(unittest.TestCase):
    def test_compile_returns_pattern_scaffold_with_pinned_attributes(self) -> None:
        pattern = rebar.compile("abc", rebar.IGNORECASE)

        self.assertIs(type(pattern), rebar.Pattern)
        self.assertEqual(pattern.pattern, "abc")
        self.assertEqual(pattern.flags, int(rebar.IGNORECASE | rebar.UNICODE))
        self.assertEqual(pattern.groups, 0)
        self.assertEqual(pattern.groupindex, {})

        bytes_pattern = rebar.compile(b"abc", rebar.IGNORECASE)
        self.assertEqual(bytes_pattern.pattern, b"abc")
        self.assertEqual(bytes_pattern.flags, int(rebar.IGNORECASE))
        self.assertEqual(bytes_pattern.groups, 0)
        self.assertEqual(bytes_pattern.groupindex, {})

    def test_compile_reuses_existing_pattern_without_reprocessing_flags(self) -> None:
        pattern = rebar.compile("abc")

        self.assertIs(rebar.compile(pattern), pattern)
        with self.assertRaisesRegex(ValueError, "cannot process flags argument with a compiled pattern"):
            rebar.compile(pattern, rebar.IGNORECASE)

    def test_compile_rejects_non_pattern_inputs(self) -> None:
        with self.assertRaisesRegex(TypeError, "first argument must be string or compiled pattern"):
            rebar.compile(123)

    def test_pattern_literal_methods_return_match_objects(self) -> None:
        pattern = rebar.compile("abc")

        search_match = pattern.search("zzabczz")
        self.assertIs(type(search_match), rebar.Match)
        self.assertEqual(search_match.group(0), "abc")
        self.assertEqual(search_match.span(), (2, 5))

        anchored_match = pattern.match("abcdef")
        self.assertIs(type(anchored_match), rebar.Match)
        self.assertEqual(anchored_match.group(0), "abc")
        self.assertEqual(anchored_match.span(), (0, 3))

        full_match = pattern.fullmatch("abc")
        self.assertIs(type(full_match), rebar.Match)
        self.assertEqual(full_match.group(0), "abc")
        self.assertEqual(full_match.span(), (0, 3))

        self.assertIsNone(pattern.search("zzz"))
        self.assertIsNone(pattern.match("zabc"))
        self.assertIsNone(pattern.fullmatch("abcz"))

    def test_pattern_literal_methods_stay_placeholder_for_unsupported_flags(self) -> None:
        pattern = rebar.compile("abc", rebar.IGNORECASE | rebar.ASCII)

        for method_name in ("search", "match", "fullmatch"):
            with self.subTest(method=method_name):
                with self.assertRaises(NotImplementedError) as raised:
                    getattr(pattern, method_name)("abc")
                self.assertIn(
                    f"rebar.Pattern.{method_name}() is a scaffold placeholder",
                    str(raised.exception),
                )

    @unittest.skipUnless(
        MATURIN is not None,
        "native pattern scaffold smoke requires a maturin executable on PATH",
    )
    def test_built_wheel_keeps_pattern_scaffold_contract(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rebar-pattern-scaffold-") as temp_dir:
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

compiled = rebar.compile("abc", rebar.IGNORECASE)

result = {
    "native_module_loaded": rebar.native_module_loaded(),
    "pattern_type_name": type(compiled).__name__,
    "pattern_type_module": type(compiled).__module__,
    "pattern_value": compiled.pattern,
    "flags": compiled.flags,
    "groups": compiled.groups,
    "groupindex": compiled.groupindex,
}

try:
    compiled.search("abc")
except Exception as exc:
    result["search_exception_type"] = type(exc).__name__
    result["search_exception_message"] = str(exc)
else:
    result["search_exception_type"] = None
    result["search_exception_message"] = None
    result["search_result"] = {
        "type_name": type(compiled.search("abc")).__name__,
        "group0": compiled.search("abc").group(0),
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
            self.assertEqual(result["pattern_type_name"], "Pattern")
            self.assertEqual(result["pattern_type_module"], "re")
            self.assertEqual(result["pattern_value"], "abc")
            self.assertEqual(result["flags"], int(rebar.IGNORECASE | rebar.UNICODE))
            self.assertEqual(result["groups"], 0)
            self.assertEqual(result["groupindex"], {})
            self.assertIsNone(result["search_exception_type"])
            self.assertIsNone(result["search_exception_message"])
            self.assertEqual(
                result["search_result"],
                {
                    "type_name": "Match",
                    "group0": "abc",
                },
            )


if __name__ == "__main__":
    unittest.main()
