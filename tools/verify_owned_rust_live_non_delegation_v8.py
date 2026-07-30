#!/usr/bin/env python3
"""Freeze bounded fresh-process live ownership checks for the exact V33 Rust engine."""

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
SOURCE = "tools/verify_owned_rust_live_non_delegation_v8.py"
PROTOCOL = "oracle/phase2/RUST-LIVE-NON-DELEGATION-V8.md"
CONTRACT = "oracle/phase2/rust-live-non-delegation-v8.json"
SCHEMA = "rebar-phase2-first-party-rust-live-non-delegation-v8"
RESULT = "oracle/phase2/evidence/rust-live-non-delegation-v8-actual-runtime-proof.json"
MAX_SOURCE = 4 * 1024 * 1024
MAX_RESPONSE = 256 * 1024
MAX_RECEIPT = 1024 * 1024
HEX = frozenset("0123456789abcdef")
OPEN, READ, FSTAT, CLOSE = os.open, os.read, os.fstat, os.close

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
V7_OWNERS = {
    "tools/verify_owned_rust_live_non_delegation_v7.py":
        "b401815315f91e4edac1d3026b99d11dff30bbdfe4ae1030a160d3cd91954311",
    "oracle/phase2/RUST-LIVE-NON-DELEGATION-V7.md":
        "e89e11bdaad39a7d836b45a535306e273f8c34f49eb4eefdb9a3de4c8d350ce1",
    "oracle/phase2/rust-live-non-delegation-v7.json":
        "a58f5ccea2b0d514344d5dab301ae7c6abc227c56119aa0a61e449dfab90c542",
}
PROVEN_SOURCE = {
    "tools/audit_from_scratch.py":
        "4c47a77cf096df354e59d03096447c56bff890389869c6a75667a36c8471d024",
}
PUBLIC_RECEIPTS = {
    "v33_publication": {
        "path": "oracle/phase2/evidence/native-source-build-v33-rust-phase2-v33-rust-"
                "full-public-semantic-source-root-provenance-publication-receipt.json",
        "sha256": "cfe1464e1e8ce96bfa514b15cf96879a0642686987159dd79c15f4d9db408749",
        "bytes": 6696, "device": 2064, "inode": 525066, "mode": "0600",
    },
    "v33_root": {
        "path": "oracle/phase2/evidence/native-source-build-v33-rust-phase2-v33-rust-"
                "full-public-semantic-source-root-provenance-root-provenance-receipt.json",
        "sha256": "7122c9bdff731be0f68602a4a216c1fa9700e6a78f9da9b534eeaef282c64c1c",
        "bytes": 80421, "device": 2064, "inode": 525067, "mode": "0600",
    },
    "original": {
        "path": "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v30-rust-"
                "complete-semantic-source-root-provenance-original-p0-v26-publication-receipt.json",
        "sha256": "84804409997794ce7e8bfff67ca8ffdcada9651a1660bda2654742befbba20f5",
        "bytes": 12055, "device": 2064, "inode": 525046, "mode": "0600",
    },
    "v33_original": {
        "path": "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v33-rust-"
                "full-public-semantic-source-root-provenance-original-p0-v28-publication-receipt.json",
        "sha256": "5204823a291ec01890913218582ff978cbe923dd5c787c8d6ae68a9790c43064",
        "bytes": 12067, "device": 2064, "inode": 526161, "mode": "0600",
    },
    "public": {
        "path": "oracle/phase2/evidence/rust-full-public-correctness-v5-v33-full-public-v5-run-001-"
                "publication-receipt.json",
        "sha256": "8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9",
        "bytes": 6889, "device": 2064, "inode": 525451, "mode": "0600",
    },
    "static": {
        "path": "oracle/phase2/evidence/rust-clean-non-delegation-v5-actual-source-audit.json",
        "sha256": "a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203",
        "bytes": 16427, "device": 2064, "inode": 525089, "mode": "0600",
    },
    "v6_failure": {
        "path": "oracle/phase2/evidence/rust-live-non-delegation-v6-actual-runtime-failure.json",
        "sha256": "9dcc4d6dbf81ed828189cacf8e981de788190bcf9912d01b8858e6841397286b",
        "bytes": 416, "device": 2064, "inode": 525883, "mode": "0600",
    },
    "v7_failure": {
        "path": "oracle/phase2/evidence/rust-live-non-delegation-v7-actual-runtime-failure.json",
        "sha256": "ba92eb59cc0dc188f2990a4d2bdacab59824d15613b36cafd700712306e12660",
        "bytes": 312, "device": 2064, "inode": 526001, "mode": "0600",
    },
}
SOURCE_OWNERS = {
    "adapter": ("source/candidates/rust_candidate.py",
                "f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227", 34039, "0600"),
    "bridge_source": ("source/candidates/rust/py_bridge.c",
                      "f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e", 178472, "0600"),
    "engine_source": ("source/candidates/rust/src/lib.rs",
                      "7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38", 189493, "0600"),
    "search_source": ("source/candidates/rust/src/search.rs",
                      "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7", 24305, "0600"),
}
NATIVE_OWNERS = {
    "bridge": ("native/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
               "ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000", 148728, "0700"),
    "engine": ("native/_rust_engine.so",
               "e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8", 672440, "0600"),
}
COHORTS = (
    ("entry", ("compiled_named_unicode_search", "module_search_cache", "module_match")),
    ("types", ("module_fullmatch", "bytes_memoryview_search", "scoped_unicode_category")),
    ("unicode", ("verbose_named_escape_comment", "findall_named_digits", "finditer_spans")),
    ("replacement", ("split_digits", "sub_callback", "subn_named_template")),
    ("scanners", ("match_expand_named_template", "pattern_scanner_search", "public_lexical_scanner")),
    ("advanced", ("bytes_named_substitution", "lookbehind_search", "backreference_fullmatch")),
    ("lifecycle", ("bytes_ignorecase", "cache_lifecycle", "match_reduce_copyreg")),
    ("serialization", ("scanner_reduce_rejected",)),
)
EXPECTED_OPERATIONS = tuple(item for _, operations in COHORTS for item in operations)
FORBIDDEN = frozenset({"re", "_sre", "inspect", "tokenize", "regex", "re2", "pcre", "pcre2",
                       "onig", "oniguruma", "rure", "hyperscan", "ahocorasick", "ctypes",
                       "cffi", "importlib", "subprocess", "socket"})
ALLOWED = frozenset({"abc", "_abc", "_blake2", "_codecs", "_collections", "_collections_abc",
                     "_contextvars", "_functools", "_hashlib", "_io", "_operator", "_py_warnings",
                     "_signal", "_stat", "_thread", "_types", "_warnings", "_weakref", "builtins",
                     "candidates", "codecs", "collections", "contextvars", "copyreg", "encodings",
                     "enum", "errno", "functools", "genericpath", "hashlib", "itertools", "keyword",
                     "linecache", "marshal", "operator", "os", "posix", "posixpath", "reprlib",
                     "stat", "sys", "time", "types", "unicodedata", "warnings", "zipimport"})
DENIED_MAPS = ("libpcre", "libonig", "libre2", "libhyperscan", "libhs.so", "librure",
               "_sre.", "/regex/", "/candidates/_vm", "/candidates/_zig",
               "/candidates/_cpp", "/candidates/_go", "/candidates/_fortran")

