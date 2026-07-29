#!/usr/bin/env python3
"""Freeze the reproducible cumulative first-party Rust captured-findall build."""

from __future__ import annotations

import sys

if "re" in sys.modules or "_sre" in sys.modules:
    raise SystemExit("a first-party Rust source freeze cannot import a matcher")

import builtins
import hashlib
import os
import stat


ROOT = "/home/dev-user/src/rebar"
SCHEMA = "rebar-phase2-owned-rust-captured-findall-source-build-v21"
VERSION = 21
FAMILY = "rust"
SOURCE_PATH = "tools/reproduce_owned_rust_captured_findall_source_build_v21.py"
PROTOCOL_PATH = "oracle/phase2/RUST-CAPTURED-FINDALL-SOURCE-BUILD-V21.md"
CONTRACT_PATH = "oracle/phase2/rust-captured-findall-source-build-v21.json"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
DEVICE = 2064
MAX_OWNER_BYTES = 4 * 1024 * 1024
GRAPH_VERSION = 86
EVIDENCE_FLOOR = 277
HISTORY_FLOOR = 282
PROPOSED_FINAL_HOLDOUT_CASE_COUNT = 14_155_776
PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT = 4_194_304
ROOT_PREFIX = "rebar-phase2-native-build-v9-rust-"
BUILD_LABEL = "phase2-v21-rust-captured-findall-root-provenance"
EVIDENCE_PATH = "oracle/phase2/evidence"
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)
V20 = {
    "source": (
        "v20_literal_findall_build_source",
        "tools/reproduce_owned_rust_literal_findall_source_build_v20.py",
        "e1c30d8713d1acafdffba28123966dc9814ea765b97cf3ad09da3ccf42c97b0e",
        122839, DEVICE, 429585,
    ),
    "protocol": (
        "v20_literal_findall_build_protocol",
        "oracle/phase2/RUST-LITERAL-FINDALL-SOURCE-BUILD-V20.md",
        "3393f73b11c6ad38c9f8dffc9f36e02ba11da64997ef351220e600bbae975f86",
        6221, DEVICE, 525265,
    ),
    "contract": (
        "v20_literal_findall_build_contract",
        "oracle/phase2/rust-literal-findall-source-build-v20.json",
        "5b584cc225226928e22169903d1a7f8712039b4ae3d34dd5a634f8174f4d8eb0",
        17479, DEVICE, 524764,
    ),
}
V20_BUILD_RECEIPT = (
    "actual_v20_literal_findall_build_receipt",
    "oracle/phase2/evidence/native-source-build-v20-rust-phase2-v20-rust-"
    "literal-findall-root-provenance-publication-receipt.json",
    "b9945838778c800f59a505021503655ea5bb4b3e11e1f0cf17f4be48cadde1b0",
    3498, DEVICE, 524791,
)
V20_ROOT_RECEIPT = (
    "actual_v20_literal_findall_root_receipt",
    "oracle/phase2/evidence/native-source-build-v20-rust-phase2-v20-rust-"
    "literal-findall-root-provenance-root-provenance-receipt.json",
    "bb5bd524a7bd8c4b3845c9654e81981cb6136c4fcff7a5e52ca375ce75e745aa",
    5685, DEVICE, 524792,
)
V20_ARCHIVE_METADATA = {
    "path": "oracle/phase2/evidence/native-source-build-v20-rust-phase2-v20-"
            "rust-literal-findall-root-provenance.json.gz",
    "sha256": "0edfe0559f45b00a295cce4094bc7ddc85acd87ef0f4205cdac8c8e3f970f883",
    "bytes": 108498,
    "device": DEVICE,
    "inode": 524790,
}
CAPTURE_VARIANT = (
    "cumulative_captured_findall_variant",
    "candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/py_bridge.c",
    "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a",
    179520, DEVICE, 524770,
)
CAPTURE_FEATURE = {
    "source": (
        "captured_findall_feature_source",
        "tools/verify_owned_rust_captured_findall_source_v1.py",
        "61c4d4beda9baf82150a8ae5e47f78eb1363595a583f0317626e93beb5373832",
        59368, DEVICE, 429082,
    ),
    "protocol": (
        "captured_findall_feature_protocol",
        "oracle/phase2/RUST-CAPTURED-FINDALL-ONE-PASS-V1.md",
        "ffcaeec11704a81a2fd5ca25d7fc746c8a66fab033bb1f108f0e6c19445079fe",
        5953, DEVICE, 524771,
    ),
    "contract": (
        "captured_findall_feature_contract",
        "oracle/phase2/rust-captured-findall-one-pass-v1.json",
        "ec396c100f606923f08d1969f283a9bb2bcf35dbf9edf9e9c5d2360057f9079b",
        5320, DEVICE, 524780,
    ),
}
_ROOT_CAPTURE: dict[str, object] | None = None


class GateError(Exception):
    """Reject substituted owners, invented effects, or false build provenance."""


def require(value: object, reason: str) -> None:
    if value is not True:
        raise GateError(reason)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete first-party source bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_hash(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value),
            "require an exact lowercase SHA-256: " + label)
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.realpath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == ROOT + "/" + SOURCE_PATH
            and os.path.realpath(__file__) == ROOT + "/" + SOURCE_PATH
            and "re" not in sys.modules and "_sre" not in sys.modules
            and "regex" not in sys.modules
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "require isolated CPython 3.14.6 without matcher or candidate imports")


def bootstrap_v20() -> dict[str, object]:
    owner = V20["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(ROOT + "/" + owner[1], flags)
    try:
        before = os.fstat(handle)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_uid == os.geteuid()
                and before.st_nlink == 1
                and (before.st_dev, before.st_ino, before.st_size)
                    == (owner[4], owner[5], owner[3]),
                "bootstrap only the genuinely frozen first-party V20 source")
        chunks: list[bytes] = []
        remaining = owner[3]
        while remaining:
            block = os.read(handle, min(remaining, 262144))
            require(type(block) is bytes and bool(block),
                    "reject truncated first-party V20 source")
            chunks.append(block)
            remaining -= len(block)
        require(os.read(handle, 1) == b"", "reject extra V20 source bytes")
        after = os.fstat(handle)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
                "reject a first-party V20 owner changed during bootstrap")
    finally:
        os.close(handle)
    raw = b"".join(chunks)
    require(digest(raw) == owner[2], "reject substituted V20 build source")
    namespace: dict[str, object] = {
        "__name__": "_rebar_exact_v21_first_party_v20_source",
        "__file__": ROOT + "/" + owner[1],
        "__package__": None,
    }
    exec(compile(raw, namespace["__file__"], "exec", dont_inherit=True), namespace)
    require(namespace.get("SCHEMA")
                == "rebar-phase2-owned-rust-literal-findall-source-build-v20"
            and namespace.get("VERSION") == 20
            and namespace.get("FAMILY") == FAMILY
            and namespace.get("PYTHON") == PYTHON
            and namespace.get("PYTHON_SHA256") == PYTHON_SHA256
            and namespace.get("GRAPH_VERSION") == GRAPH_VERSION
            and namespace.get("EVIDENCE_FLOOR") == EVIDENCE_FLOOR
            and namespace.get("HISTORY_FLOOR") == HISTORY_FLOOR
            and namespace.get("ROOT_PREFIX") == ROOT_PREFIX
            and tuple(namespace.get("PHASES", ())) == PHASES
            and tuple(namespace.get("PROCESS_NAMES", ())) == PROCESS_NAMES
            and namespace.get("PROPOSED_FINAL_HOLDOUT_CASE_COUNT")
                == PROPOSED_FINAL_HOLDOUT_CASE_COUNT
            and namespace.get("PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT")
                == PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT
            and namespace.get("SOURCE_PATH") == V20["source"][1]
            and namespace.get("PROTOCOL_PATH") == V20["protocol"][1]
            and namespace.get("CONTRACT_PATH") == V20["contract"][1]
            and "re" not in sys.modules and "_sre" not in sys.modules,
            "derive only the exact, independently frozen first-party V20 controller")
    return namespace


