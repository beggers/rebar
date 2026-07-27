#!/usr/bin/env python3
"""Reproduce an explicitly pinned, independently owned Zig engine and bridge.

V4 retains V3's fourteen complete, bounded source and toolchain owners while
requiring the caller to pin both evolving Zig-family sources explicitly. V3 is
separately authenticated as a frozen predecessor. A real build runs only when
explicitly requested and writes fresh, no-clobber evidence even when it fails.
Synthetic self-tests never read source or evidence, start a compiler or worker,
import a candidate, access a network, or sample randomness or a clock.
"""

from __future__ import annotations

import argparse
import base64
import builtins
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
from typing import Any


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/reproduce_owned_zig_source_build_v4.py"
EVIDENCE_RELATIVE = "experiments/rust_public_practice_v1"
SCHEMA = "rebar-owned-zig-source-build-v4"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_INCLUDE = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
ZIG_VERSION = "0.16.0"
ZIG_COMPILER = "/tmp/zig-x86_64-linux-0.16.0/zig"
ZIG_ARCHIVE = "/tmp/rebar-zig-0.16.0-x86_64-linux.tar.xz"
PINNED_HOST_CC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_HOST_READELF = "/usr/bin/x86_64-linux-gnu-readelf"
ZIG_ARCHIVE_SIZE = 55_478_392
ZIG_COMPILER_SIZE = 172_641_672
WORK_PREFIX = "rebar-owned-zig-source-build-v4-"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_OFFICIAL_COMPILER_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024

OWNED_BRIDGE_RELATIVE = "candidates/zig/py_bridge.c"
OWNED_ADAPTER_RELATIVE = "candidates/zig_candidate.py"
OWNED_SOURCE_LOCATIONS = frozenset({
    OWNED_BRIDGE_RELATIVE,
    OWNED_ADAPTER_RELATIVE,
})
FROZEN_V3_PREDECESSOR = (
    "frozen_v3_build_predecessor",
    "tools/reproduce_owned_zig_source_build_v3.py",
    "af5a04fccf179de8629c4d9470d20accbb126c8897d3d45d3fe041138d2abfc3",
    MAX_SOURCE_BYTES,
    None,
)

