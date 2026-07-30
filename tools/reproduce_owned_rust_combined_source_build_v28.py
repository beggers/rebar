#!/usr/bin/env python3
"""Freeze and, only after root authorization, build the combined Rust V28.

Every source gate installs an irreversible deny-default wall before opening an
owner.  The retired V2 final-holdout proposal is metadata-only and explicitly
INVALIDATED; REKEYED SUCCESSOR REQUIRED.  Actual compilation is a separate,
caller-pinned, committed-and-pushed, root-only operation using the authentic
V16/V9/V7/V4 first-party 28-process offline compiler and ELF-audit kernel.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("the V28 first-party source boundary must not load a matcher")

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
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
DEVICE = 2064
SOURCE = "tools/reproduce_owned_rust_combined_source_build_v28.py"
PROTOCOL = "oracle/phase2/RUST-COMBINED-SOURCE-BUILD-V28.md"
CONTRACT = "oracle/phase2/rust-combined-source-build-v28.json"
SCHEMA = "rebar-phase2-owned-rust-combined-source-build-v28"
VERSION = 28
FAMILY = "rust"
LABEL = "phase2-v28-rust-combined-source-root-provenance"
FINAL_HOLDOUT_STATUS = "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
RETIRED_PROPOSAL = "oracle/phase3/expanded-sealed-holdout-v2.json"
RETIRED_PROPOSAL_SHA = "5d9fa3920c1dcabc92a3521d742cd10ec399cff1a979b71ac079daba6f92cba0"
RETIRED_PROPOSAL_BYTES = 15561
RETIRED_PROPOSAL_INODE = 525920
RETIRED_PROPOSAL_CASE_COUNT = 141557760
ENGINE_SHA = "c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee"
ENGINE_BYTES = 189423
SEARCH_SHA = "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7"
SEARCH_BYTES = 24305
BRIDGE_SHA = "2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7"
BRIDGE_BYTES = 177146
ADAPTER_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
ADAPTER_BYTES = 31934
MAX_OWNER_BYTES = 2 * 1024 * 1024
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)

# role, exact workspace-relative path, complete SHA-256, bytes, device-2064 inode
CANONICAL_OWNERS = (
    ("cargo_lock", "candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, 428098),
    ("cargo_manifest", "candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, 428094),
    ("original_bridge", "candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676, 419054),
    ("original_engine", "candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967, 428096),
    ("original_newline", "candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416, 427958),
    ("original_search", "candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773, 429682),
    ("original_stack", "candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269, 428151),
    ("original_unicode", "candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989, 428152),
    ("original_adapter", "candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151, 428100),
)

# These are inspected only after every explicit root-only actual-build pin has
# passed.  No source gate may open or inspect either installed native file.
ACTUAL_RUNTIME_TARGETS = (
    ("original_engine_source", "candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967, 428096, 0o600),
    ("original_bridge_source", "candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676, 419054, 0o600),
    ("original_public_adapter", "candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151, 428100, 0o600),
    ("original_installed_engine", "candidates/_rust_engine.so", "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4", 660440, 430563, 0o755),
    ("original_installed_bridge", "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so", "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15", 144992, 430629, 0o755),
)

STATIC_OWNERS = CANONICAL_OWNERS + (
    ("goal", "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044),
    ("original_phase_one", "oracle/phase1/p0-completeness-v4.json", "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("anchor_transformer", "tools/apply_owned_rust_mandatory_anchor_search_v1.py", "d118af0c0da3b058fc8d40a59d47090a97fd8838fcbdb0fba36bcd0271da2eff", 74375, 429756),
    ("compiler_transformer", "tools/apply_owned_rust_compiler_allocation_fastpath_v1.py", "13ad7948ba05a057f1c93f404998d72217ad42a8a93da8d71f9a3f7b5a41d1bf", 75362, 429789),
    ("anchor_variant_engine", "candidates/rust/variants/mandatory_anchor_search_v1/lib.rs", "5fa8c47c88c1f5d830a59735946378910374afab6f1558d281f0254207ad5e84", 189369, 526181),
    ("compiler_variant_engine", "candidates/rust/variants/compiler_allocation_fastpath_v1/lib.rs", "64228afb698f5326e6a30fd93c2ea27bd81653ecdd4a4a8e2b0dda5983e895b6", 178021, 526157),
    ("adapter_repair_source", "tools/apply_owned_rust_public_contract_source_repair_v3.py", "5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859", 92060, 431033),
    ("adapter_repair_protocol", "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md", "2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34", 6405, 524675),
    ("adapter_repair_contract", "oracle/phase2/rust-public-contract-source-repair-v3.json", "82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1", 14817, 524678),
    ("combined_v2_source", "tools/apply_owned_rust_combined_search_compiler_fastpath_v2.py", "f8f2f7cf4e9339cf592048fd75cafe9a9d22d79c77137d1f8ab6d3b7493d976b", 89742, 430531),
    ("combined_v2_protocol", "oracle/phase2/RUST-COMBINED-SEARCH-COMPILER-FASTPATH-V2.md", "b612af3b53bb21b6f13b69db4c4197590a71af045fab14de250dad301a1794a1", 5577, 524866),
    ("combined_v2_contract", "oracle/phase2/rust-combined-search-compiler-fastpath-v2.json", "68f097d8433596fb45a9a9ca940eff68dcb8fe9f0d667a8c0ce9c5eb403196a6", 13914, 524939),
    ("combined_v2_application", "oracle/phase2/evidence/rust-combined-search-compiler-fastpath-v2-application.json", "1bce63305e04e4056ce3c660760a0bb8a3670a76aa528b9309232d0918c5061e", 2201, 525099),
    ("combined_v2_engine", "candidates/rust/variants/combined_search_compiler_fastpath_v2/lib.rs", ENGINE_SHA, ENGINE_BYTES, 525097),
    ("combined_v2_search", "candidates/rust/variants/combined_search_compiler_fastpath_v2/search.rs", SEARCH_SHA, SEARCH_BYTES, 525098),
    ("no_introspection_source", "tools/apply_owned_rust_no_external_introspection_v1.py", "68cafe6b6bdf336aff162f86c4c9ddc1aec7607e312c09b2a032e7462e466ec7", 61181, 430722),
    ("no_introspection_protocol", "oracle/phase2/RUST-NO-EXTERNAL-INTROSPECTION-V1.md", "15f068ecd0c1970d8bec1f9cb011072c09cb5d064938c24abe1088e4565268c3", 6240, 526268),
    ("no_introspection_contract", "oracle/phase2/rust-no-external-introspection-v1.json", "224e118a3878692552b31d588b38ea4953bee9c77c7853687b424360776b53d2", 5305, 526270),
    ("no_introspection_application", "oracle/phase2/evidence/rust-no-external-introspection-v1-application.json", "57e28ad65b538db5189f264904d303f37f13506022eae07b12185a52f2624a43", 1774, 524813),
    ("no_introspection_bridge", "candidates/rust/variants/no_external_introspection_v1/py_bridge.c", BRIDGE_SHA, BRIDGE_BYTES, 524811),
    ("v25_build_source", "tools/reproduce_owned_rust_capture_clamp_source_build_v25.py", "f0a5d0b0af76b83e4f7091050afc187458c8c4380a37418f5df0de41d882b408", 186263, 429530),
    ("v25_build_protocol", "oracle/phase2/RUST-CAPTURE-CLAMP-SOURCE-BUILD-V25.md", "ddc7c1fcf385ec979c73a304123025a6e5974a8eb37dd61cf189ccba20687f85", 7140, 525993),
    ("v25_build_contract", "oracle/phase2/rust-capture-clamp-source-build-v25.json", "528d2bcccb2cceed5f607f7ec8428b18df10f30b9b6b6f7313083a288061127a", 229419, 526066),
    ("v25_build_publication", "oracle/phase2/evidence/native-source-build-v25-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-publication-receipt.json", "55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc", 5231, 526084),
    ("v25_build_root", "oracle/phase2/evidence/native-source-build-v25-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-root-provenance-receipt.json", "e8633ac1224235db9f8ea48c683c833fba3015cd73f071cd2488fa0b13a117a2", 61798, 526085),
    ("v25_full_failure", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json", "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59", 11832, 524846),
    ("v26_build_source", "tools/reproduce_owned_rust_anchor_source_build_v26.py", "7a276a4bf675f818cfe3716aad13c5e741f4a45709e899c82af36e2b4cb10e66", 112085, 430771),
    ("v26_build_protocol", "oracle/phase2/RUST-ANCHOR-SOURCE-BUILD-V26.md", "06ffb539e1f9e2bf7350b1d27478c988dd7c429f2ee295e40181b9320b3e3fd3", 7578, 524812),
    ("v26_build_contract", "oracle/phase2/rust-anchor-source-build-v26.json", "ea213e235fb56ca4235763643d5569ebb1b63c45678363efe322a525eef65924", 21189, 524863),
    ("v26_build_publication", "oracle/phase2/evidence/native-source-build-v26-rust-phase2-v26-rust-mandatory-anchor-root-provenance-publication-receipt.json", "8a0e9d70dab2a3e1f3738d6e0e1a4716b78e0a1b329ce3b16010bd94b6598cd6", 5075, 524963),
    ("v26_build_root", "oracle/phase2/evidence/native-source-build-v26-rust-phase2-v26-rust-mandatory-anchor-root-provenance-root-provenance-receipt.json", "aaed35f9fe86090d75ce2162bae7902910461a7b4e731c22eba275406f328ba1", 76442, 524964),
    ("v27_build_source", "tools/reproduce_owned_rust_compiler_fastpath_source_build_v27.py", "4ac3123d83db6858a9fddd311b3b7ac7966e29aede6e786594c7d956e2bf9e8e", 245008, 429062),
    ("v27_build_protocol", "oracle/phase2/RUST-COMPILER-FASTPATH-SOURCE-BUILD-V27.md", "43b81f47a196d3db0972269d6fba4d94b4437cb59a1c5a3648d8d45f5939fa5f", 5810, 524809),
    ("v27_build_contract", "oracle/phase2/rust-compiler-fastpath-source-build-v27.json", "a2ffa190a8fd15ec3bcf82f0e1eedc5eb4b919af8c6b3fbf99cf54a525604a41", 617433, 524861),
    ("v27_build_publication", "oracle/phase2/evidence/native-source-build-v27-rust-phase2-v27-rust-compiler-fast-v1-root-provenance-publication-receipt.json", "7fcbe3e07885f2a488ed1b3c79bc02888ad22dd2b21179081b3cecfc7b464c99", 6444, 524869),
    ("v27_build_root", "oracle/phase2/evidence/native-source-build-v27-rust-phase2-v27-rust-compiler-fast-v1-root-provenance-root-provenance-receipt.json", "c6958056757ab6145d613490db1a21165714dcb89c61e6d3bdf52500fad221b0", 64122, 524870),
    ("strict_audit_source", "tools/audit_candidate_runtime_non_delegation_v4.py", "597f2f1156d773a42e32103ef7370e8552a416756910c013cdcd0cfc34d39b02", 121807, 429582),
    ("strict_audit_protocol", "oracle/phase2/RUNTIME-NON-DELEGATION-V4.md", "6c3bd6b2ccabe3ab240771d743afce5b32f1de17a510bedd835e867c5cea7826", 5325, 526087),
    ("strict_audit_contract", "oracle/phase2/runtime-non-delegation-v4.json", "edc3ac8866da7afb5934b56fbcbff38a908e5109f7975f998753b479aa7bc672", 7266, 526086),
    ("strict_audit_failure", "oracle/phase2/evidence/runtime-non-delegation-v4-actual-source-audit-failure.json", "c3020fe067ad06c2bf7309a73b960884572addd9e984d01d2cf27d5cd9d61f19", 20985, 526140),
    ("public_profile", "oracle/phase3/rust-public-profile-v1.json", "b791b141eabbf6eb8a67484f5deb82bb41e324aedbdfe5b53a98ebc1553372c5", 1797, 525928),
    ("public_python", "experiments/rust_public_profile_v1/public-run-001/stdlib.correctness.raw.json", "efe0a3cc37194290b9577d5bd4f502a5c482016bc2b8ae90acec6254545b5381", 445036, 526005),
    ("public_rust", "experiments/rust_public_profile_v1/public-run-001/rust.correctness.raw.json", "8774ad035e17126252803e75494a80d376386a85e13c46cb3e0380b82dae89b0", 445394, 526006),
    ("public_paired", "experiments/rust_public_profile_v1/public-run-001/paired-timing.raw.json", "3da06bdb04ace9897d359aaa962ca412f3e9260a5c1a337703e0aa35567b6b85", 504907, 526015),
    ("public_graph", "docs/evidence/rust-public-practice-overall-v1.inputs.json", "ebcbce1c46a7c36be2b50e49c90e826f90b1822055c10fa89bf3984566be70fc", 16044, 429788),
    ("actual_v16_kernel", "tools/reproduce_owned_rust_buffer_shape_source_build_v16.py", "bcea8f23fc5e52af1e8062145d75ef1a6ed835cea3ac113a155cc8ebf3116a8a", 134640, 431980),
    ("actual_v9_kernel", "tools/reproduce_owned_native_source_build_v9.py", "c4a4b85b92ef0d600528732c9e0acb8f8303b7b2fbfc320e84c9b9e2d384219f", 81124, 429976),
    ("actual_v7_kernel", "tools/reproduce_owned_native_source_build_v7.py", "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7", 300624, 431752),
    ("actual_v4_kernel", "tools/reproduce_owned_native_source_build_v4.py", "efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1", 136084, 431135),
)

OWNER_BY_ROLE = {row[0]: row for row in STATIC_OWNERS}
SOURCE_MODES = ("--render-contract", "--verify-frozen-context", "--self-test")
ACTUAL_MODES = ("--build", "--run")
NOT_MEASURED = "NOT MEASURED"


class BuildFreezeError(Exception):
    """A complete V28 source owner, isolated gate, or actual build changed."""


def require(value: object, explanation: str) -> None:
    if value is not True:
        raise BuildFreezeError(explanation)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete immutable first-party bytes")
    return hashlib.sha256(raw).hexdigest()


def hash_pin(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value)
            and len(set(value)) > 1,
            "require one independently pinned complete SHA-256: " + label)
    assert isinstance(value, str)
    return value


def commit_pin(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(character in "0123456789abcdef" for character in value)
            and len(set(value)) > 1,
            "require one complete independently caller-pinned commit: " + label)
    assert isinstance(value, str)
    return value


def clean_imports() -> None:
    forbidden = (
        "re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
        "ctypes", "subprocess", "socket", "threading", "multiprocessing",
        "concurrent.interpreters", "candidates", "rebar",
    )
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject a candidate, regular-expression engine, loader, or worker")


class SourceWall:
    """Irreversible descriptor-only source isolation plus one retired-file stat."""

    def __init__(self) -> None:
        require(len(OWNER_BY_ROLE) == len(STATIC_OWNERS),
                "every pinned source owner must have a distinct role")
        relatives = (SOURCE, PROTOCOL, CONTRACT) + tuple(row[1] for row in STATIC_OWNERS)
        require(len(relatives) == len(frozenset(relatives)),
                "reject duplicate or aliased pinned first-party source paths")
        self.allowed = frozenset(ROOT + "/" + path for path in relatives)
        self.dynamic = {
            ROOT + "/" + OWNER_BY_ROLE["anchor_transformer"][1]:
                OWNER_BY_ROLE["anchor_transformer"][2],
            ROOT + "/" + OWNER_BY_ROLE["compiler_transformer"][1]:
                OWNER_BY_ROLE["compiler_transformer"][2],
            ROOT + "/" + OWNER_BY_ROLE["combined_v2_source"][1]:
                OWNER_BY_ROLE["combined_v2_source"][2],
        }
        self.retired = ROOT + "/" + RETIRED_PROPOSAL
        self.live: set[int] = set()
        self.blocked: dict[str, int] = {}
        self.proposal_metadata_probes = 0
        self.proposal_content_opens = 0
        self.pending_name: str | None = None
        self.pending_code: object | None = None
        self.installed = False
        self._raw_open = os.open
        self._raw_read = os.read
        self._raw_fstat = os.fstat
        self._raw_stat = os.stat
        self._raw_lstat = os.lstat

    def deny(self, category: str, explanation: str) -> object:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise BuildFreezeError("the V28 irreversible source wall rejected " + explanation)

    def audit(self, event: str, arguments: tuple[object, ...]) -> None:
        if not self.installed:
            return
        if event == "open":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            flags = arguments[2] if len(arguments) > 2 else None
            if type(path) is str and path == self.retired:
                self.deny("final_holdout", "content access to the invalidated V2 proposal")
            if type(flags) is not int:
                self.deny("foreign_read", "an unpinned descriptor or file mode")
            if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
                os.O_CREAT | os.O_EXCL | os.O_TRUNC | os.O_APPEND
            ) or (getattr(os, "O_TMPFILE", 0)
                  and flags & os.O_TMPFILE == os.O_TMPFILE):
                self.deny("write", "a destructive, temporary, or writable source open")
            if type(mode) is str and any(character in mode for character in "wax+"):
                self.deny("write", "a writable source-mode file object")
            if type(path) is not str or path not in self.allowed:
                spelling = path.lower() if type(path) is str else "descriptor"
                if spelling.startswith("/tmp/"):
                    self.deny("private_root", "a private build root or installed runtime")
                if any(term in spelling for term in
                       ("holdout", "sealed", "hidden", "fixture", ".gz", "archive")):
                    self.deny("final_holdout", "a final case, hidden case, or archive")
                if spelling.endswith((".so", ".dll", ".dylib")):
                    self.deny("native", "an installed or private native binary")
                if "candidate" in spelling:
                    self.deny("candidate", "an unapproved candidate source or runtime")
                self.deny("foreign_read", "an unapproved source owner")
            if not flags & getattr(os, "O_NOFOLLOW", 0):
                self.deny("foreign_read", "a symlink-following source descriptor")
            return
        if event == "import":
            self.deny("candidate", "a late module, candidate, native, or regex import")
        if event == "compile":
            payload = arguments[0] if arguments else None
            filename = arguments[1] if len(arguments) > 1 else None
            if type(filename) is not str or filename != self.pending_name:
                self.deny("candidate", "compilation of unapproved executable source")
            if type(payload) is not bytes or digest(payload) != self.dynamic.get(filename):
                self.deny("candidate", "compilation of unauthenticated predecessor bytes")
            return
        if event == "exec":
            code = arguments[0] if arguments else None
            if code is not self.pending_code:
                self.deny("candidate", "execution of unapproved candidate or code")
            return
        if event.startswith(("subprocess.", "os.posix_spawn", "os.spawn", "os.exec",
                             "os.fork", "os.system", "_interpreters.", "threading.",
                             "_thread.", "cpython.PyInterpreterState_New")):
            self.deny("process", "a candidate, compiler, profiler, or worker")
        if event.startswith(("ctypes.", "os.dlopen", "marshal.loads")):
            self.deny("native", "a native binary, imported object, or code loader")
        if event.startswith("socket."):
            self.deny("network", "a socket or network request")
        if event.startswith(("os.mkdir", "os.rmdir", "os.remove", "os.unlink",
                             "os.rename", "os.replace", "os.chmod", "os.chown",
                             "os.link", "os.symlink", "os.truncate", "shutil.")):
            self.deny("write", "a workspace, candidate, or final-case mutation")
        if event in ("os.listdir", "os.scandir", "glob.glob"):
            self.deny("foreign_read", "a private root, workspace, or case enumeration")

    def read(self, descriptor: int, count: int, /) -> bytes:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("foreign_read", "an inherited or unapproved source descriptor")
        return self._raw_read(descriptor, count)

    def fstat(self, descriptor: int, /) -> os.stat_result:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("foreign_read", "metadata for an inherited or native descriptor")
        return self._raw_fstat(descriptor)

    def metadata(self, path: object, *args: object, **kwargs: object) -> os.stat_result:
        if type(path) is not str or path != self.retired or args:
            self.deny("foreign_read", "direct metadata outside the retired V2 proposal")
        if kwargs and kwargs != {"follow_symlinks": False}:
            self.deny("foreign_read", "a symlink-following retired-proposal metadata probe")
        if self.proposal_metadata_probes != 0:
            self.deny("final_holdout", "a repeated or exploratory retired-proposal stat")
        self.proposal_metadata_probes += 1
        return self._raw_stat(path, follow_symlinks=False)

    def no_clock(self, *_args: object, **_kwargs: object) -> object:
        return self.deny("clock", "a clock, timer, profiler, or sleep")

    def no_entropy(self, *_args: object, **_kwargs: object) -> object:
        return self.deny("entropy", "randomness or generation of hidden cases")

    def no_direct_io(self, *_args: object, **_kwargs: object) -> object:
        return self.deny("foreign_read", "an unguarded Python file-object primitive")

    def install(self) -> None:
        require(self.installed is False, "the one-way V28 source wall was reused")
        sys.addaudithook(self.audit)
        self.installed = True
        os.read = self.read
        os.fstat = self.fstat
        os.stat = self.metadata
        os.lstat = self.metadata
        builtins.open = self.no_direct_io
        io.open = self.no_direct_io
        _io.open = self.no_direct_io
        if hasattr(os, "getrandom"):
            os.getrandom = self.no_entropy
        if hasattr(os, "urandom"):
            os.urandom = self.no_entropy
        for name in ("time", "time_ns", "clock_gettime", "clock_gettime_ns",
                     "clock_settime", "clock_settime_ns", "ctime", "gmtime",
                     "localtime", "strftime", "perf_counter", "perf_counter_ns",
                     "monotonic", "monotonic_ns", "process_time", "process_time_ns",
                     "thread_time", "thread_time_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.no_clock)
        if hasattr(os, "times"):
            os.times = self.no_clock


def read_owner(wall: SourceWall, row: tuple[object, ...]) -> tuple[bytes, dict[str, object]]:
    require(type(row) is tuple and len(row) == 5, "require a complete frozen owner")
    role, relative, expected, count, inode = row
    require(type(role) is str and type(relative) is str and relative
            and not relative.startswith("/") and ".." not in relative.split("/")
            and type(count) is int and 0 < count <= MAX_OWNER_BYTES
            and type(inode) is int and inode > 0,
            "reject an altered first-party source owner identity")
    hash_pin(expected, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    wall.live.add(descriptor)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == count and before.st_uid == os.geteuid()
                and before.st_nlink == 1,
                "a complete descriptor-pinned source owner changed: " + role)
        pieces: list[bytes] = []
        remaining = count
        while remaining:
            part = os.read(descriptor, min(remaining, 65536))
            require(type(part) is bytes and bool(part),
                    "a complete source owner was truncated: " + role)
            pieces.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"", "a frozen source owner grew: " + role)
        after = os.fstat(descriptor)
        require(all(getattr(before, field) == getattr(after, field)
                    for field in ("st_dev", "st_ino", "st_size", "st_nlink",
                                  "st_mtime_ns", "st_ctime_ns")),
                "a first-party owner changed during its complete descriptor read")
        raw = b"".join(pieces)
        require(digest(raw) == expected, "a complete source-owner digest changed: " + role)
        return raw, {"role": role, "path": relative, "sha256": expected,
                     "bytes": count, "device": before.st_dev, "inode": before.st_ino,
                     "mode": "0600", "uid": before.st_uid, "nlink": before.st_nlink}
    finally:
        wall.live.discard(descriptor)
        os.close(descriptor)


def live_owner(wall: SourceWall, role: str, relative: str,
               expected: str) -> tuple[bytes, dict[str, object]]:
    require(relative in (SOURCE, PROTOCOL, CONTRACT),
            "reject an unrelated or unauthenticated live V28 owner")
    hash_pin(expected, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    wall.live.add(descriptor)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode)
                and stat.S_IMODE(identity.st_mode) == 0o600
                and identity.st_dev == DEVICE and identity.st_uid == os.geteuid()
                and identity.st_nlink == 1 and 0 < identity.st_size <= MAX_OWNER_BYTES,
                "reject a substituted independently pinned V28 live owner")
        pieces: list[bytes] = []
        remaining = identity.st_size
        while remaining:
            part = os.read(descriptor, min(65536, remaining))
            require(bool(part), "a complete caller-pinned V28 owner ended early")
            pieces.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"", "a caller-pinned V28 owner grew")
        after = os.fstat(descriptor)
        require(all(getattr(identity, key) == getattr(after, key)
                    for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                "st_mtime_ns", "st_ctime_ns")),
                "a caller-pinned V28 owner changed during its descriptor read")
        raw = b"".join(pieces)
        require(digest(raw) == expected, "a caller-pinned V28 owner digest changed")
        return raw, {"role": role, "path": relative, "sha256": expected,
                     "bytes": identity.st_size, "device": identity.st_dev,
                     "inode": identity.st_ino, "mode": "0600", "uid": identity.st_uid,
                     "nlink": identity.st_nlink}
    finally:
        wall.live.discard(descriptor)
        os.close(descriptor)


def frozen_module(wall: SourceWall, role: str, payload: bytes) -> types.ModuleType:
    owner = OWNER_BY_ROLE[role]
    path = ROOT + "/" + owner[1]
    require(digest(payload) == owner[2] and len(payload) == owner[3]
            and wall.dynamic.get(path) == owner[2]
            and wall.pending_name is None and wall.pending_code is None,
            "execute only one complete independently pinned source transformer")
    name = "_rebar_v28_frozen_" + role
    require(name not in sys.modules, "reject a reused or substituted source transformer")
    module = types.ModuleType(name)
    module.__file__ = path
    sys.modules[name] = module
    wall.pending_name = path
    try:
        code = compile(payload, path, "exec", dont_inherit=True)
        wall.pending_code = code
        exec(code, module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    finally:
        wall.pending_name = None
        wall.pending_code = None
    clean_imports()
    return module


def public_document(parser: types.ModuleType, payload: bytes,
                    label: str) -> dict[str, object]:
    value = parser.StrictJSON(payload).document()
    require(type(value) is dict, "require one complete public JSON object: " + label)
    return value


def extract_adapter_literals(source: bytes) -> dict[str, bytes]:
    required = ("OLD_FLAG_BLOCK", "V2_FLAG_BLOCK", "OLD_ERROR_BLOCK",
                "V2_ERROR_BLOCK", "OLD_PATTERN_BLOCK", "V2_PATTERN_BLOCK",
                "V3_PATTERN_BLOCK")
    result: dict[str, bytes] = {}
    for name in required:
        marker = name.encode("ascii") + b' = b"""'
        require(source.count(marker) == 1,
                "require exactly one authenticated adapter repair literal: " + name)
        first = source.index(marker) + len(marker)
        last = source.find(b'"""', first)
        require(last >= first, "an authenticated adapter repair literal was truncated")
        result[name] = source[first:last]
    return result


