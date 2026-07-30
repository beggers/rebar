#!/usr/bin/env python3
"""Reproduce honest, baseline-relative progress without running a regex engine."""

from __future__ import annotations

import _io
import argparse
import copy
import hashlib
import io
import os
from pathlib import Path
import stat
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v96.py"
OUTPUT = "docs/evidence/candidate-current-overview-v96"
INPUT_PATH = OUTPUT + ".inputs.json"
SUMMARY_PATH = OUTPUT + ".summary.json"
SVG_PATH = OUTPUT + ".svg"
SCHEMA = "rebar-candidate-current-overview-v96"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
OWNER_LIMIT = 4 * 1024 * 1024
CASE_COUNT = 31237
SUPPLEMENTAL_CASE_COUNT = 8244
HOLDOUT_PROPOSAL_COUNT = 14155776
HISTORICAL_HOLDOUT_PROPOSAL_COUNT = 4194304
EVIDENCE_FLOOR = 344
HISTORY_FLOOR = 349

V95 = {
    "source": (
        "tools/render_candidate_current_overview_v95.py",
        "a0aee36be3b6d12bd00dfa53fa249bcadd5710745eb5d84d6a3e781cf289b3db",
        112368,
        431101,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v95.inputs.json",
        "1cc29cf050596470ea80149fb55a73090823fb8ee7b1944657ab79d14c011cd6",
        22847,
        431104,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v95.summary.json",
        "50b7347a0421982d0b3bdd922e62d5afce167af0939e3e8745f8bb5c238ff47f",
        3877390,
        431113,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v95.svg",
        "03a9e03e495fb4ec8362150f02072a4828e13e5f049af430042c435370c6808d",
        9848,
        431114,
    ),
}

C_SOURCE = {
    "source": (
        "tools/run_owned_repaired_c_original_campaign_v10.py",
        "ad8b8451847b3e5c566c141e829bdf6eecea8ae9f502b608288449022c83c790",
        50278,
        430925,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V10.md",
        "ba673181c02daf3a572e3569283a5a4c490ed04e7cd76927e3f2fe1430630179",
        5941,
        525204,
    ),
    "contract": (
        "oracle/phase2/repaired-c-original-campaign-v10.json",
        "2aad4885fe80b93f61f59c28ed6969fbcf16dda0b8a3457c71b449a9972bb595",
        44516,
        525205,
    ),
}

C_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v10-c-phase2-v21-c-original-match-"
    "semantics-original-p0-v10-failures-publication-receipt.json",
    "c5c85f828da7e960c90a23b1eb4d74c30a671d030de04ef61b0e4d00d7e5433a",
    7247,
    525475,
)

ZIG14_SOURCE = {
    "source": (
        "tools/run_owned_repaired_zig_original_campaign_v14.py",
        "8757ff2fdda5e8e60ee694b0d803018ddf33ea7266b8d7a5eff6d52d0866569d",
        49601,
        431103,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V14.md",
        "691ab654b88ed30f6cd0729d987415162708fdfb90c36d91bf41dcefdbb5fcef",
        7539,
        525386,
    ),
    "contract": (
        "oracle/phase2/repaired-zig-original-campaign-v14.json",
        "1c7326dc2f63635f3e32ec0558b51f21c952d51480f336e3b0d4d49e38428a0a",
        31103,
        525387,
    ),
}

ZIG14_RECEIPT = (
    "oracle/phase2/evidence/"
    "zig-original-campaign-v14-setter-safe-prepublication-controller-failure.json",
    "2d1bad717e782b7ed3e0af856f8687e9a29abc93ebf1553adc6d65f668aa5c65",
    5474,
    525461,
)

SUITES = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912),
    ("substitution_v2", 5120),
    ("shape_v2", 10240),
    ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)

C_WORKER_PIDS = (83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 189, 190, 191)
C_ROW_SHA256 = {
    "original_bounded_v5": "991219c87a900605e88afcee2c85c6689faead5250589423b96c833a7cf2f1df",
    "public_v3": "55d03bda8b15be9160fa9600d7a2313044a306f16595fcac1ba73ab8bf7dc8cb",
    "scanner_v3": "ae85fb4b312340faa649401e9f918a892398a92fbe138cec7acd456c39bceb7b",
    "buffer_v3": "c45c434e945eae34d0ac77bd37b8e2e7246055432ca5c0945298942315c8a016",
    "managed_v1": "6cc0d194fbdf74e874c21b2811b2c3c92768adf2083fd90019df74eac2b65be6",
    "scanner_verbose_v1": "ff42792d8af519c8b04f22845bcaa3be3d6f7e477dcdb57a46f0ba18dde6d4fe",
    "public_types_v1": "5d84fb9cbcf151bbe94738f814893139ba5919afa4d642198092eccb12bd1c91",
    "substitution_v2": "6f6e43ee29050055d8afd02bd48a19c2e7aa574237789d55e5734ad5e0a75f13",
    "shape_v2": "d56668085f509da0a37f98a9ecaff072c0b56199049df8158393e09366a53ef2",
    "public_surface_v19": "8c91a8b288ad8bead58a8ebe273019768227570279f6a7012bd862840bddcf20",
    "subinterpreter_v2": "6e61d4d8107b40c78a86324790b838bda0d575a45d44a151856482de5c7eb136",
    "pep688_v4": "274f21b0a8f056a3238c59373567ef46678162768bbcd8e121a014afc90e105f",
    "threaded_pattern_v1": "226234a0ab6f4aa34e2dc230c6d811abcacd8d771f0376587ee66a78e228fb5d",
}
C_MISMATCHES = {
    "managed_v1": 16,
    "public_types_v1": 248,
    "substitution_v2": 224,
    "public_surface_v19": 114,
    "pep688_v4": 4,
}
C_FAILURES = frozenset({
    "original_bounded_v5",
    "public_v3",
    "scanner_v3",
    "buffer_v3",
    "subinterpreter_v2",
})
C_ROW_KEYS = frozenset({
    "actual_candidate_workers",
    "case_execution_denominator",
    "error_type",
    "failure_class",
    "failure_phase",
    "mismatch_count",
    "plain_failure_diagnostic",
    "status",
    "suite",
    "worker_process_id",
})

V95_RUST_POOL = (
    "lossless_v95_rust_v22_original_campaign_evidence_pool",
    138081,
    "7b32e4d599c2a6d8e0f44cead35b5732f32da47b75eb5308b4b26094d8503690",
    1,
)
V95_SNAPSHOT_SHA256 = (
    "165c181bedde4e252f680b950a50cd2ff60fe06cae4d90eb25a5b16385d238d0"
)
V95_SNAPSHOT_BYTES = 14985

POOL_KEY = "lossless_v96_c_v10_and_zig_v14_public_evidence_pool"
POOL_SCHEMA = SCHEMA + "-lossless-complete-public-campaign-pool-v1"
C_ENTRY_SCHEMA = SCHEMA + "-lossless-complete-c-original-campaign-entry-v1"
ZIG_ENTRY_SCHEMA = SCHEMA + "-lossless-complete-zig-controller-failure-entry-v1"
REFERENCE_SCHEMA = SCHEMA + "-complete-public-evidence-reference-v1"
C_LATEST_KEY = "c_v10_actual_original_campaign"
ZIG_CONTROLLER_KEY = "zig_v14_actual_prepublication_controller_failure"

C_CONTRACT_KEYS = frozenset({
    "actual_first_party_c21_build",
    "actual_operation_policy",
    "authenticated_complete_v9_controller_transform",
    "authenticated_cumulative_controller_transform",
    "candidate_correctness",
    "candidate_qualification",
    "expanded_holdout",
    "family",
    "first_party_match_semantics",
    "frozen_original_producer",
    "goal_sha256",
    "holdout",
    "label",
    "memory",
    "original_reference_manifest_v1",
    "performance",
    "phase",
    "phase_one_v4",
    "pinned_cpython",
    "preserved_actual_c_v6_campaign",
    "preserved_actual_c_v7_campaign",
    "preserved_actual_c_v9_campaign",
    "preserved_full_v8_reporting_freeze",
    "preserved_full_v9_reporting_freeze",
    "protocol",
    "public_surface_digest_provenance_repair",
    "qualified_candidate_count",
    "runtime_non_delegation",
    "schema",
    "source",
    "source_only_effects",
    "source_wall",
    "status",
    "status_scope",
    "strict_runtime_guard",
    "strict_runtime_guard_v3",
    "supplemental_candidate_correctness",
    "undefined_behavior",
    "version",
    "winner_selected",
})

C_RECEIPT_KEYS = frozenset({
    "actual_c21_build_receipt_sha256",
    "actual_c21_root_receipt_sha256",
    "actual_candidate_workers",
    "actual_worker_process_ids",
    "actual_worker_process_ids_are_distinct",
    "archive",
    "attempted_suite_count",
    "benchmark_files_read",
    "candidate_execution_failure_count",
    "candidate_qualified",
    "candidate_status",
    "case_execution_denominator",
    "clock_samples",
    "completed_suite_count",
    "contract_sha256",
    "corrected_source_sha256",
    "expanded_holdout_proposed_case_count",
    "family",
    "hidden_cases_read",
    "holdout",
    "infrastructure_failure_count",
    "label",
    "memory",
    "named_private_waiver_count",
    "native_bridge_sha256",
    "native_engine_sha256",
    "observed_semantic_mismatch_lower_bound",
    "original_native_inode_restored",
    "original_source_targets_modified",
    "performance",
    "preserved_actual_v6_failure_receipt_sha256",
    "preserved_actual_v7_failure_receipt_sha256",
    "protocol_sha256",
    "publication_pass_means",
    "publication_status",
    "schema",
    "semantic_mismatch_count",
    "separate_reference_case_count",
    "separate_reference_cases_counted_as_candidate_cases",
    "source_sha256",
    "status",
    "suite_count",
    "suite_outcomes",
    "timing_trials_run",
    "unchanged_adapter_sha256",
    "uncompressed_bytes",
    "uncompressed_sha256",
    "undefined_behavior",
    "verified_passing_case_count",
    "version",
    "winner_selected",
    "worker_timeout_count",
    "worker_timeout_seconds",
})

ZIG_CONTRACT_KEYS = frozenset({
    "complete_actual_v13_publication",
    "corrected_original_matching",
    "corrected_subinterpreter",
    "corrected_supplemental_matching",
    "corrected_warning",
    "current_qualified_candidates",
    "expanded_sealed_holdout_proposal",
    "family",
    "first_party_in_memory_setter_safe_adapter",
    "future_actual_run",
    "goal",
    "holdout",
    "holdout_case_count",
    "holdout_case_status",
    "immutable_v5_original_producer",
    "independently_frozen_setter_v2",
    "label",
    "memory",
    "minimum_qualified_candidates",
    "original_oracle",
    "performance",
    "physical_source_wall",
    "pinned_cpython",
    "protocol",
    "pushed_v13_original_campaign",
    "pushed_v3_real_interpreter_guard",
    "qualified_candidate_count",
    "runtime_non_delegation",
    "schema",
    "source",
    "source_only_effects",
    "source_only_worker_transport",
    "status",
    "undefined_behavior",
    "version",
    "winner_selected",
})

ZIG_RECEIPT_KEYS = frozenset({
    "actual_candidate_worker_count",
    "actual_completed_suite_count",
    "actual_semantic_mismatch_count",
    "actual_verified_passing_case_count",
    "all_three_original_targets_restored",
    "attempt_count",
    "candidate_process_exit_code",
    "candidate_status",
    "complete_captured_standard_error",
    "complete_captured_standard_output",
    "contract_sha256",
    "controller_error_message",
    "controller_error_type",
    "corrected_finalizer_warning_count",
    "expanded_holdout_proposed_case_count",
    "failure_archive_created",
    "failure_receipt_created",
    "failure_stage",
    "family",
    "frozen_authority",
    "historical_v13_observed_semantic_mismatch_lower_bound",
    "historical_v13_verified_passing_case_count",
    "historical_v13_warning_worker_count",
    "holdout",
    "label",
    "memory",
    "original_case_execution_denominator",
    "original_suite_count",
    "performance",
    "pipeline_exit_code",
    "protocol_sha256",
    "qualified_candidate_count",
    "recovery_root_created",
    "required_locale_path",
    "required_locale_path_verified_before_run",
    "restored_original_targets",
    "schema",
    "source_sha256",
    "status",
    "success_archive_created",
    "success_receipt_created",
    "undefined_behavior",
    "winner_selected",
})

