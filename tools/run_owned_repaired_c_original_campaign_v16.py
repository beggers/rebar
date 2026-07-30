#!/usr/bin/env python3
"""Freeze the genuine C11 controller and repair only its original case transport.

Source-only modes inherit the complete authenticated C11 physical source wall.
They never run a candidate or a reference, open an archive or a holdout, load
native code, start a worker, take a clock sample, or modify the workspace.
An actual run remains separately authorized and is never a source-only gate.
"""

from __future__ import annotations

import ast
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/run_owned_repaired_c_original_campaign_v16.py"
PROTOCOL = "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V16.md"
CONTRACT = "oracle/phase2/repaired-c-original-campaign-v16.json"
SCHEMA = "rebar-owned-repaired-c-original-campaign-v16"
LABEL = "phase2-v24-c-final-public-semantics-original-p0-v16"
DEVICE = 2064
MAX_OWNER = 8 * 1024 * 1024
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
MATRIX_SHA256 = "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240"
REFERENCE_SHA256 = "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"
ORIGINAL_SOURCE_SHA256 = "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
ORIGINAL_SUITE = "original_bounded_v5"
SOURCE_METHOD_COUNT = 165
PUBLIC_RECORD_COUNT = 152
EXECUTED_CASE_COUNT = 151
DEBUG_SKIP_COUNT = 1
SKIPPED_TEST = "ReTests.test_memory_leaks"
SKIP_REASONS = ["requires debug build"]
PRIVATE_WAIVER_NAMES = (
    "DebugTests.test_debug_flag",
    "DebugTests.test_atomic_group",
    "DebugTests.test_possesive_repeat_one",
    "DebugTests.test_possesive_repeat",
    "ImplementationTest.test_immutable",
    "ImplementationTest.test_overlap_table",
    "ImplementationTest.test_signedness",
    "ImplementationTest.test_disallow_instantiation",
    "ImplementationTest.test_deprecated_modules",
    "ImplementationTest.test_case_helpers",
    "ImplementationTest.test_dealloc",
    "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
    "ImplementationTest.test_sre_template_invalid_group_index",
)
RECORD_KEYS = frozenset((
    "test", "source_ast_sha256", "status", "tests_run",
    "failure_count", "error_count", "skip_count",
    "failure_tracebacks", "error_tracebacks", "skip_reasons",
))

C11 = (
    ("tools/run_owned_repaired_c_original_campaign_v11.py",
     "b2871592ad3c2138e4a7a9dbea034fc50c699fb34c44f6ff6185087a144e52c2",
     128680, 431190),
    ("oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V11.md",
     "cfddebcfb5b481a495b86ed7958f2563ad5ffecc3aebcc94820cae5e0612ed39",
     10493, 525492),
    ("oracle/phase2/repaired-c-original-campaign-v11.json",
     "e2396ea5a51fbe6ad0b34f2831461d3c6c362d4076a931791ce23820ca810b93",
     58479, 525493),
)
C11_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v11-c-phase2-v21-c-"
    "original-match-semantics-original-p0-v11-failures-publication-receipt.json",
    "3db5daf9352f5c9837f4f7134bead6c0a05b2bddf9815a9cf134ea953b0ecd3e",
    10404, 525589,
)
V5 = (
    ("tools/run_owned_six_family_original_p0_producer_v5.py",
     "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
     102286, 431370),
    ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md",
     "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
     5270, 524884),
    ("oracle/phase2/six-family-p0-producer-v5.json",
     "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
     21036, 524885),
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
V4_GUARD = (
    ("tools/verify_owned_candidate_runtime_independence_v4.py",
     "5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3",
     48_687, 429243),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md",
     "835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16",
     4_492, 525890),
    ("oracle/phase2/candidate-runtime-independence-v4.json",
     "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2",
     9_352, 525891),
)
PREVIOUS_C12 = (
    ("tools/run_owned_repaired_c_original_campaign_v12.py",
     "80af52f1df9c2787df858afef4addb1597fb87845225554d258f4c9173dabb17",
     78_137, 431488),
    ("oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V12.md",
     "6f7c81007f78eb6435204521548f238b531d6bcb9f517f1c35e395e0e2b82344",
     7_712, 525513),
    ("oracle/phase2/repaired-c-original-campaign-v12.json",
     "758578965291c0b8cf251d7ec46267de7400935e30d4388a126c22821b85090b",
     76_691, 525515),
)
PREVIOUS_C12_FAILURE = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v12-c-phase2-v21-"
    "c-original-match-semantics-original-p0-v12-failures-publication-receipt.json",
    "a3f4b90b8f289df9dfe49f776266e3c290edb2c21c62713137f501a5f997c21b",
    10_943, 525645,
)
SUPERSEDED_C13 = (
    ("tools/run_owned_repaired_c_original_campaign_v13.py",
     "416967b24ef16ca239a7c7b40a8b62114305eb9c3a2c3efa46c23f51b5bf2984",
     123_942, 431414),
    ("oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V13.md",
     "623c8e0c12e2ee456df400db7e95fa376c24749a58bb9cb242702309fa7cc308",
     12_062, 526366),
    ("oracle/phase2/repaired-c-original-campaign-v13.json",
     "7a4326fe96ad1a21e49ea9e994353763f15e364c2912bfb321ec20944a2e85e4",
     92_336, 526407),
)
PREVIOUS_C14 = (
    ("tools/run_owned_repaired_c_original_campaign_v14.py",
     "0f54e57c548c79ae168fa30eba1f5e6758a51c89a1498b759468014c5510941b",
     133_651, 431589),
    ("oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V14.md",
     "4f3d10484bea345598d00229b234bdde93671be770cd9460f32b9d12aef15d97",
     13_231, 526419),
    ("oracle/phase2/repaired-c-original-campaign-v14.json",
     "4da92d793d2eed6117c957d0e34838d8ae8ee04982e3407321c22daedc477fa8",
     93_595, 526431),
)
PREVIOUS_C14_CRASH = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v14-publication-recursion-failure.json",
    "7773620e2df5e0f3bc26acad6b3dca8651d1844e68501ad4453dd41866f05377",
    351, 526451,
)


FINAL_REPAIR = (
    ("tools/apply_owned_c_final_public_semantics_v1.py",
     "028899a11fa051c80651a27f2b0365512e4821f6509634223599c4a523e72c5b",
     63_777, 431679),
    ("oracle/phase2/C-FINAL-PUBLIC-SEMANTICS-V1.md",
     "69da3db828b1ef8cf8fd6885031cf485540db6321e86b5691b96ecae33a9b2b5",
     8_153, 526554),
    ("oracle/phase2/c-final-public-semantics-v1.json",
     "e31ce572d791a11db8cb6224b3cff4e17f3ae0b5f5cc0b8ae271d96d4bb2aa6b",
     4_825, 526555),
)
FINAL_APPLICATION = (
    "oracle/phase2/evidence/c-final-public-semantics-v1-application.json",
    "3b45b8cf24d829221f36f311e7cc3852f42b0b73840a4952d7e5b7441c625ace",
    1_303, 526587,
)
PREVIOUS_C15 = (
    ("tools/run_owned_repaired_c_original_campaign_v15.py",
     "c2977729a36712a8d1f4f54d9aa04e15d129899d52799c2f518cf9c95b03e341",
     142_317, 431621),
    ("oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V15.md",
     "21392c44286b3953e936e6e2fd689405c9f48957efbe5be650c2caf77ad9465b",
     15_244, 526472),
    ("oracle/phase2/repaired-c-original-campaign-v15.json",
     "37574150a0bf6a6a7515b41605ee6ab37eeda3aa247e0aef2417bb7b170c65b3",
     95_844, 526474),
)
PREVIOUS_C15_FAILURE = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v15-c-"
    "phase2-v23-c-complete-semantics-original-p0-v15-"
    "failures-publication-receipt.json",
    "6adea6a4da59bb0c63c54006991257b46149c4447a82bb1cd6b8810e6bee5b43",
    10_888, 526500,
)
HISTORICAL_C23 = (
    ("tools/reproduce_owned_c_complete_semantic_source_build_v23.py",
     "712da0fe4b5ee10ab567f5a679c67b876d5a247276ebd1ed2cf450e692ffcfe0",
     87_985, 431173),
    ("oracle/phase2/C-COMPLETE-SEMANTIC-SOURCE-BUILD-V23.md",
     "50f4597fe04cec60aacea4381f8e0f0a904f18d6f06d70c3d3d04a28b7bb2379",
     13_313, 526317),
    ("oracle/phase2/c-complete-semantic-source-build-v23.json",
     "e29180b0bf7f7ddc254ad1592c8bb8a4c683cfff1a7c1043084e024861642ac3",
     14_197, 526318),
)
HISTORICAL_C23_PUBLIC = (
    "oracle/phase2/evidence/native-source-build-v23-c-phase2-v23-"
    "c-complete-semantics-publication-receipt.json",
    "36dac1112f0bb388c6a172228b8e2172246d7eac083899539b2695323afce63c",
    13_561, 526379,
)
HISTORICAL_C23_ROOT = (
    "oracle/phase2/evidence/native-source-build-v23-c-phase2-v23-"
    "c-complete-semantics-root-provenance-receipt.json",
    "857ef237d4460bc02965393d780e8ef9aaea1533c2f577a139a79546a9ded79c",
    11_962, 526380,
)

C24_BUILD = (
    ("tools/reproduce_owned_c_complete_semantic_source_build_v24.py",
     "a82f5613ea2d57e15dfcaf6cc8e6d6c88ed13d23d78bb02dbd5267a73c5621be",
     107_319, 431807),
    ("oracle/phase2/C-COMPLETE-SEMANTIC-SOURCE-BUILD-V24.md",
     "080fea9f10569e4601c48c913e0b1a311ade4eb9ea458b5514170800b1111ed0",
     18_367, 526621),
    ("oracle/phase2/c-complete-semantic-source-build-v24.json",
     "9e6e92cdd7fe58c1351b6fb24e7f265f722c4928353d80a27ede75028c5f5901",
     19_394, 526623),
)
# Filled only after root publishes both genuine C24 build receipts.
C24_PUBLIC_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v24-c-phase2-v24-"
    "c-complete-semantics-publication-receipt.json",
    "ed0c119b2e672342f3665c9dc7c4896977ea590bceec08ff3b97cd56b9f92a75",
    14_172, 526667,
)
C24_ROOT_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v24-c-phase2-v24-"
    "c-complete-semantics-root-provenance-receipt.json",
    "36cb6adcf3a28d635fc997c090e62e1ce5563754deab02c05b41f4d034ad3048",
    12_573, 526668,
)
C24_NATIVE_SHA256 = (
    "891acc0d0f496045e90e2efc0f0a3125e4f508352c2ee5e31ee807ea2fb1801a"
)
C24_NATIVE_BYTES = 163_544
C24_ROOT_PATH = (
    "/tmp/rebar-phase2-c-complete-native-semantics-v24-"
    "d95b1a1342b65ddc0bf118d181aeca8b"
)
C24_ROOT_DEVICE = 2049
C24_ROOT_INODE = 11680793
CORRECTED_NATIVE_SOURCE_SHA256 = (
    "99f45846551705379ccd7365333995ee68fe25e10d101655a17ad45c5e13a5e6"
)
CORRECTED_NATIVE_SOURCE_BYTES = 221_715
CORRECTED_ADAPTER_SHA256 = (
    "e91819b1d6b399954b3384519fdfddb6ccd6d4e4099a34e06d702c9959a79193"
)
CORRECTED_ADAPTER_BYTES = 62_209
ORIGINAL_ADAPTER_SHA256 = (
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
)
ORIGINAL_ADAPTER_BYTES = 60_707
ADAPTER_TARGET_NAME = "vm_candidate.py"
ADAPTER_TARGET_RELATIVE = "candidates/" + ADAPTER_TARGET_NAME
ADAPTER_BACKUP_NAME = ".rebar-c-original-campaign-v16-original-adapter"
ADAPTER_STAGE_NAME = ".rebar-c-original-campaign-v16-staged-adapter"
ADAPTER_JOURNAL_NAME = "original-adapter-recovery-journal-v16.json"
FINAL_HOLDOUT_STATUS = "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
ORIGINAL_HARNESS = (
    "tools/rust_original_cpython_suite_v1.py",
    "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95",
    67175, 430765,
)
ORIGINAL_EVALUATOR = (
    "tools/independent_original_cpython_suite_v5.py",
    ORIGINAL_SOURCE_SHA256, 123750, 431594,
)

