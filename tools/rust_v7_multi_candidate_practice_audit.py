#!/usr/bin/env python3
"""Independently replay the frozen, four-way public practice measurement.

This verifier never imports, runs, or times a regular-expression candidate.  It
reconstructs every paired observation and confidence interval from the recorded
public practice data, the previously frozen practice plan, and the existing
independent source and native-library audit.  It never accesses a held-out case.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import gzip
import hashlib
import io
import json
import math
import os
import platform
import random
import statistics
import sys
from pathlib import Path
from typing import BinaryIO


ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "performance/v7/evidence"
RAW_PATH = EVIDENCE / "three-qualified-engines-public-practice-v1-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE / "three-qualified-engines-public-practice-v1-summary.json"
OUTPUT_PATH = EVIDENCE / "three-qualified-engines-public-practice-v1-integrity.json"
AUDIT_PATH = ROOT / "candidates/audits/FROM-SCRATCH-AUDIT.json"
PLAN_PATH = ROOT / "candidates/evidence/rust-v7-calibration-plan.json"
EDGE_SOURCE_PATH = ROOT / "tools/rust_v7_edge_oracle.py"
STDLIB_EDGE_PATH = ROOT / "candidates/evidence/rust-v7-edge-oracle-stdlib-baseline.json.gz"
PINNED_PYTHON = Path("/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14")
PINNED_RE = PINNED_PYTHON.parent.parent / "lib/python3.14/re/__init__.py"

SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v1"
ROW_SCHEMA = "rebar-rust-balanced-calibration-row-v7"
SUMMARY_SCHEMA = "rebar-rust-balanced-calibration-pilot-v7"
PLAN_SCHEMA = "rebar-rust-balanced-calibration-plan-v7"
EDGE_SCHEMA = "rebar-v7-independent-edge-oracle-v1"
PRACTICE = "calibration"
MODULES = (
    "re",
    "candidates.rust_candidate",
    "candidates.vm_candidate",
    "candidates.zig_candidate",
)
FAMILIES = {
    "candidates.rust_candidate": "rust",
    "candidates.vm_candidate": "vm",
    "candidates.zig_candidate": "zig",
}
EXPECTED_SUMMARY_SHA256 = "20c33badfc08d98566c5476452370f042cd8ff544ecc5ed98f6d1111550328f0"
EXPECTED_COMPRESSED_RAW_SHA256 = "9cc74e1baddc2dc954c26802956e0a37c10a320eef4f3eb9425b55977ea19f3c"
EXPECTED_RAW_SHA256 = "83fbd07a3062e6ba374d8558234f5997fbaf5b59050af85c9ba6bcd15d532881"
EXPECTED_AUDIT_SHA256 = "94b00886ab790d096f243775540d2590c33ea7a316d9a6098cd40d52b19f6f09"
EXPECTED_PLAN_SHA256 = "8e3da72df3c69ad68c181574ad62ed6bf77e2e9cd9987111aa7accbec6901744"
EXPECTED_EDGE_SOURCE_SHA256 = "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
EXPECTED_EDGE_ANSWER_SHA256 = "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
EXPECTED_STDLIB_EDGE_SHA256 = "38d5cdcce6a2f6d8baaa194d4866ebd582400a6b425387ae951ca65f2d0ea40a"
EXPECTED_FROZEN_ANSWER_SHA256 = "2e6c098bd3a4757620461363106a9795f8defa98fe8bc9c13c0ebbf7ed58b598"
EXPECTED_SLOT = "three-qualified-engines-public-practice-v1"
EXPECTED_CASES = 624
EXPECTED_CATEGORIES = 260
EXPECTED_APIS = 12
EXPECTED_TRIALS = 7
EXPECTED_BOOTSTRAPS = 499
EXPECTED_WARMUPS = 4
EXPECTED_MAX_OPERATIONS = 16
EXPECTED_REGRESSIONS = 426
EXPECTED_ROWS = EXPECTED_CASES * EXPECTED_TRIALS * len(MODULES)
EXPECTED_CORRECTNESS_CHECKS = EXPECTED_ROWS * 3
REGRESSION_THRESHOLD = 5.0 / 6.0
MAX_RAW_LINE_BYTES = 131_072
MAX_EDGE_BYTES = 8 * 1024 * 1024

ROW_KEYS = frozenset({
    "api", "case", "category", "cohort", "elapsed_ns", "expected_sha256",
    "frozen_operations", "hwm_kb", "input", "lifecycle", "measurement",
    "module", "ns_per_op", "operations", "order", "peak_traced_bytes",
    "result_density", "rss_after_kb", "rss_before_kb", "schema",
    "selection_reasons", "trial",
})


class AuditError(RuntimeError):
    """Recorded evidence is missing, inconsistent, or not independently bound."""


@dataclasses.dataclass(frozen=True)
class Profile:
    cases: int = EXPECTED_CASES
    trials: int = EXPECTED_TRIALS
    bootstraps: int = EXPECTED_BOOTSTRAPS
    categories: int = EXPECTED_CATEGORIES
    apis: int = EXPECTED_APIS

    @property
    def rows(self) -> int:
        return self.cases * self.trials * len(MODULES)


def require(condition: object, message: str) -> None:
    if not condition:
        raise AuditError(message)


def is_positive(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1_048_576), b""):
                digest.update(chunk)
    except OSError as error:
        raise AuditError(f"cannot read required evidence: {display_path(path)}") from error
    return digest.hexdigest()


def display_path(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict[str, object] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def reject_nonfinite(value: str) -> object:
    raise AuditError(f"non-finite JSON number in recorded evidence: {value}")


def decode_json(payload: bytes, label: str) -> dict:
    try:
        result = json.loads(
            payload,
            object_pairs_hook=unique_object,
            parse_constant=reject_nonfinite,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise AuditError(f"invalid {label}") from error
    require(isinstance(result, dict), f"{label} is not a JSON object")
    return result


def read_json(path: Path, label: str, expected_sha256: str) -> dict:
    require(path.is_file(), f"missing {label}")
    require(sha256_file(path) == expected_sha256, f"{label} no longer has its frozen SHA-256")
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise AuditError(f"cannot read {label}") from error
    return decode_json(payload, label)


def percentile(values: list[float], quantile: float) -> float:
    require(values and 0.0 <= quantile <= 1.0, "invalid bootstrap percentile")
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    left = math.floor(position)
    right = math.ceil(position)
    fraction = position - left
    return ordered[left] * (1.0 - fraction) + ordered[right] * fraction


def confidence_interval(logs: list[float], seed: int, draws: int) -> tuple[float, float]:
    require(logs and draws > 0, "cannot bootstrap missing paired observations")
    require(all(math.isfinite(value) for value in logs), "non-finite paired log speed")
    generator = random.Random(seed)
    size = len(logs)
    samples = [
        math.exp(statistics.fmean(logs[generator.randrange(size)] for _ in range(size)))
        for _ in range(draws)
    ]
    return percentile(samples, 0.025), percentile(samples, 0.975)


def paired_seed(base_seed: int, case: str, candidate: str) -> int:
    payload = f"{base_seed}:{case}:{candidate}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def expected_order(case: str, trial: int, order_seed: int) -> tuple[str, ...]:
    result = list(MODULES)
    random.Random(order_seed + trial * 1009 + sum(map(ord, case))).shuffle(result)
    return tuple(result)


def validate_plan(plan: dict, profile: Profile) -> dict[str, dict]:
    require(plan.get("schema") == PLAN_SCHEMA, "incorrect frozen public practice plan")
    require(plan.get("cohort") == PRACTICE, "practice plan contains a non-practice cohort")
    require(plan.get("holdout_accessed") is False, "practice plan accessed held-out cases")
    require(plan.get("failed") == 0, "practice plan contains failures")
    require(plan.get("cases") == profile.cases, "frozen practice case denominator changed")
    require(plan.get("default_trials") == profile.trials, "public practice trial count changed")
    require(plan.get("default_bootstrap_samples") == profile.bootstraps, "public bootstrap count changed")
    require(plan.get("maximum_operations_per_trial") == EXPECTED_MAX_OPERATIONS, "operation bound changed")
    require(plan.get("strict_regression_speedup_threshold") == REGRESSION_THRESHOLD, "strict slowdown threshold changed")
    entries = plan.get("selected_cases")
    require(isinstance(entries, list) and len(entries) == profile.cases, "frozen practice case list changed")
    cases: dict[str, dict] = {}
    for entry in entries:
        require(isinstance(entry, dict), "invalid frozen public practice case")
        identifier = entry.get("case")
        require(isinstance(identifier, str) and identifier not in cases, "duplicate frozen public practice case")
        require(entry.get("cohort") == PRACTICE, "held-out case entered public practice")
        require(isinstance(entry.get("selection_reasons"), list), "frozen case selection proof is absent")
        operations = entry.get("frozen_operations")
        require(isinstance(operations, int) and not isinstance(operations, bool) and operations > 0, "invalid frozen operation count")
        cases[identifier] = entry
    return cases


def validate_header(summary: dict, plan: dict, profile: Profile, raw_path: Path | None) -> None:
    require(summary.get("schema") == SUMMARY_SCHEMA, "incorrect public practice summary schema")
    require(summary.get("cohort") == PRACTICE, "summary contains held-out workloads")
    require(summary.get("holdout_accessed") is False, "summary admits holdout access")
    require(summary.get("failed") == 0, "practice correctness gate reports a failure")
    require(summary.get("modules") == list(MODULES), "baseline or candidate module order changed")
    require(summary.get("cases") == profile.cases, "summary changed the practice denominator")
    require(summary.get("trials") == profile.trials, "summary changed paired trial count")
    require(summary.get("bootstrap_samples") == profile.bootstraps, "summary changed bootstrap draws")
    require(summary.get("warmups") == EXPECTED_WARMUPS, "summary changed warmups")
    require(summary.get("maximum_operations_per_trial") == EXPECTED_MAX_OPERATIONS, "summary changed the timing bound")
    require(summary.get("paired_raw_rows") == profile.rows, "summary changed the raw timing denominator")
    require(summary.get("correctness_checks") == profile.rows * 3, "summary concealed a correctness gate")
    require(summary.get("strict_regression_speedup_threshold") == REGRESSION_THRESHOLD, "summary changed the strict 20% boundary")
    require(summary.get("all_bounded_workload_categories") == profile.categories, "summary changed the category denominator")
    require(isinstance(summary.get("public_operations"), dict) and len(summary["public_operations"]) == profile.apis, "summary omitted a public API")
    for key in (
        "public_operations", "lifetimes", "inputs", "result_densities",
        "api_lifetimes", "bootstrap_seed", "selection_seed", "order_seed",
        "expected_sha256", "all_bounded_workload_categories",
    ):
        require(summary.get(key) == plan.get(key), f"summary changed the frozen {key}")
    if raw_path is not None:
        require(summary.get("exclusive_slot") == EXPECTED_SLOT, "public run used a different exclusive slot")
        require(summary.get("raw_path") == str(raw_path.resolve()), "summary identifies a different raw observation file")
        require(
            summary.get("measurement") == "balanced practice diagnostic only; not a holdout result or final speed claim",
            "practice results are misrepresented as final performance",
        )


def validate_memory(row: dict) -> None:
    for key in ("rss_before_kb", "rss_after_kb", "hwm_kb"):
        value = row.get(key)
        require(
            value is None or (isinstance(value, int) and not isinstance(value, bool) and value >= 0),
            f"invalid process memory observation: {key}",
        )
    after = row.get("rss_after_kb")
    high = row.get("hwm_kb")
    require(after is None or high is None or high >= after, "process high-water memory is less than observed memory")
    peak = row.get("peak_traced_bytes")
    require(isinstance(peak, int) and not isinstance(peak, bool) and peak >= 0, "invalid traced Python allocation")


def validate_row(
    row: dict,
    cases: dict[str, dict],
    profile: Profile,
    order_seed: int,
    seen: set[tuple[str, int, str]],
) -> tuple[str, int, str]:
    require(frozenset(row) == ROW_KEYS, "practice raw observation fields changed")
    require(row.get("schema") == ROW_SCHEMA, "practice raw observation schema changed")
    require(row.get("cohort") == PRACTICE, "held-out observation entered public practice")
    identifier = row.get("case")
    require(isinstance(identifier, str) and identifier in cases, "unknown or omitted frozen practice case")
    case = cases[identifier]
    module = row.get("module")
    require(module in MODULES, "unknown or substituted production engine")
    trial = row.get("trial")
    require(isinstance(trial, int) and not isinstance(trial, bool) and 0 <= trial < profile.trials, "invalid paired trial")
    key = (identifier, trial, module)
    require(key not in seen, "duplicated frozen case, paired trial, or engine")
    for name in ("category", "api", "lifecycle", "input", "result_density", "selection_reasons", "frozen_operations"):
        require(row.get(name) == case.get(name), f"practice observation changed frozen {name}")
    require(row.get("expected_sha256") == case.get("expected_result_sha256"), "practice observation changed the frozen expected answer")
    operations = row.get("operations")
    require(
        isinstance(operations, int)
        and not isinstance(operations, bool)
        and operations == min(case["frozen_operations"], EXPECTED_MAX_OPERATIONS),
        "practice observation exceeded or changed its operation bound",
    )
    require(row.get("order") == expected_order(identifier, trial, order_seed).index(module), "paired engine execution order changed")
    elapsed = row.get("elapsed_ns")
    require(isinstance(elapsed, int) and not isinstance(elapsed, bool) and elapsed > 0, "invalid or zero elapsed time")
    require(is_positive(row.get("ns_per_op")) and row["ns_per_op"] == elapsed / operations, "invalid per-operation timing")
    require(
        row.get("measurement") == "bounded practice diagnostic only; not a holdout result",
        "raw observations claim final or held-out performance",
    )
    validate_memory(row)
    return key


def read_observations(
    source: BinaryIO,
    compressed_sha256: str,
    summary: dict,
    plan: dict,
    profile: Profile,
) -> dict[tuple[str, int, str], dict]:
    require(compressed_sha256 == summary.get("compressed_raw_sha256"), "compressed practice observations changed")
    header = source.read(10)
    require(len(header) == 10 and header[:2] == b"\x1f\x8b", "practice observations have no gzip header")
    require(header[3] & 0x08 == 0 and header[4:8] == b"\0\0\0\0", "practice gzip header is not reproducible")
    source.seek(0)
    frozen_cases = validate_plan(plan, profile)
    seen: set[tuple[str, int, str]] = set()
    observations: dict[tuple[str, int, str], dict] = {}
    raw_digest = hashlib.sha256()
    try:
        with gzip.GzipFile(fileobj=source, mode="rb") as archive:
            for number in range(profile.rows + 1):
                encoded = archive.readline(MAX_RAW_LINE_BYTES + 1)
                if not encoded:
                    break
                require(number < profile.rows, "practice observations contain additional rows")
                require(len(encoded) <= MAX_RAW_LINE_BYTES and encoded.endswith(b"\n"), "invalid or oversized practice observation")
                raw_digest.update(encoded)
                row = decode_json(encoded, f"public practice raw observation {number + 1}")
                key = validate_row(row, frozen_cases, profile, plan["order_seed"], seen)
                seen.add(key)
                observations[key] = row
    except (OSError, EOFError, zlib_error()) as error:
        raise AuditError("truncated or corrupted public practice gzip observations") from error
    require(raw_digest.hexdigest() == summary.get("raw_sha256"), "uncompressed public practice observations changed")
    require(len(observations) == profile.rows, "practice observations changed their raw-row denominator")
    for case in plan["selected_cases"]:
        for trial in range(profile.trials):
            for module in MODULES:
                require((case["case"], trial, module) in observations, "practice observations omitted a paired case, trial, or engine")
    counts = collections.Counter(module for _, _, module in observations)
    require(counts == collections.Counter({module: profile.cases * profile.trials for module in MODULES}), "paired engines have unequal case or trial weights")
    return observations


def zlib_error() -> type[Exception]:
    # gzip raises zlib.error for a poisoned compressed stream.
    import zlib

    return zlib.error


def recompute_results(
    plan: dict,
    observations: dict[tuple[str, int, str], dict],
    profile: Profile,
) -> tuple[list[dict], list[dict]]:
    results: list[dict] = []
    bootstrap_seed = plan["bootstrap_seed"]
    for case in plan["selected_cases"]:
        identifier = case["case"]
        baseline = [observations[identifier, trial, "re"] for trial in range(profile.trials)]
        for candidate in MODULES[1:]:
            contender = [observations[identifier, trial, candidate] for trial in range(profile.trials)]
            logs = [
                math.log(reference["ns_per_op"] / observed["ns_per_op"])
                for reference, observed in zip(baseline, contender, strict=True)
            ]
            low, high = confidence_interval(
                logs, paired_seed(bootstrap_seed, identifier, candidate), profile.bootstraps
            )
            speedup = math.exp(statistics.fmean(logs))
            results.append({
                "case": identifier,
                "cohort": PRACTICE,
                "category": case["category"],
                "api": case["api"],
                "lifecycle": case["lifecycle"],
                "input": case["input"],
                "result_density": case["result_density"],
                "candidate": candidate,
                "weight": 1,
                "speedup": speedup,
                "ci95_low": low,
                "ci95_high": high,
                "baseline_ns": statistics.median(row["ns_per_op"] for row in baseline),
                "candidate_ns": statistics.median(row["ns_per_op"] for row in contender),
                "peak_traced_ratio": (
                    statistics.median(row["peak_traced_bytes"] for row in contender)
                    / max(1, statistics.median(row["peak_traced_bytes"] for row in baseline))
                ),
                "statistically_faster": low > 1.0,
                "regression_gt_20pct": speedup < REGRESSION_THRESHOLD,
            })

    rankings: list[dict] = []
    for candidate in MODULES[1:]:
        selected = [row for row in results if row["candidate"] == candidate]
        require(len(selected) == profile.cases, "ranking omitted public practice cases")
        logs = [math.log(row["speedup"]) for row in selected]
        low, high = confidence_interval(
            logs, paired_seed(bootstrap_seed, PRACTICE, candidate), profile.bootstraps
        )
        rankings.append({
            "cohort": PRACTICE,
            "candidate": candidate,
            "cases": len(selected),
            "weight": sum(row["weight"] for row in selected),
            "geomean_speedup": math.exp(statistics.fmean(logs)),
            "ci95_low": low,
            "ci95_high": high,
            "statistically_faster_cases": sum(row["statistically_faster"] for row in selected),
            "regressions_gt_20pct": sum(row["regression_gt_20pct"] for row in selected),
        })
    rankings.sort(key=lambda row: (-row["geomean_speedup"], row["candidate"]))
    return results, rankings


def validate_results(summary: dict, results: list[dict], rankings: list[dict], profile: Profile) -> list[dict]:
    require(len(results) == profile.cases * (len(MODULES) - 1), "candidate-case denominator changed")
    require(summary.get("case_results") == results, "recorded speed, bootstrap confidence, memory, or case flags do not reproduce")
    require(summary.get("rankings") == rankings, "recorded aggregate confidence, ranking, or win counts do not reproduce")
    regressions = [row for row in results if row["speedup"] < REGRESSION_THRESHOLD]
    require(summary.get("regressions") == regressions, "recorded evidence omitted, added, or altered a substantial slowdown")
    for row in results:
        require(is_positive(row["speedup"]) and is_positive(row["ci95_low"]) and is_positive(row["ci95_high"]), "invalid speedup or confidence interval")
        require(row["ci95_low"] <= row["ci95_high"], "confidence interval endpoints are inverted")
        require(row["statistically_faster"] is (row["ci95_low"] > 1.0), "significant-win classification changed")
        require(row["regression_gt_20pct"] is (row["speedup"] < REGRESSION_THRESHOLD), "strict slowdown boundary changed")
    return regressions


def checked_production_path(value: object, label: str) -> Path:
    require(isinstance(value, str) and bool(value), f"invalid {label} path")
    candidate = Path(value)
    require(not candidate.is_absolute(), f"{label} path escaped the repository")
    resolved = (ROOT / candidate).resolve()
    require(resolved.is_relative_to(ROOT.resolve()), f"{label} path escaped the repository")
    return resolved


def validate_independence(audit: dict) -> tuple[dict[str, str], dict[str, str]]:
    require(audit.get("schema_version") == 1 and audit.get("passed") is True and audit.get("result") == "PASS", "the canonical independence audit does not pass")
    require(audit.get("verified_core_family_count") == 3, "canonical independent core family count changed")
    require(audit.get("verified_distinct_pipeline_count") == 4, "canonical independent pipeline count changed")
    require(audit.get("core_families") == ["ast", "vm", "rust"], "canonical core family evidence changed")
    require(audit.get("all_public_source_families") == ["ast", "vm", "rust", "zig"], "canonical audited source families changed")
    self_test = audit.get("self_test")
    require(isinstance(self_test, dict) and self_test.get("passed") is True and self_test.get("check_count") == 76, "canonical audit did not pass all 76 anti-delegation controls")
    controls = self_test.get("checks")
    require(isinstance(controls, list) and len(controls) == 76, "canonical audit omitted anti-delegation controls")
    require(all(isinstance(control, dict) and control.get("passed") is True for control in controls), "a canonical anti-delegation control failed")
    scope = audit.get("scope")
    require(isinstance(scope, dict) and scope.get("benchmark_or_timing_executed") is False, "canonical audit performed benchmark timing")
    require(scope.get("holdout_or_case_fixture_access") is False, "canonical audit accessed held-out cases")
    require(scope.get("mapped_binaries_hashed_against_static_elf") is True, "canonical audit omitted mapped-binary identity")
    families = audit.get("families")
    require(isinstance(families, dict) and set(families) == {"ast", "rust", "vm", "zig"}, "canonical family evidence is incomplete")
    sources: dict[str, str] = {}
    for family in ("rust", "vm", "zig"):
        evidence = families.get(family)
        require(isinstance(evidence, dict) and evidence.get("passed") is True, f"{family} is not independently verified")
        pipeline = evidence.get("owned_pipeline")
        runtime = evidence.get("isolated_runtime")
        require(isinstance(pipeline, dict) and pipeline.get("passed") is True, f"{family} does not own its semantic pipeline")
        require(isinstance(runtime, dict) and runtime.get("passed") is True, f"{family} failed isolated independence checks")
        source_entries = [evidence.get("python_source"), *evidence.get("native_sources", [])]
        require(source_entries and all(isinstance(item, dict) for item in source_entries), f"{family} source evidence is missing")
        for item in source_entries:
            require(item.get("passed") is True and item.get("issues") == [], f"{family} contains forbidden delegation or source issues")
            path = checked_production_path(item.get("file"), f"{family} source")
            digest = item.get("sha256")
            require(sha256_file(path) == digest, f"audited {family} production source changed")
            relative = display_path(path)
            require(relative not in sources, "independent engine families share a production source")
            sources[relative] = digest

    native = audit.get("native_elf_provenance")
    require(isinstance(native, dict) and native.get("passed") is True, "canonical native-library independence audit failed")
    require(native.get("audited_binary_count") == 5 and native.get("expected_binary_count") == 5, "canonical audit did not verify all five native libraries")
    native_families = native.get("families")
    require(isinstance(native_families, dict) and set(native_families) == {"rust", "vm", "zig"}, "native audit omitted an independently measured engine")
    expected_native = {
        "rust": {
            "bridge": ("candidates.rust_candidate:native-bridge", "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
            "engine": ("candidates.rust_candidate:native-engine", "candidates/_rust_engine.so"),
        },
        "vm": {
            "native": ("candidates.vm_candidate:native-engine", "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"),
        },
        "zig": {
            "bridge": ("candidates.zig_candidate:native-bridge", "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so"),
            "engine": ("candidates.zig_candidate:native-engine", "candidates/_zig_probe.so"),
        },
    }
    native_fingerprints: dict[str, str] = {}
    expected_paths: set[str] = set()
    for family, expected in expected_native.items():
        evidence = native_families.get(family)
        require(isinstance(evidence, dict) and evidence.get("passed") is True, f"{family} native independence proof failed")
        files = evidence.get("files")
        require(isinstance(files, dict) and set(files) == set(expected), f"{family} native library roles changed")
        for role, (fingerprint_key, expected_path) in expected.items():
            entry = files[role]
            require(isinstance(entry, dict) and entry.get("file") == expected_path, f"{family} native library path changed")
            require(entry.get("forbidden_regex_symbols") == [] and entry.get("cross_candidate_symbols") == [], f"{family} native library delegates matching")
            path = checked_production_path(expected_path, f"{family} native library")
            digest = entry.get("sha256")
            require(sha256_file(path) == digest, f"loaded {family} native library changed")
            native_fingerprints[fingerprint_key] = digest
            expected_paths.add(expected_path)
    require(set(scope.get("native_elf_paths", [])) == expected_paths, "canonical native audit omitted an actual measured library")
    mappings = audit.get("runtime_native_mapping_provenance")
    require(isinstance(mappings, dict) and mappings.get("passed") is True, "canonical loaded-library mapping audit failed")
    actual_mapping = mappings.get("families")
    require(isinstance(actual_mapping, dict) and set(actual_mapping) == {"ast", "rust", "vm", "zig"}, "runtime audit omitted a candidate family")
    for family, expected_count in (("ast", 0), ("rust", 2), ("vm", 1), ("zig", 2)):
        entry = actual_mapping.get(family)
        require(
            isinstance(entry, dict)
            and entry.get("passed") is True
            and entry.get("expected_owned_mapping_count") == expected_count
            and entry.get("observed_owned_mapping_count") == expected_count,
            f"{family} loaded a missing, substituted, or shared native engine",
        )
    return dict(sorted(sources.items())), dict(sorted(native_fingerprints.items()))


def validate_measured_fingerprints(
    summary: dict,
    source_fingerprints: dict[str, str],
    native_fingerprints: dict[str, str],
) -> dict[str, str]:
    require(PINNED_RE.is_file(), "the pinned Python baseline source is missing")
    actual: dict[str, str] = {
        "re:module": sha256_file(PINNED_RE),
        "candidates.rust_candidate:module": source_fingerprints["candidates/rust_candidate.py"],
        "candidates.rust_candidate:bridge-source": source_fingerprints["candidates/rust/py_bridge.c"],
        "candidates.rust_candidate:native-source": source_fingerprints["candidates/rust/src/lib.rs"],
        "candidates.vm_candidate:module": source_fingerprints["candidates/vm_candidate.py"],
        "candidates.zig_candidate:module": source_fingerprints["candidates/zig_candidate.py"],
        **native_fingerprints,
    }
    before = summary.get("candidate_binary_sha256_before")
    after = summary.get("candidate_binary_sha256_after")
    require(isinstance(before, dict) and before == actual, "measured production sources or native binaries do not match the independence audit")
    require(isinstance(after, dict) and after == actual, "production sources or native binaries changed during paired timing")
    return dict(sorted(actual.items()))


def read_edge(path: Path, label: str) -> tuple[dict, str]:
    require(path.is_file(), f"missing {label}")
    try:
        with gzip.open(path, "rb") as source:
            payload = source.read(MAX_EDGE_BYTES + 1)
    except (OSError, EOFError, zlib_error()) as error:
        raise AuditError(f"truncated or corrupted {label}") from error
    require(len(payload) <= MAX_EDGE_BYTES, f"oversized {label}")
    return decode_json(payload, label), hashlib.sha256(payload).hexdigest()


def validate_edges(summary: dict, measured: dict[str, str]) -> list[dict]:
    require(sha256_file(EDGE_SOURCE_PATH) == EXPECTED_EDGE_SOURCE_SHA256, "frozen independent correctness-oracle source changed")
    stdlib, stdlib_digest = read_edge(STDLIB_EDGE_PATH, "pinned Python correctness report")
    require(stdlib_digest == EXPECTED_STDLIB_EDGE_SHA256, "pinned Python correctness evidence changed")
    validate_edge_document(stdlib, "re")
    references = summary.get("verified_edge_oracles")
    require(isinstance(references, list) and len(references) == len(MODULES) - 1, "summary omitted an independently correctness-qualified engine")
    expected_edges = {
        "candidates.rust_candidate": ROOT / "candidates/evidence/rust-v7-edge-oracle-rust-mandatory-prefix-inline-singleton.json.gz",
        "candidates.vm_candidate": ROOT / "candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-19.json.gz",
        "candidates.zig_candidate": ROOT / "candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-11.json.gz",
    }
    for expected_module, reference in zip(MODULES[1:], references, strict=True):
        require(isinstance(reference, dict) and reference.get("module") == expected_module, "candidate correctness proof is missing, reordered, or substituted")
        path = expected_edges[expected_module]
        require(reference.get("path") == str(path.resolve()), "candidate correctness proof path changed")
        require(reference.get("script_sha256") == EXPECTED_EDGE_SOURCE_SHA256, "candidate correctness proof uses a different oracle")
        require(reference.get("correctness_checks") == 223_198, "candidate correctness proof omitted frozen cases")
        require(reference.get("actual_sha256") == EXPECTED_EDGE_ANSWER_SHA256, "candidate correctness proof disagrees with Python")
        require(reference.get("stdlib_baseline_sha256") == stdlib_digest, "candidate correctness proof uses a different baseline")
        document, payload_digest = read_edge(path, f"{expected_module} correctness report")
        require(payload_digest == reference.get("report_sha256"), "candidate correctness proof changed after measurement")
        validate_edge_document(document, expected_module)
        artifacts = document.get("candidate_artifacts")
        require(isinstance(artifacts, list), "candidate correctness proof omitted source or native fingerprints")
        reconstructed: dict[str, dict[str, str]] = {}
        for entry in artifacts:
            require(isinstance(entry, dict) and set(entry) == {"role", "path", "sha256"}, "candidate correctness artifact fields changed")
            role = entry["role"]
            require(isinstance(role, str) and role not in reconstructed, "candidate correctness artifact role is duplicated")
            location = checked_production_path(entry.get("path"), "candidate correctness artifact")
            require(sha256_file(location) == entry.get("sha256"), "candidate correctness artifact no longer matches measured production")
            reconstructed[role] = {"path": display_path(location), "sha256": entry["sha256"]}
        require(reference.get("candidate_artifacts") == reconstructed, "summary changed independently verified source or native artifacts")
        for role, artifact in reconstructed.items():
            if role == "public-python":
                key = f"{expected_module}:module"
            elif expected_module == "candidates.vm_candidate" and role == "native-bridge":
                key = f"{expected_module}:native-engine"
            else:
                key = f"{expected_module}:{role}"
            require(measured.get(key) == artifact["sha256"], "correctness-qualified binary differs from timed production binary")
    return references


def validate_edge_document(document: dict, module: str) -> None:
    require(document.get("schema") == EDGE_SCHEMA and document.get("module") == module, "incorrect independent edge-oracle identity")
    require(document.get("correctness_checks") == 223_198 and document.get("failed") == 0, "independent edge-oracle has missing or failing checks")
    require(document.get("expected_sha256") == EXPECTED_EDGE_ANSWER_SHA256, "independent edge-oracle changed its frozen Python answers")
    require(document.get("actual_sha256") == EXPECTED_EDGE_ANSWER_SHA256, "independent candidate differs from the frozen Python answers")
    require(document.get("script_sha256") == EXPECTED_EDGE_SOURCE_SHA256, "independent edge-oracle source identity changed")
    require(document.get("performance") == "NOT MEASURED" and document.get("holdout") == "NOT ACCESSED", "correctness oracle measured or opened held-out performance")
    categories = document.get("categories")
    require(isinstance(categories, dict) and len(categories) == 49, "independent edge-oracle omitted frozen correctness categories")
    require(
        all(isinstance(count, int) and not isinstance(count, bool) and count >= 0 for count in categories.values())
        and sum(categories.values()) == 223_198,
        "independent edge-oracle changed its exact correctness denominator",
    )


def synthetic_evidence() -> tuple[dict, dict, bytes, Profile]:
    profile = Profile(cases=2, trials=3, bootstraps=19, categories=2, apis=2)
    cases = []
    for index in range(profile.cases):
        cases.append({
            "case": f"synthetic.public.{index}", "cohort": PRACTICE,
            "category": f"synthetic-category-{index}",
            "api": "search" if index == 0 else "match",
            "lifecycle": "compiled", "input": "text", "result_density": "one",
            "selection_reasons": ["synthetic-poison-control"],
            "frozen_operations": EXPECTED_MAX_OPERATIONS,
            "expected_result_sha256": hashlib.sha256(f"synthetic-answer-{index}".encode()).hexdigest(),
        })
    plan = {
        "schema": PLAN_SCHEMA, "cohort": PRACTICE, "holdout_accessed": False,
        "failed": 0, "cases": profile.cases, "default_trials": profile.trials,
        "default_bootstrap_samples": profile.bootstraps,
        "maximum_operations_per_trial": EXPECTED_MAX_OPERATIONS,
        "strict_regression_speedup_threshold": REGRESSION_THRESHOLD,
        "selected_cases": cases, "all_bounded_workload_categories": profile.categories,
        "public_operations": {"match": 1, "search": 1},
        "lifetimes": {"compiled": profile.cases}, "inputs": {"text": profile.cases},
        "result_densities": {"one": profile.cases},
        "api_lifetimes": {"match / compiled": 1, "search / compiled": 1},
        "bootstrap_seed": 1986072302, "selection_seed": 1986072311,
        "order_seed": 1986072301, "expected_sha256": EXPECTED_FROZEN_ANSWER_SHA256,
    }
    records: list[dict] = []
    module_elapsed = {
        "re": 1_600,
        "candidates.rust_candidate": 1_280,
        "candidates.vm_candidate": 960,
        "candidates.zig_candidate": 2_080,
    }
    for case_index, case in enumerate(cases):
        for trial in range(profile.trials):
            for order, module in enumerate(expected_order(case["case"], trial, plan["order_seed"])):
                elapsed = module_elapsed[module] + case_index * 16 + trial * 16
                records.append({
                    "schema": ROW_SCHEMA, "cohort": PRACTICE,
                    "case": case["case"], "trial": trial, "module": module,
                    "order": order, "api": case["api"], "category": case["category"],
                    "lifecycle": case["lifecycle"], "input": case["input"],
                    "result_density": case["result_density"],
                    "selection_reasons": case["selection_reasons"],
                    "expected_sha256": case["expected_result_sha256"],
                    "frozen_operations": case["frozen_operations"],
                    "operations": EXPECTED_MAX_OPERATIONS,
                    "elapsed_ns": elapsed, "ns_per_op": elapsed / EXPECTED_MAX_OPERATIONS,
                    "peak_traced_bytes": 100 + MODULES.index(module),
                    "rss_before_kb": 1000, "rss_after_kb": 1000, "hwm_kb": 1001,
                    "measurement": "bounded practice diagnostic only; not a holdout result",
                })
    payload = b"".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
        for row in records
    )
    compressed = gzip.compress(payload, mtime=0)
    summary = {
        "schema": SUMMARY_SCHEMA, "cohort": PRACTICE, "holdout_accessed": False,
        "failed": 0, "modules": list(MODULES), "cases": profile.cases,
        "trials": profile.trials, "bootstrap_samples": profile.bootstraps,
        "warmups": EXPECTED_WARMUPS, "maximum_operations_per_trial": EXPECTED_MAX_OPERATIONS,
        "paired_raw_rows": profile.rows, "correctness_checks": profile.rows * 3,
        "strict_regression_speedup_threshold": REGRESSION_THRESHOLD,
        "all_bounded_workload_categories": profile.categories,
        "compressed_raw_sha256": hashlib.sha256(compressed).hexdigest(),
        "raw_sha256": hashlib.sha256(payload).hexdigest(),
        **{key: plan[key] for key in (
            "public_operations", "lifetimes", "inputs", "result_densities",
            "api_lifetimes", "bootstrap_seed", "selection_seed", "order_seed",
            "expected_sha256",
        )},
    }
    observed = read_observations(
        io.BytesIO(compressed), summary["compressed_raw_sha256"], summary, plan, profile
    )
    results, rankings = recompute_results(plan, observed, profile)
    summary["case_results"] = results
    summary["rankings"] = rankings
    summary["regressions"] = [row for row in results if row["speedup"] < REGRESSION_THRESHOLD]
    return plan, summary, compressed, profile


def self_test() -> dict:
    plan, summary, compressed, profile = synthetic_evidence()

    def replay(current_plan: dict, current_summary: dict, payload: bytes) -> None:
        validate_plan(current_plan, profile)
        validate_header(current_summary, current_plan, profile, None)
        observations = read_observations(
            io.BytesIO(payload), hashlib.sha256(payload).hexdigest(),
            current_summary, current_plan, profile,
        )
        results, rankings = recompute_results(current_plan, observations, profile)
        validate_results(current_summary, results, rankings, profile)

    replay(plan, summary, compressed)
    controls: list[dict[str, object]] = []

    def reject(name: str, action: object) -> None:
        try:
            action()  # type: ignore[operator]
        except (AuditError, KeyError, ValueError, TypeError, OverflowError):
            controls.append({"name": name, "passed": True})
            return
        raise AuditError(f"synthetic poisoned practice evidence was accepted: {name}")

    def altered_summary(key: str, value: object) -> None:
        replay(plan, {**summary, key: value}, compressed)

    def altered_row(mutator: object) -> None:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as source:
            rows = [decode_json(line, "synthetic raw row") for line in source]
        mutator(rows)  # type: ignore[operator]
        encoded = b"".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
            for row in rows
        )
        poisoned = gzip.compress(encoded, mtime=0)
        poisoned_summary = {
            **summary,
            "compressed_raw_sha256": hashlib.sha256(poisoned).hexdigest(),
            "raw_sha256": hashlib.sha256(encoded).hexdigest(),
        }
        replay(plan, poisoned_summary, poisoned)

    reject("missing-candidate-module", lambda: altered_summary("modules", list(MODULES[:-1])))
    reject("reordered-baseline-or-candidates", lambda: altered_summary("modules", list(reversed(MODULES))))
    reject("changed-case-denominator", lambda: altered_summary("cases", profile.cases + 1))
    reject("changed-trial-denominator", lambda: altered_summary("trials", profile.trials + 1))
    reject("changed-raw-row-denominator", lambda: altered_summary("paired_raw_rows", profile.rows - 1))
    reject("missing-correctness-gate", lambda: altered_summary("correctness_checks", profile.rows * 3 - 1))
    reject("changed-bootstrap-draws", lambda: altered_summary("bootstrap_samples", profile.bootstraps + 1))
    reject("changed-strict-regression-threshold", lambda: altered_summary("strict_regression_speedup_threshold", 0.8))
    reject("holdout-falsely-marked-accessed", lambda: altered_summary("holdout_accessed", True))
    reject("reported-correctness-failure", lambda: altered_summary("failed", 1))
    reject("missing-candidate-case", lambda: altered_summary("case_results", summary["case_results"][:-1]))
    reject("hidden-substantial-regression", lambda: altered_summary("regressions", summary["regressions"][:-1]))
    reject("poisoned-bootstrap-interval", lambda: altered_summary(
        "case_results", [{**summary["case_results"][0], "ci95_low": 999.0}, *summary["case_results"][1:]]
    ))
    reject("poisoned-aggregate-ranking", lambda: altered_summary(
        "rankings", [{**summary["rankings"][0], "geomean_speedup": 999.0}, *summary["rankings"][1:]]
    ))
    reject("changed-compressed-hash", lambda: altered_summary("compressed_raw_sha256", "0" * 64))
    reject("changed-uncompressed-hash", lambda: altered_summary("raw_sha256", "0" * 64))
    reject("missing-paired-raw-row", lambda: altered_row(lambda rows: rows.pop()))
    reject("duplicated-paired-raw-row", lambda: altered_row(lambda rows: rows.__setitem__(1, dict(rows[0]))))
    reject("substituted-engine", lambda: altered_row(lambda rows: rows[0].__setitem__("module", "external.regex.wrapper")))
    reject("zero-elapsed-time", lambda: altered_row(lambda rows: rows[0].__setitem__("elapsed_ns", 0)))
    reject("timing-divides-by-wrong-operation-count", lambda: altered_row(lambda rows: rows[0].__setitem__("ns_per_op", rows[0]["ns_per_op"] + 1.0)))
    reject("overbound-operation-count", lambda: altered_row(lambda rows: rows[0].__setitem__("operations", EXPECTED_MAX_OPERATIONS + 1)))
    reject("substituted-frozen-case", lambda: altered_row(lambda rows: rows[0].__setitem__("case", "synthetic.secret.case")))
    reject("substituted-frozen-answer", lambda: altered_row(lambda rows: rows[0].__setitem__("expected_sha256", "0" * 64)))
    reject("altered-paired-execution-order", lambda: altered_row(lambda rows: rows[0].__setitem__("order", (rows[0]["order"] + 1) % len(MODULES))))
    reject("invalid-process-memory", lambda: altered_row(lambda rows: rows[0].__setitem__("hwm_kb", 0)))
    reject("practice-row-claims-final-performance", lambda: altered_row(lambda rows: rows[0].__setitem__("measurement", "final held-out result")))
    reject("tampered-gzip-stream", lambda: replay(plan, summary, compressed[:-4]))
    require(len(controls) >= 28, "synthetic self-test omitted required poisoned controls")
    require(REGRESSION_THRESHOLD == 5.0 / 6.0, "strict slowdown boundary changed")
    require(not (REGRESSION_THRESHOLD < REGRESSION_THRESHOLD), "exactly 20% was incorrectly counted as a regression")
    return {
        "schema": SCHEMA + "-self-test", "result": "PASS",
        "synthetic_cases": profile.cases, "synthetic_modules": len(MODULES),
        "synthetic_trials": profile.trials, "synthetic_bootstrap_draws": profile.bootstraps,
        "poisoned_controls": controls, "poisoned_control_count": len(controls),
        "holdout_accessed": False, "timing_performed": False, "failed": 0,
    }


def verify(raw_path: Path, summary_path: Path, audit_path: Path, output_path: Path) -> dict:
    require(platform.python_implementation() == "CPython" and tuple(sys.version_info[:3]) == (3, 14, 6), "verification requires the pinned CPython 3.14.6")
    require(Path(sys.executable).resolve() == PINNED_PYTHON.resolve(), "verification requires the exact pinned baseline interpreter")
    require(raw_path.resolve() == RAW_PATH.resolve(), "verification cannot substitute its frozen public raw evidence")
    require(summary_path.resolve() == SUMMARY_PATH.resolve(), "verification cannot substitute its frozen public practice summary")
    require(audit_path.resolve() == AUDIT_PATH.resolve(), "verification cannot substitute its independent source audit")
    require(output_path.resolve() == OUTPUT_PATH.resolve(), "verification cannot overwrite or redirect its unique public evidence")
    require(not output_path.exists(), "the unique public practice integrity result already exists")
    require(not any(name in sys.modules for name in MODULES[1:]), "the independent verifier unexpectedly imported a production candidate")

    profile = Profile()
    plan = read_json(PLAN_PATH, "frozen public practice plan", EXPECTED_PLAN_SHA256)
    require(plan.get("expected_sha256") == EXPECTED_FROZEN_ANSWER_SHA256, "frozen practice Python answers changed")
    validate_plan(plan, profile)
    summary = read_json(summary_path, "frozen four-way public practice summary", EXPECTED_SUMMARY_SHA256)
    validate_header(summary, plan, profile, raw_path)
    require(summary.get("compressed_raw_sha256") == EXPECTED_COMPRESSED_RAW_SHA256, "public practice compressed hash changed")
    require(summary.get("raw_sha256") == EXPECTED_RAW_SHA256, "public practice raw hash changed")
    require(sha256_file(raw_path) == EXPECTED_COMPRESSED_RAW_SHA256, "public practice compressed bytes changed")

    audit = read_json(audit_path, "canonical from-scratch independence audit", EXPECTED_AUDIT_SHA256)
    source_fingerprints, native_fingerprints = validate_independence(audit)
    measured_fingerprints = validate_measured_fingerprints(
        summary, source_fingerprints, native_fingerprints
    )
    edge_proofs = validate_edges(summary, measured_fingerprints)

    try:
        with raw_path.open("rb") as source:
            observations = read_observations(
                source, EXPECTED_COMPRESSED_RAW_SHA256, summary, plan, profile
            )
    except OSError as error:
        raise AuditError("cannot open the frozen public practice observations") from error
    results, rankings = recompute_results(plan, observations, profile)
    regressions = validate_results(summary, results, rankings, profile)
    require(len(regressions) == EXPECTED_REGRESSIONS, "the four-way practice result concealed or added a substantial slowdown")
    controls = self_test()
    require(not any(name in sys.modules for name in MODULES[1:]), "verification loaded a production candidate")

    document = {
        "schema": SCHEMA,
        "result": "PASS",
        "holdout_accessed": False,
        "timing_performed": False,
        "measurement": "independent replay of recorded public practice; not a final or held-out performance result",
        "module_order": list(MODULES),
        "cases_per_candidate": EXPECTED_CASES,
        "candidate_case_count": len(results),
        "trials_per_module_case": EXPECTED_TRIALS,
        "raw_rows": len(observations),
        "correctness_checks": EXPECTED_CORRECTNESS_CHECKS,
        "bootstrap_draws": EXPECTED_BOOTSTRAPS,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "strict_regression_speedup_threshold": REGRESSION_THRESHOLD,
        "strict_regressions": len(regressions),
        "summary_sha256": EXPECTED_SUMMARY_SHA256,
        "compressed_raw_sha256": EXPECTED_COMPRESSED_RAW_SHA256,
        "raw_sha256": EXPECTED_RAW_SHA256,
        "frozen_plan_sha256": EXPECTED_PLAN_SHA256,
        "source_sha256": sha256_file(Path(__file__).resolve()),
        "from_scratch_audit_sha256": EXPECTED_AUDIT_SHA256,
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": len(MODULES) - 1,
        "verified_native_library_count": len(native_fingerprints),
        "qualified_source_fingerprints": source_fingerprints,
        "native_elf_fingerprints": native_fingerprints,
        "candidate_binary_sha256_before": summary["candidate_binary_sha256_before"],
        "candidate_binary_sha256_after": summary["candidate_binary_sha256_after"],
        "verified_edge_oracles": edge_proofs,
        "rankings": rankings,
        "regressions": regressions,
        "self_test": controls,
        "memory_limitation": (
            "Per-case memory ratios describe Python-traced allocations only; the recorded "
            "shared-process RSS and high-water marks cannot establish isolated native-engine memory."
        ),
        "failed": 0,
    }
    encoded = (
        json.dumps(document, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n"
    ).encode("ascii")
    try:
        with output_path.open("xb") as destination:
            destination.write(encoded)
            destination.flush()
            os.fsync(destination.fileno())
    except FileExistsError as error:
        raise AuditError("the unique public practice integrity result already exists") from error
    except OSError as error:
        raise AuditError("cannot persist the unique verified public practice result") from error
    return {
        "schema": SCHEMA, "result": "PASS", "holdout_accessed": False,
        "timing_performed": False, "cases_per_candidate": EXPECTED_CASES,
        "candidate_case_count": len(results), "trials_per_module_case": EXPECTED_TRIALS,
        "raw_rows": len(observations), "correctness_checks": EXPECTED_CORRECTNESS_CHECKS,
        "bootstrap_draws": EXPECTED_BOOTSTRAPS,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "strict_regressions": len(regressions),
        "verified_native_library_count": len(native_fingerprints),
        "poisoned_control_count": controls["poisoned_control_count"],
        "output": display_path(output_path), "sha256": hashlib.sha256(encoded).hexdigest(),
        "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="run in-memory synthetic corruption controls")
    verify_parser = commands.add_parser("verify", help="independently verify the actual four-way public practice run")
    verify_parser.add_argument("--raw", type=Path, required=True)
    verify_parser.add_argument("--summary", type=Path, required=True)
    verify_parser.add_argument("--from-scratch-audit", type=Path, required=True)
    verify_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "self-test":
            result = self_test()
        else:
            result = verify(args.raw, args.summary, args.from_scratch_audit, args.output)
    except (AuditError, KeyError, ValueError, TypeError, OverflowError, RecursionError) as error:
        print(json.dumps({
            "schema": SCHEMA, "result": "FAIL", "holdout_accessed": False,
            "timing_performed": False, "error": str(error), "failed": 1,
        }, sort_keys=True))
        raise SystemExit(1) from error
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
