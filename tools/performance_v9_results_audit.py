#!/usr/bin/env python3
"""Independently replay an explicitly supplied, already completed v9 result.

This verifier never discovers an input, opens a secret, generates a held-out
case, imports a candidate, or measures an operation. Real verification accepts
only explicitly supplied, already existing final evidence. Public synthetic
verification constructs a small, complete, domain-separated fixture in memory.
"""

from __future__ import annotations

import argparse
import builtins
import copy
import gzip
import hashlib
import io
import json
import math
import platform
import random
import statistics
import subprocess
import sys
import zlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Callable, Iterator, Mapping
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
PUBLIC_SOURCE = ROOT / "tools/rust_v9_holdout_protocol.py"
EVIDENCE_ROOT = ROOT / "performance/v9/evidence"

MANIFEST_SCHEMA = "rebar-v9-prospective-semantic-performance-holdout-v1"
SUMMARY_SCHEMA = "rebar-v9-real-public-operation-summary-v1"
TIMING_ROW_SCHEMA = "rebar-v9-real-public-operation-paired-row-v1"
MEMORY_ROW_SCHEMA = "rebar-v9-independent-memory-row-v1"
FREEZE_SCHEMA = "rebar-v9-current-native-candidate-freeze-v1"
AUDIT_SCHEMA = "rebar-v9-independent-complete-final-results-audit-v1"
SELF_TEST_SCHEMA = "rebar-v9-results-audit-public-synthetic-self-test-v1"

