#!/usr/bin/env python3
"""Run a bounded, calibration-first diagnostic on the frozen v6 workloads."""

from __future__ import annotations

import argparse
import gc
import gzip
import hashlib
import importlib
import json
import math
import random
import statistics
import time
import tracemalloc
from collections import Counter
from pathlib import Path

from tools.perf_v5 import digest, proc_memory, snapshot, source_kind
from tools.perf_v6 import correctness_gate, frozen, operation
from tools.rust_v6_loss_probe import interval, summarize_groups


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "candidates" / "evidence" / "rust-v6-calibration-plan.json"
INITIAL = ROOT / "performance" / "v6" / "evidence" / "initial-summary.json.gz"
BASELINE = "re"
RUST = "candidates.rust_candidate"
ZIG = "candidates.zig_candidate"
VARIANTS = (0, 7, 15, 31, 63)
MAX_SUBJECT = 8192
MAX_RESULTS = 192
LEGACY_FAMILIES = 12


def result_count(result):
    if result is None:
        return 0
    if isinstance(result, (list, tuple)):
        return len(result)
    return 1


def density(count):
    if count == 0:
        return "empty"
    if count == 1:
        return "one"
    if count < 8:
        return "few"
    return "many"


def subject_length(case):
    value = case.get("string")
    return 0 if value is None else len(value)


def bounded(case, expected):
    return (
        subject_length(case) <= MAX_SUBJECT
        and result_count(expected["result"]) <= MAX_RESULTS
    )


def historical_losses(cohort):
    with gzip.open(INITIAL, "rt", encoding="utf-8") as source:
        initial = json.load(source)
    rows = sorted(
        (
            row
            for row in initial["case_results"]
            if row["candidate"] == RUST
            and row["cohort"] == cohort
            and not row["category"].startswith("deeper-")
            and row["regression_gt_20pct"]
        ),
        key=lambda row: (row["speedup"], row["case"]),
    )
    return rows, initial["expected_sha256"]


