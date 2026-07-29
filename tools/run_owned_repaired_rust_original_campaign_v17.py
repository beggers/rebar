#!/usr/bin/env python3
"""Freeze the complete original Rust campaign on the real V21 captured build.

Source-only operations never activate a matcher, compiler, archive, private
root, clock, or holdout. A separately authorized complete campaign reuses the
authenticated original V16 controller, genuine V5 observers, unchanged V2
physical guard, and reversible four-role journal with every actual V21 native
owner and the cumulative first-party captured bridge bound explicitly.
"""

from __future__ import annotations

import ast
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SOURCE = "tools/run_owned_repaired_rust_original_campaign_v17.py"
PROTOCOL = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V17.md"
CONTRACT = "oracle/phase2/repaired-rust-original-campaign-v17.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v17"
VERSION = 17
FAMILY = "rust"
BUILD_LABEL = "phase2-v21-rust-captured-findall-root-provenance"
LABEL = BUILD_LABEL + "-original-p0-v17"
RECOVERY_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v17-"
RECOVERY_ROOT = "/tmp/" + RECOVERY_PREFIX + BUILD_LABEL + "-original-p0"
LOCALE_PATH = "/tmp/rebar-official-locale-proof-0EdjeBJ1lS"
CASE_COUNT = 31_237
WORKER_COUNT = 13
SUPPLEMENTAL_COUNT = 8_244
PRIVATE_WAIVER_COUNT = 13
HOLDOUT_CASE_COUNT = 14_155_776
ROOT_DEVICE = 2049
ROOT_INODE = 11675087
ROOT_PATH = "/tmp/rebar-phase2-native-build-v9-rust-rnxxta4f"
ENGINE_SHA = "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
ENGINE_BYTES = 658344
BRIDGE_SHA = "bfc9c55ffd3e6bedb6a0a82457c347d362adc9299b8cb107f98dc02a66ea1a43"
BRIDGE_BYTES = 148792
PHASE_NATIVE_INODES = (
    (11675207, 11675213),
    (11675237, 11675243),
)
CAPTURE_SHA = "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a"
CAPTURE_BYTES = 179520
ADAPTER_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
ADAPTER_BYTES = 31934
ARCHIVE_SHA = "19e6bb346fd0a6a510772db6071899696bce2906cc92674a2bd757047cbf9372"
ARCHIVE_BYTES = 108632
ARCHIVE_INODE = 524893
PLAIN_SHA = "3e96dd2686cb1252ea3dbee7254723a9a31cb16f0a26cad58276c677fe6c9295"
PLAIN_BYTES = 760199

V16 = (
    ("tools/run_owned_repaired_rust_original_campaign_v16.py",
     "4705f5afb0639812e4902a455c11cee469b78a2a8f78bd64e1bf3388390d060e",
     153060, 429584),
    ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V16.md",
     "b168f394244c1f2e2f1051a0d9ed038fd11b596708667b9c8dc196b3f8f2c66f",
     13426, 525263),
    ("oracle/phase2/repaired-rust-original-campaign-v16.json",
     "1879abea2cfc3665ec5e0eeb9549286f1d566806f4f49482064855199a86d46b",
     15406, 525264),
)
V21 = (
    ("tools/reproduce_owned_rust_captured_findall_source_build_v21.py",
     "bc5f5b4efd8b20a564692e14f972c77267c58ac44a560b432a0a1cc38e794c58",
     100150, 430883),
    ("oracle/phase2/RUST-CAPTURED-FINDALL-SOURCE-BUILD-V21.md",
     "d7c137d2432c2f28f4b6b26fdde3a591b92f7d62e6018d047cfa0b3ccfe0a8c4",
     4943, 524834),
    ("oracle/phase2/rust-captured-findall-source-build-v21.json",
     "61e14e1d47f55759a73721635594b69ba098541bc83c9046c99c0c282223fd4a",
     18420, 524837),
)
V21_PUBLICATION = (
    "oracle/phase2/evidence/native-source-build-v21-rust-"
    "phase2-v21-rust-captured-findall-root-provenance-"
    "publication-receipt.json",
    "bc3ebdc835ef6a89d351c4541863274d410e2685d35eacdc9668f4bf3a474102",
    3502, 524894,
)
V21_ROOT = (
    "oracle/phase2/evidence/native-source-build-v21-rust-"
    "phase2-v21-rust-captured-findall-root-provenance-"
    "root-provenance-receipt.json",
    "73cee9c0a4f44d113da96b505eb0e9224577584b75c347e6fd351995d1d09a4e",
    6306, 524895,
)
CAPTURE_OWNER = (
    "candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/"
    "py_bridge.c",
    CAPTURE_SHA,
    CAPTURE_BYTES,
    524770,
)
PROPOSAL = (
    ("tools/verify_expanded_sealed_holdout_v1.py",
     "3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309",
     27311, 428806),
    ("oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md",
     "818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4",
     13237, 524760),
    ("oracle/phase3/expanded-sealed-holdout-v1.json",
     "676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76",
     6628, 524761),
)
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768),
    ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120),
    ("shape_v2", 10240), ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
