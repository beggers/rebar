#!/usr/bin/env python3
"""Freeze an owned offline Rust build with recoverable private-root provenance."""

from __future__ import annotations

import sys

if "re" in sys.modules or "_sre" in sys.modules:
    raise SystemExit("a first-party Rust source freeze cannot import a matcher")

import ast
import builtins
import hashlib
import os
import stat


ROOT = "/home/dev-user/src/rebar"
SCHEMA = "rebar-phase2-owned-rust-buffer-shape-source-build-v19"
VERSION = 19
FAMILY = "rust"
SOURCE_PATH = "tools/reproduce_owned_rust_buffer_shape_source_build_v19.py"
PROTOCOL_PATH = "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V19.md"
CONTRACT_PATH = "oracle/phase2/rust-buffer-shape-source-build-v19.json"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
DEVICE = 2064
MAX_OWNER_BYTES = 4 * 1024 * 1024
GRAPH_VERSION = 70
EVIDENCE_FLOOR = 233
HISTORY_FLOOR = 238
ROOT_PREFIX = "rebar-phase2-native-build-v9-rust-"
BUILD_LABEL = "phase2-v19-rust-buffer-shape-root-provenance"
EVIDENCE_PATH = "oracle/phase2/evidence"
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)
V18 = {
    "source": (
        "v18_source", "tools/reproduce_owned_rust_buffer_shape_source_build_v18.py",
        "5a464fbd62ac375d236fa2debce14ae1507ce1bf494efb35695210199bdbef8c",
        128761, DEVICE, 428939,
    ),
    "protocol": (
        "v18_protocol", "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V18.md",
        "52513bb429416e182774558eebf2ae4e1d217e8656da673b9f765d4f3df75991",
        6523, DEVICE, 524727,
    ),
    "contract": (
        "v18_contract", "oracle/phase2/rust-buffer-shape-source-build-v18.json",
        "e57d67e1b16bb13a3555c05c0b6b546b83ab3a6a7e63beec5c81896e01f92301",
        23099, DEVICE, 524728,
    ),
}
GRAPH = {
    "source": (
        "v70_graph_source", "tools/render_candidate_current_overview_v70.py",
        "35495c3f330d9e11e4ee5d9b16dbc057b91c34e22cc6cb7fc340df7894ddc5b7",
        75541, DEVICE, 430956,
    ),
    "inputs": (
        "v70_graph_inputs", "docs/evidence/candidate-current-overview-v70.inputs.json",
        "719520244f366f538a2c3672ca575feebf47dc083028f24e84fbaa7b348913d2",
        1107190, DEVICE, 430957,
    ),
    "summary": (
        "v70_graph_summary", "docs/evidence/candidate-current-overview-v70.json",
        "124cc1583b065aa656ecb9fb0d93aa8beecfebf4998a2f58fb619dd7d609702c",
        3097493, DEVICE, 430958,
    ),
    "svg": (
        "v70_graph_svg", "docs/evidence/candidate-current-overview-v70.svg",
        "bb2ea5e22cd40f5ae767829f47c4bfcb4793e91126626d40507ba1887573670c",
        6992, DEVICE, 430966,
    ),
}
V11 = {
    "source": (
        "v11_campaign_source", "tools/run_owned_repaired_rust_original_campaign_v11.py",
        "27bf88358d5a45a5b487680e70f5fa5b5192a05f053f33f6ddb651c972c94f2d",
        310760, DEVICE, 430525,
    ),
    "protocol": (
        "v11_campaign_protocol", "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V11.md",
        "a3a5b35701aa6b149ff0b4fbebb9f6722dd08436d2f7e4f600f3db12c8c6ac2b",
        7353, DEVICE, 524748,
    ),
    "contract": (
        "v11_campaign_contract", "oracle/phase2/repaired-rust-original-campaign-v11.json",
        "e6cd2028e36d8ddac0937e6735132bf474327f2ff04855d44e6aa71f5f5c0f96",
        16783, DEVICE, 524749,
    ),
}
V11_ROOT_BLOCK = "BLOCKED PENDING INDEPENDENTLY ATTESTED PRIVATE ROOT"
P0_V4 = {
    "source": (
        "phase1_v4_source", "tools/verify_owned_p0_completeness_v4.py",
        "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
        29094, DEVICE, 428927,
    ),
    "protocol": (
        "phase1_v4_protocol", "oracle/phase1/P0-COMPLETENESS-V4.md",
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        4261, DEVICE, 524712,
    ),
    "contract": (
        "phase1_v4_contract", "oracle/phase1/p0-completeness-v4.json",
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        34875, DEVICE, 524713,
    ),
}
RUST_V18_RECEIPT = (
    "v18_actual_build_receipt",
    "oracle/phase2/evidence/native-source-build-v18-rust-phase2-v18-rust-"
    "buffer-shape-pickle-lifetime-publication-receipt.json",
    "32c422b9624a2565afd8d710700e377aa39aae4aa93d3742da483843869f2104",
    3486, DEVICE, 524747,
)
RUST_V18_ARCHIVE_METADATA = {
    "path": "oracle/phase2/evidence/native-source-build-v18-rust-phase2-"
            "v18-rust-buffer-shape-pickle-lifetime.json.gz",
    "sha256": "f59818e4aaea2999a5fec608d4d8ed761d372e1725548e3c3ff57773d01dffdc",
    "bytes": 109345,
    "device": DEVICE,
    "inode": 524733,
}
C_V16_RECEIPT = (
    "c_v16_actual_build_receipt",
    "oracle/phase2/evidence/native-source-build-v16-c-phase2-v16-c-"
    "subject-buffer-original-p0-publication-receipt.json",
    "16794f5b1487b76a909a176948f4bbac8ed3108768f3127e27c44f9f392ae3d6",
    2671, DEVICE, 524751,
)
C_V16_ARCHIVE_METADATA = {
    "path": "oracle/phase2/evidence/native-source-build-v16-c-phase2-"
            "v16-c-subject-buffer-original-p0.json.gz",
    "sha256": "45cf839dd4fcb7615d70af79bc38b4695911159b109c9a79fd1d7d037b338f55",
    "bytes": 37795,
    "device": DEVICE,
    "inode": 524750,
}
C_V16_SOURCE = {
    "source": (
        "c_v16_source", "tools/reproduce_owned_c_subject_buffer_source_build_v16.py",
        "655b1c72c66fe9bfd06d96c7daeca3d2eb4817a5e28fdbbd737bbfd59713aa90",
        79602, DEVICE, 430076,
    ),
    "protocol": (
        "c_v16_protocol", "oracle/phase2/C-SUBJECT-BUFFER-SOURCE-BUILD-V16.md",
        "19b9ef86be5ce0c77c0addc40cfdefbbfb05102adfdd7baa38b39d62b08497a9",
        4778, DEVICE, 524731,
    ),
    "contract": (
        "c_v16_contract", "oracle/phase2/c-subject-buffer-source-build-v16.json",
        "7ea6bbe9a72a95e905e21cd1c45ac9a5b25620980f40d1ea141163642142a3c7",
        12543, DEVICE, 524732,
    ),
}
QUALIFICATION_BLOCKERS = (
    "ORIGINAL_31237_CANDIDATE_GATE_NOT_PASSED",
    "SUPPLEMENTAL_8244_CANDIDATE_GATE_NOT_RUN",
    "PUBLIC_IMPORT_FAIL",
    "PUBLIC_CALLABLE_SIGNATURE_CANDIDATE_GATE_NOT_RUN",
    "FULL_SIZE_2GIB_CANDIDATE_SEARCH_NOT_RUN",
    "FULL_SIZE_2GIB_CANDIDATE_SUBSTITUTION_NOT_RUN",
    "RUNTIME_NO_DELEGATION_NOT_ESTABLISHED",
)
_ROOT_CAPTURE: dict[str, object] | None = None


class GateError(Exception):
    """Reject stale ownership, unearned root provenance, or real source effects."""


def require(value: object, reason: str) -> None:
    if value is not True:
        raise GateError(reason)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only exact bounded first-party source")
    return hashlib.sha256(raw).hexdigest()


def checked_hash(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
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
            "use only isolated, no-bytecode CPython 3.14.6 without any matcher")


def bootstrap_read(row: tuple[object, ...]) -> bytes:
    name, relative, expected, size, device, inode = row
    require(type(name) is str and type(relative) is str
            and relative == V18["source"][1]
            and not relative.startswith("/") and ".." not in relative.split("/")
            and size == V18["source"][3] and device == DEVICE
            and inode == V18["source"][5],
            "bootstrap only the immutable exact first-party Rust V18 source")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(ROOT + "/" + relative, flags)
    try:
        before = os.fstat(handle)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_nlink == 1 and before.st_uid == os.geteuid()
                and (before.st_dev, before.st_ino, before.st_size)
                == (device, inode, size),
                "reject a changed or nonprivate first-party Rust V18 bootstrap")
        blocks: list[bytes] = []
        remaining = size
        while remaining:
            block = os.read(handle, min(remaining, 262144))
            require(type(block) is bytes and bool(block),
                    "reject truncated first-party Rust V18 source")
            blocks.append(block)
            remaining -= len(block)
        require(os.read(handle, 1) == b"", "reject extra V18 bootstrap bytes")
        after = os.fstat(handle)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns),
                "reject a swapped first-party Rust V18 bootstrap")
    finally:
        os.close(handle)
    raw = b"".join(blocks)
    require(digest(raw) == expected, "reject an incorrect exact V18 source digest")
    return raw


