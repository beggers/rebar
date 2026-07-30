#!/usr/bin/env python3
"""Show honest, reproducible progress toward a faster Python re replacement."""

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
SELF = "tools/render_candidate_current_overview_v95.py"
OUTPUT = "docs/evidence/candidate-current-overview-v95"
INPUT_PATH = OUTPUT + ".inputs.json"
SUMMARY_PATH = OUTPUT + ".summary.json"
SVG_PATH = OUTPUT + ".svg"
SCHEMA = "rebar-candidate-current-overview-v95"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
OWNER_LIMIT = 4 * 1024 * 1024
CASE_COUNT = 31237
SUPPLEMENTAL_CASE_COUNT = 8244
HOLDOUT_PROPOSAL_COUNT = 14155776
HISTORICAL_HOLDOUT_PROPOSAL_COUNT = 4194304
EVIDENCE_FLOOR = 336
HISTORY_FLOOR = 341

V94 = {
    "source": (
        "tools/render_candidate_current_overview_v94.py",
        "f5fc03f33ab5d26edab90538aa58a5bf3f8029685975f31c88a8df70828e5ee3",
        93969,
        430979,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v94.inputs.json",
        "59f0c46fc4c4e64f607850a7914bcea496db6652ec5930b7d476a5adf2cb575a",
        19615,
        430998,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v94.summary.json",
        "1885047737ae4345e0791c4c2b44297cf0edc029ae823640e857eca69c64048e",
        3705403,
        430999,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v94.svg",
        "49812bb7857b5b130bf8f9159897016d65bcb150a619e6eb5d9f17ade6e9d0c8",
        9430,
        431008,
    ),
}

RUST_SOURCE = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v22.py",
        "e88f242835781e9b70efa18e68a7b06b0b9368e91320ed596995ef0e16370c61",
        61761,
        430995,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V22.md",
        "c6a2a5db9c9c27974c29af01b3d7f7042bae73e254c638fe27813505ef11f396",
        6038,
        525307,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v22.json",
        "f1c021049e4bb173be8d47339920354e02c8c0194aead877b8474a128b5e158a",
        42352,
        525314,
    ),
}

RUST_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v16-rust-phase2-v22-rust-capture-shape-"
    "root-provenance-original-p0-v22-failures-publication-receipt.json",
    "7013c42f6309d94e094dd89cc8e9f24fe245c0cba5ca4791d35ffe5fa2b7dad7",
    47336,
    525371,
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

WORKER_PIDS = (81, 83, 84, 85, 86, 87, 88, 89, 90, 91, 188, 189, 190)
SUITE_ROW_SHA256 = {
    "original_bounded_v5": "c62495b7562e3fe9ee7b5718e840cd527fd5d455ba4c90475b44bdb159e36cc9",
    "public_v3": "3a9f52000cb1395b29e0dd5e80be02c08052ef6117c71327ad43ef1541426a1f",
    "scanner_v3": "46286308cc402a7f5242799e2933ac669301d7762673649d49fe45216bf2b25d",
    "buffer_v3": "0235f4e8dda286945498077ec113f51b6299ff3085ba973921b4b309d4fac3d3",
    "managed_v1": "a2a10abfd8cbac37711ec9e9ba8449d1fec9f4a8a84aba31cd81f0858240023c",
    "scanner_verbose_v1": "fa319638a8a293e3fbed5ccfe1bfe4e3f9cb8d2b9d8672fec4119dd2b7b228ff",
    "public_types_v1": "2eccbfd8f0c77e67f59d5dc6172a16ac78a9b466fe554fd0e99b642ffacd14ea",
    "substitution_v2": "c81076c70583a3307d563271c6aea6417fff69150dff2b1f713c88030796c546",
    "shape_v2": "1d49921f6d3bb468161c5d216b2d75366b8137e99d90470f05cd667414b76447",
    "public_surface_v19": "41e4cc287839fc321861f5767f2023774efd75e59c9fdf8a85b3261e4abad67c",
    "subinterpreter_v2": "0a763bf5aaaff32766e3dbb56a7ec42354bb585143a309674b7c8a9724dc0335",
    "pep688_v4": "d6f67cec3b1df33e11791370289ddd62a2b98b17c257875f0d23acfb099ee10d",
    "threaded_pattern_v1": "913de4de372ec2ce50304d8c56ff1a45bd7b5f9ac98c269ce9256f3d0dcebc90",
}
MISMATCHES = {
    "managed_v1": 42,
    "substitution_v2": 352,
    "shape_v2": 1624,
}

V94_ZIG_POOL = (
    "lossless_v94_zig_v13_original_campaign_evidence_pool",
    205726,
    "f983fc7ccee47fc606cc4d4235b43d742d7417a19653fc4929a8551400cffc2a",
    1,
)
V94_SNAPSHOT_SHA256 = (
    "a68ecb2322287ac578b857896e5d5ebce57d6bb3d2a81387bb4dc6568911c472"
)
V94_SNAPSHOT_BYTES = 12228

POOL_KEY = "lossless_v95_rust_v22_original_campaign_evidence_pool"
POOL_SCHEMA = SCHEMA + "-lossless-complete-rust-original-campaign-pool-v1"
ENTRY_SCHEMA = SCHEMA + "-lossless-complete-rust-original-campaign-entry-v1"
REFERENCE_SCHEMA = SCHEMA + "-complete-rust-original-campaign-reference-v1"
LATEST_KEY = "rust_v22_actual_original_campaign"

RECEIPT_KEYS = frozenset({
    "actual_candidate_workers",
    "actual_v22_build_archive_gzip_inflation_count",
    "actual_v22_build_archive_read_count",
    "actual_v22_build_archive_sha256",
    "actual_v22_build_contract_sha256",
    "actual_v22_build_private_root",
    "actual_v22_build_private_root_device",
    "actual_v22_build_private_root_inode",
    "actual_v22_build_protocol_sha256",
    "actual_v22_build_receipt_sha256",
    "actual_v22_build_source_sha256",
    "actual_v22_compiler_process_count",
    "actual_worker_process_ids",
    "all_four_original_targets_restored",
    "all_original_observation_vectors_complete",
    "all_original_suite_rows_validated_before_publication",
    "all_worker_failure_capture_count",
    "all_worker_failure_capture_scope",
    "all_worker_failure_captures",
    "archive",
    "attempted_suite_count",
    "benchmark_files_read",
    "campaign_contract_sha256",
    "campaign_protocol_sha256",
    "campaign_source_sha256",
    "candidate_qualified",
    "candidate_run_uses_both_complete_reference_vectors",
    "candidate_status",
    "case_execution_denominator",
    "clock_samples",
    "combined_bridge_source_bytes",
    "combined_bridge_source_sha256",
    "completed_suite_count",
    "corrected_public_adapter_bytes",
    "corrected_public_adapter_sha256",
    "corrected_reference_cache_records_sha256",
    "corrected_reference_case_count",
    "corrected_reference_process_ids",
    "corrected_reference_receipt_sha256",
    "corrected_reference_records_sha256",
    "current_overview_version",
    "distinct_worker_process_id_count",
    "duplicate_worker_process_id_count",
    "family",
    "group_atomic",
    "hidden_cases_read",
    "historical_authenticated_reference_count_before_publication",
    "historical_evidence_owner_count_before_publication",
    "holdout",
    "infrastructure_failure_count",
    "label",
    "memory",
    "missing_worker_process_id_count",
    "named_private_waiver_count",
    "native_bridge_bytes",
    "native_bridge_sha256",
    "native_engine_bytes",
    "native_engine_sha256",
    "new_repository_evidence_owner_count",
    "original_v5_producer_contract_sha256",
    "original_v5_producer_protocol_sha256",
    "original_v5_producer_source_sha256",
    "original_v5_producer_version",
    "performance",
    "power_failure_automatically_recovered",
    "preserved_previous_rust_semantic_mismatch_count",
    "preserved_previous_rust_verified_passing_case_count",
    "public_recovery_root",
    "publication_pass_means",
    "publication_status",
    "published_current_v86_inputs_sha256",
    "published_current_v86_source_sha256",
    "published_current_v86_summary_sha256",
    "published_current_v86_svg_sha256",
    "recovery_journal_sha256",
    "restoration_verified_before_publication",
    "restored_original_targets",
    "resulting_authenticated_reference_count",
    "resulting_repository_evidence_owner_count",
    "schema",
    "semantic_mismatch_count",
    "sigkill_automatically_recovered",
    "started_suite_count",
    "status",
    "suite_count",
    "suite_integrity",
    "timing_trials_run",
    "uncompressed_bytes",
    "uncompressed_chunk_count",
    "uncompressed_sha256",
    "undefined_behavior",
    "verified_passing_case_count",
    "winner_selected",
    "worker_failure_capture",
    "worker_failure_capture_complete",
    "worker_failure_capture_count",
})

ROW_KEYS = frozenset({
    "actual_worker_started",
    "case_execution_denominator",
    "complete_original_row_sha256",
    "failure_class",
    "fully_observed",
    "mismatch_count",
    "pid",
    "returncode",
    "suite",
    "verified_passing_case_count",
    "worker_attempted",
})

CAPTURE_KEYS = frozenset({
    "case_execution_denominator",
    "error_message",
    "error_type",
    "pid",
    "returncode",
    "semantic_mismatch_count",
    "stderr",
    "stdout",
    "suite",
    "traceback",
    "worker_failure_diagnostics",
})
STREAM_KEYS = frozenset({
    "available",
    "base64",
    "capture_limit_bytes",
    "captured_size_bytes",
    "category",
    "complete",
    "limit_bytes",
    "sha256",
    "size_bytes",
    "source_sha256",
    "source_size_bytes",
    "truncated",
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
BASE64_ALPHABET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
)
ORIGINAL_OS_WRITE = os.write
ORIGINAL_OS_WRITEV = getattr(os, "writev", None)
ORIGINAL_FILEIO = _io.FileIO


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    if not (type(size) is int and 0 < size <= OWNER_LIMIT):
        raise ValueError("reject an unbounded V95 public plaintext owner: " + label)
    if (
        not isinstance(relative, str)
        or relative.startswith("/")
        or ".." in relative.split("/")
        or relative.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
    ):
        raise ValueError("reject a private, native, or archived V95 owner")
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
            raise ValueError("reject substituted complete V95 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated complete V95 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject extended complete V95 owner: " + label)
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
            raise ValueError("reject changed complete V95 owner: " + label)
        return raw
    finally:
        os.close(handle)


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_EVENTS:
        raise ValueError("V95 source-only operation rejected " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if isinstance(name, str) and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise ValueError("V95 source-only import rejected " + name)
        return
    if event != "open":
        return
    if len(arguments) < 3:
        raise ValueError("V95 rejected an unauthenticated file open")
    path, mode, flags = arguments[:3]
    if not isinstance(path, str) or not isinstance(flags, int):
        raise ValueError("V95 rejected inherited descriptors and unverified owners")
    if mode not in (None, "r", "rb"):
        raise ValueError("V95 source-only operation cannot open writable files")
    if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
        os.O_CREAT | os.O_TRUNC | os.O_APPEND
    ):
        raise ValueError("V95 source-only operation cannot create or change files")
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        if normalized != str(ROOT) and not normalized.startswith(str(ROOT) + "/"):
            raise ValueError("V95 rejected private roots and unopened holdout cases")
    elif "/" in normalized or normalized in (".", ".."):
        raise ValueError("V95 rejected an escaped relative evidence owner")
    if (
        normalized.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
        or "candidate-current-overview-v95." in normalized
        or "/.git/" in normalized
        or "/__pycache__/" in normalized
        or "/performance/" in normalized
        or "/experiments/" in normalized
    ):
        raise ValueError("V95 rejected graph output, archive, native, or holdout")


def reject_descriptor_write(*arguments: object, **keywords: object) -> int:
    raise ValueError("V95 source-only operation rejected direct descriptor writing")


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
    ):
        raise ValueError("V95 source-only operation rejected direct _io writing")
    if opener is not None:
        raise ValueError("V95 source-only operation rejected a descriptor opener")
    return ORIGINAL_FILEIO(file, mode, closefd)


