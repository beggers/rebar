#!/usr/bin/env python3
"""Plan or explicitly authorize bounded, calibration-only Rust experiments."""

from __future__ import annotations

import argparse
import collections
import gc
import gzip
import hashlib
import importlib
import json
import math
import random
import statistics
import subprocess
import time
import tracemalloc
import types
from pathlib import Path

from tools.perf_v5 import digest, operation, proc_memory, snapshot, source_kind
from tools.perf_v7 import (
    EXPECTED_PATH,
    MANIFEST_PATH,
    REGRESSION_SPEEDUP_THRESHOLD,
    ROOT,
    SUITE_PATH,
    correctness_gate,
    is_runtime_regression,
    valid_process_memory,
    verify_regression_boundaries,
)


PLAN_SCHEMA = "rebar-rust-balanced-calibration-plan-v7"
ROW_SCHEMA = "rebar-rust-balanced-calibration-row-v7"
REPORT_SCHEMA = "rebar-rust-balanced-calibration-pilot-v7"
EDGE_SCHEMA = "rebar-v7-independent-edge-oracle-v1"
FIXTURE_SCHEMA = "rebar-rust-sealed-calibration-fixture-v7"
FIXTURE_MANIFEST_SCHEMA = "rebar-rust-sealed-calibration-fixture-manifest-v7"
PRIORITIES_SCHEMA = "rebar-rust-practice-priorities-v7"
PRACTICE = "calibration"
BASELINE = "re"
RUST = "candidates.rust_candidate"
DEFAULT_CASES = 624
MIN_CASES = 300
MAX_CASES = 700
MIN_CASES_PER_API = 40
MAX_SUBJECT = 8192
MAX_RESULTS = 128
MAX_OPERATIONS = 16
DEFAULT_TRIALS = 7
DEFAULT_BOOTSTRAPS = 499
DEFAULT_PLAN = ROOT / "candidates/evidence/rust-v7-calibration-plan.json"
DEFAULT_FIXTURE = ROOT / "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
DEFAULT_FIXTURE_MANIFEST = ROOT / "performance/v7/evidence/rust-calibration-fixture-manifest.json"
DEFAULT_PRIORITIES_ARCHIVE = (
    ROOT / "candidates/evidence/rust-v7-calibration-priorities-rejected-mixed-loader.json.gz"
)


def forbidden_full_cohort(*_args: object, **_kwargs: object) -> object:
    raise RuntimeError("full-cohort performance generation is forbidden in calibration")


def pack_calibration_value(value: object) -> object:
    if isinstance(value, bytes):
        return {"__rebar_calibration_type__": "bytes", "hex": value.hex()}
    if isinstance(value, bytearray):
        return {"__rebar_calibration_type__": "bytearray", "hex": bytes(value).hex()}
    if isinstance(value, memoryview):
        return {"__rebar_calibration_type__": "memoryview", "hex": bytes(value).hex()}
    if isinstance(value, tuple):
        return {
            "__rebar_calibration_type__": "tuple",
            "items": [pack_calibration_value(item) for item in value],
        }
    if isinstance(value, list):
        return [pack_calibration_value(item) for item in value]
    if isinstance(value, dict):
        require(
            "__rebar_calibration_type__" not in value,
            "reserved calibration serialization marker",
        )
        return {key: pack_calibration_value(item) for key, item in value.items()}
    return value