def load_base(v20: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    v19 = v20["bootstrap_v19"]()
    base = v20["load_base"](v19)
    require(type(v19) is dict and type(base) is dict
            and base.get("FAMILY") == FAMILY
            and base.get("PYTHON") == PYTHON
            and base.get("PYTHON_SHA256") == PYTHON_SHA256
            and base.get("V2_BRIDGE_SHA256")
                == "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740"
            and base.get("V2_BRIDGE_BYTES") == 179961
            and base.get("CORRECTED_ADAPTER_SHA256")
                == "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
            and base.get("CORRECTED_ADAPTER_BYTES") == 31934
            and tuple(base.get("RUST_SOURCE_NAMES", ()))
                == ("cargo_lock", "cargo_manifest", "original_bridge", "rust_engine",
                    "rust_newline", "rust_search", "rust_stack", "rust_unicode",
                    "original_adapter"),
            "retain exactly nine canonical zero-dependency first-party Rust owners")
    additions = {
        ROOT + "/" + SOURCE_PATH,
        ROOT + "/" + PROTOCOL_PATH,
        ROOT + "/" + CONTRACT_PATH,
        ROOT + "/" + CAPTURE_VARIANT[1],
        ROOT + "/" + V20_BUILD_RECEIPT[1],
        ROOT + "/" + V20_ROOT_RECEIPT[1],
    }
    additions.update(ROOT + "/" + row[1] for row in V20.values())
    additions.update(ROOT + "/" + row[1] for row in CAPTURE_FEATURE.values())
    base["_ALLOWLIST"] = frozenset(set(base["_ALLOWLIST"]) | additions)
    return v19, base


def canonical(base: dict[str, object], value: object) -> bytes:
    return (base["canonical"](value) + "\n").encode("ascii")


def document(base: dict[str, object], raw: bytes, label: str) -> dict[str, object]:
    value = base["StrictJSON"](raw).decode()
    require(type(value) is dict and canonical(base, value) == raw,
            "reject invalid, duplicate, or noncanonical public owner: " + label)
    return value


def row_document(row: tuple[object, ...]) -> dict[str, object]:
    return {"path": row[1], "sha256": row[2], "bytes": row[3],
            "device": row[4], "inode": row[5], "mode": "0600", "nlink": 1}


def public_document(row: tuple[object, ...]) -> dict[str, object]:
    return {"path": row[1], "sha256": row[2], "bytes": row[3]}


def row_group(rows: dict[str, tuple[object, ...]]) -> dict[str, dict[str, object]]:
    return {name: row_document(row) for name, row in sorted(rows.items())}


def boundary(v20: dict[str, object]) -> dict[str, object]:
    return {
        **v20["boundary"](),
        "captured_findall_practice_case_count": 48,
        "captured_findall_materialized_case_count": 44,
        "captured_findall_empty_case_count": 4,
        "captured_variant_practice_execution": "NOT RUN",
        "captured_variant_timing": "NOT MEASURED",
        "actual_previous_v20_compiler_process_count": 28,
        "actual_previous_v20_source_phase_count": 2,
        "previous_private_root_opened": False,
        "previous_archive_opened": False,
    }


def validate_actual_v20_receipts(
    v20: dict[str, object], build: dict[str, object], root: dict[str, object],
) -> dict[str, object]:
    archive = build.get("archive_publication")
    require(build.get("schema")
                == "rebar-phase2-owned-rust-literal-findall-source-build-v20-"
                   "durable-publication-receipt"
            and build.get("status") == "PASS"
            and build.get("build_status") == "PASS"
            and build.get("family") == FAMILY
            and build.get("label") == v20["BUILD_LABEL"]
            and build.get("source_sha256") == V20["source"][2]
            and build.get("protocol_sha256") == V20["protocol"][2]
            and build.get("contract_sha256") == V20["contract"][2]
            and build.get("current_graph_version") == GRAPH_VERSION
            and build.get("prepublication_evidence_owner_lower_bound")
                == EVIDENCE_FLOOR
            and build.get("prepublication_history_reference_lower_bound")
                == HISTORY_FLOOR
            and build.get("expected_actual_compiler_process_count") == 28
            and build.get("actual_compiler_process_count") == 28
            and build.get("combined_bridge_sha256") == v20["LITERAL_VARIANT"][2]
            and build.get("combined_bridge_bytes") == v20["LITERAL_VARIANT"][3]
            and build.get("combined_bridge_overlay_apply_count") == 2
            and build.get("corrected_public_adapter_sha256")
                == "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
            and build.get("corrected_public_adapter_bytes") == 31934
            and build.get("corrected_public_adapter_overlay_apply_count") == 2
            and build.get("archive_relative") == V20_ARCHIVE_METADATA["path"]
            and build.get("archive_sha256") == V20_ARCHIVE_METADATA["sha256"]
            and build.get("archive_bytes") == V20_ARCHIVE_METADATA["bytes"]
            and type(archive) is dict
            and archive.get("sha256") == V20_ARCHIVE_METADATA["sha256"]
            and archive.get("bytes") == V20_ARCHIVE_METADATA["bytes"]
            and archive.get("device") == V20_ARCHIVE_METADATA["device"]
            and archive.get("inode") == V20_ARCHIVE_METADATA["inode"]
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("same_inode_readback_verified") is True
            and build.get("candidate_correctness") == "NOT MEASURED"
            and build.get("candidate_matching") == "NOT RUN"
            and build.get("candidate_qualified") is False
            and build.get("candidate_workers_started") == 0
            and build.get("native_libraries_loaded") == 0
            and build.get("hidden_cases_read") == 0
            and build.get("clock_samples") == 0
            and build.get("timing_trials_run") == 0
            and build.get("performance") == "NOT MEASURED"
            and build.get("holdout") == "NOT OPENED",
            "authenticate actual 28-role V20 build using only its small public receipt")
    captured_root = root.get("root")
    require(root.get("schema")
                == "rebar-phase2-owned-rust-literal-findall-source-build-v20-"
                   "durable-root-provenance-receipt"
            and root.get("status") == "PASS"
            and root.get("family") == FAMILY
            and root.get("label") == v20["BUILD_LABEL"]
            and root.get("source_sha256") == V20["source"][2]
            and root.get("protocol_sha256") == V20["protocol"][2]
            and root.get("contract_sha256") == V20["contract"][2]
            and root.get("frozen_graph_version") == GRAPH_VERSION
            and root.get("frozen_graph_summary_sha256")
                == v20["GRAPH"]["summary"][2]
            and root.get("one_pass_literal_bridge_sha256")
                == v20["LITERAL_VARIANT"][2]
            and root.get("one_pass_literal_bridge_bytes")
                == v20["LITERAL_VARIANT"][3]
            and root.get("expanded_holdout_proposal_source_sha256")
                == v20["EXPANDED_HOLDOUT_PROPOSAL"]["source"][2]
            and root.get("expanded_holdout_proposal_protocol_sha256")
                == v20["EXPANDED_HOLDOUT_PROPOSAL"]["protocol"][2]
            and root.get("expanded_holdout_proposal_contract_sha256")
                == v20["EXPANDED_HOLDOUT_PROPOSAL"]["contract"][2]
            and root.get("expanded_holdout_proposal_case_count")
                == PROPOSED_FINAL_HOLDOUT_CASE_COUNT
            and root.get("previous_holdout_proposal_case_count")
                == PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT
            and root.get("expanded_holdout_proposal_status")
                == "PRE-PHASE-3 PROPOSAL"
            and root.get("canonical_build_status") == "PASS"
            and root.get("canonical_build_archive_relative")
                == V20_ARCHIVE_METADATA["path"]
            and root.get("canonical_build_archive_sha256")
                == V20_ARCHIVE_METADATA["sha256"]
            and root.get("canonical_build_archive_bytes")
                == V20_ARCHIVE_METADATA["bytes"]
            and root.get("canonical_build_archive_opened") is False
            and root.get("canonical_build_receipt_relative")
                == V20_BUILD_RECEIPT[1]
            and root.get("canonical_build_receipt_sha256")
                == V20_BUILD_RECEIPT[2]
            and root.get("canonical_build_receipt_bytes")
                == V20_BUILD_RECEIPT[3]
            and root.get("actual_compiler_process_count") == 28
            and root.get("expected_compiler_process_count") == 28
            and root.get("actual_source_phase_count") == 2
            and root.get("bridge_overlay_apply_count") == 2
            and root.get("adapter_overlay_apply_count") == 2
            and root.get("candidate_correctness") == "NOT MEASURED"
            and root.get("candidate_matching") == "NOT RUN"
            and root.get("candidate_qualified") is False
            and root.get("candidate_workers_started") == 0
            and root.get("native_libraries_loaded") == 0
            and root.get("tmp_directory_scanned") is False
            and root.get("historical_archives_opened") == 0
            and root.get("hidden_cases_read") == 0
            and root.get("clock_samples") == 0
            and root.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and root.get("performance") == "NOT MEASURED"
            and root.get("holdout") == "NOT OPENED"
            and type(captured_root) is dict
            and type(captured_root.get("path")) is str
            and captured_root["path"].startswith("/tmp/" + ROOT_PREFIX)
            and captured_root.get("prefix") == ROOT_PREFIX
            and captured_root.get("mode") == "0700"
            and captured_root.get("uid") == os.geteuid()
            and captured_root.get("phase_count") == 2
            and captured_root.get("directory_scanned") is False
            and captured_root.get("nofollow_directory_descriptor") is True
            and captured_root.get("descriptor_opened_during_live_verification") is True,
            "authenticate real V20 provenance without opening its archive or root")
    phases = captured_root.get("phases")
    require(type(phases) is list and len(phases) == 2,
            "require both genuinely attested historical V20 source phases")
    identities: set[tuple[int, int]] = set()
    hashes: dict[str, str] = {}
    for index, phase in enumerate(phases):
        require(type(phase) is dict and phase.get("name") == PHASES[index]
                and phase.get("absolute_path")
                    == captured_root["path"] + "/" + PHASES[index]
                and phase.get("mode") == "0700"
                and phase.get("uid") == os.geteuid(),
                "reject borrowed or omitted V20 provenance phases")
        outputs = phase.get("native_outputs")
        require(type(outputs) is list and len(outputs) == 2,
                "retain both historical first-party native output roles")
        for position, (role, name) in enumerate((
            ("engine", "_rust_engine.so"),
            ("bridge", "_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
        )):
            artifact = outputs[position]
            require(type(artifact) is dict
                    and artifact.get("role") == role
                    and artifact.get("file_name") == name
                    and artifact.get("absolute_path")
                        == phase["absolute_path"] + "/native/" + name
                    and type(artifact.get("sha256")) is str
                    and len(artifact["sha256"]) == 64
                    and type(artifact.get("bytes")) is int and artifact["bytes"] > 0
                    and type(artifact.get("device")) is int
                    and type(artifact.get("inode")) is int
                    and artifact.get("uid") == os.geteuid()
                    and artifact.get("nlink") == 1
                    and artifact.get("native_loaded") is False
                    and artifact.get("hash_provenance")
                        == "COMPLETE ORIGINAL FIRST-PARTY ELF VERIFICATION",
                    "preserve receipt-only historical native ownership")
            identity = (artifact["device"], artifact["inode"])
            require(identity not in identities,
                    "reject shared historical Rust engine or bridge ownership")
            identities.add(identity)
            if role in hashes:
                require(hashes[role] == artifact["sha256"],
                        "retain actual historical two-phase ELF byte identity")
            else:
                hashes[role] = artifact["sha256"]
    require(len(identities) == 4 and len(hashes) == 2,
            "require all four distinct receipt-attested V20 native outputs")
    return {
        "status": "PASS",
        "scope": "ACTUAL HISTORICAL V20 BUILD; NOT V21 COMPILATION",
        "build_receipt_sha256": V20_BUILD_RECEIPT[2],
        "root_receipt_sha256": V20_ROOT_RECEIPT[2],
        "actual_previous_build_status": "PASS",
        "actual_previous_root_provenance_status": "PASS",
        "actual_previous_compiler_process_count": 28,
        "actual_previous_phase_count": 2,
        "actual_previous_native_artifact_count": 4,
        "previous_archive_opened": False,
        "previous_private_root_opened": False,
        "previous_private_root_scanned": False,
        "new_capture_variant_built": False,
        "holdout": "NOT OPENED",
    }


def validate_capture_bytes(v20: dict[str, object], previous: bytes,
                           captured: bytes) -> dict[str, object]:
    require(type(previous) is bytes
            and len(previous) == v20["LITERAL_VARIANT"][3]
            and digest(previous) == v20["LITERAL_VARIANT"][2]
            and type(captured) is bytes
            and len(captured) == CAPTURE_VARIANT[3]
            and digest(captured) == CAPTURE_VARIANT[2],
            "authenticate both complete independently owned cumulative Rust bridges")
    marker = b"static int rust_append_batched_findall("
    suffix = b"\nstatic PyObject *rust_batched_findall("
    require(previous.count(marker) == 1 and captured.count(marker) == 1
            and previous.count(suffix) == 1 and captured.count(suffix) == 1,
            "require exactly one bounded first-party captured-findall helper")
    previous_prefix, previous_tail = previous.split(marker, 1)
    captured_prefix, captured_tail = captured.split(marker, 1)
    previous_body, previous_suffix = previous_tail.split(suffix, 1)
    captured_body, captured_suffix = captured_tail.split(suffix, 1)
    require(previous_prefix == captured_prefix
            and previous_suffix == captured_suffix
            and previous_body != captured_body
            and b"if (groups == 2)" not in previous_body
            and captured_body.count(b"if (groups == 2)") == 1
            and captured_body.count(b"PyObject *row = PyTuple_New(2);") == 1
            and b"rust_findall_item(subject, begins[1], ends[1])" in captured_body
            and b"rust_findall_item(subject, begins[2], ends[2])" in captured_body
            and b"PyTuple_SET_ITEM(row, 0, first);" in captured_body
            and b"PyTuple_SET_ITEM(row, 1, second);" in captured_body
            and captured_body.count(b"Py_DECREF(row);") >= 2
            and b"return rust_list_append_owned(result, row);" in captured_body
            and b"size_t first = groups == 0 ? 0 : 1;" in captured_body
            and b"size_t values = groups <= 1 ? 1 : groups;" in captured_body
            and b"for (size_t index = 0; index < values; index++)"
                in captured_body
            and b"static PyObject *rust_pattern_literal_findall_direct("
                in previous_suffix
            and b"static PyObject *rust_pattern_literal_findall_direct("
                in captured_suffix,
            "retain literal one-pass and alter only ordered two-capture owned tuples")
    return {
        "status": "PASS",
        "scope": "STATIC FIRST-PARTY CUMULATIVE SOURCE ONLY",
        "immediate_predecessor": public_document(v20["LITERAL_VARIANT"]),
        "captured_variant": row_document(CAPTURE_VARIANT),
        "changed_first_party_function": "rust_append_batched_findall",
        "changed_first_party_function_count": 1,
        "specialized_capture_count": 2,
        "unchanged_immediate_prefix_and_suffix": True,
        "literal_one_pass_preserved": True,
        "ordered_owned_capture_items": True,
        "owned_tuple_reference_cleanup": True,
        "general_capture_fallback_preserved": True,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
    }


def validate_capture_feature(
    v20: dict[str, object], contract: dict[str, object],
) -> dict[str, object]:
    variant = contract.get("candidate_variant")
    predecessor = contract.get("immediate_literal_predecessor")
    history = contract.get("historical_public_practice")
    proposal = contract.get("expanded_sealed_holdout_proposal")
    references = contract.get("frozen_python_reference")
    effects = contract.get("phase_boundary")
    future = contract.get("required_future_gates")
    require(contract.get("schema")
                == "rebar-phase2-owned-rust-captured-findall-one-pass-v1-source-freeze"
            and contract.get("version") == 1
            and contract.get("status")
                == "SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED"
            and contract.get("family") == FAMILY
            and contract.get("source") == public_document(CAPTURE_FEATURE["source"])
            and contract.get("protocol")
                == public_document(CAPTURE_FEATURE["protocol"])
            and type(variant) is dict
            and variant.get("path") == CAPTURE_VARIANT[1]
            and variant.get("sha256") == CAPTURE_VARIANT[2]
            and variant.get("bytes") == CAPTURE_VARIANT[3]
            and variant.get("changed_function") == "rust_append_batched_findall"
            and variant.get("changed_function_count") == 1
            and variant.get("specialized_capture_count") == 2
            and variant.get("inherits_literal_single_pass") is True
            and variant.get("all_other_immediate_predecessor_bytes_unchanged")
                is True
            and variant.get("complete_independently_owned_source") is True
            and variant.get("native_build") == "NOT RUN"
            and variant.get("matching") == "NOT RUN"
            and variant.get("qualified") is False,
            "authenticate independently frozen cumulative captured-findall source")
    require(type(predecessor) is dict
            and predecessor.get("path") == v20["LITERAL_VARIANT"][1]
            and predecessor.get("sha256") == v20["LITERAL_VARIANT"][2]
            and predecessor.get("bytes") == v20["LITERAL_VARIANT"][3]
            and predecessor.get("source_status")
                == "SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED"
            and predecessor.get("verifier")
                == public_document(v20["LITERAL_FEATURE"]["source"])
            and predecessor.get("protocol")
                == public_document(v20["LITERAL_FEATURE"]["protocol"])
            and predecessor.get("contract")
                == public_document(v20["LITERAL_FEATURE"]["contract"]),
            "preserve historical literal-feature source without erasing actual V20 receipts")
    require(type(history) is dict and history.get("case_count") == 864
            and history.get("findall_case_count") == 48
            and history.get("two_named_capture_case_count") == 48
            and history.get("materialized_capture_case_count") == 44
            and history.get("empty_capture_case_count") == 4
            and history.get("module_findall_case_count") == 24
            and history.get("pattern_findall_case_count") == 24
            and history.get("new_variant_exercised") is False
            and history.get("new_variant_timed") is False
            and history.get("benchmark_files_read") == 0
            and history.get("hidden_cases_read") == 0
            and history.get("effect_on_historical_pilot") == "NOT MEASURED",
            "retain 48 historical capture cases without opening or running practice")
    require(type(references) is dict and references.get("cpython") == "3.14.6"
            and references.get("original_cases") == 31237
            and references.get("original_groups") == 13
            and references.get("named_private_waivers") == 13
            and references.get("additional_differential_property_cases") == 8244
            and references.get("reference_status") == "PASS"
            and references.get("candidate_status") == "NOT RUN"
            and type(proposal) is dict
            and proposal.get("case_count") == PROPOSED_FINAL_HOLDOUT_CASE_COUNT
            and proposal.get("historical_previous_proposal_case_count")
                == PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT
            and proposal.get("proposal_status") == "PRE-PHASE-3 PROPOSAL"
            and proposal.get("final_protocol_status") == "NOT FROZEN"
            and proposal.get("generator_status") == "NOT FROZEN"
            and proposal.get("case_status") == "NOT GENERATED; NOT OPENED"
            and proposal.get("minimum_qualified_independent_family_count") == 3
            and proposal.get("qualified_independent_family_count") == 0
            and proposal.get("runtime_independence_status") == "NOT ESTABLISHED"
            and proposal.get("controller")
                == public_document(v20["EXPANDED_HOLDOUT_PROPOSAL"]["source"])
            and proposal.get("protocol")
                == public_document(v20["EXPANDED_HOLDOUT_PROPOSAL"]["protocol"])
            and proposal.get("contract")
                == public_document(v20["EXPANDED_HOLDOUT_PROPOSAL"]["contract"]),
            "preserve the actual expanded unopened proposal and reference denominators")
    require(type(effects) is dict
            and effects.get("archive_opens") == 0
            and effects.get("candidate_processes_started") == 0
            and effects.get("candidate_workers_started") == 0
            and effects.get("clock_samples") == 0
            and effects.get("compiler_processes_started") == 0
            and effects.get("correctness") == "NOT MEASURED"
            and effects.get("external_regex_dependencies") == 0
            and effects.get("hidden_cases_read") == 0
            and effects.get("historical_previous_holdout_proposal_case_count")
                == PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT
            and effects.get("holdout")
                == "NOT FROZEN; NOT GENERATED; NOT OPENED"
            and effects.get("holdout_case_count")
                == PROPOSED_FINAL_HOLDOUT_CASE_COUNT
            and effects.get("matching_operations") == 0
            and effects.get("native_libraries_loaded") == 0
            and effects.get("performance") == "NOT MEASURED"
            and effects.get("qualified_candidate_count") == 0
            and effects.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and effects.get("timing_trials_run") == 0
            and effects.get("winner_selected") is False
            and type(future) is dict
            and future.get("complete_original_correctness") == "NOT RUN"
            and future.get("complete_additional_correctness") == "NOT RUN"
            and future.get("fresh_native_build_and_provenance") == "NOT RUN"
            and future.get("public_api_and_buffer_correctness") == "NOT RUN"
            and future.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and future.get("separately_frozen_public_capture_practice")
                == "NOT FROZEN",
            "reject invented build, capture matching, timing, holdout, or qualification")
    return {
        "status": "PASS",
        "source_owner_count": 3,
        "source_sha256": CAPTURE_FEATURE["source"][2],
        "protocol_sha256": CAPTURE_FEATURE["protocol"][2],
        "contract_sha256": CAPTURE_FEATURE["contract"][2],
        "captured_variant_sha256": CAPTURE_VARIANT[2],
        "captured_variant_bytes": CAPTURE_VARIANT[3],
        "changed_function_count": 1,
        "specialized_capture_count": 2,
        "historical_practice_case_count": 864,
        "historical_findall_case_count": 48,
        "historical_materialized_capture_count": 44,
        "historical_empty_capture_count": 4,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def collect_context(
    v20: dict[str, object], v19: dict[str, object], base: dict[str, object],
    source_pin: str, protocol_pin: str, contract_pin: str | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    checked_hash(source_pin, "V21 captured Rust source")
    checked_hash(protocol_pin, "V21 captured Rust protocol")
    source_raw, source_info = base["read_self"](SOURCE_PATH, source_pin)
    protocol_raw, protocol_info = base["read_self"](PROTOCOL_PATH, protocol_pin)
    require(source_raw.endswith(b"\n") and not source_raw.endswith(b"\n\n")
            and protocol_raw.endswith(b"\n") and not protocol_raw.endswith(b"\n\n"),
            "require exactly one final V21 source and protocol newline")
    previous_context, previous_state = v20["collect_context"](
        v19, base, V20["source"][2], V20["protocol"][2], V20["contract"][2],
    )
    require(previous_context.get("status") == "PASS"
            and previous_context.get("version") == 20
            and previous_context.get("authenticated_current_graph_version")
                == GRAPH_VERSION
            and previous_context.get("first_party_rust_source_owner_count") == 9
            and previous_context.get("future_total_compiler_process_count") == 28
            and previous_context.get("expanded_holdout_proposal_case_count")
                == PROPOSED_FINAL_HOLDOUT_CASE_COUNT
            and previous_context.get("candidate_qualification") == "BLOCKED"
            and previous_context.get("latest_rust_completed_suite_count") == 8
            and previous_context.get("latest_rust_worker_failure_count") == 5,
            "preserve the exact independently published V20 source and V86 losses")
    build = document(base, base["read_exact"](V20_BUILD_RECEIPT),
                     "small actual V20 native build publication receipt")
    root = document(base, base["read_exact"](V20_ROOT_RECEIPT),
                    "small actual V20 private-root provenance receipt")
    real_previous_build = validate_actual_v20_receipts(v20, build, root)
    capture_contract = document(
        base, base["read_exact"](CAPTURE_FEATURE["contract"]),
        "independently reviewed cumulative captured-findall source contract",
    )
    for role in ("source", "protocol"):
        base["read_exact"](CAPTURE_FEATURE[role])
    captured_feature = validate_capture_feature(v20, capture_contract)
    captured = base["read_exact"](CAPTURE_VARIANT)
    previous_bytes = base["read_exact"](v20["LITERAL_VARIANT"])
    shape = validate_capture_bytes(v20, previous_bytes, captured)
    v18_state = previous_state.get("v18_state")
    require(type(v18_state) is dict
            and type(v18_state.get("originals")) is dict
            and len(v18_state["originals"]) == 9
            and type(v18_state.get("corrected_adapter")) is bytes
            and digest(v18_state["corrected_adapter"])
                == base["CORRECTED_ADAPTER_SHA256"]
            and len(v18_state["corrected_adapter"])
                == base["CORRECTED_ADAPTER_BYTES"]
            and type(v18_state.get("low_level_v9_source")) is bytes
            and previous_state.get("literal_bytes") == previous_bytes,
            "retain all nine original owners and exact complete V20 literal bridge")
    context: dict[str, object] = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "version": VERSION,
        "status": "PASS",
        "family": FAMILY,
        "source": source_info,
        "protocol": protocol_info,
        "authenticated_current_graph_version": GRAPH_VERSION,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "actual_previous_v20_build_receipt_sha256": V20_BUILD_RECEIPT[2],
        "actual_previous_v20_root_receipt_sha256": V20_ROOT_RECEIPT[2],
        "actual_previous_v20_build_status": "PASS",
        "actual_previous_v20_root_provenance_status": "PASS",
        "actual_previous_v20_native_artifact_count": 4,
        "first_party_rust_source_owner_count": 9,
        "literal_predecessor_sha256": v20["LITERAL_VARIANT"][2],
        "literal_predecessor_bytes": v20["LITERAL_VARIANT"][3],
        "captured_findall_variant_sha256": CAPTURE_VARIANT[2],
        "captured_findall_variant_bytes": CAPTURE_VARIANT[3],
        "captured_feature_source_sha256": CAPTURE_FEATURE["source"][2],
        "captured_feature_protocol_sha256": CAPTURE_FEATURE["protocol"][2],
        "captured_feature_contract_sha256": CAPTURE_FEATURE["contract"][2],
        "captured_feature_source_shape": "PASS",
        "phase1_v4_readiness": "PASS",
        "candidate_qualification": "BLOCKED",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "supplemental_reference_cases_per_worker": 8244,
        "historical_complete_rust_semantic_mismatch_count": 1440,
        "historical_complete_rust_verified_passing_case_count": 14853,
        "latest_rust_completed_suite_count": 8,
        "latest_rust_verified_passing_case_count": 12942,
        "latest_rust_worker_failure_count": 5,
        "latest_rust_semantic_mismatch_count": "NOT MEASURED",
        "expanded_holdout_proposal_source_sha256":
            v20["EXPANDED_HOLDOUT_PROPOSAL"]["source"][2],
        "expanded_holdout_proposal_protocol_sha256":
            v20["EXPANDED_HOLDOUT_PROPOSAL"]["protocol"][2],
        "expanded_holdout_proposal_contract_sha256":
            v20["EXPANDED_HOLDOUT_PROPOSAL"]["contract"][2],
        "expanded_holdout_proposal_source_field_count": 71,
        "expanded_holdout_proposal_verifier_executed": False,
        "expanded_holdout_proposal_cases_generated": 0,
        "expanded_holdout_proposal_cases_opened": 0,
        "future_phase_count": 2,
        "future_compiler_process_count_per_phase": 14,
        "future_total_compiler_process_count": 28,
        **boundary(v20),
    }
    state: dict[str, object] = {
        "source_info": source_info,
        "protocol_info": protocol_info,
        "v20_context": previous_context,
        "v20_state": previous_state,
        "v18_state": v18_state,
        "v20_build_receipt": build,
        "v20_root_receipt": root,
        "actual_v20_build": real_previous_build,
        "capture_contract": capture_contract,
        "capture_feature": captured_feature,
        "capture_shape": shape,
        "captured_bytes": captured,
        "immediate_literal_bytes": previous_bytes,
    }
    expected = contract_document(v20, base, source_pin, protocol_pin, state)
    if contract_pin is not None:
        checked_hash(contract_pin, "V21 complete canonical machine contract")
        raw, info = base["read_self"](CONTRACT_PATH, contract_pin)
        require(raw == canonical(base, expected)
                and document(base, raw, "complete V21 machine contract") == expected,
                "reject stale, partial, or substituted V21 source-freeze evidence")
        context["contract"] = info
    base["no_matching_imports"]()
    return context, state


def contract_document(
    v20: dict[str, object], base: dict[str, object], source_pin: str,
    protocol_pin: str, state: dict[str, object],
) -> dict[str, object]:
    owners = base["OWNER_BY_NAME"]
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "phase": "SOURCE FREEZE; CUMULATIVE CAPTURE NATIVE NOT BUILT OR RUN",
        "family": FAMILY,
        "source": {"path": SOURCE_PATH, "sha256": source_pin,
                   "bytes": state["source_info"]["bytes"]},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin,
                     "bytes": state["protocol_info"]["bytes"]},
        "pinned_cpython": {
            "implementation": "CPython", "version": "3.14.6",
            "executable": PYTHON, "sha256": PYTHON_SHA256,
            "isolated": True, "bytecode": False,
        },
        "published_current_graph": {
            "version": GRAPH_VERSION,
            "owners": row_group(v20["GRAPH"]),
            "owner_count": 4,
            "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
            "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
            "lower_bounds_are_not_a_global_census": True,
        },
        "phase1_v4_readiness": {
            "owners": row_group(v20["V19_PHASE1"]),
            "status": "PASS",
            "status_scope": "PHASE 1 PYTHON-ORACLE READINESS ONLY",
            "candidate_qualification_status": "BLOCKED",
            "qualification_blockers": list(v20["QUALIFICATION_BLOCKERS"]),
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "named_private_waiver_count": 13,
            "supplemental_reference_worker_count": 2,
            "supplemental_case_count_per_reference": 8244,
            "supplemental_added_to_original_denominator": False,
        },
        "historical_rust_results": {
            "historical_complete_candidate_status": "FAIL",
            "historical_complete_semantic_mismatch_count": 1440,
            "historical_complete_verified_passing_case_count": 14853,
            "latest_guarded_candidate_status": "FAIL",
            "latest_guarded_attempted_suite_count": 13,
            "latest_guarded_completed_suite_count": 8,
            "latest_guarded_verified_passing_case_count": 12942,
            "latest_guarded_worker_failure_count": 5,
            "latest_guarded_semantic_mismatch_count": "NOT MEASURED",
            "latest_guarded_failure_capture_complete": True,
            "candidate_qualified": False,
        },
        "authenticated_first_party_v20_source": {
            "owners": row_group(V20),
            "source_owner_count": 3,
            "source_modified": False,
            "historical_source_freeze_is_not_a_runtime_result": True,
        },
        "actual_successful_v20_native_build": {
            "publication_receipt": row_document(V20_BUILD_RECEIPT),
            "root_provenance_receipt": row_document(V20_ROOT_RECEIPT),
            "build_status": "PASS",
            "root_provenance_status": "PASS",
            "actual_compiler_process_count": 28,
            "actual_source_phase_count": 2,
            "actual_receipt_attested_native_artifact_count": 4,
            "immediate_literal_bridge":
                public_document(v20["LITERAL_VARIANT"]),
            "corrected_public_adapter_sha256":
                base["CORRECTED_ADAPTER_SHA256"],
            "corrected_public_adapter_bytes":
                base["CORRECTED_ADAPTER_BYTES"],
            "archive_metadata_attested_by_receipt": {
                **V20_ARCHIVE_METADATA,
                "archive_opened": False,
                "archive_hash_recomputed": False,
                "archive_bytes_read": 0,
            },
            "previous_private_root_opened": False,
            "previous_private_root_scanned": False,
            "previous_candidate_matching": "NOT RUN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "v21_captured_bridge_built": False,
        },
        "owned_rust_source_family": {
            "canonical_source_owners": [
                row_document(owners[name]) for name in base["RUST_SOURCE_NAMES"]
            ],
            "canonical_source_owner_count": 9,
            "private_overlays_per_phase": 2,
            "cargo_package_count": 1,
            "external_cargo_dependency_count": 0,
            "external_regular_expression_engine": "FORBIDDEN",
            "stdlib_regex_engine": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "canonical_sources_modified": False,
        },
        "independently_reviewed_literal_feature": {
            "owners": row_group(v20["LITERAL_FEATURE"]),
            "source_owner_count": 3,
            "variant": row_document(v20["LITERAL_VARIANT"]),
            "literal_single_pass_retained": True,
        },
        "independently_reviewed_captured_feature": {
            "owners": row_group(CAPTURE_FEATURE),
            "source_owner_count": 3,
            "variant": row_document(CAPTURE_VARIANT),
            "changed_function": "rust_append_batched_findall",
            "changed_first_party_function_count": 1,
            "specialized_capture_count": 2,
            "inherits_literal_single_pass": True,
            "historical_practice_case_count": 864,
            "historical_capture_findall_case_count": 48,
            "historical_materialized_capture_count": 44,
            "historical_empty_capture_count": 4,
            "new_variant_matching": "NOT RUN",
            "new_variant_correctness": "NOT MEASURED",
            "new_variant_performance": "NOT MEASURED",
        },
        "published_expanded_sealed_holdout_proposal": {
            "owners": row_group(v20["EXPANDED_HOLDOUT_PROPOSAL"]),
            "source_owner_count": 3,
            "source_field_count": 71,
            "proposal_status": "PRE-PHASE-3 PROPOSAL",
            "final_protocol_status": "NOT FROZEN",
            "generator_status": "NOT FROZEN",
            "secret_status": "NOT GENERATED",
            "case_status": "NOT GENERATED; NOT OPENED",
            "case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
            "timed_case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
            "preserved_previous_proposal_case_count":
                PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT,
            "operation_count": 36,
            "pattern_family_count": 24,
            "subject_type_count": 4,
            "lifecycle_count": 4,
            "stratum_count": 13824,
            "cases_per_stratum": 1024,
            "qualified_independent_family_count": 0,
            "minimum_qualified_independent_family_count": 3,
            "timing_status": "NOT RUN; NOT MEASURED",
            "memory_status": "NOT RUN; NOT MEASURED",
            "runtime_independence_status": "NOT ESTABLISHED",
            "winner_status": "NOT SELECTED",
            "proposal_verifier_executed": False,
            "proposal_cases_generated": 0,
            "proposal_cases_opened": 0,
            "proposal_generator_run": False,
        },
        "authenticated_first_party_build_kernel": {
            "v20_source": row_document(V20["source"]),
            "v16": [row_document(owners[name]) for name in (
                "v16_builder", "v16_protocol", "v16_contract",
            )],
            "v9": [row_document(owners[name]) for name in (
                "low_level_v9", "low_level_v9_protocol", "low_level_v9_contract",
            )],
            "v7": [row_document(owners[name]) for name in (
                "low_level_v7", "low_level_v7_protocol", "low_level_v7_contract",
            )],
            "build_kernel_run_during_source_freeze": False,
        },
        "future_offline_captured_root_provenance_build": {
            "authorization": "EXPLICIT FUTURE --build ONLY",
            "unique_label": BUILD_LABEL,
            "root_parent": "/tmp",
            "exact_owned_private_root_prefix": ROOT_PREFIX,
            "private_root_path": "NOT MEASURED",
            "private_root_device": "NOT MEASURED",
            "private_root_inode": "NOT MEASURED",
            "private_root_uid": "NOT MEASURED",
            "private_root_mode": "0700",
            "root_capture_flags": "O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW",
            "root_capture_origin":
                "ACTUAL verify_actual_phases(v9,v7,workdir,phases,steps) CALLBACK",
            "tmp_directory_scanning": "FORBIDDEN",
            "phase_names": list(PHASES),
            "independent_phase_count": 2,
            "source_owners_per_phase": 9,
            "unchanged_source_owners_per_phase": 7,
            "cumulative_captured_bridge_overlays": 2,
            "corrected_public_adapter_overlays": 2,
            "process_roles_per_phase": list(PROCESS_NAMES),
            "compiler_process_count_per_phase": 14,
            "expected_actual_compiler_process_count": 28,
            "cargo_flags": ["--release", "--locked", "--offline", "--frozen"],
            "phase_local_cargo_home": True,
            "external_cargo_dependency_count": 0,
            "verify_original_reproducibility_first": True,
            "compare_complete_owned_engine_and_bridge_elf": True,
            "root_receipt_exclusive_creation": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "root_receipt_file_fsync": True,
            "root_receipt_directory_fsync": True,
            "additional_root_receipt_count": 1,
            "native_activation": "FORBIDDEN",
            "matching_or_candidate_workers": "FORBIDDEN",
            "holdout": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "build_pass_means": "REPRODUCIBLE COMPILATION AND ROOT PROVENANCE ONLY",
        },
        "performance_evidence": {
            "historical_public_practice_case_count": 864,
            "historical_capture_findall_case_count": 48,
            "historical_materialized_capture_count": 44,
            "historical_empty_capture_count": 4,
            "cumulative_captured_variant_development_cohort": "NOT FROZEN",
            "candidate_matching": "NOT RUN",
            "speedup": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "final_holdout_proposal_status": "PRE-PHASE-3 PROPOSAL",
            "final_holdout_case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
            "previous_holdout_proposal_case_count":
                PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT,
            "final_holdout": "NOT OPENED",
            "winner_selected": False,
        },
        "source_only_effects": boundary(v20),
    }


def synthetic_root_plan(
    v20: dict[str, object], v19: dict[str, object], base: dict[str, object],
) -> dict[str, object]:
    plan = base["clone"](v20["synthetic_root_plan"](v19, base))
    require(type(plan) is dict, "derive only the exact first-party synthetic plan")
    plan["schema"] = SCHEMA + "-synthetic-root-control"
    plan["graph_version"] = GRAPH_VERSION
    plan["captured_variant_sha256"] = CAPTURE_VARIANT[2]
    plan["captured_variant_bytes"] = CAPTURE_VARIANT[3]
    plan["immediate_literal_predecessor_sha256"] = v20["LITERAL_VARIANT"][2]
    plan["immediate_literal_predecessor_bytes"] = v20["LITERAL_VARIANT"][3]
    return plan


def validate_synthetic_root(
    v20: dict[str, object], v19: dict[str, object], base: dict[str, object],
    plan: object,
) -> dict[str, object]:
    require(type(plan) is dict
            and plan.get("schema") == SCHEMA + "-synthetic-root-control"
            and plan.get("graph_version") == GRAPH_VERSION
            and plan.get("captured_variant_sha256") == CAPTURE_VARIANT[2]
            and plan.get("captured_variant_bytes") == CAPTURE_VARIANT[3]
            and plan.get("immediate_literal_predecessor_sha256")
                == v20["LITERAL_VARIANT"][2]
            and plan.get("immediate_literal_predecessor_bytes")
                == v20["LITERAL_VARIANT"][3]
            and plan.get("actual_root_descriptor_opens") == 0
            and plan.get("actual_compiler_process_count") == 0
            and plan.get("candidate_workers_started") == 0
            and plan.get("archive_opens") == 0
            and plan.get("native_libraries_loaded") == 0
            and plan.get("holdout") == "NOT OPENED",
            "reject invented actual builds, roots, native execution, or holdout")
    previous = base["clone"](plan)
    previous["schema"] = v20["SCHEMA"] + "-synthetic-root-control"
    for name in (
        "captured_variant_sha256", "captured_variant_bytes",
        "immediate_literal_predecessor_sha256",
        "immediate_literal_predecessor_bytes",
    ):
        previous.pop(name)
    proof = v20["validate_synthetic_root"](v19, base, previous)
    require(proof.get("status") == "PASS"
            and proof.get("synthetic_only") is True
            and proof.get("synthetic_phase_count") == 2
            and proof.get("synthetic_native_owner_count") == 4
            and proof.get("synthetic_process_role_count") == 28
            and proof.get("actual_root_descriptor_opens") == 0
            and proof.get("actual_compiler_process_count") == 0,
            "retain all 28 synthetic controls without executing a compiler")
    return {**proof, "captured_variant_sha256": CAPTURE_VARIANT[2],
            "captured_variant_bytes": CAPTURE_VARIANT[3]}


def checked_label(value: object) -> str:
    require(type(value) is str and 0 < len(value) <= 48
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in value),
            "require an exact safe unique V21 first-party evidence label")
    return value


