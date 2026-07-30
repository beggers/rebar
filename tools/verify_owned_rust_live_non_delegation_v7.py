#!/usr/bin/env python3
"""Run isolated live proof that the exact qualified-by-correctness Rust uses its own engine."""

from __future__ import annotations

import ast
import builtins
import hashlib
import importlib
import io
import json
import os
import socket
import stat
import subprocess
import sys
import threading
import time


ROOT = "/home/dev-user/src/rebar"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_STDLIB = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/"
SOURCE = "tools/verify_owned_rust_live_non_delegation_v7.py"
PROTOCOL = "oracle/phase2/RUST-LIVE-NON-DELEGATION-V7.md"
CONTRACT = "oracle/phase2/rust-live-non-delegation-v7.json"
SCHEMA = "rebar-phase2-first-party-rust-live-non-delegation-v7"
RESULT_PATH = "oracle/phase2/evidence/rust-live-non-delegation-v7-actual-runtime-proof.json"
HEX = frozenset("0123456789abcdef")
MAX_SOURCE = 4 * 1024 * 1024
MAX_RESULT = 1024 * 1024
READ_CHUNK = 65536

V33_OWNERS = {
    "tools/reproduce_owned_rust_full_public_semantic_source_build_v33.py":
        "31251c3aa6006108ba1a5b5e7b5a07147d9b8ccf76123f4aa08ecffb20c91c63",
    "oracle/phase2/RUST-FULL-PUBLIC-SEMANTIC-SOURCE-BUILD-V33.md":
        "c73843e1705beb24e4ced9ab3d9fa95da7420c5d24cd8f6ffaeeb747aa382071",
    "oracle/phase2/rust-full-public-semantic-source-build-v33.json":
        "bb7d338cb766b7f1ff52e616355d5d5cddb00849532e42755b31a9bf09119337",
}
V5_OWNERS = {
    "tools/audit_clean_rust_runtime_non_delegation_v5.py":
        "5ab79fc493f1b798d1020311dddf7a061e5b272d3c6f2c10e19127311b57b542",
    "oracle/phase2/RUST-CLEAN-NON-DELEGATION-V5.md":
        "4efa6122a16c438224f226f468d0654473df489fa338f2539ae22411ce4d01fa",
    "oracle/phase2/rust-clean-non-delegation-v5.json":
        "605e0a55f57d1e5c9061bcefe9323bf4de62905c92ca9a29021a79503546cd57",
}
V6_OWNERS = {
    "tools/verify_owned_rust_live_non_delegation_v6.py":
        "e8932317ae1bf5fb4be0a95bf91db216e235434f62db06a4a1dd2f12b9e993e6",
    "oracle/phase2/RUST-LIVE-NON-DELEGATION-V6.md":
        "88486535a29e777c130eba40c8c353c1bc34d0eda7ae6e796051189beec87675",
    "oracle/phase2/rust-live-non-delegation-v6.json":
        "76c78d974145c509222d28fca085cd3ef3d1f8e458919ea94b363d848da28b42",
}
V33_PUBLICATION_PATH = (
    "oracle/phase2/evidence/native-source-build-v33-rust-phase2-v33-rust-"
    "full-public-semantic-source-root-provenance-publication-receipt.json"
)
V33_PUBLICATION = {
    "sha256": "cfe1464e1e8ce96bfa514b15cf96879a0642686987159dd79c15f4d9db408749",
    "bytes": 6696, "device": 2064, "inode": 525066, "mode": "0600",
}
V33_ROOT_PATH = (
    "oracle/phase2/evidence/native-source-build-v33-rust-phase2-v33-rust-"
    "full-public-semantic-source-root-provenance-root-provenance-receipt.json"
)
V33_ROOT = {
    "sha256": "7122c9bdff731be0f68602a4a216c1fa9700e6a78f9da9b534eeaef282c64c1c",
    "bytes": 80421, "device": 2064, "inode": 525067, "mode": "0600",
}
ORIGINAL_PASS_PATH = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v30-rust-"
    "complete-semantic-source-root-provenance-original-p0-v26-publication-receipt.json"
)
ORIGINAL_PASS = {
    "sha256": "84804409997794ce7e8bfff67ca8ffdcada9651a1660bda2654742befbba20f5",
    "bytes": 12055, "device": 2064, "inode": 525046, "mode": "0600",
}
PUBLIC_PASS_PATH = (
    "oracle/phase2/evidence/rust-full-public-correctness-v5-v33-full-public-v5-run-001-"
    "publication-receipt.json"
)
PUBLIC_PASS = {
    "sha256": "8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9",
    "bytes": 6889, "device": 2064, "inode": 525451, "mode": "0600",
}
STATIC_PASS_PATH = "oracle/phase2/evidence/rust-clean-non-delegation-v5-actual-source-audit.json"
STATIC_PASS = {
    "sha256": "a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203",
    "bytes": 16427, "device": 2064, "inode": 525089, "mode": "0600",
}
V6_FAILURE_PATH = "oracle/phase2/evidence/rust-live-non-delegation-v6-actual-runtime-failure.json"
V6_FAILURE = {
    "sha256": "9dcc4d6dbf81ed828189cacf8e981de788190bcf9912d01b8858e6841397286b",
    "bytes": 416, "device": 2064, "inode": 525883, "mode": "0600",
}
APPROVED_RECEIPTS = frozenset({
    V33_PUBLICATION_PATH, V33_ROOT_PATH, ORIGINAL_PASS_PATH, PUBLIC_PASS_PATH,
    STATIC_PASS_PATH, V6_FAILURE_PATH,
})
SOURCE_IDENTITIES = {
    "adapter": {
        "relative": "source/candidates/rust_candidate.py",
        "sha256": "f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227",
        "bytes": 34039, "mode": "0600",
    },
    "bridge_source": {
        "relative": "source/candidates/rust/py_bridge.c",
        "sha256": "f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e",
        "bytes": 178472, "mode": "0600",
    },
    "engine_source": {
        "relative": "source/candidates/rust/src/lib.rs",
        "sha256": "7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38",
        "bytes": 189493, "mode": "0600",
    },
    "search_source": {
        "relative": "source/candidates/rust/src/search.rs",
        "sha256": "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7",
        "bytes": 24305, "mode": "0600",
    },
}
NATIVE_IDENTITIES = {
    "engine": {
        "relative": "native/_rust_engine.so",
        "file_name": "_rust_engine.so",
        "sha256": "e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8",
        "bytes": 672440, "mode": "0600",
    },
    "bridge": {
        "relative": "native/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "file_name": "_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "sha256": "ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000",
        "bytes": 148728, "mode": "0700",
    },
}
EXPECTED_OPERATIONS = (
    "compiled_named_unicode_search",
    "module_search_cache",
    "module_match",
    "module_fullmatch",
    "bytes_memoryview_search",
    "scoped_unicode_category",
    "verbose_named_escape_comment",
    "findall_named_digits",
    "finditer_spans",
    "split_digits",
    "sub_callback",
    "subn_named_template",
    "match_expand_named_template",
    "pattern_scanner_search",
    "public_lexical_scanner",
    "bytes_named_substitution",
    "lookbehind_search",
    "backreference_fullmatch",
    "bytes_ignorecase",
    "cache_lifecycle",
    "match_reduce_copyreg",
    "scanner_reduce_rejected",
)
FORBIDDEN_ROOTS = frozenset({
    "re", "_sre", "inspect", "tokenize", "regex", "re2", "pcre", "pcre2",
    "onig", "oniguruma", "rure", "hyperscan", "ahocorasick", "ctypes",
    "cffi", "importlib", "subprocess", "socket",
})
ALLOWED_IMPORT_ROOTS = frozenset({
    "abc", "_abc", "_blake2", "_codecs", "_collections", "_collections_abc",
    "_contextvars", "_functools", "_hashlib", "_io", "_operator", "_py_warnings",
    "_signal", "_stat", "_thread", "_types", "_warnings", "_weakref", "builtins",
    "candidates", "codecs", "collections", "contextvars", "copyreg", "encodings",
    "enum", "errno", "functools", "genericpath", "hashlib", "itertools", "keyword",
    "linecache", "marshal", "operator", "os", "posix", "posixpath", "reprlib",
    "stat", "sys", "time", "types", "unicodedata", "warnings", "zipimport",
})
FORBIDDEN_MAP_FRAGMENTS = (
    "libpcre", "libonig", "libre2", "libhyperscan", "libhs.so", "librure",
    "_sre.", "/regex/", "/candidates/_vm", "/candidates/_zig", "/candidates/_cpp",
    "/candidates/_go", "/candidates/_fortran",
)
_OPEN, _READ, _FSTAT, _CLOSE = os.open, os.read, os.fstat, os.close