C11_OUTCOMES = (
    ("original_bounded_v5", 151, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("public_v3", 864, "PASS", "PASS", 0),
    ("scanner_v3", 1024, "PASS", "PASS", 0),
    ("buffer_v3", 768, "PASS", "PASS", 0),
    ("managed_v1", 1024, "FAIL", "SEMANTIC MISMATCH", 16),
    ("scanner_verbose_v1", 2854, "PASS", "PASS", 0),
    ("public_types_v1", 6912, "FAIL", "SEMANTIC MISMATCH", 248),
    ("substitution_v2", 5120, "FAIL", "SEMANTIC MISMATCH", 224),
    ("shape_v2", 10240, "PASS", "PASS", 0),
    ("public_surface_v19", 1376, "FAIL", "SEMANTIC MISMATCH", 114),
    ("subinterpreter_v2", 128, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("pep688_v4", 264, "FAIL", "SEMANTIC MISMATCH", 4),
    ("threaded_pattern_v1", 512, "PASS", "PASS", 0),
)
C11_FINGERPRINTS = (
    ("public_v3", 864, 0, 0,
     "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"),
    ("scanner_v3", 1024, 0, 0,
     "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"),
    ("buffer_v3", 768, 0, 0,
     "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"),
    ("managed_v1", 1024, 16, 1,
     "3488267b9c2a5aff58a0917adb142d26d482526536b71ceb8e3a39e5d5ed4352"),
    ("scanner_verbose_v1", 2854, 0, 0,
     "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"),
    ("public_types_v1", 6912, 248, 8,
     "b278976e7d01f2c56359bcdc442fefa1ee6cef899275f1cf5ef00de2fd7e2eff"),
    ("substitution_v2", 5120, 224, 7,
     "2ba4b132a4f84ba43fb1a87b1b5c0ab2c8cceffc8f5937bebc285af9da11044a"),
    ("shape_v2", 10240, 0, 0,
     "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"),
    ("public_surface_v19", 1376, 114, 4,
     "443312e6ef63ea99dcf0553ec2e251a40f7221f75697139d85c52084cd0fee22"),
    ("pep688_v4", 264, 4, 1,
     "9377c56ba63c694fd0ce4839ad802cbc1e821ce708c4fbde5f5d7c8d7e5c26cc"),
    ("threaded_pattern_v1", 512, 0, 0,
     "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"),
)

REPLACEMENTS = {
    C11[0][0]: SOURCE,
    C11[1][0]: PROTOCOL,
    C11[2][0]: CONTRACT,
    "rebar-owned-repaired-c-original-campaign-v11": SCHEMA,
    "phase2-v21-c-original-match-semantics-original-p0-v11": LABEL,
    "/tmp/rebar-phase2-repaired-c-original-campaign-v11":
        "/tmp/rebar-phase2-repaired-c-original-campaign-v16",
    ".rebar-c-original-campaign-v11-original-native":
        ".rebar-c-original-campaign-v16-original-native",
    ".rebar-c-original-campaign-v11-staged-native":
        ".rebar-c-original-campaign-v16-staged-native",
    "original-native-recovery-journal-v11.json":
        "original-native-recovery-journal-v16.json",
    "repaired-c-original-campaign-v11-c-":
        "repaired-c-original-campaign-v16-c-",
    "SOURCE FROZEN; ACTUAL C21 V11 ORIGINAL CAMPAIGN NOT RUN":
        "SOURCE FROZEN; ACTUAL C21 V16 ORIGINAL CAMPAIGN NOT RUN",
    "SOURCE FREEZE, PRESERVED ACTUAL V6, V7, AND V9 FAILURES; "
    "NOT A V11 CANDIDATE RESULT":
        "SOURCE FREEZE, PRESERVED ACTUAL V6, V7, V9, V10, AND V11 "
        "FAILURES; NOT A V16 CANDIDATE RESULT",
    "LATEST P0 V4 AND EXPLICIT C21 V11 ONLY":
        "LATEST P0 V4 AND EXPLICIT C21 V16 ONLY",
    "NOT RUN BY V11": "NOT RUN BY V16",
    "v11_candidate_correctness": "v16_candidate_correctness",
    "-v11": "-v16",
    "v11-original-native": "v16-original-native",
    "v11-staged-native": "v16-staged-native",
    "_rebar_owned_c_v11_authenticated_v8":
        "_rebar_owned_c_v16_authenticated_v8",
    "_rebar_owned_c_v11_authenticated_complete_v9":
        "_rebar_owned_c_v16_authenticated_complete_v9",
    "_rebar_owned_actual_c_v11_runtime_guard_v3":
        "_rebar_owned_actual_c_v16_runtime_guard_v3",
    "C21 original campaign V11: ": "C21 original campaign V16: ",
    "EXPLICIT INDEPENDENTLY PINNED C21 C11 --run ONLY":
        "EXPLICIT INDEPENDENTLY PINNED C21 C12 --run ONLY",
    "exclusively create one owner-only C11 evidence inode":
        "exclusively create one owner-only C12 evidence inode",
    "reject incomplete or substituted durable C11 evidence":
        "reject incomplete or substituted durable C12 evidence",
    "require every genuine complete or unfinished original C11 suite":
        "require every genuine complete or unfinished original C12 suite",
    "strictly round-trip the entire actual lossless C11 worker":
        "strictly round-trip the entire actual lossless C12 worker",
}


class CampaignError(Exception):
    """A source owner, historical receipt, or complete case vector is false."""


def need(condition: object, reason: str) -> None:
    if not condition:
        raise CampaignError(reason)


def clean_runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and os.path.abspath(sys.executable) == PYTHON
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "ctypes" not in sys.modules
        and not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
        "require the exact matcher-free stable CPython 3.14.6 -I -B -S",
    )


def exact_owner(owner: tuple) -> bytes:
    permitted = C11 + V5 + V3 + (C11_RECEIPT, ORIGINAL_HARNESS,
                                  ORIGINAL_EVALUATOR)
    need(type(owner) is tuple and len(owner) == 4
         and any(owner == item for item in permitted),
         "reject an invented or unapproved complete plaintext source owner")
    relative, expected, size, inode = owner
    need(type(relative) is str and not relative.startswith(
        ("/", "candidates/", "docs/evidence/")
    ) and not any(word in relative.lower()
                  for word in ("holdout", "benchmark"))
         and not relative.endswith((".gz", ".xz", ".zip", ".tar", ".so"))
         and type(expected) is str and len(expected) == 64
         and all(letter in "0123456789abcdef" for letter in expected)
         and type(size) is int and 0 < size <= MAX_OWNER
         and type(inode) is int and inode > 0,
         "physically exclude candidate, archive, native, private, and holdout")
    descriptor = os.open(
        ROOT + "/" + relative,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode)
             and before.st_dev == DEVICE
             and before.st_ino == inode
             and before.st_size == size
             and before.st_uid == os.geteuid()
             and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject a substituted immutable plaintext owner: " + relative)
        blocks = []
        remaining = size
        while remaining:
            block = os.read(descriptor, min(remaining, 262144))
            need(bool(block), "reject a truncated immutable plaintext owner")
            blocks.append(block)
            remaining -= len(block)
        need(not os.read(descriptor, 1),
             "reject an expanded immutable plaintext owner")
        raw = b"".join(blocks)
        after = os.fstat(descriptor)
        need(hashlib.sha256(raw).hexdigest() == expected
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject a changed complete immutable plaintext owner: " + relative)
        return raw
    finally:
        os.close(descriptor)


def owner_record(owner: tuple) -> dict:
    return {
        "path": owner[0], "sha256": owner[1], "bytes": owner[2],
        "device": DEVICE, "inode": owner[3], "mode": "0600", "nlink": 1,
    }


def hex_digest(value: object) -> bool:
    return (type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value))


class ExactV11ToV16(ast.NodeTransformer):
    """Retarget the entire genuine C11 and exactly its post-observation encoder."""

    def __init__(self) -> None:
        self.identities = {identity: 0 for identity in REPLACEMENTS}
        self.functions: list[str] = []
        self.worker_definitions = 0
        self.vector_assignments = 0
        self.denominator_guards = 0
        self.complete_flag_assignments = 0
        self.truncation_flag_assignments = 0
        self.decoded_return_guards = 0
        self.install_extensions = 0
        self.inner_version_assignments = 0
        self.transformer_version_assignments = 0
        self.receipt_version_fields = 0
        self.contract_version_checks = 0
        self.receipt_extensions = 0

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if type(node.value) is str and node.value in REPLACEMENTS:
            self.identities[node.value] += 1
            return ast.copy_location(
                ast.Constant(REPLACEMENTS[node.value]), node,
            )
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        if node.name == "lossless_c11_protected_worker":
            need(node.lineno == 1471,
                 "reject a relocated immutable C11 original worker")
            self.worker_definitions += 1
        self.functions.append(node.name)
        try:
            return self.generic_visit(node)
        finally:
            self.functions.pop()

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        node = self.generic_visit(node)
        if (len(node.targets) == 1
                and isinstance(node.value, ast.Constant)
                and type(node.value.value) is int
                and node.value.value == 11
                and isinstance(node.targets[0], ast.Attribute)
                and node.targets[0].attr == "value"):
            target = node.targets[0].value
            if (isinstance(target, ast.Attribute)
                    and target.attr == "value"
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "node"):
                node.value.value = 16
                self.inner_version_assignments += 1
            elif isinstance(target, ast.Name) and target.id == "value":
                node.value.value = 16
                self.transformer_version_assignments += 1

        if (len(node.targets) != 1
                or not isinstance(node.targets[0], ast.Subscript)
                or not isinstance(node.targets[0].slice, ast.Constant)
                or not self.functions
                or self.functions[-1] != "lossless_c11_protected_worker"):
            return node

        target = node.targets[0]
        key = target.slice.value
        if (key == "candidate_records"
                and isinstance(target.value, ast.Name)
                and target.value.id == "compact"):
            need(node.lineno == 1488
                 and isinstance(node.value, ast.Call)
                 and isinstance(node.value.func, ast.Attribute)
                 and isinstance(node.value.func.value, ast.Name)
                 and node.value.func.value.id == "history"
                 and node.value.func.attr == "lossless_vector",
                 "reject a replaced immutable original candidate encoder")
            node.value = ast.copy_location(ast.Call(
                func=ast.Name("_c12_encode_candidate_records", ast.Load()),
                args=[ast.Name("records", ast.Load()),
                      ast.Name("compact", ast.Load()),
                      ast.Name("producer", ast.Load()),
                      ast.Name("history", ast.Load()),
                      ast.Call(ast.Attribute(
                          ast.Name("parsed", ast.Load()), "get", ast.Load(),
                      ), [ast.Constant("--suite")], [])],
                keywords=[],
            ), node.value)
            self.vector_assignments += 1
        elif (key == "all_original_records_and_mismatches_preserved"
              and isinstance(target.value, ast.Name)
              and target.value.id == "row"):
            need(node.lineno == 1545,
                 "reject relocated original full-record preservation flag")
            node.value = ast.copy_location(ast.Call(
                ast.Name("_c12_complete_records_preserved", ast.Load()),
                [ast.Name("records", ast.Load()),
                 ast.Name("compact", ast.Load()),
                 ast.Name("history", ast.Load())], [],
            ), node.value)
            self.complete_flag_assignments += 1
        elif (key == "original_record_prefix_explicitly_truncated"
              and isinstance(target.value, ast.Name)
              and target.value.id == "row"):
            need(node.lineno == 1550,
                 "reject relocated original full-record truncation flag")
            node.value = ast.copy_location(ast.Call(
                ast.Name("_c12_record_prefix_truncated", ast.Load()),
                [ast.Name("records", ast.Load()),
                 ast.Name("compact", ast.Load()),
                 ast.Name("history", ast.Load())], [],
            ), node.value)
            self.truncation_flag_assignments += 1
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        node = self.generic_visit(node)
        if (self.functions
                and self.functions[-1] == "lossless_c11_protected_worker"
                and isinstance(node.func, ast.Name)
                and node.func.id == "need"
                and len(node.args) == 2
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value
                == "preserve the genuine complete original case denominator"):
            need(node.lineno == 1493
                 and isinstance(node.args[0], ast.Compare)
                 and len(node.args[0].ops) == 1
                 and isinstance(node.args[0].ops[0], ast.Eq),
                 "reject a replaced immutable C11 original denominator guard")
            node.args[0] = ast.copy_location(ast.Call(
                ast.Name("_c12_validate_candidate_record_counts", ast.Load()),
                [ast.Name("compact", ast.Load()),
                 ast.Name("records", ast.Load()),
                 ast.Call(ast.Attribute(
                     ast.Name("parsed", ast.Load()), "get", ast.Load(),
                 ), [ast.Constant("--suite")], []),
                 ast.Name("producer", ast.Load()),
                 ast.Name("history", ast.Load())], [],
            ), node.args[0])
            self.denominator_guards += 1
        return node

    def visit_Return(self, node: ast.Return) -> ast.AST | list[ast.stmt]:
        node = self.generic_visit(node)
        if (self.functions
                and self.functions[-1] == "lossless_c11_protected_worker"
                and isinstance(node.value, ast.Name)
                and node.value.id == "decoded"):
            need(node.lineno == 1621,
                 "reject a relocated complete original worker round trip")
            check = ast.copy_location(ast.Expr(ast.Call(
                ast.Name("_c12_validate_decoded_original", ast.Load()),
                [ast.Name("decoded", ast.Load()),
                 ast.Call(ast.Attribute(
                     ast.Name("parsed", ast.Load()), "get", ast.Load(),
                 ), [ast.Constant("--suite")], []),
                 ast.Name("producer", ast.Load()),
                 ast.Name("history", ast.Load())], [],
            )), node)
            self.decoded_return_guards += 1
            return [check, node]
        return node

    def visit_Expr(self, node: ast.Expr) -> ast.AST | list[ast.stmt]:
        node = self.generic_visit(node)
        if (len(self.functions) >= 2
                and self.functions[-2:] == ["main", "install_all"]
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "install_v11"):
            need(node.lineno == 2767
                 and len(node.value.args) == 4,
                 "reject a replaced genuine whole-source C11 installer")
            extension = ast.copy_location(ast.Expr(ast.Call(
                ast.Name("_c12_install_v16", ast.Load()),
                [ast.Name("historical", ast.Load()),
                 ast.Name("history", ast.Load()),
                 ast.Name("module", ast.Load()),
                 ast.Name("transform", ast.Load())], [],
            )), node)
            self.install_extensions += 1
            return [node, extension]
        return node

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        node = self.generic_visit(node)
        if (len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq)
                and len(node.comparators) == 1
                and isinstance(node.comparators[0], ast.Constant)
                and type(node.comparators[0].value) is int
                and node.comparators[0].value == 11
                and isinstance(node.left, ast.Call)
                and isinstance(node.left.func, ast.Attribute)
                and isinstance(node.left.func.value, ast.Name)
                and node.left.func.value.id == "base"
                and node.left.func.attr == "get"
                and len(node.left.args) == 1
                and isinstance(node.left.args[0], ast.Constant)
                and node.left.args[0].value == "version"):
            node.comparators[0].value = 16
            self.contract_version_checks += 1
        return node

    def visit_Dict(self, node: ast.Dict) -> ast.AST:
        node = self.generic_visit(node)
        for key, value in zip(node.keys, node.values, strict=True):
            if (isinstance(key, ast.Constant)
                    and key.value == "version"
                    and isinstance(value, ast.Constant)
                    and type(value.value) is int and value.value == 11):
                value.value = 16
                self.receipt_version_fields += 1
        if (self.functions
                and self.functions[-1] == "publish_lossless_c11_evidence"
                and any(isinstance(key, ast.Constant)
                        and key.value == "publication_pass_means"
                        for key in node.keys)):
            additions = (
                ("preserved_actual_v11_failure_receipt_sha256",
                 ast.Name("_c12_previous_failure_receipt_sha256", ast.Load())),
                ("complete_original_case_records_preserved",
                 ast.Call(ast.Attribute(
                     ast.Name("document", ast.Load()), "get", ast.Load(),
                 ), [ast.Constant("complete_original_case_records_preserved"),
                     ast.Constant(False)], [])),
                ("complete_original_public_record_count",
                 ast.Call(ast.Attribute(
                     ast.Name("document", ast.Load()), "get", ast.Load(),
                 ), [ast.Constant("complete_original_public_record_count"),
                     ast.Constant("NOT MEASURED")], [])),
                ("complete_original_executed_case_count",
                 ast.Call(ast.Attribute(
                     ast.Name("document", ast.Load()), "get", ast.Load(),
                 ), [ast.Constant("complete_original_executed_case_count"),
                     ast.Constant("NOT MEASURED")], [])),
                ("complete_original_source_method_count",
                 ast.Call(ast.Attribute(
                     ast.Name("document", ast.Load()), "get", ast.Load(),
                 ), [ast.Constant("complete_original_source_method_count"),
                     ast.Constant("NOT MEASURED")], [])),
                ("complete_original_case_vector_sha256",
                 ast.Call(ast.Attribute(
                     ast.Name("document", ast.Load()), "get", ast.Load(),
                 ), [ast.Constant("complete_original_case_vector_sha256"),
                     ast.Constant("NOT MEASURED")], [])),
            )
            existing = {key.value for key in node.keys
                        if isinstance(key, ast.Constant)}
            need(all(key not in existing for key, _ in additions),
                 "reject replaced original complete-case receipt fields")
            for key, value in additions:
                node.keys.append(ast.Constant(key))
                node.values.append(value)
            self.receipt_extensions += 1
        return node


def validate_original_record(record: object) -> None:
    need(type(record) is dict and set(record) == RECORD_KEYS,
         "preserve all ten authentic original test-result fields")
    need(type(record["test"]) is str and bool(record["test"])
         and hex_digest(record["source_ast_sha256"])
         and record["tests_run"] == 1
         and type(record["failure_count"]) is int
         and type(record["error_count"]) is int
         and type(record["skip_count"]) is int
         and type(record["failure_tracebacks"]) is list
         and type(record["error_tracebacks"]) is list
         and type(record["skip_reasons"]) is list
         and record["failure_count"] == len(record["failure_tracebacks"])
         and record["error_count"] == len(record["error_tracebacks"])
         and record["skip_count"] == len(record["skip_reasons"])
         and all(type(item) is str for item in record["failure_tracebacks"])
         and all(type(item) is str for item in record["error_tracebacks"])
         and all(type(item) is str for item in record["skip_reasons"]),
         "reject omitted or fabricated genuine original result details")
    failures = record["failure_count"] + record["error_count"]
    skip = record["skip_count"]
    need(skip in (0, 1) and not (skip and failures)
         and record["status"]
         == ("FAIL" if failures else "SKIP" if skip else "PASS"),
         "never convert a real original failure, error, or debug skip")


def validate_original_observation(observed: object, records: object,
                                  producer: types.ModuleType) -> str:
    need(type(observed) is dict and type(records) in (list, tuple)
         and len(records) == PUBLIC_RECORD_COUNT,
         "retain all 152 original public records in immutable source order")
    need(observed.get("suite") == ORIGINAL_SUITE
         and observed.get("source_relative") == ORIGINAL_EVALUATOR[0]
         and observed.get("source_sha256") == ORIGINAL_SOURCE_SHA256
         and observed.get("matrix_sha256") == MATRIX_SHA256
         and observed.get("reference_records_sha256") == REFERENCE_SHA256
         and observed.get("case_execution_denominator") == EXECUTED_CASE_COUNT
         and observed.get("actual_candidate_case_count") == EXECUTED_CASE_COUNT
         and observed.get("actual_public_record_count") == PUBLIC_RECORD_COUNT
         and observed.get("actual_debug_skip_count") == DEBUG_SKIP_COUNT
         and observed.get("named_private_waiver_count")
         == len(PRIVATE_WAIVER_NAMES)
         and type(observed.get("named_private_waivers")) in (list, tuple)
         and tuple(observed["named_private_waivers"]) == PRIVATE_WAIVER_NAMES,
         "preserve exact independent 165-method, 152-record, 151-case originals")
    identities = set()
    skipped = []
    for record in records:
        validate_original_record(record)
        identity = record["test"]
        need(identity not in identities
             and identity not in PRIVATE_WAIVER_NAMES,
             "reject duplicated public methods or private-waiver observations")
        identities.add(identity)
        if record["status"] == "SKIP":
            skipped.append(record)
    need(len(identities) == PUBLIC_RECORD_COUNT
         and len(skipped) == DEBUG_SKIP_COUNT
         and skipped[0]["test"] == SKIPPED_TEST
         and skipped[0]["skip_reasons"] == SKIP_REASONS,
         "retain exactly the authentic original release-build debug skip")
    expected = observed.get("candidate_records_sha256")
    raw = producer.canonical(records)
    need(hex_digest(expected) and raw.endswith(b"\n")
         and hashlib.sha256(raw).hexdigest() == expected,
         "bind all actual candidate records, including real failure tracebacks")
    return expected


def validate_complete_original_cases(vector: object,
                                     producer: types.ModuleType,
                                     campaign: types.ModuleType) -> dict:
    need(type(vector) is dict
         and vector.get("schema")
         == SCHEMA + "-lossless-original-public-case-vector"
         and vector.get("suite") == ORIGINAL_SUITE
         and vector.get("vector_kind") == "ORIGINAL PUBLIC CASE OBSERVATIONS"
         and vector.get("all_observed_records_preserved") is True
         and vector.get("complete_vector_embedded") is True
         and vector.get("truncated") is False
         and vector.get("source_method_count") == SOURCE_METHOD_COUNT
         and vector.get("public_record_count") == PUBLIC_RECORD_COUNT
         and vector.get("complete_record_count") == PUBLIC_RECORD_COUNT
         and vector.get("total_count") == PUBLIC_RECORD_COUNT
         and vector.get("case_execution_denominator") == EXECUTED_CASE_COUNT
         and vector.get("actual_debug_skip_count") == DEBUG_SKIP_COUNT
         and vector.get("named_private_waiver_count")
         == len(PRIVATE_WAIVER_NAMES)
         and vector.get("matrix_sha256") == MATRIX_SHA256
         and vector.get("reference_records_sha256") == REFERENCE_SHA256
         and hex_digest(vector.get("actual_candidate_records_sha256"))
         and vector.get("source_complete_vector_sha256")
         == vector.get("actual_candidate_records_sha256")
         and vector.get("transport_complete_vector_sha256")
         == vector.get("actual_candidate_records_sha256")
         and vector.get("source_comparison_modified") is False,
         "reject guessed, prefix-only, crossed, or normalized original cases")
    bridge = dict(vector)
    bridge["schema"] = SCHEMA + "-lossless-original-mismatch-vector"
    checked = campaign.validate_complete_c_mismatches(
        bridge, producer, ORIGINAL_SUITE, PUBLIC_RECORD_COUNT,
    )
    need(checked["record_count"] == PUBLIC_RECORD_COUNT
         and checked["transport_complete_vector_sha256"]
         == vector["actual_candidate_records_sha256"]
         and checked["all_observed_records_preserved"] is True,
         "reject a missing, reordered, or forged full original case chunk")
    return checked


