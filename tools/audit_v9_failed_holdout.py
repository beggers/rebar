#!/usr/bin/env python3
"""Verify the original, irreversible failed final run without retrying it.

Only the original closed partial gzip, immutable unseal marker, committed
candidate freeze, and prospective manifest are read.  Candidate engines,
opening material, benchmark execution, generated cases, final speeds, memory,
and completed rankings are never loaded or reconstructed.
"""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import os
import sys
from pathlib import Path
from typing import BinaryIO, Iterable


ROOT = Path(__file__).absolute().parent.parent
EVIDENCE = ROOT / "performance/v9/evidence"
MARKER_PATH = EVIDENCE / "V9-FINAL-HOLDOUT-24576-UNSEAL-MARKER.json"
RAW_PATH = EVIDENCE / "V9-FINAL-HOLDOUT-24576-RAW.jsonl.gz"
FREEZE_PATH = EVIDENCE / "V9-FINAL-CANDIDATE-SELECTION-FREEZE.json"
MANIFEST_PATH = ROOT / "performance/v9/holdout-manifest.json"
PROTOCOL_SOURCE_PATH = ROOT / "tools/rust_v9_holdout_protocol.py"
OUTPUT_PATH = EVIDENCE / "V9-FINAL-HOLDOUT-24576-FAILURE.json"

SCHEMA = "rebar-v9-sealed-final-holdout-failure-v1"
MARKER_SCHEMA = "rebar-v9-single-use-final-unseal-v1"
FREEZE_SCHEMA = "rebar-v9-current-native-candidate-freeze-v1"
MANIFEST_SCHEMA = "rebar-v9-prospective-semantic-performance-holdout-v1"
ROW_SCHEMA = "rebar-v9-real-public-operation-paired-row-v1"
MARKER_SHA256 = "1df71b41bfdad7e850344242c16dc15c79039b9b925b1fbc709de18cce917cb2"
PARTIAL_RAW_SHA256 = "b93b5318fbd260d0778196f1ab5c668f003647c86b66b015fe369261f72ac53e"
CANDIDATE_FREEZE_SHA256 = "52066760bb4210a57f7b10f13e9ff73e36c53982a5b97aff40ead330c79edf41"
MANIFEST_SHA256 = "d747bfbca78e94b7dada3fdc24acd027fc8cd2e31a46a9441c328fb72153460f"
PROTOCOL_SOURCE_SHA256 = "a699ce1e661ead447af0643584d69f080e72712059ad611fbd6b998f2ca19219"
PROTOCOL_BINDING_SHA256 = "1ebfa3b1a57c285826627e0362c78daff016b4029529639502325550a1ac0aaf"
FROM_SCRATCH_AUDIT_SHA256 = "a790fe1a75c8748df7f8bb6f1e39d0be841636055358aaee94db0aa35523f326"
MODULES = (
    "re", "candidates.vm_candidate",
    "candidates.rust_candidate", "candidates.zig_candidate",
)
HOLDOUT_STATE = "irreversibly-authorized-no-retry"
FAILURE_CASE = "v9.split.literal-and-long-prefix.006"
FAILURE_ROUND = "warmup"
FAILURE_CANDIDATE = "candidates.zig_candidate"
FAILURE_MESSAGE = (
    "v9 sealed protocol rejected: pinned CPython result mismatch: "
    "v9.split.literal-and-long-prefix.006:warmup:candidates.zig_candidate"
)
RUNNER_EXIT_CODE = 2
REQUIRED_CASES = 24_576
COMPLETE_CASES = 14_342
TRIALS_PER_MODULE_CASE = 31
PAIRED_MODULES_PER_CASE = 4
REQUIRED_RAW_ROWS = 3_047_424
OBSERVED_RAW_ROWS = 1_778_408
OPERATIONS_PER_SAMPLE = 16

