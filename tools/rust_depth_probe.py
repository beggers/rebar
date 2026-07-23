#!/usr/bin/env python3
"""Bounded subprocess oracle for Rust regex recursion and allocation safety."""

from __future__ import annotations

import argparse
import collections
import json
import math
import platform
import random
import re
import subprocess
import sys
from pathlib import Path


SEED = 2026072323
DEPTHS = (16, 64, 128, 256, 494, 495, 496, 497, 512, 1024, 2048, 4096, 8192, 16384, 32768)

CHILD = r"""
import hashlib
import importlib
import json
import resource
import sys
import warnings

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
memory = int(sys.argv[2]) * 1024 * 1024
resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
cpu = int(sys.argv[3])
resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
warnings.simplefilter("ignore", FutureWarning)
module = importlib.import_module(sys.argv[1])
case = json.loads(sys.stdin.read())
if case.get("recursion_limit") is not None:
    sys.setrecursionlimit(int(case["recursion_limit"]))


def pattern_of(spec):
    kind = spec["builder"]
    depth = spec.get("depth", 0)
    if kind == "groups":
        return "(" * depth + "a" + ")" * depth
    if kind == "lookahead":
        return "(?=" * depth + "a" + ")" * depth
    if kind == "negative-lookahead":
        return "(?!" * depth + "a" + ")" * depth
    if kind == "noncapture":
        return "(?:" * depth + "a" + ")" * depth
    if kind == "atomic":
        return "(?>" * depth + "a" + ")" * depth
    if kind == "nullable":
        return "(?:" * depth + "a?" + ")*" * depth
    if kind == "lookbehind":
        return "(?<=" * depth + "a" + ")" * depth
    if kind == "unclosed":
        return "(" * depth + "a"
    if kind == "alternatives":
        return "(?:" + "|".join(f"prefix{index:08d}" for index in range(depth)) + ")"
    if kind == "captures":
        return "(a)" * depth
    if kind == "long-literal":
        return "a" * depth
    if kind == "literal":
        return spec["pattern"]
    raise ValueError("unknown bounded pattern builder")


def normalized(value):
    if isinstance(value, tuple):
        return {"tuple": [normalized(item) for item in value]}
    if isinstance(value, list):
        return [normalized(item) for item in value]
    if isinstance(value, dict):
        return {str(key): normalized(item) for key, item in value.items()}
    return value


def snapshot(match):
    if match is None:
        return None
    return {
        "span": normalized(match.span()),
        "groups": normalized(match.groups()),
        "groupdict": normalized(match.groupdict()),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
    }


try:
    pattern = pattern_of(case)
    compiled = module.compile(pattern, case.get("flags", 0))
    operation = case.get("operation", "compile")
    if operation == "compile":
        encoded = compiled.pattern.encode("utf-8", "surrogatepass")
        result = {
            "pattern_length": len(compiled.pattern),
            "pattern_sha256": hashlib.sha256(encoded).hexdigest(),
            "flags": int(compiled.flags),
            "groups": compiled.groups,
            "groupindex": dict(compiled.groupindex),
        }
    else:
        subject = case.get("subject", "a")
        if case.get("subject_repeat") is not None:
            subject = "a" * int(case["subject_repeat"])
        if operation == "finditer":
            result = [snapshot(item) for item in compiled.finditer(subject)]
        elif operation == "findall":
            result = normalized(compiled.findall(subject))
        else:
            result = snapshot(getattr(compiled, operation)(subject))
    print(json.dumps({"value": result}, ensure_ascii=True, sort_keys=True))
except Exception as error:
    result = {"error": type(error).__name__, "message": str(error)}
    if all(hasattr(error, name) for name in ("msg", "pattern", "pos")):
        result["pattern_error"] = {
            "msg": getattr(error, "msg", None),
            "pattern_length": len(error.pattern) if error.pattern is not None else None,
            "pos": getattr(error, "pos", None),
            "lineno": getattr(error, "lineno", None),
            "colno": getattr(error, "colno", None),
        }
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
"""


def C(label, category, builder, **details):
    return {"id": label, "category": category, "builder": builder, **details}