def derive_adapter(original: bytes, repair: bytes) -> bytes:
    require(digest(original) == OWNER_BY_ROLE["original_adapter"][2]
            and len(original) == OWNER_BY_ROLE["original_adapter"][3]
            and digest(repair) == OWNER_BY_ROLE["adapter_repair_source"][2],
            "authenticate both complete immutable adapter-repair inputs")
    blocks = extract_adapter_literals(repair)
    fixed = original
    for before, after in (
        ("OLD_FLAG_BLOCK", "V2_FLAG_BLOCK"),
        ("OLD_ERROR_BLOCK", "V2_ERROR_BLOCK"),
        ("OLD_PATTERN_BLOCK", "V2_PATTERN_BLOCK"),
        ("V2_PATTERN_BLOCK", "V3_PATTERN_BLOCK"),
    ):
        previous, replacement = blocks[before], blocks[after]
        require(fixed.count(previous) == 1 and fixed.count(replacement) == 0,
                "each complete historical adapter repair must apply exactly once")
        fixed = fixed.replace(previous, replacement, 1)
    require(len(fixed) == ADAPTER_BYTES and digest(fixed) == ADAPTER_SHA,
            "reconstruct the exact independently frozen corrected public adapter")
    return fixed


def validate_bridge(payload: bytes, correction: dict[str, object],
                    application: dict[str, object]) -> None:
    require(len(payload) == BRIDGE_BYTES and digest(payload) == BRIDGE_SHA,
            "require the exact complete materialized NO-EXTERNAL-INTROSPECTION bridge")
    require(correction.get("target_path") == OWNER_BY_ROLE["no_introspection_bridge"][1]
            and correction.get("target_sha256") == BRIDGE_SHA
            and correction.get("target_bytes") == BRIDGE_BYTES
            and correction.get("deleted_private_function") == "rust_bound_get_signature"
            and correction.get("deleted_private_getset") == "__signature__"
            and correction.get("public_pattern_methods_use_native_descriptors") is True
            and correction.get("capture_clamp_correction_retained") is True,
            "preserve every independently frozen exact private-introspection correction")
    require(application.get("schema")
            == "rebar-owned-rust-no-external-introspection-v1-source-freeze-root-materialization"
            and application.get("status")
            == "PASS; EXACT PRIVATE INTROSPECTION REMOVED; NOT BUILT; NOT RUN"
            and application.get("source_sha256")
            == OWNER_BY_ROLE["no_introspection_source"][2]
            and application.get("protocol_sha256")
            == OWNER_BY_ROLE["no_introspection_protocol"][2]
            and application.get("contract_sha256")
            == OWNER_BY_ROLE["no_introspection_contract"][2]
            and application.get("target_path")
            == OWNER_BY_ROLE["no_introspection_bridge"][1]
            and application.get("target_sha256") == BRIDGE_SHA
            and application.get("target_bytes") == BRIDGE_BYTES
            and application.get("capture_clamp_preserved") is True
            and application.get("public_native_descriptors_preserved") is True,
            "authenticate the exact exclusively materialized safe bridge receipt")
    require(b"rust_bound_get_signature" not in payload
            and b'PyImport_ImportModule("inspect")' not in payload
            and b'"__signature__"' not in payload
            and payload.count(b"PyDescr_NewMethod(") >= 1
            and payload.count(b"Py_CLEAR(method->signature)") == 2
            and payload.count(b"Py_VISIT(method->signature)") == 1,
            "reject any restored private introspection getter or lost native descriptor")
    for forbidden in (b'PyImport_ImportModule("re")', b'PyImport_ImportModule("_sre")',
                      b'PyImport_ImportModule("inspect")', b"dlopen(", b"pcre2",
                      b"oniguruma", b"regex.compile"):
        require(forbidden not in payload,
                "reject delegated regular-expression matching in the complete safe bridge")


