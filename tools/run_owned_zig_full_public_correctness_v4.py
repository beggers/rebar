#!/usr/bin/env python3
"""Freeze the unchanged 10,434-case public oracle for the first-party Zig engine.

Source gates authenticate public plaintext only and never inspect candidates,
private builds, archives, holdouts, benchmarks, clocks, or native objects.
Only separately authorized root execution may activate the exact previously
correctness-tested Zig V17 build, install the immutable V4 runtime guard before
candidate import, and run every frozen public operation in isolated processes.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("full Zig public correctness cannot bootstrap with a matcher")

import _io
import ast
import builtins
import hashlib
import io
import os
import stat
import time
import types

ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
DEVICE = 2064
PRIVATE_DEVICE = 2049
SOURCE = "tools/run_owned_zig_full_public_correctness_v4.py"
PROTOCOL = "oracle/phase2/ZIG-FULL-PUBLIC-CORRECTNESS-V4.md"
CONTRACT = "oracle/phase2/zig-full-public-correctness-v4.json"
SCHEMA = "rebar-owned-zig-full-public-correctness-v4"
VERSION = 4
CASE_COUNT = 10434
DATASET_COUNT = 94
OPERATIONS_PER_DATASET = 111
DOMAIN_CASE_COUNT = 5217
PUBLISHED_SEED = 5928217332825411634
MATRIX_SHA = "0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d"
FINAL_HOLDOUT = "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
PUBLIC_HARNESS_SHA = "a3d7e70343d231bf433fbad6a6669025a970d83691c49cb9f434a186aef3d9e6"
ZIG_HARNESS_SHA = "e4c8c523481034c579df7ffdbbdf84ac52a89c6473a08c0aaeb615e63d6b2d17"
ZIG_HARNESS_BYTES = 114297
BUILD_SOURCE_SHA = "57b2abc0d21740b552ff43f213709acb8dbb8145d10408a07d68b720321c578f"
BUILD_PROTOCOL_SHA = "093c4f5dabcbb3f60584afae74616520b2cd74982b182d93999972eb9da6f47b"
BUILD_CONTRACT_SHA = "987e52d8815cdbff0812afabfd22bcda550b9b1d3478af4d07a173250e2a1b3b"
BUILD_RECEIPT_SHA = "a7b4fafa4f91b6e6345c71feccd4dab3570ac4bc3d06f8689aa4b1c15613703e"
ROOT_RECEIPT_SHA = "2e0f09ef2fea088088608cd430f90f32e86124295e98f672ccab9dc92e16987c"
ORIGINAL_SOURCE_SHA = "43da93fb4dd80133345e8966bbc4bd54d79ae23a1f6776af5bf5ab97d1a411b2"
ORIGINAL_PROTOCOL_SHA = "991e84f4cdb35e46776dee35853ce61e9e6b82c0498f0710ee6fbbc8d6807c7c"
ORIGINAL_CONTRACT_SHA = "5bec9b8875b822a4a383e8f47acdd2313a6047101e490120203e2d9f777d4523"
ORIGINAL_PASS_SHA = "b2762eaea6dd505aa34bd446996b0464b7a0e057e7fb7162355885e065e19bd0"
GUARD_SOURCE_SHA = "5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3"
GUARD_PROTOCOL_SHA = "835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16"
GUARD_CONTRACT_SHA = "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2"
ADAPTER_SHA = "a6587f43112cc54f2fbf86c8c62ea28426950caae94c6fce2ccead61fcc0f124"
ADAPTER_BYTES = 67657
ENGINE_SOURCE_SHA = "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28"
ENGINE_SOURCE_BYTES = 186915
BRIDGE_SOURCE_SHA = "4228199b7c65c4d02a78e0e9764a52aed63ff9a4c8230381925d5d3f2eb588ac"
BRIDGE_SOURCE_BYTES = 176761
ENGINE_SHA = "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071"
ENGINE_BYTES = 108888
BRIDGE_SHA = "34c75d06820f9ec3495c9da3158e2f571aee753e58b62a369ea59336130b380b"
BRIDGE_BYTES = 138104
PRIVATE_ROOT = "/tmp/rebar-phase2-zig-final-original-source-build-v17-79ubeu49"
PRIVATE_ROOT_INODE = 11677246
MAX_OWNER_BYTES = 2 * 1024 * 1024
MAX_ACTUAL_BYTES = 128 * 1024 * 1024
SOURCE_MODES = ("--render-contract", "--verify-frozen-context", "--self-test")
ACTUAL_MODES = ("--run", "--candidate-worker")
OVERLAY_PREFIX = "rebar-zig-full-public-correctness-v4-"
PUBLIC_OUTPUT = ROOT + "/experiments/zig_full_public_correctness_v4"
PREVIOUS_SOURCE = (
    "tools/run_owned_zig_full_public_correctness_v1.py",
    "5ac635da716a7472b5d5a5bd6865bc2ad519ae354f240e3e6c1a8673f2cab087",
    69668,
    431849,
)
PREVIOUS_PROTOCOL = (
    "oracle/phase2/ZIG-FULL-PUBLIC-CORRECTNESS-V1.md",
    "679d6472ac44dd602a5b8aee57fba12b54f46c6ab8b4b5c35a287fe2fa8e9fb6",
    4378,
    526677,
)
PREVIOUS_CONTRACT = (
    "oracle/phase2/zig-full-public-correctness-v1.json",
    "4efc2b4effc284808e21911c13079890722a6afdefd5ba346c5816b5769ee80f",
    12784,
    526678,
)
PREVIOUS_FAILURE = (
    "oracle/phase2/evidence/zig-full-public-correctness-v1-"
    "v17-zig-public-v1-run-001-preactivation-failure.json",
    "50199c81810b376c0711fb300fdf7dc3b2d781a35404b8704fb21dbdd12644ee",
    1544,
    526690,
)
PREVIOUS_V2_SOURCE = (
    "tools/run_owned_zig_full_public_correctness_v2.py",
    "4eb351a11383df97d5f6b5f1f242e988a685992bafbaa87ee89e67fa1dcb0f3c",
    77198,
    431854,
)
PREVIOUS_V2_PROTOCOL = (
    "oracle/phase2/ZIG-FULL-PUBLIC-CORRECTNESS-V2.md",
    "047cf9ff200f7c0423419230aa63ce0c2f3479361f70dd85c354612192b07abd",
    5125,
    526706,
)
PREVIOUS_V2_CONTRACT = (
    "oracle/phase2/zig-full-public-correctness-v2.json",
    "48f59c6a10412cb250b1995e1a37033aa73fc99aa2689117b01b8a2d07f5453c",
    14898,
    526707,
)
PREVIOUS_V2_FAILURE = (
    "oracle/phase2/evidence/zig-full-public-correctness-v2-"
    "v17-zig-public-v2-run-001-guard-failure.json",
    "4466d9be63f9c480ac24de1d42b13524c1a4f82dba4d543779014605dcd74aa3",
    1533,
    526724,
)
PREVIOUS_V3_SOURCE = (
    "tools/run_owned_zig_full_public_correctness_v3.py",
    "081858e598a12b5cf3ecd1832dea8debb2452af575c82c759a2d4532f691bddb",
    95346,
    428900,
)
PREVIOUS_V3_PROTOCOL = (
    "oracle/phase2/ZIG-FULL-PUBLIC-CORRECTNESS-V3.md",
    "8b62bc9aef39ef0fd7cf0432704351dadf6867e2cfba07fe70d4f23203a9b2a2",
    6500,
    525088,
)
PREVIOUS_V3_CONTRACT = (
    "oracle/phase2/zig-full-public-correctness-v3.json",
    "571c9599f1a6b0bcbd201da94b85a8efee58c9ac7b1cb26cafeff88eed00f4af",
    17472,
    525090,
)
PREVIOUS_V3_FAILURE = (
    "oracle/phase2/evidence/zig-full-public-correctness-v3-"
    "v17-zig-public-v3-run-001-authenticated-worker-failure.json",
    "657e26407ba9f024fcd35fdf54b3bcaa3b434bd069f3e012ad7c795b31c63da8",
    7259,
    525113,
)
RECOVERY_PREFIX = "/tmp/rebar-phase2-repaired-zig-original-campaign-v18-"

PUBLIC_OWNERS = (
    ("previous_v1_source", *PREVIOUS_SOURCE),
    ("previous_v1_protocol", *PREVIOUS_PROTOCOL),
    ("previous_v1_contract", *PREVIOUS_CONTRACT),
    ("previous_v1_failure", *PREVIOUS_FAILURE),
    ("previous_v2_source", *PREVIOUS_V2_SOURCE),
    ("previous_v2_protocol", *PREVIOUS_V2_PROTOCOL),
    ("previous_v2_contract", *PREVIOUS_V2_CONTRACT),
    ("previous_v2_failure", *PREVIOUS_V2_FAILURE),
    ("previous_v3_source", *PREVIOUS_V3_SOURCE),
    ("previous_v3_protocol", *PREVIOUS_V3_PROTOCOL),
    ("previous_v3_contract", *PREVIOUS_V3_CONTRACT),
    ("previous_v3_failure", *PREVIOUS_V3_FAILURE),
    ("rust_v5_source", "tools/run_owned_rust_full_public_correctness_v5.py", "97d36e9448336d3cfa732324779c14959bf739a8e6daa556d839e0ecdd0d0602", 83637, 430313),
    ("rust_v5_protocol", "oracle/phase2/RUST-FULL-PUBLIC-CORRECTNESS-V5.md", "066f3e4663bb19612b795f797144c0098bf2d998455d3c0b4c814186d0204bd0", 6570, 525361),
    ("rust_v5_contract", "oracle/phase2/rust-full-public-correctness-v5.json", "fd10e77356945e7544d5b5b91d7a95f95c173384e152506e02c11240b58eb52c", 31041, 525365),
    ("rust_v5_pass", "oracle/phase2/evidence/rust-full-public-correctness-v5-v33-full-public-v5-run-001-publication-receipt.json", "8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9", 6889, 525451),
    ("public_kernel", "tools/run_owned_rust_native_architecture_public_gate_v3.py", "12d0ae388cd2841d0cb091e7da88859a772a3b3c293f18938b488196a32c5eab", 106590, 431279),
    ("public_kernel_protocol", "oracle/phase2/RUST-NATIVE-ARCHITECTURE-PUBLIC-GATE-V3.md", "fdf695478fc1b542026c2b98ba94524df254aea84b46ebab568a98050474cae4", 5911, 525630),
    ("public_kernel_contract", "oracle/phase2/rust-native-architecture-public-gate-v3.json", "80a350478ae4dbf4d745683974b4c60630d900d2e3f97d59cf391bfb1d8358a0", 26615, 525842),
    ("public_harness", "tools/rust_public_practice_benchmark_v2.py", PUBLIC_HARNESS_SHA, 112729, 429259),
    ("zig_build_source", "tools/reproduce_owned_zig_final_original_source_build_v17.py", BUILD_SOURCE_SHA, 63822, 431624),
    ("zig_build_protocol", "oracle/phase2/ZIG-FINAL-ORIGINAL-SOURCE-BUILD-V17.md", BUILD_PROTOCOL_SHA, 4780, 526458),
    ("zig_build_contract", "oracle/phase2/zig-final-original-source-build-v17.json", BUILD_CONTRACT_SHA, 19445, 526487),
    ("zig_build_receipt", "oracle/phase2/evidence/zig-final-original-source-build-v17-phase2-v17-zig-final-original-build-receipt.json", BUILD_RECEIPT_SHA, 174825, 526520),
    ("zig_build_root", "oracle/phase2/evidence/zig-final-original-source-build-v17-phase2-v17-zig-final-original-private-root-receipt.json", ROOT_RECEIPT_SHA, 78070, 526519),
    ("zig_original_source", "tools/run_owned_repaired_zig_original_campaign_v18.py", ORIGINAL_SOURCE_SHA, 74720, 431668),
    ("zig_original_protocol", "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V18.md", ORIGINAL_PROTOCOL_SHA, 4906, 526508),
    ("zig_original_contract", "oracle/phase2/repaired-zig-original-campaign-v18.json", ORIGINAL_CONTRACT_SHA, 8916, 526528),
    ("zig_original_pass", "oracle/phase2/evidence/repaired-zig-original-campaign-v18-phase2-v18-zig-final-original-p0-v18-success-publication-receipt.json", ORIGINAL_PASS_SHA, 20905, 526565),
    ("guard_source", "tools/verify_owned_candidate_runtime_independence_v4.py", GUARD_SOURCE_SHA, 48687, 429243),
    ("guard_protocol", "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md", GUARD_PROTOCOL_SHA, 4492, 525890),
    ("guard_contract", "oracle/phase2/candidate-runtime-independence-v4.json", GUARD_CONTRACT_SHA, 9352, 525891),
    ("zig_historical_failure", "oracle/phase2/evidence/repaired-zig-original-campaign-v16-phase2-v16-zig-full-semantic-original-p0-v16-failures-publication-receipt.json", "a7019c02b2906eb15f622e9bd9e61eb7476c528019fac537ed7072b3f82efe7a", 21041, 526355),
    ("zig_materialization", "oracle/phase2/evidence/zig-final-original-semantics-v1-application.json", "4e84a251bf8ae5ff05a9cd640fc45c184150b445c71970fa014f6f6a7ed33532", 2495, 526473),
)

class PublicError(Exception):
    """Reject substituted public history or an unauthorized full candidate run."""


class CapturedWorkerFailure(Exception):
    """Preserve an authenticated nested failure through three-owner restoration."""

    def __init__(self, document: dict):
        self.document = document
        super().__init__("authentic strict-V4 Zig worker failure captured")


def need(value: object, reason: str) -> None:
    if value is not True:
        raise PublicError(reason)


def digest(payload: bytes) -> str:
    need(type(payload) is bytes, "hash only complete actual bytes")
    return hashlib.sha256(payload).hexdigest()


def sha(value: object, name: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(item in "0123456789abcdef" for item in value),
         "require independently pinned lowercase SHA-256: " + name)
    assert isinstance(value, str)
    return value


def commit(value: object, name: str) -> str:
    need(type(value) is str and len(value) == 40
         and all(item in "0123456789abcdef" for item in value),
         "require one complete already-pushed lowercase commit: " + name)
    assert isinstance(value, str)
    return value


def sterile_modules() -> None:
    forbidden = ("re", "_sre", "regex", "_regex", "ctypes", "candidates",
                 "subprocess", "socket", "threading", "multiprocessing")
    need(not any(name == root or name.startswith(root + ".")
                 for name in sys.modules for root in forbidden),
         "public source gate imported a candidate, matcher, loader, or worker")


class PublicWall:
    """Irreversibly allow only pinned phase-two plaintext and owned transforms."""

    def __init__(self) -> None:
        relatives = (SOURCE, PROTOCOL, CONTRACT,
                     *(row[1] for row in PUBLIC_OWNERS))
        self.allowed = frozenset(ROOT + "/" + item for item in relatives)
        need(all((item.startswith(ROOT + "/tools/")
                  or item.startswith(ROOT + "/oracle/phase2/"))
                 and not item.endswith((".gz", ".so"))
                 and "/candidates/" not in item
                 and not any(word in item.lower()
                             for word in ("holdout", "hidden", "sealed", "proposal"))
                 for item in self.allowed),
             "never allow candidate, final proposal, archive, or phase-three ownership")
        self.live: set[int] = set()
        self.blocked: dict[str, int] = {}
        self.installed = False
        self.raw_open, self.raw_read = os.open, os.read
        self.raw_fstat, self.raw_close = os.fstat, os.close

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise PublicError("full Zig public V4 source wall rejected " + category)

    def approved(self, path: object) -> bool:
        return (type(path) is str and path in self.allowed
                and path.startswith(ROOT + "/")
                and path == os.path.normpath(path)
                and not any(part in (".", "..") for part in path.split("/"))
                and not path.endswith((".gz", ".so"))
                and "/candidates/" not in path
                and not any(word in path.lower()
                            for word in ("holdout", "hidden", "sealed", "proposal")))

    def audit(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            flags = arguments[2] if len(arguments) > 2 else None
            mutation = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                        | os.O_APPEND | getattr(os, "O_TMPFILE", 0))
            if (self.approved(path) and type(flags) is int
                    and flags & getattr(os, "O_NOFOLLOW", 0)
                    and not flags & mutation
                    and not (type(mode) is str
                             and any(item in mode for item in "wax+"))):
                return
            self.deny("unowned-private-candidate-proposal-or-mutation-open")
        if event in ("compile", "exec"):
            item = arguments[0] if arguments else None
            name = (getattr(item, "co_filename", None) if event == "exec"
                    else arguments[1] if len(arguments) > 1 else None)
            if self.approved(name):
                return
            self.deny("foreign-dynamic-code")
        if (event in ("import", "marshal.loads", "os.system", "os.fork",
                      "os.posix_spawn", "os.posix_spawnp", "os.rename",
                      "os.replace", "os.remove", "os.unlink", "os.mkdir",
                      "os.rmdir", "os.chmod", "os.chown", "os.urandom",
                      "os.getrandom", "_interpreters.create",
                      "_interpreters.exec", "cpython.PyInterpreterState_New")
                or event.startswith(("subprocess.", "socket.", "ctypes.",
                                     "threading.", "multiprocessing.",
                                     "tempfile.", "time.", "os.exec", "os.spawn"))):
            self.deny("candidate-worker-native-clock-network-or-mutation")

    def forbidden(self, category: str):
        def reject(*_args: object, **_kwargs: object) -> object:
            self.deny(category)
        return reject

    def guarded_open(self, path: object, flags: object, mode: int = 0o777,
                     *, dir_fd: object = None) -> int:
        excluded = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                    | os.O_APPEND | getattr(os, "O_TMPFILE", 0)
                    | getattr(os, "O_DIRECTORY", 0))
        if (dir_fd is not None or not self.approved(path)
                or type(flags) is not int or bool(flags & excluded)
                or not flags & getattr(os, "O_NOFOLLOW", 0)):
            self.deny("unowned-descriptor-private-root-or-proposal")
        assert isinstance(path, str) and isinstance(flags, int)
        descriptor = self.raw_open(path, flags, mode)
        need(type(descriptor) is int and descriptor >= 0
             and descriptor not in self.live,
             "reject an invented, reused, or inherited source descriptor")
        self.live.add(descriptor)
        return descriptor

    def guarded_read(self, descriptor: object, count: object) -> bytes:
        if (type(descriptor) is not int or descriptor not in self.live
                or type(count) is not int or not 0 <= count <= MAX_OWNER_BYTES):
            self.deny("foreign-or-unbounded-source-descriptor")
        assert isinstance(descriptor, int) and isinstance(count, int)
        return self.raw_read(descriptor, count)

    def guarded_fstat(self, descriptor: object) -> os.stat_result:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("private-proposal-or-foreign-metadata")
        assert isinstance(descriptor, int)
        return self.raw_fstat(descriptor)

    def guarded_close(self, descriptor: object) -> None:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("foreign-source-descriptor-close")
        self.live.remove(descriptor)
        assert isinstance(descriptor, int)
        self.raw_close(descriptor)

    def install(self) -> None:
        need(self.installed is False, "install the irreversible V5 source wall once")
        sys.addaudithook(self.audit)
        builtins.open = self.forbidden("direct-builtins-open")
        for module in (_io, io):
            module.open = self.forbidden("direct-io-open")
            module.FileIO = self.forbidden("direct-io-fileio")
            if hasattr(module, "open_code"):
                module.open_code = self.forbidden("direct-open-code")
        os.open, os.read = self.guarded_open, self.guarded_read
        os.fstat, os.close = self.guarded_fstat, self.guarded_close
        for name in ("write", "fsync", "fdopen", "dup", "dup2", "stat", "lstat",
                     "readlink", "listdir", "scandir", "walk", "fwalk", "access",
                     "fork", "posix_spawn", "posix_spawnp", "system", "mkdir",
                     "makedirs", "remove", "unlink", "rename", "replace",
                     "rmdir", "chmod", "chown", "urandom", "getrandom"):
            if hasattr(os, name):
                setattr(os, name, self.forbidden("direct-os-" + name))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns",
                     "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.forbidden("clock-" + name))
        self.installed = True


def owner_read(wall: PublicWall | None, row: tuple) -> bytes:
    need(type(row) is tuple and len(row) == 5,
         "require an independently pinned complete public owner")
    role, relative, fingerprint, size, inode = row
    sha(fingerprint, str(role))
    need(type(role) is str and type(relative) is str and not relative.startswith("/")
         and ".." not in relative.split("/") and type(size) is int
         and 0 < size <= MAX_OWNER_BYTES and type(inode) is int and inode > 0,
         "reject an unsafe or partial public first-party owner")
    absolute = ROOT + "/" + relative
    need(wall is None or wall.installed and wall.approved(absolute),
         "install the wall before the first public predecessor owner read")
    descriptor = os.open(absolute, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode)
             and stat.S_IMODE(before.st_mode) == 0o600
             and before.st_dev == DEVICE and before.st_ino == inode
             and before.st_size == size and before.st_nlink == 1
             and before.st_uid == os.geteuid(),
             "reject substituted independently owned public plaintext: " + role)
        remaining, blocks = size, []
        while remaining:
            block = os.read(descriptor, min(remaining, 65536))
            need(type(block) is bytes and bool(block),
                 "reject truncated authenticated public plaintext: " + role)
            blocks.append(block)
            remaining -= len(block)
        need(os.read(descriptor, 1) == b"", "reject grown public plaintext: " + role)
        after = os.fstat(descriptor)
        need(all(getattr(before, key) == getattr(after, key)
                 for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                             "st_mtime_ns", "st_ctime_ns")),
             "reject a concurrently replaced public source owner: " + role)
        payload = b"".join(blocks)
        need(digest(payload) == fingerprint,
             "reject altered complete public evidence bytes: " + role)
        return payload
    finally:
        os.close(descriptor)


def live_owner(wall: PublicWall | None, role: str,
               relative: str, expected: str) -> tuple:
    sha(expected, role)
    allowed = (SOURCE, PROTOCOL, CONTRACT)
    need(relative in allowed, "reject invented dynamic candidate or final owner")
    absolute = ROOT + "/" + relative
    need(wall is None or wall.installed and wall.approved(absolute),
         "install the physical wall before authenticating a live public owner")
    descriptor = os.open(absolute, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(descriptor)
        need(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o600
             and info.st_dev == DEVICE and info.st_uid == os.geteuid()
             and info.st_nlink == 1 and 0 < info.st_size <= MAX_OWNER_BYTES,
             "reject substituted dynamic public owner: " + role)
        return role, relative, expected, info.st_size, info.st_ino
    finally:
        os.close(descriptor)


def pin(row: tuple) -> dict:
    return {"role": row[0], "path": row[1], "sha256": row[2],
            "bytes": row[3], "device": DEVICE, "inode": row[4],
            "mode": "0600", "nlink": 1}


def bootstrap(payload: bytes, row: tuple) -> types.ModuleType:
    need(digest(payload) == row[2],
         "authenticate the immutable original public V3 helper before execution")
    module = types.ModuleType("_rebar_zig_v1_authenticated_public_gate_v3")
    module.__file__ = ROOT + "/" + row[1]
    exec(compile(payload, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    need(module.SCHEMA == "rebar-owned-rust-native-architecture-public-gate-v3"
         and module.PUBLIC_CORRECTNESS_CASES == CASE_COUNT
         and module.PUBLIC_CORRECTNESS_MATRIX == MATRIX_SHA
         and module.PUBLIC_CORRECTNESS_SEED == PUBLISHED_SEED
         and callable(module.json_object) and callable(module.document)
         and callable(module.load_harness) and callable(module.run_worker)
         and callable(module.exact_file) and callable(module.snapshot_canonical),
         "retain only the independently authenticated complete V3 public worker kernel")
    return module


def parse_json(module: types.ModuleType, payload: bytes, label: str) -> dict:
    result = module.json_object(payload, label)
    need(type(result) is dict,
         "require one complete duplicate-free public JSON document: " + label)
    return result


def public_operations(payload: bytes) -> tuple[str, ...]:
    path = ROOT + "/tools/rust_public_practice_benchmark_v2.py"
    tree = ast.parse(payload, filename=path)
    values = []
    for node in tree.body:
        if (isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name)
                        and target.id == "OPERATIONS" for target in node.targets)):
            values.append(ast.literal_eval(node.value))
    need(len(values) == 1 and type(values[0]) is tuple
         and len(values[0]) == OPERATIONS_PER_DATASET
         and all(type(item) is str and item for item in values[0])
         and len(set(values[0])) == OPERATIONS_PER_DATASET
         and "pattern.scanner.search" in values[0]
         and "module.sub.callback" in values[0],
         "authenticate every exact original source-defined public operation")
    return values[0]




OLD_NAMESPACE_AUDIT = b'''            origin = owned_origin(module, description="first-party runtime " + name)
            require(os.path.commonpath((owned_root, origin)) == owned_root,
                    "a first-party candidate runtime escaped the owned module root")
'''

NEW_NAMESPACE_AUDIT = b'''            if name == "candidates":
                specification = getattr(module, "__spec__", None)
                paths = getattr(specification, "submodule_search_locations", None)
                loader = getattr(specification, "loader", None)
                require(module is sys.modules.get("candidates")
                        and module.__name__ == "candidates"
                        and getattr(module, "__file__", None) is None
                        and specification is not None
                        and getattr(specification, "name", None) == "candidates"
                        and getattr(specification, "origin", object()) is None
                        and paths is not None
                        and tuple(paths) == (owned_root,)
                        and getattr(module, "__path__", None) is paths
                        and isinstance(loader, importlib.machinery.NamespaceLoader)
                        and type(loader).__module__ == "_frozen_importlib_external"
                        and type(loader).__name__ == "NamespaceLoader"
                        and getattr(module, "__loader__", None) is loader
                        and os.path.isabs(owned_root)
                        and os.path.abspath(owned_root) == owned_root
                        and os.path.realpath(owned_root) == owned_root
                        and os.path.commonpath((str(ROOT), owned_root)) == str(ROOT),
                        "an authenticated first-party namespace package was substituted")
                continue
            origin = owned_origin(module, description="first-party runtime " + name)
            require(os.path.commonpath((owned_root, origin)) == owned_root,
                    "a first-party candidate runtime escaped the owned module root")
'''


def namespace_harness_controls(original: bytes, transformed: bytes) -> dict:
    need(type(original) is bytes and type(transformed) is bytes
         and original.count(OLD_NAMESPACE_AUDIT) == 1
         and original.count(NEW_NAMESPACE_AUDIT) == 0
         and transformed.count(NEW_NAMESPACE_AUDIT) == 1
         and transformed.count(OLD_NAMESPACE_AUDIT) == 1,
         "retain exactly one authenticated first-party namespace exception")
    owner = ROOT + "/tools/rust_public_practice_benchmark_v2.py"
    old_tree = ast.parse(original, filename=owner)
    new_tree = ast.parse(transformed, filename=owner)
    old_audit = [item for item in old_tree.body
                 if isinstance(item, ast.FunctionDef)
                 and item.name == "audit_candidate_runtime"]
    new_audit = [item for item in new_tree.body
                 if isinstance(item, ast.FunctionDef)
                 and item.name == "audit_candidate_runtime"]
    need(len(old_audit) == len(new_audit) == 1,
         "preserve the single frozen candidate runtime-audit function")
    pending = [new_audit[0]]
    new_branches = []
    while pending:
        item = pending.pop()
        if (isinstance(item, ast.If)
                and isinstance(item.test, ast.Compare)
                and isinstance(item.test.left, ast.Name)
                and item.test.left.id == "name"
                and len(item.test.ops) == 1
                and isinstance(item.test.ops[0], ast.Eq)
                and len(item.test.comparators) == 1
                and isinstance(item.test.comparators[0], ast.Constant)
                and item.test.comparators[0].value == "candidates"):
            new_branches.append(item)
        pending.extend(ast.iter_child_nodes(item))
    need(len(new_branches) == 1
         and any(isinstance(item, ast.Continue)
                 for item in new_branches[0].body),
         "limit the exception to the exact root namespace and preserve siblings")
    statements = NEW_NAMESPACE_AUDIT.decode("ascii")
    for token in ('module is sys.modules.get("candidates")',
                  'module.__name__ == "candidates"',
                  'getattr(module, "__file__", None) is None',
                  'getattr(specification, "name", None) == "candidates"',
                  'getattr(specification, "origin", object()) is None',
                  "tuple(paths) == (owned_root,)",
                  'getattr(module, "__path__", None) is paths',
                  "isinstance(loader, importlib.machinery.NamespaceLoader)",
                  'type(loader).__module__ == "_frozen_importlib_external"',
                  'type(loader).__name__ == "NamespaceLoader"',
                  'getattr(module, "__loader__", None) is loader',
                  "os.path.realpath(owned_root) == owned_root"):
        need(token in statements,
             "reject missing authenticated namespace ownership check: " + token)
    need(transformed.count(
        b'owned_origin(module, description="first-party runtime " + name)'
    ) == 1
         and b"import re\n" not in transformed
         and b"import regex\n" not in transformed,
         "retain exact file-owned submodule/native and no-delegation checks")
    return {"namespace_package_branches": 1,
            "namespace_identity_checks": 12,
            "file_backed_submodule_origin_checks_retained": 1,
            "public_operations_changed": 0,
            "stdlib_or_external_matching_delegation_added": 0}


def zig_harness(payload: bytes) -> bytes:
    need(digest(payload) == PUBLIC_HARNESS_SHA,
         "authenticate complete unchanged frozen 111-operation public harness")
    edits = (
        (b"candidates.rust_candidate", b"candidates.zig_candidate", 2),
        (b"rust_candidate.py", b"zig_candidate.py", 1),
        (b"candidates._rust_bridge", b"candidates._zig_bridge", 4),
        (b"    verify_pinned_runtime()\n    reject_external_regex_packages()",
         b'    verify_pinned_runtime(permit_candidate=(name == "rust"))\n'
         b"    reject_external_regex_packages()", 1),
        (OLD_NAMESPACE_AUDIT, NEW_NAMESPACE_AUDIT, 1),
    )
    result = payload
    for old, new, expected in edits:
        need(result.count(old) == expected,
             "preserve each frozen Zig-only public harness adapter anchor")
        result = result.replace(old, new)
    need(len(result) == ZIG_HARNESS_BYTES and digest(result) == ZIG_HARNESS_SHA
         and b"candidates.rust_candidate" not in result
         and b"candidates._rust_bridge" not in result,
         "reject changed operations, candidate alias, or public harness transform")
    original = public_operations(payload)
    adapted = public_operations(result)
    need(adapted == original and len(adapted) == OPERATIONS_PER_DATASET,
         "never change one public operation, dataset, weight, or case")
    namespace_harness_controls(payload, result)
    return result


def validate_history(module: types.ModuleType,
                     payloads: dict[str, bytes]) -> dict:
    rows = {entry[0]: entry for entry in PUBLIC_OWNERS}
    predecessor = parse_json(module, payloads["previous_v1_contract"],
                             "complete immutable wider-public V1 source freeze")
    predecessor_public = predecessor.get("public_correctness")
    need(predecessor.get("schema")
         == "rebar-owned-zig-full-public-correctness-v1-source-freeze"
         and predecessor.get("version") == 1
         and predecessor.get("source", {}).get("sha256") == PREVIOUS_SOURCE[1]
         and predecessor.get("protocol", {}).get("sha256")
             == PREVIOUS_PROTOCOL[1]
         and type(predecessor_public) is dict
         and predecessor_public.get("case_count") == CASE_COUNT
         and predecessor_public.get("operation_count") == OPERATIONS_PER_DATASET
         and predecessor_public.get("dataset_count") == DATASET_COUNT
         and predecessor_public.get("matrix_sha256") == MATRIX_SHA
         and predecessor_public.get("published_seed") == PUBLISHED_SEED
         and predecessor_public.get("candidate_runtime_guard_version") == 4
         and predecessor_public.get("all_cases_execute_even_on_failure") is True
         and predecessor_public.get("all_mismatches_retained") is True,
         "preserve the complete immutable V1 public freeze without weakening")
    previous_failure = parse_json(module, payloads["previous_v1_failure"],
                                  "actual immutable V1 preactivation failure")
    need(previous_failure.get("schema")
         == "rebar-owned-zig-full-public-correctness-v1-preactivation-failure"
         and previous_failure.get("status") == "FAIL"
         and previous_failure.get("candidate_family") == "zig"
         and previous_failure.get("source_sha256") == PREVIOUS_SOURCE[1]
         and previous_failure.get("protocol_sha256") == PREVIOUS_PROTOCOL[1]
         and previous_failure.get("contract_sha256") == PREVIOUS_CONTRACT[1]
         and previous_failure.get("error_type") == "CampaignError"
         and previous_failure.get("error_message")
             == "reject an unsafe exact recovery target"
         and previous_failure.get("expected_recovery_directory_prefix")
             == RECOVERY_PREFIX
         and previous_failure.get("candidate_original_case_count") == 31237
         and previous_failure.get("candidate_original_semantic_mismatch_count")
             == 0
         and previous_failure.get("planned_wider_public_case_count") == CASE_COUNT
         and previous_failure.get("planned_public_operation_count")
             == OPERATIONS_PER_DATASET
         and previous_failure.get("candidate_import_count") == 0
         and previous_failure.get("candidate_matching_case_count") == 0
         and previous_failure.get("candidate_source_targets_modified") == 0
         and previous_failure.get("hidden_holdout_cases_opened") == 0
         and previous_failure.get("timing_trials_run") == 0
         and previous_failure.get("candidate_qualified") is False
         and previous_failure.get("winner_selected") is False,
         "retain the complete genuine V1 preactivation failure unchanged")
    v2 = parse_json(module, payloads["previous_v2_contract"],
                    "complete immutable wider-public V2 source freeze")
    v2_public = v2.get("public_correctness")
    need(v2.get("schema")
         == "rebar-owned-zig-full-public-correctness-v2-source-freeze"
         and v2.get("version") == 2
         and v2.get("source", {}).get("sha256") == PREVIOUS_V2_SOURCE[1]
         and v2.get("protocol", {}).get("sha256") == PREVIOUS_V2_PROTOCOL[1]
         and type(v2_public) is dict
         and v2_public.get("case_count") == CASE_COUNT
         and v2_public.get("operation_count") == OPERATIONS_PER_DATASET
         and v2_public.get("matrix_sha256") == MATRIX_SHA
         and v2_public.get("published_seed") == PUBLISHED_SEED
         and v2_public.get("candidate_runtime_guard_version") == 4
         and v2.get("preserved_previous_v1", {}).get("failure_receipt_sha256")
             == PREVIOUS_FAILURE[1],
         "preserve the exact immutable V2 oracle and predecessor failure")
    v2_failure = parse_json(module, payloads["previous_v2_failure"],
                            "immutable V2 outer worker failure; stage unavailable")
    need(v2_failure.get("schema")
         == "rebar-owned-zig-full-public-correctness-v2-guard-failure"
         and v2_failure.get("status") == "FAIL"
         and v2_failure.get("source_sha256") == PREVIOUS_V2_SOURCE[1]
         and v2_failure.get("protocol_sha256") == PREVIOUS_V2_PROTOCOL[1]
         and v2_failure.get("contract_sha256") == PREVIOUS_V2_CONTRACT[1]
         and v2_failure.get("previous_v1_failure_sha256") == PREVIOUS_FAILURE[1]
         and v2_failure.get("candidate_family") == "zig"
         and v2_failure.get("planned_wider_public_case_count") == CASE_COUNT
         and v2_failure.get("planned_public_operation_count")
             == OPERATIONS_PER_DATASET
         and v2_failure.get("error_type") == "PublicError"
         and type(v2_failure.get("error_message")) is str
         and "require genuine installed V4 before complete Zig candidate execution"
             in v2_failure["error_message"]
         and v2_failure.get("candidate_source_targets_restored") is True
         and v2_failure.get("candidate_qualified") is False
         and v2_failure.get("winner_selected") is False,
         "preserve authentic generic V2 failure without trusting missing inner stage")
    v3 = parse_json(module, payloads["previous_v3_contract"],
                    "complete transparent wider-public V3 source freeze")
    v3_public = v3.get("public_correctness")
    need(v3.get("schema")
         == "rebar-owned-zig-full-public-correctness-v3-source-freeze"
         and v3.get("version") == 3
         and v3.get("source", {}).get("sha256") == PREVIOUS_V3_SOURCE[1]
         and v3.get("protocol", {}).get("sha256") == PREVIOUS_V3_PROTOCOL[1]
         and type(v3_public) is dict
         and v3_public.get("case_count") == CASE_COUNT
         and v3_public.get("operation_count") == OPERATIONS_PER_DATASET
         and v3_public.get("matrix_sha256") == MATRIX_SHA
         and v3_public.get("published_seed") == PUBLISHED_SEED
         and v3_public.get("candidate_runtime_guard_version") == 4
         and v3.get("preserved_previous_v2", {}).get("failure_receipt_sha256")
             == PREVIOUS_V2_FAILURE[1]
         and v3.get("authentic_worker_failure_preservation", {}).get(
             "generic_failure_replacement_allowed") is False,
         "preserve the exact immutable V3 oracle and authentic nested diagnostics")
    v3_failure = parse_json(module, payloads["previous_v3_failure"],
                            "actual authenticated V3 nested namespace failure")
    nested = v3_failure.get("complete_authentic_v18_worker_failure")
    frames = v3_failure.get("traceback_frames")
    need(v3_failure.get("schema")
         == "rebar-owned-zig-full-public-correctness-v3-"
            "actual-authenticated-worker-failure"
         and v3_failure.get("status") == "FAIL"
         and v3_failure.get("family") == "zig"
         and v3_failure.get("source_sha256") == PREVIOUS_V3_SOURCE[1]
         and v3_failure.get("protocol_sha256") == PREVIOUS_V3_PROTOCOL[1]
         and v3_failure.get("contract_sha256") == PREVIOUS_V3_CONTRACT[1]
         and v3_failure.get("preserved_v1_failure_sha256") == PREVIOUS_FAILURE[1]
         and v3_failure.get("preserved_v2_failure_sha256")
             == PREVIOUS_V2_FAILURE[1]
         and v3_failure.get("public_case_execution_denominator") == CASE_COUNT
         and v3_failure.get("public_api_operation_count")
             == OPERATIONS_PER_DATASET
         and v3_failure.get("runtime_guard_version") == 4
         and v3_failure.get("guard_installed_before_candidate_import") is True
         and v3_failure.get("candidate_imported") is True
         and v3_failure.get("activation_stage")
             == "OBSERVE_COMPLETE_DIRECT_ORIGINAL_SUITE"
         and v3_failure.get("error_type") == "PublicPracticeError"
         and v3_failure.get("error_message")
             == "an exact owned first-party runtime candidates module origin was substituted"
         and v3_failure.get("candidate_matching_case_count") == "NOT MEASURED"
         and v3_failure.get("all_three_original_targets_restored") is True
         and type(nested) is dict
         and nested.get("schema") ==
             "rebar-owned-repaired-zig-original-campaign-v18-actual-worker-failure"
         and nested.get("activation_stage")
             == v3_failure["activation_stage"]
         and nested.get("error_message") == v3_failure["error_message"]
         and nested.get("guard_installed_before_candidate_import") is True
         and nested.get("candidate_imported") is True
         and type(frames) is list
         and any(frame.get("function") == "owned_origin" for frame in frames)
         and any(frame.get("function") == "audit_candidate_runtime"
                 for frame in frames)
         and v3_failure.get("candidate_qualified") is False,
         "preserve genuine strict-V4 installed/imported namespace-only failure")
    kernel = parse_json(module, payloads["public_kernel_contract"],
                        "frozen complete public V3 matrix")
    public = kernel.get("public_correctness")
    need(kernel.get("schema")
         == "rebar-owned-rust-native-architecture-public-gate-v3-source-freeze"
         and kernel.get("source_sha256") == rows["public_kernel"][2]
         and kernel.get("protocol_sha256") == rows["public_kernel_protocol"][2]
         and type(public) is dict and public.get("case_count") == CASE_COUNT
         and public.get("matrix_sha256") == MATRIX_SHA
         and public.get("published_seed") == PUBLISHED_SEED
         and public.get("preserve_all_mismatches") is True
         and kernel.get("current_final_holdout") == FINAL_HOLDOUT
         and kernel.get("candidate_qualified") is False,
         "preserve the exact frozen 10,434-case public correctness oracle")

    rust = parse_json(module, payloads["rust_v5_contract"],
                      "complete Rust public V5 source freeze")
    rust_public = rust.get("public_correctness", {})
    need(rust.get("schema")
         == "rebar-owned-rust-full-public-correctness-v5-source-freeze"
         and rust.get("version") == 5 and type(rust_public) is dict
         and rust_public.get("case_count") == CASE_COUNT
         and rust_public.get("operation_count") == OPERATIONS_PER_DATASET
         and rust_public.get("dataset_count") == DATASET_COUNT
         and rust_public.get("str_case_count") == DOMAIN_CASE_COUNT
         and rust_public.get("bytes_case_count") == DOMAIN_CASE_COUNT
         and rust_public.get("matrix_sha256") == MATRIX_SHA
         and rust_public.get("published_seed") == PUBLISHED_SEED
         and rust_public.get("all_cases_execute_even_on_failure") is True
         and rust_public.get("all_mismatches_retained") is True,
         "preserve unchanged V5 wider-public operations and exact denominator")
    operations = public_operations(payloads["public_harness"])
    need(tuple(rust_public.get("operations", [])) == operations,
         "reject changed inherited operation definitions")

    rust_result = parse_json(module, payloads["rust_v5_pass"],
                             "actual full public Rust PASS")
    need(rust_result.get("schema")
         == "rebar-owned-rust-full-public-correctness-v5-durable-publication-receipt"
         and rust_result.get("status") == "PASS"
         and rust_result.get("candidate_status") == "PASS"
         and rust_result.get("public_10434_case_count") == CASE_COUNT
         and rust_result.get("public_10434_verified_passing_case_count") == CASE_COUNT
         and rust_result.get("public_10434_mismatch_count") == 0
         and rust_result.get("public_api_operation_count") == OPERATIONS_PER_DATASET
         and rust_result.get("published_seed") == PUBLISHED_SEED
         and rust_result.get("matrix_sha256") == MATRIX_SHA
         and rust_result.get("candidate_qualified") is False,
         "preserve the previously published independent Rust full-public PASS")

    original = parse_json(module, payloads["zig_original_pass"],
                          "actual all-original Zig V18 PASS")
    diagnostics = original.get("original_suite_diagnostics")
    need(original.get("schema")
         == "rebar-owned-repaired-zig-original-campaign-v18-durable-publication-receipt"
         and original.get("status") == "PASS"
         and original.get("candidate_status") == "PASS"
         and original.get("original_campaign_passed") is True
         and original.get("case_execution_denominator") == 31237
         and original.get("verified_passing_case_count") == 31237
         and original.get("semantic_mismatch_count") == 0
         and original.get("actual_candidate_workers") == 13
         and original.get("completed_suite_count") == 13
         and original.get("infrastructure_failure_count") == 0
         and type(diagnostics) is list and len(diagnostics) == 13
         and all(type(row) is dict and row.get("status") == "PASS"
                 and row.get("infrastructure_failure") is False
                 for row in diagnostics)
         and sum(row["case_execution_denominator"] for row in diagnostics) == 31237
         and original.get("candidate_qualified") is False,
         "retain every genuine independent Zig original-oracle success")

    historical = parse_json(module, payloads["zig_historical_failure"],
                            "preserved complete earlier Zig failure")
    need(historical.get("family") == "zig"
         and historical.get("semantic_mismatch_count") == 1156
         and historical.get("verified_passing_case_count") == 18056
         and historical.get("candidate_qualified") is False,
         "never erase the authentic previous 1,156 Zig mismatches")

    guard = parse_json(module, payloads["guard_contract"],
                       "frozen immutable V4 runtime policy")
    need(guard.get("schema")
         == "rebar-owned-candidate-runtime-independence-v4-source-freeze"
         and guard.get("version") == 4
         and guard.get("runtime_non_delegation") == "NOT ESTABLISHED"
         and guard.get("qualified_candidate_count") == 0,
         "preserve immutable strict V4 without claiming runtime qualification")

    build = parse_json(module, payloads["zig_build_receipt"],
                       "actual complete independent Zig V17 dual build")
    root = parse_json(module, payloads["zig_build_root"],
                      "actual complete independent Zig V17 root receipt")
    complete = build.get("complete_actual_build")
    need(build.get("schema")
         == "rebar-owned-zig-final-original-source-build-v17-plaintext-build-receipt"
         and build.get("status") == "PASS" and build.get("family") == "zig"
         and build.get("version") == 17
         and build.get("source_sha256") == BUILD_SOURCE_SHA
         and build.get("protocol_sha256") == BUILD_PROTOCOL_SHA
         and build.get("contract_sha256") == BUILD_CONTRACT_SHA
         and build.get("private_root_receipt_sha256") == ROOT_RECEIPT_SHA
         and type(complete) is dict and complete.get("status") == "PASS"
         and complete.get("actual_process_count") == 26
         and complete.get("strict_runtime_guard_version") == 4
         and complete.get("strict_runtime_guard_contract_sha256")
             == GUARD_CONTRACT_SHA
         and complete.get("first_party_engine_source_sha256") == ENGINE_SOURCE_SHA
         and complete.get("first_party_bridge_source_sha256") == BRIDGE_SOURCE_SHA
         and complete.get("corrected_adapter_sha256") == ADAPTER_SHA
         and complete.get("external_regex_dependency_count") == 0
         and complete.get("stdlib_regex_engine_count") == 0
         and complete.get("cross_family_engine_count") == 0,
         "require complete zero-external Zig V17 source-built engines")
    phases = complete.get("build_phases")
    private = root.get("private_root")
    root_phases = root.get("phases")
    need(root.get("schema")
         == "rebar-owned-zig-final-original-source-build-v17-private-root-receipt"
         and root.get("status") == "PASS" and root.get("version") == 17
         and root.get("actual_process_count") == 26
         and root.get("strict_runtime_guard_version") == 4
         and root.get("strict_runtime_guard_contract_sha256") == GUARD_CONTRACT_SHA
         and root.get("final_adapter_sha256") == ADAPTER_SHA
         and root.get("final_bridge_source_sha256") == BRIDGE_SOURCE_SHA
         and root.get("first_party_engine_source_sha256") == ENGINE_SOURCE_SHA
         and type(private) is dict and private.get("path") == PRIVATE_ROOT
         and private.get("device") == PRIVATE_DEVICE
         and private.get("inode") == PRIVATE_ROOT_INODE
         and private.get("mode") == "0700"
         and type(phases) is list and type(root_phases) is list
         and len(phases) == len(root_phases) == 2,
         "reject crossed, single-phase, or substituted genuine Zig V17 build root")
    for index, phase in enumerate(phases):
        need(phase.get("name") == ("reference-a", "reference-b")[index]
             and root_phases[index].get("name") == phase["name"],
             "reject omitted or reordered independent Zig build phases")
        outputs = phase.get("native_outputs", {})
        for role, expected_sha, expected_bytes in (
                ("engine", ENGINE_SHA, ENGINE_BYTES),
                ("bridge", BRIDGE_SHA, BRIDGE_BYTES)):
            entry = outputs.get(role, {})
            owner = entry.get("owner", {})
            audit = entry.get("independence_audit", {})
            root_owner = root_phases[index].get("native_outputs", {}).get(role, {}).get("owner")
            need(type(owner) is dict and owner == root_owner
                 and owner.get("sha256") == expected_sha
                 and owner.get("bytes") == expected_bytes
                 and owner.get("device") == PRIVATE_DEVICE
                 and owner.get("mode") == "0700"
                 and type(audit) is dict
                 and audit.get("external_regex_dependency_count") == 0
                 and audit.get("stdlib_regex_engine_count") == 0
                 and audit.get("cross_family_engine_count") == 0
                 and audit.get("benign_copyreg_import_count")
                    == (1 if role == "bridge" else 0),
                 "reject an external, crossed, or substituted Zig native artifact")
    adapted = zig_harness(payloads["public_harness"])
    return {"operations": operations, "kernel": kernel, "rust": rust,
            "rust_pass": rust_result, "original": original, "historical": historical,
            "guard": guard, "build": build, "root": root,
            "adapted_harness": adapted, "previous_v1": predecessor,
            "previous_v1_failure": previous_failure,
            "previous_v2": v2, "previous_v2_failure": v2_failure,
            "previous_v3": v3, "previous_v3_failure": v3_failure}


def contract_document(rows: dict[str, tuple], history: dict) -> dict:
    operations = list(history["operations"])
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "status": "SOURCE FROZEN; SAME ORIGINAL-PASS ZIG BUILD; PUBLIC CORRECTNESS NOT RUN",
        "source": pin(rows["source"]),
        "protocol": pin(rows["protocol"]),
        "authenticated_public_owners": [pin(row) for row in PUBLIC_OWNERS],
        "preserved_previous_v1": {
            "source_sha256": PREVIOUS_SOURCE[1],
            "protocol_sha256": PREVIOUS_PROTOCOL[1],
            "contract_sha256": PREVIOUS_CONTRACT[1],
            "failure_receipt_sha256": PREVIOUS_FAILURE[1],
            "failure_receipt_bytes": PREVIOUS_FAILURE[2],
            "failure_receipt_inode": PREVIOUS_FAILURE[3],
            "failure_status": "FAIL",
            "failure_error_type": "CampaignError",
            "failure_error_message": "reject an unsafe exact recovery target",
            "candidate_imports_before_failure": 0,
            "candidate_cases_before_failure": 0,
            "original_candidate_source_targets_modified": 0,
            "failed_freeze_replaced_or_edited": False,
        },
        "preserved_previous_v2": {
            "source_sha256": PREVIOUS_V2_SOURCE[1],
            "protocol_sha256": PREVIOUS_V2_PROTOCOL[1],
            "contract_sha256": PREVIOUS_V2_CONTRACT[1],
            "failure_receipt_sha256": PREVIOUS_V2_FAILURE[1],
            "failure_receipt_bytes": PREVIOUS_V2_FAILURE[2],
            "failure_receipt_inode": PREVIOUS_V2_FAILURE[3],
            "failure_status": "FAIL",
            "failure_outer_error_type": "PublicError",
            "inner_v18_worker_document_preserved": False,
            "inner_v18_activation_stage": "NOT MEASURED",
            "inner_v18_candidate_imported": "NOT MEASURED",
            "inner_v18_matching_case_count": "NOT MEASURED",
            "inner_v18_guard_identity_result": "NOT MEASURED",
            "prior_unverified_before_matching_claim":
                "NOT ESTABLISHED; AUTHENTIC INNER DOCUMENT WAS DISCARDED",
            "prior_unverified_zero_matching_claim":
                "NOT ESTABLISHED; AUTHENTIC INNER DOCUMENT WAS DISCARDED",
            "prior_unverified_guard_identity_failure_claim":
                "NOT ESTABLISHED; AUTHENTIC INNER DOCUMENT WAS DISCARDED",
            "immutable_v2_failure_receipt_changed": False,
        },
        "preserved_previous_v3": {
            "source_sha256": PREVIOUS_V3_SOURCE[1],
            "protocol_sha256": PREVIOUS_V3_PROTOCOL[1],
            "contract_sha256": PREVIOUS_V3_CONTRACT[1],
            "failure_receipt_sha256": PREVIOUS_V3_FAILURE[1],
            "failure_receipt_bytes": PREVIOUS_V3_FAILURE[2],
            "failure_receipt_inode": PREVIOUS_V3_FAILURE[3],
            "failure_status": "FAIL",
            "authentic_activation_stage": "OBSERVE_COMPLETE_DIRECT_ORIGINAL_SUITE",
            "authentic_error_type": "PublicPracticeError",
            "authentic_error_message":
                "an exact owned first-party runtime candidates module origin was substituted",
            "strict_v4_installed_before_candidate_import": True,
            "candidate_imported": True,
            "candidate_matching_case_count": "NOT MEASURED",
            "all_three_original_targets_restored": True,
            "authentic_nested_document_preserved": True,
            "immutable_v3_failure_receipt_changed": False,
        },
        "authentic_pep420_namespace_repair": {
            "only_exact_root_namespace_package_exempted": True,
            "namespace_module_name": "candidates",
            "namespace_module_file": None,
            "namespace_spec_name": "candidates",
            "namespace_spec_origin": None,
            "namespace_single_search_location": ROOT + "/candidates",
            "namespace_search_locations_and_module_path_same_object": True,
            "namespace_loader_module": "_frozen_importlib_external",
            "namespace_loader_class": "NamespaceLoader",
            "package_loader_identity_verified": True,
            "namespace_path_absolute_real_and_owned": True,
            "all_candidate_submodule_origin_checks_preserved": True,
            "all_native_extension_origin_checks_preserved": True,
            "previous_harness_sha256":
                "dfb0eaa7cef2ff96562e663ac774d02463e445f3bb5a015bfda471c684350b49",
            "corrected_harness_sha256": ZIG_HARNESS_SHA,
            "corrected_harness_bytes": ZIG_HARNESS_BYTES,
            "strict_runtime_guard_weakened": False,
            "external_regular_expression_engines_allowed": 0,
            "cross_candidate_delegation_allowed": 0,
            "operation_definitions_changed": 0,
        },
        "authentic_worker_failure_preservation": {
            "strict_v18_worker_document_required": True,
            "activation_stage_preserved": True,
            "error_type_preserved": True,
            "error_message_preserved": True,
            "error_traceback_preserved": True,
            "traceback_frames_preserved": True,
            "guard_installation_observation_preserved": True,
            "candidate_import_observation_preserved": True,
            "matching_case_count_inferred": False,
            "durable_root_failure_receipt_required": True,
            "exact_original_targets_restored_before_root_result": True,
            "generic_failure_replacement_allowed": False,
        },
        "corrected_original_v18_recovery": {
            "exact_required_prefix": RECOVERY_PREFIX,
            "coordinator_and_candidate_use_identical_recovery": True,
            "strict_v18_recovery_directory_guard_weakened": False,
            "strict_v4_candidate_import_guard_weakened": False,
            "three_role_journaled_activation_preserved": True,
            "exact_original_inode_restoration_preserved": True,
            "recovery_target_case_specific": True,
        },
        "original_correctness": {
            "receipt_sha256": ORIGINAL_PASS_SHA,
            "case_execution_denominator": 31237,
            "verified_passing_case_count": 31237,
            "semantic_mismatch_count": 0,
            "independent_worker_count": 13,
            "all_original_categories_completed": 13,
            "historical_failure_receipt_sha256":
                "a7019c02b2906eb15f622e9bd9e61eb7476c528019fac537ed7072b3f82efe7a",
            "historical_mismatch_count_preserved": 1156,
        },
        "public_correctness": {
            "case_count": CASE_COUNT,
            "dataset_count": DATASET_COUNT,
            "str_case_count": DOMAIN_CASE_COUNT,
            "bytes_case_count": DOMAIN_CASE_COUNT,
            "operation_count": OPERATIONS_PER_DATASET,
            "operations_per_dataset": OPERATIONS_PER_DATASET,
            "operations": operations,
            "published_seed": PUBLISHED_SEED,
            "matrix_sha256": MATRIX_SHA,
            "harness_source_sha256": PUBLIC_HARNESS_SHA,
            "first_party_zig_adapter_transform_sha256": ZIG_HARNESS_SHA,
            "first_party_zig_adapter_transform_bytes": ZIG_HARNESS_BYTES,
            "all_cases_execute_even_on_failure": True,
            "all_mismatches_retained": True,
            "reference_and_candidate_isolated_processes": True,
            "reference_worker_count": 1,
            "candidate_worker_count": 1,
            "candidate_runtime_guard_version": 4,
            "candidate_guard_installed_before_import": True,
            "timing_trials_run": 0,
        },
        "actual_independent_zig_v17_build": {
            "source_sha256": BUILD_SOURCE_SHA,
            "protocol_sha256": BUILD_PROTOCOL_SHA,
            "contract_sha256": BUILD_CONTRACT_SHA,
            "build_receipt_sha256": BUILD_RECEIPT_SHA,
            "private_root_receipt_sha256": ROOT_RECEIPT_SHA,
            "actual_compiler_process_count": 26,
            "independent_build_phase_count": 2,
            "private_root": {"path": PRIVATE_ROOT, "device": PRIVATE_DEVICE,
                             "inode": PRIVATE_ROOT_INODE},
            "adapter": {"sha256": ADAPTER_SHA, "bytes": ADAPTER_BYTES},
            "engine_source": {"sha256": ENGINE_SOURCE_SHA,
                              "bytes": ENGINE_SOURCE_BYTES},
            "bridge_source": {"sha256": BRIDGE_SOURCE_SHA,
                              "bytes": BRIDGE_SOURCE_BYTES},
            "native_engine": {"sha256": ENGINE_SHA, "bytes": ENGINE_BYTES},
            "native_bridge": {"sha256": BRIDGE_SHA, "bytes": BRIDGE_BYTES},
            "external_regex_dependency_count": 0,
            "stdlib_regex_engine_count": 0,
            "cross_family_engine_count": 0,
        },
        "strict_runtime_guard_v4": {
            "source_sha256": GUARD_SOURCE_SHA,
            "protocol_sha256": GUARD_PROTOCOL_SHA,
            "contract_sha256": GUARD_CONTRACT_SHA,
            "installed_in_candidate_process_before_candidate_import": True,
            "narrow_copyreg_exception_count": 1,
            "copyreg_exception_is_matching_engine": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "source_only_effects": {
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "reference_workers_started": 0,
            "native_libraries_loaded": 0,
            "candidate_source_files_opened": 0,
            "private_roots_opened": 0,
            "private_roots_statted": 0,
            "compressed_archives_opened": 0,
            "proposal_content_opens": 0,
            "proposal_metadata_probes": 0,
            "hidden_cases_read": 0,
            "hidden_cases_generated": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "candidate_qualified": False,
            "winner_selected": False,
            "final_holdout": FINAL_HOLDOUT,
        },
    }


def load_context(options: dict, wall: PublicWall | None) -> dict:
    rows = {
        "source": live_owner(wall, "source", SOURCE, options["source_sha256"]),
        "protocol": live_owner(wall, "protocol", PROTOCOL,
                               options["protocol_sha256"]),
    }
    if options["mode"] != "--render-contract":
        rows["contract"] = live_owner(wall, "contract", CONTRACT,
                                      options["contract_sha256"])
    owner_read(wall, rows["source"])
    owner_read(wall, rows["protocol"])
    payloads = {entry[0]: owner_read(wall, entry) for entry in PUBLIC_OWNERS}
    kernel_row = next(row for row in PUBLIC_OWNERS if row[0] == "public_kernel")
    module = bootstrap(payloads["public_kernel"], kernel_row)
    history = validate_history(module, payloads)
    freeze = contract_document(rows, history)
    if "contract" in rows:
        actual = owner_read(wall, rows["contract"])
        parsed = parse_json(module, actual, "complete frozen Zig full public contract")
        need(parsed == freeze and actual == module.document(freeze),
             "reject omitted, reordered, or weakened full public Zig obligation")
    sterile_modules()
    return {"rows": rows, "payloads": payloads, "module": module,
            "history": history, "freeze": freeze}


def rejected(wall: PublicWall, label: str, action) -> str:
    before = sum(wall.blocked.values())
    try:
        action()
    except (PublicError, OSError, ValueError, TypeError, AttributeError):
        need(sum(wall.blocked.values()) > before,
             "hostile source control missed physical public wall: " + label)
        return label
    raise PublicError("hostile public source control escaped: " + label)


def self_test(wall: PublicWall, state: dict) -> dict:
    path = ROOT + "/" + SOURCE
    hidden = ROOT + "/oracle/phase3/final-held-out-cases.json"
    controls = [
        rejected(wall, "builtins-open", lambda: builtins.open(path, "rb")),
        rejected(wall, "io-open", lambda: io.open(path, "rb")),
        rejected(wall, "_io-open", lambda: _io.open(path, "rb")),
        rejected(wall, "unowned-candidate", lambda: os.open(
            ROOT + "/candidates/zig_candidate.py", os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "private-native", lambda: os.open(
            PRIVATE_ROOT + "/reference-a/native/_zig_probe.so",
            os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "private-metadata", lambda: os.stat(PRIVATE_ROOT)),
        rejected(wall, "hidden-content", lambda: os.open(hidden, os.O_RDONLY)),
        rejected(wall, "hidden-metadata", lambda: os.stat(hidden)),
        rejected(wall, "archive", lambda: os.open(
            ROOT + "/oracle/phase2/evidence/private.json.gz",
            os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "proposal", lambda: os.open(
            ROOT + "/oracle/phase3/holdout-proposal.json",
            os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "write", lambda: os.open(
            path, os.O_WRONLY | os.O_TRUNC | os.O_NOFOLLOW)),
        rejected(wall, "mkdir", lambda: os.mkdir(ROOT + "/unsafe")),
        rejected(wall, "subprocess", lambda: os.system("true")),
        rejected(wall, "clock", lambda: time.perf_counter()),
        rejected(wall, "metadata", lambda: os.lstat(path)),
        rejected(wall, "foreign-read", lambda: os.read(0, 1)),
        rejected(wall, "foreign-fstat", lambda: os.fstat(0)),
        rejected(wall, "foreign-close", lambda: os.close(0)),
        rejected(wall, "foreign-write", lambda: os.write(1, b"x")),
    ]
    good_session = "v17-zig-public-v4-source-only-control"
    corrected = recovery_path(good_session)
    need(corrected == RECOVERY_PREFIX + "zig-public-v4-" + good_session
         and os.path.dirname(corrected) == "/tmp"
         and corrected.startswith(RECOVERY_PREFIX)
         and not "/tmp/rebar-zig-public-v1-recovery-".startswith(RECOVERY_PREFIX),
         "reject a recurrence of the exact V1 recovery-prefix failure")
    rejected_recovery = 0
    for value in ("", "v17-zig-public-v1-run-001", "v17-zig-public-v4-../x",
                  "v17-zig-public-v4-hidden", "v17-zig-public-v4-HIGH",
                  "v17-zig-public-v4-a/b", 7, None):
        try:
            recovery_path(value)
        except PublicError:
            rejected_recovery += 1
        else:
            raise PublicError("unsafe inherited V18 recovery session accepted")
    synthetic_message = "independently bounded synthetic V18 failure"
    synthetic_bytes = synthetic_message.encode("utf-8")
    bounded = {"text": synthetic_message,
               "total_bytes": len(synthetic_bytes),
               "captured_bytes": len(synthetic_bytes),
               "limit_bytes": 4096, "truncated": False,
               "sha256": digest(synthetic_bytes),
               "encoding": "UTF-8; INVALID BYTES BACKSLASH-ESCAPED"}
    synthetic_failure = {
        "schema": "rebar-owned-repaired-zig-original-campaign-v18-"
                  "actual-worker-failure",
        "status": "FAIL", "family": "zig",
        "label": "phase2-v18-zig-final-original-p0-v18",
        "suite": "public_v3", "case_execution_denominator": 864,
        "activation_stage": "SYNTHETIC SOURCE-ONLY AUTHENTICITY CONTROL",
        "error_type": "SyntheticOwnedFailure",
        "error_message": synthetic_message,
        "error_message_detail": dict(bounded),
        "error_traceback": dict(bounded),
        "traceback_frames": [{"file": ROOT + "/tools/first-party.py",
                              "function": "synthetic", "line": 1}],
        "traceback_frames_truncated": False,
        "runtime_guard_version": 4,
        "guard_installed_before_candidate_import": True,
        "candidate_imported": True,
        "actual_candidate_workers": 1,
        "synthetic_control": False,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "timing_trials_run": 0, "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    need(authenticated_worker_failure(synthetic_failure) is synthetic_failure,
         "preserve an exact bounded synthetic authentic V18 failure")
    diagnostic_rejections = 0
    for key, poisoned in (("schema", "forged"), ("status", "PASS"),
                          ("family", "rust"), ("activation_stage", ""),
                          ("error_type", ""), ("error_message", None),
                          ("error_traceback", {}), ("traceback_frames", []),
                          ("runtime_guard_version", 3),
                          ("candidate_imported", "NOT MEASURED"),
                          ("hidden_cases_read", 1)):
        changed = dict(synthetic_failure)
        changed[key] = poisoned
        if key == "traceback_frames":
            changed[key] = [{"file": 1, "function": "bad", "line": 1}]
        try:
            authenticated_worker_failure(changed)
        except PublicError:
            diagnostic_rejections += 1
        else:
            raise PublicError("discarded or forged nested worker failure escaped")
    actual_harness = state["history"]["adapted_harness"]
    namespace_controls = namespace_harness_controls(
        state["payloads"]["public_harness"], actual_harness,
    )
    poisoned_namespace = 0
    for old, poisoned in (
        (b'if name == "candidates":', b'if name.startswith("candidates"):'),
        (b'and getattr(module, "__file__", None) is None',
         b'and getattr(module, "__file__", None) is not None'),
        (b'and tuple(paths) == (owned_root,)', b'and bool(tuple(paths))'),
        (b'and getattr(specification, "origin", object()) is None',
         b'and getattr(specification, "origin", object()) is not None'),
        (b'and isinstance(loader, importlib.machinery.NamespaceLoader)',
         b'and isinstance(loader, object)'),
        (b'origin = owned_origin(module, description="first-party runtime " + name)',
         b'origin = owned_root'),
    ):
        need(actual_harness.count(old) == 1,
             "preserve a unique hostile namespace ownership-control anchor")
        try:
            namespace_harness_controls(
                state["payloads"]["public_harness"],
                actual_harness.replace(old, poisoned, 1),
            )
        except PublicError:
            poisoned_namespace += 1
        else:
            raise PublicError("forged or overly broad namespace package escaped")
    need(not wall.live and len(controls) >= 18,
         "close all frozen public descriptors and retain hostile controls")
    return {"schema": SCHEMA + "-source-only-gate", "status": "PASS",
            "mode": "self-test", "hostile_control_count": len(controls),
            "hostile_controls": controls,
            "authenticated_public_owner_count": len(PUBLIC_OWNERS),
            "public_case_count": CASE_COUNT,
            "public_api_operation_count": OPERATIONS_PER_DATASET,
            "zig_original_case_count": 31237,
            "zig_original_verified_passing_case_count": 31237,
            "zig_original_mismatch_count": 0,
            "candidate_source_files_opened": 0,
            "private_roots_opened": 0,
            "archives_opened": 0,
            "hidden_cases_read": 0,
            "candidate_workers_started": 0,
            "clock_samples": 0,
            "preserved_v1_failure_receipt_sha256": PREVIOUS_FAILURE[1],
            "repaired_v18_recovery_prefix": RECOVERY_PREFIX,
            "unsafe_recovery_sessions_rejected": rejected_recovery,
            "forged_nested_worker_failures_rejected": diagnostic_rejections,
            "authenticated_namespace_package_controls": namespace_controls,
            "forged_or_broadened_namespace_packages_rejected": poisoned_namespace,
            "v2_nested_activation_stage": "NOT MEASURED",
            "v2_candidate_import": "NOT MEASURED",
            "v2_matching_case_count": "NOT MEASURED",
            "recovery_directories_created": 0,
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "candidate_qualified": False,
            "winner_selected": False}


def verify_summary(wall: PublicWall, state: dict) -> dict:
    need(not wall.live,
         "close each authenticated immutable source-only descriptor")
    return {"schema": SCHEMA + "-source-only-gate", "status": "PASS",
            "mode": "verify-frozen-context",
            "authenticated_public_owner_count": len(PUBLIC_OWNERS),
            "public_case_count": CASE_COUNT,
            "public_api_operation_count": OPERATIONS_PER_DATASET,
            "public_dataset_count": DATASET_COUNT,
            "text_case_count": DOMAIN_CASE_COUNT,
            "bytes_case_count": DOMAIN_CASE_COUNT,
            "public_matrix_sha256": MATRIX_SHA,
            "published_seed": PUBLISHED_SEED,
            "zig_original_case_count": 31237,
            "zig_original_verified_passing_case_count": 31237,
            "zig_original_mismatch_count": 0,
            "zig_engine_sha256": ENGINE_SHA,
            "zig_bridge_sha256": BRIDGE_SHA,
            "zig_adapter_sha256": ADAPTER_SHA,
            "strict_runtime_guard_version": 4,
            "candidate_source_files_opened": 0,
            "private_roots_opened": 0,
            "archives_opened": 0,
            "hidden_cases_read": 0,
            "candidate_workers_started": 0,
            "clock_samples": 0,
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "candidate_qualified": False,
            "winner_selected": False}


def output_eligible(path: object, payload: object) -> bool:
    return (type(path) is str and type(payload) is bytes
            and (path.startswith(PUBLIC_OUTPUT + "/")
                 or path.startswith(ROOT + "/oracle/phase2/evidence/")
                 or path.startswith("/tmp/" + OVERLAY_PREFIX))
            and "/../" not in path and 0 <= len(payload) <= MAX_ACTUAL_BYTES)


def output_write(path: str, payload: bytes, mode: int = 0o600) -> dict:
    need(output_eligible(path, payload) is True,
         "reject unrelated or nonexclusive Zig public correctness output")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                 | os.O_CLOEXEC | os.O_NOFOLLOW, mode)
    try:
        view = memoryview(payload)
        while view:
            count = os.write(fd, view)
            need(type(count) is int and count > 0,
                 "reject incomplete exclusive public correctness evidence")
            view = view[count:]
        os.fsync(fd)
        info = os.fstat(fd)
        need(stat.S_ISREG(info.st_mode)
             and stat.S_IMODE(info.st_mode) == mode
             and info.st_nlink == 1 and info.st_size == len(payload),
             "reject substituted full public evidence")
        return {"path": path, "sha256": digest(payload), "bytes": len(payload),
                "device": info.st_dev, "inode": info.st_ino,
                "mode": format(mode, "04o"),
                "exclusive_creation": True, "file_fsync_completed": True}
    finally:
        os.close(fd)


ACTUAL_PINNED = {
    "previous_v1_source_sha256": PREVIOUS_SOURCE[1],
    "previous_v1_protocol_sha256": PREVIOUS_PROTOCOL[1],
    "previous_v1_contract_sha256": PREVIOUS_CONTRACT[1],
    "previous_v1_failure_sha256": PREVIOUS_FAILURE[1],
    "previous_v2_source_sha256": PREVIOUS_V2_SOURCE[1],
    "previous_v2_protocol_sha256": PREVIOUS_V2_PROTOCOL[1],
    "previous_v2_contract_sha256": PREVIOUS_V2_CONTRACT[1],
    "previous_v2_failure_sha256": PREVIOUS_V2_FAILURE[1],
    "previous_v3_source_sha256": PREVIOUS_V3_SOURCE[1],
    "previous_v3_protocol_sha256": PREVIOUS_V3_PROTOCOL[1],
    "previous_v3_contract_sha256": PREVIOUS_V3_CONTRACT[1],
    "previous_v3_failure_sha256": PREVIOUS_V3_FAILURE[1],
    "build_source_sha256": BUILD_SOURCE_SHA,
    "build_protocol_sha256": BUILD_PROTOCOL_SHA,
    "build_contract_sha256": BUILD_CONTRACT_SHA,
    "build_receipt_sha256": BUILD_RECEIPT_SHA,
    "root_receipt_sha256": ROOT_RECEIPT_SHA,
    "original_source_sha256": ORIGINAL_SOURCE_SHA,
    "original_protocol_sha256": ORIGINAL_PROTOCOL_SHA,
    "original_contract_sha256": ORIGINAL_CONTRACT_SHA,
    "original_pass_sha256": ORIGINAL_PASS_SHA,
    "guard_source_sha256": GUARD_SOURCE_SHA,
    "guard_protocol_sha256": GUARD_PROTOCOL_SHA,
    "guard_contract_sha256": GUARD_CONTRACT_SHA,
    "adapter_sha256": ADAPTER_SHA,
    "adapter_bytes": str(ADAPTER_BYTES),
    "engine_source_sha256": ENGINE_SOURCE_SHA,
    "bridge_source_sha256": BRIDGE_SOURCE_SHA,
    "native_engine_sha256": ENGINE_SHA,
    "native_engine_bytes": str(ENGINE_BYTES),
    "native_bridge_sha256": BRIDGE_SHA,
    "native_bridge_bytes": str(BRIDGE_BYTES),
    "private_root": PRIVATE_ROOT,
    "private_root_device": str(PRIVATE_DEVICE),
    "private_root_inode": str(PRIVATE_ROOT_INODE),
    "public_harness_sha256": PUBLIC_HARNESS_SHA,
    "zig_harness_sha256": ZIG_HARNESS_SHA,
}


def recovery_path(session: object) -> str:
    need(type(session) is str and 1 <= len(session) <= 72
         and session.startswith("v17-zig-public-v4-")
         and all(character in "abcdefghijklmnopqrstuvwxyz0123456789-"
                 for character in session)
         and not any(word in session for word in
                     ("holdout", "hidden", "sealed", "proposal")),
         "reject unsafe or non-public exact V18 recovery session")
    path = RECOVERY_PREFIX + "zig-public-v4-" + session
    need(os.path.dirname(path) == "/tmp"
         and path.startswith(RECOVERY_PREFIX)
         and "/../" not in path and not path.endswith("/")
         and path != "/tmp" and path != RECOVERY_PREFIX,
         "preserve the exact inherited original V18 recovery safety guard")
    return path


def actual_authority(options: dict) -> None:
    need(options.get("root_authorized") is True
         and options.get("frozen_committed_pushed") is True
         and commit(options.get("frozen_commit"), "frozen public V4 commit")
         == commit(options.get("pushed_commit"), "pushed public V4 commit"),
         "require the exact already committed and pushed root-authorized freeze")
    for name, value in ACTUAL_PINNED.items():
        need(options.get(name) == value,
             "require root-pinned exact independently built Zig owner: " + name)
    session = options.get("session")
    need(type(session) is str and 1 <= len(session) <= 72
         and session.startswith("v17-zig-public-v4-")
         and all(char in "abcdefghijklmnopqrstuvwxyz0123456789-"
                 for char in session)
         and not any(word in session for word in
                     ("holdout", "hidden", "sealed", "proposal")),
         "require one fresh, exclusively public Zig correctness session")
    recovery_path(session)


def authenticated_worker_failure(observed: object) -> dict:
    need(type(observed) is dict
         and observed.get("schema") ==
             "rebar-owned-repaired-zig-original-campaign-v18-actual-worker-failure"
         and observed.get("status") == "FAIL"
         and observed.get("family") == "zig"
         and observed.get("label") == "phase2-v18-zig-final-original-p0-v18"
         and observed.get("suite") == "public_v3"
         and observed.get("runtime_guard_version") == 4
         and type(observed.get("guard_installed_before_candidate_import")) is bool
         and type(observed.get("candidate_imported")) is bool
         and observed.get("actual_candidate_workers") == 1
         and observed.get("synthetic_control") is False
         and observed.get("hidden_cases_read") == 0
         and observed.get("benchmark_files_read") == 0
         and observed.get("timing_trials_run") == 0
         and observed.get("holdout") == "NOT OPENED"
         and observed.get("winner_selected") is False,
         "preserve an authentic full V18 FAIL instead of replacing its stage")
    stage = observed.get("activation_stage")
    kind = observed.get("error_type")
    message = observed.get("error_message")
    detail = observed.get("error_message_detail")
    traceback = observed.get("error_traceback")
    frames = observed.get("traceback_frames")
    need(type(stage) is str and 0 < len(stage) <= 256
         and type(kind) is str and 0 < len(kind) <= 256
         and type(message) is str and len(message.encode("utf-8")) <= 65536
         and type(detail) is dict and type(traceback) is dict
         and type(frames) is list and len(frames) <= 64
         and type(observed.get("traceback_frames_truncated")) is bool
         and observed.get("case_execution_denominator") in (None, 864, CASE_COUNT)
         and (not observed["candidate_imported"]
              or observed["guard_installed_before_candidate_import"]),
         "reject omitted, invented, unbounded, or contradictory V18 failure")
    for value, label in ((detail, "message"), (traceback, "traceback")):
        text = value.get("text")
        total = value.get("total_bytes")
        captured = value.get("captured_bytes")
        limit = value.get("limit_bytes")
        fingerprint = value.get("sha256")
        need(type(text) is str and type(total) is int and total >= 0
             and type(captured) is int and 0 <= captured <= total
             and type(limit) is int and 0 < limit <= 1048576
             and captured <= limit
             and type(value.get("truncated")) is bool
             and captured == len(text.encode("utf-8", "backslashreplace"))
             and len(text.encode("utf-8", "backslashreplace")) <= limit
             and sha(fingerprint, "authentic nested " + label)
                 == fingerprint,
             "reject incomplete authentic bounded V18 " + label)
    for frame in frames:
        need(type(frame) is dict and type(frame.get("file")) is str
             and type(frame.get("function")) is str
             and type(frame.get("line")) is int
             and 0 < frame["line"] < 10_000_000,
             "reject replaced or invented nested V18 traceback frame")
    return observed


def v18_module(state: dict):
    row = next(entry for entry in PUBLIC_OWNERS
               if entry[0] == "zig_original_source")
    module = types.ModuleType("_rebar_zig_v4_exact_v18_runtime")
    module.__file__ = ROOT + "/" + row[1]
    exec(compile(state["payloads"]["zig_original_source"], module.__file__,
                 "exec", dont_inherit=True), module.__dict__)
    need(module.SELF == row[1] and module.SCHEMA
         == "rebar-owned-repaired-zig-original-campaign-v18"
         and module.FAMILY == "zig"
         and module.BUILD_LABEL == "phase2-v17-zig-final-original"
         and module.GUARD[0][1] == GUARD_SOURCE_SHA,
         "reject the exact already-original-qualified V18 guarded worker")
    return module


def isolated_candidate(options: dict, state: dict) -> dict:
    actual_authority(options)
    v18 = v18_module(state)
    recovery = recovery_path(options["session"])
    v18.RECOVERY = recovery
    original_state = v18.frozen_context(ORIGINAL_SOURCE_SHA,
                                         ORIGINAL_PROTOCOL_SHA,
                                         ORIGINAL_CONTRACT_SHA)
    legacy = v18.patched_legacy(original_state)
    legacy.RECOVERY = recovery
    producer = original_state["producer"]
    suite = producer.suite_spec("public_v3")
    need(suite.name == "public_v3" and suite.case_count == 864,
         "retain exact inherited original suite before bounded public overlay")
    original_suite = producer.suite_spec

    def public_suite(name):
        need(name == "public_v3",
             "reject a substituted candidate public worker suite")
        return types.SimpleNamespace(name="public_v3", case_count=CASE_COUNT)

    transformed = state["history"]["adapted_harness"]

    def public_observer(selected_suite, selected, pins, source_pins, manifest):
        need(selected_suite.name == "public_v3"
             and selected_suite.case_count == CASE_COUNT
             and selected.name == "zig"
             and len(pins) == 3 and type(source_pins) is dict
             and type(manifest) is dict,
             "reject an unguarded or substituted complete Zig observation")
        harness = types.ModuleType("_rebar_owned_zig_full_public_v4_worker")
        harness.__file__ = ROOT + "/tools/rust_public_practice_benchmark_v2.py"
        harness.__package__ = None
        exec(compile(transformed, harness.__file__, "exec",
                     dont_inherit=True), harness.__dict__)
        harness.verify_pinned_runtime(permit_candidate=True)
        observed = harness.observe_worker("zig-public-v4-candidate", "rust")
        records = observed.get("records")
        need(type(records) is list and len(records) == CASE_COUNT
             and observed.get("matrix_sha256") == MATRIX_SHA
             and observed.get("published_seed") == PUBLISHED_SEED
             and observed.get("candidate_runtime_provenance_checked") is True
             and observed.get("external_regex_package_count") == 0
             and observed.get("hidden_cases_read") == 0,
             "preserve every guarded public Zig outcome without delegation")
        return {"status": "PASS", "suite": "public_v3",
                "candidate_family": "zig",
                "case_execution_denominator": CASE_COUNT,
                "actual_candidate_workers": 1,
                "records": records,
                "records_sha256": observed["records_sha256"],
                "candidate_worker_pid": observed["pid"],
                "runtime_guard_version": 4,
                "guard_installed_before_candidate_import": True,
                "hidden_cases_read": 0,
                "benchmark_files_read": 0,
                "holdout": "NOT OPENED",
                "timing_trials_run": 0}

    producer.suite_spec = public_suite
    producer.observe_direct_suite = public_observer
    journal = sha(options.get("journal_sha256"),
                  "active genuine V18 recovery journal")
    args = {
        "--source-sha256": ORIGINAL_SOURCE_SHA,
        "--protocol-sha256": ORIGINAL_PROTOCOL_SHA,
        "--contract-sha256": ORIGINAL_CONTRACT_SHA,
        "--family": "zig",
        "--label": v18.LABEL,
        "--suite": "public_v3",
        "--recovery-journal-sha256": journal,
        "--root-authorized": True,
        "--frozen-committed-pushed": True,
        "--frozen-commit": options["frozen_commit"],
        "--pushed-commit": options["pushed_commit"],
    }
    args.update({flag: value for flag, value in v18.ACTUAL_PINS})
    observed = v18.worker(args, state=original_state, legacy=legacy)
    if observed.get("status") == "FAIL":
        failure = authenticated_worker_failure(observed)
        return {"schema": SCHEMA + "-isolated-candidate-failure",
                "status": "FAIL", "family": "zig",
                "public_case_execution_denominator": CASE_COUNT,
                "public_api_operation_count": OPERATIONS_PER_DATASET,
                "runtime_guard_version": 4,
                "guard_installed_before_candidate_import":
                    failure["guard_installed_before_candidate_import"],
                "candidate_imported": failure["candidate_imported"],
                "activation_stage": failure["activation_stage"],
                "error_type": failure["error_type"],
                "error_message": failure["error_message"],
                "error_traceback": failure["error_traceback"],
                "traceback_frames": failure["traceback_frames"],
                "traceback_frames_truncated":
                    failure["traceback_frames_truncated"],
                "authentic_v18_worker_failure": failure,
                "matching_case_count": "NOT MEASURED",
                "hidden_cases_read": 0,
                "holdout": "NOT OPENED", "timing_trials_run": 0,
                "performance": "NOT MEASURED", "candidate_qualified": False,
                "winner_selected": False}
    need(observed.get("status") == "PASS"
         and observed.get("runtime_guard_version") == 4
         and observed.get("guard_installed_before_candidate_import") is True
         and observed.get("candidate_imported") is True
         and observed.get("case_execution_denominator") == CASE_COUNT,
         "require genuine installed V4 before complete Zig candidate execution")
    observation = observed.get("complete_actual_observation")
    need(type(observation) is dict
         and type(observation.get("records")) is list
         and len(observation["records"]) == CASE_COUNT,
         "publish all complete guarded Zig public records")
    return {"schema": SCHEMA + "-isolated-candidate-worker",
            "status": "PASS", "family": "zig",
            "pid": observation["candidate_worker_pid"],
            "case_count": CASE_COUNT,
            "matrix_sha256": MATRIX_SHA,
            "published_seed": PUBLISHED_SEED,
            "runtime_guard_version": 4,
            "guard_installed_before_candidate_import": True,
            "candidate_imported": True,
            "records_sha256": observation["records_sha256"],
            "records": observation["records"],
            "external_regex_package_count": 0,
            "hidden_cases_read": 0,
            "holdout": "NOT OPENED",
            "timing_trials_run": 0}


def actual_run(options: dict, state: dict) -> dict:
    actual_authority(options)
    kernel = state["module"]
    v18 = v18_module(state)
    recovery = recovery_path(options["session"])
    v18.RECOVERY = recovery
    original_state = v18.frozen_context(ORIGINAL_SOURCE_SHA,
                                         ORIGINAL_PROTOCOL_SHA,
                                         ORIGINAL_CONTRACT_SHA)
    legacy = v18.patched_legacy(original_state)
    legacy.RECOVERY = recovery
    before = [legacy.target_identity(role, v18.ORIGINALS[role])
              for role in v18.ROLES]
    recovery_fd = lock_fd = candidate_fd = None
    restored = None
    primary = None
    published = None
    try:
        recovery_fd, lock_fd, candidate_fd, journal = v18.prepare(
            legacy, original_state)
        journal_sha = journal["published_journal"]["sha256"]

        import tempfile
        import subprocess
        import json

        overlay = tempfile.mkdtemp(prefix=OVERLAY_PREFIX, dir="/tmp")
        need(os.path.realpath(overlay) == overlay
             and stat.S_IMODE(os.stat(overlay).st_mode) == 0o700,
             "create only one fresh owner-only standard-library oracle overlay")
        os.mkdir(overlay + "/tools", 0o700)
        output_write(overlay + "/tools/rust_public_practice_benchmark_v2.py",
                     state["payloads"]["public_harness"])
        previous_bootstrap = kernel.WORKER_BOOTSTRAP
        old_prefix = "rebar-rust-native-public-v3-"
        need(previous_bootstrap.count(old_prefix) == 1,
             "preserve the original unmodified complete public worker kernel")
        kernel.WORKER_BOOTSTRAP = previous_bootstrap.replace(
            old_prefix, OVERLAY_PREFIX)
        reference, reference_raw = kernel.run_worker(
            overlay, "rust_public_practice_benchmark_v2.py",
            PUBLIC_HARNESS_SHA, "zig-public-v4-stdlib", "stdlib", "observe")
        need(reference.get("case_count") == CASE_COUNT
             and reference.get("oracle_is_stdlib_only") is True,
             "execute every real isolated standard-library public answer")

        command = [PYTHON, "-I", "-B", "-S", ROOT + "/" + SOURCE,
                   "--candidate-worker"]
        for name in ("source_sha256", "protocol_sha256", "contract_sha256",
                     "frozen_commit", "pushed_commit", "session"):
            command.extend(("--" + name.replace("_", "-"), options[name]))
        for name, value in ACTUAL_PINNED.items():
            command.extend(("--" + name.replace("_", "-"), value))
        command.extend(("--journal-sha256", journal_sha,
                        "--root-authorized", "--frozen-committed-pushed"))
        child = subprocess.Popen(
            command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=ROOT, shell=False, close_fds=True,
            env={"PATH": "/usr/bin:/bin", "LC_ALL": "C",
                 "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                 "PYTHONMALLOC": "malloc"})
        stdout, stderr = child.communicate(timeout=300)
        need(child.returncode in (0, 1) and not stderr
             and 0 < len(stdout) <= MAX_ACTUAL_BYTES,
             "strict-V4 Zig candidate did not publish bounded authentic JSON: "
             + stderr[:3000].decode("utf-8", "replace"))
        candidate = json.loads(stdout.decode("utf-8"))
        if child.returncode == 1:
            need(type(candidate) is dict
                 and candidate.get("schema")
                     == SCHEMA + "-isolated-candidate-failure"
                 and candidate.get("status") == "FAIL"
                 and candidate.get("family") == "zig"
                 and candidate.get("public_case_execution_denominator") == CASE_COUNT
                 and candidate.get("public_api_operation_count")
                     == OPERATIONS_PER_DATASET
                 and candidate.get("runtime_guard_version") == 4
                 and candidate.get("matching_case_count") == "NOT MEASURED"
                 and candidate.get("hidden_cases_read") == 0
                 and candidate.get("holdout") == "NOT OPENED"
                 and candidate.get("timing_trials_run") == 0
                 and candidate.get("candidate_qualified") is False
                 and candidate.get("winner_selected") is False,
                 "reject substituted or weakened nested candidate failure")
            nested = authenticated_worker_failure(
                candidate.get("authentic_v18_worker_failure")
            )
            need(candidate.get("activation_stage") == nested["activation_stage"]
                 and candidate.get("error_type") == nested["error_type"]
                 and candidate.get("error_message") == nested["error_message"]
                 and candidate.get("error_traceback") == nested["error_traceback"]
                 and candidate.get("traceback_frames") == nested["traceback_frames"]
                 and candidate.get("guard_installed_before_candidate_import")
                     == nested["guard_installed_before_candidate_import"]
                 and candidate.get("candidate_imported")
                     == nested["candidate_imported"],
                 "preserve every authentic V18 stage, error, and import observation")
            raise CapturedWorkerFailure({
                "schema": SCHEMA + "-actual-authenticated-worker-failure",
                "version": VERSION,
                "status": "FAIL",
                "family": "zig",
                "session": options["session"],
                "source_sha256": options["source_sha256"],
                "protocol_sha256": options["protocol_sha256"],
                "contract_sha256": options["contract_sha256"],
                "frozen_commit": options["frozen_commit"],
                "pushed_commit": options["pushed_commit"],
                "preserved_v1_failure_sha256": PREVIOUS_FAILURE[1],
                "preserved_v2_failure_sha256": PREVIOUS_V2_FAILURE[1],
                "v2_nested_stage": "NOT MEASURED; V2 DISCARDED INNER DOCUMENT",
                "v2_candidate_import": "NOT MEASURED; V2 DISCARDED INNER DOCUMENT",
                "v2_matching_case_count": "NOT MEASURED; V2 DISCARDED INNER DOCUMENT",
                "public_case_execution_denominator": CASE_COUNT,
                "public_api_operation_count": OPERATIONS_PER_DATASET,
                "actual_reference_worker_count": 1,
                "actual_candidate_worker_count": 1,
                "actual_reference_case_count": CASE_COUNT,
                "runtime_guard_version": 4,
                "guard_installed_before_candidate_import":
                    nested["guard_installed_before_candidate_import"],
                "candidate_imported": nested["candidate_imported"],
                "activation_stage": nested["activation_stage"],
                "error_type": nested["error_type"],
                "error_message": nested["error_message"],
                "error_traceback": nested["error_traceback"],
                "traceback_frames": nested["traceback_frames"],
                "traceback_frames_truncated": nested["traceback_frames_truncated"],
                "complete_authentic_v18_worker_failure": nested,
                "candidate_matching_case_count": "NOT MEASURED",
                "candidate_wider_public_correctness": "NOT MEASURED",
                "hidden_cases_read": 0,
                "holdout": "NOT OPENED", "timing_trials_run": 0,
                "performance": "NOT MEASURED",
                "runtime_non_delegation": "NOT ESTABLISHED",
                "candidate_qualified": False, "winner_selected": False,
            })
        need(child.returncode == 0,
             "reject a candidate success without a genuine zero process status")
        need(type(candidate) is dict
             and candidate.get("schema") == SCHEMA + "-isolated-candidate-worker"
             and candidate.get("status") == "PASS"
             and candidate.get("family") == "zig"
             and candidate.get("case_count") == CASE_COUNT
             and candidate.get("matrix_sha256") == MATRIX_SHA
             and candidate.get("runtime_guard_version") == 4
             and candidate.get("guard_installed_before_candidate_import") is True
             and candidate.get("external_regex_package_count") == 0
             and candidate.get("hidden_cases_read") == 0
             and candidate.get("pid") != reference.get("pid"),
             "require independently isolated strict-V4 full Zig candidate")
        baseline_rows = reference.get("records")
        actual_rows = candidate.get("records")
        need(type(baseline_rows) is list and type(actual_rows) is list
             and len(baseline_rows) == len(actual_rows) == CASE_COUNT,
             "never omit a baseline or candidate public case")
        mismatches = []
        for expected, actual in zip(baseline_rows, actual_rows):
            need(type(expected) is dict and type(actual) is dict
                 and expected.get("case") == actual.get("case"),
                 "reject reordered or deleted complete public case")
            if expected != actual:
                mismatches.append({"case": expected["case"],
                                   "expected_record": expected,
                                   "actual_record": actual})
        status = "PASS" if not mismatches else "FAIL"
        full = {"schema": SCHEMA + "-complete-public-observation",
                "status": status,
                "family": "zig",
                "case_denominator": CASE_COUNT,
                "actual_baseline_cases": CASE_COUNT,
                "actual_zig_cases": CASE_COUNT,
                "mismatch_count": len(mismatches),
                "all_mismatches": mismatches,
                "public_api_operation_count": OPERATIONS_PER_DATASET,
                "dataset_count": DATASET_COUNT,
                "text_case_count": DOMAIN_CASE_COUNT,
                "bytes_case_count": DOMAIN_CASE_COUNT,
                "matrix_sha256": MATRIX_SHA,
                "published_seed": PUBLISHED_SEED,
                "reference_pid": reference["pid"],
                "zig_pid": candidate["pid"],
                "actual_candidate_workers": 1,
                "actual_reference_workers": 1,
                "runtime_guard_version": 4,
                "guard_installed_before_candidate_import": True,
                "timing_trials_run": 0,
                "clock_samples": 0,
                "hidden_cases_read": 0,
                "holdout": "NOT OPENED",
                "candidate_qualified": False,
                "winner_selected": False}
        try:
            os.mkdir(PUBLIC_OUTPUT, 0o700)
        except FileExistsError:
            info = os.stat(PUBLIC_OUTPUT, follow_symlinks=False)
            need(stat.S_ISDIR(info.st_mode)
                 and stat.S_IMODE(info.st_mode) == 0o700
                 and info.st_uid == os.geteuid(),
                 "reject substituted public correctness evidence directory")
        target = PUBLIC_OUTPUT + "/" + options["session"]
        os.mkdir(target, 0o700)
        artifacts = [
            output_write(target + "/public-10434-stdlib.correctness.raw.json",
                         reference_raw),
            output_write(target + "/public-10434-zig.correctness.raw.json",
                         kernel.document(candidate)),
            output_write(target + "/public-10434-correctness.raw.json",
                         kernel.document(full)),
        ]
        receipt = {"schema": SCHEMA + "-durable-publication-receipt",
                   "version": VERSION,
                   "status": "PASS",
                   "publication_status": "PASS",
                   "publication_pass_means": "DURABLE PUBLICATION ONLY",
                   "candidate_status": status,
                   "family": "zig",
                   "public_10434_correctness_status": status,
                   "public_10434_case_count": CASE_COUNT,
                   "public_10434_verified_passing_case_count":
                        CASE_COUNT - len(mismatches),
                   "public_10434_mismatch_count": len(mismatches),
                   "all_public_mismatches_preserved": True,
                   "public_api_operation_count": OPERATIONS_PER_DATASET,
                   "public_dataset_count": DATASET_COUNT,
                   "public_text_case_count": DOMAIN_CASE_COUNT,
                   "public_bytes_case_count": DOMAIN_CASE_COUNT,
                   "matrix_sha256": MATRIX_SHA,
                   "published_seed": PUBLISHED_SEED,
                   "reference_worker_count": 1,
                   "candidate_worker_count": 1,
                   "reference_pid": reference["pid"],
                   "zig_pid": candidate["pid"],
                   "strict_runtime_guard_version": 4,
                   "guard_installed_before_candidate_import": True,
                   "source_sha256": options["source_sha256"],
                   "protocol_sha256": options["protocol_sha256"],
                   "contract_sha256": options["contract_sha256"],
                   "frozen_commit": options["frozen_commit"],
                   "pushed_commit": options["pushed_commit"],
                   "v17_build_receipt_sha256": BUILD_RECEIPT_SHA,
                   "v17_private_root_receipt_sha256": ROOT_RECEIPT_SHA,
                   "v18_original_pass_receipt_sha256": ORIGINAL_PASS_SHA,
                   "v18_original_verified_passing_case_count": 31237,
                   "final_adapter_sha256": ADAPTER_SHA,
                   "native_engine_sha256": ENGINE_SHA,
                   "native_bridge_sha256": BRIDGE_SHA,
                   "frozen_111_operation_harness_sha256": PUBLIC_HARNESS_SHA,
                   "authenticated_zig_harness_transform_sha256": ZIG_HARNESS_SHA,
                   "historical_zig_mismatch_count_preserved": 1156,
                   "artifacts": artifacts,
                   "timing_trials_run": 0,
                   "clock_samples": 0,
                   "performance": "NOT MEASURED",
                   "memory": "NOT MEASURED",
                   "undefined_behavior": "NOT MEASURED",
                   "runtime_non_delegation": "NOT ESTABLISHED",
                   "candidate_qualified": False,
                   "hidden_cases_read": 0,
                   "winner_selected": False,
                   "final_holdout": FINAL_HOLDOUT}
        receipt_path = (ROOT + "/oracle/phase2/evidence/"
                        "zig-full-public-correctness-v4-" + options["session"]
                        + "-publication-receipt.json")
        publication = output_write(receipt_path, kernel.document(receipt))
        published = {"schema": SCHEMA + "-actual-root-operation",
                     "status": status,
                     "publication_status": "PASS",
                     "publication_pass_means": "DURABLE PUBLICATION ONLY",
                     "candidate_status": status,
                     "family": "zig",
                     "public_10434_correctness_status": status,
                     "public_10434_case_count": CASE_COUNT,
                     "public_10434_verified_passing_case_count":
                         CASE_COUNT - len(mismatches),
                     "public_10434_mismatch_count": len(mismatches),
                     "public_api_operation_count": OPERATIONS_PER_DATASET,
                     "candidate_worker_count": 1,
                     "reference_worker_count": 1,
                     "strict_runtime_guard_version": 4,
                     "guard_installed_before_candidate_import": True,
                     "v18_original_verified_passing_case_count": 31237,
                     "canonical_candidate_modified": False,
                     "publication_receipt": publication,
                     "artifacts": artifacts,
                     "runtime_non_delegation": "NOT ESTABLISHED",
                     "performance": "NOT MEASURED",
                     "memory": "NOT MEASURED",
                     "hidden_cases_read": 0,
                     "candidate_qualified": False,
                     "winner_selected": False}
    except CapturedWorkerFailure as error:
        published = error.document
    except BaseException as error:
        primary = error
    finally:
        if candidate_fd is not None:
            try:
                with legacy.CriticalSignals():
                    restored = legacy.restore(candidate_fd, journal)
            except BaseException as error:
                if primary is None:
                    primary = error
            finally:
                os.close(candidate_fd)
                os.close(lock_fd)
                os.close(recovery_fd)
    if primary is not None:
        raise primary
    need(type(restored) is list and len(restored) == 3
         and all(legacy.target_identity(role, v18.ORIGINALS[role])
                 for role in v18.ROLES)
         and type(published) is dict,
         "restore all three exact original Zig candidate owner inodes")
    published["all_three_original_targets_restored"] = True
    if published.get("status") == "FAIL":
        receipt_path = (ROOT + "/oracle/phase2/evidence/"
                        "zig-full-public-correctness-v4-" + options["session"]
                        + "-authenticated-worker-failure.json")
        publication = output_write(receipt_path, kernel.document(published))
        published["durable_failure_receipt"] = publication
    return published


def parse_options(values: list[str]) -> dict:
    modes = [item for item in values if item in SOURCE_MODES + ACTUAL_MODES]
    need(len(modes) == 1,
         "select exactly one Zig public source-only, root, or candidate action")
    result: dict[str, object] = {"mode": modes[0]}
    at = 0
    while at < len(values):
        flag = values[at]
        if flag in SOURCE_MODES + ACTUAL_MODES:
            at += 1
            continue
        if flag in ("--root-authorized", "--frozen-committed-pushed"):
            key = flag[2:].replace("-", "_")
            need(key not in result, "reject duplicate root-only public authority")
            result[key] = True
            at += 1
            continue
        need(flag.startswith("--") and at + 1 < len(values),
             "reject incomplete or positional public correctness authority")
        key = flag[2:].replace("-", "_")
        need(key not in result,
             "reject duplicate independently pinned public authority: " + flag)
        result[key] = values[at + 1]
        at += 2
    standard = {"source_sha256", "protocol_sha256"}
    if result["mode"] != "--render-contract":
        standard.add("contract_sha256")
    for name in standard:
        sha(result.get(name), name)
    if result["mode"] in SOURCE_MODES:
        need(set(result) == {"mode", *standard},
             "source gates cannot authorize candidates, private roots, or workers")
    else:
        extras = {"root_authorized", "frozen_committed_pushed",
                  "frozen_commit", "pushed_commit", "session",
                  *ACTUAL_PINNED}
        if result["mode"] == "--candidate-worker":
            extras.add("journal_sha256")
        need(set(result) == {"mode", *standard, *extras},
             "pin every independently built root-only Zig public owner")
        for name in (*standard, *ACTUAL_PINNED):
            if name.endswith("_sha256"):
                sha(result.get(name), name)
        commit(result.get("frozen_commit"), "frozen Zig public commit")
        commit(result.get("pushed_commit"), "pushed Zig public commit")
        if result["mode"] == "--candidate-worker":
            sha(result.get("journal_sha256"), "active V18 recovery journal")
    return result


def main(values: list[str]) -> int:
    need(sys.executable == PYTHON
         and sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1
         and sys.flags.no_site == 1
         and sys.dont_write_bytecode is True,
         "use exact isolated no-site no-bytecode pinned CPython 3.14.6")
    sterile_modules()
    options = parse_options(values)
    wall = PublicWall() if options["mode"] in SOURCE_MODES else None
    if wall is not None:
        wall.install()
    state = load_context(options, wall)
    if options["mode"] == "--render-contract":
        need(wall is not None and not wall.live,
             "close all public descriptors before canonical source rendering")
        result = state["freeze"]
    elif options["mode"] == "--verify-frozen-context":
        need(wall is not None, "require permanent source-only verification wall")
        result = verify_summary(wall, state)
    elif options["mode"] == "--self-test":
        need(wall is not None, "require permanent source-only hostile-control wall")
        result = self_test(wall, state)
    elif options["mode"] == "--candidate-worker":
        result = isolated_candidate(options, state)
    else:
        result = actual_run(options, state)
    sys.stdout.buffer.write(state["module"].document(result))
    sys.stdout.buffer.flush()
    return 0 if result.get("status") == "PASS" or options["mode"] == "--render-contract" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (PublicError, OSError, ValueError, TypeError, KeyError,
            SyntaxError, AttributeError) as error:
        sys.stderr.write("full first-party Zig public correctness rejected: "
                         + type(error).__qualname__ + ": " + str(error) + "\\n")
        raise SystemExit(2)