def install_source_wall() -> None:
    sys.addaudithook(audit_wall)
    os.write = reject_descriptor_write
    if ORIGINAL_OS_WRITEV is not None:
        os.writev = reject_descriptor_write
    _io.FileIO = guarded_fileio
    io.FileIO = guarded_fileio


def decode_base64(value: object, maximum: int, label: str) -> bytes:
    if not isinstance(value, str) or len(value) == 0 or len(value) % 4:
        raise ValueError("reject malformed captured base64: " + label)
    if len(value) > ((maximum + 2) // 3) * 4:
        raise ValueError("reject oversized captured base64: " + label)
    table = {character: index for index, character in enumerate(BASE64_ALPHABET)}
    result = bytearray()
    for start in range(0, len(value), 4):
        group = value[start:start + 4]
        if group[0] not in table or group[1] not in table:
            raise ValueError("reject malformed captured base64: " + label)
        a = table[group[0]]
        b = table[group[1]]
        last = start + 4 == len(value)
        if group[2] == "=":
            if not last or group[3] != "=" or b & 15:
                raise ValueError("reject noncanonical captured base64: " + label)
            result.append((a << 2) | (b >> 4))
        elif group[2] in table:
            c = table[group[2]]
            result.append((a << 2) | (b >> 4))
            result.append(((b & 15) << 4) | (c >> 2))
            if group[3] == "=":
                if not last or c & 3:
                    raise ValueError("reject noncanonical captured base64: " + label)
            elif group[3] in table:
                result.append(((c & 3) << 6) | table[group[3]])
            else:
                raise ValueError("reject malformed captured base64: " + label)
        else:
            raise ValueError("reject malformed captured base64: " + label)
        if len(result) > maximum:
            raise ValueError("reject oversized captured diagnostic stream: " + label)
    return bytes(result)


def load_previous() -> tuple[types.ModuleType, tuple, types.ModuleType]:
    raw = read_fixed(V94["source"], "whole actual published V94 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v94")
    previous.__file__ = str(ROOT / V94["source"][0])
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
        and previous.SCHEMA == "rebar-candidate-current-overview-v94"
        and previous.SELF == V94["source"][0]
        and tuple(previous.SUITES) == SUITES
        and len(SUITES) == 13
        and sum(count for _, count in SUITES) == CASE_COUNT
        and len(chain) == 3,
        "require exact isolated Python, complete V94 history, and original cases",
    )
    return previous, chain, base


def previous_options(previous: types.ModuleType) -> argparse.Namespace:
    pins: dict[str, object] = {
        "source_sha256": V94["source"][1],
        "source_bytes": V94["source"][2],
        "zig_receipt_sha256": previous.ZIG_RECEIPT[1],
    }
    for role, item in previous.V93.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.ZIG_SOURCE.items():
        pins["zig_" + role + "_sha256"] = item[1]
    return argparse.Namespace(**pins)


def previous_pools(previous: types.ModuleType, chain: tuple) -> tuple:
    pools = tuple(previous.previous_pools(chain[0])) + (V94_ZIG_POOL,)
    if len(pools) != 16 or len({item[0] for item in pools}) != 16:
        raise ValueError("require all sixteen exact complete V94 history pools")
    return pools


def validate_previous(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    value: object,
) -> dict:
    base.need(
        type(value) is dict
        and value.get("schema") == "rebar-candidate-current-overview-v94-summary"
        and value.get("version") == 94
        and value.get("status") == "PASS"
        and value.get("authenticated_evidence_owner_lower_bound") == 332
        and value.get("authenticated_history_reference_lower_bound") == 337
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
        "retain exact V94 baseline, sealed holdout, denominator, and history",
    )
    assert isinstance(value, dict)
    base.need(
        value.get("rust_v20_original_campaign_verified_passing_case_count") == 15749
        and value.get("rust_v20_original_campaign_observed_mismatch_lower_bound") == 1296
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
        and value.get("zig_v13_original_campaign_actual_child_guards_installed") == 0
        and value.get("lossless_v94_zig_v13_complete_plaintext_receipt_count") == 1
        and value.get("lossless_v94_zig_v13_complete_source_owner_count") == 3
        and value.get("lossless_v94_zig_v13_complete_original_suite_count") == 13,
        "preserve previous best Rust, all real C results, and all Zig warnings",
    )
    snapshot = value.get("snapshot")
    raw = base.canonical(snapshot)
    base.need(
        type(snapshot) is dict
        and snapshot.get("schema")
        == "rebar-candidate-current-overview-v94-compact-current-snapshot"
        and snapshot.get("version") == 94
        and len(raw) == V94_SNAPSHOT_BYTES
        and base.digest(raw) == V94_SNAPSHOT_SHA256,
        "retain every exact byte of the immutable actual V94 snapshot",
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
            "preserve the exact complete V94 evidence pool: " + key,
        )
    families = value.get("families")
    base.need(
        type(families) is list
        and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and families[0].get("correctness") == "BASELINE PASS",
        "retain Python and all six distinct first-party candidate families",
    )
    latest = value.get("latest_original_campaigns")
    base.need(
        type(latest) is dict
        and set(latest) == {"rust", "c", "zig"}
        and type(latest.get("rust")) is dict
        and latest["rust"].get("verified_passing_case_count") == 15749
        and latest["rust"].get("observed_semantic_mismatch_lower_bound") == 1296
        and type(value.get("headline")) is dict
        and value["headline"].get("verified_original_checks_by_candidate")
        == {
            "c": 13606,
            "cpp": "NOT MEASURED",
            "fortran": "NOT MEASURED",
            "go": "NOT MEASURED",
            "rust": 15749,
            "zig": 4607,
        },
        "preserve the genuine V94 Rust comparator rather than stale receipt history",
    )
    return value


