#!/usr/bin/env python3
"""Record an actual independent Zig build without claiming matching or speed."""

from __future__ import annotations

import argparse
import base64
import binascii
import copy
import hashlib
import os
from pathlib import Path
import stat
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v86.py"
OUTPUT = "docs/evidence/candidate-current-overview-v86"
SCHEMA = "rebar-candidate-current-overview-v86"
BUILD_KEY = "actual_zig_v13_first_party_scanner_source_build"
BUILD_POOL_SCHEMA = SCHEMA + "-lossless-complete-zig-build-pool-v1"
BUILD_REFERENCE_SCHEMA = SCHEMA + "-complete-zig-build-reference-v1"
V85 = {
    "source": (
        "tools/render_candidate_current_overview_v85.py",
        "90a66dfe3d239cba478b278e63dc5b90c65243117b5f961fe7b2f71c6999bfd0",
        75303,
        431675,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v85.inputs.json",
        "80a2f6992f895145368581004f0bfccf69898467af01e32b854b7598380841bb",
        1344687,
        431676,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v85.json",
        "f9e712902186d8df7b73d3b92aa6a45e3917cadb0d879e5d8d8c626ce07e4d32",
        3873825,
        431677,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v85.svg",
        "e69496318003461c0983b236e749a28c55c04ddcf593d84e388453947356c9a1",
        6152,
        431678,
    ),
}
ROOT_RECEIPT = (
    "oracle/phase2/evidence/"
    "zig-scanner-phrase-source-build-v13-"
    "phase2-v13-zig-scanner-phrase-v4-private-root-receipt.json",
    "03f661f87c9a061cb1fd1af49041b1dc5e616449ed91feb0575a1f013fafb3c2",
    74891,
    525148,
)
BUILD_RECEIPT = (
    "oracle/phase2/evidence/"
    "zig-scanner-phrase-source-build-v13-"
    "phase2-v13-zig-scanner-phrase-v4-build-receipt.json",
    "8d86fd25025caf440937679a7893aa2d72308f86eccd577073dbe502a341725d",
    170856,
    525149,
)
ROOT_RECEIPT_KEYS = frozenset({
    "actual_process_count",
    "candidate_correctness",
    "candidate_workers_started",
    "compressed_archives_created",
    "contract_sha256",
    "family",
    "frozen_evidence_owner_lower_bound",
    "frozen_graph_version",
    "frozen_history_reference_lower_bound",
    "holdout",
    "label",
    "native_activations",
    "performance",
    "phase_names",
    "phases",
    "private_root",
    "private_root_cleanup",
    "private_root_retained",
    "protocol_sha256",
    "schema",
    "source_sha256",
    "source_snapshots_per_completed_phase",
    "status",
    "version",
    "winner_selected",
})
BUILD_RECEIPT_KEYS = frozenset({
    "candidate_correctness",
    "complete_actual_build",
    "compressed_evidence_owner_count",
    "contract_sha256",
    "failure_preserved",
    "family",
    "frozen_evidence_owner_lower_bound",
    "frozen_graph_version",
    "frozen_history_reference_lower_bound",
    "holdout",
    "label",
    "new_exclusive_plaintext_evidence_owner_count",
    "performance",
    "private_root_receipt",
    "private_root_receipt_sha256",
    "protocol_sha256",
    "schema",
    "source_sha256",
    "status",
    "version",
    "winner_selected",
})
ACTUAL_BUILD_KEYS = frozenset({
    "actual_process_count",
    "actual_source_snapshot_count",
    "benchmark_files_opened",
    "build_phases",
    "candidate_correctness",
    "candidate_imports",
    "candidate_matching",
    "candidate_qualified",
    "candidate_workers_started",
    "clock_samples",
    "contract_sha256",
    "corrected_adapter_sha256",
    "cross_family_engine_count",
    "expected_process_count_only_after_success",
    "external_regex_dependency_count",
    "failure_cleanup",
    "family",
    "first_party_bridge_source_sha256",
    "first_party_engine_source_sha256",
    "frozen_evidence_owner_lower_bound",
    "frozen_graph_version",
    "frozen_history_reference_lower_bound",
    "holdout",
    "holdout_files_opened",
    "label",
    "matching_archives_opened",
    "memory",
    "native_activations",
    "native_libraries_loaded",
    "network_requests",
    "original_case_execution_denominator",
    "original_named_private_waiver_count",
    "original_suite_count",
    "owned_original_sources_after",
    "owned_original_sources_before",
    "performance",
    "private_root",
    "processes",
    "protocol_sha256",
    "reference_workers_started",
    "reproducibility",
    "schema",
    "source_sha256",
    "status",
    "stdlib_regex_engine_count",
    "supplemental_reference_case_count",
    "undefined_behavior",
    "version",
    "winner_selected",
})
PROCESS_KEYS = frozenset({
    "argv",
    "environment",
    "phase",
    "pid",
    "returncode",
    "role",
    "signal",
    "stderr",
    "stdout",
    "working_directory",
})
PHASE_KEYS = frozenset({"directories", "name", "native_outputs", "source_snapshots"})
STREAM_KEYS = frozenset({"base64", "bytes", "sha256"})
NATIVE_OWNER_KEYS = frozenset({
    "bytes", "device", "inode", "mode", "nlink", "path", "sha256", "uid"
})
AUDIT_KEYS = frozenset({
    "allowed_unicode_helpers",
    "cross_family_engine_count",
    "defined_dynamic_symbol_count",
    "defined_first_party_symbols",
    "external_regex_dependency_count",
    "imported_first_party_symbols",
    "legacy_rpath_count",
    "native_loader_dependency_count",
    "needed",
    "role",
    "runpath",
    "soname",
    "stdlib_regex_engine_count",
    "undefined_dynamic_symbol_count",
})
ACTUAL_PIDS = (
    81, 82, 83, 84, 120, 125, 126, 127, 128, 129, 130, 131, 132,
    133, 134, 135, 136, 172, 177, 178, 179, 180, 181, 182, 183, 184,
)
ENGINE_SHA256 = (
    "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071"
)
BRIDGE_SHA256 = (
    "3dfd80e26773d83acfc83cba7f0df1b85a796ed0059aaa6d855ec0a3b5a93121"
)


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / relative), flags)
    try:
        before = os.fstat(descriptor)
        if not (
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_dev == 2064
            and before.st_ino == inode
            and before.st_size == size
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600
        ):
            raise ValueError("reject substituted whole V86 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated whole V86 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise ValueError("reject extended whole V86 owner: " + label)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_nlink,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_nlink,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise ValueError("reject changed whole V86 owner: " + label)
        return raw
    finally:
        os.close(descriptor)


def load_previous() -> tuple[
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    tuple,
    types.ModuleType,
]:
    raw = read_fixed(V85["source"], "actual complete pushed V85 graph renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v85")
    previous.__file__ = str(ROOT / V85["source"][0])
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    v84, v83, v82, chain, base = previous.load_previous()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v85"
        and previous.SELF == V85["source"][0]
        and len(chain) == 15,
        "authenticate the complete actually pushed V85 historical source chain",
    )
    return previous, v84, v83, v82, chain, base


