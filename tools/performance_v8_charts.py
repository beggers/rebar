#!/usr/bin/env python3
"""Render complete, prospective v8 final charts without opening the holdout.

This script never discovers an input, imports a benchmark, or opens raw
measurements, candidates, evidence, or a seed. Normal operation requires all
three explicitly supplied paths::

    python3.14 -B tools/performance_v8_charts.py \
        --manifest PUBLIC_MANIFEST.json --summary FINAL_SUMMARY.json \
        --prefix /explicit/output/v8-final

The public manifest contains commitments and the 12-by-8 public descriptor
layout, not individual held-out cases. Individual cases are accepted only from
an explicitly supplied, already-unsealed final summary. ``--self-test`` uses
exclusively synthetic, in-memory manifests and results and touches no files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal
from html import escape
from pathlib import Path
from typing import Any, Callable, Mapping
from xml.etree import ElementTree


MANIFEST_SCHEMA = "rebar-v8-prospective-performance-holdout-v1"
SUMMARY_SCHEMA = "rebar-v8-prospective-performance-summary-v1"
CASE_COUNT = 12_288
API_COUNT = 12
WORKLOAD_COUNT = 8
DESCRIPTOR_COUNT = API_COUNT * WORKLOAD_COUNT
CASES_PER_DESCRIPTOR = 128
CASES_PER_API = WORKLOAD_COUNT * CASES_PER_DESCRIPTOR
TRIAL_COUNT = 31
BOOTSTRAP_COUNT = 9_999
SIGNIFICANT_WIN_TARGET = 7_373
SLOWDOWN_THRESHOLD = 5 / 6

API_LABELS: dict[str, str] = {
    "compile": "Prepare a pattern",
    "escape": "Escape special characters",
    "findall": "Find every match",
    "finditer": "Stream each match",
    "fullmatch": "Match the entire input",
    "match": "Match at the beginning",
    "match-surface": "Read the match details",
    "scanner": "Scan repeated matches",
    "search": "Search for a match",
    "split": "Split around matches",
    "sub": "Replace matches",
    "subn": "Replace and count matches",
}

BLUE = "#175cd3"
GREEN = "#067647"
RED = "#b42318"
AMBER = "#a15c00"
GREY = "#475467"
PALE = "#f2f4f7"
INK = "#101828"
PROCESS_RATIO_FIELDS = (
    "peak_process_rss_ratio",
    "process_peak_rss_ratio",
    "process_rss_ratio",
    "peak_rss_ratio",
    "rss_ratio",
)
NATIVE_RATIO_FIELDS = (
    "native_peak_ratio",
    "peak_native_ratio",
    "native_memory_ratio",
    "native_allocator_ratio",
)


@dataclass(frozen=True)
class ManifestLayout:
    digest: str
    binding: str
    seed_commitment: str
    apis: tuple[str, ...]
    workloads: tuple[str, ...]
    descriptors: frozenset[tuple[str, str]]


@dataclass(frozen=True)
class MemoryMetric:
    field: str | None
    mode: str


@dataclass(frozen=True)
class CandidateResult:
    module: str
    label: str
    ranking: Mapping[str, Any]
    rows: tuple[Mapping[str, Any], ...]
    groups: Mapping[tuple[str, str], tuple[Mapping[str, Any], ...]]
    api_intervals: Mapping[str, tuple[float, float]]


@dataclass(frozen=True)
class FinalResult:
    manifest: ManifestLayout
    candidates: tuple[CandidateResult, ...]
    process_memory: MemoryMetric
    native_memory: MemoryMetric


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def finite(value: Any, label: str, *, positive: bool = True) -> float:
    require(
        isinstance(value, (int, float, Decimal)) and not isinstance(value, bool),
        f"{label} must be a finite number",
    )
    number = float(value)
    require(math.isfinite(number), f"{label} is not finite")
    require(number > 0 if positive else number >= 0, f"{label} is out of range")
    return number


def integer(value: Any, label: str) -> int:
    require(isinstance(value, int) and not isinstance(value, bool), f"{label} must be an integer")
    return value


def alias(
    payload: Mapping[str, Any],
    names: tuple[str, ...],
    label: str,
    *,
    required: bool = True,
) -> Any:
    supplied = [(name, payload[name]) for name in names if name in payload]
    if not supplied:
        require(not required, f"missing {label}")
        return None
    first = supplied[0][1]
    require(all(value == first for _name, value in supplied[1:]), f"conflicting {label}")
    return first


def count_alias(
    payload: Mapping[str, Any],
    names: tuple[str, ...],
    label: str,
    expected: int,
    *,
    required: bool = True,
) -> int:
    supplied: list[int] = []
    for name in names:
        if name not in payload:
            continue
        value = payload[name]
        if name in {"cases", "holdout_cases"} and isinstance(value, list):
            continue
        if name == "trials" and isinstance(value, dict):
            continue
        supplied.append(integer(value, f"{label} ({name})"))
    require(bool(supplied) or not required, f"missing {label}")
    if not supplied:
        return expected
    require(all(value == expected for value in supplied), f"incorrect {label}: expected {expected:,}")
    return expected


def object_section(payload: Mapping[str, Any], name: str, label: str) -> Mapping[str, Any] | None:
    if name not in payload:
        return None
    section = payload[name]
    require(isinstance(section, dict), f"{label} must be a JSON object")
    return section


def count_sources(
    sources: tuple[Mapping[str, Any], ...],
    names: tuple[str, ...],
    label: str,
    expected: int,
    *,
    required: bool = True,
) -> int:
    present = False
    for source in sources:
        if any(
            name in source
            and not (name in {"cases", "holdout_cases"} and isinstance(source[name], list))
            and not (name == "trials" and isinstance(source[name], dict))
            for name in names
        ):
            present = True
            count_alias(source, names, label, expected)
    require(present or not required, f"missing {label}")
    return expected


def sha256_value(value: Any, label: str) -> str:
    require(isinstance(value, str), f"missing {label}")
    if value.startswith("sha256:"):
        value = value[7:]
    require(
        len(value) == 64 and all(character in "0123456789abcdef" for character in value),
        f"{label} is not a lowercase SHA-256 commitment",
    )
    return value


def sha256_alias(
    payload: Mapping[str, Any], names: tuple[str, ...], label: str, *, required: bool = True
) -> str | None:
    supplied = [(name, sha256_value(payload[name], f"{label} ({name})")) for name in names if name in payload]
    if not supplied:
        require(not required, f"missing {label}")
        return None
    result = supplied[0][1]
    require(all(value == result for _name, value in supplied[1:]), f"conflicting {label}")
    return result


def sha256_sources(
    sources: tuple[Mapping[str, Any], ...],
    names: tuple[str, ...],
    label: str,
    *,
    required: bool = True,
) -> str | None:
    found: list[str] = []
    for source in sources:
        value = sha256_alias(source, names, label, required=False)
        if value is not None:
            found.append(value)
    require(bool(found) or not required, f"missing {label}")
    if not found:
        return None
    require(all(value == found[0] for value in found), f"conflicting {label}")
    return found[0]


def public_names(
    payload: Mapping[str, Any], names: tuple[str, ...], label: str, expected: int
) -> tuple[str, ...] | None:
    found: list[tuple[str, ...]] = []
    for name in names:
        if name not in payload:
            continue
        raw = payload[name]
        if isinstance(raw, dict):
            values = tuple(raw)
        elif isinstance(raw, list) and all(isinstance(value, str) for value in raw):
            values = tuple(raw)
        else:
            continue
        require(len(values) == expected, f"incorrect public {label} count")
        require(all(isinstance(value, str) and value.strip() == value and value for value in values), f"invalid public {label}")
        require(len(set(values)) == expected, f"duplicated public {label}")
        found.append(values)
    if not found:
        return None
    require(all(set(values) == set(found[0]) for values in found[1:]), f"conflicting public {label}")
    return found[0]


def descriptor_key(entry: Mapping[str, Any], label: str) -> tuple[str, str]:
    api = alias(entry, ("api", "operation", "public_operation"), f"{label} API")
    workload = alias(entry, ("workload", "category", "family", "workload_family"), f"{label} workload")
    require(isinstance(api, str) and bool(api), f"invalid {label} API")
    require(isinstance(workload, str) and bool(workload), f"invalid {label} workload")
    return api, workload


def descriptor_entries(payload: Mapping[str, Any]) -> dict[tuple[str, str], int] | None:
    found: list[dict[tuple[str, str], int]] = []
    for name in (
        "descriptors",
        "descriptor_counts",
        "public_descriptors",
        "workload_descriptors",
        "holdout_descriptors",
        "groups",
    ):
        if name not in payload:
            continue
        source = payload[name]
        entries: dict[tuple[str, str], int] = {}
        if isinstance(source, list):
            require(len(source) == DESCRIPTOR_COUNT, f"{name} must contain all 96 public descriptors, not held-out cases")
            for offset, raw in enumerate(source):
                require(isinstance(raw, dict), f"invalid public descriptor {name}[{offset}]")
                key = descriptor_key(raw, f"public descriptor {name}[{offset}]")
                count = count_alias(
                    raw,
                    ("cases", "case_count", "count", "holdout_cases", "examples", "cases_per_descriptor"),
                    f"public descriptor {name}[{offset}] case count",
                    CASES_PER_DESCRIPTOR,
                )
                require(key not in entries, f"duplicated public descriptor {key!r}")
                entries[key] = count
        elif isinstance(source, dict):
            for raw_api, workloads in source.items():
                require(isinstance(raw_api, str) and isinstance(workloads, dict), f"{name} must map public APIs to workload counts")
                for raw_workload, raw_count in workloads.items():
                    require(isinstance(raw_workload, str), f"invalid public workload in {name}")
                    key = (raw_api, raw_workload)
                    require(key not in entries, f"duplicated public descriptor {key!r}")
                    entries[key] = integer(raw_count, f"public descriptor {key!r} case count")
        else:
            raise ValueError(f"invalid public descriptor layout: {name}")
        require(len(entries) == DESCRIPTOR_COUNT, f"{name} omits a public descriptor")
        require(all(count == CASES_PER_DESCRIPTOR for count in entries.values()), f"{name} changed a 128-case public descriptor")
        found.append(entries)
    if not found:
        return None
    require(all(entries == found[0] for entries in found[1:]), "conflicting public descriptor layouts")
    return found[0]


def validate_manifest(payload: Mapping[str, Any], digest: str) -> ManifestLayout:
    require(isinstance(payload, dict), "the public manifest must be a JSON object")
    require(payload.get("schema") == MANIFEST_SCHEMA, "incorrect prospective v8 public-manifest schema")
    sha256_value(digest, "public manifest file digest")
    if "cohort" in payload:
        require(payload["cohort"] == "holdout", "the public manifest is not the held-out cohort")

    nested_layout = object_section(payload, "layout", "public manifest layout")
    layout = nested_layout if nested_layout is not None else payload
    nested_trials = object_section(payload, "trials", "public trial protocol") if isinstance(payload.get("trials"), dict) else None
    nested_statistics = object_section(payload, "statistics", "public statistics protocol")
    nested_seal = object_section(payload, "seal", "public holdout seal")
    layout_sources = (layout, payload) if nested_layout is not None else (payload,)
    trial_sources = (nested_trials, payload) if nested_trials is not None else (payload,)
    statistic_sources = (nested_statistics, payload) if nested_statistics is not None else (payload,)
    seal_sources = (nested_seal, payload) if nested_seal is not None else (payload,)

    # The frozen public file must remain blinded: it describes only 96 groups.
    for source in layout_sources:
        for forbidden in ("case_manifest", "case_definitions", "case_ids", "held_out_cases", "unsealed_cases"):
            require(forbidden not in source, f"the public manifest must not contain individual held-out cases ({forbidden})")
        for potentially_listed in ("cases", "holdout_cases"):
            if potentially_listed in source:
                require(not isinstance(source[potentially_listed], list), "the public manifest must not materialize held-out cases")

    count_sources(layout_sources, ("cases", "case_count", "holdout_cases", "holdout_case_count", "total_cases"), "public held-out case count", CASE_COUNT)
    count_sources(trial_sources, ("paired_rounds", "paired_trials", "trial_count", "trials"), "paired trial count", TRIAL_COUNT)
    count_sources(statistic_sources, ("overall_bootstrap_draws", "bootstrap_resamples", "bootstrap_samples", "bootstrap_replicates", "bootstrap_iterations"), "bootstrap resample count", BOOTSTRAP_COUNT)
    count_sources(layout_sources, ("api_count", "public_api_count", "operation_count"), "public API count", API_COUNT, required=False)
    count_sources(layout_sources, ("workload_count", "workloads_per_api", "categories_per_api", "families_per_api"), "public workloads per API", WORKLOAD_COUNT, required=False)
    count_sources(layout_sources, ("descriptor_count", "group_count", "public_descriptor_count"), "public descriptor count", DESCRIPTOR_COUNT, required=False)
    count_sources(layout_sources, ("cases_per_api",), "public cases per API", CASES_PER_API, required=nested_layout is not None)
    count_sources(
        statistic_sources,
        ("minimum_significant_wins", "significant_win_target"),
        "public significant-win target",
        SIGNIFICANT_WIN_TARGET,
        required=nested_statistics is not None,
    )

    commitment = sha256_sources(
        seal_sources,
        ("opening_sha256", "seed_commitment", "blinded_seed_commitment", "holdout_seed_commitment", "seed_sha256", "seed_commitment_sha256"),
        "blinded holdout-seed commitment",
    )
    assert commitment is not None
    binding = sha256_alias(payload, ("binding_sha256", "manifest_binding_sha256", "public_binding_sha256"), "frozen public-manifest binding", required=nested_layout is not None)
    if binding is None:
        binding = digest
    declared_apis = public_names(layout, ("api_names", "apis", "public_operations", "operations"), "API names", API_COUNT)
    declared_workloads = public_names(layout, ("workload_names", "workloads", "workload_families", "categories", "families"), "workload names", WORKLOAD_COUNT)
    descriptors = descriptor_entries(layout)
    if nested_layout is not None:
        root_descriptors = descriptor_entries(payload)
        if root_descriptors is not None:
            require(descriptors is None or root_descriptors == descriptors, "the public manifest has conflicting root and layout descriptors")
            if descriptors is None:
                descriptors = root_descriptors

    if descriptors is not None:
        derived_apis = {api for api, _workload in descriptors}
        derived_workloads = {workload for _api, workload in descriptors}
        require(len(derived_apis) == API_COUNT, "the public descriptor layout omits an API")
        require(len(derived_workloads) == WORKLOAD_COUNT, "the public descriptor layout omits a workload")
        if declared_apis is None:
            declared_apis = tuple(api for api in API_LABELS if api in derived_apis)
        if declared_workloads is None:
            declared_workloads = tuple(sorted(derived_workloads))
        require(set(declared_apis) == derived_apis, "public descriptors disagree with the declared APIs")
        require(set(declared_workloads) == derived_workloads, "public descriptors disagree with the declared workloads")
    else:
        require(declared_apis is not None and declared_workloads is not None, "the public manifest must declare all API and workload names")
        count_sources(
            layout_sources,
            ("cases_per_cell", "cases_per_descriptor", "cases_per_category", "cases_per_workload", "examples_per_descriptor"),
            "public cases per descriptor",
            CASES_PER_DESCRIPTOR,
        )

    assert declared_apis is not None and declared_workloads is not None
    require(set(declared_apis) == set(API_LABELS), "the public manifest changed or omitted a Python regular-expression API")
    expected = frozenset((api, workload) for api in declared_apis for workload in declared_workloads)
    require(len(expected) == DESCRIPTOR_COUNT, "the public manifest does not declare the full 12-by-8 grid")
    if descriptors is not None:
        require(set(descriptors) == expected, "the public descriptor layout is not the complete API-by-workload grid")
    return ManifestLayout(digest, binding, commitment, tuple(API_LABELS), tuple(declared_workloads), expected)


def geometric(rows: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]]) -> float:
    require(bool(rows), "a complete result group is missing")
    return math.exp(math.fsum(math.log(finite(row.get("speedup"), "case speedup")) for row in rows) / len(rows))


def case_identifier(row: Mapping[str, Any], label: str) -> str:
    value = alias(row, ("case", "case_id", "id"), f"{label} identifier")
    require(isinstance(value, str) and bool(value) and value.strip() == value, f"invalid {label} identifier")
    return value


def candidate_label(module: str, ranking: Mapping[str, Any]) -> str:
    value = alias(ranking, ("label", "display_name", "name"), f"{module} display name", required=False)
    if value is not None:
        require(isinstance(value, str) and bool(value.strip()), f"invalid display name for {module}")
        return value.strip()
    tail = module.rsplit(".", 1)[-1].removesuffix("_candidate")
    return tail.replace("_", " ").strip().title() or module


def verify_artifacts(payload: Mapping[str, Any], modules: tuple[str, ...]) -> None:
    before = alias(payload, ("candidate_binary_sha256_before", "candidate_artifact_sha256_before", "artifact_sha256_before"), "candidate artifacts before measurement")
    after = alias(payload, ("candidate_binary_sha256_after", "candidate_artifact_sha256_after", "artifact_sha256_after"), "candidate artifacts after measurement")
    require(isinstance(before, dict) and bool(before), "candidate artifact provenance is missing")
    require(isinstance(after, dict) and before == after, "candidate artifacts changed during the final measurement")
    for artifact, digest in before.items():
        require(isinstance(artifact, str) and bool(artifact), "invalid measured artifact name")
        sha256_value(digest, f"artifact fingerprint {artifact}")
    for module in modules:
        require(
            any(artifact == module or artifact.startswith(f"{module}:") for artifact in before),
            f"no measured artifact fingerprint covers {module}",
        )


def validated_memory_metric(
    payload: Mapping[str, Any],
    rows: tuple[Mapping[str, Any], ...],
    *,
    kind: str,
    fields: tuple[str, ...],
) -> MemoryMetric:
    present = [field for field in fields if any(field in row for row in rows)]
    require(len(present) <= 1, f"ambiguous {kind} memory measurements")
    metadata = alias(payload, ("memory_measurements", "memory_measurement", "memory_provenance"), "memory provenance", required=False)
    if metadata is not None:
        require(isinstance(metadata, dict), "memory provenance must be an object")
    detail: Any = None
    if isinstance(metadata, dict):
        detail = metadata.get("process" if kind == "process" else "native")
        if detail is None:
            detail = metadata.get("process_rss" if kind == "process" else "native_allocator")
    if detail is not None:
        require(isinstance(detail, dict), f"{kind} memory provenance must be an object")

    if not present:
        require(not (isinstance(detail, dict) and detail.get("candidate_specific") is True), f"{kind} memory is claimed but no complete measurements exist")
        return MemoryMetric(None, "unavailable")

    field = present[0]
    require(all(field in row for row in rows), f"{kind} memory observations omit a measured case")
    for row in rows:
        finite(row[field], f"{kind} memory ratio", positive=False)

    if not isinstance(detail, dict) or detail.get("candidate_specific") is not True:
        return MemoryMetric(field, "unattributed")

    scope = detail.get("scope", detail.get("isolation"))
    require(isinstance(scope, str), f"{kind} memory lacks measurement-scope provenance")
    accepted = (
        {"isolated-candidate-process", "candidate-isolated-process", "per-candidate-process", "isolated_process", "per_candidate_process"}
        if kind == "process"
        else {"native-allocator", "candidate-native-allocator", "native_allocator", "allocator"}
    )
    require(scope in accepted, f"{kind} memory does not establish candidate-specific attribution")
    return MemoryMetric(field, "isolated")


def final_blocks(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    supplied = payload.get("results")
    if supplied is None:
        return {}
    require(isinstance(supplied, list) and bool(supplied), "final per-candidate results must be a nonempty array")
    blocks: dict[str, Mapping[str, Any]] = {}
    for offset, entry in enumerate(supplied):
        require(isinstance(entry, dict), f"invalid final result block {offset}")
        module = alias(entry, ("candidate", "module"), f"final result block {offset} candidate")
        require(isinstance(module, str) and bool(module) and module != "re", f"invalid final result block {offset} candidate")
        require(module not in blocks, f"duplicated final result block for {module}")
        if "cohort" in entry:
            require(entry["cohort"] == "holdout", f"{module} result block is not exclusively held-out")
        count_sources((entry,), ("cases", "case_count", "holdout_cases", "holdout_case_count"), f"{module} result-block case count", CASE_COUNT, required=False)
        rows = entry.get("case_results")
        require(isinstance(rows, list) and len(rows) == CASE_COUNT, f"{module} result block does not retain every held-out case")
        blocks[module] = entry
    return blocks


def block_ranking(block: Mapping[str, Any], module: str) -> Mapping[str, Any]:
    for name in ("ranking", "overall", "overall_ranking"):
        if name in block:
            result = block[name]
            require(isinstance(result, dict), f"{module} final {name} must be an object")
            return result
    required = {"geomean_speedup", "ci95_low", "ci95_high", "statistically_faster_cases", "regressions_gt_20pct"}
    require(required.issubset(block), f"{module} result block omits its overall ranking")
    return block


def block_sources(block: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    sources: list[Mapping[str, Any]] = [block]
    for name in ("proofs", "provenance", "artifacts", "measurements"):
        section = block.get(name)
        if section is None:
            continue
        require(isinstance(section, dict), f"candidate {name} provenance must be an object")
        sources.append(section)
        for child_name in ("artifacts", "measurements", "raw"):
            child = section.get(child_name)
            if child is not None:
                require(isinstance(child, dict), f"candidate {name}.{child_name} provenance must be an object")
                sources.append(child)
    raw = block.get("raw")
    if raw is not None:
        require(isinstance(raw, dict), "candidate raw provenance must be an object, not a file to open")
        sources.append(raw)
    return tuple(sources)


def verify_raw_provenance(
    payload: Mapping[str, Any], modules: tuple[str, ...], blocks: Mapping[str, Mapping[str, Any]]
) -> None:
    raw_names = (
        "raw_sha256",
        "raw_rows_sha256",
        "paired_raw_sha256",
        "raw_measurements_sha256",
        "raw_jsonl_sha256",
    )
    top_digest = sha256_alias(payload, raw_names, "complete paired-raw-measurement fingerprint", required=False)
    raw_count_names = ("paired_raw_rows", "raw_row_count", "paired_measurement_rows")
    top_count_present = any(name in payload for name in raw_count_names)
    if top_count_present:
        count_alias(payload, raw_count_names, "complete paired-raw row count", CASE_COUNT * TRIAL_COUNT * (len(modules) + 1))

    for module in modules:
        block = blocks.get(module)
        if block is None:
            continue
        sources = block_sources(block)
        candidate_digest = sha256_sources(sources, raw_names, f"{module} paired-raw-measurement fingerprint", required=False)
        raw_section = block.get("raw")
        if isinstance(raw_section, dict):
            direct = sha256_alias(raw_section, ("sha256", *raw_names), f"{module} raw provenance fingerprint", required=False)
            if direct is not None:
                require(candidate_digest is None or direct == candidate_digest, f"{module} raw provenance fingerprints conflict")
                candidate_digest = direct
        require(candidate_digest is not None or top_digest is not None, f"{module} has no paired-raw-measurement fingerprint")
        candidate_count_present = any(any(name in source for name in raw_count_names) for source in sources)
        if candidate_count_present:
            count_sources(sources, raw_count_names, f"{module} complete Python-and-candidate paired-raw row count", CASE_COUNT * TRIAL_COUNT * 2)
        else:
            require(top_count_present, f"{module} has no complete paired-raw row count")

    require(top_digest is not None or bool(blocks), "complete paired-raw-measurement fingerprints are missing")
    require(top_count_present or bool(blocks), "complete paired-raw row counts are missing")


def verify_final_artifacts(
    payload: Mapping[str, Any], modules: tuple[str, ...], blocks: Mapping[str, Mapping[str, Any]]
) -> None:
    before_names = ("candidate_binary_sha256_before", "candidate_artifact_sha256_before", "artifact_sha256_before")
    after_names = ("candidate_binary_sha256_after", "candidate_artifact_sha256_after", "artifact_sha256_after")
    root_before = any(name in payload for name in before_names)
    root_after = any(name in payload for name in after_names)
    if root_before or root_after:
        verify_artifacts(payload, modules)
        return
    require(bool(blocks), "candidate artifact provenance is missing")
    for module in modules:
        block = blocks.get(module)
        require(block is not None, f"no artifact-provenance block covers {module}")
        sources = block_sources(block)
        before_values = [source for source in sources if any(name in source for name in before_names)]
        after_values = [source for source in sources if any(name in source for name in after_names)]
        require(len(before_values) == 1 and len(after_values) == 1, f"{module} measured artifacts are missing or ambiguous")
        merged: dict[str, Any] = {}
        merged.update(before_values[0])
        merged.update(after_values[0])
        verify_artifacts(merged, (module,))


def validate_summary(payload: Mapping[str, Any], manifest: ManifestLayout) -> FinalResult:
    require(isinstance(payload, dict), "the final summary must be a JSON object")
    require(payload.get("schema") == SUMMARY_SCHEMA, "incorrect prospective v8 final-summary schema")
    blocks = final_blocks(payload)
    if "cohort" in payload:
        require(payload["cohort"] == "holdout", "only a fully measured held-out final cohort can be charted")
    else:
        require(bool(blocks), "the final held-out cohort is not identified")
        require(all(block.get("cohort") == "holdout" for block in blocks.values()), "every final result block must identify the held-out cohort")
    if "holdout_accessed" in payload:
        require(payload["holdout_accessed"] is True, "the supplied summary is not an unsealed final measurement")

    nested_layout = object_section(payload, "layout", "final summary layout")
    nested_trials = object_section(payload, "trials", "final trial protocol") if isinstance(payload.get("trials"), dict) else None
    nested_statistics = object_section(payload, "statistics", "final statistics protocol")
    nested_seal = object_section(payload, "seal", "final public seal")
    nested_manifest = object_section(payload, "manifest", "final public-manifest provenance") if isinstance(payload.get("manifest"), dict) else None
    layout_sources = (nested_layout, payload) if nested_layout is not None else (payload,)
    trial_sources = (nested_trials, payload) if nested_trials is not None else (payload,)
    statistic_sources = (nested_statistics, payload) if nested_statistics is not None else (payload,)
    seal_sources = (nested_seal, payload) if nested_seal is not None else (payload,)
    manifest_sources = (nested_manifest, payload) if nested_manifest is not None else (payload,)

    count_sources(layout_sources, ("cases", "case_count", "holdout_cases", "holdout_case_count", "total_cases"), "final held-out case count", CASE_COUNT, required=not bool(blocks))
    trial_names = ("paired_rounds", "paired_trials", "trial_count", "trials")
    trial_declared = any(any(name in source and not (name == "trials" and isinstance(source[name], dict)) for name in trial_names) for source in trial_sources)
    count_sources(trial_sources, trial_names, "final paired trial count", TRIAL_COUNT, required=not bool(blocks))
    if not trial_declared:
        for module, block in blocks.items():
            sources = block_sources(block)
            count_sources(sources, trial_names, f"{module} final paired trial count", TRIAL_COUNT)

    bootstrap_names = ("overall_bootstrap_draws", "bootstrap_resamples", "bootstrap_samples", "bootstrap_replicates", "bootstrap_iterations")
    bootstrap_declared = any(any(name in source for name in bootstrap_names) for source in statistic_sources)
    count_sources(statistic_sources, bootstrap_names, "final bootstrap resample count", BOOTSTRAP_COUNT, required=not bool(blocks))
    if not bootstrap_declared:
        for module, block in blocks.items():
            ranking = block_ranking(block, module)
            count_sources((block, ranking), bootstrap_names, f"{module} final bootstrap resample count", BOOTSTRAP_COUNT)

    for source in statistic_sources:
        if "confidence_level" in source:
            require(math.isclose(finite(source["confidence_level"], "confidence level"), 0.95, rel_tol=0, abs_tol=1e-15), "the confidence interval is not 95%")
    threshold_values = [
        alias(source, ("strict_regression_speedup_threshold", "regression_speedup_threshold"), "strict runtime-slowdown threshold", required=False)
        for source in statistic_sources
    ]
    threshold_values = [value for value in threshold_values if value is not None]
    require(bool(threshold_values), "missing strict runtime-slowdown threshold")
    threshold = finite(threshold_values[0], "strict runtime-slowdown threshold")
    require(all(math.isclose(finite(value, "strict runtime-slowdown threshold"), threshold, rel_tol=0, abs_tol=1e-15) for value in threshold_values), "conflicting runtime-slowdown thresholds")
    require(math.isclose(threshold, SLOWDOWN_THRESHOLD, rel_tol=0, abs_tol=1e-15), "a more-than-20% runtime slowdown must use the strict speedup threshold 5/6")
    count_sources(statistic_sources, ("minimum_significant_wins", "significant_win_target"), "significant-win target", SIGNIFICANT_WIN_TARGET, required=False)

    manifest_digest = sha256_sources(manifest_sources, ("manifest_sha256", "holdout_manifest_sha256", "public_manifest_sha256"), "final public-manifest file fingerprint", required=False)
    manifest_binding = sha256_sources(manifest_sources, ("binding_sha256", "manifest_binding_sha256", "public_binding_sha256", "holdout_binding_sha256"), "final frozen public-manifest binding", required=False)
    require(manifest_digest is not None or manifest_binding is not None, "the final summary does not cryptographically identify the public manifest")
    if manifest_digest is not None:
        require(manifest_digest == manifest.digest, "the final summary did not use the explicitly supplied public manifest file")
    if manifest_binding is not None:
        require(manifest_binding == manifest.binding, "the final summary changed the frozen public-manifest binding")
    seed_commitment = sha256_sources(seal_sources, ("opening_sha256", "seed_commitment", "blinded_seed_commitment", "holdout_seed_commitment", "seed_sha256", "seed_commitment_sha256"), "final blinded holdout-seed commitment", required=False)
    if seed_commitment is not None:
        require(seed_commitment == manifest.seed_commitment, "the final summary changed the blinded holdout-seed commitment")

    supplied_modules = payload.get("modules")
    if supplied_modules is None and blocks:
        supplied_modules = ["re", *blocks]
    require(isinstance(supplied_modules, list) and len(supplied_modules) >= 2, "the final summary must identify Python and every measured replacement")
    require(supplied_modules[0] == "re", "the comparison baseline must be Python re")
    require(all(isinstance(module, str) and bool(module) for module in supplied_modules), "invalid measured module")
    require(len(set(supplied_modules)) == len(supplied_modules), "a final module was duplicated")
    modules = tuple(supplied_modules[1:])
    if blocks:
        require(set(blocks) == set(modules), "the per-candidate results omit or invent a measured replacement")
    if "baseline" in payload:
        require(payload["baseline"] == "re", "the final Python baseline changed")
    verify_raw_provenance(payload, modules, blocks)
    verify_final_artifacts(payload, modules, blocks)

    supplied_rankings = payload.get("rankings")
    if supplied_rankings is None and blocks:
        supplied_rankings = []
        for module in modules:
            ranking = dict(block_ranking(blocks[module], module))
            ranking.setdefault("candidate", module)
            ranking.setdefault("cohort", blocks[module].get("cohort", payload.get("cohort")))
            ranking.setdefault("cases", blocks[module].get("cases", CASE_COUNT))
            supplied_rankings.append(ranking)
    require(isinstance(supplied_rankings, list) and len(supplied_rankings) == len(modules), "the final rankings omit or duplicate a replacement")
    rankings: dict[str, Mapping[str, Any]] = {}
    for offset, raw in enumerate(supplied_rankings):
        require(isinstance(raw, dict), f"invalid final ranking {offset}")
        module = raw.get("candidate")
        require(isinstance(module, str) and module in modules and module not in rankings, "a final ranking has an unmeasured or duplicated candidate")
        require(raw.get("cohort") == "holdout", f"{module} ranking is not exclusively held-out")
        require(integer(raw.get("cases"), f"{module} ranking case count") == CASE_COUNT, f"{module} ranking changed the final denominator")
        if "weight" in raw:
            require(integer(raw["weight"], f"{module} ranking weight") == CASE_COUNT, f"{module} ranking changed case weighting")
        point = finite(raw.get("geomean_speedup"), f"{module} overall speed")
        low = finite(raw.get("ci95_low"), f"{module} overall 95% lower bound")
        high = finite(raw.get("ci95_high"), f"{module} overall 95% upper bound")
        require(low <= point <= high, f"{module} overall confidence interval excludes its reported speed")
        rankings[module] = raw
    require(set(rankings) == set(modules), "the final rankings do not cover every measured replacement")

    raw_rows = payload.get("case_results")
    if blocks:
        flattened_rows: list[Any] = []
        for module in modules:
            block_rows = blocks[module]["case_results"]
            require(isinstance(block_rows, list) and len(block_rows) == CASE_COUNT, f"{module} result block dropped a held-out case")
            flattened_rows.extend(block_rows)
        if raw_rows is None:
            raw_rows = flattened_rows
        else:
            require(isinstance(raw_rows, list) and raw_rows == flattened_rows, "root and per-candidate final case evidence conflict")
    require(isinstance(raw_rows, list), "complete final per-case results are missing")
    require(len(raw_rows) == CASE_COUNT * len(modules), "the final per-case evidence omitted or duplicated a result")
    by_candidate: dict[str, list[Mapping[str, Any]]] = {module: [] for module in modules}
    identifiers: dict[str, set[str]] = {module: set() for module in modules}
    identifier_layouts: dict[str, dict[str, tuple[str, str]]] = {module: {} for module in modules}
    groups: dict[str, dict[tuple[str, str], list[Mapping[str, Any]]]] = {
        module: defaultdict(list) for module in modules
    }
    all_regressions: dict[tuple[str, str], Mapping[str, Any]] = {}

    for offset, raw in enumerate(raw_rows):
        require(isinstance(raw, dict), f"invalid final case result {offset}")
        module = raw.get("candidate")
        require(isinstance(module, str) and module in by_candidate, "a final case belongs to an unmeasured candidate")
        identifier = case_identifier(raw, "final case")
        require(identifier not in identifiers[module], f"{module} duplicated held-out case {identifier}")
        identifiers[module].add(identifier)
        require(raw.get("cohort") == "holdout", f"{module} includes a non-held-out case")
        key = descriptor_key(raw, f"{module} case {identifier}")
        require(key in manifest.descriptors, f"{module} case {identifier} is outside the frozen public descriptor grid")
        identifier_layouts[module][identifier] = key
        require(integer(raw.get("weight"), f"{module} case {identifier} weight") == 1, f"{module} reweighted case {identifier}")
        speed = finite(raw.get("speedup"), f"{module} case {identifier} speed")
        low = finite(raw.get("ci95_low"), f"{module} case {identifier} 95% lower bound")
        high = finite(raw.get("ci95_high"), f"{module} case {identifier} 95% upper bound")
        require(low <= speed <= high, f"{module} case {identifier} has an invalid confidence interval")
        finite(raw.get("baseline_ns"), f"{module} case {identifier} Python time")
        finite(raw.get("candidate_ns"), f"{module} case {identifier} replacement time")
        finite(raw.get("peak_traced_ratio"), f"{module} case {identifier} Python-traced memory", positive=False)
        faster = raw.get("statistically_faster")
        regression = raw.get("regression_gt_20pct")
        require(isinstance(faster, bool) and faster == (low > 1.0), f"{module} case {identifier} changes the strict significant-win rule")
        require(isinstance(regression, bool) and regression == (speed < SLOWDOWN_THRESHOLD), f"{module} case {identifier} hides or invents a more-than-20% runtime slowdown")
        by_candidate[module].append(raw)
        groups[module][key].append(raw)
        if regression:
            all_regressions[(module, identifier)] = raw

    reference_ids = identifiers[modules[0]]
    require(len(reference_ids) == CASE_COUNT, "the first replacement did not measure all 12,288 cases")
    for module in modules:
        require(identifiers[module] == reference_ids, f"{module} did not run the identical 12,288 held-out cases")
        require(identifier_layouts[module] == identifier_layouts[modules[0]], f"{module} changed the public descriptor assigned to a shared held-out case")
        require(set(groups[module]) == manifest.descriptors, f"{module} omitted a public API or workload descriptor")
        require(all(len(rows) == CASES_PER_DESCRIPTOR for rows in groups[module].values()), f"{module} changed a 128-case descriptor denominator")

    saved = payload.get("regressions")
    if blocks:
        flattened_regressions: list[Any] = []
        block_regressions_complete = True
        for module in modules:
            block_saved = blocks[module].get("regressions")
            if block_saved is None:
                block_regressions_complete = False
                continue
            require(isinstance(block_saved, list), f"{module} result-block slowdown audit must be an array")
            flattened_regressions.extend(block_saved)
        if saved is None:
            require(block_regressions_complete, "every final result block must retain its complete slowdown audit")
            saved = flattened_regressions
        elif block_regressions_complete:
            require(isinstance(saved, list) and saved == flattened_regressions, "root and per-candidate slowdown audits conflict")
    require(isinstance(saved, list), "the complete more-than-20% slowdown audit is missing")
    require(len(saved) == len(all_regressions), "the slowdown audit omitted or invented a case")
    saved_keys: set[tuple[str, str]] = set()
    for offset, entry in enumerate(saved):
        require(isinstance(entry, dict), f"invalid slowdown-audit row {offset}")
        module = entry.get("candidate")
        require(isinstance(module, str), f"slowdown-audit row {offset} omits its candidate")
        identifier = case_identifier(entry, "slowdown-audit case")
        key = (module, identifier)
        require(key in all_regressions and key not in saved_keys, "the slowdown audit omitted, duplicated, or invented a case")
        actual = all_regressions[key]
        require(descriptor_key(entry, f"slowdown-audit case {identifier}") == descriptor_key(actual, f"final case {identifier}"), "the slowdown audit changed a case descriptor")
        for field in ("speedup", "ci95_low", "ci95_high", "regression_gt_20pct"):
            require(field in entry and entry[field] == actual[field], f"the slowdown audit changed {field} for {identifier}")
        saved_keys.add(key)
    require(saved_keys == set(all_regressions), "the slowdown audit is incomplete")

    optional_api = payload.get("api_rankings")
    if blocks:
        block_api: list[Any] = []
        supplied_block_api = [module for module in modules if "api_rankings" in blocks[module]]
        if supplied_block_api:
            require(len(supplied_block_api) == len(modules), "API-level rankings omit a measured replacement")
            for module in modules:
                entries = blocks[module]["api_rankings"]
                require(isinstance(entries, list), f"{module} API-level rankings must be an array")
                block_api.extend(entries)
            if optional_api is None:
                optional_api = block_api
            else:
                require(isinstance(optional_api, list) and optional_api == block_api, "root and per-candidate API confidence intervals conflict")
    api_intervals: dict[tuple[str, str], tuple[float, float]] = {}
    if optional_api is not None:
        require(isinstance(optional_api, list) and len(optional_api) == len(modules) * API_COUNT, "API confidence intervals must cover every replacement and API")
        for entry in optional_api:
            require(isinstance(entry, dict), "invalid API-level ranking")
            module = entry.get("candidate")
            api = alias(entry, ("api", "operation", "public_operation"), "API-level ranking operation")
            key = (module, api)
            require(isinstance(module, str) and module in modules and api in manifest.apis and key not in api_intervals, "an API-level ranking is missing, duplicated, or unmeasured")
            require(integer(entry.get("cases"), "API-level case count") == CASES_PER_API, "an API-level ranking changed the 1,024-case denominator")
            selected = tuple(row for workload in manifest.workloads for row in groups[module][(api, workload)])
            point = finite(entry.get("geomean_speedup"), "API-level speed")
            require(math.isclose(point, geometric(selected), rel_tol=1e-11, abs_tol=1e-12), "an API-level ranking dropped or reweighted cases")
            low = finite(entry.get("ci95_low"), "API-level 95% lower bound")
            high = finite(entry.get("ci95_high"), "API-level 95% upper bound")
            require(low <= point <= high, "an API-level confidence interval excludes its reported speed")
            api_intervals[key] = (low, high)

    results: list[CandidateResult] = []
    for module in modules:
        rows = tuple(by_candidate[module])
        ranking = rankings[module]
        point = finite(ranking["geomean_speedup"], f"{module} overall speed")
        require(math.isclose(point, geometric(rows), rel_tol=1e-11, abs_tol=1e-12), f"{module} overall speed dropped or reweighted a held-out case")
        wins = sum(row["ci95_low"] > 1.0 for row in rows)
        losses = sum(row["ci95_high"] < 1.0 for row in rows)
        regressions = sum(row["regression_gt_20pct"] for row in rows)
        require(integer(ranking.get("statistically_faster_cases"), f"{module} significant-win count") == wins, f"{module} ranking hid a significant win")
        require(integer(ranking.get("regressions_gt_20pct"), f"{module} large-slowdown count") == regressions, f"{module} ranking hid a large slowdown")
        if "statistically_slower_cases" in ranking:
            require(integer(ranking["statistically_slower_cases"], f"{module} significant-loss count") == losses, f"{module} ranking hid a significant loss")
        if "uncertain_cases" in ranking:
            require(integer(ranking["uncertain_cases"], f"{module} uncertain-case count") == CASE_COUNT - wins - losses, f"{module} ranking hid an inconclusive case")
        frozen_groups = {key: tuple(values) for key, values in groups[module].items()}
        intervals = {api: api_intervals[(module, api)] for api in manifest.apis} if optional_api is not None else {}
        results.append(CandidateResult(module, candidate_label(module, ranking), ranking, rows, frozen_groups, intervals))

    results.sort(key=lambda item: (-finite(item.ranking["geomean_speedup"], "ranking speed"), item.label, item.module))
    frozen_rows = tuple(row for item in results for row in item.rows)
    process_memory = validated_memory_metric(payload, frozen_rows, kind="process", fields=PROCESS_RATIO_FIELDS)
    native_memory = validated_memory_metric(payload, frozen_rows, kind="native", fields=NATIVE_RATIO_FIELDS)
    return FinalResult(manifest, tuple(results), process_memory, native_memory)


def exact(value: Any) -> str:
    number = finite(value, "displayed speed", positive=False)
    representation = format(Decimal(str(number)), "f")
    if "." in representation:
        representation = representation.rstrip("0").rstrip(".")
    return f"{representation}×"


def compact(value: float) -> str:
    return f"{value:.4g}×"


def svg_open(width: int, height: int, title: str, subtitle: str, detail: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="chart-title chart-description">',
        f'<title id="chart-title">{escape(title)}</title>',
        f'<desc id="chart-description">{escape(detail)}</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#101828}.title{font-size:29px;font-weight:760}.sub{font-size:15px;fill:#475467}.head{font-size:16px;font-weight:720}.label{font-size:14px}.small{font-size:12.5px;fill:#475467}.value{font-size:14px;font-weight:700}.tick{font-size:12px;fill:#475467}.panel{fill:#f9fafb;stroke:#eaecf0;stroke-width:1}.grid{stroke:#e4e7ec;stroke-width:1}.baseline{stroke:#344054;stroke-width:2;stroke-dasharray:6 4}.foot{font-size:12.5px;fill:#475467}</style>',
        f'<text x="28" y="45" class="title">{escape(title)}</text>',
        f'<text x="28" y="72" class="sub">{escape(subtitle)}</text>',
    ]


def svg_text(body: list[str], x: float, y: float, class_name: str, value: str, *, anchor: str | None = None) -> None:
    alignment = f' text-anchor="{anchor}"' if anchor is not None else ""
    body.append(f'<text x="{x:.2f}" y="{y:.2f}" class="{class_name}"{alignment}>{escape(value)}</text>')


def nice_axis(maximum: float) -> tuple[float, float]:
    target = max(1.2, maximum * 1.10)
    magnitude = 10 ** math.floor(math.log10(target / 6))
    for factor in (1.0, 2.0, 2.5, 5.0, 10.0):
        step = factor * magnitude
        if math.ceil(target / step) <= 8:
            return math.ceil(target / step) * step, step
    raise ValueError("cannot construct a readable chart axis")


def speed_x(value: float, left: int, right: int, upper: float) -> float:
    require(0 <= value <= upper * (1 + 1e-12), "a reported interval falls outside its complete chart axis")
    return left + (right - left) * value / upper


def draw_speed_grid(body: list[str], *, left: int, right: int, top: int, bottom: int, upper: float, step: float) -> None:
    ticks = int(round(upper / step))
    for index in range(ticks + 1):
        value = index * step
        x = speed_x(value, left, right, upper)
        body.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" class="grid"/>')
        label = "0" if value == 0 else f"{value:.5g}×"
        svg_text(body, x, top - 9, "tick", label, anchor="middle")
    baseline = speed_x(1.0, left, right, upper)
    body.append(f'<line x1="{baseline:.2f}" y1="{top}" x2="{baseline:.2f}" y2="{bottom}" class="baseline"/>')
    svg_text(body, baseline, bottom + 17, "tick", "1× = Python re", anchor="middle")


def whisker(body: list[str], *, left_x: float, right_x: float, point_x: float, y: float, color: str, description: str) -> None:
    body.append(f'<g><title>{escape(description)}</title><line x1="{left_x:.2f}" y1="{y:.2f}" x2="{right_x:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width="4" stroke-linecap="round"/><line x1="{left_x:.2f}" y1="{y - 7:.2f}" x2="{left_x:.2f}" y2="{y + 7:.2f}" stroke="{color}" stroke-width="2"/><line x1="{right_x:.2f}" y1="{y - 7:.2f}" x2="{right_x:.2f}" y2="{y + 7:.2f}" stroke="{color}" stroke-width="2"/><circle cx="{point_x:.2f}" cy="{y:.2f}" r="6" fill="{color}" stroke="#ffffff" stroke-width="2"/></g>')


def outcome_counts(item: CandidateResult) -> tuple[int, int, int, int]:
    wins = sum(row["ci95_low"] > 1.0 for row in item.rows)
    losses = sum(row["ci95_high"] < 1.0 for row in item.rows)
    uncertain = CASE_COUNT - wins - losses
    regressions = sum(bool(row["regression_gt_20pct"]) for row in item.rows)
    require(wins + uncertain + losses == CASE_COUNT, "an outcome chart changed the final case denominator")
    return wins, uncertain, losses, regressions


def headline_chart(result: FinalResult) -> str:
    width = 1800
    left, right = 330, 1040
    height = 207 + 82 * (len(result.candidates) + 1)
    maximum = max([1.0, *(finite(item.ranking["ci95_high"], "overall confidence upper bound") for item in result.candidates)])
    upper, step = nice_axis(maximum)
    body = svg_open(
        width,
        height,
        "How much faster is each replacement than Python?",
        "12,288 held-out cases · 31 paired runs · 9,999 bootstrap resamples · exact reported 95% confidence whiskers",
        "Complete final results. Bars show geometric-mean speed relative to Python re at exactly one times. Whiskers show the reported overall 95 percent confidence interval. Every measured replacement and all held-out cases are included.",
    )
    draw_speed_grid(body, left=left, right=right, top=112, bottom=height - 58, upper=upper, step=step)
    baseline_y = 149
    baseline_x = speed_x(1.0, left, right, upper)
    svg_text(body, 30, baseline_y + 5, "head", "Python re (baseline)")
    body.append(f'<rect x="{left}" y="{baseline_y - 11}" width="{baseline_x - left:.2f}" height="22" rx="5" fill="{GREY}"/>')
    svg_text(body, 1070, baseline_y + 5, "value", "Exactly 1× · reference for the identical 12,288 cases")
    for offset, item in enumerate(result.candidates):
        y = 231 + 82 * offset
        point = finite(item.ranking["geomean_speedup"], "overall speed")
        low = finite(item.ranking["ci95_low"], "overall lower bound")
        high = finite(item.ranking["ci95_high"], "overall upper bound")
        color = GREEN if low > 1.0 else RED if high < 1.0 else AMBER
        interpretation = (
            "Clearly faster overall"
            if low > 1.0
            else "Clearly slower overall"
            if high < 1.0
            else "No established overall difference: the 95% interval includes 1×"
        )
        px = speed_x(point, left, right, upper)
        svg_text(body, 30, y + 5, "head", item.label)
        body.append(f'<rect x="{left}" y="{y - 11}" width="{px - left:.2f}" height="22" rx="5" fill="{color}" fill-opacity="0.22"/>')
        whisker(
            body,
            left_x=speed_x(low, left, right, upper),
            right_x=speed_x(high, left, right, upper),
            point_x=px,
            y=y,
            color=color,
            description=f"{item.label}: exact reported mean {exact(point)}; exact reported 95% confidence interval {exact(low)} to {exact(high)}",
        )
        svg_text(body, 1070, y - 12, "value", f"{exact(point)} as fast · exact 95% interval {exact(low)} to {exact(high)}")
        svg_text(body, 1070, y + 8, "small", interpretation)
        wins, _uncertain, _losses, regressions = outcome_counts(item)
        svg_text(body, 1070, y + 27, "small", f"{wins:,}/{CASE_COUNT:,} significantly faster · {regressions:,}/{CASE_COUNT:,} take more than 20% longer")
    svg_text(body, 28, height - 14, "foot", "Higher speed is better. A runtime taking more than 20% longer has speed strictly below 5/6; every case and every loss is retained.")
    return "\n".join((*body, "</svg>", ""))


def outcomes_chart(result: FinalResult) -> str:
    width = 1780
    left, right = 370, 1110
    panel_height = 173
    height = 128 + panel_height * len(result.candidates) + 45
    body = svg_open(
        width,
        height,
        "How often does each replacement actually win?",
        "Every one of 12,288 held-out cases · confidence-based wins, uncertain results and losses · 7,373-win target",
        "Complete confidence-based outcomes for every held-out case. Green, grey and red segments add to all 12,288 cases. The separate large-slowdown bar uses the same denominator and the strict five-sixths timing rule.",
    )
    scale = (right - left) / CASE_COUNT
    for offset, item in enumerate(result.candidates):
        top = 105 + offset * panel_height
        wins, uncertain, losses, regressions = outcome_counts(item)
        body.append(f'<rect x="18" y="{top - 12}" width="{width - 36}" height="{panel_height - 11}" rx="9" class="panel"/>')
        svg_text(body, 31, top + 13, "head", item.label)
        svg_text(body, 31, top + 47, "label", "95%-confidence outcome")
        cursor = float(left)
        for count, color, label in ((wins, GREEN, "significantly faster"), (uncertain, GREY, "no established difference"), (losses, RED, "significantly slower")):
            bar_width = count * scale
            if count:
                body.append(f'<g><title>{escape(f"{count:,} of {CASE_COUNT:,} cases: {label}")}</title><rect x="{cursor:.2f}" y="{top + 30}" width="{bar_width:.2f}" height="22" fill="{color}"/></g>')
                if bar_width >= 62:
                    body.append(f'<text x="{cursor + bar_width / 2:.2f}" y="{top + 46}" text-anchor="middle" style="font-size:12px;font-weight:750;fill:#ffffff">{count:,}</text>')
            cursor += bar_width
        svg_text(body, right + 16, top + 46, "value", f"{CASE_COUNT:,}/{CASE_COUNT:,}")
        svg_text(body, left, top + 74, "small", f"Green: {wins:,}/{CASE_COUNT:,} faster · grey: {uncertain:,}/{CASE_COUNT:,} inconclusive · red: {losses:,}/{CASE_COUNT:,} slower")
        target_message = "MEETS" if wins >= SIGNIFICANT_WIN_TARGET else "DOES NOT MEET"
        target_color = GREEN if wins >= SIGNIFICANT_WIN_TARGET else RED
        body.append(f'<text x="{left}" y="{top + 96}" style="font-size:13px;font-weight:720;fill:{target_color}">{escape(target_message)} the 7,373 significantly-faster-case target</text>')
        svg_text(body, 31, top + 127, "label", "Took more than 20% longer")
        body.append(f'<rect x="{left}" y="{top + 111}" width="{right - left}" height="20" rx="4" fill="#fee4e2"/>')
        if regressions:
            body.append(f'<rect x="{left}" y="{top + 111}" width="{regressions * scale:.2f}" height="20" rx="4" fill="{RED}"/>')
        svg_text(body, right + 16, top + 126, "value", f"{regressions:,}/{CASE_COUNT:,}")
        svg_text(body, left, top + 149, "small", "Large slowdowns are counted separately, including cases whose individual confidence intervals cross 1×.")
    svg_text(body, 27, height - 14, "foot", "A significant win requires the case’s 95% lower bound to be strictly above 1×. A large runtime slowdown requires speed strictly below 5/6.")
    return "\n".join((*body, "</svg>", ""))


def api_group(item: CandidateResult, manifest: ManifestLayout, api: str) -> tuple[Mapping[str, Any], ...]:
    rows = tuple(row for workload in manifest.workloads for row in item.groups[(api, workload)])
    require(len(rows) == CASES_PER_API, f"{item.module} omitted a case from API {api}")
    return rows


def api_chart(result: FinalResult) -> str:
    width = 1850
    left, right = 365, 1030
    row_height = 39
    panel_height = 78 + API_COUNT * row_height
    height = 118 + panel_height * len(result.candidates) + 45
    has_intervals = bool(result.candidates[0].api_intervals)
    values = [1.0]
    for item in result.candidates:
        for api in result.manifest.apis:
            rows = api_group(item, result.manifest, api)
            values.append(geometric(rows))
            if api in item.api_intervals:
                values.append(item.api_intervals[api][1])
    upper, step = nice_axis(max(values))
    subtitle = (
        "All 12 operations · 1,024 held-out cases per operation · exact reported API-level 95% confidence whiskers"
        if has_intervals
        else "All 12 operations · 1,024 held-out cases per operation · dots are complete-group averages, not confidence intervals"
    )
    body = svg_open(width, height, "Where is each replacement faster or slower?", subtitle, "Every replacement, all 12 public Python regular-expression APIs, all eight workloads per API, and all 12,288 held-out cases are included. API confidence whiskers are shown only when independently reported in the final summary.")
    for offset, item in enumerate(result.candidates):
        top = 110 + offset * panel_height
        body.append(f'<rect x="18" y="{top - 13}" width="{width - 36}" height="{panel_height - 9}" rx="9" class="panel"/>')
        svg_text(body, 30, top + 9, "head", item.label)
        draw_speed_grid(body, left=left, right=right, top=top + 47, bottom=top + 51 + API_COUNT * row_height, upper=upper, step=step)
        for index, api in enumerate(result.manifest.apis):
            rows = api_group(item, result.manifest, api)
            y = top + 73 + index * row_height
            point = geometric(rows)
            wins = sum(row["ci95_low"] > 1.0 for row in rows)
            regressions = sum(bool(row["regression_gt_20pct"]) for row in rows)
            px = speed_x(point, left, right, upper)
            svg_text(body, 30, y + 5, "label", f"{API_LABELS[api]} ({api})")
            if api in item.api_intervals:
                low, high = item.api_intervals[api]
                color = GREEN if low > 1.0 else RED if high < 1.0 else AMBER
                whisker(body, left_x=speed_x(low, left, right, upper), right_x=speed_x(high, left, right, upper), point_x=px, y=y, color=color, description=f"{item.label}, {api}: {exact(point)}; reported 95% interval {exact(low)} to {exact(high)}; all {CASES_PER_API:,} cases")
                label = f"{exact(point)} · 95%: {exact(low)} to {exact(high)}"
            else:
                body.append(f'<g><title>{escape(f"{item.label}, {api}: full-group average {exact(point)}; no API confidence interval asserted")}</title><circle cx="{px:.2f}" cy="{y}" r="6" fill="{BLUE}" stroke="#ffffff" stroke-width="2"/></g>')
                label = f"{exact(point)} average · no group interval claimed"
            svg_text(body, 1055, y + 5, "value", label)
            svg_text(body, 1470, y + 5, "small", f"{wins:,}/{CASES_PER_API:,} wins · {regressions:,}/{CASES_PER_API:,} large losses")
    svg_text(body, 28, height - 14, "foot", "Every operation contains exactly eight frozen public workload descriptors and 128 cases per descriptor; no API, workload, unfavorable case, or zero is removed.")
    return "\n".join((*body, "</svg>", ""))


def regressions_chart(result: FinalResult) -> str:
    width = 1750
    left, right = 420, 1100
    row_height = 27
    panel_height = 65 + DESCRIPTOR_COUNT * row_height
    height = 119 + panel_height * len(result.candidates) + 43
    body = svg_open(
        width,
        height,
        "Every category with a more-than-20% runtime slowdown",
        "All 96 frozen API-by-workload categories · all 128 cases per category · zero-count categories remain visible",
        "A complete audit of every candidate and every public descriptor. Each red bar uses its actual 128-case denominator; zero-loss descriptors are shown, and the totals match the full per-case slowdown audit.",
    )
    for offset, item in enumerate(result.candidates):
        top = 107 + offset * panel_height
        _wins, _uncertain, _losses, total = outcome_counts(item)
        body.append(f'<rect x="18" y="{top - 12}" width="{width - 36}" height="{panel_height - 7}" rx="9" class="panel"/>')
        svg_text(body, 31, top + 10, "head", f"{item.label} · all {total:,}/{CASE_COUNT:,} large runtime slowdowns")
        rendered = 0
        index = 0
        for api in result.manifest.apis:
            for workload in result.manifest.workloads:
                rows = item.groups[(api, workload)]
                count = sum(bool(row["regression_gt_20pct"]) for row in rows)
                rendered += count
                y = top + 33 + index * row_height
                index += 1
                svg_text(body, 30, y + 13, "label", f"{API_LABELS[api]} · {workload}")
                body.append(f'<rect x="{left}" y="{y}" width="{right - left}" height="17" rx="4" fill="{PALE}"/>')
                if count:
                    body.append(f'<rect x="{left}" y="{y}" width="{(right - left) * count / CASES_PER_DESCRIPTOR:.2f}" height="17" rx="4" fill="{RED}"/>')
                svg_text(body, right + 16, y + 13, "value", f"{count:,}/{CASES_PER_DESCRIPTOR:,}")
                svg_text(body, right + 119, y + 13, "small", f"{100 * count / CASES_PER_DESCRIPTOR:.1f}% of this complete category")
        require(index == DESCRIPTOR_COUNT and rendered == total, f"the regression chart omitted a category or slowdown for {item.module}")
    svg_text(body, 28, height - 14, "foot", "The rule is strictly Python-time / replacement-time < 5/6: a replacement takes more than 20% longer. All 96 categories, including zero-count categories, are retained.")
    return "\n".join((*body, "</svg>", ""))


def metric_medians(item: CandidateResult, manifest: ManifestLayout, field: str) -> list[float]:
    return [float(statistics.median(finite(row[field], f"{field} observation", positive=False) for row in api_group(item, manifest, api))) for api in manifest.apis]


def memory_chart(result: FinalResult) -> str:
    width = 1850
    left, right = 370, 1010
    row_height = 35
    trace_panel = 80 + API_COUNT * row_height
    process_panel = (70 + API_COUNT * row_height) if result.process_memory.mode == "isolated" else 87
    native_panel = (70 + API_COUNT * row_height) if result.native_memory.mode == "isolated" else 87
    candidate_panel = trace_panel + process_panel + native_panel + 32
    height = 126 + len(result.candidates) * candidate_panel + 52
    trace_values = [1.0]
    for item in result.candidates:
        trace_values.extend(metric_medians(item, result.manifest, "peak_traced_ratio"))
    trace_upper, trace_step = nice_axis(max(trace_values))
    body = svg_open(
        width,
        height,
        "What memory was actually measured?",
        "All 12,288 held-out cases · Python-traced allocations, whole-process RSS and native allocator measurements are kept separate",
        "Python-traced temporary memory is displayed for every API and candidate. Whole-process RSS is never described as native-allocator memory, and shared-process observations are never attributed to an individual candidate. Native-allocator data is displayed only with explicit candidate-specific allocator provenance.",
    )
    for offset, item in enumerate(result.candidates):
        top = 108 + offset * candidate_panel
        body.append(f'<rect x="18" y="{top - 11}" width="{width - 36}" height="{candidate_panel - 10}" rx="9" class="panel"/>')
        svg_text(body, 30, top + 11, "head", f"{item.label} · Python-traced temporary allocations")
        draw_speed_grid(body, left=left, right=right, top=top + 49, bottom=top + 53 + API_COUNT * row_height, upper=trace_upper, step=trace_step)
        medians = metric_medians(item, result.manifest, "peak_traced_ratio")
        for index, (api, median) in enumerate(zip(result.manifest.apis, medians, strict=True)):
            y = top + 73 + index * row_height
            rows = api_group(item, result.manifest, api)
            zeroes = sum(row["peak_traced_ratio"] == 0 for row in rows)
            color = GREEN if median < 1 else RED if median > 1 else GREY
            px = speed_x(median, left, right, trace_upper)
            svg_text(body, 30, y + 5, "label", f"{API_LABELS[api]} ({api})")
            body.append(f'<circle cx="{px:.2f}" cy="{y}" r="5.5" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>')
            svg_text(body, right + 20, y + 5, "value", f"{exact(median)} Python-traced median")
            svg_text(body, right + 335, y + 5, "small", f"all {CASES_PER_API:,} cases · {zeroes:,} zero-allocation cases")

        next_top = top + trace_panel
        for kind, metric, section_height in (
            ("Whole-process RSS (not native allocator memory)", result.process_memory, process_panel),
            ("Native-allocator memory (not Python-traced allocations)", result.native_memory, native_panel),
        ):
            svg_text(body, 30, next_top + 19, "head", kind)
            if metric.mode == "isolated":
                assert metric.field is not None
                values = metric_medians(item, result.manifest, metric.field)
                upper, step = nice_axis(max([1.0, *values]))
                draw_speed_grid(body, left=left, right=right, top=next_top + 49, bottom=next_top + 53 + API_COUNT * row_height, upper=upper, step=step)
                for index, (api, median) in enumerate(zip(result.manifest.apis, values, strict=True)):
                    y = next_top + 72 + index * row_height
                    color = GREEN if median < 1 else RED if median > 1 else GREY
                    svg_text(body, 30, y + 5, "label", f"{API_LABELS[api]} ({api})")
                    body.append(f'<circle cx="{speed_x(median, left, right, upper):.2f}" cy="{y}" r="5.5" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>')
                    svg_text(body, right + 20, y + 5, "value", f"{exact(median)} independently attributed median")
                    svg_text(body, right + 365, y + 5, "small", f"all {CASES_PER_API:,} cases")
            elif metric.mode == "unattributed":
                svg_text(body, 36, next_top + 45, "small", "Observations exist, but candidate-specific attribution has not been established; no per-candidate memory claim or invented bar is shown.")
                svg_text(body, 36, next_top + 66, "small", "Whole-process RSS includes the Python interpreter, shared libraries and other allocations; RSS is not a measurement of the native allocator.")
            else:
                svg_text(body, 36, next_top + 45, "small", "No independently attributed observations were supplied. Python-traced memory does not estimate whole-process RSS or native allocations.")
                svg_text(body, 36, next_top + 66, "small", "Unavailable measurements are stated explicitly and are never presented as zero or as a candidate advantage.")
            next_top += section_height
    svg_text(body, 28, height - 26, "foot", "For memory, lower is better. Zero Python-traced allocations are shown at 0× and included in all medians and denominators.")
    svg_text(body, 28, height - 9, "foot", "Python-traced temporary allocations, isolated whole-process RSS and native-allocator measurements are different metrics and must not be substituted for one another.")
    return "\n".join((*body, "</svg>", ""))


def rankings_chart(result: FinalResult) -> str:
    width = 1800
    left, right = 410, 1030
    all_items: list[tuple[float, str, CandidateResult | None]] = [(1.0, "Python re (baseline)", None)]
    all_items.extend((finite(item.ranking["geomean_speedup"], "ranking speed"), item.label, item) for item in result.candidates)
    all_items.sort(key=lambda entry: (-entry[0], entry[1], "" if entry[2] is None else entry[2].module))
    height = 170 + len(all_items) * 79 + 48
    maximum = max([1.0, *(finite(item.ranking["ci95_high"], "ranking upper confidence bound") for item in result.candidates)])
    upper, step = nice_axis(maximum)
    body = svg_open(
        width,
        height,
        "Complete final ranking, including Python",
        "Every measured replacement and the Python 1× reference · all 12,288 held-out cases · exact reported 95% intervals",
        "Complete geometric-mean speed ranking. Python re and every measured candidate are shown and sorted using every equally weighted held-out case. Full overall confidence intervals, significant-win counts and every large slowdown are retained.",
    )
    draw_speed_grid(body, left=left, right=right, top=113, bottom=height - 60, upper=upper, step=step)
    for index, (point, label, item) in enumerate(all_items):
        y = 150 + index * 79
        svg_text(body, 30, y + 5, "head", f"{index + 1}. {label}")
        px = speed_x(point, left, right, upper)
        if item is None:
            body.append(f'<rect x="{left}" y="{y - 10}" width="{px - left:.2f}" height="20" rx="4" fill="{GREY}"/>')
            svg_text(body, 1050, y + 5, "value", "Exactly 1× · Python reference · all 12,288 cases")
            continue
        low = finite(item.ranking["ci95_low"], "ranking confidence lower bound")
        high = finite(item.ranking["ci95_high"], "ranking confidence upper bound")
        color = GREEN if low > 1.0 else RED if high < 1.0 else AMBER
        body.append(f'<rect x="{left}" y="{y - 10}" width="{px - left:.2f}" height="20" rx="4" fill="{color}" fill-opacity="0.2"/>')
        whisker(body, left_x=speed_x(low, left, right, upper), right_x=speed_x(high, left, right, upper), point_x=px, y=y, color=color, description=f"Rank {index + 1}: {label}; exact overall speed {exact(point)}; reported 95% interval {exact(low)} to {exact(high)}")
        wins, _uncertain, _losses, regressions = outcome_counts(item)
        svg_text(body, 1050, y - 6, "value", f"{exact(point)} · exact 95%: {exact(low)} to {exact(high)}")
        svg_text(body, 1050, y + 15, "small", f"{wins:,}/{CASE_COUNT:,} significant wins · {regressions:,}/{CASE_COUNT:,} large slowdowns")
    svg_text(body, 28, height - 14, "foot", "Ranks use the complete, equally weighted held-out cohort, not selected workloads. Overlapping confidence intervals must not be interpreted as an established difference.")
    return "\n".join((*body, "</svg>", ""))


def build_charts(result: FinalResult) -> dict[str, str]:
    charts = {
        "overall": headline_chart(result),
        "outcomes": outcomes_chart(result),
        "api": api_chart(result),
        "regressions": regressions_chart(result),
        "memory": memory_chart(result),
        "rankings": rankings_chart(result),
    }
    require(len(charts) == 6, "a required final chart is missing")
    for name, content in charts.items():
        require("12,288" in content, f"{name} chart omitted its full final denominator")
        require("<title" in content and "<desc" in content and 'role="img"' in content, f"{name} chart lacks accessible descriptions")
        try:
            ElementTree.fromstring(content)
        except ElementTree.ParseError as error:
            raise ValueError(f"invalid generated {name} SVG") from error
    return charts


def synthetic_inputs() -> tuple[dict[str, Any], str, dict[str, Any]]:
    workloads = tuple(f"synthetic-workload-{index + 1:02d}" for index in range(WORKLOAD_COUNT))
    commitment = hashlib.sha256(b"v8-chart-self-test-synthetic-blinded-commitment").hexdigest()
    binding = hashlib.sha256(b"v8-chart-self-test-synthetic-public-binding").hexdigest()
    manifest: dict[str, Any] = {
        "binding_sha256": binding,
        "correctness": {"synthetic_only": True},
        "history": {"synthetic_only": True},
        "independence": {"synthetic_only": True},
        "layout": {
            "apis": list(API_LABELS),
            "applicability": "synthetic-complete-public-grid",
            "cases": CASE_COUNT,
            "cases_per_api": CASES_PER_API,
            "cases_per_cell": CASES_PER_DESCRIPTOR,
            "workloads": list(workloads),
        },
        "memory": {"synthetic_only": True},
        "reference": {"module": "re"},
        "schema": MANIFEST_SCHEMA,
        "seal": {"opening_sha256": commitment},
        "source": {"synthetic_only": True},
        "state": "synthetic-sealed",
        "statistics": {
            "minimum_significant_wins": SIGNIFICANT_WIN_TARGET,
            "overall_bootstrap_draws": BOOTSTRAP_COUNT,
        },
        "trials": {"paired_rounds": TRIAL_COUNT},
    }
    manifest_bytes = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    digest = hashlib.sha256(manifest_bytes).hexdigest()
    modules = ("synthetic.clearly_faster", "synthetic.mixed_outcomes")
    rows: list[dict[str, Any]] = []
    regressions: list[dict[str, Any]] = []
    rankings: list[dict[str, Any]] = []
    api_rankings: list[dict[str, Any]] = []
    result_blocks: list[dict[str, Any]] = []
    for module_index, module in enumerate(modules):
        module_rows: list[dict[str, Any]] = []
        for api_index, api in enumerate(API_LABELS):
            for workload_index, workload in enumerate(workloads):
                for case_index in range(CASES_PER_DESCRIPTOR):
                    pattern = (case_index + api_index + workload_index) % 16
                    if pattern == 0 and workload_index != WORKLOAD_COUNT - 1:
                        speed, low, high = 0.78, 0.70, 0.82
                    elif pattern == 0:
                        speed, low, high = 1.03, 0.96, 1.10
                    elif pattern == 1:
                        speed, low, high = SLOWDOWN_THRESHOLD, 0.80, 0.89
                    elif pattern == 2:
                        speed, low, high = 1.0, 0.94, 1.07
                    elif pattern == 3:
                        speed, low, high = 1.09, 1.0, 1.18
                    elif module_index == 0 or pattern < 11:
                        speed, low, high = (1.52, 1.34, 1.72) if module_index == 0 else (1.18, 1.06, 1.34)
                    else:
                        speed, low, high = 0.94, 0.83, 1.05
                    identifier = f"synthetic.v8.{api_index:02d}.{workload_index:02d}.{case_index:03d}"
                    row: dict[str, Any] = {
                        "case": identifier,
                        "cohort": "holdout",
                        "candidate": module,
                        "api": api,
                        "workload": workload,
                        "weight": 1,
                        "speedup": speed,
                        "ci95_low": low,
                        "ci95_high": high,
                        "baseline_ns": 1_000.0,
                        "candidate_ns": 1_000.0 / speed,
                        "peak_traced_ratio": float(pattern % 7) / 6,
                        "statistically_faster": low > 1.0,
                        "regression_gt_20pct": speed < SLOWDOWN_THRESHOLD,
                    }
                    rows.append(row)
                    module_rows.append(row)
                    if row["regression_gt_20pct"]:
                        regressions.append(dict(row))
        point = geometric(module_rows)
        wins = sum(bool(row["statistically_faster"]) for row in module_rows)
        losses = sum(row["ci95_high"] < 1 for row in module_rows)
        ranking = {
            "candidate": module,
            "label": "Synthetic faster example" if module_index == 0 else "Synthetic mixed example",
            "cohort": "holdout",
            "cases": CASE_COUNT,
            "weight": CASE_COUNT,
            "geomean_speedup": point,
            "ci95_low": point * 0.97,
            "ci95_high": point * 1.03,
            "statistically_faster_cases": wins,
            "statistically_slower_cases": losses,
            "uncertain_cases": CASE_COUNT - wins - losses,
            "regressions_gt_20pct": sum(bool(row["regression_gt_20pct"]) for row in module_rows),
        }
        rankings.append(ranking)
        module_api_rankings: list[dict[str, Any]] = []
        for api in API_LABELS:
            selected = [row for row in module_rows if row["api"] == api]
            api_point = geometric(selected)
            api_ranking = {
                "candidate": module,
                "api": api,
                "cases": CASES_PER_API,
                "geomean_speedup": api_point,
                "ci95_low": api_point * 0.96,
                "ci95_high": api_point * 1.04,
            }
            api_rankings.append(api_ranking)
            module_api_rankings.append(api_ranking)
        fingerprint = hashlib.sha256(f"synthetic-chart-engine-{module_index}".encode("ascii")).hexdigest()
        artifacts = {f"{module}:native-engine": fingerprint}
        result_blocks.append({
            "candidate": module,
            "cohort": "holdout",
            "cases": CASE_COUNT,
            "paired_rounds": TRIAL_COUNT,
            "overall_bootstrap_draws": BOOTSTRAP_COUNT,
            "ranking": ranking,
            "case_results": module_rows,
            "regressions": [dict(row) for row in module_rows if row["regression_gt_20pct"]],
            "api_rankings": module_api_rankings,
            "raw_sha256": hashlib.sha256(f"synthetic-chart-raw-{module_index}".encode("ascii")).hexdigest(),
            "paired_raw_rows": CASE_COUNT * TRIAL_COUNT * 2,
            "candidate_binary_sha256_before": dict(artifacts),
            "candidate_binary_sha256_after": dict(artifacts),
        })
    fingerprints = {
        f"{modules[0]}:native-engine": hashlib.sha256(b"synthetic-chart-engine-0").hexdigest(),
        f"{modules[1]}:native-engine": hashlib.sha256(b"synthetic-chart-engine-1").hexdigest(),
    }
    summary: dict[str, Any] = {
        "schema": SUMMARY_SCHEMA,
        "cohort": "holdout",
        "holdout_accessed": True,
        "cases": CASE_COUNT,
        "trials": TRIAL_COUNT,
        "bootstrap_resamples": BOOTSTRAP_COUNT,
        "confidence_level": 0.95,
        "strict_regression_speedup_threshold": SLOWDOWN_THRESHOLD,
        "significant_win_target": SIGNIFICANT_WIN_TARGET,
        "manifest_sha256": digest,
        "binding_sha256": binding,
        "seed_commitment": commitment,
        "raw_sha256": hashlib.sha256(b"synthetic-chart-raw-commitment-only").hexdigest(),
        "paired_raw_rows": CASE_COUNT * TRIAL_COUNT * (len(modules) + 1),
        "baseline": "re",
        "modules": ["re", *modules],
        "candidate_binary_sha256_before": dict(fingerprints),
        "candidate_binary_sha256_after": dict(fingerprints),
        "rankings": rankings,
        "case_results": rows,
        "regressions": regressions,
        "api_rankings": api_rankings,
        "results": result_blocks,
    }
    return manifest, digest, summary


def copy_for_mutation(summary: Mapping[str, Any]) -> dict[str, Any]:
    copied = dict(summary)
    for field in ("modules", "rankings", "case_results", "regressions", "api_rankings", "results"):
        value = copied.get(field)
        if isinstance(value, list):
            copied[field] = list(value)
    for field in ("candidate_binary_sha256_before", "candidate_binary_sha256_after"):
        value = copied.get(field)
        if isinstance(value, dict):
            copied[field] = dict(value)
    return copied


def replace_row(summary: dict[str, Any], offset: int, **changes: Any) -> None:
    rows = summary["case_results"]
    replacement = dict(rows[offset])
    replacement.update(changes)
    rows[offset] = replacement


def replace_ranking(summary: dict[str, Any], offset: int, **changes: Any) -> None:
    rankings = summary["rankings"]
    replacement = dict(rankings[offset])
    replacement.update(changes)
    rankings[offset] = replacement


def omit_block_fields(summary: dict[str, Any], *fields: str) -> None:
    blocks = summary.get("results")
    if blocks is None:
        return
    require(isinstance(blocks, list), "synthetic result blocks must be an array")
    summary["results"] = [
        {name: value for name, value in block.items() if name not in fields}
        for block in blocks
    ]


def remove_all_raw_fingerprints(summary: dict[str, Any]) -> None:
    for field in (
        "raw_sha256",
        "raw_rows_sha256",
        "paired_raw_sha256",
        "raw_measurements_sha256",
        "raw_jsonl_sha256",
    ):
        summary.pop(field, None)
    omit_block_fields(
        summary,
        "raw_sha256",
        "raw_rows_sha256",
        "paired_raw_sha256",
        "raw_measurements_sha256",
        "raw_jsonl_sha256",
        "raw",
    )


def expect_summary_rejection(
    original: Mapping[str, Any],
    manifest: ManifestLayout,
    label: str,
    mutation: Callable[[dict[str, Any]], None],
) -> None:
    poisoned = copy_for_mutation(original)
    mutation(poisoned)
    try:
        validate_summary(poisoned, manifest)
    except (ValueError, TypeError, KeyError, OverflowError):
        return
    raise ValueError(f"synthetic self-test accepted {label}")


def expect_manifest_rejection(
    original: Mapping[str, Any],
    digest: str,
    label: str,
    mutation: Callable[[dict[str, Any]], None],
) -> None:
    poisoned = dict(original)
    for section_name in ("layout", "trials", "statistics", "seal"):
        section = poisoned.get(section_name)
        if isinstance(section, dict):
            copied_section = dict(section)
            for array_name in ("apis", "workloads", "descriptors"):
                if isinstance(copied_section.get(array_name), list):
                    copied_section[array_name] = list(copied_section[array_name])
            poisoned[section_name] = copied_section
    if isinstance(poisoned.get("descriptors"), list):
        poisoned["descriptors"] = list(poisoned["descriptors"])
    if isinstance(poisoned.get("api_names"), list):
        poisoned["api_names"] = list(poisoned["api_names"])
    if isinstance(poisoned.get("workload_names"), list):
        poisoned["workload_names"] = list(poisoned["workload_names"])
    mutation(poisoned)
    try:
        validate_manifest(poisoned, digest)
    except (ValueError, TypeError, KeyError, OverflowError):
        return
    raise ValueError(f"synthetic self-test accepted {label}")


def self_test() -> None:
    synthetic_manifest, digest, synthetic_summary = synthetic_inputs()
    layout = validate_manifest(synthetic_manifest, digest)
    result = validate_summary(synthetic_summary, layout)
    charts = build_charts(result)
    require(charts == build_charts(result), "the six final charts are not deterministic")

    overall = charts["overall"]
    outcomes = charts["outcomes"]
    rankings = charts["rankings"]
    require("Python re (baseline)" in overall and "Exactly 1×" in overall, "the headline omitted the exact Python baseline")
    require("7,373" in outcomes, "the outcome chart omitted the significant-win threshold")
    require("MEETS the 7,373" in outcomes and "DOES NOT MEET the 7,373" in outcomes, "the outcome chart failed to distinguish passing and failing synthetic examples")
    require("0/128" in charts["regressions"], "the slowdown chart dropped zero-loss categories")
    for item in result.candidates:
        low = exact(item.ranking["ci95_low"])
        point = exact(item.ranking["geomean_speedup"])
        high = exact(item.ranking["ci95_high"])
        for required in (item.label, low, point, high):
            require(escape(required) in overall and escape(required) in rankings, "a headline or ranking omitted an exact reported result")
        wins, uncertain, losses, regressions = outcome_counts(item)
        for count in (wins, uncertain, losses, regressions):
            require(f"{count:,}/{CASE_COUNT:,}" in outcomes, "the outcome chart omitted a complete measured outcome")
        for api in layout.apis:
            require(f"({escape(api)})" in charts["api"], f"the API chart omitted {api}")
            require(f"({escape(api)})" in charts["memory"], f"the Python-traced memory chart omitted {api}")
        for api in layout.apis:
            for workload in layout.workloads:
                require(escape(f"{API_LABELS[api]} · {workload}") in charts["regressions"], "the slowdown chart omitted a public API-by-workload category")
    for required in ("Python-traced temporary allocations", "Whole-process RSS (not native allocator memory)", "Native-allocator memory (not Python-traced allocations)", "No independently attributed observations were supplied"):
        require(required in charts["memory"], "the memory chart confused or fabricated Python, process, or native memory")

    first = synthetic_summary["case_results"][0]
    exact_boundary = next(index for index, row in enumerate(synthetic_summary["case_results"]) if row["speedup"] == SLOWDOWN_THRESHOLD)
    tied_boundary = next(index for index, row in enumerate(synthetic_summary["case_results"]) if row["ci95_low"] == 1.0)
    mutations: tuple[tuple[str, Callable[[dict[str, Any]], None]], ...] = (
        ("a practice-only final cohort", lambda value: value.__setitem__("cohort", "calibration")),
        ("an incorrect final schema", lambda value: value.__setitem__("schema", "rebar-v8-invented-summary-v1")),
        ("a changed final case denominator", lambda value: value.__setitem__("cases", CASE_COUNT - 1)),
        ("a changed paired-trial count", lambda value: value.__setitem__("trials", TRIAL_COUNT - 1)),
        ("a changed bootstrap denominator", lambda value: value.__setitem__("bootstrap_resamples", BOOTSTRAP_COUNT - 1)),
        ("a replaced public manifest", lambda value: value.__setitem__("manifest_sha256", "0" * 64)),
        ("a changed blinded seed commitment", lambda value: value.__setitem__("seed_commitment", "0" * 64)),
        ("missing paired-raw provenance", remove_all_raw_fingerprints),
        ("an incomplete paired-raw row count", lambda value: value.__setitem__("paired_raw_rows", value["paired_raw_rows"] - 1)),
        ("an artifact changed during measurement", lambda value: value["candidate_binary_sha256_after"].__setitem__(next(iter(value["candidate_binary_sha256_after"])), "0" * 64)),
        ("the wrong Python baseline", lambda value: value["modules"].__setitem__(0, "not_python_re")),
        ("a dropped measured candidate", lambda value: value["rankings"].pop()),
        ("a dropped held-out case", lambda value: value["case_results"].pop()),
        ("a duplicated held-out case", lambda value: value["case_results"].__setitem__(1, dict(first))),
        ("a non-held-out case", lambda value: replace_row(value, 0, cohort="calibration")),
        ("a descriptor outside the public commitment", lambda value: replace_row(value, 0, workload="invented-hidden-workload")),
        ("a reweighted case", lambda value: replace_row(value, 0, weight=2)),
        ("an inverted per-case confidence interval", lambda value: replace_row(value, 0, ci95_low=2.0)),
        ("a hidden significant win", lambda value: replace_ranking(value, 0, statistically_faster_cases=value["rankings"][0]["statistically_faster_cases"] - 1)),
        ("a hidden large slowdown", lambda value: replace_ranking(value, 0, regressions_gt_20pct=value["rankings"][0]["regressions_gt_20pct"] - 1)),
        ("a dropped slowdown-audit case", lambda value: value["regressions"].pop()),
        ("a substituted overall geometric mean", lambda value: replace_ranking(value, 0, geomean_speedup=value["rankings"][0]["geomean_speedup"] * 1.001)),
        ("a fabricated overall confidence interval", lambda value: replace_ranking(value, 0, ci95_low=value["rankings"][0]["geomean_speedup"] * 1.01)),
        ("a weakened runtime-slowdown threshold", lambda value: value.__setitem__("strict_regression_speedup_threshold", 0.8)),
        ("a falsely included exact five-sixths boundary", lambda value: replace_row(value, exact_boundary, regression_gt_20pct=True)),
        ("a falsely significant 1× confidence boundary", lambda value: replace_row(value, tied_boundary, statistically_faster=True)),
        ("an altered significant-win target", lambda value: value.__setitem__("significant_win_target", SIGNIFICANT_WIN_TARGET - 1)),
        ("a replaced frozen public binding", lambda value: value.__setitem__("binding_sha256", "0" * 64)),
        ("a negative Python-traced memory observation", lambda value: replace_row(value, 0, peak_traced_ratio=-1)),
        ("an omitted API confidence interval", lambda value: value["api_rankings"].pop()),
        ("an incomplete process-memory observation", lambda value: replace_row(value, 0, peak_process_rss_ratio=1.0)),
    )
    for label, mutation in mutations:
        expect_summary_rejection(synthetic_summary, layout, label, mutation)

    manifest_mutations: tuple[tuple[str, Callable[[dict[str, Any]], None]], ...] = (
        ("the wrong public manifest schema", lambda value: value.__setitem__("schema", "rebar-v8-unfrozen-manifest-v1")),
        ("a changed public case count", lambda value: value["layout"].__setitem__("cases", CASE_COUNT - 1)),
        ("a dropped public operation", lambda value: value["layout"]["apis"].pop()),
        ("a dropped public workload", lambda value: value["layout"]["workloads"].pop()),
        ("a changed public 96-descriptor grid", lambda value: value["layout"].__setitem__("descriptor_count", DESCRIPTOR_COUNT - 1)),
        ("a public descriptor with the wrong denominator", lambda value: value["layout"].__setitem__("cases_per_cell", CASES_PER_DESCRIPTOR - 1)),
        ("materialized hidden case definitions", lambda value: value.__setitem__("case_definitions", [{"case": "synthetic-forbidden"}])),
        ("a materialized hidden case list", lambda value: value["layout"].__setitem__("holdout_cases", [{"case": "synthetic-forbidden"}])),
        ("a missing blinded seed commitment", lambda value: value["seal"].pop("opening_sha256")),
        ("a weakened public significant-win target", lambda value: value["statistics"].__setitem__("minimum_significant_wins", SIGNIFICANT_WIN_TARGET - 1)),
    )
    for label, mutation in manifest_mutations:
        expect_manifest_rejection(synthetic_manifest, digest, label, mutation)

    without_api = copy_for_mutation(synthetic_summary)
    without_api.pop("api_rankings")
    omit_block_fields(without_api, "api_rankings")
    no_api_intervals = build_charts(validate_summary(without_api, layout))["api"]
    require("no group interval claimed" in no_api_intervals, "unreported API confidence intervals were invented")

    blocks_only = copy_for_mutation(synthetic_summary)
    for field in (
        "modules",
        "rankings",
        "case_results",
        "regressions",
        "api_rankings",
        "raw_sha256",
        "paired_raw_rows",
        "candidate_binary_sha256_before",
        "candidate_binary_sha256_after",
    ):
        blocks_only.pop(field, None)
    require(
        build_charts(validate_summary(blocks_only, layout)) == charts,
        "per-candidate prospective result blocks were dropped, reweighted, or rendered inconsistently",
    )

    measured_memory = copy_for_mutation(synthetic_summary)
    measured_memory.pop("results", None)
    measured_memory["case_results"] = [
        {
            **row,
            "peak_process_rss_ratio": 0.7 + 0.1 * float(row["peak_traced_ratio"]),
            "native_peak_ratio": 0.4 + 0.2 * float(row["peak_traced_ratio"]),
        }
        for row in synthetic_summary["case_results"]
    ]
    measured_memory["memory_measurements"] = {
        "process": {"candidate_specific": True, "scope": "isolated-candidate-process"},
        "native": {"candidate_specific": True, "scope": "native-allocator"},
    }
    attributed_memory = build_charts(validate_summary(measured_memory, layout))["memory"]
    require(
        "independently attributed median" in attributed_memory
        and "Whole-process RSS (not native allocator memory)" in attributed_memory
        and "Native-allocator memory (not Python-traced allocations)" in attributed_memory,
        "independently proven process and native memory were confused or omitted",
    )
    expect_summary_rejection(
        measured_memory,
        layout,
        "a shared process falsely advertised as candidate-native memory",
        lambda value: value.__setitem__(
            "memory_measurements",
            {
                "process": {"candidate_specific": True, "scope": "shared-process"},
                "native": {"candidate_specific": True, "scope": "native-allocator"},
            },
        ),
    )

    try:
        main(["--self-test", "--summary", "/synthetic/never-read.json"])
    except (ValueError, TypeError, KeyError, OverflowError):
        pass
    else:
        raise ValueError("synthetic self-test accepted a real-input path")

    print(
        f"PASS: {len(charts)} deterministic, accessible SVG charts; "
        f"{len(result.candidates)} synthetic candidates; "
        f"{CASE_COUNT:,} synthetic cases per candidate; "
        f"all {DESCRIPTOR_COUNT} public {CASES_PER_DESCRIPTOR}-case descriptor groups; "
        f"{len(mutations) + len(manifest_mutations) + 2} fail-closed corruption checks; "
        "no files, real measurements, hidden case definitions, seeds, or holdout evidence accessed"
    )


def load_json(path: Path, label: str) -> tuple[dict[str, Any], str]:
    try:
        content = path.read_bytes()
        payload = json.loads(content)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read explicitly supplied {label}: {path}") from error
    require(isinstance(payload, dict), f"the explicitly supplied {label} is not a JSON object")
    return payload, hashlib.sha256(content).hexdigest()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run deterministic, exclusively synthetic in-memory checks; do not open any input or create any output")
    parser.add_argument("--manifest", type=Path, help="explicit frozen, blinded, public v8 holdout-manifest JSON path")
    parser.add_argument("--summary", type=Path, help="explicit already-unsealed, correctness-qualified final v8 summary JSON path")
    parser.add_argument("--prefix", type=Path, help="explicit output prefix; six named SVGs are created only after complete validation")
    args = parser.parse_args(argv)
    if args.self_test:
        require(args.manifest is None and args.summary is None and args.prefix is None, "synthetic self-test must not receive or read any real paths")
        self_test()
        return
    require(args.manifest is not None and args.summary is not None and args.prefix is not None, "normal operation requires explicit --manifest, --summary and --prefix paths")
    manifest_payload, manifest_digest = load_json(args.manifest, "public manifest")
    manifest = validate_manifest(manifest_payload, manifest_digest)
    summary_payload, _summary_digest = load_json(args.summary, "final summary")
    result = validate_summary(summary_payload, manifest)
    charts = build_charts(result)
    paths = {name: Path(f"{args.prefix}-{name}.svg") for name in charts}
    require(len({path.resolve() for path in paths.values()}) == len(charts), "final chart destinations collide")
    protected = {args.manifest.resolve(), args.summary.resolve()}
    require(not any(path.resolve() in protected for path in paths.values()), "a final chart would overwrite an explicitly supplied input")
    args.prefix.parent.mkdir(parents=True, exist_ok=True)
    for name, content in charts.items():
        destination = paths[name]
        destination.write_text(content, encoding="utf-8")
        print(f"wrote {destination}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, KeyError, OverflowError) as error:
        raise SystemExit(f"error: {error}") from error
