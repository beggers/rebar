#!/usr/bin/env python3
"""Run correctness-gated, reproducible Rust pilots on frozen v6 tasks."""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib
import json
import math
import random
import statistics
import time
import tracemalloc
from collections import Counter, defaultdict
from pathlib import Path

from tools.perf_v5 import digest, proc_memory, snapshot, source_kind
from tools.perf_v6 import correctness_gate, frozen, operation


BASELINE = "re"
CANDIDATE = "candidates.rust_candidate"
MODULES = (BASELINE, CANDIDATE)
DEFAULT_CATEGORIES = (
    "deeper-cold-compile",
    "deeper-dense-class-finditer",
    "deeper-dense-literal-findall",
    "deeper-file-names",
    "deeper-fullmatch-structured",
    "deeper-lookahead-chain",
    "deeper-lookbehind-chain",
    "deeper-match-short",
    "deeper-money-units",
    "deeper-module-warm-search",
    "deeper-module-warm-sub",
    "deeper-scanner-window",
    "deeper-search-long-hit",
    "deeper-search-long-miss",
    "deeper-shared-prefix-alternatives",
    "deeper-unicode-word-lines",
)


def interval(values: list[float], rng: random.Random, samples: int) -> tuple[float, float]:
    """Return the seeded, paired bootstrap interval for log-speed ratios."""
    draws = sorted(
        statistics.fmean(values[rng.randrange(len(values))] for _ in values)
        for _ in range(samples)
    )
    return (
        math.exp(draws[math.floor(0.025 * (samples - 1))]),
        math.exp(draws[math.floor(0.975 * (samples - 1))]),
    )


def summarize_groups(
    results: list[dict],
    dimensions: tuple[str, ...],
    paired_logs: dict[str, list[float]],
    rng: random.Random,
    samples: int,
) -> list[dict]:
    """Keep every pilot case visible in each independent reporting dimension."""
    grouped: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for result in results:
        grouped[tuple(result[dimension] for dimension in dimensions)].append(result)

    summaries = []
    for key, members in sorted(grouped.items()):
        logs = [math.log(member["speedup"]) for member in members]
        denominator = sum(member["weight"] for member in members)
        draws = sorted(
            sum(
                statistics.fmean(
                    paired_logs[member["case"]][
                        rng.randrange(len(paired_logs[member["case"]]))
                    ]
                    for _ in paired_logs[member["case"]]
                )
                * member["weight"]
                for member in members
            )
            / denominator
            for _ in range(samples)
        )
        low = math.exp(draws[math.floor(0.025 * (samples - 1))])
        high = math.exp(draws[math.floor(0.975 * (samples - 1))])
        summary = dict(zip(dimensions, key, strict=True))
        summary.update(
            {
                "cases": len(members),
                "speedup": math.exp(statistics.fmean(logs)),
                "ci95_low": low,
                "ci95_high": high,
                "faster": sum(member["statistically_faster"] for member in members),
                "slow": sum(member["regression_gt_20pct"] for member in members),
                "median_baseline_ns": statistics.median(
                    member["baseline_ns"] for member in members
                ),
                "median_rust_ns": statistics.median(
                    member["rust_ns"] for member in members
                ),
                "median_peak_traced_ratio": statistics.median(
                    member["peak_traced_ratio"] for member in members
                ),
            }
        )
        summaries.append(summary)
    return summaries


