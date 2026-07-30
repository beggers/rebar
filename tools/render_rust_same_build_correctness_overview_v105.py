#!/usr/bin/env python3
"""Freeze and render only an actually observed same-build Rust correctness PASS."""

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
SOURCE = "tools/render_rust_same_build_correctness_overview_v105.py"
PROTOCOL = "oracle/phase2/RUST-SAME-BUILD-CORRECTNESS-OVERVIEW-V105.md"
CONTRACT = "oracle/phase2/rust-same-build-correctness-overview-v105.json"
OUTPUT = "docs/evidence/candidate-current-overview-v105"
VERSION = 105
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
ORIGINAL_RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v33-rust-full-public-semantic-source-root-provenance-original-"
    "p0-v28-publication-receipt.json",
    "5204823a291ec01890913218582ff978cbe923dd5c787c8d6ae68a9790c43064",
    12_067,
)
ENGINE_SHA = "e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8"
BRIDGE_SHA = "ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000"
ADAPTER_SHA = "f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227"
V33_BUILD_RECEIPT_SHA = "cfe1464e1e8ce96bfa514b15cf96879a0642686987159dd79c15f4d9db408749"
V33_ROOT_RECEIPT_SHA = "7122c9bdff731be0f68602a4a216c1fa9700e6a78f9da9b534eeaef282c64c1c"
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1_024), ("buffer_v3", 768),
    ("managed_v1", 1_024), ("scanner_verbose_v1", 2_854),
    ("public_types_v1", 6_912), ("substitution_v2", 5_120),
    ("shape_v2", 10_240), ("public_surface_v19", 1_376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)


class Rejected(ValueError):
    """A same-build claim, immutable owner, or physical source wall changed."""


def require(condition: object, reason: str) -> None:
    if condition is not True:
        raise Rejected(reason)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha(value: object, name: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value),
            "require a complete independent lowercase SHA-256: " + name)
    return value


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, allow_nan=False,
                   sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")


def unique(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "reject duplicate same-build evidence JSON fields")
        result[key] = value
    return result


def document(payload: bytes, name: str) -> dict:
    try:
        value = json.loads(
            payload, object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                Rejected("reject nonfinite same-build evidence")),
        )
    except (TypeError, ValueError, UnicodeError) as failure:
        raise Rejected("reject malformed same-build evidence: " + name) from failure
    require(type(value) is dict and canonical(value) == payload,
            "reject incomplete or noncanonical same-build evidence: " + name)
    return value


def same(actual: object, expected: dict, label: str) -> None:
    require(type(actual) is dict,
            "require a complete authenticated same-build object: " + label)
    for key, value in expected.items():
        require(actual.get(key) == value,
                "same-build evidence changed: " + label + ": " + key)


def reference(owner: tuple[str, str, int]) -> dict:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2]}


def original_owner(path: object, fingerprint: object,
                   count: object) -> tuple[str, str, int]:
    require(type(path) is str and path == ORIGINAL_RECEIPT[0]
            and sha(fingerprint, "same-build original receipt")
            == ORIGINAL_RECEIPT[1]
            and type(count) is int and count == ORIGINAL_RECEIPT[2],
            "accept only the exact genuinely published V28/V33 same-build PASS")
    return ORIGINAL_RECEIPT


def rows(receipt: tuple[str, str, int]) -> tuple[tuple[str, str, int], ...]:
    return (GOAL, *PREVIOUS.values(), PUBLIC_RECEIPT, AUDIT_RECEIPT, receipt)


class SourceWall:
    """Permit exact public plaintext evidence and exclusively owned new outputs."""

    def __init__(self, mode: str, owners: tuple[tuple[str, str, int], ...]):
        self.mode = mode
        self.approved = frozenset(os.path.join(ROOT, owner[0]) for owner in owners)
        self.contract_output = os.path.join(ROOT, CONTRACT)
        self.graph_outputs = frozenset(os.path.join(ROOT, OUTPUT + extension)
                                       for extension in (".svg", ".inputs.json", ".json"))

    def check(self, event: str, arguments: tuple) -> None:
        if event == "open":
            target = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 and type(arguments[2]) is int else 0
            require(type(target) is str,
                    "reject descriptor, relative, private, or candidate file access")
            writable = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                                     | os.O_APPEND | os.O_TRUNC))
            if writable:
                required = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                allowed = (self.mode == "graph" and target in self.graph_outputs)
                require(allowed and flags & required == required,
                        "reject unapproved or nonexclusive same-build artifact mutation")
            else:
                require(target in self.approved and flags & os.O_NOFOLLOW != 0,
                        "reject candidate, native, proposal, seed, archive, or hidden cases")
            return
        if (event.startswith(("subprocess.", "socket.", "ctypes.", "os.exec", "os.spawn"))
                or event in {
                    "os.system", "os.fork", "os.posix_spawn", "os.mkdir",
                    "os.remove", "os.rename", "os.rmdir", "os.chdir", "os.chmod",
                    "os.link", "os.symlink", "os.truncate", "os.putenv",
                    "time.time", "time.monotonic", "time.perf_counter",
                    "_thread.start_new_thread",
                }):
            raise Rejected("reject candidate execution, compiler, native load, "
                           "network, clock, thread, or unrelated mutation")
        if event == "import" and arguments:
            name = arguments[0]
            require(not (type(name) is str and (
                name in {"re", "_sre", "regex", "re2", "ctypes", "gzip"}
                or name.startswith(("candidates.", "rebar."))
            )), "reject regex engine, candidate, native, or archive import")


