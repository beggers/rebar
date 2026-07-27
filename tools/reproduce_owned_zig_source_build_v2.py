#!/usr/bin/env python3
"""Freeze and, only on explicit request, rebuild the owned Zig engine.

The source self-test is synthetic: it neither reads nor writes files, starts a
process, loads a candidate, samples a clock, nor performs a build.  An actual
build authenticates all frozen inputs first and leaves both native outputs in a
fresh private directory under /tmp; it never replaces an existing candidate.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import hashlib
import importlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/reproduce_owned_zig_source_build_v2.py"
EVIDENCE_RELATIVE = "experiments/rust_public_practice_v1"
SCHEMA = "rebar-owned-zig-source-build-v2"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PYTHON_INCLUDE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
)
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
ZIG_VERSION = "0.16.0"
ZIG_COMPILER = "/tmp/zig-x86_64-linux-0.16.0/zig"
ZIG_ARCHIVE = "/tmp/rebar-zig-0.16.0-x86_64-linux.tar.xz"
PINNED_HOST_CC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_HOST_READELF = "/usr/bin/x86_64-linux-gnu-readelf"
ZIG_ARCHIVE_SIZE = 55_478_392
WORK_PREFIX = "rebar-owned-zig-source-build-v2-"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024

# Each path, hash, and byte limit is fixed before a real compiler can run.
FROZEN_INPUTS = (
    (
        "build_record",
        "docs/ZIG-SOURCE-BUILD-V1.md",
        "b2f0b0c85d28ace4593ba38cac95d731fb15f05e22de5b4ffcbc7d17d41efc49",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "zig_engine_source",
        "candidates/zig/mini_regex.zig",
        "539bf5d378e0c2845c01519fcce62f1ef5e68610f477912c44a03027fb67a346",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "zig_bridge_source",
        "candidates/zig/py_bridge.c",
        "f4900d04734a7c02bd766aee81c1d64114803dbefcf6f4591bfb667262658fea",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "zig_python_adapter",
        "candidates/zig_candidate.py",
        "66d9f98cabeeb1e00f16880534e817b0e79075b8afd97ea86c9e2ab08d2682c1",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "frozen_original_correctness_oracle",
        "tools/independent_original_cpython_suite_v5.py",
        "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "frozen_from_scratch_audit",
        "tools/independent_from_scratch_audit_v2.py",
        "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "official_zig_archive",
        ZIG_ARCHIVE,
        "70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00",
        MAX_BINARY_BYTES,
        ZIG_ARCHIVE_SIZE,
    ),
    (
        "official_zig_compiler",
        ZIG_COMPILER,
        "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c",
        MAX_BINARY_BYTES,
        None,
    ),
    (
        "pinned_python_header",
        PYTHON_INCLUDE + "/Python.h",
        "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "pinned_python_patchlevel",
        PYTHON_INCLUDE + "/patchlevel.h",
        "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95",
        MAX_SOURCE_BYTES,
        None,
    ),
    (
        "pinned_host_c_compiler",
        PINNED_HOST_CC,
        "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26",
        MAX_BINARY_BYTES,
        None,
    ),
    (
        "pinned_host_readelf",
        PINNED_HOST_READELF,
        "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0",
        MAX_BINARY_BYTES,
        None,
    ),
    (
        "frozen_build_predecessor",
        "tools/reproduce_owned_zig_source_build_v1.py",
        "53df4260eee56a143d2cd9134e5c0dc336b412758218c681f59acee0a8b8644e",
        MAX_SOURCE_BYTES,
        None,
    ),
)

REQUIRED_ENGINE_EXPORTS = frozenset(
    {
        "rebar_zig_batch",
        "rebar_zig_collect_captures",
        "rebar_zig_collect_records",
        "rebar_zig_collect_records_wide",
        "rebar_zig_compile",
        "rebar_zig_compile_guarded",
        "rebar_zig_flags",
        "rebar_zig_free",
        "rebar_zig_groups",
        "rebar_zig_match",
        "rebar_zig_match_captures",
        "rebar_zig_match_captures_wide",
        "rebar_zig_match_inverted_wide",
        "rebar_zig_match_nonempty_wide",
        "rebar_zig_match_tree",
        "rebar_zig_match_wide",
        "rebar_zig_name_copy",
        "rebar_zig_name_count",
        "rebar_zig_name_group",
        "rebar_zig_name_length",
        "rebar_zig_program_memory",
        "rebar_zig_program_size",
    }
)
ALLOWED_ENGINE_UNDEFINED = frozenset(
    {
        "_PyUnicode_IsAlpha",
        "_PyUnicode_IsDecimalDigit",
        "_PyUnicode_IsDigit",
        "_PyUnicode_IsNumeric",
        "_PyUnicode_IsWhitespace",
        "_PyUnicode_ToLowercase",
        "_PyUnicode_ToUppercase",
        "__gmon_start__",
        "free",
        "isalnum",
        "malloc",
        "malloc_usable_size",
        "memcpy",
        "memset",
        "posix_memalign",
        "realloc",
        "tolower",
    }
)
REQUIRED_BRIDGE_ENGINE_REFERENCES = frozenset(
    {
        "rebar_zig_collect_records_wide",
        "rebar_zig_compile",
        "rebar_zig_compile_guarded",
        "rebar_zig_flags",
        "rebar_zig_free",
        "rebar_zig_groups",
        "rebar_zig_match_captures_wide",
        "rebar_zig_match_inverted_wide",
        "rebar_zig_match_nonempty_wide",
        "rebar_zig_match_wide",
        "rebar_zig_name_copy",
        "rebar_zig_name_count",
        "rebar_zig_name_group",
        "rebar_zig_name_length",
    }
)
ALLOWED_BRIDGE_SYSTEM_UNDEFINED = frozenset(
    {
        "_ITM_deregisterTMCloneTable", "_ITM_registerTMCloneTable",
        "__assert_fail", "__ctype_b_loc", "__ctype_tolower_loc",
        "__cxa_finalize", "__gmon_start__", "__memcpy_chk",
        "__stack_chk_fail", "bcmp", "calloc", "free", "malloc",
        "memchr", "memcmp", "memcpy", "memmem", "memmove", "memset",
        "realloc", "strlen",
    }
)
FORBIDDEN_NATIVE_SYMBOLS = frozenset(
    {
        "dlmopen", "dlopen", "dlsym", "dlvsym", "execv", "execve",
        "fork", "popen", "posix_spawn", "regcomp", "regexec",
        "regfree", "system", "PyRun_AnyFile", "PyRun_SimpleString",
        "PyRun_String", "Py_CompileString", "PyEval_EvalCode",
    }
)
FORBIDDEN_NATIVE_PREFIXES = (
    "_PyImport_", "_PyRun_", "PyInit__sre", "PyImport_ExecCode",
    "PyImport_Import", "PyRun_", "Py_CompileString", "PyEval_Eval",
    "hs_", "onig_", "pcre2_", "pcre_", "re2_", "regex_", "sre_",
)
ALLOWED_SYSTEM_NEEDED = frozenset(
    {"libc.so.6", "libm.so.6", "libgcc_s.so.1"}
)


class BuildError(Exception):
    """An owned input, compiler invocation, or fresh output is untrustworthy."""


class SourceOnlyError(BuildError):
    """A synthetic control attempted a real external side effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise BuildError(message)


