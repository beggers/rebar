#!/usr/bin/env python3
"""Preserve every real Python-regex correctness result, including failures.

This worker is a separately versioned successor.  It never edits or runs an
older correctness gate.  A nonzero producer exit is evidence to authenticate,
not permission to drop a signed report.  The independently frozen nested V3
owner must be published before this draft can authorize a real candidate.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
from dataclasses import dataclass
import gc
import gzip
import hashlib
import importlib
import io
import json
import locale
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import types
from typing import Any, Callable, Iterator, Mapping, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_frozen_p0_candidate_worker_v4.py"
PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V6.md"
DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v6.json"
SCHEMA = "rebar-frozen-python-re-p0-candidate-worker-v4"
PROTOCOL_SCHEMA = "rebar-frozen-python-re-p0-candidate-protocol-v6"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
P0_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
P0_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
P0_VERIFIER_RELATIVE = "tools/verify_p0_completeness_v1.py"
P0_VERIFIER_SHA256 = "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c"
V1_RELATIVE = "tools/run_frozen_p0_candidate_v1.py"
V1_SHA256 = "c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8"
V1_PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V1.md"
V1_PROTOCOL_SHA256 = "e73c8a9a1b1edeb847d23c3d27d594d19bdfc514bee9e89790cd4d18fc9d3844"
V1_DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v1.json"
V1_DOCUMENT_SHA256 = "7ca70c9d4ae7491ae2b9b9a660c8c72efcee629708103ac7654f31353fa7cd0c"
V2_RELATIVE = "tools/run_frozen_p0_candidate_v2.py"
V2_SHA256 = "6789f54668ab1a6b8401135a429c3a3cc9cbcb7c820fdf1df02811cdf7975ced"
V3_RELATIVE = "tools/run_frozen_p0_candidate_v3.py"
V3_SHA256 = "478d7d6d119c0f1b248890b1d4e27ffe1714688684b439ecb14bd4a83ecee557"
V4_RELATIVE = "tools/run_frozen_p0_candidate_v4.py"
V4_SHA256 = "7bb6104423fbd6604decdb46b1c9b1cc0c0782094d04db467710b3b3b2cc208c"
V3_PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V3.md"
V3_PROTOCOL_SHA256 = "3587e71b91f15c7727749554d971c120ecf5dea2b3624298be19e5dd849adb84"
V3_DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v3.json"
V3_DOCUMENT_SHA256 = "ebdbc2b9e6ada77a25d6c95d83078fc2af9fde5dd0c2887c5aab09748a67c8bc"
V3_FAILURE_RELATIVE = "oracle/phase2/evidence/frozen-p0-candidate-v3-c-phase2-v3-failures.json.gz"
V3_FAILURE_SHA256 = "3f7718b09080d0aa9612dabc7f97e8f41ea35958c8bbfeb7febbbf678d06028d"
V3_FAILURE_RECEIPT_RELATIVE = "oracle/phase2/evidence/frozen-p0-candidate-v3-c-phase2-v3-failures-publication-receipt.json"
V3_FAILURE_RECEIPT_SHA256 = "02996c09c8662c75eadadeccef2ac77895d942a56e06aca323e880f951a330a1"
V4_PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V4.md"
V4_PROTOCOL_SHA256 = "1d7afe5658e8f0f7bb8576fbf1f191a9d8d2d82bde7c97d179b46e1760de2b1f"
V4_DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v4.json"
V4_DOCUMENT_SHA256 = "e874b253b7baf4ab8cb3f359a44c2d4eacb4251abc3e5703507dceac616690a8"
V4_FAILURE_RELATIVE = "oracle/phase2/evidence/frozen-p0-candidate-v4-c-phase2-v4-failures.json.gz"
V4_FAILURE_SHA256 = "08614ef777081edb2335bcdaed615104c1d8a957ce246261b05d275d8bc6f50c"
V4_FAILURE_RECEIPT_RELATIVE = "oracle/phase2/evidence/frozen-p0-candidate-v4-c-phase2-v4-failures-publication-receipt.json"
V4_FAILURE_RECEIPT_SHA256 = "4ba965cca31ae3644ba37b4d8bb52f093d27349dd2aa1b747b8d2918fd60e23b"
V5_RELATIVE = "tools/run_frozen_p0_candidate_v5.py"
V5_SHA256 = "5dfdd52069379f4410a9620f95914717e0a9d278fdfc9f1d7416f3aa36ec6326"
V5_WORKER_RELATIVE = "tools/run_frozen_p0_candidate_worker_v3.py"
V5_WORKER_SHA256 = "3364ee6d2168803751a2a8c06533828fe9762bb5ad323e8f798bc346a4a2f475"
V5_DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v5.json"
V5_DOCUMENT_SHA256 = "f0ae8a783a3091cb2f59fdb7f82cb012fe34eceffbead347ff3ee2e11ec1724b"
V5_PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V5.md"
V5_PROTOCOL_SHA256 = "a943eb9d8d9dbc8ca13562c274b9a96b340ddc531423d6669a00d2aeba65ead8"
ACTIVATION_RELATIVE = "tools/activate_verified_native_candidate_v2.py"
ACTIVATION_SHA256 = "e6e8a72feffcf670da9a3e4d2e8b642e933c1d81cfe5bf7d1636385f207d6218"
ACTIVATION_PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V2.md"
ACTIVATION_PROTOCOL_SHA256 = "a675b411873c01ae88ea50d4f95aab7231a29dde38a458a947437f07ed850529"
ACTIVATION_SCHEMA = "rebar-phase2-verified-native-candidate-activation-v2"
AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
AUDIT_SHA256 = "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
CORE_RELATIVE = "tools/independent_public_contract_v3.py"
CORE_SHA256 = "9a831571c81e542d7d43ae56aea271f8e6c69550173d97ae1c9f8213eef40bf3"
SURFACE_VALIDATOR_RELATIVE = "tools/python_re_public_surface_oracle_stage27.py"
SURFACE_VALIDATOR_SHA256 = "fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b"
SURFACE_V17_RELATIVE = "tools/python_re_public_surface_oracle_stage17.py"
SURFACE_V17_SHA256 = "cc36700fd5e43ed409472423a74b7da686804b09c92511d90bec863026c25bf8"
SURFACE_V17_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V17.md"
SURFACE_V17_PROTOCOL_SHA256 = "a703805d1cc711488f84bf4d5a4596de8ef194fd47a2116162ec6a490a3da0e5"
SURFACE_V18_RELATIVE = "tools/python_re_public_surface_oracle_stage18.py"
SURFACE_V18_SHA256 = "31419fb54be8292dd1b7ecf82e23506889fa6b03eb8e7d29e19de90287546862"
SURFACE_V18_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V18.md"
SURFACE_V18_PROTOCOL_SHA256 = "66c6f52ff50c57f4bd6c22cdb13a55a1bfe41982238c5e7742b069505e624abb"
LOCALE_HARNESS_RELATIVE = "tools/rust_original_cpython_suite_v1.py"
LOCALE_HARNESS_SHA256 = "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95"

# This corrected controller was independently reviewed before its source,
# machine protocol, and explanation were separately committed and pushed.
NESTED_V3_RELATIVE = "tools/run_owned_candidate_subinterpreters_v3.py"
NESTED_V3_DOCUMENT_RELATIVE = "oracle/phase2/candidate-subinterpreters-v3.json"
NESTED_V3_PROTOCOL_RELATIVE = "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V3.md"
NESTED_V3_SHA256 = "21febe241549963a2818af2a20782da81bdf952fb7be8affc4289d9ccc9ad5b4"
NESTED_V3_DOCUMENT_SHA256 = "17dac72e6a0ae75bf1f013656b9779a1e948e71439cf336499c1e680beb19284"
NESTED_V3_PROTOCOL_SHA256 = "97354130b4d1ab97ee2c684b43b72e29a0a68439c2a1ead5a4f45edc20e6c9b4"

NESTED_V1_RELATIVE = "tools/run_owned_candidate_subinterpreters_v1.py"
NESTED_V1_SHA256 = "45e9b47c7c635fc30ebdb2cb4830d2d1fe382a5a7e4b663fb1a8e0112779e1a7"
NESTED_V1_DOCUMENT_SHA256 = "7d282b559952df68b95b5ebd55634b99d922ffc27b7a640778822ec3eed6ebe2"
NESTED_V1_PROTOCOL_SHA256 = "1dee7ebb7a98ccfec65cdb58f95378836a6747c1c9532ca676599cce62367332"
NESTED_V2_RELATIVE = "tools/run_owned_candidate_subinterpreters_v2.py"
NESTED_V2_SHA256 = "7dd5b4a5cdfecbe6dd674632bb5cee456ee877291de88ffc76ba60472d81408a"
NESTED_V2_DOCUMENT_SHA256 = "f740da205f8431898f0a1089df5419f01612c2384def78c7d9831748ecca1b24"
NESTED_V2_PROTOCOL_SHA256 = "c7a501f4487dfbe547c2cf8f5844be5179da035e7ae5f5e89f803234f3bf32dc"

BUILD_VERSIONS: dict[str, dict[str, str]] = {
    "2": {
        "source": "tools/reproduce_phase2_native_builds_v2.py",
        "source_sha256": "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796",
        "protocol": "oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md",
        "protocol_sha256": "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603",
        "schema": "rebar-phase2-independent-native-source-build-v2",
    },
    "3": {
        "source": "tools/reproduce_phase2_native_builds_v3.py",
        "source_sha256": "c33d8e89c4b86f06e7cc06ecef9bca7052af86191d2e09ac89e665500147ba6f",
        "protocol": "oracle/phase2/NATIVE-SOURCE-BUILDS-V3.md",
        "protocol_sha256": "273e5de944b661ec1f5cfbe3a26bcabc2e9b8c04353891fcfb822b07955eace3",
        "schema": "rebar-phase2-independent-native-source-build-v3",
    },
}
FAMILY_BUILD_VERSION = {"c": "2", "rust": "2", "zig": "3"}
FAMILIES = ("rust", "c", "zig")
CASE_DENOMINATOR = 31_237
SUITE_COUNT = 13
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_PLAIN_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 96 * 1024 * 1024
MAX_REPORT_BYTES = 32 * 1024 * 1024
MAX_LABEL_LENGTH = 48
TIMEOUT_SECONDS = 3_600
PROJECTED_REFERENCE_SHA256 = "cf5633c8dc1038d650603eee421371285d0e32f6446190ce728590f1f5c55021"
THREAD_WARNING_SHA256 = "f28af6781328eacabdbe96460e8c54cba1e7802f6a052cefb4a7c59f30ce4413"


class CandidateGateError(Exception):
    """A frozen result, owner, case identity, or isolation boundary failed."""


class SourceOnlyEffect(CandidateGateError):
    """A synthetic check attempted a real external operation."""


@dataclass(frozen=True, slots=True)
class SuiteSpec:
    name: str
    case_count: int
    source_relative: str
    source_sha256: str
    matrix_sha256: str
    reference_sha256: str
    seed: int | None = None
    recorder_relative: str | None = None
    recorder_sha256: str | None = None
    baseline_label: str | None = None
    evidence_slug: str | None = None
    label_suffix: str | None = None


FROZEN_SUITES = (
    SuiteSpec("original_bounded_v5", 151,
              "tools/independent_original_cpython_suite_v5.py",
              "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
              "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240",
              "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"),
    SuiteSpec("public_v3", 864,
              "tools/rust_public_practice_benchmark_v1.py",
              "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37",
              "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e",
              "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c",
              5928217332825411633),
    SuiteSpec("scanner_v3", 1024,
              "tools/rust_scanner_differential_v1.py",
              "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7",
              "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c",
              "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d",
              5999710933164053041),
    SuiteSpec("buffer_v3", 768,
              "tools/rust_memoryview_expand_differential_v1.py",
              "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6",
              "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60",
              "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75",
              5567953616029762609),
    SuiteSpec("managed_v1", 1024,
              "tools/independent_managed_buffer_lifetime_v1.py",
              "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489",
              "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976",
              "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df",
              5567095966978627121,
              "tools/record_independent_managed_buffer_candidates_v1.py",
              "d7f9fdeb9979eaeaa5ffdcea5a655be31c070356d93d293289b9b90de876877a",
              "shared-suite-v1", "managed-buffer-lifetime-v1", "managed"),
    SuiteSpec("scanner_verbose_v1", 2854,
              "tools/independent_scanner_verbose_comments_v1.py",
              "5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d",
              "01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b",
              "d7e2d499eb4dbe6ae0f8743d8b152e4835898656daa8b3167598636ef7be6012",
              5999725261024810545,
              "tools/record_independent_scanner_verbose_comments_v1.py",
              "d75934bef992e01ad5c1131a8abef997d3b540f8b150518822ad7e55c39c9191",
              "shared-suite-v1", "scanner-verbose-comments-v1", "verbose"),
    SuiteSpec("public_types_v1", 6912,
              "tools/independent_public_type_identity_serialization_v1.py",
              "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20",
              "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123",
              "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21",
              6077977430793212465,
              "tools/record_independent_public_type_identity_serialization_v1.py",
              "ee3e6fc00991758fee93b710a63dad9094f881f1ea57777cae2415397f752eae",
              "shared-suite-v1", "public-type-identity-serialization-v1", "types"),
    SuiteSpec("substitution_v2", 5120,
              "tools/independent_substitution_buffer_semantics_v2.py",
              "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573",
              "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54",
              "2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b",
              6004778603531028017,
              "tools/record_independent_substitution_buffer_semantics_v3.py",
              "1e6bd77cea22c511ca3ee0ccdd4c02b12b4aa22c4fb79cb0df74d2894280807c",
              "shared-suite-v2", "substitution-buffer-semantics-v2", "substitution"),
    SuiteSpec("shape_v2", 10240,
              "tools/independent_shape_changing_buffer_semantics_v2.py",
              "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c",
              "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8",
              "58bbc78828ba2d4cde6b99cbebea815ce9381cda24d0acec03f6cc095b8b643c",
              6001118316486346290,
              "tools/record_independent_shape_changing_buffer_semantics_v2.py",
              "0ddcb154378807ce6d3b8c5726f37e72ed9fcf921fe348d7640e1a6f1a898cc9",
              "shared-suite-v2", "shape-changing-buffer-semantics-v2", "shape"),
    SuiteSpec("public_surface_v19", 1376,
              "tools/python_re_public_surface_oracle_stage19.py",
              "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e",
              "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa",
              "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef",
              2026072483),
    SuiteSpec("subinterpreter_v2", 128,
              "tools/python_re_subinterpreter_oracle_v2.py",
              "54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8",
              "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3",
              "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8",
              2026072501),
    SuiteSpec("pep688_v4", 264,
              "tools/python_re_buffer_exporter_oracle_v4.py",
              "8da0b8e5c5519e7335cd1b53ceb7042f1da1f902c486ad8ac35ddf53d8a04490",
              "2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891",
              "7827586e0c7d4f43ac1fbd288f6b28f6a44b810b46274830d3803505c76692a8"),
    SuiteSpec("threaded_pattern_v1", 512,
              "tools/python_re_threaded_pattern_oracle_v1.py",
              "05226e59736d8721a975eda8afa10247213999690c2766a7b3235c567b9f8276",
              "a7d467e3e529204946fe00ddb819e734421e7087ea909af9ec24b757e42afa0b",
              "928ea100d6fdaecc7c1dcf01e32c24fd98a146964c0955989a8149c1216ffe81",
              2026072701),
)

HISTORICAL_V5: dict[str, dict[str, Any]] = {
    "c": {
        "passing_suites": 7,
        "qualified_cases": 7197,
        "semantic_mismatches": 2094,
        "outer_archive": "f8c4465be0d982445f79ec66744c710b20c64bd308eaff8a12ba571b5bb0ef91",
        "outer_receipt": "10b1bb903ae3e6cf6b0b732e0518bfadce8f17a0021c36ba86bef1e641da07a1",
        "worker_archive": "149bc01c571c15034896d26eb05708985a7a3a49e361e26199682860f8c83e13",
        "worker_receipt": "fc68840c6bbf0e9bc1510894b575d0111246401eba70e8706e2a33542365fc55",
        "restoration": "2bc016478561ea93c4783773a89789af4534368b9388f2d81baf2aefcdeb9dde",
        "nested_archive": "e375edafd74a0b77e349178b59d2d38d2cf423272b9b91dfb4baad91ad94c0f6",
        "nested_receipt": "3e05efd1a83cd650ab3d91cebf0380df0f0cacd5758e6c92f91e08f8acd26a62",
        "specialized": {
            "managed_v1": ("687ba3fbaa15ac56977f78c50027041a67b8db8cf0570af1e2afd99c7e789328", "42ce0458d9ac184a92697788f67f0658cacab96639324aa1ef76c6bc68b41d09"),
            "scanner_verbose_v1": ("13a354c15343cb50449ebe4c2900a94f9ad1b0a937ae4f84690edc577f5a7a9a", "7be61fe54d99949627ec85a64e323de7afaac3fc684de1a53377d5973722cce4"),
            "public_types_v1": ("4d17b3443e543d83a160e5c7d5fd32542415cf41e424369106a9be8e58434e4a", "2c046b2107b3eb7485eb12765b7858f925662fb0e6e37023c37cdf1481a27551"),
            "substitution_v2": ("07c66a0d0e2d08b4886241741087a8c40d5898a6824e90d50dc9c2aba271fc1b", "ed9797fe2e7b66302383af944efce4b53a83f24a864cd4a222effc98ff47cb35"),
            "shape_v2": ("9e43e7613e9f41ee646da7922baeb943a11df0b4175bb4d52a8ecd62429362da", "7dbc8a952fcc71537b0074fae9375850a1b4cb455c029dc2ad992fc13fd1457e"),
        },
    },
    "rust": {
        "passing_suites": 8,
        "qualified_cases": 7461,
        "semantic_mismatches": 2042,
        "outer_archive": "bf0915a4dab62ebaea67b92258eafbc01f52b436b70f81bf7e0ca42211f95bff",
        "outer_receipt": "72070ab4f68200c305d317a59c7ff6405888d23fadaaf04835aba68d33a6c6ec",
        "worker_archive": "a2106050b59130a9eb7f083d13c2e42e22dcf9a33f5a7b35b634ff9dd9b2f9ae",
        "worker_receipt": "f6fe003c100a93e06239a072380c4f3839dc9863391b939ebfc6d667b174f0d9",
        "restoration": "3cd828fbd507d048d0e80715efef754930e89f3c176717ba1dd8985784832889",
        "nested_archive": "b73ea6fd2f944a46bbc89a593df251a054f62bed288b60765eb3c9dc3a9619cd",
        "nested_receipt": "99b32d784182800b92b3fcb555add6c8d27d599a91dc5255b46ca597667c6049",
        "specialized": {
            "managed_v1": ("74a5ede2b9c75b9ad9a1d7ecc2802786793197c8a1f399046d5d6d1997b781ca", "f63816d95048ed26bf1572d87676d91364761369fdfb5c49f65d1bcf3ef3ccf7"),
            "scanner_verbose_v1": ("8f1b6df4044970fed48eecdf2b6bcd9434dcee1956abf8a3308fec80fad6d44a", "929f4899b211d795c8a5e570148ca19c984d2dbeb78fda18ba89701ddee1e241"),
            "public_types_v1": ("f5819a54871a88edf3c6e1b302d67809e5c74cc1912e9bba91a57b6f2e237772", "ab6b37f02ef81945bef6a3f38dcaa9a7c4594a0cd6d851ecf9df89aa2507646a"),
            "substitution_v2": ("49c9bf367ddef35d1970b07c483d4468da9e09348522a26780bf0495391673fa", "4905f6cd20f44453b16f0598e5e77ffa99340107a229987c1728b9635a9e7e60"),
            "shape_v2": ("ee69217102b87f5c5a288c2fa58b44a1e881f46191f21520e6510313cf346b00", "339a1744bffc467495daa4992622d3cfca0219bc4e7433cb21910b46c04b467c"),
        },
    },
}

if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise CandidateGateError(message)


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(value, ensure_ascii=True, allow_nan=False,
                       sort_keys=True, separators=(",", ":")).encode("ascii")
            + b"\n"
        )
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise CandidateGateError("require bounded, finite canonical evidence") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require an exact lowercase SHA-256: " + label)
    return value


def checked_family(value: Any) -> str:
    require(type(value) is str and value in FAMILIES,
            "select exactly one independent Rust, C, or Zig candidate")
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL_LENGTH
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(char in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in value)
            and "--" not in value and not value.endswith("-"),
            "require an exact lowercase non-traversing evidence label")
    return value


def checked_case_count(value: Any, maximum: int, label: str) -> int:
    require(type(value) is int and 0 <= value <= maximum,
            "require an exact real case count: " + label)
    return value


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject duplicate or non-string evidence keys")
        result[key] = value
    return result


def decode_document(raw: Any, label: str, *, canonical_required: bool = False,
                    maximum: int = MAX_PLAIN_BYTES) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= maximum,
            "require complete bounded JSON evidence: " + label)
    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique_pairs,
            parse_constant=lambda name: (_ for _ in ()).throw(
                CandidateGateError("reject non-finite JSON: " + name)),
        )
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise CandidateGateError("reject malformed complete evidence: " + label) from error
    require(type(value) is dict, "require a complete JSON object: " + label)
    if canonical_required:
        require(canonical(value) == raw,
                "reject noncanonical, altered, or incomplete evidence: " + label)
    return value


def bounded_gzip(raw: bytes, label: str, *, maximum: int = MAX_PLAIN_BYTES) -> bytes:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES
            and type(maximum) is int and 0 < maximum <= MAX_PLAIN_BYTES,
            "require a strictly bounded compressed owner: " + label)
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as stream:
            plain = stream.read(maximum + 1)
            require(0 < len(plain) <= maximum,
                    "reject an oversized decompressed evidence archive: " + label)
            require(stream.read(1) == b"",
                    "reject an extra decompressed evidence suffix: " + label)
    except (OSError, EOFError, gzip.BadGzipFile, ValueError) as error:
        raise CandidateGateError("reject a corrupt gzip archive: " + label) from error
    return plain


def safe_relative(relative: Any, allowed: frozenset[str]) -> tuple[str, ...]:
    require(type(relative) is str and relative in allowed
            and not relative.startswith("/") and "\\" not in relative
            and "\x00" not in relative,
            "read only an independently predetermined evidence owner")
    parts = tuple(relative.split("/"))
    require(bool(parts) and all(part not in {"", ".", ".."} for part in parts)
            and not any(part in {"holdout", "hidden", "benchmark", "benchmarks",
                                 "performance"} for part in parts),
            "reject traversal, hidden cases, benchmarks, and broad file roots")
    return parts


def read_owned(relative: str, expected: str, *, allowed: frozenset[str],
               maximum: int = MAX_SOURCE_BYTES) -> tuple[bytes, dict[str, Any]]:
    checked_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_PLAIN_BYTES,
            "require a strict positive typed evidence size bound")
    parts = safe_relative(relative, allowed)
    regular = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
               | getattr(os, "O_NOFOLLOW", 0))
    directory = regular | getattr(os, "O_DIRECTORY", 0)
    descriptors: list[int] = []
    try:
        parent = os.open(str(ROOT), directory)
        descriptors.append(parent)
        for part in parts[:-1]:
            parent = os.open(part, directory, dir_fd=parent)
            descriptors.append(parent)
            require(stat.S_ISDIR(os.fstat(parent).st_mode),
                    "reject a replaced or symlinked evidence parent")
        descriptor = os.open(parts[-1], regular, dir_fd=parent)
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        visible = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and 0 < before.st_size <= maximum,
                "reject a symlinked, substituted, empty, or oversized owner")
        hasher = hashlib.sha256()
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(type(block) is bytes and bool(block),
                    "reject a truncated independently owned file")
            hasher.update(block)
            pieces.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"",
                "reject an unannounced owned-file suffix")
        after = os.fstat(descriptor)
        final = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (after.st_dev, after.st_ino, after.st_size)
                == (final.st_dev, final.st_ino, final.st_size)
                and hasher.hexdigest() == expected,
                "reject changed inode, size, timestamps, or SHA-256")
        raw = b"".join(pieces)
        return raw, {
            "relative": relative,
            "path": str(ROOT / relative),
            "sha256": expected,
            "size_bytes": len(raw),
            "device": after.st_dev,
            "inode": after.st_ino,
            "mode": stat.S_IMODE(after.st_mode),
        }
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def import_frozen(relative: str, expected: str,
                  allowed: frozenset[str]) -> types.ModuleType:
    read_owned(relative, expected, allowed=allowed)
    name = relative.removesuffix(".py").replace("/", ".")
    module = importlib.import_module(name)
    require(type(module) is types.ModuleType and module.__name__ == name
            and os.path.abspath(str(module.__file__)) == str(ROOT / relative),
            "reject a copied, rebound, or replaced correctness source: " + relative)
    read_owned(relative, expected, allowed=allowed)
    return module


def suite_spec(name: Any) -> SuiteSpec:
    require(type(name) is str, "select exactly one frozen producer")
    matches = [suite for suite in FROZEN_SUITES if suite.name == name]
    require(len(matches) == 1, "reject an omitted or substituted correctness suite")
    return matches[0]


def specialized_evidence_paths(suite: SuiteSpec, family: str,
                               run_label: str) -> tuple[str, str]:
    require(suite.evidence_slug is not None and suite.label_suffix is not None,
            "only an independently frozen recorder owns specialized evidence")
    family = checked_family(family)
    label = checked_label(checked_label(run_label) + "-" + suite.label_suffix)
    stem = ("experiments/rust_public_practice_v1/" + family + "-"
            + suite.evidence_slug + "-" + label)
    return stem + ".json.gz", stem + "-publication-receipt.json"


def nested_evidence_paths(family: str, run_label: str, *, version: str,
                          failure: bool) -> tuple[str, str]:
    require(version in {"1", "3"}, "select only an original signed nested owner")
    family = checked_family(family)
    label = checked_label(checked_label(run_label) + "-subinterpreters")
    stem = ("oracle/phase2/evidence/owned-candidate-subinterpreters-v"
            + version + "-" + family + "-" + label)
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def historical_evidence_paths(family: str) -> dict[str, str]:
    family = checked_family(family)
    require(family in HISTORICAL_V5,
            "only genuinely published C and Rust V5 campaigns are historical")
    values = HISTORICAL_V5[family]
    prefix = "oracle/phase2/evidence/"
    stem = "frozen-p0-candidate-v5-" + family + "-phase2-v5-failures"
    worker = "frozen-p0-candidate-worker-v3-" + family + "-phase2-v5-failures"
    paths = {
        prefix + stem + ".json.gz": values["outer_archive"],
        prefix + stem + "-publication-receipt.json": values["outer_receipt"],
        prefix + worker + ".json.gz": values["worker_archive"],
        prefix + worker + "-publication-receipt.json": values["worker_receipt"],
        prefix + "frozen-p0-candidate-v5-" + family
        + "-phase2-v5-restoration-receipt.json": values["restoration"],
    }
    nested_archive, nested_receipt = nested_evidence_paths(
        family, "phase2-v5", version="1", failure=True,
    )
    paths[nested_archive] = values["nested_archive"]
    paths[nested_receipt] = values["nested_receipt"]
    for name, pair in values["specialized"].items():
        archive, receipt = specialized_evidence_paths(
            suite_spec(name), family, "phase2-v5",
        )
        paths[archive], paths[receipt] = pair
    require(len(paths) == 17,
            "preserve exactly sixteen real family artifacts and one restoration")
    return dict(sorted(paths.items()))


def capture_stream(raw: Any) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "preserve a complete bounded original process stream")
    return {
        "encoding": "base64",
        "data": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
    }


def restore_stream(record: Any, label: str) -> bytes:
    require(type(record) is dict and record.get("complete") is True,
            "require a complete authenticated process stream: " + label)
    if set(record) == {"encoding", "data", "bytes", "sha256", "complete"}:
        require(record.get("encoding") == "base64"
                and type(record.get("data")) is str,
                "require the frozen original process-stream codec: " + label)
        encoded = record["data"]
    elif set(record) == {"base64", "bytes", "sha256", "complete"}:
        require(type(record.get("base64")) is str,
                "require the frozen specialized process-stream codec: " + label)
        encoded = record["base64"]
    else:
        raise CandidateGateError("reject omitted or extra process-stream fields: " + label)
    expected = checked_digest(record.get("sha256"), label)
    require(type(record.get("bytes")) is int
            and 0 <= record["bytes"] <= MAX_PROCESS_BYTES,
            "require the exact bounded actual stream length: " + label)
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as error:
        raise CandidateGateError("reject malformed exact process base64: " + label) from error
    require(len(raw) == record["bytes"]
            and hashlib.sha256(raw).hexdigest() == expected,
            "reject a truncated or substituted actual process stream: " + label)
    return raw


def compare_records(expected: Any, actual: Any, *, suite: str,
                    identity: str, expected_count: int) -> list[dict[str, Any]]:
    require(type(expected) is list and type(actual) is list
            and len(expected) == len(actual) == expected_count,
            "preserve every source-ordered actual and frozen case: " + suite)
    differences: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, (reference, observed) in enumerate(zip(expected, actual, strict=True)):
        require(type(reference) is dict and type(observed) is dict,
                "preserve complete typed frozen and candidate rows: " + suite)
        case = reference.get(identity)
        require(type(case) is str and case not in seen
                and observed.get(identity) == case,
                "reject omitted, repeated, or reordered case identities: " + suite)
        seen.add(case)
        if reference != observed:
            differences.append({
                "index": index,
                "case": case,
                "cohort": reference.get("cohort", reference.get("group")),
                "expected_record": reference,
                "actual_record": observed,
            })
    return differences


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {name: 0 for name in (
        "file_reads", "file_writes", "candidate_imports",
        "reference_workers", "candidate_workers", "source_builds",
        "native_promotions", "native_libraries_loaded", "thread_starts",
        "interpreter_creations", "clock_samples", "gc_collections",
        "network_requests", "hidden_cases_read", "benchmark_files_read",
        "blocked_reads", "blocked_writes", "blocked_imports",
        "blocked_processes", "blocked_promotions", "blocked_threads",
        "blocked_clocks", "blocked_gc", "blocked_network",
    )}
    installed: list[tuple[Any, str, Any]] = []

    def deny(field: str, reason: str) -> Callable[..., Any]:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            effects[field] += 1
            raise SourceOnlyEffect(reason)
        return blocked

    def install(owner: Any, name: str, field: str) -> None:
        if hasattr(owner, name):
            installed.append((owner, name, getattr(owner, name)))
            setattr(owner, name, deny(field, "source-only boundary: " + name))

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"),
            (os, "read"), (os, "stat"), (os, "lstat"),
            (Path, "open"), (Path, "read_bytes"), (Path, "read_text"),
        ):
            install(owner, name, "blocked_reads")
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"),
            (os, "rename"), (os, "mkdir"), (os, "rmdir"), (os, "fsync"),
            (Path, "write_bytes"), (Path, "write_text"),
            (Path, "mkdir"), (Path, "unlink"),
        ):
            install(owner, name, "blocked_writes")
        install(os, "replace", "blocked_promotions")
        install(importlib, "import_module", "blocked_imports")
        install(subprocess, "Popen", "blocked_processes")
        install(subprocess, "run", "blocked_processes")
        install(threading.Thread, "start", "blocked_threads")
        install(socket, "create_connection", "blocked_network")
        install(socket.socket, "connect", "blocked_network")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "thread_time"):
            install(time, name, "blocked_clocks")
        install(gc, "collect", "blocked_gc")
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def protocol_document() -> dict[str, Any]:
    """Describe a prospective freeze without reading any source or evidence."""
    suites = []
    for suite in FROZEN_SUITES:
        row: dict[str, Any] = {
            "id": suite.name,
            "case_count": suite.case_count,
            "source_path": suite.source_relative,
            "source_sha256": suite.source_sha256,
            "matrix_sha256": suite.matrix_sha256,
            "reference_records_sha256": suite.reference_sha256,
            "published_seed": suite.seed,
        }
        if suite.recorder_relative is not None:
            row.update(
                candidate_recorder_path=suite.recorder_relative,
                candidate_recorder_sha256=suite.recorder_sha256,
                baseline_label=suite.baseline_label,
                evidence_slug=suite.evidence_slug,
                evidence_label_suffix=suite.label_suffix,
            )
        if suite.name == "original_bounded_v5":
            row.update(public_records=152, runnable_cases=151,
                       genuine_public_debug_skips=1,
                       named_private_waivers=13)
        if suite.name == "public_surface_v19":
            row.update(real_locale_cases=64, real_locale_transitions=192,
                       canonical_digest="original-stage17-without-newline")
        if suite.name == "pep688_v4":
            row.update(canonical_digest="original-pep688-with-newline")
        if suite.name == "threaded_pattern_v1":
            row.update(canonical_digest="original-threaded-without-newline")
        if suite.name == "subinterpreter_v2":
            row.update(actual_interpreters_required=11,
                       actual_case_interpreter_exec_calls_required=394,
                       actual_initialization_calls_required=11,
                       actual_cleanup_calls_required=11,
                       projected_reference_records_sha256=
                       PROJECTED_REFERENCE_SHA256,
                       supplemental_cases_added_to_denominator=False)
        suites.append(row)
    history = []
    for family in ("c", "rust"):
        observed = HISTORICAL_V5[family]
        history.append({
            "candidate_family": family,
            "actual_passing_suite_count": observed["passing_suites"],
            "actual_qualified_case_count": observed["qualified_cases"],
            "actual_semantic_mismatch_count": observed["semantic_mismatches"],
            "overall_status": "FAIL",
            "candidate_qualified": False,
            "suite_process_attempt_count": SUITE_COUNT,
            "original_case_denominator": CASE_DENOMINATOR,
            "actual_case_interpreter_exec_calls":
            0 if family == "c" else "NOT ESTABLISHED",
            "unverified_original_interpreter_cases": 128,
            "published_artifact_count": 16,
            "separate_restoration_receipt_count": 1,
            "artifacts": [
                {"path": path, "sha256": fingerprint}
                for path, fingerprint in historical_evidence_paths(family).items()
            ],
        })
    return {
        "schema": PROTOCOL_SCHEMA,
        "version": 6,
        "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; VERSION-SIX CANDIDATES NOT RUN",
        "goal_sha256": GOAL_SHA256,
        "phase1": {
            "inventory_path": P0_RELATIVE,
            "inventory_sha256": P0_SHA256,
            "verifier_path": P0_VERIFIER_RELATIVE,
            "verifier_sha256": P0_VERIFIER_SHA256,
            "python_path": PINNED_PYTHON,
            "python_sha256": PINNED_PYTHON_SHA256,
            "python_version": "3.14.6",
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "public_obligation_count": 73,
            "named_private_waiver_count": 13,
            "runnable_original_public_method_count": 151,
            "preserved_original_public_record_count": 152,
            "genuine_original_public_debug_skip_count": 1,
        },
        "runner": {
            "source_path": "tools/run_frozen_p0_candidate_v6.py",
            "source_sha256_mode":
            "mandatory-exact-caller-pinned-published-source-bytes",
        },
        "full_case_worker": {
            "source_path": SOURCE_RELATIVE,
            "schema": SCHEMA,
            "source_sha256_mode":
            "mandatory-exact-caller-pinned-published-source-bytes",
            "all_original_suite_routes_required": True,
            "producer_zero_or_one_exit_authenticated_before_status": True,
            "child_chosen_owner_path_allowed": False,
            "receipt_pass_is_candidate_pass": False,
            "maximum_published_uncompressed_report_bytes": MAX_REPORT_BYTES,
        },
        "preserved_candidate_sources": [
            {"path": V1_RELATIVE, "sha256": V1_SHA256},
            {"path": V2_RELATIVE, "sha256": V2_SHA256},
            {"path": V3_RELATIVE, "sha256": V3_SHA256},
            {"path": V4_RELATIVE, "sha256": V4_SHA256},
            {"path": V5_RELATIVE, "sha256": V5_SHA256},
            {"path": V5_WORKER_RELATIVE, "sha256": V5_WORKER_SHA256},
        ],
        "preserved_earlier_real_failures": [
            {"version": 3, "candidate_family": "c", "status": "FAIL",
             "archive_path": V3_FAILURE_RELATIVE,
             "archive_sha256": V3_FAILURE_SHA256,
             "receipt_path": V3_FAILURE_RECEIPT_RELATIVE,
             "receipt_sha256": V3_FAILURE_RECEIPT_SHA256},
            {"version": 4, "candidate_family": "c", "status": "FAIL",
             "archive_path": V4_FAILURE_RELATIVE,
             "archive_sha256": V4_FAILURE_SHA256,
             "receipt_path": V4_FAILURE_RECEIPT_RELATIVE,
             "receipt_sha256": V4_FAILURE_RECEIPT_SHA256},
        ],
        "corrected_canonical_activation": {
            "source_path": ACTIVATION_RELATIVE,
            "source_sha256": ACTIVATION_SHA256,
            "protocol_path": ACTIVATION_PROTOCOL_RELATIVE,
            "protocol_sha256": ACTIVATION_PROTOCOL_SHA256,
            "schema": ACTIVATION_SCHEMA,
            "version": 2,
            "explicit_build_version_required": True,
            "genuine_promotion_intents_required": True,
            "original_guard_copy_or_rebinding_allowed": False,
            "canonical_import_root": str(ROOT),
        },
        "native_source_builds": [
            {
                "version": int(version),
                "source_path": build["source"],
                "source_sha256": build["source_sha256"],
                "protocol_path": build["protocol"],
                "protocol_sha256": build["protocol_sha256"],
                "schema": build["schema"],
                "required_independent_fresh_phase_count": 2,
            }
            for version, build in BUILD_VERSIONS.items()
        ],
        "candidate_families": [
            {"name": family, "build_version": int(FAMILY_BUILD_VERSION[family]),
             "independently_owned_parser_compiler_executor_required": True,
             "external_engine_or_sibling_delegation_allowed": False}
            for family in FAMILIES
        ],
        "corrected_original_subinterpreter_owner": {
            "source_path": NESTED_V3_RELATIVE,
            "source_sha256": NESTED_V3_SHA256,
            "protocol_path": NESTED_V3_DOCUMENT_RELATIVE,
            "protocol_sha256": NESTED_V3_DOCUMENT_SHA256,
            "explanation_path": NESTED_V3_PROTOCOL_RELATIVE,
            "explanation_sha256": NESTED_V3_PROTOCOL_SHA256,
            "version": 3,
            "original_case_count": 128,
            "required_case_interpreter_exec_calls": 394,
            "required_interpreters_created": 11,
            "required_interpreters_destroyed": 11,
            "required_initialization_calls": 11,
            "required_cleanup_calls": 11,
            "supplemental_cases_added_to_original_denominator": False,
        },
        "preserved_v5_actual_campaigns": history,
        "suites": suites,
        "failure_evidence": {
            "producer_report_and_receipt_fixed_before_invocation": True,
            "producer_complete_stdout_and_stderr_required": True,
            "candidate_exit_one_authenticated_before_status": True,
            "publication_receipt_status_pass_means_durable_publication_only": True,
            "all_signed_baseline_and_candidate_rows_reconstructed": True,
            "every_actual_expected_and_observed_mismatch_retained": True,
            "exact_64_bit_published_seeds_required": True,
            "unknown_interpreter_cases_count_as_executed": False,
            "source_specific_reference_digest_required": True,
        },
        "publication": {
            "directory": "oracle/phase2/evidence",
            "worker_archive_prefix": "frozen-p0-candidate-worker-v4-",
            "aggregate_archive_prefix": "frozen-p0-candidate-v6-",
            "exclusive_creation": True,
            "no_follow": True,
            "same_inode_readback_required": True,
            "file_and_directory_fsync_required": True,
            "deterministic_gzip_mtime": 0,
            "maximum_uncompressed_report_bytes": MAX_REPORT_BYTES,
        },
        "boundaries": {
            "fresh_reference_workers_started": 0,
            "original_python_engine_delegation_allowed": False,
            "external_regex_engine_allowed": False,
            "cross_candidate_delegation_allowed": False,
            "fallback_allowed": False,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "final_holdout_authorized": False,
            "final_holdout_opened": False,
            "final_winner_selected": False,
        },
        "candidate_results": "NOT MEASURED",
    }


def validate_protocol_document(value: Any) -> dict[str, Any]:
    require(type(value) is dict and canonical(value) == canonical(protocol_document()),
            "the exact independently frozen V6 correctness protocol changed")
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and sys.path and sys.path[0] == str(ROOT),
            "use the exact isolated frozen CPython and canonical V4 worker")


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, operation: Callable[[], Any]) -> Any:
        try:
            observed = operation()
        except Exception as error:
            raise CandidateGateError("a mandatory synthetic positive failed: " + name) from error
        accepted.append(name)
        return observed

    def reject(name: str, operation: Callable[[], Any]) -> None:
        try:
            operation()
        except (CandidateGateError, SourceOnlyEffect, TypeError, ValueError,
                KeyError, OverflowError, UnicodeError, RecursionError):
            rejected.append(name)
            return
        raise CandidateGateError("a mandatory hostile control escaped: " + name)

    with source_only_boundary() as effects:
        document = accept("accept-complete-frozen-independent-version-six-protocol",
                          lambda: validate_protocol_document(protocol_document()))
        accept("preserve-exactly-thirteen-original-frozen-suites",
               lambda: require(len(FROZEN_SUITES) == SUITE_COUNT,
                               "all original suites are mandatory"))
        accept("preserve-exactly-31237-original-runnable-executions",
               lambda: require(sum(item.case_count for item in FROZEN_SUITES)
                               == CASE_DENOMINATOR,
                               "never alter or duplicate the original denominator"))
        accept("retain-152-original-public-records-but-only-151-runnable-cases",
               lambda: require(document["suites"][0]["public_records"] == 152
                               and document["suites"][0]["runnable_cases"] == 151
                               and document["suites"][0]["genuine_public_debug_skips"] == 1,
                               "never count the actual named debug skip as matching"))
        accept("retain-exact-independent-published-corrected-nested-v3",
               lambda: require(all(type(pin) is str and len(pin) == 64
                                   for pin in (NESTED_V3_SHA256,
                                               NESTED_V3_DOCUMENT_SHA256,
                                               NESTED_V3_PROTOCOL_SHA256)),
                               "pin the separately pushed corrected nested owner"))
        for family in ("c", "rust"):
            paths = accept("retain-all-seventeen-published-" + family + "-owners",
                           lambda family=family: historical_evidence_paths(family))
            accept("retain-sixteen-actual-" + family + "-reports-plus-restoration",
                   lambda paths=paths: require(len(paths) == 17,
                       "preserve every actual report, receipt, and restoration"))
            accept("retain-honest-original-" + family + "-passing-case-count",
                   lambda family=family: require(
                       HISTORICAL_V5[family]["qualified_cases"]
                       == (7197 if family == "c" else 7461),
                       "never propagate the incorrect V5 aggregate zero"))
            for relative, fingerprint in paths.items():
                accept("accept-historical-" + family + "-" + relative.rsplit("/", 1)[-1],
                       lambda fingerprint=fingerprint: checked_digest(
                           fingerprint, "genuine previously published owner"))
                reject("reject-forged-historical-" + family + "-"
                       + relative.rsplit("/", 1)[-1],
                       lambda fingerprint=fingerprint: require(
                           checked_digest("0" * 64, "forged owner") == fingerprint,
                           "reject a substituted historical artifact"))
        for index, suite in enumerate(FROZEN_SUITES):
            accept("resolve-exact-source-owned-suite-" + suite.name,
                   lambda suite=suite: suite_spec(suite.name))
            for field in ("id", "case_count", "source_path", "source_sha256",
                          "matrix_sha256", "reference_records_sha256", "published_seed"):
                def alter(index: int = index, field: str = field) -> Any:
                    forged = protocol_document()
                    old = forged["suites"][index][field]
                    forged["suites"][index][field] = (
                        old + 1 if type(old) is int else
                        "0" * 64 if type(old) is str and field.endswith("sha256") else
                        "forged" if old is None else str(old) + "-forged"
                    )
                    return validate_protocol_document(forged)
                reject("reject-suite-" + suite.name + "-" + field, alter)
            def omit(index: int = index) -> Any:
                forged = protocol_document()
                del forged["suites"][index]
                return validate_protocol_document(forged)
            reject("reject-omitted-frozen-suite-" + suite.name, omit)
        for family in FAMILIES:
            accept("select-independent-source-built-family-" + family,
                   lambda family=family: checked_family(family))
            accept("select-correct-source-build-generation-" + family,
                   lambda family=family: require(
                       FAMILY_BUILD_VERSION[family]
                       == ("3" if family == "zig" else "2"),
                       "reject a cross-version source-built engine"))
        expected = [{"case": "case.0", "outcome": {"status": "return", "value": 1}},
                    {"case": "case.1", "outcome": {"status": "raise",
                                                     "exception": {"type": "ValueError"}}}]
        accept("accept-original-expected-exception-as-a-real-matching-outcome",
               lambda: require(compare_records(expected, expected,
                   suite="synthetic", identity="case", expected_count=2) == [],
                   "a genuine expected exception is not a regex mismatch"))
        changed = [expected[0], {"case": "case.1", "outcome":
                                  {"status": "return", "value": 2}}]
        mismatches = accept("retain-exact-expected-and-actual-failed-outcomes",
                            lambda: compare_records(expected, changed,
                                suite="synthetic", identity="case", expected_count=2))
        accept("preserve-one-exact-source-ordered-mismatch",
               lambda: require(len(mismatches) == 1
                               and mismatches[0]["case"] == "case.1"
                               and mismatches[0]["expected_record"] == expected[1]
                               and mismatches[0]["actual_record"] == changed[1],
                               "never replace real mismatch outcomes with hashes"))
        reject("reject-dropped-original-case", lambda: compare_records(
            expected, changed[:1], suite="synthetic", identity="case", expected_count=2))
        reject("reject-reordered-original-cases", lambda: compare_records(
            expected, list(reversed(changed)), suite="synthetic",
            identity="case", expected_count=2))
        reject("reject-repeated-original-case-identities", lambda: compare_records(
            expected, [changed[0], changed[0]], suite="synthetic",
            identity="case", expected_count=2))
        genuine = capture_stream(b"{\"status\":\"FAIL\"}\n")
        accept("accept-complete-exit-one-failed-producer-stdout",
               lambda: restore_stream(genuine, "source-only genuine failure"))
        for field in ("encoding", "data", "bytes", "sha256", "complete"):
            def forge_stream(field: str = field) -> bytes:
                value = dict(genuine)
                value[field] = (False if field == "complete" else
                                value[field] + 1 if field == "bytes" else
                                "0" * 64 if field == "sha256" else "forged")
                return restore_stream(value, "source-only forged stream")
            reject("reject-truncated-forged-process-stream-" + field, forge_stream)
        allowed = frozenset({"oracle/phase2/evidence/approved.json"})
        accept("accept-independently-predetermined-evidence-path",
               lambda: safe_relative("oracle/phase2/evidence/approved.json", allowed))
        for name, path in (
            ("child-selected", "oracle/phase2/evidence/child-selected.json"),
            ("absolute", "/oracle/phase2/evidence/approved.json"),
            ("parent", "oracle/phase2/evidence/../approved.json"),
            ("backslash", "oracle\\phase2\\evidence\\approved.json"),
            ("holdout", "holdout/approved.json"),
            ("hidden", "hidden/approved.json"),
            ("benchmark", "benchmarks/approved.json"),
            ("nul", "oracle/phase2/\x00/approved.json"),
        ):
            reject("reject-" + name + "-archive-owner-before-open",
                   lambda path=path: safe_relative(path, allowed))
        for field in ("phase1", "full_case_worker", "corrected_canonical_activation",
                      "corrected_original_subinterpreter_owner",
                      "failure_evidence", "publication", "boundaries"):
            for name in document[field]:
                def change(section: str = field, name: str = name) -> Any:
                    forged = protocol_document()
                    value = forged[section][name]
                    forged[section][name] = (
                        not value if type(value) is bool else
                        value + 1 if type(value) is int else
                        "0" * 64 if type(value) is str and name.endswith("sha256") else
                        str(value) + "-forged"
                    )
                    return validate_protocol_document(forged)
                reject("reject-frozen-" + field + "-" + name, change)
        reject("reject-int-one-as-a-literal-true-guard",
               lambda: require(1, "strict literal booleans are mandatory"))
        reject("reject-int-zero-as-a-literal-false-guard",
               lambda: require(type(0) is bool,
                               "integers cannot stand in for frozen false"))
        reject("reject-real-file-reads-from-a-synthetic-source-test",
               lambda: builtins.open("GOAL.md", "rb"))
        reject("reject-real-processes-from-a-synthetic-source-test",
               lambda: subprocess.Popen([PINNED_PYTHON]))
        reject("reject-real-clocks-from-a-synthetic-source-test",
               lambda: time.perf_counter())
        reject("reject-real-native-promotions-from-a-synthetic-source-test",
               lambda: os.replace("synthetic-a", "synthetic-b"))
    for field in ("file_reads", "file_writes", "candidate_imports",
                  "reference_workers", "candidate_workers", "source_builds",
                  "native_promotions", "native_libraries_loaded", "thread_starts",
                  "interpreter_creations", "clock_samples", "gc_collections",
                  "network_requests", "hidden_cases_read", "benchmark_files_read"):
        require(effects[field] == 0,
                "a source-only correctness test had a real effect: " + field)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "synthetic": True,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "preserved_actual_candidate_families": ["c", "rust"],
        "preserved_historical_artifact_count": 32,
        "preserved_historical_restoration_receipt_count": 2,
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "accepted": accepted,
        "rejected": rejected,
        "source_only_effects": effects,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_native_promotions": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


@contextlib.contextmanager
def frozen_context_boundary() -> Iterator[dict[str, int]]:
    """Permit frozen reads and pure validator imports, never real activity."""
    counts = {name: 0 for name in (
        "file_writes", "candidate_imports", "reference_workers",
        "candidate_workers", "source_builds", "native_promotions",
        "native_libraries_loaded", "interpreter_creations", "thread_starts",
        "clock_samples", "network_requests", "hidden_cases_read",
        "benchmark_files_read", "blocked_writes", "blocked_processes",
        "blocked_candidate_imports", "blocked_clocks", "blocked_threads",
        "blocked_network", "blocked_promotions",
    )}
    installed: list[tuple[Any, str, Any]] = []

    def block(field: str, name: str) -> Callable[..., Any]:
        def deny(*args: Any, **kwargs: Any) -> Any:
            counts[field] += 1
            raise SourceOnlyEffect("frozen context forbids " + name)
        return deny

    def install(owner: Any, name: str, field: str) -> None:
        if hasattr(owner, name):
            installed.append((owner, name, getattr(owner, name)))
            setattr(owner, name, block(field, name))

    original_import = importlib.import_module
    original_builtin_open = builtins.open
    original_io_open = io.open
    original_path_open = Path.open
    original_os_open = os.open

    def checked_mode(value: Any) -> None:
        require(type(value) is str and bool(value)
                and not any(flag in value for flag in ("w", "a", "x", "+")),
                "read-only frozen context forbids writable file handles")

    def readonly_builtin_open(file: Any, mode: str = "r",
                              *args: Any, **kwargs: Any) -> Any:
        try:
            checked_mode(mode)
        except CandidateGateError as error:
            counts["blocked_writes"] += 1
            raise SourceOnlyEffect(str(error)) from error
        return original_builtin_open(file, mode, *args, **kwargs)

    def readonly_io_open(file: Any, mode: str = "r",
                         *args: Any, **kwargs: Any) -> Any:
        try:
            checked_mode(mode)
        except CandidateGateError as error:
            counts["blocked_writes"] += 1
            raise SourceOnlyEffect(str(error)) from error
        return original_io_open(file, mode, *args, **kwargs)

    def readonly_path_open(path: Path, mode: str = "r",
                           *args: Any, **kwargs: Any) -> Any:
        try:
            checked_mode(mode)
        except CandidateGateError as error:
            counts["blocked_writes"] += 1
            raise SourceOnlyEffect(str(error)) from error
        return original_path_open(path, mode, *args, **kwargs)

    def readonly_os_open(path: Any, flags: Any,
                         *args: Any, **kwargs: Any) -> int:
        blocked = os.O_CREAT | os.O_TRUNC | os.O_APPEND
        temporary = getattr(os, "O_TMPFILE", 0)
        if (type(flags) is not int
                or (flags & os.O_ACCMODE) != os.O_RDONLY
                or bool(flags & blocked)
                or bool(temporary and (flags & temporary) == temporary)):
            counts["blocked_writes"] += 1
            raise SourceOnlyEffect("frozen context forbids writable file descriptors")
        return original_os_open(path, flags, *args, **kwargs)

    def pure_import(name: str, package: str | None = None) -> types.ModuleType:
        if name == "candidates" or name.startswith("candidates."):
            counts["blocked_candidate_imports"] += 1
            raise SourceOnlyEffect("frozen context cannot import a native candidate")
        return original_import(name, package)

    try:
        for owner, name, replacement in (
            (builtins, "open", readonly_builtin_open),
            (io, "open", readonly_io_open),
            (Path, "open", readonly_path_open),
            (os, "open", readonly_os_open),
        ):
            installed.append((owner, name, getattr(owner, name)))
            setattr(owner, name, replacement)
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"), (os, "rename"),
            (os, "mkdir"), (os, "makedirs"), (os, "rmdir"),
            (os, "removedirs"), (os, "fsync"), (os, "link"),
            (os, "symlink"), (os, "truncate"), (os, "ftruncate"),
            (os, "chmod"), (os, "chown"),
            (Path, "write_bytes"), (Path, "write_text"), (Path, "unlink"),
            (Path, "touch"), (Path, "mkdir"), (Path, "rmdir"),
            (Path, "rename"), (Path, "replace"), (Path, "chmod"),
            (Path, "symlink_to"), (Path, "hardlink_to"),
            (tempfile, "mkstemp"), (tempfile, "mkdtemp"),
            (tempfile, "NamedTemporaryFile"), (tempfile, "TemporaryFile"),
            (tempfile, "TemporaryDirectory"),
        ):
            install(owner, name, "blocked_writes")
        install(os, "replace", "blocked_promotions")
        install(subprocess, "Popen", "blocked_processes")
        install(subprocess, "run", "blocked_processes")
        install(threading.Thread, "start", "blocked_threads")
        install(socket, "create_connection", "blocked_network")
        install(socket.socket, "connect", "blocked_network")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns"):
            install(time, name, "blocked_clocks")
        installed.append((importlib, "import_module", original_import))
        importlib.import_module = pure_import
        yield counts
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def fixed_source_owners(options: argparse.Namespace) -> dict[str, str]:
    """Construct an independent allow-list before accepting child evidence."""
    build_version = getattr(options, "build_version", None)
    build_keys = BUILD_VERSIONS if build_version is None else {
        str(build_version): BUILD_VERSIONS.get(str(build_version), {}),
    }
    fixed: dict[str, str] = {
        "GOAL.md": GOAL_SHA256,
        P0_RELATIVE: P0_SHA256,
        P0_VERIFIER_RELATIVE: P0_VERIFIER_SHA256,
        V1_RELATIVE: V1_SHA256,
        V1_PROTOCOL_RELATIVE: V1_PROTOCOL_SHA256,
        V1_DOCUMENT_RELATIVE: V1_DOCUMENT_SHA256,
        V2_RELATIVE: V2_SHA256,
        V3_RELATIVE: V3_SHA256,
        V3_PROTOCOL_RELATIVE: V3_PROTOCOL_SHA256,
        V3_DOCUMENT_RELATIVE: V3_DOCUMENT_SHA256,
        V3_FAILURE_RELATIVE: V3_FAILURE_SHA256,
        V3_FAILURE_RECEIPT_RELATIVE: V3_FAILURE_RECEIPT_SHA256,
        V4_RELATIVE: V4_SHA256,
        V4_PROTOCOL_RELATIVE: V4_PROTOCOL_SHA256,
        V4_DOCUMENT_RELATIVE: V4_DOCUMENT_SHA256,
        V4_FAILURE_RELATIVE: V4_FAILURE_SHA256,
        V4_FAILURE_RECEIPT_RELATIVE: V4_FAILURE_RECEIPT_SHA256,
        V5_RELATIVE: V5_SHA256,
        V5_WORKER_RELATIVE: V5_WORKER_SHA256,
        V5_DOCUMENT_RELATIVE: V5_DOCUMENT_SHA256,
        V5_PROTOCOL_RELATIVE: V5_PROTOCOL_SHA256,
        ACTIVATION_RELATIVE: ACTIVATION_SHA256,
        ACTIVATION_PROTOCOL_RELATIVE: ACTIVATION_PROTOCOL_SHA256,
        AUDIT_RELATIVE: AUDIT_SHA256,
        CORE_RELATIVE: CORE_SHA256,
        SURFACE_VALIDATOR_RELATIVE: SURFACE_VALIDATOR_SHA256,
        SURFACE_V17_RELATIVE: SURFACE_V17_SHA256,
        SURFACE_V17_PROTOCOL_RELATIVE: SURFACE_V17_PROTOCOL_SHA256,
        SURFACE_V18_RELATIVE: SURFACE_V18_SHA256,
        SURFACE_V18_PROTOCOL_RELATIVE: SURFACE_V18_PROTOCOL_SHA256,
        LOCALE_HARNESS_RELATIVE: LOCALE_HARNESS_SHA256,
        NESTED_V1_RELATIVE: NESTED_V1_SHA256,
        "oracle/phase2/candidate-subinterpreters-v1.json":
        NESTED_V1_DOCUMENT_SHA256,
        "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V1.md":
        NESTED_V1_PROTOCOL_SHA256,
        NESTED_V2_RELATIVE: NESTED_V2_SHA256,
        "oracle/phase2/candidate-subinterpreters-v2.json":
        NESTED_V2_DOCUMENT_SHA256,
        "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V2.md":
        NESTED_V2_PROTOCOL_SHA256,
        NESTED_V3_RELATIVE: NESTED_V3_SHA256,
        NESTED_V3_DOCUMENT_RELATIVE: NESTED_V3_DOCUMENT_SHA256,
        NESTED_V3_PROTOCOL_RELATIVE: NESTED_V3_PROTOCOL_SHA256,
    }
    for build in build_keys.values():
        require(type(build) is dict and bool(build),
                "select only genuine independently frozen source-build versions")
        fixed[build["source"]] = build["source_sha256"]
        fixed[build["protocol"]] = build["protocol_sha256"]
    for suite in FROZEN_SUITES:
        fixed[suite.source_relative] = suite.source_sha256
        if suite.recorder_relative is not None:
            require(type(suite.recorder_sha256) is str,
                    "pin the exact frozen candidate-owned recorder source")
            fixed[suite.recorder_relative] = suite.recorder_sha256
    for family in ("c", "rust"):
        fixed.update(historical_evidence_paths(family))
    own_source = getattr(options, "source_sha256", None)
    if own_source is not None:
        fixed[SOURCE_RELATIVE] = checked_digest(own_source, "V4 worker source")
    document_pin = getattr(options, "document_sha256", None)
    if document_pin is not None:
        fixed[DOCUMENT_RELATIVE] = checked_digest(document_pin, "V6 machine protocol")
    protocol_pin = getattr(options, "protocol_sha256", None)
    if protocol_pin is not None:
        fixed[PROTOCOL_RELATIVE] = checked_digest(protocol_pin, "V6 frozen prose")
    return fixed


def phase_one_row(context: Mapping[str, Any], suite: SuiteSpec) -> dict[str, Any]:
    rows = context["phase1"].get("suites")
    require(type(rows) is list and len(rows) == SUITE_COUNT,
            "retain all original frozen source-owned oracle suites")
    selected = [row for row in rows
                if type(row) is dict and row.get("id") == suite.name]
    require(len(selected) == 1,
            "reject an omitted, duplicated, or reordered frozen producer")
    row = selected[0]
    require(row.get("case_execution_count") == suite.case_count
            and row.get("matrix_sha256") == suite.matrix_sha256
            and row.get("baseline_records_sha256") == suite.reference_sha256
            and type(row.get("source")) is dict
            and row["source"].get("path") == suite.source_relative
            and row["source"].get("sha256") == suite.source_sha256,
            "reject a changed original source, denominator, matrix, or baseline")
    if suite.seed is not None and row.get("published_seed_decimal") is not None:
        require(row["published_seed_decimal"] == str(suite.seed),
                "preserve the exact full-width frozen original seed")
    return row


def phase_one_baseline_paths(row: Mapping[str, Any]) -> dict[str, str]:
    baseline = row.get("baseline")
    require(type(baseline) is dict and baseline.get("status") == "PASS",
            "use only the previously passed independent original baseline")
    owners: dict[str, str] = {}
    for key in ("compressed_report", "publication_receipt", "report"):
        item = baseline.get(key)
        if item is not None:
            require(type(item) is dict and type(item.get("path")) is str,
                    "preserve each predetermined original reference owner")
            owners[item["path"]] = checked_digest(item.get("sha256"), key)
    return owners


def validate_source_digest(module: types.ModuleType, records: Any,
                           expected: str, label: str) -> None:
    original_digest = getattr(module, "digest", None)
    require(callable(original_digest),
            "use the unchanged producer-specific canonical digest: " + label)
    require(original_digest(records) == checked_digest(expected, label),
            "reject a changed source-specific original record vector: " + label)


def archived_direct_reference(context: Mapping[str, Any], suite: SuiteSpec,
                              allowed: frozenset[str]) -> tuple[list[dict[str, Any]],
                                                               types.ModuleType]:
    row = phase_one_row(context, suite)
    baseline = row["baseline"]
    source = import_frozen(suite.source_relative, suite.source_sha256, allowed)
    if suite.name == "public_surface_v19":
        item = baseline.get("report")
        require(type(item) is dict,
                "the original plain V19 dual-reference archive is mandatory")
        raw, _ = read_owned(item["path"], item["sha256"],
                            allowed=allowed, maximum=MAX_PLAIN_BYTES)
        reference = decode_document(raw, "frozen original surface reference")
        require(reference.get("schema")
                == "rebar-python-re-cycle-safe-guarded-public-surface-v19-self-oracle"
                and reference.get("status") == "PASS"
                and reference.get("cases") == suite.case_count
                and reference.get("record_sha256") == suite.reference_sha256
                and reference.get("actual_independent_reference_count") == 2
                and reference.get("matrix_sha256") == suite.matrix_sha256,
                "authenticate both real previously published public references")
    elif suite.name == "pep688_v4":
        item = baseline.get("compressed_report")
        receipt_item = baseline.get("publication_receipt")
        require(type(item) is dict and type(receipt_item) is dict,
                "require the genuine PEP 688 archive and durable receipt")
        compressed, _ = read_owned(item["path"], item["sha256"],
                                   allowed=allowed, maximum=MAX_ARCHIVE_BYTES)
        receipt_raw, _ = read_owned(receipt_item["path"], receipt_item["sha256"],
                                    allowed=allowed, maximum=MAX_SOURCE_BYTES)
        receipt = decode_document(receipt_raw, "original PEP 688 baseline receipt")
        require(receipt.get("status") == "PASS",
                "the frozen genuine PEP 688 publication was not durable")
        plain = bounded_gzip(compressed, "original PEP 688 baseline")
        recorded = baseline.get("uncompressed_report")
        require(type(recorded) is dict and recorded.get("bytes") == len(plain)
                and recorded.get("sha256") == hashlib.sha256(plain).hexdigest(),
                "the exact complete original PEP 688 baseline was altered")
        reference = decode_document(plain, "frozen PEP 688 dual reference")
        require(reference.get("schema")
                == "rebar-python-re-pep688-buffer-exporter-v4-self-oracle"
                and reference.get("status") == "PASS"
                and reference.get("case_count") == suite.case_count
                and reference.get("actual_independent_reference_count") == 2
                and reference.get("matrix_sha256") == suite.matrix_sha256,
                "authenticate both previously recorded real PEP references")
    else:
        raise CandidateGateError("only surface and PEP use direct baseline loading")
    workers = reference.get("reference_worker_reports")
    require(type(workers) is dict and set(workers) == {"reference_a", "reference_b"},
            "retain both independently frozen original worker reports")
    first, second = workers["reference_a"], workers["reference_b"]
    require(type(first) is dict and type(second) is dict
            and type(first.get("records")) is list
            and len(first["records"]) == suite.case_count
            and first["records"] == second.get("records"),
            "both complete original reference vectors must independently agree")
    validate_source_digest(source, first["records"], suite.reference_sha256,
                           suite.name + " original producer digest")
    return first["records"], source


def authenticated_history(context: Mapping[str, Any], family: str,
                          allowed: frozenset[str]) -> dict[str, Any]:
    values = HISTORICAL_V5[family]
    paths = historical_evidence_paths(family)
    snapshots: dict[str, bytes] = {}
    owners: list[dict[str, Any]] = []
    for relative, fingerprint in paths.items():
        raw, owner = read_owned(relative, fingerprint, allowed=allowed,
                                maximum=MAX_ARCHIVE_BYTES)
        snapshots[relative] = raw
        owners.append(owner)
    prefix = "oracle/phase2/evidence/"
    outer_name = prefix + "frozen-p0-candidate-v5-" + family + "-phase2-v5-failures"
    worker_name = (prefix + "frozen-p0-candidate-worker-v3-"
                   + family + "-phase2-v5-failures")
    outer_plain = bounded_gzip(snapshots[outer_name + ".json.gz"],
                               family + " complete real V5 aggregate")
    outer = decode_document(outer_plain, family + " complete real V5 aggregate")
    outer_receipt = decode_document(
        snapshots[outer_name + "-publication-receipt.json"],
        family + " real V5 aggregate receipt", canonical_required=True,
    )
    require(outer.get("schema")
            == "rebar-frozen-python-re-p0-candidate-v5-actual-complete-candidate"
            and outer.get("status") == "FAIL"
            and outer.get("candidate_family") == family
            and outer.get("suite_count") == SUITE_COUNT
            and outer.get("case_execution_denominator") == CASE_DENOMINATOR
            and outer.get("qualified_candidate_case_executions") == 0
            and outer.get("candidate_qualified") is False
            and outer_receipt.get("status") == "PASS"
            and outer_receipt.get("candidate_status") == "FAIL"
            and outer_receipt.get("uncompressed_bytes") == len(outer_plain)
            and outer_receipt.get("uncompressed_sha256")
            == hashlib.sha256(outer_plain).hexdigest(),
            "preserve the genuine failed V5 aggregate without upgrading its zero")
    worker_plain = bounded_gzip(snapshots[worker_name + ".json.gz"],
                                family + " complete true V5 case worker")
    worker = decode_document(worker_plain, family + " complete true V5 case worker")
    receipt = decode_document(
        snapshots[worker_name + "-publication-receipt.json"],
        family + " complete true V5 case worker receipt", canonical_required=True,
    )
    rows = worker.get("all_suites")
    require(worker.get("schema")
            == "rebar-frozen-python-re-p0-candidate-worker-v3-complete-candidate-evaluation"
            and worker.get("status") == "FAIL"
            and worker.get("candidate_family") == family
            and type(rows) is list and len(rows) == SUITE_COUNT
            and worker.get("case_execution_denominator") == CASE_DENOMINATOR
            and worker.get("qualified_candidate_case_executions")
            == values["qualified_cases"]
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("uncompressed_bytes") == len(worker_plain)
            and receipt.get("uncompressed_sha256")
            == hashlib.sha256(worker_plain).hexdigest(),
            "preserve the complete failed but genuinely executed V5 worker")
    passing = [row for row in rows if row.get("status") == "PASS"]
    require(len(passing) == values["passing_suites"]
            and sum(row.get("actual_candidate_case_count", 0)
                    for row in passing) == values["qualified_cases"],
            "retain the independently witnessed 7,197 or 7,461 passing cases")
    actual_mismatches = 0
    nested_case_calls: int | str | None = None
    nested_created: int | str | None = None
    nested_destroyed: int | str | None = None
    for suite in FROZEN_SUITES:
        matches = [row for row in rows if row.get("suite") == suite.name]
        require(len(matches) == 1,
                "preserve every original V5 route and producer process")
        row = matches[0]
        process = row.get("actual_process")
        require(type(process) is dict and process.get("timed_out") is False
                and process.get("returncode") in (0, 1),
                "retain the exact original V5 producer's real exit")
        raw_stdout = restore_stream(process.get("stdout"),
                                    family + " V5 " + suite.name + " stdout")
        require(restore_stream(process.get("stderr"),
                               family + " V5 " + suite.name + " stderr") == b"",
                "never conceal an original producer's actual stderr")
        child = decode_document(raw_stdout,
                                family + " original V5 " + suite.name + " result")
        if suite.recorder_relative is not None:
            archive_path, receipt_path = specialized_evidence_paths(
                suite, family, "phase2-v5",
            )
            require(archive_path in snapshots and receipt_path in snapshots,
                    "preserve both fixed source-owned recorder outputs")
            producer_archive = decode_document(
                bounded_gzip(snapshots[archive_path],
                             family + " preserved " + suite.name),
                family + " preserved " + suite.name + " full archive",
            )
            producer_receipt = decode_document(
                snapshots[receipt_path],
                family + " preserved " + suite.name + " receipt",
                canonical_required=True,
            )
            require(producer_archive.get("candidate_family") == family
                    and producer_archive.get("case_count") == suite.case_count
                    and producer_archive.get("matrix_sha256") == suite.matrix_sha256
                    and producer_archive.get("baseline_records_sha256")
                    == suite.reference_sha256
                    and producer_archive.get("published_seed") == suite.seed
                    and producer_receipt.get("status") == "PASS"
                    and producer_receipt.get("candidate_result_status")
                    == producer_archive.get("status")
                    and producer_receipt.get("report_relative") == archive_path
                    and producer_receipt.get("receipt_relative") == receipt_path
                    and producer_receipt.get("report_sha256")
                    == values["specialized"][suite.name][0]
                    and producer_receipt.get("report_bytes")
                    == len(snapshots[archive_path])
                    and producer_receipt.get("report_uncompressed_sha256")
                    == hashlib.sha256(bounded_gzip(
                        snapshots[archive_path], family + " exact historical report",
                    )).hexdigest(),
                    "authenticate genuine route-specific V5 publication and seed")
            mismatches = producer_archive.get("all_mismatches")
            require(type(mismatches) is list
                    and producer_archive.get("mismatch_count") == len(mismatches),
                    "retain the complete previous actual mismatch ledger")
            actual_mismatches += len(mismatches)
        elif suite.name == "subinterpreter_v2":
            nested_path, nested_receipt_path = nested_evidence_paths(
                family, "phase2-v5", version="1", failure=True,
            )
            nested_compressed = snapshots[nested_path]
            nested_plain = bounded_gzip(
                nested_compressed, family + " historical full nested failure",
            )
            nested_full = decode_document(
                nested_plain, family + " complete actual nested V1 failure",
            )
            nested_receipt = decode_document(
                snapshots[nested_receipt_path],
                family + " genuine historical nested V1 receipt",
                canonical_required=True,
            )
            require(
                nested_full.get("schema")
                == "rebar-owned-candidate-subinterpreters-v1-candidate-evaluation"
                and nested_full.get("status") == "FAIL"
                and nested_full.get("candidate_family") == family
                and nested_full.get("label") == "phase2-v5-subinterpreters"
                and nested_full.get("source_sha256") == NESTED_V1_SHA256
                and nested_full.get("protocol_sha256") == NESTED_V1_DOCUMENT_SHA256
                and nested_full.get("explanation_sha256") == NESTED_V1_PROTOCOL_SHA256
                and nested_full.get("performance") == "NOT MEASURED"
                and nested_full.get("hidden_cases_read") == 0
                and nested_full.get("benchmark_files_read") == 0
                and nested_full.get("clock_samples") == 0
                and nested_receipt.get("schema")
                == "rebar-owned-candidate-subinterpreters-v1-publication-receipt"
                and nested_receipt.get("status") == "PASS"
                and nested_receipt.get("result_status") == "FAIL"
                and nested_receipt.get("family") == family
                and nested_receipt.get("label") == "phase2-v5-subinterpreters"
                and nested_receipt.get("archive_relative") == nested_path
                and nested_receipt.get("archive_sha256")
                == values["nested_archive"]
                and nested_receipt.get("archive_bytes") == len(nested_compressed)
                and nested_receipt.get("uncompressed_bytes") == len(nested_plain)
                and nested_receipt.get("uncompressed_sha256")
                == hashlib.sha256(nested_plain).hexdigest(),
                "authenticate the real failed original nested archive and receipt",
            )
            nested_worker = nested_full.get("worker")
            nested_process = nested_full.get("worker_process")
            require(nested_worker is None,
                    "neither historical family had a passing original interpreter worker")
            if nested_process is None:
                require(family == "rust",
                        "only Rust failed before starting a real interpreter worker")
                nested_case_calls = nested_created = nested_destroyed = "NOT ESTABLISHED"
            else:
                require(family == "c" and type(nested_process) is dict
                        and nested_process.get("timed_out") is False
                        and nested_process.get("returncode") == 1
                        and type(nested_process.get("pid")) is int
                        and nested_process["pid"] > 0,
                        "preserve the genuine failed C interpreter worker and PID")
                failure = nested_full.get("failure")
                require(type(failure) is dict
                        and type(failure.get("actual_failure")) is dict
                        and type(failure["actual_failure"].get("actual_failure")) is dict,
                        "retain the complete nested genuine C lifecycle failure")
                actual = failure["actual_failure"]["actual_failure"]
                require(actual.get("active_phase")
                        == "install-real-persistent-original-V5-in-A"
                        and actual.get("actual_case_interpreter_exec_calls") == 0
                        and actual.get("actual_initialization_interpreter_exec_calls") == 1
                        and actual.get("actual_guard_cleanup_interpreter_exec_calls") == 2
                        and actual.get("actual_interpreters_created") == 2
                        and actual.get("actual_interpreters_destroyed") == 2
                        and actual.get("completed_a_records") == []
                        and actual.get("completed_b_records") == []
                        and actual.get("completed_repeated_a_records") == [],
                        "derive the exact zero-case C lifecycle from its real failure")
                nested_case_calls = actual["actual_case_interpreter_exec_calls"]
                nested_created = actual["actual_interpreters_created"]
                nested_destroyed = actual["actual_interpreters_destroyed"]
        elif suite.name in {"public_surface_v19", "pep688_v4"}:
            records = child.get("candidate_records")
            reference, source = archived_direct_reference(context, suite, allowed)
            validate_source_digest(source, records,
                                   child.get("candidate_records_sha256"),
                                   family + " actual " + suite.name)
            identity = "id" if suite.name == "public_surface_v19" else "case"
            actual_mismatches += len(compare_records(
                reference, records, suite=suite.name,
                identity=identity, expected_count=suite.case_count,
            ))
    require(actual_mismatches == values["semantic_mismatches"],
            "retain every real C/Rust expected-and-actual mismatch")
    require(nested_case_calls is not None and nested_created is not None
            and nested_destroyed is not None,
            "derive original interpreter metadata from the actual archived worker")
    restoration_path = (prefix + "frozen-p0-candidate-v5-"
                        + family + "-phase2-v5-restoration-receipt.json")
    restoration = decode_document(snapshots[restoration_path],
                                  family + " original native restoration",
                                  canonical_required=True)
    require(restoration.get("status") == "PASS"
            and restoration.get("family") == family
            and restoration.get("candidate_import_root") == str(ROOT)
            and restoration.get("performance") == "NOT MEASURED",
            "retain the real exact-byte V5 native restoration receipt")
    return {
        "candidate_family": family,
        "status": "FAIL",
        "candidate_qualified": False,
        "suite_process_attempt_count": SUITE_COUNT,
        "passing_suite_count": len(passing),
        "qualified_case_count": values["qualified_cases"],
        "actual_semantic_mismatch_count": actual_mismatches,
        "original_case_denominator": CASE_DENOMINATOR,
        "preserved_artifact_count": 16,
        "separate_restoration_receipt_count": 1,
        "artifact_owners": owners,
        "actual_case_interpreter_exec_calls": nested_case_calls,
        "actual_interpreters_created": nested_created,
        "actual_interpreters_destroyed": nested_destroyed,
        "unverified_original_interpreter_cases": 128,
        "performance": "NOT MEASURED",
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
    }


def authenticate_pinned_python() -> dict[str, Any]:
    """Hash the actual isolated executable without following a replaced inode."""
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(PINNED_PYTHON, flags)
    try:
        before = os.fstat(descriptor)
        visible = os.stat(PINNED_PYTHON, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and 0 < before.st_size <= MAX_ARCHIVE_BYTES,
                "open the real pinned CPython as a bounded same-inode regular file")
        recorded = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "reject a truncated genuine pinned CPython executable")
            remaining -= len(chunk)
            recorded.update(chunk)
        require(os.read(descriptor, 1) == b"",
                "reject extra genuine pinned Python executable bytes")
        after = os.fstat(descriptor)
        final = os.stat(PINNED_PYTHON, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (after.st_dev, after.st_ino, after.st_size)
                == (final.st_dev, final.st_ino, final.st_size)
                and recorded.hexdigest() == PINNED_PYTHON_SHA256,
                "authenticate the actual full immutable pinned CPython executable")
        return {
            "path": PINNED_PYTHON, "sha256": PINNED_PYTHON_SHA256,
            "size_bytes": after.st_size, "device": after.st_dev,
            "inode": after.st_ino, "no_follow": True,
            "same_inode_verified": True,
        }
    finally:
        os.close(descriptor)


def authenticate_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    verify_runtime()
    python_owner = authenticate_pinned_python()
    fixed = fixed_source_owners(options)
    raw_p0, _ = read_owned(P0_RELATIVE, P0_SHA256, allowed=frozenset(fixed))
    phase1 = decode_document(raw_p0, "complete independently frozen phase one")
    legacy = import_frozen(V5_WORKER_RELATIVE, V5_WORKER_SHA256, frozenset(fixed))
    phase1 = legacy.validate_phase1_document(phase1)
    allowed_rows = dict(fixed)
    for suite in FROZEN_SUITES:
        selected = next(row for row in phase1["suites"] if row["id"] == suite.name)
        allowed_rows.update(phase_one_baseline_paths(selected))
    allowed = frozenset(allowed_rows)
    for relative, fingerprint in fixed.items():
        read_owned(relative, fingerprint, allowed=allowed,
                   maximum=MAX_ARCHIVE_BYTES if relative.endswith(".json.gz")
                   else MAX_SOURCE_BYTES)
    if DOCUMENT_RELATIVE in fixed:
        inventory, _ = read_owned(DOCUMENT_RELATIVE, fixed[DOCUMENT_RELATIVE],
                                  allowed=allowed)
        validate_protocol_document(decode_document(inventory,
                                                    "exact frozen V6 inventory"))
    original = import_frozen(V1_RELATIVE, V1_SHA256, allowed)
    original_inventory, verified = original.authenticate_phase1()
    require(type(original_inventory) is dict
            and canonical(original_inventory) == canonical(phase1)
            and type(verified) is dict and verified.get("status") == "PASS"
            and verified.get("suite_count") == SUITE_COUNT
            and verified.get("case_execution_denominator") == CASE_DENOMINATOR
            and verified.get("new_candidate_workers") == 0
            and verified.get("hidden_cases_read") == 0
            and verified.get("performance_files_read") == 0
            and verified.get("clock_samples") == 0,
            "reauthenticate full original phase one without starting a reference")
    nested = import_frozen(NESTED_V3_RELATIVE, NESTED_V3_SHA256, allowed)
    require(getattr(nested, "SCHEMA", None)
            == "rebar-owned-candidate-subinterpreters-v3"
            and callable(getattr(nested, "validate_actual_worker", None))
            and callable(getattr(nested, "verify_frozen_context", None)),
            "authenticate only the separately pushed genuine nested V3 owner")
    context: dict[str, Any] = {
        "phase1": phase1,
        "phase1_verification": verified,
        "pinned_python_owner": python_owner,
        "legacy_worker": legacy,
        "original_candidate_gate": original,
        "nested": nested,
        "allowed_paths": allowed,
        "fixed_source_owners": fixed,
    }
    context["preserved_v5_campaigns"] = {
        family: authenticated_history(context, family, allowed)
        for family in ("c", "rust")
    }
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "the original-only frozen context imported a native candidate")
    return context


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    for name in ("candidate", "label", "build_label", "activation_root",
                 "suite", "activation_report_sha256", "activation_receipt_sha256",
                 "recovery_journal_sha256", "candidate_source_sha256",
                 "native_engine_sha256", "native_bridge_sha256",
                 "build_archive_sha256", "build_receipt_sha256"):
        require(getattr(options, name, None) is None,
                "read-only context cannot authorize a candidate: " + name)
    require(not getattr(options, "owned_source_sha256", []),
            "read-only context cannot authorize actual candidate owners")
    require(getattr(options, "build_version", None) is None,
            "read-only context cannot choose an actual native build")
    with frozen_context_boundary() as effects:
        context = authenticate_frozen_context(options)
        summaries = context["preserved_v5_campaigns"]
        require(set(summaries) == {"c", "rust"}
                and summaries["c"]["qualified_case_count"] == 7197
                and summaries["rust"]["qualified_case_count"] == 7461
                and summaries["c"]["actual_semantic_mismatch_count"] == 2094
                and summaries["rust"]["actual_semantic_mismatch_count"] == 2042,
                "preserve both actual failed-but-partially-passing campaigns")
    for field in ("file_writes", "candidate_imports", "reference_workers",
                  "candidate_workers", "source_builds", "native_promotions",
                  "native_libraries_loaded", "interpreter_creations", "thread_starts",
                  "clock_samples", "network_requests", "hidden_cases_read",
                  "benchmark_files_read"):
        require(effects[field] == 0,
                "a read-only correctness context attempted a real effect: " + field)
    return {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS",
        "read_only": True,
        "goal_sha256": GOAL_SHA256,
        "phase1_inventory_sha256": P0_SHA256,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "original_public_record_count": 152,
        "runnable_original_public_case_count": 151,
        "genuine_original_debug_skip_count": 1,
        "named_private_waiver_count": 13,
        "corrected_nested_v3_source_sha256": NESTED_V3_SHA256,
        "preserved_actual_campaigns": summaries,
        "preserved_historical_artifact_count": 32,
        "preserved_historical_restoration_receipt_count": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_promotions": 0,
        "actual_interpreters_created": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
        "read_only_effects": effects,
    }


def authenticate_canonical_activation(
    options: argparse.Namespace, context: Mapping[str, Any],
) -> dict[str, Any]:
    """Require the actual V2 activation and its genuine durable intentions."""
    family = checked_family(options.candidate)
    version = str(options.build_version)
    require(FAMILY_BUILD_VERSION[family] == version,
            "C and Rust require build V2; independently built Zig requires V3")
    build = BUILD_VERSIONS[version]
    require(options.activation_source_sha256 == ACTIVATION_SHA256
            and options.activation_protocol_sha256 == ACTIVATION_PROTOCOL_SHA256
            and options.build_source_sha256 == build["source_sha256"]
            and options.build_protocol_sha256 == build["protocol_sha256"],
            "pin the genuine corrected activator and family-specific native build")
    allowed = context["allowed_paths"]
    activation = import_frozen(ACTIVATION_RELATIVE, ACTIVATION_SHA256, allowed)
    root = activation.checked_private_root(
        options.activation_root, family, build=False,
    )
    report_raw, report_owner = activation.read_owned(
        root, activation.REPORT_NAME, options.activation_report_sha256,
        maximum=MAX_SOURCE_BYTES, private=True,
    )
    receipt_raw, receipt_owner = activation.read_owned(
        root, activation.RECEIPT_NAME, options.activation_receipt_sha256,
        maximum=MAX_SOURCE_BYTES, private=True,
    )
    report = activation.decode_document(report_raw, "complete V2 activation")
    receipt = activation.decode_document(receipt_raw, "complete V2 activation receipt")
    journal_claim = report.get("recovery_journal")
    require(type(journal_claim) is dict,
            "retain the exact original source-verified native recovery journal")
    journal_pin = checked_digest(journal_claim.get("sha256"), "V2 recovery journal")
    if options.recovery_journal_sha256 is not None:
        require(options.recovery_journal_sha256 == journal_pin,
                "never substitute a caller-pinned native recovery journal")
    journal_raw, journal_owner = activation.read_owned(
        root, activation.JOURNAL_NAME, journal_pin,
        maximum=MAX_SOURCE_BYTES, private=True,
    )
    journal = activation.decode_document(journal_raw, "complete V2 recovery journal")
    arguments = {
        "family": family, "build_version": version,
        "activation_root": root,
        "activation_source_sha256": ACTIVATION_SHA256,
        "activation_protocol_sha256": ACTIVATION_PROTOCOL_SHA256,
        "activation_report_sha256": options.activation_report_sha256,
        "activation_receipt_sha256": options.activation_receipt_sha256,
    }
    proved = activation.validate_activation_documents(
        report, receipt, journal, arguments=arguments,
    )
    provenance = proved["source_build"]
    require(provenance.get("schema") == build["schema"]
            and provenance.get("build_version") == version
            and provenance.get("family") == family
            and provenance.get("label") == checked_label(options.build_label)
            and provenance.get("source_sha256") == build["source_sha256"]
            and provenance.get("protocol_sha256") == build["protocol_sha256"]
            and provenance.get("archive_sha256") == options.build_archive_sha256
            and provenance.get("receipt_sha256") == options.build_receipt_sha256
            and provenance.get("independent_fresh_phase_count") == 2,
            "require both actual independent source-to-native build phases")
    intents = activation.authenticate_promotion_intents(
        root, journal, journal_pin,
        announced_targets=proved["canonical_targets"],
    )
    target_roles = activation.FAMILIES[family]["binaries"]
    require(set(intents) == set(target_roles),
            "authenticate an actual durable original promotion intent per native role")
    targets = proved["canonical_targets"]
    for role, filename in target_roles.items():
        selected = activation.current_canonical("candidates/" + filename)
        require(selected is not None
                and activation.same_owner(selected[1], targets[role])
                and activation.same_owner(selected[1], intents[role]["target"]),
                "the actually proved canonical native owner changed: " + role)
    original = context["original_candidate_gate"]
    spec = original.family_spec(family)
    pins = original.validate_owners(
        spec, adapter=options.candidate_source_sha256,
        engine=options.native_engine_sha256,
        bridge=options.native_bridge_sha256,
        source_entries=options.owned_source_sha256,
    )
    require(pins == {
        "source": options.candidate_source_sha256,
        "native_engine": options.native_engine_sha256,
        "native_bridge": options.native_bridge_sha256,
    }, "use the unchanged original independent candidate and native matcher guard")
    native_roles = ("extension", "extension") if family == "c" else ("engine", "bridge")
    require(all(role in targets for role in native_roles),
            "retain the actual independently promoted engine and bridge owners")
    return {
        "family": family, "build_version": version,
        "pins": pins, "source_build": provenance,
        "canonical_activation": proved, "promotion_intents": intents,
        "activation_report_owner": report_owner,
        "activation_receipt_owner": receipt_owner,
        "recovery_journal_owner": journal_owner,
        "native_engine_bytes": targets[native_roles[0]]["size_bytes"],
        "native_bridge_bytes": targets[native_roles[1]]["size_bytes"],
    }


def nested_arguments(options: argparse.Namespace,
                     approval: Mapping[str, Any]) -> list[str]:
    family = checked_family(options.candidate)
    build = BUILD_VERSIONS[str(options.build_version)]
    pairs: tuple[tuple[str, Any], ...] = (
        ("--family", family),
        ("--build-version", str(options.build_version)),
        ("--label", checked_label(options.label + "-subinterpreters")),
        ("--candidate-source-sha256", options.candidate_source_sha256),
        ("--source-sha256", NESTED_V3_SHA256),
        ("--protocol-sha256", NESTED_V3_DOCUMENT_SHA256),
        ("--explanation-sha256", NESTED_V3_PROTOCOL_SHA256),
        ("--v1-source-sha256", NESTED_V1_SHA256),
        ("--v1-protocol-sha256", NESTED_V1_DOCUMENT_SHA256),
        ("--v1-explanation-sha256", NESTED_V1_PROTOCOL_SHA256),
        ("--v2-source-sha256", NESTED_V2_SHA256),
        ("--v2-protocol-sha256", NESTED_V2_DOCUMENT_SHA256),
        ("--v2-explanation-sha256", NESTED_V2_PROTOCOL_SHA256),
        ("--build-label", checked_label(options.build_label)),
        ("--build-source-sha256", build["source_sha256"]),
        ("--build-protocol-sha256", build["protocol_sha256"]),
        ("--build-archive-sha256", options.build_archive_sha256),
        ("--build-receipt-sha256", options.build_receipt_sha256),
        ("--activation-root", options.activation_root),
        ("--activation-source-sha256", ACTIVATION_SHA256),
        ("--activation-protocol-sha256", ACTIVATION_PROTOCOL_SHA256),
        ("--activation-report-sha256", options.activation_report_sha256),
        ("--activation-receipt-sha256", options.activation_receipt_sha256),
        ("--native-engine-sha256", options.native_engine_sha256),
        ("--native-bridge-sha256", options.native_bridge_sha256),
        ("--native-engine-bytes", approval["native_engine_bytes"]),
        ("--native-bridge-bytes", approval["native_bridge_bytes"]),
    )
    result: list[str] = ["--record-candidate"]
    for option, value in pairs:
        require(type(value) in {str, int} and type(value) is not bool,
                "bind every exact real original nested V3 argument")
        result.extend((option, str(value)))
    for owner in options.owned_source_sha256:
        result.extend(("--owned-source-sha256", owner))
    return result


def frozen_owner_arguments(options: argparse.Namespace) -> list[str]:
    required: tuple[tuple[str, Any], ...] = (
        ("--candidate", options.candidate),
        ("--label", options.label),
        ("--build-version", options.build_version),
        ("--build-label", options.build_label),
        ("--source-sha256", options.source_sha256),
        ("--protocol-sha256", options.protocol_sha256),
        ("--document-sha256", options.document_sha256),
        ("--build-source-sha256", options.build_source_sha256),
        ("--build-protocol-sha256", options.build_protocol_sha256),
        ("--build-archive-sha256", options.build_archive_sha256),
        ("--build-receipt-sha256", options.build_receipt_sha256),
        ("--activation-root", options.activation_root),
        ("--activation-source-sha256", options.activation_source_sha256),
        ("--activation-protocol-sha256", options.activation_protocol_sha256),
        ("--activation-report-sha256", options.activation_report_sha256),
        ("--activation-receipt-sha256", options.activation_receipt_sha256),
        ("--candidate-source-sha256", options.candidate_source_sha256),
        ("--native-engine-sha256", options.native_engine_sha256),
        ("--native-bridge-sha256", options.native_bridge_sha256),
    )
    result: list[str] = []
    for name, value in required:
        require(type(value) is str and bool(value),
                "pin every source, V2 activation, and native build authorization")
        result.extend((name, value))
    if options.recovery_journal_sha256 is not None:
        result.extend(("--recovery-journal-sha256", options.recovery_journal_sha256))
    for owner in options.owned_source_sha256:
        result.extend(("--owned-source-sha256", owner))
    return result


def producer_command(suite: SuiteSpec, options: argparse.Namespace,
                     context: Mapping[str, Any],
                     approval: Mapping[str, Any]) -> list[str]:
    executable = [PINNED_PYTHON, "-I", "-B"]
    if suite.name == "subinterpreter_v2":
        return [*executable, str(ROOT / NESTED_V3_RELATIVE),
                *nested_arguments(options, approval)]
    if suite.name in {"public_surface_v19", "pep688_v4", "threaded_pattern_v1"}:
        return [*executable, str(ROOT / SOURCE_RELATIVE),
                "--internal-candidate-worker", "--suite", suite.name,
                *frozen_owner_arguments(options)]
    legacy = context["legacy_worker"]
    legacy_suite = legacy.suite_spec(suite.name)
    row = phase_one_row(context, suite)
    return legacy.producer_command(legacy_suite, options, row)


def encoded_process(command: Sequence[str]) -> dict[str, Any]:
    require(type(command) in {list, tuple}
            and list(command[:3]) == [PINNED_PYTHON, "-I", "-B"]
            and all(type(part) is str for part in command),
            "invoke only one exact isolated frozen candidate-owned producer")
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
        "LC_ALL": "C", "PATH": "/usr/bin:/bin",
    }
    process = subprocess.Popen(
        list(command), shell=False, cwd=str(ROOT), stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
    )
    try:
        stdout, stderr = process.communicate(timeout=TIMEOUT_SECONDS)
        return {
            "status": "OBSERVED", "timed_out": False, "pid": process.pid,
            "returncode": process.returncode,
            "signal": -process.returncode if process.returncode < 0 else None,
            "stdout": capture_stream(stdout), "stderr": capture_stream(stderr),
        }
    except subprocess.TimeoutExpired as error:
        process.kill()
        stdout, stderr = process.communicate()
        return {
            "status": "FAIL", "timed_out": True, "pid": process.pid,
            "returncode": process.returncode,
            "timeout_type": type(error).__name__,
            "stdout": capture_stream(stdout), "stderr": capture_stream(stderr),
        }


def source_owned_publication(value: Any, relative: str,
                             *, compressed: bool,
                             allowed: frozenset[str]) -> tuple[bytes, dict[str, Any]]:
    require(type(value) is dict,
            "require a source-owned exact durable publication: " + relative)
    actual_relative = value.get("path", value.get("relative"))
    size = value.get("bytes", value.get("size_bytes"))
    require(actual_relative == relative and type(size) is int and size > 0,
            "reject a child-selected, substituted, or truncated evidence path")
    if "actual_write_calls" in value:
        expected_fields = {
            "path", "sha256", "bytes", "uncompressed_bytes",
            "uncompressed_sha256", "compression",
            "actual_write_calls", "atomic_no_overwrite_link",
            "complete_readback_verified", "directory_fsync_completed",
            "file_fsync_completed", "owned_temporary_removed",
        }
        require(set(value) == expected_fields
                and type(value["actual_write_calls"]) is int
                and value["actual_write_calls"] > 0
                and all(value[name] is True for name in (
                    "atomic_no_overwrite_link", "complete_readback_verified",
                    "directory_fsync_completed", "file_fsync_completed",
                    "owned_temporary_removed",
                ))
                and value.get("compression")
                == ("gzip-mtime-zero-level-9" if compressed else "none"),
                "authenticate the exact original recorder durable-owner schema")
    else:
        require(value.get("exclusive_creation") is True
                and value.get("file_fsync_completed") is True
                and value.get("same_inode_readback_verified") is True,
                "authenticate original nested exclusive same-inode publication")
    raw, owner = read_owned(
        relative, checked_digest(value.get("sha256"), relative),
        allowed=allowed,
        maximum=MAX_ARCHIVE_BYTES if compressed else MAX_SOURCE_BYTES,
    )
    require(len(raw) == size,
            "authenticate the exact published complete source-owner byte count")
    if "uncompressed_sha256" in value:
        plain = (bounded_gzip(raw, relative + " complete owner stream")
                 if compressed else raw)
        require(type(value.get("uncompressed_bytes")) is int
                and value["uncompressed_bytes"] == len(plain)
                and checked_digest(value.get("uncompressed_sha256"),
                                   relative + " complete decoded owner")
                == hashlib.sha256(plain).hexdigest(),
                "bind the durable original owner to all exact uncompressed bytes")
    return raw, {**owner, "bytes": len(raw)}


def authenticate_specialized_baseline(
    suite: SuiteSpec, options: argparse.Namespace,
    context: Mapping[str, Any], recorder: types.ModuleType,
    source: types.ModuleType,
) -> tuple[list[dict[str, Any]], Any, list[dict[str, Any]]]:
    row = phase_one_row(context, suite)
    base = row["baseline"]
    archive = base["compressed_report"]
    receipt_item = base["publication_receipt"]
    allowed = context["allowed_paths"]
    receipt_raw, _ = read_owned(
        receipt_item["path"], receipt_item["sha256"],
        allowed=allowed, maximum=MAX_SOURCE_BYTES,
    )
    archive_raw, _ = read_owned(
        archive["path"], archive["sha256"],
        allowed=allowed, maximum=MAX_ARCHIVE_BYTES,
    )
    plain = bounded_gzip(archive_raw, suite.name + " complete original baseline")
    uncompressed = base.get("uncompressed_report")
    require(type(uncompressed) is dict
            and uncompressed.get("bytes") == len(plain)
            and uncompressed.get("sha256") == hashlib.sha256(plain).hexdigest(),
            "authenticate the exact complete lossless original reference archive")
    baseline = decode_document(plain, suite.name + " complete original baseline")
    receipt = decode_document(receipt_raw, suite.name + " original baseline receipt")
    matrix = recorder.validate_matrix(recorder.build_frozen_matrix())
    if type(matrix) is str:
        matrix = recorder.build_frozen_matrix()
    require(type(matrix) is list and len(matrix) == suite.case_count,
            "preserve every source-ordered original recorder matrix case")
    if suite.name == "managed_v1":
        pins = recorder.make_owner_pins(
            options.candidate, suite.recorder_sha256,
            options.candidate_source_sha256, options.native_engine_sha256,
            options.native_bridge_sha256, options.owned_source_sha256,
        )
        checked_receipt = recorder.validate_baseline_receipt(receipt)
        selected = {
            field: baseline[field] for field in recorder.BASELINE_SELECTED_FIELDS
        }
        proved = recorder.validate_baseline_archive(
            selected, matrix, checked_receipt, source,
        )
        expected = proved["reference_a_records"]
    else:
        base_pins = recorder.make_baseline_pins(
            suite.baseline_label, receipt_item["sha256"],
            archive["sha256"], suite.reference_sha256,
        )
        pins = recorder.make_owner_pins(
            options.candidate, suite.recorder_sha256,
            options.candidate_source_sha256, options.native_engine_sha256,
            options.native_bridge_sha256, options.owned_source_sha256,
            base_pins,
        )
        checked_receipt = recorder.validate_baseline_receipt(receipt, pins)
        proved = recorder.validate_archived_baseline(
            baseline, pins, source, matrix, checked_receipt,
        )
        if suite.name == "shape_v2":
            derived = recorder.reconstruct_baseline_result(
                proved, source, matrix,
            )
            expected = derived["reference_a"]["records"]
        else:
            expected = proved["reference_a_records"]
    require(type(expected) is list and len(expected) == suite.case_count,
            "reconstruct every original signed reference, never descriptor text")
    validate_source_digest(recorder, expected, suite.reference_sha256,
                           suite.name + " reconstructed baseline")
    return expected, pins, matrix


def validate_mismatch_ledger(
    suite: SuiteSpec, recorder: types.ModuleType,
    expected: Sequence[dict[str, Any]], actual: Sequence[dict[str, Any]],
    ledger: Any,
) -> list[dict[str, Any]]:
    differences = compare_records(
        list(expected), list(actual), suite=suite.name,
        identity="case", expected_count=suite.case_count,
    )
    require(type(ledger) is list and len(ledger) == len(differences),
            "never omit, duplicate, or invent an original actual mismatch")
    for difference, retained in zip(differences, ledger, strict=True):
        require(type(retained) is dict
                and retained.get("case") == difference["case"],
                "preserve the exact source-ordered failed original case identity")
        baseline_outcome = difference["expected_record"]["outcome"]
        candidate_outcome = difference["actual_record"]["outcome"]
        if suite.name in {"public_types_v1", "substitution_v2"}:
            require(retained.get("baseline_outcome_sha256")
                    == recorder.digest(baseline_outcome)
                    and retained.get("candidate_outcome_sha256")
                    == recorder.digest(candidate_outcome),
                    "decode the real full outcomes behind every hashed mismatch")
        else:
            require(retained.get("baseline_outcome") == baseline_outcome
                    and retained.get("candidate_outcome") == candidate_outcome,
                    "preserve every actual expected and actual mismatch outcome")
        difference["source_owned_ledger_record"] = retained
    return differences


def archived_record_vector(
    context: Mapping[str, Any], suite: SuiteSpec,
) -> tuple[list[dict[str, Any]], types.ModuleType]:
    """Recover both independently agreed archived category/thread vectors."""
    row = phase_one_row(context, suite)
    baseline = row["baseline"]
    archive = baseline.get("compressed_report")
    receipt_item = baseline.get("publication_receipt")
    require(type(archive) is dict and type(receipt_item) is dict,
            "require both genuine frozen original archive and durable receipt")
    allowed = context["allowed_paths"]
    compressed, _ = read_owned(
        archive["path"], archive["sha256"],
        allowed=allowed, maximum=MAX_ARCHIVE_BYTES,
    )
    receipt_raw, _ = read_owned(
        receipt_item["path"], receipt_item["sha256"],
        allowed=allowed, maximum=MAX_SOURCE_BYTES,
    )
    receipt = decode_document(receipt_raw, suite.name + " original archive receipt")
    require(receipt.get("status") == "PASS",
            "only an actual original durably passed reference can be compared")
    plain = bounded_gzip(compressed, suite.name + " full reference vectors")
    size = baseline.get("uncompressed_report")
    require(type(size) is dict and size.get("bytes") == len(plain)
            and size.get("sha256") == hashlib.sha256(plain).hexdigest(),
            "pin every exact genuine archived original reference byte")
    report = decode_document(plain, suite.name + " complete original references")
    require(report.get("status") == "PASS"
            and report.get("case_count") == suite.case_count
            and report.get("matrix_sha256") == suite.matrix_sha256,
            "preserve the complete exact original source-owned baseline")
    if suite.name == "threaded_pattern_v1":
        roles = report.get("reference_roles")
        require(type(roles) is dict
                and set(roles) == {"reference_a", "reference_b"}
                and report.get("actual_independent_reference_count") == 2
                and report.get("reference_records_sha256")
                == suite.reference_sha256
                and report.get("reference_warning_records_sha256")
                == THREAD_WARNING_SHA256,
                "preserve both real threaded reference processes and warnings")
        first, second = roles["reference_a"], roles["reference_b"]
        require(type(first) is dict and type(second) is dict
                and first.get("status") == second.get("status") == "PASS"
                and type(first.get("report")) is dict
                and type(second.get("report")) is dict,
                "authenticate both complete actual source-owned threaded roles")
        first, second = first["report"], second["report"]
    else:
        roles = report.get("reference_workers")
        require(type(roles) is dict
                and set(roles) == {"reference_a", "reference_b"}
                and report.get("actual_reference_workers") == 2
                and report.get("frozen_baseline_records_sha256")
                == suite.reference_sha256,
                "preserve both independent common-contract reference workers")
        first, second = roles["reference_a"], roles["reference_b"]
    require(type(first) is dict and type(second) is dict
            and type(first.get("records")) is list
            and first["records"] == second.get("records")
            and len(first["records"]) == suite.case_count
            and first.get("records_sha256") == suite.reference_sha256
            and second.get("records_sha256") == suite.reference_sha256,
            "both real frozen original workers must agree on every full outcome")
    source = import_frozen(suite.source_relative, suite.source_sha256, allowed)
    validate_source_digest(source, first["records"], suite.reference_sha256,
                           suite.name + " exact source-owned reference digest")
    return first["records"], source


def validate_category_result(
    value: Any, suite: SuiteSpec, options: argparse.Namespace,
    context: Mapping[str, Any], producer_exit: int,
) -> dict[str, Any]:
    category = {"public_v3": "public", "scanner_v3": "scanner",
                "buffer_v3": "buffer"}[suite.name]
    require(type(value) is dict and value.get("status") == "OBSERVED"
            and value.get("category") == category
            and value.get("role") == "candidate-" + options.candidate
            and value.get("candidate_family") == options.candidate
            and value.get("controller_source_sha256") == CORE_SHA256
            and value.get("category_source_sha256") == suite.source_sha256
            and value.get("matrix_sha256") == suite.matrix_sha256
            and value.get("frozen_baseline_records_sha256")
            == suite.reference_sha256
            and value.get("case_count") == suite.case_count
            and type(value.get("records")) is list
            and len(value["records"]) == suite.case_count
            and value.get("actual_candidate_workers") == 1
            and value.get("clock_samples") == 0
            and value.get("hidden_cases_read") == 0
            and producer_exit == 0,
            "preserve every complete genuine common-contract candidate result")
    expected, source = archived_record_vector(context, suite)
    candidate_pin = checked_digest(value.get("records_sha256"),
                                   suite.name + " exact actual outcome vector")
    validate_source_digest(source, value["records"], candidate_pin,
                           suite.name + " exact original category codec")
    identity = next(
        (field for field in ("case", "case_id", "id")
         if type(expected[0].get(field)) is str),
        None,
    )
    require(type(identity) is str,
            "retain the real source-owned common-contract case identity")
    differences = compare_records(
        expected, value["records"], suite=suite.name,
        identity=identity, expected_count=suite.case_count,
    )
    return {
        "actual_candidate_case_count": suite.case_count,
        "actual_candidate_workers": 1,
        "candidate_records_sha256": candidate_pin,
        "native_provenance": value.get("native_provenance"),
        "matcher_guard": value.get("matcher_guard"),
        "mismatch_count": len(differences),
        "all_mismatches": differences,
        "all_failure_reasons": [],
    }


def validate_specialized_result(
    value: Any, suite: SuiteSpec, options: argparse.Namespace,
    context: Mapping[str, Any], producer_exit: int,
) -> dict[str, Any]:
    require(suite.recorder_relative is not None
            and suite.recorder_sha256 is not None,
            "use only the independently frozen original specialized recorder")
    archive_path, receipt_path = specialized_evidence_paths(
        suite, options.candidate, options.label,
    )
    allowed = frozenset({*context["allowed_paths"], archive_path, receipt_path})
    require(type(value) is dict
            and value.get("candidate_family") == options.candidate
            and value.get("publication_status") == "PASS"
            and value.get("matrix_sha256") == suite.matrix_sha256
            and value.get("baseline_records_sha256") == suite.reference_sha256
            and value.get("validated_baseline_record_count") == suite.case_count
            and value.get("validated_candidate_record_count") == suite.case_count
            and value.get("actual_candidate_process_invocations") == 1
            and value.get("clock_samples") == 0
            and value.get("timing_trials_run") == 0
            and value.get("benchmark_files_read") == 0
            and value.get("hidden_cases_read") == 0
            and value.get("performance") == "NOT MEASURED"
            and value.get("candidate_qualified_for_hidden_benchmark") is False
            and value.get("final_winner_selected") is False,
            "authenticate the complete actual source-owned recorder result")
    compressed, archive_owner = source_owned_publication(
        value.get("report_publication"), archive_path,
        compressed=True, allowed=allowed,
    )
    receipt_raw, receipt_owner = source_owned_publication(
        value.get("receipt_publication"), receipt_path,
        compressed=False, allowed=allowed,
    )
    plain = bounded_gzip(compressed, suite.name + " complete actual recorder archive")
    full = decode_document(plain, suite.name + " complete actual recorder report")
    receipt = decode_document(
        receipt_raw, suite.name + " actual durable publication receipt",
        canonical_required=True,
    )
    recorder = import_frozen(
        suite.recorder_relative, suite.recorder_sha256,
        context["allowed_paths"],
    )
    source = import_frozen(
        suite.source_relative, suite.source_sha256,
        context["allowed_paths"],
    )
    require(full.get("schema") == recorder.SCHEMA + "-complete-candidate-report"
            and full.get("candidate_family") == options.candidate
            and full.get("case_count") == suite.case_count
            and full.get("matrix_sha256") == suite.matrix_sha256
            and full.get("baseline_records_sha256") == suite.reference_sha256
            and full.get("published_seed") == suite.seed
            and full.get("status") in {"PASS", "FAIL"}
            and full.get("status") == value.get("status")
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_result_status") == full["status"]
            and receipt.get("report_relative") == archive_path
            and receipt.get("report_sha256") == archive_owner["sha256"]
            and receipt.get("report_bytes") == len(compressed)
            and receipt.get("report_uncompressed_sha256")
            == hashlib.sha256(plain).hexdigest()
            and receipt.get("report_uncompressed_bytes") == len(plain)
            and receipt.get("receipt_relative") == receipt_path,
            "a PASS publication receipt must never be mistaken for a passing candidate")
    expected, pins, matrix = authenticate_specialized_baseline(
        suite, options, context, recorder, source,
    )
    child_stdout = restore_stream(
        full.get("complete_candidate_process_stdout"),
        suite.name + " complete actual candidate worker",
    )
    require(restore_stream(
        full.get("complete_candidate_process_stderr"),
        suite.name + " complete actual candidate worker stderr",
    ) == b"", "never conceal original actual candidate stderr")
    child = decode_document(child_stdout, suite.name + " exact actual worker")
    actual_pid = full.get("actual_candidate_pid")
    if suite.name == "managed_v1":
        exact = recorder.validate_worker(
            child, pins, matrix, expected_pid=actual_pid, managed=source,
        )
    elif suite.name == "public_types_v1":
        exact = recorder.validate_candidate_worker(
            child, manifest=full["audit_manifest"],
            source_pin=suite.source_sha256, matrix=matrix,
            expected_pid=actual_pid,
        )
    else:
        audit = import_frozen(AUDIT_RELATIVE, AUDIT_SHA256,
                              context["allowed_paths"])
        exact = recorder.validate_candidate_worker(
            child, pins, matrix, expected_pid=actual_pid,
            oracle=source, audit=audit,
        )
    original_archive = phase_one_row(
        context, suite,
    )["baseline"]["compressed_report"]
    require(type(exact) is dict and exact == child
            and full.get("baseline_archive_relative") == original_archive["path"]
            and full.get("baseline_archive_sha256") == original_archive["sha256"],
            "bind every complete recorder report to the original reference owner")
    if suite.name != "public_types_v1":
        require(child.get("baseline_archive_relative") == original_archive["path"]
                and child.get("baseline_archive_sha256")
                == original_archive["sha256"],
                "bind the source-owned child to its real original archive")
    observed = child.get("records")
    require(type(observed) is list and len(observed) == suite.case_count,
            "reconstruct every actual candidate outcome from genuine child stdout")
    candidate_pin = checked_digest(
        full.get("candidate_records_sha256"), suite.name + " actual outcomes",
    )
    require(child.get("records_sha256") == candidate_pin,
            "the actual child output and complete source report disagree")
    validate_source_digest(recorder, observed, candidate_pin,
                           suite.name + " actual complete candidate outcomes")
    mismatches = validate_mismatch_ledger(
        suite, recorder, expected, observed, full.get("all_mismatches"),
    )
    require(full.get("mismatch_count") == len(mismatches)
            and value.get("mismatch_count") == len(mismatches)
            and full.get("all_mismatches_preserved") is True
            and (full["status"] == "PASS") is (len(mismatches) == 0)
            and producer_exit == (0 if not mismatches else 1),
            "keep each exact real mismatch even when the original producer exits one")
    if "mismatch_evidence_sha256" in full:
        require(recorder.digest(full["all_mismatches"])
                == full["mismatch_evidence_sha256"],
                "verify the original complete source-owned hashed mismatch ledger")
    return {
        "actual_candidate_case_count": suite.case_count,
        "actual_candidate_workers": 1,
        "candidate_records_sha256": candidate_pin,
        "candidate_records_location": archive_owner,
        "candidate_publication_receipt": receipt_owner,
        "mismatch_count": len(mismatches),
        "all_mismatches": mismatches,
        "all_failure_reasons": full.get("all_failure_reasons", []),
        "source_owned_candidate_status": full["status"],
        "source_owned_publication_status": "PASS",
    }


def validate_direct_result(
    value: Any, suite: SuiteSpec, options: argparse.Namespace,
    context: Mapping[str, Any], producer_exit: int,
) -> dict[str, Any]:
    require(type(value) is dict and value.get("status") == "OBSERVED"
            and value.get("suite") == suite.name
            and value.get("candidate_family") == options.candidate
            and value.get("matrix_sha256") == suite.matrix_sha256
            and value.get("actual_candidate_cases") == suite.case_count
            and type(value.get("candidate_records")) is list
            and len(value["candidate_records"]) == suite.case_count
            and value.get("reference_records_sha256") == suite.reference_sha256
            and value.get("actual_candidate_workers") == 1
            and value.get("clock_samples") == 0
            and value.get("benchmark_files_read") == 0
            and value.get("hidden_cases_read") == 0
            and producer_exit == 0,
            "observe every actual direct source-owned candidate result")
    source = import_frozen(
        suite.source_relative, suite.source_sha256,
        context["allowed_paths"],
    )
    candidate_pin = checked_digest(
        value.get("candidate_records_sha256"), suite.name + " actual records",
    )
    validate_source_digest(source, value["candidate_records"], candidate_pin,
                           suite.name + " source-specific candidate codec")
    metadata = value.get("resource_evidence")
    if suite.name == "threaded_pattern_v1":
        context["legacy_worker"].validate_thread_evidence(metadata)
        expected, _ = archived_record_vector(context, suite)
        mismatches: list[dict[str, Any]] = compare_records(
            expected, value["candidate_records"], suite=suite.name,
            identity="case_id", expected_count=suite.case_count,
        )
    else:
        expected, _ = archived_direct_reference(
            context, suite, context["allowed_paths"],
        )
        identity = "id" if suite.name == "public_surface_v19" else "case"
        mismatches = compare_records(
            expected, value["candidate_records"], suite=suite.name,
            identity=identity, expected_count=suite.case_count,
        )
        if suite.name == "public_surface_v19":
            require(type(metadata) is dict
                    and metadata.get("real_locale_case_count") == 64
                    and metadata.get("real_locale_transition_count") == 192
                    and metadata.get("used_original_v17_evaluator") is True
                    and metadata.get("used_original_v19_cycle_safe_normalizer")
                    is True,
                    "run all 64 real source-owned cases and 192 locale transitions")
    return {
        "actual_candidate_case_count": suite.case_count,
        "actual_candidate_workers": 1,
        "candidate_records_sha256": candidate_pin,
        "native_provenance": value.get("native_provenance"),
        "matcher_guard": value.get("matcher_guard"),
        "resource_evidence": metadata,
        "mismatch_count": len(mismatches),
        "all_mismatches": mismatches,
        "all_failure_reasons": [],
    }


def validate_nested_result(
    value: Any, suite: SuiteSpec, options: argparse.Namespace,
    context: Mapping[str, Any], approval: Mapping[str, Any],
    producer_exit: int,
) -> dict[str, Any]:
    require(type(value) is dict
            and value.get("schema")
            == "rebar-owned-candidate-subinterpreters-v3-published-candidate-result"
            and value.get("candidate_family") == options.candidate
            and value.get("build_version") == str(options.build_version)
            and value.get("label") == options.label + "-subinterpreters"
            and value.get("status") in {"PASS", "FAIL"}
            and value.get("failure_preserved") is (value["status"] == "FAIL")
            and value.get("directory_fsync_completed") is True
            and value.get("phase1_case_execution_denominator") == CASE_DENOMINATOR
            and value.get("supplemental_cases_added_to_phase1_denominator") is False
            and value.get("performance") == "NOT MEASURED"
            and value.get("holdout") == "NOT OPENED"
            and producer_exit == (0 if value["status"] == "PASS" else 1),
            "preserve an actual corrected V3 nested failure without qualifying it")
    archive_path, receipt_path = nested_evidence_paths(
        options.candidate, options.label, version="3",
        failure=value["status"] == "FAIL",
    )
    allowed = frozenset({*context["allowed_paths"], archive_path, receipt_path})
    compressed, archive_owner = source_owned_publication(
        value.get("archive"), archive_path, compressed=True, allowed=allowed,
    )
    receipt_raw, receipt_owner = source_owned_publication(
        value.get("receipt"), receipt_path, compressed=False, allowed=allowed,
    )
    nested_bound = getattr(context["nested"], "MAX_REPORT_BYTES", None)
    require(type(nested_bound) is int and 0 < nested_bound <= MAX_PLAIN_BYTES,
            "retain the original independently frozen V3 inbound report bound")
    plain = bounded_gzip(compressed, "complete real nested V3 archive",
                         maximum=nested_bound)
    full = decode_document(plain, "complete corrected original nested V3 result",
                           maximum=nested_bound)
    receipt = decode_document(receipt_raw, "real nested V3 durable receipt",
                              canonical_required=True)
    require(full.get("schema")
            == "rebar-owned-candidate-subinterpreters-v3-candidate-evaluation"
            and full.get("status") == value["status"]
            and full.get("candidate_family") == options.candidate
            and full.get("build_version") == str(options.build_version)
            and full.get("label") == options.label + "-subinterpreters"
            and full.get("source_sha256") == NESTED_V3_SHA256
            and full.get("protocol_sha256") == NESTED_V3_DOCUMENT_SHA256
            and full.get("explanation_sha256") == NESTED_V3_PROTOCOL_SHA256
            and receipt.get("schema")
            == "rebar-owned-candidate-subinterpreters-v3-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("result_status") == full["status"]
            and receipt.get("candidate_family") == options.candidate
            and receipt.get("build_version") == str(options.build_version)
            and receipt.get("archive_relative") == archive_path
            and receipt.get("archive_sha256") == archive_owner["sha256"]
            and receipt.get("archive_bytes") == len(compressed)
            and receipt.get("uncompressed_bytes") == len(plain)
            and receipt.get("uncompressed_sha256")
            == hashlib.sha256(plain).hexdigest()
            and receipt.get("supplemental_cases_added_to_phase1_denominator")
            is False,
            "bind the genuine nested result to its route-derived durable archive")
    if full["status"] != "PASS":
        failure = full.get("failure")
        require(type(failure) is dict,
                "retain the complete actual failed corrected interpreter lifecycle")
        worker = full.get("worker")
        actual_calls: int | str = "NOT ESTABLISHED"
        created: int | str = "NOT ESTABLISHED"
        destroyed: int | str = "NOT ESTABLISHED"
        actual = failure.get("actual_failure")
        if type(actual) is dict:
            inner = actual.get("actual_failure", actual)
            if type(inner) is dict:
                for field in ("actual_case_interpreter_exec_calls",
                              "actual_interpreters_created",
                              "actual_interpreters_destroyed"):
                    if field in inner:
                        checked_case_count(inner[field], 10_000, field)
                actual_calls = inner.get("actual_case_interpreter_exec_calls",
                                         "NOT ESTABLISHED")
                created = inner.get("actual_interpreters_created", "NOT ESTABLISHED")
                destroyed = inner.get("actual_interpreters_destroyed", "NOT ESTABLISHED")
        require(worker is None,
                "never count missing or failed interpreter cases as executed")
        return {
            "actual_candidate_case_count": 0,
            "actual_candidate_workers": 1
            if full.get("worker_process") is not None else 0,
            "candidate_records_location": archive_owner,
            "candidate_publication_receipt": receipt_owner,
            "actual_case_interpreter_exec_calls": actual_calls,
            "actual_interpreters_created": created,
            "actual_interpreters_destroyed": destroyed,
            "mismatch_count": 0,
            "all_mismatches": [],
            "all_failure_reasons": [failure],
            "source_owned_candidate_status": "FAIL",
            "source_owned_publication_status": "PASS",
        }
    nested = context["nested"]
    arguments = nested.parse_arguments(nested_arguments(options, approval))
    nested_context = nested.authenticate_prerequisites(arguments)
    original = nested_context["original"]
    baseline = original.load_original_baseline()
    worker = full.get("worker")
    require(type(worker) is dict and type(worker.get("pid")) is int,
            "require the actual complete nested interpreter worker and PID")
    exact = nested.validate_actual_worker(
        worker, context=nested_context, baseline=baseline,
        expected_pid=worker["pid"],
    )
    require(exact == worker and worker.get("case_count") == suite.case_count
            and worker.get("actual_case_interpreter_exec_calls") == 394
            and worker.get("actual_initialization_interpreter_exec_calls") == 11
            and worker.get("actual_guard_cleanup_interpreter_exec_calls") == 11
            and worker.get("actual_interpreters_created") == 11
            and worker.get("actual_interpreters_destroyed") == 11
            and worker.get("reference_records_sha256") == suite.reference_sha256
            and worker.get("projected_reference_records_sha256")
            == PROJECTED_REFERENCE_SHA256
            and all(worker.get(flag) is True for flag in (
                "all_real_pipes_read_to_eof", "all_real_pipe_descriptors_closed",
                "interpreter_live_set_restored", "locale_restored",
                "simultaneous_interpreters_verified",
                "b_closed_before_a_reexecution", "fresh_c_verified",
                "persistent_original_v5_per_interpreter",
            )),
            "only all 128 original cases and genuine 394 V3 calls can pass")
    return {
        "actual_candidate_case_count": suite.case_count,
        "actual_candidate_workers": 1,
        "candidate_records_location": archive_owner,
        "candidate_publication_receipt": receipt_owner,
        "candidate_records_sha256": worker.get("records_sha256"),
        "actual_case_interpreter_exec_calls": 394,
        "actual_initialization_interpreter_exec_calls": 11,
        "actual_guard_cleanup_interpreter_exec_calls": 11,
        "actual_interpreters_created": 11,
        "actual_interpreters_destroyed": 11,
        "projected_reference_records_sha256": PROJECTED_REFERENCE_SHA256,
        "mismatch_count": 0,
        "all_mismatches": [],
        "all_failure_reasons": [],
        "source_owned_candidate_status": "PASS",
        "source_owned_publication_status": "PASS",
    }


def direct_worker(options: argparse.Namespace) -> dict[str, Any]:
    context = authenticate_frozen_context(options)
    approval = authenticate_canonical_activation(options, context)
    suite = suite_spec(options.suite)
    require(suite.name in {"public_surface_v19", "pep688_v4",
                           "threaded_pattern_v1"},
            "direct observation is restricted to the exact three original suites")
    original = context["original_candidate_gate"]
    spec = original.suite_spec(suite.name)
    family = original.family_spec(options.candidate)
    if suite.name == "public_surface_v19":
        harness = import_frozen(LOCALE_HARNESS_RELATIVE, LOCALE_HARNESS_SHA256,
                                context["allowed_paths"])
        original_locale = locale.setlocale(locale.LC_CTYPE)
        original_path = os.environ.get("LOCPATH")
        with harness.authentic_private_locales() as locale_evidence:
            result = original.run_direct_candidate_worker(
                spec, family, approval["pins"],
                locale_names={"iso8859_1": "en_US.iso88591", "utf8": "en_US.utf8"},
            )
        require(locale.setlocale(locale.LC_CTYPE) == original_locale
                and os.environ.get("LOCPATH") == original_path
                and locale_evidence.get("actual_localedef_workers") == 2
                and locale_evidence.get("iso_8859_1_verified") is True
                and locale_evidence.get("utf_8_verified") is True
                and locale_evidence.get("temporary_directory_removed") is True,
                "create, observe, and clean both genuinely differently encoded locales")
        result["resource_evidence"]["actual_private_locale_provision"] = locale_evidence
    else:
        result = original.run_direct_candidate_worker(spec, family, approval["pins"])
    require(type(result) is dict and result.get("status") == "OBSERVED"
            and result.get("suite") == suite.name
            and result.get("candidate_family") == options.candidate,
            "return only the full original authentic native candidate observations")
    return result


def actual_native_pins(options: argparse.Namespace,
                       context: Mapping[str, Any],
                       approval: Mapping[str, Any]) -> dict[str, str]:
    original = context["original_candidate_gate"]
    current = original.validate_owners(
        original.family_spec(options.candidate),
        adapter=options.candidate_source_sha256,
        engine=options.native_engine_sha256,
        bridge=options.native_bridge_sha256,
        source_entries=options.owned_source_sha256,
    )
    require(current == approval["pins"],
            "the exact source-verified canonical candidate changed during a suite")
    return current


def observe_actual_suite(suite: SuiteSpec, options: argparse.Namespace,
                         context: Mapping[str, Any],
                         approval: Mapping[str, Any]) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "suite": suite.name,
        "candidate_family": options.candidate,
        "case_execution_denominator": suite.case_count,
        "matrix_sha256": suite.matrix_sha256,
        "reference_records_sha256": suite.reference_sha256,
        "producer_source_path": suite.source_relative,
        "producer_source_sha256": suite.source_sha256,
        "status": "FAIL",
        "actual_process": None,
        "actual_candidate_case_count": 0,
        "actual_candidate_workers": 0,
        "mismatch_count": 0,
        "all_mismatches": [],
        "all_failure_reasons": [],
        "failure": None,
    }
    try:
        actual_native_pins(options, context, approval)
        command = producer_command(suite, options, context, approval)
        process = encoded_process(command)
        evidence["actual_process"] = process
        require(process.get("timed_out") is False
                and process.get("returncode") in {0, 1},
                "preserve the exact actual timeout, fatal signal, or native crash")
        stdout = restore_stream(process.get("stdout"),
                                suite.name + " complete producer stdout")
        stderr = restore_stream(process.get("stderr"),
                                suite.name + " complete producer stderr")
        require(stderr == b"",
                "preserve rather than hide genuine candidate producer stderr")
        value = decode_document(stdout, suite.name + " complete actual producer")
        if suite.recorder_relative is not None:
            observed = validate_specialized_result(
                value, suite, options, context, process["returncode"],
            )
        elif suite.name == "subinterpreter_v2":
            observed = validate_nested_result(
                value, suite, options, context, approval,
                process["returncode"],
            )
        elif suite.name in {"public_surface_v19", "pep688_v4",
                            "threaded_pattern_v1"}:
            observed = validate_direct_result(
                value, suite, options, context, process["returncode"],
            )
        elif suite.name == "original_bounded_v5":
            require(process["returncode"] == 0,
                    "preserve the genuine failed original CPython test process")
            observed = context["legacy_worker"].validate_original_result(
                value, context["legacy_worker"].suite_spec(suite.name), options,
            )
            observed.update(actual_candidate_workers=1, mismatch_count=0,
                            all_mismatches=[], all_failure_reasons=[])
        else:
            observed = validate_category_result(
                value, suite, options, context, process["returncode"],
            )
        require(type(observed) is dict,
                "retain the complete original source-owned suite outcome")
        evidence.update(observed)
        if (observed.get("actual_candidate_case_count") == suite.case_count
                and observed.get("mismatch_count") == 0
                and not observed.get("all_failure_reasons")
                and observed.get("source_owned_candidate_status", "PASS")
                != "FAIL"):
            evidence["status"] = "PASS"
        else:
            evidence["failure"] = {
                "type": "ActualCandidateMismatch",
                "message": "the complete original source-owned cases did not match",
                "actual_mismatch_count": observed.get("mismatch_count", 0),
                "actual_failure_reasons": observed.get("all_failure_reasons", []),
            }
    except Exception as error:
        actual = locals().get("value")
        if type(actual) is dict:
            records = actual.get("candidate_records", actual.get("records"))
            if type(records) is list:
                if suite.name == "original_bounded_v5":
                    runnable = [record for record in records
                                if type(record) is dict
                                and record.get("status") != "SKIP"]
                    evidence["actual_candidate_case_count"] = len(runnable)
                else:
                    evidence["actual_candidate_case_count"] = len(records)
                evidence["actual_candidate_workers"] = (
                    actual.get("actual_candidate_workers", 1)
                )
                evidence["candidate_records_sha256"] = (
                    actual.get("candidate_records_sha256")
                    or actual.get("records_sha256")
                )
            evidence["complete_decoded_failed_producer"] = actual
        failure: dict[str, Any] = {
            "type": type(error).__qualname__,
            "message": str(error),
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__,
            ),
        }
        details = getattr(error, "details", None)
        if type(details) is dict:
            failure["actual_failure"] = details
        evidence["failure"] = failure
        evidence["all_failure_reasons"].append(failure)
    actual_native_pins(options, context, approval)
    return evidence


def planned_worker_paths(family: str, label: str,
                         *, failure: bool) -> tuple[str, str]:
    stem = "oracle/phase2/evidence/frozen-p0-candidate-worker-v4-"
    stem += checked_family(family) + "-" + checked_label(label)
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def ensure_fresh_run_evidence(family: str, label: str) -> None:
    predetermined: set[str] = set()
    for failure in (False, True):
        predetermined.update(planned_worker_paths(family, label, failure=failure))
        predetermined.update(nested_evidence_paths(
            family, label, version="3", failure=failure,
        ))
    for suite in FROZEN_SUITES:
        if suite.recorder_relative is not None:
            predetermined.update(specialized_evidence_paths(suite, family, label))
    for relative in sorted(predetermined):
        require(relative.startswith("oracle/phase2/evidence/")
                or relative.startswith("experiments/rust_public_practice_v1/"),
                "check only the exact frozen producer-owned evidence roots")
        try:
            os.lstat(str(ROOT / relative))
        except FileNotFoundError:
            continue
        raise CandidateGateError(
            "refuse to replace an immutable published candidate result: " + relative
        )


def write_fresh_evidence(directory: int, basename: str,
                         content: bytes) -> dict[str, Any]:
    require(type(directory) is int and directory >= 0
            and type(basename) is str and basename not in {"", ".", ".."}
            and "/" not in basename and "\\" not in basename
            and type(content) is bytes and 0 < len(content) <= MAX_REPORT_BYTES,
            "publish only one exact bounded exclusive candidate evidence owner")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(basename, flags, 0o644, dir_fd=directory)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode),
                "publish only a fresh regular exact-byte evidence owner")
        offset = 0
        while offset < len(content):
            written = os.write(descriptor, content[offset:])
            require(type(written) is int and written > 0,
                    "retain every real candidate evidence byte")
            offset += written
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require((before.st_dev, before.st_ino)
                == (after.st_dev, after.st_ino)
                and (after.st_dev, after.st_ino, after.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and after.st_size == len(content),
                "verify the same exclusively created durable evidence inode")
        return {
            "relative": "oracle/phase2/evidence/" + basename,
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": len(content),
            "device": after.st_dev,
            "inode": after.st_ino,
            "exclusive_creation": True,
            "file_fsync_completed": True,
            "same_inode_readback_verified": True,
        }
    finally:
        os.close(descriptor)


def publish_actual_report(report: dict[str, Any], options: argparse.Namespace,
                          *, prefix: str = "frozen-p0-candidate-worker-v4-",
                          schema: str = SCHEMA) -> dict[str, Any]:
    family, label = checked_family(options.candidate), checked_label(options.label)
    require(report.get("status") in {"PASS", "FAIL"}
            and report.get("candidate_family") == family
            and report.get("suite_count") == SUITE_COUNT
            and report.get("case_execution_denominator") == CASE_DENOMINATOR,
            "preserve the complete actual original 13-suite candidate result")
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT_BYTES,
            "the lossless complete candidate report exceeds the frozen 32-MiB limit")
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(compressed) <= MAX_REPORT_BYTES,
            "retain the bounded deterministic complete candidate gzip")
    failed = report["status"] == "FAIL"
    stem = prefix + family + "-" + label + ("-failures" if failed else "")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0))
    directory = os.open(str(ROOT / "oracle/phase2/evidence"), flags)
    try:
        archive = write_fresh_evidence(directory, stem + ".json.gz", compressed)
        os.fsync(directory)
        receipt_document = {
            "schema": schema + "-durable-publication-receipt",
            "status": "PASS",
            "candidate_status": report["status"],
            "candidate_family": family,
            "label": label,
            "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "document_sha256": report["document_sha256"],
            "archive": archive,
            "uncompressed_sha256": hashlib.sha256(plain).hexdigest(),
            "uncompressed_bytes": len(plain),
            "archive_directory_fsync_completed": True,
            "failure_preserved": failed,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "final_holdout_authorized": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        receipt = write_fresh_evidence(
            directory, stem + "-publication-receipt.json",
            canonical(receipt_document),
        )
        os.fsync(directory)
    finally:
        os.close(directory)
    return {
        "schema": schema + "-published-complete-candidate",
        "status": report["status"],
        "candidate_family": family,
        "label": label,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "completed_candidate_suite_count":
        report["completed_candidate_suite_count"],
        "qualified_candidate_case_executions":
        report["qualified_candidate_case_executions"],
        "candidate_qualified": report["candidate_qualified"],
        "complete_archive": archive,
        "complete_publication_receipt": receipt,
        "all_mismatches_crashes_and_timeouts_preserved": True,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def run_actual_candidate(options: argparse.Namespace) -> dict[str, Any]:
    context = authenticate_frozen_context(options)
    approval = authenticate_canonical_activation(options, context)
    family = checked_family(options.candidate)
    label = checked_label(options.label)
    ensure_fresh_run_evidence(family, label)
    suites: list[dict[str, Any]] = []
    for suite in FROZEN_SUITES:
        suites.append(observe_actual_suite(suite, options, context, approval))
    passing = [row for row in suites if row.get("status") == "PASS"]
    passing_cases = sum(row["actual_candidate_case_count"] for row in passing)
    all_cases = len(passing) == SUITE_COUNT and passing_cases == CASE_DENOMINATOR
    report: dict[str, Any] = {
        "schema": SCHEMA + "-complete-candidate-evaluation",
        "status": "PASS" if all_cases else "FAIL",
        "candidate_family": family,
        "label": label,
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "document_sha256": options.document_sha256,
        "build_version": str(options.build_version),
        "phase1_inventory_sha256": P0_SHA256,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "attempted_candidate_suite_count": len(suites),
        "completed_candidate_suite_count": len(passing),
        "qualified_candidate_case_executions": passing_cases,
        "actual_semantic_mismatch_count": sum(
            checked_case_count(row.get("mismatch_count"),
                               row["case_execution_denominator"],
                               row["suite"] + " actual mismatches")
            for row in suites
        ),
        "candidate_qualified": all_cases,
        "all_suites": suites,
        "all_failure_reasons": [
            {"suite": row["suite"], "failure": row["failure"]}
            for row in suites if row.get("failure") is not None
        ],
        "pinned_python_owner": context["pinned_python_owner"],
        "corrected_canonical_activation": approval["canonical_activation"],
        "corrected_source_build": approval["source_build"],
        "preserved_actual_v5_campaigns":
        context["preserved_v5_campaigns"],
        "preserved_historical_artifact_count": 32,
        "preserved_historical_restoration_receipt_count": 2,
        "all_mismatches_crashes_and_timeouts_preserved": True,
        "supplemental_cases_added_to_phase1_denominator": False,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    return publish_actual_report(report, options)


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate every immutable original Python regex case honestly.",
        allow_abbrev=False,
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--internal-candidate-worker", action="store_true")
    parser.add_argument("--suite")
    parser.add_argument("--candidate", choices=FAMILIES)
    parser.add_argument("--label")
    parser.add_argument("--build-version", choices=("2", "3"))
    parser.add_argument("--build-label")
    parser.add_argument("--activation-root")
    parser.add_argument("--owned-source-sha256", action="append", default=[])
    for name in (
        "source", "protocol", "document", "subinterpreter-source",
        "subinterpreter-protocol", "subinterpreter-explanation",
        "build-source", "build-protocol", "build-archive", "build-receipt",
        "activation-source", "activation-protocol", "activation-report",
        "activation-receipt", "recovery-journal", "candidate-source",
        "native-engine", "native-bridge",
    ):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(arguments)
    if options.self_test:
        require(not any(getattr(options, name) is not None for name in (
            "suite", "candidate", "label", "build_version", "build_label",
            "activation_root", "source_sha256", "protocol_sha256",
            "document_sha256", "candidate_source_sha256",
            "native_engine_sha256", "native_bridge_sha256",
        )) and not options.owned_source_sha256,
                "a source-only synthetic test cannot authorize actual activity")
        return options
    for name, expected in (
        ("subinterpreter_source_sha256", NESTED_V3_SHA256),
        ("subinterpreter_protocol_sha256", NESTED_V3_DOCUMENT_SHA256),
        ("subinterpreter_explanation_sha256", NESTED_V3_PROTOCOL_SHA256),
        ("activation_source_sha256", ACTIVATION_SHA256),
        ("activation_protocol_sha256", ACTIVATION_PROTOCOL_SHA256),
    ):
        observed = getattr(options, name)
        if observed is not None:
            require(checked_digest(observed, name) == expected,
                    "reject a substituted original nested or corrected V2 owner")
    for name in (
        "source_sha256", "protocol_sha256", "document_sha256",
        "build_source_sha256", "build_protocol_sha256",
        "build_archive_sha256", "build_receipt_sha256",
        "activation_report_sha256", "activation_receipt_sha256",
        "recovery_journal_sha256", "candidate_source_sha256",
        "native_engine_sha256", "native_bridge_sha256",
    ):
        value = getattr(options, name)
        if value is not None:
            checked_digest(value, name)
    if options.verify_frozen_context:
        return options
    mandatory = (
        "candidate", "label", "build_version", "build_label",
        "activation_root", "source_sha256", "protocol_sha256",
        "document_sha256", "build_source_sha256", "build_protocol_sha256",
        "build_archive_sha256", "build_receipt_sha256",
        "activation_source_sha256", "activation_protocol_sha256",
        "activation_report_sha256", "activation_receipt_sha256",
        "candidate_source_sha256", "native_engine_sha256",
        "native_bridge_sha256",
    )
    require(all(getattr(options, name) is not None for name in mandatory)
            and bool(options.owned_source_sha256),
            "explicitly pin all actual candidate, activation, and source owners")
    checked_family(options.candidate)
    checked_label(options.label)
    checked_label(options.build_label)
    require(FAMILY_BUILD_VERSION[options.candidate] == options.build_version,
            "Zig requires genuine V3; C and Rust require genuine V2")
    for entry in options.owned_source_sha256:
        require(type(entry) is str and entry.count("=") == 1,
                "authenticate the complete unchanged independent source closure")
        relative, fingerprint = entry.split("=", 1)
        require(type(relative) is str and bool(relative),
                "preserve each independently owned actual candidate source")
        checked_digest(fingerprint, relative)
    if options.internal_candidate_worker:
        require(options.suite is not None,
                "select exactly one frozen original direct observation route")
    else:
        require(options.suite is None,
                "run the complete original matrix, never a hand-picked subset")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        options = parse_arguments(arguments)
        if options.self_test:
            result = source_self_test()
        elif options.verify_frozen_context:
            result = verify_frozen_context(options)
        elif options.internal_candidate_worker:
            result = direct_worker(options)
        else:
            result = run_actual_candidate(options)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") in {"PASS", "OBSERVED"} else 1
    except Exception as error:
        failure = {
            "schema": SCHEMA + "-entry-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error_message": str(error),
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "final_holdout_authorized": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        details = getattr(error, "details", None)
        if type(details) is dict:
            failure["actual_failure"] = details
        sys.stdout.buffer.write(canonical(failure))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
