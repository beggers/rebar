#!/usr/bin/env python3
"""Preserve only the genuine, otherwise volatile Go publication failure.

Self-tests are synthetic. Frozen-context verification is read-only. Only an
explicit, completely pinned ``--preserve`` can publish the two evidence files.
This recorder never activates, builds, imports, or runs a matching candidate.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import copy
import ctypes
import gzip
import hashlib
import importlib
import importlib.util
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
from typing import Any, Callable, Mapping, Sequence
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/preserve_owned_go_campaign_publication_failure_v1.py"
PROTOCOL_RELATIVE = "oracle/phase2/OWNED-GO-CAMPAIGN-PUBLICATION-FAILURE-V1.md"
CONTRACT_RELATIVE = "oracle/phase2/owned-go-campaign-publication-failure-v1.json"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-owned-go-campaign-publication-failure-v1"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_ORIGINAL_REPORT_BYTES = 256 * 1024 * 1024
MAX_PRESERVATION_REPORT_BYTES = 1024 * 1024
EXPECTED_UID = 1000

CAMPAIGN_OWNERS = (
    ("source", "tools/run_owned_six_family_original_p0_campaign_v1.py",
     "50ac9f549739bb6b540f1762177f25b46c1fa345dce717ea7163e15d98ae7e88", 93832),
    ("protocol", "oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V1.md",
     "01d5908b9c1c3c356059a21cd0b418a7278559843d465e9062155b68f6497422", 4249),
    ("contract", "oracle/phase2/six-family-p0-campaign-v1.json",
     "c619e63dd18b8242bfc1af9e01030eff60e8d17128a83de216992b5cdc619801", 19273),
)
ACTIVATION_OWNERS = (
    ("source", "tools/activate_verified_native_candidate_v4.py",
     "f22106dab1e4a2f66178cdda66388c12dda83ad09254b045b447759615bf5cd7", 308110),
    ("protocol", "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V4.md",
     "3b4d463103380e30b7eb324598b4d39edb66e29f6ad483f7783cf51e4456621d", 7757),
    ("contract", "oracle/phase2/verified-native-activation-v4.json",
     "b1ba6cccfea423f562056e1813c8fe6c1e0ef24c2beabb099809dd1669982cf5", 26819),
)
GO_BUILD_OWNERS = (
    ("source", "tools/reproduce_owned_native_source_build_v6.py",
     "2af9da3cb37a55782f3bfb8bdbdfdb7a945532994a5c988f4645d888dbe57ebc", 196660),
    ("protocol", "oracle/phase2/NATIVE-SOURCE-BUILD-V6.md",
     "108dbd52144c78530221e36882a0070fe9805b1bef6a136caf4636148ae9131d", 10297),
    ("contract", "oracle/phase2/native-source-build-v6.json",
     "0121aaa5902b449e107396d6a1107ca8fe0fefebb0a0f09eb58d2d19c8888db4", 29292),
    ("archive", "oracle/phase2/evidence/native-source-build-v6-go-phase2-v6.json.gz",
     "05c24a5fff228d8eab8bec961d825b0e65504072e11e8c574ec580d9f3e6e245", 37619),
    ("receipt", "oracle/phase2/evidence/native-source-build-v6-go-phase2-v6-publication-receipt.json",
     "f3adcb20bb591946600e1e2b1db037fb3b4828c3d4a628a0347cfed40f262fca", 3262),
)
CPP_EVIDENCE_OWNERS = (
    ("archive", "oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-cpp-phase2-v1-failures.json.gz",
     "0462adbd6ee7bafb274578462117513669de9b849473a2e1ada441407bc814a2", 3244833),
    ("receipt", "oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-cpp-phase2-v1-failures-publication-receipt.json",
     "7b1156c07441acd579149ca9b3aedcb9308eb75a130ce7f7df98aa6a89d776f6", 3936),
)
PRIVATE_ROOT = "/tmp/rebar-phase2-verified-native-activation-v4-go-gdwheo66"
PRIVATE_ROOT_DEVICE = 2049
PRIVATE_ROOT_INODE = 11385000
PRIVATE_OWNERS = (
    ("activation_report", "activation-report.json",
     "58bab0b59bbec0bd3d536f04a752b98424d5f690dc70c532adb8fffcc678309c", 6959, 11387742),
    ("activation_receipt", "activation-receipt.json",
     "43c07c72d44148b4adf69337732bdc139dc5e4eb8893bb8a31fd27dea0a325c3", 2667, 11387753),
    ("recovery_journal", "recovery-journal.json",
     "8c71db399823923982d2fc81d8fc17e52dad44a6c4ed85d1be339300e3e95518", 3471, 11385003),
    ("engine_intention", "promotion-intent-engine.json",
     "e599d5ab3cc01cd39bd87251f837d08c9e4a25193a78bc7114dc63c351092c41", 1121, 11385035),
    ("bridge_intention", "promotion-intent-bridge.json",
     "0db59bf159edf46b87c7d179cdbd94c068094ffb86b14f08fdbebdb31633f4d9", 1177, 11387740),
)
GO_TARGETS = {
    "engine": {
        "relative": "candidates/_go_engine.so",
        "sha256": "38ab223b8ef88340a7be86f2195c417ee7d2dd9deead48cc6495a5b4e3c31b27",
        "size_bytes": 2712912, "device": 2064, "inode": 431825,
    },
    "bridge": {
        "relative": "candidates/_go_bridge.cpython-314-x86_64-linux-gnu.so",
        "sha256": "dd71ab6cb15a98e1a07c38965cdb178da0dbba2a26db937975e0d6435a2a5d0c",
        "size_bytes": 41904, "device": 2064, "inode": 431826,
    },
}
OUTCOME_STEM = "owned-six-family-original-p0-campaign-v1-go-phase2-v1"
MISSING_OUTCOME_NAMES = (
    OUTCOME_STEM + ".json.gz",
    OUTCOME_STEM + "-publication-receipt.json",
    OUTCOME_STEM + "-failures.json.gz",
    OUTCOME_STEM + "-failures-publication-receipt.json",
)
ARCHIVE_NAME = OUTCOME_STEM + "-publication-failure-evidence.json.gz"
RECEIPT_NAME = OUTCOME_STEM + "-publication-failure-evidence-publication-receipt.json"
UNKNOWN_FIELDS = (
    "actual_attempted_suite_count", "actual_completed_suite_count",
    "actual_suite_statuses", "actual_mismatch_count", "actual_crash_count",
    "actual_timeout_count", "actual_original_report_bytes",
    "actual_full_worker_stdout", "actual_restoration_route",
)


class PreservationError(Exception):
    """A real failure, owner, absence, or publication is unproven."""


class ForbiddenEffect(PreservationError):
    """A guarded source operation attempted an external effect."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise PreservationError(message)


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":"))
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, OverflowError, RecursionError, UnicodeError) as error:
        raise PreservationError("require one finite surrogate-safe canonical document") from error


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value),
            "require one exact lowercase SHA-256: " + label)
    return value


def unique_json(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "reject a duplicate failure-evidence document key")
        result[key] = value
    return result


def decode_document(raw: Any, label: str, *, canonical_required: bool = True,
                    maximum: int = MAX_PRESERVATION_REPORT_BYTES) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= maximum,
            "require one complete bounded document: " + label)
    try:
        value = json.loads(raw.decode("utf-8", "strict"),
                           object_pairs_hook=unique_json,
                           parse_constant=lambda item: (_ for _ in ()).throw(
                               ValueError("nonfinite JSON: " + item)))
    except (ValueError, UnicodeError, RecursionError) as error:
        raise PreservationError("reject malformed evidence: " + label) from error
    require(type(value) is dict
            and (not canonical_required or canonical(value) == raw),
            "reject changed, noncanonical, or truncated evidence: " + label)
    return value


