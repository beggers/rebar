#!/usr/bin/env python3
"""Profile frozen Rust workloads without changing the production candidate.

Build the optional native counter outside the repository:

    cc -std=c11 -O3 -fPIC -shared -Wall -Wextra -Werror \
       tools/rust_native_allocator_v6.c \
       -o /tmp/rebar-rust-native-allocator-v6.so

Then run the pinned Python with LD_PRELOAD. Timing and allocation samples are
always checked against the frozen CPython oracle, and both native binaries are
fingerprinted before and after measurement.
"""

from __future__ import annotations

import argparse
import collections
import cProfile
import ctypes
import gc
import gzip
import hashlib
import importlib
import io
import json
import math
import pstats
import random
import statistics
import sysconfig
import time
import tracemalloc
from pathlib import Path

from tools.perf_v5 import snapshot, source_kind
from tools.perf_v6 import correctness_gate, frozen, operation


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "candidates" / "_rust_engine.so"
BRIDGE = ROOT / "candidates" / (
    "_rust_bridge" + str(sysconfig.get_config_var("EXT_SUFFIX"))
)
FROZEN_SUMMARY = ROOT / "performance" / "v6" / "evidence" / "initial-summary.json.gz"
FIELDS = (
    "malloc_calls",
    "calloc_calls",
    "realloc_calls",
    "free_calls",
    "malloc_bytes",
    "calloc_bytes",
    "realloc_bytes",
    "failed_calls",
)
DEFAULT_CATEGORIES = (
    "deeper-quote-captures",
    "deeper-config-lines",
    "deeper-unicode-casefold",
    "expanded-html-tags",
    "deeper-combining-wide",
    "expanded-unicode-words",
    "deeper-markdown-code",
    "deeper-source-comments",
    "deeper-csv-split-even",
    "deeper-http-headers",
    "deeper-path-mixed-bytes",
    "deeper-file-names",
    "deeper-money-units",
    "deeper-shared-prefix-alternatives",
    "deeper-unicode-word-lines",
    "deeper-dense-literal-findall",
    "deeper-dense-class-finditer",
    "deeper-search-long-hit",
    "deeper-search-long-miss",
    "deeper-cold-compile",
    "expanded-cold-compile",
    "large-cold-compile",
    "large-literal-hit",
    "large-literal-miss",
    "expanded-backreference",
    "deeper-lookbehind-chain",
    "deeper-conditionals-nested",
    "deeper-bounded-repeats",
)


def file_stamp(path: Path) -> dict:
    info = path.stat()
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {
        "path": str(path),
        "sha256": digest,
        "size": info.st_size,
        "mtime_ns": info.st_mtime_ns,
        "inode": info.st_ino,
    }


class NativeAllocationCounter:
    """Access only the explicitly preloaded, dependency-free glibc counter."""

    def __init__(self):
        library = ctypes.CDLL(None)
        try:
            self.begin = library.rebar_rust_osprofile_begin
            self.end = library.rebar_rust_osprofile_end
            self.snapshot = library.rebar_rust_osprofile_snapshot
        except AttributeError as error:
            raise RuntimeError(
                "compile tools/rust_native_allocator_v6.c into /tmp and run "
                "with LD_PRELOAD=/tmp/rebar-rust-native-allocator-v6.so"
            ) from error
        self.begin.argtypes = []
        self.begin.restype = None
        self.end.argtypes = []
        self.end.restype = None
        self.snapshot.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.c_size_t]
        self.snapshot.restype = None
        self.buffer = (ctypes.c_uint64 * len(FIELDS))()

    def sample(self, action):
        gc_enabled = gc.isenabled()
        if gc_enabled:
            gc.disable()
        try:
            self.begin()
            try:
                result = action()
            finally:
                self.end()
            self.snapshot(self.buffer, len(FIELDS))
            return result, {
                name: int(self.buffer[index]) for index, name in enumerate(FIELDS)
            }
        finally:
            if gc_enabled:
                gc.enable()


def geometric_mean(values):
    values = list(values)
    if not values:
        return None
    if any(value <= 0 for value in values):
        raise RuntimeError("geometric mean requires positive performance measurements")
    return math.exp(statistics.fmean(math.log(value) for value in values))


def result_count(value):
    if isinstance(value, (list, tuple)):
        return len(value)
    return int(value is not None)


def artifact_stamps():
    return {"engine": file_stamp(NATIVE), "bridge": file_stamp(BRIDGE)}


