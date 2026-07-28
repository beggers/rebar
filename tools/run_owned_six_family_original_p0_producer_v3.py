#!/usr/bin/env python3
"""Replay all original Python ``re`` cases against six first-party engines.

This is a full, directly auditable descendant of the SHA-pinned original V1
evaluator.  V3 preserves every original suite, seed, case, guard, quarantine,
and real subinterpreter lifecycle.  It fixes only the proven native ownership,
native bridge-profile, and archived public-reference infrastructure failures.

Self-tests are wholly synthetic.  Frozen-context verification is strictly
read-only.  Neither mode imports a candidate, starts a reference or candidate
process, builds, activates, samples a clock, or opens the sealed holdout.
"""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
import contextlib
import copy
from dataclasses import dataclass
import hashlib
import importlib
import importlib.abc
import importlib.machinery
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
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_owned_six_family_original_p0_producer_v3.py"
PROTOCOL_RELATIVE = "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md"
DOCUMENT_RELATIVE = "oracle/phase2/six-family-p0-producer-v3.json"
SCHEMA = "rebar-owned-six-family-original-p0-producer-v3"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PHASE1_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
SUITE_COUNT = 13
CASE_DENOMINATOR = 31_237
PRIVATE_WAIVER_COUNT = 13
ORIGINAL_PUBLIC_RECORD_COUNT = 152
ORIGINAL_DEBUG_SKIP_COUNT = 1
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_PLAIN_BYTES = 64 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_PIPE_BYTES = 256 * 1024
MAX_LABEL_BYTES = 48

V7_RUNNER_RELATIVE = "tools/run_frozen_p0_candidate_v7.py"
V7_RUNNER_SHA256 = "08ab73a0d42a2bb3bb658cf6924786a7ba396aacd229957a710866572e178690"
V7_WORKER_RELATIVE = "tools/run_frozen_p0_candidate_worker_v5.py"
V7_WORKER_SHA256 = "66f869e71e1aaf77944f4b7115e91ab34f6bc9b06fb4d17f097ea26c97c9c780"
V7_PROTOCOL_RELATIVE = "oracle/phase2/P0-CANDIDATE-PROTOCOL-V7.md"
V7_PROTOCOL_SHA256 = "ed595cbb3d5f040454da7efff3d8330befb09dda2ac6eebc681b630b96f32733"
V7_DOCUMENT_RELATIVE = "oracle/phase2/p0-candidate-protocol-v7.json"
V7_DOCUMENT_SHA256 = "16f24a46113e0a120fc5cf7fea2122d78e76445665959a9553b610a27b8843b1"

V5_BUILD_RELATIVE = "tools/reproduce_owned_native_source_build_v5.py"
V5_BUILD_SHA256 = "39ba55b6906a2aebf204c878c143894562f317765b0427f4f1f449e35e1dde92"
V5_BUILD_PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILD-V5.md"
V5_BUILD_PROTOCOL_SHA256 = "d2f7ca95cb0df377f4698399f56eea9eb0c237b0ad2f9e3790d74a0bee2246d9"
V5_BUILD_DOCUMENT_RELATIVE = "oracle/phase2/native-source-build-v5.json"
V5_BUILD_DOCUMENT_SHA256 = "a54121391d43f5ee5e2debcdecf06567cb947d2e654142ba622c7adf0681ee11"

ORIGINAL_GATE_RELATIVE = "tools/run_frozen_p0_candidate_v1.py"
ORIGINAL_GATE_SHA256 = "c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8"
ORIGINAL_V5_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
ORIGINAL_V5_SHA256 = "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
NESTED_ORIGINAL_RELATIVE = "tools/run_owned_candidate_subinterpreters_v1.py"
NESTED_ORIGINAL_SHA256 = "45e9b47c7c635fc30ebdb2cb4830d2d1fe382a5a7e4b663fb1a8e0112779e1a7"
NESTED_V3_RELATIVE = "tools/run_owned_candidate_subinterpreters_v3.py"
NESTED_V3_SHA256 = "21febe241549963a2818af2a20782da81bdf952fb7be8affc4289d9ccc9ad5b4"
NESTED_PROJECTED_REFERENCE_SHA256 = "cf5633c8dc1038d650603eee421371285d0e32f6446190ce728590f1f5c55021"
NESTED_CASE_COUNT = 128
NESTED_CASE_EXECUTIONS = 394
NESTED_INTERPRETER_COUNT = 11
NESTED_FRESH_INTERPRETER_COUNT = 8
HISTORICAL_FAILED_ZIG_EXECUTIONS = 385

V2_ACTIVATION_SHA256 = "e6e8a72feffcf670da9a3e4d2e8b642e933c1d81cfe5bf7d1636385f207d6218"
V2_ACTIVATION_PROTOCOL_SHA256 = "a675b411873c01ae88ea50d4f95aab7231a29dde38a458a947437f07ed850529"
V3_ACTIVATION_SHA256 = "39a170d5981e3484366eca223c0533366d92927975271fdb004fbce784b7a21e"
V3_ACTIVATION_PROTOCOL_SHA256 = "17656cd0ea3aa879cc5c69078460118f1e5e977f3e5c8d977c784954ea9f65bf"
V3_ACTIVATION_DOCUMENT_SHA256 = "87d2d34a142f620894b87b35f3216ede4a0374921a3dfacb9d8e209e3d3133fc"

ORIGINAL_V1_OWNERS = {
    "source": (
        "tools/run_owned_six_family_original_p0_producer_v1.py",
        "36451c10221857cca8c77fad7533382f4e3969a20a5cdf73c055beea1d315d33",
        149599,
    ),
    "protocol": (
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V1.md",
        "1e7ed2cbd63e080c563dd49b4ea2a2be284d831d75739c47edecfae50373ce17",
        8711,
    ),
    "document": (
        "oracle/phase2/six-family-p0-producer-v1.json",
        "5206bcc097cd399cddd91a8d0356fd780b44ef7c173d70605d28a175dac71c0b",
        19054,
    ),
}
V21_OWNERS = {
    "source": (
        "tools/render_candidate_current_overview_v21.py",
        "617a64691bf9da7730e44bfed96fe20dbd9c8e38b575e0daf8a3432dbf2625e9",
        75566,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v21.inputs.json",
        "704b2e07e32260ac741b0a914e2ae04a3deb583de317ba170432f85126af5139",
        14631,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v21.json",
        "d2143b09bbf35a7a83977c08a35f6a0c87435a50e478df517099aa719e8fa28c",
        96376,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v21.svg",
        "ba7b82d7552603eb836a0c18e47546390c4e1398bbb74951616e309135b9ce5c",
        8074,
    ),
}
PUBLIC_RECORDER_RELATIVE = (
    "tools/record_independent_public_type_identity_serialization_v1.py"
)
PUBLIC_RECORDER_SHA256 = (
    "ee3e6fc00991758fee93b710a63dad9094f881f1ea57777cae2415397f752eae"
)
PUBLIC_RECORDER_BYTES = 220890
PUBLIC_BASELINE_LABEL = "shared-suite-v1"
PUBLIC_BASELINE_ARCHIVE_RELATIVE = (
    "experiments/rust_public_practice_v1/"
    "public-type-identity-serialization-v1-shared-suite-v1.json.gz"
)
PUBLIC_BASELINE_ARCHIVE_SHA256 = (
    "8956c0b26e074d1537a47047062fb51e11d3f0196dc97ce4a6e24d2ae45128e2"
)
PUBLIC_BASELINE_ARCHIVE_BYTES = 2926031
PUBLIC_BASELINE_RECEIPT_RELATIVE = (
    "experiments/rust_public_practice_v1/"
    "public-type-identity-serialization-v1-shared-suite-v1-publication-receipt.json"
)
PUBLIC_BASELINE_RECEIPT_SHA256 = (
    "6a8ce4334d0b605483e0f78a909f620a8bcdd0e5ad8cdb4fae4960fc237132fd"
)
PUBLIC_BASELINE_RECEIPT_BYTES = 7596
PUBLIC_BASELINE_UNCOMPRESSED_SHA256 = (
    "64ff0810882fd1cc0ba343de127145ae4051ab78e07a0d76f8be21cdfd7f6174"
)
PUBLIC_BASELINE_UNCOMPRESSED_BYTES = 55903155
PUBLIC_REFERENCE_PIDS = (82, 83)
PUBLIC_REFERENCE_STDOUT = (
    ("26b9ae69b1ecc49340599eb6e288ccd9077c4c722305cb527585bc02a56524b1",
     15719219),
    ("20ac1c3bc93aa855ed6cf671921e3e2218b04a0e32ba3226fe84c72d8a627bdf",
     15719219),
)
RESTORED_C_NATIVE_RELATIVE = (
    "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"
)
RESTORED_C_NATIVE_SHA256 = (
    "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd"
)
RESTORED_C_NATIVE_BYTES = 149976
V8_BUILD_OWNERS = {
    "source": (
        "tools/reproduce_owned_native_source_build_v8.py",
        "afc4f8070cb3c1bccf312b77b019cbb6d71f8dcf976f4a2e921e18cc7c063dd4",
        63656,
    ),
    "protocol": (
        "oracle/phase2/NATIVE-SOURCE-BUILD-V8.md",
        "376aae2bdcbeb0c399369c2a15e7e39efb2b1bcce53129a20c229fbbb995cda2",
        4498,
    ),
    "document": (
        "oracle/phase2/native-source-build-v8.json",
        "7f463b70367156d65e73b561629bd1e14ae265b2273afae9b0a984608492019b",
        6207,
    ),
}
V5_ACTIVATION_OWNERS = {
    "source": (
        "tools/activate_verified_native_candidate_v5.py",
        "bdfcb93e4ac3f436474cf82725165c92b61c8982efff0bf113900cbce3e8aff5",
        78853,
    ),
    "protocol": (
        "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V5.md",
        "4693558f9796a0fbf38326fda3a86b2cf19348598b21eab60610df6ee7f241bc",
        5610,
    ),
    "document": (
        "oracle/phase2/verified-native-activation-v5.json",
        "a580c6b745c867a69f1f017506c1feec8310aa3070bfd58abd006740b01948da",
        6223,
    ),
}
OUTER_CAMPAIGN_ARCHIVE = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v1-c-phase2-v8-original-p0-failures.json.gz",
    "a8319a686c2486e27374bfb9c6ada4e4ec104c27c1cafdbc2205c98f40fa9fb7",
    5120,
)
OUTER_CAMPAIGN_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v1-c-phase2-v8-original-p0-failures-"
    "publication-receipt.json",
    "034207331f8d61ef69f510cb42b9babe921b85570c571198ea8eb310c75ffecd",
    933,
)
BRIDGE_METHOD_PROFILES = {
    "c": (
        "build", "match", "collect", "configure", "pattern_type",
        "escape", "check_recursion",
    ),
    "rust": ("compile", "pattern_type", "pattern_descriptors", "run", "collect"),
    "zig": ("compile", "initialize_pattern", "free", "collect"),
    "cpp": ("compile", "subject", "run"),
    "go": ("compile", "execute"),
    "fortran": ("compile", "subject", "run"),
}
PRESERVED_EVIDENCE_OWNER_COUNT = 103
PRESERVED_REFERENCE_PATH_COUNT = 108
PRESERVED_NEW_CAMPAIGN_OWNER_COUNT = 30


class ProducerError(Exception):
    """An original case, native owner, or real observation cannot be proven."""


class SourceOnlyViolation(ProducerError):
    """A source-only check tried to cause an external effect."""