APIS = (
    "compile", "escape", "search", "match", "fullmatch", "findall",
    "finditer", "split", "sub", "subn", "match-surface", "scanner",
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
ARTIFACT_ROLES = {
    "candidates.vm_candidate": frozenset({"public-python", "native-bridge"}),
    "candidates.rust_candidate": frozenset(
        {"public-python", "native-source", "bridge-source", "native-bridge", "native-engine"}
    ),
    "candidates.zig_candidate": frozenset(
        {"public-python", "native-bridge", "native-engine"}
    ),
}

REAL_CASES_PER_CELL = 256
REAL_MEMORY_PER_CELL = 16
PAIR_ROUNDS = 31
OPERATIONS_PER_SAMPLE = 16
WARMUPS = 4
BOOTSTRAP_DRAWS = 9_999
ORDER_SEED = 20260723931
BOOTSTRAP_SEED = 20260723999
STUDENT_T_DF30_975 = 2.0422724563012373
REGRESSION_THRESHOLD = 5.0 / 6.0
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"

MEMORY_FIELDS = (
    "python_current_bytes",
    "python_peak_bytes",
    "process_current_before_bytes",
    "process_current_after_bytes",
    "process_peak_bytes",
)


@dataclass(frozen=True)
class ReplaySpec:
    cases_per_cell: int
    memory_per_cell: int
    synthetic: bool = False

    @property
    def descriptors(self) -> frozenset[tuple[str, str]]:
        return frozenset((api, workload) for api in APIS for workload in WORKLOADS)

    @property
    def case_count(self) -> int:
        return len(APIS) * len(WORKLOADS) * self.cases_per_cell

    @property
    def cases_per_api(self) -> int:
        return len(WORKLOADS) * self.cases_per_cell

    @property
    def minimum_wins(self) -> int:
        return (3 * self.case_count + 4) // 5

    @property
    def timing_rows(self) -> int:
        return self.case_count * PAIR_ROUNDS * len(MODULES)

    @property
    def correctness_snapshots(self) -> int:
        return self.timing_rows * 3

    @property
    def memory_cases(self) -> int:
        return len(APIS) * len(WORKLOADS) * self.memory_per_cell

    @property
    def memory_rows(self) -> int:
        return self.memory_cases * len(MODULES)


REAL_SPEC = ReplaySpec(REAL_CASES_PER_CELL, REAL_MEMORY_PER_CELL)
SYNTHETIC_SPEC = ReplaySpec(4, 1, synthetic=True)


@dataclass(frozen=True)
class PublicLayout:
    binding: str
    digest: str
    source_digest: str
    opening_commitment: str
    modules: tuple[str, ...]
    spec: ReplaySpec


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


def fingerprint(value: Any, label: str) -> str:
    require(
        isinstance(value, str)
        and len(value) == 64
        and all(letter in "0123456789abcdef" for letter in value),
        f"{label} is not a complete lowercase SHA-256 fingerprint",
    )
    return value


def integer(value: Any, label: str, expected: int | None = None) -> int:
    require(isinstance(value, int) and not isinstance(value, bool), f"{label} is not an integer")
    require(value >= 0, f"{label} is negative")
    if expected is not None:
        require(value == expected, f"{label} must equal {expected:,}")
    return value


def positive(value: Any, label: str) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{label} is not a number")
    result = float(value)
    require(math.isfinite(result) and result > 0, f"{label} must be finite and positive")
    return result


def same_float(actual: Any, expected: float, label: str) -> float:
    result = positive(actual, label)
    require(
        math.isclose(result, expected, rel_tol=1e-12, abs_tol=1e-13),
        f"{label} does not reproduce the frozen paired measurements",
    )
    return result


def is_runtime_regression(speedup: float) -> bool:
    """Apply the frozen strictly-greater-than-20-percent time boundary."""
    return positive(speedup, "the strict runtime-regression speedup") < REGRESSION_THRESHOLD


def validate_pinned_python() -> None:
    require(
        platform.python_implementation() == "CPython"
        and tuple(sys.version_info[:3]) == (3, 14, 6),
        "independent replay requires pinned CPython 3.14.6",
    )


def validate_manifest(
    document: Mapping[str, Any],
    spec: ReplaySpec,
    source_digest: str,
) -> PublicLayout:
    require(isinstance(document, dict), "the prospective public manifest is not an object")
    require(document.get("schema") == MANIFEST_SCHEMA, "the frozen v9 public-manifest schema changed")
    require(
        document.get("state") == "prospectively-sealed-not-materialized",
        "the prospective blinded manifest state changed",
    )
    source = document.get("source")
    require(
        isinstance(source, dict)
        and source.get("path") == "tools/rust_v9_holdout_protocol.py"
        and fingerprint(source.get("sha256"), "the frozen public protocol source") == source_digest,
        "the actual public final runner changed after the prospective freeze",
    )
    reference = document.get("reference")
    require(
        isinstance(reference, dict)
        and reference.get("implementation") == "CPython"
        and reference.get("version") == "3.14.6"
        and reference.get("unicode_version") == "16.0.0"
        and reference.get("enforced_worker_locale") == "C",
        "the pinned CPython, Unicode, or isolated C locale changed",
    )
    seal = document.get("seal")
    require(
        isinstance(seal, dict)
        and seal.get("algorithm") == "sha256"
        and seal.get("opening_bytes") == 32
        and seal.get("opening_mode") == "0600",
        "the prospective public blinded-commitment protocol changed",
    )
    opening = fingerprint(seal.get("opening_sha256"), "the public blinded opening commitment")
    layout = document.get("layout")
    require(isinstance(layout, dict), "the frozen public descriptor grid is missing")
    require(layout.get("apis") == list(APIS), "a frozen public Python operation changed")
    require(layout.get("workloads") == list(WORKLOADS), "a frozen public workload changed")
    integer(layout.get("cases"), "the complete case denominator", spec.case_count)
    integer(layout.get("cases_per_api"), "the cases per public API", spec.cases_per_api)
    integer(layout.get("cases_per_cell"), "the cases per frozen workload", spec.cases_per_cell)
    applicability = layout.get("applicability")
    require(
        isinstance(applicability, dict) and set(applicability) == set(APIS),
        "a real public operation lost its independently frozen applicability",
    )
    trials = document.get("trials")
    require(isinstance(trials, dict), "the frozen paired-trial protocol is missing")
    integer(trials.get("minimum_candidates"), "the independent candidate minimum", 3)
    require(
        trials.get("required_independent_native_families") == ["vm", "rust", "zig"],
        "the three genuinely independent native pipelines changed",
    )
    integer(trials.get("paired_rounds"), "the frozen paired rounds", PAIR_ROUNDS)
    integer(trials.get("warmups"), "the frozen warmups", WARMUPS)
    integer(trials.get("operations_per_sample"), "the real operations per sample", OPERATIONS_PER_SAMPLE)
    integer(trials.get("order_seed"), "the frozen rotating-order seed", ORDER_SEED)
    integer(trials.get("four_engine_timed_rows"), "the complete four-engine paired rows", spec.timing_rows)
    integer(
        trials.get("four_engine_correctness_snapshots"),
        "the complete independent timing correctness checks",
        spec.correctness_snapshots,
    )
    require(
        trials.get("order_method") == "seeded-counterbalanced-rotating-latin-square",
        "the counterbalanced paired-engine order changed",
    )
    statistics_section = document.get("statistics")
    require(isinstance(statistics_section, dict), "the frozen statistical protocol is missing")
    same_float(statistics_section.get("confidence"), 0.95, "the frozen confidence level")
    same_float(
        statistics_section.get("case_student_t_critical"),
        STUDENT_T_DF30_975,
        "the paired Student-t critical value",
    )
    require(
        statistics_section.get("case_method") == "paired-log-student-t-df30"
        and statistics_section.get("overall_method")
        == "stratified-paired-whole-case-cluster-percentile-bootstrap",
        "the frozen exact paired confidence method changed",
    )
    integer(statistics_section.get("minimum_significant_wins"), "the significant-win denominator", spec.minimum_wins)
    integer(statistics_section.get("overall_bootstrap_draws"), "the complete seeded bootstrap draws", BOOTSTRAP_DRAWS)
    integer(statistics_section.get("bootstrap_seed"), "the public frozen bootstrap seed", BOOTSTRAP_SEED)
    same_float(statistics_section.get("overall_lower_bound"), 1.5, "the minimum overall confidence lower bound")
    require(
        statistics_section.get("runtime_regression") == "candidate_time > 1.2 * baseline_time",
        "the strict greater-than-20-percent runtime definition changed",
    )
    correctness = document.get("correctness")
    require(isinstance(correctness, dict), "the independently frozen correctness obligations are missing")
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
        integer(correctness.get(key), f"the frozen correctness obligation {key}", count)
    require(correctness.get("goal_sha256") == GOAL_SHA256, "the immutable experiment objective changed")
    memory = document.get("memory")
    require(isinstance(memory, dict), "the independent balanced memory protocol is missing")
    integer(memory.get("cases"), "independent memory cases per engine", spec.memory_cases)
    integer(memory.get("cases_per_cell"), "independent memory cases per workload", spec.memory_per_cell)
    require(
        memory.get("python_peak") == "tracemalloc-python-allocations-only"
        and memory.get("process_current") == "procfs-resident-bytes"
        and memory.get("process_peak") == "whole-process-peak-resident-bytes",
        "isolated process memory was confused with Python or candidate-native allocations",
    )
    history = document.get("history")
    require(
        isinstance(history, dict)
        and history.get("v9_results") == "NOT MEASURED"
        and history.get("combined_results") == "NOT MEASURED",
        "the public prospective manifest claims invented performance",
    )
    binding = fingerprint(document.get("binding_sha256"), "the complete public manifest binding")
    require(
        binding == canonical_digest({key: value for key, value in document.items() if key != "binding_sha256"}),
        "the frozen public manifest content was tampered with",
    )
    return PublicLayout(binding, canonical_digest(document), source_digest, opening, MODULES, spec)


class CanonicalGzipRows:
    """Stream one deterministic gzip member and canonical newline-delimited JSON."""

    def __init__(self, stream: BinaryIO, label: str) -> None:
        self.stream = stream
        self.label = label
        self.digest = hashlib.sha256()
        self.count = 0

    def __iter__(self) -> Iterator[dict[str, Any]]:
        header = self.stream.read(10)
        require(
            len(header) == 10
            and header[:3] == b"\x1f\x8b\x08"
            and header[3] == 0
            and header[4:8] == b"\x00\x00\x00\x00",
            f"{self.label} does not use the single frozen, nameless, zero-timestamp gzip format",
        )
        self.stream.seek(0)
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        pending = b""
        try:
            while True:
                compressed = self.stream.read(1_048_576)
                if not compressed:
                    break
                expanded = decoder.decompress(compressed)
                require(not decoder.unused_data, f"{self.label} contains a second gzip member or trailing data")
                pending += expanded
                require(len(pending) <= 64 * 1024 * 1024, f"{self.label} has an oversized evidence line")
                parts = pending.split(b"\n")
                pending = parts.pop()
                for segment in parts:
                    line = segment + b"\n"
                    try:
                        row = json.loads(segment)
                    except (UnicodeError, json.JSONDecodeError) as error:
                        raise ValueError(f"{self.label} row {self.count} is invalid JSON") from error
                    require(
                        isinstance(row, dict) and canonical_bytes(row) + b"\n" == line,
                        f"{self.label} row {self.count} is not canonical ASCII JSON",
                    )
                    self.digest.update(line)
                    self.count += 1
                    yield row
            remaining = decoder.flush()
        except zlib.error as error:
            raise ValueError(f"{self.label} is a corrupt compressed evidence stream") from error
        require(decoder.eof and not decoder.unused_data, f"{self.label} has a truncated or concatenated gzip member")
        require(not remaining and not pending, f"{self.label} has an unterminated canonical evidence row")


def counterbalanced_order(
    modules: tuple[str, ...], identifier: str, round_index: int
) -> tuple[str, ...]:
    require(modules == MODULES, "the replay requires Python followed by the exact frozen candidates")
    require(0 <= round_index < PAIR_ROUNDS, "a paired round escaped its frozen denominator")
    digest = hashlib.sha256(
        f"rebar-v9-balanced-order:{ORDER_SEED}:{identifier}".encode("utf-8")
    ).digest()
    ordered = list(modules)
    random.Random(int.from_bytes(digest[:16], "big")).shuffle(ordered)
    start = (int.from_bytes(digest[16:24], "big") + round_index) % len(ordered)
    return tuple(ordered[start:] + ordered[:start])


def case_confidence(logs: list[float]) -> tuple[float, float]:
    require(len(logs) == PAIR_ROUNDS, "a replayed case lost a paired round")
    require(all(math.isfinite(value) for value in logs), "a paired log ratio is not finite")
    center = statistics.fmean(logs)
    spread = STUDENT_T_DF30_975 * statistics.stdev(logs) / math.sqrt(PAIR_ROUNDS)
    low, high = math.exp(center - spread), math.exp(center + spread)
    positive(low, "the replayed case confidence lower bound")
    positive(high, "the replayed case confidence upper bound")
    return low, high


def percentile(values: list[float], quantile: float) -> float:
    require(bool(values) and 0 <= quantile <= 1, "the exact bootstrap percentile is invalid")
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def stratified_bootstrap(
    cells: Mapping[tuple[str, str], list[float]],
    spec: ReplaySpec,
    seed: int,
    *,
    draws: int = BOOTSTRAP_DRAWS,
) -> tuple[float, float]:
    require(set(cells) == spec.descriptors, "the exact bootstrap omits a frozen public stratum")
    integer(draws, "the seeded bootstrap draw denominator", BOOTSTRAP_DRAWS)
    ordered = [cells[(api, workload)] for api in APIS for workload in WORKLOADS]
    require(all(len(cell) == spec.cases_per_cell for cell in ordered), "a bootstrap workload changed its exact case weight")
    require(all(math.isfinite(value) for cell in ordered for value in cell), "the exact bootstrap contains a nonfinite case")
    if all(all(value == cell[0] for value in cell) for cell in ordered):
        point = math.exp(statistics.fmean(cell[0] for cell in ordered))
        return point, point
    generator = random.Random(seed)
    denominator = len(ordered) * spec.cases_per_cell
    observations: list[float] = []
    for _ in range(draws):
        total = 0.0
        for cell in ordered:
            total += sum(cell[generator.randrange(spec.cases_per_cell)] for _ in range(spec.cases_per_cell))
        value = math.exp(total / denominator)
        positive(value, "a replayed overall bootstrap observation")
        observations.append(value)
    return percentile(observations, 0.025), percentile(observations, 0.975)


def validate_live_provenance(
    summary: Mapping[str, Any],
    layout: PublicLayout,
    freeze_document: Mapping[str, Any],
    freeze_digest: str,
    audit_document: Mapping[str, Any],
    audit_digest: str,
    artifact_digests: Mapping[str, str],
) -> None:
    require(
        isinstance(audit_document, dict)
        and audit_document.get("schema_version") == 1
        and audit_document.get("audit") == "bounded-from-scratch-engine-provenance"
        and audit_document.get("passed") is True
        and audit_document.get("result") == "PASS"
        and audit_document.get("minimum_required_independent_families") == 3
        and integer(audit_document.get("verified_core_family_count"), "audited independent engine families") >= 3
        and integer(audit_document.get("verified_distinct_pipeline_count"), "audited distinct semantic pipelines") >= 3,
        "the genuine from-scratch audit does not prove three independent engines",
    )
    scope = audit_document.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("holdout_or_case_fixture_access") is False
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("mapped_binaries_hashed_against_static_elf") is True,
        "the independently frozen native audit accessed performance or omitted live ELF mappings",
    )
    reported_audit = summary.get("from_scratch_audit")
    require(
        isinstance(reported_audit, dict)
        and fingerprint(reported_audit.get("sha256"), "the frozen live-audit fingerprint") == audit_digest
        and integer(reported_audit.get("owned_native_artifacts"), "the five owned native artifacts", 5) == 5
        and integer(reported_audit.get("distinct_pipelines"), "the distinct native semantic pipelines") >= 3,
        "the actual from-scratch audit differs from the final results",
    )
    wrapper = summary.get("candidate_freeze")
    require(
        isinstance(wrapper, dict)
        and fingerprint(wrapper.get("sha256"), "the candidate-freeze fingerprint") == freeze_digest
        and wrapper.get("document") == freeze_document,
        "the actual candidate freeze differs from the final result",
    )
    require(
        isinstance(freeze_document, dict)
        and freeze_document.get("schema") == FREEZE_SCHEMA
        and freeze_document.get("protocol_binding_sha256") == layout.binding
        and freeze_document.get("baseline") == "re"
        and freeze_document.get("from_scratch_audit_sha256") == audit_digest
        and freeze_document.get("opening_read") is False
        and freeze_document.get("hidden_cases_generated") == 0
        and freeze_document.get("performance_measured") is False,
        "the independent candidate stopping point was not prospectively frozen",
    )
    commit = freeze_document.get("stopping_commit")
    require(
        isinstance(commit, str)
        and len(commit) in {40, 64}
        and all(value in "0123456789abcdef" for value in commit),
        "the frozen candidate stopping point is not an immutable Git object",
    )
    records = freeze_document.get("candidates")
    require(isinstance(records, list) and len(records) == 3, "a frozen independent candidate is missing")
    seen: set[str] = set()
    native_roles = 0
    for record in records:
        require(isinstance(record, dict), "a frozen candidate is invalid")
        module = record.get("module")
        require(module in MODULES[1:] and module not in seen, "a frozen candidate is foreign or duplicated")
        for field in ("edge_sha256", "campaign_sha256", "deep_contract_sha256"):
            fingerprint(record.get(field), f"the frozen {module} {field}")
        artifacts = record.get("artifacts")
        require(
            isinstance(artifacts, dict) and set(artifacts) == ARTIFACT_ROLES[module],
            f"{module} changed or shared its independently owned artifact roles",
        )
        for role, artifact in artifacts.items():
            require(isinstance(artifact, dict), f"{module} has an invalid frozen {role}")
            path = artifact.get("path")
            require(isinstance(path, str) and bool(path), f"{module} has no frozen {role} path")
            expected = fingerprint(artifact.get("sha256"), f"the frozen {module} {role}")
            require(artifact_digests.get(path) == expected, f"{module} source or native {role} changed after qualification")
            if role == "public-python":
                require(
                    Path(path).name == f"{module.rsplit('.', 1)[-1]}.py",
                    f"{module} reused another production candidate",
                )
            if role in {"native-bridge", "native-engine"}:
                native_roles += 1
        seen.add(module)
    require(seen == set(MODULES[1:]), "a genuinely independent frozen pipeline is missing")
    require(native_roles == 5, "the actual four-engine comparison does not own five distinct native artifacts")