def zero_effects() -> dict[str, Any]:
    return {
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "actual_native_promotions": 0,
        "actual_native_libraries_loaded": 0,
        "actual_interpreters_created": 0,
        "actual_threads_started": 0,
        "actual_subprocesses_started": 0,
        "actual_network_requests": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def owner_contract(rows: tuple[tuple[Any, ...], ...]) -> list[dict[str, Any]]:
    return [{"role": role, "relative": path, "sha256": digest,
             "size_bytes": size} for role, path, digest, size in rows]


def expected_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 1,
        "status": "FROZEN",
        "goal_sha256": GOAL_SHA256,
        "candidate_family": "go",
        "candidate_label": "phase2-v1",
        "frozen_original_campaign": owner_contract(CAMPAIGN_OWNERS),
        "frozen_activation": owner_contract(ACTIVATION_OWNERS),
        "frozen_go_source_build": owner_contract(GO_BUILD_OWNERS),
        "retained_cpp_evidence": owner_contract(CPP_EVIDENCE_OWNERS),
        "inherited_historical_evidence_owner_count": 65,
        "retained_cpp_evidence_owner_count": 2,
        "total_retained_repository_evidence_owner_count": 67,
        "historical_compiler_process_count": 169,
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "original_named_private_waiver_count": 13,
        "original_report_publication_max_bytes": MAX_ORIGINAL_REPORT_BYTES,
        "original_archive_publication_max_bytes": MAX_ORIGINAL_REPORT_BYTES,
        "private_activation_root": {
            "path": PRIVATE_ROOT, "device": PRIVATE_ROOT_DEVICE,
            "inode": PRIVATE_ROOT_INODE, "mode": 0o700, "uid": EXPECTED_UID,
        },
        "private_activation_owners": [
            {"role": role, "relative": name, "sha256": digest,
             "size_bytes": size, "device": PRIVATE_ROOT_DEVICE,
             "inode": inode, "mode": 0o600, "uid": EXPECTED_UID}
            for role, name, digest, size, inode in PRIVATE_OWNERS
        ],
        "original_go_targets": copy.deepcopy(GO_TARGETS),
        "required_absent_original_outcome_owners": [
            EVIDENCE_RELATIVE + "/" + name for name in MISSING_OUTCOME_NAMES
        ],
        "failure_evidence_archive": EVIDENCE_RELATIVE + "/" + ARCHIVE_NAME,
        "failure_evidence_receipt": EVIDENCE_RELATIVE + "/" + RECEIPT_NAME,
        "publication_policy": {
            "archive_mode": "0600", "receipt_mode": "0600",
            "distinct_owner_inodes": True, "exclusive_creation": True,
            "no_follow": True, "same_inode_readback_required": True,
            "archive_file_fsync_required": True,
            "archive_directory_fsync_required": True,
            "receipt_file_fsync_required": True,
            "receipt_directory_fsync_required": True,
            "gzip_mtime": 0, "gzip_compresslevel": 9,
            "maximum_failure_report_bytes": MAX_PRESERVATION_REPORT_BYTES,
            "embed_complete_original_five_owner_bytes": True,
        },
        "failure_result_policy": {
            "infrastructure_status": "FAIL",
            "candidate_status": "NOT VERIFIED",
            "candidate_qualified": False,
            "unknown_result_fields": list(UNKNOWN_FIELDS),
            "unknown_result_value": "NOT RECORDED",
            "prepared_journal_is_not_restoration_proof": True,
            "absent_targets_are_not_restoration_route_proof": True,
            "report_exact_bytes_must_not_be_guessed": True,
            "receipt_pass_means_evidence_publication_only": True,
        },
        "verification_effects": zero_effects(),
    }


class EffectBoundary:
    """Block external effects; synthetic mode also blocks all file reads."""

    def __init__(self, *, source_only: bool) -> None:
        self.source_only = source_only
        self.originals: list[tuple[Any, str, Any]] = []
        self.blocked: dict[str, int] = {
            "file_reads": 0, "file_writes": 0, "processes": 0,
            "network": 0, "clocks": 0, "threads": 0,
            "native_loads": 0, "temporary_files": 0,
        }
        self.initial_candidate_modules = frozenset(
            name for name in sys.modules
            if name == "candidates" or name.startswith("candidates."))

    def replace(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def blocked(*args: Any, **kwargs: Any) -> Any:
            self.blocked[category] += 1
            raise ForbiddenEffect("blocked " + category + ": " + name)

        self.originals.append((owner, name, original))
        setattr(owner, name, blocked)

    def __enter__(self) -> "EffectBoundary":
        if self.source_only:
            for owner, name in ((builtins, "open"), (os, "open"),
                                (os, "stat"), (os, "lstat"),
                                (os, "listdir"), (os, "scandir")):
                self.replace(owner, name, "file_reads")
        for owner, name in ((os, "write"), (os, "fsync"), (os, "mkdir"),
                            (os, "makedirs"), (os, "unlink"), (os, "remove"),
                            (os, "rename"), (os, "replace"), (os, "rmdir"),
                            (os, "fchmod"), (os, "chmod")):
            self.replace(owner, name, "file_writes")
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            self.replace(subprocess, name, "processes")
        self.replace(socket, "socket", "network")
        self.replace(ctypes, "CDLL", "native_loads")
        self.replace(tempfile, "mkdtemp", "temporary_files")
        self.replace(tempfile, "mkstemp", "temporary_files")
        self.replace(threading.Thread, "start", "threads")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns"):
            self.replace(time, name, "clocks")
        return self

    def __exit__(self, error_type: Any, error: Any, traceback: Any) -> bool:
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        current = frozenset(name for name in sys.modules
                            if name == "candidates" or name.startswith("candidates."))
        require(current == self.initial_candidate_modules,
                "a failure-only source operation imported a real candidate")
        return False


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and os.path.realpath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and os.geteuid() == EXPECTED_UID
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "use only isolated owner-only stable CPython 3.14.6 without a candidate")