FORBIDDEN_EVENTS = frozenset({
    "subprocess.Popen",
    "os.system",
    "os.posix_spawn",
    "os.posix_spawnp",
    "os.fork",
    "os.forkpty",
    "ctypes.dlopen",
    "ctypes.dlsym",
    "socket.__new__",
    "socket.connect",
    "socket.bind",
    "socket.sendto",
    "os.remove",
    "os.rename",
    "os.rmdir",
    "os.mkdir",
})
FORBIDDEN_IMPORTS = frozenset({
    "regex",
    "re",
    "_sre",
    "ctypes",
    "subprocess",
    "multiprocessing",
    "socket",
    "time",
    "gzip",
    "bz2",
    "lzma",
    "tarfile",
    "zipfile",
    "candidates",
    "rebar",
})
ORIGINAL_OS_WRITE = os.write
ORIGINAL_OS_WRITEV = getattr(os, "writev", None)
ORIGINAL_FILEIO = _io.FileIO


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    if not (type(size) is int and 0 < size <= OWNER_LIMIT):
        raise ValueError("reject an unbounded V96 plaintext owner: " + label)
    if (
        not isinstance(relative, str)
        or relative.startswith("/")
        or ".." in relative.split("/")
        or relative.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
    ):
        raise ValueError("reject a private, native, or compressed V96 owner")
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
            raise ValueError("reject substituted complete V96 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated complete V96 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject extended complete V96 owner: " + label)
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
            raise ValueError("reject changed complete V96 owner: " + label)
        return raw
    finally:
        os.close(handle)


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_EVENTS:
        raise ValueError("V96 source-only operation rejected " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if isinstance(name, str) and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise ValueError("V96 source-only import rejected " + name)
        return
    if event != "open":
        return
    if len(arguments) < 3:
        raise ValueError("V96 rejected an unauthenticated file open")
    path, mode, flags = arguments[:3]
    if not isinstance(path, str) or not isinstance(flags, int):
        raise ValueError("V96 rejected inherited descriptors and unknown owners")
    if mode not in (None, "r", "rb"):
        raise ValueError("V96 source-only operation cannot open writable files")
    if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
        os.O_CREAT | os.O_TRUNC | os.O_APPEND
    ):
        raise ValueError("V96 source-only operation cannot create or change files")
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        if normalized != str(ROOT) and not normalized.startswith(str(ROOT) + "/"):
            raise ValueError("V96 rejected a private root or unopened holdout")
    elif "/" in normalized or normalized in (".", ".."):
        raise ValueError("V96 rejected an escaped relative evidence owner")
    if (
        normalized.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
        or "candidate-current-overview-v96." in normalized
        or "/.git/" in normalized
        or "/__pycache__/" in normalized
        or "/performance/" in normalized
        or "/experiments/" in normalized
        or "/holdout/" in normalized
    ):
        raise ValueError("V96 rejected graph output, archive, native, or holdout")


def reject_descriptor_write(*arguments: object, **keywords: object) -> int:
    raise ValueError("V96 source-only operation rejected direct descriptor writing")


def guarded_fileio(
    file: object,
    mode: str = "r",
    closefd: bool = True,
    opener: object = None,
) -> object:
    if (
        type(file) is int
        or not isinstance(mode, str)
        or any(flag in mode for flag in ("w", "a", "x", "+"))
        or opener is not None
    ):
        raise ValueError("V96 source-only operation rejected direct _io writing")
    return ORIGINAL_FILEIO(file, mode, closefd)


def install_source_wall() -> None:
    sys.addaudithook(audit_wall)
    os.write = reject_descriptor_write
    if ORIGINAL_OS_WRITEV is not None:
        os.writev = reject_descriptor_write
    _io.FileIO = guarded_fileio
    io.FileIO = guarded_fileio