def validate_summary_header(summary: Mapping[str, Any], layout: PublicLayout) -> None:
    require(isinstance(summary, dict), "the final summary is not an object")
    require(summary.get("schema") == SUMMARY_SCHEMA, "the real v9 final-summary schema changed")
    require(summary.get("python") == "3.14.6" and summary.get("locale") == "C", "the final pinned Python or locale changed")
    require(summary.get("failed") == 0, "the real final comparison has an unexplained failure")
    require(
        summary.get("protocol_binding_sha256") == layout.binding
        and summary.get("manifest_sha256") == layout.digest
        and summary.get("opening_sha256") == layout.opening_commitment,
        "the real final summary does not match its frozen public manifest",
    )
    require(
        summary.get("original_holdout_accessed") is False
        and summary.get("v8_holdout_accessed") is False
        and summary.get("original_v7_cases") == 10_312
        and summary.get("combined_results") == "NOT MEASURED",
        "the final replay reused or invented a previous holdout",
    )
    require(summary.get("modules") == list(layout.modules), "the final engine order omits Python, C, Rust, or Zig")
    integer(summary.get("cases"), "the complete final case denominator", layout.spec.case_count)
    integer(summary.get("paired_rounds"), "the complete paired rounds", PAIR_ROUNDS)
    integer(summary.get("operations_per_sample"), "the exact public operations per sample", OPERATIONS_PER_SAMPLE)
    integer(summary.get("warmups"), "the frozen four warmups", WARMUPS)
    integer(summary.get("overall_bootstrap_draws"), "the exact 9,999 bootstrap draws", BOOTSTRAP_DRAWS)
    integer(summary.get("correctness_snapshots"), "the complete timing correctness checks", layout.spec.correctness_snapshots)
    startup = summary.get("cold_process_startup")
    require(isinstance(startup, list) and len(startup) == len(layout.modules), "an isolated process startup is missing")
    found: set[str] = set()
    for record in startup:
        require(isinstance(record, dict), "an isolated process startup is invalid")
        module = record.get("module")
        require(module in layout.modules and module not in found, "an isolated engine startup was duplicated")
        require(
            integer(record.get("elapsed_ns"), "isolated startup nanoseconds") > 0,
            "isolated startup must consume a strictly positive measured duration",
        )
        require(
            record.get("included_in_main_speedup") is False
            and record.get("definition") == "isolated-process-start-import-and-current-native-proof",
            "cold startup was falsely combined with paired operation time",
        )
        found.add(module)


def summary_case_blocks(
    summary: Mapping[str, Any], layout: PublicLayout
) -> tuple[dict[str, dict[str, Any]], dict[str, tuple[str, str]], list[str]]:
    supplied = summary.get("results")
    require(isinstance(supplied, list) and len(supplied) == 3, "a final candidate result block was removed")
    blocks: dict[str, dict[str, Any]] = {}
    shared: dict[str, tuple[str, str]] | None = None
    ordered: list[str] | None = None
    for block in supplied:
        require(isinstance(block, dict), "a final candidate ranking is invalid")
        module = block.get("module")
        require(module in layout.modules[1:] and module not in blocks, "a final candidate ranking is missing or repeated")
        integer(block.get("cases"), f"{module} complete case denominator", layout.spec.case_count)
        integer(block.get("bootstrap_draws"), f"{module} exact overall bootstrap draws", BOOTSTRAP_DRAWS)
        integer(block.get("minimum_statistically_faster_cases"), f"{module} minimum significant wins", layout.spec.minimum_wins)
        source = block.get("case_results")
        require(isinstance(source, list) and len(source) == layout.spec.case_count, f"{module} omitted a final case result")
        identities: dict[str, tuple[str, str]] = {}
        counts: Counter[tuple[str, str]] = Counter()
        for row in source:
            require(isinstance(row, dict), f"{module} has an invalid summary case")
            identifier = row.get("case")
            require(
                isinstance(identifier, str)
                and bool(identifier)
                and identifier not in identities
                and (identifier.startswith("synthetic.v9.audit.") if layout.spec.synthetic else not identifier.startswith("synthetic.")),
                f"{module} duplicated or substituted an actual case identity",
            )
            key = (row.get("api"), row.get("workload"))
            require(key in layout.spec.descriptors, f"{module} changed a frozen descriptor")
            integer(row.get("paired_rounds"), f"{module} case paired rounds", PAIR_ROUNDS)
            integer(row.get("operations_per_sample"), f"{module} case public operations", OPERATIONS_PER_SAMPLE)
            speed = positive(row.get("speedup"), f"{module} case speed")
            low = positive(row.get("confidence_low"), f"{module} case lower confidence")
            high = positive(row.get("confidence_high"), f"{module} case upper confidence")
            require(low <= speed <= high, f"{module} supplied an invalid case confidence interval")
            require(
                isinstance(row.get("statistically_faster"), bool)
                and row["statistically_faster"] is (low > 1.0),
                f"{module} changed the strict confidence-qualified case-win rule",
            )
            require(
                isinstance(row.get("runtime_regression_over_20_percent"), bool)
                and row["runtime_regression_over_20_percent"] is is_runtime_regression(speed),
                f"{module} changed the strict five-sixths regression rule",
            )
            identities[identifier] = key
            counts[key] += 1
        require(
            set(counts) == layout.spec.descriptors
            and all(count == layout.spec.cases_per_cell for count in counts.values()),
            f"{module} silently changed a 96-cell case denominator",
        )
        if shared is None:
            shared = identities
            ordered = [row["case"] for row in source]
        else:
            require(identities == shared, f"{module} did not run exactly the same paired cases")
            require([row["case"] for row in source] == ordered, f"{module} reordered a frozen case")
        blocks[module] = block
    require(set(blocks) == set(layout.modules[1:]), "a genuinely independent candidate is unranked")
    assert shared is not None and ordered is not None
    return blocks, shared, ordered