def make_plan(selection="calibration"):
    if selection not in {"calibration", "holdout", "both"}:
        raise ValueError("cohort must be calibration, holdout, or both")

    suite, cases, expected, manifest = frozen()
    cohorts = (
        ("calibration", "holdout")
        if selection == "both"
        else (selection,)
    )
    per_family = 1 if selection == "both" else 2
    indexed = {
        case["id"]: (number, case, want)
        for number, (case, want) in enumerate(zip(cases, expected, strict=True))
    }
    selected = {}

    for family_index, family in enumerate(suite.FAMILIES):
        for cohort in cohorts:
            prefix = "cal" if cohort == "calibration" else "hold"
            offset = (suite.SEEDS[cohort] + family_index * 3) % len(VARIANTS)
            variants = (*VARIANTS[offset:], *VARIANTS[:offset])
            found = 0

            for variant in (*variants, *range(64)):
                case_id = f"{prefix}.deeper.{family}.{variant:02d}"
                entry = indexed.get(case_id)
                if (
                    entry is None
                    or case_id in selected
                    or not bounded(entry[1], entry[2])
                ):
                    continue
                selected[case_id] = (*entry, "all-48-frozen-families")
                found += 1
                if found == per_family:
                    break

            if found != per_family:
                raise RuntimeError(
                    f"missing bounded {cohort} variants for deeper-{family}"
                )

    loss_cohort = "calibration" if "calibration" in cohorts else "holdout"
    losses, initial_digest = historical_losses(loss_cohort)
    if initial_digest != manifest["expected_sha256"]:
        raise RuntimeError("historical performance results changed the v6 fixture")
    loss_families = set()
    for loss in losses:
        if len(loss_families) == LEGACY_FAMILIES:
            break
        if loss["category"] in loss_families:
            continue
        entry = indexed[loss["case"]]
        if not bounded(entry[1], entry[2]):
            continue
        selected[loss["case"]] = (*entry, "worst-same-cohort-legacy-loss")
        loss_families.add(loss["category"])

    def complete_dimension(title, required, identify, reason):
        present = {
            identify(case, want) for _, case, want, _ in selected.values()
        }
        for missing in sorted(required - present):
            chosen = next(
                (
                    entry
                    for entry in indexed.values()
                    if entry[1]["cohort"] in cohorts
                    and identify(entry[1], entry[2]) == missing
                    and bounded(entry[1], entry[2])
                ),
                None,
            )
            if chosen is None:
                raise RuntimeError(f"no bounded {selection} {title}: {missing}")
            selected[chosen[1]["id"]] = (*chosen, reason)

    complete_dimension(
        "API",
        {case["api"] for case in cases},
        lambda case, _want: case["api"],
        "missing-frozen-api",
    )
    complete_dimension(
        "lifecycle",
        {case["lifecycle"] for case in cases},
        lambda case, _want: case["lifecycle"],
        "missing-frozen-lifecycle",
    )
    complete_dimension(
        "input",
        {"text", "bytes", "bytearray", "memoryview"},
        lambda case, _want: source_kind(case),
        "missing-frozen-input",
    )
    complete_dimension(
        "result density",
        {"empty", "one", "few", "many"},
        lambda _case, want: density(result_count(want["result"])),
        "missing-result-density",
    )

    rows = sorted(selected.values(), key=lambda entry: entry[0])
    family_counts = Counter(
        (case["cohort"], case["category"])
        for _, case, _, _ in rows
        if case["category"].startswith("deeper-")
    )
    required_families = {
        (cohort, f"deeper-{family}")
        for cohort in cohorts
        for family in suite.FAMILIES
    }
    if (
        family_counts.keys() != required_families
        or any(count < per_family for count in family_counts.values())
    ):
        raise RuntimeError("the diagnostic lost a frozen family or variant")
    if any(case["cohort"] not in cohorts for _, case, _, _ in rows):
        raise RuntimeError("the diagnostic crossed its explicit cohort boundary")

    api_counts = Counter(case["api"] for _, case, _, _ in rows)
    lifecycle_counts = Counter(case["lifecycle"] for _, case, _, _ in rows)
    input_counts = Counter(source_kind(case) for _, case, _, _ in rows)
    density_counts = Counter(
        density(result_count(want["result"])) for _, _, want, _ in rows
    )
    if api_counts.keys() != {case["api"] for case in cases}:
        raise RuntimeError("the diagnostic lost a frozen public API")
    if lifecycle_counts.keys() != {case["lifecycle"] for case in cases}:
        raise RuntimeError("the diagnostic lost a frozen lifecycle")
    if not {"text", "bytes", "bytearray", "memoryview"} <= input_counts.keys():
        raise RuntimeError("the diagnostic lost a frozen input representation")
    if density_counts.keys() != {"empty", "one", "few", "many"}:
        raise RuntimeError("the diagnostic lost a result density")

    plan = {
        "schema": "rebar-rust-v6-calibration-diagnostic-plan-v1",
        "measurement": "diagnostic only; not a full frozen-holdout result",
        "cohort_selection": selection,
        "holdout_protection": (
            "Iterative optimization defaults to calibration only. "
            "Holdout and both-cohort access require an explicit --cohort."
        ),
        "expected_sha256": manifest["expected_sha256"],
        "frozen_cases": len(cases),
        "frozen_trials": suite.TRIALS,
        "frozen_warmups": suite.WARMUPS,
        "frozen_bootstraps": suite.BOOTSTRAPS,
        "order_seed": suite.ORDER_SEED,
        "bootstrap_seed": suite.BOOTSTRAP_SEED,
        "selection_seeds": dict(sorted(suite.SEEDS.items())),
        "preferred_variants": list(VARIANTS),
        "families": len(suite.FAMILIES),
        "family_cohort_pairs": len(family_counts),
        "variants_per_family_cohort": per_family,
        "legacy_loss_cohort": loss_cohort,
        "legacy_loss_families": len(loss_families),
        "cases": len(rows),
        "apis": dict(sorted(api_counts.items())),
        "lifecycles": dict(sorted(lifecycle_counts.items())),
        "inputs": dict(sorted(input_counts.items())),
        "result_densities": dict(sorted(density_counts.items())),
        "maximum_subject_length": max(subject_length(case) for _, case, _, _ in rows),
        "maximum_result_count": max(
            result_count(want["result"]) for _, _, want, _ in rows
        ),
        "tasks": [
            {
                "case": case["id"],
                "cohort": case["cohort"],
                "category": case["category"],
                "api": case["api"],
                "lifecycle": case["lifecycle"],
                "input": source_kind(case),
                "subject_length": subject_length(case),
                "result_count": result_count(want["result"]),
                "result_density": density(result_count(want["result"])),
                "frozen_operations": case["ops"],
                "expected_sha256": want["result_sha256"],
                "reason": reason,
            }
            for _, case, want, reason in rows
        ],
    }
    return suite, rows, manifest, plan


