#!/usr/bin/env python3
"""Render an honest, receipt-pinned overview of two actual Python references."""

from __future__ import annotations

import sys


_BOOT_MODULES = frozenset(sys.modules)
_FORBIDDEN_MODULES = (
    "re", "_sre", "array", "mmap", "rebar", "candidates", "regex",
    "_regex", "re2", "google_re2", "rure", "pcre", "pcre2", "onig",
    "oniguruma", "hyperscan", "vectorscan", "rust_regex", "fancy_regex",
    "gzip", "zlib", "subprocess", "socket", "ctypes", "json",
)
if any(name == root or name.startswith(root + ".")
       for name in _BOOT_MODULES for root in _FORBIDDEN_MODULES):
    raise SystemExit("reference chart requires a clean, engine-free bootstrap")

import builtins
import hashlib
import os
import stat


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/render_public_buffer_carriers_reference_overview_v1.py"
RECEIPT = (
    "oracle/phase1/evidence/"
    "public-buffer-carriers-reference-v1-cpython-3.14.6-publication-receipt.json"
)
REFERENCE_CONTRACT = "oracle/phase1/p0-public-buffer-carriers-reference-v1.json"
SUPPLEMENT_CONTRACT = "oracle/phase1/p0-public-buffer-carriers-supplement-v1.json"
OUTPUT_DIRECTORY = "docs/evidence"
OUTPUT_BASENAME = "public-buffer-carriers-reference-overview-v1"
SCHEMA = "rebar-public-buffer-carriers-reference-overview-v1"
RECEIPT_SHA256 = (
    "946daf4c428a2e37a42e1c351a161095a0aa85ab64a69fae012f4ddeddd741b6"
)
REFERENCE_CONTRACT_SHA256 = (
    "857a330b26f1441d7f16b3adbd28f11fa63021b8b671451b2c0ddc3ca96230a3"
)
MATRIX_SHA256 = (
    "4de04250c99a87d188bf1f8386ad80044ae86d136908ea7aa1bc86e8b7c32ab1"
)
RECORDS_SHA256 = (
    "c5730292aae072aa24ea2a155ae33cc18e0d6d93205f0797ab4ddc8fe0195e26"
)
ARCHIVE_SHA256 = (
    "f0d32fae77ff8c2cd82561fbe876aa4cb7deeafc14427622563430ef34f93452"
)
ORIGINAL_CASES = 31_237
ORIGINAL_SUITES = 13
ORIGINAL_OBLIGATIONS = 73
ORIGINAL_CROSSWALK = 34
ORIGINAL_PRIVATE_WAIVERS = 13
ADDITIVE_CASES = 48_416
CARRIERS = 86
WORKER_PIDS = (81, 82)
MAX_DOCUMENT_BYTES = 4 * 1024 * 1024
MAX_OWNER_BYTES = 40 * 1024 * 1024
MAX_JSON_DEPTH = 40
COHORTS = (
    ("subject", "Search inputs", 28_294),
    ("pattern-carrier", "Pattern inputs", 3_870),
    ("replacement-carrier", "Replacement inputs", 3_184),
    ("escape-carrier", "Escaping inputs", 344),
    ("owner-lifetime", "Buffer lifetime", 12_724),
)
OUTPUT_NAMES = (
    OUTPUT_BASENAME + ".inputs.json",
    OUTPUT_BASENAME + ".summary.json",
    OUTPUT_BASENAME + ".svg",
)

# Every source-only read is independently bounded to an exact, single-link
# immutable owner. In particular, no compressed archive is an allowed owner.
OWNERS = (
    ("goal", "GOAL.md",
     "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
     3_756, 2064, 31364044, 0o600, 1),
    ("original_p0_contract", "oracle/phase1/p0-completeness-v1.json",
     "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
     45_632, 2064, 524385, 0o600, 1),
    ("current_p0_contract", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
     34_875, 2064, 524713, 0o600, 1),
    ("supplement_source",
     "tools/verify_owned_public_buffer_carriers_supplement_v1.py",
     "ac3ffc76fb0ea8af97715ddc6bd55833dcb0d7e85231b0d9ef37eb7bb46c0d15",
     94_823, 2064, 431102, 0o600, 1),
    ("supplement_protocol",
     "oracle/phase1/P0-PUBLIC-BUFFER-CARRIERS-SUPPLEMENT-V1.md",
     "da5854c7f9befc54076a8032d0723baf60f53e446f1cb15724bb2d37c71a790d",
     9_082, 2064, 525381, 0o600, 1),
    ("supplement_contract", SUPPLEMENT_CONTRACT,
     "0086959c29967beb40d1b153a52aafffeb3eacbda98d5c7cf40a3b9890cb9db2",
     39_733, 2064, 525385, 0o600, 1),
    ("reference_source",
     "tools/run_owned_public_buffer_carriers_reference_v1.py",
     "e82e93fbc9c7474f17ca4d2fc5eb7682ccb997651d4ad21c334d1e0cab1da3ee",
     201_975, 2064, 431189, 0o600, 1),
    ("reference_protocol",
     "oracle/phase1/P0-PUBLIC-BUFFER-CARRIERS-REFERENCE-V1.md",
     "981015c163a4c428b74b8f545f3f8fc111ea56b399fd2df0d811d82f4293306d",
     9_351, 2064, 525486, 0o600, 1),
    ("reference_contract", REFERENCE_CONTRACT, REFERENCE_CONTRACT_SHA256,
     42_775, 2064, 525491, 0o600, 1),
    ("actual_publication_receipt", RECEIPT, RECEIPT_SHA256,
     1_644, 2064, 525592, 0o600, 1),
    ("pinned_cpython", PYTHON,
     "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
     32_387_816, 2049, 9594007, 0o711, 1),
)


class FreezeError(Exception):
    """A reference chart owner, receipt, prediction, or boundary is not exact."""


_AUDIT_INSTALLED = False
_BLOCKED_AUDIT_EVENTS: dict[str, int] = {}
_BLOCKED_CALLS: dict[str, int] = {}
_CALL_GUARDS: list[tuple[object, str, object]] = []
_CAPTURED_OS_OPEN = os.open
_CAPTURED_OS_STAT = os.stat
_CAPTURED_BUILTIN_IMPORT = builtins.__import__
_CAPTURED_IO_OPEN = getattr(sys.modules.get("_io"), "open", None)
_CAPTURED_POSIX_OPEN = getattr(sys.modules.get("posix"), "open", None)


def require(condition: object, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete, exact bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value)
            and len(set(value)) > 1,
            "require an independent lowercase SHA-256 for " + label)
    return value


def clean_bootstrap() -> None:
    require(tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PYTHON
            and sys.flags.isolated == 1
            and sys.flags.no_site == 1
            and sys.dont_write_bytecode,
            "use the exact stable CPython 3.14.6 with -I -B -S")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in _FORBIDDEN_MODULES),
            "never import a regex engine, candidate, archive, process, or network")


def absolute_owner(path: str) -> str:
    require(type(path) is str and path and "\x00" not in path,
            "reject an empty or embedded-NUL owner")
    if path == PYTHON:
        return path
    require(not path.startswith("/")
            and all(part not in ("", ".", "..") for part in path.split("/")),
            "reject an absolute, ambiguous, or escaped source owner")
    return ROOT + "/" + path


