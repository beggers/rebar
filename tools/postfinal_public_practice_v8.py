#!/usr/bin/env python3
"""Measure only a prospectively frozen, enlarged *public* regex comparison.

The 33,280 examples in this experiment are public development data.  They are
not secret, held-out, or final performance evidence.  This controller never
imports a candidate or an older experiment.  Its four engines run in separate
processes started by the independently authenticated, immutable V1 guard.

``--self-test`` uses only synthetic in-memory values.  Real freezing and
measurement fail closed until the exact V7 predecessor, V8 generator and
protocol, complete V5 audits, both Stage 10 Python references, and all three
independently guarded Stage 10 candidate proofs have been authenticated.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import importlib
import io
import json
import math
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = Path(__file__).resolve()
VERSION = "postfinal-public-practice-v8"
VERSION_ROOT = ROOT / "performance" / "postfinal-public-v8"
PROTOCOL_PATH = VERSION_ROOT / "PROTOCOL.md"
MANIFEST_PATH = VERSION_ROOT / "manifest.json"
EVIDENCE_ROOT = VERSION_ROOT / "evidence"
RAW_PATH = EVIDENCE_ROOT / f"{VERSION}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE_ROOT / f"{VERSION}-summary.json"
INTEGRITY_PATH = EVIDENCE_ROOT / f"{VERSION}-integrity.json"

PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
GOAL_PATH = ROOT / "GOAL.md"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
V7_SOURCE_PATH = ROOT / "tools" / "postfinal_public_practice_v7.py"
V7_PROTOCOL_PATH = ROOT / "performance" / "postfinal-public-v7" / "PROTOCOL.md"
GENERATOR_SOURCE_PATH = ROOT / "tools" / "postfinal_public_expansion_v8.py"
PUBLIC_V6_MANIFEST_PATH = (
    ROOT / "performance" / "postfinal-public-v6" / "manifest.json"
)
PUBLIC_V6_MANIFEST_SHA256 = (
    "65e024a1a79d13b03e4e5ad0f3d4ae010dbb6e4f09b52a8542837a2ea4c6198a"
)

# The public experiment is authorized only by source-bound, genuinely passing
# Stage 10 reference and candidate evidence.  Historical Stage 07 reference
# failures and Stage 08 candidate failures remain failures; neither is passed
# off as an independently successful correctness experiment.
V7_SOURCE_SHA256 = (
    "cc5b79daf3a0d018d15c76d01665cf94a30d3838c5a5c21389cba51444e96e7e"
)
V7_PROTOCOL_SHA256 = (
    "c8fed02bde3d2b096905a44db99405b47801743749053e8dc402cb70cc1f51c0"
)
GENERATOR_SOURCE_SHA256 = (
    "e921d5962746d564381a0a11d22eb125b080370b572ffd0f630e925025f1ec97"
)
PROTOCOL_SHA256 = (
    "e19d504f6d7504b4052f2bbfbc0a584596178919c5396e076d3e6261356a2095"
)

BASE_AUDIT_SOURCE_PATH = ROOT / "tools" / "postfinal_from_scratch_audit_v5.py"
BASE_AUDIT_SOURCE_SHA256 = (
    "100520ae06c3a837b3fa4ca508099ceb6e11efda8f63bcc0234b544071d17843"
)
BASE_AUDIT_PATH = (
    ROOT / "candidates" / "audits" / "POSTFINAL-FROM-SCRATCH-AUDIT-V5.json"
)
BASE_AUDIT_SHA256 = (
    "42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198"
)
STRICT_AUDIT_SOURCE_PATH = ROOT / "tools" / "postfinal_no_delegation_audit_v5.py"
STRICT_AUDIT_SOURCE_SHA256 = (
    "18a04023659e386780d6e9cd6b90065553254c18f2fe54ae78c37acbc468a7b6"
)
STRICT_AUDIT_PATH = (
    ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V5.json"
)
STRICT_AUDIT_SHA256 = (
    "50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb"
)
GUARD_SOURCE_PATH = ROOT / "tools" / "postfinal_no_delegation_audit_v1.py"
GUARD_SOURCE_SHA256 = (
    "e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed"
)
GUARD_REPORT_PATH = (
    ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
)
GUARD_REPORT_SHA256 = (
    "c4605c8af5da805c099b1efb7f15e8390781768bb3014276b465a7712b4ed06b"
)
GUARD_SCHEMA = "rebar-postfinal-no-delegation-audit-v1"

LOCALE_SOURCE_PATH = ROOT / "tools" / "postfinal_cpython_locale_oracle_v1.py"
LOCALE_SOURCE_SHA256 = (
    "b87bbdcddef2d19a462e8c4b37bd159f6c3a30ea9b4fe5d9471eff1f51fbcb55"
)
LOCALE_REPORT_PATH = (
    ROOT / "oracle" / "cpython-3.14.6" / "evidence"
    / "postfinal-locale-v1-all.json"
)
LOCALE_REPORT_SHA256 = (
    "bc17ee74409543d1b57f3aee65088e990ab21ac83dc75ac46fbd1f97f04b6621"
)
LOCALE_SCHEMA = "rebar-postfinal-cpython-public-locale-v1"
UNIVERSAL_SOURCE_PATH = (
    ROOT / "tools" / "python_re_universal_public_oracle_stage06.py"
)
UNIVERSAL_SOURCE_SHA256 = (
    "ff365f1d867f4873146aaf6f77fa2f360b197bbccfb9dd06239bdcf4b776e7f2"
)
UNIVERSAL_REPORT_PATH = (
    ROOT / "candidates" / "evidence"
    / "python-re-universal-public-oracle-v6-all.json"
)
UNIVERSAL_REPORT_SHA256 = (
    "bf4f7cc82c876ee54e55c0971c65db209f6fdf0c8b00baa8c57fbc5f460b1528"
)
UNIVERSAL_CASE_SHA256 = (
    "8e5c120a4e637c30940363e20d6042324d65d9f7d03fbd35240ffabf2df282ae"
)
ORIGINAL_SELECTED_METHOD_SHA256 = (
    "d33571d09a3a9cb428a84dece5af233e66267b831d3043c90e3ad77cb8de5178"
)
ORIGINAL_OFFICIAL_RUNNER_SHA256 = (
    "d5084fd43352f34267f3ed9b4b5d60a6070e2c50d4b787739270502c856e18bb"
)
ORIGINAL_OFFICIAL_SOURCE_SHA256 = {
    "LICENSE": "b0e25a78cffb43f4d92de8b61ccfa1f1f98ecbc22330b54b5251e7b6ba010231",
    "re_tests.py": "ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab",
    "test_re.py": "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2",
}

# Authenticate the actual successful stage rather than relabeling a preserved
# failed Stage 07 or Stage 08 experiment.  The seed and complete case matrix
# intentionally remain those of the original public compatibility contract.
STAGE10_SOURCE_PATH = ROOT / "tools" / "python_re_universal_public_oracle_stage10.py"
STAGE10_PROTOCOL_PATH = (
    ROOT / "oracle" / "cpython-3.14.6" / "PUBLIC-CONTRACT-V10.md"
)
STAGE10_SELF_ORACLE_PATH = (
    ROOT / "oracle" / "cpython-3.14.6" / "evidence"
    / "public-contract-v10-self-oracle.json"
)
STAGE10_ALL_CANDIDATE_PATH = (
    ROOT / "candidates" / "evidence"
    / "python-re-universal-public-oracle-v10-all.json"
)
STAGE10_SOURCE_SHA256 = (
    "a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08"
)
STAGE10_PROTOCOL_SHA256 = (
    "c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543"
)
STAGE10_SELF_ORACLE_SHA256 = (
    "5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9"
)
STAGE10_ALL_CANDIDATE_SHA256 = (
    "0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7"
)
STAGE10_SCHEMA = "rebar-python-re-public-contract-v10"
STAGE10_SELF_ORACLE_SCHEMA = STAGE10_SCHEMA + "-self-oracle"
STAGE10_ALL_CANDIDATE_SCHEMA = STAGE10_SCHEMA + "-all-candidates"
STAGE10_METADATA_SCHEMA = STAGE10_SCHEMA + "-isolated-public-metadata"
STAGE10_OBSERVATION_DOMAIN = "rebar/python-re/public-contract/v10"
STAGE10_MATRIX_SHA256 = (
    "0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db"
)
STAGE10_SEED = 2_026_072_437
STAGE10_SEED_DOMAIN = "rebar/python-re/public-contract/v7"
STAGE10_COHORT_CASES = {
    "public-surface": 256,
    "invalid-grammar": 256,
    "real-locale": 1_024,
    "buffer-lifetime": 256,
    "object-contract": 256,
    "callback-scanner": 256,
    "shared-pattern-threads": 256,
    "bounded-unicode": 1_024,
}
STAGE10_CASES = 3_584
STAGE10_STDLIB_CHECKS = 7_168
STAGE10_CANDIDATE_CHECKS = 10_752
STAGE10_NATIVE_LOADER_ALIASES = (
    "ctypes.CDLL",
    "ctypes.cdll.LoadLibrary",
    "ctypes.cdll._dlltype",
    "ctypes._dlopen",
    "_ctypes.dlopen",
)
PRESERVED_STAGE07_FAILURE_SHA256 = (
    "765e635745a7e332a1bd22426065c43fd52036d013add0d88d840d8fde1121e0"
)
PRESERVED_STAGE08_SELF_ORACLE_SHA256 = (
    "efcf0f661363e9032ce8c0afe7ea06a4762b783eec4c4ee6ec7c7059c14994df"
)
PRESERVED_STAGE08_RUST_FAILURE_SHA256 = (
    "f509cedf5f58d1c211b63177fb843bfba3dc0b132469a392df43a9c802e323b1"
)

CONTROLLER_SOURCE_PATH = (
    ROOT / "tools" / "rust_v8_multi_candidate_campaign_postfinal_v5.py"
)
CONTROLLER_SOURCE_SHA256 = (
    "50a39f8338b176b9376cac1437a7c0aaeb343594af0ebfea797a7beea04e86d9"
)
CONTROLLER_ANCESTOR_PATH = (
    ROOT / "tools" / "rust_v8_multi_candidate_campaign_postfinal_v4.py"
)
CONTROLLER_ANCESTOR_SHA256 = (
    "67a7555976ab60c371c9aad1b7f94c112bd1c6aaf990e39c02f4484f3010e799"
)
CAMPAIGN_SCHEMA = "rebar-v8-multi-candidate-sealed-campaign-postfinal-v5"
CAMPAIGN_PRODUCTION_ROLE_COUNTS = {"rust": 5, "vm": 3, "zig": 5}
CAMPAIGN_DIGESTS: dict[str, str | None] = {
    "rust": "bdc10bbdf1f6a7711283826b04c1fe7f4ab700a7cf97d4c8f0595d20cab80024",
    "vm": "3156b02d4dd428b82c6c3947b620fa046330234b1ce0fd66058dff4a3d0c6d16",
    "zig": "e9a096349fd3b3cd9c91464b6033880ef9f2d30dece18e04d0c2a79efc6812cf",
}
CAMPAIGN_STAGES = (
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

EXPECTED_SOURCE_FINGERPRINTS = {
    "candidates/rust/py_bridge.c": (
        "3d432d8f53a75eb2c3c75d118c811ac7ba12c432d987422223d55773fbb36abe"
    ),
    "candidates/rust/src/lib.rs": (
        "3a2ab20885daea11bbc90cb9707a154174742f836e818521c1d00e2a0afd0b64"
    ),
    "candidates/rust/src/newline.rs": (
        "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b"
    ),
    "candidates/rust/src/search.rs": (
        "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe"
    ),
    "candidates/rust/src/stack.rs": (
        "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e"
    ),
    "candidates/rust/src/unicode_tables.rs": (
        "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af"
    ),
    "candidates/rust_candidate.py": (
        "ed210957f3fc7a8d87ce38cfc775cd380bed19dcde7e8acd23d09197abb60048"
    ),
    "candidates/_vm_native.c": (
        "3684b0cd45b149edf14aad50704b35dedf74bde65f238ab3be151193aeef2d6f"
    ),
    "candidates/vm_candidate.py": (
        "ef00948bb6138342501fbfef4070900ce1b4a57ecf9d805fc897fedcb36978d0"
    ),
    "candidates/zig/mini_regex.zig": (
        "539bf5d378e0c2845c01519fcce62f1ef5e68610f477912c44a03027fb67a346"
    ),
    "candidates/zig/py_bridge.c": (
        "17d8578bbc1e73db84aa59755bf3c8add2801066d238e506c0e6f16efa920568"
    ),
    "candidates/zig_candidate.py": (
        "b7330484e8436adc91d1d0960745a54be94752eb7f7fc7fbf747ddfa3cb80d6b"
    ),
}
EXPECTED_NATIVE_FILES = {
    "candidates.rust_candidate:native-bridge": (
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36",
    ),
    "candidates.rust_candidate:native-engine": (
        "candidates/_rust_engine.so",
        "d590300720215718782227dd8da1192047b4781bdb41ed94446cac06ba880e84",
    ),
    "candidates.vm_candidate:native-engine": (
        "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "af702483ebecb4164d1a059922ce7a909d192bdd42c60474bf0c81e6d49764aa",
    ),
    "candidates.zig_candidate:native-bridge": (
        "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "32dadc46281d13df784693f0785d4d149e6d3cd000aa3de6eb220a4a9ed50c9c",
    ),
    "candidates.zig_candidate:native-engine": (
        "candidates/_zig_probe.so",
        "f658b2325642b38e8303d94c6bdc42e74ba8b1f021af76e80f0c8936aa10f81a",
    ),
}

FROZEN_FAMILY_PROOFS: dict[str, tuple[str, str]] = {
    "rust-edge": (
        "candidates/evidence/rust-v7-edge-oracle-rust-postfinal-locale-v1.json.gz",
        "8569275c5b705870bde368ee20981be1a90c07675b12fe53b64f19c7e765b408",
    ),
    "rust-deep-public-contract": (
        "candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-LOCALE-V1.json.gz",
        "ca437ae8e2dc46f4d0b8e259f304a402efc6f0817dfe89600d92728a86c2ce9f",
    ),
    "rust-observability": (
        "candidates/evidence/rust-v8-observability-rust-qualified-postfinal-locale-v1.json.gz",
        "db139cf63dfe6605120a9e36db16b749f060fc31961fe6215397623b454929fa",
    ),
    "vm-edge": (
        "candidates/evidence/rust-v7-edge-oracle-vm-postfinal-locale-v1.json.gz",
        "0c07fdbf8848f4236735c97bbda4969c4de0ceb6e10c11fdac0c674d5efd303b",
    ),
    "vm-deep-public-contract": (
        "candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-LOCALE-V1.json.gz",
        "9d8aa10cd07d4bee48b021f26fbb66e5d2f3293f6c1d8a0d1039a9087af932de",
    ),
    "vm-observability": (
        "candidates/evidence/rust-v8-observability-vm-qualified-postfinal-locale-v1.json.gz",
        "35c63238162f420c41a5b021641530344d91ddc036b15dac73705b3f144ee43b",
    ),
    "zig-edge": (
        "candidates/evidence/rust-v7-edge-oracle-zig-postfinal-locale-v1.json.gz",
        "8a8f76a85e2888dc0eb19e07c7343dd5c8caeab8745baf8a277f68beea1424a6",
    ),
    "zig-deep-public-contract": (
        "candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-LOCALE-V1.json.gz",
        "f522ae69bea26792b8406254360809ae9cfddeb03cc012dc579f2397c7e8813d",
    ),
    "zig-observability": (
        "candidates/evidence/rust-v8-observability-zig-qualified-postfinal-locale-v1.json.gz",
        "43053dd764ee9b6c40ccfee72107b1e1ebe56e1081b951ec026c3ab8c124e15d",
    ),
}

PLAN_SCHEMA = "rebar-postfinal-public-development-plan-v8"
REPORT_SCHEMA = "rebar-postfinal-public-practice-report-v8"
INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v8"
ROW_SCHEMA = "rebar-postfinal-public-practice-row-v8"
SELF_TEST_SCHEMA = "rebar-postfinal-public-practice-self-test-v8"
COHORT = "calibration"
SEED_DOMAIN = "rebar/public-development/v8"
SELECTION_SEED = 2_026_072_428
ORDER_SEED = 2_026_072_429
BOOTSTRAP_SEED = 2_026_072_430
CATEGORY_COUNT = 260
CASES_PER_CATEGORY = 128
CASE_COUNT = CATEGORY_COUNT * CASES_PER_CATEGORY
ORIGINAL_CASE_COUNT = 8_192
GENERATED_CASE_COUNT = CASE_COUNT - ORIGINAL_CASE_COUNT
TRIALS = 13
WARMUPS = 4
BOOTSTRAPS = 2_000
MAX_OPERATIONS = 16
MAX_RESPONSE_BYTES = 262_144
SUBJECT_LIMIT = 8_192
RESULT_LIMIT = 128
PACKING_MARKER = "__rebar_calibration_type__"
MODULES = (
    "re",
    "candidates.rust_candidate",
    "candidates.vm_candidate",
    "candidates.zig_candidate",
)
FAMILIES = {
    "re": "re",
    "candidates.rust_candidate": "rust",
    "candidates.vm_candidate": "vm",
    "candidates.zig_candidate": "zig",
}
PUBLIC_OPERATIONS = frozenset(
    {
        "compile", "escape", "findall", "finditer", "fullmatch", "match",
        "match-surface", "scanner", "search", "split", "sub", "subn",
    }
)
EXPECTED_RAW_ROWS = CASE_COUNT * len(MODULES) * TRIALS
EXPECTED_CORRECTNESS_ANSWERS = EXPECTED_RAW_ROWS * 3
EXPECTED_CONFIDENCE_INTERVALS = (CASE_COUNT + 1) * (len(MODULES) - 1)
EXPECTED_PROCESS_NATIVE_CHECKS = CASE_COUNT * len(MODULES) * 2 + len(MODULES) * 2
EXPECTED_GLOBAL_PREQUALIFICATIONS = CASE_COUNT * (len(MODULES) - 1)

QUALIFICATION_CLOCK_NAMES = (
    "perf_counter", "perf_counter_ns", "monotonic", "monotonic_ns",
    "process_time", "process_time_ns", "thread_time", "thread_time_ns",
    "time", "time_ns",
)

QUALIFICATION_FUNCTION_SOURCE = r'''
def qualify_public_v8_case(candidate, request):
    if prepared is None or pilot is None:
        raise RuntimeError("public V8 correctness case was not prepared")
    if request.get("case") != prepared[0].get("id"):
        raise RuntimeError("public V8 correctness case was substituted")

    def reject_clock(*args, **kwargs):
        raise RuntimeError("a clock was accessed during public V8 correctness")

    for clock_name in (
        "perf_counter", "perf_counter_ns", "monotonic", "monotonic_ns",
        "process_time", "process_time_ns", "thread_time", "thread_time_ns",
        "time", "time_ns",
    ):
        if hasattr(time, clock_name):
            setattr(time, clock_name, reject_clock)

    before = verify_runtime()
    case, expected, action = prepared
    independently_checked = pilot.correctness_gate(candidate, case, expected)
    actual = action()
    actual_snapshot = pilot.snapshot(actual)
    actual_result_sha256 = pilot.digest(actual_snapshot)
    if actual_snapshot != expected.get("result"):
        raise RuntimeError("public V8 actual candidate result differs from CPython")
    if actual_result_sha256 != expected.get("result_sha256"):
        raise RuntimeError("public V8 actual candidate result digest differs from CPython")
    if independently_checked != actual_result_sha256:
        raise RuntimeError("public V8 independent correctness gate digest disagrees")
    pilot.exact_snapshot(
        actual, expected, actual_result_sha256,
        "public V8 complete untimed candidate prequalification",
    )
    after = verify_runtime()
    if before.get("passed") is not True or after.get("passed") is not True:
        raise RuntimeError("public V8 candidate lost its guarded native provenance")
    return {
        "op": "qualify",
        "passed": True,
        "family": family,
        "module": module_name,
        "case": case["id"],
        "actual_result_sha256": actual_result_sha256,
        "independent_correctness_gate_sha256": independently_checked,
        "actual_snapshot_checked": True,
        "timing_performed": False,
        "clock_accessed": False,
        "guard_persistent": True,
        "registry_provenance": after["registry_provenance"],
        "native_mapping_provenance": after["native_mapping_provenance"],
    }

'''

QUALIFICATION_DEFINITION_MARKER = "\ndef observe_case(candidate, request):\n"
QUALIFICATION_DISPATCH_MARKER = (
    '            elif operation == "observe":\n'
    '                result = observe_case(candidate, request)'
)


class PublicPracticeError(RuntimeError):
    """A frozen public provenance, isolation, or measurement gate failed."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise PublicPracticeError(message)


