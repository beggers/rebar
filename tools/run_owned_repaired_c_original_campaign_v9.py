#!/usr/bin/env python3
"""Freeze a cumulative, first-party, actual-build-bound C21 oracle campaign.

Source modes physically exclude every candidate, binary, private directory,
archive, graph, holdout, worker, clock, and source of operating-system entropy.
Only a separately pinned actual operation may activate the two-phase corrected
C21 native and run the unchanged original 31,237-case Python oracle.
"""

from __future__ import annotations

import ast
import builtins
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/run_owned_repaired_c_original_campaign_v9.py"
PROTOCOL = "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V9.md"
CONTRACT = "oracle/phase2/repaired-c-original-campaign-v9.json"
SCHEMA = "rebar-owned-repaired-c-original-campaign-v9"
LABEL = "phase2-v21-c-original-match-semantics-original-p0-v9"
DEVICE = 2064
ROOT_DEVICE = 2049
MAX_OWNER = 8 * 1024 * 1024
WORKER_TIMEOUT_SECONDS = 120
NATIVE_NAME = "_vm_native.cpython-314-x86_64-linux-gnu.so"
NATIVE_RELATIVE = "candidates/" + NATIVE_NAME
C21_NATIVE_SHA256 = (
    "7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60"
)
C21_NATIVE_BYTES = 163504
C21_VARIANT_SHA256 = (
    "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2"
)
C21_VARIANT_BYTES = 221647
C21_VARIANT_RELATIVE = (
    "candidates/c/variants/original_match_semantics_v1/vm_native.c"
)
ORIGINAL_NATIVE_SHA256 = (
    "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd"
)
ORIGINAL_NATIVE_INODE = 430300
ORIGINAL_NATIVE_BYTES = 149976
C18_NATIVE_SHA256 = (
    "f3794f963819a9af3798c1d97f32edcbc2a117f9ed20c56ec554a605de82eeae"
)
C8 = (
    (
        "tools/run_owned_repaired_c_original_campaign_v8.py",
        "16339f07efae669a6cf17a53dfb0b69e2f58bfb70858d6d5f6d0b83b24776ee6",
        56019, 431457,
    ),
    (
        "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V8.md",
        "f94cd39bb6a61cd8140ec3db7b208ec301512c516b5d5c5aab379d02d1a774bb",
        5360, 525367,
    ),
    (
        "oracle/phase2/repaired-c-original-campaign-v8.json",
        "8e82006beafdf535b9f2e80a82f3a01f6182dbd17ac0367d484428a438054a94",
        27773, 525389,
    ),
)
C21_BUILD = (
    (
        "tools/reproduce_owned_c_original_match_semantics_source_build_v21.py",
        "a1879dfefab15e91bfec95a74c4665d44e9894bef881c4945bccb3121be04726",
        32001, 429061,
    ),
    (
        "oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-SOURCE-BUILD-V21.md",
        "20844ff1c5a4b4908bc903d1a3c3e31e72c7f397b863741fce528ecd8b20d226",
        7097, 524815,
    ),
    (
        "oracle/phase2/c-original-match-semantics-source-build-v21.json",
        "a32651018f9c60cfa5963768ffd0cb4463e6c691556958dfd3cd3bea0a42a382",
        18982, 524816,
    ),
)
C21_BUILD_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-"
    "c-original-match-semantics-publication-receipt.json",
    "9475dd0c441a0440136f12425f94e6a4244e4cdc52d49f803e891f6663a647df",
    11878, 524817,
)
C21_ROOT_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-"
    "c-original-match-semantics-root-provenance-receipt.json",
    "8f913d623bf5bb4aec3669e9b3daa882df16aad6f2f1bc3db1f02f4988a8afa2",
    10837, 524818,
)
SEMANTIC = (
    (
        "tools/apply_owned_c_original_match_semantics_v1.py",
        "e2a67d418ab531a93bb2f894844a256460ba7fde70a6e1f6fb2ae82eba63b1c6",
        49528, 431406,
    ),
    (
        "oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-V1.md",
        "a71e397d87ecd538ee8a1eb218a6dbdf68849cc9598c208ddc83066dc9aec7b9",
        6310, 525326,
    ),
    (
        "oracle/phase2/c-original-match-semantics-v1.json",
        "6a7a53c77bd20664fed15a61d5ad5c1d7ae5354405e99e8d72427d44ab9f134c",
        14770, 525329,
    ),
)
REPLACEMENTS = {
    C8[0][0]: SOURCE,
    C8[1][0]: PROTOCOL,
    C8[2][0]: CONTRACT,
    "rebar-owned-repaired-c-original-campaign-v8": SCHEMA,
    "phase2-v18-c-subject-buffer-root-provenance-original-p0-v8": LABEL,
    "/tmp/rebar-phase2-repaired-c-original-campaign-v8":
        "/tmp/rebar-phase2-repaired-c-original-campaign-v9",
    ".rebar-c-original-campaign-v8-original-native":
        ".rebar-c-original-campaign-v9-original-native",
    ".rebar-c-original-campaign-v8-staged-native":
        ".rebar-c-original-campaign-v9-staged-native",
    "original-native-recovery-journal-v8.json":
        "original-native-recovery-journal-v9.json",
    "repaired-c-original-campaign-v8-c-":
        "repaired-c-original-campaign-v9-c-",
    "SOURCE FROZEN; ACTUAL C18 V8 ORIGINAL CAMPAIGN NOT RUN":
        "SOURCE FROZEN; ACTUAL C21 V9 ORIGINAL CAMPAIGN NOT RUN",
    "SOURCE FREEZE, PRESERVED ACTUAL V6 AND V7 FAILURES; "
    "NOT A V8 CANDIDATE RESULT":
        "SOURCE FREEZE, PRESERVED ACTUAL V6 AND V7 FAILURES; "
        "NOT A V9 CANDIDATE RESULT",
    "LATEST P0 V4 AND EXPLICIT C V8 ONLY":
        "LATEST P0 V4 AND EXPLICIT C21 V9 ONLY",
    "NOT RUN BY V8": "NOT RUN BY V9",
    "v8_candidate_correctness": "v9_candidate_correctness",
    "-v8": "-v9",
    "v8-original-native": "v9-original-native",
    "v8-staged-native": "v9-staged-native",
}


class CampaignError(Exception):
    """Reject a substituted build, original test, source, or worker."""


def need(condition: object, reason: str) -> None:
    if not condition:
        raise CampaignError(reason)


def clean_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and os.path.abspath(sys.executable) == PYTHON
         and sys.flags.isolated == 1
         and sys.flags.no_site == 1
         and sys.dont_write_bytecode is True
         and "re" not in sys.modules
         and "_sre" not in sys.modules
         and "ctypes" not in sys.modules
         and not any(item == "candidates" or item.startswith("candidates.")
                     for item in sys.modules),
         "require clean pinned matcher-free CPython 3.14.6 -I -B -S")


