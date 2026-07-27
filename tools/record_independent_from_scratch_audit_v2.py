#!/usr/bin/env python3
"""Durably record one frozen, from-scratch Rust, C, or Zig ownership audit.

The synthetic ``--self-test`` never reads candidate files, starts a process,
measures time, or writes evidence. Only an explicitly pinned ``--candidate``
may start the one independently frozen V2 audit controller. Both complete
process streams, including genuine failures and native crashes, are preserved
in a fresh, atomically published report and independently linked receipt.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
from dataclasses import dataclass
import gc
import hashlib
import importlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Iterator, Mapping


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/record_independent_from_scratch_audit_v2.py"
SCHEMA = "rebar-independent-from-scratch-audit-v2-recorder"
AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v2.py"
AUDIT_SHA256 = "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
AUDIT_ORACLE = "independent-from-scratch-audit-v2"
AUDIT_PREDECESSOR = "tools/rust_from_scratch_audit_v1.py"
AUDIT_PREDECESSOR_SHA256 = (
    "536dea67430257ea38e968c98e9da50462d37fb8188a973e33775d14d7545ce0"
)
RECORDER_PREDECESSOR = "tools/record_rust_original_cpython_v3.py"
RECORDER_PREDECESSOR_SHA256 = (
    "ab3000efb5b6697864a3d0f12cf935ec19fae225fce0a1bf2930b34690043f9c"
)
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
APPROVED_DIRECTORY = "experiments/rust_public_practice_v1"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024
MAX_REPORT_BYTES = 96 * 1024 * 1024
ZIG_CTYPES_SYMBOLS = frozenset({
    "rebar_zig_compile", "rebar_zig_free", "rebar_zig_groups",
    "rebar_zig_flags", "rebar_zig_program_memory", "rebar_zig_name_count",
    "rebar_zig_name_length", "rebar_zig_name_group", "rebar_zig_name_copy",
})
ZIG_BRIDGE_REFERENCES = frozenset({
    "rebar_zig_collect_records_wide", "rebar_zig_compile",
    "rebar_zig_compile_guarded", "rebar_zig_flags", "rebar_zig_free",
    "rebar_zig_groups", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_wide", "rebar_zig_name_copy", "rebar_zig_name_count",
    "rebar_zig_name_group", "rebar_zig_name_length",
})
RUST_ENGINE_EXPORTS = frozenset({
    "rebar_collect_ascii", "rebar_collect_wide", "rebar_compile",
    "rebar_compile_scanner", "rebar_error_copy", "rebar_error_include",
    "rebar_error_len", "rebar_error_pos", "rebar_flags", "rebar_free",
    "rebar_groups", "rebar_match", "rebar_match_ascii", "rebar_match_wide",
    "rebar_name_copy", "rebar_name_count", "rebar_name_group", "rebar_name_len",
})
ZIG_ENGINE_EXPORTS = frozenset({
    "rebar_zig_batch", "rebar_zig_collect_captures", "rebar_zig_collect_records",
    "rebar_zig_collect_records_wide", "rebar_zig_compile",
    "rebar_zig_compile_guarded", "rebar_zig_flags", "rebar_zig_free",
    "rebar_zig_groups", "rebar_zig_match", "rebar_zig_match_captures",
    "rebar_zig_match_captures_wide", "rebar_zig_match_inverted_wide",
    "rebar_zig_match_nonempty_wide", "rebar_zig_match_tree",
    "rebar_zig_match_wide", "rebar_zig_name_copy", "rebar_zig_name_count",
    "rebar_zig_name_group", "rebar_zig_name_length", "rebar_zig_program_memory",
    "rebar_zig_program_size",
})
ZIG_SYSTEM_HELPERS = frozenset({
    "_PyUnicode_IsAlpha", "_PyUnicode_IsDecimalDigit", "_PyUnicode_IsDigit",
    "_PyUnicode_IsNumeric", "_PyUnicode_IsWhitespace",
    "_PyUnicode_ToLowercase", "_PyUnicode_ToUppercase", "tolower", "isalnum",
})


@dataclass(frozen=True)
class FamilySpec:
    name: str
    module: str
    bridge_module: str
    adapter: str
    engine: str
    bridge: str
    sources: tuple[tuple[str, str], ...]
    binaries: tuple[tuple[str, str], ...]


FAMILY_SPECS = {
    "rust": FamilySpec(
        "rust", "candidates.rust_candidate", "candidates._rust_bridge",
        "candidates/rust_candidate.py", "candidates/_rust_engine.so",
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        (
            ("candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b"),
            ("candidates/rust/py_bridge.c", "6f4401a8e9205e3e7b9797dd655f1a0b3d51190b8bd5239f77c5ad1534707f2d"),
            ("candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966"),
            ("candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63"),
            ("candidates/rust/src/lib.rs", "4ac8f3e9b96e37f5670cb610c6b031315eeedf92fd645399ac693f2f3d27ba72"),
            ("candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b"),
            ("candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe"),
            ("candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e"),
            ("candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af"),
        ),
        (
            ("candidates/_rust_engine.so", "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4"),
            ("candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so", "a7ef601a91527d7dcefcacb4c602afb972e4adbbed7d112239e7896530416c02"),
        ),
    ),
    "c": FamilySpec(
        "c", "candidates.vm_candidate", "candidates._vm_native",
        "candidates/vm_candidate.py",
        "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        (
            ("candidates/vm_candidate.py", "2bd8cd6d3844d6cd8c94f338803b41671d6aa1e999897e21a81cbe91182eb2fb"),
            ("candidates/_vm_native.c", "a516ae8f2409af054b456068e403df63d8fea029a516ce1adb22ee5f836a819c"),
        ),
        (("candidates/_vm_native.cpython-314-x86_64-linux-gnu.so", "9308563f7541f7b9f56afc7965a47ae4d4d00b1a94db8857891e493a82ae5148"),),
    ),
    "zig": FamilySpec(
        "zig", "candidates.zig_candidate", "candidates._zig_bridge",
        "candidates/zig_candidate.py", "candidates/_zig_probe.so",
        "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        (
            ("candidates/zig_candidate.py", "07e9fa19af8fe9938dc8ed5170e30a478ff56f0d04cd2488a0bd1869e28201cc"),
            ("candidates/zig/mini_regex.zig", "539bf5d378e0c2845c01519fcce62f1ef5e68610f477912c44a03027fb67a346"),
            ("candidates/zig/py_bridge.c", "f4900d04734a7c02bd766aee81c1d64114803dbefcf6f4591bfb667262658fea"),
        ),
        (
            ("candidates/_zig_probe.so", "96b899f8c5f25e4c94fe029d6218c0408cd20f7a86d661bcc4ce891648f17cb6"),
            ("candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so", "ad1a7ea024721e329857753d288abd834fcfc029055a6274195daf00754bf65a"),
        ),
    ),
}


class RecorderError(Exception):
    """The frozen audit, captured process, or durable publication is unsafe."""


class SourceOnlyError(RecorderError):
    """A synthetic control attempted a real side effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise RecorderError(message)


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        ) + "\n").encode("ascii")
    except (TypeError, ValueError, UnicodeError) as error:
        raise RecorderError("evidence is not complete canonical JSON") from error


