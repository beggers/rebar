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
    ("split", ("abc", "abc"), {}),
    ("findall", ("abc", "abc"), {}),
    ("finditer", ("abc", "abc"), {}),
    ("sub", ("abc", "x", "abc"), {}),
    ("subn", ("abc", "x", "abc"), {}),
    ("template", ("abc",), {}),
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
    "template",
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

    def test_source_package_compile_returns_pattern_scaffold(self) -> None:
        compiled = rebar.compile("abc", rebar.IGNORECASE)

        self.assertIs(type(compiled), rebar.Pattern)
        self.assertEqual(compiled.pattern, "abc")
        self.assertEqual(compiled.flags, int(rebar.IGNORECASE | rebar.UNICODE))
        self.assertEqual(compiled.groups, 0)
        self.assertEqual(compiled.groupindex, {})

    def test_source_package_literal_helpers_return_match_objects(self) -> None:
        search_match = rebar.search("abc", "zzabczz")
        self.assertIs(type(search_match), rebar.Match)
        self.assertEqual(search_match.group(0), "abc")
        self.assertEqual(search_match.span(), (2, 5))

        anchored_match = rebar.match("abc", "abcdef")
        self.assertIs(type(anchored_match), rebar.Match)
        self.assertEqual(anchored_match.group(0), "abc")
        self.assertEqual(anchored_match.span(), (0, 3))

        full_match = rebar.fullmatch("abc", "abc")
        self.assertIs(type(full_match), rebar.Match)
        self.assertEqual(full_match.group(0), "abc")
        self.assertEqual(full_match.span(), (0, 3))

        self.assertIsNone(rebar.search("abc", "zzz"))
        self.assertIsNone(rebar.match("abc", "zabc"))
        self.assertIsNone(rebar.fullmatch("abc", "abcz"))

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
    "split": [["abc", "abc"], {}],
    "findall": [["abc", "abc"], {}],
    "finditer": [["abc", "abc"], {}],
    "sub": [["abc", "x", "abc"], {}],
    "subn": [["abc", "x", "abc"], {}],
    "template": [["abc"], {}],
    "escape": [["abc"], {}],
}

result = {
    "native_module_loaded": rebar.native_module_loaded(),
    "native_scaffold_status": rebar.native_scaffold_status(),
    "exported_helpers_present": all(
        hasattr(rebar, name)
        for name in ["search", "match", "fullmatch"] + sorted(cases) + ["purge"]
    ),
    "purge_result": rebar.purge(),
}

compiled = rebar.compile("abc", rebar.IGNORECASE)
result["compiled_pattern"] = {
    "type_name": type(compiled).__name__,
    "type_module": type(compiled).__module__,
    "pattern": compiled.pattern,
    "flags": compiled.flags,
    "groups": compiled.groups,
    "groupindex": compiled.groupindex,
}

search_match = rebar.search("abc", "zzabczz")
result["literal_search"] = {
    "type_name": type(search_match).__name__,
    "group0": search_match.group(0),
    "span": list(search_match.span()),
}

result["literal_match_none"] = rebar.match("abc", "zabc")
full_match = rebar.fullmatch("abc", "abc")
result["literal_fullmatch"] = {
    "type_name": type(full_match).__name__,
    "group0": full_match.group(0),
    "span": list(full_match.span()),
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
            self.assertEqual(
                result["literal_search"],
                {
                    "type_name": "Match",
                    "group0": "abc",
                    "span": [2, 5],
                },
            )
            self.assertIsNone(result["literal_match_none"])
            self.assertEqual(
                result["literal_fullmatch"],
                {
                    "type_name": "Match",
                    "group0": "abc",
                    "span": [0, 3],
                },
            )
            self.assertEqual(
                result["compiled_pattern"],
                {
                    "type_name": "Pattern",
                    "type_module": "rebar",
                    "pattern": "abc",
                    "flags": int(rebar.IGNORECASE | rebar.UNICODE),
                    "groups": 0,
                    "groupindex": {},
                },
            )

            for helper_name in EXPECTED_HELPERS - {"purge", "search", "match", "fullmatch"}:
                with self.subTest(helper=helper_name):
                    exception_payload = result["exceptions"][helper_name]
                    self.assertEqual(exception_payload["type"], "NotImplementedError")
                    self.assertIn(
                        f"rebar.{helper_name}() is a scaffold placeholder",
                        exception_payload["message"],
                    )


if __name__ == "__main__":
    unittest.main()