WORKER_PROGRAM = r'''
import sys

_forbidden = {"re", "_sre", "inspect", "tokenize", "regex", "re2", "pcre", "pcre2",
              "onig", "oniguruma", "rure", "hyperscan", "ahocorasick", "ctypes",
              "cffi", "importlib", "subprocess", "socket"}
_starting = tuple(sorted(name for name in sys.modules
                         if name.split(".", 1)[0] in _forbidden))
if _starting:
    sys.stdout.write(repr({"status": "FAIL", "message": "forbidden preloaded module",
                           "modules": _starting}) + "\n")
    raise SystemExit(1)

import builtins
import hashlib
import os
import types

if any(name.split(".", 1)[0] in _forbidden for name in sys.modules):
    raise SystemExit("bootstrap loaded a forbidden matcher")
_phase, _phase_path, _cohort, _adapter_sha, _bridge_source_sha, _engine_source_sha, \
    _search_sha, _bridge_sha, _engine_sha = sys.argv[1:]
if _phase not in {"reference-a", "reference-b"} or not _phase_path.startswith(
        "/tmp/rebar-phase2-native-build-v9-rust-"):
    raise SystemExit("invalid private owner")
_source = _phase_path + "/source/candidates"
_native = _phase_path + "/native"
_adapter = _source + "/rust_candidate.py"
_bridge_source = _source + "/rust/py_bridge.c"
_engine_source = _source + "/rust/src/lib.rs"
_search_source = _source + "/rust/src/search.rs"
_bridge = _native + "/_rust_bridge.cpython-314-x86_64-linux-gnu.so"
_engine = _native + "/_rust_engine.so"
_stdlib = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/"
_allowed_files = {_adapter, _bridge_source, _engine_source, _search_source, _bridge, _engine,
                  _source + "/__pycache__/rust_candidate.cpython-314.pyc", "/proc/self/maps"}
_allowed_imports = {
    "abc", "_abc", "_blake2", "_codecs", "_collections", "_collections_abc",
    "_contextvars", "_functools", "_hashlib", "_io", "_operator", "_py_warnings",
    "_signal", "_stat", "_thread", "_types", "_warnings", "_weakref", "builtins",
    "candidates", "codecs", "collections", "contextvars", "copyreg", "encodings",
    "enum", "errno", "functools", "genericpath", "hashlib", "itertools", "keyword",
    "linecache", "marshal", "operator", "os", "posix", "posixpath", "reprlib",
    "stat", "sys", "time", "types", "unicodedata", "warnings", "zipimport",
}
_events, _opened, _imported = [], [], []
_phase_marker = "bootstrap"
_forbidden_attempts = _process_attempts = _network_attempts = 0
_native_load_attempts = _outside_open_attempts = 0
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
            if name == "candidates._rust_bridge" and path != _bridge:
                _native_load_attempts += 1
                _deny("foreign bridge " + path)
            if name != "candidates._rust_bridge" and not path.startswith(_stdlib):
                _native_load_attempts += 1
                _deny("foreign extension " + path)
        _imported.append((name, path if isinstance(path, str) else None, _phase_marker))
    elif event == "open":
        path = args[0] if args else ""
        mode = args[1] if len(args) > 1 else None
        flags = args[2] if len(args) > 2 else 0
        if not isinstance(path, str) or (path not in _allowed_files
                                         and not path.startswith(_stdlib)):
            _outside_open_attempts += 1
            _deny("unapproved owner " + repr(path))
        if path.startswith(_stdlib) and any(item in path.casefold() for item in
                                             ("/re/", "/regex/", "/_sre", "/inspect.py", "/tokenize.py")):
            _forbidden_attempts += 1
            _deny("stdlib matcher or introspection " + path)
        if ((isinstance(mode, str) and any(item in mode for item in "wax+"))
                or (isinstance(flags, int)
                    and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))):
            _outside_open_attempts += 1
            _deny("write-capable owner open")
        _opened.append((path, _phase_marker))
    elif event in {"subprocess.Popen", "os.system", "os.posix_spawn", "os.posix_spawnp",
                   "os.fork", "os.exec"}:
        _process_attempts += 1
        _deny("external process")
    elif event in {"socket.connect", "socket.__new__", "socket.getaddrinfo"}:
        _network_attempts += 1
        _deny("network")
    elif event.startswith("ctypes.") or event == "os.add_dll_directory":
        _native_load_attempts += 1
        _deny("foreign native loader")
    elif event == "sys.addaudithook":
        _deny("replacement audit hook")
    elif event == "exec":
        filename = getattr(args[0] if args else None, "co_filename", "")
        if not (filename == _adapter or filename.startswith(_stdlib)
                or filename.startswith("<frozen ")):
            _deny("unowned dynamic execution " + repr(filename))
    elif event == "compile":
        filename = args[1] if len(args) > 1 else ""
        if isinstance(filename, bytes):
            filename = filename.decode("utf-8", "replace")
        if not (filename == _adapter or
                (isinstance(filename, str) and filename.startswith(_stdlib))):
            _deny("unowned dynamic compilation " + repr(filename))
    elif event in {"os.listdir", "os.scandir"}:
        path = args[0] if args else ""
        if not (isinstance(path, str) and
                (path in {_source, _native} or path.startswith(_stdlib))):
            _deny("unowned directory enumeration")
    if len(_events) >= 384:
        _deny("small isolated cohort exceeded its frozen event limit")
    _events.append((event, _phase_marker))

def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    global _forbidden_attempts
    if level or not _safe_module(name) or name.split(".", 1)[0] in _forbidden:
        _forbidden_attempts += 1
        _deny("forbidden direct or relative import " + repr(name))
    if name == "candidates" and any(item != "_rust_bridge" for item in fromlist):
        _forbidden_attempts += 1
        _deny("cross-family bridge")
    if name.startswith("candidates.") and name not in {
            "candidates.rust_candidate", "candidates._rust_bridge"}:
        _forbidden_attempts += 1
        _deny("cross-family adapter")
    return _old_import(name, globals, locals, fromlist, level)

def _identity(path, expected_sha, expected_bytes, expected_mode):
    with open(path, "rb") as stream:
        raw = stream.read(expected_bytes + 1)
    owner = os.stat(path, follow_symlinks=False)
    if (len(raw) != expected_bytes or hashlib.sha256(raw).hexdigest() != expected_sha
            or owner.st_uid != os.getuid() or owner.st_nlink != 1
            or owner.st_mode & 0o777 != expected_mode):
        _deny("exact owner changed " + path)
    return {"sha256": expected_sha, "bytes": expected_bytes,
            "device": owner.st_dev, "inode": owner.st_ino,
            "mode": format(owner.st_mode & 0o777, "04o")}

def _maps():
    with open("/proc/self/maps", "r", encoding="utf-8") as stream:
        raw = stream.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        _deny("native mapping snapshot exceeded frozen bound")
    return tuple(line.rsplit(None, 1)[-1].strip() for line in raw.splitlines()
                 if line.rstrip().endswith(".so") or ".so." in line)

def _loaded_forbidden():
    return tuple(sorted(name for name in sys.modules
                        if name.split(".", 1)[0] in _forbidden))

try:
    if _cohort not in {"entry", "types", "unicode", "replacement",
                       "scanners", "advanced", "lifecycle", "serialization"}:
        _deny("unfrozen cohort")
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
    if _bridge in _maps() or _engine in _maps() or _loaded_forbidden():
        _deny("uncontained owner preloaded before candidate import")
    package = types.ModuleType("candidates")
    package.__path__ = [_native, _source]
    package.__package__ = "candidates"
    sys.modules["candidates"] = package
    _phase_marker = "candidate_import"
    candidate = _guarded_import("candidates.rust_candidate", fromlist=("rust_candidate",))
    native = sys.modules.get("candidates._rust_bridge")
    if (candidate is not sys.modules.get("candidates.rust_candidate") or native is None
            or getattr(native, "__file__", None) != _bridge):
        _deny("exact native bridge was not loaded")
    mapped = _maps()
    if _bridge not in mapped or _engine not in mapped:
        _deny("exact first-party bridge/engine were not mapped")
    if any(any(fragment in path.casefold() for fragment in (
            "libpcre", "libonig", "libre2", "libhyperscan", "libhs.so", "librure",
            "_sre.", "/regex/", "/candidates/_vm", "/candidates/_zig",
            "/candidates/_cpp", "/candidates/_go", "/candidates/_fortran"))
           for path in mapped):
        _deny("foreign or cross-family native mapping")
    if _loaded_forbidden():
        _deny("forbidden module loaded by candidate import")
    _phase_marker = "candidate_operations"
    operations = []

    def check(name, condition):
        if not condition or _loaded_forbidden():
            _deny("wrong answer or forbidden matcher in " + name)
        if len(operations) >= 3:
            _deny("isolated cohort exceeded three operations")
        operations.append(name)

    if _cohort == "entry":
        match = candidate.compile(r"(?P<word>\w+)").search("..café..", 2)
        check("compiled_named_unicode_search",
              match is not None and match.group("word") == "café" and match.span() == (2, 6))
        check("module_search_cache", candidate.search("cache", "--cache--").span() == (2, 7))
        check("module_match", candidate.match(r"(?P<a>a+)", "aaab").group("a") == "aaa")
    elif _cohort == "types":
        check("module_fullmatch", candidate.fullmatch(r"(?i:ab)c", "ABc").span() == (0, 3))
        check("bytes_memoryview_search",
              candidate.search(rb"a+", memoryview(bytearray(b"--aaa--"))).span() == (2, 5))
        check("scoped_unicode_category", candidate.search(r"(?a:(?u:\w))", "é").span() == (0, 1))
    elif _cohort == "unicode":
        verbose = "(?x)\\N{LATIN SMALL LETTER A} # \\N{NOT A NAME}\na"
        check("verbose_named_escape_comment", candidate.fullmatch(verbose, "aa").span() == (0, 2))
        check("findall_named_digits", candidate.findall(r"(?P<n>\d+)", "a12b003") == ["12", "003"])
        check("finditer_spans", [item.span() for item in candidate.finditer(r"\d+", "a12b003")]
              == [(1, 3), (4, 7)])
    elif _cohort == "replacement":
        check("split_digits", candidate.split(r"\d+", "a12b003c") == ["a", "b", "c"])
        check("sub_callback", candidate.sub(r"\d+", lambda item: "[" + item.group() + "]",
                                             "a12b003") == "a[12]b[003]")
        check("subn_named_template", candidate.subn(r"(?P<n>\d+)", r"<\g<n>>", "a12b003")
              == ("a<12>b<003>", 2))
    elif _cohort == "scanners":
        match = candidate.search(r"(?P<word>\w+)", "..café..")
        check("match_expand_named_template", match.expand(r"\g<word>:\g<word>") == "café:café")
        scanner = candidate.compile(r"\w+").scanner("ab cd")
        first, second = scanner.search(), scanner.search()
        check("pattern_scanner_search", first.group() == "ab" and second.group() == "cd"
              and scanner.search() is None)
        lexical = candidate.Scanner([(r"\d+", lambda scanner, value: ("number", value)),
                                     (r"\s+", None),
                                     (r"[A-Za-z]+", lambda scanner, value: ("word", value))])
        check("public_lexical_scanner", lexical.scan("12 ab")
              == ([("number", "12"), ("word", "ab")], ""))
    elif _cohort == "advanced":
        check("bytes_named_substitution", candidate.sub(rb"(?P<n>\d+)", br"<\g<n>>", b"a12b003")
              == b"a<12>b<003>")
        check("lookbehind_search", candidate.search(r"(?<=ab)c", "zabc").span() == (3, 4))
        check("backreference_fullmatch", candidate.fullmatch(r"(a+)\1", "aaaa").span() == (0, 4))
    elif _cohort == "lifecycle":
        check("bytes_ignorecase", candidate.fullmatch(rb"abc", b"AbC", candidate.IGNORECASE)
              .span() == (0, 3))
        first, second = candidate.compile("cache-lifecycle"), candidate.compile("cache-lifecycle")
        candidate.purge()
        check("cache_lifecycle", first is second and candidate.compile("cache-lifecycle") is not first)
        reduced = candidate.search(r"(?P<word>\w+)", "café").__reduce_ex__(0)
        check("match_reduce_copyreg", len(reduced) == 2
              and getattr(reduced[0], "__module__", None) == "copyreg")
    else:
        scanner = candidate.compile(r"\w+").scanner("ab cd")
        try:
            scanner.__reduce_ex__(0)
        except TypeError as error:
            check("scanner_reduce_rejected", "cannot pickle" in str(error))
        else:
            _deny("scanner serialization unexpectedly succeeded")

    after = _maps()
    if (_bridge not in after or _engine not in after or _loaded_forbidden()
            or builtins.__import__ is not _guarded_import
            or not 1 <= len(operations) <= 3
            or _forbidden_attempts or _process_attempts or _network_attempts
            or _native_load_attempts or _outside_open_attempts):
        _deny("isolated cohort escaped its frozen first-party boundary")
    copyreg_observed = any(row[0] == "copyreg" and row[2] == "candidate_operations"
                           for row in _imported)
    if _cohort == "lifecycle" and not copyreg_observed:
        _deny("native copyreg metadata import was not audited")
    answer = {
        "schema": "rebar-phase2-rust-live-worker-v8", "status": "PASS",
        "phase": _phase, "cohort": _cohort, "operation_names": tuple(operations),
        "operation_count": len(operations), "fresh_isolated_process": True,
        "audit_hook_precedes_candidate_import": True,
        "candidate_module": candidate.__name__, "native_module": native.__name__,
        "candidate_native_bridge_path": native.__file__, "candidate_native_engine_path": _engine,
        "source_and_native_owners": identities,
        "loaded_native_objects": tuple(sorted({_bridge, _engine})),
        "observed_imports": tuple(_imported), "observed_file_opens": tuple(_opened),
        "audit_event_count": len(_events), "copyreg_import_observed": copyreg_observed,
        "forbidden_preloaded_modules": _starting, "forbidden_loaded_modules": _loaded_forbidden(),
        "forbidden_module_import_attempts": _forbidden_attempts,
        "external_native_load_attempts": _native_load_attempts,
        "cross_family_load_count": 0, "subprocess_attempts": _process_attempts,
        "network_attempts": _network_attempts, "outside_open_attempts": _outside_open_attempts,
        "holdout_reads": 0, "proposal_content_opens": 0, "proposal_metadata_probes": 0,
        "hidden_case_reads": 0, "benchmark_reads": 0,
        "external_regex_packages": 0, "external_regex_libraries": 0,
        "runtime_non_delegation": "ESTABLISHED FOR THIS EXACT ISOLATED COHORT",
    }
    sys.stdout.buffer.write((repr(answer) + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()
except BaseException as error:
    answer = {"schema": "rebar-phase2-rust-live-worker-v8", "status": "FAIL",
              "phase": _phase, "cohort": _cohort, "error_type": type(error).__name__,
              "message": str(error)[:2048], "audit_event_count": len(_events),
              "forbidden_module_import_attempts": _forbidden_attempts,
              "external_native_load_attempts": _native_load_attempts,
              "subprocess_attempts": _process_attempts, "network_attempts": _network_attempts,
              "outside_open_attempts": _outside_open_attempts,
              "observed_imports": tuple(_imported[-16:]),
              "runtime_non_delegation": "NOT ESTABLISHED"}
    sys.stdout.buffer.write((repr(answer) + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()
    raise SystemExit(1)
'''


