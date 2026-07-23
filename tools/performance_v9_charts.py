#!/usr/bin/env python3
"""Render the frozen v9 results without discovering or opening a holdout.

Normal rendering accepts only an explicitly supplied public manifest, final
summary, independently measured compressed memory evidence, and output prefix.
The timing evidence, previous experiments, candidate implementations, and
secret opening are never opened. The separately requested self-test constructs
all of its data in memory and does not read or create a file.
"""

from __future__ import annotations

import argparse
import builtins
import copy
import gzip
import hashlib
import json
import math
import statistics
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from html import escape
from pathlib import Path
from typing import Any, Callable, Mapping
from unittest import mock
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent.parent
MANIFEST_SCHEMA = "rebar-v9-prospective-semantic-performance-holdout-v1"
SUMMARY_SCHEMA = "rebar-v9-real-public-operation-summary-v1"
MEMORY_ROW_SCHEMA = "rebar-v9-independent-memory-row-v1"
FREEZE_SCHEMA = "rebar-v9-current-native-candidate-freeze-v1"
CHART_SELF_TEST_SCHEMA = "rebar-v9-performance-charts-synthetic-self-test-v1"

APIS = (
    "compile",
    "escape",
    "search",
    "match",
    "fullmatch",
    "findall",
    "finditer",
    "split",
    "sub",
    "subn",
    "match-surface",
    "scanner",
)
WORKLOADS = (
    "literal-and-long-prefix",
    "character-class-and-unicode",
    "anchors-boundaries-and-windows",
    "greedy-lazy-atomic-and-possessive",
    "alternation-groups-and-backreferences",
    "lookaround-and-zero-width",
    "replacement-split-and-result-density",
    "logs-paths-urls-identifiers-and-noise",
)
MODULES = (
    "re",
    "candidates.vm_candidate",
    "candidates.rust_candidate",
    "candidates.zig_candidate",
)
FAMILY_BY_MODULE = {
    "candidates.vm_candidate": "vm",
    "candidates.rust_candidate": "rust",
    "candidates.zig_candidate": "zig",
}
ARTIFACT_ROLES = {
    "candidates.vm_candidate": frozenset({"public-python", "native-bridge"}),
    "candidates.rust_candidate": frozenset(
        {"public-python", "native-source", "bridge-source", "native-bridge", "native-engine"}
    ),
    "candidates.zig_candidate": frozenset(
        {"public-python", "native-bridge", "native-engine"}
    ),
}
API_LABELS = {
    "compile": "Prepare a pattern",
    "escape": "Escape special characters",
    "search": "Search for a match",
    "match": "Match at the beginning",
    "fullmatch": "Match the entire input",
    "findall": "Find every match",
    "finditer": "Stream each match",
    "split": "Split around matches",
    "sub": "Replace matches",
    "subn": "Replace and count matches",
    "match-surface": "Read the match details",
    "scanner": "Scan repeated matches",
}

CASE_COUNT = 24_576
CASES_PER_CELL = 256
CASES_PER_API = 2_048
CELL_COUNT = 96
ENGINE_COUNT = 4
CANDIDATE_COUNT = 3
PAIRED_ROUNDS = 31
OPERATIONS_PER_SAMPLE = 16
WARMUPS = 4
BOOTSTRAP_DRAWS = 9_999
BOOTSTRAP_SEED = 20260723999
MINIMUM_WINS = 14_746
REGRESSION_THRESHOLD = 5.0 / 6.0
MEMORY_CASES = 1_536
MEMORY_CASES_PER_CELL = 16
MEMORY_CASES_PER_API = 128
RAW_ROWS = CASE_COUNT * PAIRED_ROUNDS * ENGINE_COUNT
CORRECTNESS_SNAPSHOTS = RAW_ROWS * 3
MEMORY_ROWS = MEMORY_CASES * ENGINE_COUNT
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"

MEMORY_FIELDS = (
    "python_current_bytes",
    "python_peak_bytes",
    "process_current_before_bytes",
    "process_current_after_bytes",
    "process_peak_bytes",
)

BLUE = "#175cd3"
GREEN = "#067647"
RED = "#b42318"
AMBER = "#a15c00"
GREY = "#475467"
PALE = "#f2f4f7"


@dataclass(frozen=True)
class ManifestLayout:
    digest: str
    binding: str
    opening_commitment: str
    descriptors: frozenset[tuple[str, str]]


@dataclass(frozen=True)
class CandidateResult:
    module: str
    label: str
    ranking: Mapping[str, Any]
    rows: tuple[Mapping[str, Any], ...]
    groups: Mapping[tuple[str, str], tuple[Mapping[str, Any], ...]]
    wins: int
    losses: int
    uncertain: int
    regressions: int


@dataclass(frozen=True)
class MemoryResult:
    rows: tuple[Mapping[str, Any], ...]
    groups: Mapping[tuple[str, str], tuple[Mapping[str, Any], ...]]
    baseline_by_case: Mapping[str, Mapping[str, Any]]


@dataclass(frozen=True)
class FinalResult:
    manifest: ManifestLayout
    modules: tuple[str, ...]
    candidates: tuple[CandidateResult, ...]
    memory: MemoryResult


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def valid_digest(value: Any, label: str) -> str:
    require(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        f"{label} is not a complete lowercase SHA-256 fingerprint",
    )
    return value


def integer(value: Any, label: str, expected: int | None = None) -> int:
    require(isinstance(value, int) and not isinstance(value, bool), f"{label} is not an integer")
    require(value >= 0, f"{label} is negative")
    if expected is not None:
        require(value == expected, f"{label} must be exactly {expected:,}")
    return value


def finite(value: Any, label: str, *, allow_zero: bool = False) -> float:
    require(
        isinstance(value, (int, float, Decimal)) and not isinstance(value, bool),
        f"{label} is not a number",
    )
    result = float(value)
    require(math.isfinite(result), f"{label} is not finite")
    require(result >= 0 if allow_zero else result > 0, f"{label} is out of range")
    return result


def exact(value: Any) -> str:
    number = finite(value, "displayed ratio", allow_zero=True)
    rendered = format(Decimal(str(number)), "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return f"{rendered}×"


def display_bytes(value: float) -> str:
    finite(value, "displayed memory", allow_zero=True)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:,.0f} {unit}" if unit == "B" else f"{value:,.2f} {unit}"
        value /= 1024
    raise ValueError("memory unit escaped the supported range")


def label_for(module: str) -> str:
    return {"candidates.vm_candidate": "C virtual machine", "candidates.rust_candidate": "Rust", "candidates.zig_candidate": "Zig"}[module]


def validate_manifest(payload: Mapping[str, Any]) -> ManifestLayout:
    require(isinstance(payload, dict), "the v9 public manifest is not a JSON object")
    require(payload.get("schema") == MANIFEST_SCHEMA, "the v9 public-manifest schema is wrong")
    require(
        payload.get("state") == "prospectively-sealed-not-materialized",
        "the prospective v9 manifest state changed",
    )
    reference = payload.get("reference")
    require(
        isinstance(reference, dict)
        and reference.get("implementation") == "CPython"
        and reference.get("version") == "3.14.6"
        and reference.get("unicode_version") == "16.0.0"
        and reference.get("enforced_worker_locale") == "C",
        "the pinned Python, Unicode version, or worker locale changed",
    )
    source = payload.get("source")
    require(
        isinstance(source, dict)
        and source.get("path") == "tools/rust_v9_holdout_protocol.py",
        "the prospective v9 protocol source changed",
    )
    valid_digest(source.get("sha256"), "the frozen v9 public protocol source")
    seal = payload.get("seal")
    require(
        isinstance(seal, dict)
        and seal.get("algorithm") == "sha256"
        and seal.get("opening_bytes") == 32
        and seal.get("opening_mode") == "0600",
        "the prospective v9 blinded commitment changed",
    )
    commitment = valid_digest(seal.get("opening_sha256"), "the public opening commitment")
    layout = payload.get("layout")
    require(isinstance(layout, dict), "the public v9 descriptor layout is missing")
    require(layout.get("apis") == list(APIS), "a frozen public Python operation was omitted or replaced")
    require(layout.get("workloads") == list(WORKLOADS), "a frozen public workload family was omitted or replaced")
    integer(layout.get("cases"), "the public case denominator", CASE_COUNT)
    integer(layout.get("cases_per_api"), "the public operation denominator", CASES_PER_API)
    integer(layout.get("cases_per_cell"), "the public workload denominator", CASES_PER_CELL)
    applicability = layout.get("applicability")
    require(
        isinstance(applicability, dict) and set(applicability) == set(APIS),
        "the prospective applicability of a public operation changed",
    )
    trials = payload.get("trials")
    require(isinstance(trials, dict), "the prospective paired-trial protocol is missing")
    integer(trials.get("minimum_candidates"), "the independent candidate minimum", CANDIDATE_COUNT)
    require(
        trials.get("required_independent_native_families") == ["vm", "rust", "zig"],
        "the three independently built candidate families changed",
    )
    integer(trials.get("paired_rounds"), "the paired-trial denominator", PAIRED_ROUNDS)
    integer(trials.get("warmups"), "the independent warmup denominator", WARMUPS)
    integer(trials.get("operations_per_sample"), "the timed public-operation denominator", OPERATIONS_PER_SAMPLE)
    integer(trials.get("four_engine_timed_rows"), "the four-engine timing-row denominator", RAW_ROWS)
    integer(
        trials.get("four_engine_correctness_snapshots"),
        "the four-engine correctness-snapshot denominator",
        CORRECTNESS_SNAPSHOTS,
    )
    statistics_section = payload.get("statistics")
    require(isinstance(statistics_section, dict), "the prospective confidence protocol is missing")
    require(
        math.isclose(finite(statistics_section.get("confidence"), "confidence level"), 0.95, rel_tol=0, abs_tol=1e-15),
        "the confidence level is not the frozen 95 percent",
    )
    require(
        statistics_section.get("case_method") == "paired-log-student-t-df30"
        and statistics_section.get("overall_method")
        == "stratified-paired-whole-case-cluster-percentile-bootstrap",
        "the predeclared paired confidence method changed",
    )
    integer(
        statistics_section.get("minimum_significant_wins"),
        "the confidence-qualified win target",
        MINIMUM_WINS,
    )
    integer(
        statistics_section.get("overall_bootstrap_draws"),
        "the prospective bootstrap denominator",
        BOOTSTRAP_DRAWS,
    )
    integer(statistics_section.get("bootstrap_seed"), "the frozen bootstrap seed", BOOTSTRAP_SEED)
    require(
        math.isclose(finite(statistics_section.get("overall_lower_bound"), "the required speed"), 1.5, rel_tol=0, abs_tol=1e-15)
        and statistics_section.get("runtime_regression") == "candidate_time > 1.2 * baseline_time",
        "a success or strict runtime-slowdown threshold changed",
    )
    correctness = payload.get("correctness")
    require(isinstance(correctness, dict), "the frozen correctness requirements are missing")
    for key, count in (
        ("snapshots_per_timed_row", 3),
        ("mismatches_allowed", 0),
        ("timeouts_allowed", 0),
        ("crashes_allowed", 0),
        ("edge_checks", 223_198),
        ("edge_categories", 49),
        ("grammar_checks", 20_480),
        ("object_checks", 14_783),
        ("unicode_checks", 4_494_555),
        ("observable_checks", 479),
        ("native_binder_checks", 34),
        ("deep_contract_checks", 393),
        ("minimum_current_campaign_stages", 22),
    ):
        integer(correctness.get(key), f"the frozen {key}", count)
    require(correctness.get("goal_sha256") == GOAL_SHA256, "the immutable experiment goal changed")
    memory = payload.get("memory")
    require(isinstance(memory, dict), "the separate memory protocol is missing")
    integer(memory.get("cases"), "the separate memory-case denominator", MEMORY_CASES)
    integer(memory.get("cases_per_cell"), "the separate memory-cell denominator", MEMORY_CASES_PER_CELL)
    require(
        memory.get("python_peak") == "tracemalloc-python-allocations-only"
        and memory.get("process_peak") == "whole-process-peak-resident-bytes",
        "Python-traced allocations and whole-process RSS were confused",
    )
    history = payload.get("history")
    require(
        isinstance(history, dict)
        and history.get("v9_results") == "NOT MEASURED"
        and history.get("combined_results") == "NOT MEASURED",
        "the prospective public manifest claims an unmeasured result",
    )
    supplied_binding = valid_digest(payload.get("binding_sha256"), "the frozen public manifest binding")
    expected_binding = canonical_digest(
        {key: value for key, value in payload.items() if key != "binding_sha256"}
    )
    require(supplied_binding == expected_binding, "the complete public manifest commitment was tampered with")
    descriptors = frozenset((api, workload) for api in APIS for workload in WORKLOADS)
    require(len(descriptors) == CELL_COUNT, "the public 96-descriptor grid changed")
    return ManifestLayout(canonical_digest(payload), supplied_binding, commitment, descriptors)