def validate_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(letter in "0123456789abcdef" for letter in value)
        and len(set(value)) > 1,
        "an independently pinned lowercase SHA-256 is required: " + label,
    )
    return value


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
        and bool(sys.path) and sys.path[0] == str(ROOT)
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
        and os.path.abspath(sys.executable) == str(PINNED_PYTHON),
        "use only isolated, no-bytecode, frozen CPython 3.14.6",
    )
    require(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules),
        "the recorder must never import or execute a candidate in its own process",
    )


def validate_family(value: Any) -> FamilySpec:
    require(type(value) is str and value in FAMILY_SPECS,
            "choose exactly one frozen Rust, C, or Zig candidate family")
    return FAMILY_SPECS[value]


def validate_label(value: Any) -> str:
    require(
        type(value) is str and 1 <= len(value) <= 64
        and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and value[-1] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and all(c in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in value)
        and "--" not in value,
        "a bounded, lowercase, nonescaping audit-run label is required",
    )
    return value


def approved_paths(family: Any, label: Any) -> tuple[str, str]:
    spec = validate_family(family)
    slug = spec.name + "-from-scratch-audit-v2-" + validate_label(label)
    return (
        APPROVED_DIRECTORY + "/" + slug + ".json",
        APPROVED_DIRECTORY + "/" + slug + "-publication-receipt.json",
    )


def safe_parts(relative: Any) -> tuple[str, ...]:
    require(type(relative) is str and bool(relative)
            and "\\" not in relative and "\x00" not in relative,
            "an exact owned no-follow relative path is mandatory")
    parts = tuple(relative.split("/"))
    require(all(part not in ("", ".", "..") for part in parts)
            and "/".join(parts) == relative,
            "an escaping or noncanonical audit path was rejected")
    return parts


def directory_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))


def regular_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def read_owned_regular(relative: str, expected: str, maximum: int) -> dict[str, Any]:
    parts = safe_parts(relative)
    expected = validate_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "a bounded frozen source or native artifact is required")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "invalid repository root")
        for component in parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a frozen source parent is not an owned no-follow directory")
        descriptor = os.open(parts[-1], regular_flags(), dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino) == (named.st_dev, named.st_ino)
                and 0 < before.st_size <= maximum,
                "a frozen owned artifact is linked, replaced, missing, or unbounded")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part), "a frozen artifact was truncated")
            chunks.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"", "a frozen artifact has a hidden suffix")
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size)
                == (after.st_dev, after.st_ino, after.st_size),
                "a frozen owned artifact changed while being authenticated")
        raw = b"".join(chunks)
        require(hashlib.sha256(raw).hexdigest() == expected,
                "a prospectively frozen source or binary changed: " + relative)
        return {
            "relative": relative, "sha256": expected, "bytes": len(raw),
            "device": before.st_dev, "inode": before.st_ino,
        }
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def authenticate_artifacts(spec: FamilySpec) -> dict[str, Any]:
    verify_runtime()
    audit = read_owned_regular(AUDIT_RELATIVE, AUDIT_SHA256, MAX_SOURCE_BYTES)
    audit_predecessor = read_owned_regular(
        AUDIT_PREDECESSOR, AUDIT_PREDECESSOR_SHA256, MAX_SOURCE_BYTES,
    )
    recorder_predecessor = read_owned_regular(
        RECORDER_PREDECESSOR, RECORDER_PREDECESSOR_SHA256, MAX_SOURCE_BYTES,
    )
    sources = {
        relative: read_owned_regular(relative, digest, MAX_SOURCE_BYTES)
        for relative, digest in spec.sources
    }
    binaries = {
        relative: read_owned_regular(relative, digest, MAX_BINARY_BYTES)
        for relative, digest in spec.binaries
    }
    return {
        "audit_source": audit,
        "audit_predecessor": audit_predecessor,
        "recorder_predecessor": recorder_predecessor,
        "family": spec.name,
        "candidate_module": spec.module,
        "bridge_module": spec.bridge_module,
        "sources": sources,
        "native_binaries": binaries,
    }


@contextlib.contextmanager
def preflight_fresh_outputs(family: str, label: str) -> Iterator[dict[str, Any]]:
    report, receipt = approved_paths(family, label)
    report_parts, receipt_parts = safe_parts(report), safe_parts(receipt)
    require(report_parts[:-1] == receipt_parts[:-1]
            == ("experiments", "rust_public_practice_v1")
            and report_parts[-1] != receipt_parts[-1],
            "preflight exactly two fresh family-specific owned audit outputs")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "invalid owned project root")
        for component in report_parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "the exact audit evidence directory follows a symlink")
        info = os.fstat(current)
        for basename in (report_parts[-1], receipt_parts[-1]):
            try:
                os.stat(basename, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise RecorderError("refusing to overwrite existing audit evidence: " + basename)
        preflight = {
            "report_relative": report, "receipt_relative": receipt,
            "report_basename": report_parts[-1],
            "receipt_basename": receipt_parts[-1],
            "directory_descriptor": current,
            "directory_device": info.st_dev, "directory_inode": info.st_ino,
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
        }
        retained_directory(preflight)
        yield preflight
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def require_directory_identity(
    retained: tuple[int, int], expected: tuple[int, int],
    literal: tuple[int, int],
) -> None:
    require(type(retained) is tuple and type(expected) is tuple
            and type(literal) is tuple
            and len(retained) == len(expected) == len(literal) == 2
            and all(type(item) is int and item >= 0
                    for identity in (retained, expected, literal)
                    for item in identity)
            and retained == expected and literal == retained,
            "the literal approved evidence path no longer names its retained directory")


def retained_directory(preflight: Mapping[str, Any]) -> int:
    descriptor = preflight.get("directory_descriptor")
    require(type(descriptor) is int and descriptor >= 0,
            "retain the exact preflighted owned audit directory")
    retained = os.fstat(descriptor)
    require(stat.S_ISDIR(retained.st_mode),
            "the preflighted owned audit directory was replaced")
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the literal audit repository root is not an owned directory")
        for component in ("experiments", "rust_public_practice_v1"):
            current = os.open(component, directory_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a literal approved evidence parent became a symlink")
        current_identity = os.fstat(current)
        require_directory_identity(
            (retained.st_dev, retained.st_ino),
            (preflight.get("directory_device"), preflight.get("directory_inode")),
            (current_identity.st_dev, current_identity.st_ino),
        )
    finally:
        for opened_descriptor in reversed(opened):
            os.close(opened_descriptor)
    return descriptor


def readback(
    preflight: Mapping[str, Any], basename: str, expected: bytes,
) -> None:
    directory = retained_directory(preflight)
    descriptor = os.open(basename, regular_flags(), dir_fd=directory)
    try:
        info = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(info.st_mode) and stat.S_ISREG(named.st_mode)
                and (info.st_dev, info.st_ino) == (named.st_dev, named.st_ino)
                and info.st_size == len(expected),
                "atomic audit evidence changed inode, type, or size")
        chunks: list[bytes] = []
        remaining = len(expected)
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part),
                    "atomic audit evidence readback was incomplete")
            chunks.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"", "atomic audit evidence has a suffix")
        require(b"".join(chunks) == expected,
                "the durably published complete audit evidence was altered")
    finally:
        os.close(descriptor)
    retained_directory(preflight)