def canonical(value: Any) -> bytes:
    return (
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
        + b"\n"
    )


def valid_digest(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def checked_digest(value: Any, description: str) -> str:
    require(valid_digest(value), "an exact lowercase SHA-256 is required: " + description)
    return value


def checked_label(value: Any) -> str:
    require(
        type(value) is str
        and 21 <= len(value) <= 100
        and value.startswith("zig-source-build-v2-")
        and all(character in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in value)
        and not value.endswith("-")
        and "--" not in value,
        "use one fresh, bounded zig-source-build-v2-* publication label",
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


def checked_input(spec: Any) -> tuple[str, str, str, int, int | None]:
    require(
        type(spec) is tuple and len(spec) == 5 and spec in FROZEN_INPUTS,
        "only an exact prospectively frozen Zig build input may be read",
    )
    name, location, expected, maximum, exact_size = spec
    require(type(name) is str and valid_digest(expected), "the frozen input pin was forged")
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES, "the frozen size bound was forged")
    require(
        exact_size is None or type(exact_size) is int and 0 < exact_size <= maximum,
        "the exact official archive size was forged",
    )
    path = Path(location)
    if path.is_absolute():
        require(
            location in {
                ZIG_ARCHIVE, ZIG_COMPILER, PYTHON_INCLUDE + "/Python.h",
                PYTHON_INCLUDE + "/patchlevel.h", PINNED_HOST_CC,
                PINNED_HOST_READELF,
            },
            "a frozen toolchain input escaped its exact absolute path",
        )
    else:
        require(
            location == str(path)
            and path.parts
            and not any(part in ("", ".", "..") for part in path.parts)
            and path.parts[0] in {"candidates", "docs", "tools"},
            "an owned source input escaped its exact repository path",
        )
    return name, location, expected, maximum, exact_size


def authenticate_path(
    path: Path, *, expected: str | None, maximum: int, exact_size: int | None = None,
) -> dict[str, Any]:
    require(path.is_absolute(), "authenticate only an exact absolute native input")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(path), flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode), "an authenticated input is not a real regular file")
        require(0 <= before.st_size <= maximum, "an authenticated input exceeded its frozen size bound")
        if exact_size is not None:
            require(before.st_size == exact_size, "the official Zig archive has the wrong exact size")
        hasher = hashlib.sha256()
        actual_size = 0
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            actual_size += len(chunk)
            require(actual_size <= maximum, "an authenticated input grew while it was read")
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
            "an authenticated input path was replaced or redirected",
        )
        actual = hasher.hexdigest()
        if expected is not None:
            require(actual == checked_digest(expected, str(path)), "a frozen source or compiler SHA-256 changed: " + str(path))
        return {"path": str(path), "sha256": actual, "size_bytes": actual_size}
    finally:
        os.close(descriptor)


