#!/usr/bin/env python3
"""Freeze and reproducibly build the genuinely first-party Rust anchor engine.

Source-only modes physically admit only individually pinned public source and
development evidence.  They do not enter a private root, touch native files,
start a compiler/candidate, sample a clock, or open an archive/holdout.  Only
an independently pinned, explicitly root-authorized actual build may compose
the two owned Rust anchor variants with the existing safe clamp bridge and
corrected Python adapter in the original 28-process offline build kernel.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("source-only native-build verification must not import regex")

import _io
import builtins
import hashlib
import io
import os
import stat
import time
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
DEVICE = 2064
SOURCE = "tools/reproduce_owned_rust_anchor_source_build_v26.py"
PROTOCOL = "oracle/phase2/RUST-ANCHOR-SOURCE-BUILD-V26.md"
CONTRACT = "oracle/phase2/rust-anchor-source-build-v26.json"
SCHEMA = "rebar-phase2-owned-rust-anchor-source-build-v26"
VERSION = 26
FAMILY = "rust"
NOT_MEASURED = "NOT MEASURED"
MAX_SOURCE_BYTES = 2 * 1024 * 1024
LABEL = "phase2-v26-rust-mandatory-anchor-root-provenance"
EVIDENCE_DIRECTORY = "oracle/phase2/evidence"
ROOT_PREFIX = "rebar-phase2-native-build-v9-rust-"
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)
GOAL_SHA = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
ANCHOR_LIB_SHA = "5fa8c47c88c1f5d830a59735946378910374afab6f1558d281f0254207ad5e84"
ANCHOR_LIB_BYTES = 189369
ANCHOR_SEARCH_SHA = "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7"
ANCHOR_SEARCH_BYTES = 24305
BRIDGE_SHA = "a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54"
BRIDGE_BYTES = 178805
ADAPTER_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
ADAPTER_BYTES = 31934
V25_RECEIPT_SHA = "55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc"
V25_ROOT_SHA = "e8633ac1224235db9f8ea48c683c833fba3015cd73f071cd2488fa0b13a117a2"
V25_CANDIDATE_FAILURE_SHA = "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59"
V24_FAILURE_SHA = "5acd8dee2a515af56306e61f6ae8774c567f1f47e0ef1930a17e6809c2aafa09"
STRICT_AUDIT_FAILURE_SHA = "c3020fe067ad06c2bf7309a73b960884572addd9e984d01d2cf27d5cd9d61f19"
SEALED_PROPOSAL_SHA = "5d9fa3920c1dcabc92a3521d742cd10ec399cff1a979b71ac079daba6f92cba0"
SEALED_PROPOSAL_CASE_COUNT = 141557760
PUBLIC_MATRIX_SHA = "b13ff74122041ea792774fd5ee2d1f6d38033e94a1a6703c6e48522e461552a7"
PUBLIC_RECORDS_SHA = "41f83dc761a93ea8e3203f46cedbba1e10918cf053194c20b37b8c209e992242"

# Every owner is a complete, already committed public plaintext source,
# contract, source variant, or development-practice result.  No private root,
# compressed archive, installed native library, or final case corpus is named.
CANONICAL_OWNERS = (
    ("cargo_lock", "candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, 428098),
    ("cargo_manifest", "candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, 428094),
    ("original_bridge", "candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676, 419054),
    ("original_lib", "candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967, 428096),
    ("original_newline", "candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416, 427958),
    ("original_search", "candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773, 429682),
    ("original_stack", "candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269, 428151),
    ("original_unicode", "candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989, 428152),
    ("original_adapter", "candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151, 428100),
)

PHASE_ONE_OWNERS = (
    ("phase1_source", "tools/verify_owned_p0_completeness_v4.py", "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d", 29094, 428927),
    ("phase1_protocol", "oracle/phase1/P0-COMPLETENESS-V4.md", "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2", 4261, 524712),
    ("phase1_contract", "oracle/phase1/p0-completeness-v4.json", "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
)

V25_OWNERS = (
    ("v25_source", "tools/reproduce_owned_rust_capture_clamp_source_build_v25.py", "f0a5d0b0af76b83e4f7091050afc187458c8c4380a37418f5df0de41d882b408", 186263, 429530),
    ("v25_protocol", "oracle/phase2/RUST-CAPTURE-CLAMP-SOURCE-BUILD-V25.md", "ddc7c1fcf385ec979c73a304123025a6e5974a8eb37dd61cf189ccba20687f85", 7140, 525993),
    ("v25_contract", "oracle/phase2/rust-capture-clamp-source-build-v25.json", "528d2bcccb2cceed5f607f7ec8428b18df10f30b9b6b6f7313083a288061127a", 229419, 526066),
    ("v25_success_receipt", "oracle/phase2/evidence/native-source-build-v25-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-publication-receipt.json", V25_RECEIPT_SHA, 5231, 526084),
    ("v25_root_receipt", "oracle/phase2/evidence/native-source-build-v25-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-root-provenance-receipt.json", V25_ROOT_SHA, 61798, 526085),
    ("v25_candidate_failure", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json", V25_CANDIDATE_FAILURE_SHA, 11832, 524846),
)

ANCHOR_OWNERS = (
    ("anchor_source", "tools/apply_owned_rust_mandatory_anchor_search_v1.py", "d118af0c0da3b058fc8d40a59d47090a97fd8838fcbdb0fba36bcd0271da2eff", 74375, 429756),
    ("anchor_protocol", "oracle/phase2/RUST-MANDATORY-ANCHOR-SEARCH-V1.md", "85d65a26042f8e084f52a4037ad2267dd4f59e1e6166a9694b56703960af148e", 3253, 526101),
    ("anchor_contract", "oracle/phase2/rust-mandatory-anchor-search-v1.json", "25a7a5ea578c2c6a54eae6635c0869bdc3eaed6d1a8cce46b77c1d752ea04249", 1591, 526102),
    ("anchor_application", "oracle/phase2/evidence/rust-mandatory-anchor-search-v1-application.json", "c4396052f94a76f67088678cd0a5176bb70c1d917675fbc03353806047ca20bb", 1871, 526183),
    ("anchor_lib", "candidates/rust/variants/mandatory_anchor_search_v1/lib.rs", ANCHOR_LIB_SHA, ANCHOR_LIB_BYTES, 526181),
    ("anchor_search", "candidates/rust/variants/mandatory_anchor_search_v1/search.rs", ANCHOR_SEARCH_SHA, ANCHOR_SEARCH_BYTES, 526182),
)

CLAMP_OWNERS = (
    ("clamp_source", "tools/apply_owned_rust_capture_clamp_semantics_v1.py", "ff4b45f370bb6df1a3693cb1046031df93f3dffb336f4cca695768a1adb34fb7", 71522, 429579),
    ("clamp_protocol", "oracle/phase2/RUST-CAPTURE-CLAMP-SEMANTICS-V1.md", "15bd3b25b3f86638ddcb45cbc11d962341a905903a4cd52a632f6c3f1a078ff9", 4645, 526033),
    ("clamp_contract", "oracle/phase2/rust-capture-clamp-semantics-v1.json", "46344723f24c65c123c4550c9652b3547866a2ae1a8419444d3359eb048294c6", 11342, 526034),
    ("clamp_application", "oracle/phase2/evidence/rust-capture-clamp-semantics-v1-application.json", "881c8b3583509f341f4851734a87f7e1e536c88ace7ae04473326b6a3a6d06df", 2426, 526065),
    ("safe_clamp_bridge", "candidates/rust/variants/capture_clamp_semantics_v1/py_bridge.c", BRIDGE_SHA, BRIDGE_BYTES, 526064),
)

GUARD_OWNERS = (
    ("guard_source", "tools/verify_owned_candidate_runtime_independence_v4.py", "5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3", 48687, 429243),
    ("guard_protocol", "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md", "835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16", 4492, 525890),
    ("guard_contract", "oracle/phase2/candidate-runtime-independence-v4.json", "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2", 9352, 525891),
)

AUDIT_OWNERS = (
    ("strict_audit_source", "tools/audit_candidate_runtime_non_delegation_v4.py", "597f2f1156d773a42e32103ef7370e8552a416756910c013cdcd0cfc34d39b02", 121807, 429582),
    ("strict_audit_protocol", "oracle/phase2/RUNTIME-NON-DELEGATION-V4.md", "6c3bd6b2ccabe3ab240771d743afce5b32f1de17a510bedd835e867c5cea7826", 5325, 526087),
    ("strict_audit_contract", "oracle/phase2/runtime-non-delegation-v4.json", "edc3ac8866da7afb5934b56fbcbff38a908e5109f7975f998753b479aa7bc672", 7266, 526086),
    ("strict_audit_actual_failure", "oracle/phase2/evidence/runtime-non-delegation-v4-actual-source-audit-failure.json", STRICT_AUDIT_FAILURE_SHA, 20985, 526140),
)

HOLDOUT_OWNERS = (
    ("proposal_source", "tools/verify_expanded_sealed_holdout_v2.py", "48d39e0a39a835c9876344591f8b4b63cfad336c3b4e1b1dd2164255763b33f7", 50749, 429450),
    ("proposal_protocol", "oracle/phase3/EXPANDED-SEALED-HOLDOUT-V2.md", "96c6edae1fe959faa59079ada499bb98173101171c8c377e900eba7bb2673c38", 19395, 525919),
    ("proposal_contract", "oracle/phase3/expanded-sealed-holdout-v2.json", SEALED_PROPOSAL_SHA, 15561, 525920),
)

PUBLIC_OWNERS = (
    ("goal", "GOAL.md", GOAL_SHA, 3756, 31364044),
    ("v24_failure", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v24-rust-capture-shape-v2-root-provenance-original-p0-v24-failures-publication-receipt.json", V24_FAILURE_SHA, 11832, 525952),
    ("practice_graph", "docs/evidence/rust-public-practice-overall-v1.inputs.json", "ebcbce1c46a7c36be2b50e49c90e826f90b1822055c10fa89bf3984566be70fc", 16044, 429788),
    ("practice_failure", "oracle/phase3/evidence/rust-public-profile-v1-run-001-prepublication-failure.json", "ac244e241d3ec9fa1d738030a1637942012e238c586053152d6ba088f82aadba", 502796, 526089),
    ("practice_rust", "experiments/rust_public_profile_v1/public-run-001/rust.correctness.raw.json", "8774ad035e17126252803e75494a80d376386a85e13c46cb3e0380b82dae89b0", 445394, 526006),
    ("practice_python", "experiments/rust_public_profile_v1/public-run-001/stdlib.correctness.raw.json", "efe0a3cc37194290b9577d5bd4f502a5c482016bc2b8ae90acec6254545b5381", 445036, 526005),
    ("practice_timings", "experiments/rust_public_profile_v1/public-run-001/paired-timing.raw.json", "3da06bdb04ace9897d359aaa962ca412f3e9260a5c1a337703e0aa35567b6b85", 504907, 526015),
    ("public_profile_manifest", "oracle/phase3/rust-public-profile-v1.json", "b791b141eabbf6eb8a67484f5deb82bb41e324aedbdfe5b53a98ebc1553372c5", 1797, 525928),
    ("owned_simd_search_research", "tools/rust_search_lab.rs", "45726e1ba3e4864ef64b441eb63c67d68729a43be3bd2f02682453fe113c35c7", 20573, 429633),
    ("owned_simd_search_results", "candidates/evidence/RUST-V6-SEARCH-LAB.md", "dfa25003ab643cbd1012943771a1364d34f7d9b3c170d4022e6a26f18b17b8b0", 4725, 429638),
)

OWNERS = (CANONICAL_OWNERS + PHASE_ONE_OWNERS + V25_OWNERS
          + ANCHOR_OWNERS + CLAMP_OWNERS + GUARD_OWNERS
          + AUDIT_OWNERS + HOLDOUT_OWNERS + PUBLIC_OWNERS)
ALLOWED = frozenset(ROOT + "/" + row[1] for row in OWNERS) | {
    ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL, ROOT + "/" + CONTRACT,
}
WALL_ACTIVE = False
WALL_INSTALLED = False
SOURCE_DESCRIPTORS: set[int] = set()
ORIGINAL_OS_READ = os.read
BLOCKED = {name: 0 for name in (
    "candidate", "native", "process", "clock", "write", "private_root",
    "archive_holdout", "foreign_read", "network",
)}
ROOT_CAPTURE: dict[str, object] | None = None


class BuildFreezeError(Exception):
    """The first-party source-only freeze or real dual build failed closed."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise BuildFreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete immutable owner bytes")
    return hashlib.sha256(raw).hexdigest()


def hash_pin(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value)
            and len(set(value)) > 1,
            "a real lowercase SHA-256 is mandatory: " + label)
    return value


