#!/usr/bin/env python3
"""Crash-safe activation of independently proven V2 or V3 native engines.

``--self-test`` is synthetic and actively forbids filesystem, process, clock,
environment, import, thread, and network effects.  An explicitly pinned
``--activate`` is the only operation that can promote a native artifact.  A
durable journal and per-role intention are synchronized before each canonical
replacement.  ``--recover`` needs only the original pinned journal, including
after a process is killed before an activation report exists.

This tool is standalone.  It never imports a candidate, native extension,
earlier activator, native-build recorder, regex engine, benchmark, or holdout.
"""

from __future__ import annotations

import base64
import builtins
import copy
import gzip
import hashlib
import importlib
import io
import json
import os
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import zlib
from typing import Any


ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/activate_verified_native_candidate_v2.py"
PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V2.md"
SCHEMA = "rebar-phase2-verified-native-candidate-activation-v2"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
JOURNAL_SCHEMA = SCHEMA + "-recovery-journal"
INTENT_SCHEMA = SCHEMA + "-durable-promotion-intent"
REPORT_NAME = "activation-report.json"
RECEIPT_NAME = "activation-receipt.json"
JOURNAL_NAME = "recovery-journal.json"
PRIVATE_PREFIX = "rebar-phase2-verified-native-activation-v2-"
SANITIZED_BUILD_ROOT = "<FRESH_PRIVATE_TMP>"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PYTHON_INCLUDE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
GOAL_SHA256 = (
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
)
PHASE1_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
PHASE1_SHA256 = (
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
)
PINNED_GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_READELF = "/usr/bin/x86_64-linux-gnu-readelf"
RUST_TOOLCHAIN = "/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu"
PINNED_RUSTC = RUST_TOOLCHAIN + "/bin/rustc"
PINNED_CARGO = RUST_TOOLCHAIN + "/bin/cargo"
PINNED_ZIG = "/tmp/zig-x86_64-linux-0.16.0/zig"

MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024
MAX_LABEL_BYTES = 48

OWNER_FIELDS = (
    "relative", "path", "sha256", "size_bytes", "device", "inode", "mode",
)
DURABLE_FLAGS = (
    "exclusive_creation", "same_inode_readback_verified",
    "file_fsync_completed", "directory_fsync_completed",
)
PROMOTION_FLAGS = (
    "atomic_replace_completed", "adjacent_exclusive_stage_verified",
    "candidate_directory_fsync_completed",
)

BUILD_VERSIONS: dict[str, dict[str, str]] = {
    "2": {
        "source_relative": "tools/reproduce_phase2_native_builds_v2.py",
        "source_sha256":
            "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796",
        "protocol_relative": "oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md",
        "protocol_sha256":
            "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603",
        "schema": "rebar-phase2-independent-native-source-build-v2",
        "private_prefix": "rebar-phase2-native-build-v2-",
        "evidence_prefix": "native-source-build-v2-",
    },
    "3": {
        "source_relative": "tools/reproduce_phase2_native_builds_v3.py",
        "source_sha256":
            "c33d8e89c4b86f06e7cc06ecef9bca7052af86191d2e09ac89e665500147ba6f",
        "protocol_relative": "oracle/phase2/NATIVE-SOURCE-BUILDS-V3.md",
        "protocol_sha256":
            "273e5de944b661ec1f5cfbe3a26bcabc2e9b8c04353891fcfb822b07955eace3",
        "schema": "rebar-phase2-independent-native-source-build-v3",
        "private_prefix": "rebar-phase2-native-build-v3-",
        "evidence_prefix": "native-source-build-v3-",
    },
}

ORIGINAL_GUARD_SOURCES: dict[str, str] = {
    "tools/independent_original_cpython_suite_v5.py":
        "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
    "tools/independent_original_cpython_suite_v4.py":
        "1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3",
    "tools/rust_original_cpython_suite_v1.py":
        "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95",
    "tools/rust_original_cpython_suite_v2.py":
        "569036804b557b01eb29ba404c6fea0ecc5806bdbc2b6b9eb61c1ea18aa79267",
    "tools/rust_original_cpython_suite_v3.py":
        "55aced566c4ef0a236f26ddf4607dbe3e69ae9dc15ab6fd95399d4ddc346cea2",
}