def allocation_samples(counter, action, expected, repetitions):
    rows = []
    for _ in range(repetitions):
        result, counts = counter.sample(action)
        if snapshot(result) != expected:
            raise RuntimeError("post-allocation result does not match the frozen oracle")
        if counts["failed_calls"]:
            raise RuntimeError("observed a failed allocation during a profiled workload")
        rows.append(counts)
    return {
        **{name: statistics.median(row[name] for row in rows) for name in FIELDS},
        "samples": rows,
    }


def timed_batch(action, count):
    gc_enabled = gc.isenabled()
    if gc_enabled:
        gc.disable()
    try:
        cpu_begin = time.thread_time_ns()
        wall_begin = time.perf_counter_ns()
        result = None
        for _ in range(count):
            result = action()
        elapsed = time.perf_counter_ns() - wall_begin
        cpu = time.thread_time_ns() - cpu_begin
        return result, elapsed / count, cpu / count
    finally:
        if gc_enabled:
            gc.enable()


def peak_python_memory(action, expected):
    tracemalloc.start()
    try:
        result = action()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    if snapshot(result) != expected:
        raise RuntimeError("post-memory result does not match the frozen oracle")
    return peak


def historical(args):
    suite, cases, _, manifest = frozen()
    case_map = {case["id"]: case for case in cases}
    with gzip.open(FROZEN_SUMMARY, "rt", encoding="utf-8") as stream:
        summary = json.load(stream)
    rust_name = "candidates.rust_candidate"
    rows = [
        row
        for row in summary["case_results"]
        if row["candidate"] == rust_name
        and (args.cohort == "all" or row["cohort"] == args.cohort)
    ]
    required = suite.CASES_PER_COHORT * (2 if args.cohort == "all" else 1)
    if len(rows) != required:
        raise RuntimeError(f"frozen historical row count changed: {len(rows)} != {required}")
    grouped = {
        name: collections.defaultdict(list)
        for name in ("category", "api", "lifecycle", "input")
    }
    for row in rows:
        case = case_map[row["case"]]
        grouped["category"][case["category"]].append(row)
        grouped["api"][case["api"]].append(row)
        grouped["lifecycle"][case["lifecycle"]].append(row)
        grouped["input"][source_kind(case)].append(row)
    analyses = {}
    for name, groups in grouped.items():
        analyses[name] = sorted(
            (
                {
                    "group": key,
                    "cases": len(members),
                    "geomean_speedup": geometric_mean(row["speedup"] for row in members),
                    "statistically_faster": sum(
                        bool(row["statistically_faster"]) for row in members
                    ),
                    "regressions_gt_20pct": sum(
                        bool(row["regression_gt_20pct"]) for row in members
                    ),
                    "median_peak_traced_ratio": statistics.median(
                        row["peak_traced_ratio"] for row in members
                    ),
                }
                for key, members in groups.items()
            ),
            key=lambda row: row["geomean_speedup"],
        )
    ranking = next(
        row
        for row in summary["rankings"]
        if row["candidate"] == rust_name and row["cohort"] == args.cohort
    )
    result = {
        "schema": "rebar-rust-readonly-historical-profile-v6",
        "cohort": args.cohort,
        "frozen_expected_sha256": manifest["expected_sha256"],
        "initial_summary": file_stamp(FROZEN_SUMMARY),
        "ranking": ranking,
        "groups": analyses,
    }
    write_result(result, args.output)
    print("API               cases speedup faster large_losses median_python_memory", flush=True)
    for row in analyses["api"]:
        print(
            f"{row['group']:<17} {row['cases']:>5} {row['geomean_speedup']:>8.4f} "
            f"{row['statistically_faster']:>6} {row['regressions_gt_20pct']:>12} "
            f"{row['median_peak_traced_ratio']:>20.3f}",
            flush=True,
        )
    print("worst family                           cases speedup faster large_losses", flush=True)
    for row in analyses["category"][:24]:
        print(
            f"{row['group']:<37} {row['cases']:>4} {row['geomean_speedup']:>8.5f} "
            f"{row['statistically_faster']:>5} {row['regressions_gt_20pct']:>5}",
            flush=True,
        )
    print(json.dumps({"output": args.output, "ranking": ranking}, sort_keys=True), flush=True)


def selected_cases(cases, expected, categories, variants, cohort):
    if len(categories) != len(set(categories)):
        raise RuntimeError("duplicate workload families would change the comparison denominator")
    if any(index < 0 for index in variants):
        raise RuntimeError("workload variant indexes must not be negative")
    wanted = set(categories)
    grouped = collections.defaultdict(list)
    for case, want in zip(cases, expected, strict=True):
        if case["cohort"] == cohort and case["category"] in wanted:
            grouped[case["category"]].append((case, want))
    missing = wanted - grouped.keys()
    if missing:
        raise RuntimeError(f"unknown frozen v6 workload categories: {sorted(missing)}")
    chosen = []
    for name in categories:
        members = sorted(grouped[name], key=lambda pair: pair[0]["id"])
        indexes = sorted({min(index, len(members) - 1) for index in variants})
        chosen.extend(members[index] for index in indexes)
    return chosen