def deny(kind: str, reason: str) -> None:
    BLOCKED[kind] += 1
    raise BuildFreezeError("the physical V26 source wall rejected " + reason)


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if not WALL_ACTIVE:
        return
    if event == "open":
        path = arguments[0] if arguments else None
        mode = arguments[1] if len(arguments) > 1 else None
        flags = arguments[2] if len(arguments) > 2 else 0
        if (type(mode) is str and any(letter in mode for letter in "wax+")) or (
            type(flags) is int and (
                flags & os.O_ACCMODE != os.O_RDONLY
                or flags & (os.O_CREAT | os.O_EXCL | os.O_TRUNC | os.O_APPEND)
            )
        ):
            deny("write", "a source-mode filesystem mutation")
        if type(path) is not str or path not in ALLOWED:
            spelling = path.lower() if type(path) is str else "descriptor"
            if spelling.startswith("/tmp/"):
                deny("private_root", "a historical or future private build root")
            if any(value in spelling for value in
                   ("archive", "holdout", "sealed", "hidden", "fixture", ".gz")):
                deny("archive_holdout", "a hidden case, compressed archive, or holdout")
            if spelling.endswith((".so", ".dylib", ".dll")):
                deny("native", "an installed or private native candidate")
            if "candidate" in spelling:
                deny("candidate", "an unapproved candidate source or runtime owner")
            deny("foreign_read", "an unapproved source owner")
        if type(flags) is not int or not flags & os.O_NOFOLLOW:
            deny("foreign_read", "a symlink-following approved source-owner descriptor")
    elif event == "import":
        deny("native", "a late candidate, regex, or native import")
    elif event == "compile":
        filename = arguments[1] if len(arguments) > 1 else None
        if type(filename) is not str or filename not in ALLOWED:
            deny("candidate", "compilation of unapproved candidate or executable code")
    elif event == "exec":
        filename = getattr(arguments[0], "co_filename", None) if arguments else None
        if type(filename) is not str or filename not in ALLOWED:
            deny("candidate", "execution of unapproved candidate or executable code")
    elif event.startswith(("subprocess.", "os.posix_spawn", "os.spawn",
                           "os.exec", "os.fork", "os.system", "_interpreters.",
                           "cpython.PyInterpreterState_New", "threading.",
                           "_thread.")):
        deny("process", "a compiler, candidate, profiler, or oracle process")
    elif event.startswith(("ctypes.", "os.dlopen", "marshal.loads")):
        deny("native", "a native library load")
    elif event.startswith("socket."):
        deny("network", "network access")
    elif event.startswith(("os.mkdir", "os.rmdir", "os.remove", "os.unlink",
                           "os.rename", "os.replace", "os.chmod", "os.chown",
                           "os.link", "os.symlink", "os.truncate", "shutil.")):
        deny("write", "source-mode workspace mutation")
    elif event in ("os.listdir", "os.scandir", "glob.glob"):
        deny("foreign_read", "directory or private-root enumeration")


def no_clock(*_args: object, **_kwargs: object) -> object:
    deny("clock", "a clock, timing trial, or sleep")


def source_read(descriptor: int, length: int, /) -> bytes:
    if WALL_ACTIVE and (type(descriptor) is not int
                        or descriptor not in SOURCE_DESCRIPTORS):
        deny("foreign_read", "an inherited, hidden, or unapproved source descriptor")
    return ORIGINAL_OS_READ(descriptor, length)


def install_wall() -> None:
    global WALL_ACTIVE, WALL_INSTALLED
    require(WALL_INSTALLED is False, "the irreversible source wall was reused")
    sys.addaudithook(audit_wall)
    WALL_ACTIVE = True
    WALL_INSTALLED = True
    os.read = source_read
    for name in ("time", "time_ns", "clock_gettime", "clock_gettime_ns",
                 "clock_settime", "clock_settime_ns",
                 "ctime", "gmtime", "localtime", "strftime",
                 "perf_counter", "perf_counter_ns", "monotonic",
                 "monotonic_ns", "process_time", "process_time_ns", "thread_time",
                 "thread_time_ns", "sleep"):
        if hasattr(time, name):
            setattr(time, name, no_clock)
    if hasattr(os, "times"):
        os.times = no_clock


def owned(row: tuple[object, ...]) -> tuple[bytes, dict[str, object]]:
    require(type(row) is tuple and len(row) == 5, "a frozen source owner is required")
    role, relative, expected, size, inode = row
    require(type(role) is str and type(relative) is str and relative
            and not relative.startswith("/") and ".." not in relative.split("/")
            and type(size) is int and 0 < size <= MAX_SOURCE_BYTES
            and type(inode) is int and inode > 0,
            "a frozen owner path, size, or identity changed")
    hash_pin(expected, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    SOURCE_DESCRIPTORS.add(descriptor)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == size and before.st_uid == os.geteuid()
                and before.st_nlink == 1,
                "an independently frozen first-party source owner changed: " + role)
        parts: list[bytes] = []
        remaining = size
        while remaining:
            item = os.read(descriptor, min(remaining, 65536))
            require(type(item) is bytes and bool(item),
                    "a frozen owner ended before its complete byte count")
            parts.append(item)
            remaining -= len(item)
        require(os.read(descriptor, 1) == b"", "a frozen owner grew during verification")
        after = os.fstat(descriptor)
        require(all(getattr(before, field) == getattr(after, field)
                    for field in ("st_dev", "st_ino", "st_size", "st_nlink",
                                  "st_mtime_ns", "st_ctime_ns")),
                "a frozen owner changed while its no-follow descriptor was open")
    finally:
        SOURCE_DESCRIPTORS.discard(descriptor)
        os.close(descriptor)
    raw = b"".join(parts)
    require(digest(raw) == expected, "a frozen owner SHA-256 changed: " + role)
    return raw, {"role": role, "path": relative, "sha256": expected,
                 "bytes": size, "device": before.st_dev, "inode": before.st_ino,
                 "mode": "0600", "nlink": before.st_nlink, "uid": before.st_uid}


def dynamic(relative: str, expected: str) -> tuple[bytes, dict[str, object]]:
    hash_pin(expected, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    SOURCE_DESCRIPTORS.add(descriptor)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode) and stat.S_IMODE(identity.st_mode) == 0o600
                and identity.st_dev == DEVICE and identity.st_uid == os.geteuid()
                and identity.st_nlink == 1 and 0 < identity.st_size <= MAX_SOURCE_BYTES,
                "an independently pinned dynamic V26 owner changed")
        actual = b""
        while len(actual) < identity.st_size:
            part = os.read(descriptor, min(65536, identity.st_size - len(actual)))
            require(bool(part), "a dynamic V26 owner ended early")
            actual += part
        require(os.read(descriptor, 1) == b"", "a dynamic V26 owner grew")
        observed = os.fstat(descriptor)
        require(all(getattr(identity, field) == getattr(observed, field)
                    for field in ("st_dev", "st_ino", "st_size", "st_nlink",
                                  "st_mtime_ns", "st_ctime_ns")),
                "a pinned dynamic V26 owner changed during authentication")
    finally:
        SOURCE_DESCRIPTORS.discard(descriptor)
        os.close(descriptor)
    require(digest(actual) == expected, "a dynamic V26 source hash changed")
    return actual, {"path": relative, "sha256": expected, "bytes": len(actual),
                    "device": identity.st_dev, "inode": identity.st_ino,
                    "mode": "0600", "uid": identity.st_uid, "nlink": identity.st_nlink}


def load_anchor_transformer(raw: bytes) -> types.ModuleType:
    name = "_rebar_v26_read_only_frozen_anchor_source"
    require(name not in sys.modules, "the independently frozen anchor source was reused")
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + ANCHOR_OWNERS[0][1]
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    require(module.SCHEMA == "rebar-owned-rust-mandatory-anchor-search-v1"
            and module.SOURCE == ANCHOR_OWNERS[0][1]
            and module.PROTOCOL == ANCHOR_OWNERS[1][1]
            and module.CONTRACT == ANCHOR_OWNERS[2][1]
            and callable(module.transform_engine)
            and callable(module.transform_search)
            and callable(module.check_model)
            and callable(module.check_practice_evidence),
            "only the complete frozen first-party anchor transformer may execute")
    return module


def decode(module: types.ModuleType, raw: bytes, label: str) -> dict[str, object]:
    value = module.StrictJSON(raw).document()
    require(type(value) is dict, "a complete public JSON object is mandatory: " + label)
    return value


def secure_owner_document(row: tuple[object, ...]) -> dict[str, object]:
    role, path, sha, size, inode = row
    return {"role": role, "path": path, "sha256": sha, "bytes": size,
            "device": DEVICE, "inode": inode, "mode": "0600"}


