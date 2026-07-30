#!/usr/bin/env python3
"""Freeze the complete 10,434-case public Rust oracle; root alone runs it.

Source modes install an irreversible public-phase-two-only wall before their
first predecessor read.  They never inspect a candidate, private root, native
object, archive, final proposal, clock, or phase-three file.  The immutable V32
precompiler failure, V26 original PASS, V28 public FAIL-1145, and clean V5 static
PASS remain distinct.  Actual matching requires a successful independently
pinned V33 build, a separately pushed V5 freeze, and explicit root authority.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("full public correctness must bootstrap without a matcher")

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
SOURCE = "tools/run_owned_rust_full_public_correctness_v5.py"
PROTOCOL = "oracle/phase2/RUST-FULL-PUBLIC-CORRECTNESS-V5.md"
CONTRACT = "oracle/phase2/rust-full-public-correctness-v5.json"
SCHEMA = "rebar-owned-rust-full-public-correctness-v5"
VERSION = 5
BUILD_VERSION = 33
BUILD_LABEL = "phase2-v33-rust-full-public-semantic-source-root-provenance"
CASE_COUNT = 10434
DATASET_COUNT = 94
OPERATIONS_PER_DATASET = 111
DOMAIN_CASE_COUNT = 5217
PUBLISHED_SEED = 5928217332825411634
MATRIX_SHA = "0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d"
FINAL_HOLDOUT = "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
ENGINE_SOURCE_SHA = "7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38"
ENGINE_SOURCE_BYTES = 189493
SEARCH_SOURCE_SHA = "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7"
SEARCH_SOURCE_BYTES = 24305
BRIDGE_SOURCE_SHA = "f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e"
BRIDGE_SOURCE_BYTES = 178472
ADAPTER_SHA = "f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227"
ADAPTER_BYTES = 34039
V32_SOURCE_SHA = "19b4eb39ecadd0486b1385071716e78c6bf52f38b73bc54a3fd9bafc76106153"
V32_PROTOCOL_SHA = "cbfefb56f5c99209d30a5e7b368533554a9ce454db07acf42f274728ba0cb650"
V32_CONTRACT_SHA = "cf5c05d19a4b10ce3e4d32c326f63850a936d5e11c53f4a8d8a59fdcb90dec72"
V32_FAILURE_SHA = "8adf8ae6fd08c0bf38df121ff6a2ea245ae69de19908a1effd0a50dbff809e85"
V26_ORIGINAL_SHA = "84804409997794ce7e8bfff67ca8ffdcada9651a1660bda2654742befbba20f5"
V28_PUBLIC_SHA = "c786b1216a58c4ac6a29363ce87d7741fb55fbb85f30665f795875bef244becb"
V5_AUDIT_SHA = "a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203"
V4_SOURCE_SHA = "6317f4e4a51e745fe68d2a15743164d0e102e6ea33330cde381ccbb1d9f61c61"
V4_PROTOCOL_SHA = "ec27b57a5e0461ada40513199e4a97574c3aef656670fc469343015ac311f081"
V4_CONTRACT_SHA = "f5a101f2cd146db0e9c6048a7977098383aa7c4b0f72780e398d7a7ace270796"
V4_FAILURE_SHA = "24d1e884b6268d08f6d51efbe30ccce4d446bd3a51381a88e0dd204370a9328d"
PUBLIC_HARNESS_SHA = "a3d7e70343d231bf433fbad6a6669025a970d83691c49cb9f434a186aef3d9e6"
V33_SOURCE_PATH = "tools/reproduce_owned_rust_full_public_semantic_source_build_v33.py"
V33_PROTOCOL_PATH = "oracle/phase2/RUST-FULL-PUBLIC-SEMANTIC-SOURCE-BUILD-V33.md"
V33_CONTRACT_PATH = "oracle/phase2/rust-full-public-semantic-source-build-v33.json"
V33_PUBLICATION_PATH = (
    "oracle/phase2/evidence/native-source-build-v33-rust-"
    "phase2-v33-rust-full-public-semantic-source-root-provenance-"
    "publication-receipt.json"
)
V33_ROOT_PATH = (
    "oracle/phase2/evidence/native-source-build-v33-rust-"
    "phase2-v33-rust-full-public-semantic-source-root-provenance-"
    "root-provenance-receipt.json"
)
MAX_OWNER_BYTES = 2 * 1024 * 1024
MAX_NATIVE_BYTES = 16 * 1024 * 1024
MAX_ACTUAL_BYTES = 128 * 1024 * 1024
SOURCE_MODES = ("--render-contract", "--verify-frozen-context", "--self-test")
ACTUAL_MODES = ("--run",)
OVERLAY_PREFIX = "rebar-rust-full-public-correctness-v5-"
PUBLIC_OUTPUT = ROOT + "/experiments/rust_full_public_correctness_v5"
PARTITION = {"scanner": 470, "substitution": 376,
             "comment": 297, "scoped_unicode": 2}

# Exact immutable public plaintext only. Candidate variants and phase-three
# public files are deliberately excluded even though predecessors mention them.
PUBLIC_OWNERS = (
    ("v4_gate_source", "tools/run_owned_rust_full_public_correctness_v4.py", V4_SOURCE_SHA, 78952, 430152),
    ("v4_gate_protocol", "oracle/phase2/RUST-FULL-PUBLIC-CORRECTNESS-V4.md", V4_PROTOCOL_SHA, 5762, 525071),
    ("v4_gate_contract", "oracle/phase2/rust-full-public-correctness-v4.json", V4_CONTRACT_SHA, 29463, 525078),
    ("v4_preworker_failure", "oracle/phase2/evidence/rust-full-public-correctness-v4-preworker-failure.json", V4_FAILURE_SHA, 969, 525216),
    ("v3_gate_source", "tools/run_owned_rust_native_architecture_public_gate_v3.py", "12d0ae388cd2841d0cb091e7da88859a772a3b3c293f18938b488196a32c5eab", 106590, 431279),
    ("v3_gate_protocol", "oracle/phase2/RUST-NATIVE-ARCHITECTURE-PUBLIC-GATE-V3.md", "fdf695478fc1b542026c2b98ba94524df254aea84b46ebab568a98050474cae4", 5911, 525630),
    ("v3_gate_contract", "oracle/phase2/rust-native-architecture-public-gate-v3.json", "80a350478ae4dbf4d745683974b4c60630d900d2e3f97d59cf391bfb1d8358a0", 26615, 525842),
    ("public_harness", "tools/rust_public_practice_benchmark_v2.py", PUBLIC_HARNESS_SHA, 112729, 429259),
    ("public_evidence_source", "tools/run_rust_public_correctness_evidence_v2.py", "e24a630c2ac60c49dd4ac707f80afc07a2516629e47c7b15fd4e7dca75102281", 56423, 429551),
    ("v32_source", "tools/reproduce_owned_rust_full_public_semantic_source_build_v32.py", V32_SOURCE_SHA, 164862, 430558),
    ("v32_protocol", "oracle/phase2/RUST-FULL-PUBLIC-SEMANTIC-SOURCE-BUILD-V32.md", V32_PROTOCOL_SHA, 6353, 525053),
    ("v32_contract", "oracle/phase2/rust-full-public-semantic-source-build-v32.json", V32_CONTRACT_SHA, 53381, 525055),
    ("v32_precompiler_failure", "oracle/phase2/evidence/native-source-build-v32-rust-full-public-preexecution-failure.json", V32_FAILURE_SHA, 1113, 524905),
    ("v26_original_source", "tools/run_owned_repaired_rust_original_campaign_v26.py", "37d3edd69f93c33defaaeb8a1473e39b0563f06af57e6038340679dd8c61091d", 97746, 431629),
    ("v26_original_protocol", "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V26.md", "aefd84daf141fc92e73c6fedec82a9c179b9d67db6f67f93bcaf6d8cca40b42d", 7501, 526047),
    ("v26_original_contract", "oracle/phase2/repaired-rust-original-campaign-v26.json", "8493afcb087e79b0b2419711746fb82dd5c09785fe086fa627ea99af41365eaa", 22874, 526048),
    ("v26_original_pass", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v30-rust-complete-semantic-source-root-provenance-original-p0-v26-publication-receipt.json", V26_ORIGINAL_SHA, 12055, 525046),
    ("v28_public_failure", "oracle/phase2/evidence/rust-native-architecture-public-gate-v3-v28-combined-public-run-001-publication-receipt.json", V28_PUBLIC_SHA, 40372, 525923),
    ("v5_audit_source", "tools/audit_clean_rust_runtime_non_delegation_v5.py", "5ab79fc493f1b798d1020311dddf7a061e5b272d3c6f2c10e19127311b57b542", 86600, 428898),
    ("v5_audit_protocol", "oracle/phase2/RUST-CLEAN-NON-DELEGATION-V5.md", "4efa6122a16c438224f226f468d0654473df489fa338f2539ae22411ce4d01fa", 5918, 525041),
    ("v5_audit_contract", "oracle/phase2/rust-clean-non-delegation-v5.json", "605e0a55f57d1e5c9061bcefe9323bf4de62905c92ca9a29021a79503546cd57", 6150, 525047),
    ("v5_static_pass", "oracle/phase2/evidence/rust-clean-non-delegation-v5-actual-source-audit.json", V5_AUDIT_SHA, 16427, 525089),
    ("v30_source", "tools/reproduce_owned_rust_complete_semantic_source_build_v30.py", "dd0ed268775537b985a060e5f608c6bc2730f86922ad20ee78cff19e4c387a1d", 138860, 431674),
    ("v30_protocol", "oracle/phase2/RUST-COMPLETE-SEMANTIC-SOURCE-BUILD-V30.md", "9f508fd651fa544ecea82487cb05bc94cce6aa1049ec676d257eb62fc73b3c61", 8746, 524934),
    ("v30_contract", "oracle/phase2/rust-complete-semantic-source-build-v30.json", "38e0a8f44cf1e3f68abb643b004f7f47350e743f5c3f1994d101b02e5ebc1956", 41458, 524935),
    ("v30_publication", "oracle/phase2/evidence/native-source-build-v30-rust-phase2-v30-rust-complete-semantic-source-root-provenance-publication-receipt.json", "c29361f0436f73ada037ba497a0eb008eeadac6ebb41c50019521c0212448abd", 3438, 524977),
    ("v30_root", "oracle/phase2/evidence/native-source-build-v30-rust-phase2-v30-rust-complete-semantic-source-root-provenance-root-provenance-receipt.json", "26445b833ac0e846538a1f648059a1c8a224e4e2f1acd58f82e9458dcc142404", 77160, 524978),
    ("scanner_source", "tools/apply_owned_rust_complete_scanner_bridge_v1.py", "de9446d64c8aaf4253d2301118973e2c9de82b40dc52da9e2848e460685f1999", 88297, 429524),
    ("scanner_protocol", "oracle/phase2/RUST-COMPLETE-SCANNER-BRIDGE-V1.md", "1418606f649fa36e373b559ee7ba428bcb9a139ddb016b89fc903504c89106a2", 9872, 524936),
    ("scanner_contract", "oracle/phase2/rust-complete-scanner-bridge-v1.json", "e4b1b52fd9a8a9b3008672ceb6c685dc62dda60a217cdedf51841ca43300f7b7", 8013, 524969),
    ("scanner_application", "oracle/phase2/evidence/rust-complete-scanner-bridge-v1-application.json", "c665041fd03cb44cf29041a38848bdd3e61cee051f432e377a32d49a87537e97", 1031, 525190),
    ("scoped_source", "tools/apply_owned_rust_combined_scoped_unicode_engine_v1.py", "819b2a2576825e7bb84738564e432162063240ed09b9d3b8031c3815d2d17d16", 74851, 430270),
    ("scoped_protocol", "oracle/phase2/RUST-COMBINED-SCOPED-UNICODE-ENGINE-V1.md", "6eba43efaa7019826806055ef2af6d0fe8cf180884f53baac0457d911ec9c36b", 5807, 524902),
    ("scoped_contract", "oracle/phase2/rust-combined-scoped-unicode-engine-v1.json", "d5eb343f1ab16ace5d3ae9038a934d7a2dc5a22282e1e81f607234478c01a570", 9863, 525036),
    ("scoped_application", "oracle/phase2/evidence/rust-combined-scoped-unicode-engine-v1-application.json", "776c7a631eb45edc4fa804bec1bb4e663f74ae18e5a1d5ccccbc0773545264df", 1091, 525399),
    ("comment_source", "tools/apply_owned_rust_corrected_comment_adapter_v2.py", "209b05313a3cc7d58520f3979088a96d747c8e55e65f02313f64a33fe234795d", 65237, 430684),
    ("comment_protocol", "oracle/phase2/RUST-CORRECTED-COMMENT-ADAPTER-V2.md", "cbbf0b168618767b27565b44c38c36a2dea85166d6050d6d3b4fab8f97937f5b", 9420, 525358),
    ("comment_contract", "oracle/phase2/rust-corrected-comment-adapter-v2.json", "b9d7e7e4149591539e4682024b543fa69605e79a22e2a3397a244a25e6e0cc1a", 5762, 525396),
    ("comment_application", "oracle/phase2/evidence/rust-corrected-comment-adapter-v2-application.json", "50c9d569d5c34118d7984e9d952b3cb99bb8cbb27e992caf786e626d383de6a8", 2162, 525455),
    ("comment_v1_failure", "oracle/phase2/evidence/rust-corrected-comment-adapter-v1-preapplication-failure.json", "7bc692fcf17780ed05ca49c982536849212e1909f73337764b2392ea3ee9a37b", 902, 525290),
)


class PublicError(Exception):
    """Reject substituted public history or an unauthorized full candidate run."""


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
        relatives = (SOURCE, PROTOCOL, CONTRACT, V33_SOURCE_PATH,
                     V33_PROTOCOL_PATH, V33_CONTRACT_PATH,
                     V33_PUBLICATION_PATH, V33_ROOT_PATH,
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
        raise PublicError("full public V5 source wall rejected " + category)

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
    allowed = (SOURCE, PROTOCOL, CONTRACT, V33_SOURCE_PATH, V33_PROTOCOL_PATH,
               V33_CONTRACT_PATH, V33_PUBLICATION_PATH, V33_ROOT_PATH)
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
    module = types.ModuleType("_rebar_v5_authenticated_public_gate_v3")
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


def validate_history(module: types.ModuleType,
                     payloads: dict[str, bytes]) -> dict:
    by_role = {row[0]: row for row in PUBLIC_OWNERS}
    v3 = parse_json(module, payloads["v3_gate_contract"], "complete V3 gate freeze")
    public = v3.get("public_correctness")
    need(v3.get("schema")
         == "rebar-owned-rust-native-architecture-public-gate-v3-source-freeze"
         and v3.get("source_sha256") == by_role["v3_gate_source"][2]
         and v3.get("protocol_sha256") == by_role["v3_gate_protocol"][2]
         and type(public) is dict and public.get("case_count") == CASE_COUNT
         and public.get("matrix_sha256") == MATRIX_SHA
         and public.get("published_seed") == PUBLISHED_SEED
         and public.get("preserve_all_mismatches") is True
         and v3.get("candidate_qualified") is False
         and v3.get("current_final_holdout") == FINAL_HOLDOUT,
         "preserve independently frozen full 10,434-case V3 public oracle")
    original = parse_json(module, payloads["v26_original_pass"],
                          "actual complete independently restored original V26 PASS")
    suites = original.get("suite_integrity")
    need(original.get("schema")
         == "rebar-owned-repaired-rust-original-campaign-v26-durable-publication-receipt"
         and original.get("status") == "PASS"
         and original.get("publication_status") == "PASS"
         and original.get("candidate_status") == "PASS"
         and original.get("candidate_original_oracle_pass") is True
         and original.get("original_suite_correctness_qualified") is True
         and original.get("candidate_qualified") is False
         and original.get("case_execution_denominator") == 31237
         and original.get("verified_passing_case_count") == 31237
         and original.get("semantic_mismatch_count") == 0
         and original.get("actual_candidate_workers") == 13
         and original.get("distinct_worker_process_id_count") == 13
         and original.get("completed_suite_count") == 13
         and original.get("infrastructure_failure_count") == 0
         and original.get("all_four_original_targets_restored") is True
         and type(suites) is list and len(suites) == 13
         and all(type(row) is dict and row.get("fully_observed") is True
                 and row.get("mismatch_count") == 0
                 and row.get("verified_passing_case_count")
                     == row.get("case_execution_denominator")
                 for row in suites)
         and sum(row["case_execution_denominator"] for row in suites) == 31237,
         "preserve all actual independent V26 original observations, not a build claim")
    # The complete V28 publication contains genuine historical timing floats.
    # The frozen integer-only predecessor parser must never decode or truncate
    # that evidence. Authenticate complete bytes first, then exact unique public
    # structural markers and the separately preserved full-mismatch owner.
    historical = payloads["v28_public_failure"]
    mismatch_vector = {
        "path": ROOT + "/experiments/rust_native_architecture_public_v3/"
                "v28-combined-public-run-001/public-10434-correctness.raw.json",
        "sha256": "7fc4c743e35bbe4f57ed0e3a872b9a9646b2603feedb9ae2c24421afed5430aa",
        "bytes": 1428906, "device": DEVICE, "inode": 525893,
        "mode": "0600",
    }
    historical_markers = (
        b'"schema":"rebar-owned-rust-native-architecture-public-gate-v3-'
        b'durable-publication-receipt"',
        b'"architecture":"v28"',
        b'"public_10434_correctness_status":"FAIL"',
        b'"public_10434_case_count":10434',
        b'"public_10434_mismatch_count":1145',
        b'"candidate_qualified":false',
        b'"current_final_holdout":"INVALIDATED; REKEYED SUCCESSOR REQUIRED"',
        b'"path":"' + mismatch_vector["path"].encode("ascii") + b'"',
        b'"sha256":"' + mismatch_vector["sha256"].encode("ascii") + b'"',
        b'"bytes":1428906',
        b'"inode":525893',
    )
    need(all(historical.count(item) == 1 for item in historical_markers),
         "retain every authentic V28 public mismatch and its exact raw-vector owner")
    immutable_v4 = parse_json(module, payloads["v4_gate_contract"],
                             "complete immutable unsuccessfully executed V4 public freeze")
    v4_failed = parse_json(module, payloads["v4_preworker_failure"],
                           "immutable root-authorized V4 preworker actual failure")
    need(immutable_v4.get("schema")
         == "rebar-owned-rust-full-public-correctness-v4-source-freeze"
         and immutable_v4.get("source_sha256") == V4_SOURCE_SHA
         and immutable_v4.get("protocol_sha256") == V4_PROTOCOL_SHA
         and immutable_v4.get("public_correctness", {}).get("case_count") == CASE_COUNT
         and immutable_v4.get("public_correctness", {}).get("operation_count")
             == OPERATIONS_PER_DATASET
         and immutable_v4.get("candidate_qualified") is False
         and v4_failed.get("schema")
             == "rebar-owned-rust-full-public-correctness-v4-preworker-failure"
         and v4_failed.get("status") == "FAIL"
         and v4_failed.get("failure_phase") == "ROOT_OVERLAY_NONEMPTY_OUTPUT"
         and v4_failed.get("controller_source_sha256") == V4_SOURCE_SHA
         and v4_failed.get("protocol_sha256") == V4_PROTOCOL_SHA
         and v4_failed.get("contract_sha256") == V4_CONTRACT_SHA
         and v4_failed.get("candidate_workers_started") == 0
         and v4_failed.get("reference_workers_started") == 0
         and v4_failed.get("candidate_executions") == 0
         and v4_failed.get("public_case_execution_denominator") == CASE_COUNT
         and v4_failed.get("public_operation_count") == OPERATIONS_PER_DATASET
         and v4_failed.get("candidate_qualified") is False,
         "retain immutable V4 actual preworker failure before authenticating V5 successor")
    failed = parse_json(module, payloads["v32_precompiler_failure"],
                        "immutable root-authenticated V32 precompiler rejection")
    need(failed.get("schema")
         == "rebar-phase2-owned-rust-full-public-semantic-source-build-v32-preexecution-failure"
         and failed.get("status") == "FAIL"
         and failed.get("failure_phase") == "AUTHENTICATED_PRIVATE_OVERLAY_VALIDATION"
         and failed.get("source_sha256") == V32_SOURCE_SHA
         and failed.get("protocol_sha256") == V32_PROTOCOL_SHA
         and failed.get("contract_sha256") == V32_CONTRACT_SHA
         and failed.get("corrected_adapter_sha256") == ADAPTER_SHA
         and failed.get("corrected_adapter_bytes") == ADAPTER_BYTES
         and failed.get("inherited_kernel_adapter_sha256")
             == "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
         and failed.get("compiler_processes_started") == 0
         and failed.get("candidate_executions") == 0
         and failed.get("native_build_started") is False
         and failed.get("final_proposal_reads") == 0
         and failed.get("candidate_qualified") is False,
         "never erase or promote the genuine V32 adapter-kernel precompiler failure")
    audit = parse_json(module, payloads["v5_static_pass"],
                       "complete independently published V5 static source/ELF PASS")
    need(audit.get("schema")
         == "rebar-phase2-clean-first-party-rust-non-delegation-v5-root-static-audit"
         and audit.get("status") == "PASS" and audit.get("finding_count") == 0
         and audit.get("clean_candidate_source_static_non_delegation") == "PASS"
         and audit.get("clean_candidate_native_elf_static_non_delegation") == "PASS"
         and all(audit.get(key) == 0 for key in (
             "external_regex_packages", "external_regex_libraries",
             "external_regex_symbols", "cross_family_dependencies",
             "candidate_executions", "native_library_loads"))
         and audit.get("candidate_qualified") is False
         and audit.get("runtime_non_delegation")
             == "NOT ESTABLISHED; STATIC SOURCE AND ELF AUDIT ONLY",
         "preserve zero-external V5 static PASS without inventing runtime qualification")
    operations = public_operations(payloads["public_harness"])
    return {"operations": operations, "v3": v3, "v26": original,
            "v28": {"status": "PASS", "candidate_status": "FAIL",
                    "case_count": CASE_COUNT, "mismatch_count": 1145},
            "v28_full_vector": mismatch_vector,
            "v32": failed, "v4_freeze": immutable_v4,
            "v4_failure": v4_failed, "v5": audit}


def native_identity(item: object, phase: dict, role: str) -> dict:
    need(type(item) is dict and item.get("role") == role,
         "require one exact separately reproduced native " + role)
    expected_name = ("_rust_engine.so" if role == "engine"
                     else "_rust_bridge.cpython-314-x86_64-linux-gnu.so")
    expected_mode = "0600" if role == "engine" else "0700"
    path = str(item.get("absolute_path"))
    need(item.get("file_name") == expected_name
         and path == phase["absolute_path"] + "/native/" + expected_name
         and type(item.get("sha256")) is str
         and len(sha(item["sha256"], role + " native")) == 64
         and type(item.get("bytes")) is int
         and 0 < item["bytes"] <= MAX_NATIVE_BYTES
         and item.get("device") == PRIVATE_DEVICE
         and type(item.get("inode")) is int and item["inode"] > 0
         and item.get("mode") == expected_mode
         and item.get("nlink") == 1 and item.get("uid") == os.geteuid()
         and item.get("native_loaded") is False,
         "reject substituted, preloaded, or unowned native " + role)
    return {"role": role, "absolute_path": path, "sha256": item["sha256"],
            "bytes": item["bytes"], "device": PRIVATE_DEVICE,
            "inode": item["inode"], "mode": expected_mode,
            "uid": item["uid"], "nlink": 1, "native_loaded": False}


def validate_build(module: types.ModuleType, payloads: dict[str, bytes],
                   rows: dict[str, tuple], history: dict) -> dict:
    freeze = parse_json(module, payloads["v33_contract"],
                        "complete committed first-party V33 source build freeze")
    public = parse_json(module, payloads["v33_publication"],
                        "complete successful actual V33 native-build publication")
    root = parse_json(module, payloads["v33_root"],
                      "complete successful independently reproduced V33 private root")
    prior = freeze.get("preserved_public_v28_1145_disjoint_partition")
    previous = freeze.get("preserved_original_31237_case_pass")
    candidate_sources = freeze.get("candidate_sources")
    build = freeze.get("frozen_offline_dual_phase_build")
    need(freeze.get("schema")
         == "rebar-phase2-owned-rust-full-public-semantic-source-build-v33-source-freeze"
         and freeze.get("version") == BUILD_VERSION
         and freeze.get("source", {}).get("sha256") == rows["v33_source"][2]
         and freeze.get("protocol", {}).get("sha256") == rows["v33_protocol"][2]
         and type(previous) is dict and previous.get("candidate_status") == "PASS"
         and previous.get("verified_passing_case_count") == 31237
         and previous.get("receipt_sha256") == V26_ORIGINAL_SHA
         and type(prior) is dict and prior.get("candidate_status") == "FAIL"
         and prior.get("case_count") == CASE_COUNT
         and prior.get("mismatch_count") == 1145
         and prior.get("partition") == PARTITION
         and prior.get("scanner_comment_overlap_count") == 15
         and prior.get("substitution_comment_overlap_count") == 12
         and prior.get("receipt_sha256") == V28_PUBLIC_SHA
         and type(candidate_sources) is dict and type(build) is dict
         and candidate_sources.get("combined_engine", {}).get("sha256")
             == ENGINE_SOURCE_SHA
         and candidate_sources.get("combined_search", {}).get("sha256")
             == SEARCH_SOURCE_SHA
         and candidate_sources.get("complete_scanner_bridge", {}).get("sha256")
             == BRIDGE_SOURCE_SHA
         and candidate_sources.get("corrected_comment_adapter", {}).get("sha256")
             == ADAPTER_SHA
         and build.get("required_actual_compiler_process_count") == 28
         and build.get("external_cargo_dependency_count") == 0
         and build.get("independent_phase_count") == 2
         and build.get("canonical_source_owners_per_phase") == 9,
         "reject incomplete V33 composition, original history, or disjoint public failures")
    need(public.get("schema")
         == "rebar-phase2-owned-rust-full-public-semantic-source-build-v33-durable-publication-receipt"
         and public.get("version") == BUILD_VERSION
         and public.get("status") == "PASS"
         and public.get("build_status") == "PASS"
         and public.get("label") == BUILD_LABEL
         and public.get("source_sha256") == rows["v33_source"][2]
         and public.get("protocol_sha256") == rows["v33_protocol"][2]
         and public.get("contract_sha256") == rows["v33_contract"][2]
         and public.get("actual_compiler_process_count") == 28
         and public.get("actual_completed_phase_count") == 2
         and public.get("external_cargo_dependency_count") == 0
         and public.get("combined_engine_source_sha256") == ENGINE_SOURCE_SHA
         and public.get("combined_search_source_sha256") == SEARCH_SOURCE_SHA
         and public.get("safe_no_external_introspection_bridge_sha256")
             == BRIDGE_SOURCE_SHA
         and public.get("corrected_public_adapter_sha256") == ADAPTER_SHA
         and public.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
         and public.get("latest_original_v26_candidate_status") == "PASS"
         and public.get("latest_original_v26_verified_passing_case_count") == 31237
         and public.get("latest_public_v28_mismatch_count") == 1145
         and public.get("candidate_qualified") is False,
         "require complete successful V33 publication before any candidate correctness")
    need(root.get("schema")
         == "rebar-phase2-owned-rust-full-public-semantic-source-build-v33-durable-root-provenance-receipt"
         and root.get("version") == BUILD_VERSION and root.get("status") == "PASS"
         and root.get("label") == BUILD_LABEL
         and root.get("source_sha256") == rows["v33_source"][2]
         and root.get("protocol_sha256") == rows["v33_protocol"][2]
         and root.get("contract_sha256") == rows["v33_contract"][2]
         and root.get("canonical_build_status") == "PASS"
         and root.get("canonical_build_receipt_sha256") == rows["v33_publication"][2]
         and root.get("actual_compiler_process_count") == 28
         and root.get("actual_source_phase_count") == 2
         and root.get("distinct_private_source_identity_count") == 18
         and root.get("all_original_source_identities_restored") is True
         and root.get("all_original_runtime_target_identities_restored") is True
         and root.get("actual_original_runtime_target_count") == 5
         and root.get("cross_phase_complete_engine_elf_byte_identical") is True
         and root.get("cross_phase_complete_bridge_elf_byte_identical") is True
         and root.get("combined_engine_source_sha256") == ENGINE_SOURCE_SHA
         and root.get("combined_search_source_sha256") == SEARCH_SOURCE_SHA
         and root.get("safe_no_external_introspection_bridge_sha256")
             == BRIDGE_SOURCE_SHA
         and root.get("corrected_public_adapter_sha256") == ADAPTER_SHA
         and root.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
         and root.get("latest_original_v26_candidate_status") == "PASS"
         and root.get("latest_public_v28_mismatch_count") == 1145
         and root.get("candidate_qualified") is False,
         "require complete authentic V33 root provenance, restoration, and both phases")
    private = root.get("root")
    records = root.get("actual_private_source_owners")
    need(type(private) is dict and type(records) is list and len(records) == 2
         and type(private.get("path")) is str
         and private["path"].startswith("/tmp/rebar-phase2-native-build-v9-rust-")
         and "/../" not in private["path"]
         and private.get("device") == PRIVATE_DEVICE
         and type(private.get("inode")) is int and private["inode"] > 0
         and private.get("phase_count") == 2
         and private.get("directory_scanned") is False,
         "independently pin one exact no-scan V33 root and both private source phases")
    phases = private.get("phases")
    need(type(phases) is list and len(phases) == 2,
         "require both exact independently reproduced V33 source phases")
    checked = []
    seen: set[int] = set()
    expected_sources = {
        "candidates/rust/src/lib.rs": (ENGINE_SOURCE_SHA, ENGINE_SOURCE_BYTES),
        "candidates/rust/src/search.rs": (SEARCH_SOURCE_SHA, SEARCH_SOURCE_BYTES),
        "candidates/rust/py_bridge.c": (BRIDGE_SOURCE_SHA, BRIDGE_SOURCE_BYTES),
        "candidates/rust_candidate.py": (ADAPTER_SHA, ADAPTER_BYTES),
    }
    for index, name in enumerate(("reference-a", "reference-b")):
        phase = phases[index]
        owner_record = records[index]
        need(type(phase) is dict and phase.get("name") == name
             and phase.get("absolute_path") == private["path"] + "/" + name
             and phase.get("device") == PRIVATE_DEVICE
             and type(phase.get("inode")) is int and phase["inode"] > 0
             and phase.get("mode") == "0700"
             and type(owner_record) is dict and owner_record.get("phase") == name,
             "reject substituted independent V33 private phase " + name)
        owners = owner_record.get("owners")
        need(type(owners) is dict and len(owners) == 9,
             "authenticate every exact V33 private source owner in phase " + name)
        selected_sources = {}
        for relative, (fingerprint, count) in expected_sources.items():
            item = owners.get(relative)
            need(type(item) is dict and item.get("sha256") == fingerprint
                 and item.get("bytes") == count
                 and item.get("device") == PRIVATE_DEVICE
                 and type(item.get("inode")) is int and item["inode"] > 0
                 and item.get("exclusive_creation") is True
                 and item.get("same_inode_readback_verified") is True
                 and item.get("file_fsync_completed") is True,
                 "reject substituted private source " + relative + " in " + name)
            selected_sources[relative] = dict(item)
            need(item["inode"] not in seen,
                 "reject reused private V33 corrected source owner inode")
            seen.add(item["inode"])
        binaries = phase.get("native_outputs")
        need(type(binaries) is list and len(binaries) == 2,
             "require both genuine native artifacts in " + name)
        native = {item.get("role"): item for item in binaries
                  if type(item) is dict}
        need(set(native) == {"engine", "bridge"},
             "reject incomplete independently reproduced V33 ELF roles")
        checked_native = {role: native_identity(native[role], phase, role)
                          for role in ("engine", "bridge")}
        for value in checked_native.values():
            need(value["inode"] not in seen,
                 "reject reused independently reproduced V33 native owner")
            seen.add(value["inode"])
        checked.append({"name": name, "absolute_path": phase["absolute_path"],
                        "device": PRIVATE_DEVICE, "inode": phase["inode"],
                        "mode": "0700", "source_owners": selected_sources,
                        "all_private_source_owner_count": 9,
                        "native_outputs": checked_native})
    need(checked[0]["native_outputs"]["engine"]["sha256"]
         == checked[1]["native_outputs"]["engine"]["sha256"]
         and checked[0]["native_outputs"]["engine"]["bytes"]
         == checked[1]["native_outputs"]["engine"]["bytes"]
         and checked[0]["native_outputs"]["bridge"]["sha256"]
         == checked[1]["native_outputs"]["bridge"]["sha256"]
         and checked[0]["native_outputs"]["bridge"]["bytes"]
         == checked[1]["native_outputs"]["bridge"]["bytes"],
         "reject nonreproducible V33 cross-phase native outputs")
    return {"freeze": freeze, "publication": public, "root": root,
            "private_root": {"path": private["path"], "device": PRIVATE_DEVICE,
                             "inode": private["inode"], "phase_count": 2,
                             "directory_scanned": False},
            "phases": checked,
            "engine": dict(checked[0]["native_outputs"]["engine"]),
            "bridge": dict(checked[0]["native_outputs"]["bridge"])}


def contract_document(rows: dict[str, tuple], history: dict,
                      build: dict, source_pin: str, protocol_pin: str) -> dict:
    return {
        "schema": SCHEMA + "-source-freeze", "version": VERSION,
        "status": "SOURCE FROZEN; SUCCESSFUL V33 BUILD; PUBLIC CORRECTNESS NOT RUN",
        "family": "rust", "source": pin(rows["source"]),
        "protocol": pin(rows["protocol"]), "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "authenticated_public_plaintext_owner_count": len(PUBLIC_OWNERS) + 5,
        "authenticated_public_plaintext_owners":
            [pin(row) for row in PUBLIC_OWNERS]
            + [pin(rows[name]) for name in (
                "v33_source", "v33_protocol", "v33_contract",
                "v33_publication", "v33_root")],
        "public_correctness": {
            "case_count": CASE_COUNT, "dataset_count": DATASET_COUNT,
            "operations_per_dataset": OPERATIONS_PER_DATASET,
            "str_case_count": DOMAIN_CASE_COUNT,
            "bytes_case_count": DOMAIN_CASE_COUNT,
            "published_seed": PUBLISHED_SEED,
            "matrix_sha256": MATRIX_SHA,
            "operation_count": len(history["operations"]),
            "operations": list(history["operations"]),
            "harness_source_sha256": PUBLIC_HARNESS_SHA,
            "all_cases_execute_even_on_failure": True,
            "all_mismatches_retained": True,
            "reference_and_candidate_isolated_processes": True,
            "performance_operation_available": False,
            "profile_416_operation_available": False,
            "timing_trials_run": 0,
        },
        "actual_successful_v33_build": {
            "label": BUILD_LABEL, "source": pin(rows["v33_source"]),
            "protocol": pin(rows["v33_protocol"]),
            "contract": pin(rows["v33_contract"]),
            "publication_receipt": pin(rows["v33_publication"]),
            "root_provenance_receipt": pin(rows["v33_root"]),
            "build_status": "PASS", "actual_compiler_process_count": 28,
            "independent_source_phase_count": 2,
            "source_owners_per_phase": 9,
            "private_root": build["private_root"],
            "phase_native_and_corrected_source_owners": build["phases"],
            "engine_source_sha256": ENGINE_SOURCE_SHA,
            "search_source_sha256": SEARCH_SOURCE_SHA,
            "bridge_source_sha256": BRIDGE_SOURCE_SHA,
            "adapter_source_sha256": ADAPTER_SHA,
            "adapter_source_bytes": ADAPTER_BYTES,
            "native_engine": build["engine"],
            "native_bridge": build["bridge"],
            "external_cargo_dependency_count": 0,
            "canonical_owners_changed": False,
        },
        "immutable_v4_preworker_failure": {
            "receipt_sha256": V4_FAILURE_SHA, "status": "FAIL",
            "failure_phase": "ROOT_OVERLAY_NONEMPTY_OUTPUT",
            "source_sha256": V4_SOURCE_SHA, "protocol_sha256": V4_PROTOCOL_SHA,
            "contract_sha256": V4_CONTRACT_SHA,
            "candidate_workers_started": 0, "reference_workers_started": 0,
            "candidate_executions": 0,
            "root_cause": "TRUTHY NONEMPTY BYTES MUST BECOME bool(payload)",
            "actual_output_positive_control_required": True,
        },
        "immutable_v32_precompiler_failure": {
            "receipt_sha256": V32_FAILURE_SHA, "status": "FAIL",
            "failure_phase": "AUTHENTICATED_PRIVATE_OVERLAY_VALIDATION",
            "source_sha256": V32_SOURCE_SHA,
            "protocol_sha256": V32_PROTOCOL_SHA,
            "contract_sha256": V32_CONTRACT_SHA,
            "corrected_adapter_sha256": ADAPTER_SHA,
            "inherited_kernel_adapter_sha256":
                "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e",
            "compiler_processes_started": 0,
            "native_build_started": False, "candidate_executions": 0,
        },
        "preserved_original_v26": {
            "receipt_sha256": V26_ORIGINAL_SHA, "candidate_status": "PASS",
            "case_count": 31237, "verified_passing_case_count": 31237,
            "semantic_mismatch_count": 0, "suite_count": 13,
            "candidate_qualified": False,
        },
        "preserved_public_v28": {
            "receipt_sha256": V28_PUBLIC_SHA, "candidate_status": "FAIL",
            "case_count": CASE_COUNT, "mismatch_count": 1145,
            "exact_disjoint_mismatch_partition": dict(PARTITION),
            "scanner_comment_overlap_count": 15,
            "substitution_comment_overlap_count": 12,
            "overlaps_counted_in_disjoint_denominator": False,
            "complete_mismatch_vector_owner_metadata_only":
                history["v28_full_vector"],
            "historical_mismatch_vector_opened": False,
        },
        "preserved_v5_static_audit": {
            "receipt_sha256": V5_AUDIT_SHA,
            "status": "PASS; STATIC SOURCE AND ELF AUDIT ONLY",
            "finding_count": 0, "external_regex_packages": 0,
            "external_regex_libraries": 0, "external_regex_symbols": 0,
            "cross_family_dependencies": 0, "runtime_non_delegation":
                "NOT ESTABLISHED; STATIC SOURCE AND ELF AUDIT ONLY",
            "audited_family_count": 1,
        },
        "actual_entry_policy": {
            "run": "ROOT ONLY AFTER FOUR GATES AND INDEPENDENT COMMIT/PUSH",
            "root_authorized_flag_required": True,
            "frozen_committed_pushed_flag_required": True,
            "frozen_and_pushed_commit_must_match": True,
            "all_v33_source_build_native_root_and_phase_authorities_required": True,
            "canonical_source_and_native_identity_snapshot_before_after": True,
            "isolated_private_overlay_only": True,
            "candidate_qualified_after_public_pass": False,
            "runtime_non_delegation_after_public_pass": "NOT ESTABLISHED",
            "optional_profile_or_timing_available": False,
        },
        "physical_source_wall": {
            "installed_before_first_predecessor_read": True,
            "allowed_scope": "ONLY PINNED tools/ AND oracle/phase2/ PLAINTEXT",
            "all_oracle_phase3_paths_allowed": False,
            "final_proposal_content_opens_allowed": False,
            "final_proposal_metadata_probes_allowed": False,
            "candidate_sources_allowed": False, "native_artifacts_allowed": False,
            "private_roots_allowed": False, "archives_allowed": False,
            "candidate_workers_allowed": False, "clock_access_allowed": False,
            "workspace_mutations_allowed": False,
            "four_source_gates": ["normal verify", "sterile verify",
                                  "normal self-test", "sterile self-test"],
        },
        "source_only_effects": {
            "candidate_workers_started": 0, "reference_workers_started": 0,
            "candidate_imports": 0, "native_libraries_loaded": 0,
            "private_roots_opened": 0, "private_roots_statted": 0,
            "compressed_archives_opened": 0, "proposal_content_opens": 0,
            "proposal_metadata_probes": 0, "hidden_cases_read": 0,
            "hidden_cases_generated": 0, "clock_samples": 0,
            "timing_trials_run": 0, "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_qualified": False, "winner_selected": False,
            "final_holdout": FINAL_HOLDOUT,
        },
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "candidate_qualified": False, "winner_selected": False,
        "final_holdout": FINAL_HOLDOUT,
    }


def load_context(options: dict, wall: PublicWall | None) -> dict:
    rows: dict[str, tuple] = {row[0]: row for row in PUBLIC_OWNERS}
    need(len(rows) == len(PUBLIC_OWNERS), "reject duplicate pinned public owner roles")
    payloads: dict[str, bytes] = {}
    first = rows["v3_gate_source"]
    payloads[first[0]] = owner_read(wall, first)
    module = bootstrap(payloads[first[0]], first)
    for role, row in rows.items():
        if role != first[0]:
            payloads[role] = owner_read(wall, row)
    dynamic = (
        ("source", SOURCE, options["source_sha256"]),
        ("protocol", PROTOCOL, options["protocol_sha256"]),
        ("v33_source", V33_SOURCE_PATH, options["v33_source_sha256"]),
        ("v33_protocol", V33_PROTOCOL_PATH, options["v33_protocol_sha256"]),
        ("v33_contract", V33_CONTRACT_PATH, options["v33_contract_sha256"]),
        ("v33_publication", V33_PUBLICATION_PATH,
         options["v33_publication_sha256"]),
        ("v33_root", V33_ROOT_PATH, options["v33_root_sha256"]),
    )
    for role, relative, fingerprint in dynamic:
        row = live_owner(wall, role, relative, fingerprint)
        rows[role] = row
        payloads[role] = owner_read(wall, row)
    history = validate_history(module, payloads)
    build = validate_build(module, payloads, rows, history)
    freeze = contract_document(rows, history, build,
                               options["source_sha256"],
                               options["protocol_sha256"])
    if options["mode"] != "--render-contract":
        contract_row = live_owner(wall, "contract", CONTRACT,
                                  options["contract_sha256"])
        observed = owner_read(wall, contract_row)
        need(observed == module.document(freeze),
             "reject incomplete, changed, or noncanonical V5 full public freeze")
        rows["contract"] = contract_row
        payloads["contract"] = observed
    if wall is not None:
        need(wall.installed and not wall.live,
             "close every public descriptor before reporting candidate-free provenance")
        sterile_modules()
    return {"module": module, "rows": rows, "payloads": payloads,
            "history": history, "build": build, "freeze": freeze}


def rejected(wall: PublicWall, label: str, operation: object) -> str:
    need(callable(operation), "require a genuine hostile source operation")
    try:
        operation()
    except Exception:
        return label
    raise PublicError("full-public source-only gate accepted: " + label)


def self_test(wall: PublicWall, state: dict) -> dict:
    checks = []
    pure_overlay = "/tmp/" + OVERLAY_PREFIX + "pure-source-control"
    need(output_eligible(pure_overlay + "/candidates/rust_candidate.py",
                         b"first-party-nonempty-adapter") is True,
         "replay the exact V4 nonempty actual adapter path without a source write")
    need(output_eligible(pure_overlay + "/candidates/__init__.py", b"") is True,
         "retain the unique permitted empty first-party package initializer")
    controls = (
        ("candidate-source-open", lambda: os.open(
            ROOT + "/candidates/rust_candidate.py",
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("candidate-variant-open", lambda: os.open(
            ROOT + "/candidates/rust/variants/corrected_comment_adapter_v2/rust_candidate.py",
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("installed-native-open", lambda: os.open(
            ROOT + "/candidates/_rust_engine.so",
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("private-root-open", lambda: os.open(
            state["build"]["private_root"]["path"],
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("compressed-archive-open", lambda: os.open(
            ROOT + "/oracle/phase2/evidence/native-source-build-v33.json.gz",
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("retired-final-proposal-open", lambda: os.open(
            ROOT + "/oracle/phase3/expanded-sealed-holdout-v2.json",
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("successor-final-proposal-open", lambda: os.open(
            ROOT + "/oracle/phase3/expanded-sealed-holdout-v3.json",
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("proposal-metadata", lambda: os.lstat(
            ROOT + "/oracle/phase3/expanded-sealed-holdout-v3.json")),
        ("public-phase-three", lambda: os.open(
            ROOT + "/oracle/phase3/rust-public-practice-benchmark-v2.json",
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("inherited-descriptor", lambda: os.read(0, 1)),
        ("direct-builtins", lambda: builtins.open(ROOT + "/GOAL.md", "rb")),
        ("direct-io", lambda: io.open(ROOT + "/GOAL.md", "rb")),
        ("candidate-import", lambda: __import__("candidates.rust_candidate")),
        ("subprocess-launch", lambda: sys.audit("subprocess.Popen", "rust", [], None, None)),
        ("native-loader", lambda: sys.audit("ctypes.dlopen", "native.so")),
        ("clock", lambda: time.perf_counter_ns()),
        ("entropy", lambda: os.urandom(4)),
        ("directory-metadata", lambda: os.stat(ROOT)),
        ("private-directory-list", lambda: os.listdir("/tmp")),
        ("workspace-mutation", lambda: os.open(
            ROOT + "/oracle/phase2/forbidden-full-public-v4.json",
            os.O_CREAT | os.O_WRONLY, 0o600)),
        ("foreign-dynamic-code", lambda: compile("1", "<foreign>", "exec")),
        ("duplicate-json", lambda: state["module"].json_object(
            b'{"a":1,"a":2}', "duplicate hostile JSON")),
        ("false-commit", lambda: commit("a" * 64, "invalid commit")),
        ("empty-noninitializer-output", lambda: need(
            output_eligible(pure_overlay + "/candidates/rust_candidate.py", b"")
            is True, "reject empty actual candidate adapter output")),
        ("foreign-nonempty-output", lambda: need(
            output_eligible(ROOT + "/forbidden-v5-output", b"nonempty")
            is True, "reject nonempty output outside the V5 exclusive roots")),
        ("truthy-nonbytes-output", lambda: need(
            output_eligible(pure_overlay + "/candidate.py", "nonempty")
            is True, "reject truthy nonbytes actual output")),
        ("false-engine", lambda: native_identity(
            {**state["build"]["phases"][0]["native_outputs"]["engine"],
             "native_loaded": True}, state["build"]["phases"][0], "engine")),
    )
    for name, callback in controls:
        checks.append(rejected(wall, name, callback))
    need(len(checks) == len(controls) and not wall.live,
         "exercise every physically blocked full-public source capability")
    sterile_modules()
    return {"schema": SCHEMA + "-source-self-test", "status": "PASS",
            "hostile_control_count": len(checks), "hostile_controls": checks,
            "blocked_categories": dict(sorted(wall.blocked.items())),
            "source_wall_installed_before_predecessor": True,
            "candidate_workers_started": 0, "reference_workers_started": 0,
            "native_libraries_loaded": 0, "private_roots_opened": 0,
            "proposal_content_opens": 0, "proposal_metadata_probes": 0,
            "archive_opens": 0, "clock_samples": 0,
            "case_execution_denominator": CASE_COUNT,
            "public_operation_count": OPERATIONS_PER_DATASET,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED", "candidate_qualified": False,
            "final_holdout": FINAL_HOLDOUT}


def verify_summary(wall: PublicWall, state: dict, options: dict) -> dict:
    need(wall.installed and not wall.live,
         "close every source descriptor before final isolated source verification")
    sterile_modules()
    return {"schema": SCHEMA + "-source-verification", "status": "PASS",
            "source_sha256": options["source_sha256"],
            "protocol_sha256": options["protocol_sha256"],
            "contract_sha256": options["contract_sha256"],
            "v33_source_sha256": options["v33_source_sha256"],
            "v33_protocol_sha256": options["v33_protocol_sha256"],
            "v33_contract_sha256": options["v33_contract_sha256"],
            "v33_publication_sha256": options["v33_publication_sha256"],
            "v33_root_sha256": options["v33_root_sha256"],
            "preserved_v4_preworker_failure_sha256": V4_FAILURE_SHA,
            "preserved_v32_failure_sha256": V32_FAILURE_SHA,
            "preserved_v26_original_pass_sha256": V26_ORIGINAL_SHA,
            "preserved_v28_public_failure_sha256": V28_PUBLIC_SHA,
            "preserved_v5_static_pass_sha256": V5_AUDIT_SHA,
            "public_case_execution_denominator": CASE_COUNT,
            "public_operation_count": OPERATIONS_PER_DATASET,
            "source_wall_installed_before_predecessor": True,
            "candidate_workers_started": 0, "reference_workers_started": 0,
            "candidate_imports": 0, "native_libraries_loaded": 0,
            "private_roots_opened": 0, "private_root_metadata_probes": 0,
            "compressed_archives_opened": 0, "proposal_content_opens": 0,
            "proposal_metadata_probes": 0, "hidden_cases_read": 0,
            "clock_samples": 0, "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED", "runtime_non_delegation":
                "NOT ESTABLISHED", "candidate_qualified": False,
            "winner_selected": False, "final_holdout": FINAL_HOLDOUT}


def output_eligible(path: object, payload: object) -> bool:
    """Pure exact actual-output predicate; never open or mutate a path."""
    return (type(path) is str and type(payload) is bytes
            and (path.startswith(PUBLIC_OUTPUT + "/")
                 or path.startswith(ROOT + "/oracle/phase2/evidence/")
                 or path.startswith("/tmp/" + OVERLAY_PREFIX))
            and "/../" not in path and 0 <= len(payload) <= MAX_ACTUAL_BYTES
            and (bool(payload) or path.endswith("/candidates/__init__.py")))


def output_write(path: str, payload: bytes, mode: int = 0o600) -> dict:
    need(output_eligible(path, payload) is True,
         "reject an unrelated, oversized, or nonexclusive V5 actual output")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0), mode)
    try:
        view = memoryview(payload)
        while view:
            count = os.write(descriptor, view)
            need(type(count) is int and count > 0,
                 "reject a partial exclusive public correctness publication")
            view = view[count:]
        os.fsync(descriptor)
        info = os.fstat(descriptor)
        need(stat.S_ISREG(info.st_mode)
             and stat.S_IMODE(info.st_mode) == mode and info.st_nlink == 1
             and info.st_size == len(payload),
             "reject a replaced exclusive first-party public correctness output")
        return {"path": path, "sha256": digest(payload), "bytes": len(payload),
                "device": info.st_dev, "inode": info.st_ino,
                "mode": format(mode, "04o"), "exclusive_creation": True,
                "file_fsync_completed": True}
    finally:
        os.close(descriptor)


def actual_authority(options: dict, state: dict) -> None:
    build = state["build"]
    native = build["engine"], build["bridge"]
    required = {
        "v33_private_root": build["private_root"]["path"],
        "v33_private_root_device": str(PRIVATE_DEVICE),
        "v33_private_root_inode": str(build["private_root"]["inode"]),
        "v33_native_engine_sha256": native[0]["sha256"],
        "v33_native_engine_bytes": str(native[0]["bytes"]),
        "v33_native_bridge_sha256": native[1]["sha256"],
        "v33_native_bridge_bytes": str(native[1]["bytes"]),
        "v33_engine_source_sha256": ENGINE_SOURCE_SHA,
        "v33_search_source_sha256": SEARCH_SOURCE_SHA,
        "v33_bridge_source_sha256": BRIDGE_SOURCE_SHA,
        "v33_adapter_sha256": ADAPTER_SHA,
        "v33_adapter_bytes": str(ADAPTER_BYTES),
        "v32_failure_sha256": V32_FAILURE_SHA,
        "v26_original_pass_sha256": V26_ORIGINAL_SHA,
        "v28_public_failure_sha256": V28_PUBLIC_SHA,
        "v5_static_pass_sha256": V5_AUDIT_SHA,
        "v4_failure_sha256": V4_FAILURE_SHA,
    }
    for key, value in required.items():
        need(options.get(key) == value,
             "require independently root-pinned actual full public authority: " + key)
    need(options.get("root_authorized") is True
         and options.get("frozen_committed_pushed") is True
         and commit(options.get("frozen_commit"), "frozen V5 commit")
         == commit(options.get("pushed_commit"), "pushed V5 commit"),
         "root alone may run after exact V4 source triple is committed and pushed")
    session = options.get("session")
    need(type(session) is str and 1 <= len(session) <= 80
         and session.startswith("v33-")
         and all(item in "abcdefghijklmnopqrstuvwxyz0123456789-"
                 for item in session)
         and not any(item in session for item in
                     ("holdout", "sealed", "hidden", "final")),
         "require a fresh exclusive explicitly public V33 correctness session")


def exact_private(module: types.ModuleType, path: str, owner: dict,
                  role: str, mode: int = 0o600) -> bytes:
    return module.exact_file(path, expected_sha=owner["sha256"],
                             expected_bytes=owner["bytes"],
                             device=PRIVATE_DEVICE, inode=owner["inode"],
                             mode=mode, role=role)


def run_actual(options: dict, state: dict) -> dict:
    actual_authority(options, state)
    module = state["module"]
    phase = state["build"]["phases"][0]
    private = state["build"]["private_root"]
    root_info = os.stat(private["path"], follow_symlinks=False)
    need(stat.S_ISDIR(root_info.st_mode)
         and stat.S_IMODE(root_info.st_mode) == 0o700
         and root_info.st_dev == PRIVATE_DEVICE
         and root_info.st_ino == private["inode"]
         and root_info.st_uid == os.geteuid()
         and os.path.realpath(private["path"]) == private["path"],
         "reject changed exact independently caller-pinned V33 private build root")
    phase_info = os.stat(phase["absolute_path"], follow_symlinks=False)
    need(stat.S_ISDIR(phase_info.st_mode)
         and stat.S_IMODE(phase_info.st_mode) == 0o700
         and phase_info.st_dev == PRIVATE_DEVICE
         and phase_info.st_ino == phase["inode"]
         and phase_info.st_uid == os.geteuid(),
         "reject substituted live first independently built V33 source phase")
    canonical_before = module.snapshot_canonical()
    corrected_sources = {}
    for relative, owner in phase["source_owners"].items():
        corrected_sources[relative] = exact_private(
            module, phase["absolute_path"] + "/source/" + relative,
            owner, "V33 corrected first-party source " + relative,
        )
    adapter = corrected_sources["candidates/rust_candidate.py"]
    engine = exact_private(module, phase["native_outputs"]["engine"]["absolute_path"],
                           phase["native_outputs"]["engine"],
                           "independently reproduced V33 native engine")
    bridge = exact_private(module, phase["native_outputs"]["bridge"]["absolute_path"],
                           phase["native_outputs"]["bridge"],
                           "independently reproduced V33 first-party bridge", 0o700)
    import tempfile
    overlay = tempfile.mkdtemp(prefix=OVERLAY_PREFIX, dir="/tmp")
    need(os.path.realpath(overlay) == overlay
         and stat.S_IMODE(os.stat(overlay).st_mode) == 0o700,
         "create only a fresh owner-only isolated public candidate overlay")
    os.mkdir(overlay + "/tools", 0o700)
    os.mkdir(overlay + "/candidates", 0o700)
    output_write(overlay + "/candidates/__init__.py", b"", 0o600)
    output_write(overlay + "/candidates/rust_candidate.py", adapter, 0o600)
    output_write(overlay + "/candidates/_rust_engine.so", engine, 0o600)
    output_write(overlay + "/candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
                 bridge, 0o700)
    output_write(overlay + "/tools/rust_public_practice_benchmark_v2.py",
                 state["payloads"]["public_harness"], 0o600)

    try:
        os.mkdir(PUBLIC_OUTPUT, 0o700)
    except FileExistsError:
        directory = os.stat(PUBLIC_OUTPUT, follow_symlinks=False)
        need(stat.S_ISDIR(directory.st_mode)
             and stat.S_IMODE(directory.st_mode) == 0o700
             and directory.st_uid == os.geteuid(),
             "reject substituted public-correctness V4 evidence parent")
    session = str(options["session"])
    target = PUBLIC_OUTPUT + "/" + session
    os.mkdir(target, 0o700)
    original_bootstrap = module.WORKER_BOOTSTRAP
    old_prefix = "rebar-rust-native-public-v3-"
    need(original_bootstrap.count(old_prefix) == 1,
         "retain the exact independently frozen genuine public V3 worker bootstrap")
    module.WORKER_BOOTSTRAP = original_bootstrap.replace(old_prefix, OVERLAY_PREFIX)
    harness = module.load_harness(state["payloads"]["public_harness"], overlay,
                                  "rust_public_practice_benchmark_v2.py")
    actual_workers: dict[str, tuple[dict, bytes]] = {}

    def isolated(role: str, engine_name: str,
                 operation: str, **_keywords: object) -> dict:
        need(engine_name in ("stdlib", "rust") and operation == "observe",
             "execute only complete untimed separately isolated public observations")
        value, payload = module.run_worker(
            overlay, "rust_public_practice_benchmark_v2.py", PUBLIC_HARNESS_SHA,
            "v33-" + role, engine_name, "observe",
        )
        actual_workers[engine_name] = (value, payload)
        return value

    harness.run_isolated_worker = isolated
    full = harness.run_correctness_only()
    rows = full.get("all_mismatches")
    need(type(full) is dict and full.get("status") in ("PASS", "FAIL")
         and full.get("case_denominator") == CASE_COUNT
         and full.get("actual_baseline_cases") == CASE_COUNT
         and full.get("actual_rust_cases") == CASE_COUNT
         and full.get("published_seed") == PUBLISHED_SEED
         and full.get("matrix_sha256") == MATRIX_SHA
         and full.get("actual_candidate_workers") == 1
         and type(rows) is list and len(rows) == full.get("mismatch_count")
         and full.get("status") == ("PASS" if not rows else "FAIL")
         and set(actual_workers) == {"stdlib", "rust"}
         and actual_workers["stdlib"][0].get("case_count") == CASE_COUNT
         and actual_workers["rust"][0].get("case_count") == CASE_COUNT
         and actual_workers["stdlib"][0].get("pid")
             != actual_workers["rust"][0].get("pid")
         and full.get("timing_trials_run") == 0
         and full.get("clock_samples") == 0
         and full.get("hidden_cases_read") == 0
         and full.get("archive_files_read") == 0,
         "run all 10,434 genuine public cases and preserve every actual mismatch")
    artifacts = [
        output_write(target + "/public-10434-stdlib.correctness.raw.json",
                     actual_workers["stdlib"][1]),
        output_write(target + "/public-10434-rust.correctness.raw.json",
                     actual_workers["rust"][1]),
        output_write(target + "/public-10434-correctness.raw.json",
                     harness.canonical(full)),
    ]
    canonical_after = module.snapshot_canonical()
    need(canonical_before == canonical_after,
         "preserve every original canonical Rust source, adapter, and native inode")
    candidate_status = full["status"]
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt", "version": VERSION,
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": candidate_status,
        "public_10434_correctness_status": candidate_status,
        "public_10434_case_count": CASE_COUNT,
        "public_10434_verified_passing_case_count": CASE_COUNT - len(rows),
        "public_10434_mismatch_count": len(rows),
        "public_api_operation_count": OPERATIONS_PER_DATASET,
        "public_dataset_count": DATASET_COUNT,
        "published_seed": PUBLISHED_SEED, "matrix_sha256": MATRIX_SHA,
        "all_public_cases_observed": True,
        "all_public_mismatches_preserved": True,
        "baseline_pid": actual_workers["stdlib"][0]["pid"],
        "rust_pid": actual_workers["rust"][0]["pid"],
        "candidate_worker_count": 1, "reference_worker_count": 1,
        "source_sha256": options["source_sha256"],
        "protocol_sha256": options["protocol_sha256"],
        "contract_sha256": options["contract_sha256"],
        "frozen_commit": options["frozen_commit"],
        "pushed_commit": options["pushed_commit"],
        "v33_source_sha256": options["v33_source_sha256"],
        "v33_protocol_sha256": options["v33_protocol_sha256"],
        "v33_contract_sha256": options["v33_contract_sha256"],
        "v33_publication_sha256": options["v33_publication_sha256"],
        "v33_root_sha256": options["v33_root_sha256"],
        "v33_native_engine_sha256": state["build"]["engine"]["sha256"],
        "v33_native_bridge_sha256": state["build"]["bridge"]["sha256"],
        "v33_adapter_sha256": ADAPTER_SHA,
        "v4_preworker_failure_sha256": V4_FAILURE_SHA,
        "v32_precompiler_failure_sha256": V32_FAILURE_SHA,
        "v26_original_pass_sha256": V26_ORIGINAL_SHA,
        "v26_original_verified_passing_case_count": 31237,
        "v28_public_failure_sha256": V28_PUBLIC_SHA,
        "v28_historical_public_mismatch_count": 1145,
        "v28_historical_exact_disjoint_mismatch_partition": dict(PARTITION),
        "v28_historical_scanner_comment_overlap_count": 15,
        "v28_historical_substitution_comment_overlap_count": 12,
        "v5_static_pass_sha256": V5_AUDIT_SHA,
        "v5_static_external_regex_package_count": 0,
        "v5_static_external_regex_library_count": 0,
        "v5_static_external_regex_symbol_count": 0,
        "canonical_candidates_before": canonical_before,
        "canonical_candidates_after": canonical_after,
        "canonical_candidate_modified": False,
        "private_overlay": overlay, "session": session,
        "artifacts": artifacts, "timing_trials_run": 0,
        "clock_samples": 0, "paired_row_count": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False, "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "proposal_content_opens": 0, "proposal_metadata_probes": 0,
        "hidden_cases_read": 0, "hidden_cases_generated": 0,
        "winner_selected": False, "final_holdout": FINAL_HOLDOUT,
    }
    receipt_name = ROOT + "/oracle/phase2/evidence/rust-full-public-correctness-v5-"
    receipt_owner = output_write(receipt_name + session + "-publication-receipt.json",
                                 harness.canonical(receipt))
    return {"schema": SCHEMA + "-actual-root-operation",
            "status": candidate_status, "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": candidate_status,
            "public_10434_correctness_status": candidate_status,
            "public_10434_case_count": CASE_COUNT,
            "public_10434_verified_passing_case_count": CASE_COUNT - len(rows),
            "public_10434_mismatch_count": len(rows),
            "public_api_operation_count": OPERATIONS_PER_DATASET,
            "reference_worker_count": 1, "candidate_worker_count": 1,
            "v33_publication_sha256": options["v33_publication_sha256"],
            "v33_root_sha256": options["v33_root_sha256"],
            "v4_preworker_failure_sha256": V4_FAILURE_SHA,
            "v32_precompiler_failure_sha256": V32_FAILURE_SHA,
            "v26_original_verified_passing_case_count": 31237,
            "v28_historical_public_mismatch_count": 1145,
            "v28_historical_exact_disjoint_mismatch_partition": dict(PARTITION),
            "v5_static_pass_sha256": V5_AUDIT_SHA,
            "canonical_candidate_modified": False,
            "publication_receipt": receipt_owner,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_qualified": False, "hidden_cases_read": 0,
            "proposal_content_opens": 0, "winner_selected": False,
            "final_holdout": FINAL_HOLDOUT}


def parse_options(values: list[str]) -> dict:
    need(bool(values), "select exactly one explicit V5 source-only or root-only mode")
    modes = [item for item in values if item in SOURCE_MODES + ACTUAL_MODES]
    need(len(modes) == 1,
         "select exactly one candidate-free source gate or separately authorized actual run")
    result: dict[str, object] = {"mode": modes[0]}
    index = 0
    while index < len(values):
        flag = values[index]
        if flag in SOURCE_MODES + ACTUAL_MODES:
            index += 1
            continue
        if flag in ("--root-authorized", "--frozen-committed-pushed"):
            key = flag[2:].replace("-", "_")
            need(key not in result,
                 "reject repeated explicit root-only public authorization")
            result[key] = True
            index += 1
            continue
        need(flag.startswith("--") and index + 1 < len(values),
             "reject positional or incomplete independently pinned V5 authority")
        key = flag[2:].replace("-", "_")
        need(key not in result,
             "reject duplicate independently pinned public authority: " + flag)
        result[key] = values[index + 1]
        index += 2
    source_names = {"source_sha256", "protocol_sha256", "v33_source_sha256",
                    "v33_protocol_sha256", "v33_contract_sha256",
                    "v33_publication_sha256", "v33_root_sha256"}
    if result["mode"] != "--render-contract":
        source_names.add("contract_sha256")
    for key in source_names:
        sha(result.get(key), key)
    if result["mode"] in SOURCE_MODES:
        need(set(result) == {"mode", *source_names},
             "source-only mode may not authorize candidates, private roots, or clocks")
    else:
        extras = {"root_authorized", "frozen_committed_pushed", "frozen_commit",
                  "pushed_commit", "session", "v33_private_root",
                  "v33_private_root_device", "v33_private_root_inode",
                  "v33_native_engine_sha256", "v33_native_engine_bytes",
                  "v33_native_bridge_sha256", "v33_native_bridge_bytes",
                  "v33_engine_source_sha256", "v33_search_source_sha256",
                  "v33_bridge_source_sha256", "v33_adapter_sha256",
                  "v33_adapter_bytes", "v32_failure_sha256",
                  "v26_original_pass_sha256", "v28_public_failure_sha256",
                  "v5_static_pass_sha256", "v4_failure_sha256"}
        need(set(result) == {"mode", *source_names, *extras},
             "independently pin every root-only V33 public correctness authority")
        need(result.get("root_authorized") is True
             and result.get("frozen_committed_pushed") is True,
             "require explicit root approval after frozen triple commit and push")
        commit(result.get("frozen_commit"), "frozen V5 commit")
        commit(result.get("pushed_commit"), "pushed V5 commit")
        for key in extras:
            if key.endswith("_sha256"):
                sha(result.get(key), key)
    return result


def main(arguments: list[str]) -> int:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode is True
         and os.path.abspath(sys.executable) == PYTHON
         and os.path.realpath(sys.executable) == PYTHON,
         "use only exact isolated, no-site, no-bytecode pinned CPython 3.14.6")
    sterile_modules()
    options = parse_options(arguments)
    wall = PublicWall() if options["mode"] in SOURCE_MODES else None
    if wall is not None:
        wall.install()
    state = load_context(options, wall)
    if options["mode"] == "--render-contract":
        assert wall is not None
        need(not wall.live, "close every public descriptor before canonical rendering")
        result = state["freeze"]
    elif options["mode"] == "--verify-frozen-context":
        assert wall is not None
        result = verify_summary(wall, state, options)
    elif options["mode"] == "--self-test":
        assert wall is not None
        result = self_test(wall, state)
    else:
        result = run_actual(options, state)
    sys.stdout.buffer.write(state["module"].document(result))
    sys.stdout.buffer.flush()
    return 0 if result.get("status") == "PASS" or options["mode"] == "--render-contract" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (PublicError, OSError, ValueError, TypeError, KeyError,
            SyntaxError) as error:
        sys.stderr.write("full Rust public correctness V5 rejected: " + str(error) + "\n")
        raise SystemExit(2)
