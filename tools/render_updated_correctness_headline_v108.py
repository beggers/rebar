#!/usr/bin/env python3
"""Render an authenticated, plain-language overview of measured correctness."""

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
SOURCE = "tools/render_updated_correctness_headline_v108.py"
PROTOCOL = "oracle/phase2/UPDATED-CORRECTNESS-HEADLINE-V108.md"
CONTRACT = "oracle/phase2/updated-correctness-headline-v108.json"
OUTPUT = "docs/evidence/candidate-current-overview-v108"
VERSION = 108
ORIGINAL = 31_237
PUBLIC = 10_434
UNMEASURED = "NOT MEASURED"
GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3_756,
)
PREVIOUS = {
    "source": (
        "tools/render_rust_correctness_public_overview_v104.py",
        "41ee40ee41b4a6ca226460ad5f1bbcc7a9da77f8d3a583c32ad07ee5f83d7f30",
        53_068,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v104.inputs.json",
        "874820795d5fb8c2258d63bbf379f301db05d7b7b2c3dc838143920accfa4e5c",
        5_245,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v104.json",
        "3b5f782bd71914bea528e1b065af9d89314c9966eecc0c98eba6927e900f6553",
        21_391,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v104.svg",
        "21631e6e10bd91bd6309c9dcb519aac99030ba0b81744cc98c67d2a6c3661836",
        9_924,
    ),
}
ORIGINAL_RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v33-rust-full-public-semantic-source-root-provenance-original-"
    "p0-v28-publication-receipt.json",
    "5204823a291ec01890913218582ff978cbe923dd5c787c8d6ae68a9790c43064",
    12_067,
)
PUBLIC_RECEIPT = (
    "oracle/phase2/evidence/rust-full-public-correctness-v5-"
    "v33-full-public-v5-run-001-publication-receipt.json",
    "8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9",
    6_889,
)
AUDIT_RECEIPT = (
    "oracle/phase2/evidence/rust-clean-non-delegation-v5-actual-source-audit.json",
    "a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203",
    16_427,
)
ZIG_RECEIPT = (
    "oracle/phase2/evidence/repaired-zig-original-campaign-v18-phase2-v18-"
    "zig-final-original-p0-v18-success-publication-receipt.json",
    "b2762eaea6dd505aa34bd446996b0464b7a0e057e7fb7162355885e065e19bd0",
    20_905,
)
ZIG_FAILURE_RECEIPT = (
    "oracle/phase2/evidence/repaired-zig-original-campaign-v16-phase2-v16-"
    "zig-full-semantic-original-p0-v16-failures-publication-receipt.json",
    "a7019c02b2906eb15f622e9bd9e61eb7476c528019fac537ed7072b3f82efe7a",
    21_041,
)
C_BUILD_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v23-c-phase2-v23-c-"
    "complete-semantics-publication-receipt.json",
    "36dac1112f0bb388c6a172228b8e2172246d7eac083899539b2695323afce63c",
    13_561,
)
C_RESULT_RECEIPT = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v15-c-phase2-v23-"
    "c-complete-semantics-original-p0-v15-failures-publication-receipt.json",
    "6adea6a4da59bb0c63c54006991257b46149c4447a82bb1cd6b8810e6bee5b43",
    10_888,
)
FALSIFIED_V107 = {
    "source": (
        "tools/render_updated_correctness_headline_v107.py",
        "63aff115b24eeb7066e71ea7ee093a740b2a6a39a1fae0994908e7fa43ac9eea",
        63_064,
    ),
    "protocol": (
        "oracle/phase2/UPDATED-CORRECTNESS-HEADLINE-V107.md",
        "205ecfdab25feaebd03333fe0ac2e48bda527c46d879870162a7afd85df6317c",
        3_664,
    ),
    "contract": (
        "oracle/phase2/updated-correctness-headline-v107.json",
        "64d08dfdfd09334d0d852a20c4056a4ad62bf4644189fe09d503d202e0436367",
        7_064,
    ),
}
ENGINE_SHA = "e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8"
BRIDGE_SHA = "ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000"
ADAPTER_SHA = "f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227"
AUDITED_V30_ENGINE_SHA = "3c952a1a9eee234f646bdbd119978d8fb18c223ac71b63db1ed0eada9aed1237"
AUDITED_V30_BRIDGE_SHA = "ee63273fe7fc79934004db26a5c8df5b94ec3d0083837aed4bee701a7ed52256"
AUDITED_V30_BRIDGE_SOURCE_SHA = "254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55"
AUDITED_V30_ADAPTER_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
AUDITED_V30_PUBLICATION_SHA = "c29361f0436f73ada037ba497a0eb008eeadac6ebb41c50019521c0212448abd"
AUDITED_V30_ROOT_SHA = "26445b833ac0e846538a1f648059a1c8a224e4e2f1acd58f82e9458dcc142404"
BUILD_SHA = "cfe1464e1e8ce96bfa514b15cf96879a0642686987159dd79c15f4d9db408749"
ROOT_SHA = "7122c9bdff731be0f68602a4a216c1fa9700e6a78f9da9b534eeaef282c64c1c"
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1_024), ("buffer_v3", 768),
    ("managed_v1", 1_024), ("scanner_verbose_v1", 2_854),
    ("public_types_v1", 6_912), ("substitution_v2", 5_120),
    ("shape_v2", 10_240), ("public_surface_v19", 1_376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
OWNERS = (GOAL, *PREVIOUS.values(), *FALSIFIED_V107.values(),
          ORIGINAL_RECEIPT, PUBLIC_RECEIPT,
          AUDIT_RECEIPT, ZIG_RECEIPT, ZIG_FAILURE_RECEIPT,
          C_BUILD_RECEIPT, C_RESULT_RECEIPT)


class Rejected(ValueError):
    """The evidence, output, or strict source-only boundary changed."""


def require(value: object, reason: str) -> None:
    if value is not True:
        raise Rejected(reason)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                       sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def unique(items: list[tuple[str, object]]) -> dict:
    result = {}
    for name, value in items:
        require(type(name) is str and name not in result,
                "reject duplicate evidence fields")
        result[name] = value
    return result


def document(value: bytes, name: str) -> dict:
    try:
        result = json.loads(value, object_pairs_hook=unique,
                            parse_constant=lambda _: (_ for _ in ()).throw(
                                Rejected("reject infinite or nonnumeric evidence")))
    except (TypeError, ValueError, UnicodeError) as failure:
        raise Rejected("reject malformed evidence: " + name) from failure
    require(type(result) is dict and canonical(result) == value,
            "reject changed or noncanonical evidence: " + name)
    return result


def same(value: object, expected: dict, name: str) -> None:
    require(type(value) is dict, "require an authenticated object: " + name)
    for key, item in expected.items():
        require(value.get(key) == item, "evidence changed: " + name + ": " + key)


def reference(owner: tuple[str, str, int]) -> dict:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2]}


def sha(value: object, name: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require a separately pinned lowercase SHA-256: " + name)
    return value


class SourceWall:
    """Allow exact public evidence reads and root-only exclusive output writes."""

    def __init__(self, mode: str,
                 owners: tuple[tuple[str, str, int], ...]) -> None:
        self.mode = mode
        self.readable = frozenset(os.path.join(ROOT, item[0]) for item in owners)
        self.writable = frozenset(os.path.join(ROOT, OUTPUT + suffix)
                                  for suffix in (".svg", ".inputs.json", ".json"))

    def check(self, event: str, arguments: tuple) -> None:
        if event == "open":
            target = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 and type(arguments[2]) is int else 0
            require(type(target) is str, "reject relative paths or borrowed descriptors")
            mutation = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                                     | os.O_TRUNC | os.O_APPEND))
            if mutation:
                needed = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                require(self.mode == "graph" and target in self.writable
                        and flags & needed == needed,
                        "reject nonexclusive or unauthorized graph mutation")
            else:
                require(target in self.readable and flags & os.O_NOFOLLOW != 0,
                        "reject candidate, private root, archive, benchmark, or holdout access")
            return
        if event.startswith(("subprocess.", "socket.", "ctypes.", "os.exec", "os.spawn")):
            raise Rejected("reject candidate execution, native load, compiler, or network")
        if event in {"os.system", "os.fork", "os.posix_spawn", "os.mkdir",
                     "os.remove", "os.rename", "os.rmdir", "os.chdir", "os.chmod",
                     "os.link", "os.symlink", "os.truncate", "os.putenv",
                     "time.time", "time.monotonic", "time.perf_counter",
                     "_thread.start_new_thread"}:
            raise Rejected("reject unrelated mutation, timing, process, or thread")
        if event == "import" and arguments:
            name = arguments[0]
            require(not (type(name) is str and (
                name in {"re", "_sre", "regex", "re2", "ctypes", "gzip"}
                or name.startswith(("candidates.", "rebar."))
            )), "reject candidate, regex engine, native loader, or archive import")


