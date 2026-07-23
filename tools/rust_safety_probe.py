#!/usr/bin/env python3
"""Run adversarial Rust regex checks in bounded, core-dump-free subprocesses."""

from __future__ import annotations

import argparse
import collections
import json
import math
import os
import platform
import random
import re
import subprocess
import sys
from pathlib import Path


SEED = 2026072319

CHILD = r"""
import importlib
import json
import resource
import sys
import warnings

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
memory = int(sys.argv[3]) * 1024 * 1024
resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
cpu = int(sys.argv[4])
resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
warnings.simplefilter("ignore", FutureWarning)
module = importlib.import_module(sys.argv[1])
case = json.loads(sys.argv[2])


def value(item):
    if isinstance(item, bytes):
        return {"bytes_hex": item.hex()}
    if isinstance(item, tuple):
        return {"tuple": [value(part) for part in item]}
    if isinstance(item, list):
        return [value(part) for part in item]
    if isinstance(item, dict):
        return {str(key): value(part) for key, part in item.items()}
    return item


def snapshot(match):
    if match is None:
        return None
    return {
        "span": value(match.span()),
        "regs": value(match.regs),
        "groups": value(match.groups()),
        "groupdict": value(match.groupdict()),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
    }


def decode(raw, kind):
    if kind == "str":
        return raw
    data = bytes.fromhex(raw)
    if kind == "bytes":
        return data
    if kind == "bytearray":
        return bytearray(data)
    if kind == "memoryview":
        return memoryview(data)
    if kind == "noncontiguous":
        return memoryview(data)[::2]
    if kind == "multidimensional":
        return memoryview(data).cast("B", shape=[2, len(data) // 2])
    raise ValueError("unknown subject kind")


try:
    pattern = decode(case["pattern"], case.get("pattern_kind", "str"))
    compiled = module.compile(pattern, case.get("flags", 0))
    operation = case["operation"]
    if operation == "compile":
        result = {
            "pattern": value(compiled.pattern),
            "flags": int(compiled.flags),
            "groups": compiled.groups,
            "groupindex": value(dict(compiled.groupindex)),
        }
    else:
        subject = decode(case["subject"], case.get("subject_kind", "str"))
        args = case.get("args", [])
        if operation == "scanner-search" or operation == "scanner-match":
            scanner = compiled.scanner(subject, *args)
            method = scanner.search if operation == "scanner-search" else scanner.match
            matches = []
            for _ in range(min(256, len(subject) * 2 + 5)):
                match = method()
                matches.append(snapshot(match))
                if match is None:
                    break
            result = matches
        elif operation == "finditer":
            result = [snapshot(match) for match in compiled.finditer(subject, *args)]
        elif operation == "findall":
            result = value(compiled.findall(subject, *args))
        elif operation == "split":
            result = value(compiled.split(subject, *args))
        elif operation == "sub" or operation == "subn":
            replacement = decode(case["replacement"], case.get("replacement_kind", "str"))
            result = value(getattr(compiled, operation)(replacement, subject, *args))
        else:
            result = snapshot(getattr(compiled, operation)(subject, *args))
    print(json.dumps({"value": result}, ensure_ascii=True, sort_keys=True))
except Exception as error:
    result = {"error": type(error).__name__, "message": str(error)}
    if all(hasattr(error, name) for name in ("msg", "pattern", "pos")):
        result["pattern_error"] = {
            name: value(getattr(error, name, None))
            for name in ("msg", "pattern", "pos", "lineno", "colno")
        }
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
"""


def C(label, category, pattern, **options):
    result = {"id": label, "category": category, "pattern": pattern, "operation": "compile"}
    result.update(options)
    return result


