#!/usr/bin/env python3
"""Freeze an exact commuting composition of two first-party Rust improvements.

Verification owns only bounded authenticated source and already-public evidence.
An always-on descriptor wall remains active even while root exclusively creates
the two independently predicted source outputs after the freeze is pushed.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("combined first-party source freeze must not import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/apply_owned_rust_combined_search_compiler_fastpath_v2.py"
PROTOCOL = "oracle/phase2/RUST-COMBINED-SEARCH-COMPILER-FASTPATH-V2.md"
CONTRACT = "oracle/phase2/rust-combined-search-compiler-fastpath-v2.json"
PROPOSAL = "oracle/phase3/expanded-sealed-holdout-v2.json"
PARENT = "candidates/rust/variants"
DIRECTORY = "combined_search_compiler_fastpath_v2"
LIB_TARGET = PARENT + "/" + DIRECTORY + "/lib.rs"
SEARCH_TARGET = PARENT + "/" + DIRECTORY + "/search.rs"
SCHEMA = "rebar-first-party-rust-combined-search-compiler-fastpath-v2"
DEVICE = 2064
PARENT_INODE = 524946
PROPOSAL_INODE = 525920
PROPOSAL_BYTES = 15561
PROPOSAL_SHA256 = "5d9fa3920c1dcabc92a3521d742cd10ec399cff1a979b71ac079daba6f92cba0"
LIB_SHA256 = "c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee"
LIB_BYTES = 189423
SEARCH_SHA256 = "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7"
SEARCH_BYTES = 24305
MAX_OWNER_BYTES = 1_048_576
NOT_MEASURED = "NOT MEASURED"

# role, repository-relative owner, exact SHA-256, exact bytes, exact inode
OWNERS = (
    ("goal", "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044),
    ("cargo_manifest", "candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, 428094),
    ("cargo_lock", "candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, 428098),
    ("canonical_lib", "candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967, 428096),
    ("canonical_search", "candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773, 429682),
    ("compiler_source", "tools/apply_owned_rust_compiler_allocation_fastpath_v1.py", "13ad7948ba05a057f1c93f404998d72217ad42a8a93da8d71f9a3f7b5a41d1bf", 75362, 429789),
    ("compiler_protocol", "oracle/phase2/RUST-COMPILER-ALLOCATION-FASTPATH-V1.md", "dd1516d037aa9f56458d0bbcb61ee36a283463c7fc38bb9372ac55c35112382c", 5306, 526090),
    ("compiler_contract", "oracle/phase2/rust-compiler-allocation-fastpath-v1.json", "915170849be177d17c26b135b6fb8792981ffef35d6876bc4c073237d0f58f55", 9667, 526100),
    ("compiler_application", "oracle/phase2/evidence/rust-compiler-allocation-fastpath-v1-application.json", "37f9a96e511095461af237e3fcf7d9e674995c274e7fe5c69368d59afeddccc6", 2143, 526158),
    ("compiler_variant", "candidates/rust/variants/compiler_allocation_fastpath_v1/lib.rs", "64228afb698f5326e6a30fd93c2ea27bd81653ecdd4a4a8e2b0dda5983e895b6", 178021, 526157),
    ("anchor_source", "tools/apply_owned_rust_mandatory_anchor_search_v1.py", "d118af0c0da3b058fc8d40a59d47090a97fd8838fcbdb0fba36bcd0271da2eff", 74375, 429756),
    ("anchor_protocol", "oracle/phase2/RUST-MANDATORY-ANCHOR-SEARCH-V1.md", "85d65a26042f8e084f52a4037ad2267dd4f59e1e6166a9694b56703960af148e", 3253, 526101),
    ("anchor_contract", "oracle/phase2/rust-mandatory-anchor-search-v1.json", "25a7a5ea578c2c6a54eae6635c0869bdc3eaed6d1a8cce46b77c1d752ea04249", 1591, 526102),
    ("anchor_application", "oracle/phase2/evidence/rust-mandatory-anchor-search-v1-application.json", "c4396052f94a76f67088678cd0a5176bb70c1d917675fbc03353806047ca20bb", 1871, 526183),
    ("anchor_lib", "candidates/rust/variants/mandatory_anchor_search_v1/lib.rs", "5fa8c47c88c1f5d830a59735946378910374afab6f1558d281f0254207ad5e84", 189369, 526181),
    ("anchor_search", "candidates/rust/variants/mandatory_anchor_search_v1/search.rs", SEARCH_SHA256, SEARCH_BYTES, 526182),
    ("capture_clamp_bridge", "candidates/rust/variants/capture_clamp_semantics_v1/py_bridge.c", "a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54", 178805, 526064),
    ("actual_v24_failure", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v24-rust-capture-shape-v2-root-provenance-original-p0-v24-failures-publication-receipt.json", "5acd8dee2a515af56306e61f6ae8774c567f1f47e0ef1930a17e6809c2aafa09", 11832, 525952),
    ("actual_v25_safe_build", "oracle/phase2/evidence/native-source-build-v25-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-publication-receipt.json", "55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc", 5231, 526084),
    ("public_profile_contract", "oracle/phase3/rust-public-profile-v1.json", "b791b141eabbf6eb8a67484f5deb82bb41e324aedbdfe5b53a98ebc1553372c5", 1797, 525928),
    ("public_python_correctness", "experiments/rust_public_profile_v1/public-run-001/stdlib.correctness.raw.json", "efe0a3cc37194290b9577d5bd4f502a5c482016bc2b8ae90acec6254545b5381", 445036, 526005),
    ("public_rust_correctness", "experiments/rust_public_profile_v1/public-run-001/rust.correctness.raw.json", "8774ad035e17126252803e75494a80d376386a85e13c46cb3e0380b82dae89b0", 445394, 526006),
    ("public_paired_rows", "experiments/rust_public_profile_v1/public-run-001/paired-timing.raw.json", "3da06bdb04ace9897d359aaa962ca412f3e9260a5c1a337703e0aa35567b6b85", 504907, 526015),
    ("failed_v1_source", "tools/apply_owned_rust_combined_search_compiler_fastpath_v1.py", "a7c6c4f8bd8eb1dd3e9439901f4dcb765b73cd8623e27fa6fb3803045995e35c", 80291, 430776),
    ("failed_v1_protocol", "oracle/phase2/RUST-COMBINED-SEARCH-COMPILER-FASTPATH-V1.md", "b46c64cf620f62f04322417c329f13523c147249aa0b2120e48e7f80f6f9de03", 4681, 526292),
    ("failed_v1_contract", "oracle/phase2/rust-combined-search-compiler-fastpath-v1.json", "07a1d0720202f66a345041ae56911cd0e1dbf6e1ac5c41c1641876bd7eea3387", 11789, 524808),
    ("failed_v1_application", "oracle/phase2/evidence/rust-combined-search-compiler-fastpath-v1-application-failure.json", "6427758e2e45ca77aede33aad02e2ea72d50508f025f81003d9046a327d7ca97", 1163, 524864),
)


class FreezeError(Exception):
    """A frozen owner, composition proof, or physical source wall was violated."""


def require(condition: object, explanation: str) -> None:
    if condition is not True:
        raise FreezeError(explanation)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash complete immutable genuine bytes")
    return hashlib.sha256(raw).hexdigest()


def exact_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value)
            and len(set(value)) > 1, "require a real lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def exact_commit(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(char in "0123456789abcdef" for char in value)
            and len(set(value)) > 1, "require a full pushed commit hash: " + label)
    assert isinstance(value, str)
    return value


def clean_imports() -> None:
    forbidden = ("re", "_sre", "regex", "regex._regex", "re2", "pcre", "pcre2",
                 "oniguruma", "ctypes", "subprocess", "socket", "threading",
                 "multiprocessing", "concurrent.interpreters", "candidates", "rebar")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject an imported matcher, candidate, native loader, worker, or network")


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= 64, "reject excessive frozen JSON nesting")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
                   "\n": "\\n", "\r": "\\r", "\t": "\\t"}
        require(not any(0xD800 <= ord(item) <= 0xDFFF for item in value),
                "reject an unpaired frozen JSON surrogate")
        return '"' + "".join(escapes.get(item, "\\u" + format(ord(item), "04x")
                                         if ord(item) < 32 else item)
                              for item in value) + '"'
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "reject a nontext JSON key")
        return "{" + ",".join(canonical(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise FreezeError("reject a nonfinite or unsupported frozen JSON value")


def document(value: object) -> bytes:
    return (canonical(value) + "\n").encode("utf-8")


class SourceWall:
    """One-way owner descriptors plus exactly one root-owned two-file publication."""

    def __init__(self, apply: bool) -> None:
        self.apply = apply
        self.allowed = frozenset(
            (ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL, ROOT + "/" + CONTRACT)
            + tuple(ROOT + "/" + row[1] for row in OWNERS)
        )
        self.transformers = frozenset((ROOT + "/" + OWNERS[5][1],
                                      ROOT + "/" + OWNERS[10][1]))
        self.proposal = ROOT + "/" + PROPOSAL
        self.parent_path = ROOT + "/" + PARENT
        self.stage = "source"
        self.owners: set[int] = set()
        self.parent_fd: int | None = None
        self.child_fd: int | None = None
        self.outputs: dict[int, str] = {}
        self.opened_names: list[str] = []
        self.expected: dict[str, bytes] = {}
        self.written: dict[str, int] = {}
        self.synced: set[str] = set()
        self.child_synced = False
        self.parent_synced = False
        self.proposal_stat_count = 0
        self.proposal_open_count = 0
        self.compile_name: str | None = None
        self.compile_raw: bytes | None = None
        self.pending_code: object | None = None
        self.compile_count = 0
        self.exec_count = 0
        self.blocked: dict[str, int] = {}
        self.installed = False

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise FreezeError("combined source wall rejected " + category)

    def owner_path(self, path: object) -> bool:
        return (type(path) is str and path in self.allowed
                and path.startswith(ROOT + "/") and path == os.path.normpath(path)
                and not any(piece in (".", "..") for piece in path.split("/"))
                and not path.endswith((".so", ".gz", ".er")))

    def temporary_file_flags(self, flags: object) -> bool:
        temporary = getattr(os, "O_TMPFILE", 0)
        return (type(flags) is int and type(temporary) is int and temporary != 0
                and flags & temporary == temporary)

    def directory_flags(self, flags: object) -> bool:
        required = os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
        destructive = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL
                       | os.O_TRUNC | os.O_APPEND)
        return (type(flags) is int and flags & required == required
                and not flags & destructive and not self.temporary_file_flags(flags))

    def output_flags(self, flags: object) -> bool:
        required = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        destructive = (os.O_RDWR | os.O_TRUNC | os.O_APPEND
                       | getattr(os, "O_DIRECTORY", 0))
        return (type(flags) is int and flags & required == required
                and not flags & destructive and not self.temporary_file_flags(flags))

    def audit(self, event: str, arguments: tuple[object, ...]) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else None
            destructive = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL
                           | os.O_TRUNC | os.O_APPEND
                           | getattr(os, "O_DIRECTORY", 0))
            if (self.owner_path(path) and type(flags) is int
                    and flags & getattr(os, "O_NOFOLLOW", 0)
                    and not flags & destructive and not self.temporary_file_flags(flags)):
                return
            if (self.apply and self.stage == "ready" and path == self.parent_path
                    and self.directory_flags(flags)):
                return
            if (self.apply and self.stage == "created" and path == DIRECTORY
                    and self.directory_flags(flags)):
                return
            if (self.apply and self.stage == "child" and path in ("lib.rs", "search.rs")
                    and self.output_flags(flags)
                    and path == ("lib.rs" if not self.opened_names else "search.rs")
                    and len(self.opened_names) < 2):
                return
            if path == self.proposal:
                self.deny("unopened-holdout-content")
            self.deny("unowned-source-native-archive-output-open")
        if event == "os.mkdir":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            directory = arguments[2] if len(arguments) > 2 else None
            if (self.apply and self.stage == "parent" and path == DIRECTORY
                    and mode == 0o700 and directory == self.parent_fd):
                return
            self.deny("unapproved-directory-mutation")
        if event == "compile":
            raw = arguments[0] if arguments else None
            filename = arguments[1] if len(arguments) > 1 else None
            expected_owner = (OWNERS[5] if self.compile_count == 0
                              else OWNERS[10] if self.compile_count == 1 else None)
            if (expected_owner is not None
                    and filename == ROOT + "/" + expected_owner[1]
                    and filename == self.compile_name and self.compile_name in self.transformers
                    and type(raw) is bytes and raw == self.compile_raw
                    and digest(raw) == expected_owner[2]
                    and self.exec_count == self.compile_count):
                self.compile_count += 1
                return
            self.deny("unapproved-dynamic-compile")
        if event == "exec":
            candidate = arguments[0] if arguments else None
            expected_owner = (OWNERS[5] if self.exec_count == 0
                              else OWNERS[10] if self.exec_count == 1 else None)
            if (expected_owner is not None and candidate is self.pending_code
                    and self.pending_code is not None and self.compile_count == self.exec_count + 1
                    and getattr(candidate, "co_filename", None)
                        == ROOT + "/" + expected_owner[1]
                    and getattr(candidate, "co_name", None) == "<module>"):
                self.exec_count += 1
                return
            self.deny("unapproved-dynamic-execution")
        if (event == "import" or event == "sys.addaudithook"
                or event.startswith(("subprocess.", "socket.", "ctypes.",
                                     "threading.", "multiprocessing.", "tempfile.",
                                     "time.", "_interpreters.", "cpython.PyInterpreterState",
                                     "os.exec", "os.spawn"))
                or event in ("marshal.loads", "code.__new__", "os.system", "os.fork",
                             "os.posix_spawn", "os.posix_spawnp", "os.rename", "os.replace",
                             "os.remove", "os.unlink", "os.rmdir", "os.chmod", "os.chown",
                             "os.link", "os.symlink", "os.truncate", "os.putenv",
                             "os.unsetenv", "os.urandom", "os.getrandom")):
            self.deny("candidate-native-process-clock-or-mutation")

    def forbidden(self, category: str):
        def reject(*_args: object, **_keywords: object) -> object:
            self.deny(category)
        return reject

    def install(self) -> None:
        require(not self.installed, "install the combined source wall exactly once")
        native_open = os.open
        native_read = os.read
        native_write = os.write
        native_fstat = os.fstat
        native_close = os.close
        native_fsync = os.fsync
        native_lstat = os.lstat
        native_mkdir = os.mkdir

        def guarded_open(path: object, flags: object, mode: int = 0o777,
                         *, dir_fd: object = None) -> int:
            require(type(flags) is int and type(mode) is int,
                    "reject malformed guarded source descriptor flags")
            read_owner = (dir_fd is None and self.owner_path(path)
                          and flags & getattr(os, "O_NOFOLLOW", 0)
                          and not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                                           | os.O_EXCL | os.O_TRUNC | os.O_APPEND
                                           | getattr(os, "O_DIRECTORY", 0))
                          and not self.temporary_file_flags(flags))
            parent = (self.apply and self.stage == "ready" and path == self.parent_path
                      and dir_fd is None and self.directory_flags(flags))
            child = (self.apply and self.stage == "created" and path == DIRECTORY
                     and dir_fd == self.parent_fd and self.directory_flags(flags))
            output = (self.apply and self.stage == "child" and dir_fd == self.child_fd
                      and path in ("lib.rs", "search.rs") and self.output_flags(flags)
                      and mode == 0o600
                      and path == ("lib.rs" if not self.opened_names else "search.rs")
                      and len(self.opened_names) < 2)
            if not any((read_owner, parent, child, output)):
                self.deny("unapproved-descriptor-open-or-dir-fd")
            descriptor = native_open(path, flags, mode, dir_fd=dir_fd)
            require(type(descriptor) is int and descriptor >= 0
                    and descriptor not in self.owners and descriptor not in self.outputs
                    and descriptor != self.parent_fd and descriptor != self.child_fd,
                    "reject a reused or invalid combined-source descriptor")
            if read_owner:
                self.owners.add(descriptor)
            elif parent:
                self.parent_fd = descriptor
                self.stage = "parent"
            elif child:
                self.child_fd = descriptor
                self.stage = "child"
            else:
                assert isinstance(path, str)
                self.outputs[descriptor] = path
                self.opened_names.append(path)
                self.written[path] = 0
            return descriptor

        def guarded_read(descriptor: object, count: object) -> bytes:
            if (type(descriptor) is not int or descriptor not in self.owners
                    or type(count) is not int or not 0 <= count <= MAX_OWNER_BYTES):
                self.deny("foreign-or-unbounded-descriptor-read")
            return native_read(descriptor, count)

        def guarded_write(descriptor: object, value: object) -> int:
            if (type(descriptor) is not int or descriptor not in self.outputs
                    or type(value) not in (bytes, memoryview)):
                self.deny("foreign-or-unapproved-descriptor-write")
            name = self.outputs[descriptor]
            raw = self.expected[name]
            offset = self.written[name]
            block = bytes(value)
            if not block or block != raw[offset:offset + len(block)]:
                self.deny("incorrect-or-unbounded-output-bytes")
            count = native_write(descriptor, value)
            require(type(count) is int and 0 < count <= len(block),
                    "reject a failed or oversized private source write")
            self.written[name] += count
            return count

        def guarded_fstat(descriptor: object) -> os.stat_result:
            if (type(descriptor) is not int or descriptor not in self.owners
                    and descriptor not in self.outputs
                    and descriptor != self.parent_fd and descriptor != self.child_fd):
                self.deny("foreign-descriptor-metadata")
            return native_fstat(descriptor)

        def guarded_close(descriptor: object) -> None:
            if type(descriptor) is not int:
                self.deny("foreign-descriptor-close")
            if descriptor in self.owners:
                self.owners.remove(descriptor)
            elif descriptor in self.outputs:
                name = self.outputs[descriptor]
                require(name in self.synced and self.written[name] == len(self.expected[name]),
                        "do not close an incomplete or unsynchronized output")
                del self.outputs[descriptor]
            elif descriptor == self.child_fd:
                require(self.child_synced and not self.outputs,
                        "synchronize both outputs and private directory before closing it")
                self.child_fd = None
            elif descriptor == self.parent_fd:
                require(self.parent_synced and self.child_fd is None,
                        "synchronize the parent after closing its private child")
                self.parent_fd = None
            else:
                self.deny("foreign-descriptor-close")
            native_close(descriptor)

        def guarded_fsync(descriptor: object) -> None:
            if not self.apply or type(descriptor) is not int:
                self.deny("foreign-descriptor-sync")
            if descriptor in self.outputs:
                name = self.outputs[descriptor]
                require(self.written[name] == len(self.expected[name]),
                        "do not synchronize an incomplete private output")
                native_fsync(descriptor)
                self.synced.add(name)
            elif descriptor == self.child_fd:
                require(self.opened_names == ["lib.rs", "search.rs"]
                        and self.synced == {"lib.rs", "search.rs"}
                        and not self.outputs and not self.child_synced,
                        "synchronize the private directory only after both complete files")
                native_fsync(descriptor)
                self.child_synced = True
            elif descriptor == self.parent_fd:
                require(self.child_synced and self.child_fd is None and not self.parent_synced,
                        "synchronize the parent only after publishing its complete child")
                native_fsync(descriptor)
                self.parent_synced = True
            else:
                self.deny("foreign-descriptor-sync")

        def guarded_lstat(path: object, *, dir_fd: object = None) -> os.stat_result:
            if path != self.proposal or dir_fd is not None or self.proposal_stat_count != 0:
                self.deny("foreign-or-repeated-holdout-metadata")
            result = native_lstat(path)
            self.proposal_stat_count += 1
            return result

        def guarded_mkdir(path: object, mode: int = 0o777,
                          *, dir_fd: object = None) -> None:
            if (not self.apply or self.stage != "parent" or path != DIRECTORY
                    or mode != 0o700 or dir_fd != self.parent_fd):
                self.deny("unapproved-private-variant-directory")
            native_mkdir(path, mode, dir_fd=dir_fd)
            self.stage = "created"

        invocation_authorized = self.apply

        def immutable_authority_audit(event: str, arguments: tuple[object, ...]) -> None:
            if self.apply is not invocation_authorized:
                self.deny("forged-root-publication-authority")
            self.audit(event, arguments)

        sys.addaudithook(immutable_authority_audit)
        native_module = sys.modules.get("posix")
        require(native_module is not None, "authenticate the already-loaded native OS module")
        builtins.open = self.forbidden("builtins-open")
        _io.open = self.forbidden("direct-_io-open")
        _io.FileIO = self.forbidden("direct-_io-fileio")
        io.open = self.forbidden("direct-io-open")
        io.FileIO = self.forbidden("direct-io-fileio")
        for module in (_io, io):
            if hasattr(module, "open_code"):
                setattr(module, "open_code", self.forbidden("direct-open-code"))
        os.open = guarded_open
        os.read = guarded_read
        os.write = guarded_write
        os.fstat = guarded_fstat
        os.close = guarded_close
        os.fsync = guarded_fsync
        os.lstat = guarded_lstat
        os.mkdir = guarded_mkdir
        native_module.open = guarded_open
        native_module.read = guarded_read
        native_module.write = guarded_write
        native_module.fstat = guarded_fstat
        native_module.close = guarded_close
        native_module.fsync = guarded_fsync
        native_module.lstat = guarded_lstat
        native_module.mkdir = guarded_mkdir
        for name in ("fdopen", "dup", "dup2", "stat", "readlink", "listdir", "scandir",
                     "walk", "fwalk", "access", "fork", "posix_spawn", "posix_spawnp",
                     "system", "makedirs", "remove", "unlink", "rename", "replace",
                     "rmdir", "chmod", "chown", "urandom", "getrandom", "pread",
                     "pwrite", "preadv", "pwritev", "readv", "writev", "sendfile",
                     "copy_file_range", "splice", "truncate", "ftruncate", "utime",
                     "link", "symlink", "fchmod", "fchown", "mknod", "mkfifo",
                     "execv", "execve", "execvp", "execvpe", "execl", "execle",
                     "execlp", "execlpe", "spawnl", "spawnle", "spawnlp", "spawnlpe",
                     "spawnv", "spawnve", "spawnvp", "spawnvpe", "kill", "killpg",
                     "chdir", "fchdir", "setuid", "setgid", "setreuid", "setregid"):
            if hasattr(os, name):
                reject = self.forbidden("direct-os-" + name)
                setattr(os, name, reject)
                if hasattr(native_module, name):
                    setattr(native_module, name, reject)
        for name in ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                     "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
                     "thread_time_ns", "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.forbidden("clock-" + name))
        self.installed = True


def read_owner(wall: SourceWall, row: tuple[object, ...]) -> bytes:
    role, relative, expected, count, inode = row
    require(type(role) is str and type(relative) is str
            and type(count) is int and 0 < count <= MAX_OWNER_BYTES
            and type(inode) is int and inode > 0, "reject an incomplete pinned owner")
    exact_sha(expected, relative)
    assert isinstance(relative, str) and isinstance(count, int) and isinstance(inode, int)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(ROOT + "/" + relative, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == count and before.st_nlink == 1
                and before.st_uid == os.geteuid(), "reject a substituted owner: " + role)
        chunks: list[bytes] = []
        remaining = count
        while remaining:
            chunk = os.read(descriptor, min(remaining, 65536))
            require(type(chunk) is bytes and bool(chunk), "reject a truncated owner: " + role)
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "reject a grown owner: " + role)
        after = os.fstat(descriptor)
        require(all(getattr(before, key) == getattr(after, key)
                    for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                "st_mtime_ns", "st_ctime_ns")),
                "reject an owner changed while authenticated: " + role)
        result = b"".join(chunks)
        require(digest(result) == expected, "reject altered frozen owner bytes: " + role)
        return result
    finally:
        os.close(descriptor)


def live_owner(wall: SourceWall, role: str, relative: str, expected: str) -> tuple[object, ...]:
    require(relative in (SOURCE, PROTOCOL, CONTRACT), "reject an unrelated live freeze owner")
    exact_sha(expected, relative)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(ROOT + "/" + relative, flags)
    try:
        owner = os.fstat(descriptor)
        require(stat.S_ISREG(owner.st_mode) and stat.S_IMODE(owner.st_mode) == 0o600
                and owner.st_dev == DEVICE and owner.st_uid == os.geteuid()
                and owner.st_nlink == 1 and 0 < owner.st_size <= MAX_OWNER_BYTES,
                "reject substituted live freeze owner: " + role)
        return role, relative, expected, owner.st_size, owner.st_ino
    finally:
        os.close(descriptor)


def owner_document(row: tuple[object, ...]) -> dict[str, object]:
    role, path, value, count, inode = row
    return {"role": role, "path": path, "sha256": value, "bytes": count,
            "device": DEVICE, "inode": inode, "mode": "0600", "nlink": 1}


def load_previous(wall: SourceWall, name: str, raw: bytes) -> dict[str, object]:
    path = ROOT + "/" + (OWNERS[5][1] if name == "compiler" else OWNERS[10][1])
    expected = OWNERS[5][2] if name == "compiler" else OWNERS[10][2]
    require(digest(raw) == expected and wall.compile_name is None
            and wall.pending_code is None, "load only exact frozen predecessor code")
    wall.compile_name = path
    wall.compile_raw = raw
    try:
        code = compile(raw, path, "exec")
        wall.pending_code = code
        namespace: dict[str, object] = {"__name__": "combined_frozen_" + name}
        exec(code, namespace)
        return namespace
    finally:
        wall.pending_code = None
        wall.compile_raw = None
        wall.compile_name = None


def metadata_only(wall: SourceWall) -> dict[str, object]:
    owner = os.lstat(ROOT + "/" + PROPOSAL)
    require(stat.S_ISREG(owner.st_mode) and stat.S_IMODE(owner.st_mode) == 0o600
            and owner.st_dev == DEVICE and owner.st_ino == PROPOSAL_INODE
            and owner.st_size == PROPOSAL_BYTES and owner.st_nlink == 1
            and owner.st_uid == os.geteuid()
            and wall.proposal_stat_count == 1 and wall.proposal_open_count == 0,
            "reject altered unopened final proposal metadata")
    return {"path": PROPOSAL, "sha256_independently_pinned_not_read": PROPOSAL_SHA256,
            "bytes_metadata_only": PROPOSAL_BYTES, "device": DEVICE,
            "inode_metadata_only": PROPOSAL_INODE, "case_count": 141557760,
            "content_open_count": 0, "metadata_probe_count": 1,
            "status": "NOT FROZEN; NOT GENERATED; NOT OPENED"}


def validate_history(owners: dict[str, bytes], parse) -> dict[str, object]:
    compiler = parse(owners["compiler_contract"], "previous compiler contract")
    anchor = parse(owners["anchor_contract"], "previous mandatory-anchor contract")
    compiler_application = parse(owners["compiler_application"], "actual compiler source")
    anchor_application = parse(owners["anchor_application"], "actual anchor source")
    actual = parse(owners["actual_v24_failure"], "complete original Rust failure")
    build = parse(owners["actual_v25_safe_build"], "actual first-party safe build")
    failed_v1 = parse(owners["failed_v1_contract"], "frozen failed first combination")
    failed_application = parse(owners["failed_v1_application"],
                               "complete failed first combination publication")
    public = parse(owners["public_profile_contract"], "public practice contract")
    stdlib = parse(owners["public_python_correctness"], "official public practice")
    rust = parse(owners["public_rust_correctness"], "first-party public practice")
    paired = parse(owners["public_paired_rows"], "all paired public practice rows")

    require(failed_v1.get("schema")
                == "rebar-first-party-rust-combined-search-compiler-fastpath-v1"
            and failed_v1.get("version") == 1
            and failed_v1["source"]["sha256"] == OWNERS[23][2]
            and failed_v1["protocol"]["sha256"] == OWNERS[24][2]
            and failed_v1["derived"]["engine"]["sha256"] == LIB_SHA256
            and failed_v1["derived"]["search"]["sha256"] == SEARCH_SHA256
            and failed_v1["new_combined_synthetic_semantics"]
                ["combined_differential_case_count"] == 111552,
            "reject the exact immutable first combined-source freeze")
    require(failed_application.get("schema")
                == "rebar-rust-combined-search-compiler-fastpath-v1-actual-application-failure"
            and failed_application.get("status") == "FAIL"
            and failed_application.get("source_sha256") == OWNERS[23][2]
            and failed_application.get("protocol_sha256") == OWNERS[24][2]
            and failed_application.get("contract_sha256") == OWNERS[25][2]
            and failed_application.get("frozen_commit")
                == "0129b1528d68e4afa9487b361c0980a67804d1c0"
            and failed_application.get("exit_code") == 2
            and failed_application.get("error_message")
                == "combined first-party source freeze rejected: combined source wall "
                   "rejected unapproved-descriptor-open-or-dir-fd"
            and failed_application.get("root_cause")
                == "Linux O_TMPFILE includes the O_DIRECTORY bit; the guard incorrectly "
                   "rejects ordinary directory opens by testing any overlapping O_TMPFILE bit."
            and failed_application.get("observed_failed_attempt_count") == 2
            and failed_application.get("first_attempt_authorization")
                == "UNAUTHORIZED DELEGATED READ-ONLY AGENT; SCOPE VIOLATION"
            and failed_application.get("second_attempt_authorization")
                == "ROOT-AUTHORIZED INDEPENDENT REPRODUCTION"
            and failed_application.get("destination")
                == "candidates/rust/variants/combined_search_compiler_fastpath_v1"
            and failed_application.get("destination_exists_after_failure") is False
            and failed_application.get("variant_files_created") == 0
            and failed_application.get("holdout") == "NOT OPENED",
            "reject or conceal either genuine committed first-combination failure")

    require(compiler.get("schema") == "rebar-owned-rust-compiler-allocation-fastpath-v1-source-freeze"
            and compiler["source"]["sha256"] == OWNERS[5][2]
            and compiler["protocol"]["sha256"] == OWNERS[6][2]
            and compiler["derived_first_party_compiler_source"]["sha256"] == OWNERS[9][2]
            and compiler["synthetic_differential_compiler_semantics"]["synthetic_case_count"] == 960
            and compiler["synthetic_differential_compiler_semantics"]
                ["synthetic_distinct_scanner_runtime_flag_case_count"] == 42
            and compiler["synthetic_differential_compiler_semantics"]
                ["synthetic_source_lifetime_control_count"] == 40,
            "reject incomplete frozen first-party compiler provenance")
    require(compiler_application.get("status") == "PASS"
            and compiler_application.get("variant_materialized") is True
            and compiler_application.get("source_sha256") == OWNERS[5][2]
            and compiler_application.get("protocol_sha256") == OWNERS[6][2]
            and compiler_application.get("contract_sha256") == OWNERS[7][2]
            and compiler_application["materialized_variant"]["sha256"] == OWNERS[9][2]
            and compiler_application.get("synthetic_differential_case_count") == 960
            and compiler_application.get("holdout") == "NOT OPENED",
            "reject incomplete actual compiler-source materialization")
    require(anchor.get("schema") == "rebar-owned-rust-mandatory-anchor-search-v1"
            and anchor.get("source_sha256") == OWNERS[10][2]
            and anchor.get("protocol_sha256") == OWNERS[11][2]
            and anchor["derived"]["engine"]["sha256"] == OWNERS[14][2]
            and anchor["derived"]["search"]["sha256"] == SEARCH_SHA256,
            "reject incomplete frozen first-party anchor provenance")
    require(anchor_application.get("status") == "APPLIED"
            and anchor_application.get("source_sha256") == OWNERS[10][2]
            and anchor_application.get("protocol_sha256") == OWNERS[11][2]
            and anchor_application.get("contract_sha256") == OWNERS[12][2]
            and anchor_application["created"]["engine"]["sha256"] == OWNERS[14][2]
            and anchor_application["created"]["search"]["sha256"] == SEARCH_SHA256
            and anchor_application["synthetic"]["differential_checks"] == 11328
            and anchor_application["synthetic"]["semantic_pattern_count"] == 18
            and anchor_application.get("holdout_opened") == 0,
            "reject incomplete actual anchor-source materialization")

    require(actual.get("status") == "PASS"
            and actual.get("candidate_status") == "FAIL"
            and actual.get("semantic_mismatch_count") == 1352
            and actual.get("verified_passing_case_count") == 15877
            and actual.get("case_execution_denominator") == 31237
            and actual.get("actual_candidate_workers") == 13
            and actual.get("completed_suite_count") == 13
            and actual.get("suite_count") == 13
            and type(actual.get("suite_integrity")) is list
            and len(actual["suite_integrity"]) == 13,
            "reject the genuine complete previous Rust compatibility failure")
    failures = {row["suite"]: row["mismatch_count"]
                for row in actual["suite_integrity"]
                if type(row) is dict and row.get("mismatch_count", 0) != 0}
    require(failures == {"substitution_v2": 240, "shape_v2": 1112}
            and all(type(row) is dict and row.get("fully_observed") is True
                    and row.get("actual_worker_started") is True
                    for row in actual["suite_integrity"]),
            "reject omitted per-obligation failures or incomplete Rust original workers")
    require(build.get("status") == "PASS" and build.get("build_status") == "PASS"
            and build.get("actual_compiler_process_count") == 28
            and build.get("actual_completed_phase_count") == 2
            and build.get("combined_bridge_sha256") == OWNERS[16][2]
            and build.get("latest_v24_original_campaign_receipt_sha256") == OWNERS[17][2]
            and build.get("latest_v24_candidate_status") == "FAIL"
            and build.get("latest_v24_semantic_mismatch_count") == 1352
            and build.get("expanded_holdout_proposal_case_count") == 141557760
            and build.get("holdout") == "NOT OPENED",
            "reject the successful zero-dependency safe Rust build history")

    require(public.get("case_count") == 416 and public.get("operation_count") == 26
            and public.get("pinned_cpython") == "3.14.6",
            "reject the existing public-only practice freeze")
    for name, row, imports in (("stdlib", stdlib, 0), ("rust", rust, 3)):
        require(row.get("status") == "PASS" and row.get("engine") == name
                and row.get("case_count") == 416 and row.get("candidate_import_count") == imports
                and row.get("holdout_files_read") == 0
                and row.get("records_sha256")
                    == "41f83dc761a93ea8e3203f46cedbba1e10918cf053194c20b37b8c209e992242"
                and type(row.get("records")) is list and len(row["records"]) == 416,
                "reject complete previous public correctness: " + name)
    require(stdlib["records"] == rust["records"],
            "the independently observed 416 complete public outcomes no longer match")
    require(paired.get("schema") == "rebar-rust-fresh-public-profile-v1-paired-timing-rows"
            and paired.get("rows_sha256")
                == "ce5ddb143be0d58588d2b18540c0db1b716eebb138cfe32a04690a0efe62c378"
            and type(paired.get("rows")) is list and len(paired["rows"]) == 1664,
            "reject any omitted or altered public paired-practice observation")
    require(b"[dependencies]" not in owners["cargo_manifest"]
            and owners["cargo_lock"].count(b"[[package]]") == 1
            and b'name = "rebar-rust-continuation"' in owners["cargo_lock"],
            "the first-party Rust replacement gained an external package")
    require(owners["capture_clamp_bridge"].count(b"rebar_compile(") >= 1
            and owners["capture_clamp_bridge"].count(b"rebar_compile_scanner(") >= 1
            and owners["capture_clamp_bridge"].find(b"rebar_compile(")
                < owners["capture_clamp_bridge"].rfind(b"PyMem_Free(owned_pattern)")
            and owners["capture_clamp_bridge"].find(b"rebar_compile_scanner(")
                < owners["capture_clamp_bridge"].rfind(b"PyMem_Free(owned_sources[index])"),
            "the synchronous C-owned parser input lifetime is no longer established")
    return {"original_case_execution_denominator": 31237,
            "latest_rust_verified_passing_case_count": 15877,
            "latest_rust_semantic_mismatch_count": 1352,
            "latest_rust_substitution_mismatch_count": 240,
            "latest_rust_changing_buffer_mismatch_count": 1112,
            "latest_rust_candidate_status": "FAIL",
            "safe_first_party_build_completed_phases": 2,
            "safe_first_party_build_compiler_process_count": 28,
            "external_rust_dependency_count": 0,
            "public_case_count": 416, "public_paired_observation_count": 1664,
            "previous_compiler_synthetic_case_count": 960,
            "previous_compiler_scanner_distinction_count": 42,
            "previous_compiler_lifetime_control_count": 40,
            "previous_anchor_differential_case_count": 11328,
            "previous_anchor_pattern_family_count": 18,
            "failed_v1_frozen_commit": "0129b1528d68e4afa9487b361c0980a67804d1c0",
            "failed_v1_receipt_sha256": OWNERS[26][2],
            "failed_v1_observed_attempt_count": 2,
            "failed_v1_first_attempt_authorization":
                "UNAUTHORIZED DELEGATED READ-ONLY AGENT; SCOPE VIOLATION",
            "failed_v1_second_attempt_authorization":
                "ROOT-AUTHORIZED INDEPENDENT REPRODUCTION",
            "failed_v1_variant_files_created": 0,
            "failed_v1_root_cause":
                "Linux O_TMPFILE includes O_DIRECTORY; any-bit overlap rejected safe directories"}


def to_anchor_ast(expression: tuple, compiler_flags: int) -> tuple:
    kind = expression[0]
    if kind == "literal":
        value, flags = expression[1], expression[2]
        actual = (2 if flags & 1 else 0) | (64 if flags & 2 else 0)
        return "lit", ord(value), actual
    if kind == "escaped":
        value, flags = expression[1], expression[2]
        actual = (2 if flags & 1 else 0) | (64 if flags & 2 else 0)
        return "lit", ord(value), actual
    if kind == "class":
        return ("dot",)
    if kind == "seq":
        return "seq", tuple(to_anchor_ast(value, compiler_flags) for value in expression[1])
    if kind == "alt":
        return "alt", tuple(to_anchor_ast(value, compiler_flags) for value in expression[1])
    if kind == "group":
        return "group", to_anchor_ast(expression[2], compiler_flags)
    raise FreezeError("reject an unsupported combined parser AST: " + str(kind))


def modeled_outcome(parser: object, error: type[BaseException]) -> tuple:
    try:
        return "PASS", parser.parse(), parser.flags, parser.runtime_flags  # type: ignore[attr-defined]
    except error as failure:
        return ("FAIL", failure.text, failure.position,  # type: ignore[attr-defined]
                parser.flags, parser.runtime_flags)  # type: ignore[attr-defined]


def folded_language(node: tuple, alphabet: tuple[int, ...]) -> list[tuple[int, ...]]:
    kind = node[0]
    if kind == "lit":
        value, flags = node[1], node[2]
        if flags & 2 and (65 <= value <= 90 or 97 <= value <= 122):
            lower = value | 32
            return [(lower,), (lower - 32,)]
        return [(value,)]
    if kind in ("dot", "class"):
        return [(value,) for value in alphabet]
    if kind in ("group", "atomic"):
        return folded_language(node[1], alphabet)
    if kind in ("alt", "cond"):
        return [word for child in node[1]
                for word in folded_language(child, alphabet)][:256]
    if kind == "seq":
        result: list[tuple[int, ...]] = [()]
        for child in node[1]:
            result = [left + right for left in result
                      for right in folded_language(child, alphabet)][:256]
        return result
    raise FreezeError("reject an unsupported combined folded-language node: " + str(kind))


def check_composition(compiler: dict[str, object], anchor: dict[str, object]) -> dict[str, int]:
    base = compiler["SyntheticParser"]

    class ScopedScannerParser(base):  # type: ignore[misc, valid-type]
        def group(self, flags: int) -> tuple:
            index = self.index + 1
            scoped_on = self.source.startswith("?i:", index)
            scoped_off = self.source.startswith("?-i:", index)
            previous = self.runtime_flags
            if self.scanner and (scoped_on or scoped_off):
                self.runtime_flags = ((previous | 1) if scoped_on else (previous & ~1))
            try:
                return super().group(flags)
            finally:
                self.runtime_flags = previous

    corpus = ("", "a", "ab", "A", "a|A", "a|", "|a", "(?:ab|a)",
              "(?i:a)b", "(?-i:a)b", "(?i:a(?-i:b)c)d", "(?-i:a(?i:b)c)d",
              "(?i:a|B)b", "(?-i:A|b)c", "(?x:a # ignored\n| b)",
              "a\\|b", "[a|b]c", "(?:aaab|aaaa)c", "(?:bcaaaa|baaaaa)")
    corpus += ("(", "[", "\\", "a)", "(?#unterminated")
    subjects = (b"", b"a", b"A", b"ab", b"Aab", b"aaaaab",
                b"bcaaaa", b"bbcaaaa", b"AaBbCcDd", b"\x80a\xffb",
                b"a" * 31 + b"b", b"b" * 32 + b"a",
                b"a" * 63 + b"b", b"A" * 65 + b"B")
    cases = 0
    scanner_cases = 0
    scoped_cases = 0
    saved_allocations = 0
    restored_scopes = 0
    error_cases = 0
    for spelling in corpus:
        for flags in (0, 1, 2, 3):
            for scanner in (False, True):
                old = ScopedScannerParser(spelling, flags, scanner, False)
                new = ScopedScannerParser(spelling, flags, scanner, True)
                expected = modeled_outcome(old, compiler["SyntheticError"])  # type: ignore[arg-type]
                observed = modeled_outcome(new, compiler["SyntheticError"])  # type: ignore[arg-type]
                require(expected == observed,
                        "combined parser changed an AST, lexical error, position, or flags")
                if expected[0] == "FAIL":
                    error_cases += 1
                    continue
                parsed = observed[1]
                require(new.allocations <= old.allocations,
                        "combined parser introduced a previously absent allocation")
                require(old.runtime_flags == flags and new.runtime_flags == flags,
                        "scoped scanner runtime flags escaped their group")
                saved_allocations += old.allocations - new.allocations
                scanner_cases += int(scanner)
                scoped_cases += int("(?i:" in spelling or "(?-i:" in spelling)
                restored_scopes += int(scanner and ("(?i:" in spelling or "(?-i:" in spelling))
                expression = to_anchor_ast(parsed, flags)
                plan = anchor["model_plan"](expression)
                words = folded_language(expression, tuple(b"aAbBcCx|"))
                for subject in subjects:
                    starts = (0, 1, len(subject), len(subject) + 1)
                    ends = (0, 1, 15, 16, 17, 31, 32, 33, 63, 64, 65,
                            len(subject), (1 << 64) - 1)
                    for start in starts:
                        for end in ends:
                            direct = anchor["model_original"](words, subject, start, end)
                            filtered = anchor["model_filtered"](words, subject, start, end, plan)
                            require(direct == filtered,
                                    "combined anchor lost a leftmost or ordered alternative")
                            cases += 1

    phrases = (("abc", "abX"), ("ab", "a"), ("", "abc"),
               ("(?i:a)b", "aB"), ("(?-i:a)b", "aB"),
               ("(?i:a(?-i:b)c)d", "abCd"), ("aaab", "aaaa"),
               ("bcaaaa", "baaaaa"))
    phrase_roots = 0
    phrase_owners = 0
    ownership_rejections = 0
    for pair in phrases:
        for flags in (0, 1):
            branches: list[tuple] = []
            leases: list[tuple] = []
            for spelling in pair:
                owner = compiler["SyntheticSourceOwner"](tuple(map(ord, spelling)))
                borrowed = owner.borrow()
                observed = "".join(chr(borrowed.read(index))
                                   for index in range(len(owner.values)))
                parser = ScopedScannerParser(observed, flags, True, True)
                result = modeled_outcome(parser, compiler["SyntheticError"])  # type: ignore[arg-type]
                require(result[0] == "PASS" and parser.runtime_flags == flags,
                        "a scanner phrase escaped or mis-restored its scoped runtime flags")
                branches.append(("group", to_anchor_ast(result[1], flags)))
                borrowed.release()
                owner.close()
                leases.append((owner, borrowed))
                phrase_owners += 1
            root = "alt", tuple(branches)
            plan = anchor["model_plan"](root)
            words = folded_language(root, tuple(b"aAbBcCxX|"))
            for subject in subjects:
                for start, end in ((0, len(subject)), (1, len(subject)),
                                   (0, (1 << 64) - 1), (len(subject), len(subject))):
                    direct = anchor["model_original"](words, subject, start, end)
                    filtered = anchor["model_filtered"](words, subject, start, end, plan)
                    require(direct == filtered,
                            "a combined scanner lost phrase priority or an empty alternative")
                    cases += 1
            for owner, borrowed in leases:
                for action in (lambda value=borrowed: value.read(0),
                               lambda value=borrowed: value.release(),
                               lambda value=owner: value.borrow()):
                    try:
                        action()
                    except compiler["FreezeError"]:  # type: ignore[misc]
                        ownership_rejections += 1
                    else:
                        raise FreezeError("a scanner anchor retained a released phrase source")
            phrase_roots += 1

    owner = compiler["SyntheticSourceOwner"]((65, 66, 67))
    borrowed = owner.borrow()
    for invalid in (-1, 3, 1 << 64):
        try:
            borrowed.read(invalid)
        except compiler["FreezeError"]:  # type: ignore[misc]
            ownership_rejections += 1
        else:
            raise FreezeError("a combined parser accepted an out-of-bounds source view")
    expression = ("seq", tuple(("lit", borrowed.read(index), 0) for index in range(3)))
    retained = anchor["model_plan"](expression)
    require(retained is not None, "derive an owned anchor plan while its parser source is live")
    borrowed.release()
    owner.close()
    require(anchor["model_next"](b"xxxABC", 0, 6, retained) == 3,
            "the owned anchor plan retained a released parser-source view")
    try:
        borrowed.read(0)
    except compiler["FreezeError"]:  # type: ignore[misc]
        ownership_rejections += 1
    else:
        raise FreezeError("combined anchor accepted a released parser borrow")

    require(cases >= 50000 and error_cases >= 20
            and scanner_cases >= 60 and scoped_cases >= 30
            and restored_scopes >= 15 and saved_allocations >= 50
            and phrase_roots == 16 and phrase_owners == 32
            and ownership_rejections >= 100,
            "require meaningful scanner, flag, ordering, bounds, and ownership composition")
    return {"combined_differential_case_count": cases,
            "combined_parser_error_case_count": error_cases,
            "combined_scanner_parse_count": scanner_cases,
            "combined_scoped_parse_count": scoped_cases,
            "combined_restored_scanner_scope_count": restored_scopes,
            "combined_eliminated_parser_allocation_count": saved_allocations,
            "combined_multi_phrase_root_count": phrase_roots,
            "combined_released_phrase_owner_count": phrase_owners,
            "combined_invalid_source_ownership_rejection_count": ownership_rejections,
            "combined_released_source_anchor_ownership_count": phrase_owners + 1,
            "synthetic_ignorecase_maps_to_rust_flag": 2,
            "synthetic_verbose_maps_to_rust_flag": 64}


def derive_sources(owners: dict[str, bytes], compiler: dict[str, object],
                   anchor: dict[str, object]) -> tuple[bytes, bytes, dict[str, object]]:
    replacements = compiler["REPLACEMENTS"]
    require(type(replacements) is tuple and len(replacements) == 7,
            "require the seven frozen independently authored compiler substitutions")
    candidate = owners["anchor_lib"]
    baseline = owners["canonical_lib"]
    rows: list[dict[str, object]] = []
    spans: list[tuple[int, int]] = []
    for label, before, after in replacements:
        require(type(label) is str and type(before) is bytes and type(after) is bytes
                and before != after and candidate.count(before) == 1
                and baseline.count(before) == 1 and candidate.count(after) == 0,
                "reject nonunique, overlapping, or already applied compiler anchor: " + label)
        position = candidate.index(before)
        spans.append((position, position + len(before)))
        rows.append({"name": label,
                     "canonical_line": baseline.count(b"\n", 0, baseline.index(before)) + 1,
                     "anchor_line": candidate.count(b"\n", 0, position) + 1,
                     "anchor_offset": position,
                     "old_bytes": len(before), "new_bytes": len(after),
                     "source_delta_bytes": len(after) - len(before)})
    ordered = sorted(spans)
    require(all(previous[1] <= following[0]
                for previous, following in zip(ordered, ordered[1:])),
            "two independent compiler substitutions overlap")
    for label, before, after in replacements:
        require(candidate.count(before) == 1,
                "a previous compiler substitution changed the next anchor: " + label)
        candidate = candidate.replace(before, after, 1)
        require(candidate.count(after) == 1,
                "a combined compiler substitution cannot reverse uniquely: " + label)

    compiler_only = compiler["derive_source"](owners["canonical_lib"])
    require(compiler_only == owners["compiler_variant"],
            "the exact committed compiler variant cannot be reproduced")
    search_only = anchor["transform_engine"](owners["canonical_lib"])
    require(search_only == owners["anchor_lib"],
            "the exact committed mandatory-anchor engine cannot be reproduced")
    exact_search = anchor["transform_search"](owners["canonical_search"])
    require(exact_search == owners["anchor_search"],
            "the exact committed mandatory-anchor search source cannot be reproduced")
    opposite = anchor["transform_engine"](owners["compiler_variant"])
    require(candidate == opposite and digest(candidate) == LIB_SHA256
            and len(candidate) == LIB_BYTES and digest(exact_search) == SEARCH_SHA256
            and len(exact_search) == SEARCH_BYTES,
            "the independently authored first-party source transformations do not commute")

    reverse = candidate
    for label, before, after in reversed(replacements):
        require(reverse.count(after) == 1,
                "a combined compiler substitution lost unique reversibility: " + label)
        reverse = reverse.replace(after, before, 1)
    require(reverse == owners["anchor_lib"],
            "the exact combined source does not reverse to the frozen anchor owner")
    require(candidate.count(b"struct Parser<'a> {\n    source: &'a [u32],\n") == 1
            and candidate.count(b"mandatory_anchor_search: Option<search::AnchorPlan>") == 1
            and candidate.count(b"let mandatory_anchor_search = mandatory_anchor_search(&root);") == 2
            and candidate.count(b"source: unsafe { slice::from_raw_parts(phrase.source, phrase.length) },") == 1
            and candidate.count(b"source: &source,") == 1
            and candidate.count(b"mod mandatory_anchor_search_tests") == 1
            and exact_search.count(b"mod anchor_position_tests") == 1,
            "the complete combined Rust parser, scanner, anchor, or test ownership changed")
    for forbidden in (b"extern crate regex", b"use regex::", b"pcre2", b"oniguruma",
                      b"_sre", b"std::process::Command", b"dlopen(", b"ctypes"):
        require(forbidden not in candidate and forbidden not in exact_search,
                "a borrowed engine or forbidden native loader entered combined Rust source")
    return candidate, exact_search, {"replacement_count": 7,
                                    "substitution_spans_disjoint": True,
                                    "transformations_commute": True,
                                    "transformation_is_exactly_reversible": True,
                                    "replacement_source_delta_bytes": 54,
                                    "replacements": rows}


def frozen_contract(source_row: tuple[object, ...], protocol_row: tuple[object, ...],
                    proposal: dict[str, object], history: dict[str, object],
                    compiler_model: dict[str, object], anchor_model: dict[str, object],
                    interaction: dict[str, int], composition: dict[str, object]) -> dict[str, object]:
    return {"schema": SCHEMA, "version": 2,
            "status": "SOURCE FROZEN; COMBINED VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN",
            "phase": "CANDIDATES", "family": "rust",
            "source": owner_document(source_row), "protocol": owner_document(protocol_row),
            "authenticated_previous_owner_count": len(OWNERS),
            "authenticated_previous_owners": [owner_document(owner) for owner in OWNERS],
            "original_correctness": history,
            "previous_compiler_synthetic_semantics": compiler_model,
            "previous_anchor_synthetic_semantics": anchor_model,
            "new_combined_synthetic_semantics": interaction,
            "exact_commuting_composition": composition,
            "derived": {"engine": {"path": LIB_TARGET, "sha256": LIB_SHA256,
                                     "bytes": LIB_BYTES},
                        "search": {"path": SEARCH_TARGET, "sha256": SEARCH_SHA256,
                                    "bytes": SEARCH_BYTES}},
            "expanded_final_holdout_metadata_only": proposal,
            "physical_source_wall": {"policy": "CONTINUOUS DENY DEFAULT; PINNED DESCRIPTORS",
                                     "installed_before_owner_reads": True,
                                     "remains_active_during_root_publication": True,
                                     "underlying_posix_aliases_guarded": True,
                                     "python_wrapper_closure_raw_primitives_visible": True,
                                     "dynamic_source_execution_hash_pinned": True,
                                     "allowed_native_binary_count": 0,
                                     "allowed_archive_count": 0,
                                     "allowed_holdout_content_count": 0,
                                     "allowed_proposal_metadata_probe_count": 1,
                                     "allowed_dynamic_frozen_transformer_count": 2,
                                     "source_mode_writes_allowed": False,
                                     "root_output_directory_mode": "0700",
                                     "root_output_file_mode": "0600",
                                     "root_output_file_policy": "O_CREAT|O_EXCL|O_NOFOLLOW",
                                     "linux_tmpfile_detection": "FULL COMPOSITE MASK; NOT ANY OVERLAP",
                                     "ordinary_directory_overlap_is_allowed": True,
                                     "full_tmpfile_directory_and_output_are_rejected": True,
                                     "source_owner_fsync_count": 2,
                                     "directory_fsync_count": 2},
            "source_only_effects": {"candidate_imports": 0, "candidate_workers_started": 0,
                                    "compiler_processes_started": 0,
                                    "native_libraries_loaded": 0,
                                    "native_binaries_opened": 0,
                                    "archives_opened": 0, "clocks_sampled": 0,
                                    "workspace_mutations": 0,
                                    "holdout_cases_generated": 0,
                                    "holdout_cases_opened": 0,
                                    "holdout_proposal_content_open_count": 0,
                                    "holdout_proposal_metadata_probe_count": 1,
                                    "qualified_independent_candidate_count": 0,
                                    "original_p0_denominator": 31237,
                                    "candidate_correctness": NOT_MEASURED,
                                    "candidate_performance": NOT_MEASURED,
                                    "candidate_memory": NOT_MEASURED,
                                    "undefined_behavior": NOT_MEASURED,
                                    "holdout": "NOT OPENED", "winner_selected": False}}


def directory_flag_proof(wall: SourceWall) -> dict[str, int]:
    directory = (os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                 | getattr(os, "O_CLOEXEC", 0))
    temporary = getattr(os, "O_TMPFILE", 0)
    require(type(temporary) is int and temporary != 0
            and temporary & os.O_DIRECTORY == os.O_DIRECTORY
            and directory & temporary != temporary,
            "authenticate the real Linux composite temporary-file flag collision")
    legacy_destructive = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL
                          | os.O_TRUNC | os.O_APPEND | temporary)
    require(bool(directory & legacy_destructive)
            and wall.directory_flags(directory) is True
            and wall.temporary_file_flags(directory) is False,
            "prove the exact committed V1 failure and corrected safe directory acceptance")

    correct_output = (os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                      | getattr(os, "O_CLOEXEC", 0))
    require(wall.output_flags(correct_output) is True,
            "preserve the exact exclusively created first-party Rust output flags")
    bad_directory = (directory | os.O_WRONLY, directory | os.O_RDWR,
                     directory | os.O_CREAT, directory | os.O_EXCL,
                     directory | os.O_TRUNC, directory | os.O_APPEND,
                     directory & ~os.O_NOFOLLOW, directory & ~os.O_DIRECTORY,
                     directory | temporary, directory | temporary | os.O_WRONLY,
                     directory | temporary | os.O_RDWR)
    require(all(wall.directory_flags(flags) is False for flags in bad_directory),
            "reject every destructive, anonymous, or untrusted directory mode")
    bad_output = (correct_output & ~os.O_WRONLY, correct_output & ~os.O_CREAT,
                  correct_output & ~os.O_EXCL, correct_output & ~os.O_NOFOLLOW,
                  correct_output | os.O_RDWR, correct_output | os.O_TRUNC,
                  correct_output | os.O_APPEND, correct_output | os.O_DIRECTORY,
                  correct_output | temporary)
    require(all(wall.output_flags(flags) is False for flags in bad_output),
            "reject every incomplete, destructive, directory, or anonymous output mode")

    preview = SourceWall(True)
    preview.stage = "ready"
    preview.audit("open", (preview.parent_path, None, directory))
    preview.stage = "created"
    preview.audit("open", (DIRECTORY, None, directory))
    rejected = 0
    for flags in bad_directory:
        preview.stage = "ready"
        try:
            preview.audit("open", (preview.parent_path, None, flags))
        except FreezeError:
            rejected += 1
        else:
            raise FreezeError("an unsafe root directory passed the full composite-mask audit")
    require(rejected == len(bad_directory),
            "exercise every rejected temporary, destructive, and anonymous directory mode")
    return {"actual_linux_o_directory": os.O_DIRECTORY,
            "actual_linux_o_tmpfile": temporary,
            "ordinary_directory_parent_and_child_positive_controls": 2,
            "rejected_directory_flag_control_count": len(bad_directory),
            "rejected_output_flag_control_count": len(bad_output),
            "rejected_directory_audit_control_count": rejected,
            "legacy_v1_rejects_real_safe_directory": True,
            "corrected_v2_accepts_real_safe_directory": True,
            "real_safe_directory_has_full_tmpfile_mask": False}


def validate_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PYTHON and sys.flags.isolated == 1
            and sys.flags.no_site == 1 and sys.dont_write_bytecode is True,
            "require exact pinned CPython 3.14.6 under -I -B -S")
    clean_imports()


def parse_arguments(values: list[str]) -> tuple[str, dict[str, str], frozenset[str]]:
    require(type(values) is list and len(values) > 0, "require exactly one explicit frozen action")
    mode = values[0]
    require(mode in ("--render-contract", "--verify-source", "--self-test", "--apply"),
            "reject an unknown, missing, or combined frozen action")
    pins: dict[str, str] = {}
    flags: set[str] = set()
    position = 1
    while position < len(values):
        name = values[position]
        if name in ("--root-authorized", "--frozen-committed-pushed"):
            require(name not in flags, "reject duplicate explicit root authorization")
            flags.add(name)
            position += 1
            continue
        require(name in ("--source-sha256", "--protocol-sha256", "--contract-sha256",
                         "--frozen-commit", "--pushed-commit")
                and name not in pins and position + 1 < len(values),
                "reject an unknown, duplicate, or incomplete frozen argument")
        value = values[position + 1]
        pins[name] = (exact_commit(value, name) if name.endswith("commit")
                      else exact_sha(value, name))
        position += 2
    basic = {"--source-sha256", "--protocol-sha256"}
    if mode == "--render-contract":
        require(set(pins) == basic and not flags,
                "contract rendering accepts only the independently pinned source and protocol")
    elif mode in ("--verify-source", "--self-test"):
        require(set(pins) == basic | {"--contract-sha256"} and not flags,
                "source-only verification requires exactly its three immutable owner hashes")
    else:
        require(set(pins) == basic | {"--contract-sha256", "--frozen-commit", "--pushed-commit"}
                and pins["--frozen-commit"] == pins["--pushed-commit"]
                and flags == {"--root-authorized", "--frozen-committed-pushed"},
                "exclusive root publication requires all hashes and matching pushed authority")
    return mode, pins, frozenset(flags)


def load_context(wall: SourceWall, mode: str, pins: dict[str, str]) -> dict[str, object]:
    source_row = live_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol_row = live_owner(wall, "protocol", PROTOCOL, pins["--protocol-sha256"])
    read_owner(wall, source_row)
    read_owner(wall, protocol_row)
    contract_row = None
    if mode != "--render-contract":
        contract_row = live_owner(wall, "contract", CONTRACT, pins["--contract-sha256"])
    owners = {row[0]: read_owner(wall, row) for row in OWNERS}
    compiler = load_previous(wall, "compiler", owners["compiler_source"])
    anchor = load_previous(wall, "anchor", owners["anchor_source"])
    clean_imports()
    parser = compiler["json_object"]
    history = validate_history(owners, parser)
    proposal = metadata_only(wall)
    lib, search, composition = derive_sources(owners, compiler, anchor)
    compiler_model = compiler["synthetic_semantics"]()
    anchor_model = anchor["check_model"]()
    directory_proof = directory_flag_proof(wall)
    require(compiler_model.get("synthetic_case_count") == 960
            and compiler_model.get("synthetic_distinct_scanner_runtime_flag_case_count") == 42
            and compiler_model.get("synthetic_source_lifetime_control_count") == 40,
            "the frozen first-party compiler differential model changed")
    require(anchor_model.get("differential_checks") == 11328
            and anchor_model.get("semantic_pattern_count") == 18,
            "the frozen first-party anchor differential model changed")
    interaction = check_composition(compiler, anchor)
    contract = frozen_contract(source_row, protocol_row, proposal, history,
                               compiler_model, anchor_model, interaction, composition)
    contract["corrected_linux_directory_flag_semantics"] = directory_proof
    if contract_row is not None:
        raw = read_owner(wall, contract_row)
        require(raw == document(contract) and parser(raw, "complete combined contract") == contract,
                "reject an incomplete or altered combined source-freeze obligation")
    require(not wall.owners and wall.parent_fd is None and wall.child_fd is None
            and not wall.outputs and wall.compile_count == 2 and wall.exec_count == 2
            and wall.proposal_stat_count == 1 and wall.proposal_open_count == 0,
            "close all authenticated source descriptors without opening holdout or candidates")
    return {"contract": contract, "lib": lib, "search": search,
            "compiler": compiler, "anchor": anchor, "composition": composition,
            "interaction": interaction, "history": history,
            "directory_flag_proof": directory_proof}


def expect_rejected(wall: SourceWall, label: str, operation) -> str:
    before = sum(wall.blocked.values())
    try:
        operation()
    except (FreezeError, OSError, TypeError, ValueError):
        require(sum(wall.blocked.values()) > before,
                "hostile control did not encounter the physical source wall: " + label)
        return label
    raise FreezeError("hostile source operation escaped the physical wall: " + label)


def hostile_self_test(wall: SourceWall, state: dict[str, object]) -> dict[str, object]:
    source = ROOT + "/" + SOURCE

    def forged_compilation() -> None:
        saved = wall.compile_name, wall.compile_raw, wall.compile_count, wall.exec_count
        wall.compile_name = ROOT + "/" + OWNERS[5][1]
        wall.compile_raw = b"pass"
        wall.compile_count = 0
        wall.exec_count = 0
        try:
            compile(b"pass", wall.compile_name, "exec")
        finally:
            wall.compile_name, wall.compile_raw, wall.compile_count, wall.exec_count = saved

    def forged_publication_authority() -> None:
        saved = wall.apply
        wall.apply = True
        try:
            sys.audit("os.exec", "/bin/true", (), None)
        finally:
            wall.apply = saved

    native = sys.modules["posix"]
    controls = [
        expect_rejected(wall, "builtins-read", lambda: builtins.open(source, "rb")),
        expect_rejected(wall, "builtins-write", lambda: builtins.open(source, "wb")),
        expect_rejected(wall, "direct-io-open", lambda: io.open(source, "rb")),
        expect_rejected(wall, "direct-_io-open", lambda: _io.open(source, "rb")),
        expect_rejected(wall, "owner-write", lambda: os.open(source, os.O_WRONLY)),
        expect_rejected(wall, "owner-missing-nofollow", lambda: os.open(source, os.O_RDONLY)),
        expect_rejected(wall, "parent-source-open",
                        lambda: os.open(ROOT + "/" + PARENT,
                                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)),
        expect_rejected(wall, "anonymous-owner-readwrite",
                        lambda: os.open(source, os.O_TMPFILE | os.O_RDWR | os.O_NOFOLLOW)),
        expect_rejected(wall, "anonymous-owner-write-create",
                        lambda: os.open(source, os.O_TMPFILE | os.O_WRONLY
                                        | os.O_CREAT | os.O_NOFOLLOW)),
        expect_rejected(wall, "anonymous-parent-directory",
                        lambda: os.open(ROOT + "/" + PARENT,
                                        os.O_TMPFILE | os.O_DIRECTORY | os.O_NOFOLLOW)),
        expect_rejected(wall, "target-before-publication",
                        lambda: os.open(ROOT + "/" + LIB_TARGET,
                                        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW)),
        expect_rejected(wall, "source-alias",
                        lambda: os.open(ROOT + "/tools/../" + SOURCE,
                                        os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "foreign-read",
                        lambda: os.open("/etc/passwd", os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "native-binary",
                        lambda: os.open(ROOT + "/candidates/_rust_engine.so",
                                        os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "archive",
                        lambda: os.open(ROOT + "/oracle/phase2/evidence/private.gz",
                                        os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "final-holdout-content",
                        lambda: os.open(ROOT + "/" + PROPOSAL,
                                        os.O_RDONLY | os.O_NOFOLLOW)),
        expect_rejected(wall, "repeated-final-metadata",
                        lambda: os.lstat(ROOT + "/" + PROPOSAL)),
        expect_rejected(wall, "foreign-read-fd", lambda: os.read(0, 1)),
        expect_rejected(wall, "foreign-write-fd", lambda: os.write(1, b"rejected")),
        expect_rejected(wall, "foreign-fstat", lambda: os.fstat(0)),
        expect_rejected(wall, "foreign-fsync", lambda: os.fsync(1)),
        expect_rejected(wall, "foreign-close", lambda: os.close(0)),
        expect_rejected(wall, "directory-creation",
                        lambda: os.mkdir(DIRECTORY, 0o700, dir_fd=0)),
        expect_rejected(wall, "process", lambda: os.system("true")),
        expect_rejected(wall, "process-exec-audit",
                        lambda: sys.audit("os.exec", "/bin/true", (), None)),
        expect_rejected(wall, "clock", lambda: time.time()),
        expect_rejected(wall, "nanosecond-clock", lambda: time.perf_counter_ns()),
        expect_rejected(wall, "dynamic-compile", lambda: compile(b"1", "hostile.py", "exec")),
        expect_rejected(wall, "forged-authenticated-compile", forged_compilation),
        expect_rejected(wall, "dynamic-execution", lambda: exec("1")),
        expect_rejected(wall, "forged-publication-authority", forged_publication_authority),
        expect_rejected(wall, "native-import", lambda: __import__("ctypes")),
        expect_rejected(wall, "matcher-import", lambda: __import__("re")),
        expect_rejected(wall, "underlying-posix-write", lambda: native.write(1, b"rejected")),
        expect_rejected(wall, "underlying-posix-read", lambda: native.read(0, 1)),
        expect_rejected(wall, "underlying-posix-fstat", lambda: native.fstat(0)),
    ]
    for name in ("dup", "pread", "pwrite", "readv", "writev", "sendfile", "link",
                 "symlink", "truncate", "ftruncate", "utime", "listdir", "stat",
                 "execv", "execve", "spawnv", "spawnve", "kill", "chdir"):
        if hasattr(os, name):
            function = getattr(os, name)
            controls.append(expect_rejected(wall, "descriptor-alias-" + name,
                                            lambda actual=function: actual()))

    compiler = state["compiler"]
    parser = compiler["json_object"]
    malformed = (b'{"duplicate":1,"duplicate":2}', b'{"leading":01}',
                 b'{"nonfinite":NaN}', b'{"fraction":1.5}', b'{"trailing":1}{}',
                 b'{"surrogate":"\\ud800"}', b'{"escape":"\\q"}', b'[1]')
    malformed_count = 0
    for raw in malformed:
        try:
            parser(raw, "hostile malformed frozen contract")
        except (compiler["FreezeError"], IndexError, ValueError):  # type: ignore[misc]
            malformed_count += 1
        else:
            raise FreezeError("a malformed or duplicate frozen JSON owner escaped")

    replacement_count = 0
    for label, old, new in compiler["REPLACEMENTS"]:
        require(old != new and type(label) is str, "a frozen reversible substitution disappeared")
        for hostile in (b"extern crate regex", b"use regex::Regex", b"pcre2", b"_sre",
                        b"std::process::Command", b"dlopen(", b"ctypes"):
            try:
                require(hostile not in old + b"\n" + hostile + b"\n" + new,
                        "hostile external engine control")
            except FreezeError:
                replacement_count += 1
            else:
                raise FreezeError("a hostile engine control escaped the combined verifier")
    require(len(controls) >= 35 and malformed_count == len(malformed)
            and replacement_count == 49,
            "require complete physical, JSON, ownership, and no-delegation controls")
    closure_raw_visible = any(
        callable(cell.cell_contents)
        for function in (os.read, os.write, os.fstat, os.close, os.fsync)
        for cell in (function.__closure__ or ())
    )
    require(closure_raw_visible is True,
            "publish Python closure capability visibility honestly")
    require(wall.proposal_open_count == 0 and wall.proposal_stat_count == 1,
            "a rejected hidden-case attempt must never count as opened content")
    clean_imports()
    return {"physical_hostile_control_count": len(controls),
            "physical_hostile_controls": controls,
            "malformed_json_control_count": malformed_count,
            "no_external_engine_control_count": replacement_count,
            "physically_blocked_categories": dict(wall.blocked),
            "underlying_posix_aliases_guarded": True,
            "python_wrapper_closure_raw_primitives_visible": True,
            "untrusted_dynamic_execution_authorized": False,
            "root_directory_positive_controls": 2,
            "linux_full_composite_tmpfile_hostile_controls": 3,
            "wall_remains_installed": wall.installed}


def create_output(wall: SourceWall, name: str, raw: bytes) -> dict[str, object]:
    require(wall.child_fd is not None and digest(raw)
            == (LIB_SHA256 if name == "lib.rs" else SEARCH_SHA256),
            "authenticate complete output bytes before exclusive creation")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
    descriptor = os.open(name, flags, 0o600, dir_fd=wall.child_fd)
    try:
        initial = os.fstat(descriptor)
        require(stat.S_ISREG(initial.st_mode) and stat.S_IMODE(initial.st_mode) == 0o600
                and initial.st_dev == DEVICE and initial.st_uid == os.geteuid()
                and initial.st_nlink == 1 and initial.st_size == 0,
                "reject an exchanged, linked, or nonempty exclusive Rust source")
        offset = 0
        while offset < len(raw):
            offset += os.write(descriptor, memoryview(raw)[offset:])
        os.fsync(descriptor)
        complete = os.fstat(descriptor)
        require(complete.st_dev == initial.st_dev and complete.st_ino == initial.st_ino
                and complete.st_size == len(raw) and complete.st_nlink == 1
                and stat.S_IMODE(complete.st_mode) == 0o600,
                "reject an incomplete or exchanged exclusive Rust output")
        return {"path": LIB_TARGET if name == "lib.rs" else SEARCH_TARGET,
                "sha256": digest(raw), "bytes": len(raw), "device": complete.st_dev,
                "inode": complete.st_ino, "mode": "0600", "nlink": 1,
                "exclusive_no_follow": True, "fsync_completed": True}
    finally:
        os.close(descriptor)


def apply_root_only(wall: SourceWall, state: dict[str, object],
                    pins: dict[str, str], flags: frozenset[str]) -> dict[str, object]:
    require(flags == {"--root-authorized", "--frozen-committed-pushed"}
            and pins["--frozen-commit"] == pins["--pushed-commit"]
            and pins["--source-sha256"] == state["contract"]["source"]["sha256"]
            and pins["--protocol-sha256"] == state["contract"]["protocol"]["sha256"],
            "revalidate complete immutable root authorization before variant creation")
    require(wall.apply and wall.stage == "source" and not wall.owners
            and wall.proposal_stat_count == 1 and wall.proposal_open_count == 0
            and digest(state["lib"]) == LIB_SHA256 and len(state["lib"]) == LIB_BYTES
            and digest(state["search"]) == SEARCH_SHA256
            and len(state["search"]) == SEARCH_BYTES,
            "complete all authenticated composition proofs before any root mutation")
    wall.expected = {"lib.rs": state["lib"], "search.rs": state["search"]}
    wall.stage = "ready"
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    parent = os.open(ROOT + "/" + PARENT, flags)
    parent_stat = os.fstat(parent)
    require(stat.S_ISDIR(parent_stat.st_mode)
            and stat.S_IMODE(parent_stat.st_mode) == 0o700
            and parent_stat.st_dev == DEVICE and parent_stat.st_ino == PARENT_INODE
            and parent_stat.st_uid == os.geteuid(),
            "authenticate the exact real first-party Rust variants directory")
    os.mkdir(DIRECTORY, 0o700, dir_fd=parent)
    child = os.open(DIRECTORY, flags, dir_fd=parent)
    child_stat = os.fstat(child)
    require(stat.S_ISDIR(child_stat.st_mode)
            and stat.S_IMODE(child_stat.st_mode) == 0o700
            and child_stat.st_dev == DEVICE and child_stat.st_uid == os.geteuid(),
            "authenticate one newly created real private Rust variant directory")
    lib = create_output(wall, "lib.rs", state["lib"])
    search = create_output(wall, "search.rs", state["search"])
    os.fsync(child)
    os.close(child)
    os.fsync(parent)
    os.close(parent)
    require(wall.opened_names == ["lib.rs", "search.rs"]
            and wall.synced == {"lib.rs", "search.rs"}
            and wall.child_synced and wall.parent_synced
            and wall.parent_fd is None and wall.child_fd is None and not wall.outputs,
            "fully synchronize and close exactly two exclusive Rust source outputs")
    return {"status": "APPLIED", "mode": "apply", "schema": SCHEMA + "-application",
            "source_sha256": pins["--source-sha256"],
            "protocol_sha256": pins["--protocol-sha256"],
            "contract_sha256": pins["--contract-sha256"],
            "frozen_pushed_commit": pins["--pushed-commit"],
            "created": {"directory": {"path": PARENT + "/" + DIRECTORY,
                                        "device": child_stat.st_dev,
                                        "inode": child_stat.st_ino,
                                        "mode": "0700", "fsync_completed": True},
                        "engine": lib, "search": search},
            "workspace_mutation_count": 3,
            "continuous_wall_active": wall.installed,
            "owner_output_fsync_count": 2, "directory_fsync_count": 2,
            "original_case_execution_denominator": 31237,
            "actual_v24_rust_candidate_status": "FAIL",
            "actual_v24_rust_semantic_mismatch_count": 1352,
            "preserved_failed_v1_receipt_sha256": OWNERS[26][2],
            "preserved_failed_v1_attempt_count": 2,
            "linux_full_composite_tmpfile_guard_corrected": True,
            "previous_compiler_synthetic_case_count": 960,
            "previous_anchor_differential_case_count": 11328,
            "combined_synthetic_case_count":
                state["interaction"]["combined_differential_case_count"],
            "public_case_count": 416, "public_paired_observation_count": 1664,
            "candidate_imports": 0, "candidate_workers_started": 0,
            "compiler_processes_started": 0, "native_libraries_loaded": 0,
            "clock_samples": 0, "holdout_content_open_count": 0,
            "holdout_metadata_probe_count": 1,
            "holdout": "NOT OPENED", "candidate_correctness": NOT_MEASURED,
            "performance": NOT_MEASURED, "memory": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED, "candidate_qualified": False,
            "winner_selected": False}


def main() -> int:
    validate_runtime()
    mode, pins, flags = parse_arguments(list(sys.argv[1:]))
    wall = SourceWall(mode == "--apply")
    wall.install()
    state = load_context(wall, mode, pins)
    if mode == "--render-contract":
        sys.stdout.buffer.write(document(state["contract"]))
    elif mode == "--apply":
        sys.stdout.buffer.write(document(apply_root_only(wall, state, pins, flags)))
    else:
        output = {"schema": SCHEMA + "-source-only-gate", "status": "PASS",
                  "mode": mode[2:], "source_sha256": pins["--source-sha256"],
                  "protocol_sha256": pins["--protocol-sha256"],
                  "contract_sha256": pins["--contract-sha256"],
                  "authenticated_previous_owner_count": len(OWNERS),
                  "actual_v24_rust_candidate_status": "FAIL",
                  "actual_v24_rust_semantic_mismatch_count": 1352,
                  "preserved_failed_v1_receipt_sha256": OWNERS[26][2],
                  "preserved_failed_v1_attempt_count": 2,
                  "linux_full_composite_tmpfile_guard_corrected": True,
                  "original_case_execution_denominator": 31237,
                  "previous_compiler_synthetic_case_count": 960,
                  "previous_compiler_scanner_distinction_count": 42,
                  "previous_compiler_lifetime_control_count": 40,
                  "previous_anchor_differential_case_count": 11328,
                  "combined_synthetic_case_count":
                      state["interaction"]["combined_differential_case_count"],
                  "derived_engine_sha256": LIB_SHA256,
                  "derived_engine_bytes": LIB_BYTES,
                  "derived_search_sha256": SEARCH_SHA256,
                  "derived_search_bytes": SEARCH_BYTES,
                  "source_mutations": 0, "candidate_imports": 0,
                  "candidate_workers_started": 0,
                  "compiler_processes_started": 0,
                  "native_libraries_loaded": 0, "archives_opened": 0,
                  "clock_samples": 0, "holdout_content_open_count": 0,
                  "holdout_metadata_probe_count": 1,
                  "holdout": "NOT OPENED", "performance": NOT_MEASURED,
                  "memory": NOT_MEASURED, "undefined_behavior": NOT_MEASURED,
                  "candidate_correctness": NOT_MEASURED,
                  "qualified_candidate_count": 0, "winner_selected": False}
        if mode == "--self-test":
            output["hostile"] = hostile_self_test(wall, state)
        sys.stdout.buffer.write(document(output))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, UnicodeError, ValueError, TypeError, IndexError,
            KeyError, AttributeError) as error:
        sys.stderr.write("combined first-party source freeze rejected: " + str(error) + "\n")
        raise SystemExit(2)
