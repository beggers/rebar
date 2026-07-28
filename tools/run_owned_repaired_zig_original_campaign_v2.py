#!/usr/bin/env python3
"""Freeze the repaired V2 original Python re correctness campaign for Zig.

Source verification cannot activate, import or run a candidate. Real workers
preserve the immutable original V3 observers and continuous isolation guards.
All thirteen workers run before both exact original Zig inodes are restored
and a complete, exclusive, losslessly compressed result is published.
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
import io
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
import traceback
import types
from typing import Any, Sequence

ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_owned_repaired_zig_original_campaign_v2.py"
PROTOCOL_RELATIVE = "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V2.md"
CONTRACT_RELATIVE = "oracle/phase2/repaired-zig-original-campaign-v2.json"
SCHEMA = "rebar-owned-repaired-zig-original-campaign-v2"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
WORKER_SCHEMA = SCHEMA + "-actual-original-suite-worker"
CAMPAIGN_SCHEMA = SCHEMA + "-complete-original-campaign"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
RESULT_SCHEMA = SCHEMA + "-published-complete-original-campaign"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
FAMILY = "zig"
LABEL = "phase2-v11-zig-scanner-original-p0"
BUILD_LABEL = "phase2-v11-zig-scanner"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_STDOUT_BYTES = 256 * 1024 * 1024
MAX_STDERR_BYTES = 16 * 1024 * 1024
MAX_ERROR_BYTES = 64 * 1024
WORKER_TIMEOUT_SECONDS = 8 * 3600
SUITE_COUNT = 13
CASE_COUNT = 31_237
PRIVATE_WAIVER_COUNT = 13
ACTIVATION = {
 "source": ("tools/activate_verified_native_candidate_v6.py", "d3a9b08c1bf7e3408719a0e92b8c1965aa6160dd2e18ab1501bb8662aaf8e4a1", 107982),
 "protocol": ("oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V6.md", "0e736d575835fa22388841a527e22b62eef1ddf39eac9415bd7c518ba985b1d0", 6688),
 "contract": ("oracle/phase2/verified-native-activation-v6.json", "e0d486cc6d621e963f8af5db1c4f7a47d590ad679837db1f53e11d05b670332e", 12902),
}
NORMALIZED_ACTIVATION = {
 "source": ("tools/activate_verified_native_candidate_v7.py", "98002a0a283ffec24670bcb9f35546c5720d2a7a1d098257729d244918022f8e", 61930),
 "protocol": ("oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V7.md", "f333b50f9810cf246ae659c6d07eb4c63b8e2114d07b485b50d570ab272f22f8", 5141),
 "contract": ("oracle/phase2/verified-native-activation-v7.json", "62375f7d013b7b02a160b9492e5aa249b7af556041f2c86f20e7bfd5ad6885b1", 9718),
}
FAILED_CAMPAIGN = {
 "source": ("tools/run_owned_repaired_zig_original_campaign_v1.py", "ff4bc83173930c193de5984659aa6e8aca1848496d06f3d3dca3c28294c37c90", 92313),
 "protocol": ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V1.md", "974c1cc09511c7a119a2ea0f59fab8c39e8d1887c948df19657de2458b5b9d67", 5108),
 "contract": ("oracle/phase2/repaired-zig-original-campaign-v1.json", "f3f1bdfea41b8b4d5bce22b2b236c76f653e97268e500b951fbef262052718f0", 9563),
}
PREFLIGHT_PRESERVER = {
 "source": ("tools/preserve_owned_zig_campaign_preflight_failure_v1.py", "4a401ea42b4446535d51d1c7c65c688196185a0bb9fa2e15aebdb3bfebb85498", 58558),
 "protocol": ("oracle/phase2/ZIG-CAMPAIGN-PREFLIGHT-FAILURE-V1.md", "a3c005c95c61a68a5683125f7805564f4749ea9e82350f2d883da9e29b2817c5", 4413),
 "contract": ("oracle/phase2/zig-campaign-preflight-failure-v1.json", "534a3cde3084c12a4124f5dea057ddb80b53fa4c591c8c72e26931bc277735f0", 16494),
}
PREFLIGHT_ARCHIVE = (
 "oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz",
 "1cb38eb48a2d3305ea98d5103a27ce6ae758137168f68df07a408dec3d055a37",
 3711,
)
PREFLIGHT_RECEIPT = (
 "oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json",
 "e15180c3ae0b313374079007455a810c78f91cabff926560cae702dfbc14bd23",
 1992,
)
PREFLIGHT_UNCOMPRESSED_SHA256 = "df0c3cff6b6f956b58fe43f828d6b8d26efc8b9b0dac8972ae4f9902dd58302d"
PREFLIGHT_UNCOMPRESSED_BYTES = 9482
PREFLIGHT_STDERR_SHA256 = "4810a51ee1a1194292f5fce1414b35fc1e2ed3e280dd28ef326314c84349593e"
PREFLIGHT_STDERR_BYTES = 1539
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
V26 = {
 "renderer": ("tools/render_candidate_current_overview_v26.py", "55c36e916f0da8b9ef7b6992724d1d1f98161e834f4d2d21729663d9671a3982", 80805),
 "inputs": ("docs/evidence/candidate-current-overview-v26.inputs.json", "c29e8df08d9b5a03eaad283b625465ba6638f19f69d7d3ab4ea5512e83c37685", 36434),
 "summary": ("docs/evidence/candidate-current-overview-v26.json", "8ebf2ccb74ae2cf62196a1507f94bd39ff4b103122c450865121306accf71f48", 186394),
 "svg": ("docs/evidence/candidate-current-overview-v26.svg", "52b42c7ceccf45f80777d94820a812c7f8e0f790fba03a57aef28c11573dd9cc", 12936),
}
CURRENT_EVIDENCE_OWNER_COUNT = 141
CURRENT_REFERENCE_COUNT = 146

PRODUCER = {
 "source": ("tools/run_owned_six_family_original_p0_producer_v3.py", "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c", 195555),
 "protocol": ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md", "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76", 5522),
 "contract": ("oracle/phase2/six-family-p0-producer-v3.json", "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1", 26909),
}
PUBLICATION = {
 "source": ("tools/run_owned_six_family_original_p0_campaign_v2.py", "6b06931ff64c5fe5b6bbbc3e970e56c0a94a24c28dfa6d3aa6140fc4d8fb54a1", 101836),
 "protocol": ("oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V2.md", "e47cce8a6f60971bd3c18a4bfe248039ed9abd5b4144ec4355a77825a1435d4e", 4995),
 "contract": ("oracle/phase2/six-family-p0-campaign-v2.json", "e44960e46c590cb5ab482ef323f3ae8598900f144b53a2377f62b3bb827935d7", 21314),
}
GOAL = ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
PHASE_ONE = ("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632)
V25 = {
 "renderer": ("tools/render_candidate_current_overview_v25.py", "9b1eabba4a3bd991c4359af4ab1482fe6f1ce848bb9e5df6fdd9e8bdafb21204", 98948),
 "inputs": ("docs/evidence/candidate-current-overview-v25.inputs.json", "123210219fac109506c03c2f76f89fda33aa5e08b0628fef43b9236d05bc1abe", 37281),
 "summary": ("docs/evidence/candidate-current-overview-v25.json", "8e4101c896e316190928d0710ca4442488c925ee5ef421507ba4dd08ff10a6d9", 144980),
 "svg": ("docs/evidence/candidate-current-overview-v25.svg", "db2f1a11e49fd58701ad89111aa422e619431eb9834d3fb5ae66deffcd75f0bb", 13188),
}
BUILD_ARCHIVE = ("oracle/phase2/evidence/native-source-build-v11-zig-phase2-v11-zig-scanner.json.gz", "e4a1f369b647f588ac5b12585f7d0e30c4ee3409adc88f660081fb7a59a8df5c", 48246)
BUILD_RECEIPT = ("oracle/phase2/evidence/native-source-build-v11-zig-phase2-v11-zig-scanner-publication-receipt.json", "d53766d0dad571f8b72288cece15fb1ad0892db32c3b3b6b512027db94ca4fcc", 1683)
ENGINE_SHA256 = "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071"
ENGINE_BYTES = 108888
BRIDGE_SHA256 = "75032107c7769f24f0c80a6e473a26dad3c74f99290e3d89bf46767e07ec3681"
BRIDGE_BYTES = 133656
DERIVED_BRIDGE_SHA256 = "a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148"
SOURCE_OWNERS = (
 ("candidates/zig_candidate.py", "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862", 68422),
 ("candidates/zig/mini_regex.zig", "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28", 186915),
 ("candidates/zig/py_bridge.c", "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b", 173026),
)
SUITES = (
 ("original_bounded_v5", 151), ("public_v3", 864),
 ("scanner_v3", 1024), ("buffer_v3", 768), ("managed_v1", 1024),
 ("scanner_verbose_v1", 2854), ("public_types_v1", 6912),
 ("substitution_v2", 5120), ("shape_v2", 10240),
 ("public_surface_v19", 1376), ("subinterpreter_v2", 128),
 ("pep688_v4", 264), ("threaded_pattern_v1", 512),
)


class CampaignError(Exception):
    """A complete original Zig campaign or recovery was not proven."""


class SourceOnlyViolation(CampaignError):
    """An effect was attempted in an effect-free synthetic source gate."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise CampaignError(message)


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value),
            "require one exact lowercase SHA-256: " + label)
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 64
            and all(c.isascii() and (c.isalnum() or c in "-_") for c in value),
            "require exactly one safe frozen original Zig campaign label")
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and bool(value) and not value.startswith("/")
            and "\\" not in value and "\x00" not in value
            and all(c not in ("", ".", "..") for c in value.split("/")),
            "refuse absolute, broad, escaping or ambiguous owners")
    return value


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=True, allow_nan=False,
                          sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise CampaignError("reject incomplete or noncanonical evidence") from error


def strict_document(raw: bytes, label: str) -> dict[str, Any]:
    def unique(rows: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in rows:
            require(type(key) is str and key not in result,
                    "reject duplicate JSON keys in " + label)
            result[key] = value
        return result

    def invalid(value: str) -> Any:
        raise CampaignError("reject nonfinite JSON in " + label)

    try:
        document = json.loads(raw, object_pairs_hook=unique,
                              parse_constant=invalid)
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise CampaignError("reject incomplete JSON: " + label) from error
    require(type(document) is dict and canonical(document) == raw,
            "require exact canonical bytes: " + label)
    return document


def bounded_error(error: BaseException) -> str:
    raw = str(error).encode("utf-8", "backslashreplace")
    if len(raw) > MAX_ERROR_BYTES:
        raw = raw[:MAX_ERROR_BYTES] + b" [error summary truncated]"
    return raw.decode("utf-8", "replace")


def owner_record(value: tuple[str, str, int]) -> dict[str, Any]:
    return {"path": value[0], "sha256": value[1], "bytes": value[2]}


def mapped_owners(group: dict[str, tuple[str, str, int]]) -> dict[str, Any]:
    return {name: owner_record(item) for name, item in sorted(group.items())}


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PYTHON
            and os.path.realpath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and os.path.realpath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "use only isolated, pinned, no-bytecode stable CPython 3.14.6")


