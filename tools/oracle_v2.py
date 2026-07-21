#!/usr/bin/env python3
"""Freeze and verify the expanded CPython 3.14 re correctness oracle."""

import argparse
import copy
import hashlib
import importlib
import importlib.util
import json
import pickle
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1_RUNNER = ROOT / "tools" / "oracle.py"
v1_spec = importlib.util.spec_from_file_location("rebar_oracle_v1_runner", V1_RUNNER)
v1 = importlib.util.module_from_spec(v1_spec)
v1_spec.loader.exec_module(v1)
SUITE_PATH = ROOT / "oracle" / "v2" / "suite.py"
EXPECTED = ROOT / "oracle" / "v2" / "expected.jsonl"
MANIFEST = ROOT / "oracle" / "v2" / "manifest.json"
SEEDS = ROOT / "oracle" / "v2" / "seeds.json"
PARENT_EXPECTED = ROOT / "oracle" / "v1" / "expected.jsonl"
PARENT_MANIFEST = ROOT / "oracle" / "v1" / "manifest.json"
GOAL_HASH = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"


def suite_module():
    spec = importlib.util.spec_from_file_location("rebar_oracle_v2_suite", SUITE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def materialize(value, kind):
    if kind == "bytes":
        return value
    if kind == "bytearray":
        return bytearray(value)
    if kind == "memoryview":
        return memoryview(value)
    raise RuntimeError(f"unknown bytes-like kind: {kind}")


def result_info(value, subject=None):
    if hasattr(value, "group") and hasattr(value, "span"):
        if not isinstance(value.string, (bytes, bytearray, memoryview)):
            return v1.match_info(value)
        default = b"<missing>"
        indexes = list(range(value.re.groups + 1))
        return {"bool": bool(value), "group0": v1.jsonable(value.group(0)), "groups": v1.jsonable(value.groups()), "groups_default": v1.jsonable(value.groups(default)), "groupdict": v1.jsonable(value.groupdict()), "groupdict_default": v1.jsonable(value.groupdict(default)), "items": v1.jsonable([value[index] for index in indexes]), "starts": v1.jsonable([value.start(index) for index in indexes]), "ends": v1.jsonable([value.end(index) for index in indexes]), "spans": v1.jsonable([value.span(index) for index in indexes]), "regs": v1.jsonable(value.regs), "lastindex": value.lastindex, "lastgroup": value.lastgroup, "pos": value.pos, "endpos": value.endpos, "string": {"type": type(value.string).__name__, "bytes_hex": bytes(value.string).hex()}, "string_is_subject": value.string is subject, "expand": v1.jsonable(value.expand(b"<\\g<0>>")), "re": v1.pattern_info(value.re), "public": sorted(name for name in dir(value) if not name.startswith("_"))}
    if isinstance(value, list):
        return [result_info(item, subject) for item in value]
    if isinstance(value, tuple):
        return [result_info(item, subject) for item in value]
    if hasattr(value, "__next__"):
        return [result_info(item, subject) for item in value]
    if isinstance(value, (bytearray, memoryview)):
        return {"type": type(value).__name__, "bytes_hex": bytes(value).hex()}
    return v1.jsonable(value)


def execute(module, case):
    kind = case["kind"]
    if kind == "byteslike":
        subject = materialize(case["string"], case["subject_kind"])
        flags = v1.flags_value(module, case["flags"])
        api = case["api"]
        kwargs = {}
        if api == "split":
            kwargs["maxsplit"] = case.get("maxsplit", 0)
        if api in {"sub", "subn"}:
            kwargs["count"] = case.get("count", 0)
            replacement = materialize(case["repl"], case["replacement_kind"])
        if case["surface"] == "module":
            function = getattr(module, api)
            if api in {"sub", "subn"}:
                value = function(case["pattern"], replacement, subject, flags=flags, **kwargs)
            else:
                value = function(case["pattern"], subject, flags=flags, **kwargs)
        else:
            function = getattr(module.compile(case["pattern"], flags), api)
            value = function(replacement, subject, **kwargs) if api in {"sub", "subn"} else function(subject, **kwargs)
        return result_info(value, subject)
    if kind == "byteslike-escape":
        return v1.jsonable(module.escape(materialize(case["value"], case["value_kind"])))
    if kind == "generic":
        argument = str if case["argument"] == "str" else bytes
        alias = getattr(module, case["owner"])[argument]
        return {"type": type(alias).__name__, "origin": alias.__origin__.__name__, "arguments": [item.__name__ for item in alias.__args__]}
    if kind == "representation":
        flags = v1.flags_value(module, case["flags"])
        if case["target"] == "pattern":
            return repr(module.compile(case["pattern"], flags))
        return repr(module.search(case["pattern"], case["string"], flags))
    if kind == "pattern-equality":
        flags = v1.flags_value(module, case["flags"])
        module.purge()
        first = module.compile(case["pattern"], flags)
        module.purge()
        second = module.compile(case["pattern"], flags)
        other = module.compile(case["pattern"] + "b", flags)
        return {"equal_after_purge": first == second, "hash_equal_after_purge": hash(first) == hash(second), "different_pattern_unequal": first != other}
    if kind == "match-copy":
        match = module.search(case["pattern"], case["string"], v1.flags_value(module, case["flags"]))
        if case["action"] == "copy":
            value = copy.copy(match)
            return {"same": value is match, "match": v1.match_info(value)}
        if case["action"] == "deepcopy":
            value = copy.deepcopy(match)
            return {"same": value is match, "match": v1.match_info(value)}
        try:
            pickle.dumps(match)
        except Exception as error:
            return v1.exception_info(error)
        return {"unexpected_success": True}
    if kind == "positional-warning":
        flags = v1.flags_value(module, case["flags"])
        with warnings.catch_warnings(record=True) as seen:
            warnings.simplefilter("always")
            if case["api"] == "split":
                value = module.split(case["pattern"], case["string"], case["count"], flags)
            else:
                value = getattr(module, case["api"])(case["pattern"], case["repl"], case["string"], case["count"], flags)
        return {"result": result_info(value), "warnings": [{"type": item.category.__name__, "message": str(item.message)} for item in seen]}
    return v1.execute(module, case)


def records(module, cases):
    for case in cases:
        result = execute(module, case)
        if case["kind"] in {"error", "match-copy"} and result.get("unexpected_success"):
            raise RuntimeError(f"invalid-input case unexpectedly succeeds: {case['id']}")
        if case["kind"] == "property" and not all(result.values()):
            raise RuntimeError(f"self-oracle property is false: {case['id']}")
        yield {"id": case["id"], "kind": case["kind"], "obligations": case["obligations"], "result": result}


def encoded(records):
    return "".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for item in records).encode("utf-8")