def retired_metadata(wall: SourceWall) -> dict[str, object]:
    current = os.lstat(ROOT + "/" + RETIRED_PROPOSAL)
    require(stat.S_ISREG(current.st_mode)
            and stat.S_IMODE(current.st_mode) == 0o600
            and current.st_dev == DEVICE and current.st_ino == RETIRED_PROPOSAL_INODE
            and current.st_size == RETIRED_PROPOSAL_BYTES
            and current.st_uid == os.geteuid() and current.st_nlink == 1
            and wall.proposal_metadata_probes == 1
            and wall.proposal_content_opens == 0,
            "authenticate retired V2 proposal by metadata only without reading content")
    return {
        "path": RETIRED_PROPOSAL,
        "sha256_historical_independent_pin_not_read": RETIRED_PROPOSAL_SHA,
        "bytes_metadata_only": RETIRED_PROPOSAL_BYTES,
        "device": current.st_dev,
        "inode_metadata_only": current.st_ino,
        "historical_proposed_case_count": RETIRED_PROPOSAL_CASE_COUNT,
        "metadata_probe_count": 1,
        "content_open_count_by_this_controller": 0,
        "hidden_cases_generated_by_this_controller": 0,
        "global_unopened_claim": False,
        "status": FINAL_HOLDOUT_STATUS,
        "reason": "RETIRED AFTER SOURCE-SCOPE ACCESS INCIDENT; NEVER A VALID FINAL",
        "replacement": "A FRESH REKEYED SUCCESSOR MUST BE INDEPENDENTLY FROZEN",
    }