def authenticate_previous(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> dict:
    snapshot, assets = previous.build(*chain, previous_options(previous))
    for role in ("inputs", "summary", "svg"):
        item = V94[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole published V94 " + role),
            "reconstruct all complete actual committed V94 " + role + " bytes",
        )
    old = base.document(assets[V94["summary"][0]], "whole immutable V94 summary")
    validate_previous(previous, chain, base, old)
    base.need(
        base.canonical(snapshot) == base.canonical(old["snapshot"]),
        "preserve the exact independently reproduced V94 graph snapshot",
    )
    return old


def validate_source_contract(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict
        and len(value) == 435
        and value.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v22-recoverable-source-freeze"
        and value.get("version") == 22
        and value.get("status") == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
        and value.get("source_sha256") == RUST_SOURCE["source"][1]
        and value.get("protocol_sha256") == RUST_SOURCE["protocol"][1]
        and value.get("cpython_version") == "3.14.6"
        and value.get("cpython_executable") == PYTHON
        and value.get("cpython_executable_sha256")
        == "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
        and value.get("case_execution_denominator") == CASE_COUNT
        and value.get("suite_count") == 13
        and value.get("private_waiver_count") == 13
        and value.get("supplemental_case_count") == SUPPLEMENTAL_CASE_COUNT
        and value.get("supplemental_cases_counted_in_original_denominator") is False
        and value.get("planned_actual_original_candidate_worker_count") == 13
        and value.get("actual_v20_verified_passing_case_count") == 15749
        and value.get("actual_v20_fully_observed_semantic_mismatch_lower_bound")
        == 1296
        and value.get("frozen_graph_version") == 86
        and value.get("candidate_correctness") == "NOT MEASURED"
        and value.get("candidate_matching") == "NOT RUN"
        and value.get("candidate_qualified") is False
        and value.get("qualified_candidate_count") == 0
        and value.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("memory") == "NOT MEASURED"
        and value.get("undefined_behavior") == "NOT MEASURED"
        and value.get("timing_trials_run") == 0
        and value.get("winner_selected") is False
        and value.get("actual_modes_require_v3_guard_before_candidate_import") is True
        and value.get("stdlib_regex_engine_allowed") is False,
        "authenticate all original source fields without treating a freeze as matching",
    )
    assert isinstance(value, dict)
    for field in (
        "actual_candidate_imports",
        "actual_candidate_workers_started",
        "actual_hidden_cases_read",
        "actual_clock_samples",
        "actual_compiler_processes_started",
        "actual_native_libraries_loaded",
        "actual_private_build_root_opens",
        "actual_private_build_root_stats",
        "actual_build_archive_opens",
        "actual_build_archive_inflations",
        "actual_reference_workers_started",
    ):
        base.need(
            type(value.get(field)) is int and value[field] == 0,
            "reject real source-freeze side effects or fabricated runtime proof: " + field,
        )
    suites = value.get("suites")
    base.need(
        type(suites) is list and len(suites) == 13,
        "preserve all thirteen original source-frozen Rust test groups",
    )
    for row, (suite, count) in zip(suites, SUITES, strict=True):
        base.need(
            type(row) is dict
            and row.get("id") == suite
            and row.get("case_execution_count") == count,
            "reject a changed frozen original Rust suite: " + suite,
        )
    return value


def decode_captured_stream(
    base: types.ModuleType,
    value: object,
    category: str,
) -> bytes:
    base.need(
        type(value) is dict
        and set(value) == STREAM_KEYS
        and value.get("available") is True
        and value.get("category") == category
        and value.get("capture_limit_bytes") == 65536
        and value.get("complete") is True
        and value.get("truncated") is False
        and type(value.get("captured_size_bytes")) is int
        and value.get("captured_size_bytes") == value.get("size_bytes")
        and value.get("size_bytes") == value.get("source_size_bytes")
        and value.get("sha256") == value.get("source_sha256"),
        "reject omitted, truncated, or misidentified real worker " + category,
    )
    assert isinstance(value, dict)
    raw = decode_base64(value["base64"], 65536, "complete failure " + category)
    base.need(
        len(raw) == value["captured_size_bytes"]
        and hashlib.sha256(raw).hexdigest() == value["sha256"]
        and base.checked(value["sha256"], "complete real " + category)
        == value["sha256"],
        "authenticate every complete captured Rust failure " + category + " byte",
    )
    return raw


def validate_nested_failure(
    base: types.ModuleType,
    stderr: bytes,
) -> dict:
    first = stderr.split(b"\n", 1)[0]
    marker = b"REBAR-V16-AUTHENTIC-PRODUCER-FAILURE "
    base.need(
        first.startswith(marker),
        "retain the complete authentic original Rust producer failure",
    )
    outer = base.document(
        first[len(marker):] + b"\n", "complete captured producer failure"
    )
    base.need(
        type(outer) is dict
        and outer.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v22-"
        "authenticated-original-producer-failure"
        and outer.get("status") == "FAIL"
        and outer.get("suite") == "subinterpreter_v2"
        and outer.get("candidate_family") == "rust"
        and outer.get("case_execution_denominator") == 128
        and outer.get("diagnostic_only") is True,
        "reject a fabricated successful original private-interpreter execution",
    )
    captured = outer["complete_canonical_failure_details"]
    base.need(
        type(captured) is dict
        and set(captured)
        == {
            "base64",
            "capture_limit_bytes",
            "captured_size_bytes",
            "complete",
            "source_sha256",
            "source_size_bytes",
            "truncated",
        }
        and captured.get("complete") is True
        and captured.get("truncated") is False
        and captured.get("captured_size_bytes") == captured.get("source_size_bytes")
        and type(captured.get("capture_limit_bytes")) is int,
        "retain every authentic nested original producer-failure byte",
    )
    nested_raw = decode_base64(
        captured["base64"], captured["capture_limit_bytes"], "nested original failure"
    )
    base.need(
        len(nested_raw) == captured["source_size_bytes"]
        and hashlib.sha256(nested_raw).hexdigest() == captured["source_sha256"],
        "authenticate the genuinely captured nested original interpreter failure",
    )
    failure = base.document(nested_raw, "complete real nested interpreter failure")
    base.need(
        type(failure) is dict
        and failure.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v5-genuine-nested-failure"
        and failure.get("status") == "FAIL"
        and failure.get("suite") == "subinterpreter_v2"
        and failure.get("candidate_family") == "rust"
        and failure.get("actual_candidate_subprocesses") == 0
        and failure.get("actual_child_guards_installed") == 0
        and failure.get("actual_guard_cleanup_interpreter_exec_calls") == 0
        and failure.get("expected_case_interpreter_exec_calls") == 394
        and failure.get("expected_interpreters_created") == 11,
        "distinguish expected interpreter counts from actual failed child guards",
    )
    original = failure["complete_original_failure_details"]
    base.need(
        type(original) is dict
        and original.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v4-genuine-nested-failure"
        and original.get("status") == "FAIL"
        and original.get("active_phase") == "create-genuine-owned-interpreter-A"
        and original.get("error_type") == "GuardError"
        and original.get("error_message")
        == "runtime guard blocked missing-or-fabricated-native-child-creation"
        and original.get("actual_case_interpreter_exec_calls") == 0
        and original.get("actual_guard_cleanup_interpreter_exec_calls") == 0
        and original.get("actual_initialization_interpreter_exec_calls") == 0
        and original.get("actual_interpreters_created") == 0
        and original.get("actual_interpreters_destroyed") == 0
        and original.get("actual_prepared_interpreter_ids") == []
        and original.get("completed_a_records") == []
        and original.get("completed_b_records") == []
        and original.get("completed_fresh_records") == []
        and original.get("completed_repeated_a_records") == []
        and original.get("pipe_ledgers") == [],
        "reject invented child interpreters, child guards, or completed child matching",
    )
    return failure


def validate_failure_capture(base: types.ModuleType, receipt: dict) -> dict:
    captures = receipt["all_worker_failure_captures"]
    base.need(
        type(captures) is list and len(captures) == 1,
        "retain the sole actual completely captured failed Rust worker",
    )
    detail = captures[0]
    base.need(
        type(detail) is dict
        and set(detail) == CAPTURE_KEYS
        and detail.get("suite") == "subinterpreter_v2"
        and detail.get("pid") == 188
        and detail.get("case_execution_denominator") == 128
        and detail.get("error_type") == "CampaignError"
        and detail.get("error_message")
        == "CampaignError: reject an incomplete, borrowed, or falsified V16 worker"
        and detail.get("returncode") == 2
        and detail.get("semantic_mismatch_count") == "NOT MEASURED",
        "retain the original failed worker without fabricating a matching result",
    )
    stdout = decode_captured_stream(base, detail["stdout"], "stdout")
    stderr = decode_captured_stream(base, detail["stderr"], "stderr")
    base.need(
        len(stdout) == 1052
        and hashlib.sha256(stdout).hexdigest()
        == "981d63efa1b23af1227a797aaa6d1857fb3b2c6c15c680c8e4ede054cefeed7e"
        and len(stderr) == 10183
        and hashlib.sha256(stderr).hexdigest()
        == "96858958d5329b881acc0581f548aeea5cee5b6429f4f10fc6a28419f676ee0b"
        and stderr.count(b"Exception ignored while calling deallocator") == 16
        and b"Pattern.__del__" in stderr
        and b"'NoneType' object has no attribute 'free'" in stderr
        and b"RuntimeWarning: remaining subinterpreters" in stderr,
        "retain all sixteen real warnings in the single complete failed worker",
    )
    payload = base.document(stdout, "complete actual failed Rust worker stdout")
    base.need(
        type(payload) is dict
        and payload.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v22-"
        "actual-original-suite-worker-failure"
        and payload.get("version") == 22
        and payload.get("status") == "FAIL"
        and payload.get("suite") == "subinterpreter_v2"
        and payload.get("error_type") == "ActualSuiteFailure"
        and payload.get("failure_class") == "INFRASTRUCTURE FAILURE"
        and payload.get("runtime_guard_installed_before_candidate_import") is True
        and payload.get("actual_candidate_workers") == 1
        and payload.get("actual_candidate_imports") == 1
        and payload.get("actual_native_libraries_loaded") == 2
        and payload.get("holdout") == "NOT OPENED"
        and payload.get("performance") == "NOT MEASURED"
        and payload.get("winner_selected") is False,
        "validate only the one captured guard, not invented guards for all workers",
    )
    traceback = detail["traceback"]
    base.need(
        type(traceback) is dict
        and set(traceback)
        == {
            "capture_limit_bytes",
            "captured_size_bytes",
            "complete",
            "source_sha256",
            "source_size_bytes",
            "text",
            "truncated",
            "unicode_transport",
        }
        and traceback.get("capture_limit_bytes") == 65536
        and traceback.get("captured_size_bytes") == 923
        and traceback.get("source_size_bytes") == 923
        and traceback.get("complete") is True
        and traceback.get("truncated") is False
        and traceback.get("unicode_transport") == "UTF-8 SURROGATEPASS; REVERSIBLE"
        and type(traceback.get("text")) is str
        and len(traceback["text"].encode("utf-8", "surrogatepass")) == 923
        and hashlib.sha256(
            traceback["text"].encode("utf-8", "surrogatepass")
        ).hexdigest()
        == "44c12197e1d8ebe7da081436299554602c441f0a557e46ca17df43494297135e"
        and traceback.get("source_sha256")
        == "44c12197e1d8ebe7da081436299554602c441f0a557e46ca17df43494297135e",
        "retain every exact original byte of the single real failure traceback",
    )
    diagnostics = detail["worker_failure_diagnostics"]
    base.need(
        type(diagnostics) is dict
        and set(diagnostics)
        == {
            "actual_child_returncode",
            "capture_version",
            "child_created",
            "communicate_calls",
            "communicate_exception",
            "first_communicate_recorded",
            "traceback_complete",
        }
        and diagnostics.get("actual_child_returncode") == 2
        and diagnostics.get("capture_version") == 16
        and diagnostics.get("child_created") is True
        and diagnostics.get("communicate_calls") == 1
        and diagnostics.get("communicate_exception") is None
        and diagnostics.get("first_communicate_recorded") is True
        and diagnostics.get("traceback_complete") is True,
        "distinguish one real outer subprocess from genuine Python subinterpreters",
    )
    nested = validate_nested_failure(base, stderr)
    capture = receipt["worker_failure_capture"]
    base.need(
        type(capture) is dict
        and set(capture)
        == {
            "actual_failure_count",
            "all_failure_metadata_preserved",
            "diagnostic_stream_limit_bytes",
            "diagnostic_traceback_limit_bytes",
            "first_worker_failure",
            "schema",
            "suite_failure_summaries",
            "total_diagnostic_budget_bytes",
        }
        and capture.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v22-"
        "complete-bounded-worker-failure-capture"
        and capture.get("actual_failure_count") == 1
        and capture.get("all_failure_metadata_preserved") is True
        and capture.get("diagnostic_stream_limit_bytes") == 65536
        and capture.get("diagnostic_traceback_limit_bytes") == 65536
        and capture.get("total_diagnostic_budget_bytes") == 4194304
        and type(capture.get("suite_failure_summaries")) is list
        and len(capture["suite_failure_summaries"]) == 1,
        "preserve both different complete and projected real failure representations",
    )
    first = capture["first_worker_failure"]
    base.need(
        type(first) is dict
        and set(first)
        == {
            "error_message",
            "error_type",
            "pid",
            "returncode",
            "stderr",
            "stderr_complete",
            "stderr_sha256",
            "stderr_size_bytes",
            "stdout",
            "stdout_complete",
            "stdout_sha256",
            "stdout_size_bytes",
            "suite",
            "traceback",
            "traceback_complete",
            "traceback_sha256",
        }
        and first.get("suite") == "subinterpreter_v2"
        and first.get("pid") == 188
        and first.get("returncode") == 2
        and first.get("error_type") == "CampaignError"
        and first.get("error_message") == detail["error_message"]
        and first.get("stdout_complete") is True
        and first.get("stderr_complete") is True
        and first.get("traceback_complete") is True
        and first.get("stdout_sha256") == detail["stdout"]["sha256"]
        and first.get("stdout_size_bytes") == 1052
        and first.get("stderr_sha256") == detail["stderr"]["sha256"]
        and first.get("stderr_size_bytes") == 10183
        and first.get("traceback_sha256") == traceback["source_sha256"]
        and base.canonical(first.get("stdout")) == base.canonical(detail["stdout"])
        and base.canonical(first.get("stderr")) == base.canonical(detail["stderr"])
        and base.canonical(first.get("traceback")) == base.canonical(traceback)
        and base.canonical(first) != base.canonical(detail),
        "reject conflation of the exact real and projected failure-capture schemas",
    )
    summary = capture["suite_failure_summaries"][0]
    base.need(
        type(summary) is dict
        and set(summary)
        == {
            "error_message",
            "error_type",
            "pid",
            "returncode",
            "stderr_complete",
            "stderr_sha256",
            "stderr_size_bytes",
            "stdout_complete",
            "stdout_sha256",
            "stdout_size_bytes",
            "suite",
            "traceback_complete",
            "traceback_sha256",
        }
        and summary.get("suite") == "subinterpreter_v2"
        and summary.get("pid") == 188
        and summary.get("returncode") == 2
        and summary.get("error_type") == "CampaignError"
        and summary.get("error_message") == detail["error_message"]
        and summary.get("stdout_complete") is True
        and summary.get("stderr_complete") is True
        and summary.get("traceback_complete") is True
        and summary.get("stdout_sha256") == detail["stdout"]["sha256"]
        and summary.get("stderr_sha256") == detail["stderr"]["sha256"]
        and summary.get("traceback_sha256") == traceback["source_sha256"]
        and summary.get("stdout_size_bytes") == 1052
        and summary.get("stderr_size_bytes") == 10183,
        "retain the genuine complete bounded single-failure metadata summary",
    )
    return {
        "actual_failure_count": 1,
        "outer_worker_subprocess_created": True,
        "actual_child_returncode": 2,
        "actual_genuine_child_interpreters_created": 0,
        "actual_genuine_child_guards_installed": 0,
        "actual_genuine_child_case_execution_count": 0,
        "warning_worker_count_proven": 1,
        "complete_failure_worker_warning_count": 16,
        "complete_failure_worker_stderr_bytes": 10183,
        "complete_failure_worker_stderr_sha256": detail["stderr"]["sha256"],
        "complete_failure_worker_stdout_bytes": 1052,
        "complete_failure_worker_stdout_sha256": detail["stdout"]["sha256"],
        "complete_failure_worker_traceback_bytes": 923,
        "complete_failure_worker_traceback_sha256": traceback["source_sha256"],
        "remaining_subinterpreter_runtime_warning_count": 1,
        "all_rust_worker_warning_count": "NOT MEASURED",
        "per_worker_guard_installation_count": "NOT MEASURED",
        "captured_single_failure_guard_installed_before_candidate_import": True,
        "complete_capture_schema_distinct_from_projection": True,
        "nested_genuine_failure_schema": nested["schema"],
    }


def validate_rust_receipt(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and set(value) == RECEIPT_KEYS,
        "authenticate all 96 complete actual Rust V22 plaintext receipt fields",
    )
    assert isinstance(value, dict)
    base.need(
        value["schema"]
        == "rebar-owned-repaired-rust-original-campaign-v22-durable-publication-receipt"
        and value["family"] == "rust"
        and value["label"] == "phase2-v22-rust-capture-shape-root-provenance-original-p0-v22"
        and value["status"] == "PASS"
        and value["publication_status"] == "PASS"
        and value["publication_pass_means"] == "DURABLE PUBLICATION ONLY"
        and value["candidate_status"] == "FAIL"
        and value["candidate_qualified"] is False
        and value["campaign_source_sha256"] == RUST_SOURCE["source"][1]
        and value["campaign_protocol_sha256"] == RUST_SOURCE["protocol"][1]
        and value["campaign_contract_sha256"] == RUST_SOURCE["contract"][1]
        and value["case_execution_denominator"] == CASE_COUNT
        and value["named_private_waiver_count"] == 13
        and value["suite_count"] == 13
        and value["attempted_suite_count"] == 13
        and value["started_suite_count"] == 13
        and value["actual_candidate_workers"] == 13
        and value["actual_worker_process_ids"] == list(WORKER_PIDS)
        and value["distinct_worker_process_id_count"] == 13
        and value["duplicate_worker_process_id_count"] == 0
        and value["missing_worker_process_id_count"] == 0
        and value["completed_suite_count"] == 12
        and value["verified_passing_case_count"] == 14725
        and value["semantic_mismatch_count"] == "NOT MEASURED"
        and value["infrastructure_failure_count"] == 1
        and value["all_original_observation_vectors_complete"] is False
        and value["all_original_suite_rows_validated_before_publication"] is True
        and value["all_four_original_targets_restored"] is True
        and value["restoration_verified_before_publication"] is True
        and value["group_atomic"] is False
        and value["power_failure_automatically_recovered"] is False
        and value["sigkill_automatically_recovered"] is False
        and value["current_overview_version"] == 86
        and value["preserved_previous_rust_verified_passing_case_count"] == 14853
        and value["preserved_previous_rust_semantic_mismatch_count"] == 1440
        and value["corrected_reference_case_count"] == 6912
        and value["corrected_reference_process_ids"] == [81, 82]
        and value["candidate_run_uses_both_complete_reference_vectors"] is True
        and value["all_worker_failure_capture_count"] == 1
        and value["worker_failure_capture_count"] == 1
        and value["worker_failure_capture_complete"] is True
        and value["all_worker_failure_capture_scope"]
        == "COMPLETE INDIVIDUAL BOUNDED STDOUT STDERR TRACEBACK; ACTUAL "
        "INFRASTRUCTURE ONLY"
        and value["hidden_cases_read"] == 0
        and value["benchmark_files_read"] == 0
        and value["clock_samples"] == 0
        and value["timing_trials_run"] == 0
        and value["holdout"] == "NOT OPENED"
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["undefined_behavior"] == "NOT MEASURED"
        and value["winner_selected"] is False,
        "reject publication-as-success, omitted Rust regressions, or invented speed",
    )
    archive = value["archive"]
    base.need(
        type(archive) is dict
        and set(archive)
        == {
            "device",
            "directory_fsync_completed",
            "exclusive_creation",
            "file_fsync_completed",
            "inode",
            "mode",
            "path",
            "relative",
            "same_inode_readback_verified",
            "sha256",
            "size_bytes",
            "streaming_readback_verified",
            "write_calls",
        }
        and archive.get("relative")
        == "repaired-rust-original-campaign-v16-rust-phase2-v22-rust-capture-"
        "shape-root-provenance-original-p0-v22-failures.json.gz"
        and archive.get("path")
        == str(
            ROOT
            / "oracle/phase2/evidence/"
            "repaired-rust-original-campaign-v16-rust-phase2-v22-rust-capture-"
            "shape-root-provenance-original-p0-v22-failures.json.gz"
        )
        and archive.get("sha256")
        == "2358931770c81fd9d358507c249dc247ca7fb03ae5e4fe03e9b8b2311621eab5"
        and archive.get("size_bytes") == 3755965
        and archive.get("device") == 2064
        and archive.get("inode") == 525368
        and archive.get("mode") == 384
        and archive.get("exclusive_creation") is True
        and archive.get("file_fsync_completed") is True
        and archive.get("directory_fsync_completed") is True
        and archive.get("same_inode_readback_verified") is True
        and archive.get("streaming_readback_verified") is True
        and archive.get("write_calls") == 21
        and value["uncompressed_bytes"] == 5820020
        and value["uncompressed_sha256"]
        == "041f0e8725177594ff7ed8016e74d935cb285fe1cfcb054dad1fd9608bef20b1",
        "preserve actual archive metadata only without opening or statting archive",
    )
    targets = value["restored_original_targets"]
    base.need(
        type(targets) is dict and set(targets)
        == {"adapter", "bridge", "bridge_source", "engine"},
        "retain all four actually restored candidate target metadata owners",
    )
    for role, expected in (
        ("adapter", (
            "candidates/rust_candidate.py",
            "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
            31151,
            428100,
            384,
        )),
        ("bridge", (
            "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
            "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15",
            144992,
            430629,
            493,
        )),
        ("bridge_source", (
            "candidates/rust/py_bridge.c",
            "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
            175676,
            419054,
            384,
        )),
        ("engine", (
            "candidates/_rust_engine.so",
            "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4",
            660440,
            430563,
            493,
        )),
    ):
        relative, digest, size, inode, mode = expected
        item = targets[role]
        base.need(
            type(item) is dict
            and set(item)
            == {"bytes", "device", "inode", "mode", "nlink", "path", "relative", "sha256", "size_bytes", "uid"}
            and item.get("relative") == relative
            and item.get("path") == str(ROOT / relative)
            and item.get("sha256") == digest
            and item.get("bytes") == size
            and item.get("size_bytes") == size
            and item.get("device") == 2064
            and item.get("inode") == inode
            and item.get("mode") == mode
            and item.get("nlink") == 1
            and item.get("uid") == os.geteuid(),
            "retain real restored target metadata without opening native code: " + role,
        )
    rows = value["suite_integrity"]
    base.need(
        type(rows) is list and len(rows) == 13,
        "retain all thirteen actual Rust worker integrity observations",
    )
    clean: list[dict] = []
    mismatches: list[dict] = []
    incomplete: list[dict] = []
    pids: set[int] = set()
    for index, (row, (suite, denominator)) in enumerate(zip(rows, SUITES, strict=True)):
        base.need(
            type(row) is dict
            and set(row) == ROW_KEYS
            and row.get("suite") == suite
            and row.get("case_execution_denominator") == denominator
            and row.get("pid") == WORKER_PIDS[index]
            and row["pid"] not in pids
            and row.get("worker_attempted") is True
            and row.get("actual_worker_started") is True
            and base.checked(
                row.get("complete_original_row_sha256"),
                "actual original Rust worker record " + suite,
            ) == SUITE_ROW_SHA256[suite],
            "reject an omitted, invented, or duplicated actual Rust worker: " + suite,
        )
        pids.add(row["pid"])
        if suite == "subinterpreter_v2":
            base.need(
                row.get("failure_class") == "INFRASTRUCTURE FAILURE"
                and row.get("fully_observed") is False
                and row.get("mismatch_count") == "NOT MEASURED"
                and row.get("verified_passing_case_count") == 0
                and row.get("returncode") == 2,
                "retain the genuinely incomplete original interpreter case group",
            )
            incomplete.append(row)
        elif suite in MISMATCHES:
            base.need(
                row.get("failure_class") == "SEMANTIC MISMATCH"
                and row.get("fully_observed") is True
                and row.get("mismatch_count") == MISMATCHES[suite]
                and row.get("verified_passing_case_count") == 0
                and row.get("returncode") == 1,
                "retain every actually observed Rust mismatch group: " + suite,
            )
            mismatches.append(row)
        else:
            base.need(
                row.get("failure_class") == "PASS"
                and row.get("fully_observed") is True
                and row.get("mismatch_count") == 0
                and row.get("verified_passing_case_count") == denominator
                and row.get("returncode") == 0,
                "reject an invented fully passing Rust test group: " + suite,
            )
            clean.append(row)
    base.need(
        len(pids) == 13
        and tuple(row["pid"] for row in rows) == WORKER_PIDS
        and len(clean) == 9
        and len(mismatches) == 3
        and len(incomplete) == 1
        and len(clean) + len(mismatches) == 12
        and sum(row["verified_passing_case_count"] for row in clean) == 14725
        and {row["suite"]: row["mismatch_count"] for row in mismatches} == MISMATCHES
        and sum(row["mismatch_count"] for row in mismatches) == 2018,
        "derive all real Rust passes and observed mismatch lower bounds from evidence",
    )
    failure = validate_failure_capture(base, value)
    return {
        "family": "rust",
        "display_name": "Rust",
        "actual_candidate_worker_count": 13,
        "unique_candidate_worker_count": 13,
        "actual_worker_process_ids": list(WORKER_PIDS),
        "attempted_suite_count": 13,
        "started_suite_count": 13,
        "clean_suite_count": 9,
        "completed_suite_count": 12,
        "mismatch_suite_count": 3,
        "infrastructure_failure_count": 1,
        "infrastructure_failure_suite": "subinterpreter_v2",
        "verified_passing_case_count": 14725,
        "observed_semantic_mismatch_lower_bound": 2018,
        "aggregate_semantic_mismatch_count": "NOT MEASURED",
        "case_execution_denominator": CASE_COUNT,
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "all_original_suite_rows_validated": True,
        "all_original_observation_vectors_complete": False,
        "all_four_original_targets_restored": True,
        "complete_worker_failure_capture_count": 1,
        "historical_best_verified_passing_case_count": 15749,
        "verified_passing_case_regression_from_v94": -1024,
        "historical_best_observed_mismatch_lower_bound": 1296,
        "observed_mismatch_lower_bound_increase_from_v94": 722,
        "receipt_historical_graph_version": 86,
        "receipt_historical_rust_verified_passing_case_count": 14853,
        "receipt_historical_rust_semantic_mismatch_count": 1440,
        "source_sha256": RUST_SOURCE["source"][1],
        "protocol_sha256": RUST_SOURCE["protocol"][1],
        "contract_sha256": RUST_SOURCE["contract"][1],
        "archive_metadata_sha256": archive["sha256"],
        "archive_metadata_bytes": archive["size_bytes"],
        "archive_opened_by_graph": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "failed_worker_capture": failure,
    }


def load_rust_evidence(base: types.ModuleType) -> tuple[dict, dict, dict]:
    raws = {
        role: read_fixed(item, "whole first-party Rust V22 " + role)
        for role, item in RUST_SOURCE.items()
    }
    contract = base.document(raws["contract"], "whole actual Rust V22 contract")
    base.need(
        base.canonical(contract) == raws["contract"],
        "reject a partial or noncanonical actual Rust V22 source contract",
    )
    validate_source_contract(base, contract)
    raw = read_fixed(RUST_RECEIPT, "whole actual Rust V22 plaintext outcome receipt")
    receipt = base.document(raw, "whole actual Rust V22 public receipt")
    base.need(
        base.canonical(receipt) == raw,
        "reject a partial or synthetic actual Rust V22 plaintext receipt",
    )
    return contract, receipt, validate_rust_receipt(base, receipt)


def compact_suite_proof(base: types.ModuleType, row: dict) -> dict:
    raw = base.canonical(row)
    return {
        "suite": row["suite"],
        "case_execution_denominator": row["case_execution_denominator"],
        "complete_integrity_row_sha256": base.digest(raw),
        "complete_integrity_row_canonical_bytes": len(raw),
        "complete_original_row_sha256_from_receipt_metadata":
        row["complete_original_row_sha256"],
        "actual_worker_process_id": row["pid"],
        "actual_worker_started": row["actual_worker_started"],
        "worker_attempted": row["worker_attempted"],
        "fully_observed": row["fully_observed"],
        "failure_class": row["failure_class"],
        "mismatch_count": row["mismatch_count"],
        "verified_passing_case_count": row["verified_passing_case_count"],
        "returncode": row["returncode"],
    }


def make_evidence_pool(
    base: types.ModuleType,
    contract: dict,
    receipt: dict,
    facts: dict,
) -> dict:
    entry = {
        "schema": ENTRY_SCHEMA,
        "family": "rust",
        "complete_plaintext_receipt_owner": base.synthetic_owner(
            RUST_RECEIPT[:3], RUST_RECEIPT[3]
        ),
        "complete_plaintext_receipt_sha256": RUST_RECEIPT[1],
        "complete_plaintext_receipt_bytes": RUST_RECEIPT[2],
        "complete_plaintext_receipt_field_count": len(RECEIPT_KEYS),
        "complete_plaintext_receipt_embedded": True,
        "complete_plaintext_receipt": copy.deepcopy(receipt),
        "complete_first_party_source_owner_count": 3,
        "complete_first_party_source_owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in RUST_SOURCE.items()
        },
        "complete_source_contract_field_count": 435,
        "complete_source_contract_embedded": True,
        "complete_source_contract": copy.deepcopy(contract),
        "complete_original_suite_count": 13,
        "complete_original_suite_rows": [
            compact_suite_proof(base, row) for row in receipt["suite_integrity"]
        ],
        "complete_public_archive_metadata": copy.deepcopy(receipt["archive"]),
        "complete_actual_failure_capture": copy.deepcopy(
            receipt["all_worker_failure_captures"][0]
        ),
        "complete_projected_failure_capture": copy.deepcopy(
            receipt["worker_failure_capture"]
        ),
        "validated_campaign_outcome": copy.deepcopy(facts),
        "compressed_archive_opened_by_graph": False,
        "compressed_archive_statted_by_graph": False,
        "private_build_root_opened_by_graph": False,
        "complete_failure_diagnostics_available_without_archive": True,
    }
    pool = {
        "schema": POOL_SCHEMA,
        "version": 1,
        "hash_algorithm": "sha256",
        "complete_public_receipt_count": 1,
        "complete_first_party_source_owner_count": 3,
        "entries": {RUST_RECEIPT[1]: entry},
    }
    validate_evidence_pool(base, pool, contract, receipt, facts)
    return pool