class ActualSuiteFailure(ProducerError):
    """Keep the complete genuinely observed partial failure."""

    def __init__(self, message: str, details: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.details = dict(details)


@dataclass(frozen=True, slots=True)
class SuiteSpec:
    name: str
    case_count: int
    source_relative: str
    source_sha256: str
    matrix_sha256: str
    reference_sha256: str
    seed: int | None
    route: str


@dataclass(frozen=True, slots=True)
class FamilySpec:
    name: str
    module: str
    adapter_relative: str
    bridge_module: str
    engine_relative: str
    bridge_relative: str
    source_owners: tuple[tuple[str, str, int], ...]
    combined_native: bool
    owned_ctypes: bool


SUITES: tuple[SuiteSpec, ...] = (
    SuiteSpec("original_bounded_v5", 151, ORIGINAL_V5_RELATIVE,
              ORIGINAL_V5_SHA256,
              "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240",
              "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276",
              None, "unchanged-165-method-upstream-source"),
    SuiteSpec("public_v3", 864, "tools/rust_public_practice_benchmark_v1.py",
              "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37",
              "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e",
              "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c",
              5928217332825411633, "unchanged-public-source-evaluator"),
    SuiteSpec("scanner_v3", 1024, "tools/rust_scanner_differential_v1.py",
              "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7",
              "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c",
              "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d",
              5999710933164053041, "unchanged-scanner-and-callback-evaluator"),
    SuiteSpec("buffer_v3", 768, "tools/rust_memoryview_expand_differential_v1.py",
              "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6",
              "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60",
              "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75",
              5567953616029762609, "unchanged-memoryview-evaluator"),
    SuiteSpec("managed_v1", 1024, "tools/independent_managed_buffer_lifetime_v1.py",
              "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489",
              "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976",
              "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df",
              5567095966978627121, "unchanged-real-buffer-lifetime-evaluator"),
    SuiteSpec("scanner_verbose_v1", 2854,
              "tools/independent_scanner_verbose_comments_v1.py",
              "5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d",
              "01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b",
              "d7e2d499eb4dbe6ae0f8743d8b152e4835898656daa8b3167598636ef7be6012",
              5999725261024810545, "unchanged-verbose-tokenizer-evaluator"),
    SuiteSpec("public_types_v1", 6912,
              "tools/independent_public_type_identity_serialization_v1.py",
              "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20",
              "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123",
              "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21",
              6077977430793212465, "unchanged-public-type-and-pickle-evaluator"),
    SuiteSpec("substitution_v2", 5120,
              "tools/independent_substitution_buffer_semantics_v2.py",
              "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573",
              "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54",
              "2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b",
              6004778603531028017, "unchanged-substitution-and-callback-evaluator"),
    SuiteSpec("shape_v2", 10240,
              "tools/independent_shape_changing_buffer_semantics_v2.py",
              "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c",
              "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8",
              "58bbc78828ba2d4cde6b99cbebea815ce9381cda24d0acec03f6cc095b8b643c",
              6001118316486346290, "unchanged-real-changing-buffer-evaluator"),
    SuiteSpec("public_surface_v19", 1376,
              "tools/python_re_public_surface_oracle_stage19.py",
              "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e",
              "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa",
              "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef",
              2026072483, "unchanged-real-64-locale-and-192-transition-evaluator"),
    SuiteSpec("subinterpreter_v2", 128,
              "tools/python_re_subinterpreter_oracle_v2.py",
              "54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8",
              "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3",
              "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8",
              2026072501, "unchanged-real-128-case-394-call-11-interpreter-lifecycle"),
    SuiteSpec("pep688_v4", 264,
              "tools/python_re_buffer_exporter_oracle_v4.py",
              "8da0b8e5c5519e7335cd1b53ceb7042f1da1f902c486ad8ac35ddf53d8a04490",
              "2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891",
              "7827586e0c7d4f43ac1fbd288f6b28f6a44b810b46274830d3803505c76692a8",
              None, "unchanged-real-python-buffer-exporter-evaluator"),
    SuiteSpec("threaded_pattern_v1", 512,
              "tools/python_re_threaded_pattern_oracle_v1.py",
              "05226e59736d8721a975eda8afa10247213999690c2766a7b3235c567b9f8276",
              "a7d467e3e529204946fe00ddb819e734421e7087ea909af9ec24b757e42afa0b",
              "928ea100d6fdaecc7c1dcf01e32c24fd98a146964c0955989a8149c1216ffe81",
              2026072701, "unchanged-real-barrier-synchronized-shared-pattern-threads"),
)


OWNED_SOURCES: dict[str, tuple[tuple[str, str, int], ...]] = {
    "c": (
        ("candidates/vm_candidate.py", "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096", 60707),
        ("candidates/_vm_native.c", "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55", 218185),
    ),
    "rust": (
        ("candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151),
        ("candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676),
        ("candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
        ("candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
        ("candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
        ("candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
        ("candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
        ("candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
        ("candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
    ),
    "zig": (
        ("candidates/zig_candidate.py", "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862", 68422),
        ("candidates/zig/mini_regex.zig", "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28", 186915),
        ("candidates/zig/py_bridge.c", "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b", 173026),
    ),
    "cpp": (
        ("candidates/cpp_candidate.py", "8dcece29b1a194eea023143148af37bb679a9df4c39c01153f5ee23f778e16d5", 27488),
        ("candidates/cpp/engine.hpp", "66998fed1839f5e5f7f09382830ed9fda1a62b80bd545305c4eee95ed9a13df9", 4089),
        ("candidates/cpp/engine.cpp", "a9ceb37cfde77447a01a36a8882f7713faf5f201d7a15a193dd17e7b91d118f5", 62813),
        ("candidates/cpp/py_bridge.cpp", "1d930b63b2f9493dd4759b7521f75d8846daf2580a5699337fcf82540484ab6d", 25068),
    ),
    "go": (
        ("candidates/go_candidate.py", "816d21527b9806afbc9457122f72f8f6b62c39b8b791d3f363745d412cbe3d20", 31049),
        ("candidates/go/go.mod", "9297c4e8fe4649196150400d23a4da584d7ef721347f7095399a7382edad669b", 44),
        ("candidates/go/engine.go", "6472c4413921f3a877455315400c532e7632a871a96d46de9583fa6170a43192", 53782),
        ("candidates/go/py_bridge.c", "52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a", 39373),
    ),
    "fortran": (
        ("candidates/fortran_candidate.py", "8db564771d38c0896a5207f1241a44463432dc5bf75dfcf657740d8bcfefd194", 26521),
        ("candidates/fortran/engine.f90", "5180da085487b9932e3f769e6baded6a8409a0b778890e6197aaea6dad1923a5", 85062),
        ("candidates/fortran/py_bridge.c", "8540b708de4819f1b3340c32e78eaf083c1cad35f016c0f7af33a27773694b0d", 26311),
    ),
}


FAMILIES: dict[str, FamilySpec] = {
    "rust": FamilySpec("rust", "candidates.rust_candidate",
                       "candidates/rust_candidate.py", "candidates._rust_bridge",
                       "candidates/_rust_engine.so",
                       "candidates/_rust_bridge" + EXTENSION_SUFFIX,
                       OWNED_SOURCES["rust"], False, False),
    "c": FamilySpec("c", "candidates.vm_candidate",
                    "candidates/vm_candidate.py", "candidates._vm_native",
                    "candidates/_vm_native" + EXTENSION_SUFFIX,
                    "candidates/_vm_native" + EXTENSION_SUFFIX,
                    OWNED_SOURCES["c"], True, False),
    "zig": FamilySpec("zig", "candidates.zig_candidate",
                      "candidates/zig_candidate.py", "candidates._zig_bridge",
                      "candidates/_zig_probe.so",
                      "candidates/_zig_bridge" + EXTENSION_SUFFIX,
                      OWNED_SOURCES["zig"], False, True),
    "cpp": FamilySpec("cpp", "candidates.cpp_candidate",
                      "candidates/cpp_candidate.py", "candidates._cpp_bridge",
                      "candidates/_cpp_bridge" + EXTENSION_SUFFIX,
                      "candidates/_cpp_bridge" + EXTENSION_SUFFIX,
                      OWNED_SOURCES["cpp"], True, False),
    "go": FamilySpec("go", "candidates.go_candidate",
                     "candidates/go_candidate.py", "candidates._go_bridge",
                     "candidates/_go_engine.so",
                     "candidates/_go_bridge" + EXTENSION_SUFFIX,
                     OWNED_SOURCES["go"], False, False),
    "fortran": FamilySpec("fortran", "candidates.fortran_candidate",
                          "candidates/fortran_candidate.py",
                          "candidates._fortran_bridge",
                          "candidates/_fortran_engine.so",
                          "candidates/_fortran_bridge" + EXTENSION_SUFFIX,
                          OWNED_SOURCES["fortran"], False, False),
}


HISTORICAL_V5_BUILDS: dict[str, dict[str, Any]] = {
    "go": {
        "family": "go",
        "label": "phase2-v5",
        "status": "FAIL",
        "archive_relative": "oracle/phase2/evidence/native-source-build-v5-go-phase2-v5-failures.json.gz",
        "archive_sha256": "ff92f5f182307b5e6e123ab883e630c6aca63f8c75318fa4ac083b1d72db6169",
        "archive_bytes": 5595,
        "uncompressed_sha256": "7dfa02625cb532d2dd65491a65ca8a04848041fc6dc2fd5547bac2e3c8b7a685",
        "uncompressed_bytes": 18380,
        "receipt_relative": "oracle/phase2/evidence/native-source-build-v5-go-phase2-v5-failures-publication-receipt.json",
        "receipt_sha256": "00a126f6c462913ad00ea9961334bbeb5aa2bfd1301d02d8f8c5d55c2e239db0",
        "receipt_bytes": 2903,
        "actual_process_count": 5,
        "expected_process_count": 26,
        "completed_phase_count": 0,
        "expected_process_names": (
            "readelf_version", "gcc_version", "go_version",
            "build_go_engine", "build_go_bridge",
        ),
        "failed_process": "build_go_bridge",
        "required_diagnostic": "SSIZE_MAX",
        "failed_stderr_sha256": "6477560bffdde31d9422ba4c8addbb1a733cb0becbd09b5815d51d837caf477a",
        "failed_stderr_bytes": 2640,
    },
    "fortran": {
        "family": "fortran",
        "label": "phase2-v5",
        "status": "FAIL",
        "archive_relative": "oracle/phase2/evidence/native-source-build-v5-fortran-phase2-v5-failures.json.gz",
        "archive_sha256": "eadf8844a1bda48d2420c7b3311ced77de9fda7ccfb806f73764550080823e53",
        "archive_bytes": 26274,
        "uncompressed_sha256": "4e3a8a2e9cb03fe12105f40499da6055b9adb3336667b9af801579106b991996",
        "uncompressed_bytes": 167482,
        "receipt_relative": "oracle/phase2/evidence/native-source-build-v5-fortran-phase2-v5-failures-publication-receipt.json",
        "receipt_sha256": "f9bf0a652e9c10c949d7b5faabf261d3931681548d4f5d1af69f0accc6d742f2",
        "receipt_bytes": 2848,
        "actual_process_count": 26,
        "expected_process_count": 26,
        "completed_phase_count": 2,
        "expected_process_names": None,
        "failed_process": None,
        "required_diagnostic": None,
        "first_engine_sha256": "6f005b6f1ec68658857ee2ba9c21e21d65cd4c41aa8fd608d6060712db63164a",
        "second_engine_sha256": "0d1f94c1b51e0cf6527ce742c092bffe9f0ae1207b0414bab6b5be56e9b7f092",
        "engine_bytes": 74624,
        "identical_bridge_sha256": "0e4197e9b16df93f5d29333fcfda928d1d29c193c0449afb730146819229faf8",
        "bridge_bytes": 37424,
    },
}


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise ProducerError(message)


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require one complete lowercase SHA-256: " + label)
    return value


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           separators=(",", ":"), sort_keys=True)
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, OverflowError, RecursionError,
            UnicodeError) as error:
        raise ProducerError("require complete finite canonical evidence") from error


def sha256(value: bytes) -> str:
    require(type(value) is bytes, "hash only genuine bytes")
    return hashlib.sha256(value).hexdigest()


def unique_json(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "reject repeated or nonstring canonical evidence fields")
        result[key] = value
    return result


def decode_document(raw: Any, label: str, *, canonical_required: bool = False) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PLAIN_BYTES,
            "bound the complete original evidence: " + label)
    try:
        value = json.loads(raw.decode("utf-8", "strict"),
                           object_pairs_hook=unique_json,
                           parse_constant=lambda item: (_ for _ in ()).throw(
                               ValueError("nonfinite evidence: " + item)))
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ProducerError("reject invalid or duplicated evidence: " + label) from error
    require(type(value) is dict, "require one complete evidence object: " + label)
    if canonical_required:
        require(canonical(value) == raw,
                "reject changed canonical source evidence: " + label)
    return value


def checked_label(value: Any, label: str = "label") -> str:
    require(type(value) is str and 0 < len(value.encode("utf-8")) <= MAX_LABEL_BYTES
            and all(char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
                    for char in value),
            "require one exact bounded " + label)
    return value


def family_spec(value: Any) -> FamilySpec:
    require(type(value) is str and value in FAMILIES,
            "select one of the six independently owned native engines")
    result = FAMILIES[value]
    require(type(result) is FamilySpec and result.name == value
            and result.module.startswith("candidates.")
            and result.bridge_module.startswith("candidates.")
            and result.module != result.bridge_module
            and result.adapter_relative.startswith("candidates/")
            and result.bridge_relative.startswith("candidates/")
            and result.bridge_relative.endswith(EXTENSION_SUFFIX)
            and (result.engine_relative == result.bridge_relative)
            is result.combined_native
            and result.combined_native is (value in {"c", "cpp"})
            and result.owned_ctypes is (value == "zig")
            and result.source_owners == OWNED_SOURCES[value]
            and result.adapter_relative in {
                relative for relative, _, _ in result.source_owners
            }, "reject a substituted, crossed, or borrowed native family")
    return result


def suite_spec(value: Any) -> SuiteSpec:
    selected = [item for item in SUITES if item.name == value]
    require(type(value) is str and len(selected) == 1,
            "select exactly one unchanged frozen original suite")
    return selected[0]


def verify_runtime(*, permit_candidate: bool = False) -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and os.path.realpath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "run only the exact isolated, pinned, no-bytecode CPython 3.14.6")
    if not permit_candidate:
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
                "verification must never import a native candidate")


def safe_relative(value: Any) -> str:
    require(type(value) is str and bool(value) and "\x00" not in value,
            "require one exact relative first-party path")
    path = Path(value)
    require(not path.is_absolute() and tuple(path.parts)
            and all(part not in {"", ".", ".."} for part in path.parts)
            and str(path) == value,
            "reject broad, absolute, parent, symlink, or ambiguous paths")
    target = ROOT / path
    require(os.path.abspath(str(target)) == str(target)
            and os.path.realpath(str(target)) == str(target),
            "reject a symlinked original source or historical owner")
    return value


def read_owned(relative: str, expected: str, *, maximum: int,
               exact_size: int | None = None) -> tuple[bytes, dict[str, Any]]:
    relative = safe_relative(relative)
    expected = checked_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "bound every exact first-party source owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / relative), flags)
    try:
        before = os.fstat(descriptor)
        visible = os.stat(str(ROOT / relative), follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and 0 < before.st_size <= maximum
                and (exact_size is None or before.st_size == exact_size),
                "reject a substituted, linked, empty, oversized, or resized owner: "
                + relative)
        digest = hashlib.sha256()
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part),
                    "reject a truncated independently owned file: " + relative)
            pieces.append(part)
            digest.update(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"",
                "reject unrecorded bytes after a frozen owner: " + relative)
        after = os.fstat(descriptor)
        final = os.stat(str(ROOT / relative), follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (after.st_dev, after.st_ino, after.st_size)
                == (final.st_dev, final.st_ino, final.st_size)
                and digest.hexdigest() == expected,
                "reject a changed inode, source, timestamp, or digest: " + relative)
        raw = b"".join(pieces)
        return raw, {
            "relative": relative, "path": str(ROOT / relative),
            "sha256": expected, "size_bytes": len(raw),
            "device": after.st_dev, "inode": after.st_ino,
            "mode": stat.S_IMODE(after.st_mode),
            "no_follow": True, "same_inode_readback_verified": True,
        }
    finally:
        os.close(descriptor)


def frozen_module(relative: str, digest: str) -> types.ModuleType:
    read_owned(relative, digest, maximum=MAX_SOURCE_BYTES)
    if not sys.path or sys.path[0] != str(ROOT):
        sys.path.insert(0, str(ROOT))
    module_name = relative.removesuffix(".py").replace("/", ".")
    module = importlib.import_module(module_name)
    require(type(module) is types.ModuleType and module.__name__ == module_name
            and os.path.abspath(str(getattr(module, "__file__", "")))
            == str(ROOT / relative)
            and os.path.realpath(str(module.__file__)) == str(ROOT / relative),
            "import only the exact independently pinned first-party source: " + relative)
    read_owned(relative, digest, maximum=MAX_SOURCE_BYTES)
    return module


def owner_protocol(spec: FamilySpec) -> dict[str, Any]:
    return {
        "family": spec.name, "module": spec.module,
        "adapter_relative": spec.adapter_relative,
        "bridge_module": spec.bridge_module,
        "engine_relative": spec.engine_relative,
        "bridge_relative": spec.bridge_relative,
        "combined_native_engine_and_bridge": spec.combined_native,
        "owned_ctypes_allowed": spec.owned_ctypes,
        "owned_source_count": len(spec.source_owners),
        "sources": [{"relative": path, "sha256": digest,
                     "size_bytes": size}
                    for path, digest, size in spec.source_owners],
    }


def suite_protocol(spec: SuiteSpec) -> dict[str, Any]:
    return {
        "id": spec.name,
        "case_execution_count": spec.case_count,
        "source_relative": spec.source_relative,
        "source_sha256": spec.source_sha256,
        "matrix_sha256": spec.matrix_sha256,
        "reference_records_sha256": spec.reference_sha256,
        "published_seed_decimal": None if spec.seed is None else str(spec.seed),
        "unchanged_original_producer_route": spec.route,
    }


def historical_protocol() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for name, value in sorted(HISTORICAL_V5_BUILDS.items()):
        rows.append({
            key: list(item) if isinstance(item, tuple) else item
            for key, item in value.items()
        })
        require(name == value["family"], "bind the actual V5 build history to its owner")
    return {
        "frozen_v7_candidate_evidence_owner_count": 51,
        "frozen_v4_source_build_evidence_owner_count": 6,
        "frozen_v5_source_build_evidence_owner_count": 2 * len(rows),
        "original_v1_historical_evidence_owner_count": 57 + 2 * len(rows),
        "preserved_v20_evidence_owner_count": 73,
        "preserved_v20_reference_path_count": 78,
        "new_repaired_c_campaign_evidence_owner_count": (
            PRESERVED_NEW_CAMPAIGN_OWNER_COUNT
        ),
        "total_distinct_evidence_owner_count": PRESERVED_EVIDENCE_OWNER_COUNT,
        "total_authenticated_reference_path_count": (
            PRESERVED_REFERENCE_PATH_COUNT
        ),
        "actual_repaired_c_suite_count": SUITE_COUNT,
        "actual_repaired_c_case_denominator": CASE_DENOMINATOR,
        "actual_repaired_c_infrastructure_failure_count": SUITE_COUNT,
        "actual_repaired_c_verified_passing_case_count": 0,
        "actual_repaired_c_failure_causes": {
            "PYTHON-COMPATIBLE PUBLIC TYPE OWNERSHIP CHECK": 12,
            "SAVED PYTHON REFERENCE DECODING": 1,
        },
        "repaired_c_campaign_archive": {
            "relative": OUTER_CAMPAIGN_ARCHIVE[0],
            "sha256": OUTER_CAMPAIGN_ARCHIVE[1],
            "size_bytes": OUTER_CAMPAIGN_ARCHIVE[2],
        },
        "repaired_c_campaign_receipt": {
            "relative": OUTER_CAMPAIGN_RECEIPT[0],
            "sha256": OUTER_CAMPAIGN_RECEIPT[1],
            "size_bytes": OUTER_CAMPAIGN_RECEIPT[2],
        },
        "source_builds": rows,
        "failed_zig_is_not_a_success": {
            "actual_case_interpreter_exec_calls": 385,
            "actual_initialization_interpreter_exec_calls": 3,
            "actual_guard_cleanup_interpreter_exec_calls": 4,
            "actual_interpreters_created": 3,
            "actual_interpreters_destroyed": 3,
            "cleanup_failure_count": 3,
            "verified_passing_nested_cases": 0,
            "candidate_status": "FAIL",
        },
    }


def protocol_document() -> dict[str, Any]:
    families = [owner_protocol(family_spec(name))
                for name in ("rust", "c", "zig", "cpp", "go", "fortran")]
    owners = [row["relative"] for family in families for row in family["sources"]]
    require(len(owners) == len(set(owners)) == 25,
            "freeze exactly 25 genuinely independent semantic source owners")
    rows = [suite_protocol(spec) for spec in SUITES]
    require(len(rows) == SUITE_COUNT
            and len({row["id"] for row in rows}) == SUITE_COUNT
            and sum(row["case_execution_count"] for row in rows) == CASE_DENOMINATOR,
            "preserve all 13 original suites and all 31,237 original cases")
    return {
        "schema": CONTRACT_SCHEMA,
        "version": 3,
        "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        "goal_sha256": GOAL_SHA256,
        "pinned_cpython": {
            "version": "3.14.6", "path": PINNED_PYTHON,
            "sha256": PINNED_PYTHON_SHA256,
        },
        "phase_one": {
            "inventory_relative": PHASE1_RELATIVE,
            "inventory_sha256": PHASE1_SHA256,
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_DENOMINATOR,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "original_public_record_count": ORIGINAL_PUBLIC_RECORD_COUNT,
            "original_real_debug_skip_count": ORIGINAL_DEBUG_SKIP_COUNT,
            "supplemental_cases_added": False,
        },
        "frozen_original_v1_producer": {
            key: {
                "relative": item[0], "sha256": item[1],
                "size_bytes": item[2],
            }
            for key, item in sorted(ORIGINAL_V1_OWNERS.items())
        },
        "frozen_original_v5_evaluator": {
            "relative": ORIGINAL_V5_RELATIVE,
            "sha256": ORIGINAL_V5_SHA256,
            "supported_upstream_native_families": ["rust", "c", "zig"],
            "unsupported_families_use_complete_v1_owner_policy": [
                "cpp", "go", "fortran",
            ],
        },
        "frozen_v21_history": {
            "owners": {
                key: {
                    "relative": item[0], "sha256": item[1],
                    "size_bytes": item[2],
                }
                for key, item in sorted(V21_OWNERS.items())
            },
            "actual_evidence_owner_count": PRESERVED_EVIDENCE_OWNER_COUNT,
            "authenticated_reference_path_count": (
                PRESERVED_REFERENCE_PATH_COUNT
            ),
            "new_actual_campaign_owner_count": (
                PRESERVED_NEW_CAMPAIGN_OWNER_COUNT
            ),
        },
        "frozen_public_type_reference": {
            "recorder_relative": PUBLIC_RECORDER_RELATIVE,
            "recorder_sha256": PUBLIC_RECORDER_SHA256,
            "recorder_size_bytes": PUBLIC_RECORDER_BYTES,
            "baseline_label": PUBLIC_BASELINE_LABEL,
            "archive_relative": PUBLIC_BASELINE_ARCHIVE_RELATIVE,
            "archive_sha256": PUBLIC_BASELINE_ARCHIVE_SHA256,
            "archive_size_bytes": PUBLIC_BASELINE_ARCHIVE_BYTES,
            "receipt_relative": PUBLIC_BASELINE_RECEIPT_RELATIVE,
            "receipt_sha256": PUBLIC_BASELINE_RECEIPT_SHA256,
            "receipt_size_bytes": PUBLIC_BASELINE_RECEIPT_BYTES,
            "uncompressed_sha256": PUBLIC_BASELINE_UNCOMPRESSED_SHA256,
            "uncompressed_size_bytes": PUBLIC_BASELINE_UNCOMPRESSED_BYTES,
            "reference_pids": list(PUBLIC_REFERENCE_PIDS),
            "reference_stdout": [
                {"sha256": sha, "size_bytes": size}
                for sha, size in PUBLIC_REFERENCE_STDOUT
            ],
            "case_count": 6912,
            "records_sha256": (
                "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21"
            ),
            "source_owned_validators": [
                "authenticate_baseline_receipt", "stream_baseline_archive",
                "validate_archived_baseline", "validate_public_baseline_result",
            ],
            "candidate_family_selected_by_baseline": False,
            "new_reference_processes_started": 0,
        },
        "native_bridge_profiles": {
            name: {
                "required_extension_owned_builtins": list(profile),
                "all_builtins_bound_to_exact_bridge": True,
                "bridge_match_type_required": name in {"rust", "c", "zig"},
                "python_compatible_re_module_names_required": (
                    name in {"rust", "c", "zig"}
                ),
                "direct_native_pattern_base_required": name == "c",
                "adapter_owned_public_types_required": (
                    name in {"cpp", "go", "fortran"}
                ),
                "adapter_owned_go_create_constructors_required": name == "go",
            }
            for name, profile in sorted(BRIDGE_METHOD_PROFILES.items())
        },
        "frozen_v8_source_build": {
            key: {
                "relative": item[0], "sha256": item[1],
                "size_bytes": item[2],
            }
            for key, item in sorted(V8_BUILD_OWNERS.items())
        },
        "frozen_v5_activation": {
            key: {
                "relative": item[0], "sha256": item[1],
                "size_bytes": item[2],
            }
            for key, item in sorted(V5_ACTIVATION_OWNERS.items())
        },
        "frozen_v7": {
            "runner_relative": V7_RUNNER_RELATIVE,
            "runner_sha256": V7_RUNNER_SHA256,
            "worker_relative": V7_WORKER_RELATIVE,
            "worker_sha256": V7_WORKER_SHA256,
            "protocol_relative": V7_PROTOCOL_RELATIVE,
            "protocol_sha256": V7_PROTOCOL_SHA256,
            "document_relative": V7_DOCUMENT_RELATIVE,
            "document_sha256": V7_DOCUMENT_SHA256,
            "historically_runnable_family_count": 3,
            "qualified_candidate_count": 0,
        },
        "frozen_v5_source_build": {
            "source_relative": V5_BUILD_RELATIVE,
            "source_sha256": V5_BUILD_SHA256,
            "protocol_relative": V5_BUILD_PROTOCOL_RELATIVE,
            "protocol_sha256": V5_BUILD_PROTOCOL_SHA256,
            "document_relative": V5_BUILD_DOCUMENT_RELATIVE,
            "document_sha256": V5_BUILD_DOCUMENT_SHA256,
            "v5_aware_activation": "NOT AVAILABLE; FAIL CLOSED",
        },
        "families": families,
        "family_count": len(families),
        "source_owner_count": len(owners),
        "pairwise_shared_semantic_source_count": 0,
        "suites": rows,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "successful_nested_lifecycle": {
            "counted_case_count": NESTED_CASE_COUNT,
            "actual_case_interpreter_exec_calls": NESTED_CASE_EXECUTIONS,
            "actual_initialization_interpreter_exec_calls": NESTED_INTERPRETER_COUNT,
            "actual_guard_cleanup_interpreter_exec_calls": NESTED_INTERPRETER_COUNT,
            "actual_interpreters_created": NESTED_INTERPRETER_COUNT,
            "actual_interpreters_destroyed": NESTED_INTERPRETER_COUNT,
            "actual_fresh_temporary_interpreters": NESTED_FRESH_INTERPRETER_COUNT,
            "projected_reference_records_sha256": NESTED_PROJECTED_REFERENCE_SHA256,
            "source_relative": NESTED_ORIGINAL_RELATIVE,
            "source_sha256": NESTED_ORIGINAL_SHA256,
            "historical_v3_relative": NESTED_V3_RELATIVE,
            "historical_v3_sha256": NESTED_V3_SHA256,
        },
        "historical_evidence": historical_protocol(),
        "activation_policy": {
            "rust": {"native_build_version": 2, "activation_version": 2},
            "c": {"native_build_version": 2, "activation_version": 2},
            "zig": {"native_build_version": 3, "activation_version": 2},
            "cpp": {"native_build_version": 4, "activation_version": 3},
            "go": "NO PASS BUILD OR VERIFIED ACTIVATION; FAIL CLOSED",
            "fortran": "NO PASS BUILD AND VERIFIED ACTIVATION; FAIL CLOSED",
            "repaired_c_v8_source_build_with_v5_activation": (
                "FROZEN; VERIFY EXISTING LIVE ACTIVATION ONLY"
            ),
            "v5_build_without_v5_aware_activation": "FAIL CLOSED",
            "activation_creates_or_replaces_targets": False,
            "source_build_started": False,
        },
        "independence_policy": {
            "candidate_regex_stdlib_allowed": False,
            "candidate_sre_allowed": False,
            "third_party_regex_allowed": False,
            "cross_family_source_allowed": False,
            "cross_family_native_engine_allowed": False,
            "fallback_allowed": False,
            "actual_source_and_native_owner_proof_required": True,
            "continuous_original_matcher_identity_guard_required": True,
            "upstream_original_authenticator_restricted_to_rust_c_zig": True,
            "exact_source_backed_native_builtin_profiles_required": True,
            "original_public_reference_recorder_required": True,
            "new_public_reference_processes_allowed": False,
            "all_103_evidence_owners_must_be_authenticated": True,
            "all_108_reference_paths_must_be_authenticated": True,
        },
        "verification_effects": {
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "actual_reference_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
            "actual_native_promotions": 0,
            "actual_interpreters_created": 0,
            "actual_threads_started": 0,
            "actual_subprocesses_started": 0,
            "actual_native_libraries_loaded": 0,
            "actual_network_requests": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "candidate_qualified_count": 0,
            "winner_selected": False,
        },
    }


def validate_protocol_document(document: Any) -> dict[str, Any]:
    expected = protocol_document()
    require(type(document) is dict and canonical(document) == canonical(expected),
            "reject any changed suite, case, seed, source, family, history, "
            "activation policy, nested lifecycle, or zero-effect boundary")
    return document


class EffectBoundary:
    """Block actual processes, writes, clocks, networks, threads and candidates."""

    def __init__(self, *, source_only: bool) -> None:
        self.source_only = source_only
        self.installed: list[tuple[Any, str, Any]] = []
        self.counts: dict[str, int] = {
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "actual_reference_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
            "actual_native_promotions": 0,
            "actual_interpreters_created": 0,
            "actual_threads_started": 0,
            "actual_subprocesses_started": 0,
            "actual_native_libraries_loaded": 0,
            "actual_network_requests": 0,
            "actual_file_reads": 0,
            "actual_file_writes": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "blocked_file_operations": 0,
            "blocked_process_operations": 0,
            "blocked_thread_operations": 0,
            "blocked_clock_operations": 0,
            "blocked_network_operations": 0,
            "blocked_import_operations": 0,
            "blocked_temporary_operations": 0,
            "blocked_native_operations": 0,
        }
        self.original_modules: frozenset[str] = frozenset()

    def replace(self, owner: Any, name: str,
                callback: Callable[..., Any]) -> None:
        if hasattr(owner, name):
            previous = getattr(owner, name)
            self.installed.append((owner, name, previous))
            setattr(owner, name, callback)

    def blocked(self, counter: str, operation: str) -> Callable[..., Any]:
        def fail(*args: Any, **kwargs: Any) -> Any:
            self.counts[counter] += 1
            raise SourceOnlyViolation("a verification cannot " + operation)
        return fail

    def __enter__(self) -> EffectBoundary:
        self.original_modules = frozenset(sys.modules)
        for owner, name, counter, operation in (
            (subprocess, "Popen", "blocked_process_operations", "start a subprocess"),
            (subprocess, "run", "blocked_process_operations", "start a subprocess"),
            (subprocess, "call", "blocked_process_operations", "start a subprocess"),
            (subprocess, "check_call", "blocked_process_operations", "start a subprocess"),
            (subprocess, "check_output", "blocked_process_operations", "start a subprocess"),
            (os, "system", "blocked_process_operations", "start a system process"),
            (os, "fork", "blocked_process_operations", "fork an interpreter"),
            (os, "posix_spawn", "blocked_process_operations", "spawn a process"),
            (os, "posix_spawnp", "blocked_process_operations", "spawn a process"),
            (os, "pipe", "blocked_process_operations", "open a case-observation pipe"),
            (threading.Thread, "start", "blocked_thread_operations", "start a real thread"),
            (threading.Barrier, "wait", "blocked_thread_operations", "wait at a thread barrier"),
            (time, "time", "blocked_clock_operations", "sample a wall clock"),
            (time, "time_ns", "blocked_clock_operations", "sample a wall clock"),
            (time, "monotonic", "blocked_clock_operations", "sample a monotonic clock"),
            (time, "monotonic_ns", "blocked_clock_operations", "sample a monotonic clock"),
            (time, "perf_counter", "blocked_clock_operations", "measure performance"),
            (time, "perf_counter_ns", "blocked_clock_operations", "measure performance"),
            (time, "process_time", "blocked_clock_operations", "measure CPU time"),
            (time, "process_time_ns", "blocked_clock_operations", "measure CPU time"),
            (time, "thread_time", "blocked_clock_operations", "measure thread time"),
            (time, "thread_time_ns", "blocked_clock_operations", "measure thread time"),
            (time, "sleep", "blocked_clock_operations", "wait on a clock"),
            (socket, "socket", "blocked_network_operations", "open a network socket"),
            (socket, "create_connection", "blocked_network_operations", "open a network connection"),
            (tempfile, "mkdtemp", "blocked_temporary_operations", "create a temporary directory"),
            (tempfile, "mkstemp", "blocked_temporary_operations", "create a temporary file"),
            (os, "replace", "blocked_file_operations", "activate or replace a file"),
            (os, "rename", "blocked_file_operations", "rename or promote a file"),
            (os, "unlink", "blocked_file_operations", "delete a file"),
            (os, "remove", "blocked_file_operations", "delete a file"),
            (os, "mkdir", "blocked_file_operations", "create a directory"),
            (os, "makedirs", "blocked_file_operations", "create a directory"),
            (os, "rmdir", "blocked_file_operations", "remove a directory"),
            (os, "write", "blocked_file_operations", "write a file descriptor"),
        ):
            self.replace(owner, name, self.blocked(counter, operation))
        if self.source_only:
            self.replace(os, "open", self.blocked(
                "blocked_file_operations", "read or open a filesystem owner"))
            self.replace(builtins, "open", self.blocked(
                "blocked_file_operations", "read or write a file"))
            self.replace(io, "open", self.blocked(
                "blocked_file_operations", "read or write a file"))
            for name in ("open", "read_bytes", "read_text", "write_bytes",
                         "write_text", "touch", "mkdir", "unlink", "rename",
                         "replace"):
                self.replace(Path, name, self.blocked(
                    "blocked_file_operations", "access a filesystem path",
                ))
            self.replace(importlib, "import_module", self.blocked(
                "blocked_import_operations", "import a candidate or source module"))
            self.replace(builtins, "__import__", self.blocked(
                "blocked_import_operations", "import a Python or native module",
            ))
            for name in ("create_module", "exec_module"):
                self.replace(importlib.machinery.ExtensionFileLoader, name,
                             self.blocked(
                                 "blocked_native_operations",
                                 "load a native extension",
                             ))
        else:
            previous = builtins.open

            def readonly_open(file: Any, mode: Any = "r", *args: Any,
                              **kwargs: Any) -> Any:
                require(type(mode) is str and not any(item in mode for item in "wax+"),
                        "a frozen context cannot open a file for writing")
                return previous(file, mode, *args, **kwargs)

            self.replace(builtins, "open", readonly_open)
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        for owner, name, value in reversed(self.installed):
            setattr(owner, name, value)
        added = set(sys.modules) - self.original_modules
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in added),
                "a source-only or read-only context imported an actual candidate")


def history_owner_map(worker: Any) -> dict[str, str]:
    require(getattr(worker, "SCHEMA", None)
            == "rebar-frozen-python-re-p0-candidate-worker-v5",
            "derive history only from the exact independently frozen V7 worker")
    result: dict[str, str] = {}

    def insert(relative: str, digest: str) -> None:
        require(relative not in result, "a historical evidence owner was duplicated")
        result[safe_relative(relative)] = checked_digest(digest, relative)

    for name in ("c", "rust"):
        records = worker.historical_v5_owners(name)
        require(type(records) is dict and len(records) == 17,
                "preserve all seventeen real candidate owners per family")
        for relative, digest in sorted(records.items()):
            insert(relative, digest)
    zig = worker.HISTORICAL_ZIG_OWNERS
    require(type(zig) is dict and len(zig) == 17,
            "preserve all seventeen real historical Zig candidate owners")
    for relative, digest in sorted(zig.items()):
        insert(relative, digest)
    builds = worker.HISTORICAL_V4_BUILD_OWNERS
    require(type(builds) is dict and set(builds) == {"cpp", "go", "fortran"},
            "preserve the three actual V4 source-build results")
    for value in builds.values():
        for field in ("archive", "receipt"):
            insert(value[field], value[field + "_sha256"])
    require(len(result) == 57,
            "the unchanged V7 historical graph has exactly 57 actual file owners")
    return result


def validate_v5_history_record(
    value: Mapping[str, Any], build: Any,
) -> dict[str, Any]:
    archive_raw, archive_owner = read_owned(
        value["archive_relative"], value["archive_sha256"],
        maximum=MAX_ARCHIVE_BYTES, exact_size=value["archive_bytes"],
    )
    receipt_raw, receipt_owner = read_owned(
        value["receipt_relative"], value["receipt_sha256"],
        maximum=MAX_SOURCE_BYTES, exact_size=value["receipt_bytes"],
    )
    plain = build.bounded_gzip(archive_raw, exact_size=value["uncompressed_bytes"])
    require(len(plain) == value["uncompressed_bytes"]
            and sha256(plain) == value["uncompressed_sha256"],
            "retain the complete original signed V5 " + value["family"] + " build")
    report = build.decode_json(plain, canonical_required=True)
    receipt = build.decode_json(receipt_raw, canonical_required=True)
    family = value["family"]
    expected_sources = {path: digest for path, digest, _ in OWNED_SOURCES[family]}
    require(report.get("schema") == "rebar-phase2-owned-native-source-build-v5"
            and report.get("version") == 5
            and report.get("status") == value["status"]
            and report.get("family") == family
            and report.get("label") == value["label"]
            and report.get("source_sha256") == V5_BUILD_SHA256
            and report.get("protocol_sha256") == V5_BUILD_PROTOCOL_SHA256
            and report.get("contract_sha256") == V5_BUILD_DOCUMENT_SHA256
            and report.get("owned_source_sha256") == expected_sources
            and report.get("actual_v5_compiler_process_count")
            == value["actual_process_count"]
            and report.get("expected_v5_compiler_process_count")
            == value["expected_process_count"],
            "authenticate the real V5 native source, family, result, and processes")
    processes = report.get("processes")
    phases = report.get("build_phases")
    require(type(processes) is list and len(processes) == value["actual_process_count"]
            and type(phases) is list
            and len(phases) == value["completed_phase_count"],
            "preserve every real compiler process and actual completed source phase")
    names = tuple(row.get("name") for row in processes if type(row) is dict)
    expected_names = value.get("expected_process_names")
    if expected_names is not None:
        require(names == tuple(expected_names),
                "preserve the exact ordered genuine V5 compiler history")
    identities: set[int] = set()
    for index, process in enumerate(processes):
        require(type(process) is dict
                and type(process.get("pid")) is int and process["pid"] > 0
                and process["pid"] not in identities
                and process.get("shell") is False
                and type(process.get("exit_status")) is int,
                "require genuine process identities unique within this actual run")
        identities.add(process["pid"])
        stdout = build.decode_process_stream(process, "stdout")
        stderr = build.decode_process_stream(process, "stderr")
        if process.get("name") == value.get("failed_process"):
            require(process["exit_status"] != 0
                    and type(value.get("required_diagnostic")) is str
                    and value["required_diagnostic"].encode("ascii") in stderr
                    and process.get("stderr_sha256")
                    == value.get("failed_stderr_sha256")
                    and len(stderr) == value.get("failed_stderr_bytes"),
                    "preserve the complete actual V5 failed compiler diagnostic")
        else:
            require(process["exit_status"] == 0,
                    "a successful historical compiler command was misclassified")
        require(type(stdout) is bytes and type(stderr) is bytes,
                "retain both exact actual compiler output streams")
    if family == "go":
        require(value["status"] == "FAIL" and value["failed_process"] == "build_go_bridge"
                and len(processes) == 5 and len(phases) == 0
                and processes[3].get("name") == "build_go_engine"
                and processes[3].get("exit_status") == 0
                and processes[4].get("name") == "build_go_bridge"
                and processes[4].get("exit_status") != 0
                and b"SSIZE_MAX" in build.decode_process_stream(processes[4], "stderr")
                and report.get("go_private_package_reproducibility") is None,
                "Go's engine compiled; its separate genuine bridge failed on SSIZE_MAX")
    if family == "fortran":
        require(value["status"] == "FAIL"
                and len(processes) == value["expected_process_count"] == 26
                and len(phases) == 2
                and [phase.get("name") for phase in phases]
                == ["reference-a", "reference-b"]
                and report.get("reproducibility") is None
                and type(report.get("error")) is dict
                and report["error"].get("type") == "BuildError"
                and "not genuinely byte-identical" in str(
                    report["error"].get("message", "")),
                "preserve both complete V5 Fortran builds and the real reproducibility failure")
        artifacts: set[tuple[int, int]] = set()
        source_identities: set[tuple[int, int]] = set()
        output_rows: list[dict[str, Any]] = []
        for phase in phases:
            source_rows = phase.get("fresh_source_owners")
            require(type(source_rows) is dict
                    and set(source_rows) == set(expected_sources),
                    "preserve all independently snapshotted Fortran source owners")
            for relative, expected in expected_sources.items():
                item = source_rows[relative]
                require(type(item) is dict and item.get("sha256") == expected
                        and type(item.get("device")) is int
                        and type(item.get("inode")) is int,
                        "reject a substituted V5 Fortran source phase")
                identity = (item["device"], item["inode"])
                require(identity not in source_identities,
                        "V5 Fortran phases must not share a source inode")
                source_identities.add(identity)
            outputs = phase.get("native_outputs")
            require(type(outputs) is dict and set(outputs) == {"engine", "bridge"},
                    "both complete V5 Fortran phases require both owned native outputs")
            for role in ("engine", "bridge"):
                output = outputs[role]
                require(type(output) is dict
                        and checked_digest(output.get("sha256"), role)
                        and type(output.get("size_bytes")) is int
                        and output["size_bytes"] > 0
                        and type(output.get("device")) is int
                        and type(output.get("inode")) is int,
                        "authenticate each real independently owned V5 Fortran binary")
                identity = (output["device"], output["inode"])
                require(identity not in artifacts,
                        "V5 Fortran phases must not share a native binary inode")
                artifacts.add(identity)
            output_rows.append(outputs)
        require(output_rows[0]["engine"]["size_bytes"]
                == output_rows[1]["engine"]["size_bytes"]
                == value["engine_bytes"]
                and output_rows[0]["engine"]["sha256"]
                == value["first_engine_sha256"]
                and output_rows[1]["engine"]["sha256"]
                == value["second_engine_sha256"]
                and value["first_engine_sha256"]
                != value["second_engine_sha256"]
                and output_rows[0]["bridge"]["sha256"]
                == output_rows[1]["bridge"]["sha256"]
                == value["identical_bridge_sha256"]
                and output_rows[0]["bridge"]["size_bytes"]
                == output_rows[1]["bridge"]["size_bytes"]
                == value["bridge_bytes"],
                "retain the actual equal-sized but genuinely nonidentical V5 Fortran engines")
    require(receipt.get("schema")
            == "rebar-phase2-owned-native-source-build-v5-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == value["status"]
            and receipt.get("family") == family
            and receipt.get("label") == value["label"]
            and receipt.get("archive_relative") == value["archive_relative"]
            and receipt.get("archive_sha256") == value["archive_sha256"]
            and receipt.get("archive_bytes") == value["archive_bytes"]
            and receipt.get("uncompressed_sha256") == value["uncompressed_sha256"]
            and receipt.get("uncompressed_bytes") == value["uncompressed_bytes"]
            and receipt.get("actual_v5_compiler_process_count")
            == value["actual_process_count"]
            and receipt.get("expected_v5_compiler_process_count")
            == value["expected_process_count"]
            and receipt.get("owned_source_sha256") == expected_sources,
            "a successful receipt publishes the real build status, not a candidate pass")
    archive_claim = receipt.get("archive_publication")
    require(type(archive_claim) is dict
            and archive_claim.get("sha256") == archive_owner["sha256"]
            and archive_claim.get("bytes") == archive_owner["size_bytes"]
            and archive_claim.get("device") == archive_owner["device"]
            and archive_claim.get("inode") == archive_owner["inode"]
            and archive_claim.get("exclusive_creation") is True
            and archive_claim.get("same_inode_readback_verified") is True
            and archive_claim.get("file_fsync_completed") is True,
            "authenticate the actual signed and durable V5 source-build owner")
    for document in (report, receipt):
        for field in ("candidate_processes_started", "candidate_imports",
                      "native_libraries_loaded", "hidden_cases_read",
                      "benchmark_files_read", "clock_samples", "timing_trials_run"):
            require(document.get(field) == 0,
                    "historical V5 source evidence must not execute a candidate: " + field)
        require(document.get("performance") == "NOT MEASURED"
                and document.get("candidate_correctness") == "NOT MEASURED"
                and document.get("holdout") == "NOT OPENED"
                and document.get("winner_selected") is False,
                "a genuine source build never establishes speed or compatibility")
    return {
        "family": family, "status": value["status"],
        "receipt_publication_status": "PASS",
        "actual_process_count": len(processes),
        "expected_process_count": value["expected_process_count"],
        "completed_phase_count": len(phases),
        "failure_preserved": value["status"] == "FAIL",
        "archive": archive_owner, "receipt": receipt_owner,
        "candidate_cases_executed": 0,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
    }


def read_frozen_owner_group(
    group: Mapping[str, tuple[str, str, int]], label: str,
) -> tuple[dict[str, bytes], dict[str, dict[str, Any]]]:
    require(type(group) is dict and bool(group),
            "require one exact independently pinned source-owner group: " + label)
    results: dict[str, bytes] = {}
    owners: dict[str, dict[str, Any]] = {}
    for name, item in sorted(group.items()):
        require(type(name) is str and type(item) is tuple and len(item) == 3
                and type(item[2]) is int and item[2] > 0,
                "require every complete first-party owner: " + label)
        raw, owner = read_owned(item[0], item[1],
                                maximum=MAX_SOURCE_BYTES,
                                exact_size=item[2])
        results[name] = raw
        owners[name] = owner
    require(len(results) == len(owners) == len(group),
            "never omit or duplicate an authenticated source owner: " + label)
    return results, owners


def authenticate_preserved_v21_history() -> dict[str, Any]:
    frozen, owners = read_frozen_owner_group(V21_OWNERS, "frozen V21 history")
    renderer = frozen_module(V21_OWNERS["source"][0],
                             V21_OWNERS["source"][1])
    require(getattr(renderer, "SCHEMA", None)
            == "rebar-candidate-current-overview-v21"
            and getattr(renderer, "SELF", None) == V21_OWNERS["source"][0]
            and getattr(renderer, "OUTER_ARCHIVE", None)
            == OUTER_CAMPAIGN_ARCHIVE
            and getattr(renderer, "OUTER_RECEIPT", None)
            == OUTER_CAMPAIGN_RECEIPT,
            "use only the exact frozen V21 103-owner historical verifier")
    manifest, snapshot, outputs = renderer.build(
        V21_OWNERS["source"][1],
        OUTER_CAMPAIGN_ARCHIVE[1],
        OUTER_CAMPAIGN_RECEIPT[1],
    )
    require(type(outputs) is tuple and len(outputs) == 3,
            "reproduce all three independently frozen V21 graph owners")
    output_map: dict[str, bytes] = {}
    for item in outputs:
        require(type(item) is tuple and len(item) == 2
                and type(item[0]) is str and type(item[1]) is bytes
                and item[0] not in output_map,
                "reject an omitted, reordered, or duplicated V21 graph owner")
        output_map[item[0]] = item[1]
    require(set(output_map)
            == {V21_OWNERS[name][0]
                for name in ("inputs", "summary", "svg")},
            "independently reproduce exactly the three published V21 outputs")
    for name in ("inputs", "summary", "svg"):
        path, expected, size = V21_OWNERS[name]
        require(output_map[path] == frozen[name]
                and len(output_map[path]) == size
                and sha256(output_map[path]) == expected,
                "reject changed already-published V21 history: " + name)
    renderer.validate_snapshot(snapshot)
    manifest_document = decode_document(
        frozen["inputs"], "exact frozen V21 input manifest",
        canonical_required=True,
    )
    summary_document = decode_document(
        frozen["summary"], "exact frozen V21 result summary",
        canonical_required=True,
    )
    require(type(manifest) is dict and manifest == manifest_document
            and type(summary_document) is dict
            and summary_document.get("snapshot") == snapshot
            and manifest.get("repository_evidence_owner_count")
            == PRESERVED_EVIDENCE_OWNER_COUNT
            and summary_document.get("repository_evidence_owner_count")
            == PRESERVED_EVIDENCE_OWNER_COUNT
            and manifest.get("all_digest_addressed_history_path_count")
            == PRESERVED_REFERENCE_PATH_COUNT
            and summary_document.get("authenticated_digest_addressed_history_paths")
            == PRESERVED_REFERENCE_PATH_COUNT
            and snapshot.get("all_actual_candidate_and_native_evidence_owner_count")
            == PRESERVED_EVIDENCE_OWNER_COUNT
            and snapshot.get("all_digest_addressed_history_path_count")
            == PRESERVED_REFERENCE_PATH_COUNT
            and snapshot.get("new_repaired_c_campaign_repository_evidence_owner_count")
            == PRESERVED_NEW_CAMPAIGN_OWNER_COUNT,
            "authenticate all actual 103 independent owners and 108 references")
    campaign = snapshot.get("c_v8_repaired_original_campaign")
    require(type(campaign) is dict
            and campaign.get("status") == "FAIL"
            and campaign.get("suite_count") == SUITE_COUNT
            and campaign.get("completed_suite_count") == SUITE_COUNT
            and campaign.get("full_case_denominator") == CASE_DENOMINATOR
            and campaign.get("infrastructure_failure_count") == SUITE_COUNT
            and campaign.get("verified_passing_case_count") == 0
            and campaign.get("observed_matching_case_count") == 0
            and campaign.get("semantic_mismatch_count") == "NOT MEASURED"
            and campaign.get("qualified") is False
            and campaign.get("new_repository_evidence_owner_count")
            == PRESERVED_NEW_CAMPAIGN_OWNER_COUNT
            and campaign.get("failure_causes")
            == historical_protocol()["actual_repaired_c_failure_causes"]
            and campaign.get("original_canonical_native_restored") is True
            and campaign.get("restoration_status") == "PASS"
            and campaign.get("holdout") == "NOT OPENED"
            and campaign.get("performance") == "NOT MEASURED"
            and campaign.get("memory") == "NOT MEASURED"
            and campaign.get("winner_selected") is False,
            "preserve all 30 actual owners and every original 12+1 C failure")
    native = campaign.get("original_canonical_native")
    require(type(native) is dict
            and native.get("path") == RESTORED_C_NATIVE_RELATIVE
            and native.get("sha256") == RESTORED_C_NATIVE_SHA256
            and native.get("bytes") == RESTORED_C_NATIVE_BYTES
            and native.get("device") == 2064
            and native.get("inode") == 430300
            and native.get("mode") == 0o755
            and native.get("nlink") == 1
            and native.get("present") is True
            and native.get("is_repaired_v8_native") is False,
            "preserve the exact restored original C device, inode, and mode")
    return {
        "source": owners["source"],
        "inputs": owners["inputs"],
        "summary": owners["summary"],
        "svg": owners["svg"],
        "actual_evidence_owner_count": PRESERVED_EVIDENCE_OWNER_COUNT,
        "authenticated_reference_path_count": PRESERVED_REFERENCE_PATH_COUNT,
        "new_repaired_c_campaign_owner_count": (
            PRESERVED_NEW_CAMPAIGN_OWNER_COUNT
        ),
        "repaired_c_infrastructure_failure_count": SUITE_COUNT,
        "repaired_c_failure_causes": dict(campaign["failure_causes"]),
        "repaired_c_original_native_restored": True,
        "repaired_c_verified_passing_case_count": 0,
        "repaired_c_matching": "NOT MEASURED",
    }


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    verify_runtime()
    with EffectBoundary(source_only=False) as boundary:
        source_raw, source_owner = read_owned(
            SOURCE_RELATIVE, options.source_sha256, maximum=MAX_SOURCE_BYTES,
        )
        protocol_raw, protocol_owner = read_owned(
            PROTOCOL_RELATIVE, options.protocol_sha256,
            maximum=MAX_SOURCE_BYTES,
        )
        document_raw, document_owner = read_owned(
            DOCUMENT_RELATIVE, options.document_sha256,
            maximum=MAX_SOURCE_BYTES,
        )
        require(bool(source_raw) and bool(protocol_raw),
                "authenticate all three genuine frozen V3 producer owners")
        try:
            ast.parse(source_raw.decode("utf-8", "strict"),
                      filename=str(ROOT / SOURCE_RELATIVE))
        except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
            raise ProducerError("the exact independent V3 source is invalid") from error
        document = validate_protocol_document(decode_document(
            document_raw, "the exact canonical V3 six-family source contract",
            canonical_required=True,
        ))
        _, goal_owner = read_owned("GOAL.md", GOAL_SHA256,
                                   maximum=MAX_SOURCE_BYTES)
        phase_raw, phase_owner = read_owned(
            PHASE1_RELATIVE, PHASE1_SHA256, maximum=MAX_SOURCE_BYTES,
        )
        phase = decode_document(phase_raw, "unchanged original phase-one matrix",
                                canonical_required=True)
        v1_raw, v1_owners = read_frozen_owner_group(
            ORIGINAL_V1_OWNERS, "immutable original V1 producer",
        )
        original_contract = decode_document(
            v1_raw["document"], "unchanged original V1 source contract",
            canonical_required=True,
        )
        require(original_contract.get("schema")
                == "rebar-owned-six-family-original-p0-producer-v1-source-freeze"
                and original_contract.get("version") == 1
                and original_contract.get("suites")
                == [suite_protocol(suite) for suite in SUITES]
                and original_contract.get("families")
                == [owner_protocol(family_spec(name))
                    for name in ("rust", "c", "zig", "cpp", "go", "fortran")]
                and original_contract.get("successful_nested_lifecycle")
                == document["successful_nested_lifecycle"],
                "preserve the entire exact source-frozen V1 evaluation contract")
        try:
            ast.parse(v1_raw["source"].decode("utf-8", "strict"),
                      filename=str(ROOT / ORIGINAL_V1_OWNERS["source"][0]))
        except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
            raise ProducerError("the immutable original V1 source changed") from error
        require(type(phase.get("suites")) is list
                and len(phase["suites"]) == SUITE_COUNT,
                "authenticate all thirteen unchanged phase-one suites")
        for expected, observed in zip(SUITES, phase["suites"], strict=True):
            require(type(observed) is dict
                    and observed.get("id") == expected.name
                    and observed.get("case_execution_count") == expected.case_count
                    and observed.get("matrix_sha256") == expected.matrix_sha256
                    and observed.get("baseline_records_sha256")
                    == expected.reference_sha256
                    and type(observed.get("source")) is dict
                    and observed["source"].get("path")
                    == expected.source_relative
                    and observed["source"].get("sha256")
                    == expected.source_sha256,
                    "reject an omitted or changed original suite: " + expected.name)
            if expected.seed is not None:
                require(observed.get("published_seed_decimal")
                        in {None, str(expected.seed)},
                        "preserve the full published original seed: " + expected.name)
            suite_raw, _ = read_owned(
                expected.source_relative, expected.source_sha256,
                maximum=MAX_SOURCE_BYTES,
            )
            try:
                ast.parse(suite_raw.decode("utf-8", "strict"),
                          filename=str(ROOT / expected.source_relative))
            except (UnicodeError, SyntaxError, ValueError,
                    RecursionError) as error:
                raise ProducerError(
                    "an unchanged original suite is invalid: " + expected.name
                ) from error
        source_identities: set[str] = set()
        for spec in FAMILIES.values():
            family_spec(spec.name)
            profile = BRIDGE_METHOD_PROFILES.get(spec.name)
            require(type(profile) is tuple and bool(profile)
                    and len(set(profile)) == len(profile),
                    "freeze an exact source-backed native bridge profile")
            for relative, expected, size in spec.source_owners:
                require(relative not in source_identities,
                        "never borrow a semantic source from another family")
                source_identities.add(relative)
                read_owned(relative, expected, maximum=MAX_SOURCE_BYTES,
                           exact_size=size)
        require(len(source_identities) == 25,
                "preserve exactly 25 independent first-party semantic sources")
        _, build_owners = read_frozen_owner_group(
            V8_BUILD_OWNERS, "independently frozen V8 C source build",
        )
        _, activation_owners = read_frozen_owner_group(
            V5_ACTIVATION_OWNERS,
            "independently frozen reversible V5 native activation",
        )
        v21_history = authenticate_preserved_v21_history()
        public_suite = suite_spec("public_types_v1")
        first, second, public_reference = (
            authenticate_original_public_type_baseline(public_suite)
        )
        require(len(first) == len(second) == 6912 and first == second
                and public_reference["baseline_reference_pids"]
                == list(PUBLIC_REFERENCE_PIDS)
                and public_reference["new_reference_workers_started"] == 0,
                "preserve both genuine independently signed public references")
        nested = document["successful_nested_lifecycle"]
        require(validate_successful_nested_lifecycle(copy.deepcopy(nested))
                == nested
                and SOURCE_RELATIVE
                == "tools/run_owned_six_family_original_p0_producer_v3.py",
                "authenticate the complete genuine V3-owned nested lifecycle")
        actual = dict(boundary.counts)
    for name in ("actual_candidate_workers", "actual_candidate_imports",
                 "actual_reference_workers", "actual_source_builds",
                 "actual_native_activations", "actual_native_promotions",
                 "actual_interpreters_created", "actual_threads_started",
                 "actual_subprocesses_started", "actual_native_libraries_loaded",
                 "actual_network_requests", "actual_file_writes",
                 "hidden_cases_read", "benchmark_files_read", "clock_samples",
                 "timing_trials_run"):
        require(actual.get(name) == 0,
                "read-only V3 verification attempted an effect: " + name)
    return {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS",
        "read_only": True,
        "source": source_owner,
        "protocol": protocol_owner,
        "document": document_owner,
        "goal": goal_owner,
        "phase_one": phase_owner,
        "original_v1_owners": v1_owners,
        "v8_source_build_owners": build_owners,
        "v5_activation_owners": activation_owners,
        "v21_history": v21_history,
        "public_type_reference": public_reference,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": 6,
        "source_owner_count": 25,
        "pairwise_shared_semantic_source_count": 0,
        "historically_runnable_p0_family_count": 3,
        "candidate_qualified_count": 0,
        "fully_qualified_candidate_count": 0,
        "total_distinct_historical_evidence_owner_count": (
            PRESERVED_EVIDENCE_OWNER_COUNT
        ),
        "total_authenticated_historical_reference_path_count": (
            PRESERVED_REFERENCE_PATH_COUNT
        ),
        "new_repaired_c_campaign_evidence_owner_count": (
            PRESERVED_NEW_CAMPAIGN_OWNER_COUNT
        ),
        "successful_nested_lifecycle": nested,
        "historical_failed_zig_lifecycle": document["historical_evidence"][
            "failed_zig_is_not_a_success"
        ],
        "source_only_effects": actual,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "actual_native_promotions": 0,
        "actual_interpreters_created": 0,
        "actual_threads_started": 0,
        "actual_subprocesses_started": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def parse_source_owners(spec: FamilySpec, entries: Sequence[str]) -> dict[str, str]:
    require(type(entries) in (list, tuple),
            "provide every actual first-party candidate source pin")
    expected = {path: digest for path, digest, _ in spec.source_owners}
    result: dict[str, str] = {}
    for entry in entries:
        require(type(entry) is str and entry.count("=") == 1,
                "pin each native family source as exact relative=sha256")
        relative, digest = entry.split("=", 1)
        require(relative in expected and relative not in result
                and checked_digest(digest, relative) == expected[relative],
                "reject repeated, borrowed, omitted, or changed native family sources")
        result[relative] = digest
    require(result == expected,
            "bind matching to the selected engine's complete independent source closure")
    return result


def native_pins(spec: FamilySpec, options: argparse.Namespace) -> dict[str, str]:
    result = {
        "source": checked_digest(options.candidate_source_sha256,
                                 "selected candidate adapter"),
        "native_engine": checked_digest(options.native_engine_sha256,
                                        "selected native engine"),
        "native_bridge": checked_digest(options.native_bridge_sha256,
                                        "selected Python bridge"),
    }
    require((result["native_engine"] == result["native_bridge"])
            is spec.combined_native,
            "only the genuinely combined C and C++ engines may share their bridge")
    sources = parse_source_owners(spec, options.owned_source_sha256)
    require(sources[spec.adapter_relative] == result["source"],
            "bind the selected adapter to its own complete semantic source closure")
    return result


def exact_native_owners(
    spec: FamilySpec, pins: Mapping[str, str], source_pins: Mapping[str, str],
) -> dict[str, dict[str, Any]]:
    require(type(pins) is dict and set(pins)
            == {"source", "native_engine", "native_bridge"}
            and (pins["native_engine"] == pins["native_bridge"])
            is spec.combined_native,
            "reject crossed, substituted, or falsely combined native engine owners")
    expected = {path: digest for path, digest, _ in spec.source_owners}
    require(dict(source_pins) == expected,
            "verify all selected independently owned semantic sources")
    for relative, digest, size in spec.source_owners:
        read_owned(relative, digest, maximum=MAX_SOURCE_BYTES, exact_size=size)
    _, source = read_owned(spec.adapter_relative, pins["source"],
                           maximum=MAX_SOURCE_BYTES)
    _, engine = read_owned(spec.engine_relative, pins["native_engine"],
                           maximum=MAX_BINARY_BYTES)
    if spec.combined_native:
        bridge = dict(engine)
    else:
        _, bridge = read_owned(spec.bridge_relative, pins["native_bridge"],
                               maximum=MAX_BINARY_BYTES)

    def original_owner(item: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "relative": item["relative"],
            "sha256": item["sha256"],
            "bytes": item["size_bytes"],
            "device": item["device"],
            "inode": item["inode"],
        }

    result = {"source": original_owner(source),
              "native_engine": original_owner(engine),
              "native_bridge": original_owner(bridge)}
    require((result["native_engine"] == result["native_bridge"])
            is spec.combined_native,
            "verify the real alias policy for C, C++, and split-language native engines")
    return result


def validate_native_bridge_profile(
    bridge: types.ModuleType, profile: tuple[str, ...],
) -> types.ModuleType:
    require(type(bridge) is types.ModuleType
            and type(profile) is tuple
            and bool(profile)
            and len(profile) == len(set(profile))
            and all(type(name) is str and bool(name) for name in profile),
            "require one complete, distinct, source-backed native bridge profile")
    for name in profile:
        value = getattr(bridge, name, None)
        require(type(value) is types.BuiltinFunctionType
                and getattr(value, "__self__", None) is bridge
                and getattr(value, "__name__", None) == name,
                "require the exact extension-owned native built-in: "
                + bridge.__name__ + "." + name)
    return bridge


def validate_public_type_ownership(
    spec: FamilySpec, module: types.ModuleType, bridge: types.ModuleType,
) -> tuple[type, type]:
    require(type(module) is types.ModuleType
            and module.__name__ == spec.module
            and type(bridge) is types.ModuleType
            and bridge.__name__ == spec.bridge_module,
            "bind public types to the exact source-owned adapter and bridge")
    pattern = getattr(module, "Pattern", None)
    match = getattr(module, "Match", None)
    require(isinstance(pattern, type) and isinstance(match, type)
            and pattern is not match
            and vars(module).get("Pattern") is pattern
            and vars(module).get("Match") is match,
            "require both distinct actual independently owned public regex types")
    if spec.name in {"c", "rust", "zig"}:
        require(getattr(pattern, "__module__", None) == "re"
                and getattr(match, "__module__", None) == "re"
                and getattr(bridge, "Match", None) is match,
                "require Python-compatible public names and the exact native Match owner")
        if spec.name == "c":
            require(getattr(bridge, "Pattern", None) is pattern.__base__
                    and pattern.__base__ is not object,
                    "require a direct public C Pattern base from the exact C bridge")
    else:
        require(getattr(pattern, "__module__", None) == spec.module
                and getattr(match, "__module__", None) == spec.module,
                "retain the exact adapter-owned C++, Go, or Fortran public types")
        if spec.name == "go":
            require(type(vars(pattern).get("_create")) is classmethod
                    and type(vars(match).get("_create")) is classmethod
                    and "__new__" in vars(pattern)
                    and "__new__" in vars(match)
                    and "__init__" not in vars(pattern)
                    and "__init__" not in vars(match),
                    "preserve genuinely owned Go __new__ and _create constructors")
        else:
            require(type(vars(pattern).get("__init__")) is types.FunctionType
                    and type(vars(match).get("__init__")) is types.FunctionType
                    and vars(pattern)["__init__"].__module__ == spec.module
                    and vars(match)["__init__"].__module__ == spec.module,
                    "preserve genuine adapter-owned C++ or Fortran constructors")
    return pattern, match


def authenticate_candidate_module(
    spec: FamilySpec, pins: Mapping[str, str], source_pins: Mapping[str, str],
) -> tuple[types.ModuleType, dict[str, dict[str, Any]]]:
    provenance = exact_native_owners(spec, pins, source_pins)
    if spec.name in {"c", "rust", "zig"}:
        original = frozen_module(ORIGINAL_V5_RELATIVE, ORIGINAL_V5_SHA256)
        native_spec = make_original_family_spec(original, spec)
        module, authenticated = original.authenticate_family_candidate(
            native_spec, dict(pins),
        )
        require(type(authenticated) is dict and authenticated == provenance
                and original.validate_owners(authenticated, native_spec, pins),
                "require exact agreement with the original upstream native owners")
    else:
        module = importlib.import_module(spec.module)
    require(type(module) is types.ModuleType
            and module.__name__ == spec.module
            and os.path.abspath(str(getattr(module, "__file__", "")))
            == str(ROOT / spec.adapter_relative)
            and os.path.realpath(str(module.__file__))
            == str(ROOT / spec.adapter_relative)
            and module.__spec__ is not None
            and module.__spec__.name == spec.module
            and module.__spec__.origin == str(ROOT / spec.adapter_relative)
            and isinstance(module.__spec__.loader,
                           importlib.machinery.SourceFileLoader),
            "load only the exact selected source-owned public Python adapter")
    bridge = sys.modules.get(spec.bridge_module)
    expected_bridge = str(ROOT / spec.bridge_relative)
    require(type(bridge) is types.ModuleType
            and bridge.__name__ == spec.bridge_module
            and os.path.abspath(str(getattr(bridge, "__file__", "")))
            == expected_bridge
            and os.path.realpath(str(bridge.__file__)) == expected_bridge
            and bridge.__spec__ is not None
            and bridge.__spec__.name == spec.bridge_module
            and bridge.__spec__.origin == expected_bridge
            and isinstance(bridge.__spec__.loader,
                           importlib.machinery.ExtensionFileLoader),
            "load only the exact selected owned native extension")
    require(getattr(bridge.__spec__.loader, "name", None) == spec.bridge_module
            and getattr(bridge.__spec__.loader, "path", None) == expected_bridge,
            "bind the independently owned extension to its exact native loader")
    pattern, _ = validate_public_type_ownership(spec, module, bridge)
    for name in ("search", "match", "fullmatch", "findall", "finditer",
                 "split", "sub", "subn", "scanner"):
        require(callable(getattr(pattern, name, None)),
                "an independently owned Pattern operation is missing: " + name)
    for name in ("compile", "search", "match", "fullmatch", "findall",
                 "finditer", "split", "sub", "subn", "escape", "Scanner"):
        require(callable(getattr(module, name, None)),
                "an independently owned public regex operation is missing: " + name)
    profile = BRIDGE_METHOD_PROFILES.get(spec.name)
    require(type(profile) is tuple,
            "require the selected independently source-backed language profile")
    validate_native_bridge_profile(bridge, profile)
    exact_native_owners(spec, pins, source_pins)
    return module, provenance


def make_original_family_spec(original: Any, spec: FamilySpec) -> Any:
    return original.FamilySpec(
        spec.name, spec.module, spec.adapter_relative, spec.engine_relative,
        spec.bridge_module, spec.bridge_relative, spec.owned_ctypes,
    )


def validate_guard_identity(
    original: Any, spec: FamilySpec, native_spec: Any,
    module: types.ModuleType, provenance: Mapping[str, Any],
    pins: Mapping[str, str], baseline_ownership: Mapping[str, Any],
    isolation: Mapping[str, Any], blocker: Any,
) -> None:
    require(sys.meta_path and sys.meta_path[0] is blocker
            and isinstance(blocker, original.FamilyImportBlocker)
            and blocker.spec is native_spec,
            "retain the continuously installed selected-family import quarantine")
    require(sys.modules.get(spec.module) is module
            and type(sys.modules.get(spec.bridge_module)) is types.ModuleType
            and module.Pattern is not baseline_ownership["pattern_type"]
            and module.Match is not baseline_ownership["match_type"],
            "reject original CPython matcher ownership or a replaced candidate")
    for name in tuple(sys.modules):
        require(not original.forbidden_family_module(name, native_spec),
                "reject an external or sibling regex engine: " + name)
    require(type(provenance) is dict
            and set(provenance) == {"source", "native_engine", "native_bridge"}
            and provenance["source"].get("sha256") == pins["source"]
            and provenance["native_engine"].get("sha256")
            == pins["native_engine"]
            and provenance["native_bridge"].get("sha256")
            == pins["native_bridge"]
            and (provenance["native_engine"] == provenance["native_bridge"])
            is spec.combined_native,
            "retain the genuine per-language source and native owners")
    require(isolation.get("rejected_cross_family_or_external_imports") == 0
            and isolation.get("rejected_foreign_dynamic_loads") == 0
            and isolation.get("rejected_process_delegations") == 0,
            "reject original matching, external packages, native substitution, or delegation")


@contextlib.contextmanager
def chosen_six_family_guard(
    original: Any, identity: Any, warning: Any, baseline: Any,
    spec: FamilySpec, pins: Mapping[str, str], source_pins: Mapping[str, str],
) -> Iterator[dict[str, Any]]:
    native_spec = make_original_family_spec(original, spec)
    trusted = original.preload_trusted_stdlib_ctypes(native_spec, warning)
    ownership = identity.capture_original_identities(baseline)
    with original.isolated_family_imports(native_spec) as isolation:
        blocker = sys.meta_path[0]

        def candidate_loader() -> tuple[types.ModuleType, dict[str, Any]]:
            return authenticate_candidate_module(spec, pins, source_pins)

        with identity.original_regex_guard(
            baseline, dict(pins), candidate_loader=candidate_loader,
        ) as active:
            module = active.get("candidate")
            provenance = active.get("native_provenance")
            require(type(module) is types.ModuleType
                    and type(provenance) is dict,
                    "a real owned native candidate did not enter the continuous guard")
            bridge = sys.modules.get(spec.bridge_module)
            require(type(bridge) is types.ModuleType,
                    "authenticate the selected native bridge under quarantine")
            native_classes = original.owned_class_identities((module, bridge), native_spec)
            visited: set[int] = set()
            for owned in (module, bridge):
                original.forbid_owned_original_matchers(
                    owned, ownership, native_spec, identity, native_classes,
                    spec.name + " independently owned matcher",
                    visited=visited,
                )
            validate_guard_identity(original, spec, native_spec, module,
                                    provenance, pins, ownership, isolation, blocker)
            previous_verify = active["verify"]

            def verify() -> None:
                previous_verify()
                validate_guard_identity(original, spec, native_spec, module,
                                        provenance, pins, ownership,
                                        isolation, blocker)

            active["verify"] = verify
            active["cross_family_imports_blocked"] = True
            active["external_regex_imports_blocked"] = True
            active["owned_native_ffi_allowed"] = spec.owned_ctypes
            active["trusted_stdlib_ctypes_preloaded"] = spec.owned_ctypes
            active["trusted_stdlib_ctypes_builtin_verified"] = spec.owned_ctypes
            active["trusted_stdlib_ctypes_pythonapi_initialized"] = spec.owned_ctypes
            active["trusted_stdlib_ctypes_source_sha256"] = (
                original.PINNED_STDLIB_CTYPES_SHA256 if spec.owned_ctypes else None
            )
            active["owned_ctypes_load_count"] = len(
                isolation["owned_ctypes_load_paths"])
            active["owned_ctypes_symbol_count"] = len(
                isolation["owned_ctypes_symbol_names"])
            require((trusted is not None) is spec.owned_ctypes,
                    "authenticate exactly the selected Zig-only first-party FFI preload")
            try:
                yield active
            finally:
                verify()


def v7_actual_worker_options(
    options: argparse.Namespace, spec: FamilySpec, worker: Any,
) -> argparse.Namespace:
    args = [
        "--run", "--source-sha256", V7_WORKER_SHA256,
        "--protocol-sha256", V7_PROTOCOL_SHA256,
        "--document-sha256", V7_DOCUMENT_SHA256,
        "--candidate", spec.name,
        "--label", checked_label(options.label),
        "--build-version", options.build_version,
        "--build-label", checked_label(options.build_label, "build label"),
        "--activation-root", options.activation_root,
    ]
    for name in ("build-source", "build-protocol", "build-archive",
                 "build-receipt", "activation-source", "activation-protocol",
                 "activation-report", "activation-receipt", "candidate-source",
                 "native-engine", "native-bridge"):
        value = getattr(options, name.replace("-", "_") + "_sha256")
        args.extend(("--" + name + "-sha256",
                     checked_digest(value, name)))
    for name in ("build-contract", "activation-contract", "recovery-journal"):
        value = getattr(options, name.replace("-", "_") + "_sha256")
        if value is not None:
            args.extend(("--" + name + "-sha256",
                         checked_digest(value, name)))
    for value in options.owned_source_sha256:
        args.extend(("--owned-source-sha256", value))
    return worker.parse_arguments(args)


def authenticate_actual_activation(
    options: argparse.Namespace, spec: FamilySpec,
) -> tuple[dict[str, Any], dict[str, Any]]:
    pins = native_pins(spec, options)
    source_pins = parse_source_owners(spec, options.owned_source_sha256)
    require(options.build_version in {"2", "3", "4"},
            "a V5 source build has no committed V5-aware activation; fail closed")
    worker = frozen_module(V7_WORKER_RELATIVE, V7_WORKER_SHA256)
    selected = v7_actual_worker_options(options, spec, worker)
    context = worker.authenticate_frozen_context(selected)
    if options.activation_source_sha256 == V2_ACTIVATION_SHA256:
        require(spec.name in {"rust", "c", "zig"}
                and options.activation_protocol_sha256
                == V2_ACTIVATION_PROTOCOL_SHA256
                and options.activation_contract_sha256 is None
                and options.build_contract_sha256 is None
                and options.build_version
                == {"rust": "2", "c": "2", "zig": "3"}[spec.name],
                "authorize only a genuine version-correct original V2 activation")
        approval = context["v6_worker"].authenticate_canonical_activation(
            context["v6_options"], context,
        )
    else:
        require(options.activation_source_sha256 == V3_ACTIVATION_SHA256
                and options.activation_protocol_sha256
                == V3_ACTIVATION_PROTOCOL_SHA256
                and options.activation_contract_sha256
                == V3_ACTIVATION_DOCUMENT_SHA256
                and options.build_version == "4",
                "require the exact genuine V3 activation and a passing V4 build")
        approval = worker.authenticate_canonical_activation_v3(selected, context)
    require(type(approval) is dict and approval.get("family") == spec.name,
            "the genuine reversible activation belongs to another candidate")
    approved_sources = approval.get("pins")
    if type(approved_sources) is dict and set(approved_sources) == set(source_pins):
        require(approved_sources == source_pins,
                "bind V3 activation to every exact selected native source")
    elif type(approved_sources) is dict:
        require(approved_sources == pins,
                "bind the genuine original V2 activation to its actual native pins")
    else:
        raise ProducerError("the reversible activation omitted actual native ownership")
    exact_native_owners(spec, pins, source_pins)
    return approval, context


def legacy_family_spec(gate: Any, spec: FamilySpec) -> Any:
    return gate.FamilySpec(
        spec.name,
        "c_vm" if spec.name == "c" else spec.name,
        spec.module, spec.adapter_relative, spec.bridge_module,
        spec.engine_relative, spec.bridge_relative,
        tuple(relative for relative, _, _ in spec.source_owners),
    )


def validate_direct_records(
    suite: SuiteSpec, source: Any,
    records: list[dict[str, Any]], baseline: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    require(type(records) is list and type(baseline) is list
            and len(records) == len(baseline) == suite.case_count,
            "never omit or fabricate an actual original case: " + suite.name)
    producer_digest = getattr(source, "digest", None)
    require(callable(producer_digest)
            and producer_digest(baseline) == suite.reference_sha256,
            "compare only to the exact original suite-specific reference codec")
    gate = frozen_module(ORIGINAL_GATE_RELATIVE, ORIGINAL_GATE_SHA256)
    seen: set[str] = set()
    differences: list[dict[str, Any]] = []
    for expected, actual in zip(baseline, records, strict=True):
        identity = gate.case_identity(expected)
        require(identity not in seen and gate.case_identity(actual) == identity,
                "an actual original candidate case was reordered or duplicated")
        seen.add(identity)
        if expected != actual:
            differences.append({
                "case": identity,
                "expected_record": expected,
                "actual_record": actual,
            })
    return differences


def authenticate_original_public_type_baseline(
    suite: SuiteSpec,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    require(suite.name == "public_types_v1"
            and suite.case_count == 6912
            and suite.source_sha256
            == "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20"
            and suite.matrix_sha256
            == "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123"
            and suite.reference_sha256
            == "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21",
            "authenticate only the unchanged original 6,912 public-type cases")
    recorder = frozen_module(PUBLIC_RECORDER_RELATIVE, PUBLIC_RECORDER_SHA256)
    require(getattr(recorder, "SOURCE_RELATIVE", None)
            == PUBLIC_RECORDER_RELATIVE
            and getattr(recorder, "ORACLE_RELATIVE", None)
            == suite.source_relative
            and getattr(recorder, "ORACLE_SHA256", None)
            == suite.source_sha256
            and getattr(recorder, "MATRIX_SHA256", None)
            == suite.matrix_sha256
            and getattr(recorder, "CASE_COUNT", None) == suite.case_count,
            "use only the source-pinned original public reference recorder")
    oracle = frozen_module(suite.source_relative, suite.source_sha256)
    original = frozen_module(ORIGINAL_V5_RELATIVE, ORIGINAL_V5_SHA256)
    source_owners: dict[str, dict[str, Any]] = {}
    for role, relative, expected in (
        ("recorder", PUBLIC_RECORDER_RELATIVE, PUBLIC_RECORDER_SHA256),
        ("parent_recorder", recorder.PARENT_RECORDER_RELATIVE,
         recorder.PARENT_RECORDER_SHA256),
        ("public_type_oracle", recorder.ORACLE_RELATIVE,
         recorder.ORACLE_SHA256),
        ("original_v5", recorder.V5_RELATIVE, recorder.V5_SHA256),
        ("from_scratch_audit_v3", recorder.AUDIT_RELATIVE,
         recorder.AUDIT_SHA256),
        ("previous_ownership_policy", recorder.PREVIOUS_POLICY_RELATIVE,
         recorder.PREVIOUS_POLICY_SHA256),
    ):
        owner, retained = recorder.read_owned_regular(
            relative, expected, recorder.MAX_SOURCE_BYTES,
        )
        require(retained is None,
                "never duplicate a complete signed baseline source owner")
        source_owners[role] = owner
    recorder.validate_frozen_source_owners(source_owners,
                                           PUBLIC_RECORDER_SHA256)
    matrix = oracle.build_matrix()
    require(getattr(original, "SOURCE_RELATIVE", None) == ORIGINAL_V5_RELATIVE
            and getattr(recorder, "ORACLE_MODULE", None) == oracle.__name__
            and getattr(oracle, "MATRIX_SHA256", None) == suite.matrix_sha256
            and getattr(oracle, "CASE_COUNT", None) == suite.case_count
            and recorder.validate_matrix(matrix, suite.matrix_sha256)
            == suite.matrix_sha256
            and oracle.validate_matrix(matrix, suite.matrix_sha256)
            == suite.matrix_sha256
            and len(matrix) == suite.case_count
            and type(source_owners) is dict,
            "retain the exact original public oracle, matrix, and source owners")
    baseline = recorder.make_baseline_pins(
        PUBLIC_BASELINE_LABEL,
        PUBLIC_BASELINE_RECEIPT_SHA256,
        PUBLIC_BASELINE_ARCHIVE_SHA256,
        suite.reference_sha256,
    )
    c_spec = family_spec("c")
    owner_pins = recorder.make_owner_pins(
        "c", PUBLIC_RECORDER_SHA256,
        OWNED_SOURCES["c"][0][1],
        RESTORED_C_NATIVE_SHA256, RESTORED_C_NATIVE_SHA256,
        [relative + "=" + sha
         for relative, sha, _ in c_spec.source_owners],
        baseline,
    )
    receipt, receipt_owner = recorder.authenticate_baseline_receipt(owner_pins)
    require(receipt_owner.get("relative") == PUBLIC_BASELINE_RECEIPT_RELATIVE
            and receipt_owner.get("sha256") == PUBLIC_BASELINE_RECEIPT_SHA256
            and receipt_owner.get("bytes") == PUBLIC_BASELINE_RECEIPT_BYTES
            and receipt.get("report_uncompressed_sha256")
            == PUBLIC_BASELINE_UNCOMPRESSED_SHA256
            and receipt.get("report_uncompressed_bytes")
            == PUBLIC_BASELINE_UNCOMPRESSED_BYTES
            and receipt.get("source_closure_before") == source_owners
            and receipt.get("source_closure_after") == source_owners
            and receipt.get("baseline_reference_pids")
            == list(PUBLIC_REFERENCE_PIDS),
            "authenticate the exact existing independently signed baseline receipt")
    restored, archive_owner = recorder.stream_baseline_archive(
        owner_pins, oracle, matrix, receipt,
    )
    require(archive_owner.get("relative") == PUBLIC_BASELINE_ARCHIVE_RELATIVE
            and archive_owner.get("sha256") == PUBLIC_BASELINE_ARCHIVE_SHA256
            and archive_owner.get("bytes") == PUBLIC_BASELINE_ARCHIVE_BYTES
            and restored.get("baseline_records_sha256") == suite.reference_sha256
            and restored.get("baseline_reference_pids")
            == list(PUBLIC_REFERENCE_PIDS)
            and restored.get("actual_reference_workers") == 2
            and restored.get("actual_candidate_workers") == 0
            and restored.get("actual_candidate_imports") == 0
            and restored.get("hidden_cases_read") == 0
            and restored.get("benchmark_files_read") == 0
            and restored.get("clock_samples") == 0
            and restored.get("performance") == "NOT MEASURED",
            "preserve both genuine saved Python references without rerunning them")
    first = restored.get("reference_a_records")
    second = restored.get("reference_b_records")
    result = restored.get("complete_baseline_result")
    processes = result.get("reference_processes") if type(result) is dict else None
    require(type(first) is list and type(second) is list
            and len(first) == len(second) == suite.case_count
            and first == second
            and oracle.digest(first) == oracle.digest(second)
            == suite.reference_sha256
            and type(processes) is list and len(processes) == 2,
            "retain both complete original 6,912-record reference vectors")
    for index, role in enumerate(("reference_a", "reference_b")):
        process = processes[index]
        expected_sha, expected_bytes = PUBLIC_REFERENCE_STDOUT[index]
        require(type(process) is dict
                and process.get("role") == role
                and process.get("pid") == PUBLIC_REFERENCE_PIDS[index]
                and type(process.get("stdout")) is dict
                and process["stdout"].get("sha256") == expected_sha
                and process["stdout"].get("bytes") == expected_bytes
                and process["stdout"].get("complete") is True,
                "retain the exact signed, complete, independently isolated "
                + role + " process")
    require(processes[0]["pid"] != processes[1]["pid"],
            "never replace two actual independent references with one process")
    return first, second, {
        "actual_independent_reference_count": 2,
        "reference_decoder": PUBLIC_RECORDER_RELATIVE,
        "reference_decoder_sha256": PUBLIC_RECORDER_SHA256,
        "reference_roles_separately_authenticated": True,
        "reference_records_sha256": suite.reference_sha256,
        "baseline_label": PUBLIC_BASELINE_LABEL,
        "baseline_archive": archive_owner,
        "baseline_receipt": receipt_owner,
        "baseline_reference_pids": list(PUBLIC_REFERENCE_PIDS),
        "reference_stdout": [
            {"role": role, "sha256": sha, "bytes": size}
            for role, (sha, size) in zip(
                ("reference_a", "reference_b"),
                PUBLIC_REFERENCE_STDOUT,
                strict=True,
            )
        ],
        "new_reference_workers_started": 0,
        "candidate_imports_by_reference_decoder": 0,
    }


def observe_direct_suite(
    suite: SuiteSpec, spec: FamilySpec, pins: dict[str, str],
    source_pins: dict[str, str], phase1: dict[str, Any],
) -> dict[str, Any]:
    gate = frozen_module(ORIGINAL_GATE_RELATIVE, ORIGINAL_GATE_SHA256)
    original = frozen_module(ORIGINAL_V5_RELATIVE, ORIGINAL_V5_SHA256)
    original_spec = gate.suite_spec(suite.name)
    source = gate.import_suite_source(original_spec)
    core = category = None
    support: dict[str, Any] | None = None
    if suite.name in {"public_v3", "scanner_v3", "buffer_v3"}:
        core, category = gate.source_module_for_core(original_spec)
        _, _, selected_source, matrix, _, _ = core.load_prerequisites(category)
        require(selected_source is source,
                "run the exact unchanged source-owned public case evaluator")
    else:
        matrix = gate.producer_matrix(source, original_spec)
        if suite.name == "public_types_v1":
            support = source.preload_support_modules()
            source.verify_support_modules(support)
    if suite.name == "public_types_v1":
        baseline, second, baseline_evidence = (
            authenticate_original_public_type_baseline(suite)
        )
    else:
        baseline, second, baseline_evidence = gate.archived_vectors(
            phase1, original_spec,
        )
    require(baseline == second and len(baseline) == suite.case_count,
            "authenticate both existing original reference roles without rerunning them")
    warning, identity, harness, _ = original.load_frozen_oracles()
    original_re = sys.modules.get("re")
    require(type(original_re) is types.ModuleType
            and original_re.__name__ == "re",
            "preload the pinned original identity before quarantining matching")
    family = legacy_family_spec(gate, spec)
    records: list[dict[str, Any]] = []
    resource_evidence: dict[str, Any] = {}
    active_case: str | None = None
    try:
        locale_context: Any = contextlib.nullcontext(None)
        if suite.name == "public_surface_v19":
            locale_context = harness.authentic_private_locales()
        with locale_context as actual_locales:
            with warning.installed_warning_safe_guard(identity):
                with chosen_six_family_guard(
                    original, identity, warning, original_re,
                    spec, pins, source_pins,
                ) as active:
                    candidate = active["candidate"]
                    if suite.name == "threaded_pattern_v1":
                        records, resource_evidence = gate.observe_threaded_suite(
                            source, candidate, matrix, active,
                        )
                    elif suite.name == "public_surface_v19":
                        records, resource_evidence = gate.observe_public_surface(
                            source, candidate, matrix, active,
                            {"iso8859_1": "en_US.iso88591", "utf8": "en_US.utf8"},
                        )
                        require(type(actual_locales) is dict
                                and actual_locales.get("actual_localedef_workers") == 2
                                and actual_locales.get("iso_8859_1_verified") is True
                                and actual_locales.get("utf_8_verified") is True,
                                "provision both genuinely differently encoded locales")
                        resource_evidence["actual_private_locale_provision"] = (
                            actual_locales
                        )
                    else:
                        for case in matrix:
                            active_case = gate.case_identity(case)
                            active["verify"]()
                            actual = gate.create_frozen_record(
                                original_spec, source, case, candidate,
                                core=core, category=category, support=support,
                            )
                            active["verify"]()
                            records.append(actual)
                            active_case = None
                    matcher_guard = gate.capture_guard(
                        active,
                        2 * len(source.COHORTS)
                        if suite.name == "threaded_pattern_v1"
                        else 2 * len(records),
                        family,
                    )
                    actual_provenance = active["native_provenance"]
                    active["verify"]()
    except BaseException as error:
        details = {
            "schema": SCHEMA + "-genuine-suite-failure",
            "status": "FAIL", "suite": suite.name,
            "candidate_family": spec.name,
            "active_case": active_case,
            "completed_candidate_cases": len(records),
            "completed_candidate_records": records,
            "error_type": type(error).__qualname__,
            "error_message": str(error),
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__),
            "actual_candidate_workers": 1,
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
        }
        extra = getattr(error, "details", None)
        if type(extra) is dict:
            details["complete_original_failure_details"] = extra
        raise ActualSuiteFailure(
            "preserve the complete genuine original case failure: " + suite.name,
            details,
        ) from error
    differences = validate_direct_records(suite, source, records, baseline)
    candidate_hash = source.digest(records)
    return {
        "schema": SCHEMA + "-actual-original-suite",
        "status": "PASS" if not differences else "FAIL",
        "suite": suite.name,
        "candidate_family": spec.name,
        "candidate_module": spec.module,
        "case_execution_denominator": suite.case_count,
        "actual_candidate_case_count": len(records),
        "source_relative": suite.source_relative,
        "source_sha256": suite.source_sha256,
        "matrix_sha256": suite.matrix_sha256,
        "reference_records_sha256": suite.reference_sha256,
        "candidate_records_sha256": candidate_hash,
        "baseline_evidence": baseline_evidence,
        "candidate_records": records,
        "mismatch_count": len(differences),
        "all_mismatches": differences,
        "matcher_guard": matcher_guard,
        "native_provenance": actual_provenance,
        "resource_evidence": resource_evidence,
        "actual_candidate_workers": 1,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_qualified": False,
        "winner_selected": False,
    }


def observe_original_upstream(
    suite: SuiteSpec, spec: FamilySpec, pins: dict[str, str],
    source_pins: dict[str, str],
) -> dict[str, Any]:
    original = frozen_module(ORIGINAL_V5_RELATIVE, ORIGINAL_V5_SHA256)
    warning, identity, harness, matrix = original.load_frozen_oracles()
    require(original.digest(matrix) == suite.matrix_sha256
            and len(matrix) == 165
            and len([row for row in matrix
                     if row.get("classification") == "named-private-waiver"])
            == PRIVATE_WAIVER_COUNT,
            "preserve all genuine upstream methods and exactly thirteen named private waivers")
    original_re = sys.modules.get("re")
    require(type(original_re) is types.ModuleType,
            "quarantine the actual pinned original upstream matcher")
    previous_guard = harness.original_regex_guard

    @contextlib.contextmanager
    def selected_guard(baseline: Any, actual: Mapping[str, str]) -> Iterator[dict[str, Any]]:
        require(dict(actual) == pins,
                "the actual upstream candidate's native closure changed")
        with chosen_six_family_guard(
            original, identity, warning, baseline,
            spec, pins, source_pins,
        ) as active:
            yield active

    try:
        with warning.installed_warning_safe_guard(identity):
            harness.original_regex_guard = selected_guard
            observed = harness.execute_original_worker(
                "rust", "rust", original.HARNESS_SHA256, pins,
            )
    except BaseException as error:
        raise ActualSuiteFailure(
            "the literal unchanged upstream public-method source failed",
            {
                "schema": SCHEMA + "-genuine-original-upstream-failure",
                "status": "FAIL", "suite": suite.name,
                "candidate_family": spec.name,
                "error_type": type(error).__qualname__,
                "error_message": str(error),
                "traceback": traceback.format_exception(
                    type(error), error, error.__traceback__),
                "actual_candidate_workers": 1,
                "performance": "NOT MEASURED", "holdout": "NOT OPENED",
                "hidden_cases_read": 0, "benchmark_files_read": 0,
                "clock_samples": 0,
            },
        ) from error
    finally:
        harness.original_regex_guard = previous_guard
    records = observed.get("records")
    require(type(records) is list and len(records) == ORIGINAL_PUBLIC_RECORD_COUNT
            and observed.get("matrix_sha256") == suite.matrix_sha256
            and observed.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and len(observed.get("private_waivers", [])) == PRIVATE_WAIVER_COUNT,
            "preserve the complete original 152 public-method records and 13 waivers")
    skips = [row for row in records if row.get("status") == "SKIP"]
    require(len(skips) <= 1
            and (not skips or (
                skips[0].get("test") == "ReTests.test_memory_leaks"
                and skips[0].get("skip_reasons") == ["requires debug build"]
            )), "never waive or replace the actual original debug-build skip")
    digest = original.digest(records)
    failures = [row for row in records if row.get("status") == "FAIL"]
    if digest != suite.reference_sha256 and not failures:
        failures = [{
            "type": "ActualOriginalVectorMismatch",
            "expected_records_sha256": suite.reference_sha256,
            "actual_records_sha256": digest,
            "complete_actual_records": records,
        }]
    passed = (not failures and len(skips) == ORIGINAL_DEBUG_SKIP_COUNT
              and digest == suite.reference_sha256
              and observed.get("pass_count") == suite.case_count)
    return {
        "schema": SCHEMA + "-actual-original-suite",
        "status": "PASS" if passed else "FAIL",
        "suite": suite.name, "candidate_family": spec.name,
        "candidate_module": spec.module,
        "source_relative": suite.source_relative,
        "source_sha256": suite.source_sha256,
        "matrix_sha256": suite.matrix_sha256,
        "reference_records_sha256": suite.reference_sha256,
        "candidate_records_sha256": digest,
        "case_execution_denominator": suite.case_count,
        "actual_candidate_case_count": suite.case_count,
        "actual_public_record_count": len(records),
        "actual_debug_skip_count": len(skips),
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "named_private_waivers": observed["private_waivers"],
        "candidate_records": records,
        "mismatch_count": len(failures),
        "all_mismatches": failures,
        "native_provenance": observed.get("native_provenance"),
        "matcher_guard": observed.get("matcher_guard"),
        "actual_candidate_workers": 1,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "candidate_qualified": False, "winner_selected": False,
    }


def nested_original_family(nested: Any, spec: FamilySpec) -> Any:
    return nested.FamilySpec(
        spec.name,
        "c_vm" if spec.name == "c" else spec.name,
        spec.module, spec.adapter_relative, spec.bridge_module,
        spec.engine_relative, spec.bridge_relative,
        tuple(relative for relative, _, _ in spec.source_owners),
    )


def install_owned_interpreter_guard(
    family: str, pins: Mapping[str, str], sources: Mapping[str, str],
    *, owner: str, producer_sha256: str,
) -> None:
    verify_runtime()
    require(owner in {"A", "B", "C"},
            "assign a genuine isolated candidate interpreter owner")
    read_owned(SOURCE_RELATIVE, producer_sha256, maximum=MAX_SOURCE_BYTES)
    spec = family_spec(family)
    require(type(pins) is dict and set(pins)
            == {"source", "native_engine", "native_bridge"}
            and type(sources) is dict
            and sources == {path: digest for path, digest, _ in spec.source_owners},
            "authenticate every source owner in the real private interpreter")
    original = frozen_module(ORIGINAL_V5_RELATIVE, ORIGINAL_V5_SHA256)
    warning, identity, _, _ = original.load_frozen_oracles()
    genuine_original = importlib.import_module("re")
    stack = contextlib.ExitStack()
    try:
        stack.enter_context(warning.installed_warning_safe_guard(identity))
        active = stack.enter_context(chosen_six_family_guard(
            original, identity, warning, genuine_original,
            spec, dict(pins), dict(sources),
        ))
        active["verify"]()
        module = active["candidate"]
        bridge = sys.modules.get(spec.bridge_module)
        require(type(module) is types.ModuleType
                and module.__name__ == spec.module
                and type(bridge) is types.ModuleType
                and sys.modules.get("re") is module,
                "install the genuine independently owned interpreter-local candidate")
        builtins._rebar_owned_candidate_subinterpreter_v1 = {
            "candidate": module,
            "adapter_module": spec.module,
            "bridge_module": spec.bridge_module,
            "bridge": bridge,
            "verify": active["verify"],
            "stack": stack,
            "original": genuine_original,
            "candidate_origin_verified": True,
            "candidate_import_count": 1,
            "original_matcher_calls": 0,
            "external_engine_imports": 0,
            "cross_candidate_imports": 0,
            "foreign_native_loads": 0,
        }
        builtins._rebar_subinterpreter_v2_owner = owner
        builtins._rebar_subinterpreter_v2_patterns = {}
    except BaseException:
        stack.close()
        raise


def interpreter_bootstrap_source(
    spec: FamilySpec, pins: Mapping[str, str], source_pins: Mapping[str, str],
    *, owner: str, producer_sha256: str,
) -> str:
    require(owner in {"A", "B", "C"},
            "choose one genuinely independent interpreter lifecycle owner")
    checked_digest(producer_sha256, "six-family interpreter bootstrap source")
    code = (
        "import os as _six_os\n"
        "import sys as _six_sys\n"
        "import importlib as _six_importlib\n"
        "_six_root = " + repr(str(ROOT)) + "\n"
        "if not _six_sys.path or _six_sys.path[0] != _six_root:\n"
        "    _six_sys.path.insert(0, _six_root)\n"
        "assert not any(name == 'candidates' or name.startswith('candidates.') "
        "for name in _six_sys.modules), 'a candidate entered the real interpreter early'\n"
        "_six_producer = _six_importlib.import_module("
        + repr(SOURCE_RELATIVE.removesuffix(".py").replace("/", ".")) + ")\n"
        "assert _six_os.path.realpath(_six_producer.__file__) == "
        + repr(str(ROOT / SOURCE_RELATIVE)) + "\n"
        "_six_producer.install_owned_interpreter_guard("
        + repr(spec.name) + ", " + repr(dict(pins)) + ", "
        + repr(dict(sorted(source_pins.items())))
        + ", owner=" + repr(owner)
        + ", producer_sha256=" + repr(producer_sha256) + ")\n"
    )
    try:
        ast.parse(code, filename="<frozen-six-family-owned-interpreter-bootstrap>")
    except (SyntaxError, ValueError, RecursionError) as error:
        raise ProducerError("the exact six-family genuine interpreter bootstrap is invalid") from error
    return code


def validate_nested_case(
    nested: Any, record: Any, baseline: Any,
    spec: FamilySpec, pins: Mapping[str, str],
) -> dict[str, Any]:
    required = nested.REQUIRED_CASE_FIELDS | nested.REQUIRED_CANDIDATE_FIELDS
    require(type(record) is dict and set(record) == required
            and record.get("candidate_family") == spec.name
            and record.get("candidate_module") == spec.module
            and record.get("candidate_origin_verified") is True
            and type(record.get("candidate_import_count")) is int
            and record["candidate_import_count"] >= 1,
            "require one complete genuinely imported private-interpreter observation")
    for field, key in (("candidate_source_sha256", "source"),
                       ("candidate_engine_sha256", "native_engine"),
                       ("candidate_bridge_sha256", "native_bridge")):
        require(record.get(field) == checked_digest(pins.get(key), key),
                "the actual interpreter switched its native candidate owner")
    require((record["candidate_engine_sha256"]
             == record["candidate_bridge_sha256"])
            is spec.combined_native,
            "preserve the real combined C/C++ and separate Go/Fortran native ABIs")
    for name in ("original_matcher_calls", "external_engine_imports",
                 "cross_candidate_imports", "foreign_native_loads"):
        require(type(record.get(name)) is int and record[name] == 0,
                "an actual subinterpreter delegated regex production: " + name)
    actual = {name: record[name] for name in nested.REQUIRED_CASE_FIELDS}
    require(nested.canonical(actual)
            == nested.canonical(nested.project_reference_record(baseline)),
            "retain the exact unchanged original source-owned nested semantics")
    return actual


def observe_owned_interpreter(
    nested: Any, interpreter: Any, *, case: dict[str, Any],
    baseline: dict[str, Any], owner: str, main_id: int,
    program: Mapping[str, Any], original_spec: Any,
    spec: FamilySpec, pins: Mapping[str, str],
    reference: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    events: list[dict[str, Any]] = []
    pieces: list[bytes] = []
    reader: int | None = None
    writer: int | None = None
    result: dict[str, Any] | None = None
    failure: BaseException | None = None
    eof = False
    stage = "open-genuine-owned-interpreter-pipe"
    try:
        reader, writer = os.pipe()
        events.extend((
            {"role": "reader", "action": "open", "fd": reader, "status": "PASS"},
            {"role": "writer", "action": "open", "fd": writer, "status": "PASS"},
        ))
        stage = "compose-unchanged-source-owned-interpreter-case"
        script = nested.observation_source(
            case, writer, owner, main_id, reference["source"],
            program, original_spec, pins, str(ROOT),
        )
        stage = "execute-genuine-owned-public-subinterpreter"
        require(interpreter.exec(script) is None,
                "the exact genuine in-interpreter original matching case failed")
        stage = "close-genuine-owned-pipe-writer"
        closing = writer
        writer = None
        os.close(closing)
        events.append({"role": "writer", "action": "close", "fd": closing,
                       "status": "PASS"})
        stage = "read-genuine-owned-case-pipe-to-eof"
        total = 0
        while True:
            request = min(65_536, MAX_PIPE_BYTES - total + 1)
            part = os.read(reader, request)
            events.append({"role": "reader", "action": "read", "fd": reader,
                           "requested_bytes": request,
                           "returned_bytes": len(part), "status": "PASS"})
            if not part:
                eof = True
                break
            total += len(part)
            require(total <= MAX_PIPE_BYTES,
                    "retain the unchanged 256-KiB genuine interpreter pipe bound")
            pieces.append(part)
        stage = "decode-complete-genuine-owned-interpreter-observation"
        result = nested.decode_document(
            b"".join(pieces), "genuine six-family interpreter observation",
            newline=True,
        )
        validate_nested_case(nested, result, baseline, spec, pins)
    except BaseException as error:
        failure = error
    finally:
        for role in ("writer", "reader"):
            descriptor = writer if role == "writer" else reader
            if descriptor is None:
                continue
            if role == "writer":
                writer = None
            else:
                reader = None
            event = {"role": role, "action": "close", "fd": descriptor,
                     "status": "PENDING"}
            events.append(event)
            try:
                os.close(descriptor)
            except BaseException as cleanup:
                event.update(status="FAIL", error_type=type(cleanup).__name__,
                             error_message=str(cleanup))
                if failure is None:
                    failure = cleanup
            else:
                event["status"] = "PASS"
    if failure is not None:
        raise ActualSuiteFailure(
            "preserve a real private interpreter, candidate, or pipe failure",
            {
                "status": "FAIL", "candidate_family": spec.name,
                "active_case": case, "active_phase": stage,
                "interpreter_role": owner,
                "error_type": type(failure).__qualname__,
                "error_message": str(failure),
                "partial_observation_stream": nested.encoded_stream(b"".join(pieces)),
                "observation_stream_complete": eof,
                "descriptor_events": events,
            },
        ) from failure
    require(type(result) is dict and eof
            and all(row.get("status") == "PASS" for row in events)
            and sum(row.get("action") == "open" for row in events) == 2
            and sum(row.get("action") == "close" for row in events) == 2,
            "keep both real observation descriptors and their complete EOF lifecycle")
    return result, {
        "case_id": case["case_id"], "owner": owner,
        "interpreter_id": int(interpreter.id),
        "reached_eof": True, "all_descriptors_closed": True,
        "descriptor_events": events,
        "observation_stream": nested.encoded_stream(b"".join(pieces)),
    }


def observe_subinterpreters(
    suite: SuiteSpec, spec: FamilySpec, pins: dict[str, str],
    source_pins: dict[str, str], *, producer_sha256: str,
) -> dict[str, Any]:
    nested = frozen_module(NESTED_ORIGINAL_RELATIVE, NESTED_ORIGINAL_SHA256)
    reference = nested.load_original_baseline()
    require(type(reference) is dict
            and len(reference.get("matrix", [])) == NESTED_CASE_COUNT
            and len(reference.get("records", [])) == NESTED_CASE_COUNT
            and reference["source"].validate_matrix(reference["matrix"])
            == suite.matrix_sha256
            and nested.digest(reference["records"]) == suite.reference_sha256
            and nested.digest(reference["projected_records"])
            == NESTED_PROJECTED_REFERENCE_SHA256,
            "load only the existing exact original 128-case interpreter reference")
    neutral = {
        "source": pins["source"],
        "native_engine": pins["native_engine"],
        "native_bridge": pins["native_engine"],
    }
    program = nested.compose_owned_program(
        reference["original_program"], nested.FAMILIES["c"], neutral,
    )
    original_spec = nested_original_family(nested, spec)
    nested.authenticate_path(Path(nested.PINNED_INTERPRETERS),
                             nested.PINNED_INTERPRETERS_SHA256,
                             maximum=MAX_SOURCE_BYTES)
    public = importlib.import_module("concurrent.interpreters")
    require(type(public) is types.ModuleType and public.__spec__ is not None
            and os.path.abspath(str(public.__spec__.origin))
            == nested.PINNED_INTERPRETERS,
            "load only the original pinned public subinterpreter provider")
    before = {int(item.id) for item in public.list_all()}
    main_id = int(public.get_current().id)
    before_locale = locale.setlocale(locale.LC_CTYPE)
    first = second = third = temporary = None
    created = destroyed = executions = initializations = cleanups = 0
    active_case: dict[str, Any] | None = None
    active_phase = "create-genuine-owned-interpreter-A"
    identities: dict[str, Any] = {"A": None, "B": None, "C": None,
                                  "temporary": []}
    records: list[dict[str, Any]] = []
    peers: list[dict[str, Any]] = []
    repeats: list[dict[str, Any]] = []
    fresh: list[dict[str, Any]] = []
    pipes: list[dict[str, Any]] = []
    post_b: dict[str, Any] | None = None
    final_c: dict[str, Any] | None = None
    prepared: set[int] = set()
    cleanup_failures: list[dict[str, Any]] = []
    primary: BaseException | None = None

    def prepare(interpreter: Any, owner: str) -> None:
        nonlocal initializations
        initializations += 1
        code = interpreter_bootstrap_source(
            spec, pins, source_pins, owner=owner,
            producer_sha256=producer_sha256,
        )
        require(interpreter.exec(code) is None,
                "install the genuine persistent six-family original matcher guard")
        prepared.add(int(interpreter.id))

    def close(interpreter: Any) -> None:
        nonlocal cleanups, destroyed
        identity = int(interpreter.id)
        require(identity in {int(item.id) for item in public.list_all()},
                "an actual private Python interpreter disappeared")
        if identity in prepared:
            cleanups += 1
            require(interpreter.exec(nested.interpreter_cleanup_source()) is None,
                    "restore the exact original matcher in its real interpreter")
            prepared.remove(identity)
        interpreter.close()
        destroyed += 1
        require(identity not in {int(item.id) for item in public.list_all()},
                "a real private Python interpreter remained alive after cleanup")

    def execute(interpreter: Any, case: dict[str, Any], owner: str,
                expected: dict[str, Any]) -> dict[str, Any]:
        nonlocal executions
        executions += 1
        actual, ledger = observe_owned_interpreter(
            nested, interpreter, case=case, baseline=expected,
            owner=owner, main_id=main_id, program=program,
            original_spec=original_spec, spec=spec, pins=pins,
            reference=reference,
        )
        pipes.append(ledger)
        return actual

    try:
        first = public.create()
        created += 1
        identities["A"] = int(first.id)
        active_phase = "create-genuine-owned-interpreter-B"
        second = public.create()
        created += 1
        identities["B"] = int(second.id)
        require(len({main_id, identities["A"], identities["B"]}) == 3,
                "keep both genuinely distinct simultaneously live interpreters")
        active_phase = "install-original-private-guard-A"
        prepare(first, "A")
        active_phase = "install-original-private-guard-B"
        prepare(second, "B")
        for case, expected in zip(reference["matrix"], reference["records"],
                                  strict=True):
            active_case = case
            active_phase = "execute-real-interpreter-A"
            left = execute(first, case, "A", expected)
            records.append(left)
            active_phase = "execute-real-interpreter-B"
            middle = execute(second, case, "B", expected)
            peers.append(middle)
            active_phase = "execute-real-interpreter-A-after-B"
            right = execute(first, case, "A", expected)
            repeats.append(right)
            require(nested.canonical(left) == nested.canonical(middle)
                    and nested.canonical(left) == nested.canonical(right),
                    "all original A/B/A in-interpreter observations must agree")
        temporary_cases = [
            case for case in reference["matrix"]
            if case["cohort"] == "repeated-interpreter-creation-and-destruction"
        ]
        require(len(temporary_cases) == NESTED_FRESH_INTERPRETER_COUNT,
                "preserve all eight genuinely newly created original interpreters")
        for case in temporary_cases:
            active_case = case
            active_phase = "create-genuine-fresh-private-interpreter"
            temporary = public.create()
            created += 1
            identities["temporary"].append(int(temporary.id))
            active_phase = "install-genuine-fresh-original-guard"
            prepare(temporary, "C")
            active_phase = "execute-genuine-fresh-private-case"
            fresh.append(execute(
                temporary, case, "C", reference["records"][case["ordinal"]],
            ))
            active_phase = "restore-and-destroy-genuine-fresh-interpreter"
            close(temporary)
            temporary = None
        active_phase = "restore-and-destroy-genuine-interpreter-B"
        close(second)
        second = None
        active_phase = "execute-genuine-A-after-B-destruction"
        active_case = reference["matrix"][-1]
        post_b = execute(first, active_case, "A", reference["records"][-1])
        active_phase = "restore-and-destroy-genuine-interpreter-A"
        close(first)
        first = None
        active_phase = "create-genuine-final-private-interpreter-C"
        third = public.create()
        created += 1
        identities["C"] = int(third.id)
        active_phase = "install-genuine-final-private-guard"
        prepare(third, "C")
        active_phase = "execute-genuine-final-private-interpreter-C"
        final_c = execute(third, active_case, "C", reference["records"][-1])
        active_phase = "restore-and-destroy-genuine-final-interpreter-C"
        close(third)
        third = None
        require(created == destroyed == initializations == cleanups
                == NESTED_INTERPRETER_COUNT
                and executions == NESTED_CASE_EXECUTIONS and not prepared,
                "only the genuine complete 128/394/11/11 lifecycle can pass")
    except BaseException as error:
        primary = error
    finally:
        for owner, interpreter in (("temporary", temporary), ("C", third),
                                   ("B", second), ("A", first)):
            if interpreter is None:
                continue
            try:
                close(interpreter)
            except BaseException as error:
                cleanup_failures.append({
                    "role": owner, "interpreter_id": int(interpreter.id),
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                })
    if primary is not None or cleanup_failures:
        details: dict[str, Any] = {
            "schema": SCHEMA + "-genuine-nested-failure",
            "status": "FAIL", "candidate_family": spec.name,
            "active_phase": active_phase, "active_case": active_case,
            "actual_interpreter_ids": identities,
            "completed_a_records": records,
            "completed_b_records": peers,
            "completed_repeated_a_records": repeats,
            "completed_fresh_records": fresh,
            "actual_post_b_close_a_record": post_b,
            "actual_fresh_c_record": final_c,
            "actual_case_interpreter_exec_calls": executions,
            "actual_initialization_interpreter_exec_calls": initializations,
            "actual_guard_cleanup_interpreter_exec_calls": cleanups,
            "actual_interpreters_created": created,
            "actual_interpreters_destroyed": destroyed,
            "actual_prepared_interpreter_ids": sorted(prepared),
            "pipe_ledgers": pipes,
            "cleanup_failures": cleanup_failures,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
        }
        if primary is not None:
            details.update(error_type=type(primary).__name__,
                           error_message=str(primary))
            extra = getattr(primary, "details", None)
            if type(extra) is dict:
                details["actual_case_failure"] = extra
        raise ActualSuiteFailure(
            "retain every genuine failed private-interpreter call and cleanup",
            details,
        ) from primary
    require({int(item.id) for item in public.list_all()} == before
            and locale.setlocale(locale.LC_CTYPE) == before_locale,
            "restore the exact live interpreter set and real locale")
    require(type(post_b) is dict and type(final_c) is dict,
            "retain the actual A-after-B and newly created final C observations")
    for rows in (records, peers, repeats):
        require(len(rows) == NESTED_CASE_COUNT,
                "keep every original source-ordered private-interpreter case")
        for case, actual, baseline in zip(reference["matrix"], rows,
                                          reference["records"], strict=True):
            require(actual.get("case_id") == case["case_id"],
                    "an original interpreter case was omitted or reordered")
            validate_nested_case(nested, actual, baseline, spec, pins)
        projected = [
            {name: actual[name] for name in nested.REQUIRED_CASE_FIELDS}
            for actual in rows
        ]
        require(nested.digest(projected) == NESTED_PROJECTED_REFERENCE_SHA256,
                "preserve every exact original projected interpreter observation")
    nested.validate_pipe_schedule(
        reference["matrix"], identities, pipes,
        records, peers, repeats, fresh, post_b, final_c,
    )
    return {
        "schema": SCHEMA + "-actual-original-suite",
        "status": "PASS", "suite": suite.name,
        "candidate_family": spec.name,
        "candidate_module": spec.module,
        "case_execution_denominator": NESTED_CASE_COUNT,
        "actual_candidate_case_count": NESTED_CASE_COUNT,
        "source_relative": suite.source_relative,
        "source_sha256": suite.source_sha256,
        "matrix_sha256": suite.matrix_sha256,
        "reference_records_sha256": suite.reference_sha256,
        "projected_reference_records_sha256": NESTED_PROJECTED_REFERENCE_SHA256,
        "candidate_records": records,
        "peer_records": peers,
        "repeated_a_records": repeats,
        "repeated_creation_records": fresh,
        "actual_post_b_close_a_record": post_b,
        "actual_fresh_c_record": final_c,
        "actual_interpreter_ids": identities,
        "actual_case_interpreter_exec_calls": executions,
        "actual_initialization_interpreter_exec_calls": initializations,
        "actual_guard_cleanup_interpreter_exec_calls": cleanups,
        "actual_interpreters_created": created,
        "actual_interpreters_destroyed": destroyed,
        "all_real_pipes_read_to_eof": all(item["reached_eof"] for item in pipes),
        "all_real_pipe_descriptors_closed": all(
            item["all_descriptors_closed"] for item in pipes),
        "pipe_ledgers": pipes,
        "interpreter_live_set_restored": True,
        "locale_restored": True,
        "mismatch_count": 0,
        "all_mismatches": [],
        "actual_candidate_workers": 1,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "candidate_qualified": False, "winner_selected": False,
    }


def run_actual_suite(options: argparse.Namespace) -> dict[str, Any]:
    context_options = argparse.Namespace(
        source_sha256=options.source_sha256,
        protocol_sha256=options.protocol_sha256,
        document_sha256=options.document_sha256,
    )
    context = verify_frozen_context(context_options)
    require(context.get("status") == "PASS"
            and context.get("total_distinct_historical_evidence_owner_count")
            == PRESERVED_EVIDENCE_OWNER_COUNT
            and context.get("total_authenticated_historical_reference_path_count")
            == PRESERVED_REFERENCE_PATH_COUNT,
            "reauthenticate all actual frozen original and historical evidence")
    spec = family_spec(options.family)
    suite = suite_spec(options.suite)
    source_pins = parse_source_owners(spec, options.owned_source_sha256)
    pins = native_pins(spec, options)
    approval, _ = authenticate_actual_activation(options, spec)
    phase1_raw, _ = read_owned(PHASE1_RELATIVE, PHASE1_SHA256,
                                maximum=MAX_SOURCE_BYTES)
    phase1 = decode_document(phase1_raw, "actual frozen phase-one inventory",
                             canonical_required=True)
    if suite.name == "original_bounded_v5":
        observed = observe_original_upstream(suite, spec, pins, source_pins)
    elif suite.name == "subinterpreter_v2":
        observed = observe_subinterpreters(
            suite, spec, pins, source_pins,
            producer_sha256=options.source_sha256,
        )
    else:
        observed = observe_direct_suite(suite, spec, pins, source_pins, phase1)
    observed["actual_verified_native_activation"] = {
        "family": approval["family"],
        "build_version": options.build_version,
        "activation_source_sha256": options.activation_source_sha256,
        "reversible_canonical_activation": True,
        "activation_started_by_producer": False,
    }
    observed["phase_one_case_execution_denominator"] = CASE_DENOMINATOR
    observed["supplemental_cases_added_to_phase_one"] = False
    observed["total_preserved_historical_evidence_owner_count"] = (
        PRESERVED_EVIDENCE_OWNER_COUNT
    )
    observed["total_authenticated_historical_reference_path_count"] = (
        PRESERVED_REFERENCE_PATH_COUNT
    )
    return observed


def validate_successful_nested_lifecycle(value: Any) -> dict[str, Any]:
    expected = protocol_document()["successful_nested_lifecycle"]
    require(type(value) is dict and canonical(value) == canonical(expected),
            "only all original 128 cases, 394 calls, and eleven complete interpreter "
            "lifecycles can qualify")
    require(value["actual_case_interpreter_exec_calls"]
            != HISTORICAL_FAILED_ZIG_EXECUTIONS,
            "the historical failed 385-call Zig lifecycle is never a passing result")
    return value


def validate_synthetic_activation(value: Any) -> dict[str, Any]:
    require(type(value) is dict and set(value) == {
        "family", "build_version", "activation_version", "build_status",
        "activation_status", "phase_count", "actual_source_build",
        "actual_reversible_activation", "source_owner_count",
        "combined_native_engine_and_bridge", "candidate_qualified",
    }, "require the complete genuine version-bound activation proof")
    spec = family_spec(value.get("family"))
    policy = protocol_document()["activation_policy"].get(spec.name)
    require(type(policy) is dict,
            "a failed Go or Fortran build cannot create an activation proof")
    require(value["build_version"] == policy["native_build_version"]
            and value["activation_version"] == policy["activation_version"]
            and value["build_status"] == "PASS"
            and value["activation_status"] == "PASS"
            and value["phase_count"] == 2
            and value["actual_source_build"] is True
            and value["actual_reversible_activation"] is True
            and value["source_owner_count"] == len(spec.source_owners)
            and value["combined_native_engine_and_bridge"] is spec.combined_native
            and value["candidate_qualified"] is False,
            "reject failed, invented, cross-family, V5-only, or candidate-qualified activation")
    return value


def synthetic_activation(family: str) -> dict[str, Any]:
    spec = family_spec(family)
    policy = protocol_document()["activation_policy"][family]
    require(type(policy) is dict,
            "no synthetic activation exists for a real failed Go or Fortran build")
    return {
        "family": family,
        "build_version": policy["native_build_version"],
        "activation_version": policy["activation_version"],
        "build_status": "PASS",
        "activation_status": "PASS",
        "phase_count": 2,
        "actual_source_build": True,
        "actual_reversible_activation": True,
        "source_owner_count": len(spec.source_owners),
        "combined_native_engine_and_bridge": spec.combined_native,
        "candidate_qualified": False,
    }


def validate_synthetic_observation(value: Any) -> dict[str, Any]:
    require(type(value) is dict and set(value) == {
        "suite", "family", "case_count", "source_sha256", "matrix_sha256",
        "reference_records_sha256", "published_seed_decimal",
        "source_owner_count", "combined_native_engine_and_bridge",
        "actual_candidate_workers", "actual_reference_workers",
        "clock_samples", "hidden_cases_read", "benchmark_files_read",
        "performance", "holdout", "candidate_qualified",
    }, "preserve every exact candidate-facing original suite obligation")
    suite = suite_spec(value.get("suite"))
    spec = family_spec(value.get("family"))
    require(value["case_count"] == suite.case_count
            and value["source_sha256"] == suite.source_sha256
            and value["matrix_sha256"] == suite.matrix_sha256
            and value["reference_records_sha256"] == suite.reference_sha256
            and value["published_seed_decimal"]
            == (None if suite.seed is None else str(suite.seed))
            and value["source_owner_count"] == len(spec.source_owners)
            and value["combined_native_engine_and_bridge"] is spec.combined_native
            and value["actual_candidate_workers"] == 0
            and value["actual_reference_workers"] == 0
            and value["clock_samples"] == 0
            and value["hidden_cases_read"] == 0
            and value["benchmark_files_read"] == 0
            and value["performance"] == "NOT MEASURED"
            and value["holdout"] == "NOT OPENED"
            and value["candidate_qualified"] is False,
            "reject altered cases, guessed results, cross-family ownership, or timing")
    return value


def synthetic_observation(suite: SuiteSpec, family: FamilySpec) -> dict[str, Any]:
    return {
        "suite": suite.name,
        "family": family.name,
        "case_count": suite.case_count,
        "source_sha256": suite.source_sha256,
        "matrix_sha256": suite.matrix_sha256,
        "reference_records_sha256": suite.reference_sha256,
        "published_seed_decimal": None if suite.seed is None else str(suite.seed),
        "source_owner_count": len(family.source_owners),
        "combined_native_engine_and_bridge": family.combined_native,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_qualified": False,
    }


def synthetic_owned_public_types(
    family: str,
) -> tuple[FamilySpec, types.ModuleType, types.ModuleType]:
    spec = family_spec(family)
    module = types.ModuleType(spec.module)
    bridge = types.ModuleType(spec.bridge_module)
    if family in {"rust", "c", "zig"}:
        match = type("Match", (), {"__module__": "re"})
        bridge.Match = match
        if family == "c":
            native_pattern = type("Pattern", (), {"__module__": "re"})
            bridge.Pattern = native_pattern
            pattern = type("Pattern", (native_pattern,),
                           {"__module__": "re"})
        else:
            pattern = type("Pattern", (), {"__module__": "re"})
    elif family == "go":
        def owned_new(cls: type, *args: Any, **kwargs: Any) -> Any:
            del cls, args, kwargs
            raise TypeError("cannot directly create a native Go public type")

        def owned_create(cls: type, *args: Any) -> Any:
            del args
            return object.__new__(cls)

        owned_new.__module__ = spec.module
        owned_create.__module__ = spec.module
        namespace = {
            "__module__": spec.module,
            "__new__": owned_new,
            "_create": classmethod(owned_create),
        }
        pattern = type("Pattern", (), dict(namespace))
        match = type("Match", (), dict(namespace))
    else:
        def owned_init(self: Any, *args: Any) -> None:
            del self, args

        owned_init.__module__ = spec.module
        pattern = type("Pattern", (), {
            "__module__": spec.module, "__init__": owned_init,
        })
        match = type("Match", (), {
            "__module__": spec.module, "__init__": owned_init,
        })
    module.Pattern = pattern
    module.Match = match
    return spec, module, bridge


def self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted
                and name not in rejected and condition is True,
                "a positive independent source control failed: " + name)
        accepted.append(name)

    def reject(name: str, callback: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected
                and name not in accepted,
                "a hostile independent source control was repeated")
        try:
            callback()
        except (ProducerError, SourceOnlyViolation, ValueError, TypeError,
                KeyError, OverflowError, RecursionError, UnicodeError,
                AssertionError):
            rejected.append(name)
        else:
            raise ProducerError("a hostile source mutation escaped: " + name)

    with EffectBoundary(source_only=True) as boundary:
        contract = protocol_document()
        accept("freeze-exact-complete-original-source-contract",
               validate_protocol_document(contract) is contract)
        accept("preserve-all-thirteen-source-ordered-original-suites",
               len(contract["suites"]) == SUITE_COUNT)
        accept("preserve-all-31237-unchanged-original-cases",
               sum(row["case_execution_count"]
                   for row in contract["suites"]) == CASE_DENOMINATOR)
        accept("preserve-six-genuinely-independent-native-families",
               len(contract["families"]) == 6)
        accept("preserve-all-25-distinct-owned-semantic-sources",
               contract["source_owner_count"] == 25
               and contract["pairwise_shared_semantic_source_count"] == 0)
        accept("freeze-all-103-genuine-historical-evidence-file-owners",
               contract["historical_evidence"]
               ["total_distinct_evidence_owner_count"]
               == PRESERVED_EVIDENCE_OWNER_COUNT)
        accept("freeze-all-108-independently-authenticated-history-paths",
               contract["historical_evidence"]
               ["total_authenticated_reference_path_count"]
               == PRESERVED_REFERENCE_PATH_COUNT)
        accept("preserve-all-30-actual-repaired-c-campaign-owners",
               contract["historical_evidence"]
               ["new_repaired_c_campaign_evidence_owner_count"]
               == PRESERVED_NEW_CAMPAIGN_OWNER_COUNT)
        accept("preserve-all-thirteen-real-12-plus-1-runner-failures",
               contract["historical_evidence"]
               ["actual_repaired_c_failure_causes"] == {
                   "PYTHON-COMPATIBLE PUBLIC TYPE OWNERSHIP CHECK": 12,
                   "SAVED PYTHON REFERENCE DECODING": 1,
               })
        accept("freeze-only-the-four-unchanged-v21-graph-owners",
               set(contract["frozen_v21_history"]["owners"])
               == {"source", "inputs", "summary", "svg"}
               and contract["frozen_v21_history"]
               ["actual_evidence_owner_count"] == PRESERVED_EVIDENCE_OWNER_COUNT
               and contract["frozen_v21_history"]
               ["authenticated_reference_path_count"]
               == PRESERVED_REFERENCE_PATH_COUNT)
        reference = contract["frozen_public_type_reference"]
        accept("freeze-both-genuine-signed-6912-case-public-reference-workers",
               reference["case_count"] == 6912
               and reference["reference_pids"] == list(PUBLIC_REFERENCE_PIDS)
               and reference["new_reference_processes_started"] == 0
               and reference["candidate_family_selected_by_baseline"] is False
               and reference["records_sha256"]
               == suite_spec("public_types_v1").reference_sha256)
        accept("freeze-lossless-55903155-byte-original-public-reference-report",
               reference["archive_sha256"] == PUBLIC_BASELINE_ARCHIVE_SHA256
               and reference["receipt_sha256"] == PUBLIC_BASELINE_RECEIPT_SHA256
               and reference["uncompressed_sha256"]
               == PUBLIC_BASELINE_UNCOMPRESSED_SHA256
               and reference["uncompressed_size_bytes"]
               == PUBLIC_BASELINE_UNCOMPRESSED_BYTES)
        accept("retain-all-six-different-source-backed-native-method-profiles",
               set(contract["native_bridge_profiles"])
               == set(FAMILIES) == set(BRIDGE_METHOD_PROFILES)
               and "build" in BRIDGE_METHOD_PROFILES["c"]
               and "compile" not in BRIDGE_METHOD_PROFILES["c"]
               and BRIDGE_METHOD_PROFILES["go"] == ("compile", "execute"))
        accept("restrict-upstream-native-authentication-to-three-real-families",
               contract["frozen_original_v5_evaluator"]
               ["supported_upstream_native_families"] == ["rust", "c", "zig"]
               and contract["frozen_original_v5_evaluator"]
               ["unsupported_families_use_complete_v1_owner_policy"]
               == ["cpp", "go", "fortran"])
        accept("preserve-both-real-v5-go-and-fortran-source-build-failures",
               {row["family"]: row["status"]
                for row in contract["historical_evidence"]["source_builds"]}
               == {"go": "FAIL", "fortran": "FAIL"})
        accept("allow-genuine-combined-c-and-cpp-native-bridges",
               FAMILIES["c"].combined_native is True
               and FAMILIES["cpp"].combined_native is True
               and all(FAMILIES[name].combined_native is False
                       for name in ("rust", "zig", "go", "fortran")))
        accept("allow-first-party-zig-ffi-only",
               [name for name, value in FAMILIES.items() if value.owned_ctypes]
               == ["zig"])
        lifecycle = copy.deepcopy(contract["successful_nested_lifecycle"])
        accept("freeze-real-original-128-case-394-call-11-interpreter-lifecycle",
               validate_successful_nested_lifecycle(lifecycle) is lifecycle)
        historical = contract["historical_evidence"]["failed_zig_is_not_a_success"]
        accept("preserve-genuine-zig-385-call-failure-as-failed",
               historical["actual_case_interpreter_exec_calls"] == 385
               and historical["candidate_status"] == "FAIL"
               and historical["verified_passing_nested_cases"] == 0)
        for name in ("rust", "c", "zig", "cpp"):
            claim = synthetic_activation(name)
            accept("accept-exact-version-correct-actual-activation-" + name,
                   validate_synthetic_activation(claim) is claim)
        accept("preserve-original-private-waivers-and-real-debug-skip",
               contract["phase_one"]["named_private_waiver_count"] == 13
               and contract["phase_one"]["original_public_record_count"] == 152
               and contract["phase_one"]["original_real_debug_skip_count"] == 1)
        accept("leave-performance-and-holdout-unmeasured",
               contract["verification_effects"]["performance"] == "NOT MEASURED"
               and contract["verification_effects"]["holdout"] == "NOT OPENED"
               and contract["verification_effects"]["winner_selected"] is False)

        for suite_index, suite in enumerate(SUITES):
            for family_name in FAMILIES:
                family = family_spec(family_name)
                observation = synthetic_observation(suite, family)
                accept("accept-" + suite.name + "-" + family_name
                       + "-original-source-route",
                       validate_synthetic_observation(observation) is observation)
            for field, changed in (
                ("case_execution_count", suite.case_count + 1),
                ("source_sha256", "0" * 64),
                ("matrix_sha256", "1" * 64),
                ("reference_records_sha256", "2" * 64),
                ("unchanged_original_producer_route", "invented-wrapper"),
                ("id", "changed-" + suite.name),
            ):
                def poison_contract(index: int = suite_index,
                                    key: str = field,
                                    value: Any = changed) -> Any:
                    forged = copy.deepcopy(contract)
                    forged["suites"][index][key] = value
                    return validate_protocol_document(forged)

                reject("reject-" + suite.name + "-" + field, poison_contract)
            if suite.seed is not None:
                def poison_seed(index: int = suite_index) -> Any:
                    forged = copy.deepcopy(contract)
                    forged["suites"][index]["published_seed_decimal"] = str(
                        suite.seed ^ (1 << 48)
                    )
                    return validate_protocol_document(forged)

                reject("reject-truncated-full-width-seed-" + suite.name,
                       poison_seed)

        for family_index, family_name in enumerate(FAMILIES):
            spec = family_spec(family_name)
            for source_index, (relative, _, _) in enumerate(spec.source_owners):
                for field, forged_value in (
                    ("sha256", "f" * 64),
                    ("size_bytes", 0),
                    ("relative", "candidates/borrowed_foreign_engine.c"),
                ):
                    def poison_owner(index: int = family_index,
                                     owner: int = source_index,
                                     key: str = field,
                                     value: Any = forged_value) -> Any:
                        forged = copy.deepcopy(contract)
                        forged["families"][index]["sources"][owner][key] = value
                        return validate_protocol_document(forged)

                    reject("reject-" + family_name + "-source-"
                           + str(source_index) + "-" + field,
                           poison_owner)
            for field in ("module", "adapter_relative", "bridge_module",
                          "engine_relative", "bridge_relative"):
                def poison_route(index: int = family_index,
                                 key: str = field) -> Any:
                    forged = copy.deepcopy(contract)
                    forged["families"][index][key] = "candidates.foreign_matcher"
                    return validate_protocol_document(forged)

                reject("reject-cross-family-" + family_name + "-" + field,
                       poison_route)
            def poison_combined(index: int = family_index) -> Any:
                forged = copy.deepcopy(contract)
                forged["families"][index][
                    "combined_native_engine_and_bridge"
                ] = not forged["families"][index][
                    "combined_native_engine_and_bridge"
                ]
                return validate_protocol_document(forged)

            reject("reject-forged-combined-native-" + family_name,
                   poison_combined)

        for name in ("rust", "c", "zig", "cpp"):
            authentic = synthetic_activation(name)
            for field, forged_value in (
                ("build_version", 5),
                ("activation_version", 4),
                ("build_status", "FAIL"),
                ("activation_status", "FAIL"),
                ("phase_count", 1),
                ("actual_source_build", False),
                ("actual_reversible_activation", False),
                ("source_owner_count", 0),
                ("candidate_qualified", True),
            ):
                def poison_activation(key: str = field,
                                      value: Any = forged_value,
                                      actual: dict[str, Any] = authentic) -> Any:
                    forged = dict(actual)
                    forged[key] = value
                    return validate_synthetic_activation(forged)

                reject("reject-" + name + "-activation-" + field,
                       poison_activation)

        for name in ("go", "fortran"):
            reject("reject-fabricated-v5-activation-" + name,
                   lambda family=name: synthetic_activation(family))
        for key, changed in (
            ("counted_case_count", 127),
            ("actual_case_interpreter_exec_calls", 385),
            ("actual_initialization_interpreter_exec_calls", 3),
            ("actual_guard_cleanup_interpreter_exec_calls", 4),
            ("actual_interpreters_created", 3),
            ("actual_interpreters_destroyed", 3),
            ("actual_fresh_temporary_interpreters", 7),
            ("projected_reference_records_sha256", "0" * 64),
            ("source_sha256", "f" * 64),
        ):
            def poison_lifecycle(field: str = key,
                                 value: Any = changed) -> Any:
                forged = copy.deepcopy(lifecycle)
                forged[field] = value
                return validate_successful_nested_lifecycle(forged)

            reject("reject-fabricated-nested-lifecycle-" + key,
                   poison_lifecycle)

        for row_index, row in enumerate(contract["historical_evidence"]["source_builds"]):
            for field in ("status", "archive_sha256", "receipt_sha256",
                          "actual_process_count", "completed_phase_count"):
                def poison_history(index: int = row_index,
                                   key: str = field) -> Any:
                    forged = copy.deepcopy(contract)
                    target = forged["historical_evidence"]["source_builds"][index]
                    target[key] = "PASS" if key == "status" else (
                        "0" * 64 if key.endswith("sha256") else -1
                    )
                    return validate_protocol_document(forged)

                reject("reject-actual-v5-" + row["family"] + "-" + field,
                       poison_history)

        for key in ("total_distinct_evidence_owner_count",
                    "frozen_v7_candidate_evidence_owner_count",
                    "frozen_v4_source_build_evidence_owner_count",
                    "frozen_v5_source_build_evidence_owner_count"):
            def poison_denominator(field: str = key) -> Any:
                forged = copy.deepcopy(contract)
                forged["historical_evidence"][field] += 1
                return validate_protocol_document(forged)

            reject("reject-changed-genuine-evidence-denominator-" + key,
                   poison_denominator)

        for name, callback in (
            ("actual-source-file-read", lambda: os.open(str(ROOT / SOURCE_RELATIVE), os.O_RDONLY)),
            ("actual-builtin-file-read", lambda: builtins.open(str(ROOT / SOURCE_RELATIVE), "rb")),
            ("actual-subprocess", lambda: subprocess.Popen(["/usr/bin/true"])),
            ("actual-reference-process", lambda: subprocess.run([PINNED_PYTHON, "-V"])),
            ("actual-native-promotion", lambda: os.replace("six-source-a", "six-source-b")),
            ("actual-real-thread", lambda: threading.Thread(target=lambda: None).start()),
            ("actual-real-case-pipe", lambda: os.pipe()),
            ("actual-performance-clock", lambda: time.perf_counter()),
            ("actual-monotonic-clock", lambda: time.monotonic()),
            ("actual-network", lambda: socket.create_connection(("127.0.0.1", 1))),
            ("actual-temporary-root", lambda: tempfile.mkdtemp()),
            ("actual-candidate-import", lambda: importlib.import_module("candidates.cpp_candidate")),
            ("actual-reference-import", lambda: importlib.import_module("re")),
        ):
            reject("reject-" + name, callback)
        reject("reject-bool-as-genuine-case-count",
               lambda: validate_synthetic_observation({
                   **synthetic_observation(SUITES[0], FAMILIES["rust"]),
                   "case_count": True,
               }))
        reject("reject-guessed-candidate-qualification",
               lambda: validate_synthetic_observation({
                   **synthetic_observation(SUITES[0], FAMILIES["rust"]),
                   "candidate_qualified": True,
               }))
        reject("reject-premature-performance-measurement",
               lambda: validate_synthetic_observation({
                   **synthetic_observation(SUITES[0], FAMILIES["rust"]),
                   "performance": "1.5x",
               }))
        reject("reject-hidden-holdout-read",
               lambda: validate_synthetic_observation({
                   **synthetic_observation(SUITES[0], FAMILIES["rust"]),
                   "hidden_cases_read": 1,
               }))
        reject("reject-opened-final-holdout",
               lambda: validate_synthetic_observation({
                   **synthetic_observation(SUITES[0], FAMILIES["rust"]),
                   "holdout": "OPENED",
               }))

        for family_name in FAMILIES:
            selected, synthetic_module, synthetic_bridge = (
                synthetic_owned_public_types(family_name)
            )
            accept("accept-exact-source-backed-public-type-ownership-" + family_name,
                   validate_public_type_ownership(
                       selected, synthetic_module, synthetic_bridge,
                   ) == (synthetic_module.Pattern, synthetic_module.Match))

            def reject_replaced_public_pattern(name: str = family_name) -> Any:
                chosen, module, bridge = synthetic_owned_public_types(name)
                module.Pattern = module.Match
                return validate_public_type_ownership(chosen, module, bridge)

            reject("reject-replaced-or-aliased-public-pattern-" + family_name,
                   reject_replaced_public_pattern)

            def reject_foreign_public_name(name: str = family_name) -> Any:
                chosen, module, bridge = synthetic_owned_public_types(name)
                module.Pattern.__module__ = "external_regex"
                return validate_public_type_ownership(chosen, module, bridge)

            reject("reject-foreign-public-pattern-owner-" + family_name,
                   reject_foreign_public_name)

            def reject_forged_profile(name: str = family_name) -> Any:
                forged = copy.deepcopy(contract)
                forged["native_bridge_profiles"][name][
                    "required_extension_owned_builtins"
                ][0] = "external_regex"
                return validate_protocol_document(forged)

            reject("reject-substituted-native-bridge-profile-" + family_name,
                   reject_forged_profile)

        for family_name in ("rust", "c", "zig"):
            def reject_foreign_native_match(name: str = family_name) -> Any:
                selected, module, bridge = synthetic_owned_public_types(name)
                bridge.Match = type("Match", (), {"__module__": "re"})
                return validate_public_type_ownership(selected, module, bridge)

            reject("reject-substituted-native-Match-owner-" + family_name,
                   reject_foreign_native_match)

        def reject_borrowed_c_pattern_base() -> Any:
            selected, module, bridge = synthetic_owned_public_types("c")
            foreign_base = type("Pattern", (), {"__module__": "re"})
            module.Pattern = type("Pattern", (foreign_base,),
                                  {"__module__": "re"})
            return validate_public_type_ownership(selected, module, bridge)

        reject("reject-C-Pattern-with-borrowed-native-base",
               reject_borrowed_c_pattern_base)

        def reject_invented_go_init() -> Any:
            selected, module, bridge = synthetic_owned_public_types("go")

            def invented(self: Any) -> None:
                del self

            invented.__module__ = selected.module
            module.Pattern.__init__ = invented
            return validate_public_type_ownership(selected, module, bridge)

        reject("reject-invented-Go-init-in-place-of-owned-create",
               reject_invented_go_init)

        def reject_missing_go_create() -> Any:
            selected, module, bridge = synthetic_owned_public_types("go")
            del module.Match._create
            return validate_public_type_ownership(selected, module, bridge)

        reject("reject-missing-owned-Go-Match-create", reject_missing_go_create)
        accept("accept-real-module-bound-native-builtins-only",
               validate_native_bridge_profile(
                   sys, ("getrecursionlimit", "getsizeof"),
               ) is sys)

        foreign_bridge = types.ModuleType("candidates.synthetic_foreign")
        foreign_bridge.compile = builtins.len
        reject("reject-native-builtin-bound-to-a-different-module",
               lambda: validate_native_bridge_profile(
                   foreign_bridge, ("compile",),
               ))
        foreign_bridge.compile = lambda value: value
        reject("reject-Python-wrapper-pretending-to-be-native-builtin",
               lambda: validate_native_bridge_profile(
                   foreign_bridge, ("compile",),
               ))
        reject("reject-duplicate-native-bridge-methods",
               lambda: validate_native_bridge_profile(
                   sys, ("getsizeof", "getsizeof"),
               ))
        reject("reject-missing-source-backed-native-bridge-method",
               lambda: validate_native_bridge_profile(
                   sys, ("not_a_real_owned_native_builtin",),
               ))

        for field, replacement in (
            ("recorder_sha256", "0" * 64),
            ("archive_sha256", "1" * 64),
            ("receipt_sha256", "2" * 64),
            ("records_sha256", "3" * 64),
            ("uncompressed_sha256", "4" * 64),
            ("uncompressed_size_bytes", PUBLIC_BASELINE_UNCOMPRESSED_BYTES - 1),
            ("archive_size_bytes", PUBLIC_BASELINE_ARCHIVE_BYTES - 1),
            ("receipt_size_bytes", PUBLIC_BASELINE_RECEIPT_BYTES - 1),
            ("case_count", 6911),
            ("reference_pids", [82, 82]),
            ("new_reference_processes_started", 1),
            ("candidate_family_selected_by_baseline", True),
            ("source_owned_validators", ["extract_role_record"]),
        ):
            def poison_saved_reference(
                key: str = field, value: Any = replacement,
            ) -> Any:
                forged = copy.deepcopy(contract)
                forged["frozen_public_type_reference"][key] = value
                return validate_protocol_document(forged)

            reject("reject-forged-signed-public-reference-" + field,
                   poison_saved_reference)
        for index in (0, 1):
            for field in ("sha256", "size_bytes"):
                def poison_reference_stdout(
                    role: int = index, key: str = field,
                ) -> Any:
                    forged = copy.deepcopy(contract)
                    forged["frozen_public_type_reference"][
                        "reference_stdout"
                    ][role][key] = "0" * 64 if key == "sha256" else 0
                    return validate_protocol_document(forged)

                reject("reject-truncated-public-reference-"
                       + str(index) + "-" + field, poison_reference_stdout)
        for role in ("source", "inputs", "summary", "svg"):
            for field, changed in (
                ("sha256", "0" * 64),
                ("relative", "docs/evidence/foreign-unfrozen.json"),
                ("size_bytes", 0),
            ):
                def poison_v21_owner(
                    name: str = role, key: str = field,
                    value: Any = changed,
                ) -> Any:
                    forged = copy.deepcopy(contract)
                    forged["frozen_v21_history"]["owners"][name][key] = value
                    return validate_protocol_document(forged)

                reject("reject-replaced-V21-" + role + "-" + field,
                       poison_v21_owner)
        for key, changed in (
            ("total_distinct_evidence_owner_count", 102),
            ("total_authenticated_reference_path_count", 107),
            ("new_repaired_c_campaign_evidence_owner_count", 29),
            ("actual_repaired_c_infrastructure_failure_count", 12),
            ("actual_repaired_c_verified_passing_case_count", 1),
        ):
            def poison_complete_history(
                field: str = key, value: Any = changed,
            ) -> Any:
                forged = copy.deepcopy(contract)
                forged["historical_evidence"][field] = value
                return validate_protocol_document(forged)

            reject("reject-changed-full-V21-history-" + key,
                   poison_complete_history)
        reject("reject-duplicate-canonical-evidence-fields",
               lambda: decode_document(b'{"owner":1,"owner":2}',
                                       "duplicated source evidence"))
        reject("reject-nonfinite-canonical-evidence",
               lambda: decode_document(b'{"owner":NaN}',
                                       "nonfinite source evidence"))
        reject("reject-noncanonical-signed-evidence",
               lambda: decode_document(b'{ "owner": 1 }',
                                       "noncanonical source evidence",
                                       canonical_required=True))
        c_pins = {
            "source": OWNED_SOURCES["c"][0][1],
            "native_engine": RESTORED_C_NATIVE_SHA256,
            "native_bridge": RESTORED_C_NATIVE_SHA256,
        }
        c_sources = {relative: value
                     for relative, value, _ in OWNED_SOURCES["c"]}
        bootstrap = interpreter_bootstrap_source(
            FAMILIES["c"], c_pins, c_sources,
            owner="A", producer_sha256="a" * 64,
        )
        accept("bootstrap-genuine-V3-in-every-nested-subinterpreter",
               "tools.run_owned_six_family_original_p0_producer_v3" in bootstrap
               and str(ROOT / SOURCE_RELATIVE) in bootstrap
               and "run_owned_six_family_original_p0_producer_v1" not in bootstrap
               and "a" * 64 in bootstrap)
        reject("reject-invented-nested-interpreter-owner",
               lambda: interpreter_bootstrap_source(
                   FAMILIES["c"], c_pins, c_sources,
                   owner="foreign", producer_sha256="a" * 64,
               ))
        reject("reject-truncated-nested-V3-producer-source-pin",
               lambda: interpreter_bootstrap_source(
                   FAMILIES["c"], c_pins, c_sources,
                   owner="A", producer_sha256="a" * 63,
               ))
        effects = dict(boundary.counts)
    for name in ("actual_candidate_workers", "actual_candidate_imports",
                 "actual_reference_workers", "actual_source_builds",
                 "actual_native_activations", "actual_native_promotions",
                 "actual_interpreters_created", "actual_threads_started",
                 "actual_subprocesses_started", "actual_native_libraries_loaded",
                 "actual_network_requests", "actual_file_reads",
                 "actual_file_writes", "hidden_cases_read",
                 "benchmark_files_read", "clock_samples", "timing_trials_run"):
        require(effects[name] == 0,
                "a synthetic six-family test performed a real effect: " + name)
    require(len(rejected) >= 200 and len(accepted) >= 90,
            "freeze broad independent hostile and positive original source controls")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS", "synthetic": True,
        "accepted_count": len(accepted), "rejected_count": len(rejected),
        "accepted": accepted, "rejected": rejected,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_DENOMINATOR,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_family_count": 6, "source_owner_count": 25,
        "historically_runnable_p0_family_count": 3,
        "qualified_candidate_count": 0,
        "total_distinct_historical_evidence_owner_count": (
            PRESERVED_EVIDENCE_OWNER_COUNT
        ),
        "total_authenticated_historical_reference_path_count": (
            PRESERVED_REFERENCE_PATH_COUNT
        ),
        "new_repaired_c_campaign_evidence_owner_count": (
            PRESERVED_NEW_CAMPAIGN_OWNER_COUNT
        ),
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "actual_native_promotions": 0,
        "actual_interpreters_created": 0,
        "actual_threads_started": 0,
        "actual_subprocesses_started": 0,
        "source_only_effects": effects,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
        "frozen_contract": protocol_document(),
    }


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    if arguments is None:
        arguments = sys.argv[1:]
    require(isinstance(arguments, (list, tuple))
            and all(type(item) is str for item in arguments),
            "require one explicit exact six-family producer command")
    flags = [item for item in arguments if item.startswith("--")]
    for flag in set(flags):
        require(flag == "--owned-source-sha256" or flags.count(flag) == 1,
                "reject a duplicated or ambiguous actual candidate authorization")
    parser = argparse.ArgumentParser(
        description="Run the unchanged frozen Python regex cases on one owned engine.",
        allow_abbrev=False,
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--emit-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--family", choices=tuple(FAMILIES))
    parser.add_argument("--suite", choices=tuple(item.name for item in SUITES))
    parser.add_argument("--label")
    parser.add_argument("--build-version", choices=("2", "3", "4", "5", "8"))
    parser.add_argument("--build-label")
    parser.add_argument("--activation-root")
    parser.add_argument("--owned-source-sha256", action="append", default=[])
    for name in ("source", "protocol", "document", "build-source",
                 "build-protocol", "build-contract", "build-archive",
                 "build-receipt", "activation-source", "activation-protocol",
                 "activation-contract", "activation-report", "activation-receipt",
                 "recovery-journal", "candidate-source", "native-engine",
                 "native-bridge"):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(list(arguments))
    digest_names = (
        "source_sha256", "protocol_sha256", "document_sha256",
        "build_source_sha256", "build_protocol_sha256",
        "build_contract_sha256", "build_archive_sha256",
        "build_receipt_sha256", "activation_source_sha256",
        "activation_protocol_sha256", "activation_contract_sha256",
        "activation_report_sha256", "activation_receipt_sha256",
        "recovery_journal_sha256", "candidate_source_sha256",
        "native_engine_sha256", "native_bridge_sha256",
    )
    if options.self_test or options.emit_contract:
        require(not any(getattr(options, name) is not None for name in (
            "family", "suite", "label", "build_version", "build_label",
            "activation_root", *digest_names,
        )) and not options.owned_source_sha256,
                "source-only verification cannot authorize a source, candidate, or activation")
        return options
    for name in digest_names:
        value = getattr(options, name)
        if value is not None:
            checked_digest(value, name)
    require(all(getattr(options, name) is not None for name in (
        "source_sha256", "protocol_sha256", "document_sha256",
    )), "independently pin all three exact committed six-family producer owners")
    if options.verify_frozen_context:
        require(not any(getattr(options, name) is not None for name in (
            "family", "suite", "label", "build_version", "build_label",
            "activation_root", "build_source_sha256", "build_protocol_sha256",
            "build_contract_sha256", "build_archive_sha256",
            "build_receipt_sha256", "activation_source_sha256",
            "activation_protocol_sha256", "activation_contract_sha256",
            "activation_report_sha256", "activation_receipt_sha256",
            "recovery_journal_sha256", "candidate_source_sha256",
            "native_engine_sha256", "native_bridge_sha256",
        )) and not options.owned_source_sha256,
                "a read-only context cannot select, activate, or run a candidate")
        return options
    required = (
        "family", "suite", "label", "build_version", "build_label",
        "activation_root", "build_source_sha256", "build_protocol_sha256",
        "build_archive_sha256", "build_receipt_sha256",
        "activation_source_sha256", "activation_protocol_sha256",
        "activation_report_sha256", "activation_receipt_sha256",
        "candidate_source_sha256", "native_engine_sha256",
        "native_bridge_sha256",
    )
    require(all(getattr(options, name) is not None for name in required)
            and bool(options.owned_source_sha256),
            "require actual separately verified build, reversible activation, and all source owners")
    spec = family_spec(options.family)
    suite_spec(options.suite)
    checked_label(options.label)
    checked_label(options.build_label, "build label")
    require(options.build_version != "5",
            "a V5 source build has no published V5-aware reversible activator; fail closed")
    parse_source_owners(spec, options.owned_source_sha256)
    native_pins(spec, options)
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        options = parse_arguments(arguments)
        if options.emit_contract:
            verify_runtime()
            with EffectBoundary(source_only=True) as boundary:
                contract = protocol_document()
                require(validate_protocol_document(contract) is contract,
                        "emit only the exact source-only V3 canonical contract")
                raw = canonical(contract)
                actual = dict(boundary.counts)
            require(all(actual[name] == 0 for name in (
                "actual_candidate_workers", "actual_candidate_imports",
                "actual_reference_workers", "actual_source_builds",
                "actual_native_activations", "actual_native_promotions",
                "actual_interpreters_created", "actual_threads_started",
                "actual_subprocesses_started", "actual_native_libraries_loaded",
                "actual_network_requests", "actual_file_reads",
                "actual_file_writes", "hidden_cases_read",
                "benchmark_files_read", "clock_samples", "timing_trials_run",
            )), "canonical V3 source-only emission attempted a real effect")
            sys.stdout.buffer.write(raw)
            sys.stdout.buffer.flush()
            return 0
        if options.self_test:
            result = self_test()
        elif options.verify_frozen_context:
            result = verify_frozen_context(options)
        else:
            result = run_actual_suite(options)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except BaseException as error:
        failure: dict[str, Any] = {
            "schema": SCHEMA + "-entry-failure", "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error_message": str(error),
            "actual_candidate_workers": 0,
            "actual_reference_workers": 0,
            "actual_source_builds": 0,
            "actual_native_activations": 0,
            "actual_native_promotions": 0,
            "actual_interpreters_created": 0,
            "actual_threads_started": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        details = getattr(error, "details", None)
        if type(details) is dict:
            failure["actual_failure"] = details
            failure["actual_candidate_workers"] = details.get(
                "actual_candidate_workers", 0,
            )
        try:
            sys.stdout.buffer.write(canonical(failure))
            sys.stdout.buffer.flush()
        except (OSError, ValueError, TypeError):
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
