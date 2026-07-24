#!/usr/bin/env python3
"""Freeze and replay an independently qualified public Python regex comparison.

This additive version preserves all 8,192 version-six public cases and their
weights.  Planning never imports an engine, starts a worker, opens the final
holdout, reads previous timing results, or performs a timing.  The three
measured implementations must have current, independently validated proofs.
"""

from __future__ import annotations

import collections
import copy
import hashlib
import importlib
import json
import os
import subprocess
import sys
import time
import types
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Mapping
from unittest import mock

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import postfinal_public_practice_v6 as predecessor


frozen_v4 = predecessor.frozen_v4
frozen_v5 = predecessor.frozen_v5
ROOT = frozen_v4.ROOT
SOURCE_PATH = Path(__file__).resolve()

# Capture the original implementation before applying this version's globals.
_ORIGINAL_MAKE_MANIFEST = predecessor._FROZEN_V4_MAKE_MANIFEST
_ORIGINAL_SELF_TEST = predecessor._FROZEN_V4_SELF_TEST
_ORIGINAL_VERIFIED_AUDIT = predecessor._FROZEN_V4_VERIFIED_AUDIT
_ORIGINAL_MEASURE = predecessor._FROZEN_V4_MEASURE
_ORIGINAL_VERIFY = predecessor._FROZEN_V4_VERIFY

VERSION = "postfinal-public-practice-v7"
VERSION_ROOT = ROOT / "performance" / "postfinal-public-v7"
EVIDENCE_ROOT = VERSION_ROOT / "evidence"
MANIFEST_PATH = VERSION_ROOT / "manifest.json"
RAW_PATH = EVIDENCE_ROOT / f"{VERSION}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE_ROOT / f"{VERSION}-summary.json"
INTEGRITY_PATH = EVIDENCE_ROOT / f"{VERSION}-integrity.json"
POSTFINAL_PLAN_SCHEMA = "rebar-postfinal-public-practice-plan-v7"
POSTFINAL_REPORT_SCHEMA = "rebar-postfinal-public-practice-report-v7"
POSTFINAL_INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v7"
EXCLUSIVE_SLOT = VERSION

GOAL_PATH = ROOT / "GOAL.md"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"

FROZEN_V6_SOURCE_PATH = ROOT / "tools" / "postfinal_public_practice_v6.py"
FROZEN_V6_SOURCE_SHA256 = "16a56d1573526894733b6284204ff3712b4d4e2a9c63027d51b8de1869df3fc3"
FROZEN_V6_MANIFEST_PATH = ROOT / "performance" / "postfinal-public-v6" / "manifest.json"
FROZEN_V6_MANIFEST_SHA256 = "65e024a1a79d13b03e4e5ad0f3d4ae010dbb6e4f09b52a8542837a2ea4c6198a"
FROZEN_V6_PROTOCOL_PATH = ROOT / "performance" / "postfinal-public-v6" / "PROTOCOL.md"
FROZEN_V6_PROTOCOL_SHA256 = "166f9c65eae008426c2d84e64240f6ddf667412d047f643726b7a377337e52c2"

BASE_AUDIT_SOURCE_PATH = ROOT / "tools" / "postfinal_from_scratch_audit_v5.py"
BASE_AUDIT_SOURCE_SHA256 = "100520ae06c3a837b3fa4ca508099ceb6e11efda8f63bcc0234b544071d17843"
BASE_AUDIT_PATH = ROOT / "candidates" / "audits" / "POSTFINAL-FROM-SCRATCH-AUDIT-V5.json"
BASE_AUDIT_SHA256 = "42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198"
BASE_AUDIT_SCHEMA = "rebar-postfinal-from-scratch-audit-v5"
BASE_AUDIT_WRAPPER_CONTROL_COUNT = 198

STRICT_AUDIT_SOURCE_PATH = ROOT / "tools" / "postfinal_no_delegation_audit_v5.py"
STRICT_AUDIT_SOURCE_SHA256: str | None = (
    "18a04023659e386780d6e9cd6b90065553254c18f2fe54ae78c37acbc468a7b6"
)
STRICT_AUDIT_PATH = ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V5.json"
STRICT_AUDIT_SHA256: str | None = (
    "50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb"
)
STRICT_AUDIT_SCHEMA = "rebar-postfinal-no-delegation-audit-v5"
STRICT_AUDIT_CONTROL_COUNT = 32
STRICT_AUDIT_WRAPPER_CONTROL_COUNT = 676
PREVIOUS_V3_STRICT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v3.py"
PREVIOUS_V3_STRICT_SOURCE_SHA256 = (
    "80d2450439893e1d6e1e2d1986cc59cc7da20e4d4c871f6670b31587da0f24f5"
)
PREVIOUS_V3_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V3.json"
)
PREVIOUS_V3_STRICT_REPORT_SHA256 = (
    "51f745b0cf4a1a91457d865b8fac26b71534f801ca6632b2fd762bd6933c6ab5"
)
PREVIOUS_V4_STRICT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v4.py"
PREVIOUS_V4_STRICT_SOURCE_SHA256 = (
    "f4587015e8ab90a3bab3cc5a8874aabe3664da4c69445c0845a6672960209658"
)
PREVIOUS_V4_BASE_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V4.json"
)
PREVIOUS_V4_BASE_REPORT_SHA256 = (
    "5677065d42ba0c4f135182cb681533181e57de823a367fdd54fde3d90120f87a"
)

IMMUTABLE_WORKER_SOURCE_PATH = ROOT / "tools" / "postfinal_no_delegation_audit_v1.py"
IMMUTABLE_WORKER_SOURCE_SHA256 = "e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed"
IMMUTABLE_WORKER_REPORT_PATH = ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
IMMUTABLE_WORKER_REPORT_SHA256 = "c4605c8af5da805c099b1efb7f15e8390781768bb3014276b465a7712b4ed06b"
IMMUTABLE_WORKER_SCHEMA = "rebar-postfinal-no-delegation-audit-v1"

UNIVERSAL_SOURCE_PATH = ROOT / "tools" / "python_re_universal_public_oracle_stage06.py"
UNIVERSAL_SOURCE_SHA256 = "ff365f1d867f4873146aaf6f77fa2f360b197bbccfb9dd06239bdcf4b776e7f2"
UNIVERSAL_REPORT_PATH = (
    ROOT / "candidates" / "evidence" / "python-re-universal-public-oracle-v6-all.json"
)
UNIVERSAL_REPORT_SHA256: str | None = (
    "bf4f7cc82c876ee54e55c0971c65db209f6fdf0c8b00baa8c57fbc5f460b1528"
)
UNIVERSAL_CASE_SHA256 = "8e5c120a4e637c30940363e20d6042324d65d9f7d03fbd35240ffabf2df282ae"

STAGE10_SOURCE_PATH = ROOT / "tools" / "python_re_universal_public_oracle_stage10.py"
STAGE10_SOURCE_SHA256 = (
    "a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08"
)
STAGE10_PROTOCOL_PATH = (
    ROOT / "oracle" / "cpython-3.14.6" / "PUBLIC-CONTRACT-V10.md"
)
STAGE10_PROTOCOL_SHA256 = (
    "c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543"
)
STAGE10_SCHEMA = "rebar-python-re-public-contract-v10"
STAGE10_SELF_ORACLE_SCHEMA = STAGE10_SCHEMA + "-self-oracle"
STAGE10_ALL_CANDIDATE_SCHEMA = STAGE10_SCHEMA + "-all-candidates"
STAGE10_METADATA_SCHEMA = STAGE10_SCHEMA + "-isolated-public-metadata"
STAGE10_SELF_ORACLE_PATH = (
    ROOT
    / "oracle"
    / "cpython-3.14.6"
    / "evidence"
    / "public-contract-v10-self-oracle.json"
)
STAGE10_SELF_ORACLE_SHA256 = (
    "5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9"
)
STAGE10_ALL_CANDIDATE_PATH = (
    ROOT
    / "candidates"
    / "evidence"
    / "python-re-universal-public-oracle-v10-all.json"
)
STAGE10_ALL_CANDIDATE_SHA256 = (
    "0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7"
)
STAGE10_MATRIX_SHA256 = (
    "0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db"
)
STAGE10_REFERENCE_RECORD_SHA256 = (
    "0d6a74b1f923436c14569bfdd84431e4251f3bb8dd3129fbbcaf82a47f906b94"
)
STAGE10_METADATA_RECORD_SHA256 = (
    "41dde3a1364426a1d4d9fe34136e987fce29afd54a0eaf2cdea4d2032a6cac65"
)
STAGE10_OBSERVATION_DOMAIN = "rebar/python-re/public-contract/v10"
STAGE10_SEED = 2026072437
STAGE10_SEED_DOMAIN = "rebar/python-re/public-contract/v7"
STAGE10_CASES = 3_584
STAGE10_COHORT_COUNTS = {
    "public-surface": 256,
    "invalid-grammar": 256,
    "real-locale": 1_024,
    "buffer-lifetime": 256,
    "object-contract": 256,
    "callback-scanner": 256,
    "shared-pattern-threads": 256,
    "bounded-unicode": 1_024,
}
STAGE10_BLOCKED_NATIVE_LOADER_ALIASES = (
    "ctypes.CDLL",
    "ctypes.cdll.LoadLibrary",
    "ctypes.cdll._dlltype",
    "ctypes._dlopen",
    "_ctypes.dlopen",
)

PRESERVED_STAGE07_SOURCE_PATH = (
    ROOT / "tools" / "python_re_universal_public_oracle_stage07.py"
)
PRESERVED_STAGE07_SOURCE_SHA256 = (
    "150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25"
)
PRESERVED_STAGE07_PROTOCOL_PATH = (
    ROOT / "oracle" / "cpython-3.14.6" / "PUBLIC-CONTRACT-V7.md"
)
PRESERVED_STAGE07_PROTOCOL_SHA256 = (
    "b4d719609179dde5f582695393539e7a320c09438e4bc635ca843627ac9d7524"
)
PRESERVED_STAGE07_FAILURE_PATH = (
    ROOT
    / "oracle"
    / "cpython-3.14.6"
    / "evidence"
    / "public-contract-v7-self-oracle-failures.json"
)
PRESERVED_STAGE07_FAILURE_SHA256 = (
    "765e635745a7e332a1bd22426065c43fd52036d013add0d88d840d8fde1121e0"
)
PRESERVED_STAGE08_SOURCE_PATH = (
    ROOT / "tools" / "python_re_universal_public_oracle_stage08.py"
)
PRESERVED_STAGE08_SOURCE_SHA256 = (
    "10464ca347e6eab248a2887a6fd0625cff63497173024616ca8338af0801b0aa"
)
PRESERVED_STAGE08_PROTOCOL_PATH = (
    ROOT / "oracle" / "cpython-3.14.6" / "PUBLIC-CONTRACT-V8.md"
)
PRESERVED_STAGE08_PROTOCOL_SHA256 = (
    "502f300e8ffbd33cf3cbbf6fde7e9cb5e81ed3f87f83634f47068015cdd9dbdd"
)
PRESERVED_STAGE08_SELF_ORACLE_PATH = (
    ROOT
    / "oracle"
    / "cpython-3.14.6"
    / "evidence"
    / "public-contract-v8-self-oracle.json"
)
PRESERVED_STAGE08_SELF_ORACLE_SHA256 = (
    "efcf0f661363e9032ce8c0afe7ea06a4762b783eec4c4ee6ec7c7059c14994df"
)
PRESERVED_STAGE08_RUST_FAILURE_PATH = (
    ROOT
    / "candidates"
    / "evidence"
    / "python-re-universal-public-oracle-v8-rust-failures.json"
)
PRESERVED_STAGE08_RUST_FAILURE_SHA256 = (
    "f509cedf5f58d1c211b63177fb843bfba3dc0b132469a392df43a9c802e323b1"
)

# Bind only the genuine, current-source qualification for CPython and all
# three engines.  In particular, a previous 144-test campaign can never
# authorize freezing this prospective public comparison.
OFFICIAL_LOCALE_REPORT_PATH = (
    ROOT
    / "oracle"
    / "cpython-3.14.6"
    / "evidence"
    / "postfinal-locale-v1-all.json"
)
OFFICIAL_LOCALE_REPORT_SHA256: str | None = (
    "bc17ee74409543d1b57f3aee65088e990ab21ac83dc75ac46fbd1f97f04b6621"
)
OFFICIAL_LOCALE_SCHEMA = "rebar-postfinal-cpython-public-locale-v1"
OFFICIAL_LOCALE_TESTS = 146
OFFICIAL_LOCALE_SOURCE_PATH = ROOT / "tools" / "postfinal_cpython_locale_oracle_v1.py"
OFFICIAL_LOCALE_SOURCE_SHA256: str | None = (
    "b87bbdcddef2d19a462e8c4b37bd159f6c3a30ea9b4fe5d9471eff1f51fbcb55"
)
ORIGINAL_OFFICIAL_MANIFEST_RELATIVE = "oracle/cpython-3.14.6/manifest.json"
ORIGINAL_OFFICIAL_RUNNER_RELATIVE = "tools/cpython_re_oracle.py"
ORIGINAL_OFFICIAL_MANIFEST_SHA256 = (
    "2c89ce37e474cb6f59d61f86ad810662b50b83bbdce3610c04523fe092688597"
)
ORIGINAL_OFFICIAL_RUNNER_SHA256 = (
    "d5084fd43352f34267f3ed9b4b5d60a6070e2c50d4b787739270502c856e18bb"
)
ORIGINAL_OFFICIAL_TEST_SOURCE_SHA256 = (
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2"
)
ORIGINAL_OFFICIAL_SELECTED_METHOD_SHA256 = (
    "d33571d09a3a9cb428a84dece5af233e66267b831d3043c90e3ad77cb8de5178"
)
ORIGINAL_OFFICIAL_SOURCE_HASHES = {
    "LICENSE": "b0e25a78cffb43f4d92de8b61ccfa1f1f98ecbc22330b54b5251e7b6ba010231",
    "re_tests.py": "ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab",
    "test_re.py": ORIGINAL_OFFICIAL_TEST_SOURCE_SHA256,
}
ORIGINAL_OFFICIAL_PRIVATE_METHOD_WAIVERS = {
    "ReTests.test_re_groupref_overflow": (
        "PRIVATE-CONSTANTS: imports re._constants.MAXGROUPS"
    ),
    "ReTests.test_large_search": (
        "RESOURCE-BIGMEM: requires a multi-gigabyte test resource"
    ),
    "ReTests.test_large_subn": (
        "RESOURCE-BIGMEM: requires a multi-gigabyte test resource"
    ),
    "ReTests.test_search_anchor_at_beginning": (
        "PERFORMANCE-ASSERTION: timing threshold belongs in the frozen performance oracle"
    ),
    "ReTests.test_regression_gh94675": (
        "ENV-MULTIPROCESSING: sandbox cannot create the required forkserver socket"
    ),
    "ReTests.test_memory_leaks": (
        "PRIVATE-DEBUG-HOOK: requires Pattern._fail_after from a debug CPython build"
    ),
}
ORIGINAL_OFFICIAL_PRIVATE_CLASS_WAIVERS = {
    "DebugTests": (
        "PRIVATE-DEBUG-TEXT: stdlib opcode/debug text is not a public contract"
    ),
    "ImplementationTest": (
        "PRIVATE-INTERNAL-COMPILER: checks re._compiler, _sre, and deprecated internal modules"
    ),
}

CAMPAIGN_CONTROLLER_SCHEMA = (
    "rebar-v8-multi-candidate-sealed-campaign-postfinal-v5"
)
RUST_CAMPAIGN_CONTROLLER_PATH = (
    ROOT / "tools" / "rust_v8_multi_candidate_campaign_postfinal_v5.py"
)
RUST_CAMPAIGN_CONTROLLER_SHA256 = (
    "50a39f8338b176b9376cac1437a7c0aaeb343594af0ebfea797a7beea04e86d9"
)
CAMPAIGN_ANCESTOR_PATH = (
    ROOT / "tools" / "rust_v8_multi_candidate_campaign_postfinal_v4.py"
)
CAMPAIGN_ANCESTOR_SHA256 = (
    "67a7555976ab60c371c9aad1b7f94c112bd1c6aaf990e39c02f4484f3010e799"
)
CAMPAIGN_COMPLETE_PRODUCTION_ROLE_COUNTS = {"rust": 5, "vm": 3, "zig": 5}
RUST_CAMPAIGN_PATH = (
    ROOT
    / "candidates"
    / "evidence"
    / "rust-v8-rust-postfinal-locale-v5-sealed-campaign.json"
)
VM_CAMPAIGN_PATH = (
    ROOT
    / "candidates"
    / "evidence"
    / "rust-v8-vm-postfinal-locale-v5-sealed-campaign.json"
)
ZIG_CAMPAIGN_PATH = (
    ROOT
    / "candidates"
    / "evidence"
    / "rust-v8-zig-postfinal-locale-v5-sealed-campaign.json"
)
# A genuine report digest is set only after the exact, candidate-specific V5
# campaign actually passes.  None is intentionally not a SHA-256 digest, so
# every real proof and freeze fails closed until all three reports exist.
RUST_CAMPAIGN_SHA256: str | None = (
    "bdc10bbdf1f6a7711283826b04c1fe7f4ab700a7cf97d4c8f0595d20cab80024"
)
VM_CAMPAIGN_SHA256: str | None = (
    "3156b02d4dd428b82c6c3947b620fa046330234b1ce0fd66058dff4a3d0c6d16"
)
ZIG_CAMPAIGN_SHA256: str | None = (
    "e9a096349fd3b3cd9c91464b6033880ef9f2d30dece18e04d0c2a79efc6812cf"
)
REJECTED_RUST_CAMPAIGN_PATH = ROOT / "candidates" / "evidence" / "rust-v8-rust-postfinal-assertion-snapshot-v1-sealed-campaign.json"
REJECTED_RUST_CAMPAIGN_SHA256 = "9e744de16c6c627715303bcf27ae9ef628b04fcdc078e3ebe9e936204b719db2"
REJECTED_ARCHIVED_RUST_V4_CAMPAIGN_SHA256 = (
    "0311663e7e7c501d660f2dab8a8cd877795c35cfe507c65f7f92d9f0913d4540"
)

RUST_SOURCE_SHA256 = "3a2ab20885daea11bbc90cb9707a154174742f836e818521c1d00e2a0afd0b64"
EXPECTED_NATIVE_FINGERPRINTS = {
    "candidates.rust_candidate:native-bridge": "81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36",
    "candidates.rust_candidate:native-engine": "d590300720215718782227dd8da1192047b4781bdb41ed94446cac06ba880e84",
    "candidates.vm_candidate:native-engine": "af702483ebecb4164d1a059922ce7a909d192bdd42c60474bf0c81e6d49764aa",
    "candidates.zig_candidate:native-bridge": "32dadc46281d13df784693f0785d4d149e6d3cd000aa3de6eb220a4a9ed50c9c",
    "candidates.zig_candidate:native-engine": "f658b2325642b38e8303d94c6bdc42e74ba8b1f021af76e80f0c8936aa10f81a",
}
EXPECTED_SOURCE_FINGERPRINTS = {
    "candidates/rust/py_bridge.c": "3d432d8f53a75eb2c3c75d118c811ac7ba12c432d987422223d55773fbb36abe",
    "candidates/rust/src/lib.rs": RUST_SOURCE_SHA256,
    "candidates/rust/src/newline.rs": "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b",
    "candidates/rust/src/search.rs": "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe",
    "candidates/rust/src/stack.rs": "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e",
    "candidates/rust/src/unicode_tables.rs": "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af",
    "candidates/rust_candidate.py": "ed210957f3fc7a8d87ce38cfc775cd380bed19dcde7e8acd23d09197abb60048",
    "candidates/_vm_native.c": "3684b0cd45b149edf14aad50704b35dedf74bde65f238ab3be151193aeef2d6f",
    "candidates/vm_candidate.py": "ef00948bb6138342501fbfef4070900ce1b4a57ecf9d805fc897fedcb36978d0",
    "candidates/zig/mini_regex.zig": "539bf5d378e0c2845c01519fcce62f1ef5e68610f477912c44a03027fb67a346",
    "candidates/zig/py_bridge.c": "17d8578bbc1e73db84aa59755bf3c8add2801066d238e506c0e6f16efa920568",
    "candidates/zig_candidate.py": "b7330484e8436adc91d1d0960745a54be94752eb7f7fc7fbf747ddfa3cb80d6b",
}

FRESH_RUST_PROOF_PATHS = {
    "rust-edge": ROOT / "candidates" / "evidence" / "rust-v7-edge-oracle-rust-postfinal-locale-v1.json.gz",
    "rust-deep-public-contract": ROOT / "candidates" / "audits" / "RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-LOCALE-V1.json.gz",
    "rust-observability": ROOT / "candidates" / "evidence" / "rust-v8-observability-rust-qualified-postfinal-locale-v1.json.gz",
    "rust-complete-correctness-campaign": RUST_CAMPAIGN_PATH,
}
FRESH_PEER_PROOF_PATHS = {
    "vm-edge": (
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v7-edge-oracle-vm-postfinal-locale-v1.json.gz"
    ),
    "vm-deep-public-contract": (
        ROOT
        / "candidates"
        / "audits"
        / "RUST-V8-DEEP-CONTRACT-C-POSTFINAL-LOCALE-V1.json.gz"
    ),
    "vm-observability": (
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v8-observability-vm-qualified-postfinal-locale-v1.json.gz"
    ),
    "vm-complete-correctness-campaign": VM_CAMPAIGN_PATH,
    "zig-edge": (
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v7-edge-oracle-zig-postfinal-locale-v1.json.gz"
    ),
    "zig-deep-public-contract": (
        ROOT
        / "candidates"
        / "audits"
        / "RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-LOCALE-V1.json.gz"
    ),
    "zig-observability": (
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v8-observability-zig-qualified-postfinal-locale-v1.json.gz"
    ),
    "zig-complete-correctness-campaign": ZIG_CAMPAIGN_PATH,
}
PROOF_SHA256: dict[str, str | None] = {
    "rust-edge": "8569275c5b705870bde368ee20981be1a90c07675b12fe53b64f19c7e765b408",
    "rust-deep-public-contract": "ca437ae8e2dc46f4d0b8e259f304a402efc6f0817dfe89600d92728a86c2ce9f",
    "rust-observability": "db139cf63dfe6605120a9e36db16b749f060fc31961fe6215397623b454929fa",
    "rust-complete-correctness-campaign": RUST_CAMPAIGN_SHA256,
    "vm-edge": "0c07fdbf8848f4236735c97bbda4969c4de0ceb6e10c11fdac0c674d5efd303b",
    "vm-deep-public-contract": "9d8aa10cd07d4bee48b021f26fbb66e5d2f3293f6c1d8a0d1039a9087af932de",
    "vm-observability": "35c63238162f420c41a5b021641530344d91ddc036b15dac73705b3f144ee43b",
    "vm-complete-correctness-campaign": VM_CAMPAIGN_SHA256,
    "zig-edge": "8a8f76a85e2888dc0eb19e07c7343dd5c8caeab8745baf8a277f68beea1424a6",
    "zig-deep-public-contract": "f522ae69bea26792b8406254360809ae9cfddeb03cc012dc579f2397c7e8813d",
    "zig-observability": "43053dd764ee9b6c40ccfee72107b1e1ebe56e1081b951ec026c3ab8c124e15d",
    "zig-complete-correctness-campaign": ZIG_CAMPAIGN_SHA256,
}
EXPECTED_CAMPAIGN_STAGES = (
    "from-scratch-static-audit",
    "independent-source-no-delegation",
    "independent-owned-native-pipeline",
    "candidate-frozen-edge-proof",
    "candidate-frozen-deep-public-proof",
    "independent-native-boundary-self-oracle",
    "independent-native-boundary-integrity",
    "independent-native-boundary-poison",
    "independent-native-boundary-compatibility",
    "frozen-cross-family-observability",
    "frozen-correctness-v2",
    "frozen-correctness-v3",
    "official-cpython-tests",
    "upstream-public-surface",
    "candidate-public-surface",
    "unicode-group-name-errors",
    "replacement-and-callback-adversarial",
    "deep-replacement-and-callback-adversarial",
    "extended-cpython-paths",
    "isolated-crash-and-resource-safety",
    "isolated-depth-and-overflow-safety",
    "full-unicode-plane",
)