def authenticate_public_context() -> tuple[types.ModuleType, dict[str, bytes],
                                            dict[str, object]]:
    originals: dict[str, bytes] = {}
    identities: list[dict[str, object]] = []
    for row in OWNERS:
        payload, identity = owned(row)
        require(row[0] not in originals, "an independently pinned owner role repeated")
        originals[row[0]] = payload
        identities.append(identity)
    require(len(originals) == len(OWNERS), "the complete public-source census changed")
    transformer = load_anchor_transformer(originals["anchor_source"])
    derived_engine = transformer.transform_engine(originals["original_lib"])
    derived_search = transformer.transform_search(originals["original_search"])
    require(derived_engine == originals["anchor_lib"]
            and len(derived_engine) == ANCHOR_LIB_BYTES
            and digest(derived_engine) == ANCHOR_LIB_SHA
            and derived_search == originals["anchor_search"]
            and len(derived_search) == ANCHOR_SEARCH_BYTES
            and digest(derived_search) == ANCHOR_SEARCH_SHA,
            "the complete independently derived first-party anchor architecture changed")
    model = transformer.check_model()
    require(model == {"differential_checks": 11328,
                      "seed": 0x52454241525F4131,
                      "semantic_pattern_count": 18},
            "the frozen deterministic first-party anchor semantic model changed")
    practice = transformer.check_practice_evidence({
        "rust_practice_correctness": originals["practice_rust"],
        "python_practice_correctness": originals["practice_python"],
        "public_paired_timings": originals["practice_timings"],
        "public_profile_manifest": originals["public_profile_manifest"],
        "rust_manifest": originals["cargo_manifest"],
        "rust_lock": originals["cargo_lock"],
        "owned_simd_search_results": originals["owned_simd_search_results"],
        "owned_simd_search_research": originals["owned_simd_search_research"],
    })
    require(practice == {
        "public_case_count": 416,
        "paired_row_count": 1664,
        "dense_paired_row_count": 416,
        "dense_python_elapsed_ns": 21797729,
        "dense_rust_elapsed_ns": 102371349,
        "worst_alternation_python_elapsed_ns": 254724,
        "worst_alternation_rust_elapsed_ns": 2554459,
        "records_sha256": PUBLIC_RECORDS_SHA,
    }, "all complete historical public cases and observed regressions must remain visible")
    graph = originals["practice_graph"]
    for marker in (
        b'"public_equal_case_geometric_speedup":0.8485646292880136',
        b'"dense_prefix_public_equal_case_geometric_speedup":0.41613883193210616',
        b'"public_aggregate_total_elapsed_speedup":0.5958109767071408',
        b'"public_correctness_case_count":416',
        b'"public_rust_faster_pair_count":723',
        b'"public_rust_slower_pair_count":937',
        b'"public_tied_pair_count":4',
        b'"public_profiler_status":"FAIL; INCOMPLETE STDLIB-ONLY COLLECTION"',
    ):
        require(marker in graph,
                "the complete actual public evidence lost an important measured outcome")
    require(b'"all_slower_paired_observation_count":937'
            in originals["practice_failure"]
            or b'"slower_paired_observation_count":937'
            in originals["practice_failure"],
            "preserve every actual slower paired public observation")

    anchor_receipt = decode(transformer, originals["anchor_application"],
                            "actual applied mandatory-anchor source receipt")
    require(anchor_receipt.get("schema") == transformer.SCHEMA
            and anchor_receipt.get("status") == "APPLIED"
            and anchor_receipt.get("source_sha256") == ANCHOR_OWNERS[0][2]
            and anchor_receipt.get("protocol_sha256") == ANCHOR_OWNERS[1][2]
            and anchor_receipt.get("contract_sha256") == ANCHOR_OWNERS[2][2]
            and anchor_receipt.get("candidate_processes") == 0
            and anchor_receipt.get("clocks_sampled") == 0
            and anchor_receipt.get("native_libraries_loaded") == 0
            and type(anchor_receipt.get("holdout_opened")) is int
            and anchor_receipt.get("holdout_opened") == 0,
            "authenticate the real committed two-owner first-party source application")
    previous_success = decode(transformer, originals["v25_success_receipt"],
                              "actual successful V25 compiler publication")
    previous_root = decode(transformer, originals["v25_root_receipt"],
                           "actual successful V25 private-root provenance")
    require(previous_success.get("status") == "PASS"
            and previous_success.get("build_status") == "PASS"
            and previous_success.get("actual_compiler_process_count") == 28
            and previous_success.get("combined_bridge_sha256") == BRIDGE_SHA
            and previous_success.get("combined_bridge_bytes") == BRIDGE_BYTES
            and previous_success.get("corrected_public_adapter_sha256") == ADAPTER_SHA
            and previous_success.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
            and previous_success.get("latest_v24_candidate_status") == "FAIL"
            and previous_success.get("latest_v24_semantic_mismatch_count") == 1352
            and previous_success.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and previous_success.get("holdout") == "NOT OPENED",
            "preserve the real successful V25 build without inventing candidate success")
    root = previous_root.get("root")
    outputs = previous_root.get("actual_reproduced_native_outputs")
    require(previous_root.get("status") == "PASS"
            and previous_root.get("canonical_build_status") == "PASS"
            and previous_root.get("canonical_build_receipt_sha256") == V25_RECEIPT_SHA
            and previous_root.get("actual_compiler_process_count") == 28
            and previous_root.get("actual_source_phase_count") == 2
            and previous_root.get("bridge_overlay_apply_count") == 2
            and previous_root.get("adapter_overlay_apply_count") == 2
            and previous_root.get("materialized_complete_bridge_sha256") == BRIDGE_SHA
            and previous_root.get("corrected_public_adapter_sha256") == ADAPTER_SHA
            and type(root) is dict and root.get("device") == 2049
            and root.get("inode") == 11676733 and root.get("mode") == "0700"
            and root.get("phase_count") == 2
            and root.get("path") == "/tmp/rebar-phase2-native-build-v9-rust-gx53scyp"
            and type(outputs) is dict and set(outputs) == {"engine", "bridge"}
            and outputs.get("engine", {}).get("sha256")
            == "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
            and outputs.get("engine", {}).get("size_bytes") == 658344
            and outputs.get("bridge", {}).get("sha256")
            == "adcb000c036e075a52f43926750648a4610e853e628d5433b1fbcc17e99a89e4"
            and outputs.get("bridge", {}).get("size_bytes") == 148720
            and previous_root.get("latest_v24_candidate_status") == "FAIL"
            and previous_root.get("latest_v24_semantic_mismatch_count") == 1352
            and previous_root.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and previous_root.get("holdout") == "NOT OPENED",
            "preserve all actual prior native/root facts solely from public plaintext")
    failure = decode(transformer, originals["v24_failure"],
                     "previous actual full original P0 candidate failure")
    require(failure.get("status") == "PASS" and failure.get("candidate_status") == "FAIL"
            and failure.get("semantic_mismatch_count") == 1352
            and failure.get("verified_passing_case_count") == 15877
            and failure.get("completed_suite_count") == 13,
            "do not misreport the previous genuine full-oracle candidate failure")
    latest_failure = decode(transformer, originals["v25_candidate_failure"],
                            "latest actual V25 complete original P0 candidate failure")
    require(latest_failure.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v25-durable-publication-receipt"
            and latest_failure.get("status") == "PASS"
            and latest_failure.get("publication_status") == "PASS"
            and latest_failure.get("candidate_status") == "FAIL"
            and latest_failure.get("semantic_mismatch_count") == 1352
            and latest_failure.get("verified_passing_case_count") == 15877
            and latest_failure.get("case_execution_denominator") == 31237
            and latest_failure.get("completed_suite_count") == 13
            and latest_failure.get("suite_count") == 13
            and latest_failure.get("attempted_suite_count") == 13
            and latest_failure.get("started_suite_count") == 13
            and latest_failure.get("infrastructure_failure_count") == 0
            and latest_failure.get("actual_candidate_workers") == 13
            and latest_failure.get("distinct_worker_process_id_count") == 13
            and latest_failure.get("all_four_original_targets_restored") is True
            and latest_failure.get("combined_bridge_source_sha256") == BRIDGE_SHA
            and latest_failure.get("corrected_public_adapter_sha256") == ADAPTER_SHA
            and latest_failure.get("actual_v25_build_receipt_sha256") == V25_RECEIPT_SHA
            and latest_failure.get("actual_v25_build_contract_sha256") == V25_OWNERS[2][2]
            and latest_failure.get("holdout") == "NOT OPENED"
            and latest_failure.get("clock_samples") == 0
            and latest_failure.get("timing_trials_run") == 0,
            "preserve the fresh complete V25 real candidate FAIL and all 13 actual workers")
    suite_rows = latest_failure.get("suite_integrity")
    require(type(suite_rows) is list and len(suite_rows) == 13
            and sorted(row.get("mismatch_count") for row in suite_rows
                       if type(row) is dict and row.get("mismatch_count", 0) > 0)
            == [240, 1112],
            "preserve all latest actual substitution and shape mismatches without guessing")
    audit = decode(transformer, originals["strict_audit_actual_failure"],
                   "actual strict static first-party audit failure")
    finding = audit.get("findings")
    require(audit.get("status") == "FAIL" and audit.get("finding_count") == 1
            and audit.get("candidate_qualified") is False
            and audit.get("runtime_non_delegation")
            == "NOT ESTABLISHED; CANDIDATES NEVER EXECUTED"
            and audit.get("holdout") == "NOT OPENED"
            and type(finding) is list and len(finding) == 1
            and finding[0].get("code") == "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE"
            and finding[0].get("family") == FAMILY
            and finding[0].get("path") == "candidates/rust/py_bridge.c"
            and finding[0].get("line") == 4403
            and finding[0].get("reachability")
            == "PRIVATE_BRIDGE_BIND_GETTER; PUBLIC_MATCHING_DELEGATION_NOT_PROVEN"
            and finding[0].get("severity") == "FAIL"
            and b'PyImport_ImportModule("inspect")' in originals["safe_clamp_bridge"],
            "retain the actual unremediated private getter and failed strict audit")
    proposal = decode(transformer, originals["proposal_contract"],
                      "complete unopened expanded phase-three proposal metadata")
    require(proposal.get("case_count") == SEALED_PROPOSAL_CASE_COUNT
            and proposal.get("proposal_status") == "PRE-PHASE-3 PROPOSAL"
            and proposal.get("case_status") == "NOT GENERATED; NOT OPENED"
            and proposal.get("final_protocol_status") == "NOT FROZEN"
            and proposal.get("phase3_gate_status")
            == "BLOCKED UNTIL THREE DISTINCT COMPLETE-P0 NO-DELEGATION PASSES"
            and proposal.get("qualified_independent_family_count") == 0
            and proposal.get("minimum_qualified_independent_family_count") == 3
            and proposal.get("generator_status") == "NOT FROZEN"
            and proposal.get("secret_status") == "NOT GENERATED"
            and proposal.get("timing_status") == "NOT RUN; NOT MEASURED",
            "preserve the complete unopened, unfrozen expanded holdout proposal")
    return transformer, originals, {
        "owners": identities,
        "practice": practice,
        "model": model,
        "anchor_application": anchor_receipt,
        "previous_v25_success": previous_success,
        "previous_v25_root": previous_root,
        "previous_v24_failure": failure,
        "latest_v25_failure": latest_failure,
        "strict_audit": audit,
        "expanded_proposal": proposal,
    }