def validate_freeze(
    payload: Mapping[str, Any],
    manifest: ManifestLayout,
    modules: tuple[str, ...],
) -> None:
    audit = payload.get("from_scratch_audit")
    require(isinstance(audit, dict), "the complete from-scratch audit is missing")
    audit_digest = valid_digest(audit.get("sha256"), "the from-scratch native-audit fingerprint")
    require(
        integer(audit.get("owned_native_artifacts"), "the actual independently owned native artifacts", 5) == 5
        and integer(audit.get("distinct_pipelines"), "the actual independent semantic pipelines") >= 3,
        "the final comparison is not built from three independent native pipelines",
    )
    wrapper = payload.get("candidate_freeze")
    require(isinstance(wrapper, dict), "the committed candidate freeze is missing")
    valid_digest(wrapper.get("sha256"), "the committed candidate-freeze fingerprint")
    require(
        isinstance(wrapper.get("path"), str) and bool(wrapper["path"]),
        "the committed candidate freeze has no provenance path",
    )
    freeze = wrapper.get("document")
    require(isinstance(freeze, dict), "the immutable candidate-freeze document is missing")
    require(
        freeze.get("schema") == FREEZE_SCHEMA
        and freeze.get("protocol_binding_sha256") == manifest.binding
        and freeze.get("baseline") == "re"
        and freeze.get("from_scratch_audit_sha256") == audit_digest
        and freeze.get("opening_read") is False
        and freeze.get("hidden_cases_generated") == 0
        and freeze.get("performance_measured") is False,
        "the candidate freeze is stale, unqualified, or not prospectively blind",
    )
    stopping = freeze.get("stopping_commit")
    require(
        isinstance(stopping, str)
        and len(stopping) in {40, 64}
        and all(character in "0123456789abcdef" for character in stopping),
        "the immutable candidate stopping point is missing",
    )
    entries = freeze.get("candidates")
    require(
        isinstance(entries, list) and len(entries) == CANDIDATE_COUNT,
        "the freeze does not contain exactly three independent replacements",
    )
    selected: set[str] = set()
    for entry in entries:
        require(isinstance(entry, dict), "a frozen candidate is not an object")
        module = entry.get("module")
        require(
            isinstance(module, str) and module in modules[1:] and module not in selected,
            "the freeze omits, repeats, or substitutes a candidate",
        )
        for key in ("edge_sha256", "campaign_sha256", "deep_contract_sha256"):
            valid_digest(entry.get(key), f"the frozen {module} {key}")
        artifacts = entry.get("artifacts")
        require(
            isinstance(artifacts, dict) and set(artifacts) == ARTIFACT_ROLES[module],
            f"the frozen {module} owns missing, foreign, or duplicate native artifacts",
        )
        for role, record in artifacts.items():
            require(isinstance(record, dict), f"the frozen {module} {role} is invalid")
            path = record.get("path")
            require(isinstance(path, str) and bool(path), f"the frozen {module} {role} has no path")
            valid_digest(record.get("sha256"), f"the frozen {module} {role} fingerprint")
            if role == "public-python":
                require(
                    Path(path).name == f"{module.rsplit('.', 1)[-1]}.py",
                    f"the frozen {module} public source belongs to another candidate",
                )
        selected.add(module)
    require(selected == set(modules[1:]), "a selected candidate was not prospectively frozen")


def geometric(rows: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]]) -> float:
    require(bool(rows), "the complete equally weighted result group is missing")
    return math.exp(
        math.fsum(math.log(finite(row.get("speedup"), "paired case speed")) for row in rows)
        / len(rows)
    )


def validate_case(
    row: Any,
    module: str,
    manifest: ManifestLayout,
    identifiers: set[str],
) -> tuple[str, tuple[str, str]]:
    require(isinstance(row, dict), f"{module} has an invalid case result")
    identifier = row.get("case")
    require(
        isinstance(identifier, str) and bool(identifier) and identifier.strip() == identifier,
        f"{module} has an invalid measured case identifier",
    )
    require(identifier not in identifiers, f"{module} repeated a measured case")
    key = (row.get("api"), row.get("workload"))
    require(key in manifest.descriptors, f"{module} changed a frozen public workload")
    integer(row.get("paired_rounds"), f"{module} case paired rounds", PAIRED_ROUNDS)
    integer(
        row.get("operations_per_sample"),
        f"{module} case public operations",
        OPERATIONS_PER_SAMPLE,
    )
    speed = finite(row.get("speedup"), f"{module} case speed")
    low = finite(row.get("confidence_low"), f"{module} case 95% lower bound")
    high = finite(row.get("confidence_high"), f"{module} case 95% upper bound")
    require(low <= speed <= high, f"{module} case confidence interval excludes its speed")
    require(
        isinstance(row.get("statistically_faster"), bool)
        and row["statistically_faster"] is (low > 1.0),
        f"{module} changed the strict confidence-qualified win rule",
    )
    require(
        isinstance(row.get("runtime_regression_over_20_percent"), bool)
        and row["runtime_regression_over_20_percent"] is (speed < REGRESSION_THRESHOLD),
        f"{module} hid or invented a strict more-than-20-percent slowdown",
    )
    identifiers.add(identifier)
    return identifier, key