def _owned_relative(path: Path) -> str:
    """Validate a canonical lexical repository path without reading it."""

    frozen_v4.require(isinstance(path, Path), "the V7 evidence path is not a path")
    absolute = path.absolute()
    root = ROOT.absolute()
    frozen_v4.require(
        absolute.is_relative_to(root) and ".." not in absolute.relative_to(root).parts,
        "a public version-7 input escaped the owned repository",
    )
    return absolute.relative_to(root).as_posix()


def _require_pinned_file(path: Path, digest: str | None, label: str) -> None:
    frozen_v4.require(
        isinstance(digest, str)
        and frozen_v4.valid_sha256(digest)
        and path.is_file()
        and not path.is_symlink()
        and frozen_v4.pilot.file_sha256(path) == digest,
        f"the exact {label} is missing, substituted, or stale",
    )


def _make_mixed_proof_paths() -> tuple[tuple[str, Path], ...]:
    return tuple(
        (
            f"{family}-{suffix}",
            FRESH_RUST_PROOF_PATHS[f"{family}-{suffix}"]
            if family == "rust"
            else FRESH_PEER_PROOF_PATHS[f"{family}-{suffix}"],
        )
        for family in ("rust", "vm", "zig")
        for suffix in (
            "edge",
            "deep-public-contract",
            "observability",
            "complete-correctness-campaign",
        )
    )


MIXED_CORRECTNESS_PATHS = _make_mixed_proof_paths()
MIXED_EDGE_ORACLES = tuple(
    path for role, path in MIXED_CORRECTNESS_PATHS if role.endswith("-edge")
)


def _require_complete_campaign_pins() -> None:
    """Reject an incomplete or reused source-bound V5 family campaign."""

    expected = {
        "rust": (RUST_CAMPAIGN_PATH, RUST_CAMPAIGN_SHA256),
        "vm": (VM_CAMPAIGN_PATH, VM_CAMPAIGN_SHA256),
        "zig": (ZIG_CAMPAIGN_PATH, ZIG_CAMPAIGN_SHA256),
    }
    actual_paths = dict(MIXED_CORRECTNESS_PATHS)
    digests: list[str] = []
    for family, (path, digest) in expected.items():
        role = f"{family}-complete-correctness-campaign"
        frozen_v4.require(
            actual_paths.get(role) == path
            and isinstance(digest, str)
            and frozen_v4.valid_sha256(digest)
            and PROOF_SHA256.get(role) == digest
            and path.name
            == f"rust-v8-{family}-postfinal-locale-v5-sealed-campaign.json",
            f"the actual, separately source-bound V5 {family} campaign "
            "has not yet passed",
        )
        digests.append(digest)
    frozen_v4.require(
        len(set(digests)) == 3,
        "public V7 reused a sealed-campaign report for separate regex engines",
    )


def _validate_proof_contract(
    paths: tuple[tuple[str, Path], ...],
    edges: tuple[Path, ...],
    candidates: tuple[str, ...],
    deep_families: Mapping[str, str],
) -> None:
    expected_roles = tuple(role for role, _ in MIXED_CORRECTNESS_PATHS)
    frozen_v4.require(
        candidates == ("rust", "vm", "zig")
        and dict(deep_families) == {"rust": "RUST", "vm": "C", "zig": "ZIG"}
        and isinstance(paths, tuple)
        and len(paths) == 12
        and tuple(item[0] for item in paths) == expected_roles,
        "public V7 omitted, reordered, or substituted an independent proof family",
    )
    observed: list[str] = []
    for (role, path), (_, expected) in zip(
        paths, MIXED_CORRECTNESS_PATHS, strict=True
    ):
        frozen_v4.require(
            isinstance(path, Path)
            and _owned_relative(path) == _owned_relative(expected)
            and role in PROOF_SHA256,
            f"public V7 substituted the exact {role} correctness proof",
        )
        observed.append(_owned_relative(path))
    frozen_v4.require(
        len(set(observed)) == 12
        and isinstance(edges, tuple)
        and len(edges) == 3
        and all(isinstance(path, Path) for path in edges)
        and tuple(_owned_relative(path) for path in edges)
        == tuple(_owned_relative(path) for path in MIXED_EDGE_ORACLES),
        "public V7 duplicated a proof or omitted an independently qualified edge",
    )


def require_stage05_correctness_path_contract() -> None:
    _validate_proof_contract(
        frozen_v4.STAGE05_CORRECTNESS_PATHS,
        frozen_v4.DEFAULT_EDGE_ORACLES,
        frozen_v4.STAGE05_CANDIDATES,
        frozen_v4.STAGE05_DEEP_FAMILIES,
    )
    frozen_v4.require(
        frozen_v4.STAGE05_CANDIDATES == frozen_v4.UNIVERSAL_ORACLE_CANDIDATES,
        "the three independently tested Python regex families changed",
    )


def _validate_immutable_guarded_worker(
    provenance: Mapping[str, Any],
) -> None:
    frozen_v4.require(
        isinstance(provenance, Mapping)
        and provenance.get("postfinal_guarded_worker_source_path")
        == str(IMMUTABLE_WORKER_SOURCE_PATH.absolute())
        and provenance.get("postfinal_guarded_worker_source_sha256")
        == IMMUTABLE_WORKER_SOURCE_SHA256
        and provenance.get("postfinal_guarded_worker_schema")
        == IMMUTABLE_WORKER_SCHEMA
        and provenance.get("postfinal_guarded_worker_report_path")
        == str(IMMUTABLE_WORKER_REPORT_PATH.absolute())
        and provenance.get("postfinal_guarded_worker_report_sha256")
        == IMMUTABLE_WORKER_REPORT_SHA256,
        "the exact isolated immutable V1 guarded worker was substituted",
    )


def _validated_runtime_provenance(report: Mapping[str, Any]) -> dict[str, Any]:
    frozen_v4.require(
        isinstance(report, Mapping)
        and report.get("schema") == STRICT_AUDIT_SCHEMA
        and report.get("postfinal_schema") == STRICT_AUDIT_SCHEMA
        and report.get("status") == "PASS"
        and report.get("result") == "PASS"
        and report.get("passed") is True
        and report.get("audit_source_path") == _owned_relative(STRICT_AUDIT_SOURCE_PATH)
        and report.get("audit_source_sha256") == STRICT_AUDIT_SOURCE_SHA256
        and report.get("base_audit_report_path") == _owned_relative(BASE_AUDIT_PATH)
        and report.get("base_audit_report_sha256") == BASE_AUDIT_SHA256
        and report.get("base_audit_source_path") == _owned_relative(BASE_AUDIT_SOURCE_PATH)
        and report.get("base_audit_source_sha256") == BASE_AUDIT_SOURCE_SHA256
        and report.get("base_audit_postfinal_schema") == BASE_AUDIT_SCHEMA
        and report.get("inherited_control_count") == 76,
        "public V7 did not bind the passing current V5 source and isolation audits",
    )
    controls = report.get("self_test")
    inherited = report.get("inherited_self_test")
    wrapper = report.get("postfinal_wrapper_self_test")
    frozen_v4.require(
        isinstance(controls, Mapping)
        and controls.get("passed") is True
        and controls.get("check_count") == STRICT_AUDIT_CONTROL_COUNT
        and controls.get("failed") == []
        and isinstance(inherited, Mapping)
        and inherited.get("passed") is True
        and inherited.get("check_count") == 76
        and isinstance(wrapper, Mapping)
        and wrapper.get("schema") == STRICT_AUDIT_SCHEMA + "-self-test"
        and wrapper.get("status") == "PASS"
        and wrapper.get("passed") is True
        and wrapper.get("check_count") == STRICT_AUDIT_WRAPPER_CONTROL_COUNT
        and wrapper.get("failed") == []
        and wrapper.get("candidate_imported") is False,
        "the current V5 audit omitted its 676, 32, or 76 genuine poison controls",
    )
    frozen_v4.require(
        report.get("previous_v3_audit_source_path")
        == PREVIOUS_V3_STRICT_SOURCE_RELATIVE
        and report.get("previous_v3_audit_source_sha256")
        == PREVIOUS_V3_STRICT_SOURCE_SHA256
        and report.get("previous_v3_audit_report_path")
        == PREVIOUS_V3_STRICT_REPORT_RELATIVE
        and report.get("previous_v3_audit_report_sha256")
        == PREVIOUS_V3_STRICT_REPORT_SHA256
        and report.get("previous_v4_audit_source_path")
        == PREVIOUS_V4_STRICT_SOURCE_RELATIVE
        and report.get("previous_v4_audit_source_sha256")
        == PREVIOUS_V4_STRICT_SOURCE_SHA256
        and report.get("previous_v4_source_report_path")
        == PREVIOUS_V4_BASE_REPORT_RELATIVE
        and report.get("previous_v4_source_report_sha256")
        == PREVIOUS_V4_BASE_REPORT_SHA256
        and report.get("previous_v4_source_report_historical") is True
        and report.get("previous_v4_strict_report_created") is False
        and report.get("native_elf_fingerprints") == EXPECTED_NATIVE_FINGERPRINTS
        and report.get("qualified_source_fingerprints")
        == EXPECTED_SOURCE_FINGERPRINTS,
        "the source-bound V5 audit history or five independently owned engines changed",
    )
    scope = report.get("scope")
    frozen_v4.require(
        isinstance(scope, Mapping)
        and scope.get("persistent_measurement_worker_available") is True
        and scope.get("immutable_v1_source_preserved") is True
        and scope.get("immutable_v1_reports_mutated") is False
        and scope.get("immutable_v2_reports_mutated") is False
        and scope.get("immutable_v3_reports_mutated") is False
        and scope.get("immutable_v4_reports_mutated") is False
        and scope.get("base_v5_report_only") is True
        and scope.get("previous_v4_source_report_historical") is True
        and scope.get("closed_owned_source_graph") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("candidate_imports") == "isolated guarded subprocesses only"
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "public V7 weakened independently guarded, candidate-free worker isolation",
    )
    worker = {
        "postfinal_guarded_worker_source_path": str(IMMUTABLE_WORKER_SOURCE_PATH.absolute()),
        "postfinal_guarded_worker_source_sha256": IMMUTABLE_WORKER_SOURCE_SHA256,
        "postfinal_guarded_worker_schema": IMMUTABLE_WORKER_SCHEMA,
        "postfinal_guarded_worker_report_path": str(IMMUTABLE_WORKER_REPORT_PATH.absolute()),
        "postfinal_guarded_worker_report_sha256": IMMUTABLE_WORKER_REPORT_SHA256,
    }
    _validate_immutable_guarded_worker(worker)
    return worker


def verified_from_scratch_audit() -> tuple[
    str, dict[str, str], dict[str, str], dict[str, Any]
]:
    frozen_v4.require_candidate_free()
    for path, digest, label in (
        (BASE_AUDIT_SOURCE_PATH, BASE_AUDIT_SOURCE_SHA256, "V5 from-scratch verifier"),
        (BASE_AUDIT_PATH, BASE_AUDIT_SHA256, "V5 from-scratch report"),
        (STRICT_AUDIT_SOURCE_PATH, STRICT_AUDIT_SOURCE_SHA256, "V5 isolation verifier"),
        (STRICT_AUDIT_PATH, STRICT_AUDIT_SHA256, "V5 isolation report"),
        (IMMUTABLE_WORKER_SOURCE_PATH, IMMUTABLE_WORKER_SOURCE_SHA256, "immutable V1 worker"),
        (IMMUTABLE_WORKER_REPORT_PATH, IMMUTABLE_WORKER_REPORT_SHA256, "immutable V1 worker proof"),
    ):
        _require_pinned_file(path, digest, label)
    digest, sources, native, details = _ORIGINAL_VERIFIED_AUDIT()
    frozen_v4.require(
        digest == BASE_AUDIT_SHA256
        and native == EXPECTED_NATIVE_FINGERPRINTS
        and len(sources) == 12
        and details.get("postfinal_no_delegation_audit_sha256") == STRICT_AUDIT_SHA256
        and details.get("postfinal_no_delegation_audit_source_sha256")
        == STRICT_AUDIT_SOURCE_SHA256
        and details.get("postfinal_no_delegation_audit_schema") == STRICT_AUDIT_SCHEMA
        and details.get("postfinal_no_delegation_control_count") == 32,
        "the inherited V4 verifier rejected a current V5 source or native engine",
    )
    strict = frozen_v4.read_json(STRICT_AUDIT_PATH, "passing current V5 isolation audit")
    runtime = _validated_runtime_provenance(strict)
    base = frozen_v4.read_json(BASE_AUDIT_PATH, "passing current V5 from-scratch audit")
    frozen_v4.require(
        base.get("postfinal_schema") == BASE_AUDIT_SCHEMA
        and base.get("status") == "PASS"
        and base.get("passed") is True
        and base.get("audit_source_sha256") == BASE_AUDIT_SOURCE_SHA256
        and base.get("verified_distinct_pipeline_count") == 4
        and base.get("self_test", {}).get("check_count") == 76
        and base.get("postfinal_wrapper_self_test", {}).get("check_count")
        == BASE_AUDIT_WRAPPER_CONTROL_COUNT,
        "public V7 lost an independent current V5 audit or its 198 poison controls",
    )
    frozen_v4.require_candidate_free()
    return digest, sources, native, {**details, **runtime}


def load_guarded_worker_module(expected_source_sha256: str) -> types.ModuleType:
    frozen_v4.require_candidate_free()
    frozen_v4.require_pinned_python()
    frozen_v4.require(
        expected_source_sha256 == STRICT_AUDIT_SOURCE_SHA256,
        "public V7 substituted its current V5 guarded-worker verifier",
    )
    for path, digest, label in (
        (STRICT_AUDIT_SOURCE_PATH, STRICT_AUDIT_SOURCE_SHA256, "current V5 worker verifier"),
        (STRICT_AUDIT_PATH, STRICT_AUDIT_SHA256, "current V5 worker audit"),
        (IMMUTABLE_WORKER_SOURCE_PATH, IMMUTABLE_WORKER_SOURCE_SHA256, "immutable V1 worker"),
        (IMMUTABLE_WORKER_REPORT_PATH, IMMUTABLE_WORKER_REPORT_SHA256, "immutable V1 worker proof"),
    ):
        _require_pinned_file(path, digest, label)
    runtime = _validated_runtime_provenance(
        frozen_v4.read_json(STRICT_AUDIT_PATH, "current V5 guarded-worker audit")
    )
    _validate_immutable_guarded_worker(runtime)
    module = importlib.import_module("tools.postfinal_no_delegation_audit_v1")
    frozen_v4.require(
        Path(getattr(module, "__file__", "")).resolve()
        == IMMUTABLE_WORKER_SOURCE_PATH.resolve()
        and getattr(module, "SCHEMA", None) == IMMUTABLE_WORKER_SCHEMA
        and frozen_v4.pilot.file_sha256(Path(module.__file__).resolve())
        == IMMUTABLE_WORKER_SOURCE_SHA256
        and callable(getattr(module, "guarded_worker_command", None))
        and callable(getattr(module, "validate_guarded_worker_response", None)),
        "public V7 did not load the exact separately authenticated V1 bootstrap",
    )
    frozen_v4.require_candidate_free()
    return module