CORRECTED_SOURCES = (
    ("candidates/rust_candidate.py", ADAPTER_SHA, ADAPTER_BYTES),
    ("candidates/rust/py_bridge.c", CAPTURE_SHA, CAPTURE_BYTES),
    ("candidates/rust/Cargo.toml",
     "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
    ("candidates/rust/Cargo.lock",
     "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
    ("candidates/rust/src/lib.rs",
     "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
    ("candidates/rust/src/newline.rs",
     "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
    ("candidates/rust/src/search.rs",
     "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
    ("candidates/rust/src/stack.rs",
     "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
    ("candidates/rust/src/unicode_tables.rs",
     "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
)


class CampaignError(Exception):
    """Frozen V21 provenance, source-only isolation, or original integrity failed."""


def need(value: object, reason: str) -> None:
    if not value:
        raise CampaignError(reason)


def exact_sha(value: object, name: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(ch in "0123456789abcdef" for ch in value),
         "require an exact SHA-256 for " + name)
    assert isinstance(value, str)
    return value


def read_owner(owner: tuple, *, maximum: int = 4 * 1024 * 1024) -> bytes:
    path, fingerprint, count, inode = owner
    need(type(path) is str and path and not path.startswith("/")
         and ".." not in path.split("/")
         and not path.endswith((".gz", ".so"))
         and type(count) is int and 0 < count <= maximum
         and type(inode) is int and inode > 0,
         "reject an archive, native library, private root, or unsafe owner")
    exact_sha(fingerprint, path)
    descriptor = os.open(
        ROOT + "/" + path,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == 2064
             and before.st_ino == inode and before.st_size == count
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject a substituted frozen V17 input: " + path)
        pieces: list[bytes] = []
        left = count
        while left:
            part = os.read(descriptor, min(left, 262144))
            need(bool(part), "reject a truncated frozen input: " + path)
            pieces.append(part)
            left -= len(part)
        need(not os.read(descriptor, 1),
             "reject an expanded frozen input: " + path)
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        need(hashlib.sha256(raw).hexdigest() == fingerprint
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject changed frozen input: " + path)
        return raw
    finally:
        os.close(descriptor)


def dynamic_owner(path: str, fingerprint: str) -> tuple:
    need(path in (SOURCE, PROTOCOL, CONTRACT),
         "reject an unrelated live V17 owner")
    exact_sha(fingerprint, path)
    descriptor = os.open(
        ROOT + "/" + path,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        found = os.fstat(descriptor)
        need(stat.S_ISREG(found.st_mode) and found.st_dev == 2064
             and found.st_uid == os.geteuid() and found.st_nlink == 1
             and stat.S_IMODE(found.st_mode) == 0o600
             and 0 < found.st_size <= 1024 * 1024,
             "reject an unsafe V17 freeze owner: " + path)
        return path, fingerprint, found.st_size, found.st_ino
    finally:
        os.close(descriptor)


def runtime() -> None:
    need(sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode and sys.executable == PYTHON
         and sys.version_info[:3] == (3, 14, 6),
         "require pinned CPython 3.14.6 with -I -B -S")
    need("re" not in sys.modules and "_sre" not in sys.modules
         and "regex" not in sys.modules and "ctypes" not in sys.modules
         and "inspect" not in sys.modules and "tokenize" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "reject a preloaded matcher, inspect, native loader, or candidate")


def load_predecessor() -> tuple[types.ModuleType, dict,
                                types.ModuleType, types.ModuleType]:
    raw = read_owner(V16[0])
    read_owner(V16[1])
    read_owner(V16[2])
    module = types.ModuleType("_rebar_v17_immutable_v16_original_campaign")
    module.__file__ = ROOT + "/" + V16[0][0]
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    need(module.SOURCE == V16[0][0]
         and module.PROTOCOL == V16[1][0]
         and module.CONTRACT == V16[2][0]
         and module.SCHEMA == "rebar-owned-repaired-rust-original-campaign-v16"
         and tuple(module.SUITES) == SUITES
         and module.CASE_COUNT == CASE_COUNT
         and module.WORKER_COUNT == WORKER_COUNT
         and module.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT
         and callable(module.verify_frozen_context)
         and callable(module.source_hostile_controls)
         and callable(module.bind_v16_legacy)
         and callable(module.install_failure_preservation),
         "reject incomplete original V16 four-role worker and recovery")
    original, base, guard = module.verify_frozen_context(
        V16[0][1], V16[1][1], V16[2][1],
    )
    need(original.get("status") == "PASS"
         and original.get("phase1_v4_reference_readiness") == "PASS"
         and original.get("suite_count") == WORKER_COUNT
         and original.get("case_execution_denominator") == CASE_COUNT
         and original.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
         and original.get("supplemental_case_count") == SUPPLEMENTAL_COUNT
         and original.get("supplemental_cases_counted_in_original_denominator")
         is False
         and original.get("actual_candidate_workers_started") == 0
         and original.get("actual_hidden_cases_read") == 0
         and original.get("runtime_non_delegation") == "NOT ESTABLISHED"
         and original.get("v15_actual_completed_suite_count") == 8
         and original.get("v15_actual_verified_passing_case_count") == 12942
         and original.get("v15_actual_infrastructure_failure_count") == 5
         and tuple((row.get("id"), row.get("case_execution_count"))
                   for row in original.get("suites", ())) == SUITES,
         "authenticate all frozen original suites, actual losses, and waivers")
    need(type(base) is types.ModuleType and type(guard) is types.ModuleType
         and tuple(base.SUITES) == SUITES
         and tuple(base.PRIVATE_WAIVERS) == tuple(original["named_private_waivers"])
         and base.PYTHON_SHA256 == PYTHON_SHA
         and callable(guard.canonical) and callable(base.parse_document),
         "require genuine first-party phase-one producer and strict runtime guard")
    runtime()
    return module, original, base, guard


def document(base: types.ModuleType, guard: types.ModuleType,
             raw: bytes, label: str) -> dict:
    value = base.parse_document(guard, raw, label)
    need(type(value) is dict and guard.canonical(value) == raw,
         "require complete canonical first-party document: " + label)
    return value


def validate_v21_documents(build: dict, root: dict,
                           freeze: dict) -> dict:
    need(type(build) is dict and type(root) is dict and type(freeze) is dict,
         "reject non-canonical captured V21 native provenance")
    need(build.get("schema")
         == "rebar-phase2-owned-rust-captured-findall-source-build-v21-"
            "durable-publication-receipt"
         and build.get("status") == "PASS"
         and build.get("build_status") == "PASS"
         and build.get("family") == FAMILY
         and build.get("label") == BUILD_LABEL
         and build.get("source_sha256") == V21[0][1]
         and build.get("protocol_sha256") == V21[1][1]
         and build.get("contract_sha256") == V21[2][1]
         and build.get("expected_actual_compiler_process_count") == 28
         and build.get("actual_compiler_process_count") == 28
         and build.get("combined_bridge_sha256") == CAPTURE_SHA
         and build.get("combined_bridge_bytes") == CAPTURE_BYTES
         and build.get("combined_bridge_overlay_apply_count") == 2
         and build.get("corrected_public_adapter_sha256") == ADAPTER_SHA
         and build.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
         and build.get("corrected_public_adapter_overlay_apply_count") == 2
         and build.get("archive_sha256") == ARCHIVE_SHA
         and build.get("archive_bytes") == ARCHIVE_BYTES
         and build.get("uncompressed_sha256") == PLAIN_SHA
         and build.get("uncompressed_bytes") == PLAIN_BYTES
         and build.get("candidate_workers_started") == 0
         and build.get("native_libraries_loaded") == 0
         and build.get("hidden_cases_read") == 0
         and build.get("holdout") == "NOT OPENED",
         "reject stale, incomplete, foreign, or synthetic V21 publication")
    publication = build.get("archive_publication")
    need(type(publication) is dict
         and publication.get("sha256") == ARCHIVE_SHA
         and publication.get("bytes") == ARCHIVE_BYTES
         and publication.get("device") == 2064
         and publication.get("inode") == ARCHIVE_INODE
         and publication.get("exclusive_creation") is True
         and publication.get("file_fsync_completed") is True
         and publication.get("same_inode_readback_verified") is True,
         "authenticate V21 archive metadata exclusively from its small receipt")
    need(root.get("schema")
         == "rebar-phase2-owned-rust-captured-findall-source-build-v21-"
            "durable-root-provenance-receipt"
         and root.get("status") == "PASS"
         and root.get("family") == FAMILY
         and root.get("label") == BUILD_LABEL
         and root.get("source_sha256") == V21[0][1]
         and root.get("protocol_sha256") == V21[1][1]
         and root.get("contract_sha256") == V21[2][1]
         and root.get("canonical_build_status") == "PASS"
         and root.get("canonical_build_receipt_relative") == V21_PUBLICATION[0]
         and root.get("canonical_build_receipt_sha256") == V21_PUBLICATION[1]
         and root.get("canonical_build_receipt_bytes") == V21_PUBLICATION[2]
         and root.get("canonical_build_receipt_device") == 2064
         and root.get("canonical_build_receipt_inode") == V21_PUBLICATION[3]
         and root.get("canonical_build_archive_sha256") == ARCHIVE_SHA
         and root.get("canonical_build_archive_bytes") == ARCHIVE_BYTES
         and root.get("canonical_build_archive_opened") is False
         and root.get("cumulative_captured_bridge_sha256") == CAPTURE_SHA
         and root.get("cumulative_captured_bridge_bytes") == CAPTURE_BYTES
         and root.get("actual_compiler_process_count") == 28
         and root.get("expected_compiler_process_count") == 28
         and root.get("actual_source_phase_count") == 2
         and root.get("bridge_overlay_apply_count") == 2
         and root.get("adapter_overlay_apply_count") == 2
         and root.get("candidate_workers_started") == 0
         and root.get("historical_archives_opened") == 0
         and root.get("native_libraries_loaded") == 0
         and root.get("hidden_cases_read") == 0
         and root.get("clock_samples") == 0
         and root.get("runtime_non_delegation") == "NOT ESTABLISHED"
         and root.get("holdout") == "NOT OPENED"
         and root.get("expanded_holdout_proposal_case_count") == HOLDOUT_CASE_COUNT
         and root.get("expanded_holdout_cases_generated") == 0
         and root.get("expanded_holdout_cases_opened") == 0,
         "reject forged or stale actual V21 callback-bound private provenance")
    info = root.get("root")
    need(type(info) is dict and info.get("path") == ROOT_PATH
         and info.get("device") == ROOT_DEVICE
         and info.get("inode") == ROOT_INODE
         and info.get("mode") == "0700"
         and info.get("phase_count") == 2
         and info.get("directory_scanned") is False,
         "bind the actual V21 private root from receipt bytes without opening it")
    phases = info.get("phases")
    need(type(phases) is list and len(phases) == 2,
         "require both genuine, independent V21 build phases")
    distinct: set[tuple[int, int]] = set()
    for position, name in enumerate(("reference-a", "reference-b")):
        phase = phases[position]
        need(type(phase) is dict and phase.get("name") == name
             and phase.get("absolute_path") == ROOT_PATH + "/" + name
             and phase.get("device") == ROOT_DEVICE
             and phase.get("mode") == "0700",
             "reject exchanged actual captured Rust phase: " + name)
        outputs = phase.get("native_outputs")
        need(type(outputs) is list and len(outputs) == 2,
             "require exactly the two actual owned V21 phase artifacts")
        for role, fingerprint, count, filename, mode in (
            ("engine", ENGINE_SHA, ENGINE_BYTES, "_rust_engine.so", "0600"),
            ("bridge", BRIDGE_SHA, BRIDGE_BYTES,
             "_rust_bridge.cpython-314-x86_64-linux-gnu.so", "0700"),
        ):
            index = 0 if role == "engine" else 1
            owner = outputs[index]
            need(type(owner) is dict and owner.get("role") == role
                 and owner.get("file_name") == filename
                 and owner.get("sha256") == fingerprint
                 and owner.get("bytes") == count
                 and owner.get("device") == ROOT_DEVICE
                 and type(owner.get("inode")) is int
                 and owner["inode"] == PHASE_NATIVE_INODES[position][index]
                 and owner.get("uid") == os.geteuid()
                 and owner.get("mode") == mode
                 and owner.get("nlink") == 1
                 and owner.get("native_loaded") is False
                 and owner.get("absolute_path")
                 == ROOT_PATH + "/" + name + "/native/" + filename,
                 "reject substituted actual V21 " + name + " " + role)
            identity = (owner["device"], owner["inode"])
            need(identity not in distinct,
                 "reject duplicated actual V21 native inode: " + role)
            distinct.add(identity)
    need(len(distinct) == 4,
         "require four actual distinct first-party captured native artifacts")
    need(freeze.get("schema")
         == "rebar-phase2-owned-rust-captured-findall-source-build-v21-"
            "source-freeze"
         and freeze.get("version") == 21
         and freeze.get("source", {}).get("path") == V21[0][0]
         and freeze.get("source", {}).get("sha256") == V21[0][1]
         and freeze.get("protocol", {}).get("path") == V21[1][0]
         and freeze.get("protocol", {}).get("sha256") == V21[1][1],
         "authenticate the exact actual V21 captured-build source freeze")
    feature = freeze.get("independently_reviewed_captured_feature")
    proposal = freeze.get("published_expanded_sealed_holdout_proposal")
    p0 = freeze.get("phase1_v4_readiness")
    effects = freeze.get("source_only_effects")
    need(type(feature) is dict
         and feature.get("changed_first_party_function_count") == 1
         and feature.get("changed_function") == "rust_append_batched_findall"
         and feature.get("historical_capture_findall_case_count") == 48
         and feature.get("historical_materialized_capture_count") == 44
         and feature.get("historical_empty_capture_count") == 4
         and feature.get("new_variant_correctness") == "NOT MEASURED"
         and feature.get("variant", {}).get("sha256") == CAPTURE_SHA
         and feature.get("variant", {}).get("bytes") == CAPTURE_BYTES,
         "preserve the authenticated cumulative captured first-party closure")
    need(type(proposal) is dict
         and proposal.get("case_count") == HOLDOUT_CASE_COUNT
         and proposal.get("proposal_status") == "PRE-PHASE-3 PROPOSAL"
         and proposal.get("proposal_cases_generated") == 0
         and proposal.get("proposal_cases_opened") == 0
         and proposal.get("proposal_verifier_executed") is False
         and proposal.get("secret_status") == "NOT GENERATED"
         and proposal.get("qualified_independent_family_count") == 0
         and proposal.get("owners", {}).get("source", {}).get("sha256")
         == PROPOSAL[0][1]
         and proposal.get("owners", {}).get("protocol", {}).get("sha256")
         == PROPOSAL[1][1]
         and proposal.get("owners", {}).get("contract", {}).get("sha256")
         == PROPOSAL[2][1],
         "retain the unopened 14,155,776-case holdout as a proposal only")
    need(type(p0) is dict and p0.get("status") == "PASS"
         and p0.get("original_case_execution_denominator") == CASE_COUNT
         and p0.get("original_suite_count") == WORKER_COUNT
         and p0.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
         and p0.get("supplemental_case_count_per_reference") == SUPPLEMENTAL_COUNT
         and p0.get("supplemental_added_to_original_denominator") is False
         and type(effects) is dict and effects.get("actual_candidate_workers") == 0
         and effects.get("actual_compiler_process_count") == 0
         and effects.get("actual_root_descriptor_opens") == 0,
         "retain the unchanged frozen original CPython compatibility reference")
    return {"phase_count": len(phases), "native_artifact_count": len(distinct),
            "feature": feature, "proposal": proposal, "phase1": p0}


def frozen_provenance(base: types.ModuleType, guard: types.ModuleType
                      ) -> tuple[dict, dict, dict, dict]:
    for owner in V21:
        read_owner(owner)
    freeze = document(base, guard, read_owner(V21[2]), "actual V21 source freeze")
    build = document(base, guard, read_owner(V21_PUBLICATION),
                     "actual captured V21 small publication receipt")
    root = document(base, guard, read_owner(V21_ROOT),
                    "actual captured V21 small root-provenance receipt")
    proof = validate_v21_documents(build, root, freeze)
    capture = read_owner(CAPTURE_OWNER)
    need(len(capture) == CAPTURE_BYTES
         and capture.count(b'PyImport_ImportModule("inspect")') == 1
         and capture.count(b"rust_append_batched_findall") >= 2,
         "authenticate the unchanged owned captured bridge and real signature")
    for owner in PROPOSAL:
        read_owner(owner)
    runtime()
    return build, root, freeze, proof


class StrictSourceWall:
    """Deny real matching, mutations, private evidence, and process effects."""

    def __init__(self, allowed: set[str]) -> None:
        self.allowed = frozenset(allowed)
        self.blocked: dict[str, int] = {}

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise CampaignError("V17 source-only wall rejected " + category)

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else 0
            if type(path) is not str:
                self.deny("foreign-file-descriptor")
            if (type(mode) is str and any(letter in mode for letter in "wax+")):
                self.deny("source-write")
            if type(flags) is int and flags & (
                getattr(os, "O_WRONLY", 0) | getattr(os, "O_RDWR", 0)
                | getattr(os, "O_CREAT", 0) | getattr(os, "O_TRUNC", 0)
                | getattr(os, "O_APPEND", 0)
            ):
                self.deny("source-write")
            absolute = path if path.startswith("/") else ROOT + "/" + path
            if absolute not in self.allowed:
                self.deny("archive-root-holdout-or-unapproved-owner")
        elif event == "import":
            name = args[0] if args else None
            if type(name) is not str:
                self.deny("invalid-import")
            if (name in ("re", "_sre", "regex", "ctypes", "inspect", "tokenize")
                    or name.startswith(("re.", "regex.", "ctypes.",
                                        "candidates.", "socket"))
                    or name == "candidates"):
                self.deny("matcher-native-inspect-or-network-import")
        elif (event.startswith(("subprocess.", "os.exec", "os.spawn",
                                "socket.", "ctypes.", "tempfile."))
              or event in ("os.fork", "os.posix_spawn", "os.posix_spawnp",
                           "os.system", "os.mkdir", "os.remove", "os.rename",
                           "os.replace", "os.rmdir", "os.unlink", "os.chmod",
                           "os.chown", "os.putenv", "os.unsetenv",
                           "_interpreters.create", "_interpreters.exec")):
            self.deny("process-network-mutation-native-or-child")

    def install(self) -> None:
        sys.addaudithook(self.audit)


def migrate_assignments(raw: bytes, path: str,
                        expected: dict[str, object],
                        replacements: dict[str, object],
                        *, route_constants: bool = False) -> ast.Module:
    tree = ast.parse(raw, filename=path)
    need(type(tree) is ast.Module and set(expected) == set(replacements),
         "reject an incomplete V17 in-memory migration")
    counts = {name: 0 for name in expected}
    for statement in tree.body:
        if not (isinstance(statement, ast.Assign)
                and len(statement.targets) == 1
                and isinstance(statement.targets[0], ast.Name)):
            continue
        key = statement.targets[0].id
        if key not in expected:
            continue
        try:
            actual = ast.literal_eval(statement.value)
        except (ValueError, SyntaxError, TypeError) as error:
            raise CampaignError("reject a dynamic original constant: " + key) from error
        need(actual == expected[key] and counts[key] == 0,
             "reject a stale, repeated, or altered frozen constant: " + key)
        statement.value = ast.parse(repr(replacements[key]), mode="eval").body
        counts[key] += 1
    need(all(count == 1 for count in counts.values()),
         "reject a missing exact first-party V17 migration site")
    if route_constants:
        targets = [node for node in tree.body
                   if isinstance(node, ast.FunctionDef)
                   and node.name == "bind_v16_legacy"]
        need(len(targets) == 1,
             "authenticate exactly one complete V16 historical dispatcher")

        class UpdateVersion(ast.NodeTransformer):
            def __init__(self) -> None:
                self.counts = {"route": 0, "lower": 0, "upper": 0}

            def visit_Constant(self, node: ast.Constant) -> ast.AST:
                replacement = {
                    "phase2-v19-rust-buffer-shape-root-provenance-original-p0":
                        BUILD_LABEL + "-original-p0",
                    "v19": "v21",
                    "V19": "V21",
                }
                if type(node.value) is str and node.value in replacement:
                    key = ("route" if node.value.startswith("phase2-")
                           else "lower" if node.value == "v19" else "upper")
                    self.counts[key] += 1
                    return ast.copy_location(
                        ast.Constant(value=replacement[node.value]), node,
                    )
                return node

        update = UpdateVersion()
        update.visit(targets[0])
        need(update.counts == {"route": 1, "lower": 1, "upper": 1},
             "reject a missing or extra V21 historical-dispatch migration")
    return ast.fix_missing_locations(tree)


def make_v21_base(parent: types.ModuleType, original: types.ModuleType,
                  build: dict, root: dict, freeze: dict) -> types.ModuleType:
    owner = parent.V12[0]
    raw = read_owner(owner)
    expected = {
        "BUILD_LABEL": original.BUILD_LABEL,
        "BUILD": original.BUILD,
        "BUILD_RECEIPT": original.BUILD_RECEIPT,
        "ROOT_RECEIPT": original.ROOT_RECEIPT,
        "ENGINE_SHA": original.ENGINE_SHA,
        "BRIDGE_SHA": original.BRIDGE_SHA,
        "ENGINE_BYTES": original.ENGINE_BYTES,
        "BRIDGE_BYTES": original.BRIDGE_BYTES,
        "ROOT_DEVICE": original.ROOT_DEVICE,
        "ROOT_INODE": original.ROOT_INODE,
        "ROOT_PATH": original.ROOT_PATH,
        "BUILD_ARCHIVE_SHA": original.BUILD_ARCHIVE_SHA,
        "BUILD_ARCHIVE_BYTES": original.BUILD_ARCHIVE_BYTES,
        "BUILD_ARCHIVE_INODE": original.BUILD_ARCHIVE_INODE,
        "BUILD_PLAIN_SHA": original.BUILD_PLAIN_SHA,
        "BUILD_PLAIN_BYTES": original.BUILD_PLAIN_BYTES,
    }
    replacements = {
        "BUILD_LABEL": BUILD_LABEL,
        "BUILD": V21,
        "BUILD_RECEIPT": V21_PUBLICATION,
        "ROOT_RECEIPT": V21_ROOT,
        "ENGINE_SHA": ENGINE_SHA,
        "BRIDGE_SHA": BRIDGE_SHA,
        "ENGINE_BYTES": ENGINE_BYTES,
        "BRIDGE_BYTES": BRIDGE_BYTES,
        "ROOT_DEVICE": ROOT_DEVICE,
        "ROOT_INODE": ROOT_INODE,
        "ROOT_PATH": ROOT_PATH,
        "BUILD_ARCHIVE_SHA": ARCHIVE_SHA,
        "BUILD_ARCHIVE_BYTES": ARCHIVE_BYTES,
        "BUILD_ARCHIVE_INODE": ARCHIVE_INODE,
        "BUILD_PLAIN_SHA": PLAIN_SHA,
        "BUILD_PLAIN_BYTES": PLAIN_BYTES,
    }
    tree = migrate_assignments(raw, owner[0], expected, replacements)
    module = types.ModuleType("_rebar_v17_authenticated_v21_original_base")
    module.__file__ = ROOT + "/" + owner[0]
    exec(compile(tree, module.__file__, "exec", dont_inherit=True),
         module.__dict__)

    def authenticate(actual_guard: types.ModuleType) -> tuple[dict, dict]:
        need(actual_guard is not None and callable(actual_guard.canonical),
             "require the authentic unchanged V2 guard for V21 root receipts")
        fresh_build = document(module, actual_guard, read_owner(V21_PUBLICATION),
                               "actual V21 campaign build receipt")
        fresh_root = document(module, actual_guard, read_owner(V21_ROOT),
                              "actual V21 campaign root receipt")
        validate_v21_documents(fresh_build, fresh_root, freeze)
        need(fresh_build == build and fresh_root == root,
             "reject swapped authenticated V21 native-build receipts")
        return fresh_build, fresh_root

    module.authenticate_root_receipts = authenticate
    need(module.BUILD == V21 and module.BUILD_RECEIPT == V21_PUBLICATION
         and module.ROOT_RECEIPT == V21_ROOT
         and module.BUILD_LABEL == BUILD_LABEL
         and module.ROOT_PATH == ROOT_PATH
         and module.ROOT_DEVICE == ROOT_DEVICE
         and module.ROOT_INODE == ROOT_INODE
         and module.BRIDGE_SHA == BRIDGE_SHA
         and module.BRIDGE_BYTES == BRIDGE_BYTES
         and module.ENGINE_SHA == ENGINE_SHA
         and module.ENGINE_BYTES == ENGINE_BYTES
         and module.CORRECTED_ADAPTER_SHA == ADAPTER_SHA
         and module.CORRECTED_ADAPTER_BYTES == ADAPTER_BYTES
         and tuple(module.P0) == tuple(original.P0)
         and tuple(module.PRODUCER) == tuple(original.PRODUCER)
         and tuple(module.GUARD) == tuple(original.GUARD)
         and tuple(module.ROLE_ORDER) == tuple(original.ROLE_ORDER)
         and callable(module.install_worker_guard)
         and callable(module.derive_v19_private_report),
         "reject stale V19 root, bridge, oracle, producer, guard, or recovery")
    return module


def make_runner(parent: types.ModuleType) -> types.ModuleType:
    raw = read_owner(V16[0])
    expected = {
        "SOURCE": parent.SOURCE,
        "PROTOCOL": parent.PROTOCOL,
        "CONTRACT": parent.CONTRACT,
        "SCHEMA": parent.SCHEMA,
        "LABEL": parent.LABEL,
        "RECOVERY_PREFIX": parent.RECOVERY_PREFIX,
    }
    replacements = {
        "SOURCE": SOURCE,
        "PROTOCOL": PROTOCOL,
        "CONTRACT": CONTRACT,
        "SCHEMA": SCHEMA,
        "LABEL": LABEL,
        "RECOVERY_PREFIX": RECOVERY_PREFIX,
    }
    tree = migrate_assignments(raw, V16[0][0], expected, replacements,
                               route_constants=True)
    module = types.ModuleType("_rebar_v17_authenticated_original_controller")
    module.__file__ = ROOT + "/" + V16[0][0]
    exec(compile(tree, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    module.RECOVERY_ROOT = RECOVERY_ROOT
    need(module.SOURCE == SOURCE and module.PROTOCOL == PROTOCOL
         and module.CONTRACT == CONTRACT and module.SCHEMA == SCHEMA
         and module.LABEL == LABEL and module.RECOVERY_PREFIX == RECOVERY_PREFIX
         and module.RECOVERY_ROOT == RECOVERY_ROOT
         and tuple(module.SUITES) == SUITES
         and module.WORKER_COUNT == WORKER_COUNT
         and module.CASE_COUNT == CASE_COUNT
         and callable(module.actual_namespace)
         and callable(module.bind_v16_legacy)
         and callable(module.source_hostile_controls),
         "retain the exact genuine original 13-suite V16 controller")
    inherited = module.actual_required_authority

    def required(base: types.ModuleType) -> dict[str, str]:
        values = dict(inherited(base))
        values.update({
            "combined_bridge_sha256": CAPTURE_SHA,
            "combined_bridge_bytes": str(CAPTURE_BYTES),
            "previous_campaign_source_sha256": V16[0][1],
            "previous_campaign_protocol_sha256": V16[1][1],
            "previous_campaign_contract_sha256": V16[2][1],
        })
        return values

    module.actual_required_authority = required
    return module


def zero_effects() -> dict:
    return {
        "actual_candidate_imports": 0,
        "actual_candidate_workers_started": 0,
        "actual_reference_workers_started": 0,
        "actual_compiler_processes_started": 0,
        "actual_native_libraries_loaded": 0,
        "actual_private_build_root_opens": 0,
        "actual_private_build_root_stats": 0,
        "actual_build_archive_opens": 0,
        "actual_build_archive_inflations": 0,
        "actual_hidden_cases_read": 0,
        "actual_clock_samples": 0,
        "timing_trials_run": 0,
        "supplemental_candidate_case_count": 0,
        "supplemental_candidate_status": "NOT RUN",
        "supplemental_cases_counted_in_original_denominator": False,
        "expanded_holdout_proposal_case_count": HOLDOUT_CASE_COUNT,
        "expanded_holdout_cases_generated": 0,
        "expanded_holdout_cases_opened": 0,
        "expanded_holdout_proposal_verifier_executed": False,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "confidence_intervals": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None,
                   *, rendering: bool = False) -> tuple[dict, dict]:
    runtime()
    read_owner(dynamic_owner(SOURCE, source_pin))
    read_owner(dynamic_owner(PROTOCOL, protocol_pin))
    if not rendering:
        need(contract_pin is not None,
             "require the exact final V17 canonical contract")
        read_owner(dynamic_owner(CONTRACT, contract_pin))
    parent, previous, original_base, guard = load_predecessor()
    build, root, freeze, proof = frozen_provenance(original_base, guard)
    base = make_v21_base(parent, original_base, build, root, freeze)
    runner = make_runner(parent)
    required = runner.actual_required_authority(base)
    need(required.get("label") == LABEL
         and required.get("activation_root") == RECOVERY_ROOT
         and required.get("build_private_root") == ROOT_PATH
         and required.get("build_private_root_device") == str(ROOT_DEVICE)
         and required.get("build_private_root_inode") == str(ROOT_INODE)
         and required.get("build_source_sha256") == V21[0][1]
         and required.get("build_protocol_sha256") == V21[1][1]
         and required.get("build_contract_sha256") == V21[2][1]
         and required.get("build_archive_sha256") == ARCHIVE_SHA
         and required.get("build_receipt_sha256") == V21_PUBLICATION[1]
         and required.get("root_receipt_sha256") == V21_ROOT[1]
         and required.get("native_engine_sha256") == ENGINE_SHA
         and required.get("native_engine_bytes") == str(ENGINE_BYTES)
         and required.get("native_bridge_sha256") == BRIDGE_SHA
         and required.get("native_bridge_bytes") == str(BRIDGE_BYTES)
         and required.get("combined_bridge_sha256") == CAPTURE_SHA
         and required.get("combined_bridge_bytes") == str(CAPTURE_BYTES)
         and required.get("previous_campaign_source_sha256") == V16[0][1]
         and required.get("previous_campaign_protocol_sha256") == V16[1][1]
         and required.get("previous_campaign_contract_sha256") == V16[2][1],
         "reject a partial or stale V21 original-campaign caller authority")
    result = dict(previous)
    for key in tuple(result):
        if key.startswith("actual_v19_"):
            result["historical_" + key] = result.pop(key)
    result.update({
        "schema": SCHEMA + "-frozen-context",
        "status": "PASS",
        "version": VERSION,
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "previous_v16_source_sha256": V16[0][1],
        "previous_v16_protocol_sha256": V16[1][1],
        "previous_v16_contract_sha256": V16[2][1],
        "phase1_v4_reference_readiness": "PASS",
        "phase2_candidate_qualification": "BLOCKED",
        "suite_count": WORKER_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "named_private_waivers": list(original_base.PRIVATE_WAIVERS),
        "supplemental_case_count": SUPPLEMENTAL_COUNT,
        "supplemental_case_status": "NOT RUN AGAINST THIS CANDIDATE",
        "suites": [{"id": name, "case_execution_count": count}
                   for name, count in SUITES],
        "actual_v21_build_source_sha256": V21[0][1],
        "actual_v21_build_protocol_sha256": V21[1][1],
        "actual_v21_build_contract_sha256": V21[2][1],
        "actual_v21_build_receipt_sha256": V21_PUBLICATION[1],
        "actual_v21_root_receipt_sha256": V21_ROOT[1],
        "actual_v21_build_label": BUILD_LABEL,
        "actual_v21_compiler_process_count": 28,
        "actual_v21_source_build_phase_count": proof["phase_count"],
        "actual_v21_native_artifact_count": proof["native_artifact_count"],
        "actual_v21_private_build_root_provenance":
            "AUTHENTICATED RECEIPT ONLY; NOT OPENED",
        "actual_v21_private_build_root": ROOT_PATH,
        "actual_v21_private_build_root_device": ROOT_DEVICE,
        "actual_v21_private_build_root_inode": ROOT_INODE,
        "actual_v21_native_engine_sha256": ENGINE_SHA,
        "actual_v21_native_engine_bytes": ENGINE_BYTES,
        "actual_v21_native_bridge_sha256": BRIDGE_SHA,
        "actual_v21_native_bridge_bytes": BRIDGE_BYTES,
        "actual_v21_capture_source_sha256": CAPTURE_SHA,
        "actual_v21_capture_source_bytes": CAPTURE_BYTES,
        "actual_v21_build_archive_metadata_sha256": ARCHIVE_SHA,
        "actual_v21_build_archive_metadata_bytes": ARCHIVE_BYTES,
        "corrected_rust_source_owner_count": len(CORRECTED_SOURCES),
        "corrected_rust_source_owners": [
            {"path": path, "sha256": fingerprint, "bytes": count}
            for path, fingerprint, count in CORRECTED_SOURCES
        ],
        "runtime_guard_source_sha256": original_base.GUARD[0][1],
        "runtime_guard_protocol_sha256": original_base.GUARD[1][1],
        "runtime_guard_contract_sha256": original_base.GUARD[2][1],
        "runtime_guard_installation":
            "UNCHANGED V2 AUDIT HOOK BEFORE CANDIDATE IMPORT",
        "bound_signature_inspect_policy":
            "ALLOW ONLY AFTER sys.modules['re'] IS THE ATTESTED RUST CANDIDATE",
        "bound_signature_source_modified": False,
        "external_regex_packages_allowed": False,
        "stdlib_regex_engine_allowed": False,
        "matching_fallback_allowed": False,
        "recovery_role_order": list(original_base.ROLE_ORDER),
        "recovery_restoration_order": list(reversed(original_base.ROLE_ORDER)),
        "public_recovery_root": RECOVERY_ROOT,
        "recovery_lock_filename": "recoverable-controller-v17.lock",
        "actual_campaign_locale": "C",
        "actual_campaign_locale_fixture": LOCALE_PATH,
        "actual_campaign_locale_fixture_inspected": False,
        "historical_rust_semantic_mismatch_count": 1440,
        "historical_rust_verified_passing_case_count": 14853,
        **zero_effects(),
    })
    need(sum(count for _, count in SUITES) == CASE_COUNT
         and len(SUITES) == WORKER_COUNT
         and len(set(name for name, _ in SUITES)) == WORKER_COUNT
         and len(result["named_private_waivers"]) == PRIVATE_WAIVER_COUNT
         and len(CORRECTED_SOURCES) == 9,
         "preserve the complete unchanged original denominator and Rust closure")
    if not rendering:
        assert contract_pin is not None
        observed = document(
            original_base, guard,
            read_owner(dynamic_owner(CONTRACT, contract_pin)),
            "complete canonical frozen V17 original-campaign contract",
        )
        need(observed == contract_document(result),
             "reject an incomplete, stale, or changed V17 machine contract")
    runtime()
    return result, {"parent": parent, "previous": previous,
                    "original_base": original_base, "base": base,
                    "guard": guard, "runner": runner,
                    "build": build, "root": root, "freeze": freeze,
                    "proof": proof, "required": required}


def contract_document(context: dict) -> dict:
    result = dict(context)
    result["schema"] = SCHEMA + "-recoverable-source-freeze"
    result["status"] = "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
    result.pop("contract_sha256", None)
    return result


def allowed_source_paths(parent: types.ModuleType) -> set[str]:
    rows = [*V16, *V21, V21_PUBLICATION, V21_ROOT,
            CAPTURE_OWNER, *PROPOSAL]
    rows.extend(parent.HISTORY[index][1:5]
                for index in range(len(parent.HISTORY)))
    return {ROOT + "/" + item[0] for item in rows} | {
        ROOT + "/" + SOURCE,
        ROOT + "/" + PROTOCOL,
        ROOT + "/" + CONTRACT,
    }


def rejected(call: object, label: str) -> str:
    need(callable(call), "require an executable negative control")
    try:
        call()
    except (CampaignError, ValueError, TypeError, SyntaxError,
            UnicodeError, OSError):
        return label
    raise CampaignError("accepted a hostile V17 control: " + label)


def copy_document(guard: types.ModuleType, base: types.ModuleType,
                  value: dict) -> dict:
    return document(base, guard, guard.canonical(value),
                    "source-only canonical synthetic control")


def hostile_controls(context: dict, state: dict,
                     wall: StrictSourceWall) -> list[str]:
    parent = state["parent"]
    guard = state["guard"]
    base = state["original_base"]
    controls = list(parent.source_hostile_controls(guard))
    for event, args, name in (
        ("import", ("re",), "stdlib-re"),
        ("import", ("_sre",), "stdlib-native-regex"),
        ("import", ("re._compiler",), "private-regex-compiler"),
        ("import", ("re._parser",), "private-regex-parser"),
        ("import", ("regex",), "external-regex"),
        ("import", ("ctypes",), "native-ctypes"),
        ("import", ("inspect",), "early-inspect"),
        ("import", ("tokenize",), "early-tokenize"),
        ("import", ("candidates.vm_candidate",), "cross-family-candidate"),
        ("import", ("candidates.rust_candidate",), "early-rust-candidate"),
        ("subprocess.Popen", ("forbidden",), "candidate-process"),
        ("socket.connect", ("forbidden",), "network"),
        ("ctypes.dlopen", ("forbidden",), "native-loader"),
        ("os.fork", (), "unscoped-fork"),
        ("_interpreters.create", (), "unscoped-child"),
        ("os.mkdir", (ROOT_PATH,), "private-root-creation"),
        ("open", (ROOT_PATH, "r", 0), "private-root-open"),
        ("open", (ROOT + "/" + state["build"]["archive_relative"], "r", 0),
         "compressed-archive-open"),
        ("open", (ROOT + "/" + SOURCE, "w", os.O_WRONLY), "source-write"),
        ("open", ("/tmp/hidden-holdout", "r", 0), "hidden-holdout"),
    ):
        controls.append(rejected(
            lambda item=event, values=args: wall.audit(item, values),
            "wall-rejects-" + name,
        ))
    build_changes = (
        ("schema", "wrong", "schema"),
        ("status", "FAIL", "failed-build"),
        ("family", "zig", "foreign-family"),
        ("label", "phase2-v19-stale", "stale-label"),
        ("source_sha256", "0" * 64, "stale-build-source"),
        ("protocol_sha256", "0" * 64, "stale-build-protocol"),
        ("contract_sha256", "0" * 64, "stale-build-contract"),
        ("actual_compiler_process_count", 27, "incomplete-compilation"),
        ("combined_bridge_sha256", "0" * 64, "wrong-captured-source"),
        ("combined_bridge_bytes", CAPTURE_BYTES - 1, "wrong-captured-bytes"),
        ("corrected_public_adapter_sha256", "0" * 64, "foreign-adapter"),
        ("archive_sha256", "0" * 64, "foreign-archive-metadata"),
        ("candidate_workers_started", 1, "premature-candidate"),
        ("native_libraries_loaded", 1, "premature-native-load"),
        ("hidden_cases_read", 1, "opened-hidden-cases"),
    )
    for key, value, name in build_changes:
        bad = copy_document(guard, base, state["build"])
        bad[key] = value
        controls.append(rejected(
            lambda item=bad: validate_v21_documents(
                item, state["root"], state["freeze"],
            ), "reject-" + name,
        ))
    root_changes = (
        ("schema", "wrong", "root-schema"),
        ("status", "FAIL", "failed-root"),
        ("label", "phase2-v19-stale", "stale-root-label"),
        ("canonical_build_receipt_sha256", "0" * 64, "wrong-root-receipt"),
        ("canonical_build_archive_opened", True, "opened-build-archive"),
        ("cumulative_captured_bridge_sha256", "0" * 64,
         "wrong-root-captured-source"),
        ("actual_compiler_process_count", 27, "incomplete-root-compilation"),
        ("actual_source_phase_count", 1, "missing-build-phase"),
        ("native_libraries_loaded", 1, "root-native-load"),
        ("hidden_cases_read", 1, "root-hidden-cases"),
        ("clock_samples", 1, "root-clock"),
        ("expanded_holdout_cases_opened", 1, "opened-expanded-holdout"),
    )
    for key, value, name in root_changes:
        bad = copy_document(guard, base, state["root"])
        bad[key] = value
        controls.append(rejected(
            lambda item=bad: validate_v21_documents(
                state["build"], item, state["freeze"],
            ), "reject-" + name,
        ))
    for phase_index in range(2):
        for artifact_index in range(2):
            for key, value in (("sha256", "0" * 64),
                               ("bytes", 1), ("inode", 1),
                               ("native_loaded", True)):
                bad = copy_document(guard, base, state["root"])
                bad["root"]["phases"][phase_index]["native_outputs"][
                    artifact_index
                ][key] = value
                controls.append(rejected(
                    lambda item=bad: validate_v21_documents(
                        state["build"], item, state["freeze"],
                    ), "reject-phase-" + str(phase_index)
                    + "-artifact-" + str(artifact_index) + "-" + key,
                ))
    for name in ("_sre", "regex", "re._compiler", "re._parser",
                 "candidates.vm_candidate", "candidates.zig_candidate"):
        policy = guard.RuntimePolicy()
        try:
            policy.check_import(name)
        except guard.GuardError:
            controls.append("unchanged-guard-rejects-" + name)
        else:
            raise CampaignError("weakened strict original guard: " + name)
    controls.extend(publication_hostile_controls(state))
    need(sum(count for _, count in SUITES) == CASE_COUNT
         and len(controls) >= 100
         and "re" not in sys.modules and "_sre" not in sys.modules
         and "inspect" not in sys.modules and "tokenize" not in sys.modules
         and "ctypes" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "reject incomplete hostile controls or actual source-only matching")
    return controls


def parse_options(arguments: list[str]) -> dict:
    modes = ("--self-test", "--verify-frozen-context", "--render-contract",
             "--run", "--worker", "--recover")
    found = [part for part in arguments if part in modes]
    need(len(found) == 1, "select exactly one V17 source or actual operation")
    output: dict[str, object] = {"mode": found[0]}
    position = 0
    while position < len(arguments):
        flag = arguments[position]
        if flag in modes:
            position += 1
            continue
        need(type(flag) is str and flag.startswith("--")
             and position + 1 < len(arguments),
             "reject missing or positional V17 caller authority")
        key = flag[2:].replace("-", "_")
        need(key not in output,
             "reject repeated V17 caller authority: " + flag)
        output[key] = arguments[position + 1]
        position += 2
    exact_sha(output.get("source_sha256"), "V17 source")
    exact_sha(output.get("protocol_sha256"), "V17 protocol")
    if output["mode"] == "--render-contract":
        need("contract_sha256" not in output,
             "rendering cannot require its not-yet-generated contract")
    else:
        exact_sha(output.get("contract_sha256"), "V17 contract")
    if output["mode"] in ("--self-test", "--verify-frozen-context",
                          "--render-contract"):
        permitted = {"mode", "source_sha256", "protocol_sha256",
                     "contract_sha256"}
        need(set(output) <= permitted,
             "source-only verification must not authorize a candidate")
    return output


def bind_captured_controller(state: dict, context: dict,
                             bundle: dict | None,
                             counts: dict[str, int]) -> types.ModuleType:
    runner = state["runner"]
    base = state["base"]
    guard = state["guard"]
    legacy = runner.bind_v16_legacy(context, guard, base, bundle, counts)
    original_owners = tuple(legacy.SOURCE_OWNERS)
    need(len(original_owners) == 9
         and sum(1 for row in original_owners
                 if row[0] == "candidates/rust/py_bridge.c") == 1
         and sum(1 for row in original_owners
                 if row[0] == "candidates/rust_candidate.py") == 1,
         "preserve all nine authenticated original first-party Rust sources")
    legacy.COMBINED_BRIDGE_SHA256 = CAPTURE_SHA
    legacy.COMBINED_BRIDGE_BYTES = CAPTURE_BYTES
    legacy.CORRECTED_ADAPTER_SHA256 = ADAPTER_SHA
    legacy.CORRECTED_ADAPTER_BYTES = ADAPTER_BYTES
    legacy.SOURCE_OWNERS = tuple(
        (path, CAPTURE_SHA, CAPTURE_BYTES)
        if path == "candidates/rust/py_bridge.c"
        else (path, ADAPTER_SHA, ADAPTER_BYTES)
        if path == "candidates/rust_candidate.py"
        else (path, fingerprint, count)
        for path, fingerprint, count in original_owners
    )
    need(tuple(legacy.corrected_source_tuples()) == CORRECTED_SOURCES,
         "reject stale V19 bridge source or incomplete V21 nine-owner closure")
    previous_loader = legacy.load_frozen_module

    def captured_loader(owner: object, name: str) -> types.ModuleType:
        module = previous_loader(owner, name)
        if (type(module) is types.ModuleType
                and getattr(module, "SCHEMA", None)
                == "rebar-owned-repaired-rust-original-campaign-v7"):
            originals = tuple(module.ORIGINAL_SOURCE_OWNERS)
            need(len(originals) == len(CORRECTED_SOURCES)
                 and originals[0] == (
                     "candidates/rust_candidate.py",
                     "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
                     31151,
                 )
                 and originals[1] == (
                     "candidates/rust/py_bridge.c",
                     "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
                     175676,
                 )
                 and originals[2:] == CORRECTED_SOURCES[2:],
                 "preserve original immutable historical Rust sources")
            module.CORRECTED_SOURCE_OWNERS = CORRECTED_SOURCES
            module.BRIDGE_SOURCE_SHA256 = CAPTURE_SHA
            module.BRIDGE_SOURCE_BYTES = CAPTURE_BYTES
            module.CORRECTED_PUBLIC_SHA256 = ADAPTER_SHA
            module.CORRECTED_PUBLIC_BYTES = ADAPTER_BYTES
        return module

    legacy.load_frozen_module = captured_loader
    legacy.LOCK_NAME = "recoverable-controller-v17.lock"
    need(legacy.SCHEMA == SCHEMA and legacy.LABEL == LABEL
         and legacy.PUBLIC_RECOVERY_ROOT == RECOVERY_ROOT
         and legacy.BUILD_LABEL == BUILD_LABEL
         and legacy.VERIFIED_BUILD_PRIVATE_ROOT == ROOT_PATH
         and legacy.VERIFIED_BUILD_PRIVATE_ROOT_DEVICE == ROOT_DEVICE
         and legacy.VERIFIED_BUILD_PRIVATE_ROOT_INODE == ROOT_INODE
         and legacy.VERIFIED_NATIVE_ENGINE_SHA256 == ENGINE_SHA
         and legacy.VERIFIED_NATIVE_ENGINE_BYTES == ENGINE_BYTES
         and legacy.VERIFIED_NATIVE_BRIDGE_SHA256 == BRIDGE_SHA
         and legacy.VERIFIED_NATIVE_BRIDGE_BYTES == BRIDGE_BYTES
         and legacy.BUILD[0].sha256 == V21[0][1]
         and legacy.BUILD_RECEIPT.sha256 == V21_PUBLICATION[1]
         and legacy.BUILD_ARCHIVE.sha256 == ARCHIVE_SHA
         and tuple(legacy.ROLE_ORDER) == tuple(base.ROLE_ORDER)
         and tuple(legacy.RESTORATION_ORDER)
         == tuple(reversed(base.ROLE_ORDER))
         and tuple(legacy.SUITES) == SUITES,
         "bind every genuine V21 artifact, journal, suite, and recovery role")
    if bundle is None:
        install_exhaustive_publication(legacy)
    return legacy


def install_exhaustive_publication(legacy: object) -> None:
    """Validate the genuine 13 rows before the real compact publisher runs."""
    original = getattr(legacy, "preserve_actual_campaign", None)
    canonical = getattr(legacy, "canonical", None)
    need(callable(original) and callable(canonical),
         "retain the authentic first-party durable original publisher")

    def retain(report: dict, helper: object, recovery: object,
               publication: object, ledger: dict) -> dict:
        need(type(report) is dict
             and report.get("suite_count") == WORKER_COUNT
             and report.get("case_execution_denominator") == CASE_COUNT
             and report.get("attempted_suite_count") == WORKER_COUNT
             and report.get("current_overview_version") == 86
             and report.get("all_four_original_targets_restored") is True
             and report.get("restoration_verified_before_publication") is True
             and report.get("actual_v21_build_receipt_sha256")
             == V21_PUBLICATION[1]
             and report.get("corrected_bridge_source_sha256") == CAPTURE_SHA
             and report.get("native_engine_sha256") == ENGINE_SHA
             and report.get("native_bridge_sha256") == BRIDGE_SHA,
             "reject stale V19 or incomplete V21 report before publication")
        rows = report.get("suite_results")
        need(type(rows) is list and len(rows) == WORKER_COUNT,
             "require all genuine original rows before durable publication")
        compact: list[dict] = []
        for index, (suite, count) in enumerate(SUITES):
            row = rows[index]
            need(type(row) is dict and row.get("suite") == suite
                 and row.get("case_execution_denominator") == count
                 and row.get("worker_attempted") is True
                 and row.get("failure_class") in (
                     "PASS", "SEMANTIC MISMATCH", "INFRASTRUCTURE FAILURE",
                 ),
                 "reject a missing or reordered genuine suite: " + suite)
            process = row.get("process")
            if process is None:
                process = {}
            need(type(process) is dict,
                 "retain the genuine bounded worker process: " + suite)
            compact.append({
                "suite": suite,
                "case_execution_denominator": count,
                "worker_attempted": True,
                "actual_worker_started": row.get("actual_worker_started"),
                "fully_observed": row.get("fully_observed"),
                "failure_class": row.get("failure_class"),
                "mismatch_count": row.get("mismatch_count"),
                "verified_passing_case_count":
                    row.get("verified_passing_case_count"),
                "pid": process.get("pid"),
                "returncode": process.get("returncode"),
                "complete_original_row_sha256":
                    hashlib.sha256(canonical(row)).hexdigest(),
            })
        if report.get("candidate_qualified") is True:
            need(report.get("started_suite_count") == WORKER_COUNT
                 and report.get("completed_suite_count") == WORKER_COUNT
                 and report.get("actual_candidate_workers") == WORKER_COUNT
                 and report.get("distinct_worker_process_id_count")
                 == WORKER_COUNT
                 and report.get("duplicate_worker_process_id_count") == 0
                 and report.get("missing_worker_process_id_count") == 0
                 and report.get("all_original_observation_vectors_complete")
                 is True
                 and report.get("verified_passing_case_count") == CASE_COUNT
                 and report.get("semantic_mismatch_count") == 0
                 and report.get("infrastructure_failure_count") == 0
                 and all(row["actual_worker_started"] is True
                         and row["fully_observed"] is True
                         and row["failure_class"] == "PASS"
                         and row["mismatch_count"] == 0
                         and row["verified_passing_case_count"]
                         == row["case_execution_denominator"]
                         and type(row["pid"]) is int and row["pid"] > 0
                         and row["returncode"] == 0
                         for row in compact)
                 and len({row["pid"] for row in compact}) == WORKER_COUNT,
                 "never publish a qualified partial or synthetic correctness run")
        else:
            need(report.get("candidate_qualified") is False,
                 "reject ambiguous candidate qualification before publication")
        previous_writer = getattr(recovery, "write_evidence_receipt", None)
        need(callable(previous_writer),
             "retain the authentic durable first-party receipt writer")

        def retained_receipt(name: str, receipt: dict) -> dict:
            need(type(receipt) is dict
                 and receipt.get("schema")
                 == SCHEMA + "-durable-publication-receipt"
                 and receipt.get("suite_count") == WORKER_COUNT
                 and receipt.get("case_execution_denominator") == CASE_COUNT
                 and receipt.get("actual_v21_build_receipt_sha256")
                 == V21_PUBLICATION[1]
                 and receipt.get("all_four_original_targets_restored") is True
                 and receipt.get("candidate_qualified")
                 is report["candidate_qualified"],
                 "never publish incomplete or substituted V21 suite evidence")
            receipt["suite_integrity"] = compact
            receipt["all_original_suite_rows_validated_before_publication"] = True
            return previous_writer(name, receipt)

        recovery.write_evidence_receipt = retained_receipt
        try:
            result = original(report, helper, recovery, publication, ledger)
        finally:
            recovery.write_evidence_receipt = previous_writer
        need(recovery.write_evidence_receipt is previous_writer,
             "restore the exact genuine first-party durable evidence writer")
        need(type(result) is dict
             and result.get("suite_count") == WORKER_COUNT
             and result.get("case_execution_denominator") == CASE_COUNT
             and result.get("all_four_original_targets_restored") is True
             and result.get("candidate_qualified")
             is report["candidate_qualified"]
             and result.get("actual_v21_build_receipt_sha256")
             == V21_PUBLICATION[1],
             "retain the authentic compact durable first-party result")
        result["suite_integrity"] = compact
        result["all_original_suite_rows_validated_before_publication"] = True
        return result

    legacy.preserve_actual_campaign = retain


def publication_hostile_controls(state: dict) -> list[str]:
    """Prove the real compact receipt callback with synthetic rows only."""
    guard = state["guard"]
    base = state["original_base"]
    published: list[dict] = []
    rows = [
        {
            "suite": suite,
            "case_execution_denominator": count,
            "worker_attempted": True,
            "actual_worker_started": True,
            "fully_observed": True,
            "failure_class": "PASS",
            "mismatch_count": 0,
            "verified_passing_case_count": count,
            "process": {"pid": 71000 + position, "returncode": 0},
        }
        for position, (suite, count) in enumerate(SUITES)
    ]
    report = {
        "suite_count": WORKER_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "attempted_suite_count": WORKER_COUNT,
        "started_suite_count": WORKER_COUNT,
        "completed_suite_count": WORKER_COUNT,
        "actual_candidate_workers": WORKER_COUNT,
        "distinct_worker_process_id_count": WORKER_COUNT,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "all_original_observation_vectors_complete": True,
        "verified_passing_case_count": CASE_COUNT,
        "semantic_mismatch_count": 0,
        "infrastructure_failure_count": 0,
        "candidate_qualified": True,
        "current_overview_version": 86,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "actual_v21_build_receipt_sha256": V21_PUBLICATION[1],
        "corrected_bridge_source_sha256": CAPTURE_SHA,
        "native_engine_sha256": ENGINE_SHA,
        "native_bridge_sha256": BRIDGE_SHA,
        "suite_results": rows,
    }

    def synthetic_writer(name: str, receipt: dict) -> dict:
        need(name == "V17-SYNTHETIC-ONLY-NO-FILE-WRITER"
             and type(receipt) is dict
             and receipt.get("all_original_suite_rows_validated_before_publication")
             is True,
             "reject an unvalidated synthetic receipt callback")
        integrity = receipt.get("suite_integrity")
        need(type(integrity) is list and len(integrity) == WORKER_COUNT
             and tuple((row.get("suite"), row.get("case_execution_denominator"))
                       for row in integrity) == SUITES
             and all(type(row.get("complete_original_row_sha256")) is str
                     and len(row["complete_original_row_sha256"]) == 64
                     for row in integrity),
             "drop a real original row from the synthetic durable receipt")
        published.append(copy_document(guard, base, receipt))
        return {"status": "PASS", "publication_status": "PASS"}

    recovery = types.SimpleNamespace(write_evidence_receipt=synthetic_writer)

    def authentic_publication(actual: dict, helper: object,
                              actual_recovery: object,
                              publication: object, ledger: dict) -> dict:
        receipt = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "suite_count": WORKER_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "actual_v21_build_receipt_sha256": V21_PUBLICATION[1],
            "all_four_original_targets_restored": True,
            "candidate_qualified": actual["candidate_qualified"],
        }
        actual_recovery.write_evidence_receipt(
            "V17-SYNTHETIC-ONLY-NO-FILE-WRITER", receipt,
        )
        return {
            "schema": SCHEMA + "-published-complete-original-campaign",
            "status": "PASS",
            "publication_status": "PASS",
            "suite_count": WORKER_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "current_overview_version": 86,
            "actual_candidate_workers": WORKER_COUNT,
            "infrastructure_failure_count": 0,
            "semantic_mismatch_count": 0,
            "candidate_qualified": True,
            "all_four_original_targets_restored": True,
            "actual_v21_build_receipt_sha256": V21_PUBLICATION[1],
        }

    fake = types.SimpleNamespace(
        canonical=guard.canonical,
        preserve_actual_campaign=authentic_publication,
    )
    install_exhaustive_publication(fake)
    result = fake.preserve_actual_campaign(
        copy_document(guard, base, report), None, recovery, None, {},
    )
    need(len(published) == 1
         and result.get("all_original_suite_rows_validated_before_publication")
         is True
         and result.get("suite_integrity") == published[0]["suite_integrity"]
         and recovery.write_evidence_receipt is synthetic_writer,
         "fail to preserve all original digests inside the actual receipt")
    validate_complete_result(result, state)
    controls = ["accept-all-13-synthetic-rows-in-real-compact-receipt-route"]
    changes = (
        ("remove-last-suite", lambda item: item["suite_results"].pop()),
        ("reorder-first-suite",
         lambda item: item["suite_results"].reverse()),
        ("alter-first-denominator",
         lambda item: item["suite_results"][0].update(
             {"case_execution_denominator": 150},
         )),
        ("incomplete-qualified-row",
         lambda item: item["suite_results"][0].update(
             {"fully_observed": False},
         )),
        ("missing-qualified-pid",
         lambda item: item["suite_results"][0]["process"].update(
             {"pid": None},
         )),
        ("failed-qualified-process",
         lambda item: item["suite_results"][0]["process"].update(
             {"returncode": 1},
         )),
        ("duplicate-qualified-pid",
         lambda item: item["suite_results"][1]["process"].update(
             {"pid": item["suite_results"][0]["process"]["pid"]},
         )),
        ("missing-observed-case",
         lambda item: item["suite_results"][0].update(
             {"verified_passing_case_count": 150},
         )),
        ("wrong-captured-source",
         lambda item: item.update({"corrected_bridge_source_sha256": "0" * 64})),
        ("stale-native-bridge",
         lambda item: item.update({"native_bridge_sha256": "0" * 64})),
        ("stale-v19-publication",
         lambda item: item.update(
             {"actual_v21_build_receipt_sha256": "0" * 64},
         )),
        ("unrestored-original-inodes",
         lambda item: item.update({"all_four_original_targets_restored": False})),
        ("missing-prepublication-restoration",
         lambda item: item.update(
             {"restoration_verified_before_publication": False},
         )),
        ("missing-worker",
         lambda item: item.update({"actual_candidate_workers": 12})),
        ("partial-denominator",
         lambda item: item.update({"verified_passing_case_count": CASE_COUNT - 1})),
        ("unmeasured-mismatch",
         lambda item: item.update({"semantic_mismatch_count": "NOT MEASURED"})),
        ("infrastructure-qualified",
         lambda item: item.update({"infrastructure_failure_count": 1})),
    )
    for label, alter in changes:
        candidate = copy_document(guard, base, report)
        alter(candidate)
        before = len(published)
        controls.append(rejected(
            lambda value=candidate: fake.preserve_actual_campaign(
                value, None, recovery, None, {},
            ), "receipt-rejects-" + label,
        ))
        need(len(published) == before
             and recovery.write_evidence_receipt is synthetic_writer,
             "publish a hostile partial report or leak its receipt callback")
    return controls


def require_actual_locale() -> None:
    need(os.environ.get("LC_ALL") == "C"
         and os.environ.get("LOCPATH") == LOCALE_PATH
         and os.environ.get("PATH") == "/usr/bin:/bin",
         "require the exact previously prepared C-locale fixture and clean PATH")


def validate_complete_result(result: dict, state: dict) -> dict:
    need(type(result) is dict and result.get("suite_count") == WORKER_COUNT
         and result.get("case_execution_denominator") == CASE_COUNT
         and result.get("current_overview_version") == 86
         and result.get("all_four_original_targets_restored") is True,
         "reject a partial original campaign or failed four-inode restoration")
    evidence = result.get("actual_v21_build_receipt_sha256")
    if evidence is None:
        evidence = result.get("actual_v19_build_receipt_sha256")
    need(evidence == V21_PUBLICATION[1],
         "reject any actual correctness result for the stale V19 engine")
    rows = result.get("suite_integrity")
    if rows is None:
        rows = result.get("suite_results")
    if rows is None:
        rows = result.get("worker_results")
    need(type(rows) is list and len(rows) == WORKER_COUNT,
         "require all 13 real original suite rows even on failure")
    for index, (suite, count) in enumerate(SUITES):
        row = rows[index]
        need(type(row) is dict and row.get("suite") == suite
             and row.get("case_execution_denominator") == count,
             "reject missing, repeated, reordered, or partial suite " + suite)
    workers = result.get("actual_candidate_workers")
    infrastructure = result.get("infrastructure_failure_count")
    mismatches = result.get("semantic_mismatch_count")
    if result.get("candidate_qualified") is True:
        need(workers == WORKER_COUNT and infrastructure == 0
             and type(mismatches) is int and mismatches == 0
             and all(row.get("fully_observed") is True
                     and row.get("actual_worker_started") is True
                     and row.get("mismatch_count") == 0
                     and row.get("verified_passing_case_count") == count
                     for row, (_, count) in zip(rows, SUITES)),
             "never qualify missing, partial, failed, or guessed original cases")
        need(sum(row["verified_passing_case_count"] for row in rows)
             == CASE_COUNT,
             "require all 31,237 independently verified candidate observations")
    else:
        need(result.get("candidate_qualified") is False,
             "never fabricate original candidate qualification")
    result["actual_v21_build_receipt_sha256"] = V21_PUBLICATION[1]
    result["actual_v21_root_receipt_sha256"] = V21_ROOT[1]
    result["actual_v21_capture_source_sha256"] = CAPTURE_SHA
    result["actual_v21_native_bridge_sha256"] = BRIDGE_SHA
    result["supplemental_candidate_status"] = "NOT RUN"
    result["supplemental_cases_counted_in_original_denominator"] = False
    result["expanded_holdout_proposal_case_count"] = HOLDOUT_CASE_COUNT
    result["expanded_holdout_cases_opened"] = 0
    return result


def actual_operation(options: dict, context: dict, state: dict) -> dict:
    require_actual_locale()
    runner = state["runner"]
    base = state["base"]
    guard = state["guard"]
    namespace = runner.actual_namespace(options, base)
    counts = {"v11": 0, "v7": 0, "v2": 0, "v4": 0}
    bundle = (base.install_worker_guard(guard)
              if options["mode"] == "--worker" else None)
    if bundle is not None:
        need(bundle["policy"].installed
             and sys.modules.get("re") is bundle["candidate"]
             and "_sre" not in sys.modules and "ctypes" not in sys.modules
             and bundle["engine"]["sha256"] == ENGINE_SHA
             and bundle["bridge"]["sha256"] == BRIDGE_SHA
             and bundle["engine"]["mode"] == 0o600
             and bundle["bridge"]["mode"] == 0o600,
             "install the authentic V2 guard and bind Rust before inspect")
    legacy = bind_captured_controller(state, context, bundle, counts)
    if options["mode"] == "--worker":
        result = legacy.run_original_worker(namespace)
        expected_v4 = 0 if namespace.suite == "original_bounded_v5" else 1
        need(type(result) is dict
             and result.get("schema") == legacy.WORKER_SCHEMA
             and result.get("suite") == namespace.suite
             and result.get("case_execution_denominator")
             == dict(SUITES)[namespace.suite]
             and result.get("actual_candidate_workers") == 1
             and counts == {"v11": 1, "v7": 1,
                            "v2": 1, "v4": expected_v4}
             and "_sre" not in sys.modules and "ctypes" not in sys.modules,
             "retain the complete genuine guarded first-party original worker")
        assert bundle is not None
        bundle["policy"].check_modules()
        result["runtime_guard_installed_before_candidate_import"] = True
        result["runtime_guard_source_sha256"] = base.GUARD[0][1]
        result["historical_ctypes_module_imported"] = False
        result["historical_ctypes_guarded_transform_counts"] = dict(counts)
        return result
    if options["mode"] == "--recover":
        result = legacy.recover_originals(namespace)
        need(type(result) is dict and result.get("status") == "PASS"
             and result.get("activation_root") == RECOVERY_ROOT
             and result.get("candidate_workers_started") == 0,
             "restore only the exact authenticated original four owner inodes")
        return result
    need(options["mode"] == "--run",
         "reject an invented candidate execution operation")
    ledger = legacy.new_actual_ledger(namespace)
    return validate_complete_result(legacy.run_campaign(namespace, ledger), state)


def help_text() -> str:
    return (
        "Frozen first-party Rust original correctness campaign V17\n"
        "Source-only: --render-contract | --self-test | "
        "--verify-frozen-context\n"
        "Actual, separately authorized: --run | --worker | --recover\n"
        "Always pin --source-sha256 and --protocol-sha256; all but "
        "--render-contract also require --contract-sha256.\n"
        "Actual operations additionally require every original V21, "
        "P0, strict-guard, recovery, and captured-source authority.\n"
        "No candidate is activated by --help or a source-only mode.\n"
    )


def main(arguments: list[str] | None = None) -> int:
    values = list(sys.argv[1:] if arguments is None else arguments)
    if values == ["--help"]:
        sys.stdout.write(help_text())
        return 0
    guard = None
    try:
        options = parse_options(values)
        mode = options["mode"]
        context, state = verify_context(
            options["source_sha256"], options["protocol_sha256"],
            options.get("contract_sha256"),
            rendering=mode == "--render-contract",
        )
        guard = state["guard"]
        if mode == "--render-contract":
            result = contract_document(context)
        elif mode in ("--verify-frozen-context", "--self-test"):
            wall = StrictSourceWall(allowed_source_paths(state["parent"]))
            wall.install()
            if mode == "--self-test":
                result = dict(context)
                result["schema"] = SCHEMA + "-source-self-test"
                checks = hostile_controls(context, state, wall)
                result["hostile_controls"] = checks
                result["hostile_control_count"] = len(checks)
                result["physically_blocked_effects"] = dict(wall.blocked)
            else:
                result = context
            runtime()
        else:
            result = actual_operation(options, context, state)
        payload = guard.canonical(result)
        need(type(payload) is bytes and 0 < len(payload) <= 1024 * 1024,
             "bound complete canonical V17 public source or worker result")
        sys.stdout.buffer.write(payload)
        sys.stdout.buffer.flush()
        return 0 if result.get("status") in (
            "PASS", "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        ) else 1
    except Exception as error:
        if guard is not None:
            try:
                payload = guard.canonical({
                    "schema": SCHEMA + "-entry-failure",
                    "status": "FAIL",
                    "version": VERSION,
                    "error_type": type(error).__name__,
                    "error_message": str(error)[:8192],
                    **zero_effects(),
                })
                sys.stdout.buffer.write(payload)
                sys.stdout.buffer.flush()
            except (OSError, TypeError, ValueError):
                pass
        else:
            sys.stderr.write("V17 campaign rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