def validate_evidence_pool(
    base: types.ModuleType,
    pool: object,
    contract: dict,
    receipt: dict,
    facts: dict,
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
        and pool.get("complete_public_receipt_count") == 1
        and pool.get("complete_first_party_source_owner_count") == 3
        and type(pool.get("entries")) is dict
        and set(pool["entries"]) == {RUST_RECEIPT[1]},
        "require the exact independently recoverable actual Rust receipt",
    )
    assert isinstance(pool, dict)
    entry = pool["entries"][RUST_RECEIPT[1]]
    rows = [compact_suite_proof(base, row) for row in receipt["suite_integrity"]]
    base.need(
        type(entry) is dict
        and entry.get("schema") == ENTRY_SCHEMA
        and entry.get("family") == "rust"
        and base.canonical(entry.get("complete_plaintext_receipt_owner"))
        == base.canonical(base.synthetic_owner(RUST_RECEIPT[:3], RUST_RECEIPT[3]))
        and entry.get("complete_plaintext_receipt_sha256") == RUST_RECEIPT[1]
        and entry.get("complete_plaintext_receipt_bytes") == RUST_RECEIPT[2]
        and entry.get("complete_plaintext_receipt_field_count") == len(RECEIPT_KEYS)
        and entry.get("complete_plaintext_receipt_embedded") is True
        and base.canonical(entry.get("complete_plaintext_receipt"))
        == base.canonical(receipt)
        and entry.get("complete_first_party_source_owner_count") == 3
        and entry.get("complete_source_contract_field_count") == 435
        and entry.get("complete_source_contract_embedded") is True
        and base.canonical(entry.get("complete_source_contract"))
        == base.canonical(contract)
        and entry.get("complete_original_suite_count") == 13
        and base.canonical(entry.get("complete_original_suite_rows"))
        == base.canonical(rows)
        and base.canonical(entry.get("complete_public_archive_metadata"))
        == base.canonical(receipt["archive"])
        and base.canonical(entry.get("complete_actual_failure_capture"))
        == base.canonical(receipt["all_worker_failure_captures"][0])
        and base.canonical(entry.get("complete_projected_failure_capture"))
        == base.canonical(receipt["worker_failure_capture"])
        and base.canonical(entry.get("validated_campaign_outcome"))
        == base.canonical(facts)
        and entry.get("compressed_archive_opened_by_graph") is False
        and entry.get("compressed_archive_statted_by_graph") is False
        and entry.get("private_build_root_opened_by_graph") is False
        and entry.get("complete_failure_diagnostics_available_without_archive") is True,
        "reject omitted actual Rust failure, source, archive metadata, or workers",
    )
    owners = entry["complete_first_party_source_owners"]
    base.need(
        type(owners) is dict and set(owners) == set(RUST_SOURCE),
        "preserve exactly the three authentic V22 first-party source owners",
    )
    for role, item in RUST_SOURCE.items():
        base.need(
            base.canonical(owners[role])
            == base.canonical(base.synthetic_owner(item[:3], item[3])),
            "reject fabricated actual Rust V22 owner: " + role,
        )