def read_repo_owner(relative: str, digest: str, *, size: int | None = None,
                    maximum: int = MAX_SOURCE_BYTES,
                    owner_only: bool = False) -> tuple[bytes, dict[str, Any]]:
    require(type(relative) is str and bool(relative) and "\x00" not in relative,
            "require one exact relative first-party owner")
    path = Path(relative)
    require(not path.is_absolute() and str(path) == relative
            and all(part not in {"", ".", ".."} for part in path.parts),
            "reject an absolute, broad, parent, or ambiguous owner")
    checked_digest(digest, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_ORIGINAL_REPORT_BYTES
            and (size is None or type(size) is int and 0 < size <= maximum),
            "require one strictly bounded evidence size")
    target = ROOT / path
    require(os.path.realpath(str(target)) == str(target),
            "reject redirected or symlinked repository evidence")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(target), flags)
    try:
        first, visible = os.fstat(descriptor), os.stat(str(target), follow_symlinks=False)
        require(stat.S_ISREG(first.st_mode)
                and (first.st_dev, first.st_ino) == (visible.st_dev, visible.st_ino)
                and first.st_uid == EXPECTED_UID
                and 0 < first.st_size <= maximum
                and (size is None or first.st_size == size)
                and (not owner_only or stat.S_IMODE(first.st_mode) == 0o600),
                "reject an unowned, changed, oversized, or public evidence inode")
        chunks: list[bytes] = []
        remaining = first.st_size
        hasher = hashlib.sha256()
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(chunk) is bytes and bool(chunk),
                    "reject truncated original evidence")
            remaining -= len(chunk)
            hasher.update(chunk)
            chunks.append(chunk)
        require(os.read(descriptor, 1) == b"",
                "reject a hidden original-evidence suffix")
        last, named = os.fstat(descriptor), os.stat(str(target), follow_symlinks=False)
        require((first.st_dev, first.st_ino, first.st_size,
                 first.st_mtime_ns, first.st_ctime_ns)
                == (last.st_dev, last.st_ino, last.st_size,
                    last.st_mtime_ns, last.st_ctime_ns)
                and (last.st_dev, last.st_ino, last.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and hasher.hexdigest() == digest,
                "reject replaced, modified, or incorrectly hashed evidence")
        return b"".join(chunks), {
            "relative": relative, "sha256": digest, "size_bytes": last.st_size,
            "device": last.st_dev, "inode": last.st_ino,
            "mode": stat.S_IMODE(last.st_mode), "uid": last.st_uid,
        }
    finally:
        os.close(descriptor)


def frozen_module(relative: str, digest: str, size: int) -> Any:
    _, first = read_repo_owner(relative, digest, size=size)
    name = "_rebar_owned_go_publication_failure_" + digest[:24]
    module = sys.modules.get(name)
    if module is None:
        spec = importlib.util.spec_from_file_location(name, str(ROOT / relative))
        require(spec is not None and spec.loader is not None,
                "load only one source-pinned first-party support module")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            sys.modules.pop(name, None)
            raise
    _, last = read_repo_owner(relative, digest, size=size)
    require((first["device"], first["inode"])
            == (last["device"], last["inode"])
            and os.path.abspath(str(getattr(module, "__file__", "")))
            == str(ROOT / relative),
            "a source-pinned first-party support module changed during import")
    return module


def expected_build_provenance() -> dict[str, Any]:
    return {
        "schema": "rebar-phase2-owned-native-source-build-v6",
        "family": "go", "build_version": 6, "label": "phase2-v6",
        "build_root": "/tmp/rebar-phase2-native-build-v6-go-y0wu58pu",
        "source_sha256": GO_BUILD_OWNERS[0][2],
        "protocol_sha256": GO_BUILD_OWNERS[1][2],
        "contract_sha256": GO_BUILD_OWNERS[2][2],
        "archive_relative": GO_BUILD_OWNERS[3][1],
        "archive_sha256": GO_BUILD_OWNERS[3][2],
        "receipt_relative": GO_BUILD_OWNERS[4][1],
        "receipt_sha256": GO_BUILD_OWNERS[4][2],
        "independent_fresh_phase_count": 2,
        "actual_versioned_symbol_streams_verified": True,
        "generated_go_header_verified": True,
        "generated_go_header_promoted": False,
        "preserved_v2_history_process_count": 39,
    }


def read_private_owners() -> dict[str, dict[str, Any]]:
    directory_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                       | getattr(os, "O_DIRECTORY", 0)
                       | getattr(os, "O_NOFOLLOW", 0))
    root = os.open(PRIVATE_ROOT, directory_flags)
    try:
        first = os.fstat(root)
        visible = os.stat(PRIVATE_ROOT, follow_symlinks=False)
        require(stat.S_ISDIR(first.st_mode)
                and stat.S_IMODE(first.st_mode) == 0o700
                and first.st_uid == EXPECTED_UID
                and (first.st_dev, first.st_ino)
                == (PRIVATE_ROOT_DEVICE, PRIVATE_ROOT_INODE)
                and (first.st_dev, first.st_ino)
                == (visible.st_dev, visible.st_ino),
                "reject a substituted, nonprivate, or redirected Go recovery root")
        result: dict[str, dict[str, Any]] = {}
        for role, name, digest, size, expected_inode in PRIVATE_OWNERS:
            flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                     | getattr(os, "O_NOFOLLOW", 0))
            descriptor = os.open(name, flags, dir_fd=root)
            try:
                before = os.fstat(descriptor)
                named = os.stat(name, dir_fd=root, follow_symlinks=False)
                require(stat.S_ISREG(before.st_mode)
                        and stat.S_IMODE(before.st_mode) == 0o600
                        and before.st_uid == EXPECTED_UID
                        and (before.st_dev, before.st_ino, before.st_size)
                        == (PRIVATE_ROOT_DEVICE, expected_inode, size)
                        and (named.st_dev, named.st_ino, named.st_size)
                        == (before.st_dev, before.st_ino, before.st_size),
                        "reject a substituted private Go owner: " + role)
                chunks: list[bytes] = []
                remaining = size
                while remaining:
                    block = os.read(descriptor, min(remaining, 65536))
                    require(type(block) is bytes and bool(block),
                            "reject truncated original Go bytes: " + role)
                    remaining -= len(block)
                    chunks.append(block)
                require(os.read(descriptor, 1) == b"",
                        "reject appended original Go bytes: " + role)
                raw = b"".join(chunks)
                after = os.fstat(descriptor)
                current = os.stat(name, dir_fd=root, follow_symlinks=False)
                require(hashlib.sha256(raw).hexdigest() == digest
                        and (before.st_dev, before.st_ino, before.st_size,
                             before.st_mtime_ns, before.st_ctime_ns)
                        == (after.st_dev, after.st_ino, after.st_size,
                            after.st_mtime_ns, after.st_ctime_ns)
                        and (current.st_dev, current.st_ino, current.st_size)
                        == (after.st_dev, after.st_ino, after.st_size),
                        "reject modified private Go evidence: " + role)
                result[role] = {
                    "role": role, "relative": name,
                    "path": PRIVATE_ROOT + "/" + name,
                    "sha256": digest, "size_bytes": size,
                    "device": PRIVATE_ROOT_DEVICE, "inode": expected_inode,
                    "mode": 0o600, "uid": EXPECTED_UID,
                    "raw": raw,
                    "document": decode_document(raw, role),
                }
            finally:
                os.close(descriptor)
        require(len({(row["device"], row["inode"])
                     for row in result.values()}) == len(PRIVATE_OWNERS),
                "the five private Go evidence owners must be genuinely distinct")
        return result
    finally:
        os.close(root)


def role_spec(role: str) -> dict[str, Any]:
    require(role in GO_TARGETS, "reject a foreign Go native role")
    return GO_TARGETS[role]


def validate_activation_bundle(
    bundle: Mapping[str, Any], *, specs: Sequence[tuple[Any, ...]] = PRIVATE_OWNERS,
) -> dict[str, Any]:
    require(type(bundle) is dict and set(bundle) == {row[0] for row in specs},
            "require the complete five-owner authentic Go activation graph")
    identities: set[tuple[int, int]] = set()
    by_role = {row[0]: row for row in specs}
    for role, expected in by_role.items():
        name, digest, size, inode = expected[1:]
        owner = bundle[role]
        require(type(owner) is dict and owner.get("role") == role
                and owner.get("relative") == name
                and owner.get("path") == PRIVATE_ROOT + "/" + name
                and owner.get("sha256") == digest
                and owner.get("size_bytes") == size
                and owner.get("device") == PRIVATE_ROOT_DEVICE
                and owner.get("inode") == inode
                and owner.get("mode") == 0o600
                and owner.get("uid") == EXPECTED_UID
                and type(owner.get("raw")) is bytes
                and len(owner["raw"]) == size
                and hashlib.sha256(owner["raw"]).hexdigest() == digest
                and decode_document(owner["raw"], role) == owner.get("document"),
                "reject a changed, swapped, incomplete, or public Go owner: " + role)
        identity = (owner["device"], owner["inode"])
        require(identity not in identities,
                "reject repeated private Go evidence identities")
        identities.add(identity)
    report = bundle["activation_report"]["document"]
    receipt = bundle["activation_receipt"]["document"]
    journal = bundle["recovery_journal"]["document"]
    journal_digest = bundle["recovery_journal"]["sha256"]
    report_digest = bundle["activation_report"]["sha256"]
    require(report.get("schema")
            == "rebar-phase2-verified-native-candidate-activation-v4"
            and report.get("status") == "PASS"
            and receipt.get("schema")
            == "rebar-phase2-verified-native-candidate-activation-v4-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and journal.get("schema")
            == "rebar-phase2-verified-native-candidate-activation-v4-recovery-journal"
            and journal.get("status") == "PREPARED",
            "never relabel a prepared journal as completed restoration")
    for document in (report, receipt, journal):
        require(document.get("family") == "go"
                and document.get("activation_root") == PRIVATE_ROOT
                and document.get("activation_source_sha256") == ACTIVATION_OWNERS[0][2]
                and document.get("activation_protocol_sha256") == ACTIVATION_OWNERS[1][2]
                and document.get("activation_contract_sha256") == ACTIVATION_OWNERS[2][2]
                and document.get("source_build") == expected_build_provenance(),
                "reject a foreign activation, V4 pin, or genuine V6 provenance")
    require(report.get("promotion_mode") == "recoverable-canonical-promotion"
            and receipt.get("promotion_mode") == "recoverable-canonical-promotion"
            and journal.get("promotion_mode") == "recoverable-canonical-promotion"
            and report.get("group_atomic") is False
            and receipt.get("group_atomic") is False
            and report.get("generated_go_header_promoted") is False
            and report.get("recovery_journal_sha256") == journal_digest
            and receipt.get("recovery_journal_sha256") == journal_digest
            and receipt.get("activation_report_sha256") == report_digest,
            "reject a forged promotion, false group atomicity, or unlinked receipt")
    linked_report = receipt.get("activation_report")
    require(type(linked_report) is dict
            and linked_report.get("relative") == by_role["activation_report"][1]
            and linked_report.get("sha256") == report_digest
            and linked_report.get("size_bytes") == bundle["activation_report"]["size_bytes"]
            and linked_report.get("device") == PRIVATE_ROOT_DEVICE
            and linked_report.get("inode") == bundle["activation_report"]["inode"]
            and linked_report.get("mode") == 0o600
            and linked_report.get("exclusive_creation") is True
            and linked_report.get("file_fsync_completed") is True
            and linked_report.get("same_inode_readback_verified") is True
            and linked_report.get("directory_fsync_completed") is True,
            "the genuine Go receipt must authenticate its durable report owner")
    expected_backup = expected_backup_entries()
    require(report.get("backup_entries") == expected_backup
            and journal.get("backup_entries") == expected_backup
            and set(report.get("canonical_targets", {})) == {"engine", "bridge"}
            and journal.get("native_hashes") == {
                "engine": GO_TARGETS["engine"]["sha256"],
                "bridge": GO_TARGETS["bridge"]["sha256"],
                "generated_header":
                "481ebb65cc587749677ce28abeb4f3de111e2f87a18ac547ff0157fce85d2c23",
            }
            and journal.get("native_sizes") == {
                "engine": GO_TARGETS["engine"]["size_bytes"],
                "bridge": GO_TARGETS["bridge"]["size_bytes"],
                "generated_header": 3086,
            },
            "preserve both genuinely absent original owners and the build-only header")
    for role in ("engine", "bridge"):
        target = role_spec(role)
        promoted = report["canonical_targets"][role]
        intention_role = role + "_intention"
        intention_owner = bundle[intention_role]
        linked_intention = promoted.get("promotion_intent")
        require(type(promoted) is dict
                and promoted.get("relative") == target["relative"]
                and promoted.get("sha256") == target["sha256"]
                and promoted.get("size_bytes") == target["size_bytes"]
                and promoted.get("device") == target["device"]
                and promoted.get("inode") == target["inode"]
                and type(linked_intention) is dict
                and linked_intention.get("relative") == intention_owner["relative"]
                and linked_intention.get("sha256") == intention_owner["sha256"]
                and linked_intention.get("size_bytes") == intention_owner["size_bytes"]
                and linked_intention.get("device") == intention_owner["device"]
                and linked_intention.get("inode") == intention_owner["inode"]
                and linked_intention.get("mode") == 0o600
                and linked_intention.get("exclusive_creation") is True
                and linked_intention.get("file_fsync_completed") is True
                and linked_intention.get("same_inode_readback_verified") is True
                and linked_intention.get("directory_fsync_completed") is True,
                "reject an unlinked authentic promotion intention: " + role)
        intention = intention_owner["document"]
        intention_target = intention.get("target")
        require(intention.get("schema")
                == "rebar-phase2-verified-native-candidate-activation-v4-durable-promotion-intent"
                and intention.get("status") == "PREPARED"
                and intention.get("family") == "go"
                and intention.get("activation_root") == PRIVATE_ROOT
                and intention.get("role") == role
                and intention.get("recovery_journal_sha256") == journal_digest
                and type(intention_target) is dict
                and intention_target.get("relative") == target["relative"]
                and intention_target.get("sha256") == target["sha256"]
                and intention_target.get("size_bytes") == target["size_bytes"]
                and intention_target.get("device") == target["device"]
                and intention_target.get("inode") == target["inode"],
                "never pass a prepared intention as an actual restoration: " + role)
    return {
        "status": "PASS",
        "private_owner_count": len(specs),
        "private_owner_total_original_bytes": sum(row[3] for row in specs),
        "prepared_journal_status": "PREPARED",
        "prepared_intention_status": "PREPARED",
        "reportful_restoration_proven": False,
        "reportless_restoration_proven": False,
    }