def read(owner: tuple[str, str, int], approved: tuple[tuple[str, str, int], ...]
         ) -> tuple[dict, bytes]:
    require(owner in approved, "reject unapproved same-build evidence owner")
    path, fingerprint, expected_size = owner
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_uid == os.getuid()
                and before.st_nlink == 1
                and before.st_size == expected_size,
                "same-build evidence owner identity changed: " + path)
        blocks = []
        while True:
            chunk = os.read(descriptor, 1_048_576)
            if not chunk:
                break
            blocks.append(chunk)
        value = b"".join(blocks)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_uid, before.st_nlink, before.st_mtime_ns,
                 before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_uid, after.st_nlink, after.st_mtime_ns,
                    after.st_ctime_ns)
                and digest(value) == fingerprint,
                "complete same-build evidence digest changed: " + path)
        return ({"path": path, "sha256": fingerprint, "bytes": expected_size,
                 "device": after.st_dev, "inode": after.st_ino,
                 "uid": after.st_uid, "mode": "0600", "nlink": after.st_nlink}, value)
    finally:
        os.close(descriptor)


def verify_previous(state: dict) -> None:
    prior = state["previous_summary"]
    inputs = state["previous_inputs"]
    common = {
        "version": 104,
        "actual_current_graph_predecessor_version": 103,
        "goal_sha256": GOAL[1],
        "python": "3.14.6",
        "original_case_execution_denominator": ORIGINAL,
        "original_suite_count": 13,
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_counted_in_original_denominator": False,
        "static_first_party_non_delegation": "PASS",
        "live_runtime_no_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "timing_trials_run": 0,
        "holdout_proposal_files_opened_by_graph": 0,
        "holdout_proposal_files_statted_by_graph": 0,
        "holdout_cases_opened_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "winner_selected": False,
    }
    same(inputs, common, "immutable V104 graph inputs")
    same(prior, common, "immutable V104 graph publication")
    same(prior, {
        "schema": "rebar-candidate-current-overview-v104-summary",
        "status": "PASS",
        "rust_original_candidate_status": "PASS",
        "rust_broader_public_candidate_status": "PASS",
        "candidate_original_oracle_pass": True,
        "original_suite_correctness_qualified": True,
        "broader_public_suite_correctness_pass": True,
        "candidate_qualified": False,
        "original_verified_passing_case_count": ORIGINAL,
        "original_semantic_mismatch_count": 0,
        "broader_public_verified_passing_case_count": PUBLIC,
        "broader_public_semantic_mismatch_count": 0,
        "historical_c_original_observed_mismatch_count": 606,
        "historical_zig_original_observed_mismatch_lower_bound": 1_700,
    }, "preserve V104 family-level passes and every C/Zig loss")
    same(prior.get("headline"), {
        "python_verified_original_checks": ORIGINAL,
        "python_verified_broader_public_checks": PUBLIC,
        "rust_verified_original_checks": ORIGINAL,
        "rust_verified_broader_public_checks": PUBLIC,
        "c_verified_original_checks": 16_413,
        "c_observed_individual_mismatch_count": 606,
        "zig_verified_original_checks": 4_607,
        "zig_observed_individual_mismatch_lower_bound": 1_700,
        "zig_complete_original_mismatch_count": UNMEASURED,
        "rust_static_first_party_audit_status": "PASS",
        "rust_candidate_qualified": False,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "speed_relative_to_python": UNMEASURED,
    }, "retain all earlier measurements without claiming same-build equivalence")
    require(type(prior.get("complete_original_suite_results")) is list
            and len(prior["complete_original_suite_results"]) == len(SUITES)
            and type(prior.get("preserved_c_original_suite_results")) is list
            and len(prior["preserved_c_original_suite_results"]) == len(SUITES),
            "preserve every complete historical original Rust and C group")
    require(state["previous_svg"].startswith(b"<svg ")
            and b'role="img"' in state["previous_svg"]
            and b"31,237 / 31,237" in state["previous_svg"]
            and b"10,434 / 10,434" in state["previous_svg"]
            and b"606 differences" in state["previous_svg"]
            and b"At least 1,700 differences" in state["previous_svg"],
            "the whole previous V104 accessible graph was changed")


def verify_public(state: dict) -> None:
    public = state["public"]
    same(public, {
        "schema": "rebar-owned-rust-full-public-correctness-v5-durable-publication-receipt",
        "version": 5,
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "PASS",
        "candidate_qualified": False,
        "public_10434_correctness_status": "PASS",
        "public_10434_case_count": PUBLIC,
        "public_10434_verified_passing_case_count": PUBLIC,
        "public_10434_mismatch_count": 0,
        "all_public_cases_observed": True,
        "all_public_mismatches_preserved": True,
        "candidate_worker_count": 1,
        "reference_worker_count": 1,
        "v33_native_engine_sha256": ENGINE_SHA,
        "v33_native_bridge_sha256": BRIDGE_SHA,
        "v33_adapter_sha256": ADAPTER_SHA,
        "v33_publication_sha256": V33_BUILD_RECEIPT_SHA,
        "v33_root_sha256": V33_ROOT_RECEIPT_SHA,
        "v5_static_pass_sha256": AUDIT_RECEIPT[1],
        "v5_static_external_regex_library_count": 0,
        "v5_static_external_regex_package_count": 0,
        "v5_static_external_regex_symbol_count": 0,
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "timing_trials_run": 0,
        "proposal_content_opens": 0,
        "proposal_metadata_probes": 0,
        "hidden_cases_generated": 0,
        "hidden_cases_read": 0,
        "winner_selected": False,
    }, "bind every public PASS to its exact V33 first-party build identity")


def verify_audit(state: dict) -> None:
    audit = state["audit"]
    same(audit, {
        "schema": "rebar-phase2-clean-first-party-rust-non-delegation-v5-root-static-audit",
        "status": "PASS",
        "audited_family": "rust",
        "finding_count": 0,
        "findings": [],
        "external_regex_libraries": 0,
        "external_regex_packages": 0,
        "external_regex_symbols": 0,
        "cross_family_dependencies": 0,
        "clean_candidate_source_static_non_delegation": "PASS",
        "clean_candidate_native_elf_static_non_delegation": "PASS",
        "candidate_qualified": False,
        "candidate_executions": 0,
        "native_library_loads": 0,
        "runtime_non_delegation":
            "NOT ESTABLISHED; STATIC SOURCE AND ELF AUDIT ONLY",
        "performance": UNMEASURED,
        "winner_selected": False,
    }, "preserve static first-party evidence without inventing a live proof")