def validate_results(
    payload: Mapping[str, Any],
    manifest: ManifestLayout,
) -> tuple[tuple[str, ...], tuple[CandidateResult, ...], Mapping[str, tuple[str, str]]]:
    require(isinstance(payload, dict), "the v9 final summary is not a JSON object")
    require(payload.get("schema") == SUMMARY_SCHEMA, "the actual v9 final-summary schema is wrong")
    require(payload.get("python") == "3.14.6", "the final Python baseline is not CPython 3.14.6")
    require(payload.get("locale") == "C", "the final engine locale was changed")
    require(payload.get("failed") == 0, "the final measurement has an unexplained failure")
    require(
        payload.get("original_holdout_accessed") is False
        and payload.get("v8_holdout_accessed") is False
        and payload.get("original_v7_cases") == 10_312
        and payload.get("combined_results") == "NOT MEASURED",
        "the final v9 summary accesses or invents a previous holdout result",
    )
    require(
        payload.get("manifest_sha256") == manifest.digest
        and payload.get("protocol_binding_sha256") == manifest.binding
        and payload.get("opening_sha256") == manifest.opening_commitment,
        "the final results do not match the exact frozen public commitment",
    )
    supplied_modules = payload.get("modules")
    require(
        isinstance(supplied_modules, list)
        and len(supplied_modules) == ENGINE_COUNT
        and supplied_modules[0] == "re"
        and len(set(supplied_modules)) == ENGINE_COUNT
        and set(supplied_modules) == set(MODULES),
        "the measurement did not include Python and the exact three independent engines",
    )
    modules = tuple(supplied_modules)
    validate_freeze(payload, manifest, modules)
    integer(payload.get("cases"), "the complete final case denominator", CASE_COUNT)
    integer(payload.get("paired_rounds"), "the complete paired-trial denominator", PAIRED_ROUNDS)
    integer(
        payload.get("operations_per_sample"),
        "the complete public-operation denominator",
        OPERATIONS_PER_SAMPLE,
    )
    integer(payload.get("warmups"), "the complete warmup denominator", WARMUPS)
    integer(payload.get("overall_bootstrap_draws"), "the complete reported bootstrap denominator", BOOTSTRAP_DRAWS)
    integer(
        payload.get("correctness_snapshots"),
        "the complete timing correctness-snapshot denominator",
        CORRECTNESS_SNAPSHOTS,
    )
    raw = payload.get("raw")
    require(isinstance(raw, dict), "the actual paired timing provenance is missing")
    require(isinstance(raw.get("path"), str) and bool(raw["path"]), "the paired timing provenance path is missing")
    integer(raw.get("rows"), "the complete four-engine paired timing rows", RAW_ROWS)
    integer(raw.get("operations_per_row"), "the actual public operations per timing row", OPERATIONS_PER_SAMPLE)
    valid_digest(raw.get("uncompressed_rows_sha256"), "the actual paired timing fingerprint")
    startup = payload.get("cold_process_startup")
    require(isinstance(startup, list) and len(startup) == ENGINE_COUNT, "a genuine isolated startup was omitted")
    started: set[str] = set()
    for record in startup:
        require(isinstance(record, dict), "an isolated process startup is invalid")
        module = record.get("module")
        require(module in modules and module not in started, "an isolated startup engine was omitted or duplicated")
        integer(record.get("elapsed_ns"), "isolated process startup time")
        require(
            record.get("included_in_main_speedup") is False
            and record.get("definition") == "isolated-process-start-import-and-current-native-proof",
            "isolated process startup was mixed into the public-call timing",
        )
        started.add(module)
    blocks = payload.get("results")
    require(isinstance(blocks, list) and len(blocks) == CANDIDATE_COUNT, "a complete candidate ranking was omitted")
    block_modules: set[str] = set()
    reference_layout: dict[str, tuple[str, str]] | None = None
    results: list[CandidateResult] = []
    for block in blocks:
        require(isinstance(block, dict), "a candidate result is not an object")
        module = block.get("module")
        require(
            isinstance(module, str) and module in modules[1:] and module not in block_modules,
            "a measured candidate ranking was replaced or duplicated",
        )
        integer(block.get("cases"), f"{module} overall case denominator", CASE_COUNT)
        integer(block.get("bootstrap_draws"), f"{module} reported bootstrap denominator", BOOTSTRAP_DRAWS)
        integer(
            block.get("minimum_statistically_faster_cases"),
            f"{module} significant-win target",
            MINIMUM_WINS,
        )
        supplied = block.get("case_results")
        require(isinstance(supplied, list) and len(supplied) == CASE_COUNT, f"{module} omitted a final measured case")
        identifiers: set[str] = set()
        case_layout: dict[str, tuple[str, str]] = {}
        mutable_groups: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
        wins = 0
        losses = 0
        regression_rows: list[Mapping[str, Any]] = []
        for row in supplied:
            identifier, key = validate_case(row, module, manifest, identifiers)
            case_layout[identifier] = key
            mutable_groups[key].append(row)
            wins += int(row["confidence_low"] > 1.0)
            losses += int(row["confidence_high"] < 1.0)
            if row["runtime_regression_over_20_percent"]:
                regression_rows.append(row)
        require(set(mutable_groups) == manifest.descriptors, f"{module} omitted a public workload")
        require(
            all(len(rows) == CASES_PER_CELL for rows in mutable_groups.values()),
            f"{module} changed a 256-case public workload denominator",
        )
        if reference_layout is None:
            reference_layout = case_layout
        else:
            require(case_layout == reference_layout, f"{module} did not measure the exact same final cases")
        point = finite(block.get("geomean_speedup"), f"{module} overall speed")
        actual_point = geometric(tuple(supplied))
        require(
            math.isclose(point, actual_point, rel_tol=1e-11, abs_tol=1e-12),
            f"{module} reweighted or omitted a case from the overall speed",
        )
        low = finite(block.get("confidence_low"), f"{module} reported overall 95% lower bound")
        high = finite(block.get("confidence_high"), f"{module} reported overall 95% upper bound")
        require(low <= point <= high, f"{module} reported an inverted overall confidence interval")
        integer(block.get("statistically_faster_cases"), f"{module} confidence-qualified wins", wins)
        integer(block.get("regression_count"), f"{module} complete large-slowdown count", len(regression_rows))
        saved_regressions = block.get("regressions")
        require(
            isinstance(saved_regressions, list) and saved_regressions == regression_rows,
            f"{module} concealed, repeated, substituted, or reordered a large slowdown",
        )
        speed_passes = low >= 1.5
        cases_pass = wins >= MINIMUM_WINS
        require(
            block.get("meets_speed_requirement") is speed_passes
            and block.get("meets_case_requirement") is cases_pass
            and block.get("success") is (speed_passes and cases_pass),
            f"{module} changed the frozen success requirements",
        )
        groups = {key: tuple(value) for key, value in mutable_groups.items()}
        results.append(
            CandidateResult(
                module,
                label_for(module),
                block,
                tuple(supplied),
                groups,
                wins,
                losses,
                CASE_COUNT - wins - losses,
                len(regression_rows),
            )
        )
        block_modules.add(module)
    require(block_modules == set(modules[1:]), "a frozen candidate has no complete final results")
    assert reference_layout is not None
    results.sort(key=lambda item: (-float(item.ranking["geomean_speedup"]), item.label, item.module))
    return modules, tuple(results), reference_layout


def validate_memory(
    compressed: bytes,
    payload: Mapping[str, Any],
    manifest: ManifestLayout,
    modules: tuple[str, ...],
    case_layout: Mapping[str, tuple[str, str]],
) -> MemoryResult:
    section = payload.get("memory")
    require(isinstance(section, dict), "the separately measured memory provenance is missing")
    require(isinstance(section.get("path"), str) and bool(section["path"]), "the separate memory evidence path is missing")
    integer(section.get("rows"), "the complete separate-memory row denominator", MEMORY_ROWS)
    integer(section.get("cases_per_module"), "the separate memory cases per engine", MEMORY_CASES)
    require(
        section.get("python_peak_definition") == "tracemalloc-python-allocations-only"
        and section.get("process_peak_definition") == "whole-process-peak-rss-bytes",
        "the final result confuses Python-traced and whole-process memory",
    )
    expected_digest = valid_digest(
        section.get("uncompressed_rows_sha256"), "the independent memory evidence fingerprint"
    )
    try:
        uncompressed = gzip.decompress(compressed)
    except (OSError, EOFError) as error:
        raise ValueError("the explicitly supplied separate memory evidence is not valid gzip") from error
    require(
        hashlib.sha256(uncompressed).hexdigest() == expected_digest,
        "the separate memory evidence does not match the frozen final summary",
    )
    segments = uncompressed.splitlines(keepends=True)
    require(len(segments) == MEMORY_ROWS, "the compressed memory evidence omits or duplicates a row")
    rows: list[Mapping[str, Any]] = []
    by_engine: dict[str, set[str]] = {module: set() for module in modules}
    cell_counts: dict[tuple[str, str, str], int] = defaultdict(int)
    groups: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    baseline: dict[str, Mapping[str, Any]] = {}
    for number, segment in enumerate(segments):
        require(segment.endswith(b"\n"), "a separate-memory evidence line has no canonical terminator")
        try:
            row = json.loads(segment)
        except (UnicodeError, json.JSONDecodeError) as error:
            raise ValueError(f"separate-memory row {number} is not canonical JSON") from error
        require(
            isinstance(row, dict) and canonical_bytes(row) + b"\n" == segment,
            f"separate-memory row {number} was rewritten or is not canonical",
        )
        require(row.get("schema") == MEMORY_ROW_SCHEMA, "a separate-memory row uses the wrong public schema")
        module = row.get("module")
        require(module in by_engine, "the memory evidence contains an unmeasured engine")
        identifier = row.get("case")
        require(
            isinstance(identifier, str)
            and identifier in case_layout
            and identifier not in by_engine[module],
            "the memory evidence omits, repeats, or invents a measured case",
        )
        key = (row.get("api"), row.get("workload"))
        require(
            key in manifest.descriptors and case_layout[identifier] == key,
            "the memory evidence changes the frozen case descriptor",
        )
        require(
            row.get("locale") == "C"
            and row.get("correctness") is True
            and row.get("instrumentation_worker") is True
            and row.get("python_memory_is_native_memory") is False,
            "memory was not correctly measured in a separate, exact, isolated worker",
        )
        for field in MEMORY_FIELDS:
            integer(row.get(field), f"separate-memory field {field}")
        by_engine[module].add(identifier)
        cell_counts[(module, key[0], key[1])] += 1
        groups[(module, key[0])].append(row)
        if module == "re":
            baseline[identifier] = row
        rows.append(row)
    reference_ids = by_engine["re"]
    require(len(reference_ids) == MEMORY_CASES, "Python does not cover all separate-memory cases")
    for module in modules:
        require(by_engine[module] == reference_ids, f"{module} changed a paired memory-case identity")
        require(
            all(
                cell_counts[(module, api, workload)] == MEMORY_CASES_PER_CELL
                for api in APIS
                for workload in WORKLOADS
            ),
            f"{module} changed a 16-case separate-memory workload denominator",
        )
        require(
            all(len(groups[(module, api)]) == MEMORY_CASES_PER_API for api in APIS),
            f"{module} changed a 128-case operation memory denominator",
        )
    require(len(rows) == MEMORY_ROWS, "the separate-memory denominator changed")
    return MemoryResult(tuple(rows), {key: tuple(value) for key, value in groups.items()}, baseline)


def validate_final(
    manifest_payload: Mapping[str, Any],
    summary_payload: Mapping[str, Any],
    compressed_memory: bytes,
) -> FinalResult:
    manifest = validate_manifest(manifest_payload)
    modules, candidates, case_layout = validate_results(summary_payload, manifest)
    memory = validate_memory(compressed_memory, summary_payload, manifest, modules, case_layout)
    return FinalResult(manifest, modules, candidates, memory)


def svg_open(width: int, height: int, title: str, subtitle: str, description: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="chart-title chart-description">',
        f'<title id="chart-title">{escape(title)}</title>',
        f'<desc id="chart-description">{escape(description)}</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#101828}.title{font-size:27px;font-weight:750}.sub{font-size:14px;fill:#475467}.head{font-size:15px;font-weight:720}.label{font-size:12.5px}.small{font-size:11.5px;fill:#475467}.value{font-size:12px;font-weight:680}.tick{font-size:11px;fill:#475467}.panel{fill:#f9fafb;stroke:#eaecf0;stroke-width:1}.grid{stroke:#e4e7ec;stroke-width:1}.baseline{stroke:#344054;stroke-width:2;stroke-dasharray:6 4}.foot{font-size:11.5px;fill:#475467}</style>',
        f'<text x="26" y="42" class="title">{escape(title)}</text>',
        f'<text x="26" y="66" class="sub">{escape(subtitle)}</text>',
    ]


def svg_text(
    body: list[str],
    x: float,
    y: float,
    class_name: str,
    value: str,
    *,
    anchor: str | None = None,
) -> None:
    alignment = f' text-anchor="{anchor}"' if anchor is not None else ""
    body.append(
        f'<text x="{x:.2f}" y="{y:.2f}" class="{class_name}"{alignment}>{escape(value)}</text>'
    )


def nice_axis(maximum: float) -> tuple[float, float]:
    maximum = max(1.2, finite(maximum, "chart axis maximum") * 1.08)
    magnitude = 10 ** math.floor(math.log10(maximum / 6))
    for factor in (1.0, 2.0, 2.5, 5.0, 10.0):
        step = factor * magnitude
        if math.ceil(maximum / step) <= 8:
            return math.ceil(maximum / step) * step, step
    raise ValueError("a readable, complete chart axis cannot be constructed")


