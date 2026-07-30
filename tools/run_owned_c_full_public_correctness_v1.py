#!/usr/bin/env python3
"""Freeze the immutable 10,434-case public oracle for the final C24 engine.

Source gates authenticate public plaintext owners only.  They physically deny
candidate sources, private roots, native objects, archives, proposals, holdouts,
workers, clocks, entropy, and workspace mutations.  Separately authorized root
execution reuses the genuine C16 dual-owner journals and authentic V4 policy,
runs independent complete stdlib/C observations, restores both exact original
canonical inodes, and only then publishes every complete record and mismatch.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("full C public correctness requires a matcher-free bootstrap")

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
SOURCE = "tools/run_owned_c_full_public_correctness_v1.py"
PROTOCOL = "oracle/phase2/C-FULL-PUBLIC-CORRECTNESS-V1.md"
CONTRACT = "oracle/phase2/c-full-public-correctness-v1.json"
SCHEMA = "rebar-owned-c-full-public-correctness-v1"
VERSION = 1
CASE_COUNT = 10434
DATASET_COUNT = 94
OPERATIONS_PER_DATASET = 111
DOMAIN_CASE_COUNT = 5217
PUBLISHED_SEED = 5928217332825411634
MATRIX_SHA = "0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d"
FINAL_HOLDOUT = "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
PUBLIC_HARNESS_SHA = "a3d7e70343d231bf433fbad6a6669025a970d83691c49cb9f434a186aef3d9e6"
C_HARNESS_SHA = "140ff194bdd0d49dbfc5819282a46bb72391899bf3c17f735adfc96ed181c829"
C_HARNESS_BYTES = 112748
BUILD_SOURCE_SHA = "a82f5613ea2d57e15dfcaf6cc8e6d6c88ed13d23d78bb02dbd5267a73c5621be"
BUILD_PROTOCOL_SHA = "080fea9f10569e4601c48c913e0b1a311ade4eb9ea458b5514170800b1111ed0"
BUILD_CONTRACT_SHA = "9e6e92cdd7fe58c1351b6fb24e7f265f722c4928353d80a27ede75028c5f5901"
BUILD_RECEIPT_SHA = "ed0c119b2e672342f3665c9dc7c4896977ea590bceec08ff3b97cd56b9f92a75"
ROOT_RECEIPT_SHA = "36cb6adcf3a28d635fc997c090e62e1ce5563754deab02c05b41f4d034ad3048"
ORIGINAL_SOURCE_SHA = "1e39850940de3d001cc5fb80d6e9944c55997ce8cd2f772ed38cb6dea93ec663"
ORIGINAL_PROTOCOL_SHA = "20b364e18f89f607ca023956fdddf8b54f5094fcf6c7c7598ddeab599e233bf4"
ORIGINAL_CONTRACT_SHA = "a7d2a46f874b78b44a73da9a87ade3713116a0b1ed337f58fdc2c76516f146dd"
ORIGINAL_PASS_SHA = "34f1b7ccd9fe06408cdc6094f86bf98f4776bc7716ad970264bfbbda0d1280f2"
GUARD_SOURCE_SHA = "5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3"
GUARD_PROTOCOL_SHA = "835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16"
GUARD_CONTRACT_SHA = "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2"
ADAPTER_SHA = "e91819b1d6b399954b3384519fdfddb6ccd6d4e4099a34e06d702c9959a79193"
ADAPTER_BYTES = 62209
NATIVE_SOURCE_SHA = "99f45846551705379ccd7365333995ee68fe25e10d101655a17ad45c5e13a5e6"
NATIVE_SOURCE_BYTES = 221715
NATIVE_SHA = "891acc0d0f496045e90e2efc0f0a3125e4f508352c2ee5e31ee807ea2fb1801a"
NATIVE_BYTES = 163544
ORIGINAL_ADAPTER_SHA = "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
ORIGINAL_ADAPTER_BYTES = 60707
ORIGINAL_ADAPTER_INODE = 428074
ORIGINAL_NATIVE_SHA = "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd"
ORIGINAL_NATIVE_BYTES = 149976
ORIGINAL_NATIVE_INODE = 430300
PRIVATE_ROOT = "/tmp/rebar-phase2-c-complete-native-semantics-v24-d95b1a1342b65ddc0bf118d181aeca8b"
PRIVATE_ROOT_INODE = 11680793
MAX_OWNER_BYTES = 2 * 1024 * 1024
MAX_ACTUAL_BYTES = 128 * 1024 * 1024
SOURCE_MODES = ("--render-contract", "--verify-frozen-context", "--self-test")
ACTUAL_MODES = ("--run", "--candidate-worker")
OVERLAY_PREFIX = "rebar-c-full-public-correctness-v1-"
PUBLIC_OUTPUT = ROOT + "/experiments/c_full_public_correctness_v1"
RECOVERY_PREFIX = "/tmp/rebar-phase2-repaired-c-original-campaign-v16-public-v1-"

PUBLIC_OWNERS = (
    ("rust_v5_source", "tools/run_owned_rust_full_public_correctness_v5.py", "97d36e9448336d3cfa732324779c14959bf739a8e6daa556d839e0ecdd0d0602", 83637, 430313),
    ("rust_v5_protocol", "oracle/phase2/RUST-FULL-PUBLIC-CORRECTNESS-V5.md", "066f3e4663bb19612b795f797144c0098bf2d998455d3c0b4c814186d0204bd0", 6570, 525361),
    ("rust_v5_contract", "oracle/phase2/rust-full-public-correctness-v5.json", "fd10e77356945e7544d5b5b91d7a95f95c173384e152506e02c11240b58eb52c", 31041, 525365),
    ("rust_v5_pass", "oracle/phase2/evidence/rust-full-public-correctness-v5-v33-full-public-v5-run-001-publication-receipt.json", "8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9", 6889, 525451),
    ("public_kernel", "tools/run_owned_rust_native_architecture_public_gate_v3.py", "12d0ae388cd2841d0cb091e7da88859a772a3b3c293f18938b488196a32c5eab", 106590, 431279),
    ("public_kernel_protocol", "oracle/phase2/RUST-NATIVE-ARCHITECTURE-PUBLIC-GATE-V3.md", "fdf695478fc1b542026c2b98ba94524df254aea84b46ebab568a98050474cae4", 5911, 525630),
    ("public_kernel_contract", "oracle/phase2/rust-native-architecture-public-gate-v3.json", "80a350478ae4dbf4d745683974b4c60630d900d2e3f97d59cf391bfb1d8358a0", 26615, 525842),
    ("public_harness", "tools/rust_public_practice_benchmark_v2.py", PUBLIC_HARNESS_SHA, 112729, 429259),
    ("c24_source", "tools/reproduce_owned_c_complete_semantic_source_build_v24.py", BUILD_SOURCE_SHA, 107319, 431807),
    ("c24_protocol", "oracle/phase2/C-COMPLETE-SEMANTIC-SOURCE-BUILD-V24.md", BUILD_PROTOCOL_SHA, 18367, 526621),
    ("c24_contract", "oracle/phase2/c-complete-semantic-source-build-v24.json", BUILD_CONTRACT_SHA, 19394, 526623),
    ("c24_build_receipt", "oracle/phase2/evidence/native-source-build-v24-c-phase2-v24-c-complete-semantics-publication-receipt.json", BUILD_RECEIPT_SHA, 14172, 526667),
    ("c24_root_receipt", "oracle/phase2/evidence/native-source-build-v24-c-phase2-v24-c-complete-semantics-root-provenance-receipt.json", ROOT_RECEIPT_SHA, 12573, 526668),
    ("c16_source", "tools/run_owned_repaired_c_original_campaign_v16.py", ORIGINAL_SOURCE_SHA, 155961, 431851),
    ("c16_protocol", "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V16.md", ORIGINAL_PROTOCOL_SHA, 17699, 526686),
    ("c16_contract", "oracle/phase2/repaired-c-original-campaign-v16.json", ORIGINAL_CONTRACT_SHA, 102081, 526688),
    ("c16_pass", "oracle/phase2/evidence/repaired-c-original-campaign-v16-c-phase2-v24-c-final-public-semantics-original-p0-v16-results-publication-receipt.json", ORIGINAL_PASS_SHA, 10657, 525275),
    ("guard_source", "tools/verify_owned_candidate_runtime_independence_v4.py", GUARD_SOURCE_SHA, 48687, 429243),
    ("guard_protocol", "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md", GUARD_PROTOCOL_SHA, 4492, 525890),
    ("guard_contract", "oracle/phase2/candidate-runtime-independence-v4.json", GUARD_CONTRACT_SHA, 9352, 525891),
    ("repair_source", "tools/apply_owned_c_final_public_semantics_v1.py", "028899a11fa051c80651a27f2b0365512e4821f6509634223599c4a523e72c5b", 63777, 431679),
    ("repair_protocol", "oracle/phase2/C-FINAL-PUBLIC-SEMANTICS-V1.md", "69da3db828b1ef8cf8fd6885031cf485540db6321e86b5691b96ecae33a9b2b5", 8153, 526554),
    ("repair_contract", "oracle/phase2/c-final-public-semantics-v1.json", "e31ce572d791a11db8cb6224b3cff4e17f3ae0b5f5cc0b8ae271d96d4bb2aa6b", 4825, 526555),
    ("repair_application", "oracle/phase2/evidence/c-final-public-semantics-v1-application.json", "3b45b8cf24d829221f36f311e7cc3852f42b0b73840a4952d7e5b7441c625ace", 1303, 526587),
    ("zig_v2_source", "tools/run_owned_zig_full_public_correctness_v2.py", "4eb351a11383df97d5f6b5f1f242e988a685992bafbaa87ee89e67fa1dcb0f3c", 77198, 431854),
    ("zig_v2_protocol", "oracle/phase2/ZIG-FULL-PUBLIC-CORRECTNESS-V2.md", "047cf9ff200f7c0423419230aa63ce0c2f3479361f70dd85c354612192b07abd", 5125, 526706),
    ("zig_v2_contract", "oracle/phase2/zig-full-public-correctness-v2.json", "48f59c6a10412cb250b1995e1a37033aa73fc99aa2689117b01b8a2d07f5453c", 14898, 526707),
    ("zig_v2_guard_failure", "oracle/phase2/evidence/zig-full-public-correctness-v2-v17-zig-public-v2-run-001-guard-failure.json", "4466d9be63f9c480ac24de1d42b13524c1a4f82dba4d543779014605dcd74aa3", 1533, 526724),
)


class PublicError(Exception):
    """Reject substituted public owners or unauthorized genuine execution."""


def need(value: object, reason: str) -> None:
    if value is not True:
        raise PublicError(reason)


def digest(payload: bytes) -> str:
    need(type(payload) is bytes, "hash only complete immutable bytes")
    return hashlib.sha256(payload).hexdigest()


def sha(value: object, name: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(item in "0123456789abcdef" for item in value),
         "require an independently pinned lowercase SHA-256: " + name)
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
         "source-only gate imported a matcher, candidate, loader, or worker")


class PublicWall:
    """Permanently restrict source gates to explicitly pinned public text."""

    def __init__(self) -> None:
        relatives = (SOURCE, PROTOCOL, CONTRACT,
                     *(row[1] for row in PUBLIC_OWNERS))
        self.allowed = frozenset(ROOT + "/" + value for value in relatives)
        need(all((item.startswith(ROOT + "/tools/")
                  or item.startswith(ROOT + "/oracle/phase2/"))
                 and not item.endswith((".gz", ".so", ".zip", ".tar"))
                 and "/candidates/" not in item
                 and not any(word in item.lower()
                             for word in ("holdout", "hidden", "sealed", "proposal"))
                 for item in self.allowed),
             "exclude private roots, candidates, archives, and hidden proposals")
        self.live: set[int] = set()
        self.blocked: dict[str, int] = {}
        self.installed = False
        self.raw_open, self.raw_read = os.open, os.read
        self.raw_fstat, self.raw_close = os.fstat, os.close

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise PublicError("full C public V1 source wall rejected " + category)

    def approved(self, path: object) -> bool:
        return (type(path) is str and path in self.allowed
                and path.startswith(ROOT + "/")
                and path == os.path.normpath(path)
                and not any(part in (".", "..") for part in path.split("/"))
                and not path.endswith((".gz", ".so", ".zip", ".tar"))
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
        need(self.installed is False, "install the irreversible C source wall once")
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
    need(type(role) is str and type(relative) is str
         and not relative.startswith("/") and ".." not in relative.split("/")
         and type(size) is int and 0 < size <= MAX_OWNER_BYTES
         and type(inode) is int and inode > 0,
         "reject an unsafe or partial public C owner")
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
        need(os.read(descriptor, 1) == b"", "reject expanded public plaintext")
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
    need(relative in (SOURCE, PROTOCOL, CONTRACT),
         "reject invented dynamic candidate or private owner")
    absolute = ROOT + "/" + relative
    need(wall is None or wall.installed and wall.approved(absolute),
         "install the wall before authenticating a live public owner")
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
         "authenticate the immutable V3 public worker kernel before execution")
    module = types.ModuleType("_rebar_c_v1_authenticated_public_gate_v3")
    module.__file__ = ROOT + "/" + row[1]
    exec(compile(payload, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    need(module.SCHEMA == "rebar-owned-rust-native-architecture-public-gate-v3"
         and module.PUBLIC_CORRECTNESS_CASES == CASE_COUNT
         and module.PUBLIC_CORRECTNESS_MATRIX == MATRIX_SHA
         and module.PUBLIC_CORRECTNESS_SEED == PUBLISHED_SEED
         and callable(module.json_object) and callable(module.document)
         and callable(module.run_worker) and callable(module.snapshot_canonical),
         "retain the independently authenticated complete public worker kernel")
    return module


def parse_json(module: types.ModuleType, payload: bytes, label: str) -> dict:
    result = module.json_object(payload, label)
    need(type(result) is dict,
         "require one complete duplicate-free public JSON document: " + label)
    return result


def public_operations(payload: bytes) -> tuple[str, ...]:
    tree = ast.parse(payload,
                     filename=ROOT + "/tools/rust_public_practice_benchmark_v2.py")
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
         "authenticate every original frozen public operation")
    return values[0]


def c_harness(payload: bytes) -> bytes:
    need(digest(payload) == PUBLIC_HARNESS_SHA,
         "authenticate the complete unchanged public 111-operation harness")
    edits = (
        (b"candidates.rust_candidate", b"candidates.vm_candidate", 2),
        (b"rust_candidate.py", b"vm_candidate.py", 1),
        (b"candidates._rust_bridge", b"candidates._vm_native", 4),
        (b"    verify_pinned_runtime()\n    reject_external_regex_packages()",
         b'    verify_pinned_runtime(permit_candidate=(name == "rust"))\n'
         b"    reject_external_regex_packages()", 1),
    )
    result = payload
    for old, new, expected in edits:
        need(result.count(old) == expected,
             "preserve each frozen C-only public harness adapter anchor")
        result = result.replace(old, new)
    need(len(result) == C_HARNESS_BYTES and digest(result) == C_HARNESS_SHA
         and b"candidates.rust_candidate" not in result
         and b"candidates._rust_bridge" not in result,
         "reject changed operations, candidate identity, or C harness transform")
    need(public_operations(result) == public_operations(payload),
         "never alter a public operation, dataset, weight, outcome, or case")
    return result


def validate_history(module: types.ModuleType,
                     payloads: dict[str, bytes]) -> dict:
    rows = {entry[0]: entry for entry in PUBLIC_OWNERS}
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
         "preserve the immutable complete public 10,434-case oracle")

    rust = parse_json(module, payloads["rust_v5_contract"],
                      "immutable complete Rust V5 public source freeze")
    rust_public = rust.get("public_correctness")
    need(rust.get("schema")
         == "rebar-owned-rust-full-public-correctness-v5-source-freeze"
         and rust.get("version") == 5 and type(rust_public) is dict
         and rust.get("source", {}).get("sha256") == rows["rust_v5_source"][2]
         and rust.get("protocol", {}).get("sha256") == rows["rust_v5_protocol"][2]
         and rust_public.get("case_count") == CASE_COUNT
         and rust_public.get("dataset_count") == DATASET_COUNT
         and rust_public.get("operation_count") == OPERATIONS_PER_DATASET
         and rust_public.get("str_case_count") == DOMAIN_CASE_COUNT
         and rust_public.get("bytes_case_count") == DOMAIN_CASE_COUNT
         and rust_public.get("matrix_sha256") == MATRIX_SHA
         and rust_public.get("published_seed") == PUBLISHED_SEED
         and rust_public.get("harness_source_sha256") == PUBLIC_HARNESS_SHA
         and rust_public.get("all_cases_execute_even_on_failure") is True
         and rust_public.get("all_mismatches_retained") is True,
         "never substitute or weaken immutable V5 public matrix semantics")
    operations = public_operations(payloads["public_harness"])
    need(tuple(rust_public.get("operations", [])) == operations,
         "preserve every exact source-defined V5 public API operation")
    rust_pass = parse_json(module, payloads["rust_v5_pass"],
                           "actual genuine complete Rust V5 public PASS")
    need(rust_pass.get("schema")
         == "rebar-owned-rust-full-public-correctness-v5-durable-publication-receipt"
         and rust_pass.get("status") == "PASS"
         and rust_pass.get("candidate_status") == "PASS"
         and rust_pass.get("public_10434_case_count") == CASE_COUNT
         and rust_pass.get("public_10434_verified_passing_case_count") == CASE_COUNT
         and rust_pass.get("public_10434_mismatch_count") == 0
         and rust_pass.get("public_api_operation_count") == OPERATIONS_PER_DATASET
         and rust_pass.get("matrix_sha256") == MATRIX_SHA
         and rust_pass.get("published_seed") == PUBLISHED_SEED
         and rust_pass.get("candidate_qualified") is False,
         "preserve the genuine immutable 10,434-case Rust V5 PASS")

    original = parse_json(module, payloads["c16_contract"],
                          "exact independently frozen C16 full-original contract")
    c24_freeze = parse_json(module, payloads["c24_contract"],
                            "exact independently frozen dual C24 source build")
    build = parse_json(module, payloads["c24_build_receipt"],
                       "actual genuine independent dual C24 public build")
    root = parse_json(module, payloads["c24_root_receipt"],
                      "actual genuine independent dual C24 private-root receipt")
    actual_original = parse_json(module, payloads["c16_pass"],
                                 "actual complete 31,237-case C16 original PASS")
    published = original.get("actual_published_dual_c24_source_build")
    guard_entry = original.get("strict_runtime_guard_v4")
    recovery = original.get("crash_journaled_dual_canonical_activation")
    need(original.get("schema")
         == "rebar-owned-repaired-c-original-campaign-v16-source-freeze"
         and original.get("version") == 16
         and original.get("source", {}).get("sha256") == ORIGINAL_SOURCE_SHA
         and original.get("protocol", {}).get("sha256") == ORIGINAL_PROTOCOL_SHA
         and type(published) is dict
         and published.get("actual_compiler_process_count") == 14
         and published.get("independent_source_phase_count") == 2
         and published.get("distinct_native_artifact_count") == 2
         and published.get("corrected_adapter_source_sha256") == ADAPTER_SHA
         and published.get("corrected_adapter_source_bytes") == ADAPTER_BYTES
         and published.get("corrected_native_source_sha256") == NATIVE_SOURCE_SHA
         and published.get("corrected_native_source_bytes") == NATIVE_SOURCE_BYTES
         and published.get("native_artifact_sha256") == NATIVE_SHA
         and published.get("native_artifact_bytes") == NATIVE_BYTES
         and type(guard_entry) is dict and guard_entry.get("version") == 4
         and type(recovery) is dict
         and recovery.get("durable_journal_before_first_mutation") is True
         and recovery.get("publication_after_exact_dual_restoration_only") is True,
         "bind the complete authentic C16 V4 dual-owner activation source")
    need(actual_original.get("schema")
         == "rebar-owned-repaired-c-original-campaign-v16-durable-publication-receipt"
         and actual_original.get("status") == "PASS"
         and actual_original.get("publication_status") == "PASS"
         and actual_original.get("candidate_status") == "PASS"
         and actual_original.get("family") == "c"
         and actual_original.get("source_sha256") == ORIGINAL_SOURCE_SHA
         and actual_original.get("protocol_sha256") == ORIGINAL_PROTOCOL_SHA
         and actual_original.get("contract_sha256") == ORIGINAL_CONTRACT_SHA
         and actual_original.get("case_execution_denominator") == 31237
         and actual_original.get("verified_passing_case_count") == 31237
         and actual_original.get("semantic_mismatch_count") == 0
         and actual_original.get("suite_count") == 13
         and actual_original.get("attempted_suite_count") == 13
         and actual_original.get("completed_suite_count") == 13
         and actual_original.get("actual_candidate_workers") == 13
         and actual_original.get("candidate_execution_failure_count") == 0
         and actual_original.get("infrastructure_failure_count") == 0
         and actual_original.get("native_engine_sha256") == NATIVE_SHA
         and actual_original.get("native_bridge_sha256") == NATIVE_SHA
         and actual_original.get("corrected_source_sha256") == NATIVE_SOURCE_SHA
         and actual_original.get("unchanged_adapter_sha256") == ADAPTER_SHA
         and actual_original.get("actual_c21_build_receipt_sha256") == BUILD_RECEIPT_SHA
         and actual_original.get("actual_c21_root_receipt_sha256") == ROOT_RECEIPT_SHA
         and actual_original.get("original_native_inode_restored") is True
         and actual_original.get("all_observed_semantic_mismatch_records_preserved") is True
         and actual_original.get("candidate_qualified") is False,
         "require the same exact dual C24 native+adapter actual 31,237-case PASS")
    suites = actual_original.get("suite_outcomes")
    need(type(suites) is list and len(suites) == 13
         and sum(row.get("case_execution_denominator", 0) for row in suites) == 31237
         and all(row.get("status") == "PASS"
                 and row.get("mismatch_count") == 0
                 and row.get("actual_candidate_workers") == 1 for row in suites),
         "preserve all 13 genuine independent original-suite PASS outcomes")

    need(c24_freeze.get("schema")
         == "rebar-owned-c-complete-semantic-source-build-v24-source-freeze"
         and c24_freeze.get("version") == 24
         and c24_freeze.get("source", {}).get("sha256") == BUILD_SOURCE_SHA
         and c24_freeze.get("protocol", {}).get("sha256") == BUILD_PROTOCOL_SHA,
         "preserve the exact independently frozen first-party C24 source build")
    for actual, suffix in ((build, "-durable-publication-receipt"),
                           (root, "-durable-root-provenance-receipt")):
        need(actual.get("schema")
             == "rebar-owned-c-complete-semantic-source-build-v24" + suffix
             and actual.get("status") == "PASS"
             and actual.get("version") == 24
             and actual.get("family") == "c"
             and actual.get("source_sha256") == BUILD_SOURCE_SHA
             and actual.get("protocol_sha256") == BUILD_PROTOCOL_SHA
             and actual.get("contract_sha256") == BUILD_CONTRACT_SHA
             and actual.get("actual_compiler_process_count") == 14
             and actual.get("expected_compiler_process_count") == 14
             and actual.get("native_artifact_sha256") == NATIVE_SHA
             and actual.get("native_artifact_bytes") == NATIVE_BYTES
             and actual.get("corrected_native_source_sha256") == NATIVE_SOURCE_SHA
             and actual.get("corrected_adapter_source_sha256") == ADAPTER_SHA
             and actual.get("candidate_workers_started") == 0
             and actual.get("native_libraries_loaded") == 0,
             "reject substituted or incompletely built exact dual C24 provenance")
    private = root.get("root")
    need(root.get("canonical_build_receipt_sha256") == BUILD_RECEIPT_SHA
         and type(private) is dict and private.get("path") == PRIVATE_ROOT
         and private.get("device") == PRIVATE_DEVICE
         and private.get("inode") == PRIVATE_ROOT_INODE
         and private.get("mode") == "0700"
         and private.get("phase_count") == 2,
         "attest the authentic C24 private root only from published metadata")
    phases = private.get("phases")
    need(type(phases) is list and len(phases) == 2,
         "preserve both genuine independent C24 source-build phases")
    native_ids, source_ids = set(), set()
    for index, phase in enumerate(phases):
        need(type(phase) is dict
             and phase.get("name") == ("reference-a", "reference-b")[index]
             and phase.get("device") == PRIVATE_DEVICE
             and phase.get("mode") == "0700",
             "reject reordered, omitted, or substituted private C24 phases")
        native = phase.get("native_output")
        need(type(native) is dict and native.get("sha256") == NATIVE_SHA
             and native.get("bytes") == NATIVE_BYTES
             and native.get("device") == PRIVATE_DEVICE
             and native.get("nlink") == 1
             and native.get("native_loaded") is False,
             "reject a substituted independent phase C24 native artifact")
        identity = (native["device"], native["inode"])
        need(identity not in native_ids,
             "require two distinct independently built C24 native artifacts")
        native_ids.add(identity)
        owners = phase.get("source_owners")
        need(type(owners) is list and len(owners) == 2,
             "require the exact independent native and adapter source owners")
        for owner, fingerprint, count in (
                (owners[0], NATIVE_SOURCE_SHA, NATIVE_SOURCE_BYTES),
                (owners[1], ADAPTER_SHA, ADAPTER_BYTES)):
            need(type(owner) is dict and owner.get("sha256") == fingerprint
                 and owner.get("bytes") == count
                 and owner.get("device") == PRIVATE_DEVICE
                 and owner.get("mode") == "0600" and owner.get("nlink") == 1,
                 "reject a substituted independent exact C24 source owner")
            identity = (owner["device"], owner["inode"])
            need(identity not in source_ids,
                 "never count a duplicated source inode as an independent phase")
            source_ids.add(identity)
    need(len(native_ids) == 2 and len(source_ids) == 4,
         "preserve all independently materialized C24 source/native identities")

    guard = parse_json(module, payloads["guard_contract"],
                       "immutable authenticated strict V4 runtime guard")
    need(guard.get("schema")
         == "rebar-owned-candidate-runtime-independence-v4-source-freeze"
         and guard.get("version") == 4
         and guard.get("source", {}).get("sha256") == GUARD_SOURCE_SHA
         and guard.get("protocol", {}).get("sha256") == GUARD_PROTOCOL_SHA
         and guard.get("runtime_non_delegation") == "NOT ESTABLISHED"
         and guard.get("qualified_candidate_count") == 0,
         "preserve the exact V4 policy without falsely claiming qualification")
    application = parse_json(module, payloads["repair_application"],
                             "actual final first-party native+adapter application")
    created = application.get("created")
    need(application.get("schema")
         == "rebar-owned-c-final-public-semantics-v1-recorded-application"
         and application.get("status") == "APPLIED"
         and application.get("source_sha256") == rows["repair_source"][2]
         and application.get("protocol_sha256") == rows["repair_protocol"][2]
         and application.get("contract_sha256") == rows["repair_contract"][2]
         and application.get("historical_mismatches_targeted") == 224
         and type(created) is dict
         and created.get("adapter", {}).get("sha256") == ADAPTER_SHA
         and created.get("adapter", {}).get("bytes") == ADAPTER_BYTES
         and created.get("adapter", {}).get("inode") == 526585
         and created.get("native", {}).get("sha256") == NATIVE_SOURCE_SHA
         and created.get("native", {}).get("bytes") == NATIVE_SOURCE_BYTES
         and created.get("native", {}).get("inode") == 526586
         and application.get("winner_selected") is False,
         "preserve exact final first-party C native and adapter materialization")

    zig_freeze = parse_json(module, payloads["zig_v2_contract"],
                            "published immutable Zig V2 wider-public design")
    zig_failure = parse_json(module, payloads["zig_v2_guard_failure"],
                             "genuine Zig V2 guard-identity failure")
    need(zig_freeze.get("schema")
         == "rebar-owned-zig-full-public-correctness-v2-source-freeze"
         and zig_freeze.get("version") == 2
         and zig_freeze.get("public_correctness", {}).get("case_count") == CASE_COUNT
         and zig_failure.get("schema")
             == "rebar-owned-zig-full-public-correctness-v2-guard-failure"
         and zig_failure.get("status") == "FAIL"
         and zig_failure.get("candidate_family") == "zig"
         and zig_failure.get("error_type") == "PublicError"
         and "require genuine installed V4 before complete Zig candidate execution"
             in zig_failure.get("error_message", ""),
         "preserve and explicitly avoid the genuine Zig V2 outer guard mismatch")
    return {"operations": operations, "kernel": kernel, "rust": rust,
            "rust_pass": rust_pass, "original": original,
            "original_pass": actual_original, "c24_freeze": c24_freeze,
            "build": build, "root": root, "guard": guard,
            "application": application,
            "adapted_harness": c_harness(payloads["public_harness"]),
            "zig_guard_failure": zig_failure}


def contract_document(rows: dict[str, tuple], history: dict) -> dict:
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "status": "SOURCE FROZEN; EXACT ORIGINAL-PASS C24 BUILD; PUBLIC CORRECTNESS NOT RUN",
        "source": pin(rows["source"]),
        "protocol": pin(rows["protocol"]),
        "authenticated_public_owners": [pin(item) for item in PUBLIC_OWNERS],
        "preserved_rust_v5_public_oracle": {
            "source_sha256": PUBLIC_OWNERS[0][2],
            "protocol_sha256": PUBLIC_OWNERS[1][2],
            "contract_sha256": PUBLIC_OWNERS[2][2],
            "actual_pass_receipt_sha256": PUBLIC_OWNERS[3][2],
            "actual_verified_passing_case_count": CASE_COUNT,
            "actual_mismatch_count": 0,
        },
        "original_correctness": {
            "source_sha256": ORIGINAL_SOURCE_SHA,
            "protocol_sha256": ORIGINAL_PROTOCOL_SHA,
            "contract_sha256": ORIGINAL_CONTRACT_SHA,
            "actual_pass_receipt_sha256": ORIGINAL_PASS_SHA,
            "case_execution_denominator": 31237,
            "verified_passing_case_count": 31237,
            "semantic_mismatch_count": 0,
            "independent_worker_count": 13,
            "all_original_categories_completed": 13,
            "candidate_status": "PASS",
            "candidate_qualified": False,
        },
        "public_correctness": {
            "case_count": CASE_COUNT,
            "dataset_count": DATASET_COUNT,
            "str_case_count": DOMAIN_CASE_COUNT,
            "bytes_case_count": DOMAIN_CASE_COUNT,
            "operation_count": OPERATIONS_PER_DATASET,
            "operations_per_dataset": OPERATIONS_PER_DATASET,
            "operations": list(history["operations"]),
            "published_seed": PUBLISHED_SEED,
            "matrix_sha256": MATRIX_SHA,
            "harness_source_sha256": PUBLIC_HARNESS_SHA,
            "first_party_c_adapter_transform_sha256": C_HARNESS_SHA,
            "first_party_c_adapter_transform_bytes": C_HARNESS_BYTES,
            "all_cases_execute_even_on_failure": True,
            "all_mismatches_retained": True,
            "all_nested_error_records_retained": True,
            "reference_and_candidate_isolated_processes": True,
            "reference_worker_count": 1,
            "candidate_worker_count": 1,
            "candidate_runtime_guard_version": 4,
            "candidate_guard_installed_before_import": True,
            "candidate_policy_identity_checked_directly": True,
            "zig_v2_outer_result_guard_identity_mismatch_repeated": False,
            "timing_trials_run": 0,
        },
        "actual_independent_c24_build": {
            "source_sha256": BUILD_SOURCE_SHA,
            "protocol_sha256": BUILD_PROTOCOL_SHA,
            "contract_sha256": BUILD_CONTRACT_SHA,
            "build_receipt_sha256": BUILD_RECEIPT_SHA,
            "private_root_receipt_sha256": ROOT_RECEIPT_SHA,
            "actual_compiler_process_count": 14,
            "independent_build_phase_count": 2,
            "distinct_phase_source_owner_count": 4,
            "distinct_native_artifact_count": 2,
            "private_root": {"path": PRIVATE_ROOT, "device": PRIVATE_DEVICE,
                             "inode": PRIVATE_ROOT_INODE},
            "adapter": {"sha256": ADAPTER_SHA, "bytes": ADAPTER_BYTES},
            "native_source": {"sha256": NATIVE_SOURCE_SHA,
                              "bytes": NATIVE_SOURCE_BYTES},
            "native_engine": {"sha256": NATIVE_SHA, "bytes": NATIVE_BYTES},
            "native_bridge": {"sha256": NATIVE_SHA, "bytes": NATIVE_BYTES},
        },
        "strict_runtime_guard_v4": {
            "source_sha256": GUARD_SOURCE_SHA,
            "protocol_sha256": GUARD_PROTOCOL_SHA,
            "contract_sha256": GUARD_CONTRACT_SHA,
            "installed_in_candidate_process_before_candidate_import": True,
            "authenticated_c16_installer_identity_required": True,
            "live_policy_and_selected_module_identity_checked": True,
            "invented_outer_worker_metadata_required": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "crash_journaled_dual_canonical_activation": {
            "canonical_adapter_relative": "candidates/vm_candidate.py",
            "canonical_native_relative":
                "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
            "original_adapter_sha256": ORIGINAL_ADAPTER_SHA,
            "original_adapter_bytes": ORIGINAL_ADAPTER_BYTES,
            "original_adapter_inode": ORIGINAL_ADAPTER_INODE,
            "original_native_sha256": ORIGINAL_NATIVE_SHA,
            "original_native_bytes": ORIGINAL_NATIVE_BYTES,
            "original_native_inode": ORIGINAL_NATIVE_INODE,
            "corrected_adapter_sha256": ADAPTER_SHA,
            "corrected_native_sha256": NATIVE_SHA,
            "fresh_session_specific_recovery_prefix": RECOVERY_PREFIX,
            "durable_journal_before_first_mutation": True,
            "same_directory_original_inode_hard_links": True,
            "exact_original_adapter_inode_restored_before_publication": True,
            "exact_original_native_inode_restored_before_publication": True,
            "public_artifacts_created_only_after_both_restorations": True,
        },
        "preserved_zig_v2_guard_failure": {
            "source_sha256": PUBLIC_OWNERS[-4][2],
            "protocol_sha256": PUBLIC_OWNERS[-3][2],
            "contract_sha256": PUBLIC_OWNERS[-2][2],
            "guard_failure_receipt_sha256": PUBLIC_OWNERS[-1][2],
            "failure_status": "FAIL",
            "failure_type": "PublicError",
            "failure_repeated": False,
            "repair": "AUTHENTIC C16 STRICT-V4 POLICY OBJECT VERIFIED DIRECTLY",
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
            "workspace_mutations": 0,
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
    rows = {"source": live_owner(wall, "source", SOURCE,
                                  options["source_sha256"]),
            "protocol": live_owner(wall, "protocol", PROTOCOL,
                                    options["protocol_sha256"])}
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
        observed = parse_json(module, actual,
                              "complete independently frozen full-public C contract")
        need(observed == freeze and actual == module.document(freeze),
             "reject omitted, reordered, or weakened complete public C obligations")
    sterile_modules()
    return {"rows": rows, "payloads": payloads, "module": module,
            "history": history, "freeze": freeze}


def rejected(wall: PublicWall, label: str, callback) -> str:
    before = sum(wall.blocked.values())
    try:
        callback()
    except (PublicError, OSError, ValueError, TypeError, AttributeError):
        need(sum(wall.blocked.values()) > before,
             "hostile control missed the irreversible physical wall: " + label)
        return label
    raise PublicError("hostile public source control escaped: " + label)


def recovery_path(session: object) -> str:
    need(type(session) is str and 1 <= len(session) <= 72
         and session.startswith("v24-c-public-v1-")
         and all(character in "abcdefghijklmnopqrstuvwxyz0123456789-"
                 for character in session)
         and not any(word in session for word in
                     ("holdout", "hidden", "sealed", "proposal")),
         "reject an unsafe or non-public C16 dual-recovery session")
    answer = RECOVERY_PREFIX + session
    need(os.path.dirname(answer) == "/tmp"
         and answer.startswith(RECOVERY_PREFIX)
         and "/../" not in answer and answer != RECOVERY_PREFIX,
         "retain a fresh bounded case-specific genuine C16 recovery directory")
    return answer


def self_test(wall: PublicWall, _state: dict) -> dict:
    source = ROOT + "/" + SOURCE
    hidden = ROOT + "/oracle/phase3/final-held-out-cases.json"
    controls = [
        rejected(wall, "builtins-open", lambda: builtins.open(source, "rb")),
        rejected(wall, "io-open", lambda: io.open(source, "rb")),
        rejected(wall, "_io-open", lambda: _io.open(source, "rb")),
        rejected(wall, "canonical-adapter", lambda: os.open(
            ROOT + "/candidates/vm_candidate.py", os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "canonical-native", lambda: os.open(
            ROOT + "/candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
            os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "private-native", lambda: os.open(
            PRIVATE_ROOT + "/reference-a/_vm_native.cpython-314-x86_64-linux-gnu.so",
            os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "private-root-metadata", lambda: os.stat(PRIVATE_ROOT)),
        rejected(wall, "holdout-content", lambda: os.open(hidden, os.O_RDONLY)),
        rejected(wall, "holdout-metadata", lambda: os.stat(hidden)),
        rejected(wall, "compressed-archive", lambda: os.open(
            ROOT + "/oracle/phase2/evidence/private.json.gz",
            os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "proposal-content", lambda: os.open(
            ROOT + "/oracle/phase3/holdout-proposal.json",
            os.O_RDONLY | os.O_NOFOLLOW)),
        rejected(wall, "workspace-write", lambda: os.open(
            source, os.O_WRONLY | os.O_TRUNC | os.O_NOFOLLOW)),
        rejected(wall, "mkdir", lambda: os.mkdir(ROOT + "/unsafe")),
        rejected(wall, "worker", lambda: os.system("true")),
        rejected(wall, "clock", lambda: time.perf_counter()),
        rejected(wall, "metadata", lambda: os.lstat(source)),
        rejected(wall, "foreign-read", lambda: os.read(0, 1)),
        rejected(wall, "foreign-fstat", lambda: os.fstat(0)),
        rejected(wall, "foreign-close", lambda: os.close(0)),
        rejected(wall, "foreign-write", lambda: os.write(1, b"x")),
    ]
    valid = "v24-c-public-v1-source-only-control"
    need(recovery_path(valid) == RECOVERY_PREFIX + valid,
         "retain bounded fresh exact C16 dual-owner recovery path")
    rejected_sessions = 0
    for invalid in ("", "v24-c-public-v0-old", "v24-c-public-v1-../x",
                    "v24-c-public-v1-hidden", "v24-c-public-v1-UPPER",
                    "v24-c-public-v1-a/b", None, 7):
        try:
            recovery_path(invalid)
        except PublicError:
            rejected_sessions += 1
        else:
            raise PublicError("unsafe C16 recovery session unexpectedly accepted")
    need(not wall.live and len(controls) >= 20,
         "close all authenticated public descriptors and retain hostile controls")
    return {"schema": SCHEMA + "-source-only-gate", "status": "PASS",
            "mode": "self-test", "hostile_control_count": len(controls),
            "hostile_controls": controls,
            "authenticated_public_owner_count": len(PUBLIC_OWNERS),
            "public_case_count": CASE_COUNT,
            "public_api_operation_count": OPERATIONS_PER_DATASET,
            "c_original_case_count": 31237,
            "c_original_verified_passing_case_count": 31237,
            "c_original_mismatch_count": 0,
            "candidate_source_files_opened": 0,
            "private_roots_opened": 0,
            "archives_opened": 0,
            "hidden_cases_read": 0,
            "candidate_workers_started": 0,
            "clock_samples": 0,
            "unsafe_recovery_sessions_rejected": rejected_sessions,
            "recovery_directories_created": 0,
            "canonical_candidate_sources_modified": 0,
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "candidate_qualified": False,
            "winner_selected": False}


def verify_summary(wall: PublicWall, _state: dict) -> dict:
    need(not wall.live,
         "close each authenticated complete public source-only descriptor")
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
            "c_original_case_count": 31237,
            "c_original_verified_passing_case_count": 31237,
            "c_original_mismatch_count": 0,
            "c_native_sha256": NATIVE_SHA,
            "c_adapter_sha256": ADAPTER_SHA,
            "strict_runtime_guard_version": 4,
            "candidate_source_files_opened": 0,
            "private_roots_opened": 0,
            "archives_opened": 0,
            "hidden_cases_read": 0,
            "candidate_workers_started": 0,
            "clock_samples": 0,
            "canonical_candidate_sources_modified": 0,
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
    need(output_eligible(path, payload),
         "reject unrelated or nonexclusive full-public C evidence")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | os.O_CLOEXEC | os.O_NOFOLLOW, mode)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            need(type(written) is int and written > 0,
                 "reject incomplete durable public evidence")
            view = view[written:]
        os.fsync(descriptor)
        info = os.fstat(descriptor)
        need(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == mode
             and info.st_nlink == 1 and info.st_size == len(payload),
             "reject substituted full-public C correctness evidence")
        parent = os.open(os.path.dirname(path), os.O_RDONLY | os.O_DIRECTORY
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
        return {"path": path, "sha256": digest(payload), "bytes": len(payload),
                "device": info.st_dev, "inode": info.st_ino,
                "mode": format(mode, "04o"), "exclusive_creation": True,
                "file_fsync_completed": True,
                "directory_fsync_completed": True}
    finally:
        os.close(descriptor)


ACTUAL_PINNED = {
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
    "native_source_sha256": NATIVE_SOURCE_SHA,
    "native_source_bytes": str(NATIVE_SOURCE_BYTES),
    "native_engine_sha256": NATIVE_SHA,
    "native_engine_bytes": str(NATIVE_BYTES),
    "native_bridge_sha256": NATIVE_SHA,
    "native_bridge_bytes": str(NATIVE_BYTES),
    "private_root": PRIVATE_ROOT,
    "private_root_device": str(PRIVATE_DEVICE),
    "private_root_inode": str(PRIVATE_ROOT_INODE),
    "original_adapter_sha256": ORIGINAL_ADAPTER_SHA,
    "original_adapter_inode": str(ORIGINAL_ADAPTER_INODE),
    "original_native_sha256": ORIGINAL_NATIVE_SHA,
    "original_native_inode": str(ORIGINAL_NATIVE_INODE),
    "public_harness_sha256": PUBLIC_HARNESS_SHA,
    "c_harness_sha256": C_HARNESS_SHA,
}


def actual_authority(options: dict) -> None:
    need(options.get("root_authorized") is True
         and options.get("frozen_committed_pushed") is True
         and commit(options.get("frozen_commit"), "frozen C public V1 commit")
             == commit(options.get("pushed_commit"), "pushed C public V1 commit"),
         "require the exact already committed and pushed root-authorized freeze")
    for name, expected in ACTUAL_PINNED.items():
        need(options.get(name) == expected,
             "require root-pinned exact independently built C owner: " + name)
    recovery_path(options.get("session"))


def c16_runtime(state: dict, *, mode: str,
                session: str, native_inode: int | None = None,
                journal_sha: str | None = None) -> tuple:
    row = next(item for item in PUBLIC_OWNERS if item[0] == "c16_source")
    c16 = types.ModuleType("_rebar_c_public_v1_exact_c16_runtime")
    c16.__file__ = ROOT + "/" + row[1]
    c16.__package__ = ""
    exec(compile(state["payloads"]["c16_source"], c16.__file__, "exec",
                 dont_inherit=True), c16.__dict__)
    need(c16.SOURCE == row[1] and c16.SCHEMA
         == "rebar-owned-repaired-c-original-campaign-v16"
         and c16.C24_BUILD[0][1] == BUILD_SOURCE_SHA
         and c16.C24_PUBLIC_RECEIPT[1] == BUILD_RECEIPT_SHA
         and c16.C24_ROOT_RECEIPT[1] == ROOT_RECEIPT_SHA
         and c16.CORRECTED_ADAPTER_SHA256 == ADAPTER_SHA
         and c16.C24_NATIVE_SHA256 == NATIVE_SHA
         and c16.V4_GUARD[0][1] == GUARD_SOURCE_SHA,
         "reject substituted genuine C16 dual-owner/V4 activation controller")
    campaign, outer_transform = c16.bootstrap_v11()
    historical, middle_transform = campaign.bootstrap_v9()
    history, inner_transform = historical.historical_controller()
    original, prior_transform = history.bootstrap_historical()
    history.install_corrections(original, prior_transform)
    historical.install_c21(history, original, inner_transform)
    campaign.install_v11(historical, history, original, middle_transform)
    c16.install_v16(campaign, history, original, outer_transform)
    previous = original.bootstrap_v6()
    old, original_contract = original.configure_previous(previous)
    arguments = [mode, "--source-sha256", ORIGINAL_SOURCE_SHA,
                 "--protocol-sha256", ORIGINAL_PROTOCOL_SHA,
                 "--contract-sha256", ORIGINAL_CONTRACT_SHA]
    for name, value in previous.actual_authority().items():
        arguments.extend(("--" + name.replace("_", "-"), value))
    if mode == "--worker":
        need(type(native_inode) is int and native_inode > 0
             and type(journal_sha) is str,
             "independently bind the authentic promoted C24 native journal")
        arguments.extend(("--suite", "public_v3",
                          "--activation-inode", str(native_inode),
                          "--recovery-journal-sha256",
                          sha(journal_sha, "actual C16 native journal")))
    parsed = original.options(arguments, previous)
    previous.contract_document = (
        lambda selected, frozen, live_state: original.contract_document(
            selected, frozen, live_state, previous, original_contract,
        )
    )
    producer, live_state, _ = previous.collect_context(old, parsed)
    previous.RECOVERY_ROOT = recovery_path(session)
    need(live_state["c24"]["build"]["native_artifact_sha256"] == NATIVE_SHA
         and live_state["c24"]["root"]["canonical_build_receipt_sha256"]
             == BUILD_RECEIPT_SHA
         and live_state["c24_guard_contract"]["version"] == 4,
         "preserve the fully authenticated exact C24/C16 strict-V4 context")
    return c16, previous, producer, live_state, parsed


def isolated_candidate(options: dict, state: dict) -> dict:
    actual_authority(options)
    inode = options.get("activation_inode")
    need(type(inode) is str and inode.isdigit() and int(inode) > 0,
         "require one genuine promoted canonical C24 native inode")
    c16, previous, producer, live_state, _ = c16_runtime(
        state, mode="--worker", session=options["session"],
        native_inode=int(inode), journal_sha=options.get("journal_sha256"),
    )
    policy, selected = previous.install_worker_guard(live_state, int(inode))
    need(policy.installed is True and policy.prepared_family == "c"
         and selected.__name__ == "candidates.vm_candidate"
         and sys.modules.get("re") is selected
         and sys.modules.get("candidates.vm_candidate") is selected
         and type(sys.modules.get("candidates._vm_native")) is types.ModuleType
         and policy.bridge_owner["sha256"] == NATIVE_SHA
         and policy.engine_owner["sha256"] == NATIVE_SHA
         and "_sre" not in sys.modules and "ctypes" not in sys.modules,
         "verify the live authentic installed C16 V4 policy and selected C module")
    family, pins, source_pins = previous.activate_corrected_family(producer)
    provenance = producer.exact_native_owners(family, pins, source_pins)
    need(provenance.get("corrected_phase_c_source", {}).get("sha256")
             == NATIVE_SOURCE_SHA,
         "prove exact C24 native-source ownership after strict V4 installation")
    harness = types.ModuleType("_rebar_owned_c_full_public_v1_worker")
    harness.__file__ = ROOT + "/tools/rust_public_practice_benchmark_v2.py"
    harness.__package__ = None
    exec(compile(state["history"]["adapted_harness"], harness.__file__, "exec",
                 dont_inherit=True), harness.__dict__)
    harness.verify_pinned_runtime(permit_candidate=True)
    observed = harness.observe_worker("c-public-v1-candidate", "rust")
    policy.check_modules()
    records = observed.get("records")
    need(type(records) is list and len(records) == CASE_COUNT
         and observed.get("matrix_sha256") == MATRIX_SHA
         and observed.get("published_seed") == PUBLISHED_SEED
         and observed.get("candidate_runtime_provenance_checked") is True
         and observed.get("external_regex_package_count") == 0
         and observed.get("hidden_cases_read") == 0,
         "retain every genuine guarded C public outcome and nested failure")
    return {"schema": SCHEMA + "-isolated-candidate-worker", "status": "PASS",
            "family": "c", "pid": observed["pid"], "case_count": CASE_COUNT,
            "matrix_sha256": MATRIX_SHA, "published_seed": PUBLISHED_SEED,
            "runtime_guard_version": 4,
            "guard_installed_before_candidate_import": True,
            "candidate_imported": True,
            "records_sha256": observed["records_sha256"],
            "records": records,
            "candidate_runtime_provenance_checked": True,
            "external_regex_package_count": 0,
            "hidden_cases_read": 0, "holdout": "NOT OPENED",
            "timing_trials_run": 0}


def actual_run(options: dict, state: dict) -> dict:
    actual_authority(options)
    kernel = state["module"]
    c16, previous, producer, live_state, parsed = c16_runtime(
        state, mode="--run", session=options["session"],
    )
    original_adapter = c16.current_adapter(
        previous, ORIGINAL_ADAPTER_SHA, ORIGINAL_ADAPTER_BYTES,
        expected_inode=ORIGINAL_ADAPTER_INODE,
    )
    _native_bytes, original_native = previous.exact_original_native()
    need(original_native.get("inode") == ORIGINAL_NATIVE_INODE
         and original_native.get("sha256") == ORIGINAL_NATIVE_SHA
         and original_native.get("bytes") == ORIGINAL_NATIVE_BYTES,
         "authenticate both exact original canonical C owners before activation")
    adapter_active = native_active = None
    adapter_restored = native_restored = None
    primary = None
    reference = candidate = reference_raw = None
    try:
        adapter_active = c16.activate_corrected_adapter(
            previous, producer, parsed, live_state["c24"],
        )
        original_prepare = previous.prepare_recovery_root

        def existing_recovery_root() -> None:
            handle = previous.directory(previous.RECOVERY_ROOT, mode=0o700)
            try:
                identity = os.fstat(handle)
                need(stat.S_ISDIR(identity.st_mode)
                     and identity.st_uid == os.geteuid()
                     and stat.S_IMODE(identity.st_mode) == 0o700,
                     "require the genuine shared C16 dual-owner recovery root")
            finally:
                os.close(handle)

        previous.prepare_recovery_root = existing_recovery_root
        try:
            native_active = previous.activate_native(parsed, producer, live_state)
        finally:
            previous.prepare_recovery_root = original_prepare
        need(native_active["native_sha256"] == NATIVE_SHA
             and native_active["native_bytes"] == NATIVE_BYTES,
             "activate only the separately built exact C24 canonical native")

        import tempfile
        import subprocess
        import json

        overlay = tempfile.mkdtemp(prefix=OVERLAY_PREFIX, dir="/tmp")
        need(os.path.realpath(overlay) == overlay
             and stat.S_IMODE(os.stat(overlay).st_mode) == 0o700,
             "create one fresh owner-only isolated stdlib public overlay")
        os.mkdir(overlay + "/tools", 0o700)
        output_write(overlay + "/tools/rust_public_practice_benchmark_v2.py",
                     state["payloads"]["public_harness"])
        baseline_bootstrap = kernel.WORKER_BOOTSTRAP
        original_prefix = "rebar-rust-native-public-v3-"
        need(baseline_bootstrap.count(original_prefix) == 1,
             "preserve the authentic complete unmodified public worker kernel")
        kernel.WORKER_BOOTSTRAP = baseline_bootstrap.replace(
            original_prefix, OVERLAY_PREFIX,
        )
        reference, reference_raw = kernel.run_worker(
            overlay, "rust_public_practice_benchmark_v2.py",
            PUBLIC_HARNESS_SHA, "c-public-v1-stdlib", "stdlib", "observe",
        )
        need(reference.get("case_count") == CASE_COUNT
             and reference.get("oracle_is_stdlib_only") is True,
             "execute all 10,434 genuine isolated standard-library oracle cases")

        command = [PYTHON, "-I", "-B", "-S", ROOT + "/" + SOURCE,
                   "--candidate-worker"]
        for name in ("source_sha256", "protocol_sha256", "contract_sha256",
                     "frozen_commit", "pushed_commit", "session"):
            command.extend(("--" + name.replace("_", "-"), options[name]))
        for name, value in ACTUAL_PINNED.items():
            command.extend(("--" + name.replace("_", "-"), value))
        command.extend(("--journal-sha256", native_active["journal"]["sha256"],
                        "--activation-inode", str(native_active["native_inode"]),
                        "--root-authorized", "--frozen-committed-pushed"))
        worker = subprocess.Popen(
            command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=ROOT, shell=False, close_fds=True,
            env={"PATH": "/usr/bin:/bin", "LC_ALL": "C",
                 "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                 "PYTHONMALLOC": "malloc"},
        )
        stdout, stderr = worker.communicate(timeout=600)
        need(worker.returncode == 0 and not stderr
             and 0 < len(stdout) <= MAX_ACTUAL_BYTES,
             "complete authentic strict-V4 C candidate worker failed: "
             + stderr[:4000].decode("utf-8", "replace"))
        candidate = json.loads(stdout.decode("utf-8"))
        need(type(candidate) is dict
             and candidate.get("schema") == SCHEMA + "-isolated-candidate-worker"
             and candidate.get("status") == "PASS"
             and candidate.get("family") == "c"
             and candidate.get("case_count") == CASE_COUNT
             and candidate.get("matrix_sha256") == MATRIX_SHA
             and candidate.get("published_seed") == PUBLISHED_SEED
             and candidate.get("runtime_guard_version") == 4
             and candidate.get("guard_installed_before_candidate_import") is True
             and candidate.get("candidate_imported") is True
             and candidate.get("candidate_runtime_provenance_checked") is True
             and candidate.get("external_regex_package_count") == 0
             and candidate.get("hidden_cases_read") == 0
             and candidate.get("pid") != reference.get("pid"),
             "require the genuine independently isolated strict-V4 C worker")
    except BaseException as error:
        primary = error
    finally:
        if native_active is not None:
            try:
                native_restored = previous.restore_native(
                    native_active["journal_document"],
                    native_active["journal"]["sha256"], producer,
                )
            except BaseException as error:
                if primary is None:
                    primary = error
        if adapter_active is not None:
            try:
                adapter_restored = c16.restore_corrected_adapter(
                    previous, producer, adapter_active["journal_document"],
                    adapter_active["journal"]["sha256"],
                )
            except BaseException as error:
                if primary is None:
                    primary = error
    if primary is not None:
        raise primary
    need(type(native_restored) is dict and native_restored.get("status") == "PASS"
         and native_restored.get("restored_original") == original_native
         and type(adapter_restored) is dict
         and adapter_restored.get("status") == "PASS"
         and adapter_restored.get("original_adapter") == original_adapter
         and adapter_restored.get("exact_original_adapter_inode_restored") is True,
         "restore both exact original canonical C inodes before any publication")
    current_adapter = c16.current_adapter(
        previous, ORIGINAL_ADAPTER_SHA, ORIGINAL_ADAPTER_BYTES,
        expected_inode=ORIGINAL_ADAPTER_INODE,
    )
    _current_bytes, current_native = previous.exact_original_native()
    need(current_adapter == original_adapter and current_native == original_native,
         "independently reauthenticate both restored original canonical C owners")
    need(type(reference) is dict and type(candidate) is dict
         and type(reference_raw) is bytes,
         "retain both complete isolated observations after exact dual recovery")
    baseline_rows = reference.get("records")
    actual_rows = candidate.get("records")
    need(type(baseline_rows) is list and type(actual_rows) is list
         and len(baseline_rows) == len(actual_rows) == CASE_COUNT,
         "never omit one actual baseline or guarded C public case")
    mismatches = []
    for expected, actual in zip(baseline_rows, actual_rows, strict=True):
        need(type(expected) is dict and type(actual) is dict
             and expected.get("case") == actual.get("case"),
             "reject omitted, reordered, or substituted complete public case")
        if expected != actual:
            mismatches.append({"case": expected["case"],
                               "expected_record": expected,
                               "actual_record": actual})
    status = "PASS" if not mismatches else "FAIL"
    full = {"schema": SCHEMA + "-complete-public-observation", "status": status,
            "family": "c", "case_denominator": CASE_COUNT,
            "actual_baseline_cases": CASE_COUNT,
            "actual_c_cases": CASE_COUNT,
            "mismatch_count": len(mismatches),
            "all_mismatches": mismatches,
            "all_nested_error_records_retained": True,
            "public_api_operation_count": OPERATIONS_PER_DATASET,
            "dataset_count": DATASET_COUNT,
            "text_case_count": DOMAIN_CASE_COUNT,
            "bytes_case_count": DOMAIN_CASE_COUNT,
            "matrix_sha256": MATRIX_SHA,
            "published_seed": PUBLISHED_SEED,
            "reference_pid": reference["pid"], "c_pid": candidate["pid"],
            "actual_candidate_workers": 1, "actual_reference_workers": 1,
            "runtime_guard_version": 4,
            "guard_installed_before_candidate_import": True,
            "both_canonical_owners_restored_before_publication": True,
            "clock_samples": 0, "timing_trials_run": 0,
            "hidden_cases_read": 0, "holdout": "NOT OPENED",
            "candidate_qualified": False, "winner_selected": False}

    try:
        os.mkdir(PUBLIC_OUTPUT, 0o700)
    except FileExistsError:
        info = os.stat(PUBLIC_OUTPUT, follow_symlinks=False)
        need(stat.S_ISDIR(info.st_mode)
             and stat.S_IMODE(info.st_mode) == 0o700
             and info.st_uid == os.geteuid(),
             "reject a substituted public full-correctness C directory")
    target = PUBLIC_OUTPUT + "/" + options["session"]
    os.mkdir(target, 0o700)
    artifacts = [
        output_write(target + "/public-10434-stdlib.correctness.raw.json",
                     reference_raw),
        output_write(target + "/public-10434-c.correctness.raw.json",
                     kernel.document(candidate)),
        output_write(target + "/public-10434-correctness.raw.json",
                     kernel.document(full)),
    ]
    receipt = {"schema": SCHEMA + "-durable-publication-receipt",
               "version": VERSION, "status": "PASS",
               "publication_status": "PASS",
               "publication_pass_means": "DURABLE PUBLICATION ONLY",
               "candidate_status": status, "family": "c",
               "public_10434_correctness_status": status,
               "public_10434_case_count": CASE_COUNT,
               "public_10434_verified_passing_case_count":
                    CASE_COUNT - len(mismatches),
               "public_10434_mismatch_count": len(mismatches),
               "all_public_mismatches_preserved": True,
               "all_nested_error_records_preserved": True,
               "public_api_operation_count": OPERATIONS_PER_DATASET,
               "public_dataset_count": DATASET_COUNT,
               "public_text_case_count": DOMAIN_CASE_COUNT,
               "public_bytes_case_count": DOMAIN_CASE_COUNT,
               "matrix_sha256": MATRIX_SHA,
               "published_seed": PUBLISHED_SEED,
               "reference_worker_count": 1, "candidate_worker_count": 1,
               "reference_pid": reference["pid"], "c_pid": candidate["pid"],
               "strict_runtime_guard_version": 4,
               "guard_installed_before_candidate_import": True,
               "source_sha256": options["source_sha256"],
               "protocol_sha256": options["protocol_sha256"],
               "contract_sha256": options["contract_sha256"],
               "frozen_commit": options["frozen_commit"],
               "pushed_commit": options["pushed_commit"],
               "c24_build_receipt_sha256": BUILD_RECEIPT_SHA,
               "c24_private_root_receipt_sha256": ROOT_RECEIPT_SHA,
               "c16_original_pass_receipt_sha256": ORIGINAL_PASS_SHA,
               "c16_original_verified_passing_case_count": 31237,
               "final_adapter_sha256": ADAPTER_SHA,
               "native_engine_sha256": NATIVE_SHA,
               "native_bridge_sha256": NATIVE_SHA,
               "frozen_111_operation_harness_sha256": PUBLIC_HARNESS_SHA,
               "authenticated_c_harness_transform_sha256": C_HARNESS_SHA,
               "original_adapter_inode_restored_before_publication": True,
               "original_native_inode_restored_before_publication": True,
               "all_canonical_c_owners_restored_before_publication": True,
               "artifacts": artifacts,
               "clock_samples": 0, "timing_trials_run": 0,
               "performance": "NOT MEASURED", "memory": "NOT MEASURED",
               "undefined_behavior": "NOT MEASURED",
               "runtime_non_delegation": "NOT ESTABLISHED",
               "candidate_qualified": False, "hidden_cases_read": 0,
               "winner_selected": False, "final_holdout": FINAL_HOLDOUT}
    receipt_path = (ROOT + "/oracle/phase2/evidence/"
                    "c-full-public-correctness-v1-" + options["session"]
                    + "-publication-receipt.json")
    publication = output_write(receipt_path, kernel.document(receipt))
    return {"schema": SCHEMA + "-actual-root-operation", "status": status,
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": status, "family": "c",
            "public_10434_correctness_status": status,
            "public_10434_case_count": CASE_COUNT,
            "public_10434_verified_passing_case_count":
                CASE_COUNT - len(mismatches),
            "public_10434_mismatch_count": len(mismatches),
            "public_api_operation_count": OPERATIONS_PER_DATASET,
            "candidate_worker_count": 1, "reference_worker_count": 1,
            "strict_runtime_guard_version": 4,
            "guard_installed_before_candidate_import": True,
            "c16_original_verified_passing_case_count": 31237,
            "original_adapter_inode_restored_before_publication": True,
            "original_native_inode_restored_before_publication": True,
            "all_canonical_c_owners_restored_before_publication": True,
            "canonical_candidate_modified": False,
            "publication_receipt": publication, "artifacts": artifacts,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "hidden_cases_read": 0, "candidate_qualified": False,
            "winner_selected": False}


def parse_options(values: list[str]) -> dict:
    modes = [item for item in values if item in SOURCE_MODES + ACTUAL_MODES]
    need(len(modes) == 1,
         "select exactly one public source-only, root, or isolated candidate action")
    result: dict[str, object] = {"mode": modes[0]}
    index = 0
    while index < len(values):
        flag = values[index]
        if flag in SOURCE_MODES + ACTUAL_MODES:
            index += 1
            continue
        if flag in ("--root-authorized", "--frozen-committed-pushed"):
            name = flag[2:].replace("-", "_")
            need(name not in result, "reject duplicate public root authority")
            result[name] = True
            index += 1
            continue
        need(flag.startswith("--") and index + 1 < len(values),
             "reject incomplete or positional full-public C authority")
        name = flag[2:].replace("-", "_")
        need(name not in result,
             "reject duplicate independently pinned public authority: " + flag)
        result[name] = values[index + 1]
        index += 2
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
                  "frozen_commit", "pushed_commit", "session", *ACTUAL_PINNED}
        if result["mode"] == "--candidate-worker":
            extras.update(("journal_sha256", "activation_inode"))
        need(set(result) == {"mode", *standard, *extras},
             "independently pin every root-only C24/C16 public authority")
        for name in (*standard, *ACTUAL_PINNED):
            if name.endswith("_sha256"):
                sha(result.get(name), name)
        commit(result.get("frozen_commit"), "frozen full-public C commit")
        commit(result.get("pushed_commit"), "pushed full-public C commit")
        if result["mode"] == "--candidate-worker":
            sha(result.get("journal_sha256"), "actual C16 native recovery journal")
    return result


def main(values: list[str]) -> int:
    need(sys.executable == PYTHON and sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.flags.no_site == 1
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
             "close all public descriptors before canonical contract rendering")
        result = state["freeze"]
    elif options["mode"] == "--verify-frozen-context":
        need(wall is not None, "require the permanent source verification wall")
        result = verify_summary(wall, state)
    elif options["mode"] == "--self-test":
        need(wall is not None, "require the permanent hostile-control source wall")
        result = self_test(wall, state)
    elif options["mode"] == "--candidate-worker":
        result = isolated_candidate(options, state)
    else:
        result = actual_run(options, state)
    sys.stdout.buffer.write(state["module"].document(result))
    sys.stdout.buffer.flush()
    return (0 if result.get("status") == "PASS"
            or options["mode"] == "--render-contract" else 1)


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (PublicError, OSError, ValueError, TypeError, KeyError,
            SyntaxError, AttributeError) as error:
        sys.stderr.write("full first-party C public correctness rejected: "
                         + type(error).__qualname__ + ": " + str(error) + "\n")
        raise SystemExit(2)
