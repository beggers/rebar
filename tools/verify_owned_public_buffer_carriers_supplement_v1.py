#!/usr/bin/env python3
"""Freeze additional Python regex buffer questions without running a matcher."""

from __future__ import annotations

import sys


_BOOT_MODULES = frozenset(sys.modules)
_FORBIDDEN_BOOT = (
    "re", "_sre", "array", "mmap", "rebar", "candidates", "regex",
    "_regex", "re2", "google_re2", "rure", "pcre", "pcre2", "onig",
    "oniguruma", "hyperscan", "vectorscan", "rust_regex", "fancy_regex",
)
if any(name in _BOOT_MODULES for name in _FORBIDDEN_BOOT) or any(
    any(name.startswith(root + ".") for root in _FORBIDDEN_BOOT)
    for name in _BOOT_MODULES
):
    raise SystemExit("buffer-carrier source freeze requires a clean, engine-free bootstrap")

import ast
import builtins
import hashlib
import os
import stat


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
STDLIB_RE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py"
)
SCHEMA = "rebar-owned-public-buffer-carriers-supplement-v1"
SOURCE = "tools/verify_owned_public_buffer_carriers_supplement_v1.py"
PROTOCOL = "oracle/phase1/P0-PUBLIC-BUFFER-CARRIERS-SUPPLEMENT-V1.md"
CONTRACT = "oracle/phase1/p0-public-buffer-carriers-supplement-v1.json"
ORIGINAL_CASES = 31_237
ORIGINAL_SUITES = 13
ORIGINAL_OBLIGATIONS = 73
ORIGINAL_CROSSWALK = 34
ORIGINAL_PRIVATE_WAIVERS = 13
FUZZ_CASES = 8_244
SIGNATURE_CASES = 50
PROPOSED_HOLDOUT_CASES = 14_155_776
MAX_DOCUMENT_BYTES = 4 * 1024 * 1024
MAX_OWNER_BYTES = 40 * 1024 * 1024
MAX_JSON_DEPTH = 48
EXPECTED_STATUS = "NOT RECORDED"

# Name, relative or exact external path, SHA-256, bytes, device, inode,
# permission, and link count are independent, immutable source observations.
OWNERS = (
    ("goal", "GOAL.md",
     "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
     3756, 2064, 31364044, 0o600, 1),
    ("phase_one_v4_contract", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
     34875, 2064, 524713, 0o600, 1),
    ("phase_one_v4_protocol", "oracle/phase1/P0-COMPLETENESS-V4.md",
     "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
     4261, 2064, 524712, 0o600, 1),
    ("original_p0_contract", "oracle/phase1/p0-completeness-v1.json",
     "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
     45632, 2064, 524385, 0o600, 1),
    ("original_p0_protocol", "oracle/phase1/P0-COMPLETENESS-V1.md",
     "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
     10392, 2064, 524381, 0o600, 1),
    ("official_upstream_tests", "oracle/cpython-3.14.6/test_re.py",
     "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2",
     150895, 2064, 428437, 0o600, 1),
    ("official_upstream_manifest", "oracle/cpython-3.14.6/manifest-v5.json",
     "41b598475a6f756bf63dcd71141d602da05ebb7a810525c45b6c07635b78c0d7",
     75694, 2064, 432193, 0o600, 1),
    ("existing_buffer_exporter_protocol",
     "oracle/cpython-3.14.6/PUBLIC-BUFFER-EXPORTER-V4.md",
     "7f7a4a274c7b59e8f0148f2eae25c5a577fea8886dedbdff27b2fa66fe742905",
     7774, 2064, 432160, 0o600, 1),
    ("existing_two_worker_fuzz_receipt",
     "oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-"
     "two-worker-8244-v3/two-independent-reference-result.json",
     "8377e9c526a487c2e8838d7b8ba74e595b42d069f572bf7ed29f926f82d5b096",
     3658, 2064, 524707, 0o600, 1),
    ("existing_signature_contract", "oracle/phase1/p0-callable-introspection-v1.json",
     "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349",
     14749, 2064, 524650, 0o600, 1),
    ("existing_signature_receipt",
     "oracle/phase1/evidence/callable-introspection-reference-v2-"
     "cpython-3.14.6-publication-receipt.json",
     "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334",
     3533, 2064, 524690, 0o600, 1),
    ("pinned_stdlib_source", STDLIB_RE,
     "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
     17876, 2049, 9596351, 0o600, 1),
    ("pinned_cpython_executable", PYTHON,
     "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
     32387816, 2049, 9594007, 0o711, 1),
)

ARRAY_TYPECODES = ("b", "B", "h", "H", "i", "I", "l", "L", "q", "Q",
                   "f", "d", "u", "w")
UPSTREAM_EMPTY_TYPECODES = "bBhuwHiIlLfd"
BYTE_SWAPPABLE_TYPECODES = ("h", "H", "i", "I", "l", "L", "q", "Q", "f", "d")

# Declarative future fixtures. No constructor, array, mapping, view, regex, or
# callback is invoked while computing, hashing, or verifying the source freeze.
CONTROL_CARRIERS = (
    ("control.bytes.nonempty", "bytes", "readonly", "control-only"),
    ("control.bytearray.nonempty", "bytearray", "writable", "control-only"),
    ("control.bytes.view", "memoryview", "readonly", "control-only"),
    ("control.bytearray.view", "memoryview", "writable", "control-only"),
)
EMPTY_CARRIERS = (
    ("control.bytes.empty", "bytes", "readonly", "empty-control-only"),
    ("control.bytearray.empty", "bytearray", "writable", "empty-control-only"),
    ("view.bytes.empty-contiguous", "memoryview", "readonly", "empty-contiguous-view"),
    ("view.bytearray.empty-contiguous", "memoryview", "writable", "empty-contiguous-view"),
    ("array.empty.q", "array", "writable", "empty-native-typecode-q"),
    ("array.empty.Q", "array", "writable", "empty-native-typecode-Q"),
)
ENDIAN_CARRIERS = (
    ("bytes.endian.little-u16", "bytes", "readonly", "raw-little-endian-u16"),
    ("bytes.endian.big-u16", "bytes", "readonly", "raw-big-endian-u16"),
    ("bytes.endian.little-i16", "bytes", "readonly", "raw-little-endian-i16"),
    ("bytes.endian.big-i16", "bytes", "readonly", "raw-big-endian-i16"),
    ("bytes.endian.little-u32", "bytes", "readonly", "raw-little-endian-u32"),
    ("bytes.endian.big-u32", "bytes", "readonly", "raw-big-endian-u32"),
    ("view.endian.little-raw", "memoryview", "readonly", "raw-little-endian-byte-view"),
    ("view.endian.big-raw", "memoryview", "readonly", "raw-big-endian-byte-view"),
)
ENDIAN_RAW_LAYOUTS = (
    ("bytes.endian.little-u16", "u16", 0x1234, "little", "3412"),
    ("bytes.endian.big-u16", "u16", 0x1234, "big", "1234"),
    ("bytes.endian.little-i16", "i16", -2, "little", "feff"),
    ("bytes.endian.big-i16", "i16", -2, "big", "fffe"),
    ("bytes.endian.little-u32", "u32", 0x12345678, "little", "78563412"),
    ("bytes.endian.big-u32", "u32", 0x12345678, "big", "12345678"),
    ("view.endian.little-raw", "u32", 0x12345678, "little", "78563412"),
    ("view.endian.big-raw", "u32", 0x12345678, "big", "12345678"),
)
VIEW_CARRIERS = (
    ("view.bytes.contiguous", "memoryview", "readonly", "contiguous"),
    ("view.bytes.offset", "memoryview", "readonly", "contiguous-offset"),
    ("view.bytearray.contiguous", "memoryview", "writable", "contiguous"),
    ("view.bytearray.offset", "memoryview", "writable", "contiguous-offset"),
    ("view.bytearray.readonly", "memoryview", "readonly", "toreadonly"),
    ("view.bytes.step-two", "memoryview", "readonly", "noncontiguous-step-2"),
    ("view.bytearray.step-two", "memoryview", "writable", "noncontiguous-step-2"),
    ("view.bytes.reverse", "memoryview", "readonly", "noncontiguous-step-minus-1"),
    ("view.bytearray.reverse", "memoryview", "writable", "noncontiguous-step-minus-1"),
    ("view.bytes.empty-step", "memoryview", "readonly", "empty-step-2"),
    ("view.bytearray.empty-step", "memoryview", "writable", "empty-step-2"),
    ("view.bytes.single-step", "memoryview", "readonly", "single-item-step-3"),
    ("view.bytearray.single-step", "memoryview", "writable", "single-item-step-3"),
    ("view.array.native-h", "memoryview", "writable", "native-format-h"),
    ("view.array.native-H", "memoryview", "writable", "native-format-H"),
    ("view.array.native-i", "memoryview", "writable", "native-format-i"),
    ("view.array.native-I", "memoryview", "writable", "native-format-I"),
    ("view.array.native-q", "memoryview", "writable", "native-format-q"),
    ("view.array.native-Q", "memoryview", "writable", "native-format-Q"),
    ("view.array.native-f", "memoryview", "writable", "native-format-f"),
    ("view.array.native-d", "memoryview", "writable", "native-format-d"),
    ("view.cast.native-B", "memoryview", "readonly", "native-single-character-B"),
    ("view.cast.native-H", "memoryview", "readonly", "native-single-character-H"),
    ("view.cast.native-I", "memoryview", "readonly", "native-single-character-I"),
    ("view.cast.native-q", "memoryview", "readonly", "native-single-character-q"),
    ("view.cast.native-f", "memoryview", "readonly", "native-single-character-f"),
    ("view.cast.B.2x8", "memoryview", "readonly", "C-contiguous-multidimensional-B-2x8"),
    ("view.cast.H.2x4", "memoryview", "readonly", "C-contiguous-multidimensional-H-2x4"),
    ("view.cast.B.4x4.writable", "memoryview", "writable", "C-contiguous-multidimensional-B-4x4"),
    ("view.bytes.released", "memoryview", "released", "released-view"),
    ("view.bytearray.released", "memoryview", "released", "released-view"),
    ("view.array.released", "memoryview", "released", "released-native-array-view"),
)
MAPPING_CARRIERS = (
    ("mmap.anonymous.write.direct", "anonymous-mmap", "writable", "anonymous-write"),
    ("mmap.anonymous.write.view", "memoryview", "writable", "anonymous-write-view"),
    ("mmap.anonymous.write.readonly-view", "memoryview", "readonly", "anonymous-readonly-view"),
    ("mmap.file.read.direct", "file-mmap", "readonly", "file-access-read"),
    ("mmap.file.write.direct", "file-mmap", "writable", "file-access-write"),
    ("mmap.file.copy.direct", "file-mmap", "copy-on-write", "file-access-copy"),
    ("mmap.file.read.view", "memoryview", "readonly", "file-read-view"),
    ("mmap.file.write.view", "memoryview", "writable", "file-write-view"),
    ("mmap.file.copy.view", "memoryview", "copy-on-write", "file-copy-view"),
    ("mmap.file.write.readonly-view", "memoryview", "readonly", "file-write-readonly-view"),
    ("mmap.anonymous.closed", "anonymous-mmap", "closed", "closed-anonymous-mapping"),
    ("mmap.file.closed", "file-mmap", "closed", "closed-file-mapping"),
)

