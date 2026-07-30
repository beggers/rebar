#!/usr/bin/env python3
"""Freeze and independently reproduce the first-party Rust VM workspace.

The three source modes install an irreversible, deny-default wall before any
predecessor is read.  Their only final-proposal contact is one metadata probe;
that historical proposal is explicitly invalidated and cannot qualify a final
comparison.  Only an independently pinned, pushed, root-authorized actual mode
may create two private offline source trees and publish genuine build receipts.
No mode runs, imports, or loads a candidate.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("a first-party source-build controller must not load a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time
import types


ROOT = "/home/dev-user/src/rebar"
DEVICE = 2064
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SOURCE = "tools/reproduce_owned_rust_workspace_source_build_v29.py"
PROTOCOL = "oracle/phase2/RUST-WORKSPACE-SOURCE-BUILD-V29.md"
CONTRACT = "oracle/phase2/rust-workspace-source-build-v29.json"
SCHEMA = "rebar-phase2-owned-rust-workspace-source-build-v29"
VERSION = 29
FAMILY = "rust"
NOT_MEASURED = "NOT MEASURED"
FINAL_HOLDOUT_STATUS = "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
LABEL = "phase2-v29-rust-vm-workspace-root-provenance"
MAX_OWNER_BYTES = 1_048_576
MAX_PROCESS_OUTPUT_BYTES = 8_388_608
ROOT_PREFIX = "rebar-phase2-native-build-v29-rust-"
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)
GOAL_SHA = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
WORKSPACE_SHA = "0bd199957ed96cbf67109d4621698a6be300cb5c88d0ae30d25402f51777ba36"
WORKSPACE_BYTES = 178647
CANONICAL_LIB_SHA = "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d"
CANONICAL_SEARCH_SHA = "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe"
CORRECTED_BRIDGE_SHA = "2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7"
CORRECTED_BRIDGE_BYTES = 177146
CAPTURE_BRIDGE_SHA = "a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54"
CAPTURE_BRIDGE_BYTES = 178805
CORRECTED_ADAPTER_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
CORRECTED_ADAPTER_BYTES = 31934
V25_PUBLICATION_SHA = "55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc"
V25_ROOT_SHA = "e8633ac1224235db9f8ea48c683c833fba3015cd73f071cd2488fa0b13a117a2"
V25_FAILURE_SHA = "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59"
V26_PUBLICATION_SHA = "8a0e9d70dab2a3e1f3738d6e0e1a4716b78e0a1b329ce3b16010bd94b6598cd6"
V26_ROOT_SHA = "aaed35f9fe86090d75ce2162bae7902910461a7b4e731c22eba275406f328ba1"
V27_PUBLICATION_SHA = "7fcbe3e07885f2a488ed1b3c79bc02888ad22dd2b21179081b3cecfc7b464c99"
V27_ROOT_SHA = "c6958056757ab6145d613490db1a21165714dcb89c61e6d3bdf52500fad221b0"
AUDIT_FAILURE_SHA = "c3020fe067ad06c2bf7309a73b960884572addd9e984d01d2cf27d5cd9d61f19"
HISTORICAL_PROPOSAL = "oracle/phase3/expanded-sealed-holdout-v2.json"
HISTORICAL_PROPOSAL_SHA = "5d9fa3920c1dcabc92a3521d742cd10ec399cff1a979b71ac079daba6f92cba0"
HISTORICAL_PROPOSAL_BYTES = 15561
HISTORICAL_PROPOSAL_INODE = 525920
HISTORICAL_PROPOSAL_CASES = 141557760
RUST_TOOLCHAIN = "/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu"
RUSTC = RUST_TOOLCHAIN + "/bin/rustc"
CARGO = RUST_TOOLCHAIN + "/bin/cargo"
GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
READELF = "/usr/bin/x86_64-linux-gnu-readelf"
PYTHON_INCLUDE = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
ENGINE_NAME = "_rust_engine.so"
BRIDGE_NAME = "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
PREFIX_MAP = "/rebar-phase2-v6-owned-source"
SOURCE_MODES = ("--render-contract", "--verify-frozen-context", "--self-test")
ACTUAL_MODES = ("--build", "--run")

# role, complete relative path, SHA-256, exact byte count, exact device-2064 inode.
WORKSPACE_OWNERS = (
    ("goal", "GOAL.md", GOAL_SHA, 3756, 31364044),
    ("original_oracle", "oracle/phase1/p0-completeness-v4.json", "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("supplemental_oracle", "oracle/phase1/p0-differential-fuzz-reference-v3.json", "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff", 5288, 525082),
    ("latest_v25_campaign", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json", V25_FAILURE_SHA, 11832, 524846),
    ("first_party_cargo_manifest", "candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, 428094),
    ("first_party_cargo_lock", "candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, 428098),
    ("first_party_rust_vm", "candidates/rust/src/lib.rs", CANONICAL_LIB_SHA, 177967, 428096),
    ("first_party_rust_search", "candidates/rust/src/search.rs", CANONICAL_SEARCH_SHA, 14773, 429682),
    ("first_party_rust_inline_stack", "candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269, 428151),
    ("complete_public_profile_source", "tools/rust_public_profile_v2.py", "a4eb77c29e06b1a77152ebb2275525bfd75b3fa26fd25f100059c79cfb39437a", 31941, 429686),
    ("complete_public_profile_protocol", "oracle/phase3/RUST-PUBLIC-PROFILE-V2.md", "aa96b3a2132be6557020a753da8e57e1c210b1a9b9216b6a015f36715e208b9d", 3128, 526049),
    ("complete_public_profile_manifest", "oracle/phase3/rust-public-profile-v2.json", "9687806994bcbb401ed89cba11197b79a491da023b95be89e1686a7c6cccafea", 3926, 526050),
    ("complete_public_profile_summary", "experiments/rust_public_profile_v2/public-run-001/summary.json", "71468c3196d75994180de6ce27ab1a3c48e1253fd37f0e4d0f33ba7a6d4099cb", 28079, 526265),
    ("complete_public_paired_rows", "experiments/rust_public_profile_v2/public-run-001/paired-timing.raw.json", "cd237092007b231b37293414e417bce80afde3bc44a44e787adb53a0e66f7697", 504914, 526215),
    ("public_allocation_function_table", "experiments/rust_public_profile_v2/public-run-001/rust.cpu.txt", "542b2fd936535ea5739db31f7cd6e97ff62642b20bbb448c09e33095e47a7d1d", 72934, 526257),
    ("public_allocation_callers", "experiments/rust_public_profile_v2/public-run-001/rust.ffi.txt", "6957b8e19c2388173c719c757717e67aa8b116ba97243e226fed69619646d483", 525686, 526259),
    ("public_native_heap_totals", "experiments/rust_public_profile_v2/public-run-001/rust.heap.txt", "ea98056637f2a3b9634549e57c28b2183167f4874441f31140913b0c93d68b9d", 1429, 526263),
    ("public_profiler_clock_failure", "experiments/rust_public_profile_v2/public-run-001/rust.er/log.xml", "0a893318548fb3974ed0529a2379c5080c8f52142a8af81ae52645abbaf07dc2", 65536, 526246),
)
ADDITIONAL_OWNERS = (
    ("canonical_bridge", "candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676, 419054),
    ("canonical_newline", "candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416, 427958),
    ("canonical_unicode", "candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989, 428152),
    ("canonical_adapter", "candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151, 428100),
    ("workspace_source", "tools/apply_owned_rust_vm_workspace_reuse_v1.py", "8224159adcc5aa930eb93d532d69af5c2365e461329888aafae84651803e5b05", 78186, 430460),
    ("workspace_protocol", "oracle/phase2/RUST-VM-WORKSPACE-REUSE-V1.md", "c220fe3da676c45129e1e7ca88def2780a978ea3cd98cf060a2e415a9975827e", 5744, 524865),
    ("workspace_contract", "oracle/phase2/rust-vm-workspace-reuse-v1.json", "8c39d9ef323213b065ff31e50b5374df64c953677c1da76b3ee83efe17b5e40b", 10412, 524867),
    ("workspace_application", "oracle/phase2/evidence/rust-vm-workspace-reuse-v1-application.json", "5f12bd6013b0b1781dc9c66bcaa5a1ed103e3610a1602f72e84348807b42eba6", 2352, 525144),
    ("workspace_variant", "candidates/rust/variants/vm_workspace_reuse_v1/lib.rs", WORKSPACE_SHA, WORKSPACE_BYTES, 525143),
    ("corrected_bridge_source", "tools/apply_owned_rust_no_external_introspection_v1.py", "68cafe6b6bdf336aff162f86c4c9ddc1aec7607e312c09b2a032e7462e466ec7", 61181, 430722),
    ("corrected_bridge_protocol", "oracle/phase2/RUST-NO-EXTERNAL-INTROSPECTION-V1.md", "15f068ecd0c1970d8bec1f9cb011072c09cb5d064938c24abe1088e4565268c3", 6240, 526268),
    ("corrected_bridge_contract", "oracle/phase2/rust-no-external-introspection-v1.json", "224e118a3878692552b31d588b38ea4953bee9c77c7853687b424360776b53d2", 5305, 526270),
    ("corrected_bridge_application", "oracle/phase2/evidence/rust-no-external-introspection-v1-application.json", "57e28ad65b538db5189f264904d303f37f13506022eae07b12185a52f2624a43", 1774, 524813),
    ("corrected_bridge_variant", "candidates/rust/variants/no_external_introspection_v1/py_bridge.c", CORRECTED_BRIDGE_SHA, CORRECTED_BRIDGE_BYTES, 524811),
    ("capture_clamp_source", "tools/apply_owned_rust_capture_clamp_semantics_v1.py", "ff4b45f370bb6df1a3693cb1046031df93f3dffb336f4cca695768a1adb34fb7", 71522, 429579),
    ("capture_clamp_protocol", "oracle/phase2/RUST-CAPTURE-CLAMP-SEMANTICS-V1.md", "15bd3b25b3f86638ddcb45cbc11d962341a905903a4cd52a632f6c3f1a078ff9", 4645, 526033),
    ("capture_clamp_contract", "oracle/phase2/rust-capture-clamp-semantics-v1.json", "46344723f24c65c123c4550c9652b3547866a2ae1a8419444d3359eb048294c6", 11342, 526034),
    ("capture_clamp_variant", "candidates/rust/variants/capture_clamp_semantics_v1/py_bridge.c", CAPTURE_BRIDGE_SHA, CAPTURE_BRIDGE_BYTES, 526064),
    ("adapter_source", "tools/apply_owned_rust_public_contract_source_repair_v3.py", "5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859", 92060, 431033),
    ("adapter_protocol", "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md", "2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34", 6405, 524675),
    ("adapter_contract", "oracle/phase2/rust-public-contract-source-repair-v3.json", "82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1", 14817, 524678),
    ("v25_source", "tools/reproduce_owned_rust_capture_clamp_source_build_v25.py", "f0a5d0b0af76b83e4f7091050afc187458c8c4380a37418f5df0de41d882b408", 186263, 429530),
    ("v25_protocol", "oracle/phase2/RUST-CAPTURE-CLAMP-SOURCE-BUILD-V25.md", "ddc7c1fcf385ec979c73a304123025a6e5974a8eb37dd61cf189ccba20687f85", 7140, 525993),
    ("v25_contract", "oracle/phase2/rust-capture-clamp-source-build-v25.json", "528d2bcccb2cceed5f607f7ec8428b18df10f30b9b6b6f7313083a288061127a", 229419, 526066),
    ("v25_publication", "oracle/phase2/evidence/native-source-build-v25-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-publication-receipt.json", V25_PUBLICATION_SHA, 5231, 526084),
    ("v25_root", "oracle/phase2/evidence/native-source-build-v25-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-root-provenance-receipt.json", V25_ROOT_SHA, 61798, 526085),
    ("v26_source", "tools/reproduce_owned_rust_anchor_source_build_v26.py", "7a276a4bf675f818cfe3716aad13c5e741f4a45709e899c82af36e2b4cb10e66", 112085, 430771),
    ("v26_protocol", "oracle/phase2/RUST-ANCHOR-SOURCE-BUILD-V26.md", "06ffb539e1f9e2bf7350b1d27478c988dd7c429f2ee295e40181b9320b3e3fd3", 7578, 524812),
    ("v26_contract", "oracle/phase2/rust-anchor-source-build-v26.json", "ea213e235fb56ca4235763643d5569ebb1b63c45678363efe322a525eef65924", 21189, 524863),
    ("v26_publication", "oracle/phase2/evidence/native-source-build-v26-rust-phase2-v26-rust-mandatory-anchor-root-provenance-publication-receipt.json", V26_PUBLICATION_SHA, 5075, 524963),
    ("v26_root", "oracle/phase2/evidence/native-source-build-v26-rust-phase2-v26-rust-mandatory-anchor-root-provenance-root-provenance-receipt.json", V26_ROOT_SHA, 76442, 524964),
    ("v27_source", "tools/reproduce_owned_rust_compiler_fastpath_source_build_v27.py", "4ac3123d83db6858a9fddd311b3b7ac7966e29aede6e786594c7d956e2bf9e8e", 245008, 429062),
    ("v27_protocol", "oracle/phase2/RUST-COMPILER-FASTPATH-SOURCE-BUILD-V27.md", "43b81f47a196d3db0972269d6fba4d94b4437cb59a1c5a3648d8d45f5939fa5f", 5810, 524809),
    ("v27_contract", "oracle/phase2/rust-compiler-fastpath-source-build-v27.json", "a2ffa190a8fd15ec3bcf82f0e1eedc5eb4b919af8c6b3fbf99cf54a525604a41", 617433, 524861),
    ("v27_publication", "oracle/phase2/evidence/native-source-build-v27-rust-phase2-v27-rust-compiler-fast-v1-root-provenance-publication-receipt.json", V27_PUBLICATION_SHA, 6444, 524869),
    ("v27_root", "oracle/phase2/evidence/native-source-build-v27-rust-phase2-v27-rust-compiler-fast-v1-root-provenance-root-provenance-receipt.json", V27_ROOT_SHA, 64122, 524870),
    ("v4_source", "tools/audit_candidate_runtime_non_delegation_v4.py", "597f2f1156d773a42e32103ef7370e8552a416756910c013cdcd0cfc34d39b02", 121807, 429582),
    ("v4_protocol", "oracle/phase2/RUNTIME-NON-DELEGATION-V4.md", "6c3bd6b2ccabe3ab240771d743afce5b32f1de17a510bedd835e867c5cea7826", 5325, 526087),
    ("v4_contract", "oracle/phase2/runtime-non-delegation-v4.json", "edc3ac8866da7afb5934b56fbcbff38a908e5109f7975f998753b479aa7bc672", 7266, 526086),
    ("v4_actual_failure", "oracle/phase2/evidence/runtime-non-delegation-v4-actual-source-audit-failure.json", AUDIT_FAILURE_SHA, 20985, 526140),
)
ALL_ROWS = WORKSPACE_OWNERS + ADDITIONAL_OWNERS
ROW_BY_ROLE = {row[0]: row for row in ALL_ROWS}
ROW_BY_PATH: dict[str, tuple] = {}
for _row in ALL_ROWS:
    _existing = ROW_BY_PATH.get(_row[1])
    if _existing is not None and _existing[1:] != _row[1:]:
        raise SystemExit("conflicting independently pinned V29 source-owner identity")
    ROW_BY_PATH[_row[1]] = _row

TOOLCHAIN = (
    (RUSTC, "bff349e72704ff70bc08a234a3847338e797065bbedde5e556808bc87b7bf7c6", 644784, DEVICE, 31359570, 1000),
    (CARGO, "841072d1d92f9e841d9ba5b0814182a0adf064acf4527cd120967b7bc49dcb66", 42185192, DEVICE, 31359488, 1000),
    (GCC, "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26", 1023032, 1048708, 10445975, 65534),
    (READELF, "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0", 789280, 1048708, 10446013, 65534),
)

OLD_FLAG_BLOCK = b"""        ordered = ((self.ASCII, "ASCII"), (self.IGNORECASE, "IGNORECASE"), (self.LOCALE, "LOCALE"), (self.UNICODE, "UNICODE"), (self.MULTILINE, "MULTILINE"), (self.DOTALL, "DOTALL"), (self.VERBOSE, "VERBOSE"), (self.DEBUG, "DEBUG"))
        known = sum(int(bit) for bit, _ in ordered)
        parts = [f"re.{name}" for bit, name in ordered if value & int(bit)]
        unknown = value & ~known
        if unknown:
            parts.append(hex(unknown))
        return "|".join(parts)