def self_test() -> dict:
    """Check pilot bootstrap determinism without running a noisy benchmark."""
    values = [math.log(value) for value in (0.5, 0.75, 1.0, 1.25, 1.5)]
    seed = 1985072202
    samples = 41
    actual = interval(values, random.Random(seed), samples)
    reference_rng = random.Random(seed)
    reference_draws = sorted(
        statistics.fmean(
            values[reference_rng.randrange(len(values))] for _ in values
        )
        for _ in range(samples)
    )
    expected = (
        math.exp(reference_draws[math.floor(0.025 * (samples - 1))]),
        math.exp(reference_draws[math.floor(0.975 * (samples - 1))]),
    )
    if actual != expected:
        raise RuntimeError(f"Rust pilot bootstrap drift: {actual!r} != {expected!r}")

    sample = {
        "case": "bootstrap-self-test",
        "cohort": "holdout",
        "speedup": math.exp(statistics.fmean(values)),
        "weight": 1,
        "statistically_faster": False,
        "regression_gt_20pct": False,
        "baseline_ns": 1.0,
        "rust_ns": 1.0,
        "peak_traced_ratio": 1.0,
    }
    grouped = summarize_groups(
        [sample],
        ("cohort",),
        {sample["case"]: values},
        random.Random(seed),
        samples,
    )[0]
    if (grouped["ci95_low"], grouped["ci95_high"]) != expected:
        raise RuntimeError("Rust pilot grouped intervals lost paired trial uncertainty")

    suite, cases, expected_cases, manifest = frozen()
    present = {case["category"] for case in cases}
    missing = set(DEFAULT_CATEGORIES) - present
    if missing:
        raise RuntimeError(f"Rust pilot default categories are not frozen: {sorted(missing)}")
    if len(cases) != len(expected_cases) or len(cases) != manifest["cases"]:
        raise RuntimeError("Rust pilot frozen case or expectation count drift")
    if suite.TRIALS != manifest["trials"] or suite.WARMUPS != manifest["warmups"]:
        raise RuntimeError("Rust pilot frozen trial or warmup metadata drift")

    return {
        "schema": "rebar-rust-v6-loss-probe-self-test-v1",
        "passed": True,
        "bootstrap_samples": samples,
        "default_categories": len(DEFAULT_CATEGORIES),
        "frozen_cases": len(cases),
        "frozen_trials": suite.TRIALS,
        "frozen_warmups": suite.WARMUPS,
        "expected_sha256": manifest["expected_sha256"],
    }


def select_cases(cases: list[dict], expected: list[dict], args: argparse.Namespace):
    if args.all and args.category:
        raise ValueError("--all cannot be combined with --category")
    wanted = (
        {case["category"] for case in cases}
        if args.all
        else set(args.category or DEFAULT_CATEGORIES)
    )
    counts: Counter[tuple[str, str]] = Counter()
    selected = []
    for case, want in zip(cases, expected, strict=True):
        if case["category"] not in wanted:
            continue
        if args.cohort != "all" and case["cohort"] != args.cohort:
            continue
        family_key = (case["cohort"], case["category"])
        if (
            args.variants_per_family is not None
            and counts[family_key] >= args.variants_per_family
        ):
            continue
        selected.append((case, want))
        counts[family_key] += 1

    found = {case["category"] for case, _ in selected}
    if found != wanted:
        raise RuntimeError(f"unknown or unavailable workload categories: {sorted(wanted - found)}")
    if not selected:
        raise RuntimeError("Rust pilot selected no frozen tasks")
    return selected, wanted