def summarize_families(rows):
    grouped = collections.defaultdict(list)
    for row in rows:
        grouped[row["category"]].append(row)
    families = []
    for category, members in grouped.items():
        families.append(
            {
                "category": category,
                "cases": len(members),
                "wall_geomean_speedup": geometric_mean(
                    row["wall_speedup"] for row in members
                ),
                "thread_cpu_geomean_speedup": geometric_mean(
                    row["thread_cpu_speedup"] for row in members
                ),
                "median_rust_native_allocation_calls": statistics.median(
                    sum(
                        row["native_heap"]["rust"][field]
                        for field in ("malloc_calls", "calloc_calls", "realloc_calls")
                    )
                    for row in members
                ),
                "median_rust_native_allocation_bytes": statistics.median(
                    sum(
                        row["native_heap"]["rust"][field]
                        for field in ("malloc_bytes", "calloc_bytes", "realloc_bytes")
                    )
                    for row in members
                ),
                "median_stdlib_native_allocation_calls": statistics.median(
                    sum(
                        row["native_heap"]["stdlib"][field]
                        for field in ("malloc_calls", "calloc_calls", "realloc_calls")
                    )
                    for row in members
                ),
                "median_rust_traced_peak_bytes": statistics.median(
                    row["traced_peak_bytes"]["rust"] for row in members
                ),
                "median_stdlib_traced_peak_bytes": statistics.median(
                    row["traced_peak_bytes"]["stdlib"] for row in members
                ),
            }
        )
    return sorted(families, key=lambda row: row["wall_geomean_speedup"])


def family_timing(args):
    counter = NativeAllocationCounter()
    before = artifact_stamps()
    suite, cases, expected, manifest = frozen()
    modules = {
        "stdlib": importlib.import_module("re"),
        "rust": importlib.import_module("candidates.rust_candidate"),
    }
    categories = args.category or list(DEFAULT_CATEGORIES)
    pairs = selected_cases(cases, expected, categories, args.variant, args.cohort)
    rows = []
    started = time.monotonic()

    for index, (case, want) in enumerate(pairs):
        if index and time.monotonic() - started > args.max_seconds:
            break
        actions = {}
        for name, module in modules.items():
            correctness_gate(module, case, want)
            action = operation(module, case)
            for _ in range(min(suite.WARMUPS, 2)):
                result = action()
            if snapshot(result) != want["result"]:
                raise RuntimeError(f"warmup correctness mismatch: {name} {case['id']}")
            actions[name] = action

        length = len(case.get("string") or "")
        batch = max(1, min(case["ops"], args.max_ops))
        if length >= 32_768:
            batch = min(batch, 4)
        timings = {name: [] for name in modules}
        cpu_timings = {name: [] for name in modules}
        for trial in range(args.trials):
            order = list(modules)
            random.Random(
                suite.ORDER_SEED + trial * 1009 + sum(map(ord, case["id"]))
            ).shuffle(order)
            for name in order:
                result, elapsed, cpu = timed_batch(actions[name], batch)
                if snapshot(result) != want["result"]:
                    raise RuntimeError(f"timing correctness mismatch: {name} {case['id']}")
                timings[name].append(elapsed)
                cpu_timings[name].append(cpu)

        memory = {
            name: peak_python_memory(action, want["result"])
            for name, action in actions.items()
        }
        heaps = {
            name: allocation_samples(counter, action, want["result"], args.allocation_samples)
            for name, action in actions.items()
        }
        wall_speedup = geometric_mean(
            baseline / candidate
            for baseline, candidate in zip(
                timings["stdlib"], timings["rust"], strict=True
            )
        )
        cpu_speedup = geometric_mean(
            baseline / candidate
            for baseline, candidate in zip(
                cpu_timings["stdlib"], cpu_timings["rust"], strict=True
            )
        )
        row = {
            "case": case["id"],
            "cohort": case["cohort"],
            "category": case["category"],
            "api": case["api"],
            "lifecycle": case["lifecycle"],
            "input": source_kind(case),
            "subject_length": length,
            "result_count": result_count(want["result"]),
            "batch_ops": batch,
            "trials": args.trials,
            "wall_ns_per_op": timings,
            "thread_cpu_ns_per_op": cpu_timings,
            "wall_speedup": wall_speedup,
            "thread_cpu_speedup": cpu_speedup,
            "traced_peak_bytes": memory,
            "native_heap": heaps,
        }
        rows.append(row)
        rust_heap = heaps["rust"]
        stdlib_heap = heaps["stdlib"]
        print(
            f"{index + 1:>3}/{len(pairs)} {case['id']:<47} "
            f"speed={wall_speedup:.4f} cpu={cpu_speedup:.4f} "
            f"rust_alloc={sum(rust_heap[field] for field in FIELDS[:3]):.0f} "
            f"rust_bytes={sum(rust_heap[field] for field in FIELDS[4:7]):.0f} "
            f"std_alloc={sum(stdlib_heap[field] for field in FIELDS[:3]):.0f}",
            flush=True,
        )

    after = artifact_stamps()
    drift = before != after
    result = {
        "schema": "rebar-rust-readonly-native-allocator-profile-v6",
        "expected_sha256": manifest["expected_sha256"],
        "cohort": args.cohort,
        "selection": categories,
        "requested_cases": len(pairs),
        "measured_cases": len(rows),
        "correctness_checks": len(rows) * 2 * (
            args.trials + args.allocation_samples + 3
        ),
        "trials": args.trials,
        "variant_indexes": args.variant,
        "elapsed_seconds": time.monotonic() - started,
        "artifacts_before": before,
        "artifacts_after": after,
        "artifact_drift": drift,
        "pymalloc_caveat": (
            "LD_PRELOAD records glibc malloc/calloc/realloc/free, including "
            "Rust allocations. CPython small-object pymalloc arena reuse is "
            "not a native malloc call; tracemalloc independently records "
            "Python and PyMem allocations."
        ),
        "families": summarize_families(rows),
        "rows": rows,
    }
    write_result(result, args.output)
    if drift:
        raise RuntimeError(
            "production native binaries changed during measurement; "
            f"discard {args.output}"
        )
    if len(rows) != len(pairs):
        raise RuntimeError(
            f"measurement exceeded {args.max_seconds}s; "
            f"only {len(rows)}/{len(pairs)} frozen cases completed"
        )
    print(
        json.dumps(
            {
                "output": args.output,
                "measured_cases": len(rows),
                "requested_cases": len(pairs),
                "correctness_checks": result["correctness_checks"],
                "elapsed_seconds": round(result["elapsed_seconds"], 3),
                "artifact_drift": drift,
            },
            sort_keys=True,
        ),
        flush=True,
    )


