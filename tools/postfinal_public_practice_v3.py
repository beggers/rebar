#!/usr/bin/env python3
"""Freeze, measure, and independently replay additive public-only practice.

This benchmark is not a replacement for the failed final experiment.  Its only
case source is the separately sealed v7 *calibration-only* archive.  In
particular, neither freezing nor replay imports a candidate, generates a case,
opens a held-out fixture, or changes an existing benchmark or evidence file.
"""

from __future__ import annotations

import argparse
import collections
import gc
import gzip
import hashlib
import importlib
import json
import platform
import sys
import time
import tracemalloc
import types
from pathlib import Path
from typing import Any

from tools import rust_v7_calibration_pilot as pilot
from tools import rust_v7_multi_candidate_practice_audit as replay


ROOT = pilot.ROOT
VERSION = "postfinal-public-practice-v3"
VERSION_ROOT = ROOT / "performance" / "postfinal-public-v3"
EVIDENCE_ROOT = VERSION_ROOT / "evidence"
MANIFEST_PATH = VERSION_ROOT / "manifest.json"
RAW_PATH = EVIDENCE_ROOT / f"{VERSION}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE_ROOT / f"{VERSION}-summary.json"
INTEGRITY_PATH = EVIDENCE_ROOT / f"{VERSION}-integrity.json"
AUDIT_PATH = ROOT / "candidates" / "audits" / "FROM-SCRATCH-AUDIT.json"

POSTFINAL_PLAN_SCHEMA = "rebar-postfinal-public-practice-plan-v3"
POSTFINAL_REPORT_SCHEMA = "rebar-postfinal-public-practice-report-v3"
POSTFINAL_INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v3"

MODULES = (
    "re",
    "candidates.rust_candidate",
    "candidates.vm_candidate",
    "candidates.zig_candidate",
)
DEFAULT_EDGE_ORACLES = (
    ROOT / "candidates/evidence/rust-v7-edge-oracle-rust-post-final-stage-03-slot-batch.json.gz",
    ROOT / "candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-21-singleton-split-memchr.json.gz",
    ROOT / "candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-13.json.gz",
)

CASES = 4_096
FIXTURE_CASES = 10_312
ELIGIBLE_CASES = 9_731
CATEGORIES = 260
PUBLIC_APIS = 12
TRIALS = 13
BOOTSTRAPS = 2_000
MAX_OPERATIONS = 16
SELECTION_SEED = 2026072401
ORDER_SEED = 2026072402
BOOTSTRAP_SEED = 2026072403
EXCLUSIVE_SLOT = VERSION

EXPECTED_BOUNDED_API_COUNTS = {
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

Entry = tuple[int, dict[str, Any], dict[str, Any]]
SelectedEntry = tuple[int, dict[str, Any], dict[str, Any], tuple[str, ...]]


def require(condition: bool, message: str) -> None:
    """Fail closed without modifying an existing experiment or its evidence."""

    if not condition:
        raise RuntimeError(message)


def require_candidate_free() -> None:
    """Ensure that planning, synthetic testing, and replay never load an engine."""

    loaded = sorted(
        name
        for name in sys.modules
        if any(name == candidate or name.startswith(candidate + ".") for candidate in MODULES[1:])
    )
    require(not loaded, f"public-only operation imported a production candidate: {loaded!r}")


def require_pinned_python() -> None:
    require(
        platform.python_implementation() == "CPython"
        and tuple(sys.version_info[:3]) == (3, 14, 6),
        "public practice requires pinned stable CPython 3.14.6",
    )
    require(
        Path(sys.executable).resolve() == replay.PINNED_PYTHON.resolve(),
        "public practice requires the exact pinned CPython baseline executable",
    )


def exact_versioned_path(value: Path, expected: Path, label: str) -> Path:
    resolved = value.resolve()
    require(
        resolved == expected.resolve(),
        f"{label} must use its unique additive {VERSION} evidence path",
    )
    require(
        resolved.is_relative_to(VERSION_ROOT.resolve()),
        f"{label} escaped the additive public-practice evidence directory",
    )
    return resolved


def read_json(path: Path, label: str) -> dict[str, Any]:
    require(path.is_file(), f"the frozen {label} is missing")
    try:
        with path.open("rb") as stream:
            document = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"cannot decode the frozen {label}") from error
    require(isinstance(document, dict), f"the frozen {label} is not an object")
    return document


def seed_key(seed: int, identifier: str) -> tuple[bytes, str]:
    return pilot.selection_key(seed, identifier)


def stratum(case: dict[str, Any], expected: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        case["api"],
        case["lifecycle"],
        pilot.source_kind(case),
        pilot.density(expected["result"]),
    )


def allocate_quotas(
    capacities: collections.Counter[str],
    initial: collections.Counter[str],
    target: int,
    seed: int,
) -> dict[str, int]:
    """Water-fill API quotas without assuming more examples than actually exist."""

    require(target > 0, "the public-practice denominator must be positive")
    require(bool(capacities), "the bounded public API capacity is empty")
    require(set(initial) <= set(capacities), "initial selection contains an unknown API")
    require(sum(capacities.values()) >= target, "insufficient bounded public practice examples")
    require(sum(initial.values()) <= target, "mandatory public coverage exceeds the case budget")
    quotas = {api: initial.get(api, 0) for api in sorted(capacities)}
    require(
        all(quotas[api] <= capacities[api] for api in quotas),
        "mandatory public coverage exceeds an API's actual bounded capacity",
    )
    while sum(quotas.values()) < target:
        available = [api for api in quotas if quotas[api] < capacities[api]]
        require(bool(available), "bounded public API capacity was exhausted")
        api = min(available, key=lambda name: (quotas[name], seed_key(seed, f"api:{name}")))
        quotas[api] += 1
    require(sum(quotas.values()) == target, "balanced public API quotas changed their denominator")
    require(
        all(0 < quotas[api] <= capacities[api] for api in quotas),
        "balanced public API quotas exceeded a frozen available workload",
    )
    return quotas


