#!/usr/bin/env python3
"""Reproduce CPython group-name errors against the independent Rust engine."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib
import importlib.util
import json
import re
import sys
from pathlib import Path


SCHEMA = "rebar-rust-unicode-group-name-adversarial-v1"
SEED = 0x47524F55504E414D
CODEPOINTS = (
    0x0000,
    0x0001,
    0x0007,
    0x0008,
    0x0009,
    0x000A,
    0x000B,
    0x000C,
    0x000D,
    0x001B,
    0x001C,
    0x001D,
    0x001E,
    0x001F,
    0x007F,
    0x0080,
    0x00AD,
    0x0378,
    0x0379,
    0x061C,
    0x200B,
    0x200C,
    0x200D,
    0x2028,
    0x2029,
    0x2060,
    0xA7CF,
    0xD800,
    0xDBFF,
    0xDC00,
    0xDFFF,
    0xFDD0,
    0xFFFE,
    0xFFFF,
    0x10FFFF,
)


def original_formatter(pattern, message, position):
    """Replay the original engine message without any wrapper correction."""
    return message


def initial_formatter(pattern, message, position):
    """Replay the first, incomplete group-definition formatting experiment."""
    if (
        not isinstance(pattern, str)
        or not message.startswith("bad character in group name ")
        or position is None
        or not 0 <= position < len(pattern)
    ):
        return message
    end = min(
        (
            index
            for index in (pattern.find(">", position), pattern.find(")", position))
            if index >= 0
        ),
        default=len(pattern),
    )
    name = pattern[position:end]
    if name and not name.isprintable():
        return f"bad character in group name {name!r}"
    return message


def observed(module, pattern):
    try:
        compiled = module.compile(pattern)
        return {
            "status": "ok",
            "pattern": compiled.pattern,
            "flags": compiled.flags,
            "groups": compiled.groups,
            "groupindex": dict(compiled.groupindex),
        }
    except BaseException as error:
        return {
            "status": "error",
            "type": type(error).__name__,
            "message": str(error),
            "args": list(error.args),
            "msg": getattr(error, "msg", None),
            "pattern": getattr(error, "pattern", None),
            "pos": getattr(error, "pos", None),
            "lineno": getattr(error, "lineno", None),
            "colno": getattr(error, "colno", None),
        }


def cases():
    forms = (
        ("single", lambda char: char),
        ("suffix", lambda char: "x" + char),
        ("prefix", lambda char: char + "x"),
        ("interior", lambda char: "x" + char + "y"),
    )
    patterns = (
        ("definition", lambda name: "(?P<" + name + ">x)"),
        ("reference", lambda name: "(?P<x>x)(?P=" + name + ")"),
        ("conditional", lambda name: "(?P<x>x)(?(" + name + ")x|y)"),
    )
    result = []
    for point in CODEPOINTS:
        for form_name, make_name in forms:
            name = make_name(chr(point))
            for syntax_name, make_pattern in patterns:
                result.append(
                    {
                        "id": (
                            f"group-name.{syntax_name}."
                            f"u{point:06x}.{form_name}"
                        ),
                        "codepoint": f"U+{point:04X}",
                        "syntax": syntax_name,
                        "form": form_name,
                        "pattern": make_pattern(name),
                    }
                )
    if len(result) != 420:
        raise RuntimeError(f"frozen group-name case count drifted: {len(result)}")
    return result


def load_candidate(module_name, bridge_path):
    if bridge_path:
        package_name, _, _ = module_name.rpartition(".")
        if not package_name:
            raise ValueError("--bridge-path requires a package-qualified module")
        package = importlib.import_module(package_name)
        bridge_name = package_name + "._rust_bridge"
        spec = importlib.util.spec_from_file_location(bridge_name, bridge_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load Rust bridge {bridge_path!r}")
        bridge = importlib.util.module_from_spec(spec)
        sys.modules[bridge_name] = bridge
        spec.loader.exec_module(bridge)
        setattr(package, "_rust_bridge", bridge)
    return importlib.import_module(module_name)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if path else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", default="candidates.rust_candidate")
    parser.add_argument("--bridge-path")
    parser.add_argument("--engine-path")
    parser.add_argument(
        "--formatter",
        choices=("production", "original", "initial"),
        default="production",
        help="replay an isolated recorded formatting experiment",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    candidate = load_candidate(args.module, args.bridge_path)
    if args.formatter == "original":
        candidate._group_name_error = original_formatter
    elif args.formatter == "initial":
        candidate._group_name_error = initial_formatter

    suite = cases()
    failures = []
    oracle_failures = []
    for case in suite:
        expected = observed(re, case["pattern"])
        repeated = observed(re, case["pattern"])
        if expected != repeated:
            oracle_failures.append(
                {"case": case, "first": expected, "second": repeated}
            )
            continue
        actual = observed(candidate, case["pattern"])
        if expected != actual:
            failures.append(
                {"case": case, "expected": expected, "actual": actual}
            )

    report = {
        "schema": SCHEMA,
        "seed": SEED,
        "python_version": sys.version,
        "python_executable": sys.executable,
        "oracle": "stdlib re",
        "self_oracle_passes": 2,
        "self_oracle_failures": oracle_failures,
        "module": args.module,
        "module_sha256": digest(getattr(candidate, "__file__", None)),
        "bridge_path": args.bridge_path,
        "bridge_sha256": digest(args.bridge_path),
        "engine_path": args.engine_path,
        "engine_sha256": digest(args.engine_path),
        "runner_sha256": digest(__file__),
        "formatter": args.formatter,
        "codepoints": len(CODEPOINTS),
        "checks": len(suite),
        "failed": len(failures),
        "failures": failures,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")
    if output.suffix == ".gz":
        output.write_bytes(gzip.compress(payload, compresslevel=9, mtime=0))
    else:
        output.write_bytes(payload)
    print(
        json.dumps(
            {
                "schema": SCHEMA,
                "seed": SEED,
                "formatter": args.formatter,
                "checks": len(suite),
                "failed": len(failures),
                "self_oracle_failures": len(oracle_failures),
                "output": str(output),
            },
            sort_keys=True,
        )
    )
    if failures or oracle_failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