def verify_history(parser: types.ModuleType,
                   originals: dict[str, bytes]) -> dict[str, object]:
    original = public_document(parser, originals["original_phase_one"], "frozen original P0")
    require(original.get("schema") == "rebar-cpython-re-p0-completeness-v4"
            and original.get("status") == "PASS"
            and original.get("original_case_execution_denominator") == 31237
            and original.get("original_suite_count") == 13
            and original.get("original_named_private_waiver_count") == 13
            and original.get("qualified_candidate_count") == 0,
            "preserve all 31237 original cases, 13 suites, and 13 private waivers")

    combined = public_document(parser, originals["combined_v2_contract"],
                               "independently frozen combined V2 source contract")
    require(combined.get("schema")
            == "rebar-first-party-rust-combined-search-compiler-fastpath-v2"
            and combined.get("version") == 2
            and combined.get("source", {}).get("sha256")
            == OWNER_BY_ROLE["combined_v2_source"][2]
            and combined.get("protocol", {}).get("sha256")
            == OWNER_BY_ROLE["combined_v2_protocol"][2]
            and combined.get("derived", {}).get("engine", {}).get("sha256") == ENGINE_SHA
            and combined.get("derived", {}).get("engine", {}).get("bytes") == ENGINE_BYTES
            and combined.get("derived", {}).get("search", {}).get("sha256") == SEARCH_SHA
            and combined.get("derived", {}).get("search", {}).get("bytes") == SEARCH_BYTES
            and combined.get("exact_commuting_composition", {}).get("replacement_count") == 7
            and combined.get("new_combined_synthetic_semantics", {})
                .get("combined_differential_case_count") == 111552,
            "authenticate exact complete V2 source, protocol, composition, and contract")
    application = public_document(parser, originals["combined_v2_application"],
                                  "actual exclusive combined V2 source application")
    created = application.get("created", {})
    require(application.get("schema")
            == "rebar-first-party-rust-combined-search-compiler-fastpath-v2-application"
            and application.get("status") == "APPLIED"
            and application.get("source_sha256") == OWNER_BY_ROLE["combined_v2_source"][2]
            and application.get("protocol_sha256") == OWNER_BY_ROLE["combined_v2_protocol"][2]
            and application.get("contract_sha256") == OWNER_BY_ROLE["combined_v2_contract"][2]
            and created.get("engine", {}).get("sha256") == ENGINE_SHA
            and created.get("engine", {}).get("bytes") == ENGINE_BYTES
            and created.get("engine", {}).get("inode")
            == OWNER_BY_ROLE["combined_v2_engine"][4]
            and created.get("search", {}).get("sha256") == SEARCH_SHA
            and created.get("search", {}).get("bytes") == SEARCH_BYTES
            and created.get("search", {}).get("inode")
            == OWNER_BY_ROLE["combined_v2_search"][4]
            and application.get("candidate_imports") == 0
            and application.get("compiler_processes_started") == 0
            and application.get("clock_samples") == 0,
            "authenticate both actually materialized V2 combined source owners")

    bridge = public_document(parser, originals["no_introspection_contract"],
                             "frozen private-introspection correction")
    bridge_application = public_document(parser, originals["no_introspection_application"],
                                         "actual exclusive private-getter correction")
    require(bridge.get("schema") == "rebar-owned-rust-no-external-introspection-v1-source-freeze"
            and bridge.get("source", {}).get("sha256")
            == OWNER_BY_ROLE["no_introspection_source"][2]
            and bridge.get("protocol", {}).get("sha256")
            == OWNER_BY_ROLE["no_introspection_protocol"][2],
            "authenticate the independent complete safe-bridge freeze triple")
    correction = bridge.get("exact_private_introspection_correction")
    require(type(correction) is dict, "require the complete safe bridge correction")
    validate_bridge(originals["no_introspection_bridge"], correction, bridge_application)

    latest = public_document(parser, originals["v25_full_failure"],
                             "complete independently published V25 original correctness")
    require(latest.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v25-durable-publication-receipt"
            and latest.get("status") == "PASS"
            and latest.get("candidate_status") == "FAIL"
            and latest.get("semantic_mismatch_count") == 1352
            and latest.get("verified_passing_case_count") == 15877
            and latest.get("case_execution_denominator") == 31237
            and latest.get("completed_suite_count") == 13
            and latest.get("actual_candidate_workers") == 13
            and latest.get("distinct_worker_process_id_count") == 13
            and latest.get("infrastructure_failure_count") == 0,
            "preserve the real complete V25 FAIL-1352; publication PASS is not candidate PASS")
    suites = latest.get("suite_integrity")
    require(type(suites) is list and len(suites) == 13
            and sum(item.get("case_execution_denominator", 0) for item in suites
                    if type(item) is dict) == 31237
            and {item.get("suite"): item.get("mismatch_count") for item in suites
                 if type(item) is dict and item.get("mismatch_count", 0)}
            == {"substitution_v2": 240, "shape_v2": 1112},
            "preserve all thirteen genuine suites and both fully observed mismatch families")

    audit = public_document(parser, originals["strict_audit_failure"],
                            "complete actual strict V4 non-delegation failure")
    findings = audit.get("findings")
    require(audit.get("status") == "FAIL"
            and audit.get("finding_count") == 1 and type(findings) is list
            and len(findings) == 1
            and findings[0].get("code") == "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE"
            and findings[0].get("severity") == "FAIL"
            and findings[0].get("family") == FAMILY
            and findings[0].get("path") == "candidates/rust/py_bridge.c",
            "preserve the historical strict FAIL-1 without inventing a fresh audit PASS")

    previous: dict[str, dict[str, object]] = {}
    for version in (25, 26, 27):
        publication = public_document(parser, originals[f"v{version}_build_publication"],
                                      f"actual successful V{version} native publication")
        root = public_document(parser, originals[f"v{version}_build_root"],
                               f"actual successful V{version} private-root provenance")
        require(publication.get("status") == "PASS"
                and publication.get("build_status") == "PASS"
                and publication.get("actual_compiler_process_count") == 28
                and publication.get("actual_completed_phase_count") == 2
                and publication.get("corrected_public_adapter_sha256") == ADAPTER_SHA
                and publication.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
                and publication.get("latest_v25_candidate_status", "FAIL") == "FAIL"
                and publication.get("latest_v25_semantic_mismatch_count", 1352) == 1352
                and root.get("status") == "PASS"
                and root.get("canonical_build_status") == "PASS"
                and root.get("canonical_build_receipt_sha256")
                == OWNER_BY_ROLE[f"v{version}_build_publication"][2]
                and root.get("actual_compiler_process_count") == 28
                and root.get("actual_source_phase_count") == 2
                and root.get("cross_phase_complete_bridge_elf_byte_identical") is True
                and root.get("cross_phase_complete_engine_elf_byte_identical") is True
                and root.get("corrected_public_adapter_sha256") == ADAPTER_SHA
                and root.get("corrected_public_adapter_bytes") == ADAPTER_BYTES,
                f"authenticate both actual complete independent successful V{version} receipts")
        previous[str(version)] = {
            "source_sha256": OWNER_BY_ROLE[f"v{version}_build_source"][2],
            "protocol_sha256": OWNER_BY_ROLE[f"v{version}_build_protocol"][2],
            "contract_sha256": OWNER_BY_ROLE[f"v{version}_build_contract"][2],
            "publication_receipt_sha256": OWNER_BY_ROLE[f"v{version}_build_publication"][2],
            "root_provenance_receipt_sha256": OWNER_BY_ROLE[f"v{version}_build_root"][2],
            "actual_compiler_process_count": 28,
            "actual_independent_source_phase_count": 2,
            "cross_phase_complete_engine_elf_byte_identical": True,
            "cross_phase_complete_bridge_elf_byte_identical": True,
            "publication_status": "PASS; DURABLE PUBLICATION ONLY",
            "candidate_status": "NOT PROVEN BY NATIVE BUILD",
        }

    profile = public_document(parser, originals["public_profile"], "public-only profile")
    python = public_document(parser, originals["public_python"], "public Python observations")
    rust = public_document(parser, originals["public_rust"], "public Rust observations")
    paired = public_document(parser, originals["public_paired"], "public paired rows")
    rows = paired.get("rows")
    require(profile.get("case_count") == 416
            and python.get("status") == "PASS" and python.get("case_count") == 416
            and rust.get("status") == "PASS" and rust.get("case_count") == 416
            and type(rows) is list and len(rows) == 1664,
            "preserve all 416 public cases and all 1664 complete paired observations")
    graph = originals["public_graph"]
    for marker in (
        b'"public_correctness_case_count":416',
        b'"public_paired_observation_count":1664',
        b'"public_rust_faster_pair_count":723',
        b'"public_rust_slower_pair_count":937',
        b'"public_tied_pair_count":4',
        b'"public_equal_case_geometric_speedup":0.8485646292880136',
        b'"dense_prefix_public_equal_case_geometric_speedup":0.41613883193210616',
    ):
        require(marker in graph, "preserve the exact historical public-practice evidence")

    v26 = public_document(parser, originals["v26_build_contract"],
                           "complete independently frozen V26 build contract")
    v27 = public_document(parser, originals["v27_build_contract"],
                           "complete independently frozen V27 build contract")
    require(v26.get("schema") == "rebar-phase2-owned-rust-anchor-source-build-v26-source-freeze"
            and v26.get("source", {}).get("sha256") == OWNER_BY_ROLE["v26_build_source"][2]
            and v26.get("protocol", {}).get("sha256") == OWNER_BY_ROLE["v26_build_protocol"][2]
            and v26.get("external_cargo_dependency_count") == 0
            and v26.get("canonical_original_rust_source_owner_count") == 9
            and v27.get("schema")
            == "rebar-phase2-owned-rust-compiler-fastpath-source-build-v27-source-freeze"
            and v27.get("source", {}).get("sha256") == OWNER_BY_ROLE["v27_build_source"][2]
            and v27.get("protocol", {}).get("sha256") == OWNER_BY_ROLE["v27_build_protocol"][2]
            and v27.get("frozen_offline_dual_phase_build", {}).get("phase_count") == 2
            and v27.get("frozen_offline_dual_phase_build", {})
                .get("external_cargo_dependency_count") == 0,
            "anchor both independently successful complete V26/V27 source-freeze triples")

    manifest = originals["cargo_manifest"]
    lock = originals["cargo_lock"]
    require(manifest.count(b"[package]") == 1
            and manifest.count(b'[lib]') == 1
            and b'crate-type = ["cdylib"]' in manifest
            and b"[dependencies]" not in manifest
            and lock.count(b"[[package]]") == 1
            and b'name = "rebar-rust-continuation"' in manifest
            and b'name = "rebar-rust-continuation"' in lock,
            "freeze exactly one first-party Cargo package and zero external dependencies")
    return {
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "latest_v25_candidate_status": "FAIL",
        "latest_v25_semantic_mismatch_count": 1352,
        "latest_v25_substitution_mismatch_count": 240,
        "latest_v25_shape_mismatch_count": 1112,
        "latest_v25_verified_passing_case_count": 15877,
        "latest_v25_completed_suite_count": 13,
        "latest_v25_actual_candidate_worker_count": 13,
        "latest_v25_infrastructure_failure_count": 0,
        "latest_v25_failure_receipt_sha256": OWNER_BY_ROLE["v25_full_failure"][2],
        "strict_audit_status": "FAIL; HISTORICAL PRIVATE GETTER PRESENT",
        "strict_audit_finding_count": 1,
        "strict_audit_finding_code": "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE",
        "strict_audit_failure_receipt_sha256": OWNER_BY_ROLE["strict_audit_failure"][2],
        "corrected_bridge_private_getter_removed": True,
        "corrected_bridge_fresh_strict_audit": "NOT RUN; NOT ESTABLISHED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "public_case_count": 416,
        "public_paired_observation_count": 1664,
        "public_rust_faster_paired_count": 723,
        "public_rust_slower_paired_count": 937,
        "public_tied_paired_count": 4,
        "previous_successful_native_builds": previous,
        "external_cargo_dependency_count": 0,
        "first_party_package_count": 1,
        "qualified_independent_candidate_count": 0,
        "final_holdout": FINAL_HOLDOUT_STATUS,
    }


def owner_document(row: tuple[object, ...]) -> dict[str, object]:
    return {"role": row[0], "path": row[1], "sha256": row[2],
            "bytes": row[3], "device": DEVICE, "inode": row[4],
            "mode": "0600", "nlink": 1}