def read(owner: tuple[str, str, int],
         approved: tuple[tuple[str, str, int], ...]) -> tuple[dict, bytes]:
    require(owner in approved, "reject an unapproved evidence owner")
    path, fingerprint, size = owner
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_uid == os.getuid()
                and before.st_nlink == 1 and before.st_size == size,
                "public evidence owner identity changed: " + path)
        pieces = []
        while True:
            part = os.read(descriptor, 1_048_576)
            if not part:
                break
            pieces.append(part)
        payload = b"".join(pieces)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size, before.st_uid,
                 before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size, after.st_uid,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
                and digest(payload) == fingerprint,
                "complete public evidence content changed: " + path)
        return ({"path": path, "sha256": fingerprint, "bytes": size,
                 "device": after.st_dev, "inode": after.st_ino,
                 "uid": after.st_uid, "mode": "0600", "nlink": after.st_nlink},
                payload)
    finally:
        os.close(descriptor)


def effects() -> dict:
    return {
        "candidate_source_owners_opened_by_graph": 0,
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
        "timing_trials_run": 0,
    }


def verify_previous(state: dict) -> None:
    inputs, summary = state["previous_inputs"], state["previous_summary"]
    common = {
        "version": 104,
        "goal_sha256": GOAL[1],
        "original_case_execution_denominator": ORIGINAL,
        "original_suite_count": 13,
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_counted_in_original_denominator": False,
        "static_first_party_non_delegation": "PASS",
        "live_runtime_no_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    same(inputs, common, "preserved V104 inputs")
    same(summary, common, "preserved V104 summary")
    same(summary, {
        "schema": "rebar-candidate-current-overview-v104-summary",
        "status": "PASS",
        "original_verified_passing_case_count": ORIGINAL,
        "original_semantic_mismatch_count": 0,
        "broader_public_verified_passing_case_count": PUBLIC,
        "broader_public_semantic_mismatch_count": 0,
        "historical_c_original_observed_mismatch_count": 606,
        "historical_zig_original_observed_mismatch_lower_bound": 1_700,
    }, "preserve every historical result")
    same(summary.get("headline"), {
        "python_verified_original_checks": ORIGINAL,
        "rust_verified_original_checks": ORIGINAL,
        "rust_verified_broader_public_checks": PUBLIC,
        "c_verified_original_checks": 16_413,
        "c_observed_individual_mismatch_count": 606,
        "zig_verified_original_checks": 4_607,
        "zig_observed_individual_mismatch_lower_bound": 1_700,
    }, "never erase the earlier Zig/C failures")
    require(type(summary.get("complete_original_suite_results")) is list
            and len(summary["complete_original_suite_results"]) == len(SUITES)
            and type(summary.get("preserved_c_original_suite_results")) is list
            and len(summary["preserved_c_original_suite_results"]) == len(SUITES),
            "preserve every older Rust and C correctness group")
    require(state["previous_svg"].startswith(b"<svg ")
            and b"606 differences" in state["previous_svg"]
            and b"At least 1,700 differences" in state["previous_svg"],
            "the complete historical accessible graph changed")


def exact_field(receipt: dict, names: tuple[str, ...], expected: str,
                label: str) -> None:
    found = [(name, receipt[name]) for name in names if name in receipt]
    require(bool(found) and all(value == expected for _, value in found),
            "the exact Rust build identity changed: " + label)


def verify_original(state: dict) -> None:
    value = state["original"]
    same(value, {
        "status": "PASS", "publication_status": "PASS", "family": "rust",
        "candidate_status": "PASS", "candidate_original_oracle_pass": True,
        "original_suite_correctness_qualified": True, "candidate_qualified": False,
        "case_execution_denominator": ORIGINAL,
        "verified_passing_case_count": ORIGINAL,
        "semantic_mismatch_count": 0, "suite_count": 13,
        "completed_suite_count": 13, "actual_candidate_workers": 13,
        "distinct_worker_process_id_count": 13,
        "infrastructure_failure_count": 0,
        "all_four_original_targets_restored": True,
        "all_original_observation_vectors_complete": True,
        "actual_v28_build_receipt_sha256": BUILD_SHA,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "hidden_cases_read": 0, "winner_selected": False,
    }, "actual complete same-build Rust original PASS")
    exact_field(value, ("native_engine_sha256", "actual_v33_native_engine_sha256"),
                ENGINE_SHA, "native engine")
    exact_field(value, ("native_bridge_sha256", "actual_v33_native_bridge_sha256"),
                BRIDGE_SHA, "native bridge")
    exact_field(value, ("corrected_public_adapter_sha256", "v33_adapter_sha256",
                        "actual_v33_adapter_sha256"), ADAPTER_SHA, "Python interface")
    workers = value.get("actual_worker_process_ids")
    rows = value.get("suite_integrity")
    require(type(workers) is list and len(workers) == 13
            and len(set(workers)) == 13
            and all(type(item) is int and item > 0 for item in workers)
            and type(rows) is list and len(rows) == 13,
            "require 13 distinct observed original Rust workers")
    for row, (name, count) in zip(rows, SUITES, strict=True):
        same(row, {"suite": name, "case_execution_denominator": count,
                   "verified_passing_case_count": count, "mismatch_count": 0,
                   "failure_class": "PASS", "fully_observed": True,
                   "actual_worker_started": True, "worker_attempted": True,
                   "returncode": 0}, "complete Rust group " + name)
        require(row.get("pid") in workers,
                "bind every passing original group to its actual worker")


def verify_public(state: dict) -> None:
    # These immutable receipt fields cite the historical V5/V30 audit. Their
    # recorded zero counts must never be attributed to the passing V33 build.
    same(state["public"], {
        "schema": "rebar-owned-rust-full-public-correctness-v5-durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS", "candidate_status": "PASS",
        "candidate_qualified": False, "public_10434_correctness_status": "PASS",
        "public_10434_case_count": PUBLIC,
        "public_10434_verified_passing_case_count": PUBLIC,
        "public_10434_mismatch_count": 0, "all_public_cases_observed": True,
        "all_public_mismatches_preserved": True,
        "candidate_worker_count": 1, "reference_worker_count": 1,
        "v33_native_engine_sha256": ENGINE_SHA,
        "v33_native_bridge_sha256": BRIDGE_SHA,
        "v33_adapter_sha256": ADAPTER_SHA,
        "v33_publication_sha256": BUILD_SHA,
        "v33_root_sha256": ROOT_SHA,
        "v5_static_pass_sha256": AUDIT_RECEIPT[1],
        "v5_static_external_regex_library_count": 0,
        "v5_static_external_regex_package_count": 0,
        "v5_static_external_regex_symbol_count": 0,
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "hidden_cases_generated": 0, "hidden_cases_read": 0,
        "winner_selected": False,
    }, "same exact Rust build passed all wider checks")


def verify_audit(state: dict) -> None:
    audit = state["audit"]
    same(audit, {
        "schema": "rebar-phase2-clean-first-party-rust-non-delegation-v5-root-static-audit",
        "status": "PASS", "audited_family": "rust", "finding_count": 0,
        "findings": [], "external_regex_libraries": 0,
        "external_regex_packages": 0, "external_regex_symbols": 0,
        "cross_family_dependencies": 0,
        "clean_candidate_source_static_non_delegation": "PASS",
        "clean_candidate_native_elf_static_non_delegation": "PASS",
        "candidate_qualified": False, "candidate_executions": 0,
        "native_library_loads": 0,
        "runtime_non_delegation":
            "NOT ESTABLISHED; STATIC SOURCE AND ELF AUDIT ONLY",
        "winner_selected": False,
    }, "historical V30 static audit is not proof of the current V33 build")
    authenticated = audit.get("authenticated_v30")
    same(authenticated, {
        "actual_compiler_process_count": 28,
        "actual_completed_phase_count": 2,
        "actual_private_native_owner_count": 4,
        "actual_private_source_owner_count": 18,
        "external_cargo_dependencies": 0,
    }, "bind the older audited V30 build, not the passing V33 build")
    same(authenticated.get("publication_owner"), {
        "sha256": AUDITED_V30_PUBLICATION_SHA,
        "path": "oracle/phase2/evidence/native-source-build-v30-rust-phase2-v30-"
                "rust-complete-semantic-source-root-provenance-publication-receipt.json",
    }, "bind the older V30 publication without opening its owner")
    same(authenticated.get("root_provenance_owner"), {
        "sha256": AUDITED_V30_ROOT_SHA,
        "path": "oracle/phase2/evidence/native-source-build-v30-rust-phase2-v30-"
                "rust-complete-semantic-source-root-provenance-root-provenance-receipt.json",
    }, "bind the older V30 source root without opening its owner")
    phases = audit.get("phases")
    require(type(phases) is list and len(phases) == 2,
            "authenticate both older V30 static-inspection phases")
    for index, phase in enumerate(phases):
        same(phase, {
            "private_native_owner_count": 2,
            "private_source_owner_count": 9,
            "external_regex_packages": 0,
        }, "authenticate older V30 inspection phase " + str(index))
        native = phase.get("native_outputs")
        require(type(native) is list and len(native) == 2,
                "bind both older V30 native binaries")
        observed = {}
        for entry in native:
            require(type(entry) is dict, "reject an omitted older V30 native owner")
            details, owner = entry.get("audit"), entry.get("owner")
            require(type(details) is dict and type(owner) is dict,
                    "reject an incomplete older V30 native inspection")
            role = details.get("role")
            require(role in {"engine", "bridge"} and role not in observed,
                    "reject a duplicate or mislabeled older V30 native binary")
            observed[role] = owner.get("sha256")
        require(observed == {
            "engine": AUDITED_V30_ENGINE_SHA,
            "bridge": AUDITED_V30_BRIDGE_SHA,
        }, "the static audit belongs to older V30, not the passing V33")
        sources = phase.get("sources")
        require(type(sources) is dict,
                "bind the audited older V30 Python adapter and bridge source")
        adapter = sources.get("candidates/rust_candidate.py")
        bridge_source = sources.get("candidates/rust/py_bridge.c")
        require(type(adapter) is dict and type(bridge_source) is dict,
                "reject omitted older V30 source identities")
        same(adapter.get("owner"), {"sha256": AUDITED_V30_ADAPTER_SHA},
             "authenticate the older V30 Python adapter")
        same(bridge_source.get("owner"), {
            "sha256": AUDITED_V30_BRIDGE_SOURCE_SHA,
        }, "authenticate the older V30 bridge source")
    require(AUDITED_V30_ENGINE_SHA != ENGINE_SHA
            and AUDITED_V30_BRIDGE_SHA != BRIDGE_SHA
            and AUDITED_V30_ADAPTER_SHA != ADAPTER_SHA
            and AUDITED_V30_PUBLICATION_SHA != BUILD_SHA
            and AUDITED_V30_ROOT_SHA != ROOT_SHA,
            "never transfer an older V30 audit to the current V33 implementation")


def verify_falsified_v107(state: dict) -> None:
    source, protocol = state["falsified_v107_source"], state["falsified_v107_protocol"]
    require(digest(source) == FALSIFIED_V107["source"][1]
            and digest(protocol) == FALSIFIED_V107["protocol"][1],
            "preserve the immutable superseded V107 source and protocol")
    contract = state["falsified_v107_contract"]
    require(digest(canonical(contract)) == FALSIFIED_V107["contract"][1],
            "preserve the immutable superseded V107 contract")
    same(contract, {
        "schema": "rebar-updated-correctness-headline-v107-source-freeze",
        "version": 107,
    }, "preserve, rather than silently replace, the falsified V107 freeze")
    same(contract.get("same_rust_build"), {
        "engine_sha256": ENGINE_SHA,
        "bridge_sha256": BRIDGE_SHA,
        "adapter_sha256": ADAPTER_SHA,
    }, "the superseded V107 freeze described the current V33 build")
    same(contract.get("actual_rust_first_party_audit"), {
        "sha256": AUDIT_RECEIPT[1],
    }, "the superseded V107 freeze cited only the older V30 audit")
    same(contract.get("headline"), {
        "static_first_party_audit_status": "PASS",
        "external_regex_engine_count": 0,
        "external_regex_package_count": 0,
        "external_regex_symbol_count": 0,
    }, "preserve the exact older-build audit attribution falsified by V108")


def verify_previous_zig(state: dict) -> None:
    value = state["zig_previous"]
    same(value, {
        "schema": "rebar-owned-repaired-zig-original-campaign-v16-durable-publication-receipt",
        "status": "PASS", "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "family": "zig", "candidate_status": "FAIL",
        "candidate_qualified": False, "case_execution_denominator": ORIGINAL,
        "verified_passing_case_count": 18_056,
        "semantic_mismatch_count": 1_156,
        "observed_semantic_mismatch_lower_bound": 1_156,
        "suite_count": 13, "completed_suite_count": 13,
        "actual_candidate_workers": 13, "unique_candidate_worker_count": 13,
        "all_original_suites_attempted": True,
        "all_three_original_targets_restored": True,
        "infrastructure_failure_count": 0, "timeout_count": 0,
        "original_campaign_passed": False,
        "supplemental_candidate_matching": "NOT RUN",
        "hidden_cases_read": 0, "winner_selected": False,
    }, "actual complete Zig observation still has 1,156 differences")
    expected_failures = ["original_bounded_v5", "public_v3", "scanner_v3",
                         "scanner_verbose_v1", "public_types_v1",
                         "public_surface_v19"]
    require(value.get("failed_suites") == expected_failures,
            "preserve every actual failing Zig group")
    rows = value.get("original_suite_diagnostics")
    require(type(rows) is list and len(rows) == 13,
            "preserve every actual Zig worker group")
    workers, mismatches, verified = set(), 0, 0
    for row, (name, count) in zip(rows, SUITES, strict=True):
        same(row, {"suite": name, "case_execution_denominator": count,
                   "candidate_imported": True,
                   "guard_installed_before_candidate_import": True,
                   "infrastructure_failure": False,
                   "timed_out": False, "returncode": 0},
             "fully observed Zig group " + name)
        worker = row.get("pid")
        errors = row.get("observed_semantic_mismatch_count")
        require(type(worker) is int and worker > 0 and worker not in workers
                and type(errors) is int and 0 <= errors <= count,
                "bind every Zig group to a real distinct worker and valid count")
        workers.add(worker)
        mismatches += errors
        if row.get("status") == "PASS":
            require(errors == 0, "never hide a Zig difference in a passing group")
            verified += count
        else:
            require(row.get("status") == "FAIL" and errors > 0,
                    "never promote a failing Zig group to a pass")
    require(len(workers) == 13 and mismatches == 1_156 and verified == 18_056,
            "preserve exact Zig failures without counting unfinished checks as passes")


def verify_zig(state: dict) -> None:
    value = state["zig"]
    same(value, {
        "schema": "rebar-owned-repaired-zig-original-campaign-v18-durable-publication-receipt",
        "status": "PASS", "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "family": "zig", "candidate_status": "PASS",
        "candidate_qualified": False, "case_execution_denominator": ORIGINAL,
        "verified_passing_case_count": ORIGINAL,
        "semantic_mismatch_count": 0,
        "observed_semantic_mismatch_lower_bound": 0,
        "suite_count": 13, "completed_suite_count": 13,
        "actual_candidate_workers": 13, "unique_candidate_worker_count": 13,
        "all_original_suites_attempted": True,
        "all_three_original_targets_restored": True,
        "infrastructure_failure_count": 0, "timeout_count": 0,
        "original_campaign_passed": True,
        "supplemental_candidate_matching": "NOT RUN",
        "hidden_cases_read": 0, "winner_selected": False,
    }, "require the genuinely complete zero-difference original Zig candidate pass")
    require(value.get("failed_suites") == [],
            "never hide a failing original Zig group")
    rows = value.get("original_suite_diagnostics")
    require(type(rows) is list and len(rows) == 13,
            "preserve all 13 independently observed passing Zig workers")
    workers = set()
    for row, (name, count) in zip(rows, SUITES, strict=True):
        same(row, {"suite": name, "case_execution_denominator": count,
                   "candidate_imported": True,
                   "guard_installed_before_candidate_import": True,
                   "infrastructure_failure": False,
                   "timed_out": False, "returncode": 0,
                   "status": "PASS", "observed_semantic_mismatch_count": 0},
             "require complete actual passing Zig group " + name)
        worker = row.get("pid")
        require(type(worker) is int and worker > 0 and worker not in workers,
                "require a distinct actual process for every passing Zig group")
        workers.add(worker)
    require(len(workers) == 13,
            "require 13 genuine independently completed Zig workers")


def verify_c_build(state: dict) -> None:
    same(state["c_build"], {
        "schema": "rebar-owned-c-complete-semantic-source-build-v23-durable-publication-receipt",
        "status": "PASS", "build_status": "PASS", "family": "c",
        "publication_pass_means": "DURABLE FIRST-PARTY C DUAL SOURCE BUILD ONLY",
        "candidate_correctness": UNMEASURED,
        "candidate_matching": "NOT RUN",
        "actual_compiler_process_count": 14,
        "expected_compiler_process_count": 14,
        "private_phase_count": 2,
        "distinct_native_artifact_count": 2,
        "byte_identical_native_artifacts": True,
        "candidate_workers_started": 0,
        "native_libraries_loaded": 0,
        "installed_native_activated": False,
        "preserved_latest_c12_observed_mismatches": 606,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "hidden_cases_read": 0, "winner_selected": False,
    }, "a successful new C build is not a measured matching result")


def verify_c_result(state: dict) -> None:
    value = state["c_result"]
    same(value, {
        "schema": "rebar-owned-repaired-c-original-campaign-v15-durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE CORRECTNESS PUBLICATION ONLY",
        "family": "c", "candidate_status": "FAIL",
        "candidate_qualified": False, "case_execution_denominator": ORIGINAL,
        "verified_passing_case_count": 22_798,
        "semantic_mismatch_count": 224,
        "observed_semantic_mismatch_lower_bound": 224,
        "complete_observed_semantic_mismatch_record_count": 224,
        "all_observed_semantic_mismatch_records_preserved": True,
        "suite_count": 13, "completed_suite_count": 13,
        "attempted_suite_count": 13, "actual_candidate_workers": 13,
        "actual_worker_process_ids_are_distinct": True,
        "infrastructure_failure_count": 0,
        "candidate_execution_failure_count": 0,
        "worker_timeout_count": 0,
        "actual_c21_build_receipt_sha256": C_BUILD_RECEIPT[1],
        "unchanged_adapter_sha256":
            "4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a",
        "original_native_inode_restored": True,
        "original_source_targets_modified": 0,
        "hidden_cases_read": 0, "holdout": "NOT OPENED",
        "winner_selected": False,
    }, "preserve the actual complete C campaign and all 224 differences")
    rows, workers = value.get("suite_outcomes"), value.get("actual_worker_process_ids")
    require(type(rows) is list and len(rows) == 13
            and type(workers) is list and len(workers) == 13
            and all(type(item) is int and item > 0 for item in workers)
            and len(set(workers)) == 13,
            "require all 13 distinct genuine C correctness workers")
    verified, mismatches = 0, 0
    for row, (name, count) in zip(rows, SUITES, strict=True):
        same(row, {"suite": name, "case_execution_denominator": count,
                   "actual_candidate_workers": 1},
             "preserve complete actual C worker " + name)
        worker = row.get("worker_process_id")
        errors = row.get("mismatch_count")
        require(worker in workers and type(errors) is int and 0 <= errors <= count,
                "bind every original C group to a real worker and valid mismatch count")
        mismatches += errors
        if row.get("status") == "PASS":
            require(errors == 0, "never conceal a C mismatch in a passing group")
            verified += count
        else:
            require(row.get("status") == "FAIL" and errors > 0,
                    "never promote an actual failing C group to a pass")
    require(verified == 22_798 and mismatches == 224,
            "preserve all verified C checks and the complete 224-difference vector")


def verify(state: dict) -> None:
    require(digest(state["goal"]) == GOAL[1], "the immutable goal changed")
    for name, owner in (("previous_inputs", PREVIOUS["inputs"]),
                        ("previous_summary", PREVIOUS["summary"]),
                        ("original", ORIGINAL_RECEIPT),
                        ("public", PUBLIC_RECEIPT),
                        ("audit", AUDIT_RECEIPT),
                        ("zig", ZIG_RECEIPT),
                        ("zig_previous", ZIG_FAILURE_RECEIPT),
                        ("c_build", C_BUILD_RECEIPT),
                        ("c_result", C_RESULT_RECEIPT)):
        require(digest(canonical(state[name])) == owner[1],
                "authenticated evidence content changed: " + name)
    require(digest(state["previous_svg"]) == PREVIOUS["svg"][1],
            "the historical correctness graph changed")
    verify_previous(state)
    verify_falsified_v107(state)
    verify_original(state)
    verify_public(state)
    verify_audit(state)
    verify_previous_zig(state)
    verify_zig(state)
    verify_c_build(state)
    verify_c_result(state)


def escape(value: object) -> str:
    text = str(value)
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def percentage(value: int, count: int) -> str:
    return "100%" if value == count else f"{100 * value / count:.1f}%"


def image() -> bytes:
    description = (
        "Compatibility, not speed. Python, Rust, and Zig each pass all 31,237 "
        "original Python re checks with zero differences. Rust also passes all "
        "10,434 separate wider checks; Zig's wider result is not measured. "
        "C has 22,798 verified passing original checks and 224 remaining "
        "differences. Earlier C and Zig differences remain recorded. "
        "The current Rust build has no matching static or live independence "
        "audit; an older Rust build passed a separate inspection. No candidate "
        "is fully qualified, final hidden speed is not measured, and there "
        "is no winner."
    )
    items = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="1108" '
        'viewBox="0 0 1480 1108" role="img" aria-labelledby="title description">',
        '<title id="title">How close are we to a faster Python re?</title>',
        f'<desc id="description">{escape(description)}</desc>',
        '<rect width="1480" height="1108" rx="24" fill="#0c1421"/>',
        '<text x="56" y="80" fill="#f8fafc" font-size="38" '
        'font-family="system-ui,sans-serif" font-weight="760">'
        'How close are we to a faster Python re?</text>',
        '<text x="58" y="117" fill="#cbd5e1" font-size="19" '
        'font-family="system-ui,sans-serif">'
        'This picture measures matching Python correctly. It does not measure speed.</text>',
        '<rect x="55" y="151" width="859" height="164" rx="18" '
        'fill="#11293a" stroke="#32866d"/>',
        '<text x="79" y="190" fill="#86efac" font-size="22" '
        'font-family="system-ui,sans-serif" font-weight="730">'
        'Rust and Zig both pass the complete original test</text>',
        '<text x="80" y="242" fill="#f8fafc" font-size="31" '
        'font-family="system-ui,sans-serif" font-weight="760">'
        '31,237 / 31,237 checks each</text>',
        '<text x="81" y="282" fill="#d1fae5" font-size="17" '
        'font-family="system-ui,sans-serif">'
        'Rust also passes 10,434 / 10,434 wider checks.</text>',
        '<rect x="934" y="151" width="490" height="164" rx="18" '
        'fill="#182438" stroke="#52647f"/>',
        '<text x="958" y="190" fill="#e2e8f0" font-size="20" '
        'font-family="system-ui,sans-serif" font-weight="700">'
        'Independence still needs proof</text>',
        '<text x="958" y="233" fill="#86efac" font-size="18" '
        'font-family="system-ui,sans-serif" font-weight="720">'
        'Current Rust audit: NOT ESTABLISHED</text>',
        '<text x="958" y="274" fill="#fcd34d" font-size="15" '
        'font-family="system-ui,sans-serif">'
        'Older Rust build passed inspection</text>',
        '<text x="66" y="367" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif" font-weight="730">APPROACH</text>',
        '<text x="187" y="367" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif" font-weight="730">'
        'ORIGINAL PYTHON CHECKS</text>',
        '<text x="796" y="367" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif" font-weight="730">'
        'SEPARATE WIDER TEST</text>',
        '<text x="1156" y="367" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif" font-weight="730">RESULT</text>',
    ]
    entries = (
        ("Python", ORIGINAL, PUBLIC, "#34d399", "Reference", "All checks pass"),
        ("Rust", ORIGINAL, PUBLIC, "#60a5fa", "All checks pass",
         "Final qualification pending"),
        ("Zig", ORIGINAL, None, "#a78bfa", "All original checks pass",
         "Wider test not measured"),
        ("C", 22_798, None, "#fb923c", "Still different",
         "224 recorded differences"),
    )
    for position, (name, original, public, color, status, detail) in enumerate(entries):
        y = 390 + position * 113
        background = "#12283f" if name == "Rust" else "#111f30"
        width = round(416 * original / ORIGINAL)
        items += [
            f'<rect x="55" y="{y}" width="1369" height="98" rx="14" '
            f'fill="{background}"/>',
            f'<text x="75" y="{y + 38}" fill="#f8fafc" font-size="20" '
            f'font-family="system-ui,sans-serif" font-weight="710">{escape(name)}</text>',
            f'<rect x="188" y="{y + 16}" width="416" height="20" rx="7" '
            'fill="#293950"/>',
            f'<rect x="188" y="{y + 16}" width="{width}" height="20" '
            f'rx="7" fill="{color}"/>',
            f'<text x="188" y="{y + 68}" fill="#f8fafc" font-size="19" '
            'font-family="system-ui,sans-serif" font-weight="650">'
            f'{original:,} / {ORIGINAL:,}</text>',
            f'<text x="611" y="{y + 35}" fill="{color}" font-size="19" '
            f'font-family="system-ui,sans-serif" font-weight="750">'
            f'{percentage(original, ORIGINAL)}</text>',
        ]
        if public is None:
            items += [
                f'<rect x="794" y="{y + 16}" width="248" height="20" '
                'rx="7" fill="#293950"/>',
                f'<text x="794" y="{y + 68}" fill="#cbd5e1" font-size="15" '
                'font-family="system-ui,sans-serif">NOT MEASURED</text>',
            ]
        else:
            items += [
                f'<rect x="794" y="{y + 16}" width="248" height="20" '
                f'rx="7" fill="{color}"/>',
                f'<text x="794" y="{y + 68}" fill="#f8fafc" font-size="17" '
                'font-family="system-ui,sans-serif">'
                f'{public:,} / {PUBLIC:,}</text>',
            ]
        items += [
            f'<text x="1080" y="{y + 35}" fill="{color}" font-size="14" '
            f'font-family="system-ui,sans-serif" font-weight="740">'
            f'{escape(status)}</text>',
            f'<text x="1080" y="{y + 67}" fill="#e2e8f0" font-size="12" '
            f'font-family="system-ui,sans-serif">{escape(detail)}</text>',
        ]
    items += [
        '<rect x="55" y="863" width="1369" height="136" rx="17" '
        'fill="#2a1e28" stroke="#815269"/>',
        '<text x="80" y="899" fill="#fda4af" font-size="21" '
        'font-family="system-ui,sans-serif" font-weight="740">'
        'What still needs to happen?</text>',
        '<text x="81" y="934" fill="#f8fafc" font-size="16" '
        'font-family="system-ui,sans-serif">'
        'Finish C compatibility and Zig’s wider test. Prove each engine is independent. '
        'Then compare final speed against Python.</text>',
        '<text x="81" y="971" fill="#fcd34d" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'Qualified replacements: 0 of 3 required  ·  '
        'Final hidden speed: NOT MEASURED  ·  No winner</text>',
        '<text x="61" y="1046" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'Every percentage uses the same 31,237 original checks. '
        'The separate 10,434 checks do not change that total.</text>',
        '<text x="61" y="1076" fill="#94a3b8" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'C++, Go, and Fortran: complete compatibility results not available. '
        'All previous failures remain recorded.</text>',
        '</svg>',
    ]
    return ("\n".join(items) + "\n").encode("utf-8")


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
        "rust_original_percentage": "100%",
        "zig_verified_original_checks": ORIGINAL,
        "zig_observed_individual_mismatch_count": 0,
        "zig_completed_original_group_count": 13,
        "zig_original_percentage": "100%",
        "zig_broader_public_result": UNMEASURED,
        "zig_historical_verified_original_checks": 18_056,
        "zig_historical_individual_mismatch_count": 1_156,
        "c_verified_original_checks": 22_798,
        "c_observed_individual_mismatch_count": 224,
        "c_original_percentage": "73.0%",
        "c_historical_verified_original_checks": 16_413,
        "c_historical_individual_mismatch_count": 606,
        "c_corrected_source_build_status": "PASS",
        "c_corrected_source_build_count": 2,
        "c_corrected_matching_retest_status": "FAIL; 224 DIFFERENCES PRESERVED",
        "cpp_complete_original_result": UNMEASURED,
        "go_complete_original_result": UNMEASURED,
        "fortran_complete_original_result": UNMEASURED,
        "historical_v30_static_first_party_audit_status": "PASS",
        "historical_v30_external_regex_engine_count": 0,
        "historical_v30_external_regex_package_count": 0,
        "historical_v30_external_regex_symbol_count": 0,
        "historical_v30_native_engine_sha256": AUDITED_V30_ENGINE_SHA,
        "historical_v30_native_bridge_sha256": AUDITED_V30_BRIDGE_SHA,
        "historical_v30_adapter_sha256": AUDITED_V30_ADAPTER_SHA,
        "historical_v30_audit_build_differs_from_current_v33": True,
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
        "current_v33_external_regex_engine_count": "NOT ESTABLISHED",
        "current_v33_external_regex_package_count": "NOT ESTABLISHED",
        "current_v33_external_regex_symbol_count": "NOT ESTABLISHED",
        "superseded_v107_static_claim_falsified": True,
        "live_runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "final_hidden_speed": UNMEASURED,
        "winner_selected": False,
    }