def load_previous() -> tuple[types.ModuleType, tuple, types.ModuleType]:
    raw = read_fixed(V95["source"], "whole committed V95 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v95")
    previous.__file__ = str(ROOT / V95["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    chain = previous.load_previous()
    base = chain[-1]
    base.runtime()
    base.need(
        os.path.realpath(sys.executable) == PYTHON
        and sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and previous.SCHEMA == "rebar-candidate-current-overview-v95"
        and previous.SELF == V95["source"][0]
        and tuple(previous.SUITES) == SUITES
        and len(SUITES) == 13
        and sum(count for _, count in SUITES) == CASE_COUNT
        and len(chain) == 3,
        "require isolated official Python, exact V95 history, and all original cases",
    )
    return previous, chain, base


def previous_options(previous: types.ModuleType) -> argparse.Namespace:
    pins: dict[str, object] = {
        "source_sha256": V95["source"][1],
        "source_bytes": V95["source"][2],
        "rust_receipt_sha256": previous.RUST_RECEIPT[1],
    }
    for role, item in previous.V94.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.RUST_SOURCE.items():
        pins["rust_" + role + "_sha256"] = item[1]
    return argparse.Namespace(**pins)


def previous_pools(previous: types.ModuleType, chain: tuple) -> tuple:
    pools = tuple(previous.previous_pools(chain[0], chain[1])) + (V95_RUST_POOL,)
    if len(pools) != 17 or len({item[0] for item in pools}) != 17:
        raise ValueError("require all seventeen exact complete V95 evidence pools")
    return pools


def validate_previous(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    value: object,
) -> dict:
    base.need(
        type(value) is dict
        and value.get("schema") == "rebar-candidate-current-overview-v95-summary"
        and value.get("version") == 95
        and value.get("status") == "PASS"
        and value.get("authenticated_evidence_owner_lower_bound") == 336
        and value.get("authenticated_history_reference_lower_bound") == 341
        and value.get("original_case_execution_denominator") == CASE_COUNT
        and value.get("original_suite_count") == 13
        and value.get("named_private_waiver_count") == 13
        and value.get("separate_additional_reference_case_count")
        == SUPPLEMENTAL_CASE_COUNT
        and value.get("additional_cases_included_in_original_denominator") is False
        and value.get("qualified_candidate_count") == 0
        and value.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("memory") == "NOT MEASURED"
        and value.get("undefined_behavior") == "NOT MEASURED"
        and value.get("expanded_holdout_proposed_case_count") == HOLDOUT_PROPOSAL_COUNT
        and value.get("preserved_previous_holdout_proposal_case_count")
        == HISTORICAL_HOLDOUT_PROPOSAL_COUNT
        and value.get("expanded_holdout_final_protocol_status") == "NOT FROZEN"
        and value.get("expanded_holdout_case_status") == "NOT GENERATED; NOT OPENED"
        and value.get("final_holdout_opened") is False
        and value.get("winner_selected") is False,
        "retain the complete real V95 comparison and unopened final holdout",
    )
    assert isinstance(value, dict)
    base.need(
        value.get("rust_v22_original_campaign_verified_passing_case_count") == 14725
        and value.get("rust_v22_original_campaign_observed_mismatch_lower_bound")
        == 2018
        and value.get("rust_v22_original_campaign_complete_failure_worker_warning_count")
        == 16
        and value.get("rust_v22_original_campaign_all_worker_warning_count")
        == "NOT MEASURED"
        and value.get("c_v9_original_campaign_verified_passing_case_count") == 13606
        and value.get("c_v9_original_campaign_observed_mismatch_lower_bound") == 492
        and value.get("c_v9_original_campaign_candidate_execution_failure_count") == 6
        and value.get("zig_v13_original_campaign_verified_passing_case_count") == 4607
        and value.get("zig_v13_original_campaign_observed_mismatch_lower_bound") == 1700
        and value.get("zig_v13_original_campaign_cleanup_warning_worker_count") == 13
        and value.get(
            "zig_v13_original_campaign_cleanup_warning_captured_occurrence_lower_bound"
        ) == 143
        and value.get("zig_v13_original_campaign_cleanup_warning_full_occurrence_count")
        == "NOT MEASURED"
        and value.get("lossless_v95_rust_v22_complete_plaintext_receipt_count") == 1
        and value.get("lossless_v95_rust_v22_complete_source_owner_count") == 3
        and value.get("lossless_v95_rust_v22_complete_original_suite_count") == 13,
        "preserve the actual Rust regression, earlier C failure, and all Zig warnings",
    )
    snapshot = value.get("snapshot")
    raw = base.canonical(snapshot)
    base.need(
        type(snapshot) is dict
        and snapshot.get("schema")
        == "rebar-candidate-current-overview-v95-compact-current-snapshot"
        and snapshot.get("version") == 95
        and len(raw) == V95_SNAPSHOT_BYTES
        and base.digest(raw) == V95_SNAPSHOT_SHA256,
        "preserve the exact complete real V95 snapshot",
    )
    for key, size, expected, count in previous_pools(previous, chain):
        pool = value.get(key)
        whole = base.canonical(pool)
        base.need(
            type(pool) is dict
            and len(whole) == size
            and base.digest(whole) == expected
            and type(pool.get("entries")) is dict
            and len(pool["entries"]) == count,
            "preserve the complete immutable V95 evidence pool: " + key,
        )
    families = value.get("families")
    latest = value.get("latest_original_campaigns")
    base.need(
        type(families) is list
        and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and families[0].get("correctness") == "BASELINE PASS"
        and type(latest) is dict
        and set(latest) == {"rust", "c", "zig"}
        and latest["rust"].get("verified_passing_case_count") == 14725
        and latest["rust"].get("observed_semantic_mismatch_lower_bound") == 2018
        and latest["c"].get("verified_passing_case_count") == 13606
        and latest["c"].get("observed_semantic_mismatch_lower_bound") == 492
        and latest["zig"].get("verified_passing_case_count") == 4607
        and latest["zig"].get("observed_semantic_mismatch_lower_bound") == 1700
        and type(value.get("headline")) is dict
        and value["headline"].get("verified_original_checks_by_candidate")
        == {
            "c": 13606,
            "cpp": "NOT MEASURED",
            "fortran": "NOT MEASURED",
            "go": "NOT MEASURED",
            "rust": 14725,
            "zig": 4607,
        },
        "retain Python and every genuine, independently written engine result",
    )
    return value


def authenticate_previous(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> dict:
    snapshot, assets = previous.build(*chain, previous_options(previous))
    for role in ("inputs", "summary", "svg"):
        item = V95[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole published V95 " + role),
            "reconstruct the complete authenticated V95 " + role,
        )
    old = base.document(assets[V95["summary"][0]], "whole published V95 summary")
    validate_previous(previous, chain, base, old)
    base.need(
        base.canonical(snapshot) == base.canonical(old["snapshot"]),
        "preserve the complete independently reconstructed V95 snapshot",
    )
    return old


def validate_c_contract(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and set(value) == C_CONTRACT_KEYS,
        "preserve every complete independently frozen C V10 contract field",
    )
    assert isinstance(value, dict)
    base.need(
        value.get("schema") == "rebar-owned-repaired-c-original-campaign-v10-source-freeze"
        and value.get("version") == 10
        and value.get("status")
        == "SOURCE FROZEN; ACTUAL C21 V10 ORIGINAL CAMPAIGN NOT RUN"
        and value.get("family") == "c"
        and value.get("label") == "phase2-v21-c-original-match-semantics-original-p0-v10"
        and value.get("goal_sha256")
        == "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
        and value.get("candidate_correctness") == "NOT MEASURED"
        and value.get("candidate_qualification") == "NOT ESTABLISHED"
        and value.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and value.get("qualified_candidate_count") == 0
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("memory") == "NOT MEASURED"
        and value.get("undefined_behavior") == "NOT MEASURED"
        and value.get("winner_selected") is False,
        "distinguish a real C source freeze from actual candidate qualification",
    )
    for role in ("source", "protocol"):
        item = C_SOURCE[role]
        record = value.get(role)
        base.need(
            type(record) is dict
            and set(record) == {"bytes", "path", "sha256"}
            and record.get("path") == item[0]
            and record.get("sha256") == item[1]
            and record.get("bytes") == item[2],
            "reject a fabricated frozen C owner: " + role,
        )
    phase = value["phase_one_v4"]
    original = value["frozen_original_producer"]
    previous = value["preserved_actual_c_v9_campaign"]
    expanded = value["expanded_holdout"]
    base.need(
        type(phase) is dict
        and phase.get("original_case_execution_denominator") == CASE_COUNT
        and phase.get("original_suite_count") == 13
        and phase.get("original_obligation_count") == 73
        and phase.get("original_crosswalk_count") == 34
        and phase.get("named_private_waiver_count") == 13
        and phase.get("separate_reference_case_count") == SUPPLEMENTAL_CASE_COUNT
        and phase.get("separate_reference_cases_counted_in_original_denominator") is False
        and type(original) is dict
        and original.get("case_execution_denominator") == CASE_COUNT
        and original.get("suite_count") == 13
        and original.get("family_count") == 6
        and [
            (row.get("suite"), row.get("case_execution_count"))
            for row in original.get("suites", [])
        ] == list(SUITES)
        and type(previous) is dict
        and previous.get("verified_passing_case_count") == 13606
        and previous.get("observed_semantic_mismatch_lower_bound") == 492
        and previous.get("candidate_execution_failure_count") == 6
        and previous.get("infrastructure_failure_count") == 0
        and type(expanded) is dict
        and expanded.get("proposed_case_count") == HOLDOUT_PROPOSAL_COUNT
        and expanded.get("case_status") == "NOT GENERATED; NOT OPENED"
        and expanded.get("final_protocol_status") == "NOT FROZEN"
        and expanded.get("source_mode_holdout_files_read") == 0,
        "preserve the exact original C suite, previous failure, and unopened holdout",
    )
    effects = value["source_only_effects"]
    base.need(
        type(effects) is dict
        and all(type(count) is int and count == 0 for count in effects.values()),
        "reject candidate work, native loading, timing, or writes in a C source freeze",
    )
    return value


def validate_c_receipt(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and set(value) == C_RECEIPT_KEYS,
        "authenticate every complete actual C V10 public receipt field",
    )
    assert isinstance(value, dict)
    base.need(
        value.get("schema")
        == "rebar-owned-repaired-c-original-campaign-v10-durable-publication-receipt"
        and value.get("version") == 10
        and value.get("status") == "PASS"
        and value.get("publication_status") == "PASS"
        and value.get("publication_pass_means") == "DURABLE CORRECTNESS PUBLICATION ONLY"
        and value.get("family") == "c"
        and value.get("label") == "phase2-v21-c-original-match-semantics-original-p0-v10"
        and value.get("source_sha256") == C_SOURCE["source"][1]
        and value.get("protocol_sha256") == C_SOURCE["protocol"][1]
        and value.get("contract_sha256") == C_SOURCE["contract"][1]
        and value.get("candidate_status") == "FAIL"
        and value.get("candidate_qualified") is False
        and value.get("case_execution_denominator") == CASE_COUNT
        and value.get("named_private_waiver_count") == 13
        and value.get("suite_count") == 13
        and value.get("attempted_suite_count") == 13
        and value.get("actual_candidate_workers") == 13
        and value.get("actual_worker_process_ids") == list(C_WORKER_PIDS)
        and value.get("actual_worker_process_ids_are_distinct") is True
        and value.get("completed_suite_count") == 8
        and value.get("verified_passing_case_count") == 13606
        and value.get("observed_semantic_mismatch_lower_bound") == 606
        and value.get("semantic_mismatch_count") == "NOT MEASURED"
        and value.get("candidate_execution_failure_count") == 5
        and value.get("infrastructure_failure_count") == 0
        and value.get("worker_timeout_count") == 0
        and value.get("worker_timeout_seconds") == 120
        and value.get("separate_reference_case_count") == SUPPLEMENTAL_CASE_COUNT
        and value.get("separate_reference_cases_counted_as_candidate_cases") is False
        and value.get("original_native_inode_restored") is True
        and value.get("original_source_targets_modified") == 0
        and value.get("expanded_holdout_proposed_case_count") == HOLDOUT_PROPOSAL_COUNT
        and value.get("holdout") == "NOT OPENED"
        and value.get("hidden_cases_read") == 0
        and value.get("benchmark_files_read") == 0
        and value.get("clock_samples") == 0
        and value.get("timing_trials_run") == 0
        and value.get("performance") == "NOT MEASURED"
        and value.get("memory") == "NOT MEASURED"
        and value.get("undefined_behavior") == "NOT MEASURED"
        and value.get("winner_selected") is False,
        "do not confuse durable publication, actual C failures, or unmeasured speed",
    )
    archive = value["archive"]
    base.need(
        type(archive) is dict
        and set(archive)
        == {
            "bytes",
            "device",
            "directory_fsync_completed",
            "exclusive_creation",
            "file_fsync_completed",
            "inode",
            "mode",
            "nlink",
            "path",
            "sha256",
        }
        and archive.get("path")
        == "oracle/phase2/evidence/"
        "repaired-c-original-campaign-v10-c-phase2-v21-c-original-match-"
        "semantics-original-p0-v10-failures.json.gz"
        and archive.get("sha256")
        == "35b36907e699546b77d36bb7c5eea96fee5ce2fc1022b0c0f1eefe652128cc37"
        and archive.get("bytes") == 52085
        and archive.get("device") == 2064
        and archive.get("inode") == 525474
        and archive.get("mode") == "0600"
        and archive.get("nlink") == 1
        and archive.get("exclusive_creation") is True
        and archive.get("file_fsync_completed") is True
        and archive.get("directory_fsync_completed") is True
        and value.get("uncompressed_bytes") == 1388177
        and value.get("uncompressed_sha256")
        == "0efcabf545cc2a506936906cb51c3b725e6f17005bd188d737d388d3b3e64321",
        "retain C archive metadata only; never open, inflate, or stat the archive",
    )
    rows = value["suite_outcomes"]
    base.need(
        type(rows) is list and len(rows) == 13,
        "retain all thirteen actually observed C workers",
    )
    clean: list[dict] = []
    mismatches: list[dict] = []
    incomplete: list[dict] = []
    seen: set[int] = set()
    for index, (row, (suite, denominator)) in enumerate(zip(rows, SUITES, strict=True)):
        base.need(
            type(row) is dict
            and set(row) == C_ROW_KEYS
            and row.get("suite") == suite
            and row.get("case_execution_denominator") == denominator
            and row.get("actual_candidate_workers") == 1
            and row.get("worker_process_id") == C_WORKER_PIDS[index]
            and row["worker_process_id"] not in seen
            and base.digest(base.canonical(row)) == C_ROW_SHA256[suite],
            "reject a fabricated, changed, omitted, or duplicate actual C row: " + suite,
        )
        seen.add(row["worker_process_id"])
        if suite in C_FAILURES:
            base.need(
                row.get("status") == "FAIL"
                and row.get("failure_class") == "CANDIDATE EXECUTION FAILURE"
                and row.get("error_type") == "ActualSuiteFailure"
                and row.get("failure_phase") == "OBSERVE COMPLETE ORIGINAL SUITE"
                and row.get("mismatch_count") == "NOT MEASURED"
                and type(row.get("plain_failure_diagnostic")) is str
                and len(row["plain_failure_diagnostic"]) > 0,
                "retain an unfinished C candidate worker, not an infrastructure failure: "
                + suite,
            )
            incomplete.append(row)
        elif suite in C_MISMATCHES:
            base.need(
                row.get("status") == "FAIL"
                and row.get("failure_class") == "SEMANTIC MISMATCH"
                and row.get("error_type") == "NOT APPLICABLE"
                and row.get("failure_phase") == "OBSERVE COMPLETE ORIGINAL SUITE"
                and row.get("mismatch_count") == C_MISMATCHES[suite]
                and row.get("plain_failure_diagnostic")
                == "original C suite reported a semantic mismatch",
                "retain the complete observed C mismatch group: " + suite,
            )
            mismatches.append(row)
        else:
            base.need(
                row.get("status") == "PASS"
                and row.get("failure_class") == "PASS"
                and row.get("error_type") == "NOT APPLICABLE"
                and row.get("failure_phase") == "NOT APPLICABLE"
                and row.get("mismatch_count") == 0
                and row.get("plain_failure_diagnostic") == "",
                "reject an invented fully passing C group: " + suite,
            )
            clean.append(row)
    base.need(
        len(seen) == 13
        and len(clean) == 3
        and len(mismatches) == 5
        and len(incomplete) == 5
        and len(clean) + len(mismatches) == 8
        and sum(row["case_execution_denominator"] for row in clean) == 13606
        and {row["suite"]: row["mismatch_count"] for row in mismatches}
        == C_MISMATCHES
        and sum(row["mismatch_count"] for row in mismatches) == 606,
        "derive all actual C passes, lower-bound differences, and five failed workers",
    )
    return {
        "family": "c",
        "display_name": "C",
        "actual_candidate_worker_count": 13,
        "unique_candidate_worker_count": 13,
        "actual_worker_process_ids": list(C_WORKER_PIDS),
        "attempted_suite_count": 13,
        "completed_suite_count": 8,
        "clean_suite_count": 3,
        "mismatch_suite_count": 5,
        "candidate_execution_failure_count": 5,
        "infrastructure_failure_count": 0,
        "verified_passing_case_count": 13606,
        "observed_semantic_mismatch_lower_bound": 606,
        "aggregate_semantic_mismatch_count": "NOT MEASURED",
        "individual_mismatch_vector_count": "NOT MEASURED",
        "complete_individual_mismatch_vectors": "NOT MEASURED",
        "case_execution_denominator": CASE_COUNT,
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "all_original_suite_rows_validated": True,
        "all_original_observation_vectors_complete": False,
        "original_native_inode_restored": True,
        "original_source_targets_modified": 0,
        "previous_verified_passing_case_count": 13606,
        "verified_passing_case_change_from_v95": 0,
        "previous_observed_semantic_mismatch_lower_bound": 492,
        "observed_mismatch_lower_bound_increase_from_v95": 114,
        "previous_candidate_execution_failure_count": 6,
        "candidate_execution_failure_change_from_v95": -1,
        "source_sha256": C_SOURCE["source"][1],
        "protocol_sha256": C_SOURCE["protocol"][1],
        "contract_sha256": C_SOURCE["contract"][1],
        "archive_metadata_sha256": archive["sha256"],
        "archive_metadata_bytes": archive["bytes"],
        "archive_opened_by_graph": False,
        "archive_statted_by_graph": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
    }


def validate_zig_contract(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict
        and set(value) == ZIG_CONTRACT_KEYS
        and value.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v14-guarded-setter-safe-source-freeze"
        and value.get("version") == 14
        and value.get("status")
        == "SOURCE FROZEN; V3-GUARDED SETTER-SAFE ZIG MATCHING NOT RUN"
        and value.get("family") == "zig"
        and value.get("label")
        == "phase2-v14-zig-guard-clean-lifetime-setattr-v2-original-p0-v14"
        and value.get("corrected_original_matching") == "NOT RUN"
        and value.get("corrected_supplemental_matching") == "NOT RUN"
        and value.get("corrected_warning") == "NOT MEASURED"
        and value.get("corrected_subinterpreter") == "NOT MEASURED"
        and value.get("current_qualified_candidates") == 0
        and value.get("qualified_candidate_count") == 0
        and value.get("holdout") == "NOT OPENED"
        and value.get("holdout_case_count") == HOLDOUT_PROPOSAL_COUNT
        and value.get("holdout_case_status") == "NOT GENERATED; NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("memory") == "NOT MEASURED"
        and value.get("undefined_behavior") == "NOT MEASURED"
        and value.get("winner_selected") is False,
        "reject invented corrected Zig matching, warning cleanup, or a qualification",
    )
    assert isinstance(value, dict)
    for role in ("source", "protocol"):
        expected = ZIG14_SOURCE[role]
        record = value.get(role)
        base.need(
            type(record) is dict
            and record.get("path") == expected[0]
            and record.get("sha256") == expected[1]
            and record.get("bytes") == expected[2],
            "preserve the frozen first-party Zig V14 " + role,
        )
    original = value.get("original_oracle")
    expanded = value.get("expanded_sealed_holdout_proposal")
    effects = value.get("source_only_effects")
    base.need(
        type(original) is dict
        and original.get("case_execution_denominator") == CASE_COUNT
        and original.get("suite_count") == 13
        and original.get("named_private_waiver_count") == 13
        and original.get("crosswalk_count") == 34
        and original.get("obligation_count") == 73
        and original.get("supplemental_reference_case_count")
        == SUPPLEMENTAL_CASE_COUNT
        and original.get("supplemental_cases_added_to_original_denominator") is False
        and type(expanded) is dict
        and expanded.get("case_count") == HOLDOUT_PROPOSAL_COUNT
        and expanded.get("final_protocol_status") == "NOT FROZEN"
        and expanded.get("holdout_case_status") == "NOT GENERATED; NOT OPENED"
        and expanded.get("holdout_files_opened") == 0
        and expanded.get("timing_trials_run") == 0
        and type(effects) is dict
        and all(type(number) is int and number == 0 for number in effects.values()),
        "preserve the unopened holdout and the independently frozen Zig original suite",
    )
    return value


def validate_zig_controller(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and set(value) == ZIG_RECEIPT_KEYS,
        "authenticate the complete actual Zig V14 prepublication failure",
    )
    assert isinstance(value, dict)
    message = (
        "actual three-role campaign/recovery failed: CampaignError: "
        "source-only wall rejected unlisted, native, archive, holdout or write open"
    )
    base.need(
        value.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v14-"
        "prepublication-controller-failure-v1"
        and value.get("status") == "FAIL"
        and value.get("family") == "zig"
        and value.get("label")
        == "phase2-v14-zig-guard-clean-lifetime-setattr-v2-original-p0-v14"
        and value.get("source_sha256") == ZIG14_SOURCE["source"][1]
        and value.get("protocol_sha256") == ZIG14_SOURCE["protocol"][1]
        and value.get("contract_sha256") == ZIG14_SOURCE["contract"][1]
        and value.get("attempt_count") == 1
        and value.get("pipeline_exit_code") == 4
        and value.get("controller_error_type") == "CampaignError"
        and value.get("controller_error_message") == message
        and value.get("complete_captured_standard_error")
        == "first-party V3-guarded setter-safe Zig V14 campaign rejected: "
        "CampaignError: " + message + "\n"
        and value.get("complete_captured_standard_output") == ""
        and value.get("failure_stage")
        == "ACTUAL THREE-ROLE CAMPAIGN OR RECOVERY BEFORE PUBLICATION"
        and value.get("candidate_status") == "NOT MEASURED"
        and value.get("candidate_process_exit_code") == "NOT MEASURED"
        and value.get("actual_candidate_worker_count") == "NOT MEASURED"
        and value.get("actual_completed_suite_count") == "NOT MEASURED"
        and value.get("actual_verified_passing_case_count") == "NOT MEASURED"
        and value.get("actual_semantic_mismatch_count") == "NOT MEASURED"
        and value.get("corrected_finalizer_warning_count") == "NOT MEASURED"
        and value.get("original_case_execution_denominator") == CASE_COUNT
        and value.get("original_suite_count") == 13
        and value.get("historical_v13_verified_passing_case_count") == 4607
        and value.get("historical_v13_observed_semantic_mismatch_lower_bound") == 1700
        and value.get("historical_v13_warning_worker_count") == 13
        and value.get("all_three_original_targets_restored") is True
        and value.get("recovery_root_created") is False
        and value.get("failure_archive_created") is False
        and value.get("failure_receipt_created") is False
        and value.get("success_archive_created") is False
        and value.get("success_receipt_created") is False
        and value.get("expanded_holdout_proposed_case_count") == HOLDOUT_PROPOSAL_COUNT
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("memory") == "NOT MEASURED"
        and value.get("undefined_behavior") == "NOT MEASURED"
        and value.get("qualified_candidate_count") == 0
        and value.get("winner_selected") is False,
        "do not invent matching, cleanup, workers, or a result from a Zig controller failure",
    )
    roles = value["restored_original_targets"]
    expected_roles = {
        "adapter": (
            "candidates/zig_candidate.py",
            "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
            68422,
            429360,
            "0600",
        ),
        "bridge": (
            "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
            "d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b",
            134112,
            431274,
            "0700",
        ),
        "engine": (
            "candidates/_zig_probe.so",
            "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652",
            478432,
            431260,
            "0700",
        ),
    }
    base.need(
        type(roles) is dict and set(roles) == set(expected_roles),
        "preserve three exact Zig target metadata owners without opening native code",
    )
    for role, expected in expected_roles.items():
        relative, digest, size, inode, mode = expected
        item = roles[role]
        base.need(
            type(item) is dict
            and set(item) == {"relative", "sha256", "bytes", "device", "inode", "mode", "uid", "nlink"}
            and item.get("relative") == relative
            and item.get("sha256") == digest
            and item.get("bytes") == size
            and item.get("device") == 2064
            and item.get("inode") == inode
            and item.get("mode") == mode
            and item.get("uid") == os.geteuid()
            and item.get("nlink") == 1,
            "reject fabricated restored Zig target metadata: " + role,
        )
    authority = value["frozen_authority"]
    authority_raw = base.canonical(authority)
    base.need(
        type(authority) is dict
        and len(authority) == 23
        and len(authority_raw) == 2098
        and base.digest(authority_raw)
        == "3b709179457b465eb78900d60abf187f3ae1a951482888ecf3f0ea69def7b87d"
        and authority.get("v13_source_sha256")
        == "fa46d4029f5590adceb22bfe4e612248da5f7f90ed6362d58faa5b631fee7ff8"
        and authority.get("v13_failure_receipt_sha256")
        == "b3443a647c638cbbbe7905a2c668a734770f38cb678f06a387af497917fc4bca"
        and authority.get("setter_safe_adapter_sha256")
        == "c16a6e4c9745eff3a55dcf85eb14c26ec84092d70ddbc40d5e841ab0140d3032",
        "retain actual prior Zig authority without treating it as corrected matching",
    )
    return {
        "family": "zig",
        "display_name": "Zig controller only",
        "status": "FAIL",
        "failure_stage": value["failure_stage"],
        "attempt_count": 1,
        "pipeline_exit_code": 4,
        "controller_error_type": "CampaignError",
        "controller_error_message": message,
        "candidate_status": "NOT MEASURED",
        "candidate_process_exit_code": "NOT MEASURED",
        "actual_candidate_worker_count": "NOT MEASURED",
        "actual_completed_suite_count": "NOT MEASURED",
        "actual_verified_passing_case_count": "NOT MEASURED",
        "actual_semantic_mismatch_count": "NOT MEASURED",
        "corrected_finalizer_warning_count": "NOT MEASURED",
        "historical_v13_verified_passing_case_count": 4607,
        "historical_v13_observed_semantic_mismatch_lower_bound": 1700,
        "historical_v13_warning_worker_count": 13,
        "all_three_original_targets_restored": True,
        "recovery_root_created": False,
        "failure_archive_created": False,
        "failure_receipt_created": False,
        "success_archive_created": False,
        "success_receipt_created": False,
        "source_sha256": ZIG14_SOURCE["source"][1],
        "protocol_sha256": ZIG14_SOURCE["protocol"][1],
        "contract_sha256": ZIG14_SOURCE["contract"][1],
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def load_new_evidence(
    base: types.ModuleType,
) -> tuple[dict, dict, dict, dict, dict, dict]:
    c_raws = {
        role: read_fixed(item, "whole independently frozen C V10 " + role)
        for role, item in C_SOURCE.items()
    }
    c_contract = base.document(c_raws["contract"], "whole frozen C V10 contract")
    base.need(
        base.canonical(c_contract) == c_raws["contract"],
        "reject a partial or noncanonical C V10 contract",
    )
    validate_c_contract(base, c_contract)
    c_raw = read_fixed(C_RECEIPT, "whole actual C V10 public failure receipt")
    c_receipt = base.document(c_raw, "whole actual C V10 public failure receipt")
    base.need(
        base.canonical(c_receipt) == c_raw,
        "reject a partial, noncanonical, or synthetic C V10 receipt",
    )
    c_facts = validate_c_receipt(base, c_receipt)
    zig_raws = {
        role: read_fixed(item, "whole independently frozen Zig V14 " + role)
        for role, item in ZIG14_SOURCE.items()
    }
    zig_contract = base.document(zig_raws["contract"], "whole frozen Zig V14 contract")
    base.need(
        base.canonical(zig_contract) == zig_raws["contract"],
        "reject a partial or noncanonical Zig V14 contract",
    )
    validate_zig_contract(base, zig_contract)
    zig_raw = read_fixed(ZIG14_RECEIPT, "whole genuine Zig V14 controller failure")
    zig_receipt = base.document(
        zig_raw,
        "whole genuine noncanonical Zig V14 controller failure",
        exact=False,
    )
    base.need(
        len(zig_raw) == ZIG14_RECEIPT[2]
        and base.digest(zig_raw) == ZIG14_RECEIPT[1],
        "preserve every exact original byte of the actual Zig V14 failure receipt",
    )
    zig_facts = validate_zig_controller(base, zig_receipt)
    return c_contract, c_receipt, c_facts, zig_contract, zig_receipt, zig_facts


def compact_c_row(base: types.ModuleType, row: dict) -> dict:
    raw = base.canonical(row)
    return {
        "suite": row["suite"],
        "case_execution_denominator": row["case_execution_denominator"],
        "complete_public_row_sha256": base.digest(raw),
        "complete_public_row_canonical_bytes": len(raw),
        "actual_worker_process_id": row["worker_process_id"],
        "actual_candidate_workers": row["actual_candidate_workers"],
        "failure_class": row["failure_class"],
        "status": row["status"],
        "mismatch_count": row["mismatch_count"],
        "failure_phase": row["failure_phase"],
        "error_type": row["error_type"],
        "complete_plain_failure_diagnostic": row["plain_failure_diagnostic"],
    }


def make_evidence_pool(
    base: types.ModuleType,
    c_contract: dict,
    c_receipt: dict,
    c_facts: dict,
    zig_contract: dict,
    zig_receipt: dict,
    zig_facts: dict,
) -> dict:
    zig_original_raw = read_fixed(
        ZIG14_RECEIPT, "complete exact noncanonical Zig V14 controller receipt"
    )
    base.need(
        base.canonical(
            base.document(
                zig_original_raw,
                "complete exact noncanonical Zig V14 controller receipt",
                exact=False,
            )
        ) == base.canonical(zig_receipt),
        "retain all actual noncanonical Zig controller receipt bytes and fields",
    )
    c_entry = {
        "schema": C_ENTRY_SCHEMA,
        "family": "c",
        "complete_plaintext_receipt_owner": base.synthetic_owner(
            C_RECEIPT[:3], C_RECEIPT[3]
        ),
        "complete_plaintext_receipt_sha256": C_RECEIPT[1],
        "complete_plaintext_receipt_bytes": C_RECEIPT[2],
        "complete_plaintext_receipt_field_count": len(C_RECEIPT_KEYS),
        "complete_plaintext_receipt_embedded": True,
        "complete_plaintext_receipt": copy.deepcopy(c_receipt),
        "complete_first_party_source_owner_count": 3,
        "complete_first_party_source_owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in C_SOURCE.items()
        },
        "complete_source_contract_embedded": True,
        "complete_source_contract": copy.deepcopy(c_contract),
        "complete_original_suite_count": 13,
        "complete_original_suite_rows": [
            compact_c_row(base, row) for row in c_receipt["suite_outcomes"]
        ],
        "complete_public_archive_metadata": copy.deepcopy(c_receipt["archive"]),
        "validated_campaign_outcome": copy.deepcopy(c_facts),
        "compressed_archive_opened_by_graph": False,
        "compressed_archive_statted_by_graph": False,
        "private_build_root_opened_by_graph": False,
        "complete_public_c_suite_outcomes_preserved_without_archive": True,
        "individual_mismatch_vectors_read_by_graph": 0,
        "complete_individual_mismatch_vectors": "NOT MEASURED",
    }
    zig_entry = {
        "schema": ZIG_ENTRY_SCHEMA,
        "family": "zig",
        "complete_plaintext_receipt_owner": base.synthetic_owner(
            ZIG14_RECEIPT[:3], ZIG14_RECEIPT[3]
        ),
        "complete_plaintext_receipt_sha256": ZIG14_RECEIPT[1],
        "complete_plaintext_receipt_bytes": ZIG14_RECEIPT[2],
        "complete_plaintext_receipt_field_count": len(ZIG_RECEIPT_KEYS),
        "complete_plaintext_receipt_embedded": True,
        "complete_plaintext_receipt": copy.deepcopy(zig_receipt),
        "complete_plaintext_receipt_original_utf8": zig_original_raw.decode("utf-8"),
        "complete_first_party_source_owner_count": 3,
        "complete_first_party_source_owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in ZIG14_SOURCE.items()
        },
        "complete_source_contract_embedded": True,
        "complete_source_contract": copy.deepcopy(zig_contract),
        "complete_controller_stdout": zig_receipt["complete_captured_standard_output"],
        "complete_controller_stderr": zig_receipt["complete_captured_standard_error"],
        "complete_restored_target_metadata": copy.deepcopy(
            zig_receipt["restored_original_targets"]
        ),
        "validated_controller_outcome": copy.deepcopy(zig_facts),
        "candidate_matching_claimed": False,
        "candidate_workers_claimed": False,
        "warning_resolution_claimed": False,
        "compressed_archive_opened_by_graph": False,
        "compressed_archive_statted_by_graph": False,
        "private_build_root_opened_by_graph": False,
    }
    pool = {
        "schema": POOL_SCHEMA,
        "version": 1,
        "hash_algorithm": "sha256",
        "complete_public_receipt_count": 2,
        "complete_first_party_source_owner_count": 6,
        "entries": {C_RECEIPT[1]: c_entry, ZIG14_RECEIPT[1]: zig_entry},
    }
    validate_evidence_pool(
        base, pool, c_contract, c_receipt, c_facts,
        zig_contract, zig_receipt, zig_facts,
    )
    return pool


def validate_evidence_pool(
    base: types.ModuleType,
    pool: object,
    c_contract: dict,
    c_receipt: dict,
    c_facts: dict,
    zig_contract: dict,
    zig_receipt: dict,
    zig_facts: dict,
) -> None:
    base.need(
        type(pool) is dict
        and set(pool)
        == {
            "schema",
            "version",
            "hash_algorithm",
            "complete_public_receipt_count",
            "complete_first_party_source_owner_count",
            "entries",
        }
        and pool.get("schema") == POOL_SCHEMA
        and pool.get("version") == 1
        and pool.get("hash_algorithm") == "sha256"
        and pool.get("complete_public_receipt_count") == 2
        and pool.get("complete_first_party_source_owner_count") == 6
        and type(pool.get("entries")) is dict
        and set(pool["entries"]) == {C_RECEIPT[1], ZIG14_RECEIPT[1]},
        "preserve both exact complete actual C and controller-only Zig receipts",
    )
    assert isinstance(pool, dict)
    for family, receipt_owner, sources, contract, receipt, facts, schema in (
        ("c", C_RECEIPT, C_SOURCE, c_contract, c_receipt, c_facts, C_ENTRY_SCHEMA),
        (
            "zig",
            ZIG14_RECEIPT,
            ZIG14_SOURCE,
            zig_contract,
            zig_receipt,
            zig_facts,
            ZIG_ENTRY_SCHEMA,
        ),
    ):
        entry = pool["entries"][receipt_owner[1]]
        base.need(
            type(entry) is dict
            and entry.get("schema") == schema
            and entry.get("family") == family
            and base.canonical(entry.get("complete_plaintext_receipt_owner"))
            == base.canonical(base.synthetic_owner(receipt_owner[:3], receipt_owner[3]))
            and entry.get("complete_plaintext_receipt_sha256") == receipt_owner[1]
            and entry.get("complete_plaintext_receipt_bytes") == receipt_owner[2]
            and entry.get("complete_plaintext_receipt_embedded") is True
            and base.canonical(entry.get("complete_plaintext_receipt"))
            == base.canonical(receipt)
            and entry.get("complete_first_party_source_owner_count") == 3
            and entry.get("complete_source_contract_embedded") is True
            and base.canonical(entry.get("complete_source_contract"))
            == base.canonical(contract)
            and entry.get("compressed_archive_opened_by_graph") is False
            and entry.get("compressed_archive_statted_by_graph") is False
            and entry.get("private_build_root_opened_by_graph") is False,
            "reject omitted complete actual " + family + " receipt or source proof",
        )
        owners = entry["complete_first_party_source_owners"]
        base.need(
            type(owners) is dict and set(owners) == set(sources),
            "retain every independent first-party " + family + " source owner",
        )
        for role, item in sources.items():
            base.need(
                base.canonical(owners[role])
                == base.canonical(base.synthetic_owner(item[:3], item[3])),
                "reject an invented first-party " + family + " owner: " + role,
            )
        if family == "c":
            base.need(
                entry.get("complete_plaintext_receipt_field_count")
                == len(C_RECEIPT_KEYS)
                and entry.get("complete_original_suite_count") == 13
                and base.canonical(entry.get("complete_original_suite_rows"))
                == base.canonical([
                    compact_c_row(base, row) for row in receipt["suite_outcomes"]
                ])
                and base.canonical(entry.get("complete_public_archive_metadata"))
                == base.canonical(receipt["archive"])
                and base.canonical(entry.get("validated_campaign_outcome"))
                == base.canonical(facts)
                and entry.get("complete_public_c_suite_outcomes_preserved_without_archive")
                is True
                and entry.get("individual_mismatch_vectors_read_by_graph") == 0
                and entry.get("complete_individual_mismatch_vectors") == "NOT MEASURED",
                "retain authenticated public C suite outcomes and archive metadata only",
            )
        else:
            original_text = entry.get("complete_plaintext_receipt_original_utf8")
            base.need(
                type(original_text) is str
                and len(original_text.encode("utf-8")) == ZIG14_RECEIPT[2]
                and base.digest(original_text.encode("utf-8")) == ZIG14_RECEIPT[1]
                and base.canonical(
                    base.document(
                        original_text.encode("utf-8"),
                        "complete embedded noncanonical Zig controller receipt",
                        exact=False,
                    )
                ) == base.canonical(receipt),
                "preserve every original pretty-printed Zig receipt byte losslessly",
            )
            base.need(
                entry.get("complete_plaintext_receipt_field_count")
                == len(ZIG_RECEIPT_KEYS)
                and entry.get("complete_controller_stdout")
                == receipt["complete_captured_standard_output"]
                and entry.get("complete_controller_stderr")
                == receipt["complete_captured_standard_error"]
                and base.canonical(entry.get("complete_restored_target_metadata"))
                == base.canonical(receipt["restored_original_targets"])
                and base.canonical(entry.get("validated_controller_outcome"))
                == base.canonical(facts)
                and entry.get("candidate_matching_claimed") is False
                and entry.get("candidate_workers_claimed") is False
                and entry.get("warning_resolution_claimed") is False,
                "retain the Zig controller failure without inventing corrected matching",
            )


def make_reference(base: types.ModuleType, pool: dict, family: str) -> dict:
    receipt = C_RECEIPT if family == "c" else ZIG14_RECEIPT
    entry = pool["entries"][receipt[1]]
    raw = base.canonical(entry)
    return {
        "schema": REFERENCE_SCHEMA,
        "family": family,
        "complete_plaintext_receipt_sha256": receipt[1],
        "complete_plaintext_receipt_bytes": receipt[2],
        "complete_first_party_source_owner_count": 3,
        "complete_reference_sha256": base.digest(raw),
        "complete_reference_canonical_bytes": len(raw),
    }


def resolve_reference(
    base: types.ModuleType,
    pool: dict,
    reference: object,
    family: str,
) -> dict:
    owner = C_RECEIPT if family == "c" else ZIG14_RECEIPT
    base.need(
        type(reference) is dict
        and set(reference)
        == {
            "schema",
            "family",
            "complete_plaintext_receipt_sha256",
            "complete_plaintext_receipt_bytes",
            "complete_first_party_source_owner_count",
            "complete_reference_sha256",
            "complete_reference_canonical_bytes",
        }
        and reference.get("schema") == REFERENCE_SCHEMA
        and reference.get("family") == family
        and reference.get("complete_plaintext_receipt_sha256") == owner[1]
        and reference.get("complete_plaintext_receipt_bytes") == owner[2]
        and reference.get("complete_first_party_source_owner_count") == 3
        and type(pool.get("entries")) is dict
        and owner[1] in pool["entries"],
        "reject an invented complete " + family + " evidence reference",
    )
    assert isinstance(reference, dict)
    entry = pool["entries"][owner[1]]
    raw = base.canonical(entry)
    base.need(
        len(raw) == reference["complete_reference_canonical_bytes"]
        and base.digest(raw) == reference["complete_reference_sha256"],
        "authenticate every byte of the complete " + family + " evidence reference",
    )
    return copy.deepcopy(entry)


def make_changes(c_reference: dict, zig_reference: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 95,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v96_new_directly_authenticated_owner_count": 8,
        "v96_new_directly_authenticated_c_source_owner_count": 3,
        "v96_new_directly_authenticated_c_plaintext_receipt_owner_count": 1,
        "v96_new_directly_authenticated_zig_source_owner_count": 3,
        "v96_new_directly_authenticated_zig_controller_receipt_owner_count": 1,
        "lossless_previous_v95_proof_pool_count": 17,
        "lossless_v95_all_seventeen_previous_pool_identity_status": "PASS",
        "lossless_v95_snapshot_identity_status": "PASS",
        "lossless_v95_family_identity_status": "PASS",
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "c_v10_original_campaign_actual_worker_count": 13,
        "c_v10_original_campaign_distinct_worker_count": 13,
        "c_v10_original_campaign_attempted_suite_count": 13,
        "c_v10_original_campaign_clean_suite_count": 3,
        "c_v10_original_campaign_completed_suite_count": 8,
        "c_v10_original_campaign_mismatch_suite_count": 5,
        "c_v10_original_campaign_verified_passing_case_count": 13606,
        "c_v10_original_campaign_observed_mismatch_lower_bound": 606,
        "c_v10_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "c_v10_original_campaign_individual_mismatch_vector_count": "NOT MEASURED",
        "c_v10_original_campaign_complete_individual_mismatch_vectors": "NOT MEASURED",
        "c_v10_original_campaign_candidate_execution_failure_count": 5,
        "c_v10_original_campaign_infrastructure_failure_count": 0,
        "c_v10_original_campaign_previous_verified_passing_case_count": 13606,
        "c_v10_original_campaign_verified_passing_case_change_from_v95": 0,
        "c_v10_original_campaign_previous_mismatch_lower_bound": 492,
        "c_v10_original_campaign_mismatch_lower_bound_increase_from_v95": 114,
        "c_v10_original_campaign_previous_candidate_execution_failure_count": 6,
        "c_v10_original_campaign_candidate_execution_failure_change_from_v95": -1,
        "c_v10_original_campaign_candidate_status": "FAIL",
        "c_v10_original_campaign_candidate_qualified": False,
        "c_v10_original_campaign_original_native_inode_restored": True,
        "zig_v14_controller_failure_attempt_count": 1,
        "zig_v14_controller_failure_pipeline_exit_code": 4,
        "zig_v14_controller_failure_candidate_status": "NOT MEASURED",
        "zig_v14_controller_failure_candidate_worker_count": "NOT MEASURED",
        "zig_v14_controller_failure_completed_suite_count": "NOT MEASURED",
        "zig_v14_controller_failure_verified_passing_case_count": "NOT MEASURED",
        "zig_v14_controller_failure_semantic_mismatch_count": "NOT MEASURED",
        "zig_v14_controller_failure_corrected_warning_count": "NOT MEASURED",
        "zig_v14_controller_failure_all_three_original_targets_restored": True,
        "zig_v14_controller_failure_recovery_root_created": False,
        "zig_v14_controller_failure_matching_archive_created": False,
        "zig_v14_controller_failure_matching_receipt_created": False,
        "current_aggregate_semantic_mismatch_counts": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "timing_trials_run": 0,
        "clock_samples_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "compressed_archives_statted_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "expanded_holdout_proposed_case_count": HOLDOUT_PROPOSAL_COUNT,
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "preserved_previous_holdout_proposal_case_count":
        HISTORICAL_HOLDOUT_PROPOSAL_COUNT,
        "final_holdout_opened": False,
        "winner_selected": False,
        C_LATEST_KEY: copy.deepcopy(c_reference),
        ZIG_CONTROLLER_KEY: copy.deepcopy(zig_reference),
    }


def make_svg() -> bytes:
    rows = (
        ("Python re", CASE_COUNT, "13 of 13 original groups passed", "BASELINE", "#34d399"),
        (
            "Rust",
            14725,
            "9 passed; 3 differ; 1 unfinished; 16 captured warnings",
            "NOT YET COMPATIBLE",
            "#fb7185",
        ),
        (
            "C",
            13606,
            "3 passed; 5 differ; 5 did not finish; at least 606 differences",
            "NOT YET COMPATIBLE",
            "#fbbf24",
        ),
        (
            "Zig",
            4607,
            "Prior result; 13 workers warned; new attempt stopped before matching",
            "NOT YET COMPATIBLE",
            "#fbbf24",
        ),
        ("C++", None, "Full current matching result not measured", "NOT MEASURED", "#94a3b8"),
        ("Go", None, "Full current matching result not measured", "NOT MEASURED", "#94a3b8"),
        ("Fortran", None, "Independent builds disagreed; matching not measured", "BUILD FAILED", "#fb7185"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1520" height="1120" '
        'viewBox="0 0 1520 1120" role="img" aria-labelledby="title description">',
        '<title id="title">How close are from-scratch alternatives to Python re?</title>',
        '<desc id="description">Bars show confirmed matching checks, never speed. '
        'Python passes 31,237 of 31,237 original checks. Rust verifies 14,725 '
        'and retains its prior real regression. C verifies 13,606, with '
        'an observed lower bound of 606 differences, five mismatch groups, and five '
        'unfinished candidate workers; there were zero infrastructure failures. '
        'Individual mismatch-vector completeness is not measured. '
        'Zig retains its previous 4,607 verified checks, its 13 warning-bearing '
        'workers, and at least 1,700 differences. Its newer corrected controller '
        'failed before publishing any matching result, so no corrected checks, '
        'workers, or eliminated warnings are claimed. C++, Go, and Fortran '
        'have no fully measured original result. The 8,244 separate reference '
        'checks are excluded from the 31,237 denominator. The proposed '
        '14,155,776-case speed test is not frozen, not generated, and not opened. '
        'Speed, memory, safety, and rankings are not measured. No winner.</desc>',
        '<rect width="1520" height="1120" rx="24" fill="#0b1220"/>',
        '<text x="48" y="66" fill="#f8fafc" font-size="32" '
        'font-family="system-ui,sans-serif" font-weight="740">'
        'Building a faster Python re, from scratch</text>',
        '<text x="49" y="104" fill="#cbd5e1" font-size="17" '
        'font-family="system-ui,sans-serif">Six independently written approaches; '
        'no fully compatible replacement; no speed result; no winner</text>',
        '<rect x="46" y="127" width="1428" height="78" rx="13" fill="#172338"/>',
        '<text x="65" y="158" fill="#f8fafc" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'The bars show compatibility with Python, not speed.</text>',
        '<text x="65" y="184" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif">All bars use the same 31,237 original '
        'checks. Failed, unfinished, and unmeasured checks never count as passes.</text>',
        '<text x="50" y="244" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">APPROACH</text>',
        '<text x="161" y="244" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'ORIGINAL PYTHON CHECKS CONFIRMED</text>',
        '<text x="724" y="244" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">WHAT THE TESTS SHOW</text>',
        '<text x="1260" y="244" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">SPEED</text>',
        '<text x="1470" y="244" text-anchor="end" fill="#94a3b8" '
        'font-size="12" font-family="system-ui,sans-serif" '
        'font-weight="690">RESULT</text>',
        '<line x1="46" y1="261" x2="1474" y2="261" stroke="#334155"/>',
    ]
    for index, (name, passed, details, result, colour) in enumerate(rows):
        y = 305 + 68 * index
        parts.append(
            f'<text x="51" y="{y}" fill="#f8fafc" font-size="16" '
            f'font-family="system-ui,sans-serif" font-weight="670">{name}</text>'
        )
        parts.append(
            f'<rect x="160" y="{y - 16}" width="314" height="20" '
            'rx="6" fill="#1e293b"/>'
        )
        if passed is None:
            label = "NOT MEASURED"
        else:
            width = max(3, round(314 * passed / CASE_COUNT))
            percent = "100%" if passed == CASE_COUNT else f"{100 * passed / CASE_COUNT:.1f}%"
            parts.append(
                f'<rect x="160" y="{y - 16}" width="{width}" height="20" '
                f'rx="6" fill="{colour}"/>'
            )
            label = f"{passed:,} / {CASE_COUNT:,} ({percent})"
        parts.append(
            f'<text x="485" y="{y}" fill="#e2e8f0" font-size="12" '
            f'font-family="system-ui,sans-serif">{label}</text>'
        )
        parts.append(
            f'<text x="724" y="{y}" fill="#cbd5e1" font-size="11" '
            f'font-family="system-ui,sans-serif">{details}</text>'
        )
        parts.append(
            f'<text x="1260" y="{y}" fill="#94a3b8" font-size="11" '
            'font-family="system-ui,sans-serif">NOT MEASURED</text>'
        )
        parts.append(
            f'<text x="1470" y="{y}" text-anchor="end" fill="{colour}" '
            f'font-size="10" font-family="system-ui,sans-serif" '
            f'font-weight="730">{result}</text>'
        )
    parts.extend((
        '<line x1="46" y1="757" x2="1474" y2="757" stroke="#334155"/>',
        '<text x="51" y="790" fill="#f8fafc" font-size="17" '
        'font-family="system-ui,sans-serif" font-weight="700">'
        'What did the newest real experiments show?</text>',
        '<text x="51" y="817" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">C still confirms 13,606 checks. '
        'The observed difference lower bound increased from 492 to 606. '
        'Five candidate workers did not finish; zero were infrastructure failures.</text>',
        '<text x="51" y="846" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">The corrected Zig controller stopped '
        'before a matching result could be published. Its corrected matching '
        'and cleanup are NOT MEASURED.</text>',
        '<text x="51" y="875" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">The previous real Rust regression, '
        'all 13 previous Zig warning-bearing workers, and every earlier '
        'result remain preserved.</text>',
        '<rect x="46" y="899" width="1428" height="120" rx="13" fill="#172338"/>',
        '<text x="66" y="932" fill="#f8fafc" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="680">'
        'Future speed comparison: proposed 14,155,776 cases</text>',
        '<text x="66" y="959" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">NOT FROZEN; NOT GENERATED; '
        'NOT OPENED; NOT RUN. Speed, memory, confidence, and rankings: '
        'NOT MEASURED.</text>',
        '<text x="66" y="986" fill="#cbd5e1" font-size="12" '
        'font-family="system-ui,sans-serif">The separate 8,244 reference checks '
        'are not added to the 31,237 original checks.</text>',
        '<text x="51" y="1065" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif">Overview 96; all observed losses '
        'preserved; no corrected Zig matching invented; no speed claims; no winner</text>',
        "</svg>",
        "",
    ))
    return "\n".join(parts).encode("utf-8")


def validate_families(
    base: types.ModuleType,
    old: dict,
    families: object,
    pool: dict,
    c_reference: dict,
    c_facts: dict,
    zig_reference: dict,
    zig_facts: dict,
) -> None:
    base.need(
        type(families) is list
        and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve Python and all six distinct independently written candidates",
    )
    assert isinstance(families, list)
    for row, original in zip(families, old["families"], strict=True):
        family = original["family"]
        base.need(
            type(row) is dict and row.get("family") == family,
            "reject a fabricated or omitted engine family: " + family,
        )
        if family == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "preserve every real Python baseline field",
            )
            continue
        base.need(
            row.get("authenticated_evidence_owner_lower_bound") == EVIDENCE_FLOOR
            and row.get("authenticated_history_reference_lower_bound") == HISTORY_FLOOR
            and row.get("qualified") is False
            and row.get("runtime_no_delegation") == "NOT ESTABLISHED"
            and row.get("performance") == "NOT MEASURED",
            "reject invented compatibility, engine independence, or speed: " + family,
        )
        restored = copy.deepcopy(row)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        if family == "c":
            proof = resolve_reference(base, pool, row.get(C_LATEST_KEY), "c")
            base.need(
                base.canonical(proof["validated_campaign_outcome"])
                == base.canonical(c_facts)
                and base.canonical(row.get("v96_latest_original_campaign"))
                == base.canonical(c_facts)
                and base.canonical(row.get(C_LATEST_KEY))
                == base.canonical(c_reference),
                "preserve genuine C worker failures and every observed C difference",
            )
            restored.pop(C_LATEST_KEY)
            restored.pop("v96_latest_original_campaign")
        if family == "zig":
            proof = resolve_reference(base, pool, row.get(ZIG_CONTROLLER_KEY), "zig")
            base.need(
                base.canonical(proof["validated_controller_outcome"])
                == base.canonical(zig_facts)
                and base.canonical(row.get("v96_prepublication_controller_failure"))
                == base.canonical(zig_facts)
                and base.canonical(row.get(ZIG_CONTROLLER_KEY))
                == base.canonical(zig_reference),
                "preserve genuine controller failure without changing Zig matching",
            )
            restored.pop(ZIG_CONTROLLER_KEY)
            restored.pop("v96_prepublication_controller_failure")
        base.need(
            base.canonical(restored) == base.canonical(original),
            "preserve every previous complete candidate family field: " + family,
        )


def build(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None
        and type(options.source_bytes) is int
        and 0 < options.source_bytes <= OWNER_LIMIT,
        "caller-pin the complete immutable V96 renderer",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "whole immutable V96 renderer"),
        options.source_bytes,
        private=True,
    )
    for role, item in V95.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the complete actually committed V95 " + role,
        )
    for role, item in C_SOURCE.items():
        base.need(
            getattr(options, "c_" + role + "_sha256") == item[1],
            "caller-pin the exact independently authored C V10 " + role,
        )
    for role, item in ZIG14_SOURCE.items():
        base.need(
            getattr(options, "zig_" + role + "_sha256") == item[1],
            "caller-pin the exact independently authored Zig V14 " + role,
        )
    base.need(
        options.c_receipt_sha256 == C_RECEIPT[1]
        and options.zig_controller_receipt_sha256 == ZIG14_RECEIPT[1],
        "caller-pin both complete, actual, distinct public failure receipts",
    )
    old = authenticate_previous(previous, chain, base)
    evidence = load_new_evidence(base)
    c_contract, c_receipt, c_facts, zig_contract, zig_receipt, zig_facts = evidence
    pool = make_evidence_pool(base, *evidence)
    c_reference = make_reference(base, pool, "c")
    zig_reference = make_reference(base, pool, "zig")
    changes = make_changes(c_reference, zig_reference)
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V95.items()
    }
    c_owners = {
        role: base.pin(item[0], item[1], item[2]) for role, item in C_SOURCE.items()
    }
    zig_owners = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in ZIG14_SOURCE.items()
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update({
        "schema": SCHEMA + "-compact-current-snapshot",
        "version": 96,
        "previous_complete_snapshot_sha256": V95_SNAPSHOT_SHA256,
        "previous_complete_snapshot_canonical_bytes": V95_SNAPSHOT_BYTES,
        "previous_complete_overview_sha256": V95["summary"][1],
        "previous_complete_overview_bytes": V95["summary"][2],
        **copy.deepcopy(changes),
    })
    headline = copy.deepcopy(old["headline"])
    headline.update({
        "bars_measure": "VERIFIED ORIGINAL CORRECTNESS CHECKS; NOT SPEED",
        "fully_compatible_candidate_count": 0,
        "latest_complete_candidate_mismatch_totals": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "speed_relative_to_python": "NOT MEASURED",
        "winner_selected": False,
        "c_current_verified_original_checks": 13606,
        "c_previous_verified_original_checks": 13606,
        "c_verified_check_change_from_previous_graph": 0,
        "c_observed_mismatch_lower_bound": 606,
        "c_previous_observed_mismatch_lower_bound": 492,
        "c_observed_mismatch_lower_bound_change": 114,
        "c_incomplete_candidate_worker_count": 5,
        "c_infrastructure_failure_count": 0,
        "c_complete_mismatch_total": "NOT MEASURED",
        "c_individual_mismatch_vector_count": "NOT MEASURED",
        "c_complete_individual_mismatch_vectors": "NOT MEASURED",
        "zig_corrected_rerun_result": "PREPUBLICATION CONTROLLER FAILURE",
        "zig_corrected_matching": "NOT MEASURED",
        "zig_corrected_worker_count": "NOT MEASURED",
        "zig_corrected_cleanup": "NOT MEASURED",
    })
    headline["verified_original_checks_by_candidate"]["c"] = 13606
    inputs = {
        "schema": SCHEMA + "-inputs",
        "version": 96,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": copy.deepcopy(predecessor),
        "c_v10_source_owners": copy.deepcopy(c_owners),
        "c_v10_plaintext_receipt_owner": base.pin(
            C_RECEIPT[0], C_RECEIPT[1], C_RECEIPT[2]
        ),
        "zig_v14_source_owners": copy.deepcopy(zig_owners),
        "zig_v14_controller_failure_receipt_owner": base.pin(
            ZIG14_RECEIPT[0], ZIG14_RECEIPT[1], ZIG14_RECEIPT[2]
        ),
        "headline": copy.deepcopy(headline),
        "snapshot": copy.deepcopy(snapshot),
        "complete_original_suites": [
            {"suite": suite, "case_execution_denominator": count}
            for suite, count in SUITES
        ],
        **copy.deepcopy(changes),
    }
    families = copy.deepcopy(old["families"])
    for row in families:
        family = row["family"]
        if family == "python":
            continue
        row["authenticated_evidence_owner_lower_bound"] = EVIDENCE_FLOOR
        row["authenticated_history_reference_lower_bound"] = HISTORY_FLOOR
        if family == "c":
            row[C_LATEST_KEY] = copy.deepcopy(c_reference)
            row["v96_latest_original_campaign"] = copy.deepcopy(c_facts)
        if family == "zig":
            row[ZIG_CONTROLLER_KEY] = copy.deepcopy(zig_reference)
            row["v96_prepublication_controller_failure"] = copy.deepcopy(zig_facts)
    validate_families(
        base, old, families, pool, c_reference, c_facts, zig_reference, zig_facts
    )
    inputs_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 96,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(INPUT_PATH, base.digest(inputs_raw), len(inputs_raw)),
        "svg": base.pin(SVG_PATH, base.digest(svg_raw), len(svg_raw)),
        "previous_overview": copy.deepcopy(predecessor),
        "previous_v95_snapshot": copy.deepcopy(old["snapshot"]),
        "previous_v95_snapshot_canonical_sha256": V95_SNAPSHOT_SHA256,
        "previous_v95_snapshot_canonical_bytes": V95_SNAPSHOT_BYTES,
        "snapshot": copy.deepcopy(snapshot),
        "headline": copy.deepcopy(headline),
        "families": families,
        POOL_KEY: pool,
        "lossless_v96_complete_public_receipt_count": 2,
        "lossless_v96_complete_source_owner_count": 6,
        "lossless_v96_c_v10_complete_original_suite_count": 13,
        "lossless_v96_zig_v14_controller_matching_claimed": False,
        "preserved_v95_latest_original_campaigns": copy.deepcopy(
            old["latest_original_campaigns"]
        ),
        "latest_original_campaigns": {
            **copy.deepcopy(old["latest_original_campaigns"]),
            "c": copy.deepcopy(c_facts),
        },
        **copy.deepcopy(changes),
    })
    for key, size, expected, count in previous_pools(previous, chain):
        raw = base.canonical(summary[key])
        base.need(
            len(raw) == size
            and base.digest(raw) == expected
            and raw == base.canonical(old[key])
            and len(summary[key]["entries"]) == count,
            "retain every complete original V95 proof-pool byte: " + key,
        )
    base.need(
        base.canonical(summary["previous_v95_snapshot"])
        == base.canonical(old["snapshot"])
        and base.canonical(summary["previous_v94_snapshot"])
        == base.canonical(old["previous_v94_snapshot"])
        and base.canonical(summary["previous_v93_snapshot"])
        == base.canonical(old["previous_v93_snapshot"])
        and base.canonical(summary["families"][0])
        == base.canonical(old["families"][0])
        and base.canonical(summary["latest_original_campaigns"]["rust"])
        == base.canonical(old["latest_original_campaigns"]["rust"])
        and base.canonical(summary["latest_original_campaigns"]["zig"])
        == base.canonical(old["latest_original_campaigns"]["zig"])
        and base.canonical(summary["preserved_v95_latest_original_campaigns"]["c"])
        == base.canonical(old["latest_original_campaigns"]["c"])
        and summary["rust_v22_original_campaign_verified_passing_case_count"] == 14725
        and summary["rust_v22_original_campaign_observed_mismatch_lower_bound"] == 2018
        and summary["rust_v22_original_campaign_complete_failure_worker_warning_count"]
        == 16
        and summary["c_v9_original_campaign_verified_passing_case_count"] == 13606
        and summary["c_v9_original_campaign_observed_mismatch_lower_bound"] == 492
        and summary["c_v9_original_campaign_candidate_execution_failure_count"] == 6
        and summary["c_v10_original_campaign_verified_passing_case_count"] == 13606
        and summary["c_v10_original_campaign_observed_mismatch_lower_bound"] == 606
        and summary["c_v10_original_campaign_candidate_execution_failure_count"] == 5
        and summary["c_v10_original_campaign_infrastructure_failure_count"] == 0
        and summary["zig_v13_original_campaign_verified_passing_case_count"] == 4607
        and summary["zig_v13_original_campaign_cleanup_warning_worker_count"] == 13
        and summary["zig_v14_controller_failure_candidate_worker_count"]
        == "NOT MEASURED"
        and summary["zig_v14_controller_failure_corrected_warning_count"]
        == "NOT MEASURED"
        and summary["authenticated_evidence_owner_lower_bound"] == EVIDENCE_FLOOR
        and summary["authenticated_history_reference_lower_bound"] == HISTORY_FLOOR
        and summary["qualified_candidate_count"] == 0
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED"
        and summary["memory"] == "NOT MEASURED"
        and summary["undefined_behavior"] == "NOT MEASURED"
        and summary["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and summary["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and summary["final_holdout_opened"] is False
        and summary["winner_selected"] is False,
        "preserve all failures, warning scope, independent history, and unopened holdout",
    )
    validate_evidence_pool(base, summary[POOL_KEY], *evidence)
    for family, reference, facts, key in (
        ("c", c_reference, c_facts, C_LATEST_KEY),
        ("zig", zig_reference, zig_facts, ZIG_CONTROLLER_KEY),
    ):
        entry = resolve_reference(base, pool, reference, family)
        outcome = (
            entry["validated_campaign_outcome"]
            if family == "c"
            else entry["validated_controller_outcome"]
        )
        base.need(
            base.canonical(outcome) == base.canonical(facts)
            and base.canonical(summary[key]) == base.canonical(reference)
            and base.canonical(snapshot[key]) == base.canonical(reference)
            and base.canonical(inputs[key]) == base.canonical(reference),
            "retain independently recoverable actual " + family + " evidence",
        )
    assets = {
        INPUT_PATH: inputs_raw,
        SUMMARY_PATH: base.canonical(summary),
        SVG_PATH: svg_raw,
    }
    for path, raw in assets.items():
        base.need(
            type(raw) is bytes and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
            "reject unbounded complete V96 graph evidence: " + path,
        )
    return snapshot, assets


def result_payload(
    base: types.ModuleType,
    options: argparse.Namespace,
    assets: dict[str, bytes],
    outputs_written: bool,
    additional: dict | None = None,
) -> dict:
    result = {
        "schema": SCHEMA + (
            "-published" if outputs_written else "-source-only-frozen-context"
        ),
        "version": 96,
        "status": "PASS",
        "source_sha256": options.source_sha256,
        "source_bytes": options.source_bytes,
        "inputs_sha256": base.digest(assets[INPUT_PATH]),
        "inputs_bytes": len(assets[INPUT_PATH]),
        "summary_sha256": base.digest(assets[SUMMARY_PATH]),
        "summary_bytes": len(assets[SUMMARY_PATH]),
        "svg_sha256": base.digest(assets[SVG_PATH]),
        "svg_bytes": len(assets[SVG_PATH]),
        "actual_current_graph_predecessor_version": 95,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v96_new_directly_authenticated_owner_count": 8,
        "v96_new_directly_authenticated_c_source_owner_count": 3,
        "v96_new_directly_authenticated_c_plaintext_receipt_owner_count": 1,
        "v96_new_directly_authenticated_zig_source_owner_count": 3,
        "v96_new_directly_authenticated_zig_controller_receipt_owner_count": 1,
        "lossless_previous_v95_proof_pool_count": 17,
        "lossless_v95_all_seventeen_previous_pool_identity_status": "PASS",
        "lossless_v95_snapshot_identity_status": "PASS",
        "lossless_v95_family_identity_status": "PASS",
        "lossless_v95_rust_v22_complete_original_suite_count": 13,
        "lossless_v96_complete_public_receipt_count": 2,
        "lossless_v96_complete_source_owner_count": 6,
        "lossless_v96_c_v10_complete_original_suite_count": 13,
        "lossless_v96_zig_v14_controller_matching_claimed": False,
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "rust_v22_original_campaign_verified_passing_case_count": 14725,
        "rust_v22_original_campaign_observed_mismatch_lower_bound": 2018,
        "rust_v22_original_campaign_complete_failure_worker_warning_count": 16,
        "rust_v22_original_campaign_all_worker_warning_count": "NOT MEASURED",
        "c_v9_original_campaign_verified_passing_case_count": 13606,
        "c_v9_original_campaign_observed_mismatch_lower_bound": 492,
        "c_v9_original_campaign_candidate_execution_failure_count": 6,
        "c_v10_original_campaign_actual_worker_count": 13,
        "c_v10_original_campaign_distinct_worker_count": 13,
        "c_v10_original_campaign_clean_suite_count": 3,
        "c_v10_original_campaign_completed_suite_count": 8,
        "c_v10_original_campaign_mismatch_suite_count": 5,
        "c_v10_original_campaign_verified_passing_case_count": 13606,
        "c_v10_original_campaign_observed_mismatch_lower_bound": 606,
        "c_v10_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "c_v10_original_campaign_individual_mismatch_vector_count": "NOT MEASURED",
        "c_v10_original_campaign_complete_individual_mismatch_vectors": "NOT MEASURED",
        "c_v10_original_campaign_candidate_execution_failure_count": 5,
        "c_v10_original_campaign_infrastructure_failure_count": 0,
        "c_v10_original_campaign_verified_passing_case_change_from_v95": 0,
        "c_v10_original_campaign_mismatch_lower_bound_increase_from_v95": 114,
        "c_v10_original_campaign_candidate_status": "FAIL",
        "c_v10_original_campaign_candidate_qualified": False,
        "zig_v13_original_campaign_verified_passing_case_count": 4607,
        "zig_v13_original_campaign_observed_mismatch_lower_bound": 1700,
        "zig_v13_original_campaign_cleanup_warning_worker_count": 13,
        "zig_v13_original_campaign_cleanup_warning_captured_occurrence_lower_bound": 143,
        "zig_v14_controller_failure_attempt_count": 1,
        "zig_v14_controller_failure_pipeline_exit_code": 4,
        "zig_v14_controller_failure_candidate_status": "NOT MEASURED",
        "zig_v14_controller_failure_candidate_worker_count": "NOT MEASURED",
        "zig_v14_controller_failure_completed_suite_count": "NOT MEASURED",
        "zig_v14_controller_failure_verified_passing_case_count": "NOT MEASURED",
        "zig_v14_controller_failure_semantic_mismatch_count": "NOT MEASURED",
        "zig_v14_controller_failure_corrected_warning_count": "NOT MEASURED",
        "expanded_holdout_proposed_case_count": HOLDOUT_PROPOSAL_COUNT,
        "preserved_previous_holdout_proposal_case_count":
        HISTORICAL_HOLDOUT_PROPOSAL_COUNT,
        "expanded_holdout_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "compressed_archives_opened_by_graph": 0,
        "compressed_archives_statted_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "clock_samples_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
        "outputs_written": outputs_written,
    }
    if additional:
        result.update(additional)
    return result


def self_test(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> dict:
    prior = previous.self_test(*chain, previous_options(previous))
    base.need(
        prior.get("status") == "PASS"
        and prior.get("version") == 95
        and type(prior.get("rejected_hostile_control_count")) is int
        and prior["rejected_hostile_control_count"] >= 13000
        and prior.get("authenticated_evidence_owner_lower_bound") == 336
        and prior.get("authenticated_history_reference_lower_bound") == 341
        and prior.get("lossless_previous_v94_proof_pool_count") == 16
        and prior.get("lossless_v94_all_sixteen_previous_pool_identity_status")
        == "PASS"
        and prior.get("rust_v22_original_campaign_verified_passing_case_count") == 14725
        and prior.get("rust_v22_original_campaign_observed_mismatch_lower_bound") == 2018
        and prior.get("c_v9_original_campaign_verified_passing_case_count") == 13606
        and prior.get("zig_v13_original_campaign_verified_passing_case_count") == 4607
        and prior.get("qualified_candidate_count") == 0
        and prior.get("performance") == "NOT MEASURED"
        and prior.get("outputs_written") is False,
        "preserve every full predecessor hostile-control test and immutable result",
    )
    _, assets = build(previous, chain, base, options)
    old = authenticate_previous(previous, chain, base)
    evidence = load_new_evidence(base)
    c_contract, c_receipt, c_facts, zig_contract, zig_receipt, zig_facts = evidence
    summary = base.document(assets[SUMMARY_PATH], "complete in-memory V96 summary")
    pool = summary[POOL_KEY]
    rejected = 0

    def reject(label: str, callback: object) -> None:
        nonlocal rejected
        try:
            if not callable(callback):
                raise ValueError("require a callable V96 hostile control")
            callback()
        except Exception:
            rejected += 1
        else:
            base.need(False, "V96 accepted fabricated public evidence: " + label)

    for key in sorted(C_CONTRACT_KEYS):
        forged = dict(c_contract)
        forged.pop(key)
        reject(
            "omitted actual frozen C contract field " + key,
            lambda value=forged: validate_c_contract(base, value),
        )
    for key, wrong in (
        ("schema", "invented"),
        ("version", 9),
        ("family", "zig"),
        ("candidate_correctness", "PASS"),
        ("candidate_qualification", "PASS"),
        ("runtime_non_delegation", "PASS"),
        ("qualified_candidate_count", 1),
        ("holdout", "OPENED"),
        ("performance", "FASTER"),
        ("winner_selected", True),
    ):
        forged = dict(c_contract)
        forged[key] = wrong
        reject("fabricated C source claim " + key, lambda value=forged: validate_c_contract(base, value))
    for key in sorted(C_RECEIPT_KEYS):
        forged = dict(c_receipt)
        forged.pop(key)
        reject(
            "omitted complete actual C receipt field " + key,
            lambda value=forged: validate_c_receipt(base, value),
        )
    for key, wrong in (
        ("schema", "invented"),
        ("status", "FAIL"),
        ("publication_status", "FAIL"),
        ("publication_pass_means", "CANDIDATE PASS"),
        ("family", "zig"),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("suite_count", 12),
        ("attempted_suite_count", 12),
        ("completed_suite_count", 13),
        ("actual_candidate_workers", 12),
        ("verified_passing_case_count", 31237),
        ("observed_semantic_mismatch_lower_bound", 492),
        ("semantic_mismatch_count", 606),
        ("candidate_execution_failure_count", 0),
        ("infrastructure_failure_count", 5),
        ("worker_timeout_count", 1),
        ("separate_reference_case_count", 0),
        ("separate_reference_cases_counted_as_candidate_cases", True),
        ("hidden_cases_read", 1),
        ("benchmark_files_read", 1),
        ("clock_samples", 1),
        ("timing_trials_run", 1),
        ("holdout", "OPENED"),
        ("performance", "FASTER"),
        ("winner_selected", True),
    ):
        forged = dict(c_receipt)
        forged[key] = wrong
        reject("fabricated actual C result " + key, lambda value=forged: validate_c_receipt(base, value))
    for index, (suite, _) in enumerate(SUITES):
        for key in sorted(C_ROW_KEYS):
            forged = dict(c_receipt)
            rows = list(c_receipt["suite_outcomes"])
            row = dict(rows[index])
            row.pop(key)
            rows[index] = row
            forged["suite_outcomes"] = rows
            reject(
                "omitted actual C worker field " + suite + ":" + key,
                lambda value=forged: validate_c_receipt(base, value),
            )
        for field, wrong in (
            ("suite", "invented"),
            ("worker_process_id", 0),
            ("case_execution_denominator", 0),
            ("actual_candidate_workers", 0),
            ("status", "invented"),
            ("failure_class", "invented"),
            ("mismatch_count", -1),
            ("failure_phase", "invented"),
            ("error_type", "invented"),
            ("plain_failure_diagnostic", "invented"),
        ):
            forged = dict(c_receipt)
            rows = list(c_receipt["suite_outcomes"])
            row = dict(rows[index])
            row[field] = wrong
            rows[index] = row
            forged["suite_outcomes"] = rows
            reject(
                "forged complete authenticated C row " + suite + ":" + field,
                lambda value=forged: validate_c_receipt(base, value),
            )
    for key in sorted(ZIG_RECEIPT_KEYS):
        forged = dict(zig_receipt)
        forged.pop(key)
        reject(
            "omitted actual Zig controller failure field " + key,
            lambda value=forged: validate_zig_controller(base, value),
        )
    for key in sorted(ZIG_CONTRACT_KEYS):
        forged = dict(zig_contract)
        forged.pop(key)
        reject(
            "omitted complete frozen Zig V14 contract field " + key,
            lambda value=forged: validate_zig_contract(base, value),
        )
    for key, wrong in (
        ("schema", "invented"),
        ("version", 13),
        ("family", "c"),
        ("corrected_original_matching", "PASS"),
        ("corrected_supplemental_matching", "PASS"),
        ("corrected_warning", 0),
        ("corrected_subinterpreter", "PASS"),
        ("current_qualified_candidates", 1),
        ("qualified_candidate_count", 1),
        ("holdout", "OPENED"),
        ("performance", "FASTER"),
        ("winner_selected", True),
    ):
        forged = dict(zig_contract)
        forged[key] = wrong
        reject(
            "fabricated frozen Zig V14 claim " + key,
            lambda value=forged: validate_zig_contract(base, value),
        )
    for key, wrong in (
        ("schema", "invented"),
        ("status", "PASS"),
        ("family", "c"),
        ("attempt_count", 2),
        ("pipeline_exit_code", 0),
        ("candidate_status", "PASS"),
        ("actual_candidate_worker_count", 13),
        ("actual_completed_suite_count", 13),
        ("actual_verified_passing_case_count", 31237),
        ("actual_semantic_mismatch_count", 0),
        ("corrected_finalizer_warning_count", 0),
        ("historical_v13_verified_passing_case_count", 31237),
        ("historical_v13_warning_worker_count", 0),
        ("all_three_original_targets_restored", False),
        ("recovery_root_created", True),
        ("failure_archive_created", True),
        ("failure_receipt_created", True),
        ("success_archive_created", True),
        ("success_receipt_created", True),
        ("holdout", "OPENED"),
        ("performance", "FASTER"),
        ("qualified_candidate_count", 1),
        ("winner_selected", True),
    ):
        forged = dict(zig_receipt)
        forged[key] = wrong
        reject(
            "fabricated Zig matching from a controller failure " + key,
            lambda value=forged: validate_zig_controller(base, value),
        )
    for role in ("adapter", "bridge", "engine"):
        for field, wrong in (
            ("sha256", "0" * 64),
            ("bytes", 0),
            ("inode", 0),
            ("mode", "0777"),
            ("nlink", 2),
        ):
            forged = dict(zig_receipt)
            roles = dict(zig_receipt["restored_original_targets"])
            item = dict(roles[role])
            item[field] = wrong
            roles[role] = item
            forged["restored_original_targets"] = roles
            reject(
                "forged restored Zig metadata " + role + ":" + field,
                lambda value=forged: validate_zig_controller(base, value),
            )
    for key in sorted(zig_receipt["frozen_authority"]):
        forged = dict(zig_receipt)
        authority = dict(zig_receipt["frozen_authority"])
        authority.pop(key)
        forged["frozen_authority"] = authority
        reject(
            "omitted actual Zig controller frozen authority " + key,
            lambda value=forged: validate_zig_controller(base, value),
        )
    for key, size, expected, count in previous_pools(previous, chain):
        forged = dict(old)
        forged.pop(key)
        reject(
            "omitted exact V95 predecessor evidence pool " + key,
            lambda value=forged: validate_previous(previous, chain, base, value),
        )
        forged = dict(old)
        changed = dict(old[key])
        changed["entries"] = {}
        forged[key] = changed
        reject(
            "discarded complete V95 predecessor evidence pool " + key,
            lambda value=forged: validate_previous(previous, chain, base, value),
        )
    for key, wrong in (
        ("version", 94),
        ("authenticated_evidence_owner_lower_bound", 332),
        ("authenticated_history_reference_lower_bound", 337),
        ("original_case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("rust_v22_original_campaign_verified_passing_case_count", 15749),
        ("c_v9_original_campaign_observed_mismatch_lower_bound", 606),
        ("zig_v13_original_campaign_cleanup_warning_worker_count", 0),
        ("qualified_candidate_count", 1),
        ("performance", "FASTER"),
        ("expanded_holdout_case_status", "OPENED"),
        ("winner_selected", True),
    ):
        forged = dict(old)
        forged[key] = wrong
        reject(
            "invented complete predecessor result " + key,
            lambda value=forged: validate_previous(previous, chain, base, value),
        )
    for family, owner in (("c", C_RECEIPT), ("zig", ZIG14_RECEIPT)):
        reference = summary[C_LATEST_KEY if family == "c" else ZIG_CONTROLLER_KEY]
        for field, wrong in (
            ("schema", "invented"),
            ("family", "invented"),
            ("complete_plaintext_receipt_sha256", "0" * 64),
            ("complete_plaintext_receipt_bytes", 1),
            ("complete_reference_sha256", "0" * 64),
            ("complete_reference_canonical_bytes", 1),
        ):
            forged = dict(reference)
            forged[field] = wrong
            reject(
                "fabricated complete " + family + " evidence reference " + field,
                lambda value=forged, name=family: resolve_reference(
                    base, pool, value, name
                ),
            )
        for field in (
            "complete_plaintext_receipt",
            "complete_source_contract",
            "complete_first_party_source_owners",
            "validated_campaign_outcome" if family == "c"
            else "validated_controller_outcome",
        ):
            forged = dict(pool)
            entries = dict(pool["entries"])
            item = dict(entries[owner[1]])
            item.pop(field)
            entries[owner[1]] = item
            forged["entries"] = entries
            reject(
                "omitted complete actual " + family + " proof " + field,
                lambda value=forged: validate_evidence_pool(base, value, *evidence),
            )
    for event, arguments in (
        ("subprocess.Popen", ("candidate",)),
        ("os.posix_spawn", ("candidate",)),
        ("os.fork", ()),
        ("ctypes.dlopen", ("candidate.so",)),
        ("socket.connect", ("holdout",)),
        ("os.remove", (str(ROOT / "GOAL.md"),)),
        ("os.rename", (str(ROOT / "GOAL.md"), str(ROOT / "invented"))),
        ("os.mkdir", (str(ROOT / "private"),)),
        ("import", ("re", None, None, None, None)),
        ("import", ("_sre", None, None, None, None)),
        ("import", ("regex", None, None, None, None)),
        ("import", ("candidates.c_candidate", None, None, None, None)),
        ("import", ("gzip", None, None, None, None)),
        ("import", ("time", None, None, None, None)),
        ("open", (str(ROOT / INPUT_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / SUMMARY_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / SVG_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / "performance/holdout.json"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "private.json.gz"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "candidates/_zig_probe.so"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "invented-file"), "wb", os.O_WRONLY | os.O_CREAT)),
        ("open", ("/tmp/private-root", None, os.O_RDONLY)),
        ("open", (1, "wb", os.O_WRONLY)),
    ):
        reject(
            "forbidden source-only effect " + event,
            lambda name=event, values=arguments: audit_wall(name, values),
        )
    for label, callback in (
        ("direct stdout descriptor", lambda: os.write(1, b"forged")),
        ("direct stderr descriptor", lambda: os.write(2, b"forged")),
        ("direct output FileIO", lambda: _io.FileIO(str(ROOT / INPUT_PATH), "wb")),
        ("direct SVG FileIO", lambda: io.FileIO(str(ROOT / SVG_PATH), "wb")),
        ("inherited stdout FileIO", lambda: _io.FileIO(1, "w", closefd=False)),
        ("inherited stderr FileIO", lambda: io.FileIO(2, "w", closefd=False)),
    ):
        reject(label, callback)
    if ORIGINAL_OS_WRITEV is not None:
        reject("direct stdout writev", lambda: os.writev(1, [b"forged"]))
    base.need(rejected >= 450, "require complete new V96 hostile evidence controls")
    return result_payload(base, options, assets, False, {
        "schema": SCHEMA + "-source-only-self-test",
        "inherited_rejected_hostile_control_count":
        prior["rejected_hostile_control_count"],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count":
        prior["rejected_hostile_control_count"] + rejected,
    })


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {INPUT_PATH, SUMMARY_PATH, SVG_PATH}
        and type(raw) is bytes
        and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
        "publish only a bounded, exclusively created V96 evidence owner",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0, "write complete V96 evidence")
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_dev == 2064
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "authenticate every exclusively created V96 evidence byte",
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
    base.need(actual == raw, "reauthenticate every complete final V96 graph byte")


def parse(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-preview", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for role in V95:
        parser.add_argument("--previous-" + role + "-sha256", required=True)
    for role in C_SOURCE:
        parser.add_argument("--c-" + role + "-sha256", required=True)
    for role in ZIG14_SOURCE:
        parser.add_argument("--zig-" + role + "-sha256", required=True)
    parser.add_argument("--c-receipt-sha256", required=True)
    parser.add_argument("--zig-controller-receipt-sha256", required=True)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse(arguments)
    try:
        previous, chain, base = load_previous()
        if not options.render:
            install_source_wall()
        if options.self_test:
            result = self_test(previous, chain, base, options)
        else:
            _, assets = build(previous, chain, base, options)
            if options.render:
                for path, raw in assets.items():
                    publish(base, path, raw)
            result = result_payload(base, options, assets, bool(options.render))
            if options.render_preview:
                result["schema"] = SCHEMA + "-source-only-render-preview"
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V96 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
