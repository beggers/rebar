#!/usr/bin/env python3
"""Render only the genuinely recorded corrected-Zig compatibility result."""

from __future__ import annotations

import argparse
import builtins
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import types


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/render_candidate_current_overview_v34.py"
OUTPUT = "docs/evidence/candidate-current-overview-v34"
SCHEMA = "rebar-candidate-current-overview-v34"
LIMIT = 8 * 1024 * 1024
V33 = {
    "source": (
        "tools/render_candidate_current_overview_v33.py",
        "e81a1c032c550475c4a4ece9ae11b903d105d62e8666ce46b69138b260ca91d5",
        75615,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v33.inputs.json",
        "1f98790a6a31d8cdf298bf5fd13c6d4d14cfb44785e1e445d791c83557de921e",
        106942,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v33.json",
        "b56b5f0e09ff3aa3990b210934e1d73d1989bd03c6bb479a8a7abd66eb93a9a6",
        380577,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v33.svg",
        "203c15b16b74cf1dd8be3308677ddd67fa94a7a8411e5de38b43186647ccf858",
        13068,
    ),
}
CAMPAIGN_SOURCE = (
    "tools/run_owned_repaired_zig_original_campaign_v3.py",
    "e4efad7dfbe921bec9f7160cd33dbbed0376b1373037a78de8bcaabdcd2ece98",
    178576,
)
CAMPAIGN_PROTOCOL = (
    "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V3.md",
    "0463e23aaed9de6e1b50db7f106a1f175b504eefdbf868fa1f03ed5b313776d1",
    8448,
)
CAMPAIGN_CONTRACT = (
    "oracle/phase2/repaired-zig-original-campaign-v3.json",
    "4d20518685e2db7b80c9a1936f4ae480cff85c2a3b672562f6d4fded20b8328d",
    16316,
)
ARCHIVE = (
    "oracle/phase2/evidence/"
    "repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-"
    "v2-original-p0-failures.json.gz",
    "ab857c82369ea0c1a443d2d140c8009d7f4b5216b5ee6a0bb4e9280000cb9d6b",
    3722337,
    2064,
    524695,
)
RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-"
    "v2-original-p0-failures-publication-receipt.json",
    "40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96",
    4111,
    2064,
    524696,
)
BUILD_ARCHIVE = (
    "oracle/phase2/evidence/"
    "native-source-build-v12-zig-phase2-v12-zig-scanner-v2.json.gz",
    "3e0ccc41de392c17eaec64100776eacecafb3f0bb3355e18ef4d65fcdc79ea8d",
    48371,
)
BUILD_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v12-zig-phase2-v12-zig-scanner-"
    "v2-publication-receipt.json",
    "6269fb49b67919e772ffbcdd211c696aae871971ab524bc0b1612a797d4c2f9b",
    2029,
)
RECOVERY = "12a67b4c8f8a14a137375cef7a72b0a7508c6c6b16d3e665e9fbfd746590a31a"
BRIDGE_SOURCE = "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b"
ENGINE_NATIVE = "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071"
BRIDGE_NATIVE = "e5809566a166f469e7f95fc1a43e814a3beeeffa2a6e848c00a3a48215ee6726"
PRODUCER_SOURCE = "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c"
PRODUCER_PROTOCOL = "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76"
PRODUCER_CONTRACT = "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1"
ACTIVATION_SOURCE = "98002a0a283ffec24670bcb9f35546c5720d2a7a1d098257729d244918022f8e"
PUBLIC_RECOVERY = (
    "/tmp/rebar-phase2-repaired-zig-original-campaign-v3-"
    "phase2-v12-zig-scanner-v2-original-p0"
)
RESTORED = {
    "engine": {
        "relative": "candidates/_zig_probe.so",
        "sha256": "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652",
        "size_bytes": 478432,
        "device": 2064,
        "inode": 431260,
        "mode": 0o700,
        "nlink": 1,
        "uid": 1000,
    },
    "bridge": {
        "relative": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "sha256": "d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b",
        "size_bytes": 134112,
        "device": 2064,
        "inode": 431274,
        "mode": 0o700,
        "nlink": 1,
        "uid": 1000,
    },
}


class GraphError(Exception):
    """Reject fabricated compatibility, provenance, speed, or evidence."""


def need(value: object, reason: str) -> None:
    if value is not True:
        raise GraphError(reason)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only actual authenticated evidence bytes")
    return hashlib.sha256(raw).hexdigest()


def checked(value: object, label: str) -> str:
    need(
        type(value) is str and len(value) == 64
        and all(char in "0123456789abcdef" for char in value),
        "require an exact lowercase SHA-256 for " + label,
    )
    return value


def canonical(value: object) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False, sort_keys=True,
                separators=(",", ":"),
            ) + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise GraphError("reject noncanonical V34 evidence") from error


def document(raw: bytes, label: str) -> dict:
    def unique(items: list[tuple[str, object]]) -> dict:
        found: dict[str, object] = {}
        for key, value in items:
            need(key not in found, "reject duplicate JSON keys in " + label)
            found[key] = value
        return found

    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                GraphError("reject nonfinite JSON in " + label)
            ),
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise GraphError("reject malformed " + label) from error
    need(type(value) is dict and canonical(value) == raw,
         "require complete canonical " + label)
    return value


def runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
        and os.path.realpath(sys.executable) == PYTHON,
        "require exact isolated stable CPython 3.14.6",
    )


def pin(path: str, fingerprint: str, size: int) -> dict:
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT,
         "bound a frozen first-party graph owner")
    return {"path": path, "sha256": fingerprint, "bytes": size}


def read_owner(
    path: str, fingerprint: str, size: int, *, private: bool = False,
    device: int | None = None, inode: int | None = None,
    retain: bool = True,
) -> tuple[bytes | None, dict]:
    need(
        type(path) is str and bool(path) and not path.startswith("/")
        and "." not in Path(path).parts and ".." not in Path(path).parts,
        "reject escaped, absolute or substituted first-party owner",
    )
    checked(fingerprint, path)
    need(type(size) is int and 0 <= size <= LIMIT,
         "reject an unbounded or invented first-party owner " + path)
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    file_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptors: list[int] = []
    handle: int | None = None
    try:
        descriptors.append(os.open(str(ROOT), directory_flags))
        for part in Path(path).parts[:-1]:
            descriptors.append(os.open(part, directory_flags,
                                       dir_fd=descriptors[-1]))
        handle = os.open(Path(path).parts[-1], file_flags,
                         dir_fd=descriptors[-1])
        before = os.fstat(handle)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1 and before.st_size == size
            and (not private or stat.S_IMODE(before.st_mode) == 0o600)
            and (device is None or before.st_dev == device)
            and (inode is None or before.st_ino == inode),
            "reject replaced, linked, foreign, or nonprivate owner " + path,
        )
        hashed = hashlib.sha256()
        remaining = size
        pieces: list[bytes] = []
        while remaining:
            piece = os.read(handle, min(remaining, 1024 * 1024))
            need(bool(piece), "reject truncated exact owner " + path)
            hashed.update(piece)
            if retain:
                pieces.append(piece)
            remaining -= len(piece)
        need(os.read(handle, 1) == b"", "reject trailing owner bytes " + path)
        after = os.fstat(handle)
        need(
            (before.st_dev, before.st_ino, before.st_size,
             before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size,
                after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)
            and hashed.hexdigest() == fingerprint,
            "reject an owner changed during full authenticated read " + path,
        )
        return (b"".join(pieces) if retain else None), {
            "path": path, "sha256": fingerprint, "bytes": size,
            "device": after.st_dev, "inode": after.st_ino,
            "mode": f"{stat.S_IMODE(after.st_mode):04o}",
            "nlink": after.st_nlink, "uid": after.st_uid,
        }
    finally:
        if handle is not None:
            os.close(handle)
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def load_v33() -> types.ModuleType:
    raw, _ = read_owner(*V33["source"])
    need(type(raw) is bytes, "retain only the exact immutable V33 renderer")
    old = types.ModuleType("_rebar_actual_v33_corrected_zig_evidence_v34")
    old.__file__ = str(ROOT / V33["source"][0])
    old.__package__ = ""
    exec(compile(raw, old.__file__, "exec", dont_inherit=True),
         old.__dict__)
    need(
        old.SCHEMA == "rebar-candidate-current-overview-v33"
        and old.SELF == V33["source"][0]
        and old.ARCHIVE[1] == BUILD_ARCHIVE[1]
        and old.RECEIPT[1] == BUILD_RECEIPT[1],
        "reuse only the exact independently committed V33 source/build proof",
    )
    return old