WORKER_PROGRAM = r'''
import sys

_forbidden = {
    "re", "_sre", "inspect", "tokenize", "regex", "re2", "pcre", "pcre2",
    "onig", "oniguruma", "rure", "hyperscan", "ahocorasick", "ctypes",
    "cffi", "importlib", "subprocess", "socket",
}
_starting = tuple(sorted(name for name in sys.modules
                         if name.split(".", 1)[0] in _forbidden))
if _starting:
    sys.stdout.write(repr({"status": "FAIL", "message": "forbidden preloaded modules",
                           "modules": _starting}) + "\n")
    raise SystemExit(1)

import builtins
import hashlib
import os
import types

if any(name.split(".", 1)[0] in _forbidden for name in sys.modules):
    sys.stdout.write(repr({"status": "FAIL", "message": "bootstrap imported forbidden modules",
                           "modules": sorted(name for name in sys.modules
                                             if name.split(".", 1)[0] in _forbidden)}) + "\n")
    raise SystemExit(1)

_phase, _phase_path, _adapter_sha, _bridge_source_sha, _engine_source_sha, _search_sha, \
    _bridge_sha, _engine_sha = sys.argv[1:]
if _phase not in {"reference-a", "reference-b"} or not _phase_path.startswith(
        "/tmp/rebar-phase2-native-build-v9-rust-"):
    raise SystemExit("invalid worker private phase")
_source = _phase_path + "/source/candidates"
_native = _phase_path + "/native"
_adapter = _source + "/rust_candidate.py"
_bridge_source = _source + "/rust/py_bridge.c"
_engine_source = _source + "/rust/src/lib.rs"
_search_source = _source + "/rust/src/search.rs"
_bridge = _native + "/_rust_bridge.cpython-314-x86_64-linux-gnu.so"
_engine = _native + "/_rust_engine.so"
_stdlib = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/"
_allowed_files = {
    _adapter, _bridge_source, _engine_source, _search_source, _bridge, _engine,
    _source + "/__pycache__/rust_candidate.cpython-314.pyc",
    "/proc/self/maps",
}
_allowed_imports = {
    "abc", "_abc", "_blake2", "_codecs", "_collections", "_collections_abc",
    "_contextvars", "_functools", "_hashlib", "_io", "_operator", "_py_warnings",
    "_signal", "_stat", "_thread", "_types", "_warnings", "_weakref", "builtins",
    "candidates", "codecs", "collections", "contextvars", "copyreg", "encodings",
    "enum", "errno", "functools", "genericpath", "hashlib", "itertools", "keyword",
    "linecache", "marshal", "operator", "os", "posix", "posixpath", "reprlib",
    "stat", "sys", "time", "types", "unicodedata", "warnings", "zipimport",
}
_events = []
_opened = []
_imported = []
_phase_marker = "bootstrap"
_forbidden_attempts = 0
_process_attempts = 0
_network_attempts = 0
_native_load_attempts = 0
_outside_open_attempts = 0
_old_import = builtins.__import__


def _deny(message):
    raise RuntimeError("LIVE_NON_DELEGATION_DENIED: " + message)


def _safe_module(name):
    return isinstance(name, str) and name.split(".", 1)[0] in _allowed_imports


def _audit(event, args):
    global _forbidden_attempts, _process_attempts, _network_attempts
    global _native_load_attempts, _outside_open_attempts
    if event == "import":
        name = args[0] if args else ""
        path = args[1] if len(args) > 1 else None
        if not _safe_module(name) or name.split(".", 1)[0] in _forbidden:
            _forbidden_attempts += 1
            _deny("foreign module " + repr(name))
        if name.startswith("candidates.") and name not in {
                "candidates.rust_candidate", "candidates._rust_bridge"}:
            _forbidden_attempts += 1
            _deny("cross-family candidate " + name)
        if isinstance(path, str) and path.endswith(".so"):
            if name == "candidates._rust_bridge":
                if path != _bridge:
                    _native_load_attempts += 1
                    _deny("foreign Rust bridge " + path)
            elif not path.startswith(_stdlib):
                _native_load_attempts += 1
                _deny("foreign extension module " + path)
        _imported.append((name, path if isinstance(path, str) else None, _phase_marker))
    elif event == "open":
        path = args[0] if args else ""
        mode = args[1] if len(args) > 1 else None
        flags = args[2] if len(args) > 2 else 0
        if not isinstance(path, str):
            _outside_open_attempts += 1
            _deny("descriptor-based unowned open")
        if path not in _allowed_files and not path.startswith(_stdlib):
            _outside_open_attempts += 1
            _deny("unapproved owner " + path)
        if path.startswith(_stdlib):
            lower = path.casefold()
            if "/re/" in lower or "/regex/" in lower or "/_sre" in lower \
                    or lower.endswith("/inspect.py") or lower.endswith("/tokenize.py"):
                _forbidden_attempts += 1
                _deny("stdlib regex/introspection source " + path)
        if isinstance(mode, str) and any(flag in mode for flag in "wax+"):
            _outside_open_attempts += 1
            _deny("workspace or private source mutation")
        if isinstance(flags, int) and flags & (
                os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            _outside_open_attempts += 1
            _deny("write-capable native open")
        _opened.append((path, _phase_marker))
    elif event in {"subprocess.Popen", "os.system", "os.posix_spawn",
                   "os.posix_spawnp", "os.fork", "os.exec"}:
        _process_attempts += 1
        _deny("subprocess or external executable")
    elif event in {"socket.connect", "socket.__new__", "socket.getaddrinfo"}:
        _network_attempts += 1
        _deny("network access")
    elif event.startswith("ctypes.") or event in {"os.add_dll_directory"}:
        _native_load_attempts += 1
        _deny("external native library loader")
    elif event == "sys.addaudithook":
        _deny("candidate attempted to replace live audit hooks")
    elif event == "exec":
        code = args[0] if args else None
        filename = getattr(code, "co_filename", "")
        if not (filename == _adapter or filename.startswith(_stdlib)
                or filename.startswith("<frozen ")):
            _deny("dynamic execution outside the exact adapter/stdlib " + repr(filename))
    elif event == "compile":
        filename = args[1] if len(args) > 1 else ""
        if isinstance(filename, bytes):
            filename = filename.decode("utf-8", "replace")
        if not (filename == _adapter or (
                isinstance(filename, str) and filename.startswith(_stdlib))):
            _deny("dynamic candidate code compilation " + repr(filename))
    elif event in {"os.listdir", "os.scandir"}:
        path = args[0] if args else ""
        if not (isinstance(path, str) and (
                path in {_source, _native} or path.startswith(_stdlib))):
            _deny("candidate attempted unrelated directory enumeration")
    if len(_events) < 768:
        _events.append((event, _phase_marker))
    else:
        _deny("audit event count exceeded its frozen finite bound")


def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    global _forbidden_attempts
    if level != 0 or not _safe_module(name) or name.split(".", 1)[0] in _forbidden:
        _forbidden_attempts += 1
        _deny("forbidden direct or relative import " + repr(name))
    if name == "candidates":
        if any(item != "_rust_bridge" for item in fromlist):
            _forbidden_attempts += 1
            _deny("cross-family native bridge import")
    elif name.startswith("candidates.") and name not in {
            "candidates.rust_candidate", "candidates._rust_bridge"}:
        _forbidden_attempts += 1
        _deny("cross-family candidate adapter")
    return _old_import(name, globals, locals, fromlist, level)


def _identity(path, expected_sha, expected_bytes, expected_mode):
    with open(path, "rb") as stream:
        raw = stream.read(expected_bytes + 1)
    info = os.stat(path, follow_symlinks=False)
    if len(raw) != expected_bytes or hashlib.sha256(raw).hexdigest() != expected_sha \
            or info.st_uid != os.getuid() or info.st_nlink != 1 \
            or (info.st_mode & 0o777) != expected_mode:
        _deny("candidate source/native identity changed " + path)
    return {"path": path, "sha256": expected_sha, "bytes": expected_bytes,
            "device": info.st_dev, "inode": info.st_ino,
            "mode": format(info.st_mode & 0o777, "04o")}


def _forbidden_loaded():
    return sorted(name for name in sys.modules
                  if name.split(".", 1)[0] in _forbidden)


def _maps():
    with open("/proc/self/maps", "r", encoding="utf-8") as stream:
        return tuple(line.rsplit(None, 1)[-1].strip()
                     for line in stream if line.rstrip().endswith(".so")
                     or ".so." in line)


try:
    sys.addaudithook(_audit)
    builtins.__import__ = _guarded_import
    _phase_marker = "authenticate"
    identities = {
        "adapter": _identity(_adapter, _adapter_sha, 34039, 0o600),
        "bridge_source": _identity(_bridge_source, _bridge_source_sha, 178472, 0o600),
        "engine_source": _identity(_engine_source, _engine_source_sha, 189493, 0o600),
        "search_source": _identity(_search_source, _search_sha, 24305, 0o600),
        "bridge": _identity(_bridge, _bridge_sha, 148728, 0o700),
        "engine": _identity(_engine, _engine_sha, 672440, 0o600),
    }
    _before_maps = _maps()
    if _bridge in _before_maps or _engine in _before_maps:
        _deny("candidate native libraries were loaded before guarded candidate import")
    if _forbidden_loaded():
        _deny("forbidden modules existed before candidate import")

    _package = types.ModuleType("candidates")
    _package.__path__ = [_native, _source]
    _package.__package__ = "candidates"
    sys.modules["candidates"] = _package
    _phase_marker = "candidate_import"
    candidate = _guarded_import("candidates.rust_candidate", fromlist=("rust_candidate",))
    native = sys.modules.get("candidates._rust_bridge")
    if candidate is not sys.modules.get("candidates.rust_candidate") or native is None \
            or getattr(native, "__file__", None) != _bridge:
        _deny("candidate did not import its exact owned native bridge")
    _loaded_maps = _maps()
    if _bridge not in _loaded_maps or _engine not in _loaded_maps:
        _deny("both exact first-party Rust native objects were not actually loaded")
    for path in _loaded_maps:
        lowered = path.casefold()
        if any(fragment in lowered for fragment in (
                "libpcre", "libonig", "libre2", "libhyperscan", "libhs.so",
                "librure", "_sre.", "/regex/", "/candidates/_vm", "/candidates/_zig",
                "/candidates/_cpp", "/candidates/_go", "/candidates/_fortran")):
            _deny("foreign candidate or external regex library mapping " + path)
    if _forbidden_loaded():
        _deny("candidate import reached a forbidden stdlib/external regex module")

    _operations = []
    _phase_marker = "candidate_operations"

    def check(name, condition):
        if not condition:
            _deny("live candidate returned an unexpected answer for " + name)
        if _forbidden_loaded():
            _deny("live operation imported forbidden regex module " + name)
        _operations.append(name)

    compiled = candidate.compile(r"(?P<word>\w+)")
    matched = compiled.search("..café..", 2)
    check("compiled_named_unicode_search",
          matched is not None and matched.group("word") == "café" and matched.span() == (2, 6))
    check("module_search_cache",
          candidate.search("cache", "--cache--").span() == (2, 7))
    check("module_match", candidate.match(r"(?P<a>a+)", "aaab").group("a") == "aaa")
    check("module_fullmatch", candidate.fullmatch(r"(?i:ab)c", "ABc").span() == (0, 3))
    check("bytes_memoryview_search",
          candidate.search(rb"a+", memoryview(bytearray(b"--aaa--"))).span() == (2, 5))
    check("scoped_unicode_category",
          candidate.search(r"(?a:(?u:\w))", "é").span() == (0, 1))
    verbose = "(?x)\\N{LATIN SMALL LETTER A} # \\N{NOT A NAME}\na"
    check("verbose_named_escape_comment", candidate.fullmatch(verbose, "aa").span() == (0, 2))
    check("findall_named_digits",
          candidate.findall(r"(?P<n>\d+)", "a12b003") == ["12", "003"])
    check("finditer_spans",
          [item.span() for item in candidate.finditer(r"\d+", "a12b003")] == [(1, 3), (4, 7)])
    check("split_digits", candidate.split(r"\d+", "a12b003c") == ["a", "b", "c"])
    check("sub_callback", candidate.sub(r"\d+", lambda item: "[" + item.group() + "]",
                                         "a12b003") == "a[12]b[003]")
    check("subn_named_template",
          candidate.subn(r"(?P<n>\d+)", r"<\g<n>>", "a12b003")
          == ("a<12>b<003>", 2))
    check("match_expand_named_template",
          matched.expand(r"\g<word>:\g<word>") == "café:café")
    iterator = candidate.compile(r"\w+").scanner("ab cd")
    first, second = iterator.search(), iterator.search()
    check("pattern_scanner_search",
          first.group() == "ab" and second.group() == "cd" and iterator.search() is None)
    lexical = candidate.Scanner([
        (r"\d+", lambda scanner, value: ("number", value)),
        (r"\s+", None),
        (r"[A-Za-z]+", lambda scanner, value: ("word", value)),
    ])
    check("public_lexical_scanner",
          lexical.scan("12 ab") == ([("number", "12"), ("word", "ab")], ""))
    check("bytes_named_substitution",
          candidate.sub(rb"(?P<n>\d+)", br"<\g<n>>", b"a12b003")
          == b"a<12>b<003>")
    check("lookbehind_search", candidate.search(r"(?<=ab)c", "zabc").span() == (3, 4))
    check("backreference_fullmatch",
          candidate.fullmatch(r"(a+)\1", "aaaa").span() == (0, 4))
    check("bytes_ignorecase",
          candidate.fullmatch(rb"abc", b"AbC", candidate.IGNORECASE).span() == (0, 3))
    cached_a = candidate.compile("cache-lifecycle")
    cached_b = candidate.compile("cache-lifecycle")
    candidate.purge()
    cached_c = candidate.compile("cache-lifecycle")
    check("cache_lifecycle", cached_a is cached_b and cached_c is not cached_a)
    reduced = matched.__reduce_ex__(0)
    check("match_reduce_copyreg",
          len(reduced) == 2 and getattr(reduced[0], "__module__", None) == "copyreg")
    try:
        iterator.__reduce_ex__(0)
    except TypeError as error:
        check("scanner_reduce_rejected", "cannot pickle" in str(error))
    else:
        _deny("scanner serialization unexpectedly succeeded")

    _after_maps = _maps()
    if _bridge not in _after_maps or _engine not in _after_maps or _forbidden_loaded() \
            or builtins.__import__ is not _guarded_import:
        _deny("live operation escaped exact native owner/import containment")
    if "copyreg" not in sys.modules or not any(
            row[0] == "copyreg" and row[2] == "candidate_operations" for row in _imported):
        _deny("first-party bridge did not perform its audited direct native metadata import")
    if len(_operations) != 22 or _forbidden_attempts or _process_attempts \
            or _network_attempts or _native_load_attempts or _outside_open_attempts:
        _deny("live proof operation count or foreign-effect counters changed")
    _answer = {
        "schema": "rebar-phase2-rust-live-worker-v7", "status": "PASS",
        "phase": _phase,
        "initial_forbidden_modules": _starting,
        "final_forbidden_modules": tuple(_forbidden_loaded()),
        "audit_hook_installed_before_candidate_import": True,
        "guarded_python_import_installed": True,
        "candidate_adapter_module": candidate.__name__,
        "native_bridge_module": native.__name__,
        "candidate_native_bridge_path": native.__file__,
        "candidate_native_engine_path": _engine,
        "source_and_native_owners": identities,
        "observed_imports": tuple(_imported),
        "observed_file_opens": tuple(_opened),
        "observed_audit_events": tuple(_events),
        "loaded_native_objects": tuple(sorted(set(path for path in _after_maps
                                                  if path in {_bridge, _engine}))),
        "operation_names": tuple(_operations),
        "operation_count": len(_operations),
        "candidate_native_copyreg_import_observed": True,
        "forbidden_module_import_attempts": _forbidden_attempts,
        "external_native_load_attempts": _native_load_attempts,
        "cross_family_load_count": 0,
        "subprocess_attempts": _process_attempts,
        "network_attempts": _network_attempts,
        "outside_open_attempts": _outside_open_attempts,
        "holdout_reads": 0, "proposal_content_opens": 0,
        "proposal_metadata_probes": 0, "hidden_case_reads": 0,
        "benchmark_reads": 0, "external_regex_packages": 0,
        "external_regex_libraries": 0,
        "runtime_non_delegation": "ESTABLISHED FOR THIS EXACT CANDIDATE AND OPERATION SET",
    }
    sys.stdout.buffer.write((repr(_answer) + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()
except BaseException as error:
    _answer = {"schema": "rebar-phase2-rust-live-worker-v7", "status": "FAIL",
               "phase": _phase, "error_type": type(error).__name__,
               "message": str(error)[:2048], "forbidden_module_import_attempts": _forbidden_attempts,
               "external_native_load_attempts": _native_load_attempts,
               "subprocess_attempts": _process_attempts, "network_attempts": _network_attempts,
               "outside_open_attempts": _outside_open_attempts,
               "observed_imports": tuple(_imported[-32:]),
               "observed_audit_events": tuple(_events[-64:]),
               "runtime_non_delegation": "NOT ESTABLISHED"}
    sys.stdout.buffer.write((repr(_answer) + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()
    raise SystemExit(1)
'''