def read_owner(relative: str, expected: str, *,
               maximum: int = MAX_SOURCE_BYTES,
               exact_size: int | None = None,
               owner_only: bool = False) -> tuple[bytes, dict[str, Any]]:
    checked_relative(relative)
    checked_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_STDOUT_BYTES,
            "bound every independently authenticated original owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        parent = os.open(str(ROOT), directory_flags)
        opened.append(parent)
        parts = relative.split("/")
        for part in parts[:-1]:
            parent = os.open(part, directory_flags, dir_fd=parent)
            opened.append(parent)
        descriptor = os.open(parts[-1], flags, dir_fd=parent)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
                and (before.st_dev, before.st_ino, before.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and 0 < before.st_size <= maximum
                and (exact_size is None or before.st_size == exact_size)
                and (not owner_only or stat.S_IMODE(before.st_mode) == 0o600),
                "reject incomplete, linked, changed or redirected owner: " + relative)
        remaining = before.st_size
        blocks: list[bytes] = []
        digest = hashlib.sha256()
        while remaining:
            part = os.read(descriptor, min(remaining, 1048576))
            require(type(part) is bytes and bool(part),
                    "reject truncated frozen original bytes: " + relative)
            remaining -= len(part)
            blocks.append(part)
            digest.update(part)
        require(os.read(descriptor, 1) == b"",
                "reject hidden trailing original bytes")
        after = os.fstat(descriptor)
        final = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (after.st_dev, after.st_ino, after.st_size)
                == (final.st_dev, final.st_ino, final.st_size)
                and digest.hexdigest() == expected,
                "reject a concurrently substituted original owner: " + relative)
        return b"".join(blocks), {
            "relative": relative, "path": str(ROOT / relative),
            "sha256": expected, "bytes": after.st_size,
            "device": after.st_dev, "inode": after.st_ino,
            "mode": stat.S_IMODE(after.st_mode), "nlink": after.st_nlink,
            "uid": after.st_uid,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def load_frozen(owner: tuple[str, str, int],
                purpose: str) -> types.ModuleType:
    relative, digest, size = owner
    raw, first = read_owner(relative, digest, exact_size=size)
    name = "_rebar_owned_zig_original_campaign_v2_" + purpose + "_" + digest[:20]
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__file__ = str(ROOT / relative)
        module.__package__ = ""
        sys.modules[name] = module
        try:
            exec(compile(raw, module.__file__, "exec", dont_inherit=True),
                 module.__dict__)
        except BaseException:
            sys.modules.pop(name, None)
            raise
    _, final = read_owner(relative, digest, exact_size=size)
    require(type(module) is types.ModuleType and module.__name__ == name
            and os.path.abspath(str(getattr(module, "__file__", "")))
            == str(ROOT / relative)
            and os.path.realpath(str(module.__file__)) == str(ROOT / relative)
            and (first["device"], first["inode"])
            == (final["device"], final["inode"]),
            "reject an imported or substituted frozen owner: " + purpose)
    return module


def source_effects() -> dict[str, Any]:
    return {
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "canonical_target_links": 0, "canonical_target_replacements": 0,
        "source_freeze_original_targets_read": 0,
        "source_freeze_original_targets_statted": 0,
        "source_freeze_original_targets_modified": 0,
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "actual_reference_workers": 0, "actual_native_activations": 0,
        "actual_native_recoveries": 0, "actual_native_libraries_loaded": 0,
        "actual_subprocesses_started": 0, "actual_threads_started": 0,
        "actual_network_requests": 0, "workspace_mutations": 0,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False, "winner_selected": False,
    }


def protocol_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "campaign source")
    checked_digest(protocol_pin, "campaign protocol")
    return {
        "schema": CONTRACT_SCHEMA,
        "version": 2,
        "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; V2 ZIG CANDIDATE NOT YET RUN",
        "family": FAMILY,
        "campaign_label": LABEL,
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "pinned_cpython": {
            "path": PYTHON, "sha256": PYTHON_SHA256, "version": "3.14.6"
        },
        "goal": owner_record(GOAL),
        "phase_one": owner_record(PHASE_ONE),
        "original_v3_producer": mapped_owners(PRODUCER),
        "verified_zig_v7_normalized_activation": mapped_owners(
            NORMALIZED_ACTIVATION),
        "verified_zig_v6_private_journal_predecessor": mapped_owners(ACTIVATION),
        "verified_zig_v6_activation": mapped_owners(ACTIVATION),
        "actual_failed_first_original_campaign": {
            "owners": mapped_owners(FAILED_CAMPAIGN),
            "status": "FAIL",
            "failure_class": "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
            "actual_controller_runs": 1,
            "actual_controller_exit_status": 1,
            "actual_controller_process_id": "NOT RECORDED",
            "actual_candidate_workers": 0,
            "actual_matching_case_execution_count": 0,
            "completed_suite_count": 0,
            "semantic_mismatch_count": "NOT MEASURED",
            "candidate_correctness": "NOT MEASURED",
            "actual_native_activations": 0,
            "original_native_targets_unchanged": True,
            "complete_stdout_bytes": 0,
            "complete_stdout_sha256": EMPTY_SHA256,
            "complete_stderr_bytes": PREFLIGHT_STDERR_BYTES,
            "complete_stderr_sha256": PREFLIGHT_STDERR_SHA256,
            "actual_traceback_frame_count": 6,
            "preservation_owners": mapped_owners(PREFLIGHT_PRESERVER),
            "archive": owner_record(PREFLIGHT_ARCHIVE),
            "receipt": owner_record(PREFLIGHT_RECEIPT),
            "receipt_status": "PASS",
            "receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
            "receipt_preserved_failure_status": "FAIL",
            "uncompressed_sha256": PREFLIGHT_UNCOMPRESSED_SHA256,
            "uncompressed_bytes": PREFLIGHT_UNCOMPRESSED_BYTES,
        },
        "current_published_v26_history": {
            "owners": mapped_owners(V26),
            "authoritative_evidence_owner_count":
                CURRENT_EVIDENCE_OWNER_COUNT,
            "authenticated_reference_count": CURRENT_REFERENCE_COUNT,
            "actual_c_candidate_workers": 13,
            "actual_c_semantic_mismatch_count": 1262,
            "actual_c_verified_passing_case_count": 7325,
            "actual_c_infrastructure_failure_count": 0,
            "actual_rust_compiler_process_count": 28,
            "actual_rust_public_source_repair_count": 2,
            "actual_rust_bridge_source_repair_count": 2,
            "actual_zig_compiler_process_count": 26,
            "actual_zig_original_controller_runs": 1,
            "actual_zig_original_controller_exit_status": 1,
            "actual_zig_original_controller_process_id": "NOT RECORDED",
            "actual_zig_original_candidate_workers": 0,
            "actual_zig_original_matching_case_count": 0,
            "actual_zig_original_failure_class":
                "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
            "actual_zig_original_semantic_mismatch_count": "NOT MEASURED",
            "qualified_candidate_count": 0,
            "holdout": "NOT OPENED",
        },
        "historical_v25_history": {
            "owners": mapped_owners(V25),
            "historical_evidence_owner_count": 139,
            "historical_authenticated_reference_count": 144,
            "actual_c_candidate_workers": 13,
            "actual_c_semantic_mismatch_count": 1262,
            "actual_c_verified_passing_case_count": 7325,
            "actual_rust_compiler_process_count": 28,
            "actual_rust_public_source_repair_count": 2,
            "actual_rust_bridge_source_repair_count": 2,
            "historical_zig_semantic_mismatch_count": 1764,
            "qualified_candidate_count": 0,
        },
        "historical_v2_publication_primitives": {
            "owners": mapped_owners(PUBLICATION),
            "used_only_for": [
                "bounded-canonical-single-member-gzip",
                "complete-stream-readback",
                "exclusive-owner-only-archive-publication",
            ],
            "v2_cpp_or_go_matching_invoked": False,
        },
        "actual_zig_v11_source_build": {
            "label": BUILD_LABEL,
            "archive": owner_record(BUILD_ARCHIVE),
            "receipt": owner_record(BUILD_RECEIPT),
            "actual_compiler_process_count": 26,
            "independent_source_phase_count": 2,
            "historical_evidence_owner_count_at_build": 135,
            "historical_reference_count_at_build": 140,
            "derived_first_party_scanner_bridge_sha256":
                DERIVED_BRIDGE_SHA256,
            "native_roles": [
                {
                    "role": "engine", "path": "candidates/_zig_probe.so",
                    "sha256": ENGINE_SHA256, "bytes": ENGINE_BYTES,
                    "original_inode": 431260, "original_mode": "0700",
                },
                {
                    "role": "bridge",
                    "path":
                        "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
                    "sha256": BRIDGE_SHA256, "bytes": BRIDGE_BYTES,
                    "original_inode": 431274, "original_mode": "0700",
                },
            ],
            "byte_identical_native_role_count": 2,
        },
        "owned_zig_source_closure": [
            owner_record(item) for item in SOURCE_OWNERS
        ],
        "original_oracle": {
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "source_ordered_suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES
            ],
            "unchanged_original_v3_observers": [
                "observe_original_upstream",
                "observe_direct_suite",
                "observe_subinterpreters",
            ],
            "original_source_changed": False,
            "upstream_public_record_count": 152,
            "upstream_runnable_public_case_count": 151,
            "upstream_debug_build_skip_count": 1,
            "upstream_named_private_waiver_count": 13,
            "nested_case_count": 128,
            "nested_actual_case_interpreter_events": 394,
            "nested_actual_interpreters_created": 11,
            "nested_actual_interpreters_destroyed": 11,
            "nested_fresh_temporary_interpreters": 8,
            "scanner_callback_cases_preserved": True,
            "substitution_callback_cases_preserved": True,
            "pep688_original_buffer_cases_preserved": True,
            "threaded_pattern_cases_preserved": True,
            "no_supplemental_cases": True,
        },
        "worker_policy": {
            "exact_actual_worker_count": 13,
            "one_independent_process_per_original_suite": True,
            "run_all_original_suites_after_a_mismatch": True,
            "complete_stdout_and_stderr_preserved": True,
            "complete_original_records_and_mismatches_preserved": True,
            "complete_infrastructure_failures_preserved": True,
            "no_suite_filter": True,
            "no_early_candidate_qualification": True,
            "v3_legacy_activation_dispatch_invoked": False,
            "v3_original_observers_and_continuous_guards_unchanged": True,
            "zig_only_owned_ctypes_allowed": True,
            "owned_ctypes_native_target": "candidates/_zig_probe.so",
            "external_regex_engine": "FORBIDDEN",
            "stdlib_regex_matching": "FORBIDDEN",
            "other_candidate_matching": "FORBIDDEN",
            "fallback": "FORBIDDEN",
        },
        "recovery_policy": {
            "activation_version": 7,
            "inherited_private_journal_version": 6,
            "normalized_verify_context_errors_caught": True,
            "normalized_activation_errors_caught": True,
            "normalized_recovery_errors_caught": True,
            "normalized_error_exit_status": 1,
            "keyboard_interrupt_not_caught": True,
            "system_exit_not_caught": True,
            "canonical_zig_role_count": 2,
            "mature_owner_normalization":
                "DESCRIPTOR-BOUND TRUE UID AND NLINK",
            "exact_original_inode_backup": "ADJACENT SAME-DEVICE HARDLINK",
            "baseline_inside_protected_outer_try": True,
            "original_inode_preservation_required": True,
            "fixed_restoration_order": ["bridge", "engine"],
            "group_atomic": False,
            "recover_on_worker_mismatch": True,
            "recover_on_worker_crash": True,
            "recover_on_worker_timeout": True,
            "recover_on_controller_error": True,
            "verify_exact_original_device_inode_mode_uid_and_nlink": True,
            "restore_both_original_targets_before_publication": True,
            "touch_c_native_target": False,
            "touch_rust_native_targets": False,
        },
        "publication_policy": {
            "directory": EVIDENCE_RELATIVE,
            "stem": "repaired-zig-original-campaign-v2-zig-" + LABEL,
            "pass_suffix": ".json.gz",
            "failure_suffix": "-failures.json.gz",
            "receipt_suffix": "-publication-receipt.json",
            "publish_only_after_verified_original_restoration": True,
            "archive_complete_all_13_original_worker_streams": True,
            "single_member_gzip_mtime": 0,
            "gzip_compression_level": 9,
            "exclusive_archive_creation": True,
            "exclusive_receipt_creation": True,
            "mode": "0600",
            "full_stream_readback_required": True,
            "directory_fsync_required": True,
            "omit_existing_evidence": False,
            "overwrite_existing_evidence": False,
            "existing_first_preflight_failure_retained": True,
        },
        "source_only_effects": source_effects(),
    }

def validate_contract(value: Any, source_pin: str,
                      protocol_pin: str) -> dict[str, Any]:
    require(type(value) is dict and canonical(value)
            == canonical(protocol_document(source_pin, protocol_pin)),
            "reject an incomplete, changed or weakened original Zig campaign")
    return value