def cases(seed):
    low, high = "\ud800", "\udfff"
    rows = []

    reversed_ranges = (
        ("raw-pair", "[" + high + "-" + low + "]"),
        ("raw-low-ascii", "[" + low + "-a]"),
        ("raw-high-ascii", "[" + high + "-a]"),
        ("escaped-pair", r"[\udfff-\ud800]"),
        ("escaped-low-ascii", r"[\ud800-a]"),
    )
    for name, pattern in reversed_ranges:
        for flags in (0, re.I, re.A, re.I | re.A):
            rows.append(C(f"surrogate-reversed.{name}.{int(flags)}", "surrogate-reversed-range", pattern, flags=int(flags)))

    surrogate_patterns = (
        ("raw-high", low, low),
        ("raw-low", high, high),
        ("raw-class", "[" + low + "]", low),
        ("raw-range", "[" + low + "-" + high + "]", high),
        ("escaped-literal", r"\ud800", low),
        ("escaped-range", r"[\ud800-\udfff]", high),
        ("raw-capture", "(" + low + r")\1", low + low),
        ("raw-named-capture", "(?P<x>" + low + ")(?P=x)", low + low),
        ("scoped", "(?i:" + low + ")", low),
        ("verbose-comment", "(?x)#" + low + "\n" + low, low),
        ("wide-mixed", "a" + low + "😀", "a" + low + "😀"),
    )
    for name, pattern, subject in surrogate_patterns:
        for operation in ("compile", "search", "fullmatch", "findall"):
            rows.append(C(f"surrogate-valid.{name}.{operation}", "surrogate-pattern", pattern, subject=subject, operation=operation))

    malformed = (
        "[", "[]", "[a-", "[a-z", "[z-a]", "[\\", r"[\x]",
        r"[\x0]", r"[\u]", r"[\u000]", r"[\U0000000]",
        r"[\N{}]", r"[\N{NOT A UNICODE NAME}]", r"[\d-a]",
        r"[a-\d]", "(", ")", "(?", "(?P<", "(?P<>)", "(?P=)",
        "\\", r"\x", r"\u", r"\U00110000", "a**", "a{2,1}",
    )
    for index, pattern in enumerate(malformed):
        rows.append(C(f"malformed.{index:02d}", "malformed-pattern", pattern))

    name_patterns = (
        ("combining", "(?P<a\u0301>x)"),
        ("underscore-combining", "(?P<_\u0301>x)"),
        ("undertie", "(?P<a\u203f>x)"),
        ("character-tie", "(?P<a\u2040>x)"),
        ("middle-dot", "(?P<a\u00b7>x)"),
        ("greek-dot", "(?P<a\u0387>x)"),
        ("join-control", "(?P<a\u200c>x)"),
        ("join-control-zwj", "(?P<a\u200d>x)"),
        ("bare-combining", "(?P<\u0345>x)"),
        ("raw-surrogate", "(?P<" + low + ">x)"),
        ("raw-surrogate-reference", "(?P<x>x)(?P=" + low + ")"),
        ("unicode17-unassigned", "(?P<\ua7cf>x)"),
    )
    for name, pattern in name_patterns:
        rows.append(C(f"group-name.{name}", "unicode-group-name", pattern))

    repetitions = (
        ("zero", "a{0}", ""),
        ("large-fixed", "a{4294967294}", "aaa"),
        ("large-sequence", "(?:ab){4294967294}", "abab"),
        ("large-lookbehind", r"(?<=a{4294967294})b", "ab"),
        ("max-rejected", "a{4294967295}", "a"),
        ("u64-rejected", "a{18446744073709551615}", "a"),
        ("overflow-rejected", "a{18446744073709551616}", "a"),
        ("decimal-overflow", "a{" + "9" * 96 + "}", "a"),
        ("reversed", "a{4294967294,1}", "a"),
        ("large-possessive", "(?:a{1,2}){2,4}+", "aa"),
        ("large-atomic-control", "(?>(?:a{1,2}){2,4})", "aa"),
        ("large-choice-possessive", "(?:(?:a|b){1,2}){2,4}+", "ab"),
    )
    for name, pattern, subject in repetitions:
        for operation in ("compile", "fullmatch"):
            rows.append(C(f"repetition.{name}.{operation}", "repetition-boundary", pattern, subject=subject, operation=operation))

    for depth in (16, 64, 128, 256, 512, 1024, 2048, 4096):
        rows.append(C(f"depth.groups.{depth}", "nesting-depth", "(" * depth + "a" + ")" * depth))
        rows.append(C(f"depth.lookahead.{depth}", "nesting-depth", "(?=" * depth + "a" + ")" * depth))

    for count in (16, 64, 256, 1024):
        choices = "(?:" + "|".join(f"prefix{index:04d}" for index in range(count)) + ")"
        rows.append(C(f"width.alternatives.{count}", "allocation-boundary", choices))
    for count in (16, 64, 256, 1024):
        groups = "(a)" * count
        rows.append(C(f"width.groups.{count}", "allocation-boundary", groups, subject="a" * count, operation="fullmatch"))

    for operation in ("search", "match", "fullmatch", "findall", "finditer", "scanner-search", "scanner-match"):
        for suffix, args in (
            ("none-end", [0, None]),
            ("max-pos", [sys.maxsize]),
            ("overflow-pos", [sys.maxsize + 1]),
            ("negative-overflow", [-sys.maxsize - 2]),
            ("inverted", [3, 0]),
        ):
            rows.append(C(f"window.{operation}.{suffix}", "window-boundary", r"a?", subject="a", args=args, operation=operation))

    for kind in ("bytes", "bytearray", "memoryview", "noncontiguous", "multidimensional"):
        for operation in ("search", "fullmatch", "findall", "finditer"):
            rows.append(
                C(
                    f"buffer.{kind}.{operation}",
                    "buffer-boundary",
                    b"a+".hex(),
                    pattern_kind="bytes",
                    subject=b"aabb".hex(),
                    subject_kind=kind,
                    operation=operation,
                )
            )

    rng = random.Random(seed)
    fragments = ("[", "]", "(", ")", "{", "}", "?", "*", "+", "|", "\\", "a", "0", low, high)
    for index in range(48):
        pattern = "".join(rng.choice(fragments) for _ in range(rng.randrange(1, 18)))
        rows.append(C(f"seeded-malformed.{index:02d}", "seeded-malformed", pattern))
    return rows