def candidate_imports() -> list[str]:
    return sorted(
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    )


def require_candidate_free() -> None:
    require(
        not candidate_imports(),
        f"the public V8 controller imported a candidate: {candidate_imports()!r}",
    )


def valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def value_digest(value: Any) -> str:
    return hashlib.sha256(json_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), f"missing owned file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1_048_576), b""):
            digest.update(block)
    return digest.hexdigest()


def require_pinned_file(path: Path, expected: str | None, label: str) -> str:
    require(
        valid_sha256(expected),
        f"{label} has not yet been finalized and independently SHA-256 pinned",
    )
    observed = file_sha256(path)
    require(observed == expected, f"the frozen {label} changed")
    return observed


def read_pinned_json(path: Path, digest: str | None, label: str) -> dict[str, Any]:
    require_pinned_file(path, digest, label)
    try:
        with path.open("rb") as stream:
            document = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PublicPracticeError(f"invalid frozen {label}") from error
    require(isinstance(document, dict), f"the frozen {label} is not an object")
    return document


def require_pinned_python() -> None:
    require(
        platform.python_implementation() == "CPython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and Path(sys.executable).resolve() == PINNED_PYTHON.resolve(),
        "public V8 requires the exact pinned stable CPython 3.14.6",
    )


def exact_output(value: Path, expected: Path, label: str) -> Path:
    actual = value.resolve()
    require(actual == expected.resolve(), f"{label} is not the exclusive V8 path")
    require(
        actual.is_relative_to(VERSION_ROOT.resolve()),
        f"{label} escaped the public V8 evidence directory",
    )
    return actual


def checked_owned_path(relative: str, label: str) -> Path:
    require(isinstance(relative, str) and bool(relative), f"invalid {label}")
    item = Path(relative)
    require(not item.is_absolute(), f"{label} escaped the owned repository")
    target = (ROOT / item).resolve()
    require(target.is_relative_to(ROOT.resolve()), f"{label} escaped the repository")
    return target


def pack_public(value: Any) -> Any:
    if isinstance(value, bytes):
        return {PACKING_MARKER: "bytes", "hex": value.hex()}
    if isinstance(value, bytearray):
        return {PACKING_MARKER: "bytearray", "hex": bytes(value).hex()}
    if isinstance(value, memoryview):
        return {PACKING_MARKER: "memoryview", "hex": bytes(value).hex()}
    if isinstance(value, tuple):
        return {PACKING_MARKER: "tuple", "items": [pack_public(item) for item in value]}
    if isinstance(value, list):
        return [pack_public(item) for item in value]
    if isinstance(value, dict):
        return {key: pack_public(item) for key, item in value.items()}
    return value


NON_SEMANTIC_CASE_KEYS = frozenset({
    "api", "pattern", "flags", "string", "lifecycle", "id", "category",
    "cohort", "ops", "weight",
})


def canonical_public(value: Any) -> Any:
    """Use the frozen generator's exact type-sensitive identity encoding."""

    if value is None:
        return ["none"]
    if isinstance(value, bool):
        return ["bool", value]
    if isinstance(value, int):
        return ["int", str(value)]
    if isinstance(value, str):
        return ["text", value.encode("utf-8", "surrogatepass").hex()]
    if isinstance(value, bytes):
        return ["bytes", value.hex()]
    if isinstance(value, bytearray):
        return ["bytearray", bytes(value).hex()]
    if isinstance(value, memoryview):
        return ["memoryview", bytes(value).hex(), value.format, value.readonly]
    if isinstance(value, tuple):
        return ["tuple", [canonical_public(item) for item in value]]
    if isinstance(value, list):
        return ["list", [canonical_public(item) for item in value]]
    if isinstance(value, dict):
        marker = value.get(PACKING_MARKER)
        if marker in {"bytes", "bytearray", "memoryview"}:
            require(set(value) == {PACKING_MARKER, "hex"}, "invalid packed public buffer")
            encoded = value["hex"]
            require(isinstance(encoded, str), "invalid packed public buffer payload")
            try:
                payload = bytes.fromhex(encoded)
            except ValueError as error:
                raise PublicPracticeError("invalid packed public buffer hexadecimal") from error
            return [marker, payload.hex()]
        if marker == "tuple":
            require(
                set(value) == {PACKING_MARKER, "items"}
                and isinstance(value["items"], list),
                "invalid packed public tuple",
            )
            return ["tuple", [canonical_public(item) for item in value["items"]]]
        require(marker is None, "unknown or reserved public serialization marker")
        pairs = [
            (canonical_public(key), canonical_public(item))
            for key, item in value.items()
        ]
        return ["dict", sorted(pairs, key=lambda pair: json_bytes(pair[0]))]
    raise PublicPracticeError(f"unsupported canonical public value: {type(value).__name__}")


def semantic_identity(case: Mapping[str, Any]) -> str:
    require(isinstance(case, dict), "the frozen public case identity is not an object")
    fields = ("api", "pattern", "flags", "string", "lifecycle")
    require(all(field in case for field in fields), "the public case identity is incomplete")
    arguments = {
        key: value for key, value in case.items()
        if key not in NON_SEMANTIC_CASE_KEYS
    }
    return value_digest([
        canonical_public(case["api"]),
        canonical_public(case["pattern"]),
        canonical_public(case["flags"]),
        canonical_public(case["string"]),
        canonical_public(case["lifecycle"]),
        canonical_public(arguments),
    ])


def unpack_public(value: Any) -> Any:
    if isinstance(value, list):
        return [unpack_public(item) for item in value]
    if not isinstance(value, dict):
        return value
    marker = value.get(PACKING_MARKER)
    if marker is None:
        return {key: unpack_public(item) for key, item in value.items()}
    if marker in {"bytes", "bytearray", "memoryview"}:
        require(set(value) == {PACKING_MARKER, "hex"}, "invalid public byte representation")
        try:
            payload = bytes.fromhex(value["hex"])
        except (TypeError, ValueError) as error:
            raise PublicPracticeError("invalid public byte representation") from error
        return {
            "bytes": bytes,
            "bytearray": bytearray,
            "memoryview": memoryview,
        }[marker](payload)
    if marker == "tuple":
        require(
            set(value) == {PACKING_MARKER, "items"}
            and isinstance(value["items"], list),
            "invalid public tuple representation",
        )
        return tuple(unpack_public(item) for item in value["items"])
    raise PublicPracticeError("unknown public calibration serialization marker")


def result_density(value: Any) -> str:
    count = 0 if value is None else len(value) if isinstance(value, (list, tuple)) else 1
    return "none" if count == 0 else "one" if count == 1 else "few" if count <= 8 else "many"


def source_kind(case: Mapping[str, Any]) -> str:
    require(isinstance(case, dict), "public source-kind case is not an object")
    explicit = case.get("subject_kind")
    require(
        explicit is None or explicit in {"text", "bytes", "bytearray", "memoryview"},
        "unsupported public subject-kind declaration",
    )
    field = "pattern" if case.get("api") in {"compile", "escape"} else "string"
    value = unpack_public(case.get(field))
    if explicit is not None:
        if explicit == "text":
            require(isinstance(value, str), "public text subject changed its value type")
        else:
            require(
                isinstance(value, (bytes, bytearray, memoryview)),
                "public binary subject changed its value type",
            )
        return explicit
    if isinstance(value, str):
        return "text"
    if isinstance(value, bytes):
        return "bytes"
    if isinstance(value, bytearray):
        return "bytearray"
    if isinstance(value, memoryview):
        return "memoryview"
    raise PublicPracticeError("cannot derive the frozen public source kind")


def executable_public_case(case: dict[str, Any]) -> dict[str, Any]:
    """Materialize the exact frozen public buffer kind for both worker roles."""

    require(isinstance(case, dict), "the executable V8 public case is not an object")
    if case.get("api") in {"compile", "escape"}:
        return case
    declared = case.get("subject_kind")
    require(
        declared is None or declared in {"text", "bytes", "bytearray", "memoryview"},
        "the executable public case declared an unsupported input type",
    )
    if declared is None:
        return case
    subject = unpack_public(case.get("string"))
    if declared == "text":
        require(isinstance(subject, str), "a public text case lost its actual text")
        return case
    require(
        isinstance(subject, (bytes, bytearray, memoryview)),
        "a declared public buffer has no actual binary source",
    )
    converted: bytes | bytearray | memoryview
    if declared == "bytes":
        converted = bytes(subject)
    elif declared == "bytearray":
        converted = bytearray(subject)
    else:
        converted = memoryview(subject)
    executable = dict(case)
    executable["string"] = pack_public(converted)
    require(
        executable["id"] == case["id"]
        and executable.get("api") == case.get("api")
        and executable.get("cohort") == case.get("cohort")
        and executable.get("category") == case.get("category")
        and executable.get("subject_kind") == declared,
        "a concrete public buffer changed its frozen case or workload identity",
    )
    return executable


def process_memory_valid(response: Mapping[str, Any]) -> bool:
    return all(
        isinstance(response.get(field), int)
        and not isinstance(response.get(field), bool)
        and response[field] >= 0
        for field in ("rss_before_kb", "rss_after_kb", "hwm_kb", "peak_traced_bytes")
    ) and response["hwm_kb"] >= max(response["rss_before_kb"], response["rss_after_kb"])


def paired_order(case_id: str, trial: int) -> tuple[str, ...]:
    require(isinstance(case_id, str) and bool(case_id), "missing paired case identity")
    require(
        isinstance(trial, int) and not isinstance(trial, bool) and 0 <= trial < TRIALS,
        "invalid paired public trial",
    )
    order = list(MODULES)
    random.Random(ORDER_SEED + trial * 1009 + sum(map(ord, case_id))).shuffle(order)
    return tuple(order)


def percentile(values: list[float], fraction: float) -> float:
    require(bool(values), "cannot calculate a confidence interval from empty samples")
    require(0.0 <= fraction <= 1.0, "confidence percentile escaped its bounds")
    ordered = sorted(values)
    location = fraction * (len(ordered) - 1)
    lower = math.floor(location)
    upper = math.ceil(location)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (location - lower)


def paired_interval(
    log_ratios: list[float],
    case_id: str,
    candidate: str,
    *,
    draws: int = BOOTSTRAPS,
) -> tuple[float, float, float]:
    require(bool(log_ratios), "cannot bootstrap an empty paired comparison")
    require(
        isinstance(draws, int) and not isinstance(draws, bool) and draws >= 2,
        "invalid deterministic public bootstrap denominator",
    )
    require(all(math.isfinite(value) for value in log_ratios), "invalid paired log speedup")
    seed = int.from_bytes(
        hashlib.sha256(f"{BOOTSTRAP_SEED}:{case_id}:{candidate}".encode()).digest()[:8],
        "big",
    )
    generator = random.Random(seed)
    size = len(log_ratios)
    samples = [
        math.exp(math.fsum(log_ratios[generator.randrange(size)] for _ in range(size)) / size)
        for _ in range(draws)
    ]
    return (
        math.exp(math.fsum(log_ratios) / size),
        percentile(samples, 0.025),
        percentile(samples, 0.975),
    )


def validate_campaign(
    family: str,
    document: Mapping[str, Any],
    base: Mapping[str, Any],
) -> None:
    module = f"candidates.{family}_candidate"
    require(
        family in CAMPAIGN_DIGESTS
        and document.get("schema") == "rebar-rust-campaign-gate-v1"
        and document.get("postfinal_schema") == CAMPAIGN_SCHEMA
        and document.get("controller_source_path")
        == "tools/rust_v8_multi_candidate_campaign_postfinal_v5.py"
        and document.get("controller_source_sha256") == CONTROLLER_SOURCE_SHA256
        and document.get("ancestor_source_path")
        == "tools/rust_v8_multi_candidate_campaign_postfinal_v4.py"
        and document.get("ancestor_source_sha256") == CONTROLLER_ANCESTOR_SHA256
        and document.get("candidate") == module
        and document.get("passed") is True
        and document.get("required_correctness_step_count") == len(CAMPAIGN_STAGES)
        and document.get("mode") == "sealed-practice-only"
        and document.get("performance") == "NOT MEASURED"
        and document.get("holdout_accessed") is False
        and document.get("timing_performed") is False
        and document.get("fail_fast") is True
        and document.get("pinned_cpython") == "3.14.6"
        and document.get("python_version") == "3.14.6",
        f"the exact current 22-stage {family} correctness campaign has not passed",
    )
    goal = document.get("goal")
    require(
        isinstance(goal, dict)
        and goal.get("passed") is True
        and goal.get("expected_sha256") == GOAL_SHA256
        and goal.get("actual_sha256") == GOAL_SHA256,
        f"the {family} campaign is not bound to the immutable goal",
    )
    steps = document.get("steps")
    require(
        isinstance(steps, list)
        and len(steps) == len(CAMPAIGN_STAGES)
        and all(isinstance(step, dict) for step in steps)
        and tuple(step["name"] for step in steps) == CAMPAIGN_STAGES
        and all(step.get("passed") is True and step.get("status") == "passed" for step in steps),
        f"the {family} campaign omitted, reordered, or failed a correctness stage",
    )
    by_name = {step["name"]: step for step in steps}
    for stage, expected in (
        ("candidate-frozen-edge-proof", 223_198),
        ("candidate-frozen-deep-public-proof", 393),
        ("frozen-cross-family-observability", 479),
        ("official-cpython-tests", 146),
        ("full-unicode-plane", 4_494_555),
    ):
        require(
            by_name[stage].get("expected_checks") == expected,
            f"the {family} campaign weakened its {stage} correctness denominator",
        )
    unicode = by_name["full-unicode-plane"].get("evidence")
    require(
        isinstance(unicode, dict)
        and unicode.get("schema") == "rebar-rust-unicode-probe-v1"
        and unicode.get("module") == module
        and unicode.get("correctness_checks") == 4_494_555
        and unicode.get("failed") == 0,
        f"the {family} campaign omitted the complete Unicode-plane proof",
    )
    static = by_name["from-scratch-static-audit"].get("evidence")
    require(isinstance(static, dict), f"the {family} campaign omitted its V5 audit")
    exact_locale = {
        "schema": LOCALE_SCHEMA,
        "path": str(LOCALE_REPORT_PATH.relative_to(ROOT)),
        "sha256": LOCALE_REPORT_SHA256,
        "source_path": str(LOCALE_SOURCE_PATH.relative_to(ROOT)),
        "source_sha256": LOCALE_SOURCE_SHA256,
        "official_methods": 146,
        "candidate_family": family,
        "all_roles": ["re", "rust", "vm", "zig"],
    }
    exact_strict = {
        "schema": "rebar-postfinal-no-delegation-audit-v5",
        "path": str(STRICT_AUDIT_PATH.relative_to(ROOT)),
        "sha256": STRICT_AUDIT_SHA256,
        "source_path": str(STRICT_AUDIT_SOURCE_PATH.relative_to(ROOT)),
        "source_sha256": STRICT_AUDIT_SOURCE_SHA256,
        "strict_control_count": 32,
        "inherited_control_count": 76,
    }
    exact_controller = {
        "postfinal_schema": CAMPAIGN_SCHEMA,
        "source_path": str(CONTROLLER_SOURCE_PATH.relative_to(ROOT)),
        "source_sha256": CONTROLLER_SOURCE_SHA256,
        "ancestor_source_path": str(CONTROLLER_ANCESTOR_PATH.relative_to(ROOT)),
        "ancestor_source_sha256": CONTROLLER_ANCESTOR_SHA256,
        "expected_complete_production_role_count": (
            CAMPAIGN_PRODUCTION_ROLE_COUNTS[family]
        ),
    }
    require(
        static.get("sealed_locale_provenance") == exact_locale
        and static.get("sealed_no_delegation_provenance") == exact_strict
        and static.get("sealed_campaign_controller") == exact_controller,
        f"the {family} V5 campaign changed real-locale, no-delegation, or ownership provenance",
    )
    stripped = {
        key: value for key, value in static.items()
        if key not in {
            "sealed_locale_provenance", "sealed_no_delegation_provenance",
            "sealed_campaign_controller",
        }
    }
    require(stripped == base, f"the {family} campaign substituted the current V5 audit")
    official = by_name["official-cpython-tests"].get("evidence")
    require(
        isinstance(official, dict)
        and official.get("schema") == "rebar-cpython-re-result-v1"
        and official.get("module") == module
        and official.get("methods") == 146
        and official.get("passed") == 146
        and official.get("skipped") == 0
        and official.get("failed") == 0
        and official.get("crashes") == 0
        and official.get("timeouts") == 0
        and official.get("runner_sha256") == ORIGINAL_OFFICIAL_RUNNER_SHA256
        and official.get("source_sha256") == ORIGINAL_OFFICIAL_SOURCE_SHA256
        and isinstance(official.get("records"), list)
        and len(official["records"]) == 146
        and all(
            isinstance(row, dict)
            and row.get("status") == "passed"
            and row.get("skipped") == 0
            and row.get("reason") is None
            and not row.get("failures")
            for row in official["records"]
        ),
        f"the {family} campaign omitted an unskipped original CPython test",
    )
    official_names: set[str] = set()
    for result in official["records"]:
        name = result.get("test")
        require(
            isinstance(name, str) and name not in official_names,
            f"the {family} campaign duplicated or removed an official CPython method",
        )
        official_names.add(name)
    require(
        "ReTests.test_locale_caching" in official_names
        and "ReTests.test_locale_compiled" in official_names
        and value_digest(sorted(official_names)) == ORIGINAL_SELECTED_METHOD_SHA256,
        f"the {family} campaign changed its immutable official locale-test identities",
    )