def publish_atomic(
    preflight: Mapping[str, Any], document: Mapping[str, Any], kind: str,
) -> dict[str, Any]:
    require(kind in ("report", "receipt"), "publish only two approved audit outputs")
    directory = retained_directory(preflight)
    basename = preflight[kind + "_basename"]
    raw = canonical(dict(document))
    require(0 < len(raw) <= MAX_REPORT_BYTES, "complete audit evidence is unbounded")
    temporary = "." + basename + ".tmp-" + os.urandom(16).hex()
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor: int | None = None
    temporary_created = False
    write_calls = 0
    try:
        retained_directory(preflight)
        descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
        temporary_created = True
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode), "atomic audit temporary is not regular")
        position = 0
        while position < len(raw):
            written = os.write(descriptor, raw[position:])
            require(type(written) is int and written > 0,
                    "the complete atomic audit publication was truncated")
            write_calls += 1
            position += written
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        require((initial.st_dev, initial.st_ino) == (final.st_dev, final.st_ino)
                and final.st_size == len(raw),
                "the complete temporary audit publication was replaced")
        os.close(descriptor)
        descriptor = None
        retained_directory(preflight)
        os.link(temporary, basename, src_dir_fd=directory, dst_dir_fd=directory,
                follow_symlinks=False)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino) == (initial.st_dev, initial.st_ino),
                "the audit publication did not atomically link its own complete inode")
        os.unlink(temporary, dir_fd=directory)
        temporary_created = False
        retained_directory(preflight)
        os.fsync(directory)
        retained_directory(preflight)
        readback(preflight, basename, raw)
        retained_directory(preflight)
        return {
            "path": preflight[kind + "_relative"],
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw), "actual_write_calls": write_calls,
            "atomic_no_overwrite_link_completed": True,
            "file_fsync_completed": True,
            "directory_fsync_completed": True,
            "complete_readback_verified": True,
        }
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_created:
            try:
                actual = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
                if (actual.st_dev, actual.st_ino) == (initial.st_dev, initial.st_ino):
                    os.unlink(temporary, dir_fd=directory)
                    os.fsync(directory)
            except FileNotFoundError:
                pass


def capture_stream(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "the complete bounded audit stream must be preserved: " + label)
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
    }


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "duplicate audit JSON keys cannot conceal a failure")
        result[key] = value
    return result


def decode_audit(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "the complete frozen audit result is required")
    try:
        result = json.loads(
            raw, object_pairs_hook=unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(
                RecorderError("nonfinite ownership evidence is forbidden"),
            ),
        )
    except (UnicodeError, ValueError, TypeError, json.JSONDecodeError) as error:
        raise RecorderError("the complete audit stdout is not canonical JSON") from error
    require(type(result) is dict and canonical(result) == raw,
            "the frozen audit did not emit exact complete canonical evidence")
    return result


def expected_dynamic(spec: FamilySpec, binary: str) -> tuple[list[str], list[str]]:
    require(binary in dict(spec.binaries), "an ELF artifact crosses candidate families")
    if spec.name == "rust" and binary == spec.engine:
        return sorted(("libgcc_s.so.1", "libc.so.6", "ld-linux-x86-64.so.2")), []
    if spec.name == "rust":
        return sorted(("_rust_engine.so", "libc.so.6")), ["$ORIGIN"]
    if spec.name == "c" or binary == spec.engine:
        return ["libc.so.6"], []
    return sorted(("_zig_probe.so", "libc.so.6")), ["$ORIGIN"]


def expected_exports(spec: FamilySpec, binary: str) -> list[str]:
    if spec.name == "rust" and binary == spec.engine:
        return sorted(RUST_ENGINE_EXPORTS)
    if spec.name == "rust":
        return ["PyInit__rust_bridge"]
    if spec.name == "c":
        return ["PyInit__vm_native"]
    if binary == spec.engine:
        return sorted(ZIG_ENGINE_EXPORTS)
    return ["PyInit__zig_bridge"]


def expected_owned_references(spec: FamilySpec, binary: str) -> list[str]:
    require(binary in dict(spec.binaries),
            "an owned native symbol reference crosses candidate families")
    if spec.name == "rust" and binary == spec.bridge:
        return sorted(RUST_ENGINE_EXPORTS)
    if spec.name == "zig" and binary == spec.bridge:
        return sorted(ZIG_BRIDGE_REFERENCES)
    return []


def expected_undefined_count(spec: FamilySpec, binary: str) -> int:
    require(binary in dict(spec.binaries),
            "an undefined-symbol table crosses candidate families")
    if spec.name == "rust":
        return 53 if binary == spec.engine else 143
    if spec.name == "c":
        return 130
    return 17 if binary == spec.engine else 124


def expected_adapter(spec: FamilySpec) -> dict[str, Any]:
    if spec.name == "rust":
        return {
            "modules": sorted(("enum", "operator", "os", "types", "unicodedata", "warnings")),
            "from_imports": [["candidates", "_rust_bridge", None]],
        }
    if spec.name == "c":
        return {
            "modules": sorted(("enum", "os", "types", "unicodedata", "warnings")),
            "from_imports": [
                ["candidates", "_vm_native", None],
                ["copyreg", "_reconstructor", "_copy_reconstructor"],
                ["struct", "calcsize", "_native_calcsize"],
            ],
        }
    return {
        "modules": sorted(("ctypes", "enum", "os", "types", "unicodedata", "warnings")),
        "from_imports": [["candidates", "_zig_bridge", None]],
        "owned_ctypes": {
            "owned_library": "candidates/_zig_probe.so",
            "configured_symbols": sorted(ZIG_CTYPES_SYMBOLS),
        },
    }


def expected_bridge(spec: FamilySpec) -> dict[str, Any]:
    if spec.name == "rust":
        headers = ("Python.h", "stddef.h", "stdint.h", "string.h")
        imports = ("copyreg", "functools", "inspect")
    elif spec.name == "c":
        headers = ("Python.h", "ctype.h", "stddef.h", "stdint.h", "stdlib.h", "string.h")
        imports = ()
    else:
        headers = ("Python.h", "stddef.h", "stdint.h")
        imports = ()
    return {
        "includes": sorted(headers),
        "compatibility_imports": sorted(imports),
        "owned_compatible_scanner_names": 1,
    }