def build_contract(source: dict[str, object], protocol: dict[str, object],
                   history: dict[str, object], proposal: dict[str, object],
                   composition: dict[str, object], anchor_model: dict[str, object],
                   compiler_model: dict[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "status": "SOURCE FROZEN; NATIVE BUILD NOT RUN; CORRECTNESS NOT MEASURED",
        "phase": "PHASE 2: FIRST-PARTY RUST CANDIDATE CORRECTNESS",
        "family": FAMILY,
        "source": source,
        "protocol": protocol,
        "authenticated_first_party_owner_count": len(STATIC_OWNERS),
        "authenticated_first_party_owners": [owner_document(row) for row in STATIC_OWNERS],
        "original_correctness": history,
        "retired_expanded_holdout_metadata_only": proposal,
        "final_holdout": FINAL_HOLDOUT_STATUS,
        "candidate_sources": {
            "combined_engine": owner_document(OWNER_BY_ROLE["combined_v2_engine"]),
            "combined_search": owner_document(OWNER_BY_ROLE["combined_v2_search"]),
            "no_external_introspection_bridge":
                owner_document(OWNER_BY_ROLE["no_introspection_bridge"]),
            "corrected_adapter": {
                "derivation": "FOUR EXACT AUTHENTICATED HISTORICAL BYTE SUBSTITUTIONS",
                "source_path": OWNER_BY_ROLE["original_adapter"][1],
                "source_sha256": OWNER_BY_ROLE["original_adapter"][2],
                "repair_source_path": OWNER_BY_ROLE["adapter_repair_source"][1],
                "repair_source_sha256": OWNER_BY_ROLE["adapter_repair_source"][2],
                "derived_sha256": ADAPTER_SHA,
                "derived_bytes": ADAPTER_BYTES,
                "candidate_adapter_executed": False,
            },
        },
        "authentic_combined_v2": {
            "source_sha256": OWNER_BY_ROLE["combined_v2_source"][2],
            "protocol_sha256": OWNER_BY_ROLE["combined_v2_protocol"][2],
            "contract_sha256": OWNER_BY_ROLE["combined_v2_contract"][2],
            "application_receipt_sha256": OWNER_BY_ROLE["combined_v2_application"][2],
            "replacement_count": 7,
            "combined_differential_case_count": 111552,
            "composition": composition,
            "anchor_synthetic_model": anchor_model,
            "compiler_synthetic_model": compiler_model,
        },
        "authentic_no_external_introspection_v1": {
            "source_sha256": OWNER_BY_ROLE["no_introspection_source"][2],
            "protocol_sha256": OWNER_BY_ROLE["no_introspection_protocol"][2],
            "contract_sha256": OWNER_BY_ROLE["no_introspection_contract"][2],
            "application_receipt_sha256": OWNER_BY_ROLE["no_introspection_application"][2],
            "target_sha256": BRIDGE_SHA,
            "target_bytes": BRIDGE_BYTES,
            "private_signature_getter_removed": True,
            "capture_clamp_preserved": True,
            "public_native_descriptors_preserved": True,
            "strict_audit": "NOT RERUN; HISTORICAL FAIL-1 PRESERVED",
        },
        "frozen_offline_dual_phase_build": {
            "status": "NOT RUN",
            "label": LABEL,
            "actual_authorization": "ROOT ONLY AFTER ALL THREE OWNERS COMMITTED AND PUSHED",
            "required_commit_equals_pushed_commit": True,
            "phase_names": list(PHASES),
            "independent_phase_count": 2,
            "canonical_source_owners_per_phase": 9,
            "original_runtime_targets_restored_after_actual_build": 5,
            "unchanged_canonical_source_owners_per_phase": 5,
            "exclusive_authenticated_source_overlays_per_phase": 4,
            "combined_engine_overlay_sha256": ENGINE_SHA,
            "combined_engine_overlay_bytes": ENGINE_BYTES,
            "combined_search_overlay_sha256": SEARCH_SHA,
            "combined_search_overlay_bytes": SEARCH_BYTES,
            "safe_no_external_introspection_bridge_overlay_sha256": BRIDGE_SHA,
            "safe_no_external_introspection_bridge_overlay_bytes": BRIDGE_BYTES,
            "corrected_adapter_overlay_sha256": ADAPTER_SHA,
            "corrected_adapter_overlay_bytes": ADAPTER_BYTES,
            "compiler_process_roles_per_phase": list(PROCESS_NAMES),
            "required_actual_compiler_process_count": 28,
            "external_cargo_dependency_count": 0,
            "cargo_flags": ["build", "--release", "--locked", "--offline", "--frozen"],
            "complete_engine_elf_byte_equality_required": True,
            "complete_bridge_elf_byte_equality_required": True,
            "native_symbol_and_dynamic_link_audits_required": True,
            "external_regular_expression_engine": "FORBIDDEN",
            "private_root_mode": "0700",
            "private_source_mode": "0600",
            "native_engine_sha256": NOT_MEASURED,
            "native_bridge_sha256": NOT_MEASURED,
        },
        "physical_source_wall": {
            "policy": "IRREVERSIBLE DENY DEFAULT; EXACT DESCRIPTOR-PINNED OWNERS ONLY",
            "installed_before_first_owner_read": True,
            "retired_v2_proposal_allowed_metadata_probes": 1,
            "retired_v2_proposal_content_opens_by_this_controller": 0,
            "global_v2_unopened_claim": False,
            "candidate_imports_allowed": False,
            "candidate_execution_allowed": False,
            "native_binary_opens_allowed": False,
            "native_library_loads_allowed": False,
            "compiler_processes_allowed": False,
            "clock_access_allowed": False,
            "entropy_or_hidden_case_generation_allowed": False,
            "archive_reads_allowed": False,
            "private_root_access_allowed": False,
            "workspace_mutations_allowed": False,
            "network_access_allowed": False,
            "exact_pinned_dynamic_source_transformer_count": 3,
            "four_required_source_gates": [
                "normal --self-test", "normal --verify-frozen-context",
                "sterile --self-test", "sterile --verify-frozen-context",
            ],
        },
        "source_only_effects": {
            "candidate_imports": 0,
            "candidate_executions": 0,
            "candidate_workers_started": 0,
            "compiler_processes_started": 0,
            "native_binary_files_opened": 0,
            "native_libraries_loaded": 0,
            "compressed_archives_opened": 0,
            "hidden_cases_opened": 0,
            "hidden_cases_generated": 0,
            "retired_holdout_content_open_count_by_this_controller": 0,
            "retired_holdout_metadata_probe_count": 1,
            "clock_samples": 0,
            "network_requests": 0,
            "workspace_mutations": 0,
            "private_roots_created": 0,
            "private_roots_opened": 0,
            "candidate_correctness": NOT_MEASURED,
            "candidate_matching": "NOT RUN",
            "candidate_performance": NOT_MEASURED,
            "candidate_memory": NOT_MEASURED,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_qualified": False,
            "winner_selected": False,
            "final_holdout": FINAL_HOLDOUT_STATUS,
        },
    }


def load_source_context(mode: str, source_pin: str, protocol_pin: str,
                        contract_pin: str | None) -> dict[str, object]:
    clean_imports()
    wall = SourceWall()
    wall.install()
    source_raw, source_info = live_owner(wall, "source", SOURCE, source_pin)
    protocol_raw, protocol_info = live_owner(wall, "protocol", PROTOCOL, protocol_pin)
    require(source_raw.startswith(b"#!/usr/bin/env python3\n")
            and b"SOURCE-ONLY WALL" in protocol_raw
            and FINAL_HOLDOUT_STATUS.encode("ascii") in protocol_raw,
            "authenticate the complete V28 controller and invalidated-final protocol")

    originals: dict[str, bytes] = {}
    for row in STATIC_OWNERS:
        payload, _identity = read_owner(wall, row)
        originals[row[0]] = payload
    anchor = frozen_module(wall, "anchor_transformer", originals["anchor_transformer"])
    compiler = frozen_module(wall, "compiler_transformer", originals["compiler_transformer"])
    combined = frozen_module(wall, "combined_v2_source", originals["combined_v2_source"])
    require(anchor.SCHEMA == "rebar-owned-rust-mandatory-anchor-search-v1"
            and compiler.SCHEMA == "rebar-owned-rust-compiler-allocation-fastpath-v1-source-freeze"
            and combined.SCHEMA == "rebar-first-party-rust-combined-search-compiler-fastpath-v2"
            and callable(anchor.StrictJSON) and callable(anchor.canonical)
            and callable(compiler.derive_source) and callable(compiler.synthetic_semantics)
            and callable(combined.derive_sources) and callable(combined.check_composition),
            "load only the exact three independently frozen source-only transformers")

    history = verify_history(anchor, originals)
    exact_owners = {
        "anchor_lib": originals["anchor_variant_engine"],
        "canonical_lib": originals["original_engine"],
        "canonical_search": originals["original_search"],
        "compiler_variant": originals["compiler_variant_engine"],
        "anchor_search": originals["combined_v2_search"],
    }
    engine, search, composition = combined.derive_sources(
        exact_owners, compiler.__dict__, anchor.__dict__,
    )
    require(engine == originals["combined_v2_engine"]
            and search == originals["combined_v2_search"]
            and digest(engine) == ENGINE_SHA and len(engine) == ENGINE_BYTES
            and digest(search) == SEARCH_SHA and len(search) == SEARCH_BYTES
            and composition.get("replacement_count") == 7
            and composition.get("transformations_commute") is True
            and composition.get("transformation_is_exactly_reversible") is True,
            "independently rederive both exact commuting combined Rust source owners")
    anchor_model = anchor.check_model()
    compiler_model = compiler.synthetic_semantics()
    interaction = combined.check_composition(compiler.__dict__, anchor.__dict__)
    require(anchor_model.get("differential_checks") == 11328
            and anchor_model.get("semantic_pattern_count") == 18
            and compiler_model.get("synthetic_case_count") == 960
            and compiler_model.get("synthetic_source_lifetime_control_count") == 40
            and compiler_model.get("synthetic_distinct_scanner_runtime_flag_case_count") == 42
            and interaction.get("combined_differential_case_count") == 111552,
            "rerun every independent 11328/960/111552 combined source-only semantic proof")
    adapter = derive_adapter(originals["original_adapter"], originals["adapter_repair_source"])
    proposal = retired_metadata(wall)
    frozen = build_contract(source_info, protocol_info, history, proposal,
                            composition, anchor_model, compiler_model)
    if mode != "--render-contract":
        require(type(contract_pin) is str,
                "independently pin the complete frozen V28 machine contract")
        contract_raw, _contract_info = live_owner(wall, "contract", CONTRACT, contract_pin)
        expected = (anchor.canonical(frozen) + "\n").encode("utf-8")
        require(contract_raw == expected
                and public_document(anchor, contract_raw, "complete frozen V28 contract")
                == frozen,
                "reject any altered, incomplete, or noncanonical V28 frozen contract")
    require(not wall.live and wall.proposal_metadata_probes == 1
            and wall.proposal_content_opens == 0,
            "close all source descriptors without reading the invalidated final proposal")
    clean_imports()
    return {"wall": wall, "contract": frozen, "canonical": anchor.canonical,
            "originals": originals, "adapter": adapter}


def hostile_controls(context: dict[str, object]) -> dict[str, object]:
    wall = context["wall"]
    assert isinstance(wall, SourceWall)
    controls: tuple[tuple[str, object], ...] = (
        ("candidate-import", lambda: __import__("candidates.rust_candidate")),
        ("native-installed-engine", lambda: os.open(
            ROOT + "/candidates/_rust_engine.so", os.O_RDONLY | os.O_NOFOLLOW)),
        ("private-root", lambda: os.open(
            "/tmp/rebar-phase2-native-build-v9-rust-v28", os.O_RDONLY | os.O_NOFOLLOW)),
        ("retired-final-content", lambda: os.open(
            ROOT + "/" + RETIRED_PROPOSAL, os.O_RDONLY | os.O_NOFOLLOW)),
        ("retired-final-second-metadata", lambda: os.lstat(ROOT + "/" + RETIRED_PROPOSAL)),
        ("hidden-case", lambda: os.open(
            ROOT + "/oracle/phase3/hidden-case-v28.json", os.O_RDONLY | os.O_NOFOLLOW)),
        ("native-loader", lambda: sys.audit("ctypes.dlopen", "forbidden-v28.so")),
        ("compiler-process", lambda: sys.audit("subprocess.Popen", "cargo", [], None, None)),
        ("candidate-process", lambda: sys.audit("os.posix_spawn", "candidate", [], {})),
        ("network", lambda: sys.audit("socket.connect", object(), object())),
        ("clock", lambda: time.perf_counter_ns()),
        ("entropy", lambda: os.urandom(8)),
        ("inherited-descriptor", lambda: os.read(0, 1)),
        ("direct-metadata", lambda: os.stat(ROOT)),
        ("workspace-write", lambda: os.open(
            ROOT + "/" + SOURCE, os.O_WRONLY | os.O_NOFOLLOW)),
        ("directory-enumeration", lambda: os.listdir(ROOT)),
        ("foreign-code", lambda: compile("1", "forbidden-v28-code", "exec")),
    )
    rejected: list[str] = []
    for label, operation in controls:
        try:
            assert callable(operation)
            operation()
        except BuildFreezeError:
            rejected.append(label)
        else:
            raise BuildFreezeError("an actual hostile source-only control escaped: " + label)
    require(len(rejected) == len(controls) and not wall.live,
            "physically reject every candidate, native, clock, process, and final-case attack")
    # The rejected hostile open is counted separately and does not mean content was read.
    require(wall.proposal_metadata_probes == 1,
            "the invalidated V2 final proposal permits exactly one metadata-only probe")
    return {"schema": SCHEMA + "-source-only-self-test", "version": VERSION,
            "status": "PASS", "hostile_controls_rejected": rejected,
            "hostile_control_count": len(rejected), "blocked_effects": dict(wall.blocked),
            "retired_proposal_content_bytes_read": 0,
            "candidate_imports": 0, "candidate_executions": 0,
            "compiler_processes_started": 0, "native_libraries_loaded": 0,
            "clock_samples": 0, "hidden_cases_generated": 0,
            "workspace_mutations": 0, "final_holdout": FINAL_HOLDOUT_STATUS,
            "frozen_contract": context["contract"]}


def checked_label(value: object) -> str:
    require(type(value) is str and value == LABEL
            and all(character.isascii()
                    and (character.isalnum() or character in "-_") for character in value),
            "caller-pin the one exact genuine V28 actual build label")
    return value


def parse_source(arguments: list[str]) -> tuple[str, str, str, str | None]:
    require(type(arguments) is list and bool(arguments) and arguments[0] in SOURCE_MODES,
            "select one physically isolated V28 source-only gate")
    mode = arguments[0]
    pins: dict[str, str] = {}
    for position in range(1, len(arguments), 2):
        require(position + 1 < len(arguments), "each V28 source-only pin needs a value")
        name, value = arguments[position], arguments[position + 1]
        require(name in ("--source-sha256", "--protocol-sha256", "--contract-sha256")
                and name not in pins, "reject repeated or unknown source-only authority")
        pins[name] = hash_pin(value, name)
    expected = {"--source-sha256", "--protocol-sha256"}
    if mode != "--render-contract":
        expected.add("--contract-sha256")
    require(set(pins) == expected, "independently pin every complete V28 source gate")
    return mode, pins["--source-sha256"], pins["--protocol-sha256"], \
        pins.get("--contract-sha256")


def parse_actual(arguments: list[str]) -> dict[str, object]:
    require(type(arguments) is list and arguments and arguments[0] in ACTUAL_MODES,
            "select one genuine, separately authorized, committed V28 dual build")
    mapping = {
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
        "--frozen-commit": "frozen_commit",
        "--pushed-commit": "pushed_commit",
        "--label": "label",
        "--combined-engine-sha256": "combined_engine_sha256",
        "--combined-engine-bytes": "combined_engine_bytes",
        "--combined-search-sha256": "combined_search_sha256",
        "--combined-search-bytes": "combined_search_bytes",
        "--safe-bridge-sha256": "safe_bridge_sha256",
        "--safe-bridge-bytes": "safe_bridge_bytes",
        "--corrected-adapter-sha256": "corrected_adapter_sha256",
        "--corrected-adapter-bytes": "corrected_adapter_bytes",
        "--combined-v2-contract-sha256": "combined_v2_contract_sha256",
        "--combined-v2-application-sha256": "combined_v2_application_sha256",
        "--no-introspection-contract-sha256": "no_introspection_contract_sha256",
        "--no-introspection-application-sha256": "no_introspection_application_sha256",
        "--v26-publication-sha256": "v26_publication_sha256",
        "--v26-root-sha256": "v26_root_sha256",
        "--v27-publication-sha256": "v27_publication_sha256",
        "--v27-root-sha256": "v27_root_sha256",
        "--v25-failure-sha256": "v25_failure_sha256",
        "--strict-audit-failure-sha256": "strict_audit_failure_sha256",
        "--retired-proposal-sha256": "retired_proposal_sha256",
    }
    result: dict[str, object] = {"mode": arguments[0], "owned_source_sha256": [],
                                 "root_authorized": False,
                                 "frozen_committed_pushed": False}
    position = 1
    while position < len(arguments):
        flag = arguments[position]
        if flag in ("--root-authorized", "--frozen-committed-pushed"):
            name = flag[2:].replace("-", "_")
            require(result[name] is False, "reject duplicate root-only build authorization")
            result[name] = True
            position += 1
            continue
        require(position + 1 < len(arguments), "each exact V28 actual pin requires a value")
        value = arguments[position + 1]
        if flag == "--owned-source-sha256":
            require(type(value) is str, "caller-pin one complete immutable canonical owner")
            assert isinstance(result["owned_source_sha256"], list)
            result["owned_source_sha256"].append(value)
            position += 2
            continue
        require(flag in mapping and mapping[flag] not in result,
                "reject unknown, duplicate, or missing V28 root-build authority")
        name = mapping[flag]
        if name.endswith("_bytes"):
            require(type(value) is str and value.isascii() and value.isdecimal(),
                    "caller-pin each exact private-overlay byte count")
            result[name] = int(value)
        elif name in ("frozen_commit", "pushed_commit"):
            result[name] = commit_pin(value, name)
        elif name == "label":
            result[name] = checked_label(value)
        else:
            result[name] = hash_pin(value, name)
        position += 2
    require(set(result) == set(mapping.values())
            | {"mode", "owned_source_sha256", "root_authorized", "frozen_committed_pushed"},
            "root must caller-pin every independent V28 input before any compiler starts")
    require(result["root_authorized"] is True
            and result["frozen_committed_pushed"] is True
            and result["frozen_commit"] == result["pushed_commit"],
            "root may build only the exact fully committed and pushed V28 freeze")
    expected = {
        "combined_engine_sha256": ENGINE_SHA, "combined_engine_bytes": ENGINE_BYTES,
        "combined_search_sha256": SEARCH_SHA, "combined_search_bytes": SEARCH_BYTES,
        "safe_bridge_sha256": BRIDGE_SHA, "safe_bridge_bytes": BRIDGE_BYTES,
        "corrected_adapter_sha256": ADAPTER_SHA, "corrected_adapter_bytes": ADAPTER_BYTES,
        "combined_v2_contract_sha256": OWNER_BY_ROLE["combined_v2_contract"][2],
        "combined_v2_application_sha256": OWNER_BY_ROLE["combined_v2_application"][2],
        "no_introspection_contract_sha256": OWNER_BY_ROLE["no_introspection_contract"][2],
        "no_introspection_application_sha256": OWNER_BY_ROLE["no_introspection_application"][2],
        "v26_publication_sha256": OWNER_BY_ROLE["v26_build_publication"][2],
        "v26_root_sha256": OWNER_BY_ROLE["v26_build_root"][2],
        "v27_publication_sha256": OWNER_BY_ROLE["v27_build_publication"][2],
        "v27_root_sha256": OWNER_BY_ROLE["v27_build_root"][2],
        "v25_failure_sha256": OWNER_BY_ROLE["v25_full_failure"][2],
        "strict_audit_failure_sha256": OWNER_BY_ROLE["strict_audit_failure"][2],
        "retired_proposal_sha256": RETIRED_PROPOSAL_SHA,
        "label": LABEL,
    }
    for name, value in expected.items():
        require(result.get(name) == value, "reject substituted V28 actual authority: " + name)
    provided = result["owned_source_sha256"]
    genuine = {row[1] + "=" + row[2] for row in CANONICAL_OWNERS}
    require(type(provided) is list and len(provided) == 9
            and len(set(provided)) == 9 and set(provided) == genuine,
            "independently caller-pin all nine complete canonical Rust source owners")
    return result


def read_actual_owner(row: tuple[object, ...]) -> tuple[bytes, dict[str, object]]:
    role, relative, expected, count, inode = row
    descriptor = os.open(ROOT + "/" + str(relative),
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == count and before.st_uid == os.geteuid()
                and before.st_nlink == 1,
                "reject a substituted exact actual-build owner: " + str(role))
        chunks: list[bytes] = []
        remaining = int(count)
        while remaining:
            chunk = os.read(descriptor, min(65536, remaining))
            require(bool(chunk), "reject a truncated authenticated actual source owner")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "reject an expanded actual source owner")
        after = os.fstat(descriptor)
        require(all(getattr(before, key) == getattr(after, key)
                    for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                "st_mtime_ns", "st_ctime_ns")),
                "reject an actual source owner changed during descriptor authentication")
        payload = b"".join(chunks)
        require(digest(payload) == expected, "reject changed complete actual source bytes")
        return payload, {"role": role, "path": relative, "sha256": expected,
                         "bytes": count, "device": before.st_dev,
                         "inode": before.st_ino, "mode": "0600", "nlink": 1,
                         "uid": before.st_uid}
    finally:
        os.close(descriptor)