def select_entries(
    pairs: list[Entry],
    target: int,
    seed: int,
    *,
    expected_eligible: int | None = None,
    expected_categories: int | None = None,
    expected_api_counts: dict[str, int] | None = None,
) -> tuple[list[SelectedEntry], dict[str, int]]:
    """Select public rows without calling or changing the 700-case v7 pilot."""

    identifiers: set[str] = set()
    positions: set[int] = set()
    eligible: list[Entry] = []
    for position, case, expected in pairs:
        require(
            isinstance(position, int) and not isinstance(position, bool) and position >= 0,
            "the public-only fixture contains an invalid frozen position",
        )
        require(position not in positions, "the public-only fixture repeats a frozen position")
        positions.add(position)
        require(isinstance(case, dict) and isinstance(expected, dict), "invalid public fixture record")
        require(
            case.get("cohort") == pilot.PRACTICE and expected.get("cohort") == pilot.PRACTICE,
            "a held-out record entered additive public case selection",
        )
        identifier = case.get("id")
        require(isinstance(identifier, str) and bool(identifier), "a public case has no identifier")
        require(identifier not in identifiers, "the public-only fixture repeats a case identifier")
        identifiers.add(identifier)
        require(expected.get("id") == identifier, "a public case and frozen answer disagree")
        require(case.get("category") == expected.get("category"), "a frozen public category changed")
        require(case.get("weight") == 1, "a public case no longer has equal unit weight")
        require(
            pilot.digest(expected.get("result")) == expected.get("result_sha256"),
            "a frozen public CPython answer is corrupt",
        )
        if pilot.bounded(case, expected):
            eligible.append((position, case, expected))

    if expected_eligible is not None:
        require(len(eligible) == expected_eligible, "the bounded public calibration pool changed")
    require(len(eligible) >= target, "insufficient safely bounded public calibration cases")

    by_api: dict[str, list[Entry]] = collections.defaultdict(list)
    by_category: dict[str, list[Entry]] = collections.defaultdict(list)
    for entry in eligible:
        by_api[entry[1]["api"]].append(entry)
        by_category[entry[1]["category"]].append(entry)
    if expected_categories is not None:
        require(len(by_category) == expected_categories, "a bounded public workload category disappeared")
    capacities = collections.Counter({api: len(entries) for api, entries in by_api.items()})
    if expected_api_counts is not None:
        require(dict(sorted(capacities.items())) == expected_api_counts, "bounded public API capacity changed")

    selected: dict[str, Entry] = {}
    reasons: dict[str, set[str]] = collections.defaultdict(set)
    api_counts: collections.Counter[str] = collections.Counter()
    category_counts: collections.Counter[str] = collections.Counter()
    stratum_counts: collections.Counter[tuple[str, str, str, str]] = collections.Counter()

    def ordered(entries: list[Entry]) -> list[Entry]:
        return sorted(entries, key=lambda item: seed_key(seed, item[1]["id"]))

    def add(entry: Entry, reason: str) -> None:
        position, case, expected = entry
        require(case["cohort"] == pilot.PRACTICE, "a hidden case reached public selection")
        require(expected["cohort"] == pilot.PRACTICE, "a hidden answer reached public selection")
        require(pilot.bounded(case, expected), "an overbound case reached public selection")
        identifier = case["id"]
        reasons[identifier].add(reason)
        if identifier in selected:
            return
        selected[identifier] = (position, case, expected)
        api_counts[case["api"]] += 1
        category_counts[case["category"]] += 1
        stratum_counts[stratum(case, expected)] += 1

    for category in sorted(by_category):
        add(ordered(by_category[category])[0], "every-bounded-public-workload-category")

    coverage = (
        ("api-lifetime", lambda case, _expected: (case["api"], case["lifecycle"])),
        ("input-kind", lambda case, _expected: pilot.source_kind(case)),
        ("result-density", lambda _case, expected: pilot.density(expected["result"])),
        ("case-folding", lambda case, _expected: "I" in case.get("flags", ())),
        ("bounded-window", lambda case, _expected: "pos" in case or "endpos" in case),
    )
    for reason, identify in coverage:
        required = {identify(case, expected) for _, case, expected in eligible}
        represented = {identify(case, expected) for _, case, expected in selected.values()}
        for missing in sorted(required - represented, key=str):
            choices = [
                entry for entry in eligible if identify(entry[1], entry[2]) == missing
            ]
            require(bool(choices), f"a public coverage stratum disappeared: {reason}")
            add(ordered(choices)[0], reason)

    quotas = allocate_quotas(capacities, api_counts, target, seed)
    for api in sorted(quotas, key=lambda name: seed_key(seed, f"api:{name}")):
        while api_counts[api] < quotas[api]:
            remaining = [
                entry for entry in by_api[api] if entry[1]["id"] not in selected
            ]
            require(bool(remaining), f"bounded public API capacity is exhausted: {api}")
            entry = min(
                remaining,
                key=lambda item: (
                    category_counts[item[1]["category"]],
                    stratum_counts[stratum(item[1], item[2])],
                    seed_key(seed, item[1]["id"]),
                ),
            )
            add(entry, "seeded-capacity-balanced-public-api")

    require(len(selected) == target, "the additive public case denominator changed")
    require(dict(sorted(api_counts.items())) == quotas, "balanced public API quotas changed")
    require(set(category_counts) == set(by_category), "an existing public category was omitted")
    for reason, identify in coverage:
        require(
            {identify(case, expected) for _, case, expected in selected.values()}
            == {identify(case, expected) for _, case, expected in eligible},
            f"an available bounded public coverage stratum was omitted: {reason}",
        )
    result = [
        (position, case, expected, tuple(sorted(reasons[identifier])))
        for identifier, (position, case, expected) in selected.items()
    ]
    result.sort(key=lambda item: item[0])
    return result, quotas