class LiveProofError(Exception):
    """The frozen first-party live non-delegation proof failed closed."""


def require(value: object, message: str) -> None:
    if not value:
        raise LiveProofError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                       separators=(",", ":")) + "\n").encode("ascii")


def exact_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64 and frozenset(value) <= HEX,
            label + ": require an independently supplied full lowercase SHA-256")
    return value


def strict_json(raw: bytes, label: str) -> dict[str, object]:
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        answer = {}
        for key, value in pairs:
            require(type(key) is str and key not in answer, label + ": duplicate JSON field")
            answer[key] = value
        return answer

    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                            parse_constant=lambda value: (_ for _ in ()).throw(
                                LiveProofError(label + ": non-finite JSON " + value)))
    except (UnicodeError, ValueError, TypeError) as error:
        raise LiveProofError(label + ": malformed immutable public receipt") from error
    require(type(result) is dict, label + ": require one exact immutable JSON object")
    return result


def fresh_effects() -> dict[str, int]:
    return {key: 0 for key in (
        "approved_owner_reads", "v33_source_owner_reads", "v5_source_owner_reads",
        "v6_source_owner_reads", "v6_failure_reads", "public_receipt_reads",
        "private_build_root_opens", "private_phase_opens",
        "private_candidate_source_reads", "private_native_reads", "candidate_processes",
        "candidate_operations", "candidate_imports", "native_library_loads",
        "forbidden_module_imports", "external_engine_loads", "cross_family_loads",
        "subprocesses", "reference_workers", "archive_reads", "archive_decompressions",
        "holdout_reads", "proposal_content_opens", "proposal_metadata_probes",
        "hidden_case_reads", "benchmark_reads", "network_requests", "compiler_processes",
        "clock_samples", "workspace_mutations", "git_reads", "blocked_reads",
        "blocked_writes", "blocked_imports", "blocked_processes", "blocked_network",
        "blocked_threads", "blocked_clocks", "blocked_native_loads", "blocked_audit_hooks",
    )}