def evidence_names(label: str, failed: bool) -> tuple[str, str]:
    require(label == BUILD_LABEL and type(failed) is bool,
            "require the uniquely owned V21 captured-build outcome")
    stem = "native-source-build-v21-rust-" + checked_label(label)
    if failed:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def root_receipt_name(label: str) -> str:
    require(label == BUILD_LABEL,
            "reject a borrowed V21 capture root-provenance label")
    return "native-source-build-v21-rust-" + checked_label(label) \
        + "-root-provenance-receipt.json"


def assert_fresh_root_receipt(label: str) -> None:
    target = ROOT + "/" + EVIDENCE_PATH + "/" + root_receipt_name(label)
    try:
        os.lstat(target)
    except FileNotFoundError:
        return
    raise GateError("reject a preexisting V21 captured-build provenance receipt")


def parse_cli(
    v20: dict[str, object], base: dict[str, object], values: list[str],
) -> dict[str, object]:
    modes = ("--self-test", "--verify-frozen-context", "--render-contract", "--build")
    selected = [mode for mode in modes if mode in values]
    require(len(selected) == 1 and values.count(selected[0]) == 1,
            "require one separately authorized V21 source or build mode")
    mode = selected[0]
    result: dict[str, object] = {"mode": mode, "owned_source_sha256": []}
    mapping = {
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
        "--label": "label",
        "--combined-bridge-sha256": "combined_bridge_sha256",
        "--combined-bridge-bytes": "combined_bridge_bytes",
        "--corrected-adapter-sha256": "corrected_adapter_sha256",
        "--corrected-adapter-bytes": "corrected_adapter_bytes",
        "--predecessor-bridge-sha256": "predecessor_bridge_sha256",
        "--predecessor-bridge-bytes": "predecessor_bridge_bytes",
        "--previous-v20-source-sha256": "previous_v20_source_sha256",
        "--previous-v20-protocol-sha256": "previous_v20_protocol_sha256",
        "--previous-v20-contract-sha256": "previous_v20_contract_sha256",
        "--previous-build-receipt-sha256": "previous_build_receipt_sha256",
        "--previous-root-receipt-sha256": "previous_root_receipt_sha256",
        "--graph-summary-sha256": "graph_summary_sha256",
        "--captured-feature-source-sha256": "captured_feature_source_sha256",
        "--captured-feature-protocol-sha256": "captured_feature_protocol_sha256",
        "--captured-feature-contract-sha256": "captured_feature_contract_sha256",
        "--expanded-holdout-proposal-source-sha256":
            "expanded_holdout_proposal_source_sha256",
        "--expanded-holdout-proposal-protocol-sha256":
            "expanded_holdout_proposal_protocol_sha256",
        "--expanded-holdout-proposal-contract-sha256":
            "expanded_holdout_proposal_contract_sha256",
        "--phase1-v4-source-sha256": "phase1_v4_source_sha256",
        "--phase1-v4-protocol-sha256": "phase1_v4_protocol_sha256",
        "--phase1-v4-contract-sha256": "phase1_v4_contract_sha256",
    }
    index = 0
    while index < len(values):
        flag = values[index]
        if flag == mode:
            index += 1
            continue
        if flag == "--owned-source-sha256":
            require(index + 1 < len(values), "reject incomplete original owner pin")
            result["owned_source_sha256"].append(values[index + 1])
            index += 2
            continue
        require(flag in mapping and index + 1 < len(values),
                "reject abbreviated or unowned cumulative build authority")
        name = mapping[flag]
        require(name not in result, "reject duplicate build authority: " + flag)
        value: object = values[index + 1]
        if name.endswith("_bytes"):
            require(type(value) is str and value.isascii() and value.isdecimal(),
                    "require exact positive first-party source size")
            value = int(value)
        result[name] = value
        index += 2
    for name in ("source_sha256", "protocol_sha256"):
        require(name in result, "caller-pin the independent V21 source and protocol")
        checked_hash(result[name], name)
    build_only = (
        "label", "combined_bridge_sha256", "combined_bridge_bytes",
        "corrected_adapter_sha256", "corrected_adapter_bytes",
        "predecessor_bridge_sha256", "predecessor_bridge_bytes",
        "previous_v20_source_sha256", "previous_v20_protocol_sha256",
        "previous_v20_contract_sha256", "previous_build_receipt_sha256",
        "previous_root_receipt_sha256", "graph_summary_sha256",
        "captured_feature_source_sha256", "captured_feature_protocol_sha256",
        "captured_feature_contract_sha256",
        "expanded_holdout_proposal_source_sha256",
        "expanded_holdout_proposal_protocol_sha256",
        "expanded_holdout_proposal_contract_sha256",
        "phase1_v4_source_sha256", "phase1_v4_protocol_sha256",
        "phase1_v4_contract_sha256",
    )
    if mode == "--render-contract":
        require("contract_sha256" not in result,
                "render the exact source contract before its SHA-256 exists")
    else:
        require("contract_sha256" in result,
                "independently caller-pin the complete V21 machine contract")
        checked_hash(result["contract_sha256"], "V21 canonical contract")
    if mode != "--build":
        require(not result["owned_source_sha256"]
                and all(key not in result for key in build_only),
                "source-only verification never authorizes a native build")
        return result
    require(result.get("label") == BUILD_LABEL
            and checked_label(BUILD_LABEL) == BUILD_LABEL
            and result.get("combined_bridge_sha256") == CAPTURE_VARIANT[2]
            and result.get("combined_bridge_bytes") == CAPTURE_VARIANT[3]
            and result.get("corrected_adapter_sha256")
                == base["CORRECTED_ADAPTER_SHA256"]
            and result.get("corrected_adapter_bytes")
                == base["CORRECTED_ADAPTER_BYTES"]
            and result.get("predecessor_bridge_sha256")
                == v20["LITERAL_VARIANT"][2]
            and result.get("predecessor_bridge_bytes")
                == v20["LITERAL_VARIANT"][3]
            and result.get("previous_v20_source_sha256") == V20["source"][2]
            and result.get("previous_v20_protocol_sha256") == V20["protocol"][2]
            and result.get("previous_v20_contract_sha256") == V20["contract"][2]
            and result.get("previous_build_receipt_sha256") == V20_BUILD_RECEIPT[2]
            and result.get("previous_root_receipt_sha256") == V20_ROOT_RECEIPT[2]
            and result.get("graph_summary_sha256")
                == v20["GRAPH"]["summary"][2]
            and result.get("captured_feature_source_sha256")
                == CAPTURE_FEATURE["source"][2]
            and result.get("captured_feature_protocol_sha256")
                == CAPTURE_FEATURE["protocol"][2]
            and result.get("captured_feature_contract_sha256")
                == CAPTURE_FEATURE["contract"][2]
            and result.get("expanded_holdout_proposal_source_sha256")
                == v20["EXPANDED_HOLDOUT_PROPOSAL"]["source"][2]
            and result.get("expanded_holdout_proposal_protocol_sha256")
                == v20["EXPANDED_HOLDOUT_PROPOSAL"]["protocol"][2]
            and result.get("expanded_holdout_proposal_contract_sha256")
                == v20["EXPANDED_HOLDOUT_PROPOSAL"]["contract"][2],
            "caller-pin actual V20 receipts, capture source, and unopened proposal")
    for role, key in (
        ("source", "phase1_v4_source_sha256"),
        ("protocol", "phase1_v4_protocol_sha256"),
        ("contract", "phase1_v4_contract_sha256"),
    ):
        require(result.get(key) == v20["V19_PHASE1"][role][2],
                "independently caller-pin all three passing P0 reference owners")
    expected = {
        base["OWNER_BY_NAME"][name][1] + "=" + base["OWNER_BY_NAME"][name][2]
        for name in base["RUST_SOURCE_NAMES"]
    }
    provided = result["owned_source_sha256"]
    require(type(provided) is list and len(provided) == 9
            and set(provided) == expected,
            "caller-pin precisely nine original independent Rust source owners")
    return result