def exact_owner(owner: tuple) -> bytes:
    relative, expected, count, inode = owner
    allowed = C8 + C21_BUILD + (C21_BUILD_RECEIPT, C21_ROOT_RECEIPT) + SEMANTIC
    need(type(relative) is str and any(owner == item for item in allowed)
         and not relative.startswith(("/", "candidates/", "docs/evidence/"))
         and "holdout" not in relative.lower()
         and "benchmark" not in relative.lower()
         and not relative.endswith((".so", ".gz", ".zip", ".xz", ".tar"))
         and type(expected) is str and len(expected) == 64
         and all(char in "0123456789abcdef" for char in expected)
         and type(count) is int and 0 < count <= MAX_OWNER
         and type(inode) is int and inode > 0,
         "reject an unauthenticated or unsafe source-only owner")
    descriptor = os.open(
        ROOT + "/" + relative,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode)
             and before.st_dev == DEVICE
             and before.st_ino == inode
             and before.st_size == count
             and before.st_uid == os.geteuid()
             and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject a substituted complete frozen owner: " + relative)
        chunks = []
        remaining = count
        while remaining:
            block = os.read(descriptor, min(remaining, 262144))
            need(bool(block), "reject a truncated source owner: " + relative)
            chunks.append(block)
            remaining -= len(block)
        need(not os.read(descriptor, 1),
             "reject an expanded frozen source owner: " + relative)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        need(hashlib.sha256(raw).hexdigest() == expected
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject a concurrently changed source owner: " + relative)
        return raw
    finally:
        os.close(descriptor)


class V8ToV9(ast.NodeTransformer):
    """Retarget exact frozen controller identity, never an original test."""

    def __init__(self) -> None:
        self.identities = {key: 0 for key in REPLACEMENTS}
        self.version_assignments = 0

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if type(node.value) is str and node.value in REPLACEMENTS:
            self.identities[node.value] += 1
            return ast.copy_location(ast.Constant(REPLACEMENTS[node.value]), node)
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        node = self.generic_visit(node)
        if len(node.targets) != 1 or not isinstance(node.value, ast.Constant):
            return node
        if type(node.value.value) is not int or node.value.value != 8:
            return node
        target = node.targets[0]
        target_is_version = (
            isinstance(target, ast.Subscript)
            and isinstance(target.slice, ast.Constant)
            and target.slice.value == "version"
        )
        target_is_inner = (
            isinstance(target, ast.Attribute)
            and target.attr == "value"
            and (
                isinstance(target.value, ast.Name)
                and target.value.id == "value"
                or isinstance(target.value, ast.Attribute)
                and target.value.attr == "value"
                and isinstance(target.value.value, ast.Name)
                and target.value.value.id == "node"
            )
        )
        if target_is_version or target_is_inner:
            node.value.value = 9
            self.version_assignments += 1
        return node


def historical_controller() -> tuple[types.ModuleType, dict]:
    clean_runtime()
    raw = exact_owner(C8[0])
    tree = ast.parse(raw.decode("utf-8", "strict"), filename=C8[0][0])
    change = V8ToV9()
    corrected = ast.fix_missing_locations(change.visit(tree))
    critical = (C8[0][0], C8[1][0], C8[2][0],
                "rebar-owned-repaired-c-original-campaign-v8",
                "phase2-v18-c-subject-buffer-root-provenance-original-p0-v8",
                "/tmp/rebar-phase2-repaired-c-original-campaign-v8",
                ".rebar-c-original-campaign-v8-original-native",
                ".rebar-c-original-campaign-v8-staged-native",
                "original-native-recovery-journal-v8.json",
                "repaired-c-original-campaign-v8-c-")
    need(all(change.identities[item] >= 1 for item in critical)
         and change.version_assignments == 3,
         "reject an incomplete or broadened immutable C V8 retarget")
    historical = types.ModuleType("_rebar_owned_c_v9_authenticated_v8")
    historical.__file__ = ROOT + "/" + SOURCE
    historical.__package__ = ""
    exec(compile(corrected, historical.__file__, "exec", dont_inherit=True),
         historical.__dict__)
    need(historical.SOURCE == SOURCE
         and historical.PROTOCOL == PROTOCOL
         and historical.CONTRACT == CONTRACT
         and historical.SCHEMA == SCHEMA
         and historical.LABEL == LABEL
         and historical.MAX_VECTOR_PREFIX == 24
         and historical.MAX_TRANSPORT_DEPTH == 60
         and historical.V7_RECEIPT[1]
         == "bba4b8498a37db0bf9651c0bb040deaf96f9eef363ba6f2e2c923379d7fa5080",
         "reject incomplete cumulative, lossless V8 source provenance")
    clean_runtime()
    return historical, {
        "historical_source": {
            "path": C8[0][0], "sha256": C8[0][1],
            "bytes": C8[0][2], "inode": C8[0][3],
        },
        "exact_identity_replacements": dict(change.identities),
        "exact_version_assignments": change.version_assignments,
        "frozen_oracle_source_changes": 0,
        "frozen_runtime_guard_changes": 0,
        "actual_candidate_imports": 0,
        "actual_private_root_opens": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def owner_record(owner: tuple) -> dict:
    return {
        "path": owner[0], "sha256": owner[1], "bytes": owner[2],
        "device": DEVICE, "inode": owner[3],
        "mode": "0600", "nlink": 1,
    }


def validate_c21(build: object, receipt: object,
                 semantic: object, build_contract: object) -> dict:
    need(type(build) is dict and type(receipt) is dict
         and type(semantic) is dict and type(build_contract) is dict,
         "require complete independent C21 and Match semantics contracts")
    label = "phase2-v21-c-original-match-semantics-source-build"
    need(build.get("schema")
         == "rebar-owned-c-original-match-semantics-source-build-v21-"
            "durable-publication-receipt"
         and build.get("status") == "PASS"
         and build.get("build_status") == "PASS"
         and build.get("publication_pass_means")
         == "DURABLE FIRST-PARTY C MATCH-SOURCE BUILD ONLY"
         and build.get("version") == 21
         and build.get("family") == "c"
         and build.get("label") == label
         and build.get("source_sha256") == C21_BUILD[0][1]
         and build.get("protocol_sha256") == C21_BUILD[1][1]
         and build.get("contract_sha256") == C21_BUILD[2][1]
         and build.get("actual_compiler_process_count") == 14
         and build.get("expected_compiler_process_count") == 14
         and build.get("actual_source_apply_count") == 2
         and build.get("expected_source_apply_count") == 2
         and build.get("private_phase_count") == 2
         and build.get("distinct_phase_source_owner_count") == 4
         and build.get("distinct_native_artifact_count") == 2
         and build.get("byte_identical_native_artifacts") is True
         and build.get("variant_source_sha256") == C21_VARIANT_SHA256
         and build.get("variant_source_bytes") == C21_VARIANT_BYTES
         and build.get("adapter_source_sha256")
         == "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
         and build.get("semantic_source_sha256") == SEMANTIC[0][1]
         and build.get("semantic_contract_sha256") == SEMANTIC[2][1]
         and build.get("source_audit_status") == "PASS"
         and build.get("installed_native_inode_preserved") is True
         and build.get("installed_native_activated") is False
         and build.get("candidate_matching") == "NOT RUN"
         and build.get("candidate_correctness") == "NOT MEASURED"
         and build.get("candidate_workers_started") == 0
         and build.get("native_libraries_loaded") == 0
         and build.get("candidate_source_mutations") == 0
         and build.get("historical_archives_opened") == 0
         and build.get("hidden_cases_read") == 0
         and build.get("clock_samples") == 0
         and build.get("timing_trials_run") == 0
         and build.get("holdout") == "NOT OPENED"
         and build.get("performance") == "NOT MEASURED",
         "reject changed, incomplete, or falsely qualifying actual C21 build")
    need(receipt.get("schema")
         == "rebar-owned-c-original-match-semantics-source-build-v21-"
            "durable-root-provenance-receipt"
         and receipt.get("status") == "PASS"
         and receipt.get("publication_pass_means")
         == "DURABLE FIRST-PARTY C MATCH-SOURCE ROOT PROVENANCE ONLY"
         and receipt.get("version") == 21
         and receipt.get("family") == "c"
         and receipt.get("label") == label
         and receipt.get("source_sha256") == C21_BUILD[0][1]
         and receipt.get("protocol_sha256") == C21_BUILD[1][1]
         and receipt.get("contract_sha256") == C21_BUILD[2][1]
         and receipt.get("canonical_build_receipt_relative")
         == C21_BUILD_RECEIPT[0]
         and receipt.get("canonical_build_receipt_sha256")
         == C21_BUILD_RECEIPT[1]
         and receipt.get("canonical_build_status") == "PASS"
         and receipt.get("actual_compiler_process_count") == 14
         and receipt.get("expected_compiler_process_count") == 14
         and receipt.get("derived_variant_sha256") == C21_VARIANT_SHA256
         and receipt.get("derived_variant_bytes") == C21_VARIANT_BYTES
         and receipt.get("match_semantics_contract_sha256") == SEMANTIC[2][1]
         and receipt.get("installed_native_inode_preserved") is True
         and receipt.get("installed_native_activated") is False
         and receipt.get("candidate_matching") == "NOT RUN"
         and receipt.get("candidate_correctness") == "NOT MEASURED"
         and receipt.get("candidate_workers_started") == 0
         and receipt.get("native_libraries_loaded") == 0
         and receipt.get("canonical_sources_modified") is False
         and receipt.get("historical_archives_opened") == 0
         and receipt.get("hidden_cases_read") == 0
         and receipt.get("clock_samples") == 0
         and receipt.get("holdout") == "NOT OPENED"
         and receipt.get("performance") == "NOT MEASURED",
         "reject a crossed or invented actual C21 root-provenance receipt")
    need(build_contract.get("schema")
         == "rebar-owned-c-original-match-semantics-source-build-v21-source-freeze"
         and build_contract.get("version") == 21
         and build_contract.get("family") == "c"
         and build_contract.get("source", {}).get("sha256") == C21_BUILD[0][1]
         and build_contract.get("protocol", {}).get("sha256") == C21_BUILD[1][1]
         and build_contract.get("candidate_correctness") == "NOT MEASURED"
         and build_contract.get("holdout") == "NOT OPENED",
         "reject the separately frozen complete C21 native-build contract")
    correction = semantic.get("source_correction")
    need(semantic.get("schema")
         == "rebar-owned-c-original-match-semantics-v1-source-freeze"
         and semantic.get("version") == 1
         and semantic.get("source", {}).get("sha256") == SEMANTIC[0][1]
         and semantic.get("protocol", {}).get("sha256") == SEMANTIC[1][1]
         and type(correction) is dict
         and correction.get("derived_variant_sha256") == C21_VARIANT_SHA256
         and correction.get("derived_variant_bytes") == C21_VARIANT_BYTES
         and correction.get("prospective_variant_path") == C21_VARIANT_RELATIVE
         and correction.get("derived_variant_materialized") is False
         and correction.get("exact_changed_block_count") == 1
         and correction.get("pickle_protocols") == [0, 1, 2, 3, 4, 5]
         and correction.get("nested_exporter_acquisition_flags_preserved")
         == [0, 0, 284]
         and correction.get("nested_exporter_release_order_preserved") == "LIFO"
         and correction.get("match_copy_identity_source_preserved") is True
         and correction.get("match_deepcopy_identity_source_preserved") is True,
         "reject incomplete genuine first-party all-protocol Match correction")
    original = build.get("installed_native_before")
    need(type(original) is dict
         and original == build.get("installed_native_after")
         and original.get("path") == NATIVE_RELATIVE
         and original.get("sha256") == ORIGINAL_NATIVE_SHA256
         and original.get("bytes") == ORIGINAL_NATIVE_BYTES
         and original.get("device") == DEVICE
         and original.get("inode") == ORIGINAL_NATIVE_INODE
         and original.get("mode") == "0755"
         and original.get("nlink") == 1,
         "preserve the real original 075350 native and exact original inode")
    root = receipt.get("root")
    build_root = build.get("root")
    need(type(root) is dict and type(build_root) is dict
         and root.get("device") == ROOT_DEVICE
         and root.get("uid") == os.geteuid()
         and root.get("inode") == 11389900
         and root.get("mode") == "0700"
         and root.get("nofollow_directory_descriptor") is True
         and root.get("directory_scanned") is False
         and root.get("prefix") == "rebar-phase2-c-original-match-semantics-v21-"
         and type(root.get("path")) is str
         and root["path"].startswith(
             "/tmp/rebar-phase2-c-original-match-semantics-v21-"
         )
         and root.get("path") == build_root.get("path")
         and root.get("inode") == build_root.get("inode")
         and root.get("device") == build_root.get("device")
         and root.get("mode") == build_root.get("mode")
         and root.get("phase_count") == 2
         and root.get("distinct_source_owner_count") == 4
         and root.get("distinct_native_owner_count") == 2
         and root.get("byte_identical_native_output") is True,
         "reject an unauthenticated, scanned, or substituted C21 phase root")
    phases = root.get("phases")
    published = build.get("phases")
    need(type(phases) is list and len(phases) == 2
         and type(published) is list and phases == published,
         "require two genuinely cross-bound, independently built C21 phases")
    role_order = ("readelf_version", "gcc_version", "build_c_extension",
                  "extension_dynamic", "extension_symbols",
                  "extension_sections", "extension_notes")
    native_inodes = set()
    source_inodes = set()
    process_ids = []
    for phase, name in zip(phases, ("reference-a", "reference-b"), strict=True):
        need(type(phase) is dict and phase.get("name") == name
             and phase.get("device") == ROOT_DEVICE
             and phase.get("mode") == "0700"
             and type(phase.get("inode")) is int,
             "reject a reordered or fabricated actual C21 phase: " + name)
        native = phase.get("native_output")
        need(type(native) is dict
             and native.get("name") == NATIVE_NAME
             and native.get("sha256") == C21_NATIVE_SHA256
             and native.get("bytes") == C21_NATIVE_BYTES
             and native.get("device") == ROOT_DEVICE
             and native.get("mode") == "0700"
             and native.get("nlink") == 1
             and native.get("native_loaded") is False
             and type(native.get("inode")) is int,
             "reject a substituted, loaded, or stale C21 phase-native owner")
        native_inodes.add(native["inode"])
        owners = phase.get("source_owners")
        need(type(owners) is list and len(owners) == 2,
             "require both genuine corrected C and unchanged adapter owners")
        expected_owners = (
            ("match-corrected-native-source", "vm_native.c",
             C21_VARIANT_SHA256, C21_VARIANT_BYTES),
            ("unchanged-python-adapter", "vm_candidate.py",
             "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
             60707),
        )
        for owner, expected in zip(owners, expected_owners, strict=True):
            role, filename, fingerprint, size = expected
            need(type(owner) is dict and owner.get("role") == role
                 and owner.get("name") == filename
                 and owner.get("sha256") == fingerprint
                 and owner.get("bytes") == size
                 and owner.get("device") == ROOT_DEVICE
                 and owner.get("mode") == "0600"
                 and owner.get("nlink") == 1
                 and owner.get("exclusive_creation") is True
                 and owner.get("file_fsync_completed") is True
                 and owner.get("directory_fsync_completed") is True
                 and type(owner.get("inode")) is int,
                 "reject a crossed C21 native-source or Python-adapter owner")
            source_inodes.add(owner["inode"])
        processes = phase.get("processes")
        need(type(processes) is list and len(processes) == len(role_order),
             "require all seven real C21 compilation and inspection roles")
        for process, role in zip(processes, role_order, strict=True):
            need(type(process) is dict and process.get("role") == role
                 and process.get("phase") == name
                 and process.get("exit_status") == 0
                 and type(process.get("pid")) is int
                 and process["pid"] > 0,
                 "reject a failed or fabricated authentic C21 compiler role")
            process_ids.append(process["pid"])
    need(len(native_inodes) == 2 and len(source_inodes) == 4
         and len(process_ids) == 14 and len(set(process_ids)) == 14
         and process_ids == build.get("actual_compiler_process_ids")
         and process_ids == receipt.get("actual_compiler_process_ids")
         and C21_NATIVE_SHA256 not in
         (C18_NATIVE_SHA256, ORIGINAL_NATIVE_SHA256),
         "require 14 real process identities and two independently built C21 outputs")
    return root


def canonical_native_guard_owner(owner: object, role: str,
                                 inode: int) -> dict:
    required = frozenset((
        "family", "role", "relative", "absolute_path", "sha256", "bytes",
        "device", "inode", "mode", "nlink",
    ))
    need(role in ("bridge", "engine")
         and type(inode) is int and inode > 0
         and type(owner) is dict
         and frozenset(owner) == required
         and owner.get("family") == "c"
         and owner.get("role") == role
         and owner.get("relative") == NATIVE_RELATIVE
         and owner.get("absolute_path") == ROOT + "/" + NATIVE_RELATIVE
         and owner.get("sha256") == C21_NATIVE_SHA256
         and owner.get("bytes") == C21_NATIVE_BYTES
         and owner.get("device") == DEVICE
         and owner.get("inode") == inode
         and owner.get("mode") == 0o600
         and owner.get("nlink") == 1,
         "reject an incomplete, crossed, or invented original native guard owner")
    return {
        "role": role,
        "family": "c",
        "absolute_path": ROOT + "/" + NATIVE_RELATIVE,
        "relative": NATIVE_RELATIVE,
        "file_name": NATIVE_NAME,
        "sha256": C21_NATIVE_SHA256,
        "bytes": C21_NATIVE_BYTES,
        "size_bytes": C21_NATIVE_BYTES,
        "device": DEVICE,
        "inode": inode,
        "mode": 0o600,
        "uid": os.geteuid(),
        "nlink": 1,
        "native_loaded": False,
    }


def actual_c21_receipt_code(function: object) -> types.CodeType:
    replacements = {
        "actual_c18_build_receipt_sha256":
            "actual_c21_build_receipt_sha256",
        "actual_c18_root_receipt_sha256":
            "actual_c21_root_receipt_sha256",
    }
    need(type(function) is types.FunctionType,
         "retarget only an authenticated actual result-producing function")
    counts = {key: 0 for key in replacements}

    def transform(value: object) -> object:
        if type(value) is str and value in replacements:
            counts[value] += 1
            return replacements[value]
        if type(value) is tuple:
            return tuple(transform(item) for item in value)
        if isinstance(value, types.CodeType):
            return value.replace(
                co_consts=tuple(transform(item) for item in value.co_consts)
            )
        return value

    corrected = transform(function.__code__)
    need(type(corrected) is types.CodeType
         and all(count == 1 for count in counts.values()),
         "reject missing, duplicated, or broadened C21 receipt-key corrections")
    return corrected


def source_effects() -> dict:
    return {
        "actual_archives_opened": 0,
        "actual_benchmark_files_read": 0,
        "actual_candidate_imports": 0,
        "actual_candidate_source_owners_opened": 0,
        "actual_candidate_workers": 0,
        "actual_clock_samples": 0,
        "actual_compiler_processes": 0,
        "actual_graph_owners_opened": 0,
        "actual_guard_installations": 0,
        "actual_holdout_cases_read": 0,
        "actual_native_libraries_loaded": 0,
        "actual_network_requests": 0,
        "actual_private_roots_opened": 0,
        "actual_reference_workers": 0,
        "actual_source_entropy_requests": 0,
        "actual_workspace_mutations": 0,
    }


def prepare_c21_phase(root: dict, previous: types.ModuleType,
                      *, source_only: bool = False) -> tuple:
    need(source_only is False,
         "never open an actual C21 root from a source-only operation")
    phase = root["phases"][0]
    rootfd = previous.directory(root["path"], device=ROOT_DEVICE,
                                inode=root["inode"], mode=0o700)
    phasefd = None
    try:
        phasefd = os.open(
            "reference-a",
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0), dir_fd=rootfd,
        )
        info = os.fstat(phasefd)
        need(stat.S_ISDIR(info.st_mode)
             and info.st_dev == phase["device"]
             and info.st_ino == phase["inode"]
             and info.st_uid == os.geteuid()
             and stat.S_IMODE(info.st_mode) == 0o700,
             "reject a substituted exact receipt-bound C21 source phase")
        return rootfd, phasefd, phase
    except BaseException:
        if phasefd is not None:
            os.close(phasefd)
        os.close(rootfd)
        raise


def read_c21_native(root: dict, previous: types.ModuleType) -> tuple:
    rootfd = phasefd = nativefd = None
    try:
        rootfd, phasefd, phase = prepare_c21_phase(root, previous)
        expected = phase["native_output"]
        nativefd = os.open(
            NATIVE_NAME,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0), dir_fd=phasefd,
        )
        before = os.fstat(nativefd)
        need(stat.S_ISREG(before.st_mode)
             and before.st_dev == expected["device"]
             and before.st_ino == expected["inode"]
             and before.st_size == C21_NATIVE_BYTES
             and before.st_uid == os.geteuid()
             and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o700,
             "reject an unowned direct C21 native phase inode")
        payload = previous.hash_descriptor(
            nativefd, C21_NATIVE_BYTES, C21_NATIVE_SHA256
        )
        after = os.fstat(nativefd)
        need((before.st_dev, before.st_ino, before.st_size,
              before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject a native output changed during authenticated C21 streaming")
        actual = dict(expected)
        actual["uid"] = os.geteuid()
        actual["phase_name"] = phase["name"]
        return payload, actual
    finally:
        for descriptor in (nativefd, phasefd, rootfd):
            if descriptor is not None:
                os.close(descriptor)


def phase_source_descriptor(root: dict, previous: types.ModuleType) -> tuple:
    rootfd = phasefd = handle = None
    try:
        rootfd, phasefd, phase = prepare_c21_phase(root, previous)
        owner = phase["source_owners"][0]
        handle = os.open(
            "vm_native.c",
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0), dir_fd=phasefd,
        )
        before = os.fstat(handle)
        need(stat.S_ISREG(before.st_mode)
             and before.st_dev == owner["device"]
             and before.st_ino == owner["inode"]
             and before.st_size == C21_VARIANT_BYTES
             and before.st_uid == os.geteuid()
             and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject an unowned actual corrected C21 source-phase inode")
        previous.hash_descriptor(handle, C21_VARIANT_BYTES,
                                 C21_VARIANT_SHA256)
        after = os.fstat(handle)
        need((before.st_dev, before.st_ino, before.st_size,
              before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject a corrected C21 source changed during hashing")
        os.lseek(handle, 0, os.SEEK_SET)
        owned = handle
        handle = None
        return owned, dict(owner)
    finally:
        for descriptor in (handle, phasefd, rootfd):
            if descriptor is not None:
                os.close(descriptor)


def install_c21(historical: types.ModuleType,
                module: types.ModuleType, transform: dict) -> None:
    previous_configure = module.configure_previous
    previous_controls = module.source_controls

    def configure(previous: types.ModuleType) -> tuple:
        old, original_contract = previous_configure(previous)
        permitted = (
            (old.GOAL,) + tuple(old.P0) + tuple(old.PRODUCER)
            + tuple(old.GUARD) + tuple(previous.OLD)
            + tuple(previous.BUILD)
            + (previous.BUILD_RECEIPT, previous.ROOT_RECEIPT,
               previous.V1_MANIFEST, previous.V4_PRODUCER)
            + tuple(module.V6) + (module.V6_RECEIPT,)
            + tuple(historical.V7) + (historical.V7_RECEIPT,)
            + C8 + C21_BUILD + (C21_BUILD_RECEIPT, C21_ROOT_RECEIPT)
            + SEMANTIC
            + (historical.SURFACE_OWNER, historical.THREADED_OWNER)
        )
        unique = {}
        for owner in permitted:
            need(type(owner) is tuple and len(owner) == 4,
                 "require one complete bounded immutable C21 source owner")
            if owner[0] in unique:
                need(unique[owner[0]] == owner,
                     "reject a crossed duplicate frozen source owner")
            else:
                unique[owner[0]] = owner
        forbidden_parts = ("holdout", "benchmark")
        for path in unique:
            need(type(path) is str
                 and not path.startswith(("/", "candidates/", "docs/evidence/"))
                 and not any(token in path.lower() for token in forbidden_parts)
                 and not path.endswith((".so", ".gz", ".zip", ".tar", ".xz")),
                 "never allow native, candidate, graph, archive, or holdout: "
                 + str(path))
        old.STATIC_OWNERS = tuple(unique.values())
        old.OWNED_PATHS = frozenset(unique) | {SOURCE, PROTOCOL, CONTRACT}
        wall_base = old.SourceWall

        class StrictC21SourceWall(wall_base):
            def __enter__(self) -> object:
                active = super().__enter__()
                self.patch(os, "urandom", self.denied_callable(
                    "source-only C21 operating-system entropy"
                ))
                if hasattr(os, "getrandom"):
                    self.patch(os, "getrandom", self.denied_callable(
                        "source-only C21 private-root randomness"
                    ))
                return active

        old.SourceWall = StrictC21SourceWall
        previous_c18_authority = previous.actual_authority

        def authority() -> dict:
            result = previous_c18_authority()
            result.update({
                "family": "c",
                "label": LABEL,
                "build_source_sha256": C21_BUILD[0][1],
                "build_protocol_sha256": C21_BUILD[1][1],
                "build_contract_sha256": C21_BUILD[2][1],
                "build_receipt_sha256": C21_BUILD_RECEIPT[1],
                "root_receipt_sha256": C21_ROOT_RECEIPT[1],
                "native_engine_sha256": C21_NATIVE_SHA256,
                "native_bridge_sha256": C21_NATIVE_SHA256,
                "semantic_source_sha256": SEMANTIC[0][1],
                "semantic_protocol_sha256": SEMANTIC[1][1],
                "semantic_contract_sha256": SEMANTIC[2][1],
                "derived_variant_sha256": C21_VARIANT_SHA256,
                "v8_source_sha256": C8[0][1],
                "v8_protocol_sha256": C8[1][1],
                "v8_contract_sha256": C8[2][1],
                "previous_v7_failure_receipt_sha256":
                    historical.V7_RECEIPT[1],
            })
            return result

        previous.actual_authority = authority
        previous.collect_context = collect_context
        need(previous.RECOVERY_ROOT.endswith("-v9")
             and previous.BACKUP_NAME.endswith("v9-original-native")
             and previous.STAGE_NAME.endswith("v9-staged-native")
             and previous.JOURNAL_NAME == "original-native-recovery-journal-v9.json"
             and previous.BUILD_RECEIPT[1]
             == "4070feca7129fdcf3dc9762fae853649c68c722940af6157ecdcfa59d23e65ae"
             and previous.ROOT_RECEIPT[1]
             == "a231eec31b29ca796c75cee03b702a3e35a9195e74675c8f56209419dfeb03c8",
             "preserve immutable C18 history before explicit C21 activation")
        return old, original_contract

    def collect_context(old: types.ModuleType, parsed: dict,
                        *, controls: bool = False) -> tuple:
        clean_runtime()
        with old.SourceWall() as wall:
            source = old.read_dynamic(SOURCE, parsed["--source-sha256"])
            protocol = old.read_dynamic(PROTOCOL, parsed["--protocol-sha256"])
            need(source.endswith(b"\n") and not source.endswith(b"\n\n")
                 and protocol.endswith(b"\n")
                 and not protocol.endswith(b"\n\n"),
                 "freeze complete canonical C21 V9 source and protocol")
            raw = {owner[0]: old.read_owner(owner)
                   for owner in old.STATIC_OWNERS}
            producer = old.load_producer(raw[old.PRODUCER[0][0]])
            previous = active_previous[0]
            need(previous is not None,
                 "require the exact authenticated immutable original controller")
            p0 = previous.parse_document(
                producer, raw[old.P0[2][0]], "complete original Python P0 V4"
            )
            producer.validate_p0(p0)
            guard = previous.parse_document(
                producer, raw[old.GUARD[2][0]],
                "complete unchanged strict runtime guard",
            )
            producer.validate_runtime_guard_v2(guard)
            manifest = previous.parse_document(
                producer, raw[previous.V1_MANIFEST[0]],
                "complete original 31,237-case frozen manifest",
            )
            previous.validate_v1_manifest(manifest, producer)
            v8 = previous.parse_document(
                producer, raw[C8[2][0]], "complete cumulative C V8 contract"
            )
            need(v8.get("schema")
                 == "rebar-owned-repaired-c-original-campaign-v8-source-freeze"
                 and v8.get("version") == 8
                 and v8.get("source", {}).get("sha256") == C8[0][1]
                 and v8.get("protocol", {}).get("sha256") == C8[1][1]
                 and v8.get("goal_sha256") == old.GOAL[1]
                 and v8.get("holdout") == "NOT OPENED"
                 and v8.get("performance") == "NOT MEASURED",
                 "reject the genuinely frozen cumulative lossless V8 reporter")
            semantic = previous.parse_document(
                producer, raw[SEMANTIC[2][0]],
                "complete independently frozen first-party Match correction",
            )
            c21_contract = previous.parse_document(
                producer, raw[C21_BUILD[2][0]],
                "complete independently frozen C21 source-build contract",
            )
            build = previous.parse_document(
                producer, raw[C21_BUILD_RECEIPT[0]],
                "small genuinely published C21 build receipt",
            )
            root_receipt = previous.parse_document(
                producer, raw[C21_ROOT_RECEIPT[0]],
                "small genuinely published C21 root-provenance receipt",
            )
            root = validate_c21(build, root_receipt, semantic, c21_contract)
            prior_c18_build = previous.parse_document(
                producer, raw[previous.BUILD_RECEIPT[0]],
                "small genuine historical C18 build receipt",
            )
            prior_c18_root = previous.parse_document(
                producer, raw[previous.ROOT_RECEIPT[0]],
                "small genuine historical C18 root-provenance receipt",
            )
            previous.validate_build_and_root(prior_c18_build, prior_c18_root)
            v7_receipt = previous.parse_document(
                producer, raw[historical.V7_RECEIPT[0]],
                "small genuine actual C V7 failure receipt",
            )
            historical.validate_previous_receipt(v7_receipt, previous)
            state = {
                "source_raw": source,
                "protocol_raw": protocol,
                "producer_raw": raw[old.PRODUCER[0][0]],
                "guard_raw": raw[old.GUARD[0][0]],
                "phase1_v4": p0,
                "manifest": manifest,
                "build": build,
                "root_receipt": root_receipt,
                "root": root,
                "c21_build_contract": c21_contract,
                "semantic_contract": semantic,
                "v8_contract": v8,
                "v7_failure_receipt": v7_receipt,
                "historical_c18_build": prior_c18_build,
                "historical_c18_root": prior_c18_root,
                "wall_owner_count": len(old.STATIC_OWNERS),
                "historical_context": {
                    "candidate_source_reads": 0,
                    "native_reads": 0,
                    "private_root_reads": 0,
                    "archive_reads": 0,
                    "graph_reads": 0,
                    "holdout_reads": 0,
                },
            }
            expected = previous.contract_document(parsed, old, state)
            if parsed["mode"] != "--render-contract":
                actual_raw = old.read_dynamic(
                    CONTRACT, parsed["--contract-sha256"]
                )
                actual = previous.parse_document(
                    producer, actual_raw, "independently frozen complete C21 V9 contract"
                )
                need(actual_raw == producer.canonical(expected)
                     and actual == expected,
                     "reject an altered, unpinned, or incomplete C21 V9 contract")
            hostile = previous.hostile_controls(wall, old) if controls else []
            result = {
                "schema": SCHEMA + "-frozen-context",
                "status": "PASS",
                "family": "c",
                "label": LABEL,
                "source_sha256": parsed["--source-sha256"],
                "protocol_sha256": parsed["--protocol-sha256"],
                "contract_sha256": parsed.get("--contract-sha256"),
                "suite_count": 13,
                "case_execution_denominator": 31237,
                "named_private_waiver_count": 13,
                "separate_reference_case_count": 8244,
                "separate_reference_cases_counted_as_candidate_cases": False,
                "actual_c21_compiler_process_count": 14,
                "actual_c21_source_phase_count": 2,
                "build_receipt_sha256": C21_BUILD_RECEIPT[1],
                "root_receipt_sha256": C21_ROOT_RECEIPT[1],
                "corrected_phase_native_sha256": C21_NATIVE_SHA256,
                "corrected_phase_source_sha256": C21_VARIANT_SHA256,
                "previous_v7_failure_receipt_sha256": historical.V7_RECEIPT[1],
                "previous_v7_mismatch_lower_bound": 236,
                "expanded_holdout_proposed_case_count": 14155776,
                "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
                "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
                "candidate_matching": "NOT RUN",
                "candidate_correctness": "NOT MEASURED",
                "candidate_qualified": False,
                "runtime_non_delegation": "NOT ESTABLISHED",
                "performance": "NOT MEASURED",
                "memory": "NOT MEASURED",
                "undefined_behavior": "NOT MEASURED",
                "holdout": "NOT OPENED",
                "winner_selected": False,
                "source_only_effects": source_effects(),
                "hostile_controls": hostile,
                "physical_source_wall_read_count": wall.read_count,
            }
        clean_runtime()
        if parsed["mode"] in ("--run", "--worker", "--recover"):
            prepare_actual(previous, state)
        return producer, state, result

    def contract_document(parsed: dict, old: types.ModuleType,
                          state: dict, previous: types.ModuleType,
                          unused_contract: object) -> dict:
        del unused_contract
        frozen = state["v8_contract"]
        phase1 = frozen["phase_one_v4"]
        producer_info = frozen["frozen_original_producer"]
        previous_v7 = frozen["preserved_actual_c_v7_campaign"]
        need(phase1.get("status") == "PASS"
             and phase1.get("original_case_execution_denominator") == 31237
             and phase1.get("original_suite_count") == 13
             and phase1.get("named_private_waiver_count") == 13
             and phase1.get("separate_reference_case_count") == 8244
             and phase1.get("separate_reference_cases_counted_in_original_denominator")
             is False
             and producer_info.get("case_execution_denominator") == 31237
             and producer_info.get("suite_count") == 13
             and previous_v7.get("candidate_status") == "FAIL"
             and previous_v7.get("observed_semantic_mismatch_lower_bound") == 236
             and len(previous_v7.get("suite_outcomes", ())) == 13,
             "preserve all frozen original cases and every historical V7 failure")
        policy = dict(frozen["actual_operation_policy"])
        policy.update({
            "authorization": "EXPLICIT INDEPENDENTLY PINNED C21 --run ONLY",
            "required_authority": previous.actual_authority(),
            "native_build_identity": "ACTUAL PUBLISHED C21 ONLY",
            "future_c19_build_authorized": False,
            "historical_c18_native_activated": False,
            "original_installed_native_sha256": ORIGINAL_NATIVE_SHA256,
            "corrected_c21_native_sha256": C21_NATIVE_SHA256,
            "corrected_c21_source_sha256": C21_VARIANT_SHA256,
            "corrected_c21_source_materialized_in_workspace": False,
            "source_mode_candidate_paths_physically_denied": True,
            "source_mode_private_root_physically_denied": True,
            "source_mode_entropy_physically_denied": True,
            "source_mode_graphs_physically_denied": True,
            "source_mode_holdout_physically_denied": True,
            "source_mode_archive_physically_denied": True,
            "source_mode_native_physically_denied": True,
            "corrected_phase_source_owner_fd_attested": True,
            "actual_original_inode_restoration_required": True,
            "all_original_candidate_cases_required": 31237,
            "all_original_suite_workers_required": 13,
            "supplemental_cases_counted_as_candidate_cases": False,
            "strict_original_subinterpreter_guard_unchanged": True,
            "strict_original_subinterpreter_owner_field_count": 14,
            "strict_original_subinterpreter_owner_roles": ["bridge", "engine"],
            "strict_original_subinterpreter_owner_uid_required": True,
            "strict_original_subinterpreter_owner_equality_preserved": True,
            "truthful_actual_build_receipt_key":
                "actual_c21_build_receipt_sha256",
            "truthful_actual_root_receipt_key":
                "actual_c21_root_receipt_sha256",
            "historical_c18_receipt_keys_unchanged": True,
        })
        root = state["root"]
        return {
            "schema": SCHEMA + "-source-freeze",
            "version": 9,
            "phase": "PHASE 2: CANDIDATES",
            "status": "SOURCE FROZEN; ACTUAL C21 V9 ORIGINAL CAMPAIGN NOT RUN",
            "status_scope": (
                "CUMULATIVE V8 REPORTING, AUTHENTIC C21 BUILD, AND "
                "EXPLICIT ORIGINAL RUN AUTHORIZATION; NOT A CANDIDATE RESULT"
            ),
            "family": "c",
            "label": LABEL,
            "goal_sha256": old.GOAL[1],
            "source": {
                "path": SOURCE,
                "sha256": parsed["--source-sha256"],
                "bytes": len(state["source_raw"]),
            },
            "protocol": {
                "path": PROTOCOL,
                "sha256": parsed["--protocol-sha256"],
                "bytes": len(state["protocol_raw"]),
            },
            "pinned_cpython": frozen["pinned_cpython"],
            "phase_one_v4": phase1,
            "original_reference_manifest_v1":
                frozen["original_reference_manifest_v1"],
            "frozen_original_producer": producer_info,
            "strict_runtime_guard": frozen["runtime_guard"],
            "preserved_actual_c_v6_campaign":
                frozen["preserved_actual_c_v6_campaign"],
            "preserved_actual_c_v7_campaign": previous_v7,
            "preserved_full_v8_reporting_freeze": {
                "owners": [owner_record(item) for item in C8],
                "status": frozen["status"],
                "candidate_correctness": "NOT MEASURED",
                "source_specific_full_vector_digest_preserved": True,
                "lossless_surrogate_transport_preserved": True,
                "authentic_normalized_envelope_provenance_preserved": True,
                "all_13_failure_diagnostics_preserved": True,
            },
            "actual_first_party_c21_build": {
                "build_owner_triplet": [owner_record(item)
                                         for item in C21_BUILD],
                "actual_public_receipt": owner_record(C21_BUILD_RECEIPT),
                "actual_root_provenance_receipt":
                    owner_record(C21_ROOT_RECEIPT),
                "build_status": "PASS",
                "build_pass_means":
                    state["build"]["publication_pass_means"],
                "actual_distinct_compiler_process_count": 14,
                "actual_independent_phase_count": 2,
                "actual_distinct_phase_source_owner_count": 4,
                "actual_distinct_native_owner_count": 2,
                "byte_identical_corrected_native_outputs": True,
                "corrected_native_sha256": C21_NATIVE_SHA256,
                "corrected_native_bytes": C21_NATIVE_BYTES,
                "corrected_c_source_sha256": C21_VARIANT_SHA256,
                "corrected_c_source_bytes": C21_VARIANT_BYTES,
                "root_device": root["device"],
                "root_inode": root["inode"],
                "root_mode": root["mode"],
                "root_opened_in_source_mode": False,
                "native_opened_in_source_mode": False,
                "candidate_matching": "NOT RUN",
                "candidate_correctness": "NOT MEASURED",
            },
            "first_party_match_semantics": {
                "owners": [owner_record(item) for item in SEMANTIC],
                "source_correction":
                    state["semantic_contract"]["source_correction"],
                "phase_source_descriptor_required_only_in_actual_worker": True,
                "source_path_materialized_in_workspace": False,
                "external_regex_engine": "FORBIDDEN",
                "another_candidate_engine": "FORBIDDEN",
                "cpython_sre_engine": "FORBIDDEN",
                "fallback": "FORBIDDEN",
            },
            "authenticated_cumulative_controller_transform": transform,
            "actual_operation_policy": policy,
            "source_wall": {
                "owner_count": state["wall_owner_count"],
                "canonical_candidate_sources_allowed": False,
                "native_binary_allowed": False,
                "private_root_allowed": False,
                "compressed_archive_allowed": False,
                "graph_allowed": False,
                "holdout_allowed": False,
                "benchmark_allowed": False,
                "entropy_allowed": False,
            },
            "source_only_effects": source_effects(),
            "expanded_holdout": {
                "proposed_case_count": 14155776,
                "case_status": "NOT GENERATED; NOT OPENED",
                "final_protocol_status": "NOT FROZEN",
                "source_mode_holdout_files_read": 0,
            },
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualification": "NOT ESTABLISHED",
            "qualified_candidate_count": 0,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "supplemental_candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }

    def extra_controls(previous: types.ModuleType,
                       wall: object, old: types.ModuleType) -> list:
        answers = previous_controls(previous, wall, old)

        def reject(label: str, operation: object) -> None:
            denied = False
            try:
                operation()
            except Exception:
                denied = True
            need(denied, "source-only wall accepted forbidden operation: " + label)
            answers.append(label)

        readonly = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        prohibited = (
            ("canonical native", ROOT + "/" + NATIVE_RELATIVE),
            ("canonical C engine source", ROOT + "/candidates/_vm_native.c"),
            ("canonical C adapter", ROOT + "/candidates/vm_candidate.py"),
            ("historical C18 variant",
             ROOT + "/candidates/c/variants/subject_buffer_ownership_v1/vm_native.c"),
            ("unmaterialized C21 variant", ROOT + "/" + C21_VARIANT_RELATIVE),
            ("authentic C21 private phase root",
             "/tmp/rebar-phase2-c-original-match-semantics-v21-"
             "66118b4c946a061c863a4c643fd7185e"),
            ("unopened expanded holdout", ROOT + "/performance/holdout/forbidden.json"),
            ("unopened phase-three proposal",
             ROOT + "/oracle/phase3/expanded-sealed-holdout-v1.json"),
            ("unopened historical C overview",
             ROOT + "/docs/evidence/candidate-current-overview-v88.json"),
            ("unopened C21 compressed evidence",
             ROOT + "/oracle/phase2/evidence/native-source-build-v21-"
             "c-phase2-v21-c-original-match-semantics.json.gz"),
        )
        for label, path in prohibited:
            reject("physically deny " + label,
                   lambda target=path: os.open(target, readonly))
        reject("physically deny source-only cryptographic entropy",
               lambda: os.urandom(16))
        reject("physically deny actual C21 campaign",
               lambda: module.options(["--run"], previous))
        reject("physically deny actual C21 worker",
               lambda: module.options(["--worker"], previous))
        reject("physically deny actual C21 recovery",
               lambda: module.options(["--recover"], previous))
        for wrong in (C18_NATIVE_SHA256, ORIGINAL_NATIVE_SHA256,
                      "0" * 64):
            reject("reject stale or invented corrected C21 native " + wrong[:8],
                   lambda value=wrong: need(
                       value == C21_NATIVE_SHA256,
                       "reject stale original, C18, or guessed C21 native",
                   ))

        for role in ("bridge", "engine"):
            original_owner = {
                "family": "c", "role": role,
                "relative": NATIVE_RELATIVE,
                "absolute_path": ROOT + "/" + NATIVE_RELATIVE,
                "sha256": C21_NATIVE_SHA256,
                "bytes": C21_NATIVE_BYTES, "device": DEVICE,
                "inode": 917, "mode": 0o600, "nlink": 1,
            }
            exact = canonical_native_guard_owner(original_owner, role, 917)
            need(len(exact) == 14
                 and exact["role"] == role
                 and exact["file_name"] == NATIVE_NAME
                 and exact["size_bytes"] == C21_NATIVE_BYTES
                 and exact["uid"] == os.geteuid()
                 and exact["native_loaded"] is False,
                 "preserve exact frozen strict original child guard metadata")
            answers.append("preserve exact 14-field original child " + role)
            for field, replacement in (
                ("role", "rust"),
                ("sha256", "0" * 64),
                ("inode", 918),
                ("absolute_path", ROOT + "/candidates/forged.so"),
                ("nlink", 2),
            ):
                forged = dict(original_owner)
                forged[field] = replacement
                reject("reject forged child " + role + " " + field,
                       lambda item=forged, selected=role:
                           canonical_native_guard_owner(item, selected, 917))
            extra = dict(original_owner)
            extra["native_loaded"] = False
            reject("reject invented original child " + role + " metadata",
                   lambda item=extra, selected=role:
                       canonical_native_guard_owner(item, selected, 917))

        for holder, name in (
            (previous, "actual_worker"),
            (module, "early_worker_failure"),
            (module, "run_campaign"),
            (module, "publish_evidence"),
        ):
            function = getattr(holder, name)
            corrected = actual_c21_receipt_code(function)
            need(function.__code__ is not corrected,
                 "never mutate an original C18 receipt function in source mode")
            answers.append("attest actual-only truthful C21 receipt " + name)

        need(len(answers) >= 86
             and source_effects()["actual_candidate_source_owners_opened"] == 0,
             "preserve all cumulative V8 and dedicated physical C21 hostile gates")
        return answers

    def install_family(producer: types.ModuleType,
                       state: dict, previous: types.ModuleType) -> tuple:
        original = producer.family_spec("c")
        need(original.name == "c"
             and original.module == "candidates.vm_candidate"
             and original.bridge_module == "candidates._vm_native"
             and original.adapter_relative == "candidates/vm_candidate.py"
             and original.engine_relative == NATIVE_RELATIVE
             and original.bridge_relative == NATIVE_RELATIVE
             and original.combined_native is True
             and original.owned_ctypes is False,
             "preserve the exact guarded first-party C public matcher identity")
        owners = (
            (previous.ADAPTER[0], previous.ADAPTER[1], previous.ADAPTER[2]),
            (C21_VARIANT_RELATIVE, C21_VARIANT_SHA256, C21_VARIANT_BYTES),
        )
        exact = producer.FamilySpec(
            original.name, original.module, original.adapter_relative,
            original.bridge_module, original.engine_relative,
            original.bridge_relative, owners, original.combined_native,
            original.owned_ctypes,
        )
        producer.OWNED_SOURCES["c"] = owners
        producer.FAMILIES["c"] = exact
        original_owner_check = producer.exact_native_owners

        def prove_phase_owned(spec: object, pins: object,
                              source_pins: object) -> dict:
            need(spec is exact
                 and pins == {
                     "source": previous.ADAPTER[1],
                     "native_engine": C21_NATIVE_SHA256,
                     "native_bridge": C21_NATIVE_SHA256,
                 }
                 and source_pins == {
                     previous.ADAPTER[0]: previous.ADAPTER[1],
                     C21_VARIANT_RELATIVE: C21_VARIANT_SHA256,
                 },
                 "reject crossed, borrowed, or incomplete actual C21 source pins")
            phasefd, phase_owner = phase_source_descriptor(
                state["root"], previous
            )
            true_open = os.open

            def exact_phase_open(path: object, flags: object,
                                 mode: int = 0o777, **kwargs: object) -> int:
                if path != ROOT + "/" + C21_VARIANT_RELATIVE:
                    return true_open(path, flags, mode, **kwargs)
                need(type(flags) is int
                     and flags & os.O_ACCMODE == os.O_RDONLY
                     and flags & getattr(os, "O_NOFOLLOW", 0)
                     and not flags & (
                         getattr(os, "O_CREAT", 0)
                         | getattr(os, "O_TRUNC", 0)
                         | getattr(os, "O_APPEND", 0)
                     )
                     and kwargs.get("dir_fd") is None,
                     "reject a write, alias, or crossed corrected-phase source")
                os.lseek(phasefd, 0, os.SEEK_SET)
                return os.dup(phasefd)

            try:
                os.open = exact_phase_open
                result = original_owner_check(spec, pins, source_pins)
            finally:
                os.open = true_open
                os.close(phasefd)
            result["corrected_phase_c_source"] = phase_owner
            need(result["corrected_phase_c_source"]["sha256"]
                 == C21_VARIANT_SHA256,
                 "preserve the genuinely attested private C21 source owner")
            return result

        producer.exact_native_owners = prove_phase_owned
        pins = {
            "source": previous.ADAPTER[1],
            "native_engine": C21_NATIVE_SHA256,
            "native_bridge": C21_NATIVE_SHA256,
        }
        source_pins = {name: digest for name, digest, _ in owners}
        return exact, pins, source_pins

    def prepare_actual(previous: types.ModuleType, state: dict) -> None:
        need(state["build"]["variant_source_sha256"] == C21_VARIANT_SHA256
             and state["root_receipt"]["canonical_build_receipt_sha256"]
             == C21_BUILD_RECEIPT[1]
             and previous.NATIVE_SHA256 == C18_NATIVE_SHA256,
             "require complete historical validation before actual C21 overlay")
        previous.BUILD = C21_BUILD
        previous.BUILD_RECEIPT = C21_BUILD_RECEIPT
        previous.ROOT_RECEIPT = C21_ROOT_RECEIPT
        previous.NATIVE_SHA256 = C21_NATIVE_SHA256
        previous.NATIVE_BYTES = C21_NATIVE_BYTES
        previous.CORRECTED_SOURCE = (
            C21_VARIANT_RELATIVE, C21_VARIANT_SHA256,
            C21_VARIANT_BYTES, state["root"]["phases"][0]
            ["source_owners"][0]["inode"],
        )
        historical_record = previous.record

        def actual_phase_record(owner: tuple) -> dict:
            if owner is not previous.CORRECTED_SOURCE:
                return historical_record(owner)
            descriptor, actual = phase_source_descriptor(
                state["root"], previous
            )
            try:
                need(actual["sha256"] == C21_VARIANT_SHA256
                     and actual["bytes"] == C21_VARIANT_BYTES
                     and actual["device"] == ROOT_DEVICE
                     and actual["mode"] == "0600"
                     and actual["nlink"] == 1
                     and actual["role"] == "match-corrected-native-source",
                     "reject a fabricated C21 recovery-journal source owner")
                return {
                    "path": state["root"]["path"]
                    + "/reference-a/vm_native.c",
                    "sha256": actual["sha256"],
                    "bytes": actual["bytes"],
                    "device": actual["device"],
                    "inode": actual["inode"],
                    "mode": actual["mode"],
                    "nlink": actual["nlink"],
                    "role": actual["role"],
                    "phase": "reference-a",
                    "root_receipt_sha256": C21_ROOT_RECEIPT[1],
                    "prospective_workspace_relative": C21_VARIANT_RELATIVE,
                    "prospective_workspace_materialized": False,
                }
            finally:
                os.close(descriptor)

        previous.record = actual_phase_record
        historical_guard_owner = previous.native_guard_owner

        def actual_native_guard_owner(role: str, inode: int) -> dict:
            original = historical_guard_owner(role, inode)
            canonical = canonical_native_guard_owner(original, role, inode)
            descriptor = os.open(
                canonical["absolute_path"],
                os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0),
            )
            try:
                before = os.fstat(descriptor)
                need(stat.S_ISREG(before.st_mode)
                     and before.st_dev == canonical["device"]
                     and before.st_ino == canonical["inode"]
                     and before.st_size == canonical["bytes"]
                     and before.st_uid == canonical["uid"]
                     and before.st_nlink == canonical["nlink"]
                     and stat.S_IMODE(before.st_mode) == canonical["mode"],
                     "reject substituted actual first-party C21 guard native")
                previous.hash_descriptor(
                    descriptor, C21_NATIVE_BYTES, C21_NATIVE_SHA256
                )
                after = os.fstat(descriptor)
                need((before.st_dev, before.st_ino, before.st_size,
                      before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
                     == (after.st_dev, after.st_ino, after.st_size,
                         after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
                     "reject actual C21 child guard native changed during hashing")
                return canonical
            finally:
                os.close(descriptor)

        previous.native_guard_owner = actual_native_guard_owner
        for holder, name in (
            (previous, "actual_worker"),
            (module, "early_worker_failure"),
            (module, "run_campaign"),
            (module, "publish_evidence"),
        ):
            function = getattr(holder, name)
            function.__code__ = actual_c21_receipt_code(function)
        previous.read_root_phase = (
            lambda root: read_c21_native(root, previous)
        )
        previous.activate_corrected_family = (
            lambda producer: install_family(producer, state, previous)
        )
        previous_validate = previous.validate_build_and_root

        def validate_active(build: dict, receipt: dict) -> dict:
            if build.get("version") == 21 and receipt.get("version") == 21:
                return validate_c21(
                    build, receipt, state["semantic_contract"],
                    state["c21_build_contract"],
                )
            return previous_validate(build, receipt)

        previous.validate_build_and_root = validate_active

    active_previous: list = [None]

    def remember(previous: types.ModuleType) -> tuple:
        result = configure(previous)
        active_previous[0] = previous
        return result

    module.configure_previous = remember
    module.contract_document = contract_document
    module.source_controls = extra_controls


def main(arguments: list[str]) -> int:
    history, transform = historical_controller()
    original, prior_transform = history.bootstrap_historical()
    history.install_corrections(original, prior_transform)
    install_c21(history, original, transform)
    return original.main(arguments)


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as error:
        os.write(2, (
            "C21 original campaign V9: "
            + type(error).__qualname__ + ": " + str(error) + "\n"
        ).encode("utf-8", "backslashreplace"))
        raise SystemExit(2)
