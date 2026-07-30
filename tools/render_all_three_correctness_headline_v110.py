#!/usr/bin/env python3
"""Render a source-only, truthful compatibility graph for three first-party engines."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import stat
import sys

ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/render_all_three_correctness_headline_v110.py"
PROTOCOL = "oracle/phase2/ALL-THREE-CORRECTNESS-HEADLINE-V110.md"
CONTRACT = "oracle/phase2/all-three-correctness-headline-v110.json"
OUTPUT = "docs/evidence/candidate-current-overview-v110"
VERSION, ORIGINAL, PUBLIC = 110, 31_237, 10_434
UNMEASURED = "NOT MEASURED"
DEVICE = 2064
SOURCE_INODE = 431872
PROTOCOL_INODE = 526734
GOAL_SHA = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
RUST_ENGINE = "e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8"
RUST_BRIDGE = "ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000"
RUST_ADAPTER = "f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227"
V30_ENGINE = "3c952a1a9eee234f646bdbd119978d8fb18c223ac71b63db1ed0eada9aed1237"
V30_BRIDGE = "ee63273fe7fc79934004db26a5c8df5b94ec3d0083837aed4bee701a7ed52256"
V30_ADAPTER = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
C_NATIVE = "891acc0d0f496045e90e2efc0f0a3125e4f508352c2ee5e31ee807ea2fb1801a"
C_ADAPTER = "e91819b1d6b399954b3384519fdfddb6ccd6d4e4099a34e06d702c9959a79193"
C_SOURCE = "99f45846551705379ccd7365333995ee68fe25e10d101655a17ad45c5e13a5e6"
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864), ("scanner_v3", 1_024),
    ("buffer_v3", 768), ("managed_v1", 1_024), ("scanner_verbose_v1", 2_854),
    ("public_types_v1", 6_912), ("substitution_v2", 5_120), ("shape_v2", 10_240),
    ("public_surface_v19", 1_376), ("subinterpreter_v2", 128),
    ("pep688_v4", 264), ("threaded_pattern_v1", 512),
)

# Every owner is immutable public plaintext. Native binaries, archives, private
# roots, candidates, benchmarks, proposals, and final cases are deliberately absent.
OWNERS = (
    ("goal", "GOAL.md", GOAL_SHA, 3756, 31364044),
    ("v104_source", "tools/render_rust_correctness_public_overview_v104.py",
     "41ee40ee41b4a6ca226460ad5f1bbcc7a9da77f8d3a583c32ad07ee5f83d7f30", 53068, 430711),
    ("v104_inputs", "docs/evidence/candidate-current-overview-v104.inputs.json",
     "874820795d5fb8c2258d63bbf379f301db05d7b7b2c3dc838143920accfa4e5c", 5245, 430724),
    ("v104_summary", "docs/evidence/candidate-current-overview-v104.json",
     "3b5f782bd71914bea528e1b065af9d89314c9966eecc0c98eba6927e900f6553", 21391, 430726),
    ("v104_svg", "docs/evidence/candidate-current-overview-v104.svg",
     "21631e6e10bd91bd6309c9dcb519aac99030ba0b81744cc98c67d2a6c3661836", 9924, 430723),
    ("v107_source", "tools/render_updated_correctness_headline_v107.py",
     "63aff115b24eeb7066e71ea7ee093a740b2a6a39a1fae0994908e7fa43ac9eea", 63064, 431578),
    ("v107_protocol", "oracle/phase2/UPDATED-CORRECTNESS-HEADLINE-V107.md",
     "205ecfdab25feaebd03333fe0ac2e48bda527c46d879870162a7afd85df6317c", 3664, 526409),
    ("v107_contract", "oracle/phase2/updated-correctness-headline-v107.json",
     "64d08dfdfd09334d0d852a20c4056a4ad62bf4644189fe09d503d202e0436367", 7064, 526418),
    ("v108_source", "tools/render_updated_correctness_headline_v108.py",
     "b9b1d0a268595d70b49ad40cc05ebb833ed99c5d6976ca9b8c4bbbafe7cba6fd", 76015, 431808),
    ("v108_protocol", "oracle/phase2/UPDATED-CORRECTNESS-HEADLINE-V108.md",
     "40195e9db372ab3ea3ba8aa9a4b2e2ad4112e77af935e21eae80f2bf991d7e29", 4630, 526622),
    ("v108_contract", "oracle/phase2/updated-correctness-headline-v108.json",
     "1fe218a2638d91b36cdba79f7753f3f4ecc21ea86ad3a5111f8e6c6a27ca42d8", 9131, 526624),
    ("v108_inputs", "docs/evidence/candidate-current-overview-v108.inputs.json",
     "f355d9481aa885253cf4e994598897c76cc208f57b86abcb0c75cc76822e2ea8", 7969, 431838),
    ("v108_summary", "docs/evidence/candidate-current-overview-v108.json",
     "cfbe714e870bd633438e2e617688f0cfe8adf7879fc9c17862a1b61f01741e5c", 40287, 431839),
    ("v108_svg", "docs/evidence/candidate-current-overview-v108.svg",
     "19f8600264956fb4687eb840d498fc8073636b0e66765776ad7d8f8afdc2ceae", 7752, 431837),
    ("rust_original",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v33-"
     "rust-full-public-semantic-source-root-provenance-original-p0-v28-publication-receipt.json",
     "5204823a291ec01890913218582ff978cbe923dd5c787c8d6ae68a9790c43064", 12067, 526161),
    ("rust_public",
     "oracle/phase2/evidence/rust-full-public-correctness-v5-v33-full-public-v5-run-001-"
     "publication-receipt.json",
     "8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9", 6889, 525451),
    ("rust_v30_audit", "oracle/phase2/evidence/rust-clean-non-delegation-v5-actual-source-audit.json",
     "a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203", 16427, 525089),
    ("zig_original",
     "oracle/phase2/evidence/repaired-zig-original-campaign-v18-phase2-v18-zig-final-"
     "original-p0-v18-success-publication-receipt.json",
     "b2762eaea6dd505aa34bd446996b0464b7a0e057e7fb7162355885e065e19bd0", 20905, 526565),
    ("zig_previous",
     "oracle/phase2/evidence/repaired-zig-original-campaign-v16-phase2-v16-zig-full-"
     "semantic-original-p0-v16-failures-publication-receipt.json",
     "a7019c02b2906eb15f622e9bd9e61eb7476c528019fac537ed7072b3f82efe7a", 21041, 526355),
    ("c_build",
     "oracle/phase2/evidence/native-source-build-v24-c-phase2-v24-c-complete-semantics-"
     "publication-receipt.json",
     "ed0c119b2e672342f3665c9dc7c4896977ea590bceec08ff3b97cd56b9f92a75", 14172, 526667),
    ("c_root",
     "oracle/phase2/evidence/native-source-build-v24-c-phase2-v24-c-complete-semantics-"
     "root-provenance-receipt.json",
     "36cb6adcf3a28d635fc997c090e62e1ce5563754deab02c05b41f4d034ad3048", 12573, 526668),
    ("c_original",
     "oracle/phase2/evidence/repaired-c-original-campaign-v16-c-phase2-v24-c-final-"
     "public-semantics-original-p0-v16-results-publication-receipt.json",
     "34f1b7ccd9fe06408cdc6094f86bf98f4776bc7716ad970264bfbbda0d1280f2", 10657, 525275),
    ("c_previous",
     "oracle/phase2/evidence/repaired-c-original-campaign-v15-c-phase2-v23-c-complete-"
     "semantics-original-p0-v15-failures-publication-receipt.json",
     "6adea6a4da59bb0c63c54006991257b46149c4447a82bb1cd6b8810e6bee5b43", 10888, 526500),
)


class Rejected(ValueError):
    """Reject altered evidence, hidden access, or misleading current results."""


def require(value: object, message: str) -> None:
    if value is not True:
        raise Rejected(message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                       separators=(",", ":")) + "\n").encode("ascii")


def unique(entries: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in entries:
        require(type(key) is str and key not in result, "reject duplicate JSON keys")
        result[key] = value
    return result


def document(payload: bytes, label: str) -> dict:
    try:
        result = json.loads(payload, object_pairs_hook=unique,
                            parse_constant=lambda value: (_ for _ in ()).throw(
                                Rejected("reject infinite or invalid evidence")))
    except (ValueError, TypeError, UnicodeError) as error:
        raise Rejected("reject malformed evidence: " + label) from error
    require(type(result) is dict and canonical(result) == payload,
            "reject noncanonical public evidence: " + label)
    return result


def same(value: object, expected: dict, label: str) -> None:
    require(type(value) is dict, "require complete object: " + label)
    for key, expected_value in expected.items():
        require(value.get(key) == expected_value,
                "authenticated evidence changed: " + label + ": " + key)


class SourceWall:
    """Deny all access except pinned public plaintext and root-only fresh graphs."""

    def __init__(self, mode: str, owners: tuple) -> None:
        self.mode = mode
        self.readable = frozenset(os.path.join(ROOT, row[1]) for row in owners)
        self.writable = frozenset(os.path.join(ROOT, OUTPUT + suffix)
                                  for suffix in (".svg", ".inputs.json", ".json"))

    def check(self, event: str, values: tuple) -> None:
        if event == "open":
            target = values[0] if values else None
            flags = values[2] if len(values) > 2 and type(values[2]) is int else 0
            require(type(target) is str, "reject borrowed descriptors and relative paths")
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                                    | os.O_TRUNC | os.O_APPEND))
            if writing:
                needed = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                require(self.mode == "graph" and target in self.writable
                        and flags & needed == needed,
                        "reject unauthorized or nonexclusive graph writes")
            else:
                require(target in self.readable and flags & os.O_NOFOLLOW != 0,
                        "reject candidate, native, archive, private, or holdout owner")
            return
        if event.startswith(("subprocess.", "socket.", "ctypes.", "os.exec", "os.spawn")):
            raise Rejected("reject candidate, compiler, native loader, process, or network")
        if event in {"os.system", "os.fork", "os.posix_spawn", "os.mkdir", "os.remove",
                     "os.rename", "os.rmdir", "os.chdir", "os.chmod", "os.link",
                     "os.symlink", "os.truncate", "os.putenv", "time.time",
                     "time.monotonic", "time.perf_counter", "_thread.start_new_thread",
                     "os.stat", "os.lstat", "os.listdir", "os.scandir"}:
            raise Rejected("reject unrelated mutation, metadata, timing, or thread")
        if event == "import" and values:
            name = values[0]
            require(not (type(name) is str and
                         (name in {"re", "_sre", "regex", "re2", "ctypes", "gzip"}
                          or name.startswith(("candidates.", "rebar.")))),
                    "reject candidate, matcher, native loader, or archive import")


def read(row: tuple, approved: tuple) -> tuple[dict, bytes]:
    require(row in approved, "reject an unapproved public plaintext owner")
    role, path, checksum, size, inode = row
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
                and before.st_ino == inode and before.st_size == size
                and before.st_uid == os.getuid() and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600,
                "reject changed physical public evidence owner: " + role)
        blocks = []
        while True:
            block = os.read(descriptor, 1_048_576)
            if not block:
                break
            blocks.append(block)
        payload = b"".join(blocks)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size, before.st_uid,
                 before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size, after.st_uid,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
                and digest(payload) == checksum,
                "reject swapped or incomplete public evidence: " + role)
        return ({"role": role, "path": path, "sha256": checksum,
                 "bytes": size, "inode": inode, "device": DEVICE,
                 "mode": "0600", "nlink": 1}, payload)
    finally:
        os.close(descriptor)


def effects() -> dict:
    return {"candidate_source_owners_opened_by_graph": 0,
            "candidate_workers_started_by_graph": 0,
            "reference_workers_started_by_graph": 0,
            "compiler_processes_started_by_graph": 0,
            "native_binary_files_opened_by_graph": 0,
            "native_binary_metadata_probes_by_graph": 0,
            "native_libraries_loaded_by_graph": 0,
            "private_build_roots_opened_by_graph": 0,
            "private_build_roots_statted_by_graph": 0,
            "compressed_archives_opened_by_graph": 0,
            "compressed_archives_statted_by_graph": 0,
            "holdout_proposal_files_opened_by_graph": 0,
            "holdout_proposal_files_statted_by_graph": 0,
            "seed_files_opened_by_graph": 0,
            "holdout_cases_opened_by_graph": 0,
            "hidden_cases_read_by_graph": 0,
            "final_holdout_opened": False,
            "clock_samples_by_graph": 0,
            "timing_trials_run": 0}


def verify_groups(value: dict, family: str, rows_key: str, worker_key: str,
                  mismatch_key: str) -> None:
    rows = value.get(rows_key)
    require(type(rows) is list and len(rows) == len(SUITES),
            "require all 13 independently completed " + family + " groups")
    workers, total = set(), 0
    for row, (name, cases) in zip(rows, SUITES, strict=True):
        same(row, {"suite": name, "case_execution_denominator": cases,
                   mismatch_key: 0, "status": "PASS"},
             "complete passing " + family + " group " + name)
        worker = row.get(worker_key)
        require(type(worker) is int and worker > 0 and worker not in workers,
                "require a distinct actual " + family + " process: " + name)
        workers.add(worker)
        total += cases
    require(total == ORIGINAL and len(workers) == 13,
            "preserve every actual " + family + " original check")


def verify(state: dict) -> None:
    entries = state["documents"]
    for role, value in entries.items():
        require(digest(canonical(value)) == state["owners"][role]["sha256"],
                "reject changed authenticated public JSON: " + role)
    require(digest(state["payloads"]["goal"]) == GOAL_SHA,
            "never edit or silently replace the immutable goal")

    rust = entries["rust_original"]
    same(rust, {"status": "PASS", "family": "rust", "candidate_status": "PASS",
                "candidate_qualified": False, "case_execution_denominator": ORIGINAL,
                "verified_passing_case_count": ORIGINAL, "semantic_mismatch_count": 0,
                "suite_count": 13, "completed_suite_count": 13,
                "actual_candidate_workers": 13, "infrastructure_failure_count": 0,
                "native_engine_sha256": RUST_ENGINE, "native_bridge_sha256": RUST_BRIDGE,
                "corrected_public_adapter_sha256": RUST_ADAPTER,
                "runtime_non_delegation": "NOT ESTABLISHED", "hidden_cases_read": 0,
                "winner_selected": False}, "exact original-suite Rust V33 PASS")
    rows = rust.get("suite_integrity")
    require(type(rows) is list and len(rows) == 13,
            "preserve every actual original Rust worker")
    workers = set()
    for row, (name, count) in zip(rows, SUITES, strict=True):
        same(row, {"suite": name, "case_execution_denominator": count,
                   "verified_passing_case_count": count, "mismatch_count": 0,
                   "failure_class": "PASS", "fully_observed": True,
                   "actual_worker_started": True, "returncode": 0},
             "actual passing Rust original group " + name)
        worker = row.get("pid")
        require(type(worker) is int and worker > 0 and worker not in workers,
                "reject omitted or repeated Rust workers")
        workers.add(worker)

    same(entries["rust_public"], {
        "schema": "rebar-owned-rust-full-public-correctness-v5-durable-publication-receipt",
        "status": "PASS", "candidate_status": "PASS", "candidate_qualified": False,
        "public_10434_correctness_status": "PASS", "public_10434_case_count": PUBLIC,
        "public_10434_verified_passing_case_count": PUBLIC,
        "public_10434_mismatch_count": 0, "all_public_cases_observed": True,
        "all_public_mismatches_preserved": True, "candidate_worker_count": 1,
        "reference_worker_count": 1, "v33_native_engine_sha256": RUST_ENGINE,
        "v33_native_bridge_sha256": RUST_BRIDGE, "v33_adapter_sha256": RUST_ADAPTER,
        "runtime_non_delegation": "NOT ESTABLISHED", "hidden_cases_read": 0,
        "winner_selected": False}, "the same exact Rust build passes its wider suite")

    audit = entries["rust_v30_audit"]
    same(audit, {"status": "PASS", "audited_family": "rust", "finding_count": 0,
                 "external_regex_libraries": 0, "external_regex_packages": 0,
                 "external_regex_symbols": 0, "candidate_qualified": False,
                 "runtime_non_delegation":
                     "NOT ESTABLISHED; STATIC SOURCE AND ELF AUDIT ONLY"},
         "preserve the older V30-only static first-party inspection")
    phases = audit.get("phases")
    require(type(phases) is list and len(phases) == 2,
            "preserve both genuine older Rust V30 audit phases")
    for phase in phases:
        binaries = phase.get("native_outputs")
        require(type(binaries) is list and len(binaries) == 2,
                "authenticate both older V30 native identities")
        observed = {entry["audit"]["role"]: entry["owner"]["sha256"]
                    for entry in binaries}
        require(observed == {"engine": V30_ENGINE, "bridge": V30_BRIDGE}
                and observed["engine"] != RUST_ENGINE
                and observed["bridge"] != RUST_BRIDGE,
                "never transfer an older V30 inspection to the passing V33 build")
        same(phase.get("sources", {}).get("candidates/rust_candidate.py", {})
             .get("owner"), {"sha256": V30_ADAPTER},
             "authenticate the distinct older V30 Python adapter")

    zig = entries["zig_original"]
    same(zig, {"status": "PASS", "family": "zig", "candidate_status": "PASS",
               "candidate_qualified": False, "case_execution_denominator": ORIGINAL,
               "verified_passing_case_count": ORIGINAL, "semantic_mismatch_count": 0,
               "suite_count": 13, "completed_suite_count": 13,
               "actual_candidate_workers": 13, "unique_candidate_worker_count": 13,
               "all_original_suites_attempted": True,
               "all_three_original_targets_restored": True,
               "infrastructure_failure_count": 0, "original_campaign_passed": True,
               "hidden_cases_read": 0, "winner_selected": False},
         "require all 31,237 real Zig original checks")
    verify_groups(zig, "Zig", "original_suite_diagnostics", "pid",
                  "observed_semantic_mismatch_count")
    same(entries["zig_previous"], {"family": "zig", "candidate_status": "FAIL",
                                    "verified_passing_case_count": 18_056,
                                    "semantic_mismatch_count": 1_156,
                                    "completed_suite_count": 13},
         "preserve every earlier genuine Zig failure")

    build, root = entries["c_build"], entries["c_root"]
    same(build, {
        "schema": "rebar-owned-c-complete-semantic-source-build-v24-durable-publication-receipt",
        "status": "PASS", "build_status": "PASS", "family": "c",
        "actual_compiler_process_count": 14, "expected_compiler_process_count": 14,
        "private_phase_count": 2, "distinct_native_artifact_count": 2,
        "byte_identical_native_artifacts": True, "native_artifact_sha256": C_NATIVE,
        "corrected_adapter_source_sha256": C_ADAPTER,
        "corrected_native_source_sha256": C_SOURCE,
        "candidate_workers_started": 0, "runtime_non_delegation": "NOT ESTABLISHED",
        "hidden_cases_read": 0}, "authenticate the exact twice-built C V24 native engine")
    same(root, {
        "schema": "rebar-owned-c-complete-semantic-source-build-v24-durable-root-provenance-receipt",
        "status": "PASS", "family": "c", "actual_compiler_process_count": 14,
        "native_artifact_sha256": C_NATIVE,
        "corrected_adapter_source_sha256": C_ADAPTER,
        "corrected_native_source_sha256": C_SOURCE,
        "runtime_non_delegation": "NOT ESTABLISHED"},
         "authenticate the exact C V24 source-root provenance without opening it")
    build_phases = build.get("phases")
    require(type(build_phases) is list and len(build_phases) == 2,
            "require two independent successful C source-build phases")
    for number, phase in enumerate(build_phases):
        same(phase, {"name": ("reference-a", "reference-b")[number],
                     "mode": "0700"}, "actual independent C phase " + str(number))
        same(phase.get("native_output"),
             {"sha256": C_NATIVE, "bytes": 163_544, "native_loaded": False},
             "authenticate the exact native C engine without loading it")

    current = entries["c_original"]
    same(current, {
        "schema": "rebar-owned-repaired-c-original-campaign-v16-durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS", "family": "c",
        "candidate_status": "PASS", "candidate_qualified": False,
        "case_execution_denominator": ORIGINAL,
        "verified_passing_case_count": ORIGINAL, "semantic_mismatch_count": 0,
        "complete_observed_semantic_mismatch_record_count": 0,
        "all_observed_semantic_mismatch_records_preserved": True,
        "suite_count": 13, "completed_suite_count": 13,
        "actual_candidate_workers": 13, "actual_worker_process_ids_are_distinct": True,
        "infrastructure_failure_count": 0, "candidate_execution_failure_count": 0,
        "worker_timeout_count": 0,
        "actual_c21_build_receipt_sha256":
            "ed0c119b2e672342f3665c9dc7c4896977ea590bceec08ff3b97cd56b9f92a75",
        "actual_c21_root_receipt_sha256":
            "36cb6adcf3a28d635fc997c090e62e1ce5563754deab02c05b41f4d034ad3048",
        "native_engine_sha256": C_NATIVE, "native_bridge_sha256": C_NATIVE,
        "unchanged_adapter_sha256": C_ADAPTER,
        "original_native_inode_restored": True, "original_source_targets_modified": 0,
        "hidden_cases_read": 0, "winner_selected": False},
         "bind the actual all-original C PASS to its exact C V24 native build")
    verify_groups(current, "C", "suite_outcomes", "worker_process_id", "mismatch_count")
    same(entries["c_previous"], {
        "status": "PASS", "family": "c", "candidate_status": "FAIL",
        "case_execution_denominator": ORIGINAL, "verified_passing_case_count": 22_798,
        "semantic_mismatch_count": 224,
        "complete_observed_semantic_mismatch_record_count": 224,
        "all_observed_semantic_mismatch_records_preserved": True,
        "completed_suite_count": 13}, "preserve the complete earlier 224 C differences")

    v104, v107 = entries["v104_summary"], entries["v107_contract"]
    same(v104.get("headline"), {"c_verified_original_checks": 16_413,
                                "c_observed_individual_mismatch_count": 606,
                                "zig_verified_original_checks": 4_607,
                                "zig_observed_individual_mismatch_lower_bound": 1_700},
         "preserve all older historical C and Zig failures")
    same(v107, {"version": 107}, "preserve the invalid immutable V107 freeze")
    same(v107.get("headline"), {"static_first_party_audit_status": "PASS",
                                "external_regex_engine_count": 0},
         "preserve rather than rewrite the falsified V107 Rust audit claim")

    predecessor, graph = entries["v108_contract"], entries["v108_summary"]
    same(predecessor, {
        "schema": "rebar-updated-correctness-headline-v108-source-freeze",
        "version": 108, "superseded_v107_static_claim_falsified": True,
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED"},
         "preserve the prior append-only V108 correction")
    same(graph, {"version": 108, "latest_c_verified_passing_case_count": 22_798,
                 "latest_c_semantic_mismatch_count": 224,
                 "latest_zig_verified_passing_case_count": ORIGINAL,
                 "historical_c_verified_passing_case_count": 16_413,
                 "historical_c_semantic_mismatch_count": 606,
                 "static_first_party_non_delegation": "NOT ESTABLISHED",
                 "qualified_candidate_count": 0, "winner_selected": False},
         "preserve the complete immutable existing V108 graph")
    require(b"224 recorded differences" in state["payloads"]["v108_svg"],
            "do not overwrite or silently modify the historical V108 graph")


def headline() -> dict:
    return {
        "purpose": "Build a faster, fully compatible Python re from scratch.",
        "bars_measure": "VERIFIED ORIGINAL COMPATIBILITY, NOT SPEED",
        "python_verified_original_checks": ORIGINAL,
        "python_verified_broader_public_checks": PUBLIC,
        "rust_verified_original_checks": ORIGINAL,
        "rust_verified_broader_public_checks": PUBLIC,
        "rust_original_mismatch_count": 0,
        "rust_broader_public_mismatch_count": 0,
        "rust_same_exact_build_verified": True,
        "zig_verified_original_checks": ORIGINAL,
        "zig_original_mismatch_count": 0,
        "zig_completed_original_group_count": 13,
        "zig_broader_public_result": UNMEASURED,
        "zig_historical_verified_original_checks": 18_056,
        "zig_historical_individual_mismatch_count": 1_156,
        "c_verified_original_checks": ORIGINAL,
        "c_original_mismatch_count": 0,
        "c_completed_original_group_count": 13,
        "c_broader_public_result": UNMEASURED,
        "c_previous_verified_original_checks": 22_798,
        "c_previous_individual_mismatch_count": 224,
        "c_historical_verified_original_checks": 16_413,
        "c_historical_individual_mismatch_count": 606,
        "historical_v30_static_first_party_audit_status": "PASS",
        "historical_v30_native_engine_sha256": V30_ENGINE,
        "historical_v30_native_bridge_sha256": V30_BRIDGE,
        "historical_v30_adapter_sha256": V30_ADAPTER,
        "historical_v30_audit_build_differs_from_current_v33": True,
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
        "current_v33_external_regex_engine_count": "NOT ESTABLISHED",
        "current_v33_external_regex_package_count": "NOT ESTABLISHED",
        "live_runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "cpp_complete_original_result": UNMEASURED,
        "go_complete_original_result": UNMEASURED,
        "fortran_complete_original_result": UNMEASURED,
        "final_hidden_speed": UNMEASURED,
        "winner_selected": False,
    }


def freeze(state: dict) -> dict:
    owners = state["owners"]
    return {
        "schema": "rebar-all-three-correctness-headline-v110-source-freeze",
        "version": VERSION,
        "status": "SOURCE FROZEN; ALL-THREE CORRECTNESS GRAPH NOT RENDERED",
        "goal_sha256": GOAL_SHA,
        "source": owners["source"],
        "protocol": owners["protocol"],
        "preserved_public_owners": {name: owner for name, owner in owners.items()
                                     if name not in {"source", "protocol", "contract"}},
        "same_exact_rust_build": {"engine_sha256": RUST_ENGINE,
                                  "bridge_sha256": RUST_BRIDGE,
                                  "adapter_sha256": RUST_ADAPTER},
        "same_exact_c_v24_build": {"native_engine_sha256": C_NATIVE,
                                   "native_bridge_sha256": C_NATIVE,
                                   "adapter_sha256": C_ADAPTER,
                                   "native_source_sha256": C_SOURCE},
        "headline": headline(),
        "original_case_execution_denominator": ORIGINAL,
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_counted_in_original_denominator": False,
        "historical_v30_audit_build_differs_from_current_v33": True,
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "final_hidden_speed": UNMEASURED,
        "winner_selected": False,
        "source_only_effects": effects(),
        "graph_publication": {
            "authorization": "ROOT-AUTHORIZED ONLY AFTER FROZEN COMMIT AND PUSH",
            "svg": OUTPUT + ".svg",
            "inputs": OUTPUT + ".inputs.json",
            "summary": OUTPUT + ".json",
            "actual_graph_rendered": False,
            "existing_graphs_mutated": False,
        },
    }


def escape(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def image() -> bytes:
    description = (
        "Compatibility, not speed. Python, Rust, Zig, and C all pass all 31,237 "
        "original Python re checks with zero differences. Rust also passes all "
        "10,434 separate wider checks; wider Zig and C results remain unmeasured. "
        "Historical 224 and 606 C differences and 1,156 Zig differences remain "
        "recorded. Current Rust static and live independence are not established; "
        "the static inspection covers an older Rust build only. No replacement is "
        "fully qualified, final hidden speed is not measured, and there is no winner."
    )
    rows = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="1030" '
        'viewBox="0 0 1480 1030" role="img" aria-labelledby="title description">',
        '<title id="title">How close are we to a faster Python re?</title>',
        '<desc id="description">' + escape(description) + '</desc>',
        '<rect width="1480" height="1030" rx="24" fill="#0c1421"/>',
        '<text x="56" y="80" fill="#f8fafc" font-size="38" '
        'font-family="system-ui,sans-serif" font-weight="760">'
        'How close are we to a faster Python re?</text>',
        '<text x="58" y="117" fill="#cbd5e1" font-size="19" '
        'font-family="system-ui,sans-serif">'
        'This picture measures compatibility with Python. It does not measure speed.</text>',
        '<rect x="55" y="151" width="857" height="156" rx="18" '
        'fill="#11293a" stroke="#32866d"/>',
        '<text x="78" y="191" fill="#86efac" font-size="24" '
        'font-family="system-ui,sans-serif" font-weight="740">'
        'Rust, Zig, and C all pass the original Python tests</text>',
        '<text x="79" y="243" fill="#f8fafc" font-size="31" '
        'font-family="system-ui,sans-serif" font-weight="760">'
        '31,237 / 31,237 checks each</text>',
        '<text x="80" y="277" fill="#d1fae5" font-size="16" '
        'font-family="system-ui,sans-serif">'
        'Rust also passes 10,434 / 10,434 separate wider checks.</text>',
        '<rect x="932" y="151" width="493" height="156" rx="18" '
        'fill="#182438" stroke="#52647f"/>',
        '<text x="955" y="190" fill="#e2e8f0" font-size="20" '
        'font-family="system-ui,sans-serif" font-weight="710">'
        'Important checks still remain</text>',
        '<text x="956" y="228" fill="#fcd34d" font-size="17" '
        'font-family="system-ui,sans-serif">'
        'Current Rust independence: NOT ESTABLISHED</text>',
        '<text x="956" y="267" fill="#cbd5e1" font-size="15" '
        'font-family="system-ui,sans-serif">'
        'An older Rust build passed inspection.</text>',
        '<text x="72" y="356" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif" font-weight="730">APPROACH</text>',
        '<text x="187" y="356" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif" font-weight="730">ORIGINAL PYTHON CHECKS</text>',
        '<text x="791" y="356" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif" font-weight="730">SEPARATE WIDER TEST</text>',
        '<text x="1127" y="356" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif" font-weight="730">RESULT</text>',
    ]
    for position, (name, color, public, detail) in enumerate((
            ("Python", "#34d399", PUBLIC, "Reference baseline"),
            ("Rust", "#60a5fa", PUBLIC, "Wider checks also pass"),
            ("Zig", "#a78bfa", None, "Wider test not measured"),
            ("C", "#fb923c", None, "Wider test not measured"))):
        y = 377 + position * 109
        rows.extend((
            f'<rect x="55" y="{y}" width="1370" height="94" rx="14" fill="#112034"/>',
            f'<text x="76" y="{y + 40}" fill="#f8fafc" font-size="21" '
            f'font-family="system-ui,sans-serif" font-weight="740">{escape(name)}</text>',
            f'<rect x="188" y="{y + 17}" width="419" height="20" rx="7" '
            f'fill="{color}"/>',
            f'<text x="188" y="{y + 69}" fill="#f8fafc" font-size="18" '
            f'font-family="system-ui,sans-serif">31,237 / 31,237</text>',
            f'<text x="617" y="{y + 35}" fill="{color}" font-size="18" '
            f'font-family="system-ui,sans-serif" font-weight="750">100%</text>',
        ))
        if public is None:
            rows.extend((
                f'<rect x="792" y="{y + 17}" width="240" height="20" rx="7" '
                'fill="#293950"/>',
                f'<text x="792" y="{y + 69}" fill="#cbd5e1" font-size="14" '
                'font-family="system-ui,sans-serif">NOT MEASURED</text>',
            ))
        else:
            rows.extend((
                f'<rect x="792" y="{y + 17}" width="240" height="20" rx="7" '
                f'fill="{color}"/>',
                f'<text x="792" y="{y + 69}" fill="#f8fafc" font-size="16" '
                'font-family="system-ui,sans-serif">10,434 / 10,434</text>',
            ))
        rows.append(
            f'<text x="1064" y="{y + 43}" fill="{color}" font-size="15" '
            f'font-family="system-ui,sans-serif" font-weight="700">'
            f'{escape(detail)}</text>')
    rows.extend((
        '<rect x="55" y="832" width="1370" height="126" rx="17" '
        'fill="#2a1e28" stroke="#815269"/>',
        '<text x="80" y="866" fill="#fda4af" font-size="20" '
        'font-family="system-ui,sans-serif" font-weight="740">'
        'What still needs to happen?</text>',
        '<text x="80" y="899" fill="#f8fafc" font-size="15" '
        'font-family="system-ui,sans-serif">'
        'Run the wider Zig and C tests. Prove every implementation is independent. '
        'Then measure final speed.</text>',
        '<text x="80" y="933" fill="#fcd34d" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="680">'
        'Qualified replacements: 0 of 3 required  ·  '
        'Final hidden speed: NOT MEASURED  ·  No winner</text>',
        '<text x="59" y="992" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'Every original percentage uses 31,237 checks. Earlier C and Zig failures '
        'remain recorded. C++, Go, and Fortran are not fully measured.</text>',
        '</svg>',
    ))
    return ("\n".join(rows) + "\n").encode("utf-8")


def graph(state: dict) -> dict:
    common = {
        "version": VERSION,
        "actual_current_graph_predecessor_version": 108,
        "goal_sha256": GOAL_SHA,
        "python": "3.14.6",
        "source": state["owners"]["source"],
        "protocol": state["owners"]["protocol"],
        "contract": state["owners"]["contract"],
        "preserved_public_owners": {
            name: owner for name, owner in state["owners"].items()
            if name not in {"source", "protocol", "contract"}
        },
        "headline": headline(),
        "original_case_execution_denominator": ORIGINAL,
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_counted_in_original_denominator": False,
        "rust_original_verified_passing_case_count": ORIGINAL,
        "rust_public_verified_passing_case_count": PUBLIC,
        "zig_original_verified_passing_case_count": ORIGINAL,
        "zig_original_semantic_mismatch_count": 0,
        "zig_wider_public_result": UNMEASURED,
        "c_original_verified_passing_case_count": ORIGINAL,
        "c_original_semantic_mismatch_count": 0,
        "c_wider_public_result": UNMEASURED,
        "previous_c_verified_passing_case_count": 22_798,
        "previous_c_semantic_mismatch_count": 224,
        "historical_c_verified_passing_case_count": 16_413,
        "historical_c_semantic_mismatch_count": 606,
        "historical_zig_verified_passing_case_count": 18_056,
        "historical_zig_semantic_mismatch_count": 1_156,
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
        "historical_v30_static_first_party_non_delegation": "PASS",
        "historical_v30_audit_build_differs_from_current_v33": True,
        "live_runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "candidate_qualified": False,
        "performance_measured_by_graph": UNMEASURED,
        "final_hidden_speed": UNMEASURED,
        "winner_selected": False,
        **effects(),
    }
    inputs = {**common, "schema": "rebar-candidate-current-overview-v110-inputs"}
    summary = {**common, "schema": "rebar-candidate-current-overview-v110-summary",
               "status": "PASS",
               "status_scope": "AUTHENTICATED CORRECTNESS GRAPH ONLY",
               "all_three_original_suite_pass_count": 3,
               "qualified_independent_family_count": 0,
               "rust_original_suite_results": state["documents"]["rust_original"]["suite_integrity"],
               "zig_original_suite_results": state["documents"]["zig_original"]
                   ["original_suite_diagnostics"],
               "c_original_suite_results": state["documents"]["c_original"]["suite_outcomes"],
               "previous_c_original_suite_results": state["documents"]["c_previous"]
                   ["suite_outcomes"]}
    return {"svg": image(), "inputs": canonical(inputs), "summary": canonical(summary)}


def validate_graph(state: dict, output: dict) -> None:
    require(output == graph(state), "require deterministic complete graph generation")
    for role in ("inputs", "summary"):
        result = document(output[role], "complete generated graph " + role)
        same(result, {"version": VERSION, "actual_current_graph_predecessor_version": 108,
                      "original_case_execution_denominator": ORIGINAL,
                      "broader_public_case_execution_denominator": PUBLIC,
                      "broader_public_counted_in_original_denominator": False,
                      "rust_original_verified_passing_case_count": ORIGINAL,
                      "rust_public_verified_passing_case_count": PUBLIC,
                      "zig_original_verified_passing_case_count": ORIGINAL,
                      "zig_original_semantic_mismatch_count": 0,
                      "zig_wider_public_result": UNMEASURED,
                      "c_original_verified_passing_case_count": ORIGINAL,
                      "c_original_semantic_mismatch_count": 0,
                      "c_wider_public_result": UNMEASURED,
                      "previous_c_verified_passing_case_count": 22_798,
                      "previous_c_semantic_mismatch_count": 224,
                      "historical_c_verified_passing_case_count": 16_413,
                      "historical_c_semantic_mismatch_count": 606,
                      "historical_v30_audit_build_differs_from_current_v33": True,
                      "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
                      "live_runtime_non_delegation": "NOT ESTABLISHED",
                      "qualified_candidate_count": 0,
                      "final_hidden_speed": UNMEASURED,
                      "winner_selected": False,
                      "hidden_cases_read_by_graph": 0,
                      "candidate_workers_started_by_graph": 0},
             "publish all real current results and preserve every old failure")
        same(result.get("headline"), headline(), "use one exact shared graph headline")
    for marker in (b'role="img"', b'aria-labelledby="title description"',
                   b"Rust, Zig, and C all pass the original Python tests",
                   b"31,237 / 31,237 checks each", b"10,434 / 10,434",
                   b"Current Rust independence: NOT ESTABLISHED",
                   b"Qualified replacements: 0 of 3 required",
                   b"Final hidden speed: NOT MEASURED", b"No winner"):
        require(marker in output["svg"],
                "accessible plain-language graph omitted: " + marker.decode())
    for private in (b"141557760", b"141,557,760", b"226492416", b"226,492,416"):
        require(all(private not in output[role] for role in ("svg", "inputs", "summary")),
                "never disclose private final-test proposal details")


def changed(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + " ALTERED"
    if type(value) is list:
        return value + ["ALTERED"]
    if type(value) is dict:
        return {**value, "__v110_hostile": True}
    if value is None:
        return "ALTERED"
    raise Rejected("unsupported hostile evidence change")


def controls(state: dict, output: dict) -> int:
    rejected = 0

    def deny(label: str, function) -> None:
        nonlocal rejected
        try:
            function()
        except (Rejected, ValueError, TypeError, KeyError, IndexError):
            rejected += 1
            return
        raise Rejected("a dishonest headline or unsafe access was accepted: " + label)

    for name, original in state["documents"].items():
        for field in sorted(original):
            def mutate_document(role=name, key=field):
                hostile = copy.deepcopy(state)
                hostile["documents"][role][key] = changed(
                    hostile["documents"][role][key])
                verify(hostile)
            deny(name + " altered " + field, mutate_document)
    for role, rows_key, worker_key in (
            ("rust_original", "suite_integrity", "pid"),
            ("zig_original", "original_suite_diagnostics", "pid"),
            ("c_original", "suite_outcomes", "worker_process_id")):
        for number in range(13):
            for field in ("suite", "case_execution_denominator", worker_key):
                def mutate_worker(name=role, index=number, key=field):
                    hostile = copy.deepcopy(state)
                    hostile["documents"][name][rows_key][index][key] = changed(
                        hostile["documents"][name][rows_key][index][key])
                    verify(hostile)
                deny(role + " omitted or changed worker " + str(number), mutate_worker)
    for role in ("inputs", "summary"):
        for key, value in (
                ("original_case_execution_denominator", ORIGINAL + PUBLIC),
                ("broader_public_counted_in_original_denominator", True),
                ("rust_original_verified_passing_case_count", ORIGINAL - 1),
                ("zig_original_verified_passing_case_count", ORIGINAL - 1),
                ("c_original_verified_passing_case_count", ORIGINAL - 1),
                ("c_original_semantic_mismatch_count", 224),
                ("zig_wider_public_result", "PASS"),
                ("c_wider_public_result", "PASS"),
                ("previous_c_semantic_mismatch_count", 0),
                ("historical_c_semantic_mismatch_count", 0),
                ("current_v33_static_first_party_non_delegation", "PASS"),
                ("historical_v30_audit_build_differs_from_current_v33", False),
                ("live_runtime_non_delegation", "ESTABLISHED"),
                ("qualified_candidate_count", 1),
                ("final_hidden_speed", "2x"),
                ("hidden_cases_read_by_graph", 1),
                ("winner_selected", True)):
            def mutate_output(name=role, field=key, replacement=value):
                hostile = dict(output)
                value = document(hostile[name], "hostile graph result")
                value[field] = replacement
                hostile[name] = canonical(value)
                validate_graph(state, hostile)
            deny(role + " dishonest " + key, mutate_output)
    for label, path in (
            ("candidate source", ROOT + "/candidates/rust_candidate.py"),
            ("native binary", ROOT + "/candidates/_rust_engine.so"),
            ("private build", "/tmp/rebar-phase2-native-build-v33-private"),
            ("compressed archive", ROOT + "/oracle/phase2/evidence/original.gz"),
            ("final proposal", ROOT + "/oracle/phase3/expanded-sealed-holdout-v3.json"),
            ("hidden seed", ROOT + "/oracle/phase3/final.seed"),
            ("hidden cases", ROOT + "/oracle/phase3/final-hidden.json"),
            ("benchmark", ROOT + "/performance/public.json")):
        deny(label, lambda value=path: state["wall"].check(
            "open", (value, None, os.O_RDONLY | os.O_NOFOLLOW)))
    for label, event, values in (
            ("candidate worker", "subprocess.Popen", (PYTHON,)),
            ("native loader", "ctypes.dlopen", ("engine.so",)),
            ("candidate import", "import", ("candidates.rust_candidate",)),
            ("standard-library engine", "import", ("re",)),
            ("compressed evidence", "import", ("gzip",)),
            ("benchmark timer", "time.perf_counter", ()),
            ("private metadata", "os.stat", ("/tmp/private",)),
            ("network", "socket.connect", ("example.invalid",)),
            ("thread", "_thread.start_new_thread", ()),
            ("rewrite graph", "os.rename", ("old", "new"))):
        deny(label, lambda action=event, arguments=values:
             state["wall"].check(action, arguments))
    require(rejected >= 450,
            "require exhaustive evidence, worker, graph, and hidden-access controls")
    return rejected


def valid_sha(value: str, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require exact independently pinned SHA-256: " + label)
    return value


def arguments() -> argparse.Namespace:
    flags = [item for item in sys.argv[1:] if item.startswith("--")]
    require(len(flags) == len(set(flags)), "reject duplicate source-freeze flags")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render-graph", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--protocol-bytes", required=True, type=int)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--contract-bytes", type=int)
    parser.add_argument("--contract-inode", type=int)
    parser.add_argument("--root-authorized", action="store_true")
    parser.add_argument("--frozen-committed-pushed", action="store_true")
    parser.add_argument("--frozen-commit")
    parser.add_argument("--pushed-commit")
    options = parser.parse_args()
    valid_sha(options.source_sha256, "source")
    valid_sha(options.protocol_sha256, "protocol")
    require(type(options.source_bytes) is int and 0 < options.source_bytes < 262_144
            and type(options.protocol_bytes) is int and 0 < options.protocol_bytes < 65_536,
            "independently pin exact whole source and protocol byte counts")
    if options.render_contract:
        require(options.contract_sha256 is None and options.contract_bytes is None
                and options.contract_inode is None
                and not options.root_authorized and not options.frozen_committed_pushed
                and options.frozen_commit is None and options.pushed_commit is None,
                "contract creation never receives graph-publication authority")
    else:
        valid_sha(options.contract_sha256, "contract")
        require(type(options.contract_bytes) is int and 0 < options.contract_bytes < 262_144,
                "independently pin exact complete contract bytes")
        require(type(options.contract_inode) is int and options.contract_inode > 0,
                "independently pin exact immutable frozen contract inode")
        if options.render_graph:
            require(options.root_authorized and options.frozen_committed_pushed
                    and type(options.frozen_commit) is str
                    and len(options.frozen_commit) == 40
                    and all(char in "0123456789abcdef" for char in options.frozen_commit)
                    and options.frozen_commit == options.pushed_commit,
                    "only root may render after the exact source freeze is committed and pushed")
        else:
            require(not options.root_authorized and not options.frozen_committed_pushed
                    and options.frozen_commit is None and options.pushed_commit is None,
                    "source-only verification has no graph-publication authority")
    return options


def context(options: argparse.Namespace) -> dict:
    source = ("source", SOURCE, options.source_sha256, options.source_bytes,
              SOURCE_INODE)
    protocol = ("protocol", PROTOCOL, options.protocol_sha256, options.protocol_bytes,
                PROTOCOL_INODE)
    owners = (*OWNERS, source, protocol)
    if not options.render_contract:
        owners += (("contract", CONTRACT, options.contract_sha256,
                    options.contract_bytes, options.contract_inode),)
    mode = "graph" if options.render_graph else "source"
    wall = SourceWall(mode, owners)
    sys.addaudithook(wall.check)
    metadata, payloads, documents = {}, {}, {}
    for owner in owners:
        identity, payload = read(owner, owners)
        role = owner[0]
        metadata[role], payloads[role] = identity, payload
        if owner[1].endswith(".json"):
            documents[role] = document(payload, role)
    result = {"options": options, "wall": wall, "owners": metadata,
              "payloads": payloads, "documents": documents}
    verify(result)
    if not options.render_contract:
        require(documents["contract"] == freeze(result),
                "reject stale, incomplete, or dishonest graph source contract")
    return result


def publish(path: str, content: bytes) -> None:
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        offset = 0
        while offset < len(content):
            count = os.write(descriptor, content[offset:])
            require(count > 0, "exclusive graph publication stopped")
            offset += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def main() -> int:
    options = arguments()
    require(sys.executable == PYTHON and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.no_site == 1
            and sys.flags.dont_write_bytecode == 1,
            "require exact pinned isolated no-site CPython 3.14.6")
    state = context(options)
    if options.render_contract:
        os.write(1, canonical(freeze(state)))
        return 0
    output = graph(state)
    validate_graph(state, output)
    hostile = controls(state, output) if options.self_test else 0
    if options.render_graph:
        for name, suffix in (("svg", ".svg"), ("inputs", ".inputs.json"),
                             ("summary", ".json")):
            publish(OUTPUT + suffix, output[name])
    result = {
        "schema": "rebar-all-three-correctness-headline-v110-source-result",
        "status": "PASS", "version": VERSION,
        "mode": "SELF-TEST" if options.self_test else
                ("GRAPH RENDER" if options.render_graph else "FROZEN CONTEXT"),
        "rust_original_verified_passing_case_count": ORIGINAL,
        "rust_wider_verified_passing_case_count": PUBLIC,
        "zig_original_verified_passing_case_count": ORIGINAL,
        "zig_wider_public_result": UNMEASURED,
        "c_original_verified_passing_case_count": ORIGINAL,
        "c_original_semantic_mismatch_count": 0,
        "c_wider_public_result": UNMEASURED,
        "preserved_previous_c_semantic_mismatch_count": 224,
        "preserved_historical_c_semantic_mismatch_count": 606,
        "historical_v30_audit_build_differs_from_current_v33": True,
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
        "live_runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "hostile_controls_rejected": hostile,
        "final_hidden_speed": UNMEASURED,
        "winner_selected": False,
        **effects(),
    }
    if options.render_graph:
        result.update({name + "_sha256": digest(payload)
                       for name, payload in output.items()})
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Rejected, OSError, TypeError, ValueError, KeyError, IndexError) as error:
        print("all-three-correctness-headline-v110: " + str(error), file=sys.stderr)
        raise SystemExit(1)