def expected_backup_entries() -> dict[str, Any]:
    return {
        role: {
            "backup": None,
            "original_owner": None,
            "originally_present": False,
            "promoted_sha256": target["sha256"],
            "promoted_size_bytes": target["size_bytes"],
            "role": role,
            "target_path": str(ROOT / target["relative"]),
            "target_relative": target["relative"],
        }
        for role, target in GO_TARGETS.items()
    }


def inspect_missing_names(names: Sequence[str], *, relative: str,
                          label: str) -> list[dict[str, Any]]:
    require(type(names) is tuple and len(names) == len(set(names))
            and all(type(name) is str and bool(name)
                    and "/" not in name and "\\" not in name
                    and name not in {".", ".."} for name in names),
            "reject an ambiguous absence scope: " + label)
    directory_path = str(ROOT / relative)
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(directory_path, flags)
    try:
        first = os.fstat(descriptor)
        visible = os.stat(directory_path, follow_symlinks=False)
        require(stat.S_ISDIR(first.st_mode)
                and first.st_uid == EXPECTED_UID
                and (first.st_dev, first.st_ino)
                == (visible.st_dev, visible.st_ino),
                "reject a replaced or unowned absence directory: " + label)
        result = []
        for name in names:
            try:
                os.stat(name, dir_fd=descriptor, follow_symlinks=False)
            except FileNotFoundError:
                result.append({"relative": relative + "/" + name,
                               "present": False})
            else:
                raise PreservationError(
                    "never overwrite or misreport a real " + label + ": " + name)
        return result
    finally:
        os.close(descriptor)


def validate_absence(rows: Any, names: Sequence[str], *, relative: str,
                     label: str) -> list[dict[str, Any]]:
    require(type(rows) is list and len(rows) == len(names)
            and rows == [{"relative": relative + "/" + name, "present": False}
                         for name in names],
            "never invent, omit, reorder, or falsely claim an absence: " + label)
    return rows


def validate_candidate_unknowns(value: Mapping[str, Any]) -> None:
    require(type(value) is dict
            and value.get("infrastructure_status") == "FAIL"
            and value.get("candidate_status") == "NOT VERIFIED"
            and value.get("candidate_qualified") is False
            and value.get("actual_original_campaign_publication_status") == "FAIL"
            and value.get("actual_original_report_publication_max_bytes")
            == MAX_ORIGINAL_REPORT_BYTES
            and value.get("actual_original_archive_publication_max_bytes")
            == MAX_ORIGINAL_REPORT_BYTES
            and value.get("actual_original_report_cap_error")
            == "bound and preserve the entire canonical original campaign"
            and value.get("prepared_journal_is_restoration_proof") is False
            and value.get("absent_canonical_targets_prove_restoration_route") is False,
            "never relabel a publication failure as verified Go correctness")
    for key in UNKNOWN_FIELDS:
        require(value.get(key) == "NOT RECORDED",
                "never fabricate missing actual Go correctness evidence: " + key)


def candidate_unknowns() -> dict[str, Any]:
    return {
        "infrastructure_status": "FAIL",
        "candidate_status": "NOT VERIFIED",
        "candidate_qualified": False,
        "actual_original_campaign_publication_status": "FAIL",
        "actual_original_report_publication_max_bytes": MAX_ORIGINAL_REPORT_BYTES,
        "actual_original_archive_publication_max_bytes": MAX_ORIGINAL_REPORT_BYTES,
        "actual_original_report_cap_error":
        "bound and preserve the entire canonical original campaign",
        "prepared_journal_is_restoration_proof": False,
        "absent_canonical_targets_prove_restoration_route": False,
        **{key: "NOT RECORDED" for key in UNKNOWN_FIELDS},
    }


def validate_cpp_receipt(receipt: dict[str, Any], archive_owner: dict[str, Any]) -> None:
    archive = receipt.get("archive")
    require(receipt.get("schema")
            == "rebar-owned-six-family-original-p0-campaign-v1-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("candidate_family") == "cpp"
            and receipt.get("label") == "phase2-v1"
            and receipt.get("campaign_source_sha256") == CAMPAIGN_OWNERS[0][2]
            and receipt.get("campaign_protocol_sha256") == CAMPAIGN_OWNERS[1][2]
            and receipt.get("campaign_document_sha256") == CAMPAIGN_OWNERS[2][2]
            and receipt.get("suite_count") == 13
            and receipt.get("case_execution_denominator") == 31237
            and receipt.get("completed_suite_count") == 13
            and receipt.get("failure_preserved") is True
            and type(archive) is dict
            and archive.get("relative")
            == CPP_EVIDENCE_OWNERS[0][1].split("/")[-1]
            and archive.get("sha256") == archive_owner["sha256"]
            and archive.get("size_bytes") == archive_owner["size_bytes"]
            and archive.get("device") == archive_owner["device"]
            and archive.get("inode") == archive_owner["inode"]
            and archive.get("mode") == 0o600
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("same_inode_readback_verified") is True
            and receipt.get("archive_directory_fsync_completed") is True,
            "preserve the two actual C++ failure owners without inventing Go results")


def validate_go_build_receipt(receipt: dict[str, Any]) -> None:
    require(receipt.get("schema")
            == "rebar-phase2-owned-native-source-build-v6-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == "go"
            and receipt.get("label") == "phase2-v6"
            and receipt.get("source_sha256") == GO_BUILD_OWNERS[0][2]
            and receipt.get("protocol_sha256") == GO_BUILD_OWNERS[1][2]
            and receipt.get("contract_sha256") == GO_BUILD_OWNERS[2][2]
            and receipt.get("archive_relative") == GO_BUILD_OWNERS[3][1]
            and receipt.get("archive_sha256") == GO_BUILD_OWNERS[3][2]
            and receipt.get("archive_bytes") == GO_BUILD_OWNERS[3][3]
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("performance") == "NOT MEASURED",
            "a passing native build receipt does not establish regex compatibility")