def verified_from_scratch_audit() -> tuple[str, dict[str, str], dict[str, str]]:
    require_candidate_free()
    document = read_json(AUDIT_PATH, "from-scratch independence audit")
    sources, native = replay.validate_independence(document)
    require(len(native) == 5, "the public practice must verify all five owned native libraries")
    require_candidate_free()
    return pilot.file_sha256(AUDIT_PATH), sources, native


def make_manifest(edge_paths: list[Path]) -> tuple[types.SimpleNamespace, list[SelectedEntry], dict[str, Any]]:
    require_candidate_free()
    require_pinned_python()
    require(pilot.MAX_CASES == 700, "the immutable original public-pilot case bound changed")
    require(pilot.MAX_SUBJECT == 8_192, "the immutable original public subject bound changed")
    require(pilot.MAX_RESULTS == 128, "the immutable original public result bound changed")
    require(pilot.MAX_OPERATIONS == MAX_OPERATIONS, "the immutable operation safety bound changed")

    source_suite, pairs, parent, _history, fixture_manifest = pilot.load_calibration_fixture()
    require(len(pairs) == FIXTURE_CASES, "the sealed public-only fixture denominator changed")
    require(source_suite.CASES_PER_COHORT == FIXTURE_CASES, "the public-only cohort weight changed")
    require(source_suite.TRIALS == TRIALS, "the frozen public trial protocol changed")
    require(source_suite.WARMUPS == 4, "the frozen public warmup protocol changed")
    require(source_suite.BOOTSTRAPS == BOOTSTRAPS, "the frozen public confidence protocol changed")
    require(set(source_suite.SEEDS) == {pilot.PRACTICE}, "a nonpublic seed entered practice")
    require(set(MODULES) <= set(source_suite.MODULES), "an independently qualified engine is missing")
    require(len({SELECTION_SEED, ORDER_SEED, BOOTSTRAP_SEED}) == 3, "public seeds overlap")
    require(
        not {SELECTION_SEED, ORDER_SEED, BOOTSTRAP_SEED}
        & {
            source_suite.SEEDS[pilot.PRACTICE],
            source_suite.ORDER_SEED,
            source_suite.BOOTSTRAP_SEED,
        },
        "a fresh public-practice seed reuses a historical public seed",
    )

    entries, quotas = select_entries(
        pairs,
        CASES,
        SELECTION_SEED,
        expected_eligible=ELIGIBLE_CASES,
        expected_categories=CATEGORIES,
        expected_api_counts=EXPECTED_BOUNDED_API_COUNTS,
    )
    suite = types.SimpleNamespace(
        MODULES=source_suite.MODULES,
        CASES_PER_COHORT=source_suite.CASES_PER_COHORT,
        SEEDS={pilot.PRACTICE: SELECTION_SEED},
        ORDER_SEED=ORDER_SEED,
        BOOTSTRAP_SEED=BOOTSTRAP_SEED,
        TRIALS=TRIALS,
        WARMUPS=source_suite.WARMUPS,
        BOOTSTRAPS=BOOTSTRAPS,
    )

    categories = collections.Counter(case["category"] for _, case, _, _ in entries)
    lifetimes = collections.Counter(case["lifecycle"] for _, case, _, _ in entries)
    inputs = collections.Counter(pilot.source_kind(case) for _, case, _, _ in entries)
    densities = collections.Counter(pilot.density(expected["result"]) for _, _, expected, _ in entries)
    api_lifetimes = collections.Counter(
        (case["api"], case["lifecycle"]) for _, case, _, _ in entries
    )
    eligible = [(position, case, expected) for position, case, expected in pairs if pilot.bounded(case, expected)]
    require(len(categories) == CATEGORIES, "an existing bounded public category was omitted")
    require(len(quotas) == PUBLIC_APIS, "a public regular-expression operation was omitted")
    require(
        set(lifetimes) == {case["lifecycle"] for _, case, _ in eligible},
        "an available public pattern lifecycle was omitted",
    )
    require(
        set(inputs) == {pilot.source_kind(case) for _, case, _ in eligible},
        "an available public text or buffer representation was omitted",
    )
    require(
        set(densities) == {pilot.density(expected["result"]) for _, _, expected in eligible},
        "an available public result-density stratum was omitted",
    )
    require(
        set(api_lifetimes)
        == {(case["api"], case["lifecycle"]) for _, case, _ in eligible},
        "an available public API and lifecycle pair was omitted",
    )

    audit_digest, source_fingerprints, native_fingerprints = verified_from_scratch_audit()
    require(len(edge_paths) == len(MODULES) - 1, "each native candidate requires its own correctness proof")
    edge_oracles = pilot.verified_edge_oracles(edge_paths, MODULES)
    require(len(edge_oracles) == len(MODULES) - 1, "an independently qualified engine was omitted")
    require_candidate_free()

    document: dict[str, Any] = {
        "schema": pilot.PLAN_SCHEMA,
        "postfinal_schema": POSTFINAL_PLAN_SCHEMA,
        "protocol_version": VERSION,
        "measurement": "balanced practice diagnostic; never a holdout ranking or final speed claim",
        "measurement_role": "additive post-final public practice only; not a held-out or final result",
        "python": parent["python"],
        "cohort": pilot.PRACTICE,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "historical_performance_read": False,
        "timing_performed": False,
        "expected_sha256": parent["expected_sha256"],
        "source_fixture": fixture_manifest["fixture"],
        "source_fixture_sha256": fixture_manifest["fixture_sha256"],
        "source_fixture_uncompressed_sha256": fixture_manifest["uncompressed_fixture_sha256"],
        "source_fixture_manifest_sha256": pilot.file_sha256(pilot.DEFAULT_FIXTURE_MANIFEST),
        "source_v7_manifest_sha256": fixture_manifest["source_v7_manifest_sha256"],
        "source_v7_suite_sha256": fixture_manifest["source_v7_suite_sha256"],
        "source_v7_runner_sha256": fixture_manifest["source_v7_runner_sha256"],
        "source_public_pilot_sha256": pilot.file_sha256(Path(pilot.__file__).resolve()),
        "source_public_replay_sha256": pilot.file_sha256(Path(replay.__file__).resolve()),
        "runner_sha256": pilot.file_sha256(Path(__file__).resolve()),
        "from_scratch_audit_path": str(AUDIT_PATH.resolve()),
        "from_scratch_audit_sha256": audit_digest,
        "qualified_source_fingerprints": source_fingerprints,
        "native_elf_fingerprints": native_fingerprints,
        "verified_edge_oracles": edge_oracles,
        "modules": list(MODULES),
        "exclusive_slot": EXCLUSIVE_SLOT,
        "selection_seed": SELECTION_SEED,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "frozen_trials": TRIALS,
        "frozen_warmups": suite.WARMUPS,
        "frozen_bootstrap_samples": BOOTSTRAPS,
        "default_trials": TRIALS,
        "default_bootstrap_samples": BOOTSTRAPS,
        "cases": len(entries),
        "source_public_cases": FIXTURE_CASES,
        "eligible_practice_cases": ELIGIBLE_CASES,
        "all_bounded_workload_categories": len(categories),
        "bounded_public_api_capacities": dict(sorted(EXPECTED_BOUNDED_API_COUNTS.items())),
        "public_operations": quotas,
        "lifetimes": dict(sorted(lifetimes.items())),
        "inputs": dict(sorted(inputs.items())),
        "result_densities": dict(sorted(densities.items())),
        "api_lifetimes": {
            f"{api} / {lifecycle}": count
            for (api, lifecycle), count in sorted(api_lifetimes.items())
        },
        "categories": dict(sorted(categories.items())),
        "maximum_subject_length": max(
            pilot.input_length(case) for _, case, _, _ in entries
        ),
        "maximum_result_count": max(
            pilot.cardinality(expected["result"]) for _, _, expected, _ in entries
        ),
        "maximum_subject_limit": pilot.MAX_SUBJECT,
        "maximum_result_limit": pilot.MAX_RESULTS,
        "maximum_operations_per_trial": MAX_OPERATIONS,
        "strict_regression_speedup_threshold": pilot.REGRESSION_SPEEDUP_THRESHOLD,
        "execution_safety": (
            "Exactly four fixed independent engines; an exclusive post-final public slot; "
            "frozen calibration-only cases; and pre-timing, allocation-sample, and "
            "post-timing CPython correctness gates for every paired observation."
        ),
        "selected_cases": [
            {
                "case": case["id"],
                "cohort": case["cohort"],
                "category": case["category"],
                "api": case["api"],
                "lifecycle": case["lifecycle"],
                "input": pilot.source_kind(case),
                "subject_length": pilot.input_length(case),
                "result_count": pilot.cardinality(expected["result"]),
                "result_density": pilot.density(expected["result"]),
                "frozen_operations": case["ops"],
                "expected_result_sha256": expected["result_sha256"],
                "selection_reasons": list(reasons),
            }
            for _, case, expected, reasons in entries
        ],
        "failed": 0,
    }
    require(document["maximum_subject_length"] <= pilot.MAX_SUBJECT, "public subject bound weakened")
    require(document["maximum_result_count"] <= pilot.MAX_RESULTS, "public result bound weakened")
    require(document["strict_regression_speedup_threshold"] == 5.0 / 6.0, "strict regression boundary weakened")
    return suite, entries, document