def make_reference(base: types.ModuleType, pool: dict) -> dict:
    raw = base.canonical(pool["entries"][RUST_RECEIPT[1]])
    return {
        "schema": REFERENCE_SCHEMA,
        "family": "rust",
        "complete_plaintext_receipt_sha256": RUST_RECEIPT[1],
        "complete_plaintext_receipt_bytes": RUST_RECEIPT[2],
        "complete_first_party_source_owner_count": 3,
        "complete_reference_sha256": base.digest(raw),
        "complete_reference_canonical_bytes": len(raw),
    }


def resolve_reference(
    base: types.ModuleType,
    pool: dict,
    value: object,
) -> dict:
    base.need(
        type(value) is dict
        and set(value)
        == {
            "schema",
            "family",
            "complete_plaintext_receipt_sha256",
            "complete_plaintext_receipt_bytes",
            "complete_first_party_source_owner_count",
            "complete_reference_sha256",
            "complete_reference_canonical_bytes",
        }
        and value.get("schema") == REFERENCE_SCHEMA
        and value.get("family") == "rust"
        and value.get("complete_plaintext_receipt_sha256") == RUST_RECEIPT[1]
        and value.get("complete_plaintext_receipt_bytes") == RUST_RECEIPT[2]
        and value.get("complete_first_party_source_owner_count") == 3,
        "reject a fabricated actual complete Rust V22 reference",
    )
    assert isinstance(value, dict)
    entry = pool["entries"].get(RUST_RECEIPT[1])
    raw = base.canonical(entry)
    base.need(
        type(entry) is dict
        and base.checked(value["complete_reference_sha256"], "whole Rust V22 proof")
        == base.digest(raw)
        and value["complete_reference_canonical_bytes"] == len(raw),
        "reject a missing genuine Rust failure, regression, or captured stream",
    )
    return copy.deepcopy(entry)


def make_changes(reference: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 94,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v95_new_directly_authenticated_owner_count": 4,
        "v95_new_directly_authenticated_rust_source_owner_count": 3,
        "v95_new_directly_authenticated_rust_plaintext_receipt_owner_count": 1,
        "lossless_previous_v94_proof_pool_count": 16,
        "lossless_v94_all_sixteen_previous_pool_identity_status": "PASS",
        "lossless_v94_snapshot_identity_status": "PASS",
        "lossless_v94_family_identity_status": "PASS",
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "rust_v22_original_campaign_actual_worker_count": 13,
        "rust_v22_original_campaign_distinct_worker_count": 13,
        "rust_v22_original_campaign_attempted_suite_count": 13,
        "rust_v22_original_campaign_clean_suite_count": 9,
        "rust_v22_original_campaign_completed_suite_count": 12,
        "rust_v22_original_campaign_mismatch_suite_count": 3,
        "rust_v22_original_campaign_verified_passing_case_count": 14725,
        "rust_v22_original_campaign_observed_mismatch_lower_bound": 2018,
        "rust_v22_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "rust_v22_original_campaign_infrastructure_failure_count": 1,
        "rust_v22_original_campaign_infrastructure_failure_suite": "subinterpreter_v2",
        "rust_v22_original_campaign_historical_best_verified_passing_case_count": 15749,
        "rust_v22_original_campaign_verified_passing_case_change_from_v94": -1024,
        "rust_v22_original_campaign_previous_mismatch_lower_bound": 1296,
        "rust_v22_original_campaign_mismatch_lower_bound_increase_from_v94": 722,
        "rust_v22_original_campaign_receipt_historical_graph_version": 86,
        "rust_v22_original_campaign_receipt_historical_verified_passing_case_count":
        14853,
        "rust_v22_original_campaign_actual_failure_capture_count": 1,
        "rust_v22_original_campaign_outer_failed_worker_subprocess_created": True,
        "rust_v22_original_campaign_genuine_child_interpreters_created": 0,
        "rust_v22_original_campaign_genuine_child_guards_installed": 0,
        "rust_v22_original_campaign_genuine_child_case_execution_count": 0,
        "rust_v22_original_campaign_complete_failure_worker_warning_count": 16,
        "rust_v22_original_campaign_proven_warning_worker_count": 1,
        "rust_v22_original_campaign_all_worker_warning_count": "NOT MEASURED",
        "rust_v22_original_campaign_per_worker_guard_installation_count":
        "NOT MEASURED",
        "rust_v22_original_campaign_all_four_original_targets_restored": True,
        "rust_v22_original_campaign_candidate_status": "FAIL",
        "rust_v22_original_campaign_candidate_qualified": False,
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
        LATEST_KEY: copy.deepcopy(reference),
    }


