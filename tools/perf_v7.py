#!/usr/bin/env python3
"""Freeze and audit a broader, independently seeded Python ``re`` benchmark."""

from __future__ import annotations

import argparse
import array
import ctypes
import gc
import hashlib
import importlib
import importlib.util
import json
import math
import random
import statistics
import time
import tracemalloc
from collections import Counter
from pathlib import Path

from tools.perf_v5 import digest, encode, operation, proc_memory, snapshot, source_kind
from tools.perf_v6 import frozen as parent_frozen
from tools.perf_v6_analyze_fast import (
    helper as bootstrap_helper,
    pointer,
    self_test as bootstrap_self_test,
)


ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "performance" / "v7" / "suite.py"
EXPECTED_PATH = ROOT / "performance" / "v7" / "expected.jsonl"
MANIFEST_PATH = ROOT / "performance" / "v7" / "manifest.json"
PARENT_EXPECTED_PATH = ROOT / "performance" / "v6" / "expected.jsonl"
GOAL_HASH = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
ROW_SCHEMA = "rebar-performance-row-v7"
SUMMARY_SCHEMA = "rebar-performance-summary-v7"
COHORTS = ("calibration", "holdout")
REGRESSION_SLOWDOWN_FACTOR = 1.2
REGRESSION_SPEEDUP_THRESHOLD = 5.0 / 6.0


def is_runtime_regression(speedup):
    """Return whether candidate elapsed time is more than 20% greater."""
    return speedup < REGRESSION_SPEEDUP_THRESHOLD


def verify_regression_boundaries():
    expectations = (
        (0.80, True),
        (0.81, True),
        (0.833, True),
        (REGRESSION_SPEEDUP_THRESHOLD, False),
        (0.84, False),
        (1.0, False),
    )
    for value, expected in expectations:
        if is_runtime_regression(value) is not expected:
            raise RuntimeError(
                f"the exact 20% elapsed-time regression rule changed at {value}"
            )
    return {
        "regression_speedup_threshold": REGRESSION_SPEEDUP_THRESHOLD,
        "regression_boundary_checks": len(expectations),
    }


def stable_value(value):
    if isinstance(value, dict):
        return tuple(
            (key, stable_value(item))
            for key, item in sorted(value.items())
        )
    if isinstance(value, list):
        return tuple(stable_value(item) for item in value)
    return value


def semantic_key(case):
    """Describe the work actually performed, without IDs or timing counts."""
    api = case["api"]
    subject = None if api in {"compile", "escape"} else case.get("string")
    replacement = case.get("repl") if api in {"sub", "subn"} else None
    return (
        api,
        case["lifecycle"],
        stable_value(case["pattern"]),
        stable_value(subject),
        tuple(case["flags"]),
        case.get("subject_kind") if subject is not None else None,
        stable_value(replacement),
        case.get("replacement_kind") if replacement is not None else None,
        case.get("count") if api in {"sub", "subn"} else None,
        case.get("maxsplit") if api == "split" else None,
        case.get("pos"),
        case.get("endpos"),
        stable_value(case.get("expand")) if api == "match-surface" else None,
    )