SUBJECT_OPERATIONS = (
    "module.match", "module.search", "module.fullmatch", "module.findall",
    "module.finditer", "module.split", "module.sub.template",
    "module.sub.callback.bytes", "module.sub.callback.bytearray",
    "module.sub.callback.memoryview", "module.sub.callback.exception",
    "module.subn.template", "module.subn.callback.bytes",
    "module.subn.callback.bytearray", "module.subn.callback.memoryview",
    "module.subn.callback.exception", "pattern.match", "pattern.search",
    "pattern.fullmatch", "pattern.findall", "pattern.finditer",
    "pattern.split", "pattern.sub.template", "pattern.sub.callback.bytes",
    "pattern.sub.callback.bytearray", "pattern.sub.callback.memoryview",
    "pattern.sub.callback.exception", "pattern.subn.template",
    "pattern.subn.callback.bytes", "pattern.subn.callback.bytearray",
    "pattern.subn.callback.memoryview", "pattern.subn.callback.exception",
    "pattern.scanner.match", "pattern.scanner.search",
    "pattern.scanner.alternating", "pattern.scanner.window",
    "public-scanner.scan", "public-scanner.callback",
    "public-scanner.remainder", "public-scanner.zero-progress",
    "public-scanner.callback-exception",
)
SUBJECT_SCENARIOS = (
    "literal", "no-match", "empty-pattern", "zero-width", "capturing-group",
    "window", "high-byte", "embedded-nul", "lookaround",
)
PATTERN_CARRIER_OPERATIONS = (
    "module.compile", "module.match", "module.search", "module.fullmatch",
    "module.findall", "module.finditer", "module.split", "module.sub",
    "module.subn",
)
PATTERN_CARRIER_SCENARIOS = (
    "bytes-pattern-position", "text-pattern-position", "explicit-flags",
    "repeated-cache-key", "mutated-cache-key",
)
REPLACEMENT_OPERATIONS = (
    "module.sub.template", "module.subn.template", "pattern.sub.template",
    "pattern.subn.template", "module.sub.callback-return",
    "module.subn.callback-return", "pattern.sub.callback-return",
    "pattern.subn.callback-return",
)
REPLACEMENT_SCENARIOS = (
    "literal", "numeric-backreference", "named-backreference",
    "escaped-backslash", "invalid-escape", "empty-replacement",
)
ESCAPE_SCENARIOS = (
    "plain-bytes", "regex-special-bytes", "high-byte", "embedded-nul",
)
LIFETIME_OPERATIONS = (
    "module.match", "module.search", "module.finditer", "module.sub.template",
    "module.sub.callback", "module.subn.callback", "pattern.match",
    "pattern.search", "pattern.finditer", "pattern.sub.callback",
    "pattern.scanner.match", "pattern.scanner.search", "public-scanner.scan",
    "public-scanner.callback",
)
LIFETIME_SCENARIOS = (
    "match-string-identity", "match-group-before-mutation",
    "match-group-after-same-length-mutation", "match-group-after-shorter-mutation",
    "byte-offset-not-element-offset", "nested-result-exact-type",
    "iterator-live-export", "iterator-exhausted-export",
    "iterator-dropped-export", "scanner-live-export", "scanner-exhausted-export",
    "scanner-dropped-export", "owner-gc-with-live-holder",
    "owner-gc-after-holder-release", "view-release-before-operation",
    "view-release-with-live-holder", "mapping-close-with-live-view",
    "mapping-close-after-view-release", "mapping-resize-with-live-view",
    "mapping-resize-after-view-release", "array-resize-with-live-view",
    "array-resize-after-view-release", "bytearray-resize-with-live-view",
    "bytearray-resize-after-view-release", "callback-same-length-mutation",
    "callback-resize-attempt", "callback-user-exception-identity",
    "callback-keyboard-interrupt", "callback-system-exit",
    "callback-generator-exit", "file-backed-close-before-unlink",
    "public-scanner-remainder-slice-type",
)
OBSERVATION_FIELDS = (
    "case_id", "carrier_id", "carrier_role", "operation", "scenario",
    "fixture_construction_status", "carrier_exact_type", "carrier_readonly",
    "buffer_format", "buffer_itemsize", "buffer_nbytes", "buffer_shape",
    "buffer_strides", "c_contiguous", "host_byteorder", "result_exact_type",
    "nested_result_types", "result_bytes", "span_byte_offsets",
    "match_string_identity", "scanner_remainder_exact_type",
    "scanner_remainder_buffer_metadata", "callback_argument_types",
    "callback_return_exact_type", "callback_call_count", "exception_module",
    "exception_class", "exception_args", "exception_message",
    "warning_category", "warning_message", "exporter_events",
    "holder_lifetime", "garbage_collection_events", "cleanup_events",
)


class FreezeError(Exception):
    """A source-only buffer-carrier freeze failed closed."""


_AUDIT_INSTALLED = False
_BLOCKED_AUDIT_EVENTS: dict[str, int] = {}
_BLOCKED_CALLS: dict[str, int] = {}
_CALL_GUARDS: list[tuple[object, str, object]] = []
_AUTHENTICATED_OWNERS: dict[str, dict[str, object]] = {}
_EXPECTED_CONTRACT_CACHE: dict[tuple[str, str], dict[str, object]] = {}
_CAPTURED_IO_OPEN = getattr(sys.modules.get("_io"), "open", None)
_CAPTURED_POSIX_OPEN = getattr(sys.modules.get("posix"), "open", None)
_CAPTURED_POSIX_EXECV = getattr(sys.modules.get("posix"), "execv", None)
_CAPTURED_BUILTIN_IMPORT = builtins.__import__
_CAPTURED_OS_OPEN = os.open
_CAPTURED_OS_STAT = os.stat


def require(condition: object, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete, exact source bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value)
            and len(set(value)) > 1,
            "require an independent lowercase SHA-256 for " + label)
    return value


def clean_bootstrap() -> None:
    require(tuple(sys.version_info[:3]) == (3, 14, 6),
            "use only pinned stable CPython 3.14.6")
    require(sys.executable == PYTHON and sys.flags.isolated == 1
            and sys.dont_write_bytecode and sys.flags.no_site == 1,
            "run the pinned interpreter with -I -B -S")
    require(not any(name in sys.modules for name in _FORBIDDEN_BOOT),
            "never import re, _sre, mmap, array, rebar, or candidates")
    require(not any(any(name.startswith(root + ".") for root in _FORBIDDEN_BOOT)
                    for name in sys.modules),
            "never import a candidate, external matcher, or public replacement")
    require(sys.byteorder in ("little", "big"),
            "freeze the actual pinned host byte order without constructing an array")


def absolute_owner(path: str) -> str:
    require(type(path) is str and bool(path) and "\x00" not in path,
            "reject an empty or embedded-NUL source-owner path")
    if path in (PYTHON, STDLIB_RE):
        return path
    require(not path.startswith("/") and all(
        piece not in ("", ".", "..") for piece in path.split("/")
    ), "reject an absolute, ambiguous, or escaping source-owner path")
    return ROOT + "/" + path


def allowed_paths() -> frozenset[str]:
    return frozenset(
        [absolute_owner(SOURCE), absolute_owner(PROTOCOL), absolute_owner(CONTRACT)]
        + [absolute_owner(item[1]) for item in OWNERS]
    )


def blocked_audit(event: str, detail: str) -> None:
    _BLOCKED_AUDIT_EVENTS[event] = _BLOCKED_AUDIT_EVENTS.get(event, 0) + 1
    raise FreezeError("physical source-only audit blocked " + event + ": " + detail)


def source_audit_hook(event: str, arguments: tuple[object, ...]) -> None:
    if event == "open":
        path = arguments[0] if arguments else None
        flags = arguments[2] if len(arguments) > 2 else None
        if type(path) is not str or path not in allowed_paths():
            blocked_audit(event, "read is outside the immutable source-owner allowlist")
        if type(flags) is not int:
            blocked_audit(event, "require exact read-only descriptor flags")
        prohibited = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                      | os.O_APPEND | getattr(os, "O_TMPFILE", 0))
        if flags & prohibited:
            blocked_audit(event, "workspace writes and creation are forbidden")
        if flags & getattr(os, "O_NOFOLLOW", 0) != getattr(os, "O_NOFOLLOW", 0):
            blocked_audit(event, "source reads must not follow a final symlink")
        if flags & getattr(os, "O_CLOEXEC", 0) != getattr(os, "O_CLOEXEC", 0):
            blocked_audit(event, "source descriptors require close-on-exec")
        return
    if event == "compile":
        source = arguments[0] if arguments else None
        filename = arguments[1] if len(arguments) > 1 else None
        allowed = {
            absolute_owner("oracle/cpython-3.14.6/test_re.py"):
            "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2",
            STDLIB_RE:
            "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
        }
        if filename not in allowed or type(source) is not bytes:
            blocked_audit(event, "only authenticated upstream source AST parsing is allowed")
        if len(source) > MAX_DOCUMENT_BYTES or digest(source) != allowed[filename]:
            blocked_audit(event, "upstream AST source differs from its pinned bytes")
        return
    if (event == "import" or event == "exec" or event == "sys.addaudithook"
            or event.startswith("ctypes.") or event.startswith("subprocess.")
            or event.startswith("socket.") or event.startswith("multiprocessing.")
            or event.startswith("threading.") or event.startswith("time.")
            or event.startswith("mmap.") or event.startswith("array.")
            or event.startswith("gc.") or event.startswith("gzip.")
            or event.startswith("zlib.") or event.startswith("marshal.")
            or event.startswith("os.exec") or event.startswith("os.spawn")
            or event.startswith("os.posix_spawn")
            or event in {
                "os.system", "os.fork", "os.forkpty", "os.chdir", "os.putenv",
                "os.unsetenv", "os.remove", "os.rename", "os.replace",
                "os.mkdir", "os.rmdir", "os.symlink", "os.link", "os.chmod",
                "os.chown", "os.truncate", "os.utime", "os.scandir",
                "os.listdir", "os.walk", "os.fwalk", "os.readlink",
                "os.getxattr", "os.setxattr", "os.removexattr",
                "code.__new__", "function.__new__", "builtins.input",
            }):
        blocked_audit(event, "matching, buffer construction, import, archive, "
                      "native load, process, time, or mutation is forbidden")


def blocked_call(kind: str, name: str) -> None:
    _BLOCKED_CALLS[kind] = _BLOCKED_CALLS.get(kind, 0) + 1
    raise FreezeError("physical source-only call blocked " + kind + ": " + name)


