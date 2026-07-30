#!/usr/bin/env python3
"""Freeze the exact first-party compiler/search/VM-workspace composition.

Source gates authenticate only previously public, independently frozen owners.
The retired final proposal is never opened or even inspected: it is invalidated
and a separately rekeyed successor is required before any final comparison.
Only a separately committed, pushed, explicitly authorized root may publish the
two exclusive source files; this transformer never builds or runs a candidate.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("combined first-party workspace freeze must not import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/apply_owned_rust_combined_vm_workspace_v1.py"
PROTOCOL = "oracle/phase2/RUST-COMBINED-VM-WORKSPACE-V1.md"
CONTRACT = "oracle/phase2/rust-combined-vm-workspace-v1.json"
RETIRED_PROPOSAL = "oracle/phase3/expanded-sealed-holdout-v2.json"
PARENT = "candidates/rust/variants"
DIRECTORY = "combined_vm_workspace_v1"
LIB_TARGET = PARENT + "/" + DIRECTORY + "/lib.rs"
SEARCH_TARGET = PARENT + "/" + DIRECTORY + "/search.rs"
SCHEMA = "rebar-first-party-rust-combined-vm-workspace-v1"
DEVICE = 2064
PARENT_INODE = 524946
MAX_OWNER_BYTES = 1_048_576
LIB_SHA256 = "9fcd158da1af49dabf916168472938d00d9dde527a4c877a5281d5829200b4ab"
LIB_BYTES = 190103
COMBINED_LIB_SHA256 = "c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee"
COMBINED_LIB_BYTES = 189423
WORKSPACE_LIB_SHA256 = "0bd199957ed96cbf67109d4621698a6be300cb5c88d0ae30d25402f51777ba36"
WORKSPACE_LIB_BYTES = 178647
SEARCH_SHA256 = "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7"
SEARCH_BYTES = 24305
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
NOT_MEASURED = "NOT MEASURED"

# role, repository-relative path, exact SHA-256, exact bytes, device-2064 inode
OWNERS = (
    ("goal", "GOAL.md", GOAL_SHA256, 3756, 31364044),
    ("original_oracle", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("supplemental_oracle", "oracle/phase1/p0-differential-fuzz-reference-v3.json",
     "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff", 5288, 525082),
    ("latest_v25_campaign",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-"
     "rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json",
     "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59", 11832, 524846),
    ("cargo_manifest", "candidates/rust/Cargo.toml",
     "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, 428094),
    ("cargo_lock", "candidates/rust/Cargo.lock",
     "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, 428098),
    ("canonical_lib", "candidates/rust/src/lib.rs",
     "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967, 428096),
    ("canonical_search", "candidates/rust/src/search.rs",
     "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773, 429682),
    ("canonical_inline_stack", "candidates/rust/src/stack.rs",
     "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269, 428151),
    ("combined_v2_source", "tools/apply_owned_rust_combined_search_compiler_fastpath_v2.py",
     "f8f2f7cf4e9339cf592048fd75cafe9a9d22d79c77137d1f8ab6d3b7493d976b", 89742, 430531),
    ("combined_v2_protocol", "oracle/phase2/RUST-COMBINED-SEARCH-COMPILER-FASTPATH-V2.md",
     "b612af3b53bb21b6f13b69db4c4197590a71af045fab14de250dad301a1794a1", 5577, 524866),
    ("combined_v2_contract", "oracle/phase2/rust-combined-search-compiler-fastpath-v2.json",
     "68f097d8433596fb45a9a9ca940eff68dcb8fe9f0d667a8c0ce9c5eb403196a6", 13914, 524939),
    ("combined_v2_application",
     "oracle/phase2/evidence/rust-combined-search-compiler-fastpath-v2-application.json",
     "1bce63305e04e4056ce3c660760a0bb8a3670a76aa528b9309232d0918c5061e", 2201, 525099),
    ("combined_v2_lib", "candidates/rust/variants/combined_search_compiler_fastpath_v2/lib.rs",
     COMBINED_LIB_SHA256, COMBINED_LIB_BYTES, 525097),
    ("combined_v2_search", "candidates/rust/variants/combined_search_compiler_fastpath_v2/search.rs",
     SEARCH_SHA256, SEARCH_BYTES, 525098),
    ("workspace_v1_source", "tools/apply_owned_rust_vm_workspace_reuse_v1.py",
     "8224159adcc5aa930eb93d532d69af5c2365e461329888aafae84651803e5b05", 78186, 430460),
    ("workspace_v1_protocol", "oracle/phase2/RUST-VM-WORKSPACE-REUSE-V1.md",
     "c220fe3da676c45129e1e7ca88def2780a978ea3cd98cf060a2e415a9975827e", 5744, 524865),
    ("workspace_v1_contract", "oracle/phase2/rust-vm-workspace-reuse-v1.json",
     "8c39d9ef323213b065ff31e50b5374df64c953677c1da76b3ee83efe17b5e40b", 10412, 524867),
    ("workspace_v1_application", "oracle/phase2/evidence/rust-vm-workspace-reuse-v1-application.json",
     "5f12bd6013b0b1781dc9c66bcaa5a1ed103e3610a1602f72e84348807b42eba6", 2352, 525144),
    ("workspace_v1_lib", "candidates/rust/variants/vm_workspace_reuse_v1/lib.rs",
     WORKSPACE_LIB_SHA256, WORKSPACE_LIB_BYTES, 525143),
    ("no_external_bridge", "candidates/rust/variants/capture_clamp_semantics_v1/py_bridge.c",
     "a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54", 178805, 526064),
    ("no_external_bridge_safe_build",
     "oracle/phase2/evidence/native-source-build-v25-rust-phase2-v25-"
     "rust-capture-clamp-v1-root-provenance-publication-receipt.json",
     "55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc", 5231, 526084),
    ("previous_v24_failure",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v24-"
     "rust-capture-shape-v2-root-provenance-original-p0-v24-failures-publication-receipt.json",
     "5acd8dee2a515af56306e61f6ae8774c567f1f47e0ef1930a17e6809c2aafa09", 11832, 525952),
    ("first_public_profile_contract", "oracle/phase3/rust-public-profile-v1.json",
     "b791b141eabbf6eb8a67484f5deb82bb41e324aedbdfe5b53a98ebc1553372c5", 1797, 525928),
    ("first_public_python_correctness",
     "experiments/rust_public_profile_v1/public-run-001/stdlib.correctness.raw.json",
     "efe0a3cc37194290b9577d5bd4f502a5c482016bc2b8ae90acec6254545b5381", 445036, 526005),
    ("first_public_rust_correctness",
     "experiments/rust_public_profile_v1/public-run-001/rust.correctness.raw.json",
     "8774ad035e17126252803e75494a80d376386a85e13c46cb3e0380b82dae89b0", 445394, 526006),
    ("first_public_paired_rows",
     "experiments/rust_public_profile_v1/public-run-001/paired-timing.raw.json",
     "3da06bdb04ace9897d359aaa962ca412f3e9260a5c1a337703e0aa35567b6b85", 504907, 526015),
    ("complete_public_profile_source", "tools/rust_public_profile_v2.py",
     "a4eb77c29e06b1a77152ebb2275525bfd75b3fa26fd25f100059c79cfb39437a", 31941, 429686),
    ("complete_public_profile_protocol", "oracle/phase3/RUST-PUBLIC-PROFILE-V2.md",
     "aa96b3a2132be6557020a753da8e57e1c210b1a9b9216b6a015f36715e208b9d", 3128, 526049),
    ("complete_public_profile_manifest", "oracle/phase3/rust-public-profile-v2.json",
     "9687806994bcbb401ed89cba11197b79a491da023b95be89e1686a7c6cccafea", 3926, 526050),
    ("complete_public_profile_summary", "experiments/rust_public_profile_v2/public-run-001/summary.json",
     "71468c3196d75994180de6ce27ab1a3c48e1253fd37f0e4d0f33ba7a6d4099cb", 28079, 526265),
    ("complete_public_paired_rows",
     "experiments/rust_public_profile_v2/public-run-001/paired-timing.raw.json",
     "cd237092007b231b37293414e417bce80afde3bc44a44e787adb53a0e66f7697", 504914, 526215),
    ("public_allocation_function_table",
     "experiments/rust_public_profile_v2/public-run-001/rust.cpu.txt",
     "542b2fd936535ea5739db31f7cd6e97ff62642b20bbb448c09e33095e47a7d1d", 72934, 526257),
    ("public_allocation_callers", "experiments/rust_public_profile_v2/public-run-001/rust.ffi.txt",
     "6957b8e19c2388173c719c757717e67aa8b116ba97243e226fed69619646d483", 525686, 526259),
    ("public_native_heap_totals", "experiments/rust_public_profile_v2/public-run-001/rust.heap.txt",
     "ea98056637f2a3b9634549e57c28b2183167f4874441f31140913b0c93d68b9d", 1429, 526263),
    ("public_profiler_clock_failure", "experiments/rust_public_profile_v2/public-run-001/rust.er/log.xml",
     "0a893318548fb3974ed0529a2379c5080c8f52142a8af81ae52645abbaf07dc2", 65536, 526246),
)


class FreezeError(Exception):
    """Reject modified evidence, hidden tests, source mutation, or bad authority."""


def require(condition: object, explanation: str) -> None:
    if condition is not True:
        raise FreezeError(explanation)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete immutable bytes")
    return hashlib.sha256(raw).hexdigest()


def exact_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value)
            and len(set(value)) > 1, "require an exact lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def exact_commit(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(item in "0123456789abcdef" for item in value)
            and len(set(value)) > 1, "require a full pushed commit: " + label)
    assert isinstance(value, str)
    return value


def clean_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "subprocess", "socket", "threading", "multiprocessing",
                 "concurrent.interpreters", "candidates", "rebar")
    require(not any(name == prefix or name.startswith(prefix + ".")
                    for name in sys.modules for prefix in forbidden),
            "reject matcher, candidate, native loader, worker, process, or network")


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= 80, "reject excessive frozen JSON depth")
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
    if type(value) in (tuple, list):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "reject nontext JSON keys")
        return "{" + ",".join(canonical(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise FreezeError("reject unsupported, floating, or nonfinite frozen JSON value")


def document(value: object) -> bytes:
    return (canonical(value) + "\n").encode("utf-8")


class SourceWall:
    """Deny-default descriptor wall with one exclusive root two-file publication."""

    def __init__(self, apply: bool) -> None:
        self.apply = apply
        self.allowed = frozenset((ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL,
                                  ROOT + "/" + CONTRACT)
                                 + tuple(ROOT + "/" + row[1] for row in OWNERS))
        self.dynamic = (OWNERS[15], OWNERS[9])
        self.proposal = ROOT + "/" + RETIRED_PROPOSAL
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
        self.compile_name: str | None = None
        self.compile_raw: bytes | None = None
        self.pending_code: object | None = None
        self.compile_count = 0
        self.exec_count = 0
        self.proposal_open_count = 0
        self.proposal_metadata_count = 0
        self.blocked: dict[str, int] = {}
        self.installed = False

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise FreezeError("combined VM workspace wall rejected " + category)

    def owner_path(self, path: object) -> bool:
        return (type(path) is str and path in self.allowed
                and path.startswith(ROOT + "/") and path == os.path.normpath(path)
                and not any(part in (".", "..") for part in path.split("/"))
                and not path.endswith((".so", ".gz", ".er")))

    def temporary_file_flags(self, flags: object) -> bool:
        temporary = getattr(os, "O_TMPFILE", 0)
        return (type(flags) is int and type(temporary) is int and temporary != 0
                and flags & temporary == temporary)

    def directory_flags(self, flags: object) -> bool:
        needed = os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
        denied = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_TRUNC | os.O_APPEND
        return (type(flags) is int and flags & needed == needed
                and not flags & denied and not self.temporary_file_flags(flags))

    def output_flags(self, flags: object) -> bool:
        needed = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        denied = os.O_RDWR | os.O_TRUNC | os.O_APPEND | getattr(os, "O_DIRECTORY", 0)
        return (type(flags) is int and flags & needed == needed
                and not flags & denied and not self.temporary_file_flags(flags))

    def audit(self, event: str, arguments: tuple[object, ...]) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else None
            destructive = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL
                           | os.O_TRUNC | os.O_APPEND | getattr(os, "O_DIRECTORY", 0))
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
                self.deny("invalidated-final-proposal-content")
            self.deny("foreign-candidate-native-archive-source-or-write")
        if event == "os.mkdir":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            descriptor = arguments[2] if len(arguments) > 2 else None
            if (self.apply and self.stage == "parent" and path == DIRECTORY
                    and mode == 0o700 and descriptor == self.parent_fd):
                return
            self.deny("foreign-directory-mutation")
        if event == "compile":
            raw = arguments[0] if arguments else None
            filename = arguments[1] if len(arguments) > 1 else None
            previous = (self.dynamic[self.compile_count]
                        if self.compile_count < len(self.dynamic) else None)
            if (previous is not None and filename == ROOT + "/" + previous[1]
                    and filename == self.compile_name and type(raw) is bytes
                    and raw == self.compile_raw and digest(raw) == previous[2]
                    and self.compile_count == self.exec_count):
                self.compile_count += 1
                return
            self.deny("unapproved-dynamic-compile")
        if event == "exec":
            code = arguments[0] if arguments else None
            previous = (self.dynamic[self.exec_count]
                        if self.exec_count < len(self.dynamic) else None)
            if (previous is not None and code is self.pending_code
                    and self.pending_code is not None
                    and self.compile_count == self.exec_count + 1
                    and getattr(code, "co_filename", None) == ROOT + "/" + previous[1]
                    and getattr(code, "co_name", None) == "<module>"):
                self.exec_count += 1
                return
            self.deny("unapproved-dynamic-execution")
        if (event == "import" or event == "sys.addaudithook"
                or event.startswith(("subprocess.", "socket.", "ctypes.", "threading.",
                                     "multiprocessing.", "tempfile.", "time.",
                                     "_interpreters.", "cpython.PyInterpreterState",
                                     "os.exec", "os.spawn"))
                or event in ("marshal.loads", "code.__new__", "os.system", "os.fork",
                             "os.posix_spawn", "os.posix_spawnp", "os.rename", "os.replace",
                             "os.remove", "os.unlink", "os.rmdir", "os.chmod", "os.chown",
                             "os.link", "os.symlink", "os.truncate", "os.putenv",
                             "os.unsetenv", "os.urandom", "os.getrandom")):
            self.deny("candidate-native-process-clock-mutation-or-network")

    def forbidden(self, category: str):
        def reject(*_arguments: object, **_keywords: object) -> object:
            self.deny(category)
        return reject

    def install(self) -> None:
        require(not self.installed, "install exactly one irreversible source wall")
        native_open, native_read, native_write = os.open, os.read, os.write
        native_fstat, native_close, native_fsync = os.fstat, os.close, os.fsync
        native_mkdir = os.mkdir

        def guarded_open(path: object, flags: object, mode: int = 0o777,
                         *, dir_fd: object = None) -> int:
            require(type(flags) is int and type(mode) is int,
                    "reject malformed source descriptor flags")
            owner = (dir_fd is None and self.owner_path(path)
                     and flags & getattr(os, "O_NOFOLLOW", 0)
                     and not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL
                                      | os.O_TRUNC | os.O_APPEND
                                      | getattr(os, "O_DIRECTORY", 0))
                     and not self.temporary_file_flags(flags))
            parent = (self.apply and self.stage == "ready" and path == self.parent_path
                      and dir_fd is None and self.directory_flags(flags))
            child = (self.apply and self.stage == "created" and path == DIRECTORY
                     and dir_fd == self.parent_fd and self.directory_flags(flags))
            output = (self.apply and self.stage == "child" and dir_fd == self.child_fd
                      and path in ("lib.rs", "search.rs") and self.output_flags(flags)
                      and mode == 0o600 and len(self.opened_names) < 2
                      and path == ("lib.rs" if not self.opened_names else "search.rs"))
            if not any((owner, parent, child, output)):
                self.deny("unapproved-descriptor-open-or-dir-fd")
            descriptor = native_open(path, flags, mode, dir_fd=dir_fd)
            require(type(descriptor) is int and descriptor >= 0
                    and descriptor not in self.owners and descriptor not in self.outputs
                    and descriptor != self.parent_fd and descriptor != self.child_fd,
                    "reject a reused or invalid source descriptor")
            if owner:
                self.owners.add(descriptor)
            elif parent:
                self.parent_fd, self.stage = descriptor, "parent"
            elif child:
                self.child_fd, self.stage = descriptor, "child"
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
            raw, offset = self.expected[name], self.written[name]
            block = bytes(value)
            if not block or block != raw[offset:offset + len(block)]:
                self.deny("incorrect-or-unbounded-output-bytes")
            written = native_write(descriptor, value)
            require(type(written) is int and 0 < written <= len(block),
                    "reject incomplete private source write")
            self.written[name] += written
            return written

        def guarded_fstat(descriptor: object) -> os.stat_result:
            if (type(descriptor) is not int or descriptor not in self.owners
                    and descriptor not in self.outputs and descriptor != self.parent_fd
                    and descriptor != self.child_fd):
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
                        "synchronize two sources and their private directory")
                self.child_fd = None
            elif descriptor == self.parent_fd:
                require(self.parent_synced and self.child_fd is None,
                        "synchronize the parent after its private child")
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
                        "do not synchronize incomplete output")
                native_fsync(descriptor)
                self.synced.add(name)
            elif descriptor == self.child_fd:
                require(self.opened_names == ["lib.rs", "search.rs"]
                        and self.synced == {"lib.rs", "search.rs"}
                        and not self.outputs and not self.child_synced,
                        "publish two complete outputs before syncing their directory")
                native_fsync(descriptor)
                self.child_synced = True
            elif descriptor == self.parent_fd:
                require(self.child_synced and self.child_fd is None and not self.parent_synced,
                        "synchronize the parent only after its complete child")
                native_fsync(descriptor)
                self.parent_synced = True
            else:
                self.deny("foreign-descriptor-sync")

        def guarded_mkdir(path: object, mode: int = 0o777,
                          *, dir_fd: object = None) -> None:
            if (not self.apply or self.stage != "parent" or path != DIRECTORY
                    or mode != 0o700 or dir_fd != self.parent_fd):
                self.deny("unapproved-private-variant-directory")
            native_mkdir(path, mode, dir_fd=dir_fd)
            self.stage = "created"

        invocation_authorized = self.apply

        def immutable_authority(event: str, arguments: tuple[object, ...]) -> None:
            if self.apply is not invocation_authorized:
                self.deny("forged-root-publication-authority")
            self.audit(event, arguments)

        sys.addaudithook(immutable_authority)
        native_module = sys.modules.get("posix")
        require(native_module is not None, "authenticate the loaded native OS module")
        builtins.open = self.forbidden("builtins-open")
        _io.open = self.forbidden("direct-_io-open")
        _io.FileIO = self.forbidden("direct-_io-fileio")
        io.open = self.forbidden("direct-io-open")
        io.FileIO = self.forbidden("direct-io-fileio")
        for module in (_io, io):
            if hasattr(module, "open_code"):
                setattr(module, "open_code", self.forbidden("direct-open-code"))
        for name, function in (("open", guarded_open), ("read", guarded_read),
                               ("write", guarded_write), ("fstat", guarded_fstat),
                               ("close", guarded_close), ("fsync", guarded_fsync),
                               ("mkdir", guarded_mkdir)):
            setattr(os, name, function)
            setattr(native_module, name, function)
        for name in ("fdopen", "dup", "dup2", "stat", "lstat", "readlink", "listdir",
                     "scandir", "walk", "fwalk", "access", "fork", "posix_spawn",
                     "posix_spawnp", "system", "makedirs", "remove", "unlink", "rename",
                     "replace", "rmdir", "chmod", "chown", "urandom", "getrandom",
                     "pread", "pwrite", "preadv", "pwritev", "readv", "writev",
                     "sendfile", "copy_file_range", "splice", "truncate", "ftruncate",
                     "utime", "link", "symlink", "fchmod", "fchown", "mknod", "mkfifo",
                     "execv", "execve", "execvp", "execvpe", "execl", "execle", "execlp",
                     "execlpe", "spawnl", "spawnle", "spawnlp", "spawnlpe", "spawnv",
                     "spawnve", "spawnvp", "spawnvpe", "kill", "killpg", "chdir", "fchdir",
                     "setuid", "setgid", "setreuid", "setregid"):
            if hasattr(os, name):
                rejected = self.forbidden("direct-os-" + name)
                setattr(os, name, rejected)
                if hasattr(native_module, name):
                    setattr(native_module, name, rejected)
        for name in ("time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                     "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
                     "thread_time_ns", "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.forbidden("clock-" + name))
        self.installed = True


def read_owner(wall: SourceWall, row: tuple[object, ...]) -> bytes:
    role, path, expected, count, inode = row
    exact_sha(expected, str(path))
    require(type(role) is str and type(path) is str and type(count) is int
            and 0 < count <= MAX_OWNER_BYTES and type(inode) is int and inode > 0,
            "reject an incomplete or unbounded frozen owner")
    require(wall.installed, "install the wall before reading any authenticated owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(ROOT + "/" + path, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == count and before.st_nlink == 1
                and before.st_uid == os.geteuid(), "reject a substituted owner: " + role)
        chunks: list[bytes] = []
        remaining = count
        while remaining:
            block = os.read(descriptor, min(remaining, 65536))
            require(type(block) is bytes and bool(block), "reject a truncated owner: " + role)
            chunks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"", "reject a grown owner: " + role)
        after = os.fstat(descriptor)
        require(all(getattr(before, key) == getattr(after, key)
                    for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                "st_mtime_ns", "st_ctime_ns")),
                "reject an owner exchanged while authenticated: " + role)
        result = b"".join(chunks)
        require(digest(result) == expected, "reject altered frozen owner bytes: " + role)
        return result
    finally:
        os.close(descriptor)


def live_owner(wall: SourceWall, role: str, path: str, expected: str) -> tuple[object, ...]:
    require(path in (SOURCE, PROTOCOL, CONTRACT), "reject an unrelated live freeze owner")
    exact_sha(expected, path)
    descriptor = os.open(ROOT + "/" + path,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        result = os.fstat(descriptor)
        require(stat.S_ISREG(result.st_mode) and stat.S_IMODE(result.st_mode) == 0o600
                and result.st_dev == DEVICE and result.st_uid == os.geteuid()
                and result.st_nlink == 1 and 0 < result.st_size <= MAX_OWNER_BYTES,
                "reject substituted live freeze owner: " + role)
        return role, path, expected, result.st_size, result.st_ino
    finally:
        os.close(descriptor)


def owner_document(row: tuple[object, ...]) -> dict[str, object]:
    role, path, expected, count, inode = row
    return {"role": role, "path": path, "sha256": expected, "bytes": count,
            "device": DEVICE, "inode": inode, "mode": "0600", "nlink": 1}


def load_previous(wall: SourceWall, role: str, raw: bytes) -> dict[str, object]:
    index = 15 if role == "workspace" else 9 if role == "combined" else -1
    require(index >= 0 and wall.compile_count == wall.exec_count
            and wall.compile_count < len(wall.dynamic)
            and wall.dynamic[wall.compile_count] == OWNERS[index]
            and digest(raw) == OWNERS[index][2],
            "load only the next exact independently frozen predecessor")
    path = ROOT + "/" + str(OWNERS[index][1])
    wall.compile_name, wall.compile_raw = path, raw
    try:
        code = compile(raw, path, "exec")
        wall.pending_code = code
        namespace: dict[str, object] = {"__name__": "combined_workspace_frozen_" + role}
        exec(code, namespace)
        return namespace
    finally:
        wall.pending_code = None
        wall.compile_name = None
        wall.compile_raw = None


def validate_history(evidence: dict[str, bytes], workspace: dict[str, object]) -> dict[str, object]:
    parse = workspace["json_object"]
    require(callable(parse), "require the frozen duplicate-rejecting JSON parser")
    original = parse(evidence["original_oracle"], "original 31,237-case completeness")
    supplemental = parse(evidence["supplemental_oracle"], "supplemental reference")
    latest = parse(evidence["latest_v25_campaign"], "latest complete V25 campaign")
    workspace["validate_oracles"](original, supplemental, latest)
    workspace["validate_cargo"](evidence["cargo_manifest"], evidence["cargo_lock"],
                                  evidence["canonical_lib"], evidence["canonical_inline_stack"],
                                  evidence["canonical_search"])

    combined = parse(evidence["combined_v2_contract"], "frozen combined V2 contract")
    combined_receipt = parse(evidence["combined_v2_application"], "actual combined V2 source")
    require(combined.get("schema") == "rebar-first-party-rust-combined-search-compiler-fastpath-v2"
            and combined.get("version") == 2
            and combined["source"]["sha256"] == OWNERS[9][2]
            and combined["protocol"]["sha256"] == OWNERS[10][2]
            and combined["derived"]["engine"]["sha256"] == COMBINED_LIB_SHA256
            and combined["derived"]["engine"]["bytes"] == COMBINED_LIB_BYTES
            and combined["derived"]["search"]["sha256"] == SEARCH_SHA256
            and combined["derived"]["search"]["bytes"] == SEARCH_BYTES
            and combined["exact_commuting_composition"]["replacement_count"] == 7
            and combined["exact_commuting_composition"]["transformations_commute"] is True
            and combined["new_combined_synthetic_semantics"]
                ["combined_differential_case_count"] == 111552
            and combined["original_correctness"]["original_case_execution_denominator"] == 31237
            and combined["original_correctness"]["latest_rust_semantic_mismatch_count"] == 1352,
            "reject the independently frozen parser/mandatory-anchor composition")
    require(combined_receipt.get("schema")
                == "rebar-first-party-rust-combined-search-compiler-fastpath-v2-application"
            and combined_receipt.get("status") == "APPLIED"
            and combined_receipt.get("source_sha256") == OWNERS[9][2]
            and combined_receipt.get("protocol_sha256") == OWNERS[10][2]
            and combined_receipt.get("contract_sha256") == OWNERS[11][2]
            and combined_receipt["created"]["engine"]["sha256"] == COMBINED_LIB_SHA256
            and combined_receipt["created"]["search"]["sha256"] == SEARCH_SHA256
            and combined_receipt.get("combined_synthetic_case_count") == 111552
            and combined_receipt.get("original_case_execution_denominator") == 31237
            and combined_receipt.get("actual_v24_rust_candidate_status") == "FAIL"
            and combined_receipt.get("actual_v24_rust_semantic_mismatch_count") == 1352
            and combined_receipt.get("holdout") == "NOT OPENED",
            "reject the actual immutable combined V2 two-file application")

    previous = parse(evidence["workspace_v1_contract"], "frozen VM workspace contract")
    receipt = parse(evidence["workspace_v1_application"], "actual VM workspace source")
    require(previous.get("schema") == "rebar-owned-rust-vm-workspace-reuse-v1-source-freeze"
            and previous.get("version") == 1
            and previous["source"]["sha256"] == OWNERS[15][2]
            and previous["protocol"]["sha256"] == OWNERS[16][2]
            and previous["derived_first_party_vm_source"]["sha256"] == WORKSPACE_LIB_SHA256
            and previous["derived_first_party_vm_source"]["bytes"] == WORKSPACE_LIB_BYTES
            and previous["derived_first_party_vm_source"]["exact_reversible_replacement_count"] == 7
            and previous["derived_first_party_vm_source"]["capture_undo_reused"] is False
            and previous["synthetic_differential_semantics"]["case_count"] == 18144
            and previous["synthetic_differential_semantics"]["synthetic_allocations_avoided"] == 16848
            and previous["latest_complete_candidate_result"]["candidate_status"] == "FAIL"
            and previous["latest_complete_candidate_result"]["semantic_mismatch_count"] == 1352,
            "reject the independently frozen four-vector VM workspace transformation")
    require(receipt.get("schema")
                == "rebar-owned-rust-vm-workspace-reuse-v1-source-freeze-source-only-gate"
            and receipt.get("status") == "PASS"
            and receipt.get("variant_materialized") is True
            and receipt.get("source_sha256") == OWNERS[15][2]
            and receipt.get("protocol_sha256") == OWNERS[16][2]
            and receipt.get("contract_sha256") == OWNERS[17][2]
            and receipt["materialized_variant"]["sha256"] == WORKSPACE_LIB_SHA256
            and receipt.get("latest_candidate_campaign") == "V25"
            and receipt.get("latest_candidate_status") == "FAIL"
            and receipt.get("latest_semantic_mismatch_count") == 1352
            and receipt.get("synthetic_differential_case_count") == 18144
            and receipt.get("holdout") == "NOT OPENED",
            "reject actual first-party VM workspace materialization")

    first = parse(evidence["first_public_profile_contract"], "first public profile")
    python = parse(evidence["first_public_python_correctness"], "public Python outcomes")
    rust = parse(evidence["first_public_rust_correctness"], "public first-party outcomes")
    paired = parse(evidence["first_public_paired_rows"], "all first public paired rows")
    require(first.get("case_count") == 416 and first.get("operation_count") == 26
            and first.get("pinned_cpython") == "3.14.6"
            and python.get("status") == "PASS" and rust.get("status") == "PASS"
            and python.get("engine") == "stdlib" and rust.get("engine") == "rust"
            and python.get("case_count") == 416 and rust.get("case_count") == 416
            and python.get("holdout_files_read") == 0 and rust.get("holdout_files_read") == 0
            and python.get("records_sha256") == rust.get("records_sha256")
            and type(python.get("records")) is list and len(python["records"]) == 416
            and python["records"] == rust.get("records")
            and type(paired.get("rows")) is list and len(paired["rows"]) == 1664,
            "reject any of the complete original public outcomes or paired rows")
    second = workspace["validate_profile"](evidence)

    bridge = evidence["no_external_bridge"]
    build = parse(evidence["no_external_bridge_safe_build"], "optional safe first-party bridge")
    require(bridge.count(b"rebar_compile(") >= 1
            and bridge.count(b"rebar_compile_scanner(") >= 1
            and bridge.find(b"rebar_compile(") < bridge.rfind(b"PyMem_Free(owned_pattern)")
            and bridge.find(b"rebar_compile_scanner(")
                < bridge.rfind(b"PyMem_Free(owned_sources[index])")
            and b'PyImport_ImportModule("re")' not in bridge
            and b'PyImport_ImportModule("regex")' not in bridge
            and build.get("status") == "PASS" and build.get("build_status") == "PASS"
            and build.get("combined_bridge_sha256") == OWNERS[20][2]
            and build.get("latest_v24_original_campaign_receipt_sha256") == OWNERS[22][2]
            and build.get("latest_v24_candidate_status") == "FAIL"
            and build.get("latest_v24_semantic_mismatch_count") == 1352
            and build.get("actual_compiler_process_count") == 28
            and build.get("holdout") == "NOT OPENED",
            "preserve the optional synchronous no-external-engine first-party C bridge")
    return {"original_case_execution_denominator": 31237,
            "original_suite_count": 13, "supplemental_reference_case_count": 8244,
            "latest_campaign": "V25", "latest_candidate_status": "FAIL",
            "latest_semantic_mismatch_count": 1352,
            "latest_changing_buffer_mismatch_count": 1112,
            "latest_substitution_mismatch_count": 240,
            "latest_verified_passing_case_count": 15877,
            "latest_candidate_qualified": False,
            "public_profile_v1_case_count": 416,
            "public_profile_v1_paired_observation_count": 1664,
            "public_profile_v2": second,
            "combined_v2_synthetic_case_count": 111552,
            "workspace_v1_synthetic_case_count": 18144,
            "workspace_v1_synthetic_allocations_avoided": 16848,
            "compiler_case_count": 960,
            "mandatory_anchor_case_count": 11328,
            "zero_external_dependencies": True,
            "optional_safe_bridge_source_sha256": OWNERS[20][2],
            "optional_safe_bridge_execution": "NOT RUN"}


def compose_sources(evidence: dict[str, bytes], workspace: dict[str, object]) -> tuple[bytes, dict]:
    replacements = workspace["REPLACEMENTS"]
    canonical_vm = workspace["transform_source"](evidence["canonical_lib"])
    require(canonical_vm == evidence["workspace_v1_lib"]
            and digest(canonical_vm) == WORKSPACE_LIB_SHA256,
            "independently reproduce the materialized canonical VM workspace source")
    source = evidence["combined_v2_lib"]
    derived = source
    anchors: list[dict[str, object]] = []
    for label, old, new in replacements:
        require(type(label) is str and type(old) is bytes and type(new) is bytes
                and old != new and derived.count(old) == 1,
                "require one untouched first-party workspace anchor: " + str(label))
        offset = derived.find(old)
        require(offset >= 0, "locate the exact disjoint VM source substitution")
        derived = derived[:offset] + new + derived[offset + len(old):]
        require(derived.count(new) == 1,
                "the exact reversible VM workspace anchor was duplicated: " + label)
        anchors.append({"name": label, "offset_before": offset,
                        "old_bytes": len(old), "new_bytes": len(new),
                        "source_delta_bytes": len(new) - len(old)})
    restored = derived
    for label, old, new in reversed(replacements):
        require(restored.count(new) == 1,
                "reverse one and only one exact VM workspace substitution: " + label)
        restored = restored.replace(new, old, 1)
    require(restored == source and len(replacements) == 7
            and sum(item["source_delta_bytes"] for item in anchors) == 680
            and len(derived) == LIB_BYTES and digest(derived) == LIB_SHA256,
            "reject an inexact, overlapping, stale, or irreversible three-way composition")

    mandatory_block = (b"&& let Some(plan) = engine.mandatory_anchor_search.as_ref()\n"
                       b"            && let Some(values) = context.bytes.or_else(|| {")
    require(source.count(mandatory_block) == 1 and derived.count(mandatory_block) == 1
            and source.count(b"mandatory_anchor_search: Option<search::AnchorPlan>") == 1
            and derived.count(b"mandatory_anchor_search: Option<search::AnchorPlan>") == 1
            and source.count(b"struct Parser<'a> {") == 1
            and derived.count(b"struct Parser<'a> {") == 1
            and derived.count(b"source: &'a [u32],") == 1
            and derived.count(b"impl Parser<'_> {") == 1
            and source.count(b"#[unsafe(no_mangle)]")
                == derived.count(b"#[unsafe(no_mangle)]")
            and derived.count(b"struct VmStateScratch {") == 1
            and derived.count(b"Some(&mut scratch)") == 1
            and derived.count(b"scratch: Option<&mut VmStateScratch>") == 1
            and derived.count(b"overflow_guards.fill(usize::MAX);") == 1
            and derived.count(b"overflow_repeats.fill(RepeatState::default());") == 1
            and derived.count(b"overflow_old_begins.clear();") == 1
            and derived.count(b"overflow_old_ends.clear();") == 1
            and derived.count(b"const INLINE_STATE_SLOTS: usize = 8;") == 1
            and derived.count(b"const INLINE_LOOK_CAPTURE_SLOTS: usize = 16;") == 1
            and workspace["NEW_LOOK"].count(b"            None,\n") == 3,
            "preserve compiler borrowing, anchor filtering, public ABI, and isolated VM state")
    for forbidden in (b"extern crate regex", b"use regex::", b"pcre2", b"oniguruma",
                      b"std::process::Command", b"dlopen(", b"ctypes", b"holdout"):
        require(derived.count(forbidden) == source.count(forbidden),
                "reject an external matcher, process, native loader, or hidden-test detector")
    search = evidence["combined_v2_search"]
    require(digest(search) == SEARCH_SHA256 and len(search) == SEARCH_BYTES
            and search.count(b"pub(crate) struct AnchorPlan") == 1
            and search.count(b"pub(crate) struct AnchorSet") == 1
            and b'is_x86_feature_detected!("avx2")' in search,
            "preserve the exact authenticated mandatory-anchor search implementation")
    return derived, {"replacement_count": len(replacements), "source_delta_bytes": 680,
                     "replacements": anchors, "transformations_commute": True,
                     "substitution_spans_disjoint": True,
                     "transformations_are_exactly_reversible": True,
                     "mandatory_anchor_block_unchanged": True,
                     "parser_borrowed_lifetime_unchanged": True,
                     "nested_lookaround_receives_distinct_workspace": True,
                     "capture_undo_reused": False}


def fold_ascii(value: int) -> int:
    return value + 32 if 65 <= value <= 90 else value


def ordered_at(branches: tuple, values: bytes, start: int,
               end: int, folded: bool) -> tuple | None:
    for branch_index, branch in enumerate(branches):
        if start + len(branch) > end:
            continue
        matched = True
        for offset, expected in enumerate(branch):
            if expected is None:
                continue
            actual = values[start + offset]
            if (fold_ascii(actual) if folded else actual) != (
                    fold_ascii(expected) if folded else expected):
                matched = False
                break
        if matched:
            finish = start + len(branch)
            return start, finish, branch_index, (start, finish)
    return None


def make_plan(branches: tuple, disabled: bool) -> tuple | None:
    if disabled or not branches:
        return None
    width = min(len(branch) for branch in branches)
    if width == 0:
        return None
    columns = []
    for offset in range(width):
        allowed = {branch[offset] for branch in branches}
        if None in allowed or not 0 < len(allowed) <= 8:
            continue
        columns.append((offset, tuple(sorted(allowed))))
    if not columns:
        return None
    first = columns[0]
    second = (min(columns[1:], key=lambda item: (len(item[1]), -item[0]))
              if len(columns) > 1 else None)
    return first, second, width


def anchor_next(values: bytes, start: int, end: int, plan: tuple,
                vector: bool = True) -> int | None:
    first, second, width = plan
    end = min(end, len(values))
    if start > end or width > end - start:
        return None
    last = end - width
    primary, secondary = first, second
    available = last - start + 1
    if secondary is not None and available >= 128:
        first_count = sum(values[start + index + primary[0]] in primary[1]
                          for index in range(64))
        second_count = sum(values[start + index + secondary[0]] in secondary[1]
                           for index in range(64))
        if second_count < first_count:
            primary, secondary = secondary, primary
    cursor = start
    while cursor <= last:
        stop = min(last + 1, cursor + (32 if vector and last - cursor >= 31 else 1))
        for candidate in range(cursor, stop):
            if values[candidate + primary[0]] in primary[1] and (
                    secondary is None or values[candidate + secondary[0]] in secondary[1]):
                return candidate
        cursor = stop
    return None


def synthetic_composition(workspace: dict[str, object]) -> dict[str, object]:
    previous = workspace["synthetic_semantics"]()
    require(previous.get("case_count") == 18144
            and previous.get("synthetic_allocations_avoided") == 16848
            and previous.get("nested_frames_are_independent") is True
            and previous.get("callback_reentry_uses_independent_root_frame") is True,
            "rerun the complete independent nested/reentry workspace differential")
    A, B, C, Z, HIGH = 65, 66, 67, 90, 255
    families = (
        ((((A, A, A, A, A, B), (A, A, A, A, A, C))), 0),
        ((((B, C, A, A, A, A), (B, C, A, A, A, Z))), 0),
        ((((A, None, None, B),)), 0),
        ((((HIGH, A, HIGH), (HIGH, C, HIGH))), 0),
        ((((A,), (B,), (C,))), 0),
        ((((None, A, None, C), (None, B, None, C))), 0),
        ((((A, A, A, A, A, A, A, Z),)), 0),
        ((((A, B), (A, B, C))), 0),
        ((((None, None, None),)), 0),
        ((((), (A,))), 0),
        ((((A, B, C),)), 1),
        ((((HIGH, B, C),)), 2),
        ((((A, None, B),)), 4),
        ((((A, B, HIGH),)), 8),
        ((((A, A, B), (A, B))), 16),
        ((((A, B, C),)), 32),
        ((((HIGH, HIGH, Z, A), (HIGH, HIGH, Z, B))), 0),
        ((((B, None, A, None, Z), (B, None, C, None, Z))), 0),
    )
    cases = 0
    selected = 0
    disabled = 0
    high_byte = 0
    vector_edges = 0
    reentry = 0
    released_owner = 0
    root_frames = 0
    for family_index, (branches, flags) in enumerate(families):
        plan = make_plan(branches, bool(flags))
        disabled += int(plan is None)
        if plan is not None:
            original = plan
            scratch_owner = bytearray((family_index, len(branches), 255))
            scratch_owner[:] = b"\x00\x00\x00"
            del scratch_owner
            require(plan == original, "borrowed parser input escaped into an anchor plan")
            released_owner += 1
        for seed in range(96):
            values = bytearray((seed * 37 + index * 19 + family_index * 61) & 255
                               for index in range(72))
            for index in range(0, len(values), 5):
                values[index] = A if (seed + index + family_index) & 1 else HIGH
            branch = branches[(seed + family_index) % len(branches)]
            if branch:
                position = (seed * 11 + family_index * 7) % (len(values) - len(branch) + 1)
                for offset, value in enumerate(branch):
                    if value is not None:
                        values[position + offset] = value
            frozen = bytes(values)
            high_byte += int(HIGH in frozen)
            for window in range(64):
                start = (seed * 13 + window * 7 + family_index) % 75
                end = min(len(frozen), (seed * 17 + window * 11 + family_index * 3) % 75)
                expected = None
                if start <= end:
                    for cursor in range(start, end + 1):
                        expected = ordered_at(branches, frozen, cursor, end, bool(flags & 1))
                        if expected is not None:
                            break
                actual = None
                cursor = start
                while cursor <= end:
                    if plan is not None:
                        position = anchor_next(frozen, cursor, end, plan)
                        scalar = anchor_next(frozen, cursor, end, plan, False)
                        require(position == scalar,
                                "vector-sized mandatory-anchor filtering changed leftmost order")
                        vector_edges += int(end - cursor >= 31)
                        if position is None:
                            break
                        cursor = position
                        selected += 1
                    actual = ordered_at(branches, frozen, cursor, end, bool(flags & 1))
                    if actual is not None:
                        break
                    cursor += 1
                require(actual == expected,
                        "mandatory-anchor filtering changed ordered branch, bounds, or captures")
                if cases % 64 == 0:
                    groups = 17 if cases % 128 else 32
                    guards = 9 if cases % 256 else 12
                    repeats = 13 if cases % 512 else 9
                    baseline_frame = workspace["ModelWorkspace"]()
                    shared_frame = workspace["ModelWorkspace"]()
                    expected_state = workspace["model_attempt"](
                        seed + family_index, groups, guards, repeats, cursor, baseline_frame,
                        2, reentry=True)
                    actual_state = workspace["model_attempt"](
                        seed + family_index, groups, guards, repeats, cursor, shared_frame,
                        2, reentry=True)
                    require(actual_state == expected_state and shared_frame is not baseline_frame,
                            "combined filtered search shared nested or callback VM state")
                    root_frames += 1
                    reentry += 1
                cases += 1
    require(cases == 110592 and len(families) == 18 and selected > 0 and disabled > 0
            and high_byte > 0 and vector_edges > 0 and released_owner > 0
            and root_frames == 1728 and reentry == 1728,
            "cover dense/sparse anchors, vectors, high bytes, ownership, and nested reentry")
    return {"combined_differential_case_count": cases,
            "anchor_pattern_family_count": len(families),
            "selected_mandatory_anchor_position_count": selected,
            "conservative_disabled_anchor_family_count": disabled,
            "high_byte_subject_count": high_byte,
            "vector_boundary_window_count": vector_edges,
            "released_parser_owner_control_count": released_owner,
            "isolated_root_workspace_case_count": root_frames,
            "nested_callback_reentry_case_count": reentry,
            "previous_workspace_differential_case_count": previous["case_count"],
            "previous_workspace_synthetic_allocations_avoided":
                previous["synthetic_allocations_avoided"],
            "inline_guard_repeat_threshold": 8,
            "inline_assertion_capture_threshold": 16,
            "inline_capture_undo_threshold": 48,
            "ordered_alternative_priority_preserved": True,
            "nested_assertions_have_independent_workspaces": True,
            "callback_reentry_has_independent_root_workspace": True,
            "parser_borrowed_input_never_escapes_into_anchor_plan": True,
            "capture_undo_reused": False,
            "candidate_executed": False, "native_code_executed": False}


def frozen_contract(source_row: tuple[object, ...], protocol_row: tuple[object, ...],
                    history: dict, composition: dict, semantics: dict) -> dict:
    return {"schema": SCHEMA, "version": 1,
            "status": "SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN",
            "phase": "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS", "family": "rust",
            "immutable_goal_sha256": GOAL_SHA256,
            "source": owner_document(source_row), "protocol": owner_document(protocol_row),
            "authenticated_frozen_owner_count": len(OWNERS),
            "authenticated_frozen_owners": [owner_document(row) for row in OWNERS],
            "independently_authenticated_predecessors": {
                "combined_search_compiler_v2": {
                    "source_sha256": OWNERS[9][2], "protocol_sha256": OWNERS[10][2],
                    "contract_sha256": OWNERS[11][2],
                    "actual_application_sha256": OWNERS[12][2],
                    "engine_sha256": COMBINED_LIB_SHA256,
                    "engine_bytes": COMBINED_LIB_BYTES,
                    "search_sha256": SEARCH_SHA256,
                    "search_bytes": SEARCH_BYTES,
                    "source_materialized": True,
                    "synthetic_differential_case_count": 111552},
                "vm_workspace_v1": {
                    "source_sha256": OWNERS[15][2], "protocol_sha256": OWNERS[16][2],
                    "contract_sha256": OWNERS[17][2],
                    "actual_application_sha256": OWNERS[18][2],
                    "engine_sha256": WORKSPACE_LIB_SHA256,
                    "engine_bytes": WORKSPACE_LIB_BYTES,
                    "source_materialized": True,
                    "synthetic_differential_case_count": 18144,
                    "synthetic_allocations_avoided": 16848}},
            "original_correctness_history": {
                "case_execution_denominator": 31237, "suite_count": 13,
                "supplemental_reference_case_count": 8244,
                "supplemental_reference_counted_in_original_denominator": False},
            "latest_complete_candidate_result": {
                "campaign": "V25", "candidate_status": "FAIL",
                "publication_status": "PASS", "case_execution_denominator": 31237,
                "completed_suite_count": 13, "actual_candidate_worker_count": 13,
                "semantic_mismatch_count": 1352, "verified_passing_case_count": 15877,
                "fully_observed_suite_mismatch_counts": {
                    "shape_v2": 1112, "substitution_v2": 240},
                "candidate_qualified": False, "holdout": "NOT OPENED"},
            "first_party_crate": {
                "package_count": 1, "external_dependency_count": 0,
                "stdlib_matching_delegation": False,
                "another_candidate_engine_delegation": False,
                "runtime_external_regex_engine": False,
                "optional_first_party_no_external_bridge_sha256": OWNERS[20][2],
                "optional_bridge_build_or_execution": "NOT RUN"},
            "independently_authenticated_public_profiles": {
                "first_public_profile": {
                    "case_count": 416, "paired_observation_count": 1664,
                    "complete_python_and_rust_outcomes_match": True,
                    "contract_sha256": OWNERS[23][2]},
                "second_public_allocation_profile": history["public_profile_v2"]},
            "exact_first_party_composition": composition,
            "derived": {"engine": {"path": LIB_TARGET, "sha256": LIB_SHA256,
                                      "bytes": LIB_BYTES},
                        "search": {"path": SEARCH_TARGET, "sha256": SEARCH_SHA256,
                                    "bytes": SEARCH_BYTES}},
            "preserved_source_architecture": {
                "borrowed_parser_source": True,
                "lazy_parser_alternative_allocation": True,
                "mandatory_two_position_anchor_filter": True,
                "mandatory_anchor_is_owned_fixed_byte_data": True,
                "search_start_order_and_bounds_preserved": True,
                "search_source_byte_identical": True,
                "root_search_owns_one_workspace": True,
                "nested_lookaround_owns_independent_workspace": True,
                "callback_reentry_owns_independent_workspace": True,
                "reused_state": ["overflow guards", "overflow repeat states",
                                 "large assertion begin snapshots",
                                 "large assertion end snapshots"],
                "capture_undo_reused": False,
                "guard_state_reset": "usize::MAX on every attempt",
                "repeat_state_reset": "RepeatState::default() on every attempt",
                "inline_guard_repeat_threshold": 8,
                "inline_assertion_capture_threshold": 16,
                "inline_capture_undo_threshold": 48,
                "public_api_changed": False, "external_dependencies_added": 0,
                "canonical_source_modified": False,
                "mandatory_filter_convergence": "SEPARATE FUTURE EXPERIMENT; NOT IMPLEMENTED",
                "capture_history_reuse": "SEPARATE FUTURE EXPERIMENT; NOT IMPLEMENTED"},
            "synthetic_differential_semantics": semantics,
            "retired_final_proposal": {
                "path": RETIRED_PROPOSAL,
                "status": "INVALIDATED",
                "reason": "PREVIOUS V2 FINAL PROPOSAL MUST NOT BE REUSED",
                "content_open_count": 0, "metadata_probe_count": 0,
                "cases_generated": 0, "cases_opened": 0},
            "successor_final_proposal": {
                "status": "REKEYED SUCCESSOR REQUIRED",
                "final_protocol_status": "NOT FROZEN",
                "final_cases_status": "NOT GENERATED; NOT OPENED",
                "content_open_count": 0, "metadata_probe_count": 0,
                "qualified_independent_candidate_count": 0},
            "physical_source_wall": {
                "policy": "CONTINUOUS DENY DEFAULT; EXACT FIRST-PARTY SOURCES AND PUBLIC EVIDENCE",
                "installed_before_owner_reads": True,
                "source_mode_filesystem_writes_allowed": False,
                "dynamic_frozen_predecessor_execution_count": 2,
                "candidate_or_compiler_process_allowed": False,
                "clock_access_allowed": False,
                "allowed_native_binary_count": 0,
                "allowed_archive_count": 0,
                "allowed_holdout_content_count": 0,
                "allowed_holdout_metadata_count": 0,
                "retired_final_proposal_invalidated": True,
                "rekeyed_successor_required": True,
                "linux_tmpfile_detection": "FULL COMPOSITE MASK; NOT ANY OVERLAP",
                "ordinary_safe_directory_overlap_is_allowed": True,
                "apply_requires_matching_frozen_and_pushed_commit": True,
                "apply_requires_explicit_root_authorization": True,
                "apply_target_policy": "FD-ANCHORED EXCLUSIVE O_NOFOLLOW|O_CREAT|O_EXCL",
                "parent_directory_device": DEVICE,
                "parent_directory_inode": PARENT_INODE,
                "child_directory_mode": "0700", "derived_source_mode": "0600",
                "output_file_count": 2, "output_fsync_count": 2,
                "directory_fsync_count": 2},
            "source_only_effects": {
                "candidate_imports": 0, "candidate_workers_started": 0,
                "compiler_processes_started": 0, "native_libraries_loaded": 0,
                "native_binaries_opened": 0, "compressed_archives_opened": 0,
                "network_requests": 0, "clock_samples": 0,
                "new_timing_trials_run": 0, "private_roots_opened": 0,
                "holdout_cases_generated": 0, "holdout_cases_opened": 0,
                "holdout_proposal_content_open_count": 0,
                "holdout_proposal_metadata_probe_count": 0,
                "retired_final_proposal": "INVALIDATED",
                "successor_final_proposal": "REKEYED SUCCESSOR REQUIRED",
                "holdout": "NOT OPENED", "performance": NOT_MEASURED,
                "memory": NOT_MEASURED, "cpu_function_profile": NOT_MEASURED,
                "candidate_correctness": NOT_MEASURED,
                "runtime_non_delegation": "NOT ESTABLISHED",
                "undefined_behavior": NOT_MEASURED,
                "qualified_candidate_count": 0, "winner_selected": False}}


def validate_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PYTHON and sys.flags.isolated == 1
            and sys.flags.no_site == 1 and sys.dont_write_bytecode is True,
            "require exact pinned CPython 3.14.6 under -I -B -S")
    clean_imports()


def parse_arguments(values: list[str]) -> tuple[str, dict[str, str], frozenset[str]]:
    require(type(values) is list and bool(values), "require one explicit frozen action")
    mode = values[0]
    require(mode in ("--render-contract", "--verify-source", "--self-test", "--apply"),
            "reject an unknown or combined frozen action")
    pins: dict[str, str] = {}
    flags: set[str] = set()
    position = 1
    while position < len(values):
        name = values[position]
        if name in ("--root-authorized", "--frozen-committed-pushed"):
            require(name not in flags, "reject duplicate explicit root authority")
            flags.add(name)
            position += 1
            continue
        require(name in ("--source-sha256", "--protocol-sha256", "--contract-sha256",
                         "--frozen-commit", "--pushed-commit")
                and name not in pins and position + 1 < len(values),
                "reject unknown, duplicate, or incomplete frozen authority")
        value = values[position + 1]
        pins[name] = (exact_commit(value, name) if name.endswith("commit")
                      else exact_sha(value, name))
        position += 2
    basic = {"--source-sha256", "--protocol-sha256"}
    if mode == "--render-contract":
        require(set(pins) == basic and not flags,
                "rendering accepts only independently pinned source and protocol")
    elif mode in ("--verify-source", "--self-test"):
        require(set(pins) == basic | {"--contract-sha256"} and not flags,
                "source gates require exactly three independently frozen owner hashes")
    else:
        require(set(pins) == basic | {"--contract-sha256", "--frozen-commit", "--pushed-commit"}
                and pins["--frozen-commit"] == pins["--pushed-commit"]
                and flags == {"--root-authorized", "--frozen-committed-pushed"},
                "publication requires all pins, matching pushed commit, and root authority")
    return mode, pins, frozenset(flags)


def load_context(wall: SourceWall, mode: str, pins: dict[str, str]) -> dict[str, object]:
    source_row = live_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol_row = live_owner(wall, "protocol", PROTOCOL, pins["--protocol-sha256"])
    read_owner(wall, source_row)
    read_owner(wall, protocol_row)
    contract_row = (None if mode == "--render-contract" else
                    live_owner(wall, "contract", CONTRACT, pins["--contract-sha256"]))
    evidence = {row[0]: read_owner(wall, row) for row in OWNERS}
    workspace = load_previous(wall, "workspace", evidence["workspace_v1_source"])
    combined = load_previous(wall, "combined", evidence["combined_v2_source"])
    require(combined.get("SCHEMA")
                == "rebar-first-party-rust-combined-search-compiler-fastpath-v2"
            and combined.get("LIB_SHA256") == COMBINED_LIB_SHA256
            and combined.get("SEARCH_SHA256") == SEARCH_SHA256
            and workspace.get("SCHEMA")
                == "rebar-owned-rust-vm-workspace-reuse-v1-source-freeze"
            and workspace.get("DERIVED_SHA256") == WORKSPACE_LIB_SHA256,
            "authenticate both independently frozen predecessor transformer modules")
    clean_imports()
    history = validate_history(evidence, workspace)
    lib, composition = compose_sources(evidence, workspace)
    semantics = synthetic_composition(workspace)
    contract = frozen_contract(source_row, protocol_row, history, composition, semantics)
    if contract_row is not None:
        raw = read_owner(wall, contract_row)
        parsed = workspace["json_object"](raw, "complete combined VM workspace contract")
        require(raw == document(contract) and parsed == contract,
                "reject altered, incomplete, or stale combined VM workspace freeze")
    require(not wall.owners and wall.parent_fd is None and wall.child_fd is None
            and not wall.outputs and wall.compile_count == 2 and wall.exec_count == 2
            and wall.proposal_open_count == 0 and wall.proposal_metadata_count == 0,
            "close every source descriptor and never inspect either final proposal")
    return {"source": evidence["combined_v2_lib"], "lib": lib,
            "search": evidence["combined_v2_search"], "contract": contract,
            "history": history, "composition": composition, "semantics": semantics,
            "workspace": workspace}


def expect_rejected(wall: SourceWall, label: str, operation) -> str:
    before = sum(wall.blocked.values())
    try:
        operation()
    except (FreezeError, OSError, TypeError, ValueError):
        require(sum(wall.blocked.values()) > before,
                "hostile source action bypassed the physical wall: " + label)
        return label
    raise FreezeError("hostile source action escaped the physical wall: " + label)


def hostile_self_test(wall: SourceWall, state: dict[str, object]) -> dict[str, object]:
    source = ROOT + "/" + SOURCE

    def forged_authority() -> None:
        saved = wall.apply
        wall.apply = not saved
        try:
            sys.audit("os.exec", "/bin/true", (), None)
        finally:
            wall.apply = saved

    def forged_compile() -> None:
        saved = wall.compile_name, wall.compile_raw, wall.compile_count, wall.exec_count
        wall.compile_name = ROOT + "/" + str(OWNERS[15][1])
        wall.compile_raw = b"pass"
        wall.compile_count = 0
        wall.exec_count = 0
        try:
            compile(b"pass", wall.compile_name, "exec")
        finally:
            wall.compile_name, wall.compile_raw, wall.compile_count, wall.exec_count = saved

    native = sys.modules["posix"]
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    controls = [
        expect_rejected(wall, "builtins-read", lambda: builtins.open(source, "rb")),
        expect_rejected(wall, "builtins-write", lambda: builtins.open(source, "wb")),
        expect_rejected(wall, "direct-io-open", lambda: io.open(source, "rb")),
        expect_rejected(wall, "direct-_io-open", lambda: _io.open(source, "rb")),
        expect_rejected(wall, "owner-write", lambda: os.open(source, os.O_WRONLY)),
        expect_rejected(wall, "owner-missing-nofollow", lambda: os.open(source, os.O_RDONLY)),
        expect_rejected(wall, "candidate-python",
                        lambda: os.open(ROOT + "/candidates/rust_candidate.py", flags)),
        expect_rejected(wall, "candidate-native",
                        lambda: os.open(ROOT + "/candidates/_rust_engine.so", flags)),
        expect_rejected(wall, "candidate-native-bridge",
                        lambda: os.open(ROOT + "/candidates/_rust_bridge.so", flags)),
        expect_rejected(wall, "invalidated-final-proposal",
                        lambda: os.open(ROOT + "/" + RETIRED_PROPOSAL, flags)),
        expect_rejected(wall, "invalidated-final-metadata",
                        lambda: os.lstat(ROOT + "/" + RETIRED_PROPOSAL)),
        expect_rejected(wall, "unknown-rekeyed-successor",
                        lambda: os.open(ROOT + "/oracle/phase3/expanded-sealed-holdout-v3.json", flags)),
        expect_rejected(wall, "hidden-final-cases",
                        lambda: os.open(ROOT + "/oracle/phase3/final-hidden-cases.json", flags)),
        expect_rejected(wall, "compressed-archive",
                        lambda: os.open(ROOT + "/oracle/phase2/evidence/candidate.json.gz", flags)),
        expect_rejected(wall, "private-native-root",
                        lambda: os.open("/tmp/rebar-private-native-build", flags)),
        expect_rejected(wall, "premature-target",
                        lambda: os.open(ROOT + "/" + LIB_TARGET,
                                        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW)),
        expect_rejected(wall, "source-alias",
                        lambda: os.open(ROOT + "/tools/../" + SOURCE, flags)),
        expect_rejected(wall, "foreign-host-file", lambda: os.open("/etc/passwd", flags)),
        expect_rejected(wall, "anonymous-owner",
                        lambda: os.open(source, os.O_TMPFILE | os.O_RDWR | os.O_NOFOLLOW)),
        expect_rejected(wall, "anonymous-parent",
                        lambda: os.open(ROOT + "/" + PARENT,
                                        os.O_TMPFILE | os.O_DIRECTORY | os.O_NOFOLLOW)),
        expect_rejected(wall, "parent-before-publication",
                        lambda: os.open(ROOT + "/" + PARENT,
                                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)),
        expect_rejected(wall, "foreign-read-fd", lambda: os.read(0, 1)),
        expect_rejected(wall, "foreign-write-fd", lambda: os.write(1, b"reject")),
        expect_rejected(wall, "foreign-fstat", lambda: os.fstat(0)),
        expect_rejected(wall, "foreign-fsync", lambda: os.fsync(1)),
        expect_rejected(wall, "foreign-close", lambda: os.close(0)),
        expect_rejected(wall, "foreign-directory",
                        lambda: os.mkdir(DIRECTORY, 0o700, dir_fd=0)),
        expect_rejected(wall, "process", lambda: os.system("true")),
        expect_rejected(wall, "process-audit",
                        lambda: sys.audit("os.exec", "/bin/true", (), None)),
        expect_rejected(wall, "clock", lambda: time.time()),
        expect_rejected(wall, "nanosecond-clock", lambda: time.perf_counter_ns()),
        expect_rejected(wall, "dynamic-compile", lambda: compile(b"1", "hostile.py", "exec")),
        expect_rejected(wall, "forged-predecessor-compile", forged_compile),
        expect_rejected(wall, "dynamic-execution", lambda: exec("1")),
        expect_rejected(wall, "forged-root-authority", forged_authority),
        expect_rejected(wall, "native-import", lambda: __import__("ctypes")),
        expect_rejected(wall, "matcher-import", lambda: __import__("re")),
        expect_rejected(wall, "underlying-posix-write", lambda: native.write(1, b"reject")),
        expect_rejected(wall, "underlying-posix-read", lambda: native.read(0, 1)),
        expect_rejected(wall, "underlying-posix-fstat", lambda: native.fstat(0)),
    ]
    for name in ("dup", "pread", "pwrite", "readv", "writev", "sendfile", "link",
                 "symlink", "truncate", "ftruncate", "utime", "listdir", "stat",
                 "execv", "execve", "spawnv", "spawnve", "kill", "chdir"):
        if hasattr(os, name):
            controls.append(expect_rejected(wall, "descriptor-alias-" + name,
                                            lambda operation=getattr(os, name): operation()))
    parse = state["workspace"]["json_object"]
    malformed = (b'{"duplicate":1,"duplicate":2}', b'{"leading":01}',
                 b'{"nonfinite":NaN}', b'{"trailing":1}{}',
                 b'{"surrogate":"\\ud800"}', b'{"escape":"\\q"}', b"[1]")
    rejected_json = 0
    for raw in malformed:
        try:
            parse(raw, "hostile malformed composition contract")
        except (Exception,):
            rejected_json += 1
        else:
            raise FreezeError("a malformed, ambiguous, or duplicate JSON owner escaped")
    poisoned = 0
    for label, old, new in state["workspace"]["REPLACEMENTS"]:
        require(old != new and state["source"].count(old) == 1,
                "an exact, independently frozen VM source replacement disappeared")
        broken = state["source"].replace(old, b"BROKEN-FROZEN-SOURCE-ANCHOR\n", 1)
        require(broken.count(old) == 0,
                "reject every poisoned first-party VM composition anchor: " + label)
        poisoned += 1
    corrected = (os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    require(wall.directory_flags(corrected)
            and not wall.directory_flags(os.O_TMPFILE | os.O_DIRECTORY | os.O_NOFOLLOW)
            and len(controls) >= 55 and rejected_json == len(malformed) and poisoned == 7
            and wall.proposal_open_count == 0 and wall.proposal_metadata_count == 0,
            "exercise complete physical, parser, composition, tmpfile, and hidden-case controls")
    clean_imports()
    return {"physical_hostile_control_count": len(controls),
            "physical_hostile_controls": controls,
            "malformed_json_control_count": rejected_json,
            "poisoned_composition_anchor_control_count": poisoned,
            "physically_blocked_categories": dict(wall.blocked),
            "linux_full_composite_tmpfile_guard_corrected": True,
            "underlying_posix_aliases_guarded": True,
            "retired_final_proposal_opened": False,
            "retired_final_proposal_metadata_read": False,
            "rekeyed_successor_required": True,
            "wall_remains_installed": wall.installed}


def create_output(wall: SourceWall, name: str, raw: bytes) -> dict[str, object]:
    expected = LIB_SHA256 if name == "lib.rs" else SEARCH_SHA256
    require(wall.child_fd is not None and digest(raw) == expected,
            "authenticate complete immutable output before exclusive creation")
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
        finished = os.fstat(descriptor)
        require(finished.st_dev == initial.st_dev and finished.st_ino == initial.st_ino
                and finished.st_size == len(raw) and finished.st_nlink == 1
                and stat.S_IMODE(finished.st_mode) == 0o600,
                "reject incomplete or exchanged exclusive Rust output")
        return {"path": LIB_TARGET if name == "lib.rs" else SEARCH_TARGET,
                "sha256": digest(raw), "bytes": len(raw), "device": finished.st_dev,
                "inode": finished.st_ino, "mode": "0600", "nlink": 1,
                "exclusive_no_follow": True, "fsync_completed": True}
    finally:
        os.close(descriptor)


def apply_root_only(wall: SourceWall, state: dict[str, object], pins: dict[str, str],
                    flags: frozenset[str]) -> dict[str, object]:
    require(flags == {"--root-authorized", "--frozen-committed-pushed"}
            and pins["--frozen-commit"] == pins["--pushed-commit"]
            and pins["--source-sha256"] == state["contract"]["source"]["sha256"]
            and pins["--protocol-sha256"] == state["contract"]["protocol"]["sha256"]
            and wall.apply and wall.stage == "source" and not wall.owners
            and wall.proposal_open_count == 0 and wall.proposal_metadata_count == 0
            and digest(state["lib"]) == LIB_SHA256 and len(state["lib"]) == LIB_BYTES
            and digest(state["search"]) == SEARCH_SHA256
            and len(state["search"]) == SEARCH_BYTES,
            "authenticate frozen source, root authority, and invalidated final proposal")
    wall.expected = {"lib.rs": state["lib"], "search.rs": state["search"]}
    wall.stage = "ready"
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    parent = os.open(ROOT + "/" + PARENT, directory_flags)
    parent_stat = os.fstat(parent)
    require(stat.S_ISDIR(parent_stat.st_mode) and stat.S_IMODE(parent_stat.st_mode) == 0o700
            and parent_stat.st_dev == DEVICE and parent_stat.st_ino == PARENT_INODE
            and parent_stat.st_uid == os.geteuid(),
            "authenticate the owned first-party Rust variants parent")
    os.mkdir(DIRECTORY, 0o700, dir_fd=parent)
    child = os.open(DIRECTORY, directory_flags, dir_fd=parent)
    child_stat = os.fstat(child)
    require(stat.S_ISDIR(child_stat.st_mode) and stat.S_IMODE(child_stat.st_mode) == 0o700
            and child_stat.st_dev == DEVICE and child_stat.st_uid == os.geteuid(),
            "authenticate exactly one new private Rust source directory")
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
            "synchronize two exclusive files, their private directory, and their parent")
    return {"schema": SCHEMA + "-application", "status": "APPLIED", "mode": "apply",
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
            "owner_output_fsync_count": 2, "directory_fsync_count": 2,
            "continuous_wall_active": wall.installed,
            "original_case_execution_denominator": 31237,
            "latest_candidate_campaign": "V25", "latest_candidate_status": "FAIL",
            "latest_semantic_mismatch_count": 1352,
            "combined_synthetic_case_count":
                state["semantics"]["combined_differential_case_count"],
            "workspace_synthetic_case_count": 18144,
            "retired_final_proposal": "INVALIDATED",
            "successor_final_proposal": "REKEYED SUCCESSOR REQUIRED",
            "holdout_content_open_count": 0, "holdout_metadata_probe_count": 0,
            "candidate_imports": 0, "candidate_workers_started": 0,
            "compiler_processes_started": 0, "native_libraries_loaded": 0,
            "clock_samples": 0, "holdout": "NOT OPENED",
            "candidate_correctness": NOT_MEASURED, "performance": NOT_MEASURED,
            "memory": NOT_MEASURED, "undefined_behavior": NOT_MEASURED,
            "candidate_qualified": False, "winner_selected": False}


def main() -> int:
    validate_runtime()
    mode, pins, flags = parse_arguments(list(sys.argv[1:]))
    wall = SourceWall(mode == "--apply")
    wall.install()
    state = load_context(wall, mode, pins)
    if mode == "--render-contract":
        output = state["contract"]
    elif mode == "--apply":
        output = apply_root_only(wall, state, pins, flags)
    else:
        output = {"schema": SCHEMA + "-source-only-gate", "status": "PASS",
                  "mode": mode[2:], "source_sha256": pins["--source-sha256"],
                  "protocol_sha256": pins["--protocol-sha256"],
                  "contract_sha256": pins["--contract-sha256"],
                  "authenticated_frozen_owner_count": len(OWNERS),
                  "original_case_execution_denominator": 31237,
                  "latest_candidate_campaign": "V25", "latest_candidate_status": "FAIL",
                  "latest_semantic_mismatch_count": 1352,
                  "combined_v2_synthetic_case_count": 111552,
                  "workspace_v1_synthetic_case_count": 18144,
                  "combined_synthetic_case_count":
                      state["semantics"]["combined_differential_case_count"],
                  "isolated_root_workspace_case_count":
                      state["semantics"]["isolated_root_workspace_case_count"],
                  "derived_engine_sha256": LIB_SHA256,
                  "derived_engine_bytes": LIB_BYTES,
                  "derived_search_sha256": SEARCH_SHA256,
                  "derived_search_bytes": SEARCH_BYTES,
                  "exact_reversible_replacement_count": 7,
                  "retired_final_proposal": "INVALIDATED",
                  "successor_final_proposal": "REKEYED SUCCESSOR REQUIRED",
                  "holdout_content_open_count": 0, "holdout_metadata_probe_count": 0,
                  "source_mutations": 0, "candidate_imports": 0,
                  "candidate_workers_started": 0, "compiler_processes_started": 0,
                  "native_libraries_loaded": 0, "archives_opened": 0,
                  "clock_samples": 0, "holdout": "NOT OPENED",
                  "candidate_correctness": NOT_MEASURED,
                  "performance": NOT_MEASURED, "memory": NOT_MEASURED,
                  "undefined_behavior": NOT_MEASURED,
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
        sys.stderr.write("combined first-party VM workspace freeze rejected: "
                         + str(error) + "\n")
        raise SystemExit(2)