def cases(seed):
    rows = []
    builders = ("groups", "lookahead", "negative-lookahead", "noncapture", "atomic", "nullable", "lookbehind")
    for depth in DEPTHS:
        for builder in builders:
            rows.append(C(f"depth.{builder}.{depth}", "parser-nesting", builder, depth=depth))

    for limit in (49, 51, 64, 101, 128, 179, 181, 256, 512, 768, 999, 1000, 1001, 4096):
        for offset in (-8, -4, 0, 4):
            depth = max(1, limit // 2 + offset)
            for builder in ("groups", "lookahead"):
                rows.append(
                    C(
                        f"limit.{limit}.{builder}.{offset:+d}",
                        "dynamic-recursion-limit",
                        builder,
                        depth=depth,
                        recursion_limit=limit,
                    )
                )

    for depth in (16, 64, 128, 256):
        for builder in ("groups", "lookahead", "noncapture", "atomic"):
            rows.append(C(f"match.{builder}.{depth}", "nested-matching", builder, depth=depth, operation="fullmatch"))

    for depth in (256, 512, 8192, 16384):
        rows.append(C(f"unclosed.{depth}", "malformed-nesting", "unclosed", depth=depth))

    for count in (64, 512, 2048, 8192):
        rows.append(C(f"width.alternatives.{count}", "allocation-width", "alternatives", depth=count))
    for count in (16, 64, 256, 512, 1024, 2048):
        rows.append(C(f"width.captures.{count}.compile", "allocation-width", "captures", depth=count))
        rows.append(C(f"width.captures.{count}.fullmatch", "allocation-width", "captures", depth=count, subject_repeat=count, operation="fullmatch"))
    for length in (4096, 32768, 131072, 262144):
        rows.append(C(f"width.literal.{length}", "allocation-width", "long-literal", depth=length))

    repeats = (
        ("zero", "a{0}", ""),
        ("large-fixed", "a{4294967294}", "aaa"),
        ("large-sequence", "(?:ab){4294967294}", "abab"),
        ("large-lookbehind", r"(?<=a{4294967294})b", "ab"),
        ("max-rejected", "a{4294967295}", "a"),
        ("u64-rejected", "a{18446744073709551615}", "a"),
        ("overflow-rejected", "a{18446744073709551616}", "a"),
        ("decimal-overflow", "a{" + "9" * 128 + "}", "a"),
        ("reversed", "a{4294967294,1}", "a"),
        ("compound-possessive", "(?:a{1,2}){2,4}+", "aa"),
        ("compound-atomic", "(?>(?:a{1,2}){2,4})", "aa"),
        ("choice-possessive", "(?:(?:a|b){1,2}){2,4}+", "ab"),
    )
    for name, pattern, subject in repeats:
        for operation in ("compile", "fullmatch"):
            rows.append(C(f"repeat.{name}.{operation}", "repetition-overflow", "literal", pattern=pattern, subject=subject, operation=operation))

    conditional_numbers = (
        ("u32-boundary", "4294967295"),
        ("u64-boundary", "18446744073709551615"),
        ("u64-overflow", "18446744073709551616"),
        ("all-nine-64", "9" * 64),
        ("all-nine-80", "9" * 80),
        ("all-nine-100", "9" * 100),
        ("all-zero-64", "0" * 64),
        ("all-zero-100", "0" * 100),
        ("leading-zero-64", "0" * 63 + "1"),
        ("leading-zero-100", "0" * 99 + "1"),
    )
    for name, digits in conditional_numbers:
        for prefix in ("", "(a)?"):
            label = "capture" if prefix else "plain"
            pattern = prefix + "(?(" + digits + ")a|b)"
            rows.append(
                C(
                    f"conditional.{name}.{label}",
                    "numeric-condition-overflow",
                    "literal",
                    pattern=pattern,
                )
            )

    for width in (4, 8, 12, 16, 18):
        for name, pattern in (
            ("nested-plus", r"^(a+)+$"),
            ("overlap", r"^(a|aa)+$"),
            ("nullable", r"^(a?)*$"),
        ):
            rows.append(C(f"backtrack.{name}.{width}", "bounded-backtracking", "literal", pattern=pattern, subject="a" * width + "!", operation="fullmatch"))

    rng = random.Random(seed)
    for index in range(32):
        builder = rng.choice(builders)
        depth = rng.randrange(1, 768)
        rows.append(C(f"seeded.{index:02d}", "seeded-nesting", builder, depth=depth))
    return rows


def execute(module, case, timeout, memory_mib):
    payload = json.dumps(case, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    try:
        process = subprocess.run(
            [
                sys.executable,
                "-c",
                CHILD,
                module,
                str(memory_mib),
                str(max(2, math.ceil(timeout) + 1)),
            ],
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "timeout_seconds": timeout}
    if process.returncode:
        return {
            "status": "crash" if process.returncode < 0 else "process-error",
            "returncode": process.returncode,
            "signal": -process.returncode if process.returncode < 0 else None,
            "stderr": process.stderr[-2048:],
        }
    try:
        result = json.loads(process.stdout)
    except json.JSONDecodeError:
        return {
            "status": "invalid-output",
            "stdout": process.stdout[-2048:],
            "stderr": process.stderr[-2048:],
        }
    return {"status": "completed", "result": result}


def equivalent(expected, actual):
    if expected.get("status") != "completed" or actual.get("status") != "completed":
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
    parser.add_argument("--timeout", type=float, default=5.0)
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

    totals = collections.Counter()
    failed_totals = collections.Counter()
    failures = []
    crashes = 0
    timeouts = 0
    oracle_failures = 0
    for index, case in enumerate(selected):
        expected = execute("re", case, args.timeout, args.memory_mib)
        actual = execute(args.module, case, args.timeout, args.memory_mib)
        category = case["category"]
        totals[category] += 1
        if expected.get("status") != "completed":
            oracle_failures += 1
        if actual.get("status") == "crash":
            crashes += 1
        if actual.get("status") == "timeout":
            timeouts += 1
        if not equivalent(expected, actual):
            failed_totals[category] += 1
            failures.append({"case": case, "expected": expected, "actual": actual})
        if (index + 1) % 24 == 0:
            print(f"checked {index + 1}/{len(selected)}; failures={len(failures)} crashes={crashes} timeouts={timeouts}", flush=True)

    report = {
        "schema": "rebar-rust-depth-safety-v1",
        "oracle": "CPython stdlib re",
        "python_version": platform.python_version(),
        "module": args.module,
        "seed": args.seed,
        "isolation": "one independent subprocess per engine and case",
        "pattern_transport": "compact generator descriptor over subprocess standard input",
        "core_dumps": "disabled in every child process",
        "timeout_seconds": args.timeout,
        "memory_limit_mib": args.memory_mib,
        "cpu_limit_seconds": max(2, math.ceil(args.timeout) + 1),
        "correctness_checks": len(selected),
        "categories": dict(sorted(totals.items())),
        "failed_categories": dict(sorted(failed_totals.items())),
        "oracle_failures": oracle_failures,
        "crashes": crashes,
        "timeouts": timeouts,
        "failed": len(failures),
        "failures": failures,
    }
    Path(args.output).write_text(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "failures"}, sort_keys=True))
    if failures or oracle_failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