def suite_module():
    specification = importlib.util.spec_from_file_location(
        "rebar_performance_v7", SUITE_PATH
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load the broader v7 performance suite")
    suite = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(suite)
    return suite


def validate_suite(suite, cases):
    parent_suite, parent_cases, _parent_records, parent = parent_frozen()
    correctness = json.loads(
        (ROOT / "oracle" / "v3" / "manifest.json").read_text(encoding="utf-8")
    )

    if cases[: len(parent_cases)] != parent_cases:
        raise RuntimeError("the broader v7 suite changed a frozen v6 case")
    if parent.get("schema") != "rebar-performance-v6" or parent.get("cases") != 12432:
        raise RuntimeError("the frozen v6 parent has changed")
    if suite.MODULES != parent_suite.MODULES:
        raise RuntimeError("the broader benchmark changed the independent engines")
    if (
        suite.TRIALS != parent_suite.TRIALS
        or suite.WARMUPS != parent_suite.WARMUPS
        or suite.BOOTSTRAPS != parent_suite.BOOTSTRAPS
    ):
        raise RuntimeError("the broader benchmark changed the frozen trial protocol")
    if len(suite.FAMILIES) != 64 or suite.VARIANTS != 64:
        raise RuntimeError("the broader benchmark must add 64 balanced families")
    if len(set(suite.FAMILIES)) != len(suite.FAMILIES):
        raise RuntimeError("the broader benchmark repeats a workload family")
    expected_domains = {
        "protocols",
        "source",
        "unicode",
        "lookaround",
        "backtracking",
        "buffers",
        "lifecycle",
        "density",
    }
    domains = Counter(item["domain"] for item in suite.SPECS)
    if set(domains) != expected_domains or any(count != 8 for count in domains.values()):
        raise RuntimeError("the broader benchmark changed its eight balanced workload groups")
    if set(suite.SEEDS) != set(COHORTS):
        raise RuntimeError("practice and holdout require separate stable seeds")
    seeds = tuple(suite.SEEDS[cohort] for cohort in COHORTS)
    if len(set(seeds)) != 2 or any(seed in parent_suite.SEEDS.values() for seed in seeds):
        raise RuntimeError("the broader benchmark reuses a frozen workload seed")
    if len({*seeds, suite.ORDER_SEED, suite.BOOTSTRAP_SEED}) != 4:
        raise RuntimeError("broader workload, order, and confidence seeds overlap")

    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        raise RuntimeError("the broader benchmark contains duplicate task IDs")
    if any(
        not isinstance(case.get("ops"), int)
        or isinstance(case.get("ops"), bool)
        or case["ops"] <= 0
        or case.get("weight") != 1
        for case in cases
    ):
        raise RuntimeError("every workload requires positive operations and equal weight")

    expected_total = parent["cases"] + 2 * len(suite.FAMILIES) * suite.VARIANTS
    if len(cases) != expected_total or suite.CASES_PER_COHORT != 10312:
        raise RuntimeError("the broader benchmark changed its 20,624-task denominator")

    allowed_apis = {
        "compile",
        "escape",
        "findall",
        "finditer",
        "fullmatch",
        "match",
        "match-surface",
        "scanner",
        "search",
        "split",
        "sub",
        "subn",
    }
    generated_by_cohort = {}
    for cohort in COHORTS:
        selected = [case for case in cases if case["cohort"] == cohort]
        if len(selected) != suite.CASES_PER_COHORT:
            raise RuntimeError(f"broader workload count changed: {cohort}")
        added = [case for case in selected if ".broader." in case["id"]]
        counts = Counter(case["category"] for case in added)
        wanted = {f"broader-{family}" for family in suite.FAMILIES}
        if (
            len(added) != len(suite.FAMILIES) * suite.VARIANTS
            or set(counts) != wanted
            or any(count != suite.VARIANTS for count in counts.values())
        ):
            raise RuntimeError(f"broader workload balance changed: {cohort}")
        generated_by_cohort[cohort] = {case["id"]: case for case in added}
        prefix = "cal" if cohort == "calibration" else "hold"
        for family in suite.FAMILIES:
            family_cases = [
                generated_by_cohort[cohort].get(
                    f"{prefix}.broader.{family}.{variant:02d}"
                )
                for variant in range(suite.VARIANTS)
            ]
            if any(case is None for case in family_cases):
                raise RuntimeError(
                    f"a broader workload variant is missing: {cohort} {family}"
                )
            if len({semantic_key(case) for case in family_cases}) != suite.VARIANTS:
                raise RuntimeError(
                    f"a broader workload repeats actual inputs: {cohort} {family}"
                )
        if {case["api"] for case in selected} != allowed_apis:
            raise RuntimeError(f"broader API coverage changed: {cohort}")
        if {case["api"] for case in added} != allowed_apis:
            raise RuntimeError(f"new broader families omit a Python re call: {cohort}")
        if {case["lifecycle"] for case in selected} != {
            "cold",
            "compiled",
            "module",
        }:
            raise RuntimeError(f"broader call lifecycle coverage changed: {cohort}")
        if {case["lifecycle"] for case in added} != {
            "cold",
            "compiled",
            "module",
        }:
            raise RuntimeError(f"new broader families omit a call lifecycle: {cohort}")
        if not {"text", "bytes", "bytearray", "memoryview"}.issubset(
            {source_kind(case) for case in selected}
        ):
            raise RuntimeError(f"broader text and buffer coverage changed: {cohort}")
        if not {"text", "bytes", "bytearray", "memoryview"}.issubset(
            {source_kind(case) for case in added}
        ):
            raise RuntimeError(f"new broader families omit a text or buffer input: {cohort}")
        if not {1, 2, 4}.issubset(
            {
                width
                for case in added
                if (width := unicode_width(case)) is not None
            }
        ):
            raise RuntimeError(f"new broader families omit a native Unicode width: {cohort}")
        if not any(
            isinstance(case.get("string"), str)
            and any(0xD800 <= ord(value) <= 0xDFFF for value in case["string"])
            for case in added
        ):
            raise RuntimeError(f"new broader families omit lone-surrogate text: {cohort}")
        if not any(isinstance(case.get("repl"), dict) for case in added):
            raise RuntimeError(f"new broader families omit callback replacements: {cohort}")
        if not any(
            isinstance(case.get("repl"), (str, bytes))
            and (
                "\\g<" in case["repl"]
                if isinstance(case["repl"], str)
                else b"\\g<" in case["repl"]
            )
            for case in added
        ):
            raise RuntimeError(f"new broader families omit capture templates: {cohort}")
        if not any("pos" in case or "endpos" in case for case in added):
            raise RuntimeError(f"new broader families omit bounded input windows: {cohort}")
        if {
            case.get("maxsplit", 0)
            for case in added
            if case["api"] == "split"
        } != {0, 1, 2, 4, 8}:
            raise RuntimeError(f"new broader families omit split limits: {cohort}")
        if not {0, 1, 2, 4}.issubset(
            {
                case.get("count", 0)
                for case in added
                if case["api"] in {"sub", "subn"}
            }
        ):
            raise RuntimeError(f"new broader families omit replacement limits: {cohort}")

    practice_semantics = {}
    for case in generated_by_cohort["calibration"].values():
        practice_semantics.setdefault(semantic_key(case), []).append(case["id"])
    expected_added = len(suite.FAMILIES) * suite.VARIANTS
    if len(practice_semantics) != expected_added:
        raise RuntimeError("broader practice families share an executable scenario")
    collisions = []
    unseen_semantics = set()
    for case in generated_by_cohort["holdout"].values():
        actual = semantic_key(case)
        unseen_semantics.add(actual)
        for practice_id in practice_semantics.get(actual, ()):
            collisions.append((practice_id, case["id"]))
    if len(unseen_semantics) != expected_added:
        raise RuntimeError("broader unseen families share an executable scenario")
    if collisions:
        raise RuntimeError(
            "practice and unseen workloads are not independent: "
            f"{len(collisions)} collisions; first {collisions[:8]}"
        )

    if hashlib.sha256((ROOT / "GOAL.md").read_bytes()).hexdigest() != GOAL_HASH:
        raise RuntimeError("GOAL.md changed")
    if (
        correctness.get("schema") != "rebar-correctness-v3"
        or correctness.get("cases") != 44084
        or correctness.get("mapped_obligations") != 51
        or correctness.get("expected_sha256") != parent.get("correctness_expected_sha256")
    ):
        raise RuntimeError("the established complete correctness oracle changed")
    return correctness, parent


def records_for(module, cases):
    for index, case in enumerate(cases):
        try:
            result = snapshot(operation(module, case)())
        except BaseException as error:
            raise RuntimeError(
                f"baseline fixture failed: {case['id']}: "
                f"{type(error).__name__}: {error}"
            ) from error
        if index and index % 2048 == 0:
            print(f"checking the Python baseline {index}/{len(cases)}", flush=True)
        yield {
            "id": case["id"],
            "cohort": case["cohort"],
            "category": case["category"],
            "result": result,
            "result_sha256": digest(result),
        }


def unicode_width(case):
    subject = case.get("string")
    if not isinstance(subject, str):
        return None
    highest = max(map(ord, subject), default=0)
    if highest <= 0xFF:
        return 1
    if highest <= 0xFFFF:
        return 2
    return 4


def result_density(result):
    if result is None:
        return "zero"
    if isinstance(result, list):
        if not result:
            return "zero"
        if len(result) == 1:
            return "one"
        if len(result) < 16:
            return "few"
        return "many"
    return "one"


def freeze(_args):
    suite = suite_module()
    cases = suite.cases()
    correctness, parent = validate_suite(suite, cases)
    baseline = importlib.import_module("re")
    first = list(records_for(baseline, cases))
    baseline.purge()
    regenerated = suite.cases()
    if cases != regenerated:
        raise RuntimeError("the broader seeded workload generator is not deterministic")
    validate_suite(suite, regenerated)
    second = list(records_for(baseline, regenerated))
    if first != second:
        raise RuntimeError("Python re does not reproduce the broader fixture")

    parent_payload = PARENT_EXPECTED_PATH.read_bytes()
    if encode(first[: parent["cases"]]) != parent_payload:
        raise RuntimeError("the v7 fixture does not preserve every frozen v6 byte")
    payload = encode(first)
    EXPECTED_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPECTED_PATH.write_bytes(payload)
    manifest = {
        "schema": "rebar-performance-v7",
        "python": "3.14.6",
        "implementation": "CPython",
        "goal_sha256": GOAL_HASH,
        "correctness_expected_sha256": correctness["expected_sha256"],
        "parent_expected_sha256": parent["expected_sha256"],
        "parent_suite_sha256": parent["suite_sha256"],
        "parent_runner_sha256": parent["runner_sha256"],
        "parent_cases": parent["cases"],
        "suite_sha256": hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "expected_sha256": hashlib.sha256(payload).hexdigest(),
        "modules": suite.MODULES,
        "cases": len(cases),
        "cohorts": {cohort: suite.CASES_PER_COHORT for cohort in COHORTS},
        "weights": {cohort: suite.CASES_PER_COHORT for cohort in COHORTS},
        "expanded_families": len(suite.FAMILIES),
        "variants_per_family": suite.VARIANTS,
        "unique_variants_per_family": suite.VARIANTS,
        "practice_holdout_semantic_collisions": 0,
        "new_unique_semantic_scenarios": {
            cohort: len(suite.FAMILIES) * suite.VARIANTS
            for cohort in COHORTS
        },
        "domain_counts": dict(
            sorted(Counter(item["domain"] for item in suite.SPECS).items())
        ),
        "seeds": dict(sorted(suite.SEEDS.items())),
        "api_counts": dict(sorted(Counter(case["api"] for case in cases).items())),
        "lifecycle_counts": dict(
            sorted(Counter(case["lifecycle"] for case in cases).items())
        ),
        "input_counts": dict(sorted(Counter(source_kind(case) for case in cases).items())),
        "unicode_width_counts": dict(
            sorted(
                Counter(
                    str(width)
                    for case in cases
                    if (width := unicode_width(case)) is not None
                ).items()
            )
        ),
        "result_density_counts": dict(
            sorted(Counter(result_density(record["result"]) for record in first).items())
        ),
        "regression_rule": {
            "basis": "candidate elapsed time divided by Python re elapsed time",
            "slowdown_factor_exclusive": REGRESSION_SLOWDOWN_FACTOR,
            "speedup_threshold_exclusive": REGRESSION_SPEEDUP_THRESHOLD,
        },
        "split_limit_counts": dict(
            sorted(
                Counter(
                    str(case.get("maxsplit", 0))
                    for case in cases
                    if case["api"] == "split"
                ).items()
            )
        ),
        "replacement_limit_counts": dict(
            sorted(
                Counter(
                    str(case.get("count", 0))
                    for case in cases
                    if case["api"] in {"sub", "subn"}
                ).items()
            )
        ),
        "surrogate_subject_cases": sum(
            isinstance(case.get("string"), str)
            and any(0xD800 <= ord(value) <= 0xDFFF for value in case["string"])
            for case in cases
        ),
        "maximum_subject_length": max(
            len(case.get("string") or "") for case in cases
        ),
        "callable_replacement_cases": sum(
            isinstance(case.get("repl"), dict)
            and "callable" in case["repl"]
            for case in cases
        ),
        "trials": suite.TRIALS,
        "warmups": suite.WARMUPS,
        "order_seed": suite.ORDER_SEED,
        "bootstrap_seed": suite.BOOTSTRAP_SEED,
        "bootstraps": suite.BOOTSTRAPS,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, sort_keys=True))
    return manifest