def actual_self(relative: str, pin: str) -> tuple[bytes, dict[str, object]]:
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode)
                and stat.S_IMODE(identity.st_mode) == 0o600
                and identity.st_dev == DEVICE and identity.st_uid == os.geteuid()
                and identity.st_nlink == 1 and 0 < identity.st_size <= MAX_OWNER_BYTES,
                "reject a substituted actual V28 frozen owner")
        raw = b""
        while len(raw) < identity.st_size:
            part = os.read(descriptor, min(65536, identity.st_size - len(raw)))
            require(bool(part), "a caller-pinned actual V28 owner ended early")
            raw += part
        require(os.read(descriptor, 1) == b"" and digest(raw) == pin,
                "reject an incomplete or substituted root-authorized V28 owner")
        return raw, {"path": relative, "sha256": pin, "bytes": identity.st_size,
                     "device": identity.st_dev, "inode": identity.st_ino,
                     "mode": "0600", "uid": identity.st_uid, "nlink": identity.st_nlink}
    finally:
        os.close(descriptor)


def snapshot_actual_runtime_targets() -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for role, relative, expected, size, inode, mode in ACTUAL_RUNTIME_TARGETS:
        descriptor = os.open(ROOT + "/" + relative,
                             os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
        try:
            before = os.fstat(descriptor)
            require(stat.S_ISREG(before.st_mode)
                    and stat.S_IMODE(before.st_mode) == mode
                    and before.st_dev == DEVICE and before.st_ino == inode
                    and before.st_size == size and before.st_uid == os.geteuid()
                    and before.st_nlink == 1,
                    "reject a substituted original runtime target: " + role)
            hashed = hashlib.sha256()
            remaining = size
            while remaining:
                part = os.read(descriptor, min(remaining, 65536))
                require(bool(part), "an original runtime target ended early: " + role)
                hashed.update(part)
                remaining -= len(part)
            require(os.read(descriptor, 1) == b"" and hashed.hexdigest() == expected,
                    "authenticate every complete unchanged original runtime target")
            after = os.fstat(descriptor)
            require(all(getattr(before, key) == getattr(after, key)
                        for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                    "st_mtime_ns", "st_ctime_ns")),
                    "an original runtime target changed during actual authentication")
            result[role] = {"path": relative, "sha256": expected, "bytes": size,
                            "device": before.st_dev, "inode": before.st_ino,
                            "mode": "0755" if mode == 0o755 else "0600",
                            "uid": before.st_uid, "nlink": before.st_nlink,
                            "mtime_ns": before.st_mtime_ns,
                            "ctime_ns": before.st_ctime_ns}
        finally:
            os.close(descriptor)
    require(len(result) == 5,
            "preserve the original engine, bridge, adapter, and both installed native files")
    return result


def actual_evidence_names(label: str, failed: bool) -> tuple[str, str]:
    stem = "native-source-build-v28-rust-" + checked_label(label)
    if failed:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def actual_root_receipt_name(label: str) -> str:
    return "native-source-build-v28-rust-" + checked_label(label) \
        + "-root-provenance-receipt.json"


def actual_module(role: str, payload: bytes, name: str) -> types.ModuleType:
    owner = OWNER_BY_ROLE[role]
    require(digest(payload) == owner[2] and len(payload) == owner[3]
            and name not in sys.modules,
            "execute only complete independently authenticated actual build kernels")
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + owner[1]
    sys.modules[name] = module
    try:
        exec(compile(payload, module.__file__, "exec", dont_inherit=True), module.__dict__)
        return module
    except BaseException:
        sys.modules.pop(name, None)
        raise


def copy_four_overlays(module: types.ModuleType, workdir: str, family: str,
                       phase: str, originals: dict[str, bytes]) -> dict[str, object]:
    require(module._ACTIVE is not None,
            "require the genuine root-authorized V28 28-process native build kernel")
    state = module._ACTIVE
    kernel = state["kernel"]
    low_level = state["v9"]
    expected_paths = {owner.path for owner in module.RUST_OWNERS}
    require(family == FAMILY and phase in PHASES and set(originals) == expected_paths
            and (workdir, phase) not in module._APPLIED_PHASES,
            "require exactly nine immutable first-party owners in a fresh V28 phase")
    paths = low_level.phase_paths(workdir, family, phase)
    overlays = {
        "candidates/rust/src/lib.rs": (state["combined_engine"], ENGINE_SHA,
                                         ENGINE_BYTES, "combined-search-and-parser-engine"),
        "candidates/rust/src/search.rs": (state["combined_search"], SEARCH_SHA,
                                            SEARCH_BYTES, "combined-mandatory-anchor-search"),
        module.BRIDGE_PATH: (state["combined_bridge"], BRIDGE_SHA,
                             BRIDGE_BYTES, "no-external-introspection-safe-bridge"),
        module.PUBLIC_PATH: (state["corrected_adapter"], ADAPTER_SHA,
                             ADAPTER_BYTES, "corrected-first-party-public-adapter"),
    }
    rows: dict[str, object] = {}
    for original in sorted(module.RUST_OWNERS, key=lambda row: row.path):
        raw = originals[original.path]
        require(type(raw) is bytes and digest(raw) == original.sha256
                and len(raw) == original.size,
                "preserve every exact original immutable first-party Rust owner")
        if original.path in overlays:
            continue
        target = paths["source"] / original.path
        kernel.mkdir_private(target.parent)
        item = kernel.write_fresh(target, raw, synchronize=False)
        item["path"] = low_level.sanitized(item["path"], workdir, family)
        rows[original.path] = item
    require(len(rows) == 5,
            "preserve five unchanged canonical owners in each private source phase")
    for path, (payload, expected_sha, expected_bytes, role) in overlays.items():
        require(type(payload) is bytes and digest(payload) == expected_sha
                and len(payload) == expected_bytes,
                "authenticate one exact complete first-party private V28 overlay")
        if path in ("candidates/rust/src/lib.rs", "candidates/rust/src/search.rs"):
            audit = kernel.audit_native_source(payload, family=FAMILY, location=path)
            require(type(audit) is dict and audit.get("external_regex_dependency_count") == 0
                    and audit.get("cross_family_dependency_count") == 0,
                    "reject a delegated, borrowed, or external Rust matching engine")
        if path == module.BRIDGE_PATH:
            require(b"rust_bound_get_signature" not in payload
                    and b'PyImport_ImportModule("inspect")' not in payload,
                    "never silently reinstall the historical private-getter audit failure")
        target = paths["source"] / path
        kernel.mkdir_private(target.parent)
        saved = kernel.write_fresh(target, payload, synchronize=True)
        verified, reread = kernel.authenticate_file(
            target, expected=expected_sha, maximum=MAX_OWNER_BYTES,
            exact_size=expected_bytes, capture=True,
        )
        require(type(reread) is bytes and reread == payload
                and saved.get("sha256") == expected_sha
                and saved.get("bytes") == expected_bytes
                and saved.get("device") == verified.get("device")
                and saved.get("inode") == verified.get("inode")
                and saved.get("exclusive_creation") is True
                and saved.get("file_fsync_completed") is True
                and stat.S_IMODE(os.lstat(target).st_mode) == 0o600,
                "exclusively create, synchronize, and reread one genuine private overlay")
        rows[path] = {
            "path": low_level.sanitized(verified["path"], workdir, family),
            "sha256": verified["sha256"], "bytes": verified["size_bytes"],
            "device": verified["device"], "inode": verified["inode"],
            "exclusive_creation": True, "same_inode_readback_verified": True,
            "file_fsync_completed": True,
            "source_overlay": {"status": "PASS", "phase": phase, "role": role,
                               "source_apply_count": 1, "derived_sha256": expected_sha,
                               "derived_source_sha256": expected_sha,
                               "derived_bytes": expected_bytes,
                               "derived_source_bytes": expected_bytes,
                               "candidate_original_modified": False,
                               "canonical_candidate_modified": False},
        }
    require(set(rows) == expected_paths,
            "close one independent five-original, four-overlay Rust source phase")
    for row in CANONICAL_OWNERS:
        read_actual_owner(row)
    module._APPLIED_PHASES.add((workdir, phase))
    return rows