REQUIRED_ENGINE_EXPORTS = frozenset({
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
ALLOWED_ENGINE_UNDEFINED = frozenset({
    "_PyUnicode_IsAlpha", "_PyUnicode_IsDecimalDigit", "_PyUnicode_IsDigit",
    "_PyUnicode_IsNumeric", "_PyUnicode_IsWhitespace",
    "_PyUnicode_ToLowercase", "_PyUnicode_ToUppercase", "__gmon_start__",
    "free", "isalnum", "malloc", "malloc_usable_size", "memcpy", "memset",
    "posix_memalign", "realloc", "tolower",
})
REQUIRED_BRIDGE_ENGINE_REFERENCES = frozenset({
    "rebar_zig_collect_records_wide", "rebar_zig_compile",
    "rebar_zig_compile_guarded", "rebar_zig_flags", "rebar_zig_free",
    "rebar_zig_groups", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_wide", "rebar_zig_name_copy", "rebar_zig_name_count",
    "rebar_zig_name_group", "rebar_zig_name_length",
})
ALLOWED_BRIDGE_SYSTEM_UNDEFINED = frozenset({
    "_ITM_deregisterTMCloneTable", "_ITM_registerTMCloneTable",
    "__assert_fail", "__ctype_b_loc", "__ctype_tolower_loc",
    "__cxa_finalize", "__gmon_start__", "__memcpy_chk",
    "__stack_chk_fail", "bcmp", "calloc", "free", "malloc", "memchr",
    "memcmp", "memcpy", "memmem", "memmove", "memset", "realloc", "strlen",
})
FORBIDDEN_NATIVE_SYMBOLS = frozenset({
    "dlmopen", "dlopen", "dlsym", "dlvsym", "execv", "execve", "fork",
    "popen", "posix_spawn", "regcomp", "regexec", "regfree", "system",
    "PyRun_AnyFile", "PyRun_SimpleString", "PyRun_String",
    "Py_CompileString", "PyEval_EvalCode",
})
FORBIDDEN_NATIVE_PREFIXES = (
    "_PyImport_", "_PyRun_", "PyInit__sre", "PyImport_ExecCode",
    "PyImport_Import", "PyRun_", "Py_CompileString", "PyEval_Eval",
    "hs_", "onig_", "pcre2_", "pcre_", "re2_", "regex_", "sre_",
)
ALLOWED_SYSTEM_NEEDED = frozenset({"libc.so.6", "libm.so.6", "libgcc_s.so.1"})


class BuildError(Exception):
    """A pin, owned input, isolated build, or publication was untrustworthy."""


class SourceOnlyError(BuildError):
    """A synthetic control attempted a forbidden real external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise BuildError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii") + b"\n"


def valid_digest(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def checked_digest(value: Any, description: str) -> str:
    require(
        valid_digest(value),
        "an exact lowercase SHA-256 is required: " + description,
    )
    return value


def checked_owned_source_pins(values: Any) -> dict[str, str]:
    require(
        type(values) is list and len(values) == len(OWNED_SOURCE_LOCATIONS),
        "supply exactly two distinct --owned-source-sha256 PATH=SHA256 pins",
    )
    pins: dict[str, str] = {}
    for value in values:
        require(
            type(value) is str and value.count("=") == 1,
            "an owned source pin must be exactly PATH=SHA256",
        )
        location, digest = value.split("=", 1)
        require(
            location in OWNED_SOURCE_LOCATIONS and location not in pins,
            "pin each exact owned Zig bridge and adapter path exactly once",
        )
        pins[location] = checked_digest(digest, location)
    require(
        set(pins) == OWNED_SOURCE_LOCATIONS,
        "both exact owned Zig bridge and adapter source pins are mandatory",
    )
    require(
        pins[OWNED_BRIDGE_RELATIVE] != pins[OWNED_ADAPTER_RELATIVE],
        "distinct owned Zig sources cannot reuse a claimed SHA-256",
    )
    return pins


def frozen_inputs(pins: Any) -> tuple[tuple[str, str, str, int, int | None], ...]:
    require(
        type(pins) is dict
        and set(pins) == OWNED_SOURCE_LOCATIONS
        and all(valid_digest(digest) for digest in pins.values())
        and pins[OWNED_BRIDGE_RELATIVE] != pins[OWNED_ADAPTER_RELATIVE],
        "construct the fourteen owners only from two exact caller-pinned sources",
    )
    return (
        (
            "build_record", "docs/ZIG-SOURCE-BUILD-V1.md",
            "b2f0b0c85d28ace4593ba38cac95d731fb15f05e22de5b4ffcbc7d17d41efc49",
            MAX_SOURCE_BYTES, None,
        ),
        (
            "zig_engine_source", "candidates/zig/mini_regex.zig",
            "539bf5d378e0c2845c01519fcce62f1ef5e68610f477912c44a03027fb67a346",
            MAX_SOURCE_BYTES, None,
        ),
        (
            "zig_bridge_source", OWNED_BRIDGE_RELATIVE,
            pins[OWNED_BRIDGE_RELATIVE], MAX_SOURCE_BYTES, None,
        ),
        (
            "zig_python_adapter", OWNED_ADAPTER_RELATIVE,
            pins[OWNED_ADAPTER_RELATIVE], MAX_SOURCE_BYTES, None,
        ),
        (
            "frozen_original_correctness_oracle",
            "tools/independent_original_cpython_suite_v5.py",
            "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
            MAX_SOURCE_BYTES, None,
        ),
        (
            "frozen_from_scratch_audit",
            "tools/independent_from_scratch_audit_v2.py",
            "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d",
            MAX_SOURCE_BYTES, None,
        ),
        (
            "official_zig_archive", ZIG_ARCHIVE,
            "70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00",
            MAX_BINARY_BYTES, ZIG_ARCHIVE_SIZE,
        ),
        (
            "official_zig_compiler", ZIG_COMPILER,
            "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c",
            MAX_OFFICIAL_COMPILER_BYTES, ZIG_COMPILER_SIZE,
        ),
        (
            "pinned_python_header", PYTHON_INCLUDE + "/Python.h",
            "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f",
            MAX_SOURCE_BYTES, None,
        ),
        (
            "pinned_python_patchlevel", PYTHON_INCLUDE + "/patchlevel.h",
            "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95",
            MAX_SOURCE_BYTES, None,
        ),
        (
            "pinned_host_c_compiler", PINNED_HOST_CC,
            "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26",
            MAX_BINARY_BYTES, None,
        ),
        (
            "pinned_host_readelf", PINNED_HOST_READELF,
            "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0",
            MAX_BINARY_BYTES, None,
        ),
        (
            "frozen_build_predecessor",
            "tools/reproduce_owned_zig_source_build_v1.py",
            "53df4260eee56a143d2cd9134e5c0dc336b412758218c681f59acee0a8b8644e",
            MAX_SOURCE_BYTES, None,
        ),
        (
            "frozen_v2_build_predecessor",
            "tools/reproduce_owned_zig_source_build_v2.py",
            "e7a387c2281e44e67ea8e1258d00ec4e46e70fe475f1ac2e3c011953a30ed3a1",
            MAX_SOURCE_BYTES, None,
        ),
    )


def checked_label(value: Any) -> str:
    require(
        type(value) is str
        and 21 <= len(value) <= 100
        and value.startswith("zig-source-build-v4-")
        and all(ch in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in value)
        and not value.endswith("-")
        and "--" not in value,
        "use one fresh, bounded zig-source-build-v4-* publication label",
    )
    return value


def checked_workdir(value: Any) -> str:
    require(
        type(value) is str
        and value.startswith("/tmp/" + WORK_PREFIX)
        and Path(value).parent == Path("/tmp")
        and value == str(Path(value))
        and len(Path(value).name) <= 120,
        "the isolated build must use one fresh direct child of /tmp",
    )
    return value


def checked_input(
    specification: Any,
    specifications: tuple[tuple[str, str, str, int, int | None], ...],
) -> tuple[str, str, str, int, int | None]:
    require(
        type(specifications) is tuple
        and len(specifications) == 14
        and type(specification) is tuple
        and len(specification) == 5
        and specification in specifications,
        "only one of the exact fourteen caller-frozen Zig inputs may be read",
    )
    name, location, expected, maximum, exact_size = specification
    require(
        type(name) is str and valid_digest(expected),
        "a frozen owned-input name or SHA-256 was forged",
    )
    if name == "official_zig_compiler":
        require(
            location == ZIG_COMPILER
            and maximum == MAX_OFFICIAL_COMPILER_BYTES
            and exact_size == ZIG_COMPILER_SIZE
            and MAX_BINARY_BYTES < exact_size < maximum,
            "only the exact official Zig compiler receives the 256 MiB bound",
        )
    else:
        require(
            type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "a non-compiler frozen artifact bound was forged or enlarged",
        )
        require(
            exact_size is None
            or type(exact_size) is int and 0 < exact_size <= maximum,
            "an exact non-compiler artifact size was forged",
        )
    path = Path(location)
    if path.is_absolute():
        require(
            location in {
                ZIG_ARCHIVE,
                ZIG_COMPILER,
                PYTHON_INCLUDE + "/Python.h",
                PYTHON_INCLUDE + "/patchlevel.h",
                PINNED_HOST_CC,
                PINNED_HOST_READELF,
            },
            "a frozen official toolchain escaped its exact absolute path",
        )
    else:
        require(
            location == str(path)
            and path.parts
            and not any(part in ("", ".", "..") for part in path.parts)
            and path.parts[0] in {"candidates", "docs", "tools"},
            "a frozen owned input escaped its exact repository path",
        )
    return name, location, expected, maximum, exact_size


def checked_v3_predecessor(
    specification: Any,
) -> tuple[str, str, str, int, int | None]:
    require(
        type(specification) is tuple
        and specification == FROZEN_V3_PREDECESSOR
        and valid_digest(specification[2])
        and specification[3] == MAX_SOURCE_BYTES
        and specification[4] is None,
        "the independent exact frozen V3 controller predecessor was forged",
    )
    return specification


def authenticate_path(
    path: Path,
    *,
    expected: str | None,
    maximum: int,
    exact_size: int | None = None,
) -> dict[str, Any]:
    require(path.is_absolute(), "authenticate only an exact absolute input path")
    require(
        type(maximum) is int and 0 < maximum <= MAX_OFFICIAL_COMPILER_BYTES,
        "an authenticated native input has an invalid size bound",
    )
    if exact_size is not None:
        require(
            type(exact_size) is int and 0 < exact_size <= maximum,
            "an authenticated native input has an invalid exact size",
        )
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(path), flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode), "an input is not a real regular file")
        require(
            0 <= before.st_size <= maximum,
            "an authenticated input exceeded its frozen size bound",
        )
        if exact_size is not None:
            require(
                before.st_size == exact_size,
                "a frozen artifact has the wrong exact byte size",
            )
        hasher = hashlib.sha256()
        actual_size = 0
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            actual_size += len(chunk)
            require(actual_size <= maximum, "an input grew during its complete read")
            hasher.update(chunk)
        after = os.fstat(descriptor)
        require(
            actual_size == before.st_size == after.st_size
            and (before.st_dev, before.st_ino, before.st_mtime_ns)
            == (after.st_dev, after.st_ino, after.st_mtime_ns),
            "an authenticated input changed during its complete no-follow read",
        )
        visible = os.lstat(str(path))
        require(
            stat.S_ISREG(visible.st_mode)
            and (visible.st_dev, visible.st_ino, visible.st_size)
            == (after.st_dev, after.st_ino, after.st_size),
            "an authenticated source path was redirected or replaced",
        )
        digest = hasher.hexdigest()
        if expected is not None:
            require(
                digest == checked_digest(expected, str(path)),
                "a frozen source, bridge, adapter, or compiler changed: " + str(path),
            )
        return {"path": str(path), "sha256": digest, "size_bytes": actual_size}
    finally:
        os.close(descriptor)


def authenticate_frozen_input(
    specification: Any,
    specifications: tuple[tuple[str, str, str, int, int | None], ...],
) -> tuple[str, dict[str, Any]]:
    name, location, expected, maximum, exact_size = checked_input(
        specification,
        specifications,
    )
    path = Path(location) if Path(location).is_absolute() else ROOT / location
    return name, authenticate_path(
        path,
        expected=expected,
        maximum=maximum,
        exact_size=exact_size,
    )


def authenticate_v3_predecessor() -> tuple[str, dict[str, Any]]:
    name, location, expected, maximum, exact_size = checked_v3_predecessor(
        FROZEN_V3_PREDECESSOR,
    )
    return name, authenticate_path(
        ROOT / location,
        expected=expected,
        maximum=maximum,
        exact_size=exact_size,
    )


def planned_commands(workdir: str) -> dict[str, list[str]]:
    base = Path(checked_workdir(workdir))
    engine = base / "_zig_probe.so"
    bridge = base / ("_zig_bridge" + EXTENSION_SUFFIX)
    return {
        "compiler_version": [ZIG_COMPILER, "version"],
        "build_zig_engine": [
            ZIG_COMPILER,
            "build-lib",
            str(ROOT / "candidates/zig/mini_regex.zig"),
            "-dynamic",
            "-lc",
            "-O",
            "ReleaseFast",
            "-fallow-shlib-undefined",
            "-fsoname=_zig_probe.so",
            "--cache-dir",
            str(base / "local-cache"),
            "--global-cache-dir",
            str(base / "global-cache"),
            "-femit-bin=" + str(engine),
        ],
        "build_python_bridge": [
            PINNED_HOST_CC,
            "-shared",
            "-fPIC",
            "-O3",
            "-I" + PYTHON_INCLUDE,
            str(ROOT / OWNED_BRIDGE_RELATIVE),
            str(engine),
            "-Wl,-rpath,$ORIGIN",
            "-o",
            str(bridge),
        ],
        "engine_dynamic": [PINNED_HOST_READELF, "--dynamic", "--wide", str(engine)],
        "bridge_dynamic": [PINNED_HOST_READELF, "--dynamic", "--wide", str(bridge)],
        "engine_symbols": [PINNED_HOST_READELF, "--dyn-syms", "--wide", str(engine)],
        "bridge_symbols": [PINNED_HOST_READELF, "--dyn-syms", "--wide", str(bridge)],
    }


def checked_command(name: Any, argv: Any, workdir: str) -> list[str]:
    planned = planned_commands(workdir)
    require(
        type(name) is str
        and name in planned
        and type(argv) is list
        and all(type(item) is str and "\x00" not in item for item in argv)
        and argv == planned[name],
        "only an exact, frozen, shell-free owned Zig build command may run",
    )
    return list(argv)


def sanitize_command(argv: list[str], workdir: str) -> list[str]:
    prefix = checked_workdir(workdir)
    return [item.replace(prefix, "<FRESH_PRIVATE_TMP>") for item in argv]


def run_process(
    name: str,
    workdir: str,
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    argv = checked_command(name, planned_commands(workdir)[name], workdir)
    empty = hashlib.sha256(b"").hexdigest()
    entry: dict[str, Any] = {
        "name": name,
        "argv": sanitize_command(argv, workdir),
        "shell": False,
        "stdout": "",
        "stderr": "",
        "stdout_base64": "",
        "stderr_base64": "",
        "stdout_sha256": empty,
        "stderr_sha256": empty,
        "stdout_bytes": 0,
        "stderr_bytes": 0,
        "exit_status": None,
    }
    steps.append(entry)
    try:
        completed = subprocess.run(
            argv,
            cwd=workdir,
            env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C", "TZ": "UTC"},
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            shell=False,
        )
        entry["exit_status"] = completed.returncode
        entry["stdout_bytes"] = len(completed.stdout)
        entry["stderr_bytes"] = len(completed.stderr)
        require(
            len(completed.stdout) <= MAX_PROCESS_BYTES
            and len(completed.stderr) <= MAX_PROCESS_BYTES,
            "complete actual compiler output exceeded its frozen size bound",
        )
        for stream_name, raw in (
            ("stdout", completed.stdout),
            ("stderr", completed.stderr),
        ):
            entry[stream_name + "_base64"] = base64.b64encode(raw).decode("ascii")
            entry[stream_name + "_sha256"] = hashlib.sha256(raw).hexdigest()
            entry[stream_name] = raw.decode("utf-8", "backslashreplace")
        require(
            completed.returncode == 0,
            "the actual owned source-build command failed: " + name,
        )
    except Exception as error:
        entry["exception_type"] = type(error).__name__
        entry["exception_message"] = str(error)
        raise
    return entry


def dynamic_metadata(output: str) -> dict[str, list[str]]:
    require(type(output) is str, "complete actual ELF dynamic output is mandatory")
    groups: dict[str, list[str]] = {
        "needed": [],
        "soname": [],
        "runpath": [],
        "rpath": [],
    }
    tags = {
        "(NEEDED)": "needed",
        "(SONAME)": "soname",
        "(RUNPATH)": "runpath",
        "(RPATH)": "rpath",
    }
    for line in output.splitlines():
        opening = line.find("[")
        closing = line.find("]", opening + 1)
        if opening < 0 or closing < opening:
            continue
        for marker, group in tags.items():
            if marker in line:
                groups[group].append(line[opening + 1 : closing])
                break
    return groups


def dynamic_symbols(output: str) -> tuple[set[str], set[str]]:
    require(type(output) is str, "complete actual ELF symbol output is mandatory")
    exported: set[str] = set()
    undefined: set[str] = set()
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 8 and parts[0].rstrip(":").isdigit():
            name = parts[7].split("@", 1)[0]
            if parts[6] == "UND":
                require(name not in undefined, "an undefined ELF symbol was duplicated")
                undefined.add(name)
            elif parts[4] in {"GLOBAL", "WEAK"}:
                require(name not in exported, "an exported ELF symbol was duplicated")
                exported.add(name)
    return exported, undefined


def validate_elf(
    engine: Any,
    bridge: Any,
    engine_symbols: Any,
    engine_undefined: Any,
    bridge_symbols: Any,
    bridge_undefined: Any,
) -> dict[str, Any]:
    require(
        type(engine) is dict and type(bridge) is dict,
        "both complete native ELF dynamic records are mandatory",
    )
    require(
        engine.get("soname") == ["_zig_probe.so"]
        and not engine.get("rpath")
        and not engine.get("runpath")
        and set(engine.get("needed", ())).issubset(ALLOWED_SYSTEM_NEEDED),
        "the fresh Zig engine has a foreign dependency, search path, or SONAME",
    )
    require(
        bridge.get("runpath") == ["$ORIGIN"]
        and not bridge.get("rpath")
        and "_zig_probe.so" in bridge.get("needed", ())
        and set(bridge.get("needed", ())).issubset(
            ALLOWED_SYSTEM_NEEDED | {"_zig_probe.so"},
        ),
        "the fresh bridge does not bind solely to its adjacent owned Zig engine",
    )
    require(
        all(
            type(value) is set
            for value in (
                engine_symbols,
                engine_undefined,
                bridge_symbols,
                bridge_undefined,
            )
        ),
        "actual defined and undefined symbol sets from both ELFs are mandatory",
    )
    require(
        engine_symbols == REQUIRED_ENGINE_EXPORTS,
        "the actual Zig engine lacks its exact twenty-two owned exports",
    )
    require(
        engine_undefined == ALLOWED_ENGINE_UNDEFINED,
        "the actual Zig engine references an unapproved external symbol",
    )
    require(
        bridge_symbols == {"PyInit__zig_bridge"},
        "the bridge lacks its sole exact CPython initialization export",
    )
    require(
        bridge_undefined & REQUIRED_ENGINE_EXPORTS
        == REQUIRED_BRIDGE_ENGINE_REFERENCES,
        "the fresh bridge does not reference exactly its own Zig engine",
    )
    unexpected = {
        name
        for name in bridge_undefined
        if name not in REQUIRED_ENGINE_EXPORTS
        and name not in ALLOWED_BRIDGE_SYSTEM_UNDEFINED
        and not name.startswith(("Py", "_Py"))
    }
    require(not unexpected, "the actual bridge resolves a foreign native symbol")
    all_symbols = engine_symbols | engine_undefined | bridge_symbols | bridge_undefined
    forbidden = sorted(
        name
        for name in all_symbols
        if name in FORBIDDEN_NATIVE_SYMBOLS
        or name.startswith(FORBIDDEN_NATIVE_PREFIXES)
    )
    require(
        not forbidden,
        "the native build references an external regex engine, importer, or loader",
    )
    return {
        "engine": engine,
        "bridge": bridge,
        "required_owned_engine_exports": sorted(REQUIRED_ENGINE_EXPORTS),
        "required_owned_engine_exports_present": True,
        "owned_engine_undefined_symbols": sorted(engine_undefined),
        "owned_bridge_engine_references": sorted(
            bridge_undefined & REQUIRED_ENGINE_EXPORTS,
        ),
        "bridge_initialization_symbol": "PyInit__zig_bridge",
        "forbidden_native_symbols": forbidden,
    }


def open_evidence_directory() -> int:
    return os.open(
        str(ROOT / EVIDENCE_RELATIVE),
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )


def require_fresh_publications(directory: int, label: str) -> tuple[str, str]:
    checked_label(label)
    names = (label + ".json", label + "-publication-receipt.json")
    for name in names:
        try:
            os.stat(name, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            continue
        raise BuildError("a fresh V4 source-build publication already exists: " + name)
    return names


def publish_fresh(directory: int, name: str, document: dict[str, Any]) -> dict[str, Any]:
    require(
        type(name) is str and "/" not in name and name.endswith(".json"),
        "an atomic evidence filename escaped its exclusively owned directory",
    )
    data = canonical(document)
    temporary = "." + name + "." + os.urandom(12).hex() + ".tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(temporary, flags, 0o600, dir_fd=directory)
    try:
        remaining = memoryview(data)
        while remaining:
            amount = os.write(descriptor, remaining)
            require(amount > 0, "atomic evidence stopped before the complete record")
            remaining = remaining[amount:]
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        os.link(
            temporary,
            name,
            src_dir_fd=directory,
            dst_dir_fd=directory,
            follow_symlinks=False,
        )
        os.fsync(directory)
        observed_descriptor = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory,
        )
        try:
            observed = bytearray()
            while True:
                chunk = os.read(observed_descriptor, 1024 * 1024)
                if not chunk:
                    break
                observed.extend(chunk)
                require(
                    len(observed) <= MAX_PROCESS_BYTES,
                    "fresh published evidence exceeded its complete readback bound",
                )
        finally:
            os.close(observed_descriptor)
        require(
            bytes(observed) == data,
            "fresh no-clobber evidence failed its complete independent readback",
        )
        return {
            "relative": EVIDENCE_RELATIVE + "/" + name,
            "sha256": hashlib.sha256(data).hexdigest(),
            "size_bytes": len(data),
        }
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass


class SyntheticSandbox:
    """Reject and separately count all real effects of synthetic V4 controls."""

    def __init__(self) -> None:
        self.counts = {
            "filesystem_reads": 0,
            "filesystem_writes": 0,
            "processes": 0,
            "candidate_imports": 0,
            "candidate_workers": 0,
            "network_access": 0,
            "random_samples": 0,
            "clock_samples": 0,
        }
        self.blocked = {name: 0 for name in self.counts}
        self.originals: list[tuple[Any, str, Any]] = []

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def blocked(*args: Any, **kwargs: Any) -> Any:
            self.blocked[category] += 1
            raise SourceOnlyError(
                "synthetic Zig V4 controls forbid " + category + ": " + name,
            )

        self.originals.append((owner, name, original))
        setattr(owner, name, blocked)

    def __enter__(self) -> SyntheticSandbox:
        for owner, name, category in (
            (builtins, "open", "filesystem_reads"),
            (io, "open", "filesystem_reads"),
            (os, "open", "filesystem_reads"),
            (os, "read", "filesystem_reads"),
            (os, "stat", "filesystem_reads"),
            (os, "lstat", "filesystem_reads"),
            (os, "listdir", "filesystem_reads"),
            (os, "scandir", "filesystem_reads"),
            (os, "write", "filesystem_writes"),
            (os, "mkdir", "filesystem_writes"),
            (os, "unlink", "filesystem_writes"),
            (os, "remove", "filesystem_writes"),
            (os, "rename", "filesystem_writes"),
            (os, "replace", "filesystem_writes"),
            (os, "link", "filesystem_writes"),
            (tempfile, "mkdtemp", "filesystem_writes"),
            (subprocess, "run", "processes"),
            (subprocess, "Popen", "processes"),
            (os, "system", "processes"),
            (os, "fork", "processes"),
            (os, "posix_spawn", "processes"),
            (os, "posix_spawnp", "processes"),
            (importlib, "import_module", "candidate_imports"),
            (threading.Thread, "start", "candidate_workers"),
            (socket, "create_connection", "network_access"),
            (socket, "socket", "network_access"),
            (os, "urandom", "random_samples"),
            (time, "time", "clock_samples"),
            (time, "time_ns", "clock_samples"),
            (time, "monotonic", "clock_samples"),
            (time, "monotonic_ns", "clock_samples"),
            (time, "perf_counter", "clock_samples"),
            (time, "perf_counter_ns", "clock_samples"),
            (time, "process_time", "clock_samples"),
            (time, "thread_time", "clock_samples"),
        ):
            self.install(owner, name, category)
        return self

    def __exit__(self, error_type: Any, error: Any, trace: Any) -> None:
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)


def source_self_test() -> dict[str, Any]:
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(
            type(name) is str and name not in accepted and name not in rejected,
            "an accepted synthetic control name was forged or duplicated",
        )
        require(condition, "a valid synthetic Zig build control was rejected: " + name)
        accepted.append(name)

    def reject(
        name: str,
        action: Any,
        error_type: type[Exception] = BuildError,
    ) -> None:
        require(
            type(name) is str and name not in accepted and name not in rejected,
            "a rejected synthetic control name was forged or duplicated",
        )
        try:
            action()
        except error_type:
            rejected.append(name)
        else:
            raise BuildError(
                "a forged or unsafe synthetic Zig control was accepted: " + name,
            )

    with SyntheticSandbox() as sandbox:
        bridge_pin = "1" * 64
        adapter_pin = "2" * 64
        pin_arguments = [
            OWNED_BRIDGE_RELATIVE + "=" + bridge_pin,
            OWNED_ADAPTER_RELATIVE + "=" + adapter_pin,
        ]
        pins = checked_owned_source_pins(pin_arguments)
        specifications = frozen_inputs(pins)
        accept(
            "exactly-two-distinct-explicit-owned-bridge-and-adapter-pins",
            pins == {
                OWNED_BRIDGE_RELATIVE: bridge_pin,
                OWNED_ADAPTER_RELATIVE: adapter_pin,
            },
        )
        accept(
            "caller-pins-are-order-independent",
            checked_owned_source_pins(list(reversed(pin_arguments))) == pins,
        )
        accept(
            "all-fourteen-complete-caller-frozen-owned-input-specifications",
            len(specifications) == 14,
        )
        accept(
            "each-of-fourteen-exact-source-and-official-toolchain-pins",
            all(checked_input(spec, specifications) == spec for spec in specifications),
        )
        accept("exact-official-zig-version", ZIG_VERSION == "0.16.0")
        accept("exact-official-archive-size", ZIG_ARCHIVE_SIZE == 55_478_392)
        accept("exact-official-compiler-size", ZIG_COMPILER_SIZE == 172_641_672)
        accept(
            "only-authenticated-official-compiler-receives-256-mib-bound",
            MAX_OFFICIAL_COMPILER_BYTES == 256 * 1024 * 1024
            and specifications[7][3] == MAX_OFFICIAL_COMPILER_BYTES
            and all(
                specification[3] <= MAX_BINARY_BYTES
                for index, specification in enumerate(specifications)
                if index != 7
            ),
        )
        accept("preserve-128-mib-native-output-bound", MAX_BINARY_BYTES == 128 * 1024 * 1024)
        accept("preserve-eight-mib-source-bound", MAX_SOURCE_BYTES == 8 * 1024 * 1024)
        accept(
            "preserve-32-mib-complete-process-output-bound",
            MAX_PROCESS_BYTES == 32 * 1024 * 1024,
        )
        accept(
            "compiler-exact-size-exceeds-native-output-bound",
            MAX_BINARY_BYTES < ZIG_COMPILER_SIZE < MAX_OFFICIAL_COMPILER_BYTES,
        )
        accept(
            "exact-stable-cpython-extension-suffix",
            EXTENSION_SUFFIX == ".cpython-314-x86_64-linux-gnu.so",
        )
        accept(
            "exact-pinned-host-c-compiler-and-elf-inspector",
            specifications[10][1] == PINNED_HOST_CC
            and specifications[11][1] == PINNED_HOST_READELF,
        )
        accept(
            "exact-frozen-from-scratch-zig-engine-source",
            specifications[1][1] == "candidates/zig/mini_regex.zig"
            and specifications[1][2]
            == "539bf5d378e0c2845c01519fcce62f1ef5e68610f477912c44a03027fb67a346",
        )
        accept(
            "exact-explicit-current-bridge-source-pin",
            specifications[2][1] == OWNED_BRIDGE_RELATIVE
            and specifications[2][2] == bridge_pin,
        )
        accept(
            "exact-explicit-current-adapter-source-pin",
            specifications[3][1] == OWNED_ADAPTER_RELATIVE
            and specifications[3][2] == adapter_pin,
        )
        accept(
            "exact-corrected-frozen-v5-cpython-original-oracle",
            specifications[4][1] == "tools/independent_original_cpython_suite_v5.py"
            and specifications[4][2]
            == "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
        )
        accept(
            "preserve-exact-frozen-v1-build-predecessor",
            specifications[12][1] == "tools/reproduce_owned_zig_source_build_v1.py"
            and specifications[12][2]
            == "53df4260eee56a143d2cd9134e5c0dc336b412758218c681f59acee0a8b8644e",
        )
        accept(
            "preserve-exact-frozen-v2-build-predecessor",
            specifications[13][1] == "tools/reproduce_owned_zig_source_build_v2.py"
            and specifications[13][2]
            == "e7a387c2281e44e67ea8e1258d00ec4e46e70fe475f1ac2e3c011953a30ed3a1",
        )
        accept(
            "independently-preserve-exact-frozen-v3-build-predecessor",
            checked_v3_predecessor(FROZEN_V3_PREDECESSOR)
            == (
                "frozen_v3_build_predecessor",
                "tools/reproduce_owned_zig_source_build_v3.py",
                "af5a04fccf179de8629c4d9470d20accbb126c8897d3d45d3fe041138d2abfc3",
                MAX_SOURCE_BYTES,
                None,
            ),
        )

        label = checked_label("zig-source-build-v4-synthetic-01")
        accept(
            "one-fresh-exact-v4-publication-label",
            label == "zig-source-build-v4-synthetic-01",
        )
        workdir = checked_workdir("/tmp/" + WORK_PREFIX + "synthetic01")
        commands = planned_commands(workdir)
        accept(
            "seven-exact-shell-free-owned-build-and-elf-commands",
            len(commands) == 7
            and all(
                checked_command(name, argv, workdir) == argv
                for name, argv in commands.items()
            ),
        )
        accept(
            "invoke-only-pinned-host-c-compiler-and-elf-inspector",
            commands["build_python_bridge"][0] == PINNED_HOST_CC
            and all(
                commands[name][0] == PINNED_HOST_READELF
                for name in (
                    "engine_dynamic",
                    "bridge_dynamic",
                    "engine_symbols",
                    "bridge_symbols",
                )
            ),
        )
        accept(
            "build-only-explicitly-owned-current-bridge-source",
            str(ROOT / OWNED_BRIDGE_RELATIVE)
            in commands["build_python_bridge"],
        )
        accept(
            "build-only-frozen-from-scratch-zig-engine-source",
            str(ROOT / "candidates/zig/mini_regex.zig")
            in commands["build_zig_engine"],
        )
        accept(
            "fresh-private-local-and-global-zig-caches",
            "--cache-dir" in commands["build_zig_engine"]
            and "--global-cache-dir" in commands["build_zig_engine"],
        )
        accept(
            "only-approved-host-python-undefined-zig-symbols",
            "-fallow-shlib-undefined" in commands["build_zig_engine"],
        )
        accept(
            "literal-owned-origin-only-bridge-runpath",
            "-Wl,-rpath,$ORIGIN" in commands["build_python_bridge"],
        )
        accept(
            "never-replace-existing-candidate-native-binaries",
            commands["build_zig_engine"][-1].startswith(
                "-femit-bin=/tmp/" + WORK_PREFIX,
            )
            and commands["build_python_bridge"][-1].startswith(
                "/tmp/" + WORK_PREFIX,
            ),
        )

        good_engine = dynamic_metadata(
            "0 (NEEDED) Shared library: [libc.so.6]\n"
            "0 (SONAME) Library soname: [_zig_probe.so]\n",
        )
        good_bridge = dynamic_metadata(
            "0 (NEEDED) Shared library: [_zig_probe.so]\n"
            "0 (NEEDED) Shared library: [libc.so.6]\n"
            "0 (RUNPATH) Library runpath: [$ORIGIN]\n",
        )
        good_engine_symbols = set(REQUIRED_ENGINE_EXPORTS)
        good_engine_undefined = set(ALLOWED_ENGINE_UNDEFINED)
        good_bridge_symbols = {"PyInit__zig_bridge"}
        good_bridge_undefined = set(REQUIRED_BRIDGE_ENGINE_REFERENCES)
        good_bridge_undefined.add("PyExc_RuntimeError")
        good_elf = validate_elf(
            good_engine,
            good_bridge,
            good_engine_symbols,
            good_engine_undefined,
            good_bridge_symbols,
            good_bridge_undefined,
        )
        accept(
            "synthetic-owned-elf-soname-origin-symbols-and-engine",
            good_elf["required_owned_engine_exports_present"]
            and good_elf["forbidden_native_symbols"] == [],
        )
        poisoned_exports, poisoned_undefined = dynamic_symbols(
            "  7: 0000000000000000 0 FUNC GLOBAL DEFAULT UND "
            "dlopen@GLIBC_2.34 (3)\n",
        )
        accept(
            "parse-versioned-forbidden-native-symbol-name",
            poisoned_exports == set() and poisoned_undefined == {"dlopen"},
        )

        for index, invalid in enumerate((
            None,
            True,
            1,
            "",
            "a" * 63,
            "A" * 64,
            "g" * 64,
            "../" + "a" * 61,
            "a" * 65,
        )):
            reject(
                "reject-forged-sha256-" + format(index, "02d"),
                lambda invalid=invalid: checked_digest(invalid, "synthetic"),
            )

        invalid_pin_lists: tuple[Any, ...] = (
            None,
            True,
            (),
            [],
            [pin_arguments[0]],
            [pin_arguments[1]],
            [pin_arguments[0], pin_arguments[0]],
            [pin_arguments[1], pin_arguments[1]],
            pin_arguments + ["candidates/other.py=" + "3" * 64],
            [OWNED_BRIDGE_RELATIVE + "=" + bridge_pin, "candidates/other.py=" + adapter_pin],
            [OWNED_BRIDGE_RELATIVE + "=" + bridge_pin, OWNED_ADAPTER_RELATIVE],
            [OWNED_BRIDGE_RELATIVE + "==" + bridge_pin, pin_arguments[1]],
            [OWNED_BRIDGE_RELATIVE + "=" + "A" * 64, pin_arguments[1]],
            [OWNED_BRIDGE_RELATIVE + "=" + bridge_pin, OWNED_ADAPTER_RELATIVE + "=" + bridge_pin],
            ["../" + OWNED_BRIDGE_RELATIVE + "=" + bridge_pin, pin_arguments[1]],
        )
        for index, invalid in enumerate(invalid_pin_lists):
            reject(
                "reject-missing-duplicate-extra-or-forged-owned-pin-"
                + format(index, "02d"),
                lambda invalid=invalid: checked_owned_source_pins(invalid),
            )

        for index, invalid in enumerate((
            None,
            True,
            1,
            "",
            "../zig-source-build-v4-x",
            "zig-source-build-v4-../x",
            "zig-source-build-v4-X",
            "zig-source-build-v4-a/b",
            "zig-source-build-v4-a--b",
            "zig-source-build-v4-",
            "zig-source-build-v3-synthetic-01",
        )):
            reject(
                "reject-unsafe-stale-or-non-v4-publication-label-"
                + format(index, "02d"),
                lambda invalid=invalid: checked_label(invalid),
            )

        for index, invalid in enumerate((
            None,
            True,
            1,
            "",
            "/",
            "/tmp",
            "/tmp/../tmp/" + WORK_PREFIX + "x",
            "/tmp/" + WORK_PREFIX + "x/child",
            str(ROOT),
            str(ROOT / "candidates"),
            "/tmp/rebar-owned-zig-source-build-v3-synthetic01",
        )):
            reject(
                "reject-unsafe-stale-or-non-v4-build-directory-"
                + format(index, "02d"),
                lambda invalid=invalid: checked_workdir(invalid),
            )

        for index, specification in enumerate(specifications):
            name, location, digest, maximum, exact_size = specification
            changed_digest = ("0" if digest[0] != "0" else "1") + digest[1:]
            for variation, forged in (
                ("digest", (name, location, changed_digest, maximum, exact_size)),
                ("path", (name, "../" + location, digest, maximum, exact_size)),
                ("maximum", (name, location, digest, maximum + 1, exact_size)),
                (
                    "exact-size",
                    (
                        name,
                        location,
                        digest,
                        maximum,
                        1 if exact_size is None else exact_size + 1,
                    ),
                ),
            ):
                reject(
                    "reject-forged-"
                    + name
                    + "-"
                    + variation
                    + "-"
                    + format(index, "02d"),
                    lambda forged=forged: checked_input(forged, specifications),
                )

        reject(
            "reject-stale-v3-historical-bridge-against-current-caller-pin",
            lambda: checked_input(
                (
                    "zig_bridge_source",
                    OWNED_BRIDGE_RELATIVE,
                    "f4900d04734a7c02bd766aee81c1d64114803dbefcf6f4591bfb667262658fea",
                    MAX_SOURCE_BYTES,
                    None,
                ),
                specifications,
            ),
        )
        reject(
            "reject-stale-v3-historical-adapter-against-current-caller-pin",
            lambda: checked_input(
                (
                    "zig_python_adapter",
                    OWNED_ADAPTER_RELATIVE,
                    "66d9f98cabeeb1e00f16880534e817b0e79075b8afd97ea86c9e2ab08d2682c1",
                    MAX_SOURCE_BYTES,
                    None,
                ),
                specifications,
            ),
        )
        reject(
            "reject-stale-v4-original-correctness-oracle",
            lambda: checked_input(
                (
                    "frozen_original_correctness_oracle",
                    "tools/independent_original_cpython_suite_v4.py",
                    "1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3",
                    MAX_SOURCE_BYTES,
                    None,
                ),
                specifications,
            ),
        )

        compiler = specifications[7]
        for variation, forged in (
            (
                "old-128-mib-compiler-limit",
                (
                    compiler[0],
                    compiler[1],
                    compiler[2],
                    MAX_BINARY_BYTES,
                    ZIG_COMPILER_SIZE,
                ),
            ),
            (
                "compiler-one-byte-too-small",
                (
                    compiler[0],
                    compiler[1],
                    compiler[2],
                    compiler[3],
                    ZIG_COMPILER_SIZE - 1,
                ),
            ),
            (
                "compiler-one-byte-too-large",
                (
                    compiler[0],
                    compiler[1],
                    compiler[2],
                    compiler[3],
                    ZIG_COMPILER_SIZE + 1,
                ),
            ),
            (
                "compiler-without-exact-size",
                (compiler[0], compiler[1], compiler[2], compiler[3], None),
            ),
            (
                "compiler-bound-too-small",
                (
                    compiler[0],
                    compiler[1],
                    compiler[2],
                    ZIG_COMPILER_SIZE - 1,
                    ZIG_COMPILER_SIZE,
                ),
            ),
            (
                "compiler-bound-too-large",
                (
                    compiler[0],
                    compiler[1],
                    compiler[2],
                    MAX_OFFICIAL_COMPILER_BYTES + 1,
                    ZIG_COMPILER_SIZE,
                ),
            ),
        ):
            reject(
                "reject-" + variation,
                lambda forged=forged: checked_input(forged, specifications),
            )

        for index, specification in enumerate(specifications):
            if specification[0] == "official_zig_compiler":
                continue
            name, location, digest, _, exact_size = specification
            reject(
                "reject-compiler-only-256-mib-bound-on-"
                + name
                + "-"
                + format(index, "02d"),
                lambda name=name, location=location, digest=digest,
                exact_size=exact_size: checked_input(
                    (
                        name,
                        location,
                        digest,
                        MAX_OFFICIAL_COMPILER_BYTES,
                        exact_size,
                    ),
                    specifications,
                ),
            )

        name, location, digest, maximum, exact_size = FROZEN_V3_PREDECESSOR
        for variation, forged in (
            ("digest", (name, location, "0" + digest[1:], maximum, exact_size)),
            ("path", (name, "../" + location, digest, maximum, exact_size)),
            ("maximum", (name, location, digest, maximum + 1, exact_size)),
            ("exact-size", (name, location, digest, maximum, 1)),
        ):
            reject(
                "reject-forged-independent-v3-predecessor-" + variation,
                lambda forged=forged: checked_v3_predecessor(forged),
            )

        for index, name in enumerate(commands):
            substituted = list(commands[name])
            substituted[0] = "/bin/sh"
            reject(
                "reject-substituted-shell-compiler-or-elf-command-"
                + format(index, "02d"),
                lambda name=name, substituted=substituted: checked_command(
                    name,
                    substituted,
                    workdir,
                ),
            )
            extended = list(commands[name]) + ["--unapproved-extra-argument"]
            reject(
                "reject-extra-unfrozen-build-or-elf-argument-"
                + format(index, "02d"),
                lambda name=name, extended=extended: checked_command(
                    name,
                    extended,
                    workdir,
                ),
            )

        poisoned_engine = dict(good_engine)
        poisoned_engine["needed"] = ["libpcre2-8.so.0"]
        reject(
            "reject-external-regex-shared-library",
            lambda: validate_elf(
                poisoned_engine,
                good_bridge,
                good_engine_symbols,
                good_engine_undefined,
                good_bridge_symbols,
                good_bridge_undefined,
            ),
        )
        poisoned_bridge = dict(good_bridge)
        poisoned_bridge["runpath"] = ["/usr/lib"]
        reject(
            "reject-non-origin-external-bridge-runpath",
            lambda: validate_elf(
                good_engine,
                poisoned_bridge,
                good_engine_symbols,
                good_engine_undefined,
                good_bridge_symbols,
                good_bridge_undefined,
            ),
        )
        borrowed_bridge = dict(good_bridge)
        borrowed_bridge["needed"] = ["_rust_engine.so"]
        reject(
            "reject-borrowed-independent-rust-family-engine",
            lambda: validate_elf(
                good_engine,
                borrowed_bridge,
                good_engine_symbols,
                good_engine_undefined,
                good_bridge_symbols,
                good_bridge_undefined,
            ),
        )
        reject(
            "reject-missing-owned-zig-engine-export",
            lambda: validate_elf(
                good_engine,
                good_bridge,
                good_engine_symbols - {"rebar_zig_compile"},
                good_engine_undefined,
                good_bridge_symbols,
                good_bridge_undefined,
            ),
        )
        reject(
            "reject-unapproved-native-cpython-importer-symbol",
            lambda: validate_elf(
                good_engine,
                good_bridge,
                good_engine_symbols,
                good_engine_undefined | {"_PyImport_FindExtensionObject"},
                good_bridge_symbols,
                good_bridge_undefined,
            ),
        )
        reject(
            "reject-missing-exact-cpython-bridge-initializer",
            lambda: validate_elf(
                good_engine,
                good_bridge,
                good_engine_symbols,
                good_engine_undefined,
                set(),
                good_bridge_undefined,
            ),
        )
        reject(
            "reject-missing-owned-bridge-engine-reference",
            lambda: validate_elf(
                good_engine,
                good_bridge,
                good_engine_symbols,
                good_engine_undefined,
                good_bridge_symbols,
                good_bridge_undefined - {"rebar_zig_compile"},
            ),
        )
        reject(
            "reject-versioned-forbidden-native-dynamic-loader",
            lambda: validate_elf(
                good_engine,
                good_bridge,
                good_engine_symbols,
                good_engine_undefined,
                good_bridge_symbols,
                good_bridge_undefined | poisoned_undefined,
            ),
        )

        reject(
            "block-real-owned-source-open",
            lambda: builtins.open(OWNED_BRIDGE_RELATIVE, "rb"),
            SourceOnlyError,
        )
        reject(
            "block-real-pathlib-owned-source-read",
            lambda: Path(OWNED_ADAPTER_RELATIVE).read_bytes(),
            SourceOnlyError,
        )
        reject(
            "block-real-owned-source-stat",
            lambda: os.stat("candidates/zig/mini_regex.zig"),
            SourceOnlyError,
        )
        reject(
            "block-real-official-compiler-authentication",
            lambda: authenticate_frozen_input(specifications[7], specifications),
            SourceOnlyError,
        )
        reject(
            "block-real-frozen-v3-predecessor-authentication",
            authenticate_v3_predecessor,
            SourceOnlyError,
        )
        reject(
            "block-real-build-evidence-directory",
            open_evidence_directory,
            SourceOnlyError,
        )
        reject(
            "block-real-native-compiler-process",
            lambda: subprocess.run([ZIG_COMPILER, "version"]),
            SourceOnlyError,
        )
        reject(
            "block-real-external-subprocess-worker",
            lambda: subprocess.Popen([ZIG_COMPILER, "version"]),
            SourceOnlyError,
        )
        reject(
            "block-real-zig-candidate-import",
            lambda: importlib.import_module("candidates.zig_candidate"),
            SourceOnlyError,
        )
        reject(
            "block-real-fresh-build-directory",
            lambda: tempfile.mkdtemp(prefix=WORK_PREFIX, dir="/tmp"),
            SourceOnlyError,
        )
        reject(
            "block-real-background-candidate-worker",
            lambda: threading.Thread(target=lambda: None).start(),
            SourceOnlyError,
        )
        reject(
            "block-real-network-connection",
            lambda: socket.create_connection(("127.0.0.1", 1)),
            SourceOnlyError,
        )
        reject(
            "block-real-random-sample",
            lambda: os.urandom(12),
            SourceOnlyError,
        )
        reject(
            "block-real-high-resolution-clock-sample",
            time.perf_counter_ns,
            SourceOnlyError,
        )
        reject(
            "block-real-wall-clock-sample",
            time.time,
            SourceOnlyError,
        )
        accept(
            "zero-actual-source-evidence-build-network-worker-clock-or-random-effects",
            all(amount == 0 for amount in sandbox.counts.values()),
        )
        accept(
            "every-forbidden-real-effect-is-independently-exercised",
            all(amount > 0 for amount in sandbox.blocked.values()),
        )
        actual = dict(sandbox.counts)
        blocked = dict(sandbox.blocked)

    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "frozen_input_count": len(specifications),
        "additional_frozen_v3_predecessor_count": 1,
        "explicit_owned_source_pin_count": len(pins),
        "synthetic_owned_c_bridge_source_sha256": bridge_pin,
        "synthetic_owned_python_adapter_source_sha256": adapter_pin,
        "official_zig_version": ZIG_VERSION,
        "official_zig_archive_sha256": specifications[6][2],
        "official_zig_archive_size_bytes": ZIG_ARCHIVE_SIZE,
        "official_zig_compiler_sha256": specifications[7][2],
        "official_zig_compiler_size_bytes": ZIG_COMPILER_SIZE,
        "official_zig_compiler_maximum_bytes": MAX_OFFICIAL_COMPILER_BYTES,
        "other_native_artifacts_maximum_bytes": MAX_BINARY_BYTES,
        "source_input_maximum_bytes": MAX_SOURCE_BYTES,
        "complete_process_output_maximum_bytes": MAX_PROCESS_BYTES,
        "pinned_host_c_compiler_sha256": specifications[10][2],
        "pinned_host_readelf_sha256": specifications[11][2],
        "owned_zig_engine_source_sha256": specifications[1][2],
        "frozen_original_correctness_oracle_sha256": specifications[4][2],
        "frozen_from_scratch_audit_sha256": specifications[5][2],
        "frozen_build_protocol_sha256": specifications[0][2],
        "frozen_v1_build_predecessor_sha256": specifications[12][2],
        "frozen_v2_build_predecessor_sha256": specifications[13][2],
        "frozen_v3_build_predecessor_sha256": FROZEN_V3_PREDECESSOR[2],
        "actual_external_effects": actual,
        "actual_blocked_effect_attempts": blocked,
        "accepted_control_count": len(accepted),
        "accepted_controls": accepted,
        "rejected_control_count": len(rejected),
        "rejected_controls": rejected,
        "actual_compiler_processes": 0,
        "actual_native_outputs": 0,
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_network_accesses": 0,
        "actual_random_samples": 0,
        "actual_clock_samples": 0,
        "source_build_status": "NOT MEASURED",
        "binary_reproduction_status": "NOT MEASURED",
        "candidate_correctness_status": "NOT MEASURED",
        "candidate_performance_status": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
    }


def run_build(
    label: str,
    source_pin: str,
    owned_source_arguments: list[str],
) -> tuple[dict[str, Any], int]:
    checked_label(label)
    checked_digest(source_pin, "frozen owned Zig V4 build controller")
    pins = checked_owned_source_pins(owned_source_arguments)
    specifications = frozen_inputs(pins)
    require(
        sys.executable == PINNED_PYTHON and sys.version_info[:3] == (3, 14, 6),
        "run an actual Zig source build only with exact pinned CPython 3.14.6",
    )
    evidence_directory = open_evidence_directory()
    try:
        report_name, receipt_name = require_fresh_publications(
            evidence_directory,
            label,
        )
        document: dict[str, Any] = {
            "schema": SCHEMA + "-complete-source-build",
            "status": "FAIL",
            "label": label,
            "controller_source_sha256": source_pin,
            "explicit_owned_source_sha256": dict(sorted(pins.items())),
            "frozen_input_count": len(specifications),
            "additional_frozen_v3_predecessor_count": 1,
            "official_zig_version": ZIG_VERSION,
            "official_zig_compiler_exact_size_bytes": ZIG_COMPILER_SIZE,
            "official_zig_compiler_maximum_bytes": MAX_OFFICIAL_COMPILER_BYTES,
            "other_native_artifacts_maximum_bytes": MAX_BINARY_BYTES,
            "pinned_python": PINNED_PYTHON,
            "pinned_python_include": PYTHON_INCLUDE,
            "pinned_extension_suffix": EXTENSION_SUFFIX,
            "authenticated_inputs": {},
            "fresh_private_work_directory": None,
            "processes": [],
            "fresh_outputs": {},
            "elf": None,
            "source_inputs_reauthenticated": {},
            "all_frozen_inputs_reauthenticated": {},
            "failure": None,
            "existing_candidates_modified": False,
            "historical_binary_equality": "NOT MEASURED",
            "candidate_correctness_status": "NOT MEASURED",
            "candidate_performance_status": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
        }
        try:
            document["authenticated_inputs"]["build_controller"] = authenticate_path(
                ROOT / SOURCE_RELATIVE,
                expected=source_pin,
                maximum=MAX_SOURCE_BYTES,
            )
            for specification in specifications:
                name, observed = authenticate_frozen_input(
                    specification,
                    specifications,
                )
                document["authenticated_inputs"][name] = observed
            predecessor_name, predecessor = authenticate_v3_predecessor()
            document["authenticated_inputs"][predecessor_name] = predecessor
            require(
                os.path.realpath("/usr/bin/cc") == PINNED_HOST_CC,
                "the host C compiler no longer resolves to its frozen binary",
            )
            require(
                os.path.realpath("/usr/bin/readelf") == PINNED_HOST_READELF,
                "the host ELF inspector no longer resolves to its frozen binary",
            )
            workdir = checked_workdir(
                tempfile.mkdtemp(prefix=WORK_PREFIX, dir="/tmp"),
            )
            document["fresh_private_work_directory"] = workdir
            os.mkdir(str(Path(workdir) / "local-cache"), 0o700)
            os.mkdir(str(Path(workdir) / "global-cache"), 0o700)
            steps = document["processes"]
            version = run_process("compiler_version", workdir, steps)
            require(
                version["stdout"].strip() == ZIG_VERSION,
                "the authenticated official compiler reported another Zig version",
            )
            run_process("build_zig_engine", workdir, steps)
            engine_path = Path(workdir) / "_zig_probe.so"
            document["fresh_outputs"]["native_engine"] = authenticate_path(
                engine_path,
                expected=None,
                maximum=MAX_BINARY_BYTES,
            )
            run_process("build_python_bridge", workdir, steps)
            bridge_path = Path(workdir) / ("_zig_bridge" + EXTENSION_SUFFIX)
            document["fresh_outputs"]["native_bridge"] = authenticate_path(
                bridge_path,
                expected=None,
                maximum=MAX_BINARY_BYTES,
            )
            engine_dynamic = dynamic_metadata(
                run_process("engine_dynamic", workdir, steps)["stdout"],
            )
            bridge_dynamic = dynamic_metadata(
                run_process("bridge_dynamic", workdir, steps)["stdout"],
            )
            engine_symbols, engine_undefined = dynamic_symbols(
                run_process("engine_symbols", workdir, steps)["stdout"],
            )
            bridge_symbols, bridge_undefined = dynamic_symbols(
                run_process("bridge_symbols", workdir, steps)["stdout"],
            )
            document["elf"] = validate_elf(
                engine_dynamic,
                bridge_dynamic,
                engine_symbols,
                engine_undefined,
                bridge_symbols,
                bridge_undefined,
            )
            for specification in specifications[1:4]:
                name, observed = authenticate_frozen_input(
                    specification,
                    specifications,
                )
                require(
                    observed == document["authenticated_inputs"][name],
                    "an owned source changed during the isolated Zig build: " + name,
                )
                document["source_inputs_reauthenticated"][name] = observed
            for specification in specifications:
                name, observed = authenticate_frozen_input(
                    specification,
                    specifications,
                )
                require(
                    observed == document["authenticated_inputs"][name],
                    "a frozen input changed during the isolated Zig build: " + name,
                )
                document["all_frozen_inputs_reauthenticated"][name] = observed
            predecessor_name, predecessor_after = authenticate_v3_predecessor()
            require(
                predecessor_after == document["authenticated_inputs"][predecessor_name],
                "the exact frozen V3 build predecessor changed during the V4 build",
            )
            document["all_frozen_inputs_reauthenticated"][predecessor_name] = (
                predecessor_after
            )
            controller_after = authenticate_path(
                ROOT / SOURCE_RELATIVE,
                expected=source_pin,
                maximum=MAX_SOURCE_BYTES,
            )
            require(
                controller_after == document["authenticated_inputs"]["build_controller"],
                "the authenticated V4 controller changed during its actual build",
            )
            document["controller_reauthenticated"] = controller_after
            document["status"] = "PASS"
        except Exception as error:
            document["failure"] = {
                "type": type(error).__name__,
                "message": str(error),
            }
        report = publish_fresh(evidence_directory, report_name, document)
        receipt_document = {
            "schema": SCHEMA + "-fresh-publication-receipt",
            "status": "PASS",
            "build_status": document["status"],
            "label": label,
            "controller_source_sha256": source_pin,
            "explicit_owned_source_sha256": dict(sorted(pins.items())),
            "complete_report": report,
            "existing_candidates_modified": False,
            "candidate_correctness_status": "NOT MEASURED",
            "candidate_performance_status": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
        }
        receipt = publish_fresh(evidence_directory, receipt_name, receipt_document)
        return {
            "schema": SCHEMA + "-compact-publication-result",
            "status": document["status"],
            "label": label,
            "explicit_owned_source_sha256": dict(sorted(pins.items())),
            "complete_report": report,
            "publication_receipt": receipt,
            "failure": document["failure"],
            "fresh_private_work_directory": document["fresh_private_work_directory"],
            "candidate_correctness_status": "NOT MEASURED",
            "candidate_performance_status": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
        }, 0 if document["status"] == "PASS" else 1
    finally:
        os.close(evidence_directory)


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild the explicitly caller-pinned from-scratch Zig engine and "
            "Python bridge in an isolated directory without replacing a candidate"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--self-test",
        action="store_true",
        help="run only deterministic, side-effect-free synthetic source controls",
    )
    modes.add_argument(
        "--build",
        action="store_true",
        help="build isolated owned native outputs and publish the actual outcome",
    )
    parser.add_argument(
        "--label",
        help="one fresh zig-source-build-v4-* label; actual build only",
    )
    parser.add_argument(
        "--controller-source-sha256",
        help="exact frozen V4 controller SHA-256; actual build only",
    )
    parser.add_argument(
        "--owned-source-sha256",
        action="append",
        default=None,
        metavar="PATH=SHA256",
        help=(
            "exact caller-frozen source; provide once for "
            "candidates/zig/py_bridge.c and once for candidates/zig_candidate.py"
        ),
    )
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(
            options.label is None
            and options.controller_source_sha256 is None
            and options.owned_source_sha256 is None,
            "a synthetic self-test cannot request a source pin, build, or publication",
        )
        print(canonical(source_self_test()).decode("ascii"), end="")
        return 0
    require(
        options.label is not None
        and options.controller_source_sha256 is not None
        and options.owned_source_sha256 is not None,
        "an actual build requires a fresh label, controller hash, and both owned pins",
    )
    result, exit_status = run_build(
        options.label,
        options.controller_source_sha256,
        options.owned_source_sha256,
    )
    print(canonical(result).decode("ascii"), end="")
    return exit_status


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildError as error:
        print(
            canonical({
                "schema": SCHEMA + "-controller-failure",
                "status": "FAIL",
                "failure": {
                    "type": type(error).__name__,
                    "message": str(error),
                },
                "candidate_correctness_status": "NOT MEASURED",
                "candidate_performance_status": "NOT MEASURED",
                "candidate_qualified_for_hidden_benchmark": False,
            }).decode("ascii"),
            end="",
        )
        raise SystemExit(2) from None