class ProofError(Exception):
    """Reject any missing frozen owner, delegated engine, or unbounded worker."""


def require(value: object, message: str) -> None:
    if not value:
        raise ProofError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                       separators=(",", ":")) + "\n").encode("ascii")


def fingerprint(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64 and frozenset(value) <= HEX,
            label + ": require one complete independent lowercase SHA-256")
    return value


def effects() -> dict[str, int]:
    return {key: 0 for key in (
        "approved_owner_reads", "v33_source_owner_reads", "v5_source_owner_reads",
        "v6_source_owner_reads", "v7_source_owner_reads", "proven_audit_source_reads",
        "public_receipt_reads", "v6_failure_reads", "v7_failure_reads",
        "private_build_root_opens", "private_phase_opens", "private_candidate_source_reads",
        "private_native_reads", "candidate_processes", "candidate_operations",
        "candidate_imports", "native_library_loads", "subprocesses", "reference_workers",
        "forbidden_module_imports", "external_engine_loads", "cross_family_loads",
        "archive_reads", "archive_decompressions", "holdout_reads", "proposal_content_opens",
        "proposal_metadata_probes", "hidden_case_reads", "benchmark_reads", "network_requests",
        "compiler_processes", "clock_samples", "workspace_mutations", "git_reads",
        "blocked_reads", "blocked_writes", "blocked_imports", "blocked_processes",
        "blocked_network", "blocked_threads", "blocked_clocks", "blocked_native_loads",
        "blocked_audit_hooks",
    )}