def load_v18() -> dict[str, object]:
    raw = bootstrap_read(V18["source"])
    namespace: dict[str, object] = {
        "__name__": "_rebar_exact_v19_owned_v18_source",
        "__file__": ROOT + "/" + V18["source"][1],
        "__package__": None,
    }
    exec(compile(raw, namespace["__file__"], "exec", dont_inherit=True), namespace)
    require(namespace.get("SCHEMA") == "rebar-phase2-owned-rust-buffer-shape-source-build-v18"
            and namespace.get("VERSION") == 18
            and namespace.get("FAMILY") == FAMILY
            and namespace.get("PYTHON") == PYTHON
            and namespace.get("PYTHON_SHA256") == PYTHON_SHA256
            and namespace.get("ROOT_PREFIX") == ROOT_PREFIX
            and tuple(namespace.get("PHASES", ())) == PHASES
            and tuple(namespace.get("PROCESS_NAMES", ())) == PROCESS_NAMES
            and namespace.get("GRAPH_VERSION") == 65
            and namespace.get("SOURCE_PATH") == V18["source"][1]
            and namespace.get("PROTOCOL_PATH") == V18["protocol"][1]
            and namespace.get("CONTRACT_PATH") == V18["contract"][1]
            and "re" not in sys.modules and "_sre" not in sys.modules,
            "derive only the exact no-matcher authenticated Rust V18 source")
    additions = {ROOT + "/" + SOURCE_PATH,
                 ROOT + "/" + PROTOCOL_PATH,
                 ROOT + "/" + CONTRACT_PATH,
                 ROOT + "/" + RUST_V18_RECEIPT[1],
                 ROOT + "/" + C_V16_RECEIPT[1]}
    for group in (V18, V11, GRAPH, P0_V4, C_V16_SOURCE):
        additions.update(ROOT + "/" + row[1] for row in group.values())
    namespace["_ALLOWLIST"] = frozenset(
        set(namespace["_ALLOWLIST"]) | additions,
    )
    return namespace


def canonical(base: dict[str, object], value: object) -> bytes:
    return (base["canonical"](value) + "\n").encode("ascii")


def row_document(row: tuple[object, ...]) -> dict[str, object]:
    return {"path": row[1], "sha256": row[2], "bytes": row[3],
            "device": row[4], "inode": row[5], "mode": "0600", "nlink": 1}


def public_document(row: tuple[object, ...]) -> dict[str, object]:
    return {"path": row[1], "sha256": row[2], "bytes": row[3]}


def row_group(rows: dict[str, tuple[object, ...]]) -> dict[str, dict[str, object]]:
    return {name: row_document(row) for name, row in sorted(rows.items())}


def document(base: dict[str, object], raw: bytes, label: str) -> dict[str, object]:
    value = base["StrictJSON"](raw).decode()
    require(type(value) is dict and canonical(base, value) == raw,
            "reject a noncanonical, repeated, or malformed owner: " + label)
    return value