def expected_implementation(spec: FamilySpec) -> dict[str, Any]:
    if spec.name == "rust":
        return {
            "cargo": {
                "package": "rebar-rust-continuation", "package_count": 1,
                "external_package_count": 0, "build_script_count": 0,
            },
            "engine": {
                "source_count": 5,
                "owned_modules": ["newline", "search", "stack", "unicode_tables"],
            },
        }
    if spec.name == "c":
        return {"engine": "independently owned Python compiler and native C VM"}
    return {
        "engine": {
            "standard_library_imports": 1,
            "approved_unicode_and_system_helpers": sorted(ZIG_SYSTEM_HELPERS),
            "external_regex_package_count": 0,
        },
    }


def validate_ownership_result(result: Any, spec: FamilySpec) -> dict[str, Any]:
    require(type(result) is dict and set(result) == {
        "oracle", "status", "python", "candidate", "candidate_module",
        "ownership", "runtime", "unchanged_before_after",
        "source_to_binary_reproducibility", "final_holdout_opened",
        "hidden_cases_read", "performance_measured", "winner_selected",
    }, "a complete, unmodified ownership audit result is mandatory")
    require(result["oracle"] == AUDIT_ORACLE and result["status"] == "PASS"
            and result["candidate"] == spec.name
            and result["candidate_module"] == spec.module
            and result["python"] == {
                "implementation": "cpython", "version": [3, 14, 6],
                "executable": str(PINNED_PYTHON),
            }, "the audit, isolated frozen Python, or candidate family was forged")
    require(result["unchanged_before_after"] is True
            and result["source_to_binary_reproducibility"] == "NOT ESTABLISHED"
            and result["final_holdout_opened"] is False
            and result["hidden_cases_read"] is False
            and result["performance_measured"] is False
            and result["winner_selected"] is False,
            "the ownership audit weakened its frozen boundaries or overstated reproducibility")
    owned = result["ownership"]
    require(type(owned) is dict and set(owned) == {
        "family", "source_sha256", "native_sha256",
        "predecessor_source_sha256", "adapter", "bridge", "implementation",
        "native", "external_regex_package_count", "source_to_binary_reproducibility",
    }, "the complete actual source and native ELF ownership evidence is mandatory")
    require(owned["family"] == spec.name
            and owned["source_sha256"] == dict(spec.sources)
            and owned["native_sha256"] == dict(spec.binaries)
            and owned["predecessor_source_sha256"] == AUDIT_PREDECESSOR_SHA256
            and owned["external_regex_package_count"] == 0
            and type(owned["external_regex_package_count"]) is int
            and owned["source_to_binary_reproducibility"] == "NOT ESTABLISHED",
            "frozen source pins, native pins, external-package proof, or predecessor changed")
    require(type(owned["adapter"]) is dict
            and owned["adapter"] == expected_adapter(spec)
            and type(owned["bridge"]) is dict
            and owned["bridge"] == expected_bridge(spec)
            and type(owned["implementation"]) is dict
            and owned["implementation"] == expected_implementation(spec),
            "the exact owned parser, imports, bridge, FFI, or matching engine was forged")
    native = owned["native"]
    require(type(native) is dict and set(native) == set(dict(spec.binaries)),
            "the audit must inspect every exact owned native ELF binary")
    for binary in dict(spec.binaries):
        item = native.get(binary)
        needed, runpaths = expected_dynamic(spec, binary)
        require(type(item) is dict and set(item) == {
            "needed", "runpaths", "defined_exports",
            "undefined_symbol_count", "owned_engine_references",
        } and item["needed"] == needed and item["runpaths"] == runpaths
            and item["defined_exports"] == expected_exports(spec, binary)
            and type(item["undefined_symbol_count"]) is int
            and item["undefined_symbol_count"]
            == expected_undefined_count(spec, binary)
            and item["owned_engine_references"]
            == expected_owned_references(spec, binary),
            "complete frozen native dependencies, ABI, or ELF symbols were forged")
    runtime = result["runtime"]
    require(type(runtime) is dict and set(runtime) == {
        "status", "family", "runtime_checks", "owned_graph_checks",
        "guarded_import_calls", "forbidden_import_or_execution_count",
        "removed_preexisting_forbidden_module_count",
        "caller_replacement_callback_supported", "owned_public_re_names_supported",
        "owned_public_sre_scanner_name_supported",
        "actual_standard_library_engine_loaded", "candidate_modules",
        "owned_ctypes_library_load_count", "owned_ctypes_symbols",
    }, "complete isolated runtime ownership checks are mandatory")
    require(runtime["status"] == "PASS" and runtime["family"] == spec.name
            and type(runtime["runtime_checks"]) is int
            and runtime["runtime_checks"] >= 20
            and type(runtime["owned_graph_checks"]) is int
            and runtime["owned_graph_checks"] > 0
            and type(runtime["guarded_import_calls"]) is int
            and runtime["guarded_import_calls"] > 0
            and type(runtime["removed_preexisting_forbidden_module_count"]) is int
            and runtime["removed_preexisting_forbidden_module_count"] >= 0
            and type(runtime["forbidden_import_or_execution_count"]) is int
            and runtime["forbidden_import_or_execution_count"] == 0
            and runtime["caller_replacement_callback_supported"] is True
            and runtime["owned_public_re_names_supported"] is True
            and runtime["owned_public_sre_scanner_name_supported"] is True
            and runtime["actual_standard_library_engine_loaded"] is False
            and runtime["candidate_modules"]
            == sorted((spec.module, spec.bridge_module)),
            "guarded actual matching, callbacks, imports, or engine ownership failed")
    expected_loads = 1 if spec.name == "zig" else 0
    expected_symbols = sorted(ZIG_CTYPES_SYMBOLS) if spec.name == "zig" else []
    require(type(runtime["owned_ctypes_library_load_count"]) is int
            and runtime["owned_ctypes_library_load_count"] == expected_loads
            and runtime["owned_ctypes_symbols"] == expected_symbols,
            "native FFI must use only the exact candidate-owned Zig engine")
    return result


def run_one_audit(spec: FamilySpec) -> dict[str, Any]:
    command = [str(PINNED_PYTHON), "-I", "-B", str(ROOT / AUDIT_RELATIVE),
               "--candidate", spec.name]
    environment = {
        "LC_ALL": "C", "PATH": "/usr/bin:/bin",
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
    }
    try:
        process = subprocess.Popen(
            command, cwd=str(ROOT), env=environment,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {
            "started": False, "pid": None, "returncode": None,
            "timed_out": False, "signal": None, "spawn_error": str(error),
            "stdout": b"", "stderr": b"",
        }
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=120)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        stdout, stderr = process.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes,
            "the isolated actual audit must preserve both complete byte streams")
    code = process.returncode
    require(type(code) is int, "the genuine ownership audit process has no exit status")
    return {
        "started": True, "pid": process.pid, "returncode": code,
        "timed_out": timed_out, "signal": -code if code < 0 else None,
        "spawn_error": None, "stdout": stdout, "stderr": stderr,
    }