def authenticate_v33() -> tuple[dict, dict, dict[str, str]]:
    old = load_v33()
    old_snapshot, produced = old.build(
        V33["source"][1], BUILD_ARCHIVE[1], BUILD_RECEIPT[1],
    )
    expected = dict(produced)
    actual: dict[str, bytes] = {}
    for name in ("inputs", "summary", "svg"):
        raw, _ = read_owner(*V33[name], private=True)
        need(type(raw) is bytes and raw == expected[V33[name][0]],
             "independently reproduce exact immutable V33 " + name)
        actual[name] = raw
    manifest = document(actual["inputs"], "exact committed V33 graph inputs")
    summary = document(actual["summary"], "exact committed V33 graph summary")
    snapshot = summary.get("snapshot")
    need(type(snapshot) is dict and snapshot == old_snapshot,
         "bind the historical graph to the authentic complete V33 snapshot")
    old.validate(snapshot)
    need(
        summary.get("schema") == old.SCHEMA + "-summary"
        and summary.get("version") == 33 and summary.get("status") == "PASS"
        and summary.get("repository_evidence_owner_count") == 155
        and summary.get("authenticated_digest_addressed_history_paths") == 160
        and summary.get("suite_count") == 13
        and summary.get("full_case_denominator") == 31237
        and summary.get("private_waiver_count") == 13
        and summary.get("qualified_candidate_count") == 0
        and summary.get("rust_original_campaign_semantic_mismatch_count") == 1036
        and summary.get("rust_original_campaign_verified_passing_case_count") == 8965
        and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
        and summary.get("c_original_campaign_verified_passing_case_count") == 7325
        and summary.get("zig_original_campaign_semantic_mismatch_count") == 2172
        and summary.get("zig_original_campaign_verified_passing_case_count") == 2847
        and summary.get("zig_v12_source_build_status") == "PASS"
        and summary.get("zig_v12_source_build_process_count") == 26
        and summary.get("zig_v12_source_build_phase_count") == 2
        and summary.get("zig_v12_source_build_source_apply_count") == 2
        and manifest.get("repository_evidence_owner_count") == 155
        and manifest.get("all_digest_addressed_history_path_count") == 160,
        "retain exact V33 compatibility, build, denominator and owner counts",
    )
    _, _, history = old.authenticate_v32()
    _, added = old.authenticate_zig_v12(
        BUILD_ARCHIVE[1], BUILD_RECEIPT[1], history,
    )
    need(
        len(history) == 158 and len(added) == 2
        and not (set(history) & set(added)),
        "reconstruct the complete 158 historical + two actual Zig-build references",
    )
    refs = {**history, **added}
    need(len(refs) == 160,
         "authenticate exactly 160 append-only V33 history references")
    return summary, manifest, refs


def restored_originals(receipt: dict) -> dict:
    actual = receipt.get("restored_original_targets")
    need(type(actual) is dict and set(actual) == {"engine", "bridge"},
         "require both exactly restored original Zig native owners")
    for role, expected in RESTORED.items():
        item = actual.get(role)
        need(
            type(item) is dict
            and all(item.get(key) == value for key, value in expected.items())
            and item.get("path") == str(ROOT / expected["relative"]),
            "bind recovery to the exact original " + role + " inode and hash",
        )
    need(
        (actual["engine"]["device"], actual["engine"]["inode"])
        != (actual["bridge"]["device"], actual["bridge"]["inode"]),
        "preserve two distinct genuinely restored original Zig native inodes",
    )
    return copy.deepcopy(actual)