def guard_call(owner: object, name: str, kind: str) -> None:
    original = getattr(owner, name, None)
    if original is None:
        return

    def denied(*_arguments: object, **_keywords: object) -> object:
        detail = (name + ":" + str(_arguments[0])
                  if name == "__import__" and _arguments else name)
        blocked_call(kind, detail)
        raise AssertionError("unreachable denied source-only call")

    _CALL_GUARDS.append((owner, name, original))
    setattr(owner, name, denied)


def install_wall() -> None:
    global _AUDIT_INSTALLED
    clean_bootstrap()
    require(not _AUDIT_INSTALLED and not _CALL_GUARDS,
            "install exactly one irreversible source-only audit hook")
    sys.addaudithook(source_audit_hook)
    _AUDIT_INSTALLED = True
    for name in ("__import__", "open", "memoryview", "bytearray", "input"):
        guard_call(builtins, name, "import" if name == "__import__"
                   else "buffer" if name in ("memoryview", "bytearray")
                   else "filesystem")
    for name in ("scandir", "listdir", "walk", "fwalk", "readlink", "getxattr"):
        guard_call(os, name, "filesystem")
    for name in ("write", "mkdir", "makedirs", "unlink", "remove", "rename",
                 "replace", "rmdir", "symlink", "link", "chmod", "chown",
                 "truncate", "utime", "putenv", "unsetenv", "urandom",
                 "fsync", "fdatasync"):
        guard_call(os, name, "write")
    for name in ("fork", "forkpty", "system", "posix_spawn", "posix_spawnp",
                 "execv", "execve", "execl", "execle", "execlp", "execlpe",
                 "execvp", "execvpe", "spawnv", "spawnve", "spawnvp", "spawnvpe"):
        guard_call(os, name, "process")
    direct = (
        ("_io", ("open",), "filesystem"),
        ("posix", ("scandir", "listdir", "walk", "readlink", "getxattr"), "filesystem"),
        ("posix", ("write", "mkdir", "unlink", "remove", "rename", "replace",
                    "rmdir", "symlink", "link", "chmod", "chown", "truncate",
                    "utime", "putenv", "unsetenv", "urandom", "fsync"), "write"),
        ("posix", ("fork", "forkpty", "system", "posix_spawn", "posix_spawnp",
                    "execv", "execve", "spawnv", "spawnve", "spawnvp", "spawnvpe"),
         "process"),
        ("_posixsubprocess", ("fork_exec",), "process"),
        ("_ctypes", ("dlopen",), "native"),
        ("_imp", ("create_dynamic", "exec_dynamic", "create_builtin",
                   "exec_builtin", "init_frozen"), "native"),
        ("_socket", ("socket", "getaddrinfo"), "network"),
        ("_thread", ("start_new_thread", "start_joinable_thread"), "thread"),
    )
    for module_name, names, kind in direct:
        module = sys.modules.get(module_name)
        if module is not None:
            for name in names:
                guard_call(module, name, kind)
    clean_bootstrap()


def quoted(value: str) -> str:
    require(type(value) is str, "JSON strings require exact built-in str")
    result = ['"']
    escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    for character in value:
        number = ord(character)
        if character in escapes:
            result.append(escapes[character])
        elif number < 0x20 or 0x7f <= number <= 0xffff:
            result.append("\\u" + format(number, "04x"))
        elif number > 0xffff:
            number -= 0x10000
            result.append("\\u" + format(0xd800 + (number >> 10), "04x"))
            result.append("\\u" + format(0xdc00 + (number & 0x3ff), "04x"))
        else:
            result.append(character)
    result.append('"')
    return "".join(result)


def canonical_text(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "canonical JSON nesting exceeds its limit")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is str:
        return quoted(value)
    if type(value) is int:
        return str(value)
    if type(value) is float:
        require(value == value and abs(value) != float("inf"),
                "reject nonfinite JSON observations")
        return repr(value)
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical_text(item, depth + 1)
                               for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value),
                "reject non-string JSON object keys")
        return "{" + ",".join(quoted(key) + ":" + canonical_text(value[key], depth + 1)
                               for key in sorted(value)) + "}"
    raise FreezeError("unsupported canonical JSON type: " + type(value).__name__)


def canonical_bytes(value: object) -> bytes:
    result = canonical_text(value).encode("ascii") + b"\n"
    require(len(result) <= MAX_DOCUMENT_BYTES,
            "canonical document exceeds its separately frozen byte limit")
    return result