"""
V2_FLAG_BLOCK = b"""        ordered = (
            (self.ASCII, "ASCII"),
            (self.IGNORECASE, "IGNORECASE"),
            (self.LOCALE, "LOCALE"),
            (self.UNICODE, "UNICODE"),
            (self.MULTILINE, "MULTILINE"),
            (self.DOTALL, "DOTALL"),
            (self.VERBOSE, "VERBOSE"),
            (self.DEBUG, "DEBUG"),
        )
        known = sum(int(bit) for bit, _ in ordered)
        parts = [f"re.{name}" for bit, name in ordered if value & int(bit)]
        unknown = value & ~known
        if unknown:
            if not parts:
                return f"re.RegexFlag({value})"
            parts.append(hex(unknown))
        return "|".join(parts)
"""
OLD_ERROR_BLOCK = b"""class PatternError(Exception):
    def __init__(self, msg, pattern=None, pos=None):
"""
V2_ERROR_BLOCK = b"""class PatternError(Exception):
    __module__ = "re"

    def __init__(self, msg, pattern=None, pos=None):
"""
OLD_PATTERN_BLOCK = b"""    def __repr__(self):
        flags = self.flags & ~int(UNICODE)
        shown = repr(self.pattern)
        if len(shown) > 200:
            shown = shown[:200]
        suffix = f", {RegexFlag(flags)!r}" if flags else ""
        return f"re.compile({shown}{suffix})"

    def __eq__(self, other):
        if not isinstance(other, Pattern):
            return NotImplemented
        return (type(self.pattern), self.pattern, self.flags) == (type(other.pattern), other.pattern, other.flags)

    def __hash__(self):
        return hash((type(self.pattern), self.pattern, self.flags))
"""
V2_PATTERN_BLOCK = b"""    def __repr__(self):
        flags = self.flags & ~int(UNICODE)
        shown = repr(self.pattern)
        if len(shown) > 200:
            shown = shown[:200]
        if flags:
            rendered = repr(RegexFlag(flags))
            if rendered.startswith("re.RegexFlag("):
                rendered = hex(flags)
            suffix = f", {rendered}"
        else:
            suffix = ""
        return f"re.compile({shown}{suffix})"

    def __eq__(self, other):
        if not isinstance(other, Pattern):
            return NotImplemented
        return (self.pattern, self.flags) == (other.pattern, other.flags)

    def __hash__(self):
        return hash((self.pattern, self.flags))
"""
V3_PATTERN_BLOCK = b"""    def __repr__(self):
        flags = self.flags & ~int(UNICODE)
        shown = repr(self.pattern)
        if len(shown) > 200:
            shown = shown[:200]
        if flags:
            ordered = (
                (int(IGNORECASE), "re.IGNORECASE"),
                (int(LOCALE), "re.LOCALE"),
                (int(MULTILINE), "re.MULTILINE"),
                (int(DOTALL), "re.DOTALL"),
                (int(UNICODE), "re.UNICODE"),
                (int(VERBOSE), "re.VERBOSE"),
                (int(DEBUG), "re.DEBUG"),
                (int(ASCII), "re.ASCII"),
            )
            parts = [name for bit, name in ordered if flags & bit]
            unknown = flags & ~sum(bit for bit, _ in ordered)
            if unknown:
                parts.append(hex(unknown))
            suffix = ", " + "|".join(parts)
        else:
            suffix = ""
        return f"re.compile({shown}{suffix})"

    def __eq__(self, other):
        if not isinstance(other, Pattern):
            return NotImplemented
        return (self.pattern, self.flags) == (other.pattern, other.flags)

    def __hash__(self):
        return hash((self.pattern, self.flags))
"""


class BuildFreezeError(Exception):
    """Reject altered evidence, forbidden effects, or an unauthorized build."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise BuildFreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only genuine complete immutable bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value)
            and len(set(value)) > 1,
            "require one independent lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def no_matching_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "subprocess", "socket", "candidates", "rebar")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject candidate, native, matching-engine, process, or network imports")


