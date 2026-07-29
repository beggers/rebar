#!/usr/bin/env python3
"""Show real first-party Rust and C builds without claiming compatibility or speed."""

from __future__ import annotations

import argparse
import copy
import hashlib
import os
from pathlib import Path
import stat
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v88.py"
OUTPUT = "docs/evidence/candidate-current-overview-v88"
SCHEMA = "rebar-candidate-current-overview-v88"
OWNER_LIMIT = 4 * 1024 * 1024
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"

V87 = {
    "source": (
        "tools/render_candidate_current_overview_v87.py",
        "176ff7cee7735bb6a25475bf3d8f112def2ea0ff12779b28e1469c2fb85cdd44",
        82214,
        430870,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v87.inputs.json",
        "03c191f676a4551b6643a3c57d86f57cac21a51517e40a86926bf49e5176a8ee",
        1348917,
        430884,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v87.json",
        "1bd2765e4f22cc279872a5ab0253b1c55422899fad996bc2bc1aac4d4f300233",
        4106304,
        430885,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v87.svg",
        "7af85c8f26d47ec5b7ff7813aa7bfd3ceec5f82498b60da8be5884558c521101",
        6365,
        430886,
    ),
}

FEATURE = {
    "source": (
        "tools/reproduce_owned_rust_captured_findall_source_build_v21.py",
        "bc5f5b4efd8b20a564692e14f972c77267c58ac44a560b432a0a1cc38e794c58",
        100150,
        430883,
    ),
    "protocol": (
        "oracle/phase2/RUST-CAPTURED-FINDALL-SOURCE-BUILD-V21.md",
        "d7c137d2432c2f28f4b6b26fdde3a591b92f7d62e6018d047cfa0b3ccfe0a8c4",
        4943,
        524834,
    ),
    "contract": (
        "oracle/phase2/rust-captured-findall-source-build-v21.json",
        "61e14e1d47f55759a73721635594b69ba098541bc83c9046c99c0c282223fd4a",
        18420,
        524837,
    ),
}

BUILD_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v21-rust-phase2-v21-rust-captured-findall-"
    "root-provenance-publication-receipt.json",
    "bc3ebdc835ef6a89d351c4541863274d410e2685d35eacdc9668f4bf3a474102",
    3502,
    524894,
)
ROOT_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v21-rust-phase2-v21-rust-captured-findall-"
    "root-provenance-root-provenance-receipt.json",
    "73cee9c0a4f44d113da96b505eb0e9224577584b75c347e6fd351995d1d09a4e",
    6306,
    524895,
)

C_FEATURE = {
    "source": (
        "tools/reproduce_owned_c_subject_buffer_source_build_v18.py",
        "bf50ac15a7fdc7633e5804da066a77ee1342540228245cd33a5d977bfdfdc339",
        122194,
        430336,
    ),
    "protocol": (
        "oracle/phase2/C-SUBJECT-BUFFER-SOURCE-BUILD-V18.md",
        "97ab6a9881e2e2cf7c779660459adb00f7bb9e6db5e5b63da5c75d00f250c5aa",
        10389,
        524789,
    ),
    "contract": (
        "oracle/phase2/c-subject-buffer-source-build-v18.json",
        "aa68e0da13d666ea02565fe5aed347d5a34150e768df70fc5acc4a1e594b1a6a",
        17921,
        524797,
    ),
}
C_BUILD_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v18-c-phase2-v18-c-subject-buffer-"
    "root-provenance-publication-receipt.json",
    "4070feca7129fdcf3dc9762fae853649c68c722940af6157ecdcfa59d23e65ae",
    4713,
    524898,
)
C_ROOT_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v18-c-phase2-v18-c-subject-buffer-"
    "root-provenance-root-provenance-receipt.json",
    "a231eec31b29ca796c75cee03b702a3e35a9195e74675c8f56209419dfeb03c8",
    7629,
    524899,
)

SOURCE_KEY = "rust_captured_source_build_v21"
SOURCE_POOL_KEY = "lossless_v88_captured_source_evidence_pool"
SOURCE_POOL_SCHEMA = SCHEMA + "-lossless-complete-captured-source-pool-v1"
SOURCE_REFERENCE_SCHEMA = SCHEMA + "-complete-captured-source-reference-v1"
ACTUAL_KEY = "actual_rust_v21_captured_native_build"
ACTUAL_POOL_KEY = "lossless_v88_captured_actual_build_evidence_pool"
ACTUAL_POOL_SCHEMA = SCHEMA + "-lossless-complete-captured-build-pool-v1"
ACTUAL_REFERENCE_SCHEMA = SCHEMA + "-complete-captured-build-reference-v1"
C_SOURCE_KEY = "c_subject_source_build_v18"
C_SOURCE_POOL_KEY = "lossless_v88_c_source_evidence_pool"
C_SOURCE_POOL_SCHEMA = SCHEMA + "-lossless-complete-c-source-pool-v1"
C_SOURCE_REFERENCE_SCHEMA = SCHEMA + "-complete-c-source-reference-v1"
C_ACTUAL_KEY = "actual_c_v18_subject_native_build"
C_ACTUAL_POOL_KEY = "lossless_v88_c_actual_build_evidence_pool"
C_ACTUAL_POOL_SCHEMA = SCHEMA + "-lossless-complete-c-build-pool-v1"
C_ACTUAL_REFERENCE_SCHEMA = SCHEMA + "-complete-c-build-reference-v1"

CAPTURE_SOURCE_SHA256 = (
    "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a"
)
LITERAL_SOURCE_SHA256 = (
    "b707e924a23980385b0c5b0306daecd55bbb03d6f2511437f0532b6d39b2a112"
)
ENGINE_SHA256 = (
    "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
)
CAPTURE_NATIVE_BRIDGE_SHA256 = (
    "bfc9c55ffd3e6bedb6a0a82457c347d362adc9299b8cb107f98dc02a66ea1a43"
)
ARCHIVE_PATH = (
    "oracle/phase2/evidence/"
    "native-source-build-v21-rust-phase2-v21-rust-captured-findall-"
    "root-provenance.json.gz"
)
ARCHIVE_SHA256 = (
    "19e6bb346fd0a6a510772db6071899696bce2906cc92674a2bd757047cbf9372"
)
C_VARIANT_SHA256 = (
    "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962"
)
C_EXTENSION_SHA256 = (
    "f3794f963819a9af3798c1d97f32edcbc2a117f9ed20c56ec554a605de82eeae"
)
C_ADAPTER_SHA256 = (
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
)
C_ARCHIVE_PATH = (
    "oracle/phase2/evidence/"
    "native-source-build-v18-c-phase2-v18-c-subject-buffer-"
    "root-provenance.json.gz"
)
C_ARCHIVE_SHA256 = (
    "412b900038f0f9765593f67f1eef086359a5dbbbad1c90e967d211e0b8bbc504"
)


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    if not (type(size) is int and 0 < size <= OWNER_LIMIT):
        raise ValueError("reject an unbounded V88 source owner: " + label)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / relative), flags)
    try:
        before = os.fstat(handle)
        if not (
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_dev == 2064
            and before.st_ino == inode
            and before.st_size == size
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600
        ):
            raise ValueError("reject substituted exact V88 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject a truncated V88 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject extended whole V88 owner: " + label)
        raw = b"".join(chunks)
        after = os.fstat(handle)
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
            raise ValueError("reject changed whole V88 owner: " + label)
        return raw
    finally:
        os.close(handle)


FORBIDDEN_EVENTS = frozenset({
    "subprocess.Popen", "os.system", "os.posix_spawn", "os.posix_spawnp",
    "os.fork", "os.forkpty", "ctypes.dlopen", "ctypes.dlsym",
    "socket.__new__", "socket.connect", "socket.bind", "socket.sendto",
})
FORBIDDEN_IMPORTS = frozenset({
    "regex", "ctypes", "subprocess", "multiprocessing", "socket", "time",
    "gzip", "bz2", "lzma", "tarfile", "zipfile",
})


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_EVENTS:
        raise ValueError("V88 source-only operation rejected " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if isinstance(name, str) and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise ValueError("V88 source-only import rejected " + name)
        return
    if event != "open":
        return
    if len(arguments) < 3:
        raise ValueError("V88 rejected an unverifiable file open")
    path, mode, flags = arguments[:3]
    if not isinstance(path, str) or not isinstance(flags, int):
        raise ValueError("V88 rejected a descriptor or unverified owner")
    if mode not in (None, "r", "rb"):
        raise ValueError("V88 source mode rejected writable owner")
    if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
        os.O_CREAT | os.O_TRUNC | os.O_APPEND
    ):
        raise ValueError("V88 source mode cannot create or change files")
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        if normalized != str(ROOT) and not normalized.startswith(str(ROOT) + "/"):
            raise ValueError("V88 rejected private roots and holdout access")
    elif "/" in normalized or normalized in (".", ".."):
        raise ValueError("V88 rejected an escaped relative owner")
    if (
        normalized.endswith((".gz", ".bz2", ".xz", ".zip", ".so"))
        or "candidate-current-overview-v88." in normalized
        or "/.git/" in normalized
        or "/__pycache__/" in normalized
        or "/performance/" in normalized
        or "/experiments/" in normalized
    ):
        raise ValueError("V88 rejected archives, outputs, benchmarks, or native code")


