#!/usr/bin/env python3
"""Freeze and verify the large deterministic CPython re correctness holdout."""

import argparse
import hashlib
import importlib
import importlib.util
import json
import signal
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V2_RUNNER = ROOT / "tools" / "oracle_v2.py"
v2_spec = importlib.util.spec_from_file_location("rebar_oracle_v2_runner", V2_RUNNER)
v2 = importlib.util.module_from_spec(v2_spec)
v2_spec.loader.exec_module(v2)
v1 = v2.v1
SUITE_PATH = ROOT / "oracle" / "v3" / "suite.py"
EXPECTED = ROOT / "oracle" / "v3" / "expected.jsonl"
MANIFEST = ROOT / "oracle" / "v3" / "manifest.json"
SEEDS = ROOT / "oracle" / "v3" / "seeds.json"
PARENT_EXPECTED = ROOT / "oracle" / "v2" / "expected.jsonl"
PARENT_MANIFEST = ROOT / "oracle" / "v2" / "manifest.json"
GOAL_HASH = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
CASE_TIMEOUT_SECONDS = 1.0


def suite_module():
    spec = importlib.util.spec_from_file_location("rebar_oracle_v3_suite", SUITE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def subject(value, kind):
    if kind in {"text", "bytes"}:
        return value
    if kind == "bytearray":
        return bytearray(value)
    if kind == "memoryview":
        return memoryview(bytearray(value))
    raise RuntimeError(f"unknown subject kind: {kind}")


def replacement(value):
    if not isinstance(value, dict):
        return value
    if value.get("callable") != "bracket_upper":
        raise RuntimeError(f"unknown callable replacement: {value!r}")

    def bracket_upper(match):
        text = match.group(0)
        return b"[" + text.upper() + b"]" if isinstance(text, bytes) else "[" + text.upper() + "]"

    return bracket_upper


def hold_call(module, case):
    value = subject(case["string"], case["subject_kind"])
    flags = v1.flags_value(module, case["flags"])
    api = case["api"]
    kwargs = {}
    if api == "split":
        kwargs["maxsplit"] = case.get("maxsplit", 0)
    if api in {"sub", "subn"}:
        kwargs["count"] = case.get("count", 0)
    if case["surface"] == "module":
        function = getattr(module, api)
        result = function(case["pattern"], replacement(case["repl"]), value, flags=flags, **kwargs) if api in {"sub", "subn"} else function(case["pattern"], value, flags=flags, **kwargs)
    else:
        function = getattr(module.compile(case["pattern"], flags), api)
        if api in {"search", "match", "fullmatch", "findall", "finditer"}:
            if "pos" in case:
                kwargs["pos"] = case["pos"]
            if "endpos" in case:
                kwargs["endpos"] = case["endpos"]
        result = function(replacement(case["repl"]), value, **kwargs) if api in {"sub", "subn"} else function(value, **kwargs)
    return v2.result_info(result, value)


def scanner_case(module, case):
    value = subject(case["string"], case["subject_kind"])
    pattern = module.compile(case["pattern"], v1.flags_value(module, case["flags"]))
    scanner = pattern.scanner(value, pos=case["pos"], endpos=case["endpos"])
    mutations = {}
    for item in case["mutations"]:
        mutations.setdefault(item["after"], []).append(item)
    results = []
    for index, method in enumerate(case["methods"]):
        result = getattr(scanner, method)()
        results.append(v2.result_info(result, value))
        for item in mutations.get(index, ()):
            value[item["index"]] = item["value"]
    return {"pattern": v1.pattern_info(scanner.pattern), "public": sorted(name for name in dir(scanner) if not name.startswith("_")), "results": results, "final_subject": v1.jsonable(bytes(value) if not isinstance(value, str) else value)}


def property_case(module, case):
    value = subject(case["string"], case["subject_kind"])
    flags = v1.flags_value(module, case["flags"])
    pattern = module.compile(case["pattern"], flags)
    matches = list(pattern.finditer(value))
    window_matches = list(pattern.finditer(value, case["pos"], case["endpos"]))
    byte_mode = not isinstance(value, str)
    empty = b"" if byte_mode else ""
    if pattern.groups == 0:
        derived_findall = [item.group(0) for item in matches]
        derived_window = [item.group(0) for item in window_matches]
    elif pattern.groups == 1:
        derived_findall = [item.group(1) if item.group(1) is not None else empty for item in matches]
        derived_window = [item.group(1) if item.group(1) is not None else empty for item in window_matches]
    else:
        derived_findall = [tuple(part if part is not None else empty for part in item.groups()) for item in matches]
        derived_window = [tuple(part if part is not None else empty for part in item.groups()) for item in window_matches]
    repl = b"#" if byte_mode else "#"
    substituted, replacement_count = pattern.subn(repl, value, count=case["count"])
    scanner = pattern.scanner(value, pos=case["pos"], endpos=case["endpos"])
    scanned = []
    while True:
        item = scanner.search()
        if item is None:
            break
        scanned.append(item)
    escaped = module.escape(value)
    return {
        "search_surface_equal": v2.result_info(module.search(case["pattern"], value, flags), value) == v2.result_info(pattern.search(value), value),
        "match_surface_equal": v2.result_info(module.match(case["pattern"], value, flags), value) == v2.result_info(pattern.match(value), value),
        "fullmatch_surface_equal": v2.result_info(module.fullmatch(case["pattern"], value, flags), value) == v2.result_info(pattern.fullmatch(value), value),
        "finditer_surface_equal": v2.result_info(module.finditer(case["pattern"], value, flags), value) == v2.result_info(iter(matches), value),
        "findall_from_finditer": v1.jsonable(pattern.findall(value)) == v1.jsonable(derived_findall),
        "window_findall_from_finditer": v1.jsonable(pattern.findall(value, case["pos"], case["endpos"])) == v1.jsonable(derived_window),
        "scanner_from_window_finditer": v2.result_info(iter(scanned), value) == v2.result_info(iter(window_matches), value),
        "split_surface_equal": v1.jsonable(module.split(case["pattern"], value, flags=flags)) == v1.jsonable(pattern.split(value)),
        "sub_equals_subn": v1.jsonable(pattern.sub(repl, value, count=case["count"])) == v1.jsonable(substituted),
        "subn_count_bounded": replacement_count >= 0 and (case["count"] == 0 or replacement_count <= case["count"]),
        "escape_roundtrip": module.fullmatch(escaped, value) is not None,
    }


def execute(module, case):
    if case["kind"] == "hold-call":
        return hold_call(module, case)
    if case["kind"] == "hold-scanner":
        return scanner_case(module, case)
    if case["kind"] == "hold-property":
        return property_case(module, case)
    return v2.execute(module, case)


def guarded_execute(module, case):
    def expired(_signum, _frame):
        raise TimeoutError(f"correctness case exceeded {CASE_TIMEOUT_SECONDS:g}s: {case['id']}")

    previous = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, CASE_TIMEOUT_SECONDS)
    try:
        return execute(module, case)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def records(module, cases):
    for case in cases:
        result = guarded_execute(module, case)
        if case["kind"] == "error" and result.get("unexpected_success"):
            raise RuntimeError(f"invalid-input case unexpectedly succeeds: {case['id']}")
        if case["kind"] in {"property", "hold-property"} and not all(result.values()):
            raise RuntimeError(f"self-oracle property is false: {case['id']}")
        yield {"id": case["id"], "kind": case["kind"], "obligations": case["obligations"], "result": result}