class SourceWall:
    """An irreversible exact-owner descriptor wall with one metadata exception."""

    def __init__(self, *, source_mode: bool) -> None:
        self.source_mode = source_mode
        self.installed = False
        self.allowed = frozenset(ROOT + "/" + path for path in ROW_BY_PATH) | {
            ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL, ROOT + "/" + CONTRACT,
        }
        self.live: set[int] = set()
        self.blocked: dict[str, int] = {}
        self.metadata_probes = 0
        self.proposal_open_count = 0
        self.native_open = os.open
        self.native_read = os.read
        self.native_fstat = os.fstat
        self.native_close = os.close
        self.native_lstat = os.lstat

    def deny(self, reason: str) -> None:
        self.blocked[reason] = self.blocked.get(reason, 0) + 1
        raise BuildFreezeError("physical V29 source wall rejected " + reason)

    def approved(self, path: object) -> bool:
        return (type(path) is str and path in self.allowed
                and path == os.path.normpath(path)
                and ".." not in path.split("/")
                and not path.endswith((".so", ".gz", ".zip"))
                and "holdout" not in path.lower()
                and "/.git/" not in path and "/.codex/" not in path
                and "/.agents/" not in path)

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else None
            destructive = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL
                           | os.O_TRUNC | os.O_APPEND | getattr(os, "O_TMPFILE", 0))
            if (not self.approved(path) or type(flags) is not int
                    or flags & destructive or not flags & os.O_NOFOLLOW
                    or type(mode) is str and any(item in mode for item in "wax+")):
                if type(path) is str and path == ROOT + "/" + HISTORICAL_PROPOSAL:
                    self.proposal_open_count += 1
                self.deny("candidate-native-final-archive-or-foreign-open")
            return
        if event in ("compile", "exec"):
            item = args[0] if args else None
            path = args[1] if event == "compile" and len(args) > 1 else (
                getattr(item, "co_filename", None) if event == "exec" else None)
            if path not in {
                ROOT + "/" + ROW_BY_ROLE["workspace_source"][1],
                ROOT + "/" + ROW_BY_ROLE["corrected_bridge_source"][1],
            }:
                self.deny("candidate-execution-or-unapproved-code")
            return
        if event == "import":
            self.deny("candidate-native-matcher-or-late-import")
        if event.startswith(("subprocess.", "socket.", "ctypes.", "threading.",
                             "multiprocessing.", "_thread.", "os.exec", "os.spawn",
                             "os.posix_spawn", "os.fork", "os.system", "os.dlopen",
                             "_interpreters.", "cpython.PyInterpreterState_New")):
            self.deny("candidate-compiler-native-process-network-or-interpreter")
        if event.startswith(("os.mkdir", "os.remove", "os.unlink", "os.rename",
                             "os.replace", "os.rmdir", "os.chmod", "os.chown",
                             "os.utime", "os.truncate", "os.chdir", "tempfile.")):
            self.deny("filesystem-mutation-private-root-or-broad-discovery")
        if event.startswith(("time.", "os.urandom", "os.getrandom")):
            self.deny("clock-or-entropy")

    def forbidden(self, label: str):
        def reject(*_args: object, **_kwargs: object) -> object:
            self.deny(label)
        return reject

    def open(self, path: str, flags: int, mode: int = 0,
             *, dir_fd: int | None = None) -> int:
        if (not self.approved(path) or dir_fd is not None or mode != 0
                or type(flags) is not int
                or flags != (os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)):
            self.deny("unticketed-candidate-native-final-or-write-open")
        descriptor = self.native_open(path, flags)
        require(descriptor not in self.live, "reject aliased source descriptor")
        self.live.add(descriptor)
        return descriptor

    def read(self, descriptor: int, size: int, /) -> bytes:
        if descriptor not in self.live or type(size) is not int or size < 0:
            self.deny("foreign-or-candidate-descriptor-read")
        return self.native_read(descriptor, size)

    def fstat(self, descriptor: int, /) -> os.stat_result:
        if descriptor not in self.live:
            self.deny("foreign-or-native-descriptor-metadata")
        return self.native_fstat(descriptor)

    def close(self, descriptor: int, /) -> None:
        if descriptor not in self.live:
            self.deny("foreign-descriptor-close")
        self.native_close(descriptor)
        self.live.remove(descriptor)

    def metadata(self, path: str, *, dir_fd: int | None = None) -> os.stat_result:
        if (path != ROOT + "/" + HISTORICAL_PROPOSAL or dir_fd is not None
                or self.metadata_probes != 0):
            self.deny("native-final-successor-private-root-or-broad-metadata")
        info = self.native_lstat(path)
        self.metadata_probes += 1
        return info

    def install(self) -> None:
        require(self.source_mode and not self.installed,
                "install one irreversible source-only physical wall")
        sys.addaudithook(self.audit)
        os.open = self.open
        os.read = self.read
        os.fstat = self.fstat
        os.close = self.close
        os.lstat = self.metadata
        builtins.open = self.forbidden("builtin-foreign-or-native-file-open")
        io.open = self.forbidden("io-foreign-or-native-file-open")
        _io.open = self.forbidden("native-foreign-or-native-file-open")
        for name in ("stat", "listdir", "scandir", "walk", "fwalk", "access",
                     "readlink", "fdopen", "dup", "dup2", "pipe", "pipe2",
                     "write", "mkdir", "makedirs", "remove", "unlink", "rename",
                     "replace", "rmdir", "chmod", "chown", "chdir", "fchdir",
                     "fork", "posix_spawn", "posix_spawnp", "system", "urandom",
                     "getrandom", "times", "waitpid"):
            if hasattr(os, name):
                setattr(os, name, self.forbidden("filesystem-process-native-or-clock-" + name))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns",
                     "clock_gettime", "clock_gettime_ns", "sleep", "gmtime",
                     "localtime", "ctime", "strftime"):
            if hasattr(time, name):
                setattr(time, name, self.forbidden("clock-" + name))
        self.installed = True


def read_owner(wall: SourceWall, row: tuple, *, dynamic: bool = False) -> tuple[bytes, dict]:
    role, relative, fingerprint, length, inode = row
    checked_sha(fingerprint, role)
    require(type(relative) is str and relative in ROW_BY_PATH or dynamic,
            "reject an unowned exact public source path")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    descriptor = os.open(ROOT + "/" + relative, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_uid == os.geteuid()
                and before.st_nlink == 1 and 0 < before.st_size <= MAX_OWNER_BYTES
                and (dynamic or before.st_size == length and before.st_ino == inode),
                "reject substituted, linked, foreign, or unsafe source owner: " + role)
        remaining = before.st_size
        blocks: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(remaining, 65536))
            require(type(block) is bytes and bool(block),
                    "reject truncated complete source owner: " + role)
            blocks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"", "reject a growing source owner: " + role)
        after = os.fstat(descriptor)
        require(all(getattr(before, item) == getattr(after, item)
                    for item in ("st_dev", "st_ino", "st_size", "st_nlink",
                                 "st_mode", "st_mtime_ns", "st_ctime_ns")),
                "reject a source owner changed while authenticated: " + role)
    finally:
        os.close(descriptor)
    raw = b"".join(blocks)
    require(digest(raw) == fingerprint,
            "reject a substituted complete SHA-256 source owner: " + role)
    return raw, {"role": role, "path": relative, "sha256": fingerprint,
                 "bytes": before.st_size, "device": before.st_dev,
                 "inode": before.st_ino, "mode": "0600", "uid": before.st_uid,
                 "nlink": before.st_nlink}


def dynamic_owner(wall: SourceWall, role: str, relative: str, pin: str) -> tuple[bytes, dict]:
    require(relative in (SOURCE, PROTOCOL, CONTRACT),
            "independently pin exactly one dynamic V29 freeze owner")
    return read_owner(wall, (role, relative, checked_sha(pin, role), 1, 1), dynamic=True)


def load_module(role: str, raw: bytes) -> types.ModuleType:
    row = ROW_BY_ROLE[role]
    name = "_rebar_v29_authenticated_" + role
    require(name not in sys.modules, "reject a reused first-party source controller")
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + row[1]
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def exact_replace(source: bytes, before: bytes, after: bytes, label: str) -> bytes:
    require(before != after and source.count(before) == 1
            and source.count(after) == 0,
            "reject nonexclusive corrected-adapter replacement: " + label)
    return source.replace(before, after, 1)


def derive_adapter(source: bytes) -> bytes:
    canonical = ROW_BY_ROLE["canonical_adapter"]
    require(len(source) == canonical[3] and digest(source) == canonical[2],
            "derive the adapter solely from the immutable canonical first-party owner")
    result = source
    for label, before, after in (
        ("flag", OLD_FLAG_BLOCK, V2_FLAG_BLOCK),
        ("error", OLD_ERROR_BLOCK, V2_ERROR_BLOCK),
        ("pattern-v2", OLD_PATTERN_BLOCK, V2_PATTERN_BLOCK),
        ("pattern-v3", V2_PATTERN_BLOCK, V3_PATTERN_BLOCK),
    ):
        result = exact_replace(result, before, after, label)
    require(len(result) == CORRECTED_ADAPTER_BYTES
            and digest(result) == CORRECTED_ADAPTER_SHA,
            "rederive the exact previously authenticated corrected public adapter")
    for forbidden in (b"import re\n", b"from re import", b"import _sre",
                      b"regex.compile", b"pcre", b"oniguruma", b"subprocess"):
        require(result.count(forbidden) == source.count(forbidden),
                "never add an external matching engine or another candidate")
    return result


def strict_document(module: types.ModuleType, raw: bytes, label: str) -> dict:
    value = module.json_object(raw, label)
    require(type(value) is dict, "require a complete strict public document: " + label)
    return value