def load_frozen_manifest(path: Path) -> tuple[types.SimpleNamespace, list[SelectedEntry], dict[str, Any], str]:
    manifest_path = exact_versioned_path(path, MANIFEST_PATH, "frozen public practice manifest")
    document = read_json(manifest_path, "additive public practice manifest")
    require(document.get("postfinal_schema") == POSTFINAL_PLAN_SCHEMA, "incorrect additive manifest schema")
    require(document.get("protocol_version") == VERSION, "incorrect additive public protocol version")
    proofs = document.get("verified_edge_oracles")
    require(isinstance(proofs, list), "the frozen independent correctness proofs are missing")
    paths: list[Path] = []
    for proof in proofs:
        require(isinstance(proof, dict) and isinstance(proof.get("path"), str), "invalid frozen independent correctness proof")
        paths.append(Path(proof["path"]))
    suite, entries, actual = make_manifest(paths)
    require(document == actual, "the immutable public manifest, sources, candidates, or cases changed")
    return suite, entries, document, pilot.file_sha256(manifest_path)


def synthetic_self_test() -> dict[str, Any]:
    """Exercise only generated in-memory controls; never open or run a case."""

    require_candidate_free()
    inherited = replay.self_test()
    require(
        inherited.get("result") == "PASS"
        and inherited.get("holdout_accessed") is False
        and inherited.get("timing_performed") is False
        and inherited.get("poisoned_control_count", 0) >= 28,
        "the inherited candidate-free paired-replay corruption controls failed",
    )

    synthetic: list[Entry] = []
    for api_index, api in enumerate(sorted(EXPECTED_BOUNDED_API_COUNTS)):
        for variant in range(8 + api_index % 4):
            identifier = f"cal.postfinal.synthetic.{api}.{variant:02d}"
            use_bytes = variant % 5 == 0
            result: Any = None if variant % 4 == 0 else ["synthetic"] * (1 + variant % 3)
            lifecycle = "cold" if api == "compile" else "module" if api == "escape" else "compiled"
            case: dict[str, Any] = {
                "id": identifier,
                "cohort": pilot.PRACTICE,
                "category": f"synthetic-{api}-{variant % 2}",
                "api": api,
                "lifecycle": lifecycle,
                "pattern": b"synthetic" if use_bytes else "synthetic",
                "string": b"synthetic" if use_bytes else "synthetic",
                "flags": ["I"] if variant % 3 == 0 else [],
                "ops": MAX_OPERATIONS,
                "weight": 1,
            }
            if use_bytes:
                case["subject_kind"] = ("bytes", "bytearray", "memoryview")[variant % 3]
            if variant % 4 == 1:
                case["pos"] = 0
            expected = {
                "id": identifier,
                "cohort": pilot.PRACTICE,
                "category": case["category"],
                "result": result,
                "result_sha256": pilot.digest(result),
            }
            synthetic.append((len(synthetic), case, expected))

    selected, quotas = select_entries(
        synthetic,
        64,
        SELECTION_SEED,
        expected_eligible=len(synthetic),
        expected_categories=24,
    )
    repeated, repeated_quotas = select_entries(
        list(reversed(synthetic)),
        64,
        SELECTION_SEED,
        expected_eligible=len(synthetic),
        expected_categories=24,
    )
    require(selected == repeated and quotas == repeated_quotas, "public selection is not deterministic")
    require(len(quotas) == PUBLIC_APIS and sum(quotas.values()) == 64, "synthetic API balance changed")
    require(len({case["category"] for _, case, _, _ in selected}) == 24, "synthetic category coverage changed")
    require(all(pilot.bounded(case, expected) for _, case, expected, _ in selected), "synthetic selection exceeded a safety bound")

    controls: list[dict[str, Any]] = []

    def reject(name: str, action: Any) -> None:
        try:
            action()
        except (RuntimeError, replay.AuditError, KeyError, TypeError, ValueError):
            controls.append({"name": name, "passed": True})
            return
        raise RuntimeError(f"synthetic public isolation control was accepted: {name}")

    first_position, first_case, first_expected = synthetic[0]

    def substitute(case: dict[str, Any], expected: dict[str, Any]) -> list[Entry]:
        return [(first_position, case, expected), *synthetic[1:]]

    reject(
        "hidden-case-cohort",
        lambda: select_entries(
            substitute({**first_case, "cohort": "holdout"}, first_expected), 64, SELECTION_SEED
        ),
    )
    reject(
        "hidden-expected-cohort",
        lambda: select_entries(
            substitute(first_case, {**first_expected, "cohort": "holdout"}), 64, SELECTION_SEED
        ),
    )
    reject(
        "substituted-frozen-answer",
        lambda: select_entries(
            substitute(first_case, {**first_expected, "result_sha256": "0" * 64}),
            64,
            SELECTION_SEED,
        ),
    )
    reject(
        "unequal-case-weight",
        lambda: select_entries(
            substitute({**first_case, "weight": 2}, first_expected), 64, SELECTION_SEED
        ),
    )
    reject(
        "duplicate-frozen-case",
        lambda: select_entries([*synthetic, synthetic[0]], 64, SELECTION_SEED),
    )
    reject(
        "missing-public-category",
        lambda: select_entries(synthetic, 64, SELECTION_SEED, expected_categories=25),
    )
    reject(
        "changed-public-denominator",
        lambda: select_entries(synthetic, 64, SELECTION_SEED, expected_eligible=len(synthetic) + 1),
    )
    reject(
        "oversubscribed-api-capacity",
        lambda: allocate_quotas(collections.Counter({"search": 1}), collections.Counter(), 2, SELECTION_SEED),
    )
    reject(
        "historical-manifest-path",
        lambda: exact_versioned_path(pilot.DEFAULT_PLAN, MANIFEST_PATH, "synthetic public manifest"),
    )
    reject(
        "historical-raw-path",
        lambda: exact_versioned_path(
            ROOT / "performance/v7/evidence/three-qualified-engines-public-practice-v1-raw.jsonl.gz",
            RAW_PATH,
            "synthetic public raw observations",
        ),
    )
    require(pilot.MAX_CASES == 700, "a synthetic control changed the original 700-case bound")
    require(pilot.MAX_SUBJECT == 8_192 and pilot.MAX_RESULTS == 128, "a synthetic control weakened a frozen bound")
    require(pilot.REGRESSION_SPEEDUP_THRESHOLD == 5.0 / 6.0, "a synthetic control weakened the regression boundary")
    require_candidate_free()
    return {
        "schema": POSTFINAL_INTEGRITY_SCHEMA + "-self-test",
        "result": "PASS",
        "protocol_version": VERSION,
        "synthetic_only": True,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "timing_performed": False,
        "candidate_imported": False,
        "synthetic_cases": 64,
        "synthetic_public_operations": len(quotas),
        "synthetic_categories": 24,
        "inherited_poisoned_control_count": inherited["poisoned_control_count"],
        "postfinal_poisoned_control_count": len(controls),
        "postfinal_poisoned_controls": controls,
        "strict_regression_speedup_threshold": pilot.REGRESSION_SPEEDUP_THRESHOLD,
        "original_pilot_max_cases": pilot.MAX_CASES,
        "failed": 0,
    }