class SourceWall:
    def __init__(self) -> None:
        self.effects = effects()
        self.restore: list[tuple[object, str, object]] = []

    def block(self, owner: object, name: str, counter: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def denied(*_args: object, **_kwargs: object) -> object:
            self.effects[counter] += 1
            raise ProofError("source-only wall rejected " + name)

        self.restore.append((owner, name, original))
        setattr(owner, name, denied)

    def __enter__(self) -> SourceWall:
        for owner, name in ((builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
                            (os, "fstat"), (os, "stat"), (os, "lstat"),
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
                     "perf_counter_ns", "process_time", "process_time_ns", "sleep"):
            self.block(time, name, "blocked_clocks")
        for module_name in ("ctypes", "_ctypes"):
            module = sys.modules.get(module_name)
            if module is not None:
                for name in ("CDLL", "PyDLL", "dlopen", "_dlopen"):
                    self.block(module, name, "blocked_native_loads")
        return self

    def __exit__(self, *_args: object) -> None:
        for owner, name, original in reversed(self.restore):
            setattr(owner, name, original)


def strict_json(raw: bytes, label: str) -> dict[str, object]:
    def unique(items: list[tuple[str, object]]) -> dict[str, object]:
        answer: dict[str, object] = {}
        for key, value in items:
            require(type(key) is str and key not in answer, label + ": duplicate JSON field")
            answer[key] = value
        return answer

    try:
        answer = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                            parse_constant=lambda value: (_ for _ in ()).throw(
                                ProofError(label + ": non-finite JSON " + value)))
    except (UnicodeError, ValueError, TypeError) as error:
        raise ProofError(label + ": malformed frozen JSON") from error
    require(type(answer) is dict, label + ": require one exact JSON object")
    return answer


def public_parts(path: str, *, receipt: bool = False) -> tuple[str, ...]:
    require(type(path) is str and path and not path.startswith("/")
            and "\\" not in path and "\x00" not in path,
            "require one project-relative frozen public owner")
    pieces = tuple(path.split("/"))
    require(all(item not in {"", ".", "..", ".git", ".codex", ".agents",
                             "__pycache__", "candidates", "performance"}
                for item in pieces), "deny traversal, candidate, git, or performance ownership")
    for item in pieces:
        lowered = item.casefold()
        require(not any(word in lowered for word in
                        ("holdout", "hidden", "benchmark", "postfinal", "proposal", "phase3")),
                "deny protected final or benchmark ownership")
        if lowered == "evidence":
            require(receipt and any(path == row["path"] for row in PUBLIC_RECEIPTS.values()),
                    "deny unapproved evidence ownership")
    return pieces


def read_at(base: int, pieces: tuple[str, ...], label: str, account: dict[str, int],
            category: str, expected: dict[str, object] | None = None) -> tuple[bytes, dict[str, object]]:
    handles: list[int] = []
    try:
        parent = base
        for item in pieces[:-1]:
            current = OPEN(item, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                           dir_fd=parent)
            handles.append(current)
            parent = current
        handle = OPEN(pieces[-1], os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=parent)
        handles.append(handle)
        before = FSTAT(handle)
        require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= MAX_SOURCE
                and before.st_uid == os.getuid() and before.st_nlink == 1,
                label + ": require bounded owned regular single-link owner")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            block = READ(handle, min(remaining, 65536))
            require(bool(block), label + ": frozen owner truncated")
            chunks.append(block)
            remaining -= len(block)
        require(not READ(handle, 1), label + ": frozen owner grew")
        after = FSTAT(handle)
        identity = lambda row: (row.st_dev, row.st_ino, row.st_size,
                                row.st_mtime_ns, row.st_ctime_ns, row.st_nlink)
        require(identity(before) == identity(after), label + ": frozen owner changed")
        raw = b"".join(chunks)
        owner = {"path": label, "sha256": digest(raw), "bytes": len(raw),
                 "device": before.st_dev, "inode": before.st_ino,
                 "mode": format(stat.S_IMODE(before.st_mode), "04o"),
                 "uid": before.st_uid, "nlink": before.st_nlink}
        for name, value in (expected or {}).items():
            require(owner.get(name) == value, label + ": frozen " + name + " changed")
        account["approved_owner_reads"] += 1
        if category != "approved_owner_reads":
            account[category] += 1
        return raw, owner
    finally:
        for handle in reversed(handles):
            CLOSE(handle)


def public_read(path: str, account: dict[str, int], category: str,
                expected: dict[str, object] | None = None) -> tuple[bytes, dict[str, object]]:
    parts = public_parts(path, receipt=category == "public_receipt_reads")
    root = OPEN(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        return read_at(root, parts, path, account, category, expected)
    finally:
        CLOSE(root)


def require_interpreter() -> None:
    require(sys.executable == PINNED_PYTHON and sys.version_info[:3] == (3, 14, 6)
            and os.path.abspath(__file__) == ROOT + "/" + SOURCE,
            "require exact isolated pinned CPython 3.14.6 controller")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules), "controller imported candidate prematurely")


def module_allowed(value: object) -> bool:
    return (type(value) is str and bool(value) and value.split(".", 1)[0] in ALLOWED
            and value.split(".", 1)[0] not in FORBIDDEN
            and (not value.startswith("candidates.") or value in {
                "candidates.rust_candidate", "candidates._rust_bridge"}))


def worker_path_allowed(path: object, phase: str) -> bool:
    if type(path) is not str or phase not in {"reference-a", "reference-b"}:
        return False
    if path == "/proc/self/maps":
        return True
    if path.startswith(PINNED_STDLIB):
        return not any(word in path.casefold() for word in
                       ("/re/", "/regex/", "/_sre", "/inspect.py", "/tokenize.py"))
    prefix = "/tmp/rebar-phase2-native-build-v9-rust-"
    marker = "/" + phase + "/"
    if not path.startswith(prefix) or marker not in path:
        return False
    return path.split(marker, 1)[1] in {
        "source/candidates/rust_candidate.py",
        "source/candidates/__pycache__/rust_candidate.cpython-314.pyc",
        "source/candidates/rust/py_bridge.c", "source/candidates/rust/src/lib.rs",
        "source/candidates/rust/src/search.rs", "native/_rust_engine.so",
        "native/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
    }


def cohort_manifest() -> list[dict[str, object]]:
    return [{"name": name, "operation_names": list(operations),
             "operation_count": len(operations)} for name, operations in COHORTS]


def source_self_test() -> dict[str, object]:
    require_interpreter()
    positive = hostile = 0
    with SourceWall() as wall:
        tree = ast.parse(WORKER_PROGRAM, filename="<frozen-rust-live-worker-v8>")
        imports = set()
        pending = [tree]
        while pending:
            item = pending.pop()
            pending.extend(ast.iter_child_nodes(item))
            if isinstance(item, ast.Import):
                imports.update(alias.name for alias in item.names)
            elif isinstance(item, ast.ImportFrom):
                imports.add(item.module or "")
        require(imports == {"sys", "builtins", "hashlib", "os", "types"},
                "isolated worker bootstrap imported an unapproved module")
        require("sys.addaudithook(_audit)" in WORKER_PROGRAM
                and WORKER_PROGRAM.index("sys.addaudithook(_audit)")
                < WORKER_PROGRAM.index('candidate = _guarded_import("candidates.rust_candidate"')
                and 'builtins.__import__ = _guarded_import' in WORKER_PROGRAM
                and "small isolated cohort exceeded its frozen event limit" in WORKER_PROGRAM,
                "live candidate hook or bounded fresh-worker architecture weakened")
        require(len(COHORTS) == 8 and len(EXPECTED_OPERATIONS) == 22
                and all(1 <= len(operations) <= 3 for _, operations in COHORTS)
                and len(set(EXPECTED_OPERATIONS)) == 22,
                "frozen fresh-process manifest is missing or duplicated")
        for name in ALLOWED:
            require(module_allowed(name), "safe frozen module rejected: " + name)
            positive += 1
        for name in FORBIDDEN:
            for target in (name, name + ".engine", name + ".engine.indirect"):
                require(not module_allowed(target), "forbidden matcher escaped: " + target)
                hostile += 1
        for name in ("candidates.vm_candidate", "candidates._vm_native",
                     "candidates.zig_candidate", "candidates._zig_bridge",
                     "candidates.cpp_candidate", "candidates.go_candidate",
                     "candidates.fortran_candidate", "", "foreign_engine"):
            require(not module_allowed(name), "foreign candidate escaped: " + name)
            hostile += 1
        for phase in ("reference-a", "reference-b"):
            prefix = "/tmp/rebar-phase2-native-build-v9-rust-fixture/" + phase + "/"
            for relative, _, _, _ in (*SOURCE_OWNERS.values(), *NATIVE_OWNERS.values()):
                require(worker_path_allowed(prefix + relative, phase),
                        "exact fresh-worker owner was rejected: " + relative)
                positive += 1
            for path in (prefix + "source/candidates/../holdout.json",
                         prefix + "native/libpcre2.so", prefix + "native/_zig_probe.so",
                         prefix + "source/candidates/another.py", "/tmp/foreign.so",
                         "/home/dev-user/src/rebar/oracle/phase3/final.json"):
                require(not worker_path_allowed(path, phase),
                        "foreign fresh-worker owner escaped: " + path)
                hostile += 1
        require(worker_path_allowed("/proc/self/maps", "reference-a"), "maps rejected")
        require(worker_path_allowed(PINNED_STDLIB + "enum.py", "reference-a"),
                "ordinary pinned stdlib source rejected")
        positive += 2
        for path in ("../private", ".git/config", "candidates/rust_candidate.py",
                     "oracle/holdout.json", "oracle/hidden/cases.json",
                     "oracle/phase2/evidence/foreign.json", "performance/results.json"):
            try:
                public_parts(path)
            except ProofError:
                hostile += 1
            else:
                raise ProofError("protected owner escaped source-only wall: " + path)
        require(positive >= 50 and hostile >= 80,
                "fresh-worker positive/hostile source controls shrank")
        require(all(value == 0 for value in wall.effects.values()),
                "source-only hostile controls performed external work")
        account = dict(wall.effects)
    return {"schema": SCHEMA + "-source-self-test", "status": "PASS",
            "positive_controls": positive, "hostile_controls": hostile,
            "cohort_count_per_phase": len(COHORTS), "maximum_operations_per_worker": 3,
            "operation_count_per_phase": len(EXPECTED_OPERATIONS),
            "candidate_processes_per_phase": len(COHORTS),
            "live_worker_program_sha256": digest(WORKER_PROGRAM.encode("utf-8")),
            "candidate_source_reads": 0, "private_build_roots_opened": 0,
            "candidate_processes": 0, "candidate_executions": 0,
            "live_runtime_non_delegation": "NOT RUN", "final_cases_generated": 0,
            "performance": "NOT MEASURED", "winner_selected": False, "effects": account}