def freeze(state: dict) -> dict:
    return {
        "schema": "rebar-updated-correctness-headline-v108-source-freeze",
        "version": VERSION,
        "status": "SOURCE FROZEN; UPDATED CORRECTNESS GRAPH NOT RENDERED",
        "goal_sha256": GOAL[1],
        "source": state["owners"][SOURCE],
        "protocol": state["owners"][PROTOCOL],
        "previous_overview": {
            name: state["owners"][owner[0]] for name, owner in PREVIOUS.items()
        },
        "actual_rust_original_receipt": state["owners"][ORIGINAL_RECEIPT[0]],
        "actual_rust_wider_receipt": state["owners"][PUBLIC_RECEIPT[0]],
        "historical_v30_rust_first_party_audit": state["owners"][AUDIT_RECEIPT[0]],
        "superseded_falsified_v107_freeze": {
            name: state["owners"][owner[0]]
            for name, owner in FALSIFIED_V107.items()
        },
        "actual_latest_zig_receipt": state["owners"][ZIG_RECEIPT[0]],
        "preserved_previous_zig_failure_receipt":
            state["owners"][ZIG_FAILURE_RECEIPT[0]],
        "actual_corrected_c_build_receipt": state["owners"][C_BUILD_RECEIPT[0]],
        "actual_latest_c_result_receipt": state["owners"][C_RESULT_RECEIPT[0]],
        "same_rust_build": {"engine_sha256": ENGINE_SHA,
                            "bridge_sha256": BRIDGE_SHA,
                            "adapter_sha256": ADAPTER_SHA},
        "historical_v30_audited_build": {
            "engine_sha256": AUDITED_V30_ENGINE_SHA,
            "bridge_sha256": AUDITED_V30_BRIDGE_SHA,
            "adapter_sha256": AUDITED_V30_ADAPTER_SHA,
            "publication_sha256": AUDITED_V30_PUBLICATION_SHA,
            "root_sha256": AUDITED_V30_ROOT_SHA,
        },
        "historical_v30_audit_build_differs_from_current_v33": True,
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
        "superseded_v107_static_claim_falsified": True,
        "headline": headline(),
        "original_case_execution_denominator": ORIGINAL,
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_counted_in_original_denominator": False,
        "qualified_candidate_count": 0,
        "candidate_qualified": False,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "final_hidden_speed": UNMEASURED,
        "winner_selected": False,
        "source_only_effects": effects(),
        "graph_publication": {
            "authorization": "ROOT-AUTHORIZED ONLY AFTER FROZEN COMMIT AND PUSH",
            "svg": OUTPUT + ".svg", "inputs": OUTPUT + ".inputs.json",
            "summary": OUTPUT + ".json", "actual_graph_rendered": False,
            "existing_graphs_mutated": False,
        },
    }