def run_actual(options: dict[str, object]) -> dict[str, object]:
    require(options.get("root_authorized") is True
            and options.get("frozen_committed_pushed") is True
            and options.get("frozen_commit") == options.get("pushed_commit")
            and options.get("label") == LABEL,
            "only root may run the separately committed and pushed complete V28 build")
    runtime_before = snapshot_actual_runtime_targets()
    source_raw, source_info = actual_self(SOURCE, str(options["source_sha256"]))
    protocol_raw, protocol_info = actual_self(PROTOCOL, str(options["protocol_sha256"]))
    contract_raw, contract_info = actual_self(CONTRACT, str(options["contract_sha256"]))
    require(source_raw.startswith(b"#!/usr/bin/env python3\n")
            and FINAL_HOLDOUT_STATUS.encode("ascii") in protocol_raw
            and FINAL_HOLDOUT_STATUS.encode("ascii") in contract_raw,
            "require the exact complete invalidated-final V28 source freeze")
    raw: dict[str, bytes] = {}
    identities: dict[str, dict[str, object]] = {}
    for row in STATIC_OWNERS:
        payload, identity = read_actual_owner(row)
        raw[row[0]] = payload
        identities[row[0]] = identity
    canonical_before = {row[1]: identities[row[0]] for row in CANONICAL_OWNERS}
    require(len(canonical_before) == 9, "authenticate all nine immutable original owners")
    adapter = derive_adapter(raw["original_adapter"], raw["adapter_repair_source"])

    # Actual mode deliberately loads only the already pinned operational kernel.
    # Its authenticated V9/V7/V4 descendants perform the complete native ELF audit.
    kernel_name = "_rebar_v28_authenticated_actual_v16_native_kernel"
    module = actual_module("actual_v16_kernel", raw["actual_v16_kernel"], kernel_name)
    require(module.SCHEMA == "rebar-phase2-owned-rust-buffer-shape-source-build-v16"
            and module.VERSION == 16 and module.FAMILY == FAMILY
            and module.PHASES == PHASES and module.PROCESS_NAMES == PROCESS_NAMES
            and callable(module.run_build) and callable(module.verify_reproduced_phases),
            "reject a dummy, delegated, or substituted first-party 28-process build kernel")
    frozen = module.json.loads(contract_raw)
    require(type(frozen) is dict and frozen.get("schema") == SCHEMA + "-source-freeze"
            and frozen.get("final_holdout") == FINAL_HOLDOUT_STATUS
            and frozen.get("source", {}).get("sha256") == options["source_sha256"]
            and frozen.get("protocol", {}).get("sha256") == options["protocol_sha256"]
            and frozen.get("candidate_sources", {}).get("combined_engine", {})
                .get("sha256") == ENGINE_SHA
            and frozen.get("candidate_sources", {}).get("combined_search", {})
                .get("sha256") == SEARCH_SHA
            and frozen.get("candidate_sources", {}).get("no_external_introspection_bridge", {})
                .get("sha256") == BRIDGE_SHA,
            "authenticate the exact canonical V28 source contract before actual compilation")

    module.SCHEMA = SCHEMA
    module.VERSION = VERSION
    module.SOURCE_PATH = SOURCE
    module.PROTOCOL_PATH = PROTOCOL
    module.CONTRACT_PATH = CONTRACT
    module.COMBINED_VARIANT = module.Owner(
        OWNER_BY_ROLE["no_introspection_bridge"][1], BRIDGE_SHA, BRIDGE_BYTES,
    )
    module.BUFFER_VARIANT = module.COMBINED_VARIANT
    module.checked_label = checked_label
    module.evidence_names = actual_evidence_names
    captures: dict[str, object] = {}

    def context(source_pin: str, protocol_pin: str,
                contract_pin: str) -> tuple[dict[str, object], dict[str, object]]:
        require((source_pin, protocol_pin, contract_pin)
                == (options["source_sha256"], options["protocol_sha256"],
                    options["contract_sha256"]),
                "reject substituted or incomplete actual V28 triple authority")
        return {"schema": SCHEMA + "-verified-actual-context", "status": "PASS",
                "family": FAMILY, "source": source_info, "protocol": protocol_info,
                "contract": contract_info, "final_holdout": FINAL_HOLDOUT_STATUS}, {
                    "originals": {row[1]: raw[row[0]] for row in CANONICAL_OWNERS},
                    "combined_bridge": raw["no_introspection_bridge"],
                    "corrected_adapter": adapter,
                    "low_level_v9_source": raw["actual_v9_kernel"],
                    "combined_engine": raw["combined_v2_engine"],
                    "combined_search": raw["combined_v2_search"],
                }

    original_expected = module.expected_source_owner

    def expected(path: str) -> tuple[str, int]:
        if path == "candidates/rust/src/lib.rs":
            return ENGINE_SHA, ENGINE_BYTES
        if path == "candidates/rust/src/search.rs":
            return SEARCH_SHA, SEARCH_BYTES
        return original_expected(path)

    previous_verify = module.verify_reproduced_phases

    def verify(low_level: types.ModuleType, native: types.ModuleType, workdir: str,
               phases: list[dict[str, object]],
               operations: list[dict[str, object]]) -> dict[str, object]:
        require(type(operations) is list and len(operations) == 28
                and not captures, "require 28 distinct real successful V28 process roles")
        proof = previous_verify(low_level, native, workdir, phases, operations)
        require(proof.get("status") == "PASS"
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
                "require two actual independent byte-identical engine and safe bridge ELFs")
        phase_owners: list[dict[str, object]] = []
        all_inodes: set[tuple[int, int]] = set()
        pids: set[int] = set()
        for index, operation in enumerate(operations):
            require(operation.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                    and type(operation.get("pid")) is int
                    and operation["pid"] not in pids
                    and operation.get("exit_status") == 0,
                    "require every compiler and native-symbol inspection role exactly once")
            pids.add(operation["pid"])
        for index, phase in enumerate(phases):
            require(phase.get("name") == PHASES[index],
                    "preserve both ordered independently owned private source phases")
            owners = phase.get("fresh_source_owners")
            require(type(owners) is dict and len(owners) == 9,
                    "require nine independent source owners in each actual V28 phase")
            for path, owner in owners.items():
                require(type(owner) is dict and type(owner.get("device")) is int
                        and type(owner.get("inode")) is int
                        and (owner["device"], owner["inode"]) not in all_inodes,
                        "no private source may be borrowed or hard-linked across phases")
                all_inodes.add((owner["device"], owner["inode"]))
            for path, expected_sha, expected_bytes in (
                ("candidates/rust/src/lib.rs", ENGINE_SHA, ENGINE_BYTES),
                ("candidates/rust/src/search.rs", SEARCH_SHA, SEARCH_BYTES),
                (module.BRIDGE_PATH, BRIDGE_SHA, BRIDGE_BYTES),
                (module.PUBLIC_PATH, ADAPTER_SHA, ADAPTER_BYTES),
            ):
                item = owners.get(path)
                overlay = item.get("source_overlay") if type(item) is dict else None
                require(type(overlay) is dict and overlay.get("status") == "PASS"
                        and overlay.get("phase") == PHASES[index]
                        and overlay.get("source_apply_count") == 1
                        and overlay.get("derived_sha256") == expected_sha
                        and overlay.get("derived_bytes") == expected_bytes,
                        "prove every authentic independently applied private source overlay")
            phase_owners.append({"phase": PHASES[index], "owners": dict(owners)})
        require(len(all_inodes) == 18 and len(pids) == 28,
                "require 18 genuine private source identities and 28 real process identities")
        root = os.lstat(workdir)
        require(stat.S_ISDIR(root.st_mode) and stat.S_IMODE(root.st_mode) == 0o700
                and root.st_uid == os.geteuid()
                and workdir.startswith("/tmp/rebar-phase2-native-build-v9-rust-"),
                "preserve one actual fresh owner-only retained private V28 build root")
        proof.update({"unchanged_source_owners_per_phase": 5,
                      "combined_engine_overlay_count": 2,
                      "combined_search_overlay_count": 2,
                      "safe_no_external_introspection_bridge_overlay_count": 2,
                      "corrected_public_adapter_overlay_count": 2,
                      "total_private_source_overlay_apply_count": 8,
                      "distinct_private_source_identity_count": 18,
                      "final_holdout": FINAL_HOLDOUT_STATUS})
        captures.update({"root": {"path": workdir, "device": root.st_dev,
                                   "inode": root.st_ino, "mode": "0700",
                                   "uid": root.st_uid, "phase_count": 2},
                         "process_ids": sorted(pids), "private_source_owners": phase_owners,
                         "native_outputs": proof["native_outputs"]})
        return proof

    def publish(kernel: types.ModuleType,
                report: dict[str, object]) -> dict[str, object]:
        require(report.get("status") in ("PASS", "FAIL")
                and report.get("family") == FAMILY and report.get("label") == LABEL,
                "publish only one complete genuine root-authorized V28 build outcome")
        complete = dict(report)
        complete.update({
            "schema": SCHEMA + "-actual-combined-dual-source-build",
            "version": VERSION,
            "frozen_commit": options["frozen_commit"],
            "pushed_commit": options["pushed_commit"],
            "combined_engine_sha256": ENGINE_SHA,
            "combined_engine_bytes": ENGINE_BYTES,
            "combined_search_sha256": SEARCH_SHA,
            "combined_search_bytes": SEARCH_BYTES,
            "safe_no_external_introspection_bridge_sha256": BRIDGE_SHA,
            "safe_no_external_introspection_bridge_bytes": BRIDGE_BYTES,
            "corrected_public_adapter_sha256": ADAPTER_SHA,
            "corrected_public_adapter_bytes": ADAPTER_BYTES,
            "latest_v25_candidate_status": "FAIL",
            "latest_v25_semantic_mismatch_count": 1352,
            "latest_v25_verified_passing_case_count": 15877,
            "latest_v25_original_case_execution_denominator": 31237,
            "latest_v25_completed_suite_count": 13,
            "strict_audit_status": "FAIL; HISTORICAL PRIVATE GETTER PRESENT",
            "strict_audit_finding_count": 1,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "historical_v26_publication_receipt_sha256":
                OWNER_BY_ROLE["v26_build_publication"][2],
            "historical_v26_root_receipt_sha256": OWNER_BY_ROLE["v26_build_root"][2],
            "historical_v27_publication_receipt_sha256":
                OWNER_BY_ROLE["v27_build_publication"][2],
            "historical_v27_root_receipt_sha256": OWNER_BY_ROLE["v27_build_root"][2],
            "hidden_cases_read": 0,
            "hidden_cases_generated": 0,
            "retired_v2_holdout_content_opened_by_this_controller": False,
            "retired_v2_holdout_global_unopened_claim": False,
            "historical_retired_v2_proposal_case_count": RETIRED_PROPOSAL_CASE_COUNT,
            "final_holdout": FINAL_HOLDOUT_STATUS,
            "holdout": FINAL_HOLDOUT_STATUS,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False,
            "winner_selected": False,
        })
        archive_name, receipt_name = actual_evidence_names(
            LABEL, complete["status"] == "FAIL",
        )
        directory = module.ROOT / module.EVIDENCE_PATH
        plain = module.canonical(complete)
        compressed = module.gzip.compress(plain, compresslevel=9, mtime=0)
        archived = kernel.write_fresh(directory / archive_name, compressed,
                                      synchronize=True)
        archive_sync = kernel.fsync_directory(directory)
        receipt = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "version": VERSION, "status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "build_status": complete["status"], "family": FAMILY, "label": LABEL,
            "source_sha256": options["source_sha256"],
            "protocol_sha256": options["protocol_sha256"],
            "contract_sha256": options["contract_sha256"],
            "frozen_commit": options["frozen_commit"],
            "pushed_commit": options["pushed_commit"],
            "archive_relative": module.EVIDENCE_PATH + "/" + archive_name,
            "archive_sha256": archived["sha256"], "archive_bytes": archived["bytes"],
            "archive_directory_fsync": archive_sync,
            "uncompressed_sha256": digest(plain), "uncompressed_bytes": len(plain),
            "actual_compiler_process_count": complete.get("actual_compiler_process_count", 0),
            "actual_completed_phase_count": complete.get("phase_count", 0),
            "external_cargo_dependency_count": 0,
            "combined_engine_source_sha256": ENGINE_SHA,
            "combined_engine_source_bytes": ENGINE_BYTES,
            "combined_search_source_sha256": SEARCH_SHA,
            "combined_search_source_bytes": SEARCH_BYTES,
            "safe_no_external_introspection_bridge_sha256": BRIDGE_SHA,
            "safe_no_external_introspection_bridge_bytes": BRIDGE_BYTES,
            "corrected_public_adapter_sha256": ADAPTER_SHA,
            "corrected_public_adapter_bytes": ADAPTER_BYTES,
            "latest_v25_candidate_status": "FAIL",
            "latest_v25_semantic_mismatch_count": 1352,
            "latest_v25_original_case_execution_denominator": 31237,
            "strict_audit_status": "FAIL; HISTORICAL PRIVATE GETTER PRESENT",
            "strict_audit_finding_count": 1,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "historical_retired_v2_proposal_case_count": RETIRED_PROPOSAL_CASE_COUNT,
            "retired_v2_holdout_global_unopened_claim": False,
            "candidate_matching": "NOT RUN", "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False, "winner_selected": False,
            "hidden_cases_generated": 0,
            "final_holdout": FINAL_HOLDOUT_STATUS, "holdout": FINAL_HOLDOUT_STATUS,
        }
        receipt_raw = module.canonical(receipt)
        saved = kernel.write_fresh(directory / receipt_name, receipt_raw,
                                   synchronize=True)
        kernel.fsync_directory(directory)
        result: dict[str, object] = {
            "schema": SCHEMA + "-published-actual-build",
            "status": complete["status"], "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "family": FAMILY, "label": LABEL,
            "archive_relative": module.EVIDENCE_PATH + "/" + archive_name,
            "archive_sha256": archived["sha256"],
            "receipt_relative": module.EVIDENCE_PATH + "/" + receipt_name,
            "receipt_sha256": saved["sha256"],
            "failure_preserved": complete["status"] == "FAIL",
            "candidate_matching": "NOT RUN", "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False,
            "final_holdout": FINAL_HOLDOUT_STATUS, "winner_selected": False,
        }
        if complete["status"] != "PASS":
            return result
        require(captures and len(captures["process_ids"]) == 28,
                "publish private-root provenance only after both real native phases pass")
        canonical_after = {row[1]: read_actual_owner(row)[1] for row in CANONICAL_OWNERS}
        runtime_after = snapshot_actual_runtime_targets()
        require(canonical_before == canonical_after,
                "preserve all nine exact canonical Rust owner identities")
        require(runtime_before == runtime_after,
                "preserve every original source, adapter, and installed native identity")
        root_receipt = {
            "schema": SCHEMA + "-durable-root-provenance-receipt",
            "version": VERSION, "status": "PASS", "family": FAMILY, "label": LABEL,
            "source_sha256": options["source_sha256"],
            "protocol_sha256": options["protocol_sha256"],
            "contract_sha256": options["contract_sha256"],
            "canonical_build_status": "PASS",
            "canonical_build_receipt_relative": result["receipt_relative"],
            "canonical_build_receipt_sha256": result["receipt_sha256"],
            "root": captures["root"],
            "actual_compiler_process_count": 28,
            "actual_compiler_process_ids": captures["process_ids"],
            "actual_source_phase_count": 2,
            "actual_private_source_owners": captures["private_source_owners"],
            "actual_reproduced_native_outputs": captures["native_outputs"],
            "cross_phase_complete_engine_elf_byte_identical": True,
            "cross_phase_complete_bridge_elf_byte_identical": True,
            "distinct_private_source_identity_count": 18,
            "unchanged_canonical_source_owners_per_phase": 5,
            "combined_engine_overlay_apply_count": 2,
            "combined_search_overlay_apply_count": 2,
            "safe_no_external_introspection_bridge_overlay_apply_count": 2,
            "corrected_adapter_overlay_apply_count": 2,
            "total_private_source_overlay_apply_count": 8,
            "combined_engine_source_sha256": ENGINE_SHA,
            "combined_engine_source_bytes": ENGINE_BYTES,
            "combined_search_source_sha256": SEARCH_SHA,
            "combined_search_source_bytes": SEARCH_BYTES,
            "safe_no_external_introspection_bridge_sha256": BRIDGE_SHA,
            "safe_no_external_introspection_bridge_bytes": BRIDGE_BYTES,
            "corrected_public_adapter_sha256": ADAPTER_SHA,
            "corrected_public_adapter_bytes": ADAPTER_BYTES,
            "all_original_source_identities_restored": True,
            "all_original_runtime_target_identities_restored": True,
            "actual_original_runtime_target_count": 5,
            "actual_original_runtime_targets_before": runtime_before,
            "actual_original_runtime_targets_after": runtime_after,
            "actual_original_source_identities_before": canonical_before,
            "actual_original_source_identities_after": canonical_after,
            "latest_v25_candidate_status": "FAIL",
            "latest_v25_semantic_mismatch_count": 1352,
            "latest_v25_original_case_execution_denominator": 31237,
            "strict_audit_status": "FAIL; HISTORICAL PRIVATE GETTER PRESENT",
            "strict_audit_finding_count": 1,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "historical_retired_v2_proposal_case_count": RETIRED_PROPOSAL_CASE_COUNT,
            "retired_v2_holdout_global_unopened_claim": False,
            "hidden_cases_generated": 0,
            "candidate_matching": "NOT RUN", "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False, "winner_selected": False,
            "final_holdout": FINAL_HOLDOUT_STATUS, "holdout": FINAL_HOLDOUT_STATUS,
        }
        root_name = actual_root_receipt_name(LABEL)
        root_raw = module.canonical(root_receipt)
        published_root = kernel.write_fresh(directory / root_name, root_raw,
                                             synchronize=True)
        kernel.fsync_directory(directory)
        result.update({"root_provenance_status": "PASS",
                       "root_receipt_relative": module.EVIDENCE_PATH + "/" + root_name,
                       "root_receipt_sha256": published_root["sha256"],
                       "actual_compiler_process_count": 28,
                       "actual_source_phase_count": 2,
                       "cross_phase_complete_engine_elf_byte_identical": True,
                       "cross_phase_complete_bridge_elf_byte_identical": True})
        return result

    module.verify_frozen_context = context
    module.expected_source_owner = expected
    module.copy_combined_snapshot = lambda workdir, family, phase, originals: (
        copy_four_overlays(module, workdir, family, phase, originals)
    )
    module.verify_reproduced_phases = verify
    module.publish_build_report = publish

    class ActualOptions:
        pass

    forwarded = ActualOptions()
    for name in ("source_sha256", "protocol_sha256", "contract_sha256", "label",
                 "owned_source_sha256", "corrected_adapter_sha256",
                 "corrected_adapter_bytes"):
        setattr(forwarded, name, options[name])
    forwarded.combined_bridge_sha256 = BRIDGE_SHA
    forwarded.combined_bridge_bytes = BRIDGE_BYTES
    result = module.run_build(forwarded)
    require(type(result) is dict and result.get("family") == FAMILY,
            "publish exactly one genuine V28 first-party native build outcome")
    canonical_after = {row[1]: read_actual_owner(row)[1] for row in CANONICAL_OWNERS}
    require(canonical_before == canonical_after
            and runtime_before == snapshot_actual_runtime_targets(),
            "restore all nine canonical sources and all five original runtime targets")
    # Keep the authenticated operational module until main emits canonical
    # bytes.  Re-executing a source-only transformer after subprocess/json
    # imports would correctly trip its clean-matcher precondition.
    return result


