from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import textwrap

import pytest

import rebar

from rebar_harness import benchmarks


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
MATURIN = shutil.which("maturin")


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


def test_source_tree_shim_metadata_contract() -> None:
    assert rebar.TARGET_CPYTHON_SERIES == "3.12.x"
    assert rebar.SCAFFOLD_STATUS == "scaffold-only"
    assert rebar.NATIVE_MODULE_NAME == "rebar._rebar"
    assert isinstance(rebar.native_module_loaded(), bool)

    if rebar.native_module_loaded():
        assert rebar.native_scaffold_status() == "scaffold-only"
        assert rebar.native_target_cpython_series() == "3.12.x"
    else:
        assert rebar.native_scaffold_status() is None
        assert rebar.native_target_cpython_series() is None


@pytest.mark.skipif(
    MATURIN is None,
    reason="native extension smoke requires a maturin executable on PATH",
)
def test_built_wheel_keeps_native_surface_contract() -> None:
    with tempfile.TemporaryDirectory(prefix="rebar-native-smoke-") as temp_dir:
        temp_root = pathlib.Path(temp_dir)
        provisioned, temp_dir_handle, error = benchmarks.provision_built_native_runtime()
        assert provisioned is not None, error
        assert temp_dir_handle is not None, error

        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(
            str(path) for path in (provisioned["install_root"], PYTHON_SOURCE)
        )

        try:
            completed = subprocess.run(
                [sys.executable, "-c", PROBE],
                cwd=temp_root,
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
        finally:
            temp_dir_handle.cleanup()
        result = json.loads(completed.stdout)

        assert result["native_module_loaded"]
        assert result["native_scaffold_status"] == "scaffold-only"
        assert result["native_target_cpython_series"] == "3.12.x"
        assert result["native_private_flag"]
        assert result["native_module_name"] == "rebar._rebar"
        assert result["exported_helpers_present"]
        assert result["purge_result"] is None
        assert result["template_exception"] == {
            "type": "NotImplementedError",
            "message": "rebar.template() is a scaffold placeholder",
        }
        assert result["compile_exception"] is None
        assert result["compiled_pattern"] == {
            "type_name": "Pattern",
            "type_module": "re",
            "pattern": "abc",
            "flags": 34,
            "groups": 0,
            "groupindex": {},
        }
        assert result["compiled_search_exception"] is None
        assert result["compiled_search"] == {
            "type_name": "Match",
            "group0": "abc",
            "span": [0, 3],
        }
        assert result["literal_search"] == {
            "type_name": "Match",
            "group0": "abc",
            "span": [2, 5],
        }
        assert result["literal_match_none"] is None
        assert result["literal_fullmatch"] == {
            "type_name": "Match",
            "group0": "abc",
            "span": [0, 3],
        }
        assert result["literal_split"] == ["", "abc"]
        assert result["literal_findall"] == ["abc", "abc"]
        assert result["literal_finditer"] == [
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
        ]
        assert result["escape_outputs"] == {
            "simple_str": "a\\-b\\.c",
            "punctuation_str": '\\ !"\\#%\\&,/:;<=>@`\\~',
            "simple_bytes": "a\\-b\\.c",
        }