def authenticate_zig_v3(
    archive_pin: str, receipt_pin: str, history: dict[str, str],
) -> tuple[dict, dict[str, str]]:
    need(
        checked(archive_pin, "actual corrected Zig V3 matching archive")
        == ARCHIVE[1]
        and checked(receipt_pin, "actual corrected Zig V3 matching receipt")
        == RECEIPT[1],
        "pin only the actually published corrected-Zig semantic failure",
    )
    receipt_raw, receipt_owner = read_owner(
        RECEIPT[0], RECEIPT[1], RECEIPT[2], private=True,
        device=RECEIPT[3], inode=RECEIPT[4],
    )
    need(type(receipt_raw) is bytes,
         "read only the bounded actual 4,111-byte Zig receipt")
    receipt = document(receipt_raw, "actual corrected Zig V3 publication receipt")
    _, archive_owner = read_owner(
        ARCHIVE[0], ARCHIVE[1], ARCHIVE[2], private=True,
        device=ARCHIVE[3], inode=ARCHIVE[4], retain=False,
    )
    claimed = receipt.get("archive")
    need(
        type(claimed) is dict
        and claimed.get("relative") == Path(ARCHIVE[0]).name
        and claimed.get("path") == str(ROOT / ARCHIVE[0])
        and claimed.get("sha256") == archive_owner["sha256"]
        and claimed.get("size_bytes") == archive_owner["bytes"]
        and claimed.get("device") == archive_owner["device"]
        and claimed.get("inode") == archive_owner["inode"]
        and claimed.get("mode") == 0o600
        and claimed.get("exclusive_creation") is True
        and claimed.get("same_inode_readback_verified") is True
        and claimed.get("streaming_readback_verified") is True
        and claimed.get("file_fsync_completed") is True
        and claimed.get("directory_fsync_completed") is True
        and type(claimed.get("write_calls")) is int
        and claimed["write_calls"] > 0
        and (archive_owner["device"], archive_owner["inode"])
        != (receipt_owner["device"], receipt_owner["inode"])
        and ARCHIVE[0] not in history and RECEIPT[0] not in history,
        "authenticate distinct durable owners without inflating matching evidence",
    )
    need(
        receipt.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v3-"
        "durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("publication_status") == "PASS"
        and receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("family") == "zig"
        and receipt.get("label") == "phase2-v12-zig-scanner-v2-original-p0"
        and receipt.get("campaign_source_sha256") == CAMPAIGN_SOURCE[1]
        and receipt.get("campaign_protocol_sha256") == CAMPAIGN_PROTOCOL[1]
        and receipt.get("campaign_contract_sha256") == CAMPAIGN_CONTRACT[1]
        and receipt.get("original_v3_producer_source_sha256") == PRODUCER_SOURCE
        and receipt.get("original_v3_producer_protocol_sha256") == PRODUCER_PROTOCOL
        and receipt.get("original_v3_producer_contract_sha256") == PRODUCER_CONTRACT
        and receipt.get("actual_v12_build_archive_sha256") == BUILD_ARCHIVE[1]
        and receipt.get("actual_v12_build_receipt_sha256") == BUILD_RECEIPT[1]
        and receipt.get("canonical_corrected_bridge_source_sha256") == BRIDGE_SOURCE
        and receipt.get("native_engine_sha256") == ENGINE_NATIVE
        and receipt.get("native_bridge_sha256") == BRIDGE_NATIVE,
        "distinguish durable publication PASS from actual Zig compatibility FAIL",
    )
    need(
        receipt.get("suite_count") == 13
        and receipt.get("case_execution_denominator") == 31237
        and receipt.get("named_private_waiver_count") == 13
        and receipt.get("completed_suite_count") == 13
        and receipt.get("actual_candidate_workers") == 13
        and receipt.get("verified_passing_case_count") == 3711
        and receipt.get("semantic_mismatch_count") == 1764
        and receipt.get("infrastructure_failure_count") == 0
        and receipt.get("candidate_qualified") is False
        and receipt.get("historical_evidence_owner_count_before_publication") == 155
        and receipt.get("historical_authenticated_reference_count_before_publication")
        == 160
        and receipt.get("new_repository_evidence_owner_count") == 2
        and receipt.get("resulting_repository_evidence_owner_count") == 157
        and receipt.get("resulting_authenticated_reference_count") == 162
        and receipt.get("actual_corrected_rust_semantic_mismatch_count") == 1036
        and receipt.get("actual_c_semantic_mismatch_count") == 1230
        and receipt.get("historical_zig_semantic_mismatch_count") == 2172,
        "preserve all 13 actual workers, 1,764 failures and 3,711 proven passes",
    )
    need(
        receipt.get("public_recovery_root") == PUBLIC_RECOVERY
        and receipt.get("recovery_journal_sha256") == RECOVERY
        and receipt.get("all_original_native_targets_restored") is True
        and receipt.get("restoration_verified_before_publication") is True
        and receipt.get("v7_normalized_activation_source_sha256")
        == ACTIVATION_SOURCE
        and receipt.get("group_atomic") is False
        and receipt.get("sigkill_automatically_recovered") is False
        and receipt.get("power_failure_automatically_recovered") is False,
        "require genuine prepublication recovery without overstating crash safety",
    )
    originals = restored_originals(receipt)
    need(
        checked(receipt.get("uncompressed_sha256"), "recorded Zig report digest")
        == "5f33a22258baee31c972a13bbcb1f4be30c486982284a3c1f3cd6085ca1cd3f0"
        and receipt.get("uncompressed_bytes") == 5367720
        and receipt.get("uncompressed_chunk_count") == 5012
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("benchmark_files_read") == 0
        and receipt.get("clock_samples") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("undefined_behavior") == "NOT MEASURED"
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("winner_selected") is False,
        "never inflate matching reports or invent speed, safety or hidden cases",
    )
    _, source = read_owner(*CAMPAIGN_SOURCE)
    _, protocol = read_owner(*CAMPAIGN_PROTOCOL)
    contract_raw, contract = read_owner(*CAMPAIGN_CONTRACT)
    need(type(contract_raw) is bytes, "retain the exact frozen Zig V3 contract")
    frozen = document(contract_raw, "frozen original corrected Zig V3 campaign")
    oracle = frozen.get("original_oracle")
    build = frozen.get("actual_corrected_v12_build")
    evidence = frozen.get("current_evidence")
    past = frozen.get("actual_previous_zig_matching")
    future = frozen.get("future_complete_campaign")
    recovery = frozen.get("normalized_recovery")
    extra = frozen.get("additive_callable_introspection")
    need(
        frozen.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v3-"
        "recoverable-source-freeze"
        and frozen.get("version") == 3
        and frozen.get("source")
        == {"path": CAMPAIGN_SOURCE[0], "sha256": CAMPAIGN_SOURCE[1]}
        and frozen.get("protocol")
        == {"path": CAMPAIGN_PROTOCOL[0], "sha256": CAMPAIGN_PROTOCOL[1]}
        and type(oracle) is dict
        and oracle.get("case_execution_denominator") == 31237
        and oracle.get("suite_count") == 13
        and oracle.get("named_private_waiver_count") == 13
        and oracle.get("family_count") == 6
        and oracle.get("candidate_wrapper_allowed") is False
        and oracle.get("external_regex_dependency_allowed") is False
        and oracle.get("cross_family_matching_allowed") is False,
        "bind the result to the authentic frozen 31,237-case Python oracle",
    )
    need(
        type(build) is dict and build.get("build_status") == "PASS"
        and build.get("actual_compiler_process_count") == 26
        and build.get("actual_corrected_source_apply_count") == 2
        and build.get("actual_independent_phase_count") == 2
        and build.get("both_phase_native_roles_byte_identical") is True
        and build.get("external_matching_engine_count") == 0
        and build.get("cross_family_engine_count") == 0
        and type(evidence) is dict
        and evidence.get("actual_evidence_owner_count_before_new_campaign") == 155
        and evidence.get("actual_authenticated_reference_count_before_new_campaign")
        == 160
        and type(past) is dict and past.get("candidate_status") == "FAIL"
        and past.get("semantic_mismatch_count") == 2172
        and past.get("verified_passing_case_count") == 2847
        and type(future) is dict
        and future.get("future_worker_count") == 13
        and future.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and type(recovery) is dict
        and recovery.get("public_recovery_root") == PUBLIC_RECOVERY
        and recovery.get("group_atomic") is False
        and type(extra) is dict and extra.get("additive_case_count") == 50
        and extra.get("reference_status") == "NOT RUN"
        and extra.get("included_in_original_denominator") is False,
        "authenticate first-party build provenance without claiming runtime audit",
    )
    added = {ARCHIVE[0]: ARCHIVE[1], RECEIPT[0]: RECEIPT[1]}
    proof = {
        "schema": SCHEMA + "-authenticated-complete-zig-v3-matching-failure",
        "status": "FAIL",
        "failure_class": "SEMANTIC MISMATCH",
        "family": "zig",
        "label": "phase2-v12-zig-scanner-v2-original-p0",
        "source": source,
        "protocol": protocol,
        "contract": contract,
        "archive": archive_owner,
        "receipt": receipt_owner,
        "publication_receipt": receipt,
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "suite_count": 13,
        "completed_suite_count": 13,
        "case_execution_denominator": 31237,
        "private_waiver_count": 13,
        "actual_candidate_workers": 13,
        "verified_passing_case_count": 3711,
        "semantic_mismatch_count": 1764,
        "historical_zig_semantic_mismatch_count": 2172,
        "historical_zig_verified_passing_case_count": 2847,
        "semantic_mismatch_reduction": 408,
        "additional_verified_passing_case_count": 864,
        "infrastructure_failure_count": 0,
        "candidate_qualified": False,
        "historical_evidence_owner_count_before_publication": 155,
        "historical_authenticated_reference_count_before_publication": 160,
        "new_repository_evidence_owner_count": 2,
        "resulting_repository_evidence_owner_count": 157,
        "resulting_authenticated_reference_count": 162,
        "actual_v12_build_archive_sha256": BUILD_ARCHIVE[1],
        "actual_v12_build_receipt_sha256": BUILD_RECEIPT[1],
        "actual_build_compiler_process_count": 26,
        "actual_independent_build_phase_count": 2,
        "actual_build_source_apply_count": 2,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "canonical_corrected_bridge_source_sha256": BRIDGE_SOURCE,
        "native_engine_sha256": ENGINE_NATIVE,
        "native_bridge_sha256": BRIDGE_NATIVE,
        "public_recovery_root": PUBLIC_RECOVERY,
        "recovery_journal_sha256": RECOVERY,
        "all_original_native_targets_restored": True,
        "restoration_verified_before_publication": True,
        "restored_original_targets": originals,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "compressed_matching_archive_streamed_bytes_read_by_graph": ARCHIVE[2],
        "matching_archive_materialized_in_memory_by_graph": False,
        "uncompressed_matching_archive_opened_by_graph": False,
        "uncompressed_matching_archive_bytes_read_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "uncompressed_archive_sha256": receipt["uncompressed_sha256"],
        "uncompressed_archive_bytes": receipt["uncompressed_bytes"],
        "individual_zig_suite_mismatches":
            "NOT PRESENT IN DURABLE RECEIPT",
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_native_activations_by_graph": 0,
        "original_native_targets_inspected_by_graph": False,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return proof, added


def validate(snapshot: object) -> None:
    need(
        type(snapshot) is dict
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("baseline_passed") == 31237
        and snapshot.get("frozen_independent_engine_family_count") == 6
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("preserved_v33_repository_evidence_owner_count") == 155
        and snapshot.get("preserved_v33_digest_addressed_history_path_count") == 160
        and snapshot.get("new_zig_v3_original_campaign_repository_evidence_owner_count")
        == 2
        and snapshot.get("all_actual_candidate_and_native_evidence_owner_count") == 157
        and snapshot.get("all_digest_addressed_history_path_count") == 162,
        "derive exactly 155 + 2 evidence owners and 160 + 2 references",
    )
    for name, mismatches, passes in (
        ("rust_v4_original_campaign", 1036, 8965),
        ("rust_v3_original_campaign", 1087, 7438),
        ("c_v4_original_campaign", 1230, 7325),
        ("zig_v2_original_campaign", 2172, 2847),
        ("zig_v3_original_campaign", 1764, 3711),
    ):
        actual = snapshot.get(name)
        need(
            type(actual) is dict and actual.get("status") == "FAIL"
            and actual.get("actual_candidate_workers") == 13
            and actual.get("completed_suite_count") == 13
            and actual.get("semantic_mismatch_count") == mismatches
            and actual.get("verified_passing_case_count") == passes
            and actual.get("infrastructure_failure_count") == 0
            and actual.get("candidate_qualified") is False,
            "preserve the exact complete actual matching outcome " + name,
        )
    proof = snapshot["zig_v3_original_campaign"]
    need(
        proof.get("schema")
        == SCHEMA + "-authenticated-complete-zig-v3-matching-failure"
        and proof.get("failure_class") == "SEMANTIC MISMATCH"
        and proof.get("family") == "zig"
        and proof.get("label") == "phase2-v12-zig-scanner-v2-original-p0"
        and proof.get("publication_status") == "PASS"
        and proof.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and proof.get("suite_count") == 13
        and proof.get("case_execution_denominator") == 31237
        and proof.get("private_waiver_count") == 13
        and proof.get("historical_zig_semantic_mismatch_count") == 2172
        and proof.get("historical_zig_verified_passing_case_count") == 2847
        and proof.get("semantic_mismatch_reduction") == 408
        and proof.get("additional_verified_passing_case_count") == 864
        and proof.get("historical_evidence_owner_count_before_publication") == 155
        and proof.get("historical_authenticated_reference_count_before_publication")
        == 160
        and proof.get("new_repository_evidence_owner_count") == 2
        and proof.get("resulting_repository_evidence_owner_count") == 157
        and proof.get("resulting_authenticated_reference_count") == 162,
        "report 408 fewer genuine failures without calling publication a test pass",
    )
    archive, receipt = proof.get("archive"), proof.get("receipt")
    need(
        type(archive) is dict and archive.get("path") == ARCHIVE[0]
        and archive.get("sha256") == ARCHIVE[1]
        and archive.get("bytes") == ARCHIVE[2]
        and archive.get("device") == ARCHIVE[3]
        and archive.get("inode") == ARCHIVE[4]
        and archive.get("mode") == "0600" and archive.get("nlink") == 1
        and archive.get("uid") == os.geteuid()
        and type(receipt) is dict and receipt.get("path") == RECEIPT[0]
        and receipt.get("sha256") == RECEIPT[1]
        and receipt.get("bytes") == RECEIPT[2]
        and receipt.get("device") == RECEIPT[3]
        and receipt.get("inode") == RECEIPT[4]
        and receipt.get("mode") == "0600" and receipt.get("nlink") == 1
        and receipt.get("uid") == os.geteuid()
        and (archive.get("device"), archive.get("inode"))
        != (receipt.get("device"), receipt.get("inode")),
        "require exactly two distinct genuine owner-only Zig matching records",
    )
    publication = proof.get("publication_receipt")
    need(
        type(publication) is dict
        and publication.get("status") == "PASS"
        and publication.get("publication_status") == "PASS"
        and publication.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and publication.get("candidate_status") == "FAIL"
        and publication.get("semantic_mismatch_count") == 1764
        and publication.get("verified_passing_case_count") == 3711
        and publication.get("actual_candidate_workers") == 13
        and publication.get("completed_suite_count") == 13
        and publication.get("infrastructure_failure_count") == 0
        and publication.get("candidate_qualified") is False,
        "never misread durable publication PASS as candidate compatibility",
    )
    need(
        proof.get("actual_v12_build_archive_sha256") == BUILD_ARCHIVE[1]
        and proof.get("actual_v12_build_receipt_sha256") == BUILD_RECEIPT[1]
        and proof.get("actual_build_compiler_process_count") == 26
        and proof.get("actual_independent_build_phase_count") == 2
        and proof.get("actual_build_source_apply_count") == 2
        and proof.get("native_source_build_independence") == "VERIFIED"
        and proof.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and proof.get("production_runtime_delegation_audit") == "NOT ESTABLISHED"
        and proof.get("canonical_corrected_bridge_source_sha256") == BRIDGE_SOURCE
        and proof.get("native_engine_sha256") == ENGINE_NATIVE
        and proof.get("native_bridge_sha256") == BRIDGE_NATIVE
        and proof.get("public_recovery_root") == PUBLIC_RECOVERY
        and proof.get("recovery_journal_sha256") == RECOVERY
        and proof.get("all_original_native_targets_restored") is True
        and proof.get("restoration_verified_before_publication") is True
        and proof.get("group_atomic") is False
        and proof.get("sigkill_automatically_recovered") is False
        and proof.get("power_failure_automatically_recovered") is False,
        "separate verified first-party source independence from unproven runtime",
    )
    restored_originals({"restored_original_targets":
                        proof.get("restored_original_targets")})
    need(
        proof.get("compressed_matching_archive_streamed_bytes_read_by_graph")
        == ARCHIVE[2]
        and proof.get("matching_archive_materialized_in_memory_by_graph") is False
        and proof.get("uncompressed_matching_archive_opened_by_graph") is False
        and proof.get("uncompressed_matching_archive_bytes_read_by_graph") == 0
        and proof.get("matching_archive_gzip_inflation_count") == 0
        and proof.get("individual_zig_suite_mismatches")
        == "NOT PRESENT IN DURABLE RECEIPT"
        and proof.get("actual_candidate_workers_started_by_graph") == 0
        and proof.get("actual_candidate_imports_by_graph") == 0
        and proof.get("actual_native_activations_by_graph") == 0
        and proof.get("original_native_targets_inspected_by_graph") is False
        and proof.get("hidden_cases_read") == 0
        and proof.get("benchmark_files_read") == 0
        and proof.get("clock_samples") == 0
        and proof.get("timing_trials_run") == 0
        and proof.get("performance") == "NOT MEASURED"
        and proof.get("memory") == "NOT MEASURED"
        and proof.get("confidence_intervals") == "NOT MEASURED"
        and proof.get("undefined_behavior") == "NOT MEASURED"
        and proof.get("holdout") == "NOT OPENED"
        and proof.get("winner_selected") is False,
        "never inflate matching evidence or run candidates, clocks, or holdout",
    )
    build = snapshot.get("zig_v12_corrected_scanner_source_build")
    need(
        type(build) is dict and build.get("status") == "PASS"
        and build.get("build_status") == "PASS"
        and build.get("actual_compiler_process_count") == 26
        and build.get("independent_phase_count") == 2
        and build.get("actual_source_apply_count") == 2
        and build.get("candidate_correctness") == "NOT MEASURED",
        "preserve independently authenticated from-scratch Zig build provenance",
    )
    need(
        snapshot.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and snapshot.get("production_runtime_delegation_audit")
        == "NOT ESTABLISHED"
        and snapshot.get("native_source_build_independence") == "VERIFIED"
        and snapshot.get("additional_signature_frozen_case_count") == 50
        and snapshot.get("additional_signature_reference_status") == "NOT RUN"
        and snapshot.get("additional_signature_reference_cases_executed") == 0
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("confidence_intervals") == "NOT MEASURED"
        and snapshot.get("undefined_behavior") == "NOT MEASURED"
        and snapshot.get("hidden_cases_read") == 0
        and snapshot.get("performance_files_read") == 0
        and snapshot.get("clock_samples") == 0
        and snapshot.get("timing_trials_run") == 0
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("winner_selected") is False,
        "leave runtime audit, all additional checks, performance and holdout honest",
    )


def xml(value: object) -> str:
    return (
        str(value).replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
    )


def make_svg(snapshot: dict, source: str, inputs: str) -> bytes:
    validate(snapshot)
    checked(source, "actual V34 renderer")
    checked(inputs, "actual V34 graph inputs")
    rows = (
        ("Python re — original reference", "COMPATIBLE REFERENCE", 0,
         "All 31,237 original reference checks pass.", "pass"),
        ("Rust — current from-scratch candidate", "NOT COMPATIBLE", 1036,
         "13 actual workers; 1,036 differences; 8,965 confirmed passing checks.",
         "fail"),
        ("C — current from-scratch candidate", "NOT COMPATIBLE", 1230,
         "13 actual workers; 1,230 differences; 7,325 confirmed passing checks.",
         "fail"),
        ("Zig — newly corrected and fully tested", "NOT COMPATIBLE", 1764,
         "13 actual workers; 1,764 differences; 3,711 confirmed passing checks.",
         "fail"),
        ("Zig — earlier fully tested version", "HISTORICAL; NOT COMPATIBLE",
         2172,
         "Historical only: 2,172 differences; 2,847 confirmed passing checks.",
         "history"),
    )
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1740" '
        'viewBox="0 0 1440 1740" role="img" '
        'aria-labelledby="v34-title v34-description">',
        '<title id="v34-title">Building a faster Python re: corrected Zig '
        'has 408 fewer differences but is not yet a compatible replacement</title>',
        '<desc id="v34-description">Against the frozen 31,237-case Python '
        'reference, corrected Zig has 1,764 observed compatibility differences, '
        '3,711 confirmed passes, and 13 real test workers. The earlier Zig had '
        '2,172 differences: an actual improvement of 408. Rust has 1,036 '
        'differences and C has 1,230. No replacement is compatible. Six '
        'first-party engine families have independently owned source. Runtime '
        'no-delegation is NOT ESTABLISHED. Speed, memory, confidence intervals '
        'and undefined behavior are NOT MEASURED. The 4,194,304-case expanded '
        'holdout remains unopened and ungenerated. Fifty extra Python '
        'signature checks have not run and are not in the denominator. '
        'Exactly 157 evidence owners and 162 history references are '
        'authenticated without inflating any matching report.</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,'
        '"Segoe UI",sans-serif}.title{font-size:27px;font-weight:760;fill:'
        '#16324f}.heading{font-size:19px;font-weight:750;fill:#16324f}'
        '.body{font-size:14px;fill:#42556c}.name{font-size:15px;font-weight:'
        '710;fill:#16324f}.pass{font-size:12px;font-weight:750;fill:#00794c}'
        '.fail{font-size:12px;font-weight:750;fill:#a75c13}.history{font-size:'
        '12px;font-weight:740;fill:#596b81}.pending{font-size:12px;font-weight:'
        '740;fill:#53667b}.big{font-size:21px;font-weight:760;fill:#16324f}'
        '.small{font-size:11px;fill:#42556c}.foot{font-size:10px;fill:'
        '#53667b}</style>',
        '<rect width="1440" height="1740" rx="22" fill="#f4f7fb"/>',
        '<text x="44" y="54" class="title">Can we build a faster '
        'replacement for Python re?</text>',
        '<text x="46" y="82" class="body">Corrected Zig improved by '
        '408 differences, but no candidate yet matches Python re. Speed has '
        'NOT BEEN MEASURED.</text>',
    ]
    cards = (
        ("31,237", "original reference checks"),
        ("0", "compatible replacements"),
        ("1,036", "current Rust differences"),
        ("1,230", "current C differences"),
        ("1,764", "new tested Zig differences"),
        ("408 fewer", "Zig vs. previous version"),
        ("157 / 162", "evidence / references"),
    )
    for index, (number, label) in enumerate(cards):
        left = 44 + index * 195
        lines.extend((
            f'<rect x="{left}" y="100" width="184" height="82" rx="11" '
            'fill="#fff" stroke="#dae4ee"/>',
            f'<text x="{left + 9}" y="133" class="big">{xml(number)}</text>',
            f'<text x="{left + 9}" y="159" class="small">{xml(label)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="201" width="1352" height="476" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="235" class="heading">1. Overall: can any '
        'candidate replace Python re?</text>',
        '<text x="66" y="259" class="body">Compatibility differences '
        'against the same frozen original Python tests. Lower is better; '
        'only zero qualifies.</text>',
        '<text x="65" y="284" class="small">Compatibility only. '
        'These bars are not speed, benchmark rankings, or percentages.</text>',
    ))
    for index, (name, outcome, differences, detail, kind) in enumerate(rows):
        top = 302 + index * 70
        width = round(620 * differences / 2172) if differences else 0
        color = "#0b8d61" if not differences else (
            "#b77a36" if kind != "history" else "#8390a0"
        )
        lines.extend((
            f'<text x="67" y="{top + 17}" class="name">{xml(name)}</text>',
            f'<text x="1370" y="{top + 17}" class="{kind}" '
            f'text-anchor="end">{xml(outcome)}</text>',
            f'<rect x="68" y="{top + 28}" width="620" height="11" '
            'rx="5" fill="#edf1f5"/>',
            f'<rect x="68" y="{top + 28}" width="{width}" height="11" '
            f'rx="5" fill="{color}"/>',
            f'<text x="704" y="{top + 39}" class="small">'
            f'{differences:,} differences</text>',
            f'<text x="68" y="{top + 58}" class="small">'
            f'{xml(detail)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="695" width="1352" height="260" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="730" class="heading">2. What the new Zig '
        'experiment actually established</text>',
    ))
    observations = (
        "The corrected engine was built from the project’s own source in two independent phases.",
        "All 26 actual build and inspection processes succeeded; both native roles reproduced.",
        "Thirteen real workers completed all 13 original Python test groups.",
        "Zig differences fell from 2,172 to 1,764: 408 fewer, but still not compatible.",
        "The published receipt records 3,711 verified passes and no infrastructure failures.",
        "The original two Zig native files were restored before evidence publication.",
        "Source and build independence are verified; full runtime no-delegation is NOT ESTABLISHED.",
    )
    for index, line in enumerate(observations):
        lines.append(
            f'<text x="67" y="{759 + 25 * index}" class="body">'
            f'{xml(line)}</text>'
        )
    lines.extend((
        '<rect x="44" y="972" width="1352" height="305" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1007" class="heading">3. What remains '
        'unproven or unmeasured</text>',
    ))
    remaining = (
        ("Compatible replacement", "NONE: all three tested current candidates still have differences."),
        ("Faster than Python re", "NOT MEASURED: correctness must pass before performance tests."),
        ("Memory and statistical confidence", "NOT MEASURED: no candidate has qualified for benchmarking."),
        ("Runtime no-delegation", "NOT ESTABLISHED: independent source is not a complete runtime audit."),
        ("50 extra Python signature checks", "REFERENCE NOT RUN: separate; not added to the 31,237 tests."),
        ("4,194,304-case final holdout", "NOT OPENED and NOT GENERATED: no hidden cases have run."),
        ("Overall winner", "NONE: speed, safety, and full compatibility remain unproven."),
    )
    for index, (name, detail) in enumerate(remaining):
        top = 1038 + 34 * index
        lines.extend((
            f'<text x="68" y="{top}" class="name">{xml(name)}</text>',
            f'<text x="382" y="{top}" class="body">{xml(detail)}</text>',
        ))
    lines.extend((
        '<rect x="44" y="1294" width="1352" height="308" rx="15" '
        'fill="#fff" stroke="#dae4ee"/>',
        '<text x="64" y="1329" class="heading">4. How to interpret '
        'the recorded evidence</text>',
    ))
    audit_notes = (
        "The reference stays at exactly 31,237 checks, 13 original suites and 13 named private waivers.",
        "The new matching receipt is a durable publication PASS, but the Zig matching result is FAIL.",
        "155 existing evidence owners + one failure archive + one distinct receipt = 157 owners.",
        "160 previous authenticated history references + two genuine new owners = 162 references.",
        "The compressed matching evidence was streaming-hashed, not inflated or loaded into memory.",
        "No graph process ran a candidate, compiler, performance clock, or additional Python reference.",
        "No hidden holdout case was generated, read, or benchmarked; no winner was selected.",
        "Runtime delegation, confidence intervals, memory and undefined behavior remain unestablished.",
    )
    for index, note in enumerate(audit_notes):
        lines.append(
            f'<text x="67" y="{1360 + index * 26}" class="body">'
            f'{xml(note)}</text>'
        )
    lines.extend((
        f'<text x="47" y="1640" class="foot">Inputs SHA-256: '
        f'{xml(inputs)}</text>',
        f'<text x="47" y="1661" class="foot">Renderer SHA-256: '
        f'{xml(source)}</text>',
        f'<text x="47" y="1682" class="foot">Actual Zig matching failure '
        f'archive SHA-256: {xml(ARCHIVE[1])}</text>',
        f'<text x="47" y="1703" class="foot">Actual distinct matching '
        f'receipt SHA-256: {xml(RECEIPT[1])}</text>',
        '</svg>',
    ))
    return ("\n".join(lines) + "\n").encode("utf-8")