def unpack_calibration_value(value: object) -> object:
    if isinstance(value, list):
        return [unpack_calibration_value(item) for item in value]
    if not isinstance(value, dict):
        return value
    kind = value.get("__rebar_calibration_type__")
    if kind is None:
        return {key: unpack_calibration_value(item) for key, item in value.items()}
    if kind in {"bytes", "bytearray", "memoryview"}:
        require(set(value) == {"__rebar_calibration_type__", "hex"}, "invalid calibration byte encoding")
        require(isinstance(value["hex"], str), "invalid calibration byte payload")
        try:
            payload = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise RuntimeError("invalid calibration byte payload") from error
        if kind == "bytes":
            return payload
        if kind == "bytearray":
            return bytearray(payload)
        return memoryview(payload)
    if kind == "tuple":
        require(set(value) == {"__rebar_calibration_type__", "items"}, "invalid calibration tuple encoding")
        require(isinstance(value["items"], list), "invalid calibration tuple payload")
        return tuple(unpack_calibration_value(item) for item in value["items"])
    raise RuntimeError(f"unknown calibration serialization marker: {kind!r}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def positive_int(value: str) -> int:
    try:
        result = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if result < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return result


def cardinality(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, (list, tuple)):
        return len(value)
    return 1


def density(value: object) -> str:
    count = cardinality(value)
    if count == 0:
        return "none"
    if count == 1:
        return "one"
    if count <= 8:
        return "few"
    return "many"


def input_length(case: dict) -> int:
    value = case.get("string")
    return len(value) if isinstance(value, (str, bytes, bytearray, memoryview)) else 0


def bounded(case: dict, expected: dict) -> bool:
    return input_length(case) <= MAX_SUBJECT and cardinality(expected["result"]) <= MAX_RESULTS


def selection_key(seed: int, identifier: str) -> tuple[bytes, str]:
    return hashlib.sha256(f"{seed}:{identifier}".encode("utf-8")).digest(), identifier


def selected_entries(
    pairs: list[tuple[int, dict, dict]], target: int, seed: int
) -> list[tuple[int, dict, dict, tuple[str, ...]]]:
    require(MIN_CASES <= target <= MAX_CASES, "practice pilot must contain 300–700 cases")
    eligible = [
        (position, case, expected)
        for position, case, expected in pairs
        if case.get("cohort") == PRACTICE and bounded(case, expected)
    ]
    require(bool(eligible), "no bounded frozen practice workloads are available")

    by_api: dict[str, list[tuple[int, dict, dict]]] = collections.defaultdict(list)
    by_category: dict[str, list[tuple[int, dict, dict]]] = collections.defaultdict(list)
    for entry in eligible:
        by_api[entry[1]["api"]].append(entry)
        by_category[entry[1]["category"]].append(entry)
    ordered = lambda entries: sorted(
        entries, key=lambda entry: selection_key(seed, entry[1]["id"])
    )
    require(len(by_api) == 12, "bounded practice cases must retain all 12 public operations")

    selected: dict[str, tuple[int, dict, dict]] = {}
    reasons: dict[str, set[str]] = collections.defaultdict(set)

    def add(entry: tuple[int, dict, dict], reason: str) -> None:
        position, case, expected = entry
        require(case["cohort"] == PRACTICE, "hidden workload entered the practice plan")
        require(bounded(case, expected), "unbounded workload entered the practice plan")
        selected[case["id"]] = (position, case, expected)
        reasons[case["id"]].add(reason)

    # Preserve every existing frozen workload category before choosing additional
    # variants. No historical case speed or hidden workload is used for selection.
    for category, entries in sorted(by_category.items()):
        add(ordered(entries)[0], "every-bounded-workload-category")

    coverage = (
        ("api-lifetime", lambda case, _want: (case["api"], case["lifecycle"])),
        ("input-kind", lambda case, _want: source_kind(case)),
        ("result-density", lambda _case, want: density(want["result"])),
        ("case-folding", lambda case, _want: "I" in case["flags"]),
        ("bounded-window", lambda case, _want: "pos" in case or "endpos" in case),
    )
    for reason, identify in coverage:
        required_values = {identify(case, want) for _number, case, want in eligible}
        represented = {
            identify(case, want)
            for _number, case, want in selected.values()
        }
        for missing in sorted(required_values - represented, key=str):
            choices = [
                entry
                for entry in eligible
                if identify(entry[1], entry[2]) == missing
            ]
            add(ordered(choices)[0], reason)

    counts = collections.Counter(case["api"] for _number, case, _want in selected.values())
    quotas = {
        api: max(MIN_CASES_PER_API, counts[api])
        for api in sorted(by_api)
    }
    require(
        sum(quotas.values()) <= target,
        "the requested practice size cannot retain every workload and balanced API",
    )
    api_order = sorted(by_api, key=lambda api: selection_key(seed, api))
    remainder = target - sum(quotas.values())
    for index in range(remainder):
        quotas[api_order[index % len(api_order)]] += 1

    category_counts = collections.Counter(
        case["category"] for _number, case, _want in selected.values()
    )
    stratum_counts = collections.Counter(
        (case["api"], case["lifecycle"], source_kind(case), density(want["result"]))
        for _number, case, want in selected.values()
    )
    for api in api_order:
        pool = ordered(by_api[api])
        while counts[api] < quotas[api]:
            remaining = [entry for entry in pool if entry[1]["id"] not in selected]
            require(bool(remaining), f"insufficient bounded practice examples for {api}")
            entry = min(
                remaining,
                key=lambda item: (
                    category_counts[item[1]["category"]],
                    stratum_counts[
                        (
                            item[1]["api"],
                            item[1]["lifecycle"],
                            source_kind(item[1]),
                            density(item[2]["result"]),
                        )
                    ],
                    selection_key(seed, item[1]["id"]),
                ),
            )
            add(entry, "seeded-balanced-api-variant")
            case = entry[1]
            counts[api] += 1
            category_counts[case["category"]] += 1
            stratum_counts[
                (case["api"], case["lifecycle"], source_kind(case), density(entry[2]["result"]))
            ] += 1

    require(len(selected) == target, "balanced practice case denominator changed")
    require(counts == collections.Counter(quotas), "balanced public-API quotas changed")
    require(
        {case["category"] for _position, case, _want in selected.values()}
        == set(by_category),
        "a bounded frozen workload category was omitted",
    )
    result = [
        (*entry, tuple(sorted(reasons[identifier])))
        for identifier, entry in selected.items()
    ]
    result.sort(key=lambda item: item[0])
    return result


def calibration_base_source() -> tuple[types.SimpleNamespace, list[tuple[int, dict]]]:
    """Execute only the original calibration declarations, never held-out cases."""
    path = ROOT / "performance/v3/suite.py"
    prefix: list[bytes] = []
    selected: list[tuple[int, bytes]] = []
    in_cases = False
    position = 0
    with path.open("rb") as source:
        for raw in source:
            if not in_cases:
                if raw.strip() == b"CASES = [":
                    in_cases = True
                else:
                    prefix.append(raw)
                continue
            if raw.strip() == b"]":
                break
            if not raw.strip():
                continue
            if raw.startswith(b'    C("cal.'):
                selected.append((position, raw))
                position += 1
                continue
            if raw.startswith(b'    C("hold.'):
                # The held-out declaration remains opaque bytes. In particular,
                # it is never decoded, compiled, evaluated, or made into a case.
                position += 1
                continue
            raise RuntimeError("the frozen v3 calibration declaration shape changed")
    require(in_cases, "the frozen v3 calibration declaration is missing")
    body = b"".join(prefix) + b"CASES = [\n" + b"".join(raw for _, raw in selected) + b"]\n"
    namespace: dict[str, object] = {"__name__": "rebar_v3_calibration_only"}
    exec(compile(body, str(path), "exec"), namespace)
    module = types.SimpleNamespace(**namespace)
    require(module.CASES_PER_COHORT == 72, "the frozen v3 calibration denominator changed")
    require(len(selected) == module.CASES_PER_COHORT, "a frozen v3 calibration case was omitted")
    require(position == 2 * module.CASES_PER_COHORT, "the frozen v3 declaration layout changed")
    pairs = [
        (offset, case)
        for (offset, _raw), case in zip(selected, module.CASES, strict=True)
    ]
    require(
        all(case.get("cohort") == PRACTICE for _offset, case in pairs),
        "a non-calibration base case was executed",
    )
    return module, pairs


def calibration_generated_source(
    version: int, parent: types.SimpleNamespace
) -> types.SimpleNamespace:
    """Load additive generators without importing or invoking parent cases."""
    path = ROOT / f"performance/v{version}/suite.py"
    source = path.read_bytes()
    imports = [line for line in source.splitlines(keepends=True) if line.startswith(b"from performance.")]
    expected = f"from performance.v{version - 1}.suite import ".encode("ascii")
    require(
        len(imports) == 1 and imports[0].startswith(expected),
        f"the frozen v{version} parent import changed",
    )
    safe_source = b"".join(
        line
        for line in source.splitlines(keepends=True)
        if not line.startswith(b"from performance.")
    )
    namespace: dict[str, object] = {
        "__name__": f"rebar_v{version}_calibration_only",
        "parent_cases": forbidden_full_cohort,
        "MODULES": parent.MODULES,
    }
    exec(compile(safe_source, str(path), "exec"), namespace)
    module = types.SimpleNamespace(**namespace)
    require(callable(module.generated_case), f"frozen v{version} has no calibration generator")
    require(module.SEEDS.get(PRACTICE) is not None, f"frozen v{version} has no practice seed")
    return module


def append_generated_calibration_cases(
    suite: object,
    pairs: list[tuple[int, dict]],
    start: int,
    label: str,
) -> int:
    produced = 0
    for family in suite.FAMILIES:
        for variant in range(suite.VARIANTS):
            case = suite.generated_case(PRACTICE, family, variant)
            require(
                isinstance(case, dict) and case.get("cohort") == PRACTICE,
                f"{label} generated a non-calibration case",
            )
            pairs.append((start + produced, case))
            produced += 1
    require(
        produced == len(suite.FAMILIES) * suite.VARIANTS,
        f"{label} changed its practice-family denominator",
    )
    return produced


def calibration_source_cases() -> tuple[types.SimpleNamespace, list[tuple[int, dict]], dict]:
    """Reproduce exact global positions without constructing a hidden workload."""
    suite, pairs = calibration_base_source()
    previous_total = 2 * suite.CASES_PER_COHORT
    source_hashes = {
        "performance/v3/suite.py": file_sha256(ROOT / "performance/v3/suite.py")
    }
    for version in range(4, 8):
        suite = calibration_generated_source(version, suite)
        if hasattr(suite, "PARENT_CASES_PER_COHORT"):
            require(
                suite.PARENT_CASES_PER_COHORT * 2 == previous_total,
                f"frozen v{version} changed its parent case denominator",
            )
        produced = append_generated_calibration_cases(
            suite, pairs, previous_total, f"frozen v{version}"
        )
        require(
            suite.CASES_PER_COHORT * 2 == previous_total + 2 * produced,
            f"frozen v{version} changed its additive case layout",
        )
        previous_total = 2 * suite.CASES_PER_COHORT
        source_hashes[f"performance/v{version}/suite.py"] = file_sha256(
            ROOT / f"performance/v{version}/suite.py"
        )
    require(suite.CASES_PER_COHORT == 10_312, "the frozen v7 calibration denominator changed")
    require(len(pairs) == suite.CASES_PER_COHORT, "the complete calibration fixture was not generated")
    identifiers = [case["id"] for _position, case in pairs]
    require(len(identifiers) == len(set(identifiers)), "duplicate frozen calibration case")
    return suite, pairs, source_hashes


def decode_calibration_expected(
    lines: object,
    cases: dict[str, dict],
    *,
    decoder: object = json.loads,
    source_digest: object | None = None,
) -> dict[str, dict]:
    """Identify the cohort in opaque bytes before any JSON deserialization."""
    records: dict[str, dict] = {}
    for raw in lines:
        require(isinstance(raw, bytes), "a frozen expected record is not opaque bytes")
        if source_digest is not None:
            source_digest.update(raw)
        header, separator, _rest = raw.partition(b',"id":')
        if not separator or not header.endswith(b'"cohort":"calibration"'):
            continue
        try:
            record = decoder(raw)
        except (UnicodeError, json.JSONDecodeError, ValueError) as error:
            raise RuntimeError("invalid frozen calibration expected record") from error
        require(isinstance(record, dict), "frozen calibration expected record is not an object")
        require(record.get("cohort") == PRACTICE, "a hidden record reached JSON deserialization")
        identifier = record.get("id")
        require(isinstance(identifier, str) and identifier in cases, "unfrozen calibration result")
        require(identifier not in records, "duplicate frozen calibration result")
        require(record.get("category") == cases[identifier]["category"], "changed calibration category")
        require(digest(record.get("result")) == record.get("result_sha256"), "corrupted calibration result")
        records[identifier] = record
    require(set(records) == set(cases), "a frozen calibration result is missing")
    return records


def historical_calibration_archive(path: Path) -> tuple[dict, dict[str, dict]]:
    """Load an archive that already contains practice records exclusively."""
    require(
        path.resolve() == DEFAULT_PRIORITIES_ARCHIVE.resolve(),
        "only the frozen calibration-only priorities archive may seed practice history",
    )
    with gzip.open(path, "rb") as source:
        payload = source.read()
    try:
        document = json.loads(payload)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError("invalid practice-only optimization archive") from error
    require(isinstance(document, dict), "practice-only optimization archive is not an object")
    require(document.get("schema") == PRIORITIES_SCHEMA, "incorrect practice-only archive schema")
    require(document.get("cohort") == PRACTICE, "optimization archive is not practice-only")
    rows = document.get("practice_cases")
    rankings = document.get("practice_rankings")
    require(isinstance(rows, list), "practice-only optimization rows are missing")
    require(isinstance(rankings, list), "practice-only optimization rankings are missing")
    indexed: dict[str, dict] = {}
    for row in rows:
        require(isinstance(row, dict), "practice-only optimization row is not an object")
        require(row.get("cohort") == PRACTICE, "a hidden optimization result entered the practice archive")
        identifier = row.get("case")
        require(isinstance(identifier, str), "practice-only optimization case has no identifier")
        require(identifier not in indexed, "duplicate practice-only optimization case")
        indexed[identifier] = row
    require(len(indexed) == document.get("cases") == 10_312, "practice-only optimization denominator changed")
    require(
        all(isinstance(row, dict) and row.get("cohort") == PRACTICE for row in rankings),
        "a hidden candidate ranking entered the practice archive",
    )
    return document, indexed


def freeze_calibration_fixture(args: argparse.Namespace) -> None:
    """One-time byte-filtered extraction; ordinary runs never open mixed data."""
    destination = Path(args.fixture)
    manifest_path = Path(args.manifest)
    require(not destination.exists(), f"refusing to overwrite sealed calibration fixture: {destination}")
    require(not manifest_path.exists(), f"refusing to overwrite sealed calibration manifest: {manifest_path}")
    suite, pairs, source_hashes = calibration_source_cases()
    with MANIFEST_PATH.open("rb") as source:
        parent_manifest = json.load(source)
    require(parent_manifest.get("schema") == "rebar-performance-v7", "incorrect frozen v7 manifest")
    require(parent_manifest.get("python") == "3.14.6", "frozen v7 Python baseline changed")
    require(parent_manifest.get("cases") == 2 * suite.CASES_PER_COHORT, "frozen v7 case count changed")
    require(parent_manifest.get("cohorts", {}).get(PRACTICE) == suite.CASES_PER_COHORT, "frozen v7 practice weight changed")
    require(source_hashes["performance/v7/suite.py"] == parent_manifest.get("suite_sha256"), "frozen v7 suite source changed")
    require(file_sha256(ROOT / "tools/perf_v7.py") == parent_manifest.get("runner_sha256"), "frozen v7 runner source changed")
    require(list(suite.MODULES) == parent_manifest.get("modules"), "frozen independent engine families changed")

    history, historical_rows = historical_calibration_archive(Path(args.history))
    require(history.get("expected_sha256") == parent_manifest.get("expected_sha256"), "practice history uses a different frozen fixture")
    cases = {case["id"]: case for _position, case in pairs}
    require(set(historical_rows) == set(cases), "practice history changed the sealed workload IDs")

    source_digest = hashlib.sha256()
    with EXPECTED_PATH.open("rb") as source:
        expected = decode_calibration_expected(source, cases, source_digest=source_digest)
    require(source_digest.hexdigest() == parent_manifest.get("expected_sha256"), "frozen v7 expected bytes changed")
    for identifier, historical in historical_rows.items():
        require(
            historical.get("expected_result_sha256") == expected[identifier]["result_sha256"],
            f"practice history changed a frozen calibration result: {identifier}",
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    uncompressed = hashlib.sha256()
    with destination.open("xb") as target:
        with gzip.GzipFile(filename="", fileobj=target, mode="wb", compresslevel=9, mtime=0) as archive:
            for position, case in pairs:
                identifier = case["id"]
                document = {
                    "schema": FIXTURE_SCHEMA,
                    "cohort": PRACTICE,
                    "position": position,
                    "case": pack_calibration_value(case),
                    "expected": expected[identifier],
                    "historical": historical_rows[identifier],
                }
                payload = (
                    json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
                    + "\n"
                ).encode("ascii")
                uncompressed.update(payload)
                archive.write(payload)

    fixture_manifest = {
        "schema": FIXTURE_MANIFEST_SCHEMA,
        "python": parent_manifest["python"],
        "cohort": PRACTICE,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "performance": "NOT MEASURED",
        "cases": len(pairs),
        "candidate_case_results": history["candidate_case_results"],
        "expected_sha256": parent_manifest["expected_sha256"],
        "source_v7_manifest_sha256": file_sha256(MANIFEST_PATH),
        "source_v7_suite_sha256": source_hashes["performance/v7/suite.py"],
        "source_v7_runner_sha256": parent_manifest["runner_sha256"],
        "source_expected_sha256": source_digest.hexdigest(),
        "source_suite_sha256": source_hashes,
        "source_practice_archive_sha256": file_sha256(Path(args.history)),
        "historical_summary_sha256": history["summary_sha256"],
        "historical_raw_sha256": history["raw_sha256"],
        "historical_practice_rankings": history["practice_rankings"],
        "fixture": str(destination.resolve().relative_to(ROOT.resolve())),
        "fixture_sha256": file_sha256(destination),
        "uncompressed_fixture_sha256": uncompressed.hexdigest(),
        "suite": {
            "MODULES": list(suite.MODULES),
            "CASES_PER_COHORT": suite.CASES_PER_COHORT,
            "SEEDS": {PRACTICE: suite.SEEDS[PRACTICE]},
            "ORDER_SEED": suite.ORDER_SEED,
            "BOOTSTRAP_SEED": suite.BOOTSTRAP_SEED,
            "TRIALS": suite.TRIALS,
            "WARMUPS": suite.WARMUPS,
            "BOOTSTRAPS": suite.BOOTSTRAPS,
        },
        "failed": 0,
    }
    manifest_sha256 = save_json(manifest_path, fixture_manifest)
    loaded_suite, loaded_pairs, loaded_parent, loaded_history, loaded_manifest = load_calibration_fixture(
        destination, manifest_path
    )
    require(loaded_suite.CASES_PER_COHORT == suite.CASES_PER_COHORT, "sealed calibration protocol changed")
    require(len(loaded_pairs) == len(pairs), "sealed calibration fixture lost a workload")
    require(loaded_parent["expected_sha256"] == parent_manifest["expected_sha256"], "sealed parent fixture hash changed")
    require(set(loaded_history) == set(historical_rows), "sealed practice history changed")
    require(loaded_manifest["fixture_sha256"] == fixture_manifest["fixture_sha256"], "sealed fixture verification changed")
    print(json.dumps({
        "schema": FIXTURE_MANIFEST_SCHEMA,
        "cohort": PRACTICE,
        "cases": len(loaded_pairs),
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "timing_performed": False,
        "fixture_sha256": fixture_manifest["fixture_sha256"],
        "uncompressed_fixture_sha256": fixture_manifest["uncompressed_fixture_sha256"],
        "manifest_sha256": manifest_sha256,
        "failed": 0,
    }, sort_keys=True))


def load_calibration_fixture(
    fixture: Path = DEFAULT_FIXTURE,
    manifest_path: Path = DEFAULT_FIXTURE_MANIFEST,
) -> tuple[types.SimpleNamespace, list[tuple[int, dict, dict]], dict, dict[str, dict], dict]:
    """Load exclusively the pre-frozen, single-cohort calibration archive."""
    require(fixture.is_file(), "the sealed calibration-only fixture has not been frozen")
    require(manifest_path.is_file(), "the sealed calibration-only fixture manifest is missing")
    with manifest_path.open("rb") as source:
        manifest = json.load(source)
    require(isinstance(manifest, dict), "invalid sealed calibration fixture manifest")
    require(manifest.get("schema") == FIXTURE_MANIFEST_SCHEMA, "incorrect sealed calibration fixture schema")
    require(manifest.get("python") == "3.14.6", "sealed calibration Python baseline changed")
    require(manifest.get("cohort") == PRACTICE, "sealed fixture is not calibration-only")
    require(manifest.get("holdout_accessed") is False, "sealed fixture admits holdout access")
    require(manifest.get("held_out_cases_generated") == 0, "sealed fixture generated hidden workloads")
    require(manifest.get("held_out_records_deserialized") == 0, "sealed fixture decoded hidden results")
    require(manifest.get("performance") == "NOT MEASURED", "performance leaked into the calibration freeze")
    require(manifest.get("failed") == 0, "sealed calibration fixture contains failures")
    require(manifest.get("fixture") == str(fixture.resolve().relative_to(ROOT.resolve())), "sealed calibration fixture path changed")
    require(file_sha256(fixture) == manifest.get("fixture_sha256"), "sealed calibration fixture bytes changed")
    require(file_sha256(MANIFEST_PATH) == manifest.get("source_v7_manifest_sha256"), "frozen v7 parent manifest changed")
    with MANIFEST_PATH.open("rb") as source:
        parent = json.load(source)
    require(parent.get("schema") == "rebar-performance-v7", "incorrect frozen v7 parent manifest")
    require(parent.get("expected_sha256") == manifest.get("source_expected_sha256"), "frozen v7 parent expected hash changed")
    require(parent.get("suite_sha256") == manifest.get("source_v7_suite_sha256"), "frozen v7 parent suite hash changed")
    require(parent.get("runner_sha256") == manifest.get("source_v7_runner_sha256"), "frozen v7 parent runner hash changed")
    protocol = manifest.get("suite")
    require(isinstance(protocol, dict), "sealed calibration protocol is missing")
    required_protocol = {
        "MODULES", "CASES_PER_COHORT", "SEEDS", "ORDER_SEED", "BOOTSTRAP_SEED",
        "TRIALS", "WARMUPS", "BOOTSTRAPS",
    }
    require(set(protocol) == required_protocol, "sealed calibration protocol fields changed")
    require(protocol["SEEDS"].keys() == {PRACTICE}, "sealed calibration protocol exposes a hidden seed")
    require(protocol["MODULES"] == parent.get("modules"), "sealed independent candidate families changed")
    require(protocol["CASES_PER_COHORT"] == parent.get("cohorts", {}).get(PRACTICE), "sealed practice weight changed")
    suite = types.SimpleNamespace(**protocol)

    rows: list[tuple[int, dict, dict]] = []
    history: dict[str, dict] = {}
    uncompressed = hashlib.sha256()
    positions: set[int] = set()
    with gzip.open(fixture, "rb") as source:
        for raw in source:
            uncompressed.update(raw)
            try:
                document = json.loads(raw)
            except (UnicodeError, json.JSONDecodeError) as error:
                raise RuntimeError("invalid sealed calibration fixture record") from error
            require(isinstance(document, dict), "sealed calibration record is not an object")
            require(document.get("schema") == FIXTURE_SCHEMA, "incorrect sealed calibration record schema")
            require(document.get("cohort") == PRACTICE, "hidden record entered the sealed calibration archive")
            position = document.get("position")
            require(isinstance(position, int) and not isinstance(position, bool) and position >= 0, "invalid calibration case position")
            require(position not in positions, "duplicate frozen calibration position")
            positions.add(position)
            case = unpack_calibration_value(document.get("case"))
            expected = document.get("expected")
            previous = document.get("historical")
            require(isinstance(case, dict) and case.get("cohort") == PRACTICE, "non-calibration case in the sealed fixture")
            require(isinstance(expected, dict) and expected.get("cohort") == PRACTICE, "non-calibration answer in the sealed fixture")
            require(isinstance(previous, dict) and previous.get("cohort") == PRACTICE, "non-calibration ranking in the sealed fixture")
            identifier = case.get("id")
            require(isinstance(identifier, str) and identifier not in history, "duplicate sealed calibration case")
            require(expected.get("id") == identifier, "sealed case and answer disagree")
            require(previous.get("case") == identifier, "sealed case and practice history disagree")
            require(expected.get("category") == case.get("category") == previous.get("category"), "sealed calibration category changed")
            require(digest(expected.get("result")) == expected.get("result_sha256"), "sealed calibration answer is corrupted")
            require(previous.get("expected_result_sha256") == expected.get("result_sha256"), "sealed practice ranking answer changed")
            rows.append((position, case, expected))
            history[identifier] = previous
    require(uncompressed.hexdigest() == manifest.get("uncompressed_fixture_sha256"), "sealed calibration record content changed")
    require(len(rows) == len(history) == suite.CASES_PER_COHORT == manifest.get("cases"), "sealed practice denominator changed")
    require(rows == sorted(rows, key=lambda item: item[0]), "sealed calibration case ordering changed")
    rankings = manifest.get("historical_practice_rankings")
    require(isinstance(rankings, list), "sealed practice rankings are missing")
    require(all(isinstance(row, dict) and row.get("cohort") == PRACTICE for row in rankings), "sealed rankings expose a hidden cohort")
    return suite, rows, parent, history, manifest


def make_plan(target: int = DEFAULT_CASES) -> tuple[object, list[tuple[int, dict, dict, tuple[str, ...]]], dict, dict]:
    suite, pairs, manifest, _history, _fixture_manifest = load_calibration_fixture()
    selection_seed = suite.SEEDS[PRACTICE]
    entries = selected_entries(pairs, target, selection_seed)
    eligible = [
        (position, case, want)
        for position, case, want in pairs
        if case["cohort"] == PRACTICE and bounded(case, want)
    ]
    api_counts = collections.Counter(case["api"] for _position, case, _want, _reasons in entries)
    lifetimes = collections.Counter(case["lifecycle"] for _position, case, _want, _reasons in entries)
    input_counts = collections.Counter(
        source_kind(case) for _position, case, _want, _reasons in entries
    )
    densities = collections.Counter(
        density(want["result"]) for _position, _case, want, _reasons in entries
    )
    api_lifetimes = collections.Counter(
        (case["api"], case["lifecycle"])
        for _position, case, _want, _reasons in entries
    )
    required_apis = {case["api"] for _position, case, _want in eligible}
    required_lifetimes = {case["lifecycle"] for _position, case, _want in eligible}
    required_inputs = {source_kind(case) for _position, case, _want in eligible}
    required_densities = {density(want["result"]) for _position, _case, want in eligible}
    required_api_lifetimes = {
        (case["api"], case["lifecycle"])
        for _position, case, _want in eligible
    }
    require(set(api_counts) == required_apis, "a public regular-expression operation is missing")
    require(set(lifetimes) == required_lifetimes, "a pattern lifetime is missing")
    require(set(input_counts) == required_inputs, "a Python text or buffer representation is missing")
    require(set(densities) == required_densities, "a result-density category is missing")
    require(set(api_lifetimes) == required_api_lifetimes, "an API/lifetime pair is missing")
    require(
        {case["cohort"] for _position, case, _want, _reasons in entries} == {PRACTICE},
        "a held-back workload entered a calibration-only experiment",
    )
    categories = collections.Counter(
        case["category"] for _position, case, _want, _reasons in entries
    )
    plan = {
        "schema": PLAN_SCHEMA,
        "measurement": "balanced practice diagnostic; never a holdout ranking or final speed claim",
        "python": manifest["python"],
        "cohort": PRACTICE,
        "holdout_accessed": False,
        "historical_performance_read": False,
        "timing_performed": False,
        "expected_sha256": manifest["expected_sha256"],
        "selection_seed": selection_seed,
        "order_seed": suite.ORDER_SEED,
        "bootstrap_seed": suite.BOOTSTRAP_SEED,
        "frozen_trials": suite.TRIALS,
        "frozen_warmups": suite.WARMUPS,
        "frozen_bootstrap_samples": suite.BOOTSTRAPS,
        "cases": len(entries),
        "eligible_practice_cases": len(eligible),
        "all_bounded_workload_categories": len(categories),
        "public_operations": dict(sorted(api_counts.items())),
        "lifetimes": dict(sorted(lifetimes.items())),
        "inputs": dict(sorted(input_counts.items())),
        "result_densities": dict(sorted(densities.items())),
        "api_lifetimes": {
            f"{api} / {lifecycle}": count
            for (api, lifecycle), count in sorted(api_lifetimes.items())
        },
        "maximum_subject_length": max(input_length(case) for _index, case, _want, _reason in entries),
        "maximum_result_count": max(
            cardinality(want["result"]) for _index, _case, want, _reason in entries
        ),
        "maximum_subject_limit": MAX_SUBJECT,
        "maximum_result_limit": MAX_RESULTS,
        "maximum_operations_per_trial": MAX_OPERATIONS,
        "default_trials": DEFAULT_TRIALS,
        "default_bootstrap_samples": DEFAULT_BOOTSTRAPS,
        "strict_regression_speedup_threshold": REGRESSION_SPEEDUP_THRESHOLD,
        "execution_safety": (
            "The measure command requires an explicit --exclusive-slot. "
            "Each shuffled paired timing receives exact frozen pre-timing, "
            "memory-sample, and post-timing correctness gates."
        ),
        "categories": dict(sorted(categories.items())),
        "selected_cases": [
            {
                "case": case["id"],
                "cohort": case["cohort"],
                "category": case["category"],
                "api": case["api"],
                "lifecycle": case["lifecycle"],
                "input": source_kind(case),
                "subject_length": input_length(case),
                "result_count": cardinality(want["result"]),
                "result_density": density(want["result"]),
                "frozen_operations": case["ops"],
                "expected_result_sha256": want["result_sha256"],
                "selection_reasons": list(reasons),
            }
            for _position, case, want, reasons in entries
        ],
        "failed": 0,
    }
    return suite, entries, manifest, plan


def percentile(values: list[float], quantile: float) -> float:
    require(bool(values), "cannot calculate an empty confidence interval")
    require(0 <= quantile <= 1, "invalid confidence quantile")
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    left = math.floor(position)
    right = math.ceil(position)
    fraction = position - left
    return ordered[left] * (1.0 - fraction) + ordered[right] * fraction


def confidence_interval(logs: list[float], seed: int, samples: int) -> tuple[float, float]:
    require(bool(logs), "cannot bootstrap an empty paired trial")
    require(samples > 0, "bootstrap samples must be positive")
    require(all(math.isfinite(value) for value in logs), "paired log speeds are not finite")
    generator = random.Random(seed)
    count = len(logs)
    draws = [
        math.exp(
            statistics.fmean(logs[generator.randrange(count)] for _ in range(count))
        )
        for _ in range(samples)
    ]
    return percentile(draws, 0.025), percentile(draws, 0.975)


def trial_order(modules: tuple[str, ...], case_id: str, trial: int, seed: int) -> tuple[str, ...]:
    order = list(modules)
    random.Random(seed + trial * 1009 + sum(map(ord, case_id))).shuffle(order)
    return tuple(order)


def selected_modules(suite: object, names: list[str] | None) -> tuple[str, ...]:
    modules = tuple(names) if names else (BASELINE, RUST, "candidates.zig_candidate")
    require(bool(modules) and modules[0] == BASELINE, "Python re must be the paired first baseline")
    require(RUST in modules, "the from-scratch Rust candidate must be measured")
    require(len(set(modules)) == len(modules), "duplicate paired candidate engine")
    require(set(modules) <= set(suite.MODULES), "unknown frozen candidate in paired calibration")
    return modules


def file_sha256(path: Path) -> str:
    digest_value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest_value.update(chunk)
    return digest_value.hexdigest()


def module_fingerprints(modules: dict[str, object]) -> dict[str, str]:
    paths: dict[str, Path] = {}
    native_paths: set[Path] = set()
    for name, module in modules.items():
        source = getattr(module, "__file__", None)
        require(isinstance(source, str), f"paired module has no source fingerprint: {name}")
        paths[f"{name}:module"] = Path(source).resolve()
        if name == RUST:
            paths[f"{name}:native-engine"] = Path(source).with_name("_rust_engine.so").resolve()
            bridge = importlib.import_module("candidates._rust_bridge")
            paths[f"{name}:native-bridge"] = Path(bridge.__file__).resolve()
            paths[f"{name}:native-source"] = (ROOT / "candidates/rust/src/lib.rs").resolve()
            paths[f"{name}:bridge-source"] = (ROOT / "candidates/rust/py_bridge.c").resolve()
            native_paths.update((paths[f"{name}:native-engine"], paths[f"{name}:native-bridge"]))
        elif name == "candidates.zig_candidate":
            engine = Path(source).with_name("_zig_probe.so")
            if engine.is_file():
                paths[f"{name}:native-engine"] = engine.resolve()
                native_paths.add(paths[f"{name}:native-engine"])
            bridge = importlib.import_module("candidates._zig_bridge")
            paths[f"{name}:native-bridge"] = Path(bridge.__file__).resolve()
            native_paths.add(paths[f"{name}:native-bridge"])
        elif name == "candidates.vm_candidate":
            native = importlib.import_module("candidates._vm_native")
            paths[f"{name}:native-engine"] = Path(native.__file__).resolve()
            native_paths.add(paths[f"{name}:native-engine"])
    for label, path in paths.items():
        require(path.is_file(), f"paired module artifact is missing: {label}")
    if native_paths:
        maps_path = Path("/proc/self/maps")
        require(maps_path.is_file(), "loaded native candidate mappings cannot be verified")
        mapped: set[Path] = set()
        with maps_path.open("r", encoding="utf-8", errors="surrogateescape") as maps:
            for line in maps:
                fields = line.split(maxsplit=5)
                if len(fields) != 6:
                    continue
                location = fields[5].strip()
                if not location.startswith("/") or location.endswith(" (deleted)"):
                    continue
                mapped.add(Path(location).resolve())
        for path in native_paths:
            require(path in mapped, f"candidate native artifact is not actually loaded: {path}")
    return {name: file_sha256(path) for name, path in sorted(paths.items())}


def required_edge_artifact_roles(candidate: str) -> frozenset[str]:
    if candidate == RUST:
        return frozenset({
            "public-python", "native-bridge", "native-engine", "native-source", "bridge-source"
        })
    if candidate == "candidates.zig_candidate":
        return frozenset({"public-python", "native-bridge", "native-engine"})
    if candidate == "candidates.vm_candidate":
        return frozenset({"public-python", "native-bridge"})
    if candidate == "candidates.ast_candidate":
        return frozenset({"public-python"})
    raise RuntimeError(f"unknown frozen candidate artifact roles: {candidate}")


def verify_reported_artifacts(candidate: str, artifacts: object) -> dict[str, dict[str, str]]:
    require(isinstance(artifacts, list) and bool(artifacts), "edge oracle has no candidate fingerprints")
    required = required_edge_artifact_roles(candidate)
    resolved: dict[str, dict[str, str]] = {}
    candidates_root = (ROOT / "candidates").resolve()
    expected_public = (candidates_root / f"{candidate.rsplit('.', 1)[-1]}.py").resolve()
    fixed = {
        "public-python": expected_public,
        "native-source": (candidates_root / "rust/src/lib.rs").resolve(),
        "bridge-source": (candidates_root / "rust/py_bridge.c").resolve(),
    }
    if candidate == RUST:
        fixed["native-engine"] = (candidates_root / "_rust_engine.so").resolve()
    elif candidate == "candidates.zig_candidate":
        fixed["native-engine"] = (candidates_root / "_zig_probe.so").resolve()
    for artifact in artifacts:
        require(isinstance(artifact, dict), "invalid edge-oracle candidate fingerprint")
        require(set(artifact) == {"role", "path", "sha256"}, "edge-oracle artifact fields changed")
        role = artifact.get("role")
        require(isinstance(role, str) and role in required, f"unexpected edge-oracle artifact role: {role!r}")
        require(role not in resolved, f"duplicate edge-oracle artifact role: {role}")
        location = artifact.get("path")
        require(isinstance(location, str), "edge-oracle candidate fingerprint has no path")
        item = Path(location)
        item = item.resolve() if item.is_absolute() else (ROOT / item).resolve()
        require(item.is_relative_to(candidates_root), f"edge-oracle candidate artifact escaped production: {location}")
        if role in fixed:
            require(item == fixed[role], f"edge-oracle candidate artifact has the wrong role path: {role}")
        if role == "native-bridge":
            prefix = {
                RUST: "_rust_bridge.",
                "candidates.zig_candidate": "_zig_bridge.",
                "candidates.vm_candidate": "_vm_native.",
            }[candidate]
            require(item.parent == candidates_root and item.name.startswith(prefix), "edge-oracle native bridge does not belong to the candidate")
        require(item.is_file(), f"edge-oracle candidate artifact disappeared: {location}")
        expected = artifact.get("sha256")
        require(
            isinstance(expected, str)
            and len(expected) == 64
            and all(char in "0123456789abcdef" for char in expected),
            f"invalid edge-oracle candidate artifact digest: {role}",
        )
        require(file_sha256(item) == expected, f"candidate changed after independent edge verification: {candidate} {role}")
        resolved[role] = {"path": str(item.relative_to(ROOT.resolve())), "sha256": expected}
    require(set(resolved) == required, f"missing required edge-oracle candidate artifact roles: {candidate}")
    return {role: resolved[role] for role in sorted(resolved)}


def match_reported_fingerprints(reports: list[dict], fingerprints: dict[str, str]) -> None:
    for report in reports:
        candidate = report["module"]
        artifacts = report.get("candidate_artifacts")
        require(isinstance(artifacts, dict), "verified candidate artifact roles are missing")
        require(set(artifacts) == required_edge_artifact_roles(candidate), "verified candidate artifact role set changed")
        labels = {"public-python": f"{candidate}:module"}
        if candidate in {RUST, "candidates.zig_candidate"}:
            labels.update({
                "native-bridge": f"{candidate}:native-bridge",
                "native-engine": f"{candidate}:native-engine",
            })
        if candidate == RUST:
            labels.update({
                "native-source": f"{candidate}:native-source",
                "bridge-source": f"{candidate}:bridge-source",
            })
        if candidate == "candidates.vm_candidate":
            labels["native-bridge"] = f"{candidate}:native-engine"
        require(set(labels) == set(artifacts), "native candidate artifact/fingerprint role mapping changed")
        for role, label in labels.items():
            require(label in fingerprints, f"measured candidate artifact is missing: {label}")
            require(
                fingerprints[label] == artifacts[role].get("sha256"),
                f"measured candidate is not the correctness-qualified artifact: {candidate} {role}",
            )


def edge_document(path: Path) -> tuple[dict, bytes]:
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as stream:
            payload = stream.read()
    else:
        payload = path.read_bytes()
    try:
        report = json.loads(payload)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"invalid independent edge oracle: {path}") from error
    require(isinstance(report, dict), f"invalid independent edge-oracle object: {path}")
    require(report.get("schema") == EDGE_SCHEMA, f"incorrect edge-oracle schema: {path}")
    return report, payload


def verify_edge_source_hash(report: dict, expected: str, label: str) -> None:
    require(
        isinstance(expected, str)
        and len(expected) == 64
        and all(char in "0123456789abcdef" for char in expected),
        "invalid committed independent edge-oracle source digest",
    )
    require(
        report.get("script_sha256") == expected,
        f"edge oracle does not match the current committed independent source: {label}",
    )


def verified_edge_oracles(paths: list[Path], modules: tuple[str, ...]) -> list[dict]:
    """Fail closed unless every measured candidate passed the frozen edge oracle."""
    script = ROOT / "tools/rust_v7_edge_oracle.py"
    baseline_path = ROOT / "candidates/evidence/rust-v7-edge-oracle-stdlib-baseline.json.gz"
    require(script.is_file(), "the independent all-engine edge oracle has not been frozen")
    require(baseline_path.is_file(), "the independent CPython edge self-oracle has not been frozen")
    tracked = subprocess.run(
        [
            "git",
            "ls-files",
            "--error-unmatch",
            "tools/rust_v7_edge_oracle.py",
            "candidates/evidence/rust-v7-edge-oracle-stdlib-baseline.json.gz",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    require(
        tracked.returncode == 0,
        "the independent all-engine edge oracle must be committed before live timing",
    )
    clean = subprocess.run(
        [
            "git",
            "status",
            "--porcelain",
            "--",
            "tools/rust_v7_edge_oracle.py",
            "candidates/evidence/rust-v7-edge-oracle-stdlib-baseline.json.gz",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    require(
        clean.returncode == 0 and not clean.stdout.strip(),
        "the committed independent edge oracle has uncommitted changes",
    )
    expected_source = file_sha256(script)
    baseline, baseline_payload = edge_document(baseline_path)
    require(baseline.get("module") == BASELINE, "frozen edge reference is not Python re")
    require(baseline.get("python") == "3.14.6", "frozen edge reference changed pinned Python")
    require(baseline.get("unicode") == "16.0.0", "frozen edge reference changed Unicode")
    require(baseline.get("locale") == "C", "frozen edge reference changed character locale")
    require(baseline.get("failed") == 0, "frozen CPython edge self-oracle failed")
    verify_edge_source_hash(baseline, expected_source, BASELINE)
    require(
        baseline.get("expected_sha256") == baseline.get("actual_sha256"),
        "frozen CPython edge self-oracle is not deterministic",
    )
    require(
        isinstance(baseline.get("correctness_checks"), int)
        and baseline["correctness_checks"] >= 223_198,
        "frozen CPython edge self-oracle dropped the comprehensive baseline",
    )
    categories = baseline.get("categories")
    require(
        isinstance(categories, dict)
        and len(categories) >= 49
        and sum(categories.values()) == baseline["correctness_checks"],
        "frozen CPython edge self-oracle dropped a correctness category",
    )
    require(baseline.get("performance") == "NOT MEASURED", "performance leaked into the edge reference")
    require(baseline.get("holdout") == "NOT ACCESSED", "holdout leaked into the edge reference")
    baseline_digest = hashlib.sha256(baseline_payload).hexdigest()
    required_modules = set(modules) - {BASELINE}
    reports: dict[str, dict] = {}
    for path in paths:
        report, payload = edge_document(path)
        candidate = report.get("module")
        require(candidate in required_modules, f"unexpected edge-oracle candidate: {candidate}")
        require(candidate not in reports, f"duplicate edge-oracle candidate: {candidate}")
        for key in ("python", "unicode", "locale", "seed", "seeded_cases", "unicode_stride"):
            require(
                report.get(key) == baseline.get(key),
                f"edge oracle changed the frozen Python matrix {key}: {candidate}",
            )
        require(report.get("failed") == 0, f"edge oracle contains failures: {candidate}")
        require(
            report.get("correctness_checks") == baseline["correctness_checks"],
            f"edge oracle changed the complete CPython check denominator: {candidate}",
        )
        require(
            report.get("categories") == categories,
            f"edge oracle changed or dropped a frozen CPython category: {candidate}",
        )
        require(
            report.get("expected_sha256")
            == report.get("actual_sha256")
            == baseline["expected_sha256"],
            f"edge oracle does not match the exact frozen CPython answers: {candidate}",
        )
        verify_edge_source_hash(report, expected_source, candidate)
        require(report.get("performance") == "NOT MEASURED", "performance leaked into the edge oracle")
        require(report.get("holdout") == "NOT ACCESSED", "holdout leaked into the edge oracle")
        artifacts = verify_reported_artifacts(candidate, report.get("candidate_artifacts"))
        reports[candidate] = {
            "module": candidate,
            "path": str(path.resolve()),
            "report_sha256": hashlib.sha256(payload).hexdigest(),
            "stdlib_baseline_sha256": baseline_digest,
            "script_sha256": expected_source,
            "correctness_checks": report["correctness_checks"],
            "actual_sha256": report["actual_sha256"],
            "candidate_artifacts": artifacts,
        }
    require(
        set(reports) == required_modules,
        "every measured candidate must pass the committed independent edge oracle first",
    )
    return [reports[name] for name in modules if name != BASELINE]


def exact_snapshot(value: object, expected: dict, expected_digest: str, label: str) -> None:
    actual = snapshot(value)
    require(
        actual == expected["result"] and digest(actual) == expected_digest,
        f"paired practice {label} correctness gate failed",
    )


def per_case_seed(base_seed: int, case_id: str, candidate: str) -> int:
    encoded = hashlib.sha256(f"{base_seed}:{case_id}:{candidate}".encode("utf-8")).digest()
    return int.from_bytes(encoded[:8], "big")


def summarize_measurements(
    suite: object,
    entries: list[tuple[int, dict, dict, tuple[str, ...]]],
    names: tuple[str, ...],
    observed: dict[tuple[str, int, str], dict],
    trials: int,
    bootstraps: int,
) -> tuple[list[dict], list[dict]]:
    results = []
    for _position, case, want, _reasons in entries:
        baseline = [observed[case["id"], trial, BASELINE] for trial in range(trials)]
        for name in names[1:]:
            candidate = [observed[case["id"], trial, name] for trial in range(trials)]
            logs = [
                math.log(reference["ns_per_op"] / contender["ns_per_op"])
                for reference, contender in zip(baseline, candidate, strict=True)
            ]
            seed = per_case_seed(suite.BOOTSTRAP_SEED, case["id"], name)
            low, high = confidence_interval(logs, seed, bootstraps)
            speedup = math.exp(statistics.fmean(logs))
            results.append(
                {
                    "case": case["id"],
                    "cohort": PRACTICE,
                    "category": case["category"],
                    "api": case["api"],
                    "lifecycle": case["lifecycle"],
                    "input": source_kind(case),
                    "result_density": density(want["result"]),
                    "candidate": name,
                    "weight": case["weight"],
                    "speedup": speedup,
                    "ci95_low": low,
                    "ci95_high": high,
                    "baseline_ns": statistics.median(row["ns_per_op"] for row in baseline),
                    "candidate_ns": statistics.median(row["ns_per_op"] for row in candidate),
                    "peak_traced_ratio": (
                        statistics.median(row["peak_traced_bytes"] for row in candidate)
                        / max(1, statistics.median(row["peak_traced_bytes"] for row in baseline))
                    ),
                    "statistically_faster": low > 1.0,
                    "regression_gt_20pct": is_runtime_regression(speedup),
                }
            )

    groups = []
    for name in names[1:]:
        selected = [row for row in results if row["candidate"] == name]
        require(len(selected) == len(entries), f"paired practice ranking omitted cases: {name}")
        aggregate_logs = [math.log(row["speedup"]) for row in selected]
        seed = per_case_seed(suite.BOOTSTRAP_SEED, PRACTICE, name)
        low, high = confidence_interval(aggregate_logs, seed, bootstraps)
        groups.append(
            {
                "cohort": PRACTICE,
                "candidate": name,
                "cases": len(selected),
                "weight": sum(row["weight"] for row in selected),
                "geomean_speedup": math.exp(statistics.fmean(aggregate_logs)),
                "ci95_low": low,
                "ci95_high": high,
                "statistically_faster_cases": sum(row["statistically_faster"] for row in selected),
                "regressions_gt_20pct": sum(row["regression_gt_20pct"] for row in selected),
            }
        )
    groups.sort(key=lambda row: (-row["geomean_speedup"], row["candidate"]))
    return results, groups


def save_json(path: Path, document: dict, *, replace_identical: bool = False) -> str:
    payload = (
        json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    if path.exists():
        require(replace_identical, f"refusing to overwrite practice evidence: {path}")
        require(path.read_bytes() == payload, f"existing practice evidence differs: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as output:
            output.write(payload)
    return hashlib.sha256(payload).hexdigest()


def measure(args: argparse.Namespace) -> None:
    require(bool(args.exclusive_slot and args.exclusive_slot.strip()), "live timing requires an authorized exclusive slot")
    require(args.trials > 0 and args.bootstraps > 0, "trial and confidence counts must be positive")
    require(1 <= args.max_operations <= MAX_OPERATIONS, "operations exceed the bounded pilot cap")
    suite, entries, manifest, plan = make_plan(args.cases)
    names = selected_modules(suite, args.module)
    edge_oracles = verified_edge_oracles(args.edge_oracle, names)
    modules = {name: importlib.import_module(name) for name in names}
    fingerprints_before = module_fingerprints(modules)
    match_reported_fingerprints(edge_oracles, fingerprints_before)
    target = Path(args.raw)
    target.parent.mkdir(parents=True, exist_ok=True)
    require(not target.exists(), f"refusing to overwrite raw practice measurements: {target}")
    observed: dict[tuple[str, int, str], dict] = {}
    raw_digest = hashlib.sha256()
    checks = 0

    with target.open("xb") as destination:
        with gzip.GzipFile(filename="", fileobj=destination, mode="wb", compresslevel=9, mtime=0) as compressed:
            for position, (_index, case, want, reasons) in enumerate(entries, 1):
                require(case["cohort"] == PRACTICE, "hidden case reached a live calibration measurement")
                actions = {name: operation(module, case) for name, module in modules.items()}
                operations = min(case["ops"], args.max_operations)
                for trial in range(args.trials):
                    order = trial_order(names, case["id"], trial, suite.ORDER_SEED)
                    for order_index, name in enumerate(order):
                        action = actions[name]
                        expected_digest = correctness_gate(modules[name], case, want)
                        checks += 1
                        for _ in range(suite.WARMUPS):
                            action()

                        tracemalloc.start()
                        try:
                            sampled = action()
                            _current, peak = tracemalloc.get_traced_memory()
                        finally:
                            tracemalloc.stop()
                        exact_snapshot(sampled, want, expected_digest, f"memory: {name} {case['id']}")
                        checks += 1

                        before_memory = proc_memory()
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
                        after_memory = proc_memory()
                        exact_snapshot(result, want, expected_digest, f"post-timing: {name} {case['id']}")
                        checks += 1
                        require(elapsed > 0, f"nonpositive practice timing: {name} {case['id']}")

                        row = {
                            "schema": ROW_SCHEMA,
                            "measurement": "bounded practice diagnostic only; not a holdout result",
                            "case": case["id"],
                            "cohort": PRACTICE,
                            "category": case["category"],
                            "api": case["api"],
                            "lifecycle": case["lifecycle"],
                            "input": source_kind(case),
                            "result_density": density(want["result"]),
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
                        require(valid_process_memory(row), "invalid paired practice process memory")
                        key = (case["id"], trial, name)
                        require(key not in observed, f"duplicate paired practice measurement: {key}")
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
                                "schema": ROW_SCHEMA + "-progress",
                                "cohort": PRACTICE,
                                "completed": position,
                                "cases": len(entries),
                                "holdout_accessed": False,
                            },
                            sort_keys=True,
                        ),
                        flush=True,
                    )

    required_rows = len(entries) * args.trials * len(names)
    require(len(observed) == required_rows, "paired practice trial denominator changed")
    require(checks == 3 * required_rows, "a pre-, memory-, or post-timing gate was omitted")
    fingerprints_after = module_fingerprints(modules)
    require(fingerprints_before == fingerprints_after, "candidate binaries changed during exclusive timing")
    results, rankings = summarize_measurements(
        suite, entries, names, observed, args.trials, args.bootstraps
    )
    require(
        len(results) == len(entries) * (len(names) - 1),
        "paired practice candidate case results were omitted",
    )
    report = {
        "schema": REPORT_SCHEMA,
        "measurement": "balanced practice diagnostic only; not a holdout result or final speed claim",
        "cohort": PRACTICE,
        "holdout_accessed": False,
        "exclusive_slot": args.exclusive_slot,
        "verified_edge_oracles": edge_oracles,
        "expected_sha256": manifest["expected_sha256"],
        "selection_seed": plan["selection_seed"],
        "order_seed": suite.ORDER_SEED,
        "bootstrap_seed": suite.BOOTSTRAP_SEED,
        "modules": list(names),
        "cases": len(entries),
        "all_bounded_workload_categories": plan["all_bounded_workload_categories"],
        "public_operations": plan["public_operations"],
        "lifetimes": plan["lifetimes"],
        "inputs": plan["inputs"],
        "result_densities": plan["result_densities"],
        "api_lifetimes": plan["api_lifetimes"],
        "trials": args.trials,
        "warmups": suite.WARMUPS,
        "maximum_operations_per_trial": args.max_operations,
        "bootstrap_samples": args.bootstraps,
        "strict_regression_speedup_threshold": REGRESSION_SPEEDUP_THRESHOLD,
        "raw_path": str(target.resolve()),
        "raw_sha256": raw_digest.hexdigest(),
        "compressed_raw_sha256": file_sha256(target),
        "paired_raw_rows": required_rows,
        "correctness_checks": checks,
        "candidate_binary_sha256_before": fingerprints_before,
        "candidate_binary_sha256_after": fingerprints_after,
        "case_results": results,
        "rankings": rankings,
        "regressions": [row for row in results if row["regression_gt_20pct"]],
        "failed": 0,
    }
    report_path = Path(args.output)
    report_sha256 = save_json(report_path, report)
    print(
        json.dumps(
            {
                "schema": REPORT_SCHEMA,
                "cohort": PRACTICE,
                "holdout_accessed": False,
                "cases": len(entries),
                "categories": plan["all_bounded_workload_categories"],
                "public_operations": len(plan["public_operations"]),
                "modules": list(names),
                "trials": args.trials,
                "paired_raw_rows": required_rows,
                "correctness_checks": checks,
                "strict_regressions": len(report["regressions"]),
                "raw_sha256": raw_digest.hexdigest(),
                "compressed_raw_sha256": report["compressed_raw_sha256"],
                "report_sha256": report_sha256,
                "failed": 0,
            },
            sort_keys=True,
        )
    )


def self_test(target: int) -> dict:
    boundary = verify_regression_boundaries()
    first_suite, first_entries, first_manifest, first = make_plan(target)
    second_suite, second_entries, second_manifest, second = make_plan(target)
    require(first == second, "seeded practice planning is not deterministic")
    require(first_manifest == second_manifest, "frozen practice fixtures changed")
    require(first_suite.ORDER_SEED == second_suite.ORDER_SEED, "frozen trial seed changed")
    require(
        [case["id"] for _position, case, _want, _reasons in first_entries]
        == [case["id"] for _position, case, _want, _reasons in second_entries],
        "repeated seeded practice planning selected different cases",
    )

    _suite, pairs, _manifest, _history, _fixture_manifest = load_calibration_fixture()
    hidden = {
        "id": "hold.self-test.should-never-be-read",
        "cohort": "holdout",
    }
    unchanged = selected_entries(
        [*pairs, (len(pairs), hidden, {})], target, first["selection_seed"]
    )
    require(
        [case["id"] for _number, case, _want, _reason in unchanged]
        == [case["id"] for _number, case, _want, _reason in first_entries],
        "a synthetic hidden workload influenced practice selection",
    )
    checks = ((0.80, True), (0.81, True), (0.833, True), (5.0 / 6.0, False), (0.84, False), (1.0, False))
    require(
        all(is_runtime_regression(value) is result for value, result in checks),
        "strict pilot slowdown threshold changed",
    )
    require(
        confidence_interval([0.0] * 7, first["bootstrap_seed"], 31) == (1.0, 1.0),
        "self-versus-self paired confidence interval is not exactly 1×",
    )
    modules = (BASELINE, RUST, "candidates.zig_candidate")
    case_id = first_entries[0][1]["id"]
    order = trial_order(modules, case_id, 0, first["order_seed"])
    require(order == trial_order(modules, case_id, 0, first["order_seed"]), "paired trial order is not deterministic")
    require(set(order) == set(modules), "seeded paired order dropped an engine")

    synthetic_value = ["practice", 7, {"exact": True}]
    synthetic_expected = {"result": snapshot(synthetic_value)}
    synthetic_digest = digest(synthetic_expected["result"])
    exact_snapshot(synthetic_value, synthetic_expected, synthetic_digest, "synthetic")
    for corrupted in (
        ["practice", 8, {"exact": True}],
        ["practice", 7, {"exact": False}],
    ):
        try:
            exact_snapshot(corrupted, synthetic_expected, synthetic_digest, "synthetic")
        except RuntimeError:
            pass
        else:
            raise RuntimeError("paired exact-result gate accepted a corrupted snapshot")

    rejected = 0
    for invalid in (MIN_CASES - 1, MAX_CASES + 1):
        try:
            selected_entries(pairs, invalid, first["selection_seed"])
        except RuntimeError:
            rejected += 1
        else:
            raise RuntimeError("bounded practice planner accepted an invalid case denominator")

    observed_decodes: list[bytes] = []
    synthetic_case = {"id": "cal.synthetic.poison", "cohort": PRACTICE, "category": "synthetic"}
    synthetic_answer = {
        "id": synthetic_case["id"],
        "cohort": PRACTICE,
        "category": synthetic_case["category"],
        "result": snapshot(["calibration", 3]),
    }
    synthetic_answer["result_sha256"] = digest(synthetic_answer["result"])
    practice_line = (
        json.dumps(synthetic_answer, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")
    poison_line = (
        b'{"category":"poison","cohort":"holdout","id":"hold.poison",'
        b'"result":THIS_MUST_NEVER_BE_JSON_DECODED}\n'
    )

    def guarded_decoder(payload: bytes) -> dict:
        require(b'"cohort":"holdout"' not in payload, "a poisoned hidden record reached the JSON decoder")
        observed_decodes.append(payload)
        return json.loads(payload)

    decoded = decode_calibration_expected(
        (poison_line, practice_line, poison_line),
        {synthetic_case["id"]: synthetic_case},
        decoder=guarded_decoder,
    )
    require(decoded == {synthetic_case["id"]: synthetic_answer}, "poisoned hidden bytes changed practice decoding")
    require(observed_decodes == [practice_line], "a hidden record reached practice JSON deserialization")
    observed_generation: list[tuple[str, str, int]] = []

    def poisoned_generator(cohort: str, family: str, variant: int) -> dict:
        require(cohort == PRACTICE, "the poisoned generator received a held-out cohort")
        observed_generation.append((cohort, family, variant))
        return {
            "id": f"cal.synthetic.generated.{variant}",
            "cohort": cohort,
            "category": family,
        }

    synthetic_suite = types.SimpleNamespace(
        FAMILIES=("synthetic",),
        VARIANTS=2,
        generated_case=poisoned_generator,
    )
    synthetic_pairs: list[tuple[int, dict]] = []
    require(
        append_generated_calibration_cases(synthetic_suite, synthetic_pairs, 73, "poisoned generator") == 2,
        "poisoned practice generator changed its workload count",
    )
    require(
        observed_generation == [(PRACTICE, "synthetic", 0), (PRACTICE, "synthetic", 1)]
        and [position for position, _case in synthetic_pairs] == [73, 74],
        "the poisoned generator reached a hidden workload or changed practice positions",
    )
    try:
        forbidden_full_cohort()
    except RuntimeError:
        rejected += 1
    else:
        raise RuntimeError("full-cohort generation was not poisoned")

    candidates_root = ROOT / "candidates"
    bridges = sorted(candidates_root.glob("_rust_bridge.*.so"))
    require(len(bridges) == 1, "native provenance self-test requires exactly one production Rust bridge")
    roles = {
        "public-python": candidates_root / "rust_candidate.py",
        "native-bridge": bridges[0],
        "native-engine": candidates_root / "_rust_engine.so",
        "native-source": candidates_root / "rust/src/lib.rs",
        "bridge-source": candidates_root / "rust/py_bridge.c",
    }
    evidence = [
        {
            "role": role,
            "path": str(path.resolve().relative_to(ROOT.resolve())),
            "sha256": file_sha256(path),
        }
        for role, path in roles.items()
    ]
    valid = verify_reported_artifacts(RUST, evidence)
    synthetic_fingerprints = {
        f"{RUST}:module": valid["public-python"]["sha256"],
        f"{RUST}:native-bridge": valid["native-bridge"]["sha256"],
        f"{RUST}:native-engine": valid["native-engine"]["sha256"],
        f"{RUST}:native-source": valid["native-source"]["sha256"],
        f"{RUST}:bridge-source": valid["bridge-source"]["sha256"],
    }
    valid_report = {"module": RUST, "candidate_artifacts": valid}
    match_reported_fingerprints([valid_report], synthetic_fingerprints)
    for corruption in (
        evidence[:-1],
        [*evidence, dict(evidence[0])],
        [
            {**artifact, "path": evidence[1]["path"], "sha256": evidence[1]["sha256"]}
            if artifact["role"] == "native-engine" else artifact
            for artifact in evidence
        ],
        [
            {**artifact, "sha256": "0" * 64}
            if artifact["role"] == "native-source" else artifact
            for artifact in evidence
        ],
    ):
        try:
            verify_reported_artifacts(RUST, corruption)
        except RuntimeError:
            rejected += 1
        else:
            raise RuntimeError("native provenance accepted missing, duplicated, swapped, or stale artifacts")

    try:
        match_reported_fingerprints(
            [valid_report],
            {**synthetic_fingerprints, f"{RUST}:native-engine": "0" * 64},
        )
    except RuntimeError:
        rejected += 1
    else:
        raise RuntimeError("native provenance accepted a different measured Rust engine")

    current_edge_source = file_sha256(ROOT / "tools/rust_v7_edge_oracle.py")
    verify_edge_source_hash({"script_sha256": current_edge_source}, current_edge_source, "synthetic")
    try:
        verify_edge_source_hash({"script_sha256": "0" * 64}, current_edge_source, "synthetic")
    except RuntimeError:
        rejected += 1
    else:
        raise RuntimeError("native provenance accepted a stale correctness-oracle source")

    return {
        "schema": PLAN_SCHEMA + "-self-test",
        **boundary,
        "cases": len(first_entries),
        "categories": first["all_bounded_workload_categories"],
        "public_operations": len(first["public_operations"]),
        "api_lifetime_pairs": len(first["api_lifetimes"]),
        "input_representations": len(first["inputs"]),
        "result_densities": len(first["result_densities"]),
        "hidden_case_noninterference_checks": 3,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "poisoned_record_decoder_checks": 2,
        "poisoned_generation_checks": len(observed_generation),
        "native_provenance_roles": len(valid),
        "current_edge_oracle_sha256": current_edge_source,
        "rejected_corruptions": rejected,
        "deterministic_selection": True,
        "deterministic_trial_order": True,
        "self_comparison_confidence": 1.0,
        "holdout_accessed": False,
        "timing_performed": False,
        "failed": 0,
    }


def save_plan(args: argparse.Namespace) -> None:
    _suite, _entries, _manifest, plan = make_plan(args.cases)
    destination = Path(args.output)
    controls = self_test(args.cases) if args.verify else None
    document = {**plan, "self_test": controls} if controls is not None else plan
    if destination.exists():
        try:
            previous = json.loads(destination.read_bytes())
        except (UnicodeError, json.JSONDecodeError) as error:
            raise RuntimeError("existing frozen calibration plan is invalid") from error
        require(isinstance(previous, dict), "existing frozen calibration plan is not an object")
        require(
            {key: value for key, value in previous.items() if key != "self_test"} == plan,
            "refusing to change the frozen 624-case calibration plan",
        )
        document = previous
    plan_sha256 = save_json(destination, document, replace_identical=True)
    print(
        json.dumps(
            {
                "schema": PLAN_SCHEMA,
                "cohort": PRACTICE,
                "holdout_accessed": False,
                "historical_performance_read": False,
                "timing_performed": False,
                "cases": plan["cases"],
                "categories": plan["all_bounded_workload_categories"],
                "public_operations": plan["public_operations"],
                "api_lifetime_pairs": len(plan["api_lifetimes"]),
                "inputs": plan["inputs"],
                "result_densities": plan["result_densities"],
                "maximum_subject_length": plan["maximum_subject_length"],
                "maximum_result_count": plan["maximum_result_count"],
                "selection_seed": plan["selection_seed"],
                "plan_sha256": plan_sha256,
                "failed": 0,
            },
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    freeze = commands.add_parser(
        "freeze-calibration-fixture",
        help="extract only byte-identified practice records into a sealed single-cohort archive",
    )
    freeze.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    freeze.add_argument("--manifest", type=Path, default=DEFAULT_FIXTURE_MANIFEST)
    freeze.add_argument("--history", type=Path, default=DEFAULT_PRIORITIES_ARCHIVE)
    freeze.set_defaults(handler=freeze_calibration_fixture)

    plan = commands.add_parser("plan", help="freeze a bounded practice plan without timing")
    plan.add_argument("--cases", type=positive_int, default=DEFAULT_CASES)
    plan.add_argument("--output", type=Path, default=DEFAULT_PLAN)
    plan.add_argument("--verify", action="store_true")
    plan.set_defaults(handler=save_plan)

    test = commands.add_parser("self-test", help="verify the plan without importing a candidate")
    test.add_argument("--cases", type=positive_int, default=DEFAULT_CASES)
    test.set_defaults(handler=lambda args: print(json.dumps(self_test(args.cases), sort_keys=True)))

    live = commands.add_parser("measure", help="run only in an explicitly authorized timing slot")
    live.add_argument("--exclusive-slot", required=True)
    live.add_argument(
        "--edge-oracle",
        type=Path,
        action="append",
        required=True,
        help="passing committed independent edge-oracle report; repeat once per measured candidate",
    )
    live.add_argument("--cases", type=positive_int, default=DEFAULT_CASES)
    live.add_argument("--raw", type=Path, required=True)
    live.add_argument("--output", type=Path, required=True)
    live.add_argument("--module", action="append")
    live.add_argument("--trials", type=positive_int, default=DEFAULT_TRIALS)
    live.add_argument("--max-operations", type=positive_int, default=MAX_OPERATIONS)
    live.add_argument("--bootstraps", type=positive_int, default=DEFAULT_BOOTSTRAPS)
    live.set_defaults(handler=measure)

    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