def parse_arguments(arguments: Sequence[str] | None = None) -> dict[str, Any]:
    values = list(sys.argv[1:] if arguments is None else arguments)
    require(all(type(item) is str for item in values),
            "require exact typed failure-preservation arguments")
    if values == ["--self-test"]:
        return {"mode": "self-test"}
    require(bool(values)
            and values[0] in {"--verify-frozen-context", "--preserve"},
            "explicitly choose synthetic test, read-only verification, or preservation")
    mapping = {
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
    }
    require(len(values) == 7,
            "pin all three freeze owners; reject every extra, hidden, or abbreviated flag")
    result: dict[str, Any] = {"mode": values[0][2:]}
    for index in (1, 3, 5):
        flag, value = values[index], values[index + 1]
        require(flag in mapping and mapping[flag] not in result,
                "reject duplicate, unknown, or omitted failure-freeze flags")
        result[mapping[flag]] = checked_digest(value, flag)
    require(set(result) == {"mode", *mapping.values()},
            "pin the exact complete source-freeze document graph")
    return result


def collect_context(options: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], Any]:
    verify_runtime()
    with EffectBoundary(source_only=False) as boundary:
        _, self_source = read_repo_owner(
            SOURCE_RELATIVE, options["source_sha256"], maximum=MAX_SOURCE_BYTES)
        _, self_protocol = read_repo_owner(
            PROTOCOL_RELATIVE, options["protocol_sha256"], maximum=MAX_SOURCE_BYTES)
        contract_raw, self_contract = read_repo_owner(
            CONTRACT_RELATIVE, options["contract_sha256"], maximum=MAX_SOURCE_BYTES)
        actual_contract = decode_document(
            contract_raw, "frozen Go failure contract", canonical_required=False,
            maximum=MAX_SOURCE_BYTES)
        require(actual_contract == expected_contract(),
                "reject an omitted or altered complete Go publication-failure contract")
        raw_goal, _ = read_repo_owner("GOAL.md", GOAL_SHA256,
                                     maximum=MAX_SOURCE_BYTES)
        require(raw_goal.startswith(b"/goal "),
                "the original immutable user objective must remain unchanged")
        repository_owners: dict[str, list[dict[str, Any]]] = {}
        loaded: dict[str, dict[str, bytes]] = {}
        for label, owners in (("campaign", CAMPAIGN_OWNERS),
                              ("activation", ACTIVATION_OWNERS),
                              ("go_v6", GO_BUILD_OWNERS),
                              ("cpp", CPP_EVIDENCE_OWNERS)):
            repository_owners[label] = []
            loaded[label] = {}
            for role, relative, digest, size in owners:
                raw, owner = read_repo_owner(
                    relative, digest, size=size,
                    maximum=MAX_ORIGINAL_REPORT_BYTES
                    if size > MAX_SOURCE_BYTES else MAX_SOURCE_BYTES,
                    owner_only=relative.startswith(EVIDENCE_RELATIVE + "/"))
                repository_owners[label].append({"role": role, **owner})
                loaded[label][role] = raw
        campaign = frozen_module(
            CAMPAIGN_OWNERS[0][1], CAMPAIGN_OWNERS[0][2], CAMPAIGN_OWNERS[0][3])
        inherited = campaign.verify_frozen_context(argparse.Namespace(
            source_sha256=CAMPAIGN_OWNERS[0][2],
            protocol_sha256=CAMPAIGN_OWNERS[1][2],
            document_sha256=CAMPAIGN_OWNERS[2][2],
        ))
        require(type(inherited) is dict and inherited.get("status") == "PASS"
                and inherited.get("read_only") is True
                and inherited.get("suite_count") == 13
                and inherited.get("case_execution_denominator") == 31237
                and inherited.get("named_private_waiver_count") == 13
                and inherited.get("source_family_count") == 6
                and inherited.get("source_owner_count") == 25
                and inherited.get("total_distinct_historical_evidence_owner_count") == 65
                and inherited.get("all_historical_versions_actual_compiler_process_count") == 169
                and inherited.get("qualified_candidate_count", 0) == 0
                and inherited.get("actual_v4_activations") == "NOT RUN",
                "independently verify all 65 original immutable historical evidence owners")
        v1_machine = decode_document(
            loaded["campaign"]["contract"], "original campaign machine",
            maximum=MAX_SOURCE_BYTES)
        policy = v1_machine.get("publication_policy")
        require(type(policy) is dict
                and policy.get("maximum_report_bytes") == MAX_ORIGINAL_REPORT_BYTES
                and policy.get("maximum_archive_bytes") == MAX_ORIGINAL_REPORT_BYTES
                and policy.get("archive_mode") == "0600"
                and policy.get("receipt_mode") == "0600"
                and v1_machine.get("suite_count") == 13
                and v1_machine.get("case_execution_denominator") == 31237
                and campaign.MAX_REPORT_BYTES == MAX_ORIGINAL_REPORT_BYTES
                and campaign.MAX_ARCHIVE_BYTES == MAX_ORIGINAL_REPORT_BYTES,
                "prove the genuine immutable 256 MiB original report guard")
        cpp_archive = next(row for row in repository_owners["cpp"]
                           if row["role"] == "archive")
        cpp_receipt = decode_document(loaded["cpp"]["receipt"],
                                      "authentic retained C++ failure receipt")
        validate_cpp_receipt(cpp_receipt, cpp_archive)
        build_receipt = decode_document(loaded["go_v6"]["receipt"],
                                        "authentic Go V6 source-build receipt")
        validate_go_build_receipt(build_receipt)
        bundle = read_private_owners()
        checked_bundle = validate_activation_bundle(bundle)
        missing_outcomes = inspect_missing_names(
            MISSING_OUTCOME_NAMES, relative=EVIDENCE_RELATIVE,
            label="original Go outcome owner")
        validate_absence(missing_outcomes, MISSING_OUTCOME_NAMES,
                         relative=EVIDENCE_RELATIVE, label="original Go outcomes")
        target_names = tuple(target["relative"].split("/", 1)[1]
                             for target in GO_TARGETS.values())
        missing_targets = inspect_missing_names(
            target_names, relative="candidates", label="original Go canonical target")
        validate_absence(missing_targets, target_names,
                         relative="candidates", label="original Go canonical targets")
        activation = campaign.frozen_module(
            ACTIVATION_OWNERS[0][1], ACTIVATION_OWNERS[0][2], ACTIVATION_OWNERS[0][3])
        require(activation.MAX_BINARY_BYTES == MAX_ORIGINAL_REPORT_BYTES
                and callable(activation.write_fresh)
                and callable(activation.synchronize_directory),
                "require the exact source-pinned owner-only durable V4 writer")
    require(all(value == 0 for value in boundary.blocked.values()),
            "read-only context attempted a forbidden external effect")
    report = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS", "read_only": True,
        "source": self_source, "protocol": self_protocol,
        "contract": self_contract,
        "repository_support_owners": repository_owners,
        "inherited_historical_evidence_owner_count": 65,
        "retained_cpp_evidence_owner_count": 2,
        "total_retained_repository_evidence_owner_count": 67,
        "historical_compiler_process_count": 169,
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "original_report_publication_max_bytes": MAX_ORIGINAL_REPORT_BYTES,
        "private_activation_root": expected_contract()["private_activation_root"],
        "private_activation_owners": [
            {key: value for key, value in bundle[role].items()
             if key not in {"raw", "document"}}
            for role, *_ in PRIVATE_OWNERS
        ],
        "private_bundle_verification": checked_bundle,
        "absent_original_outcome_owners": missing_outcomes,
        "absent_original_canonical_targets": missing_targets,
        "failure_claim": candidate_unknowns(),
        **zero_effects(),
    }
    return report, bundle, activation