class SourceWall:
    """Block all real effects while running hostile synthetic controls."""

    def __init__(self) -> None:
        self.previous: list[tuple[Any, str, Any]] = []
        self.blocked = {name: 0 for name in (
            "filesystem", "process", "clock", "network",
            "thread", "native", "import",
        )}

    def install(self, owner: Any, name: str, kind: str) -> None:
        if not hasattr(owner, name):
            return
        old = getattr(owner, name)

        def deny(*args: Any, **kwargs: Any) -> Any:
            self.blocked[kind] += 1
            raise SourceOnlyViolation("source-only mode forbids " + kind)

        self.previous.append((owner, name, old))
        setattr(owner, name, deny)

    def __enter__(self) -> "SourceWall":
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"),
            (os, "read"), (os, "write"), (os, "stat"), (os, "lstat"),
            (os, "fstat"), (os, "link"), (os, "replace"),
            (os, "rename"), (os, "unlink"), (os, "remove"),
            (os, "mkdir"), (os, "makedirs"), (os, "fsync"),
            (os, "fchmod"), (tempfile, "mkdtemp"),
        ):
            self.install(owner, name, "filesystem")
        for name in ("Popen", "run", "call", "check_output"):
            self.install(subprocess, name, "process")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "sleep"):
            self.install(time, name, "clock")
        self.install(socket, "create_connection", "network")
        self.install(socket.socket, "connect", "network")
        self.install(threading.Thread, "start", "thread")
        self.install(ctypes, "CDLL", "native")
        self.install(importlib, "import_module", "import")
        return self

    def __exit__(self, *_: Any) -> None:
        for owner, name, previous in reversed(self.previous):
            setattr(owner, name, previous)


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(contract_pin, "frozen original campaign contract")
    accepted: list[str] = []
    rejected: list[str] = []
    with SourceWall() as wall:
        frozen = protocol_document(source_pin, protocol_pin)

        def accept(name: str, valid: Any) -> None:
            require(valid is True, "positive source control failed: " + name)
            accepted.append(name)

        def reject(name: str, action: Any) -> None:
            try:
                action()
            except (CampaignError, SourceOnlyViolation, OSError, ValueError,
                    TypeError, UnicodeError, OverflowError, RecursionError):
                rejected.append(name)
                return
            raise CampaignError("a hostile source control passed: " + name)

        class SyntheticNormalizedActivationError(Exception):
            """Exercise the genuine ordinary V7 exception hierarchy."""

        def normalized_failure_is_caught(stage: str) -> bool:
            try:
                raise SyntheticNormalizedActivationError(stage)
            except Exception as error:
                return (
                    type(error) is SyntheticNormalizedActivationError
                    and str(error) == stage
                )

        def control_signal_escapes(signal: BaseException) -> bool:
            try:
                try:
                    raise signal
                except Exception:
                    return False
            except BaseException as observed:
                return observed is signal
            return False

        history = frozen["historical_v25_history"]
        build = frozen["actual_zig_v11_source_build"]
        oracle = frozen["original_oracle"]
        workers = frozen["worker_policy"]
        recovery = frozen["recovery_policy"]
        publication = frozen["publication_policy"]
        current = frozen["current_published_v26_history"]
        preserved = frozen["actual_failed_first_original_campaign"]
        for stage in ("verify-frozen-context", "activate", "recover"):
            accept(
                "catch-genuine-ordinary-v7-" + stage + "-error",
                normalized_failure_is_caught(stage),
            )
        accept(
            "do-not-swallow-keyboard-interrupt",
            control_signal_escapes(KeyboardInterrupt("synthetic interrupt")),
        )
        accept(
            "do-not-swallow-system-exit",
            control_signal_escapes(SystemExit(1)),
        )
        accept(
            "freeze-controlled-v7-exit-and-signal-policy",
            recovery["normalized_verify_context_errors_caught"] is True
            and recovery["normalized_activation_errors_caught"] is True
            and recovery["normalized_recovery_errors_caught"] is True
            and recovery["normalized_error_exit_status"] == 1
            and recovery["keyboard_interrupt_not_caught"] is True
            and recovery["system_exit_not_caught"] is True,
        )
        accept("current-released-v26-exact-141-evidence-owners",
               current["authoritative_evidence_owner_count"] == 141)
        accept("current-released-v26-exact-146-authenticated-references",
               current["authenticated_reference_count"] == 146)
        accept("authenticate-all-four-exact-released-v26-owners",
               current["owners"] == mapped_owners(V26))
        accept("use-exact-normalized-v7-three-owner-freeze",
               frozen["verified_zig_v7_normalized_activation"]
               == mapped_owners(NORMALIZED_ACTIVATION))
        accept("retain-actual-v6-inherited-private-journal-schema",
               frozen["verified_zig_v6_private_journal_predecessor"]
               == mapped_owners(ACTIVATION)
               and recovery["activation_version"] == 7
               and recovery["inherited_private_journal_version"] == 6)
        accept("retain-real-first-v1-infrastructure-failure",
               preserved["status"] == "FAIL"
               and preserved["failure_class"]
               == "PRE-ACTIVATION INFRASTRUCTURE FAILURE")
        accept("never-count-failure-receipt-as-candidate-pass",
               preserved["receipt_status"] == "PASS"
               and preserved["receipt_pass_means"]
               == "DURABLE FAILURE PUBLICATION ONLY"
               and preserved["receipt_preserved_failure_status"] == "FAIL"
               and preserved["candidate_correctness"] == "NOT MEASURED")
        accept("retain-both-exact-distinct-published-failure-owners",
               preserved["archive"] == owner_record(PREFLIGHT_ARCHIVE)
               and preserved["receipt"] == owner_record(PREFLIGHT_RECEIPT)
               and preserved["archive"]["path"]
               != preserved["receipt"]["path"])
        accept("retain-genuine-controller-and-six-traceback-frames",
               preserved["actual_controller_runs"] == 1
               and preserved["actual_controller_exit_status"] == 1
               and preserved["actual_controller_process_id"] == "NOT RECORDED"
               and preserved["actual_traceback_frame_count"] == 6)
        accept("retain-exact-complete-first-attempt-streams",
               preserved["complete_stdout_bytes"] == 0
               and preserved["complete_stdout_sha256"] == EMPTY_SHA256
               and preserved["complete_stderr_bytes"] == PREFLIGHT_STDERR_BYTES
               and preserved["complete_stderr_sha256"]
               == PREFLIGHT_STDERR_SHA256)
        accept("retain-zero-real-first-attempt-workers-and-matching",
               preserved["actual_candidate_workers"] == 0
               and preserved["actual_matching_case_execution_count"] == 0
               and preserved["semantic_mismatch_count"] == "NOT MEASURED")
        accept("protect-original-baseline-inside-outer-try",
               recovery["baseline_inside_protected_outer_try"] is True)

        accept("all-thirteen-original-suites", len(SUITES) == 13)
        accept("all-31237-original-case-executions",
               sum(value for _, value in SUITES) == 31237)
        accept("exact-pushed-v6-three-owner-freeze",
               frozen["verified_zig_v6_activation"] == mapped_owners(ACTIVATION))
        accept("exact-immutable-v3-original-observer",
               frozen["original_v3_producer"] == mapped_owners(PRODUCER))
        accept("historical-only-v25-139-144",
               history["historical_evidence_owner_count"] == 139
               and history["historical_authenticated_reference_count"] == 144)
        accept("distinct-historical-135-140-zig-build",
               build["historical_evidence_owner_count_at_build"] == 135
               and build["historical_reference_count_at_build"] == 140)
        accept("real-26-zig-28-rust-processes",
               build["actual_compiler_process_count"] == 26
               and history["actual_rust_compiler_process_count"] == 28)
        accept("retain-real-c-losses", history["actual_c_semantic_mismatch_count"]
               == 1262 and history["actual_c_candidate_workers"] == 13)
        accept("two-real-native-zig-roles", len(build["native_roles"]) == 2)
        accept("retain-exact-original-user-inodes",
               [x["original_inode"] for x in build["native_roles"]]
               == [431260, 431274])
        accept("all-152-upstream-records",
               oracle["upstream_public_record_count"] == 152)
        accept("151-real-cpython-methods-and-one-debug-skip",
               oracle["upstream_runnable_public_case_count"] == 151
               and oracle["upstream_debug_build_skip_count"] == 1)
        accept("retain-all-thirteen-named-private-waivers",
               oracle["named_private_waiver_count"] == 13)
        accept("real-128-case-394-event-lifecycle",
               oracle["nested_case_count"] == 128
               and oracle["nested_actual_case_interpreter_events"] == 394)
        accept("create-and-destroy-eleven-real-interpreters",
               oracle["nested_actual_interpreters_created"] == 11
               and oracle["nested_actual_interpreters_destroyed"] == 11)
        accept("allow-owned-zig-ctypes-only",
               workers["zig_only_owned_ctypes_allowed"] is True
               and workers["owned_ctypes_native_target"]
               == "candidates/_zig_probe.so")
        accept("never-call-obsolete-v3-activation",
               workers["v3_legacy_activation_dispatch_invoked"] is False)
        accept("never-invoke-v2-cpp-or-go-matching",
               frozen["historical_v2_publication_primitives"]
               ["v2_cpp_or_go_matching_invoked"] is False)
        accept("run-all-real-workers-after-every-mismatch",
               workers["exact_actual_worker_count"] == 13
               and workers["run_all_original_suites_after_a_mismatch"] is True)
        accept("retain-every-complete-worker-stream",
               workers["complete_stdout_and_stderr_preserved"] is True
               and publication["archive_complete_all_13_original_worker_streams"]
               is True)
        accept("truthful-independent-per-file-replacement",
               recovery["group_atomic"] is False)
        accept("preserve-exact-original-inodes",
               recovery["original_inode_preservation_required"] is True)
        accept("reverse-restore-before-exclusive-publication",
               recovery["fixed_restoration_order"] == ["bridge", "engine"]
               and publication["publish_only_after_verified_original_restoration"]
               is True)
        accept("canonical-full-contract-roundtrip",
               strict_document(canonical(frozen), "synthetic full contract")
               == frozen)
        fixture = canonical({"cases": ["real", "original"], "status": "PASS"})
        compressed = gzip.compress(fixture, compresslevel=9, mtime=0)
        accept("lossless-deterministic-zero-mtime-gzip",
               gzip.decompress(compressed) == fixture
               and compressed == gzip.compress(fixture, compresslevel=9, mtime=0)
               and compressed[4:8] == b"\x00\x00\x00\x00")
        for value in ("", "a" * 63, "a" * 65, "A" * 64,
                      "g" * 64, None, 1):
            reject("hostile-digest-" + repr(value),
                   lambda x=value: checked_digest(x, "hostile"))
        for value in ("", "/", "/tmp", "../x", "a/../b", "a//b",
                      "a\\b", "a\x00b", None, 1):
            reject("hostile-relative-" + repr(value),
                   lambda x=value: checked_relative(x))
        mutations = (
            ("let-v7-verify-context-error-escape",
             lambda x: x["recovery_policy"].update(
                 {"normalized_verify_context_errors_caught": False})),
            ("let-v7-activation-error-escape",
             lambda x: x["recovery_policy"].update(
                 {"normalized_activation_errors_caught": False})),
            ("let-v7-recovery-error-escape",
             lambda x: x["recovery_policy"].update(
                 {"normalized_recovery_errors_caught": False})),
            ("invent-successful-v7-error-exit",
             lambda x: x["recovery_policy"].update(
                 {"normalized_error_exit_status": 0})),
            ("swallow-keyboard-interrupt",
             lambda x: x["recovery_policy"].update(
                 {"keyboard_interrupt_not_caught": False})),
            ("swallow-system-exit",
             lambda x: x["recovery_policy"].update(
                 {"system_exit_not_caught": False})),
            ("substitute-current-v26-owner-count",
             lambda x: x["current_published_v26_history"].update(
                 {"authoritative_evidence_owner_count": 139})),
            ("substitute-current-v26-reference-count",
             lambda x: x["current_published_v26_history"].update(
                 {"authenticated_reference_count": 144})),
            ("hide-real-first-preflight-failure",
             lambda x: x["actual_failed_first_original_campaign"].update(
                 {"status": "PASS"})),
            ("invent-first-attempt-candidate-worker",
             lambda x: x["actual_failed_first_original_campaign"].update(
                 {"actual_candidate_workers": 1})),
            ("count-failure-publication-receipt-as-candidate-pass",
             lambda x: x["actual_failed_first_original_campaign"].update(
                 {"receipt_preserved_failure_status": "PASS"})),
            ("replace-normalized-v7-with-broken-v6-direct-activation",
             lambda x: x["recovery_policy"].update(
                 {"activation_version": 6})),
            ("misidentify-real-v6-private-journal-as-v7",
             lambda x: x["recovery_policy"].update(
                 {"inherited_private_journal_version": 7})),
            ("leave-baseline-outside-recovery-protected-try",
             lambda x: x["recovery_policy"].update(
                 {"baseline_inside_protected_outer_try": False})),
            ("weaken-case-denominator",
             lambda x: x["original_oracle"].update(
                 {"case_execution_denominator": 151})),
            ("omit-original-suite",
             lambda x: x["original_oracle"]["source_ordered_suites"].pop()),
            ("invent-correctness",
             lambda x: x["source_only_effects"].update(
                 {"candidate_correctness": "PASS", "candidate_qualified": True})),
            ("skip-workers-after-mismatch",
             lambda x: x["worker_policy"].update(
                 {"run_all_original_suites_after_a_mismatch": False})),
            ("erase-original-worker-stream",
             lambda x: x["worker_policy"].update(
                 {"complete_stdout_and_stderr_preserved": False})),
            ("borrow-external-v2-matching",
             lambda x: x["historical_v2_publication_primitives"].update(
                 {"v2_cpp_or_go_matching_invoked": True})),
            ("invoke-obsolete-v3-activation",
             lambda x: x["worker_policy"].update(
                 {"v3_legacy_activation_dispatch_invoked": True})),
            ("allow-foreign-ctypes",
             lambda x: x["worker_policy"].update(
                 {"owned_ctypes_native_target": "external.so"})),
            ("publish-before-restoration",
             lambda x: x["publication_policy"].update(
                 {"publish_only_after_verified_original_restoration": False})),
            ("copy-original-inode",
             lambda x: x["recovery_policy"].update(
                 {"original_inode_preservation_required": False})),
            ("invent-group-atomicity",
             lambda x: x["recovery_policy"].update({"group_atomic": True})),
            ("reverse-recovery",
             lambda x: x["recovery_policy"].update(
                 {"fixed_restoration_order": ["engine", "bridge"]})),
            ("replace-historical-v25-history",
             lambda x: x["historical_v25_history"].update(
                 {"authoritative_evidence_owner_count": 135})),
            ("hide-c-losses",
             lambda x: x["historical_v25_history"].update(
                 {"actual_c_semantic_mismatch_count": 0})),
            ("open-sealed-holdout",
             lambda x: x["source_only_effects"].update({"holdout": "OPENED"})),
        )
        for name, mutate in mutations:
            def hostile(operation: Any = mutate) -> None:
                changed = copy.deepcopy(frozen)
                operation(changed)
                validate_contract(changed, source_pin, protocol_pin)
            reject(name, hostile)
        for name, action in (
            ("filesystem", lambda: os.open("/forbidden", os.O_RDONLY)),
            ("process", lambda: subprocess.run(["/usr/bin/true"])),
            ("clock", lambda: time.perf_counter_ns()),
            ("network", lambda: socket.create_connection(("invalid", 1))),
            ("native", lambda: ctypes.CDLL("foreign-regex.so")),
            ("import", lambda: importlib.import_module("candidates.zig_candidate")),
            ("thread", lambda: threading.Thread(target=lambda: None).start()),
        ):
            reject("block-real-" + name, action)
        blocked = dict(wall.blocked)
    require(len(accepted) >= 20 and all(x > 0 for x in blocked.values()),
            "require every genuine hostile source-isolation category")
    return {
        "schema": SCHEMA + "-synthetic-self-test",
        "status": "PASS", "version": 2, "family": FAMILY,
        "mode": "SYNTHETIC SOURCE ONLY",
        "accepted_control_count": len(accepted),
        "accepted_controls": accepted,
        "rejected_hostile_control_count": len(rejected),
        "rejected_hostile_controls": rejected,
        "blocked_effects_by_kind": blocked,
        "suite_count": 13, "case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "published_v26_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
        "published_v26_authenticated_reference_count": CURRENT_REFERENCE_COUNT,
        "historical_v25_evidence_owner_count": 139,
        "historical_v25_authenticated_reference_count": 144,
        "actual_first_v1_attempt_status": "FAIL",
        "actual_first_v1_candidate_workers": 0,
        "actual_first_v1_matching_case_execution_count": 0,
        "actual_first_v1_candidate_correctness": "NOT MEASURED",
        "actual_first_v1_receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
        "normalized_activation_version": 7,
        "inherited_private_journal_version": 6,
        "normalized_verify_context_errors_caught": True,
        "normalized_activation_errors_caught": True,
        "normalized_recovery_errors_caught": True,
        "normalized_error_exit_status": 1,
        "keyboard_interrupt_not_caught": True,
        "system_exit_not_caught": True,
        "zig_build_historical_evidence_owner_count": 135,
        "zig_build_historical_reference_count": 140,
        "actual_zig_build_process_count": 26,
        "actual_rust_build_process_count": 28,
        "actual_c_semantic_mismatch_count": 1262,
        "actual_c_candidate_worker_count": 13,
        "native_role_count": 2, "restoration_order": ["bridge", "engine"],
        "group_atomic": False, **source_effects(),
    }


def reference_matches(
    reference: Any, definition: tuple[str, str, int],
    owner: dict[str, Any] | None = None,
) -> bool:
    if not (
        type(reference) is dict
        and reference.get("path") == definition[0]
        and reference.get("sha256") == definition[1]
        and reference.get("bytes") == definition[2]
    ):
        return False
    if owner is None:
        return True
    expected_mode = format(owner["mode"], "04o")
    return (
        reference.get("device") == owner["device"]
        and reference.get("inode") == owner["inode"]
        and reference.get("mode") in (owner["mode"], expected_mode)
        and reference.get("nlink") == owner["nlink"]
        and ("uid" not in reference or reference["uid"] == owner["uid"])
    )


