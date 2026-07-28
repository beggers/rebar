#!/usr/bin/env python3
"""Freeze and later preserve one real Zig preflight failure without rerunning it."""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
import copy
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
import types


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/preserve_owned_zig_campaign_preflight_failure_v1.py"
PROTOCOL = "oracle/phase2/ZIG-CAMPAIGN-PREFLIGHT-FAILURE-V1.md"
CONTRACT = "oracle/phase2/zig-campaign-preflight-failure-v1.json"
SCHEMA = "rebar-owned-zig-campaign-preflight-failure-v1"
EVIDENCE = "oracle/phase2/evidence"
LABEL = "phase2-v11-zig-scanner-original-p0"
MAX_SOURCE = 8 * 1024 * 1024
MAX_REPORT = 8 * 1024 * 1024
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
CAMPAIGN = {
    "source": ("tools/run_owned_repaired_zig_original_campaign_v1.py",
               "ff4bc83173930c193de5984659aa6e8aca1848496d06f3d3dca3c28294c37c90", 92313),
    "protocol": ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V1.md",
                 "974c1cc09511c7a119a2ea0f59fab8c39e8d1887c948df19657de2458b5b9d67", 5108),
    "contract": ("oracle/phase2/repaired-zig-original-campaign-v1.json",
                 "f3f1bdfea41b8b4d5bce22b2b236c76f653e97268e500b951fbef262052718f0", 9563),
}
ACTIVATION = {
    "source": ("tools/activate_verified_native_candidate_v6.py",
               "d3a9b08c1bf7e3408719a0e92b8c1965aa6160dd2e18ab1501bb8662aaf8e4a1", 107982),
    "protocol": ("oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V6.md",
                 "0e736d575835fa22388841a527e22b62eef1ddf39eac9415bd7c518ba985b1d0", 6688),
    "contract": ("oracle/phase2/verified-native-activation-v6.json",
                 "e0d486cc6d621e963f8af5db1c4f7a47d590ad679837db1f53e11d05b670332e", 12902),
}
MATURE = {
    "source": ("tools/activate_verified_native_candidate_v2.py",
               "e6e8a72feffcf670da9a3e4d2e8b642e933c1d81cfe5bf7d1636385f207d6218", 205006),
    "protocol": ("oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V2.md",
                 "a675b411873c01ae88ea50d4f95aab7231a29dde38a458a947437f07ed850529", 10346),
}
PRODUCER = {
    "source": ("tools/run_owned_six_family_original_p0_producer_v3.py",
               "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c", 195555),
    "protocol": ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md",
                 "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76", 5522),
    "contract": ("oracle/phase2/six-family-p0-producer-v3.json",
                 "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1", 26909),
}
PUBLICATION = {
    "source": ("tools/run_owned_six_family_original_p0_campaign_v2.py",
               "6b06931ff64c5fe5b6bbbc3e970e56c0a94a24c28dfa6d3aa6140fc4d8fb54a1", 101836),
    "protocol": ("oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V2.md",
                 "e47cce8a6f60971bd3c18a4bfe248039ed9abd5b4144ec4355a77825a1435d4e", 4995),
    "contract": ("oracle/phase2/six-family-p0-campaign-v2.json",
                 "e44960e46c590cb5ab482ef323f3ae8598900f144b53a2377f62b3bb827935d7", 21314),
}
V25 = {
    "renderer": ("tools/render_candidate_current_overview_v25.py",
                 "9b1eabba4a3bd991c4359af4ab1482fe6f1ce848bb9e5df6fdd9e8bdafb21204", 98948),
    "inputs": ("docs/evidence/candidate-current-overview-v25.inputs.json",
               "123210219fac109506c03c2f76f89fda33aa5e08b0628fef43b9236d05bc1abe", 37281),
    "summary": ("docs/evidence/candidate-current-overview-v25.json",
                "8e4101c896e316190928d0710ca4442488c925ee5ef421507ba4dd08ff10a6d9", 144980),
    "svg": ("docs/evidence/candidate-current-overview-v25.svg",
            "db2f1a11e49fd58701ad89111aa422e619431eb9834d3fb5ae66deffcd75f0bb", 13188),
}
GOAL = ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
P0 = ("oracle/phase1/p0-completeness-v1.json",
      "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632)
ZIG_BUILD = {
    "archive": ("oracle/phase2/evidence/native-source-build-v11-zig-phase2-v11-zig-scanner.json.gz",
                "e4a1f369b647f588ac5b12585f7d0e30c4ee3409adc88f660081fb7a59a8df5c", 48246),
    "receipt": ("oracle/phase2/evidence/"
                "native-source-build-v11-zig-phase2-v11-zig-scanner-publication-receipt.json",
                "d53766d0dad571f8b72288cece15fb1ad0892db32c3b3b6b512027db94ca4fcc", 1683),
}
RUST_BUILD = {
    "archive": ("oracle/phase2/evidence/native-source-build-v11-rust-phase2-v11-rust-dual-overlay.json.gz",
                "282927f91fd885701dff6c431474f586afbc09460c6a20417ffa20be5a2e891c", 107639),
    "receipt": ("oracle/phase2/evidence/"
                "native-source-build-v11-rust-phase2-v11-rust-dual-overlay-publication-receipt.json",
                "4c75468663af0de60b37cdbabfca384c4e7f75e25a6155c2ff1c33f654d3f1d7", 1902),
}
ORIGINALS = {
    "engine": {
        "relative": "candidates/_zig_probe.so",
        "sha256": "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652",
        "bytes": 478432, "device": 2064, "inode": 431260,
        "mode": 0o700, "nlink": 1, "uid": 1000,
    },
    "bridge": {
        "relative": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "sha256": "d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b",
        "bytes": 134112, "device": 2064, "inode": 431274,
        "mode": 0o700, "nlink": 1, "uid": 1000,
    },
}
OBSERVED_STDERR = (
    "Traceback (most recent call last):\n"
    "  File \"/home/dev-user/src/rebar/tools/run_owned_repaired_zig_original_campaign_v1.py\", line 1811, in <module>\n"
    "    raise SystemExit(main())\n"
    "                     ~~~~^^\n"
    "  File \"/home/dev-user/src/rebar/tools/run_owned_repaired_zig_original_campaign_v1.py\", line 1796, in main\n"
    "    result = run_campaign(options)\n"
    "  File \"/home/dev-user/src/rebar/tools/run_owned_repaired_zig_original_campaign_v1.py\", line 1525, in run_campaign\n"
    "    baseline = exact_originals(activation, mature)\n"
    "  File \"/home/dev-user/src/rebar/tools/run_owned_repaired_zig_original_campaign_v1.py\", line 1366, in exact_originals\n"
    "    _, owner = activation.exact_current_original(mature, role)\n"
    "               ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^\n"
    "  File \"/home/dev-user/src/rebar/tools/activate_verified_native_candidate_v6.py\", line 1429, in exact_current_original\n"
    "    require(\n"
    "    ~~~~~~~^\n"
    "        mature_owner_matches(owner, definition[\"original\"]),\n"
    "        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
    "        \"refuse an absent, linked, altered, or substituted original Zig \"\n"
    "        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
    "        + role + \" inode\",\n"
    "        ^^^^^^^^^^^^^^^^^^\n"
    "    )\n"
    "    ^\n"
    "  File \"/home/dev-user/src/rebar/tools/activate_verified_native_candidate_v6.py\", line 271, in require\n"
    "    raise ActivationError(reason)\n"
    "_rebar_owned_zig_original_campaign_v1_v6_activation_d3a9b08c1bf7e3408719.ActivationError: refuse an absent, linked, altered, or substituted original Zig engine inode\n"
).encode("utf-8")
V2_OWNER_FIELDS = ("relative", "path", "sha256", "size_bytes", "device", "inode", "mode")
MISSING_OWNER_FIELDS = ("nlink", "uid")
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768), ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854), ("public_types_v1", 6912),
    ("substitution_v2", 5120), ("shape_v2", 10240),
    ("public_surface_v19", 1376), ("subinterpreter_v2", 128),
    ("pep688_v4", 264), ("threaded_pattern_v1", 512),
)
TRACEBACK_FRAMES = (
    ("tools/run_owned_repaired_zig_original_campaign_v1.py", 1811, "<module>"),
    ("tools/run_owned_repaired_zig_original_campaign_v1.py", 1796, "main"),
    ("tools/run_owned_repaired_zig_original_campaign_v1.py", 1525, "run_campaign"),
    ("tools/run_owned_repaired_zig_original_campaign_v1.py", 1366, "exact_originals"),
    ("tools/activate_verified_native_candidate_v6.py", 1429, "exact_current_original"),
    ("tools/activate_verified_native_candidate_v6.py", 271, "require"),
)