def frozen():
    suite = suite_module()
    cases = suite.cases()
    correctness, parent = validate_suite(suite, cases)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    payload = EXPECTED_PATH.read_bytes()
    checks = (
        ("schema", manifest.get("schema"), "rebar-performance-v7"),
        ("suite", hashlib.sha256(SUITE_PATH.read_bytes()).hexdigest(), manifest.get("suite_sha256")),
        ("runner", hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), manifest.get("runner_sha256")),
        ("expected", hashlib.sha256(payload).hexdigest(), manifest.get("expected_sha256")),
        ("correctness", correctness["expected_sha256"], manifest.get("correctness_expected_sha256")),
        ("parent", parent["expected_sha256"], manifest.get("parent_expected_sha256")),
        ("parent suite", parent["suite_sha256"], manifest.get("parent_suite_sha256")),
        ("parent runner", parent["runner_sha256"], manifest.get("parent_runner_sha256")),
        ("parent cases", parent["cases"], manifest.get("parent_cases")),
        ("cases", len(cases), manifest.get("cases")),
        ("semantic collisions", 0, manifest.get("practice_holdout_semantic_collisions")),
        ("unique variants", suite.VARIANTS, manifest.get("unique_variants_per_family")),
        (
            "regression slowdown factor",
            REGRESSION_SLOWDOWN_FACTOR,
            manifest.get("regression_rule", {}).get("slowdown_factor_exclusive"),
        ),
        (
            "regression speedup threshold",
            REGRESSION_SPEEDUP_THRESHOLD,
            manifest.get("regression_rule", {}).get("speedup_threshold_exclusive"),
        ),
    )
    if any(actual != expected for _, actual, expected in checks):
        raise RuntimeError(f"broader frozen performance fixture drift: {checks}")
    records = [json.loads(line) for line in payload.splitlines()]
    if len(records) != len(cases):
        raise RuntimeError("broader performance fixture record count changed")
    if encode(records[: parent["cases"]]) != PARENT_EXPECTED_PATH.read_bytes():
        raise RuntimeError("a frozen v6 parent record changed")
    if any(
        (record.get("id"), record.get("cohort"), record.get("category"))
        != (case["id"], case["cohort"], case["category"])
        for case, record in zip(cases, records, strict=True)
    ):
        raise RuntimeError("a broader frozen case or record moved")
    return suite, cases, records, manifest


