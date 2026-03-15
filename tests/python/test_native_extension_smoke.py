from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import textwrap
import unittest

from tests.benchmarks import native_benchmark_test_support as native_test_support


PROBE = textwrap.dedent(
    """
    import json
    import rebar
    import rebar._rebar as native

    result = {
        "native_module_loaded": rebar.native_module_loaded(),
        "native_scaffold_status": rebar.native_scaffold_status(),
        "native_target_cpython_series": rebar.native_target_cpython_series(),
        "native_private_flag": getattr(native, "__rebar_scaffold__", False),
        "native_module_name": native.__name__,
        "exported_helpers_present": all(
            hasattr(rebar, name)
            for name in (
                "search",
                "match",
                "fullmatch",
                "split",
                "findall",
                "finditer",
                "template",
                "purge",
            )
        ),
        "purge_result": rebar.purge(),
    }

    try:
        rebar.template("abc")
    except Exception as exc:
        result["template_exception"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
    else:
        result["template_exception"] = None

    try:
        compiled = rebar.compile("abc", rebar.IGNORECASE)
    except Exception as exc:
        result["compile_exception"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
    else:
        result["compile_exception"] = None
        result["compiled_pattern"] = {
            "type_name": type(compiled).__name__,
            "type_module": type(compiled).__module__,
            "pattern": compiled.pattern,
            "flags": compiled.flags,
            "groups": compiled.groups,
            "groupindex": compiled.groupindex,
        }
        try:
            compiled_search = compiled.search("abc")
        except Exception as exc:
            result["compiled_search_exception"] = {
                "type": type(exc).__name__,
                "message": str(exc),
            }
        else:
            result["compiled_search_exception"] = None
            result["compiled_search"] = {
                "type_name": type(compiled_search).__name__,
                "group0": compiled_search.group(0),
                "span": list(compiled_search.span()),
            }

    search_match = rebar.search("abc", "zzabczz")
    full_match = rebar.fullmatch("abc", "abc")
    result["literal_search"] = {
        "type_name": type(search_match).__name__,
        "group0": search_match.group(0),
        "span": list(search_match.span()),
    }
    result["literal_match_none"] = rebar.match("abc", "zabc")
    result["literal_fullmatch"] = {
        "type_name": type(full_match).__name__,
        "group0": full_match.group(0),
        "span": list(full_match.span()),
    }
    result["literal_split"] = rebar.split("abc", "abcabc", 1)
    result["literal_findall"] = rebar.findall("abc", "zabcabc")
    result["literal_finditer"] = [
        {
            "type_name": type(match).__name__,
            "group0": match.group(0),
            "span": list(match.span()),
        }
        for match in rebar.finditer("abc", "zabcabc")
    ]
    result["escape_outputs"] = {
        "simple_str": rebar.escape("a-b.c"),
        "punctuation_str": rebar.escape(' !"#%&,/:;<=>@`~'),
        "simple_bytes": rebar.escape(b"a-b.c").decode("latin-1"),
    }

    print(json.dumps(result))
    """
)


class RebarNativeExtensionSmokeTest(unittest.TestCase):
    @unittest.skipUnless(
        native_test_support.MATURIN is not None,
        "native extension smoke requires a maturin executable on PATH",
    )
    def test_built_wheel_keeps_native_surface_contract(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rebar-native-smoke-") as temp_dir:
            temp_root = pathlib.Path(temp_dir)
            with native_test_support.built_native_runtime(self) as (python_bin, env):
                completed = subprocess.run(
                    [str(python_bin), "-c", PROBE],
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
            self.assertTrue(result["exported_helpers_present"])
            self.assertIsNone(result["purge_result"])
            self.assertEqual(
                result["template_exception"],
                {
                    "type": "NotImplementedError",
                    "message": "rebar.template() is a scaffold placeholder",
                },
            )
            self.assertIsNone(result["compile_exception"])
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
            self.assertIsNone(result["compiled_search_exception"])
            self.assertEqual(
                result["compiled_search"],
                {
                    "type_name": "Match",
                    "group0": "abc",
                    "span": [0, 3],
                },
            )
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
            self.assertEqual(result["literal_split"], ["", "abc"])
            self.assertEqual(result["literal_findall"], ["abc", "abc"])
            self.assertEqual(
                result["literal_finditer"],
                [
                    {
                        "type_name": "Match",
                        "group0": "abc",
                        "span": [1, 4],
                    },
                    {
                        "type_name": "Match",
                        "group0": "abc",
                        "span": [4, 7],
                    },
                ],
            )
            self.assertEqual(
                result["escape_outputs"],
                {
                    "simple_str": "a\\-b\\.c",
                    "punctuation_str": '\\ !"\\#%\\&,/:;<=>@`\\~',
                    "simple_bytes": "a\\-b\\.c",
                },
            )


if __name__ == "__main__":
    unittest.main()
