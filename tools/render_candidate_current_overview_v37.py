#!/usr/bin/env python3
"""Show the actual falsified Python reference before testing any candidate."""

from __future__ import annotations

import argparse
import builtins
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import types
import zlib


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SELF = "tools/render_candidate_current_overview_v37.py"
OUTPUT = "docs/evidence/candidate-current-overview-v37"
SCHEMA = "rebar-candidate-current-overview-v37"
LIMIT = 8 * 1024 * 1024
VECTOR_SHA = "b32f2ea83213686a8b97d63a15ba5c83d323c2dee1f831bab41176544d6adb0a"
FALSIFICATION = (
    "oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json",
    "319f0f75aaaea16fd1f41d814785d67060c57060852893349366cc3b482c4670",
    3892,
)
CASE_IDS_SHA = "df43bd52adb112c0fde2bfe24a45200ca2ac30a9c41dfdc5716e3e81cbe19ce0"
CASE_MATRIX_SHA = "09b5d7cb665af227b8d6c733c795d68f9a1e22c62956b9d64105a9234af6abca"
SCRIPT_VECTOR_SHA = "df849727d5aa74cbec19950c2d56764bd592404b76c49abe87418bccd3a5013a"
ACTUAL_VECTOR_SHA = "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
FIRST_SCRIPT_SHA = "33d63c67211bba811706bef2457230573cd13b498642c5ba0fa27b2e5091688c"
FIRST_ACTUAL_SHA = "7d8752048b7a3520b2657a21c3fe03722a507e0914d777404f16ffeec60d2292"
PUBLIC_TYPES_MATRIX_SHA = "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123"
V36 = {
    "source": (
        "tools/render_candidate_current_overview_v36.py",
        "1163df648d3fc3fb6b8f07abe260955958ea3b19826fafd09ee20b6fd5ba0cb1",
        94469,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v36.inputs.json",
        "0b5587a1b9790ee33ca00f6234efe162a79019618334b2726e2b239a425c230c",
        148736,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v36.json",
        "a082592fbb9aa29e9c577aac32c5f4b9db0e2bd503e149df0f1a39ee44b0cad6",
        463741,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v36.svg",
        "a94a73b62ac356acf54bcf3e066857b2160176d7f63c0cd44597641d1739d764",
        10021,
    ),
}
DECLARED_SOURCES = {
    "candidate_suite_gate": (
        "tools/run_frozen_p0_candidate_v1.py",
        "c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8",
    ),
    "public_type_observer": (
        "tools/independent_public_type_identity_serialization_v1.py",
        "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20",
    ),
    "candidate_case_producer": (
        "tools/run_owned_six_family_original_p0_producer_v3.py",
        "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
    ),
    "original_public_reference_archive": (
        "experiments/rust_public_practice_v1/"
        "public-type-identity-serialization-v1-shared-suite-v1.json.gz",
        "8956c0b26e074d1537a47047062fb51e11d3f0196dc97ce4a6e24d2ae45128e2",
    ),
    "original_public_reference_receipt": (
        "experiments/rust_public_practice_v1/"
        "public-type-identity-serialization-v1-shared-suite-v1-publication-receipt.json",
        "6a8ce4334d0b605483e0f78a909f620a8bcdd0e5ad8cdb4fae4960fc237132fd",
    ),
}


class GraphError(Exception):
    """Reject misleading reference, candidate, speed or holdout claims."""


def need(condition: object, explanation: str) -> None:
    if condition is not True:
        raise GraphError(explanation)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only exact independently owned bytes")
    return hashlib.sha256(raw).hexdigest()


def checked(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(character in "0123456789abcdef" for character in value),
         "require the exact independently supplied SHA-256 for " + label)
    return value


def canonical(value: object) -> bytes:
    try:
        return (
            json.dumps(value, ensure_ascii=True, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise GraphError("reject noncanonical V37 evidence") from error


def document(raw: bytes, label: str, *, exact: bool = True) -> dict:
    def unique(pairs: list[tuple[str, object]]) -> dict:
        found: dict[str, object] = {}
        for key, value in pairs:
            need(key not in found, "reject a duplicate JSON key in " + label)
            found[key] = value
        return found

    try:
        result = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                GraphError("reject nonfinite JSON in " + label)
            ),
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GraphError("reject incomplete or malformed " + label) from error
    need(type(result) is dict and (not exact or canonical(result) == raw),
         "authenticate the entire exact " + label)
    return result


def runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
         and os.path.realpath(sys.executable) == PYTHON,
         "require the exact stable isolated CPython 3.14.6 oracle")


def pin(path: str, fingerprint: str, size: int) -> dict:
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT,
         "bound the exact " + path + " evidence owner")
    return {"path": path, "sha256": fingerprint, "bytes": size}


def read_owner(path: str, fingerprint: str, size: int,
               *, private: bool = False) -> tuple[bytes, dict]:
    need(type(path) is str and bool(path) and not path.startswith("/")
         and "." not in Path(path).parts and ".." not in Path(path).parts,
         "reject an escaped, absolute or substituted evidence owner")
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT,
         "reject an unbounded evidence owner " + path)
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    file_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                  | getattr(os, "O_NOFOLLOW", 0))
    directories: list[int] = []
    handle: int | None = None
    try:
        directories.append(os.open(str(ROOT), directory_flags))
        for part in Path(path).parts[:-1]:
            directories.append(os.open(part, directory_flags,
                                       dir_fd=directories[-1]))
        handle = os.open(Path(path).parts[-1], file_flags,
                         dir_fd=directories[-1])
        before = os.fstat(handle)
        need(stat.S_ISREG(before.st_mode)
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and before.st_size == size
             and (not private or stat.S_IMODE(before.st_mode) == 0o600),
             "reject a substituted, nonprivate or linked owner " + path)
        chunks: list[bytes] = []
        remaining = size
        while remaining:
            part = os.read(handle, min(remaining, 1024 * 1024))
            need(bool(part), "reject truncated frozen evidence " + path)
            chunks.append(part)
            remaining -= len(part)
        need(os.read(handle, 1) == b"", "reject extra owner bytes " + path)
        raw = b"".join(chunks)
        after = os.fstat(handle)
        need((before.st_dev, before.st_ino, before.st_size, before.st_nlink,
              before.st_mtime_ns, before.st_ctime_ns)
             == (after.st_dev, after.st_ino, after.st_size, after.st_nlink,
                 after.st_mtime_ns, after.st_ctime_ns)
             and digest(raw) == fingerprint,
             "reject evidence changed during authentication " + path)
        return raw, {
            "path": path, "sha256": fingerprint, "bytes": size,
            "device": after.st_dev, "inode": after.st_ino,
            "mode": f"{stat.S_IMODE(after.st_mode):04o}",
            "nlink": after.st_nlink, "uid": after.st_uid,
        }
    finally:
        if handle is not None:
            os.close(handle)
        for directory in reversed(directories):
            os.close(directory)