def authenticate_frozen_input(spec: Any) -> tuple[str, dict[str, Any]]:
    name, location, expected, maximum, exact_size = checked_input(spec)
    path = Path(location) if Path(location).is_absolute() else ROOT / location
    return name, authenticate_path(path, expected=expected, maximum=maximum, exact_size=exact_size)


def planned_commands(workdir: str) -> dict[str, list[str]]:
    base = Path(checked_workdir(workdir))
    engine = base / "_zig_probe.so"
    bridge = base / ("_zig_bridge" + EXTENSION_SUFFIX)
    return {
        "compiler_version": [ZIG_COMPILER, "version"],
        "build_zig_engine": [
            ZIG_COMPILER, "build-lib", str(ROOT / "candidates/zig/mini_regex.zig"),
            "-dynamic", "-lc", "-O", "ReleaseFast",
            "-fallow-shlib-undefined", "-fsoname=_zig_probe.so",
            "--cache-dir", str(base / "local-cache"),
            "--global-cache-dir", str(base / "global-cache"),
            "-femit-bin=" + str(engine),
        ],
        "build_python_bridge": [
            PINNED_HOST_CC, "-shared", "-fPIC", "-O3", "-I" + PYTHON_INCLUDE,
            str(ROOT / "candidates/zig/py_bridge.c"), str(engine),
            "-Wl,-rpath,$ORIGIN", "-o", str(bridge),
        ],
        "engine_dynamic": [PINNED_HOST_READELF, "--dynamic", "--wide", str(engine)],
        "bridge_dynamic": [PINNED_HOST_READELF, "--dynamic", "--wide", str(bridge)],
        "engine_symbols": [PINNED_HOST_READELF, "--dyn-syms", "--wide", str(engine)],
        "bridge_symbols": [PINNED_HOST_READELF, "--dyn-syms", "--wide", str(bridge)],
    }


def checked_command(name: Any, argv: Any, workdir: str) -> list[str]:
    planned = planned_commands(workdir)
    require(
        type(name) is str and name in planned and type(argv) is list
        and all(type(item) is str and "\x00" not in item for item in argv)
        and argv == planned[name],
        "only the exact frozen shell-free owned Zig build command may run",
    )
    return list(argv)


def sanitize_command(argv: list[str], workdir: str) -> list[str]:
    prefix = checked_workdir(workdir)
    return [item.replace(prefix, "<FRESH_PRIVATE_TMP>") for item in argv]


def run_process(name: str, workdir: str, steps: list[dict[str, Any]]) -> dict[str, Any]:
    argv = checked_command(name, planned_commands(workdir)[name], workdir)
    entry: dict[str, Any] = {
        "name": name,
        "argv": sanitize_command(argv, workdir),
        "shell": False,
        "stdout": "",
        "stderr": "",
        "stdout_base64": "",
        "stderr_base64": "",
        "stdout_sha256": hashlib.sha256(b"").hexdigest(),
        "stderr_sha256": hashlib.sha256(b"").hexdigest(),
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
            "complete genuine compiler output exceeded its frozen size bound",
        )
        entry["stdout_base64"] = base64.b64encode(completed.stdout).decode("ascii")
        entry["stderr_base64"] = base64.b64encode(completed.stderr).decode("ascii")
        entry["stdout_sha256"] = hashlib.sha256(completed.stdout).hexdigest()
        entry["stderr_sha256"] = hashlib.sha256(completed.stderr).hexdigest()
        entry["stdout"] = completed.stdout.decode("utf-8", "backslashreplace")
        entry["stderr"] = completed.stderr.decode("utf-8", "backslashreplace")
        require(completed.returncode == 0, "the genuine owned build command failed: " + name)
    except Exception as error:
        entry["exception_type"] = type(error).__name__
        entry["exception_message"] = str(error)
        raise
    return entry


def dynamic_metadata(output: str) -> dict[str, Any]:
    require(type(output) is str, "genuine complete ELF dynamic output is mandatory")
    needed: list[str] = []
    soname: list[str] = []
    runpath: list[str] = []
    rpath: list[str] = []
    for line in output.splitlines():
        opening = line.find("[")
        closing = line.find("]", opening + 1)
        if opening < 0 or closing < opening:
            continue
        value = line[opening + 1:closing]
        if "(NEEDED)" in line:
            needed.append(value)
        elif "(SONAME)" in line:
            soname.append(value)
        elif "(RUNPATH)" in line:
            runpath.append(value)
        elif "(RPATH)" in line:
            rpath.append(value)
    return {"needed": needed, "soname": soname, "runpath": runpath, "rpath": rpath}