def correctness_gate(module, case, expected):
    actual = snapshot(operation(module, case)())
    actual_digest = digest(actual)
    if actual_digest != expected["result_sha256"] or actual != expected["result"]:
        raise RuntimeError(f"performance correctness mismatch: {module.__name__} {case['id']}")
    return actual_digest


def verify(args):
    suite, cases, expected, manifest = frozen()
    names = tuple(args.module or suite.MODULES)
    unknown = set(names) - set(suite.MODULES)
    if unknown:
        raise RuntimeError(f"unknown performance candidates: {sorted(unknown)}")
    failures = []
    for name in names:
        module = importlib.import_module(name)
        for index, (case, want) in enumerate(zip(cases, expected, strict=True)):
            try:
                correctness_gate(module, case, want)
            except BaseException as error:
                failures.append(
                    {
                        "module": name,
                        "case": case["id"],
                        "type": type(error).__name__,
                        "message": str(error),
                    }
                )
            if index and index % 2048 == 0:
                print(f"checking {name} {index}/{len(cases)}", flush=True)
    result = {
        "schema": "rebar-performance-correctness-v7",
        "modules": list(names),
        "cases_per_module": len(cases),
        "checks": len(cases) * len(names),
        "failed": len(failures),
        "expected_sha256": manifest["expected_sha256"],
        "failures": failures,
    }
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    if failures:
        for failure in failures[:40]:
            print(
                f"{failure['module']} {failure['case']}: "
                f"{failure['type']}: {failure['message']}",
                flush=True,
            )
        raise SystemExit(1)
    return result