def axis_x(value: float, left: int, right: int, upper: float) -> float:
    require(0 <= value <= upper * (1 + 1e-11), "a measured value escapes the complete chart axis")
    return left + (right - left) * value / upper


def draw_grid(
    body: list[str],
    *,
    left: int,
    right: int,
    top: int,
    bottom: int,
    upper: float,
    step: float,
    baseline: str = "1× = Python",
) -> None:
    for index in range(int(round(upper / step)) + 1):
        value = index * step
        x = axis_x(value, left, right, upper)
        body.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" class="grid"/>')
        svg_text(body, x, top - 8, "tick", "0" if value == 0 else f"{value:.5g}×", anchor="middle")
    position = axis_x(1.0, left, right, upper)
    body.append(f'<line x1="{position:.2f}" y1="{top}" x2="{position:.2f}" y2="{bottom}" class="baseline"/>')
    svg_text(body, position, bottom + 16, "tick", baseline, anchor="middle")


def whisker(
    body: list[str],
    *,
    left_x: float,
    right_x: float,
    point_x: float,
    y: float,
    color: str,
    description: str,
) -> None:
    body.append(
        f'<g><title>{escape(description)}</title>'
        f'<line x1="{left_x:.2f}" y1="{y:.2f}" x2="{right_x:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>'
        f'<line x1="{left_x:.2f}" y1="{y - 6:.2f}" x2="{left_x:.2f}" y2="{y + 6:.2f}" stroke="{color}" stroke-width="2"/>'
        f'<line x1="{right_x:.2f}" y1="{y - 6:.2f}" x2="{right_x:.2f}" y2="{y + 6:.2f}" stroke="{color}" stroke-width="2"/>'
        f'<circle cx="{point_x:.2f}" cy="{y:.2f}" r="5.5" fill="{color}" stroke="#ffffff" stroke-width="1.5"/></g>'
    )


def close_svg(body: list[str]) -> str:
    return "\n".join((*body, "</svg>", ""))


def overall_chart(result: FinalResult) -> str:
    width, height = 1780, 494
    left, right = 340, 985
    upper, step = nice_axis(
        max(1.0, *(float(item.ranking["confidence_high"]) for item in result.candidates))
    )
    body = svg_open(
        width,
        height,
        "How much faster is each replacement than Python?",
        "24,576 unseen cases per engine · 31 paired rounds · 9,999 reported bootstrap draws",
        "Python is exactly 1×. Rust, Zig, and the independently built C virtual machine all use the same 24,576 cases. Whiskers are the 95% intervals reported by the frozen final protocol; this chart does not independently rerun the bootstrap.",
    )
    draw_grid(body, left=left, right=right, top=112, bottom=height - 83, upper=upper, step=step)
    y = 151
    python_x = axis_x(1.0, left, right, upper)
    svg_text(body, 29, y + 5, "head", "Python re (baseline)")
    body.append(f'<rect x="{left}" y="{y - 10}" width="{python_x - left:.2f}" height="20" rx="4" fill="{GREY}"/>')
    svg_text(body, 1012, y + 5, "value", "Exactly 1× · all 24,576 cases")
    for index, item in enumerate(result.candidates):
        y = 222 + index * 72
        point = float(item.ranking["geomean_speedup"])
        low = float(item.ranking["confidence_low"])
        high = float(item.ranking["confidence_high"])
        color = GREEN if low > 1.0 else RED if high < 1.0 else AMBER
        x = axis_x(point, left, right, upper)
        svg_text(body, 29, y + 5, "head", item.label)
        body.append(f'<rect x="{left}" y="{y - 10}" width="{x - left:.2f}" height="20" rx="4" fill="{color}" fill-opacity=".2"/>')
        whisker(
            body,
            left_x=axis_x(low, left, right, upper),
            right_x=axis_x(high, left, right, upper),
            point_x=x,
            y=y,
            color=color,
            description=f"{item.label}: {exact(point)}; frozen-protocol-reported 95% interval {exact(low)} to {exact(high)}",
        )
        svg_text(body, 1012, y - 9, "value", f"{exact(point)} · reported 95%: {exact(low)} to {exact(high)}")
        svg_text(
            body,
            1012,
            y + 11,
            "small",
            f"{item.wins:,}/{CASE_COUNT:,} clearly faster · {item.regressions:,}/{CASE_COUNT:,} more than 20% slower",
        )
        svg_text(
            body,
            1012,
            y + 28,
            "small",
            "Meets both frozen success requirements" if item.ranking["success"] else "Does not meet both frozen success requirements",
        )
    svg_text(body, 27, height - 35, "foot", "Success requires a reported 95% lower bound of at least 1.5× and at least 14,746 clearly faster cases.")
    svg_text(body, 27, height - 15, "foot", "Intervals are reported by the frozen 9,999-draw paired bootstrap; this chart does not independently recompute that bootstrap.")
    return close_svg(body)


def outcomes_chart(result: FinalResult) -> str:
    width, left, right = 1720, 365, 1080
    panel_height = 160
    height = 138 + len(result.candidates) * panel_height + 38
    body = svg_open(
        width,
        height,
        "How often does each replacement win or lose?",
        "All 24,576 cases · proven wins, uncertain cases, proven losses, and every large slowdown",
        "Green, gray, and red always add to the same 24,576 cases. Large slowdowns are independently counted using the exact strict greater-than-20% runtime rule.",
    )
    scale = (right - left) / CASE_COUNT
    for index, item in enumerate(result.candidates):
        top = 111 + index * panel_height
        body.append(f'<rect x="18" y="{top - 10}" width="{width - 36}" height="{panel_height - 9}" rx="8" class="panel"/>')
        svg_text(body, 30, top + 13, "head", item.label)
        cursor = float(left)
        for count, color, meaning in (
            (item.wins, GREEN, "clearly faster"),
            (item.uncertain, GREY, "no proven difference"),
            (item.losses, RED, "clearly slower"),
        ):
            length = count * scale
            if count:
                body.append(f'<g><title>{escape(f"{count:,}/{CASE_COUNT:,}: {meaning}")}</title><rect x="{cursor:.2f}" y="{top + 31}" width="{length:.2f}" height="21" fill="{color}"/></g>')
            cursor += length
        svg_text(body, right + 13, top + 47, "value", f"{CASE_COUNT:,}/{CASE_COUNT:,}")
        svg_text(body, left, top + 70, "small", f"Faster {item.wins:,} · uncertain {item.uncertain:,} · slower {item.losses:,} · denominator {CASE_COUNT:,}")
        threshold = "MEETS" if item.wins >= MINIMUM_WINS else "DOES NOT MEET"
        target_color = GREEN if item.wins >= MINIMUM_WINS else RED
        body.append(f'<text x="{left}" y="{top + 91}" style="font-size:12px;font-weight:700;fill:{target_color}">{escape(f"{threshold} the 14,746-case clearly-faster requirement")}</text>')
        body.append(f'<rect x="{left}" y="{top + 103}" width="{right - left}" height="17" rx="4" fill="#fee4e2"/>')
        if item.regressions:
            body.append(f'<rect x="{left}" y="{top + 103}" width="{item.regressions * scale:.2f}" height="17" rx="4" fill="{RED}"/>')
        svg_text(body, right + 13, top + 116, "value", f"{item.regressions:,}/{CASE_COUNT:,}")
        svg_text(body, left, top + 137, "small", "Separate count: took strictly more than 20% longer than Python.")
    svg_text(body, 26, height - 13, "foot", "A win requires its per-case 95% lower bound to be strictly above 1×; speed exactly 5/6 is not a greater-than-20% slowdown.")
    return close_svg(body)


def api_chart(result: FinalResult) -> str:
    width, left, right = 1810, 335, 1010
    row_height = 37
    panel_height = 76 + len(APIS) * row_height
    height = 130 + len(result.candidates) * panel_height + 44
    values = [1.0]
    for item in result.candidates:
        for api in APIS:
            selected = tuple(row for workload in WORKLOADS for row in item.groups[(api, workload)])
            require(len(selected) == CASES_PER_API, "the API chart changed its full operation denominator")
            values.append(geometric(selected))
    upper, step = nice_axis(max(values))
    body = svg_open(
        width,
        height,
        "Which everyday Python operations are faster?",
        "All 12 operations · 2,048 cases each · all 24,576 cases per replacement",
        "Every candidate and each Python operation is included. Dots are the exact equally weighted operation means. The frozen v9 runner does not report API-level confidence intervals, so no such interval is invented.",
    )
    for candidate_index, item in enumerate(result.candidates):
        top = 111 + candidate_index * panel_height
        body.append(f'<rect x="17" y="{top - 10}" width="{width - 34}" height="{panel_height - 8}" rx="8" class="panel"/>')
        svg_text(body, 29, top + 11, "head", item.label)
        draw_grid(body, left=left, right=right, top=top + 42, bottom=top + 48 + len(APIS) * row_height, upper=upper, step=step)
        for index, api in enumerate(APIS):
            rows = tuple(row for workload in WORKLOADS for row in item.groups[(api, workload)])
            y = top + 67 + index * row_height
            point = geometric(rows)
            wins = sum(row["confidence_low"] > 1.0 for row in rows)
            losses = sum(row["confidence_high"] < 1.0 for row in rows)
            regressions = sum(bool(row["runtime_regression_over_20_percent"]) for row in rows)
            svg_text(body, 29, y + 4, "label", f"{API_LABELS[api]} ({api})")
            body.append(f'<circle cx="{axis_x(point, left, right, upper):.2f}" cy="{y}" r="5" fill="{BLUE}" stroke="#fff" stroke-width="1.5"/>')
            svg_text(body, 1024, y + 4, "value", f"{exact(point)} average · no API confidence interval measured")
            svg_text(body, 1480, y + 4, "small", f"{wins:,} win · {losses:,} lose · {regressions:,} large / {CASES_PER_API:,}")
    svg_text(body, 26, height - 14, "foot", "Every operation contains exactly eight public workloads and 256 cases per workload. Operation-level confidence intervals are NOT MEASURED.")
    return close_svg(body)