def authenticate_preserved_failure() -> dict[str, Any]:
    for definition in FAILED_CAMPAIGN.values():
        read_owner(*definition[:2], exact_size=definition[2])
    for definition in PREFLIGHT_PRESERVER.values():
        read_owner(*definition[:2], exact_size=definition[2])
    freeze_raw, _ = read_owner(
        *PREFLIGHT_PRESERVER["contract"][:2],
        exact_size=PREFLIGHT_PRESERVER["contract"][2],
    )
    freeze = strict_document(
        freeze_raw, "genuine frozen first-failure preservation contract")
    require(
        freeze.get("schema")
        == "rebar-owned-zig-campaign-preflight-failure-v1-source-freeze"
        and freeze.get("version") == 1
        and freeze.get("family") == FAMILY
        and freeze.get("label") == LABEL
        and freeze.get("source") == {
            "path": PREFLIGHT_PRESERVER["source"][0],
            "sha256": PREFLIGHT_PRESERVER["source"][1],
        }
        and freeze.get("protocol") == {
            "path": PREFLIGHT_PRESERVER["protocol"][0],
            "sha256": PREFLIGHT_PRESERVER["protocol"][1],
        },
        "authenticate the immutable actual first-failure preservation freeze",
    )
    compressed, archive_owner = read_owner(
        *PREFLIGHT_ARCHIVE[:2], exact_size=PREFLIGHT_ARCHIVE[2],
        owner_only=True,
    )
    require(
        compressed[:10] == b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff",
        "require the actual preserved single-member zero-mtime failure gzip",
    )
    try:
        expanded = gzip.decompress(compressed)
    except (OSError, EOFError, ValueError) as error:
        raise CampaignError(
            "reject an incomplete original first-attempt failure archive"
        ) from error
    require(
        len(expanded) == PREFLIGHT_UNCOMPRESSED_BYTES
        and sha256(expanded) == PREFLIGHT_UNCOMPRESSED_SHA256,
        "authenticate every real canonical first-attempt failure byte",
    )
    failure = strict_document(
        expanded, "complete actual first-attempt infrastructure failure")
    require(
        failure.get("schema")
        == "rebar-owned-zig-campaign-preflight-failure-v1"
           "-actual-preserved-infrastructure-failure"
        and failure.get("version") == 1
        and failure.get("status") == "FAIL"
        and failure.get("failure_class")
        == "PRE-ACTIVATION INFRASTRUCTURE FAILURE"
        and failure.get("family") == FAMILY
        and failure.get("label") == LABEL
        and failure.get("suite_count") == SUITE_COUNT
        and failure.get("case_execution_denominator") == CASE_COUNT
        and failure.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and failure.get("completed_suite_count") == 0
        and failure.get("actual_candidate_workers") == 0
        and failure.get("actual_matching_case_execution_count") == 0
        and failure.get("semantic_mismatch_count") == "NOT MEASURED"
        and failure.get("candidate_correctness") == "NOT MEASURED"
        and failure.get("candidate_qualified") is False
        and failure.get("native_target_activation_occurred") is False
        and failure.get("native_target_restoration_required") is False
        and failure.get("original_native_targets_unchanged") is True
        and failure.get("archive_published_only_after_original_targets_verified")
        is True
        and failure.get("preservation_source_sha256")
        == PREFLIGHT_PRESERVER["source"][1]
        and failure.get("preservation_protocol_sha256")
        == PREFLIGHT_PRESERVER["protocol"][1]
        and failure.get("preservation_contract_sha256")
        == PREFLIGHT_PRESERVER["contract"][1]
        and failure.get("actual_c_candidate_workers") == 13
        and failure.get("actual_c_semantic_mismatch_count") == 1262
        and failure.get("actual_c_verified_passing_case_count") == 7325
        and failure.get("actual_rust_build_process_count") == 28
        and failure.get("actual_zig_build_process_count") == 26
        and failure.get("hidden_cases_read") == 0
        and failure.get("benchmark_files_read") == 0
        and failure.get("clock_samples") == 0
        and failure.get("timing_trials_run") == 0
        and failure.get("holdout") == "NOT OPENED",
        "preserve the genuine failed first attempt without inventing matching",
    )
    controller = failure.get("actual_once_only_controller")
    require(
        type(controller) is dict
        and controller.get("exit_status") == 1
        and controller.get("process_id") == "NOT RECORDED"
        and controller.get("process_id_recorded") is False
        and controller.get("exception_type") == "ActivationError"
        and type(controller.get("argv")) is list
        and controller["argv"][:4] == [
            PYTHON, "-I", "-B", FAILED_CAMPAIGN["source"][0],
        ]
        and "--run" in controller["argv"],
        "preserve the exact once-only failed V1 controller without fake PID",
    )
    stdout = controller.get("stdout")
    stderr = controller.get("stderr")
    require(
        type(stdout) is dict
        and stdout.get("bytes") == 0
        and stdout.get("sha256") == EMPTY_SHA256
        and stdout.get("base64") == ""
        and type(stderr) is dict
        and stderr.get("bytes") == PREFLIGHT_STDERR_BYTES
        and stderr.get("sha256") == PREFLIGHT_STDERR_SHA256
        and stderr.get("complete") is True
        and type(stderr.get("base64")) is str,
        "retain the actual complete parent-captured first-attempt streams",
    )
    try:
        decoded_stderr = base64.b64decode(
            stderr["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise CampaignError(
            "reject truncated or fabricated first-attempt stderr"
        ) from error
    require(
        len(decoded_stderr) == PREFLIGHT_STDERR_BYTES
        and sha256(decoded_stderr) == PREFLIGHT_STDERR_SHA256,
        "verify all actual first-attempt traceback bytes",
    )
    frames = controller.get("traceback_frames")
    expected_frames = (
        (FAILED_CAMPAIGN["source"][0], "<module>", 1811),
        (FAILED_CAMPAIGN["source"][0], "main", 1796),
        (FAILED_CAMPAIGN["source"][0], "run_campaign", 1525),
        (FAILED_CAMPAIGN["source"][0], "exact_originals", 1366),
        (ACTIVATION["source"][0], "exact_current_original", 1429),
        (ACTIVATION["source"][0], "require", 271),
    )
    require(
        type(frames) is list and len(frames) == len(expected_frames)
        and all(
            type(row) is dict
            and (row.get("path"), row.get("function"), row.get("line"))
            == expected
            for row, expected in zip(frames, expected_frames, strict=True)
        ),
        "retain all six exact genuine failed V1 traceback frames",
    )
    historical = failure.get("original_campaign")
    require(
        type(historical) is dict
        and all(
            historical.get(role) == owner_record(definition)
            for role, definition in FAILED_CAMPAIGN.items()
        ),
        "bind the failed run to the exact original immutable V1 triple",
    )
    cause = failure.get("root_cause")
    require(
        type(cause) is dict
        and cause.get("status") == "PASS"
        and cause.get("traceback_frame_count") == 6
        and cause.get("actual_canonical_target_reads") == 0
        and cause.get("actual_canonical_target_stats") == 0
        and cause.get("v6_missing_required_owner_fields") == ["nlink", "uid"]
        and type(cause.get("roles")) is dict
        and set(cause["roles"]) == {"engine", "bridge"}
        and all(
            type(row) is dict
            and row.get("actual_canonical_target_inspected") is False
            and row.get("actual_mature_shape_matches") is False
            and row.get("normalized_shape_matches") is True
            and row.get("missing_fields") == ["nlink", "uid"]
            for row in cause["roles"].values()
        ),
        "preserve the proven owner-shape failure without inspecting targets",
    )
    receipt_raw, receipt_owner = read_owner(
        *PREFLIGHT_RECEIPT[:2], exact_size=PREFLIGHT_RECEIPT[2],
        owner_only=True,
    )
    receipt = strict_document(
        receipt_raw, "separate actual failure-publication-only receipt")
    require(
        receipt.get("schema")
        == "rebar-owned-zig-campaign-preflight-failure-v1"
           "-durable-publication-receipt"
        and receipt.get("version") == 1
        and receipt.get("status") == "PASS"
        and receipt.get("preserved_failure_status") == "FAIL"
        and receipt.get("failure_class")
        == "PRE-ACTIVATION INFRASTRUCTURE FAILURE"
        and receipt.get("family") == FAMILY
        and receipt.get("label") == LABEL
        and receipt.get("uncompressed_sha256")
        == PREFLIGHT_UNCOMPRESSED_SHA256
        and receipt.get("uncompressed_bytes") == PREFLIGHT_UNCOMPRESSED_BYTES
        and receipt.get("actual_observed_controller_run_count") == 1
        and receipt.get("actual_observed_controller_exit_status") == 1
        and receipt.get("actual_observed_controller_process_id")
        == "NOT RECORDED"
        and receipt.get("actual_observed_stdout_sha256") == EMPTY_SHA256
        and receipt.get("actual_observed_stderr_sha256")
        == PREFLIGHT_STDERR_SHA256
        and receipt.get("actual_candidate_workers") == 0
        and receipt.get("actual_matching_case_execution_count") == 0
        and receipt.get("semantic_mismatch_count") == "NOT MEASURED"
        and receipt.get("candidate_correctness") == "NOT MEASURED"
        and receipt.get("actual_native_activations") == 0
        and receipt.get("original_native_targets_unchanged") is True
        and receipt.get("new_repository_evidence_owner_count") == 2
        and receipt.get("source_sha256") == PREFLIGHT_PRESERVER["source"][1]
        and receipt.get("protocol_sha256") == PREFLIGHT_PRESERVER["protocol"][1]
        and receipt.get("contract_sha256") == PREFLIGHT_PRESERVER["contract"][1]
        and reference_matches(
            receipt.get("archive"), PREFLIGHT_ARCHIVE, archive_owner)
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("benchmark_files_read") == 0
        and receipt.get("clock_samples") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("holdout") == "NOT OPENED"
        and (
            archive_owner["device"], archive_owner["inode"]
        ) != (
            receipt_owner["device"], receipt_owner["inode"]
        ),
        "a passing preservation receipt authenticates a FAILURE, not Zig",
    )
    return {
        "failure": failure,
        "receipt": receipt,
        "archive_owner": archive_owner,
        "receipt_owner": receipt_owner,
        "traceback_frame_count": len(frames),
    }


def authenticate_current_history(
    preserved: dict[str, Any],
) -> dict[str, Any]:
    observed: dict[str, dict[str, Any]] = {}
    raw: dict[str, bytes] = {}
    for role, definition in V26.items():
        payload, owner = read_owner(
            *definition[:2], exact_size=definition[2])
        observed[role] = owner
        raw[role] = payload
    inputs = strict_document(raw["inputs"], "actual published V26 inputs")
    summary = strict_document(raw["summary"], "actual published V26 summary")
    c = inputs.get("current_complete_c_campaign")
    rust = inputs.get("current_repaired_rust_source_build")
    zig = inputs.get("current_repaired_zig_source_build")
    first = inputs.get("preserved_zig_original_campaign_preflight_failure")
    snapshot = summary.get("snapshot")
    require(
        inputs.get("schema") == "rebar-candidate-current-overview-v26-inputs"
        and inputs.get("version") == 26
        and inputs.get("repository_evidence_owner_count")
        == CURRENT_EVIDENCE_OWNER_COUNT
        and inputs.get("all_digest_addressed_history_path_count")
        == CURRENT_REFERENCE_COUNT
        and inputs.get("suite_count") == SUITE_COUNT
        and inputs.get("full_case_denominator") == CASE_COUNT
        and inputs.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and inputs.get("candidate_qualified_count") == 0
        and inputs.get("final_holdout_opened") is False
        and inputs.get("actual_zig_candidate_workers") == 0
        and inputs.get("actual_zig_matching_case_execution_count") == 0
        and inputs.get("zig_matching_test_status") == "NOT MEASURED"
        and inputs.get("preserved_v25_repository_evidence_owner_count")
        == 139
        and inputs.get("preserved_v25_digest_addressed_history_path_count")
        == 144
        and inputs.get("new_zig_preflight_failure_repository_evidence_owner_count")
        == 2
        and inputs.get("renderer") == owner_record(V26["renderer"])
        and inputs.get("preserved_zig_preflight_failure_source_freeze")
        == mapped_owners(PREFLIGHT_PRESERVER)
        and inputs.get("performance") == "NOT MEASURED"
        and inputs.get("memory") == "NOT MEASURED"
        and inputs.get("winner_selected") is False,
        "authenticate only the literally released current V26 141/146 inputs",
    )
    require(
        type(c) is dict
        and c.get("status") == "FAIL"
        and c.get("actual_candidate_workers") == 13
        and c.get("semantic_mismatch_count") == 1262
        and c.get("verified_passing_case_count") == 7325
        and c.get("infrastructure_failure_count") == 0
        and type(rust) is dict
        and rust.get("status") == "PASS"
        and rust.get("actual_build_process_count") == 28
        and rust.get("actual_public_source_apply_count") == 2
        and rust.get("actual_bridge_source_apply_count") == 2
        and type(zig) is dict
        and zig.get("status") == "PASS"
        and zig.get("actual_build_process_count") == 26
        and zig.get("actual_source_apply_count") == 2,
        "retain actual 13-worker C losses and genuine Rust/Zig source builds",
    )
    require(
        type(first) is dict
        and first.get("schema")
        == "rebar-candidate-current-overview-v26"
           "-authenticated-zig-preflight-failure"
        and first.get("status") == "FAIL"
        and first.get("failure_class")
        == "PRE-ACTIVATION INFRASTRUCTURE FAILURE"
        and first.get("actual_candidate_workers") == 0
        and first.get("actual_matching_case_execution_count") == 0
        and first.get("semantic_mismatch_count") == "NOT MEASURED"
        and first.get("candidate_correctness") == "NOT MEASURED"
        and first.get("original_native_targets_unchanged") is True
        and first.get("holdout") == "NOT OPENED"
        and reference_matches(
            first.get("archive"), PREFLIGHT_ARCHIVE,
            preserved["archive_owner"])
        and reference_matches(
            first.get("receipt"), PREFLIGHT_RECEIPT,
            preserved["receipt_owner"]),
        "retain the exact published failed attempt and both independent owners",
    )
    require(
        summary.get("schema") == "rebar-candidate-current-overview-v26-summary"
        and summary.get("status") == "PASS"
        and summary.get("repository_evidence_owner_count")
        == CURRENT_EVIDENCE_OWNER_COUNT
        and summary.get("authenticated_digest_addressed_history_paths")
        == CURRENT_REFERENCE_COUNT
        and summary.get("full_case_denominator") == CASE_COUNT
        and summary.get("suite_count") == SUITE_COUNT
        and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
        and summary.get("qualified_candidate_count") == 0
        and summary.get("clock_samples") == 0
        and summary.get("timing_trials_run") == 0
        and summary.get("performance") == "NOT MEASURED"
        and summary.get("memory") == "NOT MEASURED"
        and summary.get("final_holdout_opened") is False
        and summary.get("source") == owner_record(V26["renderer"])
        and summary.get("inputs") == owner_record(V26["inputs"])
        and summary.get("svg") == owner_record(V26["svg"])
        and summary.get("preserved_v25_repository_evidence_owner_count") == 139
        and summary.get("preserved_v25_authenticated_reference_path_count")
        == 144
        and summary.get("c_repaired_candidate_worker_count") == 13
        and summary.get("c_repaired_semantic_mismatch_count") == 1262
        and summary.get("c_repaired_verified_passing_case_count") == 7325
        and summary.get("c_repaired_infrastructure_failure_count") == 0
        and summary.get("rust_dual_overlay_repaired_build_process_count") == 28
        and summary.get("rust_dual_overlay_repaired_public_source_apply_count")
        == 2
        and summary.get("rust_dual_overlay_repaired_bridge_source_apply_count")
        == 2
        and summary.get("zig_scanner_repaired_build_process_count") == 26
        and summary.get("zig_original_campaign_attempt_count") == 1
        and summary.get("zig_original_campaign_candidate_worker_count") == 0
        and summary.get("zig_original_campaign_controller_exit_status") == 1
        and summary.get("zig_original_campaign_controller_process_id")
        == "NOT RECORDED"
        and summary.get("zig_original_campaign_failure_class")
        == "PRE-ACTIVATION INFRASTRUCTURE FAILURE"
        and summary.get("zig_original_campaign_matching_case_execution_count")
        == 0
        and summary.get("zig_original_campaign_matching_test_status")
        == "NOT MEASURED"
        and summary.get("zig_original_campaign_original_targets_unchanged")
        is True
        and summary.get("zig_original_campaign_semantic_mismatch_count")
        == "NOT MEASURED"
        and summary.get("winner_selected") is False
        and type(snapshot) is dict
        and snapshot.get("current_source_owner_count") == 25
        and snapshot.get("all_actual_candidate_and_native_evidence_owner_count")
        == CURRENT_EVIDENCE_OWNER_COUNT
        and snapshot.get("all_digest_addressed_history_path_count")
        == CURRENT_REFERENCE_COUNT
        and snapshot.get("baseline_status") == "PASS"
        and snapshot.get("baseline_passed") == CASE_COUNT
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("actual_candidate_imports") == 0
        and snapshot.get("actual_candidate_processes_started") == 0
        and snapshot.get("final_holdout_opened") is False,
        "never present old V25 139/144 as current published evidence",
    )
    summary_first = summary.get("zig_original_campaign_preflight_failure")
    require(
        type(summary_first) is dict
        and summary_first.get("schema") == first["schema"]
        and summary_first.get("status") == "FAIL"
        and summary_first.get("failure_class") == first["failure_class"]
        and summary_first.get("actual_candidate_workers") == 0
        and summary_first.get("actual_matching_case_execution_count") == 0
        and summary_first.get("candidate_correctness") == "NOT MEASURED"
        and summary_first.get("holdout") == "NOT OPENED"
        and reference_matches(
            summary_first.get("archive"), PREFLIGHT_ARCHIVE,
            preserved["archive_owner"])
        and reference_matches(
            summary_first.get("receipt"), PREFLIGHT_RECEIPT,
            preserved["receipt_owner"]),
        "bind the summary to the actual failed first-run archive and receipt",
    )
    return {
        "inputs": inputs,
        "summary": summary,
        "owners": observed,
        "first": first,
    }

def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None, *,
                   retain: bool = False
                   ) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_runtime()
    checked_digest(source_pin, "campaign source")
    checked_digest(protocol_pin, "campaign protocol")
    _, own_source = read_owner(SOURCE_RELATIVE, source_pin)
    _, own_protocol = read_owner(PROTOCOL_RELATIVE, protocol_pin)
    normalized = load_frozen(
        NORMALIZED_ACTIVATION["source"], "v7_normalized_activation")
    require(
        normalized.SCHEMA == "rebar-phase2-verified-native-activation-v7"
        and normalized.FAMILY == FAMILY
        and normalized.BUILD_LABEL == BUILD_LABEL
        and isinstance(getattr(normalized, "ActivationError", None), type)
        and issubclass(normalized.ActivationError, Exception)
        and not issubclass(KeyboardInterrupt, Exception)
        and not issubclass(SystemExit, Exception)
        and all(
            callable(getattr(normalized, name, None))
            for name in ("verify_context", "parse_arguments", "activate", "recover")
        ),
        "load only the actual frozen V7 normalized two-role Zig activation",
    )
    for role in ("protocol", "contract"):
        read_owner(
            *NORMALIZED_ACTIVATION[role][:2],
            exact_size=NORMALIZED_ACTIVATION[role][2],
        )
    normalized_context, normalized_retained = normalized.verify_context(
        NORMALIZED_ACTIVATION["source"][1],
        NORMALIZED_ACTIVATION["protocol"][1],
        NORMALIZED_ACTIVATION["contract"][1],
        retain=True,
    )
    require(
        normalized_context.get("schema")
        == normalized.SCHEMA + "-read-only-frozen-context"
        and normalized_context.get("status") == "PASS"
        and normalized_context.get("version") == 7
        and normalized_context.get("family") == FAMILY
        and normalized_context.get("suite_count") == SUITE_COUNT
        and normalized_context.get("case_execution_denominator") == CASE_COUNT
        and normalized_context.get("named_private_waiver_count")
        == PRIVATE_WAIVER_COUNT
        and normalized_context.get("mature_original_owner_field_count") == 7
        and normalized_context.get("normalized_owner_field_count") == 9
        and normalized_context.get("owner_shape_defect_proven_without_target_access")
        is True
        and normalized_context.get("uid_and_nlink_fabricated") is False
        and normalized_context.get("actual_first_v1_attempt_status") == "FAIL"
        and normalized_context.get("actual_first_v1_candidate_workers") == 0
        and normalized_context.get("actual_first_v1_candidate_matching")
        == "NOT MEASURED"
        and normalized_context.get("canonical_target_reads") == 0
        and normalized_context.get("canonical_target_stats") == 0
        and normalized_context.get("canonical_target_links") == 0
        and normalized_context.get("canonical_target_replacements") == 0
        and normalized_context.get("source_freeze_original_targets_read") == 0
        and normalized_context.get("source_freeze_original_targets_statted") == 0
        and normalized_context.get("source_freeze_original_targets_modified") == 0
        and normalized_context.get("group_atomic") is False
        and normalized_context.get("holdout") == "NOT OPENED",
        "require real descriptor-bound UID/nlink normalization without target access",
    )
    activation = normalized_retained["v6"]
    retained_v6 = normalized_retained["inherited"]
    v6 = normalized_retained["v6_context"]
    mature = retained_v6["mature"]
    require(
        activation.SCHEMA == "rebar-phase2-verified-native-activation-v6"
        and activation.FAMILY == FAMILY
        and activation.BUILD_LABEL == BUILD_LABEL
        and tuple(activation.ROLE_ORDER) == ("engine", "bridge")
        and tuple(activation.RESTORATION_ORDER) == ("bridge", "engine")
        and callable(mature.read_owned)
        and v6.get("status") == "PASS"
        and v6.get("family") == FAMILY
        and v6.get("published_v25_evidence_owner_count") == 139
        and v6.get("published_v25_authenticated_reference_count") == 144
        and v6.get("zig_build_historical_evidence_owner_count") == 135
        and v6.get("zig_build_historical_reference_count") == 140
        and v6.get("actual_zig_build_process_count") == 26
        and v6.get("actual_rust_build_process_count") == 28
        and v6.get("actual_c_semantic_mismatch_count") == 1262
        and v6.get("actual_c_candidate_worker_count") == 13
        and v6.get("actual_c_verified_passing_case_executions") == 7325
        and v6.get("native_role_count") == 2
        and v6.get("source_freeze_original_targets_read") == 0
        and v6.get("source_freeze_original_targets_statted") == 0
        and v6.get("source_freeze_original_targets_modified") == 0
        and v6.get("canonical_target_reads") == 0
        and v6.get("canonical_target_stats") == 0
        and v6.get("canonical_target_links") == 0
        and v6.get("canonical_target_replacements") == 0
        and v6.get("group_atomic") is False
        and v6.get("holdout") == "NOT OPENED",
        "preserve genuine historical-only V6/V25 provenance under V7 normalization",
    )
    preserved_failure = authenticate_preserved_failure()
    current_history = authenticate_current_history(preserved_failure)

    producer = load_frozen(PRODUCER["source"], "original_v3_producer")
    for role in ("protocol", "contract"):
        read_owner(*PRODUCER[role][:2], exact_size=PRODUCER[role][2])
    producer_raw, _ = read_owner(*PRODUCER["contract"][:2],
                                exact_size=PRODUCER["contract"][2])
    original = strict_document(producer_raw, "complete original V3 contract")
    require(original.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v3-source-freeze"
            and original.get("version") == 3
            and original.get("suite_count") == 13
            and original.get("case_execution_denominator") == 31237
            and original.get("family_count") == 6
            and original.get("source_owner_count") == 25
            and type(original.get("suites")) is list
            and len(original["suites"]) == 13
            and tuple((x.get("id"), x.get("case_execution_count"))
                      for x in original["suites"]) == SUITES
            and all(callable(getattr(producer, name, None)) for name in (
                "family_spec", "suite_spec", "parse_source_owners",
                "native_pins", "exact_native_owners", "chosen_six_family_guard",
                "observe_original_upstream", "observe_direct_suite",
                "observe_subinterpreters",
            )), "preserve every literal unchanged original V3 observer")
    lifecycle = original.get("successful_nested_lifecycle")
    require(type(lifecycle) is dict
            and lifecycle.get("counted_case_count") == 128
            and lifecycle.get("actual_case_interpreter_exec_calls") == 394
            and lifecycle.get("actual_interpreters_created") == 11
            and lifecycle.get("actual_interpreters_destroyed") == 11
            and lifecycle.get("actual_initialization_interpreter_exec_calls") == 11
            and lifecycle.get("actual_guard_cleanup_interpreter_exec_calls") == 11
            and lifecycle.get("actual_fresh_temporary_interpreters") == 8,
            "preserve the actual original complete 128/394/11 lifecycle")
    phase_raw, _ = read_owner(*PHASE_ONE[:2], exact_size=PHASE_ONE[2])
    phase = strict_document(phase_raw, "unchanged original P0 matrix")
    activation.validate_phase_one(phase)
    phase_rows = phase.get("suites")
    require(type(phase_rows) is list and len(phase_rows) == 13,
            "retain all thirteen genuine phase-one suites")
    suite_owners: list[dict[str, Any]] = []
    for (name, count), first, second in zip(
            SUITES, original["suites"], phase_rows, strict=True):
        require(type(first) is dict and type(second) is dict
                and first.get("id") == second.get("id") == name
                and first.get("case_execution_count")
                == second.get("case_execution_count") == count
                and first.get("matrix_sha256") == second.get("matrix_sha256")
                and first.get("reference_records_sha256")
                == second.get("baseline_records_sha256")
                and type(second.get("source")) is dict
                and first.get("source_relative")
                == second["source"].get("path")
                and first.get("source_sha256")
                == second["source"].get("sha256"),
                "refuse changed, omitted or reordered original group: " + name)
        _, suite_owner = read_owner(first["source_relative"],
                                    first["source_sha256"])
        suite_owners.append(suite_owner)
    zig = producer.family_spec(FAMILY)
    require(zig.name == FAMILY
            and zig.module == "candidates.zig_candidate"
            and zig.bridge_module == "candidates._zig_bridge"
            and zig.engine_relative == "candidates/_zig_probe.so"
            and zig.bridge_relative
            == "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so"
            and zig.combined_native is False and zig.owned_ctypes is True
            and tuple(zig.source_owners) == SOURCE_OWNERS
            and tuple((x.name, x.case_count) for x in producer.SUITES)
            == SUITES
            and tuple(producer.BRIDGE_METHOD_PROFILES[FAMILY])
            == ("compile", "initialize_pattern", "free", "collect"),
            "freeze only the genuine original independent Zig bridge profile")
    families = [x for x in original.get("families", [])
                if type(x) is dict and x.get("family") == FAMILY]
    require(len(families) == 1
            and families[0].get("owned_ctypes_allowed") is True
            and families[0].get("combined_native_engine_and_bridge") is False
            and families[0].get("owned_source_count") == 3
            and [(x.get("relative"), x.get("sha256"), x.get("size_bytes"))
                 for x in families[0].get("sources", [])]
            == list(SOURCE_OWNERS),
            "reject borrowed, omitted or cross-family semantic sources")
    for relative, digest, size in SOURCE_OWNERS:
        read_owner(relative, digest, exact_size=size)
    publication = load_frozen(PUBLICATION["source"], "v2_publication_only")
    for role in ("protocol", "contract"):
        read_owner(*PUBLICATION[role][:2], exact_size=PUBLICATION[role][2])
    public_raw, _ = read_owner(*PUBLICATION["contract"][:2],
                               exact_size=PUBLICATION["contract"][2])
    previous = strict_document(public_raw, "frozen V2 publication-only contract")
    require(previous.get("schema")
            == "rebar-owned-six-family-original-p0-campaign-v2-source-freeze"
            and previous.get("version") == 2
            and previous.get("suite_count") == 13
            and previous.get("case_execution_denominator") == 31237
            and publication.SCHEMA
            == "rebar-owned-six-family-original-p0-campaign-v2"
            and all(callable(getattr(publication, name, None))
                    for name in ("stream_canonical_gzip", "verify_gzip_chunks",
                                 "open_evidence_directory",
                                 "write_streamed_archive")),
            "reuse V2 only for independently verified lossless publication")
    frozen_owner = None
    if contract_pin is not None:
        checked_digest(contract_pin, "campaign machine contract")
        raw, frozen_owner = read_owner(CONTRACT_RELATIVE, contract_pin)
        validate_contract(strict_document(raw, "complete Zig V2 contract"),
                          source_pin, protocol_pin)
    require(not any(x == "candidates" or x.startswith("candidates.")
                    for x in sys.modules),
            "source verification must never import an actual candidate")
    result = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS", "version": 2, "family": FAMILY,
        "mode": "READ-ONLY ORIGINAL ZIG SOURCE FREEZE",
        "campaign_label": LABEL, "source": own_source,
        "protocol": own_protocol, "contract": frozen_owner,
        "suite_count": 13, "case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "unchanged_original_suite_source_owner_count": len(suite_owners),
        "published_v26_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
        "published_v26_authenticated_reference_count": CURRENT_REFERENCE_COUNT,
        "historical_v25_evidence_owner_count": 139,
        "historical_v25_authenticated_reference_count": 144,
        "published_v26_renderer": owner_record(V26["renderer"]),
        "published_v26_inputs": owner_record(V26["inputs"]),
        "published_v26_summary": owner_record(V26["summary"]),
        "published_v26_svg": owner_record(V26["svg"]),
        "actual_first_v1_attempt_status": "FAIL",
        "actual_first_v1_failure_class":
            "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "actual_first_v1_controller_runs": 1,
        "actual_first_v1_controller_exit_status": 1,
        "actual_first_v1_controller_process_id": "NOT RECORDED",
        "actual_first_v1_candidate_workers": 0,
        "actual_first_v1_matching_case_execution_count": 0,
        "actual_first_v1_candidate_correctness": "NOT MEASURED",
        "actual_first_v1_failure_archive": owner_record(PREFLIGHT_ARCHIVE),
        "actual_first_v1_failure_receipt": owner_record(PREFLIGHT_RECEIPT),
        "actual_first_v1_receipt_status": "PASS",
        "actual_first_v1_receipt_preserved_failure_status": "FAIL",
        "actual_first_v1_receipt_pass_means":
            "DURABLE FAILURE PUBLICATION ONLY",
        "actual_first_v1_traceback_frame_count": 6,
        "normalized_activation_version": 7,
        "inherited_private_journal_version": 6,
        "normalized_verify_context_errors_caught": True,
        "normalized_activation_errors_caught": True,
        "normalized_recovery_errors_caught": True,
        "normalized_error_exit_status": 1,
        "keyboard_interrupt_not_caught": True,
        "system_exit_not_caught": True,
        "owner_shape_defect_proven_without_target_access": True,
        "uid_and_nlink_fabricated": False,
        "zig_build_historical_evidence_owner_count": 135,
        "zig_build_historical_reference_count": 140,
        "actual_zig_build_process_count": 26,
        "actual_rust_build_process_count": 28,
        "actual_c_semantic_mismatch_count": 1262,
        "actual_c_candidate_worker_count": 13,
        "actual_c_verified_passing_case_count": 7325,
        "native_role_count": 2, "original_zig_source_owner_count": 3,
        "actual_zig_source_repair_application_count": 2,
        "actual_rust_public_source_repair_count": 2,
        "actual_rust_bridge_source_repair_count": 2,
        "upstream_public_record_count": 152,
        "upstream_runnable_public_case_count": 151,
        "upstream_debug_skip_count": 1,
        "nested_case_count": 128,
        "nested_case_interpreter_event_count": 394,
        "nested_interpreters_created": 11,
        "nested_interpreters_destroyed": 11,
        "owned_zig_ctypes_only": True,
        "v3_legacy_activation_dispatch_invoked": False,
        "v2_cpp_or_go_matching_invoked": False,
        "group_atomic": False, "restoration_order": ["bridge", "engine"],
        **source_effects(),
    }
    kept = {
        "activation": activation,
        "normalized_activation": normalized,
        "normalized_activation_context": normalized_context,
        "normalized_activation_retained": normalized_retained,
        "v6_context": v6,
        "activation_retained": retained_v6,
        "preserved_failure": preserved_failure,
        "current_v26_history": current_history,
        "producer": producer, "producer_contract": original,
        "publication": publication, "phase": phase,
    } if retain else {}
    return result, kept