class SourceWall:
    def __init__(self) -> None:
        self.effects = fresh_effects()
        self.restore: list[tuple[object, str, object]] = []

    def block(self, owner: object, name: str, counter: str) -> None:
        if not hasattr(owner, name):
            return
        old = getattr(owner, name)

        def denied(*args: object, **kwargs: object) -> object:
            self.effects[counter] += 1
            raise LiveProofError("deny-default source wall rejected " + name)

        self.restore.append((owner, name, old))
        setattr(owner, name, denied)

    def __enter__(self) -> SourceWall:
        for owner, name in ((builtins, "open"), (io, "open"), (os, "open"),
                            (os, "read"), (os, "fstat"), (os, "stat"), (os, "lstat"),
                            (os, "listdir"), (os, "scandir"), (os, "walk")):
            self.block(owner, name, "blocked_reads")
        for name in ("write", "unlink", "remove", "mkdir", "makedirs", "rename", "replace",
                     "rmdir", "chmod", "chown", "link", "symlink", "truncate", "utime", "fsync"):
            self.block(os, name, "blocked_writes")
        self.block(builtins, "__import__", "blocked_imports")
        self.block(importlib, "import_module", "blocked_imports")
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            self.block(subprocess, name, "blocked_processes")
        for name in ("system", "popen", "fork", "posix_spawn", "posix_spawnp"):
            self.block(os, name, "blocked_processes")
        self.block(threading.Thread, "start", "blocked_threads")
        self.block(socket, "create_connection", "blocked_network")
        self.block(socket.socket, "connect", "blocked_network")
        self.block(sys, "addaudithook", "blocked_audit_hooks")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                     "perf_counter_ns", "process_time", "process_time_ns",
                     "thread_time", "thread_time_ns", "sleep"):
            self.block(time, name, "blocked_clocks")
        for module_name in ("ctypes", "_ctypes"):
            module = sys.modules.get(module_name)
            if module is not None:
                for name in ("CDLL", "PyDLL", "WinDLL", "OleDLL", "dlopen", "_dlopen"):
                    self.block(module, name, "blocked_native_loads")
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        for owner, name, value in reversed(self.restore):
            setattr(owner, name, value)


def checked_public(path: str, *, receipt: bool = False) -> tuple[str, ...]:
    require(type(path) is str and bool(path) and "\x00" not in path and "\\" not in path
            and not path.startswith("/"), "require an exact project-relative public owner")
    parts = path.split("/")
    require(all(part not in {"", ".", "..", ".git", ".agents", ".codex", "__pycache__"}
                for part in parts), "owner path contains forbidden traversal or metadata")
    for item in parts:
        lowered = item.casefold()
        require(not any(fragment in lowered for fragment in
                        ("holdout", "hidden", "benchmark", "postfinal", "archive",
                         "proposal", "phase3", "final")),
                "protected final case, benchmark, or archive access is forbidden")
        require(lowered not in {"performance", "candidates"},
                "source-only proof may not access candidate or performance paths")
        if lowered == "evidence":
            require(receipt and path in APPROVED_RECEIPTS,
                    "only five exact authenticated public receipts may be opened")
    return tuple(parts)


def read_at(base: int, parts: tuple[str, ...], label: str, effects: dict[str, int],
            category: str, *, maximum: int = MAX_SOURCE,
            expected: dict[str, object] | None = None) -> tuple[bytes, dict[str, object]]:
    require(bool(parts) and all(part not in {"", ".", ".."} and "/" not in part
                                for part in parts), "invalid descriptor-relative first-party path")
    opened: list[int] = []
    try:
        parent = base
        for part in parts[:-1]:
            child = _OPEN(part, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                          dir_fd=parent)
            opened.append(child)
            parent = child
        handle = _OPEN(parts[-1], os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=parent)
        opened.append(handle)
        before = _FSTAT(handle)
        require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum
                and before.st_uid == os.getuid() and before.st_nlink == 1,
                label + ": expected a bounded owned, single-link regular file")
        blocks: list[bytes] = []
        left = before.st_size
        while left:
            block = _READ(handle, min(left, READ_CHUNK))
            require(bool(block), label + ": frozen owner truncated during authentication")
            blocks.append(block)
            left -= len(block)
        require(not _READ(handle, 1), label + ": frozen owner grew during authentication")
        after = _FSTAT(handle)
        identity = lambda item: (item.st_dev, item.st_ino, item.st_size,
                                 item.st_mtime_ns, item.st_ctime_ns, item.st_nlink)
        require(identity(before) == identity(after), label + ": frozen owner changed while read")
        raw = b"".join(blocks)
        owner = {"path": label, "sha256": digest(raw), "bytes": len(raw),
                 "device": before.st_dev, "inode": before.st_ino,
                 "mode": format(stat.S_IMODE(before.st_mode), "04o"),
                 "uid": before.st_uid, "nlink": before.st_nlink}
        if expected is not None:
            for key, value in expected.items():
                require(owner.get(key) == value, label + ": immutable " + key + " changed")
        effects["approved_owner_reads"] += 1
        if category != "approved_owner_reads":
            effects[category] += 1
        return raw, owner
    finally:
        for handle in reversed(opened):
            _CLOSE(handle)


def read_public(path: str, effects: dict[str, int], category: str,
                *, expected: dict[str, object] | None = None) -> tuple[bytes, dict[str, object]]:
    parts = checked_public(path, receipt=(category == "public_receipt_reads"))
    root = _OPEN(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        return read_at(root, parts, path, effects, category, expected=expected)
    finally:
        _CLOSE(root)


def require_interpreter() -> None:
    require(sys.implementation.name == "cpython" and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == ROOT + "/" + SOURCE,
            "use only the frozen isolated CPython 3.14.6 interpreter")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules), "a controller imported candidate code prematurely")