def authenticate_previous(
    previous: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> tuple[dict, dict]:
    pins: dict[str, object] = {
        "source_sha256": V85["source"][1],
        "source_bytes": V85["source"][2],
    }
    for role, item in previous.V84.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.FEATURE.items():
        pins["feature_" + role + "_sha256"] = item[1]
    snapshot, assets = previous.build(
        v84, v83, v82, chain, base, argparse.Namespace(**pins)
    )
    for role in ("inputs", "summary", "svg"):
        item = V85[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole committed V85 " + role),
            "reconstruct every byte of the complete pushed V85 " + role,
        )
    old = base.document(assets[V85["summary"][0]], "whole exact V85 summary")
    inputs = base.document(assets[V85["inputs"][0]], "whole exact V85 inputs")
    base.need(
        old["snapshot"] == snapshot
        and old["version"] == 85
        and inputs["version"] == 85
        and old["actual_current_graph_predecessor_version"] == 84
        and old["authenticated_evidence_owner_lower_bound"] == 275
        and old["authenticated_history_reference_lower_bound"] == 280
        and old["lossless_family_evidence_pool_entry_count"] == 9
        and old["lossless_actual_outcome_evidence_pool_entry_count"] == 1
        and old["lossless_zig_source_evidence_pool_entry_count"] == 1
        and old["lossless_v84_family_previous_byte_identity_status"] == "PASS"
        and old["rust_v12_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v13_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v14_original_campaign_infrastructure_failure_count"] == 13
        and old["rust_v15_original_campaign_candidate_matching"] == "FAIL"
        and old["rust_v15_original_campaign_actual_worker_count"] == 13
        and old["rust_v15_original_campaign_completed_suite_count"] == 8
        and old["rust_v15_original_campaign_verified_passing_case_count"] == 12942
        and old["rust_v15_original_campaign_infrastructure_failure_count"] == 5
        and old["rust_v15_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and old[
            "rust_v15_original_campaign_pattern_destructor_proven_failure_cause"
        ] is False
        and old["zig_v13_first_party_source_build_candidate_matching"] == "NOT RUN"
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["qualified_candidate_count"] == 0
        and old["performance"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False,
        "retain the exact three historical pools and all actual Rust results",
    )
    historical = {key: copy.deepcopy(old[key]) for key in v83.PROOF_KEYS}
    v83.validate_pool(base, old["lossless_family_evidence_pool"], historical)
    v84.validate_actual_pool(
        base,
        old["lossless_actual_outcome_evidence_pool"],
        old[v84.ACTUAL_KEY],
    )
    previous.validate_zig_pool(
        base,
        old["lossless_zig_source_evidence_pool"],
        old[previous.ZIG_KEY],
    )
    return old, inputs


def validate_process_stream(
    base: types.ModuleType,
    value: object,
    phase: str,
    role: str,
    category: str,
) -> None:
    base.need(
        type(value) is dict
        and set(value) == STREAM_KEYS
        and type(value["bytes"]) is int
        and 0 <= value["bytes"] <= base.OWNER_LIMIT
        and type(value["base64"]) is str,
        "reject incomplete genuine compiler stream " + phase + ":" + role,
    )
    assert isinstance(value, dict)
    expected = base.checked(value["sha256"], "actual whole " + category)
    try:
        raw = base64.b64decode(value["base64"], validate=True)
    except (ValueError, binascii.Error) as error:
        raise ValueError("reject malformed complete " + category) from error
    base.need(
        len(raw) == value["bytes"] and hashlib.sha256(raw).hexdigest() == expected,
        "reauthenticate every byte of actual " + phase + ":" + role + ":" + category,
    )


def validate_receipts(
    base: types.ModuleType,
    previous: types.ModuleType,
    old: dict,
    root: object,
    build: object,
) -> None:
    base.need(
        type(root) is dict
        and set(root) == ROOT_RECEIPT_KEYS
        and type(build) is dict
        and set(build) == BUILD_RECEIPT_KEYS,
        "reject incomplete, fabricated or provisional actual Zig build receipts",
    )
    assert isinstance(root, dict) and isinstance(build, dict)
    source = old[previous.ZIG_KEY]["complete_feature_contract"]
    for name, receipt, expected_schema in (
        (
            "private root",
            root,
            "rebar-owned-zig-scanner-phrase-source-build-v13-private-root-receipt",
        ),
        (
            "native build",
            build,
            "rebar-owned-zig-scanner-phrase-source-build-v13-plaintext-build-receipt",
        ),
    ):
        base.need(
            receipt["schema"] == expected_schema
            and receipt["status"] == "PASS"
            and receipt["version"] == 13
            and receipt["family"] == "zig"
            and receipt["label"] == "phase2-v13-zig-scanner-phrase-v4"
            and receipt["source_sha256"] == previous.FEATURE["source"][1]
            and receipt["protocol_sha256"] == previous.FEATURE["protocol"][1]
            and receipt["contract_sha256"] == previous.FEATURE["contract"][1]
            and receipt["frozen_graph_version"] == 84
            and receipt["frozen_evidence_owner_lower_bound"] == 272
            and receipt["frozen_history_reference_lower_bound"] == 277
            and receipt["candidate_correctness"] == "NOT MEASURED"
            and receipt["performance"] == "NOT MEASURED"
            and receipt["holdout"] == "NOT OPENED"
            and receipt["winner_selected"] is False,
            "preserve whole exact independent Zig " + name + " publication",
        )
    base.need(
        root["actual_process_count"] == 26
        and root["candidate_workers_started"] == 0
        and root["compressed_archives_created"] == 0
        and root["native_activations"] == 0
        and root["phase_names"] == ["reference-a", "reference-b"]
        and type(root["phases"]) is list
        and len(root["phases"]) == 2
        and root["source_snapshots_per_completed_phase"] == 3
        and root["private_root_retained"] is True
        and root["private_root_cleanup"] == "NOT NEEDED",
        "retain exactly two genuine independent build phases, without loading them",
    )
    reference = build["private_root_receipt"]
    base.need(
        type(reference) is dict
        and set(reference)
        == {
            "bytes",
            "device",
            "directory_fsync",
            "file_fsync",
            "inode",
            "mode",
            "nlink",
            "path",
            "sha256",
            "uid",
        }
        and reference["path"] == ROOT_RECEIPT[0]
        and reference["sha256"] == ROOT_RECEIPT[1]
        and reference["bytes"] == ROOT_RECEIPT[2]
        and reference["inode"] == ROOT_RECEIPT[3]
        and reference["device"] == 2064
        and reference["mode"] == "0600"
        and reference["nlink"] == 1
        and reference["uid"] == os.geteuid()
        and reference["directory_fsync"] is True
        and reference["file_fsync"] is True
        and build["private_root_receipt_sha256"] == ROOT_RECEIPT[1]
        and build["new_exclusive_plaintext_evidence_owner_count"] == 2
        and build["compressed_evidence_owner_count"] == 0
        and build["failure_preserved"] is False,
        "cross-authenticate exactly two whole public plaintext Zig result owners",
    )
    actual = build["complete_actual_build"]
    base.need(
        type(actual) is dict
        and set(actual) == ACTUAL_BUILD_KEYS
        and actual["schema"]
        == "rebar-owned-zig-scanner-phrase-source-build-v13-complete-actual-build"
        and actual["status"] == "PASS"
        and actual["version"] == 13
        and actual["family"] == "zig"
        and actual["label"] == "phase2-v13-zig-scanner-phrase-v4"
        and actual["source_sha256"] == previous.FEATURE["source"][1]
        and actual["protocol_sha256"] == previous.FEATURE["protocol"][1]
        and actual["contract_sha256"] == previous.FEATURE["contract"][1]
        and actual["frozen_graph_version"] == 84
        and actual["frozen_evidence_owner_lower_bound"] == 272
        and actual["frozen_history_reference_lower_bound"] == 277
        and actual["actual_process_count"] == 26
        and actual["actual_source_snapshot_count"] == 6
        and actual["expected_process_count_only_after_success"] == 26
        and actual["first_party_engine_source_sha256"]
        == source["first_party_phrase_repair"]
        ["first_party_zig_parser_compiler_executor"]["sha256"]
        and actual["first_party_bridge_source_sha256"]
        == source["first_party_phrase_repair"]["first_party_cpython_c_api_bridge"]
        ["sha256"]
        and actual["corrected_adapter_sha256"]
        == source["first_party_phrase_repair"]["complete_corrected_adapter"]
        ["sha256"]
        and actual["original_case_execution_denominator"] == 31237
        and actual["original_named_private_waiver_count"] == 13
        and actual["original_suite_count"] == 13
        and actual["supplemental_reference_case_count"] == 8244
        and actual["candidate_correctness"] == "NOT MEASURED"
        and actual["candidate_matching"] == "NOT RUN"
        and actual["candidate_qualified"] is False,
        "distinguish complete actual native building from unrun P0 matching",
    )
    for key in (
        "benchmark_files_opened",
        "candidate_imports",
        "candidate_workers_started",
        "clock_samples",
        "cross_family_engine_count",
        "external_regex_dependency_count",
        "holdout_files_opened",
        "matching_archives_opened",
        "native_activations",
        "native_libraries_loaded",
        "network_requests",
        "reference_workers_started",
        "stdlib_regex_engine_count",
    ):
        base.need(actual[key] == 0, "reject forbidden actual build effect: " + key)
    base.need(
        actual["failure_cleanup"] == "NOT NEEDED"
        and actual["holdout"] == "NOT OPENED"
        and actual["performance"] == "NOT MEASURED"
        and actual["memory"] == "NOT MEASURED"
        and actual["undefined_behavior"] == "NOT MEASURED"
        and actual["winner_selected"] is False,
        "never infer matching, a winner, or performance from compiled binaries",
    )
    private = root["private_root"]
    base.need(
        type(private) is dict
        and set(private) == {"device", "inode", "mode", "path", "uid"}
        and private["device"] == 2049
        and private["inode"] == 11673391
        and private["mode"] == "0700"
        and private["path"]
        == "/tmp/rebar-phase2-zig-scanner-phrase-source-build-v13-yhzrep3u"
        and private["uid"] == os.geteuid()
        and actual["private_root"] == private
        and actual["build_phases"] == root["phases"],
        "retain exact private-root and phase descriptions solely from receipts",
    )
    processes = actual["processes"]
    base.need(
        type(processes) is list
        and len(processes) == 26
        and [item.get("pid") for item in processes if type(item) is dict]
        == list(ACTUAL_PIDS)
        and len(set(ACTUAL_PIDS)) == 26,
        "retain every distinct actual compiler process and no fabricated worker",
    )
    expected_schedule = [
        (phase, role)
        for phase in ("reference-a", "reference-b")
        for role in previous.PROCESS_ROLES
    ]
    for item, (phase, role), pid in zip(
        processes, expected_schedule, ACTUAL_PIDS, strict=True
    ):
        base.need(
            type(item) is dict
            and set(item) == PROCESS_KEYS
            and item["phase"] == phase
            and item["role"] == role
            and item["pid"] == pid
            and item["returncode"] == 0
            and item["signal"] is None
            and type(item["argv"]) is list
            and bool(item["argv"])
            and type(item["environment"]) is dict
            and type(item["working_directory"]) is str
            and item["working_directory"].startswith(private["path"] + "/"),
            "reject a missing or invented actual Zig process: " + phase + ":" + role,
        )
        validate_process_stream(base, item["stdout"], phase, role, "stdout")
        validate_process_stream(base, item["stderr"], phase, role, "stderr")
    phase_native_inodes = {
        "reference-a": {"engine": 11674251, "bridge": 11674255},
        "reference-b": {"engine": 11672935, "bridge": 11675084},
    }
    for phase, name in zip(root["phases"], ("reference-a", "reference-b"), strict=True):
        base.need(
            type(phase) is dict
            and set(phase) == PHASE_KEYS
            and phase["name"] == name
            and type(phase["source_snapshots"]) is dict
            and set(phase["source_snapshots"])
            == {
                "candidates/zig/mini_regex.zig",
                "candidates/zig/py_bridge.c",
                "candidates/zig_candidate.py",
            }
            and type(phase["native_outputs"]) is dict
            and set(phase["native_outputs"]) == {"engine", "bridge"},
            "preserve three genuine source snapshots in actual phase " + name,
        )
        for role, digest, size in (
            ("engine", ENGINE_SHA256, 108888),
            ("bridge", BRIDGE_SHA256, 133656),
        ):
            output = phase["native_outputs"][role]
            base.need(
                type(output) is dict
                and set(output)
                == {
                    "dynamic_output",
                    "independence_audit",
                    "notes_output",
                    "owner",
                    "sections_output",
                    "symbols_output",
                },
                "retain complete native audit solely from actual public receipt",
            )
            owner = output["owner"]
            audit = output["independence_audit"]
            base.need(
                type(owner) is dict
                and set(owner) == NATIVE_OWNER_KEYS
                and owner["sha256"] == digest
                and owner["bytes"] == size
                and owner["device"] == 2049
                and owner["inode"] == phase_native_inodes[name][role]
                and owner["mode"] == "0700"
                and owner["nlink"] == 1
                and owner["uid"] == os.geteuid()
                and owner["path"].startswith(private["path"] + "/" + name + "/")
                and type(audit) is dict
                and set(audit) == AUDIT_KEYS
                and audit["role"] == role
                and audit["external_regex_dependency_count"] == 0
                and audit["cross_family_engine_count"] == 0
                and audit["stdlib_regex_engine_count"] == 0
                and audit["legacy_rpath_count"] == 0
                and audit["native_loader_dependency_count"] == 0,
                "authenticate actual own native " + role + " in " + name,
            )
            if role == "engine":
                base.need(
                    audit["defined_dynamic_symbol_count"] == 22
                    and type(audit["defined_first_party_symbols"]) is list
                    and len(audit["defined_first_party_symbols"]) == 22
                    and audit["soname"] == "_zig_probe.so",
                    "retain 22 genuine owned Zig engine exports",
                )
            else:
                base.need(
                    audit["defined_dynamic_symbol_count"] == 1
                    and audit["runpath"] == "$ORIGIN"
                    and type(audit["imported_first_party_symbols"]) is list
                    and len(audit["imported_first_party_symbols"]) == 14,
                    "retain the 14 genuine own-engine bridge imports",
                )
    reproducibility = actual["reproducibility"]
    base.need(
        type(reproducibility) is dict
        and set(reproducibility)
        == {
            "all_native_artifacts_byte_identical",
            "compiler_process_count",
            "independent_phase_count",
            "native_roles",
            "source_snapshot_count",
            "status",
            "unique_compiler_process_count",
        }
        and reproducibility["status"] == "PASS"
        and reproducibility["all_native_artifacts_byte_identical"] is True
        and reproducibility["compiler_process_count"] == 26
        and reproducibility["unique_compiler_process_count"] == 26
        and reproducibility["independent_phase_count"] == 2
        and reproducibility["source_snapshot_count"] == 6
        and type(reproducibility["native_roles"]) is dict
        and set(reproducibility["native_roles"]) == {"engine", "bridge"},
        "prove two actual independent builds without counting planned processes",
    )
    for role, digest, size in (
        ("engine", ENGINE_SHA256, 108888),
        ("bridge", BRIDGE_SHA256, 133656),
    ):
        item = reproducibility["native_roles"][role]
        base.need(
            type(item) is dict
            and set(item)
            == {"byte_identical", "bytes", "distinct_phase_owner_count", "sha256"}
            and item["byte_identical"] is True
            and item["bytes"] == size
            and item["distinct_phase_owner_count"] == 2
            and item["sha256"] == digest,
            "retain complete reproducible native owner evidence: " + role,
        )
    base.need(
        actual["owned_original_sources_after"]
        == actual["owned_original_sources_before"]
        and type(actual["owned_original_sources_before"]) is dict
        and set(actual["owned_original_sources_before"])
        == {
            "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
            "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py",
            "candidates/zig_candidate.py",
        },
        "retain four unchanged genuine original candidate source owners",
    )


def make_build_proof(base: types.ModuleType, root: dict, build: dict) -> dict:
    actual = build["complete_actual_build"]
    actual_raw = base.canonical(actual)
    return {
        "schema": SCHEMA + "-actual-zig-scanner-source-build-v13-outcome",
        "version": 13,
        "complete_public_private_root_receipt": copy.deepcopy(root),
        "complete_public_build_receipt": copy.deepcopy(build),
        "complete_actual_build_receipt_path":
            "complete_public_build_receipt.complete_actual_build",
        "complete_actual_build_canonical_sha256": base.digest(actual_raw),
        "complete_actual_build_canonical_bytes": len(actual_raw),
        "root_receipt_owner": base.synthetic_owner(
            ROOT_RECEIPT[:3], ROOT_RECEIPT[3]
        ),
        "build_receipt_owner": base.synthetic_owner(
            BUILD_RECEIPT[:3], BUILD_RECEIPT[3]
        ),
        "root_receipt_sha256": ROOT_RECEIPT[1],
        "build_receipt_sha256": BUILD_RECEIPT[1],
        "actual_build_status": "PASS",
        "actual_independent_phase_count": 2,
        "actual_compiler_process_count": 26,
        "actual_unique_compiler_process_count": 26,
        "actual_source_snapshot_count": 6,
        "actual_engine_sha256": ENGINE_SHA256,
        "actual_engine_bytes": 108888,
        "actual_engine_distinct_phase_owner_count": 2,
        "actual_bridge_sha256": BRIDGE_SHA256,
        "actual_bridge_bytes": 133656,
        "actual_bridge_distinct_phase_owner_count": 2,
        "actual_native_artifacts_byte_identical": True,
        "actual_native_libraries_loaded_by_graph": 0,
        "actual_native_private_root_opened_by_graph": False,
        "actual_candidate_matching": "NOT RUN",
        "actual_candidate_qualified": False,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def make_build_pool(base: types.ModuleType, proof: dict) -> dict:
    raw = base.canonical(proof)
    digest = base.digest(raw)
    return {
        "schema": BUILD_POOL_SCHEMA,
        "version": 1,
        "hash_algorithm": "sha256",
        "entries": {
            digest: {
                "proof_key": BUILD_KEY,
                "proof_schema": proof["schema"],
                "canonical_sha256": digest,
                "canonical_bytes": len(raw),
                "complete_proof": copy.deepcopy(proof),
            },
        },
    }


def validate_build_pool(
    base: types.ModuleType,
    pool: object,
    proof: dict,
) -> None:
    base.need(
        type(pool) is dict
        and set(pool) == {"schema", "version", "hash_algorithm", "entries"}
        and pool["schema"] == BUILD_POOL_SCHEMA
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and type(pool["entries"]) is dict
        and len(pool["entries"]) == 1,
        "require one whole canonical owner for both actual Zig plaintext receipts",
    )
    assert isinstance(pool, dict)
    digest, entry = next(iter(pool["entries"].items()))
    raw = base.canonical(proof)
    base.need(
        base.checked(digest, "complete actual Zig build proof") == base.digest(raw)
        and type(entry) is dict
        and set(entry)
        == {
            "proof_key",
            "proof_schema",
            "canonical_sha256",
            "canonical_bytes",
            "complete_proof",
        }
        and entry["proof_key"] == BUILD_KEY
        and entry["proof_schema"] == proof["schema"]
        and entry["canonical_sha256"] == digest
        and entry["canonical_bytes"] == len(raw)
        and base.canonical(entry["complete_proof"]) == raw,
        "reject omitted, copied, swapped, or partial actual build receipts",
    )


def make_build_reference(
    base: types.ModuleType,
    pool: dict,
    proof: dict,
) -> dict:
    validate_build_pool(base, pool, proof)
    raw = base.canonical(proof)
    return {
        "schema": BUILD_REFERENCE_SCHEMA,
        "proof_key": BUILD_KEY,
        "sha256": base.digest(raw),
        "canonical_bytes": len(raw),
    }


def resolve_build_reference(
    base: types.ModuleType,
    pool: dict,
    reference: object,
) -> dict:
    base.need(
        type(reference) is dict
        and set(reference) == {"schema", "proof_key", "sha256", "canonical_bytes"}
        and reference["schema"] == BUILD_REFERENCE_SCHEMA
        and reference["proof_key"] == BUILD_KEY
        and type(reference["canonical_bytes"]) is int
        and reference["canonical_bytes"] > 0,
        "reject incomplete cross-family complete actual Zig build reference",
    )
    assert isinstance(reference, dict)
    digest = base.checked(reference["sha256"], "whole real Zig build reference")
    entry = pool["entries"].get(digest)
    base.need(
        type(entry) is dict
        and entry.get("proof_key") == BUILD_KEY
        and entry.get("canonical_sha256") == digest
        and entry.get("canonical_bytes") == reference["canonical_bytes"]
        and type(entry.get("complete_proof")) is dict,
        "reject a fabricated or omitted complete real native-build proof",
    )
    raw = base.canonical(entry["complete_proof"])
    base.need(
        base.digest(raw) == digest
        and len(raw) == reference["canonical_bytes"]
        and entry["proof_schema"] == entry["complete_proof"].get("schema"),
        "reauthenticate all actual process records and both whole public receipts",
    )
    return copy.deepcopy(entry["complete_proof"])


def make_changes(reference: dict) -> tuple[dict, dict]:
    zig = {
        "zig_v13_first_party_source_build_status":
            "NATIVE BUILD PASS; CANDIDATE MATCHING NOT RUN",
        "zig_v13_first_party_source_build_candidate_matching": "NOT RUN",
        "zig_v13_first_party_source_build_candidate_qualified": False,
        "zig_v13_first_party_source_build_actual_process_count": 26,
        "zig_v13_first_party_source_build_actual_unique_process_count": 26,
        "zig_v13_first_party_source_build_actual_build_receipt_count": 1,
        "zig_v13_first_party_source_build_actual_root_receipt_count": 1,
        "zig_v13_first_party_source_build_actual_phase_count": 2,
        "zig_v13_first_party_source_build_actual_source_snapshot_count": 6,
        "zig_v13_first_party_source_build_actual_native_activations": 0,
        "zig_v13_first_party_source_build_actual_engine_sha256": ENGINE_SHA256,
        "zig_v13_first_party_source_build_actual_engine_bytes": 108888,
        "zig_v13_first_party_source_build_actual_bridge_sha256": BRIDGE_SHA256,
        "zig_v13_first_party_source_build_actual_bridge_bytes": 133656,
        "zig_v13_first_party_source_build_actual_native_byte_identity": True,
        "zig_v13_first_party_source_build_private_root_opened_by_graph": False,
        "zig_v13_first_party_source_build_planned_processes_are_actual": True,
        "zig_v13_first_party_source_build_runtime_no_delegation":
            "NOT ESTABLISHED",
        "zig_v13_first_party_source_build_external_regex_packages": 0,
        "zig_v13_first_party_source_build_cross_candidate_engines": 0,
        "zig_v13_first_party_source_build_stdlib_regex_engine_dependencies": 0,
        "zig_v13_first_party_source_build_performance": "NOT MEASURED",
        "zig_v13_first_party_source_build_holdout": "NOT OPENED",
    }
    changes = {
        "actual_current_graph_predecessor_version": 85,
        "authenticated_evidence_owner_lower_bound": 277,
        "authenticated_history_reference_lower_bound": 282,
        BUILD_KEY: copy.deepcopy(reference),
        **copy.deepcopy(zig),
    }
    return changes, zig


def validate_families(
    base: types.ModuleType,
    previous: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    families: object,
    originals: list,
    historical_pool: dict,
    rust_pool: dict,
    zig_source_pool: dict,
    build_pool: dict,
    historical_documents: dict,
    rust_actual: dict,
    zig_source: dict,
    proof: dict,
    zig_changes: dict,
) -> None:
    v83.validate_pool(base, historical_pool, historical_documents)
    v84.validate_actual_pool(base, rust_pool, rust_actual)
    previous.validate_zig_pool(base, zig_source_pool, zig_source)
    validate_build_pool(base, build_pool, proof)
    base.need(
        type(families) is list
        and type(originals) is list
        and len(families) == len(originals) == 7
        and [row.get("family") for row in families if type(row) is dict]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve the real baseline and every one of six independent families",
    )
    for row, original in zip(families, originals, strict=True):
        base.need(
            type(row) is dict
            and type(original) is dict
            and row["family"] == original["family"],
            "reject a missing or artificially duplicated candidate family",
        )
        if row["family"] == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "retain every byte of the genuine Python reference baseline",
            )
            continue
        for key in v83.PROOF_KEYS:
            base.need(
                base.canonical(row[key]) == base.canonical(original[key])
                and base.canonical(
                    v83.resolve_reference(base, historical_pool, row[key], key)
                ) == base.canonical(historical_documents[key]),
                "retain complete old Rust history in " + row["family"] + ":" + key,
            )
        base.need(
            base.canonical(row[v84.ACTUAL_KEY])
            == base.canonical(original[v84.ACTUAL_KEY])
            and base.canonical(
                v84.resolve_actual_reference(
                    base, rust_pool, row[v84.ACTUAL_KEY]
                )
            ) == base.canonical(rust_actual)
            and base.canonical(row[previous.ZIG_KEY])
            == base.canonical(original[previous.ZIG_KEY])
            and base.canonical(
                previous.resolve_zig_reference(
                    base, zig_source_pool, row[previous.ZIG_KEY]
                )
            ) == base.canonical(zig_source),
            "preserve both complete actual Rust and first-party Zig source in "
            + row["family"],
        )
        base.need(
            base.canonical(resolve_build_reference(base, build_pool, row.get(BUILD_KEY)))
            == base.canonical(proof),
            "bind both entire Zig build receipts into " + row["family"],
        )
        expected = copy.deepcopy(original)
        expected["authenticated_evidence_owner_lower_bound"] = 277
        expected["authenticated_history_reference_lower_bound"] = 282
        expected[BUILD_KEY] = make_build_reference(base, build_pool, proof)
        if row["family"] == "zig":
            expected.update(copy.deepcopy(zig_changes))
        base.need(
            base.canonical(row) == base.canonical(expected),
            "prove exact complete native build family: " + row["family"],
        )
        restored = copy.deepcopy(row)
        restored.pop(BUILD_KEY)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        if row["family"] == "zig":
            for key in zig_changes:
                if key in original:
                    restored[key] = copy.deepcopy(original[key])
                else:
                    restored.pop(key)
        base.need(
            base.canonical(restored) == base.canonical(original),
            "restore every canonical pushed V85 row byte: " + row["family"],
        )
        base.need(
            row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "never infer regex matching from an actually compiled native engine",
        )


def make_svg() -> bytes:
    rows = (
        ("Python re", "Original compatibility reference", "BASELINE", "#22c55e"),
        (
            "Rust",
            "12,942 verified checks; 8 of 13 groups completed",
            "5 GROUPS FAILED",
            "#fb7185",
        ),
        ("C", "1,230 previously observed differences", "NOT COMPATIBLE", "#f59e0b"),
        (
            "Zig",
            "Own engine and bridge built twice; compatibility not tested",
            "BUILD PASS ONLY",
            "#60a5fa",
        ),
        ("C++", "2,308 differences; five startup failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four startup failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Complete Python compatibility not tested", "NOT TESTED", "#94a3b8"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1260" height="748" viewBox="0 0 1260 748" role="img" aria-labelledby="title description">',
        '<title id="title">Python compared with six from-scratch regular-expression engines</title>',
        '<desc id="description">The genuinely first-party Zig matching engine and its Python C-API bridge were actually built in two independently recorded offline phases. Twenty-six distinct successful build processes produced byte-identical first-party engine and bridge binaries and six source snapshots. This is a native build success only: no Zig candidate was imported, activated, or matched against Python, so compatibility remains not run. The real Rust result remains thirteen workers, eight completed groups, twelve thousand nine hundred forty-two verified checks, and five failures. All original results and both complete actual Zig plaintext receipts remain reproducibly preserved exactly once. No speed measurement, candidate qualification, or performance holdout was opened.</desc>',
        '<rect width="1260" height="748" rx="18" fill="#0b1220"/>',
        '<text x="34" y="48" fill="#f8fafc" font-size="26" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="81" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<line x1="34" y1="104" x2="1226" y2="104" stroke="#334155"/>',
    ]
    for index, (name, detail, result, colour) in enumerate(rows):
        y = 142 + 47 * index
        parts.extend((
            f'<circle cx="43" cy="{y - 5}" r="6" fill="{colour}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="175" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1208" y="{y}" text-anchor="end" fill="{colour}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{result}</text>',
        ))
    parts.extend((
        '<line x1="34" y1="462" x2="1226" y2="462" stroke="#334155"/>',
        '<text x="34" y="493" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">31,237 original Python checks; 8,244 separate additional checks.</text>',
        '<text x="34" y="522" fill="#93c5fd" font-size="14" font-family="system-ui,sans-serif">Actual Zig: 2 complete independent builds; 26 successful processes; identical engine and bridge.</text>',
        '<text x="34" y="550" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Full Zig compatibility and candidate matching: NOT RUN. Native build success is not a test pass.</text>',
        '<text x="34" y="578" fill="#fcd34d" font-size="13" font-family="system-ui,sans-serif">Actual Rust: 12,942 verified cases, 8/13 completed groups, and 5 failures.</text>',
        '<text x="34" y="606" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">All prior original results and both full Zig build receipts remain hash-verifiable.</text>',
        '<text x="34" y="634" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">No external regex package, Python matcher, borrowed engine, or fallback was used.</text>',
        '<text x="34" y="662" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Speed, memory, and runtime independence: NOT MEASURED or NOT ESTABLISHED.</text>',
        '<text x="34" y="691" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Final 4,194,304-case comparison: NOT FROZEN, NOT GENERATED, NOT OPENED.</text>',
        '<text x="34" y="728" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 86 · genuine two-phase first-party Zig build · no selected winner.</text>',
        '</svg>',
        '',
    ))
    return "\n".join(parts).encode("utf-8")


def build(
    previous: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None and options.source_bytes is not None,
        "caller-pin complete exact V86 actual-build graph source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "complete actual V86 source"),
        options.source_bytes,
        private=True,
    )
    for role, item in V85.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin whole pushed V85 " + role,
        )
    base.need(
        options.root_receipt_sha256 == ROOT_RECEIPT[1]
        and options.build_receipt_sha256 == BUILD_RECEIPT[1],
        "caller-pin both complete public first-party Zig build receipts",
    )
    old, previous_inputs = authenticate_previous(
        previous, v84, v83, v82, chain, base
    )
    root_raw = read_fixed(ROOT_RECEIPT, "only complete public Zig root receipt")
    build_raw = read_fixed(BUILD_RECEIPT, "only complete public Zig build receipt")
    root = base.document(root_raw, "whole exact public Zig root receipt")
    actual_build = base.document(build_raw, "whole exact public Zig build receipt")
    base.need(
        base.canonical(root) == root_raw
        and base.canonical(actual_build) == build_raw,
        "reject incomplete or noncanonical whole actual Zig public evidence",
    )
    validate_receipts(base, previous, old, root, actual_build)
    proof = make_build_proof(base, root, actual_build)
    build_pool = make_build_pool(base, proof)
    validate_build_pool(base, build_pool, proof)
    build_reference = make_build_reference(base, build_pool, proof)
    historical_pool = copy.deepcopy(old["lossless_family_evidence_pool"])
    rust_pool = copy.deepcopy(old["lossless_actual_outcome_evidence_pool"])
    zig_source_pool = copy.deepcopy(old["lossless_zig_source_evidence_pool"])
    historical_documents = {
        key: copy.deepcopy(old[key]) for key in v83.PROOF_KEYS
    }
    rust_actual = copy.deepcopy(old[v84.ACTUAL_KEY])
    zig_source = copy.deepcopy(old[previous.ZIG_KEY])
    v83.validate_pool(base, historical_pool, historical_documents)
    v84.validate_actual_pool(base, rust_pool, rust_actual)
    previous.validate_zig_pool(base, zig_source_pool, zig_source)
    base.need(
        base.canonical(historical_pool)
        == base.canonical(old["lossless_family_evidence_pool"])
        and base.canonical(rust_pool)
        == base.canonical(old["lossless_actual_outcome_evidence_pool"])
        and base.canonical(zig_source_pool)
        == base.canonical(old["lossless_zig_source_evidence_pool"]),
        "preserve every byte of all three original complete evidence pools",
    )
    changes, zig_changes = make_changes(build_reference)
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v85_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes
        if key in old["snapshot"]
    }
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V85.items()
    }
    inputs = copy.deepcopy(previous_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 86,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": predecessor,
        **copy.deepcopy(changes),
    })
    families = copy.deepcopy(old["families"])
    for row in families:
        if row["family"] == "python":
            continue
        row["authenticated_evidence_owner_lower_bound"] = 277
        row["authenticated_history_reference_lower_bound"] = 282
        row[BUILD_KEY] = copy.deepcopy(build_reference)
        if row["family"] == "zig":
            row.update(copy.deepcopy(zig_changes))
    validate_families(
        base,
        previous,
        v84,
        v83,
        families,
        old["families"],
        historical_pool,
        rust_pool,
        zig_source_pool,
        build_pool,
        historical_documents,
        rust_actual,
        zig_source,
        proof,
        zig_changes,
    )
    input_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 86,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw)
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg_raw), len(svg_raw)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        "lossless_family_evidence_pool": historical_pool,
        "lossless_family_evidence_pool_entry_count": 9,
        "lossless_family_references_per_family": 9,
        "lossless_actual_outcome_evidence_pool": rust_pool,
        "lossless_actual_outcome_evidence_pool_entry_count": 1,
        "lossless_actual_outcome_references_per_family": 1,
        "lossless_zig_source_evidence_pool": zig_source_pool,
        "lossless_zig_source_evidence_pool_entry_count": 1,
        "lossless_zig_source_references_per_family": 1,
        "lossless_zig_actual_build_evidence_pool": build_pool,
        "lossless_zig_actual_build_evidence_pool_schema": BUILD_POOL_SCHEMA,
        "lossless_zig_actual_build_evidence_pool_entry_count": 1,
        "lossless_zig_actual_build_references_per_family": 1,
        "lossless_zig_actual_build_reconstruction_status": "PASS",
        "lossless_v85_family_previous_byte_identity_status": "PASS",
        **copy.deepcopy(changes),
    })
    suites = old["actual_complete_rust_campaign"][
        "complete_independently_authenticated_suite_results"
    ]
    witnesses = old["actual_complete_rust_campaign"][
        "earliest_genuine_mismatch_witnesses"
    ]
    base.need(
        len(suites) == 13 and len(witnesses) == 6,
        "retain every original suite vector and actual mismatch witness",
    )
    for label, layer in (
        ("inputs", inputs),
        ("summary", summary),
        ("snapshot", snapshot),
    ):
        campaign = layer["actual_complete_rust_campaign"]
        base.need(
            campaign["complete_independently_authenticated_suite_results"]
            == suites
            and campaign["earliest_genuine_mismatch_witnesses"] == witnesses
            and all(
                base.canonical(layer[key])
                == base.canonical(historical_documents[key])
                for key in v83.PROOF_KEYS
            )
            and base.canonical(layer[v84.ACTUAL_KEY])
            == base.canonical(rust_actual)
            and base.canonical(layer[previous.ZIG_KEY])
            == base.canonical(zig_source)
            and base.canonical(layer[BUILD_KEY]) == base.canonical(build_reference)
            and base.canonical(
                resolve_build_reference(base, build_pool, layer[BUILD_KEY])
            ) == base.canonical(proof)
            and layer["rust_v12_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v13_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v14_original_campaign_infrastructure_failure_count"]
            == 13
            and layer["rust_v15_original_campaign_actual_worker_count"] == 13
            and layer["rust_v15_original_campaign_completed_suite_count"] == 8
            and layer["rust_v15_original_campaign_verified_passing_case_count"]
            == 12942
            and layer["rust_v15_original_campaign_infrastructure_failure_count"]
            == 5
            and layer["rust_v15_original_campaign_semantic_mismatch_count"]
            == "NOT MEASURED"
            and layer[
                "rust_v15_original_campaign_pattern_destructor_proven_failure_cause"
            ] is False
            and layer["zig_v13_first_party_source_build_candidate_matching"]
            == "NOT RUN"
            and layer["zig_v13_first_party_source_build_candidate_qualified"]
            is False
            and layer["zig_v13_first_party_source_build_actual_process_count"]
            == 26
            and layer["zig_v13_first_party_source_build_actual_phase_count"] == 2,
            "preserve all exact actual outcomes and complete build refs in " + label,
        )
    base.need(
        base.canonical(summary["lossless_family_evidence_pool"])
        == base.canonical(old["lossless_family_evidence_pool"])
        and base.canonical(summary["lossless_actual_outcome_evidence_pool"])
        == base.canonical(old["lossless_actual_outcome_evidence_pool"])
        and base.canonical(summary["lossless_zig_source_evidence_pool"])
        == base.canonical(old["lossless_zig_source_evidence_pool"])
        and summary["actual_rust_semantic_mismatch_count"] == 1440
        and summary["actual_c_semantic_mismatch_count"] == 1230
        and summary["actual_zig_semantic_mismatch_count"] == 1764
        and summary["qualified_candidate_count"] == 0
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED"
        and summary["final_holdout_opened"] is False,
        "never hide losses or mistake a reproducible build for regex compatibility",
    )
    summary_raw = base.canonical(summary)
    assets = {
        OUTPUT + ".inputs.json": input_raw,
        OUTPUT + ".json": summary_raw,
        OUTPUT + ".svg": svg_raw,
    }
    for path, raw in assets.items():
        base.need(
            type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
            "reject oversized whole build proof BEFORE publishing any V86 "
            + path,
        )
    return snapshot, assets


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
        and type(raw) is bytes
        and 0 < len(raw) <= base.OWNER_LIMIT,
        "publish only a complete, bounded, exclusively created V86 output",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(type(count) is int and count > 0, "write all V86 bytes")
            remaining = remaining[count:]
        os.fsync(descriptor)
        actual = os.fstat(descriptor)
        base.need(
            actual.st_uid == os.geteuid()
            and actual.st_dev == 2064
            and actual.st_nlink == 1
            and actual.st_size == len(raw)
            and stat.S_IMODE(actual.st_mode) == 0o600,
            "authenticate the exclusive complete V86 evidence identity",
        )
    finally:
        os.close(descriptor)
    directory = os.open(
        str(ROOT / "docs/evidence"),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    actual, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(actual == raw, "reauthenticate all complete actual build graph bytes")


def self_test(
    previous: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> dict:
    prior = previous.self_test(v84, v83, v82, chain, base)
    base.need(
        prior["status"] == "PASS"
        and prior["version"] == 85
        and prior["authenticated_evidence_owner_lower_bound"] == 275
        and prior["authenticated_history_reference_lower_bound"] == 280
        and prior["lossless_family_evidence_pool_entry_count"] == 9
        and prior["lossless_actual_outcome_evidence_pool_entry_count"] == 1
        and prior["lossless_zig_source_evidence_pool_entry_count"] == 1
        and prior["actual_v15_candidate_worker_count"] == 13
        and prior["actual_v15_completed_suite_count"] == 8
        and prior["actual_v15_verified_passing_case_count"] == 12942
        and prior["actual_v15_infrastructure_failure_count"] == 5
        and prior["actual_v15_semantic_mismatch_count"] == "NOT MEASURED"
        and prior["actual_zig_candidate_matching"] == "NOT RUN"
        and prior["actual_zig_candidate_qualified"] is False
        and prior["actual_candidate_workers_started_by_graph"] == 0
        and prior["actual_compressed_evidence_owners_opened_by_graph"] == 0
        and prior["actual_clock_samples_by_graph"] == 0
        and prior["runtime_no_delegation"] == "NOT ESTABLISHED"
        and prior["qualified_candidate_count"] == 0
        and prior["final_holdout_opened"] is False,
        "inherit all 8,446 genuine V85 hostile controls and complete old history",
    )
    old, _ = authenticate_previous(previous, v84, v83, v82, chain, base)
    root_raw = read_fixed(ROOT_RECEIPT, "whole genuine Zig public root result")
    build_raw = read_fixed(BUILD_RECEIPT, "whole genuine Zig public build result")
    root = base.document(root_raw, "complete public Zig root result")
    actual_build = base.document(build_raw, "complete public Zig build result")
    base.need(
        base.canonical(root) == root_raw
        and base.canonical(actual_build) == build_raw,
        "reject partial or noncanonical actual Zig public build receipts",
    )
    validate_receipts(base, previous, old, root, actual_build)
    proof = make_build_proof(base, root, actual_build)
    build_pool = make_build_pool(base, proof)
    reference = make_build_reference(base, build_pool, proof)
    historical_pool = copy.deepcopy(old["lossless_family_evidence_pool"])
    rust_pool = copy.deepcopy(old["lossless_actual_outcome_evidence_pool"])
    zig_source_pool = copy.deepcopy(old["lossless_zig_source_evidence_pool"])
    historical_documents = {key: copy.deepcopy(old[key]) for key in v83.PROOF_KEYS}
    rust_actual = copy.deepcopy(old[v84.ACTUAL_KEY])
    zig_source = copy.deepcopy(old[previous.ZIG_KEY])
    _, zig_changes = make_changes(reference)
    families = copy.deepcopy(old["families"])
    for row in families:
        if row["family"] == "python":
            continue
        row["authenticated_evidence_owner_lower_bound"] = 277
        row["authenticated_history_reference_lower_bound"] = 282
        row[BUILD_KEY] = copy.deepcopy(reference)
        if row["family"] == "zig":
            row.update(copy.deepcopy(zig_changes))
    validate_families(
        base,
        previous,
        v84,
        v83,
        families,
        old["families"],
        historical_pool,
        rust_pool,
        zig_source_pool,
        build_pool,
        historical_documents,
        rust_actual,
        zig_source,
        proof,
        zig_changes,
    )
    rejected = 0

    def reject(label: str, check: object) -> None:
        nonlocal rejected
        try:
            assert callable(check)
            check()
        except Exception:
            rejected += 1
        else:
            base.need(False, "accepted fabricated actual native build: " + label)

    for name, genuine in (("private root", root), ("native build", actual_build)):
        for key in sorted(genuine):
            forged = copy.deepcopy(genuine)
            forged.pop(key)
            reject(
                "omitted full " + name + " receipt field " + key,
                lambda candidate=forged, receipt_name=name: validate_receipts(
                    base,
                    previous,
                    old,
                    candidate if receipt_name == "private root" else root,
                    candidate if receipt_name == "native build" else actual_build,
                ),
            )
    for key, value in (
        ("status", "FAIL"),
        ("source_sha256", "0" * 64),
        ("protocol_sha256", "0" * 64),
        ("contract_sha256", "0" * 64),
        ("frozen_graph_version", 85),
        ("frozen_evidence_owner_lower_bound", 275),
        ("frozen_history_reference_lower_bound", 280),
        ("candidate_correctness", "PASS"),
        ("performance", "1.5x"),
        ("holdout", "OPENED"),
        ("winner_selected", True),
    ):
        for name, genuine in (("root", root), ("build", actual_build)):
            forged = copy.deepcopy(genuine)
            forged[key] = value
            reject(
                "fabricated actual " + name + " receipt " + key,
                lambda candidate=forged, role=name: validate_receipts(
                    base,
                    previous,
                    old,
                    candidate if role == "root" else root,
                    candidate if role == "build" else actual_build,
                ),
            )
    for key, value in (
        ("status", "FAIL"),
        ("actual_process_count", 25),
        ("actual_source_snapshot_count", 5),
        ("candidate_correctness", "PASS"),
        ("candidate_matching", "PASS"),
        ("candidate_qualified", True),
        ("candidate_workers_started", 1),
        ("candidate_imports", 1),
        ("native_activations", 1),
        ("native_libraries_loaded", 1),
        ("stdlib_regex_engine_count", 1),
        ("external_regex_dependency_count", 1),
        ("cross_family_engine_count", 1),
        ("original_case_execution_denominator", 31236),
        ("supplemental_reference_case_count", 8243),
        ("clock_samples", 1),
        ("benchmark_files_opened", 1),
        ("holdout_files_opened", 1),
        ("matching_archives_opened", 1),
        ("performance", "1.5x"),
        ("holdout", "OPENED"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(actual_build)
        forged["complete_actual_build"][key] = value
        reject(
            "fabricated actual native build " + key,
            lambda candidate=forged: validate_receipts(
                base, previous, old, root, candidate
            ),
        )
    for index in range(26):
        forged = copy.deepcopy(actual_build)
        forged["complete_actual_build"]["processes"][index]["returncode"] = 1
        reject(
            "invented successful compiler process " + str(index),
            lambda candidate=forged: validate_receipts(
                base, previous, old, root, candidate
            ),
        )
    for index in (0, 3, 4, 13, 16, 17):
        for category in ("stdout", "stderr"):
            forged = copy.deepcopy(actual_build)
            forged["complete_actual_build"]["processes"][index][category][
                "base64"
            ] = "AA=="
            reject(
                "altered whole process output " + str(index) + ":" + category,
                lambda candidate=forged: validate_receipts(
                    base, previous, old, root, candidate
                ),
            )
    for index in range(2):
        for role in ("engine", "bridge"):
            forged = copy.deepcopy(root)
            forged["phases"][index]["native_outputs"][role]["owner"][
                "sha256"
            ] = "0" * 64
            reject(
                "substituted actual phase native owner " + str(index) + ":" + role,
                lambda candidate=forged: validate_receipts(
                    base, previous, old, candidate, actual_build
                ),
            )
    for key, value in (
        ("status", "FAIL"),
        ("all_native_artifacts_byte_identical", False),
        ("compiler_process_count", 25),
        ("unique_compiler_process_count", 25),
        ("independent_phase_count", 1),
        ("source_snapshot_count", 5),
    ):
        forged = copy.deepcopy(actual_build)
        forged["complete_actual_build"]["reproducibility"][key] = value
        reject(
            "invented reproducible compiler evidence " + key,
            lambda candidate=forged: validate_receipts(
                base, previous, old, root, candidate
            ),
        )
    reject("missing whole actual build pool", lambda: validate_build_pool(base, None, proof))
    digest = next(iter(build_pool["entries"]))
    for key, value in (
        ("schema", "invented-build-pool"),
        ("version", 2),
        ("hash_algorithm", "sha1"),
    ):
        forged_pool = copy.deepcopy(build_pool)
        forged_pool[key] = value
        reject(
            "fabricated complete actual build pool " + key,
            lambda candidate=forged_pool: validate_build_pool(base, candidate, proof),
        )
    for key, value in (
        ("proof_key", "invented-external-engine"),
        ("proof_schema", "invented-schema"),
        ("canonical_sha256", "0" * 64),
        ("canonical_bytes", 1),
    ):
        forged_pool = copy.deepcopy(build_pool)
        forged_pool["entries"][digest][key] = value
        reject(
            "forged complete native-build proof " + key,
            lambda candidate=forged_pool: validate_build_pool(base, candidate, proof),
        )
    for row in families:
        if row["family"] == "python":
            continue
        for key, value in (
            ("schema", "invented-reference"),
            ("proof_key", "external-regex-engine"),
            ("sha256", "0" * 64),
            ("canonical_bytes", 1),
        ):
            forged_reference = copy.deepcopy(row[BUILD_KEY])
            forged_reference[key] = value
            reject(
                "swapped real build family proof " + row["family"] + ":" + key,
                lambda candidate=forged_reference: resolve_build_reference(
                    base, build_pool, candidate
                ),
            )
    base.need(
        rejected >= 140,
        "reject any omitted compiler process, history, external engine or winner",
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 86,
        "status": "PASS",
        "previous_overview_version": 85,
        "actual_current_graph_predecessor_version": 85,
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ] + rejected,
        "authenticated_evidence_owner_lower_bound": 277,
        "authenticated_history_reference_lower_bound": 282,
        "lossless_family_evidence_pool_entry_count": 9,
        "lossless_family_references_per_family": 9,
        "lossless_actual_outcome_evidence_pool_entry_count": 1,
        "lossless_actual_outcome_references_per_family": 1,
        "lossless_zig_source_evidence_pool_entry_count": 1,
        "lossless_zig_source_references_per_family": 1,
        "lossless_zig_actual_build_evidence_pool_entry_count": 1,
        "lossless_zig_actual_build_references_per_family": 1,
        "lossless_zig_actual_build_reconstruction_status": "PASS",
        "lossless_v85_family_previous_byte_identity_status": "PASS",
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "supplemental_reference_case_count": 8244,
        "previous_v12_actual_rust_infrastructure_failure_count": 13,
        "previous_v13_actual_rust_infrastructure_failure_count": 13,
        "previous_v14_actual_rust_infrastructure_failure_count": 13,
        "actual_v15_candidate_worker_count": 13,
        "actual_v15_completed_suite_count": 8,
        "actual_v15_verified_passing_case_count": 12942,
        "actual_v15_infrastructure_failure_count": 5,
        "actual_v15_semantic_mismatch_count": "NOT MEASURED",
        "actual_zig_build_status": "PASS",
        "actual_zig_build_process_count": 26,
        "actual_zig_build_unique_process_count": 26,
        "actual_zig_independent_phase_count": 2,
        "actual_zig_source_snapshot_count": 6,
        "actual_zig_engine_sha256": ENGINE_SHA256,
        "actual_zig_bridge_sha256": BRIDGE_SHA256,
        "actual_zig_candidate_matching": "NOT RUN",
        "actual_zig_candidate_qualified": False,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_compressed_evidence_owners_opened_by_graph": 0,
        "actual_compressed_evidence_inflations_by_graph": 0,
        "actual_private_build_root_opens_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "final_holdout_opened": False,
        "performance": "NOT MEASURED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in V85:
        parser.add_argument("--previous-" + role + "-sha256")
    parser.add_argument("--root-receipt-sha256")
    parser.add_argument("--build-receipt-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v84, v83, v82, chain, base = load_previous()
        if options.self_test:
            base.need(
                all(
                    getattr(options, key) is None
                    for key in (
                        "source_sha256",
                        "source_bytes",
                        "root_receipt_sha256",
                        "build_receipt_sha256",
                        "inputs_sha256",
                        "summary_sha256",
                        "svg_sha256",
                    )
                )
                and all(
                    getattr(options, "previous_" + role + "_sha256") is None
                    for role in V85
                ),
                "source-only V86 graph never runs compilers, candidates or timers",
            )
            result = self_test(previous, v84, v83, v82, chain, base)
        else:
            _, assets = build(previous, v84, v83, v82, chain, base, options)
            if options.render:
                base.need(
                    all(
                        getattr(options, role + "_sha256") is None
                        for role in ("inputs", "summary", "svg")
                    ),
                    "reject preexisting or fabricated V86 native-build outputs",
                )
                for path, raw in assets.items():
                    publish(base, path, raw)
            else:
                for role, suffix in (
                    ("inputs", ".inputs.json"),
                    ("summary", ".json"),
                    ("svg", ".svg"),
                ):
                    path = OUTPUT + suffix
                    actual, _ = base.read_owner(
                        path,
                        base.checked(
                            getattr(options, role + "_sha256"),
                            "whole read-only actual V86 " + role,
                        ),
                        len(assets[path]),
                        private=True,
                    )
                    base.need(
                        actual == assets[path],
                        "reconstruct every complete actual V86 output byte: " + role,
                    )
            result = {
                "schema": SCHEMA
                + ("-published" if options.render else "-read-only-frozen-context"),
                "version": 86,
                "status": "PASS",
                "source_sha256": options.source_sha256,
                "source_bytes": options.source_bytes,
                **{
                    role + "_sha256": base.digest(raw)
                    for role, raw in (
                        ("inputs", assets[OUTPUT + ".inputs.json"]),
                        ("summary", assets[OUTPUT + ".json"]),
                        ("svg", assets[OUTPUT + ".svg"]),
                    )
                },
                "root_receipt_sha256": ROOT_RECEIPT[1],
                "build_receipt_sha256": BUILD_RECEIPT[1],
                "previous_overview_version": 85,
                "actual_current_graph_predecessor_version": 85,
                "authenticated_evidence_owner_lower_bound": 277,
                "authenticated_history_reference_lower_bound": 282,
                "lossless_family_evidence_pool_entry_count": 9,
                "lossless_family_references_per_family": 9,
                "lossless_actual_outcome_evidence_pool_entry_count": 1,
                "lossless_actual_outcome_references_per_family": 1,
                "lossless_zig_source_evidence_pool_entry_count": 1,
                "lossless_zig_source_references_per_family": 1,
                "lossless_zig_actual_build_evidence_pool_entry_count": 1,
                "lossless_zig_actual_build_references_per_family": 1,
                "lossless_zig_actual_build_reconstruction_status": "PASS",
                "lossless_v85_family_previous_byte_identity_status": "PASS",
                "original_suite_count": 13,
                "original_case_execution_denominator": 31237,
                "supplemental_reference_case_count": 8244,
                "actual_v15_candidate_worker_count": 13,
                "actual_v15_completed_suite_count": 8,
                "actual_v15_verified_passing_case_count": 12942,
                "actual_v15_infrastructure_failure_count": 5,
                "actual_zig_build_status": "PASS",
                "actual_zig_build_process_count": 26,
                "actual_zig_build_unique_process_count": 26,
                "actual_zig_independent_phase_count": 2,
                "actual_zig_source_snapshot_count": 6,
                "actual_zig_engine_sha256": ENGINE_SHA256,
                "actual_zig_bridge_sha256": BRIDGE_SHA256,
                "actual_zig_candidate_matching": "NOT RUN",
                "actual_zig_candidate_qualified": False,
                "actual_candidate_workers_started_by_graph": 0,
                "actual_compiler_processes_started_by_graph": 0,
                "actual_compressed_evidence_owners_opened_by_graph": 0,
                "actual_compressed_evidence_inflations_by_graph": 0,
                "actual_private_build_root_opens_by_graph": 0,
                "actual_clock_samples_by_graph": 0,
                "actual_hidden_cases_read_by_graph": 0,
                "runtime_no_delegation": "NOT ESTABLISHED",
                "qualified_candidate_count": 0,
                "final_holdout_opened": False,
                "performance": "NOT MEASURED",
                "outputs_written": bool(options.render),
            }
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V86 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