def python_profile(args):
    before = artifact_stamps()
    _, cases, expected, manifest = frozen()
    rust = importlib.import_module("candidates.rust_candidate")
    categories = args.category or [
        "deeper-quote-captures",
        "deeper-config-lines",
        "expanded-html-tags",
        "deeper-unicode-casefold",
        "deeper-combining-wide",
        "deeper-search-long-hit",
        "deeper-search-long-miss",
        "deeper-cold-compile",
    ]
    chosen = selected_cases(cases, expected, categories, [args.profile_variant], args.cohort)
    rows = []
    for case, want in chosen:
        correctness_gate(rust, case, want)
        action = operation(rust, case)
        loops = max(1, min(case["ops"], args.profile_ops))
        profiler = cProfile.Profile()
        profiler.enable()
        result = None
        for _ in range(loops):
            result = action()
        profiler.disable()
        if snapshot(result) != want["result"]:
            raise RuntimeError(f"Python profile correctness mismatch: {case['id']}")
        output = io.StringIO()
        stats = pstats.Stats(profiler, stream=output).strip_dirs().sort_stats("cumulative")
        stats.print_stats(args.top)
        rows.append(
            {
                "case": case["id"],
                "category": case["category"],
                "api": case["api"],
                "subject_length": len(case.get("string") or ""),
                "loops": loops,
                "total_calls": stats.total_calls,
                "primitive_calls": stats.prim_calls,
                "total_seconds": stats.total_tt,
                "profile": output.getvalue(),
            }
        )
        print(f"profiled {case['id']} ({loops} operations)", flush=True)
        print(output.getvalue(), flush=True)

    after = artifact_stamps()
    result = {
        "schema": "rebar-rust-readonly-python-cprofile-v6",
        "expected_sha256": manifest["expected_sha256"],
        "artifacts_before": before,
        "artifacts_after": after,
        "artifact_drift": before != after,
        "correctness_checks": len(rows) * 2,
        "rows": rows,
    }
    write_result(result, args.output)
    if result["artifact_drift"]:
        raise RuntimeError("production native binaries changed during Python profiling")
    print(
        json.dumps(
            {
                "output": args.output,
                "profiles": len(rows),
                "artifact_drift": False,
            },
            sort_keys=True,
        ),
        flush=True,
    )