def validate_publication(publication: dict[str, object], root: dict[str, object],
                         original: dict[str, object], public: dict[str, object],
                         static: dict[str, object]) -> None:
    require(publication.get("schema") ==
            "rebar-phase2-owned-rust-full-public-semantic-source-build-v33-durable-publication-receipt"
            and publication.get("status") == "PASS" and publication.get("build_status") == "PASS"
            and publication.get("actual_completed_phase_count") == 2
            and publication.get("actual_compiler_process_count") == 28
            and publication.get("external_cargo_dependency_count") == 0
            and publication.get("candidate_matching") == "NOT RUN"
            and publication.get("hidden_cases_generated") == 0,
            "the genuine V33 dependency-free, 28-process dual build changed")
    require(root.get("schema") ==
            "rebar-phase2-owned-rust-full-public-semantic-source-build-v33-durable-root-provenance-receipt"
            and root.get("status") == "PASS" and root.get("actual_source_phase_count") == 2
            and root.get("actual_compiler_process_count") == 28
            and root.get("distinct_private_source_identity_count") == 18
            and root.get("cross_phase_complete_bridge_elf_byte_identical") is True
            and root.get("cross_phase_complete_engine_elf_byte_identical") is True
            and root.get("hidden_cases_generated") == 0,
            "the genuine V33 authenticated private build provenance changed")
    require(original.get("schema") ==
            "rebar-owned-repaired-rust-original-campaign-v26-durable-publication-receipt"
            and original.get("status") == "PASS"
            and original.get("candidate_status") == "PASS"
            and original.get("candidate_original_oracle_pass") is True
            and original.get("verified_passing_case_count") == 31237
            and original.get("case_execution_denominator") == 31237
            and original.get("completed_suite_count") == 13
            and original.get("semantic_mismatch_count") == 0,
            "the complete frozen 31,237-case original Rust PASS was weakened")
    require(public.get("schema") == "rebar-owned-rust-full-public-correctness-v5-durable-publication-receipt"
            and public.get("status") == "PASS" and public.get("candidate_status") == "PASS"
            and public.get("public_10434_correctness_status") == "PASS"
            and public.get("public_10434_case_count") == 10434
            and public.get("public_10434_verified_passing_case_count") == 10434
            and public.get("public_10434_mismatch_count") == 0
            and public.get("v26_original_verified_passing_case_count") == 31237
            and public.get("v26_original_pass_sha256") == ORIGINAL_PASS["sha256"]
            and public.get("v33_publication_sha256") == V33_PUBLICATION["sha256"]
            and public.get("v33_root_sha256") == V33_ROOT["sha256"]
            and public.get("v5_static_pass_sha256") == STATIC_PASS["sha256"]
            and public.get("hidden_cases_generated") == 0
            and public.get("hidden_cases_read") == 0
            and public.get("proposal_content_opens") == 0
            and public.get("proposal_metadata_probes") == 0,
            "the complete frozen 10,434-case public Rust PASS was weakened")
    require(static.get("schema") == "rebar-phase2-clean-first-party-rust-non-delegation-v5-root-static-audit"
            and static.get("status") == "PASS" and static.get("audited_family") == "rust"
            and static.get("finding_count") == 0
            and static.get("external_regex_packages") == 0
            and static.get("external_regex_libraries") == 0
            and static.get("external_regex_symbols") == 0
            and static.get("cross_family_dependencies") == 0
            and static.get("legacy_private_inspect_getter") is False
            and static.get("candidate_executions") == 0,
            "the genuine V5 Rust static zero-external-engine PASS was weakened")
    for field, expected in (
        ("source_sha256", V33_OWNERS["tools/reproduce_owned_rust_full_public_semantic_source_build_v33.py"]),
        ("protocol_sha256", V33_OWNERS["oracle/phase2/RUST-FULL-PUBLIC-SEMANTIC-SOURCE-BUILD-V33.md"]),
        ("contract_sha256", V33_OWNERS["oracle/phase2/rust-full-public-semantic-source-build-v33.json"]),
        ("combined_engine_source_sha256", SOURCE_IDENTITIES["engine_source"]["sha256"]),
        ("combined_search_source_sha256", SOURCE_IDENTITIES["search_source"]["sha256"]),
        ("materialized_complete_bridge_sha256", SOURCE_IDENTITIES["bridge_source"]["sha256"]),
        ("corrected_public_adapter_sha256", SOURCE_IDENTITIES["adapter"]["sha256"]),
    ):
        require(publication.get(field) == expected and root.get(field) == expected,
                "V33 publication/root disagree on exact owner " + field)
    require(public.get("v33_source_sha256") ==
            V33_OWNERS["tools/reproduce_owned_rust_full_public_semantic_source_build_v33.py"]
            and public.get("v33_protocol_sha256") ==
            V33_OWNERS["oracle/phase2/RUST-FULL-PUBLIC-SEMANTIC-SOURCE-BUILD-V33.md"]
            and public.get("v33_contract_sha256") ==
            V33_OWNERS["oracle/phase2/rust-full-public-semantic-source-build-v33.json"]
            and public.get("v33_adapter_sha256") == SOURCE_IDENTITIES["adapter"]["sha256"]
            and public.get("v33_native_engine_sha256") == NATIVE_IDENTITIES["engine"]["sha256"]
            and public.get("v33_native_bridge_sha256") == NATIVE_IDENTITIES["bridge"]["sha256"],
            "public PASS was not produced by the exact V33 sources/native artifacts")
    private = root.get("root")
    phases = root.get("phase_native_outputs")
    private_sources = root.get("actual_private_source_owners")
    require(type(private) is dict and type(private.get("path")) is str
            and private["path"].startswith("/tmp/rebar-phase2-native-build-v9-rust-")
            and private.get("mode") == "0700" and private.get("uid") == os.getuid()
            and private.get("phase_count") == 2
            and type(phases) is list and type(private_sources) is list
            and len(phases) == 2 and len(private_sources) == 2,
            "V33 no longer has exactly two owner-only authenticated Rust phases")
    for index, name in enumerate(("reference-a", "reference-b")):
        phase = phases[index]
        sources = private_sources[index]
        require(type(phase) is dict and phase.get("name") == name
                and phase.get("mode") == "0700" and phase.get("uid") == os.getuid()
                and type(phase.get("native_outputs")) is list
                and len(phase["native_outputs"]) == 2
                and type(sources) is dict and sources.get("phase") == name
                and type(sources.get("owners")) is dict and len(sources["owners"]) == 9,
                name + ": V33 frozen source/native phase inventory changed")
        for kind, expected in SOURCE_IDENTITIES.items():
            relative = expected["relative"].removeprefix("source/")
            item = sources["owners"].get(relative)
            require(type(item) is dict and item.get("sha256") == expected["sha256"]
                    and item.get("bytes") == expected["bytes"]
                    and item.get("same_inode_readback_verified") is True,
                    name + ": V33 exact private source proof changed: " + kind)
        for native in phase["native_outputs"]:
            require(type(native) is dict and native.get("role") in NATIVE_IDENTITIES,
                    name + ": unknown V33 private native candidate")
            expected = NATIVE_IDENTITIES[native["role"]]
            require(native.get("file_name") == expected["file_name"]
                    and native.get("sha256") == expected["sha256"]
                    and native.get("bytes") == expected["bytes"]
                    and native.get("mode") == expected["mode"]
                    and native.get("uid") == os.getuid() and native.get("nlink") == 1,
                    name + ": V33 native engine or bridge identity changed")
    audits = root.get("actual_reproduced_native_outputs")
    require(type(audits) is dict and set(audits) == {"engine", "bridge"},
            "V33 root proof lost one first-party native engine or bridge")
    for role in ("engine", "bridge"):
        item = audits[role]
        audit = item.get("audit") if type(item) is dict else None
        require(type(item) is dict and item.get("sha256") == NATIVE_IDENTITIES[role]["sha256"]
                and item.get("size_bytes") == NATIVE_IDENTITIES[role]["bytes"]
                and item.get("fresh_independent_inode_count") == 2
                and type(audit) is dict and audit.get("external_regex_dependency_count") == 0
                and audit.get("cross_family_dependency_count") == 0,
                "V33 exact native ELF already contains a forbidden external/cross-family owner")


def verify_lineage(effects: dict[str, int]) -> dict[str, object]:
    owners: dict[str, dict[str, object]] = {}
    for category, records in (("v33_source_owner_reads", V33_OWNERS),
                              ("v5_source_owner_reads", V5_OWNERS),
                              ("v6_source_owner_reads", V6_OWNERS)):
        for path, sha in records.items():
            _, owner = read_public(path, effects, category,
                                   expected={"sha256": sha, "mode": "0600"})
            owners[path] = owner
    receipts = {}
    for path, exact in ((V33_PUBLICATION_PATH, V33_PUBLICATION), (V33_ROOT_PATH, V33_ROOT),
                        (ORIGINAL_PASS_PATH, ORIGINAL_PASS), (PUBLIC_PASS_PATH, PUBLIC_PASS),
                        (STATIC_PASS_PATH, STATIC_PASS)):
        raw, owner = read_public(path, effects, "public_receipt_reads", expected=exact)
        receipts[path] = {"owner": owner, "content": strict_json(raw, path)}
    validate_publication(receipts[V33_PUBLICATION_PATH]["content"],
                         receipts[V33_ROOT_PATH]["content"],
                         receipts[ORIGINAL_PASS_PATH]["content"],
                         receipts[PUBLIC_PASS_PATH]["content"],
                         receipts[STATIC_PASS_PATH]["content"])
    raw, failed_owner = read_public(V6_FAILURE_PATH, effects, "public_receipt_reads",
                                    expected=V6_FAILURE)
    failure = strict_json(raw, V6_FAILURE_PATH)
    require(failure.get("schema") ==
            "rebar-phase2-first-party-rust-live-non-delegation-v6-entry-failure"
            and failure.get("status") == "FAIL"
            and failure.get("error_type") == "LiveProofError"
            and failure.get("message") ==
            "reference-a: genuine guarded candidate worker failed: "
            "\"LIVE_NON_DELEGATION_DENIED: forbidden direct or relative import '_io'\""
            and failure.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and failure.get("candidate_qualified") is False
            and failure.get("final_cases_generated") == 0,
            "the genuine V6 safe-frozen-import failure was hidden or altered")
    effects["v6_failure_reads"] += 1
    receipts[V6_FAILURE_PATH] = {"owner": failed_owner, "content": failure}
    return {"owners": owners, "receipts": receipts,
            "original_case_count": 31237, "public_case_count": 10434,
            "original_status": "PASS", "public_status": "PASS",
            "static_status": "PASS", "external_regex_packages": 0}


def validate_contract(payload: dict[str, object]) -> None:
    freeze, lineage, worker, boundaries = (
        payload.get("source_freeze"), payload.get("preserved_evidence"),
        payload.get("live_worker"), payload.get("boundaries"),
    )
    predecessor = payload.get("immutable_v6")
    require(payload.get("schema") == SCHEMA and payload.get("version") == 7
            and type(freeze) is dict and type(lineage) is dict
            and type(worker) is dict and type(boundaries) is dict
            and type(predecessor) is dict
            and freeze.get("source_path") == SOURCE and freeze.get("protocol_path") == PROTOCOL
            and freeze.get("contract_path") == CONTRACT and freeze.get("sole_owned_file_count") == 3
            and lineage.get("original_pass_sha256") == ORIGINAL_PASS["sha256"]
            and lineage.get("original_case_count") == 31237
            and lineage.get("public_pass_sha256") == PUBLIC_PASS["sha256"]
            and lineage.get("public_case_count") == 10434
            and lineage.get("static_pass_sha256") == STATIC_PASS["sha256"]
            and lineage.get("v33_publication_sha256") == V33_PUBLICATION["sha256"]
            and lineage.get("v33_root_sha256") == V33_ROOT["sha256"]
            and worker.get("phase_count") == 2
            and worker.get("candidate_process_count") == 2
            and worker.get("reference_process_count") == 0
            and worker.get("operation_names") == list(EXPECTED_OPERATIONS)
            and worker.get("operation_count_per_phase") == len(EXPECTED_OPERATIONS)
            and worker.get("program_sha256") == digest(WORKER_PROGRAM.encode("utf-8"))
            and worker.get("stdlib_regex_module_allowed") is False
            and worker.get("external_regex_engine_allowed") is False
            and worker.get("cross_family_engine_allowed") is False
            and boundaries.get("root_only_live_operation") is True
            and boundaries.get("source_only_candidate_execution") is False
            and boundaries.get("root_result_path") == RESULT_PATH
            and boundaries.get("final_cases_generated") == 0
            and boundaries.get("performance") == "NOT MEASURED"
            and boundaries.get("winner_selected") is False
            and predecessor.get("failure_receipt_sha256") == V6_FAILURE["sha256"]
            and predecessor.get("failure_status") == "FAIL"
            and predecessor.get("failure_message") ==
            "LIVE_NON_DELEGATION_DENIED: forbidden direct or relative import '_io'"
            and predecessor.get("failure_hidden") is False,
            "V7 contract weakened evidence preservation or live process containment")
    for name, expected in (
        ("adapter_sha256", SOURCE_IDENTITIES["adapter"]["sha256"]),
        ("engine_source_sha256", SOURCE_IDENTITIES["engine_source"]["sha256"]),
        ("bridge_source_sha256", SOURCE_IDENTITIES["bridge_source"]["sha256"]),
        ("search_source_sha256", SOURCE_IDENTITIES["search_source"]["sha256"]),
        ("native_engine_sha256", NATIVE_IDENTITIES["engine"]["sha256"]),
        ("native_bridge_sha256", NATIVE_IDENTITIES["bridge"]["sha256"]),
    ):
        require(worker.get(name) == expected, "V7 worker changed its exact first-party owner " + name)