def regressions_chart(result: FinalResult) -> str:
    width, left, right = 1830, 470, 1020
    row_height = 31
    panel_height = 66 + CELL_COUNT * row_height
    height = 126 + len(result.candidates) * panel_height + 43
    body = svg_open(
        width,
        height,
        "Every workload where a replacement loses",
        "All 24,576 cases · 96 public workload groups · all 256 cases per group, including zero-loss groups",
        "Every candidate and all 96 frozen Python-operation-by-workload groups are shown. Each row separately reports confidence-proven slower cases and all cases taking strictly more than 20% longer.",
    )
    for candidate_index, item in enumerate(result.candidates):
        top = 108 + candidate_index * panel_height
        body.append(f'<rect x="17" y="{top - 9}" width="{width - 34}" height="{panel_height - 7}" rx="8" class="panel"/>')
        svg_text(body, 29, top + 10, "head", f"{item.label} · {item.losses:,}/{CASE_COUNT:,} proven losses · {item.regressions:,}/{CASE_COUNT:,} large slowdowns")
        seen_losses = 0
        seen_regressions = 0
        index = 0
        for api in APIS:
            for workload in WORKLOADS:
                rows = item.groups[(api, workload)]
                losses = sum(row["confidence_high"] < 1.0 for row in rows)
                regressions = sum(bool(row["runtime_regression_over_20_percent"]) for row in rows)
                seen_losses += losses
                seen_regressions += regressions
                y = top + 33 + index * row_height
                index += 1
                svg_text(body, 27, y + 11, "label", f"{API_LABELS[api]} · {workload}")
                for offset, count, color in ((0, losses, AMBER), (10, regressions, RED)):
                    body.append(f'<rect x="{left}" y="{y + offset}" width="{right - left}" height="8" rx="2" fill="{PALE}"/>')
                    if count:
                        body.append(f'<rect x="{left}" y="{y + offset}" width="{(right - left) * count / CASES_PER_CELL:.2f}" height="8" rx="2" fill="{color}"/>')
                svg_text(body, right + 12, y + 8, "value", f"{losses:,}/{CASES_PER_CELL:,} clearly slower")
                svg_text(body, right + 230, y + 18, "small", f"{regressions:,}/{CASES_PER_CELL:,} over 20% slower")
        require(
            index == CELL_COUNT and seen_losses == item.losses and seen_regressions == item.regressions,
            f"the regression chart omitted an actual {item.module} loss",
        )
    svg_text(body, 26, height - 13, "foot", "Amber means the complete per-case 95% interval is below 1×. Red means Python time / replacement time is strictly below 5/6. No zero-loss group is removed.")
    return close_svg(body)


def memory_ratios(
    memory: MemoryResult,
    module: str,
    api: str,
    field: str,
) -> tuple[float | None, int, int]:
    selected = memory.groups[(module, api)]
    require(len(selected) == MEMORY_CASES_PER_API, "a memory chart omitted a balanced sample")
    ratios: list[float] = []
    zero_baselines = 0
    for row in selected:
        baseline = memory.baseline_by_case[row["case"]]
        reference = integer(baseline.get(field), "Python baseline memory")
        measured = integer(row.get(field), "candidate memory")
        if reference == 0:
            zero_baselines += 1
        else:
            ratios.append(measured / reference)
    return (float(statistics.median(ratios)) if ratios else None, zero_baselines, len(selected))


def memory_chart(result: FinalResult) -> str:
    width, left, right = 1910, 360, 955
    row_height = 32
    section_height = 76 + len(APIS) * row_height
    panel_height = section_height * 2 + 100
    height = 130 + len(result.candidates) * panel_height + 47
    body = svg_open(
        width,
        height,
        "What memory did the four engines actually use?",
        "1,536 separately measured cases per engine · selected from 24,576 cases · 128 balanced cases per operation",
        "Python-traced allocations and isolated whole-process resident memory are different measurements. Candidate-owned native allocator memory was not measured. Baseline-zero memory ratios are marked undefined and never counted as zero or one.",
    )
    for candidate_index, item in enumerate(result.candidates):
        top = 108 + candidate_index * panel_height
        body.append(f'<rect x="17" y="{top - 9}" width="{width - 34}" height="{panel_height - 8}" rx="8" class="panel"/>')
        for section_index, (title, field, detail) in enumerate(
            (
                (
                    "Python-traced temporary allocations",
                    "python_peak_bytes",
                    "Python allocations only; not Rust, Zig, C, or whole-process native memory",
                ),
                (
                    "Whole isolated-process peak resident memory",
                    "process_peak_bytes",
                    "Includes interpreter, native code, shared libraries, and all other process memory",
                ),
            )
        ):
            section_top = top + section_index * section_height
            svg_text(body, 28, section_top + 11, "head", f"{item.label} · {title}")
            ratios = [memory_ratios(result.memory, item.module, api, field) for api in APIS]
            visible = [ratio for ratio, _zero, _total in ratios if ratio is not None]
            upper, step = nice_axis(max([1.0, *visible]))
            draw_grid(body, left=left, right=right, top=section_top + 44, bottom=section_top + 50 + len(APIS) * row_height, upper=upper, step=step, baseline="1× = Python memory")
            for index, (api, (median, zero_baselines, count)) in enumerate(zip(APIS, ratios, strict=True)):
                y = section_top + 67 + index * row_height
                svg_text(body, 27, y + 4, "label", f"{API_LABELS[api]} ({api})")
                if median is not None:
                    color = GREEN if median < 1 else RED if median > 1 else GREY
                    body.append(f'<circle cx="{axis_x(median, left, right, upper):.2f}" cy="{y}" r="4.8" fill="{color}" stroke="#fff" stroke-width="1.2"/>')
                    value = f"{exact(median)} median from {count - zero_baselines:,}/{count:,} defined ratios"
                else:
                    value = "NOT DEFINED: Python baseline is zero for every sample"
                svg_text(body, 970, y + 4, "value", value)
                svg_text(body, 1450, y + 4, "small", f"{zero_baselines:,}/{count:,} zero Python baselines; no invented ratio")
            svg_text(body, 28, section_top + section_height - 8, "small", detail)
        native_top = top + section_height * 2 + 7
        svg_text(body, 28, native_top + 17, "head", f"{item.label} · candidate-native allocator memory")
        svg_text(body, 35, native_top + 41, "value", "NOT MEASURED — whole-process RSS and Python-traced allocations are not native allocator measurements")
        svg_text(body, 35, native_top + 62, "small", "Process-current before and after, process peak, and Python allocation fields were separately verified for every sampled case.")
    svg_text(body, 25, height - 14, "foot", "Lower defined memory ratios are better. Every operation includes all 128 separate samples; zero Python baselines remain in the stated denominator.")
    return close_svg(body)


def rankings_chart(result: FinalResult) -> str:
    width, left, right = 1780, 385, 985
    entries: list[tuple[float, str, CandidateResult | None]] = [(1.0, "Python re (baseline)", None)]
    entries.extend((float(item.ranking["geomean_speedup"]), item.label, item) for item in result.candidates)
    entries.sort(key=lambda entry: (-entry[0], entry[1]))
    height = 204 + 80 * len(entries)
    upper, step = nice_axis(max(1.0, *(float(item.ranking["confidence_high"]) for item in result.candidates)))
    body = svg_open(
        width,
        height,
        "Overall ranking: Python and every replacement",
        "All four engines · all 24,576 equally weighted cases · reported overall 95% confidence intervals",
        "Python, Rust, Zig, and the independent C virtual machine are all ranked. No losing engine, uncertain case, or large slowdown is removed.",
    )
    draw_grid(body, left=left, right=right, top=110, bottom=height - 65, upper=upper, step=step)
    for index, (point, label, item) in enumerate(entries):
        y = 149 + index * 76
        x = axis_x(point, left, right, upper)
        svg_text(body, 27, y + 5, "head", f"{index + 1}. {label}")
        if item is None:
            body.append(f'<rect x="{left}" y="{y - 9}" width="{x - left:.2f}" height="18" rx="4" fill="{GREY}"/>')
            svg_text(body, 1003, y + 5, "value", "Exactly 1× · identical 24,576-case Python baseline")
            continue
        low = float(item.ranking["confidence_low"])
        high = float(item.ranking["confidence_high"])
        color = GREEN if low > 1 else RED if high < 1 else AMBER
        body.append(f'<rect x="{left}" y="{y - 9}" width="{x - left:.2f}" height="18" rx="4" fill="{color}" fill-opacity=".2"/>')
        whisker(body, left_x=axis_x(low, left, right, upper), right_x=axis_x(high, left, right, upper), point_x=x, y=y, color=color, description=f"{label}: {exact(point)}; frozen-protocol-reported 95% interval {exact(low)} to {exact(high)}")
        svg_text(body, 1003, y - 7, "value", f"{exact(point)} · reported 95%: {exact(low)} to {exact(high)}")
        svg_text(body, 1003, y + 13, "small", f"{item.wins:,}/{CASE_COUNT:,} wins · {item.losses:,}/{CASE_COUNT:,} losses · {item.regressions:,}/{CASE_COUNT:,} large slowdowns")
    svg_text(body, 26, height - 17, "foot", "Reported bootstrap intervals are supplied by the frozen protocol and are not independently recomputed by this renderer.")
    return close_svg(body)


def build_charts(result: FinalResult) -> dict[str, str]:
    charts = {
        "overall": overall_chart(result),
        "outcomes": outcomes_chart(result),
        "api": api_chart(result),
        "regressions": regressions_chart(result),
        "memory": memory_chart(result),
        "rankings": rankings_chart(result),
    }
    require(len(charts) == 6, "a complete required final chart is missing")
    for name, content in charts.items():
        require("24,576" in content, f"the {name} chart hides its full final denominator")
        require(
            "<title" in content and "<desc" in content and 'role="img"' in content,
            f"the {name} chart has no accessible text alternative",
        )
        for module in MODULES[1:]:
            require(escape(label_for(module)) in content, f"the {name} chart hides {module}")
        try:
            ElementTree.fromstring(content)
        except ElementTree.ParseError as error:
            raise ValueError(f"the {name} chart is not valid deterministic SVG") from error
    return charts


def synthetic_digest(label: str) -> str:
    return hashlib.sha256(f"v9-chart-synthetic-only:{label}".encode("ascii")).hexdigest()