def authenticate_history(module: types.ModuleType, payload: dict[str, bytes]) -> dict:
    original = strict_document(module, payload["original_oracle"], "original P0 oracle")
    supplemental = strict_document(module, payload["supplemental_oracle"], "supplemental oracle")
    failure = strict_document(module, payload["latest_v25_campaign"], "actual V25 FAIL receipt")
    module.validate_oracles(original, supplemental, failure)
    require(failure.get("actual_candidate_workers") == 13
            and failure.get("infrastructure_failure_count") == 0,
            "preserve all 13 genuine fully observed V25 candidate workers")
    audit = strict_document(module, payload["v4_actual_failure"], "V4 runtime audit FAIL")
    findings = audit.get("findings")
    require(audit.get("schema") == "rebar-phase2-first-party-runtime-non-delegation-v4-root-static-audit"
            and audit.get("status") == "FAIL" and audit.get("finding_count") == 1
            and type(findings) is list and len(findings) == 1
            and findings[0].get("family") == FAMILY
            and findings[0].get("code") == "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE"
            and findings[0].get("path") == "candidates/rust/py_bridge.c"
            and findings[0].get("line") == 4403
            and findings[0].get("import_chain")
            == ["candidate native bridge", "inspect", "tokenize", "re", "re.compile"]
            and audit.get("holdout") == "NOT OPENED",
            "preserve the genuine V4 FAIL-1 without asserting a corrected runtime audit")

    history = {}
    for version in (25, 26, 27):
        prefix = "v" + str(version)
        freeze = strict_document(module, payload[prefix + "_contract"], prefix + " frozen build")
        publication = strict_document(module, payload[prefix + "_publication"], prefix + " public build receipt")
        root = strict_document(module, payload[prefix + "_root"], prefix + " root provenance")
        require(freeze.get("version") == version and freeze.get("family") == FAMILY
                and freeze.get("source", {}).get("sha256") == ROW_BY_ROLE[prefix + "_source"][2]
                and freeze.get("protocol", {}).get("sha256") == ROW_BY_ROLE[prefix + "_protocol"][2]
                and publication.get("status") == "PASS"
                and publication.get("build_status") == "PASS"
                and publication.get("source_sha256") == ROW_BY_ROLE[prefix + "_source"][2]
                and publication.get("protocol_sha256") == ROW_BY_ROLE[prefix + "_protocol"][2]
                and publication.get("contract_sha256") == ROW_BY_ROLE[prefix + "_contract"][2]
                and publication.get("actual_compiler_process_count") == 28
                and publication.get("actual_completed_phase_count") == 2
                and publication.get("corrected_public_adapter_sha256") == CORRECTED_ADAPTER_SHA
                and publication.get("corrected_public_adapter_bytes") == CORRECTED_ADAPTER_BYTES
                and root.get("status") == "PASS"
                and root.get("canonical_build_status") == "PASS"
                and root.get("canonical_build_receipt_sha256") == ROW_BY_ROLE[prefix + "_publication"][2]
                and root.get("actual_compiler_process_count") == 28
                and root.get("actual_source_phase_count") == 2
                and root.get("holdout") == "NOT OPENED",
                "authenticate complete genuine first-party V" + str(version) + " dual-build receipts")
        outputs = root.get("actual_reproduced_native_outputs")
        require(type(outputs) is dict and set(outputs) == {"engine", "bridge"}
                and type(outputs["engine"].get("sha256")) is str
                and outputs["bridge"].get("sha256")
                == "adcb000c036e075a52f43926750648a4610e853e628d5433b1fbcc17e99a89e4",
                "preserve both actual first-party V" + str(version) + " native outputs")
        history[prefix] = {
            "source_sha256": ROW_BY_ROLE[prefix + "_source"][2],
            "protocol_sha256": ROW_BY_ROLE[prefix + "_protocol"][2],
            "contract_sha256": ROW_BY_ROLE[prefix + "_contract"][2],
            "publication_receipt_sha256": ROW_BY_ROLE[prefix + "_publication"][2],
            "root_receipt_sha256": ROW_BY_ROLE[prefix + "_root"][2],
            "actual_compiler_process_count": 28,
            "actual_completed_phase_count": 2,
            "actual_engine_sha256": outputs["engine"]["sha256"],
            "actual_bridge_sha256": outputs["bridge"]["sha256"],
            "corrected_adapter_sha256": CORRECTED_ADAPTER_SHA,
            "candidate_executed_by_build": False,
        }
    require(history["v25"]["actual_engine_sha256"]
            == "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
            and history["v26"]["actual_engine_sha256"]
            == "fde7b6a6193cd3877753e0f119d29727014b836b2aa2e4c07bdcec0c9f29c102"
            and history["v27"]["actual_engine_sha256"]
            == "04492763937d0631f162514098ce5d3148e71de21fe7b4cd3f5f876b634f5876",
            "preserve each distinct independently verified historical Rust architecture")
    return {"original_case_execution_denominator": 31237,
            "original_suite_count": 13, "named_private_waiver_count": 13,
            "latest_original_campaign": "V25", "latest_candidate_status": "FAIL",
            "latest_candidate_publication_status": "PASS",
            "latest_candidate_semantic_mismatch_count": 1352,
            "latest_candidate_verified_passing_case_count": 15877,
            "latest_candidate_worker_count": 13,
            "latest_candidate_completed_suite_count": 13,
            "latest_candidate_infrastructure_failure_count": 0,
            "latest_mismatch_counts": {"shape_v2": 1112, "substitution_v2": 240},
            "latest_actual_candidate_receipt_sha256": V25_FAILURE_SHA,
            "historical_runtime_audit_v4_status": "FAIL",
            "historical_runtime_audit_v4_finding_count": 1,
            "historical_runtime_audit_v4_receipt_sha256": AUDIT_FAILURE_SHA,
            "new_runtime_non_delegation_audit_status": "NOT RUN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "first_party_builds": history}


def proposal_metadata(wall: SourceWall) -> dict:
    path = ROOT + "/" + HISTORICAL_PROPOSAL
    info = os.lstat(path) if wall.installed else wall.metadata(path)
    require(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o600
            and info.st_dev == DEVICE and info.st_ino == HISTORICAL_PROPOSAL_INODE
            and info.st_size == HISTORICAL_PROPOSAL_BYTES and info.st_nlink == 1
            and info.st_uid == os.geteuid() and wall.metadata_probes == 1
            and wall.proposal_open_count == 0,
            "retain only historical invalidated V2 proposal metadata without content")
    return {"historical_proposal_path": HISTORICAL_PROPOSAL,
            "historical_proposal_sha256_independently_pinned_not_read": HISTORICAL_PROPOSAL_SHA,
            "historical_proposal_bytes_metadata_only": HISTORICAL_PROPOSAL_BYTES,
            "historical_proposal_inode_metadata_only": HISTORICAL_PROPOSAL_INODE,
            "historical_proposed_case_count": HISTORICAL_PROPOSAL_CASES,
            "historical_proposal_content_open_count": 0,
            "historical_proposal_metadata_probe_count": 1,
            "historical_proposal_trust_status": "COMPROMISED; RETIRED",
            "current_final_holdout_status": FINAL_HOLDOUT_STATUS,
            "rekeyed_successor_required": True,
            "rekeyed_successor_created": False,
            "rekeyed_successor_opened": False,
            "hidden_cases_generated": 0,
            "hidden_cases_opened": 0,
            "final_comparison_authorized": False,
            "candidate_qualification_permitted": False}


def load_context(wall: SourceWall, pins: dict[str, str], *, render: bool) -> tuple[dict, dict]:
    source_raw, source_owner = dynamic_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol_raw, protocol_owner = dynamic_owner(wall, "protocol", PROTOCOL,
                                                 pins["--protocol-sha256"])
    require(source_raw.startswith(b"#!/usr/bin/env python3\n")
            and FINAL_HOLDOUT_STATUS.encode("ascii") in protocol_raw,
            "bind both independently pinned V29 source and explicit invalidated protocol")
    if not render:
        contract_raw, contract_owner = dynamic_owner(wall, "contract", CONTRACT,
                                                     pins["--contract-sha256"])
    else:
        contract_raw, contract_owner = b"", {}

    payload_by_path: dict[str, bytes] = {}
    identities: list[dict] = []
    for row in ROW_BY_PATH.values():
        raw, identity = read_owner(wall, row)
        payload_by_path[row[1]] = raw
        identities.append(identity)
    payload = {role: payload_by_path[row[1]] for role, row in ROW_BY_ROLE.items()}
    workspace = load_module("workspace_source", payload["workspace_source"])
    bridge = load_module("corrected_bridge_source", payload["corrected_bridge_source"])
    require(workspace.SCHEMA == "rebar-owned-rust-vm-workspace-reuse-v1-source-freeze"
            and workspace.DERIVED_SHA256 == WORKSPACE_SHA
            and callable(workspace.transform_source)
            and callable(workspace.synthetic_semantics)
            and callable(workspace.validate_profile)
            and bridge.SCHEMA == "rebar-owned-rust-no-external-introspection-v1-source-freeze"
            and bridge.OUTPUT_SHA256 == CORRECTED_BRIDGE_SHA
            and callable(bridge.transform),
            "execute only the two completely frozen first-party source transformers")

    workspace_contract = strict_document(workspace, payload["workspace_contract"],
                                         "frozen matching-workspace contract")
    workspace_application = strict_document(workspace, payload["workspace_application"],
                                            "actual workspace materialization receipt")
    workspace_variant = workspace.transform_source(payload["first_party_rust_vm"])
    require(workspace_variant == payload["workspace_variant"]
            and len(workspace_variant) == WORKSPACE_BYTES
            and workspace_contract.get("source", {}).get("sha256")
            == ROW_BY_ROLE["workspace_source"][2]
            and workspace_contract.get("protocol", {}).get("sha256")
            == ROW_BY_ROLE["workspace_protocol"][2]
            and workspace_contract.get("derived_first_party_vm_source", {}).get("sha256")
            == WORKSPACE_SHA
            and workspace_application.get("status") == "PASS"
            and workspace_application.get("source_sha256")
            == ROW_BY_ROLE["workspace_source"][2]
            and workspace_application.get("protocol_sha256")
            == ROW_BY_ROLE["workspace_protocol"][2]
            and workspace_application.get("contract_sha256")
            == ROW_BY_ROLE["workspace_contract"][2]
            and workspace_application.get("variant_materialized") is True
            and workspace_application.get("materialized_variant", {}).get("sha256")
            == WORKSPACE_SHA
            and workspace_application.get("materialized_variant", {}).get("inode")
            == ROW_BY_ROLE["workspace_variant"][4]
            and workspace_application.get("candidate_workers_started") == 0
            and workspace_application.get("clock_samples") == 0,
            "authenticate the complete frozen workspace triple and actual application")

    bridge_contract = strict_document(workspace, payload["corrected_bridge_contract"],
                                      "frozen private-introspection correction")
    bridge_application = strict_document(workspace, payload["corrected_bridge_application"],
                                         "actual corrected-bridge materialization")
    corrected_bridge = bridge.transform(payload["capture_clamp_variant"], exact=True)
    require(corrected_bridge == payload["corrected_bridge_variant"]
            and len(corrected_bridge) == CORRECTED_BRIDGE_BYTES
            and bridge_contract.get("source", {}).get("sha256")
            == ROW_BY_ROLE["corrected_bridge_source"][2]
            and bridge_contract.get("protocol", {}).get("sha256")
            == ROW_BY_ROLE["corrected_bridge_protocol"][2]
            and bridge_contract.get("exact_private_introspection_correction", {}).get(
                "target_sha256") == CORRECTED_BRIDGE_SHA
            and bridge_application.get("source_sha256")
            == ROW_BY_ROLE["corrected_bridge_source"][2]
            and bridge_application.get("protocol_sha256")
            == ROW_BY_ROLE["corrected_bridge_protocol"][2]
            and bridge_application.get("contract_sha256")
            == ROW_BY_ROLE["corrected_bridge_contract"][2]
            and bridge_application.get("target_sha256") == CORRECTED_BRIDGE_SHA
            and bridge_application.get("target_bytes") == CORRECTED_BRIDGE_BYTES
            and bridge_application.get("effects", {}).get("candidate_executions") == 0,
            "authenticate the complete corrected-bridge triple and actual application")
    require(b'PyImport_ImportModule("inspect")' not in corrected_bridge
            and b'PyImport_ImportModule("functools")' not in corrected_bridge
            and b"rust_bound_get_signature" not in corrected_bridge,
            "reject the historically failing private external-introspection chain")

    adapter_contract = strict_document(workspace, payload["adapter_contract"],
                                       "frozen first-party corrected adapter")
    require(adapter_contract.get("source", {}).get("sha256")
            == ROW_BY_ROLE["adapter_source"][2]
            and adapter_contract.get("protocol", {}).get("sha256")
            == ROW_BY_ROLE["adapter_protocol"][2],
            "authenticate the previously frozen corrected-adapter source triple")
    corrected_adapter = derive_adapter(payload["canonical_adapter"])
    profile = workspace.validate_profile(payload)
    require(profile.get("complete_public_case_count") == 416
            and profile.get("complete_public_paired_row_count") == 1664
            and profile.get("run_program_allocation_count") == 984
            and profile.get("run_program_guard_repeat_allocation_count") == 408
            and profile.get("run_program_guard_repeat_allocation_bytes") == 120768
            and profile.get("run_program_capture_undo_allocation_count") == 576
            and profile.get("run_program_capture_undo_allocation_bytes") == 276480
            and profile.get("cpu_function_profile") == NOT_MEASURED,
            "authenticate exact public native allocations without inventing CPU time")
    workspace.validate_cargo(payload["first_party_cargo_manifest"],
                             payload["first_party_cargo_lock"],
                             payload["first_party_rust_vm"],
                             payload["first_party_rust_inline_stack"],
                             payload["first_party_rust_search"])
    semantics = workspace.synthetic_semantics()
    require(semantics == workspace_contract.get("synthetic_differential_semantics")
            and semantics.get("case_count") == 18144
            and semantics.get("synthetic_allocations_avoided") == 16848,
            "preserve every independently frozen workspace state and rollback model")
    history = authenticate_history(workspace, payload)
    final = proposal_metadata(wall)
    state = {"source": source_owner, "protocol": protocol_owner,
             "contract": contract_owner, "identities": identities,
             "payload": payload, "workspace_module": workspace,
             "bridge_module": bridge, "workspace_variant": workspace_variant,
             "corrected_bridge": corrected_bridge,
             "corrected_adapter": corrected_adapter, "profile": profile,
             "semantics": semantics, "history": history, "final": final}
    frozen = contract_document(state)
    if not render:
        complete = strict_document(workspace, contract_raw,
                                   "complete independently pinned V29 contract")
        require(complete == frozen and workspace.document(complete) == contract_raw,
                "reject incomplete, altered, noncanonical, or stale V29 source freeze")
    require(not wall.live and wall.proposal_open_count == 0,
            "release every source descriptor and never open historical final contents")
    return frozen, state


def contract_document(state: dict) -> dict:
    profile = dict(state["profile"])
    profile["final_holdout"] = FINAL_HOLDOUT_STATUS
    return {
        "schema": SCHEMA + "-source-freeze", "version": VERSION,
        "status": "SOURCE FROZEN; OFFLINE BUILD NOT RUN; FINAL HOLDOUT INVALIDATED",
        "phase": "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS", "family": FAMILY,
        "immutable_goal_sha256": GOAL_SHA,
        "pinned_python": {"path": PYTHON, "sha256": PYTHON_SHA256,
                          "version": "3.14.6", "required_flags": ["-I", "-B", "-S"]},
        "source": state["source"], "protocol": state["protocol"],
        "authenticated_frozen_source_owner_count": len(state["identities"]),
        "authenticated_frozen_source_owners": state["identities"],
        "original_candidate_correctness": state["history"],
        "first_party_workspace_architecture": {
            "source_sha256": ROW_BY_ROLE["workspace_source"][2],
            "protocol_sha256": ROW_BY_ROLE["workspace_protocol"][2],
            "contract_sha256": ROW_BY_ROLE["workspace_contract"][2],
            "actual_application_receipt_sha256": ROW_BY_ROLE["workspace_application"][2],
            "canonical_lib_path": ROW_BY_ROLE["first_party_rust_vm"][1],
            "canonical_lib_sha256": CANONICAL_LIB_SHA,
            "materialized_variant_path": ROW_BY_ROLE["workspace_variant"][1],
            "materialized_variant_sha256": WORKSPACE_SHA,
            "materialized_variant_bytes": WORKSPACE_BYTES,
            "materialized_variant_inode": ROW_BY_ROLE["workspace_variant"][4],
            "canonical_original_search_path": ROW_BY_ROLE["first_party_rust_search"][1],
            "canonical_original_search_sha256": CANONICAL_SEARCH_SHA,
            "anchor_search_variant_used": False,
            "compiler_fastpath_variant_used": False,
            "architecture": "ROOT-MATCH-LOCAL GUARD/REPEAT/LOOKAROUND WORKSPACE REUSE",
            "nested_assertion_frames_are_independent": True,
            "callback_reentry_frames_are_independent": True,
            "guard_reset_per_attempt": "usize::MAX",
            "repeat_reset_per_attempt": "RepeatState::default()",
            "capture_undo_reuse_in_this_variant": False,
            "synthetic_differential_semantics": state["semantics"],
        },
        "corrected_first_party_no_external_introspection_bridge": {
            "source_sha256": ROW_BY_ROLE["corrected_bridge_source"][2],
            "protocol_sha256": ROW_BY_ROLE["corrected_bridge_protocol"][2],
            "contract_sha256": ROW_BY_ROLE["corrected_bridge_contract"][2],
            "actual_application_receipt_sha256": ROW_BY_ROLE["corrected_bridge_application"][2],
            "path": ROW_BY_ROLE["corrected_bridge_variant"][1],
            "sha256": CORRECTED_BRIDGE_SHA, "bytes": CORRECTED_BRIDGE_BYTES,
            "inode": ROW_BY_ROLE["corrected_bridge_variant"][4],
            "capture_clamp_source_sha256": CAPTURE_BRIDGE_SHA,
            "private_inspect_import_removed": True,
            "private_functools_import_removed": True,
            "private_signature_getter_removed": True,
            "public_native_descriptors_preserved": True,
            "new_runtime_non_delegation_audit": "NOT RUN",
        },
        "corrected_first_party_public_adapter": {
            "source_sha256": ROW_BY_ROLE["adapter_source"][2],
            "protocol_sha256": ROW_BY_ROLE["adapter_protocol"][2],
            "contract_sha256": ROW_BY_ROLE["adapter_contract"][2],
            "sha256": CORRECTED_ADAPTER_SHA, "bytes": CORRECTED_ADAPTER_BYTES,
            "independently_rederived_from_canonical_owner": True,
        },
        "authenticated_public_allocation_profile": profile,
        "frozen_offline_independent_dual_phase_build": {
            "label": LABEL, "status": "NOT RUN", "phase_count": 2,
            "phase_names": list(PHASES),
            "fresh_owner_only_private_source_roots": 2,
            "canonical_source_owners_per_phase": 9,
            "unchanged_first_party_source_owners_per_phase": 6,
            "verified_source_overlays_per_phase": 3,
            "workspace_source_sha256": WORKSPACE_SHA,
            "workspace_source_bytes": WORKSPACE_BYTES,
            "original_search_source_sha256": CANONICAL_SEARCH_SHA,
            "corrected_bridge_source_sha256": CORRECTED_BRIDGE_SHA,
            "corrected_bridge_source_bytes": CORRECTED_BRIDGE_BYTES,
            "corrected_adapter_source_sha256": CORRECTED_ADAPTER_SHA,
            "corrected_adapter_source_bytes": CORRECTED_ADAPTER_BYTES,
            "rust_toolchain_version": "1.95.0", "cargo": CARGO,
            "rustc": RUSTC, "gcc": GCC, "elf_inspector": READELF,
            "toolchain": [{"path": row[0], "sha256": row[1], "bytes": row[2],
                          "device": row[3], "inode": row[4], "uid": row[5]}
                         for row in TOOLCHAIN],
            "cargo_flags": ["build", "--manifest-path", "--release", "--locked",
                            "--offline", "--frozen", "--target-dir"],
            "external_cargo_dependency_count": 0,
            "cargo_net_offline": True, "network_requests_allowed": 0,
            "source_prefix_remap": PREFIX_MAP,
            "process_roles_per_phase": list(PROCESS_NAMES),
            "processes_per_phase": 14,
            "required_distinct_successful_compiler_process_count": 28,
            "cross_phase_complete_engine_elf_byte_equality_required": True,
            "cross_phase_complete_bridge_elf_byte_equality_required": True,
            "candidate_execution_allowed": False,
            "candidate_import_allowed": False,
            "native_library_loading_allowed": False,
            "native_engine_sha256": NOT_MEASURED,
            "native_bridge_sha256": NOT_MEASURED,
            "actual_publication_receipt_sha256": NOT_MEASURED,
            "actual_root_receipt_sha256": NOT_MEASURED,
            "actual_mode_requires_root_authorization": True,
            "actual_mode_requires_matching_frozen_and_pushed_commit": True,
            "actual_mode_requires_committed_pushed_source_triple": True,
            "candidate_correctness": NOT_MEASURED,
            "candidate_qualification": "NOT ESTABLISHED",
        },
        "historical_final_proposal_metadata_only": state["final"],
        "physical_source_wall": {
            "policy": "IRREVERSIBLE DENY DEFAULT; EXACT FROZEN PUBLIC OWNERS ONLY",
            "installed_before_predecessor_owner_reads": True,
            "candidate_execution_allowed": False,
            "candidate_import_allowed": False,
            "native_file_open_allowed": False,
            "native_file_metadata_allowed": False,
            "candidate_or_compiler_process_allowed": False,
            "clock_access_allowed": False,
            "network_access_allowed": False,
            "filesystem_write_allowed": False,
            "broad_filesystem_enumeration_allowed": False,
            "compressed_archive_access_allowed": False,
            "hidden_case_access_allowed": False,
            "historical_final_content_open_allowed": False,
            "historical_final_metadata_probes_allowed": 1,
            "rekeyed_successor_access_allowed": False,
        },
        "source_only_effects": {
            "candidate_executions": 0, "candidate_imports": 0,
            "candidate_workers_started": 0, "compiler_processes_started": 0,
            "native_binaries_opened": 0, "native_metadata_probes": 0,
            "native_libraries_loaded": 0, "clock_samples": 0,
            "network_requests": 0, "filesystem_writes": 0,
            "broad_filesystem_enumerations": 0,
            "compressed_archives_opened": 0, "private_roots_opened": 0,
            "hidden_cases_generated": 0, "hidden_cases_opened": 0,
            "historical_final_content_open_count": 0,
            "historical_final_metadata_probe_count": 1,
            "current_final_holdout_status": FINAL_HOLDOUT_STATUS,
            "candidate_correctness": NOT_MEASURED,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": NOT_MEASURED, "memory": NOT_MEASURED,
            "confidence_intervals": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "qualified_candidate_count": 0, "winner_selected": False,
        },
    }


def reject(action, label: str) -> str:
    try:
        action()
    except (BuildFreezeError, OSError, TypeError, ValueError, UnicodeError):
        return label
    raise BuildFreezeError("accepted hostile source-only control: " + label)


def self_test(wall: SourceWall, state: dict) -> list[str]:
    checks: list[str] = []
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    forbidden_paths = (
        (ROOT + "/candidates/_rust_engine.so", "candidate-native-engine"),
        (ROOT + "/candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
         "candidate-native-bridge"),
        (ROOT + "/candidates/zig_candidate.py", "cross-candidate-runtime"),
        (ROOT + "/" + HISTORICAL_PROPOSAL, "compromised-final-proposal-content"),
        (ROOT + "/oracle/phase3/expanded-sealed-holdout-v3.json",
         "uncreated-rekeyed-final-successor"),
        (ROOT + "/oracle/phase2/evidence/candidate.json.gz", "compressed-archive"),
        (ROOT + "/tools/../candidates/rust_candidate.py", "path-traversal"),
        ("/tmp/rebar-phase2-native-build-v29-rust-private", "private-build-root"),
        ("/etc/hosts", "host-filesystem"),
    )
    for path, label in forbidden_paths:
        checks.append(reject(lambda item=path: os.open(item, flags),
                             "wall-rejects-" + label))
    operations = (
        ("builtins-open", lambda: builtins.open(ROOT + "/" + SOURCE, "rb")),
        ("io-open", lambda: io.open(ROOT + "/" + SOURCE, "rb")),
        ("native-io-open", lambda: _io.open(ROOT + "/" + SOURCE, "rb")),
        ("foreign-descriptor-read", lambda: os.read(0, 1)),
        ("foreign-descriptor-stat", lambda: os.fstat(0)),
        ("foreign-descriptor-close", lambda: os.close(0)),
        ("broad-listdir", lambda: os.listdir(ROOT)),
        ("broad-scandir", lambda: os.scandir(ROOT)),
        ("broad-walk", lambda: os.walk(ROOT)),
        ("ordinary-stat", lambda: os.stat(ROOT + "/" + SOURCE)),
        ("repeat-final-metadata", lambda: os.lstat(ROOT + "/" + HISTORICAL_PROPOSAL)),
        ("clock-time", lambda: time.time()),
        ("clock-monotonic", lambda: time.monotonic()),
        ("clock-perf-counter", lambda: time.perf_counter()),
        ("entropy", lambda: os.urandom(1)),
        ("candidate-import", lambda: sys.audit("import", "candidates.rust_candidate", None)),
        ("matching-engine-import", lambda: sys.audit("import", "re", None)),
        ("native-loader", lambda: sys.audit("ctypes.dlopen", "candidate")),
        ("candidate-process", lambda: sys.audit("subprocess.Popen", "candidate")),
        ("compiler-process", lambda: sys.audit("os.posix_spawn", CARGO)),
        ("candidate-code-execution", lambda: sys.audit("exec", "candidate")),
        ("candidate-code-compilation", lambda: sys.audit("compile", b"candidate", "candidate")),
        ("network", lambda: sys.audit("socket.connect", "candidate")),
        ("source-write", lambda: os.open(ROOT + "/" + SOURCE,
                                         os.O_WRONLY | os.O_TRUNC)),
        ("private-root-create", lambda: os.mkdir("/tmp/rebar-v29-private", 0o700)),
    )
    for label, operation in operations:
        checks.append(reject(operation, "wall-rejects-" + label))
    for changed in (
        state["workspace_variant"][:-1],
        state["workspace_variant"] + b" ",
        state["corrected_bridge"][:-1],
        state["corrected_adapter"][:-1],
    ):
        checks.append(reject(
            lambda value=changed: require(
                digest(value) in (WORKSPACE_SHA, CORRECTED_BRIDGE_SHA,
                                  CORRECTED_ADAPTER_SHA),
                "reject an altered complete private overlay"),
            "reject-altered-exact-private-overlay"))
    for forged in (0, 1, 407, 409, 984, HISTORICAL_PROPOSAL_CASES):
        checks.append(reject(lambda value=forged: require(value == 408,
                                                         "reject forged allocation denominator"),
                             "reject-forged-exact-408-allocation-target"))
    checks.append(reject(lambda: require(FINAL_HOLDOUT_STATUS == "NOT OPENED",
                                         "reject compromised-final-as-sealed"),
                         "reject-compromised-final-as-unopened-sealed-holdout"))
    checks.append(reject(lambda: require(state["history"]["latest_candidate_status"]
                                         == "PASS", "reject failed candidate as passing"),
                         "reject-actual-v25-fail-1352-as-pass"))
    return checks


def parse(arguments: list[str]) -> dict:
    require(type(arguments) is list and bool(arguments), "select one exact V29 mode")
    mode = arguments[0]
    require(mode in SOURCE_MODES + ACTUAL_MODES, "reject unknown source or actual build mode")
    if mode in SOURCE_MODES:
        flags = ["--source-sha256", "--protocol-sha256"]
        if mode != "--render-contract":
            flags.append("--contract-sha256")
        require(len(arguments) == 1 + 2 * len(flags),
                "pin every source-only V29 owner exactly once")
        pins = {}
        for index in range(1, len(arguments), 2):
            flag, value = arguments[index:index + 2]
            require(flag in flags and flag not in pins,
                    "reject missing, duplicated, or foreign source-only authority")
            pins[flag] = checked_sha(value, flag)
        require(set(pins) == set(flags), "independently pin every V29 source owner")
        return {"mode": mode, "pins": pins}

    scalar = {
        "--source-sha256": "source_sha256", "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256", "--frozen-commit": "frozen_commit",
        "--pushed-commit": "pushed_commit", "--label": "label",
        "--workspace-sha256": "workspace_sha256", "--workspace-bytes": "workspace_bytes",
        "--search-sha256": "search_sha256", "--bridge-sha256": "bridge_sha256",
        "--bridge-bytes": "bridge_bytes", "--adapter-sha256": "adapter_sha256",
        "--adapter-bytes": "adapter_bytes", "--workspace-source-sha256": "workspace_source_sha256",
        "--workspace-protocol-sha256": "workspace_protocol_sha256",
        "--workspace-contract-sha256": "workspace_contract_sha256",
        "--workspace-application-sha256": "workspace_application_sha256",
        "--corrected-bridge-source-sha256": "corrected_bridge_source_sha256",
        "--corrected-bridge-protocol-sha256": "corrected_bridge_protocol_sha256",
        "--corrected-bridge-contract-sha256": "corrected_bridge_contract_sha256",
        "--corrected-bridge-application-sha256": "corrected_bridge_application_sha256",
        "--v25-publication-sha256": "v25_publication_sha256",
        "--v25-root-sha256": "v25_root_sha256",
        "--v26-publication-sha256": "v26_publication_sha256",
        "--v26-root-sha256": "v26_root_sha256",
        "--v27-publication-sha256": "v27_publication_sha256",
        "--v27-root-sha256": "v27_root_sha256",
    }
    authority = {"--root-authorized", "--frozen-committed-pushed"}
    options: dict[str, object] = {}
    index = 1
    while index < len(arguments):
        flag = arguments[index]
        if flag in authority:
            require(flag not in options, "reject repeated actual root authorization")
            options[flag] = True
            index += 1
            continue
        require(flag in scalar and scalar[flag] not in options
                and index + 1 < len(arguments),
                "reject missing, repeated, or foreign actual build authority")
        value = arguments[index + 1]
        options[scalar[flag]] = (int(value) if flag.endswith("-bytes") else value)
        index += 2
    require(set(options) == set(scalar.values()) | authority,
            "explicitly pin every source owner, overlay, predecessor, and pushed commit")
    for field in scalar.values():
        if field.endswith("sha256"):
            checked_sha(options[field], field)
    for field in ("frozen_commit", "pushed_commit"):
        value = options[field]
        require(type(value) is str and len(value) == 40
                and all(item in "0123456789abcdef" for item in value),
                "require independently checked exact pushed commit authority")
    require(options["frozen_commit"] == options["pushed_commit"]
            and options["label"] == LABEL
            and options["workspace_sha256"] == WORKSPACE_SHA
            and options["workspace_bytes"] == WORKSPACE_BYTES
            and options["search_sha256"] == CANONICAL_SEARCH_SHA
            and options["bridge_sha256"] == CORRECTED_BRIDGE_SHA
            and options["bridge_bytes"] == CORRECTED_BRIDGE_BYTES
            and options["adapter_sha256"] == CORRECTED_ADAPTER_SHA
            and options["adapter_bytes"] == CORRECTED_ADAPTER_BYTES
            and options["workspace_source_sha256"] == ROW_BY_ROLE["workspace_source"][2]
            and options["workspace_protocol_sha256"] == ROW_BY_ROLE["workspace_protocol"][2]
            and options["workspace_contract_sha256"] == ROW_BY_ROLE["workspace_contract"][2]
            and options["workspace_application_sha256"] == ROW_BY_ROLE["workspace_application"][2]
            and options["corrected_bridge_source_sha256"]
            == ROW_BY_ROLE["corrected_bridge_source"][2]
            and options["corrected_bridge_protocol_sha256"]
            == ROW_BY_ROLE["corrected_bridge_protocol"][2]
            and options["corrected_bridge_contract_sha256"]
            == ROW_BY_ROLE["corrected_bridge_contract"][2]
            and options["corrected_bridge_application_sha256"]
            == ROW_BY_ROLE["corrected_bridge_application"][2]
            and options["v25_publication_sha256"] == V25_PUBLICATION_SHA
            and options["v25_root_sha256"] == V25_ROOT_SHA
            and options["v26_publication_sha256"] == V26_PUBLICATION_SHA
            and options["v26_root_sha256"] == V26_ROOT_SHA
            and options["v27_publication_sha256"] == V27_PUBLICATION_SHA
            and options["v27_root_sha256"] == V27_ROOT_SHA,
            "reject an unpushed source triple or substituted actual V29 build lineage")
    return {"mode": mode, "options": options}


def actual_owner(path: str, fingerprint: str, size: int, device: int,
                 inode: int, uid: int, *, executable: bool) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode) and info.st_dev == device
                and info.st_ino == inode and info.st_uid == uid
                and info.st_size == size and info.st_nlink == 1
                and (stat.S_IMODE(info.st_mode) == 0o755 if executable
                     else stat.S_IMODE(info.st_mode) == 0o600),
                "reject changed independently pinned actual tool/source: " + path)
        blocks = []
        while True:
            item = os.read(descriptor, 65536)
            if not item:
                break
            blocks.append(item)
        raw = b"".join(blocks)
        require(len(raw) == size and digest(raw) == fingerprint,
                "reject an altered actual tool/source SHA-256: " + path)
        return raw
    finally:
        os.close(descriptor)


