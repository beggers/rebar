#!/usr/bin/env python3
"""Compose all frozen Rust adapter repairs with first-party comment lexing.

Source gates have an irreversible descriptor-only allowlist and never open a
candidate, native object, archive, holdout, Git metadata, clock, or network.
Only separately authorized root application reconstructs the existing private
four-repair adapter from its immutable canonical source and appends the three
independently frozen comment-aware named-escape repairs.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("a first-party adapter freeze must not import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
DEVICE = 2064
SOURCE = "tools/apply_owned_rust_corrected_comment_adapter_v2.py"
PROTOCOL = "oracle/phase2/RUST-CORRECTED-COMMENT-ADAPTER-V2.md"
CONTRACT = "oracle/phase2/rust-corrected-comment-adapter-v2.json"
SCHEMA = "rebar-owned-rust-corrected-comment-adapter-v2-source-freeze"
INPUT = "candidates/rust_candidate.py"
INPUT_SHA = "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b"
INPUT_BYTES = 31151
INPUT_INODE = 428100
CORRECTED_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
CORRECTED_BYTES = 31934
STANDALONE_SHA = "c1d150d467d5732eab4cc589f7e18583e59892592fb48d7d6f37700c00dccda0"
STANDALONE_BYTES = 33256
TARGET_DIRECTORY = "candidates/rust/variants/corrected_comment_adapter_v2"
TARGET = TARGET_DIRECTORY + "/rust_candidate.py"
OUTPUT_SHA = "f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227"
OUTPUT_BYTES = 34039
VERBOSE = 64
PUBLIC_CASES = 10434
PUBLIC_MISMATCHES = 1145
TARGETED = 324
COMMENT_ONLY = 297
SCANNER_OVERLAP = 15
SUBSTITUTION_OVERLAP = 12
MAX_OWNER_BYTES = 1_048_576

REPAIR_SOURCE = "tools/apply_owned_rust_public_contract_source_repair_v3.py"
COMMENT_SOURCE = "tools/apply_owned_rust_verbose_named_escape_semantics_v1.py"
COMMENT_APPLICATION = (
    "oracle/phase2/evidence/rust-verbose-named-escape-semantics-v1-application.json"
)
V30_PUBLICATION = (
    "oracle/phase2/evidence/native-source-build-v30-rust-phase2-v30-rust-"
    "complete-semantic-source-root-provenance-publication-receipt.json"
)
V30_ROOT = (
    "oracle/phase2/evidence/native-source-build-v30-rust-phase2-v30-rust-"
    "complete-semantic-source-root-provenance-root-provenance-receipt.json"
)
V25_RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-"
    "v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-"
    "publication-receipt.json"
)
V26_RECEIPT = (
    "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v26-"
    "anchor-public-run-001-publication-receipt.json"
)
V27_RECEIPT = (
    "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v27-"
    "compiler-public-run-001-publication-receipt.json"
)
V28_RECEIPT = (
    "oracle/phase2/evidence/rust-native-architecture-public-gate-v3-v28-"
    "combined-public-run-001-publication-receipt.json"
)
V1_FAILURE = (
    "oracle/phase2/evidence/rust-corrected-comment-adapter-v1-"
    "preapplication-failure.json"
)

# role, relative path, complete SHA-256, bytes, device-2064 inode.
OWNERS = (
    ("repair_source", REPAIR_SOURCE,
     "5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859", 92060, 431033),
    ("repair_protocol", "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md",
     "2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34", 6405, 524675),
    ("repair_contract", "oracle/phase2/rust-public-contract-source-repair-v3.json",
     "82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1", 14817, 524678),
    ("comment_source", COMMENT_SOURCE,
     "cb2dc59dbe973f0ef33606a32ba0d475d8e3617fa1d435fe867fcaf2007132f2", 79250, 431176),
    ("comment_protocol", "oracle/phase2/RUST-VERBOSE-NAMED-ESCAPE-SEMANTICS-V1.md",
     "e3707659283373c432717d1c8356ce5cb045a63361b7e971f58bceb0d5a60cac", 8256, 525870),
    ("comment_contract", "oracle/phase2/rust-verbose-named-escape-semantics-v1.json",
     "3198c323841cf3dbde87179270a4afd714d321cda7ca785748e8778a261dad57", 7115, 525871),
    ("comment_application", COMMENT_APPLICATION,
     "2d194cecca898a23c3515ffc69cd8aefc8b16fd5f1d205c5dcd84ff6113d9b90", 1760, 524891),
    ("original_v25", V25_RECEIPT,
     "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59", 11832, 524846),
    ("public_v26", V26_RECEIPT,
     "23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80", 40906, 525333),
    ("public_v27", V27_RECEIPT,
     "a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449", 68330, 525426),
    ("public_v28", V28_RECEIPT,
     "c786b1216a58c4ac6a29363ce87d7741fb55fbb85f30665f795875bef244becb", 40372, 525923),
    ("v30_source", "tools/reproduce_owned_rust_complete_semantic_source_build_v30.py",
     "dd0ed268775537b985a060e5f608c6bc2730f86922ad20ee78cff19e4c387a1d", 138860, 431674),
    ("v30_protocol", "oracle/phase2/RUST-COMPLETE-SEMANTIC-SOURCE-BUILD-V30.md",
     "9f508fd651fa544ecea82487cb05bc94cce6aa1049ec676d257eb62fc73b3c61", 8746, 524934),
    ("v30_contract", "oracle/phase2/rust-complete-semantic-source-build-v30.json",
     "38e0a8f44cf1e3f68abb643b004f7f47350e743f5c3f1994d101b02e5ebc1956", 41458, 524935),
    ("v30_publication", V30_PUBLICATION,
     "c29361f0436f73ada037ba497a0eb008eeadac6ebb41c50019521c0212448abd", 3438, 524977),
    ("v30_root", V30_ROOT,
     "26445b833ac0e846538a1f648059a1c8a224e4e2f1acd58f82e9458dcc142404", 77160, 524978),
    ("failed_v1_source", "tools/apply_owned_rust_corrected_comment_adapter_v1.py",
     "0f048599182b69965c88677cbfb9ccb162a9d9d943426d2b607503e48a797d69", 62699, 430272),
    ("failed_v1_protocol", "oracle/phase2/RUST-CORRECTED-COMMENT-ADAPTER-V1.md",
     "e04e29068703fd8580beeeb2463df75ff7af68008f811e2e8a053cf4a91112f7", 8423, 525027),
    ("failed_v1_contract", "oracle/phase2/rust-corrected-comment-adapter-v1.json",
     "ac99c411cd2cfcfcd66df63aff03c79ebedd9e41681b881eb78e7aa25252ee61", 5093, 525032),
    ("failed_v1_receipt", V1_FAILURE,
     "7bc692fcf17780ed05ca49c982536849212e1909f73337764b2392ea3ee9a37b", 902, 525290),
)

REPAIR_NAMES = (
    "OLD_FLAG_BLOCK", "V2_FLAG_BLOCK", "OLD_ERROR_BLOCK", "V2_ERROR_BLOCK",
    "OLD_PATTERN_BLOCK", "V2_PATTERN_BLOCK", "V3_PATTERN_BLOCK",
)
REPAIR_SEQUENCE = (
    ("OLD_FLAG_BLOCK", "V2_FLAG_BLOCK"),
    ("OLD_ERROR_BLOCK", "V2_ERROR_BLOCK"),
    ("OLD_PATTERN_BLOCK", "V2_PATTERN_BLOCK"),
    ("V2_PATTERN_BLOCK", "V3_PATTERN_BLOCK"),
)

ORIGINAL_COMPILE = (
    b'        named = _named_escapes(pattern) if isinstance(pattern, str) '
    b'and "\\\\N" in pattern else ()\n'
)
CORRECTED_COMPILE = (
    b'        named = _named_escapes(pattern, flags) if isinstance(pattern, str) '
    b'and "\\\\N" in pattern else ()\n'
)
ORIGINAL_SCANNER_CALL = b"                _named_escapes(pattern)\n"
CORRECTED_SCANNER_CALL = b"                _named_escapes(pattern, flags)\n"

ORIGINAL_NAMED_SCANNER = b'''def _named_escapes(pattern):
    if isinstance(pattern, bytes):
        return []
    found = []
    index = 0
    while index < len(pattern):
        if pattern[index] != "\\\\":
            index += 1
            continue
        slash = index
        index += 1
        if pattern[index:index + 2] != "N{":
            index += bool(pattern[index:index + 1])
            continue
        close = pattern.find("}", index + 2)
        if close == index + 2 or (close < 0 and index + 2 == len(pattern)):
            raise PatternError("missing character name", pattern, slash + 3)
        if close < 0:
            raise PatternError("missing }, unterminated name", pattern, slash + 3)
        name = pattern[index + 2:close]
        try:
            value = unicodedata.lookup(name)
        except KeyError:
            raise PatternError(f"undefined character name {name!r}", pattern, slash) from None
        if len(value) != 1:
            raise PatternError(f"undefined character name {name!r}", pattern, slash)
        found.append((slash, ord(value)))
        index = close + 1
    return found
'''

CORRECTED_NAMED_SCANNER = b'''def _named_escapes(pattern, flags=0):
    if isinstance(pattern, bytes):
        return []
    found = []
    index = 0
    verbose = bool(flags & int(VERBOSE))
    scopes = []
    in_class = False
    class_start = -1
    while index < len(pattern):
        char = pattern[index]
        if char == "\\\\":
            slash = index
            index += 1
            if pattern[index:index + 2] != "N{":
                index += bool(pattern[index:index + 1])
                continue
            close = pattern.find("}", index + 2)
            if close == index + 2 or (close < 0 and index + 2 == len(pattern)):
                raise PatternError("missing character name", pattern, slash + 3)
            if close < 0:
                raise PatternError("missing }, unterminated name", pattern, slash + 3)
            name = pattern[index + 2:close]
            try:
                value = unicodedata.lookup(name)
            except KeyError:
                raise PatternError(f"undefined character name {name!r}", pattern, slash) from None
            if len(value) != 1:
                raise PatternError(f"undefined character name {name!r}", pattern, slash)
            found.append((slash, ord(value)))
            index = close + 1
            continue
        if in_class:
            if char == "]" and index > class_start:
                in_class = False
            index += 1
            continue
        if verbose and char == "#":
            newline = pattern.find("\\n", index + 1)
            if newline < 0:
                break
            index = newline + 1
            continue
        if char == "[":
            in_class = True
            class_start = index + 1
            if pattern[class_start:class_start + 1] == "^":
                class_start += 1
            index += 1
            continue
        if char == "(":
            if pattern[index:index + 3] == "(?#":
                close = pattern.find(")", index + 3)
                index = len(pattern) if close < 0 else close + 1
                continue
            if pattern[index:index + 2] == "(?":
                marker = index + 2
                while (marker < len(pattern)
                       and pattern[marker] in "aiLmsux-"):
                    marker += 1
                if (marker > index + 2
                        and pattern[marker:marker + 1] in (":", ")")):
                    enabled, _, disabled = pattern[index + 2:marker].partition("-")
                    scoped_verbose = verbose
                    if "x" in enabled:
                        scoped_verbose = True
                    if "x" in disabled:
                        scoped_verbose = False
                    if pattern[marker] == ")":
                        verbose = scoped_verbose
                        index = marker + 1
                        continue
                    scopes.append(verbose)
                    verbose = scoped_verbose
                    index = marker + 1
                    continue
            scopes.append(verbose)
            index += 1
            continue
        if char == ")" and scopes:
            verbose = scopes.pop()
        index += 1
    return found
'''

PRESERVED_ANCHORS = (
    (b"from candidates import _rust_bridge\n", 1),
    (b"import unicodedata\n", 1),
    (b"class RegexFlag(enum.IntFlag):\n", 1),
    (b"    VERBOSE = X = 64\n", 1),
    (b"class _Native:\n", 1),
    (b"    def compile(self, pattern, flags):\n", 1),
    (b"    def compile_scanner(self, patterns, flags):\n", 1),
    (b"compiled = self.native_compile(pattern, flags, positions, values)", 1),
    (b"compiled = _rust_bridge.compile_scanner(\n", 1),
    (b"def _warn_ambiguous(pattern):\n", 1),
    (b"def _compile(pattern, flags):\n", 1),
    (b"_cache_pattern(key, result)", 1),
)


class FreezeError(Exception):
    """A source owner, adapter correction, or physical boundary drifted."""


def require(value: object, explanation: str) -> None:
    if value is not True:
        raise FreezeError(explanation)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash complete genuine first-party bytes only")
    return hashlib.sha256(raw).hexdigest()


def checked_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value),
            "require complete lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def quote(value: str) -> str:
    require(type(value) is str, "serialize genuine JSON text only")
    escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    return '"' + "".join(escapes.get(character, "\\u" + format(ord(character), "04x")
                         if ord(character) < 32 else character)
                         for character in value) + '"'


def canonical(value: object, depth: int = 0) -> str:
    require(depth < 64, "reject excessively nested frozen JSON output")
    if value is None:
        return "null"
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        return quote(value)
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "JSON keys must be text")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1)
                               for key in sorted(value)) + "}"
    raise FreezeError("reject unsupported, nonfinite, or user-defined JSON value")


def marker(payload: bytes, key: str, value: object,
           *, minimum: int = 1) -> None:
    token = (quote(key) + ":" + canonical(value)).encode("utf-8")
    require(payload.count(token) >= minimum,
            "missing authenticated exact JSON owner field: " + key)


def no_matching_imports() -> None:
    forbidden = ("re", "_sre", "regex", "_regex", "re2", "rure", "pcre",
                 "pcre2", "oniguruma", "hyperscan", "ctypes", "candidates",
                 "rebar", "subprocess", "socket", "threading", "multiprocessing",
                 "concurrent", "importlib", "gzip", "zipfile", "tarfile")
    require(not any(name == prefix or name.startswith(prefix + ".")
                    for name in sys.modules for prefix in forbidden),
            "forbid candidate, standard-library matcher, package, native loader, or process")


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.no_site == 1
            and sys.dont_write_bytecode is True and sys.executable == PYTHON
            and __file__ == ROOT + "/" + SOURCE,
            "require isolated, bytecode-disabled pinned official CPython 3.14.6")


class SourceWall:
    """Deny-default descriptor wall; only root apply admits one candidate."""

    def __init__(self, apply: bool = False) -> None:
        self.apply = apply
        self.public = frozenset((SOURCE, PROTOCOL, CONTRACT)
                                + tuple(row[1] for row in OWNERS))
        self.allowed = self.public
        self.input_authorized = False
        self.live: dict[int, tuple[str, str]] = {}
        self.root: int | None = None
        self.open_ticket: tuple[str, int] | None = None
        self.mkdir_ticket: tuple[str, int] | None = None
        self.source_reads = 0
        self.public_reads = 0
        self.workspace_mutations = 0
        self.output_opened = False
        self.directory_created = False
        self.installed = False
        self.blocked: dict[str, int] = {}
        self.native_open = os.open
        self.native_read = os.read
        self.native_write = os.write
        self.native_fstat = os.fstat
        self.native_close = os.close
        self.native_fsync = os.fsync
        self.native_mkdir = os.mkdir

    def deny(self, reason: str) -> None:
        self.blocked[reason] = self.blocked.get(reason, 0) + 1
        raise FreezeError("corrected-comment physical source wall: " + reason)

    def audit(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else None
            if self.open_ticket is not None and (path, flags) == self.open_ticket:
                return
            self.deny("unticketed candidate, native, holdout, archive, or owner open")
        if event == "os.mkdir":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            if self.mkdir_ticket is not None and (path, mode) == self.mkdir_ticket:
                return
            self.deny("unticketed workspace directory mutation")
        if (event in ("import", "exec", "compile", "marshal.loads", "os.system",
                      "os.fork", "os.posix_spawn", "os.posix_spawnp", "os.rename",
                      "os.replace", "os.remove", "os.unlink", "os.rmdir",
                      "os.chmod", "os.chown", "os.urandom", "os.getrandom",
                      "_interpreters.create", "_interpreters.exec", "code.__new__")
                or event.startswith(("subprocess.", "socket.", "ctypes.", "time.",
                                     "threading.", "multiprocessing.", "tempfile.",
                                     "os.exec", "os.spawn"))):
            self.deny("matcher import, process, compilation, dynamic code, or network")

    def forbidden(self, reason: str):
        def reject(*_args: object, **_kwargs: object) -> object:
            self.deny(reason)
        return reject

    def component(self, value: object) -> str:
        if type(value) is not str or not value or value in (".", "..") \
                or "/" in value or "\x00" in value:
            self.deny("unowned, hidden, invalid, or traversal component")
        assert isinstance(value, str)
        return value

    def ticket_open(self, path: str, flags: int, mode: int = 0,
                    *, dir_fd: int | None = None) -> int:
        require(self.open_ticket is None, "forbid nested descriptor authorizations")
        self.open_ticket = (path, flags)
        try:
            if dir_fd is None:
                return self.native_open(path, flags, mode)
            return self.native_open(path, flags, mode, dir_fd=dir_fd)
        finally:
            self.open_ticket = None

    def directory_flags(self) -> int:
        return (os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_CLOEXEC", 0))

    def file_flags(self) -> int:
        return os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)

    def open_root(self) -> None:
        require(self.installed and self.root is None,
                "open the pinned workspace root once after installing the wall")
        descriptor = self.ticket_open(ROOT, self.directory_flags())
        identity = self.native_fstat(descriptor)
        require(stat.S_ISDIR(identity.st_mode) and identity.st_dev == DEVICE,
                "reject substituted workspace directory")
        self.root = descriptor
        self.live[descriptor] = ("", "directory")

    def child(self, parent: int, component: str) -> int:
        component = self.component(component)
        record = self.live.get(parent)
        require(record is not None and record[1] == "directory",
                "reject foreign parent directory descriptor")
        relative = component if not record[0] else record[0] + "/" + component
        allowed = (any(path.startswith(relative + "/") for path in self.allowed)
                   or self.apply and (relative == TARGET_DIRECTORY
                                      or TARGET_DIRECTORY.startswith(relative + "/")))
        require(allowed and not relative.startswith((".git/", ".agents/", ".codex/")),
                "reject unowned candidate, holdout, archive, hidden, or private root")
        descriptor = self.ticket_open(component, self.directory_flags(), dir_fd=parent)
        identity = self.native_fstat(descriptor)
        require(stat.S_ISDIR(identity.st_mode) and identity.st_dev == DEVICE,
                "reject substituted owner directory: " + relative)
        require(descriptor not in self.live, "reject reused directory descriptor")
        self.live[descriptor] = (relative, "directory")
        return descriptor

    def close(self, descriptor: int) -> None:
        require(type(descriptor) is int and descriptor in self.live
                and descriptor != self.root, "reject foreign or root descriptor")
        self.native_close(descriptor)
        del self.live[descriptor]

    def parent(self, relative: str) -> tuple[int, list[int], str]:
        require(type(relative) is str and relative in self.allowed,
                "candidate, native, archive, final, or other owner is forbidden")
        require(self.root is not None, "open the pinned workspace descriptor first")
        pieces = relative.split("/")
        require(all(self.component(item) for item in pieces),
                "reject invalid first-party owner components")
        opened: list[int] = []
        descriptor = self.root
        try:
            for piece in pieces[:-1]:
                descriptor = self.child(descriptor, piece)
                opened.append(descriptor)
            return descriptor, opened, pieces[-1]
        except BaseException:
            for item in reversed(opened):
                self.close(item)
            raise

    def read(self, relative: str, count: int | None, inode: int | None,
             expected_sha: str) -> bytes:
        require(self.installed and relative in self.allowed,
                "forbid candidate bytes before explicit root-only application")
        parent, opened, filename = self.parent(relative)
        descriptor: int | None = None
        try:
            descriptor = self.ticket_open(filename, self.file_flags(), dir_fd=parent)
            self.live[descriptor] = (relative, "file")
            before = self.native_fstat(descriptor)
            require(stat.S_ISREG(before.st_mode)
                    and stat.S_IMODE(before.st_mode) == 0o600
                    and before.st_dev == DEVICE and before.st_nlink == 1
                    and before.st_uid == os.geteuid()
                    and 0 < before.st_size <= MAX_OWNER_BYTES
                    and (count is None or before.st_size == count)
                    and (inode is None or before.st_ino == inode),
                    "reject substituted complete plaintext owner: " + relative)
            pieces: list[bytes] = []
            remaining = before.st_size
            while remaining:
                payload = self.native_read(descriptor, min(remaining, 65536))
                require(type(payload) is bytes and bool(payload),
                        "reject truncated plaintext owner: " + relative)
                pieces.append(payload)
                remaining -= len(payload)
            require(self.native_read(descriptor, 1) == b"",
                    "reject extra plaintext owner bytes: " + relative)
            after = self.native_fstat(descriptor)
            require(all(getattr(before, key) == getattr(after, key)
                        for key in ("st_dev", "st_ino", "st_size", "st_mode",
                                    "st_mtime_ns", "st_ctime_ns")),
                    "reject concurrently mutated plaintext owner: " + relative)
            payload = b"".join(pieces)
            require(digest(payload) == checked_sha(expected_sha, relative),
                    "reject complete owner digest: " + relative)
            if relative == INPUT:
                require(self.apply and self.input_authorized and self.source_reads == 0,
                        "read the immutable canonical candidate exactly once")
                self.source_reads += 1
            else:
                self.public_reads += 1
            return payload
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            for item in reversed(opened):
                self.close(item)

    def authorize_input(self) -> None:
        require(self.apply and self.installed and self.root is not None
                and not self.input_authorized and self.source_reads == 0
                and self.workspace_mutations == 0
                and self.public_reads == len(OWNERS) + 3,
                "authorize one candidate read only after all authenticated hostile controls")
        self.allowed = self.public | frozenset((INPUT,))
        self.input_authorized = True

    def make_target_directory(self) -> int:
        require(self.apply and not self.directory_created and self.root is not None,
                "allow exactly one root-authorized fresh variant directory")
        descriptor = self.root
        opened: list[int] = []
        pieces = TARGET_DIRECTORY.split("/")
        try:
            for piece in pieces[:-1]:
                descriptor = self.child(descriptor, piece)
                opened.append(descriptor)
            name = self.component(pieces[-1])
            require(self.mkdir_ticket is None, "reject nested directory authorization")
            self.mkdir_ticket = (name, 0o700)
            try:
                self.native_mkdir(name, 0o700, dir_fd=descriptor)
            finally:
                self.mkdir_ticket = None
            self.directory_created = True
            self.workspace_mutations += 1
            return self.child(descriptor, name)
        finally:
            for item in reversed(opened):
                self.close(item)

    def materialize(self, payload: bytes) -> None:
        require(self.apply and self.source_reads == 1 and not self.output_opened,
                "require one explicit canonical read before exclusive composition")
        require(type(payload) is bytes and len(payload) == OUTPUT_BYTES
                and digest(payload) == OUTPUT_SHA,
                "reject non-frozen composed adapter before mutation")
        parent = self.make_target_directory()
        descriptor: int | None = None
        try:
            flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
            descriptor = self.ticket_open("rust_candidate.py", flags, 0o600,
                                          dir_fd=parent)
            self.live[descriptor] = (TARGET, "output")
            self.output_opened = True
            self.workspace_mutations += 1
            position = 0
            while position < len(payload):
                count = self.native_write(descriptor, payload[position:])
                require(type(count) is int and count > 0,
                        "reject incomplete exclusive corrected adapter write")
                position += count
            identity = self.native_fstat(descriptor)
            require(stat.S_ISREG(identity.st_mode)
                    and stat.S_IMODE(identity.st_mode) == 0o600
                    and identity.st_dev == DEVICE and identity.st_size == OUTPUT_BYTES
                    and identity.st_nlink == 1 and identity.st_uid == os.geteuid(),
                    "reject substituted exclusively materialized corrected adapter")
            self.native_fsync(descriptor)
            self.close(descriptor)
            descriptor = None
            self.native_fsync(parent)
            readback = self.ticket_open("rust_candidate.py", self.file_flags(),
                                        dir_fd=parent)
            try:
                self.live[readback] = (TARGET, "readback")
                pieces: list[bytes] = []
                remaining = OUTPUT_BYTES
                while remaining:
                    chunk = self.native_read(readback, min(remaining, 65536))
                    require(bool(chunk), "reject incomplete durable adapter readback")
                    pieces.append(chunk)
                    remaining -= len(chunk)
                require(self.native_read(readback, 1) == b""
                        and digest(b"".join(pieces)) == OUTPUT_SHA,
                        "reject complete durable composed adapter digest")
            finally:
                self.close(readback)
        finally:
            if descriptor is not None and descriptor in self.live:
                self.close(descriptor)
            self.close(parent)

    def install(self) -> None:
        require(not self.installed, "install irreversible source wall once")
        sys.addaudithook(self.audit)
        builtins.open = self.forbidden("builtins.open")
        _io.open = self.forbidden("_io.open")
        _io.FileIO = self.forbidden("_io.FileIO")
        io.open = self.forbidden("io.open")
        io.FileIO = self.forbidden("io.FileIO")
        for module in (_io, io):
            if hasattr(module, "open_code"):
                module.open_code = self.forbidden("open_code")
        for name in ("open", "read", "write", "fstat", "close", "fsync", "mkdir",
                     "fdopen", "dup", "dup2", "stat", "lstat", "readlink", "listdir",
                     "scandir", "walk", "fwalk", "access", "fork", "posix_spawn",
                     "posix_spawnp", "system", "makedirs", "remove", "unlink",
                     "rename", "replace", "rmdir", "chmod", "chown", "urandom",
                     "getrandom"):
            if hasattr(os, name):
                setattr(os, name, self.forbidden("os." + name))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                     "perf_counter_ns", "process_time", "process_time_ns",
                     "thread_time", "thread_time_ns", "clock_gettime",
                     "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.forbidden("time." + name))
        self.installed = True


def extract_repair_literals(source: bytes) -> dict[str, bytes]:
    require(type(source) is bytes, "extract only frozen first-party repair source bytes")
    values: dict[str, bytes] = {}
    for name in REPAIR_NAMES:
        marker = name.encode("ascii") + b' = b"""'
        require(source.count(marker) == 1,
                "require exactly one previous private repair literal: " + name)
        first = source.index(marker) + len(marker)
        last = source.find(b'"""', first)
        require(last >= first and last - first > 0,
                "reject missing complete historical adapter repair literal: " + name)
        values[name] = source[first:last]
    return values