def binary_digests(module_names):
    output = {}
    for name in module_names:
        if name == BASELINE:
            continue
        module = importlib.import_module(name)
        if name == RUST:
            from candidates import _rust_bridge

            paths = (
                Path(module.__file__).with_name("_rust_engine.so"),
                Path(_rust_bridge.__file__),
            )
        elif name == ZIG:
            from candidates import _zig_bridge

            paths = (
                Path(module.__file__).with_name("_zig_probe.so"),
                Path(_zig_bridge.__file__),
            )
        else:
            raise RuntimeError(f"unexpected diagnostic engine: {name}")
        for path in paths:
            with path.open("rb") as source:
                output[str(path)] = hashlib.file_digest(source, "sha256").hexdigest()
    return dict(sorted(output.items()))


def group_results(results, paired, suite, samples):
    output = {}
    dimensions = (
        ("families", ("cohort", "category")),
        ("apis", ("cohort", "api")),
        ("lifecycles", ("cohort", "lifecycle")),
        ("inputs", ("cohort", "input")),
        ("densities", ("cohort", "result_density")),
        ("rankings", ("cohort",)),
    )
    for dimension, fields in dimensions:
        values = []
        for candidate in sorted({row["candidate"] for row in results}):
            relevant = [row for row in results if row["candidate"] == candidate]
            logs = {
                row["case"]: paired[(row["case"], candidate)]
                for row in relevant
            }
            summaries = summarize_groups(
                relevant,
                fields,
                logs,
                random.Random(suite.BOOTSTRAP_SEED),
                samples,
            )
            values.extend({"candidate": candidate, **row} for row in summaries)
        output[dimension] = values
    return output