def execute(module, case, timeout, memory_mib):
    encoded = json.dumps(case, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                CHILD,
                module,
                encoded,
                str(memory_mib),
                str(max(2, math.ceil(timeout) + 1)),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "timeout_seconds": timeout}
    if completed.returncode:
        return {
            "status": "crash" if completed.returncode < 0 else "process-error",
            "returncode": completed.returncode,
            "signal": -completed.returncode if completed.returncode < 0 else None,
            "stderr": completed.stderr[-2048:],
        }
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {
            "status": "invalid-output",
            "stdout": completed.stdout[-2048:],
            "stderr": completed.stderr[-2048:],
        }
    return {"status": "completed", "result": result}


def equivalent(expected, actual):
    if expected.get("status") != actual.get("status"):
        return False
    if expected.get("status") != "completed":
        return False
    left, right = expected["result"], actual["result"]
    if "error" in left or "error" in right:
        if left.get("error") != right.get("error"):
            return False
        if "pattern_error" in left or "pattern_error" in right:
            return left.get("pattern_error") == right.get("pattern_error")
        return True
    return left == right


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", default="candidates.rust_candidate")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--timeout", type=float, default=4.0)
    parser.add_argument("--memory-mib", type=int, default=768)
    parser.add_argument("--category")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.memory_mib < 96:
        parser.error("--memory-mib must be at least 96")

    selected = [case for case in cases(args.seed) if args.category is None or case["category"] == args.category]
    if not selected:
        parser.error("no cases match --category")

    failures = []
    categories = collections.Counter()
    failed_categories = collections.Counter()
    crashes = 0
    timeouts = 0
    oracle_failures = 0

    for index, case in enumerate(selected):
        expected = execute("re", case, args.timeout, args.memory_mib)
        actual = execute(args.module, case, args.timeout, args.memory_mib)
        categories[case["category"]] += 1
        if expected.get("status") != "completed":
            oracle_failures += 1
        if actual.get("status") == "crash":
            crashes += 1
        if actual.get("status") == "timeout":
            timeouts += 1
        if not equivalent(expected, actual):
            failed_categories[case["category"]] += 1
            failures.append({"case": case, "expected": expected, "actual": actual})
        if (index + 1) % 32 == 0:
            print(
                f"checked {index + 1}/{len(selected)}; "
                f"failures={len(failures)} crashes={crashes} timeouts={timeouts}",
                flush=True,
            )

    report = {
        "schema": "rebar-rust-subprocess-safety-v1",
        "oracle": "CPython stdlib re",
        "python_version": platform.python_version(),
        "module": args.module,
        "seed": args.seed,
        "isolation": "one independent subprocess per engine and case",
        "core_dumps": "disabled in every child process",
        "timeout_seconds": args.timeout,
        "memory_limit_mib": args.memory_mib,
        "cpu_limit_seconds": max(2, math.ceil(args.timeout) + 1),
        "correctness_checks": len(selected),
        "categories": dict(sorted(categories.items())),
        "failed_categories": dict(sorted(failed_categories.items())),
        "oracle_failures": oracle_failures,
        "crashes": crashes,
        "timeouts": timeouts,
        "failed": len(failures),
        "failures": failures,
    }
    Path(args.output).write_text(
        json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: value for key, value in report.items() if key != "failures"}, sort_keys=True))
    if failures or oracle_failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