def apply_repairs(source: bytes, blocks: dict[str, bytes], exact: bool) -> bytes:
    if exact:
        require(len(source) == INPUT_BYTES and digest(source) == INPUT_SHA,
                "reject unauthenticated canonical first-party Rust adapter")
    result = source
    for old_name, new_name in REPAIR_SEQUENCE:
        before, after = blocks[old_name], blocks[new_name]
        require(before != after and result.count(before) == 1
                and result.count(after) == 0,
                "require one reversible historical correction: " + old_name)
        result = result.replace(before, after, 1)
    if exact:
        require(len(result) == CORRECTED_BYTES and digest(result) == CORRECTED_SHA,
                "preserve the exact four-repair private V28/V30 adapter")
    return result


def apply_comments(source: bytes, exact: bool) -> bytes:
    if exact:
        require(len(source) == CORRECTED_BYTES and digest(source) == CORRECTED_SHA,
                "apply comment lexing only to the authentic V28/V30 adapter")
    sites = ((ORIGINAL_COMPILE, CORRECTED_COMPILE),
             (ORIGINAL_SCANNER_CALL, CORRECTED_SCANNER_CALL),
             (ORIGINAL_NAMED_SCANNER, CORRECTED_NAMED_SCANNER))
    locations = []
    for before, after in sites:
        require(source.count(before) == 1 and source.count(after) == 0,
                "require exactly one pristine comment correction site")
        locations.append(source.index(before))
    require(locations[0] < locations[1] < locations[2],
            "preserve compile, scanner, and lexical-helper source order")
    for anchor, count in PRESERVED_ANCHORS:
        require(source.count(anchor) == count,
                "preserve native matching, public flags, warning, and cache anchors")
    result = source
    for before, after in sites:
        result = result.replace(before, after, 1)
    restored = result
    for before, after in reversed(sites):
        require(restored.count(after) == 1,
                "require exactly one corrected owned comment site")
        restored = restored.replace(after, before, 1)
    require(restored == source, "comment repairs must be exactly reversible")
    delta = sum(len(after) - len(before) for before, after in sites)
    require(delta == 2105 and len(result) == len(source) + delta,
            "retain exact independently frozen 2,105-byte lexical correction")
    for anchor, count in PRESERVED_ANCHORS:
        require(result.count(anchor) == count,
                "preserve every public first-party matching anchor")
    for forbidden in (b"import re\n", b"import regex\n", b"from re import ",
                      b"from regex import ", b"import ctypes\n",
                      b"import subprocess\n"):
        require(source.count(forbidden) == result.count(forbidden) == 0,
                "reject production stdlib, third-party regex, or native-loader delegation")
    if exact:
        require(len(result) == OUTPUT_BYTES and digest(result) == OUTPUT_SHA,
                "reject exact fully corrected first-party comment adapter digest")
    return result