def zero_source_effects(effects: dict[str, int], *, verify: bool = False) -> None:
    allowed = {"approved_owner_reads"}
    if verify:
        allowed |= {"v33_source_owner_reads", "v5_source_owner_reads",
                    "v6_source_owner_reads", "v6_failure_reads", "public_receipt_reads"}
    for key, value in effects.items():
        if key not in allowed:
            require(value == 0, "source-only mode escaped its denied boundary: " + key)
    if verify:
        require(effects["approved_owner_reads"] == 18
                and effects["v33_source_owner_reads"] == 3
                and effects["v5_source_owner_reads"] == 3
                and effects["v6_source_owner_reads"] == 3
                and effects["v6_failure_reads"] == 1
                and effects["public_receipt_reads"] == 6,
                "source-only verification opened anything beyond 18 exact public owners")


def source_verify(options: dict[str, object]) -> dict[str, object]:
    require_interpreter()
    pins = {SOURCE: exact_sha(options.get("source_sha256"), "V7 source"),
            PROTOCOL: exact_sha(options.get("protocol_sha256"), "V7 protocol"),
            CONTRACT: exact_sha(options.get("contract_sha256"), "V7 contract")}
    require(len(set(pins.values())) == 3, "independently supply three distinct full owner pins")
    with SourceWall() as wall:
        content = {}
        owners = {}
        for path in (SOURCE, PROTOCOL, CONTRACT):
            raw, owner = read_public(path, wall.effects, "approved_owner_reads",
                                     expected={"sha256": pins[path], "mode": "0600"})
            content[path], owners[path] = raw, owner
        contract = strict_json(content[CONTRACT], CONTRACT)
        validate_contract(contract)
        freeze = contract["source_freeze"]
        require(type(freeze) is dict and freeze.get("source_sha256") == pins[SOURCE]
                and freeze.get("protocol_sha256") == pins[PROTOCOL],
                "V7 machine contract does not independently bind source/protocol pins")
        evidence = verify_lineage(wall.effects)
        counts = dict(wall.effects)
        zero_source_effects(counts, verify=True)
    return {"schema": SCHEMA + "-source-verification", "status": "PASS",
            "phase": "SOURCE ONLY; NO CANDIDATE, NATIVE LIBRARY, OR PRIVATE ROOT OPENED",
            "owners": owners, "preserved_original_case_count": evidence["original_case_count"],
            "preserved_public_case_count": evidence["public_case_count"],
            "preserved_original_status": "PASS", "preserved_public_status": "PASS",
            "preserved_static_status": "PASS", "live_runtime_non_delegation": "NOT RUN",
            "candidate_executions": 0, "candidate_processes": 0, "private_build_roots_opened": 0,
            "final_cases_generated": 0, "performance": "NOT MEASURED",
            "winner_selected": False, "effects": counts}


def module_allowed(name: object) -> bool:
    return (type(name) is str and bool(name) and name.split(".", 1)[0] in ALLOWED_IMPORT_ROOTS
            and name.split(".", 1)[0] not in FORBIDDEN_ROOTS
            and (not name.startswith("candidates.") or name in {
                "candidates.rust_candidate", "candidates._rust_bridge",
            }))


def approved_worker_open(path: object, phase: str) -> bool:
    if type(path) is not str or phase not in {"reference-a", "reference-b"}:
        return False
    prefix = "/tmp/rebar-phase2-native-build-v9-rust-"
    if path == "/proc/self/maps":
        return True
    if path.startswith(PINNED_STDLIB):
        lowered = path.casefold()
        return not any(item in lowered for item in (
            "/re/", "/regex/", "/_sre", "/inspect.py", "/tokenize.py",
        ))
    if not path.startswith(prefix):
        return False
    marker = "/" + phase + "/"
    if marker not in path:
        return False
    suffix = path.split(marker, 1)[1]
    return suffix in {
        "source/candidates/rust_candidate.py",
        "source/candidates/__pycache__/rust_candidate.cpython-314.pyc",
        "source/candidates/rust/py_bridge.c",
        "source/candidates/rust/src/lib.rs",
        "source/candidates/rust/src/search.rs",
        "native/_rust_engine.so",
        "native/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
    }


def reject_forbidden_map(path: str) -> bool:
    lowered = path.casefold()
    return not any(fragment in lowered for fragment in FORBIDDEN_MAP_FRAGMENTS)


def source_self_test() -> dict[str, object]:
    require_interpreter()
    positive, hostile = 0, 0

    def accept(value: object, description: str) -> None:
        nonlocal positive
        require(value is True, "clean source-only control unexpectedly failed: " + description)
        positive += 1

    def reject(value: object, description: str) -> None:
        nonlocal hostile
        require(value is False, "hostile source-only control unexpectedly passed: " + description)
        hostile += 1

    with SourceWall() as wall:
        try:
            worker_tree = ast.parse(WORKER_PROGRAM, filename="<frozen-rust-live-worker-v7>")
        except (SyntaxError, RecursionError, ValueError) as error:
            raise LiveProofError("frozen live worker is not valid Python source") from error
        imported = set()
        pending = [worker_tree]
        while pending:
            node = pending.pop()
            pending.extend(ast.iter_child_nodes(node))
            if isinstance(node, ast.Import):
                imported.update(item.name for item in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module or "")
        require(imported == {"sys", "builtins", "hashlib", "os", "types"},
                "worker bootstrap imports non-frozen modules before the live audit hook")
        require("sys.addaudithook(_audit)" in WORKER_PROGRAM
                and WORKER_PROGRAM.index("sys.addaudithook(_audit)")
                < WORKER_PROGRAM.index('candidate = _guarded_import("candidates.rust_candidate"')
                and 'json.loads(' not in WORKER_PROGRAM
                and '/proc/self/maps' in WORKER_PROGRAM
                and 'builtins.__import__ = _guarded_import' in WORKER_PROGRAM,
                "live audit/import walls are not installed before candidate/native import")
        for root in sorted(ALLOWED_IMPORT_ROOTS):
            accept(module_allowed(root), "allowed first-party/stdlib module " + root)
        accept(module_allowed("candidates.rust_candidate"), "owned Rust adapter")
        accept(module_allowed("candidates._rust_bridge"), "owned Rust native bridge")
        for root in sorted(FORBIDDEN_ROOTS):
            reject(module_allowed(root), "forbidden foreign module " + root)
            reject(module_allowed(root + ".nested"), "forbidden transitive module " + root)
            reject(module_allowed(root + ".engine.dispatch"),
                   "forbidden multi-hop foreign module " + root)
        for target in (
            "candidates.zig_candidate", "candidates._zig_bridge",
            "candidates.cpp_candidate", "candidates._cpp_bridge",
            "candidates.go_candidate", "candidates._go_bridge",
            "candidates.fortran_candidate", "candidates._fortran_bridge",
            "candidates.vm_candidate", "candidates._vm_native",
            "foreign_engine", "", "candidates.rust_candidate.borrowed",
        ):
            reject(module_allowed(target), "foreign candidate or unresolved module " + target)
        for phase in ("reference-a", "reference-b"):
            root = "/tmp/rebar-phase2-native-build-v9-rust-fixture/" + phase + "/"
            for suffix in (
                "source/candidates/rust_candidate.py",
                "source/candidates/rust/py_bridge.c",
                "source/candidates/rust/src/lib.rs",
                "source/candidates/rust/src/search.rs",
                "native/_rust_engine.so",
                "native/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
            ):
                accept(approved_worker_open(root + suffix, phase), "exact private owner " + suffix)
            for path in (
                root + "source/candidates/../holdout.json",
                root + "native/libpcre2.so",
                root + "native/_zig_probe.so",
                root + "source/candidates/another.py",
                "/home/dev-user/src/rebar/oracle/phase3/final.json",
                "/tmp/rebar-phase2-native-build-v9-rust-fixture/reference-z/native/_rust_engine.so",
                "/tmp/foreign-engine.so",
            ):
                reject(approved_worker_open(path, phase), "unowned worker file " + path)
        accept(approved_worker_open("/proc/self/maps", "reference-a"), "read-only native maps")
        accept(approved_worker_open(PINNED_STDLIB + "enum.py", "reference-a"),
               "pinned ordinary stdlib source")
        for filename in ("re/__init__.py", "regex/__init__.py", "_sre.so",
                         "inspect.py", "tokenize.py"):
            reject(approved_worker_open(PINNED_STDLIB + filename, "reference-a"),
                   "forbidden stdlib matcher/introspection " + filename)
        for fragment in FORBIDDEN_MAP_FRAGMENTS:
            reject(reject_forbidden_map("/tmp/" + fragment + "/engine.so"),
                   "external regex/cross-family native mapping " + fragment)
        accept(reject_forbidden_map("/tmp/owned/_rust_engine.so"), "owned Rust native mapping")
        for malicious in ("../private", ".git/config", "performance/benchmark.json",
                          "oracle/holdout.json", "oracle/hidden/cases.json",
                          "oracle/phase2/evidence/fake.json", "candidates/rust_candidate.py",
                          "/tmp/private", "oracle/phase3/final-plan.json"):
            try:
                checked_public(malicious)
            except (LiveProofError, ValueError, TypeError):
                hostile += 1
            else:
                raise LiveProofError("hostile public path escaped " + malicious)
        require(positive >= 30 and hostile >= 100,
                f"live worker hostile source-only coverage shrank: {positive}/{hostile}")
        effects = dict(wall.effects)
        zero_source_effects(effects)
    return {"schema": SCHEMA + "-source-self-test", "status": "PASS",
            "positive_controls": positive, "hostile_controls": hostile,
            "worker_program_sha256": digest(WORKER_PROGRAM.encode("utf-8")),
            "worker_import_hook_precedes_candidate_import": True,
            "worker_starts_without_stdlib_re_or_sre": True,
            "worker_never_imports_json_or_stdlib_regex": True,
            "foreign_packages_native_engines_cross_family_and_processes_rejected": True,
            "candidate_sources_read": 0, "private_build_roots_opened": 0,
            "candidate_processes": 0, "candidate_executions": 0,
            "live_runtime_non_delegation": "NOT RUN",
            "final_cases_generated": 0, "performance": "NOT MEASURED",
            "winner_selected": False, "effects": effects}