def dynamic_symbols(output: str) -> tuple[set[str], set[str]]:
    require(type(output) is str, "genuine complete ELF dynamic symbol output is mandatory")
    exported: set[str] = set()
    undefined: set[str] = set()
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 8 and parts[0].rstrip(":").isdigit():
            name = parts[7].split("@", 1)[0]
            if parts[6] == "UND":
                require(name not in undefined, "a native undefined dynamic symbol was duplicated")
                undefined.add(name)
            elif parts[4] in {"GLOBAL", "WEAK"}:
                require(name not in exported, "an owned public dynamic export was duplicated")
                exported.add(name)
    return exported, undefined


def validate_elf(
    engine: Any, bridge: Any, engine_symbols: Any, engine_undefined: Any,
    bridge_symbols: Any, bridge_undefined: Any,
) -> dict[str, Any]:
    require(type(engine) is dict and type(bridge) is dict, "both actual native ELF records are mandatory")
    require(
        engine.get("soname") == ["_zig_probe.so"]
        and not engine.get("rpath")
        and not engine.get("runpath")
        and set(engine.get("needed", ())).issubset(ALLOWED_SYSTEM_NEEDED),
        "the fresh Zig engine has a foreign dependency, path, or SONAME",
    )
    require(
        bridge.get("runpath") == ["$ORIGIN"]
        and not bridge.get("rpath")
        and "_zig_probe.so" in bridge.get("needed", ())
        and set(bridge.get("needed", ())).issubset(ALLOWED_SYSTEM_NEEDED | {"_zig_probe.so"}),
        "the fresh Python bridge does not bind solely to its adjacent owned Zig engine",
    )
    require(
        all(type(value) is set for value in (
            engine_symbols, engine_undefined, bridge_symbols, bridge_undefined,
        )),
        "both genuine defined and undefined native ELF symbol sets are mandatory",
    )
    require(
        engine_symbols == REQUIRED_ENGINE_EXPORTS,
        "the fresh source-built Zig engine does not export its exact 22 owned matching symbols",
    )
    require(
        engine_undefined == ALLOWED_ENGINE_UNDEFINED,
        "the fresh Zig engine does not use exactly its audited CPython Unicode and libc symbols",
    )
    require(
        bridge_symbols == {"PyInit__zig_bridge"},
        "the fresh Python bridge does not export its sole exact CPython initialization symbol",
    )
    require(
        bridge_undefined & REQUIRED_ENGINE_EXPORTS == REQUIRED_BRIDGE_ENGINE_REFERENCES,
        "the fresh Python bridge does not reference exactly its own Zig matching engine",
    )
    unexpected_bridge = {
        name for name in bridge_undefined
        if name not in REQUIRED_ENGINE_EXPORTS
        and name not in ALLOWED_BRIDGE_SYSTEM_UNDEFINED
        and not name.startswith(("Py", "_Py"))
    }
    require(not unexpected_bridge, "the fresh Python bridge resolves an unapproved foreign symbol")
    all_symbols = engine_symbols | engine_undefined | bridge_symbols | bridge_undefined
    forbidden = sorted(
        item for item in all_symbols
        if item in FORBIDDEN_NATIVE_SYMBOLS or item.startswith(FORBIDDEN_NATIVE_PREFIXES)
    )
    require(not forbidden, "the source-built native artifacts reference a forbidden external matcher or loader")
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
    path = ROOT / EVIDENCE_RELATIVE
    return os.open(
        str(path),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )


