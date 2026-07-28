#!/usr/bin/env python3
"""Freeze and retain every real Python-regex candidate result, including failure.

Version 5 corrects the genuinely observed V6 nested publication-owner bug.
Original nested V3 evidence uses ``file_fsync``; specialized recorders use
``file_fsync_completed``.  Neither schema may be broadened or interchanged.
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
SOURCE_RELATIVE = "tools/run_frozen_p0_candidate_worker_v5.py"
RUNNER_RELATIVE = "tools/run_frozen_p0_candidate_v7.py"
PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V7.md"
DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v7.json"
SCHEMA = "rebar-frozen-python-re-p0-candidate-worker-v5"
PROTOCOL_SCHEMA = "rebar-frozen-python-re-p0-candidate-protocol-v7"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
PHASE1_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"

V6_WORKER_RELATIVE = "tools/run_frozen_p0_candidate_worker_v4.py"
V6_WORKER_SHA256 = "b0111d76df52ead959863c4459ea1b78f78ab6b1e0d0417624df268860918d8b"
V6_RUNNER_RELATIVE = "tools/run_frozen_p0_candidate_v6.py"
V6_RUNNER_SHA256 = "53c5abd71ba46384204f628238dfc4b91a9adf6c75f8edd838e6523300677a9c"
V6_PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V6.md"
V6_PROTOCOL_SHA256 = "b1d50f9778257d25e22df7ddba493e6830c514365d25ded518ea832b5e175c39"
V6_DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v6.json"
V6_DOCUMENT_SHA256 = "73cbdf73f94de18496793bafe4ab29c613d694bfde8c47e7ec8430d27a23b521"

NESTED_V3_RELATIVE = "tools/run_owned_candidate_subinterpreters_v3.py"
NESTED_V3_SHA256 = "21febe241549963a2818af2a20782da81bdf952fb7be8affc4289d9ccc9ad5b4"
NESTED_V3_DOCUMENT_RELATIVE = "oracle/phase2/candidate-subinterpreters-v3.json"
NESTED_V3_DOCUMENT_SHA256 = "17dac72e6a0ae75bf1f013656b9779a1e948e71439cf336499c1e680beb19284"
NESTED_V3_PROTOCOL_RELATIVE = "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V3.md"
NESTED_V3_PROTOCOL_SHA256 = "97354130b4d1ab97ee2c684b43b72e29a0a68439c2a1ead5a4f45edc20e6c9b4"

ACTIVATION_V2_RELATIVE = "tools/activate_verified_native_candidate_v2.py"
ACTIVATION_V2_SHA256 = "e6e8a72feffcf670da9a3e4d2e8b642e933c1d81cfe5bf7d1636385f207d6218"
ACTIVATION_V2_PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V2.md"
ACTIVATION_V2_PROTOCOL_SHA256 = "a675b411873c01ae88ea50d4f95aab7231a29dde38a458a947437f07ed850529"

INDEPENDENCE_V2_RELATIVE = "tools/audit_candidate_independence_v2.py"
INDEPENDENCE_V2_SHA256 = "57168db3df64414a7dc27f1793d9c22b7c493a8b37c025dc57243796e892d93c"
INDEPENDENCE_V2_PROTOCOL_RELATIVE = "oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md"
INDEPENDENCE_V2_PROTOCOL_SHA256 = "80a1de729c067da36648dcfb9751f7bd3833ff561956df9ad82fc6106a19a16b"
INDEPENDENCE_V2_DOCUMENT_RELATIVE = "oracle/phase2/candidate-independence-v2.json"
INDEPENDENCE_V2_DOCUMENT_SHA256 = "89662570a643d94ae1581393ed48015c6fa78d5dbe5ad0419e9a2032e4609659"

BUILD_V4_RELATIVE = "tools/reproduce_owned_native_source_build_v4.py"
BUILD_V4_SHA256 = "efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1"
BUILD_V4_PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILD-V4.md"
BUILD_V4_PROTOCOL_SHA256 = "e974b26562cc210c175c08cda7914e6b196fdee2ebe2a8232dd87c0cddbc0dfb"
BUILD_V4_DOCUMENT_RELATIVE = "oracle/phase2/native-source-build-v4.json"
BUILD_V4_DOCUMENT_SHA256 = "0b5641529bc49f55b9e56fe397ad38e7e23d6c9b3376587b743753814b8089d7"
FUTURE_ACTIVATION_RELATIVE = "tools/activate_verified_native_candidate_v3.py"
FUTURE_ACTIVATION_SHA256 = "39a170d5981e3484366eca223c0533366d92927975271fdb004fbce784b7a21e"
FUTURE_ACTIVATION_PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V3.md"
FUTURE_ACTIVATION_PROTOCOL_SHA256 = "17656cd0ea3aa879cc5c69078460118f1e5e977f3e5c8d977c784954ea9f65bf"
FUTURE_ACTIVATION_DOCUMENT_RELATIVE = "oracle/phase2/verified-native-activation-v3.json"
FUTURE_ACTIVATION_DOCUMENT_SHA256 = "87d2d34a142f620894b87b35f3216ede4a0374921a3dfacb9d8e209e3d3133fc"

SUITE_COUNT = 13
CASE_DENOMINATOR = 31_237
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_PLAIN_BYTES = 256 * 1024 * 1024
MAX_SPECIALIZED_BYTES = 64 * 1024 * 1024
MAX_NESTED_BYTES = 48 * 1024 * 1024
MAX_PROCESS_BYTES = 96 * 1024 * 1024
MAX_REPORT_BYTES = 32 * 1024 * 1024
TIMEOUT_SECONDS = 3_600
FAMILIES = ("rust", "c", "zig")
FUTURE_FAMILIES = ("cpp", "go", "fortran")
SOURCE_FAMILIES = (*FAMILIES, *FUTURE_FAMILIES)
FAMILY_BUILD_VERSION = {"rust": "2", "c": "2", "zig": "3",
                        "cpp": "4", "go": "4", "fortran": "4"}
PROJECTED_REFERENCE_SHA256 = "cf5633c8dc1038d650603eee421371285d0e32f6446190ce728590f1f5c55021"


class CandidateGateError(Exception):
    """An exact independently frozen candidate observation failed."""


class SourceOnlyEffect(CandidateGateError):
    """A synthetic or read-only check attempted an external side effect."""


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
        "passing_suites": 7, "verified_passing_cases": 7197,
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
        "passing_suites": 8, "verified_passing_cases": 7461,
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


HISTORICAL_ZIG_OWNERS: dict[str, str] = {
    "oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-failures.json.gz":
    "2ca2a253e4148c4232327cf89f1306c1c4e83639714f3b036ebdd7bd0225aaa3",
    "oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-failures-publication-receipt.json":
    "72c2635850273543eded2e9f541cb64529f2ce22a9d6fe5b14c30705fa474c95",
    "oracle/phase2/evidence/frozen-p0-candidate-worker-v4-zig-phase2-v6-failures.json.gz":
    "07a1be40b4aba273bdec1f5d567aad0c6fbbf860189ade527eb90cfed1aab594",
    "oracle/phase2/evidence/frozen-p0-candidate-worker-v4-zig-phase2-v6-failures-publication-receipt.json":
    "8c5f69411600781dca1efd3965b98fcecf9a1fec00afb4e5f7d319c2afa86cf4",
    "oracle/phase2/evidence/owned-candidate-subinterpreters-v3-zig-phase2-v6-subinterpreters-failures.json.gz":
    "ded1049f0d1979b6a71c80fcd86fe411e400603b02bbe28ed8b3634f513612f4",
    "oracle/phase2/evidence/owned-candidate-subinterpreters-v3-zig-phase2-v6-subinterpreters-failures-publication-receipt.json":
    "8fc8e0753458e69751fd45b820764e7c085ec6111c9dcda64ee90ef227b0ce21",
    "oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-restoration-receipt.json":
    "c415ba80c055d39a933617a839624037b557adbe30c418c2a0e859131fbe9028",
    "experiments/rust_public_practice_v1/zig-managed-buffer-lifetime-v1-phase2-v6-managed.json.gz":
    "43a8cf60484c46e85ba7b5853f38ee4c250f4383186dc33eb08162b30d0c897a",
    "experiments/rust_public_practice_v1/zig-managed-buffer-lifetime-v1-phase2-v6-managed-publication-receipt.json":
    "d28c95236df9b19e5ab27a1174d5b8616cf2ba22394314ee2dcb78c13034d516",
    "experiments/rust_public_practice_v1/zig-scanner-verbose-comments-v1-phase2-v6-verbose.json.gz":
    "ec5b4e20e05bdd068d065cf9ace9d4d988220565b29db0be91c15b1fa5a0403f",
    "experiments/rust_public_practice_v1/zig-scanner-verbose-comments-v1-phase2-v6-verbose-publication-receipt.json":
    "3e8d850af3ad191c24b92182ed4e694c44c23716b37c607a31c50c45659428d9",
    "experiments/rust_public_practice_v1/zig-public-type-identity-serialization-v1-phase2-v6-types.json.gz":
    "482dc8ba52e091e909a4d4acf6d57f964fc2e6fe8a729a105e8aca2b9448c2c6",
    "experiments/rust_public_practice_v1/zig-public-type-identity-serialization-v1-phase2-v6-types-publication-receipt.json":
    "82f96615d0894b99ed1316df6fde2c713e3d7d4b19f18cf71a7e97e82a2352df",
    "experiments/rust_public_practice_v1/zig-substitution-buffer-semantics-v2-phase2-v6-substitution.json.gz":
    "d83cdc6bb1b5bb878e55e5fea866eaec6c07e9dd78f983858cecc15463ac6de2",
    "experiments/rust_public_practice_v1/zig-substitution-buffer-semantics-v2-phase2-v6-substitution-publication-receipt.json":
    "9b4c4daaf775bb585a3dcfbe693b91c14d49eb09aafd79360fb41ed5cd083791",
    "experiments/rust_public_practice_v1/zig-shape-changing-buffer-semantics-v2-phase2-v6-shape.json.gz":
    "b4766c3c3547ea347421bf4784ac11eb2b63e6065135002139fdb17ca69bc7c8",
    "experiments/rust_public_practice_v1/zig-shape-changing-buffer-semantics-v2-phase2-v6-shape-publication-receipt.json":
    "e020e83774064cb9c9c9f9a70229ad3bcd04b0e417942317be4fbdb33f365ba9",
}

HISTORICAL_V4_BUILD_OWNERS: dict[str, dict[str, Any]] = {
    "cpp": {
        "status": "PASS", "phase_count": 2, "process_count": 10,
        "archive": "oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4.json.gz",
        "archive_sha256": "48910a6328e8aaacdac993b2c029995d878960a456359a14db5c83b9fc518df9",
        "receipt": "oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4-publication-receipt.json",
        "receipt_sha256": "7742eda3ce777b1378d0c7fb87fc064f222850ca8bcf15cd23ff8a4d87d8bebf",
        "bridge_sha256": "d444611316caceb4ba08783203bc4f1d396a8987f63a49bd24c81d5d2c532441",
        "bridge_bytes": 130744,
    },
    "go": {
        "status": "FAIL", "phase_count": 0, "process_count": 4,
        "archive": "oracle/phase2/evidence/native-source-build-v4-go-phase2-v4-failures.json.gz",
        "archive_sha256": "fcf643b7b8e9fbe80bd3b40c7ed884695a844f46e1117f5ebdb130135e5db4bb",
        "receipt": "oracle/phase2/evidence/native-source-build-v4-go-phase2-v4-failures-publication-receipt.json",
        "receipt_sha256": "215e9680bbe0f8d2250fcca8bae0335017606288e13e7636224b7c76336b5e41",
        "error_type": "BuildError",
        "error_message":
        "the exact independently owned compiler or ELF command failed: build_go_engine",
        "failed_process": "build_go_engine", "failed_process_exit_status": 1,
        "failed_process_stderr_sha256":
        "4173a7583fe0358c92056da596f06837bd7a888aa56d6e66cb2920d806600862",
    },
    "fortran": {
        "status": "FAIL", "phase_count": 2, "process_count": 18,
        "archive": "oracle/phase2/evidence/native-source-build-v4-fortran-phase2-v4-failures.json.gz",
        "archive_sha256": "ba35ea4f0d28814f716a36d2ccb384ef034a88a4029ca3f3cbf4f91eae268103",
        "receipt": "oracle/phase2/evidence/native-source-build-v4-fortran-phase2-v4-failures-publication-receipt.json",
        "receipt_sha256": "86b4b2648adf651481eea8d8b427a432f121c59322f508b522eca18af0749a08",
        "error_type": "BuildError",
        "error_message": "the two independently owned outputs are not genuinely byte-identical",
        "bridge_sha256": "eba8c1d145a53a2017fc9b7a6e4651b31ec4aef2e67e6c176c6435bffafc7b26",
        "bridge_bytes": 37424,
        "first_engine_sha256": "37557a44033a80aa11a81fa145ca76c2bbd44ee544b31974dcf6e59ba0f2949c",
        "second_engine_sha256": "696126d3f3e7239cac55975f53beb3b5e5cffc6948f08258817b6b2d86422199",
        "engine_bytes": 74624,
    },
}

ZIG_MISMATCH_COUNTS = {
    "scanner_v3": 64,
    "scanner_verbose_v1": 620,
    "public_types_v1": 248,
    "substitution_v2": 64,
    "shape_v2": 672,
    "public_surface_v19": 96,
}

NESTED_PUBLICATION_FIELDS = frozenset({
    "relative", "sha256", "bytes", "device", "inode",
    "exclusive_creation", "nofollow", "file_fsync",
    "same_inode_readback_verified",
})
SPECIALIZED_PUBLICATION_FIELDS = frozenset({
    "path", "sha256", "bytes", "uncompressed_bytes", "uncompressed_sha256",
    "compression", "actual_write_calls", "atomic_no_overwrite_link",
    "complete_readback_verified", "directory_fsync_completed",
    "file_fsync_completed", "owned_temporary_removed",
})
WORKER_PUBLICATION_FIELDS = frozenset({
    "relative", "sha256", "bytes", "device", "inode",
    "exclusive_creation", "file_fsync_completed",
    "same_inode_readback_verified",
})


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise CandidateGateError(message)


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":")).encode("ascii")
                + b"\n")
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise CandidateGateError("require exact bounded finite canonical evidence") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value),
            "require a complete lowercase SHA-256: " + label)
    return value


def checked_family(value: Any) -> str:
    require(type(value) is str and value in SOURCE_FAMILIES,
            "select only one of the six independently source-owned families")
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 48
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(item in "abcdefghijklmnopqrstuvwxyz0123456789-" for item in value)
            and "--" not in value and not value.endswith("-"),
            "require a bounded non-traversing independently frozen label")
    return value


def checked_count(value: Any, maximum: int, label: str) -> int:
    require(type(value) is int and 0 <= value <= maximum,
            "require an exact genuine nonnegative candidate count: " + label)
    return value


def suite_spec(value: Any) -> SuiteSpec:
    found = [item for item in FROZEN_SUITES if item.name == value]
    require(type(value) is str and len(found) == 1,
            "select exactly one genuinely frozen original producer")
    return found[0]


def historical_v5_owners(family: str) -> dict[str, str]:
    require(type(family) is str and family in HISTORICAL_V5,
            "freeze only the complete actually published C and Rust V5 campaigns")
    values = HISTORICAL_V5[family]
    prefix = "oracle/phase2/evidence/"
    stem = "frozen-p0-candidate-v5-" + family + "-phase2-v5-failures"
    worker = "frozen-p0-candidate-worker-v3-" + family + "-phase2-v5-failures"
    nested = ("owned-candidate-subinterpreters-v1-" + family
              + "-phase2-v5-subinterpreters-failures")
    result = {
        prefix + stem + ".json.gz": values["outer_archive"],
        prefix + stem + "-publication-receipt.json": values["outer_receipt"],
        prefix + worker + ".json.gz": values["worker_archive"],
        prefix + worker + "-publication-receipt.json": values["worker_receipt"],
        prefix + "frozen-p0-candidate-v5-" + family
        + "-phase2-v5-restoration-receipt.json": values["restoration"],
        prefix + nested + ".json.gz": values["nested_archive"],
        prefix + nested + "-publication-receipt.json": values["nested_receipt"],
    }
    for name, pair in values["specialized"].items():
        suite = suite_spec(name)
        require(suite.evidence_slug is not None and suite.label_suffix is not None,
                "bind every actual historical specialized archive to its own suite")
        stem = ("experiments/rust_public_practice_v1/" + family + "-"
                + suite.evidence_slug + "-phase2-v5-" + suite.label_suffix)
        result[stem + ".json.gz"] = pair[0]
        result[stem + "-publication-receipt.json"] = pair[1]
    require(len(result) == 17,
            "preserve all sixteen real historical results and the real restoration")
    return dict(sorted(result.items()))


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject duplicate or substituted complete JSON fields")
        result[key] = value
    return result


def decode_document(raw: Any, label: str, *, maximum: int = MAX_PLAIN_BYTES,
                    canonical_required: bool = False) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= maximum,
            "require complete bounded independently preserved evidence: " + label)
    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique_pairs,
            parse_constant=lambda item: (_ for _ in ()).throw(
                CandidateGateError("reject non-finite evidence: " + item)
            ),
        )
    except (ValueError, TypeError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise CandidateGateError("reject malformed complete evidence: " + label) from error
    require(type(value) is dict,
            "require a full original typed evidence object: " + label)
    if canonical_required:
        require(canonical(value) == raw,
                "reject altered, noncanonical, or incomplete evidence: " + label)
    return value


def protocol_document() -> dict[str, Any]:
    suites: list[dict[str, Any]] = []
    for suite in FROZEN_SUITES:
        record: dict[str, Any] = {
            "id": suite.name, "case_count": suite.case_count,
            "source_path": suite.source_relative,
            "source_sha256": suite.source_sha256,
            "matrix_sha256": suite.matrix_sha256,
            "reference_records_sha256": suite.reference_sha256,
            "published_seed": suite.seed,
        }
        if suite.recorder_relative is not None:
            record.update({
                "candidate_recorder_path": suite.recorder_relative,
                "candidate_recorder_sha256": suite.recorder_sha256,
                "baseline_label": suite.baseline_label,
                "evidence_slug": suite.evidence_slug,
                "evidence_label_suffix": suite.label_suffix,
                "maximum_specialized_uncompressed_bytes": MAX_SPECIALIZED_BYTES,
            })
        if suite.name == "original_bounded_v5":
            record.update(public_records=152, runnable_cases=151,
                          genuine_public_debug_skips=1, named_private_waivers=13)
        if suite.name == "public_surface_v19":
            record.update(real_locale_cases=64, real_locale_transitions=192,
                          canonical_digest="original-stage17-without-newline")
        if suite.name == "pep688_v4":
            record["canonical_digest"] = "original-pep688-with-newline"
        if suite.name == "threaded_pattern_v1":
            record.update(canonical_digest="original-threaded-without-newline",
                          mismatch_case_identity="case_id")
        if suite.name == "subinterpreter_v2":
            record.update({
                "original_case_count": 128,
                "actual_interpreters_required": 11,
                "actual_case_interpreter_exec_calls_required": 394,
                "actual_initialization_calls_required": 11,
                "actual_cleanup_calls_required": 11,
                "projected_reference_records_sha256": PROJECTED_REFERENCE_SHA256,
                "nested_maximum_uncompressed_bytes": MAX_NESTED_BYTES,
                "exact_original_publication_owner_fields":
                sorted(NESTED_PUBLICATION_FIELDS),
                "requires_original_nested_file_fsync": True,
                "accepts_substituted_file_fsync_completed": False,
                "failed_actual_calls_are_qualified_cases": False,
                "supplemental_cases_added_to_denominator": False,
            })
        suites.append(record)
    zig_owners = [
        {"path": relative, "sha256": fingerprint}
        for relative, fingerprint in sorted(HISTORICAL_ZIG_OWNERS.items())
    ]
    return {
        "schema": PROTOCOL_SCHEMA,
        "version": 7,
        "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; VERSION-SEVEN CANDIDATES NOT RUN",
        "goal_sha256": GOAL_SHA256,
        "phase1": {
            "inventory_path": PHASE1_RELATIVE,
            "inventory_sha256": PHASE1_SHA256,
            "python_path": PINNED_PYTHON,
            "python_sha256": PINNED_PYTHON_SHA256,
            "python_version": "3.14.6",
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "named_private_waiver_count": 13,
            "runnable_original_public_method_count": 151,
            "preserved_original_public_record_count": 152,
            "genuine_original_public_debug_skip_count": 1,
        },
        "worker": {
            "source_path": SOURCE_RELATIVE,
            "schema": SCHEMA,
            "source_sha256_mode": "mandatory-exact-caller-pinned-source-bytes",
            "maximum_published_uncompressed_report_bytes": MAX_REPORT_BYTES,
        },
        "runner": {
            "source_path": RUNNER_RELATIVE,
            "source_sha256_mode": "mandatory-exact-caller-pinned-source-bytes",
            "maximum_published_uncompressed_report_bytes": MAX_REPORT_BYTES,
        },
        "preserved_frozen_v6": {
            "worker_path": V6_WORKER_RELATIVE,
            "worker_sha256": V6_WORKER_SHA256,
            "runner_path": V6_RUNNER_RELATIVE,
            "runner_sha256": V6_RUNNER_SHA256,
            "protocol_path": V6_PROTOCOL_RELATIVE,
            "protocol_sha256": V6_PROTOCOL_SHA256,
            "document_path": V6_DOCUMENT_RELATIVE,
            "document_sha256": V6_DOCUMENT_SHA256,
            "source_bug": "genuine-nested-v3-file_fsync-rejected-as-file_fsync_completed",
            "prior_files_modified": False,
        },
        "six_family_independence": {
            "source_path": INDEPENDENCE_V2_RELATIVE,
            "source_sha256": INDEPENDENCE_V2_SHA256,
            "protocol_path": INDEPENDENCE_V2_PROTOCOL_RELATIVE,
            "protocol_sha256": INDEPENDENCE_V2_PROTOCOL_SHA256,
            "document_path": INDEPENDENCE_V2_DOCUMENT_RELATIVE,
            "document_sha256": INDEPENDENCE_V2_DOCUMENT_SHA256,
            "family_count": 6,
            "source_family_count": 6,
            "fully_runnable_p0_family_count": 3,
            "fully_runnable_p0_families": list(FAMILIES),
            "complete_source_owner_count": 25,
            "cross_family_semantic_owner_count": 0,
            "external_regex_package_count": 0,
            "source_audit_is_runtime_qualification": False,
        },
        "current_canonical_activation": {
            "source_path": ACTIVATION_V2_RELATIVE,
            "source_sha256": ACTIVATION_V2_SHA256,
            "protocol_path": ACTIVATION_V2_PROTOCOL_RELATIVE,
            "protocol_sha256": ACTIVATION_V2_PROTOCOL_SHA256,
            "version": 2,
            "families": ["c", "rust", "zig"],
            "authentic_promotion_intents_required": True,
            "rollback_journal_required": True,
            "fallback_allowed": False,
        },
        "future_six_family_v4_build": {
            "source_path": BUILD_V4_RELATIVE,
            "source_sha256": BUILD_V4_SHA256,
            "protocol_path": BUILD_V4_PROTOCOL_RELATIVE,
            "protocol_sha256": BUILD_V4_PROTOCOL_SHA256,
            "document_path": BUILD_V4_DOCUMENT_RELATIVE,
            "document_sha256": BUILD_V4_DOCUMENT_SHA256,
            "family_count": 6,
            "activation_source_path": FUTURE_ACTIVATION_RELATIVE,
            "activation_source_sha256": FUTURE_ACTIVATION_SHA256,
            "activation_protocol_path": FUTURE_ACTIVATION_PROTOCOL_RELATIVE,
            "activation_protocol_sha256": FUTURE_ACTIVATION_PROTOCOL_SHA256,
            "activation_document_path": FUTURE_ACTIVATION_DOCUMENT_RELATIVE,
            "activation_document_sha256": FUTURE_ACTIVATION_DOCUMENT_SHA256,
            "future_families": list(FUTURE_FAMILIES),
            "future_candidate_runs_authorized": False,
            "actual_v3_activation_count": 0,
            "required_v4_build_status": "PASS",
            "required_v4_independent_fresh_phase_count": 2,
            "required_v3_activation_status": "PASS",
            "required_frozen_original_producer_support": True,
            "status": "V3 FROZEN; FUTURE MATCHING BLOCKED UNTIL ORIGINAL PRODUCERS SUPPORT EACH FAMILY",
            "guess_activation_source_pin_allowed": False,
        },
        "corrected_original_subinterpreters": {
            "source_path": NESTED_V3_RELATIVE,
            "source_sha256": NESTED_V3_SHA256,
            "document_path": NESTED_V3_DOCUMENT_RELATIVE,
            "document_sha256": NESTED_V3_DOCUMENT_SHA256,
            "protocol_path": NESTED_V3_PROTOCOL_RELATIVE,
            "protocol_sha256": NESTED_V3_PROTOCOL_SHA256,
            "exact_original_owner_fields": sorted(NESTED_PUBLICATION_FIELDS),
            "file_fsync_field": "file_fsync",
            "receipt_status_qualifies_candidate": False,
            "maximum_nested_uncompressed_bytes": MAX_NESTED_BYTES,
        },
        "preserved_historical_campaigns": {
            "c": {"source_version": 5, "status": "FAIL",
                  "candidate_qualified": False,
                  "passing_suite_count": 7, "verified_passing_case_count": 7197,
                  "legacy_qualified_candidate_case_executions": 7197,
                  "semantic_mismatch_count": 2094,
                  "actual_interpreter_case_calls": 0,
                  "artifact_count_including_restoration": 17,
                  "artifacts": [
                      {"path": path, "sha256": fingerprint}
                      for path, fingerprint in historical_v5_owners("c").items()
                  ]},
            "rust": {"source_version": 5, "status": "FAIL",
                     "candidate_qualified": False,
                     "passing_suite_count": 8,
                     "verified_passing_case_count": 7461,
                     "legacy_qualified_candidate_case_executions": 7461,
                     "semantic_mismatch_count": 2042,
                     "actual_interpreter_case_calls": "NOT ESTABLISHED",
                     "artifact_count_including_restoration": 17,
                     "artifacts": [
                         {"path": path, "sha256": fingerprint}
                         for path, fingerprint in historical_v5_owners("rust").items()
                     ]},
            "zig": {"source_version": 6, "status": "FAIL",
                    "candidate_qualified": False,
                    "passing_suite_count": 6,
                    "verified_passing_case_count": 3583,
                    "legacy_qualified_candidate_case_executions": 3583,
                    "semantic_mismatch_count": 1764,
                    "mismatches_by_suite": dict(ZIG_MISMATCH_COUNTS),
                    "nested_case_interpreter_exec_calls": 385,
                    "nested_interpreters_created": 3,
                    "nested_interpreters_destroyed": 3,
                    "nested_initialization_calls": 3,
                    "nested_guard_cleanup_calls": 4,
                    "nested_cleanup_failure_count": 3,
                    "nested_original_cases_qualified": 0,
                    "nested_worker_stdout_bytes": 1_126_801,
                    "nested_worker_stdout_sha256":
                    "2da4af1e62facbe6565bb127a0920f647ec04c3f0005d02f58b233229277721d",
                    "artifact_count_including_restoration": 17,
                    "artifacts": zig_owners},
            "candidate_artifact_count_including_restorations": 51,
            "total_artifact_count_including_source_builds": 57,
        },
        "preserved_v4_source_builds": {
            "artifact_count": 6,
            "actual_source_build_process_count": 32,
            "candidate_correctness": "NOT MEASURED",
            "candidate_processes_started": 0,
            "actual_v3_activations": 0,
            "cpp": {
                **HISTORICAL_V4_BUILD_OWNERS["cpp"],
                "candidate_correctness": "NOT MEASURED",
                "candidate_matching_cases_executed": 0,
                "activation_status": "NOT RUN",
                "candidate_qualified": False,
            },
            "go": {
                **HISTORICAL_V4_BUILD_OWNERS["go"],
                "receipt_status": "PASS",
                "build_status": "FAIL",
                "candidate_correctness": "NOT MEASURED",
                "candidate_matching_cases_executed": 0,
                "activation_status": "NOT RUN",
                "generated_header_status": "NOT GENERATED",
                "candidate_qualified": False,
            },
            "fortran": {
                **HISTORICAL_V4_BUILD_OWNERS["fortran"],
                "receipt_status": "PASS",
                "build_status": "FAIL",
                "failure_kind": "NON-REPRODUCIBLE ENGINE OUTPUT",
                "candidate_correctness": "NOT MEASURED",
                "candidate_matching_cases_executed": 0,
                "activation_status": "NOT RUN",
                "candidate_qualified": False,
            },
        },
        "historical_source_build_process_accounting": {
            "v2_source_build_process_count": 39,
            "v4_cpp_source_build_process_count": 10,
            "v4_go_source_build_process_count": 4,
            "v4_fortran_source_build_process_count": 18,
            "v4_source_build_process_count": 32,
            "v2_plus_v4_source_build_process_count": 71,
            "separately_preserved_successful_v3_zig_source_build_process_count": 15,
            "v2_plus_v3_plus_v4_source_build_process_count": 86,
            "process_id_uniqueness_required_within_each_actual_run": True,
            "process_id_uniqueness_claimed_across_independent_runs": False,
            "source_build_processes_are_candidate_workers": False,
            "actual_v3_activations": 0,
            "performance": "NOT MEASURED",
        },
        "publication_owner_schemas": {
            "specialized_fields": sorted(SPECIALIZED_PUBLICATION_FIELDS),
            "nested_v3_fields": sorted(NESTED_PUBLICATION_FIELDS),
            "v7_worker_fields": sorted(WORKER_PUBLICATION_FIELDS),
            "owner_schema_substitution_allowed": False,
            "child_selected_evidence_path_allowed": False,
            "specialized_uncompressed_byte_limit": MAX_SPECIALIZED_BYTES,
            "nested_uncompressed_byte_limit": MAX_NESTED_BYTES,
            "v7_uncompressed_byte_limit": MAX_REPORT_BYTES,
            "maximum_historical_reference_bytes": MAX_ARCHIVE_BYTES,
            "deterministic_gzip_mtime": 0,
            "exclusive_publication_required": True,
            "same_inode_required": True,
            "file_and_directory_fsync_required": True,
        },
        "candidate_families": [
            {"name": family, "build_version": int(FAMILY_BUILD_VERSION[family]),
             "independently_owned_parser_compiler_executor_required": True,
             "external_regex_package_allowed": False,
             "cross_candidate_delegation_allowed": False,
             "frozen_original_p0_producers_supported": family in FAMILIES,
             "candidate_correctness": "NOT MEASURED",
             "candidate_qualified": False}
            for family in SOURCE_FAMILIES
        ],
        "suites": suites,
        "boundaries": {
            "candidate_reference_delegation_allowed": False,
            "external_regex_engine_allowed": False,
            "cross_candidate_engine_allowed": False,
            "fallback_allowed": False,
            "guessed_future_activation_allowed": False,
            "partial_nested_cleanup_counts_as_passing_cases": False,
            "receipt_pass_means_candidate_pass": False,
            "fresh_reference_workers_started": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "holdout_opened": False,
            "winner_selected": False,
        },
        "candidate_results": "NOT MEASURED",
        "source_family_count": 6,
        "fully_runnable_p0_family_count": 3,
        "candidate_qualified_count": 0,
        "fully_qualified_candidate_count": 0,
    }


def validate_protocol_document(value: Any) -> dict[str, Any]:
    require(type(value) is dict and canonical(value) == canonical(protocol_document()),
            "the complete independently frozen V7 correctness protocol changed")
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and sys.path and sys.path[0] == str(ROOT),
            "use only the exact isolated pinned V7 worker and CPython 3.14.6")


def bounded_gzip(raw: bytes, label: str, *, maximum: int) -> bytes:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES
            and type(maximum) is int and 0 < maximum <= MAX_PLAIN_BYTES,
            "require a complete independently bounded compressed owner: " + label)
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as stream:
            plain = stream.read(maximum + 1)
            require(0 < len(plain) <= maximum,
                    "reject truncated or oversized complete archive: " + label)
            require(stream.read(1) == b"",
                    "reject concealed extra decompressed bytes: " + label)
    except (OSError, EOFError, gzip.BadGzipFile, ValueError) as error:
        raise CandidateGateError("reject invalid complete gzip: " + label) from error
    return plain


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {name: 0 for name in (
        "file_reads", "file_writes", "candidate_imports", "candidate_workers",
        "reference_workers", "source_builds", "native_promotions",
        "native_libraries_loaded", "interpreter_creations", "thread_starts",
        "network_requests", "clock_samples", "hidden_cases_read",
        "benchmark_files_read", "blocked_reads", "blocked_writes",
        "blocked_processes", "blocked_imports", "blocked_threads",
        "blocked_clocks", "blocked_promotions", "blocked_network",
    )}
    installed: list[tuple[Any, str, Any]] = []

    def install(owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def blocked(*args: Any, **kwargs: Any) -> Any:
            effects[category] += 1
            raise SourceOnlyEffect("the source-only V7 freeze forbids " + name)

        installed.append((owner, name, original))
        setattr(owner, name, blocked)

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "stat"), (os, "lstat"), (Path, "open"),
            (Path, "read_bytes"), (Path, "read_text"),
        ):
            install(owner, name, "blocked_reads")
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"), (os, "mkdir"),
            (os, "makedirs"), (os, "rename"), (os, "fsync"),
            (Path, "write_bytes"), (Path, "write_text"), (Path, "touch"),
            (Path, "mkdir"), (Path, "unlink"),
            (tempfile, "mkstemp"), (tempfile, "mkdtemp"),
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
                     "process_time_ns", "thread_time", "thread_time_ns"):
            install(time, name, "blocked_clocks")
        yield effects
    finally:
        for owner, name, original in reversed(installed):
            setattr(owner, name, original)


def check_publication_shape(value: Any, *, kind: str,
                            relative: str) -> dict[str, Any]:
    schemas = {"nested": NESTED_PUBLICATION_FIELDS,
               "specialized": SPECIALIZED_PUBLICATION_FIELDS,
               "worker": WORKER_PUBLICATION_FIELDS}
    require(kind in schemas and type(value) is dict
            and frozenset(value) == schemas[kind],
            "reject substituted or incomplete " + kind + " publication owner")
    field = "path" if kind == "specialized" else "relative"
    require(value.get(field) == relative
            and type(value.get("bytes")) is int
            and 0 < value["bytes"] <= MAX_ARCHIVE_BYTES,
            "reject an invented or unbounded original publication owner")
    checked_digest(value.get("sha256"), relative)
    if kind == "nested":
        require(type(value["device"]) is int and value["device"] >= 0
                and type(value["inode"]) is int and value["inode"] > 0
                and all(value[item] is True for item in (
                    "exclusive_creation", "nofollow", "file_fsync",
                    "same_inode_readback_verified",
                )), "require the exact nine-field original nested file_fsync owner")
    elif kind == "worker":
        require(type(value["device"]) is int and value["device"] >= 0
                and type(value["inode"]) is int and value["inode"] > 0
                and all(value[item] is True for item in (
                    "exclusive_creation", "file_fsync_completed",
                    "same_inode_readback_verified",
                )), "require the exact eight-field V7 worker publication owner")
    else:
        require(type(value["actual_write_calls"]) is int
                and value["actual_write_calls"] > 0
                and type(value["uncompressed_bytes"]) is int
                and 0 < value["uncompressed_bytes"] <= MAX_SPECIALIZED_BYTES
                and value["compression"] in {"none", "gzip-mtime-zero-level-9"}
                and all(value[item] is True for item in (
                    "atomic_no_overwrite_link", "complete_readback_verified",
                    "directory_fsync_completed", "file_fsync_completed",
                    "owned_temporary_removed",
                )), "require the exact twelve-field specialized recorder owner")
        checked_digest(value["uncompressed_sha256"], relative + " decoded owner")
    return value


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, operation: Callable[[], Any]) -> Any:
        try:
            result = operation()
        except Exception as error:
            raise CandidateGateError("genuine V7 source control failed: " + name) from error
        accepted.append(name)
        return result

    def reject(name: str, operation: Callable[[], Any]) -> None:
        try:
            operation()
        except (CandidateGateError, SourceOnlyEffect, TypeError, ValueError,
                KeyError, UnicodeError, RecursionError, OverflowError, OSError):
            rejected.append(name)
            return
        raise CandidateGateError("unsafe V7 source control was accepted: " + name)

    with source_only_boundary() as effects:
        frozen = accept("exact-independently-frozen-full-v7-protocol",
                        lambda: validate_protocol_document(protocol_document()))
        accept("all-thirteen-original-suites-and-all-31237-cases",
               lambda: require(len(FROZEN_SUITES) == SUITE_COUNT
                               and sum(suite.case_count for suite in FROZEN_SUITES)
                               == CASE_DENOMINATOR,
                               "preserve all genuinely runnable original cases"))
        accept("six-independent-source-families-twenty-five-disjoint-owners",
               lambda: require(frozen["six_family_independence"]["family_count"] == 6
                               and frozen["six_family_independence"]["complete_source_owner_count"] == 25
                               and frozen["six_family_independence"]["external_regex_package_count"] == 0,
                               "require the complete from-scratch source independence audit"))
        campaigns = frozen["preserved_historical_campaigns"]
        accept("all-fifty-seven-real-historical-evidence-owners",
               lambda: require(sum(len(campaigns[name]["artifacts"])
                                   for name in ("c", "rust", "zig")) == 51
                               and campaigns["candidate_artifact_count_including_restorations"] == 51
                               and campaigns["total_artifact_count_including_source_builds"] == 57
                               and frozen["preserved_v4_source_builds"]["artifact_count"] == 6,
                               "retain all 51 real candidate owners and all six genuine V4 build owners"))
        accept("passing-cases-never-mean-a-qualified-candidate",
               lambda: require(all(campaigns[name]["candidate_qualified"] is False
                                   for name in ("c", "rust", "zig"))
                               and campaigns["zig"]["verified_passing_case_count"] == 3583
                               and frozen["fully_qualified_candidate_count"] == 0,
                               "a partially passing candidate is never qualified"))
        accept("genuine-385-failed-interpreter-calls-qualify-zero-cases",
               lambda: require(campaigns["zig"]["nested_case_interpreter_exec_calls"] == 385
                               and campaigns["zig"]["nested_original_cases_qualified"] == 0
                               and campaigns["zig"]["nested_cleanup_failure_count"] == 3,
                               "preserve real interpreter cleanup failure honestly"))
        accept("preserve-full-forty-three-megabyte-shape-archive",
               lambda: require(MAX_SPECIALIZED_BYTES == 64 * 1024 * 1024
                               and MAX_REPORT_BYTES == 32 * 1024 * 1024,
                               "distinguish specialist inputs from bounded V7 outputs"))
        accept("accept-exact-strictly-bounded-deterministic-gzip",
               lambda: require(bounded_gzip(gzip.compress(b"v7-proof", mtime=0),
                                            "synthetic original archive", maximum=8)
                               == b"v7-proof",
                               "validate exact complete synthetic bounded original archive"))
        reject("reject-oversized-real-decompression-before-source-validation",
               lambda: bounded_gzip(gzip.compress(b"ninebytes", mtime=0),
                                    "oversized synthetic archive", maximum=8))
        reject("reject-duplicate-json-evidence-keys",
               lambda: decode_document(b'{"owner":1,"owner":2}\n',
                                       "synthetic duplicate owner"))
        reject("reject-non-finite-json-evidence",
               lambda: decode_document(b'{"owner":NaN}\n',
                                       "synthetic non-finite owner"))
        accept("freeze-exact-v3-activation-without-inventing-a-candidate",
               lambda: require(frozen["future_six_family_v4_build"]["activation_source_sha256"]
                               == FUTURE_ACTIVATION_SHA256
                               and frozen["future_six_family_v4_build"]["activation_protocol_sha256"]
                               == FUTURE_ACTIVATION_PROTOCOL_SHA256
                               and frozen["future_six_family_v4_build"]["activation_document_sha256"]
                               == FUTURE_ACTIVATION_DOCUMENT_SHA256
                               and frozen["future_six_family_v4_build"]["actual_v3_activation_count"] == 0
                               and frozen["future_six_family_v4_build"]["future_candidate_runs_authorized"] is False,
                               "a source build or frozen activator never proves matching"))
        accept("distinguish-six-source-families-from-three-runnable-p0-families",
               lambda: require(frozen["source_family_count"] == 6
                               and frozen["fully_runnable_p0_family_count"] == 3
                               and frozen["fully_qualified_candidate_count"] == 0,
                               "do not invent a frozen six-family original correctness producer"))
        accept("preserve-genuine-cpp-build-without-inventing-correctness",
               lambda: require(frozen["preserved_v4_source_builds"]["cpp"]["status"] == "PASS"
                               and frozen["preserved_v4_source_builds"]["cpp"]["phase_count"] == 2
                               and frozen["preserved_v4_source_builds"]["cpp"]["process_count"] == 10
                               and frozen["preserved_v4_source_builds"]["cpp"]["candidate_correctness"]
                               == "NOT MEASURED"
                               and frozen["preserved_v4_source_builds"]["cpp"]["candidate_matching_cases_executed"] == 0,
                               "a reproducible C++ build is not an executed regex candidate"))
        accept("preserve-genuine-go-build-failure-without-promoting-receipt",
               lambda: require(frozen["preserved_v4_source_builds"]["go"]["status"] == "FAIL"
                               and frozen["preserved_v4_source_builds"]["go"]["build_status"] == "FAIL"
                               and frozen["preserved_v4_source_builds"]["go"]["receipt_status"] == "PASS"
                               and frozen["preserved_v4_source_builds"]["go"]["process_count"] == 4
                               and frozen["preserved_v4_source_builds"]["go"]["phase_count"] == 0
                               and frozen["preserved_v4_source_builds"]["go"]["generated_header_status"]
                               == "NOT GENERATED",
                               "a written Go failure receipt cannot make a Go build pass"))
        accept("preserve-genuine-fortran-reproducibility-failure",
               lambda: require(frozen["preserved_v4_source_builds"]["fortran"]["status"] == "FAIL"
                               and frozen["preserved_v4_source_builds"]["fortran"]["build_status"] == "FAIL"
                               and frozen["preserved_v4_source_builds"]["fortran"]["receipt_status"] == "PASS"
                               and frozen["preserved_v4_source_builds"]["fortran"]["process_count"] == 18
                               and frozen["preserved_v4_source_builds"]["fortran"]["phase_count"] == 2
                               and frozen["preserved_v4_source_builds"]["fortran"]["first_engine_sha256"]
                               != frozen["preserved_v4_source_builds"]["fortran"]["second_engine_sha256"],
                               "preserve both actual complete nonreproducible Fortran build phases"))
        accept("separate-71-v2-plus-v4-processes-from-15-v3-zig-processes",
               lambda: require(frozen["historical_source_build_process_accounting"]["v2_source_build_process_count"] == 39
                               and frozen["historical_source_build_process_accounting"]["v4_source_build_process_count"] == 32
                               and frozen["historical_source_build_process_accounting"]["v2_plus_v4_source_build_process_count"] == 71
                               and frozen["historical_source_build_process_accounting"]["separately_preserved_successful_v3_zig_source_build_process_count"] == 15
                               and frozen["historical_source_build_process_accounting"]["v2_plus_v3_plus_v4_source_build_process_count"] == 86
                               and frozen["historical_source_build_process_accounting"]["process_id_uniqueness_claimed_across_independent_runs"] is False,
                               "never conflate independent real historical compiler process denominators"))
        sha = "a" * 64
        nested_owner = {"relative": "oracle/phase2/evidence/synthetic.json.gz",
                        "sha256": sha, "bytes": 12, "device": 1, "inode": 2,
                        "exclusive_creation": True, "nofollow": True,
                        "file_fsync": True, "same_inode_readback_verified": True}
        worker_owner = {"relative": "oracle/phase2/evidence/synthetic.json.gz",
                        "sha256": sha, "bytes": 12, "device": 1, "inode": 2,
                        "exclusive_creation": True, "file_fsync_completed": True,
                        "same_inode_readback_verified": True}
        specialist_owner = {
            "path": "oracle/phase2/evidence/synthetic.json.gz",
            "sha256": sha, "bytes": 12, "uncompressed_bytes": 48,
            "uncompressed_sha256": sha, "compression": "gzip-mtime-zero-level-9",
            "actual_write_calls": 1, "atomic_no_overwrite_link": True,
            "complete_readback_verified": True, "directory_fsync_completed": True,
            "file_fsync_completed": True, "owned_temporary_removed": True,
        }
        for kind, owner in (("nested", nested_owner),
                            ("worker", worker_owner),
                            ("specialized", specialist_owner)):
            accept("accept-only-exact-original-" + kind + "-owner",
                   lambda kind=kind, owner=owner:
                   check_publication_shape(owner, kind=kind,
                                           relative="oracle/phase2/evidence/synthetic.json.gz"))
            for key in tuple(owner):
                reject("reject-omitted-" + kind + "-" + key,
                       lambda kind=kind, owner=owner, key=key:
                       check_publication_shape({name: value for name, value in owner.items()
                                                if name != key}, kind=kind,
                                               relative="oracle/phase2/evidence/synthetic.json.gz"))
        reject("reject-specialized-file-fsync-as-original-nested-proof",
               lambda: check_publication_shape(
                   {**{name: value for name, value in nested_owner.items()
                       if name != "file_fsync"}, "file_fsync_completed": True},
                   kind="nested", relative=nested_owner["relative"]))
        reject("reject-nested-file-fsync-as-v7-worker-proof",
               lambda: check_publication_shape(
                   {**{name: value for name, value in worker_owner.items()
                       if name != "file_fsync_completed"}, "file_fsync": True},
                   kind="worker", relative=worker_owner["relative"]))
        for field in frozen:
            def mutate(field: str = field) -> Any:
                forged = protocol_document()
                value = forged[field]
                if type(value) is bool:
                    forged[field] = not value
                elif type(value) is int:
                    forged[field] = value + 1
                elif type(value) is dict:
                    forged[field] = {**value, "forged": True}
                elif type(value) is list:
                    forged[field] = value[:-1]
                else:
                    forged[field] = str(value) + "-forged"
                return validate_protocol_document(forged)
            reject("reject-altered-complete-v7-" + field, mutate)
        for index, spec in enumerate(FROZEN_SUITES):
            for field in ("id", "case_count", "source_path", "source_sha256",
                          "matrix_sha256", "reference_records_sha256",
                          "published_seed"):
                def forge_suite(index: int = index, field: str = field) -> Any:
                    forged = protocol_document()
                    value = forged["suites"][index][field]
                    if type(value) is int:
                        forged["suites"][index][field] = value + 1
                    elif value is None:
                        forged["suites"][index][field] = 0
                    else:
                        forged["suites"][index][field] = str(value) + "-forged"
                    return validate_protocol_document(forged)
                reject("reject-altered-" + spec.name + "-" + field,
                       forge_suite)
        for family in SOURCE_FAMILIES:
            reject("reject-invented-runnable-original-producer-" + family,
                   lambda family=family: validate_protocol_document({
                       **protocol_document(),
                       "fully_runnable_p0_family_count":
                       4 if family in FUTURE_FAMILIES else 2,
                   }))
        for family in ("c", "rust", "zig"):
            for index, item in enumerate(campaigns[family]["artifacts"]):
                def forge_owner(family: str = family, index: int = index) -> Any:
                    forged = protocol_document()
                    forged["preserved_historical_campaigns"][family]["artifacts"][index]["sha256"] = sha
                    return validate_protocol_document(forged)
                reject("reject-altered-historical-" + family + "-owner-" + str(index),
                       forge_owner)
        for family in ("cpp", "go", "fortran"):
            for field in ("archive_sha256", "receipt_sha256"):
                def forge_build(family: str = family, field: str = field) -> Any:
                    forged = protocol_document()
                    forged["preserved_v4_source_builds"][family][field] = sha
                    return validate_protocol_document(forged)
                reject("reject-altered-historical-v4-" + family + "-" + field,
                       forge_build)
        for name, operation in (
            ("real-file-read", lambda: builtins.open("GOAL.md", "rb")),
            ("real-descriptor", lambda: os.open("GOAL.md", os.O_RDONLY)),
            ("real-candidate-process", lambda: subprocess.Popen([PINNED_PYTHON])),
            ("real-candidate-import", lambda: importlib.import_module("candidates")),
            ("real-clock", lambda: time.perf_counter()),
            ("real-native-promotion", lambda: os.replace("v7-a", "v7-b")),
            ("real-network", lambda: socket.create_connection(("127.0.0.1", 1))),
            ("real-temporary-file", lambda: tempfile.mkstemp()),
        ):
            reject("reject-" + name, operation)
        reject("reject-integer-in-place-of-exact-true",
               lambda: require(1, "only the literal true qualifies an obligation"))
    for name in ("file_reads", "file_writes", "candidate_imports",
                 "candidate_workers", "reference_workers", "source_builds",
                 "native_promotions", "native_libraries_loaded",
                 "interpreter_creations", "thread_starts", "network_requests",
                 "clock_samples", "hidden_cases_read", "benchmark_files_read"):
        require(effects[name] == 0,
                "a synthetic V7 check caused a real external effect: " + name)
    return {"schema": SCHEMA + "-source-self-test", "status": "PASS",
            "synthetic": True, "accepted_count": len(accepted),
            "rejected_count": len(rejected), "accepted": accepted,
            "rejected": rejected, "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "preserved_historical_candidate_artifact_count": 51,
            "preserved_historical_artifact_count_including_source_builds": 57,
            "source_family_count": 6,
            "fully_runnable_p0_family_count": 3,
            "candidate_qualified_count": 0,
            "fully_qualified_candidate_count": 0,
            "source_only_effects": effects, "actual_candidate_workers": 0,
            "actual_reference_workers": 0, "actual_source_builds": 0,
            "actual_native_promotions": 0, "benchmark_files_read": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "performance": "NOT MEASURED",
            "final_holdout_authorized": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False}


def v6_options(options: argparse.Namespace, *, readonly: bool) -> argparse.Namespace:
    base = importlib.import_module("tools.run_frozen_p0_candidate_worker_v4")
    require(getattr(base, "SCHEMA", None)
            == "rebar-frozen-python-re-p0-candidate-worker-v4"
            and getattr(base, "CASE_DENOMINATOR", None) == CASE_DENOMINATOR,
            "load only the exactly pinned original immutable V6 validator")
    arguments = ["--verify-frozen-context" if readonly else
                 "--internal-candidate-worker" if options.internal_candidate_worker
                 else "--run",
                 "--source-sha256", V6_WORKER_SHA256,
                 "--protocol-sha256", V6_PROTOCOL_SHA256,
                 "--document-sha256", V6_DOCUMENT_SHA256]
    if not readonly:
        for name in ("candidate", "label", "build_version", "build_label",
                     "activation_root", "build_source_sha256",
                     "build_protocol_sha256", "build_archive_sha256",
                     "build_receipt_sha256", "activation_source_sha256",
                     "activation_protocol_sha256", "activation_report_sha256",
                     "activation_receipt_sha256", "candidate_source_sha256",
                     "native_engine_sha256", "native_bridge_sha256"):
            value = getattr(options, name)
            require(type(value) is str and bool(value),
                    "bind all genuine original V6 activation proof: " + name)
            arguments.extend(("--" + name.replace("_", "-"), value))
        if options.recovery_journal_sha256 is not None:
            arguments.extend(("--recovery-journal-sha256",
                              options.recovery_journal_sha256))
        for value in options.owned_source_sha256:
            arguments.extend(("--owned-source-sha256", value))
        if options.internal_candidate_worker:
            arguments.extend(("--suite", options.suite))
    return base.parse_arguments(arguments)


def pinned_v7_owners(options: argparse.Namespace,
                     base: types.ModuleType,
                     allowed: frozenset[str]) -> dict[str, dict[str, Any]]:
    selected = (
        (SOURCE_RELATIVE, options.source_sha256),
        (PROTOCOL_RELATIVE, options.protocol_sha256),
        (DOCUMENT_RELATIVE, options.document_sha256),
    )
    results: dict[str, dict[str, Any]] = {}
    for relative, fingerprint in selected:
        require(fingerprint is not None,
                "explicitly pin all independently committed V7 source owners")
        raw, owner = base.read_owned(relative, checked_digest(fingerprint, relative),
                                     allowed=allowed, maximum=MAX_SOURCE_BYTES)
        if relative == DOCUMENT_RELATIVE:
            validate_protocol_document(decode_document(raw,
                                                        "complete exact V7 machine protocol",
                                                        canonical_required=True))
        results[relative] = owner
    return results


def nested_publication(value: Any, relative: str, *, compressed: bool,
                       base: types.ModuleType,
                       allowed: frozenset[str]) -> tuple[bytes, dict[str, Any]]:
    proof = check_publication_shape(value, kind="nested", relative=relative)
    raw, owner = base.read_owned(relative, proof["sha256"], allowed=allowed,
                                 maximum=MAX_ARCHIVE_BYTES if compressed
                                 else MAX_SOURCE_BYTES)
    require(len(raw) == proof["bytes"]
            and owner["device"] == proof["device"]
            and owner["inode"] == proof["inode"],
            "bind the exact genuine nested archive to its authenticated inode")
    return raw, owner


def validate_nested_result(value: Any, suite: SuiteSpec,
                           options: argparse.Namespace,
                           context: Mapping[str, Any],
                           approval: Mapping[str, Any] | None,
                           producer_exit: int) -> dict[str, Any]:
    base = context["v6_worker"]
    require(suite.name == "subinterpreter_v2" and type(value) is dict
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
            "require the genuine published nested V3 result and actual process status")
    archive_path, receipt_path = base.nested_evidence_paths(
        options.candidate, options.label, version="3",
        failure=value["status"] == "FAIL")
    allowed = frozenset({*context["allowed_paths"], archive_path, receipt_path})
    compressed, archive_owner = nested_publication(
        value.get("archive"), archive_path, compressed=True,
        base=base, allowed=allowed)
    receipt_raw, receipt_owner = nested_publication(
        value.get("receipt"), receipt_path, compressed=False,
        base=base, allowed=allowed)
    plain = bounded_gzip(compressed, archive_path, maximum=MAX_NESTED_BYTES)
    full = decode_document(plain, archive_path, maximum=MAX_NESTED_BYTES)
    receipt = decode_document(receipt_raw, receipt_path, canonical_required=True)
    require(full.get("schema")
            == "rebar-owned-candidate-subinterpreters-v3-candidate-evaluation"
            and full.get("status") == value["status"]
            and full.get("candidate_family") == options.candidate
            and full.get("build_version") == str(options.build_version)
            and full.get("label") == options.label + "-subinterpreters"
            and full.get("source_sha256") == NESTED_V3_SHA256
            and full.get("protocol_sha256") == NESTED_V3_DOCUMENT_SHA256
            and full.get("explanation_sha256") == NESTED_V3_PROTOCOL_SHA256
            and full.get("phase1_case_execution_denominator") == CASE_DENOMINATOR
            and full.get("supplemental_cases_added_to_phase1_denominator") is False
            and receipt.get("schema")
            == "rebar-owned-candidate-subinterpreters-v3-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("result_status") == full["status"]
            and receipt.get("candidate_family") == options.candidate
            and receipt.get("build_version") == str(options.build_version)
            and receipt.get("label") == options.label + "-subinterpreters"
            and receipt.get("archive_relative") == archive_path
            and receipt.get("archive_sha256") == archive_owner["sha256"]
            and receipt.get("archive_bytes") == len(compressed)
            and receipt.get("archive_publication") == value["archive"]
            and receipt.get("archive_directory_fsync_completed") is True
            and receipt.get("uncompressed_bytes") == len(plain)
            and receipt.get("uncompressed_sha256")
            == hashlib.sha256(plain).hexdigest()
            and receipt.get("supplemental_cases_added_to_phase1_denominator") is False,
            "authenticate original nested archive, receipt, full source and status")
    if full["status"] == "FAIL":
        process = full.get("worker_process")
        failure = full.get("failure")
        require(full.get("worker") is None and type(process) is dict
                and type(process.get("pid")) is int and process["pid"] > 0
                and process.get("timed_out") is False
                and process.get("returncode") == 1
                and process.get("process_reaped") is True
                and type(failure) is dict
                and failure.get("pid") == process["pid"]
                and failure.get("returncode") == 1,
                "retain the genuine complete failed interpreter process and cleanup")
        stdout = base.restore_stream(process.get("stdout"),
                                     "complete failed nested V3 worker stdout")
        require(len(stdout) <= MAX_NESTED_BYTES
                and base.restore_stream(process.get("stderr"),
                                        "complete failed nested V3 worker stderr") == b"",
                "retain the exact whole genuine failed nested worker streams")
        child = decode_document(stdout, "full authentic nested V3 failure",
                                maximum=MAX_NESTED_BYTES)
        actual = child.get("actual_failure")
        require(child.get("schema")
                == "rebar-owned-candidate-subinterpreters-v3-entry-failure"
                and child.get("status") == "FAIL" and type(actual) is dict
                and actual.get("status") == "FAIL"
                and actual.get("candidate_family") == options.candidate
                and actual.get("build_version") == str(options.build_version)
                and child.get("performance") == "NOT MEASURED"
                and child.get("clock_samples") == 0
                and child.get("benchmark_files_read") == 0
                and child.get("hidden_cases_read") == 0,
                "decode the real complete original nested child failure")
        fields = ("actual_case_interpreter_exec_calls",
                  "actual_initialization_interpreter_exec_calls",
                  "actual_guard_cleanup_interpreter_exec_calls",
                  "actual_interpreters_created", "actual_interpreters_destroyed")
        counts = {field: checked_count(actual.get(field), 10_000, field)
                  for field in fields}
        ledgers = actual.get("pipe_ledgers")
        cleanup = actual.get("cleanup_failures")
        require(type(ledgers) is list
                and len(ledgers) == counts["actual_case_interpreter_exec_calls"]
                and type(cleanup) is list and bool(cleanup)
                and type(actual.get("actual_prepared_interpreter_ids")) is list
                and len(actual["actual_prepared_interpreter_ids"])
                == counts["actual_interpreters_created"]
                and counts["actual_interpreters_destroyed"]
                <= counts["actual_interpreters_created"]
                and full.get("actual_successful_supplemental_cases") == 0,
                "preserve the exact actual failed execution and cleanup ledgers")
        return {"actual_candidate_case_count": 0,
                "verified_passing_case_count": 0,
                "actual_candidate_workers": 1,
                "candidate_records_location": archive_owner,
                "candidate_publication_receipt": receipt_owner,
                **counts, "actual_cleanup_failure_count": len(cleanup),
                "complete_nested_failure_stdout_bytes": len(stdout),
                "complete_nested_failure_stdout_sha256":
                hashlib.sha256(stdout).hexdigest(),
                "actual_nested_failure": actual,
                "mismatch_count": 0, "all_mismatches": [],
                "all_failure_reasons": [failure, actual],
                "source_owned_candidate_status": "FAIL",
                "source_owned_publication_status": "PASS"}
    require(type(approval) is dict,
            "a passing interpreter requires authentic current native activation")
    base_options = context["v6_options"]
    nested = context["nested"]
    nested_arguments = base.nested_arguments(base_options, approval)
    arguments = nested.parse_arguments(nested_arguments)
    nested_context = nested.authenticate_prerequisites(arguments)
    baseline = nested_context["original"].load_original_baseline()
    worker = full.get("worker")
    require(type(worker) is dict and type(worker.get("pid")) is int,
            "require the complete actual passing interpreter worker")
    proved = nested.validate_actual_worker(worker, context=nested_context,
                                          baseline=baseline,
                                          expected_pid=worker["pid"])
    require(proved == worker and worker.get("case_count") == suite.case_count
            and worker.get("actual_case_interpreter_exec_calls") == 394
            and worker.get("actual_initialization_interpreter_exec_calls") == 11
            and worker.get("actual_guard_cleanup_interpreter_exec_calls") == 11
            and worker.get("actual_interpreters_created") == 11
            and worker.get("actual_interpreters_destroyed") == 11
            and worker.get("reference_records_sha256") == suite.reference_sha256
            and worker.get("projected_reference_records_sha256")
            == PROJECTED_REFERENCE_SHA256
            and all(worker.get(name) is True for name in (
                "all_real_pipes_read_to_eof", "all_real_pipe_descriptors_closed",
                "interpreter_live_set_restored", "locale_restored",
                "simultaneous_interpreters_verified",
                "b_closed_before_a_reexecution", "fresh_c_verified",
                "persistent_original_v5_per_interpreter")),
            "qualify exactly 128 original interpreter cases only after 394 real calls")
    return {"actual_candidate_case_count": suite.case_count,
            "verified_passing_case_count": suite.case_count,
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
            "mismatch_count": 0, "all_mismatches": [],
            "all_failure_reasons": [], "source_owned_candidate_status": "PASS",
            "source_owned_publication_status": "PASS"}


def historical_zig_options() -> argparse.Namespace:
    return argparse.Namespace(
        candidate="zig", label="phase2-v6", build_version="3",
        candidate_source_sha256=
        "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
        native_engine_sha256=
        "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071",
        native_bridge_sha256=
        "c579cf52b767b84ecc3d0a60f837d526978ace4e7739fe4cf51c2d2c8cfd90d9",
        owned_source_sha256=[
            "candidates/zig_candidate.py="
            "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
            "candidates/zig/mini_regex.zig="
            "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
            "candidates/zig/py_bridge.c="
            "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b",
        ],
    )


def check_historical_receipt(raw: bytes, *, schema: str, source: str,
                             archive_path: str, compressed: bytes,
                             plain: bytes) -> dict[str, Any]:
    receipt = decode_document(raw, schema + " full historical receipt",
                              canonical_required=True)
    proof = check_publication_shape(receipt.get("archive"), kind="worker",
                                    relative=archive_path)
    require(receipt.get("schema") == schema + "-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("failure_preserved") is True
            and receipt.get("candidate_family") == "zig"
            and receipt.get("label") == "phase2-v6"
            and receipt.get("source_sha256") == source
            and receipt.get("protocol_sha256") == V6_PROTOCOL_SHA256
            and receipt.get("document_sha256") == V6_DOCUMENT_SHA256
            and proof["bytes"] == len(compressed)
            and proof["sha256"] == hashlib.sha256(compressed).hexdigest()
            and receipt.get("uncompressed_bytes") == len(plain)
            and receipt.get("uncompressed_sha256")
            == hashlib.sha256(plain).hexdigest()
            and receipt.get("archive_directory_fsync_completed") is True
            and receipt.get("benchmark_files_read") == 0
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("final_winner_selected") is False,
            "a real publication PASS never changes the historical candidate FAIL")
    return receipt


def authenticate_specialized_publications(
    value: Mapping[str, Any], suite: SuiteSpec,
    options: argparse.Namespace, context: Mapping[str, Any],
) -> None:
    base = context["v6_worker"]
    original = base.suite_spec(suite.name)
    archive_path, receipt_path = base.specialized_evidence_paths(
        original, options.candidate, options.label)
    archive = check_publication_shape(value.get("report_publication"),
                                      kind="specialized", relative=archive_path)
    receipt = check_publication_shape(value.get("receipt_publication"),
                                      kind="specialized", relative=receipt_path)
    require(archive["compression"] == "gzip-mtime-zero-level-9"
            and receipt["compression"] == "none",
            "reject swapped original specialized archive and receipt codecs")
    allowed = frozenset({*context["allowed_paths"], archive_path, receipt_path})
    raw, _ = base.read_owned(archive_path, archive["sha256"], allowed=allowed,
                             maximum=MAX_ARCHIVE_BYTES)
    require(len(raw) == archive["bytes"],
            "authenticate every compressed original specialist owner byte")
    plain = bounded_gzip(raw, archive_path, maximum=MAX_SPECIALIZED_BYTES)
    require(len(plain) == archive["uncompressed_bytes"]
            and hashlib.sha256(plain).hexdigest()
            == archive["uncompressed_sha256"],
            "apply the genuine independent 64-MiB inbound specialist ceiling")
    receipt_raw, _ = base.read_owned(receipt_path, receipt["sha256"],
                                     allowed=allowed, maximum=MAX_SOURCE_BYTES)
    require(len(receipt_raw) == receipt["bytes"]
            and len(receipt_raw) == receipt["uncompressed_bytes"]
            and hashlib.sha256(receipt_raw).hexdigest()
            == receipt["uncompressed_sha256"],
            "authenticate the complete original specialized durable receipt")


def authenticate_historical_zig(context: dict[str, Any]) -> dict[str, Any]:
    base = context["v6_worker"]
    allowed = frozenset({*context["allowed_paths"], *HISTORICAL_ZIG_OWNERS})
    owners: dict[str, dict[str, Any]] = {}
    raw_owners: dict[str, bytes] = {}
    for relative, fingerprint in sorted(HISTORICAL_ZIG_OWNERS.items()):
        maximum = MAX_ARCHIVE_BYTES if relative.endswith(".json.gz") else MAX_SOURCE_BYTES
        raw, owner = base.read_owned(relative, fingerprint, allowed=allowed,
                                     maximum=maximum)
        owners[relative], raw_owners[relative] = owner, raw
    worker_archive = (
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v4-"
        "zig-phase2-v6-failures.json.gz")
    worker_receipt = worker_archive.removesuffix(".json.gz") + "-publication-receipt.json"
    worker_plain = bounded_gzip(raw_owners[worker_archive], worker_archive,
                                maximum=MAX_REPORT_BYTES)
    worker = decode_document(worker_plain, "complete genuine historical Zig V6 worker",
                             maximum=MAX_REPORT_BYTES)
    check_historical_receipt(raw_owners[worker_receipt],
                             schema="rebar-frozen-python-re-p0-candidate-worker-v4",
                             source=V6_WORKER_SHA256,
                             archive_path=worker_archive,
                             compressed=raw_owners[worker_archive],
                             plain=worker_plain)
    suites = worker.get("all_suites")
    require(worker.get("schema")
            == "rebar-frozen-python-re-p0-candidate-worker-v4-complete-candidate-evaluation"
            and worker.get("status") == "FAIL"
            and worker.get("candidate_family") == "zig"
            and worker.get("label") == "phase2-v6"
            and worker.get("source_sha256") == V6_WORKER_SHA256
            and worker.get("protocol_sha256") == V6_PROTOCOL_SHA256
            and worker.get("document_sha256") == V6_DOCUMENT_SHA256
            and worker.get("build_version") == "3"
            and worker.get("phase1_inventory_sha256") == PHASE1_SHA256
            and worker.get("suite_count") == SUITE_COUNT
            and worker.get("case_execution_denominator") == CASE_DENOMINATOR
            and worker.get("attempted_candidate_suite_count") == SUITE_COUNT
            and worker.get("completed_candidate_suite_count") == 6
            and worker.get("qualified_candidate_case_executions") == 3583
            and worker.get("actual_semantic_mismatch_count") == 1764
            and worker.get("candidate_qualified") is False
            and worker.get("performance") == "NOT MEASURED"
            and worker.get("clock_samples") == 0
            and worker.get("benchmark_files_read") == 0
            and worker.get("hidden_cases_read") == 0
            and worker.get("final_holdout_authorized") is False
            and worker.get("final_winner_selected") is False
            and type(suites) is list and len(suites) == SUITE_COUNT
            and [row.get("suite") for row in suites]
            == [suite.name for suite in FROZEN_SUITES],
            "preserve the actual whole failed thirteen-suite Zig V6 campaign")
    options = historical_zig_options()
    observed: list[dict[str, Any]] = []
    for spec, row in zip(FROZEN_SUITES, suites, strict=True):
        process = row.get("actual_process")
        require(type(row) is dict and row.get("suite") == spec.name
                and row.get("candidate_family") == "zig"
                and row.get("case_execution_denominator") == spec.case_count
                and row.get("matrix_sha256") == spec.matrix_sha256
                and row.get("reference_records_sha256") == spec.reference_sha256
                and type(process) is dict and process.get("timed_out") is False
                and process.get("returncode") in {0, 1}
                and base.restore_stream(process.get("stderr"),
                                        spec.name + " genuine historical stderr") == b"",
                "independently retain each complete actual historical suite")
        child = decode_document(base.restore_stream(
            process.get("stdout"), spec.name + " genuine historical stdout"),
            spec.name + " genuine historical producer", maximum=MAX_PROCESS_BYTES)
        if spec.recorder_relative is not None:
            base_spec = base.suite_spec(spec.name)
            authenticate_specialized_publications(child, spec, options, context)
            exact = base.validate_specialized_result(
                child, base_spec, options, context, process["returncode"])
        elif spec.name == "subinterpreter_v2":
            exact = validate_nested_result(child, spec, options, context, None,
                                           process["returncode"])
            failure = row.get("failure")
            require(type(failure) is dict
                    and failure.get("type") == "CandidateGateError"
                    and failure.get("message")
                    == "authenticate original nested exclusive same-inode publication"
                    and exact["actual_case_interpreter_exec_calls"] == 385
                    and exact["actual_initialization_interpreter_exec_calls"] == 3
                    and exact["actual_guard_cleanup_interpreter_exec_calls"] == 4
                    and exact["actual_interpreters_created"] == 3
                    and exact["actual_interpreters_destroyed"] == 3
                    and exact["actual_cleanup_failure_count"] == 3
                    and exact["complete_nested_failure_stdout_bytes"] == 1_126_801
                    and exact["complete_nested_failure_stdout_sha256"]
                    == "2da4af1e62facbe6565bb127a0920f647ec04c3f0005d02f58b233229277721d"
                    and exact["actual_candidate_case_count"] == 0,
                    "retain the real cleanup failure and diagnose the separate V6 owner bug")
        elif spec.name in {"public_surface_v19", "pep688_v4",
                           "threaded_pattern_v1"}:
            exact = base.validate_direct_result(child, base.suite_spec(spec.name),
                                                options, context,
                                                process["returncode"])
        elif spec.name == "original_bounded_v5":
            require(process["returncode"] == 0,
                    "retain the actually passing original historical test process")
            exact = context["legacy_worker"].validate_original_result(
                child, context["legacy_worker"].suite_spec(spec.name), options)
            exact.update(actual_candidate_workers=1, mismatch_count=0,
                         all_mismatches=[], all_failure_reasons=[])
        else:
            exact = base.validate_category_result(child, base.suite_spec(spec.name),
                                                  options, context,
                                                  process["returncode"])
        expected_mismatches = ZIG_MISMATCH_COUNTS.get(spec.name, 0)
        require(exact.get("mismatch_count") == expected_mismatches
                and row.get("mismatch_count") == expected_mismatches
                and (row.get("status") == "PASS")
                is (expected_mismatches == 0 and spec.name != "subinterpreter_v2")
                and row.get("actual_candidate_case_count")
                == (0 if spec.name == "subinterpreter_v2" else spec.case_count),
                "preserve each complete real historical candidate outcome")
        if spec.name != "subinterpreter_v2":
            require(row.get("all_mismatches") == exact.get("all_mismatches"),
                    "reconstruct every exact genuine historical semantic mismatch")
        observed.append({"suite": spec.name, "status": row["status"],
                         "case_count": spec.case_count,
                         "verified_passing_case_count":
                         spec.case_count if row["status"] == "PASS" else 0,
                         "actual_semantic_mismatch_count": expected_mismatches,
                         "actual_case_interpreter_exec_calls":
                         exact.get("actual_case_interpreter_exec_calls", 0),
                         "all_mismatches_sha256": digest(exact.get("all_mismatches", []))})
    outer_archive = (
        "oracle/phase2/evidence/frozen-p0-candidate-v6-"
        "zig-phase2-v6-failures.json.gz")
    outer_receipt = outer_archive.removesuffix(".json.gz") + "-publication-receipt.json"
    outer_plain = bounded_gzip(raw_owners[outer_archive], outer_archive,
                               maximum=MAX_REPORT_BYTES)
    outer = decode_document(outer_plain, "complete genuine historical Zig V6 runner",
                            maximum=MAX_REPORT_BYTES)
    check_historical_receipt(raw_owners[outer_receipt],
                             schema="rebar-frozen-python-re-p0-candidate-v6",
                             source=V6_RUNNER_SHA256, archive_path=outer_archive,
                             compressed=raw_owners[outer_archive], plain=outer_plain)
    require(outer.get("schema")
            == "rebar-frozen-python-re-p0-candidate-v6-actual-complete-candidate"
            and outer.get("status") == "FAIL"
            and outer.get("candidate_family") == "zig"
            and outer.get("label") == "phase2-v6"
            and outer.get("source_sha256") == V6_RUNNER_SHA256
            and outer.get("worker_source_sha256") == V6_WORKER_SHA256
            and outer.get("protocol_sha256") == V6_PROTOCOL_SHA256
            and outer.get("document_sha256") == V6_DOCUMENT_SHA256
            and outer.get("suite_count") == SUITE_COUNT
            and outer.get("case_execution_denominator") == CASE_DENOMINATOR
            and outer.get("completed_candidate_suite_count") == 6
            and outer.get("qualified_candidate_case_executions") == 3583
            and outer.get("actual_semantic_mismatch_count") == 1764
            and outer.get("candidate_qualified") is False
            and outer.get("all_suites") == suites
            and outer.get("worker_complete_archive", {}).get("sha256")
            == HISTORICAL_ZIG_OWNERS[worker_archive]
            and outer.get("worker_complete_publication_receipt", {}).get("sha256")
            == HISTORICAL_ZIG_OWNERS[worker_receipt]
            and outer.get("hidden_cases_read") == 0
            and outer.get("benchmark_files_read") == 0
            and outer.get("clock_samples") == 0
            and outer.get("performance") == "NOT MEASURED",
            "cross-check the real Zig runner and worker without rerunning either")
    restoration_path = (
        "oracle/phase2/evidence/frozen-p0-candidate-v6-"
        "zig-phase2-v6-restoration-receipt.json")
    restoration = decode_document(raw_owners[restoration_path], restoration_path,
                                  canonical_required=True)
    require(restoration.get("schema")
            == "rebar-phase2-verified-native-candidate-activation-v2-restoration-receipt"
            and restoration.get("status") == "PASS"
            and restoration.get("family") == "zig"
            and restoration.get("build_version") == "3"
            and restoration.get("candidate_import_root") == str(ROOT)
            and restoration.get("candidate_processes_started") == 0
            and restoration.get("reference_processes_started") == 0
            and restoration.get("clock_samples") == 0
            and restoration.get("hidden_cases_read") == 0
            and restoration.get("benchmark_files_read") == 0
            and restoration.get("performance") == "NOT MEASURED"
            and restoration.get("winner_selected") is False
            and type(restoration.get("restored_targets")) is dict
            and set(restoration["restored_targets"]) == {"engine", "bridge"},
            "retain the genuine durable original Zig native restoration")
    passing = sum(row["verified_passing_case_count"] for row in observed)
    require(len(observed) == SUITE_COUNT and passing == 3583
            and sum(row["actual_semantic_mismatch_count"] for row in observed) == 1764,
            "never qualify a partly passing or silently weakened Zig campaign")
    return {"status": "FAIL", "candidate_family": "zig",
            "source_version": 6, "candidate_qualified": False,
            "passing_suite_count": 6, "verified_passing_case_count": passing,
            "legacy_qualified_candidate_case_executions": 3583,
            "actual_semantic_mismatch_count": 1764,
            "mismatches_by_suite": dict(ZIG_MISMATCH_COUNTS),
            "actual_case_interpreter_exec_calls": 385,
            "actual_nested_verified_passing_case_count": 0,
            "actual_cleanup_failure_count": 3,
            "artifact_count_including_restoration": len(owners),
            "archive_owners": owners, "all_suites": observed,
            "v6_owner_bug_independently_confirmed": True,
            "receipt_publication_does_not_qualify_candidate": True,
            "performance": "NOT MEASURED", "holdout": "NOT OPENED"}


def authenticate_v4_build_history(context: Mapping[str, Any],
                                  activation: types.ModuleType) -> dict[str, Any]:
    base = context["v6_worker"]
    activation_history = context["six_family_v3_activation_context"]
    candidate_history = activation_history.get("historical_candidate_evidence")
    require(type(candidate_history) is dict
            and candidate_history.get("owner_count") == 51
            and type(candidate_history.get("families")) is dict,
            "begin with all 51 authentic independently owned candidate artifacts")
    identities: set[tuple[int, int]] = set()
    for family in ("c", "rust", "zig"):
        record = candidate_history["families"].get(family)
        require(type(record) is dict and record.get("owner_count") == 17
                and type(record.get("owners")) is list
                and len(record["owners"]) == 17,
                "preserve every genuine source-owned historical candidate file")
        for owner in record["owners"]:
            require(type(owner) is dict and type(owner.get("device")) is int
                    and type(owner.get("inode")) is int and owner["inode"] > 0
                    and owner.get("mode") == 0o600,
                    "historical candidates require exact private original evidence inodes")
            key = owner["device"], owner["inode"]
            require(key not in identities,
                    "never double-count a hard-linked historical candidate owner")
            identities.add(key)
    require(len(identities) == 51,
            "authenticate all 51 distinct genuine candidate archive and receipt inodes")
    all_paths = {path for spec in HISTORICAL_V4_BUILD_OWNERS.values()
                 for path in (spec["archive"], spec["receipt"])}
    allowed = frozenset({*context["allowed_paths"], *all_paths})
    results: dict[str, dict[str, Any]] = {}
    for family, expected in HISTORICAL_V4_BUILD_OWNERS.items():
        compressed, archive_owner = base.read_owned(
            expected["archive"], expected["archive_sha256"],
            allowed=allowed, maximum=MAX_SPECIALIZED_BYTES)
        receipt_raw, receipt_owner = base.read_owned(
            expected["receipt"], expected["receipt_sha256"],
            allowed=allowed, maximum=MAX_SOURCE_BYTES)
        plain = bounded_gzip(compressed, expected["archive"],
                             maximum=MAX_SPECIALIZED_BYTES)
        report = decode_document(plain, expected["archive"],
                                 maximum=MAX_SPECIALIZED_BYTES,
                                 canonical_required=True)
        receipt = decode_document(receipt_raw, expected["receipt"],
                                  canonical_required=True)
        for owner in (archive_owner, receipt_owner):
            key = owner["device"], owner["inode"]
            require(owner.get("mode") == 0o600 and key not in identities,
                    "require distinct private V4 build archives and receipts")
            identities.add(key)
        publication = receipt.get("archive_publication")
        sync = receipt.get("archive_directory_fsync")
        require(report.get("schema") == "rebar-phase2-owned-native-source-build-v4"
                and report.get("version") == 4
                and report.get("status") == expected["status"]
                and report.get("family") == family
                and report.get("label") == "phase2-v4"
                and report.get("source_sha256") == BUILD_V4_SHA256
                and report.get("protocol_sha256") == BUILD_V4_PROTOCOL_SHA256
                and report.get("contract_sha256") == BUILD_V4_DOCUMENT_SHA256
                and receipt.get("schema")
                == "rebar-phase2-owned-native-source-build-v4-durable-publication-receipt"
                and receipt.get("status") == "PASS"
                and receipt.get("build_status") == expected["status"]
                and receipt.get("family") == family
                and receipt.get("archive_relative") == expected["archive"]
                and receipt.get("archive_sha256") == expected["archive_sha256"]
                and receipt.get("archive_bytes") == len(compressed)
                and receipt.get("uncompressed_bytes") == len(plain)
                and receipt.get("uncompressed_sha256")
                == hashlib.sha256(plain).hexdigest()
                and type(publication) is dict
                and set(publication) == {
                    "path", "sha256", "bytes", "device", "inode",
                    "exclusive_creation", "same_inode_readback_verified",
                    "file_fsync_completed", "write_calls",
                }
                and publication.get("path") == str(ROOT / expected["archive"])
                and publication.get("sha256") == archive_owner["sha256"]
                and publication.get("bytes") == len(compressed)
                and publication.get("device") == archive_owner["device"]
                and publication.get("inode") == archive_owner["inode"]
                and publication.get("exclusive_creation") is True
                and publication.get("same_inode_readback_verified") is True
                and publication.get("file_fsync_completed") is True
                and type(publication.get("write_calls")) is int
                and publication["write_calls"] > 0
                and type(sync) is dict and sync.get("completed") is True
                and type(sync.get("device")) is int
                and type(sync.get("inode")) is int and sync["inode"] > 0
                and receipt.get("source_sha256") == BUILD_V4_SHA256
                and receipt.get("protocol_sha256") == BUILD_V4_PROTOCOL_SHA256
                and receipt.get("contract_sha256") == BUILD_V4_DOCUMENT_SHA256
                and report.get("candidate_correctness") == "NOT MEASURED"
                and receipt.get("candidate_correctness") == "NOT MEASURED"
                and report.get("candidate_processes_started") == 0
                and receipt.get("candidate_processes_started") == 0
                and report.get("candidate_imports") == 0
                and receipt.get("candidate_imports") == 0
                and report.get("native_libraries_loaded") == 0
                and receipt.get("native_libraries_loaded") == 0
                and report.get("performance") == "NOT MEASURED"
                and receipt.get("performance") == "NOT MEASURED"
                and report.get("clock_samples") == 0
                and receipt.get("clock_samples") == 0
                and report.get("hidden_cases_read") == 0
                and receipt.get("hidden_cases_read") == 0
                and report.get("benchmark_files_read") == 0
                and receipt.get("benchmark_files_read") == 0,
                "preserve the real V4 build status, never upgrade a written failure")
        original_sources = {
            path: item[0]
            for path, item in activation.SOURCE_OWNERS[family].items()
        }
        require(report.get("owned_source_sha256") == original_sources
                and receipt.get("owned_source_sha256") == original_sources,
                "bind the whole actual V4 build to its complete private semantic source")
        processes = report.get("processes")
        phases = report.get("build_phases")
        require(type(processes) is list
                and len(processes) == expected["process_count"]
                and type(phases) is list
                and len(phases) == expected["phase_count"],
                "preserve every actual compiler process and fresh phase")
        pids: set[int] = set()
        for process in processes:
            require(type(process) is dict and type(process.get("pid")) is int
                    and process["pid"] > 0 and process["pid"] not in pids
                    and process.get("shell") is False,
                    "retain distinct actual compiler PIDs without hidden shells")
            pids.add(process["pid"])
            activation.decode_process_output(process, "stdout")
            activation.decode_process_output(process, "stderr")
        if family == "cpp":
            arguments = {
                "family": "cpp", "build_label": "phase2-v4",
                "build_root": "/tmp/rebar-phase2-native-build-v4-cpp-authenticated-history",
                "build_source_sha256": BUILD_V4_SHA256,
                "build_protocol_sha256": BUILD_V4_PROTOCOL_SHA256,
                "build_contract_sha256": BUILD_V4_DOCUMENT_SHA256,
                "build_report_sha256": expected["archive_sha256"],
                "build_receipt_sha256": expected["receipt_sha256"],
                "native_hashes": {"bridge": expected["bridge_sha256"]},
                "native_sizes": {"bridge": expected["bridge_bytes"]},
            }
            proved = activation.validate_build_report(
                report, receipt, compressed, arguments, original_sources)
            require(type(proved) is dict and set(proved) == {"bridge"}
                    and proved["bridge"].get("sha256") == expected["bridge_sha256"]
                    and proved["bridge"].get("size_bytes") == expected["bridge_bytes"]
                    and all(process.get("exit_status") == 0 for process in processes),
                    "independently verify both actual reproducible complete C++ build phases")
        elif family == "go":
            error = report.get("error")
            failed = processes[-1]
            stderr = activation.decode_process_output(failed, "stderr")
            require(type(error) is dict
                    and error.get("type") == expected["error_type"]
                    and error.get("message") == expected["error_message"]
                    and failed.get("name") == expected["failed_process"]
                    and failed.get("exit_status") == expected["failed_process_exit_status"]
                    and hashlib.sha256(stderr).hexdigest()
                    == expected["failed_process_stderr_sha256"]
                    and b"Python.h" in stderr
                    and all(item.get("exit_status") == 0
                            for item in processes[:-1])
                    and report.get("reproducibility") is None
                    and receipt.get("build_status") == "FAIL",
                    "preserve the four actual Go processes and genuine Python.h build failure")
        else:
            error = report.get("error")
            require(type(error) is dict
                    and error.get("type") == expected["error_type"]
                    and error.get("message") == expected["error_message"]
                    and report.get("reproducibility") is None
                    and [phase.get("name") for phase in phases]
                    == ["reference-a", "reference-b"]
                    and all(process.get("exit_status") == 0
                            for process in processes)
                    and receipt.get("build_status") == "FAIL",
                    "preserve the authentic two-phase Fortran reproducibility failure")
            build_root = "/tmp/rebar-phase2-native-build-v4-fortran-authenticated-history"
            streams = activation.validate_processes("fortran", build_root,
                                                    processes)
            observed_engines: list[str] = []
            for phase in phases:
                name = phase["name"]
                outputs = phase.get("native_outputs")
                require(type(outputs) is dict
                        and set(outputs) == {"engine", "bridge"},
                        "preserve the real Fortran engine and bridge in both phases")
                for role, item in outputs.items():
                    require(type(item) is dict
                            and item.get("family") == "fortran"
                            and item.get("role") == role,
                            "retain source-owned Fortran phase-native roles")
                    dynamic = activation.parse_dynamic(
                        streams[(name, role + "_dynamic")])
                    symbols = activation.parse_symbols(
                        streams[(name, role + "_symbols")])
                    require(item.get("audit")
                            == activation.validate_elf("fortran", role,
                                                       dynamic, symbols),
                            "authenticate the original complete Fortran ELF streams")
                    if role == "bridge":
                        require(item.get("sha256") == expected["bridge_sha256"]
                                and item.get("size_bytes") == expected["bridge_bytes"],
                                "preserve both actual identical Fortran bridges")
                    else:
                        require(item.get("size_bytes") == expected["engine_bytes"],
                                "preserve both genuine full-size Fortran engines")
                        observed_engines.append(item.get("sha256"))
            require(observed_engines == [expected["first_engine_sha256"],
                                         expected["second_engine_sha256"]]
                    and observed_engines[0] != observed_engines[1],
                    "never promote actual different Fortran engine bytes to PASS")
        results[family] = {
            "status": expected["status"], "receipt_status": "PASS",
            "build_status": expected["status"],
            "archive_owner": archive_owner, "receipt_owner": receipt_owner,
            "phase_count": len(phases), "process_count": len(processes),
            "candidate_matching_cases_executed": 0,
            "candidate_correctness": "NOT MEASURED",
            "activation_status": "NOT RUN",
            "candidate_qualified": False,
            "generated_header_status":
            "NOT GENERATED" if family == "go" else "NOT APPLICABLE",
            "error": report.get("error"),
            **({"bridge_sha256": expected["bridge_sha256"],
                "bridge_bytes": expected["bridge_bytes"],
                "first_engine_sha256": expected["first_engine_sha256"],
                "second_engine_sha256": expected["second_engine_sha256"],
                "engine_bytes": expected["engine_bytes"],
                "failure_kind": "NON-REPRODUCIBLE ENGINE OUTPUT"}
               if family == "fortran" else {}),
        }
    v2_count = activation_history.get("preserved_v2_process_count")
    v3_records = [row for row in activation_history.get("preserved_historical_records", [])
                  if type(row) is dict and row.get("id") == "v3_zig"]
    v4_count = sum(row["process_count"] for row in results.values())
    require(v2_count == 39 and len(v3_records) == 1
            and v3_records[0].get("result_status") == "PASS"
            and v3_records[0].get("process_count") == 15
            and v4_count == 32 and len(identities) == 57,
            "derive actual V2, V3, and V4 compiler denominators from genuine records")
    v3_count = v3_records[0]["process_count"]
    return {"source_family_count": 6, "fully_runnable_p0_family_count": 3,
            "artifact_count": 6, "actual_source_build_process_count": v4_count,
            "total_distinct_historical_evidence_owner_count": len(identities),
            "v2_source_build_process_count": v2_count,
            "v2_plus_v4_source_build_process_count": v2_count + v4_count,
            "separately_preserved_successful_v3_zig_source_build_process_count": v3_count,
            "v2_plus_v3_plus_v4_source_build_process_count": v2_count + v3_count + v4_count,
            "process_id_uniqueness_claimed_across_independent_runs": False,
            "families": results,
            "actual_candidate_workers": 0, "actual_v3_activations": 0,
            "qualified_candidate_count": 0, "performance": "NOT MEASURED",
            "holdout": "NOT OPENED"}


def authenticate_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    verify_runtime()
    base = importlib.import_module("tools.run_frozen_p0_candidate_worker_v4")
    original_options = v6_options(
        options,
        readonly=options.verify_frozen_context
        or getattr(options, "candidate", None) not in FAMILIES
        or getattr(options, "activation_source_sha256", None)
        == FUTURE_ACTIVATION_SHA256)
    context = base.authenticate_frozen_context(original_options)
    extra = {
        SOURCE_RELATIVE: options.source_sha256,
        PROTOCOL_RELATIVE: options.protocol_sha256,
        DOCUMENT_RELATIVE: options.document_sha256,
        V6_RUNNER_RELATIVE: V6_RUNNER_SHA256,
        INDEPENDENCE_V2_RELATIVE: INDEPENDENCE_V2_SHA256,
        INDEPENDENCE_V2_PROTOCOL_RELATIVE: INDEPENDENCE_V2_PROTOCOL_SHA256,
        INDEPENDENCE_V2_DOCUMENT_RELATIVE: INDEPENDENCE_V2_DOCUMENT_SHA256,
        BUILD_V4_RELATIVE: BUILD_V4_SHA256,
        BUILD_V4_PROTOCOL_RELATIVE: BUILD_V4_PROTOCOL_SHA256,
        BUILD_V4_DOCUMENT_RELATIVE: BUILD_V4_DOCUMENT_SHA256,
        FUTURE_ACTIVATION_RELATIVE: FUTURE_ACTIVATION_SHA256,
        FUTURE_ACTIVATION_PROTOCOL_RELATIVE: FUTURE_ACTIVATION_PROTOCOL_SHA256,
        FUTURE_ACTIVATION_DOCUMENT_RELATIVE: FUTURE_ACTIVATION_DOCUMENT_SHA256,
        **HISTORICAL_ZIG_OWNERS,
        **{item[key]: item[key + "_sha256"]
           for item in HISTORICAL_V4_BUILD_OWNERS.values()
           for key in ("archive", "receipt")},
    }
    allowed = frozenset({*context["allowed_paths"], *extra})
    for relative, fingerprint in extra.items():
        require(type(fingerprint) is str,
                "pin every independently frozen V7 predecessor and exact source")
        base.read_owned(relative, fingerprint, allowed=allowed,
                        maximum=MAX_ARCHIVE_BYTES if relative.endswith(".json.gz")
                        else MAX_SOURCE_BYTES)
    context = {**context, "v6_worker": base, "v6_options": original_options,
               "allowed_paths": allowed}
    context["frozen_v7_source_owners"] = pinned_v7_owners(options, base, allowed)
    require({name: historical_v5_owners(name) for name in ("c", "rust")}
            == {name: base.historical_evidence_paths(name) for name in ("c", "rust")},
            "independently preserve all exact frozen historical C and Rust owners")
    audit = base.import_frozen(INDEPENDENCE_V2_RELATIVE, INDEPENDENCE_V2_SHA256,
                               allowed)
    audit_result = audit.run_verify(argparse.Namespace(
        source_sha256=INDEPENDENCE_V2_SHA256,
        protocol_sha256=INDEPENDENCE_V2_PROTOCOL_SHA256,
        inventory_sha256=INDEPENDENCE_V2_DOCUMENT_SHA256))
    require(type(audit_result) is dict and audit_result.get("status") == "PASS"
            and audit_result.get("static_independence") == "PASS"
            and audit_result.get("family_count") == 6
            and audit_result.get("source_owner_count") == 25
            and audit_result.get("pairwise_semantic_owner_overlap_count") == 0
            and audit_result.get("historical_c_rust_v5_evidence_owner_count") == 34
            and audit_result.get("candidate_correctness_qualified_count") == 0
            and audit_result.get("candidate_code_executed") is False
            and audit_result.get("native_libraries_loaded") is False
            and audit_result.get("candidate_processes_started") == 0
            and audit_result.get("reference_processes_started") == 0
            and audit_result.get("clock_samples") == 0
            and audit_result.get("hidden_cases_read") == 0
            and audit_result.get("performance_files_read") == 0,
            "independently verify six genuinely from-scratch source-owned families")
    build = base.import_frozen(BUILD_V4_RELATIVE, BUILD_V4_SHA256, allowed)
    contract = build.validate_contract(build.expected_contract())
    require(contract.get("family_count") == 6
            and contract.get("qualified_candidate_count") == 0
            and sum(len(row["owners"]) for row in contract["families"]) == 25,
            "verify the six-family V4 source freeze without building or activating")
    context["six_family_static_independence"] = audit_result
    activation = base.import_frozen(FUTURE_ACTIVATION_RELATIVE,
                                    FUTURE_ACTIVATION_SHA256, allowed)
    activation_context = activation.verify_frozen_context(
        verify_live_restored_targets=True)
    require(type(activation_context) is dict
            and activation_context.get("schema")
            == "rebar-phase2-verified-native-candidate-activation-v3-read-only-frozen-context"
            and activation_context.get("status") == "PASS"
            and activation_context.get("read_only") is True
            and activation_context.get("activation_source", {}).get("sha256")
            == FUTURE_ACTIVATION_SHA256
            and activation_context.get("activation_protocol", {}).get("sha256")
            == FUTURE_ACTIVATION_PROTOCOL_SHA256
            and activation_context.get("activation_contract", {}).get("sha256")
            == FUTURE_ACTIVATION_DOCUMENT_SHA256
            and activation_context.get("family_count") == 6
            and activation_context.get("source_owner_count") == 25
            and activation_context.get("pairwise_shared_semantic_owners") == 0
            and activation_context.get("qualified_candidate_count") == 0
            and activation_context.get("actual_v3_activations") == "NOT RUN"
            and activation_context.get("candidate_processes_started") == 0
            and activation_context.get("reference_processes_started") == 0
            and activation_context.get("candidate_imports") == 0
            and activation_context.get("native_libraries_loaded") == 0
            and activation_context.get("hidden_cases_read") == 0
            and activation_context.get("benchmark_files_read") == 0
            and activation_context.get("clock_samples") == 0
            and activation_context.get("performance") == "NOT MEASURED"
            and activation_context.get("historical_candidate_evidence", {}).get("owner_count") == 51
            and activation_context.get("historical_v4_build_evidence", {}).get("owner_count") == 6
            and activation_context.get("total_distinct_historical_evidence_owner_count") == 57
            and activation_context.get("historical_build_process_ledger", {}).get("v2_process_count") == 39
            and activation_context.get("historical_build_process_ledger", {}).get("v3_zig_process_count") == 15
            and activation_context.get("historical_build_process_ledger", {}).get("v4_process_count") == 32
            and activation_context.get("historical_build_process_ledger", {}).get("v2_and_v4_process_count") == 71
            and activation_context.get("historical_build_process_ledger", {}).get("all_historical_build_process_count") == 86,
            "authenticate exact V3, all 57 actual owners and separate 39/15/32 build processes")
    context["activation_v3"] = activation
    context["six_family_v3_activation_context"] = activation_context
    context["preserved_v4_build_history"] = authenticate_v4_build_history(
        context, activation)
    context["six_family_source_build_contract"] = {
        "source_sha256": BUILD_V4_SHA256,
        "protocol_sha256": BUILD_V4_PROTOCOL_SHA256,
        "document_sha256": BUILD_V4_DOCUMENT_SHA256,
        "family_count": 6, "source_owner_count": 25,
        "qualified_candidate_count": 0,
        "actual_source_builds": 0,
        "future_activation_source_sha256": FUTURE_ACTIVATION_SHA256,
        "future_activation_protocol_sha256": FUTURE_ACTIVATION_PROTOCOL_SHA256,
        "future_activation_document_sha256": FUTURE_ACTIVATION_DOCUMENT_SHA256,
        "actual_v3_activation_count": 0,
        "future_candidate_runs_authorized": False,
    }
    context["preserved_v6_zig_campaign"] = authenticate_historical_zig(context)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a read-only source-owned correctness context imported a candidate")
    return context


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    for name in ("candidate", "label", "build_version", "build_label",
                 "activation_root", "suite", "activation_report_sha256",
                 "activation_receipt_sha256", "recovery_journal_sha256",
                 "candidate_source_sha256", "native_engine_sha256",
                 "native_bridge_sha256", "build_source_sha256",
                 "build_protocol_sha256", "build_archive_sha256",
                 "build_receipt_sha256", "activation_source_sha256",
                 "activation_protocol_sha256", "activation_contract_sha256",
                 "build_contract_sha256"):
        require(getattr(options, name, None) is None,
                "read-only V7 verification cannot authorize candidates: " + name)
    require(not options.owned_source_sha256,
            "read-only V7 verification cannot authorize real candidate sources")
    base = importlib.import_module("tools.run_frozen_p0_candidate_worker_v4")
    with base.frozen_context_boundary() as effects:
        context = authenticate_frozen_context(options)
    histories = context["preserved_v5_campaigns"]
    zig = context["preserved_v6_zig_campaign"]
    builds = context["preserved_v4_build_history"]
    require(set(histories) == {"c", "rust"}
            and histories["c"]["qualified_case_count"] == 7197
            and histories["c"]["actual_semantic_mismatch_count"] == 2094
            and histories["rust"]["qualified_case_count"] == 7461
            and histories["rust"]["actual_semantic_mismatch_count"] == 2042
            and zig["verified_passing_case_count"] == 3583
            and zig["actual_semantic_mismatch_count"] == 1764
            and zig["candidate_qualified"] is False
            and builds["artifact_count"] == 6
            and builds["families"]["cpp"]["build_status"] == "PASS"
            and builds["families"]["cpp"]["phase_count"] == 2
            and builds["families"]["cpp"]["process_count"] == 10
            and builds["families"]["cpp"]["candidate_matching_cases_executed"] == 0
            and builds["families"]["go"]["build_status"] == "FAIL"
            and builds["families"]["go"]["receipt_status"] == "PASS"
            and builds["families"]["go"]["phase_count"] == 0
            and builds["families"]["go"]["process_count"] == 4
            and builds["families"]["fortran"]["build_status"] == "FAIL"
            and builds["families"]["fortran"]["receipt_status"] == "PASS"
            and builds["families"]["fortran"]["phase_count"] == 2
            and builds["families"]["fortran"]["process_count"] == 18
            and builds["families"]["fortran"]["first_engine_sha256"]
            != builds["families"]["fortran"]["second_engine_sha256"],
            "preserve all real candidate failures and passing/nonreproducible V4 builds")
    for name in ("file_writes", "candidate_imports", "reference_workers",
                 "candidate_workers", "source_builds", "native_promotions",
                 "native_libraries_loaded", "interpreter_creations",
                 "thread_starts", "clock_samples", "network_requests",
                 "hidden_cases_read", "benchmark_files_read"):
        require(effects[name] == 0,
                "read-only V7 verification caused an external effect: " + name)
    return {"schema": SCHEMA + "-read-only-frozen-context", "status": "PASS",
            "read_only": True, "goal_sha256": GOAL_SHA256,
            "phase1_inventory_sha256": PHASE1_SHA256,
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "named_private_waiver_count": 13,
            "frozen_v7_source_owners": context["frozen_v7_source_owners"],
            "six_family_static_independence": context["six_family_static_independence"],
            "six_family_v3_activation_context":
            context["six_family_v3_activation_context"],
            "six_family_source_build_contract": context["six_family_source_build_contract"],
            "preserved_v5_actual_campaigns": histories,
            "preserved_v6_zig_actual_campaign": zig,
            "preserved_v4_source_build_history": builds,
            "preserved_historical_candidate_artifact_count_including_restorations": 51,
            "preserved_historical_artifact_count_including_source_builds": 57,
            "preserved_historical_restoration_receipt_count": 3,
            "source_family_count": 6,
            "fully_runnable_p0_family_count": 3,
            "candidate_qualified_count": 0,
            "fully_qualified_candidate_count": 0,
            "actual_candidate_workers": 0, "actual_candidate_imports": 0,
            "actual_reference_workers": 0, "actual_source_builds": 0,
            "actual_native_promotions": 0, "actual_interpreters_created": 0,
            "read_only_effects": effects, "clock_samples": 0,
            "timing_trials_run": 0, "benchmark_files_read": 0,
            "hidden_cases_read": 0, "performance": "NOT MEASURED",
            "final_holdout_authorized": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False}


def frozen_owner_arguments(options: argparse.Namespace) -> list[str]:
    names = ("candidate", "label", "build_version", "build_label",
             "source_sha256", "protocol_sha256", "document_sha256",
             "build_source_sha256", "build_protocol_sha256",
             "build_archive_sha256", "build_receipt_sha256",
             "activation_root", "activation_source_sha256",
             "activation_protocol_sha256", "activation_report_sha256",
             "activation_receipt_sha256", "candidate_source_sha256",
             "native_engine_sha256", "native_bridge_sha256")
    result: list[str] = []
    for name in names:
        value = getattr(options, name)
        require(type(value) is str and bool(value),
                "pin every independently frozen V7 candidate owner: " + name)
        result.extend(("--" + name.replace("_", "-"), value))
    if options.recovery_journal_sha256 is not None:
        result.extend(("--recovery-journal-sha256",
                       options.recovery_journal_sha256))
    for owner in options.owned_source_sha256:
        result.extend(("--owned-source-sha256", owner))
    return result


def producer_command(suite: SuiteSpec, options: argparse.Namespace,
                     context: Mapping[str, Any],
                     approval: Mapping[str, Any]) -> list[str]:
    base = context["v6_worker"]
    original = context["v6_options"]
    prefix = [PINNED_PYTHON, "-I", "-B"]
    if suite.name == "subinterpreter_v2":
        return [*prefix, str(ROOT / NESTED_V3_RELATIVE),
                *base.nested_arguments(original, approval)]
    if suite.name in {"public_surface_v19", "pep688_v4",
                      "threaded_pattern_v1"}:
        return [*prefix, str(ROOT / SOURCE_RELATIVE),
                "--internal-candidate-worker", "--suite", suite.name,
                *frozen_owner_arguments(options)]
    original_spec = base.suite_spec(suite.name)
    row = base.phase_one_row(context, original_spec)
    return context["legacy_worker"].producer_command(
        context["legacy_worker"].suite_spec(suite.name), original, row)


def direct_worker(options: argparse.Namespace) -> dict[str, Any]:
    base = importlib.import_module("tools.run_frozen_p0_candidate_worker_v4")
    original = v6_options(options, readonly=False)
    suite = suite_spec(options.suite)
    require(suite.name in {"public_surface_v19", "pep688_v4",
                           "threaded_pattern_v1"},
            "execute only the independently frozen three original direct suites")
    result = base.direct_worker(original)
    require(type(result) is dict and result.get("status") == "OBSERVED"
            and result.get("suite") == suite.name
            and result.get("candidate_family") == options.candidate,
            "retain actual source-owned candidate direct observations")
    return result


def actual_native_pins(options: argparse.Namespace,
                       context: Mapping[str, Any],
                       approval: Mapping[str, Any]) -> None:
    original = context["original_candidate_gate"]
    actual = original.validate_owners(
        original.family_spec(options.candidate),
        adapter=options.candidate_source_sha256,
        engine=options.native_engine_sha256,
        bridge=options.native_bridge_sha256,
        source_entries=options.owned_source_sha256)
    require(actual == approval["pins"],
            "the genuinely source-built canonical matcher changed during observation")


def authenticate_canonical_activation_v3(
    options: argparse.Namespace, context: Mapping[str, Any],
) -> dict[str, Any]:
    activation = context["activation_v3"]
    family = checked_family(options.candidate)
    require(options.build_version == "4"
            and options.activation_source_sha256 == FUTURE_ACTIVATION_SHA256
            and options.activation_protocol_sha256 == FUTURE_ACTIVATION_PROTOCOL_SHA256
            and options.activation_contract_sha256 == FUTURE_ACTIVATION_DOCUMENT_SHA256
            and options.build_source_sha256 == BUILD_V4_SHA256
            and options.build_protocol_sha256 == BUILD_V4_PROTOCOL_SHA256
            and options.build_contract_sha256 == BUILD_V4_DOCUMENT_SHA256,
            "pin the exact genuine six-family V4 source build and V3 activation")
    root = activation.checked_private_root(options.activation_root, family,
                                           build=False)
    report_raw, report_owner = activation.read_owned(
        root, activation.REPORT_NAME, options.activation_report_sha256,
        maximum=MAX_SPECIALIZED_BYTES, private=True)
    receipt_raw, receipt_owner = activation.read_owned(
        root, activation.RECEIPT_NAME, options.activation_receipt_sha256,
        maximum=MAX_SOURCE_BYTES, private=True)
    report = activation.decode_document(report_raw,
                                        "actual complete six-family V3 activation")
    receipt = activation.decode_document(receipt_raw,
                                         "actual durable six-family V3 receipt")
    journal_claim = report.get("recovery_journal")
    require(type(journal_claim) is dict,
            "a real V3 activation requires its actual durable recovery journal")
    journal_pin = checked_digest(journal_claim.get("sha256"),
                                 "actual six-family V3 recovery journal")
    if options.recovery_journal_sha256 is not None:
        require(options.recovery_journal_sha256 == journal_pin,
                "reject a substituted V3 recovery journal")
    journal_raw, journal_owner = activation.read_owned(
        root, activation.JOURNAL_NAME, journal_pin,
        maximum=MAX_SOURCE_BYTES, private=True)
    journal = activation.decode_document(journal_raw,
                                         "actual genuine V3 recovery journal")
    arguments = {
        "family": family,
        "activation_root": root,
        "activation_source_sha256": FUTURE_ACTIVATION_SHA256,
        "activation_protocol_sha256": FUTURE_ACTIVATION_PROTOCOL_SHA256,
        "activation_contract_sha256": FUTURE_ACTIVATION_DOCUMENT_SHA256,
        "activation_report_sha256": options.activation_report_sha256,
        "activation_receipt_sha256": options.activation_receipt_sha256,
        "recovery_journal_sha256": journal_pin,
    }
    activation.validate_activation_documents(report, receipt, journal, arguments)
    activation.validate_recovery_journal(journal, arguments)
    proof = activation.validate_build_provenance(report.get("source_build"), family)
    require(proof.get("build_version") == 4
            and proof.get("label") == checked_label(options.build_label)
            and proof.get("archive_sha256") == options.build_archive_sha256
            and proof.get("receipt_sha256") == options.build_receipt_sha256
            and proof.get("independent_fresh_phase_count") == 2
            and proof.get("actual_versioned_symbol_streams_verified") is True
            and proof.get("generated_go_header_promoted") is False,
            "require an actually passing two-phase V4 source build, never a Go failure")
    build_arguments = activation.reconstructed_build_arguments(arguments, journal)
    actual_pins = activation.parse_owner_pins(family,
                                               options.owned_source_sha256)
    require(build_arguments.get("family") == family
            and build_arguments.get("build_report_sha256")
            == options.build_archive_sha256
            and build_arguments.get("build_receipt_sha256")
            == options.build_receipt_sha256
            and journal.get("owned_source_sha256") == actual_pins,
            "reauthenticate all exact six-family independent candidate sources")
    prerequisite = activation.authenticate_prerequisites(build_arguments)
    require(prerequisite.get("family") == family
            and prerequisite.get("pins") == actual_pins
            and prerequisite.get("build_report", {}).get("sha256")
            == options.build_archive_sha256
            and prerequisite.get("build_receipt", {}).get("sha256")
            == options.build_receipt_sha256,
            "reauthenticate both exact genuine PASS V4 build phases and receipt")
    intents = activation.authenticate_intentions(root, journal, journal_pin)
    roles = activation.FAMILIES[family]["targets"]
    require(set(intents) == set(roles),
            "require a real durable authentic promotion intention for every role")
    targets = report.get("canonical_targets")
    require(type(targets) is dict and set(targets) == set(roles),
            "require every actual V3-promoted canonical native target")
    for role, filename in roles.items():
        present = activation.current_canonical("candidates/" + filename)
        require(present is not None
                and activation.same_owner(present[1], targets[role])
                and activation.same_owner(present[1], intents[role]["target"]),
                "the actual source-verified V3 canonical native target changed")
    native = report.get("canonical_targets")
    if family == "cpp":
        require(options.native_engine_sha256 == options.native_bridge_sha256
                == native["bridge"]["sha256"],
                "pin the single genuine C++ combined matcher/bridge")
    else:
        engine_role = "extension" if family == "c" else "engine"
        bridge_role = "extension" if family == "c" else "bridge"
        require(options.native_engine_sha256 == native[engine_role]["sha256"]
                and options.native_bridge_sha256 == native[bridge_role]["sha256"],
                "pin the actual independently promoted V3 engine and bridge")
    return {"family": family, "activation_version": 3, "build_version": "4",
            "pins": actual_pins, "source_build": proof,
            "canonical_activation": report,
            "promotion_intents": intents,
            "activation_report_owner": report_owner,
            "activation_receipt_owner": receipt_owner,
            "recovery_journal_owner": journal_owner}


def observe_actual_suite(suite: SuiteSpec, options: argparse.Namespace,
                         context: Mapping[str, Any],
                         approval: Mapping[str, Any]) -> dict[str, Any]:
    base = context["v6_worker"]
    original = context["v6_options"]
    evidence: dict[str, Any] = {
        "suite": suite.name, "candidate_family": options.candidate,
        "case_execution_denominator": suite.case_count,
        "matrix_sha256": suite.matrix_sha256,
        "reference_records_sha256": suite.reference_sha256,
        "producer_source_path": suite.source_relative,
        "producer_source_sha256": suite.source_sha256,
        "status": "FAIL", "actual_process": None,
        "actual_candidate_case_count": 0,
        "verified_passing_case_count": 0, "actual_candidate_workers": 0,
        "mismatch_count": 0, "all_mismatches": [],
        "all_failure_reasons": [], "failure": None,
    }
    try:
        actual_native_pins(options, context, approval)
        process = base.encoded_process(producer_command(suite, options,
                                                         context, approval))
        evidence["actual_process"] = process
        require(process.get("timed_out") is False
                and process.get("returncode") in {0, 1},
                "retain actual candidate timeouts, failures and native crashes")
        require(base.restore_stream(process.get("stderr"),
                                    suite.name + " full producer stderr") == b"",
                "never discard real candidate producer stderr")
        value = decode_document(
            base.restore_stream(process.get("stdout"),
                                suite.name + " full producer stdout"),
            suite.name + " complete actual candidate producer",
            maximum=MAX_PROCESS_BYTES)
        if suite.recorder_relative is not None:
            base_spec = base.suite_spec(suite.name)
            authenticate_specialized_publications(value, suite, original, context)
            observed = base.validate_specialized_result(
                value, base_spec, original, context, process["returncode"])
        elif suite.name == "subinterpreter_v2":
            observed = validate_nested_result(value, suite, options, context,
                                              approval, process["returncode"])
        elif suite.name in {"public_surface_v19", "pep688_v4",
                            "threaded_pattern_v1"}:
            observed = base.validate_direct_result(
                value, base.suite_spec(suite.name), original, context,
                process["returncode"])
        elif suite.name == "original_bounded_v5":
            require(process["returncode"] == 0,
                    "retain genuine original CPython-method candidate failures")
            observed = context["legacy_worker"].validate_original_result(
                value, context["legacy_worker"].suite_spec(suite.name), original)
            observed.update(actual_candidate_workers=1, mismatch_count=0,
                            all_mismatches=[], all_failure_reasons=[])
        else:
            observed = base.validate_category_result(
                value, base.suite_spec(suite.name), original, context,
                process["returncode"])
        require(type(observed) is dict,
                "retain each actual complete source-owned candidate observation")
        evidence.update(observed)
        passed = (observed.get("actual_candidate_case_count") == suite.case_count
                  and observed.get("mismatch_count") == 0
                  and not observed.get("all_failure_reasons")
                  and observed.get("source_owned_candidate_status", "PASS") != "FAIL")
        evidence["verified_passing_case_count"] = suite.case_count if passed else 0
        if passed:
            evidence["status"] = "PASS"
        else:
            evidence["failure"] = {
                "type": "ActualCandidateMismatch",
                "message": "the actual complete original suite did not match",
                "actual_mismatch_count": observed.get("mismatch_count", 0),
                "actual_failure_reasons": observed.get("all_failure_reasons", []),
            }
    except Exception as error:
        actual = locals().get("value")
        if type(actual) is dict:
            records = actual.get("candidate_records", actual.get("records"))
            if type(records) is list:
                evidence["actual_candidate_case_count"] = len(records)
                evidence["actual_candidate_workers"] = 1
            evidence["complete_decoded_failed_producer"] = actual
        failure = {"type": type(error).__qualname__, "message": str(error),
                   "traceback": traceback.format_exception(
                       type(error), error, error.__traceback__)}
        details = getattr(error, "details", None)
        if type(details) is dict:
            failure["actual_failure"] = details
        evidence["failure"] = failure
        evidence["all_failure_reasons"].append(failure)
        evidence["verified_passing_case_count"] = 0
    actual_native_pins(options, context, approval)
    return evidence


def planned_worker_paths(family: str, label: str,
                         *, failure: bool) -> tuple[str, str]:
    stem = ("oracle/phase2/evidence/frozen-p0-candidate-worker-v5-"
            + checked_family(family) + "-" + checked_label(label)
            + ("-failures" if failure else ""))
    return stem + ".json.gz", stem + "-publication-receipt.json"


def ensure_fresh_run_evidence(options: argparse.Namespace,
                              context: Mapping[str, Any]) -> None:
    family, label = checked_family(options.candidate), checked_label(options.label)
    base = context["v6_worker"]
    planned: set[str] = set()
    for failure in (False, True):
        planned.update(planned_worker_paths(family, label, failure=failure))
        planned.update(base.nested_evidence_paths(family, label,
                                                  version="3", failure=failure))
    for suite in FROZEN_SUITES:
        if suite.recorder_relative is not None:
            planned.update(base.specialized_evidence_paths(
                base.suite_spec(suite.name), family, label))
    for relative in sorted(planned):
        require(relative.startswith("oracle/phase2/evidence/")
                or relative.startswith("experiments/rust_public_practice_v1/"),
                "check only exact independently predetermined evidence routes")
        try:
            os.lstat(str(ROOT / relative))
        except FileNotFoundError:
            continue
        raise CandidateGateError("never overwrite a published candidate result: "
                                 + relative)


def write_fresh_evidence(directory: int, basename: str,
                         content: bytes) -> dict[str, Any]:
    require(type(directory) is int and directory >= 0
            and type(basename) is str and basename not in {"", ".", ".."}
            and "/" not in basename and "\\" not in basename
            and type(content) is bytes and 0 < len(content) <= MAX_REPORT_BYTES,
            "publish only one strictly bounded independently owned V7 result")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(basename, flags, 0o644, dir_fd=directory)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode),
                "publish only a new exact-byte regular V7 evidence file")
        offset = 0
        while offset < len(content):
            written = os.write(descriptor, content[offset:])
            require(type(written) is int and written > 0,
                    "preserve every complete actual V7 evidence byte")
            offset += written
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        visible = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require((before.st_dev, before.st_ino)
                == (after.st_dev, after.st_ino)
                and (after.st_dev, after.st_ino, after.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and after.st_size == len(content),
                "prove the exclusively created original same V7 evidence inode")
        return {"relative": "oracle/phase2/evidence/" + basename,
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content), "device": after.st_dev,
                "inode": after.st_ino, "exclusive_creation": True,
                "file_fsync_completed": True,
                "same_inode_readback_verified": True}
    finally:
        os.close(descriptor)


def publish_actual_report(report: dict[str, Any], options: argparse.Namespace,
                          *, prefix: str = "frozen-p0-candidate-worker-v5-",
                          schema: str = SCHEMA) -> dict[str, Any]:
    family, label = checked_family(options.candidate), checked_label(options.label)
    require(report.get("status") in {"PASS", "FAIL"}
            and report.get("candidate_family") == family
            and report.get("suite_count") == SUITE_COUNT
            and report.get("case_execution_denominator") == CASE_DENOMINATOR
            and report.get("candidate_qualified")
            is (report["status"] == "PASS")
            and report.get("verified_passing_case_count")
            == report.get("qualified_candidate_case_executions"),
            "retain a complete actual failed or fully qualifying V7 candidate")
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT_BYTES,
            "the actual complete lossless V7 report exceeds thirty-two MiB")
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(compressed) <= MAX_REPORT_BYTES,
            "preserve the exact complete deterministic V7 report gzip")
    failed = report["status"] == "FAIL"
    stem = prefix + family + "-" + label + ("-failures" if failed else "")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0))
    directory = os.open(str(ROOT / "oracle/phase2/evidence"), flags)
    try:
        archive = write_fresh_evidence(directory, stem + ".json.gz", compressed)
        check_publication_shape(archive, kind="worker", relative=archive["relative"])
        os.fsync(directory)
        document = {
            "schema": schema + "-durable-publication-receipt",
            "status": "PASS", "candidate_status": report["status"],
            "candidate_family": family, "label": label,
            "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "document_sha256": report["document_sha256"],
            "archive": archive,
            "uncompressed_sha256": hashlib.sha256(plain).hexdigest(),
            "uncompressed_bytes": len(plain),
            "archive_directory_fsync_completed": True,
            "failure_preserved": failed,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "final_holdout_authorized": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        receipt = write_fresh_evidence(
            directory, stem + "-publication-receipt.json", canonical(document))
        check_publication_shape(receipt, kind="worker", relative=receipt["relative"])
        os.fsync(directory)
    finally:
        os.close(directory)
    return {"schema": schema + "-published-complete-candidate",
            "status": report["status"], "candidate_family": family,
            "label": label, "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "completed_candidate_suite_count":
            report["completed_candidate_suite_count"],
            "verified_passing_case_count": report["verified_passing_case_count"],
            "qualified_candidate_case_executions":
            report["qualified_candidate_case_executions"],
            "candidate_qualified": report["candidate_qualified"],
            "complete_archive": archive,
            "complete_publication_receipt": receipt,
            "all_mismatches_crashes_and_timeouts_preserved": True,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "final_holdout_authorized": False,
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False}


def run_actual_candidate(options: argparse.Namespace) -> dict[str, Any]:
    context = authenticate_frozen_context(options)
    if options.activation_source_sha256 == FUTURE_ACTIVATION_SHA256:
        authenticate_canonical_activation_v3(options, context)
        raise CandidateGateError(
            "the independently authenticated V3 activation cannot authorize "
            + options.candidate
            + ": the frozen original CPython, specialized recorder, and "
            "subinterpreter producers support only the actual V2-activated "
            "Rust/C and V2-activated Zig-V3 candidate routes; no candidate "
            "worker was started and no correctness result was invented"
        )
    original = context["v6_options"]
    approval = context["v6_worker"].authenticate_canonical_activation(
        original, context)
    ensure_fresh_run_evidence(options, context)
    results = [observe_actual_suite(suite, options, context, approval)
               for suite in FROZEN_SUITES]
    passing = [row for row in results if row["status"] == "PASS"]
    verified = sum(row["verified_passing_case_count"] for row in results)
    qualified = len(passing) == SUITE_COUNT and verified == CASE_DENOMINATOR
    report = {
        "schema": SCHEMA + "-complete-candidate-evaluation",
        "status": "PASS" if qualified else "FAIL",
        "candidate_family": checked_family(options.candidate),
        "label": checked_label(options.label),
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "document_sha256": options.document_sha256,
        "build_version": str(options.build_version),
        "phase1_inventory_sha256": PHASE1_SHA256,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "attempted_candidate_suite_count": len(results),
        "completed_candidate_suite_count": len(passing),
        "verified_passing_case_count": verified,
        "qualified_candidate_case_executions": verified,
        "actual_semantic_mismatch_count": sum(
            checked_count(row.get("mismatch_count"),
                          row["case_execution_denominator"], row["suite"])
            for row in results),
        "candidate_qualified": qualified, "all_suites": results,
        "all_failure_reasons": [
            {"suite": row["suite"], "failure": row["failure"]}
            for row in results if row["failure"] is not None],
        "pinned_python_owner": context["pinned_python_owner"],
        "six_family_static_independence": context["six_family_static_independence"],
        "corrected_canonical_activation": approval["canonical_activation"],
        "corrected_source_build": approval["source_build"],
        "preserved_v5_actual_campaigns": context["preserved_v5_campaigns"],
        "preserved_v6_zig_actual_campaign": context["preserved_v6_zig_campaign"],
        "preserved_v4_source_build_history": context["preserved_v4_build_history"],
        "preserved_historical_candidate_artifact_count_including_restorations": 51,
        "preserved_historical_artifact_count_including_source_builds": 57,
        "preserved_historical_restoration_receipt_count": 3,
        "source_family_count": 6,
        "fully_runnable_p0_family_count": 3,
        "all_mismatches_crashes_and_timeouts_preserved": True,
        "supplemental_cases_added_to_phase1_denominator": False,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "final_holdout_authorized": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    return publish_actual_report(report, options)


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preserve every independently frozen Python regex candidate outcome.",
        allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--internal-candidate-worker", action="store_true")
    parser.add_argument("--suite")
    parser.add_argument("--candidate", choices=SOURCE_FAMILIES)
    parser.add_argument("--label")
    parser.add_argument("--build-version", choices=("2", "3", "4"))
    parser.add_argument("--build-label")
    parser.add_argument("--activation-root")
    parser.add_argument("--owned-source-sha256", action="append", default=[])
    for name in ("source", "protocol", "document", "build-source",
                 "build-protocol", "build-contract", "build-archive", "build-receipt",
                 "activation-source", "activation-protocol", "activation-contract",
                 "activation-report", "activation-receipt", "recovery-journal",
                 "candidate-source", "native-engine", "native-bridge"):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(arguments)
    if options.self_test:
        require(not any(getattr(options, name) is not None for name in (
            "suite", "candidate", "label", "build_version", "build_label",
            "activation_root", "source_sha256", "protocol_sha256",
            "document_sha256", "build_source_sha256", "build_protocol_sha256",
            "build_contract_sha256", "build_archive_sha256",
            "build_receipt_sha256", "activation_source_sha256",
            "activation_protocol_sha256", "activation_contract_sha256",
            "activation_report_sha256", "activation_receipt_sha256",
            "recovery_journal_sha256", "candidate_source_sha256",
            "native_engine_sha256", "native_bridge_sha256"))
            and not options.owned_source_sha256,
            "a synthetic V7 source test cannot authorize candidate activity")
        return options
    for name in ("source_sha256", "protocol_sha256", "document_sha256",
                 "build_source_sha256", "build_protocol_sha256",
                 "build_contract_sha256",
                 "build_archive_sha256", "build_receipt_sha256",
                 "activation_source_sha256", "activation_protocol_sha256",
                 "activation_contract_sha256",
                 "activation_report_sha256", "activation_receipt_sha256",
                 "recovery_journal_sha256", "candidate_source_sha256",
                 "native_engine_sha256", "native_bridge_sha256"):
        value = getattr(options, name)
        if value is not None:
            checked_digest(value, name)
    require(all(getattr(options, name) is not None for name in (
        "source_sha256", "protocol_sha256", "document_sha256")),
        "independently pin all three separately frozen V7 worker owners")
    if options.verify_frozen_context:
        return options
    names = ("candidate", "label", "build_version", "build_label",
             "activation_root", "build_source_sha256", "build_protocol_sha256",
             "build_archive_sha256", "build_receipt_sha256",
             "activation_source_sha256", "activation_protocol_sha256",
             "activation_report_sha256", "activation_receipt_sha256",
             "candidate_source_sha256", "native_engine_sha256",
             "native_bridge_sha256")
    require(all(getattr(options, name) is not None for name in names)
            and bool(options.owned_source_sha256),
            "pin all genuine source-built candidate, V2 activation and build owners")
    checked_family(options.candidate)
    checked_label(options.label)
    checked_label(options.build_label)
    if options.activation_source_sha256 == ACTIVATION_V2_SHA256:
        require(options.candidate in FAMILIES
                and FAMILY_BUILD_VERSION[options.candidate] == options.build_version
                and options.activation_protocol_sha256 == ACTIVATION_V2_PROTOCOL_SHA256
                and options.activation_contract_sha256 is None
                and options.build_contract_sha256 is None,
                "authorize only exact genuine original three-family V2 activation")
    elif options.activation_source_sha256 == FUTURE_ACTIVATION_SHA256:
        require(options.build_version == "4"
                and options.activation_protocol_sha256 == FUTURE_ACTIVATION_PROTOCOL_SHA256
                and options.activation_contract_sha256 == FUTURE_ACTIVATION_DOCUMENT_SHA256
                and options.build_source_sha256 == BUILD_V4_SHA256
                and options.build_protocol_sha256 == BUILD_V4_PROTOCOL_SHA256
                and options.build_contract_sha256 == BUILD_V4_DOCUMENT_SHA256,
                "reject guessed V3 activation, failed Go builds, or unfrozen V4 contracts")
    else:
        raise CandidateGateError("reject unpinned or fabricated native activation")
    for owner in options.owned_source_sha256:
        require(type(owner) is str and owner.count("=") == 1,
                "pin each genuine independent candidate-owned semantic source")
        relative, fingerprint = owner.split("=", 1)
        require(bool(relative), "retain every actual source-owned candidate path")
        checked_digest(fingerprint, relative)
    if options.internal_candidate_worker:
        require(options.suite is not None,
                "select exactly one independently owned direct original producer")
    else:
        require(options.suite is None,
                "run all frozen suites without selecting an easier subset")
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
        result = {"schema": SCHEMA + "-entry-failure", "status": "FAIL",
                  "error_type": type(error).__qualname__,
                  "error_message": str(error), "hidden_cases_read": 0,
                  "benchmark_files_read": 0, "clock_samples": 0,
                  "timing_trials_run": 0, "performance": "NOT MEASURED",
                  "final_holdout_authorized": False,
                  "candidate_qualified_for_hidden_benchmark": False,
                  "final_winner_selected": False}
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