def synthetic_manifest() -> dict[str, Any]:
    commitment = synthetic_digest("never-a-real-opening")
    applicability = {api: {"synthetic_only": True} for api in APIS}
    document: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "state": "prospectively-sealed-not-materialized",
        "source": {
            "path": "tools/rust_v9_holdout_protocol.py",
            "sha256": synthetic_digest("public-protocol"),
        },
        "reference": {
            "implementation": "CPython",
            "version": "3.14.6",
            "unicode_version": "16.0.0",
            "enforced_worker_locale": "C",
        },
        "seal": {
            "algorithm": "sha256",
            "opening_bytes": 32,
            "opening_mode": "0600",
            "opening_sha256": commitment,
        },
        "layout": {
            "apis": list(APIS),
            "workloads": list(WORKLOADS),
            "cases": CASE_COUNT,
            "cases_per_api": CASES_PER_API,
            "cases_per_cell": CASES_PER_CELL,
            "applicability": applicability,
        },
        "trials": {
            "minimum_candidates": CANDIDATE_COUNT,
            "required_independent_native_families": ["vm", "rust", "zig"],
            "paired_rounds": PAIRED_ROUNDS,
            "warmups": WARMUPS,
            "operations_per_sample": OPERATIONS_PER_SAMPLE,
            "four_engine_timed_rows": RAW_ROWS,
            "four_engine_correctness_snapshots": CORRECTNESS_SNAPSHOTS,
        },
        "statistics": {
            "confidence": 0.95,
            "case_method": "paired-log-student-t-df30",
            "minimum_significant_wins": MINIMUM_WINS,
            "overall_method": "stratified-paired-whole-case-cluster-percentile-bootstrap",
            "overall_bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "overall_lower_bound": 1.5,
            "runtime_regression": "candidate_time > 1.2 * baseline_time",
        },
        "correctness": {
            "snapshots_per_timed_row": 3,
            "mismatches_allowed": 0,
            "timeouts_allowed": 0,
            "crashes_allowed": 0,
            "edge_checks": 223_198,
            "edge_categories": 49,
            "grammar_checks": 20_480,
            "object_checks": 14_783,
            "unicode_checks": 4_494_555,
            "observable_checks": 479,
            "native_binder_checks": 34,
            "deep_contract_checks": 393,
            "minimum_current_campaign_stages": 22,
            "goal_sha256": GOAL_SHA256,
        },
        "memory": {
            "cases": MEMORY_CASES,
            "cases_per_cell": MEMORY_CASES_PER_CELL,
            "python_peak": "tracemalloc-python-allocations-only",
            "process_peak": "whole-process-peak-resident-bytes",
        },
        "history": {"v9_results": "NOT MEASURED", "combined_results": "NOT MEASURED"},
    }
    document["binding_sha256"] = canonical_digest(document)
    return document


def synthetic_artifacts(module: str) -> dict[str, dict[str, str]]:
    name = module.rsplit(".", 1)[-1]
    return {
        role: {
            "path": (
                f"candidates/{name}.py"
                if role == "public-python"
                else f"candidates/synthetic-v9/{name}/{role}"
            ),
            "sha256": synthetic_digest(f"{module}:{role}"),
        }
        for role in sorted(ARTIFACT_ROLES[module])
    }


def synthetic_speed(module_index: int, index: int, api_index: int, workload_index: int) -> tuple[float, float, float]:
    if workload_index == len(WORKLOADS) - 1:
        if module_index == 0:
            return 2.2, 2.0, 2.4
        if module_index == 1:
            return 1.26, 1.11, 1.43
        return 1.08, 1.01, 1.15
    marker = (index + api_index + workload_index) % 16
    if marker == 0:
        return 0.78, 0.70, 0.82
    if marker == 1:
        return REGRESSION_THRESHOLD, 0.80, 0.90
    if marker == 2:
        return 1.0, 0.94, 1.07
    if marker == 3:
        return 1.09, 1.0, 1.18
    if module_index == 0:
        return 2.2, 2.0, 2.4
    if module_index == 1 or marker < 11:
        return 1.26, 1.11, 1.43
    return 0.94, 0.83, 1.05


def synthetic_inputs() -> tuple[dict[str, Any], dict[str, Any], bytes]:
    manifest = synthetic_manifest()
    audit_digest = synthetic_digest("native-from-scratch-audit")
    audit = {
        "path": "candidates/audits/FROM-SCRATCH-AUDIT.json",
        "sha256": audit_digest,
        "owned_native_artifacts": 5,
        "distinct_pipelines": 3,
    }
    freeze_document = {
        "schema": FREEZE_SCHEMA,
        "protocol_binding_sha256": manifest["binding_sha256"],
        "stopping_commit": synthetic_digest("stopping-commit"),
        "baseline": "re",
        "from_scratch_audit_sha256": audit_digest,
        "candidates": [
            {
                "module": module,
                "edge_sha256": synthetic_digest(f"{module}:edge"),
                "campaign_sha256": synthetic_digest(f"{module}:campaign"),
                "deep_contract_sha256": synthetic_digest(f"{module}:deep-contract"),
                "artifacts": synthetic_artifacts(module),
            }
            for module in MODULES[1:]
        ],
        "opening_read": False,
        "hidden_cases_generated": 0,
        "performance_measured": False,
    }
    blocks: list[dict[str, Any]] = []
    for module_index, module in enumerate(MODULES[1:]):
        rows: list[dict[str, Any]] = []
        for api_index, api in enumerate(APIS):
            for workload_index, workload in enumerate(WORKLOADS):
                for case_index in range(CASES_PER_CELL):
                    speed, low, high = synthetic_speed(module_index, case_index, api_index, workload_index)
                    rows.append(
                        {
                            "case": f"synthetic.v9.chart.{api_index:02d}.{workload_index:02d}.{case_index:03d}",
                            "api": api,
                            "workload": workload,
                            "paired_rounds": PAIRED_ROUNDS,
                            "operations_per_sample": OPERATIONS_PER_SAMPLE,
                            "speedup": speed,
                            "confidence_low": low,
                            "confidence_high": high,
                            "statistically_faster": low > 1.0,
                            "runtime_regression_over_20_percent": speed < REGRESSION_THRESHOLD,
                        }
                    )
        point = geometric(rows)
        low, high = point * 0.97, point * 1.03
        regressions = [row for row in rows if row["runtime_regression_over_20_percent"]]
        wins = sum(row["statistically_faster"] for row in rows)
        blocks.append(
            {
                "module": module,
                "cases": CASE_COUNT,
                "geomean_speedup": point,
                "confidence_low": low,
                "confidence_high": high,
                "bootstrap_draws": BOOTSTRAP_DRAWS,
                "statistically_faster_cases": wins,
                "minimum_statistically_faster_cases": MINIMUM_WINS,
                "regression_count": len(regressions),
                "regressions": regressions,
                "case_results": rows,
                "meets_speed_requirement": low >= 1.5,
                "meets_case_requirement": wins >= MINIMUM_WINS,
                "success": low >= 1.5 and wins >= MINIMUM_WINS,
            }
        )
    memory_lines: list[bytes] = []
    for api_index, api in enumerate(APIS):
        for workload_index, workload in enumerate(WORKLOADS):
            for case_index in range(0, CASES_PER_CELL, 16):
                identifier = f"synthetic.v9.chart.{api_index:02d}.{workload_index:02d}.{case_index:03d}"
                for module_index, module in enumerate(MODULES):
                    zero = case_index == 0 and workload_index == 0
                    peak = 0 if zero else 128 + api_index * 9 + case_index + module_index * 7
                    current = 0 if zero else 32 + api_index + module_index
                    row = {
                        "schema": MEMORY_ROW_SCHEMA,
                        "case": identifier,
                        "api": api,
                        "workload": workload,
                        "module": module,
                        "locale": "C",
                        "python_current_bytes": current,
                        "python_peak_bytes": peak,
                        "process_current_before_bytes": 38_000_000 + module_index * 10_000,
                        "process_current_after_bytes": 38_010_000 + module_index * 10_000 + case_index,
                        "process_peak_bytes": 40_000_000 + module_index * 15_000 + case_index,
                        "python_memory_is_native_memory": False,
                        "instrumentation_worker": True,
                        "correctness": True,
                    }
                    memory_lines.append(canonical_bytes(row) + b"\n")
    memory_bytes = b"".join(memory_lines)
    compressed = gzip.compress(memory_bytes, mtime=0)
    summary: dict[str, Any] = {
        "schema": SUMMARY_SCHEMA,
        "protocol_binding_sha256": manifest["binding_sha256"],
        "manifest_sha256": canonical_digest(manifest),
        "candidate_freeze": {
            "document": freeze_document,
            "path": "performance/v9/evidence/synthetic-v9-freeze.json",
            "sha256": synthetic_digest("freeze-file"),
        },
        "from_scratch_audit": audit,
        "python": "3.14.6",
        "locale": "C",
        "modules": list(MODULES),
        "cases": CASE_COUNT,
        "paired_rounds": PAIRED_ROUNDS,
        "operations_per_sample": OPERATIONS_PER_SAMPLE,
        "warmups": WARMUPS,
        "overall_bootstrap_draws": BOOTSTRAP_DRAWS,
        "correctness_snapshots": CORRECTNESS_SNAPSHOTS,
        "cold_process_startup": [
            {
                "module": module,
                "elapsed_ns": 1_000 + index,
                "included_in_main_speedup": False,
                "definition": "isolated-process-start-import-and-current-native-proof",
            }
            for index, module in enumerate(MODULES)
        ],
        "raw": {
            "path": "performance/v9/evidence/synthetic-paired-rows-never-open.jsonl.gz",
            "rows": RAW_ROWS,
            "operations_per_row": OPERATIONS_PER_SAMPLE,
            "uncompressed_rows_sha256": synthetic_digest("paired-timing-evidence"),
        },
        "memory": {
            "path": "performance/v9/evidence/synthetic-memory-never-read.jsonl.gz",
            "rows": MEMORY_ROWS,
            "cases_per_module": MEMORY_CASES,
            "uncompressed_rows_sha256": hashlib.sha256(memory_bytes).hexdigest(),
            "python_peak_definition": "tracemalloc-python-allocations-only",
            "process_peak_definition": "whole-process-peak-rss-bytes",
        },
        "results": blocks,
        "opening_sha256": manifest["seal"]["opening_sha256"],
        "original_holdout_accessed": False,
        "v8_holdout_accessed": False,
        "original_v7_cases": 10_312,
        "combined_results": "NOT MEASURED",
        "failed": 0,
    }
    return manifest, summary, compressed