class PreservationError(Exception):
    """The real, once-only original preflight failure cannot be authenticated."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise PreservationError(message)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only actual complete evidence bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise PreservationError("reject malformed canonical failure evidence") from error


def checked_digest(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(part in "0123456789abcdef" for part in value),
         "require an independent exact SHA-256: " + label)
    return value


def runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
         and os.path.realpath(sys.executable) == PYTHON,
         "use only isolated, bytecode-free, pinned CPython 3.14.6")


def checked_relative(relative: object) -> tuple[str, ...]:
    need(type(relative) is str and 0 < len(relative) <= 512
         and "\\" not in relative and "\x00" not in relative,
         "require an exact nonescaped repository owner path")
    parsed = Path(relative)
    need(not parsed.is_absolute() and str(parsed) == relative
         and 0 < len(parsed.parts) <= 12
         and all(part not in ("", ".", "..") for part in parsed.parts),
         "reject a symlinked, escaped, or noncanonical owner path")
    return tuple(parsed.parts)


def pin(owner: tuple[str, str, int]) -> dict:
    checked_relative(owner[0])
    checked_digest(owner[1], owner[0])
    need(type(owner[2]) is int and 0 < owner[2] <= MAX_SOURCE,
         "require bounded exact owner bytes")
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2]}


def read_owner(relative: str, fingerprint: str, length: int,
               *, private: bool = False) -> tuple[bytes, dict]:
    parts = checked_relative(relative)
    checked_digest(fingerprint, relative)
    need(type(length) is int and 0 < length <= MAX_SOURCE,
         "require an exact bounded frozen owner length")
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
    descriptors: list[int] = []
    try:
        directory = os.open(str(ROOT), directory_flags)
        descriptors.append(directory)
        for part in parts[:-1]:
            directory = os.open(part, directory_flags, dir_fd=directory)
            descriptors.append(directory)
        descriptor = os.open(parts[-1], os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                             dir_fd=directory)
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=directory, follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode)
             and (before.st_dev, before.st_ino, before.st_size)
             == (named.st_dev, named.st_ino, named.st_size)
             and before.st_size == length and before.st_nlink == 1,
             "reject a changed, hardlinked, or symlinked exact owner: " + relative)
        if private:
            need(before.st_uid == os.geteuid()
                 and stat.S_IMODE(before.st_mode) == 0o600,
                 "require owner-only mode-0600 durable failure evidence")
        pieces: list[bytes] = []
        remaining = length
        while remaining:
            block = os.read(descriptor, min(remaining, 1024 * 1024))
            need(bool(block), "reject a truncated authenticated owner")
            pieces.append(block)
            remaining -= len(block)
        need(os.read(descriptor, 1) == b"", "reject hidden owner suffix bytes")
        after = os.fstat(descriptor)
        need((before.st_dev, before.st_ino, before.st_size,
              before.st_mtime_ns, before.st_ctime_ns)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns),
             "reject an authenticated owner changed during descriptor reading")
        raw = b"".join(pieces)
        need(digest(raw) == fingerprint, "reject substituted owner: " + relative)
        return raw, {
            "path": relative, "sha256": fingerprint, "bytes": length,
            "device": before.st_dev, "inode": before.st_ino,
            "mode": f"{stat.S_IMODE(before.st_mode):04o}",
            "nlink": before.st_nlink, "uid": before.st_uid,
        }
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def strict_document(raw: bytes, label: str) -> dict:
    try:
        def pairs(items: list[tuple[str, object]]) -> dict:
            result: dict[str, object] = {}
            for key, value in items:
                need(type(key) is str and key not in result,
                     "reject duplicate canonical evidence key: " + key)
                result[key] = value
            return result

        result = json.loads(raw.decode("ascii"), object_pairs_hook=pairs,
                            parse_constant=lambda item: (_ for _ in ()).throw(
                                PreservationError("reject nonfinite JSON: " + item)))
        need(type(result) is dict and canonical(result) == raw,
             "require exact canonical signed evidence: " + label)
        return result
    except (UnicodeError, ValueError, TypeError, RecursionError) as error:
        raise PreservationError("reject malformed evidence: " + label) from error


def observed_argv() -> list[str]:
    return [
        PYTHON, "-I", "-B", CAMPAIGN["source"][0], "--run",
        "--source-sha256", CAMPAIGN["source"][1],
        "--protocol-sha256", CAMPAIGN["protocol"][1],
        "--contract-sha256", CAMPAIGN["contract"][1],
        "--family", "zig", "--label", LABEL,
        "--activation-source-sha256", ACTIVATION["source"][1],
        "--activation-protocol-sha256", ACTIVATION["protocol"][1],
        "--activation-contract-sha256", ACTIVATION["contract"][1],
        "--producer-source-sha256", PRODUCER["source"][1],
        "--producer-protocol-sha256", PRODUCER["protocol"][1],
        "--producer-contract-sha256", PRODUCER["contract"][1],
        "--publication-source-sha256", PUBLICATION["source"][1],
        "--publication-protocol-sha256", PUBLICATION["protocol"][1],
        "--publication-contract-sha256", PUBLICATION["contract"][1],
        "--build-archive-sha256", ZIG_BUILD["archive"][1],
        "--build-receipt-sha256", ZIG_BUILD["receipt"][1],
        "--native-engine-sha256",
        "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071",
        "--native-bridge-sha256",
        "75032107c7769f24f0c80a6e473a26dad3c74f99290e3d89bf46767e07ec3681",
        "--native-engine-bytes", "108888",
        "--native-bridge-bytes", "133656",
    ]


def absent_campaign_names() -> tuple[str, ...]:
    stem = "repaired-zig-original-campaign-v1-zig-" + LABEL
    return (stem + ".json.gz", stem + "-publication-receipt.json",
            stem + "-failures.json.gz",
            stem + "-failures-publication-receipt.json")


def preservation_names() -> tuple[str, str]:
    stem = "zig-campaign-preflight-failure-v1-zig-" + LABEL + "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def zero_effects() -> dict:
    return {
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "actual_candidate_processes_started": 0,
        "actual_reference_workers": 0,
        "actual_native_activations": 0,
        "actual_native_recoveries": 0,
        "actual_native_libraries_loaded": 0,
        "actual_native_builds_started": 0,
        "actual_compiler_processes_started": 0,
        "actual_campaign_reruns": 0,
        "actual_network_requests": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "canonical_target_links": 0,
        "canonical_target_replacements": 0,
        "workspace_mutations": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def contract_document(source_pin: str, protocol_pin: str) -> dict:
    checked_digest(source_pin, "preflight failure preservation source")
    checked_digest(protocol_pin, "preflight failure preservation protocol")
    return {
        "schema": SCHEMA + "-source-freeze", "version": 1,
        "phase": "FROZEN ACTUAL ZIG PREFLIGHT FAILURE; PRESERVATION NOT RUN",
        "family": "zig", "label": LABEL,
        "source": {"path": SOURCE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL, "sha256": protocol_pin},
        "goal": pin(GOAL), "frozen_phase_one": pin(P0),
        "published_v25": {
            "owners": {name: pin(value) for name, value in sorted(V25.items())},
            "evidence_owner_count": 139,
            "authenticated_reference_count": 144,
            "qualified_candidate_count": 0,
            "actual_c_candidate_workers": 13,
            "actual_c_semantic_mismatches": 1262,
            "actual_c_verified_passing_case_count": 7325,
            "actual_rust_compiler_process_count": 28,
            "actual_rust_public_source_repairs": 2,
            "actual_rust_bridge_source_repairs": 2,
            "historical_rust_semantic_mismatches": 2042,
            "historical_zig_semantic_mismatches": 1764,
        },
        "original_campaign": {name: pin(value)
                               for name, value in sorted(CAMPAIGN.items())},
        "v6_activation": {name: pin(value)
                          for name, value in sorted(ACTIVATION.items())},
        "mature_v2_activation": {name: pin(value)
                                 for name, value in sorted(MATURE.items())},
        "original_v3_producer": {name: pin(value)
                                 for name, value in sorted(PRODUCER.items())},
        "v2_publication_primitives": {name: pin(value)
                                     for name, value in sorted(PUBLICATION.items())},
        "actual_zig_source_build": {
            "owners": {name: pin(value)
                       for name, value in sorted(ZIG_BUILD.items())},
            "actual_process_count": 26,
            "historical_evidence_owner_count_at_build": 135,
            "historical_authenticated_reference_count_at_build": 140,
            "engine_sha256": "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071",
            "engine_bytes": 108888,
            "bridge_sha256": "75032107c7769f24f0c80a6e473a26dad3c74f99290e3d89bf46767e07ec3681",
            "bridge_bytes": 133656,
            "candidate_correctness": "NOT MEASURED",
        },
        "actual_rust_source_build": {
            "owners": {name: pin(value)
                       for name, value in sorted(RUST_BUILD.items())},
            "actual_process_count": 28,
            "actual_public_source_repair_count": 2,
            "actual_bridge_source_repair_count": 2,
            "candidate_correctness": "NOT MEASURED",
        },
        "original_correctness": {
            "python": "3.14.6", "suite_count": 13,
            "case_execution_denominator": 31237,
            "private_waiver_count": 13,
            "suites": [{"id": name, "case_execution_count": count}
                       for name, count in SUITES],
        },
        "genuine_original_zig_targets": copy.deepcopy(ORIGINALS),
        "actual_captured_once_only_attempt": {
            "observation_provenance":
                "EXACT PARENT-CAPTURED ONCE-ONLY ORIGINAL CAMPAIGN PROCESS",
            "actual_controller_run_count": 1,
            "exit_status": 1,
            "process_id": "NOT RECORDED",
            "process_id_recorded": False,
            "argv": observed_argv(),
            "stdout_bytes": 0,
            "stdout_sha256": EMPTY_SHA256,
            "stdout_base64": "",
            "stderr_bytes": len(OBSERVED_STDERR),
            "stderr_sha256": digest(OBSERVED_STDERR),
            "stderr_base64": base64.b64encode(OBSERVED_STDERR).decode("ascii"),
            "stderr_utf8": OBSERVED_STDERR.decode("utf-8"),
            "traceback_frames": [
                {"path": path, "line": line, "function": function}
                for path, line, function in TRACEBACK_FRAMES
            ],
            "exception_type": "ActivationError",
            "exception_module":
                "_rebar_owned_zig_original_campaign_v1_v6_activation_d3a9b08c1bf7e3408719",
            "exception_message":
                "refuse an absent, linked, altered, or substituted original Zig engine inode",
            "failure_class": "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
            "actual_candidate_workers": 0,
            "actual_candidate_activations": 0,
            "actual_candidate_matching_cases": 0,
            "candidate_matching": "NOT MEASURED",
            "original_campaign_archive_created": False,
            "original_campaign_receipt_created": False,
        },
        "independently_reproducible_root_cause": {
            "mature_v2_function": "read_owned",
            "mature_v2_returned_owner_fields": list(V2_OWNER_FIELDS),
            "v6_function": "mature_owner_matches",
            "v6_requires_absent_fields": list(MISSING_OWNER_FIELDS),
            "both_synthetic_real_original_shapes_falsely_rejected": True,
            "both_synthetic_normalized_owner_shapes_accepted": True,
            "baseline_before_controller_try": True,
            "preservation_unreachable_from_original_controller": True,
            "canonical_target_mutation": False,
        },
        "original_campaign_result_names": [EVIDENCE + "/" + name
                                          for name in absent_campaign_names()],
        "future_preservation": {
            "explicit_preserve_required": True,
            "may_rerun_original_campaign": False,
            "may_activate_candidate": False,
            "read_exact_original_targets_only_in_explicit_preserve": True,
            "archive": EVIDENCE + "/" + preservation_names()[0],
            "receipt": EVIDENCE + "/" + preservation_names()[1],
            "new_actual_repository_evidence_owner_count": 2,
            "canonical_single_member_gzip_mtime": 0,
            "archive_exclusive_creation": True,
            "receipt_exclusive_creation": True,
            "file_fsync": True, "directory_fsync": True,
            "evidence_mode": "0600",
            "failure_status": "FAIL",
            "failure_is_not_a_candidate_result": True,
            "process_pid": "NOT RECORDED",
        },
        "source_only_effects": zero_effects(),
    }


def validate_contract(value: object, source_pin: str, protocol_pin: str) -> None:
    need(type(value) is dict
         and canonical(value) == canonical(contract_document(source_pin, protocol_pin)),
         "reject any changed actual traceback, root cause, history, or preservation boundary")


def load_module(pin_value: tuple[str, str, int], name: str) -> tuple[types.ModuleType, bytes]:
    raw, _ = read_owner(*pin_value)
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / pin_value[0])
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    return module, raw


def prove_root_cause(v2_raw: bytes, v1_raw: bytes,
                     activation: types.ModuleType) -> dict:
    mature_tree = ast.parse(v2_raw.decode("utf-8"), filename=MATURE["source"][0])
    function = next((node for node in mature_tree.body
                     if isinstance(node, ast.FunctionDef)
                     and node.name == "read_owned"), None)
    need(function is not None, "require the genuine immutable V2 owner reader")
    shapes = []
    for node in ast.walk(function):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Tuple):
            items = node.value.elts
            if len(items) == 2 and isinstance(items[1], ast.Dict):
                keys = []
                for key in items[1].keys:
                    need(isinstance(key, ast.Constant) and type(key.value) is str,
                         "require exact original V2 returned owner fields")
                    keys.append(key.value)
                shapes.append(tuple(keys))
    need(len(shapes) == 1 and set(shapes[0]) == set(V2_OWNER_FIELDS)
         and all(field not in shapes[0] for field in MISSING_OWNER_FIELDS),
         "independently prove mature V2 never returns nlink or uid")
    campaign_tree = ast.parse(v1_raw.decode("utf-8"),
                              filename=CAMPAIGN["source"][0])
    v6_raw, _ = read_owner(*ACTIVATION["source"])
    activation_tree = ast.parse(v6_raw.decode("utf-8"),
                                filename=ACTIVATION["source"][0])

    def has_call(tree: ast.AST, line: int, name: str) -> bool:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or node.lineno != line:
                continue
            function = node.func
            if isinstance(function, ast.Name) and function.id == name:
                return True
            if isinstance(function, ast.Attribute) and function.attr == name:
                return True
        return False

    need(has_call(campaign_tree, 1811, "main")
         and has_call(campaign_tree, 1796, "run_campaign")
         and has_call(campaign_tree, 1525, "exact_originals")
         and has_call(campaign_tree, 1366, "exact_current_original")
         and has_call(activation_tree, 1429, "require")
         and has_call(activation_tree, 271, "ActivationError"),
         "bind every parent-captured traceback frame to real unchanged source lines")
    rows = {}
    for role, expected in ORIGINALS.items():
        actual_expected = activation.NATIVE_ROLES[role]["original"]
        need(actual_expected == expected,
             "preserve every genuine original user-owned Zig identity: " + role)
        mature_owner = {
            "relative": expected["relative"],
            "path": str(ROOT / expected["relative"]),
            "sha256": expected["sha256"],
            "size_bytes": expected["bytes"],
            "device": expected["device"],
            "inode": expected["inode"],
            "mode": expected["mode"],
        }
        normalized = {**mature_owner, "nlink": expected["nlink"],
                      "uid": expected["uid"]}
        need(activation.mature_owner_matches(mature_owner, expected) is False
             and activation.mature_owner_matches(normalized, expected) is True,
             "prove the actual false original-owner rejection for " + role)
        rows[role] = {
            "original_device": expected["device"],
            "original_inode": expected["inode"],
            "original_sha256": expected["sha256"],
            "original_bytes": expected["bytes"],
            "original_mode": "0700",
            "mature_owner_fields": sorted(mature_owner),
            "missing_fields": list(MISSING_OWNER_FIELDS),
            "actual_mature_shape_matches": False,
            "normalized_shape_matches": True,
            "actual_canonical_target_inspected": False,
        }
    return {
        "status": "PASS",
        "v2_owner_fields": sorted(shapes[0]),
        "v6_missing_required_owner_fields": list(MISSING_OWNER_FIELDS),
        "traceback_frame_count": len(TRACEBACK_FRAMES),
        "roles": rows,
        "actual_canonical_target_reads": 0,
        "actual_canonical_target_stats": 0,
    }


def check_absent_original_campaign() -> list[dict]:
    folder = os.open(str(ROOT / EVIDENCE),
                     os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        result = []
        for name in absent_campaign_names():
            try:
                os.stat(name, dir_fd=folder, follow_symlinks=False)
            except FileNotFoundError:
                result.append({"path": EVIDENCE + "/" + name,
                               "status": "ABSENT"})
                continue
            raise PreservationError(
                "never invent or overwrite a genuine original Zig campaign result: " + name)
        return result
    finally:
        os.close(folder)


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str) -> dict:
    runtime()
    checked_digest(source_pin, "preflight source")
    checked_digest(protocol_pin, "preflight protocol")
    checked_digest(contract_pin, "preflight contract")
    source_raw, source_owner = read_owner(SOURCE, source_pin,
                                         os.stat(ROOT / SOURCE).st_size)
    need(bool(source_raw), "require the complete frozen preservation source")
    protocol_raw, protocol_owner = read_owner(
        PROTOCOL, protocol_pin, os.stat(ROOT / PROTOCOL).st_size)
    need(bool(protocol_raw), "require the complete frozen preflight protocol")
    frozen_raw, contract_owner = read_owner(
        CONTRACT, contract_pin, os.stat(ROOT / CONTRACT).st_size)
    validate_contract(strict_document(frozen_raw, "preflight failure contract"),
                      source_pin, protocol_pin)
    read_owner(*GOAL)
    phase_raw, _ = read_owner(*P0)
    phase = strict_document(phase_raw, "exact original CPython P0 matrix")
    need(phase.get("schema") == "rebar-cpython-re-p0-completeness-v1"
         and type(phase.get("suites")) is list
         and [(item.get("id"), item.get("case_execution_count"))
              for item in phase["suites"]] == list(SUITES)
         and sum(item["case_execution_count"] for item in phase["suites"]) == 31237,
         "preserve all thirteen genuine original Python case groups")
    for values in (CAMPAIGN, ACTIVATION, MATURE, PRODUCER, PUBLICATION,
                   V25, ZIG_BUILD, RUST_BUILD):
        for owner in values.values():
            read_owner(*owner)
    campaign, v1_raw = load_module(
        CAMPAIGN["source"], "_rebar_preflight_v1_exact_campaign_ff4bc831")
    context, kept = campaign.verify_context(
        CAMPAIGN["source"][1], CAMPAIGN["protocol"][1],
        CAMPAIGN["contract"][1], retain=True,
    )
    need(context.get("status") == "PASS"
         and context.get("published_v25_evidence_owner_count") == 139
         and context.get("published_v25_authenticated_reference_count") == 144
         and context.get("actual_zig_build_process_count") == 26
         and context.get("actual_rust_build_process_count") == 28
         and context.get("actual_rust_bridge_source_repair_count") == 2
         and context.get("actual_rust_public_source_repair_count") == 2
         and context.get("actual_c_candidate_worker_count") == 13
         and context.get("actual_c_semantic_mismatch_count") == 1262
         and context.get("actual_c_verified_passing_case_count") == 7325
         and context.get("suite_count") == 13
         and context.get("case_execution_denominator") == 31237
         and context.get("named_private_waiver_count") == 13
         and context.get("actual_candidate_workers") == 0
         and context.get("actual_native_activations") == 0
         and context.get("actual_subprocesses_started") == 0
         and context.get("canonical_target_reads") == 0
         and context.get("canonical_target_stats") == 0
         and context.get("canonical_target_links") == 0
         and context.get("canonical_target_replacements") == 0
         and context.get("performance") == "NOT MEASURED"
         and context.get("memory") == "NOT MEASURED"
         and context.get("holdout") == "NOT OPENED"
         and context.get("winner_selected") is False,
         "authenticate original V25, P0, real C/Rust/Zig and zero-target V1 freeze")
    activation = kept["activation"]
    mature = kept["activation_retained"]["mature"]
    need(activation.SCHEMA == "rebar-phase2-verified-native-activation-v6"
         and mature.SCHEMA == "rebar-phase2-verified-native-candidate-activation-v2",
         "load only the genuine frozen V6 activation and mature V2 primitive")
    v2_raw, _ = read_owner(*MATURE["source"])
    cause = prove_root_cause(v2_raw, v1_raw, activation)
    absent = check_absent_original_campaign()
    summary_raw, _ = read_owner(*V25["summary"])
    summary = strict_document(summary_raw, "exact V25 current result")
    need(summary.get("status") == "PASS"
         and summary.get("repository_evidence_owner_count") == 139
         and summary.get("authenticated_digest_addressed_history_paths") == 144
         and summary.get("qualified_candidate_count") == 0
         and summary.get("rust_historical_semantic_mismatch_count") == 2042
         and summary.get("zig_historical_semantic_mismatch_count") == 1764
         and summary.get("performance") == "NOT MEASURED"
         and summary.get("final_holdout_opened") is False,
         "do not relabel the real V25 history or preflight failure as matching evidence")
    return {
        "schema": SCHEMA + "-read-only-frozen-context", "version": 1,
        "status": "PASS", "mode": "READ-ONLY PREFLIGHT FAILURE SOURCE FREEZE",
        "source": source_owner, "protocol": protocol_owner,
        "contract": contract_owner,
        "published_v25_evidence_owner_count": 139,
        "published_v25_authenticated_reference_count": 144,
        "actual_zig_build_process_count": 26,
        "actual_rust_build_process_count": 28,
        "actual_c_candidate_workers": 13,
        "actual_c_verified_passing_case_count": 7325,
        "actual_c_semantic_mismatch_count": 1262,
        "historical_rust_semantic_mismatch_count": 2042,
        "historical_zig_semantic_mismatch_count": 1764,
        "suite_count": 13, "case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "actual_observed_controller_run_count": 1,
        "actual_observed_controller_exit_status": 1,
        "actual_observed_controller_process_id": "NOT RECORDED",
        "actual_observed_stdout_bytes": 0,
        "actual_observed_stdout_sha256": EMPTY_SHA256,
        "actual_observed_stderr_bytes": len(OBSERVED_STDERR),
        "actual_observed_stderr_sha256": digest(OBSERVED_STDERR),
        "root_cause": cause,
        "original_campaign_evidence": absent,
        "preserved_preflight_evidence_owner_count": 0,
        **zero_effects(),
    }


class SourceOnlyWall:
    def __init__(self) -> None:
        self.saved: list[tuple[object, str, object]] = []
        self.blocked = 0

    def install(self, owner: object, name: str) -> None:
        previous = getattr(owner, name, None)
        if previous is None:
            return

        def forbidden(*_args: object, **_kwargs: object) -> object:
            self.blocked += 1
            raise PreservationError("blocked real preflight source effect: " + name)

        self.saved.append((owner, name, previous))
        setattr(owner, name, forbidden)

    def __enter__(self) -> SourceOnlyWall:
        for owner, names in (
            (builtins, ("open", "__import__")),
            (io, ("open",)),
            (os, ("open", "read", "write", "stat", "lstat", "mkdir", "makedirs",
                  "unlink", "remove", "rename", "replace", "link", "fsync",
                  "system", "fork", "posix_spawn")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes", "write_text",
                    "stat", "lstat", "mkdir", "unlink", "rename", "replace", "resolve")),
            (subprocess, ("run", "Popen", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection", "getaddrinfo")),
            (importlib, ("import_module",)),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile")),
            (threading.Thread, ("start",)),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "sleep")),
        ):
            for name in names:
                self.install(owner, name)
        return self

    def __exit__(self, _kind: object, _value: object, _traceback: object) -> None:
        for owner, name, previous in reversed(self.saved):
            setattr(owner, name, previous)


def self_test(source_pin: str, protocol_pin: str, contract_pin: str) -> dict:
    checked_digest(source_pin, "synthetic exact recorder source")
    checked_digest(protocol_pin, "synthetic exact recorder protocol")
    checked_digest(contract_pin, "synthetic exact recorder contract")
    with SourceOnlyWall() as wall:
        original = contract_document(source_pin, protocol_pin)
        validate_contract(original, source_pin, protocol_pin)
        rejected = 0

        def reject(value: dict) -> None:
            nonlocal rejected
            try:
                validate_contract(value, source_pin, protocol_pin)
            except (PreservationError, TypeError, ValueError, KeyError):
                rejected += 1
                return
            raise PreservationError("accepted a forged observed preflight result")

        forged = {
            "schema": "forged", "version": 2,
            "phase": "ACTIVATION AUTHORIZED",
            "family": "rust", "label": "forged",
        }
        for key, value in forged.items():
            changed = copy.deepcopy(original)
            changed[key] = value
            reject(changed)
        history_forged = {
            "evidence_owner_count": 141,
            "authenticated_reference_count": 146,
            "qualified_candidate_count": 1,
            "actual_c_candidate_workers": 0,
            "actual_c_semantic_mismatches": 0,
            "actual_c_verified_passing_case_count": 31237,
            "actual_rust_compiler_process_count": 0,
            "actual_rust_public_source_repairs": 0,
            "actual_rust_bridge_source_repairs": 0,
            "historical_rust_semantic_mismatches": 0,
            "historical_zig_semantic_mismatches": 0,
        }
        for key, value in history_forged.items():
            changed = copy.deepcopy(original)
            changed["published_v25"][key] = value
            reject(changed)
        observation_forged = {
            "actual_controller_run_count": 0,
            "exit_status": 0,
            "process_id": 1234,
            "process_id_recorded": True,
            "stdout_bytes": 1,
            "stdout_sha256": "0" * 64,
            "stdout_base64": "eA==",
            "stderr_bytes": len(OBSERVED_STDERR) + 1,
            "stderr_sha256": "0" * 64,
            "stderr_base64": "",
            "stderr_utf8": "forged",
            "exception_type": "ValueError",
            "exception_module": "forged",
            "exception_message": "forged",
            "failure_class": "SEMANTIC MISMATCH",
            "actual_candidate_workers": 1,
            "actual_candidate_activations": 1,
            "actual_candidate_matching_cases": 31237,
            "candidate_matching": "PASS",
            "original_campaign_archive_created": True,
            "original_campaign_receipt_created": True,
        }
        for key, value in observation_forged.items():
            changed = copy.deepcopy(original)
            changed["actual_captured_once_only_attempt"][key] = value
            reject(changed)
        for index, frame in enumerate(TRACEBACK_FRAMES):
            for key, value in (("path", "forged"), ("line", 0),
                               ("function", "forged")):
                changed = copy.deepcopy(original)
                changed["actual_captured_once_only_attempt"]["traceback_frames"][index][key] = value
                reject(changed)
        for key, value in (
                ("mature_v2_returned_owner_fields", []),
                ("v6_requires_absent_fields", []),
                ("both_synthetic_real_original_shapes_falsely_rejected", False),
                ("both_synthetic_normalized_owner_shapes_accepted", False),
                ("baseline_before_controller_try", False),
                ("preservation_unreachable_from_original_controller", False),
                ("canonical_target_mutation", True)):
            changed = copy.deepcopy(original)
            changed["independently_reproducible_root_cause"][key] = value
            reject(changed)
        for role in ORIGINALS:
            for key, value in (("inode", 0), ("sha256", "0" * 64),
                               ("nlink", 2), ("uid", 0), ("mode", 0o600)):
                changed = copy.deepcopy(original)
                changed["genuine_original_zig_targets"][role][key] = value
                reject(changed)
        for key, value in zero_effects().items():
            changed = copy.deepcopy(original)
            changed["source_only_effects"][key] = (
                1 if type(value) is int else True if value is False else "MEASURED"
            )
            reject(changed)
        for probe in (
            lambda: builtins.open("/tmp/rebar-zig-preflight-forbidden", "rb"),
            lambda: os.open("/tmp/rebar-zig-preflight-forbidden", os.O_RDONLY),
            lambda: os.write(-1, b"forbidden"),
            lambda: os.stat("candidates/_zig_probe.so"),
            lambda: os.link("x", "y"),
            lambda: os.replace("x", "y"),
            lambda: os.fsync(-1),
            lambda: subprocess.run(("forbidden-zig-original-campaign",)),
            lambda: importlib.import_module("candidates.zig_candidate"),
            lambda: socket.create_connection(("127.0.0.1", 1)),
            lambda: threading.Thread(target=lambda: None).start(),
            lambda: tempfile.mkdtemp(),
            lambda: time.perf_counter(),
        ):
            before = wall.blocked
            try:
                probe()
            except PreservationError:
                need(wall.blocked == before + 1,
                     "independently block every actual source-only external effect")
                rejected += 1
            else:
                raise PreservationError("synthetic control caused an actual side effect")
        need(rejected >= 90, "require comprehensive hostile preflight controls")
        return {
            "schema": SCHEMA + "-source-only-self-test", "version": 1,
            "status": "PASS", "synthetic_only": True,
            "accepted_control_count": 1,
            "rejected_hostile_control_count": rejected,
            "blocked_effect_count": wall.blocked,
            "published_v25_evidence_owner_count": 139,
            "published_v25_authenticated_reference_count": 144,
            "actual_observed_controller_run_count": 1,
            "actual_observed_controller_exit_status": 1,
            "actual_observed_controller_process_id": "NOT RECORDED",
            "actual_observed_stdout_sha256": EMPTY_SHA256,
            "actual_observed_stderr_sha256": digest(OBSERVED_STDERR),
            "mature_owner_missing_fields": list(MISSING_OWNER_FIELDS),
            "suite_count": 13,
            "case_execution_denominator": 31237,
            "preserved_preflight_evidence_owner_count": 0,
            **zero_effects(),
        }


def require_fresh_evidence(folder: int, name: str) -> None:
    need(type(name) is str and name and "/" not in name and "\x00" not in name,
         "authorize only one bounded exact durable evidence filename")
    try:
        os.stat(name, dir_fd=folder, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise PreservationError("never overwrite or reuse an actual evidence owner: " + name)


def write_exclusive(name: str, raw: bytes) -> dict:
    need(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT,
         "publish only complete bounded canonical failure bytes")
    folder = os.open(str(ROOT / EVIDENCE),
                     os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
    descriptor: int | None = None
    try:
        require_fresh_evidence(folder, name)
        descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                             | os.O_CLOEXEC | os.O_NOFOLLOW,
                             0o600, dir_fd=folder)
        start = os.fstat(descriptor)
        need(stat.S_ISREG(start.st_mode) and start.st_uid == os.geteuid()
             and start.st_nlink == 1
             and stat.S_IMODE(start.st_mode) == 0o600,
             "create only a fresh owner-only no-follow failure evidence owner")
        position = 0
        while position < len(raw):
            wrote = os.write(descriptor, raw[position:])
            need(type(wrote) is int and wrote > 0,
                 "reject incomplete exclusive preflight evidence publication")
            position += wrote
        os.fsync(descriptor)
        finish = os.fstat(descriptor)
        need((start.st_dev, start.st_ino)
             == (finish.st_dev, finish.st_ino)
             and finish.st_size == len(raw)
             and finish.st_nlink == 1
             and stat.S_IMODE(finish.st_mode) == 0o600,
             "reject a substituted or incomplete durable preflight owner")
        os.fsync(folder)
        return {
            "path": EVIDENCE + "/" + name,
            "sha256": digest(raw), "bytes": len(raw),
            "device": finish.st_dev, "inode": finish.st_ino,
            "mode": "0600", "nlink": finish.st_nlink,
            "exclusive_creation": True,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
        }
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(folder)


def verify_originals() -> dict:
    result = {}
    for role, expected in ORIGINALS.items():
        _raw, owner = read_owner(
            expected["relative"], expected["sha256"], expected["bytes"],
        )
        need(owner["device"] == expected["device"]
             and owner["inode"] == expected["inode"]
             and owner["mode"] == "0700"
             and owner["nlink"] == expected["nlink"]
             and owner["uid"] == expected["uid"],
             "reject an actually changed original user-owned Zig " + role)
        result[role] = owner
    return result


def preserve(options: argparse.Namespace) -> dict:
    need(options.label == LABEL
         and options.observed_exit_status == 1
         and options.observed_stdout_sha256 == EMPTY_SHA256
         and options.observed_stderr_sha256 == digest(OBSERVED_STDERR),
         "independently caller-pin the one genuine already-captured exit-1 failure")
    context = verify_context(options.source_sha256,
                             options.protocol_sha256,
                             options.contract_sha256)
    need(context.get("status") == "PASS"
         and len(context.get("original_campaign_evidence", ())) == 4,
         "reject altered preflight history or invented original campaign evidence")
    originals = verify_originals()
    archive_name, receipt_name = preservation_names()
    folder = os.open(str(ROOT / EVIDENCE),
                     os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        require_fresh_evidence(folder, archive_name)
        require_fresh_evidence(folder, receipt_name)
    finally:
        os.close(folder)
    report = {
        "schema": SCHEMA + "-actual-preserved-infrastructure-failure",
        "version": 1, "status": "FAIL",
        "failure_class": "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "family": "zig", "label": LABEL,
        "preservation_source_sha256": options.source_sha256,
        "preservation_protocol_sha256": options.protocol_sha256,
        "preservation_contract_sha256": options.contract_sha256,
        "original_campaign": {name: pin(value)
                              for name, value in sorted(CAMPAIGN.items())},
        "actual_once_only_controller": {
            "observation_provenance":
                "EXACT PARENT-CAPTURED ONCE-ONLY ORIGINAL CAMPAIGN PROCESS",
            "argv": observed_argv(),
            "exit_status": 1,
            "process_id": "NOT RECORDED",
            "process_id_recorded": False,
            "stdout": {"bytes": 0, "sha256": EMPTY_SHA256, "base64": ""},
            "stderr": {
                "bytes": len(OBSERVED_STDERR),
                "sha256": digest(OBSERVED_STDERR),
                "base64": base64.b64encode(OBSERVED_STDERR).decode("ascii"),
                "complete": True,
            },
            "traceback_frames": [
                {"path": path, "line": line, "function": function}
                for path, line, function in TRACEBACK_FRAMES
            ],
            "exception_type": "ActivationError",
            "exception_message":
                "refuse an absent, linked, altered, or substituted original Zig engine inode",
        },
        "root_cause": context["root_cause"],
        "original_campaign_evidence": context["original_campaign_evidence"],
        "original_campaign_archive_created": False,
        "original_campaign_receipt_created": False,
        "original_native_targets_unchanged": True,
        "genuine_original_native_targets": originals,
        "native_target_restoration_required": False,
        "native_target_activation_occurred": False,
        "suite_count": 13, "case_execution_denominator": 31237,
        "private_waiver_count": 13,
        "completed_suite_count": 0,
        "actual_candidate_workers": 0,
        "actual_matching_case_execution_count": 0,
        "semantic_mismatch_count": "NOT MEASURED",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "published_v25_evidence_owner_count": 139,
        "published_v25_authenticated_reference_count": 144,
        "actual_c_candidate_workers": 13,
        "actual_c_semantic_mismatch_count": 1262,
        "actual_c_verified_passing_case_count": 7325,
        "actual_zig_build_process_count": 26,
        "actual_rust_build_process_count": 28,
        "actual_rust_public_source_repair_count": 2,
        "actual_rust_bridge_source_repair_count": 2,
        "historical_rust_semantic_mismatch_count": 2042,
        "historical_zig_semantic_mismatch_count": 1764,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
        "archive_published_only_after_original_targets_verified": True,
    }
    plain = canonical(report)
    need(len(plain) <= MAX_REPORT,
         "bound the complete genuine once-only preflight failure record")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    archive_owner = write_exclusive(archive_name, archive)
    actual_archive, checked_archive = read_owner(
        archive_owner["path"], archive_owner["sha256"],
        archive_owner["bytes"], private=True,
    )
    need(actual_archive == archive
         and checked_archive["device"] == archive_owner["device"]
         and checked_archive["inode"] == archive_owner["inode"]
         and originals == verify_originals(),
         "fully verify exclusive archived failure bytes and both unchanged originals")
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "version": 1, "status": "PASS",
        "preserved_failure_status": "FAIL",
        "failure_class": "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "family": "zig", "label": LABEL,
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "contract_sha256": options.contract_sha256,
        "archive": archive_owner,
        "uncompressed_sha256": digest(plain),
        "uncompressed_bytes": len(plain),
        "actual_observed_controller_run_count": 1,
        "actual_observed_controller_exit_status": 1,
        "actual_observed_controller_process_id": "NOT RECORDED",
        "actual_observed_stdout_sha256": EMPTY_SHA256,
        "actual_observed_stderr_sha256": digest(OBSERVED_STDERR),
        "actual_candidate_workers": 0,
        "actual_native_activations": 0,
        "actual_matching_case_execution_count": 0,
        "candidate_correctness": "NOT MEASURED",
        "semantic_mismatch_count": "NOT MEASURED",
        "original_campaign_archive_created": False,
        "original_campaign_receipt_created": False,
        "original_native_targets_unchanged": True,
        "published_v25_evidence_owner_count": 139,
        "published_v25_authenticated_reference_count": 144,
        "new_repository_evidence_owner_count": 2,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    receipt_raw = canonical(receipt)
    receipt_owner = write_exclusive(receipt_name, receipt_raw)
    actual_receipt, checked_receipt = read_owner(
        receipt_owner["path"], receipt_owner["sha256"],
        receipt_owner["bytes"], private=True,
    )
    need(actual_receipt == receipt_raw
         and checked_receipt["device"] == receipt_owner["device"]
         and checked_receipt["inode"] == receipt_owner["inode"]
         and originals == verify_originals(),
         "verify complete independent durable failure receipt and untouched user originals")
    return {
        "schema": SCHEMA + "-published-preserved-failure",
        "version": 1, "status": "PASS",
        "actual_failure_status": "FAIL",
        "failure_class": "PRE-ACTIVATION INFRASTRUCTURE FAILURE",
        "archive": archive_owner, "receipt": receipt_owner,
        "actual_observed_controller_run_count": 1,
        "actual_observed_controller_exit_status": 1,
        "actual_observed_controller_process_id": "NOT RECORDED",
        "actual_candidate_workers": 0,
        "actual_native_activations": 0,
        "actual_campaign_reruns": 0,
        "candidate_correctness": "NOT MEASURED",
        "semantic_mismatch_count": "NOT MEASURED",
        "new_repository_evidence_owner_count": 2,
        "original_native_targets_unchanged": True,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--emit-contract", action="store_true")
    modes.add_argument("--preserve", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--contract-sha256")
    parser.add_argument("--label")
    parser.add_argument("--observed-exit-status", type=int)
    parser.add_argument("--observed-stdout-sha256")
    parser.add_argument("--observed-stderr-sha256")
    options = parser.parse_args(arguments)
    checked_digest(options.source_sha256, "preflight failure source")
    checked_digest(options.protocol_sha256, "preflight failure protocol")
    if options.emit_contract:
        need(options.contract_sha256 is None
             and options.label is None and options.observed_exit_status is None
             and options.observed_stdout_sha256 is None
             and options.observed_stderr_sha256 is None,
             "pure contract generation cannot authorize preservation or candidate runs")
        return options
    checked_digest(options.contract_sha256, "preflight failure contract")
    if options.self_test or options.verify_frozen_context:
        need(options.label is None and options.observed_exit_status is None
             and options.observed_stdout_sha256 is None
             and options.observed_stderr_sha256 is None,
             "source-only verification cannot authorize actual preservation")
        return options
    need(options.label == LABEL and options.observed_exit_status == 1,
         "explicit preservation requires the exact real exit-1 label")
    checked_digest(options.observed_stdout_sha256, "captured empty stdout")
    checked_digest(options.observed_stderr_sha256, "captured complete stderr")
    return options


def main(arguments: list[str] | None = None) -> int:
    try:
        runtime()
        options = parse_arguments(arguments)
        if options.emit_contract:
            result = contract_document(options.source_sha256,
                                       options.protocol_sha256)
        elif options.self_test:
            result = self_test(options.source_sha256,
                               options.protocol_sha256,
                               options.contract_sha256)
        elif options.verify_frozen_context:
            result = verify_context(options.source_sha256,
                                    options.protocol_sha256,
                                    options.contract_sha256)
        else:
            result = preserve(options)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0
    except (PreservationError, OSError, EOFError, ValueError, TypeError,
            KeyError, AttributeError, UnicodeError, RecursionError,
            gzip.BadGzipFile, subprocess.SubprocessError) as error:
        sys.stderr.write("ZIG PREFLIGHT FAILURE PRESERVATION V1: FAIL: "
                         + type(error).__qualname__ + ": " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