def build(
    source_pin: str, archive_pin: str, receipt_pin: str,
) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    source_pin = checked(source_pin, "actual V34 renderer")
    own, _ = read_owner(SELF, source_pin, os.path.getsize(ROOT / SELF))
    need(type(own) is bytes, "authenticate the exact current V34 renderer")
    previous, previous_inputs, refs = authenticate_v33()
    proof, added = authenticate_zig_v3(archive_pin, receipt_pin, refs)
    need(
        len(refs) == 160 and len(added) == 2
        and not (set(refs) & set(added)),
        "append exactly two actual Zig matching owners to verified V33 history",
    )
    all_refs = {**refs, **added}
    count = previous["repository_evidence_owner_count"] + len(added)
    need(count == 157 and len(all_refs) == 162,
         "derive exactly 157 genuine owners and 162 distinct history references")
    snapshot = copy.deepcopy(previous["snapshot"])
    snapshot.update({
        "preserved_v33_repository_evidence_owner_count": 155,
        "preserved_v33_digest_addressed_history_path_count": 160,
        "new_zig_v3_original_campaign_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": count,
        "all_digest_addressed_history_path_count": len(all_refs),
        "zig_v3_original_campaign": copy.deepcopy(proof),
        "zig_v3_original_campaign_status": "FAIL",
        "zig_v3_original_campaign_actual_candidate_workers": 13,
        "zig_v3_original_campaign_semantic_mismatch_count": 1764,
        "zig_v3_original_campaign_verified_passing_case_count": 3711,
        "zig_v3_original_campaign_infrastructure_failure_count": 0,
        "zig_v3_original_campaign_semantic_mismatch_reduction": 408,
        "zig_v3_original_campaign_candidate_qualified": False,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "native_source_build_independence": "VERIFIED",
        "undefined_behavior": "NOT MEASURED",
    })
    validate(snapshot)
    prior = {name: pin(*owner) for name, owner in V33.items()}
    manifest = copy.deepcopy(previous_inputs)
    manifest.update({
        "schema": SCHEMA + "-inputs",
        "version": 34,
        "python": "3.14.6",
        "renderer": pin(SELF, source_pin, len(own)),
        "previous_overview": prior,
        "actual_complete_zig_v3_campaign": copy.deepcopy(proof),
        "current_complete_zig_campaign": copy.deepcopy(proof),
        "historical_complete_zig_v2_campaign":
            copy.deepcopy(snapshot["zig_v2_original_campaign"]),
        "current_complete_rust_campaign":
            copy.deepcopy(snapshot["rust_v4_original_campaign"]),
        "current_complete_c_campaign":
            copy.deepcopy(snapshot["c_v4_original_campaign"]),
        "preserved_v33_repository_evidence_owner_count": 155,
        "preserved_v33_digest_addressed_history_path_count": 160,
        "new_zig_v3_original_campaign_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count": count,
        "all_digest_addressed_history_path_count": len(all_refs),
        "candidate_qualified_count": 0,
        "zig_original_campaign_status": "FAIL",
        "zig_original_campaign_candidate_worker_count": 13,
        "zig_original_campaign_infrastructure_failure_count": 0,
        "zig_original_campaign_semantic_mismatch_count": 1764,
        "zig_original_campaign_verified_passing_case_count": 3711,
        "zig_semantic_mismatch_reduction": 408,
        "historical_zig_semantic_mismatch_count": 2172,
        "historical_zig_verified_passing_case_count": 2847,
        "zig_recovery_journal_sha256": RECOVERY,
        "zig_original_native_targets_restored": True,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "native_source_build_independence": "VERIFIED",
        "compressed_zig_matching_archive_streamed_bytes_read_by_graph":
            ARCHIVE[2],
        "matching_archive_materialized_in_memory_by_graph": False,
        "uncompressed_new_zig_matching_archive_opened_by_graph": False,
        "uncompressed_new_zig_matching_archive_bytes_read_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    })
    manifest_raw = canonical(manifest)
    image = make_svg(snapshot, source_pin, digest(manifest_raw))
    families = copy.deepcopy(previous["families"])
    for family in families:
        if family.get("family") == "zig":
            family.update({
                "historical_v2_original_campaign":
                    copy.deepcopy(snapshot["zig_v2_original_campaign"]),
                "current_v3_original_campaign": copy.deepcopy(proof),
                "current_v3_original_campaign_status": "FAIL",
                "current_v3_original_campaign_candidate_worker_count": 13,
                "current_v3_original_campaign_semantic_mismatch_count": 1764,
                "current_v3_original_campaign_verified_passing_case_count": 3711,
                "current_v3_original_campaign_infrastructure_failure_count": 0,
                "current_v3_semantic_mismatch_reduction": 408,
                "runtime_no_delegation": "NOT ESTABLISHED",
                "qualified": False,
            })
    summary = copy.deepcopy(previous)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 34,
        "status": "PASS",
        "python": "3.14.6",
        "source": pin(SELF, source_pin, len(own)),
        "inputs": pin(OUTPUT + ".inputs.json", digest(manifest_raw),
                      len(manifest_raw)),
        "svg": pin(OUTPUT + ".svg", digest(image), len(image)),
        "previous_overview": prior,
        "snapshot": snapshot,
        "families": families,
        "preserved_v33_repository_evidence_owner_count": 155,
        "preserved_v33_authenticated_reference_path_count": 160,
        "new_zig_v3_original_campaign_repository_evidence_owner_count": 2,
        "repository_evidence_owner_count": count,
        "authenticated_digest_addressed_history_paths": len(all_refs),
        "qualified_candidate_count": 0,
        "actual_zig_v3_original_campaign": copy.deepcopy(proof),
        "actual_zig_original_campaign": copy.deepcopy(proof),
        "historical_zig_v2_original_campaign":
            copy.deepcopy(snapshot["zig_v2_original_campaign"]),
        "zig_original_campaign_status": "FAIL",
        "zig_original_campaign_candidate_worker_count": 13,
        "zig_original_campaign_completed_suite_count": 13,
        "zig_original_campaign_case_execution_denominator": 31237,
        "zig_original_campaign_private_waiver_count": 13,
        "zig_original_campaign_semantic_mismatch_count": 1764,
        "zig_original_campaign_verified_passing_case_count": 3711,
        "zig_original_campaign_infrastructure_failure_count": 0,
        "zig_original_campaign_candidate_qualified": False,
        "historical_zig_semantic_mismatch_count": 2172,
        "historical_zig_verified_passing_case_count": 2847,
        "zig_semantic_mismatch_reduction": 408,
        "zig_additional_verified_passing_cases": 864,
        "zig_recovery_journal_sha256": RECOVERY,
        "zig_original_native_targets_restored": True,
        "zig_original_native_targets_inspected_by_graph": False,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "compressed_new_zig_matching_archive_streamed_bytes_read_by_graph":
            ARCHIVE[2],
        "matching_archive_materialized_in_memory_by_graph": False,
        "uncompressed_new_zig_matching_archive_opened_by_graph": False,
        "uncompressed_new_zig_matching_archive_bytes_read_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "individual_zig_suite_mismatches":
            "NOT PRESENT IN DURABLE RECEIPT",
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", manifest_raw),
        (OUTPUT + ".json", canonical(summary)),
        (OUTPUT + ".svg", image),
    )


class Wall:
    """Physically forbid all real effects during source-only tests."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def __enter__(self) -> Wall:
        def forbid(name: str):
            def blocked(*_args: object, **_kwargs: object) -> object:
                self.blocked += 1
                raise GraphError("V34 source-only effect blocked: " + name)

            return blocked

        groups = (
            (builtins, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "unlink",
                  "remove", "rename", "replace", "mkdir", "makedirs",
                  "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "stat", "lstat", "mkdir", "unlink",
                    "rename", "replace", "resolve")),
            (subprocess, ("run", "Popen", "call", "check_call",
                          "check_output")),
            (socket, ("socket", "create_connection")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp")),
            (threading.Thread, ("start",)),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "sleep")),
        )
        for owner, names in groups:
            for name in names:
                if hasattr(owner, name):
                    self.saved.append((owner, name, getattr(owner, name)))
                    setattr(owner, name, forbid(name))
        return self

    def __exit__(self, *_errors: object) -> None:
        for owner, name, value in reversed(self.saved):
            setattr(owner, name, value)


def synthetic() -> dict:
    def campaign(mismatches: int, passes: int) -> dict:
        return {
            "status": "FAIL",
            "actual_candidate_workers": 13,
            "completed_suite_count": 13,
            "semantic_mismatch_count": mismatches,
            "verified_passing_case_count": passes,
            "infrastructure_failure_count": 0,
            "candidate_qualified": False,
        }

    archive = {
        "path": ARCHIVE[0], "sha256": ARCHIVE[1], "bytes": ARCHIVE[2],
        "device": ARCHIVE[3], "inode": ARCHIVE[4], "mode": "0600",
        "nlink": 1, "uid": 1000,
    }
    receipt = {
        "path": RECEIPT[0], "sha256": RECEIPT[1], "bytes": RECEIPT[2],
        "device": RECEIPT[3], "inode": RECEIPT[4], "mode": "0600",
        "nlink": 1, "uid": 1000,
    }
    originals = {
        role: {**item, "path": str(ROOT / item["relative"])}
        for role, item in RESTORED.items()
    }
    publication = {
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "FAIL", "semantic_mismatch_count": 1764,
        "verified_passing_case_count": 3711,
        "actual_candidate_workers": 13, "completed_suite_count": 13,
        "infrastructure_failure_count": 0, "candidate_qualified": False,
    }
    proof = {
        **campaign(1764, 3711),
        "schema": SCHEMA + "-authenticated-complete-zig-v3-matching-failure",
        "failure_class": "SEMANTIC MISMATCH",
        "family": "zig", "label": "phase2-v12-zig-scanner-v2-original-p0",
        "archive": archive, "receipt": receipt,
        "publication_receipt": publication,
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "suite_count": 13, "case_execution_denominator": 31237,
        "private_waiver_count": 13,
        "historical_zig_semantic_mismatch_count": 2172,
        "historical_zig_verified_passing_case_count": 2847,
        "semantic_mismatch_reduction": 408,
        "additional_verified_passing_case_count": 864,
        "historical_evidence_owner_count_before_publication": 155,
        "historical_authenticated_reference_count_before_publication": 160,
        "new_repository_evidence_owner_count": 2,
        "resulting_repository_evidence_owner_count": 157,
        "resulting_authenticated_reference_count": 162,
        "actual_v12_build_archive_sha256": BUILD_ARCHIVE[1],
        "actual_v12_build_receipt_sha256": BUILD_RECEIPT[1],
        "actual_build_compiler_process_count": 26,
        "actual_independent_build_phase_count": 2,
        "actual_build_source_apply_count": 2,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "canonical_corrected_bridge_source_sha256": BRIDGE_SOURCE,
        "native_engine_sha256": ENGINE_NATIVE,
        "native_bridge_sha256": BRIDGE_NATIVE,
        "public_recovery_root": PUBLIC_RECOVERY,
        "recovery_journal_sha256": RECOVERY,
        "all_original_native_targets_restored": True,
        "restoration_verified_before_publication": True,
        "restored_original_targets": originals,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "compressed_matching_archive_streamed_bytes_read_by_graph": ARCHIVE[2],
        "matching_archive_materialized_in_memory_by_graph": False,
        "uncompressed_matching_archive_opened_by_graph": False,
        "uncompressed_matching_archive_bytes_read_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "individual_zig_suite_mismatches":
            "NOT PRESENT IN DURABLE RECEIPT",
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_native_activations_by_graph": 0,
        "original_native_targets_inspected_by_graph": False,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    return {
        "full_case_denominator": 31237,
        "suite_count": 13,
        "baseline_passed": 31237,
        "frozen_independent_engine_family_count": 6,
        "qualified_candidate_count": 0,
        "preserved_v33_repository_evidence_owner_count": 155,
        "preserved_v33_digest_addressed_history_path_count": 160,
        "new_zig_v3_original_campaign_repository_evidence_owner_count": 2,
        "all_actual_candidate_and_native_evidence_owner_count": 157,
        "all_digest_addressed_history_path_count": 162,
        "rust_v4_original_campaign": campaign(1036, 8965),
        "rust_v3_original_campaign": campaign(1087, 7438),
        "c_v4_original_campaign": campaign(1230, 7325),
        "zig_v2_original_campaign": campaign(2172, 2847),
        "zig_v3_original_campaign": proof,
        "zig_v12_corrected_scanner_source_build": {
            "status": "PASS", "build_status": "PASS",
            "actual_compiler_process_count": 26,
            "independent_phase_count": 2,
            "actual_source_apply_count": 2,
            "candidate_correctness": "NOT MEASURED",
        },
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "native_source_build_independence": "VERIFIED",
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "NOT RUN",
        "additional_signature_reference_cases_executed": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "hidden_cases_read": 0, "performance_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }


def forged(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        if value == "FAIL":
            return "PASS"
        if value in ("NOT RUN", "NOT MEASURED", "NOT ESTABLISHED"):
            return "VERIFIED"
        return value + "-forged"
    if type(value) is dict:
        return {}
    if type(value) is list:
        return value[:-1]
    return "forged"


def self_test() -> dict:
    runtime()
    with Wall() as wall:
        base = synthetic()
        validate(base)
        rejected = 0

        def reject(snapshot: dict, label: str) -> None:
            nonlocal rejected
            try:
                validate(snapshot)
            except (GraphError, TypeError, ValueError, KeyError):
                rejected += 1
                return
            raise GraphError("accepted hostile synthetic V34 evidence: " + label)

        for key, value in base.items():
            if key in (
                "rust_v4_original_campaign", "rust_v3_original_campaign",
                "c_v4_original_campaign", "zig_v2_original_campaign",
                "zig_v3_original_campaign", "zig_v12_corrected_scanner_source_build",
            ):
                continue
            attack = copy.deepcopy(base)
            attack[key] = forged(value)
            reject(attack, "snapshot-" + key)
        for name in (
            "rust_v4_original_campaign", "rust_v3_original_campaign",
            "c_v4_original_campaign", "zig_v2_original_campaign",
            "zig_v3_original_campaign", "zig_v12_corrected_scanner_source_build",
        ):
            for key, value in base[name].items():
                attack = copy.deepcopy(base)
                attack[name][key] = forged(value)
                reject(attack, name + "-" + key)
        proof = base["zig_v3_original_campaign"]
        for name in ("archive", "receipt", "publication_receipt"):
            for key, value in proof[name].items():
                attack = copy.deepcopy(base)
                attack["zig_v3_original_campaign"][name][key] = forged(value)
                reject(attack, name + "-" + key)
        for role in ("engine", "bridge"):
            for key, value in proof["restored_original_targets"][role].items():
                attack = copy.deepcopy(base)
                attack["zig_v3_original_campaign"]["restored_original_targets"]\
                    [role][key] = forged(value)
                reject(attack, "recovery-" + role + "-" + key)
        collision = copy.deepcopy(base)
        collision["zig_v3_original_campaign"]["receipt"]["device"] = ARCHIVE[3]
        collision["zig_v3_original_campaign"]["receipt"]["inode"] = ARCHIVE[4]
        reject(collision, "matching-archive-and-receipt-inode-collision")
        picture = make_svg(base, "a" * 64, "b" * 64)
        for phrase in (
            b"31,237", b"157 / 162", b"1,036", b"8,965", b"1,230",
            b"7,325", b"1,764", b"3,711", b"2,172", b"2,847",
            b"408", b"NOT COMPATIBLE", b"NOT ESTABLISHED",
            b"REFERENCE NOT RUN", b"4,194,304", b"NOT GENERATED",
            b"streaming-hashed", b"not inflated", b"13 actual workers",
        ):
            need(phrase.lower() in picture.lower(),
                 "reject a misleading corrected Zig compatibility graph")
        effects = (
            lambda: builtins.open("forbidden-v34"),
            lambda: os.open("forbidden-v34", os.O_RDONLY),
            lambda: os.stat("forbidden-v34-native"),
            lambda: subprocess.run(("forbidden-v34",)),
            lambda: importlib.import_module("candidates.zig_candidate"),
            lambda: importlib.import_module("re"),
            lambda: socket.socket(),
            lambda: tempfile.mkdtemp(),
            lambda: time.perf_counter(),
            lambda: threading.Thread(target=lambda: None).start(),
        )
        for action in effects:
            try:
                action()
            except GraphError:
                continue
            raise GraphError("V34 source-only self-test leaked an actual effect")
        need(wall.blocked == len(effects),
             "block all 10 compiler, matching, runtime and holdout effects")
        need(rejected >= 125,
             "exercise owner, recovery, status, runtime, archive and case forgeries")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 34, "status": "PASS", "synthetic_only": True,
            "rejected_hostile_control_count": rejected,
            "blocked_effect_count": wall.blocked,
            "full_case_denominator": 31237, "suite_count": 13,
            "private_waiver_count": 13,
            "preserved_v33_repository_evidence_owner_count": 155,
            "preserved_v33_authenticated_reference_count": 160,
            "new_zig_v3_original_campaign_evidence_owner_count": 2,
            "repository_evidence_owner_count": 157,
            "authenticated_digest_addressed_history_paths": 162,
            "qualified_candidate_count": 0,
            "current_rust_candidate_status": "FAIL",
            "current_rust_semantic_mismatch_count": 1036,
            "current_c_candidate_status": "FAIL",
            "current_c_semantic_mismatch_count": 1230,
            "current_zig_candidate_status": "FAIL",
            "current_zig_semantic_mismatch_count": 1764,
            "current_zig_verified_passing_case_count": 3711,
            "current_zig_actual_candidate_workers": 13,
            "current_zig_infrastructure_failure_count": 0,
            "historical_zig_semantic_mismatch_count": 2172,
            "zig_semantic_mismatch_reduction": 408,
            "native_source_build_independence": "VERIFIED",
            "runtime_no_delegation": "NOT ESTABLISHED",
            "production_runtime_delegation_audit": "NOT ESTABLISHED",
            "additional_signature_frozen_case_count": 50,
            "additional_signature_reference_status": "NOT RUN",
            "additional_signature_reference_cases_executed": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_candidate_imports": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_activations": 0,
            "canonical_target_reads": 0, "canonical_target_stats": 0,
            "compressed_matching_archive_bytes_read": 0,
            "uncompressed_c_matching_archive_bytes_read": 0,
            "uncompressed_rust_matching_archive_bytes_read": 0,
            "uncompressed_zig_matching_archive_bytes_read": 0,
            "matching_archive_gzip_inflation_count": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "workspace_mutations": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
            "holdout": "NOT OPENED", "winner_selected": False,
        }


def publish(path: str, raw: bytes) -> None:
    allowed = {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
    need(path in allowed and type(raw) is bytes and 0 < len(raw) <= LIMIT,
         "write only the three exclusively reserved generated V34 graph owners")
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            written = os.write(handle, remaining)
            need(type(written) is int and written > 0,
                 "reject incomplete exclusive V34 output")
            remaining = remaining[written:]
        os.fsync(handle)
        actual = os.fstat(handle)
        need(
            actual.st_uid == os.geteuid() and actual.st_nlink == 1
            and actual.st_size == len(raw)
            and stat.S_IMODE(actual.st_mode) == 0o600,
            "reject linked, nonprivate or partial generated V34 output",
        )
    finally:
        os.close(handle)
    directory = os.open(
        str(ROOT / Path(path).parent),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    verified, _ = read_owner(path, digest(raw), len(raw), private=True)
    need(verified == raw,
         "re-read the exact separately and durably published V34 graph owner")


def result(
    source: str, archive: str, receipt: str,
    outputs: dict[str, bytes], written: bool, suffix: str,
) -> dict:
    return {
        "schema": SCHEMA + suffix,
        "version": 34,
        "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": digest(outputs[OUTPUT + ".svg"]),
        "actual_zig_v3_matching_archive_sha256": archive,
        "actual_zig_v3_matching_receipt_sha256": receipt,
        "full_case_denominator": 31237,
        "suite_count": 13,
        "private_waiver_count": 13,
        "preserved_v33_repository_evidence_owner_count": 155,
        "preserved_v33_authenticated_reference_count": 160,
        "new_zig_v3_original_campaign_evidence_owner_count": 2,
        "repository_evidence_owner_count": 157,
        "authenticated_digest_addressed_history_paths": 162,
        "qualified_candidate_count": 0,
        "rust_matching_status": "FAIL",
        "rust_semantic_mismatch_count": 1036,
        "rust_verified_passing_case_count": 8965,
        "c_matching_status": "FAIL",
        "c_semantic_mismatch_count": 1230,
        "c_verified_passing_case_count": 7325,
        "zig_matching_status": "FAIL",
        "zig_semantic_mismatch_count": 1764,
        "zig_verified_passing_case_count": 3711,
        "zig_actual_candidate_workers": 13,
        "zig_infrastructure_failure_count": 0,
        "historical_zig_semantic_mismatch_count": 2172,
        "historical_zig_verified_passing_case_count": 2847,
        "zig_semantic_mismatch_reduction": 408,
        "zig_original_native_targets_restored": True,
        "zig_recovery_journal_sha256": RECOVERY,
        "native_source_build_independence": "VERIFIED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "production_runtime_delegation_audit": "NOT ESTABLISHED",
        "additional_signature_frozen_case_count": 50,
        "additional_signature_reference_status": "NOT RUN",
        "additional_signature_reference_cases_executed": 0,
        "outputs_written": written,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_activations": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "compressed_new_zig_matching_archive_streamed_bytes_read_by_graph":
            ARCHIVE[2],
        "matching_archive_materialized_in_memory_by_graph": False,
        "uncompressed_c_matching_archive_opened": False,
        "uncompressed_c_matching_archive_bytes_read": 0,
        "uncompressed_rust_matching_archive_opened": False,
        "uncompressed_rust_matching_archive_bytes_read": 0,
        "uncompressed_zig_matching_archive_opened": False,
        "uncompressed_zig_matching_archive_bytes_read": 0,
        "matching_archive_gzip_inflation_count": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    for name in (
        "--source-sha256", "--campaign-archive-sha256",
        "--campaign-receipt-sha256", "--inputs-sha256",
        "--summary-sha256", "--svg-sha256",
    ):
        parser.add_argument(name)
    args = parser.parse_args(arguments)
    try:
        runtime()
        if args.self_test:
            need(
                all(getattr(args, key) is None for key in (
                    "source_sha256", "campaign_archive_sha256",
                    "campaign_receipt_sha256", "inputs_sha256",
                    "summary_sha256", "svg_sha256",
                )),
                "source-only self-tests accept no owner paths, pins or writes",
            )
            sys.stdout.buffer.write(canonical(self_test()))
            return 0
        source = checked(args.source_sha256, "actual V34 graph renderer")
        archive = checked(args.campaign_archive_sha256,
                          "actual corrected Zig V3 matching archive")
        receipt = checked(args.campaign_receipt_sha256,
                          "actual corrected Zig V3 matching receipt")
        _snapshot, pairs = build(source, archive, receipt)
        outputs = dict(pairs)
        if args.render:
            need(
                args.inputs_sha256 is None and args.summary_sha256 is None
                and args.svg_sha256 is None,
                "publish exactly three exclusively created V34 graph owners",
            )
            for path, raw in pairs:
                publish(path, raw)
            sys.stdout.buffer.write(
                canonical(result(source, archive, receipt, outputs,
                                 True, "-published"))
            )
            return 0
        frozen = {
            OUTPUT + ".inputs.json": checked(args.inputs_sha256,
                                               "frozen V34 graph inputs"),
            OUTPUT + ".json": checked(args.summary_sha256,
                                         "frozen V34 graph summary"),
            OUTPUT + ".svg": checked(args.svg_sha256,
                                        "frozen V34 graph image"),
        }
        for path, fingerprint in frozen.items():
            actual, _ = read_owner(path, fingerprint, len(outputs[path]),
                                   private=True)
            need(actual == outputs[path],
                 "independently reproduce every exact generated V34 owner")
        sys.stdout.buffer.write(
            canonical(result(source, archive, receipt, outputs,
                             False, "-read-only-frozen-context"))
        )
        return 0
    except (GraphError, OSError, ValueError, TypeError, EOFError,
            KeyError, AttributeError) as error:
        sys.stderr.write("current V34 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