def allowed_paths() -> frozenset[str]:
    return frozenset([absolute_owner(SOURCE)]
                     + [absolute_owner(item[1]) for item in OWNERS])


def blocked_audit(event: str, detail: str) -> None:
    _BLOCKED_AUDIT_EVENTS[event] = _BLOCKED_AUDIT_EVENTS.get(event, 0) + 1
    raise FreezeError("deny-default chart audit blocked " + event + ": " + detail)


def source_audit_hook(event: str, arguments: tuple[object, ...]) -> None:
    if event == "open":
        path = arguments[0] if arguments else None
        flags = arguments[2] if len(arguments) > 2 else None
        if type(path) is not str or path not in allowed_paths():
            blocked_audit(event, "read is outside the immutable owner allowlist")
        if type(flags) is not int:
            blocked_audit(event, "read-only descriptor flags are required")
        forbidden = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                     | os.O_APPEND | getattr(os, "O_TMPFILE", 0))
        if (flags & forbidden
                or flags & getattr(os, "O_NOFOLLOW", 0)
                != getattr(os, "O_NOFOLLOW", 0)
                or flags & getattr(os, "O_CLOEXEC", 0)
                != getattr(os, "O_CLOEXEC", 0)):
            blocked_audit(event, "reject writes, symlinks, and inherited descriptors")
        return
    blocked_audit(event, "every non-owner audit event is forbidden")


def blocked_call(kind: str, name: str) -> None:
    _BLOCKED_CALLS[kind] = _BLOCKED_CALLS.get(kind, 0) + 1
    raise FreezeError("physical chart guard blocked " + kind + ": " + name)


def guard_call(owner: object, name: str, kind: str) -> None:
    original = getattr(owner, name, None)
    if original is None:
        return

    def denied(*_arguments: object, **_keywords: object) -> object:
        blocked_call(kind, name)
        raise AssertionError("unreachable denied chart operation")

    _CALL_GUARDS.append((owner, name, original))
    setattr(owner, name, denied)


def install_wall() -> None:
    global _AUDIT_INSTALLED
    clean_bootstrap()
    require(not _AUDIT_INSTALLED and not _CALL_GUARDS,
            "install exactly one deny-default chart source audit")
    sys.addaudithook(source_audit_hook)
    _AUDIT_INSTALLED = True
    for name in ("__import__", "open", "memoryview", "bytearray", "input"):
        guard_call(builtins, name,
                   "import" if name == "__import__"
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
    guarded_modules = (
        ("_io", ("open",), "filesystem"),
        ("posix", ("scandir", "listdir", "walk", "readlink"), "filesystem"),
        ("posix", ("write", "mkdir", "unlink", "remove", "rename", "replace",
                   "rmdir", "symlink", "link", "chmod", "chown", "truncate",
                   "utime", "putenv", "unsetenv", "urandom", "fsync"), "write"),
        ("posix", ("fork", "forkpty", "system", "posix_spawn", "posix_spawnp",
                   "execv", "execve"), "process"),
        ("_posixsubprocess", ("fork_exec",), "process"),
        ("_ctypes", ("dlopen",), "native"),
        ("_imp", ("create_dynamic", "exec_dynamic", "create_builtin",
                  "exec_builtin", "init_frozen"), "native"),
        ("_socket", ("socket", "getaddrinfo"), "network"),
        ("_thread", ("start_new_thread", "start_joinable_thread"), "thread"),
    )
    for module_name, names, kind in guarded_modules:
        module = sys.modules.get(module_name)
        if module is not None:
            for name in names:
                guard_call(module, name, kind)
    clean_bootstrap()


def quoted(value: str) -> str:
    require(type(value) is str, "quote only exact JSON strings")
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
    require(depth <= MAX_JSON_DEPTH, "reject overdeep canonical JSON")
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
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical_text(item, depth + 1)
                               for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value),
                "reject non-string canonical JSON keys")
        return "{" + ",".join(
            quoted(key) + ":" + canonical_text(value[key], depth + 1)
            for key in sorted(value)
        ) + "}"
    raise FreezeError("reject noncanonical chart JSON: " + type(value).__name__)


def canonical_bytes(value: object) -> bytes:
    result = canonical_text(value).encode("ascii") + b"\n"
    require(0 < len(result) <= MAX_DOCUMENT_BYTES,
            "reject an empty or oversized chart document")
    return result