def require_fresh_publications(directory: int, label: str) -> tuple[str, str]:
    checked_label(label)
    names = (label + ".json", label + "-publication-receipt.json")
    for name in names:
        try:
            os.stat(name, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            continue
        raise BuildError("a fresh owned source-build publication already exists: " + name)
    return names


def publish_fresh(directory: int, name: str, document: dict[str, Any]) -> dict[str, Any]:
    require(type(name) is str and "/" not in name and name.endswith(".json"), "an atomic evidence filename escaped its owned directory")
    data = canonical(document)
    temporary = "." + name + "." + os.urandom(12).hex() + ".tmp"
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(temporary, flags, 0o600, dir_fd=directory)
    linked = False
    try:
        remaining = memoryview(data)
        while remaining:
            amount = os.write(descriptor, remaining)
            require(amount > 0, "atomic evidence publication stopped before its complete document")
            remaining = remaining[amount:]
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        os.link(temporary, name, src_dir_fd=directory, dst_dir_fd=directory, follow_symlinks=False)
        linked = True
        os.fsync(directory)
        read_descriptor = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory,
        )
        try:
            actual = bytearray()
            while True:
                chunk = os.read(read_descriptor, 1024 * 1024)
                if not chunk:
                    break
                actual.extend(chunk)
                require(len(actual) <= MAX_PROCESS_BYTES, "fresh evidence readback exceeded its bound")
        finally:
            os.close(read_descriptor)
        require(bytes(actual) == data, "fresh atomic evidence failed its complete independent readback")
        return {"relative": EVIDENCE_RELATIVE + "/" + name, "sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data)}
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass


class SyntheticSandbox:
    """Reject and count real effects during a pure source self-test."""

    def __init__(self) -> None:
        self.counts = {
            "filesystem_reads": 0,
            "filesystem_writes": 0,
            "processes": 0,
            "candidate_imports": 0,
            "threads": 0,
            "clock_samples": 0,
        }
        self.blocked: dict[str, int] = {name: 0 for name in self.counts}
        self.originals: list[tuple[Any, str, Any]] = []

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def blocked(*args: Any, **kwargs: Any) -> Any:
            self.blocked[category] += 1
            raise SourceOnlyError("source-only Zig controls forbid " + category + ": " + name)

        self.originals.append((owner, name, original))
        setattr(owner, name, blocked)

    def __enter__(self) -> SyntheticSandbox:
        for owner, name, category in (
            (builtins, "open", "filesystem_reads"),
            (os, "open", "filesystem_reads"),
            (os, "read", "filesystem_reads"),
            (os, "stat", "filesystem_reads"),
            (os, "lstat", "filesystem_reads"),
            (os, "listdir", "filesystem_reads"),
            (os, "scandir", "filesystem_reads"),
            (os, "write", "filesystem_writes"),
            (os, "mkdir", "filesystem_writes"),
            (os, "unlink", "filesystem_writes"),
            (os, "replace", "filesystem_writes"),
            (os, "link", "filesystem_writes"),
            (tempfile, "mkdtemp", "filesystem_writes"),
            (subprocess, "run", "processes"),
            (subprocess, "Popen", "processes"),
            (os, "system", "processes"),
            (os, "fork", "processes"),
            (importlib, "import_module", "candidate_imports"),
            (threading.Thread, "start", "threads"),
            (time, "time", "clock_samples"),
            (time, "monotonic", "clock_samples"),
            (time, "perf_counter", "clock_samples"),
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
        require(condition, "a genuine synthetic build control was rejected: " + name)
        accepted.append(name)

    def reject(name: str, action: Any, error_type: type[Exception] = BuildError) -> None:
        try:
            action()
        except error_type:
            rejected.append(name)
        else:
            raise BuildError("a forged or unsafe synthetic build control was accepted: " + name)

    with SyntheticSandbox() as sandbox:
        accept("all-thirteen-prospectively-frozen-input-specifications", len(FROZEN_INPUTS) == 13)
        accept("each-frozen-source-and-official-toolchain-pin", all(checked_input(spec) == spec for spec in FROZEN_INPUTS))
        accept("exact-official-archive-size", ZIG_ARCHIVE_SIZE == 55_478_392)
        accept("exact-cpython-extension-suffix", EXTENSION_SUFFIX == ".cpython-314-x86_64-linux-gnu.so")
        accept(
            "exact-resolved-host-c-compiler-and-readelf-pins",
            FROZEN_INPUTS[10][1] == PINNED_HOST_CC
            and FROZEN_INPUTS[11][1] == PINNED_HOST_READELF,
        )
        accept(
            "exact-current-original-correct-zig-adapter",
            FROZEN_INPUTS[3][1] == "candidates/zig_candidate.py"
            and FROZEN_INPUTS[3][2]
            == "66d9f98cabeeb1e00f16880534e817b0e79075b8afd97ea86c9e2ab08d2682c1",
        )
        accept(
            "exact-corrected-frozen-v5-cpython-original-oracle",
            FROZEN_INPUTS[4][1]
            == "tools/independent_original_cpython_suite_v5.py"
            and FROZEN_INPUTS[4][2]
            == "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
        )
        accept(
            "exact-complete-frozen-v1-build-predecessor",
            FROZEN_INPUTS[12][1]
            == "tools/reproduce_owned_zig_source_build_v1.py"
            and FROZEN_INPUTS[12][2]
            == "53df4260eee56a143d2cd9134e5c0dc336b412758218c681f59acee0a8b8644e",
        )
        valid_label = checked_label("zig-source-build-v2-synthetic-01")
        accept("one-exact-owned-publication-label", valid_label == "zig-source-build-v2-synthetic-01")
        workdir = checked_workdir("/tmp/" + WORK_PREFIX + "synthetic01")
        commands = planned_commands(workdir)
        accept(
            "invoke-only-exact-frozen-gcc-and-readelf-executables",
            commands["build_python_bridge"][0] == PINNED_HOST_CC
            and all(
                commands[name][0] == PINNED_HOST_READELF
                for name in (
                    "engine_dynamic", "bridge_dynamic",
                    "engine_symbols", "bridge_symbols",
                )
            ),
        )
        accept("seven-shell-free-pinned-build-and-elf-commands", len(commands) == 7 and all(checked_command(name, argv, workdir) == argv for name, argv in commands.items()))
        accept("only-fresh-local-and-global-zig-caches", "--cache-dir" in commands["build_zig_engine"] and "--global-cache-dir" in commands["build_zig_engine"])
        accept("allow-only-owned-host-python-undefined-symbols", "-fallow-shlib-undefined" in commands["build_zig_engine"])
        accept("literal-origin-only-runpath", "-Wl,-rpath,$ORIGIN" in commands["build_python_bridge"])
        accept("build-never-replaces-existing-candidates", commands["build_zig_engine"][-1].startswith("-femit-bin=/tmp/" + WORK_PREFIX) and commands["build_python_bridge"][-1].startswith("/tmp/" + WORK_PREFIX))
        engine_text = "0 (NEEDED) Shared library: [libc.so.6]\n0 (SONAME) Library soname: [_zig_probe.so]\n"
        bridge_text = "0 (NEEDED) Shared library: [_zig_probe.so]\n0 (NEEDED) Shared library: [libc.so.6]\n0 (RUNPATH) Library runpath: [$ORIGIN]\n"
        good_engine = dynamic_metadata(engine_text)
        good_bridge = dynamic_metadata(bridge_text)
        good_engine_symbols = set(REQUIRED_ENGINE_EXPORTS)
        good_engine_undefined = set(ALLOWED_ENGINE_UNDEFINED)
        good_bridge_symbols = {"PyInit__zig_bridge"}
        good_bridge_undefined = set(REQUIRED_BRIDGE_ENGINE_REFERENCES) | {
            "PyExc_RuntimeError",
        }
        valid_elf = validate_elf(
            good_engine, good_bridge, good_engine_symbols,
            good_engine_undefined, good_bridge_symbols, good_bridge_undefined,
        )
        accept("synthetic-owned-soname-needed-runpath-and-symbols", valid_elf["required_owned_engine_exports_present"])
        versioned_poison = (
            "  7: 0000000000000000 0 FUNC GLOBAL DEFAULT UND "
            "dlopen@GLIBC_2.34 (3)\n"
        )
        poisoned_exports, poisoned_undefined = dynamic_symbols(versioned_poison)
        accept(
            "parse-versioned-undefined-elf-name-not-version-column",
            poisoned_exports == set() and poisoned_undefined == {"dlopen"},
        )

        for index, invalid in enumerate((None, True, 1, "", "a" * 63, "A" * 64, "g" * 64, "../" + "a" * 61, "a" * 65)):
            reject("reject-forged-sha256-" + format(index, "02d"), lambda invalid=invalid: checked_digest(invalid, "synthetic"))
        for index, invalid in enumerate((None, True, 1, "", "../zig-source-build-v2-x", "zig-source-build-v2-../x", "zig-source-build-v2-X", "zig-source-build-v2-a/b", "zig-source-build-v2-a--b", "zig-source-build-v2-")):
            reject("reject-unsafe-publication-label-" + format(index, "02d"), lambda invalid=invalid: checked_label(invalid))
        for index, invalid in enumerate((None, True, 1, "", "/", "/tmp", "/tmp/../tmp/" + WORK_PREFIX + "x", "/tmp/" + WORK_PREFIX + "x/child", str(ROOT), str(ROOT / "candidates"))):
            reject("reject-unsafe-build-directory-" + format(index, "02d"), lambda invalid=invalid: checked_workdir(invalid))
        reject(
            "reject-stale-pre-correctness-fix-zig-adapter",
            lambda: checked_input((
                "zig_python_adapter", "candidates/zig_candidate.py",
                "07e9fa19af8fe9938dc8ed5170e30a478ff56f0d04cd2488a0bd1869e28201cc",
                MAX_SOURCE_BYTES, None,
            )),
        )
        reject(
            "reject-stale-v4-original-correctness-oracle",
            lambda: checked_input((
                "frozen_original_correctness_oracle",
                "tools/independent_original_cpython_suite_v4.py",
                "1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3",
                MAX_SOURCE_BYTES, None,
            )),
        )
        for index, spec in enumerate(FROZEN_INPUTS):
            name, location, pin, maximum, exact_size = spec
            for variation, forged in (("digest", (name, location, ("0" if pin[0] != "0" else "1") + pin[1:], maximum, exact_size)), ("path", (name, "../" + location, pin, maximum, exact_size)), ("size", (name, location, pin, maximum + 1, exact_size))):
                reject("reject-forged-" + name + "-" + variation + "-" + format(index, "02d"), lambda forged=forged: checked_input(forged))
        for index, name in enumerate(commands):
            forged = list(commands[name])
            forged[0] = "/bin/sh"
            reject("reject-substituted-compiler-or-elf-command-" + format(index, "02d"), lambda name=name, forged=forged: checked_command(name, forged, workdir))
        poisoned_engine = dict(good_engine)
        poisoned_engine["needed"] = ["libpcre2-8.so.0"]
        reject("reject-external-regex-shared-library", lambda: validate_elf(poisoned_engine, good_bridge, good_engine_symbols, good_engine_undefined, good_bridge_symbols, good_bridge_undefined))
        poisoned_bridge = dict(good_bridge)
        poisoned_bridge["runpath"] = ["/usr/lib"]
        reject("reject-non-origin-runpath", lambda: validate_elf(good_engine, poisoned_bridge, good_engine_symbols, good_engine_undefined, good_bridge_symbols, good_bridge_undefined))
        poisoned_bridge = dict(good_bridge)
        poisoned_bridge["needed"] = ["_rust_engine.so"]
        reject("reject-borrowed-rust-engine", lambda: validate_elf(good_engine, poisoned_bridge, good_engine_symbols, good_engine_undefined, good_bridge_symbols, good_bridge_undefined))
        reject("reject-missing-owned-zig-export", lambda: validate_elf(good_engine, good_bridge, good_engine_symbols - {"rebar_zig_compile"}, good_engine_undefined, good_bridge_symbols, good_bridge_undefined))
        reject("reject-unapproved-host-python-symbol", lambda: validate_elf(good_engine, good_bridge, good_engine_symbols, good_engine_undefined | {"_PyImport_FindExtensionObject"}, good_bridge_symbols, good_bridge_undefined))
        reject("reject-missing-python-bridge-entry", lambda: validate_elf(good_engine, good_bridge, good_engine_symbols, good_engine_undefined, set(), good_bridge_undefined))
        reject("reject-missing-owned-bridge-engine-reference", lambda: validate_elf(good_engine, good_bridge, good_engine_symbols, good_engine_undefined, good_bridge_symbols, good_bridge_undefined - {"rebar_zig_compile"}))
        reject("reject-versioned-forbidden-dynamic-loader", lambda: validate_elf(good_engine, good_bridge, good_engine_symbols, good_engine_undefined, good_bridge_symbols, good_bridge_undefined | poisoned_undefined))
        reject("block-real-source-read", lambda: builtins.open("candidates/zig/mini_regex.zig", "rb"), SourceOnlyError)
        reject("block-real-source-stat", lambda: os.stat("candidates/zig/mini_regex.zig"), SourceOnlyError)
        reject("block-real-native-build", lambda: subprocess.run([ZIG_COMPILER, "version"]), SourceOnlyError)
        reject("block-real-candidate-import", lambda: importlib.import_module("candidates.zig_candidate"), SourceOnlyError)
        reject("block-real-build-directory", lambda: tempfile.mkdtemp(prefix=WORK_PREFIX, dir="/tmp"), SourceOnlyError)
        reject("block-real-background-thread", lambda: threading.Thread(target=lambda: None).start(), SourceOnlyError)
        reject("block-real-clock-sample", time.perf_counter, SourceOnlyError)
        accept("zero-actual-source-files-native-files-or-evidence", all(amount == 0 for amount in sandbox.counts.values()))
        blocked = dict(sandbox.blocked)
        actual = dict(sandbox.counts)

    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "official_zig_version": ZIG_VERSION,
        "official_zig_archive_sha256": FROZEN_INPUTS[6][2],
        "official_zig_archive_size_bytes": ZIG_ARCHIVE_SIZE,
        "official_zig_compiler_sha256": FROZEN_INPUTS[7][2],
        "pinned_host_c_compiler_sha256": FROZEN_INPUTS[10][2],
        "pinned_host_readelf_sha256": FROZEN_INPUTS[11][2],
        "owned_zig_source_sha256": FROZEN_INPUTS[1][2],
        "owned_c_bridge_source_sha256": FROZEN_INPUTS[2][2],
        "owned_python_adapter_source_sha256": FROZEN_INPUTS[3][2],
        "frozen_original_correctness_oracle_sha256": FROZEN_INPUTS[4][2],
        "frozen_from_scratch_audit_sha256": FROZEN_INPUTS[5][2],
        "frozen_build_protocol_sha256": FROZEN_INPUTS[0][2],
        "frozen_v1_build_predecessor_sha256": FROZEN_INPUTS[12][2],
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
        "actual_clock_samples": 0,
        "source_build_status": "NOT MEASURED",
        "binary_reproduction_status": "NOT MEASURED",
        "candidate_correctness_status": "NOT MEASURED",
        "candidate_performance_status": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
    }


def run_build(label: str, source_pin: str) -> tuple[dict[str, Any], int]:
    checked_label(label)
    checked_digest(source_pin, "frozen owned Zig build controller")
    require(
        sys.executable == PINNED_PYTHON and sys.version_info[:3] == (3, 14, 6),
        "run the actual build controller only with the exact pinned CPython 3.14.6",
    )
    evidence_directory = open_evidence_directory()
    try:
        report_name, receipt_name = require_fresh_publications(evidence_directory, label)
        document: dict[str, Any] = {
            "schema": SCHEMA + "-complete-source-build",
            "status": "FAIL",
            "label": label,
            "controller_source_sha256": source_pin,
            "official_zig_version": ZIG_VERSION,
            "pinned_python": PINNED_PYTHON,
            "pinned_python_include": PYTHON_INCLUDE,
            "pinned_extension_suffix": EXTENSION_SUFFIX,
            "authenticated_inputs": {},
            "fresh_private_work_directory": None,
            "processes": [],
            "fresh_outputs": {},
            "elf": None,
            "failure": None,
            "existing_candidates_modified": False,
            "historical_binary_equality": "NOT MEASURED",
            "candidate_correctness_status": "NOT MEASURED",
            "candidate_performance_status": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
        }
        try:
            document["authenticated_inputs"]["build_controller"] = authenticate_path(
                ROOT / SOURCE_RELATIVE, expected=source_pin, maximum=MAX_SOURCE_BYTES,
            )
            for specification in FROZEN_INPUTS:
                name, observed = authenticate_frozen_input(specification)
                document["authenticated_inputs"][name] = observed
            require(
                os.path.realpath("/usr/bin/cc") == PINNED_HOST_CC,
                "the /usr/bin/cc build command no longer resolves to its pinned host compiler",
            )
            require(
                os.path.realpath("/usr/bin/readelf") == PINNED_HOST_READELF,
                "the /usr/bin/readelf command no longer resolves to its pinned ELF inspector",
            )
            workdir = checked_workdir(tempfile.mkdtemp(prefix=WORK_PREFIX, dir="/tmp"))
            document["fresh_private_work_directory"] = workdir
            os.mkdir(str(Path(workdir) / "local-cache"), 0o700)
            os.mkdir(str(Path(workdir) / "global-cache"), 0o700)
            steps = document["processes"]
            version = run_process("compiler_version", workdir, steps)
            require(version["stdout"].strip() == ZIG_VERSION, "the authenticated compiler reported a different exact Zig version")
            run_process("build_zig_engine", workdir, steps)
            engine_path = Path(workdir) / "_zig_probe.so"
            document["fresh_outputs"]["native_engine"] = authenticate_path(
                engine_path, expected=None, maximum=MAX_BINARY_BYTES,
            )
            run_process("build_python_bridge", workdir, steps)
            bridge_path = Path(workdir) / ("_zig_bridge" + EXTENSION_SUFFIX)
            document["fresh_outputs"]["native_bridge"] = authenticate_path(
                bridge_path, expected=None, maximum=MAX_BINARY_BYTES,
            )
            engine_dynamic = dynamic_metadata(run_process("engine_dynamic", workdir, steps)["stdout"])
            bridge_dynamic = dynamic_metadata(run_process("bridge_dynamic", workdir, steps)["stdout"])
            engine_symbols, engine_undefined = dynamic_symbols(
                run_process("engine_symbols", workdir, steps)["stdout"],
            )
            bridge_symbols, bridge_undefined = dynamic_symbols(
                run_process("bridge_symbols", workdir, steps)["stdout"],
            )
            document["elf"] = validate_elf(
                engine_dynamic, bridge_dynamic, engine_symbols,
                engine_undefined, bridge_symbols, bridge_undefined,
            )
            document["source_inputs_reauthenticated"] = {
                name: authenticate_frozen_input(specification)[1]
                for specification in FROZEN_INPUTS[1:4]
                for name in (specification[0],)
            }
            document["all_frozen_inputs_reauthenticated"] = {}
            for specification in FROZEN_INPUTS:
                name, observed = authenticate_frozen_input(specification)
                require(
                    observed == document["authenticated_inputs"][name],
                    "a frozen input changed during the isolated Zig build: "
                    + name,
                )
                document["all_frozen_inputs_reauthenticated"][name] = observed
            controller_after = authenticate_path(
                ROOT / SOURCE_RELATIVE, expected=source_pin,
                maximum=MAX_SOURCE_BYTES,
            )
            require(
                controller_after
                == document["authenticated_inputs"]["build_controller"],
                "the authenticated V2 controller changed during its build",
            )
            document["controller_reauthenticated"] = controller_after
            document["status"] = "PASS"
        except Exception as error:
            document["failure"] = {"type": type(error).__name__, "message": str(error)}
        report = publish_fresh(evidence_directory, report_name, document)
        receipt_document = {
            "schema": SCHEMA + "-fresh-publication-receipt",
            "status": "PASS",
            "build_status": document["status"],
            "label": label,
            "controller_source_sha256": source_pin,
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
        description="Authenticate and independently rebuild the from-scratch Zig regex engine without replacing a candidate",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true", help="run purely synthetic, side-effect-free source controls")
    modes.add_argument("--build", action="store_true", help="explicitly build fresh isolated native artifacts and publish all results")
    parser.add_argument("--label", help="fresh zig-source-build-v2-* evidence label; actual build only")
    parser.add_argument("--controller-source-sha256", help="exact prospectively frozen controller SHA-256; actual build only")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(
            options.label is None and options.controller_source_sha256 is None,
            "a synthetic source self-test cannot request a candidate, build, pin, or publication",
        )
        print(canonical(source_self_test()).decode("ascii"), end="")
        return 0
    require(options.label is not None and options.controller_source_sha256 is not None, "an actual build requires one fresh label and exact frozen controller hash")
    result, code = run_build(options.label, options.controller_source_sha256)
    print(canonical(result).decode("ascii"), end="")
    return code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildError as error:
        print(
            canonical(
                {
                    "schema": SCHEMA + "-controller-failure",
                    "status": "FAIL",
                    "failure": {"type": type(error).__name__, "message": str(error)},
                    "candidate_qualified_for_hidden_benchmark": False,
                }
            ).decode("ascii"),
            end="",
        )
        raise SystemExit(2) from None