def replay_timing(
    stream: BinaryIO,
    summary: Mapping[str, Any],
    layout: PublicLayout,
    blocks: Mapping[str, Mapping[str, Any]],
    metadata: Mapping[str, tuple[str, str]],
    case_order: list[str],
) -> dict[str, dict[str, Any]]:
    committed = summary.get("raw")
    require(isinstance(committed, dict), "the real paired timing provenance is missing")
    integer(committed.get("rows"), "the four-engine paired raw rows", layout.spec.timing_rows)
    integer(committed.get("operations_per_row"), "the actual operations per raw row", OPERATIONS_PER_SAMPLE)
    expected_digest = fingerprint(committed.get("uncompressed_rows_sha256"), "the canonical paired timing stream")
    require(isinstance(committed.get("path"), str) and bool(committed["path"]), "the paired timing provenance path is missing")
    maps = {
        module: {row["case"]: row for row in blocks[module]["case_results"]}
        for module in layout.modules[1:]
    }
    cells: dict[str, dict[tuple[str, str], list[float]]] = {
        module: {descriptor: [] for descriptor in layout.spec.descriptors}
        for module in layout.modules[1:]
    }
    wins: Counter[str] = Counter()
    losses: Counter[str] = Counter()
    replay_regressions: dict[str, list[dict[str, Any]]] = {
        module: [] for module in layout.modules[1:]
    }
    logs = {module: [] for module in layout.modules[1:]}
    paired: dict[str, int] = {}
    expected_order: tuple[str, ...] = ()
    reader = CanonicalGzipRows(stream, "the complete four-engine paired timing evidence")
    for offset, row in enumerate(reader):
        require(offset < layout.spec.timing_rows, "the paired timing evidence contains an extra row")
        case_index, within = divmod(offset, PAIR_ROUNDS * len(layout.modules))
        round_index, position = divmod(within, len(layout.modules))
        identifier = case_order[case_index]
        descriptor = metadata[identifier]
        if position == 0:
            expected_order = counterbalanced_order(layout.modules, identifier, round_index)
            paired = {}
        require(
            row.get("schema") == TIMING_ROW_SCHEMA
            and row.get("case") == identifier
            and (row.get("api"), row.get("workload")) == descriptor,
            "the paired evidence omitted, duplicated, reordered, or substituted a frozen case",
        )
        integer(row.get("round"), "the paired raw round", round_index)
        integer(row.get("position"), "the seeded Latin-order position", position)
        module = row.get("module")
        require(
            module == expected_order[position] and module not in paired,
            "a candidate or Python changed its exact seeded counterbalanced order",
        )
        integer(row.get("operations"), "actual timed public operations", OPERATIONS_PER_SAMPLE)
        elapsed = integer(row.get("elapsed_ns"), "actual paired elapsed nanoseconds")
        require(elapsed > 0, "a timed real public call is not strictly positive")
        same_float(row.get("ns_per_op"), elapsed / OPERATIONS_PER_SAMPLE, "actual nanoseconds per operation")
        require(
            row.get("locale") == "C"
            and row.get("correctness_pre") is True
            and row.get("correctness_timed") is True
            and row.get("correctness_post") is True,
            "a complete pre-, timed-, or post-operation Python correctness gate is missing",
        )
        paired[module] = elapsed
        if position != len(layout.modules) - 1:
            continue
        require(set(paired) == set(layout.modules), "a real paired candidate or Python row was omitted")
        baseline_ns = paired["re"]
        for candidate in layout.modules[1:]:
            logs[candidate].append(math.log(baseline_ns / paired[candidate]))
        if round_index != PAIR_ROUNDS - 1:
            continue
        for candidate in layout.modules[1:]:
            values = logs[candidate]
            require(len(values) == PAIR_ROUNDS, "a genuine paired round was silently removed")
            mean = statistics.fmean(values)
            speed = math.exp(mean)
            low, high = case_confidence(values)
            claimed = maps[candidate][identifier]
            same_float(claimed.get("speedup"), speed, f"{candidate} replayed case speed")
            same_float(claimed.get("confidence_low"), low, f"{candidate} replayed case lower confidence")
            same_float(claimed.get("confidence_high"), high, f"{candidate} replayed case upper confidence")
            significant = low > 1.0
            regressed = is_runtime_regression(speed)
            require(
                claimed.get("statistically_faster") is significant
                and claimed.get("runtime_regression_over_20_percent") is regressed,
                f"{candidate} concealed a case-level confidence result or runtime loss",
            )
            wins[candidate] += int(significant)
            losses[candidate] += int(high < 1.0)
            if regressed:
                replay_regressions[candidate].append(claimed)
            cells[candidate][descriptor].append(mean)
            values.clear()
    require(reader.count == layout.spec.timing_rows, "the canonical timing evidence is incomplete")
    require(reader.digest.hexdigest() == expected_digest, "the canonical timing evidence fingerprint changed")
    results: dict[str, dict[str, Any]] = {}
    for candidate_index, module in enumerate(layout.modules[1:]):
        block = blocks[module]
        grouped = cells[module]
        require(
            all(len(grouped[key]) == layout.spec.cases_per_cell for key in layout.spec.descriptors),
            f"{module} changed a weighted bootstrap workload cell",
        )
        flattened = [
            value
            for api in APIS
            for workload in WORKLOADS
            for value in grouped[(api, workload)]
        ]
        require(len(flattened) == layout.spec.case_count, f"{module} changed the equal-weight speed denominator")
        point = math.exp(statistics.fmean(flattened))
        low, high = stratified_bootstrap(grouped, layout.spec, BOOTSTRAP_SEED + candidate_index)
        same_float(block.get("geomean_speedup"), point, f"{module} complete 24,576-case geometric speed")
        same_float(block.get("confidence_low"), low, f"{module} independently replayed bootstrap lower bound")
        same_float(block.get("confidence_high"), high, f"{module} independently replayed bootstrap upper bound")
        integer(block.get("statistically_faster_cases"), f"{module} exact significant wins", wins[module])
        integer(block.get("regression_count"), f"{module} exact strict runtime losses", len(replay_regressions[module]))
        require(
            isinstance(block.get("regressions"), list)
            and block["regressions"] == replay_regressions[module],
            f"{module} omitted, invented, or reordered an individually recorded runtime regression",
        )
        passes_speed = low >= 1.5
        passes_cases = wins[module] >= layout.spec.minimum_wins
        require(
            block.get("meets_speed_requirement") is passes_speed
            and block.get("meets_case_requirement") is passes_cases
            and block.get("success") is (passes_speed and passes_cases),
            f"{module} fabricated an overall success claim",
        )
        results[module] = {
            "module": module,
            "cases": layout.spec.case_count,
            "geomean_speedup": point,
            "confidence_low": low,
            "confidence_high": high,
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "statistically_faster_cases": wins[module],
            "statistically_slower_cases": losses[module],
            "uncertain_cases": layout.spec.case_count - wins[module] - losses[module],
            "regression_count": len(replay_regressions[module]),
            "regression_sha256": canonical_digest(replay_regressions[module]),
            "success": passes_speed and passes_cases,
        }
    return results


def replay_memory(
    stream: BinaryIO,
    summary: Mapping[str, Any],
    layout: PublicLayout,
    metadata: Mapping[str, tuple[str, str]],
) -> dict[str, Any]:
    section = summary.get("memory")
    require(isinstance(section, dict), "independently measured memory provenance is missing")
    integer(section.get("rows"), "the complete four-engine memory evidence", layout.spec.memory_rows)
    integer(section.get("cases_per_module"), "independent balanced memory cases per engine", layout.spec.memory_cases)
    require(
        section.get("python_peak_definition") == "tracemalloc-python-allocations-only"
        and section.get("process_peak_definition") == "whole-process-peak-rss-bytes",
        "whole-process memory was falsely reported as native-allocator or Python allocation",
    )
    expected_digest = fingerprint(section.get("uncompressed_rows_sha256"), "the canonical independent memory stream")
    require(isinstance(section.get("path"), str) and bool(section["path"]), "the independent memory evidence path is missing")
    seen: dict[str, set[str]] = {module: set() for module in layout.modules}
    cells: Counter[tuple[str, str, str]] = Counter()
    reader = CanonicalGzipRows(stream, "the separately isolated balanced memory evidence")
    for row in reader:
        require(reader.count <= layout.spec.memory_rows, "the isolated memory evidence contains an extra record")
        require(row.get("schema") == MEMORY_ROW_SCHEMA, "an independent memory row uses a foreign schema")
        module = row.get("module")
        require(module in seen, "the memory worker measured a foreign engine")
        identifier = row.get("case")
        require(
            isinstance(identifier, str) and identifier in metadata and identifier not in seen[module],
            "the memory evidence repeated, omitted, or invented a measured case",
        )
        descriptor = (row.get("api"), row.get("workload"))
        require(descriptor == metadata[identifier], "a memory worker substituted a frozen case descriptor")
        require(
            row.get("locale") == "C"
            and row.get("correctness") is True
            and row.get("instrumentation_worker") is True
            and row.get("python_memory_is_native_memory") is False,
            "Python allocation tracing ran in a timing worker or was described as native allocation",
        )
        for field in MEMORY_FIELDS:
            integer(row.get(field), f"independent memory field {field}")
        seen[module].add(identifier)
        cells[(module, descriptor[0], descriptor[1])] += 1
    require(reader.count == layout.spec.memory_rows, "the independent memory evidence denominator is incomplete")
    require(reader.digest.hexdigest() == expected_digest, "the independently recorded memory fingerprint changed")
    baseline = seen["re"]
    require(len(baseline) == layout.spec.memory_cases, "Python did not measure every balanced memory case")
    for module in layout.modules:
        require(seen[module] == baseline, f"{module} measured different cases from the Python memory worker")
        require(
            all(cells[(module, api, workload)] == layout.spec.memory_per_cell for api in APIS for workload in WORKLOADS),
            f"{module} changed the independently balanced memory-cell denominator",
        )
    return {
        "rows": reader.count,
        "cases_per_engine": layout.spec.memory_cases,
        "cases_per_cell": layout.spec.memory_per_cell,
        "uncompressed_rows_sha256": reader.digest.hexdigest(),
        "python_memory": "tracemalloc-python-allocations-only",
        "process_memory": "whole-process-resident-bytes",
        "native_allocator_memory": "NOT MEASURED",
    }


def audit_streams(
    manifest: Mapping[str, Any],
    summary: Mapping[str, Any],
    timing_stream: BinaryIO,
    memory_stream: BinaryIO,
    freeze: Mapping[str, Any],
    freeze_digest: str,
    audit: Mapping[str, Any],
    audit_digest: str,
    artifact_digests: Mapping[str, str],
    source_digest: str,
    *,
    spec: ReplaySpec,
) -> dict[str, Any]:
    layout = validate_manifest(manifest, spec, source_digest)
    validate_summary_header(summary, layout)
    validate_live_provenance(
        summary, layout, freeze, freeze_digest, audit, audit_digest, artifact_digests
    )
    blocks, metadata, order = summary_case_blocks(summary, layout)
    result = replay_timing(timing_stream, summary, layout, blocks, metadata, order)
    memory = replay_memory(memory_stream, summary, layout, metadata)
    return {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "synthetic_only": spec.synthetic,
        "python": "3.14.6",
        "modules": list(layout.modules),
        "candidate_count": len(layout.modules) - 1,
        "cases_per_candidate": spec.case_count,
        "workload_cells": len(spec.descriptors),
        "cases_per_cell": spec.cases_per_cell,
        "paired_rounds": PAIR_ROUNDS,
        "operations_per_sample": OPERATIONS_PER_SAMPLE,
        "timing_rows": spec.timing_rows,
        "correctness_snapshots": spec.correctness_snapshots,
        "overall_bootstrap_draws": BOOTSTRAP_DRAWS,
        "minimum_significant_wins": spec.minimum_wins,
        "protocol_source_sha256": source_digest,
        "manifest_sha256": layout.digest,
        "protocol_binding_sha256": layout.binding,
        "candidate_freeze_sha256": freeze_digest,
        "from_scratch_audit_sha256": audit_digest,
        "raw_uncompressed_sha256": summary["raw"]["uncompressed_rows_sha256"],
        "memory": memory,
        "rankings": [result[module] for module in layout.modules[1:]],
        "previous_holdout_accessed": False,
        "opening_read": False,
        "hidden_cases_generated": 0,
        "candidate_imported": False,
        "timing_performed": False,
        "failed": 0,
    }


def synthetic_digest(label: str) -> str:
    return hashlib.sha256(f"v9-results-audit-public-synthetic:{label}".encode("ascii")).hexdigest()