def compose(original: bytes, repair_source: bytes, exact: bool = False) -> bytes:
    blocks = extract_repair_literals(repair_source)
    corrected = apply_repairs(original, blocks, exact)
    result = apply_comments(corrected, exact)
    lexical_first = apply_comments(original, False)
    alternate = apply_repairs(lexical_first, blocks, False)
    require(alternate == result,
            "four public-contract and three comment edits must commute exactly")
    if exact:
        require(len(lexical_first) == STANDALONE_BYTES
                and digest(lexical_first) == STANDALONE_SHA,
                "authenticate the independently materialized standalone comment result")
    return result


def synthetic_material() -> tuple[bytes, bytes]:
    literals = {
        "OLD_FLAG_BLOCK": b"OLD-FLAG\n",
        "V2_FLAG_BLOCK": b"FIXED-FLAG\n",
        "OLD_ERROR_BLOCK": b"OLD-ERROR\n",
        "V2_ERROR_BLOCK": b"FIXED-ERROR\n",
        "OLD_PATTERN_BLOCK": b"OLD-PATTERN\n",
        "V2_PATTERN_BLOCK": b"MIDDLE-PATTERN\n",
        "V3_PATTERN_BLOCK": b"FIXED-PATTERN\n",
    }
    repair = b"".join(name.encode("ascii") + b' = b"""' + value + b'"""\n'
                       for name, value in literals.items())
    adapter = b"".join((
        literals["OLD_FLAG_BLOCK"], literals["OLD_ERROR_BLOCK"],
        literals["OLD_PATTERN_BLOCK"], b"from candidates import _rust_bridge\n",
        b"import unicodedata\n", b"class RegexFlag(enum.IntFlag):\n",
        b"    VERBOSE = X = 64\n", b"class _Native:\n",
        b"    def compile(self, pattern, flags):\n", ORIGINAL_COMPILE,
        b"        compiled = self.native_compile(pattern, flags, positions, values)\n",
        b"    def compile_scanner(self, patterns, flags):\n", ORIGINAL_SCANNER_CALL,
        b"        compiled = _rust_bridge.compile_scanner(\n",
        ORIGINAL_NAMED_SCANNER, b"def _warn_ambiguous(pattern):\n",
        b"def _compile(pattern, flags):\n", b"    return _cache_pattern(key, result)\n",
    ))
    return adapter, repair