def freeze(args: argparse.Namespace) -> dict[str, Any]:
    require_candidate_free()
    target = exact_versioned_path(args.output, MANIFEST_PATH, "frozen public practice manifest")
    edge_paths = list(args.edge_oracle) if args.edge_oracle else list(DEFAULT_EDGE_ORACLES)
    _suite, entries, manifest = make_manifest(edge_paths)
    manifest_sha256 = pilot.save_json(target, manifest, replace_identical=True)
    require_candidate_free()
    return {
        "schema": POSTFINAL_PLAN_SCHEMA,
        "result": "PASS",
        "protocol_version": VERSION,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "timing_performed": False,
        "cases": len(entries),
        "source_public_cases": FIXTURE_CASES,
        "eligible_practice_cases": ELIGIBLE_CASES,
        "all_bounded_workload_categories": CATEGORIES,
        "public_operations": manifest["public_operations"],
        "trials": TRIALS,
        "bootstrap_draws": BOOTSTRAPS,
        "verified_independent_engine_count": len(MODULES) - 1,
        "verified_native_library_count": len(manifest["native_elf_fingerprints"]),
        "manifest": str(target),
        "manifest_sha256": manifest_sha256,
        "failed": 0,
    }


def measure(args: argparse.Namespace) -> dict[str, Any]:
    require_candidate_free()
    require_pinned_python()
    require(args.exclusive_slot == EXCLUSIVE_SLOT, "the unique post-final public timing slot was not authorized")
    require(args.cases == CASES, "the frozen 4,096-case public denominator cannot be changed")
    require(args.trials == TRIALS, "the frozen 13 paired public trials cannot be changed")
    require(args.bootstraps == BOOTSTRAPS, "the frozen 2,000 public bootstrap draws cannot be changed")
    require(args.max_operations == MAX_OPERATIONS, "the frozen 16-operation safety bound cannot be changed")
    suite, entries, plan, manifest_sha256 = load_frozen_manifest(args.manifest)
    raw_path = exact_versioned_path(args.raw, RAW_PATH, "public paired raw observations")
    summary_path = exact_versioned_path(args.output, SUMMARY_PATH, "public paired summary")
    require(not raw_path.exists(), "refusing to overwrite additive public raw observations")
    require(not summary_path.exists(), "refusing to overwrite the additive public practice summary")
    requested = list(args.module) if args.module else list(MODULES)
    names = pilot.selected_modules(suite, requested)
    require(names == MODULES, "public timing must retain Python, Rust, C, and Zig in frozen order")

    audit_digest, source_fingerprints, native_fingerprints = verified_from_scratch_audit()
    require(audit_digest == plan["from_scratch_audit_sha256"], "the frozen from-scratch proof changed")
    require(source_fingerprints == plan["qualified_source_fingerprints"], "an independently owned engine source changed")
    require(native_fingerprints == plan["native_elf_fingerprints"], "an independently owned native library changed")
    edge_oracles = plan["verified_edge_oracles"]
    require_candidate_free()

    modules = {name: importlib.import_module(name) for name in names}
    fingerprints_before = pilot.module_fingerprints(modules)
    pilot.match_reported_fingerprints(edge_oracles, fingerprints_before)
    replay.validate_measured_fingerprints(
        {
            "candidate_binary_sha256_before": fingerprints_before,
            "candidate_binary_sha256_after": fingerprints_before,
        },
        source_fingerprints,
        native_fingerprints,
    )

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    observed: dict[tuple[str, int, str], dict[str, Any]] = {}
    raw_digest = hashlib.sha256()
    correctness_checks = 0
    with raw_path.open("xb") as destination:
        with gzip.GzipFile(
            filename="", fileobj=destination, mode="wb", compresslevel=9, mtime=0
        ) as compressed:
            for position, (_index, case, expected, reasons) in enumerate(entries, 1):
                require(case["cohort"] == pilot.PRACTICE, "a hidden case reached authorized public timing")
                actions = {name: pilot.operation(module, case) for name, module in modules.items()}
                operations = min(case["ops"], MAX_OPERATIONS)
                for trial in range(TRIALS):
                    order = pilot.trial_order(names, case["id"], trial, ORDER_SEED)
                    for order_index, name in enumerate(order):
                        action = actions[name]
                        expected_digest = pilot.correctness_gate(modules[name], case, expected)
                        correctness_checks += 1
                        for _ in range(suite.WARMUPS):
                            action()

                        tracemalloc.start()
                        try:
                            sampled = action()
                            _current, peak = tracemalloc.get_traced_memory()
                        finally:
                            tracemalloc.stop()
                        pilot.exact_snapshot(sampled, expected, expected_digest, f"memory: {name} {case['id']}")
                        correctness_checks += 1

                        before_memory = pilot.proc_memory()
                        previously_enabled = gc.isenabled()
                        if previously_enabled:
                            gc.disable()
                        try:
                            start = time.perf_counter_ns()
                            result = None
                            for _ in range(operations):
                                result = action()
                            elapsed = time.perf_counter_ns() - start
                        finally:
                            if previously_enabled:
                                gc.enable()
                        after_memory = pilot.proc_memory()
                        pilot.exact_snapshot(result, expected, expected_digest, f"post-timing: {name} {case['id']}")
                        correctness_checks += 1
                        require(elapsed > 0, f"nonpositive public timing: {name} {case['id']}")

                        row: dict[str, Any] = {
                            "schema": pilot.ROW_SCHEMA,
                            "measurement": "bounded practice diagnostic only; not a holdout result",
                            "case": case["id"],
                            "cohort": pilot.PRACTICE,
                            "category": case["category"],
                            "api": case["api"],
                            "lifecycle": case["lifecycle"],
                            "input": pilot.source_kind(case),
                            "result_density": pilot.density(expected["result"]),
                            "selection_reasons": list(reasons),
                            "module": name,
                            "trial": trial,
                            "order": order_index,
                            "operations": operations,
                            "frozen_operations": case["ops"],
                            "elapsed_ns": elapsed,
                            "ns_per_op": elapsed / operations,
                            "peak_traced_bytes": peak,
                            "rss_before_kb": before_memory["rss_kb"],
                            "rss_after_kb": after_memory["rss_kb"],
                            "hwm_kb": after_memory["hwm_kb"],
                            "expected_sha256": expected_digest,
                        }
                        require(pilot.valid_process_memory(row), "invalid public paired process memory")
                        key = (case["id"], trial, name)
                        require(key not in observed, f"duplicate public paired timing observation: {key!r}")
                        encoded = (
                            json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                            + "\n"
                        ).encode("utf-8")
                        raw_digest.update(encoded)
                        compressed.write(encoded)
                        observed[key] = row

                if position % 32 == 0 or position == len(entries):
                    print(
                        json.dumps(
                            {
                                "schema": POSTFINAL_REPORT_SCHEMA + "-progress",
                                "protocol_version": VERSION,
                                "cohort": pilot.PRACTICE,
                                "holdout_accessed": False,
                                "completed": position,
                                "cases": len(entries),
                            },
                            sort_keys=True,
                        ),
                        flush=True,
                    )

    required_rows = CASES * TRIALS * len(MODULES)
    require(len(observed) == required_rows, "the public paired timing denominator changed")
    require(correctness_checks == 3 * required_rows, "a public correctness gate was omitted")
    fingerprints_after = pilot.module_fingerprints(modules)
    require(fingerprints_after == fingerprints_before, "a native implementation changed during public timing")
    pilot.match_reported_fingerprints(edge_oracles, fingerprints_after)
    results, rankings = pilot.summarize_measurements(
        suite, entries, names, observed, TRIALS, BOOTSTRAPS
    )
    require(len(results) == CASES * (len(MODULES) - 1), "a public candidate-case result was omitted")

    summary: dict[str, Any] = {
        "schema": pilot.REPORT_SCHEMA,
        "postfinal_schema": POSTFINAL_REPORT_SCHEMA,
        "protocol_version": VERSION,
        "measurement": "balanced practice diagnostic only; not a holdout result or final speed claim",
        "measurement_role": "additive post-final public practice only; not a held-out or final result",
        "cohort": pilot.PRACTICE,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "exclusive_slot": EXCLUSIVE_SLOT,
        "manifest_path": str(MANIFEST_PATH.resolve()),
        "manifest_sha256": manifest_sha256,
        "from_scratch_audit_sha256": audit_digest,
        "verified_edge_oracles": edge_oracles,
        "expected_sha256": plan["expected_sha256"],
        "selection_seed": SELECTION_SEED,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "modules": list(names),
        "cases": CASES,
        "all_bounded_workload_categories": CATEGORIES,
        "public_operations": plan["public_operations"],
        "lifetimes": plan["lifetimes"],
        "inputs": plan["inputs"],
        "result_densities": plan["result_densities"],
        "api_lifetimes": plan["api_lifetimes"],
        "trials": TRIALS,
        "warmups": suite.WARMUPS,
        "maximum_operations_per_trial": MAX_OPERATIONS,
        "bootstrap_samples": BOOTSTRAPS,
        "strict_regression_speedup_threshold": pilot.REGRESSION_SPEEDUP_THRESHOLD,
        "raw_path": str(raw_path),
        "raw_sha256": raw_digest.hexdigest(),
        "compressed_raw_sha256": pilot.file_sha256(raw_path),
        "paired_raw_rows": required_rows,
        "correctness_checks": correctness_checks,
        "candidate_binary_sha256_before": fingerprints_before,
        "candidate_binary_sha256_after": fingerprints_after,
        "case_results": results,
        "rankings": rankings,
        "regressions": [row for row in results if row["regression_gt_20pct"]],
        "failed": 0,
    }
    replay.validate_measured_fingerprints(summary, source_fingerprints, native_fingerprints)
    summary_sha256 = pilot.save_json(summary_path, summary)
    return {
        "schema": POSTFINAL_REPORT_SCHEMA,
        "result": "PASS",
        "protocol_version": VERSION,
        "measurement": "additive public practice only; not a final or held-out result",
        "cohort": pilot.PRACTICE,
        "holdout_accessed": False,
        "cases": CASES,
        "modules": list(names),
        "paired_trials": TRIALS,
        "bootstrap_draws": BOOTSTRAPS,
        "paired_raw_rows": required_rows,
        "correctness_checks": correctness_checks,
        "confidence_intervals": len(results) + len(rankings),
        "strict_regressions": len(summary["regressions"]),
        "raw_sha256": raw_digest.hexdigest(),
        "compressed_raw_sha256": summary["compressed_raw_sha256"],
        "summary_sha256": summary_sha256,
        "from_scratch_audit_sha256": audit_digest,
        "failed": 0,
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    """Replay frozen public evidence and independence without importing candidates."""

    require_candidate_free()
    require_pinned_python()
    _suite, entries, plan, manifest_sha256 = load_frozen_manifest(args.manifest)
    raw_path = exact_versioned_path(args.raw, RAW_PATH, "verified public raw observations")
    summary_path = exact_versioned_path(args.summary, SUMMARY_PATH, "verified public summary")
    output_path = exact_versioned_path(args.output, INTEGRITY_PATH, "public integrity evidence")
    require(not output_path.exists(), "refusing to overwrite independent public integrity evidence")
    summary = read_json(summary_path, "recorded public practice summary")
    require(summary.get("postfinal_schema") == POSTFINAL_REPORT_SCHEMA, "public summary version changed")
    require(summary.get("protocol_version") == VERSION, "public summary protocol changed")
    require(summary.get("exclusive_slot") == EXCLUSIVE_SLOT, "public summary substituted its frozen slot")
    require(summary.get("raw_path") == str(raw_path), "public summary substituted its raw observations")
    require(summary.get("manifest_path") == str(MANIFEST_PATH.resolve()), "public summary substituted its manifest")
    require(summary.get("manifest_sha256") == manifest_sha256, "public summary changed its frozen manifest")
    require(summary.get("from_scratch_audit_sha256") == plan["from_scratch_audit_sha256"], "public summary changed its independence proof")
    require(summary.get("verified_edge_oracles") == plan["verified_edge_oracles"], "public summary changed its correctness proofs")
    require(summary.get("held_out_cases_generated") == 0, "public replay generated a held-out case")
    require(summary.get("held_out_records_deserialized") == 0, "public replay decoded a held-out case")
    require(
        summary.get("measurement")
        == "balanced practice diagnostic only; not a holdout result or final speed claim",
        "public evidence was falsely represented as final performance",
    )

    profile = replay.Profile(
        cases=CASES,
        trials=TRIALS,
        bootstraps=BOOTSTRAPS,
        categories=CATEGORIES,
        apis=PUBLIC_APIS,
    )
    replay.validate_plan(plan, profile)
    replay.validate_header(summary, plan, profile, None)
    audit_digest, sources, native = verified_from_scratch_audit()
    require(audit_digest == plan["from_scratch_audit_sha256"], "the frozen from-scratch proof changed before replay")
    require(sources == plan["qualified_source_fingerprints"], "a qualified source changed before replay")
    require(native == plan["native_elf_fingerprints"], "an owned native library changed before replay")
    measured = replay.validate_measured_fingerprints(summary, sources, native)
    compressed_sha256 = pilot.file_sha256(raw_path)
    require(compressed_sha256 == summary.get("compressed_raw_sha256"), "compressed public evidence changed")
    with raw_path.open("rb") as source:
        observations = replay.read_observations(source, compressed_sha256, summary, plan, profile)
    results, rankings = replay.recompute_results(plan, observations, profile)
    regressions = replay.validate_results(summary, results, rankings, profile)
    controls = synthetic_self_test()
    require_candidate_free()

    document: dict[str, Any] = {
        "schema": POSTFINAL_INTEGRITY_SCHEMA,
        "result": "PASS",
        "protocol_version": VERSION,
        "measurement": "independent replay of additive public practice; not a final or held-out result",
        "cohort": pilot.PRACTICE,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "timing_performed": False,
        "candidate_imported": False,
        "module_order": list(MODULES),
        "cases_per_candidate": len(entries),
        "candidate_case_count": len(results),
        "trials_per_module_case": TRIALS,
        "raw_rows": len(observations),
        "correctness_checks": len(observations) * 3,
        "bootstrap_draws": BOOTSTRAPS,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "strict_regression_speedup_threshold": pilot.REGRESSION_SPEEDUP_THRESHOLD,
        "strict_regressions": len(regressions),
        "manifest_sha256": manifest_sha256,
        "summary_sha256": pilot.file_sha256(summary_path),
        "compressed_raw_sha256": compressed_sha256,
        "raw_sha256": summary["raw_sha256"],
        "from_scratch_audit_sha256": audit_digest,
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": len(MODULES) - 1,
        "verified_native_library_count": len(native),
        "qualified_source_fingerprints": sources,
        "native_elf_fingerprints": native,
        "candidate_binary_sha256_before": measured,
        "candidate_binary_sha256_after": measured,
        "verified_edge_oracles": plan["verified_edge_oracles"],
        "rankings": rankings,
        "regressions": regressions,
        "self_test": controls,
        "memory_limitation": (
            "Peak ratios are Python-traced allocations only. Shared-process RSS and "
            "high-water marks do not establish isolated native-engine memory."
        ),
        "failed": 0,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    integrity_sha256 = pilot.save_json(output_path, document)
    return {
        "schema": POSTFINAL_INTEGRITY_SCHEMA,
        "result": "PASS",
        "protocol_version": VERSION,
        "holdout_accessed": False,
        "timing_performed": False,
        "candidate_imported": False,
        "cases_per_candidate": CASES,
        "candidate_case_count": len(results),
        "trials_per_module_case": TRIALS,
        "raw_rows": len(observations),
        "correctness_checks": len(observations) * 3,
        "bootstrap_draws": BOOTSTRAPS,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "strict_regressions": len(regressions),
        "verified_native_library_count": len(native),
        "inherited_poisoned_control_count": controls["inherited_poisoned_control_count"],
        "postfinal_poisoned_control_count": controls["postfinal_poisoned_control_count"],
        "output": str(output_path),
        "sha256": integrity_sha256,
        "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    test = commands.add_parser("self-test", help="run only candidate-free in-memory corruption controls")
    test.set_defaults(handler=lambda _args: synthetic_self_test())

    plan = commands.add_parser("freeze", help="freeze one additive calibration-only public manifest")
    plan.add_argument("--output", type=Path, default=MANIFEST_PATH)
    plan.add_argument(
        "--edge-oracle",
        type=Path,
        action="append",
        help="independent public correctness proof; repeat exactly once for Rust, C, and Zig",
    )
    plan.set_defaults(handler=freeze)

    live = commands.add_parser("measure", help="perform only an explicitly authorized public timing run")
    live.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    live.add_argument("--exclusive-slot", required=True)
    live.add_argument("--cases", type=pilot.positive_int, default=CASES)
    live.add_argument("--raw", type=Path, default=RAW_PATH)
    live.add_argument("--output", type=Path, default=SUMMARY_PATH)
    live.add_argument("--module", action="append")
    live.add_argument("--trials", type=pilot.positive_int, default=TRIALS)
    live.add_argument("--max-operations", type=pilot.positive_int, default=MAX_OPERATIONS)
    live.add_argument("--bootstraps", type=pilot.positive_int, default=BOOTSTRAPS)
    live.set_defaults(handler=measure)

    check = commands.add_parser("verify", help="independently replay recorded public evidence without importing candidates")
    check.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    check.add_argument("--raw", type=Path, default=RAW_PATH)
    check.add_argument("--summary", type=Path, default=SUMMARY_PATH)
    check.add_argument("--output", type=Path, default=INTEGRITY_PATH)
    check.set_defaults(handler=verify)

    args = parser.parse_args()
    try:
        result = args.handler(args)
    except (
        RuntimeError,
        replay.AuditError,
        OSError,
        KeyError,
        TypeError,
        ValueError,
        OverflowError,
        RecursionError,
        UnicodeError,
        json.JSONDecodeError,
    ) as error:
        print(
            json.dumps(
                {
                    "schema": POSTFINAL_INTEGRITY_SCHEMA,
                    "result": "FAIL",
                    "protocol_version": VERSION,
                    "holdout_accessed": False,
                    "timing_performed": False,
                    "error": str(error),
                    "failed": 1,
                },
                sort_keys=True,
            )
        )
        raise SystemExit(1) from error
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