def check_predecessors(account: dict[str, int]) -> dict[str, object]:
    source_records = (("v33_source_owner_reads", V33_OWNERS),
                      ("v5_source_owner_reads", V5_OWNERS),
                      ("v6_source_owner_reads", V6_OWNERS),
                      ("v7_source_owner_reads", V7_OWNERS),
                      ("proven_audit_source_reads", PROVEN_SOURCE))
    proven_text = ""
    for category, records in source_records:
        for path, expected in records.items():
            raw, _ = public_read(path, account, category,
                                 {"sha256": expected, "mode": "0600"})
            if category == "proven_audit_source_reads":
                proven_text = raw.decode("utf-8")
    require('"attempt": "initial_five_elf_live_audit"' in proven_text
            and '"exit_code": 137' in proven_text
            and "running all 73 malicious controls and the complete production-source audit "
                "in the same process caused cumulative SIGKILL" in proven_text
            and "fresh isolated subprocess" in proven_text,
            "the proven historical cumulative-SIGKILL diagnosis and isolation remedy changed")
    receipts = {}
    for name, record in PUBLIC_RECEIPTS.items():
        expected = {key: value for key, value in record.items() if key != "path"}
        raw, owner = public_read(record["path"], account, "public_receipt_reads", expected)
        receipts[name] = {"owner": owner, "content": strict_json(raw, record["path"])}
    original, exact_original, public, static = (receipts[name]["content"] for name in
                                                ("original", "v33_original", "public", "static"))
    require(original.get("status") == "PASS" and original.get("candidate_status") == "PASS"
            and original.get("verified_passing_case_count") == 31237
            and original.get("case_execution_denominator") == 31237
            and original.get("semantic_mismatch_count") == 0,
            "the actual historical V30 original PASS changed")
    require(exact_original.get("schema") ==
            "rebar-owned-repaired-rust-original-campaign-v28-durable-publication-receipt"
            and exact_original.get("status") == "PASS"
            and exact_original.get("candidate_status") == "PASS"
            and exact_original.get("candidate_original_oracle_pass") is True
            and exact_original.get("original_suite_correctness_qualified") is True
            and exact_original.get("verified_passing_case_count") == 31237
            and exact_original.get("case_execution_denominator") == 31237
            and exact_original.get("completed_suite_count") == 13
            and exact_original.get("actual_candidate_workers") == 13
            and exact_original.get("semantic_mismatch_count") == 0
            and exact_original.get("infrastructure_failure_count") == 0
            and exact_original.get("corrected_public_adapter_sha256") ==
                SOURCE_OWNERS["adapter"][1]
            and exact_original.get("native_engine_sha256") == NATIVE_OWNERS["engine"][1]
            and exact_original.get("native_bridge_sha256") == NATIVE_OWNERS["bridge"][1]
            and exact_original.get("actual_v28_build_receipt_sha256") ==
                PUBLIC_RECEIPTS["v33_publication"]["sha256"]
            and exact_original.get("actual_v28_build_source_sha256") ==
                V33_OWNERS["tools/reproduce_owned_rust_full_public_semantic_source_build_v33.py"]
            and exact_original.get("actual_v28_build_protocol_sha256") ==
                V33_OWNERS["oracle/phase2/RUST-FULL-PUBLIC-SEMANTIC-SOURCE-BUILD-V33.md"]
            and exact_original.get("actual_v28_build_contract_sha256") ==
                V33_OWNERS["oracle/phase2/rust-full-public-semantic-source-build-v33.json"]
            and exact_original.get("candidate_qualified") is False
            and exact_original.get("runtime_non_delegation") == "NOT ESTABLISHED",
            "the exact same-build V33 31,237-case original PASS or owner lineage changed")
    require(public.get("status") == "PASS" and public.get("candidate_status") == "PASS"
            and public.get("public_10434_case_count") == 10434
            and public.get("public_10434_verified_passing_case_count") == 10434
            and public.get("public_10434_mismatch_count") == 0
            and public.get("v33_adapter_sha256") == SOURCE_OWNERS["adapter"][1]
            and public.get("v33_native_engine_sha256") == NATIVE_OWNERS["engine"][1]
            and public.get("v33_native_bridge_sha256") == NATIVE_OWNERS["bridge"][1],
            "the exact V33 public PASS or native ownership changed")
    require(static.get("status") == "PASS" and static.get("audited_family") == "rust"
            and static.get("finding_count") == 0
            and static.get("external_regex_packages") == 0
            and static.get("external_regex_libraries") == 0
            and static.get("external_regex_symbols") == 0
            and static.get("cross_family_dependencies") == 0
            and static.get("legacy_private_inspect_getter") is False,
            "the strict V5 zero-delegation first-party source audit changed")
    publication, root = (receipts[name]["content"] for name in ("v33_publication", "v33_root"))
    require(publication.get("status") == "PASS"
            and publication.get("actual_completed_phase_count") == 2
            and publication.get("actual_compiler_process_count") == 28
            and publication.get("external_cargo_dependency_count") == 0
            and root.get("status") == "PASS" and root.get("actual_source_phase_count") == 2
            and root.get("actual_compiler_process_count") == 28
            and root.get("cross_phase_complete_bridge_elf_byte_identical") is True
            and root.get("cross_phase_complete_engine_elf_byte_identical") is True,
            "the frozen exact V33 dependency-free native build changed")
    failure6, failure7 = (receipts[name]["content"] for name in ("v6_failure", "v7_failure"))
    require(failure6.get("status") == "FAIL"
            and failure6.get("error_type") == "LiveProofError"
            and "forbidden direct or relative import '_io'" in str(failure6.get("message"))
            and failure6.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and failure6.get("candidate_qualified") is False,
            "the immutable actual V6 safe-import failure changed or disappeared")
    require(failure7.get("schema") ==
            "rebar-phase2-first-party-rust-live-non-delegation-v7-root-execution-failure"
            and failure7.get("status") == "FAIL" and failure7.get("exit_code") == 137
            and failure7.get("signal") == "SIGKILL"
            and failure7.get("stdout_bytes") == 0 and failure7.get("stderr_bytes") == 0
            and failure7.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and failure7.get("candidate_qualified") is False,
            "the immutable actual V7 SIGKILL failure changed or disappeared")
    account["v6_failure_reads"] += 1
    account["v7_failure_reads"] += 1
    return receipts