def authenticate_private(root_provenance: dict[str, object], effects: dict[str, int]
                         ) -> list[dict[str, object]]:
    owner = root_provenance["root"]
    require(type(owner) is dict and type(owner.get("path")) is str,
            "V33 root provenance is not a candidate-source authority")
    root_path = owner["path"]
    prefix = "/tmp/rebar-phase2-native-build-v9-rust-"
    require(root_path.startswith(prefix) and "/" not in root_path[len(prefix):],
            "reject private roots outside the exact V33 first-party build prefix")
    root = _OPEN(root_path, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        root_identity = _FSTAT(root)
        require(root_identity.st_dev == owner["device"] and root_identity.st_ino == owner["inode"]
                and root_identity.st_uid == os.getuid()
                and stat.S_IMODE(root_identity.st_mode) == 0o700,
                "V33 private build root device/inode/ownership changed")
        effects["private_build_root_opens"] += 1
        answer = []
        for index, name in enumerate(("reference-a", "reference-b")):
            phase = root_provenance["phase_native_outputs"][index]
            source_owners = root_provenance["actual_private_source_owners"][index]["owners"]
            phase_fd = _OPEN(name, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                             dir_fd=root)
            try:
                identity = _FSTAT(phase_fd)
                require(identity.st_dev == phase["device"] and identity.st_ino == phase["inode"]
                        and identity.st_uid == os.getuid()
                        and stat.S_IMODE(identity.st_mode) == 0o700,
                        name + ": private V33 phase device/inode/ownership changed")
                effects["private_phase_opens"] += 1
                owners = {}
                for kind, expected in SOURCE_IDENTITIES.items():
                    relative = expected["relative"]
                    original = source_owners[relative.removeprefix("source/")]
                    _, current = read_at(phase_fd, tuple(relative.split("/")),
                                         name + "/" + relative, effects,
                                         "private_candidate_source_reads",
                                         expected={"sha256": expected["sha256"],
                                                   "bytes": expected["bytes"],
                                                   "mode": expected["mode"],
                                                   "device": original["device"],
                                                   "inode": original["inode"]})
                    owners[kind] = current
                for item in phase["native_outputs"]:
                    kind = item["role"]
                    expected = NATIVE_IDENTITIES[kind]
                    _, current = read_at(phase_fd, tuple(expected["relative"].split("/")),
                                         name + "/" + expected["relative"], effects,
                                         "private_native_reads",
                                         expected={"sha256": expected["sha256"],
                                                   "bytes": expected["bytes"],
                                                   "mode": expected["mode"],
                                                   "device": item["device"],
                                                   "inode": item["inode"]})
                    owners[kind] = current
                answer.append({"name": name, "path": root_path + "/" + name,
                               "device": phase["device"], "inode": phase["inode"],
                               "owners": owners})
            finally:
                _CLOSE(phase_fd)
        return answer
    finally:
        _CLOSE(root)


def run_worker(phase: dict[str, object], effects: dict[str, int]) -> dict[str, object]:
    require(type(phase.get("name")) is str and type(phase.get("path")) is str,
            "candidate worker requires an authenticated V33 phase")
    command = [
        PINNED_PYTHON, "-I", "-B", "-S", "-c", WORKER_PROGRAM,
        phase["name"], phase["path"],
        SOURCE_IDENTITIES["adapter"]["sha256"],
        SOURCE_IDENTITIES["bridge_source"]["sha256"],
        SOURCE_IDENTITIES["engine_source"]["sha256"],
        SOURCE_IDENTITIES["search_source"]["sha256"],
        NATIVE_IDENTITIES["bridge"]["sha256"],
        NATIVE_IDENTITIES["engine"]["sha256"],
    ]
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, cwd="/tmp",
                               env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "PYTHONHASHSEED": "0"},
                               close_fds=True)
    effects["subprocesses"] += 1
    effects["candidate_processes"] += 1
    stdout, stderr = process.communicate()
    require(type(stdout) is bytes and 0 < len(stdout) <= MAX_RESULT
            and type(stderr) is bytes and len(stderr) <= MAX_RESULT,
            phase["name"] + ": live worker produced invalid bounded output")
    try:
        result = ast.literal_eval(stdout.decode("utf-8"))
    except (SyntaxError, ValueError, UnicodeError, RecursionError) as error:
        raise LiveProofError(phase["name"] + ": live worker output was not exact literal data") from error
    require(type(result) is dict and process.returncode == 0 and result.get("status") == "PASS",
            phase["name"] + ": genuine guarded candidate worker failed: "
            + repr(result.get("message") if type(result) is dict else stderr[:512]))
    require(result.get("schema") == "rebar-phase2-rust-live-worker-v7"
            and result.get("phase") == phase["name"]
            and result.get("initial_forbidden_modules") == ()
            and result.get("final_forbidden_modules") == ()
            and result.get("audit_hook_installed_before_candidate_import") is True
            and result.get("guarded_python_import_installed") is True
            and result.get("candidate_adapter_module") == "candidates.rust_candidate"
            and result.get("native_bridge_module") == "candidates._rust_bridge"
            and result.get("candidate_native_bridge_path") ==
            phase["path"] + "/native/" + NATIVE_IDENTITIES["bridge"]["file_name"]
            and result.get("candidate_native_engine_path") ==
            phase["path"] + "/native/" + NATIVE_IDENTITIES["engine"]["file_name"]
            and result.get("operation_names") == EXPECTED_OPERATIONS
            and result.get("operation_count") == len(EXPECTED_OPERATIONS)
            and result.get("candidate_native_copyreg_import_observed") is True
            and result.get("runtime_non_delegation") ==
            "ESTABLISHED FOR THIS EXACT CANDIDATE AND OPERATION SET",
            phase["name"] + ": candidate runtime hook/native-owner/operation proof is incomplete")
    for key in ("forbidden_module_import_attempts", "external_native_load_attempts",
                "cross_family_load_count", "subprocess_attempts", "network_attempts",
                "outside_open_attempts", "holdout_reads", "proposal_content_opens",
                "proposal_metadata_probes", "hidden_case_reads", "benchmark_reads",
                "external_regex_packages", "external_regex_libraries"):
        require(result.get(key) == 0, phase["name"] + ": live candidate violated " + key)
    observed = result.get("observed_imports")
    opens = result.get("observed_file_opens")
    libraries = result.get("loaded_native_objects")
    owners = result.get("source_and_native_owners")
    require(type(observed) is tuple and type(opens) is tuple
            and type(libraries) is tuple and len(libraries) == 2
            and set(libraries) == {
                phase["path"] + "/native/" + NATIVE_IDENTITIES["engine"]["file_name"],
                phase["path"] + "/native/" + NATIVE_IDENTITIES["bridge"]["file_name"],
            }
            and type(owners) is dict and set(owners) == set(phase["owners"]),
            phase["name"] + ": runtime did not preserve exact live imports/native owners")
    for name, owner in phase["owners"].items():
        candidate = owners[name]
        require(type(candidate) is dict and candidate.get("sha256") == owner["sha256"]
                and candidate.get("bytes") == owner["bytes"]
                and candidate.get("device") == owner["device"]
                and candidate.get("inode") == owner["inode"]
                and candidate.get("mode") == owner["mode"],
                phase["name"] + ": live worker swapped a source/native owner: " + name)
    for item in observed:
        require(type(item) is tuple and len(item) == 3 and module_allowed(item[0]),
                phase["name"] + ": runtime imported an external/cross-family module")
    for item in opens:
        require(type(item) is tuple and len(item) == 2
                and approved_worker_open(item[0], phase["name"]),
                phase["name"] + ": runtime opened an unrelated/private/final owner")
    effects["candidate_imports"] += 1
    effects["native_library_loads"] += 2
    effects["candidate_operations"] += len(EXPECTED_OPERATIONS)
    return result