EXPECTED_QUALIFICATIONS = (
    {
        "module": "candidates.vm_candidate",
        "full_correctness_campaign_sha256": "a29b540e01fc9f565e01e5cc62af14db30b38d9bacbaf55e4950e95b17c7ea40",
        "deep_contract_sha256": "0b25f1793636eac02d9231b0d5ec546aa6800eab118b0e98f98f5e6276dbb65e",
        "edge_sha256": "c843dccc2d0b8eb1dcada2af282679ca05a1be2de98afc39bad95e7f448f4d7a",
        "native_artifact_sha256": {
            "native-bridge": "f6458cb4bf190f042e7d417a40020d2d58cebcb39671fda7352aab9725a7f633",
            "public-python": "91d848e2627f19e552fef19b9943eb3e265e25537934128875645bab63cf7b80",
        },
    },
    {
        "module": "candidates.rust_candidate",
        "full_correctness_campaign_sha256": "9ddbab81b16f0440ca19bffb8a539ea08d4a7ff33606ee3019eaf85977c2249a",
        "deep_contract_sha256": "f012d5e16305783d70fe6b7ece86a7692b2ac37c310c9a7e12cc856f91e0d1d0",
        "edge_sha256": "c3e67b08ac34540dbbd248b5ffb07161ae7e9b815a6f6bcbc757ef178f7585b1",
        "native_artifact_sha256": {
            "bridge-source": "83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed",
            "native-bridge": "1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34",
            "native-engine": "e7177c97070b2d0073a721044c4d23bb93e0d0883c1f2ccaa07c41eda8b96255",
            "native-source": "4b89d916e4c33e2b516be570ff3e75694f03dcea5eccf9320cedf07471b07dac",
            "public-python": "80812459261edb9585bdf703f137af3e0e788638af2ad7183d00b6d357e8a926",
        },
    },
    {
        "module": "candidates.zig_candidate",
        "full_correctness_campaign_sha256": "4ba7cb9c45a70b747cc0a6eb721f6bb51081157f527d1bf5e578e603715ae5dc",
        "deep_contract_sha256": "422f662f7c01e961ae0e913ed8e1bc1927b80c70530d7982a4a65784bf649a91",
        "edge_sha256": "a4c8b75811b5304ab115fb387f821127a20ed2615e7948ab4b96443dbe1ebe5c",
        "native_artifact_sha256": {
            "native-bridge": "80d7dab57cbee317ee1727862e27cd7dcf4cb22e1a944f4b29f2e4e983f940ed",
            "native-engine": "70bafca56a3f48477b2011f016a81b625e5f40a772af6a986d32b9098269f614",
            "public-python": "95a2010152099f2db61595927542b2f25a675eb72bd33125659969d804360239",
        },
    },
)


