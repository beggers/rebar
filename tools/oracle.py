#!/usr/bin/env python3
"""Freeze and differentially verify the versioned CPython re correctness oracle."""

import argparse
import contextlib
import copy
import hashlib
import importlib
import importlib.util
import io
import json
import locale
import os
import pickle
import platform
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "oracle" / "v1" / "suite.py"
EXPECTED = ROOT / "oracle" / "v1" / "expected.jsonl"
MANIFEST = ROOT / "oracle" / "v1" / "manifest.json"
GOAL_HASH = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"


def suite_module():
    spec = importlib.util.spec_from_file_location("rebar_oracle_v1_suite", SUITE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def jsonable(value):
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in sorted(value.items(), key=lambda x: str(x[0]))}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return {"type": type(value).__name__, "repr": repr(value)}


def flags_value(module, names):
    result = 0
    for name in names:
        result |= int(getattr(module, name))
    return result


def pattern_info(pattern):
    return {
        "pattern": jsonable(pattern.pattern),
        "flags": int(pattern.flags),
        "groups": pattern.groups,
        "groupindex": jsonable(dict(pattern.groupindex)),
        "public": sorted(name for name in dir(pattern) if not name.startswith("_")),
    }


def match_info(match):
    if match is None:
        return None
    default = b"<missing>" if isinstance(match.string, bytes) else "<missing>"
    template = b"<\\g<0>>" if isinstance(match.string, bytes) else "<\\g<0>>"
    count = match.re.groups
    indexes = list(range(count + 1))
    return {
        "bool": bool(match),
        "group0": jsonable(match.group(0)),
        "groups": jsonable(match.groups()),
        "groups_default": jsonable(match.groups(default)),
        "groupdict": jsonable(match.groupdict()),
        "groupdict_default": jsonable(match.groupdict(default)),
        "items": jsonable([match[index] for index in indexes]),
        "starts": jsonable([match.start(index) for index in indexes]),
        "ends": jsonable([match.end(index) for index in indexes]),
        "spans": jsonable([match.span(index) for index in indexes]),
        "regs": jsonable(match.regs),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
        "string": jsonable(match.string),
        "expand": jsonable(match.expand(template)),
        "re": pattern_info(match.re),
        "public": sorted(name for name in dir(match) if not name.startswith("_")),
    }


def result_info(value):
    if hasattr(value, "group") and hasattr(value, "span"):
        return match_info(value)
    if isinstance(value, list):
        return [result_info(item) for item in value]
    if isinstance(value, tuple):
        return [result_info(item) for item in value]
    if hasattr(value, "__next__"):
        return [result_info(item) for item in value]
    return jsonable(value)


def replacement(case):
    repl = case["repl"]
    if not isinstance(repl, dict):
        return repl
    if repl.get("callable") != "bracket_upper":
        raise RuntimeError(f"unknown callable replacement: {repl!r}")

    def bracket_upper(match):
        value = match.group(0)
        return b"[" + value.upper() + b"]" if isinstance(value, bytes) else "[" + value.upper() + "]"

    return bracket_upper


def call_case(module, case):
    api = case["api"]
    flags = flags_value(module, case["flags"])
    kwargs = {}
    if api in {"sub", "subn"}:
        kwargs["count"] = case.get("count", 0)
    if api == "split":
        kwargs["maxsplit"] = case.get("maxsplit", 0)
    if case["surface"] == "module":
        function = getattr(module, api)
        if api in {"sub", "subn"}:
            return function(case["pattern"], replacement(case), case["string"], flags=flags, **kwargs)
        return function(case["pattern"], case["string"], flags=flags, **kwargs)
    pattern = module.compile(case["pattern"], flags)
    function = getattr(pattern, api)
    if api in {"search", "match", "fullmatch", "findall", "finditer"}:
        if "pos" in case:
            kwargs["pos"] = case["pos"]
        if "endpos" in case:
            kwargs["endpos"] = case["endpos"]
    if api in {"sub", "subn"}:
        return function(replacement(case), case["string"], **kwargs)
    return function(case["string"], **kwargs)


