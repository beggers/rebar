#!/usr/bin/env python3
"""Freeze and, only on root authorization, run the corrected Rust campaign.

Source modes install a physical public-plaintext-only wall before the first
predecessor byte.  Actual modes preserve the entire authenticated V22/V21
history, then build a separately migrated V24 runner bound to the genuinely
published V24 native receipts and independently frozen operational V4 guard.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("a first-party Rust campaign cannot start with a matcher")

import _io
import ast
import builtins
import hashlib
import importlib
import io
import os
import stat
import time
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
DEVICE = 2064
SOURCE = "tools/run_owned_repaired_rust_original_campaign_v25.py"
PROTOCOL = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V25.md"
CONTRACT = "oracle/phase2/repaired-rust-original-campaign-v25.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v25"
VERSION = 25
FAMILY = "rust"
NOT_MEASURED = "NOT MEASURED"
GOAL_SHA = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
MAX_OWNER_BYTES = 2 * 1024 * 1024
CASE_COUNT = 31_237
WORKER_COUNT = 13
SUPPLEMENTAL_CASE_COUNT = 8_244
CORRECTED_REFERENCE_CASE_COUNT = 6_912
HOLDOUT_CASE_COUNT = 141_557_760
BUILD_LABEL = "phase2-v25-rust-capture-clamp-v1-root-provenance"
BUILD_SUFFIX = BUILD_LABEL + "-original-p0"
LABEL = BUILD_SUFFIX + "-v25"
RECOVERY_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v25-"
RECOVERY_ROOT = "/tmp/" + RECOVERY_PREFIX + BUILD_SUFFIX
LOCK_NAME = "recoverable-controller-v25.lock"
BRIDGE_SOURCE_SHA = "a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54"
BRIDGE_SOURCE_BYTES = 178805
FAILED_BRIDGE_SOURCE_SHA = "f9bd2d3c8406e4b2c703ce96f42964ee15941611e22447b12acc9b54fac98055"
ADAPTER_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
ADAPTER_BYTES = 31934
ENGINE_SHA = "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
ENGINE_BYTES = 658344
BRIDGE_SHA = "adcb000c036e075a52f43926750648a4610e853e628d5433b1fbcc17e99a89e4"
BRIDGE_BYTES = 148720
ROOT_PATH = "/tmp/rebar-phase2-native-build-v9-rust-gx53scyp"
ROOT_DEVICE = 2049
ROOT_INODE = 11676733
PHASE_NATIVE_INODES = ((11676799, 11676805), (11676834, 11676830))
ARCHIVE_SHA = "26b23871c97af8e343122caafddaeef5f14bb601070be482dd9acdd842df1f60"
ARCHIVE_BYTES = 108113
ARCHIVE_INODE = 526083
PLAIN_SHA = "cc3d2313aff40e5b6bb85a151260e5973826178a04a18a03fa1a456625fdc115"
PLAIN_BYTES = 757409

V23 = (
    ("v23_source", "tools/run_owned_repaired_rust_original_campaign_v23.py",
     "dfa8b2a4d2a8ecbadbe36097a7dc55ce92abfeda56bf6cd0a8f02ae72b544b29",
     66129, 431185),
    ("v23_protocol", "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V23.md",
     "289fb9f2ddd20d3f29749f0328894be2f540eaec8485ad0d7ba4d5e932eaf68e",
     7194, 525487),
    ("v23_contract", "oracle/phase2/repaired-rust-original-campaign-v23.json",
     "08cb3111855de792b2708db0c281c6d110735f79f3e85a3ef6c5de9944be5aa6",
     181093, 525488),
)
V22 = (
    ("v22_source", "tools/run_owned_repaired_rust_original_campaign_v22.py",
     "e88f242835781e9b70efa18e68a7b06b0b9368e91320ed596995ef0e16370c61",
     61761, 430995),
    ("v22_protocol", "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V22.md",
     "c6a2a5db9c9c27974c29af01b3d7f7042bae73e254c638fe27813505ef11f396",
     6038, 525307),
    ("v22_contract", "oracle/phase2/repaired-rust-original-campaign-v22.json",
     "f1c021049e4bb173be8d47339920354e02c8c0194aead877b8474a128b5e158a",
     42352, 525314),
)
BUILD = (
    ("build_v25_source",
     "tools/reproduce_owned_rust_capture_clamp_source_build_v25.py",
     "f0a5d0b0af76b83e4f7091050afc187458c8c4380a37418f5df0de41d882b408",
     186263, 429530),
    ("build_v25_protocol",
     "oracle/phase2/RUST-CAPTURE-CLAMP-SOURCE-BUILD-V25.md",
     "ddc7c1fcf385ec979c73a304123025a6e5974a8eb37dd61cf189ccba20687f85",
     7140, 525993),
    ("build_v25_contract",
     "oracle/phase2/rust-capture-clamp-source-build-v25.json",
     "528d2bcccb2cceed5f607f7ec8428b18df10f30b9b6b6f7313083a288061127a",
     229419, 526066),
)
BUILD_RECEIPT = (
    "build_v25_public_receipt",
    "oracle/phase2/evidence/native-source-build-v25-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-publication-receipt.json",
    "55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc",
    5231, 526084,
)
ROOT_RECEIPT = (
    "build_v25_root_receipt",
    "oracle/phase2/evidence/native-source-build-v25-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-"
    "root-provenance-receipt.json",
    "e8633ac1224235db9f8ea48c683c833fba3015cd73f071cd2488fa0b13a117a2",
    61798, 526085,
)
GUARD_V4 = (
    ("guard_v4_source", "tools/verify_owned_candidate_runtime_independence_v4.py",
     "5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3",
     48687, 429243),
    ("guard_v4_protocol", "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md",
     "835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16",
     4492, 525890),
    ("guard_v4_contract", "oracle/phase2/candidate-runtime-independence-v4.json",
     "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2",
     9352, 525891),
)
V3 = (
    ("tools/verify_owned_candidate_runtime_independence_v3.py",
     "03f051e428ee31bb671d8ced82f02d7a9fe3520f24191aba78d2e8a0697202c2",
     59765, 430856),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V3.md",
     "d3437b642d322ccccf12851981555cb596ff7f9c5a12e0a6a389d6b80b5a068a",
     5297, 525096),
    ("oracle/phase2/candidate-runtime-independence-v3.json",
     "31e9a5d2754b5b4b273d4fc30d6a27967e495b57684fdd1e9306bbac3b2caaa7",
     9157, 525114),
)
V22_FAILURE_SHA = "7013c42f6309d94e094dd89cc8e9f24fe245c0cba5ca4791d35ffe5fa2b7dad7"
V21_FAILURE_SHA = "bf4c321aa10b4961bd40ad1f12584296bd20356d18fef1542d360c03f48e6bda"
V24_FAILURE = (
    "actual_v24_complete_failure_receipt",
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v24-rust-capture-shape-v2-root-provenance-"
    "original-p0-v24-failures-publication-receipt.json",
    "5acd8dee2a515af56306e61f6ae8774c567f1f47e0ef1930a17e6809c2aafa09",
    11832, 525952,
)
PREVIOUS_V24 = (
    ("previous_v24_campaign_source",
     "tools/run_owned_repaired_rust_original_campaign_v24.py",
     "f855f73e320f4ec33063dac1f22c11b1977ba04a02e1f97dfddca1d0670f705d",
     83262, 429270),
    ("previous_v24_campaign_protocol",
     "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V24.md",
     "d482cf8d06f9f328c08fda43a63db79db408e2421bad24e6e047ad507ef70431",
     6617, 525887),
    ("previous_v24_campaign_contract",
     "oracle/phase2/repaired-rust-original-campaign-v24.json",
     "605737aa5060b78eb3802c8b3e58954a680bdf08b6f62a402de453552a0cd8f4",
     14607, 525907),
)
AUDIT_V4 = (
    ("independent_nondelegation_v4_source",
     "tools/audit_candidate_runtime_non_delegation_v4.py",
     "597f2f1156d773a42e32103ef7370e8552a416756910c013cdcd0cfc34d39b02",
     121807, 429582),
    ("independent_nondelegation_v4_protocol",
     "oracle/phase2/RUNTIME-NON-DELEGATION-V4.md",
     "6c3bd6b2ccabe3ab240771d743afce5b32f1de17a510bedd835e867c5cea7826",
     5325, 526087),
    ("independent_nondelegation_v4_contract",
     "oracle/phase2/runtime-non-delegation-v4.json",
     "edc3ac8866da7afb5934b56fbcbff38a908e5109f7975f998753b479aa7bc672",
     7266, 526086),
)
AUDIT_V4_FAILURE = (
    "independent_nondelegation_v4_actual_failure_receipt",
    "oracle/phase2/evidence/runtime-non-delegation-v4-actual-source-audit-"
    "failure.json",
    "c3020fe067ad06c2bf7309a73b960884572addd9e984d01d2cf27d5cd9d61f19",
    20985, 526140,
)

V23_STATIC_PATHS = (
    "tools/apply_owned_rust_capture_shape_semantics_v2.py",
    "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V2.md",
    "oracle/phase2/rust-capture-shape-semantics-v2.json",
    "GOAL.md", "oracle/phase1/p0-completeness-v4.json",
    "oracle/phase1/p0-differential-fuzz-reference-v3.json",
    "tools/independent_substitution_buffer_semantics_v2.py",
    "tools/independent_shape_changing_buffer_semantics_v2.py",
    "tools/apply_owned_rust_capture_shape_semantics_v1.py",
    "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V1.md",
    "oracle/phase2/rust-capture-shape-semantics-v1.json",
    "tools/reproduce_owned_rust_capture_shape_semantics_source_build_v22.py",
    "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-SOURCE-BUILD-V22.md",
    "oracle/phase2/rust-capture-shape-semantics-source-build-v22.json",
    "oracle/phase2/evidence/native-source-build-v22-rust-"
    "phase2-v22-rust-capture-shape-root-provenance-publication-receipt.json",
    "oracle/phase2/evidence/native-source-build-v22-rust-"
    "phase2-v22-rust-capture-shape-root-provenance-root-provenance-receipt.json",
    "tools/run_owned_repaired_rust_original_campaign_v22.py",
    "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V22.md",
    "oracle/phase2/repaired-rust-original-campaign-v22.json",
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v21-rust-captured-findall-root-provenance-"
    "original-p0-v20-failures-publication-receipt.json",
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v22-rust-capture-shape-root-provenance-"
    "original-p0-v22-failures-publication-receipt.json",
    "tools/verify_owned_candidate_runtime_independence_v3.py",
    "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V3.md",
    "oracle/phase2/candidate-runtime-independence-v3.json",
    "tools/verify_owned_candidate_runtime_independence_v2.py",
    "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md",
    "oracle/phase2/candidate-runtime-independence-v2.json",
    "tools/run_owned_six_family_original_p0_producer_v5.py",
    "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md",
    "oracle/phase2/six-family-p0-producer-v5.json",
)

SOURCE_MODES = ("--render-contract", "--self-test", "--verify-frozen-context")
ACTUAL_MODES = ("--run", "--worker", "--recover")
SOURCE_PIN_FLAGS = (
    "--source-sha256", "--protocol-sha256", "--contract-sha256",
    "--guard-v4-source-sha256", "--guard-v4-protocol-sha256",
    "--guard-v4-contract-sha256",
)


class CampaignError(Exception):
    """A frozen owner, historical fact, native identity, or runtime guard changed."""


def need(value: object, label: str) -> None:
    if value is not True:
        raise CampaignError(label)


def sha(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only complete authenticated public bytes")
    return hashlib.sha256(raw).hexdigest()


def sha_pin(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(item in "0123456789abcdef" for item in value),
         "require one complete independently pinned SHA-256: " + label)
    assert isinstance(value, str)
    return value


def no_matching_imports() -> None:
    roots = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
             "ctypes", "candidates", "socket", "subprocess",
             "concurrent.interpreters")
    need(not any(name == root or name.startswith(root + ".")
                 for name in sys.modules for root in roots),
         "reject stdlib, indirect, external, or cross-candidate matching")


def verify_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.executable == PYTHON and sys.flags.isolated == 1
         and sys.flags.no_site == 1 and sys.dont_write_bytecode is True,
         "require exact isolated CPython 3.14.6 with -I -B -S")
    no_matching_imports()


class PublicSourceWall:
    """Physically permit only pinned public plaintext and tracked descriptors."""

    def __init__(self) -> None:
        relatives = (
            SOURCE, PROTOCOL, CONTRACT, *V23_STATIC_PATHS,
            *(item[1] for item in V23), *(item[1] for item in BUILD),
            *(item[1] for item in GUARD_V4), *(item[1] for item in PREVIOUS_V24),
            *(item[1] for item in AUDIT_V4), BUILD_RECEIPT[1], ROOT_RECEIPT[1],
            V24_FAILURE[1], AUDIT_V4_FAILURE[1],
        )
        need(len(relatives) == len(frozenset(relatives)),
             "reject duplicate or aliased V24 public plaintext owners")
        self.allowed = frozenset(ROOT + "/" + item for item in relatives)
        self.live: set[int] = set()
        self.blocked: dict[str, int] = {}
        self.installed = False
        self.error_type: type[Exception] = CampaignError
        self.native_open, self.native_read = os.open, os.read
        self.native_fstat, self.native_close = os.fstat, os.close

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise self.error_type("V24 public source wall rejected " + category)

    def approved(self, path: object) -> bool:
        return (type(path) is str and path.startswith(ROOT + "/")
                and path == os.path.normpath(path)
                and not any(part in (".", "..") for part in path.split("/"))
                and path in self.allowed and not path.endswith((".gz", ".so"))
                and not path.startswith((ROOT + "/candidates/",
                                         ROOT + "/oracle/phase3/"))
                and "holdout" not in path.lower()
                and "benchmark" not in path.lower())

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else None
            destructive = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                           | os.O_APPEND | getattr(os, "O_TMPFILE", 0))
            if (not self.approved(path) or type(flags) is not int
                    or flags & destructive
                    or not flags & getattr(os, "O_NOFOLLOW", 0)
                    or type(mode) is str and any(item in mode for item in "wax+")):
                self.deny("unowned-direct-file-open")
            return
        if event in ("exec", "compile"):
            item = args[0] if args else None
            filename = (getattr(item, "co_filename", None) if event == "exec"
                        else args[1] if len(args) > 1 else None)
            if not self.approved(filename):
                self.deny("unowned-dynamic-execution")
            return
        if (event == "import" or event == "marshal.loads"
                or event in ("os.system", "os.fork", "os.posix_spawn",
                             "os.posix_spawnp", "os.rename", "os.replace",
                             "os.remove", "os.unlink", "os.mkdir", "os.rmdir",
                             "os.chmod", "os.chown", "os.urandom", "os.getrandom",
                             "_interpreters.create", "_interpreters.exec",
                             "cpython.PyInterpreterState_New")
                or event.startswith(("subprocess.", "socket.", "ctypes.",
                                      "threading.", "multiprocessing.",
                                      "tempfile.", "time.", "os.exec",
                                      "os.spawn", "random."))):
            self.deny("process-import-native-clock-network-or-mutation")

    def _forbidden(self, category: str):
        def blocked(*_args: object, **_kwargs: object) -> object:
            self.deny(category)
        return blocked

    def guarded_open(self, path: object, flags: object, mode: int = 0o777,
                     *, dir_fd: object = None) -> int:
        forbidden = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                     | os.O_APPEND | getattr(os, "O_TMPFILE", 0)
                     | getattr(os, "O_DIRECTORY", 0))
        if (not self.approved(path) or type(flags) is not int
                or flags & forbidden or not flags & getattr(os, "O_NOFOLLOW", 0)
                or dir_fd is not None):
            self.deny("unowned-os-open-or-private-directory")
        assert isinstance(path, str)
        descriptor = self.native_open(path, flags, mode)
        need(type(descriptor) is int and descriptor >= 0
             and descriptor not in self.live,
             "require one fresh genuine public descriptor")
        self.live.add(descriptor)
        return descriptor

    def guarded_read(self, descriptor: object, count: object) -> bytes:
        if (type(descriptor) is not int or descriptor not in self.live
                or type(count) is not int or not 0 <= count <= MAX_OWNER_BYTES):
            self.deny("foreign-or-unbounded-descriptor-read")
        assert isinstance(descriptor, int) and isinstance(count, int)
        return self.native_read(descriptor, count)

    def guarded_fstat(self, descriptor: object) -> os.stat_result:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("foreign-descriptor-metadata")
        assert isinstance(descriptor, int)
        return self.native_fstat(descriptor)

    def guarded_close(self, descriptor: object) -> None:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("foreign-descriptor-close")
        assert isinstance(descriptor, int)
        self.live.remove(descriptor)
        self.native_close(descriptor)

    def install(self) -> None:
        need(self.installed is False,
             "reject a reused V24 deny-default public source wall")
        sys.addaudithook(self.audit)
        builtins.open = self._forbidden("builtins-open")
        _io.open = self._forbidden("direct-_io-open")
        _io.FileIO = self._forbidden("direct-_io-fileio")
        io.open = self._forbidden("direct-io-open")
        io.FileIO = self._forbidden("direct-io-fileio")
        for module in (_io, io):
            if hasattr(module, "open_code"):
                module.open_code = self._forbidden("direct-open-code")
        os.open, os.read = self.guarded_open, self.guarded_read
        os.fstat, os.close = self.guarded_fstat, self.guarded_close
        for name in ("fdopen", "dup", "dup2", "stat", "lstat", "readlink",
                     "listdir", "scandir", "walk", "fwalk", "access", "fork",
                     "posix_spawn", "posix_spawnp", "system", "mkdir",
                     "makedirs", "remove", "unlink", "rename", "replace",
                     "rmdir", "chmod", "chown", "urandom", "getrandom"):
            if hasattr(os, name):
                setattr(os, name, self._forbidden("direct-os-" + name))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns",
                     "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self._forbidden("clock-" + name))
        self.installed = True


def secure_owner(wall: PublicSourceWall | None, row: tuple) -> bytes:
    need(type(row) is tuple and len(row) == 5,
         "require one fully pinned public first-party owner")
    role, relative, expected, count, inode = row
    need(type(role) is str and type(relative) is str
         and not relative.startswith("/") and ".." not in relative.split("/")
         and type(count) is int and 0 < count <= MAX_OWNER_BYTES
         and type(inode) is int and inode > 0,
         "reject unbounded, private, or incomplete first-party owner")
    sha_pin(expected, relative)
    absolute = ROOT + "/" + relative
    need(wall is None or wall.installed and wall.approved(absolute),
         "install the V24 source wall before reading any predecessor")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(absolute, flags)
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode)
             and stat.S_IMODE(before.st_mode) == 0o600
             and before.st_dev == DEVICE and before.st_ino == inode
             and before.st_size == count and before.st_uid == os.geteuid()
             and before.st_nlink == 1,
             "reject substituted complete no-follow public owner: " + role)
        remaining, chunks = count, []
        while remaining:
            chunk = os.read(descriptor, min(65536, remaining))
            need(type(chunk) is bytes and bool(chunk),
                 "reject truncated exact public evidence: " + role)
            chunks.append(chunk)
            remaining -= len(chunk)
        need(os.read(descriptor, 1) == b"",
             "reject expanded exact public evidence: " + role)
        after = os.fstat(descriptor)
        need(all(getattr(before, key) == getattr(after, key)
                 for key in ("st_dev", "st_ino", "st_size", "st_mtime_ns",
                             "st_ctime_ns", "st_nlink")),
             "reject concurrently replaced complete public owner: " + role)
        raw = b"".join(chunks)
        need(sha(raw) == expected,
             "reject altered complete pinned first-party owner: " + role)
        return raw
    finally:
        os.close(descriptor)


def dynamic_owner(wall: PublicSourceWall | None, role: str,
                  relative: str, fingerprint: str) -> tuple:
    sha_pin(fingerprint, role)
    need(relative in (SOURCE, PROTOCOL, CONTRACT),
         "reject an unowned dynamically pinned V24 source owner")
    absolute = ROOT + "/" + relative
    need(wall is None or wall.installed and wall.approved(absolute),
         "reject a current owner before physical wall installation")
    descriptor = os.open(absolute, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        found = os.fstat(descriptor)
        need(stat.S_ISREG(found.st_mode)
             and stat.S_IMODE(found.st_mode) == 0o600
             and found.st_dev == DEVICE and found.st_uid == os.geteuid()
             and found.st_nlink == 1 and 0 < found.st_size <= MAX_OWNER_BYTES,
             "reject unsafe or exchanged current V24 source owner: " + role)
        return role, relative, fingerprint, found.st_size, found.st_ino
    finally:
        os.close(descriptor)


def owner_document(row: tuple) -> dict:
    return {"role": row[0], "path": row[1], "sha256": row[2],
            "bytes": row[3], "device": DEVICE, "inode": row[4],
            "mode": "0600", "uid": os.geteuid(), "nlink": 1}


def strict_document(capture: types.ModuleType, semantic: types.ModuleType,
                    raw: bytes, label: str) -> dict:
    value = semantic.StrictJSON(raw).decode()
    need(type(value) is dict
         and capture.canonical_document(semantic, value) == raw,
         "reject duplicate, noncanonical, or incomplete public JSON: " + label)
    return value


def previous_v23(wall: PublicSourceWall) -> tuple[types.ModuleType, dict, dict]:
    raw = secure_owner(wall, V23[0])
    module = types.ModuleType("_rebar_v24_immutable_public_campaign_v23")
    module.__file__ = ROOT + "/" + V23[0][1]
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    need(module.SOURCE == V23[0][1] and module.PROTOCOL == V23[1][1]
         and module.CONTRACT == V23[2][1] and module.VERSION == 23
         and callable(module.load_context) and callable(module.self_test)
         and tuple(item[1] for item in module.STATIC_OWNERS) == V23_STATIC_PATHS,
         "authenticate complete immutable V23 public-only campaign")
    pins = {"--source-sha256": V23[0][2], "--protocol-sha256": V23[1][2],
            "--contract-sha256": V23[2][2]}
    frozen, state = module.load_context(wall, pins, False)
    need(len(frozen) == 20 and len(state["campaign"]) == 435
         and len(state["actual"]) == 96
         and frozen["immutable_previous_v22_campaign"]
             ["complete_inherited_v21_contract_field_count"] == 402,
         "preserve all immutable V23, V22, V21, and genuine worker obligations")
    return module, frozen, state


def validate_v4_guard(value: dict, rows: tuple = GUARD_V4) -> dict:
    need(type(value) is dict and len(value) == 26
         and value.get("schema")
         == "rebar-owned-candidate-runtime-independence-v4-source-freeze"
         and value.get("version") == 4
         and value.get("goal_sha256") == GOAL_SHA
         and value.get("source", {}).get("path") == rows[0][1]
         and value.get("source", {}).get("sha256") == rows[0][2]
         and value.get("protocol", {}).get("path") == rows[1][1]
         and value.get("protocol", {}).get("sha256") == rows[1][2]
         and type(value.get("immutable_predecessor_v3")) is dict
         and type(value.get("immutable_predecessor_v2")) is dict
         and type(value.get("immutable_producer_v5")) is dict
         and type(value.get("provider_proof")) is dict,
         "authenticate the entire operational V4/V3/V2/V5 runtime guard")
    predecessor = value["immutable_predecessor_v3"]
    predecessors = value["immutable_predecessor_v2"]
    producer = value["immutable_producer_v5"]
    native = value.get("native_owner_policy")
    policy = value.get("runtime_isolation_policy")
    children = value.get("subinterpreter_bootstrap")
    need(predecessor.get("version") == 3
         and predecessor.get("owners", {}).get("source", {}).get("sha256")
         == V3[0][1]
         and predecessor.get("owners", {}).get("protocol", {}).get("sha256")
         == V3[1][1]
         and predecessor.get("owners", {}).get("contract", {}).get("sha256")
         == V3[2][1]
         and predecessors.get("version") == 2 and producer.get("version") == 5
         and type(native) is dict and native.get("required_field_count") == 14
         and native.get("native_loaded") is False and type(policy) is dict
         and all(policy.get(key) == "FORBIDDEN" for key in (
             "stdlib_re_engine", "stdlib_sre_engine", "external_regex_package",
             "cross_candidate_engine", "matching_fallback"))
         and policy.get("guard_installed_before_candidate_import") is True
         and type(children) is dict and children.get("suite") == "subinterpreter_v2"
         and children.get("expected_interpreters_created") == 11
         and children.get("expected_interpreters_destroyed") == 11
         and children.get("expected_case_interpreter_exec_calls") == 394
         and children.get("expected_total_real_interpreter_exec_calls") == 416
         and children.get("actual_interpreters_created") == 0
         and children.get("actual_case_interpreter_exec_calls") == 0,
         "reject weakened V4 live child verification or first-party isolation")
    return value


def validate_previous_v24_failure(campaign: object, failure: object) -> None:
    need(
        type(campaign) is dict
        and campaign.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v24-"
           "recoverable-source-freeze"
        and campaign.get("version") == 24
        and campaign.get("source", {}).get("sha256") == PREVIOUS_V24[0][2]
        and campaign.get("protocol", {}).get("sha256") == PREVIOUS_V24[1][2]
        and campaign.get("original_correctness_boundary", {}).get(
            "case_execution_denominator",
        ) == CASE_COUNT
        and campaign.get("original_correctness_boundary", {}).get("suite_count")
        == WORKER_COUNT
        and campaign.get("operational_runtime_guard_v4", {}).get("version") == 4,
        "authenticate the complete immutable previously frozen V24 campaign",
    )
    need(
        type(failure) is dict and len(failure) == 96
        and failure.get("status") == "PASS"
        and failure.get("publication_status") == "PASS"
        and failure.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and failure.get("candidate_status") == "FAIL"
        and failure.get("semantic_mismatch_count") == 1352
        and failure.get("verified_passing_case_count") == 15877
        and failure.get("case_execution_denominator") == CASE_COUNT
        and failure.get("suite_count") == WORKER_COUNT
        and failure.get("completed_suite_count") == WORKER_COUNT
        and failure.get("actual_candidate_workers") == WORKER_COUNT
        and failure.get("distinct_worker_process_id_count") == WORKER_COUNT
        and failure.get("named_private_waiver_count") == 13
        and failure.get("corrected_public_adapter_sha256") == ADAPTER_SHA
        and failure.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
        and failure.get("combined_bridge_source_sha256")
        == "1adb6bcecfa0b2fa80403e1c2caf372916466e8b9d0516980e60aef6a9ac08f0"
        and failure.get("combined_bridge_source_bytes") == 178860
        and failure.get("holdout") == "NOT OPENED",
        "preserve the complete independently observed actual V24 FAIL-1352",
    )
    suites = failure.get("suite_integrity")
    need(
        type(suites) is list and len(suites) == WORKER_COUNT
        and all(type(row) is dict and row.get("fully_observed") is True
                for row in suites)
        and sum(row.get("mismatch_count", -1) for row in suites) == 1352
        and sum(row.get("verified_passing_case_count", -1) for row in suites)
        == 15877
        and {
            row["suite"]: row["mismatch_count"] for row in suites
            if row.get("mismatch_count", 0)
        } == {"substitution_v2": 240, "shape_v2": 1112},
        "retain every actual V24 suite and exactly 240 + 1112 failures",
    )


def validate_independent_audit_v4(contract: object, failure: object) -> None:
    need(
        type(contract) is dict
        and contract.get("schema")
        == "rebar-phase2-first-party-runtime-non-delegation-v4"
        and contract.get("version") == 4
        and contract.get("source_freeze", {}).get("source", {}).get("sha256")
        == AUDIT_V4[0][2]
        and contract.get("source_freeze", {}).get("protocol", {}).get("sha256")
        == AUDIT_V4[1][2]
        and contract.get("boundaries", {}).get("runtime_non_delegation")
        == "NOT ESTABLISHED"
        and contract.get("boundaries", {}).get("candidate_qualified") is False
        and contract.get("boundaries", {}).get("holdout") == "NOT OPENED"
        and contract.get("first_party_policy", {}).get(
            "candidate_owned_inspect_tokenize_transitive_re",
        ) == "FORBIDDEN",
        "preserve the immutable strict V4 non-delegation source policy",
    )
    need(
        type(failure) is dict
        and failure.get("schema")
        == "rebar-phase2-first-party-runtime-non-delegation-v4-root-static-audit"
        and failure.get("status") == "FAIL"
        and failure.get("finding_count") == 1
        and failure.get("pushed_source_sha256") == AUDIT_V4[0][2]
        and failure.get("candidate_qualified") is False
        and failure.get("holdout") == "NOT OPENED"
        and failure.get("runtime_non_delegation")
        == "NOT ESTABLISHED; CANDIDATES NEVER EXECUTED"
        and type(failure.get("findings")) is list
        and len(failure["findings"]) == 1
        and failure["findings"][0].get("code")
        == "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE"
        and failure["findings"][0].get("family") == FAMILY
        and failure["findings"][0].get("severity") == "FAIL"
        and failure["findings"][0].get("path")
        == "candidates/rust/py_bridge.c"
        and failure["findings"][0].get("import_chain")
        == ["candidate native bridge", "inspect", "tokenize", "re",
            "re.compile"]
        and failure.get("effects", {}).get("candidate_executions") == 0
        and failure.get("effects", {}).get("candidate_imports") == 0
        and failure.get("effects", {}).get("holdout_reads") == 0,
        "never conceal the independently observed strict V4 FAIL-1 audit",
    )


def validate_receipts(build: dict, root: dict,
                      frozen: dict, previous: dict) -> dict:
    need(type(build) is dict and len(build) == 84
         and type(root) is dict and len(root) == 99
         and type(frozen) is dict and len(frozen) == 25
         and type(previous) is dict and len(previous) == 20,
         "preserve every actual V25 receipt and both complete source freezes")
    for document, schema in ((build,
        "rebar-phase2-owned-rust-capture-clamp-source-build-v25-"
        "durable-publication-receipt"), (root,
        "rebar-phase2-owned-rust-capture-clamp-source-build-v25-"
        "durable-root-provenance-receipt")):
        need(document.get("schema") == schema and document.get("status") == "PASS"
             and document.get("family") == FAMILY
             and document.get("label") == BUILD_LABEL
             and document.get("source_sha256") == BUILD[0][2]
             and document.get("protocol_sha256") == BUILD[1][2]
             and document.get("contract_sha256") == BUILD[2][2]
             and document.get("actual_compiler_process_count") == 28
             and document.get("latest_v22_original_campaign_receipt_sha256")
             == V22_FAILURE_SHA
             and document.get("latest_v22_candidate_status") == "FAIL"
             and document.get("latest_v22_verified_passing_case_count") == 14725
             and document.get("latest_v22_observed_mismatch_lower_bound") == 2018
             and document.get("latest_v22_global_semantic_mismatch_count")
             == NOT_MEASURED
             and document.get("latest_v24_original_campaign_receipt_sha256")
             == V24_FAILURE[2]
             and document.get("latest_v24_candidate_status") == "FAIL"
             and document.get("latest_v24_semantic_mismatch_count") == 1352
             and document.get("latest_v24_verified_passing_case_count") == 15877
             and document.get("expanded_holdout_proposal_case_count")
             == HOLDOUT_CASE_COUNT
             and document.get("native_libraries_loaded") == 0
             and document.get("holdout") == "NOT OPENED",
             "reject stale, forged, delegated, or falsely qualified V25 evidence")
    need(build.get("build_status") == "PASS"
         and build.get("expected_actual_compiler_process_count") == 28
         and build.get("actual_completed_phase_count") == 2
         and build.get("combined_bridge_sha256") == BRIDGE_SOURCE_SHA
         and build.get("combined_bridge_bytes") == BRIDGE_SOURCE_BYTES
         and build.get("combined_bridge_overlay_apply_count") == 2
         and build.get("corrected_public_adapter_sha256") == ADAPTER_SHA
         and build.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
         and build.get("corrected_public_adapter_overlay_apply_count") == 2
         and build.get("archive_sha256") == ARCHIVE_SHA
         and build.get("archive_bytes") == ARCHIVE_BYTES
         and build.get("uncompressed_sha256") == PLAIN_SHA
         and build.get("uncompressed_bytes") == PLAIN_BYTES
         and build.get("candidate_workers_started") == 0
         and build.get("candidate_imports") == 0,
         "reject failed f9 bridge, partial build, package, or fabricated success")
    publication = build.get("archive_publication")
    need(type(publication) is dict and publication.get("sha256") == ARCHIVE_SHA
         and publication.get("bytes") == ARCHIVE_BYTES
         and publication.get("device") == DEVICE
         and publication.get("inode") == ARCHIVE_INODE
         and publication.get("exclusive_creation") is True
         and publication.get("file_fsync_completed") is True,
         "authenticate compressed archive metadata only; never open the archive")
    need(root.get("version") == 25
         and root.get("canonical_build_status") == "PASS"
         and root.get("canonical_build_receipt_relative") == BUILD_RECEIPT[1]
         and root.get("canonical_build_receipt_sha256") == BUILD_RECEIPT[2]
         and root.get("canonical_build_receipt_bytes") == BUILD_RECEIPT[3]
         and root.get("canonical_build_receipt_device") == DEVICE
         and root.get("canonical_build_receipt_inode") == BUILD_RECEIPT[4]
         and root.get("canonical_build_archive_sha256") == ARCHIVE_SHA
         and root.get("canonical_build_archive_bytes") == ARCHIVE_BYTES
         and root.get("canonical_build_archive_opened") is False
         and root.get("materialized_complete_bridge_sha256") == BRIDGE_SOURCE_SHA
         and root.get("materialized_complete_bridge_bytes") == BRIDGE_SOURCE_BYTES
         and root.get("corrected_public_adapter_sha256") == ADAPTER_SHA
         and root.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
         and root.get("actual_source_phase_count") == 2
         and root.get("bridge_overlay_apply_count") == 2
         and root.get("adapter_overlay_apply_count") == 2
         and root.get("cross_phase_complete_engine_elf_byte_identical") is True
         and root.get("cross_phase_complete_bridge_elf_byte_identical") is True
         and root.get("all_original_source_identities_restored") is True
         and root.get("all_original_runtime_target_identities_restored") is True
         and root.get("actual_original_runtime_targets_before")
         == root.get("actual_original_runtime_targets_after")
         and root.get("actual_original_runtime_target_count") == 4
         and root.get("original_source_identity_count") == 9
         and root.get("original_case_execution_denominator") == CASE_COUNT
         and root.get("original_suite_count") == WORKER_COUNT
         and root.get("named_private_waiver_count") == 13
         and root.get("supplemental_differential_case_count")
         == SUPPLEMENTAL_CASE_COUNT
         and root.get("supplemental_counted_in_original_denominator") is False
         and root.get("corrected_reference_case_count")
         == CORRECTED_REFERENCE_CASE_COUNT
         and root.get("corrected_reference_counted_in_original_denominator")
         is False,
         "reject fabricated root provenance, original history, or source identity")
    process_ids = root.get("actual_compiler_process_ids")
    need(type(process_ids) is list and len(process_ids) == 28
         and len(set(process_ids)) == 28
         and all(type(item) is int and item > 0 for item in process_ids),
         "require all 28 genuinely observed independent V25 compiler processes")
    info = root.get("root")
    need(type(info) is dict and info.get("path") == ROOT_PATH
         and info.get("device") == ROOT_DEVICE
         and info.get("inode") == ROOT_INODE and info.get("uid") == os.geteuid()
         and info.get("mode") == "0700" and info.get("phase_count") == 2
         and info.get("directory_scanned") is False,
         "bind only published private-root identity without opening or statting it")
    phases = info.get("phases")
    need(type(phases) is list and len(phases) == 2,
         "require both independently authenticated V24 build phases")
    observed: set[tuple[int, int]] = set()
    for phase_index, name in enumerate(("reference-a", "reference-b")):
        phase = phases[phase_index]
        need(type(phase) is dict and phase.get("name") == name
             and phase.get("absolute_path") == ROOT_PATH + "/" + name
             and phase.get("device") == ROOT_DEVICE
             and phase.get("uid") == os.geteuid()
             and phase.get("mode") == "0700",
             "reject a substituted actual V24 private phase: " + name)
        native = phase.get("native_outputs")
        need(type(native) is list and len(native) == 2,
             "require both full independently reproduced first-party ELF owners")
        for index, expected in enumerate((("engine", ENGINE_SHA, ENGINE_BYTES,
                                           "_rust_engine.so", "0600"),
                                          ("bridge", BRIDGE_SHA, BRIDGE_BYTES,
                                           "_rust_bridge.cpython-314-x86_64-linux-gnu.so",
                                           "0700"))):
            role, fingerprint, count, filename, mode = expected
            item = native[index]
            need(type(item) is dict and item.get("role") == role
                 and item.get("sha256") == fingerprint
                 and item.get("bytes") == count
                 and item.get("file_name") == filename
                 and item.get("absolute_path")
                 == ROOT_PATH + "/" + name + "/native/" + filename
                 and item.get("device") == ROOT_DEVICE
                 and item.get("inode") == PHASE_NATIVE_INODES[phase_index][index]
                 and item.get("mode") == mode and item.get("uid") == os.geteuid()
                 and item.get("nlink") == 1 and item.get("native_loaded") is False,
                 "reject an exchanged V24 phase native owner: " + name + "/" + role)
            identity = (item["device"], item["inode"])
            need(identity not in observed,
                 "reject reused or cross-phase first-party native artifact")
            observed.add(identity)
    outputs = root.get("actual_reproduced_native_outputs")
    need(type(outputs) is dict and set(outputs) == {"engine", "bridge"}
         and len(observed) == 4,
         "reject omitted or cross-candidate actual native output")
    for role, fingerprint, count in (("engine", ENGINE_SHA, ENGINE_BYTES),
                                      ("bridge", BRIDGE_SHA, BRIDGE_BYTES)):
        item = outputs[role]
        audit = item.get("audit") if type(item) is dict else None
        need(type(item) is dict and item.get("sha256") == fingerprint
             and item.get("size_bytes") == count
             and item.get("fresh_independent_inode_count") == 2
             and item.get("reproduced_in_two_fresh_directories") is True
             and type(audit) is dict
             and audit.get("external_regex_dependency_count") == 0
             and audit.get("cross_family_dependency_count") == 0,
             "reject external, delegated, or substituted first-party " + role)
    need(frozen.get("schema")
         == "rebar-phase2-owned-rust-capture-clamp-source-build-v25-"
            "source-freeze"
         and frozen.get("version") == 25 and frozen.get("family") == FAMILY
         and frozen.get("source", {}).get("sha256") == BUILD[0][2]
         and frozen.get("protocol", {}).get("sha256") == BUILD[1][2]
         and frozen.get("immutable_complete_v23_correctness_campaign", {})
             .get("complete_contract_sha256") == V23[2][2]
         and frozen.get("immutable_complete_v23_correctness_campaign", {})
             .get("complete_contract_authenticated") is True
         and len(previous) == frozen.get(
             "immutable_complete_v23_correctness_campaign", {},
         ).get("complete_contract_field_count")
         and frozen.get("immutable_complete_v24_actual_candidate_failure", {})
             .get("receipt_sha256") == V24_FAILURE[2]
         and frozen.get("immutable_complete_v24_actual_candidate_failure", {})
             .get("candidate_status") == "FAIL"
         and frozen.get("immutable_complete_v24_actual_candidate_failure", {})
             .get("semantic_mismatch_count") == 1352
         and frozen.get("immutable_operational_runtime_guard_v4", {})
             .get("complete_contract_sha256") == GUARD_V4[2][2]
         and frozen.get("materialized_first_party_variant", {})
             .get("complete_source_sha256") == BRIDGE_SOURCE_SHA
         and frozen.get("materialized_first_party_variant", {})
             .get("complete_source_bytes") == BRIDGE_SOURCE_BYTES
         and frozen.get("frozen_offline_dual_phase_build", {})
             .get("external_cargo_dependency_count") == 0,
         "preserve complete V25 build freeze, V24 FAIL, and V23 ancestry")
    return {"phase_count": 2, "native_artifact_count": 4,
            "process_ids": list(process_ids)}


def frozen_contract(source_row: tuple, protocol_row: tuple, previous: dict,
                    build_frozen: dict, build: dict, root: dict,
                    v4: dict, previous_v24: dict, actual_v24_failure: dict,
                    audit_v4: dict, audit_failure: dict) -> dict:
    historic = previous["immutable_previous_v22_campaign"]
    failure = previous["immutable_actual_v22_failure"]
    old = previous["immutable_actual_v20_failure"]
    complete_v22 = historic["complete_frozen_source_contract"]
    suites = previous["frozen_original_correctness"]["suites"]
    need(len(complete_v22) == 435
         and historic.get("complete_inherited_v21_contract_field_count") == 402
         and failure.get("complete_receipt_field_count") == 96
         and failure.get("receipt_sha256") == V22_FAILURE_SHA
         and failure.get("verified_passing_case_count") == 14725
         and failure.get("fully_observed_mismatch_lower_bound") == 2018
         and failure.get("global_semantic_mismatch_count") == NOT_MEASURED
         and failure.get("actual_failing_worker_pid") == 188
         and failure.get("actual_failing_worker_candidate_imports") == 1
         and failure.get("actual_failing_worker_native_library_loads") == 2
         and failure.get("actual_failing_worker_remaining_interpreter_warnings") == 1
         and failure.get("actual_failing_worker_destructor_warnings") == 16
         and failure.get("actual_failing_worker_successfully_returned_child_interpreters") == 0
         and failure.get("actual_failing_worker_installed_child_guards") == 0
         and failure.get("actual_failing_worker_recorded_case_interpreter_exec_calls") == 0
         and failure.get("actual_failing_worker_transient_native_child_creation")
         == NOT_MEASURED
         and old.get("verified_passing_case_count") == 15749
         and old.get("global_semantic_mismatch_count") == NOT_MEASURED,
         "never erase or inflate any genuine historical V22/V21/V20 outcome")
    need(type(suites) is list and len(suites) == WORKER_COUNT
         and sum(item["case_execution_denominator"] for item in suites)
         == CASE_COUNT and len(complete_v22["named_private_waivers"]) == 13,
         "preserve exact original suite denominator and named private waivers")
    return {
        "schema": SCHEMA + "-recoverable-source-freeze",
        "status": "SOURCE FROZEN; V25 BUILD PASS; ORIGINAL CAMPAIGN NOT RUN",
        "version": VERSION, "family": FAMILY, "goal_sha256": GOAL_SHA,
        "source": owner_document(source_row),
        "protocol": owner_document(protocol_row),
        "immutable_previous_v23_campaign": {
            "owners": [owner_document(item) for item in V23],
            "complete_contract_sha256": V23[2][2],
            "complete_top_level_field_count": 20,
            "complete_v22_contract_sha256": V22[2][2],
            "complete_v22_contract_field_count": 435,
            "complete_v21_inherited_contract_field_count": 402,
            "source_mode_controller_executed": True,
            "actual_mode_controller_dispatched": False,
        },
        "immutable_actual_v22_failure": {
            "receipt_sha256": V22_FAILURE_SHA,
            "complete_receipt_field_count": 96,
            "candidate_status": "FAIL", "publication_status": "PASS",
            "actual_candidate_workers": 13, "completed_suite_count": 12,
            "verified_passing_case_count": 14725,
            "fully_observed_mismatch_lower_bound": 2018,
            "fully_observed_suite_mismatch_counts":
                dict(failure["fully_observed_suite_mismatch_counts"]),
            "global_semantic_mismatch_count": NOT_MEASURED,
            "failing_worker_pid": 188,
            "failing_worker_candidate_imports": 1,
            "failing_worker_native_library_loads": 2,
            "failing_worker_successfully_returned_children": 0,
            "failing_worker_installed_child_guards": 0,
            "failing_worker_case_interpreter_exec_calls": 0,
            "failing_worker_transient_native_child_creation": NOT_MEASURED,
            "remaining_interpreter_warning_count": 1,
            "destructor_warning_count": 16,
            "earlier_v20_verified_passing_case_count": 15749,
            "earlier_v20_global_semantic_mismatch_count": NOT_MEASURED,
        },
        "immutable_previous_v24_correctness_campaign": {
            "owners": [owner_document(item) for item in PREVIOUS_V24],
            "complete_contract_sha256": PREVIOUS_V24[2][2],
            "complete_contract_field_count": len(previous_v24),
            "complete_contract_authenticated": True,
            "actual_campaign_executed": True,
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 1352,
            "verified_passing_case_count": 15877,
            "candidate_worker_count": 13,
            "completed_suite_count": 13,
            "case_execution_denominator": CASE_COUNT,
        },
        "immutable_actual_v24_candidate_failure": {
            "owner": owner_document(V24_FAILURE),
            "complete_receipt": actual_v24_failure,
            "complete_receipt_field_count": 96,
            "receipt_sha256": V24_FAILURE[2],
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 1352,
            "verified_passing_case_count": 15877,
            "fully_observed_suite_mismatch_counts": {
                "substitution_v2": 240,
                "shape_v2": 1112,
            },
            "actual_candidate_workers": 13,
            "completed_suite_count": 13,
            "all_observation_vectors_complete": True,
        },
        "independent_runtime_non_delegation_v4_audit": {
            "owners": [owner_document(item) for item in AUDIT_V4],
            "complete_frozen_source_contract": audit_v4,
            "actual_failure_receipt_owner": owner_document(AUDIT_V4_FAILURE),
            "complete_actual_failure_receipt": audit_failure,
            "status": "FAIL",
            "finding_count": 1,
            "finding_code": "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE",
            "candidate_owned_import_chain": [
                "candidate native bridge", "inspect", "tokenize", "re",
                "re.compile",
            ],
            "public_matching_delegation": "NOT PROVEN",
            "candidate_qualified": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "audit_is_separate_from_original_correctness": True,
        },
        "actual_v25_native_build": {
            "owners": [owner_document(item) for item in BUILD],
            "complete_contract_sha256": BUILD[2][2],
            "complete_contract_field_count": len(build_frozen),
            "publication_receipt": owner_document(BUILD_RECEIPT),
            "root_provenance_receipt": owner_document(ROOT_RECEIPT),
            "build_status": "PASS", "label": BUILD_LABEL,
            "actual_compiler_process_count": 28,
            "actual_compiler_process_ids":
                list(root["actual_compiler_process_ids"]),
            "independent_private_phase_count": 2,
            "independent_native_artifact_count": 4,
            "private_root_path": ROOT_PATH,
            "private_root_device": ROOT_DEVICE,
            "private_root_inode": ROOT_INODE,
            "private_root_provenance":
                "AUTHENTICATED COMPLETE PUBLIC ROOT RECEIPT ONLY; NOT OPENED",
            "phase_native_inodes": [list(row) for row in PHASE_NATIVE_INODES],
            "native_engine_sha256": ENGINE_SHA,
            "native_engine_bytes": ENGINE_BYTES,
            "native_bridge_sha256": BRIDGE_SHA,
            "native_bridge_bytes": BRIDGE_BYTES,
            "corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA,
            "corrected_bridge_source_bytes": BRIDGE_SOURCE_BYTES,
            "corrected_public_adapter_sha256": ADAPTER_SHA,
            "corrected_public_adapter_bytes": ADAPTER_BYTES,
            "bridge_overlay_apply_count": 2,
            "adapter_overlay_apply_count": 2,
            "archive_sha256_metadata_only": ARCHIVE_SHA,
            "archive_bytes_metadata_only": ARCHIVE_BYTES,
            "archive_inode_metadata_only": ARCHIVE_INODE,
            "archive_opened": False,
            "external_cargo_dependency_count": 0,
            "external_regular_expression_engine": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
        },
        "operational_runtime_guard_v4": {
            "owners": [owner_document(item) for item in GUARD_V4],
            "complete_contract_sha256": GUARD_V4[2][2],
            "version": 4,
            "immutable_historical_v3_source_sha256": V3[0][1],
            "immutable_historical_v3_protocol_sha256": V3[1][1],
            "immutable_historical_v3_contract_sha256": V3[2][1],
            "immutable_v2_prepare_family_identity": "EXACT ORIGINAL FUNCTION AND GLOBALS",
            "immutable_v5_producer_identity": "EXACT UNCHANGED OWNED PRODUCER",
            "guard_installed_before_candidate_import": True,
            "native_owner_required_field_count": 14,
            "stdlib_re_engine": "FORBIDDEN",
            "stdlib_sre_engine": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "expected_child_interpreters_created": 11,
            "expected_child_interpreters_destroyed": 11,
            "expected_original_case_interpreter_exec_calls": 394,
            "expected_bootstrap_interpreter_exec_calls": 11,
            "expected_cleanup_interpreter_exec_calls": 11,
            "expected_total_real_interpreter_exec_calls": 416,
            "actual_child_interpreters_created": 0,
            "actual_child_interpreters_destroyed": 0,
            "actual_original_case_interpreter_exec_calls": 0,
            "actual_total_real_interpreter_exec_calls": 0,
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "original_correctness_boundary": {
            "case_execution_denominator": CASE_COUNT,
            "suite_count": WORKER_COUNT,
            "suites": [dict(row) for row in suites],
            "named_private_waiver_count": 13,
            "named_private_waivers": list(complete_v22["named_private_waivers"]),
            "supplemental_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
            "supplemental_counted_in_original_denominator": False,
            "corrected_reference_case_count": CORRECTED_REFERENCE_CASE_COUNT,
            "corrected_reference_counted_in_original_denominator": False,
            "candidate_correctness": NOT_MEASURED,
            "candidate_semantic_mismatch_count": NOT_MEASURED,
            "candidate_verified_passing_case_count": NOT_MEASURED,
            "candidate_qualified": False,
        },
        "actual_entry_policy": {
            "run": "IMPLEMENTED; ROOT AUTHORIZATION REQUIRED; NOT RUN",
            "worker": "IMPLEMENTED; ROOT AUTHORIZATION REQUIRED; NOT RUN",
            "recover": "IMPLEMENTED; ROOT AUTHORIZATION REQUIRED; NOT RUN",
            "actual_modes_install_public_source_wall": False,
            "source_modes_install_public_wall_before_first_predecessor": True,
            "historical_v21_globals_preserved_before_migration": True,
            "v25_migration_has_separate_authenticated_namespace": True,
            "activation_label": LABEL,
            "activation_root": RECOVERY_ROOT,
            "recovery_lock_filename": LOCK_NAME,
            "recovery_role_order": list(complete_v22["recovery_role_order"]),
            "recovery_restoration_order":
                list(complete_v22["recovery_restoration_order"]),
            "source_wall_scope": "SOURCE MODES ONLY; NEVER ACTUAL ENTRY",
            "requires_complete_v25_build_receipt": True,
            "requires_complete_v25_root_receipt": True,
            "requires_independently_pinned_v4_guard": True,
            "requires_complete_v24_failure_receipt": True,
            "requires_complete_v4_independent_nondelegation_failure": True,
            "requires_all_original_native_owner_fields": True,
        },
        "source_only_effects": {
            "candidate_imports": 0, "candidate_workers_started": 0,
            "reference_workers_started": 0, "compiler_processes_started": 0,
            "native_libraries_loaded": 0, "native_binary_files_opened": 0,
            "native_binary_metadata_probes": 0, "private_roots_opened": 0,
            "private_roots_statted": 0, "compressed_archives_opened": 0,
            "compressed_archives_inflated": 0, "threads_started": 0,
            "subinterpreters_created": 0, "clock_samples": 0,
            "network_requests": 0, "hidden_cases_read": 0,
            "holdout_cases_opened": 0, "timing_trials_run": 0,
            "holdout": "NOT OPENED", "expanded_holdout_proposal_case_count":
                HOLDOUT_CASE_COUNT,
            "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
            "candidate_correctness": NOT_MEASURED,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": NOT_MEASURED, "memory": NOT_MEASURED,
            "confidence_intervals": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "qualified_candidate_count": 0, "winner_selected": False,
        },
    }


def load_source_context(wall: PublicSourceWall, options: dict,
                        rendering: bool) -> tuple[dict, dict]:
    source = dynamic_owner(wall, "source", SOURCE, options["source_sha256"])
    protocol = dynamic_owner(wall, "protocol", PROTOCOL,
                             options["protocol_sha256"])
    secure_owner(wall, source)
    secure_owner(wall, protocol)
    if not rendering:
        current = dynamic_owner(wall, "contract", CONTRACT,
                                options["contract_sha256"])
    else:
        current = None
    for key, row in zip(("guard_v4_source_sha256", "guard_v4_protocol_sha256",
                         "guard_v4_contract_sha256"), GUARD_V4, strict=True):
        need(options.get(key) == row[2],
             "require independently caller-pinned genuine V4 guard: " + key)
    previous, historical, state = previous_v23(wall)
    capture, semantic = state["capture"], state["semantic"]
    raw_v4 = {item[0]: secure_owner(wall, item) for item in GUARD_V4}
    guard = validate_v4_guard(strict_document(
        capture, semantic, raw_v4["guard_v4_contract"],
        "complete exact operational V4 guard contract",
    ))
    for row in BUILD:
        secure_owner(wall, row)
    build_frozen = strict_document(capture, semantic, secure_owner(wall, BUILD[2]),
                                   "complete exact V24 native source-build freeze")
    build_receipt = strict_document(capture, semantic,
                                    secure_owner(wall, BUILD_RECEIPT),
                                    "complete successful V24 public build receipt")
    root_receipt = strict_document(capture, semantic,
                                   secure_owner(wall, ROOT_RECEIPT),
                                   "complete successful V24 public root receipt")
    for row in PREVIOUS_V24:
        secure_owner(wall, row)
    previous_v24 = strict_document(
        capture, semantic, secure_owner(wall, PREVIOUS_V24[2]),
        "complete independently frozen original V24 correctness campaign",
    )
    actual_v24_failure = strict_document(
        capture, semantic, secure_owner(wall, V24_FAILURE),
        "complete independently observed actual original V24 FAIL-1352",
    )
    validate_previous_v24_failure(previous_v24, actual_v24_failure)
    for row in AUDIT_V4:
        secure_owner(wall, row)
    audit_v4 = semantic.StrictJSON(secure_owner(wall, AUDIT_V4[2])).decode()
    need(type(audit_v4) is dict,
         "decode the exactly hash-pinned pretty-printed V4 audit contract")
    audit_failure = strict_document(
        capture, semantic, secure_owner(wall, AUDIT_V4_FAILURE),
        "complete independently root-observed runtime non-delegation FAIL-1",
    )
    validate_independent_audit_v4(audit_v4, audit_failure)
    proof = validate_receipts(build_receipt, root_receipt,
                              build_frozen, historical)
    contract = frozen_contract(source, protocol, historical,
                               build_frozen, build_receipt, root_receipt, guard,
                               previous_v24, actual_v24_failure,
                               audit_v4, audit_failure)
    if current is not None:
        raw = secure_owner(wall, current)
        need(strict_document(capture, semantic, raw,
                             "complete exact V24 original correctness contract")
             == contract,
             "reject missing, altered, or additional V24 campaign obligations")
    need(not wall.live, "close every authenticated public source descriptor")
    no_matching_imports()
    return contract, {
        "previous": previous, "historical": historical, "v23_state": state,
        "capture": capture, "semantic": semantic, "guard_v4": guard,
        "build_frozen": build_frozen, "build": build_receipt,
        "root": root_receipt, "proof": proof,
        "previous_v24": previous_v24,
        "actual_v24_failure": actual_v24_failure,
        "audit_v4": audit_v4,
        "audit_v4_failure": audit_failure,
    }


def different(value: object) -> object:
    if value is None:
        return "HOSTILE NON-NULL VALUE"
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + "-HOSTILE"
    if type(value) is list:
        return [*value, "HOSTILE EXTRA ITEM"]
    if type(value) is dict:
        return {**value, "__hostile_v24_extra_field__": True}
    raise CampaignError("reject unsupported frozen JSON mutation")


def reject(action: object, label: str, *kinds: type) -> str:
    need(callable(action), "require an executable genuine source-only control")
    try:
        action()
    except (CampaignError, OSError, ValueError, TypeError, KeyError,
            IndexError, UnicodeError, OverflowError, *kinds):
        return label
    raise CampaignError("accepted hostile first-party V24 authority: " + label)


def source_controls(wall: PublicSourceWall, context: dict,
                    state: dict) -> list[str]:
    previous, previous_context = state["previous"], state["historical"]
    capture, semantic = state["capture"], state["semantic"]
    kinds = (previous.FreezeError, capture.FreezeError, semantic.FreezeError)
    inherited = previous.self_test(wall, previous_context, state["v23_state"])
    need(type(inherited) is list and len(inherited) >= 1280,
         "retain all complete V23/V22/V21 and V2 hostile controls")
    controls = list(inherited)
    campaign = state["v23_state"]["campaign"]
    actual = state["v23_state"]["actual"]
    for key in sorted(campaign):
        altered = dict(campaign)
        altered[key] = different(altered[key])
        controls.append(reject(
            lambda value=altered: previous.validate_exact_campaign(
                capture, semantic, value, campaign),
            "reject-altered-complete-v22-obligation-" + key, *kinds))
    for key in sorted(actual):
        missing = dict(actual)
        missing.pop(key)
        controls.append(reject(
            lambda value=missing: previous.validate_exact_actual(
                capture, semantic, value, actual),
            "reject-missing-complete-genuine-v22-failure-" + key, *kinds))
    build, root = state["build"], state["root"]
    for key in sorted(build):
        missing = dict(build)
        missing.pop(key)
        controls.append(reject(
            lambda value=missing: validate_receipts(
                value, root, state["build_frozen"], previous_context),
            "reject-missing-complete-v24-build-receipt-" + key, *kinds))
    for key in sorted(root):
        altered = dict(root)
        altered[key] = different(altered[key])
        controls.append(reject(
            lambda value=altered: (
                validate_complete_contract(capture, semantic, value, root),
                validate_receipts(build, value, state["build_frozen"],
                                  previous_context),
            ),
            "reject-altered-complete-v24-root-receipt-" + key, *kinds))
    previous_v24, actual_v24 = state["previous_v24"], state["actual_v24_failure"]
    for key in sorted(actual_v24):
        missing = dict(actual_v24)
        missing.pop(key)
        controls.append(reject(
            lambda value=missing: (
                validate_complete_contract(capture, semantic, value, actual_v24),
                validate_previous_v24_failure(previous_v24, value),
            ),
            "reject-missing-complete-v24-failure-receipt-" + key,
            *kinds,
        ))
        changed = dict(actual_v24)
        changed[key] = different(changed[key])
        controls.append(reject(
            lambda value=changed: validate_complete_contract(
                capture, semantic, value, actual_v24,
            ),
            "reject-changed-complete-v24-failure-receipt-" + key,
            *kinds,
        ))
    audit_contract = state["audit_v4"]
    audit_failure = state["audit_v4_failure"]
    for key in sorted(audit_failure):
        changed = dict(audit_failure)
        changed[key] = different(changed[key])
        controls.append(reject(
            lambda value=changed: validate_complete_contract(
                capture, semantic, value, audit_failure,
            ),
            "reject-changed-complete-nondelegation-v4-failure-" + key,
            *kinds,
        ))
    for field, value, label in (
        ("status", "PASS", "independent-nondelegation-fail-as-pass"),
        ("finding_count", 0, "erased-independent-nondelegation-finding"),
        ("candidate_qualified", True,
         "qualified-candidate-despite-independent-nondelegation-fail"),
    ):
        forged = dict(audit_failure)
        forged[field] = value
        controls.append(reject(
            lambda item=forged: validate_independent_audit_v4(
                audit_contract, item,
            ),
            "reject-" + label,
            *kinds,
        ))
    for index, key, value in (
        (0, "sha256", FAILED_BRIDGE_SOURCE_SHA),
        (0, "bytes", BRIDGE_SOURCE_BYTES + 287),
        (1, "sha256", "0" * 64),
        (1, "bytes", ADAPTER_BYTES + 1),
    ):
        forged = dict(build)
        actual_key = ("combined_bridge_" if index == 0 else
                      "corrected_public_adapter_") + key
        forged[actual_key] = value
        controls.append(reject(
            lambda item=forged: validate_receipts(
                item, root, state["build_frozen"], previous_context),
            "reject-stale-or-forged-corrected-overlay-" + actual_key, *kinds))
    guard = state["guard_v4"]
    for key in sorted(guard):
        missing = dict(guard)
        missing.pop(key)
        controls.append(reject(lambda item=missing: validate_v4_guard(item),
                               "reject-missing-complete-v4-guard-" + key,
                               *kinds))
    for key in ("stdlib_re_engine", "stdlib_sre_engine",
                "external_regex_package", "cross_candidate_engine",
                "matching_fallback"):
        forged = capture.clone(semantic, guard)
        forged["runtime_isolation_policy"][key] = "ALLOWED"
        controls.append(reject(lambda item=forged: validate_v4_guard(item),
                               "reject-weakened-v4-zero-delegation-" + key,
                               *kinds))
    for relative, label in (
        ("candidates/rust_candidate.py", "candidate-adapter"),
        ("candidates/rust/py_bridge.c", "candidate-bridge-source"),
        ("candidates/_rust_engine.so", "installed-native-engine"),
        ("candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
         "installed-native-bridge"),
        ("oracle/phase3/expanded-sealed-holdout-v2.json", "sealed-holdout"),
        ("oracle/phase2/evidence/native-source-build-v25-rust-"
         "phase2-v25-rust-capture-clamp-v1-root-provenance.json.gz", "archive"),
    ):
        controls.append(reject(
            lambda path=ROOT + "/" + relative:
                os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)),
            "reject-physical-v24-source-only-" + label, *kinds))
    controls.append(reject(lambda: os.stat(ROOT_PATH, follow_symlinks=False),
                           "reject-source-only-private-root-metadata", *kinds))
    controls.append(reject(lambda: time.time(),
                           "reject-source-only-correctness-clock", *kinds))
    for key in sorted(context):
        candidate = dict(context)
        candidate[key] = different(candidate[key])
        controls.append(reject(
            lambda item=candidate: validate_complete_contract(
                capture, semantic, item, context),
            "reject-altered-complete-v24-frozen-section-" + key, *kinds))
    need(wall.installed and not wall.live and bool(wall.blocked)
         and len(controls) > len(inherited) + 600,
         "require complete physically sterile inherited V24 hostile controls")
    no_matching_imports()
    return controls


def validate_complete_contract(capture: types.ModuleType,
                               semantic: types.ModuleType,
                               actual: dict, expected: dict) -> None:
    need(type(actual) is dict and set(actual) == set(expected)
         and capture.canonical_document(semantic, actual)
         == capture.canonical_document(semantic, expected),
         "reject omitted, additional, or changed complete V24 freeze")


def legacy_row(row: tuple) -> tuple:
    need(type(row) is tuple and len(row) == 5,
         "require one exact legacy-compatible immutable owner")
    return row[1], row[2], row[3], row[4]


def migrate_parent(previous: types.ModuleType, owner: tuple) -> types.ModuleType:
    raw = previous.secure_owner(owner)
    tree = ast.parse(raw, filename=owner[0])

    class ExactV25Literals(ast.NodeTransformer):
        def __init__(self) -> None:
            self.count = 0

        def visit_Constant(self, node: ast.Constant) -> ast.AST:
            if type(node.value) is str and (
                    "v21" in node.value or "V21" in node.value):
                self.count += 1
                return ast.copy_location(ast.Constant(
                    value=node.value.replace("v21", "v25")
                                    .replace("V21", "V25")), node)
            return node

    migration = ExactV25Literals()
    tree = migration.visit(tree)
    need(migration.count >= 20,
         "retain exact authenticated V21-to-V25 original runner migration")
    module = types.ModuleType("_rebar_v25_independently_migrated_original_parent")
    module.__file__ = ROOT + "/" + owner[0]
    module._v25_literal_migration_count = migration.count
    exec(compile(ast.fix_missing_locations(tree), module.__file__, "exec",
                 dont_inherit=True), module.__dict__)
    return module


def canonical_native_owner(owner: dict, role: str) -> dict:
    keys = frozenset(("role", "family", "absolute_path", "relative", "file_name",
                      "sha256", "bytes", "size_bytes", "device", "inode", "mode",
                      "uid", "nlink", "native_loaded"))
    expected_sha = BRIDGE_SHA if role == "bridge" else ENGINE_SHA
    expected_bytes = BRIDGE_BYTES if role == "bridge" else ENGINE_BYTES
    need(type(owner) is dict and set(owner) == keys
         and role in ("bridge", "engine") and owner.get("role") == role
         and owner.get("family") == FAMILY and owner.get("sha256") == expected_sha
         and owner.get("bytes") == expected_bytes
         and owner.get("size_bytes") == expected_bytes
         and owner.get("absolute_path") == ROOT + "/" + str(owner.get("relative"))
         and type(owner.get("relative")) is str
         and owner["relative"].startswith("candidates/")
         and ".." not in owner["relative"].split("/")
         and owner.get("device") == DEVICE
         and type(owner.get("inode")) is int and owner["inode"] > 0
         and owner.get("mode") == 0o600 and owner.get("uid") == os.geteuid()
         and owner.get("nlink") == 1 and owner.get("native_loaded") is False,
         "reject stale, preloaded, external, or noncanonical native " + role)
    return owner


def operational_v4_guard(previous: types.ModuleType,
                         old_state: dict) -> types.ModuleType:
    raw = secure_owner(None, GUARD_V4[0])
    secure_owner(None, GUARD_V4[1])
    secure_owner(None, GUARD_V4[2])
    name = "_rebar_v24_authenticated_operational_guard_v4"
    need(name not in sys.modules,
         "reject a reused or substituted operational V4 guard namespace")
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + GUARD_V4[0][1]
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True),
             module.__dict__)
        old_base = old_state["original_base"]
        need(module.SELF == GUARD_V4[0][1]
             and module.PROTOCOL == GUARD_V4[1][1]
             and module.CONTRACT == GUARD_V4[2][1]
             and type(module.RuntimePolicy) is type
             and module.RuntimePolicy.__bases__ == (module.PREVIOUS.RuntimePolicy,)
             and module.PREVIOUS.SELF == V3[0][0]
             and tuple(module.PREVIOUS.V2["source"]) == tuple(old_base.GUARD[0])
             and module.RuntimePolicy.prepare_family
             is module.BASE.RuntimePolicy.prepare_family
             and module.RuntimePolicy.prepare_family.__globals__
             is module.BASE.__dict__
             and module.child_bootstrap_source is module.BASE.child_bootstrap_source
             and module.verify_child_contract is module.BASE.verify_child_contract,
             "preserve exact V4 subclass and immutable V2/V5 child identity")
        return module
    except BaseException:
        sys.modules.pop(name, None)
        raise


def build_v24_parent(v22: types.ModuleType, previous: types.ModuleType,
                     old_state: dict, build: dict, root: dict,
                     freeze: dict, operational: types.ModuleType) -> dict:
    loaded = old_state["loaded"]
    ancestor = loaded["ancestor"]
    original_parent = loaded["state"]["parent"]
    original_base = loaded["state"]["original_base"]
    parent = migrate_parent(previous, ancestor.V17[0])
    corrected = tuple((path, BRIDGE_SOURCE_SHA, BRIDGE_SOURCE_BYTES)
                      if path == "candidates/rust/py_bridge.c"
                      else (path, ADAPTER_SHA, ADAPTER_BYTES)
                      if path == "candidates/rust_candidate.py"
                      else (path, fingerprint, count)
                      for path, fingerprint, count
                      in tuple(loaded["parent"].CORRECTED_SOURCES))
    values = {
        "SOURCE": SOURCE, "PROTOCOL": PROTOCOL, "CONTRACT": CONTRACT,
        "SCHEMA": SCHEMA, "VERSION": VERSION, "FAMILY": FAMILY,
        "BUILD_LABEL": BUILD_LABEL, "BUILD_SUFFIX": BUILD_SUFFIX,
        "LABEL": LABEL, "RECOVERY_PREFIX": RECOVERY_PREFIX,
        "RECOVERY_ROOT": RECOVERY_ROOT,
        "V21": tuple(legacy_row(row) for row in BUILD),
        "V21_PUBLICATION": legacy_row(BUILD_RECEIPT),
        "V21_ROOT": legacy_row(ROOT_RECEIPT),
        "ROOT_DEVICE": ROOT_DEVICE, "ROOT_INODE": ROOT_INODE,
        "ROOT_PATH": ROOT_PATH, "ENGINE_SHA": ENGINE_SHA,
        "ENGINE_BYTES": ENGINE_BYTES, "BRIDGE_SHA": BRIDGE_SHA,
        "BRIDGE_BYTES": BRIDGE_BYTES, "CAPTURE_SHA": BRIDGE_SOURCE_SHA,
        "CAPTURE_BYTES": BRIDGE_SOURCE_BYTES,
        "ADAPTER_SHA": ADAPTER_SHA, "ADAPTER_BYTES": ADAPTER_BYTES,
        "ARCHIVE_SHA": ARCHIVE_SHA, "ARCHIVE_BYTES": ARCHIVE_BYTES,
        "ARCHIVE_INODE": ARCHIVE_INODE, "PLAIN_SHA": PLAIN_SHA,
        "PLAIN_BYTES": PLAIN_BYTES,
        "PHASE_NATIVE_INODES": PHASE_NATIVE_INODES,
        "CORRECTED_SOURCES": corrected,
    }
    for key, value in values.items():
        setattr(parent, key, value)

    def validate(actual_build: dict, actual_root: dict,
                 actual_freeze: dict) -> dict:
        return validate_receipts(actual_build, actual_root,
                                 actual_freeze, old_state["v23_contract"])

    parent.validate_v21_documents = validate
    base = parent.make_v21_base(original_parent, original_base,
                                build, root, freeze)
    need(tuple(base.GUARD) == tuple(original_base.GUARD)
         and base.BUILD == tuple(legacy_row(row) for row in BUILD)
         and base.BUILD_RECEIPT == legacy_row(BUILD_RECEIPT)
         and base.ROOT_RECEIPT == legacy_row(ROOT_RECEIPT)
         and base.BUILD_LABEL == BUILD_LABEL and base.ROOT_PATH == ROOT_PATH
         and base.ROOT_DEVICE == ROOT_DEVICE and base.ROOT_INODE == ROOT_INODE
         and base.ENGINE_SHA == ENGINE_SHA and base.ENGINE_BYTES == ENGINE_BYTES
         and base.BRIDGE_SHA == BRIDGE_SHA and base.BRIDGE_BYTES == BRIDGE_BYTES
         and base.CORRECTED_ADAPTER_SHA == ADAPTER_SHA
         and base.CORRECTED_ADAPTER_BYTES == ADAPTER_BYTES
         and tuple(base.P0) == tuple(original_base.P0)
         and tuple(base.PRODUCER) == tuple(original_base.PRODUCER)
         and tuple(base.ROLE_ORDER) == tuple(original_base.ROLE_ORDER),
         "reject stale V22/f9 native base, V2/V5 child guard, or original roles")
    base.load_guard = lambda: operational
    original_install = base.install_worker_guard

    def exact_guard_install(guard: types.ModuleType) -> dict:
        need(guard is operational,
             "install only independently pinned operational V4 before Rust")
        bundle = original_install(guard)
        need(type(bundle) is dict and type(bundle.get("policy"))
             is operational.RuntimePolicy
             and bundle["policy"].installed is True
             and bundle.get("candidate") is sys.modules.get("re")
             and bundle.get("candidate")
             is sys.modules.get("candidates.rust_candidate")
             and "_sre" not in sys.modules and "ctypes" not in sys.modules,
             "install genuine V4 before exactly one selected Rust adapter import")
        for role in ("bridge", "engine"):
            expected = canonical_native_owner(bundle[role], role)
            need(bundle[role] == expected
                 and getattr(bundle["policy"], role + "_owner") == expected,
                 "prepare only exact immutable fourteen-field V4 native " + role)
        bundle["policy"].check_modules()
        return bundle

    base.install_worker_guard = exact_guard_install
    runner = parent.make_runner(original_parent)
    need(runner.SOURCE == SOURCE and runner.PROTOCOL == PROTOCOL
         and runner.CONTRACT == CONTRACT and runner.SCHEMA == SCHEMA
         and runner.LABEL == LABEL and runner.RECOVERY_PREFIX == RECOVERY_PREFIX
         and runner.RECOVERY_ROOT == RECOVERY_ROOT
         and tuple(runner.SUITES) == tuple(previous.SUITES)
         and runner.WORKER_COUNT == WORKER_COUNT
         and runner.CASE_COUNT == CASE_COUNT,
         "migrate exact unchanged 13-worker original V16 controller to V24")
    inherited = runner.actual_required_authority

    def required(actual_base: types.ModuleType) -> dict[str, str]:
        result = dict(inherited(actual_base))
        result.update({
            "combined_bridge_sha256": BRIDGE_SOURCE_SHA,
            "combined_bridge_bytes": str(BRIDGE_SOURCE_BYTES),
            "guard_v4_source_sha256": GUARD_V4[0][2],
            "guard_v4_protocol_sha256": GUARD_V4[1][2],
            "guard_v4_contract_sha256": GUARD_V4[2][2],
            "operational_guard_v3_source_sha256": V3[0][1],
            "operational_guard_v3_protocol_sha256": V3[1][1],
            "operational_guard_v3_contract_sha256": V3[2][1],
            "previous_v22_source_sha256": V22[0][2],
            "previous_v22_protocol_sha256": V22[1][2],
            "previous_v22_contract_sha256": V22[2][2],
            "previous_v22_failure_receipt_sha256": V22_FAILURE_SHA,
            "previous_v23_source_sha256": V23[0][2],
            "previous_v23_protocol_sha256": V23[1][2],
            "previous_v23_contract_sha256": V23[2][2],
            "previous_v24_source_sha256": PREVIOUS_V24[0][2],
            "previous_v24_protocol_sha256": PREVIOUS_V24[1][2],
            "previous_v24_contract_sha256": PREVIOUS_V24[2][2],
            "previous_v24_failure_receipt_sha256": V24_FAILURE[2],
            "independent_nondelegation_v4_source_sha256": AUDIT_V4[0][2],
            "independent_nondelegation_v4_protocol_sha256": AUDIT_V4[1][2],
            "independent_nondelegation_v4_contract_sha256": AUDIT_V4[2][2],
            "independent_nondelegation_v4_failure_receipt_sha256":
                AUDIT_V4_FAILURE[2],
            "previous_v21_preactivation_failure_receipt_sha256": V21_FAILURE_SHA,
        })
        return result

    runner.actual_required_authority = required
    runner.bounded_diagnostic_traceback = previous.bounded_unicode_traceback
    history = previous.bootstrap(loaded["module"].V19[0],
                                 "_rebar_v24_authenticated_historical_v19")
    helper = previous.bootstrap(previous.V20[0],
                                "_rebar_v24_exact_historical_v20_observer")
    for module in (history, helper):
        for name, value in (("SCHEMA", SCHEMA), ("VERSION", VERSION),
                            ("SOURCE", SOURCE), ("PROTOCOL", PROTOCOL),
                            ("CONTRACT", CONTRACT), ("BUILD_LABEL", BUILD_LABEL),
                            ("BUILD_SUFFIX", BUILD_SUFFIX), ("LABEL", LABEL),
                            ("RECOVERY_PREFIX", RECOVERY_PREFIX),
                            ("RECOVERY_ROOT", RECOVERY_ROOT)):
            setattr(module, name, value)
    inherited_bind = helper.corrected_controller(history, parent,
                                                 loaded["history"])

    def bind(actual_state: dict, context: dict, bundle: dict | None,
             counts: dict[str, int]) -> types.ModuleType:
        legacy = inherited_bind(actual_state, context, bundle, counts)
        need(legacy.LOCK_NAME == "recoverable-controller-v20.lock"
             and legacy.SCHEMA == SCHEMA and legacy.LABEL == LABEL
             and legacy.PUBLIC_RECOVERY_ROOT == RECOVERY_ROOT
             and tuple(legacy.ROLE_ORDER) == tuple(base.ROLE_ORDER)
             and tuple(legacy.SUITES) == tuple(previous.SUITES),
             "retain genuine V20 journal, four-role restoration, and 13 suites")
        legacy.LOCK_NAME = LOCK_NAME
        need(legacy.LOCK_NAME == LOCK_NAME,
             "use the independently scoped V24 recoverable-controller lock")
        return legacy

    parent.bind_captured_controller = bind
    return {"parent": parent, "base": base, "runner": runner,
            "guard": operational, "original_base": original_base,
            "historical_parent": original_parent, "helper": helper,
            "historical_campaign": history, "build": build, "root": root,
            "freeze": freeze, "required": required(base),
            "previous_v22": v22, "previous_v21": previous,
            "old_v22_state": old_state}


def actual_context(options: dict) -> tuple[dict, dict]:
    for row in (V22[0], V22[1], V22[2], V23[0], V23[1], V23[2],
                BUILD[0], BUILD[1], BUILD[2], BUILD_RECEIPT,
                ROOT_RECEIPT, *GUARD_V4, *PREVIOUS_V24, V24_FAILURE,
                *AUDIT_V4, AUDIT_V4_FAILURE):
        secure_owner(None, row)
    source = dynamic_owner(None, "source", SOURCE, options["source_sha256"])
    protocol = dynamic_owner(None, "protocol", PROTOCOL,
                             options["protocol_sha256"])
    contract_row = dynamic_owner(None, "contract", CONTRACT,
                                 options["contract_sha256"])
    for row in (source, protocol, contract_row):
        secure_owner(None, row)
    raw = secure_owner(None, V22[0])
    previous_v22 = types.ModuleType("_rebar_v24_immutable_operational_campaign_v22")
    previous_v22.__file__ = ROOT + "/" + V22[0][1]
    exec(compile(raw, previous_v22.__file__, "exec", dont_inherit=True),
         previous_v22.__dict__)
    need(previous_v22.VERSION == 22 and previous_v22.SOURCE == V22[0][1]
         and callable(previous_v22.verify_context)
         and callable(previous_v22.actual_failure),
         "bootstrap only independently authenticated immutable V22 operation")
    historical_options = {"mode": options["mode"], "source_sha256": V22[0][2],
                          "protocol_sha256": V22[1][2],
                          "contract_sha256": V22[2][2]}
    old_context, old_state = previous_v22.verify_context(historical_options, None)
    need(old_context.get("version") == 22
         and old_context.get("source_wall_installed_before_predecessor") is False
         and old_context.get("actual_v21_preactivation_failure_receipt_sha256")
         == V21_FAILURE_SHA,
         "authenticate complete genuine V21/V22 history before V24 migration")
    original_base, old_guard = old_state["original_base"], old_state["guard"]

    def document(row: tuple, label: str) -> dict:
        raw_document = secure_owner(None, row)
        value = original_base.parse_document(old_guard, raw_document, label)
        need(type(value) is dict and old_guard.canonical(value) == raw_document,
             "reject altered actual V24 public document: " + label)
        return value

    previous_document = document(V23[2], "complete immutable V23 campaign")
    frozen = document(BUILD[2], "complete actual V24 native-build source freeze")
    receipt = document(BUILD_RECEIPT, "complete successful V24 build receipt")
    root = document(ROOT_RECEIPT, "complete successful V24 root provenance")
    guard_document = document(GUARD_V4[2], "complete operational V4 guard")
    previous_v24 = document(
        PREVIOUS_V24[2], "complete immutable original V24 correctness freeze",
    )
    actual_v24_failure = document(
        V24_FAILURE, "complete actual original V24 FAIL-1352 publication",
    )
    validate_previous_v24_failure(previous_v24, actual_v24_failure)
    audit_v4 = original_base.parse_document(
        old_guard, secure_owner(None, AUDIT_V4[2]),
        "complete independently pinned pretty-printed V4 audit source freeze",
    )
    audit_failure = document(
        AUDIT_V4_FAILURE, "complete independent V4 actual static FAIL-1",
    )
    validate_independent_audit_v4(audit_v4, audit_failure)
    validate_v4_guard(guard_document)
    validate_receipts(receipt, root, frozen, previous_document)
    old_state["v23_contract"] = previous_document
    current_document = document(contract_row,
                                "complete independently frozen V24 campaign")
    expected = frozen_contract(source, protocol, previous_document,
                               frozen, receipt, root, guard_document,
                               previous_v24, actual_v24_failure,
                               audit_v4, audit_failure)
    need(current_document == expected,
         "reject incomplete actual V24 campaign context before activation")
    previous_v21 = old_state["previous_v21"]
    guard = operational_v4_guard(previous_v21, old_state)
    migrated = build_v24_parent(previous_v22, previous_v21, old_state,
                                receipt, root, frozen, guard)
    context = dict(old_context)
    context.update({
        "schema": SCHEMA + "-frozen-context", "version": VERSION,
        "source_sha256": options["source_sha256"],
        "protocol_sha256": options["protocol_sha256"],
        "contract_sha256": options["contract_sha256"],
        "public_recovery_root": RECOVERY_ROOT,
        "recovery_lock_filename": LOCK_NAME,
        "actual_v25_build_receipt_sha256": BUILD_RECEIPT[2],
        "actual_v25_root_receipt_sha256": ROOT_RECEIPT[2],
        "actual_v25_native_engine_sha256": ENGINE_SHA,
        "actual_v25_native_bridge_sha256": BRIDGE_SHA,
        "actual_v25_corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA,
        "actual_v25_corrected_adapter_sha256": ADAPTER_SHA,
        "actual_v24_original_failure_receipt_sha256": V24_FAILURE[2],
        "actual_v24_candidate_status": "FAIL",
        "actual_v24_semantic_mismatch_count": 1352,
        "actual_v24_verified_passing_case_count": 15877,
        "independent_runtime_nondelegation_v4_failure_sha256":
            AUDIT_V4_FAILURE[2],
        "independent_runtime_nondelegation_v4_status": "FAIL",
        "independent_runtime_nondelegation_v4_finding_count": 1,
        "operational_guard_version": 4,
        "operational_guard_v4_source_sha256": GUARD_V4[0][2],
        "operational_guard_v4_protocol_sha256": GUARD_V4[1][2],
        "operational_guard_v4_contract_sha256": GUARD_V4[2][2],
        "source_wall_installed_before_predecessor": False,
        "actual_candidate_imports": 0,
        "actual_candidate_workers_started": 0,
        "actual_native_libraries_loaded": 0,
    })
    migrated["actual_v24_failure"] = actual_v24_failure
    migrated["audit_v4_failure"] = audit_failure
    migrated["context"] = context
    return context, migrated


def execute_actual(options: dict, context: dict, state: dict) -> dict:
    need(options["mode"] in ACTUAL_MODES
         and context.get("source_wall_installed_before_predecessor") is False
         and context.get("operational_guard_version") == 4,
         "require genuine unwalled V24 entry and operational V4 child policy")
    for key, expected in state["required"].items():
        need(options.get(key) == expected,
             "require independently pinned actual V24 authority: " + key)
    result = state["parent"].actual_operation(options, context, state)
    if options["mode"] == "--worker":
        need(result.get("runtime_guard_installed_before_candidate_import")
             is True and result.get("actual_candidate_workers") == 1,
             "install V4 before authentic Rust candidate matching")
        result["operational_guard_v4_source_sha256"] = GUARD_V4[0][2]
        result["operational_guard_v4_protocol_sha256"] = GUARD_V4[1][2]
        result["operational_guard_v4_contract_sha256"] = GUARD_V4[2][2]
    elif options["mode"] == "--run":
        need(result.get("suite_count") == WORKER_COUNT
             and result.get("case_execution_denominator") == CASE_COUNT
             and result.get("all_four_original_targets_restored") is True
             and result.get("actual_candidate_workers") == WORKER_COUNT
             and result.get("distinct_worker_process_id_count") == WORKER_COUNT,
             "preserve all genuine original workers and exact four-role recovery")
        result["actual_v25_build_receipt_sha256"] = BUILD_RECEIPT[2]
        result["actual_v25_root_receipt_sha256"] = ROOT_RECEIPT[2]
        result["actual_v25_native_engine_sha256"] = ENGINE_SHA
        result["actual_v25_native_bridge_sha256"] = BRIDGE_SHA
        result["actual_v24_original_failure_receipt_sha256"] = V24_FAILURE[2]
        result["actual_v24_semantic_mismatch_count"] = 1352
        result["actual_v24_verified_passing_case_count"] = 15877
        result["independent_runtime_nondelegation_v4_failure_sha256"] = (
            AUDIT_V4_FAILURE[2]
        )
        result["independent_runtime_nondelegation_v4_status"] = "FAIL"
        result["independent_runtime_nondelegation_v4_finding_count"] = 1
        result["candidate_qualified"] = False
        result["runtime_non_delegation"] = "NOT ESTABLISHED; V4 STATIC AUDIT FAIL"
    result["operational_guard_version"] = 4
    return result


def parse_options(arguments: list[str]) -> dict:
    need(bool(arguments), "select one exact V24 correctness-controller mode")
    modes = [item for item in arguments if item in SOURCE_MODES + ACTUAL_MODES]
    need(len(modes) == 1,
         "select exactly one source-only or root-authorized actual V24 mode")
    options: dict[str, str] = {"mode": modes[0]}
    cursor = 0
    while cursor < len(arguments):
        flag = arguments[cursor]
        if flag in SOURCE_MODES + ACTUAL_MODES:
            cursor += 1
            continue
        need(type(flag) is str and flag.startswith("--")
             and cursor + 1 < len(arguments),
             "reject positional or incomplete independent V24 authority")
        key = flag[2:].replace("-", "_")
        need(key not in options,
             "reject repeated or aliased actual V24 authority: " + flag)
        options[key] = arguments[cursor + 1]
        cursor += 2
    required = {"source_sha256", "protocol_sha256", "guard_v4_source_sha256",
                "guard_v4_protocol_sha256", "guard_v4_contract_sha256"}
    if options["mode"] != "--render-contract":
        required.add("contract_sha256")
    for key in required:
        sha_pin(options.get(key), key)
    for key, row in zip(("guard_v4_source_sha256", "guard_v4_protocol_sha256",
                         "guard_v4_contract_sha256"), GUARD_V4, strict=True):
        need(options[key] == row[2],
             "reject substituted independently frozen V4 guard pin: " + key)
    if options["mode"] in SOURCE_MODES:
        need(set(options) == required | {"mode"},
             "source-only mode cannot authorize candidate or private activation")
    else:
        need(set(options) > required | {"mode"},
             "reject an unpinned or weakly authorized actual V24 entry")
    return options


def main(arguments: list[str] | None = None) -> int:
    options: dict | None = None
    actual_state: dict | None = None
    try:
        verify_runtime()
        options = parse_options(list(sys.argv[1:] if arguments is None
                                     else arguments))
        if options["mode"] in ACTUAL_MODES:
            context, actual_state = actual_context(options)
            result = execute_actual(options, context, actual_state)
            encoded = actual_state["guard"].canonical(result)
            sys.stdout.buffer.write(encoded)
            sys.stdout.buffer.flush()
            return 0 if result.get("status") == "PASS" else 1

        wall = PublicSourceWall()
        wall.install()
        context, state = load_source_context(
            wall, options, options["mode"] == "--render-contract",
        )
        capture, semantic = state["capture"], state["semantic"]
        if options["mode"] == "--render-contract":
            result = context
        else:
            checks = (source_controls(wall, context, state)
                      if options["mode"] == "--self-test" else [])
            result = {
                "schema": SCHEMA + "-source-only-gate", "status": "PASS",
                "version": VERSION, "mode": options["mode"].removeprefix("--"),
                "source_sha256": options["source_sha256"],
                "protocol_sha256": options["protocol_sha256"],
                "contract_sha256": options["contract_sha256"],
                "guard_v4_source_sha256": GUARD_V4[0][2],
                "guard_v4_protocol_sha256": GUARD_V4[1][2],
                "guard_v4_contract_sha256": GUARD_V4[2][2],
                "actual_v25_build_receipt_sha256": BUILD_RECEIPT[2],
                "actual_v25_root_receipt_sha256": ROOT_RECEIPT[2],
                "actual_v25_native_engine_sha256": ENGINE_SHA,
                "actual_v25_native_bridge_sha256": BRIDGE_SHA,
                "actual_v24_failure_receipt_sha256": V24_FAILURE[2],
                "actual_v24_candidate_status": "FAIL",
                "actual_v24_semantic_mismatch_count": 1352,
                "actual_v24_verified_passing_case_count": 15877,
                "actual_v24_completed_suite_count": 13,
                "actual_v24_substitution_mismatch_count": 240,
                "actual_v24_shape_mismatch_count": 1112,
                "independent_nondelegation_v4_source_sha256": AUDIT_V4[0][2],
                "independent_nondelegation_v4_protocol_sha256": AUDIT_V4[1][2],
                "independent_nondelegation_v4_contract_sha256": AUDIT_V4[2][2],
                "independent_nondelegation_v4_failure_sha256":
                    AUDIT_V4_FAILURE[2],
                "independent_nondelegation_v4_status": "FAIL",
                "independent_nondelegation_v4_finding_count": 1,
                "corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA,
                "corrected_adapter_sha256": ADAPTER_SHA,
                "complete_v22_contract_field_count": 435,
                "complete_v21_inherited_contract_field_count": 402,
                "complete_actual_v22_failure_field_count": 96,
                "actual_v22_candidate_status": "FAIL",
                "actual_v22_verified_passing_case_count": 14725,
                "actual_v22_observed_mismatch_lower_bound": 2018,
                "actual_v22_global_semantic_mismatch_count": NOT_MEASURED,
                "case_execution_denominator": CASE_COUNT,
                "suite_count": WORKER_COUNT,
                "private_waiver_count": 13,
                "supplemental_case_count": SUPPLEMENTAL_CASE_COUNT,
                "corrected_reference_case_count": CORRECTED_REFERENCE_CASE_COUNT,
                "supplemental_counted_in_original_denominator": False,
                "corrected_reference_counted_in_original_denominator": False,
                "operational_guard_version": 4,
                "expected_real_child_interpreters": 11,
                "expected_original_case_interpreter_exec_calls": 394,
                "expected_total_real_interpreter_exec_calls": 416,
                "actual_candidate_imports": 0,
                "actual_candidate_workers_started": 0,
                "actual_reference_workers_started": 0,
                "actual_compiler_processes_started": 0,
                "actual_native_libraries_loaded": 0,
                "actual_private_build_root_opens": 0,
                "actual_private_build_root_stats": 0,
                "actual_build_archive_opens": 0,
                "actual_hidden_cases_read": 0,
                "actual_clock_samples": 0,
                "actual_v4_child_interpreters_created": 0,
                "actual_v4_original_case_interpreter_exec_calls": 0,
                "source_wall_installed_before_predecessor": wall.installed,
                "source_wall_live_descriptors": len(wall.live),
                "hostile_control_count": len(checks),
                "hostile_controls": checks,
                "physically_blocked_effects": dict(wall.blocked),
                "actual_original_campaign": "NOT RUN",
                "candidate_correctness": NOT_MEASURED,
                "candidate_qualified": False,
                "runtime_non_delegation":
                    "NOT ESTABLISHED; INDEPENDENT V4 STATIC AUDIT FAIL",
                "expanded_holdout_proposal_case_count": HOLDOUT_CASE_COUNT,
                "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
                "holdout": "NOT OPENED", "performance": NOT_MEASURED,
                "memory": NOT_MEASURED, "confidence_intervals": NOT_MEASURED,
                "undefined_behavior": NOT_MEASURED,
                "qualified_candidate_count": 0, "winner_selected": False,
            }
        encoded = capture.canonical_document(semantic, result)
        need(type(encoded) is bytes and 0 < len(encoded) <= MAX_OWNER_BYTES,
             "bound complete source-only or separately authorized V24 result")
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
        return 0
    except BaseException as error:
        if actual_state is not None:
            try:
                previous = actual_state["previous_v22"]
                preserved = previous.actual_failure(
                    actual_state["old_v22_state"], options, error,
                )
                preserved["schema"] = SCHEMA + (
                    "-actual-original-suite-worker-failure"
                    if preserved.get("actual_candidate_imports") == 1
                    else "-entry-failure")
                preserved["version"] = VERSION
                preserved["operational_guard_version"] = 4
                preserved["operational_guard_v4_source_sha256"] = GUARD_V4[0][2]
                sys.stdout.buffer.write(actual_state["guard"].canonical(preserved))
                sys.stdout.buffer.flush()
            except BaseException:
                pass
        else:
            try:
                sys.stderr.write("V25 original campaign rejected: "
                                 + type(error).__name__ + ": "
                                 + str(error)[:8192] + "\n")
            except BaseException:
                pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