class StrictJSON:
    """A bounded duplicate-strict JSON decoder without json or regex imports."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and 0 < len(raw) <= MAX_DOCUMENT_BYTES,
                "reject an empty or oversized source-only JSON document")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise FreezeError("source-only JSON must be valid UTF-8") from error
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"',
                "a JSON object key or value must be quoted")
        self.index += 1
        result: list[str] = []
        plain = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                 "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            character = self.text[self.index]
            self.index += 1
            if character == '"':
                return "".join(result)
            if character != "\\":
                require(ord(character) >= 0x20,
                        "reject an unescaped JSON control character")
                result.append(character)
                continue
            require(self.index < len(self.text), "reject a truncated JSON escape")
            escape = self.text[self.index]
            self.index += 1
            if escape != "u":
                require(escape in plain, "reject an unknown JSON escape")
                result.append(plain[escape])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4 and all(
                value in "0123456789abcdefABCDEF" for value in digits
            ), "reject an invalid JSON Unicode escape")
            self.index += 4
            codepoint = int(digits, 16)
            if 0xd800 <= codepoint <= 0xdbff:
                require(self.text[self.index:self.index + 2] == "\\u",
                        "reject an unpaired high surrogate")
                low_digits = self.text[self.index + 2:self.index + 6]
                require(len(low_digits) == 4 and all(
                    value in "0123456789abcdefABCDEF" for value in low_digits
                ), "reject an invalid low-surrogate escape")
                lower = int(low_digits, 16)
                require(0xdc00 <= lower <= 0xdfff,
                        "reject an incorrectly paired high surrogate")
                self.index += 6
                result.append(chr(0x10000 + ((codepoint - 0xd800) << 10)
                                  + lower - 0xdc00))
            else:
                require(not 0xdc00 <= codepoint <= 0xdfff,
                        "reject an unpaired low surrogate")
                result.append(chr(codepoint))
        raise FreezeError("reject an unterminated JSON string")

    def number(self) -> int | float:
        begin = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "reject an incomplete JSON number")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text)
                    or self.text[self.index] not in "0123456789",
                    "reject a JSON number with a leading zero")
        else:
            require(self.text[self.index] in "123456789",
                    "reject an invalid JSON integer")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        fractional = False
        if self.text[self.index:self.index + 1] == ".":
            fractional = True
            self.index += 1
            start = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > start, "reject an incomplete JSON fraction")
        if self.text[self.index:self.index + 1] in ("e", "E"):
            fractional = True
            self.index += 1
            if self.text[self.index:self.index + 1] in ("+", "-"):
                self.index += 1
            start = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > start, "reject an incomplete JSON exponent")
        token = self.text[begin:self.index]
        require(len(token) <= 128, "reject an overlong JSON number")
        if not fractional:
            return int(token)
        value = float(token)
        require(value == value and abs(value) != float("inf"),
                "reject a nonfinite JSON number")
        return value

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "reject an overdeep JSON document")
        self.whitespace()
        require(self.index < len(self.text), "reject a missing JSON value")
        character = self.text[self.index]
        if character == '"':
            return self.string()
        if character == "{":
            self.index += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.text[self.index:self.index + 1] == "}":
                self.index += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                require(key not in result, "reject a duplicate JSON key: " + key)
                self.whitespace()
                require(self.text[self.index:self.index + 1] == ":",
                        "reject a missing JSON object colon")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "}":
                    return result
                require(separator == ",", "reject an invalid JSON object separator")
        if character == "[":
            self.index += 1
            result: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result
            while True:
                result.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return result
                require(separator == ",", "reject an invalid JSON array separator")
        if character == "-" or character in "0123456789":
            return self.number()
        for word, result in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(word, self.index):
                self.index += len(word)
                return result
        raise FreezeError("reject an invalid JSON literal")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text),
                "reject trailing data or a second JSON document")
        return result


def decode_json(raw: bytes) -> object:
    return StrictJSON(raw).decode()


def read_exact(path: str, expected: str, size: int, device: int | None = None,
               inode: int | None = None, mode: int | None = None,
               links: int | None = None) -> bytes:
    checked_digest(expected, path)
    require(type(size) is int and 0 < size <= MAX_OWNER_BYTES,
            "require a positive, bounded source-owner size")
    absolute = absolute_owner(path)
    require(absolute in allowed_paths(), "reject an unlisted source-owner path")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = _CAPTURED_OS_OPEN(absolute, flags)
    except OSError as error:
        raise FreezeError("cannot authenticate immutable source owner: " + path) from error
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_size == size,
                "reject an altered source-owner size or file type: " + path)
        require(device is None or before.st_dev == device,
                "reject a substituted source-owner device: " + path)
        require(inode is None or before.st_ino == inode,
                "reject a substituted source-owner inode: " + path)
        require(mode is None or stat.S_IMODE(before.st_mode) == mode,
                "reject altered source-owner permissions: " + path)
        require(links is None or before.st_nlink == links,
                "reject an aliased source-owner link count: " + path)
        pieces: list[bytes] = []
        total = 0
        while total < size:
            piece = os.read(descriptor, min(262_144, size - total))
            require(bool(piece), "reject a truncated immutable source owner: " + path)
            pieces.append(piece)
            total += len(piece)
        require(os.read(descriptor, 1) == b"",
                "reject an owner that grew during authentication: " + path)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size, before.st_nlink,
                 before.st_mtime_ns, stat.S_IMODE(before.st_mode))
                == (after.st_dev, after.st_ino, after.st_size, after.st_nlink,
                    after.st_mtime_ns, stat.S_IMODE(after.st_mode)),
                "reject a source owner replaced during descriptor reading: " + path)
    finally:
        os.close(descriptor)
    raw = b"".join(pieces)
    require(len(raw) == size and digest(raw) == expected,
            "reject altered complete immutable source-owner bytes: " + path)
    return raw


def read_dynamic_owner(path: str, expected: str) -> bytes:
    absolute = absolute_owner(path)
    require(absolute in allowed_paths(), "reject an unlisted dynamic source owner")
    try:
        identity = _CAPTURED_OS_STAT(absolute, follow_symlinks=False)
    except OSError as error:
        raise FreezeError("missing source-freeze owner: " + path) from error
    require(stat.S_ISREG(identity.st_mode) and identity.st_nlink == 1
            and stat.S_IMODE(identity.st_mode) == 0o600,
            "reject a linked, nonregular, or writable source-freeze owner: " + path)
    return read_exact(path, expected, identity.st_size, identity.st_dev,
                      identity.st_ino, stat.S_IMODE(identity.st_mode),
                      identity.st_nlink)


def owner_document(owner: tuple[object, ...]) -> dict[str, object]:
    name, path, expected, size, device, inode, mode, links = owner
    return {"name": name, "path": path, "sha256": expected, "bytes": size,
            "device": device, "inode": inode, "mode": format(mode, "04o"),
            "nlink": links}


def authenticate_owners() -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for item in OWNERS:
        name, path, expected, size, device, inode, mode, links = item
        result[name] = read_exact(path, expected, size, device, inode, mode, links)
        _AUTHENTICATED_OWNERS[name] = owner_document(item)
    return result


def carriers() -> tuple[tuple[str, str, str, str], ...]:
    arrays = tuple(
        ("array.native." + code, "array", "writable", "native-typecode-" + code)
        for code in ARRAY_TYPECODES
    )
    swapped = tuple(
        ("array.byteswapped." + code, "array", "writable",
         "native-typecode-" + code + "-byteswapped")
        for code in BYTE_SWAPPABLE_TYPECODES
    )
    result = (CONTROL_CARRIERS + EMPTY_CARRIERS + arrays + swapped
              + ENDIAN_CARRIERS + VIEW_CARRIERS + MAPPING_CARRIERS)
    names = [row[0] for row in result]
    require(len(names) == len(set(names)),
            "reject duplicate or silently replaced frozen carrier definitions")
    return result


def matrix_row(cohort: str, carrier: tuple[str, str, str, str], operation: str,
               scenario: str, role: str) -> dict[str, object]:
    identity, carrier_type, readonly, layout = carrier
    return {
        "case_id": "buffer-carriers.v1/" + cohort + "/" + identity + "/"
        + operation + "/" + scenario,
        "cohort": cohort,
        "carrier_id": identity,
        "carrier_kind": carrier_type,
        "carrier_role": role,
        "declared_layout": layout,
        "declared_mutability": readonly,
        "operation": operation,
        "scenario": scenario,
        "expected": EXPECTED_STATUS,
    }


def subject_applicable(operation: str, scenario: str) -> bool:
    window_operations = (
        "pattern.match", "pattern.search", "pattern.fullmatch",
        "pattern.findall", "pattern.finditer", "pattern.scanner.match",
        "pattern.scanner.search", "pattern.scanner.alternating",
        "pattern.scanner.window",
    )
    if scenario == "window":
        return operation in window_operations
    if operation == "pattern.scanner.window":
        return False
    return True


def replacement_applicable(carrier: tuple[str, str, str, str],
                           scenario: str) -> bool:
    identity, _kind, _mutability, layout = carrier
    empty = (identity in {row[0] for row in EMPTY_CARRIERS}
             or layout == "empty-step-2")
    if scenario == "empty-replacement":
        return empty
    return not empty


def lifetime_applicable(carrier: tuple[str, str, str, str],
                        operation: str, scenario: str) -> bool:
    identity, kind, mutability, _layout = carrier
    mapping = identity.startswith("mmap.")
    file_mapping = identity.startswith("mmap.file.")
    array_owner = identity.startswith(("array.", "view.array."))
    bytearray_owner = (identity.startswith(("control.bytearray.", "view.bytearray."))
                       or identity == "view.cast.B.4x4.writable")
    observable_match = any(value in operation for value in
                           ("match", "search", "finditer", "callback"))
    if mutability == "closed":
        return False
    if mutability == "released":
        return scenario == "view-release-before-operation" and kind == "memoryview"
    if scenario in ("match-group-after-same-length-mutation",
                    "match-group-after-shorter-mutation",
                    "callback-same-length-mutation", "callback-resize-attempt"):
        if mutability not in ("writable", "copy-on-write"):
            return False
    if scenario == "match-group-after-shorter-mutation" and kind == "memoryview":
        return False
    if scenario.startswith("match-group-") or scenario == "match-string-identity":
        if not observable_match:
            return False
    if scenario == "byte-offset-not-element-offset":
        wide_array = (identity.startswith(("array.native.", "array.byteswapped."))
                      and identity.rsplit(".", 1)[-1] not in ("b", "B"))
        wide_array_view = identity.startswith("view.array.native-")
        wide_cast = (identity.startswith("view.cast.native-")
                     and not identity.endswith("-B"))
        wide_multidimensional = identity == "view.cast.H.2x4"
        return (wide_array or wide_array_view or wide_cast
                or wide_multidimensional) and observable_match
    if scenario.startswith("mapping-"):
        return mapping
    if scenario == "file-backed-close-before-unlink":
        return file_mapping
    if scenario.startswith("array-resize-"):
        return array_owner
    if scenario.startswith("bytearray-resize-"):
        return bytearray_owner
    if scenario.startswith("view-release-"):
        return kind == "memoryview"
    if scenario.startswith("iterator-"):
        return operation.endswith("finditer")
    if scenario.startswith("scanner-"):
        return operation.startswith("pattern.scanner.")
    if scenario == "public-scanner-remainder-slice-type":
        return operation.startswith("public-scanner.")
    if scenario.startswith("callback-"):
        return "callback" in operation
    return True


def case_matrix() -> list[dict[str, object]]:
    all_carriers = carriers()
    result: list[dict[str, object]] = []
    for carrier in all_carriers:
        for operation in SUBJECT_OPERATIONS:
            for scenario in SUBJECT_SCENARIOS:
                if subject_applicable(operation, scenario):
                    result.append(matrix_row("subject", carrier, operation,
                                             scenario, "subject"))
    for carrier in all_carriers:
        for operation in PATTERN_CARRIER_OPERATIONS:
            for scenario in PATTERN_CARRIER_SCENARIOS:
                result.append(matrix_row("pattern-carrier", carrier, operation,
                                         scenario, "pattern"))
    for carrier in all_carriers:
        for operation in REPLACEMENT_OPERATIONS:
            for scenario in REPLACEMENT_SCENARIOS:
                if replacement_applicable(carrier, scenario):
                    result.append(matrix_row("replacement-carrier", carrier,
                                             operation, scenario, "replacement"))
    for carrier in all_carriers:
        for scenario in ESCAPE_SCENARIOS:
            result.append(matrix_row("escape-carrier", carrier, "module.escape",
                                     scenario, "escape-argument"))
    for carrier in all_carriers:
        for operation in LIFETIME_OPERATIONS:
            for scenario in LIFETIME_SCENARIOS:
                if lifetime_applicable(carrier, operation, scenario):
                    result.append(matrix_row("owner-lifetime", carrier, operation,
                                             scenario, "subject-and-exporter"))
    identities = [row["case_id"] for row in result]
    require(len(identities) == len(set(identities)),
            "reject a duplicate, missing, or shadowed additive case")
    require(result and all(row["expected"] == EXPECTED_STATUS for row in result),
            "never guess a reference answer or start a candidate")
    return result


def endian_layouts() -> list[dict[str, object]]:
    known = {row[0] for row in ENDIAN_CARRIERS}
    seen: set[str] = set()
    result: list[dict[str, object]] = []
    for identity, integer_type, value, byteorder, actual_hex in ENDIAN_RAW_LAYOUTS:
        require(identity in known and identity not in seen,
                "reject a missing or repeated explicit raw-endian carrier")
        require(integer_type in ("u16", "i16", "u32")
                and byteorder in ("little", "big")
                and type(value) is int and type(actual_hex) is str,
                "reject an ambiguous explicit raw-endian fixture")
        width = 16 if integer_type.endswith("16") else 32
        if integer_type.startswith("u"):
            require(0 <= value < 1 << width,
                    "reject an out-of-range unsigned endian fixture")
            unsigned = value
        else:
            require(-(1 << (width - 1)) <= value < (1 << (width - 1)),
                    "reject an out-of-range signed endian fixture")
            unsigned = value if value >= 0 else value + (1 << width)
        big_hex = format(unsigned, "0" + str(width // 4) + "x")
        pairs = [big_hex[index:index + 2] for index in range(0, len(big_hex), 2)]
        computed = "".join(pairs if byteorder == "big" else reversed(pairs))
        require(actual_hex == computed,
                "reject fabricated signed, width, or explicit endian fixture bytes")
        seen.add(identity)
        result.append({"carrier_id": identity, "integer_type": integer_type,
                       "integer_value": value, "byteorder": byteorder,
                       "raw_bytes_hex": actual_hex,
                       "fixture_constructed": False})
    require(seen == known, "freeze exact bytes for every raw endian carrier")
    return result


def matrix_description() -> dict[str, object]:
    rows = case_matrix()
    stream = hashlib.sha256()
    counts: dict[str, int] = {}
    for row in rows:
        stream.update(canonical_bytes(row))
        cohort = row["cohort"]
        require(type(cohort) is str, "reject a non-string additive cohort")
        counts[cohort] = counts.get(cohort, 0) + 1
    layouts = endian_layouts()
    exact_hex = {row["carrier_id"]: row["raw_bytes_hex"] for row in layouts}
    catalog = [
        {"carrier_id": name, "carrier_kind": kind, "declared_mutability": writable,
         "fixture_recipe": recipe, "fixture_constructed": False,
         "fixture_raw_bytes_hex": exact_hex.get(name, EXPECTED_STATUS),
         "itemsize": EXPECTED_STATUS, "exact_buffer_format": EXPECTED_STATUS,
         "reference_outcome": EXPECTED_STATUS}
        for name, kind, writable, recipe in carriers()
    ]
    return {
        "case_count": len(rows),
        "case_ids_are_unique": True,
        "case_id_prefix": "buffer-carriers.v1/",
        "first_case_id": rows[0]["case_id"],
        "last_case_id": rows[-1]["case_id"],
        "canonical_newline_delimited_matrix_sha256": stream.hexdigest(),
        "cohort_case_counts": counts,
        "subject_applicability_is_explicit": True,
        "replacement_applicability_is_explicit": True,
        "lifetime_applicability_is_explicit": True,
        "carrier_count": len(catalog),
        "carriers": catalog,
        "native_array_typecodes": list(ARRAY_TYPECODES),
        "original_upstream_empty_array_typecodes": UPSTREAM_EMPTY_TYPECODES,
        "byte_swappable_array_typecodes": list(BYTE_SWAPPABLE_TYPECODES),
        "native_byteorder": sys.byteorder,
        "explicit_endian_raw_layouts": layouts,
        "explicit_little_endian_input":
        "frozen raw little-endian byte fixtures; expected NOT RECORDED",
        "explicit_big_endian_input":
        "frozen raw big-endian byte fixtures; expected NOT RECORDED",
        "memoryview_non_native_cast_assumed_valid": False,
        "subject_operations": list(SUBJECT_OPERATIONS),
        "subject_scenarios": list(SUBJECT_SCENARIOS),
        "pattern_carrier_operations": list(PATTERN_CARRIER_OPERATIONS),
        "pattern_carrier_scenarios": list(PATTERN_CARRIER_SCENARIOS),
        "replacement_operations": list(REPLACEMENT_OPERATIONS),
        "replacement_scenarios": list(REPLACEMENT_SCENARIOS),
        "escape_scenarios": list(ESCAPE_SCENARIOS),
        "lifetime_operations": list(LIFETIME_OPERATIONS),
        "lifetime_scenarios": list(LIFETIME_SCENARIOS),
        "future_exact_observation_fields": list(OBSERVATION_FIELDS),
        "expected_records": EXPECTED_STATUS,
        "actual_reference_worker_count": 0,
        "actual_candidate_worker_count": 0,
    }


def boundaries() -> dict[str, object]:
    return {
        "source_audit_hook_installed": True,
        "clean_engine_free_bootstrap_required": True,
        "stdlib_regex_import_count": 0,
        "candidate_import_count": 0,
        "public_replacement_import_count": 0,
        "native_libraries_loaded": 0,
        "actual_reference_workers_started": 0,
        "actual_candidate_workers_started": 0,
        "array_objects_constructed": 0,
        "memoryview_objects_constructed": 0,
        "anonymous_mappings_created": 0,
        "file_backed_mappings_created": 0,
        "mapping_backing_files_created": 0,
        "garbage_collections_performed": 0,
        "callback_invocations": 0,
        "regex_operations_executed": 0,
        "network_operations": 0,
        "thread_starts": 0,
        "process_starts": 0,
        "clock_samples": 0,
        "compressed_archives_opened": 0,
        "compressed_archives_decompressed": 0,
        "performance_cases_read": 0,
        "holdout_cases_read": 0,
        "workspace_files_created": 0,
        "workspace_files_modified": 0,
        "proposed_holdout_case_count": PROPOSED_HOLDOUT_CASES,
        "holdout_frozen": False,
        "holdout_generated": False,
        "holdout_opened": False,
        "holdout_status": "NOT FROZEN / NOT GENERATED / NOT OPENED",
        "reference_status": "NOT RUN",
        "candidate_status": "NOT RUN",
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def contract_document(source_pin: str, protocol_pin: str) -> dict[str, object]:
    checked_digest(source_pin, "buffer-carrier source")
    checked_digest(protocol_pin, "buffer-carrier protocol")
    key = (source_pin, protocol_pin)
    previous = _EXPECTED_CONTRACT_CACHE.get(key)
    if previous is not None:
        return previous
    result = {
        "schema": SCHEMA + "-frozen-contract",
        "version": 1,
        "phase": "CORRECTNESS ORACLE",
        "status": "SOURCE FROZEN; TWO-REFERENCE BASELINE NOT RUN",
        "status_scope": "ADDITIVE SOURCE FREEZE ONLY; NO OBSERVED BUFFER OUTCOMES",
        "source": {"path": SOURCE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL, "sha256": protocol_pin},
        "pinned_cpython": owner_document(OWNERS[-1]),
        "goal": owner_document(OWNERS[0]),
        "authenticated_source_owners": [owner_document(item) for item in OWNERS],
        "original_p0": {
            "case_execution_denominator": ORIGINAL_CASES,
            "suite_count": ORIGINAL_SUITES,
            "obligation_count": ORIGINAL_OBLIGATIONS,
            "crosswalk_count": ORIGINAL_CROSSWALK,
            "named_private_waiver_count": ORIGINAL_PRIVATE_WAIVERS,
            "denominator_changed": False,
            "cases_removed": 0,
            "cases_waived": 0,
            "additional_cases_included_in_original": False,
            "original_memoryview_cases": 768,
            "original_managed_lifetime_cases": 1024,
            "original_scanner_cases": 1024,
            "original_substitution_buffer_cases": 5120,
            "original_shape_changing_buffer_cases": 10240,
            "original_pep688_exporter_cases": 264,
            "original_pep688_matrix_sha256":
            "2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891",
        },
        "separate_existing_references": {
            "differential_fuzz_case_count": FUZZ_CASES,
            "differential_fuzz_independent_reference_count": 2,
            "differential_fuzz_status": "PASS",
            "callable_signature_case_count": SIGNATURE_CASES,
            "callable_signature_independent_reference_count": 2,
            "callable_signature_status": "PASS",
            "supplements_included_in_original_denominator": False,
        },
        "additive_matrix": matrix_description(),
        "reference_plan": {
            "status": "NOT RUN",
            "expected_records": EXPECTED_STATUS,
            "required_independent_official_cpython_workers": 2,
            "actual_reference_workers_started": 0,
            "candidate_workers_started": 0,
            "record_exact_nested_result_types": True,
            "record_exception_class_module_message_and_args": True,
            "record_array_element_width_and_byte_offsets": True,
            "record_actual_native_and_swapped_byte_layout": True,
            "record_array_u_deprecation_warnings": True,
            "record_memoryview_contiguity_format_shape_strides": True,
            "record_public_scanner_remainder_carrier_type": True,
            "record_match_string_identity": True,
            "record_all_lifetime_cleanup_and_exporter_events": True,
            "source_freeze_predicts_observations": False,
            "unsupported_fixture_exceptions_predicted": False,
        },
        "source_only_boundaries": boundaries(),
        "candidate_qualification": {
            "status": "BLOCKED",
            "original_p0_candidate_status": "NOT QUALIFIED",
            "additive_buffer_carrier_candidate_status": "NOT RUN",
            "qualified_candidate_count": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "winner_selected": False,
        },
    }
    _EXPECTED_CONTRACT_CACHE[key] = result
    return result


def validate_original_context(owners: dict[str, bytes]) -> None:
    phase_one = decode_json(owners["phase_one_v4_contract"])
    original = decode_json(owners["original_p0_contract"])
    fuzz = decode_json(owners["existing_two_worker_fuzz_receipt"])
    signature = decode_json(owners["existing_signature_receipt"])
    require(type(phase_one) is dict
            and phase_one.get("schema") == "rebar-cpython-re-p0-completeness-v4"
            and phase_one.get("status") == "PASS"
            and phase_one.get("original_case_execution_denominator") == ORIGINAL_CASES
            and phase_one.get("original_suite_count") == ORIGINAL_SUITES
            and phase_one.get("original_obligation_count") == ORIGINAL_OBLIGATIONS
            and phase_one.get("original_crosswalk_count") == ORIGINAL_CROSSWALK
            and phase_one.get("original_named_private_waiver_count")
            == ORIGINAL_PRIVATE_WAIVERS,
            "reject a changed original 31,237 / 13 / 73 / 34 / 13 baseline")
    require(type(original) is dict
            and original.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and type(original.get("suites")) is list
            and len(original["suites"]) == ORIGINAL_SUITES
            and type(original.get("denominator")) is dict
            and original["denominator"].get("final_required_case_execution_denominator")
            == ORIGINAL_CASES
            and type(original.get("obligations")) is dict
            and original["obligations"].get("crosswalk_count") == ORIGINAL_CROSSWALK,
            "reject changed immutable original suite identities or crosswalk")
    reference = phase_one.get("actual_supplemental_two_reference")
    require(type(reference) is dict and reference.get("status") == "PASS"
            and reference.get("actual_reference_worker_count") == 2
            and reference.get("case_count_per_worker") == [FUZZ_CASES, FUZZ_CASES],
            "reject invented or recounted historical differential references")
    require(type(fuzz) is dict and fuzz.get("status") == "PASS"
            and fuzz.get("actual_reference_worker_count") == 2
            and fuzz.get("supplemental_case_count") == FUZZ_CASES
            and fuzz.get("original_case_execution_denominator") == ORIGINAL_CASES,
            "reject altered independent 8,244-case reference evidence")
    workers = fuzz.get("workers")
    require(type(workers) is list and len(workers) == 2
            and all(type(row) is dict and row.get("case_count") == FUZZ_CASES
                    and row.get("passed") == FUZZ_CASES
                    and row.get("failed") == 0 and row.get("exit_code") == 0
                    and row.get("module") == "re" for row in workers)
            and all(type(row.get("pid")) is int and row["pid"] > 0
                    for row in workers)
            and workers[0]["pid"] != workers[1]["pid"],
            "reject reused, incomplete, or non-independent prior fuzz workers")
    require(type(signature) is dict and signature.get("status") == "PASS"
            and signature.get("publication_status") == "PASS"
            and signature.get("reference_status") == "PASS"
            and signature.get("additional_case_count") == SIGNATURE_CASES
            and signature.get("original_case_denominator") == ORIGINAL_CASES,
            "reject altered independently counted callable-signature references")
    contracts = phase_one.get("supplemental_public_contracts")
    require(type(contracts) is dict and type(contracts.get("callable_introspection"))
            is dict and contracts["callable_introspection"].get("case_count")
            == SIGNATURE_CASES and contracts["callable_introspection"].get(
                "two_reference_status") == "PASS",
            "reject the independently authenticated original 50-case supplement")
    gate = phase_one.get("candidate_qualification_gate")
    require(type(gate) is dict and gate.get("status") == "BLOCKED"
            and gate.get("qualified_candidate_count") == 0,
            "a frozen source supplement cannot qualify any replacement")


def walk_source_nodes(root: ast.AST):
    """Walk frozen source without ast.walk's lazy collections import."""
    pending = [root]
    while pending:
        node = pending.pop()
        yield node
        children = list(ast.iter_child_nodes(node))
        pending.extend(reversed(children))