def _validate_campaign_document(
    report: Mapping[str, Any],
    module: str,
    report_sha256: str | None,
    *,
    base_report: Mapping[str, Any] | None = None,
    controller_sha256: str | None = None,
    expected_selected_method_sha256: str = ORIGINAL_OFFICIAL_SELECTED_METHOD_SHA256,
) -> None:
    family = module.removeprefix("candidates.").removesuffix("_candidate")
    expected_role = f"{family}-complete-correctness-campaign"
    frozen_v4.require(
        family in ("rust", "vm", "zig")
        and isinstance(report_sha256, str)
        and frozen_v4.valid_sha256(report_sha256)
        and isinstance(report, Mapping)
        and report.get("schema") == "rebar-rust-campaign-gate-v1"
        and report.get("postfinal_schema") == CAMPAIGN_CONTROLLER_SCHEMA
        and report.get("controller_source_path")
        == _owned_relative(RUST_CAMPAIGN_CONTROLLER_PATH)
        and report.get("controller_source_sha256")
        == RUST_CAMPAIGN_CONTROLLER_SHA256
        and report.get("ancestor_source_path")
        == _owned_relative(CAMPAIGN_ANCESTOR_PATH)
        and report.get("ancestor_source_sha256") == CAMPAIGN_ANCESTOR_SHA256
        and report.get("candidate") == module
        and report.get("passed") is True
        and report.get("required_correctness_step_count") == 22
        and report.get("mode") == "sealed-practice-only"
        and report.get("performance") == "NOT MEASURED"
        and report.get("holdout_accessed") is False
        and report.get("timing_performed") is False
        and report.get("fail_fast") is True
        and report.get("pinned_cpython") == "3.14.6"
        and report.get("python_version") == "3.14.6"
        and report_sha256 == PROOF_SHA256.get(expected_role),
        f"the complete {family} compatibility campaign was substituted or weakened",
    )
    goal = report.get("goal")
    frozen_v4.require(
        isinstance(goal, Mapping)
        and goal.get("passed") is True
        and goal.get("expected_sha256") == GOAL_SHA256
        and goal.get("actual_sha256") == GOAL_SHA256,
        f"the {family} campaign did not bind the immutable original goal",
    )
    steps = report.get("steps")
    frozen_v4.require(
        isinstance(steps, list)
        and len(steps) == 22
        and tuple(step.get("name") for step in steps if isinstance(step, Mapping))
        == EXPECTED_CAMPAIGN_STAGES
        and all(
            isinstance(step, Mapping)
            and step.get("status") == "passed"
            and step.get("passed") is True
            for step in steps
        ),
        f"the {family} campaign omitted, reordered, or failed a required stage",
    )
    by_name = {step["name"]: step for step in steps}
    for name, count in (
        ("candidate-frozen-edge-proof", 223_198),
        ("candidate-frozen-deep-public-proof", 393),
        ("frozen-cross-family-observability", 479),
        ("official-cpython-tests", OFFICIAL_LOCALE_TESTS),
        ("full-unicode-plane", 4_494_555),
    ):
        frozen_v4.require(
            by_name[name].get("expected_checks") == count,
            f"the {family} campaign weakened the exact {name} denominator",
        )
    unicode = by_name["full-unicode-plane"].get("evidence")
    frozen_v4.require(
        isinstance(unicode, Mapping)
        and unicode.get("schema") == "rebar-rust-unicode-probe-v1"
        and unicode.get("module") == module
        and unicode.get("correctness_checks") == 4_494_555
        and unicode.get("failed") == 0,
        f"the {family} campaign omitted a full, passing Unicode-plane comparison",
    )
    frozen_v4.require(
        isinstance(base_report, Mapping)
        and controller_sha256 == RUST_CAMPAIGN_CONTROLLER_SHA256,
        f"the {family} sealed campaign producer or current V5 base was substituted",
    )
    static = by_name["from-scratch-static-audit"].get("evidence")
    expected_locale = {
        "schema": OFFICIAL_LOCALE_SCHEMA,
        "path": _owned_relative(OFFICIAL_LOCALE_REPORT_PATH),
        "sha256": OFFICIAL_LOCALE_REPORT_SHA256,
        "source_path": _owned_relative(OFFICIAL_LOCALE_SOURCE_PATH),
        "source_sha256": OFFICIAL_LOCALE_SOURCE_SHA256,
        "official_methods": OFFICIAL_LOCALE_TESTS,
        "candidate_family": family,
        "all_roles": ["re", "rust", "vm", "zig"],
    }
    expected_strict = {
        "schema": STRICT_AUDIT_SCHEMA,
        "path": _owned_relative(STRICT_AUDIT_PATH),
        "sha256": STRICT_AUDIT_SHA256,
        "source_path": _owned_relative(STRICT_AUDIT_SOURCE_PATH),
        "source_sha256": STRICT_AUDIT_SOURCE_SHA256,
        "strict_control_count": STRICT_AUDIT_CONTROL_COUNT,
        "inherited_control_count": 76,
    }
    expected_controller = {
        "postfinal_schema": CAMPAIGN_CONTROLLER_SCHEMA,
        "source_path": _owned_relative(RUST_CAMPAIGN_CONTROLLER_PATH),
        "source_sha256": RUST_CAMPAIGN_CONTROLLER_SHA256,
        "ancestor_source_path": _owned_relative(CAMPAIGN_ANCESTOR_PATH),
        "ancestor_source_sha256": CAMPAIGN_ANCESTOR_SHA256,
        "expected_complete_production_role_count": (
            CAMPAIGN_COMPLETE_PRODUCTION_ROLE_COUNTS[family]
        ),
    }
    frozen_v4.require(
        isinstance(static, Mapping)
        and static.get("sealed_locale_provenance") == expected_locale
        and static.get("sealed_no_delegation_provenance") == expected_strict
        and static.get("sealed_campaign_controller") == expected_controller
        and {
            key: value
            for key, value in static.items()
            if key
            not in {
                "sealed_locale_provenance",
                "sealed_no_delegation_provenance",
                "sealed_campaign_controller",
            }
        }
        == base_report,
        f"the {family} campaign changed its exact V5 base, locale, "
        "no-delegation, producer, or owned production roles",
    )
    official = by_name["official-cpython-tests"].get("evidence")
    frozen_v4.require(
        isinstance(official, Mapping)
        and official.get("schema") == "rebar-cpython-re-result-v1"
        and official.get("module") == module
        and official.get("methods") == OFFICIAL_LOCALE_TESTS
        and official.get("passed") == OFFICIAL_LOCALE_TESTS
        and official.get("skipped") == 0
        and official.get("failed") == 0
        and official.get("crashes") == 0
        and official.get("timeouts") == 0
        and official.get("runner_sha256") == ORIGINAL_OFFICIAL_RUNNER_SHA256
        and official.get("source_sha256") == ORIGINAL_OFFICIAL_SOURCE_HASHES
        and isinstance(official.get("records"), list)
        and len(official["records"]) == OFFICIAL_LOCALE_TESTS,
        f"the {family} campaign did not genuinely run all 146 official methods",
    )
    official_names: set[str] = set()
    for record in official["records"]:
        frozen_v4.require(
            isinstance(record, Mapping)
            and isinstance(record.get("test"), str)
            and record["test"] not in official_names
            and record.get("status") == "passed"
            and record.get("skipped") == 0
            and record.get("reason") is None
            and not record.get("failures"),
            f"the {family} campaign concealed an official skip or failed method",
        )
        official_names.add(record["test"])
    frozen_v4.require(
        "ReTests.test_locale_caching" in official_names
        and "ReTests.test_locale_compiled" in official_names
        and hashlib.sha256(
            json.dumps(
                sorted(official_names),
                sort_keys=True,
                ensure_ascii=True,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("ascii")
        ).hexdigest()
        == expected_selected_method_sha256,
        f"the {family} campaign changed the exact immutable CPython method identities",
    )
    if family == "rust":
        frozen_v4.require(
            report_sha256 == RUST_CAMPAIGN_SHA256
            and report_sha256 != REJECTED_RUST_CAMPAIGN_SHA256
            and isinstance(base_report, Mapping),
            "public V7 accepted the preliminary or unverified Rust campaign",
        )
        rust = base_report.get("families", {}).get("rust", {})
        native = base_report.get("native_elf_provenance", {}).get("families", {}).get("rust", {}).get("files", {})
        sources = rust.get("native_sources")
        frozen_v4.require(
            base_report.get("postfinal_schema") == BASE_AUDIT_SCHEMA
            and base_report.get("audit_source_sha256") == BASE_AUDIT_SOURCE_SHA256
            and base_report.get("status") == "PASS"
            and base_report.get("passed") is True
            and base_report.get("self_test", {}).get("check_count") == 76
            and base_report.get("postfinal_wrapper_self_test", {}).get("check_count")
            == BASE_AUDIT_WRAPPER_CONTROL_COUNT
            and isinstance(sources, list)
            and any(
                isinstance(row, Mapping)
                and row.get("file") == "candidates/rust/src/lib.rs"
                and row.get("sha256") == RUST_SOURCE_SHA256
                for row in sources
            )
            and isinstance(native, Mapping)
            and native.get("engine", {}).get("sha256")
            == EXPECTED_NATIVE_FINGERPRINTS["candidates.rust_candidate:native-engine"]
            and native.get("bridge", {}).get("sha256")
            == EXPECTED_NATIVE_FINGERPRINTS["candidates.rust_candidate:native-bridge"],
            "the accepted Rust campaign lost its exact current V5 source or native engine",
        )


def verified_stage05_correctness_artifacts() -> list[dict[str, str]]:
    """Validate twelve current proofs without the obsolete 144-test checker."""

    frozen_v4.require_candidate_free()
    require_stage05_correctness_path_contract()
    _require_complete_campaign_pins()
    for path, digest, label in (
        (GOAL_PATH, GOAL_SHA256, "immutable original goal"),
        (BASE_AUDIT_SOURCE_PATH, BASE_AUDIT_SOURCE_SHA256, "current V5 source verifier"),
        (BASE_AUDIT_PATH, BASE_AUDIT_SHA256, "passing current V5 source audit"),
        (
            STRICT_AUDIT_SOURCE_PATH,
            STRICT_AUDIT_SOURCE_SHA256,
            "current V5 no-delegation verifier",
        ),
        (
            STRICT_AUDIT_PATH,
            STRICT_AUDIT_SHA256,
            "passing current V5 no-delegation audit",
        ),
        (
            RUST_CAMPAIGN_CONTROLLER_PATH,
            RUST_CAMPAIGN_CONTROLLER_SHA256,
            "fail-closed source-bound all-family V5 campaign producer",
        ),
        (
            CAMPAIGN_ANCESTOR_PATH,
            CAMPAIGN_ANCESTOR_SHA256,
            "actual immutable V4 ancestor of the all-family V5 campaign producer",
        ),
    ):
        _require_pinned_file(path, digest, label)
    for role, path in MIXED_CORRECTNESS_PATHS:
        _require_pinned_file(path, PROOF_SHA256[role], f"{role} correctness proof")

    controller = importlib.import_module(
        "tools.rust_v8_multi_candidate_campaign_postfinal_v5"
    )
    frozen_v4.require(
        Path(getattr(controller, "__file__", "")).resolve()
        == RUST_CAMPAIGN_CONTROLLER_PATH.resolve()
        and getattr(controller, "SCHEMA", None) == CAMPAIGN_CONTROLLER_SCHEMA
        and getattr(controller, "ANCESTOR_SOURCE_RELATIVE", None)
        == _owned_relative(CAMPAIGN_ANCESTOR_PATH)
        and getattr(controller, "ANCESTOR_SOURCE_SHA256", None)
        == CAMPAIGN_ANCESTOR_SHA256
        and frozen_v4.pilot.file_sha256(Path(controller.__file__).resolve())
        == RUST_CAMPAIGN_CONTROLLER_SHA256,
        "the candidate-free V5 proof verifier or its actual ancestor was substituted",
    )
    sealed_campaign = controller.original
    observability = importlib.import_module(
        "tools.rust_v8_multi_candidate_observability"
    )
    strict = frozen_v4.read_json(
        STRICT_AUDIT_PATH,
        "passing current V5 no-delegation audit",
    )
    _validated_runtime_provenance(strict)
    base = frozen_v4.read_json(BASE_AUDIT_PATH, "passing current V5 source audit")
    artifacts: list[dict[str, str]] = []
    path_by_role = dict(MIXED_CORRECTNESS_PATHS)
    for family in ("rust", "vm", "zig"):
        module = f"candidates.{family}_candidate"
        edge_path = path_by_role[f"{family}-edge"]
        deep_path = path_by_role[f"{family}-deep-public-contract"]
        observability_path = path_by_role[f"{family}-observability"]
        campaign_role = f"{family}-complete-correctness-campaign"
        campaign_path = path_by_role[campaign_role]

        spec, edge = sealed_campaign.validate_edge(edge_path, module)
        controller.validate_edge_artifacts(base, module, edge)
        deep = sealed_campaign.read_deep_document(deep_path, spec, edge)
        _archive, observations = observability.checked_gzip(
            observability_path,
            parent=ROOT / "candidates" / "evidence",
            description=f"current source-bound V5 {family} observability",
        )
        sealed_campaign.validate_observability_document(
            observations,
            module,
            edge,
            deep,
        )

        campaign = frozen_v4.read_json(
            campaign_path,
            f"passing, source-bound 22-stage V5 {family} campaign",
        )
        controller.ancestor.validate_report_structure(campaign, module)
        _validate_campaign_document(
            campaign,
            module,
            PROOF_SHA256[campaign_role],
            base_report=base,
            controller_sha256=RUST_CAMPAIGN_CONTROLLER_SHA256,
        )
        frozen_v4.require(
            campaign.get("edge_oracle") == edge
            and campaign.get("deep_proof") == deep
            and campaign.get("native_artifacts") == edge.get("production_artifacts"),
            f"the complete {family} campaign substituted its exact matching, "
            "Python-object, or independently owned native proof",
        )
        for suffix in (
            "edge",
            "deep-public-contract",
            "observability",
            "complete-correctness-campaign",
        ):
            role = f"{family}-{suffix}"
            path = path_by_role[role]
            artifacts.append(
                {
                    "role": role,
                    "path": _owned_relative(path),
                    "sha256": frozen_v4.pilot.file_sha256(path),
                }
            )
    frozen_v4.require(
        len(artifacts) == 12
        and tuple(item["role"] for item in artifacts)
        == tuple(role for role, _ in MIXED_CORRECTNESS_PATHS)
        and len({item["path"] for item in artifacts}) == 12
        and all(
            item["sha256"] == PROOF_SHA256[item["role"]]
            for item in artifacts
        ),
        "public V7 omitted, reordered, weakened, or substituted a current "
        "source-bound V5 correctness proof",
    )
    frozen_v4.require_candidate_free()
    return artifacts


def _validate_universal_document(report: Mapping[str, Any]) -> None:
    families = ("rust", "vm", "zig")
    frozen_v4.require(
        isinstance(report, Mapping)
        and report.get("schema") == frozen_v4.UNIVERSAL_ORACLE_SCHEMA
        and report.get("status") == "PASS"
        and report.get("selected") == "all"
        and report.get("selected_candidates") == list(families)
        and report.get("completed_candidates") == list(families)
        and report.get("comparison_complete") is True
        and report.get("failed_candidate") is None
        and report.get("worker_failure") is None
        and report.get("python") == "3.14.6"
        and report.get("seed") == 2026072417
        and report.get("seed_domain") == "rebar/python-re/universal-public/v1"
        and report.get("cases") == 8_192
        and report.get("observations_per_case") == 48
        and report.get("observations_per_candidate") == 393_216
        and report.get("total_comparisons") == 1_179_648
        and report.get("planned_total_comparisons") == 1_179_648
        and report.get("mismatches") == 0
        and report.get("grammar_family_count") == 16
        and report.get("input_stratum_count") == 16
        and report.get("examples_per_stratum") == 32
        and report.get("case_sha256") == UNIVERSAL_CASE_SHA256
        and report.get("performance") == "NOT MEASURED"
        and report.get("benchmark_or_timing_executed") is False
        and report.get("performance_fixtures_read") == 0
        and report.get("holdout") == "NOT ACCESSED"
        and report.get("holdout_cases_read") == 0
        and report.get("external_regex_packages") == 0,
        "the passing all-engine Python compatibility oracle changed or accessed timing",
    )
    audit = report.get("audit")
    frozen_v4.require(
        isinstance(audit, Mapping)
        and audit.get("audit_path") == _owned_relative(BASE_AUDIT_PATH)
        and audit.get("audit_sha256") == BASE_AUDIT_SHA256
        and audit.get("oracle_source_path") == _owned_relative(UNIVERSAL_SOURCE_PATH)
        and audit.get("oracle_source_sha256") == UNIVERSAL_SOURCE_SHA256
        and audit.get("postfinal_no_delegation_audit_path")
        == _owned_relative(STRICT_AUDIT_PATH)
        and audit.get("postfinal_no_delegation_audit_sha256") == STRICT_AUDIT_SHA256
        and audit.get("postfinal_audit_schema") == BASE_AUDIT_SCHEMA
        and audit.get("postfinal_audit_source_path")
        == _owned_relative(BASE_AUDIT_SOURCE_PATH)
        and audit.get("postfinal_audit_source_sha256") == BASE_AUDIT_SOURCE_SHA256
        and audit.get("postfinal_no_delegation_audit_schema") == STRICT_AUDIT_SCHEMA
        and audit.get("postfinal_no_delegation_audit_source_path")
        == _owned_relative(STRICT_AUDIT_SOURCE_PATH)
        and audit.get("postfinal_no_delegation_audit_source_sha256")
        == STRICT_AUDIT_SOURCE_SHA256
        and audit.get("postfinal_no_delegation_control_count") == 32
        and audit.get("postfinal_no_delegation_wrapper_control_count")
        == STRICT_AUDIT_WRAPPER_CONTROL_COUNT
        and audit.get("guarded_worker_source_path")
        == _owned_relative(IMMUTABLE_WORKER_SOURCE_PATH)
        and audit.get("guarded_worker_source_sha256")
        == IMMUTABLE_WORKER_SOURCE_SHA256
        and audit.get("guarded_worker_report_path")
        == _owned_relative(IMMUTABLE_WORKER_REPORT_PATH)
        and audit.get("guarded_worker_report_sha256")
        == IMMUTABLE_WORKER_REPORT_SHA256
        and audit.get("official_locale_schema") == OFFICIAL_LOCALE_SCHEMA
        and audit.get("official_locale_source_path")
        == _owned_relative(OFFICIAL_LOCALE_SOURCE_PATH)
        and audit.get("official_locale_source_sha256")
        == OFFICIAL_LOCALE_SOURCE_SHA256
        and audit.get("official_locale_report_path")
        == _owned_relative(OFFICIAL_LOCALE_REPORT_PATH)
        and audit.get("official_locale_report_sha256")
        == OFFICIAL_LOCALE_REPORT_SHA256
        and audit.get("official_locale_roles") == ["re", "rust", "vm", "zig"]
        and audit.get("official_locale_methods_per_role") == 146
        and audit.get("official_locale_total_method_results") == 584
        and audit.get("official_locale_selected_method_sha256")
        == ORIGINAL_OFFICIAL_SELECTED_METHOD_SHA256
        and audit.get("official_locale_skipped") == 0
        and audit.get("selected_candidates") == list(families)
        and audit.get("previous_public_timing_evidence_read") is False,
        "the all-engine oracle lost its V5 proofs or immutable V1 worker",
    )
    grouped_sources = audit.get("source_sha256")
    frozen_v4.require(
        isinstance(grouped_sources, Mapping)
        and set(grouped_sources) == set(families)
        and all(isinstance(grouped_sources[family], Mapping) for family in families),
        "the stage-06 oracle omitted an independently owned source family",
    )
    actual_sources: dict[str, str] = {}
    for family in families:
        for relative, digest in grouped_sources[family].items():
            frozen_v4.require(
                isinstance(relative, str)
                and frozen_v4.valid_sha256(digest)
                and relative not in actual_sources,
                "the stage-06 oracle substituted or duplicated an owned source",
            )
            actual_sources[relative] = digest
    frozen_v4.require(
        actual_sources == EXPECTED_SOURCE_FINGERPRINTS,
        "the stage-06 oracle changed one of the 12 current candidate sources",
    )
    native_groups = audit.get("native_binary_sha256")
    frozen_v4.require(
        isinstance(native_groups, Mapping) and set(native_groups) == set(families),
        "the stage-06 oracle omitted an independently owned native family",
    )
    for family in families:
        keys = frozen_v4.UNIVERSAL_ORACLE_NATIVE_FINGERPRINT_KEYS[family]
        observed = native_groups[family]
        frozen_v4.require(
            isinstance(observed, Mapping)
            and set(observed) == set(keys)
            and all(
                observed[relative] == EXPECTED_NATIVE_FINGERPRINTS[role]
                for relative, role in keys.items()
            ),
            f"the stage-06 oracle changed the independently owned {family} binaries",
        )
    candidates = report.get("candidate_reports")
    frozen_v4.require(
        isinstance(candidates, Mapping)
        and set(candidates) == set(families),
        "the universal public oracle concealed an independent candidate failure",
    )
    for family in families:
        item = candidates[family]
        guards = (
            {
                "ast-candidate",
                "cpython-sre",
                "stdlib-re",
                "third-party-re2",
                "third-party-regex",
            }
            | {f"{other}-candidate" for other in families if other != family}
        )
        frozen_v4.require(
            isinstance(item, Mapping)
            and item.get("candidate") == family
            and item.get("module") == f"candidates.{family}_candidate"
            and item.get("status") == "PASS"
            and item.get("cases") == 8_192
            and item.get("observations_per_case") == 48
            and item.get("checks") == 393_216
            and item.get("expected_checks") == 393_216
            and item.get("comparison_complete") is True
            and item.get("case_sha256") == UNIVERSAL_CASE_SHA256
            and item.get("mismatches") == 0
            and item.get("worker_failure") is None
            and item.get("holdout_cases_read") == 0
            and item.get("benchmark_or_timing_executed") is False
            and item.get("performance_fixtures_read") == 0
            and item.get("external_regex_packages") == 0
            and isinstance(item.get("poison_guards"), Mapping)
            and set(item["poison_guards"]) == guards
            and all(value is True for value in item["poison_guards"].values()),
            f"the stage-06 {family} candidate omitted a case or no-delegation guard",
        )


def _validate_stage10_provenance(provenance: Mapping[str, Any]) -> None:
    """Require the actual source graph, failed experiments, and five engines."""

    exact = {
        "source_path": _owned_relative(STAGE10_SOURCE_PATH),
        "source_sha256": STAGE10_SOURCE_SHA256,
        "protocol_path": _owned_relative(STAGE10_PROTOCOL_PATH),
        "protocol_sha256": STAGE10_PROTOCOL_SHA256,
        "observation_domain": STAGE10_OBSERVATION_DOMAIN,
        "base_audit_path": _owned_relative(BASE_AUDIT_PATH),
        "base_audit_sha256": BASE_AUDIT_SHA256,
        "strict_audit_path": _owned_relative(STRICT_AUDIT_PATH),
        "strict_audit_sha256": STRICT_AUDIT_SHA256,
        "official_locale_path": _owned_relative(OFFICIAL_LOCALE_REPORT_PATH),
        "official_locale_sha256": OFFICIAL_LOCALE_REPORT_SHA256,
        "official_methods_per_role": OFFICIAL_LOCALE_TESTS,
        "official_role_count": 4,
        "official_skipped": 0,
        "official_selected_method_sha256": ORIGINAL_OFFICIAL_SELECTED_METHOD_SHA256,
        "previous_public_source_sha256": UNIVERSAL_SOURCE_SHA256,
        "previous_public_report_path": _owned_relative(UNIVERSAL_REPORT_PATH),
        "previous_public_report_sha256": UNIVERSAL_REPORT_SHA256,
        "previous_public_cases": 8_192,
        "previous_public_comparisons": 1_179_648,
        "previous_failed_source_path": _owned_relative(PRESERVED_STAGE07_SOURCE_PATH),
        "previous_failed_source_sha256": PRESERVED_STAGE07_SOURCE_SHA256,
        "previous_failed_protocol_path": _owned_relative(
            PRESERVED_STAGE07_PROTOCOL_PATH
        ),
        "previous_failed_protocol_sha256": PRESERVED_STAGE07_PROTOCOL_SHA256,
        "previous_self_oracle_failure_path": _owned_relative(
            PRESERVED_STAGE07_FAILURE_PATH
        ),
        "previous_self_oracle_failure_sha256": PRESERVED_STAGE07_FAILURE_SHA256,
        "previous_self_oracle_failure_count": 32,
        "previous_hash_nondeterminism_only": True,
        "previous_stage08_source_path": _owned_relative(PRESERVED_STAGE08_SOURCE_PATH),
        "previous_stage08_source_sha256": PRESERVED_STAGE08_SOURCE_SHA256,
        "previous_stage08_protocol_path": _owned_relative(
            PRESERVED_STAGE08_PROTOCOL_PATH
        ),
        "previous_stage08_protocol_sha256": PRESERVED_STAGE08_PROTOCOL_SHA256,
        "previous_stage08_self_oracle_path": _owned_relative(
            PRESERVED_STAGE08_SELF_ORACLE_PATH
        ),
        "previous_stage08_self_oracle_sha256": PRESERVED_STAGE08_SELF_ORACLE_SHA256,
        "previous_stage08_rust_failure_path": _owned_relative(
            PRESERVED_STAGE08_RUST_FAILURE_PATH
        ),
        "previous_stage08_rust_failure_sha256": PRESERVED_STAGE08_RUST_FAILURE_SHA256,
        "previous_stage08_rust_failure_count": 256,
        "previous_stage08_rust_matching_observations": 3_328,
        "previous_stage08_rust_failure_preserved": True,
    }
    frozen_v4.require(
        isinstance(provenance, Mapping)
        and all(
            provenance.get(field) == value
            and type(provenance.get(field)) is type(value)
            for field, value in exact.items()
        ),
        "the stage-10 public proof changed its source, current audits, genuine "
        "locales, previous 1,179,648 checks, or either preserved failure",
    )
    groups = provenance.get("source_sha256_by_family")
    frozen_v4.require(
        isinstance(groups, Mapping)
        and set(groups) == {"rust", "vm", "zig"}
        and all(isinstance(groups[family], Mapping) for family in groups),
        "stage-10 omitted an independently written candidate source family",
    )
    sources: dict[str, str] = {}
    for records in groups.values():
        for relative, digest in records.items():
            frozen_v4.require(
                isinstance(relative, str)
                and frozen_v4.valid_sha256(digest)
                and relative not in sources,
                "stage-10 duplicated or weakened a current candidate source",
            )
            sources[relative] = digest
    frozen_v4.require(
        sources == EXPECTED_SOURCE_FINGERPRINTS,
        "stage-10 changed one of the twelve independently owned sources",
    )
    native = provenance.get("native_sha256_by_family")
    frozen_v4.require(
        isinstance(native, Mapping) and set(native) == {"rust", "vm", "zig"},
        "stage-10 omitted an independently owned native family",
    )
    for family in ("rust", "vm", "zig"):
        keys = frozen_v4.UNIVERSAL_ORACLE_NATIVE_FINGERPRINT_KEYS[family]
        expected = {
            relative: EXPECTED_NATIVE_FINGERPRINTS[role]
            for relative, role in keys.items()
        }
        frozen_v4.require(
            native.get(family) == expected,
            f"stage-10 changed an independently audited {family} native engine",
        )


def _validate_stage10_documents(
    reference: Mapping[str, Any],
    all_candidates: Mapping[str, Any],
    provenance: Mapping[str, Any],
    *,
    record_digest: Any,
    reference_digest: str = STAGE10_REFERENCE_RECORD_SHA256,
    metadata_digest: str = STAGE10_METADATA_RECORD_SHA256,
    observed_self_sha256: str = STAGE10_SELF_ORACLE_SHA256,
    observed_all_sha256: str = STAGE10_ALL_CANDIDATE_SHA256,
) -> None:
    """Validate real portable references, all engines, and separate observers."""

    _validate_stage10_provenance(provenance)
    identities = [
        f"{cohort}:{index:04d}"
        for cohort, count in STAGE10_COHORT_COUNTS.items()
        for index in range(count)
    ]
    reference_fields = {
        "schema": STAGE10_SELF_ORACLE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": _owned_relative(STAGE10_SOURCE_PATH),
        "source_sha256": STAGE10_SOURCE_SHA256,
        "protocol_path": _owned_relative(STAGE10_PROTOCOL_PATH),
        "protocol_sha256": STAGE10_PROTOCOL_SHA256,
        "seed": STAGE10_SEED,
        "seed_domain": STAGE10_SEED_DOMAIN,
        "matrix_sha256": STAGE10_MATRIX_SHA256,
        "cohorts": 8,
        "cases": STAGE10_CASES,
        "stdlib_checks": 2 * STAGE10_CASES,
        "mismatches": 0,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    frozen_v4.require(
        isinstance(reference, Mapping)
        and callable(record_digest)
        and observed_self_sha256 == STAGE10_SELF_ORACLE_SHA256
        and all(
            reference.get(field) == value
            and type(reference.get(field)) is type(value)
            for field, value in reference_fields.items()
        )
        and reference.get("independent_stdlib_roles") == ["stdlib-a", "stdlib-b"]
        and reference.get("cohort_cases") == STAGE10_COHORT_COUNTS
        and reference.get("failure_records") == []
        and reference.get("current_provenance") == provenance,
        "stage-10 did not genuinely run two independent Python references",
    )
    records = reference.get("baseline_records")
    frozen_v4.require(
        isinstance(records, list)
        and len(records) == STAGE10_CASES
        and all(isinstance(item, Mapping) for item in records)
        and [item.get("id") for item in records] == identities
        and reference.get("baseline_record_sha256") == reference_digest
        and reference.get("second_record_sha256") == reference_digest
        and record_digest(records) == reference_digest,
        "stage-10 lost a real reference case, genuine surrogate, or stable hash",
    )
    root_fields = {
        "schema": STAGE10_ALL_CANDIDATE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "selected": "all",
        "comparison_complete": True,
        "python": "3.14.6",
        "source_path": _owned_relative(STAGE10_SOURCE_PATH),
        "source_sha256": STAGE10_SOURCE_SHA256,
        "protocol_path": _owned_relative(STAGE10_PROTOCOL_PATH),
        "protocol_sha256": STAGE10_PROTOCOL_SHA256,
        "seed": STAGE10_SEED,
        "seed_domain": STAGE10_SEED_DOMAIN,
        "matrix_sha256": STAGE10_MATRIX_SHA256,
        "cohorts": 8,
        "cases_per_candidate": STAGE10_CASES,
        "candidate_checks": 3 * STAGE10_CASES,
        "previous_public_cases": 8_192,
        "previous_public_comparisons": 1_179_648,
        "combined_public_comparisons": 1_179_648 + 3 * STAGE10_CASES,
        "mismatches": 0,
        "self_oracle_path": _owned_relative(STAGE10_SELF_ORACLE_PATH),
        "self_oracle_sha256": STAGE10_SELF_ORACLE_SHA256,
        "external_regex_packages": 0,
        "candidate_cross_delegation": False,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    frozen_v4.require(
        isinstance(all_candidates, Mapping)
        and observed_all_sha256 == STAGE10_ALL_CANDIDATE_SHA256
        and all(
            all_candidates.get(field) == value
            and type(all_candidates.get(field)) is type(value)
            for field, value in root_fields.items()
        )
        and all_candidates.get("selected_candidates") == ["rust", "vm", "zig"]
        and all_candidates.get("completed_candidates") == ["rust", "vm", "zig"]
        and all_candidates.get("cohort_cases") == STAGE10_COHORT_COUNTS
        and all_candidates.get("current_provenance") == provenance
        and all_candidates.get("locales") == reference.get("locales"),
        "stage-10 did not genuinely pass every independently written regex engine",
    )
    candidates = all_candidates.get("candidate_reports")
    frozen_v4.require(
        isinstance(candidates, Mapping)
        and set(candidates) == {"rust", "vm", "zig"},
        "stage-10 omitted, duplicated, or substituted a regex implementation",
    )
    module_suffix = {
        "rust": "candidates._rust_bridge",
        "vm": "candidates._vm_native",
        "zig": "candidates._zig_bridge",
    }
    for family in ("rust", "vm", "zig"):
        report = candidates[family]
        frozen_v4.require(
            isinstance(report, Mapping)
            and report.get("candidate") == family
            and report.get("module") == f"candidates.{family}_candidate"
            and report.get("status") == "PASS"
            and report.get("cases") == STAGE10_CASES
            and type(report.get("cases")) is int
            and report.get("cohort_cases") == STAGE10_COHORT_COUNTS
            and report.get("record_sha256") == reference_digest
            and report.get("mismatches") == 0
            and type(report.get("mismatches")) is int
            and report.get("failure_records") == []
            and report.get("failures_recorded") == 0
            and report.get("benchmark_or_timing_executed") is False
            and report.get("holdout_cases_read") == 0
            and report.get("performance") == "NOT MEASURED"
            and report.get("native_binary_sha256")
            == provenance["native_sha256_by_family"][family],
            f"stage-10 concealed a {family} mismatch, native engine, or public case",
        )
        guard = report.get("guard")
        frozen_v4.require(
            isinstance(guard, Mapping)
            and guard.get("enabled") is True
            and guard.get("family") == family
            and guard.get("stdlib_re_blocked") is True
            and guard.get("cpython_sre_blocked") is True
            and guard.get("third_party_regex_blocked") is True
            and guard.get("cross_family_blocked") is True
            and guard.get("foreign_dynamic_libraries_blocked") is True
            and guard.get("native_loader_aliases_blocked")
            == list(STAGE10_BLOCKED_NATIVE_LOADER_ALIASES)
            and type(guard.get("cached_regex_aliases_poisoned")) is int
            and guard["cached_regex_aliases_poisoned"] > 0
            and guard.get("loaded_candidate_modules")
            == sorted((f"candidates.{family}_candidate", module_suffix[family])),
            f"stage-10 weakened the independently isolated {family} engine",
        )
        metadata = guard.get("isolated_public_metadata")
        frozen_v4.require(
            isinstance(metadata, Mapping)
            and metadata.get("enabled") is True
            and metadata.get("schema") == STAGE10_METADATA_SCHEMA
            and metadata.get("source_sha256") == STAGE10_SOURCE_SHA256
            and metadata.get("role") == family
            and metadata.get("surface_cases") == 256
            and metadata.get("record_sha256") == metadata_digest
            and metadata.get("production_matching_executed") is False
            and metadata.get("metadata_and_matcher_processes_distinct") is True
            and metadata.get("matcher_inspect_loaded") is False
            and metadata.get("matcher_tokenizer_loaded") is False,
            f"stage-10 substituted an unsafe or incomplete {family} signature observer",
        )


def _require_stage10_qualification() -> dict[str, Any]:
    """Verify only actual public correctness reports; never run a candidate."""

    frozen_v4.require_candidate_free()
    for path, digest, label in (
        (STAGE10_SOURCE_PATH, STAGE10_SOURCE_SHA256, "frozen stage-10 source"),
        (STAGE10_PROTOCOL_PATH, STAGE10_PROTOCOL_SHA256, "frozen stage-10 protocol"),
        (
            STAGE10_SELF_ORACLE_PATH,
            STAGE10_SELF_ORACLE_SHA256,
            "passing stage-10 independent Python references",
        ),
        (
            STAGE10_ALL_CANDIDATE_PATH,
            STAGE10_ALL_CANDIDATE_SHA256,
            "passing stage-10 Rust, C, and Zig proof",
        ),
        (
            PRESERVED_STAGE07_SOURCE_PATH,
            PRESERVED_STAGE07_SOURCE_SHA256,
            "preserved stage-07 failed experiment source",
        ),
        (
            PRESERVED_STAGE07_PROTOCOL_PATH,
            PRESERVED_STAGE07_PROTOCOL_SHA256,
            "preserved stage-07 failed experiment protocol",
        ),
        (
            PRESERVED_STAGE07_FAILURE_PATH,
            PRESERVED_STAGE07_FAILURE_SHA256,
            "all 32 preserved stage-07 Python self-oracle failures",
        ),
        (
            PRESERVED_STAGE08_SOURCE_PATH,
            PRESERVED_STAGE08_SOURCE_SHA256,
            "preserved stage-08 failed experiment source",
        ),
        (
            PRESERVED_STAGE08_PROTOCOL_PATH,
            PRESERVED_STAGE08_PROTOCOL_SHA256,
            "preserved stage-08 failed experiment protocol",
        ),
        (
            PRESERVED_STAGE08_SELF_ORACLE_PATH,
            PRESERVED_STAGE08_SELF_ORACLE_SHA256,
            "passing preserved stage-08 Python reference",
        ),
        (
            PRESERVED_STAGE08_RUST_FAILURE_PATH,
            PRESERVED_STAGE08_RUST_FAILURE_SHA256,
            "all 256 preserved stage-08 Rust harness failures",
        ),
    ):
        _require_pinned_file(path, digest, label)
    module = importlib.import_module(
        "tools.python_re_universal_public_oracle_stage10"
    )
    frozen_v4.require(
        Path(getattr(module, "__file__", "")).resolve()
        == STAGE10_SOURCE_PATH.resolve()
        and frozen_v4.pilot.file_sha256(Path(module.__file__).resolve())
        == STAGE10_SOURCE_SHA256
        and getattr(module, "SCHEMA", None) == STAGE10_SCHEMA
        and getattr(module, "SELF_ORACLE_SCHEMA", None) == STAGE10_SELF_ORACLE_SCHEMA
        and getattr(module, "ALL_CANDIDATE_SCHEMA", None)
        == STAGE10_ALL_CANDIDATE_SCHEMA
        and getattr(module, "OBSERVATION_DOMAIN", None) == STAGE10_OBSERVATION_DOMAIN
        and getattr(module, "MATRIX_SHA256", None) == STAGE10_MATRIX_SHA256
        and getattr(module, "REQUIRED_CANDIDATES", None) == ("rust", "vm", "zig")
        and callable(getattr(module, "_stage10_context", None))
        and callable(getattr(module, "_authenticate_current_provenance", None)),
        "public V7 did not load the actual candidate-free stage-10 verifier",
    )
    reference = frozen_v4.read_json(
        STAGE10_SELF_ORACLE_PATH,
        "passing stage-10 independent Python self-oracle",
    )
    all_candidates = frozen_v4.read_json(
        STAGE10_ALL_CANDIDATE_PATH,
        "passing all-three stage-10 public contract",
    )
    with module._stage10_context():
        provenance = module._authenticate_current_provenance()
        validated = module.stage07._validate_self_oracle(reference, provenance)
        _validate_stage10_documents(
            validated,
            all_candidates,
            provenance,
            record_digest=module.digest,
        )
        frozen_v4.require_candidate_free()
    frozen_v4.require_candidate_free()
    return {"reference": validated, "all_candidates": all_candidates, "provenance": provenance}


def _validate_locale_qualification_report(
    report: Mapping[str, Any],
    source_fingerprints: Mapping[str, str],
    native_fingerprints: Mapping[str, str],
    *,
    observed_report_sha256: str,
    expected_report_sha256: str,
    expected_producer_sha256: str,
    expected_selected_method_sha256: str,
) -> None:
    """Require the real-locale official suite for CPython and every engine."""

    families = ("re", "rust", "vm", "zig")
    frozen_v4.require(
        frozen_v4.valid_sha256(expected_report_sha256)
        and observed_report_sha256 == expected_report_sha256
        and isinstance(report, Mapping)
        and report.get("schema") == OFFICIAL_LOCALE_SCHEMA
        and report.get("status") == "PASS"
        and report.get("result") == "PASS"
        and report.get("python") == "3.14.6"
        and report.get("goal_sha256") == GOAL_SHA256
        and report.get("source_path") == _owned_relative(OFFICIAL_LOCALE_SOURCE_PATH)
        and frozen_v4.valid_sha256(expected_producer_sha256)
        and report.get("source_sha256") == expected_producer_sha256
        and report.get("qualified_source_fingerprints") == source_fingerprints
        and report.get("native_elf_fingerprints") == native_fingerprints
        and native_fingerprints == EXPECTED_NATIVE_FINGERPRINTS
        and len(source_fingerprints) == 12
        and report.get("holdout_accessed") is False
        and report.get("timing_performed") is False
        and report.get("benchmark_or_timing_executed", False) is False
        and report.get("performance") == "NOT MEASURED",
        "real-locale CPython qualification is missing, stale, or not source-bound",
    )
    original = report.get("original_oracle")
    frozen_v4.require(
        isinstance(original, Mapping)
        and original.get("manifest_path") == ORIGINAL_OFFICIAL_MANIFEST_RELATIVE
        and original.get("manifest_sha256") == ORIGINAL_OFFICIAL_MANIFEST_SHA256
        and original.get("runner_path") == ORIGINAL_OFFICIAL_RUNNER_RELATIVE
        and original.get("runner_sha256") == ORIGINAL_OFFICIAL_RUNNER_SHA256
        and original.get("source_sha256") == ORIGINAL_OFFICIAL_SOURCE_HASHES
        and original.get("total_public_methods") == 152
        and original.get("selected_methods") == OFFICIAL_LOCALE_TESTS
        and frozen_v4.valid_sha256(expected_selected_method_sha256)
        and original.get("selected_method_sha256")
        == expected_selected_method_sha256
        and original.get("named_waivers") == ORIGINAL_OFFICIAL_PRIVATE_METHOD_WAIVERS
        and original.get("named_class_waivers")
        == ORIGINAL_OFFICIAL_PRIVATE_CLASS_WAIVERS
        and original.get("all_named_waivers")
        == (ORIGINAL_OFFICIAL_PRIVATE_METHOD_WAIVERS | ORIGINAL_OFFICIAL_PRIVATE_CLASS_WAIVERS)
        and original.get("corpus_cases") == 403,
        "the real-locale run did not bind the complete original CPython oracle",
    )
    audits = report.get("audits")
    base = audits.get("from_scratch") if isinstance(audits, Mapping) else None
    strict = audits.get("no_delegation") if isinstance(audits, Mapping) else None
    frozen_v4.require(
        isinstance(base, Mapping)
        and base.get("path") == _owned_relative(BASE_AUDIT_PATH)
        and base.get("sha256") == BASE_AUDIT_SHA256
        and base.get("postfinal_schema") == BASE_AUDIT_SCHEMA
        and base.get("source_path") == _owned_relative(BASE_AUDIT_SOURCE_PATH)
        and base.get("source_sha256") == BASE_AUDIT_SOURCE_SHA256
        and isinstance(strict, Mapping)
        and strict.get("path") == _owned_relative(STRICT_AUDIT_PATH)
        and strict.get("sha256") == STRICT_AUDIT_SHA256
        and strict.get("postfinal_schema") == STRICT_AUDIT_SCHEMA
        and strict.get("source_path") == _owned_relative(STRICT_AUDIT_SOURCE_PATH)
        and strict.get("source_sha256") == STRICT_AUDIT_SOURCE_SHA256,
        "the real-locale report omitted the exact current independent source audits",
    )
    locales = report.get("locales")
    iso = locales.get("iso88591") if isinstance(locales, Mapping) else None
    utf8 = locales.get("utf8") if isinstance(locales, Mapping) else None
    frozen_v4.require(
        isinstance(locales, Mapping)
        and locales.get("private") is True
        and locales.get("genuine") is True
        and isinstance(iso, Mapping)
        and iso.get("name") == "en_US.iso88591"
        and frozen_v4.valid_sha256(iso.get("source_sha256"))
        and frozen_v4.valid_sha256(iso.get("charmap_sha256"))
        and isinstance(utf8, Mapping)
        and utf8.get("name") == "en_US.utf8"
        and frozen_v4.valid_sha256(utf8.get("source_sha256"))
        and frozen_v4.valid_sha256(utf8.get("charmap_sha256")),
        "the official suite did not run with genuine private ISO-8859-1 and UTF-8 locales",
    )
    reference = report.get("locale_reference")
    frozen_v4.require(
        isinstance(reference, Mapping)
        and reference.get("status") == "PASS"
        and reference.get("python") == "3.14.6"
        and reference.get("genuine_locales") is True
        and reference.get("compiled_locale_switch") is True
        and reference.get("candidate_modules_loaded") is False
        and reference.get("holdout_accessed") is False
        and reference.get("timing_performed") is False,
        "the real-locale reference did not independently verify CPython locale switching",
    )
    reports = report.get("roles")
    frozen_v4.require(
        isinstance(reports, Mapping) and set(reports) == set(families),
        "real-locale qualification omitted CPython or an independent candidate",
    )
    baseline_methods: set[str] | None = None
    for family in families:
        item = reports[family]
        expected_module = "re" if family == "re" else f"candidates.{family}_candidate"
        frozen_v4.require(
            isinstance(item, Mapping)
            and item.get("module") == expected_module
            and item.get("methods") == OFFICIAL_LOCALE_TESTS
            and item.get("passed") == OFFICIAL_LOCALE_TESTS
            and item.get("failed") == 0
            and item.get("failures") == 0
            and item.get("errors") == 0
            and item.get("skipped") == 0
            and item.get("crashes") == 0
            and item.get("timeouts") == 0
            and item.get("locale_caching_passed") is True
            and item.get("locale_compiled_passed") is True,
            f"the {family} engine did not genuinely pass all 146 real-locale tests",
        )
        records = item.get("records")
        frozen_v4.require(
            isinstance(records, list)
            and len(records) == OFFICIAL_LOCALE_TESTS
            and all(isinstance(record, Mapping) for record in records),
            f"the {family} locale suite concealed individual official CPython methods",
        )
        methods: set[str] = set()
        for record in records:
            name = record.get("test")
            frozen_v4.require(
                isinstance(name, str)
                and name
                and name not in methods
                and record.get("status") == "passed"
                and record.get("skipped") == 0
                and record.get("reason") is None
                and record.get("failed", 0) == 0
                and record.get("failures", 0) == 0
                and record.get("errors", 0) == 0
                and record.get("crashes", 0) == 0
                and record.get("timeouts", 0) == 0,
                f"the {family} official locale proof hid a failed or duplicated test",
            )
            methods.add(name)
        frozen_v4.require(
            "ReTests.test_locale_caching" in methods
            and "ReTests.test_locale_compiled" in methods,
            f"the {family} official proof omitted a real-locale CPython test",
        )
        if family == "re":
            baseline_methods = methods
            canonical = json.dumps(
                sorted(methods),
                sort_keys=True,
                ensure_ascii=True,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("ascii")
            frozen_v4.require(
                original.get("selected_method_sha256")
                == hashlib.sha256(canonical).hexdigest(),
                "the actual CPython selected-method identities were substituted",
            )
        else:
            frozen_v4.require(
                methods == baseline_methods,
                f"the {family} official suite changed the exact CPython reference tests",
            )


def _require_locale_qualification() -> dict[str, Any]:
    """Fail closed before a plan or worker until real-locale proof is pinned."""

    frozen_v4.require_candidate_free()
    frozen_v4.require_pinned_python()
    frozen_v4.require(
        isinstance(OFFICIAL_LOCALE_REPORT_SHA256, str)
        and frozen_v4.valid_sha256(OFFICIAL_LOCALE_REPORT_SHA256),
        "V7 freezing is blocked: no pinned, source-bound 146/146 real-locale "
        "qualification exists for CPython and all three candidates",
    )
    frozen_v4.require(
        isinstance(OFFICIAL_LOCALE_SOURCE_SHA256, str)
        and frozen_v4.valid_sha256(OFFICIAL_LOCALE_SOURCE_SHA256),
        "V7 freezing is blocked: the real-locale qualification producer "
        "has not been independently pinned",
    )
    _require_pinned_file(
        OFFICIAL_LOCALE_SOURCE_PATH,
        OFFICIAL_LOCALE_SOURCE_SHA256,
        "owned fail-closed all-engine real-locale oracle source",
    )
    _require_pinned_file(
        OFFICIAL_LOCALE_REPORT_PATH,
        OFFICIAL_LOCALE_REPORT_SHA256,
        "146/146 zero-skip all-engine real-locale qualification",
    )
    _digest, sources, native, _details = verified_from_scratch_audit()
    report = frozen_v4.read_json(
        OFFICIAL_LOCALE_REPORT_PATH,
        "passing all-engine 146-test real-locale CPython qualification",
    )
    _validate_locale_qualification_report(
        report,
        sources,
        native,
        observed_report_sha256=frozen_v4.pilot.file_sha256(
            OFFICIAL_LOCALE_REPORT_PATH
        ),
        expected_report_sha256=OFFICIAL_LOCALE_REPORT_SHA256,
        expected_producer_sha256=OFFICIAL_LOCALE_SOURCE_SHA256,
        expected_selected_method_sha256=ORIGINAL_OFFICIAL_SELECTED_METHOD_SHA256,
    )
    frozen_v4.require_candidate_free()
    return report


def _validate_public_parity(
    original: Mapping[str, Any], document: Mapping[str, Any]
) -> None:
    frozen_v4.require(
        isinstance(original, Mapping)
        and isinstance(document, Mapping)
        and original.get("postfinal_schema")
        == "rebar-postfinal-public-practice-plan-v6"
        and original.get("protocol_version")
        == "postfinal-public-practice-v6"
        and original.get("runner_sha256") == FROZEN_V6_SOURCE_SHA256
        and document.get("postfinal_schema") == POSTFINAL_PLAN_SCHEMA
        and document.get("protocol_version") == VERSION
        and frozen_v4.valid_sha256(document.get("runner_sha256")),
        "public V7 did not preserve the exact frozen V6 public plan",
    )
    for field in predecessor.PUBLIC_PARITY_FIELDS:
        frozen_v4.require(
            field in original
            and field in document
            and document[field] == original[field],
            f"public V7 changed a frozen public case or denominator: {field}",
        )
    frozen_v4.require(
        original.get("cases") == 8_192
        and original.get("all_bounded_workload_categories") == 260
        and original.get("modules") == list(frozen_v4.MODULES)
        and original.get("public_operations")
        == predecessor.FROZEN_PUBLIC_OPERATION_COUNTS
        and sum(predecessor.FROZEN_PUBLIC_OPERATION_COUNTS.values()) == 8_192
        and original.get("selection_seed") == 2026072404
        and original.get("order_seed") == 2026072405
        and original.get("bootstrap_seed") == 2026072406
        and original.get("frozen_warmups") == 4
        and original.get("frozen_trials") == 13
        and original.get("frozen_bootstrap_samples") == 2_000
        and original.get("holdout_accessed") is False
        and original.get("held_out_cases_generated") == 0
        and original.get("held_out_records_deserialized") == 0
        and original.get("historical_performance_read") is False
        and original.get("timing_performed") is False,
        "public V7 changed the original fair cases, seeds, trials, or holdout policy",
    )
    selected = original.get("selected_cases")
    frozen_v4.require(
        isinstance(selected, list) and len(selected) == 8_192,
        "public V7 changed the exact equal-weight case denominator",
    )
    identifiers: set[str] = set()
    apis: collections.Counter[str] = collections.Counter()
    categories: collections.Counter[str] = collections.Counter()
    for row in selected:
        frozen_v4.require(
            isinstance(row, Mapping)
            and isinstance(row.get("case"), str)
            and row["case"] not in identifiers
            and row.get("cohort") == frozen_v4.pilot.PRACTICE
            and isinstance(row.get("api"), str)
            and isinstance(row.get("category"), str)
            and frozen_v4.valid_sha256(row.get("expected_result_sha256"))
            and isinstance(row.get("selection_reasons"), list)
            and type(row.get("frozen_operations")) is int
            and row["frozen_operations"] > 0,
            "public V7 concealed, duplicated, or weakened an equal-weight case",
        )
        identifiers.add(row["case"])
        apis[row["api"]] += 1
        categories[row["category"]] += 1
    frozen_v4.require(
        dict(apis) == predecessor.FROZEN_PUBLIC_OPERATION_COUNTS
        and isinstance(original.get("categories"), Mapping)
        and len(original["categories"]) == 260
        and dict(categories) == dict(original["categories"]),
        "public V7 reweighted one of the 12 operations or 260 public categories",
    )


def _verified_frozen_v6_manifest() -> dict[str, Any]:
    frozen_v4.require_candidate_free()
    for path, digest, label in (
        (FROZEN_V6_SOURCE_PATH, FROZEN_V6_SOURCE_SHA256, "immutable V6 public runner"),
        (FROZEN_V6_MANIFEST_PATH, FROZEN_V6_MANIFEST_SHA256, "immutable V6 public plan"),
        (FROZEN_V6_PROTOCOL_PATH, FROZEN_V6_PROTOCOL_SHA256, "immutable V6 public protocol"),
    ):
        _require_pinned_file(path, digest, label)
    result = frozen_v4.read_json(
        FROZEN_V6_MANIFEST_PATH, "immutable unmeasured 8,192-case V6 public plan"
    )
    frozen_v4.require_candidate_free()
    return result


def make_manifest(edge_paths: list[Path]) -> tuple[Any, list[Any], dict[str, Any]]:
    frozen_v4.require_candidate_free()
    frozen_v4.require_pinned_python()
    stage10_qualification = _require_stage10_qualification()
    locale_qualification = _require_locale_qualification()
    original = _verified_frozen_v6_manifest()
    for path, digest, label in (
        (
            UNIVERSAL_SOURCE_PATH,
            UNIVERSAL_SOURCE_SHA256,
            "stage-06 all-engine public compatibility source",
        ),
        (
            UNIVERSAL_REPORT_PATH,
            UNIVERSAL_REPORT_SHA256,
            "passing stage-06 all-engine public compatibility report",
        ),
    ):
        _require_pinned_file(path, digest, label)
    _validate_universal_document(
        frozen_v4.read_json(
            UNIVERSAL_REPORT_PATH,
            "passing stage-06 all-engine public compatibility oracle",
        )
    )
    suite, entries, document = _ORIGINAL_MAKE_MANIFEST(edge_paths)
    frozen_v4.require(
        document.get("protocol_version") == VERSION
        and document.get("postfinal_schema") == POSTFINAL_PLAN_SCHEMA
        and document.get("exclusive_slot") == EXCLUSIVE_SLOT
        and document.get("runner_sha256")
        == frozen_v4.pilot.file_sha256(SOURCE_PATH),
        "public V7 did not bind its exact source or exclusive protocol",
    )
    _validate_public_parity(original, document)
    provenance: dict[str, Any] = {
        "goal_path": _owned_relative(GOAL_PATH),
        "goal_sha256": GOAL_SHA256,
        "source_public_v6_runner_path": _owned_relative(FROZEN_V6_SOURCE_PATH),
        "source_public_v6_runner_sha256": FROZEN_V6_SOURCE_SHA256,
        "source_public_v6_manifest_path": _owned_relative(FROZEN_V6_MANIFEST_PATH),
        "source_public_v6_manifest_sha256": FROZEN_V6_MANIFEST_SHA256,
        "source_public_v6_protocol_path": _owned_relative(FROZEN_V6_PROTOCOL_PATH),
        "source_public_v6_protocol_sha256": FROZEN_V6_PROTOCOL_SHA256,
        "public_v6_case_population_preserved": True,
        "public_v6_case_population_count": 8_192,
        "public_v6_workload_category_count": 260,
        "postfinal_stage10_source_path": _owned_relative(STAGE10_SOURCE_PATH),
        "postfinal_stage10_source_sha256": STAGE10_SOURCE_SHA256,
        "postfinal_stage10_protocol_path": _owned_relative(STAGE10_PROTOCOL_PATH),
        "postfinal_stage10_protocol_sha256": STAGE10_PROTOCOL_SHA256,
        "postfinal_stage10_self_oracle_path": _owned_relative(
            STAGE10_SELF_ORACLE_PATH
        ),
        "postfinal_stage10_self_oracle_sha256": STAGE10_SELF_ORACLE_SHA256,
        "postfinal_stage10_all_candidate_path": _owned_relative(
            STAGE10_ALL_CANDIDATE_PATH
        ),
        "postfinal_stage10_all_candidate_sha256": STAGE10_ALL_CANDIDATE_SHA256,
        "postfinal_stage10_schema": STAGE10_SCHEMA,
        "postfinal_stage10_self_oracle_schema": STAGE10_SELF_ORACLE_SCHEMA,
        "postfinal_stage10_all_candidate_schema": STAGE10_ALL_CANDIDATE_SCHEMA,
        "postfinal_stage10_matrix_sha256": STAGE10_MATRIX_SHA256,
        "postfinal_stage10_seed": STAGE10_SEED,
        "postfinal_stage10_seed_domain": STAGE10_SEED_DOMAIN,
        "postfinal_stage10_observation_domain": STAGE10_OBSERVATION_DOMAIN,
        "postfinal_stage10_cohort_cases": dict(STAGE10_COHORT_COUNTS),
        "postfinal_stage10_cases_per_candidate": STAGE10_CASES,
        "postfinal_stage10_candidate_checks": stage10_qualification[
            "all_candidates"
        ]["candidate_checks"],
        "postfinal_stage10_combined_public_comparisons": stage10_qualification[
            "all_candidates"
        ]["combined_public_comparisons"],
        "postfinal_stage10_self_checks": 2 * STAGE10_CASES,
        "postfinal_stage10_isolated_signature_cases": 256,
        "postfinal_stage10_native_loader_aliases": list(
            STAGE10_BLOCKED_NATIVE_LOADER_ALIASES
        ),
        "postfinal_stage10_reference_record_sha256": (
            STAGE10_REFERENCE_RECORD_SHA256
        ),
        "postfinal_stage10_metadata_record_sha256": STAGE10_METADATA_RECORD_SHA256,
        "postfinal_stage07_failure_path": _owned_relative(
            PRESERVED_STAGE07_FAILURE_PATH
        ),
        "postfinal_stage07_failure_sha256": PRESERVED_STAGE07_FAILURE_SHA256,
        "postfinal_stage07_failure_count": 32,
        "postfinal_stage08_rust_failure_path": _owned_relative(
            PRESERVED_STAGE08_RUST_FAILURE_PATH
        ),
        "postfinal_stage08_rust_failure_sha256": (
            PRESERVED_STAGE08_RUST_FAILURE_SHA256
        ),
        "postfinal_stage08_rust_failure_count": 256,
        "postfinal_sealed_campaign_schema": CAMPAIGN_CONTROLLER_SCHEMA,
        "postfinal_sealed_campaign_controller_path": _owned_relative(
            RUST_CAMPAIGN_CONTROLLER_PATH
        ),
        "postfinal_sealed_campaign_controller_sha256": (
            RUST_CAMPAIGN_CONTROLLER_SHA256
        ),
        "postfinal_sealed_campaign_ancestor_path": _owned_relative(
            CAMPAIGN_ANCESTOR_PATH
        ),
        "postfinal_sealed_campaign_ancestor_sha256": CAMPAIGN_ANCESTOR_SHA256,
        "postfinal_sealed_campaign_family_count": 3,
        "postfinal_sealed_campaign_reports": {
            family: {
                "path": _owned_relative(path),
                "sha256": digest,
                "expected_complete_production_role_count": (
                    CAMPAIGN_COMPLETE_PRODUCTION_ROLE_COUNTS[family]
                ),
            }
            for family, (path, digest) in {
                "rust": (RUST_CAMPAIGN_PATH, RUST_CAMPAIGN_SHA256),
                "vm": (VM_CAMPAIGN_PATH, VM_CAMPAIGN_SHA256),
                "zig": (ZIG_CAMPAIGN_PATH, ZIG_CAMPAIGN_SHA256),
            }.items()
        },
        "postfinal_rust_sealed_campaign_controller_path": _owned_relative(
            RUST_CAMPAIGN_CONTROLLER_PATH
        ),
        "postfinal_rust_sealed_campaign_controller_sha256": RUST_CAMPAIGN_CONTROLLER_SHA256,
        "postfinal_rust_sealed_campaign_report_path": _owned_relative(RUST_CAMPAIGN_PATH),
        "postfinal_rust_sealed_campaign_report_sha256": RUST_CAMPAIGN_SHA256,
        "postfinal_rust_sealed_campaign_required_steps": 22,
        "postfinal_rust_sealed_campaign_unicode_checks": 4_494_555,
        "postfinal_official_locale_report_path": _owned_relative(
            OFFICIAL_LOCALE_REPORT_PATH
        ),
        "postfinal_official_locale_report_sha256": OFFICIAL_LOCALE_REPORT_SHA256,
        "postfinal_official_locale_report_schema": OFFICIAL_LOCALE_SCHEMA,
        "postfinal_official_locale_source_path": _owned_relative(
            OFFICIAL_LOCALE_SOURCE_PATH
        ),
        "postfinal_official_locale_source_sha256": OFFICIAL_LOCALE_SOURCE_SHA256,
        "postfinal_official_original_manifest_sha256": ORIGINAL_OFFICIAL_MANIFEST_SHA256,
        "postfinal_official_original_runner_sha256": ORIGINAL_OFFICIAL_RUNNER_SHA256,
        "postfinal_official_original_test_source_sha256": ORIGINAL_OFFICIAL_TEST_SOURCE_SHA256,
        "postfinal_official_original_selected_method_sha256": (
            ORIGINAL_OFFICIAL_SELECTED_METHOD_SHA256
        ),
        "postfinal_official_locale_tests_per_family": OFFICIAL_LOCALE_TESTS,
        "postfinal_official_locale_family_count": len(locale_qualification["roles"]),
        "postfinal_official_locale_skipped_tests": 0,
        "private_worker_wire_format": frozen_v5.PRIVATE_WORKER_WIRE_FORMAT,
        "private_worker_wire_ensure_ascii": True,
    }
    for field, value in provenance.items():
        frozen_v4.require(
            field not in document,
            f"public V7 predecessor or campaign provenance collided: {field}",
        )
        document[field] = value
    frozen_v4.require_candidate_free()
    return suite, entries, document


def _synthetic_runtime_report() -> dict[str, Any]:
    return {
        "schema": STRICT_AUDIT_SCHEMA,
        "postfinal_schema": STRICT_AUDIT_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": _owned_relative(STRICT_AUDIT_SOURCE_PATH),
        "audit_source_sha256": STRICT_AUDIT_SOURCE_SHA256,
        "base_audit_report_path": _owned_relative(BASE_AUDIT_PATH),
        "base_audit_report_sha256": BASE_AUDIT_SHA256,
        "base_audit_source_path": _owned_relative(BASE_AUDIT_SOURCE_PATH),
        "base_audit_source_sha256": BASE_AUDIT_SOURCE_SHA256,
        "base_audit_postfinal_schema": BASE_AUDIT_SCHEMA,
        "inherited_control_count": 76,
        "inherited_self_test": {"passed": True, "check_count": 76},
        "self_test": {"passed": True, "check_count": 32, "failed": []},
        "postfinal_wrapper_self_test": {
            "schema": STRICT_AUDIT_SCHEMA + "-self-test",
            "status": "PASS",
            "passed": True,
            "check_count": STRICT_AUDIT_WRAPPER_CONTROL_COUNT,
            "failed": [],
            "candidate_imported": False,
        },
        "previous_v3_audit_source_path": PREVIOUS_V3_STRICT_SOURCE_RELATIVE,
        "previous_v3_audit_source_sha256": PREVIOUS_V3_STRICT_SOURCE_SHA256,
        "previous_v3_audit_report_path": PREVIOUS_V3_STRICT_REPORT_RELATIVE,
        "previous_v3_audit_report_sha256": PREVIOUS_V3_STRICT_REPORT_SHA256,
        "previous_v4_audit_source_path": PREVIOUS_V4_STRICT_SOURCE_RELATIVE,
        "previous_v4_audit_source_sha256": PREVIOUS_V4_STRICT_SOURCE_SHA256,
        "previous_v4_source_report_path": PREVIOUS_V4_BASE_REPORT_RELATIVE,
        "previous_v4_source_report_sha256": PREVIOUS_V4_BASE_REPORT_SHA256,
        "previous_v4_source_report_historical": True,
        "previous_v4_strict_report_created": False,
        "native_elf_fingerprints": dict(EXPECTED_NATIVE_FINGERPRINTS),
        "qualified_source_fingerprints": dict(EXPECTED_SOURCE_FINGERPRINTS),
        "scope": {
            "persistent_measurement_worker_available": True,
            "immutable_v1_source_preserved": True,
            "immutable_v1_reports_mutated": False,
            "immutable_v2_reports_mutated": False,
            "immutable_v3_reports_mutated": False,
            "immutable_v4_reports_mutated": False,
            "base_v5_report_only": True,
            "previous_v4_source_report_historical": True,
            "closed_owned_source_graph": True,
            "mapped_binaries_hashed_against_static_elf": True,
            "candidate_imports": "isolated guarded subprocesses only",
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    }


def _synthetic_base_report() -> dict[str, Any]:
    return {
        "postfinal_schema": BASE_AUDIT_SCHEMA,
        "audit_source_path": _owned_relative(BASE_AUDIT_SOURCE_PATH),
        "audit_source_sha256": BASE_AUDIT_SOURCE_SHA256,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "self_test": {"passed": True, "check_count": 76},
        "postfinal_wrapper_self_test": {
            "passed": True,
            "check_count": BASE_AUDIT_WRAPPER_CONTROL_COUNT,
        },
        "verified_distinct_pipeline_count": 4,
        "families": {
            "rust": {
                "native_sources": [
                    {
                        "file": "candidates/rust/src/lib.rs",
                        "sha256": RUST_SOURCE_SHA256,
                    }
                ]
            }
        },
        "native_elf_provenance": {
            "families": {
                "rust": {
                    "files": {
                        "bridge": {
                            "sha256": EXPECTED_NATIVE_FINGERPRINTS[
                                "candidates.rust_candidate:native-bridge"
                            ]
                        },
                        "engine": {
                            "sha256": EXPECTED_NATIVE_FINGERPRINTS[
                                "candidates.rust_candidate:native-engine"
                            ]
                        },
                    }
                }
            }
        },
    }


def _synthetic_campaign(
    family: str, base_report: Mapping[str, Any]
) -> dict[str, Any]:
    module = f"candidates.{family}_candidate"
    locale = _synthetic_locale_report(EXPECTED_SOURCE_FINGERPRINTS)
    locale_role = locale["roles"][family]
    sealed_static = {
        **copy.deepcopy(dict(base_report)),
        "sealed_locale_provenance": {
            "schema": OFFICIAL_LOCALE_SCHEMA,
            "path": _owned_relative(OFFICIAL_LOCALE_REPORT_PATH),
            "sha256": OFFICIAL_LOCALE_REPORT_SHA256,
            "source_path": _owned_relative(OFFICIAL_LOCALE_SOURCE_PATH),
            "source_sha256": OFFICIAL_LOCALE_SOURCE_SHA256,
            "official_methods": OFFICIAL_LOCALE_TESTS,
            "candidate_family": family,
            "all_roles": ["re", "rust", "vm", "zig"],
        },
        "sealed_no_delegation_provenance": {
            "schema": STRICT_AUDIT_SCHEMA,
            "path": _owned_relative(STRICT_AUDIT_PATH),
            "sha256": STRICT_AUDIT_SHA256,
            "source_path": _owned_relative(STRICT_AUDIT_SOURCE_PATH),
            "source_sha256": STRICT_AUDIT_SOURCE_SHA256,
            "strict_control_count": STRICT_AUDIT_CONTROL_COUNT,
            "inherited_control_count": 76,
        },
        "sealed_campaign_controller": {
            "postfinal_schema": CAMPAIGN_CONTROLLER_SCHEMA,
            "source_path": _owned_relative(RUST_CAMPAIGN_CONTROLLER_PATH),
            "source_sha256": RUST_CAMPAIGN_CONTROLLER_SHA256,
            "ancestor_source_path": _owned_relative(CAMPAIGN_ANCESTOR_PATH),
            "ancestor_source_sha256": CAMPAIGN_ANCESTOR_SHA256,
            "expected_complete_production_role_count": (
                CAMPAIGN_COMPLETE_PRODUCTION_ROLE_COUNTS[family]
            ),
        },
    }
    official = {
        "schema": "rebar-cpython-re-result-v1",
        "module": module,
        "methods": OFFICIAL_LOCALE_TESTS,
        "passed": OFFICIAL_LOCALE_TESTS,
        "skipped": 0,
        "failed": 0,
        "crashes": 0,
        "timeouts": 0,
        "runner_sha256": ORIGINAL_OFFICIAL_RUNNER_SHA256,
        "source_sha256": dict(ORIGINAL_OFFICIAL_SOURCE_HASHES),
        "records": copy.deepcopy(locale_role["records"]),
    }
    counts = {
        "candidate-frozen-edge-proof": 223_198,
        "candidate-frozen-deep-public-proof": 393,
        "frozen-cross-family-observability": 479,
        "official-cpython-tests": OFFICIAL_LOCALE_TESTS,
        "full-unicode-plane": 4_494_555,
    }
    steps = [
        {
            "name": name,
            "status": "passed",
            "passed": True,
            **({"expected_checks": counts[name]} if name in counts else {}),
            "evidence": (
                copy.deepcopy(sealed_static)
                if name == "from-scratch-static-audit"
                else copy.deepcopy(official)
                if name == "official-cpython-tests"
                else {
                    "schema": "rebar-rust-unicode-probe-v1",
                    "module": module,
                    "correctness_checks": 4_494_555,
                    "failed": 0,
                }
                if name == "full-unicode-plane"
                else {}
            ),
        }
        for name in EXPECTED_CAMPAIGN_STAGES
    ]
    return {
        "schema": "rebar-rust-campaign-gate-v1",
        "postfinal_schema": CAMPAIGN_CONTROLLER_SCHEMA,
        "controller_source_path": _owned_relative(RUST_CAMPAIGN_CONTROLLER_PATH),
        "controller_source_sha256": RUST_CAMPAIGN_CONTROLLER_SHA256,
        "ancestor_source_path": _owned_relative(CAMPAIGN_ANCESTOR_PATH),
        "ancestor_source_sha256": CAMPAIGN_ANCESTOR_SHA256,
        "candidate": module,
        "passed": True,
        "required_correctness_step_count": 22,
        "mode": "sealed-practice-only",
        "performance": "NOT MEASURED",
        "holdout_accessed": False,
        "timing_performed": False,
        "fail_fast": True,
        "pinned_cpython": "3.14.6",
        "python_version": "3.14.6",
        "goal": {
            "passed": True,
            "expected_sha256": GOAL_SHA256,
            "actual_sha256": GOAL_SHA256,
        },
        "steps": steps,
    }


def _synthetic_public_manifests() -> tuple[dict[str, Any], dict[str, Any]]:
    original_v5, document_v6 = predecessor._synthetic_public_manifests()
    del original_v5
    original = {
        **document_v6,
        "postfinal_schema": "rebar-postfinal-public-practice-plan-v6",
        "protocol_version": "postfinal-public-practice-v6",
        "runner_sha256": FROZEN_V6_SOURCE_SHA256,
    }
    document = {
        **document_v6,
        "postfinal_schema": POSTFINAL_PLAN_SCHEMA,
        "protocol_version": VERSION,
        "runner_sha256": "7" * 64,
    }
    return original, document


def _synthetic_universal_report() -> dict[str, Any]:
    families = ("rust", "vm", "zig")
    source_groups = {
        "rust": {
            path: digest
            for path, digest in EXPECTED_SOURCE_FINGERPRINTS.items()
            if path.startswith("candidates/rust/")
            or path == "candidates/rust_candidate.py"
        },
        "vm": {
            path: digest
            for path, digest in EXPECTED_SOURCE_FINGERPRINTS.items()
            if path in {"candidates/_vm_native.c", "candidates/vm_candidate.py"}
        },
        "zig": {
            path: digest
            for path, digest in EXPECTED_SOURCE_FINGERPRINTS.items()
            if path.startswith("candidates/zig/")
            or path == "candidates/zig_candidate.py"
        },
    }
    native_groups = {
        family: {
            relative: EXPECTED_NATIVE_FINGERPRINTS[role]
            for relative, role in frozen_v4.UNIVERSAL_ORACLE_NATIVE_FINGERPRINT_KEYS[
                family
            ].items()
        }
        for family in families
    }
    return {
        "schema": frozen_v4.UNIVERSAL_ORACLE_SCHEMA,
        "status": "PASS",
        "selected": "all",
        "selected_candidates": list(families),
        "completed_candidates": list(families),
        "comparison_complete": True,
        "failed_candidate": None,
        "worker_failure": None,
        "python": "3.14.6",
        "seed": 2026072417,
        "seed_domain": "rebar/python-re/universal-public/v1",
        "cases": 8_192,
        "observations_per_case": 48,
        "observations_per_candidate": 393_216,
        "total_comparisons": 1_179_648,
        "planned_total_comparisons": 1_179_648,
        "mismatches": 0,
        "grammar_family_count": 16,
        "input_stratum_count": 16,
        "examples_per_stratum": 32,
        "case_sha256": UNIVERSAL_CASE_SHA256,
        "performance": "NOT MEASURED",
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout": "NOT ACCESSED",
        "holdout_cases_read": 0,
        "external_regex_packages": 0,
        "audit": {
            "audit_path": _owned_relative(BASE_AUDIT_PATH),
            "audit_sha256": BASE_AUDIT_SHA256,
            "oracle_source_path": _owned_relative(UNIVERSAL_SOURCE_PATH),
            "oracle_source_sha256": UNIVERSAL_SOURCE_SHA256,
            "postfinal_audit_schema": BASE_AUDIT_SCHEMA,
            "postfinal_audit_source_path": _owned_relative(BASE_AUDIT_SOURCE_PATH),
            "postfinal_audit_source_sha256": BASE_AUDIT_SOURCE_SHA256,
            "postfinal_no_delegation_audit_path": _owned_relative(STRICT_AUDIT_PATH),
            "postfinal_no_delegation_audit_sha256": STRICT_AUDIT_SHA256,
            "postfinal_no_delegation_audit_schema": STRICT_AUDIT_SCHEMA,
            "postfinal_no_delegation_audit_source_path": _owned_relative(
                STRICT_AUDIT_SOURCE_PATH
            ),
            "postfinal_no_delegation_audit_source_sha256": STRICT_AUDIT_SOURCE_SHA256,
            "postfinal_no_delegation_control_count": 32,
            "postfinal_no_delegation_wrapper_control_count": (
                STRICT_AUDIT_WRAPPER_CONTROL_COUNT
            ),
            "guarded_worker_source_path": _owned_relative(IMMUTABLE_WORKER_SOURCE_PATH),
            "guarded_worker_source_sha256": IMMUTABLE_WORKER_SOURCE_SHA256,
            "guarded_worker_report_path": _owned_relative(IMMUTABLE_WORKER_REPORT_PATH),
            "guarded_worker_report_sha256": IMMUTABLE_WORKER_REPORT_SHA256,
            "official_locale_schema": OFFICIAL_LOCALE_SCHEMA,
            "official_locale_source_path": _owned_relative(OFFICIAL_LOCALE_SOURCE_PATH),
            "official_locale_source_sha256": OFFICIAL_LOCALE_SOURCE_SHA256,
            "official_locale_report_path": _owned_relative(OFFICIAL_LOCALE_REPORT_PATH),
            "official_locale_report_sha256": OFFICIAL_LOCALE_REPORT_SHA256,
            "official_locale_roles": ["re", "rust", "vm", "zig"],
            "official_locale_methods_per_role": 146,
            "official_locale_total_method_results": 584,
            "official_locale_selected_method_sha256": (
                ORIGINAL_OFFICIAL_SELECTED_METHOD_SHA256
            ),
            "official_locale_skipped": 0,
            "selected_candidates": list(families),
            "source_sha256": source_groups,
            "native_binary_sha256": native_groups,
            "previous_public_timing_evidence_read": False,
        },
        "candidate_reports": {
            family: {
                "candidate": family,
                "module": f"candidates.{family}_candidate",
                "status": "PASS",
                "cases": 8_192,
                "observations_per_case": 48,
                "checks": 393_216,
                "expected_checks": 393_216,
                "comparison_complete": True,
                "case_sha256": UNIVERSAL_CASE_SHA256,
                "mismatches": 0,
                "worker_failure": None,
                "holdout_cases_read": 0,
                "benchmark_or_timing_executed": False,
                "performance_fixtures_read": 0,
                "external_regex_packages": 0,
                "poison_guards": {
                    name: True
                    for name in (
                        {
                            "ast-candidate",
                            "cpython-sre",
                            "stdlib-re",
                            "third-party-re2",
                            "third-party-regex",
                        }
                        | {
                            f"{other}-candidate"
                            for other in families
                            if other != family
                        }
                    )
                },
            }
            for family in families
        },
    }


def _synthetic_locale_report(
    source_fingerprints: Mapping[str, str],
) -> dict[str, Any]:
    families = ("re", "rust", "vm", "zig")
    selected_methods = (
        "ReTests.test_locale_caching",
        "ReTests.test_locale_compiled",
        *(
            f"ReTests.test_synthetic_{index:03d}"
            for index in range(OFFICIAL_LOCALE_TESTS - 2)
        ),
    )
    selected_method_sha256 = hashlib.sha256(
        json.dumps(
            sorted(selected_methods),
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()
    return {
        "schema": OFFICIAL_LOCALE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "goal_sha256": GOAL_SHA256,
        "source_path": _owned_relative(OFFICIAL_LOCALE_SOURCE_PATH),
        "source_sha256": "9" * 64,
        "original_oracle": {
            "manifest_path": ORIGINAL_OFFICIAL_MANIFEST_RELATIVE,
            "manifest_sha256": ORIGINAL_OFFICIAL_MANIFEST_SHA256,
            "runner_path": ORIGINAL_OFFICIAL_RUNNER_RELATIVE,
            "runner_sha256": ORIGINAL_OFFICIAL_RUNNER_SHA256,
            "source_sha256": dict(ORIGINAL_OFFICIAL_SOURCE_HASHES),
            "total_public_methods": 152,
            "selected_methods": OFFICIAL_LOCALE_TESTS,
            "selected_method_sha256": selected_method_sha256,
            "named_waivers": dict(ORIGINAL_OFFICIAL_PRIVATE_METHOD_WAIVERS),
            "named_class_waivers": dict(ORIGINAL_OFFICIAL_PRIVATE_CLASS_WAIVERS),
            "all_named_waivers": (
                ORIGINAL_OFFICIAL_PRIVATE_METHOD_WAIVERS
                | ORIGINAL_OFFICIAL_PRIVATE_CLASS_WAIVERS
            ),
            "corpus_cases": 403,
        },
        "audits": {
            "from_scratch": {
                "path": _owned_relative(BASE_AUDIT_PATH),
                "sha256": BASE_AUDIT_SHA256,
                "postfinal_schema": BASE_AUDIT_SCHEMA,
                "source_path": _owned_relative(BASE_AUDIT_SOURCE_PATH),
                "source_sha256": BASE_AUDIT_SOURCE_SHA256,
            },
            "no_delegation": {
                "path": _owned_relative(STRICT_AUDIT_PATH),
                "sha256": STRICT_AUDIT_SHA256,
                "postfinal_schema": STRICT_AUDIT_SCHEMA,
                "source_path": _owned_relative(STRICT_AUDIT_SOURCE_PATH),
                "source_sha256": STRICT_AUDIT_SOURCE_SHA256,
            },
        },
        "qualified_source_fingerprints": dict(source_fingerprints),
        "native_elf_fingerprints": dict(EXPECTED_NATIVE_FINGERPRINTS),
        "holdout_accessed": False,
        "timing_performed": False,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
        "locales": {
            "private": True,
            "genuine": True,
            "iso88591": {
                "name": "en_US.iso88591",
                "source_sha256": "f" * 64,
                "charmap_sha256": "1" * 64,
            },
            "utf8": {
                "name": "en_US.utf8",
                "source_sha256": "2" * 64,
                "charmap_sha256": "3" * 64,
            },
        },
        "locale_reference": {
            "status": "PASS",
            "python": "3.14.6",
            "genuine_locales": True,
            "compiled_locale_switch": True,
            "candidate_modules_loaded": False,
            "holdout_accessed": False,
            "timing_performed": False,
        },
        "roles": {
            family: {
                "module": "re" if family == "re" else f"candidates.{family}_candidate",
                "methods": OFFICIAL_LOCALE_TESTS,
                "passed": OFFICIAL_LOCALE_TESTS,
                "failed": 0,
                "failures": 0,
                "errors": 0,
                "skipped": 0,
                "crashes": 0,
                "timeouts": 0,
                "locale_caching_passed": True,
                "locale_compiled_passed": True,
                "records": [
                    {
                        "test": name,
                        "status": "passed",
                        "skipped": 0,
                        "reason": None,
                    }
                    for name in selected_methods
                ],
            }
            for family in families
        },
    }


def _synthetic_stage10_documents() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    Any,
    str,
    str,
]:
    """Build the complete public proof in memory without running an engine."""

    families = ("rust", "vm", "zig")
    records = [
        {"id": f"{cohort}:{index:04d}", "cohort": cohort, "value": index}
        for cohort, count in STAGE10_COHORT_COUNTS.items()
        for index in range(count)
    ]

    def record_digest(items: Any) -> str:
        return hashlib.sha256(
            json.dumps(
                items,
                sort_keys=True,
                ensure_ascii=True,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("ascii")
        ).hexdigest()

    reference_digest = record_digest(records)
    metadata_digest = hashlib.sha256(
        b"rebar/public-development/v7/synthetic-stage10-metadata"
    ).hexdigest()
    sources = {
        "rust": {
            path: digest
            for path, digest in EXPECTED_SOURCE_FINGERPRINTS.items()
            if path.startswith("candidates/rust/")
            or path == "candidates/rust_candidate.py"
        },
        "vm": {
            path: digest
            for path, digest in EXPECTED_SOURCE_FINGERPRINTS.items()
            if path in {"candidates/_vm_native.c", "candidates/vm_candidate.py"}
        },
        "zig": {
            path: digest
            for path, digest in EXPECTED_SOURCE_FINGERPRINTS.items()
            if path.startswith("candidates/zig/")
            or path == "candidates/zig_candidate.py"
        },
    }
    natives = {
        family: {
            relative: EXPECTED_NATIVE_FINGERPRINTS[role]
            for relative, role in frozen_v4.UNIVERSAL_ORACLE_NATIVE_FINGERPRINT_KEYS[
                family
            ].items()
        }
        for family in families
    }
    provenance: dict[str, Any] = {
        "source_path": _owned_relative(STAGE10_SOURCE_PATH),
        "source_sha256": STAGE10_SOURCE_SHA256,
        "protocol_path": _owned_relative(STAGE10_PROTOCOL_PATH),
        "protocol_sha256": STAGE10_PROTOCOL_SHA256,
        "observation_domain": STAGE10_OBSERVATION_DOMAIN,
        "base_audit_path": _owned_relative(BASE_AUDIT_PATH),
        "base_audit_sha256": BASE_AUDIT_SHA256,
        "strict_audit_path": _owned_relative(STRICT_AUDIT_PATH),
        "strict_audit_sha256": STRICT_AUDIT_SHA256,
        "official_locale_path": _owned_relative(OFFICIAL_LOCALE_REPORT_PATH),
        "official_locale_sha256": OFFICIAL_LOCALE_REPORT_SHA256,
        "official_methods_per_role": OFFICIAL_LOCALE_TESTS,
        "official_role_count": 4,
        "official_skipped": 0,
        "official_selected_method_sha256": ORIGINAL_OFFICIAL_SELECTED_METHOD_SHA256,
        "previous_public_source_sha256": UNIVERSAL_SOURCE_SHA256,
        "previous_public_report_path": _owned_relative(UNIVERSAL_REPORT_PATH),
        "previous_public_report_sha256": UNIVERSAL_REPORT_SHA256,
        "previous_public_cases": 8_192,
        "previous_public_comparisons": 1_179_648,
        "previous_failed_source_path": _owned_relative(PRESERVED_STAGE07_SOURCE_PATH),
        "previous_failed_source_sha256": PRESERVED_STAGE07_SOURCE_SHA256,
        "previous_failed_protocol_path": _owned_relative(
            PRESERVED_STAGE07_PROTOCOL_PATH
        ),
        "previous_failed_protocol_sha256": PRESERVED_STAGE07_PROTOCOL_SHA256,
        "previous_self_oracle_failure_path": _owned_relative(
            PRESERVED_STAGE07_FAILURE_PATH
        ),
        "previous_self_oracle_failure_sha256": PRESERVED_STAGE07_FAILURE_SHA256,
        "previous_self_oracle_failure_count": 32,
        "previous_hash_nondeterminism_only": True,
        "previous_stage08_source_path": _owned_relative(PRESERVED_STAGE08_SOURCE_PATH),
        "previous_stage08_source_sha256": PRESERVED_STAGE08_SOURCE_SHA256,
        "previous_stage08_protocol_path": _owned_relative(
            PRESERVED_STAGE08_PROTOCOL_PATH
        ),
        "previous_stage08_protocol_sha256": PRESERVED_STAGE08_PROTOCOL_SHA256,
        "previous_stage08_self_oracle_path": _owned_relative(
            PRESERVED_STAGE08_SELF_ORACLE_PATH
        ),
        "previous_stage08_self_oracle_sha256": PRESERVED_STAGE08_SELF_ORACLE_SHA256,
        "previous_stage08_rust_failure_path": _owned_relative(
            PRESERVED_STAGE08_RUST_FAILURE_PATH
        ),
        "previous_stage08_rust_failure_sha256": PRESERVED_STAGE08_RUST_FAILURE_SHA256,
        "previous_stage08_rust_failure_count": 256,
        "previous_stage08_rust_matching_observations": 3_328,
        "previous_stage08_rust_failure_preserved": True,
        "source_sha256_by_family": sources,
        "native_sha256_by_family": natives,
    }
    locales = {"synthetic": True, "genuine_production_report_read": False}
    reference: dict[str, Any] = {
        "schema": STAGE10_SELF_ORACLE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": _owned_relative(STAGE10_SOURCE_PATH),
        "source_sha256": STAGE10_SOURCE_SHA256,
        "protocol_path": _owned_relative(STAGE10_PROTOCOL_PATH),
        "protocol_sha256": STAGE10_PROTOCOL_SHA256,
        "seed": STAGE10_SEED,
        "seed_domain": STAGE10_SEED_DOMAIN,
        "matrix_sha256": STAGE10_MATRIX_SHA256,
        "cohorts": len(STAGE10_COHORT_COUNTS),
        "cohort_cases": dict(STAGE10_COHORT_COUNTS),
        "cases": STAGE10_CASES,
        "stdlib_checks": 2 * STAGE10_CASES,
        "mismatches": 0,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "failure_records": [],
        "baseline_records": records,
        "baseline_record_sha256": reference_digest,
        "second_record_sha256": reference_digest,
        "current_provenance": provenance,
        "locales": locales,
    }
    bridge_modules = {
        "rust": "candidates._rust_bridge",
        "vm": "candidates._vm_native",
        "zig": "candidates._zig_bridge",
    }
    reports: dict[str, Any] = {}
    for family in families:
        reports[family] = {
            "candidate": family,
            "module": f"candidates.{family}_candidate",
            "status": "PASS",
            "cases": STAGE10_CASES,
            "cohort_cases": dict(STAGE10_COHORT_COUNTS),
            "record_sha256": reference_digest,
            "mismatches": 0,
            "failure_records": [],
            "failures_recorded": 0,
            "benchmark_or_timing_executed": False,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
            "native_binary_sha256": natives[family],
            "guard": {
                "enabled": True,
                "family": family,
                "stdlib_re_blocked": True,
                "cpython_sre_blocked": True,
                "third_party_regex_blocked": True,
                "cross_family_blocked": True,
                "foreign_dynamic_libraries_blocked": True,
                "native_loader_aliases_blocked": list(
                    STAGE10_BLOCKED_NATIVE_LOADER_ALIASES
                ),
                "cached_regex_aliases_poisoned": 1,
                "loaded_candidate_modules": sorted(
                    (f"candidates.{family}_candidate", bridge_modules[family])
                ),
                "isolated_public_metadata": {
                    "enabled": True,
                    "schema": STAGE10_METADATA_SCHEMA,
                    "source_sha256": STAGE10_SOURCE_SHA256,
                    "role": family,
                    "surface_cases": 256,
                    "record_sha256": metadata_digest,
                    "production_matching_executed": False,
                    "metadata_and_matcher_processes_distinct": True,
                    "matcher_inspect_loaded": False,
                    "matcher_tokenizer_loaded": False,
                },
            },
        }
    all_candidates: dict[str, Any] = {
        "schema": STAGE10_ALL_CANDIDATE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "selected": "all",
        "comparison_complete": True,
        "python": "3.14.6",
        "source_path": _owned_relative(STAGE10_SOURCE_PATH),
        "source_sha256": STAGE10_SOURCE_SHA256,
        "protocol_path": _owned_relative(STAGE10_PROTOCOL_PATH),
        "protocol_sha256": STAGE10_PROTOCOL_SHA256,
        "seed": STAGE10_SEED,
        "seed_domain": STAGE10_SEED_DOMAIN,
        "matrix_sha256": STAGE10_MATRIX_SHA256,
        "cohorts": len(STAGE10_COHORT_COUNTS),
        "cohort_cases": dict(STAGE10_COHORT_COUNTS),
        "cases_per_candidate": STAGE10_CASES,
        "candidate_checks": 3 * STAGE10_CASES,
        "previous_public_cases": 8_192,
        "previous_public_comparisons": 1_179_648,
        "combined_public_comparisons": 1_179_648 + 3 * STAGE10_CASES,
        "mismatches": 0,
        "self_oracle_path": _owned_relative(STAGE10_SELF_ORACLE_PATH),
        "self_oracle_sha256": STAGE10_SELF_ORACLE_SHA256,
        "external_regex_packages": 0,
        "candidate_cross_delegation": False,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
        "selected_candidates": list(families),
        "completed_candidates": list(families),
        "current_provenance": provenance,
        "locales": locales,
        "candidate_reports": reports,
    }
    return (
        reference,
        all_candidates,
        provenance,
        record_digest,
        reference_digest,
        metadata_digest,
    )


def synthetic_self_test() -> dict[str, Any]:
    """Reject synthetic poisons without files, entropy, workers, or timing."""

    frozen_v4.require_candidate_free()
    frozen_v4.require_pinned_python()
    controls: list[dict[str, Any]] = []

    def forbidden(*_args: Any, **_kwargs: Any) -> Any:
        raise RuntimeError("the candidate-free V7 self-test attempted external I/O")

    def synthetic_owned_source(value: str, _label: str) -> Path:
        frozen_v4.require(
            value == "pyproject.toml",
            "the synthetic candidate-free owned-source path was substituted",
        )
        return ROOT / "pyproject.toml"

    def reject(name: str, action: Any) -> None:
        try:
            action()
        except (
            RuntimeError,
            frozen_v4.replay.AuditError,
            AssertionError,
            KeyError,
            TypeError,
            ValueError,
            OverflowError,
            RecursionError,
        ):
            controls.append({"name": name, "passed": True})
            return
        raise RuntimeError(f"public V7 synthetic poison was accepted: {name}")

    with ExitStack() as guards:
        for target, attribute in (
            (subprocess, "Popen"),
            (subprocess, "run"),
            (os, "urandom"),
            (time, "time"),
            (time, "time_ns"),
            (time, "perf_counter"),
            (time, "perf_counter_ns"),
            (time, "monotonic"),
            (time, "monotonic_ns"),
            (frozen_v4, "read_json"),
            (frozen_v4.pilot, "file_sha256"),
            (frozen_v4.pilot, "load_calibration_fixture"),
            (Path, "open"),
        ):
            guards.enter_context(mock.patch.object(target, attribute, side_effect=forbidden))
        guards.enter_context(mock.patch("builtins.open", side_effect=forbidden))
        guards.enter_context(
            mock.patch.object(
                frozen_v4, "checked_owned_source", side_effect=synthetic_owned_source
            )
        )
        synthetic_campaign_digests = {
            family: hashlib.sha256(
                f"rebar/public-development/v7/synthetic-sealed-campaign/{family}".encode(
                    "ascii"
                )
            ).hexdigest()
            for family in ("rust", "vm", "zig")
        }
        guards.enter_context(
            mock.patch.dict(
                PROOF_SHA256,
                {
                    f"{family}-complete-correctness-campaign": digest
                    for family, digest in synthetic_campaign_digests.items()
                },
            )
        )
        for family, constant in (
            ("rust", "RUST_CAMPAIGN_SHA256"),
            ("vm", "VM_CAMPAIGN_SHA256"),
            ("zig", "ZIG_CAMPAIGN_SHA256"),
        ):
            guards.enter_context(
                mock.patch(
                    f"{__name__}.{constant}",
                    synthetic_campaign_digests[family],
                )
            )
        _require_complete_campaign_pins()

        def poisoned_campaign_pin(role: str, value: str | None) -> None:
            with mock.patch.dict(PROOF_SHA256, {role: value}):
                _require_complete_campaign_pins()

        for family in ("rust", "vm", "zig"):
            role = f"{family}-complete-correctness-campaign"
            reject(
                f"unproduced-{family}-v5-campaign-digest",
                lambda selected=role: poisoned_campaign_pin(selected, None),
            )
            other = "vm" if family == "rust" else "rust"
            reject(
                f"cross-family-{family}-v5-campaign-digest",
                lambda selected=role, wrong=other: poisoned_campaign_pin(
                    selected, synthetic_campaign_digests[wrong]
                ),
            )
        inherited = _ORIGINAL_SELF_TEST()
        frozen_v4.require(
            inherited.get("result") == "PASS"
            and inherited.get("protocol_version") == VERSION
            and inherited.get("schema") == POSTFINAL_INTEGRITY_SCHEMA + "-self-test"
            and inherited.get("candidate_imported") is False
            and inherited.get("holdout_accessed") is False
            and inherited.get("held_out_cases_generated") == 0
            and inherited.get("held_out_records_deserialized") == 0
            and inherited.get("timing_performed") is False
            and inherited.get("failed") == 0
            and inherited.get("prospective_cases") == 8_192
            and inherited.get("synthetic_public_operations") == 12
            and inherited.get("prospective_stage05_correctness_artifact_count") == 12
            and inherited.get("prospective_stage05_fresh_edge_proof_count") == 3
            and inherited.get("prospective_universal_oracle_proof_field_count") == 23
            and inherited.get("prospective_stage05_deep_family_mapping")
            == {"rust": "RUST", "vm": "C", "zig": "ZIG"}
            and inherited.get("owned_source_poisoned_control_count") == 4
            and inherited.get("postfinal_poisoned_control_count") == 10,
            "the immutable inherited candidate-free public poison controls failed",
        )

        (
            stage10_reference,
            stage10_all,
            stage10_provenance,
            stage10_record_digest,
            synthetic_reference_digest,
            synthetic_metadata_digest,
        ) = _synthetic_stage10_documents()
        _validate_stage10_documents(
            stage10_reference,
            stage10_all,
            stage10_provenance,
            record_digest=stage10_record_digest,
            reference_digest=synthetic_reference_digest,
            metadata_digest=synthetic_metadata_digest,
        )

        def poison_stage10(
            mutation: Any,
            *,
            observed_self_sha256: str = STAGE10_SELF_ORACLE_SHA256,
            observed_all_sha256: str = STAGE10_ALL_CANDIDATE_SHA256,
        ) -> None:
            reference, reports, provenance = copy.deepcopy(
                (stage10_reference, stage10_all, stage10_provenance)
            )
            mutation(reference, reports, provenance)
            _validate_stage10_documents(
                reference,
                reports,
                provenance,
                record_digest=stage10_record_digest,
                reference_digest=synthetic_reference_digest,
                metadata_digest=synthetic_metadata_digest,
                observed_self_sha256=observed_self_sha256,
                observed_all_sha256=observed_all_sha256,
            )

        for name, mutation in (
            (
                "stage10-substituted-producer-source",
                lambda _reference, _reports, provenance: provenance.update(
                    source_sha256="0" * 64
                ),
            ),
            (
                "stage10-substituted-public-protocol",
                lambda _reference, _reports, provenance: provenance.update(
                    protocol_sha256="0" * 64
                ),
            ),
            (
                "stage10-concealed-v7-reference-failure",
                lambda _reference, _reports, provenance: provenance.update(
                    previous_self_oracle_failure_count=0
                ),
            ),
            (
                "stage10-substituted-v7-reference-failure",
                lambda _reference, _reports, provenance: provenance.update(
                    previous_self_oracle_failure_sha256="0" * 64
                ),
            ),
            (
                "stage10-concealed-v8-observer-failure",
                lambda _reference, _reports, provenance: provenance.update(
                    previous_stage08_rust_failure_count=0
                ),
            ),
            (
                "stage10-substituted-v8-observer-failure",
                lambda _reference, _reports, provenance: provenance.update(
                    previous_stage08_rust_failure_sha256="0" * 64
                ),
            ),
            (
                "stage10-undisclosed-v8-observer-failure",
                lambda _reference, _reports, provenance: provenance.update(
                    previous_stage08_rust_failure_preserved=False
                ),
            ),
            (
                "stage10-substituted-self-oracle-source",
                lambda reference, _reports, _provenance: reference.update(
                    source_sha256="0" * 64
                ),
            ),
            (
                "stage10-weakened-self-oracle-denominator",
                lambda reference, _reports, _provenance: reference.update(
                    stdlib_checks=STAGE10_CASES
                ),
            ),
            (
                "stage10-substituted-baseline-record-digest",
                lambda reference, _reports, _provenance: reference.update(
                    baseline_record_sha256="0" * 64
                ),
            ),
            (
                "stage10-lost-independent-python-reference",
                lambda reference, _reports, _provenance: reference.update(
                    independent_stdlib_roles=["stdlib-a"]
                ),
            ),
            (
                "stage10-omitted-reference-case",
                lambda reference, _reports, _provenance: reference[
                    "baseline_records"
                ].pop(),
            ),
            (
                "stage10-duplicated-reference-case",
                lambda reference, _reports, _provenance: reference[
                    "baseline_records"
                ].__setitem__(1, copy.deepcopy(reference["baseline_records"][0])),
            ),
            (
                "stage10-premature-self-oracle-timing",
                lambda reference, _reports, _provenance: reference.update(
                    benchmark_or_timing_executed=True
                ),
            ),
            (
                "stage10-self-oracle-opened-holdout",
                lambda reference, _reports, _provenance: reference.update(
                    holdout_cases_read=1
                ),
            ),
            (
                "stage10-substituted-public-matrix",
                lambda _reference, reports, _provenance: reports.update(
                    matrix_sha256="0" * 64
                ),
            ),
            (
                "stage10-weakened-three-family-denominator",
                lambda _reference, reports, _provenance: reports.update(
                    candidate_checks=2 * STAGE10_CASES
                ),
            ),
            (
                "stage10-hidden-historical-comparisons",
                lambda _reference, reports, _provenance: reports.update(
                    combined_public_comparisons=3 * STAGE10_CASES
                ),
            ),
            (
                "stage10-undisclosed-external-regex-package",
                lambda _reference, reports, _provenance: reports.update(
                    external_regex_packages=1
                ),
            ),
            (
                "stage10-undisclosed-cross-family-delegation",
                lambda _reference, reports, _provenance: reports.update(
                    candidate_cross_delegation=True
                ),
            ),
            (
                "stage10-omitted-independent-family",
                lambda _reference, reports, _provenance: reports[
                    "candidate_reports"
                ].pop("zig"),
            ),
            (
                "stage10-premature-three-family-timing",
                lambda _reference, reports, _provenance: reports.update(
                    benchmark_or_timing_executed=True
                ),
            ),
            (
                "stage10-three-family-opened-holdout",
                lambda _reference, reports, _provenance: reports.update(
                    holdout_cases_read=1
                ),
            ),
        ):
            reject(name, lambda change=mutation: poison_stage10(change))

        for family in ("rust", "vm", "zig"):
            for suffix, mutation in (
                (
                    "hidden-mismatch",
                    lambda report: report.update(mismatches=1),
                ),
                (
                    "substituted-native-engine",
                    lambda report: report.update(native_binary_sha256={}),
                ),
                (
                    "unblocked-native-loader-alias",
                    lambda report: report["guard"][
                        "native_loader_aliases_blocked"
                    ].pop(),
                ),
                (
                    "unpoisoned-cached-regex-alias",
                    lambda report: report["guard"].update(
                        cached_regex_aliases_poisoned=0
                    ),
                ),
                (
                    "substituted-loaded-candidate-module",
                    lambda report: report["guard"].update(
                        loaded_candidate_modules=["candidates.foreign_candidate"]
                    ),
                ),
                (
                    "shared-matcher-and-metadata-process",
                    lambda report: report["guard"]["isolated_public_metadata"].update(
                        metadata_and_matcher_processes_distinct=False
                    ),
                ),
                (
                    "metadata-executed-production-matching",
                    lambda report: report["guard"]["isolated_public_metadata"].update(
                        production_matching_executed=True
                    ),
                ),
                (
                    "matcher-loaded-inspection",
                    lambda report: report["guard"]["isolated_public_metadata"].update(
                        matcher_inspect_loaded=True
                    ),
                ),
                (
                    "matcher-loaded-tokenizer",
                    lambda report: report["guard"]["isolated_public_metadata"].update(
                        matcher_tokenizer_loaded=True
                    ),
                ),
                (
                    "substituted-metadata-receipt",
                    lambda report: report["guard"]["isolated_public_metadata"].update(
                        record_sha256="0" * 64
                    ),
                ),
                (
                    "substituted-metadata-observer-role",
                    lambda report: report["guard"]["isolated_public_metadata"].update(
                        role="foreign"
                    ),
                ),
            ):
                reject(
                    f"stage10-{family}-{suffix}",
                    lambda role=family, change=mutation: poison_stage10(
                        lambda _reference, reports, _provenance: change(
                            reports["candidate_reports"][role]
                        )
                    ),
                )

        reject(
            "stage10-substituted-self-oracle-report-fingerprint",
            lambda: poison_stage10(
                lambda _reference, _reports, _provenance: None,
                observed_self_sha256="0" * 64,
            ),
        )
        reject(
            "stage10-substituted-three-family-report-fingerprint",
            lambda: poison_stage10(
                lambda _reference, _reports, _provenance: None,
                observed_all_sha256="0" * 64,
            ),
        )

        expected_paths = MIXED_CORRECTNESS_PATHS
        families = ("rust", "vm", "zig")
        mapping = {"rust": "RUST", "vm": "C", "zig": "ZIG"}

        def check_paths(
            paths: tuple[tuple[str, Path], ...] = expected_paths,
            edges: tuple[Path, ...] = MIXED_EDGE_ORACLES,
            candidates: tuple[str, ...] = families,
            deep_mapping: Mapping[str, str] = mapping,
        ) -> None:
            _validate_proof_contract(paths, edges, candidates, deep_mapping)

        check_paths()
        old_paths = dict(predecessor.MIXED_CORRECTNESS_PATHS)
        for name, action in (
            ("missing-current-rust-proof", lambda: check_paths(paths=expected_paths[1:])),
            (
                "rejected-preliminary-rust-v1-campaign",
                lambda: check_paths(
                    paths=(
                        *expected_paths[:3],
                        ("rust-complete-correctness-campaign", REJECTED_RUST_CAMPAIGN_PATH),
                        *expected_paths[4:],
                    )
                ),
            ),
            (
                "stale-v6-rust-edge-proof",
                lambda: check_paths(
                    paths=(("rust-edge", old_paths["rust-edge"]), *expected_paths[1:])
                ),
            ),
            (
                "stale-v6-rust-deep-proof",
                lambda: check_paths(
                    paths=(
                        expected_paths[0],
                        ("rust-deep-public-contract", old_paths["rust-deep-public-contract"]),
                        *expected_paths[2:],
                    )
                ),
            ),
            (
                "cross-family-rust-edge-proof",
                lambda: check_paths(
                    paths=(
                        ("rust-edge", dict(expected_paths)["vm-edge"]),
                        *expected_paths[1:],
                    )
                ),
            ),
            (
                "reordered-independent-proofs",
                lambda: check_paths(
                    paths=(expected_paths[1], expected_paths[0], *expected_paths[2:])
                ),
            ),
            ("missing-independent-edge", lambda: check_paths(edges=MIXED_EDGE_ORACLES[:2])),
            (
                "reordered-independent-edges",
                lambda: check_paths(edges=tuple(reversed(MIXED_EDGE_ORACLES))),
            ),
            ("missing-independent-family", lambda: check_paths(candidates=("rust", "vm"))),
            (
                "swapped-native-family",
                lambda: check_paths(
                    deep_mapping={"rust": "C", "vm": "RUST", "zig": "ZIG"}
                ),
            ),
        ):
            reject(name, action)

        runtime = _synthetic_runtime_report()
        _validated_runtime_provenance(runtime)
        runtime_poisons = (
            ("stale-v2-isolation-schema", {"schema": "rebar-postfinal-no-delegation-audit-v2"}),
            ("stale-v1-worker-as-v5-audit", {"schema": IMMUTABLE_WORKER_SCHEMA}),
            ("failed-v5-isolation", {"passed": False}),
            ("stale-v5-isolation-source", {"audit_source_sha256": "0" * 64}),
            ("stale-v5-base-report", {"base_audit_report_sha256": "0" * 64}),
            ("stale-v5-base-source", {"base_audit_source_sha256": "0" * 64}),
            ("weakened-inherited-76-controls", {"inherited_control_count": 75}),
            ("weakened-v5-32-controls", {"self_test": {"passed": True, "check_count": 31, "failed": []}}),
            ("hidden-v5-control-failure", {"self_test": {"passed": True, "check_count": 32, "failed": ["poison"]}}),
            ("stale-v3-strict-history", {"previous_v3_audit_report_sha256": "0" * 64}),
            ("stale-v4-strict-history", {"previous_v4_audit_source_sha256": "0" * 64}),
            ("substituted-historical-v4-report", {"previous_v4_source_report_sha256": "0" * 64}),
            ("invented-historical-v4-strict-report", {"previous_v4_strict_report_created": True}),
            ("weakened-676-v5-controls", {"postfinal_wrapper_self_test": {**runtime["postfinal_wrapper_self_test"], "check_count": 675}}),
            ("failing-676-v5-controls", {"postfinal_wrapper_self_test": {**runtime["postfinal_wrapper_self_test"], "passed": False}}),
            ("omitted-native-engine", {"native_elf_fingerprints": {key: value for key, value in EXPECTED_NATIVE_FINGERPRINTS.items() if "rust_candidate:native-engine" not in key}}),
            ("changed-native-engine", {"native_elf_fingerprints": {**EXPECTED_NATIVE_FINGERPRINTS, "candidates.rust_candidate:native-engine": "0" * 64}}),
            ("omitted-qualified-source", {"qualified_source_fingerprints": {f"synthetic/source-{index:02d}.py": "a" * 64 for index in range(11)}}),
        )
        for name, change in runtime_poisons:
            reject(name, lambda delta=change: _validated_runtime_provenance({**runtime, **delta}))
        worker = _validated_runtime_provenance(runtime)
        _validate_immutable_guarded_worker(worker)
        for name, field, value in (
            ("foreign-immutable-worker-source", "postfinal_guarded_worker_source_path", "/foreign.py"),
            ("changed-immutable-worker-source", "postfinal_guarded_worker_source_sha256", "0" * 64),
            ("changed-immutable-worker-report-path", "postfinal_guarded_worker_report_path", "/foreign.json"),
            ("changed-immutable-worker-report", "postfinal_guarded_worker_report_sha256", "0" * 64),
            ("changed-immutable-worker-schema", "postfinal_guarded_worker_schema", "foreign"),
        ):
            reject(
                name,
                lambda key=field, item=value: _validate_immutable_guarded_worker(
                    {**worker, key: item}
                ),
            )
        for name, key, value in (
            ("worker-opened-holdout", "holdout_or_case_fixture_access", True),
            ("worker-started-timing", "benchmark_or_timing_executed", True),
            ("unavailable-guarded-worker", "persistent_measurement_worker_available", False),
            ("weakened-native-mapping-guard", "mapped_binaries_hashed_against_static_elf", False),
            ("foreign-candidate-import-policy", "candidate_imports", "unrestricted"),
            ("mutated-v2-audit-history", "immutable_v2_reports_mutated", True),
        ):
            reject(
                name,
                lambda field=key, item=value: _validated_runtime_provenance(
                    {**runtime, "scope": {**runtime["scope"], field: item}}
                ),
            )

        base = _synthetic_base_report()
        rust = _synthetic_campaign("rust", base)
        synthetic_campaign_selected_method_sha256 = _synthetic_locale_report(
            EXPECTED_SOURCE_FINGERPRINTS
        )["original_oracle"]["selected_method_sha256"]
        _validate_campaign_document(
            rust,
            "candidates.rust_candidate",
            RUST_CAMPAIGN_SHA256,
            base_report=base,
            controller_sha256=RUST_CAMPAIGN_CONTROLLER_SHA256,
            expected_selected_method_sha256=(
                synthetic_campaign_selected_method_sha256
            ),
        )

        for family in ("rust", "vm", "zig"):
            family_module = f"candidates.{family}_candidate"
            family_campaign = rust if family == "rust" else _synthetic_campaign(
                family, base
            )
            family_digest = synthetic_campaign_digests[family]
            _validate_campaign_document(
                family_campaign,
                family_module,
                family_digest,
                base_report=base,
                controller_sha256=RUST_CAMPAIGN_CONTROLLER_SHA256,
                expected_selected_method_sha256=(
                    synthetic_campaign_selected_method_sha256
                ),
            )

            def reject_family_campaign(
                name: str,
                mutation: Any,
                *,
                document: Mapping[str, Any] = family_campaign,
                module: str = family_module,
                digest: str = family_digest,
            ) -> None:
                def validate_poison() -> None:
                    changed = copy.deepcopy(document)
                    mutation(changed)
                    _validate_campaign_document(
                        changed,
                        module,
                        digest,
                        base_report=base,
                        controller_sha256=RUST_CAMPAIGN_CONTROLLER_SHA256,
                        expected_selected_method_sha256=(
                            synthetic_campaign_selected_method_sha256
                        ),
                    )

                reject(f"{family}-{name}", validate_poison)

            for field, value, suffix in (
                ("postfinal_schema", "foreign", "foreign-v5-campaign-schema"),
                (
                    "controller_source_path",
                    "tools/foreign_campaign_controller.py",
                    "foreign-v5-campaign-controller-path",
                ),
                (
                    "controller_source_sha256",
                    "0" * 64,
                    "foreign-v5-campaign-controller-digest",
                ),
                (
                    "ancestor_source_path",
                    "tools/foreign_ancestor.py",
                    "foreign-v5-campaign-ancestor-path",
                ),
                (
                    "ancestor_source_sha256",
                    "0" * 64,
                    "foreign-v5-campaign-ancestor-digest",
                ),
            ):
                reject_family_campaign(
                    suffix,
                    lambda document, key=field, item=value: document.update(
                        {key: item}
                    ),
                )

            for field, value, suffix in (
                (
                    "postfinal_schema",
                    "foreign",
                    "foreign-v5-static-controller-schema",
                ),
                (
                    "source_path",
                    "tools/foreign_campaign_controller.py",
                    "foreign-v5-static-controller-path",
                ),
                (
                    "source_sha256",
                    "0" * 64,
                    "foreign-v5-static-controller-digest",
                ),
                (
                    "ancestor_source_path",
                    "tools/foreign_ancestor.py",
                    "foreign-v5-static-ancestor-path",
                ),
                (
                    "ancestor_source_sha256",
                    "0" * 64,
                    "foreign-v5-static-ancestor-digest",
                ),
                (
                    "expected_complete_production_role_count",
                    0,
                    "weakened-v5-complete-production-role-count",
                ),
            ):
                reject_family_campaign(
                    suffix,
                    lambda document, key=field, item=value: document["steps"][0][
                        "evidence"
                    ]["sealed_campaign_controller"].update({key: item}),
                )
            reject_family_campaign(
                "missing-v5-static-controller",
                lambda document: document["steps"][0]["evidence"].pop(
                    "sealed_campaign_controller"
                ),
            )

        def poisoned_campaign(
            mutate: Any,
            *,
            digest: str = RUST_CAMPAIGN_SHA256,
            producer: str = RUST_CAMPAIGN_CONTROLLER_SHA256,
            current_base: Mapping[str, Any] = base,
            selected_methods: str = synthetic_campaign_selected_method_sha256,
        ) -> None:
            changed = copy.deepcopy(rust)
            mutate(changed)
            _validate_campaign_document(
                changed,
                "candidates.rust_candidate",
                digest,
                base_report=current_base,
                controller_sha256=producer,
                expected_selected_method_sha256=selected_methods,
            )

        for name, mutate in (
            ("failed-rust-campaign", lambda item: item.update(passed=False)),
            ("foreign-rust-campaign", lambda item: item.update(candidate="candidates.zig_candidate")),
            ("wrong-rust-campaign-schema", lambda item: item.update(schema="foreign")),
            ("missing-sealed-campaign-step", lambda item: item["steps"].pop()),
            ("weakened-sealed-campaign-count", lambda item: item.update(required_correctness_step_count=21)),
            ("reordered-sealed-campaign", lambda item: item["steps"].reverse()),
            ("failed-sealed-campaign-step", lambda item: item["steps"][4].update(passed=False)),
            ("hidden-sealed-campaign-stage-failure", lambda item: item["steps"][4].update(status="failed")),
            ("weakened-edge-checks", lambda item: item["steps"][3].update(expected_checks=223_197)),
            ("weakened-deep-checks", lambda item: item["steps"][4].update(expected_checks=392)),
            ("weakened-observability-checks", lambda item: item["steps"][9].update(expected_checks=478)),
            ("weakened-145-official-cpython-checks", lambda item: item["steps"][12].update(expected_checks=145)),
            ("rejected-144-official-cpython-checks", lambda item: item["steps"][12].update(expected_checks=144)),
            ("weakened-unicode-stage-count", lambda item: item["steps"][-1].update(expected_checks=4_494_554)),
            ("weakened-unicode-actual-count", lambda item: item["steps"][-1]["evidence"].update(correctness_checks=4_494_554)),
            ("hidden-unicode-failure", lambda item: item["steps"][-1]["evidence"].update(failed=1)),
            ("foreign-unicode-candidate", lambda item: item["steps"][-1]["evidence"].update(module="candidates.zig_candidate")),
            ("changed-original-goal", lambda item: item["goal"].update(actual_sha256="0" * 64)),
            ("campaign-opened-holdout", lambda item: item.update(holdout_accessed=True)),
            ("campaign-started-timing", lambda item: item.update(timing_performed=True)),
            ("campaign-disabled-fail-fast", lambda item: item.update(fail_fast=False)),
            ("rejected-v2-base-source", lambda item: item["steps"][0]["evidence"].update(audit_source_sha256="0" * 64)),
        ):
            reject(name, lambda operation=mutate: poisoned_campaign(operation))
        reject(
            "accepted-preliminary-v1-report-fingerprint",
            lambda: poisoned_campaign(lambda _item: None, digest=REJECTED_RUST_CAMPAIGN_SHA256),
        )
        reject(
            "accepted-archived-v4-rust-report-fingerprint",
            lambda: poisoned_campaign(
                lambda _item: None,
                digest=REJECTED_ARCHIVED_RUST_V4_CAMPAIGN_SHA256,
            ),
        )
        reject(
            "accepted-foreign-hardened-producer",
            lambda: poisoned_campaign(lambda _item: None, producer="0" * 64),
        )

        universal = _synthetic_universal_report()
        _validate_universal_document(universal)
        for name, change in (
            ("stale-all-engine-schema", {"schema": "rebar-python-re-universal-public-oracle-v0"}),
            ("missing-universal-candidate", {"completed_candidates": ["rust", "vm"]}),
            ("changed-universal-seed", {"seed": 2026072418}),
            ("changed-universal-seed-domain", {"seed_domain": "foreign/public"}),
            ("weakened-universal-cases", {"cases": 8_191}),
            ("weakened-universal-observations", {"observations_per_case": 47}),
            ("weakened-universal-total", {"total_comparisons": 1_179_647}),
            ("omitted-universal-grammar-family", {"grammar_family_count": 15}),
            ("omitted-universal-input-stratum", {"input_stratum_count": 15}),
            ("weakened-universal-stratum", {"examples_per_stratum": 31}),
            ("universal-python-mismatch", {"mismatches": 1}),
            ("changed-universal-case-digest", {"case_sha256": "0" * 64}),
            ("universal-opened-holdout", {"holdout_cases_read": 1}),
            ("universal-ran-timing", {"benchmark_or_timing_executed": True}),
            ("universal-external-regex", {"external_regex_packages": 1}),
            ("missing-universal-candidate-report", {"candidate_reports": {key: value for key, value in universal["candidate_reports"].items() if key != "zig"}}),
        ):
            reject(name, lambda delta=change: _validate_universal_document({**universal, **delta}))
        for name, field, value in (
            ("universal-stale-v5-base", "audit_sha256", "0" * 64),
            ("universal-stale-v5-strict", "postfinal_no_delegation_audit_sha256", "0" * 64),
            ("universal-foreign-worker", "guarded_worker_source_sha256", "0" * 64),
            ("universal-read-historical-timing", "previous_public_timing_evidence_read", True),
            ("universal-lost-locale-report", "official_locale_report_sha256", "0" * 64),
            ("universal-lost-locale-producer", "official_locale_source_sha256", "0" * 64),
            ("universal-concealed-official-method", "official_locale_total_method_results", 583),
            ("universal-concealed-official-skip", "official_locale_skipped", 1),
            ("universal-weakened-v5-guard-controls", "postfinal_no_delegation_wrapper_control_count", 675),
        ):
            reject(
                name,
                lambda key=field, item=value: _validate_universal_document(
                    {**universal, "audit": {**universal["audit"], key: item}}
                ),
            )
        for family in ("rust", "vm", "zig"):
            for field, value, suffix in (
                ("candidate", "foreign", "foreign-candidate"),
                ("module", "candidates.foreign_candidate", "foreign-module"),
                ("checks", 393_215, "omitted-comparison"),
                ("mismatches", 1, "hidden-mismatch"),
                ("holdout_cases_read", 1, "opened-holdout"),
                ("benchmark_or_timing_executed", True, "ran-timing"),
                ("external_regex_packages", 1, "external-regex"),
                ("case_sha256", "0" * 64, "changed-public-cases"),
            ):
                reject(
                    f"universal-{family}-{suffix}",
                    lambda candidate=family, key=field, item=value: (
                        _validate_universal_document(
                            {
                                **universal,
                                "candidate_reports": {
                                    **universal["candidate_reports"],
                                    candidate: {
                                        **universal["candidate_reports"][candidate],
                                        key: item,
                                    },
                                },
                            }
                        )
                    ),
                )
            first_guard = next(iter(universal["candidate_reports"][family]["poison_guards"]))
            reject(
                f"universal-{family}-weakened-no-delegation-guard",
                lambda candidate=family, key=first_guard: (
                    _validate_universal_document(
                        {
                            **universal,
                            "candidate_reports": {
                                **universal["candidate_reports"],
                                candidate: {
                                    **universal["candidate_reports"][candidate],
                                    "poison_guards": {
                                        **universal["candidate_reports"][candidate][
                                            "poison_guards"
                                        ],
                                        key: False,
                                    },
                                },
                            },
                        }
                    )
                ),
            )

        locale_sources = runtime["qualified_source_fingerprints"]
        locale_report = _synthetic_locale_report(locale_sources)
        synthetic_locale_sha256 = "b" * 64

        def validate_locale(
            document: Mapping[str, Any],
            *,
            source_fingerprints: Mapping[str, str] = locale_sources,
            native_fingerprints: Mapping[str, str] = EXPECTED_NATIVE_FINGERPRINTS,
            observed_sha256: str = synthetic_locale_sha256,
            expected_sha256: str = synthetic_locale_sha256,
            producer_sha256: str = "9" * 64,
            selected_method_sha256: str = locale_report["original_oracle"][
                "selected_method_sha256"
            ],
        ) -> None:
            _validate_locale_qualification_report(
                document,
                source_fingerprints,
                native_fingerprints,
                observed_report_sha256=observed_sha256,
                expected_report_sha256=expected_sha256,
                expected_producer_sha256=producer_sha256,
                expected_selected_method_sha256=selected_method_sha256,
            )

        validate_locale(locale_report)
        for name, change in (
            ("locale-foreign-schema-accepted", {"schema": "foreign-locale-proof"}),
            ("locale-failing-suite-accepted", {"status": "FAIL"}),
            ("locale-wrong-goal-accepted", {"goal_sha256": "0" * 64}),
            ("locale-wrong-producer-source-path", {"source_path": "tools/foreign.py"}),
            ("locale-wrong-producer-source-hash", {"source_sha256": "0" * 64}),
            ("locale-substituted-source-accepted", {"qualified_source_fingerprints": {**locale_sources, "synthetic/source-00.py": "0" * 64}}),
            ("locale-substituted-native-accepted", {"native_elf_fingerprints": {**EXPECTED_NATIVE_FINGERPRINTS, "candidates.rust_candidate:native-engine": "0" * 64}}),
            ("locale-holdout-access-accepted", {"holdout_accessed": True}),
            ("locale-timing-accepted", {"timing_performed": True}),
            ("locale-clock-benchmark-accepted", {"benchmark_or_timing_executed": True}),
            ("locale-omitted-cpython-reference", {"roles": {family: value for family, value in locale_report["roles"].items() if family != "re"}}),
            ("locale-omitted-independent-engine", {"roles": {family: value for family, value in locale_report["roles"].items() if family != "zig"}}),
        ):
            reject(name, lambda delta=change: validate_locale({**locale_report, **delta}))
        for name, role, value in (
            ("locale-stale-source-audit-accepted", "from_scratch", "0" * 64),
            ("locale-stale-isolation-audit-accepted", "no_delegation", "0" * 64),
        ):
            reject(
                name,
                lambda audit_role=role, digest=value: validate_locale(
                    {
                        **locale_report,
                        "audits": {
                            **locale_report["audits"],
                            audit_role: {
                                **locale_report["audits"][audit_role],
                                "sha256": digest,
                            },
                        },
                    }
                ),
            )
        for name, field, value in (
            ("locale-private-path-not-proved", "private", False),
            ("locale-genuine-source-not-proved", "genuine", False),
        ):
            reject(
                name,
                lambda key=field, item=value: validate_locale(
                    {**locale_report, "locales": {**locale_report["locales"], key: item}}
                ),
            )
        for name, role, field, value in (
            ("locale-missing-real-iso-8859-1", "iso88591", "name", "C"),
            ("locale-missing-real-utf8", "utf8", "name", "C"),
            ("locale-unverified-iso-source", "iso88591", "source_sha256", ""),
            ("locale-unverified-utf8-charmap", "utf8", "charmap_sha256", ""),
        ):
            reject(
                name,
                lambda locale_name=role, key=field, item=value: validate_locale(
                    {
                        **locale_report,
                        "locales": {
                            **locale_report["locales"],
                            locale_name: {
                                **locale_report["locales"][locale_name],
                                key: item,
                            },
                        },
                    }
                ),
            )
        for name, field, value in (
            ("locale-reference-failed", "status", "FAIL"),
            ("locale-reference-not-genuine", "genuine_locales", False),
            ("locale-reference-did-not-switch", "compiled_locale_switch", False),
            ("locale-reference-imported-candidate", "candidate_modules_loaded", True),
            ("locale-reference-opened-holdout", "holdout_accessed", True),
            ("locale-reference-started-clock", "timing_performed", True),
        ):
            reject(
                name,
                lambda key=field, item=value: validate_locale(
                    {
                        **locale_report,
                        "locale_reference": {
                            **locale_report["locale_reference"],
                            key: item,
                        },
                    }
                ),
            )
        for name, field, value in (
            ("locale-144-tests-accepted", "selected_methods", 144),
            ("locale-145-tests-accepted", "selected_methods", 145),
            ("locale-concealed-public-method", "total_public_methods", 151),
            ("locale-concealed-private-waiver", "named_waivers", {}),
            ("locale-foreign-private-waiver", "named_waivers", {"foreign": "foreign"}),
            ("locale-concealed-private-class", "named_class_waivers", {}),
            ("locale-expanded-private-waivers", "all_named_waivers", {}),
            ("locale-substituted-selected-methods", "selected_method_sha256", "0" * 64),
            ("locale-foreign-official-manifest", "manifest_sha256", "0" * 64),
            ("locale-foreign-official-runner", "runner_sha256", ""),
            ("locale-foreign-upstream-test", "source_sha256", "0" * 64),
        ):
            reject(
                name,
                lambda key=field, item=value: validate_locale(
                    {
                        **locale_report,
                        "original_oracle": {
                            **locale_report["original_oracle"],
                            key: item,
                        },
                    }
                ),
            )
        for family in ("re", "rust", "vm", "zig"):
            for field, value, suffix in (
                ("methods", 145, "145-tests"),
                ("methods", 144, "144-tests"),
                ("passed", 145, "weakened-denominator"),
                ("failed", 1, "failed-method"),
                ("failures", 1, "failure"),
                ("errors", 1, "error"),
                ("skipped", 1, "skip"),
                ("crashes", 1, "crash"),
                ("timeouts", 1, "timeout"),
                ("locale_caching_passed", False, "locale-caching-failure"),
                ("locale_compiled_passed", False, "locale-compiled-failure"),
            ):
                reject(
                    f"{family}-{suffix}",
                    lambda name=family, key=field, item=value: validate_locale(
                        {
                            **locale_report,
                            "roles": {
                                **locale_report["roles"],
                                name: {
                                    **locale_report["roles"][name],
                                    key: item,
                                },
                            },
                        }
                    ),
                )
            for suffix, mutate in (
                (
                    "duplicate-official-record",
                    lambda records: records.__setitem__(1, copy.deepcopy(records[0])),
                ),
                (
                    "failed-official-record",
                    lambda records: records[0].update(status="failed"),
                ),
                (
                    "skipped-official-record",
                    lambda records: records[0].update(skipped=1),
                ),
                (
                    "hidden-official-record-failure",
                    lambda records: records[0].update(failures=1),
                ),
                (
                    "concealed-locale-caching-record",
                    lambda records: records[0].update(
                        test="ReTests.test_foreign_locale_caching"
                    ),
                ),
                (
                    "concealed-locale-compiled-record",
                    lambda records: records[1].update(
                        test="ReTests.test_foreign_locale_compiled"
                    ),
                ),
            ):
                def poison_record(
                    name: str = family,
                    operation: Any = mutate,
                ) -> None:
                    changed = copy.deepcopy(locale_report)
                    operation(changed["roles"][name]["records"])
                    validate_locale(changed)

                reject(f"{family}-{suffix}", poison_record)
        reject(
            "locale-wrong-report-fingerprint",
            lambda: validate_locale(locale_report, observed_sha256="0" * 64),
        )
        reject(
            "locale-unpinned-report-fingerprint",
            lambda: validate_locale(locale_report, expected_sha256=""),
        )
        reject(
            "locale-wrong-immutable-selected-method-fingerprint",
            lambda: validate_locale(locale_report, selected_method_sha256="0" * 64),
        )
        frozen_v4.require(
            (
                OFFICIAL_LOCALE_REPORT_SHA256 is None
                or frozen_v4.valid_sha256(OFFICIAL_LOCALE_REPORT_SHA256)
            )
            and (
                OFFICIAL_LOCALE_SOURCE_SHA256 is None
                or frozen_v4.valid_sha256(OFFICIAL_LOCALE_SOURCE_SHA256)
            ),
            "the real-locale evidence or producer fingerprint has an invalid format",
        )

        original, document = _synthetic_public_manifests()
        _validate_public_parity(original, document)
        first = document["selected_cases"][0]
        for name, change in (
            ("changed-public-denominator", {"cases": 8_191}),
            ("hidden-public-category", {"all_bounded_workload_categories": 259}),
            ("changed-public-selection-seed", {"selection_seed": 2026072407}),
            ("changed-public-order-seed", {"order_seed": 2026072407}),
            ("changed-confidence-seed", {"bootstrap_seed": 2026072407}),
            ("weakened-paired-trials", {"frozen_trials": 12}),
            ("weakened-public-warmups", {"frozen_warmups": 3}),
            ("weakened-bootstrap-confidence", {"frozen_bootstrap_samples": 1_999}),
            ("changed-api-weights", {"public_operations": {**predecessor.FROZEN_PUBLIC_OPERATION_COUNTS, "search": 1_056}}),
            ("substituted-public-case", {"selected_cases": [{**first, "case": "cal.public.v7.synthetic.substitution"}, *document["selected_cases"][1:]]}),
            ("duplicate-public-case", {"selected_cases": [document["selected_cases"][1], *document["selected_cases"][1:]]}),
            ("opened-final-holdout", {"holdout_accessed": True}),
            ("deserialized-final-case", {"held_out_records_deserialized": 1}),
            ("read-historical-timing", {"historical_performance_read": True}),
            ("premature-public-timing", {"timing_performed": True}),
            ("substituted-public-version", {"protocol_version": "postfinal-public-practice-v6"}),
        ):
            reject(name, lambda delta=change: _validate_public_parity(original, {**document, **delta}))

        wire: list[dict[str, Any]] = []
        for name, value in (
            ("lone-high-surrogate", "\ud800"),
            ("lone-low-surrogate", "\udfff"),
            ("separated-lone-surrogates", "\ud800x\udfff"),
            ("emoji", "\U0001f600"),
            ("astral-code-point", "\U00010348"),
            ("combining-text", "e\u0301"),
            ("escaped-newline", "left\nright"),
        ):
            payload = {
                "op": "prepare",
                "case": {"pattern": value, "string": value},
                "expected": {"value": value},
            }
            encoded = frozen_v5.encode_private_worker_request(payload)
            frozen_v4.require(
                encoded.isascii()
                and "\n" not in encoded
                and json.loads(encoded) == payload
                and frozen_v5.encode_private_worker_request(json.loads(encoded)) == encoded,
                f"public V7 lost the surrogate-safe immutable worker wire: {name}",
            )
            wire.append({"name": name, "passed": True})
        circular: dict[str, Any] = {}
        circular["self"] = circular
        for name, value in (
            ("wire-nan", {"value": float("nan")}),
            ("wire-positive-infinity", {"value": float("inf")}),
            ("wire-negative-infinity", {"value": float("-inf")}),
            ("wire-unserializable-object", {"value": object()}),
            ("wire-unserializable-bytes", {"value": b"private"}),
            ("wire-circular-document", circular),
        ):
            reject(name, lambda document=value: frozen_v5.encode_private_worker_request(document))

        frozen_v4.require(
            len(controls) >= 70
            and len({item["name"] for item in controls}) == len(controls)
            and all(item.get("passed") is True for item in controls)
            and len(wire) == 7
            and frozen_v4.PersistentGuardedWorker is frozen_v5.PersistentGuardedWorker,
            "public V7 weakened or duplicated a candidate-free poison control",
        )

    frozen_v4.require_candidate_free()
    return {
        **inherited,
        "source_public_v6_runner_path": _owned_relative(FROZEN_V6_SOURCE_PATH),
        "source_public_v6_runner_sha256": FROZEN_V6_SOURCE_SHA256,
        "source_public_v6_manifest_sha256": FROZEN_V6_MANIFEST_SHA256,
        "public_predecessor_evidence_accessed": False,
        "actual_v5_audits_accessed": False,
        "actual_universal_report_accessed": False,
        "actual_candidate_proofs_accessed": False,
        "actual_goal_accessed": False,
        "private_worker_wire_format": frozen_v5.PRIVATE_WORKER_WIRE_FORMAT,
        "private_worker_wire_ensure_ascii": True,
        "private_worker_wire_control_count": len(wire),
        "private_worker_wire_controls": wire,
        "postfinal_v7_poisoned_control_count": len(controls),
        "postfinal_v7_poisoned_controls": controls,
        "mixed_correctness_artifact_count": 12,
        "fresh_current_correctness_artifact_count": 12,
        "fresh_rust_correctness_artifact_count": 4,
        "fresh_peer_correctness_artifact_count": 8,
        "sealed_campaign_controller_schema": CAMPAIGN_CONTROLLER_SCHEMA,
        "sealed_campaign_family_count": 3,
        "sealed_campaign_stage_count": 22,
        "sealed_campaign_full_unicode_checks": 4_494_555,
        "stage10_qualification_required": True,
        "stage10_cases_per_candidate": STAGE10_CASES,
        "stage10_candidate_checks": 3 * STAGE10_CASES,
        "stage10_combined_public_comparisons": 1_179_648 + 3 * STAGE10_CASES,
        "stage10_preserved_failure_count": 32 + 256,
        "stage10_loader_aliases_blocked": len(STAGE10_BLOCKED_NATIVE_LOADER_ALIASES),
        "stage10_isolated_signature_cases": 256,
        "official_locale_qualification_required": True,
        "official_locale_required_tests_per_family": OFFICIAL_LOCALE_TESTS,
        "official_locale_required_family_count": 4,
        "official_locale_report_pinned": (
            isinstance(OFFICIAL_LOCALE_REPORT_SHA256, str)
            and frozen_v4.valid_sha256(OFFICIAL_LOCALE_REPORT_SHA256)
        ),
        "official_locale_producer_pinned": (
            isinstance(OFFICIAL_LOCALE_SOURCE_SHA256, str)
            and frozen_v4.valid_sha256(OFFICIAL_LOCALE_SOURCE_SHA256)
        ),
        "freeze_authorized": False,
        "candidate_processes_started": 0,
        "worker_processes_started": 0,
        "production_reports_read": 0,
        "performance_fixtures_opened": 0,
        "entropy_accessed": False,
        "clock_accessed": False,
        "benchmark_or_timing_executed": False,
        "failed": 0,
    }


def freeze(args: Any) -> dict[str, Any]:
    """Exclusively create one candidate-free, prospective V7 public plan."""

    frozen_v4.require_candidate_free()
    frozen_v4.require_pinned_python()
    _require_stage10_qualification()
    frozen_v4.require(
        isinstance(OFFICIAL_LOCALE_REPORT_SHA256, str)
        and frozen_v4.valid_sha256(OFFICIAL_LOCALE_REPORT_SHA256),
        "V7 freezing is blocked until CPython and all three current engines "
        "pass 146/146 real-locale official tests without skips",
    )
    _require_complete_campaign_pins()
    target = frozen_v4.exact_versioned_path(
        args.output, MANIFEST_PATH, "exclusively frozen public V7 manifest"
    )
    frozen_v4.require(
        not target.exists() and not target.is_symlink(),
        "refusing to overwrite or substitute the one-time public V7 manifest",
    )
    frozen_v4.require(
        all(not path.exists() and not path.is_symlink() for path in (RAW_PATH, SUMMARY_PATH, INTEGRITY_PATH)),
        "public V7 cannot be frozen after a timing result has been created",
    )
    edge_paths = list(args.edge_oracle) if args.edge_oracle else list(MIXED_EDGE_ORACLES)
    _suite, entries, document = make_manifest(edge_paths)
    manifest_sha256 = frozen_v4.pilot.save_json(target, document)
    frozen_v4.require_candidate_free()
    audit_fields = (
        "postfinal_no_delegation_audit_path",
        "postfinal_no_delegation_audit_sha256",
        "postfinal_no_delegation_audit_source_path",
        "postfinal_no_delegation_audit_source_sha256",
        "postfinal_no_delegation_audit_schema",
        "postfinal_no_delegation_control_count",
        "postfinal_guarded_worker_source_path",
        "postfinal_guarded_worker_source_sha256",
        "postfinal_guarded_worker_schema",
        "postfinal_guarded_worker_report_path",
        "postfinal_guarded_worker_report_sha256",
        "goal_path",
        "goal_sha256",
        "postfinal_stage10_source_path",
        "postfinal_stage10_source_sha256",
        "postfinal_stage10_protocol_path",
        "postfinal_stage10_protocol_sha256",
        "postfinal_stage10_self_oracle_path",
        "postfinal_stage10_self_oracle_sha256",
        "postfinal_stage10_all_candidate_path",
        "postfinal_stage10_all_candidate_sha256",
        "postfinal_stage10_schema",
        "postfinal_stage10_self_oracle_schema",
        "postfinal_stage10_all_candidate_schema",
        "postfinal_stage10_matrix_sha256",
        "postfinal_stage10_seed",
        "postfinal_stage10_seed_domain",
        "postfinal_stage10_observation_domain",
        "postfinal_stage10_cohort_cases",
        "postfinal_stage10_cases_per_candidate",
        "postfinal_stage10_candidate_checks",
        "postfinal_stage10_combined_public_comparisons",
        "postfinal_stage10_self_checks",
        "postfinal_stage10_isolated_signature_cases",
        "postfinal_stage10_native_loader_aliases",
        "postfinal_stage10_reference_record_sha256",
        "postfinal_stage10_metadata_record_sha256",
        "postfinal_stage07_failure_path",
        "postfinal_stage07_failure_sha256",
        "postfinal_stage07_failure_count",
        "postfinal_stage08_rust_failure_path",
        "postfinal_stage08_rust_failure_sha256",
        "postfinal_stage08_rust_failure_count",
        "postfinal_sealed_campaign_schema",
        "postfinal_sealed_campaign_controller_path",
        "postfinal_sealed_campaign_controller_sha256",
        "postfinal_sealed_campaign_ancestor_path",
        "postfinal_sealed_campaign_ancestor_sha256",
        "postfinal_sealed_campaign_family_count",
        "postfinal_sealed_campaign_reports",
        "postfinal_rust_sealed_campaign_controller_path",
        "postfinal_rust_sealed_campaign_controller_sha256",
        "postfinal_rust_sealed_campaign_report_path",
        "postfinal_rust_sealed_campaign_report_sha256",
        "postfinal_rust_sealed_campaign_required_steps",
        "postfinal_rust_sealed_campaign_unicode_checks",
        "postfinal_official_locale_report_path",
        "postfinal_official_locale_report_sha256",
        "postfinal_official_locale_report_schema",
        "postfinal_official_locale_source_path",
        "postfinal_official_locale_source_sha256",
        "postfinal_official_original_manifest_sha256",
        "postfinal_official_original_runner_sha256",
        "postfinal_official_original_test_source_sha256",
        "postfinal_official_original_selected_method_sha256",
        "postfinal_official_locale_tests_per_family",
        "postfinal_official_locale_family_count",
        "postfinal_official_locale_skipped_tests",
    )
    return {
        "schema": POSTFINAL_PLAN_SCHEMA,
        "result": "PASS",
        "protocol_version": VERSION,
        "freeze_only": True,
        "candidate_imported": False,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "timing_performed": False,
        "benchmark_or_timing_executed": False,
        "worker_processes_started": 0,
        "cases": len(entries),
        "source_public_cases": frozen_v4.FIXTURE_CASES,
        "eligible_practice_cases": frozen_v4.ELIGIBLE_CASES,
        "all_bounded_workload_categories": frozen_v4.CATEGORIES,
        "public_operations": document["public_operations"],
        "trials": frozen_v4.TRIALS,
        "warmups": frozen_v4.WARMUPS,
        "bootstrap_draws": frozen_v4.BOOTSTRAPS,
        "prospective_paired_raw_rows": frozen_v4.EXPECTED_ROWS,
        "prospective_correctness_checks": frozen_v4.EXPECTED_CORRECTNESS_CHECKS,
        "verified_independent_engine_count": len(frozen_v4.MODULES) - 1,
        "verified_native_library_count": len(document["native_elf_fingerprints"]),
        **{field: document[field] for field in audit_fields},
        **{field: document[field] for field in frozen_v4.UNIVERSAL_ORACLE_PROOF_FIELDS},
        "source_public_v6_runner_sha256": FROZEN_V6_SOURCE_SHA256,
        "source_public_v6_manifest_sha256": FROZEN_V6_MANIFEST_SHA256,
        "public_v6_case_population_preserved": True,
        "runner_sha256": document["runner_sha256"],
        "manifest": str(target),
        "manifest_sha256": manifest_sha256,
        "failed": 0,
    }


def _require_committed_and_pushed_freeze() -> None:
    """Permit actual timing only after the complete exact plan reaches main."""

    frozen_v4.require_candidate_free()

    def git(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    required = (SOURCE_PATH, MANIFEST_PATH, VERSION_ROOT / "PROTOCOL.md", GOAL_PATH)
    owned: list[str] = []
    for path in required:
        frozen_v4.require(
            path.is_file() and not path.is_symlink(),
            "the exact public V7 source, plan, protocol, or immutable goal is missing",
        )
        owned.append(_owned_relative(path))
    tracked = git("ls-files", "--error-unmatch", "--", *owned)
    frozen_v4.require(
        tracked.returncode == 0,
        "the public V7 source, protocol, manifest, and goal must be committed before timing",
    )
    clean = git("status", "--porcelain", "--", *owned)
    frozen_v4.require(
        clean.returncode == 0 and not clean.stdout.strip(),
        "a committed public V7 source, manifest, protocol, or goal has changed",
    )
    branch = git("symbolic-ref", "--quiet", "--short", "HEAD")
    frozen_v4.require(
        branch.returncode == 0 and branch.stdout.strip() == "main",
        "public V7 timing is authorized only on the committed main branch",
    )
    pushed = git("merge-base", "--is-ancestor", "HEAD", "origin/main")
    frozen_v4.require(
        pushed.returncode == 0,
        "the exact public V7 source, protocol, and manifest must be pushed before timing",
    )
    frozen_v4.require_candidate_free()


def measure(args: Any) -> dict[str, Any]:
    frozen_v4.require(
        getattr(args, "exclusive_slot", None) == EXCLUSIVE_SLOT,
        "public V7 timing requires its explicit one-time V7 slot",
    )
    _require_stage10_qualification()
    _require_locale_qualification()
    _require_committed_and_pushed_freeze()
    return _ORIGINAL_MEASURE(args)


def verify(args: Any) -> dict[str, Any]:
    _require_stage10_qualification()
    _require_locale_qualification()
    _require_committed_and_pushed_freeze()
    return _ORIGINAL_VERIFY(args)


for _name, _value in {
    "__file__": str(SOURCE_PATH),
    "VERSION": VERSION,
    "VERSION_ROOT": VERSION_ROOT,
    "EVIDENCE_ROOT": EVIDENCE_ROOT,
    "MANIFEST_PATH": MANIFEST_PATH,
    "RAW_PATH": RAW_PATH,
    "SUMMARY_PATH": SUMMARY_PATH,
    "INTEGRITY_PATH": INTEGRITY_PATH,
    "POSTFINAL_PLAN_SCHEMA": POSTFINAL_PLAN_SCHEMA,
    "POSTFINAL_REPORT_SCHEMA": POSTFINAL_REPORT_SCHEMA,
    "POSTFINAL_INTEGRITY_SCHEMA": POSTFINAL_INTEGRITY_SCHEMA,
    "EXCLUSIVE_SLOT": EXCLUSIVE_SLOT,
    "AUDIT_PATH": BASE_AUDIT_PATH,
    "AUDIT_SOURCE_PATH": BASE_AUDIT_SOURCE_PATH,
    "POSTFINAL_AUDIT_PATH": STRICT_AUDIT_PATH,
    "POSTFINAL_AUDIT_SOURCE_PATH": STRICT_AUDIT_SOURCE_PATH,
    "POSTFINAL_AUDIT_SCHEMA": STRICT_AUDIT_SCHEMA,
    "POSTFINAL_AUDIT_CONTROL_COUNT": STRICT_AUDIT_CONTROL_COUNT,
    "UNIVERSAL_ORACLE_SOURCE_PATH": UNIVERSAL_SOURCE_PATH,
    "UNIVERSAL_ORACLE_SOURCE_SHA256": UNIVERSAL_SOURCE_SHA256,
    "UNIVERSAL_ORACLE_REPORT_PATH": UNIVERSAL_REPORT_PATH,
    "STAGE05_CORRECTNESS_PATHS": MIXED_CORRECTNESS_PATHS,
    "DEFAULT_EDGE_ORACLES": MIXED_EDGE_ORACLES,
    "PersistentGuardedWorker": frozen_v5.PersistentGuardedWorker,
    "require_stage05_correctness_path_contract": require_stage05_correctness_path_contract,
    "verified_stage05_correctness_artifacts": verified_stage05_correctness_artifacts,
    "verified_from_scratch_audit": verified_from_scratch_audit,
    "load_guarded_worker_module": load_guarded_worker_module,
    "make_manifest": make_manifest,
    "synthetic_self_test": synthetic_self_test,
    "freeze": freeze,
    "measure": measure,
    "verify": verify,
}.items():
    setattr(frozen_v4, _name, _value)


def __getattr__(name: str) -> Any:
    return getattr(frozen_v4, name)


def main(arguments: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if arguments is None else arguments)
    if argv:
        argv[0] = {
            "--self-test": "self-test",
            "prepare": "freeze",
            "--prepare": "freeze",
            "--freeze": "freeze",
            "replay": "verify",
        }.get(argv[0], argv[0])
    original_argv = sys.argv
    try:
        sys.argv = [str(SOURCE_PATH), *argv]
        frozen_v4.main()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    main()