def authenticate_v36() -> tuple[dict, dict]:
    source_raw, _ = read_owner(*V36["source"])
    old = types.ModuleType("_rebar_exact_v36_before_reference_falsification")
    old.__file__ = str(ROOT / V36["source"][0])
    old.__package__ = ""
    exec(compile(source_raw, old.__file__, "exec", dont_inherit=True),
         old.__dict__)
    need(old.SCHEMA == "rebar-candidate-current-overview-v36"
         and old.SELF == V36["source"][0],
         "load only the immutable published V36 graph renderer")
    inputs_raw, _ = read_owner(*V36["inputs"], private=True)
    summary_raw, _ = read_owner(*V36["summary"], private=True)
    svg_raw, _ = read_owner(*V36["svg"], private=True)
    inputs = document(inputs_raw, "immutable published V36 inputs")
    previous = document(summary_raw, "immutable published V36 summary")
    snapshot = previous.get("snapshot")
    need(type(snapshot) is dict, "preserve the entire genuine V36 snapshot")
    old.validate(snapshot)
    need(
        previous.get("schema") == old.SCHEMA + "-summary"
        and previous.get("version") == 36
        and previous.get("status") == "PASS"
        and svg_raw == old.make_svg(snapshot, V36["source"][1],
                                   V36["inputs"][1])
        and previous.get("full_case_denominator") == 31237
        and previous.get("suite_count") == 13
        and previous.get("private_waiver_count") == 13
        and previous.get("qualified_candidate_count") == 0
        and previous.get("authenticated_evidence_owner_lower_bound") == 161
        and previous.get("authenticated_history_reference_lower_bound") == 166
        and previous.get("rust_original_campaign_semantic_mismatch_count") == 1036
        and previous.get("rust_original_campaign_verified_passing_case_count") == 8965
        and previous.get("c_original_campaign_semantic_mismatch_count") == 1230
        and previous.get("c_original_campaign_verified_passing_case_count") == 7325
        and previous.get("zig_original_campaign_semantic_mismatch_count") == 1764
        and previous.get("zig_original_campaign_verified_passing_case_count") == 3711
        and previous.get("rust_v13_source_build_status") == "PASS"
        and previous.get("rust_v13_source_build_process_count") == 28
        and previous.get("rust_v13_independent_phase_count") == 2
        and previous.get("rust_v13_matching_test_status") == "NOT RUN"
        and previous.get("additional_signature_reference_status") == "PASS"
        and previous.get("additional_signature_reference_cases_executed") == 50
        and previous.get("additional_signature_reference_process_count") == 2
        and previous.get("additional_signature_reference_process_ids") == [81, 82]
        and previous.get("additional_signature_record_vector_sha256") == VECTOR_SHA
        and previous.get("additional_signature_candidate_status") == "NOT RUN"
        and previous.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and previous.get("performance") == "NOT MEASURED"
        and previous.get("memory") == "NOT MEASURED"
        and previous.get("final_holdout_opened") is False
        and inputs.get("authenticated_evidence_owner_lower_bound") == 161
        and inputs.get("authenticated_history_reference_lower_bound") == 166,
        "preserve all genuine histories, 50 references, and the unopened holdout",
    )
    return previous, inputs


def validate_falsification_record(record: object) -> None:
    need(type(record) is dict
         and record.get("schema")
         == "rebar-public-type-candidate-context-falsification-v1"
         and record.get("version") == 1
         and record.get("status") == "FALSIFIED"
         and record.get("candidate_facing_self_oracle_status") == "FAIL",
         "reject an invented or hidden candidate-facing reference falsification")
    actual = record.get("actual_replay")
    need(type(actual) is dict
         and actual.get("python_version") == "3.14.6"
         and actual.get("python_sha256") == PYTHON_SHA
         and type(actual.get("isolated_python_process_id")) is int
         and actual["isolated_python_process_id"] > 0
         and actual.get("candidate_import_count") == 0
         and actual.get("candidate_workers_started") == 0
         and actual.get("reference_subprocesses_started") == 0
         and actual.get("matching_archives_opened") == 0
         and actual.get("holdout_opened") is False,
         "require the real independently isolated Python-only replay")
    cases = record.get("falsifying_cases")
    need(type(cases) is dict
         and cases.get("cohort") == "cache-pattern-type-separation"
         and cases.get("case_count") == 96
         and cases.get("text_subclass_case_count") == 48
         and cases.get("bytes_subclass_case_count") == 48
         and cases.get("first_case") == "cache-pattern-type-separation/000"
         and cases.get("last_case") == "cache-pattern-type-separation/095"
         and cases.get("case_ids_sha256") == CASE_IDS_SHA
         and cases.get("exact_case_matrix_sha256") == CASE_MATRIX_SHA
         and cases.get("published_script_context_records_sha256")
         == SCRIPT_VECTOR_SHA
         and cases.get("actual_named_context_stdlib_records_sha256")
         == ACTUAL_VECTOR_SHA
         and cases.get("first_script_context_record_sha256") == FIRST_SCRIPT_SHA
         and cases.get("first_named_context_stdlib_record_sha256") == FIRST_ACTUAL_SHA
         and cases.get("sole_normalized_difference_path")
         == "outcome.value.items[2].module"
         and cases.get("published_script_context_module") == "__main__"
         and cases.get("actual_candidate_facing_module")
         == "tools.independent_public_type_identity_serialization_v1",
         "retain every one of 96 exact text/bytes module-context falsifiers")
    original = record.get("original_oracle")
    need(type(original) is dict
         and original.get("case_execution_denominator") == 31237
         and original.get("suite_count") == 13
         and original.get("named_private_waiver_count") == 13
         and original.get("affected_suite") == "public_types_v1"
         and original.get("affected_suite_case_count") == 6912
         and original.get("matrix_sha256") == PUBLIC_TYPES_MATRIX_SHA
         and original.get("published_seed_decimal") == "6077977430793212465"
         and original.get("original_cases_removed") == 0
         and original.get("additional_private_waivers") == 0
         and original.get("case_denominator_changed") is False,
         "never remove, waive, reseed or quietly change the original denominator")
    outcome = record.get("interpretation")
    need(type(outcome) is dict
         and outcome.get("candidate_facing_python_against_python_agrees") is False
         and outcome.get("historical_rust_records_recomputed_or_deleted") is False
         and outcome.get("c_pattern_equality_failure_waived") is False
         and outcome.get("zig_pattern_equality_failure_waived") is False
         and outcome.get("all_candidate_matching_blocked") is True
         and outcome.get("same_context_reference_correction_status") == "NOT RUN"
         and outcome.get("separate_50_case_reference_status") == "PASS"
         and outcome.get("separate_50_case_candidate_status") == "NOT RUN"
         and outcome.get("runtime_no_delegation") == "NOT ESTABLISHED"
         and outcome.get("performance") == "NOT MEASURED"
         and outcome.get("memory") == "NOT MEASURED"
         and outcome.get("final_holdout_opened") is False
         and outcome.get("winner_selected") is False,
         "pause every candidate run; never waive genuine C or Zig failures")
    declared = record.get("immutable_sources")
    need(type(declared) is dict and set(declared) == set(DECLARED_SOURCES),
         "preserve all declared prior source and unopened archive references")
    for name, (path, fingerprint) in DECLARED_SOURCES.items():
        reference = declared.get(name)
        need(type(reference) is dict and reference.get("path") == path
             and reference.get("sha256") == fingerprint,
             "preserve the falsification-declared owner without opening " + name)
    need(declared["original_public_reference_archive"]
         .get("opened_by_replay") is False,
         "never open or inflate the historical reference archive")