def exact_original_field(receipt: dict, names: tuple[str, ...], expected: str,
                         label: str) -> str:
    values = [(name, receipt[name]) for name in names if name in receipt]
    require(bool(values), "the same-build original receipt omitted " + label)
    require(all(value == expected for _, value in values),
            "original and public results do not use the same exact " + label)
    return expected


def verify_original(state: dict) -> None:
    receipt = state["original"]
    schema = receipt.get("schema")
    require(type(schema) is str
            and schema.startswith("rebar-owned-repaired-rust-original-campaign-v")
            and schema.endswith("-durable-publication-receipt"),
            "reject source-only, controller-failure, or unrelated original receipts")
    same(receipt, {
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "family": "rust",
        "candidate_status": "PASS",
        "candidate_original_oracle_pass": True,
        "original_suite_correctness_qualified": True,
        "candidate_qualified": False,
        "case_execution_denominator": ORIGINAL,
        "verified_passing_case_count": ORIGINAL,
        "semantic_mismatch_count": 0,
        "suite_count": len(SUITES),
        "completed_suite_count": len(SUITES),
        "started_suite_count": len(SUITES),
        "attempted_suite_count": len(SUITES),
        "actual_candidate_workers": len(SUITES),
        "distinct_worker_process_id_count": len(SUITES),
        "infrastructure_failure_count": 0,
        "worker_failure_capture_count": 0,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "all_original_observation_vectors_complete": True,
        "actual_v28_build_receipt_sha256": V33_BUILD_RECEIPT_SHA,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "undefined_behavior": UNMEASURED,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "hidden_cases_read": 0,
        "winner_selected": False,
    }, "accept only an actually executed, complete V33 original candidate PASS")
    exact_original_field(receipt,
                         ("native_engine_sha256", "actual_v33_native_engine_sha256"),
                         ENGINE_SHA, "native Rust engine")
    exact_original_field(receipt,
                         ("native_bridge_sha256", "actual_v33_native_bridge_sha256"),
                         BRIDGE_SHA, "native first-party Rust bridge")
    exact_original_field(receipt,
                         ("corrected_public_adapter_sha256", "v33_adapter_sha256",
                          "actual_v33_adapter_sha256"),
                         ADAPTER_SHA, "complete Rust Python adapter")
    for key, expected, label in (
        (("actual_v33_build_receipt_sha256", "actual_v33_build_publication_sha256",
          "v33_publication_sha256"), V33_BUILD_RECEIPT_SHA, "V33 source-build receipt"),
        (("actual_v33_root_receipt_sha256", "actual_v33_root_sha256",
          "v33_root_sha256"), V33_ROOT_RECEIPT_SHA, "V33 private-root provenance"),
    ):
        present = [(name, receipt[name]) for name in key if name in receipt]
        if present:
            require(all(value == expected for _, value in present),
                    "the independently published V33 build provenance changed: " + label)
    workers = receipt.get("actual_worker_process_ids")
    rows = receipt.get("suite_integrity")
    require(type(workers) is list and len(workers) == len(SUITES)
            and all(type(value) is int and value > 0 for value in workers)
            and len(set(workers)) == len(SUITES)
            and type(rows) is list and len(rows) == len(SUITES),
            "every original Rust group needs a distinct genuinely observed worker")
    for row, (name, denominator) in zip(rows, SUITES, strict=True):
        same(row, {
            "suite": name,
            "case_execution_denominator": denominator,
            "verified_passing_case_count": denominator,
            "mismatch_count": 0,
            "failure_class": "PASS",
            "fully_observed": True,
            "actual_worker_started": True,
            "worker_attempted": True,
            "returncode": 0,
        }, "complete same-build original suite " + name)
        require(row.get("pid") in workers,
                "each same-build original row requires its actual worker process")


def verify(state: dict) -> None:
    require(digest(state["goal"]) == GOAL[1],
            "the immutable user goal changed")
    for name, expected in (
        ("previous_inputs", PREVIOUS["inputs"][1]),
        ("previous_summary", PREVIOUS["summary"][1]),
        ("public", PUBLIC_RECEIPT[1]),
        ("audit", AUDIT_RECEIPT[1]),
        ("original", state["original_owner"][1]),
    ):
        require(digest(canonical(state[name])) == expected,
                "complete digest-bound same-build evidence changed: " + name)
    require(digest(state["previous_svg"]) == PREVIOUS["svg"][1],
            "the immutable complete V104 accessible graph changed")
    verify_previous(state)
    verify_public(state)
    verify_audit(state)
    verify_original(state)


def source_effects() -> dict:
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
        "compressed_archives_inflated_by_graph": 0,
        "raw_public_case_archives_opened_by_graph": 0,
        "raw_public_case_archives_statted_by_graph": 0,
        "holdout_proposal_files_opened_by_graph": 0,
        "holdout_proposal_files_statted_by_graph": 0,
        "seed_files_opened_by_graph": 0,
        "holdout_cases_opened_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "final_holdout_opened": False,
        "clock_samples_by_graph": 0,
        "timing_trials_run": 0,
    }