def exclusive_write(path: str, raw: bytes, mode: int = 0o600) -> dict:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | os.O_CLOEXEC | os.O_NOFOLLOW, mode)
    try:
        offset = 0
        while offset < len(raw):
            count = os.write(descriptor, raw[offset:])
            require(type(count) is int and count > 0,
                    "completely materialize one exclusive private first-party owner")
            offset += count
        os.fsync(descriptor)
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == mode
                and info.st_uid == os.geteuid() and info.st_nlink == 1
                and info.st_size == len(raw),
                "reject an exchanged or incomplete exclusively materialized owner")
        return {"path": path, "sha256": digest(raw), "bytes": len(raw),
                "device": info.st_dev, "inode": info.st_ino,
                "mode": format(mode, "04o"), "nlink": info.st_nlink,
                "uid": info.st_uid}
    finally:
        os.close(descriptor)


def mkdir_private(path: str) -> None:
    os.mkdir(path, 0o700)
    info = os.lstat(path)
    require(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700
            and info.st_uid == os.geteuid(),
            "reject a shared, linked, or substituted fresh private phase")


def process(name: str, command: list[str], cwd: str,
            environment: dict[str, str], seen: set[int]) -> dict:
    require(name in PROCESS_NAMES and command[0] in (READELF, GCC, RUSTC, CARGO),
            "execute only one pinned compiler or readelf process role")
    output_read, output_write = os.pipe2(os.O_CLOEXEC)
    old_cwd = os.open(ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.chdir(cwd)
        try:
            actions = (
                (os.POSIX_SPAWN_DUP2, output_write, 1),
                (os.POSIX_SPAWN_DUP2, output_write, 2),
                (os.POSIX_SPAWN_CLOSE, output_read),
                (os.POSIX_SPAWN_CLOSE, output_write),
            )
            pid = os.posix_spawn(command[0], command, environment,
                                 file_actions=actions)
        finally:
            os.fchdir(old_cwd)
        os.close(output_write)
        output_write = -1
        blocks: list[bytes] = []
        count = 0
        while True:
            chunk = os.read(output_read, 65536)
            if not chunk:
                break
            count += len(chunk)
            require(count <= MAX_PROCESS_OUTPUT_BYTES,
                    "reject excessive or noncompiler child process output")
            blocks.append(chunk)
        waited, result = os.waitpid(pid, 0)
        output = b"".join(blocks)
        require(waited == pid and pid not in seen and os.WIFEXITED(result)
                and os.WEXITSTATUS(result) == 0,
                "require a distinct successfully completed real compiler role: " + name
                + ": " + output[:1024].decode("utf-8", "backslashreplace"))
        seen.add(pid)
        return {"name": name, "phase": cwd.rsplit("/", 1)[-1], "pid": pid,
                "exit_status": 0,
                "working_directory": "<FRESH_PRIVATE_TMP>/" + cwd.rsplit("/", 1)[-1],
                "output_bytes": len(output), "output_sha256": digest(output),
                "output": output}
    finally:
        if output_write >= 0:
            os.close(output_write)
        os.close(output_read)
        os.close(old_cwd)


def read_private(path: str) -> tuple[bytes, os.stat_result]:
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
                and before.st_uid == os.geteuid() and 0 < before.st_size <= 8_388_608,
                "authenticate an exclusively created complete private ELF")
        chunks = []
        while True:
            block = os.read(descriptor, 65536)
            if not block:
                break
            chunks.append(block)
        raw = b"".join(chunks)
        require(len(raw) == before.st_size and raw.startswith(b"\x7fELF"),
                "reject substituted, truncated, or non-ELF private native output")
        return raw, before
    finally:
        os.close(descriptor)