def assert_actual_authorization(options: argparse.Namespace) -> None:
    require(
        options.family == FAMILY
        and checked_label(options.label) == LABEL
        and options.activation_source_sha256 == ACTIVATION["source"][1]
        and options.activation_protocol_sha256 == ACTIVATION["protocol"][1]
        and options.activation_contract_sha256 == ACTIVATION["contract"][1]
        and options.normalized_activation_source_sha256
        == NORMALIZED_ACTIVATION["source"][1]
        and options.normalized_activation_protocol_sha256
        == NORMALIZED_ACTIVATION["protocol"][1]
        and options.normalized_activation_contract_sha256
        == NORMALIZED_ACTIVATION["contract"][1]
        and options.failure_preserver_source_sha256
        == PREFLIGHT_PRESERVER["source"][1]
        and options.failure_preserver_protocol_sha256
        == PREFLIGHT_PRESERVER["protocol"][1]
        and options.failure_preserver_contract_sha256
        == PREFLIGHT_PRESERVER["contract"][1]
        and options.failure_archive_sha256 == PREFLIGHT_ARCHIVE[1]
        and options.failure_receipt_sha256 == PREFLIGHT_RECEIPT[1]
        and options.overview_renderer_sha256 == V26["renderer"][1]
        and options.overview_inputs_sha256 == V26["inputs"][1]
        and options.overview_summary_sha256 == V26["summary"][1]
        and options.overview_svg_sha256 == V26["svg"][1]
        and options.producer_source_sha256 == PRODUCER["source"][1]
        and options.producer_protocol_sha256 == PRODUCER["protocol"][1]
        and options.producer_contract_sha256 == PRODUCER["contract"][1]
        and options.publication_source_sha256 == PUBLICATION["source"][1]
        and options.publication_protocol_sha256 == PUBLICATION["protocol"][1]
        and options.publication_contract_sha256 == PUBLICATION["contract"][1]
        and options.build_archive_sha256 == BUILD_ARCHIVE[1]
        and options.build_receipt_sha256 == BUILD_RECEIPT[1]
        and options.native_engine_sha256 == ENGINE_SHA256
        and options.native_bridge_sha256 == BRIDGE_SHA256
        and options.native_engine_bytes == ENGINE_BYTES
        and options.native_bridge_bytes == BRIDGE_BYTES,
        "independently caller-pin real V7, inherited V6, V26, genuine first "
        "failure, original V3, V11 and both first-party native roles",
    )