def freeze(state: dict) -> dict:
    return {
        "schema": "rebar-rust-same-build-correctness-overview-v105-source-freeze",
        "version": VERSION,
        "status": "SOURCE FROZEN; SAME-BUILD CORRECTNESS GRAPH NOT RENDERED",
        "goal_sha256": GOAL[1],
        "source": state["owners"][SOURCE],
        "protocol": state["owners"][PROTOCOL],
        "previous_overview": {
            name: state["owners"][item[0]] for name, item in PREVIOUS.items()
        },
        "actual_same_build_original_receipt": state["owners"][state["original_owner"][0]],
        "actual_same_build_public_receipt": state["owners"][PUBLIC_RECEIPT[0]],
        "static_first_party_pass_receipt": state["owners"][AUDIT_RECEIPT[0]],
        "same_build_identity": {
            "native_engine_sha256": ENGINE_SHA,
            "native_bridge_sha256": BRIDGE_SHA,
            "complete_adapter_sha256": ADAPTER_SHA,
            "v33_build_publication_sha256": V33_BUILD_RECEIPT_SHA,
            "v33_private_root_provenance_sha256": V33_ROOT_RECEIPT_SHA,
            "same_engine_verified_in_both_actual_receipts": True,
            "same_bridge_verified_in_both_actual_receipts": True,
            "same_adapter_verified_in_both_actual_receipts": True,
            "same_build_claim_requires_actual_original_candidate_pass": True,
        },
        "original_correctness": {
            "case_execution_denominator": ORIGINAL,
            "verified_passing_case_count": ORIGINAL,
            "semantic_mismatch_count": 0,
            "suite_count": len(SUITES),
            "distinct_real_worker_count": len(SUITES),
            "candidate_status": "PASS",
            "candidate_original_oracle_pass": True,
            "candidate_qualified": False,
        },
        "broader_public_correctness": {
            "case_execution_denominator": PUBLIC,
            "verified_passing_case_count": PUBLIC,
            "semantic_mismatch_count": 0,
            "candidate_status": "PASS",
            "counted_in_original_denominator": False,
            "candidate_qualified": False,
        },
        "preserved_historical_results": {
            "c_verified_original_checks": 16_413,
            "c_observed_individual_mismatch_count": 606,
            "c_incomplete_group_count": 1,
            "zig_verified_original_checks": 4_607,
            "zig_observed_individual_mismatch_lower_bound": 1_700,
            "zig_complete_original_mismatch_count": UNMEASURED,
            "previous_rust_original_mismatch_count": 1_352,
            "previous_rust_public_mismatch_count": 1_145,
        },
        "from_scratch_static_audit": {
            "status": "PASS",
            "external_regex_library_count": 0,
            "external_regex_package_count": 0,
            "external_regex_symbol_count": 0,
            "cross_family_engine_count": 0,
            "live_runtime_non_delegation": "NOT ESTABLISHED",
        },
        "graph_publication": {
            "authorization": "ROOT-AUTHORIZED ONLY AFTER FROZEN COMMIT AND PUSH",
            "svg": OUTPUT + ".svg",
            "inputs": OUTPUT + ".inputs.json",
            "summary": OUTPUT + ".json",
            "actual_graph_rendered": False,
            "existing_graphs_mutated": False,
        },
        "source_only_effects": source_effects(),
        "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "undefined_behavior": UNMEASURED,
        "winner_selected": False,
    }


def escape(value: object) -> str:
    text = str(value)
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def percentage(value: int, denominator: int) -> str:
    return "100%" if value == denominator else f"{100 * value / denominator:.1f}%"