def phase_commands(root: str, phase: str) -> tuple[dict, dict, dict]:
    base = root + "/" + phase
    source = base + "/source"
    native = base + "/native"
    target = base + "/target"
    prefixes = ["-ffile-prefix-map=" + root + "/" + peer + "/source=" + PREFIX_MAP
                for peer in PHASES]
    rustflags = " ".join("--remap-path-prefix=" + root + "/" + peer
                         + "/source=" + PREFIX_MAP for peer in PHASES)
    rustflags += " -Clink-arg=-Wl,-soname,_rust_engine.so"
    environment = {"PATH": RUST_TOOLCHAIN + "/bin:/usr/bin:/bin",
                   "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
                   "SOURCE_DATE_EPOCH": "1", "TMPDIR": base + "/temporary",
                   "CARGO_HOME": base + "/cargo-home", "CARGO_NET_OFFLINE": "true",
                   "CARGO_INCREMENTAL": "0", "CARGO_BUILD_JOBS": "1",
                   "RUSTC": RUSTC, "RUSTFLAGS": rustflags}
    engine = native + "/" + ENGINE_NAME
    bridge = native + "/" + BRIDGE_NAME
    commands = {
        "readelf_version": [READELF, "--version"],
        "gcc_version": [GCC, "--version"],
        "rustc_version": [RUSTC, "--version", "--verbose"],
        "cargo_version": [CARGO, "--version"],
        "build_rust_engine": [CARGO, "build", "--manifest-path",
                              source + "/candidates/rust/Cargo.toml", "--release",
                              "--locked", "--offline", "--frozen", "--target-dir", target],
        "build_rust_bridge": [GCC, "-pthread", "-std=c11", "-shared", "-fPIC", "-O3",
                               "-Wall", "-Wextra", "-Werror", "-Wl,-z,noexecstack",
                               "-Wl,--exclude-libs,ALL", "-Wl,--build-id=sha1",
                               *prefixes, "-I" + PYTHON_INCLUDE,
                               source + "/candidates/rust/py_bridge.c", "-L" + native,
                               "-l:_rust_engine.so", "-Wl,-rpath,$ORIGIN", "-o", bridge],
        "engine_dynamic": [READELF, "--dynamic", "--wide", engine],
        "engine_symbols": [READELF, "--dyn-syms", "--wide", engine],
        "bridge_dynamic": [READELF, "--dynamic", "--wide", bridge],
        "bridge_symbols": [READELF, "--dyn-syms", "--wide", bridge],
        "engine_sections": [READELF, "--sections", "--wide", engine],
        "engine_notes": [READELF, "--notes", "--wide", engine],
        "bridge_sections": [READELF, "--sections", "--wide", bridge],
        "bridge_notes": [READELF, "--notes", "--wide", bridge],
    }
    return commands, environment, {"base": base, "source": source,
                                    "native": native, "target": target,
                                    "engine": engine, "bridge": bridge}