def make_svg() -> bytes:
    rows = (
        ("Python re", CASE_COUNT, "13 of 13 original groups passed", "BASELINE", "#34d399"),
        (
            "Rust",
            14725,
            "9 passed; 3 differ; 1 unfinished; down 1,024",
            "REGRESSED",
            "#fb7185",
        ),
        (
            "C",
            13606,
            "3 passed; 4 differ; 6 failed to complete",
            "NOT YET COMPATIBLE",
            "#fbbf24",
        ),
        (
            "Zig",
            4607,
            "7 passed; 5 differ; 1 unfinished; warnings",
            "NOT YET COMPATIBLE",
            "#fbbf24",
        ),
        (
            "C++",
            None,
            "Full current matching result not measured",
            "NOT MEASURED",
            "#94a3b8",
        ),
        (
            "Go",
            None,
            "Full current matching result not measured",
            "NOT MEASURED",
            "#94a3b8",
        ),
        (
            "Fortran",
            None,
            "Builds disagreed; matching not measured",
            "BUILD FAILED",
            "#fb7185",
        ),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1080" '
        'viewBox="0 0 1440 1080" role="img" aria-labelledby="title description">',
        '<title id="title">How close are from-scratch alternatives to Python re?</title>',
        '<desc id="description">These bars show verified matching checks, not speed. '
        'Standard Python passes all 31,237 original checks. The latest Rust attempt '
        'passes 14,725, a regression of 1,024 compared with the separately preserved '
        'previous 15,749-check Rust result. It has nine passing groups, three fully '
        'observed mismatch groups containing at least 2,018 real differences, and '
        'one incomplete interpreter group. The single completely captured failed '
        'Rust worker emitted 16 deallocator warnings; no warning claim is made for '
        'the other workers. The outer worker subprocess was real, but no genuine '
        'nested Python interpreter or child guard was created. C verifies 13,606 '
        'checks. Zig verifies 4,607; all 13 Zig workers emitted cleanup warnings, '
        'with at least 143 captured examples. C++, Go, and Fortran do not have '
        'a fully measured current matching result. Speed and memory are not measured. '
        'The separate 8,244 checks are not added to the denominator. The proposed '
        '14,155,776-case comparison remains unfrozen and unopened. No winner.</desc>',
        '<rect width="1440" height="1080" rx="24" fill="#0b1220"/>',
        '<text x="46" y="64" fill="#f8fafc" font-size="32" '
        'font-family="system-ui,sans-serif" font-weight="740">'
        'Building a faster Python re, from scratch</text>',
        '<text x="47" y="103" fill="#cbd5e1" font-size="17" '
        'font-family="system-ui,sans-serif">Six independent approaches · '
        'no fully compatible replacement · no winner</text>',
        '<rect x="44" y="125" width="1352" height="78" rx="13" fill="#172338"/>',
        '<text x="63" y="156" fill="#f8fafc" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'The bars measure matching correctness, not speed.</text>',
        '<text x="63" y="181" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif">Every result uses the same 31,237 original '
        'Python checks. Failed, unfinished, and unmeasured checks are never '
        'counted as passes.</text>',
        '<text x="48" y="242" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">APPROACH</text>',
        '<text x="154" y="242" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'ORIGINAL CHECKS CONFIRMED</text>',
        '<text x="704" y="242" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">WHAT THE TESTS SHOW</text>',
        '<text x="1128" y="242" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">SPEED VS PYTHON</text>',
        '<text x="1393" y="242" text-anchor="end" fill="#94a3b8" '
        'font-size="12" font-family="system-ui,sans-serif" '
        'font-weight="690">RESULT</text>',
        '<line x1="44" y1="258" x2="1396" y2="258" stroke="#334155"/>',
    ]
    for index, (name, passed, details, result, colour) in enumerate(rows):
        y = 301 + 67 * index
        parts.append(
            f'<text x="49" y="{y}" fill="#f8fafc" font-size="16" '
            f'font-family="system-ui,sans-serif" font-weight="670">{name}</text>'
        )
        parts.append(
            f'<rect x="153" y="{y - 16}" width="314" height="20" '
            'rx="6" fill="#1e293b"/>'
        )
        if passed is None:
            count_label = "NOT MEASURED"
        else:
            width = max(3, round(314 * passed / CASE_COUNT))
            percent = 100 * passed / CASE_COUNT
            label = "100%" if passed == CASE_COUNT else f"{percent:.1f}%"
            parts.append(
                f'<rect x="153" y="{y - 16}" width="{width}" height="20" '
                f'rx="6" fill="{colour}"/>'
            )
            count_label = f"{passed:,} / {CASE_COUNT:,} ({label})"
        parts.append(
            f'<text x="478" y="{y}" fill="#e2e8f0" font-size="12" '
            f'font-family="system-ui,sans-serif">{count_label}</text>'
        )
        parts.append(
            f'<text x="704" y="{y}" fill="#cbd5e1" font-size="12" '
            f'font-family="system-ui,sans-serif">{details}</text>'
        )
        parts.append(
            f'<text x="1129" y="{y}" fill="#94a3b8" font-size="11" '
            'font-family="system-ui,sans-serif">NOT MEASURED</text>'
        )
        parts.append(
            f'<text x="1393" y="{y}" text-anchor="end" fill="{colour}" '
            f'font-size="10" font-family="system-ui,sans-serif" '
            f'font-weight="730">{result}</text>'
        )
    parts.extend((
        '<line x1="44" y1="748" x2="1396" y2="748" stroke="#334155"/>',
        '<text x="49" y="780" fill="#f8fafc" font-size="17" '
        'font-family="system-ui,sans-serif" font-weight="700">'
        'What changed in the latest Rust attempt?</text>',
        '<text x="49" y="806" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">Rust fell from 15,749 to 14,725 '
        'confirmed checks: 1,024 fewer. A previously passing 1,024-check '
        'group now has 42 real differences.</text>',
        '<text x="49" y="831" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">Three groups show at least 2,018 '
        'differences. The full difference total is NOT MEASURED because one '
        'interpreter group could not complete.</text>',
        '<text x="49" y="856" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">The one fully captured failed Rust '
        'worker emitted 16 cleanup warnings. No successful nested interpreter '
        'or child guard was created.</text>',
        '<text x="49" y="881" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">The separate Zig result still '
        'contains warnings from all 13 workers, with at least 143 recorded examples. '
        'All earlier results are preserved.</text>',
        '<rect x="44" y="902" width="1352" height="108" rx="13" fill="#172338"/>',
        '<text x="63" y="932" fill="#f8fafc" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="680">'
        'Future speed comparison: proposed 14,155,776 cases</text>',
        '<text x="63" y="957" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">NOT FROZEN · NOT GENERATED · '
        'NOT OPENED · NOT RUN. Speed, memory, confidence, and rankings: '
        'NOT MEASURED.</text>',
        '<text x="63" y="982" fill="#cbd5e1" font-size="12" '
        'font-family="system-ui,sans-serif">The separate 8,244 reference checks '
        'are not included in the 31,237-check original comparison.</text>',
        '<text x="49" y="1046" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif">Overview 95 · regression shown · '
        'all previous evidence preserved · no winner · no unmeasured speed claim</text>',
        "</svg>",
        "",
    ))
    return "\n".join(parts).encode("utf-8")