def compressed_rows(rows: list[dict[str, Any]]) -> tuple[bytes, str]:
    stream = io.BytesIO()
    digest = hashlib.sha256()
    with gzip.GzipFile(filename="", fileobj=stream, mode="wb", compresslevel=6, mtime=0) as archive:
        for row in rows:
            line = canonical_bytes(row) + b"\n"
            archive.write(line)
            digest.update(line)
    return stream.getvalue(), digest.hexdigest()


def synthetic_manifest(spec: ReplaySpec, source_digest: str) -> dict[str, Any]:
    document: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "state": "prospectively-sealed-not-materialized",
        "source": {"path": "tools/rust_v9_holdout_protocol.py", "sha256": source_digest},
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
            "opening_sha256": synthetic_digest("no-final-opening"),
        },
        "layout": {
            "apis": list(APIS),
            "workloads": list(WORKLOADS),
            "cases": spec.case_count,
            "cases_per_api": spec.cases_per_api,
            "cases_per_cell": spec.cases_per_cell,
            "applicability": {api: {"synthetic_only": True} for api in APIS},
        },
        "trials": {
            "minimum_candidates": 3,
            "required_independent_native_families": ["vm", "rust", "zig"],
            "paired_rounds": PAIR_ROUNDS,
            "warmups": WARMUPS,
            "operations_per_sample": OPERATIONS_PER_SAMPLE,
            "order_seed": ORDER_SEED,
            "order_method": "seeded-counterbalanced-rotating-latin-square",
            "four_engine_timed_rows": spec.timing_rows,
            "four_engine_correctness_snapshots": spec.correctness_snapshots,
        },
        "statistics": {
            "confidence": 0.95,
            "case_method": "paired-log-student-t-df30",
            "case_student_t_critical": STUDENT_T_DF30_975,
            "minimum_significant_wins": spec.minimum_wins,
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
            "cases": spec.memory_cases,
            "cases_per_cell": spec.memory_per_cell,
            "python_peak": "tracemalloc-python-allocations-only",
            "process_current": "procfs-resident-bytes",
            "process_peak": "whole-process-peak-resident-bytes",
        },
        "history": {"v9_results": "NOT MEASURED", "combined_results": "NOT MEASURED"},
    }
    document["binding_sha256"] = canonical_digest(document)
    return document


def synthetic_elapsed(module: str, workload_index: int) -> int:
    if workload_index == 0:
        return 15_000 if module != "re" else 12_000
    if workload_index == 1:
        return 14_400 if module != "re" else 12_000
    if module == "re":
        return 12_000
    if module == "candidates.vm_candidate":
        return 6_000
    if module == "candidates.rust_candidate":
        return 10_000
    return 10_000 if workload_index < 4 else 12_500


def synthetic_artifacts() -> tuple[list[dict[str, Any]], dict[str, str]]:
    records: list[dict[str, Any]] = []
    digests: dict[str, str] = {}
    for module in MODULES[1:]:
        slug = module.rsplit(".", 1)[-1]
        artifacts = {}
        for role in sorted(ARTIFACT_ROLES[module]):
            path = f"candidates/{slug}.py" if role == "public-python" else f"candidates/public-synthetic-v9/{slug}/{role}"
            digest = synthetic_digest(f"{module}:{role}")
            artifacts[role] = {"path": path, "sha256": digest}
            digests[path] = digest
        records.append(
            {
                "module": module,
                "edge_sha256": synthetic_digest(f"{module}:edge"),
                "campaign_sha256": synthetic_digest(f"{module}:campaign"),
                "deep_contract_sha256": synthetic_digest(f"{module}:deep"),
                "artifacts": artifacts,
            }
        )
    return records, digests


def synthetic_inputs() -> dict[str, Any]:
    spec = SYNTHETIC_SPEC
    source_digest = synthetic_digest("public-v9-protocol-source")
    manifest = synthetic_manifest(spec, source_digest)
    audit = {
        "schema_version": 1,
        "audit": "bounded-from-scratch-engine-provenance",
        "passed": True,
        "result": "PASS",
        "minimum_required_independent_families": 3,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 3,
        "scope": {
            "holdout_or_case_fixture_access": False,
            "benchmark_or_timing_executed": False,
            "mapped_binaries_hashed_against_static_elf": True,
        },
    }
    audit_digest = hashlib.sha256(canonical_bytes(audit) + b"\n").hexdigest()
    frozen_candidates, artifact_digests = synthetic_artifacts()
    freeze = {
        "schema": FREEZE_SCHEMA,
        "protocol_binding_sha256": manifest["binding_sha256"],
        "stopping_commit": synthetic_digest("immutable-synthetic-stop"),
        "baseline": "re",
        "from_scratch_audit_sha256": audit_digest,
        "candidates": frozen_candidates,
        "opening_read": False,
        "hidden_cases_generated": 0,
        "performance_measured": False,
    }
    freeze_digest = hashlib.sha256(canonical_bytes(freeze) + b"\n").hexdigest()
    timing: list[dict[str, Any]] = []
    memory: list[dict[str, Any]] = []
    per_candidate: dict[str, list[dict[str, Any]]] = {module: [] for module in MODULES[1:]}
    cells: dict[str, dict[tuple[str, str], list[float]]] = {
        module: {descriptor: [] for descriptor in spec.descriptors}
        for module in MODULES[1:]
    }
    for api_index, api in enumerate(APIS):
        for workload_index, workload in enumerate(WORKLOADS):
            for case_index in range(spec.cases_per_cell):
                identifier = f"synthetic.v9.audit.{api_index:02d}.{workload_index:02d}.{case_index:03d}"
                for round_index in range(PAIR_ROUNDS):
                    order = counterbalanced_order(MODULES, identifier, round_index)
                    for position, module in enumerate(order):
                        elapsed = synthetic_elapsed(module, workload_index)
                        timing.append(
                            {
                                "schema": TIMING_ROW_SCHEMA,
                                "case": identifier,
                                "api": api,
                                "workload": workload,
                                "round": round_index,
                                "module": module,
                                "position": position,
                                "operations": OPERATIONS_PER_SAMPLE,
                                "elapsed_ns": elapsed,
                                "ns_per_op": elapsed / OPERATIONS_PER_SAMPLE,
                                "locale": "C",
                                "correctness_pre": True,
                                "correctness_timed": True,
                                "correctness_post": True,
                            }
                        )
                for module in MODULES[1:]:
                    value = math.log(synthetic_elapsed("re", workload_index) / synthetic_elapsed(module, workload_index))
                    logs = [value] * PAIR_ROUNDS
                    speed = math.exp(statistics.fmean(logs))
                    low, high = case_confidence(logs)
                    per_candidate[module].append(
                        {
                            "case": identifier,
                            "api": api,
                            "workload": workload,
                            "paired_rounds": PAIR_ROUNDS,
                            "operations_per_sample": OPERATIONS_PER_SAMPLE,
                            "speedup": speed,
                            "confidence_low": low,
                            "confidence_high": high,
                            "statistically_faster": low > 1.0,
                            "runtime_regression_over_20_percent": is_runtime_regression(speed),
                        }
                    )
                    cells[module][(api, workload)].append(value)
                if case_index < spec.memory_per_cell:
                    for module_index, module in enumerate(MODULES):
                        memory.append(
                            {
                                "schema": MEMORY_ROW_SCHEMA,
                                "case": identifier,
                                "api": api,
                                "workload": workload,
                                "module": module,
                                "locale": "C",
                                "python_current_bytes": 0 if workload_index == 0 else 40 + module_index,
                                "python_peak_bytes": 0 if workload_index == 0 else 100 + module_index,
                                "process_current_before_bytes": 30_000_000 + module_index * 1_000,
                                "process_current_after_bytes": 30_001_000 + module_index * 1_000,
                                "process_peak_bytes": 32_000_000 + module_index * 1_000,
                                "python_memory_is_native_memory": False,
                                "instrumentation_worker": True,
                                "correctness": True,
                            }
                        )
    raw_bytes, raw_digest = compressed_rows(timing)
    memory_bytes, memory_digest = compressed_rows(memory)
    rankings: list[dict[str, Any]] = []
    for module_index, module in enumerate(MODULES[1:]):
        rows = per_candidate[module]
        flattened = [
            value
            for api in APIS
            for workload in WORKLOADS
            for value in cells[module][(api, workload)]
        ]
        point = math.exp(statistics.fmean(flattened))
        low, high = stratified_bootstrap(cells[module], spec, BOOTSTRAP_SEED + module_index)
        regressions = [row for row in rows if row["runtime_regression_over_20_percent"]]
        wins = sum(row["statistically_faster"] for row in rows)
        rankings.append(
            {
                "module": module,
                "cases": spec.case_count,
                "geomean_speedup": point,
                "confidence_low": low,
                "confidence_high": high,
                "bootstrap_draws": BOOTSTRAP_DRAWS,
                "statistically_faster_cases": wins,
                "minimum_statistically_faster_cases": spec.minimum_wins,
                "regression_count": len(regressions),
                "regressions": regressions,
                "case_results": rows,
                "meets_speed_requirement": low >= 1.5,
                "meets_case_requirement": wins >= spec.minimum_wins,
                "success": low >= 1.5 and wins >= spec.minimum_wins,
            }
        )
    summary = {
        "schema": SUMMARY_SCHEMA,
        "protocol_binding_sha256": manifest["binding_sha256"],
        "manifest_sha256": canonical_digest(manifest),
        "candidate_freeze": {
            "document": freeze,
            "path": "performance/v9/evidence/public-synthetic-never-created-freeze.json",
            "sha256": freeze_digest,
        },
        "from_scratch_audit": {
            "path": "candidates/audits/public-synthetic-never-created.json",
            "sha256": audit_digest,
            "owned_native_artifacts": 5,
            "distinct_pipelines": 3,
        },
        "python": "3.14.6",
        "locale": "C",
        "modules": list(MODULES),
        "cases": spec.case_count,
        "paired_rounds": PAIR_ROUNDS,
        "operations_per_sample": OPERATIONS_PER_SAMPLE,
        "warmups": WARMUPS,
        "overall_bootstrap_draws": BOOTSTRAP_DRAWS,
        "correctness_snapshots": spec.correctness_snapshots,
        "cold_process_startup": [
            {
                "module": module,
                "elapsed_ns": 100 + index,
                "included_in_main_speedup": False,
                "definition": "isolated-process-start-import-and-current-native-proof",
            }
            for index, module in enumerate(MODULES)
        ],
        "raw": {
            "path": "performance/v9/evidence/public-synthetic-never-created-raw.jsonl.gz",
            "rows": spec.timing_rows,
            "operations_per_row": OPERATIONS_PER_SAMPLE,
            "uncompressed_rows_sha256": raw_digest,
        },
        "memory": {
            "path": "performance/v9/evidence/public-synthetic-never-created-memory.jsonl.gz",
            "rows": spec.memory_rows,
            "cases_per_module": spec.memory_cases,
            "uncompressed_rows_sha256": memory_digest,
            "python_peak_definition": "tracemalloc-python-allocations-only",
            "process_peak_definition": "whole-process-peak-rss-bytes",
        },
        "results": rankings,
        "opening_sha256": manifest["seal"]["opening_sha256"],
        "original_holdout_accessed": False,
        "v8_holdout_accessed": False,
        "original_v7_cases": 10_312,
        "combined_results": "NOT MEASURED",
        "failed": 0,
    }
    return {
        "manifest": manifest,
        "summary": summary,
        "raw": raw_bytes,
        "memory": memory_bytes,
        "freeze": freeze,
        "freeze_digest": freeze_digest,
        "audit": audit,
        "audit_digest": audit_digest,
        "artifact_digests": artifact_digests,
        "source_digest": source_digest,
    }