def embedded_owners(bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    result = []
    for role, *_ in PRIVATE_OWNERS:
        owner = bundle[role]
        result.append({
            key: value for key, value in owner.items()
            if key not in {"raw", "document"}
        } | {"raw_base64": base64.b64encode(owner["raw"]).decode("ascii")})
    return result


def restore_embedded_owners(rows: Any) -> dict[str, dict[str, Any]]:
    require(type(rows) is list and len(rows) == len(PRIVATE_OWNERS),
            "embed all five complete original owner bytes exactly once")
    bundle: dict[str, dict[str, Any]] = {}
    for row, spec in zip(rows, PRIVATE_OWNERS, strict=True):
        role, name, digest, size, inode = spec
        require(type(row) is dict and row.get("role") == role
                and row.get("relative") == name
                and row.get("path") == PRIVATE_ROOT + "/" + name
                and row.get("sha256") == digest
                and row.get("size_bytes") == size
                and row.get("device") == PRIVATE_ROOT_DEVICE
                and row.get("inode") == inode
                and row.get("mode") == 0o600
                and row.get("uid") == EXPECTED_UID
                and type(row.get("raw_base64")) is str,
                "reject missing, reordered, or spoofed embedded Go owner: " + role)
        try:
            raw = base64.b64decode(row["raw_base64"], validate=True)
        except (ValueError, base64.binascii.Error) as error:
            raise PreservationError("reject malformed original Go bytes: " + role) from error
        require(len(raw) == size and hashlib.sha256(raw).hexdigest() == digest
                and base64.b64encode(raw).decode("ascii") == row["raw_base64"],
                "reject truncated, extra, or forged original Go bytes: " + role)
        bundle[role] = {key: value for key, value in row.items()
                        if key != "raw_base64"}
        bundle[role]["raw"] = raw
        bundle[role]["document"] = decode_document(raw, role)
    validate_activation_bundle(bundle)
    return bundle


def build_failure_report(options: Mapping[str, Any], context: Mapping[str, Any],
                         bundle: Mapping[str, Any]) -> dict[str, Any]:
    report = {
        "schema": SCHEMA + "-complete-original-evidence",
        "status": "FAIL",
        "failure_class": "original-canonical-report-publication-size-limit",
        "candidate_family": "go",
        "candidate_label": "phase2-v1",
        "preservation_source_sha256": options["source_sha256"],
        "preservation_protocol_sha256": options["protocol_sha256"],
        "preservation_contract_sha256": options["contract_sha256"],
        "original_campaign_source_sha256": CAMPAIGN_OWNERS[0][2],
        "original_campaign_protocol_sha256": CAMPAIGN_OWNERS[1][2],
        "original_campaign_contract_sha256": CAMPAIGN_OWNERS[2][2],
        "activation_source_sha256": ACTIVATION_OWNERS[0][2],
        "activation_protocol_sha256": ACTIVATION_OWNERS[1][2],
        "activation_contract_sha256": ACTIVATION_OWNERS[2][2],
        "go_source_build_sha256": GO_BUILD_OWNERS[0][2],
        "go_source_build_archive_sha256": GO_BUILD_OWNERS[3][2],
        "go_source_build_receipt_sha256": GO_BUILD_OWNERS[4][2],
        "retained_repository_evidence_owner_count": 67,
        "retained_cpp_candidate_evidence_owner_count": 2,
        "original_frozen_suite_count": 13,
        "original_frozen_case_execution_denominator": 31237,
        "private_activation_root": expected_contract()["private_activation_root"],
        "private_owner_count": len(PRIVATE_OWNERS),
        "private_owner_total_original_bytes": sum(row[3] for row in PRIVATE_OWNERS),
        "original_activation_owners": embedded_owners(bundle),
        "absent_original_outcome_owners": context["absent_original_outcome_owners"],
        "absent_original_canonical_targets": context["absent_original_canonical_targets"],
        "failure_claim": candidate_unknowns(),
        "candidate_qualified": False,
        "candidate_status": "NOT VERIFIED",
        "original_campaign_publication_status": "FAIL",
        "preservation_receipt_pass_is_candidate_pass": False,
        **zero_effects(),
    }
    validate_failure_report(report, options)
    return report


def validate_failure_report(report: Any, options: Mapping[str, Any]) -> None:
    require(type(report) is dict
            and report.get("schema") == SCHEMA + "-complete-original-evidence"
            and report.get("status") == "FAIL"
            and report.get("failure_class")
            == "original-canonical-report-publication-size-limit"
            and report.get("candidate_family") == "go"
            and report.get("candidate_label") == "phase2-v1"
            and report.get("preservation_source_sha256") == options["source_sha256"]
            and report.get("preservation_protocol_sha256") == options["protocol_sha256"]
            and report.get("preservation_contract_sha256") == options["contract_sha256"]
            and report.get("original_campaign_source_sha256") == CAMPAIGN_OWNERS[0][2]
            and report.get("original_campaign_protocol_sha256") == CAMPAIGN_OWNERS[1][2]
            and report.get("original_campaign_contract_sha256") == CAMPAIGN_OWNERS[2][2]
            and report.get("activation_source_sha256") == ACTIVATION_OWNERS[0][2]
            and report.get("activation_protocol_sha256") == ACTIVATION_OWNERS[1][2]
            and report.get("activation_contract_sha256") == ACTIVATION_OWNERS[2][2]
            and report.get("go_source_build_sha256") == GO_BUILD_OWNERS[0][2]
            and report.get("go_source_build_archive_sha256") == GO_BUILD_OWNERS[3][2]
            and report.get("go_source_build_receipt_sha256") == GO_BUILD_OWNERS[4][2]
            and report.get("retained_repository_evidence_owner_count") == 67
            and report.get("retained_cpp_candidate_evidence_owner_count") == 2
            and report.get("original_frozen_suite_count") == 13
            and report.get("original_frozen_case_execution_denominator") == 31237
            and report.get("private_activation_root")
            == expected_contract()["private_activation_root"]
            and report.get("private_owner_count") == len(PRIVATE_OWNERS)
            and report.get("private_owner_total_original_bytes")
            == sum(row[3] for row in PRIVATE_OWNERS)
            and report.get("candidate_qualified") is False
            and report.get("candidate_status") == "NOT VERIFIED"
            and report.get("original_campaign_publication_status") == "FAIL"
            and report.get("preservation_receipt_pass_is_candidate_pass") is False,
            "reject a fabricated failure publication or Go correctness outcome")
    validate_candidate_unknowns(report.get("failure_claim"))
    restore_embedded_owners(report.get("original_activation_owners"))
    validate_absence(report.get("absent_original_outcome_owners"),
                     MISSING_OUTCOME_NAMES, relative=EVIDENCE_RELATIVE,
                     label="all four original Go campaign outcomes")
    target_names = tuple(target["relative"].split("/", 1)[1]
                         for target in GO_TARGETS.values())
    validate_absence(report.get("absent_original_canonical_targets"),
                     target_names, relative="candidates",
                     label="both genuinely absent original Go targets")
    for key, value in zero_effects().items():
        require(type(report.get(key)) is type(value) and report.get(key) == value,
                "reject an actual candidate, clock, benchmark, or holdout effect: " + key)


def deterministic_archive(report: Mapping[str, Any], options: Mapping[str, Any]) -> tuple[bytes, bytes]:
    validate_failure_report(report, options)
    plain = canonical(report)
    require(0 < len(plain) <= MAX_PRESERVATION_REPORT_BYTES,
            "bound only the genuinely recorded five-owner failure evidence")
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(compressed) <= MAX_PRESERVATION_REPORT_BYTES,
            "bound one deterministic failure-evidence gzip")
    inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
    restored = inflater.decompress(compressed, MAX_PRESERVATION_REPORT_BYTES + 1)
    require(inflater.eof and not inflater.unused_data
            and not inflater.unconsumed_tail and restored == plain,
            "verify complete, exact, single-member original failure evidence")
    return plain, compressed