def load_previous() -> tuple[
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    tuple,
    types.ModuleType,
]:
    raw = read_fixed(V87["source"], "complete pushed V87 renderer source")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v87")
    previous.__file__ = str(ROOT / V87["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    v86, v85, v84, v83, v82, chain, base = previous.load_previous()
    base.runtime()
    base.need(
        os.path.realpath(sys.executable) == PYTHON
        and sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and previous.SCHEMA == "rebar-candidate-current-overview-v87"
        and previous.SELF == V87["source"][0]
        and len(chain) == 15,
        "require exact isolated CPython 3.14.6 and the whole pushed V87 chain",
    )
    return previous, v86, v85, v84, v83, v82, chain, base


def previous_options(previous: types.ModuleType) -> argparse.Namespace:
    pins: dict[str, object] = {
        "source_sha256": V87["source"][1],
        "source_bytes": V87["source"][2],
        "build_receipt_sha256": previous.BUILD_RECEIPT[1],
        "root_receipt_sha256": previous.ROOT_RECEIPT[1],
    }
    for role, item in previous.V86.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for key, _, roles in previous.FEATURES:
        for role, item in roles.items():
            pins[key + "_" + role + "_sha256"] = item[1]
    return argparse.Namespace(**pins)


def authenticate_previous(
    previous: types.ModuleType,
    v86: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> tuple[dict, dict]:
    snapshot, assets = previous.build(
        v86, v85, v84, v83, v82, chain, base, previous_options(previous)
    )
    for role in ("inputs", "summary", "svg"):
        item = V87[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole actually pushed V87 " + role),
            "reconstruct every byte of the complete pushed V87 " + role,
        )
    old = base.document(assets[V87["summary"][0]], "whole pushed V87 summary")
    inputs = base.document(assets[V87["inputs"][0]], "whole pushed V87 inputs")
    base.need(
        old["snapshot"] == snapshot
        and old["version"] == 87
        and inputs["version"] == 87
        and old["authenticated_evidence_owner_lower_bound"] == 299
        and old["authenticated_history_reference_lower_bound"] == 304
        and old["lossless_family_evidence_pool_entry_count"] == 9
        and old["lossless_actual_outcome_evidence_pool_entry_count"] == 1
        and old["lossless_zig_source_evidence_pool_entry_count"] == 1
        and old["lossless_zig_actual_build_evidence_pool_entry_count"] == 1
        and old["lossless_v87_source_evidence_pool_entry_count"] == 6
        and old["lossless_v87_source_references_per_family"] == 6
        and old["lossless_v87_rust_actual_build_evidence_pool_entry_count"] == 1
        and old["lossless_v86_top_level_reconstruction_status"] == "PASS"
        and old["actual_rust_semantic_mismatch_count"] == 1440
        and old["actual_rust_verified_passing_case_count"] == 14853
        and old["rust_v15_original_campaign_actual_worker_count"] == 13
        and old["rust_v15_original_campaign_completed_suite_count"] == 8
        and old["rust_v15_original_campaign_verified_passing_case_count"] == 12942
        and old["rust_v15_original_campaign_infrastructure_failure_count"] == 5
        and old["rust_v15_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and old["actual_c_semantic_mismatch_count"] == 1230
        and old["actual_zig_semantic_mismatch_count"] == 1764
        and old["rust_literal_v20_actual_build_status"] == "PASS"
        and old["rust_literal_v20_actual_compiler_process_count"] == 28
        and old["rust_literal_v20_actual_independent_phase_count"] == 2
        and old["rust_literal_v20_candidate_matching"] == "NOT RUN"
        and old["rust_captured_findall_variant_build"] == "NOT RUN"
        and old["expanded_holdout_proposed_case_count"] == 14155776
        and old["expanded_holdout_final_protocol_status"] == "NOT FROZEN"
        and old["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and old["qualified_candidate_count"] == 0
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["performance"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False,
        "retain all true V87 old and latest outcomes without stale receipt history",
    )
    historical = previous.restore_historical_top(base, v83, old)
    v83.validate_pool(base, old["lossless_family_evidence_pool"], historical)
    v84.validate_actual_pool(
        base, old["lossless_actual_outcome_evidence_pool"], old[v84.ACTUAL_KEY]
    )
    v85.validate_zig_pool(
        base, old["lossless_zig_source_evidence_pool"], old[v85.ZIG_KEY]
    )
    zig_build = v86.resolve_build_reference(
        base, old["lossless_zig_actual_build_evidence_pool"], old[v86.BUILD_KEY]
    )
    v86.validate_build_pool(
        base, old["lossless_zig_actual_build_evidence_pool"], zig_build
    )
    documents, _ = previous.load_features(base)
    previous.validate_source_pool(base, old[previous.SOURCE_POOL_KEY], documents)
    v20 = previous.resolve_actual_reference(
        base, old[previous.ACTUAL_POOL_KEY], old[previous.ACTUAL_KEY]
    )
    previous.validate_actual_pool(base, old[previous.ACTUAL_POOL_KEY], v20)
    base.need(
        [row.get("family") for row in old["families"]]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and old["families"][0]["correctness"] == "BASELINE PASS"
        and old["families"][6]["build_status"] == "FAIL"
        and old["families"][6]["completed_source_build_count"] == 2
        and old["families"][6]["matching_test_status"] == "NOT MEASURED",
        "retain the complete baseline, all six families, and the real Fortran failure",
    )
    return old, inputs


def load_contract(base: types.ModuleType) -> dict:
    for role in ("source", "protocol"):
        read_fixed(FEATURE[role], "whole exact V21 source-freeze " + role)
    raw = read_fixed(FEATURE["contract"], "whole exact V21 source-freeze contract")
    contract = base.document(raw, "whole canonical V21 source-freeze contract")
    base.need(
        type(contract) is dict
        and len(contract) == 20
        and base.canonical(contract) == raw
        and contract["schema"]
        == "rebar-phase2-owned-rust-captured-findall-source-build-v21-source-freeze"
        and contract["version"] == 21
        and contract["source"]["sha256"] == FEATURE["source"][1]
        and contract["source"]["bytes"] == FEATURE["source"][2]
        and contract["protocol"]["sha256"] == FEATURE["protocol"][1]
        and contract["protocol"]["bytes"] == FEATURE["protocol"][2]
        and contract["historical_rust_results"]
        ["historical_complete_semantic_mismatch_count"] == 1440
        and contract["historical_rust_results"]
        ["historical_complete_verified_passing_case_count"] == 14853
        and contract["historical_rust_results"]
        ["latest_guarded_completed_suite_count"] == 8
        and contract["historical_rust_results"]
        ["latest_guarded_verified_passing_case_count"] == 12942
        and contract["historical_rust_results"]
        ["latest_guarded_worker_failure_count"] == 5
        and contract["actual_successful_v20_native_build"]
        ["actual_compiler_process_count"] == 28
        and contract["actual_successful_v20_native_build"]
        ["actual_source_phase_count"] == 2
        and contract["actual_successful_v20_native_build"]
        ["immediate_literal_bridge"]["sha256"] == LITERAL_SOURCE_SHA256
        and contract["independently_reviewed_captured_feature"]
        ["variant"]["sha256"] == CAPTURE_SOURCE_SHA256
        and contract["independently_reviewed_captured_feature"]
        ["variant"]["bytes"] == 179520
        and contract["published_expanded_sealed_holdout_proposal"]
        ["case_count"] == 14155776
        and contract["published_expanded_sealed_holdout_proposal"]
        ["final_protocol_status"] == "NOT FROZEN"
        and contract["published_expanded_sealed_holdout_proposal"]
        ["case_status"] == "NOT GENERATED; NOT OPENED"
        and contract["source_only_effects"]["candidate_build"] == "NOT RUN"
        and contract["source_only_effects"]["candidate_matching"] == "NOT RUN"
        and contract["source_only_effects"]["actual_compiler_process_count"] == 0
        and contract["source_only_effects"]["qualified_candidate_count"] == 0
        and contract["source_only_effects"]["winner_selected"] is False,
        "distinguish frozen V21 source from later real native-build receipts",
    )
    return contract


def load_c_contract(base: types.ModuleType) -> dict:
    for role in ("source", "protocol"):
        read_fixed(C_FEATURE[role], "whole exact C18 source-freeze " + role)
    raw = read_fixed(C_FEATURE["contract"], "whole exact C18 source-freeze contract")
    contract = base.document(raw, "whole canonical C18 source-freeze contract")
    base.need(
        type(contract) is dict
        and len(contract) == 20
        and base.canonical(contract) == raw
        and contract["schema"]
        == "rebar-phase2-owned-c-subject-buffer-source-build-v18-source-freeze"
        and contract["version"] == 18
        and contract["family"] == "c"
        and contract["source"]["sha256"] == C_FEATURE["source"][1]
        and contract["source"]["bytes"] == C_FEATURE["source"][2]
        and contract["protocol"]["sha256"] == C_FEATURE["protocol"][1]
        and contract["protocol"]["bytes"] == C_FEATURE["protocol"][2]
        and contract["historical_c_correctness"]["semantic_mismatch_count"] == 1230
        and contract["historical_c_correctness"]["verified_passing_case_count"] == 7325
        and contract["historical_c_correctness"]["case_execution_denominator"] == 31237
        and contract["historical_c_correctness"]["status"] == "FAIL"
        and contract["historical_c_correctness"]["replacement_qualified"] is False
        and contract["preserved_latest_rust_correctness"]["attempted_suite_count"] == 13
        and contract["preserved_latest_rust_correctness"]["completed_suite_count"] == 8
        and contract["preserved_latest_rust_correctness"]["verified_passing_case_count"]
        == 12942
        and contract["preserved_latest_rust_correctness"]["infrastructure_failure_count"]
        == 5
        and contract["preserved_latest_rust_correctness"]["semantic_mismatch_count"]
        == "NOT MEASURED"
        and contract["preserved_expanded_final_comparison_proposal"]["case_count"]
        == 14155776
        and contract["preserved_expanded_final_comparison_proposal"]["cases"]
        == "NOT GENERATED; NOT OPENED"
        and contract["preserved_expanded_final_comparison_proposal"]["final_protocol"]
        == "NOT FROZEN"
        and contract["preserved_expanded_final_comparison_proposal"]
        ["previous_proposal_case_count"] == 4194304
        and contract["source_only_effects"]["candidate_build"] == "NOT RUN"
        and contract["source_only_effects"]["candidate_matching"] == "NOT RUN"
        and contract["source_only_effects"]["actual_compiler_process_count"] == 0
        and contract["source_only_effects"]["qualified_candidate_count"] == 0
        and contract["source_only_effects"]["winner_selected"] is False,
        "distinguish frozen C18 source from subsequently published real native builds",
    )
    return contract


def validate_receipts(base: types.ModuleType, build: object, root: object) -> None:
    base.need(
        type(build) is dict and len(build) == 60
        and type(root) is dict and len(root) == 68,
        "reject omitted or fabricated whole V21 actual plaintext receipts",
    )
    assert isinstance(build, dict) and isinstance(root, dict)
    for label, value, schema in (
        (
            "actual build", build,
            "rebar-phase2-owned-rust-captured-findall-source-build-v21-"
            "durable-publication-receipt",
        ),
        (
            "actual root provenance", root,
            "rebar-phase2-owned-rust-captured-findall-source-build-v21-"
            "durable-root-provenance-receipt",
        ),
    ):
        base.need(
            value["schema"] == schema
            and value["status"] == "PASS"
            and value["family"] == "rust"
            and value["label"] == "phase2-v21-rust-captured-findall-root-provenance"
            and value["source_sha256"] == FEATURE["source"][1]
            and value["protocol_sha256"] == FEATURE["protocol"][1]
            and value["contract_sha256"] == FEATURE["contract"][1]
            and value["actual_compiler_process_count"] == 28
            and value["candidate_correctness"] == "NOT MEASURED"
            and value["candidate_matching"] == "NOT RUN"
            and value["candidate_qualified"] is False
            and value["candidate_workers_started"] == 0
            and value["native_libraries_loaded"] == 0
            and value["clock_samples"] == 0
            and value["holdout"] == "NOT OPENED"
            and value["performance"] == "NOT MEASURED"
            and value["memory"] == "NOT MEASURED"
            and value["undefined_behavior"] == "NOT MEASURED"
            and value["winner_selected"] is False,
            "reject a fabricated compatible or timed V21 " + label,
        )
    base.need(
        build["build_status"] == "PASS"
        and build["expected_actual_compiler_process_count"] == 28
        and build["combined_bridge_sha256"] == CAPTURE_SOURCE_SHA256
        and build["combined_bridge_bytes"] == 179520
        and build["candidate_imports"] == 0
        and build["candidate_processes_started"] == 0
        and build["hidden_cases_read"] == 0
        and build["timing_trials_run"] == 0
        and build["archive_relative"] == ARCHIVE_PATH
        and build["archive_sha256"] == ARCHIVE_SHA256
        and build["archive_bytes"] == 108632
        and build["global_evidence_owner_census"] == "NOT MEASURED"
        and build["global_history_reference_census"] == "NOT MEASURED"
        and build["historical_actual_rust_mismatch_count"] == 928
        and build["historical_actual_rust_verified_passing_case_count"] == 8965,
        "preserve stale receipt-scoped history without promoting it to graph truth",
    )
    base.need(
        root["version"] == 21
        and root["actual_source_phase_count"] == 2
        and root["expected_compiler_process_count"] == 28
        and root["canonical_build_status"] == "PASS"
        and root["canonical_build_receipt_relative"] == BUILD_RECEIPT[0]
        and root["canonical_build_receipt_sha256"] == BUILD_RECEIPT[1]
        and root["canonical_build_receipt_bytes"] == BUILD_RECEIPT[2]
        and root["canonical_build_receipt_device"] == 2064
        and root["canonical_build_receipt_inode"] == BUILD_RECEIPT[3]
        and root["canonical_build_archive_relative"] == ARCHIVE_PATH
        and root["canonical_build_archive_sha256"] == ARCHIVE_SHA256
        and root["canonical_build_archive_bytes"] == 108632
        and root["canonical_build_archive_opened"] is False
        and root["cumulative_captured_bridge_sha256"] == CAPTURE_SOURCE_SHA256
        and root["cumulative_captured_bridge_bytes"] == 179520
        and root["previous_literal_bridge_sha256"] == LITERAL_SOURCE_SHA256
        and root["previous_literal_bridge_bytes"] == 178950
        and root["previous_v20_build_receipt_sha256"]
        == "b9945838778c800f59a505021503655ea5bb4b3e11e1f0cf17f4be48cadde1b0"
        and root["previous_v20_root_receipt_sha256"]
        == "bb5bd524a7bd8c4b3845c9654e81981cb6136c4fcff7a5e52ca375ce75e745aa"
        and root["expanded_holdout_proposal_case_count"] == 14155776
        and root["expanded_holdout_final_protocol_status"] == "NOT FROZEN"
        and root["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and root["expanded_holdout_cases_generated"] == 0
        and root["expanded_holdout_cases_opened"] == 0
        and root["historical_archives_opened"] == 0
        and root["tmp_directory_scanned"] is False,
        "preserve V20 and verify real V21 using receipt provenance alone",
    )
    private = root["root"]
    base.need(
        type(private) is dict
        and private["device"] == 2049
        and private["mode"] == "0700"
        and private["directory_scanned"] is False
        and private["nofollow_directory_descriptor"] is True
        and private["phase_count"] == 2
        and type(private["phases"]) is list
        and len(private["phases"]) == 2,
        "authenticate genuine captured-build root without opening a private root",
    )
    for phase, name in zip(private["phases"], ("reference-a", "reference-b"), strict=True):
        base.need(
            phase["name"] == name and len(phase["native_outputs"]) == 2,
            "retain the actual distinct captured build phase: " + name,
        )
        outputs = {owner["role"]: owner for owner in phase["native_outputs"]}
        base.need(
            set(outputs) == {"engine", "bridge"}
            and outputs["engine"]["sha256"] == ENGINE_SHA256
            and outputs["engine"]["bytes"] == 658344
            and outputs["bridge"]["sha256"] == CAPTURE_NATIVE_BRIDGE_SHA256
            and outputs["bridge"]["bytes"] == 148792
            and outputs["engine"]["native_loaded"] is False
            and outputs["bridge"]["native_loaded"] is False,
            "retain actual first-party captured artifacts solely from public receipts",
        )


def validate_c_receipts(base: types.ModuleType, build: object, root: object) -> None:
    base.need(
        type(build) is dict and len(build) == 66
        and type(root) is dict and len(root) == 65,
        "reject omitted or fabricated complete C18 plaintext native-build receipts",
    )
    assert isinstance(build, dict) and isinstance(root, dict)
    for label, value, schema in (
        (
            "actual build", build,
            "rebar-phase2-owned-c-subject-buffer-source-build-v18-"
            "durable-publication-receipt",
        ),
        (
            "actual root provenance", root,
            "rebar-phase2-owned-c-subject-buffer-source-build-v18-"
            "durable-root-provenance-receipt",
        ),
    ):
        base.need(
            value["schema"] == schema
            and value["version"] == 18
            and value["status"] == "PASS"
            and value["family"] == "c"
            and value["label"] == "phase2-v18-c-subject-buffer-root-provenance"
            and value["source_sha256"] == C_FEATURE["source"][1]
            and value["protocol_sha256"] == C_FEATURE["protocol"][1]
            and value["contract_sha256"] == C_FEATURE["contract"][1]
            and value["actual_compiler_process_count"] == 14
            and value["expected_compiler_process_count"] == 14
            and value["candidate_correctness"] == "NOT MEASURED"
            and value["candidate_matching"] == "NOT RUN"
            and value["native_libraries_loaded"] == 0
            and value["clock_samples"] == 0
            and value["hidden_cases_read"] == 0
            and value["holdout"] == "NOT OPENED"
            and value["performance"] == "NOT MEASURED"
            and value["memory"] == "NOT MEASURED"
            and value["undefined_behavior"] == "NOT MEASURED"
            and value["winner_selected"] is False
            and value["runtime_non_delegation"] == "NOT ESTABLISHED"
            and value["authenticated_toolchain_owner_count"] == 5
            and value["historical_c_candidate_status"] == "FAIL"
            and value["historical_c_semantic_mismatch_count"] == 1230
            and value["historical_c_verified_passing_case_count"] == 7325
            and value["historical_rust_v10_semantic_mismatch_count"] == 1440
            and value["historical_rust_v10_verified_passing_case_count"] == 14853
            and value["current_rust_completed_suite_count"] == 8
            and value["current_rust_verified_passing_case_count"] == 12942
            and value["current_rust_infrastructure_failure_count"] == 5
            and value["current_rust_semantic_mismatch_count"] == "NOT MEASURED"
            and value["proposed_final_holdout_case_count"] == 14155776
            and value["proposed_final_holdout_status"] == "NOT GENERATED; NOT OPENED",
            "reject fabricated matching, speed, or rewritten C18 history in " + label,
        )
    base.need(
        build["build_status"] == "PASS"
        and build["actual_source_apply_count"] == 2
        and build["expected_source_apply_count"] == 2
        and build["variant_source_sha256"] == C_VARIANT_SHA256
        and build["variant_source_bytes"] == 222212
        and build["adapter_source_sha256"] == C_ADAPTER_SHA256
        and build["candidate_processes_started"] == 0
        and build["candidate_imports"] == 0
        and build["timing_trials_run"] == 0
        and build["qualified_candidate_count"] == 0
        and build["archive_relative"] == C_ARCHIVE_PATH
        and build["archive_sha256"] == C_ARCHIVE_SHA256
        and build["archive_bytes"] == 38505,
        "authenticate the complete actual two-phase C18 publication without an archive",
    )
    base.need(
        root["actual_source_phase_count"] == 2
        and root["candidate_qualified"] is False
        and root["candidate_workers_started"] == 0
        and root["canonical_build_status"] == "PASS"
        and root["canonical_build_receipt_relative"] == C_BUILD_RECEIPT[0]
        and root["canonical_build_receipt_sha256"] == C_BUILD_RECEIPT[1]
        and root["canonical_build_receipt_bytes"] == C_BUILD_RECEIPT[2]
        and root["canonical_build_receipt_device"] == 2064
        and root["canonical_build_receipt_inode"] == C_BUILD_RECEIPT[3]
        and root["canonical_build_archive_relative"] == C_ARCHIVE_PATH
        and root["canonical_build_archive_sha256"] == C_ARCHIVE_SHA256
        and root["canonical_build_archive_bytes"] == 38505
        and root["canonical_build_archive_opened"] is False
        and root["distinct_actual_native_extension_count"] == 2
        and root["distinct_actual_phase_source_owner_count"] == 4
        and root["subject_buffer_source_overlay_apply_count"] == 2
        and root["native_source_delegation_audit"] == "PASS"
        and root["python_adapter_delegation_audit"] == "PASS"
        and root["tmp_directory_scanned"] is False,
        "verify C18 phase provenance without confusing source audit with independence",
    )
    private = root["root"]
    base.need(
        type(private) is dict
        and private["device"] == 2049
        and private["mode"] == "0700"
        and private["directory_scanned"] is False
        and private["nofollow_directory_descriptor"] is True
        and private["phase_count"] == 2
        and private["byte_identical_native_output"] is True
        and private["distinct_native_owner_count"] == 2
        and private["distinct_source_owner_count"] == 4
        and type(private["phases"]) is list
        and len(private["phases"]) == 2,
        "authenticate the actually recorded C18 private-root receipt without opening it",
    )
    for phase, name in zip(private["phases"], ("reference-a", "reference-b"), strict=True):
        base.need(
            phase["name"] == name
            and type(phase["native_output"]) is dict
            and type(phase["source_owners"]) is list
            and len(phase["source_owners"]) == 2,
            "retain the singular real C18 native output in phase " + name,
        )
        native = phase["native_output"]
        owners = {owner["role"]: owner for owner in phase["source_owners"]}
        base.need(
            native["role"] == "extension"
            and native["sha256"] == C_EXTENSION_SHA256
            and native["bytes"] == 163504
            and native["native_loaded"] is False
            and set(owners) == {"variant", "adapter"}
            and owners["variant"]["sha256"] == C_VARIANT_SHA256
            and owners["variant"]["bytes"] == 222212
            and owners["adapter"]["sha256"] == C_ADAPTER_SHA256
            and owners["adapter"]["bytes"] == 60707,
            "preserve every real independent C18 phase artifact from receipts only",
        )


def make_source_proof(base: types.ModuleType, contract: dict) -> dict:
    return {
        "schema": SCHEMA + "-complete-captured-source-proof-v1",
        "proof_key": SOURCE_KEY,
        "complete_feature_contract": copy.deepcopy(contract),
        "authenticated_source_owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in FEATURE.items()
        },
        "new_distinct_source_owner_count": 3,
        "source_status": "FROZEN SOURCE ONLY",
    }


def make_c_source_proof(base: types.ModuleType, contract: dict) -> dict:
    return {
        "schema": SCHEMA + "-complete-c-source-proof-v1",
        "proof_key": C_SOURCE_KEY,
        "complete_feature_contract": copy.deepcopy(contract),
        "authenticated_source_owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in C_FEATURE.items()
        },
        "new_distinct_source_owner_count": 3,
        "source_status": "FROZEN SOURCE ONLY",
    }


def make_pool(
    base: types.ModuleType, schema: str, key: str, proof: dict
) -> dict:
    raw = base.canonical(proof)
    digest = base.digest(raw)
    pool = {
        "schema": schema,
        "version": 1,
        "hash_algorithm": "sha256",
        "entries": {
            digest: {
                "proof_key": key,
                "proof_schema": proof["schema"],
                "canonical_sha256": digest,
                "canonical_bytes": len(raw),
                "complete_proof": copy.deepcopy(proof),
            }
        },
    }
    validate_pool(base, pool, schema, key, proof)
    return pool


def validate_pool(
    base: types.ModuleType,
    pool: object,
    schema: str,
    key: str,
    proof: dict,
) -> None:
    base.need(
        type(pool) is dict
        and set(pool) == {"schema", "version", "hash_algorithm", "entries"}
        and pool["schema"] == schema
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and type(pool["entries"]) is dict
        and len(pool["entries"]) == 1,
        "require exactly one complete canonical V88 proof: " + key,
    )
    assert isinstance(pool, dict)
    digest, entry = next(iter(pool["entries"].items()))
    raw = base.canonical(proof)
    base.need(
        type(entry) is dict
        and set(entry) == {
            "proof_key", "proof_schema", "canonical_sha256",
            "canonical_bytes", "complete_proof",
        }
        and entry["proof_key"] == key
        and entry["proof_schema"] == proof["schema"]
        and entry["canonical_sha256"] == digest
        and base.checked(digest, "whole V88 " + key) == base.digest(raw)
        and entry["canonical_bytes"] == len(raw)
        and base.canonical(entry["complete_proof"]) == raw,
        "reject omitted, changed, copied, or partial V88 proof: " + key,
    )


def make_reference(
    base: types.ModuleType,
    pool: dict,
    schema: str,
    key: str,
    proof: dict,
) -> dict:
    expected_pool = {
        SOURCE_KEY: SOURCE_POOL_SCHEMA,
        ACTUAL_KEY: ACTUAL_POOL_SCHEMA,
        C_SOURCE_KEY: C_SOURCE_POOL_SCHEMA,
        C_ACTUAL_KEY: C_ACTUAL_POOL_SCHEMA,
    }[key]
    validate_pool(base, pool, expected_pool, key, proof)
    raw = base.canonical(proof)
    return {
        "schema": schema,
        "proof_key": key,
        "sha256": base.digest(raw),
        "canonical_bytes": len(raw),
    }


def resolve_reference(
    base: types.ModuleType,
    pool: dict,
    reference: object,
    schema: str,
    key: str,
) -> dict:
    base.need(
        type(reference) is dict
        and set(reference) == {"schema", "proof_key", "sha256", "canonical_bytes"}
        and reference["schema"] == schema
        and reference["proof_key"] == key
        and type(reference["canonical_bytes"]) is int
        and reference["canonical_bytes"] > 0,
        "reject an omitted or fabricated V88 proof reference: " + key,
    )
    assert isinstance(reference, dict)
    digest = base.checked(reference["sha256"], "whole V88 reference " + key)
    entry = pool["entries"].get(digest)
    base.need(
        type(entry) is dict
        and entry.get("proof_key") == key
        and entry.get("canonical_sha256") == digest
        and entry.get("canonical_bytes") == reference["canonical_bytes"],
        "reject swapped, truncated, or fabricated V88 proof: " + key,
    )
    proof = entry["complete_proof"]
    raw = base.canonical(proof)
    base.need(
        len(raw) == reference["canonical_bytes"] and base.digest(raw) == digest,
        "resolve every byte of the complete V88 evidence: " + key,
    )
    return copy.deepcopy(proof)


def make_actual_proof(base: types.ModuleType, build: dict, root: dict) -> dict:
    return {
        "schema": SCHEMA + "-complete-actual-captured-build-v21",
        "version": 21,
        "complete_public_build_receipt": copy.deepcopy(build),
        "complete_public_root_provenance_receipt": copy.deepcopy(root),
        "build_receipt_owner": base.synthetic_owner(
            BUILD_RECEIPT[:3], BUILD_RECEIPT[3]
        ),
        "root_provenance_receipt_owner": base.synthetic_owner(
            ROOT_RECEIPT[:3], ROOT_RECEIPT[3]
        ),
        "actual_independent_phase_count": 2,
        "actual_compiler_process_count": 28,
        "actual_engine_sha256": ENGINE_SHA256,
        "actual_engine_bytes": 658344,
        "actual_native_bridge_sha256": CAPTURE_NATIVE_BRIDGE_SHA256,
        "actual_native_bridge_bytes": 148792,
        "compiled_captured_source_sha256": CAPTURE_SOURCE_SHA256,
        "compiled_captured_source_bytes": 179520,
        "previous_literal_source_sha256": LITERAL_SOURCE_SHA256,
        "compressed_archive_opened_by_graph": False,
        "private_root_opened_by_graph": False,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def make_c_actual_proof(base: types.ModuleType, build: dict, root: dict) -> dict:
    return {
        "schema": SCHEMA + "-complete-actual-c-build-v18",
        "version": 18,
        "complete_public_build_receipt": copy.deepcopy(build),
        "complete_public_root_provenance_receipt": copy.deepcopy(root),
        "build_receipt_owner": base.synthetic_owner(
            C_BUILD_RECEIPT[:3], C_BUILD_RECEIPT[3]
        ),
        "root_provenance_receipt_owner": base.synthetic_owner(
            C_ROOT_RECEIPT[:3], C_ROOT_RECEIPT[3]
        ),
        "actual_independent_phase_count": 2,
        "actual_compiler_process_count": 14,
        "actual_native_extension_sha256": C_EXTENSION_SHA256,
        "actual_native_extension_bytes": 163504,
        "compiled_subject_source_sha256": C_VARIANT_SHA256,
        "compiled_subject_source_bytes": 222212,
        "adapter_source_sha256": C_ADAPTER_SHA256,
        "adapter_source_bytes": 60707,
        "historical_c_semantic_mismatch_count": 1230,
        "historical_c_verified_passing_case_count": 7325,
        "compressed_archive_opened_by_graph": False,
        "private_root_opened_by_graph": False,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def make_changes(
    source_reference: dict,
    actual_reference: dict,
    c_source_reference: dict,
    c_actual_reference: dict,
) -> dict:
    return {
        "actual_current_graph_predecessor_version": 87,
        "authenticated_evidence_owner_lower_bound": 309,
        "authenticated_history_reference_lower_bound": 314,
        "v88_new_directly_authenticated_source_owner_count": 6,
        "v88_new_directly_authenticated_plaintext_build_owner_count": 4,
        "rust_captured_findall_variant_build": "PASS",
        "rust_captured_findall_variant_matching": "NOT RUN",
        "rust_captured_findall_variant_performance": "NOT MEASURED",
        "rust_captured_v21_actual_build_status": "PASS",
        "rust_captured_v21_actual_independent_phase_count": 2,
        "rust_captured_v21_actual_compiler_process_count": 28,
        "rust_captured_v21_actual_source_sha256": CAPTURE_SOURCE_SHA256,
        "rust_captured_v21_actual_source_bytes": 179520,
        "rust_captured_v21_actual_engine_sha256": ENGINE_SHA256,
        "rust_captured_v21_actual_native_bridge_sha256": CAPTURE_NATIVE_BRIDGE_SHA256,
        "rust_captured_v21_candidate_matching": "NOT RUN",
        "rust_captured_v21_candidate_qualified": False,
        "rust_literal_v20_actual_build_status": "PASS",
        "rust_literal_v20_actual_compiler_process_count": 28,
        "rust_literal_v20_actual_independent_phase_count": 2,
        "rust_literal_v20_candidate_matching": "NOT RUN",
        "c_subject_v18_actual_build_status": "PASS",
        "c_subject_v18_actual_independent_phase_count": 2,
        "c_subject_v18_actual_compiler_process_count": 14,
        "c_subject_v18_actual_source_sha256": C_VARIANT_SHA256,
        "c_subject_v18_actual_source_bytes": 222212,
        "c_subject_v18_actual_native_extension_sha256": C_EXTENSION_SHA256,
        "c_subject_v18_actual_native_extension_bytes": 163504,
        "c_subject_v18_candidate_matching": "NOT RUN",
        "c_subject_v18_candidate_qualified": False,
        "expanded_holdout_proposed_case_count": 14155776,
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "preserved_previous_holdout_proposal_case_count": 4194304,
        "compressed_v21_archive_opened_by_graph": False,
        "private_v21_build_root_opened_by_graph": False,
        "compressed_c18_archive_opened_by_graph": False,
        "private_c18_build_root_opened_by_graph": False,
        "global_evidence_owner_census": "NOT MEASURED",
        "global_history_reference_census": "NOT MEASURED",
        SOURCE_KEY: copy.deepcopy(source_reference),
        ACTUAL_KEY: copy.deepcopy(actual_reference),
        C_SOURCE_KEY: copy.deepcopy(c_source_reference),
        C_ACTUAL_KEY: copy.deepcopy(c_actual_reference),
    }


def make_svg() -> bytes:
    rows = (
        ("Python re", "The unchanged Python 3.14.6 comparison point", "BASELINE", "#34d399"),
        (
            "Rust",
            "Both first-party versions built twice; 8/13 test groups passed",
            "BUILDS PASS; TESTS FAIL",
            "#fbbf24",
        ),
        (
            "C",
            "Built twice; 1,230 previous differences remain",
            "BUILD PASS; TESTS FAIL",
            "#fbbf24",
        ),
        ("Zig", "1,764 recorded differences; own engine built twice", "NOT COMPATIBLE", "#fb7185"),
        ("C++", "2,308 differences and five startup failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences and four startup failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Two builds produced different outputs", "BUILD FAILED", "#fb7185"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="840" viewBox="0 0 1320 840" role="img" aria-labelledby="title description">',
        '<title id="title">Searching for a faster, fully compatible Python re</title>',
        '<desc id="description">Python is compared with six independent, from-scratch regular-expression engines. The Rust literal and captured-result versions were each genuinely built in two offline phases with 28 first-party compiler and inspection steps. The C subject-buffer version was genuinely built in two offline phases with 14 first-party compiler and inspection steps. These actual build successes establish reproducible compilation only, not Python compatibility, runtime independence, or speed. The latest Rust correctness attempt completed eight of thirteen original groups, explicitly verified 12,942 checks and preserved five genuine worker failures. The complete historical Rust run has 1,440 differences and 14,853 passes; the actual historical C run has 1,230 differences and 7,325 passes. Fortran was built twice and the outputs disagreed. The proposed 14,155,776-case final comparison remains not frozen, not generated, unopened and unrun. No candidate has qualified; no performance or memory has been measured; no winner exists.</desc>',
        '<rect width="1320" height="840" rx="20" fill="#0b1220"/>',
        '<text x="38" y="52" fill="#f8fafc" font-size="27" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="38" y="88" fill="#cbd5e1" font-size="17" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<line x1="38" y1="110" x2="1282" y2="110" stroke="#334155"/>',
    ]
    for index, (name, details, result, colour) in enumerate(rows):
        y = 150 + index * 51
        parts.extend((
            f'<circle cx="48" cy="{y - 5}" r="6" fill="{colour}"/>',
            f'<text x="66" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="175" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{details}</text>',
            f'<text x="1268" y="{y}" text-anchor="end" fill="{colour}" font-size="12" font-family="system-ui,sans-serif" font-weight="700">{result}</text>',
        ))
    parts.extend((
        '<line x1="38" y1="495" x2="1282" y2="495" stroke="#334155"/>',
        '<text x="38" y="530" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">Compatibility target: all 31,237 original Python checks and 8,244 separate additional checks.</text>',
        '<text x="38" y="561" fill="#fcd34d" font-size="14" font-family="system-ui,sans-serif">Latest Rust result: 12,942 verified checks; 8 of 13 groups finished; 5 genuine failures.</text>',
        '<text x="38" y="592" fill="#93c5fd" font-size="13" font-family="system-ui,sans-serif">Rust literal: 2 phases, 28 steps. Rust captured: 2 phases, 28 steps. C subject-buffer: 2 phases, 14 steps.</text>',
        '<text x="38" y="622" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">These real builds prove reproducible compilation only, not compatibility, independence, or speed.</text>',
        '<text x="38" y="652" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Fortran was actually built twice; its different outputs failed the reproducibility check.</text>',
        '<text x="38" y="682" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">No external regex package, borrowed engine, fallback, or selected winner.</text>',
        '<text x="38" y="717" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">Proposed final comparison: 14,155,776 cases.</text>',
        '<text x="38" y="748" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Not frozen, not generated, not opened, and not run. Speed and memory: NOT MEASURED.</text>',
        '<text x="38" y="779" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">The old 4,194,304-case proposal is preserved separately as historical evidence.</text>',
        '<text x="38" y="819" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 88 · all prior evidence preserved · no fully compatible candidate · no winner.</text>',
        '</svg>',
        '',
    ))
    return "\n".join(parts).encode("utf-8")


def validate_families(
    base: types.ModuleType,
    previous: types.ModuleType,
    old: dict,
    families: object,
    source_pool: dict,
    source_proof: dict,
    actual_pool: dict,
    actual_proof: dict,
    c_source_pool: dict,
    c_source_proof: dict,
    c_actual_pool: dict,
    c_actual_proof: dict,
) -> None:
    base.need(
        type(families) is list
        and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "retain unmodified Python and all six independent engine families",
    )
    assert isinstance(families, list)
    for row, original in zip(families, old["families"], strict=True):
        base.need(
            type(row) is dict and row["family"] == original["family"],
            "reject a missing or fabricated candidate engine family",
        )
        if row["family"] == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "retain every exact byte of the unmodified Python baseline",
            )
            continue
        for key, _, _ in previous.FEATURES:
            base.need(
                base.canonical(row[key]) == base.canonical(original[key]),
                "retain every existing first-party V87 source reference: " + key,
            )
        base.need(
            base.canonical(row[previous.ACTUAL_KEY])
            == base.canonical(original[previous.ACTUAL_KEY]),
            "retain complete actual first-party V20 receipts",
        )
        source = resolve_reference(
            base, source_pool, row.get(SOURCE_KEY),
            SOURCE_REFERENCE_SCHEMA, SOURCE_KEY,
        )
        actual = resolve_reference(
            base, actual_pool, row.get(ACTUAL_KEY),
            ACTUAL_REFERENCE_SCHEMA, ACTUAL_KEY,
        )
        c_source = resolve_reference(
            base, c_source_pool, row.get(C_SOURCE_KEY),
            C_SOURCE_REFERENCE_SCHEMA, C_SOURCE_KEY,
        )
        c_actual = resolve_reference(
            base, c_actual_pool, row.get(C_ACTUAL_KEY),
            C_ACTUAL_REFERENCE_SCHEMA, C_ACTUAL_KEY,
        )
        base.need(
            base.canonical(source) == base.canonical(source_proof)
            and base.canonical(actual) == base.canonical(actual_proof)
            and base.canonical(c_source) == base.canonical(c_source_proof)
            and base.canonical(c_actual) == base.canonical(c_actual_proof)
            and row["authenticated_evidence_owner_lower_bound"] == 309
            and row["authenticated_history_reference_lower_bound"] == 314
            and row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "never mistake a real native build for matching or a winning engine",
        )
        restored = copy.deepcopy(row)
        restored.pop(SOURCE_KEY)
        restored.pop(ACTUAL_KEY)
        restored.pop(C_SOURCE_KEY)
        restored.pop(C_ACTUAL_KEY)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        base.need(
            base.canonical(restored) == base.canonical(original),
            "restore the entire published V87 family: " + row["family"],
        )


def build(
    previous: types.ModuleType,
    v86: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None
        and type(options.source_bytes) is int
        and 0 < options.source_bytes <= OWNER_LIMIT,
        "caller-pin the complete immutable V88 renderer source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "exact whole V88 renderer source"),
        options.source_bytes,
        private=True,
    )
    for role, item in V87.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the exact published V87 " + role,
        )
    for role, item in FEATURE.items():
        base.need(
            getattr(options, "feature_" + role + "_sha256") == item[1],
            "caller-pin the exact independent V21 source " + role,
        )
    for role, item in C_FEATURE.items():
        base.need(
            getattr(options, "c_feature_" + role + "_sha256") == item[1],
            "caller-pin the exact independent C18 source " + role,
        )
    base.need(
        options.build_receipt_sha256 == BUILD_RECEIPT[1]
        and options.root_receipt_sha256 == ROOT_RECEIPT[1]
        and options.c_build_receipt_sha256 == C_BUILD_RECEIPT[1]
        and options.c_root_receipt_sha256 == C_ROOT_RECEIPT[1],
        "caller-pin all four actually published V21 and C18 native-build receipts",
    )
    old, previous_inputs = authenticate_previous(
        previous, v86, v85, v84, v83, v82, chain, base
    )
    contract = load_contract(base)
    source_proof = make_source_proof(base, contract)
    source_pool = make_pool(base, SOURCE_POOL_SCHEMA, SOURCE_KEY, source_proof)
    source_reference = make_reference(
        base, source_pool, SOURCE_REFERENCE_SCHEMA, SOURCE_KEY, source_proof
    )
    build_raw = read_fixed(BUILD_RECEIPT, "whole actual captured V21 build receipt")
    root_raw = read_fixed(ROOT_RECEIPT, "whole actual captured V21 root receipt")
    actual_build = base.document(build_raw, "complete captured V21 build receipt")
    actual_root = base.document(root_raw, "complete captured V21 root receipt")
    validate_receipts(base, actual_build, actual_root)
    actual_proof = make_actual_proof(base, actual_build, actual_root)
    actual_pool = make_pool(base, ACTUAL_POOL_SCHEMA, ACTUAL_KEY, actual_proof)
    actual_reference = make_reference(
        base, actual_pool, ACTUAL_REFERENCE_SCHEMA, ACTUAL_KEY, actual_proof
    )
    c_contract = load_c_contract(base)
    c_source_proof = make_c_source_proof(base, c_contract)
    c_source_pool = make_pool(
        base, C_SOURCE_POOL_SCHEMA, C_SOURCE_KEY, c_source_proof
    )
    c_source_reference = make_reference(
        base, c_source_pool, C_SOURCE_REFERENCE_SCHEMA, C_SOURCE_KEY,
        c_source_proof,
    )
    c_build_raw = read_fixed(C_BUILD_RECEIPT, "whole actual C18 build receipt")
    c_root_raw = read_fixed(C_ROOT_RECEIPT, "whole actual C18 root receipt")
    c_actual_build = base.document(c_build_raw, "complete actual C18 build receipt")
    c_actual_root = base.document(c_root_raw, "complete actual C18 root receipt")
    validate_c_receipts(base, c_actual_build, c_actual_root)
    c_actual_proof = make_c_actual_proof(base, c_actual_build, c_actual_root)
    c_actual_pool = make_pool(
        base, C_ACTUAL_POOL_SCHEMA, C_ACTUAL_KEY, c_actual_proof
    )
    c_actual_reference = make_reference(
        base, c_actual_pool, C_ACTUAL_REFERENCE_SCHEMA, C_ACTUAL_KEY,
        c_actual_proof,
    )
    changes = make_changes(
        source_reference, actual_reference, c_source_reference, c_actual_reference
    )
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V87.items()
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    inputs = copy.deepcopy(previous_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 88,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": predecessor,
        **copy.deepcopy(changes),
    })
    families = copy.deepcopy(old["families"])
    for row in families:
        if row["family"] == "python":
            continue
        row["authenticated_evidence_owner_lower_bound"] = 309
        row["authenticated_history_reference_lower_bound"] = 314
        row[SOURCE_KEY] = copy.deepcopy(source_reference)
        row[ACTUAL_KEY] = copy.deepcopy(actual_reference)
        row[C_SOURCE_KEY] = copy.deepcopy(c_source_reference)
        row[C_ACTUAL_KEY] = copy.deepcopy(c_actual_reference)
    validate_families(
        base, previous, old, families,
        source_pool, source_proof, actual_pool, actual_proof,
        c_source_pool, c_source_proof, c_actual_pool, c_actual_proof,
    )
    inputs_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 88,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(inputs_raw), len(inputs_raw)
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg_raw), len(svg_raw)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        SOURCE_POOL_KEY: source_pool,
        "lossless_v88_captured_source_evidence_pool_entry_count": 1,
        "lossless_v88_captured_source_references_per_family": 1,
        ACTUAL_POOL_KEY: actual_pool,
        "lossless_v88_captured_actual_build_evidence_pool_entry_count": 1,
        "lossless_v88_captured_actual_build_references_per_family": 1,
        C_SOURCE_POOL_KEY: c_source_pool,
        "lossless_v88_c_source_evidence_pool_entry_count": 1,
        "lossless_v88_c_source_references_per_family": 1,
        C_ACTUAL_POOL_KEY: c_actual_pool,
        "lossless_v88_c_actual_build_evidence_pool_entry_count": 1,
        "lossless_v88_c_actual_build_references_per_family": 1,
        "lossless_v87_family_previous_byte_identity_status": "PASS",
        "lossless_v87_all_six_previous_pool_identity_status": "PASS",
        **copy.deepcopy(changes),
    })
    for pool_name in (
        "lossless_family_evidence_pool",
        "lossless_actual_outcome_evidence_pool",
        "lossless_zig_source_evidence_pool",
        "lossless_zig_actual_build_evidence_pool",
        previous.SOURCE_POOL_KEY,
        previous.ACTUAL_POOL_KEY,
    ):
        base.need(
            base.canonical(summary[pool_name]) == base.canonical(old[pool_name]),
            "retain every byte of the whole published V87 pool: " + pool_name,
        )
    for name, layer in (
        ("inputs", inputs), ("snapshot", snapshot), ("summary", summary)
    ):
        base.need(
            layer["actual_rust_semantic_mismatch_count"] == 1440
            and layer["actual_rust_verified_passing_case_count"] == 14853
            and layer["rust_v15_original_campaign_actual_worker_count"] == 13
            and layer["rust_v15_original_campaign_completed_suite_count"] == 8
            and layer["rust_v15_original_campaign_verified_passing_case_count"]
            == 12942
            and layer["rust_v15_original_campaign_infrastructure_failure_count"]
            == 5
            and layer["rust_v15_original_campaign_semantic_mismatch_count"]
            == "NOT MEASURED"
            and layer["actual_c_semantic_mismatch_count"] == 1230
            and layer["actual_c_verified_passing_case_count"] == 7325
            and layer["rust_literal_v20_actual_build_status"] == "PASS"
            and layer["rust_literal_v20_actual_compiler_process_count"] == 28
            and layer["rust_literal_v20_actual_independent_phase_count"] == 2
            and layer["rust_literal_v20_candidate_matching"] == "NOT RUN"
            and layer["rust_captured_findall_variant_build"] == "PASS"
            and layer["rust_captured_v21_actual_build_status"] == "PASS"
            and layer["rust_captured_v21_actual_compiler_process_count"] == 28
            and layer["rust_captured_v21_actual_independent_phase_count"] == 2
            and layer["rust_captured_v21_actual_source_sha256"]
            == CAPTURE_SOURCE_SHA256
            and layer["rust_captured_v21_candidate_matching"] == "NOT RUN"
            and layer["rust_captured_v21_candidate_qualified"] is False
            and layer["c_subject_v18_actual_build_status"] == "PASS"
            and layer["c_subject_v18_actual_compiler_process_count"] == 14
            and layer["c_subject_v18_actual_independent_phase_count"] == 2
            and layer["c_subject_v18_actual_source_sha256"] == C_VARIANT_SHA256
            and layer["c_subject_v18_actual_native_extension_sha256"]
            == C_EXTENSION_SHA256
            and layer["c_subject_v18_candidate_matching"] == "NOT RUN"
            and layer["c_subject_v18_candidate_qualified"] is False
            and layer["expanded_holdout_proposed_case_count"] == 14155776
            and layer["expanded_holdout_final_protocol_status"] == "NOT FROZEN"
            and layer["expanded_holdout_case_status"]
            == "NOT GENERATED; NOT OPENED"
            and layer["preserved_previous_holdout_proposal_case_count"] == 4194304
            and layer["authenticated_evidence_owner_lower_bound"] == 309
            and layer["authenticated_history_reference_lower_bound"] == 314
            and layer["qualified_candidate_count"] == 0
            and layer["performance"] == "NOT MEASURED"
            and layer["final_holdout_opened"] is False,
            "preserve both real builds, true Rust history and closed holdout in " + name,
        )
        observed_source = resolve_reference(
            base, source_pool, layer[SOURCE_KEY],
            SOURCE_REFERENCE_SCHEMA, SOURCE_KEY,
        )
        observed_actual = resolve_reference(
            base, actual_pool, layer[ACTUAL_KEY],
            ACTUAL_REFERENCE_SCHEMA, ACTUAL_KEY,
        )
        observed_c_source = resolve_reference(
            base, c_source_pool, layer[C_SOURCE_KEY],
            C_SOURCE_REFERENCE_SCHEMA, C_SOURCE_KEY,
        )
        observed_c_actual = resolve_reference(
            base, c_actual_pool, layer[C_ACTUAL_KEY],
            C_ACTUAL_REFERENCE_SCHEMA, C_ACTUAL_KEY,
        )
        base.need(
            base.canonical(observed_source) == base.canonical(source_proof)
            and base.canonical(observed_actual) == base.canonical(actual_proof)
            and base.canonical(observed_c_source) == base.canonical(c_source_proof)
            and base.canonical(observed_c_actual) == base.canonical(c_actual_proof),
            "recover complete V21 and C18 source and all actual receipts in " + name,
        )
    summary_raw = base.canonical(summary)
    assets = {
        OUTPUT + ".inputs.json": inputs_raw,
        OUTPUT + ".json": summary_raw,
        OUTPUT + ".svg": svg_raw,
    }
    for path, raw in assets.items():
        base.need(
            type(raw) is bytes
            and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
            "reject oversized whole V88 evidence before any publication: " + path,
        )
    return snapshot, assets


def self_test(
    previous: types.ModuleType,
    v86: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> dict:
    prior = previous.self_test(
        v86, v85, v84, v83, v82, chain, base, previous_options(previous)
    )
    base.need(
        prior["status"] == "PASS"
        and prior["version"] == 87
        and prior["rejected_hostile_control_count"] == 9188
        and prior["authenticated_evidence_owner_lower_bound"] == 299
        and prior["authenticated_history_reference_lower_bound"] == 304
        and prior["lossless_family_evidence_pool_entry_count"] == 9
        and prior["lossless_actual_outcome_evidence_pool_entry_count"] == 1
        and prior["lossless_zig_source_evidence_pool_entry_count"] == 1
        and prior["lossless_zig_actual_build_evidence_pool_entry_count"] == 1
        and prior["lossless_v87_source_evidence_pool_entry_count"] == 6
        and prior["lossless_v87_rust_actual_build_evidence_pool_entry_count"] == 1
        and prior["actual_v15_candidate_worker_count"] == 13
        and prior["actual_v15_completed_suite_count"] == 8
        and prior["actual_v15_verified_passing_case_count"] == 12942
        and prior["actual_v15_infrastructure_failure_count"] == 5
        and prior["actual_v20_build_status"] == "PASS"
        and prior["actual_v20_compiler_process_count"] == 28
        and prior["actual_v20_independent_phase_count"] == 2
        and prior["actual_v20_candidate_matching"] == "NOT RUN"
        and prior["qualified_candidate_count"] == 0
        and prior["performance"] == "NOT MEASURED"
        and prior["outputs_written"] is False,
        "retain all 9,188 independently rejected V87 controls and true results",
    )
    _, assets = build(
        previous, v86, v85, v84, v83, v82, chain, base, options
    )
    summary = base.document(assets[OUTPUT + ".json"], "whole in-memory V88")
    source_contract = load_contract(base)
    source_pool = summary[SOURCE_POOL_KEY]
    actual_pool = summary[ACTUAL_POOL_KEY]
    c_source_contract = load_c_contract(base)
    c_source_pool = summary[C_SOURCE_POOL_KEY]
    c_actual_pool = summary[C_ACTUAL_POOL_KEY]
    actual_build = base.document(
        read_fixed(BUILD_RECEIPT, "whole V21 self-test build receipt"),
        "whole V21 actual self-test build receipt",
    )
    actual_root = base.document(
        read_fixed(ROOT_RECEIPT, "whole V21 self-test provenance receipt"),
        "whole V21 actual self-test root receipt",
    )
    c_actual_build = base.document(
        read_fixed(C_BUILD_RECEIPT, "whole C18 self-test build receipt"),
        "whole C18 actual self-test build receipt",
    )
    c_actual_root = base.document(
        read_fixed(C_ROOT_RECEIPT, "whole C18 self-test provenance receipt"),
        "whole C18 actual self-test root receipt",
    )
    source_proof = make_source_proof(base, source_contract)
    actual_proof = make_actual_proof(base, actual_build, actual_root)
    c_source_proof = make_c_source_proof(base, c_source_contract)
    c_actual_proof = make_c_actual_proof(base, c_actual_build, c_actual_root)
    rejected = 0

    def reject(label: str, callback: object) -> None:
        nonlocal rejected
        try:
            assert callable(callback)
            callback()
        except Exception:
            rejected += 1
        else:
            base.need(False, "V88 accepted fabricated source/build evidence: " + label)

    for key in sorted(source_contract):
        forged = copy.deepcopy(source_contract)
        forged.pop(key)
        expected = make_source_proof(base, forged)
        reject(
            "omitted complete captured source contract field " + key,
            lambda value=expected: validate_pool(
                base, source_pool, SOURCE_POOL_SCHEMA, SOURCE_KEY, value
            ),
        )
    for key in sorted(c_source_contract):
        forged = copy.deepcopy(c_source_contract)
        forged.pop(key)
        expected = make_c_source_proof(base, forged)
        reject(
            "omitted complete C18 source contract field " + key,
            lambda value=expected: validate_pool(
                base, c_source_pool, C_SOURCE_POOL_SCHEMA, C_SOURCE_KEY, value
            ),
        )
    for label, genuine, other in (
        ("build", actual_build, actual_root),
        ("root", actual_root, actual_build),
    ):
        for key in sorted(genuine):
            forged = copy.deepcopy(genuine)
            forged.pop(key)
            reject(
                "omitted exact V21 " + label + " receipt field " + key,
                lambda value=forged, name=label, remaining=other:
                validate_receipts(
                    base,
                    value if name == "build" else remaining,
                    value if name == "root" else remaining,
                ),
            )
        for key, wrong in (
            ("status", "FAIL"),
            ("source_sha256", "0" * 64),
            ("protocol_sha256", "0" * 64),
            ("contract_sha256", "0" * 64),
            ("actual_compiler_process_count", 27),
            ("candidate_matching", "PASS"),
            ("candidate_qualified", True),
            ("candidate_workers_started", 1),
            ("native_libraries_loaded", 1),
            ("clock_samples", 1),
            ("holdout", "OPENED"),
            ("performance", "1.5x"),
            ("winner_selected", True),
        ):
            forged = copy.deepcopy(genuine)
            forged[key] = wrong
            reject(
                "fabricated actual V21 " + label + ":" + key,
                lambda value=forged, name=label, remaining=other:
                validate_receipts(
                    base,
                    value if name == "build" else remaining,
                    value if name == "root" else remaining,
                ),
            )
    for label, genuine, other in (
        ("build", c_actual_build, c_actual_root),
        ("root", c_actual_root, c_actual_build),
    ):
        for key in sorted(genuine):
            forged = copy.deepcopy(genuine)
            forged.pop(key)
            reject(
                "omitted exact C18 " + label + " receipt field " + key,
                lambda value=forged, name=label, remaining=other:
                validate_c_receipts(
                    base,
                    value if name == "build" else remaining,
                    value if name == "root" else remaining,
                ),
            )
        for key, wrong in (
            ("status", "FAIL"),
            ("family", "rust"),
            ("source_sha256", "0" * 64),
            ("protocol_sha256", "0" * 64),
            ("contract_sha256", "0" * 64),
            ("actual_compiler_process_count", 28),
            ("expected_compiler_process_count", 28),
            ("historical_c_semantic_mismatch_count", 0),
            ("historical_c_verified_passing_case_count", 7324),
            ("current_rust_completed_suite_count", 13),
            ("current_rust_verified_passing_case_count", 14853),
            ("candidate_matching", "PASS"),
            ("native_libraries_loaded", 1),
            ("clock_samples", 1),
            ("holdout", "OPENED"),
            ("performance", "1.5x"),
            ("runtime_non_delegation", "PASS"),
            ("winner_selected", True),
        ):
            forged = copy.deepcopy(genuine)
            forged[key] = wrong
            reject(
                "fabricated actual C18 " + label + ":" + key,
                lambda value=forged, name=label, remaining=other:
                validate_c_receipts(
                    base,
                    value if name == "build" else remaining,
                    value if name == "root" else remaining,
                ),
            )
    for key, wrong in (
        ("actual_source_phase_count", 1),
        ("candidate_qualified", True),
        ("candidate_workers_started", 1),
        ("canonical_build_receipt_sha256", BUILD_RECEIPT[1]),
        ("canonical_build_archive_opened", True),
        ("distinct_actual_native_extension_count", 1),
    ):
        forged = copy.deepcopy(c_actual_root)
        forged[key] = wrong
        reject(
            "fabricated C18 root provenance:" + key,
            lambda value=forged: validate_c_receipts(base, c_actual_build, value),
        )
    for key, wrong in (
        ("build_status", "FAIL"),
        ("variant_source_sha256", CAPTURE_SOURCE_SHA256),
        ("variant_source_bytes", 179520),
        ("qualified_candidate_count", 1),
        ("timing_trials_run", 1),
    ):
        forged = copy.deepcopy(c_actual_build)
        forged[key] = wrong
        reject(
            "fabricated C18 actual publication:" + key,
            lambda value=forged: validate_c_receipts(base, value, c_actual_root),
        )
    for index, role in ((0, "native"), (1, "native"), (0, "variant"), (1, "adapter")):
        forged = copy.deepcopy(c_actual_root)
        phase = forged["root"]["phases"][index]
        if role == "native":
            phase["native_output"]["sha256"] = ENGINE_SHA256
        else:
            for owner in phase["source_owners"]:
                if owner["role"] == role:
                    owner["sha256"] = "0" * 64
        reject(
            "fabricated C18 phase " + str(index) + ":" + role,
            lambda value=forged: validate_c_receipts(base, c_actual_build, value),
        )
    for key, pool, schema, proof in (
        (SOURCE_KEY, source_pool, SOURCE_REFERENCE_SCHEMA, source_proof),
        (ACTUAL_KEY, actual_pool, ACTUAL_REFERENCE_SCHEMA, actual_proof),
        (C_SOURCE_KEY, c_source_pool, C_SOURCE_REFERENCE_SCHEMA, c_source_proof),
        (C_ACTUAL_KEY, c_actual_pool, C_ACTUAL_REFERENCE_SCHEMA, c_actual_proof),
    ):
        reference = summary[key]
        for field, wrong in (
            ("schema", "invented-proof"),
            ("proof_key", "external-regex"),
            ("sha256", "0" * 64),
            ("canonical_bytes", 1),
        ):
            forged = copy.deepcopy(reference)
            forged[field] = wrong
            reject(
                "forged full V21 reference " + key + ":" + field,
                lambda value=forged, candidate=pool, role=key, kind=schema:
                resolve_reference(base, candidate, value, kind, role),
            )
        genuine = resolve_reference(base, pool, reference, schema, key)
        base.need(
            base.canonical(genuine) == base.canonical(proof),
            "reconstruct the authentic complete V88 proof: " + key,
        )
    old, _ = authenticate_previous(
        previous, v86, v85, v84, v83, v82, chain, base
    )
    for index, row in enumerate(summary["families"]):
        if row["family"] == "python":
            continue
        for key, wrong in (
            ("qualified", True),
            ("runtime_no_delegation", "PASS"),
            ("performance", "1.5x"),
            ("authenticated_evidence_owner_lower_bound", 308),
            ("authenticated_history_reference_lower_bound", 315),
        ):
            forged_families = copy.deepcopy(summary["families"])
            forged_families[index][key] = wrong
            reject(
                "invented qualifying family " + row["family"] + ":" + key,
                lambda value=forged_families: validate_families(
                    base, previous, old, value,
                    source_pool, source_proof, actual_pool, actual_proof,
                    c_source_pool, c_source_proof, c_actual_pool, c_actual_proof,
                ),
            )
    for event, arguments in (
        ("open", (str(ROOT / "hidden.gz"), "rb", os.O_RDONLY)),
        ("open", (ARCHIVE_PATH, "rb", os.O_RDONLY)),
        ("open", (C_ARCHIVE_PATH, "rb", os.O_RDONLY)),
        ("open", ("/tmp/rebar-private-root", "rb", os.O_RDONLY)),
        ("open", (str(ROOT / (OUTPUT + ".json")), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / "safe.json"), "wb", os.O_WRONLY | os.O_CREAT)),
        ("subprocess.Popen", ("candidate",)),
        ("ctypes.dlopen", ("foreign-regex.so",)),
        ("socket.connect", ("example.invalid",)),
        ("import", ("regex", None, None, None, None)),
        ("import", ("ctypes", None, None, None, None)),
        ("import", ("time", None, None, None, None)),
    ):
        reject(
            "forbidden V88 source-only effect " + event,
            lambda name=event, values=arguments: audit_wall(name, values),
        )
    base.need(rejected >= 350, "require complete hostile Rust and C native-build controls")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 88,
        "status": "PASS",
        "source_sha256": options.source_sha256,
        "source_bytes": options.source_bytes,
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ] + rejected,
        "inputs_sha256": base.digest(assets[OUTPUT + ".inputs.json"]),
        "inputs_bytes": len(assets[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(assets[OUTPUT + ".json"]),
        "summary_bytes": len(assets[OUTPUT + ".json"]),
        "svg_sha256": base.digest(assets[OUTPUT + ".svg"]),
        "svg_bytes": len(assets[OUTPUT + ".svg"]),
        "authenticated_evidence_owner_lower_bound": 309,
        "authenticated_history_reference_lower_bound": 314,
        "lossless_family_evidence_pool_entry_count": 9,
        "lossless_actual_outcome_evidence_pool_entry_count": 1,
        "lossless_zig_source_evidence_pool_entry_count": 1,
        "lossless_zig_actual_build_evidence_pool_entry_count": 1,
        "lossless_v87_source_evidence_pool_entry_count": 6,
        "lossless_v87_rust_actual_build_evidence_pool_entry_count": 1,
        "lossless_v88_captured_source_evidence_pool_entry_count": 1,
        "lossless_v88_captured_actual_build_evidence_pool_entry_count": 1,
        "lossless_v88_c_source_evidence_pool_entry_count": 1,
        "lossless_v88_c_actual_build_evidence_pool_entry_count": 1,
        "lossless_v87_all_six_previous_pool_identity_status": "PASS",
        "actual_historical_complete_rust_semantic_mismatch_count": 1440,
        "actual_historical_complete_rust_verified_passing_case_count": 14853,
        "actual_historical_c_semantic_mismatch_count": 1230,
        "actual_historical_c_verified_passing_case_count": 7325,
        "actual_v15_candidate_worker_count": 13,
        "actual_v15_completed_suite_count": 8,
        "actual_v15_verified_passing_case_count": 12942,
        "actual_v15_infrastructure_failure_count": 5,
        "actual_v20_build_status": "PASS",
        "actual_v20_compiler_process_count": 28,
        "actual_v20_independent_phase_count": 2,
        "actual_v21_captured_build_status": "PASS",
        "actual_v21_captured_compiler_process_count": 28,
        "actual_v21_captured_independent_phase_count": 2,
        "actual_v21_captured_source_sha256": CAPTURE_SOURCE_SHA256,
        "actual_v21_captured_candidate_matching": "NOT RUN",
        "actual_v18_c_build_status": "PASS",
        "actual_v18_c_compiler_process_count": 14,
        "actual_v18_c_independent_phase_count": 2,
        "actual_v18_c_subject_source_sha256": C_VARIANT_SHA256,
        "actual_v18_c_native_extension_sha256": C_EXTENSION_SHA256,
        "actual_v18_c_candidate_matching": "NOT RUN",
        "expanded_holdout_proposed_case_count": 14155776,
        "preserved_previous_holdout_proposal_case_count": 4194304,
        "expanded_holdout_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "compressed_archives_opened_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "clock_samples_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "winner_selected": False,
        "outputs_written": False,
    }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
        and type(raw) is bytes
        and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
        "publish only an explicitly authorized, exclusive bounded V88 output",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0, "write all V88 output bytes")
            remaining = remaining[count:]
        os.fsync(handle)
        actual = os.fstat(handle)
        base.need(
            actual.st_uid == os.geteuid()
            and actual.st_dev == 2064
            and actual.st_nlink == 1
            and actual.st_size == len(raw)
            and stat.S_IMODE(actual.st_mode) == 0o600,
            "authenticate every complete and exclusively published V88 owner",
        )
    finally:
        os.close(handle)
    directory = os.open(
        str(ROOT / "docs/evidence"),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    actual, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(actual == raw, "reauthenticate the complete final V88 evidence")


def parse(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for role in V87:
        parser.add_argument("--previous-" + role + "-sha256", required=True)
    for role in FEATURE:
        parser.add_argument("--feature-" + role + "-sha256", required=True)
    for role in C_FEATURE:
        parser.add_argument("--c-feature-" + role + "-sha256", required=True)
    parser.add_argument("--build-receipt-sha256", required=True)
    parser.add_argument("--root-receipt-sha256", required=True)
    parser.add_argument("--c-build-receipt-sha256", required=True)
    parser.add_argument("--c-root-receipt-sha256", required=True)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse(arguments)
    try:
        previous, v86, v85, v84, v83, v82, chain, base = load_previous()
        if not options.render:
            sys.addaudithook(audit_wall)
        if options.self_test:
            result = self_test(
                previous, v86, v85, v84, v83, v82, chain, base, options
            )
        else:
            snapshot, assets = build(
                previous, v86, v85, v84, v83, v82, chain, base, options
            )
            if options.render:
                for path, raw in assets.items():
                    publish(base, path, raw)
            result = {
                "schema": SCHEMA + (
                    "-published" if options.render else "-source-only-frozen-context"
                ),
                "version": 88,
                "status": "PASS",
                "source_sha256": options.source_sha256,
                "source_bytes": options.source_bytes,
                "inputs_sha256": base.digest(assets[OUTPUT + ".inputs.json"]),
                "inputs_bytes": len(assets[OUTPUT + ".inputs.json"]),
                "summary_sha256": base.digest(assets[OUTPUT + ".json"]),
                "summary_bytes": len(assets[OUTPUT + ".json"]),
                "svg_sha256": base.digest(assets[OUTPUT + ".svg"]),
                "svg_bytes": len(assets[OUTPUT + ".svg"]),
                "authenticated_evidence_owner_lower_bound": 309,
                "authenticated_history_reference_lower_bound": 314,
                "lossless_family_evidence_pool_entry_count": 9,
                "lossless_actual_outcome_evidence_pool_entry_count": 1,
                "lossless_zig_source_evidence_pool_entry_count": 1,
                "lossless_zig_actual_build_evidence_pool_entry_count": 1,
                "lossless_v87_source_evidence_pool_entry_count": 6,
                "lossless_v87_rust_actual_build_evidence_pool_entry_count": 1,
                "lossless_v88_captured_source_evidence_pool_entry_count": 1,
                "lossless_v88_captured_actual_build_evidence_pool_entry_count": 1,
                "lossless_v88_c_source_evidence_pool_entry_count": 1,
                "lossless_v88_c_actual_build_evidence_pool_entry_count": 1,
                "lossless_v87_all_six_previous_pool_identity_status": "PASS",
                "actual_historical_complete_rust_semantic_mismatch_count": 1440,
                "actual_historical_complete_rust_verified_passing_case_count": 14853,
                "actual_historical_c_semantic_mismatch_count": 1230,
                "actual_historical_c_verified_passing_case_count": 7325,
                "actual_v15_candidate_worker_count": 13,
                "actual_v15_completed_suite_count": 8,
                "actual_v15_verified_passing_case_count": 12942,
                "actual_v15_infrastructure_failure_count": 5,
                "actual_v20_build_status": "PASS",
                "actual_v20_compiler_process_count": 28,
                "actual_v20_independent_phase_count": 2,
                "actual_v21_captured_build_status": "PASS",
                "actual_v21_captured_compiler_process_count": 28,
                "actual_v21_captured_independent_phase_count": 2,
                "actual_v21_captured_source_sha256": CAPTURE_SOURCE_SHA256,
                "actual_v21_captured_candidate_matching": "NOT RUN",
                "actual_v18_c_build_status": "PASS",
                "actual_v18_c_compiler_process_count": 14,
                "actual_v18_c_independent_phase_count": 2,
                "actual_v18_c_subject_source_sha256": C_VARIANT_SHA256,
                "actual_v18_c_native_extension_sha256": C_EXTENSION_SHA256,
                "actual_v18_c_candidate_matching": "NOT RUN",
                "expanded_holdout_proposed_case_count": 14155776,
                "preserved_previous_holdout_proposal_case_count": 4194304,
                "expanded_holdout_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
                "compressed_archives_opened_by_graph": 0,
                "private_build_roots_opened_by_graph": 0,
                "candidate_workers_started_by_graph": 0,
                "compiler_processes_started_by_graph": 0,
                "clock_samples_by_graph": 0,
                "hidden_cases_read_by_graph": 0,
                "qualified_candidate_count": 0,
                "performance": "NOT MEASURED",
                "winner_selected": False,
                "outputs_written": bool(options.render),
                "snapshot_holdout_case_count": snapshot[
                    "expanded_holdout_proposed_case_count"
                ],
            }
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V88 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