def frozen_contract(source: dict[str, object], protocol: dict[str, object],
                    context: dict[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "status": "PASS",
        "phase": 2,
        "family": FAMILY,
        "goal_sha256": GOAL_SHA,
        "pinned_python": PYTHON,
        "pinned_python_sha256": PYTHON_SHA,
        "source": source,
        "protocol": protocol,
        "first_party_owner_count": len(OWNERS),
        "first_party_owners": context["owners"],
        "first_party_package_count": 1,
        "external_cargo_dependency_count": 0,
        "canonical_original_rust_source_owner_count": 9,
        "previous_actual_v25_native_source": {
            "source_sha256": V25_OWNERS[0][2],
            "protocol_sha256": V25_OWNERS[1][2],
            "contract_sha256": V25_OWNERS[2][2],
            "actual_successful_publication_receipt_sha256": V25_RECEIPT_SHA,
            "actual_retained_private_root_receipt_sha256": V25_ROOT_SHA,
            "actual_compiler_process_count": 28,
            "actual_independent_phase_count": 2,
            "actual_engine_sha256":
                "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f",
            "actual_engine_bytes": 658344,
            "actual_safe_bridge_elf_sha256":
                "adcb000c036e075a52f43926750648a4610e853e628d5433b1fbcc17e99a89e4",
            "actual_safe_bridge_elf_bytes": 148720,
            "actual_private_root_path":
                "/tmp/rebar-phase2-native-build-v9-rust-gx53scyp",
            "actual_private_root_device": 2049,
            "actual_private_root_inode": 11676733,
            "actual_private_root_mode": "0700",
            "private_root_metadata_source": "PUBLIC PLAINTEXT RECEIPT ONLY",
            "actual_private_root_opened": False,
            "actual_candidate_matching": "NOT RUN",
            "actual_candidate_correctness": NOT_MEASURED,
        },
        "committed_first_party_anchor_architecture": {
            "source_sha256": ANCHOR_OWNERS[0][2],
            "protocol_sha256": ANCHOR_OWNERS[1][2],
            "contract_sha256": ANCHOR_OWNERS[2][2],
            "actual_application_receipt_sha256": ANCHOR_OWNERS[3][2],
            "architecture": "FIRST-PARTY REQUIRED-BYTE OFFSET AND ALTERNATIVE SEARCH",
            "compiler_parser_optimization_claimed": False,
            "external_regex_engine_count": 0,
            "external_package_count": 0,
            "engine_source_sha256": ANCHOR_LIB_SHA,
            "engine_source_bytes": ANCHOR_LIB_BYTES,
            "search_source_sha256": ANCHOR_SEARCH_SHA,
            "search_source_bytes": ANCHOR_SEARCH_BYTES,
            "independently_rederived_source_owner_count": 2,
            "source_semantic_model": context["model"],
        },
        "committed_first_party_safe_bridge": {
            "source_sha256": CLAMP_OWNERS[0][2],
            "protocol_sha256": CLAMP_OWNERS[1][2],
            "contract_sha256": CLAMP_OWNERS[2][2],
            "actual_application_receipt_sha256": CLAMP_OWNERS[3][2],
            "materialized_bridge_source_sha256": BRIDGE_SHA,
            "materialized_bridge_source_bytes": BRIDGE_BYTES,
            "corrected_first_party_adapter_sha256": ADAPTER_SHA,
            "corrected_first_party_adapter_bytes": ADAPTER_BYTES,
            "private_inspect_getter_present": True,
        },
        "historical_v24_original_p0_failure": {
            "actual_receipt_sha256": V24_FAILURE_SHA,
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 1352,
            "verified_passing_case_count": 15877,
            "completed_suite_count": 13,
        },
        "latest_complete_original_p0_failure": {
            "actual_receipt_sha256": V25_CANDIDATE_FAILURE_SHA,
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_version": 25,
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 1352,
            "substitution_mismatch_count": 240,
            "shape_mismatch_count": 1112,
            "verified_passing_case_count": 15877,
            "case_execution_denominator": 31237,
            "completed_suite_count": 13,
            "actual_candidate_worker_count": 13,
            "infrastructure_failure_count": 0,
            "all_original_runtime_targets_restored": True,
        },
        "actual_strict_non_delegation_audit_v4": {
            "source_sha256": AUDIT_OWNERS[0][2],
            "protocol_sha256": AUDIT_OWNERS[1][2],
            "contract_sha256": AUDIT_OWNERS[2][2],
            "actual_failure_receipt_sha256": STRICT_AUDIT_FAILURE_SHA,
            "status": "FAIL; PRIVATE GETTER PRESENT",
            "finding_count": 1,
            "finding_code": "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE",
            "finding_reachability":
                "PRIVATE_BRIDGE_BIND_GETTER; PUBLIC_MATCHING_DELEGATION_NOT_PROVEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_qualified": False,
        },
        "distinct_authenticated_runtime_guard_v4": {
            "source_sha256": GUARD_OWNERS[0][2],
            "protocol_sha256": GUARD_OWNERS[1][2],
            "contract_sha256": GUARD_OWNERS[2][2],
            "same_as_strict_static_audit": False,
        },
        "complete_actual_public_development_practice": {
            **context["practice"],
            "matrix_sha256": PUBLIC_MATRIX_SHA,
            "overall_equal_case_geometric_speedup": "0.8485646292880136",
            "dense_equal_case_geometric_speedup": "0.41613883193210616",
            "aggregate_elapsed_speedup": "0.5958109767071408",
            "rust_faster_paired_observation_count": 723,
            "rust_slower_paired_observation_count": 937,
            "tied_paired_observation_count": 4,
            "graph_input_sha256": PUBLIC_OWNERS[2][2],
            "full_slower_observation_failure_sha256": PUBLIC_OWNERS[3][2],
            "profiler_status": "FAIL; INCOMPLETE STDLIB-ONLY COLLECTION",
            "rust_native_cpu_profile": NOT_MEASURED,
            "holdout_result": NOT_MEASURED,
        },
        "expanded_sealed_holdout": {
            "proposal_source_sha256": HOLDOUT_OWNERS[0][2],
            "proposal_protocol_sha256": HOLDOUT_OWNERS[1][2],
            "proposal_contract_sha256": SEALED_PROPOSAL_SHA,
            "proposed_case_count": SEALED_PROPOSAL_CASE_COUNT,
            "proposal_status": "PRE-PHASE-3 PROPOSAL",
            "final_protocol": "NOT FROZEN",
            "cases": "NOT GENERATED; NOT OPENED",
            "qualified_independent_family_count": 0,
            "minimum_qualified_independent_family_count": 3,
            "opened": False,
            "results": NOT_MEASURED,
        },
        "frozen_actual_first_party_offline_twin_build": {
            "label": LABEL,
            "phase_names": list(PHASES),
            "compiler_process_roles_per_phase": list(PROCESS_NAMES),
            "required_compiler_process_count": 28,
            "canonical_source_owners_per_phase": 9,
            "unchanged_original_source_owners_per_phase": 5,
            "first_party_source_overlays_per_phase": 4,
            "mandatory_anchor_engine_source_overlays": 2,
            "mandatory_anchor_search_source_overlays": 2,
            "safe_clamp_bridge_source_overlays": 2,
            "corrected_adapter_source_overlays": 2,
            "external_cargo_dependency_count": 0,
            "offline_cargo_only": True,
            "independent_complete_native_elf_comparisons": 2,
            "native_libraries_loaded": 0,
            "candidate_processes_started": 0,
            "candidate_correctness": NOT_MEASURED,
            "candidate_performance": NOT_MEASURED,
            "candidate_qualified": False,
            "private_build_root_retained": True,
        },
        "source_only_effects": {
            "candidate_processes_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "private_roots_opened": 0,
            "archives_opened": 0,
            "holdout_files_opened": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_mutations": 0,
            "expanded_holdout_proposal_case_count": SEALED_PROPOSAL_CASE_COUNT,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "holdout": "NOT OPENED",
            "candidate_correctness": NOT_MEASURED,
            "candidate_performance": NOT_MEASURED,
            "memory": NOT_MEASURED,
            "confidence_intervals": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "winner_selected": False,
        },
    }


def source_only(mode: str, source_sha: str, protocol_sha: str,
                contract_sha: str | None = None) -> dict[str, object]:
    install_wall()
    source_raw, source_info = dynamic(SOURCE, source_sha)
    protocol_raw, protocol_info = dynamic(PROTOCOL, protocol_sha)
    require(source_raw.startswith(b"#!/usr/bin/env python3\n")
            and b"SOURCE-ONLY WALL" in protocol_raw,
            "independently caller-pin the complete source controller and plain protocol")
    transformer, _, context = authenticate_public_context()
    expected = frozen_contract(source_info, protocol_info, context)
    if mode == "--render-contract":
        return expected
    require(type(contract_sha) is str,
            "caller-pin the entire committed source contract for source verification")
    contract_raw, contract_info = dynamic(CONTRACT, contract_sha)
    existing = decode(transformer, contract_raw, "complete independently frozen V26 contract")
    require(existing == expected
            and (transformer.canonical(existing) + "\n").encode("ascii") == contract_raw,
            "the complete pushed V26 source freeze differs from its reproducible contract")
    outcome = {
        "schema": SCHEMA + "-verified-source-context",
        "version": VERSION,
        "status": "PASS",
        "mode": mode,
        "family": FAMILY,
        "source": source_info,
        "protocol": protocol_info,
        "contract": contract_info,
        "first_party_owner_count": len(OWNERS),
        "first_party_package_count": 1,
        "external_cargo_dependency_count": 0,
        "canonical_original_source_owner_count": 9,
        "committed_first_party_anchor_source_owner_count": 2,
        "actual_previous_v25_build_status": "PASS",
        "actual_previous_v25_root_receipt_sha256": V25_ROOT_SHA,
        "actual_previous_v24_candidate_status": "FAIL",
        "actual_previous_v24_semantic_mismatch_count": 1352,
        "actual_latest_v25_candidate_status": "FAIL",
        "actual_latest_v25_candidate_failure_receipt_sha256": V25_CANDIDATE_FAILURE_SHA,
        "actual_latest_v25_semantic_mismatch_count": 1352,
        "actual_latest_v25_verified_passing_case_count": 15877,
        "actual_latest_v25_completed_suite_count": 13,
        "actual_strict_non_delegation_audit_status": "FAIL; PRIVATE GETTER PRESENT",
        "actual_strict_non_delegation_finding_count": 1,
        "public_correctness_case_count": 416,
        "public_paired_observation_count": 1664,
        "public_equal_case_geometric_speedup": "0.8485646292880136",
        "public_dense_case_geometric_speedup": "0.41613883193210616",
        "expanded_holdout_proposal_case_count": SEALED_PROPOSAL_CASE_COUNT,
        "qualified_independent_candidate_family_count": 0,
        "compiler_processes_started": 0,
        "candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "private_roots_opened": 0,
        "archives_opened": 0,
        "holdout_files_opened": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_mutations": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "candidate_correctness": NOT_MEASURED,
        "candidate_performance": NOT_MEASURED,
        "memory": NOT_MEASURED,
        "confidence_intervals": NOT_MEASURED,
        "undefined_behavior": NOT_MEASURED,
        "winner_selected": False,
    }
    if mode == "--self-test":
        controls = (
            ("clock", lambda: time.clock_gettime(time.CLOCK_MONOTONIC)),
            ("clock", lambda: time.clock_gettime_ns(time.CLOCK_MONOTONIC)),
            ("clock", lambda: os.times()),
            ("foreign_read", lambda: os.read(0, 1)),
            ("foreign_read", lambda: sys.audit(
                "open", ROOT + "/" + SOURCE, "r", os.O_RDONLY)),
            ("process", lambda: sys.audit("subprocess.Popen")),
            ("process", lambda: sys.audit("_interpreters.create")),
            ("candidate", lambda: sys.audit("compile", b"hidden", "<unapproved>")),
            ("candidate", lambda: sys.audit("exec", object())),
            ("native", lambda: sys.audit("open", "/outside/native.so", "r", 0)),
            ("native", lambda: sys.audit("marshal.loads", b"hidden")),
            ("candidate", lambda: sys.audit(
                "open", ROOT + "/candidates/unapproved_candidate.py", "r", 0)),
            ("private_root", lambda: sys.audit(
                "open", "/tmp/rebar-phase2-native-build-v9-rust-probe", "r", 0)),
            ("archive_holdout", lambda: sys.audit(
                "open", ROOT + "/oracle/phase3/unopened-holdout.gz", "r", 0)),
            ("write", lambda: sys.audit(
                "open", ROOT + "/" + SOURCE, "w", os.O_WRONLY)),
            ("network", lambda: sys.audit("socket.connect")),
        )
        rejected = 0
        for kind, action in controls:
            before = BLOCKED[kind]
            try:
                action()
            except BuildFreezeError:
                require(BLOCKED[kind] == before + 1,
                        "a hostile sterile gate did not reject its exact effect")
                rejected += 1
            else:
                raise BuildFreezeError("a hostile sterile source-only control was accepted")
        require(rejected == len(controls) and len(SOURCE_DESCRIPTORS) == 0,
                "complete every deny-default sterile control without opening or mutating")
        outcome["hostile_source_only_controls_rejected"] = rejected
        outcome["blocked_source_only_effects"] = dict(BLOCKED)
    return outcome


def checked_label(value: object) -> str:
    require(type(value) is str and value == LABEL and len(value) == 48
            and all(character.isascii()
                    and (character.isalnum() or character in "-_")
                    for character in value),
            "caller-pin the sole authorized complete V26 first-party build label")
    return value


def evidence_names(label: str, failed: bool) -> tuple[str, str]:
    require(type(failed) is bool, "preserve real actual build failures independently")
    stem = "native-source-build-v26-rust-" + checked_label(label)
    if failed:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def root_receipt_name(label: str) -> str:
    return "native-source-build-v26-rust-" + checked_label(label) + "-root-provenance-receipt.json"


def parse_actual(arguments: list[str]) -> dict[str, object]:
    require(type(arguments) is list and arguments and arguments[0] == "--build",
            "select one actual explicitly root-authorized first-party native source build")
    mapping = {
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
        "--label": "label",
        "--anchor-source-sha256": "anchor_source_sha256",
        "--anchor-protocol-sha256": "anchor_protocol_sha256",
        "--anchor-contract-sha256": "anchor_contract_sha256",
        "--anchor-application-sha256": "anchor_application_sha256",
        "--anchor-lib-sha256": "anchor_lib_sha256",
        "--anchor-lib-bytes": "anchor_lib_bytes",
        "--anchor-search-sha256": "anchor_search_sha256",
        "--anchor-search-bytes": "anchor_search_bytes",
        "--combined-bridge-sha256": "combined_bridge_sha256",
        "--combined-bridge-bytes": "combined_bridge_bytes",
        "--corrected-adapter-sha256": "corrected_adapter_sha256",
        "--corrected-adapter-bytes": "corrected_adapter_bytes",
        "--previous-v25-source-sha256": "previous_v25_source_sha256",
        "--previous-v25-protocol-sha256": "previous_v25_protocol_sha256",
        "--previous-v25-contract-sha256": "previous_v25_contract_sha256",
        "--previous-v25-receipt-sha256": "previous_v25_receipt_sha256",
        "--previous-v25-root-receipt-sha256": "previous_v25_root_receipt_sha256",
        "--previous-v25-candidate-failure-receipt-sha256":
            "previous_v25_candidate_failure_receipt_sha256",
        "--previous-v24-failure-receipt-sha256": "previous_v24_failure_receipt_sha256",
        "--strict-audit-v4-source-sha256": "strict_audit_v4_source_sha256",
        "--strict-audit-v4-protocol-sha256": "strict_audit_v4_protocol_sha256",
        "--strict-audit-v4-contract-sha256": "strict_audit_v4_contract_sha256",
        "--strict-audit-v4-failure-sha256": "strict_audit_v4_failure_sha256",
        "--runtime-guard-v4-source-sha256": "runtime_guard_v4_source_sha256",
        "--runtime-guard-v4-protocol-sha256": "runtime_guard_v4_protocol_sha256",
        "--runtime-guard-v4-contract-sha256": "runtime_guard_v4_contract_sha256",
        "--phase1-v4-source-sha256": "phase1_v4_source_sha256",
        "--phase1-v4-protocol-sha256": "phase1_v4_protocol_sha256",
        "--phase1-v4-contract-sha256": "phase1_v4_contract_sha256",
        "--expanded-proposal-sha256": "expanded_proposal_sha256",
    }
    result: dict[str, object] = {"mode": "--build", "owned_source_sha256": [],
                                 "root_authorized": False,
                                 "frozen_committed_pushed": False}
    position = 1
    while position < len(arguments):
        flag = arguments[position]
        if flag in ("--root-authorized", "--frozen-committed-pushed"):
            key = flag[2:].replace("-", "_")
            require(result[key] is False, "reject duplicate privileged actual-build authority")
            result[key] = True
            position += 1
            continue
        require(position + 1 < len(arguments), "every genuine actual-build pin needs one value")
        value = arguments[position + 1]
        require(type(flag) is str and type(value) is str,
                "reject untrusted or computed actual first-party build authority")
        if flag == "--owned-source-sha256":
            result["owned_source_sha256"].append(value)
            position += 2
            continue
        require(flag in mapping and mapping[flag] not in result,
                "reject an unknown, repeated, or aliased actual V26 build argument")
        key = mapping[flag]
        if key.endswith("_bytes"):
            require(value.isascii() and value.isdecimal(),
                    "independently caller-pin each exact first-party overlay byte count")
            result[key] = int(value)
        elif key == "label":
            result[key] = checked_label(value)
        else:
            result[key] = hash_pin(value, key)
        position += 2
    require(set(result) == set(mapping.values())
            | {"mode", "owned_source_sha256", "root_authorized", "frozen_committed_pushed"},
            "independently caller-pin every first-party V26 actual-build authority")
    expected = {
        "anchor_source_sha256": ANCHOR_OWNERS[0][2],
        "anchor_protocol_sha256": ANCHOR_OWNERS[1][2],
        "anchor_contract_sha256": ANCHOR_OWNERS[2][2],
        "anchor_application_sha256": ANCHOR_OWNERS[3][2],
        "anchor_lib_sha256": ANCHOR_LIB_SHA,
        "anchor_lib_bytes": ANCHOR_LIB_BYTES,
        "anchor_search_sha256": ANCHOR_SEARCH_SHA,
        "anchor_search_bytes": ANCHOR_SEARCH_BYTES,
        "combined_bridge_sha256": BRIDGE_SHA,
        "combined_bridge_bytes": BRIDGE_BYTES,
        "corrected_adapter_sha256": ADAPTER_SHA,
        "corrected_adapter_bytes": ADAPTER_BYTES,
        "previous_v25_source_sha256": V25_OWNERS[0][2],
        "previous_v25_protocol_sha256": V25_OWNERS[1][2],
        "previous_v25_contract_sha256": V25_OWNERS[2][2],
        "previous_v25_receipt_sha256": V25_RECEIPT_SHA,
        "previous_v25_root_receipt_sha256": V25_ROOT_SHA,
        "previous_v25_candidate_failure_receipt_sha256": V25_CANDIDATE_FAILURE_SHA,
        "previous_v24_failure_receipt_sha256": V24_FAILURE_SHA,
        "strict_audit_v4_source_sha256": AUDIT_OWNERS[0][2],
        "strict_audit_v4_protocol_sha256": AUDIT_OWNERS[1][2],
        "strict_audit_v4_contract_sha256": AUDIT_OWNERS[2][2],
        "strict_audit_v4_failure_sha256": STRICT_AUDIT_FAILURE_SHA,
        "runtime_guard_v4_source_sha256": GUARD_OWNERS[0][2],
        "runtime_guard_v4_protocol_sha256": GUARD_OWNERS[1][2],
        "runtime_guard_v4_contract_sha256": GUARD_OWNERS[2][2],
        "phase1_v4_source_sha256": PHASE_ONE_OWNERS[0][2],
        "phase1_v4_protocol_sha256": PHASE_ONE_OWNERS[1][2],
        "phase1_v4_contract_sha256": PHASE_ONE_OWNERS[2][2],
        "expanded_proposal_sha256": SEALED_PROPOSAL_SHA,
        "label": LABEL,
        "root_authorized": True,
        "frozen_committed_pushed": True,
    }
    for name, value in expected.items():
        require(result.get(name) == value,
                "reject substituted or unpushed actual V26 authority: " + name)
    expected_originals = {row[1] + "=" + row[2] for row in CANONICAL_OWNERS}
    pins = result["owned_source_sha256"]
    require(type(pins) is list and len(pins) == 9
            and len(set(pins)) == 9 and set(pins) == expected_originals,
            "independently caller-pin every one of the nine original Rust source owners")
    return result


def copy_four_overlays(module: types.ModuleType, workdir: str, family: str,
                       phase: str, originals: dict[str, bytes]) -> dict[str, object]:
    require(module._ACTIVE is not None,
            "require the actual pinned, root-authorized V26 compiler kernel")
    state = module._ACTIVE
    kernel = state["kernel"]
    low_level = state["v9"]
    module.checked_workdir(workdir)
    expected = {item.path for item in module.RUST_OWNERS}
    require(family == FAMILY and phase in PHASES and type(originals) is dict
            and set(originals) == expected
            and (workdir, phase) not in module._APPLIED_PHASES,
            "require nine genuine canonical sources in one new independent V26 phase")
    paths = low_level.phase_paths(workdir, family, phase)
    for peer in PHASES:
        locations = low_level.phase_paths(workdir, family, peer)
        for folder in (locations["base"], locations["source"],
                       locations["source"] / "candidates",
                       locations["source"] / "candidates/rust"):
            observed = os.lstat(folder)
            require(stat.S_ISDIR(observed.st_mode)
                    and stat.S_IMODE(observed.st_mode) == 0o700
                    and observed.st_uid == os.geteuid(),
                    "both independent V26 private phases must remain owner-only")
    for item in module.RUST_OWNERS:
        value = originals.get(item.path)
        require(type(value) is bytes and len(value) == item.size
                and digest(value) == item.sha256,
                "authenticate each complete untouched canonical Rust source: " + item.path)
    overlay_paths = {
        "candidates/rust/src/lib.rs", "candidates/rust/src/search.rs",
        module.BRIDGE_PATH, module.PUBLIC_PATH,
    }
    rows: dict[str, object] = {}
    for item in sorted(module.RUST_OWNERS, key=lambda owner: owner.path):
        if item.path in overlay_paths:
            continue
        destination = paths["source"] / item.path
        kernel.mkdir_private(destination.parent)
        recorded = kernel.write_fresh(destination, originals[item.path], synchronize=False)
        recorded["path"] = low_level.sanitized(recorded["path"], workdir, family)
        rows[item.path] = recorded
    require(len(rows) == 5, "preserve all five unchanged canonical first-party Rust owners")

    for path, payload, expected_hash, expected_size, role in (
        ("candidates/rust/src/lib.rs", state["anchor_lib"], ANCHOR_LIB_SHA,
         ANCHOR_LIB_BYTES, "first-party-mandatory-anchor-matching-engine"),
        ("candidates/rust/src/search.rs", state["anchor_search"], ANCHOR_SEARCH_SHA,
         ANCHOR_SEARCH_BYTES, "first-party-mandatory-anchor-search-filter"),
        (module.BRIDGE_PATH, state["combined_bridge"], BRIDGE_SHA,
         BRIDGE_BYTES, "first-party-corrected-capture-clamp-bridge"),
        (module.PUBLIC_PATH, state["corrected_adapter"], ADAPTER_SHA,
         ADAPTER_BYTES, "first-party-corrected-public-adapter"),
    ):
        require(type(payload) is bytes and len(payload) == expected_size
                and digest(payload) == expected_hash,
                "independently authenticate one complete genuine V26 source overlay")
        if path in ("candidates/rust/src/lib.rs", "candidates/rust/src/search.rs"):
            audited = kernel.audit_native_source(payload, family=FAMILY, location=path)
            require(type(audited) is dict
                    and audited.get("external_regex_dependency_count") == 0
                    and audited.get("cross_family_dependency_count") == 0,
                    "reject an external matcher in either optimized first-party Rust source")
        destination = paths["source"] / path
        kernel.mkdir_private(destination.parent)
        published = kernel.write_fresh(destination, payload, synchronize=True)
        observed, checked = kernel.authenticate_file(
            destination, expected=expected_hash, maximum=module.MAX_SOURCE_BYTES,
            exact_size=expected_size, capture=True,
        )
        require(type(checked) is bytes and checked == payload
                and published.get("sha256") == expected_hash
                and published.get("bytes") == expected_size
                and published.get("device") == observed.get("device")
                and published.get("inode") == observed.get("inode")
                and published.get("exclusive_creation") is True
                and published.get("file_fsync_completed") is True
                and stat.S_IMODE(os.lstat(destination).st_mode) == 0o600,
                "exclusively create, synchronize, and reread the private V26 overlay")
        rows[path] = {
            "path": low_level.sanitized(observed["path"], workdir, family),
            "sha256": observed["sha256"],
            "bytes": observed["size_bytes"],
            "device": observed["device"],
            "inode": observed["inode"],
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
            "source_overlay": {
                "status": "PASS", "phase": phase, "role": role,
                "source_apply_count": 1,
                "derived_sha256": expected_hash,
                "derived_source_sha256": expected_hash,
                "derived_bytes": expected_size,
                "derived_source_bytes": expected_size,
                "candidate_original_modified": False,
                "canonical_candidate_modified": False,
            },
        }
    require(set(rows) == expected, "close exactly five untouched and four optimized Rust owners")
    for item in module.RUST_OWNERS:
        module.read_owner(item)
    module._APPLIED_PHASES.add((workdir, phase))
    return rows


def publish_actual_build(module: types.ModuleType, kernel: types.ModuleType,
                         report: dict[str, object]) -> dict[str, object]:
    require(type(report) is dict and report.get("status") in ("PASS", "FAIL")
            and report.get("family") == FAMILY and report.get("label") == LABEL,
            "durably publish only an actually observed authorized V26 build outcome")
    complete = dict(report)
    if "graph_version" in complete:
        complete["historical_frozen_graph_version"] = complete.pop("graph_version")
    if "prepublication_evidence_owner_lower_bound" in complete:
        complete["historical_frozen_evidence_owner_lower_bound"] = complete.pop(
            "prepublication_evidence_owner_lower_bound")
    if "prepublication_history_reference_lower_bound" in complete:
        complete["historical_frozen_history_reference_lower_bound"] = complete.pop(
            "prepublication_history_reference_lower_bound")
    complete.update({
        "anchor_engine_source_sha256": ANCHOR_LIB_SHA,
        "anchor_engine_source_bytes": ANCHOR_LIB_BYTES,
        "anchor_search_source_sha256": ANCHOR_SEARCH_SHA,
        "anchor_search_source_bytes": ANCHOR_SEARCH_BYTES,
        "anchor_source_sha256": ANCHOR_OWNERS[0][2],
        "anchor_protocol_sha256": ANCHOR_OWNERS[1][2],
        "anchor_contract_sha256": ANCHOR_OWNERS[2][2],
        "anchor_actual_application_receipt_sha256": ANCHOR_OWNERS[3][2],
        "previous_actual_v25_build_receipt_sha256": V25_RECEIPT_SHA,
        "previous_actual_v25_root_receipt_sha256": V25_ROOT_SHA,
        "latest_v25_candidate_failure_receipt_sha256": V25_CANDIDATE_FAILURE_SHA,
        "latest_v25_candidate_status": "FAIL",
        "latest_v25_semantic_mismatch_count": 1352,
        "latest_v25_substitution_mismatch_count": 240,
        "latest_v25_shape_mismatch_count": 1112,
        "latest_v25_verified_passing_case_count": 15877,
        "latest_v25_case_execution_denominator": 31237,
        "latest_v25_completed_suite_count": 13,
        "latest_v25_actual_candidate_worker_count": 13,
        "latest_v25_infrastructure_failure_count": 0,
        "latest_v24_candidate_failure_receipt_sha256": V24_FAILURE_SHA,
        "latest_v24_candidate_status": "FAIL",
        "latest_v24_semantic_mismatch_count": 1352,
        "latest_v24_verified_passing_case_count": 15877,
        "strict_non_delegation_audit_v4_failure_receipt_sha256": STRICT_AUDIT_FAILURE_SHA,
        "strict_non_delegation_audit_v4_status": "FAIL; PRIVATE GETTER PRESENT",
        "strict_non_delegation_audit_v4_finding_count": 1,
        "strict_non_delegation_audit_v4_finding_code":
            "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE",
        "strict_non_delegation_audit_v4_finding_reachability":
            "PRIVATE_BRIDGE_BIND_GETTER; PUBLIC_MATCHING_DELEGATION_NOT_PROVEN",
        "complete_public_practice_case_count": 416,
        "complete_public_paired_observation_count": 1664,
        "public_equal_case_geometric_speedup": "0.8485646292880136",
        "public_dense_case_geometric_speedup": "0.41613883193210616",
        "public_rust_slower_paired_observation_count": 937,
        "expanded_holdout_proposal_case_count": SEALED_PROPOSAL_CASE_COUNT,
        "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_matching": "NOT RUN",
        "candidate_correctness": NOT_MEASURED,
        "candidate_qualified": False,
        "candidate_performance": NOT_MEASURED,
        "candidate_workers_started": 0,
        "native_libraries_loaded": 0,
        "holdout": "NOT OPENED",
        "winner_selected": False,
    })
    archive_name, receipt_name = evidence_names(LABEL, report["status"] == "FAIL")
    directory = module.ROOT / EVIDENCE_DIRECTORY
    plain = module.canonical(complete)
    require(0 < len(plain) <= module.MAX_REPORT_BYTES,
            "bound the complete durable actually observed V26 compiler report")
    archive = module.gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(archive) <= module.MAX_REPORT_BYTES,
            "bound the deterministic complete V26 actual compiler evidence")
    archive_record = kernel.write_fresh(directory / archive_name, archive, synchronize=True)
    archive_sync = kernel.fsync_directory(directory)
    require(archive_record.get("sha256") == digest(archive)
            and archive_record.get("bytes") == len(archive)
            and archive_record.get("exclusive_creation") is True
            and archive_record.get("file_fsync_completed") is True
            and archive_sync.get("completed") is True,
            "exclusively publish and synchronize genuine actual V26 PASS or FAIL evidence")
    operations = complete.get("compiler_processes")
    require(type(operations) is list, "preserve every genuinely attempted compiler role")
    completed_phase_count = complete.get("phase_count")
    expected_overlay_count = complete.get("combined_bridge_overlay_apply_count", 0)
    require(type(expected_overlay_count) is int and 0 <= expected_overlay_count <= 2
            and complete.get("corrected_public_adapter_overlay_apply_count", 0)
            == expected_overlay_count,
            "preserve every actually applied private overlay even when compilation fails")
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "version": VERSION,
        "status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY; NEVER CANDIDATE SUCCESS",
        "build_status": complete["status"],
        "family": FAMILY,
        "label": LABEL,
        "source_sha256": complete["source_sha256"],
        "protocol_sha256": complete["protocol_sha256"],
        "contract_sha256": complete["contract_sha256"],
        "archive_relative": EVIDENCE_DIRECTORY + "/" + archive_name,
        "archive_sha256": archive_record["sha256"],
        "archive_bytes": archive_record["bytes"],
        "archive_publication": archive_record,
        "archive_directory_fsync": archive_sync,
        "uncompressed_sha256": digest(plain),
        "uncompressed_bytes": len(plain),
        "previous_actual_v25_source_sha256": V25_OWNERS[0][2],
        "previous_actual_v25_protocol_sha256": V25_OWNERS[1][2],
        "previous_actual_v25_contract_sha256": V25_OWNERS[2][2],
        "previous_actual_v25_success_receipt_sha256": V25_RECEIPT_SHA,
        "previous_actual_v25_root_receipt_sha256": V25_ROOT_SHA,
        "latest_v25_candidate_failure_receipt_sha256": V25_CANDIDATE_FAILURE_SHA,
        "latest_v25_candidate_status": "FAIL",
        "latest_v25_semantic_mismatch_count": 1352,
        "latest_v25_substitution_mismatch_count": 240,
        "latest_v25_shape_mismatch_count": 1112,
        "latest_v25_verified_passing_case_count": 15877,
        "latest_v25_case_execution_denominator": 31237,
        "latest_v25_completed_suite_count": 13,
        "latest_v25_actual_candidate_worker_count": 13,
        "latest_v25_infrastructure_failure_count": 0,
        "latest_v24_candidate_failure_receipt_sha256": V24_FAILURE_SHA,
        "latest_v24_candidate_status": "FAIL",
        "latest_v24_semantic_mismatch_count": 1352,
        "latest_v24_verified_passing_case_count": 15877,
        "strict_audit_v4_failure_receipt_sha256": STRICT_AUDIT_FAILURE_SHA,
        "strict_audit_v4_status": "FAIL; PRIVATE GETTER PRESENT",
        "strict_audit_v4_finding_count": 1,
        "strict_audit_v4_finding_code": "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "mandatory_anchor_source_sha256": ANCHOR_OWNERS[0][2],
        "mandatory_anchor_protocol_sha256": ANCHOR_OWNERS[1][2],
        "mandatory_anchor_contract_sha256": ANCHOR_OWNERS[2][2],
        "mandatory_anchor_application_receipt_sha256": ANCHOR_OWNERS[3][2],
        "anchor_engine_source_sha256": ANCHOR_LIB_SHA,
        "anchor_engine_source_bytes": ANCHOR_LIB_BYTES,
        "anchor_search_source_sha256": ANCHOR_SEARCH_SHA,
        "anchor_search_source_bytes": ANCHOR_SEARCH_BYTES,
        "safe_clamp_bridge_source_sha256": BRIDGE_SHA,
        "safe_clamp_bridge_source_bytes": BRIDGE_BYTES,
        "corrected_public_adapter_sha256": ADAPTER_SHA,
        "corrected_public_adapter_bytes": ADAPTER_BYTES,
        "anchor_engine_overlay_apply_count": expected_overlay_count,
        "anchor_search_overlay_apply_count": expected_overlay_count,
        "safe_clamp_bridge_overlay_apply_count":
            complete.get("combined_bridge_overlay_apply_count", 0),
        "corrected_adapter_overlay_apply_count":
            complete.get("corrected_public_adapter_overlay_apply_count", 0),
        "expected_actual_compiler_process_count": 28,
        "actual_compiler_process_count": len(operations),
        "actual_completed_phase_count": completed_phase_count,
        "canonical_original_source_owner_count": 9,
        "unchanged_canonical_source_owners_per_phase": 5,
        "external_cargo_dependency_count": 0,
        "complete_public_practice_case_count": 416,
        "complete_public_paired_observation_count": 1664,
        "public_equal_case_geometric_speedup": "0.8485646292880136",
        "public_dense_case_geometric_speedup": "0.41613883193210616",
        "public_rust_slower_paired_observation_count": 937,
        "expanded_holdout_proposal_case_count": SEALED_PROPOSAL_CASE_COUNT,
        "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "candidate_correctness": NOT_MEASURED,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": NOT_MEASURED,
        "memory": NOT_MEASURED,
        "confidence_intervals": NOT_MEASURED,
        "undefined_behavior": NOT_MEASURED,
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }

    payload = module.canonical(receipt)
    require(0 < len(payload) <= module.MAX_SOURCE_BYTES,
            "bound independently durable truthful V26 native source publication")
    recorded = kernel.write_fresh(directory / receipt_name, payload, synchronize=True)
    receipt_sync = kernel.fsync_directory(directory)
    require(recorded.get("sha256") == digest(payload)
            and recorded.get("bytes") == len(payload)
            and recorded.get("exclusive_creation") is True
            and recorded.get("file_fsync_completed") is True
            and receipt_sync.get("completed") is True,
            "durably publish actual V26 compiler outcome without overwriting history")
    return {
        "schema": SCHEMA + "-published-build",
        "status": complete["status"],
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY; NEVER CANDIDATE SUCCESS",
        "build_status": complete["status"],
        "family": FAMILY,
        "label": LABEL,
        "archive_relative": EVIDENCE_DIRECTORY + "/" + archive_name,
        "archive_sha256": archive_record["sha256"],
        "receipt_relative": EVIDENCE_DIRECTORY + "/" + receipt_name,
        "receipt_sha256": recorded["sha256"],
        "receipt_bytes": recorded["bytes"],
        "receipt_directory_fsync": receipt_sync,
        "failure_preserved": complete["status"] == "FAIL",
        "actual_compiler_process_count": len(operations),
        "actual_completed_phase_count": completed_phase_count,
        "anchor_engine_source_sha256": ANCHOR_LIB_SHA,
        "anchor_search_source_sha256": ANCHOR_SEARCH_SHA,
        "safe_clamp_bridge_source_sha256": BRIDGE_SHA,
        "corrected_public_adapter_sha256": ADAPTER_SHA,
        "strict_non_delegation_audit_status": "FAIL; PRIVATE GETTER PRESENT",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_correctness": NOT_MEASURED,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "candidate_performance": NOT_MEASURED,
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def publish_actual_root(module: types.ModuleType, state: dict[str, object],
                        result: dict[str, object], options: dict[str, object],
                        original_before: dict[str, object],
                        original_after: dict[str, object],
                        canonical_before: dict[str, object],
                        canonical_after: dict[str, object]) -> dict[str, object]:
    require(result.get("status") == "PASS" and result.get("build_status") == "PASS"
            and result.get("label") == LABEL and original_before == original_after
            and len(original_after) == 4 and type(ROOT_CAPTURE) is dict
            and canonical_before == canonical_after
            and len(canonical_after) == 9,
            "require complete actual compiler success and every original source identity")
    capture = ROOT_CAPTURE
    require(capture.get("unique_process_count") == 28
            and capture.get("phase_count") == 2
            and type(capture.get("compiler_process_ids")) is list
            and len(capture["compiler_process_ids"]) == 28
            and type(capture.get("private_source_owners")) is list
            and len(capture["private_source_owners"]) == 2
            and type(capture.get("native_outputs")) is dict
            and set(capture["native_outputs"]) == {"engine", "bridge"},
            "publish root provenance only after a genuine complete 28-process twin build")
    runtime = state.get("runtime_state")
    require(type(runtime) is dict and runtime.get("kernel") is not None,
            "retain the genuinely authenticated first-party native publication kernel")
    kernel = runtime["kernel"]
    relative = result.get("receipt_relative")
    require(relative == EVIDENCE_DIRECTORY + "/" + evidence_names(LABEL, False)[1],
            "bind the exact actually published independent V26 native build receipt")
    observed = os.stat(ROOT + "/" + str(relative), follow_symlinks=False)
    require(stat.S_ISREG(observed.st_mode)
            and stat.S_IMODE(observed.st_mode) == 0o600
            and observed.st_dev == DEVICE and observed.st_uid == os.geteuid()
            and observed.st_nlink == 1 and observed.st_size == result.get("receipt_bytes"),
            "require the exclusively created synchronized actual V26 success receipt")
    receipt_raw, _receipt_identity = dynamic(str(relative), str(result["receipt_sha256"]))
    transformer = sys.modules.get("_rebar_v26_read_only_frozen_anchor_source")
    require(type(transformer) is types.ModuleType,
            "retain only the already authenticated first-party public strict JSON reader")
    receipt = decode(transformer, receipt_raw, "fresh durable actual V26 success publication")
    for key, value in (
        ("schema", SCHEMA + "-durable-publication-receipt"),
        ("status", "PASS"), ("build_status", "PASS"),
        ("family", FAMILY), ("label", LABEL),
        ("source_sha256", options["source_sha256"]),
        ("protocol_sha256", options["protocol_sha256"]),
        ("contract_sha256", options["contract_sha256"]),
        ("previous_actual_v25_success_receipt_sha256", V25_RECEIPT_SHA),
        ("previous_actual_v25_root_receipt_sha256", V25_ROOT_SHA),
        ("latest_v25_candidate_failure_receipt_sha256", V25_CANDIDATE_FAILURE_SHA),
        ("latest_v25_candidate_status", "FAIL"),
        ("latest_v25_semantic_mismatch_count", 1352),
        ("latest_v25_substitution_mismatch_count", 240),
        ("latest_v25_shape_mismatch_count", 1112),
        ("latest_v25_verified_passing_case_count", 15877),
        ("latest_v25_case_execution_denominator", 31237),
        ("latest_v25_completed_suite_count", 13),
        ("latest_v25_actual_candidate_worker_count", 13),
        ("latest_v25_infrastructure_failure_count", 0),
        ("latest_v24_candidate_failure_receipt_sha256", V24_FAILURE_SHA),
        ("latest_v24_candidate_status", "FAIL"),
        ("latest_v24_semantic_mismatch_count", 1352),
        ("strict_audit_v4_failure_receipt_sha256", STRICT_AUDIT_FAILURE_SHA),
        ("strict_audit_v4_status", "FAIL; PRIVATE GETTER PRESENT"),
        ("strict_audit_v4_finding_count", 1),
        ("runtime_non_delegation", "NOT ESTABLISHED"),
        ("anchor_engine_source_sha256", ANCHOR_LIB_SHA),
        ("anchor_search_source_sha256", ANCHOR_SEARCH_SHA),
        ("safe_clamp_bridge_source_sha256", BRIDGE_SHA),
        ("corrected_public_adapter_sha256", ADAPTER_SHA),
        ("anchor_engine_overlay_apply_count", 2),
        ("anchor_search_overlay_apply_count", 2),
        ("safe_clamp_bridge_overlay_apply_count", 2),
        ("corrected_adapter_overlay_apply_count", 2),
        ("actual_compiler_process_count", 28),
        ("actual_completed_phase_count", 2),
        ("canonical_original_source_owner_count", 9),
        ("unchanged_canonical_source_owners_per_phase", 5),
        ("complete_public_practice_case_count", 416),
        ("complete_public_paired_observation_count", 1664),
        ("public_rust_slower_paired_observation_count", 937),
        ("expanded_holdout_proposal_case_count", SEALED_PROPOSAL_CASE_COUNT),
        ("candidate_matching", "NOT RUN"),
        ("candidate_correctness", NOT_MEASURED),
        ("candidate_qualified", False), ("holdout", "NOT OPENED"),
    ):
        require(receipt.get(key) == value,
                "the durable actual V26 success receipt omitted: " + key)
    record = {
        "schema": SCHEMA + "-durable-root-provenance-receipt",
        "version": VERSION,
        "status": "PASS",
        "publication_pass_means": "DURABLE FIRST-PARTY NATIVE SOURCE BUILD ONLY",
        "family": FAMILY, "label": LABEL,
        "source_sha256": options["source_sha256"],
        "protocol_sha256": options["protocol_sha256"],
        "contract_sha256": options["contract_sha256"],
        "previous_actual_v25_build_source_sha256": V25_OWNERS[0][2],
        "previous_actual_v25_build_protocol_sha256": V25_OWNERS[1][2],
        "previous_actual_v25_build_contract_sha256": V25_OWNERS[2][2],
        "previous_actual_v25_build_receipt_sha256": V25_RECEIPT_SHA,
        "previous_actual_v25_root_receipt_sha256": V25_ROOT_SHA,
        "latest_v25_candidate_failure_receipt_sha256": V25_CANDIDATE_FAILURE_SHA,
        "latest_v25_candidate_status": "FAIL",
        "latest_v25_semantic_mismatch_count": 1352,
        "latest_v25_substitution_mismatch_count": 240,
        "latest_v25_shape_mismatch_count": 1112,
        "latest_v25_verified_passing_case_count": 15877,
        "latest_v25_case_execution_denominator": 31237,
        "latest_v25_completed_suite_count": 13,
        "latest_v25_actual_candidate_worker_count": 13,
        "latest_v25_infrastructure_failure_count": 0,
        "previous_actual_v25_engine_sha256":
            "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f",
        "previous_actual_v25_safe_bridge_elf_sha256":
            "adcb000c036e075a52f43926750648a4610e853e628d5433b1fbcc17e99a89e4",
        "latest_v24_candidate_failure_receipt_sha256": V24_FAILURE_SHA,
        "latest_v24_candidate_status": "FAIL",
        "latest_v24_semantic_mismatch_count": 1352,
        "latest_v24_verified_passing_case_count": 15877,
        "strict_non_delegation_audit_v4_source_sha256": AUDIT_OWNERS[0][2],
        "strict_non_delegation_audit_v4_protocol_sha256": AUDIT_OWNERS[1][2],
        "strict_non_delegation_audit_v4_contract_sha256": AUDIT_OWNERS[2][2],
        "strict_non_delegation_audit_v4_failure_receipt_sha256": STRICT_AUDIT_FAILURE_SHA,
        "strict_non_delegation_audit_v4_status": "FAIL; PRIVATE GETTER PRESENT",
        "strict_non_delegation_audit_v4_finding_code":
            "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE",
        "strict_non_delegation_audit_v4_finding_reachability":
            "PRIVATE_BRIDGE_BIND_GETTER; PUBLIC_MATCHING_DELEGATION_NOT_PROVEN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "mandatory_anchor_source_sha256": ANCHOR_OWNERS[0][2],
        "mandatory_anchor_protocol_sha256": ANCHOR_OWNERS[1][2],
        "mandatory_anchor_contract_sha256": ANCHOR_OWNERS[2][2],
        "mandatory_anchor_application_receipt_sha256": ANCHOR_OWNERS[3][2],
        "mandatory_anchor_engine_source_sha256": ANCHOR_LIB_SHA,
        "mandatory_anchor_engine_source_bytes": ANCHOR_LIB_BYTES,
        "mandatory_anchor_search_source_sha256": ANCHOR_SEARCH_SHA,
        "mandatory_anchor_search_source_bytes": ANCHOR_SEARCH_BYTES,
        "materialized_safe_clamp_bridge_sha256": BRIDGE_SHA,
        "materialized_safe_clamp_bridge_bytes": BRIDGE_BYTES,
        "corrected_public_adapter_sha256": ADAPTER_SHA,
        "corrected_public_adapter_bytes": ADAPTER_BYTES,
        "external_cargo_dependency_count": 0,
        "canonical_build_status": "PASS",
        "canonical_build_archive_relative": receipt["archive_relative"],
        "canonical_build_archive_sha256": receipt["archive_sha256"],
        "canonical_build_archive_bytes": receipt["archive_bytes"],
        "canonical_build_archive_opened": False,
        "canonical_build_receipt_relative": relative,
        "canonical_build_receipt_sha256": result["receipt_sha256"],
        "canonical_build_receipt_bytes": observed.st_size,
        "canonical_build_receipt_device": observed.st_dev,
        "canonical_build_receipt_inode": observed.st_ino,
        "root": capture["root"],
        "actual_compiler_process_count": 28,
        "expected_actual_compiler_process_count": 28,
        "actual_source_phase_count": 2,
        "actual_compiler_process_ids": capture["compiler_process_ids"],
        "mandatory_anchor_engine_overlay_apply_count": 2,
        "mandatory_anchor_search_overlay_apply_count": 2,
        "safe_clamp_bridge_overlay_apply_count": 2,
        "corrected_adapter_overlay_apply_count": 2,
        "total_private_source_overlay_apply_count": 8,
        "canonical_source_owners_per_phase": 9,
        "unchanged_canonical_source_owners_per_phase": 5,
        "distinct_private_source_identity_count": 18,
        "actual_private_source_owners": capture["private_source_owners"],
        "cross_phase_complete_engine_elf_byte_identical": True,
        "cross_phase_complete_bridge_elf_byte_identical": True,
        "actual_reproduced_native_outputs": capture["native_outputs"],
        "original_source_identity_count": 9,
        "actual_original_source_identities_before": canonical_before,
        "actual_original_source_identities_after": canonical_after,
        "actual_original_runtime_target_count": 4,
        "actual_original_runtime_targets_before": original_before,
        "actual_original_runtime_targets_after": original_after,
        "all_original_source_identities_restored": True,
        "all_original_runtime_target_identities_restored": True,
        "complete_public_practice_case_count": 416,
        "complete_public_paired_observation_count": 1664,
        "public_equal_case_geometric_speedup": "0.8485646292880136",
        "public_dense_case_geometric_speedup": "0.41613883193210616",
        "public_rust_slower_paired_observation_count": 937,
        "expanded_holdout_proposal_case_count": SEALED_PROPOSAL_CASE_COUNT,
        "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "candidate_correctness": NOT_MEASURED,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "native_libraries_loaded": 0,
        "canonical_sources_modified": False,
        "tmp_directory_scanned": False,
        "historical_archives_opened": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": NOT_MEASURED,
        "memory": NOT_MEASURED,
        "confidence_intervals": NOT_MEASURED,
        "undefined_behavior": NOT_MEASURED,
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    payload = module.canonical(record)
    require(0 < len(payload) <= module.MAX_SOURCE_BYTES,
            "bound the complete genuine V26 private-root provenance receipt")
    saved = kernel.write_fresh(module.ROOT / EVIDENCE_DIRECTORY / root_receipt_name(LABEL),
                               payload, synchronize=True)
    synced = kernel.fsync_directory(module.ROOT / EVIDENCE_DIRECTORY)
    require(saved.get("sha256") == digest(payload)
            and saved.get("bytes") == len(payload)
            and saved.get("exclusive_creation") is True
            and saved.get("file_fsync_completed") is True
            and synced.get("completed") is True,
            "exclusively create and synchronize the actual V26 private-root provenance")
    return {**result,
            "root_provenance_status": "PASS",
            "root_provenance_receipt_relative":
                EVIDENCE_DIRECTORY + "/" + root_receipt_name(LABEL),
            "root_provenance_receipt_sha256": saved["sha256"],
            "root_provenance_receipt_bytes": saved["bytes"],
            "root_provenance_directory_fsync": synced,
            "actual_compiler_process_count": 28,
            "actual_private_phase_count": 2,
            "actual_compiler_process_ids": capture["compiler_process_ids"],
            "actual_reproduced_native_outputs": capture["native_outputs"],
            "mandatory_anchor_engine_source_sha256": ANCHOR_LIB_SHA,
            "mandatory_anchor_search_source_sha256": ANCHOR_SEARCH_SHA,
            "safe_clamp_bridge_source_sha256": BRIDGE_SHA,
            "corrected_public_adapter_sha256": ADAPTER_SHA,
            "all_original_source_identities_restored": True,
            "all_original_runtime_target_identities_restored": True,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_matching": "NOT RUN",
            "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False,
            "holdout": "NOT OPENED"}


def run_actual(options: dict[str, object]) -> dict[str, object]:
    global ROOT_CAPTURE
    require(options.get("mode") == "--build" and options.get("label") == LABEL
            and options.get("root_authorized") is True
            and options.get("frozen_committed_pushed") is True
            and WALL_ACTIVE is False and ROOT_CAPTURE is None,
            "only root may run one actual precommitted and pushed V26 build")
    source_raw, source_info = dynamic(SOURCE, str(options["source_sha256"]))
    protocol_raw, protocol_info = dynamic(PROTOCOL, str(options["protocol_sha256"]))
    contract_raw, contract_info = dynamic(CONTRACT, str(options["contract_sha256"]))
    require(source_raw.startswith(b"#!/usr/bin/env python3\n")
            and b"SOURCE-ONLY WALL" in protocol_raw,
            "independently authenticate the complete authorized V26 source freeze")
    transformer, owners, public_context = authenticate_public_context()
    complete = decode(transformer, contract_raw, "complete root-authorized pushed V26 contract")
    require(complete == frozen_contract(source_info, protocol_info, public_context)
            and (transformer.canonical(complete) + "\n").encode("ascii") == contract_raw,
            "actual compilation requires the complete independently caller-pinned source freeze")
    owner_identities = public_context["owners"]
    require(type(owner_identities) is list and len(owner_identities) >= 9,
            "record all nine descriptor-bound original Rust source identities")
    canonical_before = {row[1]: identity
                        for row, identity in zip(CANONICAL_OWNERS, owner_identities[:9])}
    require(len(canonical_before) == 9,
            "retain all independently authenticated canonical source owners")

    previous_name = "_rebar_v26_authenticated_previous_v25_public_controller"
    bootstrap_name = "_rebar_v26_authenticated_previous_v22_public_bootstrap"
    kernel_name = "_rebar_v26_authenticated_first_party_actual_native_v16"
    require(all(name not in sys.modules for name in
                (previous_name, bootstrap_name, kernel_name)),
            "reject reused, imported, or cross-candidate actual V26 build controllers")
    previous_raw = owners["v25_source"]
    v25 = types.ModuleType(previous_name)
    v25.__file__ = ROOT + "/" + V25_OWNERS[0][1]
    sys.modules[previous_name] = v25
    try:
        exec(compile(previous_raw, v25.__file__, "exec", dont_inherit=True), v25.__dict__)
        require(v25.SCHEMA == "rebar-phase2-owned-rust-capture-clamp-source-build-v25"
                and v25.VERSION == 25 and v25.FAMILY == FAMILY
                and v25.PHASES == PHASES and v25.PROCESS_NAMES == PROCESS_NAMES
                and callable(v25.read_actual_owner)
                and callable(v25.snapshot_actual_original_targets),
                "execute only the exact pushed prior genuine first-party V25 controller")
        original_before = v25.snapshot_actual_original_targets()
        bootstrap_raw, _bootstrap_identity = v25.read_actual_owner(v25.PUBLIC_OWNERS[8])
        bootstrap = types.ModuleType(bootstrap_name)
        bootstrap.__file__ = ROOT + "/" + v25.PUBLIC_OWNERS[8][1]
        sys.modules[bootstrap_name] = bootstrap
        exec(compile(bootstrap_raw, bootstrap.__file__, "exec", dont_inherit=True),
             bootstrap.__dict__)
        require(bootstrap.SCHEMA
                == "rebar-phase2-owned-rust-capture-shape-semantics-source-build-v22"
                and bootstrap.VERSION == 22 and bootstrap.FAMILY == FAMILY
                and bootstrap.PHASES == PHASES and bootstrap.PROCESS_NAMES == PROCESS_NAMES
                and callable(bootstrap.bootstrap_controllers),
                "authenticate the complete frozen first-party operational V22 lineage")
        _semantic, previous, parent, ancestor, base = bootstrap.bootstrap_controllers()
        require(type(previous) is dict and type(parent) is dict
                and type(ancestor) is dict and type(base) is dict
                and base.get("_WALL_ENABLED") is False
                and len(tuple(base.get("RUST_SOURCE_NAMES", ()))) == 9,
                "reject an active source wall or substituted actual first-party build chain")
        additions = {ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL,
                     ROOT + "/" + CONTRACT}
        additions.update(ROOT + "/" + row[1] for row in OWNERS)
        additions.update(ROOT + "/" + row[1] for row in v25.STATIC_OWNERS)
        base["_ALLOWLIST"] = frozenset(set(base["_ALLOWLIST"]) | additions)
        base["verify_future_phase_one_v4"](options)
        v21_context, v21_state = previous["collect_context"](
            parent, ancestor, base,
            bootstrap.V21["source"][2], bootstrap.V21["protocol"][2],
            bootstrap.V21["contract"][2],
        )
        previous_state = v21_state.get("v18_state")
        require(v21_context.get("status") == "PASS"
                and type(previous_state) is dict
                and type(previous_state.get("originals")) is dict
                and len(previous_state["originals"]) == 9
                and type(previous_state.get("corrected_adapter")) is bytes
                and len(previous_state["corrected_adapter"]) == ADAPTER_BYTES
                and digest(previous_state["corrected_adapter"]) == ADAPTER_SHA
                and type(previous_state.get("low_level_v9_source")) is bytes,
                "retain nine unchanged canonical owners and the exactly corrected adapter")
        kernel_raw = previous_state["owners"]["v16_builder"]
        owner = base["OWNER_BY_NAME"]["v16_builder"]
        require(type(kernel_raw) is bytes and digest(kernel_raw) == owner[2]
                and digest(kernel_raw)
                == "bcea8f23fc5e52af1e8062145d75ef1a6ed835cea3ac113a155cc8ebf3116a8a"
                and len(kernel_raw) == 134640,
                "load only the actual frozen zero-dependency 28-process V16 compiler kernel")
        module = types.ModuleType(kernel_name)
        module.__file__ = ROOT + "/" + owner[1]
        sys.modules[kernel_name] = module
        exec(compile(kernel_raw, module.__file__, "exec", dont_inherit=True),
             module.__dict__)
        require(module.SCHEMA == "rebar-phase2-owned-rust-buffer-shape-source-build-v16"
                and module.VERSION == 16 and module.FAMILY == FAMILY
                and module.PHASES == PHASES and module.PROCESS_NAMES == PROCESS_NAMES
                and module.ROOT_PREFIX == ROOT_PREFIX
                and callable(module.run_build)
                and callable(module.verify_reproduced_phases),
                "reject a dummy or delegated actual first-party 28-process build kernel")
        module.SCHEMA = SCHEMA
        module.VERSION = VERSION
        module.SOURCE_PATH = SOURCE
        module.PROTOCOL_PATH = PROTOCOL
        module.CONTRACT_PATH = CONTRACT
        module.FINAL_GRAPH_VERSION = previous["GRAPH_VERSION"]
        module.CURRENT_EVIDENCE_OWNER_LOWER_BOUND = previous["EVIDENCE_FLOOR"]
        module.CURRENT_HISTORY_REFERENCE_LOWER_BOUND = previous["HISTORY_FLOOR"]
        module.COMBINED_VARIANT = module.Owner(CLAMP_OWNERS[-1][1], BRIDGE_SHA, BRIDGE_BYTES)
        module.BUFFER_VARIANT = module.COMBINED_VARIANT
        module.BUFFER_FEATURE = tuple(
            module.Owner(base["OWNER_BY_NAME"][role][1],
                         base["OWNER_BY_NAME"][role][2],
                         base["OWNER_BY_NAME"][role][3])
            for role in ("v2_repair", "v2_protocol", "v2_contract")
        )
        module.FINAL_GRAPH = tuple(module.Owner(row[1], row[2], row[3])
                                   for row in parent["GRAPH"].values())
        state: dict[str, object] = {}
        verified = {
            "schema": SCHEMA + "-verified-actual-build-context",
            "version": VERSION, "status": "PASS", "family": FAMILY,
            "source": source_info, "protocol": protocol_info, "contract": contract_info,
            "previous_actual_v25_build_receipt_sha256": V25_RECEIPT_SHA,
            "previous_actual_v25_root_receipt_sha256": V25_ROOT_SHA,
            "latest_v25_candidate_failure_receipt_sha256": V25_CANDIDATE_FAILURE_SHA,
            "latest_v25_candidate_status": "FAIL",
            "latest_v25_semantic_mismatch_count": 1352,
            "latest_v25_substitution_mismatch_count": 240,
            "latest_v25_shape_mismatch_count": 1112,
            "latest_v25_verified_passing_case_count": 15877,
            "latest_v25_case_execution_denominator": 31237,
            "latest_v25_completed_suite_count": 13,
            "latest_v25_actual_candidate_worker_count": 13,
            "latest_v25_infrastructure_failure_count": 0,
            "latest_v24_candidate_status": "FAIL",
            "latest_v24_semantic_mismatch_count": 1352,
            "strict_audit_v4_status": "FAIL; PRIVATE GETTER PRESENT",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "canonical_rust_source_owner_count": 9,
            "first_party_source_overlays_per_phase": 4,
            "external_cargo_dependency_count": 0,
            "mandatory_anchor_engine_source_sha256": ANCHOR_LIB_SHA,
            "mandatory_anchor_search_source_sha256": ANCHOR_SEARCH_SHA,
            "safe_clamp_bridge_source_sha256": BRIDGE_SHA,
            "corrected_public_adapter_sha256": ADAPTER_SHA,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False,
            "holdout": "NOT OPENED",
        }

        def verify_context(source_pin: str, protocol_pin: str,
                           contract_pin: str) -> tuple[dict[str, object], dict[str, object]]:
            require((source_pin, protocol_pin, contract_pin)
                    == (options["source_sha256"], options["protocol_sha256"],
                        options["contract_sha256"]),
                    "reject substituted independently pinned actual V26 source authority")
            runtime = {
                "originals": previous_state["originals"],
                "combined_bridge": owners["safe_clamp_bridge"],
                "corrected_adapter": previous_state["corrected_adapter"],
                "low_level_v9_source": previous_state["low_level_v9_source"],
                "anchor_lib": owners["anchor_lib"],
                "anchor_search": owners["anchor_search"],
            }
            state["runtime_state"] = runtime
            return verified, runtime

        original_expected = module.expected_source_owner

        def expected_owner(path: str) -> tuple[str, int]:
            if path == "candidates/rust/src/lib.rs":
                return ANCHOR_LIB_SHA, ANCHOR_LIB_BYTES
            if path == "candidates/rust/src/search.rs":
                return ANCHOR_SEARCH_SHA, ANCHOR_SEARCH_BYTES
            return original_expected(path)

        original_verify = module.verify_reproduced_phases

        def verify_phases(low_level: types.ModuleType, kernel: types.ModuleType,
                          workdir: str, phases: list[dict[str, object]],
                          steps: list[dict[str, object]]) -> dict[str, object]:
            global ROOT_CAPTURE
            require(ROOT_CAPTURE is None and type(steps) is list and len(steps) == 28,
                    "require all 28 genuine compiler and ELF-audit processes")
            processes: set[int] = set()
            for number, operation in enumerate(steps):
                phase = PHASES[number // len(PROCESS_NAMES)]
                require(type(operation) is dict
                        and operation.get("name")
                        == PROCESS_NAMES[number % len(PROCESS_NAMES)]
                        and ("phase" not in operation or operation.get("phase") == phase)
                        and type(operation.get("pid")) is int
                        and operation["pid"] > 0 and operation["pid"] not in processes
                        and operation.get("exit_status") == 0
                        and operation.get("working_directory")
                        == "<FRESH_PRIVATE_TMP>/" + phase,
                        "reject missing, repeated, unsuccessful, or substituted native roles")
                processes.add(operation["pid"])
            descriptor, root = ancestor["capture_root_descriptor"](low_level, workdir, phases)
            try:
                proof = original_verify(low_level, kernel, workdir, phases, steps)
                require(type(proof) is dict and proof.get("status") == "PASS"
                        and proof.get("independent_fresh_phase_count") == 2
                        and proof.get("source_owners_per_phase") == 9
                        and proof.get("unique_process_count") == 28
                        and proof.get("combined_bridge_overlay_count") == 2
                        and proof.get("corrected_public_adapter_overlay_count") == 2
                        and proof.get("combined_bridge_sha256") == BRIDGE_SHA
                        and proof.get("combined_bridge_bytes") == BRIDGE_BYTES
                        and proof.get("corrected_public_adapter_sha256") == ADAPTER_SHA
                        and proof.get("byte_identical") is True
                        and proof.get("native_libraries_loaded") == 0
                        and type(proof.get("native_outputs")) is dict
                        and set(proof["native_outputs"]) == {"engine", "bridge"},
                        "require two genuinely independent byte-identical native ELF builds")
                source_identities: set[tuple[int, int]] = set()
                private_owners: list[dict[str, object]] = []
                for number, phase in enumerate(phases):
                    require(phase.get("name") == PHASES[number],
                            "preserve independent ordered source phases")
                    rows = phase.get("fresh_source_owners")
                    require(type(rows) is dict and len(rows) == 9,
                            "require all nine complete private first-party source owners")
                    for item in rows.values():
                        require(type(item) is dict
                                and type(item.get("device")) is int
                                and type(item.get("inode")) is int,
                                "every fresh source owner needs a genuine inode")
                        identity = (item["device"], item["inode"])
                        require(identity not in source_identities,
                                "no private owner may be borrowed across phases")
                        source_identities.add(identity)
                    private_owners.append({"phase": PHASES[number],
                                           "owners": dict(rows)})
                    for path, expected_hash, expected_bytes in (
                        ("candidates/rust/src/lib.rs", ANCHOR_LIB_SHA, ANCHOR_LIB_BYTES),
                        ("candidates/rust/src/search.rs", ANCHOR_SEARCH_SHA,
                         ANCHOR_SEARCH_BYTES),
                    ):
                        row = rows.get(path)
                        marker = row.get("source_overlay") if type(row) is dict else None
                        require(type(marker) is dict and marker.get("status") == "PASS"
                                and marker.get("phase") == PHASES[number]
                                and marker.get("source_apply_count") == 1
                                and marker.get("derived_sha256") == expected_hash
                                and marker.get("derived_bytes") == expected_bytes,
                                "verify both exact genuine first-party anchor source overlays")
                require(len(source_identities) == 18,
                        "all private sources must have independent phase-specific inodes")
                after = os.fstat(descriptor)
                named = os.stat(workdir, follow_symlinks=False)
                require(stat.S_ISDIR(after.st_mode)
                        and stat.S_IMODE(after.st_mode) == 0o700
                        and after.st_uid == os.geteuid()
                        and (after.st_dev, after.st_ino) == (root["device"], root["inode"])
                        and (named.st_dev, named.st_ino) == (root["device"], root["inode"]),
                        "reject a substituted, exchanged, or exposed private V26 build root")
                proof["unchanged_source_owners_per_phase"] = 5
                proof["anchor_engine_overlay_count"] = 2
                proof["anchor_search_overlay_count"] = 2
                proof["anchor_engine_sha256"] = ANCHOR_LIB_SHA
                proof["anchor_search_sha256"] = ANCHOR_SEARCH_SHA
                proof["distinct_private_source_identity_count"] = 18
                proof["total_private_source_overlay_apply_count"] = 8
                ROOT_CAPTURE = {"root": root, "phase_count": 2,
                                "unique_process_count": 28,
                                "compiler_process_ids": sorted(processes),
                                "native_outputs": proof["native_outputs"],
                                "private_source_owners": private_owners}
                return proof
            finally:
                os.close(descriptor)

        module.verify_frozen_context = verify_context
        module.expected_source_owner = expected_owner
        module.copy_combined_snapshot = lambda workdir, family, phase, originals: (
            copy_four_overlays(module, workdir, family, phase, originals)
        )
        module.verify_reproduced_phases = verify_phases
        module.evidence_names = evidence_names
        module.publish_build_report = (
            lambda kernel, report: publish_actual_build(module, kernel, report)
        )
        root_target = ROOT + "/" + EVIDENCE_DIRECTORY + "/" + root_receipt_name(LABEL)
        try:
            os.lstat(root_target)
        except FileNotFoundError:
            pass
        else:
            raise BuildFreezeError("reject preexisting actual V26 private-root provenance")

        class ActualOptions:
            pass

        forwarded = ActualOptions()
        for key in ("source_sha256", "protocol_sha256", "contract_sha256",
                    "label", "owned_source_sha256", "combined_bridge_sha256",
                    "combined_bridge_bytes", "corrected_adapter_sha256",
                    "corrected_adapter_bytes"):
            setattr(forwarded, key, options[key])
        result = module.run_build(forwarded)
        require(type(result) is dict and result.get("family") == FAMILY,
                "publish only one actual authorized first-party V26 compiler outcome")
        original_after = v25.snapshot_actual_original_targets()
        require(original_before == original_after,
                "preserve exact canonical original source, adapter, and native identities")
        canonical_after = {row[1]: owned(row)[1] for row in CANONICAL_OWNERS}
        require(canonical_before == canonical_after,
                "preserve complete identical before-and-after ownership of all nine originals")
        if result.get("status") != "PASS":
            require(result.get("build_status") == "FAIL"
                    and result.get("failure_preserved") is True,
                    "durably preserve real V26 compilation failures without inventing success")
            return {**result, "root_provenance_status": "NOT CREATED",
                    "all_original_runtime_target_identities_restored": True}
        return publish_actual_root(module, state, result, options,
                                   original_before, original_after,
                                   canonical_before, canonical_after)
    finally:
        for name in (kernel_name, bootstrap_name, previous_name):
            sys.modules.pop(name, None)


def parse_source(arguments: list[str]) -> tuple[str, str, str, str | None]:
    require(type(arguments) is list and arguments
            and arguments[0] in ("--render-contract", "--verify-frozen-context", "--self-test"),
            "select one physically isolated first-party V26 source-only gate")
    mode = arguments[0]
    values: dict[str, str] = {}
    position = 1
    while position < len(arguments):
        require(position + 1 < len(arguments),
                "independently pin every complete V26 source-only owner")
        name, value = arguments[position], arguments[position + 1]
        require(name in ("--source-sha256", "--protocol-sha256", "--contract-sha256")
                and name not in values,
                "reject unknown, repeated, or unpinned source-only authority")
        values[name] = hash_pin(value, name)
        position += 2
    expected = {"--source-sha256", "--protocol-sha256"}
    if mode != "--render-contract":
        expected.add("--contract-sha256")
    require(set(values) == expected,
            "require the exact independently pinned source-only verification authority")
    return mode, values["--source-sha256"], values["--protocol-sha256"], \
        values.get("--contract-sha256")


def main(arguments: list[str]) -> int:
    try:
        require(sys.executable == PYTHON
                and sys.version_info[:3] == (3, 14, 6)
                and sys.flags.isolated == 1 and sys.flags.no_site == 1
                and sys.flags.dont_write_bytecode == 1,
                "run only pinned official CPython 3.14.6 with -I -B -S")
        require(type(arguments) is list and bool(arguments),
                "select one isolated source gate or independently authorized actual build")
        if arguments[0] == "--build":
            result = run_actual(parse_actual(arguments))
            output = sys.modules.get("_rebar_v26_read_only_frozen_anchor_source")
        else:
            mode, source_sha, protocol_sha, contract_sha = parse_source(arguments)
            result = source_only(mode, source_sha, protocol_sha, contract_sha)
            output = sys.modules.get("_rebar_v26_read_only_frozen_anchor_source")
        require(type(output) is types.ModuleType and callable(output.canonical),
                "emit deterministic complete first-party canonical JSON only")
        sys.stdout.write(output.canonical(result) + "\n")
        sys.stdout.flush()
        return 0
    except BaseException as error:
        try:
            sys.stderr.write("V26 first-party anchor build FAILED: "
                             + type(error).__name__ + ": " + str(error)[:8192] + "\n")
            sys.stderr.flush()
        except BaseException:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