def future_build_arguments(
    v20: dict[str, object], base: dict[str, object],
    source_pin: str, protocol_pin: str, contract_pin: str,
) -> list[str]:
    arguments = [
        "--build",
        "--source-sha256", source_pin,
        "--protocol-sha256", protocol_pin,
        "--contract-sha256", contract_pin,
        "--label", BUILD_LABEL,
        "--combined-bridge-sha256", CAPTURE_VARIANT[2],
        "--combined-bridge-bytes", str(CAPTURE_VARIANT[3]),
        "--corrected-adapter-sha256", base["CORRECTED_ADAPTER_SHA256"],
        "--corrected-adapter-bytes", str(base["CORRECTED_ADAPTER_BYTES"]),
        "--predecessor-bridge-sha256", v20["LITERAL_VARIANT"][2],
        "--predecessor-bridge-bytes", str(v20["LITERAL_VARIANT"][3]),
        "--previous-v20-source-sha256", V20["source"][2],
        "--previous-v20-protocol-sha256", V20["protocol"][2],
        "--previous-v20-contract-sha256", V20["contract"][2],
        "--previous-build-receipt-sha256", V20_BUILD_RECEIPT[2],
        "--previous-root-receipt-sha256", V20_ROOT_RECEIPT[2],
        "--graph-summary-sha256", v20["GRAPH"]["summary"][2],
        "--captured-feature-source-sha256", CAPTURE_FEATURE["source"][2],
        "--captured-feature-protocol-sha256", CAPTURE_FEATURE["protocol"][2],
        "--captured-feature-contract-sha256", CAPTURE_FEATURE["contract"][2],
        "--expanded-holdout-proposal-source-sha256",
        v20["EXPANDED_HOLDOUT_PROPOSAL"]["source"][2],
        "--expanded-holdout-proposal-protocol-sha256",
        v20["EXPANDED_HOLDOUT_PROPOSAL"]["protocol"][2],
        "--expanded-holdout-proposal-contract-sha256",
        v20["EXPANDED_HOLDOUT_PROPOSAL"]["contract"][2],
        "--phase1-v4-source-sha256", v20["V19_PHASE1"]["source"][2],
        "--phase1-v4-protocol-sha256", v20["V19_PHASE1"]["protocol"][2],
        "--phase1-v4-contract-sha256", v20["V19_PHASE1"]["contract"][2],
    ]
    for name in base["RUST_SOURCE_NAMES"]:
        row = base["OWNER_BY_NAME"][name]
        arguments.extend(("--owned-source-sha256", row[1] + "=" + row[2]))
    return arguments


