#!/usr/bin/env python3
"""Independently reproduce the three owned, offline Phase-2 native builds.

``--self-test`` is synthetic and has no filesystem, compiler, subprocess,
clock, candidate, network, or holdout effects.  ``--build`` is a separately
authorized, explicitly hash-pinned operation.  It never imports a candidate,
loads a native library, runs a matcher, or measures performance.
"""

from __future__ import annotations

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
import tomllib
from typing import Any


ROOT = Path(os.path.abspath(__file__)).parent.parent
SOURCE_RELATIVE = "tools/reproduce_phase2_native_builds_v1.py"
PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILDS-V1.md"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-independent-native-source-build-v1"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
WORK_PREFIX = "rebar-phase2-native-build-v1-"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PYTHON_INCLUDE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
)
RUST_TOOLCHAIN = (
    "/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu"
)
PINNED_RUSTC = RUST_TOOLCHAIN + "/bin/rustc"
PINNED_CARGO = RUST_TOOLCHAIN + "/bin/cargo"
PINNED_RUST_DRIVER = (
    RUST_TOOLCHAIN + "/lib/librustc_driver-6108105cd7e839cf.so"
)
PINNED_GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_READELF = "/usr/bin/x86_64-linux-gnu-readelf"
ZIG_COMPILER = "/tmp/zig-x86_64-linux-0.16.0/zig"
ZIG_ARCHIVE = "/tmp/rebar-zig-0.16.0-x86_64-linux.tar.xz"

MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_LABEL_BYTES = 48

FAMILIES: dict[str, dict[str, Any]] = {
    "c": {
        "owners": (
            "candidates/vm_candidate.py",
            "candidates/_vm_native.c",
        ),
        "adapter_import": "_vm_native",
        "binaries": {"extension": "_vm_native" + EXTENSION_SUFFIX},
    },
    "rust": {
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
        "adapter_import": "_rust_bridge",
        "binaries": {
            "engine": "_rust_engine.so",
            "bridge": "_rust_bridge" + EXTENSION_SUFFIX,
        },
    },
    "zig": {
        "owners": (
            "candidates/zig_candidate.py",
            "candidates/zig/mini_regex.zig",
            "candidates/zig/py_bridge.c",
        ),
        "adapter_import": "_zig_bridge",
        "binaries": {
            "engine": "_zig_probe.so",
            "bridge": "_zig_bridge" + EXTENSION_SUFFIX,
        },
    },
}

FROZEN_INPUTS: tuple[tuple[str, str, str, int, int | None], ...] = (
    (
        "immutable_objective",
        "GOAL.md",
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "complete_correctness_manifest",
        "oracle/phase1/p0-completeness-v1.json",
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
        MAX_SOURCE_BYTES,
        45_632,
    ),
    (
        "complete_correctness_protocol",
        "oracle/phase1/P0-COMPLETENESS-V1.md",
        "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
        MAX_SOURCE_BYTES,
        10_392,
    ),
    (
        "complete_correctness_verifier",
        "tools/verify_p0_completeness_v1.py",
        "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "pinned_cpython_executable",
        PINNED_PYTHON,
        "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        MAX_BINARY_BYTES,
        32_387_816,
    ),
    (
        "pinned_cpython_header",
        PYTHON_INCLUDE + "/Python.h",
        "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "pinned_cpython_patchlevel",
        PYTHON_INCLUDE + "/patchlevel.h",
        "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "pinned_host_gcc_13",
        PINNED_GCC,
        "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26",
        MAX_BINARY_BYTES,
        1_023_032,
    ),
    (
        "pinned_host_readelf",
        PINNED_READELF,
        "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0",
        MAX_BINARY_BYTES,
        789_280,
    ),
)

RUST_INPUTS: tuple[tuple[str, str, str, int, int | None], ...] = (
    (
        "pinned_rust_1_95_0_rustc",
        PINNED_RUSTC,
        "bff349e72704ff70bc08a234a3847338e797065bbedde5e556808bc87b7bf7c6",
        MAX_BINARY_BYTES,
        644_784,
    ),
    (
        "pinned_rust_1_95_0_cargo",
        PINNED_CARGO,
        "841072d1d92f9e841d9ba5b0814182a0adf064acf4527cd120967b7bc49dcb66",
        MAX_BINARY_BYTES,
        42_185_192,
    ),
    (
        "pinned_rust_1_95_0_compiler_driver",
        PINNED_RUST_DRIVER,
        "ae69468875215df490fde685ec1f1b969743482ba7e0251f4074a222606a5484",
        MAX_BINARY_BYTES,
        153_621_360,
    ),
)

ZIG_INPUTS: tuple[tuple[str, str, str, int, int | None], ...] = (
    (
        "pinned_official_zig_0_16_0_lock",
        "toolchains/zig-0.16.0.lock.json",
        "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd",
        MAX_SOURCE_BYTES,
        628,
    ),
    (
        "pinned_official_zig_0_16_0_archive",
        ZIG_ARCHIVE,
        "70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00",
        MAX_BINARY_BYTES,
        55_478_392,
    ),
    (
        "pinned_official_zig_0_16_0_compiler",
        ZIG_COMPILER,
        "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c",
        MAX_BINARY_BYTES,
        172_641_672,
    ),
)

RUST_ENGINE_EXPORTS = frozenset({
    "rebar_collect_ascii", "rebar_collect_wide", "rebar_compile",
    "rebar_compile_scanner", "rebar_error_copy", "rebar_error_include",
    "rebar_error_len", "rebar_error_pos", "rebar_flags", "rebar_free",
    "rebar_groups", "rebar_match", "rebar_match_ascii", "rebar_match_wide",
    "rebar_name_copy", "rebar_name_count", "rebar_name_group",
    "rebar_name_len",
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
    "popen", "posix_spawn", "regcomp", "regexec", "regfree", "system",
    "PyRun_AnyFile", "PyRun_SimpleString", "PyRun_String",
    "Py_CompileString", "PyEval_EvalCode",
})
FORBIDDEN_NATIVE_PREFIXES = (
    "hs_", "onig_", "pcre2_", "pcre_", "re2_", "regex_", "sre_",
    "PyInit__sre", "PyRun_", "PyEval_Eval", "Py_CompileString",
)
FORBIDDEN_MODULES = frozenset({
    "re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
    "hyperscan", "sre_compile", "sre_constants", "sre_parse",
})
ALLOWED_SYSTEM_LIBRARIES = frozenset({
    "libc.so.6", "libm.so.6", "libgcc_s.so.1", "ld-linux-x86-64.so.2",
})
ALLOWED_BRIDGE_IMPORTS = frozenset({"copyreg", "functools", "inspect"})


class BuildError(Exception):
    """A frozen input, independent build, or native output failed closed."""