def stage10_correctness_contract() -> dict[str, Any]:
    """Return the sole, exact public V8 manifest compatibility contract."""

    return {
        "source_path": str(STAGE10_SOURCE_PATH.relative_to(ROOT)),
        "source_sha256": STAGE10_SOURCE_SHA256,
        "protocol_path": str(STAGE10_PROTOCOL_PATH.relative_to(ROOT)),
        "protocol_sha256": STAGE10_PROTOCOL_SHA256,
        "self_oracle_path": str(STAGE10_SELF_ORACLE_PATH.relative_to(ROOT)),
        "self_oracle_sha256": STAGE10_SELF_ORACLE_SHA256,
        "all_candidates_path": str(STAGE10_ALL_CANDIDATE_PATH.relative_to(ROOT)),
        "all_candidates_sha256": STAGE10_ALL_CANDIDATE_SHA256,
        "matrix_sha256": STAGE10_MATRIX_SHA256,
        "cohorts": len(STAGE10_COHORT_CASES),
        "cases": STAGE10_CASES,
        "stdlib_checks": STAGE10_STDLIB_CHECKS,
        "candidate_checks": STAGE10_CANDIDATE_CHECKS,
    }


def validate_stage10_correctness_contract(document: Any) -> dict[str, Any]:
    """Reject omitted, extra, renamed, or substituted manifest proof pins."""

    expected = stage10_correctness_contract()
    require(
        isinstance(document, dict) and set(document) == set(expected),
        "the public V8 manifest changed its exact Stage 10 proof fields",
    )
    for field, value in expected.items():
        actual = document.get(field)
        require(
            type(actual) is type(value) and actual == value,
            f"the public V8 Stage 10 correctness proof changed: {field}",
        )
    return document


def stage10_preserved_history_contract() -> dict[str, Any]:
    """Record actual historical failures without declaring either a pass."""

    return {
        "source_path": str(STAGE10_SOURCE_PATH.relative_to(ROOT)),
        "source_sha256": STAGE10_SOURCE_SHA256,
        "protocol_path": str(STAGE10_PROTOCOL_PATH.relative_to(ROOT)),
        "protocol_sha256": STAGE10_PROTOCOL_SHA256,
        "observation_domain": STAGE10_OBSERVATION_DOMAIN,
        "previous_public_source_sha256": UNIVERSAL_SOURCE_SHA256,
        "previous_public_report_sha256": UNIVERSAL_REPORT_SHA256,
        "base_audit_sha256": BASE_AUDIT_SHA256,
        "strict_audit_sha256": STRICT_AUDIT_SHA256,
        "official_locale_sha256": LOCALE_REPORT_SHA256,
        "official_selected_method_sha256": ORIGINAL_SELECTED_METHOD_SHA256,
        "official_methods_per_role": 146,
        "official_role_count": 4,
        "official_skipped": 0,
        "previous_self_oracle_failure_sha256": PRESERVED_STAGE07_FAILURE_SHA256,
        "previous_self_oracle_failure_count": 32,
        "previous_hash_nondeterminism_only": True,
        "previous_stage08_self_oracle_sha256": (
            PRESERVED_STAGE08_SELF_ORACLE_SHA256
        ),
        "previous_stage08_rust_failure_sha256": (
            PRESERVED_STAGE08_RUST_FAILURE_SHA256
        ),
        "previous_stage08_rust_failure_count": 256,
        "previous_stage08_rust_matching_observations": 3_328,
        "previous_stage08_rust_failure_preserved": True,
    }


def validate_stage10_preserved_history(document: Any) -> dict[str, Any]:
    """Reject substituted locale, source, audit, or actual failure history."""

    require(
        isinstance(document, dict),
        "the Stage 10 source-bound native provenance is missing",
    )
    for field, expected in stage10_preserved_history_contract().items():
        actual = document.get(field)
        require(
            type(actual) is type(expected) and actual == expected,
            f"Stage 10 substituted actual provenance or failure history: {field}",
        )
    return document