def graph(state: dict, source_sha: str, source_size: int,
          contract_sha: str, contract_size: int) -> dict:
    common = {
        "version": VERSION,
        "actual_current_graph_predecessor_version": 104,
        "goal_sha256": GOAL[1],
        "python": "3.14.6",
        "source": {"path": SOURCE, "sha256": source_sha, "bytes": source_size},
        "protocol": state["owners"][PROTOCOL],
        "contract": {"path": CONTRACT, "sha256": contract_sha,
                     "bytes": contract_size},
        "previous_overview": {name: reference(owner)
                              for name, owner in PREVIOUS.items()},
        "superseded_falsified_v107_freeze": {
            name: reference(owner) for name, owner in FALSIFIED_V107.items()
        },
        "rust_original_receipt": reference(ORIGINAL_RECEIPT),
        "rust_wider_receipt": reference(PUBLIC_RECEIPT),
        "historical_v30_rust_first_party_static_audit": reference(AUDIT_RECEIPT),
        "latest_zig_original_receipt": reference(ZIG_RECEIPT),
        "previous_zig_original_failure_receipt": reference(ZIG_FAILURE_RECEIPT),
        "corrected_c_build_receipt": reference(C_BUILD_RECEIPT),
        "latest_c_original_receipt": reference(C_RESULT_RECEIPT),
        "headline": headline(),
        "original_case_execution_denominator": ORIGINAL,
        "original_suite_count": len(SUITES),
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_counted_in_original_denominator": False,
        "same_exact_rust_build_verified": True,
        "same_exact_native_engine_sha256": ENGINE_SHA,
        "same_exact_native_bridge_sha256": BRIDGE_SHA,
        "same_exact_complete_adapter_sha256": ADAPTER_SHA,
        "historical_v30_static_first_party_non_delegation": "PASS",
        "historical_v30_native_engine_sha256": AUDITED_V30_ENGINE_SHA,
        "historical_v30_native_bridge_sha256": AUDITED_V30_BRIDGE_SHA,
        "historical_v30_adapter_sha256": AUDITED_V30_ADAPTER_SHA,
        "historical_v30_audit_build_differs_from_current_v33": True,
        "superseded_v107_static_claim_falsified": True,
        "static_first_party_non_delegation": "NOT ESTABLISHED",
        "live_runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "performance_measured_by_graph": UNMEASURED,
        "final_hidden_speed": UNMEASURED,
        "winner_selected": False,
        **effects(),
    }
    inputs = {**common, "schema": "rebar-candidate-current-overview-v108-inputs"}
    summary = {
        **common, "schema": "rebar-candidate-current-overview-v108-summary",
        "status": "PASS", "status_scope": "AUTHENTICATED CORRECTNESS GRAPH ONLY",
        "candidate_original_oracle_pass": True,
        "original_suite_correctness_qualified": True,
        "broader_public_correctness_pass": True,
        "candidate_qualified": False,
        "original_verified_passing_case_count": ORIGINAL,
        "original_semantic_mismatch_count": 0,
        "broader_public_verified_passing_case_count": PUBLIC,
        "broader_public_semantic_mismatch_count": 0,
        "latest_zig_verified_passing_case_count": ORIGINAL,
        "latest_zig_semantic_mismatch_count": 0,
        "latest_zig_completed_suite_count": 13,
        "latest_c_verified_passing_case_count": 22_798,
        "latest_c_semantic_mismatch_count": 224,
        "latest_c_completed_suite_count": 13,
        "historical_c_verified_passing_case_count": 16_413,
        "historical_c_semantic_mismatch_count": 606,
        "corrected_c_source_build_pass": True,
        "corrected_c_matching_retest": "FAIL; 224 DIFFERENCES PRESERVED",
        "rust_original_suite_results": state["original"]["suite_integrity"],
        "latest_zig_original_suite_results": state["zig"]["original_suite_diagnostics"],
        "latest_c_original_suite_results": state["c_result"]["suite_outcomes"],
        "historical_c_original_suite_results":
            state["previous_summary"]["preserved_c_original_suite_results"],
        "historical_zig_verified_passing_case_count": 18_056,
        "historical_zig_observed_mismatch_count": 1_156,
        "older_historical_zig_verified_passing_case_count": 4_607,
        "older_historical_zig_observed_mismatch_lower_bound": 1_700,
        "historical_previous_rust_original_mismatch_count": 1_352,
        "historical_previous_rust_public_mismatch_count": 1_145,
    }
    return {"svg": image(), "inputs": canonical(inputs),
            "summary": canonical(summary)}