def self_test(
    v20: dict[str, object], v19: dict[str, object], base: dict[str, object],
    source_pin: str, protocol_pin: str, contract_pin: str,
) -> dict[str, object]:
    context, state = collect_context(
        v20, v19, base, source_pin, protocol_pin, contract_pin,
    )
    accepted = 0
    rejected = 0

    def reject(operation: object, label: str) -> None:
        nonlocal rejected
        try:
            operation()
        except Exception:
            rejected += 1
            return
        raise GateError("accepted hostile cumulative Rust V21 control: " + label)

    plan = synthetic_root_plan(v20, v19, base)
    proof = validate_synthetic_root(v20, v19, base, plan)
    require(proof.get("synthetic_process_role_count") == 28,
            "verify only synthetic process roles, never run a compiler")
    accepted += 1
    require(context.get("status") == "PASS"
            and state["actual_v20_build"]["actual_previous_build_status"] == "PASS"
            and state["actual_v20_build"]["actual_previous_compiler_process_count"]
                == 28
            and state["capture_shape"]["changed_first_party_function_count"] == 1
            and state["capture_feature"]["historical_findall_case_count"] == 48
            and state["capture_feature"]["historical_materialized_capture_count"]
                == 44
            and state["capture_feature"]["historical_empty_capture_count"] == 4,
            "authenticate actual V20 receipts and the historical 48/44/4 cohort")
    accepted += 1
    authorized = future_build_arguments(
        v20, base, source_pin, protocol_pin, contract_pin,
    )
    parsed = parse_cli(v20, base, authorized)
    require(parsed.get("mode") == "--build"
            and parsed.get("combined_bridge_sha256") == CAPTURE_VARIANT[2]
            and parsed.get("combined_bridge_bytes") == CAPTURE_VARIANT[3]
            and len(parsed["owned_source_sha256"]) == 9
            and parsed.get("previous_build_receipt_sha256")
                == V20_BUILD_RECEIPT[2]
            and parsed.get("previous_root_receipt_sha256")
                == V20_ROOT_RECEIPT[2]
            and _ROOT_CAPTURE is None and base.get("_WALL_ENABLED") is True,
            "verify future cumulative build arguments without authorizing execution")
    accepted += 1
    for key, replacement in (
        ("schema", "borrowed-synthetic-root"),
        ("graph_version", 85),
        ("captured_variant_sha256", v20["LITERAL_VARIANT"][2]),
        ("captured_variant_bytes", v20["LITERAL_VARIANT"][3]),
        ("immediate_literal_predecessor_sha256", CAPTURE_VARIANT[2]),
        ("immediate_literal_predecessor_bytes", CAPTURE_VARIANT[3]),
        ("root_path", "/tmp/borrowed-root"),
        ("root_device", 0),
        ("root_inode", 0),
        ("root_uid", -1),
        ("root_mode", "0755"),
        ("root_evidence_kind", "ACTUAL ROOT"),
        ("phase_count", 1),
        ("expected_process_count", 27),
        ("actual_root_descriptor_opens", 1),
        ("actual_compiler_process_count", 1),
        ("candidate_workers_started", 1),
        ("archive_opens", 1),
        ("native_libraries_loaded", 1),
        ("holdout", "OPENED"),
    ):
        changed = base["clone"](plan)
        changed[key] = replacement
        reject(lambda value=changed: validate_synthetic_root(
            v20, v19, base, value,
        ), "synthetic-root:" + key)
    for index in range(2):
        for key, replacement in (
            ("name", "borrowed"), ("inode", 0), ("mode", "0755"),
            ("evidence_kind", "ACTUAL ROOT"),
        ):
            changed = base["clone"](plan)
            changed["phases"][index][key] = replacement
            reject(lambda value=changed: validate_synthetic_root(
                v20, v19, base, value,
            ), "synthetic-phase:" + str(index) + ":" + key)
        for role in ("engine", "bridge"):
            for key, replacement in (
                ("sha256", "0" * 64), ("inode", 0),
                ("file_name", "foreign_regex.so"), ("mode", "0644"),
                ("evidence_kind", "ACTUAL NATIVE"),
            ):
                changed = base["clone"](plan)
                changed["phases"][index]["native_outputs"][role][key] = replacement
                reject(lambda value=changed: validate_synthetic_root(
                    v20, v19, base, value,
                ), "synthetic-native:" + role + ":" + key)
    for index in range(28):
        for key, replacement in (
            ("name", "build_external_regex"),
            ("phase", "borrowed-phase"),
            ("pid", 0),
            ("exit_status", 1),
            ("evidence_kind", "ACTUAL COMPILER"),
        ):
            changed = base["clone"](plan)
            changed["processes"][index][key] = replacement
            reject(lambda value=changed: validate_synthetic_root(
                v20, v19, base, value,
            ), "synthetic-process:" + str(index) + ":" + key)
    for key, replacement in (
        ("schema", "foreign-capture-feature"),
        ("version", 2),
        ("status", "PASS"),
        ("family", "c"),
    ):
        changed = dict(state["capture_contract"])
        changed[key] = replacement
        reject(lambda value=changed: validate_capture_feature(v20, value),
               "captured-feature:" + key)
    for section, key, replacement in (
        ("candidate_variant", "sha256", v20["LITERAL_VARIANT"][2]),
        ("candidate_variant", "bytes", v20["LITERAL_VARIANT"][3]),
        ("candidate_variant", "changed_function_count", 2),
        ("candidate_variant", "specialized_capture_count", 1),
        ("candidate_variant", "inherits_literal_single_pass", False),
        ("candidate_variant", "qualified", True),
        ("immediate_literal_predecessor", "sha256", CAPTURE_VARIANT[2]),
        ("historical_public_practice", "findall_case_count", 47),
        ("historical_public_practice", "materialized_capture_case_count", 43),
        ("historical_public_practice", "empty_capture_case_count", 3),
        ("historical_public_practice", "new_variant_timed", True),
        ("phase_boundary", "clock_samples", 1),
        ("phase_boundary", "hidden_cases_read", 1),
        ("phase_boundary", "performance", "FASTER"),
    ):
        changed = dict(state["capture_contract"])
        inner = dict(changed[section])
        inner[key] = replacement
        changed[section] = inner
        reject(lambda value=changed: validate_capture_feature(v20, value),
               "captured-feature:" + section + ":" + key)
    for key, replacement in (
        ("schema", SCHEMA + "-durable-publication-receipt"),
        ("status", "FAIL"),
        ("build_status", "FAIL"),
        ("source_sha256", "0" * 64),
        ("protocol_sha256", "0" * 64),
        ("contract_sha256", "0" * 64),
        ("actual_compiler_process_count", 27),
        ("combined_bridge_sha256", CAPTURE_VARIANT[2]),
        ("combined_bridge_bytes", CAPTURE_VARIANT[3]),
        ("archive_sha256", "0" * 64),
        ("candidate_matching", "PASS"),
        ("candidate_qualified", True),
        ("hidden_cases_read", 1),
        ("clock_samples", 1),
        ("holdout", "OPENED"),
    ):
        changed = dict(state["v20_build_receipt"])
        changed[key] = replacement
        reject(lambda value=changed: validate_actual_v20_receipts(
            v20, value, state["v20_root_receipt"],
        ), "actual-v20-build-receipt:" + key)
    for key, replacement in (
        ("schema", SCHEMA + "-durable-root-provenance-receipt"),
        ("status", "FAIL"),
        ("canonical_build_receipt_sha256", "0" * 64),
        ("canonical_build_archive_sha256", "0" * 64),
        ("canonical_build_archive_opened", True),
        ("actual_compiler_process_count", 27),
        ("actual_source_phase_count", 1),
        ("bridge_overlay_apply_count", 1),
        ("candidate_qualified", True),
        ("tmp_directory_scanned", True),
        ("hidden_cases_read", 1),
        ("holdout", "OPENED"),
    ):
        changed = dict(state["v20_root_receipt"])
        changed[key] = replacement
        reject(lambda value=changed: validate_actual_v20_receipts(
            v20, state["v20_build_receipt"], value,
        ), "actual-v20-root-receipt:" + key)
    previous = state["immediate_literal_bytes"]
    captured = state["captured_bytes"]
    for old, fresh, label in (
        (previous, captured[:-1], "truncated-captured-bridge"),
        (previous, captured + b"\n", "extended-captured-bridge"),
        (previous, previous, "borrowed-literal-bridge"),
        (previous[:-1], captured, "truncated-literal-predecessor"),
        (captured, captured, "substituted-literal-predecessor"),
    ):
        reject(lambda before=old, after=fresh: validate_capture_bytes(
            v20, before, after,
        ), "capture-source:" + label)
    for flag, replacement in (
        ("--combined-bridge-sha256", v20["LITERAL_VARIANT"][2]),
        ("--combined-bridge-bytes", str(v20["LITERAL_VARIANT"][3])),
        ("--corrected-adapter-sha256", "0" * 64),
        ("--predecessor-bridge-sha256", CAPTURE_VARIANT[2]),
        ("--previous-v20-source-sha256", "0" * 64),
        ("--previous-v20-protocol-sha256", "0" * 64),
        ("--previous-v20-contract-sha256", "0" * 64),
        ("--previous-build-receipt-sha256", "0" * 64),
        ("--previous-root-receipt-sha256", "0" * 64),
        ("--graph-summary-sha256", "0" * 64),
        ("--captured-feature-source-sha256", "0" * 64),
        ("--captured-feature-protocol-sha256", "0" * 64),
        ("--captured-feature-contract-sha256", "0" * 64),
        ("--expanded-holdout-proposal-source-sha256", "0" * 64),
        ("--expanded-holdout-proposal-protocol-sha256", "0" * 64),
        ("--expanded-holdout-proposal-contract-sha256", "0" * 64),
        ("--phase1-v4-source-sha256", "0" * 64),
        ("--label", "borrowed-build"),
    ):
        changed = list(authorized)
        position = changed.index(flag)
        changed[position + 1] = replacement
        reject(lambda value=changed: parse_cli(v20, base, value),
               "future-capture-build:" + flag)
    omitted = list(authorized[:-2])
    reject(lambda: parse_cli(v20, base, omitted),
           "future-capture-build:omitted-owner")
    duplicate = list(authorized)
    duplicate.extend(authorized[-2:])
    reject(lambda: parse_cli(v20, base, duplicate),
           "future-capture-build:duplicated-owner")
    probes = (
        ("unlisted-file", lambda: builtins.open("/etc/hosts", "rb")),
        ("tmp-root-scan", lambda: builtins.open("/tmp", "rb")),
        ("previous-private-root", lambda: sys.audit(
            "open", "/tmp/" + ROOT_PREFIX + "forbidden", "r", os.O_RDONLY,
        )),
        ("v21-source-mutation", lambda: builtins.open(
            ROOT + "/" + SOURCE_PATH, "w",
        )),
        ("captured-source-mutation", lambda: builtins.open(
            ROOT + "/" + CAPTURE_VARIANT[1], "w",
        )),
        ("v20-archive", lambda: builtins.open(
            ROOT + "/" + V20_ARCHIVE_METADATA["path"], "rb",
        )),
        ("hidden-holdout", lambda: builtins.open(
            ROOT + "/benchmarks/holdout.json", "rb",
        )),
        ("stdlib-regex", lambda: sys.audit(
            "import", "re", None, None, None, None,
        )),
        ("cpython-matcher", lambda: sys.audit(
            "import", "_sre", None, None, None, None,
        )),
        ("candidate-import", lambda: sys.audit(
            "import", "candidates.rust_candidate", None, None, None, None,
        )),
        ("native-load", lambda: sys.audit("ctypes.dlopen", "foreign.so")),
        ("compiler", lambda: sys.audit(
            "subprocess.Popen", "cargo", (), None, None,
        )),
        ("network", lambda: sys.audit("socket.__new__", None, 2, 1, 0)),
        ("thread", lambda: sys.audit("threading.Thread.start", None)),
        ("clock", lambda: sys.audit("time.perf_counter")),
        ("temporary-root", lambda: sys.audit(
            "tempfile.mkdtemp", "/tmp/forbidden",
        )),
        ("filesystem-rename", lambda: sys.audit(
            "os.rename", "a", "b", -1, -1,
        )),
        ("archive-inflation", lambda: sys.audit(
            "gzip.decompress", b"forbidden",
        )),
        ("foreign-execution", lambda: sys.audit("exec", "forbidden")),
        ("foreign-compilation", lambda: sys.audit(
            "compile", b"forbidden", "foreign.py",
        )),
    )
    for label, operation in probes:
        reject(operation, "physically-block:" + label)
    for category in (
        "filesystem", "matching_import", "native", "process", "network",
        "thread", "clock", "temporary", "archive", "dynamic_execution",
    ):
        require(base["_BLOCKED"].get(category, 0) >= 1,
                "physically exercise the source-only audit wall: " + category)
    require(rejected >= 240,
            "reject complete cumulative capture, prior receipt, and process controls")
    base["no_matching_imports"]()
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "version": VERSION,
        "family": FAMILY,
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_positive_control_count": accepted,
        "rejected_hostile_controls": rejected,
        "blocked_effect_attempts": dict(base["_BLOCKED"]),
        "synthetic_control_proof": proof,
        "authenticated_current_graph_version": GRAPH_VERSION,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "actual_previous_v20_build_receipt_sha256": V20_BUILD_RECEIPT[2],
        "actual_previous_v20_root_receipt_sha256": V20_ROOT_RECEIPT[2],
        "actual_previous_v20_build_status": "PASS",
        "actual_previous_v20_root_provenance_status": "PASS",
        "literal_predecessor_sha256": v20["LITERAL_VARIANT"][2],
        "literal_predecessor_bytes": v20["LITERAL_VARIANT"][3],
        "captured_findall_variant_sha256": CAPTURE_VARIANT[2],
        "captured_findall_variant_bytes": CAPTURE_VARIANT[3],
        "captured_feature_source_sha256": CAPTURE_FEATURE["source"][2],
        "captured_feature_protocol_sha256": CAPTURE_FEATURE["protocol"][2],
        "captured_feature_contract_sha256": CAPTURE_FEATURE["contract"][2],
        "changed_first_party_function_count": 1,
        "specialized_capture_count": 2,
        "historical_complete_rust_semantic_mismatch_count": 1440,
        "historical_complete_rust_verified_passing_case_count": 14853,
        "latest_rust_completed_suite_count": 8,
        "latest_rust_verified_passing_case_count": 12942,
        "latest_rust_worker_failure_count": 5,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "future_total_compiler_process_count": 28,
        "expanded_holdout_proposal_source_sha256":
            v20["EXPANDED_HOLDOUT_PROPOSAL"]["source"][2],
        "expanded_holdout_proposal_protocol_sha256":
            v20["EXPANDED_HOLDOUT_PROPOSAL"]["protocol"][2],
        "expanded_holdout_proposal_contract_sha256":
            v20["EXPANDED_HOLDOUT_PROPOSAL"]["contract"][2],
        "expanded_holdout_proposal_verifier_executed": False,
        "expanded_holdout_proposal_cases_generated": 0,
        "expanded_holdout_proposal_cases_opened": 0,
        **boundary(v20),
    }