def publish_exclusive(payload: dict[str, object], effects: dict[str, int]) -> dict[str, object]:
    raw = canonical(payload)
    require(0 < len(raw) <= MAX_RESULT, "runtime-proof publication exceeds frozen bounds")
    path = ROOT + "/" + RESULT_PATH
    descriptor = _OPEN(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
                       0o600)
    try:
        position = 0
        while position < len(raw):
            count = os.write(descriptor, raw[position:])
            require(count > 0, "exclusive runtime proof write failed")
            position += count
        os.fsync(descriptor)
        owner = _FSTAT(descriptor)
        require(stat.S_ISREG(owner.st_mode) and owner.st_uid == os.getuid()
                and owner.st_nlink == 1 and stat.S_IMODE(owner.st_mode) == 0o600
                and owner.st_size == len(raw), "runtime proof did not preserve its exclusive owner")
    finally:
        _CLOSE(descriptor)
    directory = _OPEN(ROOT + "/oracle/phase2/evidence",
                      os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        os.fsync(directory)
    finally:
        _CLOSE(directory)
    effects["workspace_mutations"] += 1
    return {"path": RESULT_PATH, "sha256": digest(raw), "bytes": len(raw),
            "device": owner.st_dev, "inode": owner.st_ino, "mode": "0600",
            "exclusive_creation": True, "file_fsync_completed": True,
            "directory_fsync_completed": True}


def run_live(options: dict[str, object]) -> dict[str, object]:
    require_interpreter()
    require(options.get("root_authorized") is True,
            "actual candidate/live-engine execution is ROOT-AGENT-ONLY")
    pushed = exact_sha(options.get("pushed_source_sha256"), "pushed V7 source")
    effects = fresh_effects()
    _, source_owner = read_public(SOURCE, effects, "approved_owner_reads",
                                  expected={"sha256": pushed, "mode": "0600"})
    raw, _ = read_public(CONTRACT, effects, "approved_owner_reads")
    contract = strict_json(raw, CONTRACT)
    validate_contract(contract)
    freeze = contract["source_freeze"]
    require(type(freeze) is dict and freeze.get("source_sha256") == pushed,
            "root live operation is not bound to exact independently pushed source")
    lineage = verify_lineage(effects)
    private_root = lineage["receipts"][V33_ROOT_PATH]["content"]
    phases = authenticate_private(private_root, effects)
    outcomes = [run_worker(phase, effects) for phase in phases]
    require(effects["approved_owner_reads"] == 29
            and effects["v33_source_owner_reads"] == 3
            and effects["v5_source_owner_reads"] == 3
            and effects["v6_source_owner_reads"] == 3
            and effects["v6_failure_reads"] == 1
            and effects["public_receipt_reads"] == 6
            and effects["private_build_root_opens"] == 1
            and effects["private_phase_opens"] == 2
            and effects["private_candidate_source_reads"] == 8
            and effects["private_native_reads"] == 4
            and effects["candidate_processes"] == 2
            and effects["candidate_operations"] == 2 * len(EXPECTED_OPERATIONS)
            and effects["candidate_imports"] == 2
            and effects["native_library_loads"] == 4
            and effects["subprocesses"] == 2,
            "live proof source/native/worker/operation accounting does not close")
    for forbidden in (
        "forbidden_module_imports", "external_engine_loads", "cross_family_loads",
        "reference_workers", "archive_reads", "archive_decompressions", "holdout_reads",
        "proposal_content_opens", "proposal_metadata_probes", "hidden_case_reads",
        "benchmark_reads", "network_requests", "compiler_processes", "clock_samples",
        "git_reads",
    ):
        require(effects[forbidden] == 0, "live proof escaped its frozen boundary: " + forbidden)
    published_effects = dict(effects)
    published_effects["workspace_mutations"] = 1
    receipt = {
        "schema": SCHEMA + "-durable-runtime-proof", "status": "PASS",
        "source_owner": source_owner, "pushed_source_sha256": pushed,
        "family": "rust", "independent_candidate_family_count": 1,
        "minimum_required_independent_family_count": 3,
        "all_required_candidate_families_available": False,
        "original_v26_status": "PASS", "original_v26_case_count": 31237,
        "original_v26_publication_sha256": ORIGINAL_PASS["sha256"],
        "original_v26_architecture": "V30",
        "exact_v33_original_p0_status": "NOT MEASURED",
        "public_v33_status": "PASS", "public_v33_case_count": 10434,
        "public_v33_mismatch_count": 0,
        "public_v33_publication_sha256": PUBLIC_PASS["sha256"],
        "v5_static_status": "PASS", "v5_static_publication_sha256": STATIC_PASS["sha256"],
        "immutable_v6_failure_status": "FAIL",
        "immutable_v6_failure_sha256": V6_FAILURE["sha256"],
        "immutable_v6_failure_hidden": False,
        "immutable_v6_safe_import_rejection": "_io",
        "v33_native_build_status": "PASS",
        "v33_native_build_publication_sha256": V33_PUBLICATION["sha256"],
        "v33_native_build_root_sha256": V33_ROOT["sha256"],
        "exact_first_party_sources": {
            name: {"sha256": owner["sha256"], "bytes": owner["bytes"]}
            for name, owner in SOURCE_IDENTITIES.items()
        },
        "exact_first_party_native": {
            name: {"sha256": owner["sha256"], "bytes": owner["bytes"]}
            for name, owner in NATIVE_IDENTITIES.items()
        },
        "live_candidate_phase_count": 2,
        "live_candidate_process_count": 2,
        "reference_process_count": 0,
        "operation_names": list(EXPECTED_OPERATIONS),
        "live_operation_count_per_phase": len(EXPECTED_OPERATIONS),
        "live_total_operation_count": 2 * len(EXPECTED_OPERATIONS),
        "live_worker_program_sha256": digest(WORKER_PROGRAM.encode("utf-8")),
        "live_phases": outcomes,
        "forbidden_preloaded_module_count": 0,
        "forbidden_runtime_module_count": 0,
        "external_regex_package_count": 0,
        "external_regex_library_count": 0,
        "cross_family_native_owner_count": 0,
        "candidate_runtime_non_delegation_status": "PASS",
        "runtime_non_delegation":
            "ESTABLISHED FOR EXACT V33 RUST CANDIDATE AND FROZEN REPRESENTATIVE OPERATION SET",
        "candidate_qualified": False,
        "candidate_qualification_blocker": "EXACT V33 ORIGINAL 31,237-CASE ORACLE NOT RUN",
        "qualified_independent_family_count": 0,
        "performance": "NOT MEASURED",
        "final_cases_generated": 0,
        "winner_selected": False,
        "effects": published_effects,
    }
    receipt["publication"] = {"path": RESULT_PATH, "exclusive_creation": True,
                               "file_fsync_completed": True,
                               "directory_fsync_completed": True}
    owner = publish_exclusive(receipt, effects)
    require(effects["workspace_mutations"] == 1,
            "root live proof wrote anything beyond its one exclusive durable receipt")
    return {"schema": SCHEMA + "-root-live-publication", "status": "PASS",
            "publication_owner": owner,
            "runtime_non_delegation":
                "ESTABLISHED FOR EXACT V33 RUST CANDIDATE AND FROZEN REPRESENTATIVE OPERATION SET",
            "candidate_runtime_non_delegation_status": "PASS",
            "live_candidate_process_count": 2,
            "live_total_operation_count": 2 * len(EXPECTED_OPERATIONS),
            "original_v26_case_count": 31237,
            "exact_v33_original_p0_status": "NOT MEASURED",
            "public_v33_case_count": 10434,
            "candidate_qualified": False,
            "qualified_independent_family_count": 0,
            "performance": "NOT MEASURED", "final_cases_generated": 0,
            "winner_selected": False, "effects": effects}


def parse_arguments(arguments: list[str]) -> dict[str, object]:
    require(bool(arguments), "choose --self-test, --verify-source, or root-only --run")
    mode = arguments[0]
    require(mode in {"--self-test", "--verify-source", "--run"},
            "unrecognized V7 source verification or live execution mode")
    answer = {"mode": mode}
    mapping = {"--source-sha256": "source_sha256", "--protocol-sha256": "protocol_sha256",
               "--contract-sha256": "contract_sha256",
               "--pushed-source-sha256": "pushed_source_sha256"}
    at = 1
    while at < len(arguments):
        option = arguments[at]
        if option == "--root-authorized":
            require(mode == "--run" and "root_authorized" not in answer,
                    "root authority belongs exclusively to one later actual live run")
            answer["root_authorized"] = True
            at += 1
            continue
        require(option in mapping and at + 1 < len(arguments), "unexpected V7 option " + option)
        name = mapping[option]
        require(name not in answer, "duplicate independently supplied V7 pin " + option)
        answer[name] = arguments[at + 1]
        at += 2
    if mode == "--self-test":
        require(set(answer) == {"mode"}, "source-only hostile controls cannot authorize candidate reads")
    elif mode == "--verify-source":
        require(set(answer) == {"mode", "source_sha256", "protocol_sha256", "contract_sha256"},
                "source-only verification requires exactly three independently supplied owner pins")
    else:
        require(set(answer) == {"mode", "root_authorized", "pushed_source_sha256"},
                "live candidate operation requires root authority and the exact pushed V7 source")
    return answer


def main(arguments: list[str] | None = None) -> int:
    try:
        options = parse_arguments(list(sys.argv[1:] if arguments is None else arguments))
        if options["mode"] == "--self-test":
            result = source_self_test()
        elif options["mode"] == "--verify-source":
            result = source_verify(options)
        else:
            result = run_live(options)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except (Exception, KeyboardInterrupt) as error:
        result = {"schema": SCHEMA + "-entry-failure", "status": "FAIL",
                  "error_type": type(error).__name__, "message": str(error)[:2048],
                  "candidate_qualified": False,
                  "runtime_non_delegation": "NOT ESTABLISHED",
                  "performance": "NOT MEASURED", "final_cases_generated": 0,
                  "winner_selected": False}
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