def validate_upstream_source(owners: dict[str, bytes]) -> dict[str, object]:
    source = owners["official_upstream_tests"]
    tree = ast.parse(source, filename=absolute_owner(
        "oracle/cpython-3.14.6/test_re.py"))
    classes = [node for node in tree.body
               if isinstance(node, ast.ClassDef) and node.name == "ReTests"]
    require(len(classes) == 1, "reject a substituted official ReTests class")
    methods = {node.name: node for node in classes[0].body
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    required = ("assertTypedEqual", "test_empty_array", "test_keep_buffer",
                "test_basic_re_sub", "test_bug_29444")
    require(all(name in methods for name in required),
            "reject missing official typed-array, live-buffer, or nested-type tests")
    arrays = methods["test_empty_array"]
    found = [node.value for node in walk_source_nodes(arrays)
             if isinstance(node, ast.Constant) and type(node.value) is str
             and node.value == UPSTREAM_EMPTY_TYPECODES]
    require(found == [UPSTREAM_EMPTY_TYPECODES],
            "preserve the exact existing bBhuwHiIlLfd empty-array source")
    standard = ast.parse(owners["pinned_stdlib_source"], filename=STDLIB_RE)
    scanner = [node for node in standard.body
               if isinstance(node, ast.ClassDef) and node.name == "Scanner"]
    require(len(scanner) == 1, "preserve the independently sourced public Scanner")
    scan = [node for node in scanner[0].body
            if isinstance(node, ast.FunctionDef) and node.name == "scan"]
    require(len(scan) == 1 and any(
        isinstance(node, ast.Return) and isinstance(node.value, ast.Tuple)
        and len(node.value.elts) == 2
        for node in walk_source_nodes(scan[0])
    ), "preserve public Scanner remainder separately from Pattern.scanner")
    escapes = [node for node in standard.body
               if isinstance(node, ast.FunctionDef) and node.name == "escape"]
    require(len(escapes) == 1,
            "retain the separately observable public re.escape source")
    return {
        "upstream_source_authentication": "PASS",
        "empty_array_upstream_typecodes": UPSTREAM_EMPTY_TYPECODES,
        "upstream_empty_arrays_are_not_claimed_as_novel": True,
        "typed_nested_result_assertion_present": True,
        "live_match_mutation_assertion_present": True,
        "public_scanner_is_distinct_from_pattern_scanner": True,
        "public_escape_has_a_separate_buffer_path": True,
        "upstream_regex_operations_executed": 0,
    }


def require_exact_contract(document: object, source_pin: str,
                           protocol_pin: str) -> dict[str, object]:
    require(type(document) is dict,
            "reject a missing or non-object canonical source contract")
    expected = contract_document(source_pin, protocol_pin)
    require(document == expected,
            "reject an incomplete, substituted, predicted, or reordered source contract")
    require(canonical_bytes(document) == canonical_bytes(expected),
            "reject noncanonical or incomplete source-contract observations")
    return expected


def copy_value(value: object) -> object:
    if type(value) is dict:
        return {name: copy_value(item) for name, item in value.items()}
    if type(value) is list:
        return [copy_value(item) for item in value]
    if type(value) is tuple:
        return tuple(copy_value(item) for item in value)
    return value


def validate_matrix_description(value: object) -> None:
    require(type(value) is dict and value == matrix_description(),
            "reject altered additive rows, axes, expected states, or case counts")


def audit_attempt(event: str, arguments: tuple[object, ...]) -> None:
    previous = _BLOCKED_AUDIT_EVENTS.get(event, 0)
    try:
        sys.audit(event, *arguments)
    except FreezeError:
        require(_BLOCKED_AUDIT_EVENTS.get(event, 0) == previous + 1,
                "prove exactly one blocked synthetic audit event: " + event)
        return
    raise FreezeError("a synthetic forbidden source-only audit event escaped: " + event)


def self_test(contract: dict[str, object], source_pin: str,
              protocol_pin: str, contract_pin: str) -> dict[str, object]:
    require(_AUDIT_INSTALLED, "require the installed physical source-only audit hook")
    clean_bootstrap()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, action: object) -> None:
        require(name not in accepted and name not in rejected,
                "reject a repeated source-only control identity")
        try:
            outcome = action()  # type: ignore[operator]
        except Exception as error:
            raise FreezeError("a positive source-only control failed: " + name
                              + ": " + type(error).__name__ + ": " + str(error)) from error
        require(outcome is not False, "reject a false positive source-only control: " + name)
        accepted.append(name)

    def reject(name: str, action: object) -> None:
        require(name not in accepted and name not in rejected,
                "reject a repeated hostile source-only control identity")
        try:
            action()  # type: ignore[operator]
        except (FreezeError, ValueError, TypeError, OverflowError,
                UnicodeError, RecursionError, SyntaxError):
            rejected.append(name)
            return
        raise FreezeError("a hostile buffer-carrier source control was accepted: " + name)

    accept("strict-json-real-object", lambda: decode_json(
        b'{"z":[true,false,null],"a":2}') == {"z": [True, False, None], "a": 2})
    accept("strict-json-canonical-order", lambda: canonical_text(
        {"z": 2, "a": [True, None]}) == '{"a":[true,null],"z":2}')
    accept("strict-json-paired-surrogate", lambda: decode_json(
        b'"\\ud83d\\ude00"') == "\U0001f600")
    accept("strict-json-real-negative-integer", lambda: decode_json(
        b"-2147483649") == -2147483649)
    accept("strict-json-real-fraction", lambda: decode_json(b"1.25e2") == 125.0)
    accept("actual-host-byteorder", lambda: sys.byteorder in ("little", "big"))
    accept("all-expected-answers-unrecorded", lambda: all(
        row["expected"] == EXPECTED_STATUS for row in case_matrix()))
    accept("actual-original-denominator-unchanged", lambda:
           contract["original_p0"]["case_execution_denominator"] == ORIGINAL_CASES)
    accept("matrix-unique-identities", lambda:
           contract["additive_matrix"]["case_ids_are_unique"] is True)
    accept("source-only-boundaries-exact", lambda:
           contract["source_only_boundaries"] == boundaries())
    accept("raw-endian-fixtures-exact", lambda:
           len(endian_layouts()) == len(ENDIAN_CARRIERS))
    accept("raw-endian-u16-distinct", lambda:
           endian_layouts()[0]["raw_bytes_hex"]
           != endian_layouts()[1]["raw_bytes_hex"])
    accept("raw-endian-i16-distinct", lambda:
           endian_layouts()[2]["raw_bytes_hex"]
           != endian_layouts()[3]["raw_bytes_hex"])
    accept("raw-endian-u32-distinct", lambda:
           endian_layouts()[4]["raw_bytes_hex"]
           != endian_layouts()[5]["raw_bytes_hex"])
    all_carriers = {row[0]: row for row in carriers()}
    for name, action in (
        ("compiled-window", lambda: subject_applicable("pattern.search", "window")),
        ("native-scanner-window", lambda:
         subject_applicable("pattern.scanner.window", "window")),
        ("anonymous-mapping-close", lambda: lifetime_applicable(
            all_carriers["mmap.anonymous.write.direct"], "pattern.match",
            "mapping-close-with-live-view")),
        ("native-array-resize", lambda: lifetime_applicable(
            all_carriers["array.native.H"], "pattern.search",
            "array-resize-with-live-view")),
        ("bytearray-resize", lambda: lifetime_applicable(
            all_carriers["control.bytearray.nonempty"], "pattern.search",
            "bytearray-resize-with-live-view")),
        ("real-view-release", lambda: lifetime_applicable(
            all_carriers["view.bytes.contiguous"], "pattern.match",
            "view-release-before-operation")),
        ("empty-template", lambda: replacement_applicable(
            all_carriers["control.bytes.empty"], "empty-replacement")),
        ("nonempty-template", lambda: replacement_applicable(
            all_carriers["control.bytes.nonempty"], "numeric-backreference")),
        ("empty-stepped-template", lambda: replacement_applicable(
            all_carriers["view.bytes.empty-step"], "empty-replacement")),
        ("writable-empty-stepped-template", lambda: replacement_applicable(
            all_carriers["view.bytearray.empty-step"], "empty-replacement")),
        ("wide-native-byte-offset", lambda: lifetime_applicable(
            all_carriers["array.native.H"], "pattern.match",
            "byte-offset-not-element-offset")),
        ("wide-typed-view-byte-offset", lambda: lifetime_applicable(
            all_carriers["view.array.native-H"], "pattern.match",
            "byte-offset-not-element-offset")),
        ("direct-owner-shorter-mutation", lambda: lifetime_applicable(
            all_carriers["control.bytearray.nonempty"], "pattern.match",
            "match-group-after-shorter-mutation")),
    ):
        accept("applicability/positive/" + name, action)
    for name, action in (
        ("module-window", lambda: subject_applicable("module.search", "window")),
        ("public-scanner-window", lambda:
         subject_applicable("public-scanner.scan", "window")),
        ("non-window-native-scanner-window", lambda:
         subject_applicable("pattern.scanner.window", "literal")),
        ("bytes-mapping-close", lambda: lifetime_applicable(
            all_carriers["control.bytes.nonempty"], "pattern.match",
            "mapping-close-with-live-view")),
        ("mapping-array-resize", lambda: lifetime_applicable(
            all_carriers["mmap.file.write.direct"], "pattern.search",
            "array-resize-with-live-view")),
        ("array-bytearray-resize", lambda: lifetime_applicable(
            all_carriers["array.native.H"], "pattern.match",
            "bytearray-resize-with-live-view")),
        ("bytes-view-release", lambda: lifetime_applicable(
            all_carriers["control.bytes.nonempty"], "pattern.match",
            "view-release-before-operation")),
        ("readonly-mutation", lambda: lifetime_applicable(
            all_carriers["view.bytes.contiguous"], "pattern.match",
            "match-group-after-same-length-mutation")),
        ("readonly-callback-mutation", lambda: lifetime_applicable(
            all_carriers["mmap.file.read.direct"], "module.sub.callback",
            "callback-same-length-mutation")),
        ("released-match-identity", lambda: lifetime_applicable(
            all_carriers["view.bytes.released"], "pattern.match",
            "match-string-identity")),
        ("closed-mapping-live-view", lambda: lifetime_applicable(
            all_carriers["mmap.file.closed"], "pattern.match",
            "mapping-close-with-live-view")),
        ("non-iterator-lifetime", lambda: lifetime_applicable(
            all_carriers["array.native.H"], "pattern.search",
            "iterator-live-export")),
        ("non-scanner-lifetime", lambda: lifetime_applicable(
            all_carriers["array.native.H"], "pattern.search",
            "scanner-live-export")),
        ("public-scanner-native-holder", lambda: lifetime_applicable(
            all_carriers["array.native.H"], "public-scanner.scan",
            "scanner-live-export")),
        ("non-callback-keyboard-interrupt", lambda: lifetime_applicable(
            all_carriers["array.native.H"], "pattern.match",
            "callback-keyboard-interrupt")),
        ("anonymous-file-close", lambda: lifetime_applicable(
            all_carriers["mmap.anonymous.write.direct"], "pattern.match",
            "file-backed-close-before-unlink")),
        ("compiled-scanner-public-remainder", lambda: lifetime_applicable(
            all_carriers["array.native.H"], "pattern.scanner.match",
            "public-scanner-remainder-slice-type")),
        ("plain-bytes-element-offset", lambda: lifetime_applicable(
            all_carriers["control.bytes.nonempty"], "pattern.match",
            "byte-offset-not-element-offset")),
        ("one-byte-array-element-offset", lambda: lifetime_applicable(
            all_carriers["array.native.B"], "pattern.match",
            "byte-offset-not-element-offset")),
        ("byte-format-view-element-offset", lambda: lifetime_applicable(
            all_carriers["view.cast.native-B"], "pattern.match",
            "byte-offset-not-element-offset")),
        ("template-no-match-identity", lambda: lifetime_applicable(
            all_carriers["array.native.H"], "module.sub.template",
            "match-string-identity")),
        ("public-scan-no-match-identity", lambda: lifetime_applicable(
            all_carriers["array.native.H"], "public-scanner.scan",
            "match-string-identity")),
        ("nonempty-empty-replacement", lambda: replacement_applicable(
            all_carriers["control.bytes.nonempty"], "empty-replacement")),
        ("empty-numeric-replacement", lambda: replacement_applicable(
            all_carriers["control.bytes.empty"], "numeric-backreference")),
        ("empty-step-numeric-replacement", lambda: replacement_applicable(
            all_carriers["view.bytes.empty-step"], "numeric-backreference")),
        ("empty-step-named-replacement", lambda: replacement_applicable(
            all_carriers["view.bytearray.empty-step"], "named-backreference")),
        ("view-shorter-match-mutation", lambda: lifetime_applicable(
            all_carriers["view.bytearray.contiguous"], "pattern.match",
            "match-group-after-shorter-mutation")),
    ):
        reject("applicability/reject/" + name,
               lambda check=action: require(check(),
                                             "physically inapplicable additive row"))
    attacks = (
        ("duplicate-key", b'{"x":1,"x":2}'),
        ("nested-duplicate", b'{"x":{"y":1,"y":2}}'),
        ("trailing-document", b'{"x":1}{"y":2}'),
        ("object-trailing-comma", b'{"x":1,}'),
        ("array-trailing-comma", b"[1,]"),
        ("leading-zero", b"01"),
        ("negative-leading-zero", b"-01"),
        ("incomplete-fraction", b"1."),
        ("incomplete-exponent", b"1e"),
        ("infinite-exponent", b"1e9999"),
        ("positive-sign", b"+1"),
        ("nan", b"NaN"),
        ("infinity", b"Infinity"),
        ("unquoted-key", b"{x:1}"),
        ("unclosed-array", b"[1"),
        ("unclosed-object", b'{"x":1'),
        ("unclosed-string", b'"x'),
        ("invalid-escape", b'"\\x"'),
        ("short-unicode", b'"\\u12"'),
        ("invalid-unicode", b'"\\ugg00"'),
        ("unpaired-high", b'"\\ud800"'),
        ("unpaired-low", b'"\\udc00"'),
        ("incorrect-surrogate", b'"\\ud800\\u0041"'),
        ("literal-control", b'"x\n"'),
        ("invalid-utf8", b'"\xff"'),
        ("empty", b""),
        ("overlong-number", b"1" * 129),
        ("overdeep", b"[" * (MAX_JSON_DEPTH + 2) + b"0"
         + b"]" * (MAX_JSON_DEPTH + 2)),
    )
    for name, raw in attacks:
        reject("json/" + name, lambda data=raw: decode_json(data))
    reject("json/non-string-key", lambda: canonical_text({1: "forbidden"}))
    reject("json/nan-encoder", lambda: canonical_text(float("nan")))
    reject("json/infinity-encoder", lambda: canonical_text(float("inf")))

    for index, key in enumerate(sorted(contract)):
        def remove_top(name: str = key) -> None:
            hostile = copy_value(contract)
            del hostile[name]
            require_exact_contract(hostile, source_pin, protocol_pin)
        reject("contract/remove/" + str(index) + "/" + key, remove_top)

    original = contract["original_p0"]
    require(type(original) is dict, "require the exact original-denominator section")
    for index, key in enumerate(sorted(original)):
        def corrupt_original(name: str = key) -> None:
            hostile = copy_value(contract)
            target = hostile["original_p0"]
            old = target[name]
            if type(old) is bool:
                target[name] = not old
            elif type(old) is int:
                target[name] = old + 1
            else:
                target[name] = "altered-original-owner"
            require_exact_contract(hostile, source_pin, protocol_pin)
        reject("original/corrupt/" + str(index) + "/" + key, corrupt_original)

    matrix = contract["additive_matrix"]
    require(type(matrix) is dict, "require the exact additive case matrix")
    for index, key in enumerate(sorted(matrix)):
        def corrupt_matrix(name: str = key) -> None:
            hostile = copy_value(contract)
            section = hostile["additive_matrix"]
            old = section[name]
            if type(old) is bool:
                section[name] = not old
            elif type(old) is int:
                section[name] = old + 1
            elif type(old) is str:
                section[name] = "altered-additive-matrix"
            elif type(old) is list:
                section[name] = old[:-1]
            elif type(old) is dict:
                section[name] = {}
            else:
                section[name] = None
            require_exact_contract(hostile, source_pin, protocol_pin)
        reject("matrix/corrupt/" + str(index) + "/" + key, corrupt_matrix)

    rows = case_matrix()
    frozen_identities = frozenset(row["case_id"] for row in rows)
    for name, identity in (
        ("valid-compiled-window", matrix_row(
            "subject", all_carriers["array.native.H"], "pattern.search",
            "window", "subject")["case_id"]),
        ("valid-native-scanner-window", matrix_row(
            "subject", all_carriers["array.native.H"], "pattern.scanner.window",
            "window", "subject")["case_id"]),
        ("valid-array-byte-offset", matrix_row(
            "owner-lifetime", all_carriers["array.native.H"], "pattern.match",
            "byte-offset-not-element-offset", "subject-and-exporter")["case_id"]),
        ("valid-empty-template", matrix_row(
            "replacement-carrier", all_carriers["control.bytes.empty"],
            "module.sub.template", "empty-replacement", "replacement")["case_id"]),
        ("valid-empty-stepped-template", matrix_row(
            "replacement-carrier", all_carriers["view.bytes.empty-step"],
            "module.sub.template", "empty-replacement", "replacement")["case_id"]),
    ):
        accept("frozen-graph/present/" + name,
               lambda case=identity: case in frozen_identities)
    for name, identity in (
        ("module-window", matrix_row(
            "subject", all_carriers["array.native.H"], "module.search",
            "window", "subject")["case_id"]),
        ("public-scanner-window", matrix_row(
            "subject", all_carriers["array.native.H"], "public-scanner.scan",
            "window", "subject")["case_id"]),
        ("bytes-mapping-close", matrix_row(
            "owner-lifetime", all_carriers["control.bytes.nonempty"],
            "pattern.match", "mapping-close-with-live-view",
            "subject-and-exporter")["case_id"]),
        ("readonly-match-mutation", matrix_row(
            "owner-lifetime", all_carriers["view.bytes.contiguous"],
            "pattern.match", "match-group-after-same-length-mutation",
            "subject-and-exporter")["case_id"]),
        ("released-match-identity", matrix_row(
            "owner-lifetime", all_carriers["view.bytes.released"],
            "pattern.match", "match-string-identity",
            "subject-and-exporter")["case_id"]),
        ("plain-byte-element-offset", matrix_row(
            "owner-lifetime", all_carriers["control.bytes.nonempty"],
            "pattern.match", "byte-offset-not-element-offset",
            "subject-and-exporter")["case_id"]),
        ("public-retained-native-scanner", matrix_row(
            "owner-lifetime", all_carriers["array.native.H"],
            "public-scanner.scan", "scanner-live-export",
            "subject-and-exporter")["case_id"]),
        ("nonempty-empty-replacement", matrix_row(
            "replacement-carrier", all_carriers["control.bytes.nonempty"],
            "module.sub.template", "empty-replacement", "replacement")["case_id"]),
        ("empty-step-numeric-replacement", matrix_row(
            "replacement-carrier", all_carriers["view.bytes.empty-step"],
            "module.sub.template", "numeric-backreference", "replacement")["case_id"]),
        ("view-shorter-match-mutation", matrix_row(
            "owner-lifetime", all_carriers["view.bytearray.contiguous"],
            "pattern.match", "match-group-after-shorter-mutation",
            "subject-and-exporter")["case_id"]),
    ):
        reject("frozen-graph/absent/" + name,
               lambda case=identity: require(
                   case in frozen_identities, "inapplicable case absent from frozen graph"))
    carrier_rows = carriers()
    for number, carrier in enumerate(carrier_rows):
        def corrupt_carrier(index: int = number) -> None:
            hostile = copy_value(contract)
            hostile["additive_matrix"]["carriers"][index]["carrier_id"] += ".hidden"
            require_exact_contract(hostile, source_pin, protocol_pin)
        reject("carrier/rename/" + str(number) + "/" + carrier[0], corrupt_carrier)
        def predict_carrier(index: int = number) -> None:
            hostile = copy_value(contract)
            hostile["additive_matrix"]["carriers"][index]["reference_outcome"] = "PASS"
            require_exact_contract(hostile, source_pin, protocol_pin)
        reject("carrier/predict/" + str(number) + "/" + carrier[0], predict_carrier)
    sampled = tuple(sorted(set([0, 1, len(rows) // 4, len(rows) // 2,
                                 (3 * len(rows)) // 4, len(rows) - 2,
                                 len(rows) - 1] + [
                                     (len(rows) * index) // 64 for index in range(64)
                                 ])))
    for number in sampled:
        def mutate_row(index: int = number) -> None:
            row = copy_value(rows[index])
            row["expected"] = "PASS"
            require(row == rows[index],
                    "reject a fabricated future official CPython observation")
        reject("case/predicted-answer/" + str(number), mutate_row)
        def rename_row(index: int = number) -> None:
            row = copy_value(rows[index])
            row["case_id"] += "/replacement"
            require(row == rows[index], "reject a renamed frozen additive row")
        reject("case/renamed/" + str(number), rename_row)

    boundary = contract["source_only_boundaries"]
    require(type(boundary) is dict, "require all exact source-only boundaries")
    for index, key in enumerate(sorted(boundary)):
        def corrupt_boundary(name: str = key) -> None:
            hostile = copy_value(contract)
            section = hostile["source_only_boundaries"]
            old = section[name]
            if type(old) is bool:
                section[name] = not old
            elif type(old) is int:
                section[name] = old + 1
            else:
                section[name] = "PASS"
            require_exact_contract(hostile, source_pin, protocol_pin)
        reject("boundary/corrupt/" + str(index) + "/" + key, corrupt_boundary)

    for name in ("re", "_sre", "rebar", "candidates", "candidates.zig_candidate",
                 "candidates.rust_candidate", "candidates.c_candidate", "array",
                 "mmap", "json", "pathlib", "ctypes", "subprocess", "socket",
                 "threading", "gzip", "zlib", "regex", "_regex", "pcre2", "re2",
                 "google_re2", "rure", "pcre", "onig", "oniguruma",
                 "hyperscan", "vectorscan", "rust_regex", "fancy_regex"):
        reject("call/import/" + name, lambda module=name: builtins.__import__(module))
        before = _BLOCKED_AUDIT_EVENTS.get("import", 0)
        reject("alias/import/" + name,
               lambda module=name: _CAPTURED_BUILTIN_IMPORT(module))
        require(_BLOCKED_AUDIT_EVENTS.get("import", 0) == before + 1,
                "prove a captured import alias was physically blocked")

    for name, path, access in (
        ("foreign-owner", ROOT + "/unlisted-buffer-carrier-source.json", "rb"),
        ("candidate", ROOT + "/candidates/zig_candidate.py", "rb"),
        ("holdout", ROOT + "/performance/holdout/cases.json.gz", "rb"),
        ("matching-archive", ROOT + "/oracle/phase2/evidence/matching.json.gz", "rb"),
        ("outside-project", "/etc/passwd", "rb"),
        ("allowed-owner-via-buffered-open", ROOT + "/GOAL.md", "rb"),
        ("workspace-write", ROOT + "/GOAL.md", "wb"),
    ):
        reject("call/file/" + name,
               lambda location=path, mode=access: builtins.open(location, mode))
        if _CAPTURED_IO_OPEN is not None:
            previous = _BLOCKED_AUDIT_EVENTS.get("open", 0)
            reject("alias/_io.open/" + name,
                   lambda location=path, mode=access:
                   _CAPTURED_IO_OPEN(location, mode))
            require(_BLOCKED_AUDIT_EVENTS.get("open", 0) == previous + 1,
                    "prove a captured direct _io.open alias was physically blocked")

    forbidden_flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    for name, opener, location, flags in (
        ("captured-os-open-holdout", _CAPTURED_OS_OPEN,
         ROOT + "/performance/holdout/cases.json.gz", os.O_RDONLY),
        ("captured-os-open-write", _CAPTURED_OS_OPEN,
         ROOT + "/GOAL.md", forbidden_flags),
        ("captured-os-open-relative", _CAPTURED_OS_OPEN, "GOAL.md", os.O_RDONLY),
        ("captured-os-open-symlink-flags", _CAPTURED_OS_OPEN,
         ROOT + "/GOAL.md", os.O_RDONLY),
    ):
        previous = _BLOCKED_AUDIT_EVENTS.get("open", 0)
        reject("alias/" + name,
               lambda action=opener, path=location, mode=flags: action(path, mode))
        require(_BLOCKED_AUDIT_EVENTS.get("open", 0) == previous + 1,
                "prove the actual descriptor-open alias was blocked")
    if _CAPTURED_POSIX_OPEN is not None:
        previous = _BLOCKED_AUDIT_EVENTS.get("open", 0)
        reject("alias/posix.open/holdout", lambda:
               _CAPTURED_POSIX_OPEN(ROOT + "/performance/holdout/cases.json.gz",
                                    os.O_RDONLY))
        require(_BLOCKED_AUDIT_EVENTS.get("open", 0) == previous + 1,
                "prove the captured direct posix.open alias was blocked")

    for name, event, arguments in (
        ("mmap-anonymous-construction", "mmap.__new__", (-1, 16, 0, 0)),
        ("mmap-file-construction", "mmap.__new__", (99, 16, 0, 0)),
        ("array-construction", "array.__new__", ("H",)),
        ("native-load", "ctypes.dlopen", ("forbidden-buffer-engine.so",)),
        ("native-symbol", "ctypes.dlsym", ("forbidden", "match")),
        ("process-popen", "subprocess.Popen", ("forbidden", [], None, None)),
        ("process-fork", "os.fork", ()),
        ("process-spawn", "os.posix_spawn", ("/bin/sh", [], {})),
        ("network-create", "socket.__new__", (None, 2, 1, 0)),
        ("network-connect", "socket.connect", (None, ("127.0.0.1", 1))),
        ("thread-start", "threading.start", ()),
        ("clock-time", "time.time", ()),
        ("clock-monotonic", "time.monotonic", ()),
        ("archive-gzip", "gzip.open", ("forbidden.json.gz",)),
        ("archive-zlib", "zlib.decompress", (b"forbidden",)),
        ("garbage-collection", "gc.collect", ()),
        ("code-execution", "exec", ("forbidden",)),
        ("marshaled-code", "marshal.loads", (b"forbidden",)),
        ("environment-mutation", "os.putenv", (b"FORBIDDEN", b"1")),
        ("workspace-mutation", "os.remove", (ROOT + "/GOAL.md", -1)),
        ("audit-hook-replacement", "sys.addaudithook", (None,)),
    ):
        accept("synthetic-audit/" + name,
               lambda label=event, args=arguments: audit_attempt(label, args))

    for name, action in (
        ("memoryview-construction", lambda: builtins.memoryview(b"forbidden")),
        ("bytearray-construction", lambda: builtins.bytearray(b"forbidden")),
        ("directory-list", lambda: os.listdir(ROOT)),
        ("directory-scan", lambda: os.scandir(ROOT)),
        ("workspace-mkdir", lambda: os.mkdir(ROOT + "/forbidden-buffer-freeze")),
        ("workspace-remove", lambda: os.remove(ROOT + "/GOAL.md")),
        ("workspace-write", lambda: os.write(1, b"forbidden")),
        ("entropy", lambda: os.urandom(1)),
    ):
        reject("physical-call/" + name, action)

    require(len(accepted) >= 10 and len(rejected) >= 300,
            "exercise at least 300 unique hostile source-only controls")
    require(len(set(accepted + rejected)) == len(accepted) + len(rejected),
            "count only actually executed, uniquely named controls")
    require(_BLOCKED_AUDIT_EVENTS.get("open", 0) > 0
            and _BLOCKED_AUDIT_EVENTS.get("import", 0) > 0
            and _BLOCKED_AUDIT_EVENTS.get("mmap.__new__", 0) == 2
            and _BLOCKED_AUDIT_EVENTS.get("ctypes.dlopen", 0) == 1
            and _BLOCKED_AUDIT_EVENTS.get("gzip.open", 0) == 1
            and _BLOCKED_AUDIT_EVENTS.get("time.time", 0) == 1,
            "prove the physical aliases and labeled synthetic effects were denied")
    require(_BLOCKED_CALLS.get("buffer", 0) == 2
            and _BLOCKED_CALLS.get("filesystem", 0) > 0
            and _BLOCKED_CALLS.get("write", 0) > 0,
            "prove real carrier, filesystem, and write call attempts were denied")
    clean_bootstrap()
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 1,
        "status": "PASS",
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_control_count": len(accepted),
        "rejected_hostile_control_count": len(rejected),
        "unique_control_count": len(accepted) + len(rejected),
        "blocked_real_callable_attempts_by_kind": dict(sorted(_BLOCKED_CALLS.items())),
        "blocked_synthetic_or_alias_audit_attempts_by_event":
        dict(sorted(_BLOCKED_AUDIT_EVENTS.items())),
        "blocked_synthetic_audit_events_are_actual_operations": False,
        "physical_audit_hook_installed": _AUDIT_INSTALLED,
        "original_case_execution_denominator": ORIGINAL_CASES,
        "original_suite_count": ORIGINAL_SUITES,
        "original_obligation_count": ORIGINAL_OBLIGATIONS,
        "original_crosswalk_count": ORIGINAL_CROSSWALK,
        "original_named_private_waiver_count": ORIGINAL_PRIVATE_WAIVERS,
        "existing_fuzz_case_count": FUZZ_CASES,
        "existing_signature_case_count": SIGNATURE_CASES,
        "additive_case_count": matrix["case_count"],
        "additive_matrix_sha256":
        matrix["canonical_newline_delimited_matrix_sha256"],
        "expected_records": EXPECTED_STATUS,
        "source_only_boundaries": boundaries(),
    }