def validate_contract(value: dict[str, object]) -> None:
    freeze = value.get("source_freeze")
    evidence = value.get("preserved_evidence")
    worker = value.get("live_worker")
    history = value.get("immutable_failures")
    boundaries = value.get("boundaries")
    require(value.get("schema") == SCHEMA and value.get("version") == 8
            and type(freeze) is dict and type(evidence) is dict and type(worker) is dict
            and type(history) is dict and type(boundaries) is dict
            and freeze.get("source_path") == SOURCE
            and freeze.get("protocol_path") == PROTOCOL
            and freeze.get("contract_path") == CONTRACT
            and freeze.get("sole_owned_file_count") == 3
            and evidence.get("exact_v33_original_pass_sha256") ==
                PUBLIC_RECEIPTS["v33_original"]["sha256"]
            and evidence.get("exact_v33_original_p0_status") == "PASS"
            and evidence.get("exact_v33_original_case_count") == 31237
            and evidence.get("exact_v33_original_completed_suite_count") == 13
            and evidence.get("exact_v33_original_mismatch_count") == 0
            and evidence.get("exact_v33_original_same_adapter_sha256") ==
                SOURCE_OWNERS["adapter"][1]
            and evidence.get("exact_v33_original_same_engine_sha256") ==
                NATIVE_OWNERS["engine"][1]
            and evidence.get("exact_v33_original_same_bridge_sha256") ==
                NATIVE_OWNERS["bridge"][1]
            and evidence.get("public_v33_pass_sha256") == PUBLIC_RECEIPTS["public"]["sha256"]
            and evidence.get("public_v33_case_count") == 10434
            and evidence.get("v5_static_pass_sha256") == PUBLIC_RECEIPTS["static"]["sha256"]
            and worker.get("program_sha256") == digest(WORKER_PROGRAM.encode("utf-8"))
            and worker.get("phase_count") == 2
            and worker.get("cohort_count_per_phase") == len(COHORTS)
            and worker.get("candidate_process_count") == 2 * len(COHORTS)
            and worker.get("maximum_operations_per_worker") == 3
            and worker.get("operation_count_per_phase") == len(EXPECTED_OPERATIONS)
            and worker.get("total_operation_count") == 2 * len(EXPECTED_OPERATIONS)
            and worker.get("cohorts") == cohort_manifest()
            and worker.get("reference_process_count") == 0
            and worker.get("stdlib_regex_module_allowed") is False
            and worker.get("external_regex_engine_allowed") is False
            and worker.get("cross_family_engine_allowed") is False
            and worker.get("adapter_sha256") == SOURCE_OWNERS["adapter"][1]
            and worker.get("native_engine_sha256") == NATIVE_OWNERS["engine"][1]
            and worker.get("native_bridge_sha256") == NATIVE_OWNERS["bridge"][1]
            and history.get("v6_failure_sha256") == PUBLIC_RECEIPTS["v6_failure"]["sha256"]
            and history.get("v7_failure_sha256") == PUBLIC_RECEIPTS["v7_failure"]["sha256"]
            and history.get("v7_exit_code") == 137
            and history.get("historical_cumulative_sigkill_exit_code") == 137
            and history.get("proven_audit_source_sha256") ==
                PROVEN_SOURCE["tools/audit_from_scratch.py"]
            and history.get("historical_remedy") == "FRESH ISOLATED PINNED PROCESS PER SMALL BOUNDED COHORT"
            and boundaries.get("root_only_live_operation") is True
            and boundaries.get("source_only_candidate_execution") is False
            and boundaries.get("root_result_path") == RESULT
            and boundaries.get("candidate_qualified_before_live_runtime_proof") is False
            and boundaries.get("candidate_qualified_after_successful_same_build_live_proof") is True
            and boundaries.get("qualified_independent_family_count_after_live_pass") == 1
            and boundaries.get("final_cases_generated") == 0
            and boundaries.get("performance") == "NOT MEASURED"
            and boundaries.get("winner_selected") is False,
            "V8 freeze changed exact owners, preserved failures, or bounded fresh-process remedy")


def assert_source_effects(account: dict[str, int], verify: bool = False) -> None:
    permitted = set()
    if verify:
        permitted = {"approved_owner_reads", "v33_source_owner_reads", "v5_source_owner_reads",
                     "v6_source_owner_reads", "v7_source_owner_reads", "proven_audit_source_reads",
                     "public_receipt_reads", "v6_failure_reads", "v7_failure_reads"}
    for key, value in account.items():
        if key not in permitted:
            require(value == 0, "source-only operation escaped its frozen wall: " + key)
    if verify:
        require(account["approved_owner_reads"] == 24
                and account["v33_source_owner_reads"] == 3
                and account["v5_source_owner_reads"] == 3
                and account["v6_source_owner_reads"] == 3
                and account["v7_source_owner_reads"] == 3
                and account["proven_audit_source_reads"] == 1
                and account["public_receipt_reads"] == 8
                and account["v6_failure_reads"] == 1
                and account["v7_failure_reads"] == 1,
                "V8 source verification did not authenticate exactly 24 public owners")


def source_verify(options: dict[str, object]) -> dict[str, object]:
    require_interpreter()
    pins = {SOURCE: fingerprint(options.get("source_sha256"), "V8 source"),
            PROTOCOL: fingerprint(options.get("protocol_sha256"), "V8 protocol"),
            CONTRACT: fingerprint(options.get("contract_sha256"), "V8 contract")}
    require(len(set(pins.values())) == 3, "require independent source/protocol/contract pins")
    with SourceWall() as wall:
        raw = {}
        owners = {}
        for path in (SOURCE, PROTOCOL, CONTRACT):
            raw[path], owners[path] = public_read(path, wall.effects, "approved_owner_reads",
                                                  {"sha256": pins[path], "mode": "0600"})
        contract = strict_json(raw[CONTRACT], CONTRACT)
        validate_contract(contract)
        freeze = contract["source_freeze"]
        require(type(freeze) is dict and freeze.get("source_sha256") == pins[SOURCE]
                and freeze.get("protocol_sha256") == pins[PROTOCOL],
                "V8 contract does not independently bind the source/protocol owners")
        check_predecessors(wall.effects)
        account = dict(wall.effects)
        assert_source_effects(account, verify=True)
    return {"schema": SCHEMA + "-source-verification", "status": "PASS", "owners": owners,
            "preserved_v6_failure_status": "FAIL", "preserved_v7_failure_status": "FAIL",
            "preserved_v7_exit_code": 137,
            "historical_cumulative_sigkill_exit_code": 137,
            "fresh_candidate_processes_per_phase": len(COHORTS),
            "maximum_operations_per_worker": 3,
            "original_v30_case_count": 31237, "public_v33_case_count": 10434,
            "exact_v33_original_p0_status": "PASS",
            "exact_v33_original_p0_case_count": 31237,
            "exact_v33_original_p0_mismatch_count": 0,
            "exact_v33_original_p0_publication_sha256":
                PUBLIC_RECEIPTS["v33_original"]["sha256"],
            "candidate_qualified_before_live_proof": False,
            "candidate_processes": 0, "candidate_source_reads": 0,
            "private_build_roots_opened": 0, "live_runtime_non_delegation": "NOT RUN",
            "final_cases_generated": 0, "performance": "NOT MEASURED",
            "winner_selected": False, "effects": account}


