#!/usr/bin/env python3
"""Activate only two independently source-built, V2-proven native artifacts.

``--self-test`` is synthetic and denies file, process, clock, thread, network,
environment, and import operations.  ``--activate`` promotes only exact,
independently proven canonical native filenames after preserving a complete
durable rollback journal.  ``--restore`` recovers only those exact previous
files.  Neither operation imports a candidate, loads a native library, changes
a frozen source, opens a holdout, or measures speed.
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
SOURCE_RELATIVE = "tools/activate_verified_native_candidate_v1.py"
PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V1.md"
SCHEMA = "rebar-phase2-verified-native-candidate-activation-v1"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
REPORT_NAME = "activation-report.json"
RECEIPT_NAME = "activation-receipt.json"
JOURNAL_NAME = "recovery-journal.json"
JOURNAL_SCHEMA = SCHEMA + "-recovery-journal"
INTENT_SCHEMA = SCHEMA + "-durable-promotion-intent"
PRIVATE_PREFIX = "rebar-phase2-verified-native-activation-v1-"
BUILD_PREFIX = "rebar-phase2-native-build-v2-"
SANITIZED_BUILD_ROOT = "<FRESH_PRIVATE_TMP>"
BUILD_SCHEMA = "rebar-phase2-independent-native-source-build-v2"
BUILD_RECEIPT_SCHEMA = BUILD_SCHEMA + "-durable-publication-receipt"
BUILD_SOURCE_RELATIVE = "tools/reproduce_phase2_native_builds_v2.py"
BUILD_PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md"
BUILD_SOURCE_SHA256 = (
    "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796"
)
BUILD_PROTOCOL_SHA256 = (
    "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603"
)
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
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

ORIGINAL_GUARD_SOURCES: dict[str, str] = {
    "tools/independent_original_cpython_suite_v5.py": (
        "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
    ),
    "tools/independent_original_cpython_suite_v4.py": (
        "1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3"
    ),
    "tools/rust_original_cpython_suite_v1.py": (
        "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95"
    ),
    "tools/rust_original_cpython_suite_v2.py": (
        "569036804b557b01eb29ba404c6fea0ecc5806bdbc2b6b9eb61c1ea18aa79267"
    ),
    "tools/rust_original_cpython_suite_v3.py": (
        "55aced566c4ef0a236f26ddf4607dbe3e69ae9dc15ab6fd95399d4ddc346cea2"
    ),
}

FAMILIES: dict[str, dict[str, Any]] = {
    "c": {
        "module": "candidates.vm_candidate",
        "adapter": "candidates/vm_candidate.py",
        "owners": (
            "candidates/vm_candidate.py",
            "candidates/_vm_native.c",
        ),
        "binaries": {"extension": "_vm_native" + EXTENSION_SUFFIX},
    },
    "rust": {
        "module": "candidates.rust_candidate",
        "adapter": "candidates/rust_candidate.py",
        "owners": (
            "candidates/rust_candidate.py",
            "candidates/rust/py_bridge.c",
            "candidates/rust/Cargo.toml",
            "candidates/rust/Cargo.lock",
            "candidates/rust/src/lib.rs",
            "candidates/rust/src/newline.rs",
            "candidates/rust/src/search.rs",
            "candidates/rust/src/stack.rs",
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
            "candidates/zig_candidate.py",
            "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
        "binaries": {
            "engine": "_zig_probe.so",
            "bridge": "_zig_bridge" + EXTENSION_SUFFIX,
        },
    },
}

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


class ActivationError(Exception):
    """A frozen source, durable report, or native artifact failed closed."""


class SourceOnlyEffect(ActivationError):
    """A synthetic-only check tried to produce an outside effect."""


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
        raise ActivationError("a complete finite canonical JSON object is required") from error


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only actual complete immutable bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "an exact lowercase SHA-256 is mandatory: " + label,
    )
    return value


def checked_family(value: Any) -> str:
    require(type(value) is str and value in FAMILIES,
            "select exactly one independently owned C, Rust, or Zig family")
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL_BYTES,
            "supply the exact short published version-two build label")
    require(
        value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and all(ch in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in value)
        and "--" not in value and not value.endswith("-"),
        "reject an unsafe, duplicated, or traversing source-build label",
    )
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512,
            "require one bounded root-relative artifact name")
    require("\\" not in value and "\x00" not in value
            and not value.startswith("/"),
            "reject absolute paths, NULs, and alternate path separators")
    parts = value.split("/")
    require(all(part not in ("", ".", "..") for part in parts),
            "reject empty path components and artifact-path traversal")
    return value


def checked_private_root(value: Any, family: str, *, build: bool) -> str:
    family = checked_family(family)
    require(type(value) is str and "\x00" not in value and "\\" not in value,
            "require one literal absolute private temporary root")
    parts = value.split("/")
    require(len(parts) == 3 and parts[0] == "" and parts[1] == "tmp",
            "a private root must be one specific directory immediately under /tmp")
    prefix = (BUILD_PREFIX if build else PRIVATE_PREFIX) + family + "-"
    require(parts[2].startswith(prefix) and len(parts[2]) > len(prefix),
            "reject a broad, existing, cross-family, or unowned temporary root")
    suffix = parts[2][len(prefix):]
    require(all(ch.isascii() and (ch.isalnum() or ch in "-_") for ch in suffix),
            "reject a disguised or unsafe private-root suffix")
    return value


def parse_owner_pins(family: str, values: Any) -> dict[str, str]:
    name = checked_family(family)
    expected = tuple(FAMILIES[name]["owners"])
    require(type(values) is list and len(values) == len(expected),
            "pin every independently owned family source exactly once")
    result: dict[str, str] = {}
    for item in values:
        require(type(item) is str and item.count("=") == 1,
                "an exact source owner is RELATIVE/PATH=SHA256")
        relative, digest = item.split("=", 1)
        checked_relative(relative)
        require(relative in expected and relative not in result,
                "reject missing, duplicated, foreign, or cross-family source owners")
        result[relative] = checked_digest(digest, relative)
    require(set(result) == set(expected),
            "the complete independent candidate source closure is mandatory")
    return dict(sorted(result.items()))


def unique_json_pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "reject duplicated or non-string canonical JSON keys")
        result[key] = value
    return result


def reject_json_constant(value: str) -> Any:
    raise ActivationError("reject a non-finite signed JSON value: " + value)


def decode_document(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
            "a complete bounded canonical JSON document is mandatory: " + label)
    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique_json_pairs,
            parse_constant=reject_json_constant,
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ActivationError("reject malformed signed JSON: " + label) from error
    require(type(value) is dict and canonical(value) == raw,
            "reject altered canonical JSON bytes: " + label)
    return value


def bounded_gzip(raw: Any) -> bytes:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES,
            "the complete caller-pinned V2 archive is mandatory")
    decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        plain = decompressor.decompress(raw, MAX_REPORT_BYTES + 1)
        plain += decompressor.flush()
    except (ValueError, zlib.error) as error:
        raise ActivationError("the complete V2 report archive is invalid") from error
    require(0 < len(plain) <= MAX_REPORT_BYTES and decompressor.eof
            and not decompressor.unused_data and not decompressor.unconsumed_tail,
            "reject truncated, concatenated, hidden, or oversized V2 reports")
    require(gzip.compress(plain, compresslevel=9, mtime=0) == raw,
            "reject nondeterministic or rewritten V2 archive bytes")
    return plain


def checked_symbol_name(value: Any) -> tuple[str, str | None, bool]:
    require(type(value) is str and 0 < len(value) <= 1024,
            "an actual GNU dynamic symbol name is mandatory")
    pieces = value.split("@")
    require(1 <= len(pieces) <= 3,
            "reject malformed or multiply decorated GNU symbol versions")
    name = pieces[0]
    require(
        bool(name) and name[0] in
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$"
        and all(ch.isascii() and (ch.isalnum() or ch in "_.$") for ch in name),
        "reject an empty, shifted, disguised, or non-ASCII native symbol",
    )
    version: str | None = None
    default = False
    if len(pieces) == 2:
        version = pieces[1]
    elif len(pieces) == 3:
        require(pieces[1] == "",
                "a default GNU symbol version must contain exactly two at-signs")
        default = True
        version = pieces[2]
    if version is not None:
        require(
            0 < len(version) <= 256
            and all(ch.isascii() and (ch.isalnum() or ch in "_.+-")
                    for ch in version),
            "reject a missing, shifted, or malformed GNU symbol version",
        )
    require(name not in FORBIDDEN_NATIVE_NAMES
            and not any(name.startswith(prefix)
                        for prefix in FORBIDDEN_NATIVE_PREFIXES),
            "reject an original, external, dynamic, or delegated native matcher")
    return name, version, default


def parse_dynamic(raw: Any) -> dict[str, list[str]]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES
            and b"\x00" not in raw,
            "require the actual complete GNU dynamic-dependency stream")
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise ActivationError("an ELF dynamic stream is not UTF-8") from error
    result: dict[str, list[str]] = {
        "needed": [], "runpath": [], "rpath": [], "soname": [],
    }
    for line in text.splitlines():
        for marker, key in (
            ("(NEEDED)", "needed"), ("(RUNPATH)", "runpath"),
            ("(RPATH)", "rpath"), ("(SONAME)", "soname"),
        ):
            if marker not in line:
                continue
            start = line.find("[")
            finish = line.find("]", start + 1)
            require(start >= 0 and finish > start,
                    "a real native dependency omitted its bounded name")
            value = line[start + 1:finish]
            require(value and "\x00" not in value,
                    "reject an empty or disguised native dependency")
            result[key].append(value)
    for key, entries in result.items():
        require(len(entries) == len(set(entries)),
                "reject repeated actual native dependencies: " + key)
    return result


def parse_symbols(raw: Any) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES
            and raw.endswith(b"\n") and b"\x00" not in raw,
            "the complete actual GNU dynamic-symbol stream is mandatory")
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise ActivationError("an actual GNU symbol stream is not UTF-8") from error
    prefix = "Symbol table '.dynsym' contains "
    suffix = " entries:"
    count: int | None = None
    entries: dict[int, dict[str, Any]] = {}
    allowed_types = frozenset({
        "NOTYPE", "OBJECT", "FUNC", "SECTION", "FILE", "COMMON", "TLS",
        "GNU_IFUNC", "IFUNC",
    })
    allowed_bindings = frozenset({"LOCAL", "GLOBAL", "WEAK", "UNIQUE", "GNU_UNIQUE"})
    allowed_visibility = frozenset({"DEFAULT", "INTERNAL", "HIDDEN", "PROTECTED"})
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(prefix):
            require(count is None and stripped.endswith(suffix),
                    "reject duplicated or malformed real GNU symbol tables")
            value = stripped[len(prefix):-len(suffix)]
            require(value.isascii() and value.isdecimal()
                    and 1 <= int(value) <= 131_072,
                    "reject an omitted or unbounded real GNU symbol count")
            count = int(value)
            continue
        if stripped.startswith("Num:"):
            require(count is not None, "a GNU symbol header escaped its table")
            continue
        fields = stripped.split()
        require(bool(fields) and fields[0].endswith(":")
                and fields[0][:-1].isascii() and fields[0][:-1].isdecimal(),
                "reject an unrecognized or shifted actual GNU symbol row")
        require(count is not None,
                "reject an actual GNU symbol outside its authenticated table")
        index = int(fields[0][:-1])
        require(index not in entries and 0 <= index < count
                and 7 <= len(fields) <= 9,
                "reject duplicated, shifted, omitted, or trailing GNU symbol fields")
        address, size, kind, binding, visibility, section = fields[1:7]
        require(address.isascii() and 1 <= len(address) <= 32
                and all(ch in "0123456789abcdefABCDEF" for ch in address),
                "reject a malformed actual GNU symbol address")
        require(size.isascii() and size.isdecimal()
                and 0 <= int(size) <= MAX_BINARY_BYTES,
                "reject a malformed actual GNU symbol size")
        require(kind in allowed_types and binding in allowed_bindings
                and visibility in allowed_visibility,
                "reject a disguised GNU symbol type, visibility, or binding")
        require(section in {"UND", "ABS", "COM"}
                or section.isascii() and section.isdecimal(),
                "reject a shifted actual GNU symbol section")
        if len(fields) == 7:
            require(index == 0 and section == "UND" and binding == "LOCAL",
                    "only the actual null dynamic symbol may omit a name")
            entries[index] = {
                "index": index, "type": kind, "binding": binding,
                "visibility": visibility, "section": section, "name": None,
                "raw_name": None, "version": None,
                "default_version": False, "version_index": None,
            }
            continue
        raw_name = fields[7]
        name, version, default = checked_symbol_name(raw_name)
        version_index: int | None = None
        if len(fields) == 9:
            trailer = fields[8]
            require(version is not None and trailer.startswith("(")
                    and trailer.endswith(")")
                    and trailer[1:-1].isascii()
                    and trailer[1:-1].isdecimal()
                    and int(trailer[1:-1]) > 0,
                    "reject a shifted GNU version-index pseudo-symbol")
            version_index = int(trailer[1:-1])
        entries[index] = {
            "index": index, "type": kind, "binding": binding,
            "visibility": visibility, "section": section, "name": name,
            "raw_name": raw_name, "version": version,
            "default_version": default, "version_index": version_index,
        }
    require(count is not None and len(entries) == count
            and set(entries) == set(range(count)),
            "a real complete GNU versioned-symbol record was omitted or reordered")
    records = [entries[index] for index in range(count)]
    exports = sorted({
        row["name"] for row in records
        if row["name"] is not None and row["section"] != "UND"
        and row["binding"] in {"GLOBAL", "WEAK", "UNIQUE", "GNU_UNIQUE"}
    })
    undefined = sorted({
        row["name"] for row in records
        if row["name"] is not None and row["section"] == "UND"
    })
    require(bool(exports), "the genuine independently owned native entry point is missing")
    return {
        "exports": exports, "undefined": undefined, "symbol_count": count,
        "versioned_symbol_count": sum(row["version"] is not None for row in records),
        "symbol_records": records,
    }


def validate_elf(
    family: str, role: str, dynamic: dict[str, Any], symbols: dict[str, Any],
) -> dict[str, Any]:
    family = checked_family(family)
    specification = FAMILIES[family]
    require(role in specification["binaries"],
            "reject a sibling or replaced native artifact role")
    needed = set(dynamic["needed"])
    exports = set(symbols["exports"])
    undefined = set(symbols["undefined"])
    combined = exports | undefined
    require(not dynamic["rpath"], "reject an unsafe native-library RPATH")
    if family == "c":
        require(not any(name.startswith(("rebar_", "rebar_zig_"))
                        or name in {"PyInit__rust_bridge", "PyInit__zig_bridge"}
                        for name in combined),
                "the C implementation delegates to Rust or Zig")
        require(role == "extension" and "PyInit__vm_native" in exports
                and needed.issubset(ALLOWED_SYSTEM_LIBRARIES)
                and not dynamic["runpath"],
                "the C extension has a missing entry point or foreign matcher")
        required = {"PyInit__vm_native"}
    elif family == "rust":
        require(not any(name.startswith("rebar_zig_")
                        or name in {"PyInit__vm_native", "PyInit__zig_bridge"}
                        for name in combined),
                "the Rust implementation delegates to C or Zig")
        if role == "engine":
            require(dynamic["soname"] == ["_rust_engine.so"]
                    and not dynamic["runpath"]
                    and needed.issubset(ALLOWED_SYSTEM_LIBRARIES)
                    and RUST_ENGINE_EXPORTS.issubset(exports),
                    "the exact independently owned Rust engine is incomplete")
            required = set(RUST_ENGINE_EXPORTS)
        else:
            require("PyInit__rust_bridge" in exports
                    and "_rust_engine.so" in needed
                    and needed.issubset(ALLOWED_SYSTEM_LIBRARIES | {"_rust_engine.so"})
                    and dynamic["runpath"] == ["$ORIGIN"]
                    and any(name.startswith("rebar_") for name in undefined)
                    and not any(name.startswith("rebar_zig_") for name in undefined),
                    "the Rust bridge must load only its adjacent owned engine")
            required = {"PyInit__rust_bridge"}
    else:
        require(not any((name.startswith("rebar_")
                         and not name.startswith("rebar_zig_"))
                        or name in {"PyInit__vm_native", "PyInit__rust_bridge"}
                        for name in combined),
                "the Zig implementation delegates to C or Rust")
        if role == "engine":
            require(dynamic["soname"] == ["_zig_probe.so"]
                    and not dynamic["runpath"]
                    and needed.issubset(ALLOWED_SYSTEM_LIBRARIES)
                    and ZIG_ENGINE_EXPORTS.issubset(exports),
                    "the exact independently owned Zig engine is incomplete")
            required = set(ZIG_ENGINE_EXPORTS)
        else:
            require("PyInit__zig_bridge" in exports
                    and "_zig_probe.so" in needed
                    and needed.issubset(ALLOWED_SYSTEM_LIBRARIES | {"_zig_probe.so"})
                    and dynamic["runpath"] == ["$ORIGIN"]
                    and any(name.startswith("rebar_zig_") for name in undefined)
                    and not any(name.startswith("rebar_compile") for name in undefined),
                    "the Zig bridge must load only its adjacent owned engine")
            required = {"PyInit__zig_bridge"}
    return {
        "role": role, "needed": sorted(needed),
        "runpath": list(dynamic["runpath"]),
        "soname": list(dynamic["soname"]),
        "required_exports": sorted(required),
        "exports": list(symbols["exports"]),
        "undefined": list(symbols["undefined"]),
        "symbol_count": symbols["symbol_count"],
        "versioned_symbol_count": symbols["versioned_symbol_count"],
        "symbol_records": list(symbols["symbol_records"]),
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
    }


def decode_process_output(process: Any, field: str) -> bytes:
    require(type(process) is dict and field in {"stdout", "stderr"},
            "require the exact complete compiler or ELF-inspector process")
    encoded = process.get(field + "_base64")
    require(type(encoded) is str and encoded.isascii(),
            "reject missing actual compiler or GNU-inspector output")
    try:
        raw = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise ActivationError("reject altered GNU process-output encoding") from error
    require(base64.b64encode(raw).decode("ascii") == encoded
            and 0 <= len(raw) <= MAX_PROCESS_BYTES
            and process.get(field + "_bytes") == len(raw)
            and process.get(field + "_sha256") == sha256(raw),
            "a complete actual compiler process stream was altered")
    return raw


def expected_processes(family: str) -> list[str]:
    checked_family(family)
    versions = ["gcc_version", "readelf_version"]
    if family == "rust":
        versions.extend(("rustc_version", "cargo_version"))
    elif family == "zig":
        versions.append("zig_version")
    phase = (
        ["build_c_extension", "extension_dynamic", "extension_symbols"]
        if family == "c"
        else [
            "build_" + family + "_engine", "build_" + family + "_bridge",
            "engine_dynamic", "engine_symbols",
            "bridge_dynamic", "bridge_symbols",
        ]
    )
    return versions + phase + phase


def validate_processes(family: str, processes: Any) -> list[dict[str, Any]]:
    names = expected_processes(family)
    require(type(processes) is list and len(processes) == len(names),
            "retain every actual V2 compiler and complete GNU-inspector process")
    result: list[dict[str, Any]] = []
    pids: set[int] = set()
    executables = {
        "gcc_version": PINNED_GCC,
        "readelf_version": PINNED_READELF,
        "rustc_version": PINNED_RUSTC,
        "cargo_version": PINNED_CARGO,
        "zig_version": PINNED_ZIG,
        "build_c_extension": PINNED_GCC,
        "build_rust_engine": PINNED_CARGO,
        "build_rust_bridge": PINNED_GCC,
        "build_zig_engine": PINNED_ZIG,
        "build_zig_bridge": PINNED_GCC,
        "engine_dynamic": PINNED_READELF,
        "engine_symbols": PINNED_READELF,
        "bridge_dynamic": PINNED_READELF,
        "bridge_symbols": PINNED_READELF,
        "extension_dynamic": PINNED_READELF,
        "extension_symbols": PINNED_READELF,
    }
    for index, (process, name) in enumerate(zip(processes, names, strict=True)):
        require(type(process) is dict and process.get("name") == name
                and process.get("shell") is False
                and type(process.get("pid")) is int
                and process["pid"] > 0 and process["pid"] not in pids
                and process.get("exit_status") == 0,
                "reject an invented, repeated, failed, or shell-based V2 process")
        pids.add(process["pid"])
        argv = process.get("argv")
        require(type(argv) is list and len(argv) >= 2
                and all(type(item) is str and "\x00" not in item for item in argv)
                and argv[0] == executables[name],
                "reject an unpinned real V2 compiler or GNU-inspector command")
        environment = process.get("environment")
        require(type(environment) is dict
                and all(type(key) is str and type(value) is str
                        for key, value in environment.items())
                and environment.get("LC_ALL") == "C"
                and environment.get("LANG") == "C"
                and environment.get("TZ") == "UTC"
                and environment.get("SOURCE_DATE_EPOCH") == "1"
                and "LD_PRELOAD" not in environment
                and "LD_LIBRARY_PATH" not in environment,
                "reject an uncontrolled or substituted V2 compiler environment")
        if family == "rust":
            require(environment.get("CARGO_NET_OFFLINE") == "true"
                    and environment.get("CARGO_INCREMENTAL") == "0"
                    and environment.get("RUSTC") == PINNED_RUSTC,
                    "a Rust process was not pinned and entirely offline")
        stdout = decode_process_output(process, "stdout")
        stderr = decode_process_output(process, "stderr")
        if name.endswith("_dynamic") or name.endswith("_symbols"):
            phase_index = 0 if index < len(names) - (3 if family == "c" else 6) else 1
            phase = ("reference-a", "reference-b")[phase_index]
            role = name.rsplit("_", 1)[0]
            expected_path = (
                SANITIZED_BUILD_ROOT + "/" + phase + "/native/"
                + FAMILIES[family]["binaries"][role]
            )
            option = "--dynamic" if name.endswith("_dynamic") else "--dyn-syms"
            require(argv == [PINNED_READELF, option, "--wide", expected_path],
                    "an actual GNU inspector examined a different native artifact")
            require(bool(stdout), "the real GNU ELF inspector returned no symbol evidence")
        result.append({
            "name": name, "stdout": stdout, "stderr": stderr,
            "pid": process["pid"],
        })
    return result


def validate_publication(receipt: Any, report: Any, archive: bytes,
                         arguments: dict[str, Any]) -> None:
    family = checked_family(arguments["family"])
    label = checked_label(arguments["build_label"])
    require(type(receipt) is dict and type(report) is dict
            and report.get("schema") == BUILD_SCHEMA
            and receipt.get("schema") == BUILD_RECEIPT_SCHEMA
            and report.get("status") == "PASS"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and report.get("family") == receipt.get("family") == family
            and report.get("label") == receipt.get("label") == label,
            "only a genuinely published passing V2 family report can activate")
    require(sha256(archive) == arguments.get("build_report_sha256")
            and sha256(canonical(receipt))
            == arguments.get("build_receipt_sha256"),
            "the separately caller-pinned V2 report or receipt bytes changed")
    genuine_receipt_keys = {
        "schema", "status", "build_status", "family", "label",
        "source_sha256", "protocol_sha256", "phase1_manifest_sha256",
        "archive_relative", "archive_sha256", "archive_bytes",
        "uncompressed_sha256", "uncompressed_bytes",
        "archive_publication", "archive_directory_fsync",
        "owned_source_sha256", "candidate_processes_started",
        "candidate_imports", "native_libraries_loaded", "hidden_cases_read",
        "benchmark_files_read", "clock_samples", "timing_trials_run",
        "performance", "candidate_correctness", "winner_selected",
        "receipt_self_publication",
    }
    require(set(receipt) == genuine_receipt_keys,
            "require the exact genuine corrected V2 durable receipt key closure")
    for key, argument in (
        ("source_sha256", "build_source_sha256"),
        ("protocol_sha256", "build_protocol_sha256"),
    ):
        require(report.get(key) == receipt.get(key) == arguments[argument],
                "the exact published V2 recorder or protocol was replaced")
    archive_relative = (
        EVIDENCE_RELATIVE + "/native-source-build-v2-" + family
        + "-" + label + ".json.gz"
    )
    plain = canonical(report)
    require(receipt.get("archive_relative") == archive_relative
            and receipt.get("archive_sha256") == sha256(archive)
            and receipt.get("archive_bytes") == len(archive)
            and receipt.get("uncompressed_sha256") == sha256(plain)
            and receipt.get("uncompressed_bytes") == len(plain)
            and receipt.get("phase1_manifest_sha256") == PHASE1_SHA256,
            "the actual V2 archive, canonical report, or original oracle was substituted")
    publication = receipt.get("archive_publication")
    require(type(publication) is dict
            and publication.get("sha256") == sha256(archive)
            and publication.get("bytes") == len(archive)
            and publication.get("path") == ROOT + "/" + archive_relative
            and publication.get("exclusive_creation") is True
            and publication.get("same_inode_readback_verified") is True
            and publication.get("file_fsync_completed") is True,
            "the V2 build archive was not genuinely exclusively synchronized")
    synchronization = receipt.get("archive_directory_fsync")
    require(type(synchronization) is dict
            and synchronization.get("completed") is True
            and type(synchronization.get("device")) is int
            and type(synchronization.get("inode")) is int,
            "the actual V2 archive directory was not durably synchronized")
    counters = (
        "candidate_processes_started", "candidate_imports",
        "native_libraries_loaded", "hidden_cases_read",
        "benchmark_files_read", "clock_samples", "timing_trials_run",
    )
    for owner in (report, receipt):
        require(all(type(owner.get(key)) is int and owner.get(key) == 0
                    for key in counters),
                "a V2 source proof loaded a candidate, holdout, clock, or benchmark")
        require(owner.get("candidate_correctness") == "NOT MEASURED"
                and owner.get("performance") == "NOT MEASURED"
                and owner.get("winner_selected") is False,
                "a build proof invented candidate correctness, speed, or a winner")
    require(type(report.get("reference_processes_started")) is int
            and report.get("reference_processes_started") == 0
            and type(report.get("network_requests")) is int
            and report.get("network_requests") == 0,
            "a V2 source proof ran a reference or used the network")
    require(receipt.get("receipt_self_publication") == "NOT CLAIMED",
            "a V2 receipt falsely claims to authenticate its own bytes")


def validate_source_snapshots(
    family: str, report: dict[str, Any], receipt: dict[str, Any],
    pins: dict[str, str],
) -> None:
    expected = set(FAMILIES[family]["owners"])
    require(report.get("owned_source_sha256") == pins
            and receipt.get("owned_source_sha256") == pins
            and set(pins) == expected,
            "both passing V2 publications must pin every actual family owner")
    before = report.get("owned_source_before")
    after = report.get("owned_source_after")
    require(type(before) is dict and type(after) is dict
            and set(before) == set(after) == expected,
            "both complete V2 source snapshots are mandatory")
    for relative, expected_digest in pins.items():
        first = before[relative]
        second = after[relative]
        require(type(first) is dict and type(second) is dict
                and first.get("path") == second.get("path") == ROOT + "/" + relative
                and first.get("sha256") == second.get("sha256") == expected_digest
                and type(first.get("size_bytes")) is int
                and 0 < first["size_bytes"] <= MAX_SOURCE_BYTES
                and first.get("size_bytes") == second.get("size_bytes")
                and type(first.get("device")) is int
                and first.get("device") == second.get("device")
                and type(first.get("inode")) is int
                and first.get("inode") == second.get("inode"),
                "an owned source changed or was substituted during its V2 build")
    phase1 = report.get("phase1")
    require(type(phase1) is dict and phase1.get("status") == "PASS"
            and phase1.get("suite_count") == 13
            and phase1.get("case_execution_count") == 31_237
            and phase1.get("candidate_correctness") == "NOT MEASURED"
            and phase1.get("performance") == "NOT MEASURED"
            and phase1.get("final_holdout_authorized") is False,
            "the independently complete 31,237-case original oracle is mandatory")
    support = report.get("frozen_support_inputs")
    support_after = report.get("frozen_support_inputs_after")
    require(type(support) is dict and type(support_after) is dict
            and set(support) == set(support_after),
            "both complete frozen V2 support-input snapshots are mandatory")
    required_support = {
        "immutable_objective": (ROOT + "/GOAL.md", GOAL_SHA256),
        "complete_correctness_manifest": (
            ROOT + "/" + PHASE1_RELATIVE, PHASE1_SHA256,
        ),
        "pinned_cpython_executable": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
        "native_build_recorder": (
            ROOT + "/" + BUILD_SOURCE_RELATIVE, BUILD_SOURCE_SHA256,
        ),
        "native_build_protocol": (
            ROOT + "/" + BUILD_PROTOCOL_RELATIVE, BUILD_PROTOCOL_SHA256,
        ),
    }
    require(set(required_support).issubset(support),
            "the frozen objective, complete oracle, Python, or V2 source was omitted")
    for name, (path, digest) in required_support.items():
        first = support[name]
        second = support_after[name]
        require(type(first) is dict and type(second) is dict
                and first.get("path") == second.get("path") == path
                and first.get("sha256") == second.get("sha256") == digest
                and type(first.get("size_bytes")) is int
                and first["size_bytes"] > 0
                and first.get("size_bytes") == second.get("size_bytes")
                and type(first.get("device")) is int
                and first.get("device") == second.get("device")
                and type(first.get("inode")) is int
                and first.get("inode") == second.get("inode"),
                "a frozen V2 objective, oracle, Python, or source changed")
    history = report.get("historical_v1_c")
    require(type(history) is dict
            and history.get("status")
            == "AUTHENTIC HISTORICAL BUILD; V1 SYMBOL AUDIT FALSIFIED"
            and history.get("real_versioned_symbol_count_per_phase") == 9
            and history.get("observed_v1_parser_false_symbols")
            == ["(2)", "(3)", "(4)", "(5)", "(6)"],
            "never convert the falsified historical V1 symbol audit into V2 proof")
    audit = report.get("source_independence_audit")
    require(type(audit) is dict
            and audit.get("source_owner_count") == len(expected)
            and audit.get("external_regex_package_count") == 0
            and audit.get("cross_family_dependency_count") == 0
            and type(audit.get("source_audits")) is list,
            "the genuine independently owned V2 source audit is mandatory")
    audits = audit["source_audits"]
    audited = {item.get("path") for item in audits if type(item) is dict}
    wanted = {name for name in expected if name.endswith((".py", ".c", ".rs", ".zig"))}
    require(audited == wanted and len(audits) == len(wanted),
            "every actual native and Python source requires its V2 audit")
    for item in audits:
        require(item.get("external_regex_dependency_count") == 0,
                "an owned native source delegates to an outside matcher")
        if item["path"].endswith(".py"):
            require(item.get("cross_family_dependency_count") == 0,
                    "a candidate adapter delegates to another family")
    cargo = audit.get("cargo_dependency_closure")
    if family == "rust":
        require(type(cargo) is dict
                and cargo.get("package") == "rebar-rust-continuation"
                and cargo.get("package_count") == 1
                and cargo.get("external_package_count") == 0
                and cargo.get("registry_count") == 0
                and cargo.get("build_script_count") == 0
                and cargo.get("locked") is True
                and cargo.get("offline") is True,
                "the Rust engine must have zero outside dependencies")
    else:
        require(cargo is None, "a foreign Rust dependency closure escaped")


def validate_build_report(
    report: dict[str, Any], receipt: dict[str, Any], archive: bytes,
    arguments: dict[str, Any], owner_pins: dict[str, str],
) -> dict[str, dict[str, Any]]:
    family = checked_family(arguments["family"])
    validate_publication(receipt, report, archive, arguments)
    validate_source_snapshots(family, report, receipt, owner_pins)
    require(report.get("fresh_private_root") == SANITIZED_BUILD_ROOT
            and report.get("error") is None,
            "a passing V2 proof omitted its exact private build root")
    processes = validate_processes(family, report.get("processes"))
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == 2
            and [item.get("name") if type(item) is dict else None for item in phases]
            == ["reference-a", "reference-b"],
            "two actual separately owned V2 build phases are mandatory")
    versions = 2 + (2 if family == "rust" else 1 if family == "zig" else 0)
    step_size = 3 if family == "c" else 6
    roles = FAMILIES[family]["binaries"]
    validated: dict[str, dict[str, Any]] = {}
    for number, phase in enumerate(phases):
        phase_name = ("reference-a", "reference-b")[number]
        prefix = SANITIZED_BUILD_ROOT + "/" + phase_name
        require(phase.get("fresh_source_directory") == prefix + "/source"
                and phase.get("fresh_native_directory") == prefix + "/native"
                and all(type(phase.get(key)) is int and phase[key] == 0
                        for key in (
                            "candidate_processes_started", "candidate_imports",
                            "native_libraries_loaded", "timing_trials_run",
                            "hidden_cases_read",
                        )),
                "a V2 phase reused, loaded, or measured a candidate")
        copies = phase.get("copied_source_owners")
        require(type(copies) is dict and set(copies) == set(owner_pins),
                "both V2 phases must copy every owned family source")
        for relative, digest in owner_pins.items():
            item = copies[relative]
            require(type(item) is dict
                    and item.get("path") == prefix + "/source/" + relative
                    and item.get("sha256") == digest
                    and type(item.get("bytes")) is int and item["bytes"] > 0
                    and item.get("exclusive_creation") is True
                    and item.get("same_inode_readback_verified") is True,
                    "a complete fresh V2 phase source copy was substituted")
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict and set(outputs) == set(roles),
                "a real source-built V2 native engine or bridge is missing")
        phase_steps = processes[versions + number * step_size:
                                versions + (number + 1) * step_size]
        lookup = {item["name"]: item for item in phase_steps}
        for role, filename in roles.items():
            output = outputs[role]
            require(type(output) is dict
                    and output.get("family") == family
                    and output.get("role") == role
                    and output.get("file_name") == filename
                    and output.get("path") == prefix + "/native/" + filename
                    and type(output.get("size_bytes")) is int
                    and 0 < output["size_bytes"] <= MAX_BINARY_BYTES
                    and output.get("prebuilt_binary_read") is False
                    and output.get("candidate_imported") is False,
                    "a V2 output is stale, foreign, prebuilt, or incompletely named")
            checked_digest(output.get("sha256"), filename)
            dynamic_step = lookup.get(role + "_dynamic")
            symbol_step = lookup.get(role + "_symbols")
            require(type(dynamic_step) is dict and type(symbol_step) is dict,
                    "both actual GNU inspector process streams are mandatory")
            observed = validate_elf(
                family, role, parse_dynamic(dynamic_step["stdout"]),
                parse_symbols(symbol_step["stdout"]),
            )
            require(output.get("elf") == observed,
                    "the actual complete version-aware ELF audit was substituted")
            if number == 0:
                validated[role] = {
                    "file_name": filename,
                    "sha256": output["sha256"],
                    "size_bytes": output["size_bytes"],
                    "elf": observed,
                }
            else:
                first = validated[role]
                require(output["sha256"] == first["sha256"]
                        and output["size_bytes"] == first["size_bytes"]
                        and observed == first["elf"],
                        "the two actual independently source-built artifacts differ")
    reproducible = report.get("reproducibility")
    require(type(reproducible) is dict
            and reproducible.get("independent_fresh_phase_count") == 2
            and reproducible.get("byte_identical") is True
            and reproducible.get("prebuilt_binary_count") == 0
            and reproducible.get("native_libraries_loaded") == 0,
            "a native artifact must match both actually fresh source builds")
    outputs = reproducible.get("native_outputs")
    require(type(outputs) is dict and set(outputs) == set(validated),
            "the full V2 reproducibility record omitted a native role")
    for role, actual in validated.items():
        expected = outputs[role]
        require(type(expected) is dict
                and expected.get("file_name") == actual["file_name"]
                and expected.get("sha256") == actual["sha256"]
                and expected.get("size_bytes") == actual["size_bytes"]
                and expected.get("reproduced_in_two_fresh_directories") is True
                and expected.get("elf") == actual["elf"],
                "an actual source-built native role was not reproduced twice")
    expected_engine = arguments["native_engine_sha256"]
    expected_bridge = arguments["native_bridge_sha256"]
    expected_engine_size = arguments["native_engine_bytes"]
    expected_bridge_size = arguments["native_bridge_bytes"]
    if family == "c":
        require(expected_engine == expected_bridge
                and expected_engine_size == expected_bridge_size
                and validated["extension"]["sha256"] == expected_engine
                and validated["extension"]["size_bytes"] == expected_engine_size,
                "the exact single C native extension was not caller-pinned")
    else:
        require(expected_engine != expected_bridge
                and validated["engine"]["sha256"] == expected_engine
                and validated["bridge"]["sha256"] == expected_bridge
                and validated["engine"]["size_bytes"] == expected_engine_size
                and validated["bridge"]["size_bytes"] == expected_bridge_size,
                "the exact separate engine and bridge were not caller-pinned")
    return validated


def directory_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))


def regular_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def open_root(root: str, *, private: bool) -> int:
    require(type(root) is str and root.startswith("/")
            and "\x00" not in root and root == root.rstrip("/"),
            "open only one exact absolute no-follow source root")
    descriptor = os.open(root, directory_flags())
    try:
        info = os.fstat(descriptor)
        visible = os.stat(root, follow_symlinks=False)
        require(stat.S_ISDIR(info.st_mode) and stat.S_ISDIR(visible.st_mode)
                and (info.st_dev, info.st_ino) == (visible.st_dev, visible.st_ino),
                "an authenticated root was redirected or replaced")
        if private:
            require(stat.S_IMODE(info.st_mode) == 0o700
                    and info.st_uid == os.geteuid(),
                    "the actual family temporary root must be owned and mode 0700")
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
            "require one bounded independently authenticated owner")
    if exact_size is not None:
        require(type(exact_size) is int and 0 < exact_size <= maximum,
                "require the exact actual source-built artifact size")
    opened: list[int] = []
    try:
        current = open_root(root, private=private)
        opened.append(current)
        components = relative.split("/")
        for name in components[:-1]:
            current = os.open(name, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "an owned artifact parent was replaced with a symlink")
        descriptor = os.open(components[-1], regular_flags(), dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(components[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino)
                == (named.st_dev, named.st_ino)
                and 0 < before.st_size <= maximum
                and (exact_size is None or before.st_size == exact_size),
                "reject a symlink, non-file, stale inode, or wrong artifact size")
        digest = hashlib.sha256()
        blocks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(type(block) is bytes and bool(block),
                    "a complete owned source or native artifact was truncated")
            remaining -= len(block)
            digest.update(block)
            blocks.append(block)
        require(os.read(descriptor, 1) == b"",
                "an authenticated owner contains a hidden suffix")
        after = os.fstat(descriptor)
        renamed = os.stat(components[-1], dir_fd=current, follow_symlinks=False)
        observed = digest.hexdigest()
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (after.st_dev, after.st_ino, after.st_size)
                == (renamed.st_dev, renamed.st_ino, renamed.st_size)
                and (expected is None or observed == expected),
                "an exact owned file changed, moved, or failed its caller-pinned hash")
        raw = b"".join(blocks)
        return raw, {
            "relative": relative, "path": root + "/" + relative,
            "sha256": observed, "size_bytes": len(raw),
            "device": after.st_dev, "inode": after.st_ino,
            "mode": stat.S_IMODE(after.st_mode),
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
            for name in relative.split("/"):
                descriptor = os.open(name, directory_flags(), dir_fd=descriptor)
                opened.append(descriptor)
        before = os.fstat(descriptor)
        require(stat.S_ISDIR(before.st_mode),
                "synchronize only an actual private owned directory")
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino),
                "the private activation directory changed during synchronization")
        return {"completed": True, "device": after.st_dev, "inode": after.st_ino}
    finally:
        for item in reversed(opened):
            os.close(item)


def write_fresh(root: str, relative: str, content: bytes) -> dict[str, Any]:
    checked_relative(relative)
    require(type(content) is bytes and 0 < len(content) <= MAX_BINARY_BYTES,
            "write only complete explicitly authenticated private artifact bytes")
    opened: list[int] = []
    file_descriptor: int | None = None
    try:
        current = open_root(root, private=True)
        opened.append(current)
        components = relative.split("/")
        for component in components[:-1]:
            try:
                os.mkdir(component, 0o700, dir_fd=current)
            except FileExistsError:
                pass
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            info = os.fstat(current)
            require(stat.S_ISDIR(info.st_mode)
                    and stat.S_IMODE(info.st_mode) == 0o700
                    and info.st_uid == os.geteuid(),
                    "reject a redirected, shared, or non-private recovery directory")
        file_descriptor = os.open(
            components[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            0o600, dir_fd=current,
        )
        initial = os.fstat(file_descriptor)
        require(stat.S_ISREG(initial.st_mode)
                and stat.S_IMODE(initial.st_mode) == 0o600,
                "an activated artifact is not an exclusively owned private file")
        position = 0
        writes = 0
        while position < len(content):
            count = os.write(file_descriptor, content[position:])
            require(type(count) is int and count > 0,
                    "an exclusively activated artifact was incompletely written")
            position += count
            writes += 1
        os.fsync(file_descriptor)
        finished = os.fstat(file_descriptor)
        require((initial.st_dev, initial.st_ino)
                == (finished.st_dev, finished.st_ino)
                and finished.st_size == len(content),
                "a private artifact inode changed during durable publication")
        os.close(file_descriptor)
        file_descriptor = None
        _, result = read_owned(
            root, relative, sha256(content), maximum=MAX_BINARY_BYTES,
            exact_size=len(content), private=True,
        )
        require((result["device"], result["inode"])
                == (finished.st_dev, finished.st_ino),
                "an exclusively activated artifact was replaced after synchronization")
        return {
            **result,
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
            "write_calls": writes,
        }
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        for descriptor in reversed(opened):
            os.close(descriptor)


def checked_positive_size(value: Any, label: str) -> int:
    require(type(value) is int and 0 < value <= MAX_BINARY_BYTES,
            "require the exact bounded native size: " + label)
    return value


def parse_arguments(arguments: Any) -> dict[str, Any]:
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "supply one exact explicit activation command")
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    journal_recovery = bool(arguments) and (
        arguments[0] == "--recover"
        or arguments[0] == "--restore"
        and "--recovery-journal-sha256" in arguments[1:]
    )
    if journal_recovery:
        options = {
            "--family": "family",
            "--activation-root": "activation_root",
            "--activation-source-sha256": "activation_source_sha256",
            "--activation-protocol-sha256": "activation_protocol_sha256",
            "--recovery-journal-sha256": "recovery_journal_sha256",
        }
        recovered: dict[str, Any] = {"mode": "recover"}
        position = 1
        while position < len(arguments):
            require(position + 1 < len(arguments),
                    "every reportless recovery option requires its exact value")
            option = arguments[position]
            require(option in options and options[option] not in recovered,
                    "reject duplicated, broad, or report-dependent recovery options")
            recovered[options[option]] = arguments[position + 1]
            position += 2
        require(set(recovered) == {"mode", *options.values()},
                "pin the exact family, recovery root, frozen source, and journal")
        family = checked_family(recovered["family"])
        checked_private_root(recovered["activation_root"], family, build=False)
        for key in (
            "activation_source_sha256", "activation_protocol_sha256",
            "recovery_journal_sha256",
        ):
            checked_digest(recovered[key], key)
        return recovered
    if arguments and arguments[0] == "--restore":
        options = {
            "--family": "family",
            "--activation-root": "activation_root",
            "--activation-source-sha256": "activation_source_sha256",
            "--activation-protocol-sha256": "activation_protocol_sha256",
            "--activation-report-sha256": "activation_report_sha256",
            "--activation-receipt-sha256": "activation_receipt_sha256",
        }
        restored: dict[str, Any] = {"mode": "restore"}
        position = 1
        while position < len(arguments):
            require(position + 1 < len(arguments),
                    "every recovery argument requires its exact complete value")
            option = arguments[position]
            require(option in options and options[option] not in restored,
                    "reject duplicated, unknown, or broad recovery arguments")
            restored[options[option]] = arguments[position + 1]
            position += 2
        require(set(restored) == {"mode", *options.values()},
                "pin the family, private recovery root, frozen source, and both proofs")
        family = checked_family(restored["family"])
        checked_private_root(restored["activation_root"], family, build=False)
        for key in (
            "activation_source_sha256", "activation_protocol_sha256",
            "activation_report_sha256", "activation_receipt_sha256",
        ):
            checked_digest(restored[key], key)
        return restored
    require(bool(arguments) and arguments[0] == "--activate",
            "choose --self-test or explicitly authorized --activate")
    singles = {
        "--family": "family",
        "--build-label": "build_label",
        "--build-root": "build_root",
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
    result: dict[str, Any] = {"mode": "activate", "owned_source_sha256": []}
    position = 1
    while position < len(arguments):
        option = arguments[position]
        require(position + 1 < len(arguments),
                "every activation option requires its exact complete value")
        value = arguments[position + 1]
        if option == "--owned-source-sha256":
            result["owned_source_sha256"].append(value)
        else:
            require(option in singles and singles[option] not in result,
                    "reject unknown or duplicated source-activation options")
            key = singles[option]
            if key in {"native_engine_bytes", "native_bridge_bytes"}:
                require(value.isascii() and value.isdecimal()
                        and value == str(int(value)),
                        "a native artifact size must be a canonical positive integer")
                result[key] = checked_positive_size(int(value), key)
            else:
                result[key] = value
        position += 2
    require(set(result) == {"mode", "owned_source_sha256", *singles.values()},
            "pin every activation, V2 archive, native owner, and real build root")
    family = checked_family(result["family"])
    checked_label(result["build_label"])
    checked_private_root(result["build_root"], family, build=True)
    for key in (
        "activation_source_sha256", "activation_protocol_sha256",
        "build_source_sha256", "build_protocol_sha256",
        "build_report_sha256", "build_receipt_sha256",
        "native_engine_sha256", "native_bridge_sha256",
    ):
        checked_digest(result[key], key)
    require(result["build_source_sha256"] == BUILD_SOURCE_SHA256
            and result["build_protocol_sha256"] == BUILD_PROTOCOL_SHA256,
            "activate only the separately frozen, corrected V2 source and protocol")
    parse_owner_pins(family, result["owned_source_sha256"])
    return result


def authenticate_prerequisites(arguments: dict[str, Any]) -> dict[str, Any]:
    family = checked_family(arguments["family"])
    checked_private_root(arguments["build_root"], family, build=True)
    require(sys.executable == PINNED_PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314"
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "use only the isolated pinned stable CPython 3.14.6 without bytecode")
    owned_pins = parse_owner_pins(family, arguments["owned_source_sha256"])
    sources: dict[str, bytes] = {}
    source_evidence: dict[str, dict[str, Any]] = {}
    frozen = (
        ("GOAL.md", GOAL_SHA256),
        (PHASE1_RELATIVE, PHASE1_SHA256),
        (SOURCE_RELATIVE, arguments["activation_source_sha256"]),
        (PROTOCOL_RELATIVE, arguments["activation_protocol_sha256"]),
        (BUILD_SOURCE_RELATIVE, arguments["build_source_sha256"]),
        (BUILD_PROTOCOL_RELATIVE, arguments["build_protocol_sha256"]),
    )
    support: dict[str, dict[str, Any]] = {}
    for relative, expected in frozen:
        _, support[relative] = read_owned(
            ROOT, relative, expected, maximum=MAX_SOURCE_BYTES,
        )
    for relative, expected in owned_pins.items():
        sources[relative], source_evidence[relative] = read_owned(
            ROOT, relative, expected, maximum=MAX_SOURCE_BYTES,
        )
    guard_evidence: dict[str, dict[str, Any]] = {}
    for relative, expected in sorted(ORIGINAL_GUARD_SOURCES.items()):
        _, guard_evidence[relative] = read_owned(
            ROOT, relative, expected, maximum=MAX_SOURCE_BYTES,
        )
    label = checked_label(arguments["build_label"])
    base = EVIDENCE_RELATIVE + "/native-source-build-v2-" + family + "-" + label
    archive, archive_evidence = read_owned(
        ROOT, base + ".json.gz", arguments["build_report_sha256"],
        maximum=MAX_ARCHIVE_BYTES,
    )
    receipt_bytes, receipt_evidence = read_owned(
        ROOT, base + "-publication-receipt.json",
        arguments["build_receipt_sha256"], maximum=MAX_SOURCE_BYTES,
    )
    report = decode_document(bounded_gzip(archive), "version-two build report")
    receipt = decode_document(receipt_bytes, "version-two publication receipt")
    outputs = validate_build_report(report, receipt, archive, arguments, owned_pins)
    for relative, evidence in source_evidence.items():
        recorded = report["owned_source_after"][relative]
        require(evidence["sha256"] == recorded["sha256"]
                and evidence["size_bytes"] == recorded["size_bytes"]
                and evidence["device"] == recorded["device"]
                and evidence["inode"] == recorded["inode"],
                "an actual family source changed after its genuine version-two build")
    native: dict[str, bytes] = {}
    phase_evidence: dict[str, list[dict[str, Any]]] = {}
    for role, actual in outputs.items():
        observed: list[dict[str, Any]] = []
        first: bytes | None = None
        for phase in ("reference-a", "reference-b"):
            relative = phase + "/native/" + actual["file_name"]
            raw, evidence = read_owned(
                arguments["build_root"], relative, actual["sha256"],
                maximum=MAX_BINARY_BYTES, exact_size=actual["size_bytes"],
                private=True,
            )
            if first is None:
                first = raw
            else:
                require(raw == first,
                        "the actual two fresh native files are not byte-identical")
            observed.append(evidence)
        require(len(observed) == 2
                and (observed[0]["device"], observed[0]["inode"])
                != (observed[1]["device"], observed[1]["inode"]),
                "the two actual source phases reused one native file inode")
        require(first is not None, "the exact actual fresh native bytes are missing")
        native[role] = first
        phase_evidence[role] = observed
    return {
        "family": family, "label": label,
        "owned_source_sha256": owned_pins,
        "source_bytes": sources, "source_evidence": source_evidence,
        "guard_evidence": guard_evidence,
        "frozen_support": support,
        "build_archive": archive_evidence,
        "build_receipt": receipt_evidence,
        "native_bytes": native,
        "native_outputs": outputs,
        "native_phase_evidence": phase_evidence,
    }


def zero_effects() -> dict[str, Any]:
    return {
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "reference_processes_started": 0,
        "network_requests": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "candidate_correctness": "NOT MEASURED",
        "winner_selected": False,
    }


def canonical_candidate_directory() -> tuple[int, int]:
    root_descriptor = open_root(ROOT, private=False)
    try:
        candidate_descriptor = os.open(
            "candidates", directory_flags(), dir_fd=root_descriptor,
        )
        information = os.fstat(candidate_descriptor)
        require(stat.S_ISDIR(information.st_mode)
                and information.st_uid == os.geteuid(),
                "promote only into the actual owner-controlled candidate directory")
        return root_descriptor, candidate_descriptor
    except BaseException:
        os.close(root_descriptor)
        raise


def current_canonical(relative: str) -> tuple[bytes, dict[str, Any]] | None:
    checked_relative(relative)
    require(relative.startswith("candidates/")
            and len(relative.split("/")) == 2,
            "inspect only one explicitly approved canonical native artifact")
    root_descriptor, candidate_descriptor = canonical_candidate_directory()
    try:
        basename = relative.split("/", 1)[1]
        try:
            visible = os.stat(basename, dir_fd=candidate_descriptor,
                              follow_symlinks=False)
        except FileNotFoundError:
            return None
        require(stat.S_ISREG(visible.st_mode),
                "refuse a canonical symlink, directory, or non-regular native target")
        return read_owned(ROOT, relative, None, maximum=MAX_BINARY_BYTES)
    finally:
        os.close(candidate_descriptor)
        os.close(root_descriptor)


def same_owner(actual: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(actual.get(key) == expected.get(key)
               for key in (
                   "path", "sha256", "size_bytes", "device", "inode", "mode",
               ))


def verify_canonical_snapshot(relative: str, previous: dict[str, Any] | None) -> None:
    observed = current_canonical(relative)
    if previous is None:
        require(observed is None,
                "an absent canonical native target appeared during promotion")
    else:
        require(observed is not None and same_owner(observed[1], previous),
                "an existing canonical native owner changed before promotion")


def stage_and_replace(relative: str, content: bytes,
                      *, expected_current: dict[str, Any] | None,
                      final_mode: int = 0o600,
                      promotion_intent: dict[str, Any] | None = None) -> dict[str, Any]:
    checked_relative(relative)
    require(relative.startswith("candidates/")
            and len(relative.split("/")) == 2,
            "replace only an exactly fixed canonical family native artifact")
    require(type(content) is bytes and 0 < len(content) <= MAX_BINARY_BYTES,
            "stage only complete actual source-built or recovery-backup bytes")
    require(type(final_mode) is int and 0 <= final_mode <= 0o777,
            "restore only the exactly observed original native permission bits")
    if promotion_intent is not None:
        require(type(promotion_intent) is dict,
                "require one exact pre-replace durable promotion intention")
        family = checked_family(promotion_intent.get("family"))
        checked_private_root(promotion_intent.get("activation_root"),
                             family, build=False)
        role = promotion_intent.get("role")
        require(role in FAMILIES[family]["binaries"]
                and relative == "candidates/"
                + FAMILIES[family]["binaries"][role],
                "reject a broad, cross-family, or unjournaled promotion intention")
        checked_digest(promotion_intent.get("recovery_journal_sha256"),
                       "durable pre-promotion recovery journal")
    expected = sha256(content)
    basename = relative.split("/", 1)[1]
    nonce = os.urandom(18).hex()
    temporary = ".rebar-phase2-verified-" + nonce + "-" + basename
    require(len(temporary) <= 240,
            "the exclusive adjacent native staging name exceeded its safe bound")
    temporary_relative = "candidates/" + temporary
    root_descriptor, candidate_descriptor = canonical_candidate_directory()
    descriptor: int | None = None
    staged_identity: tuple[int, int] | None = None
    intent_evidence: dict[str, Any] | None = None
    replaced = False
    try:
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            0o600, dir_fd=candidate_descriptor,
        )
        original = os.fstat(descriptor)
        require(stat.S_ISREG(original.st_mode)
                and stat.S_IMODE(original.st_mode) == 0o600,
                "the adjacent native staging file was not exclusively created")
        staged_identity = (original.st_dev, original.st_ino)
        offset = 0
        while offset < len(content):
            written = os.write(descriptor, content[offset:])
            require(type(written) is int and written > 0,
                    "the exclusive adjacent native file was truncated")
            offset += written
        if final_mode != 0o600:
            os.fchmod(descriptor, final_mode)
        os.fsync(descriptor)
        finished = os.fstat(descriptor)
        require((finished.st_dev, finished.st_ino) == staged_identity
                and finished.st_size == len(content)
                and stat.S_IMODE(finished.st_mode) == final_mode,
                "the staged native inode or complete bytes changed")
        os.close(descriptor)
        descriptor = None
        _, staged = read_owned(
            ROOT, temporary_relative, expected,
            maximum=MAX_BINARY_BYTES, exact_size=len(content),
        )
        require((staged["device"], staged["inode"]) == staged_identity,
                "the exclusive adjacent native file was replaced")
        verify_canonical_snapshot(relative, expected_current)
        if promotion_intent is not None:
            intended_target = {
                "relative": relative,
                "path": ROOT + "/" + relative,
                "sha256": expected,
                "size_bytes": len(content),
                "device": staged["device"],
                "inode": staged["inode"],
                "mode": final_mode,
            }
            document = {
                "schema": INTENT_SCHEMA,
                "status": "PREPARED",
                "promotion_mode": "recoverable-canonical-promotion",
                "family": promotion_intent["family"],
                "activation_root": promotion_intent["activation_root"],
                "candidate_import_root": ROOT,
                "recovery_journal_sha256":
                    promotion_intent["recovery_journal_sha256"],
                "role": promotion_intent["role"],
                "target": intended_target,
                **zero_effects(),
            }
            intent_evidence = write_fresh(
                promotion_intent["activation_root"],
                "promotion-intent-" + promotion_intent["role"] + ".json",
                canonical(document),
            )
            synchronized = synchronize_directory(
                promotion_intent["activation_root"],
            )
            intent_evidence["directory_fsync_completed"] = synchronized["completed"]
            verify_canonical_snapshot(relative, expected_current)
        os.replace(temporary, basename,
                   src_dir_fd=candidate_descriptor,
                   dst_dir_fd=candidate_descriptor)
        replaced = True
        os.fsync(candidate_descriptor)
        _, promoted = read_owned(
            ROOT, relative, expected,
            maximum=MAX_BINARY_BYTES, exact_size=len(content),
        )
        require((promoted["device"], promoted["inode"]) == staged_identity,
                "the atomically promoted native inode was replaced")
        result = {
            **promoted,
            "atomic_replace_completed": True,
            "adjacent_exclusive_stage_verified": True,
            "candidate_directory_fsync_completed": True,
        }
        if intent_evidence is not None:
            result["promotion_intent"] = intent_evidence
        return result
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if staged_identity is not None and not replaced:
            try:
                observed = os.stat(temporary,
                                   dir_fd=candidate_descriptor,
                                   follow_symlinks=False)
            except FileNotFoundError:
                observed = None
            if observed is not None:
                require(stat.S_ISREG(observed.st_mode)
                        and (observed.st_dev, observed.st_ino) == staged_identity,
                        "refuse to remove a substituted native staging artifact")
                os.unlink(temporary, dir_fd=candidate_descriptor)
                os.fsync(candidate_descriptor)
        os.close(candidate_descriptor)
        os.close(root_descriptor)


def build_provenance(prerequisite: dict[str, Any],
                     arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": BUILD_SCHEMA,
        "family": prerequisite["family"],
        "label": prerequisite["label"],
        "source_sha256": arguments["build_source_sha256"],
        "protocol_sha256": arguments["build_protocol_sha256"],
        "archive_relative": prerequisite["build_archive"]["relative"],
        "archive_sha256": prerequisite["build_archive"]["sha256"],
        "receipt_relative": prerequisite["build_receipt"]["relative"],
        "receipt_sha256": prerequisite["build_receipt"]["sha256"],
        "build_root": arguments["build_root"],
        "independent_fresh_phase_count": 2,
        "actual_versioned_symbol_streams_verified": True,
    }


def prepare_recovery_journal(
    root: str, prerequisite: dict[str, Any], arguments: dict[str, Any],
    build: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    family = prerequisite["family"]
    entries: dict[str, dict[str, Any]] = {}
    for role, output in prerequisite["native_outputs"].items():
        relative = "candidates/" + output["file_name"]
        existing = current_canonical(relative)
        backup: dict[str, Any] | None = None
        original: dict[str, Any] | None = None
        if existing is not None:
            previous_bytes, original = existing
            backup = write_fresh(root, "backups/" + relative, previous_bytes)
            require(backup["sha256"] == original["sha256"]
                    and backup["size_bytes"] == original["size_bytes"],
                    "an original native binary was not preserved byte for byte")
        entries[role] = {
            "role": role,
            "target_relative": relative,
            "target_path": ROOT + "/" + relative,
            "originally_present": existing is not None,
            "original_owner": original,
            "backup": backup,
            "promoted_sha256": output["sha256"],
            "promoted_size_bytes": output["size_bytes"],
        }
    for entry in entries.values():
        verify_canonical_snapshot(entry["target_relative"],
                                  entry["original_owner"])
    if any(value["originally_present"] for value in entries.values()):
        synchronize_directory(root, "backups/candidates")
        synchronize_directory(root, "backups")
    journal = {
        "schema": JOURNAL_SCHEMA,
        "status": "PREPARED",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family,
        "label": prerequisite["label"],
        "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_source_sha256": arguments["activation_source_sha256"],
        "activation_protocol_sha256": arguments["activation_protocol_sha256"],
        "source_build_v2": build,
        "owned_source_sha256": prerequisite["owned_source_sha256"],
        "backup_entries": entries,
        **zero_effects(),
    }
    journal_owner = write_fresh(root, JOURNAL_NAME, canonical(journal))
    journal_sync = synchronize_directory(root)
    return journal, {
        **journal_owner,
        "directory_fsync_completed": journal_sync["completed"],
    }


def validate_promotion_intent(
    document: Any, *, family: str, root: str, role: str,
    journal_sha256: str, current: dict[str, Any],
) -> dict[str, Any]:
    family = checked_family(family)
    checked_private_root(root, family, build=False)
    checked_digest(journal_sha256, "immutable pre-promotion recovery journal")
    require(role in FAMILIES[family]["binaries"],
            "reject a foreign durable promotion intention")
    require(type(document) is dict and document.get("schema") == INTENT_SCHEMA
            and document.get("status") == "PREPARED"
            and document.get("promotion_mode") == "recoverable-canonical-promotion"
            and document.get("family") == family
            and document.get("activation_root") == root
            and document.get("candidate_import_root") == ROOT
            and document.get("recovery_journal_sha256") == journal_sha256
            and document.get("role") == role,
            "require the exact durable pre-replace native-inode intention")
    target = document.get("target")
    relative = "candidates/" + FAMILIES[family]["binaries"][role]
    require(type(target) is dict and type(current) is dict
            and target.get("relative") == relative
            and target.get("path") == ROOT + "/" + relative
            and same_owner(target, current),
            "refuse a promoted native inode absent from its durable intention")
    checked_digest(target.get("sha256"), relative)
    checked_positive_size(target.get("size_bytes"), relative)
    require(type(target.get("mode")) is int
            and 0 <= target["mode"] <= 0o777,
            "the exact pre-replace native permissions were not journaled")
    require(all(document.get(key) == expected
                and type(document.get(key)) is type(expected)
                for key, expected in zero_effects().items()),
            "a durable promotion intention reports candidate or timing effects")
    return dict(target)


def classify_recovery_state(entry: Any, current: Any) -> str:
    require(type(entry) is dict and type(entry.get("originally_present")) is bool,
            "classify only an exact honest canonical recovery entry")
    original = entry.get("original_owner")
    promoted_digest = checked_digest(entry.get("promoted_sha256"),
                                     "journaled promoted artifact")
    promoted_size = checked_positive_size(entry.get("promoted_size_bytes"),
                                          "journaled promoted artifact")
    if current is None:
        require(not entry["originally_present"],
                "an originally present canonical artifact disappeared")
        return "originally-absent"
    require(type(current) is dict
            and type(current.get("size_bytes")) is int
            and type(current.get("mode")) is int,
            "reject an incomplete or forged current canonical artifact")
    if entry["originally_present"]:
        require(type(original) is dict,
                "an existing original native file has no recovery identity")
        if same_owner(current, original):
            return "already-original"
    if (current.get("sha256") == promoted_digest
            and current["size_bytes"] == promoted_size):
        return "source-verified-promoted"
    raise ActivationError(
        "refuse to overwrite an unrelated changed canonical native file"
    )


def authenticate_promotion_intents(
    root: str, journal: dict[str, Any], journal_sha256: str,
) -> dict[str, dict[str, Any]]:
    family = checked_family(journal.get("family"))
    checked_private_root(root, family, build=False)
    checked_digest(journal_sha256, "crash-recovery journal")
    intents: dict[str, dict[str, Any]] = {}
    for role, filename in FAMILIES[family]["binaries"].items():
        entry = journal["backup_entries"][role]
        current = current_canonical("candidates/" + filename)
        state = classify_recovery_state(
            entry, current[1] if current is not None else None,
        )
        if state != "source-verified-promoted":
            continue
        require(current is not None,
                "the source-verified promoted target disappeared")
        relative = "promotion-intent-" + role + ".json"
        raw, owner = read_owned(
            root, relative, None, maximum=MAX_SOURCE_BYTES, private=True,
        )
        require(owner.get("mode") == 0o600,
                "the durable promoted-inode intention must be owner-only")
        document = decode_document(raw, "durable pre-replace promotion intention")
        actual = validate_promotion_intent(
            document, family=family, root=root, role=role,
            journal_sha256=journal_sha256, current=current[1],
        )
        intents[role] = {
            "intent": owner,
            "target": actual,
        }
    return intents


def restore_journal_targets(
    root: str, journal: dict[str, Any], *,
    promotion_intents: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    require(type(journal) is dict and journal.get("schema") == JOURNAL_SCHEMA
            and journal.get("status") == "PREPARED"
            and journal.get("promotion_mode") == "recoverable-canonical-promotion"
            and journal.get("candidate_import_root") == ROOT
            and journal.get("activation_root") == root,
            "require the exact durable fixed-target canonical recovery journal")
    family = checked_family(journal.get("family"))
    checked_private_root(root, family, build=False)
    entries = journal.get("backup_entries")
    roles = FAMILIES[family]["binaries"]
    require(type(entries) is dict and set(entries) == set(roles),
            "the durable recovery journal omitted a canonical native role")
    recovery: dict[str, tuple[dict[str, Any], bytes | None,
                               dict[str, Any] | None]] = {}
    for role, filename in roles.items():
        entry = entries[role]
        relative = "candidates/" + filename
        require(type(entry) is dict and entry.get("role") == role
                and entry.get("target_relative") == relative
                and entry.get("target_path") == ROOT + "/" + relative
                and type(entry.get("originally_present")) is bool,
                "reject a foreign, broad, or substituted recovery target")
        promoted_digest = checked_digest(entry.get("promoted_sha256"), filename)
        promoted_size = checked_positive_size(entry.get("promoted_size_bytes"),
                                              filename)
        original = entry.get("original_owner")
        backup = entry.get("backup")
        backup_bytes: bytes | None = None
        if entry["originally_present"]:
            require(type(original) is dict and type(backup) is dict
                    and original.get("relative") == relative
                    and original.get("path") == ROOT + "/" + relative
                    and backup.get("relative") == "backups/" + relative
                    and backup.get("sha256") == original.get("sha256")
                    and backup.get("size_bytes") == original.get("size_bytes")
                    and backup.get("exclusive_creation") is True
                    and backup.get("same_inode_readback_verified") is True
                    and backup.get("file_fsync_completed") is True,
                    "the original canonical artifact has no genuine durable backup")
            backup_bytes, actual_backup = read_owned(
                root, backup["relative"], backup["sha256"],
                maximum=MAX_BINARY_BYTES,
                exact_size=backup["size_bytes"], private=True,
            )
            require(same_owner(actual_backup, backup),
                    "the exact same-inode canonical recovery backup changed")
        else:
            require(original is None and backup is None,
                    "an originally absent native target invented a backup")
        current = current_canonical(relative)
        state = classify_recovery_state(
            entry, current[1] if current is not None else None,
        )
        if state == "source-verified-promoted" and promotion_intents is not None:
            intent = promotion_intents.get(role)
            require(type(intent) is dict and current is not None
                    and type(intent.get("target")) is dict
                    and same_owner(intent["target"], current[1]),
                    "refuse to recover a canonical inode absent from its durable intent")
        recovery[role] = (entry, backup_bytes,
                          current[1] if current is not None else None)
    restored: dict[str, dict[str, Any]] = {}
    for role in reversed(tuple(roles)):
        entry, backup_bytes, _ = recovery[role]
        relative = entry["target_relative"]
        current = current_canonical(relative)
        if entry["originally_present"]:
            require(backup_bytes is not None,
                    "the complete original canonical recovery bytes are missing")
            if current is not None and same_owner(
                current[1], entry["original_owner"],
            ):
                restored[role] = {
                    **current[1], "restored_from_verified_backup": True,
                }
                continue
            require(current is not None,
                    "the promoted canonical artifact disappeared during rollback")
            recovered = stage_and_replace(relative, backup_bytes,
                                          expected_current=current[1],
                                          final_mode=entry["original_owner"]["mode"])
            require(recovered["sha256"] == entry["original_owner"]["sha256"]
                    and recovered["size_bytes"]
                    == entry["original_owner"]["size_bytes"]
                    and recovered["mode"] == entry["original_owner"]["mode"],
                    "the exact historical native binary was not restored")
            restored[role] = {**recovered,
                              "restored_from_verified_backup": True}
        elif current is not None:
            require(current[1]["sha256"] == entry["promoted_sha256"]
                    and current[1]["size_bytes"]
                    == entry["promoted_size_bytes"],
                    "refuse to remove a non-promoted canonical native artifact")
            root_descriptor, candidate_descriptor = canonical_candidate_directory()
            try:
                basename = relative.split("/", 1)[1]
                visible = os.stat(basename, dir_fd=candidate_descriptor,
                                  follow_symlinks=False)
                require((visible.st_dev, visible.st_ino)
                        == (current[1]["device"], current[1]["inode"]),
                        "the exact promoted native inode changed before rollback")
                os.unlink(basename, dir_fd=candidate_descriptor)
                os.fsync(candidate_descriptor)
            finally:
                os.close(candidate_descriptor)
                os.close(root_descriptor)
            require(current_canonical(relative) is None,
                    "the previously absent native target was not restored")
            restored[role] = {
                "relative": relative,
                "path": ROOT + "/" + relative,
                "restored_original_absence": True,
                "candidate_directory_fsync_completed": True,
            }
        else:
            restored[role] = {
                "relative": relative,
                "path": ROOT + "/" + relative,
                "restored_original_absence": True,
                "candidate_directory_fsync_completed": True,
            }
    return restored


def activate(arguments: dict[str, Any]) -> dict[str, Any]:
    prerequisite = authenticate_prerequisites(arguments)
    family = prerequisite["family"]
    build = build_provenance(prerequisite, arguments)
    root = tempfile.mkdtemp(prefix=PRIVATE_PREFIX + family + "-", dir="/tmp")
    checked_private_root(root, family, build=False)
    descriptor = open_root(root, private=True)
    os.close(descriptor)
    journal, journal_owner = prepare_recovery_journal(
        root, prerequisite, arguments, build,
    )
    try:
        targets: dict[str, dict[str, Any]] = {}
        for role, output in prerequisite["native_outputs"].items():
            entry = journal["backup_entries"][role]
            final_mode = (entry["original_owner"]["mode"]
                          if entry["originally_present"] else 0o600)
            promoted = stage_and_replace(
                entry["target_relative"], prerequisite["native_bytes"][role],
                expected_current=entry["original_owner"],
                final_mode=final_mode,
                promotion_intent={
                    "family": family,
                    "activation_root": root,
                    "role": role,
                    "recovery_journal_sha256": journal_owner["sha256"],
                },
            )
            require(promoted["sha256"] == output["sha256"]
                    and promoted["size_bytes"] == output["size_bytes"],
                    "the promoted canonical artifact differs from both V2 builds")
            targets[role] = {
                **promoted,
                "role": role,
                "elf": output["elf"],
                "source_build_phases": prerequisite["native_phase_evidence"][role],
            }
        for role, target in targets.items():
            _, current = read_owned(
                ROOT, target["relative"], target["sha256"],
                maximum=MAX_BINARY_BYTES,
                exact_size=target["size_bytes"],
            )
            require(same_owner(current, target),
                    "a promoted family native owner changed during activation")
        for relative, expected in prerequisite["owned_source_sha256"].items():
            _, evidence = read_owned(
                ROOT, relative, expected, maximum=MAX_SOURCE_BYTES,
            )
            require(same_owner(evidence, prerequisite["source_evidence"][relative]),
                    "an owned family source changed during canonical promotion")
        adapter = {
            **prerequisite["source_evidence"][FAMILIES[family]["adapter"]],
            "module": FAMILIES[family]["module"],
        }
        report: dict[str, Any] = {
            "schema": SCHEMA,
            "status": "PASS",
            "promotion_mode": "recoverable-canonical-promotion",
            "family": family,
            "label": prerequisite["label"],
            "activation_root": root,
            "candidate_import_root": ROOT,
            "activation_source_sha256": arguments["activation_source_sha256"],
            "activation_protocol_sha256": arguments["activation_protocol_sha256"],
            "source_build_v2": build,
            "owned_source_sha256": prerequisite["owned_source_sha256"],
            "source_owners": prerequisite["source_evidence"],
            "adapter": adapter,
            "canonical_targets": targets,
            "backup_entries": journal["backup_entries"],
            "recovery_journal": journal_owner,
            "original_guard_sources": prerequisite["guard_evidence"],
            "frozen_support_inputs": prerequisite["frozen_support"],
            **zero_effects(),
        }
        report_record = write_fresh(root, REPORT_NAME, canonical(report))
        report_directory = synchronize_directory(root)
        receipt: dict[str, Any] = {
            "schema": RECEIPT_SCHEMA,
            "status": "PASS",
            "activation_status": "PASS",
            "promotion_mode": "recoverable-canonical-promotion",
            "family": family,
            "label": prerequisite["label"],
            "activation_root": root,
            "candidate_import_root": ROOT,
            "activation_source_sha256": arguments["activation_source_sha256"],
            "activation_protocol_sha256": arguments["activation_protocol_sha256"],
            "source_build_v2": build,
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
    except BaseException as error:
        try:
            intents = authenticate_promotion_intents(
                root, journal, journal_owner["sha256"],
            )
            restore_journal_targets(root, journal, promotion_intents=intents)
        except BaseException as rollback_error:
            raise ActivationError(
                "canonical promotion failed and automatic recovery needs the "
                "preserved private journal " + root + "/" + JOURNAL_NAME
                + ": " + str(rollback_error)
            ) from error
        raise ActivationError(
            "canonical promotion failed; every exact previous native artifact "
            "was automatically restored from " + root + "/" + JOURNAL_NAME
        ) from error
    return {
        "schema": SCHEMA + "-activation-result",
        "status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family,
        "activation_root": root,
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
        "source_build_v2": build,
        **zero_effects(),
    }


def validate_recorded_elf(family: str, role: str, value: Any) -> dict[str, Any]:
    require(type(value) is dict,
            "require the complete actual version-aware promoted ELF audit")
    records = value.get("symbol_records")
    count = value.get("symbol_count")
    require(type(records) is list and type(count) is int
            and 0 < count <= 131_072 and len(records) == count,
            "the complete original GNU symbol records were omitted")
    exports: set[str] = set()
    undefined: set[str] = set()
    versions = 0
    for index, row in enumerate(records):
        require(type(row) is dict and row.get("index") == index,
                "reject a reordered, repeated, or omitted real GNU symbol row")
        name = row.get("name")
        section = row.get("section")
        binding = row.get("binding")
        if name is None:
            require(index == 0 and row.get("raw_name") is None
                    and section == "UND" and binding == "LOCAL"
                    and row.get("version") is None
                    and row.get("default_version") is False
                    and row.get("version_index") is None,
                    "reject a disguised null or GNU version-index pseudo-symbol")
            continue
        parsed, version, default = checked_symbol_name(row.get("raw_name"))
        require(parsed == name and row.get("version") == version
                and row.get("default_version") is default,
                "the actual GNU symbol name or version was substituted")
        if version is not None:
            versions += 1
        trailer = row.get("version_index")
        require(trailer is None
                or version is not None and type(trailer) is int and trailer > 0,
                "reject a malformed actual GNU symbol-version index")
        if section == "UND":
            undefined.add(name)
        elif binding in {"GLOBAL", "WEAK", "UNIQUE", "GNU_UNIQUE"}:
            exports.add(name)
    require(value.get("exports") == sorted(exports)
            and value.get("undefined") == sorted(undefined)
            and value.get("versioned_symbol_count") == versions,
            "the full actual versioned ELF symbol graph changed")
    for key in ("needed", "runpath", "soname"):
        entries = value.get(key)
        require(type(entries) is list
                and all(type(item) is str for item in entries)
                and len(entries) == len(set(entries)),
                "reject incomplete or duplicated actual ELF dynamic records")
    dynamic = {
        "needed": value["needed"],
        "runpath": value["runpath"],
        "rpath": [],
        "soname": value["soname"],
    }
    symbols = {
        "exports": sorted(exports),
        "undefined": sorted(undefined),
        "symbol_count": count,
        "versioned_symbol_count": versions,
        "symbol_records": records,
    }
    observed = validate_elf(family, role, dynamic, symbols)
    require(value == observed,
            "the promoted binary's actual audited native ownership changed")
    return observed


def validate_recovery_journal(journal: Any, *, arguments: dict[str, Any]) -> dict[str, Any]:
    family = checked_family(arguments.get("family"))
    root = checked_private_root(arguments.get("activation_root"), family,
                                build=False)
    require(type(journal) is dict and journal.get("schema") == JOURNAL_SCHEMA
            and journal.get("status") == "PREPARED"
            and journal.get("promotion_mode") == "recoverable-canonical-promotion"
            and journal.get("family") == family
            and journal.get("activation_root") == root
            and journal.get("candidate_import_root") == ROOT
            and journal.get("activation_source_sha256")
            == arguments.get("activation_source_sha256")
            and journal.get("activation_protocol_sha256")
            == arguments.get("activation_protocol_sha256")
            and sha256(canonical(journal))
            == arguments.get("recovery_journal_sha256"),
            "require the exact independently pinned reportless recovery journal")
    require(all(journal.get(key) == expected
                and type(journal.get(key)) is type(expected)
                for key, expected in zero_effects().items()),
            "a crash-recovery journal claims actual candidate or timing effects")
    provenance = journal.get("source_build_v2")
    require(type(provenance) is dict
            and provenance.get("schema") == BUILD_SCHEMA
            and provenance.get("family") == family
            and provenance.get("source_sha256") == BUILD_SOURCE_SHA256
            and provenance.get("protocol_sha256") == BUILD_PROTOCOL_SHA256
            and provenance.get("independent_fresh_phase_count") == 2
            and provenance.get("actual_versioned_symbol_streams_verified") is True,
            "a crash-recovery journal lacks the corrected genuine V2 source build")
    label = checked_label(provenance.get("label"))
    require(journal.get("label") == label,
            "the exact reportless source-build label was substituted")
    checked_private_root(provenance.get("build_root"), family, build=True)
    checked_digest(provenance.get("archive_sha256"), "reportless V2 archive")
    checked_digest(provenance.get("receipt_sha256"), "reportless V2 receipt")
    base = EVIDENCE_RELATIVE + "/native-source-build-v2-" + family + "-" + label
    require(provenance.get("archive_relative") == base + ".json.gz"
            and provenance.get("receipt_relative")
            == base + "-publication-receipt.json",
            "the actual reportless recovery points to a forged V2 publication")
    pins = journal.get("owned_source_sha256")
    require(type(pins) is dict and set(pins) == set(FAMILIES[family]["owners"]),
            "a reportless journal must preserve the complete V2 source closure")
    for relative, digest in pins.items():
        checked_relative(relative)
        checked_digest(digest, relative)
    entries = journal.get("backup_entries")
    roles = FAMILIES[family]["binaries"]
    require(type(entries) is dict and set(entries) == set(roles),
            "a crash-recovery journal omitted a fixed canonical native role")
    for role, filename in roles.items():
        relative = "candidates/" + filename
        entry = entries[role]
        require(type(entry) is dict and entry.get("role") == role
                and entry.get("target_relative") == relative
                and entry.get("target_path") == ROOT + "/" + relative
                and type(entry.get("originally_present")) is bool,
                "reject a broad or substituted crash-recovery target")
        checked_digest(entry.get("promoted_sha256"), "promoted " + relative)
        checked_positive_size(entry.get("promoted_size_bytes"), relative)
        original = entry.get("original_owner")
        backup = entry.get("backup")
        if entry["originally_present"]:
            require(type(original) is dict and type(backup) is dict
                    and original.get("relative") == relative
                    and original.get("path") == ROOT + "/" + relative
                    and type(original.get("size_bytes")) is int
                    and 0 < original["size_bytes"] <= MAX_BINARY_BYTES
                    and type(original.get("device")) is int
                    and type(original.get("inode")) is int
                    and type(original.get("mode")) is int
                    and 0 <= original["mode"] <= 0o777
                    and backup.get("relative") == "backups/" + relative
                    and backup.get("path") == root + "/backups/" + relative
                    and backup.get("sha256") == original.get("sha256")
                    and backup.get("size_bytes") == original["size_bytes"]
                    and type(backup.get("device")) is int
                    and type(backup.get("inode")) is int
                    and backup.get("mode") == 0o600
                    and backup.get("exclusive_creation") is True
                    and backup.get("same_inode_readback_verified") is True
                    and backup.get("file_fsync_completed") is True,
                    "a crash recovery requires an exact durable original-file backup")
            checked_digest(original.get("sha256"), "original " + relative)
        else:
            require(original is None and backup is None,
                    "an originally absent native target fabricated a recovery backup")
    return {
        "schema": SCHEMA + "-authenticated-recovery-journal",
        "status": "PASS",
        "family": family,
        "activation_root": root,
        "candidate_import_root": ROOT,
        "source_build_v2": provenance,
        "owned_source_sha256": pins,
        "backup_entries": entries,
    }


def validate_activation_documents(
    report: Any, receipt: Any, journal: Any, *, arguments: dict[str, Any],
) -> dict[str, Any]:
    family = checked_family(arguments.get("family"))
    root = checked_private_root(arguments.get("activation_root"), family,
                                build=False)
    require(type(report) is dict and type(receipt) is dict
            and type(journal) is dict
            and report.get("schema") == SCHEMA
            and receipt.get("schema") == RECEIPT_SCHEMA
            and journal.get("schema") == JOURNAL_SCHEMA
            and report.get("status") == "PASS"
            and receipt.get("status") == "PASS"
            and receipt.get("activation_status") == "PASS"
            and journal.get("status") == "PREPARED",
            "require the complete real activation report, receipt, and recovery journal")
    for document in (report, receipt, journal):
        require(document.get("promotion_mode") == "recoverable-canonical-promotion"
                and document.get("family") == family
                and document.get("label") == report.get("label")
                and document.get("activation_root") == root
                and document.get("candidate_import_root") == ROOT
                and document.get("activation_source_sha256")
                == arguments.get("activation_source_sha256")
                and document.get("activation_protocol_sha256")
                == arguments.get("activation_protocol_sha256"),
                "require genuine immutable original-V5 canonical promotion")
        expected_effects = zero_effects()
        require(all(document.get(key) == expected
                    and (type(document.get(key)) is type(expected))
                    for key, expected in expected_effects.items()),
                "activation loaded a candidate, used a clock, or accessed a holdout")
    plain = canonical(report)
    report_hash = sha256(plain)
    require(report_hash == arguments.get("activation_report_sha256")
            and receipt.get("report_relative") == REPORT_NAME
            and receipt.get("report_sha256") == report_hash
            and receipt.get("report_bytes") == len(plain)
            and sha256(canonical(receipt))
            == arguments.get("activation_receipt_sha256"),
            "the caller-pinned canonical activation report or receipt changed")
    publication = receipt.get("report_publication")
    require(type(publication) is dict
            and publication.get("relative") == REPORT_NAME
            and publication.get("path") == root + "/" + REPORT_NAME
            and publication.get("sha256") == report_hash
            and publication.get("size_bytes") == len(plain)
            and publication.get("exclusive_creation") is True
            and publication.get("same_inode_readback_verified") is True
            and publication.get("file_fsync_completed") is True,
            "the actual canonical activation report was not exclusively durable")
    synchronized = receipt.get("report_directory_fsync")
    require(type(synchronized) is dict
            and synchronized.get("completed") is True
            and type(synchronized.get("device")) is int
            and type(synchronized.get("inode")) is int,
            "the actual private canonical-proof directory was not synchronized")
    require(receipt.get("receipt_self_publication") == "NOT CLAIMED",
            "an activation receipt cannot authenticate its own publication")
    recorded_journal = report.get("recovery_journal")
    require(type(recorded_journal) is dict
            and recorded_journal == receipt.get("recovery_journal")
            and recorded_journal.get("relative") == JOURNAL_NAME
            and recorded_journal.get("path") == root + "/" + JOURNAL_NAME
            and recorded_journal.get("sha256") == sha256(canonical(journal))
            and recorded_journal.get("size_bytes") == len(canonical(journal))
            and recorded_journal.get("exclusive_creation") is True
            and recorded_journal.get("same_inode_readback_verified") is True
            and recorded_journal.get("file_fsync_completed") is True
            and recorded_journal.get("directory_fsync_completed") is True,
            "a complete durable pre-promotion rollback journal is mandatory")
    validated_journal = validate_recovery_journal(
        journal,
        arguments={
            "family": family,
            "activation_root": root,
            "activation_source_sha256": arguments["activation_source_sha256"],
            "activation_protocol_sha256": arguments["activation_protocol_sha256"],
            "recovery_journal_sha256": recorded_journal["sha256"],
        },
    )
    require(validated_journal["status"] == "PASS",
            "the separately recoverable pre-promotion journal did not pass")
    provenance = report.get("source_build_v2")
    require(type(provenance) is dict
            and provenance == receipt.get("source_build_v2")
            and provenance == journal.get("source_build_v2")
            and provenance.get("schema") == BUILD_SCHEMA
            and provenance.get("family") == family
            and provenance.get("source_sha256") == BUILD_SOURCE_SHA256
            and provenance.get("protocol_sha256") == BUILD_PROTOCOL_SHA256
            and provenance.get("independent_fresh_phase_count") == 2
            and provenance.get("actual_versioned_symbol_streams_verified") is True,
            "the canonical promotion is not bound to the corrected genuine V2 build")
    checked_label(provenance.get("label"))
    require(report.get("label") == provenance["label"],
            "the exact published version-two family build label changed")
    checked_private_root(provenance.get("build_root"), family, build=True)
    checked_digest(provenance.get("archive_sha256"), "published V2 archive")
    checked_digest(provenance.get("receipt_sha256"), "published V2 receipt")
    require(provenance.get("archive_relative")
            == EVIDENCE_RELATIVE + "/native-source-build-v2-" + family
            + "-" + provenance["label"] + ".json.gz"
            and provenance.get("receipt_relative")
            == EVIDENCE_RELATIVE + "/native-source-build-v2-" + family
            + "-" + provenance["label"] + "-publication-receipt.json",
            "a historical or cross-family V2 publication was substituted")
    owners = report.get("owned_source_sha256")
    require(type(owners) is dict
            and owners == receipt.get("owned_source_sha256")
            and owners == journal.get("owned_source_sha256")
            and set(owners) == set(FAMILIES[family]["owners"]),
            "the exact independently built canonical family closure was omitted")
    frozen = report.get("frozen_support_inputs")
    require(type(frozen) is dict,
            "the actual immutable activation prerequisite closure is mandatory")
    for relative, expected in (
        ("GOAL.md", GOAL_SHA256),
        (PHASE1_RELATIVE, PHASE1_SHA256),
        (SOURCE_RELATIVE, arguments["activation_source_sha256"]),
        (PROTOCOL_RELATIVE, arguments["activation_protocol_sha256"]),
        (BUILD_SOURCE_RELATIVE, BUILD_SOURCE_SHA256),
        (BUILD_PROTOCOL_RELATIVE, BUILD_PROTOCOL_SHA256),
    ):
        owner = frozen.get(relative)
        require(type(owner) is dict and owner.get("relative") == relative
                and owner.get("path") == ROOT + "/" + relative
                and owner.get("sha256") == expected
                and type(owner.get("size_bytes")) is int
                and 0 < owner["size_bytes"] <= MAX_SOURCE_BYTES
                and type(owner.get("device")) is int
                and type(owner.get("inode")) is int,
                "a frozen activation, original oracle, or V2 support source changed")
    source_records = report.get("source_owners")
    require(type(source_records) is dict
            and source_records == receipt.get("source_owners")
            and set(source_records) == set(owners),
            "every actual canonical source owner must be recorded")
    for relative, digest in owners.items():
        checked_digest(digest, relative)
        evidence = source_records[relative]
        require(type(evidence) is dict
                and evidence.get("relative") == relative
                and evidence.get("path") == ROOT + "/" + relative
                and evidence.get("sha256") == digest
                and type(evidence.get("size_bytes")) is int
                and 0 < evidence["size_bytes"] <= MAX_SOURCE_BYTES
                and type(evidence.get("device")) is int
                and type(evidence.get("inode")) is int
                and type(evidence.get("mode")) is int
                and 0 <= evidence["mode"] <= 0o777,
                "reject a missing or private-rebound canonical family source")
    adapter = report.get("adapter")
    adapter_relative = FAMILIES[family]["adapter"]
    require(type(adapter) is dict
            and adapter.get("module") == FAMILIES[family]["module"]
            and {key: value for key, value in adapter.items() if key != "module"}
            == source_records[adapter_relative],
            "the canonical candidate must import its exact unchanged source adapter")
    guards = report.get("original_guard_sources")
    require(type(guards) is dict
            and guards == receipt.get("original_guard_sources")
            and set(guards) == set(ORIGINAL_GUARD_SOURCES),
            "all original V1–V5 guards must remain at their immutable project root")
    for relative, digest in ORIGINAL_GUARD_SOURCES.items():
        owner = guards[relative]
        require(type(owner) is dict and owner.get("relative") == relative
                and owner.get("path") == ROOT + "/" + relative
                and owner.get("sha256") == digest,
                "an original V5 dependency was copied, rebound, or changed")
    targets = report.get("canonical_targets")
    backups = report.get("backup_entries")
    roles = FAMILIES[family]["binaries"]
    require(type(targets) is dict and set(targets) == set(roles)
            and targets == receipt.get("canonical_targets")
            and type(backups) is dict and set(backups) == set(roles)
            and backups == receipt.get("backup_entries")
            and backups == journal.get("backup_entries"),
            "the full canonical target or rollback closure is missing")
    for role, filename in roles.items():
        relative = "candidates/" + filename
        target = targets[role]
        require(type(target) is dict and target.get("role") == role
                and target.get("relative") == relative
                and target.get("path") == ROOT + "/" + relative
                and type(target.get("size_bytes")) is int
                and 0 < target["size_bytes"] <= MAX_BINARY_BYTES
                and type(target.get("device")) is int
                and type(target.get("inode")) is int
                and type(target.get("mode")) is int
                and 0 <= target["mode"] <= 0o777
                and target.get("atomic_replace_completed") is True
                and target.get("adjacent_exclusive_stage_verified") is True
                and target.get("candidate_directory_fsync_completed") is True,
                "an exact canonical native artifact was not atomically promoted")
        checked_digest(target.get("sha256"), relative)
        validate_recorded_elf(family, role, target.get("elf"))
        intention = target.get("promotion_intent")
        require(type(intention) is dict
                and intention.get("relative")
                == "promotion-intent-" + role + ".json"
                and intention.get("path")
                == root + "/promotion-intent-" + role + ".json"
                and type(intention.get("size_bytes")) is int
                and 0 < intention["size_bytes"] <= MAX_SOURCE_BYTES
                and type(intention.get("device")) is int
                and type(intention.get("inode")) is int
                and intention.get("mode") == 0o600
                and intention.get("exclusive_creation") is True
                and intention.get("same_inode_readback_verified") is True
                and intention.get("file_fsync_completed") is True
                and intention.get("directory_fsync_completed") is True,
                "the promoted native inode has no durable pre-replace intention")
        checked_digest(intention.get("sha256"), "promotion intention " + role)
        phases = target.get("source_build_phases")
        require(type(phases) is list and len(phases) == 2,
                "both actual fresh source-built phase files are mandatory")
        for number, phase in enumerate(phases):
            expected_relative = (
                ("reference-a", "reference-b")[number] + "/native/" + filename
            )
            require(type(phase) is dict
                    and phase.get("relative") == expected_relative
                    and phase.get("path")
                    == provenance["build_root"] + "/" + expected_relative
                    and phase.get("sha256") == target["sha256"]
                    and phase.get("size_bytes") == target["size_bytes"]
                    and type(phase.get("device")) is int
                    and type(phase.get("inode")) is int,
                    "the promoted artifact is not the exact real V2 phase binary")
        require((phases[0]["device"], phases[0]["inode"])
                != (phases[1]["device"], phases[1]["inode"]),
                "the two genuine build phases shared one native-file inode")
        entry = backups[role]
        require(type(entry) is dict and entry.get("role") == role
                and entry.get("target_relative") == relative
                and entry.get("target_path") == ROOT + "/" + relative
                and type(entry.get("originally_present")) is bool
                and entry.get("promoted_sha256") == target["sha256"]
                and entry.get("promoted_size_bytes") == target["size_bytes"],
                "a previous canonical native artifact has no honest recovery entry")
        original = entry.get("original_owner")
        backup = entry.get("backup")
        if entry["originally_present"]:
            require(type(original) is dict and type(backup) is dict
                    and original.get("relative") == relative
                    and original.get("path") == ROOT + "/" + relative
                    and backup.get("relative") == "backups/" + relative
                    and backup.get("path") == root + "/backups/" + relative
                    and backup.get("sha256") == original.get("sha256")
                    and backup.get("size_bytes") == original.get("size_bytes")
                    and type(backup.get("device")) is int
                    and type(backup.get("inode")) is int
                    and backup.get("mode") == 0o600
                    and type(original.get("mode")) is int
                    and 0 <= original["mode"] <= 0o777
                    and target.get("mode") == original["mode"]
                    and backup.get("exclusive_creation") is True
                    and backup.get("same_inode_readback_verified") is True
                    and backup.get("file_fsync_completed") is True,
                    "an existing native artifact has no exact durable owned backup")
            checked_digest(original.get("sha256"), "original " + relative)
        else:
            require(original is None and backup is None
                    and target.get("mode") == 0o600,
                    "an originally absent canonical artifact has a fabricated backup")
    return {
        "schema": SCHEMA + "-authenticated-promotion",
        "status": "PASS",
        "family": family,
        "activation_root": root,
        "candidate_import_root": ROOT,
        "source_build_v2": provenance,
        "canonical_targets": targets,
        "backup_entries": backups,
        "original_guard_sources": guards,
    }


def restore(arguments: dict[str, Any]) -> dict[str, Any]:
    family = checked_family(arguments["family"])
    root = checked_private_root(arguments["activation_root"], family, build=False)
    require(sys.executable == PINNED_PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314"
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "restore only with the isolated pinned stable CPython 3.14.6")
    for relative, expected in (
        ("GOAL.md", GOAL_SHA256),
        (PHASE1_RELATIVE, PHASE1_SHA256),
        (SOURCE_RELATIVE, arguments["activation_source_sha256"]),
        (PROTOCOL_RELATIVE, arguments["activation_protocol_sha256"]),
        (BUILD_SOURCE_RELATIVE, BUILD_SOURCE_SHA256),
        (BUILD_PROTOCOL_RELATIVE, BUILD_PROTOCOL_SHA256),
    ):
        read_owned(ROOT, relative, expected, maximum=MAX_SOURCE_BYTES)
    report_bytes, _ = read_owned(
        root, REPORT_NAME, arguments["activation_report_sha256"],
        maximum=MAX_REPORT_BYTES, private=True,
    )
    receipt_bytes, _ = read_owned(
        root, RECEIPT_NAME, arguments["activation_receipt_sha256"],
        maximum=MAX_REPORT_BYTES, private=True,
    )
    report = decode_document(report_bytes, "canonical activation report")
    receipt = decode_document(receipt_bytes, "canonical activation receipt")
    journal_owner = report.get("recovery_journal")
    require(type(journal_owner) is dict,
            "a complete actual canonical recovery journal is mandatory")
    journal_bytes, actual_journal = read_owned(
        root, JOURNAL_NAME, journal_owner.get("sha256"),
        maximum=MAX_REPORT_BYTES,
        exact_size=journal_owner.get("size_bytes"), private=True,
    )
    require(same_owner(actual_journal, journal_owner),
            "the exact same-inode recovery journal was substituted")
    journal = decode_document(journal_bytes, "canonical recovery journal")
    validated = validate_activation_documents(
        report, receipt, journal, arguments=arguments,
    )
    for relative, digest in report["owned_source_sha256"].items():
        _, actual = read_owned(ROOT, relative, digest, maximum=MAX_SOURCE_BYTES)
        require(same_owner(actual, report["source_owners"][relative]),
                "an independently built family source changed before restoration")
    for relative, digest in ORIGINAL_GUARD_SOURCES.items():
        _, actual = read_owned(ROOT, relative, digest, maximum=MAX_SOURCE_BYTES)
        require(same_owner(actual, report["original_guard_sources"][relative]),
                "an immutable original V5 guard changed before restoration")
    intents = authenticate_promotion_intents(
        root, journal, actual_journal["sha256"],
    )
    for role, target in report["canonical_targets"].items():
        current = current_canonical(target["relative"])
        require(current is not None and same_owner(current[1], target),
                "refuse to restore an altered or user-replaced promoted native inode")
        require(role in intents and same_owner(intents[role]["target"], target),
                "the promoted canonical inode lacks its durable pre-replace intent")
    restored = restore_journal_targets(
        root, journal, promotion_intents=intents,
    )
    restored_record = {
        "schema": SCHEMA + "-restoration-receipt",
        "status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family,
        "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_report_sha256": arguments["activation_report_sha256"],
        "activation_receipt_sha256": arguments["activation_receipt_sha256"],
        "recovery_journal_sha256": actual_journal["sha256"],
        "source_build_v2": validated["source_build_v2"],
        "restored_targets": restored,
        **zero_effects(),
    }
    record = write_fresh(root, "restoration-receipt.json", canonical(restored_record))
    synchronized = synchronize_directory(root)
    return {
        "schema": SCHEMA + "-restoration-result",
        "status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family,
        "activation_root": root,
        "candidate_import_root": ROOT,
        "restoration_receipt_relative": "restoration-receipt.json",
        "restoration_receipt_sha256": record["sha256"],
        "receipt_directory_fsync": synchronized,
        **zero_effects(),
    }


def recover(arguments: dict[str, Any]) -> dict[str, Any]:
    """Recover a killed promotion using its pinned, pre-replace journal."""
    family = checked_family(arguments["family"])
    root = checked_private_root(arguments["activation_root"], family, build=False)
    require(sys.executable == PINNED_PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314"
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "recover only with the isolated pinned stable CPython 3.14.6")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "never import or load a candidate during crash recovery")
    for relative, expected in (
        ("GOAL.md", GOAL_SHA256),
        (PHASE1_RELATIVE, PHASE1_SHA256),
        (SOURCE_RELATIVE, arguments["activation_source_sha256"]),
        (PROTOCOL_RELATIVE, arguments["activation_protocol_sha256"]),
        (BUILD_SOURCE_RELATIVE, BUILD_SOURCE_SHA256),
        (BUILD_PROTOCOL_RELATIVE, BUILD_PROTOCOL_SHA256),
    ):
        read_owned(ROOT, relative, expected, maximum=MAX_SOURCE_BYTES)
    original_guards: dict[str, dict[str, Any]] = {}
    for relative, expected in sorted(ORIGINAL_GUARD_SOURCES.items()):
        _, original_guards[relative] = read_owned(
            ROOT, relative, expected, maximum=MAX_SOURCE_BYTES,
        )
    journal_bytes, journal_owner = read_owned(
        root, JOURNAL_NAME, arguments["recovery_journal_sha256"],
        maximum=MAX_REPORT_BYTES, private=True,
    )
    require(journal_owner.get("mode") == 0o600,
            "the exact reportless recovery journal must remain owner-only")
    journal = decode_document(journal_bytes, "reportless recovery journal")
    checked = validate_recovery_journal(journal, arguments=arguments)
    provenance = checked["source_build_v2"]
    pins = checked["owned_source_sha256"]
    source_evidence: dict[str, dict[str, Any]] = {}
    for relative, digest in pins.items():
        _, source_evidence[relative] = read_owned(
            ROOT, relative, digest, maximum=MAX_SOURCE_BYTES,
        )
    archive, _ = read_owned(
        ROOT, provenance["archive_relative"], provenance["archive_sha256"],
        maximum=MAX_ARCHIVE_BYTES,
    )
    receipt_bytes, _ = read_owned(
        ROOT, provenance["receipt_relative"], provenance["receipt_sha256"],
        maximum=MAX_SOURCE_BYTES,
    )
    report = decode_document(bounded_gzip(archive), "genuine recovery V2 report")
    receipt = decode_document(receipt_bytes, "genuine recovery V2 receipt")
    entries = checked["backup_entries"]
    engine_role = "extension" if family == "c" else "engine"
    bridge_role = "extension" if family == "c" else "bridge"
    build_arguments: dict[str, Any] = {
        "family": family,
        "build_label": provenance["label"],
        "build_root": provenance["build_root"],
        "build_source_sha256": provenance["source_sha256"],
        "build_protocol_sha256": provenance["protocol_sha256"],
        "build_report_sha256": provenance["archive_sha256"],
        "build_receipt_sha256": provenance["receipt_sha256"],
        "native_engine_sha256": entries[engine_role]["promoted_sha256"],
        "native_bridge_sha256": entries[bridge_role]["promoted_sha256"],
        "native_engine_bytes": entries[engine_role]["promoted_size_bytes"],
        "native_bridge_bytes": entries[bridge_role]["promoted_size_bytes"],
    }
    outputs = validate_build_report(report, receipt, archive,
                                    build_arguments, pins)
    for relative, observed in source_evidence.items():
        recorded = report["owned_source_after"][relative]
        require(observed["sha256"] == recorded["sha256"]
                and observed["size_bytes"] == recorded["size_bytes"]
                and observed["device"] == recorded["device"]
                and observed["inode"] == recorded["inode"],
                "a corrected V2 candidate source changed before crash recovery")
    for role, output in outputs.items():
        entry = entries[role]
        require(entry["promoted_sha256"] == output["sha256"]
                and entry["promoted_size_bytes"] == output["size_bytes"],
                "a recovery journal targets a non-V2 native artifact")
        observed_phases: list[dict[str, Any]] = []
        first: bytes | None = None
        for phase in ("reference-a", "reference-b"):
            relative = phase + "/native/" + output["file_name"]
            data, phase_owner = read_owned(
                provenance["build_root"], relative, output["sha256"],
                maximum=MAX_BINARY_BYTES,
                exact_size=output["size_bytes"], private=True,
            )
            if first is None:
                first = data
            else:
                require(data == first,
                        "both authentic crash-recovery source builds must match")
            observed_phases.append(phase_owner)
        require(len(observed_phases) == 2
                and (observed_phases[0]["device"], observed_phases[0]["inode"])
                != (observed_phases[1]["device"], observed_phases[1]["inode"]),
                "crash recovery requires two actual distinct source-build inodes")
    intents = authenticate_promotion_intents(
        root, journal, journal_owner["sha256"],
    )
    restored = restore_journal_targets(
        root, journal, promotion_intents=intents,
    )
    recovery_record = {
        "schema": SCHEMA + "-restoration-receipt",
        "status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "recovery_mode": "reportless-pinned-prepromotion-journal",
        "family": family,
        "label": provenance["label"],
        "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_source_sha256": arguments["activation_source_sha256"],
        "activation_protocol_sha256": arguments["activation_protocol_sha256"],
        "recovery_journal_sha256": journal_owner["sha256"],
        "source_build_v2": provenance,
        "owned_source_sha256": pins,
        "source_owners": source_evidence,
        "original_guard_sources": original_guards,
        "restored_targets": restored,
        **zero_effects(),
    }
    owner = write_fresh(root, "restoration-receipt.json", canonical(recovery_record))
    synchronized = synchronize_directory(root)
    return {
        "schema": SCHEMA + "-reportless-recovery-result",
        "status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "recovery_mode": "reportless-pinned-prepromotion-journal",
        "family": family,
        "activation_root": root,
        "candidate_import_root": ROOT,
        "recovery_journal_sha256": journal_owner["sha256"],
        "restoration_receipt_relative": "restoration-receipt.json",
        "restoration_receipt_sha256": owner["sha256"],
        "receipt_directory_fsync": synchronized,
        **zero_effects(),
    }


class BlockedEnvironment:
    """Reject every synthetic attempt to inspect or alter the environment."""

    def __init__(self, deny: Any) -> None:
        self.deny = deny

    def __getitem__(self, key: Any) -> Any:
        return self.deny(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        self.deny(key, value)

    def get(self, *args: Any, **kwargs: Any) -> Any:
        return self.deny(*args, **kwargs)

    def __contains__(self, key: Any) -> bool:
        self.deny(key)
        return False

    def __iter__(self) -> Any:
        return self.deny()

    def keys(self) -> Any:
        return self.deny()


class SyntheticSandbox:
    """Make all source-only self-test effects demonstrably impossible."""

    def __init__(self) -> None:
        self.previous: list[tuple[Any, str, Any]] = []
        self.blocked: dict[str, int] = {
            "filesystem": 0, "process": 0, "thread": 0,
            "clock": 0, "network": 0, "environment": 0, "import": 0,
        }

    def deny(self, category: str) -> Any:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            self.blocked[category] += 1
            raise SourceOnlyEffect("synthetic activation may not access " + category)
        return blocked

    def install(self, owner: Any, name: str, value: Any) -> None:
        if hasattr(owner, name):
            self.previous.append((owner, name, getattr(owner, name)))
            setattr(owner, name, value)

    def __enter__(self) -> SyntheticSandbox:
        filesystem = self.deny("filesystem")
        process = self.deny("process")
        thread = self.deny("thread")
        clock = self.deny("clock")
        network = self.deny("network")
        environment = self.deny("environment")
        importer = self.deny("import")
        self.install(builtins, "open", filesystem)
        self.install(io, "open", filesystem)
        for name in (
            "open", "read", "write", "stat", "lstat", "scandir", "listdir",
            "walk", "mkdir", "makedirs", "rename", "replace", "remove",
            "unlink", "fsync", "fdatasync", "chmod", "fchmod", "fdopen",
            "system", "popen",
        ):
            self.install(os, name, process if name in {"system", "popen"}
                         else filesystem)
        self.install(tempfile, "mkdtemp", filesystem)
        self.install(tempfile, "mkstemp", filesystem)
        self.install(tempfile, "NamedTemporaryFile", filesystem)
        self.install(tempfile, "TemporaryDirectory", filesystem)
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
    return sha256(("verified-native-activation-v1:" + label).encode("ascii"))


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
        native = []
    elif role == "engine":
        exports = sorted(RUST_ENGINE_EXPORTS if family == "rust"
                         else ZIG_ENGINE_EXPORTS)
        native = []
    else:
        exports = ["PyInit__" + family + "_bridge"]
        native = ["rebar_compile" if family == "rust" else "rebar_zig_compile"]
    undefined = ["__stack_chk_fail@GLIBC_2.4", *native]
    count = 1 + len(exports) + len(undefined)
    rows = [
        "Symbol table '.dynsym' contains " + str(count) + " entries:",
        "   Num: Value Size Type Bind Vis Ndx Name",
        "   0: 0000000000000000 0 NOTYPE LOCAL DEFAULT UND",
    ]
    index = 1
    for name in exports:
        rows.append("   " + str(index)
                    + ": 0000000000000010 1 FUNC GLOBAL DEFAULT 1 " + name)
        index += 1
    for name in undefined:
        extra = " (2)" if "@" in name else ""
        rows.append("   " + str(index)
                    + ": 0000000000000000 0 FUNC GLOBAL DEFAULT UND "
                    + name + extra)
        index += 1
    return ("\n".join(rows) + "\n").encode("ascii")


def synthetic_process(name: str, family: str, phase: str,
                      pid: int) -> dict[str, Any]:
    executables = {
        "gcc_version": PINNED_GCC, "readelf_version": PINNED_READELF,
        "rustc_version": PINNED_RUSTC, "cargo_version": PINNED_CARGO,
        "zig_version": PINNED_ZIG, "build_c_extension": PINNED_GCC,
        "build_rust_engine": PINNED_CARGO, "build_rust_bridge": PINNED_GCC,
        "build_zig_engine": PINNED_ZIG, "build_zig_bridge": PINNED_GCC,
    }
    if name.endswith("_dynamic") or name.endswith("_symbols"):
        role = name.rsplit("_", 1)[0]
        option = "--dynamic" if name.endswith("_dynamic") else "--dyn-syms"
        path = (SANITIZED_BUILD_ROOT + "/" + phase + "/native/"
                + FAMILIES[family]["binaries"][role])
        argv = [PINNED_READELF, option, "--wide", path]
        stdout = (synthetic_dynamic(family, role)
                  if name.endswith("_dynamic")
                  else synthetic_symbols(family, role))
    else:
        argv = [executables[name], "--synthetic-frozen-process"]
        stdout = b"genuine-synthetic-process\n"
    stderr = b""
    environment = {
        "PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C",
        "TZ": "UTC", "SOURCE_DATE_EPOCH": "1",
    }
    if family == "rust":
        environment.update({
            "CARGO_NET_OFFLINE": "true", "CARGO_INCREMENTAL": "0",
            "RUSTC": PINNED_RUSTC,
        })
    return {
        "name": name, "argv": argv, "environment": environment,
        "shell": False, "pid": pid, "exit_status": 0,
        "stdout_base64": base64.b64encode(stdout).decode("ascii"),
        "stdout_sha256": sha256(stdout), "stdout_bytes": len(stdout),
        "stderr_base64": base64.b64encode(stderr).decode("ascii"),
        "stderr_sha256": sha256(stderr), "stderr_bytes": len(stderr),
    }


def synthetic_fixture(family: str) -> tuple[dict[str, Any], dict[str, Any],
                                            bytes, dict[str, Any], dict[str, str]]:
    checked_family(family)
    label = "synthetic-v2"
    pins = {
        name: synthetic_digest(family + ":source:" + name)
        for name in sorted(FAMILIES[family]["owners"])
    }
    snapshots = {
        name: {
            "path": ROOT + "/" + name, "sha256": digest,
            "size_bytes": 123, "device": 71,
            "inode": 1000 + index,
        }
        for index, (name, digest) in enumerate(pins.items())
    }
    audits = []
    for name in pins:
        if name.endswith((".py", ".c", ".rs", ".zig")):
            item = {"path": name, "external_regex_dependency_count": 0}
            if name.endswith(".py"):
                item["cross_family_dependency_count"] = 0
            audits.append(item)
    source_audit = {
        "source_audits": audits,
        "source_owner_count": len(pins),
        "external_regex_package_count": 0,
        "cross_family_dependency_count": 0,
        "cargo_dependency_closure": (
            {"package": "rebar-rust-continuation", "package_count": 1,
             "external_package_count": 0, "registry_count": 0,
             "build_script_count": 0, "locked": True, "offline": True}
            if family == "rust" else None
        ),
    }
    phase1 = {
        "status": "PASS", "suite_count": 13, "case_execution_count": 31_237,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "final_holdout_authorized": False,
    }
    history = {
        "status": "AUTHENTIC HISTORICAL BUILD; V1 SYMBOL AUDIT FALSIFIED",
        "real_versioned_symbol_count_per_phase": 9,
        "observed_v1_parser_false_symbols": ["(2)", "(3)", "(4)", "(5)"],
    }
    history["observed_v1_parser_false_symbols"].append("(6)")
    support_specs = {
        "immutable_objective": (ROOT + "/GOAL.md", GOAL_SHA256),
        "complete_correctness_manifest": (
            ROOT + "/" + PHASE1_RELATIVE, PHASE1_SHA256,
        ),
        "pinned_cpython_executable": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
        "native_build_recorder": (
            ROOT + "/" + BUILD_SOURCE_RELATIVE, BUILD_SOURCE_SHA256,
        ),
        "native_build_protocol": (
            ROOT + "/" + BUILD_PROTOCOL_RELATIVE, BUILD_PROTOCOL_SHA256,
        ),
    }
    support = {
        name: {
            "path": path, "sha256": digest, "size_bytes": 123,
            "device": 71, "inode": 8000 + index,
        }
        for index, (name, (path, digest)) in enumerate(support_specs.items())
    }
    names = expected_processes(family)
    versions = 2 + (2 if family == "rust" else 1 if family == "zig" else 0)
    step = 3 if family == "c" else 6
    processes = []
    for index, name in enumerate(names):
        phase = "reference-a" if index < versions + step else "reference-b"
        processes.append(synthetic_process(name, family, phase, 20_000 + index))
    phases = []
    reproduced: dict[str, dict[str, Any]] = {}
    for phase in ("reference-a", "reference-b"):
        prefix = SANITIZED_BUILD_ROOT + "/" + phase
        copies = {
            name: {
                "path": prefix + "/source/" + name,
                "sha256": digest, "bytes": 123,
                "exclusive_creation": True,
                "same_inode_readback_verified": True,
            }
            for name, digest in pins.items()
        }
        outputs: dict[str, dict[str, Any]] = {}
        for role, filename in FAMILIES[family]["binaries"].items():
            elf = validate_elf(
                family, role, parse_dynamic(synthetic_dynamic(family, role)),
                parse_symbols(synthetic_symbols(family, role)),
            )
            digest = synthetic_digest(family + ":native:" + role)
            output = {
                "family": family, "role": role, "file_name": filename,
                "path": prefix + "/native/" + filename,
                "sha256": digest, "size_bytes": 9876,
                "elf": elf, "prebuilt_binary_read": False,
                "candidate_imported": False,
            }
            outputs[role] = output
            reproduced[role] = {
                "file_name": filename, "sha256": digest,
                "size_bytes": 9876,
                "reproduced_in_two_fresh_directories": True,
                "elf": elf,
            }
        phases.append({
            "name": phase,
            "fresh_source_directory": prefix + "/source",
            "fresh_native_directory": prefix + "/native",
            "copied_source_owners": copies,
            "native_outputs": outputs,
            "candidate_processes_started": 0,
            "candidate_imports": 0,
            "native_libraries_loaded": 0,
            "timing_trials_run": 0,
            "hidden_cases_read": 0,
        })
    report = {
        "schema": BUILD_SCHEMA, "status": "PASS", "family": family,
        "label": label, "source_sha256": BUILD_SOURCE_SHA256,
        "protocol_sha256": BUILD_PROTOCOL_SHA256,
        "phase1": phase1, "historical_v1_c": history,
        "frozen_support_inputs": support,
        "frozen_support_inputs_after": copy.deepcopy(support),
        "owned_source_sha256": pins,
        "owned_source_before": snapshots,
        "owned_source_after": copy.deepcopy(snapshots),
        "source_independence_audit": source_audit,
        "fresh_private_root": SANITIZED_BUILD_ROOT,
        "build_phases": phases, "processes": processes,
        "reproducibility": {
            "independent_fresh_phase_count": 2,
            "byte_identical": True, "native_outputs": reproduced,
            "prebuilt_binary_count": 0, "native_libraries_loaded": 0,
        },
        "reference_processes_started": 0,
        "network_requests": 0,
        "error": None,
        **zero_effects(),
    }
    plain = canonical(report)
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    archive_relative = (EVIDENCE_RELATIVE + "/native-source-build-v2-"
                        + family + "-" + label + ".json.gz")
    publication = {
        "path": ROOT + "/" + archive_relative,
        "sha256": sha256(archive), "bytes": len(archive),
        "exclusive_creation": True,
        "same_inode_readback_verified": True,
        "file_fsync_completed": True,
    }
    receipt = {
        "schema": BUILD_RECEIPT_SCHEMA, "status": "PASS",
        "build_status": "PASS", "family": family, "label": label,
        "source_sha256": BUILD_SOURCE_SHA256,
        "protocol_sha256": BUILD_PROTOCOL_SHA256,
        "phase1_manifest_sha256": PHASE1_SHA256,
        "archive_relative": archive_relative,
        "archive_sha256": sha256(archive), "archive_bytes": len(archive),
        "uncompressed_sha256": sha256(plain),
        "uncompressed_bytes": len(plain),
        "archive_publication": publication,
        "archive_directory_fsync": {
            "completed": True, "device": 71, "inode": 888,
        },
        "owned_source_sha256": pins,
        "receipt_self_publication": "NOT CLAIMED",
        **{
            key: value for key, value in zero_effects().items()
            if key not in {"reference_processes_started", "network_requests"}
        },
    }
    roles = FAMILIES[family]["binaries"]
    engine_role = "extension" if family == "c" else "engine"
    bridge_role = "extension" if family == "c" else "bridge"
    arguments = {
        "mode": "activate", "family": family,
        "build_label": label,
        "build_root": "/tmp/" + BUILD_PREFIX + family + "-synthetic",
        "activation_source_sha256": synthetic_digest("activation-source"),
        "activation_protocol_sha256": synthetic_digest("activation-protocol"),
        "build_source_sha256": BUILD_SOURCE_SHA256,
        "build_protocol_sha256": BUILD_PROTOCOL_SHA256,
        "build_report_sha256": sha256(archive),
        "build_receipt_sha256": sha256(canonical(receipt)),
        "native_engine_sha256": reproduced[engine_role]["sha256"],
        "native_bridge_sha256": reproduced[bridge_role]["sha256"],
        "native_engine_bytes": reproduced[engine_role]["size_bytes"],
        "native_bridge_bytes": reproduced[bridge_role]["size_bytes"],
        "owned_source_sha256": [name + "=" + digest
                                 for name, digest in pins.items()],
    }
    require(bool(roles), "every synthetic family must own actual native roles")
    return report, receipt, archive, arguments, pins


def reseal_synthetic_v2(
    report: dict[str, Any], receipt: dict[str, Any], arguments: dict[str, Any],
) -> tuple[dict[str, Any], bytes, dict[str, Any]]:
    plain = canonical(report)
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    adjusted = copy.deepcopy(receipt)
    adjusted["archive_sha256"] = sha256(archive)
    adjusted["archive_bytes"] = len(archive)
    adjusted["uncompressed_sha256"] = sha256(plain)
    adjusted["uncompressed_bytes"] = len(plain)
    publication = adjusted.get("archive_publication")
    if type(publication) is dict:
        publication["sha256"] = sha256(archive)
        publication["bytes"] = len(archive)
    sealed = dict(arguments)
    sealed["build_report_sha256"] = sha256(archive)
    sealed["build_receipt_sha256"] = sha256(canonical(adjusted))
    return adjusted, archive, sealed


def synthetic_activation_fixture(
    family: str, *, absent_role: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    build_report, build_receipt, archive, build_arguments, pins = synthetic_fixture(family)
    outputs = validate_build_report(
        build_report, build_receipt, archive, build_arguments, pins,
    )
    root = "/tmp/" + PRIVATE_PREFIX + family + "-synthetic"
    label = build_arguments["build_label"]
    provenance = {
        "schema": BUILD_SCHEMA, "family": family, "label": label,
        "source_sha256": BUILD_SOURCE_SHA256,
        "protocol_sha256": BUILD_PROTOCOL_SHA256,
        "archive_relative": build_receipt["archive_relative"],
        "archive_sha256": sha256(archive),
        "receipt_relative": (
            EVIDENCE_RELATIVE + "/native-source-build-v2-" + family
            + "-" + label + "-publication-receipt.json"
        ),
        "receipt_sha256": sha256(canonical(build_receipt)),
        "build_root": build_arguments["build_root"],
        "independent_fresh_phase_count": 2,
        "actual_versioned_symbol_streams_verified": True,
    }

    def owner(relative: str, digest: str, *, base: str,
              size: int, inode: int, exclusive: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {
            "relative": relative, "path": base + "/" + relative,
            "sha256": digest, "size_bytes": size,
            "device": 71 if base == ROOT else 83,
            "inode": inode,
            "mode": 0o600 if exclusive else 0o644,
        }
        if exclusive:
            result.update({
                "exclusive_creation": True,
                "same_inode_readback_verified": True,
                "file_fsync_completed": True,
                "write_calls": 1,
            })
        return result

    sources = {
        relative: owner(relative, digest, base=ROOT,
                        size=123, inode=1000 + index)
        for index, (relative, digest) in enumerate(pins.items())
    }
    guards = {
        relative: owner(relative, digest, base=ROOT,
                        size=456, inode=4000 + index)
        for index, (relative, digest) in enumerate(
            sorted(ORIGINAL_GUARD_SOURCES.items())
        )
    }
    frozen_specs = (
        ("GOAL.md", GOAL_SHA256),
        (PHASE1_RELATIVE, PHASE1_SHA256),
        (SOURCE_RELATIVE, build_arguments["activation_source_sha256"]),
        (PROTOCOL_RELATIVE, build_arguments["activation_protocol_sha256"]),
        (BUILD_SOURCE_RELATIVE, BUILD_SOURCE_SHA256),
        (BUILD_PROTOCOL_RELATIVE, BUILD_PROTOCOL_SHA256),
    )
    frozen = {
        relative: owner(relative, digest, base=ROOT,
                        size=321, inode=6000 + index)
        for index, (relative, digest) in enumerate(frozen_specs)
    }
    backup_entries: dict[str, dict[str, Any]] = {}
    targets: dict[str, dict[str, Any]] = {}
    for index, (role, filename) in enumerate(FAMILIES[family]["binaries"].items()):
        relative = "candidates/" + filename
        observed = outputs[role]
        present = role != absent_role
        phases = [
            owner(phase + "/native/" + filename, observed["sha256"],
                  base=build_arguments["build_root"],
                  size=observed["size_bytes"], inode=7000 + 2 * index + number)
            for number, phase in enumerate(("reference-a", "reference-b"))
        ]
        target_owner = owner(relative, observed["sha256"], base=ROOT,
                             size=observed["size_bytes"], inode=9000 + index)
        target_owner["mode"] = 0o644 if present else 0o600
        targets[role] = {
            **target_owner,
            "atomic_replace_completed": True,
            "adjacent_exclusive_stage_verified": True,
            "candidate_directory_fsync_completed": True,
            "role": role,
            "elf": observed["elf"],
            "source_build_phases": phases,
        }
        previous_digest = synthetic_digest(family + ":previous:" + role)
        previous = (owner(relative, previous_digest, base=ROOT,
                          size=6543, inode=3000 + index)
                    if present else None)
        backup_relative = "backups/" + relative
        backup = (
            owner(backup_relative, previous_digest, base=root,
                  size=6543, inode=3500 + index, exclusive=True)
            if present else None
        )
        backup_entries[role] = {
            "role": role,
            "target_relative": relative,
            "target_path": ROOT + "/" + relative,
            "originally_present": present,
            "original_owner": previous,
            "backup": backup,
            "promoted_sha256": observed["sha256"],
            "promoted_size_bytes": observed["size_bytes"],
        }
    journal = {
        "schema": JOURNAL_SCHEMA,
        "status": "PREPARED",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family,
        "label": label,
        "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_source_sha256": build_arguments["activation_source_sha256"],
        "activation_protocol_sha256": build_arguments["activation_protocol_sha256"],
        "source_build_v2": provenance,
        "owned_source_sha256": pins,
        "backup_entries": backup_entries,
        **zero_effects(),
    }
    journal_bytes = canonical(journal)
    journal_owner = owner(JOURNAL_NAME, sha256(journal_bytes), base=root,
                          size=len(journal_bytes), inode=9991, exclusive=True)
    journal_owner["directory_fsync_completed"] = True
    for index, (role, target) in enumerate(targets.items()):
        intended_target = {
            key: target[key]
            for key in ("relative", "path", "sha256", "size_bytes",
                        "device", "inode", "mode")
        }
        intention = {
            "schema": INTENT_SCHEMA,
            "status": "PREPARED",
            "promotion_mode": "recoverable-canonical-promotion",
            "family": family,
            "activation_root": root,
            "candidate_import_root": ROOT,
            "recovery_journal_sha256": journal_owner["sha256"],
            "role": role,
            "target": intended_target,
            **zero_effects(),
        }
        intent_bytes = canonical(intention)
        intent_owner = owner(
            "promotion-intent-" + role + ".json",
            sha256(intent_bytes), base=root,
            size=len(intent_bytes), inode=9500 + index, exclusive=True,
        )
        intent_owner["directory_fsync_completed"] = True
        target["promotion_intent"] = intent_owner
    report = {
        "schema": SCHEMA,
        "status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family,
        "label": label,
        "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_source_sha256": build_arguments["activation_source_sha256"],
        "activation_protocol_sha256": build_arguments["activation_protocol_sha256"],
        "source_build_v2": provenance,
        "owned_source_sha256": pins,
        "source_owners": sources,
        "adapter": {
            **sources[FAMILIES[family]["adapter"]],
            "module": FAMILIES[family]["module"],
        },
        "canonical_targets": targets,
        "backup_entries": backup_entries,
        "recovery_journal": journal_owner,
        "original_guard_sources": guards,
        "frozen_support_inputs": frozen,
        **zero_effects(),
    }
    report_bytes = canonical(report)
    report_owner = owner(REPORT_NAME, sha256(report_bytes), base=root,
                         size=len(report_bytes), inode=9992, exclusive=True)
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "status": "PASS",
        "activation_status": "PASS",
        "promotion_mode": "recoverable-canonical-promotion",
        "family": family,
        "label": label,
        "activation_root": root,
        "candidate_import_root": ROOT,
        "activation_source_sha256": build_arguments["activation_source_sha256"],
        "activation_protocol_sha256": build_arguments["activation_protocol_sha256"],
        "source_build_v2": provenance,
        "owned_source_sha256": pins,
        "report_relative": REPORT_NAME,
        "report_sha256": report_owner["sha256"],
        "report_bytes": report_owner["size_bytes"],
        "report_publication": report_owner,
        "report_directory_fsync": {
            "completed": True, "device": 83, "inode": 101,
        },
        "source_owners": sources,
        "canonical_targets": targets,
        "backup_entries": backup_entries,
        "recovery_journal": journal_owner,
        "original_guard_sources": guards,
        "receipt_self_publication": "NOT CLAIMED",
        **zero_effects(),
    }
    arguments = {
        "mode": "restore",
        "family": family,
        "activation_root": root,
        "activation_source_sha256": build_arguments["activation_source_sha256"],
        "activation_protocol_sha256": build_arguments["activation_protocol_sha256"],
        "activation_report_sha256": sha256(report_bytes),
        "activation_receipt_sha256": sha256(canonical(receipt)),
    }
    return report, receipt, journal, arguments


def self_test() -> dict[str, Any]:
    positives = 0
    hostiles = 0

    def positive(value: Any, label: str) -> None:
        nonlocal positives
        require(bool(value), "a source-only positive control failed: " + label)
        positives += 1

    def rejected(action: Any, label: str) -> None:
        nonlocal hostiles
        try:
            action()
        except (ActivationError, TypeError, ValueError, OverflowError,
                UnicodeError, RecursionError, OSError, zlib.error):
            hostiles += 1
            return
        raise ActivationError("a hostile source-only control escaped: " + label)

    with SyntheticSandbox() as sandbox:
        positive(parse_arguments(["--self-test"]) == {"mode": "self-test"},
                 "exact self-test argument")
        for family in ("c", "rust", "zig"):
            report, receipt, archive, arguments, pins = synthetic_fixture(family)
            positive(decode_document(canonical(report), family) == report,
                     family + " canonical report")
            positive(decode_document(canonical(receipt), family) == receipt,
                     family + " canonical receipt")
            positive(bounded_gzip(archive) == canonical(report),
                     family + " deterministic bounded archive")
            positive(parse_owner_pins(family, arguments["owned_source_sha256"])
                     == pins, family + " complete source owners")
            outputs = validate_build_report(report, receipt, archive, arguments, pins)
            positive(set(outputs) == set(FAMILIES[family]["binaries"]),
                     family + " real two-phase roles")
            positive(len(validate_processes(family, report["processes"]))
                     == len(expected_processes(family)),
                     family + " complete real process order")
            activation_report, activation_receipt, journal, restore_arguments = (
                synthetic_activation_fixture(family)
            )
            approved = validate_activation_documents(
                activation_report, activation_receipt, journal,
                arguments=restore_arguments,
            )
            positive(approved["status"] == "PASS"
                     and approved["candidate_import_root"] == ROOT
                     and set(approved["canonical_targets"])
                     == set(FAMILIES[family]["binaries"]),
                     family + " complete recoverable canonical promotion")
            recovery_arguments = {
                "mode": "recover",
                "family": family,
                "activation_root": restore_arguments["activation_root"],
                "activation_source_sha256":
                    restore_arguments["activation_source_sha256"],
                "activation_protocol_sha256":
                    restore_arguments["activation_protocol_sha256"],
                "recovery_journal_sha256": sha256(canonical(journal)),
            }
            recovered = validate_recovery_journal(
                journal, arguments=recovery_arguments,
            )
            positive(recovered["status"] == "PASS"
                     and recovered["candidate_import_root"] == ROOT
                     and set(recovered["backup_entries"])
                     == set(FAMILIES[family]["binaries"]),
                     family + " genuine reportless crash-recovery journal")
            recovery_command = ["--recover"]
            for option, key in (
                ("--family", "family"),
                ("--activation-root", "activation_root"),
                ("--activation-source-sha256", "activation_source_sha256"),
                ("--activation-protocol-sha256", "activation_protocol_sha256"),
                ("--recovery-journal-sha256", "recovery_journal_sha256"),
            ):
                recovery_command.extend((option, recovery_arguments[key]))
            positive(parse_arguments(recovery_command) == recovery_arguments,
                     family + " exact independently pinned reportless recovery")
            positive(parse_arguments(["--restore", *recovery_command[1:]])
                     == recovery_arguments,
                     family + " equivalent pinned journal-only restore")
            for role in FAMILIES[family]["binaries"]:
                entry = journal["backup_entries"][role]
                target = activation_report["canonical_targets"][role]
                intended = {
                    "schema": INTENT_SCHEMA,
                    "status": "PREPARED",
                    "promotion_mode": "recoverable-canonical-promotion",
                    "family": family,
                    "activation_root": restore_arguments["activation_root"],
                    "candidate_import_root": ROOT,
                    "recovery_journal_sha256":
                        recovery_arguments["recovery_journal_sha256"],
                    "role": role,
                    "target": {
                        key: target[key]
                        for key in ("relative", "path", "sha256", "size_bytes",
                                    "device", "inode", "mode")
                    },
                    **zero_effects(),
                }
                positive(validate_promotion_intent(
                    intended, family=family,
                    root=restore_arguments["activation_root"], role=role,
                    journal_sha256=recovery_arguments["recovery_journal_sha256"],
                    current=target,
                )["inode"] == target["inode"],
                    family + " durable pre-replace staged inode " + role)
                foreign_inode = copy.deepcopy(target)
                foreign_inode["inode"] += 1
                rejected(
                    lambda intended=intended, foreign_inode=foreign_inode,
                    role=role: validate_promotion_intent(
                        intended, family=family,
                        root=restore_arguments["activation_root"], role=role,
                        journal_sha256=
                            recovery_arguments["recovery_journal_sha256"],
                        current=foreign_inode,
                    ), family + " same-byte substituted promoted inode " + role,
                )
                for field in ("device", "mode"):
                    foreign_identity = copy.deepcopy(target)
                    foreign_identity[field] = (
                        foreign_identity[field] + 1
                        if field == "device" else 0o600
                        if foreign_identity[field] != 0o600 else 0o644
                    )
                    rejected(
                        lambda intended=intended,
                        foreign_identity=foreign_identity,
                        role=role: validate_promotion_intent(
                            intended, family=family,
                            root=restore_arguments["activation_root"],
                            role=role,
                            journal_sha256=
                                recovery_arguments["recovery_journal_sha256"],
                            current=foreign_identity,
                        ), family + " substituted promoted " + field + " " + role,
                    )
                positive(classify_recovery_state(
                    entry, target,
                ) == "source-verified-promoted",
                    family + " actual partially promoted " + role)
                positive(classify_recovery_state(
                    entry, entry["original_owner"],
                ) == "already-original",
                    family + " safe untouched original " + role)
                original_inode = copy.deepcopy(entry["original_owner"])
                original_inode["inode"] += 1
                rejected(
                    lambda entry=entry, original_inode=original_inode:
                    classify_recovery_state(entry, original_inode),
                    family + " preserved same-content original foreign inode " + role,
                )
                original_mode = copy.deepcopy(entry["original_owner"])
                original_mode["mode"] = (
                    0o600 if original_mode["mode"] != 0o600 else 0o644
                )
                rejected(
                    lambda entry=entry, original_mode=original_mode:
                    classify_recovery_state(entry, original_mode),
                    family + " preserved same-content original foreign mode " + role,
                )
                hostile_owner = copy.deepcopy(
                    activation_report["canonical_targets"][role],
                )
                hostile_owner["sha256"] = synthetic_digest(
                    family + ":unrelated-current-owner:" + role,
                )
                rejected(lambda entry=entry, hostile_owner=hostile_owner:
                         classify_recovery_state(entry, hostile_owner),
                         family + " preserved unrelated current " + role)
            for role in FAMILIES[family]["binaries"]:
                absent_report, absent_receipt, absent_journal, absent_arguments = (
                    synthetic_activation_fixture(family, absent_role=role)
                )
                positive(validate_activation_documents(
                    absent_report, absent_receipt, absent_journal,
                    arguments=absent_arguments,
                )["status"] == "PASS",
                    family + " honestly recorded absent original " + role)
                absent_recovery = {
                    "mode": "recover",
                    "family": family,
                    "activation_root": absent_arguments["activation_root"],
                    "activation_source_sha256":
                        absent_arguments["activation_source_sha256"],
                    "activation_protocol_sha256":
                        absent_arguments["activation_protocol_sha256"],
                    "recovery_journal_sha256": sha256(canonical(absent_journal)),
                }
                positive(validate_recovery_journal(
                    absent_journal, arguments=absent_recovery,
                )["status"] == "PASS",
                    family + " reportless originally absent native " + role)
                absent_entry = absent_journal["backup_entries"][role]
                positive(classify_recovery_state(absent_entry, None)
                         == "originally-absent",
                         family + " untouched original absence " + role)
                positive(classify_recovery_state(
                    absent_entry, absent_report["canonical_targets"][role],
                ) == "source-verified-promoted",
                    family + " interrupted promotion of absent " + role)
            restore_command = ["--restore"]
            for option, key in (
                ("--family", "family"),
                ("--activation-root", "activation_root"),
                ("--activation-source-sha256", "activation_source_sha256"),
                ("--activation-protocol-sha256", "activation_protocol_sha256"),
                ("--activation-report-sha256", "activation_report_sha256"),
                ("--activation-receipt-sha256", "activation_receipt_sha256"),
            ):
                restore_command.extend((option, restore_arguments[key]))
            positive(parse_arguments(restore_command) == restore_arguments,
                     family + " complete pinned recoverable restore command")
            command = ["--activate"]
            for option, key in (
                ("--family", "family"),
                ("--build-label", "build_label"),
                ("--build-root", "build_root"),
                ("--activation-source-sha256", "activation_source_sha256"),
                ("--activation-protocol-sha256", "activation_protocol_sha256"),
                ("--build-source-sha256", "build_source_sha256"),
                ("--build-protocol-sha256", "build_protocol_sha256"),
                ("--build-report-sha256", "build_report_sha256"),
                ("--build-receipt-sha256", "build_receipt_sha256"),
                ("--native-engine-sha256", "native_engine_sha256"),
                ("--native-bridge-sha256", "native_bridge_sha256"),
                ("--native-engine-bytes", "native_engine_bytes"),
                ("--native-bridge-bytes", "native_bridge_bytes"),
            ):
                command.extend((option, str(arguments[key])))
            for entry in arguments["owned_source_sha256"]:
                command.extend(("--owned-source-sha256", entry))
            positive(parse_arguments(command) == arguments,
                     family + " complete independently pinned command")
            for key in tuple(report):
                forged = copy.deepcopy(report)
                forged.pop(key)
                rejected(lambda forged=forged: validate_build_report(
                    forged, receipt, archive, arguments, pins,
                ), family + " omitted report field " + key)
            for key in tuple(receipt):
                forged_receipt = copy.deepcopy(receipt)
                forged_receipt.pop(key)
                rejected(lambda forged_receipt=forged_receipt:
                         validate_build_report(report, forged_receipt, archive,
                                               arguments, pins),
                         family + " omitted receipt field " + key)
            shared_zero_counters = (
                "candidate_processes_started", "candidate_imports",
                "native_libraries_loaded", "hidden_cases_read",
                "benchmark_files_read", "clock_samples", "timing_trials_run",
            )
            for key in (*shared_zero_counters,
                        "reference_processes_started", "network_requests"):
                for hostile in (False, True, 0.0, 1, None):
                    forged_report = copy.deepcopy(report)
                    if hostile is None:
                        forged_report.pop(key, None)
                    else:
                        forged_report[key] = hostile
                    sealed_receipt, sealed_archive, sealed_arguments = (
                        reseal_synthetic_v2(forged_report, receipt, arguments)
                    )
                    rejected(
                        lambda forged_report=forged_report,
                        sealed_receipt=sealed_receipt,
                        sealed_archive=sealed_archive,
                        sealed_arguments=sealed_arguments:
                        validate_build_report(
                            forged_report, sealed_receipt, sealed_archive,
                            sealed_arguments, pins,
                        ), family + " re-signed false V2 report counter " + key,
                    )
            for key in shared_zero_counters:
                for hostile in (False, True, 0.0, 1, None):
                    forged_receipt = copy.deepcopy(receipt)
                    if hostile is None:
                        forged_receipt.pop(key, None)
                    else:
                        forged_receipt[key] = hostile
                    sealed_receipt, sealed_archive, sealed_arguments = (
                        reseal_synthetic_v2(report, forged_receipt, arguments)
                    )
                    rejected(
                        lambda sealed_receipt=sealed_receipt,
                        sealed_archive=sealed_archive,
                        sealed_arguments=sealed_arguments:
                        validate_build_report(
                            report, sealed_receipt, sealed_archive,
                            sealed_arguments, pins,
                        ), family + " re-signed false V2 receipt counter " + key,
                    )
            for key in ("reference_processes_started", "network_requests"):
                for hostile in (False, True, 0.0, 0, 1):
                    forged_receipt = copy.deepcopy(receipt)
                    forged_receipt[key] = hostile
                    sealed_receipt, sealed_archive, sealed_arguments = (
                        reseal_synthetic_v2(report, forged_receipt, arguments)
                    )
                    rejected(
                        lambda sealed_receipt=sealed_receipt,
                        sealed_archive=sealed_archive,
                        sealed_arguments=sealed_arguments:
                        validate_build_report(
                            report, sealed_receipt, sealed_archive,
                            sealed_arguments, pins,
                        ), family + " inserted noncanonical V2 receipt field " + key,
                    )
            for key in tuple(activation_report):
                forged_activation = copy.deepcopy(activation_report)
                forged_activation.pop(key)
                rejected(lambda forged_activation=forged_activation:
                         validate_activation_documents(
                             forged_activation, activation_receipt, journal,
                             arguments=restore_arguments,
                         ), family + " omitted canonical promotion field " + key)
            for key in tuple(activation_receipt):
                forged_activation_receipt = copy.deepcopy(activation_receipt)
                forged_activation_receipt.pop(key)
                rejected(lambda forged_activation_receipt=forged_activation_receipt:
                         validate_activation_documents(
                             activation_report, forged_activation_receipt, journal,
                             arguments=restore_arguments,
                         ), family + " omitted canonical receipt field " + key)
            for key in tuple(journal):
                forged_journal = copy.deepcopy(journal)
                forged_journal.pop(key)
                rejected(lambda forged_journal=forged_journal:
                         validate_activation_documents(
                             activation_report, activation_receipt, forged_journal,
                             arguments=restore_arguments,
                         ), family + " omitted pre-promotion recovery field " + key)
                resealed_recovery = dict(recovery_arguments)
                resealed_recovery["recovery_journal_sha256"] = sha256(
                    canonical(forged_journal),
                )
                rejected(lambda forged_journal=forged_journal,
                         resealed_recovery=resealed_recovery:
                         validate_recovery_journal(
                             forged_journal, arguments=resealed_recovery,
                         ), family + " re-signed reportless journal field " + key)
            for role in FAMILIES[family]["binaries"]:
                for key in (
                    "relative", "path", "sha256", "size_bytes", "device",
                    "inode", "atomic_replace_completed",
                    "adjacent_exclusive_stage_verified",
                    "candidate_directory_fsync_completed", "role", "elf",
                    "source_build_phases", "promotion_intent", "mode",
                ):
                    forged_activation = copy.deepcopy(activation_report)
                    forged_activation["canonical_targets"][role].pop(key)
                    rejected(lambda forged_activation=forged_activation:
                             validate_activation_documents(
                                 forged_activation, activation_receipt, journal,
                                 arguments=restore_arguments,
                             ), family + " altered canonical " + role + ":" + key)
                for key in (
                    "role", "target_relative", "target_path",
                    "originally_present", "original_owner", "backup",
                    "promoted_sha256", "promoted_size_bytes",
                ):
                    forged_activation = copy.deepcopy(activation_report)
                    forged_activation["backup_entries"][role].pop(key)
                    rejected(lambda forged_activation=forged_activation:
                             validate_activation_documents(
                                 forged_activation, activation_receipt, journal,
                                 arguments=restore_arguments,
                             ), family + " altered durable " + role + ":" + key)
            for relative in ORIGINAL_GUARD_SOURCES:
                forged_activation = copy.deepcopy(activation_report)
                forged_activation["original_guard_sources"][relative]["path"] = (
                    restore_arguments["activation_root"] + "/" + relative
                )
                rejected(lambda forged_activation=forged_activation:
                         validate_activation_documents(
                             forged_activation, activation_receipt, journal,
                             arguments=restore_arguments,
                         ), family + " rebound immutable original guard " + relative)
            for option in (
                "--family", "--activation-root",
                "--activation-source-sha256", "--activation-protocol-sha256",
                "--activation-report-sha256", "--activation-receipt-sha256",
            ):
                index = restore_command.index(option)
                missing = restore_command[:index] + restore_command[index + 2:]
                rejected(lambda missing=missing: parse_arguments(missing),
                         family + " omitted exact restore option " + option)
                repeated = restore_command + restore_command[index:index + 2]
                rejected(lambda repeated=repeated: parse_arguments(repeated),
                         family + " repeated exact restore option " + option)
            for option in (
                "--family", "--activation-root",
                "--activation-source-sha256", "--activation-protocol-sha256",
                "--recovery-journal-sha256",
            ):
                index = recovery_command.index(option)
                missing = recovery_command[:index] + recovery_command[index + 2:]
                rejected(lambda missing=missing: parse_arguments(missing),
                         family + " omitted reportless recovery option " + option)
                repeated = recovery_command + recovery_command[index:index + 2]
                rejected(lambda repeated=repeated: parse_arguments(repeated),
                         family + " repeated reportless recovery option " + option)
            for number in range(len(report["processes"])):
                forged = copy.deepcopy(report)
                forged["processes"][number]["stdout_sha256"] = synthetic_digest(
                    family + ":forged-process:" + str(number)
                )
                rejected(lambda forged=forged: validate_build_report(
                    forged, receipt, archive, arguments, pins,
                ), family + " forged complete process " + str(number))
            for phase in range(2):
                for role in FAMILIES[family]["binaries"]:
                    for key in ("path", "sha256", "size_bytes", "elf",
                                "prebuilt_binary_read", "candidate_imported"):
                        forged = copy.deepcopy(report)
                        output = forged["build_phases"][phase]["native_outputs"][role]
                        if key in {"prebuilt_binary_read", "candidate_imported"}:
                            output[key] = True
                        else:
                            output.pop(key)
                        rejected(lambda forged=forged: validate_build_report(
                            forged, receipt, archive, arguments, pins,
                        ), family + " altered " + role + " phase "
                        + str(phase) + ":" + key)
            for relative in pins:
                forged = copy.deepcopy(report)
                forged["owned_source_after"][relative]["inode"] += 1
                rejected(lambda forged=forged: validate_build_report(
                    forged, receipt, archive, arguments, pins,
                ), family + " replaced source inode " + relative)
            for wrong in ("", "0" * 63, "g" * 64, "A" * 64, 7, None):
                rejected(lambda wrong=wrong: checked_digest(wrong, "hostile"),
                         family + " malformed digest")
            for wrong in ("", ".", "..", "/tmp/x", "x/../y", "x//y",
                          "x/./y", "x\\y", "x\x00y"):
                rejected(lambda wrong=wrong: checked_relative(wrong),
                         family + " escaped relative path")
            for wrong in ("/", "/tmp", "/tmp/", ROOT,
                          "/tmp/" + BUILD_PREFIX + family + "-",
                          "/tmp/" + BUILD_PREFIX + family + "-x/y",
                          "/tmp/" + BUILD_PREFIX + "other-x"):
                rejected(lambda wrong=wrong: checked_private_root(
                    wrong, family, build=True,
                ), family + " unsafe build root")
            for raw in (archive + b"suffix", archive[:-1], b"", b"not-gzip"):
                rejected(lambda raw=raw: bounded_gzip(raw),
                         family + " altered source-build archive")
            for forbidden in (
                "regexec@GLIBC_2.2.5", "regcomp@GLIBC_2.2.5",
                "dlopen@GLIBC_2.2.5", "pcre2_match", "onig_search",
                "_sre", "PyInit__sre", "re2_match", "hs_scan",
                "regex_match", "PyRun_String", "(2)", "@GLIBC_2.4",
                "real@", "real@@", "real@@@GLIBC_2.4",
            ):
                rejected(lambda forbidden=forbidden: checked_symbol_name(forbidden),
                         family + " delegated or version-index symbol")
            reordered = copy.deepcopy(report)
            reordered["build_phases"].reverse()
            rejected(lambda: validate_build_report(
                reordered, receipt, archive, arguments, pins,
            ), family + " swapped genuine phase order")
            one = copy.deepcopy(report)
            one["build_phases"].pop()
            rejected(lambda: validate_build_report(
                one, receipt, archive, arguments, pins,
            ), family + " omitted second fresh build")
            for option in (
                "--family", "--build-label", "--build-root",
                "--activation-source-sha256", "--activation-protocol-sha256",
                "--build-source-sha256", "--build-protocol-sha256",
                "--build-report-sha256", "--build-receipt-sha256",
                "--native-engine-sha256", "--native-bridge-sha256",
                "--native-engine-bytes", "--native-bridge-bytes",
            ):
                index = command.index(option)
                omitted = command[:index] + command[index + 2:]
                rejected(lambda omitted=omitted: parse_arguments(omitted),
                         family + " omitted exact option " + option)
                duplicated = command + command[index:index + 2]
                rejected(lambda duplicated=duplicated:
                         parse_arguments(duplicated),
                         family + " duplicated exact option " + option)
            for category, operation in (
                ("filesystem", lambda: builtins.open("forbidden", "rb")),
                ("filesystem", lambda: os.open("forbidden", os.O_RDONLY)),
                ("filesystem", lambda: os.write(1, b"forbidden")),
                ("filesystem", lambda: os.replace("forbidden", "also-forbidden")),
                ("filesystem", lambda: os.unlink("forbidden")),
                ("filesystem", lambda: os.fsync(1)),
                ("filesystem", lambda: os.fchmod(1, 0o600)),
                ("filesystem", lambda: os.mkdir("forbidden")),
                ("filesystem", lambda: tempfile.mkdtemp()),
                ("process", lambda: subprocess.run(["forbidden"])),
                ("process", lambda: os.system("forbidden")),
                ("thread", lambda: threading.Thread(target=lambda: None).start()),
                ("clock", lambda: time.perf_counter()),
                ("clock", lambda: time.time()),
                ("network", lambda: socket.socket()),
                ("network", lambda: socket.create_connection(("example", 1))),
                ("environment", lambda: os.getenv("PATH")),
                ("environment", lambda: os.environ.get("PATH")),
                ("import", lambda: importlib.import_module("candidates.vm_candidate")),
                ("import", lambda: builtins.__import__("candidates.zig_candidate")),
            ):
                before = sandbox.blocked[category]
                rejected(operation, family + " source-only " + category)
                positive(sandbox.blocked[category] == before + 1,
                         family + " genuinely blocked " + category)
        blocked = dict(sandbox.blocked)
    require(all(count > 0 for count in blocked.values()),
            "every genuine source-only boundary must be actually exercised")
    return {
        "schema": SCHEMA + "-synthetic-source-only-self-test",
        "status": "PASS",
        "positive_controls": positives,
        "hostile_controls": hostiles,
        "family_count": 3,
        "blocked_operations": blocked,
        **zero_effects(),
    }


def main(arguments: list[str] | None = None) -> int:
    try:
        parsed = parse_arguments(sys.argv[1:] if arguments is None else arguments)
        if parsed["mode"] == "self-test":
            result = self_test()
        elif parsed["mode"] == "activate":
            result = activate(parsed)
        elif parsed["mode"] == "recover":
            result = recover(parsed)
        else:
            require(parsed["mode"] == "restore",
                    "reject a substituted canonical activation mode")
            result = restore(parsed)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (ActivationError, OSError, ValueError, TypeError,
            RecursionError, zlib.error) as error:
        failure = {
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error_message": str(error),
            **zero_effects(),
        }
        sys.stdout.buffer.write(canonical(failure))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