def publish_root_provenance(
    v20: dict[str, object], base: dict[str, object], module: object,
    state: dict[str, object], result: dict[str, object],
    options: dict[str, object],
) -> dict[str, object]:
    require(result.get("status") == "PASS"
            and result.get("build_status") == "PASS"
            and result.get("family") == FAMILY
            and result.get("label") == BUILD_LABEL
            and type(_ROOT_CAPTURE) is dict,
            "publish V21 root evidence only after an actual successful full build")
    captured = _ROOT_CAPTURE
    assert isinstance(captured, dict)
    require(captured.get("unique_process_count") == 28
            and captured.get("phase_count") == 2,
            "require the genuine complete two-phase V21 compiler proof")
    runtime = state.get("runtime_state")
    require(type(runtime) is dict and runtime.get("kernel") is not None,
            "retain actual first-party durable compiler publication kernel")
    kernel = runtime["kernel"]
    relative = result.get("receipt_relative")
    receipt_hash = result.get("receipt_sha256")
    require(type(relative) is str
            and relative == EVIDENCE_PATH + "/" + evidence_names(BUILD_LABEL, False)[1],
            "bind only the fresh V21 captured-build publication receipt")
    checked_hash(receipt_hash, "actual V21 captured-build receipt")
    absolute = ROOT + "/" + relative
    observed = os.stat(absolute, follow_symlinks=False)
    row = ("actual_v21_capture_build_receipt", relative, receipt_hash,
           observed.st_size, observed.st_dev, observed.st_ino)
    base["_ALLOWLIST"] = frozenset(set(base["_ALLOWLIST"]) | {absolute})
    receipt = document(base, base["read_exact"](row),
                       "fresh genuine first-party V21 captured-build receipt")
    require(receipt.get("schema") == SCHEMA + "-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("label") == BUILD_LABEL
            and receipt.get("source_sha256") == options["source_sha256"]
            and receipt.get("protocol_sha256") == options["protocol_sha256"]
            and receipt.get("contract_sha256") == options["contract_sha256"]
            and receipt.get("expected_actual_compiler_process_count") == 28
            and receipt.get("actual_compiler_process_count") == 28
            and receipt.get("combined_bridge_sha256") == CAPTURE_VARIANT[2]
            and receipt.get("combined_bridge_bytes") == CAPTURE_VARIANT[3]
            and receipt.get("combined_bridge_overlay_apply_count") == 2
            and receipt.get("corrected_public_adapter_overlay_apply_count") == 2
            and receipt.get("archive_relative") == result.get("archive_relative")
            and receipt.get("archive_sha256") == result.get("archive_sha256")
            and receipt.get("candidate_matching") == "NOT RUN"
            and receipt.get("candidate_qualified") is False,
            "authenticate all genuine actual compiler results before V21 root proof")
    record = {
        "schema": SCHEMA + "-durable-root-provenance-receipt",
        "version": VERSION,
        "status": "PASS",
        "publication_pass_means":
            "DURABLE REPRODUCIBLE FIRST-PARTY CAPTURE BUILD ROOT PROVENANCE ONLY",
        "family": FAMILY,
        "label": BUILD_LABEL,
        "source_sha256": options["source_sha256"],
        "protocol_sha256": options["protocol_sha256"],
        "contract_sha256": options["contract_sha256"],
        "frozen_graph_version": GRAPH_VERSION,
        "frozen_graph_summary_sha256": v20["GRAPH"]["summary"][2],
        "previous_v20_source_sha256": V20["source"][2],
        "previous_v20_protocol_sha256": V20["protocol"][2],
        "previous_v20_contract_sha256": V20["contract"][2],
        "previous_v20_build_receipt_sha256": V20_BUILD_RECEIPT[2],
        "previous_v20_root_receipt_sha256": V20_ROOT_RECEIPT[2],
        "previous_literal_bridge_sha256": v20["LITERAL_VARIANT"][2],
        "previous_literal_bridge_bytes": v20["LITERAL_VARIANT"][3],
        "cumulative_captured_bridge_sha256": CAPTURE_VARIANT[2],
        "cumulative_captured_bridge_bytes": CAPTURE_VARIANT[3],
        "captured_feature_source_sha256": CAPTURE_FEATURE["source"][2],
        "captured_feature_protocol_sha256": CAPTURE_FEATURE["protocol"][2],
        "captured_feature_contract_sha256": CAPTURE_FEATURE["contract"][2],
        "expanded_holdout_proposal_source_sha256":
            v20["EXPANDED_HOLDOUT_PROPOSAL"]["source"][2],
        "expanded_holdout_proposal_protocol_sha256":
            v20["EXPANDED_HOLDOUT_PROPOSAL"]["protocol"][2],
        "expanded_holdout_proposal_contract_sha256":
            v20["EXPANDED_HOLDOUT_PROPOSAL"]["contract"][2],
        "expanded_holdout_proposal_status": "PRE-PHASE-3 PROPOSAL",
        "expanded_holdout_proposal_case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
        "previous_holdout_proposal_case_count":
            PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT,
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "expanded_holdout_generator_status": "NOT FROZEN",
        "expanded_holdout_secret_status": "NOT GENERATED",
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "expanded_holdout_proposal_verifier_executed": False,
        "expanded_holdout_cases_generated": 0,
        "expanded_holdout_cases_opened": 0,
        "canonical_build_status": "PASS",
        "canonical_build_archive_relative": receipt["archive_relative"],
        "canonical_build_archive_sha256": receipt["archive_sha256"],
        "canonical_build_archive_bytes": receipt["archive_bytes"],
        "canonical_build_archive_opened": False,
        "canonical_build_receipt_relative": relative,
        "canonical_build_receipt_sha256": receipt_hash,
        "canonical_build_receipt_bytes": observed.st_size,
        "canonical_build_receipt_device": observed.st_dev,
        "canonical_build_receipt_inode": observed.st_ino,
        "root": captured["root"],
        "actual_compiler_process_count": 28,
        "expected_compiler_process_count": 28,
        "actual_source_phase_count": 2,
        "bridge_overlay_apply_count": 2,
        "adapter_overlay_apply_count": 2,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "native_libraries_loaded": 0,
        "canonical_sources_modified": False,
        "tmp_directory_scanned": False,
        "historical_archives_opened": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    payload = canonical(base, record)
    require(0 < len(payload) <= MAX_OWNER_BYTES,
            "bound the complete actual V21 root receipt")
    target = module.ROOT / EVIDENCE_PATH / root_receipt_name(BUILD_LABEL)
    published = kernel.write_fresh(target, payload, synchronize=True)
    directory = kernel.fsync_directory(module.ROOT / EVIDENCE_PATH)
    require(published.get("sha256") == digest(payload)
            and published.get("bytes") == len(payload)
            and published.get("exclusive_creation") is True
            and published.get("file_fsync_completed") is True
            and directory.get("completed") is True,
            "publish exactly one new no-follow fsynced first-party root receipt")
    return {
        **result,
        "root_provenance_status": "PASS",
        "root_provenance_receipt_relative":
            EVIDENCE_PATH + "/" + root_receipt_name(BUILD_LABEL),
        "root_provenance_receipt_sha256": published["sha256"],
        "root_provenance_receipt_bytes": published["bytes"],
        "root_provenance_receipt_device": published["device"],
        "root_provenance_receipt_inode": published["inode"],
        "root_provenance_directory_fsync": directory,
        "actual_compiler_process_count": 28,
        "actual_private_phase_count": 2,
        "captured_findall_variant_sha256": CAPTURE_VARIANT[2],
        "captured_findall_variant_bytes": CAPTURE_VARIANT[3],
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
    }


def run_build(
    v20: dict[str, object], v19: dict[str, object], base: dict[str, object],
    options: dict[str, object],
) -> dict[str, object]:
    global _ROOT_CAPTURE
    require(options.get("mode") == "--build"
            and options.get("label") == BUILD_LABEL
            and _ROOT_CAPTURE is None and base.get("_WALL_ENABLED") is False,
            "require one explicitly authorized future captured-source native build")
    base["verify_future_phase_one_v4"](options)
    context, state = collect_context(
        v20, v19, base, options["source_sha256"], options["protocol_sha256"],
        options["contract_sha256"],
    )
    previous = state["v18_state"]
    raw = previous["owners"]["v16_builder"]
    owner = base["OWNER_BY_NAME"]["v16_builder"]
    require(type(raw) is bytes and digest(raw) == owner[2],
            "execute only the independently audited first-party V16 compiler kernel")
    import types

    name = "_rebar_v21_explicit_owned_rust_captured_v16_kernel"
    require(name not in sys.modules,
            "reject shared or foreign cumulative first-party build authority")
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + owner[1]
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True),
             module.__dict__)
        require(module.SCHEMA == "rebar-phase2-owned-rust-buffer-shape-source-build-v16"
                and module.VERSION == 16
                and module.FAMILY == FAMILY and module.PHASES == PHASES
                and module.PROCESS_NAMES == PROCESS_NAMES
                and module.ROOT_PREFIX == ROOT_PREFIX,
                "retain exact first-party compiler kernel and all real process roles")
        module.SCHEMA = SCHEMA
        module.VERSION = VERSION
        module.SOURCE_PATH = SOURCE_PATH
        module.PROTOCOL_PATH = PROTOCOL_PATH
        module.CONTRACT_PATH = CONTRACT_PATH
        module.FINAL_GRAPH_VERSION = GRAPH_VERSION
        module.CURRENT_EVIDENCE_OWNER_LOWER_BOUND = EVIDENCE_FLOOR
        module.CURRENT_HISTORY_REFERENCE_LOWER_BOUND = HISTORY_FLOOR
        module.COMBINED_VARIANT = module.Owner(
            CAPTURE_VARIANT[1], CAPTURE_VARIANT[2], CAPTURE_VARIANT[3],
        )
        module.BUFFER_VARIANT = module.COMBINED_VARIANT
        module.BUFFER_FEATURE = tuple(
            module.Owner(base["OWNER_BY_NAME"][role][1],
                         base["OWNER_BY_NAME"][role][2],
                         base["OWNER_BY_NAME"][role][3])
            for role in ("v2_repair", "v2_protocol", "v2_contract")
        )
        module.FINAL_GRAPH = tuple(
            module.Owner(row[1], row[2], row[3])
            for row in v20["GRAPH"].values()
        )

        def verified_context(
            source_pin: str, protocol_pin: str, contract_pin: str,
        ) -> tuple[dict[str, object], dict[str, object]]:
            require((source_pin, protocol_pin, contract_pin)
                    == (options["source_sha256"], options["protocol_sha256"],
                        options["contract_sha256"]),
                    "reject a substituted V21 cumulative build authority")
            runtime = {
                "originals": previous["originals"],
                "combined_bridge": state["captured_bytes"],
                "corrected_adapter": previous["corrected_adapter"],
                "low_level_v9_source": previous["low_level_v9_source"],
            }
            state["runtime_state"] = runtime
            return context, runtime

        original_verifier = module.verify_reproduced_phases

        def verify_actual_phases(
            low_level: object, kernel: object, workdir: str,
            phases: list[object], steps: list[object],
        ) -> dict[str, object]:
            global _ROOT_CAPTURE
            require(_ROOT_CAPTURE is None
                    and type(steps) is list and len(steps) == 28,
                    "require one complete actual 28-process captured build")
            process_ids: set[int] = set()
            for index, step in enumerate(steps):
                phase = PHASES[index // len(PROCESS_NAMES)]
                require(type(step) is dict
                        and step.get("name")
                            == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                        and ("phase" not in step or step.get("phase") == phase)
                        and type(step.get("pid")) is int and step["pid"] > 0
                        and step["pid"] not in process_ids
                        and step.get("exit_status") == 0
                        and step.get("working_directory")
                            == "<FRESH_PRIVATE_TMP>/" + phase,
                        "reject forged, reordered, missing, or failed actual compiler")
                process_ids.add(step["pid"])
            descriptor, root = v19["capture_root_descriptor"](
                low_level, workdir, phases,
            )
            try:
                proof = original_verifier(
                    low_level, kernel, workdir, phases, steps,
                )
                require(type(proof) is dict and proof.get("status") == "PASS"
                        and proof.get("unique_process_count") == 28
                        and proof.get("combined_bridge_overlay_count") == 2
                        and proof.get("corrected_public_adapter_overlay_count") == 2
                        and proof.get("combined_bridge_sha256") == CAPTURE_VARIANT[2]
                        and proof.get("combined_bridge_bytes") == CAPTURE_VARIANT[3]
                        and proof.get("byte_identical") is True
                        and proof.get("native_libraries_loaded") == 0,
                        "verify complete exact cumulative bridge and owned engine ELF")
                after = os.fstat(descriptor)
                named = os.stat(workdir, follow_symlinks=False)
                require(stat.S_ISDIR(after.st_mode)
                        and stat.S_IMODE(after.st_mode) == 0o700
                        and after.st_uid == os.geteuid()
                        and (after.st_dev, after.st_ino)
                            == (root["device"], root["inode"])
                        and (named.st_dev, named.st_ino)
                            == (root["device"], root["inode"]),
                        "reject a swapped genuine cumulative-build root")
                _ROOT_CAPTURE = {
                    "root": root,
                    "phase_count": 2,
                    "unique_process_count": len(process_ids),
                    "original_reproducibility": "PASS",
                    "compiler_process_ids": sorted(process_ids),
                }
                return proof
            finally:
                os.close(descriptor)

        module.verify_frozen_context = verified_context
        module.evidence_names = evidence_names
        module.verify_reproduced_phases = verify_actual_phases
        assert_fresh_root_receipt(BUILD_LABEL)

        class Options:
            pass

        forwarded = Options()
        for role in (
            "source_sha256", "protocol_sha256", "contract_sha256",
            "owned_source_sha256", "combined_bridge_sha256",
            "combined_bridge_bytes", "corrected_adapter_sha256",
            "corrected_adapter_bytes", "label",
        ):
            setattr(forwarded, role, options[role])
        outcome = module.run_build(forwarded)
        require(type(outcome) is dict and outcome.get("family") == FAMILY,
                "publish the exact actual first-party cumulative-build outcome")
        if outcome.get("status") != "PASS":
            require(outcome.get("failure_preserved") is True,
                    "preserve failed V21 compilation without inventing root evidence")
            return outcome
        return publish_root_provenance(v20, base, module, state, outcome, options)
    finally:
        sys.modules.pop(name, None)


def entry_boundary() -> dict[str, object]:
    return {
        "actual_candidate_workers": 0,
        "actual_compiler_process_count": 0,
        "actual_reference_workers": 0,
        "archive_opens": 0,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "clock_samples": 0,
        "expanded_holdout_proposal_case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
        "expanded_holdout_proposal_status": "PRE-PHASE-3 PROPOSAL",
        "hidden_cases_read": 0,
        "holdout": "NOT OPENED",
        "memory": "NOT MEASURED",
        "native_libraries_loaded": 0,
        "performance": "NOT MEASURED",
        "previous_holdout_proposal_case_count":
            PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "winner_selected": False,
    }


def main() -> int:
    try:
        verify_runtime()
        parent = bootstrap_v20()
        v19, base = load_base(parent)
        options = parse_cli(parent, base, list(sys.argv[1:]))
        mode = options["mode"]
        if mode != "--build":
            base["install_wall"]()
        if mode == "--render-contract":
            _context, state = collect_context(
                parent, v19, base, options["source_sha256"],
                options["protocol_sha256"],
            )
            result = contract_document(
                parent, base, options["source_sha256"],
                options["protocol_sha256"], state,
            )
        elif mode == "--verify-frozen-context":
            result, _state = collect_context(
                parent, v19, base, options["source_sha256"],
                options["protocol_sha256"], options["contract_sha256"],
            )
        elif mode == "--self-test":
            result = self_test(
                parent, v19, base, options["source_sha256"],
                options["protocol_sha256"], options["contract_sha256"],
            )
        else:
            result = run_build(parent, v19, base, options)
        encoded = canonical(base, result)
        require(0 < len(encoded) <= MAX_OWNER_BYTES,
                "bound the complete canonical captured-build result")
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
        return 0 if mode == "--render-contract" or result.get("status") == "PASS" else 1
    except Exception as error:
        result = {
            "schema": SCHEMA + "-entry-failure",
            "status": "FAIL",
            "version": VERSION,
            "family": FAMILY,
            "error_type": type(error).__name__,
            "error_message": str(error)[:8192],
            **entry_boundary(),
        }
        try:
            if "base" in locals():
                sys.stdout.buffer.write(canonical(base, result))
                sys.stdout.buffer.flush()
            else:
                sys.stdout.write(
                    '{"schema":"' + SCHEMA
                    + '-entry-failure","status":"FAIL","error_type":"'
                    + type(error).__name__ + '"}\n'
                )
                sys.stdout.flush()
        except (OSError, ValueError, TypeError):
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