def validate_families(
    base: types.ModuleType,
    old: dict,
    families: object,
    pool: dict,
    reference: dict,
    facts: dict,
) -> None:
    base.need(
        type(families) is list
        and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "retain unchanged Python and all six original independent engine families",
    )
    assert isinstance(families, list)
    for row, original in zip(families, old["families"], strict=True):
        family = original["family"]
        base.need(
            type(row) is dict and row.get("family") == family,
            "reject a removed or invented original first-party family: " + family,
        )
        if family == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "preserve every byte of the original unchanged Python baseline",
            )
            continue
        base.need(
            row.get("authenticated_evidence_owner_lower_bound") == EVIDENCE_FLOOR
            and row.get("authenticated_history_reference_lower_bound") == HISTORY_FLOOR
            and row.get("qualified") is False
            and row.get("runtime_no_delegation") == "NOT ESTABLISHED"
            and row.get("performance") == "NOT MEASURED",
            "reject fabricated compatibility, independence, or speed: " + family,
        )
        restored = copy.deepcopy(row)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        if family == "rust":
            evidence = resolve_reference(base, pool, row.get(LATEST_KEY))
            base.need(
                base.canonical(evidence["validated_campaign_outcome"])
                == base.canonical(facts)
                and base.canonical(row.get("v95_latest_original_campaign"))
                == base.canonical(facts)
                and base.canonical(row.get(LATEST_KEY)) == base.canonical(reference),
                "retain the exact real Rust regression and both failure captures",
            )
            restored.pop(LATEST_KEY)
            restored.pop("v95_latest_original_campaign")
        base.need(
            base.canonical(restored) == base.canonical(original),
            "retain complete V94 family history without replacing old evidence: "
            + family,
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
        "caller-pin the whole immutable V95 graph renderer source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "whole immutable V95 renderer"),
        options.source_bytes,
        private=True,
    )
    for role, item in V94.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin complete actual V94 predecessor " + role,
        )
    for role, item in RUST_SOURCE.items():
        base.need(
            getattr(options, "rust_" + role + "_sha256") == item[1],
            "caller-pin exact actual V22 Rust source owner " + role,
        )
    base.need(
        options.rust_receipt_sha256 == RUST_RECEIPT[1],
        "caller-pin the entire actual tiny Rust V22 public receipt",
    )
    old = authenticate_previous(previous, chain, base)
    contract, receipt, facts = load_rust_evidence(base)
    pool = make_evidence_pool(base, contract, receipt, facts)
    reference = make_reference(base, pool)
    changes = make_changes(reference)
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V94.items()
    }
    source_owners = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in RUST_SOURCE.items()
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update({
        "schema": SCHEMA + "-compact-current-snapshot",
        "version": 95,
        "previous_complete_snapshot_sha256": V94_SNAPSHOT_SHA256,
        "previous_complete_snapshot_canonical_bytes": V94_SNAPSHOT_BYTES,
        "previous_complete_overview_sha256": V94["summary"][1],
        "previous_complete_overview_bytes": V94["summary"][2],
        **copy.deepcopy(changes),
    })
    headline = copy.deepcopy(old["headline"])
    headline["verified_original_checks_by_candidate"]["rust"] = 14725
    headline["latest_complete_candidate_mismatch_totals"] = "NOT MEASURED"
    headline["fully_compatible_candidate_count"] = 0
    headline["performance"] = "NOT MEASURED"
    headline["memory"] = "NOT MEASURED"
    headline["winner_selected"] = False
    headline["bars_measure"] = "VERIFIED ORIGINAL CORRECTNESS CHECKS; NOT SPEED"
    headline["speed_relative_to_python"] = "NOT MEASURED"
    headline["rust_current_verified_original_checks"] = 14725
    headline["rust_previous_best_verified_original_checks"] = 15749
    headline["rust_verified_check_change_from_previous_graph"] = -1024
    headline["rust_observed_mismatch_lower_bound"] = 2018
    headline["rust_complete_mismatch_total"] = "NOT MEASURED"
    headline["rust_failed_worker_cleanup_warning_count"] = 16
    headline["rust_all_worker_cleanup_warning_count"] = "NOT MEASURED"
    headline["rust_incomplete_original_suite_count"] = 1
    inputs = {
        "schema": SCHEMA + "-inputs",
        "version": 95,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": copy.deepcopy(predecessor),
        "rust_v22_source_owners": copy.deepcopy(source_owners),
        "rust_v22_plaintext_receipt_owner": base.pin(
            RUST_RECEIPT[0], RUST_RECEIPT[1], RUST_RECEIPT[2]
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
        if family == "rust":
            row[LATEST_KEY] = copy.deepcopy(reference)
            row["v95_latest_original_campaign"] = copy.deepcopy(facts)
    validate_families(base, old, families, pool, reference, facts)
    inputs_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 95,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(INPUT_PATH, base.digest(inputs_raw), len(inputs_raw)),
        "svg": base.pin(SVG_PATH, base.digest(svg_raw), len(svg_raw)),
        "previous_overview": copy.deepcopy(predecessor),
        "previous_v94_snapshot": copy.deepcopy(old["snapshot"]),
        "previous_v94_snapshot_canonical_sha256": V94_SNAPSHOT_SHA256,
        "previous_v94_snapshot_canonical_bytes": V94_SNAPSHOT_BYTES,
        "snapshot": copy.deepcopy(snapshot),
        "headline": copy.deepcopy(headline),
        "families": families,
        POOL_KEY: pool,
        "lossless_v95_rust_v22_complete_plaintext_receipt_count": 1,
        "lossless_v95_rust_v22_complete_source_owner_count": 3,
        "lossless_v95_rust_v22_complete_original_suite_count": 13,
        "preserved_v94_latest_original_campaigns": copy.deepcopy(
            old["latest_original_campaigns"]
        ),
        "latest_original_campaigns": {
            **copy.deepcopy(old["latest_original_campaigns"]),
            "rust": copy.deepcopy(facts),
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
            "retain every exact V94 proof-pool byte: " + key,
        )
    base.need(
        base.canonical(summary["previous_v94_snapshot"])
        == base.canonical(old["snapshot"])
        and base.canonical(summary["previous_v93_snapshot"])
        == base.canonical(old["previous_v93_snapshot"])
        and base.canonical(summary["previous_v92_snapshot"])
        == base.canonical(old["previous_v92_snapshot"])
        and base.canonical(summary["previous_v91_snapshot"])
        == base.canonical(old["previous_v91_snapshot"])
        and base.canonical(summary["previous_v90_snapshot"])
        == base.canonical(old["previous_v90_snapshot"])
        and base.canonical(summary["previous_v89_snapshot"])
        == base.canonical(old["previous_v89_snapshot"])
        and base.canonical(summary["previous_v88_snapshot"])
        == base.canonical(old["previous_v88_snapshot"])
        and base.canonical(summary["families"][0]) == base.canonical(old["families"][0])
        and base.canonical(summary["latest_original_campaigns"]["c"])
        == base.canonical(old["latest_original_campaigns"]["c"])
        and base.canonical(summary["latest_original_campaigns"]["zig"])
        == base.canonical(old["latest_original_campaigns"]["zig"])
        and base.canonical(summary["preserved_v94_latest_original_campaigns"]["rust"])
        == base.canonical(old["latest_original_campaigns"]["rust"])
        and summary["rust_v20_original_campaign_verified_passing_case_count"] == 15749
        and summary["rust_v20_original_campaign_observed_mismatch_lower_bound"] == 1296
        and summary["rust_v22_original_campaign_verified_passing_case_count"] == 14725
        and summary["rust_v22_original_campaign_observed_mismatch_lower_bound"] == 2018
        and summary["rust_v22_original_campaign_verified_passing_case_change_from_v94"]
        == -1024
        and summary["rust_v22_original_campaign_mismatch_lower_bound_increase_from_v94"]
        == 722
        and summary["rust_v22_original_campaign_proven_warning_worker_count"] == 1
        and summary["rust_v22_original_campaign_complete_failure_worker_warning_count"]
        == 16
        and summary["rust_v22_original_campaign_all_worker_warning_count"]
        == "NOT MEASURED"
        and summary["rust_v22_original_campaign_genuine_child_interpreters_created"]
        == 0
        and summary["rust_v22_original_campaign_genuine_child_guards_installed"] == 0
        and summary["rust_v22_original_campaign_outer_failed_worker_subprocess_created"]
        is True
        and summary["c_v9_original_campaign_verified_passing_case_count"] == 13606
        and summary["zig_v13_original_campaign_verified_passing_case_count"] == 4607
        and summary["zig_v13_original_campaign_cleanup_warning_worker_count"] == 13
        and summary["zig_v13_original_campaign_cleanup_warning_captured_occurrence_lower_bound"]
        == 143
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
        "retain regression, all prior warnings, immutable history, and unopened holdout",
    )
    validate_evidence_pool(base, summary[POOL_KEY], contract, receipt, facts)
    recovered = resolve_reference(base, pool, reference)
    base.need(
        base.canonical(recovered["validated_campaign_outcome"]) == base.canonical(facts)
        and base.canonical(summary[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(snapshot[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(inputs[LATEST_KEY]) == base.canonical(reference),
        "retain complete independently verifiable Rust regression and failure capture",
    )
    assets = {
        INPUT_PATH: inputs_raw,
        SUMMARY_PATH: base.canonical(summary),
        SVG_PATH: svg_raw,
    }
    for path, raw in assets.items():
        base.need(
            type(raw) is bytes and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
            "reject oversized complete V95 graph evidence: " + path,
        )
    return snapshot, assets


def self_test(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> dict:
    prior = previous.self_test(*chain, previous_options(previous))
    base.need(
        prior.get("status") == "PASS"
        and prior.get("version") == 94
        and type(prior.get("rejected_hostile_control_count")) is int
        and prior["rejected_hostile_control_count"] >= 12871
        and prior.get("authenticated_evidence_owner_lower_bound") == 332
        and prior.get("authenticated_history_reference_lower_bound") == 337
        and prior.get("lossless_previous_v93_proof_pool_count") == 15
        and prior.get("lossless_v93_all_fifteen_previous_pool_identity_status") == "PASS"
        and prior.get("lossless_v94_zig_v13_complete_original_suite_count") == 13
        and prior.get("rust_v20_original_campaign_verified_passing_case_count") == 15749
        and prior.get("c_v9_original_campaign_verified_passing_case_count") == 13606
        and prior.get("zig_v13_original_campaign_verified_passing_case_count") == 4607
        and prior.get("zig_v13_original_campaign_cleanup_warning_worker_count") == 13
        and prior.get("zig_v13_original_campaign_cleanup_warning_captured_occurrence_lower_bound")
        == 143
        and prior.get("expanded_holdout_proposed_case_count") == HOLDOUT_PROPOSAL_COUNT
        and prior.get("qualified_candidate_count") == 0
        and prior.get("performance") == "NOT MEASURED"
        and prior.get("outputs_written") is False,
        "retain all actual inherited V94 rejection controls and immutable history",
    )
    _, assets = build(previous, chain, base, options)
    old = authenticate_previous(previous, chain, base)
    contract, receipt, facts = load_rust_evidence(base)
    summary = base.document(assets[SUMMARY_PATH], "whole in-memory V95 summary")
    pool = summary[POOL_KEY]
    reference = summary[LATEST_KEY]
    rejected = 0

    def reject(label: str, callback: object) -> None:
        nonlocal rejected
        try:
            if not callable(callback):
                raise ValueError("require a callable hostile control")
            callback()
        except Exception:
            rejected += 1
        else:
            base.need(False, "V95 accepted fabricated source evidence: " + label)

    for key in sorted(contract):
        forged = dict(contract)
        forged.pop(key)
        reject(
            "omitted complete frozen Rust source field " + key,
            lambda value=forged: validate_source_contract(base, value),
        )
    for key, wrong in (
        ("schema", "invented-source"),
        ("version", 21),
        ("source_sha256", "0" * 64),
        ("protocol_sha256", "0" * 64),
        ("case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("candidate_correctness", "PASS"),
        ("candidate_matching", "PASS"),
        ("candidate_qualified", True),
        ("qualified_candidate_count", 1),
        ("runtime_non_delegation", "PASS"),
        ("holdout", "OPENED"),
        ("performance", "FASTER"),
        ("winner_selected", True),
    ):
        forged = dict(contract)
        forged[key] = wrong
        reject(
            "fabricated Rust source-freeze field " + key,
            lambda value=forged: validate_source_contract(base, value),
        )
    for key in sorted(RECEIPT_KEYS):
        forged = dict(receipt)
        forged.pop(key)
        reject(
            "omitted complete actual Rust receipt field " + key,
            lambda value=forged: validate_rust_receipt(base, value),
        )
    for key, wrong in (
        ("schema", "invented-receipt"),
        ("family", "zig"),
        ("status", "FAIL"),
        ("publication_status", "FAIL"),
        ("publication_pass_means", "CANDIDATE PASS"),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("suite_count", 12),
        ("attempted_suite_count", 12),
        ("actual_candidate_workers", 12),
        ("distinct_worker_process_id_count", 12),
        ("completed_suite_count", 13),
        ("verified_passing_case_count", 15749),
        ("semantic_mismatch_count", 2018),
        ("infrastructure_failure_count", 0),
        ("all_original_observation_vectors_complete", True),
        ("all_four_original_targets_restored", False),
        ("restoration_verified_before_publication", False),
        ("current_overview_version", 94),
        ("preserved_previous_rust_verified_passing_case_count", 15749),
        ("all_worker_failure_capture_count", 0),
        ("worker_failure_capture_complete", False),
        ("hidden_cases_read", 1),
        ("benchmark_files_read", 1),
        ("clock_samples", 1),
        ("timing_trials_run", 1),
        ("holdout", "OPENED"),
        ("performance", "FASTER"),
        ("winner_selected", True),
    ):
        forged = dict(receipt)
        forged[key] = wrong
        reject(
            "fabricated actual Rust regression result " + key,
            lambda value=forged: validate_rust_receipt(base, value),
        )
    for index, (suite, _) in enumerate(SUITES):
        for key in sorted(ROW_KEYS):
            forged = dict(receipt)
            forged_rows = list(receipt["suite_integrity"])
            forged_row = dict(forged_rows[index])
            forged_row.pop(key)
            forged_rows[index] = forged_row
            forged["suite_integrity"] = forged_rows
            reject(
                "omitted actual Rust suite field " + suite + ":" + key,
                lambda value=forged: validate_rust_receipt(base, value),
            )
        for field, wrong in (
            ("suite", "invented"),
            ("pid", 0),
            ("case_execution_denominator", 0),
            ("fully_observed", "PASS"),
            ("worker_attempted", False),
            ("actual_worker_started", False),
            ("complete_original_row_sha256", "0" * 64),
        ):
            forged = dict(receipt)
            forged_rows = list(receipt["suite_integrity"])
            forged_row = dict(forged_rows[index])
            forged_row[field] = wrong
            forged_rows[index] = forged_row
            forged["suite_integrity"] = forged_rows
            reject(
                "invented real Rust worker " + suite + ":" + field,
                lambda value=forged: validate_rust_receipt(base, value),
            )
    for key, size, expected, count in previous_pools(previous, chain):
        forged = dict(old)
        forged.pop(key)
        reject(
            "omitted exact previous V94 proof pool " + key,
            lambda value=forged: validate_previous(previous, chain, base, value),
        )
        forged = dict(old)
        altered = dict(old[key])
        altered["entries"] = {}
        forged[key] = altered
        reject(
            "discarded previous V94 proof-pool evidence " + key,
            lambda value=forged: validate_previous(previous, chain, base, value),
        )
    for key, wrong in (
        ("version", 86),
        ("authenticated_evidence_owner_lower_bound", 333),
        ("authenticated_history_reference_lower_bound", 338),
        ("original_case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("rust_v20_original_campaign_verified_passing_case_count", 14853),
        ("qualified_candidate_count", 1),
        ("performance", "FASTER"),
        ("expanded_holdout_case_status", "OPENED"),
        ("winner_selected", True),
    ):
        forged = dict(old)
        forged[key] = wrong
        reject(
            "fabricated true V94 predecessor history " + key,
            lambda value=forged: validate_previous(previous, chain, base, value),
        )
    for field, wrong in (
        ("complete_plaintext_receipt_sha256", "0" * 64),
        ("complete_plaintext_receipt_bytes", 1),
        ("complete_reference_sha256", "0" * 64),
        ("complete_reference_canonical_bytes", 1),
        ("family", "zig"),
    ):
        forged = dict(reference)
        forged[field] = wrong
        reject(
            "fabricated actual Rust evidence reference " + field,
            lambda value=forged: resolve_reference(base, pool, value),
        )
    for field in (
        "complete_plaintext_receipt",
        "complete_source_contract",
        "complete_original_suite_rows",
        "complete_actual_failure_capture",
        "complete_projected_failure_capture",
        "validated_campaign_outcome",
    ):
        forged = dict(pool)
        entries = dict(pool["entries"])
        altered = dict(entries[RUST_RECEIPT[1]])
        altered.pop(field)
        entries[RUST_RECEIPT[1]] = altered
        forged["entries"] = entries
        reject(
            "omitted complete real Rust V22 campaign proof " + field,
            lambda value=forged: validate_evidence_pool(
                base, value, contract, receipt, facts
            ),
        )
    for encoded in (
        "",
        "A",
        "====",
        "AB==",
        "AAB=",
        "YWJj=",
        "YWJj\n",
        "YWJj===",
        "____",
        "A" * 65540,
    ):
        reject(
            "malformed captured diagnostic base64",
            lambda value=encoded: decode_base64(value, 16384, "hostile"),
        )
    for event, arguments in (
        ("subprocess.Popen", ("candidate",)),
        ("os.posix_spawn", ("candidate",)),
        ("os.fork", ()),
        ("ctypes.dlopen", ("candidate.so",)),
        ("socket.connect", ("holdout",)),
        ("os.remove", (str(ROOT / "GOAL.md"),)),
        ("os.rename", (str(ROOT / "GOAL.md"), str(ROOT / "forged"))),
        ("os.mkdir", (str(ROOT / "private"),)),
        ("import", ("re", None, None, None, None)),
        ("import", ("_sre", None, None, None, None)),
        ("import", ("regex", None, None, None, None)),
        ("import", ("candidates.rust_candidate", None, None, None, None)),
        ("import", ("gzip", None, None, None, None)),
        ("import", ("time", None, None, None, None)),
        ("open", (str(ROOT / SVG_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / INPUT_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / SUMMARY_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / "performance/holdout.json"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "private.json.gz"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "candidates/_rust_engine.so"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "new-file"), "wb", os.O_WRONLY | os.O_CREAT)),
        ("open", ("/tmp/private-root", None, os.O_RDONLY)),
        ("open", (1, "wb", os.O_WRONLY)),
    ):
        reject(
            "forbidden source-only effect " + event,
            lambda name=event, values=arguments: audit_wall(name, values),
        )
    for label, callback in (
        ("direct os.write to stdout", lambda: os.write(1, b"forged")),
        ("direct os.write to stderr", lambda: os.write(2, b"forged")),
        ("direct _io.FileIO graph output", lambda: _io.FileIO(str(ROOT / INPUT_PATH), "wb")),
        ("direct io.FileIO graph output", lambda: io.FileIO(str(ROOT / SVG_PATH), "wb")),
        ("direct _io inherited stdout", lambda: _io.FileIO(1, "w", closefd=False)),
        ("direct io inherited stderr", lambda: io.FileIO(2, "w", closefd=False)),
    ):
        reject(label, callback)
    if ORIGINAL_OS_WRITEV is not None:
        reject("direct os.writev to stdout", lambda: os.writev(1, [b"forged"]))
    base.need(rejected >= 700, "require complete real Rust regression hostile controls")
    return result_payload(base, options, assets, False, {
        "schema": SCHEMA + "-source-only-self-test",
        "inherited_rejected_hostile_control_count":
        prior["rejected_hostile_control_count"],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count":
        prior["rejected_hostile_control_count"] + rejected,
    })


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
        "version": 95,
        "status": "PASS",
        "source_sha256": options.source_sha256,
        "source_bytes": options.source_bytes,
        "inputs_sha256": base.digest(assets[INPUT_PATH]),
        "inputs_bytes": len(assets[INPUT_PATH]),
        "summary_sha256": base.digest(assets[SUMMARY_PATH]),
        "summary_bytes": len(assets[SUMMARY_PATH]),
        "svg_sha256": base.digest(assets[SVG_PATH]),
        "svg_bytes": len(assets[SVG_PATH]),
        "actual_current_graph_predecessor_version": 94,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v95_new_directly_authenticated_owner_count": 4,
        "v95_new_directly_authenticated_rust_source_owner_count": 3,
        "v95_new_directly_authenticated_rust_plaintext_receipt_owner_count": 1,
        "lossless_previous_v94_proof_pool_count": 16,
        "lossless_v94_all_sixteen_previous_pool_identity_status": "PASS",
        "lossless_v94_snapshot_identity_status": "PASS",
        "lossless_v94_family_identity_status": "PASS",
        "lossless_v94_zig_v13_complete_original_suite_count": 13,
        "lossless_v95_rust_v22_complete_plaintext_receipt_count": 1,
        "lossless_v95_rust_v22_complete_source_owner_count": 3,
        "lossless_v95_rust_v22_complete_original_suite_count": 13,
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "rust_v20_original_campaign_verified_passing_case_count": 15749,
        "rust_v20_original_campaign_observed_mismatch_lower_bound": 1296,
        "rust_v22_original_campaign_actual_worker_count": 13,
        "rust_v22_original_campaign_distinct_worker_count": 13,
        "rust_v22_original_campaign_clean_suite_count": 9,
        "rust_v22_original_campaign_completed_suite_count": 12,
        "rust_v22_original_campaign_mismatch_suite_count": 3,
        "rust_v22_original_campaign_verified_passing_case_count": 14725,
        "rust_v22_original_campaign_observed_mismatch_lower_bound": 2018,
        "rust_v22_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "rust_v22_original_campaign_infrastructure_failure_count": 1,
        "rust_v22_original_campaign_historical_best_verified_passing_case_count": 15749,
        "rust_v22_original_campaign_verified_passing_case_change_from_v94": -1024,
        "rust_v22_original_campaign_previous_mismatch_lower_bound": 1296,
        "rust_v22_original_campaign_mismatch_lower_bound_increase_from_v94": 722,
        "rust_v22_original_campaign_receipt_historical_graph_version": 86,
        "rust_v22_original_campaign_receipt_historical_verified_passing_case_count":
        14853,
        "rust_v22_original_campaign_actual_failure_capture_count": 1,
        "rust_v22_original_campaign_outer_failed_worker_subprocess_created": True,
        "rust_v22_original_campaign_genuine_child_interpreters_created": 0,
        "rust_v22_original_campaign_genuine_child_guards_installed": 0,
        "rust_v22_original_campaign_genuine_child_case_execution_count": 0,
        "rust_v22_original_campaign_complete_failure_worker_warning_count": 16,
        "rust_v22_original_campaign_proven_warning_worker_count": 1,
        "rust_v22_original_campaign_all_worker_warning_count": "NOT MEASURED",
        "rust_v22_original_campaign_per_worker_guard_installation_count":
        "NOT MEASURED",
        "rust_v22_original_campaign_all_four_original_targets_restored": True,
        "rust_v22_original_campaign_candidate_status": "FAIL",
        "rust_v22_original_campaign_candidate_qualified": False,
        "c_v9_original_campaign_verified_passing_case_count": 13606,
        "c_v9_original_campaign_observed_mismatch_lower_bound": 492,
        "c_v9_original_campaign_candidate_execution_failure_count": 6,
        "zig_v13_original_campaign_verified_passing_case_count": 4607,
        "zig_v13_original_campaign_observed_mismatch_lower_bound": 1700,
        "zig_v13_original_campaign_cleanup_warning_worker_count": 13,
        "zig_v13_original_campaign_cleanup_warning_captured_occurrence_lower_bound":
        143,
        "zig_v13_original_campaign_cleanup_warning_full_occurrence_count":
        "NOT MEASURED",
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


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {INPUT_PATH, SUMMARY_PATH, SVG_PATH}
        and type(raw) is bytes
        and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
        "publish only a bounded exclusively created V95 graph owner",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0, "publish complete V95 bytes")
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_dev == 2064
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "authenticate the whole exclusively published V95 graph owner",
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
    base.need(actual == raw, "reauthenticate each complete final V95 graph byte")


def parse(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-preview", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for role in V94:
        parser.add_argument("--previous-" + role + "-sha256", required=True)
    for role in RUST_SOURCE:
        parser.add_argument("--rust-" + role + "-sha256", required=True)
    parser.add_argument("--rust-receipt-sha256", required=True)
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
        sys.stderr.write("current V95 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