def image() -> bytes:
    description = (
        "Correctness only, not speed. The exact same first-party Rust native "
        "engine, bridge, and Python adapter pass all 31,237 original Python "
        "checks and all 10,434 separate broader public checks, with zero "
        "differences in both. Python passes both. C passes 16,413 original "
        "checks with 606 observed differences and an unfinished group. Zig "
        "passes 4,607 original checks with at least 1,700 observed differences. "
        "Static source and native inspection found zero external regex engines, "
        "packages, or symbols. Live runtime independence remains unestablished; "
        "no candidate qualifies, final speed is unmeasured, and no winner exists."
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1510" height="1190" '
        'viewBox="0 0 1510 1190" role="img" aria-labelledby="title description">',
        '<title id="title">One Rust engine now matches Python re in both test sets</title>',
        f'<desc id="description">{escape(description)}</desc>',
        '<rect width="1510" height="1190" rx="24" fill="#0b1220"/>',
        '<text x="56" y="76" fill="#f8fafc" font-size="36" '
        'font-family="system-ui,sans-serif" font-weight="760">'
        'One Rust engine now matches Python re in both test sets</text>',
        '<text x="58" y="112" fill="#cbd5e1" font-size="18" '
        'font-family="system-ui,sans-serif">'
        'The same verified engine, bridge, and adapter passed both comparisons.</text>',
        '<rect x="55" y="140" width="1400" height="136" rx="16" '
        'fill="#10283a" stroke="#317266"/>',
        '<text x="81" y="180" fill="#6ee7b7" font-size="25" '
        'font-family="system-ui,sans-serif" font-weight="760">'
        'One exact from-scratch Rust build. Zero differences.</text>',
        '<text x="82" y="219" fill="#f8fafc" font-size="21" '
        'font-family="system-ui,sans-serif" font-weight="670">'
        '31,237 / 31,237 original checks  +  10,434 / 10,434 broader checks</text>',
        '<text x="82" y="252" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'Matching engine, native bridge, and Python adapter are identical in both runs.</text>',
        '<text x="69" y="314" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="690">APPROACH</text>',
        '<text x="178" y="314" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'ORIGINAL PYTHON CHECKS</text>',
        '<text x="657" y="314" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'BROADER PUBLIC CHECKS</text>',
        '<text x="1105" y="314" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="690">CURRENT STATUS</text>',
    ]
    entries = (
        ("Python re", ORIGINAL, PUBLIC, "#34d399", "REFERENCE", "All checks pass"),
        ("Rust", ORIGINAL, PUBLIC, "#60a5fa", "SAME BUILD PASSES BOTH",
         "Zero differences in both runs"),
        ("C", 16_413, None, "#fbbf24", "NOT COMPATIBLE",
         "606 differences; unfinished"),
        ("Zig", 4_607, None, "#fbbf24", "NOT COMPATIBLE",
         "At least 1,700 differences"),
        ("C++", None, None, "#94a3b8", UNMEASURED,
         "Complete checks not measured"),
        ("Go", None, None, "#94a3b8", UNMEASURED,
         "Complete checks not measured"),
        ("Fortran", None, None, "#94a3b8", UNMEASURED,
         "Complete checks not measured"),
    )
    for index, (name, first, second, color, status, detail) in enumerate(entries):
        top = 331 + index * 85
        background = "#11263d" if name == "Rust" else "#101b2b"
        parts += [
            f'<rect x="55" y="{top}" width="1400" height="73" rx="11" '
            f'fill="{background}"/>',
            f'<text x="74" y="{top + 36}" fill="#f8fafc" font-size="18" '
            f'font-family="system-ui,sans-serif" font-weight="690">'
            f'{escape(name)}</text>',
            f'<rect x="178" y="{top + 12}" width="257" height="17" rx="6" '
            'fill="#29384e"/>',
            f'<rect x="657" y="{top + 12}" width="226" height="17" rx="6" '
            'fill="#29384e"/>',
        ]
        if first is not None:
            parts.append(
                f'<rect x="178" y="{top + 12}" width="{round(257 * first / ORIGINAL)}" '
                f'height="17" rx="6" fill="{color}"/>'
            )
            first_text = f"{first:,} / {ORIGINAL:,}  ·  {percentage(first, ORIGINAL)}"
        else:
            first_text = UNMEASURED
        if second is not None:
            parts.append(
                f'<rect x="657" y="{top + 12}" width="{round(226 * second / PUBLIC)}" '
                f'height="17" rx="6" fill="{color}"/>'
            )
            second_text = f"{second:,} / {PUBLIC:,}  ·  {percentage(second, PUBLIC)}"
        else:
            second_text = UNMEASURED
        parts += [
            f'<text x="178" y="{top + 53}" fill="#e2e8f0" font-size="14" '
            f'font-family="system-ui,sans-serif">{escape(first_text)}</text>',
            f'<text x="657" y="{top + 53}" fill="#e2e8f0" font-size="14" '
            f'font-family="system-ui,sans-serif">{escape(second_text)}</text>',
            f'<text x="1104" y="{top + 30}" fill="{color}" font-size="11" '
            f'font-family="system-ui,sans-serif" font-weight="730">'
            f'{escape(status)}</text>',
            f'<text x="1104" y="{top + 53}" fill="#e2e8f0" font-size="12" '
            f'font-family="system-ui,sans-serif">{escape(detail)}</text>',
        ]
    parts += [
        '<rect x="55" y="949" width="678" height="157" rx="14" '
        'fill="#122536" stroke="#326459"/>',
        '<text x="77" y="982" fill="#6ee7b7" font-size="18" '
        'font-family="system-ui,sans-serif" font-weight="750">'
        'From scratch, with the same exact build</text>',
        '<text x="78" y="1014" fill="#f8fafc" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'Engine + native bridge + Python adapter: identical in both tests.</text>',
        '<text x="78" y="1044" fill="#e2e8f0" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'External regex engines: 0  ·  External regex packages: 0</text>',
        '<text x="78" y="1074" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'All earlier Rust, C, and Zig failures remain recorded.</text>',
        '<rect x="754" y="949" width="701" height="157" rx="14" '
        'fill="#291923" stroke="#754453"/>',
        '<text x="776" y="982" fill="#fda4af" font-size="19" '
        'font-family="system-ui,sans-serif" font-weight="750">'
        'Still required before a winner</text>',
        '<text x="776" y="1014" fill="#f8fafc" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'Live runtime independence: NOT ESTABLISHED.</text>',
        '<text x="776" y="1044" fill="#e2e8f0" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'Three independently built engines must pass all requirements.</text>',
        '<text x="776" y="1074" fill="#fcd34d" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'FINAL SPEED: NOT MEASURED  ·  NO WINNER</text>',
        '<text x="62" y="1147" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'The original and broader tests stay separate. The hidden final test '
        'has not been generated or opened.</text>',
        '</svg>',
    ]
    return ("\n".join(parts) + "\n").encode("utf-8")