def authenticate_falsification(fingerprint: str) -> dict:
    checked(fingerprint, "actual Python reference falsification")
    need(fingerprint == FALSIFICATION[1],
         "accept only the independently supplied actual phase-one falsification")
    raw, owner = read_owner(*FALSIFICATION, private=True)
    record = document(raw, "complete real Python-only falsification", exact=False)
    validate_falsification_record(record)
    proof = {
        "schema": SCHEMA + "-authenticated-reference-context-falsification",
        "status": "FALSIFIED",
        "candidate_facing_self_oracle_status": "FAIL",
        "evidence": owner,
        "complete_falsification_record": copy.deepcopy(record),
        "falsifying_case_count": 96,
        "text_subclass_case_count": 48,
        "bytes_subclass_case_count": 48,
        "published_script_context_records_sha256": SCRIPT_VECTOR_SHA,
        "actual_candidate_facing_reference_records_sha256": ACTUAL_VECTOR_SHA,
        "affected_original_suite": "public_types_v1",
        "affected_original_suite_case_count": 6912,
        "full_original_case_execution_denominator": 31237,
        "original_private_waiver_count": 13,
        "original_cases_removed": 0,
        "additional_private_waivers": 0,
        "case_denominator_changed": False,
        "all_candidate_matching_blocked": True,
        "same_context_reference_correction_status": "NOT RUN",
        "c_pattern_equality_failure_waived": False,
        "zig_pattern_equality_failure_waived": False,
        "new_distinct_reference_evidence_owner_count": 1,
        "preserved_v36_evidence_owner_lower_bound": 161,
        "preserved_v36_history_reference_lower_bound": 166,
        "authenticated_evidence_owner_lower_bound": 162,
        "authenticated_history_reference_lower_bound": 167,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "candidate_workers_started_by_graph": 0,
        "reference_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "candidate_matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    proof["falsification_record_binding_sha256"] = digest(canonical({
        "evidence": owner, "record": record,
    }))
    return proof


def validate(snapshot: object) -> None:
    need(type(snapshot) is dict
         and snapshot.get("full_case_denominator") == 31237
         and snapshot.get("suite_count") == 13
         and snapshot.get("private_waiver_count") == 13
         and snapshot.get("frozen_independent_engine_family_count") == 6
         and snapshot.get("qualified_candidate_count") == 0
         and snapshot.get("preserved_v36_evidence_owner_lower_bound") == 161
         and snapshot.get("preserved_v36_history_reference_lower_bound") == 166
         and snapshot.get("new_reference_falsification_evidence_owner_count") == 1
         and snapshot.get("authenticated_evidence_owner_lower_bound") == 162
         and snapshot.get("authenticated_history_reference_lower_bound") == 167
         and snapshot.get("evidence_owner_count_is_authenticated_lower_bound") is True
         and snapshot.get("history_reference_count_is_authenticated_lower_bound") is True
         and snapshot.get("exact_whole_repository_evidence_owner_count") == "NOT MEASURED"
         and snapshot.get("exact_whole_repository_reference_count") == "NOT MEASURED",
         "preserve the 31,237-case denominator and honest ≥162/≥167 lower bounds")
    for name, mismatches, passes in (
        ("rust_v4_original_campaign", 1036, 8965),
        ("rust_v3_original_campaign", 1087, 7438),
        ("c_v4_original_campaign", 1230, 7325),
        ("zig_v2_original_campaign", 2172, 2847),
        ("zig_v3_original_campaign", 1764, 3711),
    ):
        previous = snapshot.get(name)
        need(type(previous) is dict and previous.get("status") == "FAIL"
             and previous.get("actual_candidate_workers") == 13
             and previous.get("completed_suite_count") == 13
             and previous.get("semantic_mismatch_count") == mismatches
             and previous.get("verified_passing_case_count") == passes
             and previous.get("infrastructure_failure_count") == 0
             and previous.get("candidate_qualified") is False,
             "never hide or recompute the historical actual loss " + name)
    actual = snapshot.get("reference_context_falsification")
    need(type(actual) is dict
         and actual.get("schema")
         == SCHEMA + "-authenticated-reference-context-falsification"
         and actual.get("status") == "FALSIFIED"
         and actual.get("candidate_facing_self_oracle_status") == "FAIL"
         and actual.get("falsifying_case_count") == 96
         and actual.get("text_subclass_case_count") == 48
         and actual.get("bytes_subclass_case_count") == 48
         and actual.get("published_script_context_records_sha256")
         == SCRIPT_VECTOR_SHA
         and actual.get("actual_candidate_facing_reference_records_sha256")
         == ACTUAL_VECTOR_SHA
         and actual.get("affected_original_suite") == "public_types_v1"
         and actual.get("affected_original_suite_case_count") == 6912
         and actual.get("full_original_case_execution_denominator") == 31237
         and actual.get("original_private_waiver_count") == 13
         and actual.get("original_cases_removed") == 0
         and actual.get("additional_private_waivers") == 0
         and actual.get("case_denominator_changed") is False
         and actual.get("all_candidate_matching_blocked") is True
         and actual.get("same_context_reference_correction_status") == "NOT RUN"
         and actual.get("c_pattern_equality_failure_waived") is False
         and actual.get("zig_pattern_equality_failure_waived") is False,
         "show all 96 self-reference errors and keep every candidate run paused")
    owner = actual.get("evidence")
    need(type(owner) is dict and owner.get("path") == FALSIFICATION[0]
         and owner.get("sha256") == FALSIFICATION[1]
         and owner.get("bytes") == FALSIFICATION[2]
         and type(owner.get("device")) is int
         and type(owner.get("inode")) is int and owner["inode"] > 0
         and owner.get("mode") == "0600" and owner.get("nlink") == 1
         and owner.get("uid") == os.geteuid(),
         "require the genuinely private actual Python falsification owner")
    recorded = actual.get("complete_falsification_record")
    validate_falsification_record(recorded)
    need(checked(actual.get("falsification_record_binding_sha256"),
                 "complete authentic reference falsification")
         == digest(canonical({"evidence": owner, "record": recorded})),
         "reject substituted genuine reference evidence or changed diagnostics")
    need(
        actual.get("new_distinct_reference_evidence_owner_count") == 1
        and actual.get("preserved_v36_evidence_owner_lower_bound") == 161
        and actual.get("preserved_v36_history_reference_lower_bound") == 166
        and actual.get("authenticated_evidence_owner_lower_bound") == 162
        and actual.get("authenticated_history_reference_lower_bound") == 167
        and actual.get("evidence_owner_count_is_authenticated_lower_bound") is True
        and actual.get("history_reference_count_is_authenticated_lower_bound") is True
        and actual.get("exact_whole_repository_evidence_owner_count") == "NOT MEASURED"
        and actual.get("exact_whole_repository_reference_count") == "NOT MEASURED"
        and actual.get("candidate_workers_started_by_graph") == 0
        and actual.get("reference_workers_started_by_graph") == 0
        and actual.get("compiler_processes_started_by_graph") == 0
        and actual.get("candidate_matching_archives_opened_by_graph") == 0
        and actual.get("candidate_matching_archive_gzip_inflation_count") == 0
        and actual.get("reference_archive_gzip_inflation_count") == 0
        and actual.get("canonical_target_reads") == 0
        and actual.get("canonical_target_stats") == 0
        and actual.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and actual.get("production_runtime_delegation_audit") == "NOT ESTABLISHED"
        and actual.get("hidden_cases_read") == 0
        and actual.get("clock_samples") == 0
        and actual.get("timing_trials_run") == 0
        and actual.get("performance") == "NOT MEASURED"
        and actual.get("memory") == "NOT MEASURED"
        and actual.get("confidence_intervals") == "NOT MEASURED"
        and actual.get("undefined_behavior") == "NOT MEASURED"
        and actual.get("holdout") == "NOT OPENED"
        and actual.get("winner_selected") is False,
        "never touch reference archives, candidates, clocks or the holdout")
    need(
        snapshot.get("phase_one_reference_gate_status") == "FALSIFIED"
        and snapshot.get("candidate_facing_self_oracle_status") == "FAIL"
        and snapshot.get("reference_context_falsifying_case_count") == 96
        and snapshot.get("reference_context_text_case_count") == 48
        and snapshot.get("reference_context_bytes_case_count") == 48
        and snapshot.get("all_candidate_matching_blocked") is True
        and snapshot.get("same_context_reference_correction_status") == "NOT RUN"
        and snapshot.get("additional_private_waivers") == 0
        and snapshot.get("original_cases_removed") == 0
        and snapshot.get("case_denominator_changed") is False
        and snapshot.get("c_pattern_equality_failure_waived") is False
        and snapshot.get("zig_pattern_equality_failure_waived") is False
        and snapshot.get("rust_v13_source_build_status") == "PASS"
        and snapshot.get("rust_v13_source_build_process_count") == 28
        and snapshot.get("rust_v13_independent_phase_count") == 2
        and snapshot.get("rust_v13_matching_test_status") == "NOT RUN"
        and snapshot.get("rust_v13_candidate_worker_count") == 0
        and snapshot.get("additional_signature_frozen_case_count") == 50
        and snapshot.get("additional_signature_reference_status") == "PASS"
        and snapshot.get("additional_signature_reference_cases_executed") == 50
        and snapshot.get("additional_signature_reference_process_count") == 2
        and snapshot.get("additional_signature_reference_process_ids") == [81, 82]
        and snapshot.get("additional_signature_record_vector_sha256") == VECTOR_SHA
        and snapshot.get("additional_signature_candidate_status") == "NOT RUN"
        and snapshot.get("additional_signature_candidate_cases_executed") == 0
        and snapshot.get("additional_cases_included_in_original_denominator") is False,
        "distinguish the blocked original gate from 50 genuine passing extra checks")
    need(
        snapshot.get("native_source_build_independence") == "VERIFIED"
        and snapshot.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and snapshot.get("production_runtime_delegation_audit") == "NOT ESTABLISHED"
        and snapshot.get("candidate_matching_archives_opened_by_graph") == 0
        and snapshot.get("matching_archive_gzip_inflation_count") == 0
        and snapshot.get("reference_archive_gzip_inflation_count") == 0
        and snapshot.get("actual_candidate_workers_started_by_graph") == 0
        and snapshot.get("actual_reference_workers_started_by_graph") == 0
        and snapshot.get("actual_compiler_processes_started_by_graph") == 0
        and snapshot.get("canonical_target_reads") == 0
        and snapshot.get("canonical_target_stats") == 0
        and snapshot.get("hidden_cases_read") == 0
        and snapshot.get("performance_files_read") == 0
        and snapshot.get("clock_samples") == 0
        and snapshot.get("timing_trials_run") == 0
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("confidence_intervals") == "NOT MEASURED"
        and snapshot.get("undefined_behavior") == "NOT MEASURED"
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("winner_selected") is False,
        "prohibit all current testing, false speed claims and holdout access")


def xml(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;")
            .replace("'", "&apos;"))


def make_svg(snapshot: dict, source: str, inputs: str) -> bytes:
    validate(snapshot)
    checked(source, "actual V37 renderer")
    checked(inputs, "actual V37 graph inputs")
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1855" '
        'viewBox="0 0 1440 1855" role="img" '
        'aria-labelledby="v37-title v37-description">',
        '<title id="v37-title">Building a faster Python re: Python '
        'reference falsified; all candidate runs paused</title>',
        '<desc id="v37-description">An actual isolated Python-only replay '
        'falsified all 96 affected original public-type reference records: '
        '48 text cases and 48 byte cases. The expected records ran as '
        '__main__, while candidate-facing Python uses the actual imported '
        'module name. All candidate matching must pause until the reference '
        'is repaired. No original case was removed, no waiver added, and the '
        '13-suite denominator remains 31,237. Historical Rust has 1,036 '
        'differences, C has 1,230, and Zig has 1,764; they are not new '
        'measurements. The corrected Rust build was reproduced twice but '
        'matching has not run. Fifty separate Python signature references '
        'still pass. Speed and memory are not measured and the 4,194,304-case '
        'holdout is unopened.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,'
        '"Segoe UI",sans-serif}.title{font-size:27px;font-weight:760;fill:'
        '#16324f}.heading{font-size:19px;font-weight:750;fill:#16324f}'
        '.body{font-size:14px;fill:#42556c}.name{font-size:14px;font-weight:'
        '720;fill:#16324f}.danger{font-size:18px;font-weight:780;fill:'
        '#a31f2d}.dangerbody{font-size:14px;fill:#7d2631}.pass{font-size:'
        '12px;font-weight:760;fill:#00794c}.fail{font-size:12px;font-weight:'
        '750;fill:#a75c13}.pending{font-size:12px;font-weight:740;fill:'
        '#53667b}.big{font-size:20px;font-weight:760;fill:#16324f}.small'
        '{font-size:11px;fill:#42556c}.foot{font-size:10px;fill:#53667b}'
        '</style>',
        '<rect width="1440" height="1855" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="54" class="title">Can we build a faster '
        'replacement for Python re?</text>',
        '<text x="46" y="81" class="body">First, Python must agree with '
        'itself in the exact context used to test the replacements.</text>',
        '<rect x="44" y="100" width="1352" height="108" rx="14" '
        'fill="#fff1f2" stroke="#efbec5"/>',
        '<text x="65" y="139" class="danger">REFERENCE CONTEXT '
        'FALSIFIED — 96 / 96; ALL CANDIDATE RUNS PAUSED</text>',
        '<text x="67" y="168" class="dangerbody">The existing Python '
        'reference used __main__; candidates see the imported module. '
        'Fix and re-verify the reference before running any candidate.</text>',
        '<text x="67" y="191" class="dangerbody">No cases removed. '
        'No added exceptions. No genuine C or Zig pattern-equality '
        'failure waived.</text>',
    ]
    cards = (
        ("31,237", "unchanged original cases"),
        ("96 / 96", "reference cases falsified"),
        ("48 + 48", "text and byte cases"),
        ("50 / 50", "separate Python checks pass"),
        ("28", "historical Rust build roles"),
        ("0", "new candidate runs"),
        ("≥162 / 167", "authenticated lower bounds"),
    )
    for index, (number, label) in enumerate(cards):
        left = 44 + index * 195
        lines.extend((
            f'<rect x="{left}" y="226" width="184" height="82" rx="11" '
            'fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{left + 9}" y="259" class="big">{xml(number)}</text>',
            f'<text x="{left + 9}" y="284" class="small">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="327" width="1352" height="439" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="362" class="heading">1. Overall: testing is '
        'paused until Python agrees with itself</text>',
        '<text x="66" y="388" class="body">Candidate bars are preserved '
        'historical results, not results under the corrected reference. '
        'No candidate has been rerun.</text>',
    ))
    rows = (
        ("Python reference — candidate-facing context", "FALSIFIED; RUNS PAUSED", 96, 0, "danger"),
        ("Rust — previously tested version", "HISTORICAL FAILURE", 1036, 8965, "fail"),
        ("C — previously tested version", "HISTORICAL FAILURE", 1230, 7325, "fail"),
        ("Zig — previously tested version", "HISTORICAL FAILURE", 1764, 3711, "fail"),
    )
    for index, (name, state, differences, passes, kind) in enumerate(rows):
        top = 415 + index * 62
        width = round(560 * differences / 1764)
        color = "#c73545" if index == 0 else "#b77a36"
        note = (f"{differences:,} of 96 self-reference cases disagree"
                if index == 0 else
                f"{differences:,} historical differences; {passes:,} historical passes")
        lines.extend((
            f'<text x="67" y="{top + 15}" class="name">{xml(name)}</text>',
            f'<text x="1368" y="{top + 15}" class="{kind}" '
            f'text-anchor="end">{xml(state)}</text>',
            f'<rect x="68" y="{top + 27}" width="560" height="10" '
            'rx="5" fill="#edf1f5"/>',
            f'<rect x="68" y="{top + 27}" width="{width}" height="10" '
            f'rx="5" fill="{color}"/>',
            f'<text x="645" y="{top + 37}" class="small">{xml(note)}</text>',
        ))
    lines.extend((
        '<rect x="67" y="690" width="1304" height="56" rx="10" '
        'fill="#f3f6fb" stroke="#dae4ee"/>',
        '<text x="83" y="714" class="name">Rust — corrected first-party '
        'engine independently built twice</text>',
        '<text x="1355" y="714" class="pending" text-anchor="end">'
        'MATCHING NOT RUN; BLOCKED</text>',
        '<text x="84" y="735" class="small">28 real historical build '
        'processes establish reproducibility, not compatibility.</text>',
        '<rect x="44" y="785" width="1352" height="276" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="820" class="heading">2. What exactly was '
        'falsified</text>',
    ))
    findings = (
        "One isolated, pinned CPython 3.14.6 process replayed all 96 original cache-pattern-type cases.",
        "The cases divide evenly: 48 text subclasses and 48 byte subclasses.",
        "The existing reference records identify the observing module as __main__.",
        "The actual candidate-facing Python reference identifies its real imported observer module.",
        "The sole normalized difference is outcome.value.items[2].module.",
        "Fix the reference context itself; never discard cases or turn genuine C and Zig failures into waivers.",
        "The separate 50 signature-reference cases still PASS; their candidate checks have NOT RUN.",
    )
    for index, line in enumerate(findings):
        lines.append(f'<text x="67" y="{851 + 26 * index}" class="body">'
                     f'{xml(line)}</text>')
    lines.extend((
        '<rect x="44" y="1080" width="1352" height="247" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1115" class="heading">3. What remains '
        'blocked or unmeasured</text>',
    ))
    remaining = (
        ("Corrected reference", "NOT RUN: Python must first pass the same candidate-facing context."),
        ("Every candidate matching run", "PAUSED: no Rust, C, Zig, Go, C++, or Fortran rerun is permitted."),
        ("Runtime independence", "NOT ESTABLISHED; source and native-build checks are not a runtime proof."),
        ("Speed, memory and confidence", "NOT MEASURED; no honest comparative timing is possible."),
        ("4,194,304-case final holdout", "NOT OPENED and NOT GENERATED; no hidden cases were accessed."),
        ("Winning replacement", "NONE: reference correctness and candidate correctness must come first."),
    )
    for index, (name, line) in enumerate(remaining):
        top = 1147 + 27 * index
        lines.extend((
            f'<text x="68" y="{top}" class="name">{xml(name)}</text>',
            f'<text x="350" y="{top}" class="body">{xml(line)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="1346" width="1352" height="321" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1381" class="heading">4. Independently '
        'reproducible evidence</text>',
    ))
    notes = (
        "Authenticate the immutable preceding V36 graph and replay it exactly without running a candidate.",
        "Read only the one complete, private 3,892-byte Python-only falsification record.",
        "Preserve all original 31,237 cases, all 13 groups, and exactly the existing 13 named private waivers.",
        "Preserve all historical Rust, C, and Zig losses; do not silently retest or rewrite them.",
        "Preserve the two independently recorded Python signature-reference processes and all 50 passing cases.",
        "The one new genuine evidence owner raises authenticated lower bounds from 161/166 to at least 162/167.",
        "A full repository-wide evidence or reference count remains NOT MEASURED.",
        "The graph opens no compressed archive and starts no candidate, compiler, reference, timer or benchmark.",
        "Correct the same-context Python self-oracle before authorizing or announcing any new candidate result.",
    )
    for index, line in enumerate(notes):
        lines.append(f'<text x="67" y="{1411 + 25 * index}" class="body">'
                     f'{xml(line)}</text>')
    lines.extend((
        f'<text x="47" y="1700" class="foot">Graph inputs SHA-256: '
        f'{xml(inputs)}</text>',
        f'<text x="47" y="1722" class="foot">Graph renderer SHA-256: '
        f'{xml(source)}</text>',
        f'<text x="47" y="1744" class="foot">Actual Python-only '
        f'falsification SHA-256: {xml(FALSIFICATION[1])}</text>',
        f'<text x="47" y="1766" class="foot">Actual named-context '
        f'Python reference SHA-256: {xml(ACTUAL_VECTOR_SHA)}</text>',
        f'<text x="47" y="1788" class="foot">Previous script-context '
        f'reference SHA-256: {xml(SCRIPT_VECTOR_SHA)}</text>',
        '</svg>',
    ))
    return ("\n".join(lines) + "\n").encode("utf-8")