def verify_context(contract: dict[str, object], owners: dict[str, bytes],
                   source_pin: str, protocol_pin: str,
                   contract_pin: str) -> dict[str, object]:
    validate_original_context(owners)
    upstream = validate_upstream_source(owners)
    exact = require_exact_contract(contract, source_pin, protocol_pin)
    require(digest(canonical_bytes(exact)) == contract_pin,
            "reject a substituted canonical additive source contract")
    clean_bootstrap()
    matrix = exact["additive_matrix"]
    return {
        "schema": SCHEMA + "-verified-frozen-context",
        "version": 1,
        "status": "PASS",
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "authenticated_immutable_source_owner_count": len(OWNERS),
        "original_case_execution_denominator": ORIGINAL_CASES,
        "original_suite_count": ORIGINAL_SUITES,
        "original_obligation_count": ORIGINAL_OBLIGATIONS,
        "original_crosswalk_count": ORIGINAL_CROSSWALK,
        "original_named_private_waiver_count": ORIGINAL_PRIVATE_WAIVERS,
        "existing_fuzz_case_count": FUZZ_CASES,
        "existing_fuzz_independent_reference_count": 2,
        "existing_signature_case_count": SIGNATURE_CASES,
        "existing_signature_independent_reference_count": 2,
        "additive_case_count": matrix["case_count"],
        "additive_carrier_count": matrix["carrier_count"],
        "additive_cohort_case_counts": matrix["cohort_case_counts"],
        "additive_matrix_sha256":
        matrix["canonical_newline_delimited_matrix_sha256"],
        "expected_records": EXPECTED_STATUS,
        "upstream_source_observations": upstream,
        "physical_audit_hook_installed": _AUDIT_INSTALLED,
        "blocked_real_callable_attempts_by_kind": dict(sorted(_BLOCKED_CALLS.items())),
        "blocked_synthetic_or_alias_audit_attempts_by_event":
        dict(sorted(_BLOCKED_AUDIT_EVENTS.items())),
        "source_only_boundaries": boundaries(),
    }