class SourceOnlyError(BuildError):
    """A synthetic-only control attempted a real external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise BuildError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise BuildError("a complete finite canonical JSON record is required") from error


def valid_digest(value: Any) -> bool:
    return (
        type(value) is str and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def checked_digest(value: Any, description: str) -> str:
    require(valid_digest(value), "an exact lowercase SHA-256 is required: " + description)
    return value


def checked_family(value: Any) -> str:
    require(type(value) is str and value in FAMILIES,
            "select exactly one independent C, Rust, or Zig family")
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512,
            "a bounded, repository-relative source path is mandatory")
    require("\\" not in value and "\x00" not in value and not value.startswith("/"),
            "reject absolute paths, NULs, and alternate path separators")
    components = value.split("/")
    require(all(part not in ("", ".", "..") for part in components),
            "reject source-path traversal and empty components")
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL_BYTES,
            "supply one short, unique, non-overwriting build label")
    require(value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(ch in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in value)
            and "--" not in value and not value.endswith("-"),
            "a build label must contain only lowercase letters, digits, and single hyphens")
    return value


def checked_source_pins(family: Any, values: Any) -> dict[str, str]:
    name = checked_family(family)
    expected = FAMILIES[name]["owners"]
    require(type(values) is list and len(values) == len(expected),
            "pin every independently owned source exactly once: " + name)
    result: dict[str, str] = {}
    for value in values:
        require(type(value) is str and value.count("=") == 1,
                "an owned source pin must be exactly RELATIVE/PATH=SHA256")
        path, digest = value.split("=", 1)
        checked_relative(path)
        require(path in expected and path not in result,
                "reject missing, duplicated, cross-family, or foreign source owners")
        result[path] = checked_digest(digest, path)
    require(set(result) == set(expected),
            "the complete independent native source closure was not pinned")
    return dict(sorted(result.items()))


def unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject duplicate and non-string JSON keys")
        result[key] = value
    return result


def reject_json_constant(value: str) -> Any:
    raise BuildError("reject non-finite JSON values: " + value)


def decode_json(raw: Any, *, canonical_required: bool) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
            "a complete bounded JSON source is required")
    try:
        document = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique_json_pairs,
            parse_constant=reject_json_constant,
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise BuildError("a complete, duplicate-key-free JSON source is required") from error
    require(type(document) is dict, "a top-level JSON object is mandatory")
    if canonical_required:
        require(canonical(document) == raw,
                "a signed document changed its exact canonical encoding")
    return document


def authenticate_file(
    path: Path, *, expected: str | None, maximum: int,
    exact_size: int | None = None, capture: bool = False,
) -> tuple[dict[str, Any], bytes | None]:
    require(isinstance(path, Path) and path.is_absolute(),
            "authenticate only one absolute, bounded regular file")
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "reject an invalid authenticated byte limit")
    require(type(capture) is bool, "reject a forged source capture request")
    if exact_size is not None:
        require(type(exact_size) is int and 0 < exact_size <= maximum,
                "reject an invalid exact source or compiler byte count")
    descriptor = os.open(
        str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum,
                "an authenticated owner is not a bounded regular file")
        require(exact_size is None or before.st_size == exact_size,
                "an authenticated owner has a different exact byte count")
        digest = hashlib.sha256()
        kept = bytearray() if capture else None
        actual = 0
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            actual += len(block)
            require(actual <= maximum,
                    "an authenticated owner grew during its complete read")
            digest.update(block)
            if kept is not None:
                kept.extend(block)
        after = os.fstat(descriptor)
        require(
            actual == before.st_size == after.st_size
            and (before.st_dev, before.st_ino, before.st_mtime_ns,
                 before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_mtime_ns,
                after.st_ctime_ns),
            "an authenticated owner changed during its complete no-follow read",
        )
        visible = os.lstat(str(path))
        require(stat.S_ISREG(visible.st_mode)
                and (visible.st_dev, visible.st_ino, visible.st_size)
                == (after.st_dev, after.st_ino, after.st_size),
                "an authenticated owner path was replaced or redirected")
        observed = digest.hexdigest()
        if expected is not None:
            require(observed == checked_digest(expected, str(path)),
                    "an exact frozen owner or toolchain changed: " + str(path))
        return {
            "path": str(path), "sha256": observed,
            "size_bytes": actual, "device": after.st_dev, "inode": after.st_ino,
        }, bytes(kept) if kept is not None else None
    finally:
        os.close(descriptor)


def authenticate_specification(
    specification: tuple[str, str, str, int, int | None],
    *, capture: bool = False,
) -> tuple[str, dict[str, Any], bytes | None]:
    name, location, digest, maximum, exact_size = specification
    require(type(name) is str and bool(name), "an authenticated input name is missing")
    checked_digest(digest, name)
    path = Path(location) if location.startswith("/") else ROOT / checked_relative(location)
    result, raw = authenticate_file(
        path, expected=digest, maximum=maximum,
        exact_size=exact_size, capture=capture,
    )
    return name, result, raw


def validate_cargo_closure(manifest_bytes: Any, lock_bytes: Any) -> dict[str, Any]:
    require(type(manifest_bytes) is bytes and 0 < len(manifest_bytes) <= MAX_SOURCE_BYTES
            and type(lock_bytes) is bytes and 0 < len(lock_bytes) <= MAX_SOURCE_BYTES,
            "both complete owned Cargo inputs are mandatory")
    try:
        manifest = tomllib.loads(manifest_bytes.decode("utf-8"))
        lock = tomllib.loads(lock_bytes.decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as error:
        raise BuildError("an exact dependency-free Rust Cargo closure is required") from error
    require(set(manifest) == {"package", "lib", "profile"},
            "reject external packages, registries, workspaces, build scripts, and patches")
    require(manifest["package"] == {
        "name": "rebar-rust-continuation", "version": "0.1.0",
        "edition": "2024", "rust-version": "1.85", "publish": False,
    }, "the exact unpublished independently owned Rust package changed")
    require(manifest["lib"] == {"crate-type": ["cdylib"]},
            "the Rust engine must be one independently owned native cdylib")
    require(manifest["profile"] == {"release": {
        "opt-level": 3, "lto": True, "codegen-units": 1, "panic": "abort",
    }}, "the exact independently reproducible Rust release profile changed")
    require(lock == {"version": 4, "package": [
        {"name": "rebar-rust-continuation", "version": "0.1.0"},
    ]}, "the Rust lockfile contains a foreign package, registry, or build hook")
    return {
        "package": "rebar-rust-continuation", "package_count": 1,
        "external_package_count": 0, "registry_count": 0,
        "build_script_count": 0, "locked": True, "offline": True,
    }


def native_tokens(raw: Any) -> list[tuple[str, str]]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "a complete bounded native source is required")
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise BuildError("native owner source must be valid UTF-8") from error
    tokens: list[tuple[str, str]] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if text.startswith("//", index):
            end = text.find("\n", index + 2)
            index = len(text) if end < 0 else end + 1
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            require(end >= 0, "reject an unterminated native source comment")
            index = end + 2
            continue
        if (char == "'" and index + 1 < len(text)
                and (text[index + 1] == "_" or text[index + 1].isalpha())):
            lifetime_end = index + 2
            while lifetime_end < len(text) and (
                text[lifetime_end] == "_" or text[lifetime_end].isalnum()
            ):
                lifetime_end += 1
            if lifetime_end >= len(text) or text[lifetime_end] != "'":
                tokens.append(("punctuation", char))
                index += 1
                continue
        if char in "\"'":
            quote, start = char, index
            index += 1
            while index < len(text) and text[index] != quote:
                if text[index] == "\\":
                    index += 1
                index += 1
            require(index < len(text), "reject an unterminated native source string")
            tokens.append(("string", text[start + 1:index]))
            index += 1
            continue
        if char == "_" or char.isalpha():
            start = index
            index += 1
            while index < len(text) and (
                text[index] == "_" or text[index].isalnum()
            ):
                index += 1
            tokens.append(("identifier", text[start:index]))
            continue
        tokens.append(("punctuation", char))
        index += 1
    return tokens


def audit_native_source(raw: bytes, *, family: str, location: str) -> dict[str, Any]:
    checked_family(family)
    checked_relative(location)
    tokens = native_tokens(raw)
    identifiers = {value for kind, value in tokens if kind == "identifier"}
    for name in identifiers:
        require(name not in FORBIDDEN_NATIVE_NAMES
                and not any(name.startswith(prefix)
                            for prefix in FORBIDDEN_NATIVE_PREFIXES),
                "a native source delegates to an external matcher or process: " + name)
    import_calls: list[str] = []
    for index, (kind, value) in enumerate(tokens):
        if (kind == "identifier" and value == "import"
                and index > 0 and tokens[index - 1] == ("punctuation", "@")):
            require(index + 2 < len(tokens)
                    and tokens[index + 1] == ("punctuation", "(")
                    and tokens[index + 2][0] == "string",
                    "reject a computed Zig compiler import")
            imported = tokens[index + 2][1]
            require(imported not in FORBIDDEN_MODULES,
                    "a native source imports a forbidden regex engine: " + imported)
        if kind == "identifier" and value == "PyImport_ImportModule":
            require(index + 3 < len(tokens)
                    and tokens[index + 1] == ("punctuation", "(")
                    and tokens[index + 2][0] == "string",
                    "reject a computed or nonliteral native Python import")
            imported = tokens[index + 2][1]
            require(family == "rust" and location == "candidates/rust/py_bridge.c"
                    and imported in ALLOWED_BRIDGE_IMPORTS,
                    "reject a native cross-family or standard-regex import")
            import_calls.append(imported)
    required = {
        "candidates/_vm_native.c": "PyInit__vm_native",
        "candidates/rust/py_bridge.c": "PyInit__rust_bridge",
        "candidates/rust/src/lib.rs": "rebar_compile",
        "candidates/zig/mini_regex.zig": "rebar_zig_compile",
        "candidates/zig/py_bridge.c": "PyInit__zig_bridge",
    }.get(location)
    if required is not None:
        require(required in identifiers,
                "an independently owned native entry point is missing: " + required)
    return {
        "path": location, "native_identifier_count": len(identifiers),
        "native_literal_imports": sorted(import_calls),
        "external_regex_dependency_count": 0,
    }


def audit_python_source(raw: Any, *, family: str, location: str) -> dict[str, Any]:
    checked_family(family)
    checked_relative(location)
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "a complete independently owned Python adapter is required")
    try:
        source = raw.decode("utf-8")
        document = ast.parse(source, filename=location, mode="exec")
    except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
        raise BuildError("an independently owned candidate adapter cannot be parsed") from error
    imports: set[str] = set()
    own_native = FAMILIES[family]["adapter_import"]
    saw_native = False
    for node in ast.walk(document):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                require(root not in FORBIDDEN_MODULES,
                        "a candidate adapter imports a standard or external regex engine")
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".", 1)[0]
            require(root not in FORBIDDEN_MODULES,
                    "a candidate adapter imports a standard or external regex engine")
            imports.add(module)
            if module == "candidates":
                for alias in node.names:
                    require(alias.name == own_native,
                            "a candidate delegates to another family's native engine")
                    saw_native = True
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                require(func.id not in {"__import__", "eval", "exec"},
                        "a candidate adapter contains an uninspectable dynamic import")
            elif isinstance(func, ast.Attribute):
                if isinstance(func.value, ast.Name):
                    require((func.value.id, func.attr) not in {
                        ("importlib", "import_module"),
                        ("importlib", "__import__"),
                        ("os", "system"), ("os", "popen"),
                        ("subprocess", "run"), ("subprocess", "Popen"),
                    }, "a candidate adapter dynamically imports or runs another engine")
                if func.attr == "find_library":
                    raise BuildError("a candidate resolves an unpinned native matcher")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            require(node.value != "__import__",
                    "a candidate adapter conceals the dynamic Python importer")
    require(saw_native,
            "an independently owned adapter does not import its exact own native bridge")
    if family == "zig":
        require("_zig_probe.so" in source,
                "the Zig adapter does not identify its exact owned native engine")
    return {
        "path": location, "imports": sorted(imports),
        "own_native_bridge": own_native,
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
    }


def checked_workdir(value: Any) -> str:
    require(type(value) is str and value.startswith("/tmp/" + WORK_PREFIX),
            "use only a fresh, family-specific private temporary build root")
    require("\x00" not in value and "\\" not in value
            and value == value.rstrip("/"),
            "reject an unsafe private build directory")
    parts = value.split("/")
    require(all(part not in (".", "..", "") for part in parts[1:])
            and len(parts) == 3,
            "reject broad, nested, redirected, or traversing build directories")
    return value


def phase_paths(workdir: str, family: str, phase: str) -> dict[str, Path]:
    checked_workdir(workdir)
    family = checked_family(family)
    require(phase in ("reference-a", "reference-b"),
            "exactly two fresh, independent source-build phases are mandatory")
    base = Path(workdir) / phase
    source = base / "source"
    native = base / "native"
    return {
        "base": base, "source": source, "native": native,
        "target": base / "target", "cargo_home": base / "cargo-home",
        "temporary": base / "temporary",
        "local_cache": base / "zig-local-cache",
        "global_cache": base / "zig-global-cache",
        "rust_manifest": source / "candidates/rust/Cargo.toml",
        "cargo_engine": base / "target/release/librebar_rust_continuation.so",
        **{
            "binary_" + kind: native / name
            for kind, name in FAMILIES[family]["binaries"].items()
        },
    }


def reproducible_prefix_flags(workdir: str, family: str) -> tuple[list[str], str]:
    cflags: list[str] = []
    rustflags: list[str] = []
    for phase in ("reference-a", "reference-b"):
        source = str(phase_paths(workdir, family, phase)["source"])
        cflags.append("-ffile-prefix-map=" + source + "=/rebar-phase2-owned-source")
        rustflags.append(
            "--remap-path-prefix=" + source + "=/rebar-phase2-owned-source"
        )
    if family == "rust":
        rustflags.append("-Clink-arg=-Wl,-soname,_rust_engine.so")
    return cflags, " ".join(rustflags)


def build_environment(workdir: str, family: str, phase: str) -> dict[str, str]:
    paths = phase_paths(workdir, family, phase)
    _, rustflags = reproducible_prefix_flags(workdir, family)
    env = {
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
        "SOURCE_DATE_EPOCH": "1",
        "TMPDIR": str(paths["temporary"]),
    }
    if family == "rust":
        env.update({
            "PATH": RUST_TOOLCHAIN + "/bin:/usr/bin:/bin",
            "CARGO_HOME": str(paths["cargo_home"]),
            "CARGO_NET_OFFLINE": "true",
            "CARGO_INCREMENTAL": "0",
            "CARGO_BUILD_JOBS": "1",
            "RUSTC": PINNED_RUSTC,
            "RUSTFLAGS": rustflags,
        })
    if family == "zig":
        env.update({
            "ZIG_GLOBAL_CACHE_DIR": str(paths["global_cache"]),
            "ZIG_LOCAL_CACHE_DIR": str(paths["local_cache"]),
        })
    return env


def planned_commands(workdir: str, family: str, phase: str) -> dict[str, list[str]]:
    paths = phase_paths(workdir, family, phase)
    prefix, _ = reproducible_prefix_flags(workdir, family)
    commands: dict[str, list[str]] = {
        "gcc_version": [PINNED_GCC, "--version"],
        "readelf_version": [PINNED_READELF, "--version"],
    }
    if family == "c":
        commands["build_c_extension"] = [
            PINNED_GCC, "-std=c11", "-O3", "-Wall", "-Wextra", "-Werror",
            "-fPIC", "-shared", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/_vm_native.c"),
            "-o", str(paths["binary_extension"]),
        ]
    elif family == "rust":
        commands["rustc_version"] = [PINNED_RUSTC, "--version", "--verbose"]
        commands["cargo_version"] = [PINNED_CARGO, "--version"]
        commands["build_rust_engine"] = [
            PINNED_CARGO, "build", "--manifest-path",
            str(paths["rust_manifest"]), "--release", "--locked",
            "--offline", "--frozen", "--target-dir", str(paths["target"]),
        ]
        commands["build_rust_bridge"] = [
            PINNED_GCC, "-pthread", "-std=c11", "-shared", "-fPIC", "-O3",
            "-Wall", "-Wextra", "-Werror", "-Wl,-z,noexecstack",
            "-Wl,--exclude-libs,ALL", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/rust/py_bridge.c"),
            "-L" + str(paths["native"]), "-l:_rust_engine.so",
            "-Wl,-rpath,$ORIGIN", "-o", str(paths["binary_bridge"]),
        ]
    else:
        commands["zig_version"] = [ZIG_COMPILER, "version"]
        commands["build_zig_engine"] = [
            ZIG_COMPILER, "build-lib",
            str(paths["source"] / "candidates/zig/mini_regex.zig"),
            "-dynamic", "-lc", "-O", "ReleaseFast",
            "-fallow-shlib-undefined", "-fsoname=_zig_probe.so",
            "--cache-dir", str(paths["local_cache"]),
            "--global-cache-dir", str(paths["global_cache"]),
            "-femit-bin=" + str(paths["binary_engine"]),
        ]
        commands["build_zig_bridge"] = [
            PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3",
            "-Wall", "-Wextra", "-Werror", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/zig/py_bridge.c"),
            "-L" + str(paths["native"]), "-l:_zig_probe.so",
            "-Wl,-rpath,$ORIGIN", "-o", str(paths["binary_bridge"]),
        ]
    for kind, binary in FAMILIES[family]["binaries"].items():
        path = paths["binary_" + kind]
        commands[kind + "_dynamic"] = [
            PINNED_READELF, "--dynamic", "--wide", str(path),
        ]
        commands[kind + "_symbols"] = [
            PINNED_READELF, "--dyn-syms", "--wide", str(path),
        ]
    return commands


def checked_command(
    name: Any, argv: Any, workdir: str, family: str, phase: str,
) -> list[str]:
    commands = planned_commands(workdir, family, phase)
    require(type(name) is str and name in commands
            and type(argv) is list
            and all(type(item) is str and "\x00" not in item for item in argv)
            and argv == commands[name],
            "reject an unpinned, shell-based, networked, or modified build command")
    require(argv[0] in {PINNED_GCC, PINNED_READELF, PINNED_RUSTC,
                         PINNED_CARGO, ZIG_COMPILER},
            "only an exactly authenticated compiler or ELF inspector may execute")
    return list(argv)


def sanitized(value: str, workdir: str) -> str:
    return value.replace(checked_workdir(workdir), "<FRESH_PRIVATE_TMP>")


def parse_elf_dynamic(raw: Any) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "complete bounded readelf dynamic output is mandatory")
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise BuildError("readelf dynamic output is not valid UTF-8") from error
    found: dict[str, list[str]] = {
        "needed": [], "runpath": [], "rpath": [], "soname": [],
    }
    markers = {
        "(NEEDED)": "needed", "(RUNPATH)": "runpath",
        "(RPATH)": "rpath", "(SONAME)": "soname",
    }
    for line in text.splitlines():
        for marker, key in markers.items():
            if marker in line:
                left = line.find("[")
                right = line.find("]", left + 1)
                require(left >= 0 and right > left,
                        "a native dynamic dependency has no exact bounded value")
                value = line[left + 1:right]
                require(value and "\x00" not in value,
                        "reject an empty or malformed native dependency")
                found[key].append(value)
    for key, values in found.items():
        require(len(values) == len(set(values)),
                "reject duplicated or disguised native dynamic dependencies: " + key)
    return found


def parse_elf_symbols(raw: Any) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "complete bounded readelf dynamic-symbol output is mandatory")
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise BuildError("readelf symbol output is not valid UTF-8") from error
    exports: set[str] = set()
    undefined: set[str] = set()
    for line in text.splitlines():
        columns = line.split()
        if len(columns) < 8 or not columns[0].rstrip(":").isdigit():
            continue
        name = columns[-1].split("@", 1)[0]
        if not name:
            continue
        index = columns[6]
        binding = columns[4]
        if index == "UND":
            undefined.add(name)
        elif binding in {"GLOBAL", "WEAK"}:
            exports.add(name)
    require(bool(exports), "a native binary exposes no genuine dynamic entry point")
    all_names = exports | undefined
    for name in all_names:
        require(name not in FORBIDDEN_NATIVE_NAMES
                and not any(name.startswith(prefix)
                            for prefix in FORBIDDEN_NATIVE_PREFIXES),
                "the native binary delegates to a foreign matcher or process: " + name)
    return {"exports": sorted(exports), "undefined": sorted(undefined)}


def validate_elf(
    family: str, kind: str, dynamic: dict[str, Any], symbols: dict[str, Any],
) -> dict[str, Any]:
    family = checked_family(family)
    require(kind in FAMILIES[family]["binaries"],
            "reject a substituted native binary role")
    needed = set(dynamic["needed"])
    require(not dynamic["rpath"], "a native binary contains an unsafe RPATH")
    exports = set(symbols["exports"])
    undefined = set(symbols["undefined"])
    if family == "c":
        require(kind == "extension" and "PyInit__vm_native" in exports,
                "the C extension lacks its genuine CPython entry point")
        require(needed.issubset(ALLOWED_SYSTEM_LIBRARIES)
                and not dynamic["runpath"],
                "the C extension delegates to another native matcher")
        required = {"PyInit__vm_native"}
    elif kind == "engine":
        expected_name = FAMILIES[family]["binaries"]["engine"]
        required = RUST_ENGINE_EXPORTS if family == "rust" else ZIG_ENGINE_EXPORTS
        require(dynamic["soname"] == [expected_name],
                "the owned native engine SONAME is missing or substituted")
        require(not dynamic["runpath"] and needed.issubset(ALLOWED_SYSTEM_LIBRARIES),
                "the native engine loads an external or sibling matching engine")
        require(set(required).issubset(exports),
                "a genuinely owned native matching entry point is missing")
    else:
        expected_name = FAMILIES[family]["binaries"]["engine"]
        expected_init = "PyInit__" + family + "_bridge"
        require(expected_init in exports,
                "the owned bridge lacks its exact CPython 3.14 entry point")
        require(expected_name in needed
                and needed.issubset(ALLOWED_SYSTEM_LIBRARIES | {expected_name}),
                "the bridge does not exclusively link to its own native engine")
        require(dynamic["runpath"] == ["$ORIGIN"],
                "the bridge must resolve only its adjacent owned engine")
        engine_prefix = "rebar_" if family == "rust" else "rebar_zig_"
        require(any(name.startswith(engine_prefix) for name in undefined),
                "the bridge does not call its actual own matching engine")
        forbidden_sibling = "rebar_zig_" if family == "rust" else "rebar_compile"
        require(not any(name.startswith(forbidden_sibling) for name in undefined),
                "the bridge calls another candidate's matching engine")
        required = {expected_init}
    return {
        "role": kind, "needed": sorted(needed),
        "runpath": list(dynamic["runpath"]),
        "soname": list(dynamic["soname"]),
        "required_exports": sorted(required),
        "exports": list(symbols["exports"]),
        "undefined": list(symbols["undefined"]),
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
    }


def validate_phase1_manifest(raw: bytes) -> dict[str, Any]:
    value = decode_json(raw, canonical_required=True)
    require(value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and value.get("version") == 1,
            "the independently completed Python correctness oracle was substituted")
    suites = value.get("suites")
    phase = value.get("phase_gate")
    guards = value.get("audit_boundaries")
    require(type(suites) is list and len(suites) == 13
            and sum(item.get("case_execution_count", 0) for item in suites) == 31_237
            and all(item.get("baseline", {}).get("status") == "PASS" for item in suites),
            "all 31,237 independently recorded Python cases must pass first")
    require(type(phase) is dict and phase.get("status") == "PASS"
            and phase.get("all_obligations_mapped") is True
            and phase.get("blockers") == []
            and phase.get("final_holdout_authorized") is False,
            "reject incomplete correctness or unauthorized holdout evidence")
    require(type(guards) is dict and guards.get("hidden_cases_read") == 0
            and guards.get("final_cases_read") == 0
            and guards.get("timing_trials_run") == 0,
            "the build may not read a holdout or inherit performance measurements")
    return {
        "status": "PASS", "suite_count": 13,
        "case_execution_count": 31_237,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "final_holdout_authorized": False,
    }


def validate_zig_lock(raw: bytes) -> dict[str, Any]:
    lock = decode_json(raw, canonical_required=False)
    expected = {
        "schema": "rebar-official-language-toolchain-v1",
        "language": "Zig", "version": "0.16.0",
        "release_channel": "stable", "platform": "x86_64-linux",
        "official_release_index": "https://ziglang.org/download/index.json",
        "archive_url": (
            "https://ziglang.org/download/0.16.0/zig-x86_64-linux-0.16.0.tar.xz"
        ),
        "archive_sha256": (
            "70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00"
        ),
        "archive_bytes": 55_478_392,
        "archive_root": "zig-x86_64-linux-0.16.0",
        "compiler_relative_path": "zig-x86_64-linux-0.16.0/zig",
        "compiler_sha256": (
            "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c"
        ),
    }
    require(lock == expected,
            "the exact offline, official Zig 0.16.0 release lock changed")
    return {
        "language": "Zig", "version": "0.16.0",
        "archive_sha256": lock["archive_sha256"],
        "compiler_sha256": lock["compiler_sha256"],
        "network_requests": 0,
    }


def run_process(
    name: str, workdir: str, family: str, phase: str,
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    require(type(steps) is list, "retain every actual compiler and inspector process")
    command = planned_commands(workdir, family, phase)
    require(name in command, "an independently frozen compiler command is missing")
    argv = checked_command(name, command[name], workdir, family, phase)
    environment = build_environment(workdir, family, phase)
    empty = hashlib.sha256(b"").hexdigest()
    item: dict[str, Any] = {
        "name": name,
        "argv": [sanitized(value, workdir) for value in argv],
        "environment": {
            key: sanitized(value, workdir)
            for key, value in sorted(environment.items())
        },
        "shell": False, "pid": None, "exit_status": None,
        "stdout_base64": "", "stderr_base64": "",
        "stdout_sha256": empty, "stderr_sha256": empty,
        "stdout_bytes": 0, "stderr_bytes": 0,
    }
    steps.append(item)
    try:
        process = subprocess.Popen(
            argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=environment,
            cwd=str(phase_paths(workdir, family, phase)["base"]),
            shell=False,
        )
        item["pid"] = process.pid
        try:
            stdout, stderr = process.communicate(timeout=900)
        except subprocess.TimeoutExpired as error:
            process.kill()
            stdout, stderr = process.communicate()
            item["exit_status"] = process.returncode
            raise BuildError("a bounded owned compiler process exceeded its limit") from error
        item["exit_status"] = process.returncode
        require(type(stdout) is bytes and type(stderr) is bytes
                and len(stdout) <= MAX_PROCESS_BYTES
                and len(stderr) <= MAX_PROCESS_BYTES,
                "retain complete bounded compiler output and errors")
        item["stdout_base64"] = base64.b64encode(stdout).decode("ascii")
        item["stderr_base64"] = base64.b64encode(stderr).decode("ascii")
        item["stdout_sha256"] = hashlib.sha256(stdout).hexdigest()
        item["stderr_sha256"] = hashlib.sha256(stderr).hexdigest()
        item["stdout_bytes"] = len(stdout)
        item["stderr_bytes"] = len(stderr)
        require(process.returncode == 0,
                "an exact owned compiler or ELF inspector failed: " + name)
        return {"record": item, "stdout": stdout, "stderr": stderr}
    except (OSError, subprocess.SubprocessError) as error:
        item["error_type"] = type(error).__name__
        item["error_message"] = str(error)
        raise BuildError("an authenticated compiler process could not complete") from error


def validate_version(name: str, raw: bytes) -> None:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "record the complete pinned compiler version")
    if name == "zig_version":
        require(raw == b"0.16.0\n",
                "the exact official stable Zig 0.16.0 compiler was substituted")
    elif name == "cargo_version":
        require(raw.startswith(b"cargo 1.95.0 (f2d3ce0bd"),
                "PATH cargo or a non-1.95.0 Rust toolchain was substituted")
    elif name == "rustc_version":
        require(raw.startswith(b"rustc 1.95.0 (59807616e")
                and b"release: 1.95.0\n" in raw
                and b"commit-hash: 59807616e1fa2540724bfbac14d7976d7e4a3860\n" in raw
                and b"host: x86_64-unknown-linux-gnu\n" in raw,
                "the exact official Rust 1.95.0 compiler identity changed")
    elif name == "gcc_version":
        require(b"13." in raw.split(b"\n", 1)[0],
                "the pinned host GCC 13 version changed")
    elif name == "readelf_version":
        require(b"readelf" in raw.split(b"\n", 1)[0].lower(),
                "the pinned ELF inspector version changed")
    else:
        raise BuildError("an unapproved compiler-version command was run")


def mkdir_private(path: Path) -> None:
    require(isinstance(path, Path) and path.is_absolute(),
            "create only an absolute fresh private build directory")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    result = os.lstat(str(path))
    require(stat.S_ISDIR(result.st_mode) and not stat.S_ISLNK(result.st_mode),
            "a private build directory was redirected")


def write_fresh(path: Path, content: bytes, *, synchronize: bool) -> dict[str, Any]:
    require(isinstance(path, Path) and path.is_absolute()
            and type(content) is bytes and 0 < len(content) <= MAX_ARCHIVE_BYTES,
            "write only a complete, bounded, specifically approved fresh file")
    descriptor = os.open(
        str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    calls = 0
    written = 0
    try:
        while written < len(content):
            result = os.write(descriptor, content[written:])
            require(type(result) is int and result > 0,
                    "a fresh evidence or source write stopped prematurely")
            written += result
            calls += 1
        require(written == len(content), "a fresh source or report was truncated")
        if synchronize:
            os.fsync(descriptor)
    finally:
        os.close(descriptor)
    observed, _ = authenticate_file(
        path, expected=hashlib.sha256(content).hexdigest(),
        maximum=MAX_ARCHIVE_BYTES, exact_size=len(content),
    )
    return {
        "path": str(path), "sha256": observed["sha256"],
        "bytes": len(content), "write_calls": calls,
        "exclusive_creation": True,
        "same_inode_readback_verified": True,
        "file_fsync_completed": synchronize,
    }


def snapshot_owned_sources(
    family: str, pins: dict[str, str],
) -> tuple[dict[str, dict[str, Any]], dict[str, bytes]]:
    checked_family(family)
    require(set(pins) == set(FAMILIES[family]["owners"]),
            "reject an incomplete or cross-family actual source snapshot")
    observed: dict[str, dict[str, Any]] = {}
    source: dict[str, bytes] = {}
    for relative, digest in sorted(pins.items()):
        owner, raw = authenticate_file(
            ROOT / checked_relative(relative), expected=digest,
            maximum=MAX_SOURCE_BYTES, capture=True,
        )
        require(raw is not None, "an actual owned source snapshot is missing")
        observed[relative] = owner
        source[relative] = raw
    return observed, source


def audit_owned_sources(family: str, sources: dict[str, bytes]) -> dict[str, Any]:
    require(set(sources) == set(FAMILIES[family]["owners"]),
            "the complete independent family source graph is mandatory")
    audits: list[dict[str, Any]] = []
    for relative, raw in sorted(sources.items()):
        if relative.endswith(".py"):
            audits.append(audit_python_source(raw, family=family, location=relative))
        elif relative.endswith((".c", ".rs", ".zig")):
            audits.append(audit_native_source(raw, family=family, location=relative))
    cargo = None
    if family == "rust":
        cargo = validate_cargo_closure(
            sources["candidates/rust/Cargo.toml"],
            sources["candidates/rust/Cargo.lock"],
        )
    return {
        "source_audits": audits,
        "source_owner_count": len(sources),
        "external_regex_package_count": 0,
        "cross_family_dependency_count": 0,
        "cargo_dependency_closure": cargo,
    }


def copy_snapshot(
    workdir: str, family: str, phase: str,
    sources: dict[str, bytes],
) -> dict[str, dict[str, Any]]:
    paths = phase_paths(workdir, family, phase)
    for name in ("base", "source", "native", "temporary"):
        mkdir_private(paths[name])
    if family == "rust":
        mkdir_private(paths["cargo_home"])
    if family == "zig":
        mkdir_private(paths["local_cache"])
        mkdir_private(paths["global_cache"])
    copied: dict[str, dict[str, Any]] = {}
    for relative, content in sorted(sources.items()):
        destination = paths["source"] / checked_relative(relative)
        mkdir_private(destination.parent)
        result = write_fresh(destination, content, synchronize=False)
        result["path"] = sanitized(result["path"], workdir)
        copied[relative] = result
    return copied


def verify_fresh_binary(
    workdir: str, family: str, phase: str, kind: str,
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    paths = phase_paths(workdir, family, phase)
    binary, _ = authenticate_file(
        paths["binary_" + kind], expected=None,
        maximum=MAX_BINARY_BYTES,
    )
    dynamic_result = run_process(kind + "_dynamic", workdir, family, phase, steps)
    symbol_result = run_process(kind + "_symbols", workdir, family, phase, steps)
    dynamic = parse_elf_dynamic(dynamic_result["stdout"])
    symbols = parse_elf_symbols(symbol_result["stdout"])
    audit = validate_elf(family, kind, dynamic, symbols)
    after, _ = authenticate_file(
        paths["binary_" + kind], expected=binary["sha256"],
        maximum=MAX_BINARY_BYTES, exact_size=binary["size_bytes"],
    )
    require((binary["device"], binary["inode"])
            == (after["device"], after["inode"]),
            "a fresh native binary changed during ELF inspection")
    return {
        "family": family, "role": kind,
        "file_name": FAMILIES[family]["binaries"][kind],
        "path": sanitized(binary["path"], workdir),
        "sha256": binary["sha256"], "size_bytes": binary["size_bytes"],
        "elf": audit,
        "prebuilt_binary_read": False,
        "candidate_imported": False,
    }


def exact_build_phase(
    workdir: str, family: str, phase: str,
    sources: dict[str, bytes], steps: list[dict[str, Any]],
) -> dict[str, Any]:
    copied = copy_snapshot(workdir, family, phase, sources)
    paths = phase_paths(workdir, family, phase)
    if family == "c":
        run_process("build_c_extension", workdir, family, phase, steps)
    elif family == "rust":
        run_process("build_rust_engine", workdir, family, phase, steps)
        engine, raw = authenticate_file(
            paths["cargo_engine"], expected=None,
            maximum=MAX_BINARY_BYTES, capture=True,
        )
        require(raw is not None and engine["size_bytes"] == len(raw),
                "Cargo did not produce a complete fresh owned Rust engine")
        write_fresh(paths["binary_engine"], raw, synchronize=False)
        run_process("build_rust_bridge", workdir, family, phase, steps)
    else:
        run_process("build_zig_engine", workdir, family, phase, steps)
        run_process("build_zig_bridge", workdir, family, phase, steps)
    binaries = {
        kind: verify_fresh_binary(workdir, family, phase, kind, steps)
        for kind in FAMILIES[family]["binaries"]
    }
    return {
        "name": phase,
        "fresh_source_directory": sanitized(str(paths["source"]), workdir),
        "fresh_native_directory": sanitized(str(paths["native"]), workdir),
        "copied_source_owners": copied,
        "native_outputs": binaries,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "timing_trials_run": 0,
        "hidden_cases_read": 0,
    }


def verify_reproducible_phases(
    family: str, phases: list[dict[str, Any]],
) -> dict[str, Any]:
    checked_family(family)
    require(type(phases) is list and len(phases) == 2
            and [item.get("name") for item in phases]
            == ["reference-a", "reference-b"],
            "two genuinely independent complete source-build phases are mandatory")
    first, second = phases
    require(first["fresh_source_directory"] != second["fresh_source_directory"]
            and first["fresh_native_directory"] != second["fresh_native_directory"],
            "an existing build directory or compiled candidate was reused")
    owners = set(FAMILIES[family]["owners"])
    require(set(first["copied_source_owners"])
            == set(second["copied_source_owners"]) == owners,
            "the two fresh build phases used different source closures")
    outputs: dict[str, dict[str, Any]] = {}
    for kind, name in FAMILIES[family]["binaries"].items():
        left = first["native_outputs"][kind]
        right = second["native_outputs"][kind]
        require(left["file_name"] == right["file_name"] == name
                and left["sha256"] == right["sha256"]
                and left["size_bytes"] == right["size_bytes"]
                and left["path"] != right["path"]
                and left["elf"] == right["elf"],
                "two independent native builds are not byte-for-byte reproducible")
        outputs[kind] = {
            "file_name": name, "sha256": left["sha256"],
            "size_bytes": left["size_bytes"],
            "reproduced_in_two_fresh_directories": True,
            "elf": left["elf"],
        }
    return {
        "independent_fresh_phase_count": 2,
        "byte_identical": True,
        "native_outputs": outputs,
        "prebuilt_binary_count": 0,
        "native_libraries_loaded": 0,
    }


def evidence_names(family: str, label: str, *, failure: bool) -> tuple[str, str]:
    family = checked_family(family)
    label = checked_label(label)
    base = "native-source-build-v1-" + family + "-" + label
    if failure:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def check_fresh_evidence(family: str, label: str) -> None:
    parent = ROOT / EVIDENCE_RELATIVE
    if parent.exists():
        observed = os.lstat(str(parent))
        require(stat.S_ISDIR(observed.st_mode) and not stat.S_ISLNK(observed.st_mode),
                "the native build evidence directory is unsafe")
    for failure in (False, True):
        for name in evidence_names(family, label, failure=failure):
            target = parent / name
            try:
                os.lstat(str(target))
            except FileNotFoundError:
                continue
            raise BuildError("refusing to overwrite a preserved native build: " + str(target))


def fsync_directory(path: Path) -> dict[str, Any]:
    descriptor = os.open(
        str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISDIR(before.st_mode), "synchronize only the owned report directory")
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino),
                "the published evidence directory was redirected")
        return {"completed": True, "device": after.st_dev, "inode": after.st_ino}
    finally:
        os.close(descriptor)


def publish_report(report: dict[str, Any], family: str, label: str) -> dict[str, Any]:
    failure = report.get("status") != "PASS"
    archive_name, receipt_name = evidence_names(family, label, failure=failure)
    directory = ROOT / EVIDENCE_RELATIVE
    mkdir_private(directory)
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT_BYTES,
            "a full reproducible-build report exceeded its signed byte bound")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(archive) <= MAX_ARCHIVE_BYTES,
            "a reproducible-build report archive exceeded its signed byte bound")
    archive_path = directory / archive_name
    receipt_path = directory / receipt_name
    archive_record = write_fresh(archive_path, archive, synchronize=True)
    archive_sync = fsync_directory(directory)
    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "status": "PASS",
        "build_status": report["status"],
        "family": family, "label": label,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "phase1_manifest_sha256": FROZEN_INPUTS[1][2],
        "archive_relative": EVIDENCE_RELATIVE + "/" + archive_name,
        "archive_sha256": archive_record["sha256"],
        "archive_bytes": archive_record["bytes"],
        "uncompressed_sha256": hashlib.sha256(plain).hexdigest(),
        "uncompressed_bytes": len(plain),
        "archive_publication": archive_record,
        "archive_directory_fsync": archive_sync,
        "owned_source_sha256": report["owned_source_sha256"],
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "candidate_correctness": "NOT MEASURED",
        "winner_selected": False,
        "receipt_self_publication": "NOT CLAIMED",
    }
    receipt_bytes = canonical(receipt)
    require(len(receipt_bytes) <= MAX_SOURCE_BYTES,
            "a complete native-build receipt exceeded its signed byte bound")
    receipt_record = write_fresh(receipt_path, receipt_bytes, synchronize=True)
    receipt_sync = fsync_directory(directory)
    return {
        "status": report["status"], "family": family, "label": label,
        "archive_relative": EVIDENCE_RELATIVE + "/" + archive_name,
        "archive_sha256": archive_record["sha256"],
        "receipt_relative": EVIDENCE_RELATIVE + "/" + receipt_name,
        "receipt_sha256": receipt_record["sha256"],
        "receipt_directory_fsync": receipt_sync,
        "failure_preserved": failure,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def authenticate_build_inputs(
    family: str, *, source_digest: str, protocol_digest: str,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    family = checked_family(family)
    require(sys.executable == PINNED_PYTHON
            and sys.version_info[:3] == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314",
            "invoke the exact frozen CPython 3.14.6 executable and ABI")
    support: dict[str, dict[str, Any]] = {}
    phase1: dict[str, Any] | None = None
    for specification in FROZEN_INPUTS:
        capture = specification[0] in {
            "complete_correctness_manifest", "pinned_cpython_patchlevel",
        }
        name, evidence, raw = authenticate_specification(specification, capture=capture)
        support[name] = evidence
        if name == "complete_correctness_manifest":
            require(raw is not None, "the complete Phase-1 manifest is missing")
            phase1 = validate_phase1_manifest(raw)
        if name == "pinned_cpython_patchlevel":
            require(raw is not None, "the pinned Python patch-level header is missing")
            actual_versions = [
                line.split()
                for line in raw.splitlines()
                if line.split()[:2] == [b"#define", b"PY_VERSION"]
            ]
            require(actual_versions == [[b"#define", b"PY_VERSION", b'"3.14.6"']],
                    "the exact stable CPython 3.14.6 header changed")
    source, _ = authenticate_file(
        ROOT / SOURCE_RELATIVE, expected=checked_digest(source_digest, "build recorder"),
        maximum=MAX_SOURCE_BYTES,
    )
    protocol, _ = authenticate_file(
        ROOT / PROTOCOL_RELATIVE,
        expected=checked_digest(protocol_digest, "build protocol"),
        maximum=MAX_SOURCE_BYTES,
    )
    support["native_build_recorder"] = source
    support["native_build_protocol"] = protocol
    if family == "rust":
        for specification in RUST_INPUTS:
            name, evidence, _ = authenticate_specification(specification)
            support[name] = evidence
    if family == "zig":
        for specification in ZIG_INPUTS:
            name, evidence, raw = authenticate_specification(
                specification, capture=specification[0].endswith("_lock"),
            )
            support[name] = evidence
            if name == "pinned_official_zig_0_16_0_lock":
                require(raw is not None, "the exact official Zig lock was not captured")
                validate_zig_lock(raw)
    require(phase1 is not None,
            "the previously published Python correctness phase is mandatory")
    return support, phase1


def run_build(arguments: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    family = checked_family(arguments["family"])
    label = checked_label(arguments["label"])
    pins = checked_source_pins(family, arguments["owned_source_sha256"])
    support, phase1 = authenticate_build_inputs(
        family, source_digest=arguments["source_sha256"],
        protocol_digest=arguments["protocol_sha256"],
    )
    before, sources = snapshot_owned_sources(family, pins)
    source_audit = audit_owned_sources(family, sources)
    check_fresh_evidence(family, label)
    workdir = tempfile.mkdtemp(prefix=WORK_PREFIX + family + "-", dir="/tmp")
    checked_workdir(workdir)
    report: dict[str, Any] = {
        "schema": SCHEMA, "status": "FAIL", "family": family,
        "label": label, "source_sha256": arguments["source_sha256"],
        "protocol_sha256": arguments["protocol_sha256"],
        "phase1": phase1, "frozen_support_inputs": support,
        "frozen_support_inputs_after": None,
        "owned_source_sha256": pins,
        "owned_source_before": before,
        "owned_source_after": None,
        "source_independence_audit": source_audit,
        "fresh_private_root": sanitized(workdir, workdir),
        "build_phases": [], "processes": [],
        "reproducibility": None,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "reference_processes_started": 0,
        "network_requests": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "winner_selected": False,
        "error": None,
    }
    try:
        phase = "reference-a"
        version_commands = ["gcc_version", "readelf_version"]
        if family == "rust":
            version_commands += ["rustc_version", "cargo_version"]
        elif family == "zig":
            version_commands += ["zig_version"]
        initial = phase_paths(workdir, family, phase)
        mkdir_private(initial["base"])
        mkdir_private(initial["temporary"])
        for name in version_commands:
            result = run_process(name, workdir, family, phase, report["processes"])
            validate_version(name, result["stdout"])
        for phase in ("reference-a", "reference-b"):
            report["build_phases"].append(
                exact_build_phase(workdir, family, phase, sources, report["processes"])
            )
        after, _ = snapshot_owned_sources(family, pins)
        report["owned_source_after"] = after
        for path in pins:
            require(before[path]["sha256"] == after[path]["sha256"]
                    and before[path]["size_bytes"] == after[path]["size_bytes"]
                    and before[path]["device"] == after[path]["device"]
                    and before[path]["inode"] == after[path]["inode"],
                    "a candidate owner changed during its isolated source build")
        support_after, phase1_after = authenticate_build_inputs(
            family, source_digest=arguments["source_sha256"],
            protocol_digest=arguments["protocol_sha256"],
        )
        require(phase1_after == phase1 and set(support_after) == set(support),
                "the frozen Python correctness or compiler closure changed during build")
        for name, original in support.items():
            current = support_after[name]
            require(
                (original["sha256"], original["size_bytes"],
                 original["device"], original["inode"])
                == (current["sha256"], current["size_bytes"],
                    current["device"], current["inode"]),
                "a frozen compiler, header, protocol, or correctness owner changed: "
                + name,
            )
        report["frozen_support_inputs_after"] = support_after
        report["reproducibility"] = verify_reproducible_phases(
            family, report["build_phases"],
        )
        report["status"] = "PASS"
    except Exception as error:
        report["status"] = "FAIL"
        report["error"] = {
            "type": type(error).__name__, "message": str(error),
        }
    result = publish_report(report, family, label)
    return (0 if report["status"] == "PASS" else 1), result


class SyntheticSandbox:
    """Deny and count every real effect during synthetic-only controls."""

    def __init__(self) -> None:
        self.original: list[tuple[Any, str, Any]] = []
        self.counts = {
            "actual_file_reads": 0, "actual_file_writes": 0,
            "actual_processes": 0, "actual_threads": 0,
            "actual_clocks": 0, "actual_network": 0,
            "actual_candidate_imports": 0,
            "actual_native_library_loads": 0,
            "actual_holdout_reads": 0,
            "blocked_file_operations": 0,
            "blocked_process_operations": 0,
            "blocked_thread_operations": 0,
            "blocked_clock_operations": 0,
            "blocked_network_operations": 0,
            "blocked_import_operations": 0,
            "blocked_temporary_operations": 0,
        }

    def install(self, owner: Any, name: str, replacement: Any) -> None:
        self.original.append((owner, name, getattr(owner, name)))
        setattr(owner, name, replacement)

    def deny(self, counter: str, description: str) -> Any:
        def blocked(*arguments: Any, **keywords: Any) -> Any:
            self.counts[counter] += 1
            raise SourceOnlyError(description)
        return blocked

    def __enter__(self) -> SyntheticSandbox:
        file_block = self.deny(
            "blocked_file_operations", "source-only controls cannot access files",
        )
        for owner, name in (
            (builtins, "open"), (io, "open"),
            (os, "open"), (os, "read"), (os, "write"),
            (os, "stat"), (os, "lstat"), (os, "fstat"),
            (os, "listdir"), (os, "scandir"),
            (os, "mkdir"), (os, "makedirs"),
            (os, "unlink"), (os, "remove"), (os, "replace"),
            (os, "rename"), (os, "link"), (os, "fsync"),
            (Path, "open"), (Path, "read_bytes"), (Path, "read_text"),
            (Path, "write_bytes"), (Path, "write_text"),
            (Path, "stat"), (Path, "lstat"), (Path, "exists"),
            (Path, "is_file"), (Path, "is_dir"), (Path, "mkdir"),
            (Path, "iterdir"),
        ):
            if hasattr(owner, name):
                self.install(owner, name, file_block)
        process_block = self.deny(
            "blocked_process_operations",
            "source-only controls cannot run a compiler or subprocess",
        )
        for owner, name in (
            (subprocess, "Popen"), (subprocess, "run"),
            (subprocess, "check_call"), (subprocess, "check_output"),
            (os, "system"), (os, "popen"),
        ):
            if hasattr(owner, name):
                self.install(owner, name, process_block)
        for name in ("mkdtemp", "mkstemp", "TemporaryDirectory"):
            if hasattr(tempfile, name):
                self.install(tempfile, name, self.deny(
                    "blocked_temporary_operations",
                    "source-only controls cannot create a build directory",
                ))
        self.install(threading.Thread, "start", self.deny(
            "blocked_thread_operations", "source-only controls cannot start a thread",
        ))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time", "thread_time",
        ):
            if hasattr(time, name):
                self.install(time, name, self.deny(
                    "blocked_clock_operations",
                    "source-only controls cannot measure time or performance",
                ))
        self.install(socket, "socket", self.deny(
            "blocked_network_operations",
            "source-only controls cannot open a network connection",
        ))
        self.install(importlib, "import_module", self.deny(
            "blocked_import_operations",
            "source-only controls cannot import a candidate or native engine",
        ))
        return self

    def __exit__(self, kind: Any, value: Any, trace: Any) -> bool:
        for owner, name, previous in reversed(self.original):
            setattr(owner, name, previous)
        return False


def synthetic_digest(name: str) -> str:
    return hashlib.sha256(name.encode("ascii")).hexdigest()


def synthetic_pins(family: str) -> list[str]:
    checked_family(family)
    return [path + "=" + synthetic_digest(path)
            for path in FAMILIES[family]["owners"]]


def synthetic_dynamic(
    *, needed: tuple[str, ...] = (), soname: str | None = None,
    runpath: str | None = None, rpath: str | None = None,
) -> bytes:
    lines = ["Dynamic section at offset 0x1 contains 1 entry:"]
    for value in needed:
        lines.append(" 0x1 (NEEDED) Shared library: [" + value + "]")
    if soname is not None:
        lines.append(" 0xe (SONAME) Library soname: [" + soname + "]")
    if runpath is not None:
        lines.append(" 0x1d (RUNPATH) Library runpath: [" + runpath + "]")
    if rpath is not None:
        lines.append(" 0xf (RPATH) Library rpath: [" + rpath + "]")
    return ("\n".join(lines) + "\n").encode("ascii")


def synthetic_symbols(exports: tuple[str, ...], undefined: tuple[str, ...]) -> bytes:
    lines = ["Symbol table '.dynsym' contains entries:"]
    index = 1
    for name in exports:
        lines.append(
            str(index) + ": 0000000000000000 1 FUNC GLOBAL DEFAULT 12 " + name
        )
        index += 1
    for name in undefined:
        lines.append(
            str(index) + ": 0000000000000000 0 FUNC GLOBAL DEFAULT UND " + name
        )
        index += 1
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_arguments(arguments: list[str]) -> dict[str, Any]:
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "supply exact native source-build command arguments")
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    require(bool(arguments) and arguments[0] == "--build",
            "select the synthetic --self-test or explicitly authorized --build")
    result: dict[str, Any] = {"mode": "build", "owned_source_sha256": []}
    mapping = {
        "--family": "family", "--label": "label",
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
    }
    position = 1
    while position < len(arguments):
        option = arguments[position]
        require(position + 1 < len(arguments),
                "an exact native source-build option is missing its value")
        value = arguments[position + 1]
        if option == "--owned-source-sha256":
            result["owned_source_sha256"].append(value)
        else:
            require(option in mapping,
                    "reject an abbreviated, repeated, hidden, or performance option")
            key = mapping[option]
            require(key not in result, "reject a repeated native build authorization")
            result[key] = value
        position += 2
    require(set(result) == {
        "mode", "family", "label", "source_sha256", "protocol_sha256",
        "owned_source_sha256",
    }, "pin the recorder, protocol, label, family, and complete source closure")
    checked_family(result["family"])
    checked_label(result["label"])
    checked_digest(result["source_sha256"], "native build recorder")
    checked_digest(result["protocol_sha256"], "native build protocol")
    checked_source_pins(result["family"], result["owned_source_sha256"])
    return result


def self_test() -> dict[str, Any]:
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "synthetic control names must be individually distinct")
        require(condition, "a required positive native-build control failed: " + name)
        accepted.append(name)

    def reject(name: str, operation: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "synthetic attack names must be individually distinct")
        try:
            operation()
        except (BuildError, TypeError, ValueError, UnicodeError,
                RecursionError, OverflowError, OSError):
            rejected.append(name)
            return
        raise BuildError("an unsafe native-build attack was accepted: " + name)

    with SyntheticSandbox() as guard:
        accept("exact-frozen-python-version", PINNED_PYTHON.endswith("/bin/python3.14"))
        accept("exact-native-cpython-314-extension", EXTENSION_SUFFIX
               == ".cpython-314-x86_64-linux-gnu.so")
        accept("direct-official-rust-1-95-compiler", PINNED_RUSTC.startswith(
            "/home/dev-user/.rustup/toolchains/1.95.0-"
        ) and PINNED_RUSTC.endswith("/bin/rustc"))
        accept("direct-official-rust-1-95-cargo", PINNED_CARGO.startswith(
            "/home/dev-user/.rustup/toolchains/1.95.0-"
        ) and PINNED_CARGO.endswith("/bin/cargo"))
        accept("direct-official-rust-1-95-effective-compiler-driver",
               PINNED_RUST_DRIVER.startswith(
                   "/home/dev-user/.rustup/toolchains/1.95.0-"
               ) and PINNED_RUST_DRIVER.endswith(
                   "/lib/librustc_driver-6108105cd7e839cf.so"
               ) and RUST_INPUTS[2][2]
               == "ae69468875215df490fde685ec1f1b969743482ba7e0251f4074a222606a5484"
               and RUST_INPUTS[2][4] == 153_621_360
               and MAX_BINARY_BYTES >= 153_621_360)
        accept("official-zig-0-16-binary", ZIG_COMPILER
               == "/tmp/zig-x86_64-linux-0.16.0/zig")
        accept("canonical-json-has-one-newline", canonical({"z": 1, "a": 2})
               == b'{"a":2,"z":1}\n')
        accept("strict-three-independent-families", set(FAMILIES)
               == {"c", "rust", "zig"})
        accept("exact-frozen-phase-one-matrix", FROZEN_INPUTS[1][2]
               == "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f")
        accept("synthetic-only-cli", parse_arguments(["--self-test"])
               == {"mode": "self-test"})

        for family in FAMILIES:
            pins = synthetic_pins(family)
            parsed = checked_source_pins(family, pins)
            accept(family + "-complete-distinct-source-closure",
                   set(parsed) == set(FAMILIES[family]["owners"]))
            accept(family + "-order-independent-source-pins",
                   checked_source_pins(family, list(reversed(pins))) == parsed)
            workdir = "/tmp/" + WORK_PREFIX + family + "-synthetic"
            left = phase_paths(workdir, family, "reference-a")
            right = phase_paths(workdir, family, "reference-b")
            accept(family + "-two-independent-fresh-source-roots",
                   left["source"] != right["source"]
                   and left["native"] != right["native"])
            env = build_environment(workdir, family, "reference-a")
            accept(family + "-sanitized-no-parent-environment",
                   env["LC_ALL"] == "C" and env["SOURCE_DATE_EPOCH"] == "1"
                   and env["TMPDIR"].startswith(workdir + "/reference-a/"))
            commands = planned_commands(workdir, family, "reference-a")
            for name, argv in commands.items():
                accept(family + "-exact-command-" + name,
                       checked_command(name, argv, workdir, family, "reference-a")
                       == argv and os.path.isabs(argv[0]))
                changed = list(argv)
                changed[0] = "/usr/bin/" + Path(argv[0]).name
                if changed != argv:
                    reject(family + "-reject-unpinned-command-" + name,
                           lambda name=name, changed=changed,
                           workdir=workdir, family=family:
                           checked_command(name, changed, workdir, family, "reference-a"))
                changed_arg = list(argv)
                changed_arg.append("--network")
                reject(family + "-reject-extra-command-" + name,
                       lambda name=name, changed_arg=changed_arg,
                       workdir=workdir, family=family:
                       checked_command(name, changed_arg, workdir, family, "reference-a"))
            if family == "rust":
                cargo = commands["build_rust_engine"]
                accept("rust-cargo-frozen-locked-and-offline",
                       {"--locked", "--offline", "--frozen"}.issubset(cargo)
                       and cargo[0] == PINNED_CARGO
                       and env["RUSTC"] == PINNED_RUSTC
                       and env["CARGO_NET_OFFLINE"] == "true")
                accept("rust-never-uses-path-1-97", "1.97.1" not in canonical(
                    {"commands": commands, "environment": env}
                ).decode("ascii"))
            if family == "zig":
                accept("zig-cache-is-private-to-fresh-phase",
                       "--cache-dir" in commands["build_zig_engine"]
                       and "--global-cache-dir" in commands["build_zig_engine"]
                       and env["ZIG_GLOBAL_CACHE_DIR"].startswith(workdir))
            all_args = ["--build", "--family", family, "--label", "source-v1",
                        "--source-sha256", synthetic_digest("source"),
                        "--protocol-sha256", synthetic_digest("protocol")]
            for item in pins:
                all_args += ["--owned-source-sha256", item]
            accept(family + "-complete-explicit-build-cli",
                   parse_arguments(all_args)["family"] == family)
            for index in range(len(pins)):
                missing = pins[:index] + pins[index + 1:]
                reject(family + "-reject-missing-owner-" + str(index),
                       lambda family=family, missing=missing:
                       checked_source_pins(family, missing))
                duplicate = list(pins)
                duplicate[index] = pins[(index + 1) % len(pins)]
                reject(family + "-reject-duplicated-owner-" + str(index),
                       lambda family=family, duplicate=duplicate:
                       checked_source_pins(family, duplicate))
                invalid = list(pins)
                path, _ = invalid[index].split("=", 1)
                invalid[index] = path + "=" + "A" * 64
                reject(family + "-reject-invalid-owner-digest-" + str(index),
                       lambda family=family, invalid=invalid:
                       checked_source_pins(family, invalid))
            for other in FAMILIES:
                if family != other:
                    poisoned = list(pins)
                    poisoned[0] = synthetic_pins(other)[0]
                    reject(family + "-reject-" + other + "-cross-family-owner",
                           lambda family=family, poisoned=poisoned:
                           checked_source_pins(family, poisoned))

        valid_manifest = (
            b'[package]\nname = "rebar-rust-continuation"\n'
            b'version = "0.1.0"\nedition = "2024"\n'
            b'rust-version = "1.85"\npublish = false\n\n'
            b'[lib]\ncrate-type = ["cdylib"]\n\n'
            b'[profile.release]\nopt-level = 3\nlto = true\n'
            b'codegen-units = 1\npanic = "abort"\n'
        )
        valid_lock = (
            b'version = 4\n\n[[package]]\n'
            b'name = "rebar-rust-continuation"\nversion = "0.1.0"\n'
        )
        accept("dependency-free-offline-single-package-rust",
               validate_cargo_closure(valid_manifest, valid_lock)["external_package_count"]
               == 0)
        cargo_attacks = {
            "external-regex-package": valid_manifest + b'\n[dependencies]\nregex = "1"\n',
            "external-git-dependency": valid_manifest + (
                b'\n[dependencies.bad]\ngit = "https://example.invalid/bad"\n'
            ),
            "external-build-dependency": valid_manifest + b'\n[build-dependencies]\ncc = "1"\n',
            "external-workspace": valid_manifest + b'\n[workspace]\nmembers = []\n',
            "cargo-registry-patch": valid_manifest + b'\n[patch.crates-io]\n',
            "unexpected-cargo-features": valid_manifest + b'\n[features]\ndefault = []\n',
            "weakened-cargo-release": valid_manifest.replace(b"opt-level = 3", b"opt-level = 0"),
            "foreign-cargo-package": valid_manifest.replace(
                b"rebar-rust-continuation", b"foreign-rust-matcher"
            ),
            "non-cdylib-rust-engine": valid_manifest.replace(b'"cdylib"', b'"rlib"'),
        }
        for name, value in cargo_attacks.items():
            reject("reject-" + name,
                   lambda value=value: validate_cargo_closure(value, valid_lock))
        for name, poisoned in {
            "foreign-locked-crate": valid_lock + (
                b'\n[[package]]\nname = "regex"\nversion = "1.0.0"\n'
            ),
            "foreign-locked-registry": valid_lock.replace(
                b'version = "0.1.0"',
                b'version = "0.1.0"\nsource = "registry+https://example.invalid"',
            ),
            "changed-lock-version": valid_lock.replace(b"version = 4", b"version = 3"),
        }.items():
            reject("reject-" + name,
                   lambda poisoned=poisoned:
                   validate_cargo_closure(valid_manifest, poisoned))

        for family in FAMILIES:
            own = FAMILIES[family]["adapter_import"]
            source = ("from candidates import " + own + "\n").encode("ascii")
            if family == "zig":
                source += b'engine = "_zig_probe.so"\n'
            source += b'public_match_attribute = "re"\n'
            accept(family + "-owned-python-native-bridge",
                   audit_python_source(source, family=family,
                                       location="candidates/synthetic.py")
                   ["own_native_bridge"] == own)
            for module in sorted(FORBIDDEN_MODULES):
                reject(family + "-forbid-python-module-" + module,
                       lambda family=family, own=own, module=module:
                       audit_python_source(
                           ("from candidates import " + own + "\nimport "
                            + module + "\n").encode("ascii"),
                           family=family, location="candidates/synthetic.py",
                       ))
            for other in FAMILIES:
                if other != family:
                    reject(family + "-forbid-python-bridge-" + other,
                           lambda family=family, other=other:
                           audit_python_source(
                               ("from candidates import "
                                + FAMILIES[other]["adapter_import"] + "\n")
                               .encode("ascii"),
                               family=family, location="candidates/synthetic.py",
                           ))
            for name, attack in (
                ("computed-python-import", b'__import__("re")\n'),
                ("dynamic-module-import", b'importlib.import_module("regex")\n'),
                ("subprocess-delegation", b'subprocess.run(["other"])\n'),
                ("unbounded-native-loader", b'ctypes.util.find_library("pcre")\n'),
                ("dynamic-evaluation", b'eval("import re")\n'),
            ):
                reject(family + "-forbid-" + name,
                       lambda family=family, source=source, attack=attack:
                       audit_python_source(
                           source + attack, family=family,
                           location="candidates/synthetic.py",
                       ))

        synthetic_c = (
            b"#include <Python.h>\n"
            b'const char *public_match_attribute = "re";\n'
            b"void PyInit__vm_native(void) {}\n"
        )
        accept("independent-c-source-entry", audit_native_source(
            synthetic_c, family="c", location="candidates/_vm_native.c"
        )["external_regex_dependency_count"] == 0)
        accept("rust-lifetimes-do-not-swallow-real-engine-exports",
               audit_native_source(
                   b"struct Context<'a> { value: &'a [u8] }\n"
                   b"impl Context<'_> { fn own(&self) {} }\n"
                   b"pub extern fn rebar_compile() {}\n",
                   family="rust", location="candidates/rust/src/lib.rs",
               )["external_regex_dependency_count"] == 0)
        accept("rust-byte-and-character-literals-remain-tokenized",
               ("identifier", "rebar_compile") in native_tokens(
                   b"const X: u8 = b'a'; const Y: char = '\\\\';\n"
                   b"pub extern fn rebar_compile() {}\n"
               ))
        for module in sorted(FORBIDDEN_MODULES):
            reject("reject-computed-native-import-" + module,
                   lambda module=module: audit_native_source(
                       synthetic_c + (
                           'PyImport_ImportModule("' + module + '");\n'
                       ).encode("ascii"),
                       family="c", location="candidates/_vm_native.c",
                   ))
            reject("reject-zig-foreign-compiler-import-" + module,
                   lambda module=module: audit_native_source(
                       ('const foreign = @import("' + module + '");\n'
                        'export fn rebar_zig_compile() void {}\n').encode("ascii"),
                       family="zig", location="candidates/zig/mini_regex.zig",
                   ))
        for name in sorted(FORBIDDEN_NATIVE_NAMES):
            reject("forbid-native-symbol-" + name,
                   lambda name=name: audit_native_source(
                       synthetic_c + ("void " + name + "(void);\n").encode("ascii"),
                       family="c", location="candidates/_vm_native.c",
                   ))
        for prefix in FORBIDDEN_NATIVE_PREFIXES:
            reject("forbid-native-prefix-" + prefix.rstrip("_"),
                   lambda prefix=prefix: audit_native_source(
                       synthetic_c + ("void " + prefix + "foreign(void);\n").encode("ascii"),
                       family="c", location="candidates/_vm_native.c",
                   ))
        accept("ignore-native-comments-without-masking-code",
               audit_native_source(
                   synthetic_c + b"// dlopen regex pcre\n/* dlsym re2 */\n",
                   family="c", location="candidates/_vm_native.c",
               )["external_regex_dependency_count"] == 0)

        c_dynamic = parse_elf_dynamic(synthetic_dynamic(needed=("libc.so.6",)))
        c_symbols = parse_elf_symbols(synthetic_symbols(("PyInit__vm_native",), ()))
        accept("authentic-c-native-abi",
               validate_elf("c", "extension", c_dynamic, c_symbols)
               ["required_exports"] == ["PyInit__vm_native"])
        for family in ("rust", "zig"):
            exports = tuple(sorted(
                RUST_ENGINE_EXPORTS if family == "rust" else ZIG_ENGINE_EXPORTS
            ))
            name = FAMILIES[family]["binaries"]["engine"]
            engine_dynamic = parse_elf_dynamic(synthetic_dynamic(
                needed=("libc.so.6",), soname=name,
            ))
            engine_symbols = parse_elf_symbols(synthetic_symbols(exports, ()))
            accept(family + "-authentic-native-engine-abi",
                   validate_elf(family, "engine", engine_dynamic, engine_symbols)
                   ["soname"] == [name])
            initial = "PyInit__" + family + "_bridge"
            own_reference = "rebar_compile" if family == "rust" else "rebar_zig_compile"
            bridge_dynamic = parse_elf_dynamic(synthetic_dynamic(
                needed=(name, "libc.so.6"), runpath="$ORIGIN",
            ))
            bridge_symbols = parse_elf_symbols(synthetic_symbols(
                (initial,), (own_reference,),
            ))
            accept(family + "-authentic-native-bridge-abi",
                   validate_elf(family, "bridge", bridge_dynamic, bridge_symbols)
                   ["runpath"] == ["$ORIGIN"])
            attacks = {
                "foreign-engine-needed": parse_elf_dynamic(synthetic_dynamic(
                    needed=(name, "libpcre2-8.so.0"), runpath="$ORIGIN",
                )),
                "foreign-absolute-runpath": parse_elf_dynamic(synthetic_dynamic(
                    needed=(name,), runpath="/tmp/foreign",
                )),
                "legacy-rpath-delegation": parse_elf_dynamic(synthetic_dynamic(
                    needed=(name,), runpath="$ORIGIN", rpath="/tmp/foreign",
                )),
                "missing-own-engine-dependency": parse_elf_dynamic(synthetic_dynamic(
                    needed=("libc.so.6",), runpath="$ORIGIN",
                )),
            }
            for attack_name, poisoned in attacks.items():
                reject(family + "-reject-" + attack_name,
                       lambda family=family, poisoned=poisoned,
                       bridge_symbols=bridge_symbols:
                       validate_elf(family, "bridge", poisoned, bridge_symbols))
            reject(family + "-reject-substituted-engine-soname",
                   lambda family=family, name=name, engine_symbols=engine_symbols:
                   validate_elf(family, "engine", parse_elf_dynamic(
                       synthetic_dynamic(needed=("libc.so.6",),
                                         soname="foreign-" + name)
                   ), engine_symbols))
            reject(family + "-reject-omitted-engine-export",
                   lambda family=family, name=name, exports=exports:
                   validate_elf(family, "engine", parse_elf_dynamic(
                       synthetic_dynamic(needed=("libc.so.6",), soname=name)
                   ), parse_elf_symbols(synthetic_symbols(exports[:-1], ()))))

        for value in (None, "", "A" * 64, "a" * 63, "a" * 65,
                      "g" * 64, 7, True, b"a" * 64):
            reject("invalid-sha256-" + str(len(rejected)),
                   lambda value=value: checked_digest(value, "synthetic"))
        for value in ("", "/tmp/other", "../owner", "a/../b", "a//b",
                      "./owner", "a/./b", "a\\b", "a\x00b"):
            reject("reject-unsafe-relative-path-" + str(len(rejected)),
                   lambda value=value: checked_relative(value))
        for value in ("", "A", "../x", "a_b", "a--b", "a-", "/tmp/x",
                      "x" * 49):
            reject("reject-unsafe-label-" + str(len(rejected)),
                   lambda value=value: checked_label(value))
        for value in ("/", "/tmp", "/tmp/other", "/tmp/" + WORK_PREFIX + "x/../x",
                      "/tmp/" + WORK_PREFIX + "x/child",
                      "/tmp/" + WORK_PREFIX + "x/"):
            reject("reject-broad-build-root-" + str(len(rejected)),
                   lambda value=value: checked_workdir(value))
        for raw in (b'{"x":1,"x":2}\n', b'{"x":NaN}\n',
                    b'{"x":Infinity}\n', b'{"x":-Infinity}\n',
                    b"[]\n", b"", b"{", b"\xff"):
            reject("reject-unsafe-json-" + str(len(rejected)),
                   lambda raw=raw: decode_json(raw, canonical_required=False))
        for name, operation in (
            ("actual-filesystem-open", lambda: builtins.open("/tmp/forbidden")),
            ("actual-filesystem-os-open", lambda: os.open("/tmp/forbidden", os.O_RDONLY)),
            ("actual-source-read", lambda: Path("/tmp/forbidden").read_bytes()),
            ("actual-source-write", lambda: Path("/tmp/forbidden").write_bytes(b"x")),
            ("actual-directory-scan", lambda: os.listdir("/tmp")),
            ("actual-compiler-subprocess", lambda: subprocess.run([PINNED_RUSTC])),
            ("actual-compiler-popen", lambda: subprocess.Popen([ZIG_COMPILER])),
            ("actual-private-temp-root", lambda: tempfile.mkdtemp()),
            ("actual-thread-start", lambda: threading.Thread(target=lambda: None).start()),
            ("actual-clock", lambda: time.time()),
            ("actual-performance-clock", lambda: time.perf_counter_ns()),
            ("actual-network", lambda: socket.socket()),
            ("actual-candidate-import", lambda: importlib.import_module(
                "candidates.rust_candidate"
            )),
        ):
            reject("source-only-blocks-" + name, operation)

        require(len(accepted) == len(set(accepted))
                and len(rejected) == len(set(rejected)),
                "every native build control must retain its exact distinct identity")
        require(all(guard.counts[key] == 0 for key in (
            "actual_file_reads", "actual_file_writes", "actual_processes",
            "actual_threads", "actual_clocks", "actual_network",
            "actual_candidate_imports", "actual_native_library_loads",
            "actual_holdout_reads",
        )), "synthetic controls performed a real external action")
        counters = dict(guard.counts)

    return {
        "schema": SCHEMA + "-synthetic-source-only-self-test",
        "status": "PASS",
        "synthetic": True,
        "positive_control_count": len(accepted),
        "positive_controls": accepted,
        "rejected_attack_count": len(rejected),
        "rejected_attacks": rejected,
        "guard_counters": counters,
        "family_count": 3,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "native_builds_started": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "candidate_correctness": "NOT MEASURED",
        "winner_selected": False,
        "holdout": "NOT OPENED",
    }


def main(arguments: list[str] | None = None) -> int:
    try:
        parsed = parse_arguments(list(sys.argv[1:] if arguments is None else arguments))
        if parsed["mode"] == "self-test":
            result = self_test()
            sys.stdout.buffer.write(canonical(result))
            sys.stdout.buffer.flush()
            return 0
        status, result = run_build(parsed)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return status
    except (BuildError, OSError, ValueError, UnicodeError) as error:
        sys.stderr.write(type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