def private_phases(root_receipt: dict[str, object], account: dict[str, int]) -> list[dict[str, object]]:
    root_owner = root_receipt.get("root")
    phases = root_receipt.get("phase_native_outputs")
    sources = root_receipt.get("actual_private_source_owners")
    require(type(root_owner) is dict and type(root_owner.get("path")) is str
            and root_owner["path"].startswith("/tmp/rebar-phase2-native-build-v9-rust-")
            and "/" not in root_owner["path"].removeprefix(
                "/tmp/rebar-phase2-native-build-v9-rust-")
            and type(phases) is list and len(phases) == 2
            and type(sources) is list and len(sources) == 2,
            "V33 root does not contain exactly two authenticated private phases")
    descriptor = OPEN(root_owner["path"],
                      os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        identity = FSTAT(descriptor)
        require(identity.st_dev == root_owner["device"] and identity.st_ino == root_owner["inode"]
                and identity.st_uid == os.getuid() and stat.S_IMODE(identity.st_mode) == 0o700,
                "V33 private root owner changed")
        account["private_build_root_opens"] += 1
        answer = []
        for index, name in enumerate(("reference-a", "reference-b")):
            phase = phases[index]
            source_provenance = sources[index]
            require(type(phase) is dict and phase.get("name") == name
                    and type(phase.get("native_outputs")) is list
                    and len(phase["native_outputs"]) == 2
                    and type(source_provenance) is dict
                    and source_provenance.get("phase") == name
                    and type(source_provenance.get("owners")) is dict,
                    name + ": frozen phase manifest changed")
            phase_fd = OPEN(name, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                            dir_fd=descriptor)
            try:
                phase_identity = FSTAT(phase_fd)
                require(phase_identity.st_dev == phase["device"]
                        and phase_identity.st_ino == phase["inode"]
                        and phase_identity.st_uid == os.getuid()
                        and stat.S_IMODE(phase_identity.st_mode) == 0o700,
                        name + ": authenticated private phase owner changed")
                account["private_phase_opens"] += 1
                owners = {}
                for kind, (relative, sha, size, mode) in SOURCE_OWNERS.items():
                    original = source_provenance["owners"].get(relative.removeprefix("source/"))
                    require(type(original) is dict, name + ": missing frozen source owner " + kind)
                    _, owners[kind] = read_at(phase_fd, tuple(relative.split("/")),
                                              name + "/" + relative, account,
                                              "private_candidate_source_reads",
                                              {"sha256": sha, "bytes": size, "mode": mode,
                                               "device": original["device"], "inode": original["inode"]})
                native_records = {item.get("role"): item for item in phase["native_outputs"]
                                  if type(item) is dict}
                require(set(native_records) == set(NATIVE_OWNERS),
                        name + ": missing exact first-party native engine or bridge")
                for kind, (relative, sha, size, mode) in NATIVE_OWNERS.items():
                    original = native_records[kind]
                    _, owners[kind] = read_at(phase_fd, tuple(relative.split("/")),
                                              name + "/" + relative, account,
                                              "private_native_reads",
                                              {"sha256": sha, "bytes": size, "mode": mode,
                                               "device": original["device"], "inode": original["inode"]})
                answer.append({"name": name, "path": root_owner["path"] + "/" + name,
                               "owners": owners})
            finally:
                CLOSE(phase_fd)
        return answer
    finally:
        CLOSE(descriptor)


def live_worker(phase: dict[str, object], cohort: tuple[str, tuple[str, ...]],
                account: dict[str, int]) -> dict[str, object]:
    name, operations = cohort
    command = [PINNED_PYTHON, "-I", "-B", "-S", "-c", WORKER_PROGRAM,
               phase["name"], phase["path"], name,
               SOURCE_OWNERS["adapter"][1], SOURCE_OWNERS["bridge_source"][1],
               SOURCE_OWNERS["engine_source"][1], SOURCE_OWNERS["search_source"][1],
               NATIVE_OWNERS["bridge"][1], NATIVE_OWNERS["engine"][1]]
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, cwd="/tmp", close_fds=True,
                               env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "PYTHONHASHSEED": "0"})
    account["subprocesses"] += 1
    account["candidate_processes"] += 1
    stdout, stderr = process.communicate()
    require(type(stdout) is bytes and 0 < len(stdout) <= MAX_RESPONSE
            and type(stderr) is bytes and len(stderr) <= MAX_RESPONSE,
            str(phase["name"]) + "/" + name + ": isolated candidate returned no bounded answer; "
            "exit_code=" + str(process.returncode))
    try:
        result = ast.literal_eval(stdout.decode("utf-8"))
    except (SyntaxError, ValueError, UnicodeError, RecursionError) as error:
        raise ProofError(str(phase["name"]) + "/" + name
                         + ": candidate result is not bounded literal data") from error
    require(type(result) is dict and process.returncode == 0 and not stderr
            and result.get("schema") == "rebar-phase2-rust-live-worker-v8"
            and result.get("status") == "PASS" and result.get("phase") == phase["name"]
            and result.get("cohort") == name and result.get("operation_names") == operations
            and result.get("operation_count") == len(operations)
            and result.get("fresh_isolated_process") is True
            and result.get("audit_hook_precedes_candidate_import") is True
            and result.get("candidate_module") == "candidates.rust_candidate"
            and result.get("native_module") == "candidates._rust_bridge"
            and result.get("forbidden_preloaded_modules") == ()
            and result.get("forbidden_loaded_modules") == ()
            and 0 < result.get("audit_event_count", 0) < 384,
            str(phase["name"]) + "/" + name + ": bounded worker failed: "
            + (repr(result.get("message")) if type(result) is dict else "malformed result"))
    for field in ("forbidden_module_import_attempts", "external_native_load_attempts",
                  "cross_family_load_count", "subprocess_attempts", "network_attempts",
                  "outside_open_attempts", "holdout_reads", "proposal_content_opens",
                  "proposal_metadata_probes", "hidden_case_reads", "benchmark_reads",
                  "external_regex_packages", "external_regex_libraries"):
        require(result.get(field) == 0, name + ": foreign side effect " + field)
    prefix = str(phase["path"])
    paths = {prefix + "/" + NATIVE_OWNERS["engine"][0],
             prefix + "/" + NATIVE_OWNERS["bridge"][0]}
    require(result.get("candidate_native_engine_path") ==
            prefix + "/" + NATIVE_OWNERS["engine"][0]
            and result.get("candidate_native_bridge_path") ==
            prefix + "/" + NATIVE_OWNERS["bridge"][0]
            and type(result.get("loaded_native_objects")) is tuple
            and set(result["loaded_native_objects"]) == paths,
            name + ": worker mapped foreign or missing native candidate")
    owners = result.get("source_and_native_owners")
    require(type(owners) is dict and set(owners) == set(SOURCE_OWNERS) | set(NATIVE_OWNERS),
            name + ": worker exact source/native owners disappeared")
    for kind, owner in phase["owners"].items():
        observed = owners.get(kind)
        require(type(observed) is dict
                and all(observed.get(key) == owner.get(key)
                        for key in ("sha256", "bytes", "device", "inode", "mode")),
                name + ": private owner changed after authentication: " + kind)
    if name == "lifecycle":
        require(result.get("copyreg_import_observed") is True,
                "the native copyreg metadata import was not observed")
    account["candidate_imports"] += 1
    account["native_library_loads"] += 2
    account["candidate_operations"] += len(operations)
    return {"phase": phase["name"], "cohort": name,
            "operation_names": list(operations), "operation_count": len(operations),
            "audit_event_count": result["audit_event_count"],
            "loaded_native_objects": sorted(paths),
            "copyreg_import_observed": result["copyreg_import_observed"],
            "forbidden_module_import_attempts": 0, "external_regex_package_count": 0,
            "external_regex_library_count": 0, "cross_family_native_owner_count": 0,
            "fresh_isolated_process": True, "runtime_non_delegation": "PASS"}