class WitnessPatternError(Exception):
    def __init__(self, message: str, pattern: str, position: int) -> None:
        super().__init__(message)
        self.msg, self.pattern, self.pos = message, pattern, position


KNOWN_NAMES = {
    "LATIN SMALL LETTER A": "a",
    "LATIN CAPITAL LETTER A": "A",
    "BLACK HEART SUIT": "♥",
    "MULTI CODEPOINT": "ab",
}


def witness(pattern: str | bytes, flags: int = 0,
            lookups: list[str] | None = None) -> list[tuple[int, int]]:
    if isinstance(pattern, bytes):
        return []
    found: list[tuple[int, int]] = []
    index, verbose, scopes, in_class, class_start = 0, bool(flags & VERBOSE), [], False, -1
    while index < len(pattern):
        character = pattern[index]
        if character == "\\":
            slash = index
            index += 1
            if pattern[index:index + 2] != "N{":
                index += bool(pattern[index:index + 1])
                continue
            close = pattern.find("}", index + 2)
            if close == index + 2 or (close < 0 and index + 2 == len(pattern)):
                raise WitnessPatternError("missing character name", pattern, slash + 3)
            if close < 0:
                raise WitnessPatternError("missing }, unterminated name", pattern, slash + 3)
            name = pattern[index + 2:close]
            if lookups is not None:
                lookups.append(name)
            resolved = KNOWN_NAMES.get(name)
            if resolved is None or len(resolved) != 1:
                raise WitnessPatternError(f"undefined character name {name!r}", pattern, slash)
            found.append((slash, ord(resolved)))
            index = close + 1
            continue
        if in_class:
            if character == "]" and index > class_start:
                in_class = False
            index += 1
            continue
        if verbose and character == "#":
            newline = pattern.find("\n", index + 1)
            if newline < 0:
                break
            index = newline + 1
            continue
        if character == "[":
            in_class, class_start = True, index + 1
            if pattern[class_start:class_start + 1] == "^":
                class_start += 1
            index += 1
            continue
        if character == "(":
            if pattern[index:index + 3] == "(?#":
                close = pattern.find(")", index + 3)
                index = len(pattern) if close < 0 else close + 1
                continue
            if pattern[index:index + 2] == "(?":
                marker_position = index + 2
                while marker_position < len(pattern) \
                        and pattern[marker_position] in "aiLmsux-":
                    marker_position += 1
                if marker_position > index + 2 \
                        and pattern[marker_position:marker_position + 1] in (":", ")"):
                    enabled, _, disabled = pattern[index + 2:marker_position].partition("-")
                    scoped = verbose
                    if "x" in enabled:
                        scoped = True
                    if "x" in disabled:
                        scoped = False
                    if pattern[marker_position] == ")":
                        verbose, index = scoped, marker_position + 1
                        continue
                    scopes.append(verbose)
                    verbose, index = scoped, marker_position + 1
                    continue
            scopes.append(verbose)
            index += 1
            continue
        if character == ")" and scopes:
            verbose = scopes.pop()
        index += 1
    return found