def parse_arguments(argv: list[str]) -> tuple[str, dict[str, str]]:
    choices = ("--self-test", "--verify-frozen-context", "--render-contract")
    options = {"--source-sha256": "source", "--protocol-sha256": "protocol",
               "--contract-sha256": "contract"}
    mode = ""
    result: dict[str, str] = {}
    position = 0
    while position < len(argv):
        value = argv[position]
        if value in choices:
            require(not mode, "require exactly one source-only freeze mode")
            mode = value
            position += 1
            continue
        require(value in options and position + 1 < len(argv),
                "reject an unknown freeze option or missing independent SHA-256")
        key = options[value]
        require(key not in result, "reject a duplicate independent owner pin")
        result[key] = checked_digest(argv[position + 1], key)
        position += 2
    require(mode in choices, "require one explicitly authorized source-only mode")
    expected = {"source", "protocol"} if mode == "--render-contract" else {
        "source", "protocol", "contract"
    }
    require(set(result) == expected,
            "require exactly the independent source-only pins for the chosen mode")
    return mode, result


def main(argv: list[str]) -> int:
    clean_bootstrap()
    install_wall()
    mode, pins = parse_arguments(argv)
    read_dynamic_owner(SOURCE, pins["source"])
    read_dynamic_owner(PROTOCOL, pins["protocol"])
    owners = authenticate_owners()
    validate_original_context(owners)
    validate_upstream_source(owners)
    if mode == "--render-contract":
        result = contract_document(pins["source"], pins["protocol"])
    else:
        raw = read_dynamic_owner(CONTRACT, pins["contract"])
        require(digest(raw) == pins["contract"],
                "reject the complete canonical contract owner")
        contract = require_exact_contract(decode_json(raw), pins["source"],
                                          pins["protocol"])
        require(raw == canonical_bytes(contract),
                "reject noncanonical frozen contract bytes")
        result = (self_test(contract, pins["source"], pins["protocol"],
                            pins["contract"]) if mode == "--self-test"
                  else verify_context(contract, owners, pins["source"],
                                      pins["protocol"], pins["contract"]))
    clean_bootstrap()
    sys.stdout.write(canonical_text(result) + "\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (FreezeError, OSError, UnicodeError, ValueError, TypeError,
            OverflowError, SyntaxError, RecursionError) as error:
        try:
            sys.stderr.write("public buffer-carrier source freeze failed closed: "
                             + type(error).__name__ + ": " + str(error) + "\n")
            sys.stderr.flush()
        except Exception:
            pass
        raise SystemExit(2)