def measure(args):
    if args.trials < 1 or args.max_ops < 1 or args.bootstraps < 1:
        raise ValueError("trials, operation limit, and bootstrap count must be positive")
    if args.limit is not None and args.limit < 1:
        raise ValueError("--limit must be positive")

    suite, entries, manifest, plan = make_plan(args.cohort)
    if args.limit is not None:
        entries = entries[: args.limit]
    names = (BASELINE, RUST, ZIG) if args.zig else (BASELINE, RUST)
    modules = {name: importlib.import_module(name) for name in names}
    before_binaries = binary_digests(names)
    raw = Path(args.raw)
    output = Path(args.output)
    raw.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    observed = {}
    raw_hash = hashlib.sha256()
    checks = 0

    with raw.open("w", encoding="utf-8", newline="\n") as stream:
        for number, (_, case, want, reason) in enumerate(entries):
            actions = {
                name: operation(module, case) for name, module in modules.items()
            }
            operations = min(case["ops"], args.max_ops)
            for trial in range(args.trials):
                order = list(names)
                random.Random(
                    suite.ORDER_SEED + trial * 1009 + sum(map(ord, case["id"]))
                ).shuffle(order)

                for order_number, name in enumerate(order):
                    action = actions[name]
                    expected_digest = correctness_gate(modules[name], case, want)
                    checks += 1
                    for _ in range(suite.WARMUPS):
                        action()

                    tracemalloc.start()
                    try:
                        memory_result = action()
                        _, peak = tracemalloc.get_traced_memory()
                    finally:
                        tracemalloc.stop()
                    memory = snapshot(memory_result)
                    if (
                        digest(memory) != expected_digest
                        or memory != want["result"]
                    ):
                        raise RuntimeError(
                            f"diagnostic memory mismatch: {name} {case['id']}"
                        )
                    checks += 1

                    previous_memory = proc_memory()
                    gc_enabled = gc.isenabled()
                    if gc_enabled:
                        gc.disable()
                    try:
                        started = time.perf_counter_ns()
                        result = None
                        for _ in range(operations):
                            result = action()
                        elapsed = time.perf_counter_ns() - started
                    finally:
                        if gc_enabled:
                            gc.enable()
                    current_memory = proc_memory()
                    value = snapshot(result)
                    if digest(value) != expected_digest or value != want["result"]:
                        raise RuntimeError(
                            f"diagnostic post-timing mismatch: {name} {case['id']}"
                        )
                    checks += 1
                    if elapsed <= 0:
                        raise RuntimeError(
                            f"non-positive diagnostic timing: {name} {case['id']}"
                        )

                    row = {
                        "schema": "rebar-rust-v6-calibration-pilot-row-v1",
                        "measurement": "diagnostic only; not a holdout result",
                        "case": case["id"],
                        "cohort": case["cohort"],
                        "category": case["category"],
                        "api": case["api"],
                        "lifecycle": case["lifecycle"],
                        "input": source_kind(case),
                        "result_density": density(result_count(want["result"])),
                        "reason": reason,
                        "module": name,
                        "trial": trial,
                        "order": order_number,
                        "operations": operations,
                        "frozen_operations": case["ops"],
                        "elapsed_ns": elapsed,
                        "ns_per_op": elapsed / operations,
                        "peak_traced_bytes": peak,
                        "rss_before_kb": previous_memory["rss_kb"],
                        "rss_after_kb": current_memory["rss_kb"],
                        "hwm_kb": current_memory["hwm_kb"],
                        "expected_sha256": expected_digest,
                    }
                    encoded = (
                        json.dumps(row, sort_keys=True, separators=(",", ":"))
                        + "\n"
                    )
                    stream.write(encoded)
                    raw_hash.update(encoded.encode("utf-8"))
                    key = (case["id"], trial, name)
                    if key in observed:
                        raise RuntimeError(f"duplicate diagnostic timing: {key}")
                    observed[key] = row

            if number and number % 24 == 0:
                print(f"checked {number}/{len(entries)} diagnostic tasks", flush=True)

    after_binaries = binary_digests(names)
    if before_binaries != after_binaries:
        raise RuntimeError("a native candidate binary changed during the pilot")
    required = len(entries) * args.trials * len(names)
    if len(observed) != required or checks != required * 3:
        raise RuntimeError("diagnostic row or correctness-check count drift")

    rng = random.Random(suite.BOOTSTRAP_SEED)
    results = []
    paired = {}
    for _, case, want, _reason in entries:
        baseline = [
            observed[(case["id"], trial, BASELINE)]
            for trial in range(args.trials)
        ]
        for name in names[1:]:
            candidate = [
                observed[(case["id"], trial, name)]
                for trial in range(args.trials)
            ]
            logs = [
                math.log(left["ns_per_op"] / right["ns_per_op"])
                for left, right in zip(baseline, candidate, strict=True)
            ]
            paired[(case["id"], name)] = logs
            low, high = interval(logs, rng, args.bootstraps)
            speed = math.exp(statistics.fmean(logs))
            candidate_ns = statistics.median(
                row["ns_per_op"] for row in candidate
            )
            results.append(
                {
                    "case": case["id"],
                    "cohort": case["cohort"],
                    "category": case["category"],
                    "api": case["api"],
                    "lifecycle": case["lifecycle"],
                    "input": source_kind(case),
                    "result_density": density(result_count(want["result"])),
                    "candidate": name,
                    "weight": case["weight"],
                    "speedup": speed,
                    "ci95_low": low,
                    "ci95_high": high,
                    "baseline_ns": statistics.median(
                        row["ns_per_op"] for row in baseline
                    ),
                    "candidate_ns": candidate_ns,
                    "rust_ns": candidate_ns,
                    "peak_traced_ratio": statistics.median(
                        row["peak_traced_bytes"] for row in candidate
                    )
                    / max(
                        1,
                        statistics.median(
                            row["peak_traced_bytes"] for row in baseline
                        ),
                    ),
                    "statistically_faster": low > 1,
                    "regression_gt_20pct": speed < 0.8,
                }
            )

    groups = group_results(results, paired, suite, args.bootstraps)
    report = {
        "schema": "rebar-rust-v6-calibration-diagnostic-pilot-v1",
        "measurement": (
            "diagnostic subset only; not a full frozen-holdout ranking "
            "or a final speed claim"
        ),
        "cohort_selection": plan["cohort_selection"],
        "expected_sha256": manifest["expected_sha256"],
        "raw_sha256": raw_hash.hexdigest(),
        "binary_sha256_before": before_binaries,
        "binary_sha256_after": after_binaries,
        "modules": list(names),
        "cases": len(entries),
        "planned_cases": plan["cases"],
        "frozen_cases": plan["frozen_cases"],
        "trials": args.trials,
        "frozen_trials": suite.TRIALS,
        "warmups": suite.WARMUPS,
        "max_operations": args.max_ops,
        "bootstrap_samples": args.bootstraps,
        "frozen_bootstrap_samples": suite.BOOTSTRAPS,
        "order_seed": suite.ORDER_SEED,
        "bootstrap_seed": suite.BOOTSTRAP_SEED,
        "rows": len(observed),
        "correctness_checks": checks,
        "coverage": {
            name: plan[name]
            for name in (
                "families",
                "family_cohort_pairs",
                "variants_per_family_cohort",
                "legacy_loss_cohort",
                "legacy_loss_families",
                "apis",
                "lifecycles",
                "inputs",
                "result_densities",
                "maximum_subject_length",
                "maximum_result_count",
            )
        },
        **groups,
        "case_results": results,
        "regressions": [row for row in results if row["regression_gt_20pct"]],
    }
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "schema": report["schema"],
                "cohort_selection": report["cohort_selection"],
                "cases": report["cases"],
                "planned_cases": report["planned_cases"],
                "rows": report["rows"],
                "correctness_checks": checks,
                "modules": report["modules"],
                "trials": args.trials,
                "families": plan["families"],
                "apis": len(plan["apis"]),
                "stable_native_binaries": before_binaries == after_binaries,
                "raw_sha256": report["raw_sha256"],
                "output": str(output),
            },
            sort_keys=True,
        ),
        flush=True,
    )