class StrictJSON:
    """Decode exact bounded JSON without importing json, re, or native code."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and 0 < len(raw) <= MAX_DOCUMENT_BYTES,
                "reject an unbounded or empty chart JSON owner")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise FreezeError("reject invalid owner UTF-8") from error
        self.index = 0

    def whitespace(self) -> None:
        while (self.index < len(self.text)
               and self.text[self.index] in " \t\r\n"):
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"',
                "require a quoted JSON string")
        self.index += 1
        result: list[str] = []
        simple = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
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
            require(self.index < len(self.text),
                    "reject a truncated JSON escape")
            escape = self.text[self.index]
            self.index += 1
            if escape != "u":
                require(escape in simple, "reject an unknown JSON escape")
                result.append(simple[escape])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4 and all(
                part in "0123456789abcdefABCDEF" for part in digits
            ), "reject an invalid Unicode escape")
            self.index += 4
            codepoint = int(digits, 16)
            if 0xd800 <= codepoint <= 0xdbff:
                require(self.text[self.index:self.index + 2] == "\\u",
                        "reject an unpaired high surrogate")
                low = self.text[self.index + 2:self.index + 6]
                require(len(low) == 4 and all(
                    part in "0123456789abcdefABCDEF" for part in low
                ), "reject an invalid low surrogate")
                lower = int(low, 16)
                require(0xdc00 <= lower <= 0xdfff,
                        "reject a nonpairing low surrogate")
                self.index += 6
                result.append(chr(
                    0x10000 + ((codepoint - 0xd800) << 10) + lower - 0xdc00
                ))
            else:
                require(not 0xdc00 <= codepoint <= 0xdfff,
                        "reject an unpaired low surrogate")
                result.append(chr(codepoint))
        raise FreezeError("reject an unterminated JSON string")

    def number(self) -> int:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text),
                "reject an incomplete JSON number")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text)
                    or self.text[self.index] not in "0123456789",
                    "reject leading zeroes")
        else:
            require(self.text[self.index] in "123456789",
                    "reject a non-integer owner number")
            while (self.index < len(self.text)
                   and self.text[self.index] in "0123456789"):
                self.index += 1
        require(self.text[self.index:self.index + 1] not in (".", "e", "E"),
                "reject floats, nonfinite values, and exponents")
        token = self.text[start:self.index]
        require(0 < len(token) <= 32, "reject an unbounded integer")
        return int(token)

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "reject overdeep owner JSON")
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
                require(key not in result, "reject duplicate JSON key: " + key)
                self.whitespace()
                require(self.text[self.index:self.index + 1] == ":",
                        "reject a missing JSON colon")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "}":
                    return result
                require(separator == ",", "reject an invalid object separator")
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
                require(separator == ",", "reject an invalid array separator")
        if character == "-" or character in "0123456789":
            return self.number()
        for spelling, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(spelling, self.index):
                self.index += len(spelling)
                return value
        raise FreezeError("reject an unknown JSON literal")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text),
                "reject trailing content or multiple JSON documents")
        return result


def decode_json(raw: bytes) -> object:
    return StrictJSON(raw).decode()


def copy_value(value: object) -> object:
    return decode_json(canonical_bytes(value))


def read_exact(path: str, expected: str, size: int, device: int,
               inode: int, mode: int, links: int) -> bytes:
    checked_digest(expected, path)
    require(type(size) is int and 0 < size <= MAX_OWNER_BYTES,
            "reject an unbounded immutable source owner")
    absolute = absolute_owner(path)
    require(absolute in allowed_paths(), "reject an unlisted chart owner")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    try:
        descriptor = _CAPTURED_OS_OPEN(absolute, flags)
    except OSError as error:
        raise FreezeError("cannot read exact chart owner: " + path) from error
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and (before.st_size, before.st_dev, before.st_ino,
                     stat.S_IMODE(before.st_mode), before.st_nlink)
                == (size, device, inode, mode, links),
                "reject an altered, linked, or substituted chart owner: " + path)
        parts: list[bytes] = []
        total = 0
        while total < size:
            chunk = os.read(descriptor, min(262_144, size - total))
            require(bool(chunk), "reject a truncated chart owner: " + path)
            parts.append(chunk)
            total += len(chunk)
        require(os.read(descriptor, 1) == b"",
                "reject a chart owner that grew during authentication: " + path)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_nlink, before.st_mtime_ns,
                 stat.S_IMODE(before.st_mode))
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_nlink, after.st_mtime_ns,
                    stat.S_IMODE(after.st_mode)),
                "reject an owner changed during complete descriptor read: " + path)
    finally:
        os.close(descriptor)
    raw = b"".join(parts)
    require(len(raw) == size and digest(raw) == expected,
            "reject altered complete owner bytes: " + path)
    return raw


def read_source(expected: str) -> bytes:
    checked_digest(expected, "overview source")
    identity = _CAPTURED_OS_STAT(absolute_owner(SOURCE), follow_symlinks=False)
    require(stat.S_ISREG(identity.st_mode)
            and identity.st_nlink == 1
            and stat.S_IMODE(identity.st_mode) == 0o600,
            "reject a linked, unsafe, or substituted overview source")
    return read_exact(SOURCE, expected, identity.st_size,
                      identity.st_dev, identity.st_ino,
                      stat.S_IMODE(identity.st_mode), identity.st_nlink)


def authenticate_owners() -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for name, path, expected, size, device, inode, mode, links in OWNERS:
        result[name] = read_exact(
            path, expected, size, device, inode, mode, links
        )
    return result


def owner_description(name: str) -> dict[str, object]:
    for candidate, path, expected, size, device, inode, mode, links in OWNERS:
        if candidate == name:
            return {"path": path, "sha256": expected, "bytes": size,
                    "device": device, "inode": inode,
                    "mode": format(mode, "04o"), "nlink": links}
    raise FreezeError("unknown exact chart owner: " + name)


def validate_baseline(owners: dict[str, bytes]) -> None:
    original = decode_json(owners["original_p0_contract"])
    require(type(original) is dict
            and original.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and original.get("version") == 1,
            "reject a substituted original correctness baseline")
    denominator = original.get("denominator")
    original_goal = original.get("goal")
    require(type(denominator) is dict
            and denominator.get("frozen_planned_case_execution_denominator")
            == ORIGINAL_CASES
            and denominator.get("final_required_case_execution_denominator")
            == ORIGINAL_CASES
            and denominator.get("available_frozen_vector_case_executions")
            == ORIGINAL_CASES
            and type(denominator.get("counted_suite_ids")) is list
            and len(denominator["counted_suite_ids"]) == ORIGINAL_SUITES
            and type(original_goal) is dict
            and original_goal.get("path") == "GOAL.md"
            and original_goal.get("sha256")
            == owner_description("goal")["sha256"],
            "reject a changed, doubled, or borrowed original baseline")
    current = decode_json(owners["current_p0_contract"])
    require(type(current) is dict
            and current.get("schema") == "rebar-cpython-re-p0-completeness-v4"
            and current.get("version") == 4
            and current.get("phase") == "CORRECTNESS ORACLE"
            and current.get("status") == "PASS"
            and current.get("original_case_execution_denominator")
            == ORIGINAL_CASES
            and current.get("original_suite_count") == ORIGINAL_SUITES
            and current.get("original_obligation_count") == ORIGINAL_OBLIGATIONS
            and current.get("original_crosswalk_count") == ORIGINAL_CROSSWALK
            and current.get("original_named_private_waiver_count")
            == ORIGINAL_PRIVATE_WAIVERS,
            "reject changed original cases, suites, obligations, or waivers")


def validate_matrix(document: object, expected_schema: str) -> dict[str, object]:
    require(type(document) is dict
            and document.get("schema") == expected_schema
            and document.get("version") == 1
            and document.get("phase") == "CORRECTNESS ORACLE",
            "reject a substituted frozen additive matrix owner")
    matrix = document.get("additive_matrix")
    expected_counts = {name: count for name, _label, count in COHORTS}
    require(type(matrix) is dict
            and matrix.get("case_count") == ADDITIVE_CASES
            and matrix.get("carrier_count") == CARRIERS
            and matrix.get("cohort_case_counts") == expected_counts
            and matrix.get("canonical_newline_delimited_matrix_sha256")
            == MATRIX_SHA256
            and matrix.get("expected_records") == "NOT RECORDED"
            and matrix.get("actual_reference_worker_count") == 0
            and matrix.get("actual_candidate_worker_count") == 0
            and sum(expected_counts.values()) == ADDITIVE_CASES,
            "reject invented, reordered, inferred, or changed frozen cohorts")
    return matrix


def validate_reference_contract(owners: dict[str, bytes]) -> None:
    supplement = decode_json(owners["supplement_contract"])
    validate_matrix(
        supplement,
        "rebar-owned-public-buffer-carriers-supplement-v1-frozen-contract",
    )
    supplement_source = supplement.get("source")
    supplement_protocol = supplement.get("protocol")
    require(type(supplement_source) is dict
            and supplement_source.get("path")
            == "tools/verify_owned_public_buffer_carriers_supplement_v1.py"
            and supplement_source.get("sha256")
            == owner_description("supplement_source")["sha256"]
            and type(supplement_protocol) is dict
            and supplement_protocol.get("path")
            == "oracle/phase1/P0-PUBLIC-BUFFER-CARRIERS-SUPPLEMENT-V1.md"
            and supplement_protocol.get("sha256")
            == owner_description("supplement_protocol")["sha256"],
            "reject substituted source-freeze cohort provenance")
    reference = decode_json(owners["reference_contract"])
    validate_matrix(
        reference,
        "rebar-owned-public-buffer-carriers-reference-v1-frozen-contract",
    )
    source = reference.get("source")
    protocol = reference.get("protocol")
    plan = reference.get("reference_controller")
    require(type(source) is dict
            and source.get("path")
            == "tools/run_owned_public_buffer_carriers_reference_v1.py"
            and source.get("sha256")
            == owner_description("reference_source")["sha256"]
            and type(protocol) is dict
            and protocol.get("path")
            == "oracle/phase1/P0-PUBLIC-BUFFER-CARRIERS-REFERENCE-V1.md"
            and protocol.get("sha256")
            == owner_description("reference_protocol")["sha256"]
            and type(plan) is dict
            and plan.get("status") == "NOT RUN"
            and plan.get("expected_records") == "NOT RECORDED"
            and plan.get("required_reference_roles")
            == ["reference-a", "reference-b"]
            and plan.get("required_case_count_per_worker") == ADDITIVE_CASES
            and plan.get("required_carrier_count") == CARRIERS
            and plan.get("required_ordered_matrix_sha256") == MATRIX_SHA256,
            "reject a changed reference source freeze or invented frozen answers")


def validate_receipt(receipt: object) -> dict[str, object]:
    require(type(receipt) is dict
            and receipt.get("schema")
            == "rebar-owned-public-buffer-carriers-reference-v1-"
            "durable-publication-receipt"
            and receipt.get("version") == 1
            and receipt.get("publication_status") == "PASS"
            and receipt.get("reference_status") == "PASS"
            and receipt.get("original_case_execution_denominator")
            == ORIGINAL_CASES
            and receipt.get("original_suite_count") == ORIGINAL_SUITES
            and receipt.get("original_obligation_count") == ORIGINAL_OBLIGATIONS
            and receipt.get("original_crosswalk_count") == ORIGINAL_CROSSWALK
            and receipt.get("original_named_private_waiver_count")
            == ORIGINAL_PRIVATE_WAIVERS
            and receipt.get("additive_case_count") == ADDITIVE_CASES
            and receipt.get("carrier_count") == CARRIERS
            and receipt.get("matrix_sha256") == MATRIX_SHA256
            and receipt.get("actual_reference_worker_count") == 2
            and receipt.get("actual_distinct_reference_process_ids")
            == list(WORKER_PIDS)
            and len(set(WORKER_PIDS)) == 2
            and receipt.get("actual_failure_count") == 0
            and receipt.get("records_sha256") == RECORDS_SHA256
            and receipt.get("source_sha256")
            == owner_description("reference_source")["sha256"]
            and receipt.get("protocol_sha256")
            == owner_description("reference_protocol")["sha256"]
            and receipt.get("contract_sha256") == REFERENCE_CONTRACT_SHA256
            and receipt.get("candidate_workers_started") == 0
            and receipt.get("holdout")
            == "NOT FROZEN / NOT GENERATED / NOT OPENED"
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("memory") == "NOT MEASURED"
            and receipt.get("undefined_behavior") == "NOT MEASURED"
            and receipt.get("winner_selected") is False
            and receipt.get("gzip_mtime") == 0
            and receipt.get("gzip_compression_level") == 9
            and receipt.get("uncompressed_bytes") == 470_813_612
            and receipt.get("uncompressed_sha256")
            == "8051f2f67778f55f4c4d5b1fe929f5a26b0dcb59e66626ff26cae5ddfbfaf518",
            "reject a fabricated, failed, partial, candidate, or changed actual baseline")
    archive = receipt.get("archive")
    require(type(archive) is dict
            and archive.get("path")
            == "oracle/phase1/evidence/"
            "public-buffer-carriers-reference-v1-cpython-3.14.6.json.gz"
            and archive.get("sha256") == ARCHIVE_SHA256
            and archive.get("bytes") == 11_596_116
            and archive.get("device") == 2064
            and archive.get("inode") == 525591
            and archive.get("mode") == "0600"
            and archive.get("nlink") == 1
            and archive.get("durable_file_sync") is True
            and archive.get("durable_directory_sync") is True,
            "reject receipt claims for a changed or nondurable actual archive")
    return receipt


def source_boundaries() -> dict[str, object]:
    return {
        "deny_default_audit_installed": _AUDIT_INSTALLED,
        "candidate_import_count": 0,
        "candidate_workers_started": 0,
        "reference_workers_started_by_chart": 0,
        "regex_operations_executed": 0,
        "native_libraries_loaded": 0,
        "archive_files_opened": 0,
        "archive_files_decompressed": 0,
        "holdout_files_opened": 0,
        "performance_cases_read": 0,
        "clock_samples": 0,
        "network_operations": 0,
        "process_starts": 0,
        "thread_starts": 0,
        "workspace_files_created": 0,
        "workspace_files_modified": 0,
        "chart_assets_created": 0,
        "candidate_status": "NOT RUN",
        "speed": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT FROZEN / NOT GENERATED / NOT OPENED",
    }


def xml_escape(value: str) -> str:
    require(type(value) is str, "escape only plain exact SVG text")
    return (value.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;")
            .replace("'", "&apos;"))


def number(value: int) -> str:
    require(type(value) is int and value >= 0,
            "format only measured nonnegative counts")
    return f"{value:,}"


def inputs_document(source_pin: str, receipt: dict[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA + "-inputs",
        "version": 1,
        "status": "ACTUAL PYTHON REFERENCE PASS; CANDIDATES NOT RUN",
        "chart_source": {"path": SOURCE, "sha256": source_pin},
        "authenticated_actual_receipt": owner_description(
            "actual_publication_receipt"
        ),
        "original_baseline": {
            "case_execution_denominator": ORIGINAL_CASES,
            "suite_count": ORIGINAL_SUITES,
            "obligation_count": ORIGINAL_OBLIGATIONS,
            "crosswalk_count": ORIGINAL_CROSSWALK,
            "named_private_waiver_count": ORIGINAL_PRIVATE_WAIVERS,
            "additive_cases_included_in_original_denominator": False,
        },
        "actual_reference": {
            "publication_status": receipt["publication_status"],
            "reference_status": receipt["reference_status"],
            "independent_worker_count": receipt["actual_reference_worker_count"],
            "records_sha256": receipt["records_sha256"],
            "observations": [
                {"label": "Python process " + str(pid),
                 "actual_process_id": pid,
                 "observed_case_count": ADDITIVE_CASES,
                 "frozen_case_count": ADDITIVE_CASES}
                for pid in WORKER_PIDS
            ],
        },
        "frozen_matrix": {
            "case_count": ADDITIVE_CASES,
            "carrier_count": CARRIERS,
            "sha256": MATRIX_SHA256,
            "cohorts": [
                {"id": name, "label": label, "frozen_question_count": count}
                for name, label, count in COHORTS
            ],
            "cohort_values_describe_frozen_questions_only": True,
            "per_cohort_mismatches_recorded": False,
            "per_cohort_worker_speeds_measured": False,
        },
        "scope": {
            "archive_opened_by_chart": False,
            "candidate_status": "NOT RUN",
            "candidate_workers_started": 0,
            "speed": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT FROZEN / NOT GENERATED / NOT OPENED",
            "winner_selected": False,
        },
        "expected_output_paths": [
            OUTPUT_DIRECTORY + "/" + name for name in OUTPUT_NAMES
        ],
    }


def svg_document(receipt: dict[str, object]) -> bytes:
    require(receipt.get("actual_distinct_reference_process_ids")
            == list(WORKER_PIDS),
            "render only the two independently recorded Python references")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="850"'
        ' viewBox="0 0 1120 850" role="img"'
        ' aria-labelledby="overview-title overview-description">',
        '  <title id="overview-title">Two independent Python references'
        ' answered all 48,416 new regular-expression questions</title>',
        '  <desc id="overview-description">Actual Python processes 81 and 82'
        ' each answered 48,416 of 48,416 frozen buffer-carrier questions.'
        ' Five bars describe the question categories only.'
        ' Candidates have not run. Speed has not been measured.</desc>',
        '  <rect width="1120" height="850" fill="#f5f8fc"/>',
        '  <rect x="36" y="32" width="1048" height="786" rx="20"'
        ' fill="#ffffff" stroke="#dce5ef"/>',
        '  <text x="76" y="91" fill="#10243a" font-family="Arial, sans-serif"'
        ' font-size="31" font-weight="700">Python reference:'
        ' all new questions answered</text>',
        '  <text x="76" y="127" fill="#526579"'
        ' font-family="Arial, sans-serif" font-size="17">Two independently'
        ' run Python processes; one unchanged frozen test set.</text>',
        '  <rect x="76" y="151" width="427" height="34" rx="17"'
        ' fill="#e6f5ec"/>',
        '  <text x="94" y="174" fill="#126744"'
        ' font-family="Arial, sans-serif" font-size="15"'
        ' font-weight="700">ACTUAL REFERENCE PASS'
        ' \u2022 86 kinds of buffer inputs</text>',
        '  <text x="76" y="226" fill="#10243a"'
        ' font-family="Arial, sans-serif" font-size="20"'
        ' font-weight="700">Questions answered by each Python process</text>',
    ]
    for index, pid in enumerate(WORKER_PIDS):
        top = 253 + index * 72
        colour = "#2763d1" if index == 0 else "#128b77"
        lines.extend([
            '  <text x="76" y="' + str(top + 29)
            + '" fill="#24364b" font-family="Arial, sans-serif"'
            ' font-size="16" font-weight="600">'
            + xml_escape("Python process " + str(pid)) + "</text>",
            '  <rect x="261" y="' + str(top)
            + '" width="614" height="42" rx="9" fill="#edf2f8"/>',
            '  <rect x="261" y="' + str(top)
            + '" width="614" height="42" rx="9" fill="' + colour + '"/>',
            '  <text x="890" y="' + str(top + 28)
            + '" fill="#10243a" font-family="Arial, sans-serif"'
            ' font-size="16" font-weight="700">'
            + number(ADDITIVE_CASES) + " / " + number(ADDITIVE_CASES)
            + "</text>",
        ])
    lines.extend([
        '  <line x1="76" y1="400" x2="1044" y2="400" stroke="#dce5ef"/>',
        '  <text x="76" y="445" fill="#10243a"'
        ' font-family="Arial, sans-serif" font-size="20"'
        ' font-weight="700">What the 48,416 new questions cover</text>',
        '  <text x="76" y="471" fill="#526579"'
        ' font-family="Arial, sans-serif" font-size="15">These are counts'
        ' of frozen questions, not speed or category-by-category results.</text>',
    ])
    maximum = max(count for _name, _label, count in COHORTS)
    for index, (_name, label, count) in enumerate(COHORTS):
        top = 489 + index * 45
        width = max(5, (520 * count + maximum // 2) // maximum)
        lines.extend([
            '  <text x="76" y="' + str(top + 22)
            + '" fill="#24364b" font-family="Arial, sans-serif"'
            ' font-size="15">' + xml_escape(label) + "</text>",
            '  <rect x="261" y="' + str(top)
            + '" width="520" height="29" rx="6" fill="#edf2f8"/>',
            '  <rect x="261" y="' + str(top) + '" width="' + str(width)
            + '" height="29" rx="6" fill="#6497e8"/>',
            '  <text x="795" y="' + str(top + 21)
            + '" fill="#10243a" font-family="Arial, sans-serif"'
            ' font-size="15" font-weight="600">'
            + number(count) + "</text>",
        ])
    lines.extend([
        '  <rect x="76" y="733" width="968" height="54" rx="10"'
        ' fill="#fff6e8" stroke="#f3ddb6"/>',
        '  <text x="95" y="756" fill="#76500b"'
        ' font-family="Arial, sans-serif" font-size="15"'
        ' font-weight="700">Python reference only;'
        ' candidates NOT RUN; speed NOT MEASURED.</text>',
        '  <text x="95" y="777" fill="#76500b"'
        ' font-family="Arial, sans-serif" font-size="13">The original'
        ' 31,237-question baseline remains separate.'
        ' No per-category mismatches or timings are claimed.</text>',
        "</svg>",
        "",
    ])
    result = "\n".join(lines).encode("utf-8")
    require(0 < len(result) <= MAX_DOCUMENT_BYTES,
            "reject an unbounded deterministic chart")
    require(result.startswith(b'<?xml version="1.0" encoding="UTF-8"?>\n<svg ')
            and result.endswith(b"</svg>\n")
            and result.count(b"48,416 / 48,416") == 2
            and b"Python reference only; candidates NOT RUN;"
            in result
            and b"speed NOT MEASURED." in result
            and b"<script" not in result.lower()
            and b"javascript:" not in result.lower()
            and b' href="http:' not in result.lower()
            and b' href="https:' not in result.lower()
            and b'xlink:href="http:' not in result.lower()
            and b'xlink:href="https:' not in result.lower(),
            "reject misleading, executable, external, or incomplete chart SVG")
    return result


def asset_description(name: str, content: bytes) -> dict[str, object]:
    require(name in OUTPUT_NAMES and type(content) is bytes,
            "reject an invented or escaped chart output")
    return {"path": OUTPUT_DIRECTORY + "/" + name,
            "bytes": len(content), "sha256": digest(content)}


def build_artifacts(source_pin: str, receipt: dict[str, object]
                    ) -> tuple[tuple[str, bytes], ...]:
    checked_digest(source_pin, "overview source")
    inputs = canonical_bytes(inputs_document(source_pin, receipt))
    svg = svg_document(receipt)
    summary = {
        "schema": SCHEMA + "-summary",
        "version": 1,
        "status": "ACTUAL PYTHON REFERENCE PASS; CANDIDATES NOT RUN",
        "source_sha256": source_pin,
        "actual_receipt_sha256": RECEIPT_SHA256,
        "original_case_execution_denominator": ORIGINAL_CASES,
        "additive_case_count": ADDITIVE_CASES,
        "carrier_count": CARRIERS,
        "matrix_sha256": MATRIX_SHA256,
        "records_sha256": RECORDS_SHA256,
        "actual_reference_worker_count": 2,
        "actual_distinct_reference_process_ids": list(WORKER_PIDS),
        "actual_observed_cases_per_reference": [
            ADDITIVE_CASES, ADDITIVE_CASES
        ],
        "frozen_cohort_question_counts": {
            name: count for name, _label, count in COHORTS
        },
        "cohort_values_are_case_counts_not_match_or_speed_results": True,
        "per_cohort_mismatches_claimed": False,
        "per_cohort_worker_speeds_claimed": False,
        "candidate_status": "NOT RUN",
        "candidate_workers_started": 0,
        "speed": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT FROZEN / NOT GENERATED / NOT OPENED",
        "archive_opened_by_chart": False,
        "winner_selected": False,
        "inputs": asset_description(OUTPUT_NAMES[0], inputs),
        "svg": asset_description(OUTPUT_NAMES[2], svg),
    }
    summary_bytes = canonical_bytes(summary)
    result = (
        (OUTPUT_NAMES[0], inputs),
        (OUTPUT_NAMES[1], summary_bytes),
        (OUTPUT_NAMES[2], svg),
    )
    validate_artifacts(result, source_pin, receipt)
    return result


def validate_artifacts(artifacts: tuple[tuple[str, bytes], ...],
                       source_pin: str, receipt: dict[str, object]) -> None:
    require(type(artifacts) is tuple and len(artifacts) == 3
            and tuple(name for name, _content in artifacts) == OUTPUT_NAMES
            and all(type(content) is bytes
                    and 0 < len(content) <= MAX_DOCUMENT_BYTES
                    for _name, content in artifacts),
            "reject missing, reordered, extra, escaped, or unbounded chart assets")
    inputs = decode_json(artifacts[0][1])
    summary = decode_json(artifacts[1][1])
    require(inputs == inputs_document(source_pin, receipt)
            and canonical_bytes(inputs) == artifacts[0][1],
            "reject altered exact chart inputs")
    require(type(summary) is dict
            and summary.get("schema") == SCHEMA + "-summary"
            and summary.get("source_sha256") == source_pin
            and summary.get("actual_receipt_sha256") == RECEIPT_SHA256
            and summary.get("original_case_execution_denominator")
            == ORIGINAL_CASES
            and summary.get("additive_case_count") == ADDITIVE_CASES
            and summary.get("carrier_count") == CARRIERS
            and summary.get("matrix_sha256") == MATRIX_SHA256
            and summary.get("records_sha256") == RECORDS_SHA256
            and summary.get("actual_reference_worker_count") == 2
            and summary.get("actual_distinct_reference_process_ids")
            == list(WORKER_PIDS)
            and summary.get("actual_observed_cases_per_reference")
            == [ADDITIVE_CASES, ADDITIVE_CASES]
            and summary.get("frozen_cohort_question_counts")
            == {name: count for name, _label, count in COHORTS}
            and summary.get("cohort_values_are_case_counts_not_match_or_speed_results")
            is True
            and summary.get("per_cohort_mismatches_claimed") is False
            and summary.get("per_cohort_worker_speeds_claimed") is False
            and summary.get("candidate_status") == "NOT RUN"
            and summary.get("candidate_workers_started") == 0
            and summary.get("speed") == "NOT MEASURED"
            and summary.get("memory") == "NOT MEASURED"
            and summary.get("archive_opened_by_chart") is False
            and summary.get("holdout")
            == "NOT FROZEN / NOT GENERATED / NOT OPENED"
            and summary.get("winner_selected") is False
            and summary.get("inputs")
            == asset_description(OUTPUT_NAMES[0], artifacts[0][1])
            and summary.get("svg")
            == asset_description(OUTPUT_NAMES[2], artifacts[2][1])
            and canonical_bytes(summary) == artifacts[1][1]
            and artifacts[2][1] == svg_document(receipt),
            "reject dishonest, noncanonical, or mismatched chart assets")


def predictions(artifacts: tuple[tuple[str, bytes], ...]
                ) -> list[dict[str, object]]:
    return [asset_description(name, content)
            for name, content in artifacts]


def verify_context(pins: dict[str, object], owners: dict[str, bytes]
                   ) -> dict[str, object]:
    validate_baseline(owners)
    validate_reference_contract(owners)
    raw_receipt = owners["actual_publication_receipt"]
    require(pins["receipt"] == RECEIPT_SHA256
            and pins["reference"] == REFERENCE_CONTRACT_SHA256
            and pins["matrix"] == MATRIX_SHA256
            and pins["original"] == ORIGINAL_CASES
            and digest(raw_receipt) == pins["receipt"],
            "reject unpinned source, actual receipt, frozen matrix, or denominator")
    receipt = validate_receipt(decode_json(raw_receipt))
    require(canonical_bytes(receipt) == raw_receipt,
            "reject incomplete or noncanonical actual publication receipt")
    artifacts = build_artifacts(pins["source"], receipt)
    require(not any(absolute_owner(
        "oracle/phase1/evidence/"
        "public-buffer-carriers-reference-v1-cpython-3.14.6.json.gz"
    ) == path for path in allowed_paths()),
            "never permit an actual compressed archive as a chart source")
    return {
        "schema": SCHEMA + "-source-verification",
        "version": 1,
        "status": "PASS",
        "chart_status": "SOURCE VERIFIED; OUTPUTS NOT GENERATED",
        "source_sha256": pins["source"],
        "receipt_sha256": RECEIPT_SHA256,
        "reference_contract_sha256": REFERENCE_CONTRACT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "original_case_execution_denominator": ORIGINAL_CASES,
        "original_suite_count": ORIGINAL_SUITES,
        "original_obligation_count": ORIGINAL_OBLIGATIONS,
        "original_crosswalk_count": ORIGINAL_CROSSWALK,
        "original_named_private_waiver_count": ORIGINAL_PRIVATE_WAIVERS,
        "additive_case_count": ADDITIVE_CASES,
        "carrier_count": CARRIERS,
        "actual_reference_status": "PASS",
        "actual_reference_worker_count": 2,
        "actual_distinct_reference_process_ids": list(WORKER_PIDS),
        "records_sha256": RECORDS_SHA256,
        "frozen_cohort_question_counts": {
            name: count for name, _label, count in COHORTS
        },
        "authenticated_immutable_owner_count": len(OWNERS),
        "predicted_output_count": 3,
        "predicted_outputs": predictions(artifacts),
        "source_only_boundaries": source_boundaries(),
    }


def exercise_receipt_controls(receipt: dict[str, object]) -> int:
    keys = (
        "schema", "version", "publication_status", "reference_status",
        "original_case_execution_denominator", "original_suite_count",
        "original_obligation_count", "original_crosswalk_count",
        "original_named_private_waiver_count", "additive_case_count",
        "carrier_count", "matrix_sha256", "actual_reference_worker_count",
        "actual_distinct_reference_process_ids", "actual_failure_count",
        "records_sha256", "source_sha256", "protocol_sha256",
        "contract_sha256", "candidate_workers_started", "holdout",
        "performance", "memory", "undefined_behavior", "winner_selected",
        "gzip_mtime", "gzip_compression_level", "uncompressed_bytes",
        "uncompressed_sha256",
    )
    rejected = 0
    for key in keys:
        hostile = copy_value(receipt)
        value = hostile[key]
        if type(value) is bool:
            hostile[key] = not value
        elif type(value) is int:
            hostile[key] = value + 1
        elif type(value) is str:
            hostile[key] = value + "!"
        elif type(value) is list:
            hostile[key] = value[:-1]
        else:
            hostile[key] = None
        try:
            validate_receipt(hostile)
        except FreezeError:
            rejected += 1
        else:
            raise FreezeError("accepted hostile actual receipt claim: " + key)
    for key in (
        "path", "sha256", "bytes", "device", "inode", "mode", "nlink",
        "durable_file_sync", "durable_directory_sync",
    ):
        hostile = copy_value(receipt)
        value = hostile["archive"][key]
        if type(value) is bool:
            hostile["archive"][key] = not value
        elif type(value) is int:
            hostile["archive"][key] = value + 1
        else:
            hostile["archive"][key] = value + "!"
        try:
            validate_receipt(hostile)
        except FreezeError:
            rejected += 1
        else:
            raise FreezeError("accepted hostile receipt archive claim: " + key)
    return rejected


def exercise_matrix_controls(owners: dict[str, bytes]) -> int:
    attacks = (
        ("supplement_contract",
         "rebar-owned-public-buffer-carriers-supplement-v1-frozen-contract"),
        ("reference_contract",
         "rebar-owned-public-buffer-carriers-reference-v1-frozen-contract"),
    )
    rejected = 0
    for owner, schema in attacks:
        document = decode_json(owners[owner])
        for name in (
            "case_count", "carrier_count", "cohort_case_counts",
            "canonical_newline_delimited_matrix_sha256", "expected_records",
            "actual_reference_worker_count", "actual_candidate_worker_count",
        ):
            hostile = copy_value(document)
            prior = hostile["additive_matrix"][name]
            if type(prior) is int:
                hostile["additive_matrix"][name] = prior + 1
            elif type(prior) is str:
                hostile["additive_matrix"][name] = prior + "!"
            else:
                hostile["additive_matrix"][name] = {}
            try:
                validate_matrix(hostile, schema)
            except FreezeError:
                rejected += 1
            else:
                raise FreezeError("accepted hostile frozen matrix: " + owner
                                  + ":" + name)
        for cohort, _label, _count in COHORTS:
            for change in (-1, 1):
                hostile = copy_value(document)
                hostile["additive_matrix"]["cohort_case_counts"][cohort] += change
                try:
                    validate_matrix(hostile, schema)
                except FreezeError:
                    rejected += 1
                else:
                    raise FreezeError("accepted hostile cohort count: "
                                      + owner + ":" + cohort)
    return rejected


def exercise_asset_controls(source_pin: str, receipt: dict[str, object],
                            artifacts: tuple[tuple[str, bytes], ...]) -> int:
    attacks = (
        ("missing-output", artifacts[:-1]),
        ("reordered-output", (artifacts[1], artifacts[0], artifacts[2])),
        ("extra-output", artifacts + (artifacts[0],)),
        ("renamed-input", (("changed.inputs.json", artifacts[0][1]),
                           artifacts[1], artifacts[2])),
        ("changed-input-byte", ((artifacts[0][0], artifacts[0][1] + b" "),
                                artifacts[1], artifacts[2])),
        ("changed-summary-byte", (artifacts[0],
                                  (artifacts[1][0], artifacts[1][1] + b" "),
                                  artifacts[2])),
        ("changed-svg-byte", (artifacts[0], artifacts[1],
                              (artifacts[2][0], artifacts[2][1] + b" "))),
        ("empty-svg", (artifacts[0], artifacts[1],
                       (artifacts[2][0], b""))),
    )
    rejected = 0
    for name, hostile in attacks:
        try:
            validate_artifacts(hostile, source_pin, receipt)
        except FreezeError:
            rejected += 1
        else:
            raise FreezeError("accepted hostile predicted chart asset: " + name)
    return rejected


def exercise_json_controls() -> int:
    samples = (
        b'{"x":1,"x":2}',
        b'{"x":1} {"y":2}',
        b'{"x":01}',
        b'{"x":NaN}',
        b'{"x":Infinity}',
        b'{"x":1.5}',
        b'{"x":1e3}',
        b'{"x":"\\ud800"}',
        b'{"x":"\\udc00"}',
        b'{"x":"unterminated}',
        b'{"x":true,}',
        b"",
    )
    rejected = 0
    for raw in samples:
        try:
            decode_json(raw)
        except (FreezeError, ValueError, UnicodeError, IndexError):
            rejected += 1
        else:
            raise FreezeError("accepted malformed or duplicate source-only JSON")
    return rejected


def exercise_physical_boundaries() -> int:
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    archive = absolute_owner(
        "oracle/phase1/evidence/"
        "public-buffer-carriers-reference-v1-cpython-3.14.6.json.gz"
    )
    holdout = absolute_owner("performance/holdout/cases.json.gz")
    output = absolute_owner(OUTPUT_DIRECTORY + "/" + OUTPUT_NAMES[2])
    attempts: list[tuple[str, object]] = [
        ("stdlib-re-import", lambda: builtins.__import__("re")),
        ("sre-import", lambda: builtins.__import__("_sre")),
        ("candidate-import", lambda: builtins.__import__("rebar")),
        ("gzip-import", lambda: builtins.__import__("gzip")),
        ("json-import", lambda: builtins.__import__("json")),
        ("native-import", lambda: builtins.__import__("ctypes")),
        ("process-import", lambda: builtins.__import__("subprocess")),
        ("network-import", lambda: builtins.__import__("socket")),
        ("archive-read", lambda: _CAPTURED_OS_OPEN(archive, flags)),
        ("holdout-read", lambda: _CAPTURED_OS_OPEN(holdout, flags)),
        ("asset-read", lambda: _CAPTURED_OS_OPEN(output, flags)),
        ("foreign-owner-read", lambda: _CAPTURED_OS_OPEN("/tmp", flags)),
        ("workspace-write", lambda: os.write(1, b"forbidden")),
        ("asset-unlink", lambda: os.unlink(output)),
        ("process-start", lambda: os.system("forbidden")),
        ("buffer-construction", lambda: builtins.memoryview(b"forbidden")),
        ("mutable-buffer-construction", lambda: builtins.bytearray(b"forbidden")),
        ("unknown-audit-event", lambda: sys.audit(
            "rebar.reference-overview.denied", "source-only control"
        )),
    ]
    if _CAPTURED_IO_OPEN is not None:
        attempts.append(("captured-io-archive",
                         lambda: _CAPTURED_IO_OPEN(archive, "rb")))
    if _CAPTURED_POSIX_OPEN is not None:
        attempts.append(("captured-posix-holdout",
                         lambda: _CAPTURED_POSIX_OPEN(holdout, flags)))
    rejected = 0
    for name, attempt in attempts:
        try:
            attempt()
        except FreezeError:
            rejected += 1
        else:
            raise FreezeError("physical deny-default guard accepted: " + name)
    return rejected


def self_test(pins: dict[str, object],
              owners: dict[str, bytes]) -> dict[str, object]:
    result = verify_context(pins, owners)
    receipt = validate_receipt(decode_json(
        owners["actual_publication_receipt"]
    ))
    artifacts = build_artifacts(pins["source"], receipt)
    receipt_rejected = exercise_receipt_controls(receipt)
    matrix_rejected = exercise_matrix_controls(owners)
    asset_rejected = exercise_asset_controls(
        pins["source"], receipt, artifacts
    )
    json_rejected = exercise_json_controls()
    physical_rejected = exercise_physical_boundaries()
    rejected = (receipt_rejected + matrix_rejected + asset_rejected
                + json_rejected + physical_rejected)
    require(receipt_rejected == 38
            and matrix_rejected == 34
            and asset_rejected == 8
            and json_rejected == 12
            and physical_rejected >= 18,
            "exercise every honest receipt, matrix, asset, JSON, and guard control")
    result.update({
        "schema": SCHEMA + "-source-self-test",
        "receipt_hostile_controls_rejected": receipt_rejected,
        "matrix_and_cohort_hostile_controls_rejected": matrix_rejected,
        "predicted_asset_hostile_controls_rejected": asset_rejected,
        "strict_json_hostile_controls_rejected": json_rejected,
        "physical_deny_default_controls_rejected": physical_rejected,
        "rejected_hostile_control_count": rejected,
        "blocked_actual_callable_attempts_by_kind": dict(_BLOCKED_CALLS),
        "blocked_audit_events_by_name": dict(_BLOCKED_AUDIT_EVENTS),
        "synthetic_unknown_audit_event_is_actual_operation": False,
        "source_only_boundaries": source_boundaries(),
    })
    clean_bootstrap()
    return result


def open_output_directory() -> int:
    flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
             | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(ROOT, flags)
    try:
        for name, expected_inode in (("docs", 428374), ("evidence", 431343)):
            child = os.open(name, flags, dir_fd=descriptor)
            info = os.fstat(child)
            require(stat.S_ISDIR(info.st_mode)
                    and info.st_dev == 2064
                    and info.st_ino == expected_inode
                    and stat.S_IMODE(info.st_mode) == 0o700
                    and info.st_uid == os.getuid(),
                    "reject an escaped, linked, or exposed chart output directory")
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def publish_asset(directory: int, name: str,
                  content: bytes) -> dict[str, object]:
    expected = asset_description(name, content)
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(name, flags, 0o600, dir_fd=directory)
    try:
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode)
                and stat.S_IMODE(initial.st_mode) == 0o600
                and initial.st_nlink == 1,
                "reject a linked, exposed, or nonregular chart asset")
        offset = 0
        while offset < len(content):
            written = os.write(descriptor, content[offset:])
            require(type(written) is int and written > 0,
                    "reject a partial chart asset")
            offset += written
        os.fsync(descriptor)
        final = os.fstat(descriptor)
        require((final.st_dev, final.st_ino, final.st_size,
                 stat.S_IMODE(final.st_mode), final.st_nlink)
                == (initial.st_dev, initial.st_ino, len(content), 0o600, 1),
                "reject a substituted or incomplete chart asset")
    finally:
        os.close(descriptor)
    flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
             | getattr(os, "O_CLOEXEC", 0))
    verified = os.open(name, flags, dir_fd=directory)
    try:
        info = os.fstat(verified)
        require((info.st_dev, info.st_ino, info.st_size,
                 stat.S_IMODE(info.st_mode), info.st_nlink)
                == (initial.st_dev, initial.st_ino, len(content), 0o600, 1),
                "reject a changed same-inode chart asset")
        pieces: list[bytes] = []
        total = 0
        while total < len(content):
            chunk = os.read(verified, min(262_144, len(content) - total))
            require(bool(chunk), "reject truncated chart asset readback")
            pieces.append(chunk)
            total += len(chunk)
        require(os.read(verified, 1) == b"",
                "reject chart asset growth during readback")
        require(b"".join(pieces) == content,
                "reject altered deterministic chart asset bytes")
    finally:
        os.close(verified)
    result = dict(expected)
    result.update({"device": initial.st_dev, "inode": initial.st_ino,
                   "mode": "0600", "nlink": 1,
                   "durable_file_sync": True})
    return result


def render(pins: dict[str, object],
           owners: dict[str, bytes]) -> dict[str, object]:
    require(not _AUDIT_INSTALLED,
            "only explicit --render may create the three exact chart assets")
    validate_baseline(owners)
    validate_reference_contract(owners)
    require(pins["receipt"] == RECEIPT_SHA256
            and pins["reference"] == REFERENCE_CONTRACT_SHA256
            and pins["matrix"] == MATRIX_SHA256
            and pins["original"] == ORIGINAL_CASES,
            "render only with all independently frozen caller pins")
    receipt = validate_receipt(decode_json(
        owners["actual_publication_receipt"]
    ))
    require(canonical_bytes(receipt)
            == owners["actual_publication_receipt"],
            "render only from the exact complete canonical actual receipt")
    artifacts = build_artifacts(pins["source"], receipt)
    directory = open_output_directory()
    try:
        for name, _content in artifacts:
            try:
                os.stat(name, dir_fd=directory, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise FreezeError("never overwrite an existing chart asset: " + name)
        published = [publish_asset(directory, name, content)
                     for name, content in artifacts]
        os.fsync(directory)
    finally:
        os.close(directory)
    clean_bootstrap()
    return {
        "schema": SCHEMA + "-render",
        "version": 1,
        "status": "PASS",
        "reference_status": "PASS",
        "source_sha256": pins["source"],
        "receipt_sha256": RECEIPT_SHA256,
        "reference_contract_sha256": REFERENCE_CONTRACT_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "original_case_execution_denominator": ORIGINAL_CASES,
        "additive_case_count": ADDITIVE_CASES,
        "carrier_count": CARRIERS,
        "actual_reference_worker_count": 2,
        "actual_distinct_reference_process_ids": list(WORKER_PIDS),
        "predicted_outputs": predictions(artifacts),
        "published_outputs": published,
        "durable_directory_sync": True,
        "archive_opened_by_chart": False,
        "candidate_status": "NOT RUN",
        "speed": "NOT MEASURED",
        "holdout": "NOT FROZEN / NOT GENERATED / NOT OPENED",
    }


def parse_arguments(argv: list[str]) -> tuple[str, dict[str, object]]:
    modes = ("--self-test", "--verify-frozen-context", "--render")
    options = {
        "--source-sha256": "source",
        "--receipt-sha256": "receipt",
        "--reference-contract-sha256": "reference",
        "--matrix-sha256": "matrix",
        "--original-case-count": "original",
    }
    selected = ""
    pins: dict[str, object] = {}
    index = 0
    while index < len(argv):
        word = argv[index]
        if word in modes:
            require(not selected, "require exactly one explicit chart mode")
            selected = word
            index += 1
            continue
        require(word in options and index + 1 < len(argv),
                "reject an unknown, missing, or incomplete chart pin")
        name = options[word]
        require(name not in pins, "reject a repeated independent chart pin")
        raw = argv[index + 1]
        if name == "original":
            require(raw == str(ORIGINAL_CASES),
                    "pin the original denominator exactly; never infer it")
            pins[name] = ORIGINAL_CASES
        else:
            pins[name] = checked_digest(raw, name)
        index += 2
    require(selected in modes and set(pins) == {
        "source", "receipt", "reference", "matrix", "original",
    }, "require all source, receipt, matrix, baseline, and reference-owner pins")
    require(pins["receipt"] == RECEIPT_SHA256
            and pins["reference"] == REFERENCE_CONTRACT_SHA256
            and pins["matrix"] == MATRIX_SHA256
            and pins["original"] == ORIGINAL_CASES,
            "reject stale, substituted, or guessed chart caller pins")
    return selected, pins


def main(argv: list[str]) -> int:
    clean_bootstrap()
    mode, pins = parse_arguments(argv)
    source_only = mode in ("--self-test", "--verify-frozen-context")
    if source_only:
        install_wall()
    read_source(pins["source"])
    owners = authenticate_owners()
    if mode == "--self-test":
        result = self_test(pins, owners)
    elif mode == "--verify-frozen-context":
        result = verify_context(pins, owners)
    else:
        result = render(pins, owners)
    if source_only:
        clean_bootstrap()
    sys.stdout.buffer.write(canonical_bytes(result))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (FreezeError, OSError, ValueError, TypeError, UnicodeError,
            OverflowError, RecursionError, IndexError) as error:
        try:
            sys.stderr.write(
                "public buffer-carrier reference chart rejected: "
                + type(error).__name__ + ": " + str(error) + "\n"
            )
            sys.stderr.flush()
        except BaseException:
            pass
        raise SystemExit(2)