def main(arguments: list[str]) -> int:
    try:
        require(sys.executable == PYTHON and sys.version_info[:3] == (3, 14, 6)
                and sys.flags.isolated == 1 and sys.flags.no_site == 1
                and sys.flags.dont_write_bytecode == 1,
                "use only the pinned CPython 3.14.6 with -I -B -S")
        require(type(arguments) is list and bool(arguments),
                "select one source-only V28 gate or one actual root-authorized build")
        if arguments[0] in ACTUAL_MODES:
            result = run_actual(parse_actual(arguments))
            # The actual authenticated operational kernel owns canonical JSON.
            module = sys.modules.get("_rebar_v28_authenticated_actual_v16_native_kernel")
            if type(module) is types.ModuleType and callable(module.canonical):
                output = module.canonical(result)
                sys.stdout.buffer.write(output)
                sys.stdout.flush()
                return 0
            # run_actual removes its temporary module; encode with a pinned prior transformer.
            source, _ = read_actual_owner(OWNER_BY_ROLE["anchor_transformer"])
            encoder = actual_module("anchor_transformer", source,
                                    "_rebar_v28_actual_canonical_encoder")
            sys.stdout.write(encoder.canonical(result) + "\n")
            sys.stdout.flush()
            return 0
        mode, source_pin, protocol_pin, contract_pin = parse_source(arguments)
        context = load_source_context(mode, source_pin, protocol_pin, contract_pin)
        canonical = context["canonical"]
        assert callable(canonical)
        if mode == "--render-contract":
            value = context["contract"]
        elif mode == "--self-test":
            value = hostile_controls(context)
        else:
            value = {"schema": SCHEMA + "-verified-source-only-context",
                     "version": VERSION, "status": "PASS",
                     "source_sha256": source_pin, "protocol_sha256": protocol_pin,
                     "contract_sha256": contract_pin,
                     "candidate_executions": 0, "candidate_imports": 0,
                     "compiler_processes_started": 0, "native_libraries_loaded": 0,
                     "clock_samples": 0, "hidden_cases_generated": 0,
                     "retired_holdout_content_bytes_read": 0,
                     "workspace_mutations": 0,
                     "final_holdout": FINAL_HOLDOUT_STATUS,
                     "frozen_contract": context["contract"]}
        sys.stdout.write(canonical(value) + "\n")
        sys.stdout.flush()
        return 0
    except BaseException as error:
        try:
            sys.stderr.write("V28 combined first-party source build FAILED: "
                             + type(error).__name__ + ": " + str(error)[:8192] + "\n")
            sys.stderr.flush()
        except BaseException:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
