#!/usr/bin/env python3
"""Render only the frozen, independently replayed stage-02 public practice."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from tools import postfinal_public_practice_charts_v1 as original


ROOT = Path(__file__).resolve().parent.parent
PUBLIC_ROOT = ROOT / "performance" / "postfinal-public-v2"
EVIDENCE = PUBLIC_ROOT / "evidence"
MANIFEST = PUBLIC_ROOT / "manifest.json"
MANIFEST_SHA256 = "2228e444ae142494def731d8b94ba5fcf08c69aa8a7e04cc1c47cbebeb149b4a"
RUNNER_SHA256 = "c971e63550d8c2ed5e51058b33909d4ca7fe79287080e9780cfef3262606be27"
PREFIX = "postfinal-public-practice-v2"
SUMMARY = EVIDENCE / f"{PREFIX}-summary.json"
INTEGRITY = EVIDENCE / f"{PREFIX}-integrity.json"
PUBLIC_RAW = EVIDENCE / f"{PREFIX}-raw.jsonl.gz"
PLAN_SCHEMA = "rebar-rust-balanced-calibration-plan-v7"
PLAN_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-plan-v2"
SUMMARY_SCHEMA = "rebar-rust-balanced-calibration-pilot-v7"
SUMMARY_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-report-v2"
INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v2"

CASES = 4_096
TRIALS = 13
WARMUPS = 4
BOOTSTRAPS = 2_000
CATEGORY_COUNT = 260
SOURCE_PUBLIC_CASES = 10_312
ELIGIBLE_PUBLIC_CASES = 9_731
MAX_OPERATIONS = 16
RAW_ROWS = 212_992
CORRECTNESS_GATES = 638_976
CONFIDENCE_INTERVALS = 12_291
SOURCE_CONTROL_COUNT = 76
NATIVE_LIBRARY_COUNT = 5
SELECTION_SEED = 2_026_072_401
ORDER_SEED = 2_026_072_402
BOOTSTRAP_SEED = 2_026_072_403

MODULES = (
    "re",
    "candidates.rust_candidate",
    "candidates.vm_candidate",
    "candidates.zig_candidate",
)
CANDIDATES = MODULES[1:]
API_COUNTS = {
    "compile": 210,
    "escape": 161,
    "findall": 414,
    "finditer": 414,
    "fullmatch": 358,
    "match": 229,
    "match-surface": 241,
    "scanner": 413,
    "search": 414,
    "split": 414,
    "sub": 414,
    "subn": 414,
}
BOUNDED_API_CAPACITIES = {
    "compile": 210,
    "escape": 161,
    "findall": 2_882,
    "finditer": 2_738,
    "fullmatch": 358,
    "match": 229,
    "match-surface": 241,
    "scanner": 427,
    "search": 1_057,
    "split": 451,
    "sub": 447,
    "subn": 530,
}
EDGE_PROOF_PATHS = {
    "candidates.rust_candidate": str(
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v7-edge-oracle-rust-post-final-stage-02-parity.json.gz"
    ),
    "candidates.vm_candidate": str(
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v8-edge-oracle-vm-deep-stage-21-singleton-split-memchr.json.gz"
    ),
    "candidates.zig_candidate": str(
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v8-edge-oracle-zig-deep-stage-13.json.gz"
    ),
}
AUDIT_PATH = str(
    ROOT / "candidates" / "audits" / "FROM-SCRATCH-AUDIT.json"
)
SUMMARY_MEASUREMENT = (
    "balanced practice diagnostic only; not a holdout result or final speed claim"
)
SUMMARY_ROLE = (
    "additive post-final public practice only; not a held-out or final result"
)
INTEGRITY_MEASUREMENT = (
    "independent replay of additive public practice; not a final or held-out result"
)
SUFFIXES = ("overall", "outcomes", "api", "regressions", "memory", "rankings")

require = original.require
valid_sha256 = original.valid_sha256
same_float = original.same_float


def require_candidate_free() -> None:
    loaded = sorted(
        name
        for name in sys.modules
        if any(
            name == candidate or name.startswith(candidate + ".")
            for candidate in CANDIDATES
        )
    )
    require(not loaded, f"the chart renderer imported a production candidate: {loaded!r}")


@contextmanager
def v2_renderer() -> Iterator[None]:
    """Reuse the exact committed v1 charts without retaining v2 global changes."""

    require_candidate_free()
    require(original.MODULES == MODULES, "the committed four-way chart baseline changed")
    require(original.CANDIDATES == CANDIDATES, "the committed chart candidate order changed")
    require(original.API_COUNTS == API_COUNTS, "the selected 4,096-case API quotas changed")
    require(sum(API_COUNTS.values()) == CASES, "selected API quotas changed the public denominator")
    require(
        sum(BOUNDED_API_CAPACITIES.values()) == ELIGIBLE_PUBLIC_CASES,
        "bounded public capacities changed their separate eligible denominator",
    )
    require(original.SUFFIXES == SUFFIXES, "a required public chart was substituted")
    updates = {
        "PUBLIC_ROOT": PUBLIC_ROOT,
        "EVIDENCE": EVIDENCE,
        "MANIFEST": MANIFEST,
        "MANIFEST_SHA256": MANIFEST_SHA256,
        "PREFIX": PREFIX,
        "SUMMARY": SUMMARY,
        "INTEGRITY": INTEGRITY,
        "PLAN_SCHEMA": PLAN_SCHEMA,
        "PLAN_POSTFINAL_SCHEMA": PLAN_POSTFINAL_SCHEMA,
        "SUMMARY_SCHEMA": SUMMARY_SCHEMA,
        "SUMMARY_POSTFINAL_SCHEMA": SUMMARY_POSTFINAL_SCHEMA,
        "INTEGRITY_SCHEMA": INTEGRITY_SCHEMA,
        "CASES": CASES,
        "TRIALS": TRIALS,
        "BOOTSTRAPS": BOOTSTRAPS,
        "CATEGORY_COUNT": CATEGORY_COUNT,
        "RAW_ROWS": RAW_ROWS,
        "CORRECTNESS_GATES": CORRECTNESS_GATES,
        "CONFIDENCE_INTERVALS": CONFIDENCE_INTERVALS,
    }
    saved = {key: getattr(original, key) for key in updates}
    try:
        for key, value in updates.items():
            setattr(original, key, value)
        yield
    finally:
        for key, value in saved.items():
            setattr(original, key, value)


def require_sha256_mapping(value: object, label: str) -> dict[str, str]:
    require(isinstance(value, dict) and bool(value), f"{label} is NOT MEASURED")
    require(
        all(
            isinstance(key, str) and bool(key) and valid_sha256(digest)
            for key, digest in value.items()
        ),
        f"{label} contains an invalid SHA-256 fingerprint",
    )
    return value


def check_v2_manifest(document: object, *, manifest_sha256: str) -> dict:
    original.check_manifest(document, manifest_sha256=manifest_sha256)
    require(isinstance(document, dict), "the v2 public plan is not an object")
    expected = {
        "schema": PLAN_SCHEMA,
        "postfinal_schema": PLAN_POSTFINAL_SCHEMA,
        "protocol_version": PREFIX,
        "measurement_role": SUMMARY_ROLE,
        "cohort": "calibration",
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "historical_performance_read": False,
        "timing_performed": False,
        "runner_sha256": RUNNER_SHA256,
        "from_scratch_audit_path": AUDIT_PATH,
        "modules": list(MODULES),
        "exclusive_slot": PREFIX,
        "selection_seed": SELECTION_SEED,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "frozen_trials": TRIALS,
        "frozen_warmups": WARMUPS,
        "frozen_bootstrap_samples": BOOTSTRAPS,
        "default_trials": TRIALS,
        "default_bootstrap_samples": BOOTSTRAPS,
        "cases": CASES,
        "source_public_cases": SOURCE_PUBLIC_CASES,
        "eligible_practice_cases": ELIGIBLE_PUBLIC_CASES,
        "all_bounded_workload_categories": CATEGORY_COUNT,
        "bounded_public_api_capacities": BOUNDED_API_CAPACITIES,
        "public_operations": API_COUNTS,
        "maximum_operations_per_trial": MAX_OPERATIONS,
        "failed": 0,
    }
    for key, value in expected.items():
        require(
            document.get(key) == value and type(document.get(key)) is type(value),
            f"the frozen stage-02 public manifest {key} changed",
        )
    same_float(
        original.finite(
            document.get("strict_regression_speedup_threshold"),
            "frozen public slowdown threshold",
        ),
        5 / 6,
        "the frozen stage-02 slowdown threshold changed",
    )
    require(valid_sha256(document.get("expected_sha256")), "frozen public expected answers are missing")
    require(valid_sha256(document.get("from_scratch_audit_sha256")), "the frozen independence audit is missing")
    sources = require_sha256_mapping(
        document.get("qualified_source_fingerprints"),
        "stage-02 qualified candidate sources",
    )
    native = require_sha256_mapping(
        document.get("native_elf_fingerprints"),
        "stage-02 native libraries",
    )
    require(bool(sources), "stage-02 qualified engine sources are missing")
    require(len(native) == NATIVE_LIBRARY_COUNT, "the stage-02 plan does not bind five native libraries")

    proofs = document.get("verified_edge_oracles")
    require(
        isinstance(proofs, list) and len(proofs) == len(CANDIDATES),
        "the stage-02 plan does not bind all three independent edge gates",
    )
    modules: set[str] = set()
    for proof in proofs:
        require(isinstance(proof, dict), "invalid stage-02 correctness proof")
        module = proof.get("module")
        require(module in CANDIDATES and module not in modules, "a stage-02 candidate proof is missing or duplicated")
        require(
            proof.get("path") == EDGE_PROOF_PATHS[module],
            "the frozen stage-02 candidate edge proof was substituted",
        )
        modules.add(module)

    selected = document.get("selected_cases")
    require(
        isinstance(selected, list) and len(selected) == CASES,
        "the frozen stage-02 public selection is not exactly 4,096 cases",
    )
    by_case: dict[str, dict] = {}
    for item in selected:
        require(isinstance(item, dict), "invalid frozen public selected case")
        case = item.get("case")
        require(isinstance(case, str) and case.startswith("cal."), "a nonpublic case entered the frozen selection")
        require(case not in by_case, "the stage-02 selection repeats a public case")
        require(item.get("cohort") == "calibration", "a non-calibration case entered the stage-02 plan")
        require(item.get("api") in API_COUNTS, "an original operation disappeared from the stage-02 plan")
        require(valid_sha256(item.get("expected_result_sha256")), "a frozen public expected case answer is missing")
        by_case[case] = item
    require(
        dict(Counter(item["api"] for item in selected)) == API_COUNTS,
        "the frozen stage-02 selection changed its true operation quotas",
    )
    categories = dict(Counter(item["category"] for item in selected))
    require(
        len(categories) == CATEGORY_COUNT and document.get("categories") == categories,
        "the frozen stage-02 plan omits a workload category",
    )
    for field in ("lifetimes", "inputs", "result_densities"):
        require(isinstance(document.get(field), dict), f"the frozen public {field} are missing")
    require(isinstance(document.get("api_lifetimes"), dict), "frozen API-lifetime coverage is missing")
    return by_case


def check_v2_summary(
    document: object,
    *,
    manifest: dict,
    selected_cases: dict[str, dict],
    summary_sha256: str,
    manifest_sha256: str,
) -> original.Results:
    results = original.check_summary(
        document,
        summary_sha256=summary_sha256,
        manifest_sha256=manifest_sha256,
    )
    require(isinstance(document, dict), "the stage-02 summary is not an object")
    expected = {
        "schema": SUMMARY_SCHEMA,
        "postfinal_schema": SUMMARY_POSTFINAL_SCHEMA,
        "protocol_version": PREFIX,
        "measurement": SUMMARY_MEASUREMENT,
        "measurement_role": SUMMARY_ROLE,
        "cohort": "calibration",
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "exclusive_slot": PREFIX,
        "manifest_path": str(MANIFEST),
        "manifest_sha256": manifest_sha256,
        "from_scratch_audit_sha256": manifest["from_scratch_audit_sha256"],
        "verified_edge_oracles": manifest["verified_edge_oracles"],
        "expected_sha256": manifest["expected_sha256"],
        "selection_seed": SELECTION_SEED,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "modules": list(MODULES),
        "cases": CASES,
        "all_bounded_workload_categories": CATEGORY_COUNT,
        "public_operations": API_COUNTS,
        "lifetimes": manifest["lifetimes"],
        "inputs": manifest["inputs"],
        "result_densities": manifest["result_densities"],
        "api_lifetimes": manifest["api_lifetimes"],
        "trials": TRIALS,
        "warmups": WARMUPS,
        "maximum_operations_per_trial": MAX_OPERATIONS,
        "bootstrap_samples": BOOTSTRAPS,
        "raw_path": str(PUBLIC_RAW),
        "paired_raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_GATES,
        "failed": 0,
    }
    for key, value in expected.items():
        require(
            document.get(key) == value and type(document.get(key)) is type(value),
            f"the measured stage-02 public summary {key} changed",
        )
    for key in ("raw_sha256", "compressed_raw_sha256"):
        require(valid_sha256(document.get(key)), f"the measured stage-02 {key} is missing")

    for candidate in results.candidates:
        for row in candidate.rows:
            frozen = selected_cases.get(row["case"])
            require(frozen is not None, "the summary contains a case absent from the stage-02 plan")
            for field in (
                "cohort",
                "category",
                "api",
                "lifecycle",
                "input",
                "result_density",
            ):
                require(
                    row.get(field) == frozen.get(field),
                    f"the stage-02 public case changed its frozen {field}",
                )
        for field in ("lifecycle", "input", "result_density"):
            key = {
                "lifecycle": "lifetimes",
                "input": "inputs",
                "result_density": "result_densities",
            }[field]
            actual = dict(Counter(row[field] for row in candidate.rows))
            require(actual == manifest[key], f"a stage-02 candidate changed the frozen {key}")
        api_lifetimes = dict(
            Counter(f"{row['api']} / {row['lifecycle']}" for row in candidate.rows)
        )
        require(
            api_lifetimes == manifest["api_lifetimes"],
            "a stage-02 candidate changed frozen API-lifetime coverage",
        )
    return results


def by_candidate(rows: object, label: str) -> dict[str, dict]:
    require(isinstance(rows, list) and len(rows) == len(CANDIDATES), f"{label} is incomplete")
    indexed: dict[str, dict] = {}
    for row in rows:
        require(isinstance(row, dict), f"{label} contains an invalid candidate")
        module = row.get("candidate")
        require(module in CANDIDATES and module not in indexed, f"{label} omits or duplicates a candidate")
        indexed[module] = row
    return indexed


def check_v2_integrity(
    document: object,
    results: original.Results,
    *,
    manifest: dict,
    integrity_sha256: str,
) -> None:
    original.check_integrity(document, results, integrity_sha256=integrity_sha256)
    require(isinstance(document, dict), "the stage-02 independent integrity report is invalid")
    summary = results.summary
    expected = {
        "schema": INTEGRITY_SCHEMA,
        "result": "PASS",
        "protocol_version": PREFIX,
        "measurement": INTEGRITY_MEASUREMENT,
        "cohort": "calibration",
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "timing_performed": False,
        "candidate_imported": False,
        "module_order": list(MODULES),
        "cases_per_candidate": CASES,
        "candidate_case_count": CASES * len(CANDIDATES),
        "trials_per_module_case": TRIALS,
        "raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_GATES,
        "bootstrap_draws": BOOTSTRAPS,
        "confidence_intervals_recomputed": CONFIDENCE_INTERVALS,
        "strict_regressions": len(summary["regressions"]),
        "manifest_sha256": results.manifest_sha256,
        "summary_sha256": results.summary_sha256,
        "compressed_raw_sha256": summary["compressed_raw_sha256"],
        "raw_sha256": summary["raw_sha256"],
        "from_scratch_audit_sha256": manifest["from_scratch_audit_sha256"],
        "from_scratch_control_count": SOURCE_CONTROL_COUNT,
        "verified_independent_engine_count": len(CANDIDATES),
        "verified_native_library_count": NATIVE_LIBRARY_COUNT,
        "qualified_source_fingerprints": manifest["qualified_source_fingerprints"],
        "native_elf_fingerprints": manifest["native_elf_fingerprints"],
        "candidate_binary_sha256_before": summary["candidate_binary_sha256_before"],
        "candidate_binary_sha256_after": summary["candidate_binary_sha256_after"],
        "verified_edge_oracles": manifest["verified_edge_oracles"],
        "failed": 0,
    }
    for key, value in expected.items():
        require(
            document.get(key) == value and type(document.get(key)) is type(value),
            f"the independently replayed stage-02 public {key} changed",
        )
    same_float(
        original.finite(
            document.get("strict_regression_speedup_threshold"),
            "independently audited stage-02 slowdown threshold",
        ),
        5 / 6,
        "the independent stage-02 slowdown threshold changed",
    )
    require(
        by_candidate(document.get("rankings"), "independent stage-02 rankings")
        == by_candidate(summary.get("rankings"), "measured stage-02 rankings"),
        "the independent replay did not reproduce all three measured candidate rankings",
    )
    recorded = document.get("regressions")
    require(isinstance(recorded, list), "independently replayed public losses are NOT MEASURED")
    require(all(isinstance(row, dict) for row in recorded), "an independently replayed slowdown is invalid")
    key = lambda row: (row.get("candidate", ""), row.get("case", ""))
    require(
        sorted(recorded, key=key) == sorted(summary["regressions"], key=key),
        "the independent replay omitted or altered an individual public slowdown",
    )
    limitation = document.get("memory_limitation")
    require(
        isinstance(limitation, str)
        and "Python-traced" in limitation
        and "native-engine" in limitation,
        "the replay omits the Python-traced native-memory limitation",
    )
    controls = document.get("self_test")
    require(
        isinstance(controls, dict) and controls.get("result") == "PASS",
        "the independent stage-02 replay controls did not pass",
    )


def synthetic_documents() -> tuple[dict, dict, dict]:
    """Generate only in-memory controls; never read a real evidence artifact."""

    manifest, summary, integrity = original.synthetic_documents()
    first_module = CANDIDATES[0]
    sample = [row for row in summary["case_results"] if row["candidate"] == first_module]
    require(len(sample) == CASES, "synthetic stage-02 workload lost a candidate")
    proof_by_module = {
        proof["module"]: {**proof, "path": EDGE_PROOF_PATHS[proof["module"]]}
        for proof in summary["verified_edge_oracles"]
    }
    proofs = [proof_by_module[module] for module in CANDIDATES]
    audit_sha256 = hashlib.sha256(b"synthetic-stage-02-public-source-audit").hexdigest()
    source_fingerprints = {
        f"synthetic-public-source-{index}": hashlib.sha256(
            f"synthetic-public-source-{index}".encode("utf-8")
        ).hexdigest()
        for index in range(len(CANDIDATES))
    }
    binary_fingerprints = summary["candidate_binary_sha256_before"]
    native_fingerprints = {
        role: digest
        for role, digest in binary_fingerprints.items()
        if role.endswith(":native-engine") or role.endswith(":native-bridge")
    }
    lifetimes = dict(Counter(row["lifecycle"] for row in sample))
    inputs = dict(Counter(row["input"] for row in sample))
    densities = dict(Counter(row["result_density"] for row in sample))
    api_lifetimes = dict(
        Counter(f"{row['api']} / {row['lifecycle']}" for row in sample)
    )
    categories = dict(Counter(row["category"] for row in sample))
    expected_answers = hashlib.sha256(b"synthetic-stage-02-public-answers").hexdigest()
    manifest.update(
        {
            "protocol_version": PREFIX,
            "measurement_role": SUMMARY_ROLE,
            "cohort": "calibration",
            "holdout_accessed": False,
            "held_out_cases_generated": 0,
            "held_out_records_deserialized": 0,
            "historical_performance_read": False,
            "timing_performed": False,
            "runner_sha256": RUNNER_SHA256,
            "from_scratch_audit_path": AUDIT_PATH,
            "from_scratch_audit_sha256": audit_sha256,
            "qualified_source_fingerprints": source_fingerprints,
            "native_elf_fingerprints": native_fingerprints,
            "verified_edge_oracles": proofs,
            "modules": list(MODULES),
            "exclusive_slot": PREFIX,
            "selection_seed": SELECTION_SEED,
            "order_seed": ORDER_SEED,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "frozen_trials": TRIALS,
            "frozen_warmups": WARMUPS,
            "frozen_bootstrap_samples": BOOTSTRAPS,
            "default_trials": TRIALS,
            "default_bootstrap_samples": BOOTSTRAPS,
            "source_public_cases": SOURCE_PUBLIC_CASES,
            "eligible_practice_cases": ELIGIBLE_PUBLIC_CASES,
            "bounded_public_api_capacities": dict(BOUNDED_API_CAPACITIES),
            "maximum_operations_per_trial": MAX_OPERATIONS,
            "strict_regression_speedup_threshold": 5 / 6,
            "expected_sha256": expected_answers,
            "lifetimes": lifetimes,
            "inputs": inputs,
            "result_densities": densities,
            "api_lifetimes": api_lifetimes,
            "categories": categories,
            "selected_cases": [
                {
                    "case": row["case"],
                    "cohort": row["cohort"],
                    "category": row["category"],
                    "api": row["api"],
                    "lifecycle": row["lifecycle"],
                    "input": row["input"],
                    "result_density": row["result_density"],
                    "expected_result_sha256": hashlib.sha256(
                        row["case"].encode("utf-8")
                    ).hexdigest(),
                }
                for row in sample
            ],
            "failed": 0,
        }
    )
    manifest_sha256 = original.canonical_sha256(manifest)
    raw_sha256 = hashlib.sha256(b"synthetic-stage-02-public-observations").hexdigest()
    compressed_sha256 = hashlib.sha256(
        b"synthetic-stage-02-compressed-public-observations"
    ).hexdigest()
    summary.update(
        {
            "protocol_version": PREFIX,
            "measurement": SUMMARY_MEASUREMENT,
            "measurement_role": SUMMARY_ROLE,
            "held_out_cases_generated": 0,
            "held_out_records_deserialized": 0,
            "manifest_path": str(MANIFEST),
            "manifest_sha256": manifest_sha256,
            "from_scratch_audit_sha256": audit_sha256,
            "verified_edge_oracles": proofs,
            "expected_sha256": expected_answers,
            "selection_seed": SELECTION_SEED,
            "order_seed": ORDER_SEED,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "lifetimes": lifetimes,
            "inputs": inputs,
            "result_densities": densities,
            "api_lifetimes": api_lifetimes,
            "warmups": WARMUPS,
            "maximum_operations_per_trial": MAX_OPERATIONS,
            "raw_path": str(PUBLIC_RAW),
            "raw_sha256": raw_sha256,
            "compressed_raw_sha256": compressed_sha256,
        }
    )
    summary_sha256 = original.canonical_sha256(summary)
    integrity.update(
        {
            "protocol_version": PREFIX,
            "measurement": INTEGRITY_MEASUREMENT,
            "cohort": "calibration",
            "held_out_cases_generated": 0,
            "held_out_records_deserialized": 0,
            "timing_performed": False,
            "candidate_imported": False,
            "confidence_intervals_recomputed": CONFIDENCE_INTERVALS,
            "strict_regression_speedup_threshold": 5 / 6,
            "manifest_sha256": manifest_sha256,
            "summary_sha256": summary_sha256,
            "compressed_raw_sha256": compressed_sha256,
            "raw_sha256": raw_sha256,
            "from_scratch_audit_sha256": audit_sha256,
            "from_scratch_control_count": SOURCE_CONTROL_COUNT,
            "verified_independent_engine_count": len(CANDIDATES),
            "verified_native_library_count": NATIVE_LIBRARY_COUNT,
            "qualified_source_fingerprints": source_fingerprints,
            "native_elf_fingerprints": native_fingerprints,
            "candidate_binary_sha256_before": binary_fingerprints,
            "candidate_binary_sha256_after": binary_fingerprints,
            "verified_edge_oracles": proofs,
            "rankings": copy.deepcopy(summary["rankings"]),
            "regressions": copy.deepcopy(summary["regressions"]),
            "self_test": {"result": "PASS", "mode": "synthetic public control"},
            "memory_limitation": (
                "Peak ratios are Python-traced allocations only. Shared-process RSS "
                "and high-water marks do not establish isolated native-engine memory."
            ),
            "failed": 0,
        }
    )
    return manifest, summary, integrity


def reject_summary(
    summary: dict,
    manifest: dict,
    selected_cases: dict[str, dict],
    mutate,
    label: str,
) -> None:
    changed = copy.deepcopy(summary)
    mutate(changed)
    try:
        check_v2_summary(
            changed,
            manifest=manifest,
            selected_cases=selected_cases,
            summary_sha256=original.canonical_sha256(changed),
            manifest_sha256=original.canonical_sha256(manifest),
        )
    except (ValueError, TypeError, KeyError):
        return
    raise ValueError(f"the stage-02 public synthetic control accepted {label}")


def self_test() -> dict:
    require_candidate_free()
    with v2_renderer():
        manifest, summary, integrity = synthetic_documents()
        manifest_sha256 = original.canonical_sha256(manifest)
        summary_sha256 = original.canonical_sha256(summary)
        selected = check_v2_manifest(manifest, manifest_sha256=manifest_sha256)
        results = check_v2_summary(
            summary,
            manifest=manifest,
            selected_cases=selected,
            summary_sha256=summary_sha256,
            manifest_sha256=manifest_sha256,
        )
        check_v2_integrity(
            integrity,
            results,
            manifest=manifest,
            integrity_sha256=original.canonical_sha256(integrity),
        )
        charts = original.build_charts(results)
        require(charts == original.build_charts(results), "stage-02 public charts are not deterministic")
        require(tuple(charts) == SUFFIXES, "a required stage-02 public chart disappeared")
        mutations = (
            ("hidden-test access", lambda value: value.__setitem__("holdout_accessed", True)),
            ("generated nonpublic cases", lambda value: value.__setitem__("held_out_cases_generated", 1)),
            ("deserialized nonpublic cases", lambda value: value.__setitem__("held_out_records_deserialized", 1)),
            ("the wrong stage", lambda value: value.__setitem__("protocol_version", "postfinal-public-practice-v1")),
            ("a changed public case denominator", lambda value: value.__setitem__("cases", CASES - 1)),
            ("changed paired trials", lambda value: value.__setitem__("trials", TRIALS - 1)),
            ("changed bootstrap draws", lambda value: value.__setitem__("bootstrap_samples", BOOTSTRAPS - 1)),
            ("a substituted CPython baseline", lambda value: value["modules"].__setitem__(0, "substituted")),
            ("a substituted stage-02 source audit", lambda value: value.__setitem__("from_scratch_audit_sha256", "0" * 64)),
            ("substituted frozen edge proofs", lambda value: value["verified_edge_oracles"].pop()),
            ("a changed frozen manifest", lambda value: value.__setitem__("manifest_sha256", "0" * 64)),
            ("a changed public selection seed", lambda value: value.__setitem__("selection_seed", 0)),
            ("a changed paired order seed", lambda value: value.__setitem__("order_seed", 0)),
            ("a changed bootstrap seed", lambda value: value.__setitem__("bootstrap_seed", 0)),
            ("an omitted public case", lambda value: value["case_results"].pop()),
            ("a nonpublic case", lambda value: value["case_results"][0].__setitem__("case", "nonpublic.synthetic")),
            ("a substituted shared baseline", lambda value: value["case_results"][CASES].__setitem__("baseline_ns", 999_999.0)),
            ("unmeasured traced memory", lambda value: value["case_results"][0].__setitem__("peak_traced_ratio", None)),
            ("an omitted original public API", lambda value: value["public_operations"].__setitem__("split", 413)),
            ("a concealed individual slowdown", lambda value: value["regressions"].pop()),
            ("an invented candidate ranking", lambda value: value["rankings"][0].__setitem__("statistically_faster_cases", -1)),
            ("an omitted ranked loss", lambda value: value["rankings"][0].__setitem__("regressions_gt_20pct", -1)),
            ("substituted native code", lambda value: value["candidate_binary_sha256_after"].__setitem__(f"{CANDIDATES[0]}:native-engine", "0" * 64)),
        )
        for label, mutate in mutations:
            reject_summary(summary, manifest, selected, mutate, label)

        rejected_integrities = (
            ("invented timing", lambda value: value.__setitem__("timing_performed", True)),
            ("candidate import", lambda value: value.__setitem__("candidate_imported", True)),
            ("a wrong source-control count", lambda value: value.__setitem__("from_scratch_control_count", SOURCE_CONTROL_COUNT - 1)),
            ("a hidden native library", lambda value: value.__setitem__("verified_native_library_count", NATIVE_LIBRARY_COUNT - 1)),
            ("a removed audited loss", lambda value: value["regressions"].pop()),
            ("changed independent rankings", lambda value: value["rankings"][0].__setitem__("geomean_speedup", 99.0)),
            ("a changed confidence-interval denominator", lambda value: value.__setitem__("confidence_intervals_recomputed", CONFIDENCE_INTERVALS - 1)),
        )
        for label, mutate in rejected_integrities:
            changed = copy.deepcopy(integrity)
            mutate(changed)
            try:
                check_v2_integrity(
                    changed,
                    results,
                    manifest=manifest,
                    integrity_sha256=original.canonical_sha256(changed),
                )
            except (ValueError, TypeError, KeyError):
                continue
            raise ValueError(f"the stage-02 public integrity control accepted {label}")
    require_candidate_free()
    return {
        "result": "PASS",
        "mode": "candidate-free in-memory synthetic only; no evidence files read or written",
        "protocol_version": PREFIX,
        "charts": len(SUFFIXES),
        "synthetic_cases_per_module": CASES,
        "synthetic_workload_categories": CATEGORY_COUNT,
        "synthetic_individually_visible_slowdowns": len(summary["regressions"]),
        "adversarial_rejections": len(mutations) + len(rejected_integrities),
        "frozen_public_manifest_sha256": MANIFEST_SHA256,
        "frozen_public_runner_sha256": RUNNER_SHA256,
        "genuine_stage_02_public_results": "NOT MEASURED",
        "historical_final_benchmark": "FAILED; no final winner",
    }


def render(*, summary: Path, integrity: Path, manifest: Path, output_dir: Path) -> dict:
    require_candidate_free()
    require(
        output_dir.resolve() == EVIDENCE.resolve(),
        "stage-02 charts must use the exact additive public-v2 evidence directory",
    )
    with v2_renderer():
        public_manifest, manifest_sha256 = original.read_json(
            manifest,
            allowed=MANIFEST,
            label="frozen stage-02 public manifest",
            digest=MANIFEST_SHA256,
        )
        selected = check_v2_manifest(
            public_manifest,
            manifest_sha256=manifest_sha256,
        )
        public_summary, summary_sha256 = original.read_json(
            summary,
            allowed=SUMMARY,
            label="recorded stage-02 public summary",
        )
        results = check_v2_summary(
            public_summary,
            manifest=public_manifest,
            selected_cases=selected,
            summary_sha256=summary_sha256,
            manifest_sha256=manifest_sha256,
        )
        public_integrity, integrity_sha256 = original.read_json(
            integrity,
            allowed=INTEGRITY,
            label="independently replayed stage-02 public integrity report",
        )
        check_v2_integrity(
            public_integrity,
            results,
            manifest=public_manifest,
            integrity_sha256=integrity_sha256,
        )
        charts = original.build_charts(results)
        require_candidate_free()
        try:
            EVIDENCE.mkdir(parents=True, exist_ok=True)
            outputs: list[dict[str, str]] = []
            for suffix in SUFFIXES:
                destination = EVIDENCE / f"{PREFIX}-{suffix}.svg"
                svg = charts[suffix]
                destination.write_text(svg, encoding="utf-8", newline="\n")
                outputs.append(
                    {
                        "chart": suffix,
                        "path": str(destination),
                        "sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest(),
                    }
                )
        except OSError as error:
            raise ValueError("cannot write the exact stage-02 public evidence directory") from error

    require_candidate_free()
    return {
        "result": "PASS",
        "protocol_version": PREFIX,
        "measurement": "independently replayed stage-02 public development only",
        "manifest_sha256": manifest_sha256,
        "runner_sha256": RUNNER_SHA256,
        "summary_sha256": summary_sha256,
        "integrity_sha256": integrity_sha256,
        "public_cases_per_module": CASES,
        "individually_visible_public_slowdowns": len(public_summary["regressions"]),
        "final_failure_report_sha256": original.previous.FINAL_FAILURE_REPORT_SHA256,
        "final_failure_certificate_sha256": original.previous.FINAL_FAILURE_CERTIFICATE_SHA256,
        "historical_final_benchmark": (
            "FAILED; final speed, final memory, and final ranking NOT MEASURED; no final winner"
        ),
        "charts": outputs,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render exactly six audited, stage-02, calibration-only public "
            "practice charts without importing any candidate."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run exclusively in-memory candidate-free synthetic controls",
    )
    parser.add_argument("--summary", type=Path, help="exact stage-02 public summary")
    parser.add_argument("--integrity", type=Path, help="exact stage-02 public replay")
    parser.add_argument("--manifest", type=Path, help="exact SHA-256-pinned stage-02 public plan")
    parser.add_argument("--output-dir", type=Path, help="exact public-v2 evidence directory")
    args = parser.parse_args(argv)
    values = (args.summary, args.integrity, args.manifest, args.output_dir)
    if args.self_test:
        if any(value is not None for value in values):
            parser.error("the synthetic self-test cannot access benchmark files or chart outputs")
    elif any(value is None for value in values):
        parser.error("rendering requires explicit --summary, --integrity, --manifest, and --output-dir")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = (
            self_test()
            if args.self_test
            else render(
                summary=args.summary,
                integrity=args.integrity,
                manifest=args.manifest,
                output_dir=args.output_dir,
            )
        )
    except (OSError, TypeError, ValueError, KeyError) as error:
        print(f"stage-02 public chart rendering rejected: {error}")
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