def encode_candidate_records(records: object, observed: dict,
                             producer: types.ModuleType,
                             history: types.ModuleType,
                             suite: object,
                             campaign: types.ModuleType) -> dict:
    if suite != ORIGINAL_SUITE:
        return history.lossless_vector(
            records, producer,
            expected=observed.get("candidate_records_sha256"),
            suite_name=suite,
        )
    actual_digest = validate_original_observation(observed, records, producer)
    summary = history.lossless_vector(
        records, producer, expected=actual_digest, suite_name=ORIGINAL_SUITE,
    )
    need(summary.get("total_count") == PUBLIC_RECORD_COUNT
         and summary.get("source_complete_vector_sha256") == actual_digest
         and summary.get("transport_complete_vector_sha256") == actual_digest,
         "reject a false canonical full original public-record digest")
    full = campaign.encode_complete_c_mismatches(
        records, producer, history, ORIGINAL_SUITE, PUBLIC_RECORD_COUNT,
    )
    full.update({
        "schema": SCHEMA + "-lossless-original-public-case-vector",
        "vector_kind": "ORIGINAL PUBLIC CASE OBSERVATIONS",
        "source_method_count": SOURCE_METHOD_COUNT,
        "public_record_count": PUBLIC_RECORD_COUNT,
        "case_execution_denominator": EXECUTED_CASE_COUNT,
        "actual_debug_skip_count": DEBUG_SKIP_COUNT,
        "named_private_waiver_count": len(PRIVATE_WAIVER_NAMES),
        "matrix_sha256": MATRIX_SHA256,
        "reference_records_sha256": REFERENCE_SHA256,
        "actual_candidate_records_sha256": actual_digest,
    })
    validate_complete_original_cases(full, producer, campaign)
    return full


def validate_candidate_record_counts(compact: dict, records: object,
                                     suite: object,
                                     producer: types.ModuleType,
                                     history: types.ModuleType,
                                     campaign: types.ModuleType) -> bool:
    vector = compact.get("candidate_records")
    need(type(vector) is dict and type(records) in (list, tuple),
         "require the actual complete post-observation candidate case vector")
    if suite == ORIGINAL_SUITE:
        expected = validate_original_observation(compact, records, producer)
        full = validate_complete_original_cases(vector, producer, campaign)
        need(full["record_count"] == PUBLIC_RECORD_COUNT
             and vector["actual_candidate_records_sha256"] == expected
             and compact["actual_candidate_case_count"] == EXECUTED_CASE_COUNT,
             "preserve all 152 observed original records and 151 executions")
        return True
    need(vector.get("total_count")
         == compact.get("actual_candidate_case_count",
                        vector.get("total_count")),
         "preserve the genuine complete non-original case denominator")
    return True


def complete_records_preserved(records: object, compact: dict,
                               history: types.ModuleType) -> bool:
    if type(records) not in (list, tuple):
        return True
    vector = compact.get("candidate_records")
    return bool(type(vector) is dict
                and vector.get("complete_vector_embedded") is True
                and vector.get("truncated") is False
                or len(records) <= history.MAX_VECTOR_PREFIX)


def record_prefix_truncated(records: object, compact: dict,
                            history: types.ModuleType) -> bool:
    if type(records) not in (list, tuple):
        return False
    vector = compact.get("candidate_records")
    return bool(len(records) > history.MAX_VECTOR_PREFIX
                and not (type(vector) is dict
                         and vector.get("complete_vector_embedded") is True
                         and vector.get("truncated") is False))


def validate_decoded_original(decoded: dict, suite: object,
                              producer: types.ModuleType,
                              history: types.ModuleType,
                              campaign: types.ModuleType) -> None:
    if suite != ORIGINAL_SUITE:
        return
    observed = decoded.get("original_observation")
    need(type(observed) is dict
         and decoded.get("all_original_records_and_mismatches_preserved")
         is True
         and decoded.get("original_record_prefix_explicitly_truncated")
         is False,
         "never publish a preview as complete original observations")
    vector = observed.get("candidate_records")
    validate_complete_original_cases(vector, producer, campaign)
    need(observed.get("actual_candidate_case_count") == EXECUTED_CASE_COUNT
         and observed.get("actual_public_record_count") == PUBLIC_RECORD_COUNT
         and observed.get("actual_debug_skip_count") == DEBUG_SKIP_COUNT
         and observed.get("matrix_sha256") == MATRIX_SHA256
         and observed.get("reference_records_sha256") == REFERENCE_SHA256
         and vector["actual_candidate_records_sha256"]
         == observed.get("candidate_records_sha256"),
         "preserve all original observation identities after JSON round trip")


def validate_v5(document: object) -> dict:
    need(type(document) is dict
         and document.get("schema")
         == "rebar-owned-six-family-original-p0-producer-v5-source-freeze"
         and document.get("version") == 5
         and document.get("goal_sha256") == GOAL_SHA256
         and document.get("suite_count") == 13
         and document.get("case_execution_denominator") == 31237
         and document.get("named_private_waiver_count")
         == len(PRIVATE_WAIVER_NAMES)
         and tuple(document.get("named_private_waivers", ()))
         == PRIVATE_WAIVER_NAMES
         and document.get("source", {}).get("sha256") == V5[0][1]
         and document.get("protocol", {}).get("sha256") == V5[1][1]
         and document.get("performance") == "NOT MEASURED"
         and document.get("memory") == "NOT MEASURED"
         and document.get("holdout") == "NOT OPENED",
         "preserve the complete immutable independent original V5 producer")
    upstream = document.get("original_upstream")
    need(type(upstream) is dict
         and upstream.get("all_source_ordered_method_count")
         == SOURCE_METHOD_COUNT
         and upstream.get("public_record_count") == PUBLIC_RECORD_COUNT
         and upstream.get("runnable_public_method_count")
         == EXECUTED_CASE_COUNT
         and upstream.get("release_debug_skip_count") == DEBUG_SKIP_COUNT
         and upstream.get("private_waiver_count")
         == len(PRIVATE_WAIVER_NAMES)
         and tuple(upstream.get("named_private_waivers", ()))
         == PRIVATE_WAIVER_NAMES
         and upstream.get("matrix_sha256") == MATRIX_SHA256
         and upstream.get("reference_records_sha256") == REFERENCE_SHA256
         and upstream.get("original_evaluator") == owner_record(
             ORIGINAL_EVALUATOR
         )
         and upstream.get("harness") == owner_record(ORIGINAL_HARNESS),
         "never merge original matrix, observed records, and runnable cases")
    suites = document.get("suites")
    need(type(suites) is list and len(suites) == 13
         and sum(item.get("case_execution_count", -1)
                 for item in suites if type(item) is dict) == 31237,
         "preserve all 13 real suites and all 31,237 original obligations")
    original = suites[0]
    need(type(original) is dict
         and original.get("id") == ORIGINAL_SUITE
         and original.get("case_execution_count") == EXECUTED_CASE_COUNT
         and original.get("matrix_sha256") == MATRIX_SHA256
         and original.get("reference_records_sha256") == REFERENCE_SHA256
         and original.get("source_relative") == ORIGINAL_EVALUATOR[0]
         and original.get("source_sha256") == ORIGINAL_SOURCE_SHA256,
         "reject a replaced immutable original suite or reference vector")
    return document


def validate_c11_receipt(receipt: object) -> dict:
    need(type(receipt) is dict
         and receipt.get("schema")
         == "rebar-owned-repaired-c-original-campaign-v11-"
            "durable-publication-receipt"
         and receipt.get("version") == 11
         and receipt.get("status") == "PASS"
         and receipt.get("publication_status") == "PASS"
         and receipt.get("publication_pass_means")
         == "DURABLE CORRECTNESS PUBLICATION ONLY"
         and receipt.get("family") == "c"
         and receipt.get("label")
         == "phase2-v21-c-original-match-semantics-original-p0-v11"
         and receipt.get("source_sha256") == C11[0][1]
         and receipt.get("protocol_sha256") == C11[1][1]
         and receipt.get("contract_sha256") == C11[2][1]
         and receipt.get("candidate_status") == "FAIL"
         and receipt.get("candidate_qualified") is False
         and receipt.get("suite_count") == 13
         and receipt.get("attempted_suite_count") == 13
         and receipt.get("completed_suite_count") == 11
         and receipt.get("case_execution_denominator") == 31237
         and receipt.get("actual_candidate_workers") == 13
         and receipt.get("actual_worker_process_ids_are_distinct") is True
         and receipt.get("candidate_execution_failure_count") == 2
         and receipt.get("infrastructure_failure_count") == 0
         and receipt.get("worker_timeout_count") == 0
         and receipt.get("verified_passing_case_count") == 16262
         and receipt.get("semantic_mismatch_count") == "NOT MEASURED"
         and receipt.get("observed_semantic_mismatch_lower_bound") == 606
         and receipt.get("complete_observed_semantic_mismatch_record_count")
         == 606
         and receipt.get("complete_mismatch_suite_count") == 11
         and receipt.get("complete_mismatch_chunk_count") == 21
         and receipt.get("all_observed_semantic_mismatch_records_preserved")
         is True
         and receipt.get("counterexample_normalization_before_original_comparison")
         is False
         and receipt.get("counterexample_preview_only") is False
         and receipt.get("named_private_waiver_count")
         == len(PRIVATE_WAIVER_NAMES)
         and receipt.get("hidden_cases_read") == 0
         and receipt.get("benchmark_files_read") == 0
         and receipt.get("clock_samples") == 0
         and receipt.get("timing_trials_run") == 0
         and receipt.get("performance") == "NOT MEASURED"
         and receipt.get("holdout") == "NOT OPENED"
         and receipt.get("winner_selected") is False,
         "preserve the genuine failed C11 campaign and every observed mismatch")
    archive = receipt.get("archive")
    need(type(archive) is dict
         and archive.get("path")
         == "oracle/phase2/evidence/repaired-c-original-campaign-v11-c-"
            "phase2-v21-c-original-match-semantics-original-p0-v11-"
            "failures.json.gz"
         and archive.get("sha256")
         == "2d580a5d321767b1753a645961d717cbc4345f1151c7a0d34304d6e6579cc609"
         and archive.get("bytes") == 195101
         and archive.get("device") == DEVICE
         and archive.get("inode") == 525588
         and archive.get("mode") == "0600"
         and archive.get("nlink") == 1
         and archive.get("exclusive_creation") is True
         and archive.get("file_fsync_completed") is True
         and archive.get("directory_fsync_completed") is True,
         "pin historical archive metadata without opening the archive")
    outcomes = receipt.get("suite_outcomes")
    processes = receipt.get("actual_worker_process_ids")
    need(type(outcomes) is list and len(outcomes) == 13
         and type(processes) is list and len(processes) == 13
         and all(type(number) is int and number > 0 for number in processes)
         and len(set(processes)) == 13,
         "preserve all 13 real distinct, separately guarded C11 workers")
    mismatch_total = 0
    verified = 0
    unfinished = 0
    for row, expected, pid in zip(outcomes, C11_OUTCOMES,
                                  processes, strict=True):
        name, denominator, status, category, mismatches = expected
        need(type(row) is dict
             and row.get("suite") == name
             and row.get("case_execution_denominator") == denominator
             and row.get("status") == status
             and row.get("failure_class") == category
             and row.get("actual_candidate_workers") == 1
             and row.get("worker_process_id") == pid,
             "preserve the genuine complete or unfinished C11 suite: " + name)
        if mismatches is None:
            need(row.get("mismatch_count") == "NOT MEASURED",
                 "never fabricate an unfinished genuine C11 observation")
            unfinished += 1
        else:
            need(row.get("mismatch_count") == mismatches,
                 "never discard an observed genuine C11 mismatch")
            mismatch_total += mismatches
            if mismatches == 0:
                verified += denominator
        if name == ORIGINAL_SUITE:
            need(row.get("error_type") == "CampaignError"
                 and row.get("failure_phase")
                 == "ENCODE COMPLETE GUARDED RESULT"
                 and row.get("plain_failure_diagnostic")
                 == "preserve the genuine complete original case denominator",
                 "preserve the real failed C11 original encoder")
        if name == "subinterpreter_v2":
            need(row.get("error_type") == "ActualSuiteFailure"
                 and row.get("failure_phase")
                 == "OBSERVE COMPLETE ORIGINAL SUITE"
                 and row.get("plain_failure_diagnostic")
                 == "preserve the actual guarded original child lifecycle failure",
                 "never claim the unfinished guarded child failure was fixed")
    need(mismatch_total == 606 and verified == 16262 and unfinished == 2,
         "preserve the exact C11 completion and mismatch denominators")
    fingerprints = receipt.get("complete_mismatch_suite_vector_fingerprints")
    need(type(fingerprints) is list
         and len(fingerprints) == len(C11_FINGERPRINTS),
         "retain all 11 independently published original mismatch vectors")
    for actual, expected in zip(fingerprints, C11_FINGERPRINTS, strict=True):
        name, denominator, records, chunks, digest = expected
        need(type(actual) is dict
             and actual.get("suite") == name
             and actual.get("case_execution_denominator") == denominator
             and actual.get("complete_record_count") == records
             and actual.get("complete_chunk_count") == chunks
             and actual.get("complete_vector_sha256") == digest
             and actual.get("all_observed_records_preserved") is True,
             "reject an omitted or replaced C11 full mismatch vector: " + name)
    need(sum(item[2] for item in C11_FINGERPRINTS) == 606
         and sum(item[3] for item in C11_FINGERPRINTS) == 21,
         "preserve all 606 genuinely recorded mismatch records and 21 chunks")
    return receipt


def validate_previous_c12(receipt: object, freeze: object) -> dict:
    need(type(freeze) is dict
         and freeze.get("schema")
             == "rebar-owned-repaired-c-original-campaign-v12-source-freeze"
         and freeze.get("version") == 12
         and freeze.get("source", {}).get("sha256") == PREVIOUS_C12[0][1]
         and freeze.get("protocol", {}).get("sha256") == PREVIOUS_C12[1][1]
         and freeze.get("phase_one_v4", {}).get(
             "original_case_execution_denominator") == 31_237,
         "authenticate the entire independently frozen original C12 campaign")
    need(type(receipt) is dict
         and receipt.get("schema")
             == "rebar-owned-repaired-c-original-campaign-v12-"
                "durable-publication-receipt"
         and receipt.get("version") == 12
         and receipt.get("status") == "PASS"
         and receipt.get("publication_status") == "PASS"
         and receipt.get("candidate_status") == "FAIL"
         and receipt.get("suite_count") == 13
         and receipt.get("attempted_suite_count") == 13
         and receipt.get("completed_suite_count") == 12
         and receipt.get("actual_candidate_workers") == 13
         and receipt.get("actual_worker_process_ids_are_distinct") is True
         and receipt.get("case_execution_denominator") == 31_237
         and receipt.get("verified_passing_case_count") == 16_413
         and receipt.get("candidate_execution_failure_count") == 1
         and receipt.get("observed_semantic_mismatch_lower_bound") == 606
         and receipt.get("complete_observed_semantic_mismatch_record_count")
             == 606
         and receipt.get("complete_mismatch_chunk_count") == 21
         and receipt.get("all_observed_semantic_mismatch_records_preserved")
             is True
         and receipt.get("complete_original_case_records_preserved") is True
         and receipt.get("complete_original_public_record_count") == 152
         and receipt.get("complete_original_executed_case_count") == 151
         and receipt.get("candidate_qualified") is False,
         "preserve all 606 C12 mismatches, one failure, and 16,413 observations")
    return receipt


def validate_previous_c14_crash(receipt: object, freeze: object) -> dict:
    need(type(freeze) is dict
         and freeze.get("schema")
             == "rebar-owned-repaired-c-original-campaign-v14-source-freeze"
         and freeze.get("version") == 14
         and freeze.get("source", {}).get("sha256") == PREVIOUS_C14[0][1]
         and freeze.get("protocol", {}).get("sha256") == PREVIOUS_C14[1][1]
         and freeze.get("phase_one_v4", {}).get(
             "original_case_execution_denominator") == 31_237
         and freeze.get("qualified_candidate_count") == 0,
         "preserve the exact independently committed C14 source freeze")
    need(type(receipt) is dict
         and set(receipt) == {
             "candidate_qualified", "candidate_result", "error_message",
             "error_type", "exit_code", "original_adapter_restored",
             "original_native_restored", "schema", "status",
             "winner_selected",
         }
         and receipt.get("schema")
             == "rebar-owned-repaired-c-original-campaign-v14-"
                "publication-recursion-failure"
         and receipt.get("status") == "FAIL"
         and receipt.get("error_type") == "RecursionError"
         and receipt.get("error_message") == "maximum recursion depth exceeded"
         and receipt.get("exit_code") == 2
         and receipt.get("candidate_result") == "NOT PUBLISHED"
         and receipt.get("original_adapter_restored") is True
         and receipt.get("original_native_restored") is True
         and receipt.get("candidate_qualified") is False
         and receipt.get("winner_selected") is False,
         "preserve the actual C14 recursive publication crash and exact recovery")
    return receipt