def exception_info(error):
    data = {"type": type(error).__name__, "args": jsonable(error.args), "str": str(error)}
    for name in ("msg", "pattern", "pos", "lineno", "colno"):
        if hasattr(error, name):
            data[name] = jsonable(getattr(error, name))
    return data


def execute(module, case):
    kind = case["kind"]
    if kind == "exports":
        return {
            "all": sorted(module.__all__),
            "error_alias": module.error is module.PatternError,
            "pattern_name": module.Pattern.__name__,
            "match_name": module.Match.__name__,
        }
    if kind == "flags":
        names = ["A", "I", "L", "M", "S", "X", "U", "ASCII", "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "VERBOSE", "UNICODE", "NOFLAG", "DEBUG"]
        return {
            "values": {name: int(getattr(module, name)) for name in names},
            "aliases": [module.A is module.ASCII, module.I is module.IGNORECASE, module.L is module.LOCALE, module.M is module.MULTILINE, module.S is module.DOTALL, module.X is module.VERBOSE, module.U is module.UNICODE],
            "members": [[item.name, int(item)] for item in module.RegexFlag],
            "combined": int(module.I | module.M | module.S),
            "type": module.RegexFlag.__name__,
            "noflag_repr": repr(module.NOFLAG),
        }
    if kind == "cache":
        flags = flags_value(module, case["flags"])
        module.purge()
        first = module.compile(case["pattern"], flags)
        second = module.compile(case["pattern"], flags)
        module.purge()
        third = module.compile(case["pattern"], flags)
        return {"same_before_purge": first is second, "same_after_purge": first is third, "pattern": pattern_info(first)}
    if kind == "compile":
        return pattern_info(module.compile(case["pattern"], flags_value(module, case["flags"])))
    if kind == "call":
        return result_info(call_case(module, case))
    if kind == "property":
        flags = flags_value(module, case["flags"])
        pattern = module.compile(case["pattern"], flags)
        string = case["string"]
        matches = list(pattern.finditer(string))
        if pattern.groups == 0:
            derived_findall = [item.group(0) for item in matches]
        elif pattern.groups == 1:
            empty = b"" if isinstance(string, bytes) else ""
            derived_findall = [item.group(1) if item.group(1) is not None else empty for item in matches]
        else:
            empty = b"" if isinstance(string, bytes) else ""
            derived_findall = [tuple(value if value is not None else empty for value in item.groups()) for item in matches]
        repl = b"#" if isinstance(string, bytes) else "#"
        substituted, replacement_count = pattern.subn(repl, string, count=case["count"])
        return {
            "search_surface_equal": result_info(module.search(case["pattern"], string, flags)) == result_info(pattern.search(string)),
            "match_surface_equal": result_info(module.match(case["pattern"], string, flags)) == result_info(pattern.match(string)),
            "fullmatch_surface_equal": result_info(module.fullmatch(case["pattern"], string, flags)) == result_info(pattern.fullmatch(string)),
            "finditer_surface_equal": result_info(module.finditer(case["pattern"], string, flags)) == result_info(iter(matches)),
            "findall_from_finditer": jsonable(pattern.findall(string)) == jsonable(derived_findall),
            "split_surface_equal": jsonable(module.split(case["pattern"], string, flags=flags)) == jsonable(pattern.split(string)),
            "sub_equals_subn": jsonable(pattern.sub(repl, string, count=case["count"])) == jsonable(substituted),
            "subn_count_bounded": replacement_count >= 0 and (case["count"] == 0 or replacement_count <= case["count"]),
            "escape_roundtrip": pattern_info(module.compile(module.escape(string))) is not None and module.fullmatch(module.escape(string), string) is not None,
        }
    if kind == "escape":
        return jsonable(module.escape(case["value"]))
    if kind == "scanner":
        pattern = module.compile(case["pattern"], flags_value(module, case["flags"]))
        scanner = pattern.scanner(case["string"])
        method = getattr(scanner, case["method"])
        return {"pattern": pattern_info(scanner.pattern), "public": sorted(name for name in dir(scanner) if not name.startswith("_")), "results": [match_info(method()) for _ in range(case["calls"])]}
    if kind == "roundtrip":
        pattern = module.compile(case["pattern"], flags_value(module, case["flags"]))
        return {"copy_same": copy.copy(pattern) is pattern, "deepcopy_same": copy.deepcopy(pattern) is pattern, "pickle": pattern_info(pickle.loads(pickle.dumps(pattern)))}
    if kind == "error":
        try:
            action = case["action"]
            flags = flags_value(module, case["flags"])
            if action == "compile":
                module.compile(case["pattern"], flags)
            elif action == "search":
                module.search(case["pattern"], case["string"], flags)
            elif action == "sub":
                module.sub(case["pattern"], case["repl"], case["string"], flags=flags)
            else:
                raise RuntimeError(f"unknown error action: {action}")
        except Exception as error:
            return exception_info(error)
        return {"unexpected_success": True}
    if kind == "warning":
        with warnings.catch_warnings(record=True) as seen:
            warnings.simplefilter("always")
            module.compile(case["pattern"], flags_value(module, case["flags"]))
        return [{"type": item.category.__name__, "message": str(item.message)} for item in seen]
    if kind == "debug":
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            module.compile(case["pattern"], flags_value(module, case["flags"]))
        return {"nonempty": bool(stream.getvalue().strip())}
    raise RuntimeError(f"unknown case kind: {kind}")


def validate_suite(suite, cases):
    ids = [case["id"] for case in cases]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        raise RuntimeError(f"duplicate case IDs: {duplicates}")
    invalid = sorted({item for case in cases for item in case["obligations"] if item not in suite.OBLIGATIONS})
    if invalid:
        raise RuntimeError(f"unknown obligations: {invalid}")
    mapped = {item for case in cases for item in case["obligations"]}
    missing = sorted(set(suite.OBLIGATIONS) - mapped)
    if missing:
        raise RuntimeError(f"unmapped obligations: {missing}")
    seeds_path = ROOT / "oracle" / "v1" / "seeds.json"
    if seeds_path.exists() and json.loads(seeds_path.read_text(encoding="utf-8")) != suite.SEEDS:
        raise RuntimeError("frozen seeds.json differs from suite seeds")
    if hashlib.sha256((ROOT / "GOAL.md").read_bytes()).hexdigest() != GOAL_HASH:
        raise RuntimeError("GOAL.md hash changed")


def output_records(module, cases):
    for case in cases:
        yield {"id": case["id"], "kind": case["kind"], "obligations": case["obligations"], "result": execute(module, case)}


def encoded_records(records):
    return "".join(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for record in records).encode("utf-8")


def check_runtime():
    if platform.python_implementation() != "CPython" or sys.version_info[:3] != (3, 14, 6):
        raise RuntimeError(f"oracle requires CPython 3.14.6, got {platform.python_implementation()} {sys.version.split()[0]}")
    locale.setlocale(locale.LC_CTYPE, "C")


def freeze(args):
    check_runtime()
    suite = suite_module()
    cases = suite.cases()
    validate_suite(suite, cases)
    module = importlib.import_module("re")
    first = encoded_records(output_records(module, cases))
    module.purge()
    second = encoded_records(output_records(module, cases))
    if first != second:
        raise RuntimeError("non-deterministic stdlib fixture generation")
    EXPECTED.parent.mkdir(parents=True, exist_ok=True)
    EXPECTED.write_bytes(first)
    counts = {}
    for case in cases:
        counts[case["kind"]] = counts.get(case["kind"], 0) + 1
    manifest = {
        "schema": "rebar-correctness-v1",
        "python": "3.14.6",
        "implementation": "CPython",
        "unicode": "16.0.0",
        "locale": "C",
        "goal_sha256": GOAL_HASH,
        "suite_sha256": hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "expected_sha256": hashlib.sha256(first).hexdigest(),
        "cases": len(cases),
        "obligations": len(suite.OBLIGATIONS),
        "mapped_obligations": len({item for case in cases for item in case["obligations"]}),
        "kinds": dict(sorted(counts.items())),
        "private_waivers": ["PRIVATE-CACHE-LAYOUT", "PRIVATE-DEBUG-TEXT"],
        "seeds": dict(sorted(suite.SEEDS.items())),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


def verify(args):
    check_runtime()
    suite = suite_module()
    cases = suite.cases()
    validate_suite(suite, cases)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_bytes = EXPECTED.read_bytes()
    if hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest() != manifest["suite_sha256"]:
        raise RuntimeError("suite differs from frozen manifest")
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != manifest["runner_sha256"]:
        raise RuntimeError("runner differs from frozen manifest")
    if hashlib.sha256(expected_bytes).hexdigest() != manifest["expected_sha256"]:
        raise RuntimeError("expected fixture differs from frozen manifest")
    expected = [json.loads(line) for line in expected_bytes.splitlines()]
    if len(expected) != len(cases) or len(cases) != manifest["cases"]:
        raise RuntimeError("case count differs from frozen manifest")
    if args.case:
        selected = [(case, want) for case, want in zip(cases, expected, strict=True) if case["id"] == args.case]
        if len(selected) != 1:
            raise RuntimeError(f"case ID not found exactly once: {args.case}")
        cases = [selected[0][0]]
        expected = [selected[0][1]]
    module = importlib.import_module(args.module)
    failures = []
    passed = 0
    for case, want in zip(cases, expected, strict=True):
        try:
            got = {"id": case["id"], "kind": case["kind"], "obligations": case["obligations"], "result": execute(module, case)}
        except BaseException as error:
            got = {"id": case["id"], "kind": case["kind"], "obligations": case["obligations"], "unexplained_exception": exception_info(error)}
        if got == want:
            passed += 1
        else:
            failures.append({"id": case["id"], "expected": want, "actual": got})
    result = {"schema": "rebar-correctness-result-v1", "module": args.module, "cases": len(cases), "passed": passed, "failed": len(failures), "obligations": manifest["obligations"], "mapped_obligations": manifest["mapped_obligations"], "expected_sha256": manifest["expected_sha256"], "failures": failures}
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    if failures:
        for item in failures[:10]:
            print(item["id"], file=sys.stderr)
        raise SystemExit(1)


def chart(args):
    result = json.loads(Path(args.input).read_text(encoding="utf-8"))
    cases = result["cases"]
    passed = result["passed"]
    failed = result["failed"]
    pass_width = int(680 * passed / cases) if cases else 0
    fail_width = 680 - pass_width
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="166" viewBox="0 0 760 166" role="img" aria-label="Correctness gate: {passed} passed, {failed} failed, {result['mapped_obligations']} of {result['obligations']} obligations mapped">
<rect width="760" height="166" fill="#ffffff"/>
<text x="28" y="36" font-family="sans-serif" font-size="22" font-weight="700" fill="#172033">Correctness oracle v1</text>
<text x="28" y="62" font-family="sans-serif" font-size="14" fill="#42526e">{result['module']}: {passed}/{cases} cases passed · {result['mapped_obligations']}/{result['obligations']} obligations mapped</text>
<rect x="28" y="82" width="680" height="28" rx="4" fill="#e5e7eb"/>
<rect x="28" y="82" width="{pass_width}" height="28" rx="4" fill="#15803d"/>
<rect x="{28 + pass_width}" y="82" width="{fail_width}" height="28" fill="#b91c1c"/>
<text x="28" y="139" font-family="monospace" font-size="13" fill="#172033">failed: {failed} · fixture: {result['expected_sha256'][:16]}…</text>
</svg>
'''
    Path(args.output).write_text(svg, encoding="utf-8")
    print(f"wrote {args.output}")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("freeze").set_defaults(function=freeze)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--module", default="re")
    verify_parser.add_argument("--output")
    verify_parser.add_argument("--case", help="reproduce one frozen case by its stable ID")
    verify_parser.set_defaults(function=verify)
    chart_parser = subparsers.add_parser("chart")
    chart_parser.add_argument("--input", required=True)
    chart_parser.add_argument("--output", required=True)
    chart_parser.set_defaults(function=chart)
    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