FAMILIES: dict[str, dict[str, Any]] = {
    "c": {
        "module": "candidates.vm_candidate",
        "adapter": "candidates/vm_candidate.py",
        "owners": (
            "candidates/vm_candidate.py", "candidates/_vm_native.c",
        ),
        "binaries": {"extension": "_vm_native" + EXTENSION_SUFFIX},
    },
    "rust": {
        "module": "candidates.rust_candidate",
        "adapter": "candidates/rust_candidate.py",
        "owners": (
            "candidates/rust_candidate.py", "candidates/rust/py_bridge.c",
            "candidates/rust/Cargo.toml", "candidates/rust/Cargo.lock",
            "candidates/rust/src/lib.rs", "candidates/rust/src/newline.rs",
            "candidates/rust/src/search.rs", "candidates/rust/src/stack.rs",
            "candidates/rust/src/unicode_tables.rs",
        ),
        "binaries": {
            "engine": "_rust_engine.so",
            "bridge": "_rust_bridge" + EXTENSION_SUFFIX,
        },
    },
    "zig": {
        "module": "candidates.zig_candidate",
        "adapter": "candidates/zig_candidate.py",
        "owners": (
            "candidates/zig_candidate.py", "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
        "binaries": {
            "engine": "_zig_probe.so",
            "bridge": "_zig_bridge" + EXTENSION_SUFFIX,
        },
    },
}

PRESERVED_V2_OWNER_PINS: dict[str, dict[str, str]] = {
    "c": {
        "candidates/vm_candidate.py":
            "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
        "candidates/_vm_native.c":
            "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
    },
    "rust": {
        "candidates/rust_candidate.py":
            "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
        "candidates/rust/py_bridge.c":
            "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
        "candidates/rust/Cargo.toml":
            "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966",
        "candidates/rust/Cargo.lock":
            "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63",
        "candidates/rust/src/lib.rs":
            "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d",
        "candidates/rust/src/newline.rs":
            "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b",
        "candidates/rust/src/search.rs":
            "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe",
        "candidates/rust/src/stack.rs":
            "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e",
        "candidates/rust/src/unicode_tables.rs":
            "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af",
    },
    "zig": {
        "candidates/zig_candidate.py":
            "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
        "candidates/zig/mini_regex.zig":
            "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
        "candidates/zig/py_bridge.c":
            "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b",
    },
}

HISTORICAL_V1_OWNERS: tuple[tuple[str, str, int], ...] = (
    (
        "tools/reproduce_phase2_native_builds_v1.py",
        "e4cee196fcd6ff0908f46c26ef66363aa059e3003f2e89b302df10f35f9a3afd",
        96_017,
    ),
    (
        "oracle/phase2/NATIVE-SOURCE-BUILDS-V1.md",
        "33c495f6852155130c92af73422b7a6c6aae26b1c7012e65e2ddddab028064a2",
        9_446,
    ),
    (
        "oracle/phase2/evidence/native-source-build-v1-c-phase2-v1.json.gz",
        "b7844048cde986cae25ec4dafadfbb6dc560f4ea86108b908fe074176423f2e2",
        8_942,
    ),
    (
        "oracle/phase2/evidence/native-source-build-v1-c-phase2-v1-publication-receipt.json",
        "7736349d1e8dce83e47fdf741a4e34fb313d4d370a11a2d5563dba4468e55002",
        1_636,
    ),
)

RUST_ENGINE_EXPORTS = frozenset({
    "rebar_collect_ascii", "rebar_collect_wide", "rebar_compile",
    "rebar_compile_scanner", "rebar_error_copy", "rebar_error_include",
    "rebar_error_len", "rebar_error_pos", "rebar_flags", "rebar_free",
    "rebar_groups", "rebar_match", "rebar_match_ascii", "rebar_match_wide",
    "rebar_name_copy", "rebar_name_count", "rebar_name_group", "rebar_name_len",
})
ZIG_ENGINE_EXPORTS = frozenset({
    "rebar_zig_batch", "rebar_zig_collect_captures",
    "rebar_zig_collect_records", "rebar_zig_collect_records_wide",
    "rebar_zig_compile", "rebar_zig_compile_guarded", "rebar_zig_flags",
    "rebar_zig_free", "rebar_zig_groups", "rebar_zig_match",
    "rebar_zig_match_captures", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_tree", "rebar_zig_match_wide", "rebar_zig_name_copy",
    "rebar_zig_name_count", "rebar_zig_name_group", "rebar_zig_name_length",
    "rebar_zig_program_memory", "rebar_zig_program_size",
})
FORBIDDEN_NATIVE_NAMES = frozenset({
    "dlmopen", "dlopen", "dlsym", "dlvsym", "execv", "execve", "fork",
    "popen", "posix_spawn", "regcomp", "regexec", "regerror", "regfree",
    "system", "PyRun_AnyFile", "PyRun_SimpleString", "PyRun_String",
    "Py_CompileString", "PyEval_EvalCode",
})
FORBIDDEN_NATIVE_PREFIXES = (
    "hs_", "onig_", "pcre2_", "pcre_", "re2_", "regex_", "sre_", "_sre",
    "PyInit__sre", "PyRun_", "PyEval_Eval", "Py_CompileString",
    "google_re2", "hyperscan", "vectorscan", "rust_regex", "fancy_regex",
)
ALLOWED_SYSTEM_LIBRARIES = frozenset({
    "libc.so.6", "libm.so.6", "libgcc_s.so.1", "ld-linux-x86-64.so.2",
})

PRESERVED_V2_RECORDS: tuple[dict[str, Any], ...] = (
    {
        "family": "c", "status": "PASS", "genuine_process_count": 8,
        "archive_sha256":
            "4d954992312a039daa46a2810e51fc29cfdd2bd49d159dc834f5bf003e456878",
        "archive_bytes": 16_016,
        "uncompressed_sha256":
            "0d0a67a3c8ebba83806ba3b9beaee39e154f9d0483f0e39aac6bb04ecbfc598a",
        "uncompressed_bytes": 169_716,
        "receipt_sha256":
            "e90b4c12a087c0e8864c1627e242be18bd779f9d9693ec711f7dd575288eda24",
        "receipt_bytes": 1_639,
        "phase_outputs": (
            {"extension": (
                "ed57383dad99ce311664d165635fa300f3894df6b4816b5f54801d0e68263697",
                163_136,
            )},
            {"extension": (
                "ed57383dad99ce311664d165635fa300f3894df6b4816b5f54801d0e68263697",
                163_136,
            )},
        ),
    },
    {
        "family": "rust", "status": "PASS", "genuine_process_count": 16,
        "archive_sha256":
            "69b645c14ca3e566256f5a5b393a6d18554ad347b97b542383db3d86681bb35d",
        "archive_bytes": 33_741,
        "uncompressed_sha256":
            "389a833d6a3ce6c7aed3216759278d97d8d02dd901f758815e002f7a0031d4ec",
        "uncompressed_bytes": 279_925,
        "receipt_sha256":
            "15580e4441ce651c21800df187fcfaa88ec9336322348a07d84544094d5b050e",
        "receipt_bytes": 2_346,
        "phase_outputs": (
            {
                "engine": (
                    "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f",
                    658_344,
                ),
                "bridge": (
                    "9e13396f93872222f77577ac7658609f5e2d3e77c0655a27c83572f0a1a06b4c",
                    148_536,
                ),
            },
            {
                "engine": (
                    "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f",
                    658_344,
                ),
                "bridge": (
                    "9e13396f93872222f77577ac7658609f5e2d3e77c0655a27c83572f0a1a06b4c",
                    148_536,
                ),
            },
        ),
    },
    {
        "family": "zig", "status": "FAIL", "genuine_process_count": 15,
        "archive_sha256":
            "dc5128aaaf8a4d915c57ea8770696db3dc7ca51c89d5a3570cab9d259d070a0e",
        "archive_bytes": 19_556,
        "uncompressed_sha256":
            "f6ea1eb57d9ceb23c6dc5d4f291c4eb300768460a658d97828b7ce0095c53652",
        "uncompressed_bytes": 188_479,
        "receipt_sha256":
            "97e3150e9b68d3031c96ea6e973097687c80163a371f99a67f8b3de08bc0707a",
        "receipt_bytes": 1_766,
        "phase_outputs": (
            {
                "engine": (
                    "b73d43dc4bab42abc1de92e7aaf4a0b145e242ef8407714dc1bef48fc28a7d12",
                    480_040,
                ),
                "bridge": (
                    "c579cf52b767b84ecc3d0a60f837d526978ace4e7739fe4cf51c2d2c8cfd90d9",
                    133_656,
                ),
            },
            {
                "engine": (
                    "69a3f024c079b8994c4ffdbf37cbecf59d5afd67c8bcf5200a7331cae66d1f53",
                    480_040,
                ),
                "bridge": (
                    "c579cf52b767b84ecc3d0a60f837d526978ace4e7739fe4cf51c2d2c8cfd90d9",
                    133_656,
                ),
            },
        ),
    },
)


class ActivationError(Exception):
    """An exact source, proof, native owner, or recovery record failed."""


class SourceOnlyEffect(ActivationError):
    """Synthetic verification attempted a real outside effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ActivationError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=True, allow_nan=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise ActivationError("require one complete canonical finite JSON object") from error


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only actual complete immutable bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value),
            "require one exact lowercase SHA-256: " + label)
    return value


def checked_family(value: Any) -> str:
    require(type(value) is str and value in FAMILIES,
            "select exactly one independent C, Rust, or Zig family")
    return value


def checked_build_version(value: Any) -> str:
    require(type(value) is str and value in BUILD_VERSIONS,
            "explicitly select the separately frozen native build version 2 or 3")
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL_BYTES
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(item in "abcdefghijklmnopqrstuvwxyz0123456789-" for item in value)
            and "--" not in value and not value.endswith("-"),
            "reject a missing, cross-family, traversing, or noncanonical build label")
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512
            and not value.startswith("/") and "\\" not in value
            and "\x00" not in value
            and all(part not in ("", ".", "..") for part in value.split("/")),
            "reject an absolute, broad, disguised, or traversing relative owner")
    return value


def checked_positive_size(value: Any, label: str) -> int:
    require(type(value) is int and 0 < value <= MAX_BINARY_BYTES,
            "require one typed bounded positive native size: " + label)
    return value


def checked_private_root(
    value: Any, family: str, *, build: bool, build_version: str | None = None,
) -> str:
    family = checked_family(family)
    require(type(value) is str and "\x00" not in value and "\\" not in value,
            "require one literal owner-controlled private temporary root")
    parts = value.split("/")
    require(len(parts) == 3 and parts[:2] == ["", "tmp"],
            "reject a broad, redirected, nested, or traversing temporary root")
    if build:
        version = checked_build_version(build_version)
        prefix = BUILD_VERSIONS[version]["private_prefix"] + family + "-"
    else:
        require(build_version is None,
                "never confuse a build root with an activation recovery root")
        prefix = PRIVATE_PREFIX + family + "-"
    require(parts[2].startswith(prefix) and len(parts[2]) > len(prefix),
            "reject an omitted, cross-version, or cross-family private root")
    suffix = parts[2][len(prefix):]
    require(all(character.isascii()
                and (character.isalnum() or character in "-_")
                for character in suffix),
            "reject a disguised, injected, or traversing private suffix")
    return value


def parse_owner_pins(family: str, values: Any) -> dict[str, str]:
    expected = tuple(FAMILIES[checked_family(family)]["owners"])
    require(type(values) is list and len(values) == len(expected),
            "explicitly pin every independent source owner exactly once")
    result: dict[str, str] = {}
    for value in values:
        require(type(value) is str and value.count("=") == 1,
                "an owned-source pin must be RELATIVE/PATH=SHA256")
        relative, digest = value.split("=", 1)
        checked_relative(relative)
        require(relative in expected and relative not in result,
                "reject missing, repeated, cross-family, or outside source owners")
        result[relative] = checked_digest(digest, relative)
    require(set(result) == set(expected),
            "authenticate the complete independent native source closure")
    return dict(sorted(result.items()))


def unique_json_pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        require(type(key) is str and key not in result,
                "reject repeated or disguised signed JSON keys")
        result[key] = value
    return result


def reject_json_constant(value: str) -> Any:
    raise ActivationError("reject an infinite or non-finite JSON constant: " + value)


def decode_document(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
            "require one bounded complete canonical document: " + label)
    try:
        result = json.loads(raw.decode("utf-8"),
                            object_pairs_hook=unique_json_pairs,
                            parse_constant=reject_json_constant)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ActivationError("reject malformed signed JSON: " + label) from error
    require(type(result) is dict and canonical(result) == raw,
            "reject a noncanonical, incomplete, or rewritten document: " + label)
    return result


def bounded_gzip(raw: Any) -> bytes:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES,
            "require one caller-pinned bounded genuine source-build archive")
    decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        plain = decompressor.decompress(raw, MAX_REPORT_BYTES + 1)
        plain += decompressor.flush()
    except (ValueError, zlib.error) as error:
        raise ActivationError("reject an invalid canonical native archive") from error
    require(0 < len(plain) <= MAX_REPORT_BYTES and decompressor.eof
            and not decompressor.unused_data and not decompressor.unconsumed_tail
            and gzip.compress(plain, compresslevel=9, mtime=0) == raw,
            "reject appended, concatenated, oversized, truncated, or rewritten gzip")
    return plain


def zero_effects() -> dict[str, Any]:
    return {
        "candidate_processes_started": 0, "candidate_imports": 0,
        "native_libraries_loaded": 0, "reference_processes_started": 0,
        "network_requests": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "candidate_correctness": "NOT MEASURED", "winner_selected": False,
    }


def same_owner(actual: Any, expected: Any) -> bool:
    if type(actual) is not dict or type(expected) is not dict:
        return False
    for key in OWNER_FIELDS:
        if key not in actual or key not in expected:
            return False
        if type(actual[key]) is not type(expected[key]):
            return False
        if actual[key] != expected[key]:
            return False
    if type(actual["relative"]) is not str or type(actual["path"]) is not str:
        return False
    if type(actual["sha256"]) is not str:
        return False
    return all(type(actual[key]) is int
               for key in ("size_bytes", "device", "inode", "mode"))


def require_durable_owner(
    owner: Any, *, relative: str, root: str, directory_sync: bool,
) -> dict[str, Any]:
    checked_relative(relative)
    require(type(owner) is dict and owner.get("relative") == relative
            and owner.get("path") == root + "/" + relative
            and type(owner.get("mode")) is int and owner["mode"] == 0o600
            and all(owner.get(flag) is True for flag in DURABLE_FLAGS[:3])
            and (not directory_sync
                 or owner.get("directory_fsync_completed") is True)
            and type(owner.get("write_calls")) is int
            and owner["write_calls"] > 0,
            "require the original typed owner-only durable fsync evidence")
    checked_digest(owner.get("sha256"), relative)
    require(type(owner.get("size_bytes")) is int
            and 0 < owner["size_bytes"] <= MAX_BINARY_BYTES
            and type(owner.get("device")) is int
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "require all seven typed original durable owner identity fields")
    return owner


def checked_symbol_name(value: Any) -> tuple[str, str | None, bool]:
    require(type(value) is str and 0 < len(value) <= 1024,
            "require the actual complete GNU symbol-name column")
    parts = value.split("@")
    require(1 <= len(parts) <= 3, "reject a disguised GNU versioned symbol")
    name = parts[0]
    require(bool(name) and name[0] in
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$"
            and all(ch.isascii() and (ch.isalnum() or ch in "_.$") for ch in name),
            "reject an empty, shifted, non-ASCII, or version-index pseudo-symbol")
    version: str | None = None
    default = False
    if len(parts) == 2:
        version = parts[1]
    elif len(parts) == 3:
        require(parts[1] == "", "reject a malformed default GNU symbol version")
        default, version = True, parts[2]
    if version is not None:
        require(0 < len(version) <= 256
                and all(ch.isascii() and (ch.isalnum() or ch in "_.+-")
                        for ch in version),
                "reject a missing, malformed, or shifted native symbol version")
    require(name not in FORBIDDEN_NATIVE_NAMES
            and not any(name.startswith(prefix) for prefix in FORBIDDEN_NATIVE_PREFIXES),
            "reject original CPython, external regex, process, or dynamic delegation")
    return name, version, default


def parse_dynamic(raw: Any) -> dict[str, list[str]]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES
            and b"\x00" not in raw,
            "require one complete actual GNU ELF dynamic stream")
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise ActivationError("reject a non-UTF-8 GNU dynamic stream") from error
    result: dict[str, list[str]] = {
        "needed": [], "runpath": [], "rpath": [], "soname": [],
    }
    for line in text.splitlines():
        for marker, field in (
            ("(NEEDED)", "needed"), ("(RUNPATH)", "runpath"),
            ("(RPATH)", "rpath"), ("(SONAME)", "soname"),
        ):
            if marker not in line:
                continue
            start, stop = line.find("["), line.find("]", line.find("[") + 1)
            require(start >= 0 and stop > start,
                    "reject an omitted or shifted exact native dependency")
            result[field].append(line[start + 1:stop])
    for field, entries in result.items():
        require(all(type(item) is str and bool(item) and "\x00" not in item
                    for item in entries)
                and len(entries) == len(set(entries)),
                "reject repeated or disguised native dependencies: " + field)
    return result


def parse_symbols(raw: Any) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES
            and raw.endswith(b"\n") and b"\x00" not in raw,
            "require the complete version-aware GNU dynamic-symbol stream")
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise ActivationError("reject non-UTF-8 actual native symbol evidence") from error
    prefix, suffix = "Symbol table '.dynsym' contains ", " entries:"
    count: int | None = None
    entries: dict[int, dict[str, Any]] = {}
    allowed_types = frozenset({"NOTYPE", "OBJECT", "FUNC", "SECTION", "FILE",
                               "COMMON", "TLS", "GNU_IFUNC", "IFUNC"})
    bindings = frozenset({"LOCAL", "GLOBAL", "WEAK", "UNIQUE", "GNU_UNIQUE"})
    visibilities = frozenset({"DEFAULT", "INTERNAL", "HIDDEN", "PROTECTED"})
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(prefix):
            require(count is None and stripped.endswith(suffix),
                    "reject a duplicated or disguised GNU dynamic-symbol table")
            observed = stripped[len(prefix):-len(suffix)]
            require(observed.isascii() and observed.isdecimal()
                    and 1 <= int(observed) <= 131_072,
                    "reject an incomplete or unbounded native symbol count")
            count = int(observed)
            continue
        if stripped.startswith("Num:"):
            require(count is not None, "a GNU symbol header has no table")
            continue
        fields = stripped.split()
        require(bool(fields) and fields[0].endswith(":")
                and fields[0][:-1].isascii() and fields[0][:-1].isdecimal()
                and count is not None and 7 <= len(fields) <= 9,
                "reject a shifted, omitted, or trailing actual GNU symbol row")
        index = int(fields[0][:-1])
        require(0 <= index < count and index not in entries,
                "reject a repeated or outside native dynamic-symbol index")
        address, size, kind, binding, visibility, section = fields[1:7]
        require(address.isascii() and 1 <= len(address) <= 32
                and all(ch in "0123456789abcdefABCDEF" for ch in address)
                and size.isascii() and size.isdecimal()
                and 0 <= int(size) <= MAX_BINARY_BYTES
                and kind in allowed_types and binding in bindings
                and visibility in visibilities
                and (section in {"UND", "ABS", "COM"}
                     or section.isascii() and section.isdecimal()),
                "reject an invalid real GNU dynamic-symbol column")
        if len(fields) == 7:
            require(index == 0 and section == "UND" and binding == "LOCAL",
                    "only the genuine null dynamic symbol can have no name")
            entries[index] = {
                "index": index, "type": kind, "binding": binding,
                "visibility": visibility, "section": section, "name": None,
                "raw_name": None, "version": None,
                "default_version": False, "version_index": None,
            }
            continue
        name, version, default = checked_symbol_name(fields[7])
        version_index: int | None = None
        if len(fields) == 9:
            trailer = fields[8]
            require(version is not None and trailer.startswith("(")
                    and trailer.endswith(")") and trailer[1:-1].isascii()
                    and trailer[1:-1].isdecimal() and int(trailer[1:-1]) > 0,
                    "reject a GNU version-index token treated as a symbol")
            version_index = int(trailer[1:-1])
        entries[index] = {
            "index": index, "type": kind, "binding": binding,
            "visibility": visibility, "section": section, "name": name,
            "raw_name": fields[7], "version": version,
            "default_version": default, "version_index": version_index,
        }
    require(count is not None and len(entries) == count
            and set(entries) == set(range(count)),
            "require every exact ordered real GNU symbol, including versioned rows")
    rows = [entries[index] for index in range(count)]
    exports = sorted({row["name"] for row in rows
                      if row["name"] is not None and row["section"] != "UND"
                      and row["binding"] in {"GLOBAL", "WEAK", "UNIQUE", "GNU_UNIQUE"}})
    undefined = sorted({row["name"] for row in rows
                        if row["name"] is not None and row["section"] == "UND"})
    require(bool(exports), "require the actual independently owned native entry point")
    return {
        "exports": exports, "undefined": undefined, "symbol_count": count,
        "versioned_symbol_count": sum(row["version"] is not None for row in rows),
        "symbol_records": rows,
    }


def validate_elf(
    family: str, role: str, dynamic: dict[str, Any], symbols: dict[str, Any],
) -> dict[str, Any]:
    family = checked_family(family)
    require(role in FAMILIES[family]["binaries"],
            "reject a foreign or cross-family independently built native role")
    needed, exports = set(dynamic["needed"]), set(symbols["exports"])
    undefined = set(symbols["undefined"])
    combined = exports | undefined
    require(not dynamic["rpath"], "reject a native artifact with unsafe RPATH")
    if family == "c":
        require(role == "extension" and "PyInit__vm_native" in exports
                and needed.issubset(ALLOWED_SYSTEM_LIBRARIES)
                and not dynamic["runpath"]
                and not any(item.startswith(("rebar_", "rebar_zig_"))
                            or item in {"PyInit__rust_bridge", "PyInit__zig_bridge"}
                            for item in combined),
                "reject C delegation to Rust, Zig, a foreign engine, or dynamic loading")
        required = {"PyInit__vm_native"}
    elif family == "rust":
        require(not any(item.startswith("rebar_zig_")
                        or item in {"PyInit__vm_native", "PyInit__zig_bridge"}
                        for item in combined),
                "reject Rust delegation to another regex candidate")
        if role == "engine":
            require(dynamic["soname"] == ["_rust_engine.so"]
                    and not dynamic["runpath"]
                    and needed.issubset(ALLOWED_SYSTEM_LIBRARIES)
                    and RUST_ENGINE_EXPORTS.issubset(exports),
                    "require the exact dependency-free owned Rust engine")
            required = set(RUST_ENGINE_EXPORTS)
        else:
            require("PyInit__rust_bridge" in exports
                    and "_rust_engine.so" in needed
                    and needed.issubset(ALLOWED_SYSTEM_LIBRARIES | {"_rust_engine.so"})
                    and dynamic["runpath"] == ["$ORIGIN"]
                    and any(item.startswith("rebar_") for item in undefined)
                    and not any(item.startswith("rebar_zig_") for item in undefined),
                    "require the exact $ORIGIN bridge to only the owned Rust engine")
            required = {"PyInit__rust_bridge"}
    else:
        require(not any((item.startswith("rebar_")
                         and not item.startswith("rebar_zig_"))
                        or item in {"PyInit__vm_native", "PyInit__rust_bridge"}
                        for item in combined),
                "reject Zig delegation to a C, Rust, or outside regex engine")
        if role == "engine":
            require(dynamic["soname"] == ["_zig_probe.so"]
                    and not dynamic["runpath"]
                    and needed.issubset(ALLOWED_SYSTEM_LIBRARIES)
                    and ZIG_ENGINE_EXPORTS.issubset(exports),
                    "require the exact independent source-owned Zig engine")
            required = set(ZIG_ENGINE_EXPORTS)
        else:
            require("PyInit__zig_bridge" in exports and "_zig_probe.so" in needed
                    and needed.issubset(ALLOWED_SYSTEM_LIBRARIES | {"_zig_probe.so"})
                    and dynamic["runpath"] == ["$ORIGIN"]
                    and any(item.startswith("rebar_zig_") for item in undefined)
                    and not any(item.startswith("rebar_compile") for item in undefined),
                    "require the exact $ORIGIN bridge to only the owned Zig engine")
            required = {"PyInit__zig_bridge"}
    return {
        "role": role, "needed": sorted(needed),
        "runpath": list(dynamic["runpath"]), "soname": list(dynamic["soname"]),
        "required_exports": sorted(required), "exports": list(symbols["exports"]),
        "undefined": list(symbols["undefined"]),
        "symbol_count": symbols["symbol_count"],
        "versioned_symbol_count": symbols["versioned_symbol_count"],
        "symbol_records": list(symbols["symbol_records"]),
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
    }


def expected_environment(family: str, phase: str) -> dict[str, str]:
    family = checked_family(family)
    require(phase in ("reference-a", "reference-b"),
            "require an exact independently owned native-build phase")
    base = SANITIZED_BUILD_ROOT + "/" + phase
    values = {
        "PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C",
        "TZ": "UTC", "SOURCE_DATE_EPOCH": "1",
        "TMPDIR": base + "/temporary",
    }
    if family == "rust":
        remapped = " ".join(
            "--remap-path-prefix=" + SANITIZED_BUILD_ROOT + "/" + item
            + "/source=/rebar-phase2-owned-source"
            for item in ("reference-a", "reference-b")
        )
        values.update({
            "PATH": RUST_TOOLCHAIN + "/bin:/usr/bin:/bin",
            "CARGO_HOME": base + "/cargo-home", "CARGO_NET_OFFLINE": "true",
            "CARGO_INCREMENTAL": "0", "CARGO_BUILD_JOBS": "1",
            "RUSTC": PINNED_RUSTC,
            "RUSTFLAGS": remapped + " -Clink-arg=-Wl,-soname,_rust_engine.so",
        })
    elif family == "zig":
        values.update({
            "ZIG_GLOBAL_CACHE_DIR": base + "/zig-global-cache",
            "ZIG_LOCAL_CACHE_DIR": base + "/zig-local-cache",
        })
    return values


def planned_commands(
    family: str, phase: str, build_version: str,
) -> dict[str, list[str]]:
    family = checked_family(family)
    version = checked_build_version(build_version)
    require(phase in ("reference-a", "reference-b"),
            "reject a reused or outside source-build phase")
    base = SANITIZED_BUILD_ROOT + "/" + phase
    source, native = base + "/source", base + "/native"
    prefix = [
        "-ffile-prefix-map=" + SANITIZED_BUILD_ROOT + "/" + name
        + "/source=/rebar-phase2-owned-source"
        for name in ("reference-a", "reference-b")
    ]
    commands: dict[str, list[str]] = {
        "gcc_version": [PINNED_GCC, "--version"],
        "readelf_version": [PINNED_READELF, "--version"],
    }
    if family == "c":
        commands["build_c_extension"] = [
            PINNED_GCC, "-std=c11", "-O3", "-Wall", "-Wextra", "-Werror",
            "-fPIC", "-shared", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE, source + "/candidates/_vm_native.c",
            "-o", native + "/" + FAMILIES[family]["binaries"]["extension"],
        ]
    elif family == "rust":
        commands["rustc_version"] = [PINNED_RUSTC, "--version", "--verbose"]
        commands["cargo_version"] = [PINNED_CARGO, "--version"]
        commands["build_rust_engine"] = [
            PINNED_CARGO, "build", "--manifest-path",
            source + "/candidates/rust/Cargo.toml", "--release", "--locked",
            "--offline", "--frozen", "--target-dir", base + "/target",
        ]
        commands["build_rust_bridge"] = [
            PINNED_GCC, "-pthread", "-std=c11", "-shared", "-fPIC", "-O3",
            "-Wall", "-Wextra", "-Werror", "-Wl,-z,noexecstack",
            "-Wl,--exclude-libs,ALL", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE, source + "/candidates/rust/py_bridge.c",
            "-L" + native, "-l:_rust_engine.so", "-Wl,-rpath,$ORIGIN",
            "-o", native + "/" + FAMILIES[family]["binaries"]["bridge"],
        ]
    else:
        commands["zig_version"] = [PINNED_ZIG, "version"]
        strip = ["-fstrip"] if version == "3" else []
        commands["build_zig_engine"] = [
            PINNED_ZIG, "build-lib", source + "/candidates/zig/mini_regex.zig",
            "-dynamic", "-lc", "-O", "ReleaseFast", *strip,
            "-fallow-shlib-undefined", "-fsoname=_zig_probe.so",
            "--cache-dir", base + "/zig-local-cache",
            "--global-cache-dir", base + "/zig-global-cache",
            "-femit-bin=" + native + "/_zig_probe.so",
        ]
        commands["build_zig_bridge"] = [
            PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3", "-Wall",
            "-Wextra", "-Werror", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE, source + "/candidates/zig/py_bridge.c",
            "-L" + native, "-l:_zig_probe.so", "-Wl,-rpath,$ORIGIN",
            "-o", native + "/" + FAMILIES[family]["binaries"]["bridge"],
        ]
    for role, filename in FAMILIES[family]["binaries"].items():
        commands[role + "_dynamic"] = [
            PINNED_READELF, "--dynamic", "--wide", native + "/" + filename,
        ]
        commands[role + "_symbols"] = [
            PINNED_READELF, "--dyn-syms", "--wide", native + "/" + filename,
        ]
    return commands


def expected_process_schedule(family: str) -> list[tuple[str, str]]:
    family = checked_family(family)
    initial = ["gcc_version", "readelf_version"]
    if family == "rust":
        initial.extend(("rustc_version", "cargo_version"))
    elif family == "zig":
        initial.append("zig_version")
    result = [(name, "reference-a") for name in initial]
    for phase in ("reference-a", "reference-b"):
        if family == "c":
            result.append(("build_c_extension", phase))
        else:
            result.extend((("build_" + family + "_engine", phase),
                           ("build_" + family + "_bridge", phase)))
        for role in FAMILIES[family]["binaries"]:
            result.extend(((role + "_dynamic", phase),
                           (role + "_symbols", phase)))
    return result


def decode_process_output(process: Any, field: str) -> bytes:
    require(type(process) is dict and field in {"stdout", "stderr"},
            "require one complete exact actual native compiler stream")
    encoded = process.get(field + "_base64")
    require(type(encoded) is str and encoded.isascii(),
            "reject an omitted actual compiler or versioned-symbol stream")
    try:
        raw = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise ActivationError("reject altered actual native process output") from error
    require(base64.b64encode(raw).decode("ascii") == encoded
            and len(raw) <= MAX_PROCESS_BYTES
            and type(process.get(field + "_bytes")) is int
            and process[field + "_bytes"] == len(raw)
            and process.get(field + "_sha256") == sha256(raw),
            "retain all complete bounded genuinely recorded compiler output")
    return raw


def validate_processes(
    family: str, processes: Any, build_version: str,
) -> dict[tuple[str, str], dict[str, Any]]:
    family, version = checked_family(family), checked_build_version(build_version)
    schedule = expected_process_schedule(family)
    require(type(processes) is list and len(processes) == len(schedule),
            "retain every genuine pinned compiler and GNU inspector process")
    streams: dict[tuple[str, str], dict[str, Any]] = {}
    seen: set[int] = set()
    for process, (name, phase) in zip(processes, schedule, strict=True):
        require(type(process) is dict and process.get("name") == name
                and process.get("shell") is False
                and type(process.get("pid")) is int
                and process["pid"] > 0 and process["pid"] not in seen
                and type(process.get("exit_status")) is int
                and process["exit_status"] == 0,
                "reject a fabricated, reordered, reused, shell-based, or failed process")
        seen.add(process["pid"])
        require(process.get("argv") == planned_commands(family, phase, version)[name],
                "reject any changed exact compiler, cache, source, native, or strip command")
        require(process.get("environment") == expected_environment(family, phase),
                "reject an unpinned compiler environment or shared source/cache phase")
        stdout = decode_process_output(process, "stdout")
        stderr = decode_process_output(process, "stderr")
        if name == "zig_version":
            require(stdout == b"0.16.0\n",
                    "reject a substituted official stable Zig 0.16.0 compiler")
        if name == "cargo_version":
            require(stdout.startswith(b"cargo 1.95.0 (f2d3ce0bd"),
                    "reject an unpinned Rust cargo toolchain")
        if name == "rustc_version":
            require(stdout.startswith(b"rustc 1.95.0"),
                    "reject an unpinned Rust 1.95.0 compiler")
        if name.endswith(("_dynamic", "_symbols")):
            require(bool(stdout), "retain the complete genuine GNU ELF audit")
        streams[(phase, name)] = {
            "name": name, "phase": phase, "pid": process["pid"],
            "stdout": stdout, "stderr": stderr,
        }
    return streams


def expected_history_summary() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for source in PRESERVED_V2_RECORDS:
        phases = [
            {
                role: {"sha256": digest, "size_bytes": size}
                for role, (digest, size) in phase.items()
            }
            for phase in source["phase_outputs"]
        ]
        records.append({
            "family": source["family"], "status": source["status"],
            "archive_sha256": source["archive_sha256"],
            "archive_bytes": source["archive_bytes"],
            "receipt_sha256": source["receipt_sha256"],
            "receipt_bytes": source["receipt_bytes"],
            "uncompressed_sha256": source["uncompressed_sha256"],
            "uncompressed_bytes": source["uncompressed_bytes"],
            "independent_phase_count": 2,
            "genuine_process_count": source["genuine_process_count"],
            "phase_outputs": phases,
            "external_regex_package_count": 0,
            "cross_family_dependency_count": 0,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
        })
    return {
        "source_path": BUILD_VERSIONS["2"]["source_relative"],
        "source_sha256": BUILD_VERSIONS["2"]["source_sha256"],
        "protocol_path": BUILD_VERSIONS["2"]["protocol_relative"],
        "protocol_sha256": BUILD_VERSIONS["2"]["protocol_sha256"],
        "records": records,
        "candidate_processes_started": 0, "candidate_imports": 0,
        "native_libraries_loaded": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "winner_selected": False,
    }


def validate_publication(
    receipt: Any, report: Any, archive: bytes, arguments: dict[str, Any],
) -> None:
    family = checked_family(arguments.get("family"))
    version = checked_build_version(arguments.get("build_version"))
    specification = BUILD_VERSIONS[version]
    label = checked_label(arguments.get("build_label"))
    require(type(receipt) is dict and type(report) is dict
            and report.get("schema") == specification["schema"]
            and receipt.get("schema")
            == specification["schema"] + "-durable-publication-receipt"
            and report.get("status") == "PASS"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and report.get("family") == receipt.get("family") == family
            and report.get("label") == receipt.get("label") == label,
            "receipt publication success never turns a failed source build into PASS")
    required = {
        "schema", "status", "build_status", "family", "label",
        "source_sha256", "protocol_sha256", "phase1_manifest_sha256",
        "archive_relative", "archive_sha256", "archive_bytes",
        "uncompressed_sha256", "uncompressed_bytes", "archive_publication",
        "archive_directory_fsync", "owned_source_sha256",
        "candidate_processes_started", "candidate_imports",
        "native_libraries_loaded", "hidden_cases_read", "benchmark_files_read",
        "clock_samples", "timing_trials_run", "performance",
        "candidate_correctness", "winner_selected", "receipt_self_publication",
    }
    require(set(receipt) == required,
            "reject missing, injected, or cross-version durable build receipt fields")
    require(report.get("source_sha256") == receipt.get("source_sha256")
            == arguments.get("build_source_sha256") == specification["source_sha256"]
            and report.get("protocol_sha256") == receipt.get("protocol_sha256")
            == arguments.get("build_protocol_sha256") == specification["protocol_sha256"],
            "reject mixed, relabeled, or non-frozen V2/V3 recorder and protocol owners")
    base = EVIDENCE_RELATIVE + "/" + specification["evidence_prefix"]
    archive_relative = base + family + "-" + label + ".json.gz"
    plain = canonical(report)
    require(sha256(archive) == arguments.get("build_report_sha256")
            and sha256(canonical(receipt)) == arguments.get("build_receipt_sha256")
            and receipt.get("archive_relative") == archive_relative
            and receipt.get("archive_sha256") == sha256(archive)
            and type(receipt.get("archive_bytes")) is int
            and receipt["archive_bytes"] == len(archive)
            and receipt.get("uncompressed_sha256") == sha256(plain)
            and type(receipt.get("uncompressed_bytes")) is int
            and receipt["uncompressed_bytes"] == len(plain)
            and receipt.get("phase1_manifest_sha256") == PHASE1_SHA256,
            "require the exact separately pinned passing compressed report and receipt")
    published = receipt.get("archive_publication")
    require(type(published) is dict
            and published.get("path") == ROOT + "/" + archive_relative
            and published.get("sha256") == sha256(archive)
            and type(published.get("bytes")) is int
            and published["bytes"] == len(archive)
            and published.get("exclusive_creation") is True
            and published.get("same_inode_readback_verified") is True
            and published.get("file_fsync_completed") is True
            and type(published.get("write_calls")) is int
            and published["write_calls"] > 0,
            "require every typed genuine exclusive archive publication and fsync")
    synchronized = receipt.get("archive_directory_fsync")
    require(type(synchronized) is dict and synchronized.get("completed") is True
            and type(synchronized.get("device")) is int
            and type(synchronized.get("inode")) is int
            and synchronized["inode"] > 0,
            "require the independently durable actual archive directory fsync")
    shared = (
        "candidate_processes_started", "candidate_imports",
        "native_libraries_loaded", "hidden_cases_read", "benchmark_files_read",
        "clock_samples", "timing_trials_run",
    )
    for document in (report, receipt):
        require(all(type(document.get(name)) is int and document[name] == 0
                    for name in shared)
                and document.get("candidate_correctness") == "NOT MEASURED"
                and document.get("performance") == "NOT MEASURED"
                and document.get("winner_selected") is False,
                "a source-only proof claimed candidate, timing, holdout, or winner effects")
    require(type(report.get("reference_processes_started")) is int
            and report["reference_processes_started"] == 0
            and type(report.get("network_requests")) is int
            and report["network_requests"] == 0
            and receipt.get("receipt_self_publication") == "NOT CLAIMED",
            "reject a network, reference process, or false self-authenticating receipt")


def validate_source_snapshots(
    family: str, report: dict[str, Any], receipt: dict[str, Any],
    pins: dict[str, str], build_version: str,
) -> None:
    family, version = checked_family(family), checked_build_version(build_version)
    specification = BUILD_VERSIONS[version]
    expected = set(FAMILIES[family]["owners"])
    require(set(pins) == expected and report.get("owned_source_sha256") == pins
            and receipt.get("owned_source_sha256") == pins,
            "pin the complete independently owned matching native family source graph")
    before, after = report.get("owned_source_before"), report.get("owned_source_after")
    require(type(before) is dict and type(after) is dict
            and set(before) == set(after) == expected,
            "require full unchanged before-and-after no-follow source snapshots")
    for relative, digest in pins.items():
        first, second = before[relative], after[relative]
        require(type(first) is dict and type(second) is dict
                and first.get("path") == second.get("path") == ROOT + "/" + relative
                and first.get("sha256") == second.get("sha256") == digest
                and type(first.get("size_bytes")) is int
                and 0 < first["size_bytes"] <= MAX_SOURCE_BYTES
                and first.get("size_bytes") == second.get("size_bytes")
                and type(first.get("device")) is int
                and first.get("device") == second.get("device")
                and type(first.get("inode")) is int
                and first["inode"] > 0 and first.get("inode") == second.get("inode"),
                "an independent native source changed inode during its source build")
    phase1 = report.get("phase1")
    require(type(phase1) is dict and phase1.get("status") == "PASS"
            and type(phase1.get("suite_count")) is int
            and phase1["suite_count"] == 13
            and type(phase1.get("case_execution_count")) is int
            and phase1["case_execution_count"] == 31_237
            and phase1.get("candidate_correctness") == "NOT MEASURED"
            and phase1.get("performance") == "NOT MEASURED"
            and phase1.get("final_holdout_authorized") is False,
            "preserve all 31,237 frozen oracle checks without opening the holdout")
    support, support_after = (
        report.get("frozen_support_inputs"), report.get("frozen_support_inputs_after"),
    )
    require(type(support) is dict and type(support_after) is dict
            and set(support) == set(support_after),
            "preserve the exact complete frozen native support closure")
    required = {
        "immutable_objective": (ROOT + "/GOAL.md", GOAL_SHA256),
        "complete_correctness_manifest": (ROOT + "/" + PHASE1_RELATIVE, PHASE1_SHA256),
        "pinned_cpython_executable": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
        "native_build_recorder":
            (ROOT + "/" + specification["source_relative"], specification["source_sha256"]),
        "native_build_protocol":
            (ROOT + "/" + specification["protocol_relative"], specification["protocol_sha256"]),
    }
    require(set(required).issubset(support),
            "reject a changed original oracle, Python, or exact versioned build owner")
    if version == "3":
        required_v3 = {
            "preserved_v2_build_source", "preserved_v2_build_protocol",
            "preserved_v2_c_archive", "preserved_v2_c_receipt",
            "preserved_v2_rust_archive", "preserved_v2_rust_receipt",
            "preserved_v2_zig_archive", "preserved_v2_zig_receipt",
        }
        require(required_v3.issubset(support),
                "retain all source owners of all 39 genuine prior V2 history processes")
        if family == "zig":
            require({"pinned_official_zig_0_16_0_lock",
                     "pinned_official_zig_0_16_0_archive",
                     "pinned_official_zig_0_16_0_compiler"}.issubset(support),
                    "require the exact official Zig compiler, archive, and lock")
        require(report.get("preserved_version_two") == expected_history_summary(),
                "preserve the genuine C/Rust success and original Zig failure exactly")
    else:
        require("preserved_version_two" not in report,
                "never disguise a version-three report as version two")
    for name, (path, digest) in required.items():
        first, second = support.get(name), support_after.get(name)
        require(type(first) is dict and type(second) is dict
                and first.get("path") == second.get("path") == path
                and first.get("sha256") == second.get("sha256") == digest
                and type(first.get("size_bytes")) is int and first["size_bytes"] > 0
                and first.get("size_bytes") == second.get("size_bytes")
                and type(first.get("device")) is int
                and first.get("device") == second.get("device")
                and type(first.get("inode")) is int
                and first.get("inode") == second.get("inode"),
                "a pinned immutable V2/V3 support source changed inode")
    history = report.get("historical_v1_c")
    require(type(history) is dict
            and history.get("status")
            == "AUTHENTIC HISTORICAL BUILD; V1 SYMBOL AUDIT FALSIFIED"
            and type(history.get("real_versioned_symbol_count_per_phase")) is int
            and history["real_versioned_symbol_count_per_phase"] == 9
            and history.get("observed_v1_parser_false_symbols")
            == ["(2)", "(3)", "(4)", "(5)", "(6)"],
            "never convert the falsified historical GNU symbol parser into evidence")
    audit = report.get("source_independence_audit")
    require(type(audit) is dict
            and type(audit.get("source_owner_count")) is int
            and audit["source_owner_count"] == len(expected)
            and type(audit.get("external_regex_package_count")) is int
            and audit["external_regex_package_count"] == 0
            and type(audit.get("cross_family_dependency_count")) is int
            and audit["cross_family_dependency_count"] == 0,
            "reject an external regular-expression package or candidate delegation")
    source_audits = audit.get("source_audits")
    wanted = {item for item in expected if item.endswith((".py", ".c", ".rs", ".zig"))}
    require(type(source_audits) is list and len(source_audits) == len(wanted)
            and {item.get("path") for item in source_audits if type(item) is dict}
            == wanted,
            "independently audit every owned language and Python adapter source")
    for item in source_audits:
        require(type(item.get("external_regex_dependency_count")) is int
                and item["external_regex_dependency_count"] == 0
                and (not item["path"].endswith(".py")
                     or type(item.get("cross_family_dependency_count")) is int
                     and item["cross_family_dependency_count"] == 0),
                "reject direct or indirect external or cross-candidate delegation")
    cargo = audit.get("cargo_dependency_closure")
    if family == "rust":
        require(type(cargo) is dict
                and cargo.get("package") == "rebar-rust-continuation"
                and type(cargo.get("package_count")) is int
                and cargo["package_count"] == 1
                and type(cargo.get("external_package_count")) is int
                and cargo["external_package_count"] == 0
                and type(cargo.get("registry_count")) is int
                and cargo["registry_count"] == 0
                and type(cargo.get("build_script_count")) is int
                and cargo["build_script_count"] == 0
                and cargo.get("locked") is True and cargo.get("offline") is True,
                "require a genuinely locked, offline, zero-package Rust engine")
    else:
        require(cargo is None, "reject a disguised cross-family package closure")


def validate_build_report(
    report: dict[str, Any], receipt: dict[str, Any], archive: bytes,
    arguments: dict[str, Any], pins: dict[str, str],
) -> dict[str, dict[str, Any]]:
    family = checked_family(arguments.get("family"))
    version = checked_build_version(arguments.get("build_version"))
    validate_publication(receipt, report, archive, arguments)
    validate_source_snapshots(family, report, receipt, pins, version)
    require(report.get("fresh_private_root") == SANITIZED_BUILD_ROOT
            and report.get("error") is None,
            "require an actually passing reproducible private source build")
    streams = validate_processes(family, report.get("processes"), version)
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == 2
            and [item.get("name") if type(item) is dict else None for item in phases]
            == ["reference-a", "reference-b"],
            "require exactly two independent ordered fresh native-build phases")
    verified: dict[str, dict[str, Any]] = {}
    for phase in phases:
        name = phase["name"]
        prefix = SANITIZED_BUILD_ROOT + "/" + name
        require(phase.get("fresh_source_directory") == prefix + "/source"
                and phase.get("fresh_native_directory") == prefix + "/native"
                and all(type(phase.get(key)) is int and phase[key] == 0
                        for key in ("candidate_processes_started", "candidate_imports",
                                    "native_libraries_loaded", "timing_trials_run",
                                    "hidden_cases_read")),
                "never reuse a source/output phase or run a candidate or holdout")
        copied = phase.get("copied_source_owners")
        require(type(copied) is dict and set(copied) == set(pins),
                "copy every independent owner into each distinct source-build phase")
        for relative, digest in pins.items():
            owner = copied[relative]
            require(type(owner) is dict
                    and owner.get("path") == prefix + "/source/" + relative
                    and owner.get("sha256") == digest
                    and type(owner.get("bytes")) is int and owner["bytes"] > 0
                    and owner.get("exclusive_creation") is True
                    and owner.get("same_inode_readback_verified") is True
                    and type(owner.get("write_calls")) is int
                    and owner["write_calls"] > 0,
                    "require complete typed fresh independent source-copy evidence")
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict
                and set(outputs) == set(FAMILIES[family]["binaries"]),
                "reject an omitted, outside, or cross-family native role")
        for role, filename in FAMILIES[family]["binaries"].items():
            item = outputs[role]
            require(type(item) is dict and item.get("family") == family
                    and item.get("role") == role and item.get("file_name") == filename
                    and item.get("path") == prefix + "/native/" + filename
                    and type(item.get("size_bytes")) is int
                    and 0 < item["size_bytes"] <= MAX_BINARY_BYTES
                    and item.get("prebuilt_binary_read") is False
                    and item.get("candidate_imported") is False,
                    "reject a stale, prebuilt, renamed, or imported native artifact")
            checked_digest(item.get("sha256"), filename)
            dynamic = streams[(name, role + "_dynamic")]["stdout"]
            symbols = streams[(name, role + "_symbols")]["stdout"]
            observed = validate_elf(family, role, parse_dynamic(dynamic),
                                    parse_symbols(symbols))
            require(item.get("elf") == observed,
                    "require all exact actual complete versioned GNU symbol streams")
            if name == "reference-a":
                verified[role] = {
                    "file_name": filename, "sha256": item["sha256"],
                    "size_bytes": item["size_bytes"], "elf": observed,
                }
            else:
                require(role in verified
                        and verified[role]["sha256"] == item["sha256"]
                        and verified[role]["size_bytes"] == item["size_bytes"]
                        and verified[role]["elf"] == observed,
                        "reject source builds that do not reproduce byte-for-byte")
    reproduction = report.get("reproducibility")
    require(type(reproduction) is dict
            and type(reproduction.get("independent_fresh_phase_count")) is int
            and reproduction["independent_fresh_phase_count"] == 2
            and reproduction.get("byte_identical") is True
            and type(reproduction.get("prebuilt_binary_count")) is int
            and reproduction["prebuilt_binary_count"] == 0
            and type(reproduction.get("native_libraries_loaded")) is int
            and reproduction["native_libraries_loaded"] == 0,
            "require exactly two genuinely independent fresh, identical source builds")
    output_records = reproduction.get("native_outputs")
    require(type(output_records) is dict and set(output_records) == set(verified),
            "reject incomplete or cross-family genuine reproducibility output")
    for role, observed in verified.items():
        documented = output_records[role]
        require(type(documented) is dict
                and documented.get("file_name") == observed["file_name"]
                and documented.get("sha256") == observed["sha256"]
                and type(documented.get("size_bytes")) is int
                and documented["size_bytes"] == observed["size_bytes"]
                and documented.get("reproduced_in_two_fresh_directories") is True
                and documented.get("elf") == observed["elf"],
                "require actual byte-identical source evidence for every native role")
    engine_role = "extension" if family == "c" else "engine"
    bridge_role = "extension" if family == "c" else "bridge"
    require(verified[engine_role]["sha256"] == arguments.get("native_engine_sha256")
            and verified[bridge_role]["sha256"] == arguments.get("native_bridge_sha256")
            and verified[engine_role]["size_bytes"] == arguments.get("native_engine_bytes")
            and verified[bridge_role]["size_bytes"] == arguments.get("native_bridge_bytes")
            and (family == "c"
                 or verified[engine_role]["sha256"]
                 != verified[bridge_role]["sha256"]),
            "explicitly pin the exact separate actual engine and bridge bytes")
    return verified


def directory_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))


def regular_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def open_root(root: str, *, private: bool) -> int:
    require(type(root) is str and root.startswith("/") and root == root.rstrip("/")
            and "\x00" not in root,
            "open only the exact authenticated absolute no-follow owner root")
    descriptor = os.open(root, directory_flags())
    try:
        observed = os.fstat(descriptor)
        named = os.stat(root, follow_symlinks=False)
        require(stat.S_ISDIR(observed.st_mode) and stat.S_ISDIR(named.st_mode)
                and (observed.st_dev, observed.st_ino)
                == (named.st_dev, named.st_ino),
                "reject a replaced, non-directory, or symlinked authenticated root")
        if private:
            require(stat.S_IMODE(observed.st_mode) == 0o700
                    and observed.st_uid == os.geteuid(),
                    "require the genuine owner-only mode-0700 private directory")
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def read_owned(
    root: str, relative: str, expected: str | None, *, maximum: int,
    exact_size: int | None = None, private: bool = False,
) -> tuple[bytes, dict[str, Any]]:
    checked_relative(relative)
    if expected is not None:
        checked_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "require a typed strict authenticated artifact-size bound")
    if exact_size is not None:
        require(type(exact_size) is int and 0 < exact_size <= maximum,
                "require the exact typed genuine source/native size")
    opened: list[int] = []
    try:
        parent = open_root(root, private=private)
        opened.append(parent)
        parts = relative.split("/")
        for part in parts[:-1]:
            parent = os.open(part, directory_flags(), dir_fd=parent)
            opened.append(parent)
            require(stat.S_ISDIR(os.fstat(parent).st_mode),
                    "reject a symlinked or redirected owned source parent")
        descriptor = os.open(parts[-1], regular_flags(), dir_fd=parent)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino) == (named.st_dev, named.st_ino)
                and 0 < before.st_size <= maximum
                and (exact_size is None or before.st_size == exact_size),
                "reject a stale inode, symlink, non-file, or incorrect native size")
        digest = hashlib.sha256()
        blocks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(type(block) is bytes and bool(block),
                    "reject a truncated genuine independent source artifact")
            remaining -= len(block)
            digest.update(block)
            blocks.append(block)
        require(os.read(descriptor, 1) == b"",
                "reject an extra suffix in an authenticated native owner")
        after = os.fstat(descriptor)
        visible = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        actual = digest.hexdigest()
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (after.st_dev, after.st_ino, after.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and (expected is None or actual == expected),
                "reject a replaced, changed, moved, or differently hashed owner")
        raw = b"".join(blocks)
        return raw, {
            "relative": relative, "path": root + "/" + relative,
            "sha256": actual, "size_bytes": len(raw), "device": after.st_dev,
            "inode": after.st_ino, "mode": stat.S_IMODE(after.st_mode),
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def synchronize_directory(root: str, relative: str = "") -> dict[str, Any]:
    descriptor = open_root(root, private=True)
    opened = [descriptor]
    try:
        if relative:
            checked_relative(relative)
            for component in relative.split("/"):
                descriptor = os.open(component, directory_flags(), dir_fd=descriptor)
                opened.append(descriptor)
        original = os.fstat(descriptor)
        require(stat.S_ISDIR(original.st_mode),
                "synchronize only an actual authenticated private directory")
        os.fsync(descriptor)
        current = os.fstat(descriptor)
        require((original.st_dev, original.st_ino)
                == (current.st_dev, current.st_ino),
                "reject an activation directory replaced during durable fsync")
        return {"completed": True, "device": current.st_dev, "inode": current.st_ino}
    finally:
        for item in reversed(opened):
            os.close(item)


def write_fresh(root: str, relative: str, content: bytes) -> dict[str, Any]:
    checked_relative(relative)
    require(type(content) is bytes and 0 < len(content) <= MAX_BINARY_BYTES,
            "publish only complete bounded authenticated private evidence")
    opened: list[int] = []
    descriptor: int | None = None
    try:
        parent = open_root(root, private=True)
        opened.append(parent)
        parts = relative.split("/")
        for component in parts[:-1]:
            try:
                os.mkdir(component, 0o700, dir_fd=parent)
            except FileExistsError:
                pass
            parent = os.open(component, directory_flags(), dir_fd=parent)
            opened.append(parent)
            info = os.fstat(parent)
            require(stat.S_ISDIR(info.st_mode)
                    and stat.S_IMODE(info.st_mode) == 0o700
                    and info.st_uid == os.geteuid(),
                    "require an actual owner-only mode-0700 recovery parent")
        descriptor = os.open(
            parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            0o600, dir_fd=parent,
        )
        first = os.fstat(descriptor)
        require(stat.S_ISREG(first.st_mode)
                and stat.S_IMODE(first.st_mode) == 0o600,
                "publish recovery evidence only as exclusive mode-0600 files")
        position = 0
        calls = 0
        while position < len(content):
            count = os.write(descriptor, content[position:])
            require(type(count) is int and count > 0,
                    "reject a truncated durable canonical recovery record")
            position += count
            calls += 1
        os.fsync(descriptor)
        finished = os.fstat(descriptor)
        require((first.st_dev, first.st_ino) == (finished.st_dev, finished.st_ino)
                and finished.st_size == len(content),
                "reject replaced or incomplete durable recovery evidence")
        os.close(descriptor)
        descriptor = None
        _, owner = read_owned(root, relative, sha256(content),
                              maximum=MAX_BINARY_BYTES, exact_size=len(content),
                              private=True)
        require((owner["device"], owner["inode"])
                == (finished.st_dev, finished.st_ino),
                "reject a durable owner replaced between write, fsync, and readback")
        return {
            **owner, "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True, "write_calls": calls,
        }
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for item in reversed(opened):
            os.close(item)


def parse_arguments(arguments: Any) -> dict[str, Any]:
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "require one exact canonical dual-version activation command")
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    require(bool(arguments) and arguments[0] in {"--activate", "--restore", "--recover"},
            "explicitly choose source-only test, activation, restore, or recovery")
    operation = arguments[0][2:]
    reportless = operation == "recover" or (
        operation == "restore" and "--recovery-journal-sha256" in arguments[1:]
    )
    if reportless:
        mapping = {
            "--family": "family", "--build-version": "build_version",
            "--activation-root": "activation_root",
            "--activation-source-sha256": "activation_source_sha256",
            "--activation-protocol-sha256": "activation_protocol_sha256",
            "--recovery-journal-sha256": "recovery_journal_sha256",
        }
        mode = "recover"
    elif operation == "restore":
        mapping = {
            "--family": "family", "--build-version": "build_version",
            "--activation-root": "activation_root",
            "--activation-source-sha256": "activation_source_sha256",
            "--activation-protocol-sha256": "activation_protocol_sha256",
            "--activation-report-sha256": "activation_report_sha256",
            "--activation-receipt-sha256": "activation_receipt_sha256",
        }
        mode = "restore"
    else:
        mapping = {
            "--family": "family", "--build-version": "build_version",
            "--build-label": "build_label", "--build-root": "build_root",
            "--activation-source-sha256": "activation_source_sha256",
            "--activation-protocol-sha256": "activation_protocol_sha256",
            "--build-source-sha256": "build_source_sha256",
            "--build-protocol-sha256": "build_protocol_sha256",
            "--build-report-sha256": "build_report_sha256",
            "--build-receipt-sha256": "build_receipt_sha256",
            "--native-engine-sha256": "native_engine_sha256",
            "--native-bridge-sha256": "native_bridge_sha256",
            "--native-engine-bytes": "native_engine_bytes",
            "--native-bridge-bytes": "native_bridge_bytes",
        }
        mode = "activate"
    result: dict[str, Any] = {"mode": mode}
    if mode == "activate":
        result["owned_source_sha256"] = []
    offset = 1
    while offset < len(arguments):
        require(offset + 1 < len(arguments),
                "supply the exact complete value of every frozen activation option")
        name, value = arguments[offset], arguments[offset + 1]
        if name == "--owned-source-sha256" and mode == "activate":
            result["owned_source_sha256"].append(value)
        else:
            require(name in mapping and mapping[name] not in result,
                    "reject omitted, repeated, foreign, or abbreviated activation options")
            key = mapping[name]
            if key in {"native_engine_bytes", "native_bridge_bytes"}:
                require(value.isascii() and value.isdecimal()
                        and value == str(int(value)),
                        "require canonical typed positive actual native size arguments")
                result[key] = checked_positive_size(int(value), key)
            else:
                result[key] = value
        offset += 2
    expected = {"mode", *mapping.values()}
    if mode == "activate":
        expected.add("owned_source_sha256")
    require(set(result) == expected,
            "pin every version, owner, recovery record, archive, and source exactly once")
    family = checked_family(result["family"])
    version = checked_build_version(result["build_version"])
    for key in result:
        if key.endswith("_sha256") and key != "owned_source_sha256":
            checked_digest(result[key], key)
    if mode == "activate":
        checked_label(result["build_label"])
        checked_private_root(result["build_root"], family,
                             build=True, build_version=version)
        specification = BUILD_VERSIONS[version]
        require(result["build_source_sha256"] == specification["source_sha256"]
                and result["build_protocol_sha256"] == specification["protocol_sha256"],
                "pin the exact separately published source-build version and protocol")
        parse_owner_pins(family, result["owned_source_sha256"])
    else:
        checked_private_root(result["activation_root"], family, build=False)
    return result


def validate_historical_failure(
    report: dict[str, Any], receipt: dict[str, Any], archive: bytes,
    specification: dict[str, Any],
) -> None:
    family = checked_family(specification.get("family"))
    require(family == "zig" and specification.get("status") == "FAIL"
            and report.get("schema") == BUILD_VERSIONS["2"]["schema"]
            and report.get("status") == "FAIL"
            and receipt.get("schema")
            == BUILD_VERSIONS["2"]["schema"] + "-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "FAIL"
            and report.get("family") == receipt.get("family") == family
            and report.get("label") == receipt.get("label") == "phase2-v2"
            and report.get("source_sha256") == receipt.get("source_sha256")
            == BUILD_VERSIONS["2"]["source_sha256"]
            and report.get("protocol_sha256") == receipt.get("protocol_sha256")
            == BUILD_VERSIONS["2"]["protocol_sha256"],
            "preserve the actual published Zig reproducibility failure as a failure")
    base = EVIDENCE_RELATIVE + "/native-source-build-v2-zig-phase2-v2-failures"
    require(receipt.get("archive_relative") == base + ".json.gz"
            and receipt.get("archive_sha256") == specification["archive_sha256"]
            and type(receipt.get("archive_bytes")) is int
            and receipt["archive_bytes"] == specification["archive_bytes"]
            and receipt.get("uncompressed_sha256")
            == specification["uncompressed_sha256"]
            and type(receipt.get("uncompressed_bytes")) is int
            and receipt["uncompressed_bytes"] == specification["uncompressed_bytes"]
            and receipt.get("phase1_manifest_sha256") == PHASE1_SHA256
            and receipt.get("owned_source_sha256")
            == dict(sorted(PRESERVED_V2_OWNER_PINS[family].items()))
            and sha256(archive) == specification["archive_sha256"]
            and sha256(canonical(receipt)) == specification["receipt_sha256"]
            and receipt.get("receipt_self_publication") == "NOT CLAIMED",
            "reject relabeling or rewriting the independently published Zig loss")
    publication = receipt.get("archive_publication")
    require(type(publication) is dict
            and publication.get("path") == ROOT + "/" + base + ".json.gz"
            and publication.get("sha256") == specification["archive_sha256"]
            and type(publication.get("bytes")) is int
            and publication["bytes"] == specification["archive_bytes"]
            and publication.get("exclusive_creation") is True
            and publication.get("same_inode_readback_verified") is True
            and publication.get("file_fsync_completed") is True
            and type(publication.get("write_calls")) is int
            and publication["write_calls"] > 0,
            "preserve the actual durable published original Zig failure")
    sync = receipt.get("archive_directory_fsync")
    require(type(sync) is dict and sync.get("completed") is True
            and type(sync.get("device")) is int
            and type(sync.get("inode")) is int and sync["inode"] > 0,
            "the original failure archive was not separately durably published")
    for owner in (report, receipt):
        for key in ("candidate_processes_started", "candidate_imports",
                    "native_libraries_loaded", "hidden_cases_read",
                    "benchmark_files_read", "clock_samples", "timing_trials_run"):
            require(type(owner.get(key)) is int and owner[key] == 0,
                    "the historical build failure ran a candidate or holdout")
        require(owner.get("performance") == "NOT MEASURED"
                and owner.get("candidate_correctness") == "NOT MEASURED"
                and owner.get("winner_selected") is False,
                "do not assign speed, compatibility, or a winner to a failure")
    validate_source_snapshots(
        family, report, receipt,
        dict(sorted(PRESERVED_V2_OWNER_PINS[family].items())), "2",
    )
    streams = validate_processes(family, report.get("processes"), "2")
    require(len(streams) == specification["genuine_process_count"],
            "retain all 15 actual successful compiler processes in the failed build")
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == 2
            and [phase.get("name") if type(phase) is dict else None for phase in phases]
            == ["reference-a", "reference-b"],
            "retain both distinct actual failed Zig source-build phases")
    for index, phase in enumerate(phases):
        name = phase["name"]
        expected = specification["phase_outputs"][index]
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict and set(outputs) == set(expected),
                "retain both original genuine failed Zig native roles")
        for role, (digest, size) in expected.items():
            item = outputs[role]
            require(type(item) is dict and item.get("family") == family
                    and item.get("role") == role
                    and item.get("file_name") == FAMILIES[family]["binaries"][role]
                    and item.get("path") == SANITIZED_BUILD_ROOT + "/" + name
                    + "/native/" + FAMILIES[family]["binaries"][role]
                    and item.get("sha256") == digest
                    and type(item.get("size_bytes")) is int
                    and item["size_bytes"] == size
                    and item.get("prebuilt_binary_read") is False
                    and item.get("candidate_imported") is False,
                    "reject rewritten actual failed Zig native source-build outputs")
            observed = validate_elf(
                family, role,
                parse_dynamic(streams[(name, role + "_dynamic")]["stdout"]),
                parse_symbols(streams[(name, role + "_symbols")]["stdout"]),
            )
            require(item.get("elf") == observed,
                    "retain both genuine failed Zig complete ELF symbol streams")
    require(report.get("reproducibility") is None
            and report.get("error") == {
                "message": "two independent native builds are not byte-for-byte reproducible",
                "type": "BuildError",
            }
            and specification["phase_outputs"][0]["engine"][0]
            != specification["phase_outputs"][1]["engine"][0]
            and specification["phase_outputs"][0]["bridge"]
            == specification["phase_outputs"][1]["bridge"],
            "never conceal the actual differing source-built V2 Zig engines")


def authenticate_preserved_v2_history() -> dict[str, Any]:
    for relative, digest, size in HISTORICAL_V1_OWNERS:
        read_owned(ROOT, relative, digest,
                   maximum=MAX_ARCHIVE_BYTES if relative.endswith(".gz")
                   else MAX_SOURCE_BYTES, exact_size=size)
    summaries: list[dict[str, Any]] = []
    for specification in PRESERVED_V2_RECORDS:
        family = specification["family"]
        suffix = "-failures" if specification["status"] == "FAIL" else ""
        base = (EVIDENCE_RELATIVE + "/native-source-build-v2-" + family
                + "-phase2-v2" + suffix)
        archive, archive_owner = read_owned(
            ROOT, base + ".json.gz", specification["archive_sha256"],
            maximum=MAX_ARCHIVE_BYTES, exact_size=specification["archive_bytes"],
        )
        receipt_raw, receipt_owner = read_owned(
            ROOT, base + "-publication-receipt.json",
            specification["receipt_sha256"], maximum=MAX_SOURCE_BYTES,
            exact_size=specification["receipt_bytes"],
        )
        plain = bounded_gzip(archive)
        require(sha256(plain) == specification["uncompressed_sha256"]
                and len(plain) == specification["uncompressed_bytes"]
                and archive_owner["sha256"] == specification["archive_sha256"]
                and receipt_owner["sha256"] == specification["receipt_sha256"],
                "reject any altered complete genuine prior source-build evidence")
        report = decode_document(plain, "actual preserved V2 " + family + " report")
        receipt = decode_document(receipt_raw,
                                  "actual preserved V2 " + family + " receipt")
        pins = dict(sorted(PRESERVED_V2_OWNER_PINS[family].items()))
        if specification["status"] == "FAIL":
            validate_historical_failure(report, receipt, archive, specification)
        else:
            phases = specification["phase_outputs"]
            first = phases[0]
            engine_role = "extension" if family == "c" else "engine"
            bridge_role = "extension" if family == "c" else "bridge"
            arguments = {
                "family": family, "build_version": "2",
                "build_label": "phase2-v2", "build_root":
                    "/tmp/rebar-phase2-native-build-v2-" + family + "-preserved",
                "build_source_sha256": BUILD_VERSIONS["2"]["source_sha256"],
                "build_protocol_sha256": BUILD_VERSIONS["2"]["protocol_sha256"],
                "build_report_sha256": specification["archive_sha256"],
                "build_receipt_sha256": specification["receipt_sha256"],
                "native_engine_sha256": first[engine_role][0],
                "native_bridge_sha256": first[bridge_role][0],
                "native_engine_bytes": first[engine_role][1],
                "native_bridge_bytes": first[bridge_role][1],
            }
            validated = validate_build_report(report, receipt, archive, arguments, pins)
            require(len(validate_processes(family, report["processes"], "2"))
                    == specification["genuine_process_count"]
                    and set(validated) == set(FAMILIES[family]["binaries"]),
                    "retain every actual preserved V2 compiler and native symbol stream")
        summaries.append(next(
            item for item in expected_history_summary()["records"]
            if item["family"] == family
        ))
    expected = expected_history_summary()
    require(summaries == expected["records"]
            and sum(item["genuine_process_count"] for item in summaries) == 39,
            "retain all 39 actual C/Rust success and original Zig failure processes")
    return expected


def require_isolated_interpreter() -> None:
    require(sys.executable == PINNED_PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314"
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "use only the frozen isolated stable CPython 3.14.6 without bytecode")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "never activate after importing a candidate or native regex engine")


def authenticate_prerequisites(arguments: dict[str, Any]) -> dict[str, Any]:
    require_isolated_interpreter()
    family, version = (
        checked_family(arguments.get("family")),
        checked_build_version(arguments.get("build_version")),
    )
    specification = BUILD_VERSIONS[version]
    checked_private_root(arguments.get("build_root"), family,
                         build=True, build_version=version)
    pins = parse_owner_pins(family, arguments.get("owned_source_sha256"))
    frozen = (
        ("GOAL.md", GOAL_SHA256),
        (PHASE1_RELATIVE, PHASE1_SHA256),
        (SOURCE_RELATIVE, arguments["activation_source_sha256"]),
        (PROTOCOL_RELATIVE, arguments["activation_protocol_sha256"]),
        (specification["source_relative"], specification["source_sha256"]),
        (specification["protocol_relative"], specification["protocol_sha256"]),
    )
    support: dict[str, dict[str, Any]] = {}
    for relative, digest in frozen:
        _, support[relative] = read_owned(ROOT, relative, digest,
                                          maximum=MAX_SOURCE_BYTES)
    historical = authenticate_preserved_v2_history()
    sources: dict[str, bytes] = {}
    source_owners: dict[str, dict[str, Any]] = {}
    for relative, digest in pins.items():
        sources[relative], source_owners[relative] = read_owned(
            ROOT, relative, digest, maximum=MAX_SOURCE_BYTES,
        )
    guards: dict[str, dict[str, Any]] = {}
    for relative, digest in sorted(ORIGINAL_GUARD_SOURCES.items()):
        _, guards[relative] = read_owned(ROOT, relative, digest,
                                         maximum=MAX_SOURCE_BYTES)
    label = checked_label(arguments["build_label"])
    base = (EVIDENCE_RELATIVE + "/" + specification["evidence_prefix"]
            + family + "-" + label)
    archive, archive_owner = read_owned(
        ROOT, base + ".json.gz", arguments["build_report_sha256"],
        maximum=MAX_ARCHIVE_BYTES,
    )
    receipt_raw, receipt_owner = read_owned(
        ROOT, base + "-publication-receipt.json",
        arguments["build_receipt_sha256"], maximum=MAX_SOURCE_BYTES,
    )
    report = decode_document(bounded_gzip(archive), "exact V" + version + " build report")
    receipt = decode_document(receipt_raw, "exact V" + version + " build receipt")
    outputs = validate_build_report(report, receipt, archive, arguments, pins)
    if version == "3":
        require(report.get("preserved_version_two") == historical,
                "the passing V3 native result omitted or altered its 39-process history")
    for relative, owner in source_owners.items():
        observed = report["owned_source_after"][relative]
        require(owner["sha256"] == observed["sha256"]
                and owner["size_bytes"] == observed["size_bytes"]
                and owner["device"] == observed["device"]
                and owner["inode"] == observed["inode"],
                "reject an owned native source replaced after its real source build")
    native: dict[str, bytes] = {}
    phase_evidence: dict[str, list[dict[str, Any]]] = {}
    for role, output in outputs.items():
        both: list[dict[str, Any]] = []
        contents: list[bytes] = []
        for phase in ("reference-a", "reference-b"):
            relative = phase + "/native/" + output["file_name"]
            raw, owner = read_owned(
                arguments["build_root"], relative, output["sha256"],
                maximum=MAX_BINARY_BYTES, exact_size=output["size_bytes"],
                private=True,
            )
            both.append(owner)
            contents.append(raw)
        require(len(both) == 2 and contents[0] == contents[1]
                and (both[0]["device"], both[0]["inode"])
                != (both[1]["device"], both[1]["inode"]),
                "require actual matching bytes in two separately owned phase inodes")
        native[role], phase_evidence[role] = contents[0], both
    return {
        "family": family, "build_version": version, "label": label,
        "owned_source_sha256": pins, "source_bytes": sources,
        "source_evidence": source_owners, "guard_evidence": guards,
        "frozen_support": support, "preserved_version_two": historical,
        "build_archive": archive_owner, "build_receipt": receipt_owner,
        "native_bytes": native, "native_outputs": outputs,
        "native_phase_evidence": phase_evidence,
    }


def canonical_candidate_directory() -> tuple[int, int]:
    root_descriptor = open_root(ROOT, private=False)
    try:
        candidate_descriptor = os.open("candidates", directory_flags(),
                                       dir_fd=root_descriptor)
        actual = os.fstat(candidate_descriptor)
        require(stat.S_ISDIR(actual.st_mode) and actual.st_uid == os.geteuid(),
                "promote only within the actual owner-controlled candidates directory")
        return root_descriptor, candidate_descriptor
    except BaseException:
        os.close(root_descriptor)
        raise


def current_canonical(relative: str) -> tuple[bytes, dict[str, Any]] | None:
    checked_relative(relative)
    require(relative.startswith("candidates/") and len(relative.split("/")) == 2,
            "inspect only one exact approved canonical native artifact")
    root_descriptor, descriptor = canonical_candidate_directory()
    try:
        name = relative.split("/", 1)[1]
        try:
            observed = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        except FileNotFoundError:
            return None
        require(stat.S_ISREG(observed.st_mode),
                "refuse a canonical symlink, directory, or non-regular user file")
        return read_owned(ROOT, relative, None, maximum=MAX_BINARY_BYTES)
    finally:
        os.close(descriptor)
        os.close(root_descriptor)


def verify_canonical_snapshot(relative: str, expected: dict[str, Any] | None) -> None:
    current = current_canonical(relative)
    if expected is None:
        require(current is None,
                "an originally absent canonical native target appeared")
    else:
        require(current is not None and same_owner(current[1], expected),
                "a user native target changed identity before promotion")


def stage_and_replace(
    relative: str, content: bytes, *, expected_current: dict[str, Any] | None,
    final_mode: int, promotion_intent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    checked_relative(relative)
    require(relative.startswith("candidates/") and len(relative.split("/")) == 2,
            "replace only one independently approved fixed candidate native filename")
    require(type(content) is bytes and 0 < len(content) <= MAX_BINARY_BYTES,
            "stage only complete actual authenticated native or recovery bytes")
    require(type(final_mode) is int and 0 <= final_mode <= 0o777,
            "preserve the exact typed original canonical native permission mode")
    if promotion_intent is not None:
        require(type(promotion_intent) is dict,
                "require one complete independently durable pre-replace intention")
        family = checked_family(promotion_intent.get("family"))
        checked_private_root(promotion_intent.get("activation_root"), family,
                             build=False)
        role = promotion_intent.get("role")
        require(role in FAMILIES[family]["binaries"]
                and relative == "candidates/" + FAMILIES[family]["binaries"][role],
                "reject an unapproved, broad, cross-family staged native filename")
        checked_digest(promotion_intent.get("recovery_journal_sha256"),
                       "actual pre-promotion recovery journal")
    digest = sha256(content)
    filename = relative.split("/", 1)[1]
    temporary = ".rebar-phase2-verified-v2-" + os.urandom(18).hex() + "-" + filename
    require(len(temporary) <= 240, "bound the exact adjacent exclusive staging filename")
    temporary_relative = "candidates/" + temporary
    root_descriptor, candidate_descriptor = canonical_candidate_directory()
    descriptor: int | None = None
    identity: tuple[int, int] | None = None
    replaced = False
    published_intent: dict[str, Any] | None = None
    try:
        descriptor = os.open(
            temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            0o600, dir_fd=candidate_descriptor,
        )
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode)
                and stat.S_IMODE(initial.st_mode) == 0o600,
                "create an adjacent exclusive mode-0600 staging file first")
        identity = (initial.st_dev, initial.st_ino)
        position = 0
        while position < len(content):
            count = os.write(descriptor, content[position:])
            require(type(count) is int and count > 0,
                    "reject truncated canonical native staging bytes")
            position += count
        if final_mode != 0o600:
            os.fchmod(descriptor, final_mode)
        os.fsync(descriptor)
        finished = os.fstat(descriptor)
        require((finished.st_dev, finished.st_ino) == identity
                and finished.st_size == len(content)
                and stat.S_IMODE(finished.st_mode) == final_mode,
                "preserve the exact adjacent source-built inode and original mode")
        os.close(descriptor)
        descriptor = None
        _, staged = read_owned(ROOT, temporary_relative, digest,
                               maximum=MAX_BINARY_BYTES, exact_size=len(content))
        require((staged["device"], staged["inode"]) == identity,
                "reject an adjacent staged native inode replaced after fsync")
        verify_canonical_snapshot(relative, expected_current)
        if promotion_intent is not None:
            target = {
                "relative": relative, "path": ROOT + "/" + relative,
                "sha256": digest, "size_bytes": len(content),
                "device": staged["device"], "inode": staged["inode"],
                "mode": final_mode,
            }
            intention = {
                "schema": INTENT_SCHEMA, "status": "PREPARED",
                "promotion_mode": "recoverable-canonical-promotion",
                "family": promotion_intent["family"],
                "activation_root": promotion_intent["activation_root"],
                "candidate_import_root": ROOT,
                "build_version": promotion_intent["build_version"],
                "recovery_journal_sha256":
                    promotion_intent["recovery_journal_sha256"],
                "role": promotion_intent["role"], "target": target,
                **zero_effects(),
            }
            published_intent = write_fresh(
                promotion_intent["activation_root"],
                "promotion-intent-" + promotion_intent["role"] + ".json",
                canonical(intention),
            )
            synced = synchronize_directory(promotion_intent["activation_root"])
            published_intent["directory_fsync_completed"] = synced["completed"]
            require_durable_owner(
                published_intent,
                relative="promotion-intent-" + promotion_intent["role"] + ".json",
                root=promotion_intent["activation_root"], directory_sync=True,
            )
            verify_canonical_snapshot(relative, expected_current)
        os.replace(temporary, filename,
                   src_dir_fd=candidate_descriptor, dst_dir_fd=candidate_descriptor)
        replaced = True
        os.fsync(candidate_descriptor)
        _, promoted = read_owned(ROOT, relative, digest,
                                 maximum=MAX_BINARY_BYTES, exact_size=len(content))
        require((promoted["device"], promoted["inode"]) == identity
                and promoted["mode"] == final_mode,
                "reject a replaced promoted inode or altered original native mode")
        result = {
            **promoted, "atomic_replace_completed": True,
            "adjacent_exclusive_stage_verified": True,
            "candidate_directory_fsync_completed": True,
        }
        if published_intent is not None:
            result["promotion_intent"] = published_intent
        return result
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if identity is not None and not replaced:
            try:
                named = os.stat(temporary, dir_fd=candidate_descriptor,
                                follow_symlinks=False)
            except FileNotFoundError:
                named = None
            if named is not None:
                require(stat.S_ISREG(named.st_mode)
                        and (named.st_dev, named.st_ino) == identity,
                        "never remove a substituted user-owned staging filename")
                os.unlink(temporary, dir_fd=candidate_descriptor)
                os.fsync(candidate_descriptor)
        os.close(candidate_descriptor)
        os.close(root_descriptor)


def build_provenance(
    prerequisite: dict[str, Any], arguments: dict[str, Any],
) -> dict[str, Any]:
    version = checked_build_version(arguments["build_version"])
    return {
        "build_version": version,
        "schema": BUILD_VERSIONS[version]["schema"],
        "family": prerequisite["family"], "label": prerequisite["label"],
        "source_sha256": arguments["build_source_sha256"],
        "protocol_sha256": arguments["build_protocol_sha256"],
        "archive_relative": prerequisite["build_archive"]["relative"],
        "archive_sha256": prerequisite["build_archive"]["sha256"],
        "receipt_relative": prerequisite["build_receipt"]["relative"],
        "receipt_sha256": prerequisite["build_receipt"]["sha256"],
        "build_root": arguments["build_root"],
        "independent_fresh_phase_count": 2,
        "actual_versioned_symbol_streams_verified": True,
        "preserved_version_two_history_process_count": 39,
    }


def prepare_recovery_journal(
    root: str, prerequisite: dict[str, Any], arguments: dict[str, Any],
    provenance: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for role, output in prerequisite["native_outputs"].items():
        relative = "candidates/" + output["file_name"]
        previous = current_canonical(relative)
        original: dict[str, Any] | None = None
        backup: dict[str, Any] | None = None
        if previous is not None:
            original_bytes, original = previous
            backup = write_fresh(root, "backups/" + relative, original_bytes)
            require_durable_owner(backup, relative="backups/" + relative,
                                  root=root, directory_sync=False)
            require(backup["sha256"] == original["sha256"]
                    and backup["size_bytes"] == original["size_bytes"],
                    "preserve every exact previous canonical byte before promotion")
        entries[role] = {
            "role": role, "target_relative": relative,
            "target_path": ROOT + "/" + relative,
            "originally_present": previous is not None,
            "original_owner": original, "backup": backup,
            "promoted_sha256": output["sha256"],
            "promoted_size_bytes": output["size_bytes"],
        }
    for entry in entries.values():
        verify_canonical_snapshot(entry["target_relative"], entry["original_owner"])
    if any(item["originally_present"] for item in entries.values()):
        synchronize_directory(root, "backups/candidates")
        synchronize_directory(root, "backups")
    journal = {
        "schema": JOURNAL_SCHEMA, "status": "PREPARED",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": prerequisite["family"],
        "build_version": prerequisite["build_version"],
        "label": prerequisite["label"], "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_source_sha256": arguments["activation_source_sha256"],
        "activation_protocol_sha256": arguments["activation_protocol_sha256"],
        "source_build": provenance,
        "owned_source_sha256": prerequisite["owned_source_sha256"],
        "backup_entries": entries,
        **zero_effects(),
    }
    owner = write_fresh(root, JOURNAL_NAME, canonical(journal))
    synced = synchronize_directory(root)
    owner["directory_fsync_completed"] = synced["completed"]
    require_durable_owner(owner, relative=JOURNAL_NAME,
                          root=root, directory_sync=True)
    return journal, owner


def validate_promotion_intent(
    document: Any, *, family: str, build_version: str, root: str, role: str,
    journal_sha256: str, current: dict[str, Any],
) -> dict[str, Any]:
    family, version = checked_family(family), checked_build_version(build_version)
    checked_private_root(root, family, build=False)
    checked_digest(journal_sha256, "durable pre-promotion recovery journal")
    require(role in FAMILIES[family]["binaries"]
            and type(document) is dict and document.get("schema") == INTENT_SCHEMA
            and document.get("status") == "PREPARED"
            and document.get("promotion_mode") == "recoverable-canonical-promotion"
            and document.get("family") == family
            and document.get("build_version") == version
            and document.get("activation_root") == root
            and document.get("candidate_import_root") == ROOT
            and document.get("recovery_journal_sha256") == journal_sha256
            and document.get("role") == role,
            "require the exact versioned durable native staged-inode intention")
    relative = "candidates/" + FAMILIES[family]["binaries"][role]
    target = document.get("target")
    require(type(target) is dict and target.get("relative") == relative
            and target.get("path") == ROOT + "/" + relative
            and same_owner(target, current),
            "reject a substituted relative path, hash, byte size, inode, or mode")
    checked_digest(target.get("sha256"), relative)
    checked_positive_size(target.get("size_bytes"), relative)
    require(type(target.get("mode")) is int and 0 <= target["mode"] <= 0o777,
            "preserve the exact typed original promoted native permission mode")
    require(all(type(document.get(key)) is type(value)
                and document.get(key) == value
                for key, value in zero_effects().items()),
            "a durable promotion intention reports candidate or benchmark effects")
    return {key: target[key] for key in OWNER_FIELDS}


def classify_recovery_state(entry: Any, current: Any) -> str:
    require(type(entry) is dict and type(entry.get("originally_present")) is bool,
            "classify only one honestly recorded original native target")
    digest = checked_digest(entry.get("promoted_sha256"), "journaled native role")
    size = checked_positive_size(entry.get("promoted_size_bytes"), "journaled native role")
    original = entry.get("original_owner")
    if current is None:
        require(entry["originally_present"] is False,
                "an originally present canonical user artifact disappeared")
        return "originally-absent"
    require(type(current) is dict
            and type(current.get("size_bytes")) is int
            and type(current.get("mode")) is int,
            "reject an incomplete or bool-forged canonical native owner")
    if entry["originally_present"]:
        require(type(original) is dict,
                "retain all seven typed original owner identity fields")
        if same_owner(current, original):
            return "already-original"
    if current.get("sha256") == digest and current["size_bytes"] == size:
        return "source-verified-promoted"
    raise ActivationError("refuse to replace a user-modified or unrelated native file")


def authenticate_promotion_intents(
    root: str, journal: dict[str, Any], journal_sha256: str,
    *, announced_targets: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    family = checked_family(journal.get("family"))
    version = checked_build_version(journal.get("build_version"))
    checked_private_root(root, family, build=False)
    checked_digest(journal_sha256, "crash-recovery native journal")
    if announced_targets is not None:
        require(type(announced_targets) is dict
                and set(announced_targets) == set(FAMILIES[family]["binaries"]),
                "reject missing actual announced durable promotion target records")
    result: dict[str, dict[str, Any]] = {}
    for role, filename in FAMILIES[family]["binaries"].items():
        entry = journal["backup_entries"][role]
        actual = current_canonical("candidates/" + filename)
        state = classify_recovery_state(entry, actual[1] if actual is not None else None)
        if state != "source-verified-promoted":
            continue
        require(actual is not None, "the actually promoted native inode disappeared")
        relative = "promotion-intent-" + role + ".json"
        raw, observed = read_owned(root, relative, None,
                                   maximum=MAX_SOURCE_BYTES, private=True)
        require(observed["mode"] == 0o600,
                "require the actual pre-replace intention remain owner-only")
        document = decode_document(raw, "actual pre-replace durable intention")
        target = validate_promotion_intent(
            document, family=family, build_version=version, root=root,
            role=role, journal_sha256=journal_sha256, current=actual[1],
        )
        proof: dict[str, Any] = {"intent": observed, "target": target}
        if announced_targets is not None:
            announced_target = announced_targets[role]
            require(type(announced_target) is dict
                    and all(announced_target.get(flag) is True
                            for flag in PROMOTION_FLAGS)
                    and same_owner(actual[1], announced_target),
                    "reject an unauthenticated or changed actual promoted native inode")
            rich = announced_target.get("promotion_intent")
            require(type(rich) is dict and same_owner(observed, rich),
                    "compare seven owned identity fields, not unlike metadata dicts")
            require_durable_owner(rich, relative=relative, root=root,
                                  directory_sync=True)
            proof["intent"] = rich
        result[role] = proof
    return result


def validate_build_provenance(value: Any, family: str, version: str) -> dict[str, Any]:
    family, version = checked_family(family), checked_build_version(version)
    specification = BUILD_VERSIONS[version]
    expected_keys = {
        "build_version", "schema", "family", "label", "source_sha256",
        "protocol_sha256", "archive_relative", "archive_sha256",
        "receipt_relative", "receipt_sha256", "build_root",
        "independent_fresh_phase_count", "actual_versioned_symbol_streams_verified",
        "preserved_version_two_history_process_count",
    }
    require(type(value) is dict and set(value) == expected_keys
            and value.get("build_version") == version
            and value.get("schema") == specification["schema"]
            and value.get("family") == family
            and value.get("source_sha256") == specification["source_sha256"]
            and value.get("protocol_sha256") == specification["protocol_sha256"]
            and type(value.get("independent_fresh_phase_count")) is int
            and value["independent_fresh_phase_count"] == 2
            and value.get("actual_versioned_symbol_streams_verified") is True
            and type(value.get("preserved_version_two_history_process_count")) is int
            and value["preserved_version_two_history_process_count"] == 39,
            "bind the exact discriminated native-build schema and all historical evidence")
    label = checked_label(value.get("label"))
    checked_private_root(value.get("build_root"), family,
                         build=True, build_version=version)
    checked_digest(value.get("archive_sha256"), "actual native-build archive")
    checked_digest(value.get("receipt_sha256"), "actual native-build receipt")
    base = (EVIDENCE_RELATIVE + "/" + specification["evidence_prefix"]
            + family + "-" + label)
    require(value.get("archive_relative") == base + ".json.gz"
            and value.get("receipt_relative") == base + "-publication-receipt.json",
            "never mix V2/V3 evidence paths or relabel a preserved failure")
    return value


def validate_recovery_journal(
    journal: Any, *, arguments: dict[str, Any],
) -> dict[str, Any]:
    family = checked_family(arguments.get("family"))
    version = checked_build_version(arguments.get("build_version"))
    root = checked_private_root(arguments.get("activation_root"), family, build=False)
    require(type(journal) is dict and journal.get("schema") == JOURNAL_SCHEMA
            and journal.get("status") == "PREPARED"
            and journal.get("promotion_mode") == "recoverable-canonical-promotion"
            and journal.get("family") == family
            and journal.get("build_version") == version
            and journal.get("activation_root") == root
            and journal.get("candidate_import_root") == ROOT
            and journal.get("activation_source_sha256")
            == arguments.get("activation_source_sha256")
            and journal.get("activation_protocol_sha256")
            == arguments.get("activation_protocol_sha256")
            and sha256(canonical(journal))
            == arguments.get("recovery_journal_sha256"),
            "authenticate the exact independently pinned pre-replace crash journal")
    require(all(type(journal.get(key)) is type(value)
                and journal.get(key) == value
                for key, value in zero_effects().items()),
            "a crash journal claims candidate, benchmark, network, or clock effects")
    provenance = validate_build_provenance(journal.get("source_build"), family, version)
    require(journal.get("label") == provenance["label"],
            "reject a substituted reportless build label")
    pins = journal.get("owned_source_sha256")
    require(type(pins) is dict and set(pins) == set(FAMILIES[family]["owners"]),
            "require the entire discriminated independent source closure")
    for relative, digest in pins.items():
        checked_relative(relative)
        checked_digest(digest, relative)
    entries = journal.get("backup_entries")
    require(type(entries) is dict and set(entries) == set(FAMILIES[family]["binaries"]),
            "require every exact fixed-role original-byte recovery entry")
    for role, filename in FAMILIES[family]["binaries"].items():
        relative = "candidates/" + filename
        entry = entries[role]
        require(type(entry) is dict and entry.get("role") == role
                and entry.get("target_relative") == relative
                and entry.get("target_path") == ROOT + "/" + relative
                and type(entry.get("originally_present")) is bool,
                "reject foreign, broad, symlinked, or false-typed recovery targets")
        checked_digest(entry.get("promoted_sha256"), relative)
        checked_positive_size(entry.get("promoted_size_bytes"), relative)
        original, backup = entry.get("original_owner"), entry.get("backup")
        if entry["originally_present"]:
            require(type(original) is dict
                    and original.get("relative") == relative
                    and original.get("path") == ROOT + "/" + relative
                    and type(original.get("size_bytes")) is int
                    and 0 < original["size_bytes"] <= MAX_BINARY_BYTES
                    and type(original.get("device")) is int
                    and type(original.get("inode")) is int
                    and type(original.get("mode")) is int
                    and 0 <= original["mode"] <= 0o777,
                    "preserve the exact seven-field prior canonical owner and mode")
            checked_digest(original.get("sha256"), relative)
            require_durable_owner(backup, relative="backups/" + relative,
                                  root=root, directory_sync=False)
            require(backup["sha256"] == original["sha256"]
                    and backup["size_bytes"] == original["size_bytes"],
                    "preserve every original canonical native byte in owner-only backup")
        else:
            require(original is None and backup is None,
                    "never fabricate an original native artifact or recovery backup")
    return {
        "schema": SCHEMA + "-authenticated-recovery-journal", "status": "PASS",
        "family": family, "build_version": version, "activation_root": root,
        "candidate_import_root": ROOT, "source_build": provenance,
        "owned_source_sha256": pins, "backup_entries": entries,
    }


def validate_recorded_elf(family: str, role: str, value: Any) -> dict[str, Any]:
    require(type(value) is dict and value.get("role") == role
            and type(value.get("symbol_records")) is list
            and type(value.get("symbol_count")) is int
            and value["symbol_count"] == len(value["symbol_records"])
            and type(value.get("versioned_symbol_count")) is int
            and type(value.get("exports")) is list
            and type(value.get("undefined")) is list,
            "retain the complete genuine previously verified native symbol records")
    records = value["symbol_records"]
    require(all(type(item) is dict and type(item.get("index")) is int
                and item["index"] == index
                for index, item in enumerate(records)),
            "reject omitted, shifted, reordered, or false GNU dynamic symbols")
    for item in records:
        if item.get("name") is not None:
            name, version, default = checked_symbol_name(item.get("raw_name"))
            require(item.get("name") == name and item.get("version") == version
                    and item.get("default_version") is default,
                    "reject a shifted real GNU eighth-column symbol or version")
    dynamic = {
        "needed": value.get("needed"), "runpath": value.get("runpath"),
        "rpath": [], "soname": value.get("soname"),
    }
    symbols = {
        "exports": value["exports"], "undefined": value["undefined"],
        "symbol_count": value["symbol_count"],
        "versioned_symbol_count": value["versioned_symbol_count"],
        "symbol_records": records,
    }
    require(all(type(dynamic[key]) is list for key in dynamic),
            "reject omitted authentic native dependency ownership")
    observed = validate_elf(family, role, dynamic, symbols)
    require(value == observed,
            "reject forged, external, cross-family, or rewritten full native ELF proof")
    return observed


def validate_activation_documents(
    report: Any, receipt: Any, journal: Any, *, arguments: dict[str, Any],
) -> dict[str, Any]:
    family = checked_family(arguments.get("family"))
    version = checked_build_version(arguments.get("build_version"))
    root = checked_private_root(arguments.get("activation_root"), family, build=False)
    require(type(report) is dict and type(receipt) is dict and type(journal) is dict
            and report.get("schema") == SCHEMA
            and receipt.get("schema") == RECEIPT_SCHEMA
            and journal.get("schema") == JOURNAL_SCHEMA
            and report.get("status") == "PASS"
            and receipt.get("status") == "PASS"
            and receipt.get("activation_status") == "PASS"
            and journal.get("status") == "PREPARED",
            "require the genuine separate canonical report, receipt, and crash journal")
    for document in (report, receipt, journal):
        require(document.get("promotion_mode") == "recoverable-canonical-promotion"
                and document.get("family") == family
                and document.get("build_version") == version
                and document.get("label") == report.get("label")
                and document.get("activation_root") == root
                and document.get("candidate_import_root") == ROOT
                and document.get("activation_source_sha256")
                == arguments.get("activation_source_sha256")
                and document.get("activation_protocol_sha256")
                == arguments.get("activation_protocol_sha256")
                and all(type(document.get(key)) is type(value)
                        and document.get(key) == value
                        for key, value in zero_effects().items()),
                "reject mixed-version activation or candidate/benchmark/timing effects")
    report_raw = canonical(report)
    digest = sha256(report_raw)
    require(digest == arguments.get("activation_report_sha256")
            and receipt.get("report_relative") == REPORT_NAME
            and receipt.get("report_sha256") == digest
            and type(receipt.get("report_bytes")) is int
            and receipt["report_bytes"] == len(report_raw)
            and sha256(canonical(receipt))
            == arguments.get("activation_receipt_sha256")
            and receipt.get("receipt_self_publication") == "NOT CLAIMED",
            "require both separately caller-pinned canonical activation documents")
    publication = require_durable_owner(
        receipt.get("report_publication"), relative=REPORT_NAME,
        root=root, directory_sync=False,
    )
    require(publication["sha256"] == digest
            and publication["size_bytes"] == len(report_raw),
            "authenticate the complete actual durable activation report bytes")
    synchronized = receipt.get("report_directory_fsync")
    require(type(synchronized) is dict and synchronized.get("completed") is True
            and type(synchronized.get("device")) is int
            and type(synchronized.get("inode")) is int and synchronized["inode"] > 0,
            "require an independently synchronized activation-proof directory")
    journal_owner = report.get("recovery_journal")
    require(journal_owner == receipt.get("recovery_journal"),
            "the report and receipt must preserve the identical genuine crash journal")
    require_durable_owner(journal_owner, relative=JOURNAL_NAME,
                          root=root, directory_sync=True)
    journal_raw = canonical(journal)
    require(journal_owner["sha256"] == sha256(journal_raw)
            and journal_owner["size_bytes"] == len(journal_raw),
            "reject a replaced or incomplete original durable crash journal")
    recovery = validate_recovery_journal(journal, arguments={
        "family": family, "build_version": version,
        "activation_root": root,
        "activation_source_sha256": arguments["activation_source_sha256"],
        "activation_protocol_sha256": arguments["activation_protocol_sha256"],
        "recovery_journal_sha256": journal_owner["sha256"],
    })
    provenance = validate_build_provenance(report.get("source_build"), family, version)
    require(provenance == receipt.get("source_build")
            and provenance == journal.get("source_build")
            and recovery["source_build"] == provenance
            and report.get("label") == provenance["label"],
            "reject changed or cross-version genuine activation provenance")
    require(report.get("preserved_version_two") == expected_history_summary()
            and receipt.get("preserved_version_two") == expected_history_summary(),
            "retain all 39 real prior processes and the genuine V2 Zig failure")
    owners = report.get("owned_source_sha256")
    require(type(owners) is dict and set(owners) == set(FAMILIES[family]["owners"])
            and owners == receipt.get("owned_source_sha256")
            and owners == journal.get("owned_source_sha256"),
            "require all unchanged independent source owners in all three proofs")
    frozen = report.get("frozen_support_inputs")
    require(type(frozen) is dict,
            "require the complete immutable dual-version activation prerequisites")
    specification = BUILD_VERSIONS[version]
    for relative, digest_value in (
        ("GOAL.md", GOAL_SHA256), (PHASE1_RELATIVE, PHASE1_SHA256),
        (SOURCE_RELATIVE, arguments["activation_source_sha256"]),
        (PROTOCOL_RELATIVE, arguments["activation_protocol_sha256"]),
        (specification["source_relative"], specification["source_sha256"]),
        (specification["protocol_relative"], specification["protocol_sha256"]),
    ):
        item = frozen.get(relative)
        require(type(item) is dict and item.get("relative") == relative
                and item.get("path") == ROOT + "/" + relative
                and item.get("sha256") == digest_value
                and type(item.get("size_bytes")) is int and item["size_bytes"] > 0
                and type(item.get("device")) is int
                and type(item.get("inode")) is int and item["inode"] > 0,
                "preserve every frozen original and correct version source owner")
    source_records = report.get("source_owners")
    require(type(source_records) is dict and set(source_records) == set(owners)
            and source_records == receipt.get("source_owners"),
            "preserve all actual family source-owner evidence")
    for relative, digest_value in owners.items():
        checked_digest(digest_value, relative)
        owner = source_records[relative]
        require(type(owner) is dict and owner.get("relative") == relative
                and owner.get("path") == ROOT + "/" + relative
                and owner.get("sha256") == digest_value
                and type(owner.get("size_bytes")) is int
                and 0 < owner["size_bytes"] <= MAX_SOURCE_BYTES
                and type(owner.get("device")) is int
                and type(owner.get("inode")) is int and owner["inode"] > 0
                and type(owner.get("mode")) is int
                and 0 <= owner["mode"] <= 0o777,
                "reject an incomplete, rebound, or bool-forged source owner")
    adapter = report.get("adapter")
    adapter_relative = FAMILIES[family]["adapter"]
    require(type(adapter) is dict and adapter.get("module") == FAMILIES[family]["module"]
            and {key: value for key, value in adapter.items() if key != "module"}
            == source_records[adapter_relative],
            "preserve the original canonical independent candidate adapter")
    guards = report.get("original_guard_sources")
    require(type(guards) is dict and set(guards) == set(ORIGINAL_GUARD_SOURCES)
            and guards == receipt.get("original_guard_sources"),
            "retain all actual independently frozen original candidate guard sources")
    for relative, digest_value in ORIGINAL_GUARD_SOURCES.items():
        owner = guards[relative]
        require(type(owner) is dict and owner.get("relative") == relative
                and owner.get("path") == ROOT + "/" + relative
                and owner.get("sha256") == digest_value,
                "never replace, copy, weaken, or rebind an original correctness guard")
    targets, entries = report.get("canonical_targets"), report.get("backup_entries")
    roles = FAMILIES[family]["binaries"]
    require(type(targets) is dict and set(targets) == set(roles)
            and targets == receipt.get("canonical_targets")
            and type(entries) is dict and set(entries) == set(roles)
            and entries == receipt.get("backup_entries")
            and entries == journal.get("backup_entries"),
            "require all genuine canonical native roles and exact recovery backups")
    for role, filename in roles.items():
        relative = "candidates/" + filename
        target = targets[role]
        require(type(target) is dict and target.get("role") == role
                and target.get("relative") == relative
                and target.get("path") == ROOT + "/" + relative
                and type(target.get("size_bytes")) is int
                and 0 < target["size_bytes"] <= MAX_BINARY_BYTES
                and type(target.get("device")) is int
                and type(target.get("inode")) is int and target["inode"] > 0
                and type(target.get("mode")) is int
                and 0 <= target["mode"] <= 0o777
                and all(target.get(flag) is True for flag in PROMOTION_FLAGS),
                "require the exact seven-field atomically promoted native owner")
        checked_digest(target.get("sha256"), relative)
        validate_recorded_elf(family, role, target.get("elf"))
        require_durable_owner(target.get("promotion_intent"),
                              relative="promotion-intent-" + role + ".json",
                              root=root, directory_sync=True)
        phases = target.get("source_build_phases")
        require(type(phases) is list and len(phases) == 2,
                "preserve both actual independently source-built native files")
        for index, phase in enumerate(phases):
            expected_relative = ("reference-a", "reference-b")[index] + "/native/" + filename
            require(type(phase) is dict
                    and phase.get("relative") == expected_relative
                    and phase.get("path") == provenance["build_root"]
                    + "/" + expected_relative
                    and phase.get("sha256") == target["sha256"]
                    and type(phase.get("size_bytes")) is int
                    and phase["size_bytes"] == target["size_bytes"]
                    and type(phase.get("device")) is int
                    and type(phase.get("inode")) is int and phase["inode"] > 0,
                    "reject a copied, stale, missing, or cross-version native phase")
        require((phases[0]["device"], phases[0]["inode"])
                != (phases[1]["device"], phases[1]["inode"]),
                "require two genuinely different source-build output inodes")
        entry = entries[role]
        require(type(entry) is dict and entry.get("role") == role
                and entry.get("target_relative") == relative
                and entry.get("target_path") == ROOT + "/" + relative
                and type(entry.get("originally_present")) is bool
                and entry.get("promoted_sha256") == target["sha256"]
                and entry.get("promoted_size_bytes") == target["size_bytes"],
                "preserve complete honest original native-byte rollback entries")
        if entry["originally_present"]:
            original = entry["original_owner"]
            require(type(original) is dict
                    and target["mode"] == original.get("mode"),
                    "preserve the real original canonical executable permission mode")
            backup = require_durable_owner(entry.get("backup"),
                                           relative="backups/" + relative,
                                           root=root, directory_sync=False)
            require(backup["sha256"] == original.get("sha256")
                    and backup["size_bytes"] == original.get("size_bytes"),
                    "preserve the genuine owner-only exact original-byte backup")
        else:
            require(entry.get("original_owner") is None
                    and entry.get("backup") is None and target["mode"] == 0o755,
                    "record an originally absent native executable honestly")
    return {
        "schema": SCHEMA + "-authenticated-promotion", "status": "PASS",
        "family": family, "build_version": version, "activation_root": root,
        "candidate_import_root": ROOT, "source_build": provenance,
        "canonical_targets": targets, "backup_entries": entries,
        "original_guard_sources": guards,
    }


def restore_journal_targets(
    root: str, journal: dict[str, Any], *,
    promotion_intents: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    family = checked_family(journal.get("family"))
    checked_build_version(journal.get("build_version"))
    checked_private_root(root, family, build=False)
    require(type(journal) is dict and journal.get("schema") == JOURNAL_SCHEMA
            and journal.get("status") == "PREPARED"
            and journal.get("promotion_mode") == "recoverable-canonical-promotion"
            and journal.get("activation_root") == root
            and journal.get("candidate_import_root") == ROOT,
            "require the exact prepared owner-only canonical rollback journal")
    roles = FAMILIES[family]["binaries"]
    entries = journal.get("backup_entries")
    require(type(entries) is dict and set(entries) == set(roles)
            and type(promotion_intents) is dict
            and set(promotion_intents).issubset(roles),
            "authenticate every journaled role before any canonical restoration")
    planned: list[tuple[str, dict[str, Any], str, tuple[bytes, dict[str, Any]] | None,
                         bytes | None]] = []
    for role, filename in reversed(tuple(roles.items())):
        entry = entries[role]
        relative = "candidates/" + filename
        require(type(entry) is dict and entry.get("role") == role
                and entry.get("target_relative") == relative
                and entry.get("target_path") == ROOT + "/" + relative
                and type(entry.get("originally_present")) is bool,
                "reject a missing, cross-family, broad, or user-substituted rollback target")
        current = current_canonical(relative)
        state = classify_recovery_state(entry, current[1] if current else None)
        backup_content: bytes | None = None
        if entry["originally_present"]:
            original, backup = entry.get("original_owner"), entry.get("backup")
            require(type(original) is dict,
                    "preserve the exact original canonical native owner")
            require_durable_owner(backup, relative="backups/" + relative,
                                  root=root, directory_sync=False)
            backup_content, observed = read_owned(
                root, "backups/" + relative, original.get("sha256"),
                maximum=MAX_BINARY_BYTES, exact_size=original.get("size_bytes"),
                private=True,
            )
            require(same_owner(observed, backup),
                    "reject a replaced same-content original backup inode")
        if state == "source-verified-promoted":
            require(current is not None and role in promotion_intents
                    and same_owner(current[1], promotion_intents[role].get("target")),
                    "never restore a promoted inode without its staged durable intent")
        else:
            require(role not in promotion_intents,
                    "reject an irrelevant intention for an unpromoted native role")
        planned.append((role, entry, state, current, backup_content))
    restored: dict[str, Any] = {}
    for role, entry, state, current, backup_content in planned:
        relative = entry["target_relative"]
        if entry["originally_present"]:
            original = entry["original_owner"]
            if state == "already-original":
                require(current is not None and same_owner(current[1], original),
                        "reject changed original native inode during recovery")
                restored[role] = {**current[1], "restored_from_verified_backup": True,
                                  "already_original": True}
                continue
            require(state == "source-verified-promoted" and current is not None
                    and type(backup_content) is bytes,
                    "refuse to overwrite an unrelated changed canonical native file")
            recovered = stage_and_replace(
                relative, backup_content, expected_current=current[1],
                final_mode=original["mode"],
            )
            require(recovered["sha256"] == original["sha256"]
                    and recovered["size_bytes"] == original["size_bytes"]
                    and recovered["mode"] == original["mode"],
                    "restore every genuine original canonical byte and permission mode")
            restored[role] = {**recovered, "restored_from_verified_backup": True}
        elif state == "source-verified-promoted":
            require(current is not None,
                    "an originally absent promoted native inode disappeared")
            root_descriptor, candidate_descriptor = canonical_candidate_directory()
            try:
                filename = relative.split("/", 1)[1]
                observed = os.stat(filename, dir_fd=candidate_descriptor,
                                   follow_symlinks=False)
                require(stat.S_ISREG(observed.st_mode)
                        and (observed.st_dev, observed.st_ino)
                        == (current[1]["device"], current[1]["inode"]),
                        "never remove a substituted user-owned native inode")
                os.unlink(filename, dir_fd=candidate_descriptor)
                os.fsync(candidate_descriptor)
            finally:
                os.close(candidate_descriptor)
                os.close(root_descriptor)
            require(current_canonical(relative) is None,
                    "the genuinely originally absent native target was not restored")
            restored[role] = {
                "relative": relative, "path": ROOT + "/" + relative,
                "restored_original_absence": True,
                "candidate_directory_fsync_completed": True,
            }
        else:
            require(state == "originally-absent" and current is None,
                    "refuse to delete an unjournaled canonical user artifact")
            restored[role] = {
                "relative": relative, "path": ROOT + "/" + relative,
                "restored_original_absence": True,
                "candidate_directory_fsync_completed": True,
            }
    return restored


def activate(arguments: dict[str, Any]) -> dict[str, Any]:
    prerequisite = authenticate_prerequisites(arguments)
    family, version = prerequisite["family"], prerequisite["build_version"]
    provenance = build_provenance(prerequisite, arguments)
    validate_build_provenance(provenance, family, version)
    root = tempfile.mkdtemp(prefix=PRIVATE_PREFIX + family + "-", dir="/tmp")
    checked_private_root(root, family, build=False)
    descriptor = open_root(root, private=True)
    os.close(descriptor)
    journal, journal_owner = prepare_recovery_journal(
        root, prerequisite, arguments, provenance,
    )
    try:
        targets: dict[str, dict[str, Any]] = {}
        for role, output in prerequisite["native_outputs"].items():
            entry = journal["backup_entries"][role]
            final_mode = (entry["original_owner"]["mode"]
                          if entry["originally_present"] else 0o755)
            promoted = stage_and_replace(
                entry["target_relative"], prerequisite["native_bytes"][role],
                expected_current=entry["original_owner"], final_mode=final_mode,
                promotion_intent={
                    "family": family, "build_version": version,
                    "activation_root": root, "role": role,
                    "recovery_journal_sha256": journal_owner["sha256"],
                },
            )
            require(promoted["sha256"] == output["sha256"]
                    and promoted["size_bytes"] == output["size_bytes"]
                    and promoted["mode"] == final_mode,
                    "promote only genuine source-built bytes in the original native mode")
            targets[role] = {
                **promoted, "role": role, "elf": output["elf"],
                "source_build_phases": prerequisite["native_phase_evidence"][role],
            }
        for target in targets.values():
            _, observed = read_owned(
                ROOT, target["relative"], target["sha256"],
                maximum=MAX_BINARY_BYTES, exact_size=target["size_bytes"],
            )
            require(same_owner(observed, target),
                    "a promoted source-built native inode changed before publication")
        for relative, digest in prerequisite["owned_source_sha256"].items():
            _, owner = read_owned(ROOT, relative, digest, maximum=MAX_SOURCE_BYTES)
            require(same_owner(owner, prerequisite["source_evidence"][relative]),
                    "an independent family source changed during canonical promotion")
        report = {
            "schema": SCHEMA, "status": "PASS",
            "promotion_mode": "recoverable-canonical-promotion",
            "family": family, "build_version": version,
            "label": prerequisite["label"], "activation_root": root,
            "candidate_import_root": ROOT,
            "activation_source_sha256": arguments["activation_source_sha256"],
            "activation_protocol_sha256": arguments["activation_protocol_sha256"],
            "source_build": provenance,
            "preserved_version_two": prerequisite["preserved_version_two"],
            "owned_source_sha256": prerequisite["owned_source_sha256"],
            "source_owners": prerequisite["source_evidence"],
            "adapter": {
                **prerequisite["source_evidence"][FAMILIES[family]["adapter"]],
                "module": FAMILIES[family]["module"],
            },
            "canonical_targets": targets,
            "backup_entries": journal["backup_entries"],
            "recovery_journal": journal_owner,
            "original_guard_sources": prerequisite["guard_evidence"],
            "frozen_support_inputs": prerequisite["frozen_support"],
            **zero_effects(),
        }
        report_record = write_fresh(root, REPORT_NAME, canonical(report))
        report_directory = synchronize_directory(root)
        receipt = {
            "schema": RECEIPT_SCHEMA, "status": "PASS",
            "activation_status": "PASS",
            "promotion_mode": "recoverable-canonical-promotion",
            "family": family, "build_version": version,
            "label": prerequisite["label"], "activation_root": root,
            "candidate_import_root": ROOT,
            "activation_source_sha256": arguments["activation_source_sha256"],
            "activation_protocol_sha256": arguments["activation_protocol_sha256"],
            "source_build": provenance,
            "preserved_version_two": prerequisite["preserved_version_two"],
            "owned_source_sha256": prerequisite["owned_source_sha256"],
            "report_relative": REPORT_NAME,
            "report_sha256": report_record["sha256"],
            "report_bytes": report_record["size_bytes"],
            "report_publication": report_record,
            "report_directory_fsync": report_directory,
            "source_owners": prerequisite["source_evidence"],
            "canonical_targets": targets,
            "backup_entries": journal["backup_entries"],
            "recovery_journal": journal_owner,
            "original_guard_sources": prerequisite["guard_evidence"],
            "receipt_self_publication": "NOT CLAIMED",
            **zero_effects(),
        }
        receipt_record = write_fresh(root, RECEIPT_NAME, canonical(receipt))
        receipt_directory = synchronize_directory(root)
        validation_arguments = {
            "family": family, "build_version": version, "activation_root": root,
            "activation_source_sha256": arguments["activation_source_sha256"],
            "activation_protocol_sha256": arguments["activation_protocol_sha256"],
            "activation_report_sha256": report_record["sha256"],
            "activation_receipt_sha256": receipt_record["sha256"],
        }
        proved = validate_activation_documents(
            report, receipt, journal, arguments=validation_arguments,
        )
        intentions = authenticate_promotion_intents(
            root, journal, journal_owner["sha256"],
            announced_targets=proved["canonical_targets"],
        )
        require(set(intentions) == set(targets),
                "independently prove every full rich durable role before success")
    except BaseException as error:
        try:
            intentions = authenticate_promotion_intents(
                root, journal, journal_owner["sha256"],
            )
            restore_journal_targets(root, journal, promotion_intents=intentions)
        except BaseException as recovery_error:
            raise ActivationError(
                "canonical promotion failed and crash recovery requires the retained "
                + root + "/" + JOURNAL_NAME + ": " + str(recovery_error)
            ) from error
        raise ActivationError(
            "canonical promotion failed; all exact previous native bytes and modes "
            "were restored using " + root + "/" + JOURNAL_NAME
        ) from error
    return {
        "schema": SCHEMA + "-activation-result", "status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family, "build_version": version, "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_source_sha256": arguments["activation_source_sha256"],
        "activation_protocol_sha256": arguments["activation_protocol_sha256"],
        "activation_report_relative": REPORT_NAME,
        "activation_report_sha256": report_record["sha256"],
        "activation_receipt_relative": RECEIPT_NAME,
        "activation_receipt_sha256": receipt_record["sha256"],
        "recovery_journal_relative": JOURNAL_NAME,
        "recovery_journal_sha256": journal_owner["sha256"],
        "receipt_directory_fsync": receipt_directory,
        "source_build": provenance,
        **zero_effects(),
    }


def reauthenticate_journal_build(
    journal: dict[str, Any], arguments: dict[str, Any],
) -> dict[str, Any]:
    checked = validate_recovery_journal(journal, arguments=arguments)
    provenance = checked["source_build"]
    family = checked["family"]
    entries = checked["backup_entries"]
    engine = "extension" if family == "c" else "engine"
    bridge = "extension" if family == "c" else "bridge"
    options = {
        "mode": "activate", "family": family,
        "build_version": checked["build_version"],
        "build_label": provenance["label"],
        "build_root": provenance["build_root"],
        "activation_source_sha256": arguments["activation_source_sha256"],
        "activation_protocol_sha256": arguments["activation_protocol_sha256"],
        "build_source_sha256": provenance["source_sha256"],
        "build_protocol_sha256": provenance["protocol_sha256"],
        "build_report_sha256": provenance["archive_sha256"],
        "build_receipt_sha256": provenance["receipt_sha256"],
        "native_engine_sha256": entries[engine]["promoted_sha256"],
        "native_bridge_sha256": entries[bridge]["promoted_sha256"],
        "native_engine_bytes": entries[engine]["promoted_size_bytes"],
        "native_bridge_bytes": entries[bridge]["promoted_size_bytes"],
        "owned_source_sha256": [
            relative + "=" + digest
            for relative, digest in sorted(checked["owned_source_sha256"].items())
        ],
    }
    proof = authenticate_prerequisites(options)
    for role, output in proof["native_outputs"].items():
        entry = entries[role]
        require(entry["promoted_sha256"] == output["sha256"]
                and entry["promoted_size_bytes"] == output["size_bytes"],
                "reject recovery of a non-source-built or cross-version native role")
    return proof


def restore(arguments: dict[str, Any]) -> dict[str, Any]:
    require_isolated_interpreter()
    family = checked_family(arguments["family"])
    version = checked_build_version(arguments["build_version"])
    root = checked_private_root(arguments["activation_root"], family, build=False)
    report_raw, report_owner = read_owned(
        root, REPORT_NAME, arguments["activation_report_sha256"],
        maximum=MAX_REPORT_BYTES, private=True,
    )
    receipt_raw, receipt_owner = read_owned(
        root, RECEIPT_NAME, arguments["activation_receipt_sha256"],
        maximum=MAX_REPORT_BYTES, private=True,
    )
    require(report_owner["mode"] == 0o600 and receipt_owner["mode"] == 0o600,
            "require actual owner-only canonical report and independent receipt")
    report = decode_document(report_raw, "actual dual-version activation report")
    receipt = decode_document(receipt_raw, "actual dual-version activation receipt")
    recorded = report.get("recovery_journal")
    require_durable_owner(recorded, relative=JOURNAL_NAME,
                          root=root, directory_sync=True)
    journal_raw, journal_owner = read_owned(
        root, JOURNAL_NAME, recorded["sha256"], maximum=MAX_REPORT_BYTES,
        exact_size=recorded["size_bytes"], private=True,
    )
    require(same_owner(journal_owner, recorded),
            "reject replacing a genuine durable crash-journal inode")
    journal = decode_document(journal_raw, "actual versioned crash-recovery journal")
    proved = validate_activation_documents(
        report, receipt, journal, arguments=arguments,
    )
    recovery_arguments = {
        "family": family, "build_version": version, "activation_root": root,
        "activation_source_sha256": arguments["activation_source_sha256"],
        "activation_protocol_sha256": arguments["activation_protocol_sha256"],
        "recovery_journal_sha256": journal_owner["sha256"],
    }
    proof = reauthenticate_journal_build(journal, recovery_arguments)
    for relative, owner in proof["source_evidence"].items():
        require(same_owner(owner, report["source_owners"][relative]),
                "reject a candidate source replaced before original-byte restoration")
    for relative, owner in proof["guard_evidence"].items():
        require(same_owner(owner, report["original_guard_sources"][relative]),
                "reject a changed immutable original suite guard during restoration")
    intentions = authenticate_promotion_intents(
        root, journal, journal_owner["sha256"],
        announced_targets=proved["canonical_targets"],
    )
    require(set(intentions) == set(proved["canonical_targets"]),
            "require every rich originally published durable promotion intention")
    restored = restore_journal_targets(root, journal, promotion_intents=intentions)
    document = {
        "schema": SCHEMA + "-restoration-receipt", "status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family, "build_version": version, "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_report_sha256": arguments["activation_report_sha256"],
        "activation_receipt_sha256": arguments["activation_receipt_sha256"],
        "recovery_journal_sha256": journal_owner["sha256"],
        "source_build": proved["source_build"], "restored_targets": restored,
        **zero_effects(),
    }
    owner = write_fresh(root, "restoration-receipt.json", canonical(document))
    directory = synchronize_directory(root)
    return {
        "schema": SCHEMA + "-restoration-result", "status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family, "build_version": version, "activation_root": root,
        "candidate_import_root": ROOT,
        "restoration_receipt_relative": "restoration-receipt.json",
        "restoration_receipt_sha256": owner["sha256"],
        "receipt_directory_fsync": directory,
        **zero_effects(),
    }


def recover(arguments: dict[str, Any]) -> dict[str, Any]:
    require_isolated_interpreter()
    family = checked_family(arguments["family"])
    version = checked_build_version(arguments["build_version"])
    root = checked_private_root(arguments["activation_root"], family, build=False)
    raw, journal_owner = read_owned(
        root, JOURNAL_NAME, arguments["recovery_journal_sha256"],
        maximum=MAX_REPORT_BYTES, private=True,
    )
    require(journal_owner["mode"] == 0o600,
            "require the actual owner-only reportless pre-promotion journal")
    journal = decode_document(raw, "actual reportless durable crash journal")
    checked = validate_recovery_journal(journal, arguments=arguments)
    proof = reauthenticate_journal_build(journal, arguments)
    intentions = authenticate_promotion_intents(
        root, journal, journal_owner["sha256"],
    )
    restored = restore_journal_targets(root, journal, promotion_intents=intentions)
    document = {
        "schema": SCHEMA + "-restoration-receipt", "status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "recovery_mode": "reportless-pinned-prepromotion-journal",
        "family": family, "build_version": version,
        "label": checked["source_build"]["label"], "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_source_sha256": arguments["activation_source_sha256"],
        "activation_protocol_sha256": arguments["activation_protocol_sha256"],
        "recovery_journal_sha256": journal_owner["sha256"],
        "source_build": checked["source_build"],
        "owned_source_sha256": checked["owned_source_sha256"],
        "source_owners": proof["source_evidence"],
        "original_guard_sources": proof["guard_evidence"],
        "restored_targets": restored,
        **zero_effects(),
    }
    owner = write_fresh(root, "restoration-receipt.json", canonical(document))
    directory = synchronize_directory(root)
    return {
        "schema": SCHEMA + "-reportless-recovery-result", "status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "recovery_mode": "reportless-pinned-prepromotion-journal",
        "family": family, "build_version": version, "activation_root": root,
        "candidate_import_root": ROOT,
        "recovery_journal_sha256": journal_owner["sha256"],
        "restoration_receipt_relative": "restoration-receipt.json",
        "restoration_receipt_sha256": owner["sha256"],
        "receipt_directory_fsync": directory,
        **zero_effects(),
    }


class BlockedEnvironment:
    """Fail closed on synthetic environment reads and modifications."""

    def __init__(self, denied: Any) -> None:
        self.denied = denied

    def __getitem__(self, key: Any) -> Any:
        return self.denied(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        self.denied(key, value)

    def __contains__(self, key: Any) -> bool:
        self.denied(key)
        return False

    def __iter__(self) -> Any:
        return self.denied()

    def get(self, *args: Any, **kwargs: Any) -> Any:
        return self.denied(*args, **kwargs)

    def keys(self) -> Any:
        return self.denied()


class SyntheticSandbox:
    """Make every source-only filesystem and outside-process effect impossible."""

    def __init__(self) -> None:
        self.previous: list[tuple[Any, str, Any]] = []
        self.blocked = {
            "filesystem": 0, "process": 0, "thread": 0, "clock": 0,
            "network": 0, "environment": 0, "import": 0,
        }

    def deny(self, category: str) -> Any:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            self.blocked[category] += 1
            raise SourceOnlyEffect("synthetic activation cannot access " + category)
        return blocked

    def install(self, owner: Any, name: str, replacement: Any) -> None:
        if hasattr(owner, name):
            self.previous.append((owner, name, getattr(owner, name)))
            setattr(owner, name, replacement)

    def __enter__(self) -> SyntheticSandbox:
        filesystem, process = self.deny("filesystem"), self.deny("process")
        thread, clock = self.deny("thread"), self.deny("clock")
        network, environment = self.deny("network"), self.deny("environment")
        importer = self.deny("import")
        self.install(builtins, "open", filesystem)
        self.install(io, "open", filesystem)
        for name in (
            "open", "read", "write", "stat", "lstat", "scandir", "listdir", "walk",
            "mkdir", "makedirs", "rename", "replace", "remove", "unlink", "fsync",
            "fdatasync", "chmod", "fchmod", "fdopen", "system", "popen",
        ):
            self.install(os, name, process if name in {"system", "popen"} else filesystem)
        for name in ("mkdtemp", "mkstemp", "NamedTemporaryFile", "TemporaryDirectory"):
            self.install(tempfile, name, filesystem)
        for name in ("run", "Popen", "call", "check_call", "check_output"):
            self.install(subprocess, name, process)
        self.install(threading.Thread, "start", thread)
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
            "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
            "thread_time_ns", "sleep",
        ):
            self.install(time, name, clock)
        for name in ("socket", "create_connection", "getaddrinfo"):
            self.install(socket, name, network)
        for name in ("getenv", "getenvb", "putenv", "unsetenv"):
            self.install(os, name, environment)
        self.install(os, "environ", BlockedEnvironment(environment))
        if hasattr(os, "environb"):
            self.install(os, "environb", BlockedEnvironment(environment))
        self.install(importlib, "import_module", importer)
        self.install(builtins, "__import__", importer)
        return self

    def __exit__(self, kind: Any, error: Any, trace: Any) -> bool:
        for owner, name, previous in reversed(self.previous):
            setattr(owner, name, previous)
        self.previous.clear()
        return False


def synthetic_digest(label: str) -> str:
    return sha256(("verified-native-activation-v2:" + label).encode("ascii"))


def synthetic_dynamic(family: str, role: str) -> bytes:
    lines = ["Dynamic section at offset 0 contains 3 entries:"]
    if role == "engine":
        lines.append(" 0x000000000000000e (SONAME) Library soname: ["
                     + FAMILIES[family]["binaries"][role] + "]")
    if role == "bridge":
        lines.append(" 0x0000000000000001 (NEEDED) Shared library: ["
                     + FAMILIES[family]["binaries"]["engine"] + "]")
        lines.append(" 0x000000000000001d (RUNPATH) Library runpath: [$ORIGIN]")
    lines.append(" 0x0000000000000001 (NEEDED) Shared library: [libc.so.6]")
    return ("\n".join(lines) + "\n").encode("ascii")


def synthetic_symbols(family: str, role: str) -> bytes:
    if family == "c":
        exports = ["PyInit__vm_native"]
        native: list[str] = []
    elif role == "engine":
        exports = sorted(RUST_ENGINE_EXPORTS if family == "rust" else ZIG_ENGINE_EXPORTS)
        native = []
    else:
        exports = ["PyInit__" + family + "_bridge"]
        native = ["rebar_compile" if family == "rust" else "rebar_zig_compile"]
    undefined = ["__stack_chk_fail@GLIBC_2.4", *native]
    lines = [
        "Symbol table '.dynsym' contains "
        + str(1 + len(exports) + len(undefined)) + " entries:",
        "   Num: Value Size Type Bind Vis Ndx Name",
        "   0: 0000000000000000 0 NOTYPE LOCAL DEFAULT UND",
    ]
    index = 1
    for name in exports:
        lines.append("   " + str(index)
                     + ": 0000000000000010 1 FUNC GLOBAL DEFAULT 1 " + name)
        index += 1
    for name in undefined:
        lines.append("   " + str(index)
                     + ": 0000000000000000 0 FUNC GLOBAL DEFAULT UND "
                     + name + (" (2)" if "@" in name else ""))
        index += 1
    return ("\n".join(lines) + "\n").encode("ascii")


def synthetic_process(
    family: str, version: str, name: str, phase: str, pid: int,
) -> dict[str, Any]:
    command = planned_commands(family, phase, version)[name]
    if name.endswith("_dynamic"):
        stdout = synthetic_dynamic(family, name.rsplit("_", 1)[0])
    elif name.endswith("_symbols"):
        stdout = synthetic_symbols(family, name.rsplit("_", 1)[0])
    elif name == "zig_version":
        stdout = b"0.16.0\n"
    elif name == "cargo_version":
        stdout = b"cargo 1.95.0 (f2d3ce0bd synthetic)\n"
    elif name == "rustc_version":
        stdout = b"rustc 1.95.0 synthetic\n"
    else:
        stdout = b"genuine-synthetic-pinned-process\n"
    stderr = b""
    return {
        "name": name, "argv": command,
        "environment": expected_environment(family, phase),
        "shell": False, "pid": pid, "exit_status": 0,
        "stdout_base64": base64.b64encode(stdout).decode("ascii"),
        "stdout_sha256": sha256(stdout), "stdout_bytes": len(stdout),
        "stderr_base64": base64.b64encode(stderr).decode("ascii"),
        "stderr_sha256": sha256(stderr), "stderr_bytes": len(stderr),
    }


def synthetic_build_fixture(
    family: str, version: str,
) -> tuple[dict[str, Any], dict[str, Any], bytes, dict[str, Any], dict[str, str]]:
    family, version = checked_family(family), checked_build_version(version)
    specification = BUILD_VERSIONS[version]
    label = "synthetic-v" + version
    pins = dict(sorted((name, synthetic_digest(version + ":" + family + ":" + name))
                       for name in FAMILIES[family]["owners"]))
    snapshots = {
        relative: {"path": ROOT + "/" + relative, "sha256": digest,
                   "size_bytes": 123 + index, "device": 71, "inode": 1001 + index}
        for index, (relative, digest) in enumerate(pins.items())
    }
    support_values = {
        "immutable_objective": (ROOT + "/GOAL.md", GOAL_SHA256),
        "complete_correctness_manifest": (ROOT + "/" + PHASE1_RELATIVE, PHASE1_SHA256),
        "pinned_cpython_executable": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
        "native_build_recorder":
            (ROOT + "/" + specification["source_relative"], specification["source_sha256"]),
        "native_build_protocol":
            (ROOT + "/" + specification["protocol_relative"], specification["protocol_sha256"]),
    }
    if version == "3":
        for name in (
            "preserved_v2_build_source", "preserved_v2_build_protocol",
            "preserved_v2_c_archive", "preserved_v2_c_receipt",
            "preserved_v2_rust_archive", "preserved_v2_rust_receipt",
            "preserved_v2_zig_archive", "preserved_v2_zig_receipt",
        ):
            support_values[name] = (ROOT + "/synthetic/" + name,
                                    synthetic_digest(name))
        if family == "zig":
            for name in ("pinned_official_zig_0_16_0_lock",
                         "pinned_official_zig_0_16_0_archive",
                         "pinned_official_zig_0_16_0_compiler"):
                support_values[name] = (ROOT + "/synthetic/" + name,
                                        synthetic_digest(name))
    support = {
        name: {"path": path, "sha256": digest, "size_bytes": 123,
               "device": 81, "inode": 7000 + index}
        for index, (name, (path, digest)) in enumerate(support_values.items())
    }
    audits = []
    for relative in pins:
        if relative.endswith((".py", ".c", ".rs", ".zig")):
            record: dict[str, Any] = {
                "path": relative, "external_regex_dependency_count": 0,
            }
            if relative.endswith(".py"):
                record["cross_family_dependency_count"] = 0
            audits.append(record)
    cargo = (
        {"package": "rebar-rust-continuation", "package_count": 1,
         "external_package_count": 0, "registry_count": 0,
         "build_script_count": 0, "locked": True, "offline": True}
        if family == "rust" else None
    )
    processes = [
        synthetic_process(family, version, name, phase, 20_000 + index)
        for index, (name, phase) in enumerate(expected_process_schedule(family))
    ]
    phases: list[dict[str, Any]] = []
    reproduced: dict[str, dict[str, Any]] = {}
    for phase in ("reference-a", "reference-b"):
        prefix = SANITIZED_BUILD_ROOT + "/" + phase
        copies = {
            relative: {"path": prefix + "/source/" + relative, "sha256": digest,
                       "bytes": 123 + index, "exclusive_creation": True,
                       "same_inode_readback_verified": True,
                       "file_fsync_completed": False, "write_calls": 1}
            for index, (relative, digest) in enumerate(pins.items())
        }
        outputs: dict[str, dict[str, Any]] = {}
        for role, filename in FAMILIES[family]["binaries"].items():
            digest = synthetic_digest(version + ":" + family + ":native:" + role)
            elf = validate_elf(family, role,
                               parse_dynamic(synthetic_dynamic(family, role)),
                               parse_symbols(synthetic_symbols(family, role)))
            outputs[role] = {
                "family": family, "role": role, "file_name": filename,
                "path": prefix + "/native/" + filename,
                "sha256": digest, "size_bytes": 9876,
                "elf": elf, "prebuilt_binary_read": False,
                "candidate_imported": False,
            }
            reproduced[role] = {
                "file_name": filename, "sha256": digest, "size_bytes": 9876,
                "reproduced_in_two_fresh_directories": True, "elf": elf,
            }
        phases.append({
            "name": phase, "fresh_source_directory": prefix + "/source",
            "fresh_native_directory": prefix + "/native",
            "copied_source_owners": copies, "native_outputs": outputs,
            "candidate_processes_started": 0, "candidate_imports": 0,
            "native_libraries_loaded": 0, "timing_trials_run": 0,
            "hidden_cases_read": 0,
        })
    history = {
        "status": "AUTHENTIC HISTORICAL BUILD; V1 SYMBOL AUDIT FALSIFIED",
        "real_versioned_symbol_count_per_phase": 9,
        "observed_v1_parser_false_symbols": ["(2)", "(3)", "(4)", "(5)", "(6)"],
    }
    report: dict[str, Any] = {
        "schema": specification["schema"], "status": "PASS", "family": family,
        "label": label, "source_sha256": specification["source_sha256"],
        "protocol_sha256": specification["protocol_sha256"],
        "phase1": {"status": "PASS", "suite_count": 13,
                   "case_execution_count": 31_237,
                   "candidate_correctness": "NOT MEASURED",
                   "performance": "NOT MEASURED",
                   "final_holdout_authorized": False},
        "historical_v1_c": history,
        "frozen_support_inputs": support,
        "frozen_support_inputs_after": copy.deepcopy(support),
        "owned_source_sha256": pins,
        "owned_source_before": snapshots,
        "owned_source_after": copy.deepcopy(snapshots),
        "source_independence_audit": {
            "source_audits": audits, "source_owner_count": len(pins),
            "external_regex_package_count": 0,
            "cross_family_dependency_count": 0,
            "cargo_dependency_closure": cargo,
        },
        "fresh_private_root": SANITIZED_BUILD_ROOT,
        "build_phases": phases, "processes": processes,
        "reproducibility": {
            "independent_fresh_phase_count": 2, "byte_identical": True,
            "native_outputs": reproduced, "prebuilt_binary_count": 0,
            "native_libraries_loaded": 0,
        },
        "error": None,
        **zero_effects(),
    }
    if version == "3":
        report["preserved_version_two"] = expected_history_summary()
    plain = canonical(report)
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    archive_relative = (EVIDENCE_RELATIVE + "/" + specification["evidence_prefix"]
                        + family + "-" + label + ".json.gz")
    receipt = {
        "schema": specification["schema"] + "-durable-publication-receipt",
        "status": "PASS", "build_status": "PASS",
        "family": family, "label": label,
        "source_sha256": specification["source_sha256"],
        "protocol_sha256": specification["protocol_sha256"],
        "phase1_manifest_sha256": PHASE1_SHA256,
        "archive_relative": archive_relative,
        "archive_sha256": sha256(archive), "archive_bytes": len(archive),
        "uncompressed_sha256": sha256(plain), "uncompressed_bytes": len(plain),
        "archive_publication": {
            "path": ROOT + "/" + archive_relative,
            "sha256": sha256(archive), "bytes": len(archive),
            "exclusive_creation": True, "same_inode_readback_verified": True,
            "file_fsync_completed": True, "write_calls": 1,
        },
        "archive_directory_fsync": {"completed": True, "device": 71, "inode": 888},
        "owned_source_sha256": pins,
        "candidate_processes_started": 0, "candidate_imports": 0,
        "native_libraries_loaded": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "candidate_correctness": "NOT MEASURED", "winner_selected": False,
        "receipt_self_publication": "NOT CLAIMED",
    }
    engine = "extension" if family == "c" else "engine"
    bridge = "extension" if family == "c" else "bridge"
    arguments = {
        "mode": "activate", "family": family, "build_version": version,
        "build_label": label,
        "build_root": "/tmp/" + specification["private_prefix"] + family + "-synthetic",
        "activation_source_sha256": synthetic_digest("activation-source"),
        "activation_protocol_sha256": synthetic_digest("activation-protocol"),
        "build_source_sha256": specification["source_sha256"],
        "build_protocol_sha256": specification["protocol_sha256"],
        "build_report_sha256": sha256(archive),
        "build_receipt_sha256": sha256(canonical(receipt)),
        "native_engine_sha256": reproduced[engine]["sha256"],
        "native_bridge_sha256": reproduced[bridge]["sha256"],
        "native_engine_bytes": reproduced[engine]["size_bytes"],
        "native_bridge_bytes": reproduced[bridge]["size_bytes"],
        "owned_source_sha256": [relative + "=" + digest
                                for relative, digest in pins.items()],
    }
    return report, receipt, archive, arguments, pins


def synthetic_owner(
    relative: str, digest: str, *, root: str, size: int, inode: int,
    mode: int, durable: bool = False, directory_sync: bool = False,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "relative": relative, "path": root + "/" + relative,
        "sha256": digest, "size_bytes": size,
        "device": 71 if root == ROOT else 83,
        "inode": inode, "mode": mode,
    }
    if durable:
        result.update({
            "exclusive_creation": True, "same_inode_readback_verified": True,
            "file_fsync_completed": True, "write_calls": 1,
        })
        if directory_sync:
            result["directory_fsync_completed"] = True
    return result


def synthetic_activation_fixture(
    family: str, version: str, *, absent_role: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    build_report, build_receipt, archive, build_arguments, pins = (
        synthetic_build_fixture(family, version)
    )
    outputs = validate_build_report(build_report, build_receipt, archive,
                                    build_arguments, pins)
    root = "/tmp/" + PRIVATE_PREFIX + family + "-synthetic"
    specification = BUILD_VERSIONS[version]
    provenance = {
        "build_version": version, "schema": specification["schema"],
        "family": family, "label": build_arguments["build_label"],
        "source_sha256": specification["source_sha256"],
        "protocol_sha256": specification["protocol_sha256"],
        "archive_relative": build_receipt["archive_relative"],
        "archive_sha256": sha256(archive),
        "receipt_relative": (EVIDENCE_RELATIVE + "/"
                              + specification["evidence_prefix"] + family + "-"
                              + build_arguments["build_label"]
                              + "-publication-receipt.json"),
        "receipt_sha256": sha256(canonical(build_receipt)),
        "build_root": build_arguments["build_root"],
        "independent_fresh_phase_count": 2,
        "actual_versioned_symbol_streams_verified": True,
        "preserved_version_two_history_process_count": 39,
    }
    sources = {
        relative: synthetic_owner(
            relative, digest, root=ROOT, size=123 + index,
            inode=1001 + index, mode=0o644,
        )
        for index, (relative, digest) in enumerate(pins.items())
    }
    guards = {
        relative: synthetic_owner(
            relative, digest, root=ROOT, size=456 + index,
            inode=4001 + index, mode=0o644,
        )
        for index, (relative, digest) in enumerate(sorted(ORIGINAL_GUARD_SOURCES.items()))
    }
    frozen_specs = (
        ("GOAL.md", GOAL_SHA256), (PHASE1_RELATIVE, PHASE1_SHA256),
        (SOURCE_RELATIVE, build_arguments["activation_source_sha256"]),
        (PROTOCOL_RELATIVE, build_arguments["activation_protocol_sha256"]),
        (specification["source_relative"], specification["source_sha256"]),
        (specification["protocol_relative"], specification["protocol_sha256"]),
    )
    frozen = {
        relative: synthetic_owner(relative, digest, root=ROOT,
                                  size=321 + index, inode=6001 + index, mode=0o644)
        for index, (relative, digest) in enumerate(frozen_specs)
    }
    entries: dict[str, dict[str, Any]] = {}
    targets: dict[str, dict[str, Any]] = {}
    for index, (role, filename) in enumerate(FAMILIES[family]["binaries"].items()):
        relative = "candidates/" + filename
        observed = outputs[role]
        present = role != absent_role
        original_mode = 0o700 if family == "zig" and present else 0o755
        original = (
            synthetic_owner(relative, synthetic_digest(family + ":old:" + role),
                            root=ROOT, size=6543 + index,
                            inode=3001 + index, mode=original_mode)
            if present else None
        )
        backup = (
            synthetic_owner("backups/" + relative, original["sha256"], root=root,
                            size=original["size_bytes"], inode=3501 + index,
                            mode=0o600, durable=True)
            if original is not None else None
        )
        entries[role] = {
            "role": role, "target_relative": relative,
            "target_path": ROOT + "/" + relative,
            "originally_present": present, "original_owner": original,
            "backup": backup, "promoted_sha256": observed["sha256"],
            "promoted_size_bytes": observed["size_bytes"],
        }
        target = synthetic_owner(
            relative, observed["sha256"], root=ROOT,
            size=observed["size_bytes"], inode=9001 + index,
            mode=original_mode,
        )
        target.update({
            "role": role, "atomic_replace_completed": True,
            "adjacent_exclusive_stage_verified": True,
            "candidate_directory_fsync_completed": True,
            "elf": observed["elf"],
            "source_build_phases": [
                synthetic_owner(
                    phase + "/native/" + filename, observed["sha256"],
                    root=build_arguments["build_root"],
                    size=observed["size_bytes"], inode=7001 + 2 * index + position,
                    mode=0o700,
                )
                for position, phase in enumerate(("reference-a", "reference-b"))
            ],
        })
        targets[role] = target
    journal = {
        "schema": JOURNAL_SCHEMA, "status": "PREPARED",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family, "build_version": version,
        "label": build_arguments["build_label"], "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_source_sha256": build_arguments["activation_source_sha256"],
        "activation_protocol_sha256": build_arguments["activation_protocol_sha256"],
        "source_build": provenance, "owned_source_sha256": pins,
        "backup_entries": entries,
        **zero_effects(),
    }
    journal_raw = canonical(journal)
    journal_owner = synthetic_owner(
        JOURNAL_NAME, sha256(journal_raw), root=root, size=len(journal_raw),
        inode=9991, mode=0o600, durable=True, directory_sync=True,
    )
    for index, (role, target) in enumerate(targets.items()):
        intended = {
            "schema": INTENT_SCHEMA, "status": "PREPARED",
            "promotion_mode": "recoverable-canonical-promotion",
            "family": family, "build_version": version, "activation_root": root,
            "candidate_import_root": ROOT,
            "recovery_journal_sha256": journal_owner["sha256"],
            "role": role, "target": {key: target[key] for key in OWNER_FIELDS},
            **zero_effects(),
        }
        raw = canonical(intended)
        target["promotion_intent"] = synthetic_owner(
            "promotion-intent-" + role + ".json", sha256(raw),
            root=root, size=len(raw), inode=9501 + index, mode=0o600,
            durable=True, directory_sync=True,
        )
    report = {
        "schema": SCHEMA, "status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family, "build_version": version,
        "label": build_arguments["build_label"], "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_source_sha256": build_arguments["activation_source_sha256"],
        "activation_protocol_sha256": build_arguments["activation_protocol_sha256"],
        "source_build": provenance, "preserved_version_two": expected_history_summary(),
        "owned_source_sha256": pins, "source_owners": sources,
        "adapter": {**sources[FAMILIES[family]["adapter"]],
                    "module": FAMILIES[family]["module"]},
        "canonical_targets": targets, "backup_entries": entries,
        "recovery_journal": journal_owner, "original_guard_sources": guards,
        "frozen_support_inputs": frozen,
        **zero_effects(),
    }
    report_raw = canonical(report)
    report_owner = synthetic_owner(
        REPORT_NAME, sha256(report_raw), root=root,
        size=len(report_raw), inode=9992, mode=0o600, durable=True,
    )
    receipt = {
        "schema": RECEIPT_SCHEMA, "status": "PASS", "activation_status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family, "build_version": version,
        "label": build_arguments["build_label"], "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_source_sha256": build_arguments["activation_source_sha256"],
        "activation_protocol_sha256": build_arguments["activation_protocol_sha256"],
        "source_build": provenance, "preserved_version_two": expected_history_summary(),
        "owned_source_sha256": pins,
        "report_relative": REPORT_NAME, "report_sha256": report_owner["sha256"],
        "report_bytes": report_owner["size_bytes"],
        "report_publication": report_owner,
        "report_directory_fsync": {"completed": True, "device": 83, "inode": 101},
        "source_owners": sources, "canonical_targets": targets,
        "backup_entries": entries, "recovery_journal": journal_owner,
        "original_guard_sources": guards,
        "receipt_self_publication": "NOT CLAIMED",
        **zero_effects(),
    }
    arguments = {
        "mode": "restore", "family": family, "build_version": version,
        "activation_root": root,
        "activation_source_sha256": build_arguments["activation_source_sha256"],
        "activation_protocol_sha256": build_arguments["activation_protocol_sha256"],
        "activation_report_sha256": sha256(report_raw),
        "activation_receipt_sha256": sha256(canonical(receipt)),
    }
    return report, receipt, journal, arguments


def reseal_synthetic_build(
    report: dict[str, Any], receipt: dict[str, Any], arguments: dict[str, Any],
) -> tuple[dict[str, Any], bytes, dict[str, Any]]:
    sealed_receipt = copy.deepcopy(receipt)
    sealed_arguments = copy.deepcopy(arguments)
    plain = canonical(report)
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    sealed_receipt["archive_sha256"] = sha256(archive)
    sealed_receipt["archive_bytes"] = len(archive)
    sealed_receipt["uncompressed_sha256"] = sha256(plain)
    sealed_receipt["uncompressed_bytes"] = len(plain)
    publication = sealed_receipt.get("archive_publication")
    if type(publication) is dict:
        publication["sha256"] = sha256(archive)
        publication["bytes"] = len(archive)
    sealed_arguments["build_report_sha256"] = sha256(archive)
    sealed_arguments["build_receipt_sha256"] = sha256(canonical(sealed_receipt))
    return sealed_receipt, archive, sealed_arguments


def self_test() -> dict[str, Any]:
    positives = 0
    hostile = 0

    def positive(condition: Any, label: str) -> None:
        nonlocal positives
        require(bool(condition), "a dual-version positive control failed: " + label)
        positives += 1

    def reject(action: Any, label: str) -> None:
        nonlocal hostile
        try:
            action()
        except (ActivationError, SourceOnlyEffect, TypeError, ValueError,
                UnicodeError, OverflowError, RecursionError, OSError, zlib.error):
            hostile += 1
            return
        raise ActivationError("a dual-version hostile control escaped: " + label)

    with SyntheticSandbox() as sandbox:
        positive(parse_arguments(["--self-test"]) == {"mode": "self-test"},
                 "exact isolated source-only invocation")
        history = expected_history_summary()
        positive(len(history["records"]) == 3
                 and [item["status"] for item in history["records"]]
                 == ["PASS", "PASS", "FAIL"]
                 and sum(item["genuine_process_count"]
                         for item in history["records"]) == 39,
                 "preserve exactly 39 real V2 compiler processes and Zig failure")
        for version in ("2", "3"):
            positive(checked_build_version(version) == version,
                     "exact explicit source-build version " + version)
            for family in ("c", "rust", "zig"):
                label = family + ":v" + version
                report, receipt, archive, arguments, pins = synthetic_build_fixture(
                    family, version,
                )
                positive(decode_document(canonical(report), label) == report,
                         label + " complete canonical native source report")
                positive(decode_document(canonical(receipt), label) == receipt,
                         label + " genuine independently published receipt")
                positive(bounded_gzip(archive) == canonical(report),
                         label + " deterministic single-member archive")
                positive(parse_owner_pins(family, arguments["owned_source_sha256"])
                         == pins, label + " complete independent source closure")
                outputs = validate_build_report(report, receipt, archive,
                                                arguments, pins)
                positive(set(outputs) == set(FAMILIES[family]["binaries"]),
                         label + " genuine independently source-built native roles")
                streams = validate_processes(family, report["processes"], version)
                positive(len(streams) == len(expected_process_schedule(family)),
                         label + " exact complete compiler and GNU process streams")
                if family == "zig":
                    for phase in ("reference-a", "reference-b"):
                        command = planned_commands(family, phase, version)["build_zig_engine"]
                        positive(command.count("-fstrip") == (1 if version == "3" else 0),
                                 label + " exact phase-specific compiler strip proof " + phase)
                activation, activation_receipt, journal, recovery_arguments = (
                    synthetic_activation_fixture(family, version)
                )
                proved = validate_activation_documents(
                    activation, activation_receipt, journal,
                    arguments=recovery_arguments,
                )
                positive(proved["status"] == "PASS"
                         and proved["build_version"] == version
                         and set(proved["canonical_targets"])
                         == set(FAMILIES[family]["binaries"]),
                         label + " full recoverable original-mode native activation")
                positive(validate_build_provenance(
                    activation["source_build"], family, version,
                )["preserved_version_two_history_process_count"] == 39,
                    label + " exact typed historical process provenance")
                recovery = {
                    "mode": "recover", "family": family, "build_version": version,
                    "activation_root": recovery_arguments["activation_root"],
                    "activation_source_sha256":
                        recovery_arguments["activation_source_sha256"],
                    "activation_protocol_sha256":
                        recovery_arguments["activation_protocol_sha256"],
                    "recovery_journal_sha256": sha256(canonical(journal)),
                }
                positive(validate_recovery_journal(journal, arguments=recovery)
                         ["status"] == "PASS",
                         label + " independently pinned reportless SIGKILL recovery")
                command = ["--recover"]
                for option, field in (
                    ("--family", "family"), ("--build-version", "build_version"),
                    ("--activation-root", "activation_root"),
                    ("--activation-source-sha256", "activation_source_sha256"),
                    ("--activation-protocol-sha256", "activation_protocol_sha256"),
                    ("--recovery-journal-sha256", "recovery_journal_sha256"),
                ):
                    command.extend((option, recovery[field]))
                positive(parse_arguments(command) == recovery,
                         label + " exact version-pinned reportless recovery command")
                positive(parse_arguments(["--restore", *command[1:]]) == recovery,
                         label + " exact reportless restore alias")
                for role, target in activation["canonical_targets"].items():
                    intended = {
                        "schema": INTENT_SCHEMA, "status": "PREPARED",
                        "promotion_mode": "recoverable-canonical-promotion",
                        "family": family, "build_version": version,
                        "activation_root": recovery["activation_root"],
                        "candidate_import_root": ROOT,
                        "recovery_journal_sha256": recovery["recovery_journal_sha256"],
                        "role": role,
                        "target": {key: target[key] for key in OWNER_FIELDS},
                        **zero_effects(),
                    }
                    positive(same_owner(target, intended["target"]),
                             label + " rich/naked seven-field owner equality " + role)
                    positive(validate_promotion_intent(
                        intended, family=family, build_version=version,
                        root=recovery["activation_root"], role=role,
                        journal_sha256=recovery["recovery_journal_sha256"],
                        current=target,
                    )["inode"] == target["inode"],
                        label + " typed durable exact staged inode " + role)
                    rich = target["promotion_intent"]
                    positive(require_durable_owner(
                        rich, relative="promotion-intent-" + role + ".json",
                        root=recovery["activation_root"], directory_sync=True,
                    )["write_calls"] == 1,
                        label + " four authentic fsync flags and typed positive writes " + role)
                    for field in OWNER_FIELDS:
                        forged = copy.deepcopy(intended["target"])
                        if field == "relative":
                            forged[field] = "candidates/foreign-native.so"
                        elif field == "path":
                            forged[field] = ROOT + "/candidates/foreign-native.so"
                        elif field == "sha256":
                            forged[field] = synthetic_digest(label + field)
                        elif field == "mode":
                            forged[field] = 0o700 if forged[field] != 0o700 else 0o755
                        else:
                            forged[field] += 1
                        reject(lambda forged=forged: require(
                            same_owner(target, forged), "reject changed owner identity",
                        ), label + " substituted typed owner " + role + ":" + field)
                    for field in ("size_bytes", "device", "inode", "mode"):
                        forged = copy.deepcopy(intended["target"])
                        forged[field] = False
                        reject(lambda forged=forged: require(
                            same_owner(target, forged), "reject bool-as-int owner",
                        ), label + " bool-as-int native identity " + role + ":" + field)
                    for flag in DURABLE_FLAGS:
                        forged = copy.deepcopy(rich)
                        forged[flag] = False
                        reject(lambda forged=forged, role=role: require_durable_owner(
                            forged, relative="promotion-intent-" + role + ".json",
                            root=recovery["activation_root"], directory_sync=True,
                        ), label + " removed durable fsync flag " + role + ":" + flag)
                    for invalid in (False, True, 0, -1, 0.0, None):
                        forged = copy.deepcopy(rich)
                        forged["write_calls"] = invalid
                        reject(lambda forged=forged, role=role: require_durable_owner(
                            forged, relative="promotion-intent-" + role + ".json",
                            root=recovery["activation_root"], directory_sync=True,
                        ), label + " forged typed durable write count " + role)
                    entry = journal["backup_entries"][role]
                    positive(classify_recovery_state(entry, target)
                             == "source-verified-promoted",
                             label + " genuine partially promoted native role " + role)
                    if entry["originally_present"]:
                        positive(classify_recovery_state(entry, entry["original_owner"])
                                 == "already-original",
                                 label + " exact unchanged canonical original " + role)
                        for field in ("relative", "device", "inode", "mode"):
                            foreign = copy.deepcopy(entry["original_owner"])
                            if field == "relative":
                                foreign[field] = "candidates/foreign-native.so"
                            elif field == "mode":
                                foreign[field] = (0o700 if foreign[field] != 0o700
                                                  else 0o755)
                            else:
                                foreign[field] += 1
                            reject(lambda entry=entry, foreign=foreign:
                                   classify_recovery_state(entry, foreign),
                                   label + " same-content foreign original "
                                   + role + ":" + field)
                for role in FAMILIES[family]["binaries"]:
                    absent_report, absent_receipt, absent_journal, absent_args = (
                        synthetic_activation_fixture(family, version, absent_role=role)
                    )
                    positive(validate_activation_documents(
                        absent_report, absent_receipt, absent_journal,
                        arguments=absent_args,
                    )["status"] == "PASS",
                        label + " safely recorded genuinely absent original " + role)
                for field in tuple(receipt):
                    forged = copy.deepcopy(receipt)
                    forged.pop(field)
                    reject(lambda forged=forged: validate_build_report(
                        report, forged, archive, arguments, pins,
                    ), label + " omitted exact build receipt field " + field)
                for field in tuple(report):
                    forged = copy.deepcopy(report)
                    forged.pop(field)
                    reject(lambda forged=forged: validate_build_report(
                        forged, receipt, archive, arguments, pins,
                    ), label + " omitted exact build report field " + field)
                for field in tuple(activation):
                    forged = copy.deepcopy(activation)
                    forged.pop(field)
                    reject(lambda forged=forged: validate_activation_documents(
                        forged, activation_receipt, journal,
                        arguments=recovery_arguments,
                    ), label + " omitted actual canonical activation field " + field)
                for field in tuple(activation_receipt):
                    forged = copy.deepcopy(activation_receipt)
                    forged.pop(field)
                    reject(lambda forged=forged: validate_activation_documents(
                        activation, forged, journal, arguments=recovery_arguments,
                    ), label + " omitted actual durable activation receipt field " + field)
                for field in tuple(journal):
                    forged = copy.deepcopy(journal)
                    forged.pop(field)
                    reject(lambda forged=forged: validate_activation_documents(
                        activation, activation_receipt, forged,
                        arguments=recovery_arguments,
                    ), label + " omitted durable crash-recovery journal field " + field)
                for key in ("candidate_processes_started", "candidate_imports",
                            "native_libraries_loaded", "hidden_cases_read",
                            "benchmark_files_read", "clock_samples", "timing_trials_run"):
                    for invalid in (False, True, 0.0, 1, None):
                        forged = copy.deepcopy(report)
                        if invalid is None:
                            forged.pop(key, None)
                        else:
                            forged[key] = invalid
                        sealed_receipt, sealed_archive, sealed_arguments = (
                            reseal_synthetic_build(forged, receipt, arguments)
                        )
                        reject(lambda forged=forged, sr=sealed_receipt,
                               sa=sealed_archive, ar=sealed_arguments:
                               validate_build_report(forged, sr, sa, ar, pins),
                               label + " re-signed false typed report effect " + key)
                        forged_receipt = copy.deepcopy(receipt)
                        if invalid is None:
                            forged_receipt.pop(key, None)
                        else:
                            forged_receipt[key] = invalid
                        sealed_receipt, sealed_archive, sealed_arguments = (
                            reseal_synthetic_build(report, forged_receipt, arguments)
                        )
                        reject(lambda sr=sealed_receipt, sa=sealed_archive,
                               ar=sealed_arguments:
                               validate_build_report(report, sr, sa, ar, pins),
                               label + " re-signed false typed receipt effect " + key)
                for field in ("build_status", "status"):
                    forged = copy.deepcopy(receipt)
                    forged[field] = "FAIL"
                    sr, sa, ar = reseal_synthetic_build(report, forged, arguments)
                    reject(lambda sr=sr, sa=sa, ar=ar:
                           validate_build_report(report, sr, sa, ar, pins),
                           label + " publication-only failed-build receipt " + field)
                for field in ("source_sha256", "protocol_sha256", "schema"):
                    forged = copy.deepcopy(report)
                    opposite = BUILD_VERSIONS["2" if version == "3" else "3"]
                    forged[field] = opposite[field if field == "schema"
                                             else field]
                    sr, sa, ar = reseal_synthetic_build(forged, receipt, arguments)
                    reject(lambda forged=forged, sr=sr, sa=sa, ar=ar:
                           validate_build_report(forged, sr, sa, ar, pins),
                           label + " mixed native build version " + field)
                for index, process in enumerate(report["processes"]):
                    for field in ("name", "pid", "exit_status", "shell", "argv",
                                  "environment", "stdout_base64", "stdout_sha256",
                                  "stdout_bytes", "stderr_base64", "stderr_sha256",
                                  "stderr_bytes"):
                        forged = copy.deepcopy(report)
                        forged_process = forged["processes"][index]
                        if field == "pid":
                            forged_process[field] = 0
                        elif field == "exit_status":
                            forged_process[field] = 1
                        elif field == "shell":
                            forged_process[field] = True
                        elif field in ("argv", "environment"):
                            forged_process[field] = [] if field == "argv" else {}
                        elif field.endswith("_bytes"):
                            forged_process[field] = False
                        elif field.endswith("_sha256"):
                            forged_process[field] = synthetic_digest(label + field)
                        elif field.endswith("_base64"):
                            forged_process[field] = "%%%"
                        else:
                            forged_process[field] = "foreign"
                        sr, sa, ar = reseal_synthetic_build(forged, receipt, arguments)
                        reject(lambda forged=forged, sr=sr, sa=sa, ar=ar:
                               validate_build_report(forged, sr, sa, ar, pins),
                               label + " forged genuine process "
                               + str(index) + ":" + field)
                for raw in (archive + b"hidden", archive[:-1], b"", b"not-gzip",
                            archive + archive):
                    reject(lambda raw=raw: bounded_gzip(raw),
                           label + " rewritten, hidden, or concatenated build archive")
                for forbidden in ("regexec@GLIBC_2.2.5", "regcomp@GLIBC_2.2.5",
                                  "dlopen@GLIBC_2.2.5", "pcre2_match", "onig_search",
                                  "_sre", "PyInit__sre", "re2_match", "hs_scan",
                                  "regex_match", "PyRun_String", "(2)",
                                  "@GLIBC_2.4", "real@", "real@@", "real@@@GLIBC_2.4"):
                    reject(lambda forbidden=forbidden:
                           checked_symbol_name(forbidden),
                           label + " external/version-index native symbol " + forbidden)
        for invalid in (None, False, True, 2, 3, "", "1", "4", "02", "v2"):
            reject(lambda invalid=invalid: checked_build_version(invalid),
                   "reject implicit or disguised native-build version")
        for invalid in ("", ".", "..", "/tmp/x", "x/../y", "x//y", "x/./y",
                        "x\\y", "x\x00y"):
            reject(lambda invalid=invalid: checked_relative(invalid),
                   "reject escaped source/native relative owner")
        for invalid in ("", "0" * 63, "g" * 64, "A" * 64, 1, False, None):
            reject(lambda invalid=invalid: checked_digest(invalid, "synthetic"),
                   "reject malformed or bool-forged source digest")
        attempted = (
            ("filesystem", lambda: os.open("blocked", os.O_RDONLY)),
            ("process", lambda: subprocess.run(["blocked"])),
            ("thread", lambda: threading.Thread(target=lambda: None).start()),
            ("clock", lambda: time.perf_counter()),
            ("network", lambda: socket.socket()),
            ("environment", lambda: os.environ.get("blocked")),
            ("import", lambda: importlib.import_module("blocked")),
        )
        for category, action in attempted:
            reject(action, "actively blocked source-only effect " + category)
        positive(all(count > 0 for count in sandbox.blocked.values()),
                 "actively exercise every synthetic outside-effect denial")
        blocked = dict(sandbox.blocked)
    require(positives > 0 and hostile > 0,
            "require actual independent dual-version positive and hostile controls")
    return {
        "schema": SCHEMA + "-synthetic-source-only-self-test",
        "status": "PASS", "source_only": True,
        "synthetic_positive_control_count": positives,
        "synthetic_rejection_control_count": hostile,
        "build_version_count": 2, "candidate_family_count": 3,
        "preserved_version_two_history_process_count": 39,
        "original_oracle_suite_count": 13,
        "original_oracle_case_execution_denominator": 31_237,
        "original_v2_zig_reproducibility": "FAIL",
        "expanded_final_holdout": "NOT GENERATED; NOT OPENED",
        "blocked_source_only_effects": blocked,
        "source_only_effects": {
            "filesystem_reads": 0, "filesystem_writes": 0,
            "candidate_imports": 0, "native_libraries_loaded": 0,
            "candidate_processes_started": 0,
            "reference_processes_started": 0, "source_builds": 0,
            "canonical_promotions": 0, "journal_recoveries": 0,
            "network_requests": 0, "hidden_cases_read": 0,
            "benchmark_files_read": 0, "clock_samples": 0,
            "timing_trials_run": 0,
        },
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    try:
        parsed = parse_arguments(list(sys.argv[1:] if arguments is None else arguments))
        if parsed["mode"] == "self-test":
            result = self_test()
        elif parsed["mode"] == "activate":
            result = activate(parsed)
        elif parsed["mode"] == "recover":
            result = recover(parsed)
        else:
            require(parsed["mode"] == "restore",
                    "reject an unknown dual-version activation operation")
            result = restore(parsed)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (ActivationError, SourceOnlyEffect, OSError, ValueError, TypeError,
            UnicodeError, OverflowError, RecursionError, zlib.error) as error:
        result = {
            "schema": SCHEMA + "-failure", "status": "FAIL",
            "error_type": type(error).__name__, "error_message": str(error),
            **zero_effects(),
        }
        sys.stdout.buffer.write(canonical(result))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