def boundary() -> dict[str, object]:
    return {
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_compiler_process_count": 0,
        "actual_root_descriptor_opens": 0,
        "archive_bytes_read": 0,
        "archive_inflations": 0,
        "archive_opens": 0,
        "benchmark_files_read": 0,
        "candidate_build": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_imports": 0,
        "candidate_matching": "NOT RUN",
        "candidate_processes_started": 0,
        "candidate_qualified": False,
        "canonical_source_mutations": 0,
        "clock_samples": 0,
        "compiler_processes_started": 0,
        "confidence_intervals": "NOT MEASURED",
        "hidden_cases_read": 0,
        "holdout": "NOT OPENED",
        "memory": "NOT MEASURED",
        "native_activations": 0,
        "native_libraries_loaded": 0,
        "network_requests": 0,
        "performance": "NOT MEASURED",
        "private_root_path": "NOT MEASURED",
        "private_roots_created": 0,
        "qualified_candidate_count": 0,
        "root_provenance": "NOT MEASURED",
        "root_provenance_receipts_written": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "threads_started": 0,
        "timing_trials_run": 0,
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def validate_actual_build_receipts(base: dict[str, object],
                                   rust: dict[str, object],
                                   c: dict[str, object]) -> None:
    rust_archive = rust.get("archive_publication")
    c_archive = c.get("archive_publication")
    require(rust.get("schema")
            == "rebar-phase2-owned-rust-buffer-shape-source-build-v18-durable-publication-receipt"
            and rust.get("status") == "PASS"
            and rust.get("build_status") == "PASS"
            and rust.get("family") == "rust"
            and rust.get("source_sha256") == V18["source"][2]
            and rust.get("protocol_sha256") == V18["protocol"][2]
            and rust.get("contract_sha256") == V18["contract"][2]
            and rust.get("actual_compiler_process_count") == 28
            and rust.get("expected_actual_compiler_process_count") == 28
            and rust.get("archive_relative") == RUST_V18_ARCHIVE_METADATA["path"]
            and rust.get("archive_sha256") == RUST_V18_ARCHIVE_METADATA["sha256"]
            and rust.get("archive_bytes") == RUST_V18_ARCHIVE_METADATA["bytes"]
            and type(rust_archive) is dict
            and rust_archive.get("device") == RUST_V18_ARCHIVE_METADATA["device"]
            and rust_archive.get("inode") == RUST_V18_ARCHIVE_METADATA["inode"]
            and rust_archive.get("sha256") == RUST_V18_ARCHIVE_METADATA["sha256"]
            and rust.get("candidate_matching") == "NOT RUN"
            and rust.get("candidate_qualified") is False
            and rust.get("candidate_workers_started") == 0
            and rust.get("holdout") == "NOT OPENED",
            "preserve the genuine previous Rust V18 build without opening its archive")
    require(c.get("schema")
            == "rebar-phase2-owned-c-subject-buffer-source-build-v16-durable-publication-receipt"
            and c.get("status") == "PASS"
            and c.get("build_status") == "PASS"
            and c.get("family") == "c"
            and c.get("source_sha256") == C_V16_SOURCE["source"][2]
            and c.get("protocol_sha256") == C_V16_SOURCE["protocol"][2]
            and c.get("contract_sha256") == C_V16_SOURCE["contract"][2]
            and c.get("actual_compiler_process_count") == 14
            and c.get("expected_compiler_process_count") == 14
            and c.get("archive_relative") == C_V16_ARCHIVE_METADATA["path"]
            and c.get("archive_sha256") == C_V16_ARCHIVE_METADATA["sha256"]
            and c.get("archive_bytes") == C_V16_ARCHIVE_METADATA["bytes"]
            and type(c_archive) is dict
            and c_archive.get("device") == C_V16_ARCHIVE_METADATA["device"]
            and c_archive.get("inode") == C_V16_ARCHIVE_METADATA["inode"]
            and c_archive.get("sha256") == C_V16_ARCHIVE_METADATA["sha256"]
            and c.get("candidate_correctness") == "NOT MEASURED"
            and c.get("candidate_processes_started") == 0
            and c.get("holdout") == "NOT OPENED",
            "preserve the genuine C V16 build without opening its sealed archive")


def validate_graph(summary: dict[str, object],
                   inputs: dict[str, object]) -> dict[str, object]:
    require(summary.get("schema")
            == "rebar-candidate-current-overview-v" + str(GRAPH_VERSION) + "-summary"
            and summary.get("version") == GRAPH_VERSION
            and summary.get("status") == "PASS"
            and inputs.get("schema")
            == "rebar-candidate-current-overview-v" + str(GRAPH_VERSION) + "-inputs"
            and inputs.get("version") == GRAPH_VERSION
            and summary.get("source") == public_document(GRAPH["source"])
            and summary.get("inputs") == public_document(GRAPH["inputs"])
            and summary.get("svg") == public_document(GRAPH["svg"]),
            "bind all four genuinely published current Rust V19 graph owners")
    for observed in (summary, inputs):
        require(observed.get("actual_current_graph_predecessor_version") == 69
                and observed.get("authenticated_evidence_owner_lower_bound")
                    == EVIDENCE_FLOOR
                and observed.get("authenticated_history_reference_lower_bound")
                    == HISTORY_FLOOR
                and observed.get("full_case_denominator") == 31237
                and observed.get("suite_count") == 13
                and observed.get("private_waiver_count") == 13
                and observed.get("phase1_v4_oracle_readiness_status") == "PASS"
                and observed.get("candidate_qualification_status") == "BLOCKED"
                and observed.get("qualified_candidate_count") == 0
                and observed.get("actual_rust_v10_candidate_status") == "FAIL"
                and observed.get("actual_rust_semantic_mismatch_count") == 1440
                and observed.get("actual_rust_verified_passing_case_count") == 14853
                and observed.get("rust_native_build_v17_authorization_status") == "BLOCKED"
                and observed.get("rust_native_build_v17_status") == "NOT RUN"
                and observed.get("rust_native_build_v18_status") == "PASS"
                and observed.get("rust_native_build_v18_compiler_process_count") == 28
                and observed.get("rust_native_build_v18_matching_status") == "NOT RUN"
                and observed.get("rust_native_build_v18_archive_opened_by_graph") is False
                and observed.get("c_native_build_v16_status") == "PASS"
                and observed.get("c_native_build_v16_compiler_process_count") == 14
                and observed.get("c_native_build_v16_matching_status") == "NOT RUN"
                and observed.get("c_native_build_v16_archive_opened_by_graph") is False
                and observed.get("actual_c_semantic_mismatch_count") == 1230
                and observed.get("actual_c_verified_passing_case_count") == 7325
                and observed.get("rust_v11_original_campaign_source_status")
                    == "SOURCE FROZEN"
                and observed.get("rust_v11_original_campaign_frozen_graph_version") == 69
                and observed.get(
                    "rust_v11_original_campaign_frozen_graph_evidence_owner_lower_bound"
                ) == 230
                and observed.get(
                    "rust_v11_original_campaign_frozen_graph_history_reference_lower_bound"
                ) == 235
                and observed.get("rust_v11_original_campaign_independent_source_owner_count")
                    == 3
                and observed.get("rust_v11_original_campaign_execution_status")
                    == V11_ROOT_BLOCK
                and observed.get("rust_v11_original_campaign_build_inspection_status")
                    == V11_ROOT_BLOCK
                and observed.get("rust_v11_original_campaign_matching_status")
                    == "NOT RUN"
                and observed.get("rust_v11_original_campaign_private_root")
                    == "NOT MEASURED"
                and observed.get("rust_v11_original_campaign_private_root_provenance")
                    == "NOT ESTABLISHED"
                and observed.get("rust_v11_original_campaign_native_artifact_hashes")
                    == "NOT MEASURED"
                and observed.get("rust_v11_original_campaign_actual_worker_count") == 0
                and observed.get("rust_v11_original_campaign_actual_archive_reads") == 0
                and observed.get("rust_v11_original_campaign_actual_archive_inflations") == 0
                and observed.get("rust_v11_original_campaign_actual_native_activations") == 0
                and observed.get("rust_v11_original_campaign_candidate_correctness")
                    == "NOT MEASURED"
                and observed.get("rust_v11_original_campaign_candidate_qualified") is False
                and observed.get("final_holdout_opened") is False
                and observed.get("runtime_no_delegation") == "NOT ESTABLISHED"
                and observed.get("performance") == "NOT MEASURED",
                "preserve all genuine source builds, losses, blockers and sealed holdout")
    require(summary.get("candidate_qualification_blockers")
            == list(QUALIFICATION_BLOCKERS),
            "retain all seven actual Phase 2 compatibility blockers")
    campaign = summary.get("rust_v11_original_campaign_source_freeze")
    require(type(campaign) is dict
            and campaign.get("schema")
                == "rebar-candidate-current-overview-v70-first-party-rust-original-campaign-v11"
            and campaign.get("status") == "SOURCE FROZEN"
            and campaign.get("version") == 11
            and campaign.get("frozen_graph_version") == 69
            and campaign.get("independent_feature_source_owner_count") == 3
            and campaign.get("build_inspection_status") == V11_ROOT_BLOCK
            and campaign.get("candidate_execution_status") == V11_ROOT_BLOCK
            and campaign.get("candidate_matching_status") == "NOT RUN"
            and campaign.get("private_native_root") == "NOT MEASURED"
            and campaign.get("private_native_root_provenance") == "NOT ESTABLISHED"
            and campaign.get("native_artifact_hashes") == "NOT MEASURED",
            "preserve the actual current root-blocked independently owned V11 campaign")
    campaign_owners = campaign.get("owners")
    require(type(campaign_owners) is dict
            and set(campaign_owners) == {"source", "protocol", "contract"},
            "bind exactly the three genuinely published Rust V11 campaign owners")
    for role, row in V11.items():
        item = campaign_owners[role]
        require(type(item) is dict
                and item.get("path") == row[1]
                and item.get("sha256") == row[2]
                and item.get("bytes") == row[3]
                and item.get("device") == row[4]
                and item.get("inode") == row[5]
                and item.get("mode") == "0600"
                and item.get("nlink") == 1
                and item.get("uid") == os.geteuid(),
                "reject a substituted published Rust V11 source owner: " + role)
    effects = campaign.get("source_only_effects")
    require(type(effects) is dict
            and effects.get("actual_candidate_workers") == 0
            and effects.get("actual_reference_workers") == 0
            and effects.get("actual_compiler_processes") == 0
            and effects.get("actual_native_activations") == 0
            and effects.get("historical_build_archive_reads") == 0
            and effects.get("v18_build_archive_reads") == 0
            and effects.get("private_build_root_enumerations") == 0
            and effects.get("private_build_root_reads") == 0
            and effects.get("build_private_root") == "NOT MEASURED"
            and effects.get("native_artifact_hashes") == "NOT MEASURED"
            and effects.get("candidate_matching") == "NOT RUN"
            and effects.get("candidate_qualified") is False
            and effects.get("holdout") == "NOT OPENED",
            "retain the complete real V11 private-root and no-execution blocker")
    return {
        "version": GRAPH_VERSION,
        "owner_count": 4,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "phase1_v4_readiness": "PASS",
        "candidate_qualification": "BLOCKED",
        "current_rust_candidate_status": "FAIL",
        "current_rust_semantic_mismatch_count": 1440,
        "current_rust_verified_passing_case_count": 14853,
        "rust_v18_native_build_status": "PASS",
        "rust_v18_actual_compiler_process_count": 28,
        "rust_v18_matching": "NOT RUN",
        "rust_v18_private_root": "NOT MEASURED",
        "c_v16_native_build_status": "PASS",
        "c_v16_actual_compiler_process_count": 14,
        "c_v16_matching": "NOT RUN",
        "current_c_candidate_status": "FAIL",
        "current_c_semantic_mismatch_count": 1230,
        "current_c_verified_passing_case_count": 7325,
        "published_rust_v11_campaign_status": "SOURCE FROZEN",
        "published_rust_v11_campaign_graph_version": 69,
        "published_rust_v11_campaign_source_owner_count": 3,
        "published_rust_v11_build_inspection_status": V11_ROOT_BLOCK,
        "published_rust_v11_candidate_execution_status": V11_ROOT_BLOCK,
        "published_rust_v11_candidate_matching": "NOT RUN",
        "published_rust_v11_private_root": "NOT MEASURED",
        "published_rust_v11_private_root_provenance": "NOT ESTABLISHED",
        "historical_rust_v17_authorization": "BLOCKED",
        "holdout": "NOT OPENED",
    }


def validate_v18_contract(base: dict[str, object],
                          value: dict[str, object]) -> None:
    source = value.get("source")
    protocol = value.get("protocol")
    package = value.get("first_party_rust_source_family")
    build = value.get("future_offline_native_build")
    require(value.get("schema")
            == "rebar-phase2-owned-rust-buffer-shape-source-build-v18-source-freeze"
            and value.get("version") == 18 and value.get("family") == FAMILY
            and type(source) is dict
            and source.get("sha256") == V18["source"][2]
            and type(protocol) is dict
            and protocol.get("sha256") == V18["protocol"][2]
            and type(package) is dict
            and package.get("canonical_source_owner_count") == 9
            and package.get("private_overlay_count_per_phase") == 2
            and package.get("cargo_package_count") == 1
            and package.get("external_cargo_dependency_count") == 0
            and type(build) is dict
            and build.get("mandatory_low_level_root_prefix") == ROOT_PREFIX
            and build.get("independent_phase_count") == 2
            and build.get("compiler_process_count_per_phase") == 14
            and build.get("expected_actual_compiler_process_count") == 28
            and build.get("cargo_flags")
                == ["--release", "--locked", "--offline", "--frozen"],
            "retain the exact nine-source zero-dependency offline Rust V18 closure")


def validate_v11_contract(value: dict[str, object]) -> None:
    source = value.get("source")
    protocol = value.get("protocol")
    graph = value.get("current_pushed_graph")
    rust = value.get("actual_first_party_v18_build")
    inspection = value.get("future_authorized_build_inspection")
    effects = value.get("source_only_effects")
    phase_one = value.get("phase1_v4_readiness")
    require(value.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v11-recoverable-source-freeze"
            and value.get("status")
                == "SOURCE FROZEN; ACTUAL V18 RUST CANDIDATE NOT RUN"
            and value.get("version") == 11
            and value.get("phase") == "CANDIDATES"
            and value.get("family") == FAMILY
            and type(source) is dict and source.get("path") == V11["source"][1]
            and source.get("sha256") == V11["source"][2]
            and type(protocol) is dict
            and protocol.get("path") == V11["protocol"][1]
            and protocol.get("sha256") == V11["protocol"][2]
            and type(graph) is dict
            and graph.get("version") == 69
            and graph.get("authenticated_evidence_owner_lower_bound") == 230
            and graph.get("authenticated_history_reference_lower_bound") == 235
            and graph.get("resulting_evidence_owner_lower_bound") == EVIDENCE_FLOOR
            and graph.get("resulting_history_reference_lower_bound") == HISTORY_FLOOR
            and graph.get("new_source_owner_count") == 3
            and type(phase_one) is dict and phase_one.get("status") == "PASS"
            and phase_one.get("qualified_candidate_count") == 0,
            "authenticate the complete published V11 source and exact predecessor")
    require(type(rust) is dict
            and rust.get("actual_compiler_process_count") == 28
            and rust.get("private_build_root") == "NOT MEASURED"
            and rust.get("independent_private_root_provenance") == "NOT ESTABLISHED"
            and rust.get("individual_native_elf_hashes") == "NOT MEASURED"
            and rust.get("private_root_disclosed_by_public_receipt") is False
            and rust.get("private_root_recoverable_from_sanitized_build_report") is False
            and rust.get("source_freeze_loads_native") is False
            and rust.get("source_freeze_opens_archive") is False,
            "never invent previous Rust V18 private-root or native provenance")
    require(type(inspection) is dict
            and inspection.get("existing_v18_inspection_status") == V11_ROOT_BLOCK
            and inspection.get("private_root_provenance") == "NOT ESTABLISHED"
            and inspection.get("fresh_provenance_build_required_without_independent_root")
                is True
            and inspection.get("guess_private_root") == "FORBIDDEN"
            and inspection.get("scan_tmp") == "FORBIDDEN"
            and inspection.get("candidate_matching") == "NOT RUN"
            and inspection.get("candidate_workers_started") == 0
            and inspection.get("actual_compressed_archive_reads") == 0,
            "preserve the actual fail-closed V11 root-provenance blocker")
    require(type(effects) is dict
            and effects.get("actual_candidate_workers") == 0
            and effects.get("actual_reference_workers") == 0
            and effects.get("actual_compiler_processes") == 0
            and effects.get("actual_native_activations") == 0
            and effects.get("historical_build_archive_reads") == 0
            and effects.get("v18_build_archive_reads") == 0
            and effects.get("private_build_root_enumerations") == 0
            and effects.get("private_build_root_reads") == 0
            and effects.get("build_private_root") == "NOT MEASURED"
            and effects.get("native_artifact_hashes") == "NOT MEASURED"
            and effects.get("candidate_matching") == "NOT RUN"
            and effects.get("candidate_qualified") is False
            and effects.get("holdout") == "NOT OPENED",
            "require the actual published V11 no-archive no-root source boundary")


def collect_context(base: dict[str, object], source_pin: str,
                    protocol_pin: str,
                    contract_pin: str | None = None
                    ) -> tuple[dict[str, object], dict[str, object]]:
    checked_hash(source_pin, "Rust V19 source")
    checked_hash(protocol_pin, "Rust V19 protocol")
    source_raw, source_info = base["read_self"](SOURCE_PATH, source_pin)
    protocol_raw, protocol_info = base["read_self"](PROTOCOL_PATH, protocol_pin)
    require(source_raw.endswith(b"\n") and not source_raw.endswith(b"\n\n")
            and protocol_raw.endswith(b"\n") and not protocol_raw.endswith(b"\n\n"),
            "require exactly one final source and protocol newline")
    v18_context, v18_state = base["collect_context"](
        V18["source"][2], V18["protocol"][2], V18["contract"][2],
    )
    v18_contract = document(base, base["read_exact"](V18["contract"]),
                            "immutable Rust V18 contract")
    validate_v18_contract(base, v18_contract)
    raw_graph = {role: base["read_exact"](row) for role, row in GRAPH.items()}
    summary = document(base, raw_graph["summary"], "current V70 summary")
    inputs = document(base, raw_graph["inputs"], "current V70 inputs")
    require(b"<svg" in raw_graph["svg"] and b"</svg>" in raw_graph["svg"],
            "authenticate the complete genuine current V70 overview chart")
    observation = validate_graph(summary, inputs)
    v11_contract = document(base, base["read_exact"](V11["contract"]),
                            "published root-blocked Rust V11 machine contract")
    for role in ("source", "protocol"):
        base["read_exact"](V11[role])
    validate_v11_contract(v11_contract)
    rust_receipt = document(base, base["read_exact"](RUST_V18_RECEIPT),
                            "small actual Rust V18 build receipt")
    c_receipt = document(base, base["read_exact"](C_V16_RECEIPT),
                         "small actual first-party C V16 build receipt")
    validate_actual_build_receipts(base, rust_receipt, c_receipt)
    c_contract = document(base, base["read_exact"](C_V16_SOURCE["contract"]),
                          "published first-party C V16 source freeze")
    for role in ("source", "protocol"):
        base["read_exact"](C_V16_SOURCE[role])
    require(c_contract.get("schema")
            == "rebar-phase2-owned-c-subject-buffer-source-build-v16-source-freeze"
            and c_contract.get("version") == 16
            and c_contract.get("family") == "c"
            and c_contract.get("corrected_p0_v4", {}).get("python_reference_readiness")
                == "PASS",
            "retain the distinct independently frozen first-party C family")
    phase_one = v18_state.get("phase1_v4")
    owners = v18_state.get("originals")
    require(type(phase_one) is dict
            and phase_one.get("phase_gate", {}).get("status") == "PASS"
            and phase_one.get("candidate_qualification_gate", {}).get("status")
                == "BLOCKED"
            and type(owners) is dict and len(owners) == 9
            and type(v18_context) is dict and v18_context.get("status") == "PASS"
            and v18_context.get("future_total_compiler_process_count") == 28
            and v18_state.get("combined_bridge") is not None
            and v18_state.get("corrected_adapter") is not None,
            "authenticate actual passing P0 V4 and all nine owned Rust originals")
    own_context = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "version": VERSION,
        "status": "PASS",
        "family": FAMILY,
        "source": source_info,
        "protocol": protocol_info,
        "authenticated_current_graph_version": GRAPH_VERSION,
        "authenticated_graph_owner_count": 4,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "historical_rust_v18_native_build": "PASS",
        "historical_rust_v18_compiler_process_count": 28,
        "historical_rust_v18_root_provenance": "NOT MEASURED",
        "published_rust_v11_campaign_status": "SOURCE FROZEN",
        "published_rust_v11_source_owner_count": 3,
        "published_rust_v11_frozen_graph_version": 69,
        "published_rust_v11_build_inspection_status": V11_ROOT_BLOCK,
        "published_rust_v11_candidate_execution_status": V11_ROOT_BLOCK,
        "published_rust_v11_matching_status": "NOT RUN",
        "published_rust_v11_private_root": "NOT MEASURED",
        "published_rust_v11_private_root_provenance": "NOT ESTABLISHED",
        "published_rust_v11_native_artifact_hashes": "NOT MEASURED",
        "current_rust_candidate_status": "FAIL",
        "current_rust_semantic_mismatch_count": 1440,
        "current_rust_verified_passing_case_count": 14853,
        "current_c_candidate_status": "FAIL",
        "current_c_semantic_mismatch_count": 1230,
        "current_c_verified_passing_case_count": 7325,
        "historical_c_v16_native_build": "PASS",
        "historical_c_v16_compiler_process_count": 14,
        "first_party_rust_source_owner_count": 9,
        "phase1_v4_readiness": "PASS",
        "candidate_qualification": "BLOCKED",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "supplemental_reference_cases_per_worker": 8244,
        "future_phase_count": 2,
        "future_compiler_process_count_per_phase": 14,
        "future_total_compiler_process_count": 28,
        **boundary(),
    }
    state: dict[str, object] = {
        "source_info": source_info,
        "protocol_info": protocol_info,
        "v18_context": v18_context,
        "v18_state": v18_state,
        "v18_contract": v18_contract,
        "v11_contract": v11_contract,
        "graph": observation,
        "summary": summary,
        "inputs": inputs,
        "rust_v18_receipt": rust_receipt,
        "c_v16_receipt": c_receipt,
        "c_v16_contract": c_contract,
    }
    expected = contract_document(base, source_pin, protocol_pin, state)
    if contract_pin is not None:
        checked_hash(contract_pin, "Rust V19 canonical contract")
        raw, contract_info = base["read_self"](CONTRACT_PATH, contract_pin)
        require(raw == canonical(base, expected)
                and document(base, raw, "complete Rust V19 machine contract") == expected,
                "reject stale or noncanonical Rust V19 root-provenance contract")
        own_context["contract"] = contract_info
    base["no_matching_imports"]()
    return own_context, state