def build(source_sha: str, source_bytes: int,
          falsification_sha: str) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    source_sha = checked(source_sha, "actual V37 falsification graph renderer")
    need(type(source_bytes) is int and 0 < source_bytes <= LIMIT,
         "require the exact externally supplied V37 renderer size")
    own, _ = read_owner(SELF, source_sha, source_bytes)
    previous, old_inputs = authenticate_v36()
    proof = authenticate_falsification(falsification_sha)
    snapshot = copy.deepcopy(previous["snapshot"])
    snapshot.update({
        "private_waiver_count": 13,
        "preserved_v36_evidence_owner_lower_bound": 161,
        "preserved_v36_history_reference_lower_bound": 166,
        "new_reference_falsification_evidence_owner_count": 1,
        "all_actual_candidate_and_native_evidence_owner_count": 162,
        "all_digest_addressed_history_path_count": 167,
        "authenticated_evidence_owner_lower_bound": 162,
        "authenticated_history_reference_lower_bound": 167,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "reference_context_falsification": copy.deepcopy(proof),
        "phase_one_reference_gate_status": "FALSIFIED",
        "candidate_facing_self_oracle_status": "FAIL",
        "reference_context_falsifying_case_count": 96,
        "reference_context_text_case_count": 48,
        "reference_context_bytes_case_count": 48,
        "all_candidate_matching_blocked": True,
        "same_context_reference_correction_status": "NOT RUN",
        "additional_private_waivers": 0,
        "original_cases_removed": 0,
        "case_denominator_changed": False,
        "c_pattern_equality_failure_waived": False,
        "zig_pattern_equality_failure_waived": False,
        "candidate_matching_archives_opened_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "winner_selected": False,
    })
    validate(snapshot)
    earlier = {name: pin(*item) for name, item in V36.items()}
    inputs = copy.deepcopy(old_inputs)
    shared = {
        "preserved_v36_evidence_owner_lower_bound": 161,
        "preserved_v36_history_reference_lower_bound": 166,
        "new_reference_falsification_evidence_owner_count": 1,
        "repository_evidence_owner_count": 162,
        "authenticated_evidence_owner_lower_bound": 162,
        "authenticated_history_reference_lower_bound": 167,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "phase_one_reference_gate_status": "FALSIFIED",
        "candidate_facing_self_oracle_status": "FAIL",
        "reference_context_falsifying_case_count": 96,
        "reference_context_text_case_count": 48,
        "reference_context_bytes_case_count": 48,
        "published_script_context_records_sha256": SCRIPT_VECTOR_SHA,
        "actual_candidate_facing_reference_records_sha256": ACTUAL_VECTOR_SHA,
        "all_candidate_matching_blocked": True,
        "same_context_reference_correction_status": "NOT RUN",
        "additional_private_waivers": 0,
        "original_cases_removed": 0,
        "case_denominator_changed": False,
        "c_pattern_equality_failure_waived": False,
        "zig_pattern_equality_failure_waived": False,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 0,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }
    inputs.update({
        "schema": SCHEMA + "-inputs", "version": 37,
        "python": "3.14.6", "renderer": pin(SELF, source_sha, len(own)),
        "previous_overview": earlier,
        "actual_reference_context_falsification": copy.deepcopy(proof),
        "all_digest_addressed_history_path_count": 167,
        "candidate_qualified_count": 0,
        **shared,
    })
    inputs_raw = canonical(inputs)
    svg = make_svg(snapshot, source_sha, digest(inputs_raw))
    families = copy.deepcopy(previous["families"])
    for family in families:
        if family.get("family") != "python":
            family["matching_paused_for_reference_falsification"] = True
        if family.get("family") == "rust":
            family["v13_matching_test_status"] = "NOT RUN"
            family["v13_candidate_worker_count"] = 0
            family["qualified"] = False
    summary = copy.deepcopy(previous)
    summary.update({
        "schema": SCHEMA + "-summary", "version": 37,
        "status": "PASS", "python": "3.14.6",
        "source": pin(SELF, source_sha, len(own)),
        "inputs": pin(OUTPUT + ".inputs.json", digest(inputs_raw),
                      len(inputs_raw)),
        "svg": pin(OUTPUT + ".svg", digest(svg), len(svg)),
        "previous_overview": earlier,
        "snapshot": snapshot, "families": families,
        "actual_reference_context_falsification": copy.deepcopy(proof),
        "authenticated_digest_addressed_history_paths": 167,
        "qualified_candidate_count": 0,
        **shared,
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", inputs_raw),
        (OUTPUT + ".json", canonical(summary)),
        (OUTPUT + ".svg", svg),
    )


class Wall:
    """Physically deny all candidate, reference, clock and archive effects."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def __enter__(self) -> Wall:
        def forbid(name: str):
            def denied(*_args: object, **_kwargs: object) -> object:
                self.blocked += 1
                raise GraphError("V37 source-only effect blocked: " + name)
            return denied

        groups = (
            (builtins, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "unlink",
                  "remove", "rename", "replace", "mkdir", "makedirs",
                  "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "stat", "lstat", "mkdir", "unlink",
                    "rename", "replace", "resolve")),
            (subprocess, ("run", "Popen", "call", "check_call",
                          "check_output")),
            (socket, ("socket", "create_connection")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp")),
            (threading.Thread, ("start",)),
            (zlib, ("decompress", "decompressobj")),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "sleep")),
        )
        for owner, names in groups:
            for name in names:
                if hasattr(owner, name):
                    self.saved.append((owner, name, getattr(owner, name)))
                    setattr(owner, name, forbid(name))
        return self

    def __exit__(self, *_errors: object) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic_record() -> dict:
    return {
        "schema": "rebar-public-type-candidate-context-falsification-v1",
        "version": 1, "status": "FALSIFIED",
        "candidate_facing_self_oracle_status": "FAIL",
        "actual_replay": {
            "python_version": "3.14.6", "python_sha256": PYTHON_SHA,
            "isolated_python_process_id": 80, "candidate_import_count": 0,
            "candidate_workers_started": 0, "reference_subprocesses_started": 0,
            "matching_archives_opened": 0, "holdout_opened": False,
        },
        "falsifying_cases": {
            "cohort": "cache-pattern-type-separation", "case_count": 96,
            "text_subclass_case_count": 48, "bytes_subclass_case_count": 48,
            "first_case": "cache-pattern-type-separation/000",
            "last_case": "cache-pattern-type-separation/095",
            "case_ids_sha256": CASE_IDS_SHA,
            "exact_case_matrix_sha256": CASE_MATRIX_SHA,
            "published_script_context_records_sha256": SCRIPT_VECTOR_SHA,
            "actual_named_context_stdlib_records_sha256": ACTUAL_VECTOR_SHA,
            "first_script_context_record_sha256": FIRST_SCRIPT_SHA,
            "first_named_context_stdlib_record_sha256": FIRST_ACTUAL_SHA,
            "sole_normalized_difference_path": "outcome.value.items[2].module",
            "published_script_context_module": "__main__",
            "actual_candidate_facing_module":
            "tools.independent_public_type_identity_serialization_v1",
        },
        "original_oracle": {
            "case_execution_denominator": 31237, "suite_count": 13,
            "named_private_waiver_count": 13,
            "affected_suite": "public_types_v1",
            "affected_suite_case_count": 6912,
            "matrix_sha256": PUBLIC_TYPES_MATRIX_SHA,
            "published_seed_decimal": "6077977430793212465",
            "original_cases_removed": 0,
            "additional_private_waivers": 0,
            "case_denominator_changed": False,
        },
        "interpretation": {
            "candidate_facing_python_against_python_agrees": False,
            "historical_rust_records_recomputed_or_deleted": False,
            "c_pattern_equality_failure_waived": False,
            "zig_pattern_equality_failure_waived": False,
            "all_candidate_matching_blocked": True,
            "same_context_reference_correction_status": "NOT RUN",
            "separate_50_case_reference_status": "PASS",
            "separate_50_case_candidate_status": "NOT RUN",
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "final_holdout_opened": False, "winner_selected": False,
        },
        "immutable_sources": {
            name: {
                "path": path, "sha256": fingerprint,
                **({"opened_by_replay": False}
                   if name == "original_public_reference_archive" else {}),
            }
            for name, (path, fingerprint) in DECLARED_SOURCES.items()
        },
    }


def synthetic() -> dict:
    def historical(mismatches: int, passes: int) -> dict:
        return {
            "status": "FAIL", "actual_candidate_workers": 13,
            "completed_suite_count": 13,
            "semantic_mismatch_count": mismatches,
            "verified_passing_case_count": passes,
            "infrastructure_failure_count": 0, "candidate_qualified": False,
        }

    owner = {
        "path": FALSIFICATION[0], "sha256": FALSIFICATION[1],
        "bytes": FALSIFICATION[2], "device": 2064, "inode": 524739,
        "mode": "0600", "nlink": 1, "uid": os.geteuid(),
    }
    record = synthetic_record()
    proof = {
        "schema": SCHEMA + "-authenticated-reference-context-falsification",
        "status": "FALSIFIED", "candidate_facing_self_oracle_status": "FAIL",
        "evidence": owner, "complete_falsification_record": record,
        "falsifying_case_count": 96, "text_subclass_case_count": 48,
        "bytes_subclass_case_count": 48,
        "published_script_context_records_sha256": SCRIPT_VECTOR_SHA,
        "actual_candidate_facing_reference_records_sha256": ACTUAL_VECTOR_SHA,
        "affected_original_suite": "public_types_v1",
        "affected_original_suite_case_count": 6912,
        "full_original_case_execution_denominator": 31237,
        "original_private_waiver_count": 13,
        "original_cases_removed": 0, "additional_private_waivers": 0,
        "case_denominator_changed": False,
        "all_candidate_matching_blocked": True,
        "same_context_reference_correction_status": "NOT RUN",
        "c_pattern_equality_failure_waived": False,
        "zig_pattern_equality_failure_waived": False,
        "new_distinct_reference_evidence_owner_count": 1,
        "preserved_v36_evidence_owner_lower_bound": 161,
        "preserved_v36_history_reference_lower_bound": 166,
        "authenticated_evidence_owner_lower_bound": 162,
        "authenticated_history_reference_lower_bound": 167,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "candidate_workers_started_by_graph": 0,
        "reference_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "candidate_matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    proof["falsification_record_binding_sha256"] = digest(canonical({
        "evidence": owner, "record": record,
    }))
    return {
        "full_case_denominator": 31237, "suite_count": 13,
        "private_waiver_count": 13,
        "frozen_independent_engine_family_count": 6,
        "qualified_candidate_count": 0,
        "preserved_v36_evidence_owner_lower_bound": 161,
        "preserved_v36_history_reference_lower_bound": 166,
        "new_reference_falsification_evidence_owner_count": 1,
        "authenticated_evidence_owner_lower_bound": 162,
        "authenticated_history_reference_lower_bound": 167,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "rust_v4_original_campaign": historical(1036, 8965),
        "rust_v3_original_campaign": historical(1087, 7438),
        "c_v4_original_campaign": historical(1230, 7325),
        "zig_v2_original_campaign": historical(2172, 2847),
        "zig_v3_original_campaign": historical(1764, 3711),
        "reference_context_falsification": proof,
        "phase_one_reference_gate_status": "FALSIFIED",
        "candidate_facing_self_oracle_status": "FAIL",
        "reference_context_falsifying_case_count": 96,
        "reference_context_text_case_count": 48,
        "reference_context_bytes_case_count": 48,
        "all_candidate_matching_blocked": True,
        "same_context_reference_correction_status": "NOT RUN",
        "additional_private_waivers": 0, "original_cases_removed": 0,
        "case_denominator_changed": False,
        "c_pattern_equality_failure_waived": False,
        "zig_pattern_equality_failure_waived": False,
        "rust_v13_source_build_status": "PASS",
        "rust_v13_source_build_process_count": 28,
        "rust_v13_independent_phase_count": 2,
        "rust_v13_matching_test_status": "NOT RUN",
        "rust_v13_candidate_worker_count": 0,
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_reference_process_count": 2,
        "additional_signature_reference_process_ids": [81, 82],
        "additional_signature_record_vector_sha256": VECTOR_SHA,
        "additional_signature_candidate_status": "NOT RUN",
        "additional_signature_candidate_cases_executed": 0,
        "additional_cases_included_in_original_denominator": False,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "candidate_matching_archives_opened_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "hidden_cases_read": 0, "performance_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }


def forged(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        if value == "FAIL":
            return "PASS"
        if value == "FALSIFIED":
            return "PASS"
        if value in ("NOT RUN", "NOT MEASURED", "NOT ESTABLISHED"):
            return "VERIFIED"
        return value + "-forged"
    if type(value) is dict:
        return {}
    if type(value) is list:
        return value[:-1]
    return "forged"


def self_test() -> dict:
    runtime()
    with Wall() as wall:
        fixture = synthetic()
        validate(fixture)
        rejected = 0

        def reject(candidate: dict, label: str) -> None:
            nonlocal rejected
            try:
                validate(candidate)
            except (GraphError, TypeError, ValueError, KeyError):
                rejected += 1
                return
            raise GraphError("accepted forged V37 self-reference evidence: " + label)

        groups = (
            "rust_v4_original_campaign", "rust_v3_original_campaign",
            "c_v4_original_campaign", "zig_v2_original_campaign",
            "zig_v3_original_campaign", "reference_context_falsification",
        )
        for key, value in fixture.items():
            if key not in groups:
                attack = copy.deepcopy(fixture)
                attack[key] = forged(value)
                reject(attack, "snapshot-" + key)
        for group in groups:
            for key, value in fixture[group].items():
                attack = copy.deepcopy(fixture)
                attack[group][key] = forged(value)
                reject(attack, group + "-" + key)
        evidence = fixture["reference_context_falsification"]
        for key, value in evidence["evidence"].items():
            attack = copy.deepcopy(fixture)
            attack["reference_context_falsification"]["evidence"][key] = forged(value)
            reject(attack, "actual-falsification-owner-" + key)
        for group in (
            "actual_replay", "falsifying_cases", "interpretation",
            "original_oracle", "immutable_sources",
        ):
            observed = evidence["complete_falsification_record"][group]
            for key, value in observed.items():
                attack = copy.deepcopy(fixture)
                attack["reference_context_falsification"]\
                    ["complete_falsification_record"][group][key] = forged(value)
                reject(attack, "falsification-" + group + "-" + key)
        image = make_svg(fixture, "a" * 64, "b" * 64)
        for phrase in (
            b"REFERENCE CONTEXT", b"FALSIFIED", b"96 / 96", b"PAUSED",
            b"31,237", b"48 + 48", b"50 / 50", b"1,036", b"8,965",
            b"1,230", b"7,325", b"1,764", b"3,711", b"HISTORICAL",
            b"__main__", b"module", b"NOT RUN", b"NOT ESTABLISHED",
            b"NOT MEASURED", b"lower bounds", b"4,194,304",
            b"NOT GENERATED", b"No cases removed", b"No added exceptions",
        ):
            need(phrase.lower() in image.lower(),
                 "reject a hidden or misleading reference falsification")
        effects = (
            lambda: builtins.open("forbidden-v37"),
            lambda: os.open("forbidden-v37", os.O_RDONLY),
            lambda: os.stat("forbidden-v37-native"),
            lambda: subprocess.run(("forbidden-v37",)),
            lambda: importlib.import_module("candidates.rust_candidate"),
            lambda: importlib.import_module("re"),
            lambda: socket.socket(), lambda: tempfile.mkdtemp(),
            lambda: zlib.decompressobj(), lambda: time.perf_counter(),
            lambda: threading.Thread(target=lambda: None).start(),
        )
        for effect in effects:
            try:
                effect()
            except GraphError:
                continue
            raise GraphError("source-only reference test caused a real effect")
        need(wall.blocked == len(effects) and rejected >= 130,
             "physically deny effects and reject forged reference controls")
        return {
            "schema": SCHEMA + "-source-only-self-test", "version": 37,
            "status": "PASS", "synthetic_only": True,
            "rejected_hostile_control_count": rejected,
            "blocked_effect_count": wall.blocked,
            "full_case_denominator": 31237, "suite_count": 13,
            "private_waiver_count": 13,
            "phase_one_reference_gate_status": "FALSIFIED",
            "candidate_facing_self_oracle_status": "FAIL",
            "reference_context_falsifying_case_count": 96,
            "all_candidate_matching_blocked": True,
            "same_context_reference_correction_status": "NOT RUN",
            "additional_private_waivers": 0,
            "original_cases_removed": 0,
            "case_denominator_changed": False,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "candidate_matching_archives_opened_by_graph": 0,
            "matching_archive_gzip_inflation_count": 0,
            "reference_archive_gzip_inflation_count": 0,
            "canonical_target_reads": 0, "canonical_target_stats": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "workspace_mutations": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False, "winner_selected": False,
        }


def publish(path: str, raw: bytes) -> None:
    allowed = {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
    need(path in allowed and type(raw) is bytes and 0 < len(raw) <= LIMIT,
         "publish only the three exclusively reserved V37 graph outputs")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            need(type(count) is int and count > 0,
                 "reject an incompletely written V37 graph owner")
            remaining = remaining[count:]
        os.fsync(handle)
        observed = os.fstat(handle)
        need(observed.st_uid == os.geteuid() and observed.st_nlink == 1
             and observed.st_size == len(raw)
             and stat.S_IMODE(observed.st_mode) == 0o600,
             "publish only a fully synchronized private unique V37 owner")
    finally:
        os.close(handle)
    directory = os.open(
        str(ROOT / Path(path).parent),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    observed, _ = read_owner(path, digest(raw), len(raw), private=True)
    need(observed == raw,
         "re-read the complete durable and exclusively generated V37 output")


def result(source: str, outputs: dict[str, bytes], written: bool,
           suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix, "version": 37, "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": digest(outputs[OUTPUT + ".svg"]),
        "actual_reference_falsification_sha256": FALSIFICATION[1],
        "actual_reference_falsification_bytes": FALSIFICATION[2],
        "full_case_denominator": 31237, "suite_count": 13,
        "private_waiver_count": 13, "qualified_candidate_count": 0,
        "phase_one_reference_gate_status": "FALSIFIED",
        "candidate_facing_self_oracle_status": "FAIL",
        "reference_context_falsifying_case_count": 96,
        "reference_context_text_case_count": 48,
        "reference_context_bytes_case_count": 48,
        "published_script_context_records_sha256": SCRIPT_VECTOR_SHA,
        "actual_candidate_facing_reference_records_sha256": ACTUAL_VECTOR_SHA,
        "all_candidate_matching_blocked": True,
        "same_context_reference_correction_status": "NOT RUN",
        "original_cases_removed": 0,
        "additional_private_waivers": 0,
        "case_denominator_changed": False,
        "c_pattern_equality_failure_waived": False,
        "zig_pattern_equality_failure_waived": False,
        "preserved_v36_evidence_owner_lower_bound": 161,
        "preserved_v36_history_reference_lower_bound": 166,
        "new_reference_falsification_evidence_owner_count": 1,
        "authenticated_evidence_owner_lower_bound": 162,
        "authenticated_history_reference_lower_bound": 167,
        "evidence_owner_count_is_authenticated_lower_bound": True,
        "history_reference_count_is_authenticated_lower_bound": True,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "historical_rust_semantic_mismatch_count": 1036,
        "historical_c_semantic_mismatch_count": 1230,
        "historical_zig_semantic_mismatch_count": 1764,
        "rust_v13_source_build_status": "PASS",
        "rust_v13_source_build_process_count": 28,
        "rust_v13_matching_test_status": "NOT RUN",
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_candidate_status": "NOT RUN",
        "outputs_written": written,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    parser.add_argument("--falsification-sha256")
    for name in ("inputs", "summary", "svg"):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(arguments)
    try:
        runtime()
        if options.self_test:
            need(all(getattr(options, key) is None for key in (
                "source_sha256", "source_bytes", "falsification_sha256",
                "inputs_sha256", "summary_sha256", "svg_sha256",
            )), "source-only tests must not accept genuine evidence pins")
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked(options.source_sha256, "actual V37 graph renderer")
        falsification = checked(options.falsification_sha256,
                                "actual Python-only falsification")
        _snapshot, pairs = build(source, options.source_bytes, falsification)
        outputs = dict(pairs)
        if options.render:
            need(options.inputs_sha256 is None
                 and options.summary_sha256 is None
                 and options.svg_sha256 is None,
                 "render only three genuinely new exclusively reserved V37 owners")
            for path, raw in pairs:
                publish(path, raw)
            sys.stdout.buffer.write(canonical(result(source, outputs, True,
                                                    "-published")))
            return 0
        expected = {
            OUTPUT + ".inputs.json": checked(options.inputs_sha256,
                                               "frozen V37 inputs"),
            OUTPUT + ".json": checked(options.summary_sha256,
                                         "frozen V37 summary"),
            OUTPUT + ".svg": checked(options.svg_sha256,
                                        "frozen V37 SVG"),
        }
        for path, fingerprint in expected.items():
            observed, _ = read_owner(path, fingerprint, len(outputs[path]),
                                     private=True)
            need(observed == outputs[path],
                 "independently reproduce every current V37 graph owner")
        sys.stdout.buffer.write(canonical(result(
            source, outputs, False, "-read-only-frozen-context",
        )))
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError,
            KeyError, AttributeError, zlib.error) as error:
        sys.stderr.write("current V37 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