def materialize_phase(root: str, phase: str, state: dict,
                      all_inodes: set[tuple[int, int]]) -> dict:
    _commands, _environment, paths = phase_commands(root, phase)
    base, source = paths["base"], paths["source"]
    for path in (base, source, source + "/candidates", source + "/candidates/rust",
                 source + "/candidates/rust/src", paths["native"], paths["target"],
                 base + "/temporary", base + "/cargo-home"):
        mkdir_private(path)
    canonical = (
        ("candidates/rust/Cargo.lock", "first_party_cargo_lock"),
        ("candidates/rust/Cargo.toml", "first_party_cargo_manifest"),
        ("candidates/rust/py_bridge.c", "canonical_bridge"),
        ("candidates/rust/src/lib.rs", "first_party_rust_vm"),
        ("candidates/rust/src/newline.rs", "canonical_newline"),
        ("candidates/rust/src/search.rs", "first_party_rust_search"),
        ("candidates/rust/src/stack.rs", "first_party_rust_inline_stack"),
        ("candidates/rust/src/unicode_tables.rs", "canonical_unicode"),
        ("candidates/rust_candidate.py", "canonical_adapter"),
    )
    sources = {}
    for relative, role in canonical:
        content = state["payload"][role]
        overlay = None
        if role == "first_party_rust_vm":
            content, overlay = state["workspace_variant"], "workspace-reuse"
        elif role == "canonical_bridge":
            content, overlay = state["corrected_bridge"], "no-external-introspection"
        elif role == "canonical_adapter":
            content, overlay = state["corrected_adapter"], "corrected-public-adapter"
        identity = exclusive_write(source + "/" + relative, content)
        key = (identity["device"], identity["inode"])
        require(key not in all_inodes,
                "reject a borrowed or hard-linked private source across phases")
        all_inodes.add(key)
        identity["path"] = relative
        if overlay is not None:
            identity["source_overlay"] = {
                "phase": phase, "kind": overlay, "source_apply_count": 1,
                "derived_sha256": digest(content), "derived_bytes": len(content),
            }
        sources[relative] = identity
    require(len(sources) == 9
            and sum("source_overlay" in value for value in sources.values()) == 3
            and sources["candidates/rust/src/search.rs"]["sha256"] == CANONICAL_SEARCH_SHA,
            "retain six exact canonical owners and three exact private source overlays")
    return {"name": phase, "fresh_source_owners": sources, "paths": paths}


def actual_document(module: types.ModuleType, value: dict) -> bytes:
    return module.document(value)


