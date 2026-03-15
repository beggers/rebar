from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import unittest


from tests.benchmarks.native_benchmark_test_support import MATURIN, built_native_runtime


class RebarNativeExtensionSmokeTest(unittest.TestCase):
    @unittest.skipUnless(
        MATURIN is not None,
        "native extension smoke requires a maturin executable on PATH",
    )
    def test_built_wheel_imports_native_extension(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rebar-native-smoke-") as temp_dir:
            temp_root = pathlib.Path(temp_dir)
            with built_native_runtime(self) as (python_bin, env):

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
    compiled = rebar.compile("abc", rebar.IGNORECASE)
except Exception as exc:
    result["compile_exception_type"] = type(exc).__name__
    result["compile_exception_message"] = str(exc)
else:
    result["compiled_pattern"] = {
        "type_name": type(compiled).__name__,
        "type_module": type(compiled).__module__,
        "pattern": compiled.pattern,
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
            "span": list(compiled.search("abc").span()),
        }

print(json.dumps(result))
"""
                completed = subprocess.run(
                    [str(python_bin), "-c", probe],
                    cwd=temp_root,
                    check=True,
                    capture_output=True,
                    text=True,
                    env=env,
                )
            result = json.loads(completed.stdout)

            self.assertTrue(result["native_module_loaded"])
            self.assertEqual(result["native_scaffold_status"], "scaffold-only")
            self.assertEqual(result["native_target_cpython_series"], "3.12.x")
            self.assertTrue(result["native_private_flag"])
            self.assertEqual(result["native_module_name"], "rebar._rebar")
            self.assertEqual(
                result["compiled_pattern"],
                {
                    "type_name": "Pattern",
                    "type_module": "re",
                    "pattern": "abc",
                    "flags": 34,
                    "groups": 0,
                    "groupindex": {},
                },
            )
            self.assertIsNone(result["search_exception_type"])
            self.assertIsNone(result["search_exception_message"])
            self.assertEqual(
                result["search_result"],
                {
                    "type_name": "Match",
                    "group0": "abc",
                    "span": [0, 3],
                },
            )


if __name__ == "__main__":
    unittest.main()