def trial_order(suite, case, trial):
    order = list(suite.MODULES)
    random.Random(
        suite.ORDER_SEED + trial * 1009 + sum(map(ord, case["id"]))
    ).shuffle(order)
    return order


def verify_bootstrap_seed(suite):
    """Check the v7 seed against Python's exact independent paired draws."""
    native, _target = bootstrap_helper()
    values = array.array("I", (0 for _ in range(4096)))
    native.rebar_bootstrap_seed(suite.BOOTSTRAP_SEED)
    native.rebar_bootstrap_draws(pointer(values, ctypes.c_uint32), len(values))
    reference = random.Random(suite.BOOTSTRAP_SEED)
    expected = [reference.randrange(suite.TRIALS) for _ in values]
    if list(values) != expected:
        mismatch = next(
            index
            for index, (actual, wanted) in enumerate(
                zip(values, expected, strict=True)
            )
            if actual != wanted
        )
        raise RuntimeError(
            f"broader paired confidence draws changed at {mismatch}: "
            f"{values[mismatch]} != {expected[mismatch]}"
        )
    return {
        "v7_bootstrap_seed": suite.BOOTSTRAP_SEED,
        "v7_bootstrap_draws": len(values),
    }


def valid_process_memory(row):
    values = []
    for key in ("rss_before_kb", "rss_after_kb", "hwm_kb"):
        if key not in row:
            return False
        value = row[key]
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 0
        ):
            return False
        values.append(value)
    _before, after, high_water = values
    return after is None or high_water is None or high_water >= after