class AuditError(Exception):
    """The one irreversible final failure cannot be honestly certified."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise AuditError(message)


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    document: dict[str, object] = {}
    for key, value in pairs:
        require(key not in document, "duplicate JSON keys conceal original evidence")
        document[key] = value
    return document


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as source:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
    except OSError as error:
        raise AuditError(f"cannot read required original evidence: {path.name}") from error
    return digest.hexdigest()


def read_frozen_json(path: Path, expected_sha256: str, label: str) -> dict:
    require(sha256_file(path) == expected_sha256, f"the exact original {label} was replaced or modified")
    try:
        with path.open("rb") as source:
            document = json.load(source, object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AuditError(f"cannot decode the original {label}") from error
    require(isinstance(document, dict), f"the original {label} is not a JSON object")
    return document


def validate_marker(document: dict) -> None:
    require(document.get("schema") == MARKER_SCHEMA, "the original single-use unseal marker schema changed")
    require(document.get("state") == HOLDOUT_STATE, "the original final unseal is not irreversibly closed against retry")
    require(document.get("protocol_binding_sha256") == PROTOCOL_BINDING_SHA256, "the original marker is bound to another final protocol")
    require(document.get("candidate_freeze_sha256") == CANDIDATE_FREEZE_SHA256, "the original marker is bound to another candidate freeze")
    require(document.get("modules") == list(MODULES), "the original marker changed final paired candidate order")
    require("opening_sha256" in document, "the original single-use marker omitted its committed seal binding")


def validate_manifest(document: dict) -> None:
    require(document.get("schema") == MANIFEST_SCHEMA, "the immutable prospective final manifest schema changed")
    require(document.get("state") == "prospectively-sealed-not-materialized", "the original prospective manifest state changed")
    require(document.get("binding_sha256") == PROTOCOL_BINDING_SHA256, "the prospective manifest is bound to another final protocol")
    layout = document.get("layout")
    require(isinstance(layout, dict) and layout.get("cases") == REQUIRED_CASES, "the immutable final case denominator changed")
    trials = document.get("trials")
    require(isinstance(trials, dict), "the immutable prospective paired-trial protocol is missing")
    require(trials.get("paired_rounds") == TRIALS_PER_MODULE_CASE, "the immutable final paired-round denominator changed")
    require(trials.get("four_engine_timed_rows") == REQUIRED_RAW_ROWS, "the immutable final required-row denominator changed")
    require(trials.get("minimum_candidates") == 3, "the immutable final three-family requirement changed")
    require(trials.get("operations_per_sample") == OPERATIONS_PER_SAMPLE, "the immutable final public-operation count changed")
    source = document.get("source")
    require(isinstance(source, dict), "the original final-protocol source commitment is missing")
    require(source.get("path") == "tools/rust_v9_holdout_protocol.py", "the manifest names another final protocol")
    require(source.get("sha256") == PROTOCOL_SOURCE_SHA256, "the manifest changed its immutable final-protocol source")


def validate_freeze(document: dict) -> list[dict]:
    require(document.get("schema") == FREEZE_SCHEMA, "the committed independent native-candidate freeze schema changed")
    require(document.get("protocol_binding_sha256") == PROTOCOL_BINDING_SHA256, "the committed freeze is bound to another final protocol")
    require(document.get("from_scratch_audit_sha256") == FROM_SCRATCH_AUDIT_SHA256, "the committed freeze changed its original no-delegation audit")
    require(document.get("baseline") == "re", "the committed freeze changed its pinned Python baseline")
    require(document.get("hidden_cases_generated") == 0, "the committed candidate-selection freeze was taken after hidden case generation")
    require(document.get("opening_read") is False, "the committed candidate-selection freeze had opened held-out material")
    require(document.get("performance_measured") is False, "the committed candidate-selection freeze was taken after final timing")
    entries = document.get("candidates")
    require(isinstance(entries, list) and len(entries) == 3, "the committed final freeze omitted an independent candidate family")
    normalized: list[dict] = []
    for entry, expected in zip(entries, EXPECTED_QUALIFICATIONS, strict=True):
        require(isinstance(entry, dict), "the committed final freeze contains a malformed independent candidate")
        require(entry.get("module") == expected["module"], "the committed final freeze reordered or substituted a native family")
        require(entry.get("campaign_sha256") == expected["full_correctness_campaign_sha256"], "the committed final freeze changed a passing complete correctness campaign")
        require(entry.get("deep_contract_sha256") == expected["deep_contract_sha256"], "the committed final freeze changed a public deep correctness proof")
        require(entry.get("edge_sha256") == expected["edge_sha256"], "the committed final freeze changed a decompressed independent matching proof")
        artifacts = entry.get("artifacts")
        expected_artifacts = expected["native_artifact_sha256"]
        require(isinstance(artifacts, dict) and set(artifacts) == set(expected_artifacts), "the committed final freeze omitted or replaced a native production role")
        for role, expected_digest in expected_artifacts.items():
            artifact = artifacts.get(role)
            require(isinstance(artifact, dict) and artifact.get("sha256") == expected_digest, f"the committed final freeze replaced {expected['module']}:{role}")
            artifact_path = artifact.get("path")
            require(isinstance(artifact_path, str) and Path(artifact_path).is_absolute(), "the committed final freeze omitted a native artifact provenance path")
        normalized.append(copy.deepcopy(expected))
    return normalized


def parse_row(line: bytes, index: int) -> dict:
    require(isinstance(line, bytes) and 0 < len(line) <= 1024 * 1024, f"partial final row {index} is missing or exceeds its safe bound")
    try:
        document = json.loads(line, object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise AuditError(f"partial final row {index} is not valid unique-key JSON") from error
    require(isinstance(document, dict), f"partial final row {index} is not a JSON object")
    return document


def scan_rows(
    lines: Iterable[bytes], *, modules: tuple[str, ...],
    expected_cases: int, expected_rounds: int, expected_rows: int,
) -> dict:
    require(len(modules) == PAIRED_MODULES_PER_CASE and len(set(modules)) == PAIRED_MODULES_PER_CASE, "the paired final candidate-module denominator changed")
    require(isinstance(expected_cases, int) and not isinstance(expected_cases, bool) and expected_cases > 0, "the completed partial case denominator is invalid")
    require(isinstance(expected_rounds, int) and not isinstance(expected_rounds, bool) and expected_rounds > 0, "the completed partial round denominator is invalid")
    require(expected_rows == expected_cases * expected_rounds * len(modules), "the observed partial final row denominator is inconsistent")
    by_module = {module: 0 for module in modules}
    by_round = {str(round_index): 0 for round_index in range(expected_rounds)}
    module_set = set(modules)
    seen_cases: set[str] = set()
    seen_round_modules: set[str] = set()
    current_case: str | None = None
    count = 0
    for line in lines:
        require(count < expected_rows, "the irreversible partial final evidence contains unexpected extra rows")
        row = parse_row(line, count)
        require(row.get("schema") == ROW_SCHEMA, "the original timed partial final row schema changed")
        case = row.get("case")
        require(isinstance(case, str) and case.startswith("v9."), "the original partial final row omitted its case identity")
        require(case != FAILURE_CASE, "the failing warmup was falsely recorded as a complete paired timed case")
        module = row.get("module")
        require(isinstance(module, str) and module in module_set, "the partial final evidence introduced an unqualified candidate")
        round_index = row.get("round")
        position = row.get("position")
        require(isinstance(round_index, int) and not isinstance(round_index, bool), "a partial final row changed its paired round type")
        require(isinstance(position, int) and not isinstance(position, bool), "a partial final row changed its paired module position")
        expected_round = (count // len(modules)) % expected_rounds
        expected_position = count % len(modules)
        require(round_index == expected_round, "the original partial final evidence skipped, reordered, or repeated a trial")
        require(position == expected_position, "the original partial final evidence skipped or repeated a module position")
        if expected_round == 0 and expected_position == 0:
            require(case not in seen_cases, "the partial final evidence repeated a completed held-out case")
            seen_cases.add(case)
            current_case = case
        require(case == current_case, "the partial final evidence interleaved or truncated a complete paired case")
        if expected_position == 0:
            seen_round_modules.clear()
        require(module not in seen_round_modules, "the partial final evidence repeated a candidate within one paired round")
        seen_round_modules.add(module)
        require(row.get("operations") == OPERATIONS_PER_SAMPLE and not isinstance(row.get("operations"), bool), "the original final timed operation denominator changed")
        require(row.get("correctness_pre") is True, "a recorded partial final row failed its pre-operation correctness gate")
        require(row.get("correctness_timed") is True, "a recorded partial final row failed its timed-operation correctness gate")
        require(row.get("correctness_post") is True, "a recorded partial final row failed its post-operation correctness gate")
        if expected_position == len(modules) - 1:
            require(seen_round_modules == module_set, "the partial final evidence omitted a candidate in a paired round")
        by_module[module] += 1
        by_round[str(round_index)] += 1
        count += 1
    require(count == expected_rows, "the original closed final gzip does not contain its actual complete partial row count")
    require(len(seen_cases) == expected_cases, "the closed final gzip does not contain its actual complete-case count")
    require(all(value == expected_cases * expected_rounds for value in by_module.values()), "the partial final evidence is not balanced across four frozen candidates")
    require(all(value == expected_cases * len(modules) for value in by_round.values()), "the partial final evidence is not balanced across all frozen rounds")
    return {
        "observed_raw_rows": count,
        "complete_cases": len(seen_cases),
        "incomplete_case_rows": 0,
        "rows_by_module": by_module,
        "rows_by_round": by_round,
        "gzip_valid": True,
    }


def scan_gzip(source: BinaryIO, *, expected_cases: int, expected_rounds: int, expected_rows: int) -> dict:
    try:
        with gzip.GzipFile(fileobj=source, mode="rb") as decompressed:
            return scan_rows(
                decompressed, modules=MODULES, expected_cases=expected_cases,
                expected_rounds=expected_rounds, expected_rows=expected_rows,
            )
    except (OSError, EOFError, gzip.BadGzipFile) as error:
        raise AuditError("the original partial final gzip is truncated, invalid, or has a failed CRC") from error


def fixture_rows() -> list[bytes]:
    lines: list[bytes] = []
    for case_index in range(2):
        case = f"v9.synthetic.case.{case_index:03d}"
        for round_index in range(2):
            rotated = MODULES[round_index:] + MODULES[:round_index]
            for position, module in enumerate(rotated):
                document = {
                    "schema": ROW_SCHEMA, "case": case,
                    "module": module, "round": round_index,
                    "position": position, "operations": OPERATIONS_PER_SAMPLE,
                    "correctness_pre": True, "correctness_timed": True,
                    "correctness_post": True,
                }
                lines.append((json.dumps(document, sort_keys=True) + "\n").encode("ascii"))
    return lines


def self_test() -> dict:
    lines = fixture_rows()
    expected = scan_rows(lines, modules=MODULES, expected_cases=2, expected_rounds=2, expected_rows=16)
    require(expected["complete_cases"] == 2 and expected["observed_raw_rows"] == 16, "the isolated failure-auditor synthetic self-oracle rejected its clean fixture")
    compressed = gzip.compress(b"".join(lines), mtime=0)
    validated = scan_gzip(io.BytesIO(compressed), expected_cases=2, expected_rounds=2, expected_rows=16)
    require(validated == expected, "the isolated failure-auditor synthetic gzip self-oracle disagreed")
    controls: list[dict] = []

    def reject(name: str, action: object) -> None:
        try:
            action()  # type: ignore[operator]
        except (AuditError, KeyError, ValueError, TypeError, OverflowError):
            controls.append({"name": name, "passed": True})
            return
        raise AuditError(f"the isolated failure auditor accepted synthetic tampering: {name}")

    def poisoned(index: int, field: str, value: object) -> None:
        changed = list(lines)
        document = parse_row(changed[index], index)
        document[field] = value
        changed[index] = (json.dumps(document, sort_keys=True) + "\n").encode("ascii")
        scan_rows(changed, modules=MODULES, expected_cases=2, expected_rounds=2, expected_rows=16)

    for name, index, field, value in (
        ("foreign-row-schema", 0, "schema", "rebar-forged-paired-row"),
        ("foreign-candidate-module", 0, "module", "candidates.external_regex"),
        ("candidate-cross-family-repeat", 1, "module", MODULES[0]),
        ("hidden-failure-present-in-complete-rows", 0, "case", FAILURE_CASE),
        ("empty-case-identity", 0, "case", ""),
        ("non-string-case-identity", 0, "case", 42),
        ("skipped-paired-round", 4, "round", 0),
        ("negative-paired-round", 0, "round", -1),
        ("boolean-paired-round", 0, "round", False),
        ("non-integer-paired-round", 0, "round", "0"),
        ("skipped-module-position", 1, "position", 0),
        ("boolean-module-position", 0, "position", False),
        ("non-integer-module-position", 0, "position", "0"),
        ("incorrect-operation-denominator", 0, "operations", 15),
        ("boolean-operation-denominator", 0, "operations", True),
        ("pre-correctness-gate-failure", 0, "correctness_pre", False),
        ("timed-correctness-gate-failure", 0, "correctness_timed", False),
        ("post-correctness-gate-failure", 0, "correctness_post", False),
        ("non-boolean-pre-correctness", 0, "correctness_pre", 1),
        ("interleaved-paired-case", 1, "case", "v9.synthetic.case.999"),
        ("reused-complete-paired-case", 8, "case", "v9.synthetic.case.000"),
    ):
        reject(name, lambda i=index, key=field, item=value: poisoned(i, key, item))
    reject(
        "truncated-paired-json-lines",
        lambda: scan_rows(lines[:-1], modules=MODULES, expected_cases=2, expected_rounds=2, expected_rows=16),
    )
    reject(
        "appended-forged-paired-json-line",
        lambda: scan_rows([*lines, lines[0]], modules=MODULES, expected_cases=2, expected_rounds=2, expected_rows=16),
    )
    reject(
        "malformed-paired-json-line",
        lambda: scan_rows([b"{not-json}\n", *lines[1:]], modules=MODULES, expected_cases=2, expected_rounds=2, expected_rows=16),
    )
    reject(
        "truncated-valid-gzip",
        lambda: scan_gzip(io.BytesIO(compressed[:-5]), expected_cases=2, expected_rounds=2, expected_rows=16),
    )
    reject(
        "duplicate-candidate-module-order",
        lambda: scan_rows(lines, modules=(MODULES[0], MODULES[0], MODULES[2], MODULES[3]), expected_cases=2, expected_rounds=2, expected_rows=16),
    )
    reject(
        "changed-paired-row-denominator",
        lambda: scan_rows(lines, modules=MODULES, expected_cases=2, expected_rounds=2, expected_rows=15),
    )
    reject(
        "zero-complete-case-denominator",
        lambda: scan_rows(lines, modules=MODULES, expected_cases=0, expected_rounds=2, expected_rows=16),
    )
    reject(
        "zero-paired-round-denominator",
        lambda: scan_rows(lines, modules=MODULES, expected_cases=2, expected_rounds=0, expected_rows=16),
    )
    require(len(controls) >= 25, "the independent failure auditor omitted frozen synthetic tamper controls")
    require(not any(module in sys.modules for module in MODULES[1:]), "the synthetic failure verifier imported a candidate")
    return {
        "schema": SCHEMA + "-self-test", "result": "PASS",
        "synthetic_only": True, "timing_performed": False,
        "holdout_opened": False,
        "poisoned_control_count": len(controls),
        "poisoned_controls": controls,
        "failed": 0,
    }


def exact_input(actual: Path, expected: Path, label: str) -> None:
    require(actual.absolute() == expected.absolute(), f"the {label} path differs from the actual irreversible final evidence")


def verify(
    marker_path: Path, raw_path: Path, freeze_path: Path,
    manifest_path: Path, failure_message: str, output_path: Path,
) -> dict:
    exact_input(marker_path, MARKER_PATH, "single-use unseal marker")
    exact_input(raw_path, RAW_PATH, "closed original partial raw gzip")
    exact_input(freeze_path, FREEZE_PATH, "committed candidate freeze")
    exact_input(manifest_path, MANIFEST_PATH, "immutable prospective manifest")
    exact_input(output_path, OUTPUT_PATH, "exclusive irreversible failure report")
    require(failure_message == FAILURE_MESSAGE, "the recorded original pinned-Python rejection was changed or fabricated")
    require(not any(module in sys.modules for module in MODULES[1:]), "the independent final-failure auditor imported a candidate")
    require(REQUIRED_RAW_ROWS == REQUIRED_CASES * TRIALS_PER_MODULE_CASE * PAIRED_MODULES_PER_CASE, "the immutable complete final row denominator is inconsistent")
    require(OBSERVED_RAW_ROWS == COMPLETE_CASES * TRIALS_PER_MODULE_CASE * PAIRED_MODULES_PER_CASE, "the immutable observed partial row denominator is inconsistent")
    require(sha256_file(PROTOCOL_SOURCE_PATH) == PROTOCOL_SOURCE_SHA256, "the immutable original final-protocol source changed")

    marker = read_frozen_json(marker_path, MARKER_SHA256, "single-use irreversible final-unseal marker")
    validate_marker(marker)
    manifest = read_frozen_json(manifest_path, MANIFEST_SHA256, "prospective immutable final manifest")
    validate_manifest(manifest)
    freeze = read_frozen_json(freeze_path, CANDIDATE_FREEZE_SHA256, "committed three-family native candidate freeze")
    qualifications = validate_freeze(freeze)
    require(sha256_file(raw_path) == PARTIAL_RAW_SHA256, "the original closed partial final gzip was replaced or modified")

    try:
        with raw_path.open("rb") as compressed:
            partial = scan_gzip(
                compressed, expected_cases=COMPLETE_CASES,
                expected_rounds=TRIALS_PER_MODULE_CASE,
                expected_rows=OBSERVED_RAW_ROWS,
            )
    except OSError as error:
        raise AuditError("cannot stream the original closed partial final gzip") from error
    controls = self_test()
    require(not any(module in sys.modules for module in MODULES[1:]), "the independent final-failure replay imported a candidate")

    report = {
        "schema": SCHEMA,
        "result": "FALSIFIED",
        "failed": 1,
        "auditor_result": "PASS",
        "holdout_state": HOLDOUT_STATE,
        "retry_permitted": False,
        "final_holdout_unsealed": True,
        "auditor_holdout_opened": False,
        "auditor_timing_performed": False,
        "partial_timing_performed": True,
        "complete_final_timing": False,
        "final_speed": "NOT MEASURED",
        "complete_final_summary": False,
        "complete_final_ranking_count": 0,
        "runner_exit_code": RUNNER_EXIT_CODE,
        "failure_message": FAILURE_MESSAGE,
        "failure_case": FAILURE_CASE,
        "failure_api": "split",
        "failure_round": FAILURE_ROUND,
        "failure_candidate": FAILURE_CANDIDATE,
        "source_sha256": sha256_file(Path(__file__).absolute()),
        "marker_sha256": MARKER_SHA256,
        "partial_raw_sha256": PARTIAL_RAW_SHA256,
        "candidate_freeze_sha256": CANDIDATE_FREEZE_SHA256,
        "manifest_sha256": MANIFEST_SHA256,
        "protocol_source_sha256": PROTOCOL_SOURCE_SHA256,
        "protocol_binding_sha256": PROTOCOL_BINDING_SHA256,
        "from_scratch_audit_sha256": FROM_SCRATCH_AUDIT_SHA256,
        "module_order": list(MODULES),
        "paired_modules_per_case": PAIRED_MODULES_PER_CASE,
        "trials_per_module_case": TRIALS_PER_MODULE_CASE,
        "operations_per_sample": OPERATIONS_PER_SAMPLE,
        "required_cases": REQUIRED_CASES,
        "required_raw_rows": REQUIRED_RAW_ROWS,
        "candidate_qualifications": qualifications,
        **partial,
        "self_test": controls,
    }
    require(report["observed_raw_rows"] < report["required_raw_rows"], "a complete final result cannot be misrepresented as an interrupted failure")
    encoded = (
        json.dumps(report, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")
    try:
        with output_path.open("xb") as destination:
            destination.write(encoded)
            destination.flush()
            os.fsync(destination.fileno())
    except FileExistsError as error:
        raise AuditError("the irreversible final-failure report already exists; retries are forbidden") from error
    except OSError as error:
        raise AuditError("cannot persist the exclusive irreversible final-failure proof") from error
    return {
        "schema": SCHEMA,
        "result": "FALSIFIED",
        "failed": 1,
        "auditor_result": "PASS",
        "holdout_state": HOLDOUT_STATE,
        "retry_permitted": False,
        "auditor_timing_performed": False,
        "partial_timing_performed": True,
        "complete_final_timing": False,
        "final_speed": "NOT MEASURED",
        "runner_exit_code": RUNNER_EXIT_CODE,
        "observed_raw_rows": partial["observed_raw_rows"],
        "required_raw_rows": REQUIRED_RAW_ROWS,
        "complete_cases": partial["complete_cases"],
        "required_cases": REQUIRED_CASES,
        "incomplete_case_rows": partial["incomplete_case_rows"],
        "poisoned_control_count": controls["poisoned_control_count"],
        "output": str(output_path.absolute()),
        "sha256": hashlib.sha256(encoded).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="verify only in-memory candidate-free corruption controls")
    audit = commands.add_parser("verify", help="stream the exact one-time failed final evidence without retrying")
    audit.add_argument("--marker", required=True, type=Path)
    audit.add_argument("--raw", required=True, type=Path)
    audit.add_argument("--candidate-freeze", required=True, type=Path)
    audit.add_argument("--manifest", required=True, type=Path)
    audit.add_argument("--failure-message", required=True)
    audit.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "self-test":
            result = self_test()
        else:
            result = verify(
                args.marker, args.raw, args.candidate_freeze,
                args.manifest, args.failure_message, args.output,
            )
    except (
        AuditError, KeyError, ValueError, TypeError, OverflowError,
        RecursionError, UnicodeError, json.JSONDecodeError,
    ) as error:
        print(json.dumps({
            "schema": SCHEMA,
            "result": "AUDIT_FAILED",
            "auditor_result": "FAIL",
            "retry_permitted": False,
            "auditor_timing_performed": False,
            "error": str(error),
            "failed": 1,
        }, sort_keys=True))
        raise SystemExit(1) from error
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