def authenticate_stage10_reference(
    oracle: Any,
    encoded_baseline: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Restore portable text before the real two-argument V10 validator."""

    authenticator = getattr(oracle, "_authenticate_current_provenance", None)
    previous = getattr(oracle, "previous", None)
    restore = getattr(previous, "_restore_portable", None)
    stage07 = getattr(oracle, "stage07", None)
    validator = getattr(stage07, "_validate_self_oracle", None)
    require(
        callable(authenticator) and callable(restore) and callable(validator),
        "the genuine Stage 10 self-oracle authenticator or codec is missing",
    )
    authenticated = authenticator()
    restored_baseline = restore(encoded_baseline)
    require(
        isinstance(authenticated, dict)
        and isinstance(restored_baseline, dict),
        "Stage 10 did not authenticate reversible reference provenance",
    )
    verified = validator(restored_baseline, authenticated)
    require(
        isinstance(verified, dict),
        "the genuine Stage 10 self-oracle validator rejected its reference",
    )
    return authenticated, verified


def validate_stage10_family_guard(
    family: str,
    guard: Any,
    expected_native: Mapping[str, str],
) -> dict[str, Any]:
    """Require a real independent observer and a separately guarded matcher."""

    native_module = {
        "rust": "candidates._rust_bridge",
        "vm": "candidates._vm_native",
        "zig": "candidates._zig_bridge",
    }
    canonical_native = {
        path: fingerprint
        for role, (path, fingerprint) in EXPECTED_NATIVE_FILES.items()
        if role.startswith(f"candidates.{family}_candidate:")
    }
    require(
        family in native_module
        and isinstance(expected_native, dict)
        and bool(expected_native)
        and expected_native == canonical_native
        and all(valid_sha256(value) for value in expected_native.values()),
        "the Stage 10 candidate has no exact owned native family",
    )
    expected_modules = sorted(
        (f"candidates.{family}_candidate", native_module[family])
    )
    require(
        isinstance(guard, dict)
        and guard.get("enabled") is True
        and guard.get("family") == family
        and guard.get("stdlib_re_blocked") is True
        and guard.get("cpython_sre_blocked") is True
        and guard.get("third_party_regex_blocked") is True
        and guard.get("cross_family_blocked") is True
        and guard.get("foreign_dynamic_libraries_blocked") is True
        and guard.get("native_loader_aliases_blocked")
        == list(STAGE10_NATIVE_LOADER_ALIASES)
        and guard.get("loaded_candidate_modules") == expected_modules,
        f"the Stage 10 {family} proof weakened its audited native engine guard",
    )
    receipt = guard.get("isolated_public_metadata")
    expected_receipt = {
        "enabled": True,
        "schema": STAGE10_METADATA_SCHEMA,
        "source_sha256": STAGE10_SOURCE_SHA256,
        "role": family,
        "surface_cases": 256,
        "production_matching_executed": False,
        "metadata_and_matcher_processes_distinct": True,
        "matcher_inspect_loaded": False,
        "matcher_tokenizer_loaded": False,
    }
    require(
        isinstance(receipt, dict)
        and set(receipt) == {*expected_receipt, "record_sha256"}
        and valid_sha256(receipt.get("record_sha256")),
        f"the Stage 10 {family} proof omitted authenticated isolated metadata",
    )
    for field, value in expected_receipt.items():
        actual = receipt.get(field)
        require(
            type(actual) is type(value) and actual == value,
            f"the Stage 10 {family} process-isolation proof changed: {field}",
        )
    return guard


def verified_stage10_proof(universal: Mapping[str, Any]) -> dict[str, Any]:
    """Authenticate actual reversible dual-Python and all-family V10 PASS."""

    require_candidate_free()
    require_pinned_file(
        STAGE10_SOURCE_PATH,
        STAGE10_SOURCE_SHA256,
        "final independently reviewed Stage 10 source",
    )
    require_pinned_file(
        STAGE10_PROTOCOL_PATH,
        STAGE10_PROTOCOL_SHA256,
        "final frozen eight-cohort Stage 10 protocol",
    )
    encoded_baseline = read_pinned_json(
        STAGE10_SELF_ORACLE_PATH,
        STAGE10_SELF_ORACLE_SHA256,
        "actual passing independent dual-CPython Stage 10 self-oracle",
    )
    encoded_candidates = read_pinned_json(
        STAGE10_ALL_CANDIDATE_PATH,
        STAGE10_ALL_CANDIDATE_SHA256,
        "actual passing Rust, C, and Zig Stage 10 contract",
    )
    oracle = importlib.import_module(
        "tools.python_re_universal_public_oracle_stage10"
    )
    require(
        Path(getattr(oracle, "__file__", "")).resolve()
        == STAGE10_SOURCE_PATH.resolve()
        and getattr(oracle, "SOURCE_RELATIVE", None)
        == str(STAGE10_SOURCE_PATH.relative_to(ROOT))
        and getattr(oracle, "PROTOCOL_RELATIVE", None)
        == str(STAGE10_PROTOCOL_PATH.relative_to(ROOT))
        and getattr(oracle, "SCHEMA", None) == STAGE10_SCHEMA
        and getattr(oracle, "SELF_ORACLE_SCHEMA", None)
        == STAGE10_SELF_ORACLE_SCHEMA
        and getattr(oracle, "ALL_CANDIDATE_SCHEMA", None)
        == STAGE10_ALL_CANDIDATE_SCHEMA
        and getattr(oracle, "METADATA_SCHEMA", None) == STAGE10_METADATA_SCHEMA
        and getattr(oracle, "OBSERVATION_DOMAIN", None)
        == STAGE10_OBSERVATION_DOMAIN
        and getattr(oracle, "MATRIX_SHA256", None) == STAGE10_MATRIX_SHA256
        and getattr(oracle, "REQUIRED_CANDIDATES", None)
        == ("rust", "vm", "zig")
        and callable(getattr(oracle, "_stage10_context", None)),
        "the exact independent Stage 10 producer or codec was substituted",
    )
    require_candidate_free()
    with oracle._stage10_context():
        authenticated, baseline = authenticate_stage10_reference(
            oracle,
            encoded_baseline,
        )
        candidates = oracle.previous._restore_portable(encoded_candidates)
        require(
            isinstance(candidates, dict),
            "the genuine Stage 10 reversible Unicode evidence is invalid",
        )
        expected_self = {
            "schema": STAGE10_SELF_ORACLE_SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "python": "3.14.6",
            "source_path": str(STAGE10_SOURCE_PATH.relative_to(ROOT)),
            "source_sha256": STAGE10_SOURCE_SHA256,
            "protocol_path": str(STAGE10_PROTOCOL_PATH.relative_to(ROOT)),
            "protocol_sha256": STAGE10_PROTOCOL_SHA256,
            "seed": STAGE10_SEED,
            "seed_domain": STAGE10_SEED_DOMAIN,
            "matrix_sha256": STAGE10_MATRIX_SHA256,
            "cohorts": 8,
            "cohort_cases": STAGE10_COHORT_CASES,
            "cases": STAGE10_CASES,
            "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
            "stdlib_checks": STAGE10_STDLIB_CHECKS,
            "mismatches": 0,
            "failure_records": [],
            "candidate_imports": 0,
            "candidate_processes": 0,
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
        for field, expected in expected_self.items():
            actual = baseline.get(field)
            require(
                type(actual) is type(expected) and actual == expected,
                f"the actual Stage 10 dual-Python proof changed: {field}",
            )
        rows = baseline.get("baseline_records")
        expected_ids = [
            f"{cohort}:{index:04d}"
            for cohort, count in STAGE10_COHORT_CASES.items()
            for index in range(count)
        ]
        require(
            isinstance(rows, list)
            and len(rows) == STAGE10_CASES
            and all(isinstance(row, dict) for row in rows)
            and [row.get("id") for row in rows] == expected_ids,
            "the genuine Stage 10 Python references omitted a frozen obligation",
        )
        reference_digest = oracle.previous.digest(rows)
        require(
            baseline.get("baseline_record_sha256") == reference_digest
            and baseline.get("second_record_sha256") == reference_digest,
            "both reversible Stage 10 Python references did not agree",
        )

    expected_candidates = {
        "schema": STAGE10_ALL_CANDIDATE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "selected": "all",
        "selected_candidates": ["rust", "vm", "zig"],
        "completed_candidates": ["rust", "vm", "zig"],
        "comparison_complete": True,
        "python": "3.14.6",
        "source_path": str(STAGE10_SOURCE_PATH.relative_to(ROOT)),
        "source_sha256": STAGE10_SOURCE_SHA256,
        "protocol_path": str(STAGE10_PROTOCOL_PATH.relative_to(ROOT)),
        "protocol_sha256": STAGE10_PROTOCOL_SHA256,
        "seed": STAGE10_SEED,
        "seed_domain": STAGE10_SEED_DOMAIN,
        "matrix_sha256": STAGE10_MATRIX_SHA256,
        "cohorts": 8,
        "cohort_cases": STAGE10_COHORT_CASES,
        "cases_per_candidate": STAGE10_CASES,
        "candidate_checks": STAGE10_CANDIDATE_CHECKS,
        "previous_public_cases": ORIGINAL_CASE_COUNT,
        "previous_public_comparisons": 1_179_648,
        "combined_public_comparisons": 1_190_400,
        "mismatches": 0,
        "self_oracle_path": str(STAGE10_SELF_ORACLE_PATH.relative_to(ROOT)),
        "self_oracle_sha256": STAGE10_SELF_ORACLE_SHA256,
        "external_regex_packages": 0,
        "candidate_cross_delegation": False,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for field, expected in expected_candidates.items():
        actual = candidates.get(field)
        require(
            type(actual) is type(expected) and actual == expected,
            f"the actual all-family Stage 10 correctness proof changed: {field}",
        )
    current = baseline.get("current_provenance")
    require(
        isinstance(current, dict)
        and current == authenticated
        and candidates.get("current_provenance") == current,
        "Stage 10 used different baseline and candidate native provenance",
    )
    validate_stage10_preserved_history(current)
    inherited_audit = universal.get("audit")
    require(
        isinstance(inherited_audit, dict)
        and current.get("source_sha256_by_family")
        == inherited_audit.get("source_sha256")
        and current.get("native_sha256_by_family")
        == inherited_audit.get("native_binary_sha256"),
        "Stage 10 mixed candidate sources or native engines from another campaign",
    )
    source_families = current.get("source_sha256_by_family")
    native_families = current.get("native_sha256_by_family")
    require(
        isinstance(source_families, dict)
        and set(source_families) == {"rust", "vm", "zig"}
        and isinstance(native_families, dict)
        and set(native_families) == {"rust", "vm", "zig"},
        "Stage 10 did not qualify three disjoint owned source and native families",
    )
    flattened: dict[str, str] = {}
    for family in ("rust", "vm", "zig"):
        family_sources = source_families[family]
        require(isinstance(family_sources, dict), "a Stage 10 source family is invalid")
        for relative, fingerprint in family_sources.items():
            require(
                isinstance(relative, str)
                and relative not in flattened
                and valid_sha256(fingerprint),
                "Stage 10 duplicated or substituted an owned native source",
            )
            flattened[relative] = fingerprint
    require(
        flattened == EXPECTED_SOURCE_FINGERPRINTS,
        "Stage 10 did not bind all twelve independently owned candidate sources",
    )
    outcomes = candidates.get("candidate_reports")
    require(
        isinstance(outcomes, dict) and set(outcomes) == {"rust", "vm", "zig"},
        "the actual Stage 10 proof omitted an independently built candidate",
    )
    for family in ("rust", "vm", "zig"):
        outcome = outcomes[family]
        expected_native = {
            path: digest
            for role, (path, digest) in EXPECTED_NATIVE_FILES.items()
            if role.startswith(f"candidates.{family}_candidate:")
        }
        require(
            isinstance(outcome, dict)
            and outcome.get("candidate") == family
            and outcome.get("module") == f"candidates.{family}_candidate"
            and outcome.get("status") == "PASS"
            and outcome.get("cases") == STAGE10_CASES
            and outcome.get("cohort_cases") == STAGE10_COHORT_CASES
            and outcome.get("record_sha256") == reference_digest
            and outcome.get("mismatches") == 0
            and outcome.get("failure_records") == []
            and outcome.get("failures_recorded") == 0
            and native_families.get(family) == expected_native
            and outcome.get("native_binary_sha256") == expected_native
            and outcome.get("benchmark_or_timing_executed") is False
            and outcome.get("holdout_cases_read") == 0
            and outcome.get("performance") == "NOT MEASURED",
            f"the actual Stage 10 {family} proof did not match every Python answer",
        )
        validate_stage10_family_guard(
            family,
            outcome.get("guard"),
            expected_native,
        )
    require(
        candidates.get("locales") == baseline.get("locales"),
        "Stage 10 candidate locales differ from both genuine Python references",
    )
    require_candidate_free()
    return {"stage10_correctness": stage10_correctness_contract()}


def verified_provenance() -> dict[str, Any]:
    """Read only the exact named V8 source, current V5 audits, and proofs."""

    require_candidate_free()
    require_pinned_python()
    for path, digest, label in (
        (GOAL_PATH, GOAL_SHA256, "immutable goal"),
        (V7_SOURCE_PATH, V7_SOURCE_SHA256, "final V7 public-runner source"),
        (V7_PROTOCOL_PATH, V7_PROTOCOL_SHA256, "final V7 public protocol"),
        (GENERATOR_SOURCE_PATH, GENERATOR_SOURCE_SHA256, "final V8 public generator"),
        (PROTOCOL_PATH, PROTOCOL_SHA256, "frozen V8 public protocol"),
        (BASE_AUDIT_SOURCE_PATH, BASE_AUDIT_SOURCE_SHA256, "V5 source-audit producer"),
        (STRICT_AUDIT_SOURCE_PATH, STRICT_AUDIT_SOURCE_SHA256, "V5 strict-audit producer"),
        (GUARD_SOURCE_PATH, GUARD_SOURCE_SHA256, "immutable V1 worker source"),
        (LOCALE_SOURCE_PATH, LOCALE_SOURCE_SHA256, "passing current CPython locale producer"),
        (UNIVERSAL_SOURCE_PATH, UNIVERSAL_SOURCE_SHA256, "passing all-family stage-06 producer"),
        (CONTROLLER_SOURCE_PATH, CONTROLLER_SOURCE_SHA256, "V5 campaign controller"),
        (CONTROLLER_ANCESTOR_PATH, CONTROLLER_ANCESTOR_SHA256, "V5 campaign ancestor"),
    ):
        require_pinned_file(path, digest, label)
    base = read_pinned_json(BASE_AUDIT_PATH, BASE_AUDIT_SHA256, "V5 from-scratch report")
    strict = read_pinned_json(STRICT_AUDIT_PATH, STRICT_AUDIT_SHA256, "V5 strict report")
    read_pinned_json(GUARD_REPORT_PATH, GUARD_REPORT_SHA256, "immutable V1 worker proof")
    locale = read_pinned_json(
        LOCALE_REPORT_PATH,
        LOCALE_REPORT_SHA256,
        "passing current all-family CPython locale report",
    )
    universal = read_pinned_json(
        UNIVERSAL_REPORT_PATH,
        UNIVERSAL_REPORT_SHA256,
        "passing current all-family stage-06 public correctness report",
    )
    require(
        base.get("postfinal_schema") == "rebar-postfinal-from-scratch-audit-v5"
        and base.get("status") == "PASS"
        and base.get("passed") is True
        and base.get("audit_source_sha256") == BASE_AUDIT_SOURCE_SHA256
        and base.get("verified_distinct_pipeline_count") == 4
        and base.get("self_test", {}).get("check_count") == 76
        and base.get("postfinal_wrapper_self_test", {}).get("check_count") == 198,
        "the independently source-bound V5 from-scratch audit has not passed",
    )
    require(
        strict.get("schema") == "rebar-postfinal-no-delegation-audit-v5"
        and strict.get("postfinal_schema") == "rebar-postfinal-no-delegation-audit-v5"
        and strict.get("status") == "PASS"
        and strict.get("result") == "PASS"
        and strict.get("passed") is True
        and strict.get("audit_source_sha256") == STRICT_AUDIT_SOURCE_SHA256
        and strict.get("base_audit_report_sha256") == BASE_AUDIT_SHA256
        and strict.get("base_audit_source_sha256") == BASE_AUDIT_SOURCE_SHA256
        and strict.get("inherited_control_count") == 76
        and strict.get("self_test", {}).get("check_count") == 32
        and strict.get("self_test", {}).get("passed") is True
        and strict.get("self_test", {}).get("failed") == []
        and strict.get("postfinal_wrapper_self_test", {}).get("check_count") == 676
        and strict.get("postfinal_wrapper_self_test", {}).get("passed") is True
        and strict.get("postfinal_wrapper_self_test", {}).get("failed") == [],
        "the independently source-bound V5 no-delegation audit has not passed",
    )
    sources = strict.get("qualified_source_fingerprints")
    native = strict.get("native_elf_fingerprints")
    require(
        isinstance(sources, dict) and sources == EXPECTED_SOURCE_FINGERPRINTS,
        "V5 omitted, substituted, or mixed a source-bound candidate family",
    )
    require(
        isinstance(native, dict)
        and native == {role: digest for role, (_path, digest) in EXPECTED_NATIVE_FILES.items()},
        "V5 omitted, substituted, or mixed a source-bound native engine",
    )
    require(
        all(valid_sha256(digest) for digest in sources.values())
        and all(valid_sha256(digest) for digest in native.values()),
        "the V5 independently owned candidate fingerprints are invalid",
    )
    for relative, digest in sources.items():
        require_pinned_file(
            checked_owned_path(relative, "V5 owned candidate source"),
            digest,
            f"current V5 source {relative}",
        )
    for role, (relative, digest) in EXPECTED_NATIVE_FILES.items():
        require_pinned_file(
            checked_owned_path(relative, "V5 owned native engine"),
            digest,
            f"current V5 native artifact {role}",
        )
    proof_records: list[dict[str, str]] = []
    for role, (relative, digest) in FROZEN_FAMILY_PROOFS.items():
        require_pinned_file(
            checked_owned_path(relative, "frozen independent candidate proof"),
            digest,
            f"source-bound V5 {role} correctness artifact",
        )
        proof_records.append({"role": role, "path": relative, "sha256": digest})
    require(
        locale.get("schema") == LOCALE_SCHEMA
        and locale.get("python") == "3.14.6"
        and locale.get("status") == "PASS"
        and locale.get("result") == "PASS"
        and locale.get("goal_sha256") == GOAL_SHA256
        and locale.get("qualified_source_fingerprints") == sources
        and locale.get("native_elf_fingerprints") == native
        and locale.get("timing_performed") is False
        and locale.get("performance") == "NOT MEASURED",
        "the exact four-family, no-skip CPython locale proof was substituted",
    )
    require(
        universal.get("schema") == "rebar-python-re-universal-public-oracle-v1"
        and universal.get("python") == "3.14.6"
        and universal.get("status") == "PASS"
        and universal.get("comparison_complete") is True
        and universal.get("mismatches") == 0
        and universal.get("cases") == ORIGINAL_CASE_COUNT
        and universal.get("case_sha256") == UNIVERSAL_CASE_SHA256
        and set(universal.get("completed_candidates", ())) == {"rust", "vm", "zig"}
        and set(universal.get("selected_candidates", ())) == {"rust", "vm", "zig"}
        and universal.get("benchmark_or_timing_executed") is False
        and universal.get("performance") == "NOT MEASURED"
        and universal.get("performance_fixtures_read") == 0,
        "the full source-bound current stage-06 public compatibility proof changed",
    )
    stage10 = verified_stage10_proof(universal)
    digests: list[str] = []
    campaigns: list[dict[str, str]] = []
    for family in ("rust", "vm", "zig"):
        digest = CAMPAIGN_DIGESTS[family]
        path = (
            ROOT / "candidates" / "evidence"
            / f"rust-v8-{family}-postfinal-locale-v5-sealed-campaign.json"
        )
        report = read_pinned_json(path, digest, f"current complete V5 {family} campaign")
        validate_campaign(family, report, base)
        require(isinstance(digest, str), "the V5 campaign was not pinned")
        digests.append(digest)
        campaigns.append({"family": family, "path": str(path.relative_to(ROOT)), "sha256": digest})
    require(len(set(digests)) == 3, "the three families reused one correctness campaign")
    require_candidate_free()
    return {
        "goal_sha256": GOAL_SHA256,
        "v7_source_sha256": V7_SOURCE_SHA256,
        "v7_protocol_sha256": V7_PROTOCOL_SHA256,
        "generator_source_sha256": GENERATOR_SOURCE_SHA256,
        "protocol_sha256": PROTOCOL_SHA256,
        "runner_sha256": file_sha256(SOURCE_PATH),
        "base_audit_sha256": BASE_AUDIT_SHA256,
        "strict_audit_sha256": STRICT_AUDIT_SHA256,
        "guard_source_sha256": GUARD_SOURCE_SHA256,
        "guard_report_sha256": GUARD_REPORT_SHA256,
        "locale_source_sha256": LOCALE_SOURCE_SHA256,
        "locale_report_sha256": LOCALE_REPORT_SHA256,
        "universal_source_sha256": UNIVERSAL_SOURCE_SHA256,
        "universal_report_sha256": UNIVERSAL_REPORT_SHA256,
        "campaign_controller_sha256": CONTROLLER_SOURCE_SHA256,
        "campaign_ancestor_sha256": CONTROLLER_ANCESTOR_SHA256,
        "campaigns": campaigns,
        "verified_family_proofs": proof_records,
        "qualified_source_fingerprints": sources,
        "native_elf_fingerprints": native,
        **stage10,
    }


def load_manifest(path: Path, provenance: Mapping[str, Any]) -> dict[str, Any]:
    exact = exact_output(path, MANIFEST_PATH, "frozen public V8 manifest")
    try:
        with exact.open("rb") as stream:
            document = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PublicPracticeError("cannot read the exact frozen public V8 manifest") from error
    require(isinstance(document, dict), "the V8 public manifest is not an object")
    require(
        document.get("schema") == PLAN_SCHEMA
        and document.get("python") == "3.14.6"
        and document.get("cohort") == COHORT
        and document.get("measurement_role") == "PUBLIC DEVELOPMENT; not independently secret"
        and document.get("seed_domain") == SEED_DOMAIN
        and document.get("selection_seed") == SELECTION_SEED
        and document.get("order_seed_domain") == SEED_DOMAIN + "/paired-order"
        and document.get("order_seed") == ORDER_SEED
        and document.get("bootstrap_seed_domain") == SEED_DOMAIN + "/bootstrap"
        and document.get("bootstrap_seed") == BOOTSTRAP_SEED
        and document.get("runner_path") == "tools/postfinal_public_expansion_v8.py"
        and document.get("runner_sha256") == GENERATOR_SOURCE_SHA256
        and document.get("protocol_path") == "performance/postfinal-public-v8/PROTOCOL.md"
        and document.get("protocol_sha256") == PROTOCOL_SHA256
        and document.get("cases") == CASE_COUNT
        and document.get("original_cases_preserved") == ORIGINAL_CASE_COUNT
        and document.get("all_bounded_workload_categories") == CATEGORY_COUNT
        and document.get("cases_per_category") == CASES_PER_CATEGORY
        and document.get("frozen_warmups") == WARMUPS
        and document.get("frozen_trials") == TRIALS
        and document.get("frozen_bootstrap_samples") == BOOTSTRAPS
        and document.get("expected_raw_rows") == EXPECTED_RAW_ROWS
        and document.get("expected_correctness_answers") == EXPECTED_CORRECTNESS_ANSWERS
        and document.get("expected_confidence_intervals") == EXPECTED_CONFIDENCE_INTERVALS
        and document.get("expected_process_native_checks") == EXPECTED_PROCESS_NATIVE_CHECKS
        and document.get("baseline") == MODULES[0]
        and document.get("candidates") == list(MODULES[1:])
        and document.get("maximum_subject_limit") == SUBJECT_LIMIT
        and document.get("maximum_result_limit") == RESULT_LIMIT
        and document.get("goal_sha256") == GOAL_SHA256
        and document.get("source_public_manifest")
        == "performance/postfinal-public-v6/manifest.json"
        and document.get("source_public_manifest_sha256") == PUBLIC_V6_MANIFEST_SHA256
        and document.get("qualified_source_fingerprints")
        == provenance["qualified_source_fingerprints"]
        and document.get("native_elf_fingerprints") == provenance["native_elf_fingerprints"]
        and document.get("candidate_imports") == []
        and document.get("historical_results_read") == 0
        and document.get("timing_performed") is False
        and document.get("performance") == "NOT MEASURED",
        "the prospective V8 public manifest changed a frozen population, seed, or proof",
    )
    oracle = document.get("independent_cpython_self_oracle")
    require(
        isinstance(oracle, dict)
        and oracle.get("workers") == 2
        and oracle.get("schema") == "rebar-postfinal-public-development-self-oracle-v8"
        and oracle.get("python") == "3.14.6"
        and oracle.get("failed") == 0,
        "both independently isolated CPython public self-oracles have not passed",
    )
    pinned_inputs = document.get("pinned_public_input_sha256")
    require(isinstance(pinned_inputs, dict), "the V8 generator omitted frozen public input pins")
    for relative, digest in (
        ("GOAL.md", GOAL_SHA256),
        ("performance/postfinal-public-v6/manifest.json", PUBLIC_V6_MANIFEST_SHA256),
        ("tools/postfinal_public_practice_v7.py", V7_SOURCE_SHA256),
        ("performance/postfinal-public-v7/PROTOCOL.md", V7_PROTOCOL_SHA256),
        ("tools/postfinal_from_scratch_audit_v5.py", BASE_AUDIT_SOURCE_SHA256),
        ("tools/postfinal_no_delegation_audit_v5.py", STRICT_AUDIT_SOURCE_SHA256),
        ("tools/postfinal_no_delegation_audit_v1.py", GUARD_SOURCE_SHA256),
        ("tools/postfinal_cpython_locale_oracle_v1.py", LOCALE_SOURCE_SHA256),
        ("tools/python_re_universal_public_oracle_stage06.py", UNIVERSAL_SOURCE_SHA256),
        ("candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json", BASE_AUDIT_SHA256),
        ("candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json", STRICT_AUDIT_SHA256),
    ):
        require(
            pinned_inputs.get(relative) == digest,
            f"the V8 generator substituted a frozen public input: {relative}",
        )
    for role, (relative, digest) in FROZEN_FAMILY_PROOFS.items():
        require(
            pinned_inputs.get(relative) == digest,
            f"the V8 generator substituted the exact frozen {role} proof",
        )
    require(
        "stage07_correctness" not in document,
        "the public V8 manifest misrepresented a failed Stage 07 proof",
    )
    stage10 = validate_stage10_correctness_contract(
        document.get("stage10_correctness")
    )
    require(
        stage10 == provenance["stage10_correctness"],
        "the public V8 manifest substituted its actual Stage 10 correctness proof",
    )
    records = document.get("case_records")
    descriptors = document.get("selected_cases")
    categories = document.get("categories")
    operations = document.get("public_operations")
    require(
        isinstance(records, list)
        and isinstance(descriptors, list)
        and len(records) == len(descriptors) == CASE_COUNT
        and isinstance(categories, dict)
        and len(categories) == CATEGORY_COUNT
        and all(value == CASES_PER_CATEGORY for value in categories.values())
        and isinstance(operations, dict)
        and set(operations) == PUBLIC_OPERATIONS
        and all(isinstance(value, int) and not isinstance(value, bool) and value > 0 for value in operations.values())
        and sum(operations.values()) == CASE_COUNT,
        "the V8 public manifest lost a case, operation, or balanced category",
    )
    seen: set[str] = set()
    semantic_identities: list[str] = []
    seen_semantic_identities: set[str] = set()
    counted_categories: collections.Counter[str] = collections.Counter()
    counted_operations: collections.Counter[str] = collections.Counter()
    generated = 0
    for index, (record, descriptor) in enumerate(zip(records, descriptors, strict=True)):
        require(isinstance(record, dict) and isinstance(descriptor, dict), "invalid V8 case")
        case = record.get("case")
        expected = record.get("expected")
        require(isinstance(case, dict) and isinstance(expected, dict), "missing public case answer")
        identifier = case.get("id")
        require(
            isinstance(identifier, str)
            and bool(identifier)
            and identifier not in seen
            and descriptor.get("case") == identifier
            and case.get("cohort") == expected.get("cohort") == COHORT
            and expected.get("id") == identifier
            and case.get("category") == expected.get("category") == descriptor.get("category")
            and case.get("api") in PUBLIC_OPERATIONS
            and descriptor.get("api") == case.get("api")
            and descriptor.get("lifecycle") == case.get("lifecycle")
            and isinstance(case.get("ops"), int)
            and not isinstance(case.get("ops"), bool)
            and case["ops"] > 0
            and expected.get("result_sha256") == value_digest(expected.get("result")),
            f"the frozen V8 case or reference answer changed at position {index}",
        )
        require(
            isinstance(record.get("generated"), bool)
            and record["generated"] is (index >= ORIGINAL_CASE_COUNT),
            "V8 did not retain the original 8,192 cases in their original order",
        )
        identity = semantic_identity(case)
        require(
            record.get("semantic_identity") == identity
            and identity not in seen_semantic_identities,
            "the frozen V8 matrix repeated or changed a type-sensitive case identity",
        )
        subject = unpack_public(case.get("string"))
        require(
            subject is None
            or (
                isinstance(subject, (str, bytes, bytearray, memoryview))
                and len(subject) <= SUBJECT_LIMIT
            ),
            "a frozen V8 public subject exceeds its declared bound",
        )
        result_count = (
            0 if expected["result"] is None
            else len(expected["result"])
            if isinstance(expected["result"], (list, tuple))
            else 1
        )
        require(result_count <= RESULT_LIMIT, "a frozen V8 result exceeds its declared bound")
        require(
            isinstance(record.get("source_case"), str) and bool(record["source_case"]),
            "a generated V8 case omitted its exact public source identity",
        )
        if record["generated"]:
            require(
                descriptor.get("input") == source_kind(case)
                and descriptor.get("source_case") == record["source_case"]
                and descriptor.get("expected_result_sha256") == expected["result_sha256"]
                and descriptor.get("frozen_operations") == case["ops"]
                and descriptor.get("result_count") == result_count
                and descriptor.get("result_density") == result_density(expected["result"]),
                "a generated V8 case changed its source, input, result, or bound",
            )
        seen.add(identifier)
        semantic_identities.append(identity)
        seen_semantic_identities.add(identity)
        counted_categories[case["category"]] += 1
        counted_operations[case["api"]] += 1
        generated += int(record["generated"])
    parent = read_pinned_json(
        PUBLIC_V6_MANIFEST_PATH,
        PUBLIC_V6_MANIFEST_SHA256,
        "exact original 8,192-case public V6 manifest",
    )
    require(
        parent.get("postfinal_schema") == "rebar-postfinal-public-practice-plan-v6"
        and parent.get("python") == "3.14.6"
        and parent.get("cohort") == COHORT
        and parent.get("cases") == ORIGINAL_CASE_COUNT
        and isinstance(parent.get("selected_cases"), list)
        and len(parent["selected_cases"]) == ORIGINAL_CASE_COUNT
        and descriptors[:ORIGINAL_CASE_COUNT] == parent["selected_cases"],
        "V8 did not preserve all original frozen V6 descriptors byte for byte",
    )
    require(
        generated == GENERATED_CASE_COUNT
        and dict(sorted(counted_categories.items())) == categories
        and dict(sorted(counted_operations.items())) == operations
        and len(semantic_identities) == len(seen_semantic_identities) == CASE_COUNT
        and document.get("semantic_identity_count") == CASE_COUNT
        and document.get("semantic_identity_sha256") == value_digest(semantic_identities),
        "the V8 generated population or published denominators changed",
    )
    return document


def load_immutable_guard() -> Any:
    require_candidate_free()
    require_pinned_file(GUARD_SOURCE_PATH, GUARD_SOURCE_SHA256, "immutable V1 worker")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    module = importlib.import_module("tools.postfinal_no_delegation_audit_v1")
    require(
        Path(getattr(module, "__file__", "")).resolve() == GUARD_SOURCE_PATH.resolve()
        and getattr(module, "SCHEMA", None) == GUARD_SCHEMA
        and file_sha256(Path(module.__file__).resolve()) == GUARD_SOURCE_SHA256
        and callable(getattr(module, "guarded_worker_command", None))
        and callable(getattr(module, "validate_guarded_worker_response", None)),
        "the independently audited immutable V1 worker was substituted",
    )
    require_candidate_free()
    return module


def qualification_program(source: str) -> str:
    """Extend only an isolated child copy of the exact immutable V1 guard."""

    require(isinstance(source, str) and bool(source), "missing immutable guard program")
    require(
        source.count(QUALIFICATION_DEFINITION_MARKER) == 1,
        "the immutable V1 guarded observation definition was substituted",
    )
    require(
        source.count(QUALIFICATION_DISPATCH_MARKER) == 1,
        "the immutable V1 guarded request dispatch was substituted",
    )
    extended = source.replace(
        QUALIFICATION_DEFINITION_MARKER,
        "\n" + QUALIFICATION_FUNCTION_SOURCE + QUALIFICATION_DEFINITION_MARKER,
        1,
    )
    extended = extended.replace(
        QUALIFICATION_DISPATCH_MARKER,
        '            elif operation == "qualify":\n'
        '                result = qualify_public_v8_case(candidate, request)\n'
        + QUALIFICATION_DISPATCH_MARKER,
        1,
    )
    require(
        extended.count("def qualify_public_v8_case(candidate, request):") == 1
        and extended.count('elif operation == "qualify":') == 1,
        "the V8-only correctness extension lost its unique child-only dispatch",
    )
    return extended


def run_qualification_worker(args: argparse.Namespace) -> None:
    """Run the unchanged V1 poison guards plus one untimed V8-only operation."""

    require_pinned_python()
    require_candidate_free()
    require(
        args.family in ("rust", "vm", "zig"),
        "the isolated public V8 correctness family is invalid",
    )
    require(
        valid_sha256(args.runner_sha256)
        and file_sha256(SOURCE_PATH) == args.runner_sha256,
        "the isolated V8 correctness worker source was substituted",
    )
    try:
        native = json.loads(args.native_fingerprints)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise PublicPracticeError("invalid qualified V8 native fingerprints") from error
    require(
        isinstance(native, dict)
        and native == {role: digest for role, (_path, digest) in EXPECTED_NATIVE_FILES.items()},
        "the isolated V8 correctness worker substituted its exact V5 native engines",
    )
    audit = load_immutable_guard()
    inherited = audit.guarded_worker_command(args.family, native, persistent=True)
    require(
        isinstance(inherited, list)
        and len(inherited) == 10
        and Path(inherited[0]).resolve() == PINNED_PYTHON.resolve()
        and inherited[1:4] == ["-I", "-B", "-c"]
        and isinstance(inherited[4], str)
        and inherited[4] == getattr(audit, "GUARDED_WORKER_SOURCE", None)
        and inherited[5] == str(ROOT)
        and inherited[6] == args.family
        and inherited[9] == "persistent",
        "the exact source-bound immutable V1 qualification guard was substituted",
    )
    extended = qualification_program(inherited[4])
    # Execute a private child-only copy.  No V1 module attribute, source byte,
    # old public runner, benchmark state, or candidate controller is changed.
    sys.argv = [str(SOURCE_PATH), *inherited[5:]]
    exec(compile(extended, "<source-bound-v8-correctness-guard>", "exec"), {
        "__name__": "__v8_public_correctness_guard__",
    })


class GuardedWorkerBase:
    """Bounded persistent protocol shared by separately owned V8 workers."""

    def __init__(self, audit: Any, module: str, native: dict[str, str]) -> None:
        require(module in FAMILIES, "an unknown candidate entered the V8 worker")
        self.audit = audit
        self.module = module
        self.family = FAMILIES[module]
        self.native = native
        command = self.worker_command()
        require(
            isinstance(command, list)
            and len(command) >= 4
            and all(isinstance(item, str) for item in command)
            and Path(command[0]).resolve() == PINNED_PYTHON.resolve()
            and "-I" in command
            and "-B" in command,
            f"{module} does not have an isolated, pinned, guarded worker",
        )
        self.process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        require(self.process.stdin is not None and self.process.stdout is not None, "invalid worker pipes")
        try:
            self.verify(force_hash=True)
        except (OSError, RuntimeError, ValueError):
            self.close()
            raise

    def worker_command(self) -> list[str]:
        raise NotImplementedError("a guarded V8 worker must provide its exact role")

    def request(self, document: dict[str, Any]) -> dict[str, Any]:
        require(self.process.poll() is None, f"the isolated {self.module} worker stopped")
        require(self.process.stdin is not None and self.process.stdout is not None, "lost worker pipes")
        try:
            self.process.stdin.write(json_bytes(document).decode("ascii") + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError, TypeError, ValueError) as error:
            raise PublicPracticeError(f"the isolated {self.module} worker rejected its request") from error
        for response_index in range(2):
            encoded = self.process.stdout.readline(MAX_RESPONSE_BYTES + 1)
            require(
                bool(encoded)
                and len(encoded) <= MAX_RESPONSE_BYTES
                and encoded.endswith("\n"),
                f"the isolated {self.module} worker exceeded its response bound",
            )
            try:
                response = json.loads(encoded)
            except (UnicodeError, json.JSONDecodeError) as error:
                raise PublicPracticeError(f"the isolated {self.module} returned invalid JSON") from error
            require(isinstance(response, dict), "the guarded worker returned a non-object")
            if (
                response_index == 0
                and response.get("op") in {"ready", "startup"}
                and document.get("op") not in {"ready", "startup"}
            ):
                require(response.get("passed") is True, "the guarded worker failed startup")
                continue
            require(
                response.get("passed") is True and response.get("op") == document.get("op"),
                f"the isolated {self.module} worker rejected {document.get('op')!r}",
            )
            return response
        raise PublicPracticeError(f"the isolated {self.module} worker omitted a response")

    def verify(self, *, force_hash: bool = False) -> dict[str, Any]:
        response = self.request({"op": "verify", "force_hash": force_hash})
        validated = self.audit.validate_guarded_worker_response(self.family, response, self.native)
        require(isinstance(validated, dict), "the immutable guard rejected a mapped native engine")
        mapping = validated.get("native_mapping_provenance")
        require(
            isinstance(mapping, dict)
            and mapping.get("force_hash") is force_hash
            and mapping.get("digest_cache_key") == "device,inode,size,mtime_ns,ctime_ns",
            "the worker weakened its source-bound native fingerprint policy",
        )
        if force_hash:
            records = mapping.get("observed_owned_mappings")
            require(
                isinstance(records, list)
                and all(
                    isinstance(record, dict)
                    and record.get("content_sha256_recomputed") is True
                    for record in records
                ),
                "the worker omitted a forced native content hash",
            )
        return validated

    def prepare(self, case: dict[str, Any], expected: dict[str, Any]) -> None:
        executable = executable_public_case(case)
        response = self.request({
            "op": "prepare",
            "case": pack_public(executable),
            "expected": pack_public(expected),
        })
        validated = self.audit.validate_guarded_worker_response(self.family, response, self.native)
        require(
            isinstance(validated, dict)
            and response.get("case") == case["id"]
            and response.get("module") == self.module
            and response.get("expected_sha256") == expected["result_sha256"],
            f"the isolated {self.module} worker substituted a frozen public case",
        )

    def observe(
        self,
        case: dict[str, Any],
        expected: dict[str, Any],
        trial: int,
        operations: int,
    ) -> dict[str, Any]:
        response = self.request({
            "op": "observe",
            "case": case["id"],
            "trial": trial,
            "operations": operations,
            "warmups": WARMUPS,
        })
        require(
            response.get("case") == case["id"]
            and response.get("module") == self.module
            and response.get("trial") == trial
            and response.get("operations") == operations
            and response.get("warmups") == WARMUPS
            and response.get("correctness_checks") == 3
            and response.get("expected_sha256") == expected["result_sha256"],
            f"the isolated {self.module} worker omitted a before/inside/after correctness gate",
        )
        elapsed = response.get("elapsed_ns")
        require(
            isinstance(elapsed, int)
            and not isinstance(elapsed, bool)
            and elapsed > 0
            and response.get("ns_per_op") == elapsed / operations
            and process_memory_valid(response),
            f"the isolated {self.module} produced invalid elapsed or process-memory data",
        )
        return response

    def close(self) -> None:
        if self.process.poll() is None:
            try:
                self.request({"op": "quit"})
            except (OSError, RuntimeError):
                self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=10)
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            if stream is not None:
                stream.close()


class PersistentGuardedWorker(GuardedWorkerBase):
    """The unchanged V1 timing guard, source-qualified without V7 imports."""

    def worker_command(self) -> list[str]:
        return self.audit.guarded_worker_command(
            self.family,
            self.native,
            persistent=True,
        )


class QualificationGuardedWorker(GuardedWorkerBase):
    """A V8-only untimed worker with all original V1 isolation protections."""

    def worker_command(self) -> list[str]:
        require(self.family in ("rust", "vm", "zig"), "baseline cannot qualify a candidate")
        return [
            str(PINNED_PYTHON),
            "-I",
            "-B",
            str(SOURCE_PATH),
            "--qualify-worker",
            "--family",
            self.family,
            "--native-fingerprints",
            json_bytes(self.native).decode("ascii"),
            "--runner-sha256",
            file_sha256(SOURCE_PATH),
        ]

    def observe(
        self,
        case: dict[str, Any],
        expected: dict[str, Any],
        trial: int,
        operations: int,
    ) -> dict[str, Any]:
        raise PublicPracticeError("the V8 prequalification worker cannot measure time")

    def qualify(self, case: dict[str, Any], expected: dict[str, Any]) -> None:
        response = self.request({"op": "qualify", "case": case["id"]})
        validated = self.audit.validate_guarded_worker_response(
            self.family,
            response,
            self.native,
        )
        require(
            isinstance(validated, dict)
            and response.get("family") == self.family
            and response.get("module") == self.module
            and response.get("case") == case["id"]
            and response.get("actual_snapshot_checked") is True
            and response.get("actual_result_sha256") == expected["result_sha256"]
            and response.get("independent_correctness_gate_sha256")
            == expected["result_sha256"]
            and response.get("timing_performed") is False
            and response.get("clock_accessed") is False,
            f"the V8 {self.module} did not independently reproduce its CPython answer",
        )


def prequalify_all_candidates(
    records: list[dict[str, Any]],
    audit: Any,
    native: dict[str, str],
) -> dict[str, Any]:
    """Pass every candidate answer before creating any timed engine worker."""

    require_candidate_free()
    require(len(records) == CASE_COUNT, "incomplete global public V8 case population")
    workers: dict[str, QualificationGuardedWorker] = {}
    checks = 0
    runtime_checks = 0
    try:
        for module in MODULES[1:]:
            workers[module] = QualificationGuardedWorker(audit, module, native)
            runtime_checks += 1
        for position, record in enumerate(records, 1):
            case = record["case"]
            expected = record["expected"]
            for module in MODULES[1:]:
                worker = workers[module]
                worker.prepare(case, expected)
                runtime_checks += 1
                worker.qualify(case, expected)
                checks += 1
            require_candidate_free()
            if position % 128 == 0 or position == CASE_COUNT:
                print(json.dumps({
                    "schema": REPORT_SCHEMA + "-prequalification",
                    "protocol_version": VERSION,
                    "cohort": COHORT,
                    "holdout_accessed": False,
                    "timing_performed": False,
                    "cases_completed": position,
                    "cases": CASE_COUNT,
                    "candidate_answers_verified": checks,
                }, sort_keys=True), flush=True)
        for module in MODULES[1:]:
            workers[module].verify(force_hash=True)
            runtime_checks += 1
    finally:
        for worker in workers.values():
            worker.close()
    require(
        checks == EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "at least one real candidate was not qualified against every V8 CPython answer",
    )
    require(
        runtime_checks == EXPECTED_GLOBAL_PREQUALIFICATIONS + 2 * (len(MODULES) - 1),
        "the independently mapped global qualification guards were omitted",
    )
    require_candidate_free()
    return {
        "status": "PASS",
        "candidate_families": list(MODULES[1:]),
        "candidate_cases": checks,
        "checks_per_candidate": CASE_COUNT,
        "native_runtime_checks": runtime_checks,
        "actual_snapshots_verified": checks,
        "independent_correctness_gates": checks,
        "all_candidates_passed_before_timing": True,
        "timed_workers_constructed": 0,
        "clock_accessed": False,
        "timing_performed": False,
        "failed": 0,
    }


def require_pushed_freeze() -> None:
    """Only a clean, committed, pushed main-branch V8 plan can authorize time."""

    require_candidate_free()

    def git(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    required = (SOURCE_PATH, GENERATOR_SOURCE_PATH, PROTOCOL_PATH, MANIFEST_PATH, GOAL_PATH)
    owned: list[str] = []
    for path in required:
        require(path.is_file() and not path.is_symlink(), "the committed V8 frozen plan is missing")
        owned.append(str(path.relative_to(ROOT)))
    tracked = git("ls-files", "--error-unmatch", "--", *owned)
    require(tracked.returncode == 0, "the V8 source, protocol and plan must be committed")
    clean = git("status", "--porcelain", "--", *owned)
    require(clean.returncode == 0 and not clean.stdout.strip(), "the committed frozen V8 plan changed")
    branch = git("symbolic-ref", "--quiet", "--short", "HEAD")
    require(branch.returncode == 0 and branch.stdout.strip() == "main", "V8 timing requires main")
    pushed = git("merge-base", "--is-ancestor", "HEAD", "origin/main")
    require(pushed.returncode == 0, "the exact V8 source, protocol and plan must first be pushed")
    require_candidate_free()


def make_case_result(
    case: Mapping[str, Any],
    expected: Mapping[str, Any],
    candidate: str,
    observations: Mapping[str, list[Mapping[str, Any]]],
) -> tuple[dict[str, Any], float]:
    baseline = observations.get(MODULES[0])
    measured = observations.get(candidate)
    require(
        isinstance(baseline, list)
        and isinstance(measured, list)
        and len(baseline) == len(measured) == TRIALS,
        "a public V8 paired trial or unchanged standard-Python baseline was omitted",
    )
    ratios: list[float] = []
    for trial, (reference, sample) in enumerate(zip(baseline, measured, strict=True)):
        require(
            reference.get("trial") == sample.get("trial") == trial,
            "the public V8 baseline and candidate trial were not genuinely paired",
        )
        reference_ns = reference.get("ns_per_op")
        candidate_ns = sample.get("ns_per_op")
        require(
            isinstance(reference_ns, (int, float))
            and isinstance(candidate_ns, (int, float))
            and not isinstance(reference_ns, bool)
            and not isinstance(candidate_ns, bool)
            and math.isfinite(reference_ns)
            and math.isfinite(candidate_ns)
            and reference_ns > 0
            and candidate_ns > 0,
            "a public V8 paired observation has an invalid time",
        )
        ratios.append(math.log(reference_ns / candidate_ns))
    speedup, low, high = paired_interval(ratios, str(case["id"]), candidate)
    reference_ns = math.exp(math.fsum(math.log(row["ns_per_op"]) for row in baseline) / TRIALS)
    candidate_ns = math.exp(math.fsum(math.log(row["ns_per_op"]) for row in measured) / TRIALS)
    baseline_memory = max(int(row["peak_traced_bytes"]) for row in baseline)
    candidate_memory = max(int(row["peak_traced_bytes"]) for row in measured)
    ratio = candidate_memory / baseline_memory if baseline_memory else None
    result = {
        "case": case["id"],
        "cohort": COHORT,
        "category": case["category"],
        "api": case["api"],
        "lifecycle": case["lifecycle"],
        "input": source_kind(case),
        "result_density": result_density(expected.get("result")),
        "candidate": candidate,
        "weight": 1,
        "speedup": speedup,
        "ci95_low": low,
        "ci95_high": high,
        "baseline_ns": reference_ns,
        "candidate_ns": candidate_ns,
        "peak_traced_ratio": ratio,
        "statistically_faster": low > 1.0,
        "regression_gt_20pct": candidate_ns > reference_ns * 1.2,
    }
    return result, math.fsum(ratios) / TRIALS


def make_rankings(
    results: list[dict[str, Any]],
    candidate_logs: Mapping[str, list[float]],
) -> list[dict[str, Any]]:
    rankings: list[dict[str, Any]] = []
    for candidate in MODULES[1:]:
        rows = [row for row in results if row["candidate"] == candidate]
        values = candidate_logs.get(candidate)
        require(
            len(rows) == CASE_COUNT and isinstance(values, list) and len(values) == CASE_COUNT,
            f"public V8 omitted a whole-population result for {candidate}",
        )
        speedup, low, high = paired_interval(values, COHORT, candidate)
        rankings.append({
            "cohort": COHORT,
            "candidate": candidate,
            "cases": CASE_COUNT,
            "weight": CASE_COUNT,
            "geomean_speedup": speedup,
            "ci95_low": low,
            "ci95_high": high,
            "statistically_faster_cases": sum(bool(row["statistically_faster"]) for row in rows),
            "regressions_gt_20pct": sum(bool(row["regression_gt_20pct"]) for row in rows),
        })
    require(len(rankings) == len(MODULES) - 1, "a complete public candidate ranking was omitted")
    return rankings


def validate_prequalification(document: Any) -> dict[str, Any]:
    """Do not confuse constructing an operation with checking its result."""

    require(isinstance(document, dict), "the complete global candidate proof is missing")
    expected: dict[str, Any] = {
        "status": "PASS",
        "candidate_families": list(MODULES[1:]),
        "candidate_cases": EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "checks_per_candidate": CASE_COUNT,
        "native_runtime_checks": EXPECTED_GLOBAL_PREQUALIFICATIONS + 6,
        "actual_snapshots_verified": EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "independent_correctness_gates": EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "all_candidates_passed_before_timing": True,
        "timed_workers_constructed": 0,
        "clock_accessed": False,
        "timing_performed": False,
        "failed": 0,
    }
    for field, value in expected.items():
        observed = document.get(field)
        require(
            type(observed) is type(value) and observed == value,
            f"the genuine complete pre-timing V8 candidate proof changed: {field}",
        )
    return document


def read_bounded_json(path: Path, *, limit: int, label: str) -> dict[str, Any]:
    require(
        isinstance(limit, int) and not isinstance(limit, bool) and limit > 0,
        "invalid bounded public evidence size",
    )
    require(path.is_file() and not path.is_symlink(), f"missing exact public V8 {label}")
    try:
        size = path.stat().st_size
        require(0 < size <= limit, f"the exact public V8 {label} exceeds its bound")
        with path.open("rb") as stream:
            encoded = stream.read(limit + 1)
    except OSError as error:
        raise PublicPracticeError(f"cannot read exact public V8 {label}") from error
    require(len(encoded) == size and len(encoded) <= limit, f"public V8 {label} changed during read")
    try:
        document = json.loads(encoded)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise PublicPracticeError(f"invalid exact public V8 {label}") from error
    require(isinstance(document, dict), f"the exact public V8 {label} is not an object")
    require(encoded == json_bytes(document) + b"\n", f"the V8 {label} is not canonical JSON")
    return document


def freeze(_args: argparse.Namespace) -> dict[str, Any]:
    """Only call the exact independently source-pinned public V8 generator."""

    provenance = verified_provenance()
    require(
        not MANIFEST_PATH.exists() and not MANIFEST_PATH.is_symlink(),
        "refusing to overwrite the one-time expanded public V8 manifest",
    )
    require(
        all(not path.exists() and not path.is_symlink() for path in (RAW_PATH, SUMMARY_PATH, INTEGRITY_PATH)),
        "a prospective V8 freeze cannot follow V8 performance observations",
    )
    generator = importlib.import_module("tools.postfinal_public_expansion_v8")
    require(
        Path(getattr(generator, "__file__", "")).resolve() == GENERATOR_SOURCE_PATH.resolve()
        and file_sha256(Path(generator.__file__).resolve()) == GENERATOR_SOURCE_SHA256
        and getattr(generator, "SCHEMA", None) == PLAN_SCHEMA
        and callable(getattr(generator, "freeze_public_development", None)),
        "the exact independently pinned V8 public generator was substituted",
    )
    require_candidate_free()
    generator.freeze_public_development()
    require_candidate_free()
    manifest = load_manifest(MANIFEST_PATH, provenance)
    return {
        "schema": PLAN_SCHEMA,
        "status": "PASS",
        "protocol_version": VERSION,
        "freeze_only": True,
        "cohort": COHORT,
        "cases": CASE_COUNT,
        "categories": CATEGORY_COUNT,
        "cases_per_category": CASES_PER_CATEGORY,
        "original_cases_preserved": ORIGINAL_CASE_COUNT,
        "generated_public_cases": GENERATED_CASE_COUNT,
        "selection_seed": SELECTION_SEED,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "expected_raw_rows": EXPECTED_RAW_ROWS,
        "expected_correctness_answers": EXPECTED_CORRECTNESS_ANSWERS,
        "expected_confidence_intervals": EXPECTED_CONFIDENCE_INTERVALS,
        "expected_process_native_checks": EXPECTED_PROCESS_NATIVE_CHECKS,
        "goal_sha256": GOAL_SHA256,
        "v7_source_sha256": V7_SOURCE_SHA256,
        "v7_protocol_sha256": V7_PROTOCOL_SHA256,
        "generator_source_sha256": GENERATOR_SOURCE_SHA256,
        "protocol_sha256": PROTOCOL_SHA256,
        "stage10_correctness": provenance["stage10_correctness"],
        "runner_sha256": provenance["runner_sha256"],
        "manifest_sha256": file_sha256(MANIFEST_PATH),
        "campaigns": provenance["campaigns"],
        "verified_family_proofs": provenance["verified_family_proofs"],
        "candidate_imported": False,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
        "public_operations": manifest["public_operations"],
        "failed": 0,
    }


def measure(args: argparse.Namespace) -> dict[str, Any]:
    """Measure all four families only after a clean pushed prospective freeze."""

    require(
        getattr(args, "exclusive_slot", None) == VERSION,
        "V8 measurement requires the explicit, exclusive public V8 slot",
    )
    provenance = verified_provenance()
    require_pushed_freeze()
    manifest = load_manifest(args.manifest, provenance)
    raw_path = exact_output(args.raw, RAW_PATH, "paired public V8 observations")
    summary_path = exact_output(args.output, SUMMARY_PATH, "paired public V8 summary")
    require(not raw_path.exists(), "refusing to overwrite V8 paired public observations")
    require(not summary_path.exists(), "refusing to overwrite V8 public results")
    require(args.cases == CASE_COUNT, "the frozen V8 case denominator changed")
    require(args.trials == TRIALS, "the frozen V8 paired trial denominator changed")
    require(args.bootstraps == BOOTSTRAPS, "the frozen V8 resample denominator changed")
    require(args.max_operations == MAX_OPERATIONS, "the frozen V8 operation bound changed")
    runtime_audit = load_immutable_guard()
    require_candidate_free()

    # Never construct a timing worker, open an observations file, call a
    # clock, or measure an earlier case until every candidate has reproduced
    # every one of the 33,280 exact isolated CPython reference answers.
    qualification = prequalify_all_candidates(
        manifest["case_records"],
        runtime_audit,
        provenance["native_elf_fingerprints"],
    )
    validate_prequalification(qualification)
    require(
        verified_provenance() == provenance,
        "an audited candidate source changed during global V8 prequalification",
    )
    require(
        load_manifest(args.manifest, provenance) == manifest,
        "the frozen V8 public case matrix changed during global prequalification",
    )

    workers: dict[str, PersistentGuardedWorker] = {}
    results: list[dict[str, Any]] = []
    candidate_logs: dict[str, list[float]] = {name: [] for name in MODULES[1:]}
    raw_digest = hashlib.sha256()
    raw_rows = 0
    correctness = 0
    native_checks = 0
    try:
        for module in MODULES:
            workers[module] = PersistentGuardedWorker(
                runtime_audit,
                module,
                provenance["native_elf_fingerprints"],
            )
            native_checks += 1

        raw_path.parent.mkdir(parents=True, exist_ok=True)
        with raw_path.open("xb") as destination:
            with gzip.GzipFile(
                filename="", fileobj=destination, mode="wb", compresslevel=9, mtime=0
            ) as compressed:
                for index, record in enumerate(manifest["case_records"], 1):
                    case = record["case"]
                    expected = record["expected"]
                    per_case: dict[str, list[Mapping[str, Any]]] = {
                        name: [] for name in MODULES
                    }
                    for module in MODULES:
                        workers[module].prepare(case, expected)
                        native_checks += 1
                    operations = min(case["ops"], MAX_OPERATIONS)
                    for trial in range(TRIALS):
                        for order, module in enumerate(paired_order(case["id"], trial)):
                            response = workers[module].observe(case, expected, trial, operations)
                            per_case[module].append(response)
                            correctness += 3
                            row = {
                                "schema": ROW_SCHEMA,
                                "measurement": "public development; not a held-out or final result",
                                "case": case["id"],
                                "cohort": COHORT,
                                "category": case["category"],
                                "api": case["api"],
                                "lifecycle": case["lifecycle"],
                                "input": source_kind(case),
                                "result_density": result_density(expected["result"]),
                                "selection_reasons": list(
                                    manifest["selected_cases"][index - 1].get("selection_reasons", [])
                                ),
                                "module": module,
                                "trial": trial,
                                "order": order,
                                "operations": operations,
                                "frozen_operations": case["ops"],
                                "elapsed_ns": response["elapsed_ns"],
                                "ns_per_op": response["ns_per_op"],
                                "peak_traced_bytes": response["peak_traced_bytes"],
                                "rss_before_kb": response["rss_before_kb"],
                                "rss_after_kb": response["rss_after_kb"],
                                "hwm_kb": response["hwm_kb"],
                                "expected_sha256": response["expected_sha256"],
                            }
                            encoded = json_bytes(row) + b"\n"
                            raw_digest.update(encoded)
                            compressed.write(encoded)
                            raw_rows += 1
                    for module in MODULES:
                        workers[module].verify()
                        native_checks += 1
                    for candidate in MODULES[1:]:
                        result, mean_log = make_case_result(
                            case, expected, candidate, per_case
                        )
                        results.append(result)
                        candidate_logs[candidate].append(mean_log)
                    require_candidate_free()
                    if index % 32 == 0 or index == CASE_COUNT:
                        print(json.dumps({
                            "schema": REPORT_SCHEMA + "-progress",
                            "protocol_version": VERSION,
                            "cohort": COHORT,
                            "holdout_accessed": False,
                            "completed": index,
                            "cases": CASE_COUNT,
                        }, sort_keys=True), flush=True)
        for module in MODULES:
            workers[module].verify(force_hash=True)
            native_checks += 1
    finally:
        for worker in workers.values():
            worker.close()

    require(raw_rows == EXPECTED_RAW_ROWS, "a public V8 paired observation was omitted")
    require(correctness == EXPECTED_CORRECTNESS_ANSWERS, "a public V8 correctness answer was omitted")
    require(native_checks == EXPECTED_PROCESS_NATIVE_CHECKS, "a V8 process/native guard was omitted")
    require(len(results) == CASE_COUNT * (len(MODULES) - 1), "a candidate-case result was omitted")
    refreshed = verified_provenance()
    require(refreshed == provenance, "an independently qualified source changed during V8")
    rankings = make_rankings(results, candidate_logs)
    require(
        len(results) + len(rankings) == EXPECTED_CONFIDENCE_INTERVALS,
        "the prospective V8 confidence-interval denominator changed",
    )
    summary: dict[str, Any] = {
        "schema": REPORT_SCHEMA,
        "protocol_version": VERSION,
        "status": "PASS",
        "measurement": "public development; not a held-out or final result",
        "measurement_role": "PUBLIC DEVELOPMENT; not independently secret",
        "cohort": COHORT,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "exclusive_slot": VERSION,
        "manifest_path": str(MANIFEST_PATH.resolve()),
        "manifest_sha256": file_sha256(MANIFEST_PATH),
        "runner_sha256": provenance["runner_sha256"],
        "generator_source_sha256": GENERATOR_SOURCE_SHA256,
        "v7_source_sha256": V7_SOURCE_SHA256,
        "v7_protocol_sha256": V7_PROTOCOL_SHA256,
        "protocol_sha256": PROTOCOL_SHA256,
        "goal_sha256": GOAL_SHA256,
        "base_audit_sha256": BASE_AUDIT_SHA256,
        "strict_audit_sha256": STRICT_AUDIT_SHA256,
        "guard_source_sha256": GUARD_SOURCE_SHA256,
        "guard_report_sha256": GUARD_REPORT_SHA256,
        "locale_source_sha256": LOCALE_SOURCE_SHA256,
        "locale_report_sha256": LOCALE_REPORT_SHA256,
        "universal_source_sha256": UNIVERSAL_SOURCE_SHA256,
        "universal_report_sha256": UNIVERSAL_REPORT_SHA256,
        "stage10_correctness": provenance["stage10_correctness"],
        "campaigns": provenance["campaigns"],
        "verified_family_proofs": provenance["verified_family_proofs"],
        "qualified_source_fingerprints": provenance["qualified_source_fingerprints"],
        "native_elf_fingerprints": provenance["native_elf_fingerprints"],
        "candidate_binary_sha256_before": provenance["native_elf_fingerprints"],
        "candidate_binary_sha256_after": refreshed["native_elf_fingerprints"],
        "modules": list(MODULES),
        "cases": CASE_COUNT,
        "original_cases_preserved": ORIGINAL_CASE_COUNT,
        "generated_public_cases": GENERATED_CASE_COUNT,
        "all_bounded_workload_categories": CATEGORY_COUNT,
        "cases_per_category": CASES_PER_CATEGORY,
        "public_operations": manifest["public_operations"],
        "categories": manifest["categories"],
        "selection_seed": SELECTION_SEED,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "paired_trials": TRIALS,
        "warmups": WARMUPS,
        "maximum_operations_per_trial": MAX_OPERATIONS,
        "bootstrap_draws": BOOTSTRAPS,
        "persistent_isolated_worker_count": len(MODULES),
        "global_prequalification": qualification,
        "all_candidates_passed_before_timing": True,
        "candidate_cases_prequalified": EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "per_case_runtime_guard_checks": native_checks,
        "controller_candidate_imported": False,
        "raw_path": str(raw_path),
        "raw_sha256": raw_digest.hexdigest(),
        "compressed_raw_sha256": file_sha256(raw_path),
        "paired_raw_rows": raw_rows,
        "correctness_checks": correctness,
        "confidence_intervals": len(results) + len(rankings),
        "case_results": results,
        "rankings": rankings,
        "regressions": [row for row in results if row["regression_gt_20pct"]],
        "standalone_startup_cost": "NOT MEASURED",
        "standalone_ffi_cost": "NOT MEASURED",
        "inside_native_allocation": "NOT MEASURED",
        "failed": 0,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("xb") as stream:
        stream.write(json_bytes(summary) + b"\n")
    require_candidate_free()
    return {
        "schema": REPORT_SCHEMA,
        "status": "PASS",
        "protocol_version": VERSION,
        "measurement": "public development; not a held-out or final result",
        "cohort": COHORT,
        "holdout_accessed": False,
        "cases": CASE_COUNT,
        "modules": list(MODULES),
        "paired_trials": TRIALS,
        "bootstrap_draws": BOOTSTRAPS,
        "paired_raw_rows": raw_rows,
        "correctness_checks": correctness,
        "confidence_intervals": len(results) + len(rankings),
        "process_native_checks": native_checks,
        "persistent_isolated_worker_count": len(MODULES),
        "all_candidates_passed_before_timing": True,
        "candidate_cases_prequalified": EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "controller_candidate_imported": False,
        "strict_regressions": len(summary["regressions"]),
        "raw_sha256": summary["raw_sha256"],
        "compressed_raw_sha256": summary["compressed_raw_sha256"],
        "summary_sha256": file_sha256(summary_path),
        "failed": 0,
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    """Independently replay every canonical public row without any candidate."""

    provenance = verified_provenance()
    require_pushed_freeze()
    manifest = load_manifest(args.manifest, provenance)
    raw_path = exact_output(args.raw, RAW_PATH, "verified paired V8 observations")
    summary_path = exact_output(args.summary, SUMMARY_PATH, "verified public V8 summary")
    output_path = exact_output(args.output, INTEGRITY_PATH, "independent public V8 replay")
    require(
        not output_path.exists() and not output_path.is_symlink(),
        "refusing to overwrite an independent public V8 integrity result",
    )
    summary = read_bounded_json(
        summary_path,
        limit=512 * 1024 * 1024,
        label="paired observation summary",
    )
    expected_header: dict[str, Any] = {
        "schema": REPORT_SCHEMA,
        "protocol_version": VERSION,
        "status": "PASS",
        "measurement": "public development; not a held-out or final result",
        "measurement_role": "PUBLIC DEVELOPMENT; not independently secret",
        "cohort": COHORT,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "exclusive_slot": VERSION,
        "manifest_path": str(MANIFEST_PATH.resolve()),
        "manifest_sha256": file_sha256(MANIFEST_PATH),
        "runner_sha256": provenance["runner_sha256"],
        "generator_source_sha256": GENERATOR_SOURCE_SHA256,
        "v7_source_sha256": V7_SOURCE_SHA256,
        "v7_protocol_sha256": V7_PROTOCOL_SHA256,
        "protocol_sha256": PROTOCOL_SHA256,
        "goal_sha256": GOAL_SHA256,
        "base_audit_sha256": BASE_AUDIT_SHA256,
        "strict_audit_sha256": STRICT_AUDIT_SHA256,
        "guard_source_sha256": GUARD_SOURCE_SHA256,
        "guard_report_sha256": GUARD_REPORT_SHA256,
        "locale_source_sha256": LOCALE_SOURCE_SHA256,
        "locale_report_sha256": LOCALE_REPORT_SHA256,
        "universal_source_sha256": UNIVERSAL_SOURCE_SHA256,
        "universal_report_sha256": UNIVERSAL_REPORT_SHA256,
        "stage10_correctness": provenance["stage10_correctness"],
        "campaigns": provenance["campaigns"],
        "verified_family_proofs": provenance["verified_family_proofs"],
        "qualified_source_fingerprints": provenance["qualified_source_fingerprints"],
        "native_elf_fingerprints": provenance["native_elf_fingerprints"],
        "candidate_binary_sha256_before": provenance["native_elf_fingerprints"],
        "candidate_binary_sha256_after": provenance["native_elf_fingerprints"],
        "modules": list(MODULES),
        "cases": CASE_COUNT,
        "original_cases_preserved": ORIGINAL_CASE_COUNT,
        "generated_public_cases": GENERATED_CASE_COUNT,
        "all_bounded_workload_categories": CATEGORY_COUNT,
        "cases_per_category": CASES_PER_CATEGORY,
        "public_operations": manifest["public_operations"],
        "categories": manifest["categories"],
        "selection_seed": SELECTION_SEED,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "paired_trials": TRIALS,
        "warmups": WARMUPS,
        "maximum_operations_per_trial": MAX_OPERATIONS,
        "bootstrap_draws": BOOTSTRAPS,
        "persistent_isolated_worker_count": len(MODULES),
        "all_candidates_passed_before_timing": True,
        "candidate_cases_prequalified": EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "per_case_runtime_guard_checks": EXPECTED_PROCESS_NATIVE_CHECKS,
        "controller_candidate_imported": False,
        "raw_path": str(raw_path),
        "paired_raw_rows": EXPECTED_RAW_ROWS,
        "correctness_checks": EXPECTED_CORRECTNESS_ANSWERS,
        "confidence_intervals": EXPECTED_CONFIDENCE_INTERVALS,
        "standalone_startup_cost": "NOT MEASURED",
        "standalone_ffi_cost": "NOT MEASURED",
        "inside_native_allocation": "NOT MEASURED",
        "failed": 0,
    }
    for field, expected in expected_header.items():
        actual = summary.get(field)
        require(
            type(actual) is type(expected) and actual == expected,
            f"the independently replayed public V8 evidence changed: {field}",
        )
    qualification = validate_prequalification(summary.get("global_prequalification"))
    compressed_digest = file_sha256(raw_path)
    require(
        compressed_digest == summary.get("compressed_raw_sha256"),
        "the prospective compressed V8 observations were substituted",
    )

    observed_digest = hashlib.sha256()
    row_count = 0
    correctness = 0
    results: list[dict[str, Any]] = []
    candidate_logs: dict[str, list[float]] = {name: [] for name in MODULES[1:]}
    try:
        with gzip.open(raw_path, "rb") as stream:
            for position, record in enumerate(manifest["case_records"]):
                case = record["case"]
                expected = record["expected"]
                descriptor = manifest["selected_cases"][position]
                operations = min(case["ops"], MAX_OPERATIONS)
                per_case: dict[str, list[Mapping[str, Any]]] = {
                    module: [] for module in MODULES
                }
                for trial in range(TRIALS):
                    for order, module in enumerate(paired_order(case["id"], trial)):
                        encoded = stream.readline(MAX_RESPONSE_BYTES + 1)
                        require(
                            bool(encoded)
                            and len(encoded) <= MAX_RESPONSE_BYTES
                            and encoded.endswith(b"\n"),
                            "an independently replayed V8 raw row is truncated or oversized",
                        )
                        try:
                            row = json.loads(encoded)
                        except (UnicodeError, json.JSONDecodeError) as error:
                            raise PublicPracticeError(
                                "an independently replayed V8 raw row is invalid JSON"
                            ) from error
                        require(
                            isinstance(row, dict) and encoded == json_bytes(row) + b"\n",
                            "an independently replayed V8 raw row is not canonical",
                        )
                        expected_fields: dict[str, Any] = {
                            "schema": ROW_SCHEMA,
                            "measurement": "public development; not a held-out or final result",
                            "case": case["id"],
                            "cohort": COHORT,
                            "category": case["category"],
                            "api": case["api"],
                            "lifecycle": case["lifecycle"],
                            "input": source_kind(case),
                            "result_density": result_density(expected["result"]),
                            "selection_reasons": list(
                                descriptor.get("selection_reasons", [])
                            ),
                            "module": module,
                            "trial": trial,
                            "order": order,
                            "operations": operations,
                            "frozen_operations": case["ops"],
                            "expected_sha256": expected["result_sha256"],
                        }
                        for field, expected_value in expected_fields.items():
                            actual_value = row.get(field)
                            require(
                                type(actual_value) is type(expected_value)
                                and actual_value == expected_value,
                                "a public V8 paired row changed its case, family, "
                                f"order, frozen answer, or operation: {field}",
                            )
                        elapsed = row.get("elapsed_ns")
                        ns_per_op = row.get("ns_per_op")
                        require(
                            isinstance(elapsed, int)
                            and not isinstance(elapsed, bool)
                            and elapsed > 0
                            and isinstance(ns_per_op, (float, int))
                            and not isinstance(ns_per_op, bool)
                            and math.isfinite(ns_per_op)
                            and ns_per_op == elapsed / operations
                            and process_memory_valid(row),
                            "a replayed V8 trial changed its bounded time or process memory",
                        )
                        observed_digest.update(encoded)
                        per_case[module].append(row)
                        row_count += 1
                        correctness += 3
                for candidate in MODULES[1:]:
                    result, mean_log = make_case_result(
                        case,
                        expected,
                        candidate,
                        per_case,
                    )
                    results.append(result)
                    candidate_logs[candidate].append(mean_log)
            require(stream.read(1) == b"", "unplanned paired observations follow the V8 matrix")
    except (gzip.BadGzipFile, EOFError, OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PublicPracticeError("cannot independently replay bounded V8 observations") from error

    require(row_count == EXPECTED_RAW_ROWS, "independent replay lost a V8 raw observation")
    require(
        correctness == EXPECTED_CORRECTNESS_ANSWERS,
        "independent replay lost a before, inside, or after correctness gate",
    )
    require(
        observed_digest.hexdigest() == summary.get("raw_sha256"),
        "independent replay rejected the uncompressed canonical V8 observation hash",
    )
    require(
        len(results) == CASE_COUNT * (len(MODULES) - 1)
        and results == summary.get("case_results"),
        "independent V8 replay changed a per-case paired confidence interval",
    )
    rankings = make_rankings(results, candidate_logs)
    require(
        len(results) + len(rankings) == EXPECTED_CONFIDENCE_INTERVALS
        and rankings == summary.get("rankings"),
        "independent V8 replay rejected an overall 2,000-draw confidence interval",
    )
    regressions = [row for row in results if row["regression_gt_20pct"]]
    require(
        regressions == summary.get("regressions"),
        "independent V8 replay concealed or misreported a strict 20% regression",
    )
    refreshed = verified_provenance()
    require(
        refreshed == provenance,
        "a frozen source, native engine, audit, or Stage 10 proof changed during replay",
    )
    require_candidate_free()
    integrity: dict[str, Any] = {
        "schema": INTEGRITY_SCHEMA,
        "status": "PASS",
        "protocol_version": VERSION,
        "measurement": "independent public-development replay; not a held-out or final result",
        "cohort": COHORT,
        "holdout_accessed": False,
        "timing_performed": False,
        "candidate_imported": False,
        "controller_candidate_imported": False,
        "cases": CASE_COUNT,
        "cases_per_candidate": CASE_COUNT,
        "candidate_case_results": len(results),
        "modules": list(MODULES),
        "trials_per_module_case": TRIALS,
        "bootstrap_draws": BOOTSTRAPS,
        "raw_rows": row_count,
        "correctness_checks": correctness,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "process_native_checks": EXPECTED_PROCESS_NATIVE_CHECKS,
        "candidate_cases_prequalified": EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "global_prequalification": qualification,
        "all_candidates_passed_before_timing": True,
        "manifest_sha256": file_sha256(MANIFEST_PATH),
        "runner_sha256": provenance["runner_sha256"],
        "generator_source_sha256": GENERATOR_SOURCE_SHA256,
        "v7_source_sha256": V7_SOURCE_SHA256,
        "v7_protocol_sha256": V7_PROTOCOL_SHA256,
        "protocol_sha256": PROTOCOL_SHA256,
        "goal_sha256": GOAL_SHA256,
        "base_audit_sha256": BASE_AUDIT_SHA256,
        "strict_audit_sha256": STRICT_AUDIT_SHA256,
        "locale_source_sha256": LOCALE_SOURCE_SHA256,
        "locale_report_sha256": LOCALE_REPORT_SHA256,
        "universal_source_sha256": UNIVERSAL_SOURCE_SHA256,
        "universal_report_sha256": UNIVERSAL_REPORT_SHA256,
        "stage10_correctness": provenance["stage10_correctness"],
        "campaigns": provenance["campaigns"],
        "verified_family_proofs": provenance["verified_family_proofs"],
        "qualified_source_fingerprints": provenance["qualified_source_fingerprints"],
        "native_elf_fingerprints": provenance["native_elf_fingerprints"],
        "candidate_binary_sha256_before": provenance["native_elf_fingerprints"],
        "candidate_binary_sha256_after": provenance["native_elf_fingerprints"],
        "summary_sha256": file_sha256(summary_path),
        "compressed_raw_sha256": compressed_digest,
        "raw_sha256": observed_digest.hexdigest(),
        "rankings": rankings,
        "regressions": regressions,
        "standalone_startup_cost": "NOT MEASURED",
        "standalone_ffi_cost": "NOT MEASURED",
        "inside_native_allocation": "NOT MEASURED",
        "failed": 0,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("xb") as stream:
        stream.write(json_bytes(integrity) + b"\n")
    require_candidate_free()
    return {
        "schema": INTEGRITY_SCHEMA,
        "status": "PASS",
        "protocol_version": VERSION,
        "holdout_accessed": False,
        "timing_performed": False,
        "candidate_imported": False,
        "cases": CASE_COUNT,
        "candidate_case_results": len(results),
        "trials_per_module_case": TRIALS,
        "raw_rows": row_count,
        "correctness_checks": correctness,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "process_native_checks": EXPECTED_PROCESS_NATIVE_CHECKS,
        "candidate_cases_prequalified": EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "strict_regressions": len(regressions),
        "output": str(output_path),
        "sha256": file_sha256(output_path),
        "failed": 0,
    }


def self_test() -> dict[str, Any]:
    """Exercise only fixed synthetic values without files, workers, or clocks."""

    before = candidate_imports()
    checks: list[str] = []

    def check(name: str, condition: object) -> None:
        require(name not in checks, f"duplicate synthetic V8 control: {name}")
        require(condition, f"synthetic V8 public-practice control failed: {name}")
        checks.append(name)

    def rejects(name: str, action: Any) -> None:
        try:
            action()
        except (PublicPracticeError, ValueError, TypeError, OverflowError):
            check(name, True)
        else:
            raise PublicPracticeError(f"synthetic V8 poison was accepted: {name}")

    check("public-domain-is-v8", SEED_DOMAIN == "rebar/public-development/v8")
    check("selection-seed-is-frozen", SELECTION_SEED == 2_026_072_428)
    check("order-seed-is-separate", len({SELECTION_SEED, ORDER_SEED, BOOTSTRAP_SEED}) == 3)
    check("public-categories-are-exact", CATEGORY_COUNT == 260)
    check("public-cases-per-category-are-exact", CASES_PER_CATEGORY == 128)
    check("public-case-denominator-is-exact", CASE_COUNT == 33_280)
    check("original-cases-are-preserved", ORIGINAL_CASE_COUNT == 8_192)
    check("generated-case-count-is-exact", GENERATED_CASE_COUNT == 25_088)
    check("all-four-roles-are-isolated", MODULES == (
        "re", "candidates.rust_candidate", "candidates.vm_candidate", "candidates.zig_candidate"
    ))
    check("all-twelve-public-operations-are-frozen", len(PUBLIC_OPERATIONS) == 12)
    check("four-warmups-are-frozen", WARMUPS == 4)
    check("thirteen-paired-trials-are-frozen", TRIALS == 13)
    check("two-thousand-resamples-are-frozen", BOOTSTRAPS == 2_000)
    check("raw-row-denominator-is-exact", EXPECTED_RAW_ROWS == 1_730_560)
    check("correctness-answer-denominator-is-exact", EXPECTED_CORRECTNESS_ANSWERS == 5_191_680)
    check("confidence-interval-denominator-is-exact", EXPECTED_CONFIDENCE_INTERVALS == 99_843)
    check("process-and-native-denominator-is-exact", EXPECTED_PROCESS_NATIVE_CHECKS == 266_248)
    check(
        "global-candidate-prequalification-denominator-is-exact",
        EXPECTED_GLOBAL_PREQUALIFICATIONS == 99_840,
    )
    first = paired_order("synthetic-public-v8-case", 0)
    check("paired-order-is-repeatable", first == paired_order("synthetic-public-v8-case", 0))
    check("paired-order-retains-all-four-engines", set(first) == set(MODULES))
    rejects("negative-trial-rejected", lambda: paired_order("synthetic", -1))
    rejects("boolean-trial-rejected", lambda: paired_order("synthetic", True))
    rejects("out-of-range-trial-rejected", lambda: paired_order("synthetic", TRIALS))
    check("canonical-json-is-order-independent", json_bytes({"b": 2, "a": 1}) == json_bytes({"a": 1, "b": 2}))
    check("canonical-json-rejects-nan", _synthetic_nan_is_rejected())
    check("bytes-have-explicit-public-type", pack_public(b"ab") == {PACKING_MARKER: "bytes", "hex": "6162"})
    check("bytearray-does-not-become-bytes", pack_public(bytearray(b"ab")) == {PACKING_MARKER: "bytearray", "hex": "6162"})
    check("tuple-does-not-become-list", pack_public((1, 2)) == {PACKING_MARKER: "tuple", "items": [1, 2]})
    check("public-bytes-decode-without-type-loss", unpack_public(pack_public(b"ab")) == b"ab")
    check(
        "public-bytearray-decodes-without-type-loss",
        isinstance(unpack_public(pack_public(bytearray(b"ab"))), bytearray),
    )
    check(
        "public-memoryview-decodes-without-type-loss",
        isinstance(unpack_public(pack_public(memoryview(b"ab"))), memoryview),
    )
    rejects(
        "unknown-packed-public-type-is-rejected",
        lambda: unpack_public({PACKING_MARKER: "foreign", "hex": "6162"}),
    )
    check(
        "canonical-bytes-and-text-do-not-collide",
        canonical_public(b"ab") != canonical_public("ab"),
    )
    check(
        "canonical-boolean-and-integer-do-not-collide",
        canonical_public(True) != canonical_public(1),
    )
    check(
        "canonical-tuple-and-list-do-not-collide",
        canonical_public((1, 2)) != canonical_public([1, 2]),
    )
    check(
        "canonical-dictionary-order-is-stable",
        canonical_public({"a": 1, "b": 2}) == canonical_public({"b": 2, "a": 1}),
    )
    check(
        "canonical-lone-surrogates-are-preserved",
        canonical_public("\ud800") != canonical_public("\ufffd"),
    )
    rejects("unsupported-floating-identity-is-rejected", lambda: canonical_public(1.0))
    synthetic_case: dict[str, Any] = {
        "id": "synthetic-public-v8-case",
        "cohort": COHORT,
        "category": "synthetic-search",
        "api": "search",
        "pattern": "a",
        "flags": [],
        "string": "a",
        "lifecycle": "compiled",
        "ops": 1,
        "weight": 1,
    }
    check("text-input-uses-the-frozen-text-label", source_kind(synthetic_case) == "text")
    byte_case = {
        **synthetic_case,
        "pattern": pack_public(b"a"),
        "string": pack_public(b"a"),
    }
    check("binary-input-uses-the-frozen-bytes-label", source_kind(byte_case) == "bytes")
    check(
        "bytearray-input-uses-the-declared-public-label",
        source_kind({**byte_case, "subject_kind": "bytearray"}) == "bytearray",
    )
    check(
        "memoryview-input-uses-the-declared-public-label",
        source_kind({**byte_case, "subject_kind": "memoryview"}) == "memoryview",
    )
    bytearray_case = {**byte_case, "subject_kind": "bytearray"}
    bytearray_before = value_digest(bytearray_case)
    bytearray_executable = executable_public_case(bytearray_case)
    check(
        "shared-worker-materializes-real-bytearray-subjects",
        isinstance(unpack_public(bytearray_executable["string"]), bytearray),
    )
    check(
        "shared-worker-preserves-frozen-original-bytearray-case",
        value_digest(bytearray_case) == bytearray_before
        and bytearray_case["string"] == byte_case["string"]
        and bytearray_executable["id"] == bytearray_case["id"],
    )
    memoryview_case = {**byte_case, "subject_kind": "memoryview"}
    check(
        "shared-worker-materializes-real-memoryview-subjects",
        isinstance(
            unpack_public(executable_public_case(memoryview_case)["string"]),
            memoryview,
        ),
    )
    writable_bytes_case = {
        **byte_case,
        "string": pack_public(bytearray(b"a")),
        "subject_kind": "bytes",
    }
    check(
        "shared-worker-materializes-real-immutable-bytes",
        isinstance(
            unpack_public(executable_public_case(writable_bytes_case)["string"]),
            bytes,
        ),
    )
    compile_case = {**synthetic_case, "api": "compile", "string": None}
    check(
        "compile-pattern-is-never-rewritten-as-a-subject",
        executable_public_case(compile_case) is compile_case
        and compile_case["string"] is None,
    )
    rejects(
        "text-declaration-cannot-hide-a-binary-subject",
        lambda: executable_public_case({**byte_case, "subject_kind": "text"}),
    )
    check(
        "compile-classifies-its-pattern-not-a-missing-subject",
        source_kind({**synthetic_case, "api": "compile", "string": None}) == "text",
    )
    check(
        "semantic-public-identity-is-reproducible",
        semantic_identity(synthetic_case) == semantic_identity(dict(synthetic_case)),
    )
    check(
        "semantic-public-identity-retains-operation-arguments",
        semantic_identity(synthetic_case)
        != semantic_identity({**synthetic_case, "pos": 1}),
    )
    check(
        "semantic-public-identity-retains-source-value-types",
        semantic_identity(synthetic_case) != semantic_identity(byte_case),
    )
    check("empty-result-density-is-honest", result_density(None) == "none")
    check("multi-result-density-is-honest", result_density([1, 2]) == "few")
    check("linear-percentile-is-exact", percentile([4.0, 0.0], 0.25) == 1.0)
    rejects("empty-percentile-rejected", lambda: percentile([], 0.5))
    rejects("out-of-range-percentile-rejected", lambda: percentile([1.0], 1.1))
    ratios = [math.log(2.0)] * TRIALS
    speed, low, high = paired_interval(
        ratios, "synthetic-v8-case", "candidates.rust_candidate", draws=32
    )
    check("paired-geomean-is-correct", math.isclose(speed, 2.0))
    check("paired-resample-interval-is-correct", math.isclose(low, 2.0) and math.isclose(high, 2.0))
    check("paired-resampling-is-deterministic", (speed, low, high) == paired_interval(
        ratios, "synthetic-v8-case", "candidates.rust_candidate", draws=32
    ))
    rejects("empty-paired-bootstrap-rejected", lambda: paired_interval([], "synthetic", MODULES[1], draws=8))
    rejects("invalid-bootstrap-count-rejected", lambda: paired_interval(ratios, "synthetic", MODULES[1], draws=1))
    rejects("nonfinite-bootstrap-rejected", lambda: paired_interval([math.inf], "synthetic", MODULES[1], draws=8))
    check("twenty-percent-boundary-is-not-a-regression", not (120.0 > 100.0 * 1.2))
    check("strictly-more-than-twenty-percent-is-a-regression", 120.01 > 100.0 * 1.2)
    valid_memory = {
        "rss_before_kb": 10, "rss_after_kb": 12, "hwm_kb": 13,
        "peak_traced_bytes": 20,
    }
    check("real-process-memory-shape-is-preserved", process_memory_valid(valid_memory))
    check("negative-process-memory-is-rejected", not process_memory_valid({**valid_memory, "rss_before_kb": -1}))
    check("boolean-process-memory-is-rejected", not process_memory_valid({**valid_memory, "hwm_kb": True}))
    check("low-high-water-mark-is-rejected", not process_memory_valid({**valid_memory, "hwm_kb": 11}))
    check("synthetic-gzip-is-deterministic", _synthetic_gzip(b"public-v8\n") == _synthetic_gzip(b"public-v8\n"))
    check("all-three-complete-campaigns-are-required", set(CAMPAIGN_DIGESTS) == {"rust", "vm", "zig"})
    check("all-twenty-two-campaign-stages-are-required", len(CAMPAIGN_STAGES) == 22)
    check(
        "all-nine-edge-contract-and-observability-proofs-are-frozen",
        len(FROZEN_FAMILY_PROOFS) == 9
        and {
            role.partition("-")[0] for role in FROZEN_FAMILY_PROOFS
        } == {"rust", "vm", "zig"}
        and all(valid_sha256(item[1]) for item in FROZEN_FAMILY_PROOFS.values()),
    )
    check(
        "all-twelve-owned-candidate-sources-are-frozen",
        len(EXPECTED_SOURCE_FINGERPRINTS) == 12
        and all(valid_sha256(value) for value in EXPECTED_SOURCE_FINGERPRINTS.values()),
    )
    check(
        "all-five-owned-native-engine-files-are-frozen",
        len(EXPECTED_NATIVE_FILES) == 5
        and all(valid_sha256(value[1]) for value in EXPECTED_NATIVE_FILES.values()),
    )
    check(
        "stage10-v8-pins-the-final-passing-v7-source-and-protocol",
        V7_SOURCE_SHA256
        == "cc5b79daf3a0d018d15c76d01665cf94a30d3838c5a5c21389cba51444e96e7e"
        and V7_PROTOCOL_SHA256
        == "c8fed02bde3d2b096905a44db99405b47801743749053e8dc402cb70cc1f51c0",
    )
    check(
        "stage10-v8-pins-the-final-expanded-generator-and-protocol",
        GENERATOR_SOURCE_SHA256
        == "e921d5962746d564381a0a11d22eb125b080370b572ffd0f630e925025f1ec97"
        and PROTOCOL_SHA256
        == "e19d504f6d7504b4052f2bbfbc0a584596178919c5396e076d3e6261356a2095",
    )
    check("stage10-eight-cohort-matrix-is-required", len(STAGE10_COHORT_CASES) == 8)
    check(
        "stage10-matrix-denominator-is-exact",
        sum(STAGE10_COHORT_CASES.values()) == STAGE10_CASES == 3_584,
    )
    check(
        "stage10-dual-stdlib-denominator-is-exact",
        STAGE10_STDLIB_CHECKS == 2 * STAGE10_CASES,
    )
    check(
        "stage10-all-candidate-denominator-is-exact",
        STAGE10_CANDIDATE_CHECKS == 3 * STAGE10_CASES,
    )
    check(
        "stage10-preserves-the-original-v7-matrix-seed",
        STAGE10_SEED == 2_026_072_437
        and STAGE10_SEED_DOMAIN == "rebar/python-re/public-contract/v7",
    )
    check(
        "stage10-observation-domain-is-distinct",
        STAGE10_OBSERVATION_DOMAIN == "rebar/python-re/public-contract/v10"
        and STAGE10_OBSERVATION_DOMAIN != STAGE10_SEED_DOMAIN,
    )
    check(
        "stage10-matrix-digest-is-frozen",
        STAGE10_MATRIX_SHA256
        == "0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db",
    )
    check(
        "stage10-source-schema-cannot-be-substituted",
        STAGE10_SELF_ORACLE_SCHEMA
        == "rebar-python-re-public-contract-v10-self-oracle"
        and STAGE10_ALL_CANDIDATE_SCHEMA
        == "rebar-python-re-public-contract-v10-all-candidates"
        and STAGE10_METADATA_SCHEMA
        == "rebar-python-re-public-contract-v10-isolated-public-metadata",
    )
    check(
        "stage10-preserves-actual-reference-and-candidate-failures",
        valid_sha256(PRESERVED_STAGE07_FAILURE_SHA256)
        and valid_sha256(PRESERVED_STAGE08_SELF_ORACLE_SHA256)
        and valid_sha256(PRESERVED_STAGE08_RUST_FAILURE_SHA256)
        and len({
            PRESERVED_STAGE07_FAILURE_SHA256,
            PRESERVED_STAGE08_SELF_ORACLE_SHA256,
            PRESERVED_STAGE08_RUST_FAILURE_SHA256,
        }) == 3,
    )
    reference_events: list[str] = []
    portable_reference = {"portable_reference": "synthetic"}
    restored_reference = {"baseline_records": [{"value": "\ud800"}]}
    authenticated_reference = {"source_sha256": STAGE10_SOURCE_SHA256}

    class SyntheticStage10Codec:
        def _restore_portable(self, document: Any) -> dict[str, Any]:
            require(
                document is portable_reference,
                "a synthetic Stage 10 portable reference was substituted",
            )
            reference_events.append("restore")
            return restored_reference

    class SyntheticStage10Validator:
        def _validate_self_oracle(
            self,
            document: Any,
            provenance: Any,
        ) -> dict[str, Any]:
            require(
                document is restored_reference
                and provenance is authenticated_reference,
                "the synthetic Stage 10 validator lost restored provenance",
            )
            reference_events.append("validate")
            return document

    class SyntheticStage10Oracle:
        def __init__(self) -> None:
            self.previous: Any = SyntheticStage10Codec()
            self.stage07: Any = SyntheticStage10Validator()

        def _authenticate_current_provenance(self) -> dict[str, Any]:
            reference_events.append("authenticate")
            return authenticated_reference

    synthetic_oracle = SyntheticStage10Oracle()
    authenticated, reference = authenticate_stage10_reference(
        synthetic_oracle,
        portable_reference,
    )
    check(
        "stage10-authenticates-then-restores-before-two-argument-validation",
        reference_events == ["authenticate", "restore", "validate"]
        and authenticated is authenticated_reference
        and reference is restored_reference
        and reference["baseline_records"][0]["value"] == "\ud800",
    )
    missing_codec = SyntheticStage10Oracle()
    missing_codec.previous = object()
    rejects(
        "stage10-rejects-a-missing-reversible-reference-codec",
        lambda: authenticate_stage10_reference(
            missing_codec,
            portable_reference,
        ),
    )
    missing_validator = SyntheticStage10Oracle()
    missing_validator.stage07 = object()
    rejects(
        "stage10-rejects-a-missing-two-argument-reference-validator",
        lambda: authenticate_stage10_reference(
            missing_validator,
            portable_reference,
        ),
    )
    synthetic_history = stage10_preserved_history_contract()
    check(
        "stage10-validates-preserved-source-audit-locale-and-failure-history",
        validate_stage10_preserved_history(dict(synthetic_history))
        == synthetic_history,
    )
    for field, expected in synthetic_history.items():
        if isinstance(expected, bool):
            poisoned: Any = not expected
        elif isinstance(expected, int):
            poisoned = expected + 1
        elif field.endswith("sha256"):
            poisoned = "0" * 64
        else:
            poisoned = "substituted-stage10-provenance"
        rejects(
            "stage10-rejects-substituted-preserved-history-" + field,
            lambda name=field, value=poisoned: (
                validate_stage10_preserved_history({
                    **synthetic_history,
                    name: value,
                })
            ),
        )
    stage10_contract = stage10_correctness_contract()
    check(
        "stage10-manifest-proof-has-only-thirteen-agreed-fields",
        set(stage10_contract) == {
            "source_path",
            "source_sha256",
            "protocol_path",
            "protocol_sha256",
            "self_oracle_path",
            "self_oracle_sha256",
            "all_candidates_path",
            "all_candidates_sha256",
            "matrix_sha256",
            "cohorts",
            "cases",
            "stdlib_checks",
            "candidate_checks",
        },
    )
    check(
        "stage10-real-proof-pins-are-frozen",
        all(
            valid_sha256(value)
            for value in (
                STAGE10_SOURCE_SHA256,
                STAGE10_PROTOCOL_SHA256,
                STAGE10_SELF_ORACLE_SHA256,
                STAGE10_ALL_CANDIDATE_SHA256,
                STAGE10_MATRIX_SHA256,
            )
        ),
    )
    check(
        "stage10-exact-manifest-contract-is-validated",
        validate_stage10_correctness_contract(dict(stage10_contract))
        == stage10_contract,
    )
    for field in stage10_contract:
        omitted = dict(stage10_contract)
        omitted.pop(field)
        rejects(
            "stage10-rejects-omitted-manifest-proof-" + field,
            lambda document=omitted: validate_stage10_correctness_contract(
                document
            ),
        )
    rejects(
        "stage10-rejects-an-extra-manifest-proof-field",
        lambda: validate_stage10_correctness_contract({
            **stage10_contract,
            "stage07_correctness": "FAIL",
        }),
    )
    for field in (
        "source_sha256",
        "protocol_sha256",
        "self_oracle_sha256",
        "all_candidates_sha256",
        "matrix_sha256",
    ):
        rejects(
            "stage10-rejects-substituted-manifest-proof-" + field,
            lambda name=field: validate_stage10_correctness_contract({
                **stage10_contract,
                name: "0" * 64,
            }),
        )
    for family in ("rust", "vm", "zig"):
        expected_native = {
            path: digest
            for role, (path, digest) in EXPECTED_NATIVE_FILES.items()
            if role.startswith(f"candidates.{family}_candidate:")
        }
        native_module = {
            "rust": "candidates._rust_bridge",
            "vm": "candidates._vm_native",
            "zig": "candidates._zig_bridge",
        }[family]
        synthetic_receipt = {
            "enabled": True,
            "schema": STAGE10_METADATA_SCHEMA,
            "source_sha256": STAGE10_SOURCE_SHA256,
            "role": family,
            "surface_cases": 256,
            "record_sha256": value_digest({"synthetic_family": family}),
            "production_matching_executed": False,
            "metadata_and_matcher_processes_distinct": True,
            "matcher_inspect_loaded": False,
            "matcher_tokenizer_loaded": False,
        }
        synthetic_family_guard = {
            "enabled": True,
            "family": family,
            "stdlib_re_blocked": True,
            "cpython_sre_blocked": True,
            "third_party_regex_blocked": True,
            "cross_family_blocked": True,
            "foreign_dynamic_libraries_blocked": True,
            "native_loader_aliases_blocked": list(STAGE10_NATIVE_LOADER_ALIASES),
            "loaded_candidate_modules": sorted((
                f"candidates.{family}_candidate",
                native_module,
            )),
            "isolated_public_metadata": synthetic_receipt,
        }
        check(
            "stage10-validates-independent-native-metadata-" + family,
            validate_stage10_family_guard(
                family,
                synthetic_family_guard,
                expected_native,
            ) == synthetic_family_guard,
        )
        rejects(
            "stage10-rejects-missing-isolated-metadata-" + family,
            lambda role=family, guard=synthetic_family_guard,
            natives=expected_native: (
                validate_stage10_family_guard(
                    role,
                    {**guard, "isolated_public_metadata": None},
                    natives,
                )
            ),
        )
        rejects(
            "stage10-rejects-extra-isolated-metadata-" + family,
            lambda role=family, guard=synthetic_family_guard,
            receipt=synthetic_receipt, natives=expected_native: (
                validate_stage10_family_guard(
                    role,
                    {**guard, "isolated_public_metadata": {
                        **receipt,
                        "foreign_metadata": True,
                    }},
                    natives,
                )
            ),
        )
        rejects(
            "stage10-rejects-substituted-owned-native-family-" + family,
            lambda role=family, guard=synthetic_family_guard,
            natives=expected_native: (
                validate_stage10_family_guard(
                    role,
                    guard,
                    {path: "0" * 64 for path in natives},
                )
            ),
        )
        for field, poisoned in (
            ("enabled", False),
            ("schema", "rebar-python-re-public-contract-v7-isolated-metadata"),
            ("source_sha256", "0" * 64),
            ("role", "foreign"),
            ("surface_cases", 255),
            ("record_sha256", "not-a-digest"),
            ("production_matching_executed", True),
            ("metadata_and_matcher_processes_distinct", False),
            ("matcher_inspect_loaded", True),
            ("matcher_tokenizer_loaded", True),
        ):
            rejects(
                "stage10-rejects-" + family + "-metadata-" + field,
                lambda name=field, value=poisoned,
                role=family, guard=synthetic_family_guard,
                receipt=synthetic_receipt, natives=expected_native: (
                    validate_stage10_family_guard(
                        role,
                        {**guard, "isolated_public_metadata": {
                            **receipt,
                            name: value,
                        }},
                        natives,
                    )
                ),
            )
        for field, poisoned in (
            ("stdlib_re_blocked", False),
            ("cpython_sre_blocked", False),
            ("third_party_regex_blocked", False),
            ("cross_family_blocked", False),
            ("foreign_dynamic_libraries_blocked", False),
            ("native_loader_aliases_blocked", []),
            ("loaded_candidate_modules", [f"candidates.{family}_candidate"]),
        ):
            rejects(
                "stage10-rejects-" + family + "-native-guard-" + field,
                lambda name=field, value=poisoned,
                role=family, guard=synthetic_family_guard,
                natives=expected_native: (
                    validate_stage10_family_guard(
                        role,
                        {**guard, name: value},
                        natives,
                    )
                ),
            )
    synthetic_guard = (
        "# immutable synthetic guard\n"
        + QUALIFICATION_DEFINITION_MARKER
        + "    return None\n"
        + QUALIFICATION_DISPATCH_MARKER
        + "\n"
    )
    guarded = qualification_program(synthetic_guard)
    check(
        "v8-qualification-preserves-the-original-guard-dispatch",
        QUALIFICATION_DISPATCH_MARKER in guarded,
    )
    check(
        "v8-qualification-has-one-private-dispatch",
        guarded.count('elif operation == "qualify":') == 1,
    )
    check(
        "v8-qualification-does-not-mutate-its-immutable-source",
        synthetic_guard.count('elif operation == "qualify":') == 0,
    )
    check(
        "v8-qualification-poisons-every-public-clock",
        all(clock in QUALIFICATION_FUNCTION_SOURCE for clock in QUALIFICATION_CLOCK_NAMES),
    )
    check(
        "v8-qualification-checks-the-actual-candidate-snapshot",
        "pilot.snapshot(actual)" in QUALIFICATION_FUNCTION_SOURCE,
    )
    check(
        "v8-qualification-computes-the-actual-answer-digest",
        "pilot.digest(actual_snapshot)" in QUALIFICATION_FUNCTION_SOURCE,
    )
    rejects(
        "substituted-immutable-guard-definition-rejected",
        lambda: qualification_program("not a guarded worker"),
    )
    rejects(
        "duplicate-immutable-guard-dispatch-rejected",
        lambda: qualification_program(synthetic_guard + QUALIFICATION_DISPATCH_MARKER),
    )
    synthetic_prequalification = {
        "status": "PASS",
        "candidate_families": list(MODULES[1:]),
        "candidate_cases": EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "checks_per_candidate": CASE_COUNT,
        "native_runtime_checks": EXPECTED_GLOBAL_PREQUALIFICATIONS + 6,
        "actual_snapshots_verified": EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "independent_correctness_gates": EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "all_candidates_passed_before_timing": True,
        "timed_workers_constructed": 0,
        "clock_accessed": False,
        "timing_performed": False,
        "failed": 0,
    }
    check(
        "all-family-global-proof-shape-is-validated",
        validate_prequalification(synthetic_prequalification)
        == synthetic_prequalification,
    )
    rejects(
        "missing-candidate-prequalification-is-rejected",
        lambda: validate_prequalification({
            **synthetic_prequalification,
            "candidate_cases": EXPECTED_GLOBAL_PREQUALIFICATIONS - 1,
        }),
    )
    rejects(
        "unchecked-candidate-snapshot-is-rejected",
        lambda: validate_prequalification({
            **synthetic_prequalification,
            "actual_snapshots_verified": EXPECTED_GLOBAL_PREQUALIFICATIONS - 1,
        }),
    )
    rejects(
        "prequalification-clock-access-is-rejected",
        lambda: validate_prequalification({
            **synthetic_prequalification,
            "clock_accessed": True,
        }),
    )
    rejects(
        "premature-timing-worker-is-rejected",
        lambda: validate_prequalification({
            **synthetic_prequalification,
            "timed_workers_constructed": 1,
        }),
    )
    check("moving-source-cannot-authorize-freeze", not valid_sha256(None))
    check("no-candidate-was-imported", candidate_imports() == before == [])
    return {
        "schema": SELF_TEST_SCHEMA,
        "status": "PASS",
        "protocol_version": VERSION,
        "checks": len(checks),
        "check_names": checks,
        "cases": CASE_COUNT,
        "categories": CATEGORY_COUNT,
        "cases_per_category": CASES_PER_CATEGORY,
        "expected_raw_rows": EXPECTED_RAW_ROWS,
        "expected_correctness_answers": EXPECTED_CORRECTNESS_ANSWERS,
        "expected_confidence_intervals": EXPECTED_CONFIDENCE_INTERVALS,
        "expected_process_native_checks": EXPECTED_PROCESS_NATIVE_CHECKS,
        "expected_global_candidate_prequalifications": EXPECTED_GLOBAL_PREQUALIFICATIONS,
        "candidate_imports": [],
        "worker_processes_started": 0,
        "oracle_processes_started": 0,
        "public_case_files_opened": 0,
        "manifest_files_opened": 0,
        "files_written": 0,
        "historical_results_read": 0,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
        "failed": 0,
    }


def _synthetic_nan_is_rejected() -> bool:
    try:
        json_bytes({"not_a_number": math.nan})
    except ValueError:
        return True
    return False


def _synthetic_gzip(value: bytes) -> bytes:
    destination = io.BytesIO()
    with gzip.GzipFile(filename="", fileobj=destination, mode="wb", compresslevel=9, mtime=0) as stream:
        stream.write(value)
    return destination.getvalue()


def main(argv: list[str] | None = None) -> None:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == "--qualify-worker":
        hidden = argparse.ArgumentParser(add_help=False)
        hidden.add_argument("--family", choices=("rust", "vm", "zig"), required=True)
        hidden.add_argument("--native-fingerprints", required=True)
        hidden.add_argument("--runner-sha256", required=True)
        parsed_hidden = hidden.parse_args(arguments[1:])
        run_qualification_worker(parsed_hidden)
        return
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action")
    subparsers.add_parser("self-test", help="run only synthetic in-memory controls")
    subparsers.add_parser("freeze", help="prospectively freeze the exact public V8 plan")
    live = subparsers.add_parser("measure", help="measure only a clean, pushed V8 public plan")
    live.add_argument("--exclusive-slot", required=True)
    live.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    live.add_argument("--raw", type=Path, default=RAW_PATH)
    live.add_argument("--output", type=Path, default=SUMMARY_PATH)
    live.add_argument("--cases", type=int, default=CASE_COUNT)
    live.add_argument("--trials", type=int, default=TRIALS)
    live.add_argument("--bootstraps", type=int, default=BOOTSTRAPS)
    live.add_argument("--max-operations", type=int, default=MAX_OPERATIONS)
    replay = subparsers.add_parser(
        "verify",
        help="independently replay every public observation without a candidate",
    )
    replay.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    replay.add_argument("--raw", type=Path, default=RAW_PATH)
    replay.add_argument("--summary", type=Path, default=SUMMARY_PATH)
    replay.add_argument("--output", type=Path, default=INTEGRITY_PATH)
    if arguments and arguments[0] == "--self-test":
        arguments[0] = "self-test"
    elif arguments and arguments[0] == "--freeze":
        arguments[0] = "freeze"
    parsed = parser.parse_args(arguments)
    require(parsed.action is not None, "select --self-test, --freeze, or measure")
    try:
        if parsed.action == "self-test":
            result = self_test()
        elif parsed.action == "freeze":
            result = freeze(parsed)
        elif parsed.action == "verify":
            result = verify(parsed)
        else:
            result = measure(parsed)
    except (
        PublicPracticeError, OSError, subprocess.SubprocessError,
        KeyError, TypeError, ValueError, OverflowError, RecursionError,
        UnicodeError, json.JSONDecodeError,
    ) as error:
        print(json.dumps({
            "schema": REPORT_SCHEMA,
            "status": "FAIL",
            "protocol_version": VERSION,
            "holdout_accessed": False,
            "timing_performed": False,
            "performance": "NOT MEASURED",
            "error": str(error),
            "failed": 1,
        }, sort_keys=True))
        raise SystemExit(1) from error
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, allow_nan=False))


if __name__ == "__main__":
    main()