def write_result(result, output):
    if not output:
        return
    destination = Path(output).resolve()
    if not destination.is_relative_to(Path("/tmp")):
        raise RuntimeError("external allocator profiler writes artifacts only inside /tmp")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def self_test(_args):
    suite, cases, expected, manifest = frozen()
    chosen = selected_cases(
        cases,
        expected,
        list(DEFAULT_CATEGORIES),
        [0, 7, 15, 31, 63],
        "holdout",
    )
    ids = [case["id"] for case, _ in chosen]
    if len(ids) != 137 or len(ids) != len(set(ids)):
        raise RuntimeError(f"allocator sample denominator changed: {len(ids)}")
    if geometric_mean((1, 1, 1)) != 1.0:
        raise RuntimeError("allocator performance self-oracle is not exactly 1.0")
    if result_count([]) != 0 or result_count([1, 2]) != 2:
        raise RuntimeError("allocator result-count self-oracle failed")
    if len(cases) != manifest["cases"]:
        raise RuntimeError("allocator self-test detected frozen fixture drift")

    preload_active = False
    try:
        counter = NativeAllocationCounter()
    except RuntimeError:
        pass
    else:
        libc = ctypes.CDLL(None)
        libc.malloc.argtypes = [ctypes.c_size_t]
        libc.malloc.restype = ctypes.c_void_p
        libc.free.argtypes = [ctypes.c_void_p]
        libc.free.restype = None

        def allocate():
            pointer = libc.malloc(8192)
            if not pointer:
                raise MemoryError("native allocator self-test could not allocate 8192 bytes")
            libc.free(pointer)
            return True

        result, counts = counter.sample(allocate)
        if (
            result is not True
            or counts["malloc_calls"] < 1
            or counts["malloc_bytes"] < 8192
            or counts["free_calls"] < 1
            or counts["failed_calls"]
        ):
            raise RuntimeError(f"preloaded native allocator self-oracle failed: {counts}")
        preload_active = True

    result = {
        "schema": "rebar-rust-native-allocator-self-test-v6",
        "expected_sha256": manifest["expected_sha256"],
        "frozen_cases": len(cases),
        "sample_cases": len(chosen),
        "sample_families": len(DEFAULT_CATEGORIES),
        "frozen_trials": suite.TRIALS,
        "native_preload_active": preload_active,
        "artifacts": artifact_stamps(),
        "failed": 0,
    }
    write_result(result, getattr(_args, "output", None))
    print(json.dumps(result, sort_keys=True), flush=True)


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("the value must be a positive integer")
    return number


def nonnegative_int(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("the value must not be negative")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)

    history = commands.add_parser("historical")
    history.add_argument("--cohort", choices=("calibration", "holdout", "all"), default="holdout")
    history.add_argument("--output", default="/tmp/rebar-rust-readonly-historical-v6.json")
    history.set_defaults(function=historical)

    family = commands.add_parser("families")
    family.add_argument("--cohort", choices=("calibration", "holdout"), default="holdout")
    family.add_argument("--category", action="append")
    family.add_argument("--variant", type=nonnegative_int, action="append", default=None)
    family.add_argument("--trials", type=positive_int, default=5)
    family.add_argument("--max-ops", type=positive_int, default=24)
    family.add_argument("--allocation-samples", type=positive_int, default=3)
    family.add_argument("--max-seconds", type=float, default=180)
    family.add_argument("--output", default="/tmp/rebar-rust-readonly-allocator-v6.json")
    family.set_defaults(function=family_timing)

    profile = commands.add_parser("python-profile")
    profile.add_argument("--cohort", choices=("calibration", "holdout"), default="holdout")
    profile.add_argument("--category", action="append")
    profile.add_argument("--profile-variant", type=nonnegative_int, default=7)
    profile.add_argument("--profile-ops", type=positive_int, default=16)
    profile.add_argument("--top", type=positive_int, default=18)
    profile.add_argument("--output", default="/tmp/rebar-rust-readonly-cprofile-v6.json")
    profile.set_defaults(function=python_profile)

    test = commands.add_parser("self-test")
    test.add_argument("--output")
    test.set_defaults(function=self_test)

    args = parser.parse_args()
    if getattr(args, "max_seconds", 1.0) <= 0:
        parser.error("--max-seconds must be positive")
    if hasattr(args, "variant") and args.variant is None:
        args.variant = [0, 7, 15, 31, 63]
    args.function(args)


if __name__ == "__main__":
    main()
