#!/usr/bin/env python3
"""Freeze the separately root-authorized complete Rust original campaign.

Every source-only mode installs an irreversible public-plaintext-only wall
before its first predecessor read.  The complete actual V25 FAIL-1352 and the
future genuinely published V33 native-build receipts are authenticated without
opening a private root, native object, archive, retired proposal, or clock.
Only a separately committed, pushed, explicitly root-authorized actual mode
may migrate the exact original 13-suite, four-owner recoverable controller.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("a first-party Rust original campaign cannot start with a matcher")

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
SOURCE = "tools/run_owned_repaired_rust_original_campaign_v29.py"
PROTOCOL = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V29.md"
CONTRACT = "oracle/phase2/repaired-rust-original-campaign-v29.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v29"
VERSION = 29
FAMILY = "rust"
NOT_MEASURED = "NOT MEASURED"
FINAL_HOLDOUT_STATUS = "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
GOAL_SHA = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
MAX_OWNER_BYTES = 2 * 1024 * 1024
CASE_COUNT = 31_237
WORKER_COUNT = 13
SUPPLEMENTAL_CASE_COUNT = 8_244
CORRECTED_REFERENCE_CASE_COUNT = 6_912
HISTORICAL_HOLDOUT_CASE_COUNT = 141_557_760
BUILD_LABEL = "phase2-v35-rust-optimized-safe-source-root-provenance"
BUILD_SUFFIX = BUILD_LABEL + "-original-p0"
LABEL = BUILD_SUFFIX + "-v29"
RECOVERY_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v29-"
RECOVERY_ROOT = "/tmp/" + RECOVERY_PREFIX + BUILD_SUFFIX
LOCK_NAME = "recoverable-controller-v29.lock"
BRIDGE_SOURCE_SHA = (
    "c9b22c4443c36cc6e653af18fcd829561b7987df312368b30dfcbade254538f8"
)
BRIDGE_SOURCE_BYTES = 182_459
ADAPTER_SHA = "f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227"
ADAPTER_BYTES = 34_039
ENGINE_SOURCE_SHA = (
    "7ec7dc9815bec10c3149123ddc5045f575c3cd45731531bd81e0b888362a9136"
)
ENGINE_SOURCE_BYTES = 194_276
SEARCH_SOURCE_SHA = (
    "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7"
)
SEARCH_SOURCE_BYTES = 24_305
HISTORICAL_V25_ENGINE_SHA = (
    "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
)
HISTORICAL_V25_ADAPTER_SHA = (
    "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
)
HISTORICAL_V25_ADAPTER_BYTES = 31_934

PREVIOUS = (
    ("previous_v25_source", "tools/run_owned_repaired_rust_original_campaign_v25.py",
     "09074713ee068a01dc91c07db68a7efcd4500f9b92990699f5e849fa77410edc",
     100_824, 430716),
    ("previous_v25_protocol", "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V25.md",
     "9a2d0a3a71e998750cc6213a7ad4c42c6a8bf8a022347af55723d2407aa345e1",
     5_638, 526197),
    ("previous_v25_contract", "oracle/phase2/repaired-rust-original-campaign-v25.json",
     "230e4c98914b0ca2b1d4bc55eb9d7cf38474eed835626c2639916bd4ed581c1a",
     57_478, 526253),
)
PREVIOUS_FAILURE = (
    "previous_v25_complete_actual_failure",
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-"
    "failures-publication-receipt.json",
    "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59",
    11_832, 524846,
)
ORIGINAL_V26 = (
    ("previous_v26_source", "tools/run_owned_repaired_rust_original_campaign_v26.py",
     "37d3edd69f93c33defaaeb8a1473e39b0563f06af57e6038340679dd8c61091d",
     97_746, 431629),
    ("previous_v26_protocol", "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V26.md",
     "aefd84daf141fc92e73c6fedec82a9c179b9d67db6f67f93bcaf6d8cca40b42d",
     7_501, 526047),
    ("previous_v26_contract", "oracle/phase2/repaired-rust-original-campaign-v26.json",
     "8493afcb087e79b0b2419711746fb82dd5c09785fe086fa627ea99af41365eaa",
     22_874, 526048),
)
ORIGINAL_V26_PASS = (
    "previous_v26_complete_actual_pass",
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v30-rust-complete-semantic-source-root-provenance-"
    "original-p0-v26-publication-receipt.json",
    "84804409997794ce7e8bfff67ca8ffdcada9651a1660bda2654742befbba20f5",
    12_055, 525046,
)
PUBLIC_V5 = (
    ("full_public_v5_source", "tools/run_owned_rust_full_public_correctness_v5.py",
     "97d36e9448336d3cfa732324779c14959bf739a8e6daa556d839e0ecdd0d0602",
     83_637, 430313),
    ("full_public_v5_protocol", "oracle/phase2/RUST-FULL-PUBLIC-CORRECTNESS-V5.md",
     "066f3e4663bb19612b795f797144c0098bf2d998455d3c0b4c814186d0204bd0",
     6_570, 525361),
    ("full_public_v5_contract", "oracle/phase2/rust-full-public-correctness-v5.json",
     "fd10e77356945e7544d5b5b91d7a95f95c173384e152506e02c11240b58eb52c",
     31_041, 525365),
)
PUBLIC_V5_PASS = (
    "full_public_v5_complete_actual_pass",
    "oracle/phase2/evidence/rust-full-public-correctness-v5-"
    "v33-full-public-v5-run-001-publication-receipt.json",
    "8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9",
    6_889, 525451,
)
FAILED_V27 = (
    ("previous_v27_source", "tools/run_owned_repaired_rust_original_campaign_v27.py",
     "c01ef1d2c48b5fc2c7caa3c9db9d24e97dca4442359925d8b6659bc2768b861f",
     113_821, 430770),
    ("previous_v27_protocol", "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V27.md",
     "ae0874abd3c1f01d1bc1757d8993e652c790cf096091b651167f0a0891f01100",
     8_596, 525637),
    ("previous_v27_contract", "oracle/phase2/repaired-rust-original-campaign-v27.json",
     "8f9fa8126e655d949d9350bf308f9bcf67b62349182c44d00a02a6906597b9c0",
     26_545, 525944),
)
FAILED_V27_RECEIPT = (
    "previous_v27_complete_preactivation_failure",
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v27-preactivation-failure.json",
    "69b0561814db301bb67840af591b3cb52c662d073503950ffdc2a7ee86c7b2cb",
    328, 526061,
)

HISTORICAL_V33_BUILD_LABEL = (
    "phase2-v33-rust-full-public-semantic-source-root-provenance"
)
HISTORICAL_V33_BRIDGE_SOURCE_SHA = (
    "f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e"
)
HISTORICAL_V33_ENGINE_SOURCE_SHA = (
    "7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38"
)
HISTORICAL_V33_ENGINE_SHA = (
    "e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8"
)
HISTORICAL_V33_BRIDGE_SHA = (
    "ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000"
)
HISTORICAL_V33 = (
    ("historical_v33_source",
     "tools/reproduce_owned_rust_full_public_semantic_source_build_v33.py",
     "31251c3aa6006108ba1a5b5e7b5a07147d9b8ccf76123f4aa08ecffb20c91c63",
     172_881, 429226),
    ("historical_v33_protocol",
     "oracle/phase2/RUST-FULL-PUBLIC-SEMANTIC-SOURCE-BUILD-V33.md",
     "c73843e1705beb24e4ced9ab3d9fa95da7420c5d24cd8f6ffaeeb747aa382071",
     7_434, 524906),
    ("historical_v33_contract",
     "oracle/phase2/rust-full-public-semantic-source-build-v33.json",
     "bb7d338cb766b7f1ff52e616355d5d5cddb00849532e42755b31a9bf09119337",
     56_235, 525061),
    ("historical_v33_publication",
     "oracle/phase2/evidence/native-source-build-v33-rust-"
     "phase2-v33-rust-full-public-semantic-source-root-provenance-"
     "publication-receipt.json",
     "cfe1464e1e8ce96bfa514b15cf96879a0642686987159dd79c15f4d9db408749",
     6_696, 525066),
    ("historical_v33_root",
     "oracle/phase2/evidence/native-source-build-v33-rust-"
     "phase2-v33-rust-full-public-semantic-source-root-provenance-"
     "root-provenance-receipt.json",
     "7122c9bdff731be0f68602a4a216c1fa9700e6a78f9da9b534eeaef282c64c1c",
     80_421, 525067),
)
HISTORICAL_V33_ORIGINAL_PASS = (
    "historical_v33_original_pass",
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v33-rust-full-public-semantic-source-root-provenance-"
    "original-p0-v28-publication-receipt.json",
    "5204823a291ec01890913218582ff978cbe923dd5c787c8d6ae68a9790c43064",
    12_067, 526161,
)
HISTORICAL_V28_CAMPAIGN = (
    ("historical_v28_source",
     "tools/run_owned_repaired_rust_original_campaign_v28.py",
     "462cdd40dc2b9afea685327e882fbd53239e75c86b7f5bc4231e962c3c968f37",
     123_289, 430834),
    ("historical_v28_protocol",
     "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V28.md",
     "8252325bc228f26130cdc301ed06661a737ed70e0ecea42cb99ac1864be1ea55",
     9_768, 526094),
    ("historical_v28_contract",
     "oracle/phase2/repaired-rust-original-campaign-v28.json",
     "b049a76b4d8cb1501f65bdd724aab414d85c3516dc13825dd0d76d451db20683",
     29_027, 526114),
)
NATIVE_HANDLE_LEASE = (
    ("native_handle_lease_source",
     "tools/apply_owned_rust_native_handle_lease_v1.py",
     "5c52dfec219a24a19d2771d1f6eb72fc08ab2e339249e32f2a627de017ab9cd7",
     69_830, 431766),
    ("native_handle_lease_protocol",
     "oracle/phase2/RUST-NATIVE-HANDLE-LEASE-V1.md",
     "719fa00528b423132eea0856b9047ecbef4fbde55e80edcfa950f346655357ec",
     5_907, 526588),
    ("native_handle_lease_contract",
     "oracle/phase2/rust-native-handle-lease-v1.json",
     "78d053d7663481b00bd63d1a8dd0c6fba008c260d1b486622da5d465c7e88370",
     10_757, 526604),
    ("native_handle_lease_actual_application",
     "oracle/phase2/evidence/rust-native-handle-lease-v1-application.json",
     "8f3ad6bffcbbb2129a4a95bc12a0b9865b39f08d2c953ba5ce303a4a77743764",
     1_395, 526634),
)

BUILD_PATHS = (
    ("build_v35_source",
     "tools/reproduce_owned_rust_optimized_safe_source_build_v35.py"),
    ("build_v35_protocol",
     "oracle/phase2/RUST-OPTIMIZED-SAFE-SOURCE-BUILD-V35.md"),
    ("build_v35_contract",
     "oracle/phase2/rust-optimized-safe-source-build-v35.json"),
)
PUBLIC_RECEIPT_PATH = (
    "oracle/phase2/evidence/native-source-build-v35-rust-"
    + BUILD_LABEL + "-publication-receipt.json"
)
ROOT_RECEIPT_PATH = (
    "oracle/phase2/evidence/native-source-build-v35-rust-"
    + BUILD_LABEL + "-root-provenance-receipt.json"
)

# This is the exact public-only closure already authenticated by the immutable
# V25 campaign.  Candidate source, native targets, phase-three proposals, and
# compressed evidence are intentionally absent from the physical allowlist.
INHERITED_PUBLIC_PATHS = (
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
    "tools/run_owned_repaired_rust_original_campaign_v23.py",
    "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V23.md",
    "oracle/phase2/repaired-rust-original-campaign-v23.json",
    "tools/reproduce_owned_rust_capture_clamp_source_build_v25.py",
    "oracle/phase2/RUST-CAPTURE-CLAMP-SOURCE-BUILD-V25.md",
    "oracle/phase2/rust-capture-clamp-source-build-v25.json",
    "oracle/phase2/evidence/native-source-build-v25-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-publication-receipt.json",
    "oracle/phase2/evidence/native-source-build-v25-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-root-provenance-receipt.json",
    "tools/verify_owned_candidate_runtime_independence_v4.py",
    "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md",
    "oracle/phase2/candidate-runtime-independence-v4.json",
    "tools/run_owned_repaired_rust_original_campaign_v24.py",
    "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V24.md",
    "oracle/phase2/repaired-rust-original-campaign-v24.json",
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v24-rust-capture-shape-v2-root-provenance-"
    "original-p0-v24-failures-publication-receipt.json",
    "tools/audit_candidate_runtime_non_delegation_v4.py",
    "oracle/phase2/RUNTIME-NON-DELEGATION-V4.md",
    "oracle/phase2/runtime-non-delegation-v4.json",
    "oracle/phase2/evidence/runtime-non-delegation-v4-actual-source-audit-failure.json",
    *(row[1] for row in ORIGINAL_V26), ORIGINAL_V26_PASS[1],
    *(row[1] for row in PUBLIC_V5), PUBLIC_V5_PASS[1],
    *(row[1] for row in FAILED_V27), FAILED_V27_RECEIPT[1],
    *(row[1] for row in HISTORICAL_V33), HISTORICAL_V33_ORIGINAL_PASS[1],
    *(row[1] for row in HISTORICAL_V28_CAMPAIGN),
    *(row[1] for row in NATIVE_HANDLE_LEASE),
)

SOURCE_MODES = ("--render-contract", "--verify-frozen-context", "--self-test")
ACTUAL_MODES = ("--run", "--worker", "--recover")
V35_PIN_NAMES = (
    "v35_source_sha256", "v35_protocol_sha256", "v35_contract_sha256",
    "v35_publication_sha256", "v35_root_sha256",
)
GUARD_PIN_NAMES = (
    "guard_v4_source_sha256", "guard_v4_protocol_sha256",
    "guard_v4_contract_sha256",
)


class CampaignError(Exception):
    """A frozen source, real predecessor, native identity, or guard changed."""


def need(condition: object, message: str) -> None:
    if condition is not True:
        raise CampaignError(message)


def sha(raw: bytes) -> str:
    need(type(raw) is bytes, "hash only complete authenticated public bytes")
    return hashlib.sha256(raw).hexdigest()


def sha_pin(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(character in "0123456789abcdef" for character in value),
         "require an independent complete SHA-256: " + label)
    assert isinstance(value, str)
    return value


def no_matching_imports() -> None:
    forbidden = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                 "ctypes", "candidates", "socket", "subprocess",
                 "concurrent.interpreters")
    need(not any(name == root or name.startswith(root + ".")
                 for name in sys.modules for root in forbidden),
         "reject stdlib, indirect, external, or cross-candidate matching")


def verify_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.executable == PYTHON and sys.flags.isolated == 1
         and sys.flags.no_site == 1 and sys.dont_write_bytecode is True,
         "require the exact isolated CPython 3.14.6 with -I -B -S")
    no_matching_imports()


class PublicSourceWall:
    """Irreversibly permit only exact public plaintext and live descriptors."""

    def __init__(self) -> None:
        relatives = (
            SOURCE, PROTOCOL, CONTRACT, *INHERITED_PUBLIC_PATHS,
            *(row[1] for row in PREVIOUS), PREVIOUS_FAILURE[1],
            *(row[1] for row in BUILD_PATHS),
            PUBLIC_RECEIPT_PATH, ROOT_RECEIPT_PATH,
        )
        self.allowed = frozenset(ROOT + "/" + relative for relative in relatives)
        need(all(not path.endswith((".gz", ".so"))
                 and not path.startswith((ROOT + "/candidates/",
                                          ROOT + "/oracle/phase3/"))
                 for path in self.allowed),
             "never grant candidate, native, archive, or final-proposal access")
        self.live: set[int] = set()
        self.blocked: dict[str, int] = {}
        self.installed = False
        self.error_type: type[Exception] = CampaignError
        self.native_open, self.native_read = os.open, os.read
        self.native_fstat, self.native_close = os.fstat, os.close

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise self.error_type("V29 public-source wall rejected " + category)

    def approved(self, path: object) -> bool:
        return (type(path) is str and path.startswith(ROOT + "/")
                and path == os.path.normpath(path)
                and not any(part in (".", "..") for part in path.split("/"))
                and path in self.allowed and not path.endswith((".gz", ".so"))
                and not path.startswith((ROOT + "/candidates/",
                                         ROOT + "/oracle/phase3/"))
                and "holdout" not in path.lower()
                and "benchmark" not in path.lower())

    def audit(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            flags = arguments[2] if len(arguments) > 2 else None
            mutation = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                        | os.O_APPEND | getattr(os, "O_TMPFILE", 0))
            if (not self.approved(path) or type(flags) is not int
                    or flags & mutation
                    or not flags & getattr(os, "O_NOFOLLOW", 0)
                    or type(mode) is str and any(item in mode for item in "wax+")):
                self.deny("unowned-direct-file-open")
            return
        if event in ("exec", "compile"):
            item = arguments[0] if arguments else None
            filename = (getattr(item, "co_filename", None) if event == "exec"
                        else arguments[1] if len(arguments) > 1 else None)
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

    def forbidden(self, category: str):
        def blocked(*_arguments: object, **_keywords: object) -> object:
            self.deny(category)
        return blocked

    def guarded_open(self, path: object, flags: object, mode: int = 0o777,
                     *, dir_fd: object = None) -> int:
        mutation = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                    | os.O_APPEND | getattr(os, "O_TMPFILE", 0)
                    | getattr(os, "O_DIRECTORY", 0))
        if (not self.approved(path) or type(flags) is not int
                or flags & mutation or dir_fd is not None
                or not flags & getattr(os, "O_NOFOLLOW", 0)):
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
        need(self.installed is False, "reject a reused V29 deny-default source wall")
        sys.addaudithook(self.audit)
        builtins.open = self.forbidden("builtins-open")
        _io.open = self.forbidden("direct-_io-open")
        _io.FileIO = self.forbidden("direct-_io-fileio")
        io.open = self.forbidden("direct-io-open")
        io.FileIO = self.forbidden("direct-io-fileio")
        for module in (_io, io):
            if hasattr(module, "open_code"):
                module.open_code = self.forbidden("direct-open-code")
        os.open, os.read = self.guarded_open, self.guarded_read
        os.fstat, os.close = self.guarded_fstat, self.guarded_close
        for name in ("fdopen", "dup", "dup2", "stat", "lstat", "readlink",
                     "listdir", "scandir", "walk", "fwalk", "access", "fork",
                     "posix_spawn", "posix_spawnp", "system", "mkdir",
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


def secure_owner(wall: PublicSourceWall | None, row: tuple) -> bytes:
    need(type(row) is tuple and len(row) == 5,
         "require one completely pinned public first-party owner")
    role, relative, fingerprint, size, inode = row
    need(type(role) is str and type(relative) is str
         and not relative.startswith("/") and ".." not in relative.split("/")
         and type(size) is int and 0 < size <= MAX_OWNER_BYTES
         and type(inode) is int and inode > 0,
         "reject private, unbounded, or incomplete public owner: " + str(role))
    sha_pin(fingerprint, role)
    absolute = ROOT + "/" + relative
    need(wall is None or wall.installed and wall.approved(absolute),
         "install the V29 physical wall before the first predecessor read")
    descriptor = os.open(
        absolute,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode)
             and stat.S_IMODE(before.st_mode) == 0o600
             and before.st_dev == DEVICE and before.st_ino == inode
             and before.st_size == size and before.st_uid == os.geteuid()
             and before.st_nlink == 1,
             "reject substituted no-follow public owner: " + role)
        remaining, chunks = size, []
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            need(type(chunk) is bytes and bool(chunk),
                 "reject truncated authenticated public owner: " + role)
            chunks.append(chunk)
            remaining -= len(chunk)
        need(os.read(descriptor, 1) == b"",
             "reject expanded authenticated public owner: " + role)
        after = os.fstat(descriptor)
        need(all(getattr(before, key) == getattr(after, key)
                 for key in ("st_dev", "st_ino", "st_size", "st_mtime_ns",
                             "st_ctime_ns", "st_nlink")),
             "reject concurrently replaced authenticated public owner: " + role)
        result = b"".join(chunks)
        need(sha(result) == fingerprint,
             "reject altered complete independently pinned owner: " + role)
        return result
    finally:
        os.close(descriptor)


def dynamic_owner(wall: PublicSourceWall | None, role: str, relative: str,
                  fingerprint: str) -> tuple:
    sha_pin(fingerprint, role)
    permitted = {SOURCE, PROTOCOL, CONTRACT, *(item[1] for item in BUILD_PATHS),
                 PUBLIC_RECEIPT_PATH, ROOT_RECEIPT_PATH}
    need(relative in permitted,
         "reject unowned dynamically pinned V29 public owner: " + role)
    absolute = ROOT + "/" + relative
    need(wall is None or wall.installed and wall.approved(absolute),
         "install the physical source wall before dynamic-owner authentication")
    descriptor = os.open(absolute, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        identity = os.fstat(descriptor)
        need(stat.S_ISREG(identity.st_mode)
             and stat.S_IMODE(identity.st_mode) == 0o600
             and identity.st_dev == DEVICE and identity.st_uid == os.geteuid()
             and identity.st_nlink == 1
             and 0 < identity.st_size <= MAX_OWNER_BYTES,
             "reject unsafe, private, or exchanged public owner: " + role)
        return role, relative, fingerprint, identity.st_size, identity.st_ino
    finally:
        os.close(descriptor)


def owner_document(row: tuple) -> dict:
    return {"role": row[0], "path": row[1], "sha256": row[2],
            "bytes": row[3], "device": DEVICE, "inode": row[4],
            "mode": "0600", "uid": os.geteuid(), "nlink": 1}


def load_parent(wall: PublicSourceWall | None) -> types.ModuleType:
    raw = secure_owner(wall, PREVIOUS[0])
    module = types.ModuleType("_rebar_v29_authenticated_original_campaign_v25")
    module.__file__ = ROOT + "/" + PREVIOUS[0][1]
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    need(module.VERSION == 25 and module.SOURCE == PREVIOUS[0][1]
         and module.PROTOCOL == PREVIOUS[1][1]
         and module.CONTRACT == PREVIOUS[2][1]
         and module.CASE_COUNT == CASE_COUNT
         and module.WORKER_COUNT == WORKER_COUNT
         and callable(module.load_source_context)
         and callable(module.actual_context)
         and callable(module.operational_v4_guard),
         "authenticate the complete immutable V25 first-party original controller")
    if wall is not None:
        wall.error_type = module.CampaignError
    return module


def previous_options(parent: types.ModuleType, mode: str) -> dict:
    return {
        "mode": mode,
        "source_sha256": PREVIOUS[0][2],
        "protocol_sha256": PREVIOUS[1][2],
        "contract_sha256": PREVIOUS[2][2],
        **{name: row[2]
           for name, row in zip(GUARD_PIN_NAMES, parent.GUARD_V4, strict=True)},
    }


def strict_document(parent: types.ModuleType, state: dict, raw: bytes,
                    label: str) -> dict:
    return parent.strict_document(state["capture"], state["semantic"], raw,
                                  label)


def validate_previous_failure(parent: types.ModuleType, previous: dict,
                              failure: dict) -> None:
    need(type(previous) is dict
         and previous.get("schema") == parent.SCHEMA + "-recoverable-source-freeze"
         and previous.get("version") == 25
         and previous.get("source", {}).get("sha256") == PREVIOUS[0][2]
         and previous.get("protocol", {}).get("sha256") == PREVIOUS[1][2]
         and previous.get("original_correctness_boundary", {}).get(
             "case_execution_denominator") == CASE_COUNT
         and previous.get("original_correctness_boundary", {}).get("suite_count")
             == WORKER_COUNT,
         "authenticate the complete independently frozen original V25 campaign")
    need(type(failure) is dict and len(failure) == 96
         and failure.get("schema")
             == "rebar-owned-repaired-rust-original-campaign-v25-"
                "durable-publication-receipt"
         and failure.get("status") == "PASS"
         and failure.get("publication_status") == "PASS"
         and failure.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
         and failure.get("candidate_status") == "FAIL"
         and failure.get("semantic_mismatch_count") == 1352
         and failure.get("verified_passing_case_count") == 15_877
         and failure.get("case_execution_denominator") == CASE_COUNT
         and failure.get("suite_count") == WORKER_COUNT
         and failure.get("completed_suite_count") == WORKER_COUNT
         and failure.get("actual_candidate_workers") == WORKER_COUNT
         and failure.get("distinct_worker_process_id_count") == WORKER_COUNT
         and failure.get("named_private_waiver_count") == 13
         and failure.get("corrected_public_adapter_sha256")
             == HISTORICAL_V25_ADAPTER_SHA
         and failure.get("corrected_public_adapter_bytes")
             == HISTORICAL_V25_ADAPTER_BYTES
         and failure.get("combined_bridge_source_sha256") == parent.BRIDGE_SOURCE_SHA
         and failure.get("combined_bridge_source_bytes") == parent.BRIDGE_SOURCE_BYTES
         and failure.get("all_four_original_targets_restored") is True
         and failure.get("holdout") == "NOT OPENED",
         "preserve the complete immutable d292 V25 actual candidate FAIL-1352")
    suites = failure.get("suite_integrity")
    need(type(suites) is list and len(suites) == WORKER_COUNT
         and all(type(row) is dict and row.get("fully_observed") is True
                 and row.get("actual_worker_started") is True for row in suites)
         and sum(row.get("mismatch_count", -1) for row in suites) == 1352
         and sum(row.get("verified_passing_case_count", -1) for row in suites)
             == 15_877
         and {row["suite"]: row["mismatch_count"] for row in suites
              if row.get("mismatch_count", 0)}
             == {"substitution_v2": 240, "shape_v2": 1112},
         "preserve every original V25 row and exactly 240 + 1,112 mismatches")


def validate_preserved_passes(original_freeze: dict, original_pass: dict,
                              public_freeze: dict, public_pass: dict,
                              v33: dict) -> None:
    need(type(original_freeze) is dict
         and original_freeze.get("schema")
             == "rebar-owned-repaired-rust-original-campaign-v26-"
                "recoverable-source-freeze"
         and original_freeze.get("version") == 26
         and original_freeze.get("source", {}).get("sha256")
             == ORIGINAL_V26[0][2]
         and original_freeze.get("protocol", {}).get("sha256")
             == ORIGINAL_V26[1][2]
         and original_freeze.get("original_correctness_boundary", {}).get(
             "case_execution_denominator") == CASE_COUNT
         and original_freeze.get("original_correctness_boundary", {}).get(
             "suite_count") == WORKER_COUNT,
         "authenticate the separately frozen historical V26 original campaign")
    need(type(original_pass) is dict and len(original_pass) == 101
         and original_pass.get("schema")
             == "rebar-owned-repaired-rust-original-campaign-v26-"
                "durable-publication-receipt"
         and original_pass.get("status") == "PASS"
         and original_pass.get("publication_status") == "PASS"
         and original_pass.get("candidate_status") == "PASS"
         and original_pass.get("case_execution_denominator") == CASE_COUNT
         and original_pass.get("verified_passing_case_count") == CASE_COUNT
         and original_pass.get("semantic_mismatch_count") == 0
         and original_pass.get("suite_count") == WORKER_COUNT
         and original_pass.get("completed_suite_count") == WORKER_COUNT
         and original_pass.get("actual_candidate_workers") == WORKER_COUNT
         and original_pass.get("distinct_worker_process_id_count") == WORKER_COUNT
         and original_pass.get("candidate_original_oracle_pass") is True
         and original_pass.get("original_suite_correctness_qualified") is True
         and original_pass.get("candidate_qualified") is False
         and original_pass.get("runtime_non_delegation") == "NOT ESTABLISHED"
         and original_pass.get("corrected_public_adapter_sha256")
             == HISTORICAL_V25_ADAPTER_SHA
         and original_pass.get("corrected_public_adapter_bytes")
             == HISTORICAL_V25_ADAPTER_BYTES,
         "preserve the historical V30-original 31,237-case PASS separately")
    suites = original_pass.get("suite_integrity")
    need(type(suites) is list and len(suites) == WORKER_COUNT
         and all(type(row) is dict and row.get("fully_observed") is True
                 and row.get("actual_worker_started") is True
                 and row.get("mismatch_count") == 0 for row in suites),
         "retain all historical original-suite rows without substitutions")
    build = public_freeze.get("actual_successful_v33_build", {})
    boundary = public_freeze.get("public_correctness", {})
    preserved = public_freeze.get("preserved_original_v26", {})
    need(type(public_freeze) is dict and len(public_freeze) == 25
         and public_freeze.get("schema")
             == "rebar-owned-rust-full-public-correctness-v5-source-freeze"
         and public_freeze.get("version") == 5
         and public_freeze.get("source", {}).get("sha256") == PUBLIC_V5[0][2]
         and public_freeze.get("protocol", {}).get("sha256") == PUBLIC_V5[1][2]
         and public_freeze.get("candidate_qualified") is False
         and build.get("label") == HISTORICAL_V33_BUILD_LABEL
         and build.get("build_status") == "PASS"
         and build.get("actual_compiler_process_count") == 28
         and build.get("adapter_source_sha256") == ADAPTER_SHA
         and build.get("bridge_source_sha256") == HISTORICAL_V33_BRIDGE_SOURCE_SHA
         and build.get("engine_source_sha256") == HISTORICAL_V33_ENGINE_SOURCE_SHA
         and build.get("search_source_sha256") == SEARCH_SOURCE_SHA
         and build.get("source", {}).get("sha256") == HISTORICAL_V33[0][2]
         and build.get("protocol", {}).get("sha256") == HISTORICAL_V33[1][2]
         and build.get("contract", {}).get("sha256") == HISTORICAL_V33[2][2]
         and build.get("publication_receipt", {}).get("sha256")
             == HISTORICAL_V33[3][2]
         and build.get("root_provenance_receipt", {}).get("sha256")
             == HISTORICAL_V33[4][2]
         and build.get("native_engine", {}).get("sha256")
             == HISTORICAL_V33_ENGINE_SHA
         and build.get("native_bridge", {}).get("sha256")
             == HISTORICAL_V33_BRIDGE_SHA
         and boundary.get("case_count") == 10_434
         and boundary.get("dataset_count") == 94
         and boundary.get("operation_count") == 111
         and preserved.get("receipt_sha256") == ORIGINAL_V26_PASS[2]
         and preserved.get("case_count") == CASE_COUNT
         and preserved.get("verified_passing_case_count") == CASE_COUNT
         and preserved.get("candidate_status") == "PASS",
         "authenticate the exact V33 10,434-case public controller freeze")
    need(type(public_pass) is dict and len(public_pass) == 69
         and public_pass.get("schema")
             == "rebar-owned-rust-full-public-correctness-v5-"
                "durable-publication-receipt"
         and public_pass.get("version") == 5
         and public_pass.get("status") == "PASS"
         and public_pass.get("publication_status") == "PASS"
         and public_pass.get("candidate_status") == "PASS"
         and public_pass.get("public_10434_correctness_status") == "PASS"
         and public_pass.get("public_10434_case_count") == 10_434
         and public_pass.get("public_10434_verified_passing_case_count") == 10_434
         and public_pass.get("public_10434_mismatch_count") == 0
         and public_pass.get("public_api_operation_count") == 111
         and public_pass.get("candidate_worker_count") == 1
         and public_pass.get("reference_worker_count") == 1
         and public_pass.get("source_sha256") == PUBLIC_V5[0][2]
         and public_pass.get("protocol_sha256") == PUBLIC_V5[1][2]
         and public_pass.get("contract_sha256") == PUBLIC_V5[2][2]
         and public_pass.get("v33_source_sha256") == HISTORICAL_V33[0][2]
         and public_pass.get("v33_protocol_sha256") == HISTORICAL_V33[1][2]
         and public_pass.get("v33_contract_sha256") == HISTORICAL_V33[2][2]
         and public_pass.get("v33_publication_sha256") == HISTORICAL_V33[3][2]
         and public_pass.get("v33_root_sha256") == HISTORICAL_V33[4][2]
         and public_pass.get("v33_adapter_sha256") == ADAPTER_SHA
         and public_pass.get("v33_native_engine_sha256")
             == HISTORICAL_V33_ENGINE_SHA
         and public_pass.get("v33_native_bridge_sha256")
             == HISTORICAL_V33_BRIDGE_SHA
         and public_pass.get("v26_original_pass_sha256") == ORIGINAL_V26_PASS[2]
         and public_pass.get("v26_original_verified_passing_case_count")
             == CASE_COUNT
         and public_pass.get("runtime_non_delegation") == "NOT ESTABLISHED"
         and public_pass.get("candidate_qualified") is False,
         "preserve the exact V33 10,434/10,434, 111-operation public PASS")


def validate_failed_v27_freeze(freeze: dict, receipt: dict, v33: dict) -> None:
    build = freeze.get("actual_v33_native_build", {})
    historical = freeze.get("preserved_historical_v26_original_pass", {})
    public = freeze.get("preserved_exact_v33_full_public_v5_pass", {})
    need(type(freeze) is dict
         and freeze.get("schema")
             == "rebar-owned-repaired-rust-original-campaign-v27-"
                "recoverable-source-freeze"
         and freeze.get("version") == 27
         and freeze.get("source", {}).get("sha256") == FAILED_V27[0][2]
         and freeze.get("protocol", {}).get("sha256") == FAILED_V27[1][2]
         and build.get("label") == HISTORICAL_V33_BUILD_LABEL
         and build.get("corrected_public_adapter_sha256") == ADAPTER_SHA
         and build.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
         and build.get("native_engine_sha256")
             == HISTORICAL_V33_ENGINE_SHA
         and build.get("native_bridge_sha256")
             == HISTORICAL_V33_BRIDGE_SHA
         and build.get("publication_receipt", {}).get("sha256")
             == HISTORICAL_V33[3][2]
         and build.get("root_provenance_receipt", {}).get("sha256")
             == HISTORICAL_V33[4][2]
         and historical.get("actual_pass_receipt_owner", {}).get("sha256")
             == ORIGINAL_V26_PASS[2]
         and public.get("actual_pass_receipt_owner", {}).get("sha256")
             == PUBLIC_V5_PASS[2]
         and public.get("verified_passing_case_count") == 10_434,
         "authenticate the complete immutable V27 exact-V33 failed entry freeze")
    need(type(receipt) is dict and len(receipt) == 8
         and receipt.get("schema")
             == "rebar-owned-repaired-rust-original-campaign-v27-"
                "preactivation-failure"
         and receipt.get("status") == "FAIL"
         and receipt.get("error_type") == "CampaignError"
         and receipt.get("error_message")
             == "reject stale V19 root, bridge, oracle, producer, guard, or recovery"
         and receipt.get("exit_code") == 2
         and receipt.get("exact_v33_original_correctness") == NOT_MEASURED
         and receipt.get("candidate_qualified") is False
         and receipt.get("winner_selected") is False,
         "preserve the complete committed V27 preactivation FAIL exactly")


def validate_historical_v33_original(freeze: dict, receipt: dict) -> None:
    build = freeze.get("actual_v33_native_build", {})
    need(type(freeze) is dict
         and freeze.get("schema")
             == "rebar-owned-repaired-rust-original-campaign-v28-"
                "recoverable-source-freeze"
         and freeze.get("version") == 28
         and freeze.get("source", {}).get("sha256")
             == HISTORICAL_V28_CAMPAIGN[0][2]
         and freeze.get("protocol", {}).get("sha256")
             == HISTORICAL_V28_CAMPAIGN[1][2]
         and build.get("label") == HISTORICAL_V33_BUILD_LABEL
         and build.get("publication_receipt", {}).get("sha256")
             == HISTORICAL_V33[3][2]
         and build.get("root_provenance_receipt", {}).get("sha256")
             == HISTORICAL_V33[4][2]
         and build.get("native_engine_sha256") == HISTORICAL_V33_ENGINE_SHA
         and build.get("native_bridge_sha256") == HISTORICAL_V33_BRIDGE_SHA,
         "authenticate the complete separately frozen historical V33 campaign")
    need(type(receipt) is dict
         and receipt.get("schema")
             == "rebar-owned-repaired-rust-original-campaign-v28-"
                "durable-publication-receipt"
         and receipt.get("status") == "PASS"
         and receipt.get("publication_status") == "PASS"
         and receipt.get("candidate_status") == "PASS"
         and receipt.get("campaign_source_sha256")
             == HISTORICAL_V28_CAMPAIGN[0][2]
         and receipt.get("campaign_protocol_sha256")
             == HISTORICAL_V28_CAMPAIGN[1][2]
         and receipt.get("campaign_contract_sha256")
             == HISTORICAL_V28_CAMPAIGN[2][2]
         and receipt.get("actual_v28_build_source_sha256")
             == HISTORICAL_V33[0][2]
         and receipt.get("actual_v28_build_protocol_sha256")
             == HISTORICAL_V33[1][2]
         and receipt.get("actual_v28_build_contract_sha256")
             == HISTORICAL_V33[2][2]
         and receipt.get("actual_v28_build_receipt_sha256")
             == HISTORICAL_V33[3][2]
         and receipt.get("native_engine_sha256") == HISTORICAL_V33_ENGINE_SHA
         and receipt.get("native_bridge_sha256") == HISTORICAL_V33_BRIDGE_SHA
         and receipt.get("combined_bridge_source_sha256")
             == HISTORICAL_V33_BRIDGE_SOURCE_SHA
         and receipt.get("corrected_public_adapter_sha256") == ADAPTER_SHA
         and receipt.get("case_execution_denominator") == CASE_COUNT
         and receipt.get("verified_passing_case_count") == CASE_COUNT
         and receipt.get("semantic_mismatch_count") == 0
         and receipt.get("completed_suite_count") == WORKER_COUNT
         and receipt.get("actual_candidate_workers") == WORKER_COUNT
         and receipt.get("distinct_worker_process_id_count") == WORKER_COUNT
         and receipt.get("candidate_original_oracle_pass") is True
         and receipt.get("original_suite_correctness_qualified") is True
         and receipt.get("candidate_qualified") is False,
         "preserve the exact V33 31,237-case PASS as historical evidence only")
    suites = receipt.get("suite_integrity")
    need(type(suites) is list and len(suites) == WORKER_COUNT
         and all(type(item) is dict
                 and item.get("fully_observed") is True
                 and item.get("actual_worker_started") is True
                 and item.get("mismatch_count") == 0 for item in suites),
         "retain every independently observed historical V33 original suite")


def validate_native_handle_lease(freeze: dict, application: dict) -> None:
    proof = freeze.get("independent_synthetic_lifetime_semantics", {})
    composition = freeze.get("first_party_source_composition", {})
    created = application.get("created", {})
    need(type(freeze) is dict
         and freeze.get("schema")
             == "rebar-owned-rust-native-handle-lease-v1-source-freeze"
         and freeze.get("version") == 1
         and freeze.get("source", {}).get("sha256") == NATIVE_HANDLE_LEASE[0][2]
         and freeze.get("protocol", {}).get("sha256") == NATIVE_HANDLE_LEASE[1][2]
         and proof.get("operation_callback_sequence_count") == 32_768
         and proof.get("callback_finalization_case_count") == 103_184
         and proof.get("scanner_and_finditer_lifetime_case_count") == 20_656
         and proof.get("callback_exception_case_count") == 20_480
         and proof.get("candidate_executed") is False
         and composition.get("target_sha256") == BRIDGE_SOURCE_SHA
         and composition.get("target_bytes") == BRIDGE_SOURCE_BYTES
         and composition.get("active_dispatch_strong_owner_lease") is True
         and composition.get("callback_substitution_strong_owner_lease") is True
         and composition.get("scanner_and_finditer_independent_owner_lease")
             is True
         and composition.get("private_capsule_destructor_owns_native_engine")
             is True
         and composition.get("added_source_external_regex_dependency_count") == 0
         and composition.get("added_source_stdlib_matching_delegation_count") == 0
         and freeze.get("candidate_correctness") == NOT_MEASURED
         and freeze.get("undefined_behavior") == NOT_MEASURED,
         "authenticate synthetic first-party callback/iterator ownership only")
    need(type(application) is dict
         and application.get("schema")
             == "rebar-owned-rust-native-handle-lease-v1-recorded-application"
         and application.get("status") == "APPLIED"
         and application.get("source_sha256") == NATIVE_HANDLE_LEASE[0][2]
         and application.get("protocol_sha256") == NATIVE_HANDLE_LEASE[1][2]
         and application.get("contract_sha256") == NATIVE_HANDLE_LEASE[2][2]
         and created.get("sha256") == BRIDGE_SOURCE_SHA
         and created.get("bytes") == BRIDGE_SOURCE_BYTES
         and created.get("inode") == 526633
         and application.get("operation_callback_sequence_count") == 32_768
         and application.get("callback_finalization_case_count") == 103_184
         and application.get("scanner_and_finditer_lifetime_case_count") == 20_656
         and application.get("candidate_executions") == 0
         and application.get("candidate_imports") == 0
         and application.get("candidate_correctness") == NOT_MEASURED
         and application.get("undefined_behavior") == NOT_MEASURED,
         "bind the applied safe bridge without opening candidate-owned source")


def first_exact(document: dict, keys: tuple[str, ...], expected: object,
                label: str) -> str:
    found = [key for key in keys if document.get(key) == expected]
    need(bool(found), "require exact authenticated V33 " + label)
    return found[0]


def normalize_phase_outputs(root: dict, private_root: dict,
                            outputs: dict) -> list[dict]:
    candidates = (root.get("phase_native_outputs"),
                  root.get("phase_native_inodes"),
                  private_root.get("phases"))
    records = next((value for value in candidates
                    if type(value) in (list, tuple, dict)), None)
    if type(records) is dict:
        records = [records.get(name) for name in ("reference-a", "reference-b")]
    need(type(records) in (list, tuple) and len(records) == 2,
         "require both complete independently receipt-attested V33 native phases")
    phases = []
    identities: set[tuple[int, int]] = set()
    for index, name in enumerate(("reference-a", "reference-b")):
        item = records[index]
        need(type(item) is dict,
             "require one complete published V33 native phase: " + name)
        if "name" in item or "phase" in item:
            need(item.get("name", item.get("phase")) == name,
                 "preserve the exact independently published V33 phase order")
        raw = item.get("native_outputs", item)
        if type(raw) is dict and set(raw) >= {"engine", "bridge"}:
            rows = [raw["engine"], raw["bridge"]]
        else:
            need(type(raw) in (list, tuple) and len(raw) == 2,
                 "require both fully pinned V33 native roles: " + name)
            rows = list(raw)
        native = []
        for offset, role in enumerate(("engine", "bridge")):
            value = rows[offset]
            summary = outputs[role]
            filename = ("_rust_engine.so" if role == "engine"
                        else "_rust_bridge.cpython-314-x86_64-linux-gnu.so")
            need(type(value) is dict
                 and value.get("role", role) == role
                 and value.get("sha256") == summary.get("sha256")
                 and value.get("bytes", value.get("size_bytes"))
                     == summary.get("size_bytes", summary.get("bytes"))
                 and value.get("device") == private_root.get("device")
                 and type(value.get("inode")) is int and value["inode"] > 0
                 and value.get("file_name", filename) == filename,
                 "reject exchanged V33 native role " + name + "/" + role)
            path = value.get("absolute_path", value.get("path"))
            if path is not None:
                need(path == private_root["path"] + "/" + name + "/native/"
                     + filename,
                     "reject substituted V33 phase-native path " + name)
            identity = (value["device"], value["inode"])
            need(identity not in identities,
                 "reject reused, linked, or cross-phase V33 native artifact")
            identities.add(identity)
            native.append({"role": role, "sha256": value["sha256"],
                           "bytes": value.get("bytes", value.get("size_bytes")),
                           "file_name": filename,
                           "absolute_path": private_root["path"] + "/" + name
                               + "/native/" + filename,
                           "device": value["device"], "inode": value["inode"],
                           "mode": value.get("mode", "0600" if role == "engine"
                                             else "0700"),
                           "uid": value.get("uid", os.geteuid()),
                           "nlink": value.get("nlink", 1),
                           "native_loaded": value.get("native_loaded", False)})
        phases.append({"name": name,
                       "absolute_path": private_root["path"] + "/" + name,
                       "device": private_root["device"], "uid": os.geteuid(),
                       "mode": "0700", "native_outputs": native})
    need(len(identities) == 4,
         "retain all four independently published V33 phase-native identities")
    return phases


def archive_identity(publication: dict, root: dict) -> dict:
    metadata = publication.get("archive_publication")
    if type(metadata) is not dict:
        metadata = root.get("archive_publication")
    if type(metadata) is not dict:
        metadata = {"sha256": publication.get("archive_sha256"),
                    "bytes": publication.get("archive_bytes"),
                    "device": publication.get("archive_device", DEVICE),
                    "inode": publication.get("archive_inode",
                                              root.get("archive_inode"))}
    need(type(metadata) is dict and sha_pin(metadata.get("sha256"),
                                           "V33 archive metadata")
         == publication.get("archive_sha256")
         and metadata.get("bytes") == publication.get("archive_bytes")
         and type(metadata.get("bytes")) is int and metadata["bytes"] > 0
         and metadata.get("device", DEVICE) == DEVICE
         and type(metadata.get("inode")) is int and metadata["inode"] > 0,
         "bind actual V33 compressed archive metadata without opening the archive")
    return {"sha256": metadata["sha256"], "bytes": metadata["bytes"],
            "device": DEVICE, "inode": metadata["inode"],
            "exclusive_creation": metadata.get("exclusive_creation", True),
            "file_fsync_completed": metadata.get("file_fsync_completed", True)}


def validate_v35_receipts(rows: tuple, build_freeze: dict,
                          publication: dict, root: dict,
                          failure: dict) -> dict:
    source_row, protocol_row, contract_row, public_row, root_row = rows
    expected_schema = "rebar-phase2-owned-rust-optimized-safe-source-build-v35"
    need(type(build_freeze) is dict
         and build_freeze.get("schema") == expected_schema + "-source-freeze"
         and build_freeze.get("version") == 35
         and build_freeze.get("family", FAMILY) == FAMILY,
         "authenticate the complete published V35 first-party native source freeze")
    sources = build_freeze.get("candidate_sources", {})
    need(type(sources) is dict
         and sources.get("combined_engine", {}).get("sha256") == ENGINE_SOURCE_SHA
         and sources.get("combined_engine", {}).get("bytes") == ENGINE_SOURCE_BYTES
         and sources.get("combined_search", {}).get("sha256") == SEARCH_SOURCE_SHA
         and sources.get("combined_search", {}).get("bytes") == SEARCH_SOURCE_BYTES
         and sources.get("optimized_native_handle_lease_bridge", {}).get("sha256")
             == BRIDGE_SOURCE_SHA
         and sources.get("optimized_native_handle_lease_bridge", {}).get("bytes")
             == BRIDGE_SOURCE_BYTES
         and sources.get("corrected_comment_adapter", {}).get("sha256")
             == ADAPTER_SHA
         and sources.get("corrected_comment_adapter", {}).get("bytes")
             == ADAPTER_BYTES
         and build_freeze.get("proposed_v35_correctness") == NOT_MEASURED
         and build_freeze.get("proposed_v35_undefined_behavior") == NOT_MEASURED
         and build_freeze.get("proposed_v35_live_runtime_non_delegation")
             == "NOT ESTABLISHED"
         and build_freeze.get("proposed_v35_static_source_and_elf_non_delegation")
             == "NOT ESTABLISHED",
         "cross-bind safe V35 first-party sources without reading candidate files")
    for document, suffix in ((publication, "-durable-publication-receipt"),
                             (root, "-durable-root-provenance-receipt")):
        need(type(document) is dict
             and document.get("schema") == expected_schema + suffix
             and document.get("version") == 35
             and document.get("status") == "PASS"
             and document.get("family") == FAMILY
             and document.get("label") == BUILD_LABEL
             and document.get("source_sha256") == source_row[2]
             and document.get("protocol_sha256") == protocol_row[2]
             and document.get("contract_sha256") == contract_row[2]
             and document.get("actual_compiler_process_count") == 28
             and document.get("latest_v25_candidate_status") == "FAIL"
             and document.get("latest_v25_semantic_mismatch_count") == 1352
             and document.get("latest_v25_exact_disjoint_mismatch_partition")
                 == {"substitution_v2": 240,
                     "shape_v2_ordering": 1024,
                     "shape_v2_trailing_probe": 56,
                     "shape_v2_malformed_expansion": 32}
             and document.get("candidate_qualified") is False,
             "reject unpublished, failed, delegated, or stale V35 public evidence")
    need(publication.get("build_status") == "PASS"
         and publication.get("actual_completed_phase_count") == 2
         and publication.get("external_cargo_dependency_count") == 0
         and root.get("canonical_build_status") == "PASS"
         and root.get("canonical_build_receipt_sha256") == public_row[2]
         and root.get("actual_source_phase_count") == 2
         and root.get("cross_phase_complete_engine_elf_byte_identical") is True
         and root.get("cross_phase_complete_bridge_elf_byte_identical") is True
         and root.get("all_original_source_identities_restored") is True
         and root.get("all_original_runtime_target_identities_restored") is True,
         "require both genuinely reproduced V35 phases and restored canonical owners")
    for document in (publication, root):
        first_exact(document,
                    ("complete_bridge_source_sha256", "combined_bridge_source_sha256",
                     "corrected_bridge_source_sha256",
                     "safe_no_external_introspection_bridge_sha256"),
                    BRIDGE_SOURCE_SHA, "complete corrected bridge SHA-256")
        first_exact(document,
                    ("complete_bridge_source_bytes", "combined_bridge_source_bytes",
                     "corrected_bridge_source_bytes",
                     "safe_no_external_introspection_bridge_bytes"),
                    BRIDGE_SOURCE_BYTES, "complete corrected bridge byte count")
        first_exact(document, ("corrected_public_adapter_sha256",), ADAPTER_SHA,
                    "corrected public adapter SHA-256")
        first_exact(document, ("corrected_public_adapter_bytes",), ADAPTER_BYTES,
                    "corrected public adapter byte count")
        first_exact(document, ("combined_engine_source_sha256",
                               "complete_engine_source_sha256"), ENGINE_SOURCE_SHA,
                    "first-party optimized engine source SHA-256")
        first_exact(document, ("combined_search_source_sha256",
                               "complete_search_source_sha256"), SEARCH_SOURCE_SHA,
                    "first-party optimized search source SHA-256")
    process_ids = root.get("actual_compiler_process_ids")
    need(type(process_ids) is list and len(process_ids) == 28
         and len(set(process_ids)) == 28
         and all(type(item) is int and item > 0 for item in process_ids),
         "require 28 genuinely observed and distinct V33 compiler/ELF processes")
    private_root = root.get("root")
    need(type(private_root) is dict
         and type(private_root.get("path")) is str
         and private_root["path"].startswith("/tmp/rebar-phase2-native-build-")
         and len(private_root["path"].split("/")) == 3
         and type(private_root.get("device")) is int
         and type(private_root.get("inode")) is int and private_root["inode"] > 0
         and private_root.get("mode") == "0700"
         and private_root.get("uid", os.geteuid()) == os.geteuid(),
         "bind the actual independently published V33 root without statting it")
    outputs = root.get("actual_reproduced_native_outputs")
    need(type(outputs) is dict and set(outputs) == {"engine", "bridge"},
         "require both complete independently reproduced V33 first-party ELFs")
    for role in ("engine", "bridge"):
        artifact = outputs[role]
        need(type(artifact) is dict and sha_pin(artifact.get("sha256"), role)
             and type(artifact.get("size_bytes", artifact.get("bytes"))) is int
             and artifact.get("size_bytes", artifact.get("bytes")) > 0,
             "require one complete authenticated first-party V33 native " + role)
        audit = artifact.get("audit")
        if audit is not None:
            need(type(audit) is dict
                 and audit.get("external_regex_dependency_count") == 0
                 and audit.get("cross_family_dependency_count") == 0,
                 "reject external or cross-family first-party V33 native " + role)
    phases = normalize_phase_outputs(root, private_root, outputs)
    archive = archive_identity(publication, root)
    uncompressed_sha = publication.get("uncompressed_sha256")
    uncompressed_bytes = publication.get("uncompressed_bytes")
    need(sha_pin(uncompressed_sha, "V33 uncompressed archive metadata")
         and type(uncompressed_bytes) is int and uncompressed_bytes > 0,
         "retain V33 uncompressed archive metadata without inflation")
    return {"rows": rows, "freeze": build_freeze,
            "publication": publication, "root": root,
            "private_root": private_root, "native_outputs": outputs,
            "phase_rows": phases, "archive": archive,
            "uncompressed_sha256": uncompressed_sha,
            "uncompressed_bytes": uncompressed_bytes,
            "actual_compiler_process_ids": list(process_ids),
            "previous_failure": failure,
            "publication_owner": owner_document(public_row),
            "root_owner": owner_document(root_row)}


def v35_rows(wall: PublicSourceWall | None, options: dict) -> tuple:
    names = V35_PIN_NAMES
    public = tuple(dynamic_owner(wall, role, relative, options[name])
                   for (role, relative), name in zip(BUILD_PATHS, names[:3],
                                                    strict=True))
    publication = dynamic_owner(wall, "build_v35_publication_receipt",
                                PUBLIC_RECEIPT_PATH, options[names[3]])
    root = dynamic_owner(wall, "build_v35_root_provenance_receipt",
                         ROOT_RECEIPT_PATH, options[names[4]])
    return public + (publication, root)


def contract_document(source: tuple, protocol: tuple, parent: types.ModuleType,
                      previous: dict, failure: dict, v33: dict,
                      original_freeze: dict, original_pass: dict,
                      public_freeze: dict, public_pass: dict,
                      failed_v27_freeze: dict, failed_v27_receipt: dict,
                      historical_v33_freeze: dict, historical_v33_pass: dict,
                      handle_lease_freeze: dict,
                      handle_lease_application: dict) -> dict:
    correctness = previous["original_correctness_boundary"]
    suites = correctness["suites"]
    need(type(suites) is list and len(suites) == WORKER_COUNT
         and sum(row["case_execution_denominator"] for row in suites) == CASE_COUNT
         and len(correctness["named_private_waivers"]) == 13,
         "preserve all unchanged 31,237 original vectors and 13 private waivers")
    audit = previous["independent_runtime_non_delegation_v4_audit"]
    need(audit.get("status") == "FAIL" and audit.get("finding_count") == 1
         and audit.get("runtime_non_delegation") == "NOT ESTABLISHED",
         "preserve the independent historical V4 finding as separate evidence")
    guard = previous["operational_runtime_guard_v4"]
    native = v33["native_outputs"]
    archive = v33["archive"]
    root = v33["private_root"]
    return {
        "schema": SCHEMA + "-recoverable-source-freeze",
        "status": "SOURCE FROZEN; V35 BUILD PASS; V35 ORIGINAL NOT RUN",
        "version": VERSION, "family": FAMILY, "goal_sha256": GOAL_SHA,
        "source": owner_document(source), "protocol": owner_document(protocol),
        "immutable_previous_v25_campaign": {
            "owners": [owner_document(row) for row in PREVIOUS],
            "complete_contract_sha256": PREVIOUS[2][2],
            "complete_contract_field_count": len(previous),
            "actual_failure_receipt_owner": owner_document(PREVIOUS_FAILURE),
            "actual_failure_receipt_field_count": len(failure),
            "publication_status": "PASS", "candidate_status": "FAIL",
            "semantic_mismatch_count": 1352,
            "verified_passing_case_count": 15_877,
            "actual_candidate_workers": WORKER_COUNT,
            "completed_suite_count": WORKER_COUNT,
            "fully_observed_suite_mismatch_counts":
                {"substitution_v2": 240, "shape_v2": 1112},
            "exact_disjoint_v33_corrected_mismatch_partition":
                {"substitution_v2": 240,
                 "shape_v2_ordering": 1024,
                 "shape_v2_trailing_probe": 56,
                 "shape_v2_malformed_expansion": 32},
            "complete_suite_rows": [dict(row) for row in failure["suite_integrity"]],
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
        },
        "preserved_historical_v26_original_pass": {
            "owners": [owner_document(row) for row in ORIGINAL_V26],
            "complete_contract_field_count": len(original_freeze),
            "actual_pass_receipt_owner": owner_document(ORIGINAL_V26_PASS),
            "actual_pass_receipt_field_count": len(original_pass),
            "candidate_status": "PASS", "semantic_mismatch_count": 0,
            "case_execution_denominator": CASE_COUNT,
            "verified_passing_case_count": CASE_COUNT,
            "suite_count": WORKER_COUNT,
            "actual_candidate_workers": WORKER_COUNT,
            "distinct_worker_process_id_count": WORKER_COUNT,
            "historical_adapter_sha256": HISTORICAL_V25_ADAPTER_SHA,
            "historical_adapter_bytes": HISTORICAL_V25_ADAPTER_BYTES,
            "historical_v30_pass_is_not_v33_original_evidence": True,
            "historical_v30_pass_is_not_v35_original_evidence": True,
            "candidate_qualified": False,
        },
        "preserved_historical_v33_original_pass": {
            "campaign_owners": [
                owner_document(row) for row in HISTORICAL_V28_CAMPAIGN
            ],
            "build_owners": [owner_document(row) for row in HISTORICAL_V33],
            "complete_campaign_contract_field_count": len(historical_v33_freeze),
            "actual_pass_receipt_owner":
                owner_document(HISTORICAL_V33_ORIGINAL_PASS),
            "actual_pass_receipt_field_count": len(historical_v33_pass),
            "build_label": HISTORICAL_V33_BUILD_LABEL,
            "native_engine_sha256": HISTORICAL_V33_ENGINE_SHA,
            "native_bridge_sha256": HISTORICAL_V33_BRIDGE_SHA,
            "bridge_source_sha256": HISTORICAL_V33_BRIDGE_SOURCE_SHA,
            "engine_source_sha256": HISTORICAL_V33_ENGINE_SOURCE_SHA,
            "case_execution_denominator": CASE_COUNT,
            "verified_passing_case_count": CASE_COUNT,
            "semantic_mismatch_count": 0,
            "completed_suite_count": WORKER_COUNT,
            "candidate_status": "PASS",
            "historical_v33_pass_is_not_v35_original_evidence": True,
            "candidate_qualified": False,
        },
        "preserved_exact_v33_full_public_v5_pass": {
            "owners": [owner_document(row) for row in PUBLIC_V5],
            "complete_contract_field_count": len(public_freeze),
            "actual_pass_receipt_owner": owner_document(PUBLIC_V5_PASS),
            "actual_pass_receipt_field_count": len(public_pass),
            "candidate_status": "PASS", "semantic_mismatch_count": 0,
            "verified_passing_case_count": 10_434,
            "case_execution_denominator": 10_434,
            "public_api_operation_count": 111,
            "candidate_worker_count": 1, "reference_worker_count": 1,
            "exact_v33_adapter_sha256": ADAPTER_SHA,
            "exact_v33_native_engine_sha256": HISTORICAL_V33_ENGINE_SHA,
            "exact_v33_native_bridge_sha256": HISTORICAL_V33_BRIDGE_SHA,
            "historical_v33_public_pass_is_not_v35_public_evidence": True,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_qualified": False,
        },
        "safe_first_party_native_handle_lease": {
            "owners": [owner_document(row) for row in NATIVE_HANDLE_LEASE[:3]],
            "applied_bridge_receipt_owner":
                owner_document(NATIVE_HANDLE_LEASE[3]),
            "complete_contract_field_count": len(handle_lease_freeze),
            "application_field_count": len(handle_lease_application),
            "safe_bridge_source_sha256": BRIDGE_SOURCE_SHA,
            "safe_bridge_source_bytes": BRIDGE_SOURCE_BYTES,
            "operation_callback_sequence_count": 32_768,
            "synthetic_callback_finalization_count": 103_184,
            "synthetic_scanner_iterator_lifetime_case_count": 20_656,
            "synthetic_callback_exception_case_count": 20_480,
            "callback_and_dispatch_strong_owner_lease": True,
            "scanner_and_iterator_independent_owner_lease": True,
            "private_capsule_destructor_owns_native_engine": True,
            "synthetic_checks_counted_in_original_denominator": False,
            "actual_adversarial_callback_checks": NOT_MEASURED,
            "actual_repeated_finalizer_checks": NOT_MEASURED,
            "actual_scanner_after_finalization_checks": NOT_MEASURED,
            "actual_iterator_after_finalization_checks": NOT_MEASURED,
            "actual_undefined_behavior": NOT_MEASURED,
            "synthetic_safety_is_not_actual_crash_freedom": True,
            "candidate_qualified": False,
        },
        "immutable_failed_v27_preactivation_context": {
            "owners": [owner_document(row) for row in FAILED_V27],
            "complete_contract_field_count": len(failed_v27_freeze),
            "complete_failure_receipt_owner": owner_document(FAILED_V27_RECEIPT),
            "complete_failure_receipt_field_count": len(failed_v27_receipt),
            "failed_stage": "AUTHENTICATED V12 BASE BEFORE ACTIVATION",
            "failure_code": "STALE_V12_CORRECTED_ADAPTER_CONSTANTS",
            "failure_message":
                "reject stale V19 root, bridge, oracle, producer, guard, or recovery",
            "historical_v12_adapter_sha256": HISTORICAL_V25_ADAPTER_SHA,
            "historical_v12_adapter_bytes": HISTORICAL_V25_ADAPTER_BYTES,
            "required_v33_adapter_sha256": ADAPTER_SHA,
            "required_v33_adapter_bytes": ADAPTER_BYTES,
            "candidate_workers_started": 0,
            "activation_started": False, "canonical_targets_modified": False,
            "recovery_journal_created": False,
        },
        "exact_v12_adapter_constant_migration": {
            "authenticated_owner":
                "tools/run_owned_repaired_rust_original_campaign_v12.py",
            "historical_adapter_sha256": HISTORICAL_V25_ADAPTER_SHA,
            "historical_adapter_bytes": HISTORICAL_V25_ADAPTER_BYTES,
            "migrated_adapter_sha256": ADAPTER_SHA,
            "migrated_adapter_bytes": ADAPTER_BYTES,
            "exact_source_assignment_replacement_count": 2,
            "exact_authenticated_base_migration_count": 1,
            "all_other_migration_calls_unchanged": True,
            "canonical_candidate_source_modified": False,
        },
        "actual_v35_native_build": {
            "owners": [owner_document(row) for row in v33["rows"][:3]],
            "complete_contract_field_count": len(v33["freeze"]),
            "publication_receipt": v33["publication_owner"],
            "publication_receipt_field_count": len(v33["publication"]),
            "root_provenance_receipt": v33["root_owner"],
            "root_provenance_receipt_field_count": len(v33["root"]),
            "label": BUILD_LABEL, "build_status": "PASS",
            "actual_compiler_process_count": 28,
            "actual_compiler_process_ids": v33["actual_compiler_process_ids"],
            "independent_private_phase_count": 2,
            "independent_native_artifact_count": 4,
            "private_root_path": root["path"],
            "private_root_device": root["device"],
            "private_root_inode": root["inode"],
            "private_root_provenance":
                "AUTHENTICATED COMPLETE PUBLIC ROOT RECEIPT ONLY; NOT OPENED",
            "phase_native_identities": v33["phase_rows"],
            "native_engine_sha256": native["engine"]["sha256"],
            "native_engine_bytes": native["engine"].get(
                "size_bytes", native["engine"].get("bytes")),
            "native_bridge_sha256": native["bridge"]["sha256"],
            "native_bridge_bytes": native["bridge"].get(
                "size_bytes", native["bridge"].get("bytes")),
            "corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA,
            "corrected_bridge_source_bytes": BRIDGE_SOURCE_BYTES,
            "corrected_public_adapter_sha256": ADAPTER_SHA,
            "corrected_public_adapter_bytes": ADAPTER_BYTES,
            "optimized_engine_source_sha256": ENGINE_SOURCE_SHA,
            "optimized_engine_source_bytes": ENGINE_SOURCE_BYTES,
            "optimized_search_source_sha256": SEARCH_SOURCE_SHA,
            "optimized_search_source_bytes": SEARCH_SOURCE_BYTES,
            "archive_sha256_metadata_only": archive["sha256"],
            "archive_bytes_metadata_only": archive["bytes"],
            "archive_inode_metadata_only": archive["inode"],
            "archive_opened": False,
            "external_cargo_dependency_count": 0,
            "external_regular_expression_engine": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
        },
        "independent_runtime_non_delegation_v4_audit": {
            "owners": list(audit["owners"]),
            "actual_failure_receipt_owner": dict(audit["actual_failure_receipt_owner"]),
            "status": "FAIL", "finding_count": 1,
            "finding_code": "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE",
            "historical_public_matching_delegation": "NOT PROVEN",
            "historical_finding_is_not_new_corrected_bridge_audit": True,
            "new_corrected_runtime_audit": "NOT RUN",
            "exact_v35_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "exact_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "candidate_qualified": False,
            "audit_is_separate_from_original_correctness": True,
        },
        "operational_runtime_guard_v4": dict(guard),
        "original_correctness_boundary": {
            "case_execution_denominator": CASE_COUNT,
            "suite_count": WORKER_COUNT,
            "suites": [dict(row) for row in suites],
            "named_private_waiver_count": 13,
            "named_private_waivers": list(correctness["named_private_waivers"]),
            "supplemental_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
            "supplemental_counted_in_original_denominator": False,
            "corrected_reference_case_count": CORRECTED_REFERENCE_CASE_COUNT,
            "corrected_reference_counted_in_original_denominator": False,
            "candidate_correctness": NOT_MEASURED,
            "candidate_semantic_mismatch_count": NOT_MEASURED,
            "candidate_verified_passing_case_count": NOT_MEASURED,
            "candidate_original_oracle_pass": NOT_MEASURED,
            "original_suite_correctness_qualified": NOT_MEASURED,
            "candidate_qualified": False,
        },
        "actual_entry_policy": {
            "run": "IMPLEMENTED; ROOT AUTHORIZATION REQUIRED; NOT RUN",
            "worker": "IMPLEMENTED; ROOT AUTHORIZATION REQUIRED; NOT RUN",
            "recover": "IMPLEMENTED; ROOT AUTHORIZATION REQUIRED; NOT RUN",
            "requires_explicit_root_authorized_flag": True,
            "requires_frozen_committed_pushed_flag": True,
            "requires_identical_full_frozen_and_pushed_commit": True,
            "source_modes_install_public_wall_before_first_predecessor": True,
            "actual_modes_install_public_source_wall": False,
            "activation_label": LABEL, "activation_root": RECOVERY_ROOT,
            "recovery_lock_filename": LOCK_NAME,
            "recovery_role_order":
                list(previous["actual_entry_policy"]["recovery_role_order"]),
            "recovery_restoration_order":
                list(previous["actual_entry_policy"]["recovery_restoration_order"]),
            "requires_complete_v25_failure_receipt": True,
            "requires_complete_v26_original_pass_receipt": True,
            "requires_complete_v5_full_public_pass_receipt": True,
            "requires_complete_v27_failed_preactivation_freeze": True,
            "historical_v33_public_build_is_not_current_v35_build": True,
            "requires_exact_two_authenticated_v12_adapter_migrations": True,
            "requires_complete_v35_build_receipt": True,
            "requires_complete_v35_root_receipt": True,
            "requires_all_four_published_v35_phase_native_identities": True,
            "requires_independently_pinned_v4_guard": True,
            "requires_all_original_native_owner_fields": True,
            "canonical_engine_and_search_source_modified": False,
            "all_four_canonical_target_identities_restored": True,
            "full_original_pass_is_only_original_suite_qualification": True,
            "full_candidate_qualification_without_fresh_audit": "FORBIDDEN",
            "failed_worker_diagnostics":
                "COMPLETE INDIVIDUAL BOUNDED STDOUT STDERR TRACEBACK",
            "all_observation_vectors_and_mismatches": "REQUIRED",
            "source_wall_scope": "SOURCE MODES ONLY; NEVER ACTUAL ENTRY",
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
            "retired_final_proposal_opens": 0,
            "retired_final_proposal_metadata_probes": 0,
            "successor_final_proposal_opens": 0,
            "holdout_cases_opened": 0, "timing_trials_run": 0,
            "holdout": FINAL_HOLDOUT_STATUS,
            "historical_retired_holdout_proposal_case_count":
                HISTORICAL_HOLDOUT_CASE_COUNT,
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
    current = (None if rendering else dynamic_owner(
        wall, "contract", CONTRACT, options["contract_sha256"],
    ))
    parent = load_parent(wall)
    for name, row in zip(GUARD_PIN_NAMES, parent.GUARD_V4, strict=True):
        need(options[name] == row[2],
             "require independently pinned immutable operational V4 guard: " + name)
    parent_contract, parent_state = parent.load_source_context(
        wall, previous_options(parent, "--verify-frozen-context"), False,
    )
    failure = strict_document(
        parent, parent_state, secure_owner(wall, PREVIOUS_FAILURE),
        "complete independently observed actual original V25 FAIL-1352",
    )
    validate_previous_failure(parent, parent_contract, failure)
    rows = v35_rows(wall, options)
    for row in rows:
        secure_owner(wall, row)
    freeze = strict_document(parent, parent_state, secure_owner(wall, rows[2]),
                             "complete independently frozen V33 native source build")
    publication = strict_document(parent, parent_state,
                                  secure_owner(wall, rows[3]),
                                  "complete actual V33 native build publication")
    root = strict_document(parent, parent_state, secure_owner(wall, rows[4]),
                           "complete actual V33 private-root provenance")
    v33 = validate_v35_receipts(rows, freeze, publication, root, failure)
    for row in (*ORIGINAL_V26, ORIGINAL_V26_PASS, *PUBLIC_V5, PUBLIC_V5_PASS,
                *FAILED_V27, FAILED_V27_RECEIPT, *HISTORICAL_V33,
                *HISTORICAL_V28_CAMPAIGN, HISTORICAL_V33_ORIGINAL_PASS,
                *NATIVE_HANDLE_LEASE):
        secure_owner(wall, row)
    original_freeze = strict_document(
        parent, parent_state, secure_owner(wall, ORIGINAL_V26[2]),
        "complete separately frozen historical V26 original campaign",
    )
    original_pass = strict_document(
        parent, parent_state, secure_owner(wall, ORIGINAL_V26_PASS),
        "complete actual historical V26 original 31,237-case PASS",
    )
    public_freeze = strict_document(
        parent, parent_state, secure_owner(wall, PUBLIC_V5[2]),
        "complete separately frozen exact V33 public-correctness V5 campaign",
    )
    public_pass = strict_document(
        parent, parent_state, secure_owner(wall, PUBLIC_V5_PASS),
        "complete actual exact V33 public 10,434-case, 111-operation PASS",
    )
    validate_preserved_passes(original_freeze, original_pass,
                              public_freeze, public_pass, v33)
    failed_v27_freeze = strict_document(
        parent, parent_state, secure_owner(wall, FAILED_V27[2]),
        "complete independently committed V27 exact-V33 original freeze",
    )
    failed_v27_receipt = strict_document(
        parent, parent_state, secure_owner(wall, FAILED_V27_RECEIPT),
        "complete committed V27 preactivation FAIL without candidate activation",
    )
    validate_failed_v27_freeze(failed_v27_freeze, failed_v27_receipt, v33)
    historical_v33_freeze = strict_document(
        parent, parent_state, secure_owner(wall, HISTORICAL_V28_CAMPAIGN[2]),
        "complete immutable exact-V33 historical original campaign freeze",
    )
    historical_v33_pass = strict_document(
        parent, parent_state, secure_owner(wall, HISTORICAL_V33_ORIGINAL_PASS),
        "complete independently observed historical V33 original 31,237-case PASS",
    )
    validate_historical_v33_original(historical_v33_freeze, historical_v33_pass)
    handle_lease_freeze = strict_document(
        parent, parent_state, secure_owner(wall, NATIVE_HANDLE_LEASE[2]),
        "complete independent synthetic Rust native-handle ownership proof",
    )
    application_raw = secure_owner(wall, NATIVE_HANDLE_LEASE[3])
    handle_lease_application = parent_state["semantic"].StrictJSON(
        application_raw,
    ).decode()
    need(type(handle_lease_application) is dict,
         "require the complete hash-pinned formatted safe-bridge application")
    validate_native_handle_lease(handle_lease_freeze, handle_lease_application)
    contract = contract_document(source, protocol, parent, parent_contract,
                                 failure, v33, original_freeze, original_pass,
                                 public_freeze, public_pass,
                                 failed_v27_freeze, failed_v27_receipt,
                                 historical_v33_freeze, historical_v33_pass,
                                 handle_lease_freeze, handle_lease_application)
    if current is not None:
        found = strict_document(parent, parent_state, secure_owner(wall, current),
                                "complete independently frozen V29 original campaign")
        need(found == contract,
             "reject missing, altered, or additional V29 original obligations")
    need(not wall.live,
         "close every genuine authenticated public-source descriptor")
    no_matching_imports()
    return contract, {"parent": parent, "parent_contract": parent_contract,
                      "parent_state": parent_state, "failure": failure,
                      "v33": v33, "source": source, "protocol": protocol,
                      "original_v26_freeze": original_freeze,
                      "original_v26_pass": original_pass,
                      "public_v5_freeze": public_freeze,
                      "public_v5_pass": public_pass,
                      "failed_v27_freeze": failed_v27_freeze,
                      "failed_v27_receipt": failed_v27_receipt,
                      "historical_v33_freeze": historical_v33_freeze,
                      "historical_v33_pass": historical_v33_pass,
                      "handle_lease_freeze": handle_lease_freeze,
                      "handle_lease_application": handle_lease_application}


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
        return {**value, "__hostile_v29_extra_field__": True}
    raise CampaignError("reject unsupported frozen JSON mutation")


def reject(action: object, label: str, *kinds: type) -> str:
    need(callable(action), "require an executable genuine source-only control")
    try:
        action()
    except (CampaignError, OSError, ValueError, TypeError, KeyError,
            IndexError, UnicodeError, OverflowError, *kinds):
        return label
    raise CampaignError("accepted hostile V29 original authority: " + label)


def validate_complete_contract(parent: types.ModuleType, state: dict,
                               actual: dict, expected: dict) -> None:
    capture, semantic = state["capture"], state["semantic"]
    need(type(actual) is dict and set(actual) == set(expected)
         and capture.canonical_document(semantic, actual)
             == capture.canonical_document(semantic, expected),
         "reject omitted, additional, or altered complete V29 campaign freeze")


def source_controls(wall: PublicSourceWall, contract: dict, state: dict) -> list[str]:
    parent = state["parent"]
    inherited = parent.source_controls(wall, state["parent_contract"],
                                      state["parent_state"])
    kinds = (parent.CampaignError,
             state["parent_state"]["capture"].FreezeError,
             state["parent_state"]["semantic"].FreezeError)
    need(type(inherited) is list and len(inherited) > 1_800,
         "preserve every independently frozen V25/V24/V23 hostile control")
    checks = list(inherited)
    failure = state["failure"]
    for key in sorted(failure):
        altered = dict(failure)
        altered[key] = different(altered[key])
        checks.append(reject(
            lambda value=altered: validate_complete_contract(
                parent, state["parent_state"], value, failure),
            "reject-altered-complete-v25-actual-failure-" + key, *kinds))
    v33 = state["v33"]
    for name in ("publication", "root"):
        document = v33[name]
        for key in sorted(document):
            altered = dict(document)
            altered[key] = different(altered[key])
            checks.append(reject(
                lambda value=altered, expected=document:
                    validate_complete_contract(parent, state["parent_state"],
                                               value, expected),
                "reject-altered-complete-v33-" + name + "-" + key, *kinds))
    for name in ("original_v26_freeze", "original_v26_pass",
                 "public_v5_freeze", "public_v5_pass",
                 "failed_v27_freeze", "failed_v27_receipt",
                 "historical_v33_freeze", "historical_v33_pass",
                 "handle_lease_freeze", "handle_lease_application"):
        document = state[name]
        for key in sorted(document):
            altered = dict(document)
            altered[key] = different(altered[key])
            checks.append(reject(
                lambda value=altered, expected=document:
                    validate_complete_contract(parent, state["parent_state"],
                                               value, expected),
                "reject-altered-complete-" + name + "-" + key, *kinds))
    for relative, label in (
        ("candidates/rust_candidate.py", "candidate-adapter"),
        ("candidates/rust/py_bridge.c", "canonical-candidate-bridge-source"),
        ("candidates/rust/src/lib.rs", "canonical-candidate-engine-source"),
        ("candidates/rust/src/search.rs", "canonical-candidate-search-source"),
        ("candidates/_rust_engine.so", "installed-native-engine"),
        ("candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
         "installed-native-bridge"),
        ("oracle/phase3/expanded-sealed-holdout-v2.json", "retired-final-proposal"),
        ("oracle/phase3/expanded-sealed-holdout-v3.json", "successor-final-proposal"),
        (PUBLIC_RECEIPT_PATH.removesuffix("-publication-receipt.json") + ".json.gz",
         "compressed-native-build-archive"),
    ):
        checks.append(reject(
            lambda path=ROOT + "/" + relative:
                os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)),
            "reject-physical-v29-source-only-" + label, *kinds))
    for action, label in (
        (lambda: os.stat(v33["private_root"]["path"], follow_symlinks=False),
         "private-root-metadata"),
        (lambda: os.lstat(ROOT + "/oracle/phase3/expanded-sealed-holdout-v2.json"),
         "retired-final-proposal-metadata"),
        (lambda: time.time(), "correctness-clock"),
    ):
        checks.append(reject(action, "reject-source-only-" + label, *kinds))
    for key in sorted(contract):
        changed = dict(contract)
        changed[key] = different(changed[key])
        checks.append(reject(
            lambda value=changed: validate_complete_contract(
                parent, state["parent_state"], value, contract),
            "reject-altered-complete-v29-section-" + key, *kinds))
    need(wall.installed and not wall.live and bool(wall.blocked)
         and len(checks) > len(inherited) + 100,
         "require complete physically sterile V29 public-only hostile controls")
    no_matching_imports()
    return checks


def legacy_row(row: tuple) -> tuple:
    need(type(row) is tuple and len(row) == 5,
         "require one exact legacy-compatible immutable owner")
    return row[1], row[2], row[3], row[4]


def migrate_parent(previous: types.ModuleType, owner: tuple) -> types.ModuleType:
    raw = previous.secure_owner(owner)
    tree = ast.parse(raw, filename=owner[0])

    class ExactV29Literals(ast.NodeTransformer):
        def __init__(self) -> None:
            self.count = 0

        def visit_Constant(self, node: ast.Constant) -> ast.AST:
            if type(node.value) is str and (
                    "v21" in node.value or "V21" in node.value):
                self.count += 1
                return ast.copy_location(ast.Constant(
                    value=node.value.replace("v21", "v29")
                                    .replace("V21", "V29")), node)
            return node

    migration = ExactV29Literals()
    tree = migration.visit(tree)
    need(migration.count >= 20,
         "retain exact authenticated V21-to-V29 original runner migration")
    module = types.ModuleType("_rebar_v29_independently_migrated_original_parent")
    module.__file__ = ROOT + "/" + owner[0]
    module._v29_literal_migration_count = migration.count
    exec(compile(ast.fix_missing_locations(tree), module.__file__, "exec",
                 dont_inherit=True), module.__dict__)
    return module


def normalized_receipts(v33: dict) -> tuple[dict, dict]:
    publication = dict(v33["publication"])
    publication["archive_publication"] = dict(v33["archive"])
    root = dict(v33["root"])
    root["root"] = {**v33["private_root"],
                    "phase_count": 2,
                    "uid": os.geteuid(),
                    "directory_scanned": False,
                    "phases": list(v33["phase_rows"])}
    return publication, root


def canonical_native_owner(owner: dict, role: str, v33: dict) -> dict:
    keys = frozenset(("role", "family", "absolute_path", "relative", "file_name",
                      "sha256", "bytes", "size_bytes", "device", "inode", "mode",
                      "uid", "nlink", "native_loaded"))
    output = v33["native_outputs"][role]
    expected_bytes = output.get("size_bytes", output.get("bytes"))
    need(type(owner) is dict and set(owner) == keys
         and owner.get("role") == role and owner.get("family") == FAMILY
         and owner.get("sha256") == output["sha256"]
         and owner.get("bytes") == expected_bytes
         and owner.get("size_bytes") == expected_bytes
         and owner.get("absolute_path") == ROOT + "/" + str(owner.get("relative"))
         and type(owner.get("relative")) is str
         and owner["relative"].startswith("candidates/")
         and ".." not in owner["relative"].split("/")
         and owner.get("device") == DEVICE
         and type(owner.get("inode")) is int and owner["inode"] > 0
         and owner.get("mode") == 0o600
         and owner.get("uid") == os.geteuid()
         and owner.get("nlink") == 1 and owner.get("native_loaded") is False,
         "reject stale, preloaded, external, or noncanonical native " + role)
    return owner


def install_original_only_qualification(legacy: types.ModuleType) -> None:
    """Keep a complete original PASS separate from full candidate qualification."""
    names = ("validate_v16_publication_report",
             "validate_v11_publication_report")
    found = [(name, getattr(legacy, name, None)) for name in names
             if callable(getattr(legacy, name, None))]
    need(len(found) == 1,
         "authenticate the unique immutable original-publication validator")
    validator_name, original_validator = found[0]
    original_publisher = getattr(legacy, "preserve_actual_campaign", None)
    need(callable(original_publisher),
         "retain the complete authenticated original durable publisher")

    def validate_original(report: dict, source: str, protocol: str,
                          contract: str) -> dict:
        original_pass = (type(report) is dict
                         and report.get("status") == "PASS"
                         and report.get("candidate_original_oracle_pass") is True
                         and report.get("original_suite_correctness_qualified") is True
                         and report.get("candidate_qualified") is False)
        if not original_pass:
            return original_validator(report, source, protocol, contract)
        historical = dict(report)
        historical["candidate_qualified"] = True
        checked = original_validator(historical, source, protocol, contract)
        need(type(checked) is dict
             and checked.get("status") == "PASS"
             and checked.get("candidate_qualified") is True,
             "authenticate every immutable original PASS obligation first")
        checked["candidate_qualified"] = False
        checked["candidate_original_oracle_pass"] = True
        checked["original_suite_correctness_qualified"] = True
        checked["runtime_non_delegation"] = "NOT ESTABLISHED"
        checked["final_holdout"] = FINAL_HOLDOUT_STATUS
        return checked

    setattr(legacy, validator_name, validate_original)

    def publish_original(report: dict, helper: object, recovery: object,
                         publication: object, ledger: dict) -> dict:
        need(type(report) is dict
             and report.get("suite_count") == WORKER_COUNT
             and report.get("case_execution_denominator") == CASE_COUNT,
             "publish only a complete genuine original-suite outcome")
        original_pass = report.get("status") == "PASS"
        if original_pass:
            rows = report.get("suite_results")
            need(report.get("candidate_qualified") is True
                 and report.get("actual_candidate_workers") == WORKER_COUNT
                 and report.get("distinct_worker_process_id_count") == WORKER_COUNT
                 and report.get("completed_suite_count") == WORKER_COUNT
                 and report.get("verified_passing_case_count") == CASE_COUNT
                 and report.get("semantic_mismatch_count") == 0
                 and report.get("infrastructure_failure_count") == 0
                 and type(rows) is list and len(rows) == WORKER_COUNT
                 and all(type(row) is dict
                         and row.get("fully_observed") is True
                         and row.get("actual_worker_started") is True
                         and row.get("failure_class") == "PASS"
                         and row.get("mismatch_count") == 0
                         and row.get("verified_passing_case_count")
                             == row.get("case_execution_denominator")
                         for row in rows),
                 "never relabel partial, guessed, or mismatched cases original PASS")
        candidate = dict(report)
        candidate["candidate_original_oracle_pass"] = original_pass
        candidate["original_suite_correctness_qualified"] = original_pass
        candidate["candidate_qualified"] = False
        candidate["runtime_non_delegation"] = "NOT ESTABLISHED"
        candidate["final_holdout"] = FINAL_HOLDOUT_STATUS
        original_writer = getattr(recovery, "write_evidence_receipt", None)
        need(callable(original_writer),
             "retain the authentic fsynced V2 original-evidence writer")

        def write_original(name: str, receipt: dict) -> dict:
            need(type(receipt) is dict
                 and receipt.get("candidate_status")
                     == ("PASS" if original_pass else "FAIL")
                 and receipt.get("candidate_qualified") is False
                 and receipt.get("suite_count") == WORKER_COUNT
                 and receipt.get("case_execution_denominator") == CASE_COUNT
                 and receipt.get("all_four_original_targets_restored") is True,
                 "never qualify an original PASS before fresh non-delegation audit")
            receipt["candidate_original_oracle_pass"] = original_pass
            receipt["original_suite_correctness_qualified"] = original_pass
            receipt["candidate_qualified"] = False
            receipt["runtime_non_delegation"] = "NOT ESTABLISHED"
            receipt["final_holdout"] = FINAL_HOLDOUT_STATUS
            receipt["historical_runtime_non_delegation_v4_status"] = "FAIL"
            return original_writer(name, receipt)

        recovery.write_evidence_receipt = write_original
        try:
            result = original_publisher(candidate, helper, recovery,
                                        publication, ledger)
        finally:
            recovery.write_evidence_receipt = original_writer
        need(recovery.write_evidence_receipt is original_writer
             and type(result) is dict
             and result.get("status")
                 == ("PASS" if original_pass else "FAIL")
             and result.get("candidate_qualified") is False,
             "restore the genuine writer and separate original matching qualification")
        result["candidate_original_oracle_pass"] = original_pass
        result["original_suite_correctness_qualified"] = original_pass
        result["candidate_qualified"] = False
        result["runtime_non_delegation"] = "NOT ESTABLISHED"
        result["final_holdout"] = FINAL_HOLDOUT_STATUS
        return result

    legacy.preserve_actual_campaign = publish_original


def corrected_controller(helper: types.ModuleType, campaign: types.ModuleType,
                         parent: types.ModuleType, historical: dict,
                         canonical_sources: tuple, private_sources: tuple):
    owners = historical["historical_owners"]
    historical_values = historical["v7_values"]

    def bind(state: dict, context: dict, bundle: dict | None,
             counts: dict[str, int]) -> types.ModuleType:
        runner, base, guard = state["runner"], state["base"], state["guard"]
        legacy = runner.bind_v16_legacy(context, guard, base, bundle, counts)
        fixed = campaign.replace_exact_recovery_prefix(legacy)
        need(fixed["status"] == "PASS"
             and fixed["recovery_code_constants_changed"] == 1
             and fixed["production_wrapper_added"] is False,
             "retain the exact authenticated one-constant V20 recovery proof")
        originals = tuple(legacy.SOURCE_OWNERS)
        need(len(originals) == 9,
             "preserve all nine authenticated original Rust source owners")
        legacy.COMBINED_BRIDGE_SHA256 = parent.CAPTURE_SHA
        legacy.COMBINED_BRIDGE_BYTES = parent.CAPTURE_BYTES
        legacy.CORRECTED_ADAPTER_SHA256 = parent.ADAPTER_SHA
        legacy.CORRECTED_ADAPTER_BYTES = parent.ADAPTER_BYTES
        legacy.SOURCE_OWNERS = private_sources
        private_source_tuples = tuple(legacy.corrected_source_tuples())
        need(private_source_tuples == private_sources
             and parent.CORRECTED_SOURCES == canonical_sources,
             "separate exact private V33 build sources from canonical active owners")
        legacy.corrected_source_tuples = lambda: parent.CORRECTED_SOURCES
        need(tuple(legacy.corrected_source_tuples()) == canonical_sources,
             "preserve all unchanged canonical engine/search owner identities")
        previous_loader = legacy.load_frozen_module

        def historical_first_loader(owner: object,
                                    name: str) -> types.ModuleType:
            module = previous_loader(owner, name)
            if (type(module) is types.ModuleType
                    and getattr(module, "SCHEMA", None)
                        == "rebar-owned-repaired-rust-original-campaign-v7"):
                original_rows = tuple(module.ORIGINAL_SOURCE_OWNERS)
                need(len(original_rows) == 9
                     and original_rows[0]
                         == ("candidates/rust_candidate.py",
                             "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
                             31_151)
                     and original_rows[1]
                         == ("candidates/rust/py_bridge.c",
                             "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
                             175_676)
                     and original_rows[2:] == canonical_sources[2:]
                     and tuple(module.HISTORICAL_V2_REPAIRED_SOURCE_OWNERS)
                         == owners
                     and module.BRIDGE_SOURCE_SHA256
                         == historical_values["BRIDGE_SOURCE_SHA256"]
                     and module.BRIDGE_SOURCE_BYTES
                         == historical_values["BRIDGE_SOURCE_BYTES"]
                     and module.HISTORICAL_V2_REPAIRED_PUBLIC_SHA256
                         == historical_values[
                             "HISTORICAL_V2_REPAIRED_PUBLIC_SHA256"]
                     and module.HISTORICAL_V2_REPAIRED_PUBLIC_BYTES
                         == historical_values[
                             "HISTORICAL_V2_REPAIRED_PUBLIC_BYTES"]
                     and module.CORRECTED_PUBLIC_SHA256
                         == historical_values["CORRECTED_PUBLIC_SHA256"]
                     and module.CORRECTED_PUBLIC_BYTES
                         == historical_values["CORRECTED_PUBLIC_BYTES"]
                     and module.ENGINE_SHA256 == HISTORICAL_V25_ENGINE_SHA
                     and module.BRIDGE_SHA256
                         == historical_values["BRIDGE_SHA256"]
                     and callable(module.patched_v2_helpers),
                     "retain immutable V7/V2 provenance before private V33 promotion")
                module.CORRECTED_SOURCE_OWNERS = parent.CORRECTED_SOURCES
            if (bundle is not None and type(module) is types.ModuleType
                    and getattr(module, "SCHEMA", None)
                        == "rebar-owned-six-family-original-p0-producer-v5"):
                need(getattr(owner, "path", None) == helper.PRODUCER[0]
                     and getattr(owner, "sha256", None) == helper.PRODUCER[1],
                     "patch only the authentic guard-bound V5 Rust observer")
                helper.install_family_aware_observers(module, bundle, parent)
            return module

        legacy.load_frozen_module = historical_first_loader
        legacy.LOCK_NAME = LOCK_NAME
        need(legacy.SCHEMA == SCHEMA and legacy.LABEL == LABEL
             and legacy.PUBLIC_RECOVERY_PRIVATE_PREFIX == RECOVERY_PREFIX
             and legacy.PUBLIC_RECOVERY_ROOT == RECOVERY_ROOT
             and legacy.BUILD_LABEL == BUILD_LABEL
             and legacy.VERIFIED_BUILD_PRIVATE_ROOT == parent.ROOT_PATH
             and legacy.VERIFIED_BUILD_PRIVATE_ROOT_DEVICE == parent.ROOT_DEVICE
             and legacy.VERIFIED_BUILD_PRIVATE_ROOT_INODE == parent.ROOT_INODE
             and legacy.VERIFIED_NATIVE_ENGINE_SHA256 == parent.ENGINE_SHA
             and legacy.VERIFIED_NATIVE_ENGINE_BYTES == parent.ENGINE_BYTES
             and legacy.VERIFIED_NATIVE_BRIDGE_SHA256 == parent.BRIDGE_SHA
             and legacy.VERIFIED_NATIVE_BRIDGE_BYTES == parent.BRIDGE_BYTES
             and legacy.BUILD[0].sha256 == parent.V21[0][1]
             and legacy.BUILD_RECEIPT.sha256 == parent.V21_PUBLICATION[1]
             and tuple(legacy.ROLE_ORDER) == tuple(base.ROLE_ORDER)
             and tuple(legacy.SUITES) == parent.SUITES,
             "retain four exact recoverable owners and all original V33 workers")
        if bundle is None:
            helper.install_full_failure_publication(legacy, parent)
            install_original_only_qualification(legacy)
        return legacy

    return bind


def build_v33_parent(parent25: types.ModuleType, previous22: types.ModuleType,
                     previous21: types.ModuleType, old_state: dict,
                     operational: types.ModuleType, v33: dict,
                     options: dict) -> dict:
    loaded = old_state["loaded"]
    ancestor = loaded["ancestor"]
    original_parent = loaded["state"]["parent"]
    original_base = loaded["state"]["original_base"]
    need(type(operational) is types.ModuleType
         and operational.SELF == parent25.GUARD_V4[0][1]
         and operational.PROTOCOL == parent25.GUARD_V4[1][1]
         and operational.CONTRACT == parent25.GUARD_V4[2][1],
         "reuse the one already authenticated exact V4 operational namespace")
    parent = migrate_parent(previous21, ancestor.V17[0])
    canonical = tuple(
        (path, BRIDGE_SOURCE_SHA, BRIDGE_SOURCE_BYTES)
        if path == "candidates/rust/py_bridge.c"
        else (path, ADAPTER_SHA, ADAPTER_BYTES)
        if path == "candidates/rust_candidate.py"
        else (path, fingerprint, count)
        for path, fingerprint, count in tuple(loaded["parent"].CORRECTED_SOURCES)
    )
    private_sources = tuple(
        (path, ENGINE_SOURCE_SHA, ENGINE_SOURCE_BYTES)
        if path == "candidates/rust/src/lib.rs"
        else (path, SEARCH_SOURCE_SHA, SEARCH_SOURCE_BYTES)
        if path == "candidates/rust/src/search.rs"
        else (path, fingerprint, count)
        for path, fingerprint, count in canonical
    )
    outputs = v33["native_outputs"]
    engine = outputs["engine"]
    bridge = outputs["bridge"]
    root = v33["private_root"]
    phase_native_inodes = tuple(tuple(item["inode"]
                                      for item in phase["native_outputs"])
                                for phase in v33["phase_rows"])
    archive = v33["archive"]
    build_rows = v33["rows"][:3]
    public_row, root_row = v33["rows"][3:]
    values = {
        "SOURCE": SOURCE, "PROTOCOL": PROTOCOL, "CONTRACT": CONTRACT,
        "SCHEMA": SCHEMA, "VERSION": VERSION, "FAMILY": FAMILY,
        "BUILD_LABEL": BUILD_LABEL, "BUILD_SUFFIX": BUILD_SUFFIX,
        "LABEL": LABEL, "RECOVERY_PREFIX": RECOVERY_PREFIX,
        "RECOVERY_ROOT": RECOVERY_ROOT,
        "V21": tuple(legacy_row(row) for row in build_rows),
        "V21_PUBLICATION": legacy_row(public_row),
        "V21_ROOT": legacy_row(root_row),
        "ROOT_DEVICE": root["device"], "ROOT_INODE": root["inode"],
        "ROOT_PATH": root["path"], "ENGINE_SHA": engine["sha256"],
        "ENGINE_BYTES": engine.get("size_bytes", engine.get("bytes")),
        "BRIDGE_SHA": bridge["sha256"],
        "BRIDGE_BYTES": bridge.get("size_bytes", bridge.get("bytes")),
        "CAPTURE_SHA": BRIDGE_SOURCE_SHA,
        "CAPTURE_BYTES": BRIDGE_SOURCE_BYTES,
        "ADAPTER_SHA": ADAPTER_SHA, "ADAPTER_BYTES": ADAPTER_BYTES,
        "ARCHIVE_SHA": archive["sha256"],
        "ARCHIVE_BYTES": archive["bytes"],
        "ARCHIVE_INODE": archive["inode"],
        "PLAIN_SHA": v33["uncompressed_sha256"],
        "PLAIN_BYTES": v33["uncompressed_bytes"],
        "PHASE_NATIVE_INODES": phase_native_inodes,
        "CORRECTED_SOURCES": canonical,
    }
    for key, value in values.items():
        setattr(parent, key, value)

    def validate(build: dict, root_document: dict, freeze: dict) -> dict:
        return validate_v35_receipts(v33["rows"], freeze, build,
                                     root_document, v33["previous_failure"])

    parent.validate_v21_documents = validate
    inherited_migration = parent.migrate_assignments
    adapter_migration_count = 0

    def migrate_exact_v12_adapter(raw: bytes, path: str, expected: dict,
                                  replacements: dict, *,
                                  route_constants: bool = False) -> ast.Module:
        nonlocal adapter_migration_count
        v12_owner = original_parent.V12[0]
        if path != v12_owner[0]:
            return inherited_migration(raw, path, expected, replacements,
                                       route_constants=route_constants)
        need(adapter_migration_count == 0
             and route_constants is False
             and type(raw) is bytes and sha(raw) == v12_owner[1]
             and original_base.CORRECTED_ADAPTER_SHA
                 == HISTORICAL_V25_ADAPTER_SHA
             and original_base.CORRECTED_ADAPTER_BYTES
                 == HISTORICAL_V25_ADAPTER_BYTES
             and "CORRECTED_ADAPTER_SHA" not in expected
             and "CORRECTED_ADAPTER_BYTES" not in expected
             and "CORRECTED_ADAPTER_SHA" not in replacements
             and "CORRECTED_ADAPTER_BYTES" not in replacements,
             "authenticate exactly one unmodified V12 adapter migration boundary")
        previous = {
            **expected,
            "CORRECTED_ADAPTER_SHA": HISTORICAL_V25_ADAPTER_SHA,
            "CORRECTED_ADAPTER_BYTES": HISTORICAL_V25_ADAPTER_BYTES,
        }
        corrected = {
            **replacements,
            "CORRECTED_ADAPTER_SHA": ADAPTER_SHA,
            "CORRECTED_ADAPTER_BYTES": ADAPTER_BYTES,
        }
        tree = inherited_migration(raw, path, previous, corrected,
                                   route_constants=False)
        adapter_migration_count += 1
        return tree

    parent.migrate_assignments = migrate_exact_v12_adapter
    base = parent.make_v21_base(original_parent, original_base,
                                v33["publication"], v33["root"], v33["freeze"])
    need(adapter_migration_count == 1
         and base.CORRECTED_ADAPTER_SHA == ADAPTER_SHA
         and base.CORRECTED_ADAPTER_BYTES == ADAPTER_BYTES,
         "migrate exactly two authenticated V12 adapter constants to V33")
    original_authentication = base.authenticate_root_receipts

    def authenticate(guard: types.ModuleType) -> tuple[dict, dict]:
        observed_public, observed_root = original_authentication(guard)
        need(observed_public == v33["publication"]
             and observed_root == v33["root"],
             "reauthenticate exact actual V33 receipts before private normalization")
        return normalized_receipts(v33)

    base.authenticate_root_receipts = authenticate
    need(tuple(base.GUARD) == tuple(original_base.GUARD)
         and base.BUILD == tuple(legacy_row(row) for row in build_rows)
         and base.BUILD_RECEIPT == legacy_row(public_row)
         and base.ROOT_RECEIPT == legacy_row(root_row)
         and base.BUILD_LABEL == BUILD_LABEL and base.ROOT_PATH == root["path"]
         and base.ROOT_DEVICE == root["device"]
         and base.ROOT_INODE == root["inode"]
         and base.ENGINE_SHA == engine["sha256"]
         and base.BRIDGE_SHA == bridge["sha256"]
         and tuple(base.P0) == tuple(original_base.P0)
         and tuple(base.PRODUCER) == tuple(original_base.PRODUCER)
         and tuple(base.ROLE_ORDER) == tuple(original_base.ROLE_ORDER),
         "reject substituted V33 roots, native owners, V2/V5 guard, or recovery")
    base.load_guard = lambda: operational
    original_install = base.install_worker_guard

    def exact_guard_install(guard: types.ModuleType) -> dict:
        need(guard is operational,
             "install only independently frozen operational V4 before Rust")
        bundle = original_install(guard)
        need(type(bundle) is dict
             and type(bundle.get("policy")) is operational.RuntimePolicy
             and bundle["policy"].installed is True
             and bundle.get("candidate") is sys.modules.get("re")
             and bundle.get("candidate")
                 is sys.modules.get("candidates.rust_candidate")
             and "_sre" not in sys.modules and "ctypes" not in sys.modules,
             "install genuine V4 before exactly one first-party Rust import")
        for role in ("engine", "bridge"):
            expected = canonical_native_owner(bundle[role], role, v33)
            need(bundle[role] == expected
                 and getattr(bundle["policy"], role + "_owner") == expected,
                 "prepare only exact immutable 14-field V33 native " + role)
        bundle["policy"].check_modules()
        return bundle

    base.install_worker_guard = exact_guard_install
    runner = parent.make_runner(original_parent)
    need(runner.SOURCE == SOURCE and runner.PROTOCOL == PROTOCOL
         and runner.CONTRACT == CONTRACT and runner.SCHEMA == SCHEMA
         and runner.LABEL == LABEL and runner.RECOVERY_PREFIX == RECOVERY_PREFIX
         and runner.RECOVERY_ROOT == RECOVERY_ROOT
         and tuple(runner.SUITES) == tuple(previous21.SUITES)
         and runner.WORKER_COUNT == WORKER_COUNT
         and runner.CASE_COUNT == CASE_COUNT,
         "migrate the unchanged 13-worker original controller to V33 matching")
    inherited = runner.actual_required_authority

    def required(actual_base: types.ModuleType) -> dict[str, str]:
        result = dict(inherited(actual_base))
        result.update({
            "combined_bridge_sha256": BRIDGE_SOURCE_SHA,
            "combined_bridge_bytes": str(BRIDGE_SOURCE_BYTES),
            "optimized_engine_source_sha256": ENGINE_SOURCE_SHA,
            "optimized_search_source_sha256": SEARCH_SOURCE_SHA,
            "guard_v4_source_sha256": parent25.GUARD_V4[0][2],
            "guard_v4_protocol_sha256": parent25.GUARD_V4[1][2],
            "guard_v4_contract_sha256": parent25.GUARD_V4[2][2],
            "operational_guard_v3_source_sha256": parent25.V3[0][1],
            "operational_guard_v3_protocol_sha256": parent25.V3[1][1],
            "operational_guard_v3_contract_sha256": parent25.V3[2][1],
            "previous_v22_source_sha256": parent25.V22[0][2],
            "previous_v22_protocol_sha256": parent25.V22[1][2],
            "previous_v22_contract_sha256": parent25.V22[2][2],
            "previous_v22_failure_receipt_sha256": parent25.V22_FAILURE_SHA,
            "previous_v23_source_sha256": parent25.V23[0][2],
            "previous_v23_protocol_sha256": parent25.V23[1][2],
            "previous_v23_contract_sha256": parent25.V23[2][2],
            "previous_v24_source_sha256": parent25.PREVIOUS_V24[0][2],
            "previous_v24_protocol_sha256": parent25.PREVIOUS_V24[1][2],
            "previous_v24_contract_sha256": parent25.PREVIOUS_V24[2][2],
            "previous_v24_failure_receipt_sha256": parent25.V24_FAILURE[2],
            "previous_v25_source_sha256": PREVIOUS[0][2],
            "previous_v25_protocol_sha256": PREVIOUS[1][2],
            "previous_v25_contract_sha256": PREVIOUS[2][2],
            "previous_v25_failure_receipt_sha256": PREVIOUS_FAILURE[2],
            "previous_v26_source_sha256": ORIGINAL_V26[0][2],
            "previous_v26_protocol_sha256": ORIGINAL_V26[1][2],
            "previous_v26_contract_sha256": ORIGINAL_V26[2][2],
            "previous_v26_original_pass_receipt_sha256": ORIGINAL_V26_PASS[2],
            "previous_v27_source_sha256": FAILED_V27[0][2],
            "previous_v27_protocol_sha256": FAILED_V27[1][2],
            "previous_v27_contract_sha256": FAILED_V27[2][2],
            "previous_v27_preactivation_failure_receipt_sha256":
                FAILED_V27_RECEIPT[2],
            "full_public_v5_source_sha256": PUBLIC_V5[0][2],
            "full_public_v5_protocol_sha256": PUBLIC_V5[1][2],
            "full_public_v5_contract_sha256": PUBLIC_V5[2][2],
            "full_public_v5_pass_receipt_sha256": PUBLIC_V5_PASS[2],
            "independent_nondelegation_v4_source_sha256":
                parent25.AUDIT_V4[0][2],
            "independent_nondelegation_v4_protocol_sha256":
                parent25.AUDIT_V4[1][2],
            "independent_nondelegation_v4_contract_sha256":
                parent25.AUDIT_V4[2][2],
            "independent_nondelegation_v4_failure_receipt_sha256":
                parent25.AUDIT_V4_FAILURE[2],
            "previous_v21_preactivation_failure_receipt_sha256":
                parent25.V21_FAILURE_SHA,
            **{name: options[name] for name in V35_PIN_NAMES},
            "frozen_commit": options["frozen_commit"],
            "pushed_commit": options["pushed_commit"],
        })
        return result

    runner.actual_required_authority = required
    old_worker_arguments = runner.v16_worker_arguments

    def worker_arguments(namespace: types.SimpleNamespace, suite: str,
                         active: dict, original: types.ModuleType) -> list[str]:
        return [*old_worker_arguments(namespace, suite, active, original),
                "--root-authorized", "--frozen-committed-pushed"]

    runner.v16_worker_arguments = worker_arguments
    runner.bounded_diagnostic_traceback = previous21.bounded_unicode_traceback
    history = previous21.bootstrap(loaded["module"].V19[0],
                                  "_rebar_v29_authenticated_historical_v19")
    helper = previous21.bootstrap(previous21.V20[0],
                                 "_rebar_v29_exact_historical_v20_observer")
    for module in (history, helper):
        for name, value in (("SCHEMA", SCHEMA), ("VERSION", VERSION),
                            ("SOURCE", SOURCE), ("PROTOCOL", PROTOCOL),
                            ("CONTRACT", CONTRACT), ("BUILD_LABEL", BUILD_LABEL),
                            ("BUILD_SUFFIX", BUILD_SUFFIX), ("LABEL", LABEL),
                            ("RECOVERY_PREFIX", RECOVERY_PREFIX),
                            ("RECOVERY_ROOT", RECOVERY_ROOT)):
            setattr(module, name, value)
    parent.bind_captured_controller = corrected_controller(
        helper, history, parent, loaded["history"], canonical,
        private_sources,
    )
    return {"parent": parent, "base": base, "runner": runner,
            "guard": operational, "original_base": original_base,
            "historical_parent": original_parent, "helper": helper,
            "historical_campaign": history, "build": v33["publication"],
            "root": v33["root"], "freeze": v33["freeze"],
            "required": required(base), "previous_v22": previous22,
            "previous_v21": previous21, "old_v22_state": old_state,
            "v33": v33}


def actual_context(options: dict) -> tuple[dict, dict]:
    parent25 = load_parent(None)
    for row in (*PREVIOUS, PREVIOUS_FAILURE, *ORIGINAL_V26, ORIGINAL_V26_PASS,
                *PUBLIC_V5, PUBLIC_V5_PASS, *FAILED_V27, FAILED_V27_RECEIPT,
                *HISTORICAL_V33, *HISTORICAL_V28_CAMPAIGN,
                HISTORICAL_V33_ORIGINAL_PASS, *NATIVE_HANDLE_LEASE,
                *parent25.GUARD_V4):
        secure_owner(None, row)
    parent_context, parent_state = parent25.actual_context(
        previous_options(parent25, options["mode"]),
    )
    previous22 = parent_state["previous_v22"]
    previous21 = parent_state["previous_v21"]
    old_state = parent_state["old_v22_state"]
    original_base, guard = old_state["original_base"], old_state["guard"]

    def document(row: tuple, label: str) -> dict:
        raw = secure_owner(None, row)
        result = original_base.parse_document(guard, raw, label)
        need(type(result) is dict and guard.canonical(result) == raw,
             "reject altered complete actual public document: " + label)
        return result

    previous = document(PREVIOUS[2], "complete immutable V25 original campaign")
    failure = document(PREVIOUS_FAILURE, "complete original V25 candidate FAIL-1352")
    validate_previous_failure(parent25, previous, failure)
    rows = v35_rows(None, options)
    for row in rows:
        secure_owner(None, row)
    freeze = document(rows[2], "complete authentic V35 native source freeze")
    publication = document(rows[3], "complete successful V35 native build")
    root = document(rows[4], "complete successful V35 native root provenance")
    v33 = validate_v35_receipts(rows, freeze, publication, root, failure)
    original_freeze = document(ORIGINAL_V26[2],
                               "complete historical V26 original campaign")
    original_pass = document(ORIGINAL_V26_PASS,
                             "complete historical 31,237-case original PASS")
    public_freeze = document(PUBLIC_V5[2],
                             "complete exact V33 public V5 campaign")
    public_pass = document(PUBLIC_V5_PASS,
                           "complete exact V33 10,434-case public PASS")
    validate_preserved_passes(original_freeze, original_pass,
                              public_freeze, public_pass, v33)
    failed_v27_freeze = document(FAILED_V27[2],
                                 "complete immutable V27 exact-V33 freeze")
    failed_v27_receipt = document(FAILED_V27_RECEIPT,
                                  "complete immutable V27 preactivation FAIL")
    validate_failed_v27_freeze(failed_v27_freeze, failed_v27_receipt, v33)
    historical_v33_freeze = document(
        HISTORICAL_V28_CAMPAIGN[2], "complete historical exact-V33 original freeze",
    )
    historical_v33_pass = document(
        HISTORICAL_V33_ORIGINAL_PASS, "complete historical V33 original PASS",
    )
    validate_historical_v33_original(historical_v33_freeze, historical_v33_pass)
    handle_lease_freeze = document(
        NATIVE_HANDLE_LEASE[2], "complete synthetic Rust native-handle lease proof",
    )
    handle_lease_application = original_base.parse_document(
        guard, secure_owner(None, NATIVE_HANDLE_LEASE[3]),
        "complete hash-pinned formatted safe Rust bridge application",
    )
    validate_native_handle_lease(handle_lease_freeze, handle_lease_application)
    source = dynamic_owner(None, "source", SOURCE, options["source_sha256"])
    protocol = dynamic_owner(None, "protocol", PROTOCOL,
                             options["protocol_sha256"])
    contract_row = dynamic_owner(None, "contract", CONTRACT,
                                 options["contract_sha256"])
    actual_contract = document(contract_row, "complete frozen V29 original campaign")
    expected = contract_document(source, protocol, parent25, previous, failure,
                                 v33, original_freeze, original_pass,
                                 public_freeze, public_pass,
                                 failed_v27_freeze, failed_v27_receipt,
                                 historical_v33_freeze, historical_v33_pass,
                                 handle_lease_freeze, handle_lease_application)
    need(actual_contract == expected,
         "reject an incomplete V29 original campaign before reversible activation")
    state = build_v33_parent(parent25, previous22, previous21, old_state,
                             parent_state["guard"], v33, options)
    context = dict(parent_context)
    context.update({"schema": SCHEMA + "-frozen-context", "version": VERSION,
                    "source_sha256": options["source_sha256"],
                    "protocol_sha256": options["protocol_sha256"],
                    "contract_sha256": options["contract_sha256"],
                    "public_recovery_root": RECOVERY_ROOT,
                    "recovery_lock_filename": LOCK_NAME,
                    "actual_v35_build_receipt_sha256": rows[3][2],
                    "actual_v35_root_receipt_sha256": rows[4][2],
                    "actual_v35_native_engine_sha256":
                        v33["native_outputs"]["engine"]["sha256"],
                    "actual_v35_native_bridge_sha256":
                        v33["native_outputs"]["bridge"]["sha256"],
                    "actual_v35_safe_bridge_source_sha256": BRIDGE_SOURCE_SHA,
                    "actual_v35_corrected_adapter_sha256": ADAPTER_SHA,
                    "historical_v33_original_pass_receipt_sha256":
                        HISTORICAL_V33_ORIGINAL_PASS[2],
                    "historical_v33_wider_public_pass_receipt_sha256":
                        PUBLIC_V5_PASS[2],
                    "safe_native_handle_lease_application_sha256":
                        NATIVE_HANDLE_LEASE[3][2],
                    "actual_v25_original_failure_receipt_sha256":
                        PREVIOUS_FAILURE[2],
                    "actual_v25_candidate_status": "FAIL",
                    "actual_v25_semantic_mismatch_count": 1352,
                    "actual_v25_verified_passing_case_count": 15_877,
                    "actual_v26_original_pass_receipt_sha256":
                        ORIGINAL_V26_PASS[2],
                    "actual_v26_original_verified_passing_case_count": CASE_COUNT,
                    "actual_v5_public_pass_receipt_sha256": PUBLIC_V5_PASS[2],
                    "actual_v5_public_verified_passing_case_count": 10_434,
                    "actual_v5_public_api_operation_count": 111,
                    "actual_v27_preactivation_failure_receipt_sha256":
                        FAILED_V27_RECEIPT[2],
                    "actual_v27_preactivation_status": "FAIL",
                    "authenticated_v12_adapter_constants_migrated": 2,
                    "operational_guard_version": 4,
                    "source_wall_installed_before_predecessor": False,
                    "actual_candidate_imports": 0,
                    "actual_candidate_workers_started": 0,
                    "actual_native_libraries_loaded": 0})
    state["context"] = context
    return context, state


def execute_actual(options: dict, context: dict, state: dict) -> dict:
    need(options["mode"] in ACTUAL_MODES
         and options.get("root_authorized") is True
         and options.get("frozen_committed_pushed") is True
         and options.get("frozen_commit") == options.get("pushed_commit")
         and context.get("source_wall_installed_before_predecessor") is False
         and context.get("operational_guard_version") == 4,
         "require separately pushed root-only V29 entry and strict V4 guard")
    for key, expected in state["required"].items():
        need(options.get(key) == expected,
             "require independently caller-pinned actual V33 authority: " + key)
    arguments = {key: value for key, value in options.items()
                 if key not in ("root_authorized", "frozen_committed_pushed")}
    result = state["parent"].actual_operation(arguments, context, state)
    if options["mode"] == "--worker":
        need(result.get("runtime_guard_installed_before_candidate_import") is True
             and result.get("actual_candidate_workers") == 1,
             "install strict V4 before one independently isolated Rust worker")
    elif options["mode"] == "--run":
        need(result.get("suite_count") == WORKER_COUNT
             and result.get("case_execution_denominator") == CASE_COUNT
             and result.get("all_four_original_targets_restored") is True
             and result.get("actual_candidate_workers") == WORKER_COUNT
             and result.get("distinct_worker_process_id_count") == WORKER_COUNT,
             "preserve 13 independent original workers and all four owner inodes")
        result.update({"actual_v35_build_receipt_sha256":
                           state["v33"]["rows"][3][2],
                       "actual_v35_root_receipt_sha256":
                           state["v33"]["rows"][4][2],
                       "actual_v35_native_engine_sha256":
                           state["v33"]["native_outputs"]["engine"]["sha256"],
                       "actual_v35_native_bridge_sha256":
                           state["v33"]["native_outputs"]["bridge"]["sha256"],
                       "historical_v33_original_pass_receipt_sha256":
                           HISTORICAL_V33_ORIGINAL_PASS[2],
                       "safe_native_handle_lease_application_sha256":
                           NATIVE_HANDLE_LEASE[3][2],
                       "actual_v25_original_failure_receipt_sha256":
                           PREVIOUS_FAILURE[2],
                       "actual_v25_semantic_mismatch_count": 1352,
                       "actual_v25_verified_passing_case_count": 15_877,
                       "actual_v26_original_pass_receipt_sha256":
                           ORIGINAL_V26_PASS[2],
                       "actual_v26_original_verified_passing_case_count":
                           CASE_COUNT,
                       "actual_v5_public_pass_receipt_sha256": PUBLIC_V5_PASS[2],
                       "actual_v5_public_verified_passing_case_count": 10_434,
                       "actual_v5_public_api_operation_count": 111,
                       "actual_v27_preactivation_failure_receipt_sha256":
                           FAILED_V27_RECEIPT[2],
                       "actual_v27_preactivation_status": "FAIL",
                       "authenticated_v12_adapter_constants_migrated": 2,
                       "candidate_qualified": False,
                       "runtime_non_delegation": "NOT ESTABLISHED",
                       "historical_runtime_non_delegation_v4_status": "FAIL",
                       "final_holdout": FINAL_HOLDOUT_STATUS})
    result["operational_guard_version"] = 4
    return result


def parse_options(arguments: list[str]) -> dict:
    need(bool(arguments), "select one exact V29 original-controller operation")
    modes = [item for item in arguments if item in SOURCE_MODES + ACTUAL_MODES]
    need(len(modes) == 1,
         "select exactly one public-only or root-authorized actual V29 mode")
    result: dict[str, object] = {"mode": modes[0]}
    cursor = 0
    while cursor < len(arguments):
        flag = arguments[cursor]
        if flag in SOURCE_MODES + ACTUAL_MODES:
            cursor += 1
            continue
        if flag in ("--root-authorized", "--frozen-committed-pushed"):
            key = flag[2:].replace("-", "_")
            need(key not in result, "reject repeated root-only authorization")
            result[key] = True
            cursor += 1
            continue
        need(type(flag) is str and flag.startswith("--")
             and cursor + 1 < len(arguments),
             "reject positional or incomplete independent V29 authority")
        key = flag[2:].replace("-", "_")
        need(key not in result,
             "reject repeated or aliased independent authority: " + flag)
        result[key] = arguments[cursor + 1]
        cursor += 2
    required = {"source_sha256", "protocol_sha256", *V35_PIN_NAMES,
                *GUARD_PIN_NAMES}
    if result["mode"] != "--render-contract":
        required.add("contract_sha256")
    for key in required:
        sha_pin(result.get(key), key)
    if result["mode"] in SOURCE_MODES:
        need(set(result) == required | {"mode"},
             "source-only verification cannot authorize a private root or candidate")
    else:
        need(result.get("root_authorized") is True
             and result.get("frozen_committed_pushed") is True,
             "require explicit root authorization after frozen commit and push")
        for key in ("frozen_commit", "pushed_commit"):
            value = result.get(key)
            need(type(value) is str and len(value) == 40
                 and all(character in "0123456789abcdef" for character in value),
                 "require one independent complete pushed commit: " + key)
        need(result["frozen_commit"] == result["pushed_commit"],
             "reject a frozen source not independently committed and pushed")
    return result


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
        contract, state = load_source_context(
            wall, options, options["mode"] == "--render-contract",
        )
        if options["mode"] == "--render-contract":
            result = contract
        else:
            controls = (source_controls(wall, contract, state)
                        if options["mode"] == "--self-test" else [])
            native = state["v33"]["native_outputs"]
            result = {
                "schema": SCHEMA + "-source-only-gate", "status": "PASS",
                "version": VERSION, "mode": options["mode"].removeprefix("--"),
                "source_sha256": options["source_sha256"],
                "protocol_sha256": options["protocol_sha256"],
                "contract_sha256": options["contract_sha256"],
                **{name: options[name] for name in V35_PIN_NAMES + GUARD_PIN_NAMES},
                "actual_v25_failure_receipt_sha256": PREVIOUS_FAILURE[2],
                "actual_v25_candidate_status": "FAIL",
                "actual_v25_semantic_mismatch_count": 1352,
                "actual_v25_verified_passing_case_count": 15_877,
                "actual_v25_substitution_mismatch_count": 240,
                "actual_v25_shape_mismatch_count": 1112,
                "actual_v26_original_pass_receipt_sha256": ORIGINAL_V26_PASS[2],
                "actual_v26_candidate_status": "PASS",
                "actual_v26_verified_passing_case_count": CASE_COUNT,
                "actual_v26_semantic_mismatch_count": 0,
                "actual_v5_public_pass_receipt_sha256": PUBLIC_V5_PASS[2],
                "actual_v5_public_candidate_status": "PASS",
                "actual_v5_public_verified_passing_case_count": 10_434,
                "actual_v5_public_semantic_mismatch_count": 0,
                "actual_v5_public_api_operation_count": 111,
                "actual_v27_preactivation_failure_receipt_sha256":
                    FAILED_V27_RECEIPT[2],
                "actual_v27_preactivation_status": "FAIL",
                "authenticated_v12_adapter_constants_migrated": 2,
                "actual_v35_compiler_process_count": 28,
                "actual_v35_native_engine_sha256": native["engine"]["sha256"],
                "actual_v35_native_bridge_sha256": native["bridge"]["sha256"],
                "safe_bridge_source_sha256": BRIDGE_SOURCE_SHA,
                "corrected_adapter_sha256": ADAPTER_SHA,
                "optimized_engine_source_sha256": ENGINE_SOURCE_SHA,
                "optimized_search_source_sha256": SEARCH_SOURCE_SHA,
                "historical_v33_original_pass_receipt_sha256":
                    HISTORICAL_V33_ORIGINAL_PASS[2],
                "historical_v33_original_verified_passing_case_count": CASE_COUNT,
                "historical_v33_original_applies_to_v35": False,
                "historical_v33_wider_public_applies_to_v35": False,
                "historical_v33_native_engine_sha256": HISTORICAL_V33_ENGINE_SHA,
                "historical_v33_native_bridge_sha256": HISTORICAL_V33_BRIDGE_SHA,
                "safe_native_handle_lease_application_sha256":
                    NATIVE_HANDLE_LEASE[3][2],
                "synthetic_callback_finalization_case_count": 103_184,
                "synthetic_operation_callback_sequence_count": 32_768,
                "synthetic_scanner_iterator_lifetime_case_count": 20_656,
                "synthetic_safety_cases_counted_in_original_denominator": False,
                "actual_callback_finalization_safety": NOT_MEASURED,
                "actual_scanner_iterator_finalization_safety": NOT_MEASURED,
                "exact_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
                "exact_v35_static_source_and_elf_non_delegation":
                    "NOT ESTABLISHED",
                "case_execution_denominator": CASE_COUNT,
                "suite_count": WORKER_COUNT,
                "named_private_waiver_count": 13,
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
                "actual_retired_proposal_opens": 0,
                "actual_retired_proposal_metadata_probes": 0,
                "actual_hidden_cases_read": 0,
                "actual_clock_samples": 0,
                "source_wall_installed_before_predecessor": wall.installed,
                "source_wall_live_descriptors": len(wall.live),
                "hostile_control_count": len(controls),
                "hostile_controls": controls,
                "physically_blocked_effects": dict(wall.blocked),
                "actual_original_campaign": "NOT RUN",
                "candidate_correctness": NOT_MEASURED,
                "candidate_original_oracle_pass": NOT_MEASURED,
                "original_suite_correctness_qualified": NOT_MEASURED,
                "candidate_qualified": False,
                "runtime_non_delegation": "NOT ESTABLISHED",
                "historical_retired_holdout_proposal_case_count":
                    HISTORICAL_HOLDOUT_CASE_COUNT,
                "final_holdout": FINAL_HOLDOUT_STATUS,
                "performance": NOT_MEASURED, "memory": NOT_MEASURED,
                "confidence_intervals": NOT_MEASURED,
                "undefined_behavior": NOT_MEASURED,
                "qualified_candidate_count": 0, "winner_selected": False,
            }
        parent_state = state["parent_state"]
        encoded = parent_state["capture"].canonical_document(
            parent_state["semantic"], result,
        )
        need(type(encoded) is bytes and 0 < len(encoded) <= MAX_OWNER_BYTES,
             "bound complete public-only or separately authorized V29 evidence")
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
                sys.stdout.buffer.write(actual_state["guard"].canonical(preserved))
                sys.stdout.buffer.flush()
            except BaseException:
                pass
        else:
            try:
                sys.stderr.write("V29 original campaign rejected: "
                                 + type(error).__name__ + ": "
                                 + str(error)[:8192] + "\n")
            except BaseException:
                pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