def publish(receipt: dict[str, object], account: dict[str, int]) -> dict[str, object]:
    raw = canonical(receipt)
    require(0 < len(raw) <= MAX_RECEIPT, "durable V8 receipt exceeded its frozen bound")
    descriptor = OPEN(ROOT + "/" + RESULT,
                      os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            amount = os.write(descriptor, raw[offset:])
            require(amount > 0, "durable V8 receipt write failed")
            offset += amount
        os.fsync(descriptor)
        owner = FSTAT(descriptor)
        require(stat.S_ISREG(owner.st_mode) and owner.st_uid == os.getuid()
                and owner.st_nlink == 1 and stat.S_IMODE(owner.st_mode) == 0o600
                and owner.st_size == len(raw), "durable V8 receipt is not exclusively owned")
    finally:
        CLOSE(descriptor)
    directory = OPEN(ROOT + "/oracle/phase2/evidence",
                     os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        os.fsync(directory)
    finally:
        CLOSE(directory)
    account["workspace_mutations"] += 1
    return {"path": RESULT, "sha256": digest(raw), "bytes": len(raw),
            "device": owner.st_dev, "inode": owner.st_ino, "mode": "0600",
            "exclusive_creation": True, "file_fsync_completed": True,
            "directory_fsync_completed": True}


def run_live(options: dict[str, object]) -> dict[str, object]:
    require_interpreter()
    require(options.get("root_authorized") is True,
            "candidate/private/native execution belongs exclusively to the root agent")
    source_sha = fingerprint(options.get("pushed_source_sha256"), "independently pushed V8 source")
    account = effects()
    _, source_owner = public_read(SOURCE, account, "approved_owner_reads",
                                  {"sha256": source_sha, "mode": "0600"})
    raw, _ = public_read(CONTRACT, account, "approved_owner_reads")
    contract = strict_json(raw, CONTRACT)
    validate_contract(contract)
    freeze = contract["source_freeze"]
    require(type(freeze) is dict and freeze.get("source_sha256") == source_sha,
            "root live execution is not independently bound to the pushed V8 source")
    history = check_predecessors(account)
    phases = private_phases(history["v33_root"]["content"], account)
    results = []
    for phase in phases:
        for cohort in COHORTS:
            results.append(live_worker(phase, cohort, account))
    require(account["approved_owner_reads"] == 35
            and account["v33_source_owner_reads"] == 3
            and account["v5_source_owner_reads"] == 3
            and account["v6_source_owner_reads"] == 3
            and account["v7_source_owner_reads"] == 3
            and account["proven_audit_source_reads"] == 1
            and account["public_receipt_reads"] == 8
            and account["v6_failure_reads"] == 1 and account["v7_failure_reads"] == 1
            and account["private_build_root_opens"] == 1
            and account["private_phase_opens"] == 2
            and account["private_candidate_source_reads"] == 8
            and account["private_native_reads"] == 4
            and account["candidate_processes"] == 16
            and account["candidate_imports"] == 16
            and account["native_library_loads"] == 32
            and account["candidate_operations"] == 44
            and account["subprocesses"] == 16,
            "isolated V8 phase/source/native/cohort/operation accounting does not close")
    for name in ("reference_workers", "forbidden_module_imports", "external_engine_loads",
                 "cross_family_loads", "archive_reads", "archive_decompressions",
                 "holdout_reads", "proposal_content_opens", "proposal_metadata_probes",
                 "hidden_case_reads", "benchmark_reads", "network_requests",
                 "compiler_processes", "clock_samples", "git_reads"):
        require(account[name] == 0, "isolated V8 worker escaped protected boundary: " + name)
    published_effects = dict(account)
    published_effects["workspace_mutations"] = 1
    receipt = {"schema": SCHEMA + "-durable-runtime-proof", "status": "PASS",
               "source_owner": source_owner, "pushed_source_sha256": source_sha,
               "family": "rust", "independent_candidate_family_count": 1,
               "minimum_required_independent_family_count": 3,
               "all_required_candidate_families_available": False,
               "original_v30_status": "PASS", "original_v30_case_count": 31237,
               "original_v30_publication_sha256": PUBLIC_RECEIPTS["original"]["sha256"],
               "original_v30_architecture": "V30; NOT IDENTICAL TO V33",
               "exact_v33_original_p0_status": "PASS",
               "exact_v33_original_p0_case_count": 31237,
               "exact_v33_original_p0_mismatch_count": 0,
               "exact_v33_original_p0_suite_count": 13,
               "exact_v33_original_p0_publication_sha256":
                   PUBLIC_RECEIPTS["v33_original"]["sha256"],
               "public_v33_status": "PASS", "public_v33_case_count": 10434,
               "public_v33_mismatch_count": 0,
               "public_v33_publication_sha256": PUBLIC_RECEIPTS["public"]["sha256"],
               "v5_static_status": "PASS",
               "v5_static_publication_sha256": PUBLIC_RECEIPTS["static"]["sha256"],
               "v33_native_build_status": "PASS",
               "v33_native_build_publication_sha256": PUBLIC_RECEIPTS["v33_publication"]["sha256"],
               "v33_native_build_root_sha256": PUBLIC_RECEIPTS["v33_root"]["sha256"],
               "immutable_v6_failure_status": "FAIL",
               "immutable_v6_failure_sha256": PUBLIC_RECEIPTS["v6_failure"]["sha256"],
               "immutable_v7_failure_status": "FAIL", "immutable_v7_exit_code": 137,
               "immutable_v7_failure_sha256": PUBLIC_RECEIPTS["v7_failure"]["sha256"],
               "historical_cumulative_sigkill_exit_code": 137,
               "proven_cumulative_sigkill_remedy":
                   "FRESH ISOLATED PINNED PROCESS PER SMALL BOUNDED COHORT",
               "proven_audit_source_sha256": PROVEN_SOURCE["tools/audit_from_scratch.py"],
               "exact_first_party_sources": {name: {"sha256": row[1], "bytes": row[2]}
                                              for name, row in SOURCE_OWNERS.items()},
               "exact_first_party_native": {name: {"sha256": row[1], "bytes": row[2]}
                                             for name, row in NATIVE_OWNERS.items()},
               "live_phase_count": 2, "cohort_count_per_phase": len(COHORTS),
               "maximum_operations_per_fresh_process": 3,
               "live_candidate_process_count": 16, "reference_process_count": 0,
               "operation_count_per_phase": len(EXPECTED_OPERATIONS),
               "live_total_operation_count": 44,
               "operation_names": list(EXPECTED_OPERATIONS),
               "live_worker_program_sha256": digest(WORKER_PROGRAM.encode("utf-8")),
               "live_isolated_cohorts": results,
               "external_regex_package_count": 0, "external_regex_library_count": 0,
               "cross_family_native_owner_count": 0,
               "candidate_runtime_non_delegation_status": "PASS",
               "runtime_non_delegation":
                   "ESTABLISHED FOR EXACT V33 RUST AND 44 FRESH-PROCESS GUARDED OPERATIONS",
               "candidate_qualified": True,
               "candidate_qualification_evidence":
                   "EXACT SAME-BUILD ORIGINAL 31,237/31,237 PASS + "
                   "EXACT SAME-BUILD PUBLIC 10,434/10,434 PASS + "
                   "STATIC FIRST-PARTY PASS + GUARDED LIVE RUNTIME PASS",
               "qualified_independent_family_count": 1,
               "final_cases_generated": 0, "performance": "NOT MEASURED",
               "winner_selected": False, "effects": published_effects,
               "publication": {"path": RESULT, "exclusive_creation": True,
                               "file_fsync_completed": True, "directory_fsync_completed": True}}
    owner = publish(receipt, account)
    require(account["workspace_mutations"] == 1,
            "root V8 execution wrote more than its one exclusive proof")
    return {"schema": SCHEMA + "-root-live-publication", "status": "PASS",
            "publication_owner": owner, "candidate_runtime_non_delegation_status": "PASS",
            "live_candidate_process_count": 16, "live_total_operation_count": 44,
            "maximum_operations_per_fresh_process": 3,
            "original_v30_case_count": 31237, "public_v33_case_count": 10434,
            "exact_v33_original_p0_status": "PASS",
            "exact_v33_original_p0_case_count": 31237,
            "exact_v33_original_p0_mismatch_count": 0,
            "candidate_qualified": True, "qualified_independent_family_count": 1,
            "final_cases_generated": 0, "performance": "NOT MEASURED",
            "winner_selected": False, "effects": account}


def arguments(values: list[str]) -> dict[str, object]:
    require(bool(values) and values[0] in {"--self-test", "--verify-source", "--run"},
            "choose --self-test, --verify-source, or root-only --run")
    result: dict[str, object] = {"mode": values[0]}
    mapping = {"--source-sha256": "source_sha256", "--protocol-sha256": "protocol_sha256",
               "--contract-sha256": "contract_sha256",
               "--pushed-source-sha256": "pushed_source_sha256"}
    index = 1
    while index < len(values):
        name = values[index]
        if name == "--root-authorized":
            require(values[0] == "--run" and "root_authorized" not in result,
                    "candidate/native/private operations are root-only after pushed freeze")
            result["root_authorized"] = True
            index += 1
            continue
        require(name in mapping and index + 1 < len(values), "unexpected V8 argument " + name)
        key = mapping[name]
        require(key not in result, "duplicate V8 owner pin " + name)
        result[key] = values[index + 1]
        index += 2
    required = ({"mode"} if values[0] == "--self-test" else
                {"mode", "source_sha256", "protocol_sha256", "contract_sha256"}
                if values[0] == "--verify-source" else
                {"mode", "root_authorized", "pushed_source_sha256"})
    require(set(result) == required, "V8 mode contains missing, excess, or unauthorized options")
    return result


def main(values: list[str] | None = None) -> int:
    try:
        options = arguments(list(sys.argv[1:] if values is None else values))
        result = (source_self_test() if options["mode"] == "--self-test" else
                  source_verify(options) if options["mode"] == "--verify-source" else
                  run_live(options))
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except (Exception, KeyboardInterrupt) as error:
        answer = {"schema": SCHEMA + "-entry-failure", "status": "FAIL",
                  "error_type": type(error).__name__, "message": str(error)[:2048],
                  "runtime_non_delegation": "NOT ESTABLISHED", "candidate_qualified": False,
                  "final_cases_generated": 0, "performance": "NOT MEASURED",
                  "winner_selected": False}
        sys.stdout.buffer.write(canonical(answer))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