PUBLIC_DATASETS = (
    ("text.comment.inline_unknown_named_unicode",
     r"(?# \N{NO SUCH PUBLIC CHARACTER})(?P<word>a)(?P<number>\d*)", 0),
    ("text.comment.global_verbose_unknown_named_unicode",
     r"# \N{NO SUCH PUBLIC CHARACTER}" + "\n"
     + r"(?P<word>a)(?P<number>\d*)", VERBOSE),
    ("text.comment.scoped_verbose_unknown_named_unicode",
     r"(?x:# \N{NO SUCH PUBLIC CHARACTER}" + "\n"
     + r"(?P<word>a)(?P<number>\d*))", 0),
)


def semantic_tests() -> dict[str, object]:
    cases, failures = 0, 0

    def accepted(pattern: str | bytes, flags: int,
                 expected: list[tuple[int, int]], names: list[str]) -> None:
        nonlocal cases
        observed: list[str] = []
        require(witness(pattern, flags, observed) == expected and observed == names,
                "preserve comments, flags, scopes, classes, active names, and bytes")
        cases += 1

    def rejected(pattern: str, flags: int, message: str, position: int) -> None:
        nonlocal cases, failures
        try:
            witness(pattern, flags)
        except WitnessPatternError as error:
            require(error.msg == message and error.pattern is pattern and error.pos == position,
                    "preserve the exact active Unicode error and original pattern identity")
            cases += 1
            failures += 1
            return
        raise FreezeError("an active malformed Unicode escape incorrectly passed")

    known = r"\N{LATIN SMALL LETTER A}"
    capital = r"\N{LATIN CAPITAL LETTER A}"
    unknown = r"\N{NO SUCH PUBLIC CHARACTER}"
    malformed = (unknown, r"\N{}", r"\N{", r"\N{UNTERMINATED")
    for value in malformed:
        for ordinal in range(24):
            prefix, suffix = "a" * (ordinal % 5), "z" * (ordinal // 5)
            inline = prefix + "(?# " + value + " " + suffix + ")" + known
            accepted(inline, ordinal % 2 * VERBOSE,
                     [(inline.index(known), ord("a"))], ["LATIN SMALL LETTER A"])
            global_comment = prefix + "# " + value + " " + suffix + "\n" + known
            accepted(global_comment, VERBOSE,
                     [(global_comment.index(known), ord("a"))], ["LATIN SMALL LETTER A"])
            scoped = prefix + "(?x:# " + value + " " + suffix + "\n" + known + ")"
            accepted(scoped, ordinal % 2 * VERBOSE,
                     [(scoped.index(known), ord("a"))], ["LATIN SMALL LETTER A"])
    for ordinal in range(96):
        payload = malformed[ordinal % len(malformed)].encode("ascii")
        accepted(b"(?x:# " + payload + b"\n[a#])", VERBOSE if ordinal % 2 else 0,
                 [], [])
    for outer in ("x", "-x", "imx-s", "im-x"):
        for inner in ("x", "-x", "ix-m", "i-x", "i", "s-m"):
            for initial in (0, VERBOSE):
                pattern = ("(?" + outer + ":(?" + inner + ":# " + unknown
                           + "\n" + known + ")" + capital + ")" + known)
                enabled, _, disabled = inner.partition("-")
                inner_verbose = ("x" in enabled
                                 or "x" not in disabled
                                 and ("x" in outer.partition("-")[0]
                                      or "x" not in outer.partition("-")[2]
                                      and bool(initial & VERBOSE)))
                if inner_verbose:
                    accepted(pattern, initial,
                             [(pattern.index(known), ord("a")),
                              (pattern.index(capital), ord("A")),
                              (pattern.rindex(known), ord("a"))],
                             ["LATIN SMALL LETTER A", "LATIN CAPITAL LETTER A",
                              "LATIN SMALL LETTER A"])
                else:
                    rejected(pattern, initial,
                             "undefined character name 'NO SUCH PUBLIC CHARACTER'",
                             pattern.index(unknown))
    for ordinal in range(40):
        pattern = "(?x)" + "a" * (ordinal % 4) + "# " + unknown + "\r\n" + known
        accepted(pattern, 0, [(pattern.index(known), ord("a"))],
                 ["LATIN SMALL LETTER A"])
        pattern = "(?i-x:" + r"\#" + known + ")"
        accepted(pattern, VERBOSE, [(pattern.index(known), ord("a"))],
                 ["LATIN SMALL LETTER A"])
    for pattern in ("[#" + known + "]", "[^#" + known + "]",
                    "[]#" + known + "]", "[^]#" + known + "]",
                    "[" + r"\]" + "#" + known + "]",
                    "(?x:[#" + known + "])" + capital):
        expected = [(pattern.index(known), ord("a"))]
        names = ["LATIN SMALL LETTER A"]
        if capital in pattern:
            expected.append((pattern.index(capital), ord("A")))
            names.append("LATIN CAPITAL LETTER A")
        for flags in (0, VERBOSE, VERBOSE | 2, VERBOSE | 256):
            accepted(pattern, flags, expected, names)
    for pattern, flags in ((r"\\N{NO SUCH PUBLIC CHARACTER}" + known, 0),
                           (r"\#" + known, VERBOSE),
                           (r"\(" + known + r"\)", VERBOSE),
                           (r"\[" + known + r"\]", VERBOSE),
                           (r"\ " + known, VERBOSE),
                           ("\\" + "\n" + known, VERBOSE)):
        accepted(pattern, flags, [(pattern.index(known), ord("a"))],
                 ["LATIN SMALL LETTER A"])
    for flags in (0, 2, 32, 64, 66, 96, 256, 320, -1):
        for prefix in ("", "a", "(?:", "(?i:"):
            pattern = prefix + known + (")" if prefix.endswith(":") else "")
            accepted(pattern, flags, [(pattern.index(known), ord("a"))],
                     ["LATIN SMALL LETTER A"])
    for pattern, flags, message, position in (
            (r"\N{}", 0, "missing character name", 3),
            (r"\N{", 0, "missing character name", 3),
            (r"x\N{BROKEN", 0, "missing }, unterminated name", 4),
            (unknown, 0, "undefined character name 'NO SUCH PUBLIC CHARACTER'", 0),
            (r"\N{MULTI CODEPOINT}", 0,
             "undefined character name 'MULTI CODEPOINT'", 0),
            ("#" + unknown, 0,
             "undefined character name 'NO SUCH PUBLIC CHARACTER'", 1),
            (r"\#" + unknown, VERBOSE,
             "undefined character name 'NO SUCH PUBLIC CHARACTER'", 2),
            ("[#" + unknown + "]", VERBOSE,
             "undefined character name 'NO SUCH PUBLIC CHARACTER'", 2),
            ("(?-x:#" + unknown + ")", VERBOSE,
             "undefined character name 'NO SUCH PUBLIC CHARACTER'", 6)):
        rejected(pattern, flags, message, position)
    accepted("# " + unknown, VERBOSE, [], [])
    accepted("(?# " + unknown, 0, [], [])
    accepted("(?x:# " + unknown, 0, [], [])
    counts = {"comment_only": 0, "scanner_overlap": 0, "substitution_overlap": 0}
    for name, pattern, flags in PUBLIC_DATASETS:
        for category, amount in (("comment_only", 99), ("scanner_overlap", 5),
                                 ("substitution_overlap", 4)):
            for _ordinal in range(amount):
                names: list[str] = []
                require(witness(pattern, flags, names) == [] and names == [],
                        "ignore every one of the 324 frozen public comment rows")
                counts[category] += 1
                cases += 1
        require(sum(counts.values()) % 108 == 0,
                "retain exactly 108 comment records per authenticated public dataset")
    require(counts == {"comment_only": COMMENT_ONLY, "scanner_overlap": SCANNER_OVERLAP,
                       "substitution_overlap": SUBSTITUTION_OVERLAP}
            and sum(counts.values()) == TARGETED and cases >= 800 and failures >= 15,
            "preserve all 324 rows, 297 independent rows, 27 overlaps, and active errors")
    return {"semantic_case_count": cases, "active_error_case_count": failures,
            "public_targeted_case_count": TARGETED,
            "independent_comment_only_case_count": COMMENT_ONLY,
            "scanner_overlap_case_count": SCANNER_OVERLAP,
            "substitution_overlap_case_count": SUBSTITUTION_OVERLAP,
            "nested_scopes_preserved": True, "bytes_patterns_unchanged": True,
            "active_named_error_offsets_preserved": True,
            "external_matching_packages_imported": 0}


def hostile_tests(wall: SourceWall) -> dict[str, object]:
    require(not wall.input_authorized and INPUT not in wall.allowed,
            "reject premature candidate authorization before hostile controls")
    original, repair = synthetic_material()
    result = compose(original, repair)
    require(len(result) > len(original), "compose all seven frozen synthetic correction sites")
    rejected = 0

    def reject(callback, label: str) -> None:
        nonlocal rejected
        try:
            callback()
        except (FreezeError, OSError, TypeError, ValueError, WitnessPatternError):
            rejected += 1
            return
        raise FreezeError("hostile corrected-comment control incorrectly passed: " + label)

    for name in REPAIR_NAMES:
        signature = name.encode("ascii") + b' = b"""'
        reject(lambda item=signature: compose(original, repair.replace(item, b"", 1)),
               "missing historical private correction literal")
        reject(lambda item=signature: compose(original, repair.replace(item, item * 2, 1)),
               "duplicated historical private correction literal")
    blocks = extract_repair_literals(repair)
    for name in ("OLD_FLAG_BLOCK", "OLD_ERROR_BLOCK", "OLD_PATTERN_BLOCK"):
        reject(lambda item=blocks[name]: compose(original.replace(item, b"", 1), repair),
               "missing previous public flags, error, or representation repair")
        reject(lambda item=blocks[name]: compose(original.replace(item, item * 2, 1), repair),
               "duplicated previous public flags, error, or representation repair")
    for site in (ORIGINAL_COMPILE, ORIGINAL_SCANNER_CALL, ORIGINAL_NAMED_SCANNER):
        reject(lambda item=site: compose(original.replace(item, b"", 1), repair),
               "missing complete lexical call or helper")
        reject(lambda item=site: compose(original.replace(item, item * 2, 1), repair),
               "duplicated complete lexical call or helper")
        for offset in range(0, len(site), max(1, len(site) // 12)):
            changed = site[:offset] + bytes((site[offset] ^ 1,)) + site[offset + 1:]
            reject(lambda old=site, new=changed:
                   compose(original.replace(old, new, 1), repair),
                   "single-byte lexical source drift")
    for anchor, _count in PRESERVED_ANCHORS:
        reject(lambda item=anchor: compose(original.replace(item, b"", 1), repair),
               "missing native bridge, flags, warning, or cache anchor")
    for path in (INPUT, TARGET,
                 "candidates/rust/variants/verbose_named_escape_semantics_v1/rust_candidate.py",
                 "candidates/_rust_engine.so",
                 "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
                 "oracle/phase3/expanded-sealed-holdout-v2.json",
                 "oracle/phase3/expanded-sealed-holdout-v3.json",
                 "oracle/phase2/evidence/native-source-build-v30-rust-phase2-v30-rust-"
                 "complete-semantic-source-root-provenance.json.gz",
                 ".git/config"):
        reject(lambda value=path: wall.parent(value),
               "forbidden candidate, native, final, compressed archive, or Git owner")
    reject(lambda: wall.native_open(ROOT + "/" + INPUT, wall.file_flags()),
           "saved unticketed canonical candidate primitive")
    reject(lambda: builtins.open(ROOT + "/" + INPUT), "high-level canonical candidate")
    reject(lambda: os.open(ROOT + "/" + INPUT, wall.file_flags()),
           "patched canonical candidate primitive")
    reject(lambda: os.mkdir(TARGET_DIRECTORY, 0o700), "workspace directory mutation")
    reject(lambda: time.time(), "wall clock")
    reject(lambda: time.perf_counter(), "performance clock")
    reject(lambda: sys.audit("import", "re", None, None, None, None), "stdlib matcher")
    reject(lambda: sys.audit("import", "regex", None, None, None, None), "external regex")
    reject(lambda: sys.audit("ctypes.dlopen", "candidate.so"), "native loading")
    reject(lambda: sys.audit("subprocess.Popen", "cc", (), None, None), "compilation")
    reject(lambda: sys.audit("socket.connect", None, None), "network")
    semantics = semantic_tests()
    require(rejected >= 90 and wall.source_reads == 0 and not wall.input_authorized
            and wall.workspace_mutations == 0,
            "run exhaustive hostile controls before reading or writing a candidate")
    no_matching_imports()
    return {"hostile_controls_rejected": rejected, "historical_repair_site_count": 4,
            "new_comment_repair_site_count": 3, "corrections_commute": True,
            "candidate_source_reads": 0, "workspace_mutations": 0,
            "semantic_witness": semantics}


def arguments(values: list[str]) -> dict[str, object]:
    require(type(values) is list and all(type(item) is str for item in values),
            "require explicit immutable source-gate arguments")
    flags = {"--self-test", "--verify-frozen-context", "--verify-source", "--apply",
             "--root-authorized"}
    paired = {"--source-sha256", "--protocol-sha256", "--contract-sha256",
              "--frozen-commit", "--pushed-commit"}
    parsed: dict[str, object] = {}
    index = 0
    while index < len(values):
        item = values[index]
        require(item in flags or item in paired, "reject unknown frozen option: " + item)
        require(item not in parsed, "reject duplicate frozen option: " + item)
        if item in flags:
            parsed[item] = True
            index += 1
        else:
            require(index + 1 < len(values), "missing complete frozen option: " + item)
            parsed[item] = values[index + 1]
            index += 2
    modes = [item for item in ("--self-test", "--verify-frozen-context", "--verify-source",
                               "--apply") if parsed.get(item) is True]
    require(len(modes) == 1, "require exactly one source-only or root-only mode")
    mode = modes[0]
    if mode == "--self-test":
        require(set(parsed) == {mode}, "self-test has no owner or root options")
    elif mode in ("--verify-frozen-context", "--verify-source"):
        require(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                                "--contract-sha256"},
                "source verification requires exactly three full owner digests")
    else:
        require(set(parsed) == {mode, "--source-sha256", "--protocol-sha256",
                                "--contract-sha256", "--root-authorized",
                                "--frozen-commit", "--pushed-commit"},
                "root application requires explicit authorization and pushed commitment")
        for name in ("--frozen-commit", "--pushed-commit"):
            commit = parsed[name]
            require(type(commit) is str and len(commit) == 40
                    and all(char in "0123456789abcdef" for char in commit),
                    "require one complete lowercase pushed commit: " + name)
        require(parsed["--frozen-commit"] == parsed["--pushed-commit"],
                "freeze must be committed and pushed before root-only materialization")
    for item in ("--source-sha256", "--protocol-sha256", "--contract-sha256"):
        if item in parsed:
            checked_sha(parsed[item], item)
    return parsed


def effects(wall: SourceWall, mode: str) -> dict[str, object]:
    return {"mode": mode, "approved_public_owner_reads": wall.public_reads,
            "candidate_source_files_read": wall.source_reads,
            "candidate_imports": 0, "candidate_executions": 0,
            "candidate_workers_started": 0, "compiler_processes_started": 0,
            "native_binary_files_opened": 0, "native_libraries_loaded": 0,
            "compressed_archives_opened": 0, "compressed_archives_inflated": 0,
            "proposals_opened": 0, "final_cases_generated": 0,
            "final_cases_opened": 0, "clock_samples": 0,
            "network_requests": 0, "workspace_mutations": wall.workspace_mutations,
            "candidate_correctness": "NOT MEASURED", "candidate_matching": "NOT RUN",
            "runtime_non_delegation": "NOT ESTABLISHED", "candidate_qualified": False,
            "performance": "NOT MEASURED", "winner_selected": False,
            "retired_final_global_unopened_claim": False,
            "final_holdout": "INVALIDATED; REKEYED SUCCESSOR REQUIRED"}


def authenticate_owners(payloads: dict[str, bytes], source_sha: str,
                        protocol_sha: str, contract_sha: str) -> None:
    contract = payloads["contract"]
    for key, value in (("schema", SCHEMA), ("source_sha256", source_sha),
                       ("protocol_sha256", protocol_sha), ("input_sha256", INPUT_SHA),
                       ("private_corrected_adapter_sha256", CORRECTED_SHA),
                       ("standalone_comment_adapter_sha256", STANDALONE_SHA),
                       ("target_sha256", OUTPUT_SHA), ("target_bytes", OUTPUT_BYTES),
                       ("targeted_public_mismatch_count", TARGETED),
                       ("independent_comment_only_mismatch_count", COMMENT_ONLY),
                       ("scanner_overlap_count", SCANNER_OVERLAP),
                       ("substitution_overlap_count", SUBSTITUTION_OVERLAP),
                       ("historical_private_repair_count", 4),
                       ("comment_repair_count", 3),
                       ("corrections_commute", True),
                       ("candidate_qualified", False)):
        marker(contract, key, value)
    repair_contract = payloads["repair_contract"]
    marker(repair_contract, "sha256", CORRECTED_SHA)
    marker(repair_contract, "bytes", CORRECTED_BYTES)
    marker(repair_contract, "sha256", INPUT_SHA)
    application = payloads["comment_application"]
    for key, value in (("input_sha256", INPUT_SHA), ("target_sha256", STANDALONE_SHA),
                       ("target_bytes", STANDALONE_BYTES),
                       ("targeted_public_mismatch_count", TARGETED),
                       ("disjoint_comment_only_mismatch_count", COMMENT_ONLY),
                       ("scanner_overlap_count", SCANNER_OVERLAP),
                       ("substitution_overlap_count", SUBSTITUTION_OVERLAP)):
        marker(application, key, value)
    ledger = payloads["original_v25"]
    marker(ledger, "candidate_status", "FAIL")
    marker(ledger, "semantic_mismatch_count", 1352)
    marker(ledger, "corrected_public_adapter_sha256", CORRECTED_SHA)
    for role in ("public_v26", "public_v27", "public_v28"):
        data = payloads[role]
        marker(data, "candidate_qualified", False)
        require(CORRECTED_SHA.encode("ascii") in data,
                "authenticate the corrected private adapter in every public receipt")
        require(b"10434" in data and b"1145" in data,
                "authenticate complete public denominator and observed mismatches")
    for role in ("v30_publication", "v30_root"):
        data = payloads[role]
        marker(data, "status", "PASS")
        marker(data, "actual_compiler_process_count", 28)
        marker(data, "corrected_public_adapter_sha256", CORRECTED_SHA)
        marker(data, "corrected_public_adapter_bytes", CORRECTED_BYTES)
        marker(data, "latest_v25_original_case_execution_denominator", 31237)
        marker(data, "latest_public_10434_mismatch_count", PUBLIC_MISMATCHES)
        marker(data, "retired_v2_holdout_global_unopened_claim", False)
        marker(data, "candidate_qualified", False)
    marker(payloads["v30_publication"], "actual_completed_phase_count", 2)
    marker(payloads["v30_publication"], "external_cargo_dependency_count", 0)
    marker(payloads["v30_publication"], "build_status", "PASS")
    marker(payloads["v30_root"], "corrected_adapter_overlay_apply_count", 2)
    failed = payloads["failed_v1_receipt"]
    marker(failed, "schema",
           "rebar-owned-rust-corrected-comment-adapter-v1-root-preapplication-failure")
    marker(failed, "status", "FAIL")
    marker(failed, "failure_phase", "PREAPPLICATION_SOURCE_HOSTILE_CONTROL")
    marker(failed, "controller_source_sha256",
           "0f048599182b69965c88677cbfb9ccb162a9d9d943426d2b607503e48a797d69")
    marker(failed, "protocol_sha256",
           "e04e29068703fd8580beeeb2463df75ff7af68008f811e2e8a053cf4a91112f7")
    marker(failed, "contract_sha256",
           "ac99c411cd2cfcfcd66df63aff03c79ebedd9e41681b881eb78e7aa25252ee61")
    marker(failed, "candidate_target_created", False)
    marker(failed, "candidate_source_materialized", False)
    marker(failed, "candidate_executions", 0)
    marker(failed, "final_cases_generated", 0)
    marker(contract, "predecessor_v1_failure_receipt_sha256",
           "7bc692fcf17780ed05ca49c982536849212e1909f73337764b2392ea3ee9a37b")
    marker(contract, "candidate_authorization_deferred_until_after_hostile_controls", True)
    require(contract_sha == digest(contract),
            "retain caller-pinned exact corrected-comment frozen contract")


def main(values: list[str]) -> dict[str, object]:
    verify_runtime()
    options = arguments(values)
    apply = options.get("--apply") is True
    no_matching_imports()
    wall = SourceWall(apply)
    wall.install()
    if options.get("--self-test") is True:
        controls = hostile_tests(wall)
        require(wall.root is None and wall.public_reads == 0 and wall.source_reads == 0
                and wall.workspace_mutations == 0,
                "self-test must not open an owner, candidate, or workspace descriptor")
        return {"schema": SCHEMA + "-self-test", "status": "PASS",
                "synthetic_controls": controls, "effects": effects(wall, "SELF-TEST")}
    source_sha = options["--source-sha256"]
    protocol_sha = options["--protocol-sha256"]
    contract_sha = options["--contract-sha256"]
    assert isinstance(source_sha, str) and isinstance(protocol_sha, str)
    assert isinstance(contract_sha, str)
    wall.open_root()
    payloads = {"source": wall.read(SOURCE, None, None, source_sha),
                "protocol": wall.read(PROTOCOL, None, None, protocol_sha),
                "contract": wall.read(CONTRACT, None, None, contract_sha)}
    for role, relative, sha, count, inode in OWNERS:
        payloads[role] = wall.read(relative, count, inode, sha)
    authenticate_owners(payloads, source_sha, protocol_sha, contract_sha)
    require(wall.public_reads == len(OWNERS) + 3 and wall.source_reads == 0
            and wall.workspace_mutations == 0,
            "authenticate only all frozen plaintext owners and no candidate")
    controls = hostile_tests(wall)
    if not apply:
        return {"schema": SCHEMA + "-verification",
                "status": "PASS; SOURCE FROZEN; CANDIDATE NOT OPENED",
                "source_sha256": source_sha, "protocol_sha256": protocol_sha,
                "contract_sha256": contract_sha,
                "authenticated_historical_owner_count": len(OWNERS),
                "predicted_target_path": TARGET, "predicted_target_sha256": OUTPUT_SHA,
                "predicted_target_bytes": OUTPUT_BYTES,
                "synthetic_controls": controls, "effects": effects(wall, "SOURCE FREEZE")}
    wall.authorize_input()
    original = wall.read(INPUT, INPUT_BYTES, INPUT_INODE, INPUT_SHA)
    corrected = compose(original, payloads["repair_source"], exact=True)
    wall.materialize(corrected)
    no_matching_imports()
    require(wall.source_reads == 1 and wall.workspace_mutations == 2,
            "materialize exactly one fresh directory and one composed adapter")
    return {"schema": SCHEMA + "-root-materialization",
            "status": "PASS; EXACT SEVEN CORRECTIONS; NOT BUILT; NOT RUN",
            "frozen_commit": options["--frozen-commit"],
            "pushed_commit": options["--pushed-commit"],
            "source_sha256": source_sha, "protocol_sha256": protocol_sha,
            "contract_sha256": contract_sha, "input_path": INPUT,
            "input_sha256": INPUT_SHA, "input_bytes": INPUT_BYTES,
            "private_corrected_adapter_sha256": CORRECTED_SHA,
            "private_corrected_adapter_bytes": CORRECTED_BYTES,
            "standalone_comment_adapter_sha256": STANDALONE_SHA,
            "standalone_comment_adapter_bytes": STANDALONE_BYTES,
            "target_path": TARGET, "target_sha256": OUTPUT_SHA,
            "target_bytes": OUTPUT_BYTES, "historical_private_repair_count": 4,
            "comment_repair_count": 3, "corrections_commute": True,
            "targeted_public_mismatch_count": TARGETED,
            "independent_comment_only_mismatch_count": COMMENT_ONLY,
            "scanner_overlap_count": SCANNER_OVERLAP,
            "substitution_overlap_count": SUBSTITUTION_OVERLAP,
            "effects": effects(wall, "ROOT-ONLY EXCLUSIVE MATERIALIZATION")}


if __name__ == "__main__":
    try:
        outcome = main(sys.argv[1:])
    except (FreezeError, OSError, UnicodeError, ValueError) as error:
        sys.stderr.write("rust-corrected-comment-adapter-v2: " + str(error) + "\n")
        raise SystemExit(2)
    sys.stdout.write(canonical(outcome) + "\n")