def encoded(items):
    return "".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for item in items).encode("utf-8")


def family(case_id):
    if not case_id.startswith("v3.hold."):
        return "parent"
    if case_id.startswith("v3.hold.deep.text."):
        return "deep-text"
    if case_id.startswith("v3.hold.deep.bytes."):
        return "deep-bytes"
    if case_id.startswith("v3.hold.real.text."):
        return "real-text"
    if case_id.startswith("v3.hold.real.bytes."):
        return "real-bytes"
    if case_id.startswith("v3.hold.scanner."):
        return "scanner"
    if case_id.startswith("v3.hold.property."):
        return "properties"
    if case_id.startswith("v3.hold.invalid-pattern."):
        return "invalid-pattern"
    if case_id.startswith("v3.hold.invalid-template."):
        return "invalid-template"
    raise RuntimeError(f"unknown correctness family: {case_id}")


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
    parent_checks = ((PARENT_EXPECTED, "expected_sha256"), (ROOT / "oracle" / "v2" / "suite.py", "suite_sha256"), (V2_RUNNER, "runner_sha256"))
    if any(hashlib.sha256(path.read_bytes()).hexdigest() != parent[key] for path, key in parent_checks):
        raise RuntimeError("v2 parent fixture changed")
    families = {}
    for case_id in ids:
        name = family(case_id)
        families[name] = families.get(name, 0) + 1
    if families.get("parent") != parent["cases"]:
        raise RuntimeError("parent case count changed")
    expected_families = {"parent": parent["cases"], **suite.HOLDOUT_COUNTS}
    if families != expected_families:
        raise RuntimeError(f"holdout family counts changed: {families} != {expected_families}")
    return parent, families