def validate_previous_c15(receipt: object, freeze: object,
                          correction: object, application: object) -> dict:
    need(type(freeze) is dict
         and freeze.get("schema")
             == "rebar-owned-repaired-c-original-campaign-v15-source-freeze"
         and freeze.get("version") == 15
         and freeze.get("source", {}).get("sha256") == PREVIOUS_C15[0][1]
         and freeze.get("protocol", {}).get("sha256") == PREVIOUS_C15[1][1]
         and freeze.get("qualified_candidate_count") == 0,
         "preserve the exact committed, actually completed C15 original freeze")
    need(type(receipt) is dict
         and receipt.get("schema")
             == "rebar-owned-repaired-c-original-campaign-v15-"
                "durable-publication-receipt"
         and receipt.get("version") == 15
         and receipt.get("publication_status") == "PASS"
         and receipt.get("candidate_status") == "FAIL"
         and receipt.get("source_sha256") == PREVIOUS_C15[0][1]
         and receipt.get("protocol_sha256") == PREVIOUS_C15[1][1]
         and receipt.get("contract_sha256") == PREVIOUS_C15[2][1]
         and receipt.get("suite_count") == 13
         and receipt.get("attempted_suite_count") == 13
         and receipt.get("completed_suite_count") == 13
         and receipt.get("case_execution_denominator") == 31237
         and receipt.get("actual_candidate_workers") == 13
         and receipt.get("actual_worker_process_ids_are_distinct") is True
         and receipt.get("verified_passing_case_count") == 22798
         and receipt.get("semantic_mismatch_count") == 224
         and receipt.get("complete_observed_semantic_mismatch_record_count") == 224
         and receipt.get("complete_mismatch_chunk_count") == 9
         and receipt.get("all_observed_semantic_mismatch_records_preserved") is True
         and receipt.get("candidate_execution_failure_count") == 0
         and receipt.get("infrastructure_failure_count") == 0
         and receipt.get("worker_timeout_count") == 0
         and receipt.get("complete_original_case_records_preserved") is True
         and receipt.get("complete_original_public_record_count") == 152
         and receipt.get("complete_original_executed_case_count") == 151
         and receipt.get("candidate_qualified") is False,
         "retain all 224 actually observed C15 records and all original workers")
    rows = receipt.get("suite_outcomes")
    need(type(rows) is list and len(rows) == 13
         and {row["suite"]: row["mismatch_count"] for row in rows
              if row["mismatch_count"]} == {
                  "original_bounded_v5": 2,
                  "public_types_v1": 144,
                  "public_surface_v19": 78,
              }, "preserve complete actual C15 2 + 144 + 78 mismatch cohorts")
    need(type(correction) is dict
         and correction.get("schema")
             == "rebar-owned-c-final-public-semantics-v1-source-freeze"
         and correction.get("source", {}).get("sha256") == FINAL_REPAIR[0][1]
         and correction.get("protocol", {}).get("sha256") == FINAL_REPAIR[1][1],
         "authenticate exact independently frozen final C dual-source repair")
    targets = correction.get("first_party_correction")
    need(type(targets) is dict
         and targets.get("target_sha256") == CORRECTED_ADAPTER_SHA256
         and targets.get("target_bytes") == CORRECTED_ADAPTER_BYTES
         and targets.get("native_target_sha256") == CORRECTED_NATIVE_SOURCE_SHA256
         and targets.get("native_target_bytes") == CORRECTED_NATIVE_SOURCE_BYTES
         and targets.get("complete_observed_mismatches_targeted") == 224,
         "reject changed final first-party adapter/native correction owners")
    need(type(application) is dict
         and application.get("schema")
             == "rebar-owned-c-final-public-semantics-v1-recorded-application"
         and application.get("status") == "APPLIED"
         and application.get("source_sha256") == FINAL_REPAIR[0][1]
         and application.get("protocol_sha256") == FINAL_REPAIR[1][1]
         and application.get("contract_sha256") == FINAL_REPAIR[2][1]
         and application.get("historical_mismatches_targeted") == 224
         and application.get("candidate_correctness") == "NOT MEASURED"
         and application.get("winner_selected") is False,
         "authenticate actual root-only final first-party C source materialization")
    created = application.get("created")
    need(type(created) is dict
         and created.get("adapter", {}).get("sha256") == CORRECTED_ADAPTER_SHA256
         and created.get("adapter", {}).get("bytes") == CORRECTED_ADAPTER_BYTES
         and created.get("adapter", {}).get("inode") == 526585
         and created.get("native", {}).get("sha256")
             == CORRECTED_NATIVE_SOURCE_SHA256
         and created.get("native", {}).get("bytes") == CORRECTED_NATIVE_SOURCE_BYTES
         and created.get("native", {}).get("inode") == 526586,
         "preserve exact actual final adapter/native source inode provenance")
    return receipt


def validate_c24_receipts(build: object, root: object,
                          freeze: object) -> dict:
    schema = "rebar-owned-c-complete-semantic-source-build-v24"
    need(type(freeze) is dict
         and freeze.get("schema") == schema + "-source-freeze"
         and freeze.get("version") == 24
         and freeze.get("source", {}).get("sha256") == C24_BUILD[0][1]
         and freeze.get("protocol", {}).get("sha256") == C24_BUILD[1][1],
         "authenticate the exact independently frozen complete C24 source build")
    for document, suffix in ((build, "-durable-publication-receipt"),
                             (root, "-durable-root-provenance-receipt")):
        need(type(document) is dict
             and document.get("schema") == schema + suffix
             and document.get("version") == 24
             and document.get("status") == "PASS"
             and document.get("family") == "c"
             and document.get("label")
                 == "phase2-v24-c-complete-semantic-source-build"
             and document.get("source_sha256") == C24_BUILD[0][1]
             and document.get("protocol_sha256") == C24_BUILD[1][1]
             and document.get("contract_sha256") == C24_BUILD[2][1]
             and document.get("actual_compiler_process_count") == 14
             and document.get("expected_compiler_process_count") == 14
             and document.get("native_artifact_sha256") == C24_NATIVE_SHA256
             and document.get("native_artifact_bytes") == C24_NATIVE_BYTES
             and document.get("corrected_native_source_sha256")
                 == CORRECTED_NATIVE_SOURCE_SHA256
             and document.get("corrected_adapter_source_sha256")
                 == CORRECTED_ADAPTER_SHA256
             and document.get("candidate_workers_started") == 0
             and document.get("native_libraries_loaded") == 0
             and document.get("candidate_sources_persistently_modified") == 0,
             "reject incomplete, unbuilt, substituted, or delegated C24 evidence")
    need(build.get("build_status") == "PASS"
         and build.get("private_phase_count") == 2
         and build.get("distinct_phase_source_owner_count") == 4
         and build.get("distinct_native_artifact_count") == 2
         and build.get("byte_identical_native_artifacts") is True
         and build.get("corrected_native_source_bytes")
             == CORRECTED_NATIVE_SOURCE_BYTES
         and build.get("corrected_adapter_source_bytes") == CORRECTED_ADAPTER_BYTES
         and build.get("corrected_guard_source_sha256") == V4_GUARD[0][1]
         and build.get("preserved_latest_c12_failure_receipt_sha256")
             == PREVIOUS_C12_FAILURE[1]
         and build.get("preserved_latest_c12_observed_mismatches") == 606
         and root.get("canonical_build_receipt_sha256") == C24_PUBLIC_RECEIPT[1]
         and root.get("latest_c12_failure_receipt_sha256")
             == PREVIOUS_C12_FAILURE[1]
         and build.get("preserved_actual_c15_failure_receipt_sha256")
             == PREVIOUS_C15_FAILURE[1]
         and build.get("preserved_actual_c15_exact_mismatch_count") == 224
         and root.get("preserved_actual_c15_failure_receipt_sha256")
             == PREVIOUS_C15_FAILURE[1]
         and build.get("actual_native_materialization_receipt_sha256")
             == FINAL_APPLICATION[1]
         and build.get("actual_adapter_materialization_receipt_sha256")
             == FINAL_APPLICATION[1],
         "require both exact C24 phases and preserve the complete C12 failure")
    private = root.get("root")
    need(type(private) is dict
         and private.get("path") == C24_ROOT_PATH
         and private.get("device") == C24_ROOT_DEVICE
         and private.get("inode") == C24_ROOT_INODE
         and private.get("mode") == "0700"
         and private.get("phase_count") == 2,
         "bind only receipt-attested C24 private root metadata without statting")
    phases = private.get("phases")
    need(type(phases) is list and len(phases) == 2,
         "require two distinct independently authenticated C24 build phases")
    native_identities = set()
    source_identities = set()
    for offset, phase in enumerate(phases):
        need(type(phase) is dict
             and phase.get("name") == ("reference-a", "reference-b")[offset]
             and phase.get("device") == C24_ROOT_DEVICE
             and phase.get("mode") == "0700",
             "reject reordered, substituted, or unsafe private C24 phase")
        native = phase.get("native_output")
        need(type(native) is dict and native.get("sha256") == C24_NATIVE_SHA256
             and native.get("bytes") == C24_NATIVE_BYTES
             and native.get("name")
                 == "_vm_native.cpython-314-x86_64-linux-gnu.so"
             and native.get("native_loaded") is False
             and native.get("nlink") == 1
             and type(native.get("inode")) is int and native["inode"] > 0,
             "reject exchanged first-party C24 native artifact")
        identity = (native["device"], native["inode"])
        need(identity not in native_identities,
             "do not count one C24 native artifact as two phases")
        native_identities.add(identity)
        owners = phase.get("source_owners")
        need(type(owners) is list and len(owners) == 2,
             "require separately authenticated native and adapter source owners")
        for owner, role, fingerprint, count in (
            (owners[0], "complete-first-party-native-source",
             CORRECTED_NATIVE_SOURCE_SHA256, CORRECTED_NATIVE_SOURCE_BYTES),
            (owners[1], "corrected-first-party-python-adapter",
             CORRECTED_ADAPTER_SHA256, CORRECTED_ADAPTER_BYTES),
        ):
            need(type(owner) is dict and owner.get("role") == role
                 and owner.get("sha256") == fingerprint
                 and owner.get("bytes") == count
                 and owner.get("device") == C24_ROOT_DEVICE
                 and owner.get("mode") == "0600" and owner.get("nlink") == 1
                 and type(owner.get("inode")) is int and owner["inode"] > 0,
                 "reject substituted exact C24 private " + role)
            source_identity = (owner["device"], owner["inode"])
            need(source_identity not in source_identities,
                 "reject a C24 source inode reused across phases")
            source_identities.add(source_identity)
    need(len(native_identities) == 2 and len(source_identities) == 4,
         "retain both distinct native and all four exact C24 source identities")
    return {"build": build, "root": root, "freeze": freeze,
            "private_root": private, "phases": phases}