def measure(args):
    suite, cases, expected, manifest = frozen()
    modules = {name: importlib.import_module(name) for name in suite.MODULES}
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    with destination.open("w", encoding="utf-8") as stream:
        for case, want in zip(cases, expected, strict=True):
            for trial in range(suite.TRIALS):
                for order, name in enumerate(trial_order(suite, case, trial)):
                    module = modules[name]
                    expected_digest = correctness_gate(module, case, want)
                    action = operation(module, case)
                    for _ in range(suite.WARMUPS):
                        action()
                    tracemalloc.start()
                    try:
                        action()
                        _, peak = tracemalloc.get_traced_memory()
                    finally:
                        tracemalloc.stop()
                    before = proc_memory()
                    restore_gc = gc.isenabled()
                    if restore_gc:
                        gc.disable()
                    try:
                        started = time.perf_counter_ns()
                        result = None
                        for _ in range(case["ops"]):
                            result = action()
                        elapsed = time.perf_counter_ns() - started
                    finally:
                        if restore_gc:
                            gc.enable()
                    after = proc_memory()
                    timed = snapshot(result)
                    if digest(timed) != expected_digest or timed != want["result"]:
                        raise RuntimeError(f"post-timing correctness mismatch: {name} {case['id']}")
                    row = {
                        "schema": ROW_SCHEMA,
                        "case": case["id"],
                        "cohort": case["cohort"],
                        "category": case["category"],
                        "module": name,
                        "trial": trial,
                        "order": order,
                        "ops": case["ops"],
                        "elapsed_ns": elapsed,
                        "ns_per_op": elapsed / case["ops"],
                        "peak_traced_bytes": peak,
                        "rss_before_kb": before["rss_kb"],
                        "rss_after_kb": after["rss_kb"],
                        "hwm_kb": after["hwm_kb"],
                        "expected_sha256": expected_digest,
                    }
                    stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
                    rows += 1
            print(f"measured {case['id']} ({suite.TRIALS} paired trials)", flush=True)
    required = len(cases) * len(suite.MODULES) * suite.TRIALS
    if rows != required:
        raise RuntimeError(f"broader raw row count changed: {rows} != {required}")
    result = {
        "schema": "rebar-performance-measurement-v7",
        "cases": len(cases),
        "rows": rows,
        "modules": list(suite.MODULES),
        "trials": suite.TRIALS,
        "warmups": suite.WARMUPS,
        "expected_sha256": manifest["expected_sha256"],
        "output": str(destination),
    }
    print(json.dumps(result, sort_keys=True))
    return result