def measure(args: argparse.Namespace) -> dict:
    if args.trials < 1 or args.max_ops < 1 or args.bootstraps < 1:
        raise ValueError("trial, operation, and bootstrap counts must be positive")
    if args.variants_per_family is not None and args.variants_per_family < 1:
        raise ValueError("--variants-per-family must be positive")

    suite, cases, expected, manifest = frozen()
    selected, wanted = select_cases(cases, expected, args)
    modules = {name: importlib.import_module(name) for name in MODULES}
    raw = Path(args.raw)
    raw.parent.mkdir(parents=True, exist_ok=True)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    raw_hash = hashlib.sha256()
    measurements: dict[tuple[str, int, str], dict] = {}
    checks = 0
    rows = 0

    with raw.open("w", encoding="utf-8", newline="\n") as stream:
        for case_index, (case, want) in enumerate(selected):
            actions = {
                name: operation(module, case) for name, module in modules.items()
            }
            operations = min(case["ops"], args.max_ops)
            for trial in range(args.trials):
                order = list(MODULES)
                random.Random(
                    suite.ORDER_SEED
                    + trial * 1009
                    + sum(map(ord, case["id"]))
                ).shuffle(order)
                for order_index, name in enumerate(order):
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
                    memory_snapshot = snapshot(memory_result)
                    if (
                        digest(memory_snapshot) != expected_digest
                        or memory_snapshot != want["result"]
                    ):
                        raise RuntimeError(
                            f"memory correctness mismatch: {name} {case['id']}"
                        )
                    checks += 1

                    before = proc_memory()
                    enabled = gc.isenabled()
                    if enabled:
                        gc.disable()
                    try:
                        started = time.perf_counter_ns()
                        result = None
                        for _ in range(operations):
                            result = action()
                        elapsed = time.perf_counter_ns() - started
                    finally:
                        if enabled:
                            gc.enable()
                    after = proc_memory()
                    timed = snapshot(result)
                    if digest(timed) != expected_digest or timed != want["result"]:
                        raise RuntimeError(
                            f"post-timing correctness mismatch: {name} {case['id']}"
                        )
                    checks += 1
                    if elapsed <= 0:
                        raise RuntimeError(
                            f"non-positive timing: {name} {case['id']} trial {trial}"
                        )

                    row = {
                        "schema": "rebar-rust-v6-pilot-row-v1",
                        "case": case["id"],
                        "cohort": case["cohort"],
                        "category": case["category"],
                        "api": case["api"],
                        "lifecycle": case["lifecycle"],
                        "input": source_kind(case),
                        "module": name,
                        "trial": trial,
                        "order": order_index,
                        "operations": operations,
                        "frozen_operations": case["ops"],
                        "elapsed_ns": elapsed,
                        "ns_per_op": elapsed / operations,
                        "peak_traced_bytes": peak,
                        "rss_before_kb": before["rss_kb"],
                        "rss_after_kb": after["rss_kb"],
                        "hwm_kb": after["hwm_kb"],
                        "expected_sha256": expected_digest,
                    }
                    encoded = json.dumps(
                        row, sort_keys=True, separators=(",", ":")
                    ) + "\n"
                    stream.write(encoded)
                    raw_hash.update(encoded.encode("utf-8"))
                    key = (case["id"], trial, name)
                    if key in measurements:
                        raise RuntimeError(f"duplicate Rust pilot timing: {key!r}")
                    measurements[key] = row
                    rows += 1
            if case_index and case_index % 128 == 0:
                print(f"measured {case_index}/{len(selected)} frozen Rust pilot tasks", flush=True)

    required = len(selected) * args.trials * len(MODULES)
    if rows != required or len(measurements) != required:
        raise RuntimeError(f"Rust pilot raw-row count drift: {rows} != {required}")
    if checks != required * 3:
        raise RuntimeError(f"Rust pilot correctness-check count drift: {checks}")

    rng = random.Random(suite.BOOTSTRAP_SEED)
    results = []
    paired_logs = {}
    for case, _ in selected:
        baseline = [
            measurements[(case["id"], trial, BASELINE)]
            for trial in range(args.trials)
        ]
        rust = [
            measurements[(case["id"], trial, CANDIDATE)]
            for trial in range(args.trials)
        ]
        logs = [
            math.log(left["ns_per_op"] / right["ns_per_op"])
            for left, right in zip(baseline, rust, strict=True)
        ]
        paired_logs[case["id"]] = logs
        low, high = interval(logs, rng, args.bootstraps)
        speedup = math.exp(statistics.fmean(logs))
        results.append(
            {
                "case": case["id"],
                "cohort": case["cohort"],
                "category": case["category"],
                "api": case["api"],
                "lifecycle": case["lifecycle"],
                "input": source_kind(case),
                "candidate": CANDIDATE,
                "weight": case["weight"],
                "speedup": speedup,
                "ci95_low": low,
                "ci95_high": high,
                "baseline_ns": statistics.median(
                    row["ns_per_op"] for row in baseline
                ),
                "rust_ns": statistics.median(row["ns_per_op"] for row in rust),
                "peak_traced_ratio": statistics.median(
                    row["peak_traced_bytes"] for row in rust
                )
                / max(
                    1,
                    statistics.median(
                        row["peak_traced_bytes"] for row in baseline
                    ),
                ),
                "statistically_faster": low > 1,
                "regression_gt_20pct": speedup < 0.8,
            }
        )

    summary = {
        "schema": "rebar-rust-v6-loss-probe-v1",
        "measurement": "diagnostic pilot; not a full frozen-holdout result",
        "expected_sha256": manifest["expected_sha256"],
        "raw_sha256": raw_hash.hexdigest(),
        "modules": list(MODULES),
        "categories": sorted(wanted),
        "cohort_selection": args.cohort,
        "variants_per_family": args.variants_per_family,
        "cases": len(selected),
        "frozen_cases": len(cases),
        "trials": args.trials,
        "frozen_trials": suite.TRIALS,
        "warmups": suite.WARMUPS,
        "max_operations": args.max_ops,
        "bootstraps": args.bootstraps,
        "frozen_bootstraps": suite.BOOTSTRAPS,
        "interval_method": "stratified resampling of paired per-case trial log-ratios",
        "order_seed": suite.ORDER_SEED,
        "bootstrap_seed": suite.BOOTSTRAP_SEED,
        "rows": rows,
        "correctness_checks": checks,
        "families": summarize_groups(
            results, ("cohort", "category"), paired_logs, rng, args.bootstraps
        ),
        "apis": summarize_groups(
            results, ("cohort", "api"), paired_logs, rng, args.bootstraps
        ),
        "lifecycles": summarize_groups(
            results, ("cohort", "lifecycle"), paired_logs, rng, args.bootstraps
        ),
        "inputs": summarize_groups(
            results, ("cohort", "input"), paired_logs, rng, args.bootstraps
        ),
        "rankings": summarize_groups(
            results, ("cohort",), paired_logs, rng, args.bootstraps
        ),
        "case_results": results,
        "regressions": [
            result for result in results if result["regression_gt_20pct"]
        ],
    }
    output.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for row in summary["families"]:
        if row["cohort"] == "holdout":
            print(
                f"{row['category']:<40} "
                f"{row['speedup']:.3f}× "
                f"{row['ci95_low']:.3f}–{row['ci95_high']:.3f} "
                f"faster={row['faster']}/{row['cases']} "
                f"slow={row['slow']}"
            )
    print(
        json.dumps(
            {
                key: value
                for key, value in summary.items()
                if key
                not in {
                    "families",
                    "apis",
                    "lifecycles",
                    "inputs",
                    "rankings",
                    "case_results",
                    "regressions",
                }
            },
            sort_keys=True,
        )
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="path for complete pilot JSON")
    parser.add_argument("--raw", help="path for correctness-gated JSONL")
    parser.add_argument("--trials", type=int, default=7)
    parser.add_argument("--max-ops", type=int, default=32)
    parser.add_argument("--bootstraps", type=int, default=1000)
    parser.add_argument("--category", action="append")
    parser.add_argument("--all", action="store_true")
    parser.add_argument(
        "--cohort", choices=("calibration", "holdout", "all"), default="all"
    )
    parser.add_argument("--variants-per-family", type=int)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        if args.output or args.raw:
            parser.error("--self-test cannot be combined with --output or --raw")
        print(json.dumps(self_test(), sort_keys=True))
        return
    if not args.output or not args.raw:
        parser.error("--output and --raw are required unless --self-test is used")
    measure(args)


if __name__ == "__main__":
    main()