def freeze(_args):
    v1.check_runtime()
    suite = suite_module()
    cases = suite.cases()
    parent, families = validate(suite, cases)
    baseline = importlib.import_module("re")
    first = encoded(records(baseline, cases))
    baseline.purge()
    second = encoded(records(baseline, cases))
    if first != second:
        raise RuntimeError("non-deterministic stdlib fixture generation")
    parent_bytes = PARENT_EXPECTED.read_bytes()
    if not first.startswith(parent_bytes):
        raise RuntimeError("v2 parent records are not preserved byte-for-byte")
    EXPECTED.parent.mkdir(parents=True, exist_ok=True)
    EXPECTED.write_bytes(first)
    SEEDS.write_text(json.dumps(suite.SEEDS, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    kinds = {}
    for case in cases:
        kinds[case["kind"]] = kinds.get(case["kind"], 0) + 1
    holdout = len(cases) - parent["cases"]
    manifest = {"schema": "rebar-correctness-v3", "python": "3.14.6", "implementation": "CPython", "unicode": "16.0.0", "locale": "C", "goal_sha256": GOAL_HASH, "parent_expected_sha256": parent["expected_sha256"], "suite_sha256": hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(), "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "expected_sha256": hashlib.sha256(first).hexdigest(), "cases": len(cases), "cohorts": {"parent": parent["cases"], "holdout": holdout}, "families": families, "obligations": len(suite.OBLIGATIONS), "mapped_obligations": len({item for case in cases for item in case["obligations"]}), "kinds": dict(sorted(kinds.items())), "case_timeout_seconds": CASE_TIMEOUT_SECONDS, "private_waivers": ["PRIVATE-CACHE-LAYOUT", "PRIVATE-DEBUG-TEXT"], "seeds": dict(sorted(suite.SEEDS.items()))}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


def verify(args):
    v1.check_runtime()
    suite = suite_module()
    cases = suite.cases()
    _, families = validate(suite, cases)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_bytes = EXPECTED.read_bytes()
    checks = (("suite", hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(), manifest["suite_sha256"]), ("runner", hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), manifest["runner_sha256"]), ("expected", hashlib.sha256(expected_bytes).hexdigest(), manifest["expected_sha256"]))
    if any(got != want for _, got, want in checks):
        raise RuntimeError(f"frozen oracle drift: {checks}")
    if families != manifest["families"]:
        raise RuntimeError("frozen family counts differ from suite")
    expected = [json.loads(line) for line in expected_bytes.splitlines()]
    if len(expected) != len(cases) or len(cases) != manifest["cases"]:
        raise RuntimeError("case count differs from frozen manifest")
    selected = list(zip(cases, expected, strict=True))
    if args.cohort == "holdout":
        selected = [(case, want) for case, want in selected if family(case["id"]) != "parent"]
    elif args.cohort == "parent":
        selected = [(case, want) for case, want in selected if family(case["id"]) == "parent"]
    if args.family:
        selected = [(case, want) for case, want in selected if family(case["id"]) == args.family]
    if args.case:
        selected = [(case, want) for case, want in selected if case["id"] == args.case]
        if len(selected) != 1:
            raise RuntimeError(f"case ID not found exactly once: {args.case}")
    module = importlib.import_module(args.module)
    failures = []
    passed = 0
    family_totals = {}
    family_passed = {}
    for case, want in selected:
        name = family(case["id"])
        family_totals[name] = family_totals.get(name, 0) + 1
        try:
            actual = {"id": case["id"], "kind": case["kind"], "obligations": case["obligations"], "result": guarded_execute(module, case)}
        except BaseException as error:
            actual = {"id": case["id"], "kind": case["kind"], "obligations": case["obligations"], "unexplained_exception": v1.exception_info(error)}
        if actual == want:
            passed += 1
            family_passed[name] = family_passed.get(name, 0) + 1
        else:
            failures.append({"id": case["id"], "expected": want, "actual": actual})
    result = {"schema": "rebar-correctness-result-v3", "module": args.module, "cohort": args.cohort, "family": args.family, "cases": len(selected), "passed": passed, "failed": len(failures), "obligations": manifest["obligations"], "mapped_obligations": manifest["mapped_obligations"], "expected_sha256": manifest["expected_sha256"], "families": {name: {"passed": family_passed.get(name, 0), "cases": total, "failed": total - family_passed.get(name, 0)} for name, total in sorted(family_totals.items())}, "failures": failures}
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    if failures:
        for item in failures[:30]:
            print(item["id"], file=sys.stderr)
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("freeze").set_defaults(function=freeze)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--module", default="re")
    verify_parser.add_argument("--cohort", choices=("all", "parent", "holdout"), default="all")
    verify_parser.add_argument("--family", choices=("parent", "deep-text", "deep-bytes", "real-text", "real-bytes", "scanner", "properties", "invalid-pattern", "invalid-template"))
    verify_parser.add_argument("--case")
    verify_parser.add_argument("--output")
    verify_parser.set_defaults(function=verify)
    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