def graph(state: dict, source_sha: str, source_bytes: int,
          contract_sha: str, contract_bytes: int) -> dict:
    previous = state["previous_summary"]
    headline = {
        "purpose": "Build a faster, fully compatible Python re from scratch.",
        "bars_measure": "SAME-BUILD ORIGINAL AND PUBLIC CORRECTNESS; NOT SPEED",
        "same_exact_rust_build_verified": True,
        "same_exact_native_engine_sha256": ENGINE_SHA,
        "same_exact_native_bridge_sha256": BRIDGE_SHA,
        "same_exact_complete_adapter_sha256": ADAPTER_SHA,
        "python_verified_original_checks": ORIGINAL,
        "python_verified_broader_public_checks": PUBLIC,
        "rust_verified_original_checks": ORIGINAL,
        "rust_original_mismatch_count": 0,
        "rust_verified_broader_public_checks": PUBLIC,
        "rust_broader_public_mismatch_count": 0,
        "rust_original_group_count": len(SUITES),
        "rust_distinct_original_worker_count": len(SUITES),
        "rust_broader_public_candidate_worker_count": 1,
        "rust_broader_public_reference_worker_count": 1,
        "c_verified_original_checks": 16_413,
        "c_observed_individual_mismatch_count": 606,
        "c_incomplete_original_group_count": 1,
        "zig_verified_original_checks": 4_607,
        "zig_observed_mismatch_lower_bound": 1_700,
        "zig_complete_original_mismatch_count": UNMEASURED,
        "cpp_verified_original_checks": UNMEASURED,
        "go_verified_original_checks": UNMEASURED,
        "fortran_verified_original_checks": UNMEASURED,
        "static_first_party_audit_status": "PASS",
        "external_regex_engine_count": 0,
        "external_regex_package_count": 0,
        "external_regex_symbol_count": 0,
        "cross_candidate_engine_count": 0,
        "live_runtime_non_delegation": "NOT ESTABLISHED",
        "rust_candidate_qualified": False,
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "speed_relative_to_python": UNMEASURED,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "winner_selected": False,
    }
    common = {
        "version": VERSION,
        "actual_current_graph_predecessor_version": 104,
        "goal_sha256": GOAL[1],
        "python": "3.14.6",
        "original_case_execution_denominator": ORIGINAL,
        "original_suite_count": len(SUITES),
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_counted_in_original_denominator": False,
        "same_exact_rust_build_verified": True,
        "same_exact_native_engine_sha256": ENGINE_SHA,
        "same_exact_native_bridge_sha256": BRIDGE_SHA,
        "same_exact_complete_adapter_sha256": ADAPTER_SHA,
        "source": {"path": SOURCE, "sha256": source_sha, "bytes": source_bytes},
        "protocol": state["owners"][PROTOCOL],
        "contract": {"path": CONTRACT, "sha256": contract_sha, "bytes": contract_bytes},
        "previous_overview": {
            name: reference(item) for name, item in PREVIOUS.items()
        },
        "same_build_original_receipt": reference(state["original_owner"]),
        "same_build_public_receipt": reference(PUBLIC_RECEIPT),
        "static_first_party_audit_receipt": reference(AUDIT_RECEIPT),
        "headline": headline,
        **source_effects(),
        "static_first_party_non_delegation": "PASS",
        "live_runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "undefined_behavior": UNMEASURED,
        "winner_selected": False,
    }
    inputs = {**common, "schema": "rebar-candidate-current-overview-v105-inputs"}
    summary = {
        **common,
        "schema": "rebar-candidate-current-overview-v105-summary",
        "status": "PASS",
        "status_scope": "AUTHENTICATED SAME-BUILD CORRECTNESS GRAPH ONLY",
        "candidate_original_oracle_pass": True,
        "original_suite_correctness_qualified": True,
        "broader_public_correctness_pass": True,
        "candidate_qualified": False,
        "original_verified_passing_case_count": ORIGINAL,
        "original_semantic_mismatch_count": 0,
        "broader_public_verified_passing_case_count": PUBLIC,
        "broader_public_semantic_mismatch_count": 0,
        "complete_same_build_original_suite_results":
            state["original"]["suite_integrity"],
        "previous_complete_original_suite_results":
            previous["complete_original_suite_results"],
        "preserved_c_original_suite_results":
            previous["preserved_c_original_suite_results"],
        "historical_c_observed_mismatch_count": 606,
        "historical_zig_observed_mismatch_lower_bound": 1_700,
        "historical_zig_complete_mismatch_count": UNMEASURED,
        "historical_previous_rust_original_mismatch_count": 1_352,
        "historical_previous_rust_public_mismatch_count": 1_145,
    }
    return {"svg": image(), "inputs": canonical(inputs),
            "summary": canonical(summary)}


def validate_graph(state: dict, result: dict, source_sha: str,
                   source_bytes: int, contract_sha: str,
                   contract_bytes: int) -> None:
    require(result == graph(state, source_sha, source_bytes,
                            contract_sha, contract_bytes),
            "the same-build public graph is not fully deterministic")
    inputs = document(result["inputs"], "same-build graph inputs")
    summary = document(result["summary"], "same-build graph summary")
    require(inputs["headline"] == summary["headline"]
            and inputs["previous_overview"] == summary["previous_overview"],
            "same-build graph inputs and summary disagree")
    same(summary, {
        "version": VERSION,
        "original_case_execution_denominator": ORIGINAL,
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_counted_in_original_denominator": False,
        "same_exact_rust_build_verified": True,
        "same_exact_native_engine_sha256": ENGINE_SHA,
        "same_exact_native_bridge_sha256": BRIDGE_SHA,
        "same_exact_complete_adapter_sha256": ADAPTER_SHA,
        "candidate_original_oracle_pass": True,
        "original_suite_correctness_qualified": True,
        "broader_public_correctness_pass": True,
        "candidate_qualified": False,
        "original_verified_passing_case_count": ORIGINAL,
        "original_semantic_mismatch_count": 0,
        "broader_public_verified_passing_case_count": PUBLIC,
        "broader_public_semantic_mismatch_count": 0,
        "static_first_party_non_delegation": "PASS",
        "live_runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "timing_trials_run": 0,
        "holdout_proposal_files_opened_by_graph": 0,
        "holdout_proposal_files_statted_by_graph": 0,
        "holdout_cases_opened_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "winner_selected": False,
    }, "preserve every obligation without overstating replacement qualification")
    for item in (
        b'role="img"', b'aria-labelledby="title description"',
        b"One exact from-scratch Rust build. Zero differences.",
        b"31,237 / 31,237 original checks",
        b"10,434 / 10,434 broader checks",
        b"engine, native bridge, and Python adapter are identical in both runs",
        b"16,413 / 31,237", b"4,607 / 31,237",
        b"606 differences; unfinished", b"At least 1,700 differences",
        b"External regex engines: 0", b"External regex packages: 0",
        b"Live runtime independence: NOT ESTABLISHED",
        b"FINAL SPEED: NOT MEASURED", b"NO WINNER",
        b"hidden final test has not been generated or opened",
    ):
        require(item in result["svg"],
                "the truthful accessible same-build graph omitted " + item.decode("ascii"))
    for prohibited in (b"141557760", b"141,557,760", b"226492416", b"226,492,416"):
        require(all(prohibited not in result[key]
                    for key in ("svg", "inputs", "summary")),
                "same-build reporting must not reveal or repeat proposal details")