def copy_summary(original: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(original)
    for key in ("modules", "cold_process_startup"):
        if isinstance(result.get(key), list):
            result[key] = list(result[key])
    for key in ("raw", "memory", "from_scratch_audit"):
        if isinstance(result.get(key), dict):
            result[key] = dict(result[key])
    wrapper = result.get("candidate_freeze")
    if isinstance(wrapper, dict):
        result["candidate_freeze"] = copy.deepcopy(wrapper)
    blocks = result.get("results")
    if isinstance(blocks, list):
        result["results"] = []
        for block in blocks:
            copied = dict(block)
            copied["case_results"] = list(block.get("case_results", []))
            copied["regressions"] = list(block.get("regressions", []))
            result["results"].append(copied)
    return result


def replace_case(summary: dict[str, Any], block_index: int, row_index: int, **changes: Any) -> None:
    block = summary["results"][block_index]
    row = dict(block["case_results"][row_index])
    row.update(changes)
    block["case_results"][row_index] = row


def memory_mutation(compressed: bytes, action: Callable[[dict[str, Any]], None]) -> bytes:
    payload = gzip.decompress(compressed)
    segments = payload.splitlines()
    row = json.loads(segments[0])
    require(isinstance(row, dict), "synthetic memory evidence is invalid")
    action(row)
    segments[0] = canonical_bytes(row)
    return gzip.compress(b"\n".join(segments) + b"\n", mtime=0)


def expect_rejection(
    name: str,
    action: Callable[[], Any],
) -> dict[str, Any]:
    try:
        action()
    except (ValueError, TypeError, KeyError, OverflowError, OSError, EOFError):
        return {"name": name, "passed": True}
    raise ValueError(f"the synthetic chart controls accepted corruption: {name}")


def self_test() -> dict[str, Any]:
    attempts = {"files_read": 0, "files_written": 0, "processes_started": 0}

    def blocked_read(*_args: Any, **_kwargs: Any) -> Any:
        attempts["files_read"] += 1
        raise ValueError("the synthetic-only chart test attempted a filesystem read")

    def blocked_write(*_args: Any, **_kwargs: Any) -> Any:
        attempts["files_written"] += 1
        raise ValueError("the synthetic-only chart test attempted a filesystem write")

    def blocked_process(*_args: Any, **_kwargs: Any) -> Any:
        attempts["processes_started"] += 1
        raise ValueError("the synthetic-only chart test attempted to start a process")

    with (
        mock.patch.object(builtins, "open", side_effect=blocked_read),
        mock.patch.object(Path, "open", side_effect=blocked_read),
        mock.patch.object(Path, "read_bytes", side_effect=blocked_read),
        mock.patch.object(Path, "read_text", side_effect=blocked_read),
        mock.patch.object(Path, "write_bytes", side_effect=blocked_write),
        mock.patch.object(Path, "write_text", side_effect=blocked_write),
        mock.patch.object(Path, "mkdir", side_effect=blocked_write),
        mock.patch.object(gzip, "open", side_effect=blocked_read),
        mock.patch.object(subprocess, "run", side_effect=blocked_process),
        mock.patch.object(subprocess, "Popen", side_effect=blocked_process),
    ):
        manifest, summary, memory = synthetic_inputs()
        result = validate_final(manifest, summary, memory)
        charts = build_charts(result)
        require(charts == build_charts(result), "the complete generated SVG charts are nondeterministic")
        require(
            "Python re (baseline)" in charts["overall"]
            and "Exactly 1×" in charts["overall"]
            and "14,746" in charts["outcomes"],
            "a complete headline omitted Python or the frozen success target",
        )
        require(
            "NOT MEASURED" in charts["memory"]
            and "Whole isolated-process peak resident memory" in charts["memory"]
            and "Python-traced temporary allocations" in charts["memory"]
            and "zero Python baselines" in charts["memory"]
            and "does not independently recompute" in charts["overall"],
            "the charts invent confidence, native memory, or baseline-zero ratios",
        )
        require(
            "0/256 clearly slower" in charts["regressions"]
            or "0/256 over 20% slower" in charts["regressions"],
            "the regression chart hides a zero-count frozen descriptor",
        )
        require(
            "MEETS the 14,746" in charts["outcomes"]
            and "DOES NOT MEET the 14,746" in charts["outcomes"],
            "the outcome chart fails to distinguish passing and failing engines",
        )
        controls: list[dict[str, Any]] = []

        def poison_summary(name: str, mutation: Callable[[dict[str, Any]], None]) -> None:
            def action() -> None:
                poisoned = copy_summary(summary)
                mutation(poisoned)
                validate_final(manifest, poisoned, memory)

            controls.append(expect_rejection(name, action))

        mutations: tuple[tuple[str, Callable[[dict[str, Any]], None]], ...] = (
            ("wrong-v8-final-schema", lambda value: value.update(schema="rebar-v8-prospective-performance-summary-v1")),
            ("changed-public-manifest-digest", lambda value: value.update(manifest_sha256="0" * 64)),
            ("changed-frozen-protocol-binding", lambda value: value.update(protocol_binding_sha256="0" * 64)),
            ("changed-public-opening-commitment", lambda value: value.update(opening_sha256="0" * 64)),
            ("wrong-pinned-python", lambda value: value.update(python="3.13.0")),
            ("wrong-worker-locale", lambda value: value.update(locale="POSIX")),
            ("hidden-candidate-failure", lambda value: value.update(failed=1)),
            ("original-holdout-access", lambda value: value.update(original_holdout_accessed=True)),
            ("v8-holdout-access", lambda value: value.update(v8_holdout_accessed=True)),
            ("invented-combined-result", lambda value: value.update(combined_results="MEASURED")),
            ("wrong-four-engine-baseline", lambda value: value["modules"].__setitem__(0, "synthetic.not-python")),
            ("missing-independent-engine", lambda value: value["modules"].pop()),
            ("duplicate-independent-engine", lambda value: value["modules"].__setitem__(2, value["modules"][1])),
            ("wrong-overall-case-denominator", lambda value: value.update(cases=CASE_COUNT - 1)),
            ("wrong-paired-round-denominator", lambda value: value.update(paired_rounds=PAIRED_ROUNDS - 1)),
            ("wrong-public-operation-denominator", lambda value: value.update(operations_per_sample=OPERATIONS_PER_SAMPLE - 1)),
            ("wrong-warmup-denominator", lambda value: value.update(warmups=WARMUPS - 1)),
            ("wrong-overall-bootstrap-denominator", lambda value: value.update(overall_bootstrap_draws=BOOTSTRAP_DRAWS - 1)),
            ("missing-timing-correctness-snapshot", lambda value: value.update(correctness_snapshots=CORRECTNESS_SNAPSHOTS - 1)),
            ("missing-four-engine-paired-row", lambda value: value["raw"].update(rows=RAW_ROWS - 1)),
            ("wrong-paired-row-operation-denominator", lambda value: value["raw"].update(operations_per_row=OPERATIONS_PER_SAMPLE - 1)),
            ("invalid-paired-raw-fingerprint", lambda value: value["raw"].update(uncompressed_rows_sha256="not-a-digest")),
            ("dropped-isolated-process-startup", lambda value: value["cold_process_startup"].pop()),
            ("startup-hidden-inside-public-timing", lambda value: value["cold_process_startup"].__setitem__(0, {**value["cold_process_startup"][0], "included_in_main_speedup": True})),
            ("dropped-candidate-ranking", lambda value: value["results"].pop()),
            ("duplicate-candidate-ranking", lambda value: value["results"].__setitem__(1, value["results"][0])),
            ("wrong-candidate-case-denominator", lambda value: value["results"][0].update(cases=CASE_COUNT - 1)),
            ("wrong-candidate-bootstrap-denominator", lambda value: value["results"][0].update(bootstrap_draws=BOOTSTRAP_DRAWS - 1)),
            ("weakened-14746-win-target", lambda value: value["results"][0].update(minimum_statistically_faster_cases=MINIMUM_WINS - 1)),
            ("dropped-measured-case", lambda value: value["results"][0]["case_results"].pop()),
            ("duplicate-measured-case", lambda value: value["results"][0]["case_results"].__setitem__(1, dict(value["results"][0]["case_results"][0]))),
            ("invented-workload-descriptor", lambda value: replace_case(value, 0, 0, workload="synthetic-nonfrozen-family")),
            ("wrong-case-paired-rounds", lambda value: replace_case(value, 0, 0, paired_rounds=PAIRED_ROUNDS - 1)),
            ("wrong-case-public-operation-count", lambda value: replace_case(value, 0, 0, operations_per_sample=OPERATIONS_PER_SAMPLE - 1)),
            ("nonfinite-measured-speed", lambda value: replace_case(value, 0, 0, speedup=float("nan"))),
            ("nonpositive-measured-speed", lambda value: replace_case(value, 0, 0, speedup=0.0)),
            ("inverted-case-confidence-interval", lambda value: replace_case(value, 0, 0, confidence_low=3.0)),
            ("false-case-confidence-win", lambda value: replace_case(value, 0, 3, statistically_faster=True)),
            ("false-exact-five-sixths-regression", lambda value: replace_case(value, 0, 1, runtime_regression_over_20_percent=True)),
            ("hidden-case-runtime-regression", lambda value: replace_case(value, 0, 0, runtime_regression_over_20_percent=False)),
            ("substituted-overall-geometric-mean", lambda value: value["results"][0].update(geomean_speedup=value["results"][0]["geomean_speedup"] * 1.01)),
            ("inverted-overall-confidence", lambda value: value["results"][0].update(confidence_low=value["results"][0]["geomean_speedup"] * 1.1)),
            ("hidden-confidence-qualified-win", lambda value: value["results"][0].update(statistically_faster_cases=value["results"][0]["statistically_faster_cases"] - 1)),
            ("hidden-large-regression-count", lambda value: value["results"][0].update(regression_count=value["results"][0]["regression_count"] - 1)),
            ("omitted-complete-regression-row", lambda value: value["results"][0]["regressions"].pop()),
            ("duplicated-complete-regression-row", lambda value: value["results"][0]["regressions"].append(dict(value["results"][0]["regressions"][0]))),
            ("false-overall-speed-success", lambda value: value["results"][0].update(meets_speed_requirement=not value["results"][0]["meets_speed_requirement"])),
            ("false-confidence-win-success", lambda value: value["results"][0].update(meets_case_requirement=not value["results"][0]["meets_case_requirement"])),
            ("false-final-success", lambda value: value["results"][0].update(success=not value["results"][0]["success"])),
            ("missing-native-pipeline-audit", lambda value: value["from_scratch_audit"].update(distinct_pipelines=2)),
            ("missing-five-owned-native-artifacts", lambda value: value["from_scratch_audit"].update(owned_native_artifacts=4)),
            ("wrong-candidate-freeze-schema", lambda value: value["candidate_freeze"]["document"].update(schema="rebar-v8-poison-freeze-v1")),
            ("candidate-freeze-opening-access", lambda value: value["candidate_freeze"]["document"].update(opening_read=True)),
            ("candidate-freeze-hidden-case-materialization", lambda value: value["candidate_freeze"]["document"].update(hidden_cases_generated=1)),
            ("candidate-freeze-early-measurement", lambda value: value["candidate_freeze"]["document"].update(performance_measured=True)),
            ("candidate-freeze-missing-engine", lambda value: value["candidate_freeze"]["document"]["candidates"].pop()),
            ("candidate-freeze-stale-edge", lambda value: value["candidate_freeze"]["document"]["candidates"][0].update(edge_sha256="x")),
            ("candidate-freeze-foreign-native", lambda value: value["candidate_freeze"]["document"]["candidates"][0]["artifacts"].pop("native-bridge")),
            ("incomplete-separate-memory-row-count", lambda value: value["memory"].update(rows=MEMORY_ROWS - 1)),
            ("incomplete-separate-memory-case-count", lambda value: value["memory"].update(cases_per_module=MEMORY_CASES - 1)),
            ("poisoned-separate-memory-digest", lambda value: value["memory"].update(uncompressed_rows_sha256="0" * 64)),
            ("memory-claimed-as-native-allocator", lambda value: value["memory"].update(python_peak_definition="candidate-native-allocator")),
            ("process-rss-claimed-as-native-allocator", lambda value: value["memory"].update(process_peak_definition="candidate-native-allocator")),
        )
        for name, mutation in mutations:
            poison_summary(name, mutation)

        manifest_mutations: tuple[tuple[str, Callable[[dict[str, Any]], None]], ...] = (
            ("wrong-v8-public-manifest-schema", lambda value: value.update(schema="rebar-v8-prospective-performance-holdout-v1")),
            ("changed-public-sealed-state", lambda value: value.update(state="unsealed")),
            ("changed-public-goal", lambda value: value["correctness"].update(goal_sha256="0" * 64)),
            ("missing-public-python-operation", lambda value: value["layout"]["apis"].pop()),
            ("missing-public-workload-family", lambda value: value["layout"]["workloads"].pop()),
            ("changed-public-24576-case-grid", lambda value: value["layout"].update(cases=CASE_COUNT - 1)),
            ("changed-public-2048-case-operation", lambda value: value["layout"].update(cases_per_api=CASES_PER_API - 1)),
            ("changed-public-256-case-descriptor", lambda value: value["layout"].update(cases_per_cell=CASES_PER_CELL - 1)),
            ("changed-public-31-paired-rounds", lambda value: value["trials"].update(paired_rounds=PAIRED_ROUNDS - 1)),
            ("changed-public-16-timed-calls", lambda value: value["trials"].update(operations_per_sample=OPERATIONS_PER_SAMPLE - 1)),
            ("changed-public-3047424-timing-rows", lambda value: value["trials"].update(four_engine_timed_rows=RAW_ROWS - 1)),
            ("changed-public-9142272-correctness-checks", lambda value: value["trials"].update(four_engine_correctness_snapshots=CORRECTNESS_SNAPSHOTS - 1)),
            ("changed-public-9999-bootstrap-draws", lambda value: value["statistics"].update(overall_bootstrap_draws=BOOTSTRAP_DRAWS - 1)),
            ("changed-public-14746-win-target", lambda value: value["statistics"].update(minimum_significant_wins=MINIMUM_WINS - 1)),
            ("changed-public-1536-memory-cases", lambda value: value["memory"].update(cases=MEMORY_CASES - 1)),
            ("changed-public-16-memory-cases-per-cell", lambda value: value["memory"].update(cases_per_cell=MEMORY_CASES_PER_CELL - 1)),
            ("changed-public-manifest-opening-commitment", lambda value: value["seal"].update(opening_sha256="invalid")),
            ("changed-public-manifest-binding", lambda value: value.update(binding_sha256="0" * 64)),
        )
        for name, mutation in manifest_mutations:
            def poisoned_manifest(action: Callable[[dict[str, Any]], None] = mutation) -> None:
                changed = copy.deepcopy(manifest)
                action(changed)
                validate_final(changed, summary, memory)

            controls.append(expect_rejection(name, poisoned_manifest))

        memory_mutations: tuple[tuple[str, Callable[[dict[str, Any]], None]], ...] = (
            ("wrong-independent-memory-row-schema", lambda row: row.update(schema="rebar-v8-memory-row-v1")),
            ("foreign-independent-memory-engine", lambda row: row.update(module="synthetic.foreign-candidate")),
            ("changed-independent-memory-case", lambda row: row.update(case="synthetic.v9.nonexistent")),
            ("changed-independent-memory-workload", lambda row: row.update(workload="synthetic-nonfrozen-workload")),
            ("changed-independent-memory-locale", lambda row: row.update(locale="POSIX")),
            ("negative-python-allocation", lambda row: row.update(python_peak_bytes=-1)),
            ("negative-process-peak", lambda row: row.update(process_peak_bytes=-1)),
            ("candidate-native-allocation-fabrication", lambda row: row.update(python_memory_is_native_memory=True)),
            ("timing-worker-used-for-memory", lambda row: row.update(instrumentation_worker=False)),
            ("incorrect-separate-memory-result", lambda row: row.update(correctness=False)),
        )
        for name, mutation in memory_mutations:
            def poisoned_memory(action: Callable[[dict[str, Any]], None] = mutation) -> None:
                changed_memory = memory_mutation(memory, action)
                changed_summary = copy_summary(summary)
                changed_summary["memory"]["uncompressed_rows_sha256"] = hashlib.sha256(
                    gzip.decompress(changed_memory)
                ).hexdigest()
                validate_final(manifest, changed_summary, changed_memory)

            controls.append(expect_rejection(name, poisoned_memory))

        def truncated_memory() -> None:
            changed = gzip.compress(gzip.decompress(memory).splitlines(keepends=True)[0], mtime=0)
            poisoned = copy_summary(summary)
            poisoned["memory"]["uncompressed_rows_sha256"] = hashlib.sha256(
                gzip.decompress(changed)
            ).hexdigest()
            validate_final(manifest, poisoned, changed)

        controls.append(expect_rejection("truncated-independent-memory-stream", truncated_memory))

        def noncanonical_memory() -> None:
            raw = gzip.decompress(memory)
            first, remaining = raw.split(b"\n", 1)
            row = json.loads(first)
            rewritten = json.dumps(row, sort_keys=False).encode("ascii") + b"\n" + remaining
            changed = gzip.compress(rewritten, mtime=0)
            poisoned = copy_summary(summary)
            poisoned["memory"]["uncompressed_rows_sha256"] = hashlib.sha256(rewritten).hexdigest()
            validate_final(manifest, poisoned, changed)

        controls.append(expect_rejection("noncanonical-independent-memory-line", noncanonical_memory))
        controls.append(
            expect_rejection(
                "synthetic-self-test-with-a-real-summary-path",
                lambda: main(["--self-test", "--summary", "/synthetic/never-read.json"]),
            )
        )
        controls.append(
            expect_rejection(
                "synthetic-self-test-with-a-real-memory-path",
                lambda: main(["--self-test", "--memory", "/synthetic/never-read.jsonl.gz"]),
            )
        )
        require(len(controls) >= 40, "the synthetic chart suite has too few corruption controls")
        require(
            len({entry["name"] for entry in controls}) == len(controls)
            and all(entry["passed"] is True for entry in controls),
            "a synthetic chart corruption was silently accepted",
        )
        require(
            attempts == {"files_read": 0, "files_written": 0, "processes_started": 0},
            "the synthetic-only charts accessed a file or launched an actual worker",
        )
        return {
            "schema": CHART_SELF_TEST_SCHEMA,
            "status": "PASS",
            "synthetic_only": True,
            "candidate_imported": False,
            "holdout_accessed": False,
            "opening_read": False,
            "hidden_cases_generated": 0,
            "files_read": 0,
            "files_written": 0,
            "processes_started": 0,
            "charts": len(charts),
            "engines": ENGINE_COUNT,
            "candidates": CANDIDATE_COUNT,
            "cases_per_candidate": CASE_COUNT,
            "synthetic_candidate_case_rows": CASE_COUNT * CANDIDATE_COUNT,
            "synthetic_memory_rows": MEMORY_ROWS,
            "paired_rounds": PAIRED_ROUNDS,
            "operations_per_sample": OPERATIONS_PER_SAMPLE,
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "minimum_significant_wins": MINIMUM_WINS,
            "poison_control_count": len(controls),
            "poison_controls": controls,
        }


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read the explicitly supplied {label}: {path}") from error
    require(isinstance(value, dict), f"the explicitly supplied {label} is not a JSON object")
    return value


def read_memory(path: Path) -> bytes:
    require(path.suffix == ".gz", "the separately supplied memory evidence must be gzip-compressed")
    try:
        return path.read_bytes()
    except OSError as error:
        raise ValueError(f"cannot read the explicitly supplied separate memory evidence: {path}") from error


def main(argv: list[str] | None = None) -> dict[str, Any] | None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="use only complete in-memory synthetic evidence; never read or create a file")
    parser.add_argument("--manifest", type=Path, help="explicit prospective public v9 manifest")
    parser.add_argument("--summary", type=Path, help="explicit actual, already-unsealed v9 final summary")
    parser.add_argument("--memory", type=Path, help="explicit actual, gzip-compressed separate v9 memory evidence")
    parser.add_argument("--prefix", type=Path, help="explicit output prefix for exactly six validated final SVGs")
    args = parser.parse_args(argv)
    if args.self_test:
        require(
            args.manifest is None
            and args.summary is None
            and args.memory is None
            and args.prefix is None,
            "a synthetic-only chart test must not receive an actual filesystem path",
        )
        result = self_test()
        print(json.dumps(result, allow_nan=False, ensure_ascii=True, sort_keys=True), flush=True)
        return result
    require(
        args.manifest is not None
        and args.summary is not None
        and args.memory is not None
        and args.prefix is not None,
        "real final rendering requires explicit --manifest, --summary, --memory, and --prefix paths",
    )
    manifest = read_json(args.manifest, "prospective v9 public manifest")
    summary = read_json(args.summary, "already-authorized final v9 results")
    memory_section = summary.get("memory")
    require(isinstance(memory_section, dict), "the separate-memory evidence has no frozen summary provenance")
    declared_path = memory_section.get("path")
    require(isinstance(declared_path, str) and bool(declared_path), "the separate-memory evidence has no committed path")
    require(
        args.memory.resolve() == (ROOT / declared_path).resolve(),
        "the explicitly supplied memory stream is not the one committed by the final summary",
    )
    compressed = read_memory(args.memory)
    final = validate_final(manifest, summary, compressed)
    charts = build_charts(final)
    destinations = {name: Path(f"{args.prefix}-{name}.svg") for name in charts}
    require(
        len({path.resolve() for path in destinations.values()}) == len(charts),
        "the six final SVG output destinations overlap",
    )
    protected = {args.manifest.resolve(), args.summary.resolve(), args.memory.resolve()}
    require(
        not any(path.resolve() in protected for path in destinations.values()),
        "a final SVG would overwrite actual frozen evidence",
    )
    args.prefix.parent.mkdir(parents=True, exist_ok=True)
    for name, content in charts.items():
        destination = destinations[name]
        with destination.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        print(f"wrote {destination}", flush=True)
    return None


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, KeyError, OverflowError, OSError) as error:
        raise SystemExit(f"error: {error}") from error