def validate(suite, cases):
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate case IDs")
    mapped = {item for case in cases for item in case["obligations"]}
    unknown = sorted(mapped - set(suite.OBLIGATIONS))
    missing = sorted(set(suite.OBLIGATIONS) - mapped)
    if unknown or missing:
        raise RuntimeError(f"obligation mapping failure: unknown={unknown}, missing={missing}")
    if SEEDS.exists() and json.loads(SEEDS.read_text(encoding="utf-8")) != suite.SEEDS:
        raise RuntimeError("frozen seeds differ from suite")
    if hashlib.sha256((ROOT / "GOAL.md").read_bytes()).hexdigest() != GOAL_HASH:
        raise RuntimeError("GOAL.md hash changed")
    parent = json.loads(PARENT_MANIFEST.read_text(encoding="utf-8"))
    if hashlib.sha256(PARENT_EXPECTED.read_bytes()).hexdigest() != parent["expected_sha256"]:
        raise RuntimeError("v1 parent fixture changed")
    return parent


def freeze(_args):
    v1.check_runtime()
    suite = suite_module()
    cases = suite.cases()
    parent = validate(suite, cases)
    baseline = importlib.import_module("re")
    first = encoded(records(baseline, cases))
    baseline.purge()
    second = encoded(records(baseline, cases))
    if first != second:
        raise RuntimeError("non-deterministic stdlib fixture generation")
    EXPECTED.parent.mkdir(parents=True, exist_ok=True)
    EXPECTED.write_bytes(first)
    SEEDS.write_text(json.dumps(suite.SEEDS, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    kinds = {}
    for case in cases:
        kinds[case["kind"]] = kinds.get(case["kind"], 0) + 1
    manifest = {"schema": "rebar-correctness-v2", "python": "3.14.6", "implementation": "CPython", "unicode": "16.0.0", "locale": "C", "goal_sha256": GOAL_HASH, "parent_expected_sha256": parent["expected_sha256"], "suite_sha256": hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(), "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "expected_sha256": hashlib.sha256(first).hexdigest(), "cases": len(cases), "obligations": len(suite.OBLIGATIONS), "mapped_obligations": len({item for case in cases for item in case["obligations"]}), "kinds": dict(sorted(kinds.items())), "private_waivers": ["PRIVATE-CACHE-LAYOUT", "PRIVATE-DEBUG-TEXT"], "seeds": dict(sorted(suite.SEEDS.items()))}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


def verify(args):
    v1.check_runtime()
    suite = suite_module()
    cases = suite.cases()
    validate(suite, cases)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_bytes = EXPECTED.read_bytes()
    checks = [("suite", hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(), manifest["suite_sha256"]), ("runner", hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), manifest["runner_sha256"]), ("expected", hashlib.sha256(expected_bytes).hexdigest(), manifest["expected_sha256"])]
    if any(got != want for _, got, want in checks):
        raise RuntimeError(f"frozen oracle drift: {checks}")
    expected = [json.loads(line) for line in expected_bytes.splitlines()]
    if len(expected) != len(cases) or len(cases) != manifest["cases"]:
        raise RuntimeError("case count differs from frozen manifest")
    if args.case:
        selected = [(case, want) for case, want in zip(cases, expected, strict=True) if case["id"] == args.case]
        if len(selected) != 1:
            raise RuntimeError(f"case ID not found exactly once: {args.case}")
        cases, expected = [selected[0][0]], [selected[0][1]]
    module = importlib.import_module(args.module)
    failures = []
    passed = 0
    for case, want in zip(cases, expected, strict=True):
        try:
            actual = {"id": case["id"], "kind": case["kind"], "obligations": case["obligations"], "result": execute(module, case)}
        except BaseException as error:
            actual = {"id": case["id"], "kind": case["kind"], "obligations": case["obligations"], "unexplained_exception": v1.exception_info(error)}
        if actual == want:
            passed += 1
        else:
            failures.append({"id": case["id"], "expected": want, "actual": actual})
    result = {"schema": "rebar-correctness-result-v2", "module": args.module, "cases": len(cases), "passed": passed, "failed": len(failures), "obligations": manifest["obligations"], "mapped_obligations": manifest["mapped_obligations"], "expected_sha256": manifest["expected_sha256"], "failures": failures}
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    if failures:
        for item in failures[:20]:
            print(item["id"], file=sys.stderr)
        raise SystemExit(1)


def chart(args):
    result = json.loads(Path(args.input).read_text(encoding="utf-8"))
    width = int(680 * result["passed"] / result["cases"]) if result["cases"] else 0
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="170" viewBox="0 0 800 170" role="img" aria-label="Correctness gate: {result['passed']} passed, {result['failed']} failed">
<rect width="800" height="170" fill="#fff"/>
<text x="28" y="36" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#0f172a">Expanded correctness oracle v2</text>
<text x="28" y="62" font-family="Arial, sans-serif" font-size="14" fill="#475569">{result['module']}: {result['passed']}/{result['cases']} cases passed · {result['mapped_obligations']}/{result['obligations']} obligations mapped</text>
<rect x="28" y="82" width="680" height="28" rx="4" fill="#b91c1c"/><rect x="28" y="82" width="{width}" height="28" rx="4" fill="#15803d"/>
<text x="28" y="142" font-family="monospace" font-size="13" fill="#334155">failed: {result['failed']} · fixture: {result['expected_sha256'][:16]}…</text></svg>\n'''
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(svg, encoding="utf-8")
    print(f"wrote {args.output}")


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("freeze").set_defaults(function=freeze)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--module", default="re")
    verify_parser.add_argument("--output")
    verify_parser.add_argument("--case")
    verify_parser.set_defaults(function=verify)
    chart_parser = commands.add_parser("chart")
    chart_parser.add_argument("--input", required=True)
    chart_parser.add_argument("--output", required=True)
    chart_parser.set_defaults(function=chart)
    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