def save_plan(args, *, self_test):
    suite, entries, manifest, plan = make_plan(args.cohort)
    if self_test:
        other_suite, other_entries, other_manifest, second = make_plan(args.cohort)
        if (
            plan != second
            or suite.TRIALS != other_suite.TRIALS
            or manifest != other_manifest
            or [entry[1]["id"] for entry in entries]
            != [entry[1]["id"] for entry in other_entries]
        ):
            raise RuntimeError("diagnostic task selection is not deterministic")

    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "passed": True,
                "schema": plan["schema"],
                "cohort_selection": plan["cohort_selection"],
                "expected_sha256": plan["expected_sha256"],
                "cases": plan["cases"],
                "families": plan["families"],
                "family_cohort_pairs": plan["family_cohort_pairs"],
                "variants_per_family_cohort": plan[
                    "variants_per_family_cohort"
                ],
                "apis": len(plan["apis"]),
                "lifecycles": len(plan["lifecycles"]),
                "inputs": plan["inputs"],
                "densities": plan["result_densities"],
                "legacy_loss_cohort": plan["legacy_loss_cohort"],
                "legacy_loss_families": plan["legacy_loss_families"],
                "maximum_subject_length": plan["maximum_subject_length"],
                "maximum_result_count": plan["maximum_result_count"],
                "deterministic": self_test,
                "output": str(destination),
            },
            sort_keys=True,
        )
    )


def add_cohort(parser):
    parser.add_argument(
        "--cohort",
        choices=("calibration", "holdout", "both"),
        default="calibration",
        help="calibration is the default; holdout requires an explicit choice",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    for name in ("plan", "self-test"):
        command = commands.add_parser(name)
        command.add_argument("--output", default=str(DEFAULT_PLAN))
        add_cohort(command)
        command.set_defaults(
            function=lambda args, test=name == "self-test": save_plan(
                args, self_test=test
            )
        )

    command = commands.add_parser("measure")
    command.add_argument("--raw", required=True)
    command.add_argument("--output", required=True)
    command.add_argument("--trials", type=int, default=5)
    command.add_argument("--max-ops", type=int, default=16)
    command.add_argument("--bootstraps", type=int, default=300)
    command.add_argument("--limit", type=int)
    command.add_argument("--zig", action="store_true")
    add_cohort(command)
    command.set_defaults(function=measure)

    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