def publish(path: str, raw: bytes) -> dict:
    allowed = ROOT + "/oracle/phase2/evidence/"
    require(path.startswith(allowed) and "/" not in path[len(allowed):]
            and path.endswith(".json"),
            "publish exclusively one exact V29 plaintext evidence receipt")
    identity = exclusive_write(path, raw)
    directory = os.open(allowed[:-1], os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    identity["path"] = path[len(ROOT) + 1:]
    identity["directory_fsync_completed"] = True
    identity["file_fsync_completed"] = True
    identity["exclusive_creation"] = True
    return identity


def actual_build(options: dict) -> dict:
    require(options["--root-authorized"] is True
            and options["--frozen-committed-pushed"] is True,
            "actual build requires explicit root and committed/pushed authority")
    wall = SourceWall(source_mode=False)
    pins = {"--source-sha256": options["source_sha256"],
            "--protocol-sha256": options["protocol_sha256"],
            "--contract-sha256": options["contract_sha256"]}
    frozen, state = load_context(wall, pins, render=False)
    for path, fingerprint, length, device, inode, uid in TOOLCHAIN:
        actual_owner(path, fingerprint, length, device, inode, uid, executable=True)
    root = "/tmp/" + ROOT_PREFIX + os.urandom(12).hex()
    mkdir_private(root)
    process_ids: set[int] = set()
    source_inodes: set[tuple[int, int]] = set()
    phases = [materialize_phase(root, phase, state, source_inodes) for phase in PHASES]
    require(len(source_inodes) == 18, "require 18 distinct private first-party source owners")
    outputs: list[dict] = []
    steps: list[dict] = []
    for phase in phases:
        commands, environment, paths = phase_commands(root, phase["name"])
        records = {}
        for role in PROCESS_NAMES:
            row = process(role, commands[role], paths["base"], environment, process_ids)
            output = row.pop("output")
            records[role] = output
            if role == "build_rust_engine":
                cargo_engine, _info = read_private(
                    paths["target"] + "/release/librebar_rust_continuation.so")
                exclusive_write(paths["engine"], cargo_engine)
            steps.append(row)
        require(b"_rust_engine.so" in records["engine_dynamic"]
                and b"_rust_engine.so" in records["bridge_dynamic"]
                and b"$ORIGIN" in records["bridge_dynamic"]
                and b"rebar_match" in records["engine_symbols"]
                and b"rebar_match" in records["bridge_symbols"],
                "authenticate genuine first-party ELF SONAME, RPATH, and matching exports")
        for report in records.values():
            require(not any(item in report.lower()
                            for item in (b"libpcre", b"libonig", b"libre2", b"libregex")),
                    "reject a cross-candidate or external regex native dependency")
        engine, engine_info = read_private(paths["engine"])
        bridge, bridge_info = read_private(paths["bridge"])
        outputs.append({
            "engine": {"sha256": digest(engine), "size_bytes": len(engine),
                       "device": engine_info.st_dev, "inode": engine_info.st_ino,
                       "file_name": ENGINE_NAME, "_bytes": engine},
            "bridge": {"sha256": digest(bridge), "size_bytes": len(bridge),
                       "device": bridge_info.st_dev, "inode": bridge_info.st_ino,
                       "file_name": BRIDGE_NAME, "_bytes": bridge},
        })
    require(len(process_ids) == 28 and len(steps) == 28
            and all(outputs[0][role]["_bytes"] == outputs[1][role]["_bytes"]
                    for role in ("engine", "bridge"))
            and outputs[0]["engine"]["sha256"]
            not in {state["history"]["first_party_builds"][version]["actual_engine_sha256"]
                    for version in ("v25", "v26", "v27")},
            "require two genuine byte-identical V29 native outputs and 28 distinct roles")
    clean_outputs = {role: {key: value for key, value in outputs[0][role].items()
                            if key != "_bytes"}
                     for role in ("engine", "bridge")}
    for phase in phases:
        phase.pop("paths")
    publication = {
        "schema": SCHEMA + "-durable-publication-receipt", "version": VERSION,
        "status": "PASS", "build_status": "PASS", "family": FAMILY,
        "label": LABEL, "source_sha256": options["source_sha256"],
        "protocol_sha256": options["protocol_sha256"],
        "contract_sha256": options["contract_sha256"],
        "frozen_commit": options["frozen_commit"],
        "actual_completed_phase_count": 2, "actual_compiler_process_count": 28,
        "actual_compiler_process_ids": sorted(process_ids),
        "workspace_source_sha256": WORKSPACE_SHA,
        "canonical_original_search_sha256": CANONICAL_SEARCH_SHA,
        "corrected_bridge_source_sha256": CORRECTED_BRIDGE_SHA,
        "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA,
        "cross_phase_complete_engine_elf_byte_identical": True,
        "cross_phase_complete_bridge_elf_byte_identical": True,
        "native_outputs": clean_outputs,
        "external_cargo_dependency_count": 0,
        "latest_v25_candidate_status": "FAIL",
        "latest_v25_semantic_mismatch_count": 1352,
        "latest_v25_case_execution_denominator": 31237,
        "latest_v25_suite_count": 13,
        "historical_runtime_audit_v4_status": "FAIL",
        "historical_runtime_audit_v4_finding_count": 1,
        "new_runtime_non_delegation_audit": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_executions": 0, "candidate_imports": 0,
        "candidate_workers_started": 0, "native_libraries_loaded": 0,
        "clock_samples": 0, "network_requests": 0,
        "hidden_cases_generated": 0, "hidden_cases_opened": 0,
        "historical_final_content_open_count": 0,
        "current_final_holdout_status": FINAL_HOLDOUT_STATUS,
        "candidate_correctness": NOT_MEASURED, "performance": NOT_MEASURED,
        "memory": NOT_MEASURED, "candidate_qualified": False,
        "winner_selected": False,
    }
    publication_path = ROOT + "/oracle/phase2/evidence/native-source-build-v29-rust-" \
        + LABEL + "-publication-receipt.json"
    publication_owner = publish(publication_path,
                                actual_document(state["workspace_module"], publication))
    root_info = os.lstat(root)
    root_document = {
        "schema": SCHEMA + "-durable-root-provenance-receipt", "version": VERSION,
        "status": "PASS", "canonical_build_status": "PASS", "family": FAMILY,
        "label": LABEL, "source_sha256": options["source_sha256"],
        "protocol_sha256": options["protocol_sha256"],
        "contract_sha256": options["contract_sha256"],
        "canonical_build_receipt_sha256": publication_owner["sha256"],
        "root": {"path": root, "device": root_info.st_dev,
                 "inode": root_info.st_ino, "mode": "0700"},
        "actual_source_phase_count": 2, "actual_compiler_process_count": 28,
        "actual_compiler_process_ids": sorted(process_ids),
        "actual_reproduced_native_outputs": clean_outputs,
        "private_source_phases": phases, "actual_compiler_steps": steps,
        "workspace_source_sha256": WORKSPACE_SHA,
        "canonical_original_search_sha256": CANONICAL_SEARCH_SHA,
        "corrected_bridge_source_sha256": CORRECTED_BRIDGE_SHA,
        "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA,
        "cross_phase_complete_engine_elf_byte_identical": True,
        "cross_phase_complete_bridge_elf_byte_identical": True,
        "external_cargo_dependency_count": 0,
        "candidate_executions": 0, "candidate_imports": 0,
        "candidate_workers_started": 0, "native_libraries_loaded": 0,
        "clock_samples": 0, "network_requests": 0,
        "hidden_cases_generated": 0, "hidden_cases_opened": 0,
        "historical_final_content_open_count": 0,
        "current_final_holdout_status": FINAL_HOLDOUT_STATUS,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_correctness": NOT_MEASURED, "performance": NOT_MEASURED,
        "memory": NOT_MEASURED, "candidate_qualified": False,
        "winner_selected": False,
    }
    root_path = ROOT + "/oracle/phase2/evidence/native-source-build-v29-rust-" \
        + LABEL + "-root-provenance-receipt.json"
    root_owner = publish(root_path, actual_document(state["workspace_module"], root_document))
    return {"schema": SCHEMA + "-root-authorized-actual-build", "status": "PASS",
            "family": FAMILY, "label": LABEL, "actual_completed_phase_count": 2,
            "actual_compiler_process_count": 28,
            "actual_publication_receipt": publication_owner,
            "actual_root_receipt": root_owner, "native_outputs": clean_outputs,
            "candidate_executions": 0, "candidate_correctness": NOT_MEASURED,
            "current_final_holdout_status": FINAL_HOLDOUT_STATUS,
            "hidden_cases_generated": 0, "hidden_cases_opened": 0,
            "winner_selected": False}


def source_result(choice: dict, wall: SourceWall, state: dict, checks: list[str]) -> dict:
    return {"schema": SCHEMA + "-source-only-gate", "version": VERSION,
            "status": "PASS", "mode": choice["mode"].removeprefix("--"),
            "source_sha256": choice["pins"]["--source-sha256"],
            "protocol_sha256": choice["pins"]["--protocol-sha256"],
            "contract_sha256": choice["pins"]["--contract-sha256"],
            "authenticated_first_party_owner_count": len(ROW_BY_PATH),
            "workspace_variant_sha256": WORKSPACE_SHA,
            "workspace_variant_bytes": WORKSPACE_BYTES,
            "original_search_source_sha256": CANONICAL_SEARCH_SHA,
            "corrected_no_external_introspection_bridge_sha256": CORRECTED_BRIDGE_SHA,
            "corrected_no_external_introspection_bridge_bytes": CORRECTED_BRIDGE_BYTES,
            "corrected_public_adapter_sha256": CORRECTED_ADAPTER_SHA,
            "corrected_public_adapter_bytes": CORRECTED_ADAPTER_BYTES,
            "actual_workspace_application_receipt_sha256":
                ROW_BY_ROLE["workspace_application"][2],
            "actual_corrected_bridge_application_receipt_sha256":
                ROW_BY_ROLE["corrected_bridge_application"][2],
            "actual_v25_publication_receipt_sha256": V25_PUBLICATION_SHA,
            "actual_v26_publication_receipt_sha256": V26_PUBLICATION_SHA,
            "actual_v27_publication_receipt_sha256": V27_PUBLICATION_SHA,
            "actual_v25_candidate_status": "FAIL",
            "actual_v25_semantic_mismatch_count": 1352,
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "public_practice_case_count": 416,
            "public_paired_observation_count": 1664,
            "exact_guard_repeat_allocation_target_count": 408,
            "exact_guard_repeat_allocation_target_bytes": 120768,
            "exact_capture_undo_allocation_count": 576,
            "historical_runtime_audit_v4_status": "FAIL",
            "historical_runtime_audit_v4_finding_count": 1,
            "historical_proposal_metadata_probe_count": wall.metadata_probes,
            "historical_proposal_content_open_count": wall.proposal_open_count,
            "historical_proposal_trust_status": "COMPROMISED; RETIRED",
            "current_final_holdout_status": FINAL_HOLDOUT_STATUS,
            "rekeyed_successor_required": True,
            "hidden_cases_generated": 0, "hidden_cases_opened": 0,
            "candidate_executions": 0, "candidate_imports": 0,
            "candidate_workers_started": 0, "compiler_processes_started": 0,
            "native_files_opened": 0, "native_libraries_loaded": 0,
            "clock_samples": 0, "network_requests": 0,
            "filesystem_writes": 0, "broad_filesystem_enumerations": 0,
            "private_roots_opened": 0, "compressed_archives_opened": 0,
            "hostile_control_count": len(checks), "hostile_controls": checks,
            "physically_blocked_effects": dict(wall.blocked),
            "native_build": "NOT RUN", "candidate_correctness": NOT_MEASURED,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": NOT_MEASURED, "memory": NOT_MEASURED,
            "qualified_candidate_count": 0, "winner_selected": False}


def main(arguments: list[str] | None = None) -> int:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PYTHON and sys.flags.isolated == 1
            and sys.flags.no_site == 1 and sys.dont_write_bytecode is True,
            "require exact independently pinned CPython 3.14.6 with -I -B -S")
    no_matching_imports()
    choice = parse(list(sys.argv[1:] if arguments is None else arguments))
    if choice["mode"] in ACTUAL_MODES:
        result = actual_build(choice["options"])
        # Source module loaded during actual preflight supplies deterministic JSON.
        module = sys.modules["_rebar_v29_authenticated_workspace_source"]
        sys.stdout.buffer.write(module.document(result))
        sys.stdout.buffer.flush()
        return 0

    wall = SourceWall(source_mode=True)
    wall.install()
    frozen, state = load_context(wall, choice["pins"],
                                 render=choice["mode"] == "--render-contract")
    module = state["workspace_module"]
    if choice["mode"] == "--render-contract":
        sys.stdout.buffer.write(module.document(frozen))
        sys.stdout.buffer.flush()
        return 0
    checks = self_test(wall, state) if choice["mode"] == "--self-test" else []
    require(not wall.live and wall.metadata_probes == 1,
            "leave no live source descriptors and preserve one metadata-only probe")
    sys.stdout.buffer.write(module.document(source_result(choice, wall, state, checks)))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildFreezeError, ValueError, OSError) as error:
        sys.stderr.write("V29 Rust workspace source-build rejected: " + str(error) + "\n")
        raise SystemExit(2)