def contract_document(base: dict[str, object], source_pin: str,
                      protocol_pin: str,
                      state: dict[str, object]) -> dict[str, object]:
    checked_hash(source_pin, "Rust V19 source")
    checked_hash(protocol_pin, "Rust V19 protocol")
    original_rows = base["OWNER_BY_NAME"]
    original_names = base["RUST_SOURCE_NAMES"]
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "phase": "SOURCE FREEZE; OFFLINE RUST ROOT PROVENANCE NOT BUILT OR RUN",
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
            "owners": row_group(GRAPH),
            "owner_count": 4,
            "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
            "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
            "lower_bounds_are_not_a_global_census": True,
        },
        "phase1_v4_readiness": {
            "owners": row_group(P0_V4),
            "status": "PASS",
            "status_scope": "PHASE 1 PYTHON-ORACLE READINESS ONLY",
            "candidate_qualification_status": "BLOCKED",
            "qualification_blockers": list(QUALIFICATION_BLOCKERS),
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "named_private_waiver_count": 13,
            "supplemental_reference_worker_count": 2,
            "supplemental_case_count_per_reference": 8244,
            "supplemental_added_to_original_denominator": False,
        },
        "immutable_first_party_v18": {
            "owners": row_group(V18),
            "version": 18,
            "source_modified": False,
            "original_callback_replaced": False,
            "existing_private_build_root": "NOT MEASURED",
            "existing_private_root_scanned": False,
            "previous_build_receipt": row_document(RUST_V18_RECEIPT),
            "previous_build_status": "PASS",
            "previous_actual_compiler_process_count": 28,
            "previous_archive_metadata_attested_by_receipt": {
                **RUST_V18_ARCHIVE_METADATA,
                "archive_opened": False,
                "archive_hash_recomputed": False,
                "archive_bytes_read": 0,
            },
            "previous_candidate_matching": "NOT RUN",
        },
        "published_root_blocked_rust_v11_original_campaign": {
            "owners": row_group(V11),
            "version": 11,
            "status": "SOURCE FROZEN",
            "frozen_graph_version": 69,
            "frozen_evidence_owner_lower_bound": 230,
            "frozen_history_reference_lower_bound": 235,
            "independent_source_owner_count": 3,
            "build_inspection_status": V11_ROOT_BLOCK,
            "candidate_execution_status": V11_ROOT_BLOCK,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
            "candidate_workers_started": 0,
            "previous_private_root": "NOT MEASURED",
            "previous_private_root_provenance": "NOT ESTABLISHED",
            "previous_native_artifact_hashes": "NOT MEASURED",
            "previous_build_archive_opened": False,
            "previous_private_root_scanned": False,
            "fresh_root_provenance_build_required": True,
            "holdout": "NOT OPENED",
        },
        "current_rust_candidate": {
            "status": "FAIL",
            "semantic_mismatch_count": 1440,
            "explicitly_verified_passing_case_count": 14853,
            "actual_candidate_worker_count": 13,
            "original_case_execution_denominator": 31237,
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "preserved_independent_c_family": {
            "source_owners": row_group(C_V16_SOURCE),
            "build_receipt": row_document(C_V16_RECEIPT),
            "actual_build_status": "PASS",
            "actual_compiler_process_count": 14,
            "archive_metadata_attested_by_receipt": {
                **C_V16_ARCHIVE_METADATA,
                "archive_opened": False,
                "archive_hash_recomputed": False,
                "archive_bytes_read": 0,
            },
            "previous_matching_status": "FAIL",
            "semantic_mismatch_count": 1230,
            "explicitly_verified_passing_case_count": 7325,
            "new_candidate_matching": "NOT RUN",
            "source_parser_compiler_executor_or_engine_reused": False,
        },
        "owned_rust_source_family": {
            "canonical_source_owners": [
                row_document(original_rows[name]) for name in original_names
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
        "authenticated_first_party_build_kernel": {
            "v18_source": row_document(V18["source"]),
            "v16": [
                row_document(original_rows[name])
                for name in ("v16_builder", "v16_protocol", "v16_contract")
            ],
            "v9": [
                row_document(original_rows[name])
                for name in ("low_level_v9", "low_level_v9_protocol",
                             "low_level_v9_contract")
            ],
            "v7": [
                row_document(original_rows[name])
                for name in ("low_level_v7", "low_level_v7_protocol",
                             "low_level_v7_contract")
            ],
            "build_kernel_run_during_source_freeze": False,
        },
        "future_offline_root_provenance_build": {
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
            "private_bridge_overlays": 2,
            "private_adapter_overlays": 2,
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
        "source_only_effects": boundary(),
    }


def synthetic_root_plan(base: dict[str, object]) -> dict[str, object]:
    phases: list[dict[str, object]] = []
    for index, phase in enumerate(PHASES):
        outputs: dict[str, dict[str, object]] = {}
        for role_index, role in enumerate(("engine", "bridge")):
            outputs[role] = {
                "role": role,
                "file_name": ("_rust_engine.so" if role == "engine"
                              else "_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
                "sha256": format(index * 2 + role_index + 1, "064x"),
                "bytes": 1000 + role_index,
                "device": DEVICE,
                "inode": 9000 + index * 2 + role_index,
                "mode": "0755",
                "evidence_kind": "SYNTHETIC CONTROL; NOT A REAL NATIVE",
            }
        phases.append({
            "name": phase, "device": DEVICE, "inode": 8000 + index,
            "mode": "0700",
            "evidence_kind": "SYNTHETIC CONTROL; NOT A REAL PHASE",
            "native_outputs": outputs,
        })
    processes = [{
        "phase": PHASES[index // len(PROCESS_NAMES)],
        "name": PROCESS_NAMES[index % len(PROCESS_NAMES)],
        "pid": 10000 + index,
        "exit_status": 0,
        "working_directory": "<FRESH_PRIVATE_TMP>/"
            + PHASES[index // len(PROCESS_NAMES)],
        "evidence_kind": "SYNTHETIC CONTROL; NOT A REAL PROCESS",
    } for index in range(28)]
    return {
        "schema": SCHEMA + "-synthetic-root-control",
        "graph_version": GRAPH_VERSION,
        "root_path": "/tmp/" + ROOT_PREFIX + "SYNTHETIC_CONTROL",
        "root_device": DEVICE,
        "root_inode": 7000,
        "root_uid": 1000,
        "root_mode": "0700",
        "root_evidence_kind": "SYNTHETIC CONTROL; NOT A REAL ROOT",
        "phase_count": 2,
        "expected_process_count": 28,
        "phases": phases,
        "processes": processes,
        "actual_root_descriptor_opens": 0,
        "actual_compiler_process_count": 0,
        "candidate_workers_started": 0,
        "archive_opens": 0,
        "native_libraries_loaded": 0,
        "holdout": "NOT OPENED",
    }


def validate_synthetic_root(plan: object) -> dict[str, object]:
    require(type(plan) is dict
            and plan.get("schema") == SCHEMA + "-synthetic-root-control"
            and plan.get("graph_version") == GRAPH_VERSION
            and plan.get("root_path")
                == "/tmp/" + ROOT_PREFIX + "SYNTHETIC_CONTROL"
            and plan.get("root_device") == DEVICE
            and plan.get("root_inode") == 7000
            and plan.get("root_uid") == 1000
            and plan.get("root_mode") == "0700"
            and plan.get("root_evidence_kind")
                == "SYNTHETIC CONTROL; NOT A REAL ROOT"
            and plan.get("phase_count") == 2
            and plan.get("expected_process_count") == 28
            and plan.get("actual_root_descriptor_opens") == 0
            and plan.get("actual_compiler_process_count") == 0
            and plan.get("candidate_workers_started") == 0
            and plan.get("archive_opens") == 0
            and plan.get("native_libraries_loaded") == 0
            and plan.get("holdout") == "NOT OPENED",
            "reject an invented real root, process, archive, candidate, or effect")
    phases = plan.get("phases")
    processes = plan.get("processes")
    require(type(phases) is list and len(phases) == 2
            and type(processes) is list and len(processes) == 28,
            "require complete distinctly synthetic root controls")
    identities: set[tuple[int, int]] = set()
    for index, phase in enumerate(phases):
        require(type(phase) is dict
                and phase.get("name") == PHASES[index]
                and phase.get("device") == DEVICE
                and phase.get("inode") == 8000 + index
                and phase.get("mode") == "0700"
                and phase.get("evidence_kind")
                    == "SYNTHETIC CONTROL; NOT A REAL PHASE",
                "reject a forged or unsafe private phase control")
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict and set(outputs) == {"engine", "bridge"},
                "preserve both distinct synthetic first-party native roles")
        for role_index, role in enumerate(("engine", "bridge")):
            item = outputs[role]
            pair = (item.get("device"), item.get("inode")) if type(item) is dict else None
            require(type(item) is dict and item.get("role") == role
                    and item.get("file_name")
                    == ("_rust_engine.so" if role == "engine"
                        else "_rust_bridge.cpython-314-x86_64-linux-gnu.so")
                    and item.get("sha256")
                        == format(index * 2 + role_index + 1, "064x")
                    and item.get("bytes") == 1000 + role_index
                    and item.get("device") == DEVICE
                    and item.get("inode") == 9000 + index * 2 + role_index
                    and item.get("mode") == "0755"
                    and item.get("evidence_kind")
                        == "SYNTHETIC CONTROL; NOT A REAL NATIVE"
                    and pair not in identities,
                    "reject an invented, borrowed, or aliased native root artifact")
            assert pair is not None
            identities.add(pair)
    pids: set[int] = set()
    for index, process in enumerate(processes):
        phase = PHASES[index // len(PROCESS_NAMES)]
        require(type(process) is dict
                and process.get("phase") == phase
                and process.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                and process.get("pid") == 10000 + index
                and process["pid"] not in pids
                and process.get("exit_status") == 0
                and process.get("working_directory")
                    == "<FRESH_PRIVATE_TMP>/" + phase
                and process.get("evidence_kind")
                    == "SYNTHETIC CONTROL; NOT A REAL PROCESS",
                "reject omitted, forged, reordered, or real compiler processes")
        pids.add(process["pid"])
    return {"status": "PASS", "synthetic_only": True,
            "synthetic_phase_count": 2,
            "synthetic_native_owner_count": len(identities),
            "synthetic_process_role_count": len(pids),
            "actual_root_descriptor_opens": 0,
            "actual_compiler_process_count": 0}


def self_test(base: dict[str, object], source_pin: str,
              protocol_pin: str,
              contract_pin: str) -> dict[str, object]:
    context, state = collect_context(base, source_pin, protocol_pin, contract_pin)
    accepted = 0
    rejected = 0

    def reject(operation: object, label: str) -> None:
        nonlocal rejected
        try:
            operation()
        except (GateError, Exception):
            rejected += 1
            return
        raise GateError("accepted hostile V19 root-provenance control: " + label)

    plan = synthetic_root_plan(base)
    require(validate_synthetic_root(plan)["synthetic_process_role_count"] == 28,
            "prove all synthetic offline process roles without executing one")
    accepted += 1
    require(state["v18_context"].get("status") == "PASS"
            and state["graph"]["version"] == GRAPH_VERSION,
            "independently derive real V18 and actual V70 without running Rust")
    accepted += 1
    for key, replacement in (
        ("graph_version", 65),
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
        reject(lambda value=changed: validate_synthetic_root(value), key)
    for index in range(2):
        for key, replacement in (
            ("name", "borrowed"), ("inode", 0),
            ("mode", "0755"), ("evidence_kind", "ACTUAL ROOT"),
        ):
            changed = base["clone"](plan)
            changed["phases"][index][key] = replacement
            reject(lambda value=changed: validate_synthetic_root(value), key)
        for role in ("engine", "bridge"):
            for key, replacement in (
                ("sha256", "0" * 64), ("inode", 0),
                ("file_name", "foreign_regex.so"),
                ("mode", "0644"),
                ("evidence_kind", "ACTUAL NATIVE"),
            ):
                changed = base["clone"](plan)
                changed["phases"][index]["native_outputs"][role][key] = replacement
                reject(lambda value=changed: validate_synthetic_root(value),
                       role + ":" + key)
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
            reject(lambda value=changed: validate_synthetic_root(value),
                   "process:" + str(index) + ":" + key)
    probes = (
        ("unlisted-file", lambda: builtins.open("/etc/hosts", "rb")),
        ("tmp-root-scan", lambda: builtins.open("/tmp", "rb")),
        ("native-root-provenance", lambda: sys.audit("open", "/tmp/" + ROOT_PREFIX + "fake", "r", os.O_RDONLY)),
        ("source-mutation", lambda: builtins.open(ROOT + "/" + SOURCE_PATH, "w")),
        ("compressed-archive", lambda: builtins.open(ROOT + "/" + RUST_V18_ARCHIVE_METADATA["path"], "rb")),
        ("c-compressed-archive", lambda: builtins.open(ROOT + "/" + C_V16_ARCHIVE_METADATA["path"], "rb")),
        ("hidden-holdout", lambda: builtins.open(ROOT + "/benchmarks/holdout.json", "rb")),
        ("stdlib-regex", lambda: sys.audit("import", "re", None, None, None, None)),
        ("cpython-matcher", lambda: sys.audit("import", "_sre", None, None, None, None)),
        ("candidate-import", lambda: sys.audit("import", "candidates.rust_candidate", None, None, None, None)),
        ("native-load", lambda: sys.audit("ctypes.dlopen", "foreign.so")),
        ("compiler", lambda: sys.audit("subprocess.Popen", "cargo", (), None, None)),
        ("network", lambda: sys.audit("socket.__new__", None, 2, 1, 0)),
        ("thread", lambda: sys.audit("threading.Thread.start", None)),
        ("clock", lambda: sys.audit("time.perf_counter")),
        ("temporary-root", lambda: sys.audit("tempfile.mkdtemp", "/tmp/forbidden")),
        ("filesystem-rename", lambda: sys.audit("os.rename", "a", "b", -1, -1)),
        ("archive-inflation", lambda: sys.audit("gzip.decompress", b"forbidden")),
        ("foreign-execution", lambda: sys.audit("exec", "forbidden")),
        ("foreign-compilation", lambda: sys.audit("compile", b"forbidden", "foreign.py")),
    )
    for label, operation in probes:
        reject(operation, "physically-block:" + label)
    for category in ("filesystem", "matching_import", "native", "process",
                     "network", "thread", "clock", "temporary", "archive",
                     "dynamic_execution"):
        require(base["_BLOCKED"].get(category, 0) >= 1,
                "physically exercise the real source-only wall: " + category)
    require(rejected >= 190,
            "require the complete root, artifact, compiler, and effect hostile matrix")
    base["no_matching_imports"]()
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS", "version": VERSION, "family": FAMILY,
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_positive_control_count": accepted,
        "rejected_hostile_controls": rejected,
        "blocked_effect_attempts": dict(base["_BLOCKED"]),
        "synthetic_control_proof": validate_synthetic_root(plan),
        "authenticated_current_graph_version": GRAPH_VERSION,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "actual_previous_rust_build_status": "PASS",
        "actual_previous_rust_compiler_process_count": 28,
        "actual_c_build_status": "PASS",
        "actual_c_compiler_process_count": 14,
        "current_rust_semantic_mismatch_count": 1440,
        "current_rust_verified_passing_case_count": 14853,
        "current_c_semantic_mismatch_count": 1230,
        "current_c_verified_passing_case_count": 7325,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "future_total_compiler_process_count": 28,
        **boundary(),
    }


def checked_label(value: object) -> str:
    require(type(value) is str and 0 < len(value) <= 48
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in value),
            "require one safe V16-compatible uniquely owned Rust evidence label")
    return value


def evidence_names(label: str, failed: bool) -> tuple[str, str]:
    require(label == BUILD_LABEL and type(failed) is bool,
            "require a unique first-party Rust V19 build outcome")
    stem = "native-source-build-v19-rust-" + checked_label(label)
    if failed:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def root_receipt_name(label: str) -> str:
    return "native-source-build-v19-rust-" + checked_label(label) \
        + "-root-provenance-receipt.json"


def assert_fresh_root_receipt(label: str) -> None:
    target = ROOT + "/" + EVIDENCE_PATH + "/" + root_receipt_name(label)
    try:
        os.lstat(target)
    except FileNotFoundError:
        return
    raise GateError("reject a pre-existing or borrowed root-provenance receipt")


def capture_root_descriptor(v9: object, workdir: str,
                            phases: list[object]) -> tuple[int, dict[str, object]]:
    v9.checked_workdir(workdir, FAMILY)
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    handle = os.open(workdir, flags)
    try:
        info = os.fstat(handle)
        named = os.stat(workdir, follow_symlinks=False)
        require(stat.S_ISDIR(info.st_mode)
                and stat.S_IMODE(info.st_mode) == 0o700
                and info.st_uid == os.geteuid()
                and (info.st_dev, info.st_ino)
                    == (named.st_dev, named.st_ino)
                and type(phases) is list and len(phases) == 2,
                "capture only the genuine live no-follow owned Rust build root")
        owners: list[dict[str, object]] = []
        for index, phase in enumerate(phases):
            require(type(phase) is dict and phase.get("name") == PHASES[index],
                    "bind only exact independently completed live Rust phases")
            phase_handle = os.open(PHASES[index], flags, dir_fd=handle)
            try:
                phase_info = os.fstat(phase_handle)
                require(stat.S_ISDIR(phase_info.st_mode)
                        and stat.S_IMODE(phase_info.st_mode) == 0o700
                        and phase_info.st_uid == os.geteuid(),
                        "reject borrowed or swapped Rust provenance phases")
                native_handle = os.open("native", flags, dir_fd=phase_handle)
                try:
                    outputs = phase.get("native_outputs")
                    require(type(outputs) is dict
                            and set(outputs) == {"engine", "bridge"},
                            "capture both actual first-party native output roles")
                    native_info = os.fstat(native_handle)
                    require(stat.S_ISDIR(native_info.st_mode)
                            and stat.S_IMODE(native_info.st_mode) == 0o700
                            and native_info.st_uid == os.geteuid(),
                            "capture only the owner-private native directory")
                    artifact_rows: list[dict[str, object]] = []
                    for role, expected_name in (
                        ("engine", "_rust_engine.so"),
                        ("bridge", "_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
                    ):
                        output = outputs[role]
                        require(type(output) is dict
                                and output.get("file_name") == expected_name
                                and type(output.get("sha256")) is str
                                and type(output.get("size_bytes")) is int,
                                "bind exact owned Rust engine and bridge roles")
                        fd = os.open(
                            expected_name,
                            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                            | getattr(os, "O_NOFOLLOW", 0),
                            dir_fd=native_handle,
                        )
                        try:
                            artifact = os.fstat(fd)
                            require(stat.S_ISREG(artifact.st_mode)
                                    and artifact.st_uid == os.geteuid()
                                    and artifact.st_nlink == 1
                                    and (artifact.st_dev, artifact.st_ino,
                                         artifact.st_size)
                                    == (output.get("device"), output.get("inode"),
                                        output.get("size_bytes")),
                                    "bind fresh actual ELF metadata without scanning or loading")
                            artifact_rows.append({
                                "role": role,
                                "file_name": expected_name,
                                "absolute_path": workdir + "/" + PHASES[index]
                                    + "/native/" + expected_name,
                                "sha256": output["sha256"],
                                "bytes": artifact.st_size,
                                "device": artifact.st_dev,
                                "inode": artifact.st_ino,
                                "mode": format(stat.S_IMODE(artifact.st_mode), "04o"),
                                "uid": artifact.st_uid,
                                "nlink": artifact.st_nlink,
                                "hash_provenance":
                                    "COMPLETE ORIGINAL FIRST-PARTY ELF VERIFICATION",
                                "native_loaded": False,
                            })
                        finally:
                            os.close(fd)
                finally:
                    os.close(native_handle)
                owners.append({
                    "name": PHASES[index],
                    "absolute_path": workdir + "/" + PHASES[index],
                    "device": phase_info.st_dev,
                    "inode": phase_info.st_ino,
                    "uid": phase_info.st_uid,
                    "mode": format(stat.S_IMODE(phase_info.st_mode), "04o"),
                    "native_outputs": artifact_rows,
                })
            finally:
                os.close(phase_handle)
        return handle, {
            "path": workdir,
            "prefix": ROOT_PREFIX,
            "device": info.st_dev,
            "inode": info.st_ino,
            "uid": info.st_uid,
            "mode": format(stat.S_IMODE(info.st_mode), "04o"),
            "nofollow_directory_descriptor": True,
            "descriptor_opened_during_live_verification": True,
            "directory_scanned": False,
            "phase_count": 2,
            "phases": owners,
        }
    except BaseException:
        os.close(handle)
        raise


def publish_root_provenance(base: dict[str, object],
                            module: object,
                            state: dict[str, object],
                            result: dict[str, object],
                            options: dict[str, object]) -> dict[str, object]:
    require(result.get("status") == "PASS"
            and result.get("build_status") == "PASS"
            and result.get("family") == FAMILY
            and result.get("label") == BUILD_LABEL
            and type(_ROOT_CAPTURE) is dict,
            "publish provenance only after an actual successful canonical Rust build")
    captured = _ROOT_CAPTURE
    assert isinstance(captured, dict)
    require(captured.get("unique_process_count") == 28
            and captured.get("phase_count") == 2,
            "require actual two-phase 28-process provenance")
    kernel_state = state.get("runtime_state")
    require(type(kernel_state) is dict,
            "retain the actual first-party Rust build runtime state")
    kernel = kernel_state.get("kernel")
    require(kernel is not None, "retain the authenticated offline first-party kernel")
    build_receipt_relative = result.get("receipt_relative")
    build_receipt_hash = result.get("receipt_sha256")
    require(type(build_receipt_relative) is str
            and build_receipt_relative
                == EVIDENCE_PATH + "/" + evidence_names(BUILD_LABEL, False)[1],
            "bind only this exact published V19 build receipt")
    checked_hash(build_receipt_hash, "actual V19 build receipt")
    build_row = (
        "actual_v19_build_receipt", build_receipt_relative,
        build_receipt_hash, 0, DEVICE, 0,
    )
    absolute_receipt = ROOT + "/" + build_receipt_relative
    seen = os.stat(absolute_receipt, follow_symlinks=False)
    build_row = (build_row[0], build_row[1], build_row[2],
                 seen.st_size, seen.st_dev, seen.st_ino)
    base["_ALLOWLIST"] = frozenset(
        set(base["_ALLOWLIST"]) | {absolute_receipt},
    )
    receipt_raw = base["read_exact"](build_row)
    receipt = document(base, receipt_raw, "fresh genuine Rust V19 build receipt")
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
            and receipt.get("combined_bridge_overlay_apply_count") == 2
            and receipt.get("corrected_public_adapter_overlay_apply_count") == 2
            and receipt.get("archive_relative") == result.get("archive_relative")
            and receipt.get("archive_sha256") == result.get("archive_sha256")
            and receipt.get("candidate_matching") == "NOT RUN"
            and receipt.get("candidate_qualified") is False,
            "authenticate the real canonical V19 compiler receipt before provenance")
    root_record = {
        "schema": SCHEMA + "-durable-root-provenance-receipt",
        "version": VERSION,
        "status": "PASS",
        "publication_pass_means":
            "DURABLE REPRODUCIBLE-BUILD ROOT PROVENANCE ONLY",
        "family": FAMILY,
        "label": BUILD_LABEL,
        "source_sha256": options["source_sha256"],
        "protocol_sha256": options["protocol_sha256"],
        "contract_sha256": options["contract_sha256"],
        "frozen_graph_version": GRAPH_VERSION,
        "frozen_graph_summary_sha256": GRAPH["summary"][2],
        "canonical_build_status": "PASS",
        "canonical_build_archive_relative": receipt["archive_relative"],
        "canonical_build_archive_sha256": receipt["archive_sha256"],
        "canonical_build_archive_bytes": receipt["archive_bytes"],
        "canonical_build_archive_opened": False,
        "canonical_build_receipt_relative": build_receipt_relative,
        "canonical_build_receipt_sha256": build_receipt_hash,
        "canonical_build_receipt_bytes": seen.st_size,
        "canonical_build_receipt_device": seen.st_dev,
        "canonical_build_receipt_inode": seen.st_ino,
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
    encoded = canonical(base, root_record)
    require(0 < len(encoded) <= MAX_OWNER_BYTES,
            "bound the one complete exclusive root-provenance receipt")
    destination = module.ROOT / EVIDENCE_PATH / root_receipt_name(BUILD_LABEL)
    published = kernel.write_fresh(destination, encoded, synchronize=True)
    sync = kernel.fsync_directory(module.ROOT / EVIDENCE_PATH)
    require(published.get("sha256") == digest(encoded)
            and published.get("bytes") == len(encoded)
            and published.get("exclusive_creation") is True
            and published.get("file_fsync_completed") is True
            and sync.get("completed") is True,
            "publish exactly one fresh fsynced no-follow Rust root receipt")
    return {
        **result,
        "root_provenance_status": "PASS",
        "root_provenance_receipt_relative":
            EVIDENCE_PATH + "/" + root_receipt_name(BUILD_LABEL),
        "root_provenance_receipt_sha256": published["sha256"],
        "root_provenance_receipt_bytes": published["bytes"],
        "root_provenance_receipt_device": published["device"],
        "root_provenance_receipt_inode": published["inode"],
        "root_provenance_directory_fsync": sync,
        "actual_compiler_process_count": 28,
        "actual_private_phase_count": 2,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
    }


def run_build(base: dict[str, object], options: dict[str, object]) -> dict[str, object]:
    global _ROOT_CAPTURE
    require(options.get("mode") == "--build"
            and options.get("label") == BUILD_LABEL
            and _ROOT_CAPTURE is None
            and base.get("_WALL_ENABLED") is False,
            "require one separately authorised Rust V19 offline root-provenance build")
    base["verify_future_phase_one_v4"](options)
    context, state = collect_context(
        base, options["source_sha256"], options["protocol_sha256"],
        options["contract_sha256"],
    )
    raw = state["v18_state"]["owners"]["v16_builder"]
    owner = base["OWNER_BY_NAME"]["v16_builder"]
    require(digest(raw) == owner[2],
            "load only the immutable independently audited Rust V16 build kernel")
    import types

    module_name = "_rebar_v19_explicit_owned_rust_v16_kernel"
    require(module_name not in sys.modules,
            "reject a reused or substituted V19 first-party compiler recorder")
    module = types.ModuleType(module_name)
    module.__file__ = ROOT + "/" + owner[1]
    sys.modules[module_name] = module
    runtime_state: dict[str, object] | None = None
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True),
             module.__dict__)
        require(module.SCHEMA == "rebar-phase2-owned-rust-buffer-shape-source-build-v16"
                and module.VERSION == 16 and module.FAMILY == FAMILY
                and module.PHASES == PHASES
                and module.PROCESS_NAMES == PROCESS_NAMES
                and module.ROOT_PREFIX == ROOT_PREFIX,
                "reject a changed V16/V9 process, family, or root-prefix kernel")
        module.SCHEMA = SCHEMA
        module.VERSION = VERSION
        module.SOURCE_PATH = SOURCE_PATH
        module.PROTOCOL_PATH = PROTOCOL_PATH
        module.CONTRACT_PATH = CONTRACT_PATH
        module.FINAL_GRAPH_VERSION = GRAPH_VERSION
        module.CURRENT_EVIDENCE_OWNER_LOWER_BOUND = EVIDENCE_FLOOR
        module.CURRENT_HISTORY_REFERENCE_LOWER_BOUND = HISTORY_FLOOR
        previous_state = state["v18_state"]
        module.COMBINED_VARIANT = module.Owner(
            base["OWNER_BY_NAME"]["v2_variant"][1],
            base["V2_BRIDGE_SHA256"], base["V2_BRIDGE_BYTES"],
        )
        module.BUFFER_VARIANT = module.COMBINED_VARIANT
        module.BUFFER_FEATURE = tuple(
            module.Owner(base["OWNER_BY_NAME"][name][1],
                         base["OWNER_BY_NAME"][name][2],
                         base["OWNER_BY_NAME"][name][3])
            for name in ("v2_repair", "v2_protocol", "v2_contract")
        )
        module.FINAL_GRAPH = tuple(
            module.Owner(row[1], row[2], row[3]) for row in GRAPH.values()
        )

        def verified_context(source_pin: str, protocol_pin: str,
                             contract_pin: str) -> tuple[dict[str, object],
                                                          dict[str, object]]:
            nonlocal runtime_state
            require((source_pin, protocol_pin, contract_pin)
                    == (options["source_sha256"], options["protocol_sha256"],
                        options["contract_sha256"]),
                    "reject substituted Rust V19 source-freeze authority")
            runtime_state = {
                "originals": previous_state["originals"],
                "combined_bridge": previous_state["combined_bridge"],
                "corrected_adapter": previous_state["corrected_adapter"],
                "low_level_v9_source": previous_state["low_level_v9_source"],
            }
            state["runtime_state"] = runtime_state
            return context, runtime_state

        original_verifier = module.verify_reproduced_phases

        def verify_actual_phases(v9: object, v7: object, workdir: str,
                                 phases: list[object],
                                 steps: list[object]) -> dict[str, object]:
            global _ROOT_CAPTURE
            require(_ROOT_CAPTURE is None
                    and type(steps) is list and len(steps) == 28,
                    "require one genuine complete 28-process Rust build")
            pids: set[int] = set()
            for index, step in enumerate(steps):
                phase = PHASES[index // len(PROCESS_NAMES)]
                require(type(step) is dict
                        and step.get("name")
                            == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                        and ("phase" not in step or step.get("phase") == phase)
                        and type(step.get("pid")) is int and step["pid"] > 0
                        and step["pid"] not in pids
                        and step.get("exit_status") == 0
                        and step.get("working_directory")
                            == "<FRESH_PRIVATE_TMP>/" + phase,
                        "reject forged, reordered, duplicate, or failed Rust roles")
                pids.add(step["pid"])
            descriptor, root = capture_root_descriptor(v9, workdir, phases)
            try:
                proof = original_verifier(v9, v7, workdir, phases, steps)
                require(type(proof) is dict and proof.get("status") == "PASS"
                        and proof.get("unique_process_count") == 28
                        and proof.get("combined_bridge_overlay_count") == 2
                        and proof.get("corrected_public_adapter_overlay_count") == 2
                        and proof.get("byte_identical") is True
                        and proof.get("native_libraries_loaded") == 0,
                        "preserve the complete original fail-closed V16/V9 ELF proof")
                after = os.fstat(descriptor)
                named = os.stat(workdir, follow_symlinks=False)
                require(stat.S_ISDIR(after.st_mode)
                        and stat.S_IMODE(after.st_mode) == 0o700
                        and after.st_uid == os.geteuid()
                        and (after.st_dev, after.st_ino)
                            == (root["device"], root["inode"])
                        and (named.st_dev, named.st_ino)
                            == (root["device"], root["inode"]),
                        "reject a private Rust root swapped during ELF verification")
                _ROOT_CAPTURE = {
                    "root": root,
                    "phase_count": 2,
                    "unique_process_count": len(pids),
                    "original_reproducibility": "PASS",
                    "compiler_process_ids": sorted(pids),
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
        for name in (
            "source_sha256", "protocol_sha256", "contract_sha256",
            "owned_source_sha256", "combined_bridge_sha256",
            "combined_bridge_bytes", "corrected_adapter_sha256",
            "corrected_adapter_bytes", "label",
        ):
            setattr(forwarded, name, options[name])
        result = module.run_build(forwarded)
        require(type(result) is dict and result.get("family") == FAMILY,
                "require a genuinely published first-party Rust V19 build outcome")
        if result.get("status") != "PASS":
            require(result.get("failure_preserved") is True,
                    "preserve the exact failed V19 build and never invent a root")
            return result
        return publish_root_provenance(base, module, state, result, options)
    finally:
        sys.modules.pop(module_name, None)


def parse_cli(base: dict[str, object], values: list[str]) -> dict[str, object]:
    modes = ("--self-test", "--verify-frozen-context", "--render-contract", "--build")
    chosen = [name for name in modes if name in values]
    require(len(chosen) == 1 and values.count(chosen[0]) == 1,
            "require exactly one independently authorised Rust V19 mode")
    selected = chosen[0]
    result: dict[str, object] = {"mode": selected, "owned_source_sha256": []}
    mapping = {
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
        "--label": "label",
        "--combined-bridge-sha256": "combined_bridge_sha256",
        "--combined-bridge-bytes": "combined_bridge_bytes",
        "--corrected-adapter-sha256": "corrected_adapter_sha256",
        "--corrected-adapter-bytes": "corrected_adapter_bytes",
        "--phase1-v4-source-sha256": "phase1_v4_source_sha256",
        "--phase1-v4-protocol-sha256": "phase1_v4_protocol_sha256",
        "--phase1-v4-contract-sha256": "phase1_v4_contract_sha256",
    }
    position = 0
    while position < len(values):
        flag = values[position]
        if flag == selected:
            position += 1
            continue
        if flag == "--owned-source-sha256":
            require(position + 1 < len(values), "reject an incomplete Rust source pin")
            result["owned_source_sha256"].append(values[position + 1])
            position += 2
            continue
        require(flag in mapping and position + 1 < len(values),
                "reject an unknown, abbreviated, or incomplete Rust V19 flag")
        name = mapping[flag]
        require(name not in result, "reject duplicated Rust V19 authority: " + flag)
        value: object = values[position + 1]
        if name.endswith("_bytes"):
            require(type(value) is str and value.isascii() and value.isdecimal(),
                    "require exact positive decimal private-overlay bytes")
            value = int(value)
        result[name] = value
        position += 2
    for name in ("source_sha256", "protocol_sha256"):
        require(name in result, "independently pin Rust V19 source and protocol")
        checked_hash(result[name], name)
    build_only = (
        "label", "combined_bridge_sha256", "combined_bridge_bytes",
        "corrected_adapter_sha256", "corrected_adapter_bytes",
        "phase1_v4_source_sha256", "phase1_v4_protocol_sha256",
        "phase1_v4_contract_sha256",
    )
    if selected == "--render-contract":
        require("contract_sha256" not in result,
                "render a canonical contract before its digest exists")
    else:
        require("contract_sha256" in result,
                "caller-pin the exact complete Rust V19 machine contract")
        checked_hash(result["contract_sha256"], "Rust V19 contract")
    if selected != "--build":
        require(not result["owned_source_sha256"]
                and all(name not in result for name in build_only),
                "source-only gates never authorise a root, candidate, or compiler")
        return result
    require(result.get("label") == BUILD_LABEL
            and checked_label(BUILD_LABEL) == BUILD_LABEL
            and result.get("combined_bridge_sha256") == base["V2_BRIDGE_SHA256"]
            and result.get("combined_bridge_bytes") == base["V2_BRIDGE_BYTES"]
            and result.get("corrected_adapter_sha256")
                == base["CORRECTED_ADAPTER_SHA256"]
            and result.get("corrected_adapter_bytes")
                == base["CORRECTED_ADAPTER_BYTES"],
            "independently caller-pin the unique label and exact two private overlays")
    for role, key in (
        ("source", "phase1_v4_source_sha256"),
        ("protocol", "phase1_v4_protocol_sha256"),
        ("contract", "phase1_v4_contract_sha256"),
    ):
        require(result.get(key) == P0_V4[role][2],
                "independently caller-pin passing corrected P0 V4")
    provided = result["owned_source_sha256"]
    expected = {
        base["OWNER_BY_NAME"][name][1]
        + "=" + base["OWNER_BY_NAME"][name][2]
        for name in base["RUST_SOURCE_NAMES"]
    }
    require(type(provided) is list and len(provided) == 9
            and set(provided) == expected,
            "independently caller-pin all nine canonical first-party Rust sources")
    return result


def main() -> int:
    try:
        verify_runtime()
        base = load_v18()
        options = parse_cli(base, list(sys.argv[1:]))
        mode = options["mode"]
        if mode != "--build":
            base["install_wall"]()
        if mode == "--render-contract":
            _context, state = collect_context(
                base, options["source_sha256"], options["protocol_sha256"],
            )
            result = contract_document(
                base, options["source_sha256"], options["protocol_sha256"], state,
            )
        elif mode == "--verify-frozen-context":
            result, _state = collect_context(
                base, options["source_sha256"], options["protocol_sha256"],
                options["contract_sha256"],
            )
        elif mode == "--self-test":
            result = self_test(
                base, options["source_sha256"], options["protocol_sha256"],
                options["contract_sha256"],
            )
        else:
            result = run_build(base, options)
        encoded = canonical(base, result)
        require(0 < len(encoded) <= MAX_OWNER_BYTES,
                "bound the complete canonical Rust V19 result")
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
        return 0 if mode == "--render-contract" or result.get("status") == "PASS" else 1
    except (GateError, Exception) as error:
        result = {
            "schema": SCHEMA + "-entry-failure", "status": "FAIL",
            "version": VERSION, "family": FAMILY,
            "error_type": type(error).__name__,
            "error_message": str(error)[:8192],
            **boundary(),
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