def synthetic_owner_graph() -> tuple[dict[str, dict[str, Any]], tuple[tuple[Any, ...], ...]]:
    source_build = expected_build_provenance()
    backup = expected_backup_entries()
    journal = {
        "schema": "rebar-phase2-verified-native-candidate-activation-v4-recovery-journal",
        "status": "PREPARED", "family": "go", "activation_root": PRIVATE_ROOT,
        "promotion_mode": "recoverable-canonical-promotion",
        "activation_source_sha256": ACTIVATION_OWNERS[0][2],
        "activation_protocol_sha256": ACTIVATION_OWNERS[1][2],
        "activation_contract_sha256": ACTIVATION_OWNERS[2][2],
        "source_build": source_build, "backup_entries": backup,
        "native_hashes": {
            "engine": GO_TARGETS["engine"]["sha256"],
            "bridge": GO_TARGETS["bridge"]["sha256"],
            "generated_header":
            "481ebb65cc587749677ce28abeb4f3de111e2f87a18ac547ff0157fce85d2c23",
        },
        "native_sizes": {"engine": GO_TARGETS["engine"]["size_bytes"],
                         "bridge": GO_TARGETS["bridge"]["size_bytes"],
                         "generated_header": 3086},
    }
    journal_raw = canonical(journal)
    journal_digest = hashlib.sha256(journal_raw).hexdigest()
    documents: dict[str, dict[str, Any]] = {"recovery_journal": journal}
    owner_inodes = {role: inode for role, _, _, _, inode in PRIVATE_OWNERS}
    for role in ("engine", "bridge"):
        target = role_spec(role)
        documents[role + "_intention"] = {
            "schema": "rebar-phase2-verified-native-candidate-activation-v4-durable-promotion-intent",
            "status": "PREPARED", "family": "go", "activation_root": PRIVATE_ROOT,
            "role": role, "recovery_journal_sha256": journal_digest,
            "target": {**target, "path": str(ROOT / target["relative"]), "mode": 0o755},
        }
    intentions = {}
    for role in ("engine", "bridge"):
        key = role + "_intention"
        raw = canonical(documents[key])
        original = next(row for row in PRIVATE_OWNERS if row[0] == key)
        intentions[role] = {
            "relative": original[1], "sha256": hashlib.sha256(raw).hexdigest(),
            "size_bytes": len(raw), "device": PRIVATE_ROOT_DEVICE,
            "inode": owner_inodes[key], "mode": 0o600,
            "exclusive_creation": True, "file_fsync_completed": True,
            "same_inode_readback_verified": True,
            "directory_fsync_completed": True,
        }
    targets = {
        role: {**role_spec(role), "promotion_intent": intentions[role]}
        for role in ("engine", "bridge")
    }
    report = {
        "schema": "rebar-phase2-verified-native-candidate-activation-v4",
        "status": "PASS", "family": "go", "activation_root": PRIVATE_ROOT,
        "promotion_mode": "recoverable-canonical-promotion", "group_atomic": False,
        "generated_go_header_promoted": False,
        "activation_source_sha256": ACTIVATION_OWNERS[0][2],
        "activation_protocol_sha256": ACTIVATION_OWNERS[1][2],
        "activation_contract_sha256": ACTIVATION_OWNERS[2][2],
        "recovery_journal_sha256": journal_digest,
        "source_build": source_build, "backup_entries": backup,
        "canonical_targets": targets,
    }
    report_raw = canonical(report)
    report_digest = hashlib.sha256(report_raw).hexdigest()
    report_spec = next(row for row in PRIVATE_OWNERS if row[0] == "activation_report")
    receipt = {
        "schema": "rebar-phase2-verified-native-candidate-activation-v4-durable-publication-receipt",
        "status": "PASS", "family": "go", "activation_root": PRIVATE_ROOT,
        "promotion_mode": "recoverable-canonical-promotion", "group_atomic": False,
        "activation_source_sha256": ACTIVATION_OWNERS[0][2],
        "activation_protocol_sha256": ACTIVATION_OWNERS[1][2],
        "activation_contract_sha256": ACTIVATION_OWNERS[2][2],
        "activation_report_sha256": report_digest,
        "recovery_journal_sha256": journal_digest,
        "source_build": source_build,
        "activation_report": {
            "relative": report_spec[1], "sha256": report_digest,
            "size_bytes": len(report_raw), "device": PRIVATE_ROOT_DEVICE,
            "inode": owner_inodes["activation_report"], "mode": 0o600,
            "exclusive_creation": True, "file_fsync_completed": True,
            "same_inode_readback_verified": True,
            "directory_fsync_completed": True,
        },
    }
    documents["activation_report"] = report
    documents["activation_receipt"] = receipt
    bundle = {}
    specs = []
    for role, name, _, _, inode in PRIVATE_OWNERS:
        raw = canonical(documents[role])
        digest = hashlib.sha256(raw).hexdigest()
        specs.append((role, name, digest, len(raw), inode))
        bundle[role] = {
            "role": role, "relative": name, "path": PRIVATE_ROOT + "/" + name,
            "sha256": digest, "size_bytes": len(raw),
            "device": PRIVATE_ROOT_DEVICE, "inode": inode,
            "mode": 0o600, "uid": EXPECTED_UID,
            "raw": raw, "document": documents[role],
        }
    return bundle, tuple(specs)


def self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []
    probes: list[str] = []

    def accept(name: str, operation: Callable[[], Any]) -> None:
        result = operation()
        require(result is not False, "synthetic acceptance unexpectedly failed: " + name)
        accepted.append(name)

    def reject(name: str, operation: Callable[[], Any]) -> None:
        try:
            operation()
        except (PreservationError, ValueError, TypeError, OverflowError,
                RecursionError, UnicodeError, zlib.error):
            rejected.append(name)
            return
        raise PreservationError("hostile control was not rejected: " + name)

    with EffectBoundary(source_only=True) as guard:
        fixture, specs = synthetic_owner_graph()
        accept("exact-five-synthetic-distinct-owner-graph",
               lambda: validate_activation_bundle(fixture, specs=specs))
        accept("exact-synthetic-zero-effect-policy", zero_effects)
        accept("exact-immutable-original-size-cap",
               lambda: require(MAX_ORIGINAL_REPORT_BYTES == 268435456,
                               "reject a changed original report cap") or True)
        accept("exact-source-only-arguments",
               lambda: parse_arguments(["--self-test"]))
        fake_pin = hashlib.sha256(b"synthetic-failure-freeze").hexdigest()
        for mode in ("--verify-frozen-context", "--preserve"):
            args = [mode, "--source-sha256", fake_pin,
                    "--protocol-sha256", fake_pin,
                    "--contract-sha256", fake_pin]
            accept("exact-" + mode[2:] + "-arguments",
                   lambda args=args: parse_arguments(args))
            for index in range(len(args)):
                reject(mode[2:] + "-reject-omitted-argument-" + str(index),
                       lambda index=index, args=args:
                       parse_arguments(args[:index] + args[index + 1:]))
            reject(mode[2:] + "-reject-hidden-argument",
                   lambda args=args: parse_arguments(args + ["--benchmark"]))
            reject(mode[2:] + "-reject-duplicate-flag",
                   lambda args=args: parse_arguments(
                       [args[0], "--source-sha256", fake_pin,
                        "--source-sha256", fake_pin,
                        "--contract-sha256", fake_pin]))
        for hostile in ([], ["--run"], ["--activate"], ["--benchmark"],
                        ["--self-test", "--preserve"],
                        ["--self-test", "--source-sha256", fake_pin]):
            reject("reject-unauthorized-mode-" + str(len(rejected)),
                   lambda hostile=hostile: parse_arguments(hostile))
        for role, *_ in PRIVATE_OWNERS:
            for field, hostile in (
                ("role", "other"), ("relative", "../escape"),
                ("path", "/tmp/foreign"), ("sha256", "0" * 64),
                ("size_bytes", 0), ("device", PRIVATE_ROOT_DEVICE + 1),
                ("inode", 0), ("mode", 0o644), ("uid", EXPECTED_UID + 1),
                ("raw", b"{}\n"), ("document", {}),
            ):
                attack = copy.deepcopy(fixture)
                attack[role][field] = hostile
                reject("reject-" + role + "-" + field,
                       lambda attack=attack:
                       validate_activation_bundle(attack, specs=specs))
            removed = copy.deepcopy(fixture)
            removed.pop(role)
            reject("reject-omitted-" + role,
                   lambda removed=removed:
                   validate_activation_bundle(removed, specs=specs))
        extra = copy.deepcopy(fixture)
        extra["foreign"] = copy.deepcopy(fixture["activation_report"])
        reject("reject-extra-private-owner",
               lambda: validate_activation_bundle(extra, specs=specs))
        for claim in ("infrastructure_status", "candidate_status",
                      "candidate_qualified", "actual_original_campaign_publication_status",
                      "actual_original_report_publication_max_bytes",
                      "actual_original_archive_publication_max_bytes",
                      "actual_original_report_cap_error",
                      "prepared_journal_is_restoration_proof",
                      "absent_canonical_targets_prove_restoration_route",
                      *UNKNOWN_FIELDS):
            attack = candidate_unknowns()
            attack[claim] = (
                True if isinstance(attack[claim], bool)
                else 0 if isinstance(attack[claim], int)
                else "PASS"
            )
            reject("reject-fabricated-" + claim,
                   lambda attack=attack: validate_candidate_unknowns(attack))
        absence = [{"relative": EVIDENCE_RELATIVE + "/" + name,
                    "present": False} for name in MISSING_OUTCOME_NAMES]
        accept("exact-four-absent-original-outcomes",
               lambda: validate_absence(absence, MISSING_OUTCOME_NAMES,
                                        relative=EVIDENCE_RELATIVE,
                                        label="synthetic original outcomes"))
        for index in range(len(absence)):
            attack = copy.deepcopy(absence)
            attack[index]["present"] = True
            reject("reject-fabricated-original-outcome-" + str(index),
                   lambda attack=attack: validate_absence(
                       attack, MISSING_OUTCOME_NAMES,
                       relative=EVIDENCE_RELATIVE, label="synthetic outcomes"))
        reject("reject-omitted-original-outcome",
               lambda: validate_absence(absence[:-1], MISSING_OUTCOME_NAMES,
                                        relative=EVIDENCE_RELATIVE,
                                        label="synthetic outcomes"))
        target_names = tuple(target["relative"].split("/", 1)[1]
                             for target in GO_TARGETS.values())
        targets = [{"relative": "candidates/" + name, "present": False}
                   for name in target_names]
        accept("exact-two-absent-original-go-targets",
               lambda: validate_absence(targets, target_names,
                                        relative="candidates",
                                        label="synthetic Go targets"))
        for index in range(len(targets)):
            attack = copy.deepcopy(targets)
            attack[index]["present"] = True
            reject("reject-fabricated-original-target-" + str(index),
                   lambda attack=attack: validate_absence(
                       attack, target_names, relative="candidates",
                       label="synthetic Go targets"))
        accept("exact-prepared-journal-never-completed",
               lambda: require(fixture["recovery_journal"]["document"]["status"]
                               == "PREPARED", "reject false restoration") or True)
        for probe, operation in (
            ("file-read", lambda: builtins.open("never-read")),
            ("directory-read", lambda: os.open("never-open", os.O_RDONLY)),
            ("file-write", lambda: os.write(1, b"never")),
            ("file-fsync", lambda: os.fsync(1)),
            ("process", lambda: subprocess.Popen(["never-run"])),
            ("network", lambda: socket.socket()),
            ("clock", lambda: time.perf_counter()),
            ("native-library", lambda: ctypes.CDLL("never-load")),
            ("temporary-root", lambda: tempfile.mkdtemp()),
            ("thread", lambda: threading.Thread().start()),
        ):
            before = sum(guard.blocked.values())
            reject("reject-real-" + probe, operation)
            require(sum(guard.blocked.values()) == before + 1,
                    "an external-effect probe escaped its synthetic guard")
            probes.append(probe)
    return {
        "schema": SCHEMA + "-synthetic-source-only-self-test",
        "status": "PASS", "source_only": True, "synthetic_only": True,
        "accepted_synthetic_control_count": len(accepted),
        "rejected_hostile_control_count": len(rejected),
        "accepted_synthetic_controls": accepted,
        "rejected_hostile_controls": rejected,
        "blocked_effect_probe_count": len(probes),
        "blocked_effect_probes": probes,
        "private_activation_owner_count": len(PRIVATE_OWNERS),
        "missing_original_outcome_owner_count": len(MISSING_OUTCOME_NAMES),
        "original_report_publication_max_bytes": MAX_ORIGINAL_REPORT_BYTES,
        "total_retained_repository_evidence_owner_count": 67,
        **zero_effects(),
    }