def validate_graph(state: dict, result: dict, source_sha: str,
                   source_size: int, contract_sha: str, contract_size: int) -> None:
    require(result == graph(state, source_sha, source_size, contract_sha,
                            contract_size), "graph generation must be deterministic")
    inputs = document(result["inputs"], "graph inputs")
    summary = document(result["summary"], "graph summary")
    require(inputs["headline"] == summary["headline"],
            "the generated inputs and final summary disagree")
    same(summary, {
        "version": VERSION, "original_case_execution_denominator": ORIGINAL,
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_counted_in_original_denominator": False,
        "same_exact_rust_build_verified": True,
        "original_verified_passing_case_count": ORIGINAL,
        "original_semantic_mismatch_count": 0,
        "broader_public_verified_passing_case_count": PUBLIC,
        "broader_public_semantic_mismatch_count": 0,
        "latest_zig_verified_passing_case_count": ORIGINAL,
        "latest_zig_semantic_mismatch_count": 0,
        "latest_zig_completed_suite_count": 13,
        "latest_c_verified_passing_case_count": 22_798,
        "latest_c_semantic_mismatch_count": 224,
        "latest_c_completed_suite_count": 13,
        "historical_c_verified_passing_case_count": 16_413,
        "historical_c_semantic_mismatch_count": 606,
        "corrected_c_source_build_pass": True,
        "corrected_c_matching_retest": "FAIL; 224 DIFFERENCES PRESERVED",
        "historical_v30_static_first_party_non_delegation": "PASS",
        "historical_v30_native_engine_sha256": AUDITED_V30_ENGINE_SHA,
        "historical_v30_native_bridge_sha256": AUDITED_V30_BRIDGE_SHA,
        "historical_v30_adapter_sha256": AUDITED_V30_ADAPTER_SHA,
        "historical_v30_audit_build_differs_from_current_v33": True,
        "superseded_v107_static_claim_falsified": True,
        "static_first_party_non_delegation": "NOT ESTABLISHED",
        "live_runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False, "qualified_candidate_count": 0,
        "performance_measured_by_graph": UNMEASURED,
        "final_hidden_speed": UNMEASURED, "winner_selected": False,
        "candidate_workers_started_by_graph": 0,
        "holdout_cases_opened_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
    }, "preserve every actual result without implying final qualification")
    same(summary.get("headline"), {
        "historical_v30_static_first_party_audit_status": "PASS",
        "historical_v30_external_regex_engine_count": 0,
        "historical_v30_external_regex_package_count": 0,
        "historical_v30_external_regex_symbol_count": 0,
        "historical_v30_native_engine_sha256": AUDITED_V30_ENGINE_SHA,
        "historical_v30_native_bridge_sha256": AUDITED_V30_BRIDGE_SHA,
        "historical_v30_adapter_sha256": AUDITED_V30_ADAPTER_SHA,
        "historical_v30_audit_build_differs_from_current_v33": True,
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
        "current_v33_external_regex_engine_count": "NOT ESTABLISHED",
        "current_v33_external_regex_package_count": "NOT ESTABLISHED",
        "current_v33_external_regex_symbol_count": "NOT ESTABLISHED",
        "superseded_v107_static_claim_falsified": True,
        "live_runtime_non_delegation": "NOT ESTABLISHED",
    }, "never attribute the older V30 inspection to the passing V33 build")
    for text in (
        b'role="img"', b'aria-labelledby="title description"',
        b"How close are we to a faster Python re?",
        b"This picture measures matching Python correctly. It does not measure speed.",
        b"Rust and Zig both pass the complete original test",
        b"31,237 / 31,237 checks each",
        b"Rust also passes 10,434 / 10,434 wider checks.",
        b"Independence still needs proof",
        b"Current Rust audit: NOT ESTABLISHED",
        b"Older Rust build passed inspection",
        b"22,798 / 31,237", b"73.0%", b"224 recorded differences",
        b"All original checks pass", b"Wider test not measured",
        b"Qualified replacements: 0 of 3 required",
        b"Final hidden speed: NOT MEASURED", b"No winner",
    ):
        require(text in result["svg"],
                "the accessible plain-language graph omitted: " + text.decode("ascii"))
    for forbidden in (b"141557760", b"141,557,760", b"226492416", b"226,492,416"):
        require(all(forbidden not in result[name]
                    for name in ("svg", "inputs", "summary")),
                "never reveal private final-test proposal details")