def private_phase_payload(c24: dict, role: str) -> tuple[bytes, dict]:
    phase = c24["phases"][0]
    if role == "adapter":
        expected = phase["source_owners"][1]
    elif role == "native":
        expected = phase["native_output"]
    elif role == "native_source":
        expected = phase["source_owners"][0]
    else:
        raise RuntimeError("refuse an invented C24 private source role")
    root_fd = phase_fd = handle = None
    try:
        directory_flags = (os.O_RDONLY | os.O_DIRECTORY
                           | getattr(os, "O_NOFOLLOW", 0)
                           | getattr(os, "O_CLOEXEC", 0))
        root_fd = os.open(C24_ROOT_PATH, directory_flags)
        root_info = os.fstat(root_fd)
        need(stat.S_ISDIR(root_info.st_mode)
             and (root_info.st_dev, root_info.st_ino)
                 == (C24_ROOT_DEVICE, C24_ROOT_INODE)
             and root_info.st_uid == os.geteuid()
             and stat.S_IMODE(root_info.st_mode) == 0o700,
             "refuse a foreign root during authorized C24 phase authentication")
        phase_fd = os.open("reference-a", directory_flags, dir_fd=root_fd)
        phase_info = os.fstat(phase_fd)
        need((phase_info.st_dev, phase_info.st_ino)
             == (phase["device"], phase["inode"])
             and stat.S_IMODE(phase_info.st_mode) == 0o700,
             "refuse a substituted root-receipt-bound C24 first phase")
        handle = os.open(expected["name"],
                         os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                         | getattr(os, "O_CLOEXEC", 0), dir_fd=phase_fd)
        before = os.fstat(handle)
        need(stat.S_ISREG(before.st_mode)
             and (before.st_dev, before.st_ino, before.st_size)
                 == (expected["device"], expected["inode"], expected["bytes"])
             and before.st_uid == os.geteuid()
             and before.st_nlink == 1
             and format(stat.S_IMODE(before.st_mode), "04o") == expected["mode"],
             "reject exchanged or linked private C24 " + role)
        chunks = []
        left = before.st_size
        while left:
            piece = os.read(handle, min(left, 131_072))
            need(bool(piece), "reject truncated authentic private C24 " + role)
            chunks.append(piece)
            left -= len(piece)
        need(os.read(handle, 1) == b"",
             "reject expanded authentic private C24 " + role)
        payload = b"".join(chunks)
        need(hashlib.sha256(payload).hexdigest() == expected["sha256"],
             "reject changed actual C24 phase " + role)
        after = os.fstat(handle)
        need((before.st_dev, before.st_ino, before.st_size,
              before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject private C24 " + role + " exchanged while hashing")
        return payload, dict(expected)
    finally:
        for descriptor in (handle, phase_fd, root_fd):
            if descriptor is not None:
                os.close(descriptor)


def current_adapter(previous: types.ModuleType, fingerprint: str,
                    size: int, *, expected_inode: int | None = None) -> dict:
    handle = os.open(ROOT + "/" + ADAPTER_TARGET_RELATIVE,
                     os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                     | getattr(os, "O_CLOEXEC", 0))
    try:
        before = os.fstat(handle)
        need(stat.S_ISREG(before.st_mode)
             and before.st_dev == DEVICE and before.st_size == size
             and before.st_uid == os.geteuid()
             and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600
             and (expected_inode is None or before.st_ino == expected_inode),
             "reject a substituted canonical first-party C adapter")
        previous.hash_descriptor(handle, size, fingerprint)
        after = os.fstat(handle)
        need((before.st_dev, before.st_ino, before.st_size,
              before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject canonical C adapter changed during authentication")
        return {"path": ADAPTER_TARGET_RELATIVE, "sha256": fingerprint,
                "bytes": size, "device": before.st_dev, "inode": before.st_ino,
                "mode": "0600", "nlink": before.st_nlink,
                "uid": before.st_uid}
    finally:
        os.close(handle)


def restore_corrected_adapter(previous: types.ModuleType,
                              producer: types.ModuleType,
                              journal: dict, fingerprint: str) -> dict:
    observed, _ = previous.read_private(ADAPTER_JOURNAL_NAME,
                                        fingerprint, producer)
    need(observed == journal
         and journal.get("schema") == SCHEMA + "-dual-adapter-recovery-journal"
         and journal.get("family") == "c" and journal.get("label") == LABEL
         and journal.get("target_relative") == ADAPTER_TARGET_RELATIVE
         and journal.get("backup_filename") == ADAPTER_BACKUP_NAME
         and journal.get("stage_filename") == ADAPTER_STAGE_NAME
         and journal.get("corrected_adapter_sha256") == CORRECTED_ADAPTER_SHA256
         and journal.get("corrected_adapter_bytes") == CORRECTED_ADAPTER_BYTES
         and journal.get("build_receipt_sha256") == C24_PUBLIC_RECEIPT[1]
         and journal.get("root_receipt_sha256") == C24_ROOT_RECEIPT[1],
         "refuse an unowned, crossed, or unsafe C adapter recovery journal")
    original = journal["original_adapter"]
    parent_fd = previous.native_directory()
    try:
        try:
            backup = os.stat(ADAPTER_BACKUP_NAME, dir_fd=parent_fd,
                             follow_symlinks=False)
        except FileNotFoundError:
            backup = None
        target = os.stat(ADAPTER_TARGET_NAME, dir_fd=parent_fd,
                         follow_symlinks=False)
        if backup is not None:
            need(stat.S_ISREG(backup.st_mode)
                 and (backup.st_dev, backup.st_ino)
                     == (original["device"], original["inode"])
                 and stat.S_IMODE(backup.st_mode) == 0o600,
                 "refuse to restore an unrelated canonical C adapter inode")
            if (target.st_dev, target.st_ino) == (backup.st_dev, backup.st_ino):
                need(target.st_nlink == 2 and backup.st_nlink == 2,
                     "reject changed original C adapter hard-link ownership")
                os.unlink(ADAPTER_BACKUP_NAME, dir_fd=parent_fd)
            else:
                need(target.st_dev == DEVICE and target.st_nlink == 1
                     and target.st_size == CORRECTED_ADAPTER_BYTES
                     and stat.S_IMODE(target.st_mode) == 0o600,
                     "refuse to overwrite foreign canonical C adapter")
                current_adapter(previous, CORRECTED_ADAPTER_SHA256,
                                CORRECTED_ADAPTER_BYTES, expected_inode=target.st_ino)
                os.replace(ADAPTER_BACKUP_NAME, ADAPTER_TARGET_NAME,
                           src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
            os.fsync(parent_fd)
        else:
            need((target.st_dev, target.st_ino)
                 == (original["device"], original["inode"]),
                 "refuse unjournaled, missing, or foreign C adapter recovery")
        try:
            stage = os.stat(ADAPTER_STAGE_NAME, dir_fd=parent_fd,
                            follow_symlinks=False)
        except FileNotFoundError:
            stage = None
        if stage is not None:
            need(stat.S_ISREG(stage.st_mode) and stage.st_dev == DEVICE
                 and stage.st_uid == os.geteuid() and stage.st_nlink == 1
                 and stat.S_IMODE(stage.st_mode) == 0o600
                 and stage.st_size <= CORRECTED_ADAPTER_BYTES,
                 "refuse a foreign C adapter recovery stage")
            descriptor = os.open(ADAPTER_STAGE_NAME,
                                 os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                                 dir_fd=parent_fd)
            try:
                prefix = os.read(descriptor, CORRECTED_ADAPTER_BYTES + 1)
                full, _ = private_phase_payload(journal["c24_evidence"], "adapter")
                need(prefix == full[:len(prefix)],
                     "refuse a non-C24 adapter-stage prefix")
            finally:
                os.close(descriptor)
            os.unlink(ADAPTER_STAGE_NAME, dir_fd=parent_fd)
            os.fsync(parent_fd)
        restored = current_adapter(previous, ORIGINAL_ADAPTER_SHA256,
                                   ORIGINAL_ADAPTER_BYTES,
                                   expected_inode=original["inode"])
        need(restored == original,
             "restore the exact original C adapter device/inode/mode/hash")
        return {"schema": SCHEMA + "-dual-adapter-recovery",
                "status": "PASS", "journal_sha256": fingerprint,
                "original_adapter": restored,
                "exact_original_adapter_inode_restored": True,
                "holdout": "NOT OPENED"}
    finally:
        os.close(parent_fd)


def activate_corrected_adapter(previous: types.ModuleType,
                               producer: types.ModuleType,
                               parsed: dict, c24: dict) -> dict:
    original = current_adapter(previous, ORIGINAL_ADAPTER_SHA256,
                               ORIGINAL_ADAPTER_BYTES, expected_inode=428074)
    payload, source = private_phase_payload(c24, "adapter")
    previous.prepare_recovery_root()
    journal = {
        "schema": SCHEMA + "-dual-adapter-recovery-journal",
        "status": "PREPARED", "version": 16, "family": "c", "label": LABEL,
        "controller_source_sha256": parsed["--source-sha256"],
        "controller_protocol_sha256": parsed["--protocol-sha256"],
        "controller_contract_sha256": parsed["--contract-sha256"],
        "build_receipt_sha256": C24_PUBLIC_RECEIPT[1],
        "root_receipt_sha256": C24_ROOT_RECEIPT[1],
        "target_relative": ADAPTER_TARGET_RELATIVE,
        "backup_filename": ADAPTER_BACKUP_NAME,
        "stage_filename": ADAPTER_STAGE_NAME,
        "original_adapter": original,
        "corrected_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "corrected_adapter_bytes": CORRECTED_ADAPTER_BYTES,
        "corrected_phase_source": source,
        "c24_evidence": c24,
        "holdout": "NOT OPENED",
    }
    journal_owner = previous.exclusive_document(previous.RECOVERY_ROOT,
                                                ADAPTER_JOURNAL_NAME,
                                                journal, producer)
    parent_fd = previous.native_directory()
    stage_fd = None
    linked = False
    try:
        for name in (ADAPTER_BACKUP_NAME, ADAPTER_STAGE_NAME):
            try:
                os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise RuntimeError("reject preexisting C adapter recovery artifact")
        os.link(ADAPTER_TARGET_NAME, ADAPTER_BACKUP_NAME,
                src_dir_fd=parent_fd, dst_dir_fd=parent_fd,
                follow_symlinks=False)
        linked = True
        os.fsync(parent_fd)
        stage_fd = os.open(ADAPTER_STAGE_NAME,
                           os.O_WRONLY | os.O_CREAT | os.O_EXCL
                           | getattr(os, "O_NOFOLLOW", 0),
                           0o600, dir_fd=parent_fd)
        initial = os.fstat(stage_fd)
        need(stat.S_ISREG(initial.st_mode) and initial.st_dev == DEVICE
             and initial.st_uid == os.geteuid() and initial.st_nlink == 1
             and stat.S_IMODE(initial.st_mode) == 0o600,
             "require owner-only same-device authenticated C adapter staging")
        previous.write_all(stage_fd, payload)
        os.fsync(stage_fd)
        finished = os.fstat(stage_fd)
        need((finished.st_dev, finished.st_ino, finished.st_size)
             == (DEVICE, initial.st_ino, CORRECTED_ADAPTER_BYTES),
             "reject truncated or exchanged canonical C adapter stage")
        os.close(stage_fd)
        stage_fd = None
        os.replace(ADAPTER_STAGE_NAME, ADAPTER_TARGET_NAME,
                   src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        os.fsync(parent_fd)
        active = current_adapter(previous, CORRECTED_ADAPTER_SHA256,
                                 CORRECTED_ADAPTER_BYTES,
                                 expected_inode=finished.st_ino)
        return {"schema": SCHEMA + "-dual-adapter-activation",
                "status": "PASS", "journal": journal_owner,
                "journal_document": journal,
                "original_adapter": original, "active_adapter": active}
    except BaseException:
        if stage_fd is not None:
            os.close(stage_fd)
        if linked:
            restore_corrected_adapter(previous, producer, journal,
                                      journal_owner["sha256"])
        raise
    finally:
        os.close(parent_fd)


def install_exact_c24_family(producer: types.ModuleType,
                             state: dict,
                             previous: types.ModuleType) -> tuple:
    original = producer.family_spec("c")
    need(original.name == "c"
         and original.module == "candidates.vm_candidate"
         and original.bridge_module == "candidates._vm_native"
         and original.adapter_relative == ADAPTER_TARGET_RELATIVE
         and original.engine_relative
             == "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"
         and original.bridge_relative == original.engine_relative
         and original.combined_native is True
         and original.owned_ctypes is False,
         "preserve the genuine immutable producer C-family identity")
    source_relative = previous.CORRECTED_SOURCE[0]
    owners = (
        (ADAPTER_TARGET_RELATIVE, CORRECTED_ADAPTER_SHA256,
         CORRECTED_ADAPTER_BYTES),
        (source_relative, CORRECTED_NATIVE_SOURCE_SHA256,
         CORRECTED_NATIVE_SOURCE_BYTES),
    )
    exact = producer.FamilySpec(
        original.name, original.module, original.adapter_relative,
        original.bridge_module, original.engine_relative,
        original.bridge_relative, owners, original.combined_native,
        original.owned_ctypes,
    )
    producer.OWNED_SOURCES["c"] = owners
    producer.FAMILIES["c"] = exact
    original_owner_check = producer.exact_native_owners

    def prove_exact_c24(spec: object, pins: object,
                        source_pins: object) -> dict:
        need(spec is exact
             and pins == {
                 "source": CORRECTED_ADAPTER_SHA256,
                 "native_engine": C24_NATIVE_SHA256,
                 "native_bridge": C24_NATIVE_SHA256,
             }
             and source_pins == {
                 ADAPTER_TARGET_RELATIVE: CORRECTED_ADAPTER_SHA256,
                 source_relative: CORRECTED_NATIVE_SOURCE_SHA256,
             },
             "reject crossed, stale, or incomplete exact C24 family pins")
        _, expected = private_phase_payload(state["c24"], "native_source")
        path = C24_ROOT_PATH + "/reference-a/vm_native.c"
        descriptor = os.open(path, os.O_RDONLY
                             | getattr(os, "O_NOFOLLOW", 0)
                             | getattr(os, "O_CLOEXEC", 0))
        try:
            identity = os.fstat(descriptor)
            need((identity.st_dev, identity.st_ino, identity.st_size)
                 == (expected["device"], expected["inode"], expected["bytes"])
                 and stat.S_IMODE(identity.st_mode) == 0o600
                 and identity.st_uid == os.geteuid()
                 and identity.st_nlink == 1,
                 "reject substituted C24 producer private native-source descriptor")
            true_open = os.open

            def exact_source_open(target: object, flags: object,
                                  mode: int = 0o777,
                                  **kwargs: object) -> int:
                if target != ROOT + "/" + source_relative:
                    return true_open(target, flags, mode, **kwargs)
                need(type(flags) is int
                     and flags & os.O_ACCMODE == os.O_RDONLY
                     and flags & getattr(os, "O_NOFOLLOW", 0)
                     and not flags & (getattr(os, "O_CREAT", 0)
                                      | getattr(os, "O_TRUNC", 0)
                                      | getattr(os, "O_APPEND", 0))
                     and kwargs.get("dir_fd") is None,
                     "reject unowned corrected-source write or alias")
                os.lseek(descriptor, 0, os.SEEK_SET)
                return os.dup(descriptor)

            try:
                os.open = exact_source_open
                observed = original_owner_check(spec, pins, source_pins)
            finally:
                os.open = true_open
            observed["corrected_phase_c_source"] = dict(expected)
            need(observed["corrected_phase_c_source"]["sha256"]
                 == CORRECTED_NATIVE_SOURCE_SHA256,
                 "attest the exact C24 producer-owned private source")
            return observed
        finally:
            os.close(descriptor)

    producer.exact_native_owners = prove_exact_c24
    return exact, {
        "source": CORRECTED_ADAPTER_SHA256,
        "native_engine": C24_NATIVE_SHA256,
        "native_bridge": C24_NATIVE_SHA256,
    }, {name: fingerprint for name, fingerprint, _ in owners}


def synthetic_original(producer: types.ModuleType) -> tuple[dict, list]:
    records = []
    for index in range(PUBLIC_RECORD_COUNT):
        skipped = index == 37
        failed = index == 51
        identity = SKIPPED_TEST if skipped else "ReTests.synthetic_" + str(index)
        records.append({
            "test": identity,
            "source_ast_sha256": hashlib.sha256(
                ("frozen-source-control-" + str(index)).encode("ascii")
            ).hexdigest(),
            "status": "SKIP" if skipped else "FAIL" if failed else "PASS",
            "tests_run": 1,
            "failure_count": 1 if failed else 0,
            "error_count": 0,
            "skip_count": 1 if skipped else 0,
            "failure_tracebacks": ["authentic-shaped source-only FAILURE"]
            if failed else [],
            "error_tracebacks": [],
            "skip_reasons": list(SKIP_REASONS) if skipped else [],
        })
    observed = {
        "suite": ORIGINAL_SUITE,
        "source_relative": ORIGINAL_EVALUATOR[0],
        "source_sha256": ORIGINAL_SOURCE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "reference_records_sha256": REFERENCE_SHA256,
        "candidate_records_sha256": hashlib.sha256(
            producer.canonical(records)
        ).hexdigest(),
        "case_execution_denominator": EXECUTED_CASE_COUNT,
        "actual_candidate_case_count": EXECUTED_CASE_COUNT,
        "actual_public_record_count": PUBLIC_RECORD_COUNT,
        "actual_debug_skip_count": DEBUG_SKIP_COUNT,
        "named_private_waiver_count": len(PRIVATE_WAIVER_NAMES),
        "named_private_waivers": list(PRIVATE_WAIVER_NAMES),
    }
    return observed, records


def original_case_hostile_controls(producer: types.ModuleType,
                                   history: types.ModuleType,
                                   campaign: types.ModuleType) -> list[str]:
    controls: list[str] = []
    observed, records = synthetic_original(producer)
    vector = encode_candidate_records(
        records, observed, producer, history, ORIGINAL_SUITE, campaign,
    )
    compact = {**observed, "candidate_records": vector}
    need(validate_candidate_record_counts(
        compact, records, ORIGINAL_SUITE, producer, history, campaign,
    ) is True
         and validate_complete_original_cases(
             vector, producer, campaign
         )["record_count"] == PUBLIC_RECORD_COUNT
         and vector["complete_chunk_count"] > 1
         and vector["preview_truncated"] is True
         and vector["truncated"] is False
         and complete_records_preserved(records, compact, history) is True
         and record_prefix_truncated(records, compact, history) is False
         and any(record["status"] == "FAIL" for record in records)
         and vector["actual_candidate_records_sha256"] != REFERENCE_SHA256,
         "preserve all 152 source-only synthetic records including a real-shaped loss")
    controls.append("preserve 165 source methods, 152 full public records, and 151 cases")
    controls.append("preserve exactly one authentic-shaped original debug skip")
    controls.append("preserve candidate failure tracebacks without forcing reference equality")
    controls.append("embed and round-trip every original public case chunk")
    controls.append("reject the old 24-record preview as complete observation")

    def cloned() -> dict:
        return {
            **vector,
            "complete_chunks": [dict(chunk)
                                for chunk in vector["complete_chunks"]],
        }

    def reject_vector(label: str, changed: object) -> None:
        refused = False
        try:
            validate_complete_original_cases(changed, producer, campaign)
        except (CampaignError, campaign.CampaignError, ValueError,
                TypeError, producer.ProducerError, KeyError):
            refused = True
        need(refused, "accept incomplete original public case vector: " + label)
        controls.append(label)

    def reject_observation(label: str, changed: dict,
                           actual: object = None) -> None:
        refused = False
        try:
            validate_original_observation(
                changed, records if actual is None else actual, producer,
            )
        except (CampaignError, campaign.CampaignError, ValueError,
                TypeError, producer.ProducerError, KeyError):
            refused = True
        need(refused, "accept a forged original public observation: " + label)
        controls.append(label)

    for key, bad in (
        ("source_method_count", 152),
        ("public_record_count", 151),
        ("complete_record_count", 151),
        ("total_count", 165),
        ("case_execution_denominator", 152),
        ("actual_debug_skip_count", 0),
        ("named_private_waiver_count", 0),
        ("matrix_sha256", "0" * 64),
        ("reference_records_sha256", "0" * 64),
        ("actual_candidate_records_sha256", "0" * 64),
        ("source_complete_vector_sha256", "0" * 64),
        ("transport_complete_vector_sha256", "0" * 64),
        ("complete_vector_embedded", False),
        ("all_observed_records_preserved", False),
        ("truncated", True),
        ("source_comparison_modified", True),
        ("schema", SCHEMA + "-lossless-original-mismatch-vector"),
        ("suite", "public_v3"),
        ("vector_kind", "ORIGINAL MISMATCHES"),
    ):
        changed = cloned()
        changed[key] = bad
        reject_vector("reject forged complete original case " + key, changed)

    preview_only = history.lossless_vector(
        records, producer,
        expected=observed["candidate_records_sha256"],
        suite_name=ORIGINAL_SUITE,
    )
    reject_vector("reject digest-and-preview-only original candidate records",
                  preview_only)
    missing = cloned()
    missing["complete_chunks"] = missing["complete_chunks"][:-1]
    missing["complete_chunk_count"] = len(missing["complete_chunks"])
    reject_vector("reject a dropped complete original public-case chunk", missing)
    duplicate = cloned()
    duplicate["complete_chunks"][1] = dict(duplicate["complete_chunks"][0])
    reject_vector("reject a duplicated original public-case chunk", duplicate)
    reordered = cloned()
    reordered["complete_chunks"][0], reordered["complete_chunks"][1] = (
        reordered["complete_chunks"][1], reordered["complete_chunks"][0]
    )
    reject_vector("reject reordered original public-case chunks", reordered)
    for field, bad in (
        ("first_record_index", 1),
        ("record_count", 31),
        ("uncompressed_sha256", "0" * 64),
        ("compressed_sha256", "0" * 64),
        ("complete_compressed_base64", ""),
        ("codec", "EXTERNAL REGEX PACKAGE"),
    ):
        broken = cloned()
        broken["complete_chunks"][0][field] = bad
        reject_vector("reject substituted complete original case " + field,
                      broken)

    for key, bad in (
        ("matrix_sha256", "0" * 64),
        ("reference_records_sha256", "0" * 64),
        ("source_sha256", "0" * 64),
        ("source_relative", "tools/invented_original.py"),
        ("case_execution_denominator", 152),
        ("actual_candidate_case_count", 152),
        ("actual_public_record_count", 151),
        ("actual_debug_skip_count", 0),
        ("named_private_waiver_count", 12),
        ("candidate_records_sha256", "0" * 64),
    ):
        changed = dict(observed)
        changed[key] = bad
        reject_observation("reject forged original observation " + key,
                           changed)
    fewer = [dict(item) for item in records[:-1]]
    reject_observation("reject a truncated 151-record original observation",
                       dict(observed), fewer)
    reordered_records = [dict(item) for item in records]
    reordered_records[0], reordered_records[1] = (
        reordered_records[1], reordered_records[0]
    )
    reject_observation("reject reordered source-ordered original public cases",
                       dict(observed), reordered_records)
    duplicate_records = [dict(item) for item in records]
    duplicate_records[1] = dict(duplicate_records[0])
    reject_observation("reject a duplicated original public case identity",
                       dict(observed), duplicate_records)
    missing_skip = [dict(item) for item in records]
    missing_skip[37] = {**missing_skip[37], "status": "PASS",
                        "skip_count": 0, "skip_reasons": []}
    reject_observation("reject an omitted authentic original debug-build skip",
                       dict(observed), missing_skip)
    substituted_skip = [dict(item) for item in records]
    substituted_skip[37] = {**substituted_skip[37],
                             "skip_reasons": ["invented skip"]}
    reject_observation("reject an invented original debug-build skip reason",
                       dict(observed), substituted_skip)
    erased_failure = [dict(item) for item in records]
    erased_failure[51] = {**erased_failure[51], "status": "PASS",
                          "failure_count": 0, "failure_tracebacks": []}
    reject_observation("reject normalization or removal of an original failure",
                       dict(observed), erased_failure)
    crossed_private = [dict(item) for item in records]
    crossed_private[0] = {**crossed_private[0],
                          "test": PRIVATE_WAIVER_NAMES[0]}
    reject_observation("reject a named private waiver as a public original case",
                       dict(observed), crossed_private)
    need("re" not in sys.modules and "_sre" not in sys.modules
         and "ctypes" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "all complete-case controls must remain genuinely matcher-free")
    controls.append("run full original case controls without loading a matcher")
    return controls


def dual_publisher_hostile_controls(configure: object) -> list[str]:
    need(type(configure) is types.FunctionType,
         "require the authentic C15 controller installer for closure proof")

    def nested_code(parent: types.CodeType, name: str) -> types.CodeType:
        found = [item for item in parent.co_consts
                 if type(item) is types.CodeType and item.co_name == name]
        need(len(found) == 1,
             "reject a missing or duplicated actual dual publisher: " + name)
        return found[0]

    context = nested_code(configure.__code__, "context")
    complete = nested_code(context, "publish_full")
    dual = nested_code(context, "dual_run")
    restored = nested_code(dual, "publish_after_dual_restore")
    need("complete_case_inner_publisher" in context.co_cellvars
         and "dual_restored_case_publisher" in context.co_cellvars
         and "complete_case_inner_publisher" in complete.co_freevars
         and "dual_restored_case_publisher" not in complete.co_freevars
         and "dual_restored_case_publisher" in restored.co_freevars
         and "complete_case_inner_publisher" not in restored.co_freevars
         and "prior_publisher" not in context.co_cellvars,
         "reject the authenticated C14 late-bound publisher self-cycle")
    counts = {"complete": 0, "dual": 0, "terminal": 0}
    synthetic_producer = object()
    synthetic_previous = object()

    def terminal(document: dict, producer: object,
                 previous: object) -> dict:
        counts["terminal"] += 1
        need(counts["terminal"] == 1
             and producer is synthetic_producer
             and previous is synthetic_previous
             and document.get("adapter_restored") is True
             and document.get("native_restored") is True,
             "reject a repeated or crossed synthetic terminal publisher")
        return {"status": "PASS", "terminal_calls": 1}

    complete_case_inner_publisher = terminal

    def complete_once(document: dict, producer: object,
                      previous: object) -> dict:
        counts["complete"] += 1
        need(counts["complete"] == 1,
             "reject recursive complete original-case publication")
        return complete_case_inner_publisher(document, producer, previous)

    dual_restored_case_publisher = complete_once

    def dual_once(document: dict, producer: object,
                  previous: object) -> dict:
        counts["dual"] += 1
        need(counts["dual"] == 1,
             "reject recursive exact dual-owner restoration publication")
        document.update({"adapter_restored": True, "native_restored": True})
        return dual_restored_case_publisher(document, producer, previous)

    result = dual_once({}, synthetic_producer, synthetic_previous)
    need(result == {"status": "PASS", "terminal_calls": 1}
         and counts == {"complete": 1, "dual": 1, "terminal": 1}
         and "re" not in sys.modules and "_sre" not in sys.modules
         and "ctypes" not in sys.modules,
         "exercise both synthetic actual publisher wrappers exactly once")
    return [
        "prove exact actual complete and dual publisher closure cells differ",
        "execute synthetic complete-case publisher exactly once",
        "execute synthetic dual-restoration publisher exactly once",
        "execute synthetic final receipt publisher exactly once",
        "preserve matcher-free source-only dual publisher controls",
    ]


def install_v16(campaign: types.ModuleType, history: types.ModuleType,
                module: types.ModuleType, transform: dict) -> None:
    historical_configure = module.configure_previous
    historical_contract = module.contract_document
    historical_controls = module.source_controls

    def configure(previous: types.ModuleType) -> tuple:
        old, original = historical_configure(previous)
        existing = {item[0]: item for item in old.STATIC_OWNERS}
        for owner in (C11 + V5 + V3 + V4_GUARD + PREVIOUS_C12
                      + SUPERSEDED_C13 + PREVIOUS_C14 + PREVIOUS_C15
                      + HISTORICAL_C23 + FINAL_REPAIR + C24_BUILD
                      + (C11_RECEIPT, PREVIOUS_C12_FAILURE,
                         PREVIOUS_C14_CRASH, PREVIOUS_C15_FAILURE,
                         HISTORICAL_C23_PUBLIC, HISTORICAL_C23_ROOT,
                         FINAL_APPLICATION, C24_PUBLIC_RECEIPT,
                         C24_ROOT_RECEIPT, ORIGINAL_HARNESS,
                         ORIGINAL_EVALUATOR)):
            before = existing.get(owner[0])
            need(before is None or before == owner,
                 "reject a crossed authentic C11, V5, or original source owner")
            if before is None:
                existing[owner[0]] = owner
        for relative in existing:
            need(not relative.startswith(("/", "candidates/", "docs/evidence/"))
                 and not any(word in relative.lower()
                             for word in ("holdout", "benchmark"))
                 and not relative.endswith(
                     (".so", ".gz", ".xz", ".zip", ".tar")
                 ),
                 "physically exclude native, candidate, archive, and holdout")
        old.STATIC_OWNERS = tuple(existing.values())
        old.OWNED_PATHS = frozenset(existing) | {SOURCE, PROTOCOL, CONTRACT}

        previous_authority = previous.actual_authority

        def authority() -> dict:
            actual = previous_authority()
            actual.update({
                "previous_v11_failure_receipt_sha256": C11_RECEIPT[1],
                "v11_source_sha256": C11[0][1],
                "v11_protocol_sha256": C11[1][1],
                "v11_contract_sha256": C11[2][1],
                "previous_v12_source_sha256": PREVIOUS_C12[0][1],
                "previous_v12_protocol_sha256": PREVIOUS_C12[1][1],
                "previous_v12_contract_sha256": PREVIOUS_C12[2][1],
                "previous_v12_failure_receipt_sha256": PREVIOUS_C12_FAILURE[1],
                "previous_v14_source_sha256": PREVIOUS_C14[0][1],
                "previous_v14_protocol_sha256": PREVIOUS_C14[1][1],
                "previous_v14_contract_sha256": PREVIOUS_C14[2][1],
                "previous_v14_crash_receipt_sha256": PREVIOUS_C14_CRASH[1],
                "previous_v15_source_sha256": PREVIOUS_C15[0][1],
                "previous_v15_protocol_sha256": PREVIOUS_C15[1][1],
                "previous_v15_contract_sha256": PREVIOUS_C15[2][1],
                "previous_v15_failure_receipt_sha256": PREVIOUS_C15_FAILURE[1],
                "historical_c23_source_sha256": HISTORICAL_C23[0][1],
                "historical_c23_protocol_sha256": HISTORICAL_C23[1][1],
                "historical_c23_contract_sha256": HISTORICAL_C23[2][1],
                "historical_c23_publication_sha256": HISTORICAL_C23_PUBLIC[1],
                "historical_c23_root_sha256": HISTORICAL_C23_ROOT[1],
                "final_repair_source_sha256": FINAL_REPAIR[0][1],
                "final_repair_protocol_sha256": FINAL_REPAIR[1][1],
                "final_repair_contract_sha256": FINAL_REPAIR[2][1],
                "final_repair_application_sha256": FINAL_APPLICATION[1],
                "superseded_v13_source_sha256": SUPERSEDED_C13[0][1],
                "superseded_v13_protocol_sha256": SUPERSEDED_C13[1][1],
                "superseded_v13_contract_sha256": SUPERSEDED_C13[2][1],
                "c24_source_sha256": C24_BUILD[0][1],
                "c24_protocol_sha256": C24_BUILD[1][1],
                "c24_contract_sha256": C24_BUILD[2][1],
                "c24_publication_sha256": C24_PUBLIC_RECEIPT[1],
                "c24_root_sha256": C24_ROOT_RECEIPT[1],
                "corrected_native_source_sha256": CORRECTED_NATIVE_SOURCE_SHA256,
                "corrected_adapter_source_sha256": CORRECTED_ADAPTER_SHA256,
                "corrected_native_sha256": C24_NATIVE_SHA256,
                "corrected_native_bytes": str(C24_NATIVE_BYTES),
                "build_source_sha256": C24_BUILD[0][1],
                "build_protocol_sha256": C24_BUILD[1][1],
                "build_contract_sha256": C24_BUILD[2][1],
                "build_receipt_sha256": C24_PUBLIC_RECEIPT[1],
                "root_receipt_sha256": C24_ROOT_RECEIPT[1],
                "native_engine_sha256": C24_NATIVE_SHA256,
                "native_bridge_sha256": C24_NATIVE_SHA256,
                "derived_variant_sha256": CORRECTED_NATIVE_SOURCE_SHA256,
                "guard_source_sha256": V4_GUARD[0][1],
                "guard_protocol_sha256": V4_GUARD[1][1],
                "guard_contract_sha256": V4_GUARD[2][1],
                "guard_v4_source_sha256": V4_GUARD[0][1],
                "guard_v4_protocol_sha256": V4_GUARD[1][1],
                "guard_v4_contract_sha256": V4_GUARD[2][1],
            })
            return actual

        previous.actual_authority = authority

        def install_actual_v4_guard(state: dict, inode: int) -> tuple:
            raw = state.get("c24_guard_raw")
            need(type(raw) is bytes
                 and hashlib.sha256(raw).hexdigest() == V4_GUARD[0][1]
                 and state.get("c24_guard_contract", {}).get("version") == 4
                 and type(inode) is int and inode > 0,
                 "require independently authenticated V4 before any C import")
            previous.clean_runtime()
            guard = types.ModuleType("_rebar_owned_actual_c_v16_runtime_guard_v4")
            guard.__file__ = ROOT + "/" + V4_GUARD[0][0]
            guard.__package__ = ""
            exec(compile(raw, guard.__file__, "exec", dont_inherit=True),
                 guard.__dict__)
            need(guard.SELF == V4_GUARD[0][0]
                 and guard.PROTOCOL == V4_GUARD[1][0]
                 and guard.CONTRACT == V4_GUARD[2][0]
                 and guard.PREVIOUS.SELF == V3[0][0]
                 and guard.RuntimePolicy.__bases__
                     == (guard.PREVIOUS.RuntimePolicy,)
                 and guard.RuntimePolicy.prepare_family
                     is guard.BASE.RuntimePolicy.prepare_family
                 and guard.RuntimePolicy.prepare_family.__globals__
                     is guard.BASE.__dict__
                 and guard.child_bootstrap_source
                     is guard.BASE.child_bootstrap_source,
                 "preserve exact V4/V3/V2 policy ancestry and frozen child code")
            policy = guard.RuntimePolicy()
            policy.install()
            bridge = previous.native_guard_owner("bridge", inode)
            engine = previous.native_guard_owner("engine", inode)
            need(set(bridge) == guard.NATIVE_OWNER_KEYS
                 and set(engine) == guard.NATIVE_OWNER_KEYS
                 and bridge["sha256"] == C24_NATIVE_SHA256
                 and engine["sha256"] == C24_NATIVE_SHA256,
                 "reject incomplete or substituted exact C24 native guard roles")
            policy.prepare_family("c", bridge_owner=bridge, engine_owner=engine)
            if not sys.path or sys.path[0] != ROOT:
                sys.path.insert(0, ROOT)
            candidate = __import__("candidates.vm_candidate",
                                   fromlist=["__name__"])
            policy.bind_selected(candidate, "c")
            native = sys.modules.get("candidates._vm_native")
            need(policy.installed and policy.prepared_family == "c"
                 and policy.bridge_owner == bridge
                 and policy.engine_owner == engine
                 and sys.modules.get("re") is candidate
                 and type(native) is types.ModuleType
                 and os.path.abspath(native.__file__)
                     == ROOT + "/candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"
                 and "_sre" not in sys.modules and "ctypes" not in sys.modules,
                 "install strict V4 before exactly one corrected first-party C import")
            policy.check_modules()
            return policy, candidate

        previous.install_worker_guard = install_actual_v4_guard
        previous_collect = previous.collect_context

        def context(selected: types.ModuleType, parsed: dict,
                    *, controls: bool = False) -> tuple:
            producer, state, result = previous_collect(
                selected, parsed, controls=controls,
            )
            if parsed["mode"] == "--run":
                complete_case_inner_publisher = module.publish_evidence

                def publish_full(document: dict,
                                 live_producer: types.ModuleType,
                                 live_previous: types.ModuleType) -> dict:
                    need(live_producer is producer
                         and live_previous is previous,
                         "reject a crossed original C12 complete-case publisher")
                    rows = document.get("suite_results")
                    need(type(rows) is list and len(rows) == 13,
                         "retain all original C12 suites before publication")
                    original_row = rows[0]
                    need(type(original_row) is dict
                         and original_row.get("suite") == ORIGINAL_SUITE,
                         "retain the first source-ordered genuine original suite")
                    observation = original_row.get("original_observation")
                    if type(observation) is dict:
                        vector = observation.get("candidate_records")
                        validate_complete_original_cases(
                            vector, producer, campaign,
                        )
                        need(original_row.get(
                            "all_original_records_and_mismatches_preserved"
                        ) is True
                             and original_row.get(
                                 "original_record_prefix_explicitly_truncated"
                             ) is False,
                             "never publish a prefix-only original case result")
                        document.update({
                            "complete_original_case_records_preserved": True,
                            "complete_original_public_record_count":
                            PUBLIC_RECORD_COUNT,
                            "complete_original_executed_case_count":
                            EXECUTED_CASE_COUNT,
                            "complete_original_source_method_count":
                            SOURCE_METHOD_COUNT,
                            "complete_original_case_vector_sha256":
                            vector["actual_candidate_records_sha256"],
                        })
                    else:
                        document.update({
                            "complete_original_case_records_preserved": False,
                            "complete_original_public_record_count":
                            "NOT MEASURED",
                            "complete_original_executed_case_count":
                            "NOT MEASURED",
                            "complete_original_source_method_count":
                            "NOT MEASURED",
                            "complete_original_case_vector_sha256":
                            "NOT MEASURED",
                        })
                    return complete_case_inner_publisher(
                        document, live_producer, live_previous,
                    )

                module.publish_evidence = publish_full
            result.update({
                "actual_c24_build_receipt_sha256": C24_PUBLIC_RECEIPT[1],
                "actual_c24_root_receipt_sha256": C24_ROOT_RECEIPT[1],
                "actual_c24_native_sha256": C24_NATIVE_SHA256,
                "corrected_c24_adapter_sha256": CORRECTED_ADAPTER_SHA256,
                "runtime_guard_version": 4,
                "previous_c12_failure_receipt_sha256": PREVIOUS_C12_FAILURE[1],
                "previous_c12_observed_semantic_mismatch_lower_bound": 606,
                "previous_c14_crash_receipt_sha256": PREVIOUS_C14_CRASH[1],
                "previous_c14_candidate_result": "NOT PUBLISHED",
                "previous_c15_failure_receipt_sha256":
                PREVIOUS_C15_FAILURE[1],
                "previous_c15_exact_semantic_mismatch_count": 224,
                "candidate_qualified": False,
                "runtime_non_delegation": "NOT ESTABLISHED",
                "final_holdout": FINAL_HOLDOUT_STATUS,
            })
            if parsed["mode"] in ("--run", "--worker", "--recover"):
                c24 = state["c24"]
                state["build"] = c24["build"]
                state["root_receipt"] = c24["root"]
                state["root"] = c24["private_root"]
                previous.BUILD = C24_BUILD
                previous.BUILD_RECEIPT = C24_PUBLIC_RECEIPT
                previous.ROOT_RECEIPT = C24_ROOT_RECEIPT
                previous.NATIVE_SHA256 = C24_NATIVE_SHA256
                previous.NATIVE_BYTES = C24_NATIVE_BYTES
                native_source = c24["phases"][0]["source_owners"][0]
                corrected_source = (
                    "candidates/c/variants/final_public_semantics_v1/vm_native.c",
                    CORRECTED_NATIVE_SOURCE_SHA256,
                    CORRECTED_NATIVE_SOURCE_BYTES,
                    native_source["inode"],
                )
                previous.CORRECTED_SOURCE = corrected_source
                corrected_adapter = (
                    ADAPTER_TARGET_RELATIVE, CORRECTED_ADAPTER_SHA256,
                    CORRECTED_ADAPTER_BYTES,
                    0,
                )
                previous.ADAPTER = corrected_adapter
                prior_record = previous.record

                def corrected_record(owner: tuple) -> dict:
                    if owner is previous.CORRECTED_SOURCE:
                        source = c24["phases"][0]["source_owners"][0]
                        return {
                            "path": C24_ROOT_PATH + "/reference-a/vm_native.c",
                            "sha256": source["sha256"],
                            "bytes": source["bytes"],
                            "device": source["device"],
                            "inode": source["inode"],
                            "mode": source["mode"],
                            "nlink": source["nlink"],
                            "role": "complete-first-party-native-source",
                            "phase": "reference-a",
                            "root_receipt_sha256": C24_ROOT_RECEIPT[1],
                            "prospective_workspace_materialized": False,
                        }
                    if owner is previous.ADAPTER:
                        return current_adapter(previous,
                                               CORRECTED_ADAPTER_SHA256,
                                               CORRECTED_ADAPTER_BYTES)
                    return prior_record(owner)

                previous.record = corrected_record

                def read_c24_native(_root: dict) -> tuple[bytes, dict]:
                    payload, owner = private_phase_payload(c24, "native")
                    return payload, {**owner, "uid": os.geteuid(),
                                     "phase_name": "reference-a"}

                previous.read_root_phase = read_c24_native
                historical_validate = previous.validate_build_and_root

                def validate_actual(build: dict, root_receipt: dict) -> dict:
                    if build.get("version") == 24:
                        return validate_c24_receipts(
                            build, root_receipt, c24["freeze"],
                        )["private_root"]
                    return historical_validate(build, root_receipt)

                previous.validate_build_and_root = validate_actual

                def c24_guard_owner(role: str, inode: int) -> dict:
                    need(role in ("bridge", "engine")
                         and type(inode) is int and inode > 0,
                         "reject an invented exact C24 native guard role")
                    filename = "_vm_native.cpython-314-x86_64-linux-gnu.so"
                    relative = "candidates/" + filename
                    absolute = ROOT + "/" + relative
                    descriptor = os.open(absolute,
                                         os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                                         | getattr(os, "O_CLOEXEC", 0))
                    try:
                        info = os.fstat(descriptor)
                        need(stat.S_ISREG(info.st_mode)
                             and info.st_dev == DEVICE and info.st_ino == inode
                             and info.st_size == C24_NATIVE_BYTES
                             and info.st_uid == os.geteuid()
                             and info.st_nlink == 1
                             and stat.S_IMODE(info.st_mode) == 0o600,
                             "reject foreign staged C24 canonical native inode")
                        previous.hash_descriptor(descriptor, C24_NATIVE_BYTES,
                                                 C24_NATIVE_SHA256)
                    finally:
                        os.close(descriptor)
                    owner = {"role": role, "family": "c",
                             "relative": relative, "absolute_path": absolute,
                             "file_name": filename,
                             "sha256": C24_NATIVE_SHA256,
                             "bytes": C24_NATIVE_BYTES,
                             "size_bytes": C24_NATIVE_BYTES,
                             "device": DEVICE, "inode": inode, "mode": 0o600,
                             "uid": os.geteuid(), "nlink": 1,
                             "native_loaded": False}
                    return owner

                previous.native_guard_owner = c24_guard_owner
                previous.activate_corrected_family = (
                    lambda live_producer: install_exact_c24_family(
                        live_producer, state, previous,
                    )
                )

            if parsed["mode"] == "--run":
                prior_run = module.run_campaign
                dual_restored_case_publisher = module.publish_evidence

                def dual_run(actual: dict, live_producer: types.ModuleType,
                             live_state: dict,
                             live_previous: types.ModuleType) -> dict:
                    need(live_producer is producer and live_state is state
                         and live_previous is previous,
                         "reject crossed C24 dual-owner original controller")
                    active_adapter = activate_corrected_adapter(
                        previous, producer, actual, state["c24"],
                    )
                    journal = active_adapter["journal_document"]
                    journal_sha = active_adapter["journal"]["sha256"]
                    inherited_prepare = previous.prepare_recovery_root
                    adapter_restored = False

                    def existing_recovery_root() -> None:
                        handle = previous.directory(previous.RECOVERY_ROOT,
                                                    mode=0o700)
                        try:
                            info = os.fstat(handle)
                            need(stat.S_ISDIR(info.st_mode)
                                 and info.st_uid == os.geteuid()
                                 and stat.S_IMODE(info.st_mode) == 0o700,
                                 "reject substituted shared dual-owner recovery root")
                        finally:
                            os.close(handle)

                    previous.prepare_recovery_root = existing_recovery_root

                    def publish_after_dual_restore(document: dict,
                                                   owned_producer: types.ModuleType,
                                                   owned_previous: types.ModuleType
                                                   ) -> dict:
                        nonlocal adapter_restored
                        restored = restore_corrected_adapter(
                            previous, producer, journal, journal_sha,
                        )
                        adapter_restored = True
                        document.update({
                            "corrected_c24_adapter_sha256":
                                CORRECTED_ADAPTER_SHA256,
                            "corrected_c24_native_sha256": C24_NATIVE_SHA256,
                            "original_adapter_inode_restored": True,
                            "original_adapter_restoration": restored,
                            "all_canonical_c_owners_restored_before_publication": True,
                            "candidate_qualified": False,
                            "runtime_non_delegation": "NOT ESTABLISHED",
                            "final_holdout": FINAL_HOLDOUT_STATUS,
                        })
                        return dual_restored_case_publisher(
                            document, owned_producer, owned_previous,
                        )

                    module.publish_evidence = publish_after_dual_restore
                    try:
                        result = prior_run(actual, live_producer, live_state,
                                           live_previous)
                    finally:
                        module.publish_evidence = dual_restored_case_publisher
                        previous.prepare_recovery_root = inherited_prepare
                        if not adapter_restored:
                            restore_corrected_adapter(previous, producer,
                                                      journal, journal_sha)
                    result.update({
                        "original_adapter_inode_restored": True,
                        "corrected_c24_adapter_sha256": CORRECTED_ADAPTER_SHA256,
                        "corrected_c24_native_sha256": C24_NATIVE_SHA256,
                        "candidate_qualified": False,
                        "runtime_non_delegation": "NOT ESTABLISHED",
                        "final_holdout": FINAL_HOLDOUT_STATUS,
                    })
                    return result

                module.run_campaign = dual_run
            return producer, state, result

        previous.collect_context = context
        return old, original

    def contract_document(parsed: dict, old: types.ModuleType,
                          state: dict, previous: types.ModuleType,
                          original_contract: object) -> dict:
        base = historical_contract(
            parsed, old, state, previous, original_contract,
        )
        producer = old.load_producer(state["producer_raw"])
        for owner in (C11 + V5 + V3 + V4_GUARD + PREVIOUS_C12
                      + SUPERSEDED_C13 + PREVIOUS_C14 + PREVIOUS_C15
                      + HISTORICAL_C23 + FINAL_REPAIR + C24_BUILD
                      + (C11_RECEIPT, PREVIOUS_C12_FAILURE,
                         PREVIOUS_C14_CRASH, PREVIOUS_C15_FAILURE,
                         HISTORICAL_C23_PUBLIC, HISTORICAL_C23_ROOT,
                         FINAL_APPLICATION, C24_PUBLIC_RECEIPT,
                         C24_ROOT_RECEIPT, ORIGINAL_HARNESS,
                         ORIGINAL_EVALUATOR)):
            raw = old.read_owner(owner)
            need(hashlib.sha256(raw).hexdigest() == owner[1],
                 "retain each exact authenticated complete V16 source owner")
        v5 = validate_v5(previous.parse_document(
            producer, old.read_owner(V5[2]),
            "complete immutable original C12 V5 producer contract",
        ))
        prior_contract = previous.parse_document(
            producer, old.read_owner(C11[2]),
            "complete immutable C11 source-freeze contract",
        )
        need(type(prior_contract) is dict
             and prior_contract.get("schema")
             == "rebar-owned-repaired-c-original-campaign-v11-source-freeze"
             and prior_contract.get("version") == 11
             and prior_contract.get("goal_sha256") == GOAL_SHA256
             and prior_contract.get("source", {}).get("sha256") == C11[0][1]
             and prior_contract.get("protocol", {}).get("sha256") == C11[1][1]
             and prior_contract.get("qualified_candidate_count") == 0
             and prior_contract.get("holdout") == "NOT OPENED"
             and prior_contract.get("performance") == "NOT MEASURED",
             "preserve the exact complete immutable C11 source-only contract")
        receipt = validate_c11_receipt(previous.parse_document(
            producer, old.read_owner(C11_RECEIPT),
            "complete genuine small C11 original failure publication receipt",
        ))
        previous_c12_contract = previous.parse_document(
            producer, old.read_owner(PREVIOUS_C12[2]),
            "complete independently frozen original C12 controller contract",
        )
        previous_c12_receipt = validate_previous_c12(
            previous.parse_document(
                producer, old.read_owner(PREVIOUS_C12_FAILURE),
                "complete actual C12 original 606-mismatch candidate FAIL",
            ), previous_c12_contract,
        )
        superseded_c13 = previous.parse_document(
            producer, old.read_owner(SUPERSEDED_C13[2]),
            "complete independently committed C13 source freeze; never executed",
        )
        need(superseded_c13.get("schema")
             == "rebar-owned-repaired-c-original-campaign-v13-source-freeze"
             and superseded_c13.get("version") == 13
             and superseded_c13.get("source", {}).get("sha256")
                 == SUPERSEDED_C13[0][1]
             and superseded_c13.get("protocol", {}).get("sha256")
                 == SUPERSEDED_C13[1][1]
             and superseded_c13.get("candidate_correctness") == "NOT MEASURED",
             "preserve the committed C13 freeze superseded before candidate execution")
        previous_c14_contract = previous.parse_document(
            producer, old.read_owner(PREVIOUS_C14[2]),
            "complete independently frozen original C14 controller",
        )
        previous_c14_crash = validate_previous_c14_crash(
            previous.parse_document(
                producer, old.read_owner(PREVIOUS_C14_CRASH),
                "complete actual C14 recursive publication failure receipt",
            ), previous_c14_contract,
        )
        previous_c15_contract = previous.parse_document(
            producer, old.read_owner(PREVIOUS_C15[2]),
            "complete independently frozen, actually run C15 controller",
        )
        final_repair_contract = previous.parse_document(
            producer, old.read_owner(FINAL_REPAIR[2]),
            "complete independently frozen final adapter and native repair",
        )
        final_repair_application = previous.parse_document(
            producer, old.read_owner(FINAL_APPLICATION),
            "actual final adapter and native source materialization receipt",
        )
        previous_c15_receipt = validate_previous_c15(
            previous.parse_document(
                producer, old.read_owner(PREVIOUS_C15_FAILURE),
                "complete actual C15 all-suite 224-mismatch failure",
            ), previous_c15_contract, final_repair_contract,
            final_repair_application,
        )
        c24_freeze = previous.parse_document(
            producer, old.read_owner(C24_BUILD[2]),
            "complete independently frozen C24 dual-source native build",
        )
        c24_publication = previous.parse_document(
            producer, old.read_owner(C24_PUBLIC_RECEIPT),
            "complete actual C24 dual-phase native publication receipt",
        )
        c24_root = previous.parse_document(
            producer, old.read_owner(C24_ROOT_RECEIPT),
            "complete actual C24 dual-phase private root provenance receipt",
        )
        c24 = validate_c24_receipts(c24_publication, c24_root, c24_freeze)
        guard_v4_raw = old.read_owner(V4_GUARD[0])
        guard_v4_contract = previous.parse_document(
            producer, old.read_owner(V4_GUARD[2]),
            "complete independently frozen strict actual V4 runtime guard",
        )
        need(guard_v4_contract.get("schema")
             == "rebar-owned-candidate-runtime-independence-v4-source-freeze"
             and guard_v4_contract.get("version") == 4
             and guard_v4_contract.get("source", {}).get("sha256")
                 == V4_GUARD[0][1]
             and guard_v4_contract.get("protocol", {}).get("sha256")
                 == V4_GUARD[1][1],
             "authenticate exact V4 guard while preserving immutable V2 child")
        state["c24"] = c24
        state["c24_guard_raw"] = guard_v4_raw
        state["c24_guard_contract"] = guard_v4_contract
        state["previous_c12_contract"] = previous_c12_contract
        state["previous_c12_receipt"] = previous_c12_receipt
        state["superseded_c13_contract"] = superseded_c13
        state["previous_c14_contract"] = previous_c14_contract
        state["previous_c14_crash"] = previous_c14_crash
        state["previous_c15_contract"] = previous_c15_contract
        state["previous_c15_receipt"] = previous_c15_receipt
        state["final_repair_contract"] = final_repair_contract
        state["final_repair_application"] = final_repair_application
        need(base.get("schema") == SCHEMA + "-source-freeze"
             and base.get("version") == 16
             and base.get("family") == "c"
             and base.get("label") == LABEL
             and base.get("goal_sha256") == GOAL_SHA256
             and base.get("phase_one_v4", {}).get(
                 "original_case_execution_denominator"
             ) == 31237
             and base.get("qualified_candidate_count") == 0
             and base.get("holdout") == "NOT OPENED"
             and base.get("performance") == "NOT MEASURED",
             "reject a guessed, prematurely qualified, or crossed C12 contract")
        policy = dict(base["actual_operation_policy"])
        policy.update({
            "authorization":
            "EXPLICIT INDEPENDENTLY PINNED C24 V16 ROOT --run ONLY",
            "required_authority": previous.actual_authority(),
            "previous_actual_v11_receipt_sha256": C11_RECEIPT[1],
            "previous_actual_v11_candidate_status": "FAIL",
            "previous_actual_v11_candidate_qualified": False,
            "previous_actual_v11_completed_original_suites": 11,
            "previous_actual_v11_original_candidate_execution_failures": 2,
            "previous_actual_v11_verified_passing_case_count": 16262,
            "previous_actual_v11_observed_mismatch_lower_bound": 606,
            "previous_actual_v11_exact_total_semantic_mismatches":
            "NOT MEASURED",
            "previous_actual_v11_complete_mismatch_record_count": 606,
            "previous_actual_v11_complete_mismatch_chunk_count": 21,
            "previous_actual_v11_archive_opened_in_source_mode": False,
            "previous_actual_v12_receipt_sha256": PREVIOUS_C12_FAILURE[1],
            "previous_actual_v12_candidate_status": "FAIL",
            "previous_actual_v12_completed_original_suites": 12,
            "previous_actual_v12_original_candidate_execution_failures": 1,
            "previous_actual_v12_verified_passing_case_count": 16_413,
            "previous_actual_v12_complete_mismatch_record_count": 606,
            "previous_actual_v12_complete_mismatch_chunk_count": 21,
            "previous_actual_v14_crash_receipt_sha256":
            PREVIOUS_C14_CRASH[1],
            "previous_actual_v14_publication_status": "FAIL",
            "previous_actual_v14_candidate_result": "NOT PUBLISHED",
            "previous_actual_v14_error_type": "RecursionError",
            "previous_actual_v14_original_adapter_restored": True,
            "previous_actual_v14_original_native_restored": True,
            "previous_actual_v15_failure_receipt_sha256":
            PREVIOUS_C15_FAILURE[1],
            "previous_actual_v15_candidate_status": "FAIL",
            "previous_actual_v15_completed_original_suites": 13,
            "previous_actual_v15_actual_candidate_workers": 13,
            "previous_actual_v15_verified_passing_case_count": 22798,
            "previous_actual_v15_exact_semantic_mismatch_count": 224,
            "previous_actual_v15_complete_mismatch_chunk_count": 9,
            "final_repair_application_receipt_sha256": FINAL_APPLICATION[1],
            "actual_c24_publication_receipt_sha256": C24_PUBLIC_RECEIPT[1],
            "actual_c24_root_receipt_sha256": C24_ROOT_RECEIPT[1],
            "actual_c24_native_sha256": C24_NATIVE_SHA256,
            "actual_c24_native_bytes": C24_NATIVE_BYTES,
            "actual_c24_corrected_adapter_sha256": CORRECTED_ADAPTER_SHA256,
            "actual_c24_corrected_adapter_bytes": CORRECTED_ADAPTER_BYTES,
            "runtime_guard_version": 4,
            "strict_v4_installed_before_candidate_import": True,
            "crash_journaled_canonical_owner_count": 2,
            "exact_original_adapter_inode_restoration_required": True,
            "exact_original_native_inode_restoration_required": True,
            "no_publication_before_both_owners_restored": True,
            "source_method_count": SOURCE_METHOD_COUNT,
            "public_record_count": PUBLIC_RECORD_COUNT,
            "executed_case_count": EXECUTED_CASE_COUNT,
            "authentic_debug_skip_count": DEBUG_SKIP_COUNT,
            "candidate_case_vector_fully_embedded": True,
            "candidate_case_vector_prefix_only": False,
            "candidate_case_vector_reference_equality_required": False,
            "candidate_case_failure_normalization": "FORBIDDEN",
            "candidate_case_codec": "PURE FIRST-PARTY C11 BOUNDED LZ1",
            "candidate_case_encoding_stage":
            "ONLY AFTER COMPLETE IMMUTABLE ORIGINAL COMPARISON",
            "original_or_reference_source_changes": 0,
            "source_freeze_runs_candidate": False,
        })
        base["actual_operation_policy"] = policy
        base["authenticated_complete_v11_controller_transform"] = transform
        base["preserved_full_v11_reporting_freeze"] = {
            "owners": [owner_record(owner) for owner in C11],
            "status": prior_contract["status"],
            "source_only_effects": prior_contract["source_only_effects"],
            "candidate_correctness": "NOT MEASURED",
            "historical_archive_opened": False,
            "frozen_original_source_changes": 0,
        }
        base["preserved_actual_c_v11_campaign"] = {
            "actual_failure_receipt": owner_record(C11_RECEIPT),
            "publication_status": receipt["publication_status"],
            "publication_pass_means": receipt["publication_pass_means"],
            "candidate_status": receipt["candidate_status"],
            "candidate_qualified": receipt["candidate_qualified"],
            "suite_count": receipt["suite_count"],
            "attempted_suite_count": receipt["attempted_suite_count"],
            "completed_suite_count": receipt["completed_suite_count"],
            "case_execution_denominator": receipt["case_execution_denominator"],
            "actual_candidate_workers": receipt["actual_candidate_workers"],
            "actual_worker_process_ids": receipt["actual_worker_process_ids"],
            "actual_worker_process_ids_are_distinct":
            receipt["actual_worker_process_ids_are_distinct"],
            "suite_outcomes": receipt["suite_outcomes"],
            "candidate_execution_failure_count":
            receipt["candidate_execution_failure_count"],
            "infrastructure_failure_count":
            receipt["infrastructure_failure_count"],
            "worker_timeout_count": receipt["worker_timeout_count"],
            "semantic_mismatch_count": receipt["semantic_mismatch_count"],
            "observed_semantic_mismatch_lower_bound":
            receipt["observed_semantic_mismatch_lower_bound"],
            "verified_passing_case_count": receipt["verified_passing_case_count"],
            "all_observed_semantic_mismatch_records_preserved":
            receipt["all_observed_semantic_mismatch_records_preserved"],
            "complete_observed_semantic_mismatch_record_count":
            receipt["complete_observed_semantic_mismatch_record_count"],
            "complete_mismatch_suite_count":
            receipt["complete_mismatch_suite_count"],
            "complete_mismatch_chunk_count":
            receipt["complete_mismatch_chunk_count"],
            "complete_mismatch_suite_vector_fingerprints":
            receipt["complete_mismatch_suite_vector_fingerprints"],
            "archive_metadata": dict(receipt["archive"]),
            "archive_opened_in_source_mode": False,
            "holdout": receipt["holdout"],
            "performance": receipt["performance"],
        }
        base["preserved_actual_c_v12_campaign"] = {
            "owners": [owner_record(owner) for owner in PREVIOUS_C12],
            "complete_contract_field_count": len(previous_c12_contract),
            "actual_failure_receipt": owner_record(PREVIOUS_C12_FAILURE),
            "publication_status": "PASS", "candidate_status": "FAIL",
            "candidate_qualified": False,
            "case_execution_denominator": 31_237,
            "suite_count": 13, "attempted_suite_count": 13,
            "completed_suite_count": 12, "actual_candidate_workers": 13,
            "verified_passing_case_count": 16_413,
            "candidate_execution_failure_count": 1,
            "observed_semantic_mismatch_lower_bound": 606,
            "complete_observed_semantic_mismatch_record_count": 606,
            "complete_mismatch_chunk_count": 21,
            "all_observed_semantic_mismatch_records_preserved": True,
            "complete_original_public_record_count": 152,
            "complete_original_executed_case_count": 151,
            "archive_opened_in_source_mode": False,
        }
        base["preserved_actual_c_v14_publication_recursion_failure"] = {
            "owners": [owner_record(owner) for owner in PREVIOUS_C14],
            "complete_contract_field_count": len(previous_c14_contract),
            "actual_crash_receipt": owner_record(PREVIOUS_C14_CRASH),
            "publication_status": previous_c14_crash["status"],
            "candidate_result": previous_c14_crash["candidate_result"],
            "error_type": previous_c14_crash["error_type"],
            "error_message": previous_c14_crash["error_message"],
            "exit_code": previous_c14_crash["exit_code"],
            "original_adapter_restored": True,
            "original_native_restored": True,
            "candidate_qualified": False,
            "winner_selected": False,
            "crash_cause": "LATE-BOUND SHARED PUBLISHER CLOSURE CELL",
            "repair": "DISTINCT AUTHENTICATED PUBLISHER CLOSURE CELLS",
            "candidate_results_fabricated_from_unpublished_stream": False,
            "historical_archive_opened_in_source_mode": False,
        }
        base["preserved_actual_c_v15_complete_failure"] = {
            "owners": [owner_record(owner) for owner in PREVIOUS_C15],
            "actual_failure_receipt": owner_record(PREVIOUS_C15_FAILURE),
            "publication_status": "PASS",
            "candidate_status": "FAIL",
            "candidate_qualified": False,
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "attempted_suite_count": 13,
            "completed_suite_count": 13,
            "actual_candidate_workers": 13,
            "verified_passing_case_count": 22798,
            "exact_observed_semantic_mismatch_count": 224,
            "complete_mismatch_chunk_count": 9,
            "mismatches_by_suite": {
                "original_bounded_v5": 2,
                "public_types_v1": 144,
                "public_surface_v19": 78,
            },
            "all_observed_semantic_mismatch_records_preserved": True,
            "compressed_archive_opened_in_source_mode": False,
        }
        base["final_first_party_dual_source_correction"] = {
            "owners": [owner_record(owner) for owner in FINAL_REPAIR],
            "actual_application_receipt": owner_record(FINAL_APPLICATION),
            "corrected_native_source_sha256": CORRECTED_NATIVE_SOURCE_SHA256,
            "corrected_native_source_bytes": CORRECTED_NATIVE_SOURCE_BYTES,
            "corrected_adapter_sha256": CORRECTED_ADAPTER_SHA256,
            "corrected_adapter_bytes": CORRECTED_ADAPTER_BYTES,
            "exact_previous_observed_mismatches_targeted": 224,
            "candidate_matching": "NOT RUN",
        }
        base["historical_actual_c23_dual_build"] = {
            "owners": [owner_record(owner) for owner in HISTORICAL_C23],
            "actual_publication_receipt": owner_record(HISTORICAL_C23_PUBLIC),
            "actual_root_receipt": owner_record(HISTORICAL_C23_ROOT),
            "candidate_matching": "NOT RUN",
            "private_root_opened_in_source_mode": False,
        }
        base["superseded_c13_before_actual_execution"] = {
            "owners": [owner_record(owner) for owner in SUPERSEDED_C13],
            "complete_contract_field_count": len(superseded_c13),
            "actual_candidate_run": "NOT RUN",
            "superseded_reason":
                "AUTHENTICATED C24 FAMILY SOURCE-IDENTITY MIGRATION REQUIRED",
            "candidate_correctness": "NOT MEASURED",
            "canonical_candidate_sources_modified": False,
        }
        base["actual_published_dual_c24_source_build"] = {
            "owners": [owner_record(owner) for owner in C24_BUILD],
            "publication_receipt": owner_record(C24_PUBLIC_RECEIPT),
            "root_provenance_receipt": owner_record(C24_ROOT_RECEIPT),
            "build_status": "PASS", "actual_compiler_process_count": 14,
            "independent_source_phase_count": 2,
            "distinct_phase_source_owner_count": 4,
            "distinct_native_artifact_count": 2,
            "native_artifact_sha256": C24_NATIVE_SHA256,
            "native_artifact_bytes": C24_NATIVE_BYTES,
            "corrected_native_source_sha256": CORRECTED_NATIVE_SOURCE_SHA256,
            "corrected_native_source_bytes": CORRECTED_NATIVE_SOURCE_BYTES,
            "corrected_adapter_source_sha256": CORRECTED_ADAPTER_SHA256,
            "corrected_adapter_source_bytes": CORRECTED_ADAPTER_BYTES,
            "private_root_path": C24_ROOT_PATH,
            "private_root_device": C24_ROOT_DEVICE,
            "private_root_inode": C24_ROOT_INODE,
            "private_root_opened_in_source_mode": False,
            "phase_native_and_source_owners": list(c24["phases"]),
        }
        base["strict_runtime_guard_v4"] = {
            "version": 4, "owners": [owner_record(owner) for owner in V4_GUARD],
            "candidate_guard_installations_in_source_mode": 0,
            "runtime_non_delegation": "NOT ESTABLISHED",
        }
        base["crash_journaled_dual_canonical_activation"] = {
            "canonical_adapter_relative": ADAPTER_TARGET_RELATIVE,
            "canonical_native_relative":
                "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
            "original_adapter_sha256": ORIGINAL_ADAPTER_SHA256,
            "original_adapter_bytes": ORIGINAL_ADAPTER_BYTES,
            "corrected_adapter_sha256": CORRECTED_ADAPTER_SHA256,
            "corrected_adapter_bytes": CORRECTED_ADAPTER_BYTES,
            "corrected_native_sha256": C24_NATIVE_SHA256,
            "corrected_native_bytes": C24_NATIVE_BYTES,
            "adapter_backup_name": ADAPTER_BACKUP_NAME,
            "adapter_stage_name": ADAPTER_STAGE_NAME,
            "adapter_journal_name": ADAPTER_JOURNAL_NAME,
            "durable_journal_before_first_mutation": True,
            "same_directory_original_inode_hard_links": True,
            "same_device_exclusive_owner_only_stage": True,
            "atomic_promotions": True,
            "exact_original_adapter_inode_restored": "NOT RUN",
            "exact_original_native_inode_restored": "NOT RUN",
            "publication_after_exact_dual_restoration_only": True,
        }
        base["lossless_original_public_case_evidence_v16"] = {
            "status": "SOURCE FROZEN; NO ORIGINAL CASE EXECUTED",
            "source_method_count": SOURCE_METHOD_COUNT,
            "public_record_count": PUBLIC_RECORD_COUNT,
            "case_execution_denominator": EXECUTED_CASE_COUNT,
            "authentic_debug_skip_count": DEBUG_SKIP_COUNT,
            "authentic_debug_skip": SKIPPED_TEST,
            "named_private_waiver_count": len(PRIVATE_WAIVER_NAMES),
            "named_private_waivers": list(PRIVATE_WAIVER_NAMES),
            "original_matrix_sha256": MATRIX_SHA256,
            "original_reference_records_sha256": REFERENCE_SHA256,
            "original_producer": owner_record(V5[0]),
            "original_producer_contract": owner_record(V5[2]),
            "original_harness": owner_record(ORIGINAL_HARNESS),
            "original_evaluator": owner_record(ORIGINAL_EVALUATOR),
            "upstream_original": dict(v5["original_upstream"]),
            "candidate_vector_schema":
            SCHEMA + "-lossless-original-public-case-vector",
            "candidate_case_codec": "PURE FIRST-PARTY C11 BOUNDED LZ1",
            "complete_candidate_records_required": True,
            "all_complete_case_chunks_digest_bound": True,
            "prefix_only_or_digest_only": False,
            "candidate_failure_tracebacks_preserved": True,
            "actual_candidate_digest_forced_to_reference": False,
            "normalization_before_original_comparison": False,
            "frozen_original_or_reference_source_mutations": 0,
            "actual_candidate_workers": 0,
            "actual_reference_workers": 0,
            "actual_candidate_records": 0,
            "historical_archives_opened": 0,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
        }
        base["source_wall"]["owner_count"] = len(old.STATIC_OWNERS)
        base["current_hidden_proposal"] = {
            "version": 3,
            "public_proposed_case_count": 226492416,
            "status": "PUBLIC DESIGN; UNFROZEN; NO CASES GENERATED",
            "planned_v4_case_count": 55296,
            "planned_v4_status": "PLANNED ONLY; NOT FROZEN",
            "holdout": FINAL_HOLDOUT_STATUS,
            "source_only_holdout_cases_opened": 0,
        }
        return base

    def controls(previous: types.ModuleType, wall: object,
                 old: types.ModuleType) -> list:
        answers = historical_controls(previous, wall, old)
        producer = old.load_producer(old.read_owner(old.PRODUCER[0]))
        answers.extend(original_case_hostile_controls(
            producer, history, campaign,
        ))
        answers.extend(dual_publisher_hostile_controls(configure))

        def reject(label: str, function: object) -> None:
            rejected = False
            try:
                function()
            except Exception:
                rejected = True
            need(rejected, "accept a forbidden original C12 operation: " + label)
            answers.append(label)

        for path in (
            ROOT + "/candidates/vm_candidate.py",
            ROOT + "/candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
            ROOT + "/oracle/phase2/evidence/repaired-c-original-campaign-v11-c-"
            "phase2-v21-c-original-match-semantics-original-p0-v11-failures.json.gz",
            ROOT + "/oracle/phase3/expanded-sealed-holdout-v1.json",
            "/tmp/rebar-phase2-repaired-c-original-campaign-v16",
        ):
            reject("physically deny C12 " + path.rsplit("/", 1)[-1],
                   lambda target=path: os.open(
                       target, os.O_RDONLY
                       | getattr(os, "O_CLOEXEC", 0)
                       | getattr(os, "O_NOFOLLOW", 0),
                   ))
        need(len(answers) >= 155
             and "re" not in sys.modules and "_sre" not in sys.modules
             and "ctypes" not in sys.modules
             and not any(name == "candidates"
                         or name.startswith("candidates.")
                         for name in sys.modules),
             "preserve all historical hostile controls and zero matcher effects")
        return answers

    module.configure_previous = configure
    module.contract_document = contract_document
    module.source_controls = controls


def bootstrap_v11() -> tuple[types.ModuleType, dict]:
    clean_runtime()
    raw = exact_owner(C11[0])
    tree = ast.parse(raw.decode("utf-8", "strict"),
                     filename=ROOT + "/" + C11[0][0])
    change = ExactV11ToV16()
    corrected = ast.fix_missing_locations(change.visit(tree))

    class ExactC24ObserverOwner(ast.NodeTransformer):
        def __init__(self) -> None:
            self.matches = 0

        def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
            if node.name != "require_selected_guarded_c":
                return node
            old = (
                "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2"
            )

            class ExactOwner(ast.NodeTransformer):
                def __init__(self, outer: ExactC24ObserverOwner) -> None:
                    self.outer = outer

                def visit_Constant(self, item: ast.Constant) -> ast.AST:
                    if type(item.value) is str and item.value == old:
                        self.outer.matches += 1
                        return ast.copy_location(
                            ast.Constant(CORRECTED_NATIVE_SOURCE_SHA256), item,
                        )
                    return item

            return ExactOwner(self).visit(node)

    source_owner_migration = ExactC24ObserverOwner()
    corrected = ast.fix_missing_locations(
        source_owner_migration.visit(corrected),
    )
    need(all(count >= 1 for count in change.identities.values())
         and change.worker_definitions == 1
         and change.vector_assignments == 1
         and change.denominator_guards == 1
         and change.complete_flag_assignments == 1
         and change.truncation_flag_assignments == 1
         and change.decoded_return_guards == 1
         and change.install_extensions == 1
         and change.inner_version_assignments == 1
         and change.transformer_version_assignments == 1
         and change.receipt_version_fields == 1
         and change.contract_version_checks == 1
         and change.receipt_extensions == 1
         and source_owner_migration.matches == 1,
         "reject a broadened, omitted, or partial whole-source C11 repair")
    campaign = types.ModuleType("_rebar_owned_c_v16_authenticated_complete_v11")
    campaign.__file__ = ROOT + "/" + SOURCE
    campaign.__package__ = ""
    campaign.__dict__.update({
        "_c12_previous_failure_receipt_sha256": C11_RECEIPT[1],
        "_c12_encode_candidate_records":
        lambda records, observed, producer, history, suite:
        encode_candidate_records(
            records, observed, producer, history, suite, campaign,
        ),
        "_c12_validate_candidate_record_counts":
        lambda observed, records, suite, producer, history:
        validate_candidate_record_counts(
            observed, records, suite, producer, history, campaign,
        ),
        "_c12_complete_records_preserved": complete_records_preserved,
        "_c12_record_prefix_truncated": record_prefix_truncated,
        "_c12_validate_decoded_original":
        lambda decoded, suite, producer, history:
        validate_decoded_original(
            decoded, suite, producer, history, campaign,
        ),
        "_c12_install_v16": install_v16,
    })
    exec(compile(corrected, campaign.__file__, "exec", dont_inherit=True),
         campaign.__dict__)
    need(campaign.SOURCE == SOURCE
         and campaign.PROTOCOL == PROTOCOL
         and campaign.CONTRACT == CONTRACT
         and campaign.SCHEMA == SCHEMA
         and campaign.LABEL == LABEL
         and campaign.C9[0][1]
         == "4796ba3c5e03a1341aa35f700679107a8bf835f0ebf582b02be59955ae211563"
         and campaign.V3[0][1] == V3[0][1]
         and callable(campaign.main)
         and callable(campaign.install_v11)
         and callable(campaign.encode_complete_c_mismatches)
         and callable(campaign.validate_complete_c_mismatches),
         "reject an incomplete authentic C11 original controller or first-party codec")
    clean_runtime()
    return campaign, {
        "historical_complete_source": owner_record(C11[0]),
        "exact_identity_replacements": dict(change.identities),
        "exact_original_worker_definition_count": change.worker_definitions,
        "exact_original_case_vector_encoder_count": change.vector_assignments,
        "exact_original_case_denominator_guard_count":
        change.denominator_guards,
        "exact_original_case_full_preservation_flag_count":
        change.complete_flag_assignments,
        "exact_original_case_truncation_flag_count":
        change.truncation_flag_assignments,
        "exact_decoded_original_case_validator_count":
        change.decoded_return_guards,
        "exact_historical_installer_extension_count":
        change.install_extensions,
        "exact_inner_version_assignments": change.inner_version_assignments,
        "exact_transformer_version_assignments":
        change.transformer_version_assignments,
        "exact_receipt_version_fields": change.receipt_version_fields,
        "exact_contract_version_checks": change.contract_version_checks,
        "exact_complete_case_receipt_extensions": change.receipt_extensions,
        "exact_c24_observer_source_owner_constant_migrations":
            source_owner_migration.matches,
        "frozen_original_source_modifications": 0,
        "frozen_reference_source_modifications": 0,
        "frozen_guard_v3_source_modifications": 0,
        "frozen_producer_v5_source_modifications": 0,
        "candidate_source_modifications": 0,
        "candidate_imports": 0,
        "candidate_workers": 0,
        "reference_workers": 0,
        "private_roots_opened": 0,
        "archives_opened": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }


def main(arguments: list[str]) -> int:
    campaign, transform = bootstrap_v11()
    campaign._c12_transform = transform
    original_install = campaign._c12_install_v16

    def install_with_provenance(historical: types.ModuleType,
                                history: types.ModuleType,
                                module: types.ModuleType,
                                _prior_transform: dict) -> None:
        original_install(campaign, history, module, transform)

    campaign._c12_install_v16 = install_with_provenance
    return campaign.main(arguments)


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as error:
        os.write(2, (
            "C21 original campaign V16: "
            + type(error).__qualname__ + ": " + str(error) + "\n"
        ).encode("utf-8", "backslashreplace"))
        raise SystemExit(2)