def replay_fixture(fixture: Mapping[str, Any], spec: ReplaySpec) -> dict[str, Any]:
    return audit_streams(
        fixture["manifest"],
        fixture["summary"],
        io.BytesIO(fixture["raw"]),
        io.BytesIO(fixture["memory"]),
        fixture["freeze"],
        fixture["freeze_digest"],
        fixture["audit"],
        fixture["audit_digest"],
        fixture["artifact_digests"],
        fixture["source_digest"],
        spec=spec,
    )


def copy_fixture(fixture: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(fixture)
    result["manifest"] = copy.deepcopy(fixture["manifest"])
    result["summary"] = copy.deepcopy(fixture["summary"])
    result["freeze"] = copy.deepcopy(fixture["freeze"])
    result["audit"] = copy.deepcopy(fixture["audit"])
    result["artifact_digests"] = dict(fixture["artifact_digests"])
    return result


def replace_evidence_row(blob: bytes, index: int, mutation: Callable[[dict[str, Any]], None]) -> tuple[bytes, str]:
    expanded = gzip.decompress(blob)
    lines = expanded.splitlines()
    require(0 <= index < len(lines), "a synthetic poison selects an invalid evidence row")
    row = json.loads(lines[index])
    require(isinstance(row, dict), "a synthetic evidence row is invalid")
    mutation(row)
    lines[index] = canonical_bytes(row)
    payload = b"\n".join(lines) + b"\n"
    stream = io.BytesIO()
    with gzip.GzipFile(filename="", fileobj=stream, mode="wb", compresslevel=6, mtime=0) as archive:
        archive.write(payload)
    return stream.getvalue(), hashlib.sha256(payload).hexdigest()


def expect_rejection(name: str, action: Callable[[], Any]) -> dict[str, Any]:
    try:
        action()
    except (ValueError, TypeError, KeyError, OverflowError, EOFError, zlib.error, OSError):
        return {"name": name, "passed": True}
    raise ValueError(f"the public-only results auditor accepted synthetic poison: {name}")


def public_self_test() -> dict[str, Any]:
    attempts = {"files_read": 0, "files_written": 0, "processes_started": 0}

    def deny_read(*_args: Any, **_kwargs: Any) -> Any:
        attempts["files_read"] += 1
        raise ValueError("public synthetic replay must never read an actual file")

    def deny_write(*_args: Any, **_kwargs: Any) -> Any:
        attempts["files_written"] += 1
        raise ValueError("public synthetic replay must never create an actual file")

    def deny_process(*_args: Any, **_kwargs: Any) -> Any:
        attempts["processes_started"] += 1
        raise ValueError("public synthetic replay must never start a candidate or benchmark")

    with (
        mock.patch.object(builtins, "open", side_effect=deny_read),
        mock.patch.object(Path, "open", side_effect=deny_read),
        mock.patch.object(Path, "read_bytes", side_effect=deny_read),
        mock.patch.object(Path, "read_text", side_effect=deny_read),
        mock.patch.object(Path, "write_bytes", side_effect=deny_write),
        mock.patch.object(Path, "write_text", side_effect=deny_write),
        mock.patch.object(Path, "mkdir", side_effect=deny_write),
        mock.patch.object(gzip, "open", side_effect=deny_read),
        mock.patch.object(subprocess, "run", side_effect=deny_process),
        mock.patch.object(subprocess, "Popen", side_effect=deny_process),
    ):
        fixture = synthetic_inputs()
        observed = replay_fixture(fixture, SYNTHETIC_SPEC)
        require(observed["status"] == "PASS" and observed["synthetic_only"] is True, "complete synthetic replay failed")
        require(
            REAL_SPEC.case_count == 24_576
            and len(REAL_SPEC.descriptors) == 96
            and REAL_SPEC.cases_per_cell == 256
            and REAL_SPEC.cases_per_api == 2_048
            and REAL_SPEC.minimum_wins == 14_746
            and REAL_SPEC.timing_rows == 3_047_424
            and REAL_SPEC.correctness_snapshots == 9_142_272
            and REAL_SPEC.memory_cases == 1_536
            and REAL_SPEC.memory_rows == 6_144
            and PAIR_ROUNDS == 31
            and OPERATIONS_PER_SAMPLE == 16
            and BOOTSTRAP_DRAWS == 9_999,
            "an actual frozen v9 final denominator silently changed",
        )
        require(
            SYNTHETIC_SPEC.case_count == 384
            and SYNTHETIC_SPEC.timing_rows == 47_616
            and SYNTHETIC_SPEC.memory_rows == 384,
            "the tiny complete public synthetic grid changed",
        )
        require(
            any(row["success"] for row in observed["rankings"])
            and any(not row["success"] for row in observed["rankings"]),
            "synthetic replay does not exercise passing and failing success boundaries",
        )
        checks: list[dict[str, Any]] = []

        for name, speedup, expected in (
            ("strict-regression-exact-five-sixths-is-not-a-loss", REGRESSION_THRESHOLD, False),
            (
                "strict-regression-one-ulp-below-five-sixths-is-a-loss",
                math.nextafter(REGRESSION_THRESHOLD, 0.0),
                True,
            ),
            (
                "strict-regression-one-ulp-above-five-sixths-is-not-a-loss",
                math.nextafter(REGRESSION_THRESHOLD, math.inf),
                False,
            ),
        ):
            require(
                is_runtime_regression(speedup) is expected,
                f"the public-only results auditor changed the exact regression boundary: {name}",
            )
            checks.append({"name": name, "passed": True})

        def reject_fixture(name: str, mutation: Callable[[dict[str, Any]], None]) -> None:
            def action() -> None:
                changed = copy_fixture(fixture)
                mutation(changed)
                replay_fixture(changed, SYNTHETIC_SPEC)

            checks.append(expect_rejection(name, action))

        poisons: tuple[tuple[str, Callable[[dict[str, Any]], None]], ...] = (
            ("wrong-public-manifest-schema", lambda value: value["manifest"].update(schema="rebar-v8-invalid")),
            ("wrong-final-summary-schema", lambda value: value["summary"].update(schema="rebar-v8-invalid")),
            ("wrong-public-protocol-source", lambda value: value["manifest"]["source"].update(sha256="0" * 64)),
            ("wrong-immutable-objective", lambda value: value["manifest"]["correctness"].update(goal_sha256="0" * 64)),
            ("changed-public-manifest-binding", lambda value: value["manifest"].update(binding_sha256="0" * 64)),
            ("changed-final-manifest-digest", lambda value: value["summary"].update(manifest_sha256="0" * 64)),
            ("changed-final-protocol-binding", lambda value: value["summary"].update(protocol_binding_sha256="0" * 64)),
            ("changed-blinded-opening-commitment", lambda value: value["summary"].update(opening_sha256="0" * 64)),
            ("changed-pinned-python", lambda value: value["summary"].update(python="3.13.0")),
            ("changed-isolated-locale", lambda value: value["summary"].update(locale="POSIX")),
            ("concealed-final-failure", lambda value: value["summary"].update(failed=1)),
            ("previous-original-holdout-opened", lambda value: value["summary"].update(original_holdout_accessed=True)),
            ("previous-v8-holdout-opened", lambda value: value["summary"].update(v8_holdout_accessed=True)),
            ("invented-combined-final-result", lambda value: value["summary"].update(combined_results="MEASURED")),
            ("substituted-python-baseline", lambda value: value["summary"]["modules"].__setitem__(0, "not.re")),
            ("missing-independent-candidate", lambda value: value["summary"]["modules"].pop()),
            ("duplicate-independent-candidate", lambda value: value["summary"]["modules"].__setitem__(2, value["summary"]["modules"][1])),
            ("changed-complete-case-denominator", lambda value: value["summary"].update(cases=SYNTHETIC_SPEC.case_count - 1)),
            ("changed-31-round-denominator", lambda value: value["summary"].update(paired_rounds=PAIR_ROUNDS - 1)),
            ("changed-16-operation-denominator", lambda value: value["summary"].update(operations_per_sample=OPERATIONS_PER_SAMPLE - 1)),
            ("changed-9999-bootstrap-denominator", lambda value: value["summary"].update(overall_bootstrap_draws=BOOTSTRAP_DRAWS - 1)),
            ("dropped-pre-timing-post-correctness", lambda value: value["summary"].update(correctness_snapshots=SYNTHETIC_SPEC.correctness_snapshots - 1)),
            ("dropped-paired-raw-row-denominator", lambda value: value["summary"]["raw"].update(rows=SYNTHETIC_SPEC.timing_rows - 1)),
            ("changed-paired-raw-operation-denominator", lambda value: value["summary"]["raw"].update(operations_per_row=OPERATIONS_PER_SAMPLE - 1)),
            ("changed-canonical-raw-digest", lambda value: value["summary"]["raw"].update(uncompressed_rows_sha256="0" * 64)),
            ("missing-cold-engine-startup", lambda value: value["summary"]["cold_process_startup"].pop()),
            ("zero-duration-cold-engine-startup", lambda value: value["summary"]["cold_process_startup"][0].update(elapsed_ns=0)),
            ("duplicate-cold-engine-startup", lambda value: value["summary"]["cold_process_startup"].__setitem__(1, copy.deepcopy(value["summary"]["cold_process_startup"][0]))),
            ("cold-engine-startup-hidden-inside-main-speedup", lambda value: value["summary"]["cold_process_startup"][0].update(included_in_main_speedup=True)),
            ("dropped-candidate-result-block", lambda value: value["summary"]["results"].pop()),
            ("duplicate-candidate-result-block", lambda value: value["summary"]["results"].__setitem__(1, copy.deepcopy(value["summary"]["results"][0]))),
            ("changed-candidate-case-denominator", lambda value: value["summary"]["results"][0].update(cases=SYNTHETIC_SPEC.case_count - 1)),
            ("partial-candidate-bootstrap", lambda value: value["summary"]["results"][0].update(bootstrap_draws=BOOTSTRAP_DRAWS - 1)),
            ("weakened-significant-win-target", lambda value: value["summary"]["results"][0].update(minimum_statistically_faster_cases=SYNTHETIC_SPEC.minimum_wins - 1)),
            ("dropped-candidate-case", lambda value: value["summary"]["results"][0]["case_results"].pop()),
            ("duplicated-candidate-case", lambda value: value["summary"]["results"][0]["case_results"].__setitem__(1, copy.deepcopy(value["summary"]["results"][0]["case_results"][0]))),
            ("changed-candidate-case-order", lambda value: value["summary"]["results"][1]["case_results"].reverse()),
            ("changed-public-case-descriptor", lambda value: value["summary"]["results"][0]["case_results"][0].update(workload="foreign-workload")),
            ("wrong-case-paired-rounds", lambda value: value["summary"]["results"][0]["case_results"][0].update(paired_rounds=30)),
            ("wrong-case-operation-count", lambda value: value["summary"]["results"][0]["case_results"][0].update(operations_per_sample=15)),
            ("nonfinite-case-speed", lambda value: value["summary"]["results"][0]["case_results"][0].update(speedup=float("nan"))),
            ("nonpositive-case-speed", lambda value: value["summary"]["results"][0]["case_results"][0].update(speedup=0.0)),
            ("poisoned-case-confidence", lambda value: value["summary"]["results"][0]["case_results"][0].update(confidence_low=3.0)),
            ("false-case-confidence-win", lambda value: value["summary"]["results"][0]["case_results"][0].update(statistically_faster=True)),
            ("false-strict-runtime-regression", lambda value: value["summary"]["results"][0]["case_results"][0].update(runtime_regression_over_20_percent=False)),
            ("poisoned-overall-geometric-mean", lambda value: value["summary"]["results"][0].update(geomean_speedup=value["summary"]["results"][0]["geomean_speedup"] * 1.01)),
            ("plausible-but-forged-bootstrap-lower-bound", lambda value: value["summary"]["results"][0].update(confidence_low=value["summary"]["results"][0]["geomean_speedup"] * 0.99)),
            ("plausible-but-forged-bootstrap-upper-bound", lambda value: value["summary"]["results"][0].update(confidence_high=value["summary"]["results"][0]["geomean_speedup"] * 1.01)),
            ("hidden-confidence-qualified-win", lambda value: value["summary"]["results"][0].update(statistically_faster_cases=value["summary"]["results"][0]["statistically_faster_cases"] - 1)),
            ("hidden-large-runtime-regression", lambda value: value["summary"]["results"][0].update(regression_count=value["summary"]["results"][0]["regression_count"] - 1)),
            ("dropped-case-level-runtime-regression", lambda value: value["summary"]["results"][0]["regressions"].pop()),
            ("duplicated-case-level-runtime-regression", lambda value: value["summary"]["results"][0]["regressions"].append(copy.deepcopy(value["summary"]["results"][0]["regressions"][0]))),
            ("false-overall-confidence-success", lambda value: value["summary"]["results"][0].update(meets_speed_requirement=not value["summary"]["results"][0]["meets_speed_requirement"])),
            ("false-case-frequency-success", lambda value: value["summary"]["results"][0].update(meets_case_requirement=not value["summary"]["results"][0]["meets_case_requirement"])),
            ("false-final-winning-candidate", lambda value: value["summary"]["results"][0].update(success=not value["summary"]["results"][0]["success"])),
            ("changed-candidate-freeze", lambda value: value.update(freeze_digest="0" * 64)),
            ("changed-audit-evidence", lambda value: value.update(audit_digest="0" * 64)),
            ("changed-independent-native-artifact", lambda value: value["artifact_digests"].__setitem__(next(iter(value["artifact_digests"])), "0" * 64)),
            ("incomplete-independent-memory-denominator", lambda value: value["summary"]["memory"].update(rows=SYNTHETIC_SPEC.memory_rows - 1)),
            ("changed-memory-cases-per-engine", lambda value: value["summary"]["memory"].update(cases_per_module=SYNTHETIC_SPEC.memory_cases - 1)),
            ("poisoned-independent-memory-digest", lambda value: value["summary"]["memory"].update(uncompressed_rows_sha256="0" * 64)),
            ("python-memory-falsely-called-native", lambda value: value["summary"]["memory"].update(python_peak_definition="native-allocator")),
            ("process-rss-falsely-called-native", lambda value: value["summary"]["memory"].update(process_peak_definition="native-allocator")),
        )
        for name, mutation in poisons:
            reject_fixture(name, mutation)

        def poison_raw(name: str, mutation: Callable[[dict[str, Any]], None], *, index: int = 0) -> None:
            def action() -> None:
                changed = copy_fixture(fixture)
                blob, digest = replace_evidence_row(changed["raw"], index, mutation)
                changed["raw"] = blob
                changed["summary"]["raw"]["uncompressed_rows_sha256"] = digest
                replay_fixture(changed, SYNTHETIC_SPEC)

            checks.append(expect_rejection(name, action))

        for name, mutation in (
            ("raw-row-wrong-schema", lambda row: row.update(schema="foreign-v8-row")),
            ("raw-row-foreign-case", lambda row: row.update(case="synthetic.v9.audit.foreign")),
            ("raw-row-foreign-operation", lambda row: row.update(api="foreign-operation")),
            ("raw-row-foreign-workload", lambda row: row.update(workload="foreign-workload")),
            ("raw-row-foreign-engine", lambda row: row.update(module="candidates.ast_candidate")),
            ("raw-row-wrong-round", lambda row: row.update(round=30)),
            ("raw-row-wrong-counterbalanced-position", lambda row: row.update(position=3)),
            ("raw-row-wrong-operation-count", lambda row: row.update(operations=15)),
            ("raw-row-nonpositive-timing", lambda row: row.update(elapsed_ns=0)),
            ("raw-row-poisoned-nanoseconds-per-operation", lambda row: row.update(ns_per_op=1.0)),
            ("raw-row-wrong-locale", lambda row: row.update(locale="POSIX")),
            ("raw-row-missing-pre-correctness", lambda row: row.update(correctness_pre=False)),
            ("raw-row-missing-timed-correctness", lambda row: row.update(correctness_timed=False)),
            ("raw-row-missing-post-correctness", lambda row: row.update(correctness_post=False)),
        ):
            poison_raw(name, mutation)

        def poison_memory(name: str, mutation: Callable[[dict[str, Any]], None]) -> None:
            def action() -> None:
                changed = copy_fixture(fixture)
                blob, digest = replace_evidence_row(changed["memory"], 0, mutation)
                changed["memory"] = blob
                changed["summary"]["memory"]["uncompressed_rows_sha256"] = digest
                replay_fixture(changed, SYNTHETIC_SPEC)

            checks.append(expect_rejection(name, action))

        for name, mutation in (
            ("memory-row-wrong-schema", lambda row: row.update(schema="foreign-memory-row")),
            ("memory-row-foreign-engine", lambda row: row.update(module="candidates.ast_candidate")),
            ("memory-row-foreign-case", lambda row: row.update(case="synthetic.v9.audit.foreign")),
            ("memory-row-wrong-workload", lambda row: row.update(workload="foreign-workload")),
            ("memory-row-wrong-locale", lambda row: row.update(locale="POSIX")),
            ("memory-row-negative-python-allocation", lambda row: row.update(python_peak_bytes=-1)),
            ("memory-row-negative-process-rss", lambda row: row.update(process_peak_bytes=-1)),
            ("memory-row-falsely-claims-native-allocator", lambda row: row.update(python_memory_is_native_memory=True)),
            ("memory-row-runs-in-timing-worker", lambda row: row.update(instrumentation_worker=False)),
            ("memory-row-fails-python-correctness", lambda row: row.update(correctness=False)),
        ):
            poison_memory(name, mutation)

        def truncated_stream(kind: str) -> None:
            changed = copy_fixture(fixture)
            blob = changed[kind]
            changed[kind] = blob[:-1]
            replay_fixture(changed, SYNTHETIC_SPEC)

        checks.append(expect_rejection("truncated-canonical-timing-gzip", lambda: truncated_stream("raw")))
        checks.append(expect_rejection("truncated-canonical-memory-gzip", lambda: truncated_stream("memory")))
        checks.append(
            expect_rejection(
                "synthetic-replay-rejected-as-real-24576-results",
                lambda: replay_fixture(fixture, REAL_SPEC),
            )
        )
        require(
            len(checks) >= 40
            and len({row["name"] for row in checks}) == len(checks)
            and all(row["passed"] is True for row in checks),
            "a public synthetic results-audit poison was accepted or duplicated",
        )
        require(
            attempts == {"files_read": 0, "files_written": 0, "processes_started": 0},
            "public-only replay opened a file or executed an actual candidate",
        )
        return {
            "schema": SELF_TEST_SCHEMA,
            "status": "PASS",
            "synthetic_only": True,
            "files_read": 0,
            "files_written": 0,
            "processes_started": 0,
            "candidate_imported": False,
            "opening_read": False,
            "hidden_cases_generated": 0,
            "previous_holdout_accessed": False,
            "timing_performed": False,
            "real_cases_per_candidate": REAL_SPEC.case_count,
            "real_workload_cells": len(REAL_SPEC.descriptors),
            "real_cases_per_cell": REAL_SPEC.cases_per_cell,
            "real_timing_rows": REAL_SPEC.timing_rows,
            "real_correctness_snapshots": REAL_SPEC.correctness_snapshots,
            "real_memory_rows": REAL_SPEC.memory_rows,
            "real_minimum_significant_wins": REAL_SPEC.minimum_wins,
            "paired_rounds": PAIR_ROUNDS,
            "operations_per_sample": OPERATIONS_PER_SAMPLE,
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "synthetic_cases_per_cell": SYNTHETIC_SPEC.cases_per_cell,
            "synthetic_cases_per_candidate": SYNTHETIC_SPEC.case_count,
            "synthetic_timing_rows": SYNTHETIC_SPEC.timing_rows,
            "synthetic_memory_rows": SYNTHETIC_SPEC.memory_rows,
            "synthetic_engines": len(MODULES),
            "synthetic_candidate_blocks": len(MODULES) - 1,
            "poison_control_count": len(checks),
            "poison_controls": checks,
            "failed": 0,
        }


def read_explicit_json(path: Path, label: str) -> tuple[dict[str, Any], str]:
    try:
        content = path.read_bytes()
        document = json.loads(content)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read explicitly supplied {label}") from error
    require(isinstance(document, dict), f"the explicitly supplied {label} is not a JSON object")
    return document, hashlib.sha256(content).hexdigest()


def explicit_evidence_path(path: Path, expected: str, label: str) -> Path:
    resolved = path.resolve()
    require(
        resolved == (ROOT / expected).resolve(),
        f"the explicitly supplied {label} does not match frozen final provenance",
    )
    return resolved


def collect_actual_artifact_digests(freeze: Mapping[str, Any]) -> dict[str, str]:
    entries = freeze.get("candidates")
    require(isinstance(entries, list), "the frozen native candidate list is absent")
    allowed_root = (ROOT / "candidates").resolve()
    measured: dict[str, str] = {}
    for entry in entries:
        require(isinstance(entry, dict) and isinstance(entry.get("artifacts"), dict), "invalid frozen production artifact")
        for record in entry["artifacts"].values():
            require(isinstance(record, dict), "invalid frozen production file identity")
            name = record.get("path")
            require(isinstance(name, str) and bool(name), "the frozen native production file has no path")
            resolved = (Path(name) if Path(name).is_absolute() else ROOT / name).resolve()
            require(resolved.is_relative_to(allowed_root), "the frozen native production file escapes candidates")
            try:
                with resolved.open("rb") as source:
                    digest = hashlib.file_digest(source, "sha256").hexdigest()
            except OSError as error:
                raise ValueError("cannot verify an explicitly frozen candidate production artifact") from error
            measured[name] = digest
    return measured


def write_exclusive(path: Path, payload: Mapping[str, Any], *, synthetic: bool) -> str:
    resolved = path.resolve()
    require(resolved.parent == EVIDENCE_ROOT.resolve(), "the explicitly supplied evidence output escapes v9 evidence")
    if synthetic:
        require(
            resolved.name.startswith("PERFORMANCE-RESULTS-AUDIT-PUBLIC-SYNTHETIC-SELF-TEST")
            and resolved.suffix == ".json",
            "synthetic results audit output must have its unique public-only evidence name",
        )
    content = json.dumps(payload, allow_nan=False, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    try:
        with resolved.open("x", encoding="utf-8", newline="\n") as destination:
            destination.write(content)
    except OSError as error:
        raise ValueError("cannot exclusively create the explicit new results-audit evidence") from error
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    test = commands.add_parser("self-test", help="run only a complete tiny, in-memory, domain-separated public synthetic replay")
    test.add_argument("--public-synthetic-only", action="store_true", required=True)
    test.add_argument("--output", type=Path, required=True)
    test.add_argument("--source-sha256", required=True)
    test.add_argument("--protocol-sha256", required=True)

    verify = commands.add_parser("verify", help="independently replay explicitly supplied, already-authorized actual final evidence")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--summary", type=Path, required=True)
    verify.add_argument("--raw", type=Path, required=True)
    verify.add_argument("--memory", type=Path, required=True)
    verify.add_argument("--candidate-freeze", type=Path, required=True)
    verify.add_argument("--from-scratch-audit", type=Path, required=True)
    verify.add_argument("--output", type=Path, required=True)

    args = parser.parse_args(argv)
    validate_pinned_python()
    if args.command == "self-test":
        source_digest = fingerprint(args.source_sha256, "the supplied public-only results auditor source")
        protocol_digest = fingerprint(args.protocol_sha256, "the supplied public v9 protocol source")
        observed = public_self_test()
        recorded = {
            "schema": "rebar-v9-recorded-public-synthetic-results-audit-v1",
            "execution_count": 1,
            "command_kind": "public-synthetic-only",
            "public_source": {
                "path": "tools/performance_v9_results_audit.py",
                "sha256": source_digest,
            },
            "public_protocol": {
                "path": "tools/rust_v9_holdout_protocol.py",
                "sha256": protocol_digest,
            },
            "result": observed,
        }
        evidence_digest = write_exclusive(args.output, recorded, synthetic=True)
        print(
            json.dumps(
                {
                    "schema": recorded["schema"],
                    "status": "PASS",
                    "path": str(args.output.resolve().relative_to(ROOT)),
                    "sha256": evidence_digest,
                    "source_sha256": source_digest,
                    "protocol_sha256": protocol_digest,
                    "poison_control_count": observed["poison_control_count"],
                    "failed": 0,
                    "files_read": 0,
                    "files_written_during_self_test": 0,
                    "candidate_imported": False,
                    "opening_read": False,
                    "hidden_cases_generated": 0,
                    "timing_performed": False,
                    "synthetic_only": True,
                },
                allow_nan=False,
                sort_keys=True,
            ),
            flush=True,
        )
        return 0

    manifest, _ = read_explicit_json(args.manifest, "frozen public v9 manifest")
    summary, summary_digest = read_explicit_json(args.summary, "completed v9 final results")
    freeze, freeze_digest = read_explicit_json(args.candidate_freeze, "frozen candidate selection")
    audit, audit_digest = read_explicit_json(args.from_scratch_audit, "from-scratch native audit")
    try:
        with PUBLIC_SOURCE.open("rb") as source:
            source_digest = hashlib.file_digest(source, "sha256").hexdigest()
    except OSError as error:
        raise ValueError("cannot verify the independently frozen public protocol source") from error
    raw_section = summary.get("raw")
    memory_section = summary.get("memory")
    require(isinstance(raw_section, dict) and isinstance(memory_section, dict), "actual final result evidence is missing")
    raw_path = explicit_evidence_path(args.raw, raw_section.get("path"), "canonical paired timing stream")
    memory_path = explicit_evidence_path(args.memory, memory_section.get("path"), "canonical isolated memory stream")
    wrapper = summary.get("candidate_freeze")
    require(isinstance(wrapper, dict), "the final candidate freeze provenance is absent")
    explicit_evidence_path(args.candidate_freeze, wrapper.get("path"), "candidate stopping freeze")
    reported_audit = summary.get("from_scratch_audit")
    require(isinstance(reported_audit, dict) and isinstance(reported_audit.get("path"), str), "native audit provenance is missing")
    explicit_evidence_path(args.from_scratch_audit, reported_audit["path"], "complete from-scratch native audit")
    digests = collect_actual_artifact_digests(freeze)
    try:
        with raw_path.open("rb") as timing_stream, memory_path.open("rb") as memory_stream:
            observed = audit_streams(
                manifest,
                summary,
                timing_stream,
                memory_stream,
                freeze,
                freeze_digest,
                audit,
                audit_digest,
                digests,
                source_digest,
                spec=REAL_SPEC,
            )
    except OSError as error:
        raise ValueError("cannot stream explicitly supplied actual final timing or memory evidence") from error
    observed["summary_sha256"] = summary_digest
    destination_digest = write_exclusive(args.output, observed, synthetic=False)
    print(json.dumps({"schema": AUDIT_SCHEMA, "status": "PASS", "path": str(args.output.resolve().relative_to(ROOT)), "sha256": destination_digest, "failed": 0}, allow_nan=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, TypeError, KeyError, OverflowError, OSError) as error:
        raise SystemExit(f"error: {error}") from error