def build_complete_report(
    spec: FamilySpec, label: str, process: Mapping[str, Any],
    before: Mapping[str, Any], after: Mapping[str, Any] | None,
    post_run_error: str | None = None,
) -> dict[str, Any]:
    failures: list[str] = []
    stdout = capture_stream(process.get("stdout"), "isolated audit stdout")
    stderr = capture_stream(process.get("stderr"), "isolated audit stderr")
    if process.get("started") is not True:
        failures.append("audit controller could not start: " + str(process.get("spawn_error")))
    if process.get("timed_out") is True:
        failures.append("the independently guarded audit exceeded its frozen timeout")
    if process.get("returncode") != 0:
        failures.append("the genuine audit controller returned a failing or signal exit")
    if process.get("stderr"):
        failures.append("the frozen audit emitted genuine diagnostic stderr")
    if post_run_error is not None:
        failures.append("post-audit frozen source authentication failed: " + post_run_error)
    if after != before:
        failures.append("the independently frozen artifacts changed during the audit")
    result: dict[str, Any] | None = None
    try:
        result = decode_audit(process.get("stdout"))
    except RecorderError as error:
        failures.append(str(error))
    if result is not None:
        try:
            validate_ownership_result(result, spec)
        except RecorderError as error:
            failures.append(str(error))
    return {
        "schema": SCHEMA + "-complete-report",
        "status": "FAIL" if failures else "PASS",
        "label": validate_label(label),
        "family": spec.name,
        "candidate_module": spec.module,
        "bridge_module": spec.bridge_module,
        "python": {
            "implementation": "cpython", "version": [3, 14, 6],
            "executable": str(PINNED_PYTHON),
        },
        "frozen_audit_relative": AUDIT_RELATIVE,
        "frozen_audit_sha256": AUDIT_SHA256,
        "frozen_audit_predecessor_relative": AUDIT_PREDECESSOR,
        "frozen_audit_predecessor_sha256": AUDIT_PREDECESSOR_SHA256,
        "frozen_recorder_predecessor_relative": RECORDER_PREDECESSOR,
        "frozen_recorder_predecessor_sha256": RECORDER_PREDECESSOR_SHA256,
        "frozen_source_sha256": dict(spec.sources),
        "frozen_native_sha256": dict(spec.binaries),
        "complete_artifacts_before": dict(before),
        "complete_artifacts_after": dict(after) if after is not None else None,
        "unchanged_before_after": after == before,
        "complete_process_stdout": stdout,
        "complete_process_stderr": stderr,
        "actual_audit_process_started": process.get("started") is True,
        "actual_audit_process_count": int(process.get("started") is True),
        "actual_audit_process_pid": process.get("pid"),
        "actual_audit_process_returncode": process.get("returncode"),
        "actual_audit_process_signal": process.get("signal"),
        "actual_audit_process_timed_out": process.get("timed_out") is True,
        "actual_audit_process_spawn_error": process.get("spawn_error"),
        "complete_frozen_audit_result": result,
        "all_failure_reasons": failures,
        "failure_count": len(failures),
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "hidden_cases_read": 0,
        "performance_files_read": 0,
        "timing_trials_run": 0,
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def record_audit(spec: FamilySpec, label: str) -> dict[str, Any]:
    verify_runtime()
    validate_label(label)
    before = authenticate_artifacts(spec)
    with preflight_fresh_outputs(spec.name, label) as preflight:
        retained_directory(preflight)
        process = run_one_audit(spec)
        retained_directory(preflight)
        after: dict[str, Any] | None = None
        post_run_error: str | None = None
        try:
            after = authenticate_artifacts(spec)
        except (RecorderError, OSError) as error:
            post_run_error = str(error)
        report = build_complete_report(spec, label, process, before, after, post_run_error)
        report_publication = publish_atomic(preflight, report, "report")
        receipt = {
            "schema": SCHEMA + "-publication-receipt",
            "publication_status": "PASS",
            "audit_status": report["status"],
            "family": spec.name, "label": label,
            "candidate_module": spec.module,
            "frozen_audit_relative": AUDIT_RELATIVE,
            "frozen_audit_sha256": AUDIT_SHA256,
            "frozen_audit_predecessor_sha256": AUDIT_PREDECESSOR_SHA256,
            "frozen_recorder_predecessor_sha256": RECORDER_PREDECESSOR_SHA256,
            "frozen_source_sha256": dict(spec.sources),
            "frozen_native_sha256": dict(spec.binaries),
            "report_publication": report_publication,
            "receipt_relative": preflight["receipt_relative"],
            "approved_fresh_path_count": 2,
            "fresh_paths_checked_before_candidate": True,
            "source_to_binary_reproducibility": "NOT ESTABLISHED",
            "hidden_cases_read": 0, "performance_files_read": 0,
            "timing_trials_run": 0,
            "final_holdout_opened": False, "winner_selected": False,
        }
        receipt_publication = publish_atomic(preflight, receipt, "receipt")
    verify_runtime()
    return {
        "schema": SCHEMA + "-recorded",
        "status": report["status"],
        "publication_status": "PASS",
        "family": spec.name, "label": label,
        "report_publication": report_publication,
        "receipt_publication": receipt_publication,
        "actual_audit_process_count": report["actual_audit_process_count"],
        "all_failure_reasons": report["all_failure_reasons"],
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "hidden_cases_read": 0, "performance_files_read": 0,
        "timing_trials_run": 0,
        "final_holdout_opened": False, "winner_selected": False,
    }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {key: 0 for key in (
        "blocked_reads", "blocked_writes", "blocked_imports",
        "blocked_workers", "blocked_threads", "blocked_clocks",
        "blocked_gc_collections",
    )}
    installed: list[tuple[Any, str, Any]] = []

    def deny(key: str, message: str) -> Callable[..., Any]:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            effects[key] += 1
            raise SourceOnlyError(message)
        return blocked

    def install(owner: Any, name: str, replacement: Any) -> None:
        original = getattr(owner, name, None)
        if original is not None:
            installed.append((owner, name, original))
            setattr(owner, name, replacement)

    try:
        for owner, name in ((builtins, "open"), (os, "open"), (os, "read"),
                            (Path, "open"), (Path, "read_bytes"), (Path, "read_text")):
            install(owner, name, deny("blocked_reads", "synthetic audit cannot read files"))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"), (os, "rename"),
            (os, "replace"), (os, "mkdir"), (os, "rmdir"), (os, "fsync"),
            (os, "link"), (Path, "write_bytes"), (Path, "write_text"),
            (Path, "unlink"), (Path, "mkdir"),
        ):
            install(owner, name, deny("blocked_writes", "synthetic audit cannot write files"))
        install(importlib, "import_module",
                deny("blocked_imports", "synthetic audit cannot import candidates"))
        install(subprocess, "Popen",
                deny("blocked_workers", "synthetic audit cannot start a process"))
        install(subprocess, "run",
                deny("blocked_workers", "synthetic audit cannot start a process"))
        install(threading.Thread, "start",
                deny("blocked_threads", "synthetic audit cannot start a thread"))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns"):
            install(time, name, deny("blocked_clocks", "synthetic audit cannot time work"))
        install(gc, "collect",
                deny("blocked_gc_collections", "synthetic audit cannot collect garbage"))
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def synthetic_result(spec: FamilySpec) -> dict[str, Any]:
    native: dict[str, Any] = {}
    for binary, _ in spec.binaries:
        needed, runpaths = expected_dynamic(spec, binary)
        native[binary] = {
            "needed": needed, "runpaths": runpaths,
            "defined_exports": expected_exports(spec, binary),
            "undefined_symbol_count": expected_undefined_count(spec, binary),
            "owned_engine_references": expected_owned_references(spec, binary),
        }
    return {
        "oracle": AUDIT_ORACLE, "status": "PASS",
        "python": {"implementation": "cpython", "version": [3, 14, 6],
                   "executable": str(PINNED_PYTHON)},
        "candidate": spec.name, "candidate_module": spec.module,
        "ownership": {
            "family": spec.name, "source_sha256": dict(spec.sources),
            "native_sha256": dict(spec.binaries),
            "predecessor_source_sha256": AUDIT_PREDECESSOR_SHA256,
            "adapter": expected_adapter(spec),
            "bridge": expected_bridge(spec),
            "implementation": expected_implementation(spec),
            "native": native, "external_regex_package_count": 0,
            "source_to_binary_reproducibility": "NOT ESTABLISHED",
        },
        "runtime": {
            "status": "PASS", "family": spec.name, "runtime_checks": 20,
            "owned_graph_checks": 1, "guarded_import_calls": 1,
            "forbidden_import_or_execution_count": 0,
            "removed_preexisting_forbidden_module_count": 0,
            "caller_replacement_callback_supported": True,
            "owned_public_re_names_supported": True,
            "owned_public_sre_scanner_name_supported": True,
            "actual_standard_library_engine_loaded": False,
            "candidate_modules": sorted((spec.module, spec.bridge_module)),
            "owned_ctypes_library_load_count": 1 if spec.name == "zig" else 0,
            "owned_ctypes_symbols": sorted(ZIG_CTYPES_SYMBOLS)
            if spec.name == "zig" else [],
        },
        "unchanged_before_after": True,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "final_holdout_opened": False, "hidden_cases_read": False,
        "performance_measured": False, "winner_selected": False,
    }


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []
    with source_only_boundary() as effects:
        def accept(label: str, condition: Any) -> None:
            require(condition, "synthetic audit positive control failed: " + label)
            accepted.append(label)

        def reject(label: str, operation: Callable[[], Any]) -> None:
            try:
                operation()
            except (RecorderError, OSError, ValueError, TypeError, KeyError):
                rejected.append(label)
                return
            raise RecorderError("synthetic audit poison was accepted: " + label)

        for name, spec in FAMILY_SPECS.items():
            result = synthetic_result(spec)
            accept(name + "-complete-owned-audit", validate_ownership_result(result, spec) is result)
            raw = canonical(result)
            accept(name + "-complete-canonical-process", decode_audit(raw) == result)
            report, receipt = approved_paths(name, "synthetic-proof")
            accept(name + "-two-family-specific-fresh-paths",
                   report.startswith(APPROVED_DIRECTORY + "/" + name + "-")
                   and receipt.startswith(APPROVED_DIRECTORY + "/" + name + "-")
                   and report != receipt)

            before = {"family": name, "synthetic": True}
            passing_process = {
                "started": True, "pid": 701, "returncode": 0,
                "timed_out": False, "signal": None, "spawn_error": None,
                "stdout": raw, "stderr": b"",
            }
            passing_report = build_complete_report(
                spec, "synthetic-proof", passing_process, before, before,
            )

            def complete_stream(item: Mapping[str, Any], expected: bytes) -> bool:
                return (
                    type(item) is dict
                    and item.get("complete") is True
                    and item.get("bytes") == len(expected)
                    and item.get("sha256") == hashlib.sha256(expected).hexdigest()
                    and base64.b64decode(item.get("base64", ""), validate=True)
                    == expected
                )

            accept(name + "-complete-passing-report",
                   passing_report["status"] == "PASS"
                   and passing_report["failure_count"] == 0
                   and passing_report["all_failure_reasons"] == []
                   and passing_report["complete_frozen_audit_result"] == result
                   and passing_report["actual_audit_process_pid"] == 701
                   and passing_report["actual_audit_process_returncode"] == 0
                   and complete_stream(passing_report["complete_process_stdout"], raw)
                   and complete_stream(passing_report["complete_process_stderr"], b""))

            audit_failure = canonical({
                "oracle": AUDIT_ORACLE, "status": "FAIL",
                "error": "synthetic frozen ownership mismatch",
            })
            failing_process = {
                **passing_process, "returncode": 1,
                "stdout": audit_failure,
                "stderr": b"synthetic complete frozen failure traceback\n",
            }
            failure_report = build_complete_report(
                spec, "synthetic-proof", failing_process, before, before,
            )
            accept(name + "-preserve-complete-genuine-audit-failure",
                   failure_report["status"] == "FAIL"
                   and failure_report["failure_count"] >= 2
                   and failure_report["actual_audit_process_returncode"] == 1
                   and failure_report["complete_frozen_audit_result"]
                   == decode_audit(audit_failure)
                   and complete_stream(failure_report["complete_process_stdout"], audit_failure)
                   and complete_stream(failure_report["complete_process_stderr"],
                                       failing_process["stderr"]))

            crash_stdout = b"synthetic native crash before complete JSON\n"
            crash_stderr = b"synthetic complete native signal traceback\n"
            crash_process = {
                **passing_process, "returncode": -11, "signal": 11,
                "stdout": crash_stdout, "stderr": crash_stderr,
            }
            crash_report = build_complete_report(
                spec, "synthetic-proof", crash_process, before, before,
            )
            accept(name + "-preserve-complete-native-crash",
                   crash_report["status"] == "FAIL"
                   and crash_report["failure_count"] >= 2
                   and crash_report["actual_audit_process_returncode"] == -11
                   and crash_report["actual_audit_process_signal"] == 11
                   and crash_report["complete_frozen_audit_result"] is None
                   and complete_stream(crash_report["complete_process_stdout"], crash_stdout)
                   and complete_stream(crash_report["complete_process_stderr"], crash_stderr))

            timeout_process = {
                **crash_process, "returncode": -9, "signal": 9,
                "timed_out": True,
            }
            timeout_report = build_complete_report(
                spec, "synthetic-proof", timeout_process, before, before,
            )
            accept(name + "-preserve-complete-audit-timeout",
                   timeout_report["status"] == "FAIL"
                   and timeout_report["actual_audit_process_timed_out"] is True
                   and timeout_report["actual_audit_process_returncode"] == -9
                   and timeout_report["actual_audit_process_signal"] == 9
                   and complete_stream(timeout_report["complete_process_stdout"], crash_stdout)
                   and complete_stream(timeout_report["complete_process_stderr"], crash_stderr))

            unstarted_process = {
                "started": False, "pid": None, "returncode": None,
                "timed_out": False, "signal": None,
                "spawn_error": "synthetic exact frozen interpreter cannot start",
                "stdout": b"", "stderr": b"",
            }
            unstarted_report = build_complete_report(
                spec, "synthetic-proof", unstarted_process, before, before,
            )
            accept(name + "-preserve-complete-audit-spawn-failure",
                   unstarted_report["status"] == "FAIL"
                   and unstarted_report["actual_audit_process_started"] is False
                   and unstarted_report["actual_audit_process_count"] == 0
                   and unstarted_report["actual_audit_process_spawn_error"]
                   == unstarted_process["spawn_error"]
                   and unstarted_report["complete_frozen_audit_result"] is None
                   and complete_stream(unstarted_report["complete_process_stdout"], b"")
                   and complete_stream(unstarted_report["complete_process_stderr"], b""))

            changed_report = build_complete_report(
                spec, "synthetic-proof", passing_process, before,
                {"family": name, "synthetic": "substituted"},
            )
            accept(name + "-reject-post-run-owner-substitution",
                   changed_report["status"] == "FAIL"
                   and changed_report["unchanged_before_after"] is False
                   and changed_report["complete_frozen_audit_result"] == result
                   and complete_stream(changed_report["complete_process_stdout"], raw))

            diagnostic_process = {
                **passing_process, "stderr": b"synthetic unhidden diagnostic\n",
            }
            diagnostic_report = build_complete_report(
                spec, "synthetic-proof", diagnostic_process, before, before,
            )
            accept(name + "-reject-and-preserve-audit-diagnostics",
                   diagnostic_report["status"] == "FAIL"
                   and diagnostic_report["failure_count"] >= 1
                   and diagnostic_report["complete_frozen_audit_result"] == result
                   and complete_stream(diagnostic_report["complete_process_stderr"],
                                       diagnostic_process["stderr"]))

            for key in ("oracle", "status", "python", "candidate", "candidate_module",
                        "ownership", "runtime", "unchanged_before_after",
                        "source_to_binary_reproducibility", "final_holdout_opened",
                        "hidden_cases_read", "performance_measured", "winner_selected"):
                broken = copy.deepcopy(result)
                del broken[key]
                reject(name + "-missing-" + key,
                       lambda broken=broken: validate_ownership_result(broken, spec))
            poisons: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
                ("wrong-family", lambda item: item.__setitem__("candidate", "foreign")),
                ("wrong-module", lambda item: item.__setitem__("candidate_module", "re")),
                ("forged-python", lambda item: item["python"].__setitem__("version", [3, 14, 7])),
                ("missing-source-pin", lambda item: item["ownership"]["source_sha256"].pop(spec.adapter)),
                ("foreign-source-pin", lambda item: item["ownership"]["source_sha256"].__setitem__(spec.adapter, AUDIT_SHA256)),
                ("missing-native-pin", lambda item: item["ownership"]["native_sha256"].pop(spec.engine)),
                ("foreign-native-pin", lambda item: item["ownership"]["native_sha256"].__setitem__(spec.engine, AUDIT_SHA256)),
                ("foreign-predecessor", lambda item: item["ownership"].__setitem__("predecessor_source_sha256", AUDIT_SHA256)),
                ("missing-adapter-closure", lambda item: item["ownership"].__setitem__("adapter", {})),
                ("foreign-adapter-closure", lambda item: item["ownership"]["adapter"]["modules"].append("re")),
                ("extra-adapter-proof", lambda item: item["ownership"]["adapter"].__setitem__("foreign_engine", True)),
                ("missing-bridge-proof", lambda item: item["ownership"].__setitem__("bridge", {})),
                ("foreign-bridge-header", lambda item: item["ownership"]["bridge"]["includes"].append("pcre2.h")),
                ("borrowed-bridge-scanner", lambda item: item["ownership"]["bridge"].__setitem__("owned_compatible_scanner_names", 0)),
                ("missing-implementation", lambda item: item["ownership"].__setitem__("implementation", {})),
                ("foreign-implementation", lambda item: item["ownership"]["implementation"].__setitem__("external_regex", "pcre2")),
                ("external-package", lambda item: item["ownership"].__setitem__("external_regex_package_count", 1)),
                ("false-reproducibility", lambda item: item.__setitem__("source_to_binary_reproducibility", "ESTABLISHED")),
                ("false-native-reproducibility", lambda item: item["ownership"].__setitem__("source_to_binary_reproducibility", "ESTABLISHED")),
                ("hidden-holdout", lambda item: item.__setitem__("final_holdout_opened", True)),
                ("hidden-cases", lambda item: item.__setitem__("hidden_cases_read", True)),
                ("timing", lambda item: item.__setitem__("performance_measured", True)),
                ("early-winner", lambda item: item.__setitem__("winner_selected", True)),
                ("changed-artifacts", lambda item: item.__setitem__("unchanged_before_after", False)),
                ("incomplete-runtime", lambda item: item["runtime"].__setitem__("runtime_checks", 19)),
                ("no-owned-graph", lambda item: item["runtime"].__setitem__("owned_graph_checks", 0)),
                ("unguarded-imports", lambda item: item["runtime"].__setitem__("guarded_import_calls", 0)),
                ("foreign-engine", lambda item: item["runtime"].__setitem__("actual_standard_library_engine_loaded", True)),
                ("foreign-candidate", lambda item: item["runtime"].__setitem__("candidate_modules", ["candidates.foreign"])),
                ("forbidden-import", lambda item: item["runtime"].__setitem__("forbidden_import_or_execution_count", 1)),
                ("lost-callback", lambda item: item["runtime"].__setitem__("caller_replacement_callback_supported", False)),
                ("lost-owned-names", lambda item: item["runtime"].__setitem__("owned_public_re_names_supported", False)),
                ("lost-owned-scanner", lambda item: item["runtime"].__setitem__("owned_public_sre_scanner_name_supported", False)),
                ("foreign-ffi-load", lambda item: item["runtime"].__setitem__("owned_ctypes_library_load_count", 2)),
                ("foreign-ffi-symbol", lambda item: item["runtime"].__setitem__("owned_ctypes_symbols", ["regexec"])),
                ("missing-elf", lambda item: item["ownership"]["native"].pop(spec.engine)),
                ("foreign-dependency", lambda item: item["ownership"]["native"][spec.engine].__setitem__("needed", ["libpcre2.so"])),
                ("foreign-exports", lambda item: item["ownership"]["native"][spec.engine].__setitem__("defined_exports", ["regexec"])),
                ("empty-dynamic-symbols", lambda item: item["ownership"]["native"][spec.engine].__setitem__("undefined_symbol_count", 0)),
                ("stripped-dynamic-symbols", lambda item: item["ownership"]["native"][spec.engine].__setitem__("undefined_symbol_count", expected_undefined_count(spec, spec.engine) - 1)),
                ("added-dynamic-symbols", lambda item: item["ownership"]["native"][spec.engine].__setitem__("undefined_symbol_count", expected_undefined_count(spec, spec.engine) + 1)),
                ("foreign-engine-owned-reference", lambda item: item["ownership"]["native"][spec.engine].__setitem__("owned_engine_references", ["regexec"])),
            ]
            if spec.name in ("rust", "zig"):
                poisons.extend([
                    ("missing-bridge-owned-reference", lambda item: item["ownership"]["native"][spec.bridge]["owned_engine_references"].pop()),
                    ("foreign-bridge-owned-reference", lambda item: item["ownership"]["native"][spec.bridge]["owned_engine_references"].__setitem__(0, "regexec")),
                    ("duplicate-bridge-owned-reference", lambda item: item["ownership"]["native"][spec.bridge]["owned_engine_references"].append(item["ownership"]["native"][spec.bridge]["owned_engine_references"][0])),
                    ("misordered-bridge-owned-references", lambda item: item["ownership"]["native"][spec.bridge]["owned_engine_references"].reverse()),
                ])
            for title, change in poisons:
                broken = copy.deepcopy(result)
                change(broken)
                reject(name + "-" + title,
                       lambda broken=broken: validate_ownership_result(broken, spec))
            for other, other_spec in FAMILY_SPECS.items():
                if other != name:
                    reject(name + "-reject-" + other + "-family",
                           lambda other_spec=other_spec:
                           validate_ownership_result(synthetic_result(other_spec), spec))
            reject(name + "-truncated-stdout", lambda raw=raw: decode_audit(raw[:-1]))
            reject(name + "-suffix-stdout", lambda raw=raw: decode_audit(raw + b"{}\n"))
            reject(name + "-duplicate-stdout", lambda: decode_audit(
                b'{"oracle":"a","oracle":"b"}\n',
            ))
        accept("literal-evidence-path-matches-retained-owned-directory",
               require_directory_identity((101, 701), (101, 701),
                                          (101, 701)) is None)
        for title, retained, expected, literal in (
            ("renamed-literal-evidence-directory", (101, 701), (101, 701), (101, 702)),
            ("replaced-literal-evidence-device", (101, 701), (101, 701), (102, 701)),
            ("replaced-retained-evidence-inode", (101, 702), (101, 701), (101, 702)),
            ("forged-expected-evidence-device", (101, 701), (102, 701), (101, 701)),
            ("truncated-literal-evidence-identity", (101, 701), (101, 701), (101,)),
            ("boolean-literal-evidence-identity", (101, 701), (101, 701), (True, 701)),
            ("negative-literal-evidence-identity", (101, 701), (101, 701), (-1, 701)),
        ):
            reject(title,
                   lambda retained=retained, expected=expected, literal=literal:
                   require_directory_identity(retained, expected, literal))

        for label in ("", "..", "../escape", "/absolute", "a/b", "a--b",
                      "-bad", "bad-", "bad_name", "CAPS", "a" * 65):
            reject("unsafe-label-" + repr(label),
                   lambda label=label: approved_paths("rust", label))
        for family in ("", "re", "_sre", "../zig", "external", "RUST"):
            reject("foreign-family-" + repr(family),
                   lambda family=family: validate_family(family))
        for label, operation in (
            ("read", lambda: builtins.open("synthetic-read")),
            ("write", lambda: os.write(1, b"synthetic")),
            ("import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("worker", lambda: subprocess.Popen(["synthetic"])),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter()),
            ("garbage-collection", lambda: gc.collect()),
        ):
            reject("block-actual-" + label, operation)
        accept("all-side-effects-provably-blocked", all(value > 0 for value in effects.values()))
        accept("all-three-independent-families", set(FAMILY_SPECS) == {"rust", "c", "zig"})
        accept("no-candidate-imports",
               not any(n == "candidates" or n.startswith("candidates.") for n in sys.modules))
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "python": "3.14.6", "frozen_audit_relative": AUDIT_RELATIVE,
        "frozen_audit_sha256": AUDIT_SHA256,
        "frozen_audit_predecessor_relative": AUDIT_PREDECESSOR,
        "frozen_audit_predecessor_sha256": AUDIT_PREDECESSOR_SHA256,
        "frozen_recorder_predecessor_relative": RECORDER_PREDECESSOR,
        "frozen_recorder_predecessor_sha256": RECORDER_PREDECESSOR_SHA256,
        "families": ["rust", "c", "zig"],
        "accepted_control_count": len(accepted), "accepted_controls": accepted,
        "rejected_control_count": len(rejected), "rejected_controls": rejected,
        "blocked_effects": effects,
        "real_candidate_files_read": 0, "real_native_binary_files_read": 0,
        "real_candidate_imported": False, "actual_audit_process_count": 0,
        "evidence_files_created": 0, "hidden_cases_read": 0,
        "performance_files_read": 0, "timing_trials_run": 0,
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "final_holdout_opened": False, "winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--candidate", choices=("rust", "c", "zig"))
    parser.add_argument("--label")
    parser.add_argument("--audit-source-sha256")
    parser.add_argument("--candidate-source-sha256")
    parser.add_argument("--native-engine-sha256")
    parser.add_argument("--native-bridge-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    verify_runtime()
    options = parse_arguments(arguments)
    if options.self_test:
        require(all(getattr(options, name) is None for name in (
            "candidate", "label", "audit_source_sha256",
            "candidate_source_sha256", "native_engine_sha256",
            "native_bridge_sha256",
        )), "synthetic controls cannot authenticate or execute real candidates")
        document = source_self_test()
    else:
        spec = validate_family(options.candidate)
        validate_label(options.label)
        require(validate_digest(options.audit_source_sha256, "frozen V2 audit")
                == AUDIT_SHA256, "pin the exact prospectively frozen V2 ownership audit")
        sources, binaries = dict(spec.sources), dict(spec.binaries)
        require(validate_digest(options.candidate_source_sha256, "owned adapter")
                == sources[spec.adapter], "pin the exact family-owned Python adapter")
        require(validate_digest(options.native_engine_sha256, "owned native engine")
                == binaries[spec.engine], "pin the exact family-owned native engine")
        require(validate_digest(options.native_bridge_sha256, "owned native bridge")
                == binaries[spec.bridge], "pin the exact family-owned native bridge")
        document = record_audit(spec, options.label)
    sys.stdout.buffer.write(canonical(document))
    sys.stdout.buffer.flush()
    return 0 if document.get("status") == "PASS" else 1


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RecorderError, OSError, subprocess.SubprocessError) as error:
        print("frozen independent ownership audit recording failed closed: "
              + str(error), file=sys.stderr)
        raise SystemExit(1) from error