def same_private_owner(expected: Any, actual: dict[str, Any]) -> bool:
    return (type(expected) is dict
            and expected.get("sha256") == actual.get("sha256")
            and expected.get("device") == actual.get("device")
            and expected.get("inode") == actual.get("inode")
            and expected.get("size_bytes") == actual.get("size_bytes"))


def active_worker_approval(options: argparse.Namespace,
                           kept: dict[str, Any]) -> dict[str, Any]:
    activation = kept["activation"]
    mature = kept["activation_retained"]["mature"]
    root = activation.checked_private_root(options.activation_root)
    raw_report, report_owner = mature.read_owned(
        root, "activation-report.json", options.activation_report_sha256,
        maximum=activation.MAX_REPORT_BYTES, private=True)
    raw_receipt, receipt_owner = mature.read_owned(
        root, "activation-receipt.json", options.activation_receipt_sha256,
        maximum=activation.MAX_REPORT_BYTES, private=True)
    raw_journal, journal_owner = mature.read_owned(
        root, "recovery-journal.json", options.recovery_journal_sha256,
        maximum=activation.MAX_REPORT_BYTES, private=True)
    report = activation.strict_json(raw_report, "actual V6 activation report")
    receipt = activation.strict_json(raw_receipt, "actual V6 activation receipt")
    journal = activation.strict_json(raw_journal, "actual V6 recovery journal")
    require(report.get("schema") == activation.REPORT_SCHEMA
            and report.get("status") == "PASS"
            and report.get("family") == FAMILY
            and report.get("activation_root") == root
            and report.get("build_label") == BUILD_LABEL
            and report.get("build_archive_sha256") == BUILD_ARCHIVE[1]
            and report.get("build_receipt_sha256") == BUILD_RECEIPT[1]
            and report.get("group_atomic") is False
            and report.get("exact_original_inode_backups_retained") is True
            and same_private_owner(report.get("recovery_journal"), journal_owner)
            and receipt.get("schema") == activation.RECEIPT_SCHEMA
            and receipt.get("status") == "PASS"
            and receipt.get("activation_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("activation_root") == root
            and receipt.get("group_atomic") is False
            and same_private_owner(receipt.get("activation_report"), report_owner)
            and same_private_owner(receipt.get("recovery_journal"), journal_owner)
            and journal.get("schema") == activation.JOURNAL_SCHEMA
            and journal.get("status") == "PREPARED"
            and journal.get("family") == FAMILY
            and journal.get("activation_root") == root
            and journal.get("build_label") == BUILD_LABEL
            and journal.get("activation_source_sha256") == ACTIVATION["source"][1]
            and journal.get("activation_protocol_sha256")
            == ACTIVATION["protocol"][1]
            and journal.get("activation_contract_sha256")
            == ACTIVATION["contract"][1]
            and journal.get("build_archive_sha256") == BUILD_ARCHIVE[1]
            and journal.get("build_receipt_sha256") == BUILD_RECEIPT[1]
            and journal.get("role_order") == ["engine", "bridge"]
            and journal.get("restoration_order") == ["bridge", "engine"]
            and journal.get("group_atomic") is False,
            "reject stale, incomplete, crossed or fabricated V6 activation")
    for role in ("engine", "bridge"):
        definition = activation.NATIVE_ROLES[role]
        row = journal.get("roles", {}).get(role)
        selected = report.get("canonical_targets", {}).get(role)
        require(type(row) is dict and row.get("role") == role
                and row.get("relative") == definition["relative"]
                and row.get("original") == definition["original"]
                and row.get("native_sha256") == definition["sha256"]
                and row.get("native_bytes") == definition["bytes"]
                and type(selected) is dict
                and selected.get("relative") == definition["relative"]
                and selected.get("sha256") == definition["sha256"]
                and selected.get("size_bytes") == definition["bytes"],
                "authenticate the exact real active native role: " + role)
    return {"root": root, "report": report, "report_owner": report_owner,
            "receipt": receipt, "receipt_owner": receipt_owner,
            "journal": journal, "journal_owner": journal_owner}


def worker_failure(name: str, error: BaseException) -> dict[str, Any]:
    extra = getattr(error, "details", None)
    return {
        "schema": WORKER_SCHEMA, "status": "FAIL", "candidate_family": FAMILY,
        "label": LABEL, "suite": name,
        "case_execution_denominator": dict(SUITES).get(name),
        "failure_class": "INFRASTRUCTURE FAILURE", "mismatch_count": 0,
        "error_type": type(error).__qualname__,
        "error_message": bounded_error(error),
        "traceback": traceback.format_exception(
            type(error), error, error.__traceback__),
        "complete_original_failure_details":
            copy.deepcopy(extra) if type(extra) is dict else None,
        "actual_candidate_workers": 1,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "candidate_qualified": False,
        "winner_selected": False,
    }


def run_worker(options: argparse.Namespace) -> dict[str, Any]:
    assert_actual_authorization(options)
    context, kept = verify_context(options.source_sha256,
                                   options.protocol_sha256,
                                   options.contract_sha256, retain=True)
    require(context["status"] == "PASS", "authenticate the full frozen campaign")
    approval = active_worker_approval(options, kept)
    producer = kept["producer"]
    spec = producer.family_spec(FAMILY)
    suite = producer.suite_spec(options.suite)
    require(suite.name == options.suite
            and suite.case_count == dict(SUITES)[options.suite],
            "select exactly one original frozen group")
    sources = {path: digest for path, digest, _ in SOURCE_OWNERS}
    pins = {"source": SOURCE_OWNERS[0][1],
            "native_engine": ENGINE_SHA256,
            "native_bridge": BRIDGE_SHA256}
    exact = producer.exact_native_owners(spec, pins, sources)
    require(exact["source"]["sha256"] == SOURCE_OWNERS[0][1]
            and exact["native_engine"]["sha256"] == ENGINE_SHA256
            and exact["native_bridge"]["sha256"] == BRIDGE_SHA256,
            "allow only the actual independently source-built native Zig roles")
    if suite.name == "original_bounded_v5":
        observed = producer.observe_original_upstream(
            suite, spec, pins, sources)
    elif suite.name == "subinterpreter_v2":
        observed = producer.observe_subinterpreters(
            suite, spec, pins, sources,
            producer_sha256=PRODUCER["source"][1])
    else:
        observed = producer.observe_direct_suite(
            suite, spec, pins, sources, kept["phase"])
    require(type(observed) is dict
            and observed.get("schema")
            == producer.SCHEMA + "-actual-original-suite"
            and observed.get("status") in ("PASS", "FAIL")
            and observed.get("suite") == suite.name
            and observed.get("candidate_family") == FAMILY
            and observed.get("case_execution_denominator") == suite.case_count
            and observed.get("actual_candidate_case_count") == suite.case_count
            and type(observed.get("mismatch_count")) is int
            and observed["mismatch_count"] >= 0
            and type(observed.get("all_mismatches")) is list
            and len(observed["all_mismatches"]) == observed["mismatch_count"]
            and observed.get("actual_candidate_workers") == 1
            and observed.get("hidden_cases_read") == 0
            and observed.get("benchmark_files_read") == 0
            and observed.get("clock_samples") == 0
            and observed.get("timing_trials_run") == 0
            and observed.get("holdout") == "NOT OPENED",
            "retain all complete unchanged genuine original observations")
    if suite.name == "original_bounded_v5":
        require(observed.get("actual_public_record_count") == 152
                and observed.get("actual_debug_skip_count") == 1
                and observed.get("named_private_waiver_count") == 13
                and type(observed.get("named_private_waivers")) is list
                and len(observed["named_private_waivers"]) == 13,
                "never suppress original public methods or private waivers")
    if suite.name == "subinterpreter_v2" and observed["status"] == "PASS":
        require(observed.get("actual_case_interpreter_exec_calls") == 394
                and observed.get("actual_interpreters_created") == 11
                and observed.get("actual_interpreters_destroyed") == 11
                and observed.get("actual_initialization_interpreter_exec_calls") == 11
                and observed.get("actual_guard_cleanup_interpreter_exec_calls") == 11
                and observed.get("all_real_pipes_read_to_eof") is True
                and observed.get("all_real_pipe_descriptors_closed") is True
                and observed.get("interpreter_live_set_restored") is True
                and observed.get("locale_restored") is True,
                "retain all real original interpreter and pipe events")
    return {
        "schema": WORKER_SCHEMA, "status": observed["status"],
        "candidate_family": FAMILY, "label": LABEL, "suite": suite.name,
        "case_execution_denominator": suite.case_count,
        "mismatch_count": observed["mismatch_count"],
        "failure_class":
            "PASS" if observed["status"] == "PASS" else "SEMANTIC MISMATCH",
        "original_observer_source_sha256": PRODUCER["source"][1],
        "original_observer_protocol_sha256": PRODUCER["protocol"][1],
        "original_observer_contract_sha256": PRODUCER["contract"][1],
        "original_v3_observer_unchanged": True,
        "v3_legacy_activation_dispatch_invoked": False,
        "actual_v7_normalized_activation_source_sha256":
            NORMALIZED_ACTIVATION["source"][1],
        "actual_v7_normalized_activation_protocol_sha256":
            NORMALIZED_ACTIVATION["protocol"][1],
        "actual_v7_normalized_activation_contract_sha256":
            NORMALIZED_ACTIVATION["contract"][1],
        "inherited_private_journal_version": 6,
        "published_v26_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
        "published_v26_authenticated_reference_count": CURRENT_REFERENCE_COUNT,
        "actual_first_v1_attempt_status": "FAIL",
        "actual_first_v1_candidate_workers": 0,
        "actual_first_v1_matching_case_execution_count": 0,

        "actual_v6_activation_source_sha256": ACTIVATION["source"][1],
        "actual_v6_activation_report_sha256": approval["report_owner"]["sha256"],
        "actual_v6_activation_receipt_sha256": approval["receipt_owner"]["sha256"],
        "actual_v6_recovery_journal_sha256": approval["journal_owner"]["sha256"],
        "actual_v11_build_archive_sha256": BUILD_ARCHIVE[1],
        "actual_v11_build_receipt_sha256": BUILD_RECEIPT[1],
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
        "complete_original_observation": observed,
        "all_original_records_and_mismatches_preserved": True,
        "actual_candidate_workers": 1,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "candidate_qualified": False,
        "winner_selected": False,
    }

def publication_names(label: str, *, failure: bool) -> tuple[str, str]:
    require(checked_label(label) == LABEL and type(failure) is bool,
            "authorize only one genuine frozen original Zig evidence label")
    base = "repaired-zig-original-campaign-v2-zig-" + label
    if failure:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def ensure_fresh_publication(publication: types.ModuleType,
                             label: str) -> None:
    directory = publication.open_evidence_directory()
    try:
        for failed in (False, True):
            for name in publication_names(label, failure=failed):
                try:
                    os.stat(name, dir_fd=directory, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise CampaignError(
                    "never reuse or overwrite historical evidence: " + name)
    finally:
        os.close(directory)


def worker_arguments(options: argparse.Namespace, name: str,
                     active: dict[str, Any]) -> list[str]:
    return [
        PYTHON, "-I", "-B", str(ROOT / SOURCE_RELATIVE), "--worker",
        "--source-sha256", options.source_sha256,
        "--protocol-sha256", options.protocol_sha256,
        "--contract-sha256", options.contract_sha256,
        "--family", FAMILY, "--label", LABEL, "--suite", name,
        "--normalized-activation-source-sha256", NORMALIZED_ACTIVATION["source"][1],
        "--normalized-activation-protocol-sha256", NORMALIZED_ACTIVATION["protocol"][1],
        "--normalized-activation-contract-sha256", NORMALIZED_ACTIVATION["contract"][1],
        "--failure-preserver-source-sha256", PREFLIGHT_PRESERVER["source"][1],
        "--failure-preserver-protocol-sha256", PREFLIGHT_PRESERVER["protocol"][1],
        "--failure-preserver-contract-sha256", PREFLIGHT_PRESERVER["contract"][1],
        "--failure-archive-sha256", PREFLIGHT_ARCHIVE[1],
        "--failure-receipt-sha256", PREFLIGHT_RECEIPT[1],
        "--overview-renderer-sha256", V26["renderer"][1],
        "--overview-inputs-sha256", V26["inputs"][1],
        "--overview-summary-sha256", V26["summary"][1],
        "--overview-svg-sha256", V26["svg"][1],
        "--activation-source-sha256", ACTIVATION["source"][1],
        "--activation-protocol-sha256", ACTIVATION["protocol"][1],
        "--activation-contract-sha256", ACTIVATION["contract"][1],
        "--producer-source-sha256", PRODUCER["source"][1],
        "--producer-protocol-sha256", PRODUCER["protocol"][1],
        "--producer-contract-sha256", PRODUCER["contract"][1],
        "--publication-source-sha256", PUBLICATION["source"][1],
        "--publication-protocol-sha256", PUBLICATION["protocol"][1],
        "--publication-contract-sha256", PUBLICATION["contract"][1],
        "--build-archive-sha256", BUILD_ARCHIVE[1],
        "--build-receipt-sha256", BUILD_RECEIPT[1],
        "--native-engine-sha256", ENGINE_SHA256,
        "--native-bridge-sha256", BRIDGE_SHA256,
        "--native-engine-bytes", str(ENGINE_BYTES),
        "--native-bridge-bytes", str(BRIDGE_BYTES),
        "--activation-root", active["activation_root"],
        "--activation-report-sha256", active["report"]["sha256"],
        "--activation-receipt-sha256", active["receipt"]["sha256"],
        "--recovery-journal-sha256", active["recovery_journal"]["sha256"],
    ]

def encoded_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes, "retain only real complete process bytes")
    return {"base64": base64.b64encode(raw).decode("ascii"),
            "bytes": len(raw), "sha256": sha256(raw), "complete": True}


def execute_one_worker(options: argparse.Namespace, name: str,
                       count: int, active: dict[str, Any]) -> dict[str, Any]:
    argv = worker_arguments(options, name, active)
    child = subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timed_out = False
    try:
        stdout, stderr = child.communicate(timeout=WORKER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        child.kill()
        stdout, stderr = child.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes
            and len(stdout) <= MAX_STDOUT_BYTES
            and len(stderr) <= MAX_STDERR_BYTES,
            "retain complete bounded genuine worker stdout and stderr")
    process = {
        "argv": argv, "pid": child.pid, "returncode": child.returncode,
        "timed_out": timed_out, "stdout": encoded_stream(stdout),
        "stderr": encoded_stream(stderr), "actual_worker_processes": 1,
    }
    document = None
    decoding_error = None
    try:
        document = strict_document(stdout, "complete actual original worker")
    except BaseException as error:
        decoding_error = {"error_type": type(error).__qualname__,
                          "error_message": bounded_error(error)}
    complete = (
        type(document) is dict and document.get("schema") == WORKER_SCHEMA
        and document.get("candidate_family") == FAMILY
        and document.get("label") == LABEL and document.get("suite") == name
        and document.get("case_execution_denominator") == count
        and document.get("original_observer_source_sha256")
        == PRODUCER["source"][1]
        and document.get("actual_v6_activation_source_sha256")
        == ACTIVATION["source"][1]
        and document.get("actual_v7_normalized_activation_source_sha256")
        == NORMALIZED_ACTIVATION["source"][1]
        and document.get("actual_v7_normalized_activation_protocol_sha256")
        == NORMALIZED_ACTIVATION["protocol"][1]
        and document.get("actual_v7_normalized_activation_contract_sha256")
        == NORMALIZED_ACTIVATION["contract"][1]
        and document.get("inherited_private_journal_version") == 6
        and document.get("published_v26_evidence_owner_count")
        == CURRENT_EVIDENCE_OWNER_COUNT
        and document.get("published_v26_authenticated_reference_count")
        == CURRENT_REFERENCE_COUNT
        and document.get("actual_first_v1_attempt_status") == "FAIL"
        and document.get("actual_first_v1_candidate_workers") == 0
        and document.get("actual_first_v1_matching_case_execution_count") == 0

        and document.get("native_engine_sha256") == ENGINE_SHA256
        and document.get("native_bridge_sha256") == BRIDGE_SHA256
        and document.get("all_original_records_and_mismatches_preserved") is True
        and document.get("actual_candidate_workers") == 1
        and document.get("clock_samples") == 0
        and document.get("holdout") == "NOT OPENED"
        and document.get("status") in ("PASS", "FAIL")
        and type(document.get("mismatch_count")) is int
        and document["mismatch_count"] >= 0 and timed_out is False
        and child.returncode == (0 if document["status"] == "PASS" else 1)
    )
    if complete:
        return {
            "suite": name, "status": document["status"],
            "case_execution_denominator": count,
            "failure_class": document["failure_class"],
            "mismatch_count": document["mismatch_count"],
            "actual_worker_started": True, "actual_worker_processes": 1,
            "all_original_records_and_mismatches_preserved": True,
            "original_observer": document, "process": process,
        }
    return {
        "suite": name, "status": "FAIL",
        "case_execution_denominator": count,
        "failure_class": "INFRASTRUCTURE FAILURE", "mismatch_count": 0,
        "actual_worker_started": True, "actual_worker_processes": 1,
        "all_original_records_and_mismatches_preserved": False,
        "worker_decoding_error": decoding_error,
        "original_worker_output": document, "process": process,
    }

def failed_worker(name: str, count: int,
                  error: BaseException) -> dict[str, Any]:
    return {
        "suite": name, "status": "FAIL",
        "case_execution_denominator": count,
        "failure_class": "INFRASTRUCTURE FAILURE", "mismatch_count": 0,
        "actual_worker_started": False, "actual_worker_processes": 0,
        "all_original_records_and_mismatches_preserved": False,
        "error_type": type(error).__qualname__,
        "error_message": bounded_error(error),
        "traceback": traceback.format_exception(
            type(error), error, error.__traceback__),
        "process": None,
    }


def activation_arguments() -> list[str]:
    return [
        "--activate",
        "--source-sha256", NORMALIZED_ACTIVATION["source"][1],
        "--protocol-sha256", NORMALIZED_ACTIVATION["protocol"][1],
        "--contract-sha256", NORMALIZED_ACTIVATION["contract"][1],
        "--predecessor-source-sha256", ACTIVATION["source"][1],
        "--predecessor-protocol-sha256", ACTIVATION["protocol"][1],
        "--predecessor-contract-sha256", ACTIVATION["contract"][1],
        "--family", FAMILY,
        "--build-label", BUILD_LABEL,
        "--build-archive-sha256", BUILD_ARCHIVE[1],
        "--build-receipt-sha256", BUILD_RECEIPT[1],
        "--native-engine-sha256", ENGINE_SHA256,
        "--native-bridge-sha256", BRIDGE_SHA256,
        "--native-engine-bytes", str(ENGINE_BYTES),
        "--native-bridge-bytes", str(BRIDGE_BYTES),
    ]

def recovery_arguments(root: str, journal: str) -> list[str]:
    return [
        "--recover",
        "--source-sha256", NORMALIZED_ACTIVATION["source"][1],
        "--protocol-sha256", NORMALIZED_ACTIVATION["protocol"][1],
        "--contract-sha256", NORMALIZED_ACTIVATION["contract"][1],
        "--predecessor-source-sha256", ACTIVATION["source"][1],
        "--predecessor-protocol-sha256", ACTIVATION["protocol"][1],
        "--predecessor-contract-sha256", ACTIVATION["contract"][1],
        "--family", FAMILY,
        "--activation-root", root,
        "--recovery-journal-sha256", journal,
    ]

def private_roots(activation: types.ModuleType) -> set[str]:
    result: set[str] = set()
    with os.scandir("/tmp") as rows:
        for row in rows:
            if not row.name.startswith(activation.PRIVATE_PREFIX):
                continue
            if not row.is_dir(follow_symlinks=False):
                continue
            full = activation.checked_private_root("/tmp/" + row.name)
            owner = row.stat(follow_symlinks=False)
            if (stat.S_ISDIR(owner.st_mode)
                    and stat.S_IMODE(owner.st_mode) == 0o700
                    and owner.st_uid == os.geteuid()):
                result.add(full)
    return result


def discover_journal(activation: types.ModuleType, mature: types.ModuleType,
                     previous: set[str], actual: dict[str, Any] | None
                     ) -> tuple[str, dict[str, Any], dict[str, Any]] | None:
    fresh = private_roots(activation) - previous
    if type(actual) is dict:
        fresh.add(activation.checked_private_root(actual["activation_root"]))
    require(len(fresh) <= 1, "reject ambiguous concurrent V6 recovery roots")
    if not fresh:
        return None
    root = next(iter(fresh))
    try:
        raw, owner = mature.read_owned(
            root, "recovery-journal.json", None,
            maximum=activation.MAX_REPORT_BYTES, private=True)
    except FileNotFoundError:
        return None
    journal = activation.strict_json(raw, "actual Zig V6 recovery journal")
    require(journal.get("schema") == activation.JOURNAL_SCHEMA
            and journal.get("status") == "PREPARED"
            and journal.get("family") == FAMILY
            and journal.get("activation_root") == root
            and journal.get("activation_source_sha256") == ACTIVATION["source"][1]
            and journal.get("activation_protocol_sha256")
            == ACTIVATION["protocol"][1]
            and journal.get("activation_contract_sha256")
            == ACTIVATION["contract"][1]
            and journal.get("build_archive_sha256") == BUILD_ARCHIVE[1]
            and journal.get("build_receipt_sha256") == BUILD_RECEIPT[1]
            and journal.get("restoration_order") == ["bridge", "engine"]
            and journal.get("group_atomic") is False,
            "recover only one complete authentic dual-role journal")
    return root, owner, journal


def existing_restoration(activation: types.ModuleType,
                         mature: types.ModuleType,
                         root: str, journal: dict[str, Any]
                         ) -> dict[str, Any] | None:
    try:
        raw, owner = mature.read_owned(
            root, "restoration-receipt.json", None,
            maximum=activation.MAX_REPORT_BYTES, private=True)
    except FileNotFoundError:
        return None
    result = activation.strict_json(raw, "existing actual exact restoration")
    require(result.get("schema") == activation.RESTORATION_SCHEMA
            and result.get("status") == "PASS"
            and result.get("family") == FAMILY
            and result.get("activation_root") == root
            and result.get("recovery_journal_sha256") == journal["sha256"]
            and result.get("restoration_order") == ["bridge", "engine"]
            and result.get("original_inode_preserved") is True
            and result.get("group_atomic") is False
            and type(result.get("restored_targets")) is dict
            and set(result["restored_targets"]) == {"engine", "bridge"},
            "reject an altered or incomplete original-inode restoration")
    return {"route": "existing-authenticated-exact-inode-restoration",
            "owner": owner, "restoration": result}


def exact_originals(activation: types.ModuleType,
                    mature: types.ModuleType) -> dict[str, dict[str, Any]]:
    result = {}
    for role in ("engine", "bridge"):
        _, owner = activation.exact_current_original(mature, role)
        result[role] = owner
    require(result["engine"]["inode"] == 431260
            and result["bridge"]["inode"] == 431274
            and all(
                result[role]["device"]
                == activation.NATIVE_ROLES[role]["original"]["device"]
                and result[role]["mode"]
                == activation.NATIVE_ROLES[role]["original"]["mode"]
                and result[role]["nlink"] == 1
                and result[role]["uid"]
                == activation.NATIVE_ROLES[role]["original"]["uid"]
                and result[role]["sha256"]
                == activation.NATIVE_ROLES[role]["original"]["sha256"]
                for role in ("engine", "bridge")),
            "prove exact original device, inode, mode, uid, bytes and nlink")
    return result


def preserve_campaign(report: dict[str, Any],
                      kept: dict[str, Any]) -> dict[str, Any]:
    require(report.get("schema") == CAMPAIGN_SCHEMA
            and report.get("status") in ("PASS", "FAIL")
            and report.get("family") == FAMILY
            and report.get("label") == LABEL
            and report.get("suite_count") == SUITE_COUNT
            and report.get("case_execution_denominator") == CASE_COUNT
            and report.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and report.get("completed_suite_count") == SUITE_COUNT
            and type(report.get("suite_results")) is list
            and len(report["suite_results"]) == SUITE_COUNT
            and [(x.get("suite"), x.get("case_execution_denominator"))
                 for x in report["suite_results"]] == list(SUITES)
            and report.get("original_native_restored") is True
            and report.get("restoration_verified_before_publication") is True
            and report.get("clock_samples") == 0
            and report.get("holdout") == "NOT OPENED",
            "never publish incomplete observations or unrestored native files")
    activation = kept["activation"]
    mature = kept["activation_retained"]["mature"]
    publication = kept["publication"]
    originals = exact_originals(activation, mature)
    require(report.get("restored_original_targets") == originals,
            "prove both exact original inodes immediately before publication")
    name, receipt_name = publication_names(
        LABEL, failure=report["status"] == "FAIL")
    directory = publication.open_evidence_directory()
    try:
        archive, stream = publication.write_streamed_archive(
            report, name, directory)
    finally:
        os.close(directory)
    require(archive.get("relative") == name and archive.get("mode") == 0o600
            and archive.get("exclusive_creation") is True
            and archive.get("same_inode_readback_verified") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and archive.get("streaming_readback_verified") is True
            and stream.get("gzip_mtime") == 0
            and stream.get("gzip_single_member") is True
            and stream.get("canonical_terminal_newline_count") == 1,
            "require authentic exclusive complete V2 lossless streaming")
    receipt_document = {
        "schema": RECEIPT_SCHEMA, "status": "PASS",
        "candidate_status": report["status"], "family": FAMILY,
        "label": LABEL, "archive": archive,
        "campaign_source_sha256": report["campaign_source_sha256"],
        "campaign_protocol_sha256": report["campaign_protocol_sha256"],
        "campaign_contract_sha256": report["campaign_contract_sha256"],
        "original_v3_observer_source_sha256": PRODUCER["source"][1],
        "original_v3_observer_protocol_sha256": PRODUCER["protocol"][1],
        "original_v3_observer_contract_sha256": PRODUCER["contract"][1],
        "v7_normalized_activation_source_sha256":
            NORMALIZED_ACTIVATION["source"][1],
        "v7_normalized_activation_protocol_sha256":
            NORMALIZED_ACTIVATION["protocol"][1],
        "v7_normalized_activation_contract_sha256":
            NORMALIZED_ACTIVATION["contract"][1],
        "actual_first_v1_attempt_status": "FAIL",
        "actual_first_v1_candidate_workers": 0,
        "actual_first_v1_matching_case_execution_count": 0,
        "actual_first_v1_failure_archive": owner_record(PREFLIGHT_ARCHIVE),
        "actual_first_v1_failure_receipt": owner_record(PREFLIGHT_RECEIPT),
        "actual_first_v1_receipt_pass_means":
            "DURABLE FAILURE PUBLICATION ONLY",

        "v6_activation_source_sha256": ACTIVATION["source"][1],
        "v6_activation_protocol_sha256": ACTIVATION["protocol"][1],
        "v6_activation_contract_sha256": ACTIVATION["contract"][1],
        "actual_v11_build_archive_sha256": BUILD_ARCHIVE[1],
        "actual_v11_build_receipt_sha256": BUILD_RECEIPT[1],
        "uncompressed_sha256": stream["uncompressed_sha256"],
        "uncompressed_bytes": stream["uncompressed_bytes"],
        "uncompressed_chunk_count": stream["uncompressed_chunk_count"],
        "suite_count": SUITE_COUNT, "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "completed_suite_count": SUITE_COUNT,
        "actual_candidate_workers": report["actual_candidate_workers"],
        "verified_passing_case_count": report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "infrastructure_failure_count": report["infrastructure_failure_count"],
        "candidate_qualified": report["candidate_qualified"],
        "all_original_suite_streams_retained": True,
        "original_native_restored": True,
        "restored_original_targets": originals,
        "restoration_verified_before_publication": True,
        "group_atomic": False,
        "published_v26_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
        "published_v26_authenticated_reference_count": CURRENT_REFERENCE_COUNT,
        "historical_v25_evidence_owner_count": 139,
        "historical_v25_authenticated_reference_count": 144,
        "actual_c_semantic_mismatch_count": 1262,
        "actual_rust_compiler_process_count": 28,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    root = str(ROOT / EVIDENCE_RELATIVE)
    receipt = mature.write_fresh(root, receipt_name,
                                 canonical(receipt_document))
    synchronized = mature.synchronize_directory(root)
    require(receipt.get("relative") == receipt_name
            and receipt.get("mode") == 0o600
            and receipt.get("exclusive_creation") is True
            and receipt.get("same_inode_readback_verified") is True
            and receipt.get("file_fsync_completed") is True
            and synchronized.get("completed") is True
            and (archive["device"], archive["inode"])
            != (receipt["device"], receipt["inode"]),
            "publish exactly two separately durable owner-only evidence inodes")
    exact_originals(activation, mature)
    return {
        "schema": RESULT_SCHEMA, "status": report["status"],
        "family": FAMILY, "label": LABEL,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "completed_suite_count": SUITE_COUNT,
        "actual_candidate_workers": report["actual_candidate_workers"],
        "verified_passing_case_count": report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "infrastructure_failure_count": report["infrastructure_failure_count"],
        "candidate_qualified": report["candidate_qualified"],
        "all_original_suite_streams_retained": True,
        "archive": archive, "receipt": receipt,
        "uncompressed_sha256": stream["uncompressed_sha256"],
        "uncompressed_bytes": stream["uncompressed_bytes"],
        "original_native_restored": True,
        "restored_original_targets": originals,
        "restoration_verified_before_publication": True,
        "group_atomic": False,
        "published_v26_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
        "published_v26_authenticated_reference_count": CURRENT_REFERENCE_COUNT,
        "historical_v25_evidence_owner_count": 139,
        "historical_v25_authenticated_reference_count": 144,
        "actual_c_semantic_mismatch_count": 1262,
        "actual_rust_compiler_process_count": 28,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }

def run_campaign(options: argparse.Namespace) -> dict[str, Any]:
    assert_actual_authorization(options)
    context, kept = verify_context(options.source_sha256,
                                   options.protocol_sha256,
                                   options.contract_sha256, retain=True)
    require(context.get("status") == "PASS"
            and context.get("suite_count") == 13
            and context.get("case_execution_denominator") == 31237,
            "authenticate the full immutable original Zig campaign")
    activation = kept["activation"]
    normalized = kept["normalized_activation"]
    mature = kept["activation_retained"]["mature"]
    baseline: dict[str, dict[str, Any]] | None = None
    before: set[str] | None = None
    active: dict[str, Any] | None = None
    journal: tuple[str, dict[str, Any], dict[str, Any]] | None = None
    rows: list[dict[str, Any]] = []
    failure: dict[str, Any] | None = None
    restoration: dict[str, Any] | None = None
    originals: dict[str, dict[str, Any]] | None = None
    try:
        ensure_fresh_publication(kept["publication"], LABEL)
        baseline = exact_originals(activation, mature)
        before = private_roots(activation)
        active = normalized.activate(
            normalized.parse_arguments(activation_arguments()))
        require(type(active) is dict
                and active.get("schema")
                == normalized.SCHEMA + "-normalized-activation-result"
                and active.get("version") == 7
                and active.get("immutable_v6_predecessor_schema")
                == activation.SCHEMA + "-activation-result"
                and active.get("immutable_v6_predecessor_source_sha256")
                == ACTIVATION["source"][1]
                and active.get("status") == "PASS"
                and active.get("family") == FAMILY
                and active.get("group_atomic") is False
                and active.get("original_inodes_preserved_in_adjacent_backups")
                is True, "require actual V7-normalized durable two-native V6 activation")
        journal = discover_journal(activation, mature, before, active)
        require(journal is not None
                and same_private_owner(active.get("recovery_journal"),
                                       journal[1]),
                "preserve the exact authentic V6 hardlink recovery journal")
        for name, count in SUITES:
            try:
                row = execute_one_worker(options, name, count, active)
            except BaseException as error:
                row = failed_worker(name, count, error)
            rows.append(row)
    except BaseException as error:
        failure = {
            "error_type": type(error).__qualname__,
            "error_message": bounded_error(error),
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__),
        }
    finally:
        if journal is None and before is not None:
            journal = discover_journal(activation, mature, before, active)
        if journal is not None:
            root, owner, _ = journal
            restoration = existing_restoration(
                activation, mature, root, owner)
            if restoration is None:
                restored = normalized.recover(
                    normalized.parse_arguments(
                        recovery_arguments(root, owner["sha256"])))
                require(type(restored) is dict
                        and restored.get("schema")
                        == normalized.SCHEMA + "-normalized-recovery-result"
                        and restored.get("version") == 7
                        and restored.get("immutable_v6_predecessor_schema")
                        == activation.SCHEMA + "-recovery-result"
                        and restored.get("immutable_v6_predecessor_source_sha256")
                        == ACTIVATION["source"][1]
                        and restored.get("status") == "PASS"
                        and restored.get("family") == FAMILY
                        and restored.get("group_atomic") is False
                        and restored.get("original_inode_preserved") is True,
                        "restore both real original Zig inodes in outer finally")
                restoration = {
                    "route": "authenticated-reportless-exact-inode-recovery",
                    "result": restored,
                }
        if baseline is not None:
            originals = exact_originals(activation, mature)
            require(
                originals == baseline,
                "never publish before restoring both exact original user inodes",
            )
    if baseline is None:
        raise CampaignError(
            "V2 controller failed inside the protected preflight; "
            "no native activation or candidate matching is claimed"
            + (": " + failure["error_message"] if failure else "")
        )
    if active is None:
        raise CampaignError(
            "the actual Zig activation failed; exact originals are restored; "
            "matching remains NOT MEASURED"
            + (": " + failure["error_message"] if failure else ""))
    require(len(rows) == 13
            and [(x.get("suite"), x.get("case_execution_denominator"))
                 for x in rows] == list(SUITES),
            "run and retain all thirteen genuine original worker groups")
    pids = [x["process"]["pid"] for x in rows
            if x.get("actual_worker_started") is True
            and type(x.get("process")) is dict]
    require(len(pids) == len(set(pids)),
            "require independently observed distinct original worker processes")
    verified = sum(
        count for (name, count), row in zip(SUITES, rows, strict=True)
        if row.get("suite") == name and row.get("status") == "PASS"
        and row.get("failure_class") == "PASS"
        and row.get("mismatch_count") == 0
        and row.get("all_original_records_and_mismatches_preserved") is True)
    mismatches = sum(
        x["mismatch_count"] for x in rows
        if x.get("failure_class") == "SEMANTIC MISMATCH"
        and type(x.get("mismatch_count")) is int)
    infrastructure = sum(
        x.get("failure_class") == "INFRASTRUCTURE FAILURE"
        for x in rows) + int(failure is not None)
    qualified = (len(pids) == 13 and verified == 31237
                 and mismatches == 0 and infrastructure == 0
                 and all(x.get("status") == "PASS"
                         and x.get("actual_worker_processes") == 1
                         and x.get("all_original_records_and_mismatches_preserved")
                         is True for x in rows))
    report = {
        "schema": CAMPAIGN_SCHEMA,
        "status": "PASS" if qualified else "FAIL",
        "family": FAMILY, "label": LABEL,
        "campaign_source_sha256": options.source_sha256,
        "campaign_protocol_sha256": options.protocol_sha256,
        "campaign_contract_sha256": options.contract_sha256,
        "original_v3_producer_source_sha256": PRODUCER["source"][1],
        "original_v3_producer_protocol_sha256": PRODUCER["protocol"][1],
        "original_v3_producer_contract_sha256": PRODUCER["contract"][1],
        "v3_legacy_activation_dispatch_invoked": False,
        "v2_cpp_or_go_matching_invoked": False,
        "v7_normalized_activation_source_sha256":
            NORMALIZED_ACTIVATION["source"][1],
        "v7_normalized_activation_protocol_sha256":
            NORMALIZED_ACTIVATION["protocol"][1],
        "v7_normalized_activation_contract_sha256":
            NORMALIZED_ACTIVATION["contract"][1],
        "inherited_private_journal_version": 6,
        "actual_first_v1_attempt_status": "FAIL",
        "actual_first_v1_failure_class":
            "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "actual_first_v1_candidate_workers": 0,
        "actual_first_v1_matching_case_execution_count": 0,
        "actual_first_v1_failure_archive": owner_record(PREFLIGHT_ARCHIVE),
        "actual_first_v1_failure_receipt": owner_record(PREFLIGHT_RECEIPT),
        "actual_first_v1_receipt_pass_means":
            "DURABLE FAILURE PUBLICATION ONLY",

        "v6_activation_source_sha256": ACTIVATION["source"][1],
        "v6_activation_protocol_sha256": ACTIVATION["protocol"][1],
        "v6_activation_contract_sha256": ACTIVATION["contract"][1],
        "actual_v11_build_archive_sha256": BUILD_ARCHIVE[1],
        "actual_v11_build_receipt_sha256": BUILD_RECEIPT[1],
        "actual_zig_source_repair_application_count": 2,
        "actual_zig_compiler_process_count": 26,
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
        "native_engine_bytes": ENGINE_BYTES, "native_bridge_bytes": BRIDGE_BYTES,
        "derived_first_party_scanner_bridge_sha256": DERIVED_BRIDGE_SHA256,
        "suite_count": 13, "case_execution_denominator": 31237,
        "named_private_waiver_count": 13, "completed_suite_count": 13,
        "suite_results": rows, "actual_candidate_workers": len(pids),
        "actual_worker_process_ids": pids,
        "verified_passing_case_count": verified,
        "semantic_mismatch_count": mismatches,
        "infrastructure_failure_count": infrastructure,
        "candidate_qualified": qualified,
        "all_original_suite_streams_retained": True,
        "controller_failure": failure,
        "original_native_restored": True,
        "restored_original_targets": originals,
        "restoration": restoration,
        "restoration_verified_before_publication": True,
        "group_atomic": False,
        "published_v26_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
        "published_v26_authenticated_reference_count": CURRENT_REFERENCE_COUNT,
        "historical_v25_evidence_owner_count": 139,
        "historical_v25_authenticated_reference_count": 144,
        "actual_c_semantic_mismatch_count": 1262,
        "actual_c_candidate_workers": 13,
        "actual_rust_compiler_process_count": 28,
        "actual_rust_public_source_repairs": 2,
        "actual_rust_bridge_source_repairs": 2,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    return preserve_campaign(report, kept)

def parse_arguments(arguments: Sequence[str] | None = None
                    ) -> argparse.Namespace:
    values = list(sys.argv[1:] if arguments is None else arguments)
    require(all(type(x) is str for x in values),
            "require one complete literal original Zig campaign command")
    names = [x for x in values if x.startswith("--")]
    require(len(names) == len(set(names)),
            "reject duplicate or ambiguous candidate authorization")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--worker", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--family")
    parser.add_argument("--label")
    parser.add_argument("--suite", choices=tuple(x for x, _ in SUITES))
    parser.add_argument("--activation-root")
    for name in (
        "normalized-activation-source",
        "normalized-activation-protocol",
        "normalized-activation-contract",
        "failure-preserver-source",
        "failure-preserver-protocol",
        "failure-preserver-contract",
        "failure-archive",
        "failure-receipt",
        "overview-renderer",
        "overview-inputs",
        "overview-summary",
        "overview-svg",
        "activation-source", "activation-protocol", "activation-contract",
        "activation-report", "activation-receipt", "recovery-journal",
        "producer-source", "producer-protocol", "producer-contract",
        "publication-source", "publication-protocol", "publication-contract",
        "build-archive", "build-receipt", "native-engine", "native-bridge",
    ):
        parser.add_argument("--" + name + "-sha256")
    parser.add_argument("--native-engine-bytes", type=int)
    parser.add_argument("--native-bridge-bytes", type=int)
    options = parser.parse_args(values)
    checked_digest(options.source_sha256, "campaign source")
    checked_digest(options.protocol_sha256, "campaign protocol")
    digests = (
        "normalized_activation_source_sha256",
        "normalized_activation_protocol_sha256",
        "normalized_activation_contract_sha256",
        "failure_preserver_source_sha256",
        "failure_preserver_protocol_sha256",
        "failure_preserver_contract_sha256",
        "failure_archive_sha256",
        "failure_receipt_sha256",
        "overview_renderer_sha256",
        "overview_inputs_sha256",
        "overview_summary_sha256",
        "overview_svg_sha256",
        "contract_sha256", "activation_source_sha256",
        "activation_protocol_sha256", "activation_contract_sha256",
        "activation_report_sha256", "activation_receipt_sha256",
        "recovery_journal_sha256", "producer_source_sha256",
        "producer_protocol_sha256", "producer_contract_sha256",
        "publication_source_sha256", "publication_protocol_sha256",
        "publication_contract_sha256", "build_archive_sha256",
        "build_receipt_sha256", "native_engine_sha256",
        "native_bridge_sha256",
    )
    for name in digests:
        value = getattr(options, name)
        if value is not None:
            checked_digest(value, name)
    actual = (
        "normalized_activation_source_sha256",
        "normalized_activation_protocol_sha256",
        "normalized_activation_contract_sha256",
        "failure_preserver_source_sha256",
        "failure_preserver_protocol_sha256",
        "failure_preserver_contract_sha256",
        "failure_archive_sha256",
        "failure_receipt_sha256",
        "overview_renderer_sha256",
        "overview_inputs_sha256",
        "overview_summary_sha256",
        "overview_svg_sha256",
        "family", "label", "suite", "activation_root",
        "activation_source_sha256", "activation_protocol_sha256",
        "activation_contract_sha256", "activation_report_sha256",
        "activation_receipt_sha256", "recovery_journal_sha256",
        "producer_source_sha256", "producer_protocol_sha256",
        "producer_contract_sha256", "publication_source_sha256",
        "publication_protocol_sha256", "publication_contract_sha256",
        "build_archive_sha256", "build_receipt_sha256",
        "native_engine_sha256", "native_bridge_sha256",
        "native_engine_bytes", "native_bridge_bytes",
    )
    if options.render_contract:
        require(options.contract_sha256 is None
                and all(getattr(options, x) is None for x in actual),
                "contract rendering cannot inspect or activate a native target")
        return options
    require(options.contract_sha256 is not None,
            "independently pin the exact canonical original campaign contract")
    if options.self_test or options.verify_frozen_context:
        require(all(getattr(options, x) is None for x in actual),
                "source-only gates cannot authorize a candidate or native role")
        return options
    required = (
        "normalized_activation_source_sha256",
        "normalized_activation_protocol_sha256",
        "normalized_activation_contract_sha256",
        "failure_preserver_source_sha256",
        "failure_preserver_protocol_sha256",
        "failure_preserver_contract_sha256",
        "failure_archive_sha256",
        "failure_receipt_sha256",
        "overview_renderer_sha256",
        "overview_inputs_sha256",
        "overview_summary_sha256",
        "overview_svg_sha256",
        "family", "label", "activation_source_sha256",
        "activation_protocol_sha256", "activation_contract_sha256",
        "producer_source_sha256", "producer_protocol_sha256",
        "producer_contract_sha256", "publication_source_sha256",
        "publication_protocol_sha256", "publication_contract_sha256",
        "build_archive_sha256", "build_receipt_sha256",
        "native_engine_sha256", "native_bridge_sha256",
        "native_engine_bytes", "native_bridge_bytes",
    )
    require(all(getattr(options, x) is not None for x in required),
            "pin every original observer, activation, build and publication owner")
    assert_actual_authorization(options)
    if options.worker:
        require(all(getattr(options, x) is not None for x in (
            "suite", "activation_root", "activation_report_sha256",
            "activation_receipt_sha256", "recovery_journal_sha256")),
            "a real worker must authenticate one original group and the V7-normalized V6 journal")
    else:
        require(all(getattr(options, x) is None for x in (
            "suite", "activation_root", "activation_report_sha256",
            "activation_receipt_sha256", "recovery_journal_sha256")),
            "only the controller may create a fresh actual activation root")
    return options

def main(arguments: Sequence[str] | None = None) -> int:
    try:
        options = parse_arguments(arguments)
        if options.self_test:
            result = self_test(options.source_sha256,
                               options.protocol_sha256,
                               options.contract_sha256)
        elif options.verify_frozen_context:
            result, _ = verify_context(options.source_sha256,
                                       options.protocol_sha256,
                                       options.contract_sha256)
        elif options.render_contract:
            verify_context(options.source_sha256,
                           options.protocol_sha256, None)
            result = protocol_document(options.source_sha256,
                                       options.protocol_sha256)
        elif options.worker:
            try:
                result = run_worker(options)
            except BaseException as error:
                result = worker_failure(options.suite, error)
            sys.stdout.buffer.write(canonical(result))
            sys.stdout.buffer.flush()
            return 0 if result["status"] == "PASS" else 1
        else:
            result = run_campaign(options)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        if options.run:
            return 0 if result["status"] == "PASS" else 1
        return 0
    except Exception as error:
        sys.stderr.write("REPAIRED ORIGINAL ZIG CAMPAIGN V2: FAIL: "
                         + type(error).__name__ + ": "
                         + bounded_error(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