def changed(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + " CHANGED"
    if type(value) is list:
        return value + ["CHANGED"]
    if type(value) is dict:
        return {**value, "__v108_hostile": True}
    if value is None:
        return "CHANGED"
    raise Rejected("unsupported hostile evidence mutation")


def controls(state: dict, output: dict, source_sha: str, source_size: int,
             contract_sha: str, contract_size: int) -> int:
    rejected = []

    def context_rejected(label: str, change) -> None:
        hostile = copy.deepcopy(state)
        change(hostile)
        try:
            verify(hostile)
        except (Rejected, TypeError, ValueError, KeyError, IndexError):
            rejected.append(label)
            return
        raise Rejected("unsafe correctness evidence was accepted: " + label)

    for owner in ("previous_inputs", "previous_summary", "falsified_v107_contract",
                  "original", "public",
                  "audit", "zig", "zig_previous", "c_build", "c_result"):
        for field in sorted(state[owner]):
            context_rejected(owner + ": " + field,
                             lambda hostile, name=owner, key=field:
                                 hostile[name].__setitem__(
                                     key, changed(hostile[name][key])))
    for owner in ("falsified_v107_source", "falsified_v107_protocol"):
        context_rejected(owner + " changed immutable history",
                         lambda hostile, name=owner:
                             hostile.__setitem__(name, hostile[name] + b"CHANGED"))
    for phase in range(2):
        for native, replacement in ((0, ENGINE_SHA), (1, BRIDGE_SHA)):
            context_rejected(
                "older V30 phase " + str(phase) + " native " + str(native)
                + " falsely attributed to V33",
                lambda hostile, phase_index=phase, native_index=native,
                       current=replacement:
                    hostile["audit"]["phases"][phase_index]["native_outputs"]
                           [native_index]["owner"].__setitem__("sha256", current))
        context_rejected(
            "older V30 phase " + str(phase) + " adapter falsely attributed to V33",
            lambda hostile, phase_index=phase:
                hostile["audit"]["phases"][phase_index]["sources"]
                       ["candidates/rust_candidate.py"]["owner"].__setitem__(
                           "sha256", ADAPTER_SHA))
    for key, replacement in (("publication_owner", BUILD_SHA),
                             ("root_provenance_owner", ROOT_SHA)):
        context_rejected(
            "older V30 " + key + " falsely attributed to V33",
            lambda hostile, name=key, current=replacement:
                hostile["audit"]["authenticated_v30"][name].__setitem__(
                    "sha256", current))
    for name, rows_key, worker_key in (("original", "suite_integrity", "pid"),
                                       ("zig", "original_suite_diagnostics", "pid"),
                                       ("zig_previous", "original_suite_diagnostics", "pid"),
                                       ("c_result", "suite_outcomes", "worker_process_id")):
        for number in range(len(SUITES)):
            context_rejected(name + " omitted worker " + str(number),
                             lambda hostile, owner=name, key=rows_key, index=number:
                                 hostile[owner][key].pop(index))
            for field in ("suite", "case_execution_denominator", worker_key):
                context_rejected(
                    name + " worker " + str(number) + " " + field,
                    lambda hostile, owner=name, key=rows_key, index=number,
                           item=field: hostile[owner][key][index].__setitem__(
                               item, changed(hostile[owner][key][index][item])))

    def output_rejected(label: str, name: str, change) -> None:
        hostile = dict(output)
        content = document(hostile[name], "hostile graph output")
        change(content)
        hostile[name] = canonical(content)
        try:
            validate_graph(state, hostile, source_sha, source_size,
                           contract_sha, contract_size)
        except (Rejected, TypeError, ValueError, KeyError, IndexError):
            rejected.append(label)
            return
        raise Rejected("a dishonest correctness headline was accepted: " + label)

    for name in ("inputs", "summary"):
        for field, value in (
            ("original_case_execution_denominator", ORIGINAL + PUBLIC),
            ("broader_public_case_execution_denominator", PUBLIC - 1),
            ("broader_public_counted_in_original_denominator", True),
            ("same_exact_rust_build_verified", False),
            ("static_first_party_non_delegation", "PASS"),
            ("historical_v30_static_first_party_non_delegation", "FAIL"),
            ("historical_v30_audit_build_differs_from_current_v33", False),
            ("superseded_v107_static_claim_falsified", False),
            ("live_runtime_non_delegation", "ESTABLISHED"),
            ("qualified_candidate_count", 1),
            ("performance_measured_by_graph", "2x"),
            ("final_hidden_speed", "2x"),
            ("hidden_cases_read_by_graph", 1),
            ("holdout_cases_opened_by_graph", 1),
            ("candidate_workers_started_by_graph", 1),
            ("winner_selected", True),
        ):
            output_rejected(name + " " + field, name,
                            lambda content, key=field, replacement=value:
                                content.__setitem__(key, replacement))
        for field, value in (
            ("current_v33_static_first_party_non_delegation", "PASS"),
            ("current_v33_external_regex_engine_count", 0),
            ("current_v33_external_regex_package_count", 0),
            ("current_v33_external_regex_symbol_count", 0),
            ("historical_v30_audit_build_differs_from_current_v33", False),
            ("superseded_v107_static_claim_falsified", False),
        ):
            output_rejected(name + " headline " + field, name,
                            lambda content, key=field, replacement=value:
                                content["headline"].__setitem__(key, replacement))
    for field, value in (
        ("candidate_qualified", True),
        ("latest_zig_verified_passing_case_count", 18_056),
        ("latest_zig_semantic_mismatch_count", 1_156),
        ("latest_c_verified_passing_case_count", 31_237),
        ("latest_c_semantic_mismatch_count", 0),
        ("historical_c_semantic_mismatch_count", 0),
        ("corrected_c_matching_retest", "PASS"),
        ("corrected_c_source_build_pass", False),
    ):
        output_rejected("summary " + field, "summary",
                        lambda content, key=field, replacement=value:
                            content.__setitem__(key, replacement))

    def wall_rejected(label: str, event: str, arguments: tuple) -> None:
        try:
            state["wall"].check(event, arguments)
        except Rejected:
            rejected.append(label)
            return
        raise Rejected("the source-only wall allowed " + label)

    for label, path in (
        ("candidate source", ROOT + "/candidates/rust_candidate.py"),
        ("native binary", ROOT + "/candidates/_rust_engine.so"),
        ("private build root", "/tmp/rebar-phase2-native-build-v33-private"),
        ("compressed original archive", ROOT + "/oracle/phase2/evidence/original.gz"),
        ("final proposal", ROOT + "/oracle/phase3/expanded-sealed-holdout-v3.json"),
        ("hidden seed", ROOT + "/oracle/phase3/final.seed"),
        ("hidden cases", ROOT + "/oracle/phase3/final-hidden.json"),
        ("unrelated benchmark", ROOT + "/performance/public.json"),
    ):
        wall_rejected(label, "open", (path, None, os.O_RDONLY | os.O_NOFOLLOW))
    for label, event, arguments in (
        ("candidate process", "subprocess.Popen", (PYTHON,)),
        ("native loader", "ctypes.dlopen", ("engine.so",)),
        ("candidate import", "import", ("candidates.rust_candidate",)),
        ("stdlib regex import", "import", ("re",)),
        ("archive import", "import", ("gzip",)),
        ("benchmark timer", "time.perf_counter", ()),
        ("network", "socket.connect", ("example.invalid",)),
        ("thread", "_thread.start_new_thread", ()),
        ("rename", "os.rename", ("old", "new")),
    ):
        wall_rejected(label, event, arguments)
    require(len(rejected) >= 500,
            "require comprehensive evidence, candidate, and final-test controls")
    return len(rejected)


def exclusive(path: str, payload: bytes) -> None:
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        position = 0
        while position < len(payload):
            count = os.write(descriptor, payload[position:])
            require(count > 0, "exclusive graph publication stopped")
            position += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def valid_commit(value: object, name: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(item in "0123456789abcdef" for item in value),
            "require the actual frozen and pushed source commit: " + name)
    return value


def arguments() -> argparse.Namespace:
    flags = [item for item in sys.argv[1:] if item.startswith("--")]
    require(len(flags) == len(set(flags)), "reject repeated flags or digest pins")
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
    for name in ("source", "inputs", "summary", "svg"):
        parser.add_argument("--previous-" + name + "-sha256", required=True)
    for name in ("original", "public", "audit", "zig", "zig-previous",
                 "c-build", "c-result"):
        parser.add_argument("--" + name + "-receipt-sha256", required=True)
    parser.add_argument("--root-authorized", action="store_true")
    parser.add_argument("--frozen-committed-pushed", action="store_true")
    parser.add_argument("--frozen-commit")
    parser.add_argument("--pushed-commit")
    result = parser.parse_args()
    if result.render_contract:
        require(result.contract_sha256 is None and result.contract_bytes is None
                and result.root_authorized is False
                and result.frozen_committed_pushed is False
                and result.frozen_commit is None and result.pushed_commit is None,
                "contract generation cannot have graph publication authority")
    elif result.render_graph:
        require(result.contract_sha256 is not None
                and result.contract_bytes is not None
                and result.root_authorized is True
                and result.frozen_committed_pushed is True
                and valid_commit(result.frozen_commit, "frozen")
                    == valid_commit(result.pushed_commit, "pushed"),
                "only root can render after the source is committed and pushed")
    else:
        require(result.contract_sha256 is not None
                and result.contract_bytes is not None
                and result.root_authorized is False
                and result.frozen_committed_pushed is False
                and result.frozen_commit is None and result.pushed_commit is None,
                "source-only verification cannot have graph publication authority")
    return result


def context(options: argparse.Namespace) -> dict:
    require(type(options.source_bytes) is int and 1 <= options.source_bytes <= 262_144
            and type(options.protocol_bytes) is int
            and 1 <= options.protocol_bytes <= 65_536,
            "require independently supplied complete source and protocol sizes")
    source = (SOURCE, sha(options.source_sha256, "renderer"), options.source_bytes)
    protocol = (PROTOCOL, sha(options.protocol_sha256, "protocol"),
                options.protocol_bytes)
    for name, owner in PREVIOUS.items():
        require(getattr(options, "previous_" + name + "_sha256") == owner[1],
                "the actual V104 predecessor digest changed: " + name)
    for name, owner in (("original", ORIGINAL_RECEIPT), ("public", PUBLIC_RECEIPT),
                        ("audit", AUDIT_RECEIPT), ("zig", ZIG_RECEIPT),
                        ("zig_previous", ZIG_FAILURE_RECEIPT),
                        ("c_build", C_BUILD_RECEIPT),
                        ("c_result", C_RESULT_RECEIPT)):
        require(getattr(options, name + "_receipt_sha256") == owner[1],
                "independently pin every complete actual public receipt: " + name)
    owners = (*OWNERS, source, protocol)
    contract = None
    if options.contract_sha256 is not None:
        require(type(options.contract_bytes) is int
                and 1 <= options.contract_bytes <= 262_144,
                "independently pin the complete source contract size")
        contract = (CONTRACT, sha(options.contract_sha256, "contract"),
                    options.contract_bytes)
        owners = (*owners, contract)
    mode = "contract" if options.render_contract else (
        "graph" if options.render_graph else "source")
    wall = SourceWall(mode, owners)
    sys.addaudithook(wall.check)
    metadata, payloads = {}, {}
    for owner in owners:
        identity, content = read(owner, owners)
        metadata[owner[0]], payloads[owner[0]] = identity, content
    result = {
        "options": options, "wall": wall, "owners": metadata,
        "goal": payloads[GOAL[0]],
        "previous_inputs": document(payloads[PREVIOUS["inputs"][0]], "V104 inputs"),
        "previous_summary": document(payloads[PREVIOUS["summary"][0]], "V104 summary"),
        "previous_svg": payloads[PREVIOUS["svg"][0]],
        "falsified_v107_source": payloads[FALSIFIED_V107["source"][0]],
        "falsified_v107_protocol": payloads[FALSIFIED_V107["protocol"][0]],
        "falsified_v107_contract": document(
            payloads[FALSIFIED_V107["contract"][0]],
            "preserved and falsified V107 source contract"),
        "original": document(payloads[ORIGINAL_RECEIPT[0]], "Rust original PASS"),
        "public": document(payloads[PUBLIC_RECEIPT[0]], "Rust wider PASS"),
        "audit": document(payloads[AUDIT_RECEIPT[0]],
                          "historical V30-only first-party static audit"),
        "zig": document(payloads[ZIG_RECEIPT[0]], "actual complete original Zig PASS"),
        "zig_previous": document(payloads[ZIG_FAILURE_RECEIPT[0]],
                                 "preserved previous Zig failure"),
        "c_build": document(payloads[C_BUILD_RECEIPT[0]], "actual C source build"),
        "c_result": document(payloads[C_RESULT_RECEIPT[0]], "actual complete C failure"),
    }
    if contract is not None:
        result["contract"] = document(payloads[CONTRACT], "V108 source contract")
    verify(result)
    if contract is not None:
        require(result["contract"] == freeze(result),
                "reject a stale, incomplete, or dishonest source contract")
    return result


def report(state: dict, count: int) -> dict:
    options = state["options"]
    return {
        "schema": "rebar-updated-correctness-headline-v108-source-result",
        "version": VERSION, "status": "PASS",
        "mode": "SELF-TEST" if options.self_test else (
            "GRAPH RENDER" if options.render_graph else "FROZEN CONTEXT"),
        "same_exact_rust_build_verified": True,
        "rust_original_verified_passing_case_count": ORIGINAL,
        "rust_wider_verified_passing_case_count": PUBLIC,
        "latest_zig_verified_passing_case_count": ORIGINAL,
        "latest_zig_semantic_mismatch_count": 0,
        "preserved_previous_zig_verified_passing_case_count": 18_056,
        "preserved_previous_zig_semantic_mismatch_count": 1_156,
        "latest_c_verified_passing_case_count": 22_798,
        "latest_c_semantic_mismatch_count": 224,
        "historical_c_verified_passing_case_count": 16_413,
        "historical_c_semantic_mismatch_count": 606,
        "corrected_c_source_build_status": "PASS",
        "corrected_c_matching_retest": "FAIL; 224 DIFFERENCES PRESERVED",
        "historical_v30_static_first_party_non_delegation": "PASS",
        "historical_v30_native_engine_sha256": AUDITED_V30_ENGINE_SHA,
        "historical_v30_native_bridge_sha256": AUDITED_V30_BRIDGE_SHA,
        "historical_v30_adapter_sha256": AUDITED_V30_ADAPTER_SHA,
        "historical_v30_audit_build_differs_from_current_v33": True,
        "superseded_v107_static_claim_falsified": True,
        "static_first_party_non_delegation": "NOT ESTABLISHED",
        "live_runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "hostile_controls_rejected": count,
        "final_hidden_speed": UNMEASURED,
        "winner_selected": False,
        **effects(),
    }


def main() -> int:
    options = arguments()
    require(sys.executable == PYTHON and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.no_site == 1
            and sys.flags.dont_write_bytecode == 1,
            "require the pinned isolated, no-site CPython 3.14.6 executable")
    state = context(options)
    if options.render_contract:
        os.write(1, canonical(freeze(state)))
        return 0
    output = graph(state, options.source_sha256, options.source_bytes,
                   options.contract_sha256, options.contract_bytes)
    validate_graph(state, output, options.source_sha256, options.source_bytes,
                   options.contract_sha256, options.contract_bytes)
    rejected = (controls(state, output, options.source_sha256, options.source_bytes,
                         options.contract_sha256, options.contract_bytes)
                if options.self_test else 0)
    if options.render_graph:
        for name, suffix in (("svg", ".svg"), ("inputs", ".inputs.json"),
                             ("summary", ".json")):
            exclusive(OUTPUT + suffix, output[name])
    result = report(state, rejected)
    if options.render_graph:
        result.update({name + "_sha256": digest(value)
                       for name, value in output.items()})
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Rejected, OSError, TypeError, ValueError, KeyError, IndexError) as failure:
        print("updated-correctness-headline-v108: " + str(failure), file=sys.stderr)
        raise SystemExit(1)