def preserve(options: Mapping[str, Any]) -> dict[str, Any]:
    context, bundle, activation = collect_context(options)
    verify_runtime()
    fresh = inspect_missing_names(
        (ARCHIVE_NAME, RECEIPT_NAME), relative=EVIDENCE_RELATIVE,
        label="fresh failure-preservation owner")
    validate_absence(fresh, (ARCHIVE_NAME, RECEIPT_NAME),
                     relative=EVIDENCE_RELATIVE,
                     label="fresh failure-preservation owners")
    report = build_failure_report(options, context, bundle)
    plain, compressed = deterministic_archive(report, options)
    evidence_root = str(ROOT / EVIDENCE_RELATIVE)
    archive = activation.write_fresh(evidence_root, ARCHIVE_NAME, compressed)
    archive_sync = activation.synchronize_directory(evidence_root)
    require(archive.get("relative") == ARCHIVE_NAME
            and archive.get("sha256") == hashlib.sha256(compressed).hexdigest()
            and archive.get("size_bytes") == len(compressed)
            and archive.get("mode") == 0o600
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("same_inode_readback_verified") is True
            and archive_sync.get("completed") is True,
            "independently prove genuine exclusive durable failure archive publication")
    receipt_document = {
        "schema": SCHEMA + "-durable-evidence-publication-receipt",
        "status": "PASS",
        "receipt_status_meaning": "EVIDENCE PUBLICATION ONLY",
        "infrastructure_status": "FAIL",
        "candidate_status": "NOT VERIFIED",
        "candidate_qualified": False,
        "candidate_family": "go",
        "candidate_label": "phase2-v1",
        "preservation_source_sha256": options["source_sha256"],
        "preservation_protocol_sha256": options["protocol_sha256"],
        "preservation_contract_sha256": options["contract_sha256"],
        "original_campaign_source_sha256": CAMPAIGN_OWNERS[0][2],
        "original_campaign_protocol_sha256": CAMPAIGN_OWNERS[1][2],
        "original_campaign_contract_sha256": CAMPAIGN_OWNERS[2][2],
        "actual_original_report_publication_max_bytes": MAX_ORIGINAL_REPORT_BYTES,
        "actual_original_report_bytes": "NOT RECORDED",
        "actual_restoration_route": "NOT RECORDED",
        "actual_suite_statuses": "NOT RECORDED",
        "actual_mismatch_count": "NOT RECORDED",
        "retained_repository_evidence_owner_count": 67,
        "embedded_private_owner_count": len(PRIVATE_OWNERS),
        "embedded_private_owner_total_original_bytes": sum(row[3] for row in PRIVATE_OWNERS),
        "archive": archive,
        "archive_directory_fsync_completed": archive_sync["completed"],
        "uncompressed_sha256": hashlib.sha256(plain).hexdigest(),
        "uncompressed_bytes": len(plain),
        "archive_compression": "gzip-mtime-zero-level-9",
        "original_campaign_publication_failure_preserved": True,
        "all_five_complete_original_owner_bytes_preserved": True,
        "publication_receipt_is_candidate_qualification": False,
        "receipt_self_publication": "NOT CLAIMED",
        **zero_effects(),
    }
    receipt_raw = canonical(receipt_document)
    require(0 < len(receipt_raw) <= MAX_PRESERVATION_REPORT_BYTES,
            "bound the independently owned failure-only publication receipt")
    receipt = activation.write_fresh(evidence_root, RECEIPT_NAME, receipt_raw)
    receipt_sync = activation.synchronize_directory(evidence_root)
    require(receipt.get("relative") == RECEIPT_NAME
            and receipt.get("sha256") == hashlib.sha256(receipt_raw).hexdigest()
            and receipt.get("size_bytes") == len(receipt_raw)
            and receipt.get("mode") == 0o600
            and receipt.get("exclusive_creation") is True
            and receipt.get("file_fsync_completed") is True
            and receipt.get("same_inode_readback_verified") is True
            and receipt_sync.get("completed") is True
            and (receipt.get("device"), receipt.get("inode"))
            != (archive.get("device"), archive.get("inode")),
            "prove independently synchronized distinct owner-only evidence files")
    return {
        "schema": SCHEMA + "-published-failure-evidence",
        "status": "PASS",
        "status_meaning": "FAILURE EVIDENCE PUBLICATION ONLY",
        "infrastructure_status": "FAIL",
        "candidate_status": "NOT VERIFIED",
        "candidate_qualified": False,
        "candidate_family": "go",
        "candidate_label": "phase2-v1",
        "private_owner_count": len(PRIVATE_OWNERS),
        "private_owner_total_original_bytes": sum(row[3] for row in PRIVATE_OWNERS),
        "retained_repository_evidence_owner_count": 67,
        "absent_original_outcome_owner_count": len(MISSING_OUTCOME_NAMES),
        "absent_original_canonical_target_count": len(GO_TARGETS),
        "complete_failure_evidence_archive": archive,
        "archive_directory_fsync_completed": archive_sync["completed"],
        "complete_failure_evidence_publication_receipt": receipt,
        "receipt_directory_fsync_completed": receipt_sync["completed"],
        "original_report_bytes": "NOT RECORDED",
        "original_suite_statuses": "NOT RECORDED",
        "original_mismatch_count": "NOT RECORDED",
        "original_restoration_route": "NOT RECORDED",
        **zero_effects(),
    }


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        options = parse_arguments(arguments)
        if options["mode"] == "self-test":
            result = self_test()
        elif options["mode"] == "verify-frozen-context":
            result, _, _ = collect_context(options)
        else:
            result = preserve(options)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except BaseException as error:
        failure = {
            "schema": SCHEMA + "-entry-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error_message": str(error),
            "candidate_status": "NOT VERIFIED",
            "candidate_qualified": False,
            **zero_effects(),
        }
        try:
            sys.stdout.buffer.write(canonical(failure))
            sys.stdout.buffer.flush()
        except (OSError, TypeError, ValueError):
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