def analyze(args):
    suite, cases, expected, manifest = frozen()
    modules = tuple(suite.MODULES)
    candidates = modules[1:]
    trials = suite.TRIALS
    rows_per_case = len(modules) * trials
    required = len(cases) * rows_per_case
    times = array.array("d", (0 for _ in range(required)))
    memory = array.array("Q", (0 for _ in range(required)))
    seen = bytearray(required)
    raw_hash = hashlib.sha256()
    row_count = 0
    with Path(args.input).open("rb") as stream:
        for row_count, line in enumerate(stream, 1):
            if row_count > required:
                raise RuntimeError(f"too many broader raw rows: {row_count} > {required}")
            raw_hash.update(line)
            row = json.loads(line)
            case_index = (row_count - 1) // rows_per_case
            case = cases[case_index]
            trial = row.get("trial")
            module = row.get("module")
            if (
                not isinstance(trial, int)
                or isinstance(trial, bool)
                or not 0 <= trial < trials
                or module not in modules
            ):
                raise RuntimeError(f"broader raw trial or engine changed at row {row_count}")
            key = (case_index * len(modules) + modules.index(module)) * trials + trial
            if seen[key]:
                raise RuntimeError(f"duplicate broader result: {(case['id'], trial, module)}")
            elapsed = row.get("elapsed_ns")
            per_operation = row.get("ns_per_op")
            peak = row.get("peak_traced_bytes")
            if (
                row.get("schema") != ROW_SCHEMA
                or row.get("case") != case["id"]
                or row.get("cohort") != case["cohort"]
                or row.get("category") != case["category"]
                or row.get("ops") != case["ops"]
                or row.get("expected_sha256") != expected[case_index]["result_sha256"]
                or row.get("order") != trial_order(suite, case, trial).index(module)
                or not isinstance(elapsed, int)
                or isinstance(elapsed, bool)
                or elapsed <= 0
                or not isinstance(per_operation, (int, float))
                or isinstance(per_operation, bool)
                or not math.isfinite(per_operation)
                or per_operation != elapsed / case["ops"]
                or not isinstance(peak, int)
                or isinstance(peak, bool)
                or peak < 0
                or not valid_process_memory(row)
            ):
                raise RuntimeError(f"broader timing or frozen metadata changed at row {row_count}")
            seen[key] = 1
            times[key] = per_operation
            memory[key] = peak
    if row_count != required or not all(seen):
        raise RuntimeError(f"broader raw row count changed: {row_count} != {required}")

    logs = array.array("d", (0 for _ in range(len(cases) * len(candidates) * trials)))
    for case_index in range(len(cases)):
        baseline = case_index * len(modules) * trials
        for candidate_index, name in enumerate(candidates):
            source = (case_index * len(modules) + modules.index(name)) * trials
            target = (case_index * len(candidates) + candidate_index) * trials
            for trial in range(trials):
                logs[target + trial] = math.log(times[baseline + trial] / times[source + trial])

    native, _target = bootstrap_helper()
    native.rebar_bootstrap_seed(suite.BOOTSTRAP_SEED)
    lows = array.array("d", (0 for _ in range(len(cases) * len(candidates))))
    highs = array.array("d", (0 for _ in range(len(lows))))
    if native.rebar_bootstrap_cases(
        pointer(logs, ctypes.c_double),
        len(lows),
        trials,
        suite.BOOTSTRAPS,
        pointer(lows, ctypes.c_double),
        pointer(highs, ctypes.c_double),
    ):
        raise RuntimeError("broader case confidence-range calculation failed")

    results = []
    for case_index, case in enumerate(cases):
        baseline_offset = case_index * len(modules) * trials
        baseline_memory = memory[baseline_offset : baseline_offset + trials]
        for candidate_index, name in enumerate(candidates):
            result_index = case_index * len(candidates) + candidate_index
            values = logs[result_index * trials : (result_index + 1) * trials]
            candidate_offset = (case_index * len(modules) + modules.index(name)) * trials
            candidate_memory = memory[candidate_offset : candidate_offset + trials]
            speed = math.exp(statistics.fmean(values))
            low = lows[result_index]
            results.append(
                {
                    "case": case["id"],
                    "cohort": case["cohort"],
                    "category": case["category"],
                    "candidate": name,
                    "weight": case["weight"],
                    "speedup": speed,
                    "ci95_low": low,
                    "ci95_high": highs[result_index],
                    "peak_traced_ratio": statistics.median(candidate_memory)
                    / max(1, statistics.median(baseline_memory)),
                    "statistically_faster": low > 1,
                    "regression_gt_20pct": is_runtime_regression(speed),
                }
            )

    rankings = []
    for cohort in (*COHORTS, "all"):
        selected_indexes = [
            index for index, case in enumerate(cases)
            if cohort == "all" or case["cohort"] == cohort
        ]
        denominator = sum(cases[index]["weight"] for index in selected_indexes)
        wanted = suite.CASES_PER_COHORT * (2 if cohort == "all" else 1)
        if denominator != wanted:
            raise RuntimeError(f"broader ranking denominator changed: {cohort}")
        selected = array.array("I", selected_indexes)
        weights = array.array("d", (cases[index]["weight"] for index in selected_indexes))
        for candidate_index, name in enumerate(candidates):
            low = ctypes.c_double()
            high = ctypes.c_double()
            if native.rebar_bootstrap_overall(
                pointer(logs, ctypes.c_double),
                pointer(selected, ctypes.c_uint32),
                pointer(weights, ctypes.c_double),
                len(selected),
                len(candidates),
                candidate_index,
                trials,
                suite.BOOTSTRAPS,
                denominator,
                ctypes.byref(low),
                ctypes.byref(high),
            ):
                raise RuntimeError(f"broader overall confidence-range calculation failed: {name}")
            relevant = [
                row for row in results
                if row["candidate"] == name
                and (cohort == "all" or row["cohort"] == cohort)
            ]
            total = sum(
                statistics.fmean(
                    logs[
                        (index * len(candidates) + candidate_index) * trials :
                        (index * len(candidates) + candidate_index + 1) * trials
                    ]
                ) * cases[index]["weight"]
                for index in selected_indexes
            )
            rankings.append(
                {
                    "cohort": cohort,
                    "candidate": name,
                    "cases": len(selected_indexes),
                    "weight": denominator,
                    "geomean_speedup": math.exp(total / denominator),
                    "ci95_low": low.value,
                    "ci95_high": high.value,
                    "statistically_faster_cases": sum(
                        row["statistically_faster"] for row in relevant
                    ),
                    "regressions_gt_20pct": sum(
                        row["regression_gt_20pct"] for row in relevant
                    ),
                }
            )
    summary = {
        "schema": SUMMARY_SCHEMA,
        "expected_sha256": manifest["expected_sha256"],
        "raw_sha256": raw_hash.hexdigest(),
        "rows": row_count,
        "rankings": rankings,
        "case_results": results,
        "regressions": [row for row in results if row["regression_gt_20pct"]],
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    result = {
        "rows": row_count,
        "cases": len(cases),
        "results": len(results),
        "regressions": len(summary["regressions"]),
        "raw_sha256": summary["raw_sha256"],
        "output": str(destination),
    }
    print(json.dumps(result, sort_keys=True))
    return result


def self_test(_args):
    bootstrap = bootstrap_self_test()
    suite, cases, expected, manifest = frozen()
    seeded_draws = verify_bootstrap_seed(suite)
    boundary_checks = verify_regression_boundaries()
    indexes = [0]
    for family in suite.FAMILIES:
        indexes.append(
            next(
                index for index, case in enumerate(cases)
                if case["category"] == f"broader-{family}"
                and case["cohort"] == "calibration"
                and case["id"].endswith(".00")
            )
        )
    checks = 0
    for name in suite.MODULES:
        module = importlib.import_module(name)
        for index in indexes:
            correctness_gate(module, cases[index], expected[index])
            checks += 1

    first_family = suite.FAMILIES[0]
    positions = {case["id"]: index for index, case in enumerate(cases)}
    practice_id = f"cal.broader.{first_family}.00"
    next_practice_id = f"cal.broader.{first_family}.01"
    unseen_id = f"hold.broader.{first_family}.00"
    practice = cases[positions[practice_id]]
    unseen = cases[positions[unseen_id]]
    failures = (
        (
            positions[unseen_id],
            {**practice, "id": unseen_id, "cohort": "holdout"},
        ),
        (
            positions[next_practice_id],
            {**practice, "id": next_practice_id},
        ),
        (
            positions[practice_id],
            {**practice, "weight": 2},
        ),
        (
            positions[practice_id],
            {**practice, "api": "not-a-real-re-call"},
        ),
        (
            positions[unseen_id],
            {**unseen, "id": practice_id},
        ),
    )
    rejected = 0
    for index, damaged in failures:
        changed = list(cases)
        changed[index] = damaged
        try:
            validate_suite(suite, changed)
        except (KeyError, RuntimeError, TypeError, ValueError):
            rejected += 1
        else:
            raise RuntimeError("the broader fixture accepted a corrupted case")
    result = {
        **bootstrap,
        **seeded_draws,
        **boundary_checks,
        "schema": "rebar-performance-self-test-v7",
        "expected_sha256": manifest["expected_sha256"],
        "frozen_cases": len(cases),
        "frozen_holdout": suite.CASES_PER_COHORT,
        "frozen_trials": suite.TRIALS,
        "frozen_warmups": suite.WARMUPS,
        "frozen_bootstraps": suite.BOOTSTRAPS,
        "new_families": len(suite.FAMILIES),
        "sample_correctness_checks": checks,
        "rejected_fixture_corruptions": rejected,
    }
    print(json.dumps(result, sort_keys=True))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    freeze_parser = commands.add_parser("freeze")
    freeze_parser.set_defaults(function=freeze)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--module", action="append")
    verify_parser.add_argument("--output")
    verify_parser.set_defaults(function=verify)
    measure_parser = commands.add_parser("measure")
    measure_parser.add_argument("--output", required=True)
    measure_parser.set_defaults(function=measure)
    analyze_parser = commands.add_parser("analyze")
    analyze_parser.add_argument("--input", required=True)
    analyze_parser.add_argument("--output", required=True)
    analyze_parser.set_defaults(function=analyze)
    test_parser = commands.add_parser("self-test")
    test_parser.set_defaults(function=self_test)
    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
