#!/usr/bin/env python3
"""Static and import-time delegation audit for a from-scratch candidate."""

import ast
import builtins
import importlib
import json
import sys
from pathlib import Path

BLOCKED = {"re", "_sre", "sre_compile", "sre_parse", "regex", "pcre", "pcre2", "onigurumacffi", "_onigurumacffi", "rebar"}
SOURCE_MARKERS = ("_sre", "sre_compile", "sre_parse", "PyInit__sre", "libpcre", "libonig", "oniguruma", "hyperscan")


def main():
    if len(sys.argv) not in {3, 4}:
        raise SystemExit("usage: audit_candidate.py <source.py> <module> [native-source]")
    source_path = Path(sys.argv[1])
    module_name = sys.argv[2]
    native_path = Path(sys.argv[3]) if len(sys.argv) == 4 else None
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(source_path))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(item.name for item in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    forbidden_imports = sorted(name for name in imports if name.split(".", 1)[0] in BLOCKED)
    native_source = native_path.read_text(encoding="utf-8") if native_path else ""
    forbidden_markers = sorted(marker for marker in SOURCE_MARKERS if marker in source or marker in native_source)
    if forbidden_imports or forbidden_markers:
        raise SystemExit(json.dumps({"forbidden_imports": forbidden_imports, "forbidden_markers": forbidden_markers}))
    real_import = builtins.__import__
    attempted = []

    def guarded(name, *args, **kwargs):
        if name.split(".", 1)[0] in BLOCKED:
            attempted.append(name)
            raise ImportError(f"delegation audit blocked import: {name}")
        return real_import(name, *args, **kwargs)

    builtins.__import__ = guarded
    try:
        module = importlib.import_module(module_name)
        assert module.search(r"(?P<w>\w+)-(\d+)", "x ab-12 y").groups() == ("ab", "12")
        assert module.findall(rb"\w+", b"a_b ! 12") == [b"a_b", b"12"]
        assert module.sub(r"(\w+)-(\d+)", r"\2:\1", "ab-12") == "12:ab"
        assert module.fullmatch(r"(?>a*)a", "aaaa") is None
        assert module.fullmatch(r"a*+a", "aaaa") is None
    finally:
        builtins.__import__ = real_import
    if attempted:
        raise SystemExit(json.dumps({"blocked_attempts": attempted}))
    print(json.dumps({"source": str(source_path), "native_source": str(native_path) if native_path else None, "module": module_name, "imports": sorted(set(imports)), "blocked_attempts": 0, "forbidden_markers": 0, "smoke": "pass"}, sort_keys=True))


if __name__ == "__main__":
    main()