def different(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + " CHANGED"
    if type(value) is list:
        return value + ["CHANGED"]
    if type(value) is dict:
        return {**value, "__v105_hostile": True}
    if value is None:
        return "CHANGED"
    raise Rejected("unsupported adversarial graph JSON value")


def controls(state: dict, result: dict, source_sha: str,
             source_bytes: int, contract_sha: str,
             contract_bytes: int) -> int:
    observed = []

    def reject_context(label: str, action) -> None:
        changed = copy.deepcopy(state)
        action(changed)
        try:
            verify(changed)
        except (Rejected, ValueError, TypeError, KeyError, IndexError):
            observed.append(label)
            return
        raise Rejected("unsafe same-build evidence was accepted: " + label)

    for name in ("previous_inputs", "previous_summary", "public", "audit", "original"):
        for key in sorted(state[name]):
            reject_context(
                name + " changed " + key,
                lambda hostile, owner=name, field=key:
                    hostile[owner].__setitem__(field, different(hostile[owner][field])),
            )
    for index in range(len(SUITES)):
        reject_context(
            "actual same-build original group omitted " + str(index),
            lambda hostile, position=index:
                hostile["original"]["suite_integrity"].pop(position),
        )
        for key in ("suite", "case_execution_denominator", "fully_observed",
                    "actual_worker_started", "mismatch_count",
                    "verified_passing_case_count", "pid"):
            reject_context(
                "actual group " + str(index) + " changed " + key,
                lambda hostile, position=index, field=key:
                    hostile["original"]["suite_integrity"][position].__setitem__(
                        field,
                        different(hostile["original"]["suite_integrity"][position][field]),
                    ),
            )

    def reject_output(label: str, name: str, action) -> None:
        changed = dict(result)
        payload = document(changed[name], "hostile same-build graph")
        action(payload)
        changed[name] = canonical(payload)
        try:
            validate_graph(state, changed, source_sha, source_bytes,
                           contract_sha, contract_bytes)
        except (Rejected, ValueError, TypeError, KeyError, IndexError):
            observed.append(label)
            return
        raise Rejected("dishonest same-build graph output accepted: " + label)

    for name in ("inputs", "summary"):
        for key, value in (
            ("same_exact_rust_build_verified", False),
            ("same_exact_native_engine_sha256", "0" * 64),
            ("same_exact_native_bridge_sha256", "0" * 64),
            ("same_exact_complete_adapter_sha256", "0" * 64),
            ("original_case_execution_denominator", ORIGINAL + PUBLIC),
            ("broader_public_case_execution_denominator", PUBLIC - 1),
            ("broader_public_counted_in_original_denominator", True),
            ("static_first_party_non_delegation", "FAIL"),
            ("live_runtime_non_delegation", "ESTABLISHED"),
            ("qualified_candidate_count", 1),
            ("performance", "2x"),
            ("memory", "42"),
            ("holdout_proposal_files_opened_by_graph", 1),
            ("holdout_cases_opened_by_graph", 1),
            ("hidden_cases_read_by_graph", 1),
            ("winner_selected", True),
        ):
            reject_output(
                name + " changed " + key,
                name,
                lambda payload, field=key, replacement=value:
                    payload.__setitem__(field, replacement),
            )
    for key, value in (("candidate_qualified", True),
                       ("original_semantic_mismatch_count", 1),
                       ("broader_public_semantic_mismatch_count", 1),
                       ("historical_c_observed_mismatch_count", 0),
                       ("historical_zig_observed_mismatch_lower_bound", 0)):
        reject_output(
            "summary dishonestly changed " + key,
            "summary",
            lambda payload, field=key, replacement=value:
                payload.__setitem__(field, replacement),
        )

    wall = state["wall"]

    def reject_wall(label: str, event: str, arguments: tuple) -> None:
        try:
            wall.check(event, arguments)
        except Rejected:
            observed.append(label)
            return
        raise Rejected("same-build source wall allowed " + label)

    for label, path in (
        ("candidate adapter", ROOT + "/candidates/rust_candidate.py"),
        ("native engine", ROOT + "/candidates/_rust_engine.so"),
        ("native bridge", ROOT + "/candidates/_rust_bridge.so"),
        ("old original archive", ROOT + "/oracle/phase2/evidence/original.json.gz"),
        ("private root", "/tmp/rebar-phase2-native-build-v33-private"),
        ("retired proposal", ROOT + "/oracle/phase3/expanded-sealed-holdout-v2.json"),
        ("successor proposal", ROOT + "/oracle/phase3/expanded-sealed-holdout-v3.json"),
        ("final seed", ROOT + "/oracle/phase3/final.seed"),
        ("final cases", ROOT + "/oracle/phase3/final-hidden.json"),
    ):
        reject_wall(label, "open", (path, None, os.O_RDONLY | os.O_NOFOLLOW))
    for label, event, arguments in (
        ("candidate process", "subprocess.Popen", (PYTHON,)),
        ("native engine load", "ctypes.dlopen", ("engine.so",)),
        ("candidate import", "import", ("candidates.rust_candidate",)),
        ("regex import", "import", ("re",)),
        ("archive import", "import", ("gzip",)),
        ("performance clock", "time.perf_counter", ()),
        ("network", "socket.connect", ("example.invalid",)),
        ("thread", "_thread.start_new_thread", ()),
        ("destructive rename", "os.rename", ("old", "new")),
    ):
        reject_wall(label, event, arguments)
    require(len(observed) >= 400,
            "require comprehensive same-build identities and physical-wall controls")
    return len(observed)


def exclusive(relative: str, payload: bytes) -> None:
    descriptor = os.open(os.path.join(ROOT, relative),
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        position = 0
        while position < len(payload):
            wrote = os.write(descriptor, payload[position:])
            require(wrote > 0, "exclusive same-build artifact publication stopped")
            position += wrote
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def valid_commit(value: object, name: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(item in "0123456789abcdef" for item in value),
            "require the actual committed and pushed graph source: " + name)
    return value


def arguments() -> argparse.Namespace:
    found = [item for item in sys.argv[1:] if item.startswith("--")]
    require(len(found) == len(set(found)),
            "reject repeated same-build source modes and digest pins")
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
    parser.add_argument("--public-receipt-sha256", required=True)
    parser.add_argument("--audit-receipt-sha256", required=True)
    parser.add_argument("--original-receipt-path", required=True)
    parser.add_argument("--original-receipt-sha256", required=True)
    parser.add_argument("--original-receipt-bytes", required=True, type=int)
    parser.add_argument("--root-authorized", action="store_true")
    parser.add_argument("--frozen-committed-pushed", action="store_true")
    parser.add_argument("--frozen-commit")
    parser.add_argument("--pushed-commit")
    options = parser.parse_args()
    if options.render_contract:
        require(options.contract_sha256 is None and options.contract_bytes is None
                and options.root_authorized is False
                and options.frozen_committed_pushed is False
                and options.frozen_commit is None and options.pushed_commit is None,
                "render only a prospective graph source contract")
    elif options.render_graph:
        require(options.contract_sha256 is not None
                and options.contract_bytes is not None
                and options.root_authorized is True
                and options.frozen_committed_pushed is True
                and valid_commit(options.frozen_commit, "frozen commit")
                    == valid_commit(options.pushed_commit, "pushed commit"),
                "only root may render after the complete source freeze is committed and pushed")
    else:
        require(options.contract_sha256 is not None
                and options.contract_bytes is not None
                and options.root_authorized is False
                and options.frozen_committed_pushed is False
                and options.frozen_commit is None and options.pushed_commit is None,
                "source-only graph verification cannot possess publication authority")
    return options


def context(options: argparse.Namespace) -> dict:
    source_owner = (SOURCE, sha(options.source_sha256, "V105 graph renderer"),
                    options.source_bytes)
    protocol_owner = (PROTOCOL, sha(options.protocol_sha256, "V105 graph protocol"),
                      options.protocol_bytes)
    actual = original_owner(options.original_receipt_path,
                            options.original_receipt_sha256,
                            options.original_receipt_bytes)
    require(type(options.source_bytes) is int and 1 <= options.source_bytes <= 262_144
            and type(options.protocol_bytes) is int
            and 1 <= options.protocol_bytes <= 65_536,
            "independently pin the complete renderer and protocol byte sizes")
    for name, owner in PREVIOUS.items():
        require(getattr(options, "previous_" + name + "_sha256") == owner[1],
                "immutable V104 predecessor digest changed: " + name)
    require(options.public_receipt_sha256 == PUBLIC_RECEIPT[1]
            and options.audit_receipt_sha256 == AUDIT_RECEIPT[1],
            "independently caller-pin the genuine public and first-party audit PASS")
    approved = (*rows(actual), source_owner, protocol_owner)
    contract_owner = None
    if options.contract_sha256 is not None:
        require(type(options.contract_bytes) is int
                and 1 <= options.contract_bytes <= 262_144,
                "independently pin the complete V105 graph contract size")
        contract_owner = (CONTRACT, sha(options.contract_sha256, "V105 graph contract"),
                          options.contract_bytes)
        approved = (*approved, contract_owner)
    mode = "contract" if options.render_contract else (
        "graph" if options.render_graph else "source"
    )
    wall = SourceWall(mode, approved)
    sys.addaudithook(wall.check)
    metadata, raw = {}, {}
    for owner in approved:
        identity, value = read(owner, approved)
        metadata[owner[0]], raw[owner[0]] = identity, value
    result = {
        "options": options,
        "wall": wall,
        "owners": metadata,
        "goal": raw[GOAL[0]],
        "previous_inputs": document(raw[PREVIOUS["inputs"][0]], "V104 inputs"),
        "previous_summary": document(raw[PREVIOUS["summary"][0]], "V104 summary"),
        "previous_svg": raw[PREVIOUS["svg"][0]],
        "public": document(raw[PUBLIC_RECEIPT[0]], "actual public PASS"),
        "audit": document(raw[AUDIT_RECEIPT[0]], "actual static first-party PASS"),
        "original_owner": actual,
        "original": document(raw[actual[0]], "actual same-build original PASS"),
    }
    if contract_owner is not None:
        result["contract_owner"] = contract_owner
        result["contract_document"] = document(raw[CONTRACT], "V105 source contract")
    verify(result)
    if contract_owner is not None:
        require(result["contract_document"] == freeze(result),
                "reject a stale or incomplete same-build graph source freeze")
    return result


def report(state: dict, hostile: int) -> dict:
    options = state["options"]
    return {
        "schema": "rebar-rust-same-build-correctness-overview-v105-source-result",
        "version": VERSION,
        "status": "PASS",
        "mode": "SELF-TEST" if options.self_test else (
            "GRAPH RENDER" if options.render_graph else "FROZEN CONTEXT"
        ),
        "same_exact_rust_build_verified": True,
        "same_exact_native_engine_sha256": ENGINE_SHA,
        "same_exact_native_bridge_sha256": BRIDGE_SHA,
        "same_exact_complete_adapter_sha256": ADAPTER_SHA,
        "original_case_execution_denominator": ORIGINAL,
        "original_verified_passing_case_count": ORIGINAL,
        "original_semantic_mismatch_count": 0,
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_verified_passing_case_count": PUBLIC,
        "broader_public_semantic_mismatch_count": 0,
        "static_first_party_non_delegation": "PASS",
        "live_runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "hostile_controls_rejected": hostile,
        **source_effects(),
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "winner_selected": False,
    }


def main() -> int:
    options = arguments()
    require(sys.executable == PYTHON and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.no_site == 1
            and sys.flags.dont_write_bytecode == 1,
            "require the pinned isolated, no-site CPython 3.14.6 executable")
    state = context(options)
    if options.render_contract:
        machine = freeze(state)
        payload = canonical(machine)
        os.write(1, payload)
        return 0
    assets = graph(state, options.source_sha256, options.source_bytes,
                   options.contract_sha256, options.contract_bytes)
    validate_graph(state, assets, options.source_sha256, options.source_bytes,
                   options.contract_sha256, options.contract_bytes)
    checked = (controls(state, assets, options.source_sha256, options.source_bytes,
                        options.contract_sha256, options.contract_bytes)
               if options.self_test else 0)
    if options.render_graph:
        for name, extension in (("svg", ".svg"), ("inputs", ".inputs.json"),
                                ("summary", ".json")):
            exclusive(OUTPUT + extension, assets[name])
    result = report(state, checked)
    if options.render_graph:
        result.update({name + "_sha256": digest(payload)
                       for name, payload in assets.items()})
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Rejected, OSError, ValueError, TypeError, KeyError, IndexError) as failure:
        print("same-build-correctness-v105: " + str(failure), file=sys.stderr)
        raise SystemExit(1)
