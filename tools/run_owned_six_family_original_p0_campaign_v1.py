#!/usr/bin/env python3
"""Freeze and, only on explicit request, run all original P0 candidate suites.

Self-test is exclusively in-memory. Frozen-context verification is read-only.
Neither mode activates, builds, imports or runs a candidate, starts a process,
samples a clock, reads benchmark data, or opens the holdout. An explicit run
alone may activate one genuinely built C++ or Go family, invoke all thirteen
unchanged producer suites in distinct isolated Python processes, restore every
original native owner, and durably publish the complete pass or failure.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import copy
import gzip
import hashlib
import importlib
import importlib.util
import io
import json
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
from typing import Any, Sequence
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_owned_six_family_original_p0_campaign_v1.py"
PROTOCOL_RELATIVE = "oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V1.md"
DOCUMENT_RELATIVE = "oracle/phase2/six-family-p0-campaign-v1.json"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-owned-six-family-original-p0-campaign-v1"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PHASE1_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
PRODUCER_RELATIVE = "tools/run_owned_six_family_original_p0_producer_v2.py"
PRODUCER_SHA256 = "fe6e82306852517580dcb90f289c643a55db8c01421230a4d7d05d6df365f9c1"
PRODUCER_BYTES = 69637
PRODUCER_PROTOCOL_RELATIVE = "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V2.md"
PRODUCER_PROTOCOL_SHA256 = "3add264a113550d141379229a333d19e375f66429c2b7eb47dc3193a67f7b598"
PRODUCER_PROTOCOL_BYTES = 4092
PRODUCER_DOCUMENT_RELATIVE = "oracle/phase2/six-family-p0-producer-v2.json"
PRODUCER_DOCUMENT_SHA256 = "a210e9cac8d06b47cfc745019e4f4ab3a0c465ff63a38add0bc2b83b1cd986e3"
PRODUCER_DOCUMENT_BYTES = 23966
V4_RELATIVE = "tools/activate_verified_native_candidate_v4.py"
V4_SHA256 = "f22106dab1e4a2f66178cdda66388c12dda83ad09254b045b447759615bf5cd7"
V4_BYTES = 308110
V4_PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V4.md"
V4_PROTOCOL_SHA256 = "3b4d463103380e30b7eb324598b4d39edb66e29f6ad483f7783cf51e4456621d"
V4_PROTOCOL_BYTES = 7757
V4_DOCUMENT_RELATIVE = "oracle/phase2/verified-native-activation-v4.json"
V4_DOCUMENT_SHA256 = "b1ba6cccfea423f562056e1813c8fe6c1e0ef24c2beabb099809dd1669982cf5"
V4_DOCUMENT_BYTES = 26819
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_SUITE_STDOUT_BYTES = 64 * 1024 * 1024
MAX_SUITE_STDERR_BYTES = 4 * 1024 * 1024
MAX_REPORT_BYTES = 256 * 1024 * 1024
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
SUITE_TIMEOUT_SECONDS = 3600
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"


class CampaignError(Exception):
    """An original suite, real owner, or recoverable campaign is unproven."""


class CampaignExecutionFailure(CampaignError):
    """Preserve real partial activation, worker, and recovery evidence."""

    def __init__(self, message: str, details: dict[str, Any]) -> None:
        super().__init__(message)
        self.details = details


class SourceOnlyViolation(CampaignError):
    """Source-only controls attempted an actual external effect."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise CampaignError(message)


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require one complete lowercase SHA-256: " + label)
    return value


def checked_label(value: Any, label: str = "campaign label") -> str:
    require(type(value) is str and 0 < len(value.encode("utf-8")) <= 48
            and all(item in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
                    for item in value),
            "require one bounded first-party ASCII " + label)
    return value


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           separators=(",", ":"), sort_keys=True)
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise CampaignError("preserve exact finite, surrogate-safe canonical JSON") from error


def zero_effects() -> dict[str, Any]:
    return {
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "actual_native_promotions": 0,
        "actual_interpreters_created": 0,
        "actual_threads_started": 0,
        "actual_subprocesses_started": 0,
        "actual_network_requests": 0,
        "actual_file_reads": 0,
        "actual_file_writes": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_qualified_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


SUITES = (
    ("original_bounded_v5", 151, "tools/independent_original_cpython_suite_v5.py", "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce", "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240", "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276", None, "unchanged-165-method-upstream-source"),
    ("public_v3", 864, "tools/rust_public_practice_benchmark_v1.py", "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37", "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e", "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c", 5928217332825411633, "unchanged-public-source-evaluator"),
    ("scanner_v3", 1024, "tools/rust_scanner_differential_v1.py", "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7", "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c", "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d", 5999710933164053041, "unchanged-scanner-and-callback-evaluator"),
    ("buffer_v3", 768, "tools/rust_memoryview_expand_differential_v1.py", "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6", "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60", "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75", 5567953616029762609, "unchanged-memoryview-evaluator"),
    ("managed_v1", 1024, "tools/independent_managed_buffer_lifetime_v1.py", "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489", "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976", "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df", 5567095966978627121, "unchanged-real-buffer-lifetime-evaluator"),
    ("scanner_verbose_v1", 2854, "tools/independent_scanner_verbose_comments_v1.py", "5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d", "01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b", "d7e2d499eb4dbe6ae0f8743d8b152e4835898656daa8b3167598636ef7be6012", 5999725261024810545, "unchanged-verbose-tokenizer-evaluator"),
    ("public_types_v1", 6912, "tools/independent_public_type_identity_serialization_v1.py", "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20", "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123", "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21", 6077977430793212465, "unchanged-public-type-and-pickle-evaluator"),
    ("substitution_v2", 5120, "tools/independent_substitution_buffer_semantics_v2.py", "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573", "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54", "2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b", 6004778603531028017, "unchanged-substitution-and-callback-evaluator"),
    ("shape_v2", 10240, "tools/independent_shape_changing_buffer_semantics_v2.py", "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c", "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8", "58bbc78828ba2d4cde6b99cbebea815ce9381cda24d0acec03f6cc095b8b643c", 6001118316486346290, "unchanged-real-changing-buffer-evaluator"),
    ("public_surface_v19", 1376, "tools/python_re_public_surface_oracle_stage19.py", "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e", "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa", "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef", 2026072483, "unchanged-real-64-locale-and-192-transition-evaluator"),
    ("subinterpreter_v2", 128, "tools/python_re_subinterpreter_oracle_v2.py", "54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8", "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3", "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8", 2026072501, "unchanged-real-128-case-394-call-11-interpreter-lifecycle"),
    ("pep688_v4", 264, "tools/python_re_buffer_exporter_oracle_v4.py", "8da0b8e5c5519e7335cd1b53ceb7042f1da1f902c486ad8ac35ddf53d8a04490", "2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891", "7827586e0c7d4f43ac1fbd288f6b28f6a44b810b46274830d3803505c76692a8", None, "unchanged-real-python-buffer-exporter-evaluator"),
    ("threaded_pattern_v1", 512, "tools/python_re_threaded_pattern_oracle_v1.py", "05226e59736d8721a975eda8afa10247213999690c2766a7b3235c567b9f8276", "a7d467e3e529204946fe00ddb819e734421e7087ea909af9ec24b757e42afa0b", "928ea100d6fdaecc7c1dcf01e32c24fd98a146964c0955989a8149c1216ffe81", 2026072701, "unchanged-real-barrier-synchronized-shared-pattern-threads"),
)

OWNED_SOURCES = {
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
    "c": (
        ("candidates/vm_candidate.py", "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096", 60707),
        ("candidates/_vm_native.c", "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55", 218185),
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

BUILD_PROOFS = {
    "cpp": {
        "version": 4, "label": "phase2-v4",
        "source_sha256": "efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1",
        "protocol_sha256": "e974b26562cc210c175c08cda7914e6b196fdee2ebe2a8232dd87c0cddbc0dfb",
        "contract_sha256": "0b5641529bc49f55b9e56fe397ad38e7e23d6c9b3376587b743753814b8089d7",
        "archive_relative": "oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4.json.gz",
        "archive_sha256": "48910a6328e8aaacdac993b2c029995d878960a456359a14db5c83b9fc518df9",
        "archive_bytes": 20605,
        "receipt_relative": "oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4-publication-receipt.json",
        "receipt_sha256": "7742eda3ce777b1378d0c7fb87fc064f222850ca8bcf15cd23ff8a4d87d8bebf",
        "receipt_bytes": 2074,
        "actual_compiler_process_count": 10,
        "completed_phase_count": 2,
        "candidate_adapter_sha256": "8dcece29b1a194eea023143148af37bb679a9df4c39c01153f5ee23f778e16d5",
        "native_outputs": {
            "bridge": {"sha256": "d444611316caceb4ba08783203bc4f1d396a8987f63a49bd24c81d5d2c532441", "size_bytes": 130744},
        },
        "combined_native_engine_and_bridge": True,
        "generated_go_header_promoted": False,
    },
    "go": {
        "version": 6, "label": "phase2-v6",
        "source_sha256": "2af9da3cb37a55782f3bfb8bdbdfdb7a945532994a5c988f4645d888dbe57ebc",
        "protocol_sha256": "108dbd52144c78530221e36882a0070fe9805b1bef6a136caf4636148ae9131d",
        "contract_sha256": "0121aaa5902b449e107396d6a1107ca8fe0fefebb0a0f09eb58d2d19c8888db4",
        "archive_relative": "oracle/phase2/evidence/native-source-build-v6-go-phase2-v6.json.gz",
        "archive_sha256": "05c24a5fff228d8eab8bec961d825b0e65504072e11e8c574ec580d9f3e6e245",
        "archive_bytes": 37619,
        "receipt_relative": "oracle/phase2/evidence/native-source-build-v6-go-phase2-v6-publication-receipt.json",
        "receipt_sha256": "f3adcb20bb591946600e1e2b1db037fb3b4828c3d4a628a0347cfed40f262fca",
        "receipt_bytes": 3262,
        "actual_compiler_process_count": 26,
        "completed_phase_count": 2,
        "candidate_adapter_sha256": "816d21527b9806afbc9457122f72f8f6b62c39b8b791d3f363745d412cbe3d20",
        "native_outputs": {
            "engine": {"sha256": "38ab223b8ef88340a7be86f2195c417ee7d2dd9deead48cc6495a5b4e3c31b27", "size_bytes": 2712912},
            "bridge": {"sha256": "dd71ab6cb15a98e1a07c38965cdb178da0dbba2a26db937975e0d6435a2a5d0c", "size_bytes": 41904},
            "generated_header": {"sha256": "481ebb65cc587749677ce28abeb4f3de111e2f87a18ac547ff0157fce85d2c23", "size_bytes": 3086},
        },
        "combined_native_engine_and_bridge": False,
        "generated_go_header_promoted": False,
    },
}


def suite_protocol(row: tuple[Any, ...]) -> dict[str, Any]:
    name, count, source_path, source_sha, matrix, reference, seed, route = row
    return {
        "id": name, "case_execution_count": count,
        "source_relative": source_path, "source_sha256": source_sha,
        "matrix_sha256": matrix, "reference_records_sha256": reference,
        "published_seed_decimal": None if seed is None else str(seed),
        "unchanged_original_producer_route": route,
    }


def protocol_document() -> dict[str, Any]:
    suites = [suite_protocol(row) for row in SUITES]
    families = [{
        "family": family,
        "owned_source_count": len(owners),
        "sources": [{"relative": path, "sha256": digest, "size_bytes": size}
                    for path, digest, size in owners],
        "actual_v4_campaign_supported": family in BUILD_PROOFS,
    } for family, owners in OWNED_SOURCES.items()]
    paths = [owner["relative"] for family in families for owner in family["sources"]]
    require(len(suites) == 13 and sum(row["case_execution_count"] for row in suites) == 31237
            and len({row["id"] for row in suites}) == 13
            and len(families) == 6 and len(paths) == len(set(paths)) == 25,
            "preserve all original suites and all six disjoint first-party source families")
    return {
        "schema": SCHEMA + "-source-freeze", "version": 1,
        "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; NO CAMPAIGN OR CANDIDATE RUN",
        "goal_sha256": GOAL_SHA256,
        "pinned_cpython": {"path": PINNED_PYTHON,
                           "sha256": PINNED_PYTHON_SHA256, "version": "3.14.6"},
        "phase_one": {
            "inventory_relative": PHASE1_RELATIVE,
            "inventory_sha256": PHASE1_SHA256,
            "suite_count": 13, "case_execution_denominator": 31237,
            "named_private_waiver_count": 13,
            "original_public_record_count": 152,
            "original_real_debug_skip_count": 1,
            "supplemental_cases_added": False,
        },
        "frozen_original_producer": {
            "source_relative": PRODUCER_RELATIVE,
            "source_sha256": PRODUCER_SHA256,
            "source_bytes": PRODUCER_BYTES,
            "protocol_relative": PRODUCER_PROTOCOL_RELATIVE,
            "protocol_sha256": PRODUCER_PROTOCOL_SHA256,
            "protocol_bytes": PRODUCER_PROTOCOL_BYTES,
            "document_relative": PRODUCER_DOCUMENT_RELATIVE,
            "document_sha256": PRODUCER_DOCUMENT_SHA256,
            "document_bytes": PRODUCER_DOCUMENT_BYTES,
            "actual_suite_schema": "rebar-owned-six-family-original-p0-producer-v1-actual-original-suite",
            "actual_failure_schema": "rebar-owned-six-family-original-p0-producer-v2-entry-failure",
        },
        "frozen_v4_activation": {
            "source_relative": V4_RELATIVE, "source_sha256": V4_SHA256,
            "source_bytes": V4_BYTES,
            "protocol_relative": V4_PROTOCOL_RELATIVE,
            "protocol_sha256": V4_PROTOCOL_SHA256,
            "protocol_bytes": V4_PROTOCOL_BYTES,
            "document_relative": V4_DOCUMENT_RELATIVE,
            "document_sha256": V4_DOCUMENT_SHA256,
            "document_bytes": V4_DOCUMENT_BYTES,
            "activation_version": 4,
            "promotion_group_atomic": False,
        },
        "suite_count": 13, "case_execution_denominator": 31237,
        "suites": suites,
        "family_count": 6, "source_owner_count": 25,
        "pairwise_shared_semantic_source_count": 0,
        "families": families,
        "supported_actual_campaign_families": ["cpp", "go"],
        "supported_actual_campaign_family_count": 2,
        "historically_runnable_original_families": ["c", "rust", "zig"],
        "historically_runnable_original_family_count": 3,
        "independently_source_built_family_count": 5,
        "actual_build_proofs": copy.deepcopy(BUILD_PROOFS),
        "historical_evidence": {
            "candidate_owner_count": 51,
            "v4_build_owner_count": 6,
            "v5_build_owner_count": 4,
            "v6_build_owner_count": 4,
            "total_distinct_evidence_owner_count": 65,
            "historical_build_process_ledger": {
                "v2_process_count": 39,
                "v3_zig_process_count": 15,
                "v4_process_count": 32,
                "v4_processes_by_family": {"cpp": 10, "go": 4, "fortran": 18},
                "v5_process_count": 31,
                "v5_processes_by_family": {"go": 5, "fortran": 26},
                "v6_process_count": 52,
                "v6_processes_by_family": {"go": 26, "fortran": 26},
                "v2_and_v4_process_count": 71,
                "v2_v4_v5_process_count": 102,
                "v2_v4_v5_v6_process_count": 154,
                "all_historical_build_process_count": 169,
                "all_historical_versions_actual_compiler_process_count": 169,
                "unique_pid_scope": "WITHIN EACH ACTUAL BUILD REPORT ONLY",
            },
            "historical_failed_zig_case_interpreter_calls": 385,
            "historical_failed_zig_verified_passing_nested_cases": 0,
        },
        "successful_nested_lifecycle": {
            "counted_case_count": 128,
            "actual_case_interpreter_exec_calls": 394,
            "actual_initialization_interpreter_exec_calls": 11,
            "actual_guard_cleanup_interpreter_exec_calls": 11,
            "actual_interpreters_created": 11,
            "actual_interpreters_destroyed": 11,
            "actual_fresh_temporary_interpreters": 8,
            "source_relative": "tools/run_owned_candidate_subinterpreters_v1.py",
            "source_sha256": "45e9b47c7c635fc30ebdb2cb4830d2d1fe382a5a7e4b663fb1a8e0112779e1a7",
            "historical_v3_relative": "tools/run_owned_candidate_subinterpreters_v3.py",
            "historical_v3_sha256": "21febe241549963a2818af2a20782da81bdf952fb7be8affc4289d9ccc9ad5b4",
            "projected_reference_records_sha256": "cf5633c8dc1038d650603eee421371285d0e32f6446190ce728590f1f5c55021",
        },
        "worker_policy": {
            "one_shell_free_isolated_pinned_python_per_suite": True,
            "required_worker_count": 13,
            "run_all_suites_after_any_mismatch_or_crash": True,
            "preserve_every_original_record_and_failure": True,
            "full_raw_stdout_and_stderr_preserved": True,
            "duplicate_json_keys_allowed": False,
            "unicode_surrogates_preserved": True,
            "maximum_suite_stdout_bytes": MAX_SUITE_STDOUT_BYTES,
            "maximum_suite_stderr_bytes": MAX_SUITE_STDERR_BYTES,
            "maximum_suite_timeout_seconds": SUITE_TIMEOUT_SECONDS,
            "semantic_failure_exit_one_is_not_a_crash": True,
        },
        "activation_and_recovery_policy": {
            "activation_only_under_explicit_run": True,
            "activation_directly_uses_pinned_v4": True,
            "require_actual_two_phase_source_build": True,
            "restore_before_publication_in_finally": True,
            "reportless_recovery_after_failed_restore": True,
            "preserve_activation_report_receipt_and_journal": True,
            "require_verified_canonical_original_restoration": True,
            "generated_go_header_promoted": False,
            "promotion_group_atomic": False,
        },
        "publication_policy": {
            "evidence_relative": EVIDENCE_RELATIVE,
            "archive_mode": "0600", "receipt_mode": "0600",
            "exclusive_creation": True, "no_follow": True,
            "separate_archive_and_receipt_inodes": True,
            "same_inode_readback_required": True,
            "archive_file_fsync_required": True,
            "archive_directory_fsync_required": True,
            "receipt_file_fsync_required": True,
            "receipt_directory_fsync_required": True,
            "gzip_mtime": 0, "gzip_compresslevel": 9,
            "maximum_report_bytes": MAX_REPORT_BYTES,
            "maximum_archive_bytes": MAX_ARCHIVE_BYTES,
            "partial_candidate_may_qualify": False,
        },
        "independence_policy": {
            "third_party_regex_allowed": False,
            "python_re_matching_allowed": False,
            "sre_matching_allowed": False,
            "cross_family_engine_allowed": False,
            "wrapper_counted_as_engine": False,
            "fallback_allowed": False,
            "benchmark_detection_allowed": False,
            "preserve_unchanged_v2_matcher_guard": True,
        },
        "verification_effects": zero_effects(),
    }


def validate_protocol_document(value: Any) -> dict[str, Any]:
    require(type(value) is dict and canonical(value) == canonical(protocol_document()),
            "reject altered original suites, families, histories, proofs, or boundaries")
    return value


class EffectBoundary:
    """Prevent source-only or read-only verification from causing effects."""

    def __init__(self, *, source_only: bool) -> None:
        self.source_only = source_only
        self.original: list[tuple[Any, str, Any]] = []
        self.modules: frozenset[str] = frozenset()
        self.blocked = {name: 0 for name in
                        ("file", "process", "clock", "network", "thread",
                         "temporary", "import")}
        self.actual = zero_effects()

    def replace(self, owner: Any, name: str, value: Any) -> None:
        if hasattr(owner, name):
            self.original.append((owner, name, getattr(owner, name)))
            setattr(owner, name, value)

    def deny(self, category: str) -> Any:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            self.blocked[category] += 1
            raise SourceOnlyViolation("frozen verification cannot perform " + category)
        return blocked

    def __enter__(self) -> EffectBoundary:
        self.modules = frozenset(sys.modules)
        for owner, name in ((subprocess, "Popen"), (subprocess, "run"),
                            (subprocess, "call"), (subprocess, "check_call"),
                            (subprocess, "check_output"), (os, "system"),
                            (os, "popen"), (os, "fork"), (os, "posix_spawn"),
                            (os, "posix_spawnp"), (os, "pipe")):
            self.replace(owner, name, self.deny("process"))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns", "sleep"):
            self.replace(time, name, self.deny("clock"))
        self.replace(socket, "socket", self.deny("network"))
        self.replace(socket, "create_connection", self.deny("network"))
        self.replace(threading.Thread, "start", self.deny("thread"))
        self.replace(threading.Barrier, "wait", self.deny("thread"))
        for name in ("mkstemp", "mkdtemp", "TemporaryFile",
                     "NamedTemporaryFile", "TemporaryDirectory"):
            self.replace(tempfile, name, self.deny("temporary"))
        for name in ("replace", "rename", "unlink", "remove", "mkdir",
                     "makedirs", "rmdir", "write", "fsync", "fchmod"):
            self.replace(os, name, self.deny("file"))
        if self.source_only:
            for owner, name in ((builtins, "open"), (io, "open"), (os, "open"),
                                (Path, "open"), (Path, "read_bytes"),
                                (Path, "read_text"), (Path, "write_bytes"),
                                (Path, "write_text")):
                self.replace(owner, name, self.deny("file"))
            self.replace(importlib, "import_module", self.deny("import"))
            self.replace(builtins, "__import__", self.deny("import"))
        else:
            previous = builtins.open

            def readonly_open(path: Any, mode: Any = "r", *args: Any,
                              **kwargs: Any) -> Any:
                require(type(mode) is str and not any(char in mode for char in "wax+"),
                        "read-only verification must not mutate any path")
                return previous(path, mode, *args, **kwargs)

            self.replace(builtins, "open", readonly_open)
        return self

    def __exit__(self, error_type: Any, error: Any, tb: Any) -> bool:
        for owner, name, original in reversed(self.original):
            setattr(owner, name, original)
        added = set(sys.modules) - self.modules
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in added),
                "verification imported a real candidate or matching engine")
        if self.source_only:
            require(frozenset(sys.modules) == self.modules,
                    "the source-only campaign imported another module")
        return False


def verify_runtime(*, permit_candidate: bool = False) -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and os.path.realpath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "run only the isolated, pinned, no-bytecode stable CPython 3.14.6")
    if not permit_candidate:
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
                "campaign verification may never import a matching candidate")


def read_owned(relative: str, digest: str, *, maximum: int,
               exact_size: int | None = None,
               owner_only: bool = False) -> tuple[bytes, dict[str, Any]]:
    require(type(relative) is str and bool(relative) and "\x00" not in relative,
            "require one exact first-party relative owner")
    path = Path(relative)
    require(not path.is_absolute() and str(path) == relative
            and all(part not in {"", ".", ".."} for part in path.parts),
            "reject broad, absolute, parent, or ambiguous evidence paths")
    checked_digest(digest, relative)
    target = ROOT / path
    require(os.path.abspath(str(target)) == str(target)
            and os.path.realpath(str(target)) == str(target),
            "reject redirected or symlinked campaign support")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(target), flags)
    try:
        first = os.fstat(descriptor)
        visible = os.stat(str(target), follow_symlinks=False)
        require(stat.S_ISREG(first.st_mode)
                and (first.st_dev, first.st_ino, first.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and 0 < first.st_size <= maximum
                and (exact_size is None or first.st_size == exact_size)
                and (not owner_only or stat.S_IMODE(first.st_mode) == 0o600),
                "reject a substituted, non-private, truncated, or oversized owner")
        remaining = first.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1048576))
            require(type(chunk) is bytes and bool(chunk),
                    "preserve all complete frozen evidence bytes")
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        last = os.fstat(descriptor)
        named = os.stat(str(target), follow_symlinks=False)
        require((first.st_dev, first.st_ino, first.st_size,
                 first.st_mtime_ns, first.st_ctime_ns)
                == (last.st_dev, last.st_ino, last.st_size,
                    last.st_mtime_ns, last.st_ctime_ns)
                and (last.st_dev, last.st_ino, last.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and hashlib.sha256(raw).hexdigest() == digest,
                "reject changed, replaced, or incorrectly hashed campaign evidence")
        return raw, {
            "relative": relative, "sha256": digest, "size_bytes": len(raw),
            "device": last.st_dev, "inode": last.st_ino,
            "mode": stat.S_IMODE(last.st_mode),
        }
    finally:
        os.close(descriptor)


def unique_json(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in rows:
        require(type(key) is str and key not in result,
                "reject repeated original candidate-result keys")
        result[key] = value
    return result


def decode_document(raw: bytes, label: str,
                    *, maximum: int = MAX_REPORT_BYTES) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= maximum,
            "require complete bounded original JSON: " + label)
    try:
        result = json.loads(raw.decode("utf-8", "strict"),
                            object_pairs_hook=unique_json,
                            parse_constant=lambda value: (_ for _ in ()).throw(
                                ValueError("nonfinite candidate evidence: " + value)))
    except (ValueError, UnicodeError, RecursionError) as error:
        raise CampaignError("reject malformed original JSON: " + label) from error
    require(type(result) is dict and canonical(result) == raw,
            "preserve exact surrogate-safe canonical candidate bytes: " + label)
    return result


def frozen_module(relative: str, digest: str, size: int) -> Any:
    _, original = read_owned(relative, digest, maximum=MAX_SOURCE_BYTES,
                             exact_size=size)
    name = "_rebar_owned_original_p0_campaign_frozen_" + digest[:24]
    existing = sys.modules.get(name)
    if existing is None:
        spec = importlib.util.spec_from_file_location(name, str(ROOT / relative))
        require(spec is not None and spec.loader is not None,
                "import only an independently pinned first-party support source")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            sys.modules.pop(name, None)
            raise
    else:
        module = existing
    _, final = read_owned(relative, digest, maximum=MAX_SOURCE_BYTES,
                          exact_size=size)
    require(original["device"] == final["device"]
            and original["inode"] == final["inode"]
            and os.path.abspath(str(getattr(module, "__file__", "")))
            == str(ROOT / relative)
            and os.path.realpath(str(module.__file__)) == str(ROOT / relative),
            "the exact first-party support owner changed during safe import")
    return module


def synthetic_campaign(family: str) -> dict[str, Any]:
    require(family in BUILD_PROOFS,
            "synthetic controls may exercise only real C++/Go source-build proofs")
    rows = []
    for name, count, source_path, source_sha, matrix, reference, seed, route in SUITES:
        rows.append({
            "suite": name, "status": "PASS", "case_execution_denominator": count,
            "source_relative": source_path, "source_sha256": source_sha,
            "matrix_sha256": matrix, "reference_records_sha256": reference,
            "published_seed_decimal": None if seed is None else str(seed),
            "mismatch_count": 0, "all_mismatches": [],
            "process_returncode": 0, "timed_out": False,
            "crashed": False, "actual_worker_started": False,
        })
    return {
        "family": family, "synthetic_only": True, "status": "PASS",
        "suite_count": 13, "case_execution_denominator": 31237,
        "rows": rows, "activation_verified": True,
        "restoration_verified": True,
        "actual_candidate_workers": 0,
        "actual_native_activations": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
        "candidate_qualified": False,
    }


def validate_synthetic_campaign(value: Any) -> dict[str, Any]:
    require(type(value) is dict and type(value.get("family")) is str
            and value["family"] in BUILD_PROOFS
            and value.get("synthetic_only") is True
            and value.get("suite_count") == 13
            and value.get("case_execution_denominator") == 31237
            and value.get("activation_verified") is True
            and value.get("restoration_verified") is True
            and value.get("actual_candidate_workers") == 0
            and value.get("actual_native_activations") == 0
            and value.get("hidden_cases_read") == 0
            and value.get("benchmark_files_read") == 0
            and value.get("clock_samples") == 0
            and value.get("holdout") == "NOT OPENED"
            and value.get("performance") == "NOT MEASURED"
            and value.get("candidate_qualified") is False,
            "reject fake actual workers, promotion, qualification, timing, or holdout")
    rows = value.get("rows")
    require(type(rows) is list and len(rows) == 13,
            "require every original P0 suite exactly once")
    failures = 0
    for observed, frozen in zip(rows, SUITES, strict=True):
        name, count, source_path, source_sha, matrix, reference, seed, _ = frozen
        require(type(observed) is dict and observed.get("suite") == name
                and observed.get("case_execution_denominator") == count
                and observed.get("source_relative") == source_path
                and observed.get("source_sha256") == source_sha
                and observed.get("matrix_sha256") == matrix
                and observed.get("reference_records_sha256") == reference
                and observed.get("published_seed_decimal")
                == (None if seed is None else str(seed))
                and observed.get("status") in {"PASS", "FAIL"}
                and type(observed.get("mismatch_count")) is int
                and observed["mismatch_count"] >= 0
                and type(observed.get("all_mismatches")) is list
                and len(observed["all_mismatches"]) == observed["mismatch_count"]
                and type(observed.get("process_returncode")) is int
                and type(observed.get("timed_out")) is bool
                and type(observed.get("crashed")) is bool
                and observed.get("actual_worker_started") is False,
                "reject omitted, duplicated, reordered, fabricated, or weakened suite " + name)
        failed = (observed["mismatch_count"] > 0 or observed["timed_out"]
                  or observed["crashed"] or observed["process_returncode"] != 0)
        require((observed["status"] == "FAIL") is failed,
                "reject false zero mismatches, hidden timeout, crash, or worker failure")
        failures += failed
    require(value.get("status") == ("FAIL" if failures else "PASS"),
            "never promote a partial or failing synthetic campaign")
    return value


def synthetic_publication() -> dict[str, Any]:
    report = {"schema": SCHEMA + "-synthetic-publication",
              "status": "FAIL", "complete_original_record": "preserve-\ud800",
              "all_mismatches": [{"case": "genuine-loss"}],
              "holdout": "NOT OPENED"}
    plain = canonical(report)
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    return {
        "synthetic_only": True, "candidate_status": "FAIL",
        "report": report, "plain": plain, "gzip": compressed,
        "plain_sha256": hashlib.sha256(plain).hexdigest(),
        "archive_sha256": hashlib.sha256(compressed).hexdigest(),
        "archive": {
            "device": 17, "inode": 101, "mode": 0o600,
            "exclusive_creation": True, "file_fsync_completed": True,
            "same_inode_readback_verified": True,
        },
        "receipt": {
            "status": "PASS", "candidate_status": "FAIL",
            "device": 17, "inode": 102, "mode": 0o600,
            "exclusive_creation": True, "file_fsync_completed": True,
            "same_inode_readback_verified": True,
        },
        "archive_directory_fsync_completed": True,
        "receipt_directory_fsync_completed": True,
    }


def validate_synthetic_publication(value: Any) -> dict[str, Any]:
    require(type(value) is dict and value.get("synthetic_only") is True
            and value.get("candidate_status") == "FAIL"
            and type(value.get("report")) is dict
            and type(value.get("plain")) is bytes
            and type(value.get("gzip")) is bytes
            and value.get("plain") == canonical(value["report"])
            and value["report"].get("complete_original_record")
            == "preserve-\ud800"
            and value["report"].get("all_mismatches") == [{"case": "genuine-loss"}]
            and value["report"].get("holdout") == "NOT OPENED"
            and value.get("plain_sha256")
            == hashlib.sha256(value["plain"]).hexdigest()
            and value.get("archive_sha256")
            == hashlib.sha256(value["gzip"]).hexdigest()
            and value["gzip"]
            == gzip.compress(value["plain"], compresslevel=9, mtime=0),
            "reject fabricated original bytes, lone-surrogate loss, gzip, or hashes")
    inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        recovered = inflater.decompress(value["gzip"], MAX_SOURCE_BYTES + 1)
    except (ValueError, zlib.error) as error:
        raise CampaignError("reject malformed or truncated synthetic gzip") from error
    require(inflater.eof and not inflater.unused_data
            and not inflater.unconsumed_tail and recovered == value["plain"],
            "reject truncated, trailing, concatenated, or bomb-like gzip")
    archive, receipt = value.get("archive"), value.get("receipt")
    require(type(archive) is dict and type(receipt) is dict
            and archive.get("mode") == receipt.get("mode") == 0o600
            and archive.get("device") == receipt.get("device") == 17
            and type(archive.get("inode")) is int
            and type(receipt.get("inode")) is int
            and archive["inode"] != receipt["inode"]
            and all(owner.get("exclusive_creation") is True
                    and owner.get("file_fsync_completed") is True
                    and owner.get("same_inode_readback_verified") is True
                    for owner in (archive, receipt))
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_status") == "FAIL"
            and value.get("archive_directory_fsync_completed") is True
            and value.get("receipt_directory_fsync_completed") is True,
            "reject forged, shared, non-0600, unsynced, or relabelled evidence owners")
    return value


def self_test() -> dict[str, Any]:
    verify_runtime()
    accepted = 0
    rejected = 0
    with EffectBoundary(source_only=True) as boundary:
        frozen = protocol_document()
        validate_protocol_document(frozen)
        accepted += 1

        def reject(item: Any, validator: Any = validate_protocol_document) -> None:
            nonlocal rejected
            try:
                validator(item)
            except (CampaignError, TypeError, ValueError, KeyError):
                rejected += 1
                return
            raise CampaignError("a hostile frozen-campaign control was accepted")

        for index, suite in enumerate(frozen["suites"]):
            for key, original in suite.items():
                attack = copy.deepcopy(frozen)
                attack["suites"][index][key] = (
                    original + 1 if type(original) is int
                    else "0" if original is None else str(original) + "-foreign"
                )
                reject(attack)
            accepted += 1
        for index, family in enumerate(frozen["families"]):
            for key in ("family", "owned_source_count", "actual_v4_campaign_supported"):
                attack = copy.deepcopy(frozen)
                original = attack["families"][index][key]
                attack["families"][index][key] = (
                    not original if type(original) is bool
                    else original + 1 if type(original) is int
                    else original + "-stdlib-regex"
                )
                reject(attack)
            for owner_index, owner in enumerate(family["sources"]):
                for key in ("relative", "sha256", "size_bytes"):
                    attack = copy.deepcopy(frozen)
                    original = attack["families"][index]["sources"][owner_index][key]
                    attack["families"][index]["sources"][owner_index][key] = (
                        original + 1 if type(original) is int else original + "-wrapper"
                    )
                    reject(attack)
            accepted += 1
        for name in ("frozen_original_producer", "frozen_v4_activation",
                     "historical_evidence", "worker_policy",
                     "activation_and_recovery_policy", "publication_policy",
                     "independence_policy", "successful_nested_lifecycle",
                     "phase_one", "verification_effects"):
            for key, original in frozen[name].items():
                attack = copy.deepcopy(frozen)
                attack[name][key] = (
                    not original if type(original) is bool
                    else original + 1 if type(original) is int
                    else original + "-changed" if type(original) is str
                    else {} if type(original) is dict
                    else original[:-1] if type(original) is list
                    else "changed"
                )
                reject(attack)
        for family, proof in frozen["actual_build_proofs"].items():
            for key, original in proof.items():
                attack = copy.deepcopy(frozen)
                attack["actual_build_proofs"][family][key] = (
                    not original if type(original) is bool
                    else original + 1 if type(original) is int
                    else original + "-forged" if type(original) is str
                    else {}
                )
                reject(attack)
            fixture = synthetic_campaign(family)
            validate_synthetic_campaign(fixture)
            accepted += 1
            attacks: list[dict[str, Any]] = []
            omitted = copy.deepcopy(fixture)
            omitted["rows"].pop()
            attacks.append(omitted)
            duplicate = copy.deepcopy(fixture)
            duplicate["rows"][1] = copy.deepcopy(duplicate["rows"][0])
            attacks.append(duplicate)
            reordered = copy.deepcopy(fixture)
            reordered["rows"][0], reordered["rows"][1] = (
                reordered["rows"][1], reordered["rows"][0])
            attacks.append(reordered)
            false_zero = copy.deepcopy(fixture)
            false_zero["rows"][2]["all_mismatches"] = [{"case": "real-loss"}]
            attacks.append(false_zero)
            hidden_crash = copy.deepcopy(fixture)
            hidden_crash["rows"][3]["crashed"] = True
            attacks.append(hidden_crash)
            hidden_timeout = copy.deepcopy(fixture)
            hidden_timeout["rows"][4]["timed_out"] = True
            attacks.append(hidden_timeout)
            hidden_exit = copy.deepcopy(fixture)
            hidden_exit["rows"][5]["process_returncode"] = 1
            attacks.append(hidden_exit)
            wrong_count = copy.deepcopy(fixture)
            wrong_count["rows"][6]["case_execution_denominator"] -= 1
            attacks.append(wrong_count)
            false_restoration = copy.deepcopy(fixture)
            false_restoration["restoration_verified"] = False
            attacks.append(false_restoration)
            false_actual = copy.deepcopy(fixture)
            false_actual["actual_candidate_workers"] = 13
            attacks.append(false_actual)
            holdout = copy.deepcopy(fixture)
            holdout["holdout"] = "OPENED"
            attacks.append(holdout)
            for attack in attacks:
                reject(attack, validate_synthetic_campaign)
            genuine_failure = copy.deepcopy(fixture)
            genuine_failure["rows"][0]["status"] = "FAIL"
            genuine_failure["rows"][0]["mismatch_count"] = 1
            genuine_failure["rows"][0]["all_mismatches"] = [{"case": "preserved"}]
            genuine_failure["status"] = "FAIL"
            validate_synthetic_campaign(genuine_failure)
            require(len(genuine_failure["rows"]) == 13,
                    "retain all later original suites after an actual semantic failure")
            accepted += 1
        publication = synthetic_publication()
        validate_synthetic_publication(publication)
        accepted += 1
        for key in ("plain", "gzip", "plain_sha256", "archive_sha256",
                    "candidate_status", "synthetic_only",
                    "archive_directory_fsync_completed",
                    "receipt_directory_fsync_completed"):
            attack = copy.deepcopy(publication)
            current = attack[key]
            attack[key] = (
                not current if type(current) is bool
                else current + b"forged" if type(current) is bytes
                else current + "-forged"
            )
            reject(attack, validate_synthetic_publication)
        for name in ("archive", "receipt"):
            for key in ("mode", "inode", "exclusive_creation",
                        "file_fsync_completed", "same_inode_readback_verified"):
                attack = copy.deepcopy(publication)
                current = attack[name][key]
                attack[name][key] = not current if type(current) is bool else (
                    attack["archive"]["inode"] if name == "receipt" and key == "inode"
                    else 0o644 if key == "mode" else current + 1)
                reject(attack, validate_synthetic_publication)
        falsely_passed_receipt = copy.deepcopy(publication)
        falsely_passed_receipt["receipt"]["candidate_status"] = "PASS"
        reject(falsely_passed_receipt, validate_synthetic_publication)
        for operation in (
            lambda: builtins.open("GOAL.md", "rb"),
            lambda: os.open("GOAL.md", os.O_RDONLY),
            lambda: subprocess.run(["/usr/bin/true"]),
            lambda: time.perf_counter(),
            lambda: socket.socket(),
            lambda: threading.Thread(target=lambda: None).start(),
            lambda: tempfile.mkdtemp(),
            lambda: importlib.import_module("candidates.go_candidate"),
        ):
            try:
                operation()
            except SourceOnlyViolation:
                rejected += 1
            else:
                raise CampaignError("a source-only external-effect boundary was bypassed")
        require(accepted >= 25 and rejected >= 255
                and all(value > 0 for value in boundary.blocked.values()),
                "independently exercise every suite, owner, fake proof, and real-effect wall")
        probes = dict(boundary.blocked)
    return {
        "schema": SCHEMA + "-source-only-self-test", "status": "PASS",
        "source_only": True, "synthetic_only": True,
        "accepted_synthetic_controls": accepted,
        "rejected_hostile_controls": rejected,
        "blocked_effect_probes": probes,
        "suite_count": 13, "case_execution_denominator": 31237,
        "source_family_count": 6, "source_owner_count": 25,
        "supported_actual_campaign_family_count": 2,
        "historically_runnable_original_family_count": 3,
        "independently_source_built_family_count": 5,
        "total_distinct_historical_evidence_owner_count": 65,
        "all_historical_versions_actual_compiler_process_count": 169,
        **zero_effects(),
    }


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    verify_runtime()
    with EffectBoundary(source_only=False) as guard:
        _, source = read_owned(SOURCE_RELATIVE, options.source_sha256,
                              maximum=MAX_SOURCE_BYTES)
        _, prose = read_owned(PROTOCOL_RELATIVE, options.protocol_sha256,
                             maximum=MAX_SOURCE_BYTES)
        machine_raw, machine = read_owned(DOCUMENT_RELATIVE, options.document_sha256,
                                           maximum=MAX_SOURCE_BYTES)
        validate_protocol_document(decode_document(
            machine_raw, "independent canonical original P0 campaign freeze"))
        producer = frozen_module(PRODUCER_RELATIVE, PRODUCER_SHA256, PRODUCER_BYTES)
        producer_prose, producer_protocol = read_owned(
            PRODUCER_PROTOCOL_RELATIVE, PRODUCER_PROTOCOL_SHA256,
            maximum=MAX_SOURCE_BYTES, exact_size=PRODUCER_PROTOCOL_BYTES)
        producer_raw, producer_document = read_owned(
            PRODUCER_DOCUMENT_RELATIVE, PRODUCER_DOCUMENT_SHA256,
            maximum=MAX_SOURCE_BYTES, exact_size=PRODUCER_DOCUMENT_BYTES)
        require(bool(producer_prose)
                and canonical(producer.protocol_document()) == producer_raw,
                "authenticate all three genuine unchanged P0 producer owners")
        inherited = producer.verify_frozen_context(argparse.Namespace(
            source_sha256=PRODUCER_SHA256,
            protocol_sha256=PRODUCER_PROTOCOL_SHA256,
            document_sha256=PRODUCER_DOCUMENT_SHA256,
        ))
        require(type(inherited) is dict and inherited.get("status") == "PASS"
                and inherited.get("read_only") is True
                and inherited.get("suite_count") == 13
                and inherited.get("case_execution_denominator") == 31237
                and inherited.get("named_private_waiver_count") == 13
                and inherited.get("source_family_count") == 6
                and inherited.get("source_owner_count") == 25
                and inherited.get("historically_runnable_p0_family_count") == 3
                and inherited.get("independently_source_built_family_count") == 5
                and inherited.get("total_distinct_historical_evidence_owner_count") == 65
                and inherited.get("all_historical_versions_actual_compiler_process_count") == 169
                and inherited.get("candidate_qualified_count") == 0
                and inherited.get("actual_v4_activations") == "NOT RUN",
                "independently verify the complete real 65-owner original P0 freeze")
        for key, value in zero_effects().items():
            if key in inherited:
                require(type(inherited[key]) is type(value)
                        and inherited[key] == value,
                        "the producer frozen context performed an actual effect: " + key)
        require(tuple(producer.SUITES) == SUITES
                and producer.OWNED_SOURCES == OWNED_SOURCES
                and producer.protocol_document()["successful_nested_lifecycle"]
                == protocol_document()["successful_nested_lifecycle"],
                "preserve every genuine original evaluator, full-width seed, source, and 394-call lifecycle")
        activation = frozen_module(V4_RELATIVE, V4_SHA256, V4_BYTES)
        _, activation_protocol = read_owned(
            V4_PROTOCOL_RELATIVE, V4_PROTOCOL_SHA256,
            maximum=MAX_SOURCE_BYTES, exact_size=V4_PROTOCOL_BYTES)
        activation_raw, activation_document = read_owned(
            V4_DOCUMENT_RELATIVE, V4_DOCUMENT_SHA256,
            maximum=MAX_SOURCE_BYTES, exact_size=V4_DOCUMENT_BYTES)
        activation.validate_contract(activation.decode_document(
            activation_raw, "independently pinned V4 machine", exact=False))
        history = activation.expected_historical_evidence()
        require(history.get("total_distinct_evidence_owner_count") == 65
                and history.get("candidate_evidence_owner_count") == 51
                and history.get("published_v4_build_evidence_owner_count") == 6
                and history.get("published_v5_build_evidence_owner_count") == 4
                and history.get("published_v6_build_evidence_owner_count") == 4
                and history.get("historical_build_process_ledger")
                == protocol_document()["historical_evidence"]["historical_build_process_ledger"]
                and activation.SOURCE_OWNERS == {
                    family: {path: (digest, size) for path, digest, size in owners}
                    for family, owners in OWNED_SOURCES.items()
                }, "preserve the exact actual historical evidence, process ledger, and source graph")
        histories = {(version, row.get("family")): row
                     for version, key in ((4, "published_v4_builds"),
                                          (6, "published_v6_builds"))
                     for row in history.get(key, [])}
        build_owners: dict[str, dict[str, Any]] = {}
        for family, proof in BUILD_PROOFS.items():
            actual = histories.get((proof["version"], family))
            require(type(actual) is dict and actual.get("build_status") == "PASS"
                    and actual.get("completed_phase_count") == 2
                    and actual.get("process_count") == proof["actual_compiler_process_count"]
                    and actual.get("archive_path") == proof["archive_relative"]
                    and actual.get("archive_sha256") == proof["archive_sha256"]
                    and actual.get("archive_bytes") == proof["archive_bytes"]
                    and actual.get("receipt_path") == proof["receipt_relative"]
                    and actual.get("receipt_sha256") == proof["receipt_sha256"]
                    and actual.get("receipt_bytes") == proof["receipt_bytes"]
                    and actual.get("qualified_candidate_count") == 0,
                    "require one real two-phase first-party build: " + family)
            _, archive_owner = read_owned(
                proof["archive_relative"], proof["archive_sha256"],
                maximum=MAX_ARCHIVE_BYTES, exact_size=proof["archive_bytes"],
                owner_only=True)
            _, receipt_owner = read_owned(
                proof["receipt_relative"], proof["receipt_sha256"],
                maximum=MAX_SOURCE_BYTES, exact_size=proof["receipt_bytes"],
                owner_only=True)
            require((archive_owner["device"], archive_owner["inode"])
                    != (receipt_owner["device"], receipt_owner["inode"]),
                    "a genuine build archive and receipt must have distinct 0600 owners")
            build_owners[family] = {"archive": archive_owner,
                                    "receipt": receipt_owner}
    require(all(value == 0 for key, value in guard.actual.items()
                if type(value) is int and type(value) is not bool),
            "a frozen campaign context caused an actual external effect")
    return {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS", "read_only": True,
        "source": source, "protocol": prose, "document": machine,
        "frozen_producer_source": {
            "relative": PRODUCER_RELATIVE, "sha256": PRODUCER_SHA256,
            "size_bytes": PRODUCER_BYTES,
        },
        "frozen_producer_protocol": producer_protocol,
        "frozen_producer_document": producer_document,
        "frozen_activation_source": {
            "relative": V4_RELATIVE, "sha256": V4_SHA256,
            "size_bytes": V4_BYTES,
        },
        "frozen_activation_protocol": activation_protocol,
        "frozen_activation_document": activation_document,
        "actual_passing_source_build_owners": build_owners,
        "suite_count": 13, "case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "source_family_count": 6, "source_owner_count": 25,
        "pairwise_shared_semantic_source_count": 0,
        "supported_actual_campaign_families": ["cpp", "go"],
        "supported_actual_campaign_family_count": 2,
        "historically_runnable_original_family_count": 3,
        "independently_source_built_family_count": 5,
        "total_distinct_historical_evidence_owner_count": 65,
        "historical_build_process_ledger": protocol_document()[
            "historical_evidence"]["historical_build_process_ledger"],
        "all_historical_versions_actual_compiler_process_count": 169,
        "actual_v4_activations": "NOT RUN",
        **zero_effects(),
    }


def evidence_names(family: str, label: str,
                   *, failure: bool) -> tuple[str, str]:
    require(family in BUILD_PROOFS and type(failure) is bool,
            "publish only a genuine C++ or Go complete-candidate report")
    stem = "owned-six-family-original-p0-campaign-v1-" + family + "-" + checked_label(label)
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def open_evidence_directory() -> int:
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0))
    descriptor = os.open(str(ROOT / EVIDENCE_RELATIVE), flags)
    owner = os.fstat(descriptor)
    visible = os.stat(str(ROOT / EVIDENCE_RELATIVE), follow_symlinks=False)
    require(stat.S_ISDIR(owner.st_mode)
            and (owner.st_dev, owner.st_ino) == (visible.st_dev, visible.st_ino)
            and owner.st_uid == os.geteuid(),
            "use only the existing authentic first-party evidence directory")
    return descriptor


def ensure_fresh_evidence(family: str, label: str) -> None:
    descriptor = open_evidence_directory()
    try:
        for failure in (False, True):
            for basename in evidence_names(family, label, failure=failure):
                try:
                    os.stat(basename, dir_fd=descriptor, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise CampaignError("never replace a published campaign owner: " + basename)
    finally:
        os.close(descriptor)


def bounded_process(argv: list[str], *, timeout: int) -> dict[str, Any]:
    require(type(argv) is list and all(type(item) is str for item in argv)
            and argv[:3] == [PINNED_PYTHON, "-I", "-B"]
            and type(timeout) is int and 0 < timeout <= SUITE_TIMEOUT_SECONDS,
            "run only one bounded shell-free isolated pinned producer worker")
    process = subprocess.Popen(
        argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, cwd=str(ROOT), shell=False,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"})
    require(process.stdout is not None and process.stderr is not None,
            "capture both independent complete candidate output streams")
    streams: dict[str, dict[str, Any]] = {
        "stdout": {"raw": bytearray(), "limit": MAX_SUITE_STDOUT_BYTES,
                   "overflow": False, "error": None},
        "stderr": {"raw": bytearray(), "limit": MAX_SUITE_STDERR_BYTES,
                   "overflow": False, "error": None},
    }

    def drain(name: str, handle: Any) -> None:
        state = streams[name]
        try:
            while True:
                piece = handle.read(65536)
                if not piece:
                    break
                remaining = state["limit"] - len(state["raw"])
                if len(piece) > remaining:
                    if remaining:
                        state["raw"].extend(piece[:remaining])
                    state["overflow"] = True
                    process.kill()
                    break
                state["raw"].extend(piece)
        except BaseException as error:
            state["error"] = {
                "type": type(error).__qualname__, "message": str(error),
                "traceback": traceback.format_exception(
                    type(error), error, error.__traceback__),
            }
            try:
                process.kill()
            except OSError:
                pass

    threads = [threading.Thread(target=drain, args=("stdout", process.stdout)),
               threading.Thread(target=drain, args=("stderr", process.stderr))]
    for item in threads:
        item.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait(timeout=15)
    finally:
        for item in threads:
            item.join(timeout=15)
    require(all(not item.is_alive() for item in threads),
            "never discard a live candidate stdout or stderr reader")
    stdout = bytes(streams["stdout"]["raw"])
    stderr = bytes(streams["stderr"]["raw"])
    return {
        "returncode": process.returncode,
        "timed_out": timed_out,
        "stdout_base64": base64.b64encode(stdout).decode("ascii"),
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stdout_bytes": len(stdout),
        "stdout_overflow": streams["stdout"]["overflow"],
        "stdout_reader_error": streams["stdout"]["error"],
        "stderr_base64": base64.b64encode(stderr).decode("ascii"),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "stderr_bytes": len(stderr),
        "stderr_overflow": streams["stderr"]["overflow"],
        "stderr_reader_error": streams["stderr"]["error"],
    }


def activation_arguments(options: argparse.Namespace) -> list[str]:
    proof = BUILD_PROOFS[options.family]
    args = ["--activate", "--family", options.family,
            "--build-label", proof["label"],
            "--build-root", options.build_root,
            "--activation-source-sha256", V4_SHA256,
            "--activation-protocol-sha256", V4_PROTOCOL_SHA256,
            "--activation-contract-sha256", V4_DOCUMENT_SHA256,
            "--build-source-sha256", proof["source_sha256"],
            "--build-protocol-sha256", proof["protocol_sha256"],
            "--build-contract-sha256", proof["contract_sha256"],
            "--build-report-sha256", proof["archive_sha256"],
            "--build-receipt-sha256", proof["receipt_sha256"]]
    for path, digest, _ in OWNED_SOURCES[options.family]:
        args.extend(("--owned-source-sha256", path + "=" + digest))
    for role, native in proof["native_outputs"].items():
        args.extend(("--native-sha256", role + "=" + native["sha256"]))
        args.extend(("--native-bytes", role + "=" + str(native["size_bytes"])))
    return args


def actual_worker_arguments(options: argparse.Namespace,
                            suite: tuple[Any, ...], activation: dict[str, Any]) -> list[str]:
    family = options.family
    proof = BUILD_PROOFS[family]
    outputs = proof["native_outputs"]
    bridge = outputs["bridge"]["sha256"]
    engine = bridge if family == "cpp" else outputs["engine"]["sha256"]
    args = [PINNED_PYTHON, "-I", "-B", str(ROOT / PRODUCER_RELATIVE),
            "--run", "--family", family, "--suite", suite[0],
            "--label", options.label,
            "--build-version", str(proof["version"]),
            "--build-label", proof["label"],
            "--activation-root", activation["activation_root"],
            "--source-sha256", PRODUCER_SHA256,
            "--protocol-sha256", PRODUCER_PROTOCOL_SHA256,
            "--document-sha256", PRODUCER_DOCUMENT_SHA256,
            "--build-source-sha256", proof["source_sha256"],
            "--build-protocol-sha256", proof["protocol_sha256"],
            "--build-contract-sha256", proof["contract_sha256"],
            "--build-archive-sha256", proof["archive_sha256"],
            "--build-receipt-sha256", proof["receipt_sha256"],
            "--activation-source-sha256", V4_SHA256,
            "--activation-protocol-sha256", V4_PROTOCOL_SHA256,
            "--activation-contract-sha256", V4_DOCUMENT_SHA256,
            "--activation-report-sha256", activation["activation_report_sha256"],
            "--activation-receipt-sha256", activation["activation_receipt_sha256"],
            "--recovery-journal-sha256", activation["recovery_journal_sha256"],
            "--candidate-source-sha256", proof["candidate_adapter_sha256"],
            "--native-engine-sha256", engine,
            "--native-bridge-sha256", bridge]
    for path, digest, _ in OWNED_SOURCES[family]:
        args.extend(("--owned-source-sha256", path + "=" + digest))
    return args


def observe_actual_worker(options: argparse.Namespace,
                          suite: tuple[Any, ...], activation: dict[str, Any]) -> dict[str, Any]:
    name, count, source_path, source_sha, matrix, reference, _, _ = suite
    process: dict[str, Any] | None = None
    try:
        process = bounded_process(actual_worker_arguments(options, suite, activation),
                                  timeout=SUITE_TIMEOUT_SECONDS)
        raw = base64.b64decode(process["stdout_base64"], validate=True)
        observation: dict[str, Any] | None = None
        decode_error: dict[str, Any] | None = None
        try:
            observation = decode_document(raw, "complete original suite " + name,
                                          maximum=MAX_SUITE_STDOUT_BYTES)
        except (CampaignError, ValueError, UnicodeError) as error:
            decode_error = {
                "type": type(error).__qualname__, "message": str(error),
                "traceback": traceback.format_exception(
                    type(error), error, error.__traceback__),
            }
        genuine = (type(observation) is dict
                   and observation.get("schema")
                   == "rebar-owned-six-family-original-p0-producer-v1-actual-original-suite"
                   and observation.get("suite") == name
                   and observation.get("candidate_family") == options.family
                   and observation.get("case_execution_denominator") == count
                   and observation.get("actual_candidate_case_count") == count
                   and type(observation.get("candidate_records")) is list
                   and len(observation["candidate_records"])
                   == (152 if name == "original_bounded_v5" else count)
                   and observation.get("source_relative") == source_path
                   and observation.get("source_sha256") == source_sha
                   and observation.get("matrix_sha256") == matrix
                   and observation.get("reference_records_sha256") == reference
                   and observation.get("phase_one_case_execution_denominator") == 31237
                   and observation.get("supplemental_cases_added_to_phase_one") is False
                   and observation.get("total_preserved_historical_evidence_owner_count") == 65
                   and observation.get("actual_candidate_workers") == 1
                   and observation.get("hidden_cases_read") == 0
                   and observation.get("benchmark_files_read") == 0
                   and observation.get("clock_samples") == 0
                   and observation.get("performance") == "NOT MEASURED"
                   and observation.get("holdout") == "NOT OPENED")
        if name == "original_bounded_v5" and genuine:
            genuine = (observation.get("actual_public_record_count") == 152
                       and observation.get("actual_debug_skip_count") == 1
                       and observation.get("named_private_waiver_count") == 13
                       and type(observation.get("named_private_waivers")) is list
                       and len(observation["named_private_waivers"]) == 13)
        mismatch_count = (observation.get("mismatch_count")
                          if type(observation) is dict else None)
        mismatches = (observation.get("all_mismatches")
                      if type(observation) is dict else None)
        passing = (genuine and process["returncode"] == 0
                   and not process["timed_out"]
                   and not process["stdout_overflow"]
                   and not process["stderr_overflow"]
                   and process["stdout_reader_error"] is None
                   and process["stderr_reader_error"] is None
                   and observation.get("status") == "PASS"
                   and type(mismatch_count) is int and mismatch_count == 0
                   and type(mismatches) is list and not mismatches)
        if name == "subinterpreter_v2" and passing:
            passing = (observation.get("actual_case_interpreter_exec_calls") == 394
                       and observation.get("actual_initialization_interpreter_exec_calls") == 11
                       and observation.get("actual_guard_cleanup_interpreter_exec_calls") == 11
                       and observation.get("actual_interpreters_created") == 11
                       and observation.get("actual_interpreters_destroyed") == 11
                       and observation.get("all_real_pipes_read_to_eof") is True
                       and observation.get("all_real_pipe_descriptors_closed") is True)
        return {
            "suite": name, "status": "PASS" if passing else "FAIL",
            "case_execution_denominator": count,
            "frozen_source_sha256": source_sha,
            "frozen_matrix_sha256": matrix,
            "frozen_reference_records_sha256": reference,
            "process": process,
            "complete_original_observation": observation,
            "json_decode_failure": decode_error,
            "genuine_original_suite": genuine,
            "mismatch_count": mismatch_count,
            "all_mismatches": mismatches,
            "semantic_failure_preserved": bool(genuine
                and observation.get("status") == "FAIL"
                and process["returncode"] == 1),
            "actual_worker_started": True,
        }
    except BaseException as error:
        return {
            "suite": name, "status": "FAIL",
            "case_execution_denominator": count,
            "frozen_source_sha256": source_sha,
            "frozen_matrix_sha256": matrix,
            "frozen_reference_records_sha256": reference,
            "process": process,
            "complete_original_observation": None,
            "json_decode_failure": None,
            "genuine_original_suite": False,
            "mismatch_count": None,
            "all_mismatches": None,
            "semantic_failure_preserved": False,
            "actual_worker_started": process is not None,
            "actual_failure": {
                "type": type(error).__qualname__, "message": str(error),
                "traceback": traceback.format_exception(
                    type(error), error, error.__traceback__),
            },
        }


def restore_activation(activation_module: Any,
                       family: str,
                       published: dict[str, Any]) -> dict[str, Any]:
    reportful = ["--restore", "--family", family,
                 "--activation-root", published["activation_root"],
                 "--activation-source-sha256", V4_SHA256,
                 "--activation-protocol-sha256", V4_PROTOCOL_SHA256,
                 "--activation-contract-sha256", V4_DOCUMENT_SHA256,
                 "--activation-report-sha256", published["activation_report_sha256"],
                 "--activation-receipt-sha256", published["activation_receipt_sha256"]]
    try:
        restored = activation_module.recover(
            activation_module.parse_arguments(reportful))
        require(type(restored) is dict and restored.get("status") == "PASS"
                and restored.get("schema") == activation_module.RESTORATION_SCHEMA
                and restored.get("family") == family
                and restored.get("activation_root") == published["activation_root"]
                and restored.get("recovery_journal_sha256")
                == published["recovery_journal_sha256"]
                and restored.get("reportless_recovery") is False
                and set(restored.get("restored_targets", {}))
                == set(activation_module.FAMILIES[family]["targets"]),
                "the actual complete reportful V4 restoration was not verified")
        return {"status": "PASS", "route": "reportful-restore",
                "actual_restoration": restored,
                "reportful_failure": None}
    except BaseException as original:
        reportless = ["--recover", "--family", family,
                      "--activation-root", published["activation_root"],
                      "--activation-source-sha256", V4_SHA256,
                      "--activation-protocol-sha256", V4_PROTOCOL_SHA256,
                      "--activation-contract-sha256", V4_DOCUMENT_SHA256,
                      "--recovery-journal-sha256",
                      published["recovery_journal_sha256"]]
        try:
            restored = activation_module.recover(
                activation_module.parse_arguments(reportless))
            require(type(restored) is dict and restored.get("status") == "PASS"
                    and restored.get("schema") == activation_module.RESTORATION_SCHEMA
                    and restored.get("family") == family
                    and restored.get("recovery_journal_sha256")
                    == published["recovery_journal_sha256"]
                    and restored.get("reportless_recovery") is True
                    and set(restored.get("restored_targets", {}))
                    == set(activation_module.FAMILIES[family]["targets"]),
                    "the genuine reportless V4 fallback did not restore all targets")
            return {
                "status": "PASS", "route": "reportless-recovery",
                "actual_restoration": restored,
                "reportful_failure": {
                    "type": type(original).__qualname__, "message": str(original),
                    "traceback": traceback.format_exception(
                        type(original), original, original.__traceback__),
                },
            }
        except BaseException as secondary:
            return {
                "status": "FAIL", "route": "reportless-recovery-failed",
                "actual_restoration": None,
                "reportful_failure": {
                    "type": type(original).__qualname__, "message": str(original),
                    "traceback": traceback.format_exception(
                        type(original), original, original.__traceback__),
                },
                "reportless_failure": {
                    "type": type(secondary).__qualname__, "message": str(secondary),
                    "traceback": traceback.format_exception(
                        type(secondary), secondary, secondary.__traceback__),
                },
            }


def publish_actual_report(report: dict[str, Any], options: argparse.Namespace) -> dict[str, Any]:
    family, label = options.family, checked_label(options.label)
    require(report.get("schema") == SCHEMA + "-complete-candidate-evaluation"
            and report.get("candidate_family") == family
            and report.get("label") == label
            and report.get("suite_count") == 13
            and report.get("case_execution_denominator") == 31237
            and report.get("completed_suite_count") == 13
            and len(report.get("suite_results", [])) == 13
            and report.get("restoration", {}).get("status") == "PASS"
            and report.get("status") in {"PASS", "FAIL"}
            and report.get("candidate_qualified") is (report["status"] == "PASS"),
            "publish only a complete, genuinely restored original candidate campaign")
    plain = canonical(report)
    require(0 < len(plain) <= MAX_REPORT_BYTES,
            "bound and preserve the entire canonical original campaign")
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(compressed) <= MAX_ARCHIVE_BYTES,
            "bound a deterministic complete single-member campaign archive")
    inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
    recovered = inflater.decompress(compressed, MAX_REPORT_BYTES + 1)
    require(inflater.eof and not inflater.unused_data
            and not inflater.unconsumed_tail and recovered == plain,
            "prove exact complete gzip recovery before durable publication")
    archive_name, receipt_name = evidence_names(
        family, label, failure=report["status"] == "FAIL")
    activation_module = frozen_module(V4_RELATIVE, V4_SHA256, V4_BYTES)
    evidence_root = str(ROOT / EVIDENCE_RELATIVE)
    archive = activation_module.write_fresh(
        evidence_root, archive_name, compressed)
    archive_sync = activation_module.synchronize_directory(evidence_root)
    require(archive.get("mode") == 0o600
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("same_inode_readback_verified") is True
            and archive_sync.get("completed") is True,
            "prove the genuine pinned V4 owner-only archive and directory fsync")
    receipt_document = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "status": "PASS", "candidate_status": report["status"],
            "candidate_family": family, "label": label,
            "campaign_source_sha256": options.source_sha256,
            "campaign_protocol_sha256": options.protocol_sha256,
            "campaign_document_sha256": options.document_sha256,
            "producer_source_sha256": PRODUCER_SHA256,
            "producer_protocol_sha256": PRODUCER_PROTOCOL_SHA256,
            "producer_document_sha256": PRODUCER_DOCUMENT_SHA256,
            "phase_one_manifest_sha256": PHASE1_SHA256,
            "suite_count": 13, "case_execution_denominator": 31237,
            "completed_suite_count": 13,
            "archive": archive,
            "archive_directory_fsync_completed": archive_sync["completed"],
            "uncompressed_sha256": hashlib.sha256(plain).hexdigest(),
            "uncompressed_bytes": len(plain),
            "activation": report["activation"],
            "restoration": report["restoration"],
            "all_mismatches_crashes_and_timeouts_preserved": True,
            "failure_preserved": report["status"] == "FAIL",
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
            "winner_selected": False,
            "receipt_self_publication": "NOT CLAIMED",
    }
    receipt_raw = canonical(receipt_document)
    require(len(receipt_raw) <= MAX_SOURCE_BYTES,
            "bound the separate owner-only complete-campaign receipt")
    receipt = activation_module.write_fresh(
        evidence_root, receipt_name, receipt_raw)
    receipt_sync = activation_module.synchronize_directory(evidence_root)
    require(receipt.get("mode") == 0o600
            and receipt.get("exclusive_creation") is True
            and receipt.get("file_fsync_completed") is True
            and receipt.get("same_inode_readback_verified") is True
            and receipt_sync.get("completed") is True
            and (archive["device"], archive["inode"])
            != (receipt["device"], receipt["inode"]),
            "independently fsync two distinct genuine owner-only V4 evidence inodes")
    return {
        "schema": SCHEMA + "-published-complete-candidate",
        "status": report["status"], "candidate_family": family,
        "label": label, "suite_count": 13,
        "case_execution_denominator": 31237,
        "completed_suite_count": 13,
        "verified_passing_case_count": report["verified_passing_case_count"],
        "candidate_qualified": report["candidate_qualified"],
        "complete_archive": archive,
        "complete_publication_receipt": receipt,
        "all_mismatches_crashes_and_timeouts_preserved": True,
        "restoration_verified_before_publication": True,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def run_actual_campaign(options: argparse.Namespace) -> dict[str, Any]:
    context = verify_frozen_context(argparse.Namespace(
        source_sha256=options.source_sha256,
        protocol_sha256=options.protocol_sha256,
        document_sha256=options.document_sha256,
    ))
    require(context.get("status") == "PASS"
            and context.get("total_distinct_historical_evidence_owner_count") == 65,
            "require the complete original campaign freeze before any promotion")
    ensure_fresh_evidence(options.family, options.label)
    activation_module = frozen_module(V4_RELATIVE, V4_SHA256, V4_BYTES)
    activate_options = activation_module.parse_arguments(
        activation_arguments(options))
    prerequisite = activation_module.authenticate_prerequisites(activate_options)
    require(prerequisite.get("family") == options.family
            and prerequisite.get("build_version")
            == BUILD_PROOFS[options.family]["version"],
            "prove the actual passing two-phase source build before activation")
    published: dict[str, Any] | None = None
    restoration: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    outer_failure: dict[str, Any] | None = None
    try:
        published = activation_module.activate(activate_options)
        require(type(published) is dict
                and published.get("schema")
                == activation_module.SCHEMA + "-published-activation"
                and published.get("status") == "PASS"
                and published.get("family") == options.family
                and type(published.get("activation_root")) is str
                and all(type(published.get(key)) is str for key in
                        ("activation_report_sha256", "activation_receipt_sha256",
                         "recovery_journal_sha256")),
                "require the actual owner-only recoverable V4 activation")
        for suite in SUITES:
            rows.append(observe_actual_worker(options, suite, published))
    except BaseException as error:
        outer_failure = {
            "type": type(error).__qualname__, "message": str(error),
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__),
        }
    finally:
        if published is not None:
            restoration = restore_activation(activation_module, options.family, published)
    if published is None:
        raise CampaignExecutionFailure(
            "activation failed before a recoverable campaign existed",
            {"activation": None, "restoration": restoration,
             "suite_results": rows, "outer_failure": outer_failure,
             "actual_candidate_workers": sum(
                 bool(row.get("actual_worker_started")) for row in rows),
             "actual_native_activations": 0})
    if restoration is None or restoration.get("status") != "PASS":
        raise CampaignExecutionFailure(
            "actual original canonical owners were not genuinely restored",
            {"activation": published, "restoration": restoration,
             "suite_results": rows, "outer_failure": outer_failure,
             "actual_candidate_workers": sum(
                 bool(row.get("actual_worker_started")) for row in rows),
             "actual_native_activations": 1})
    if outer_failure is not None:
        if len(rows) != 13:
            raise CampaignExecutionFailure(
                "fail closed after restoration: not all original suites were observed",
                {"activation": published, "restoration": restoration,
                 "suite_results": rows, "outer_failure": outer_failure,
                 "actual_candidate_workers": sum(
                     bool(row.get("actual_worker_started")) for row in rows),
                 "actual_native_activations": 1})
    require(len(rows) == 13 and [row.get("suite") for row in rows]
            == [suite[0] for suite in SUITES],
            "never omit, duplicate, reorder, or qualify a partial original campaign")
    passes = [row for row in rows if row.get("status") == "PASS"]
    passing_cases = sum(row["case_execution_denominator"] for row in passes)
    status = "PASS" if len(passes) == 13 and outer_failure is None else "FAIL"
    report = {
        "schema": SCHEMA + "-complete-candidate-evaluation",
        "status": status, "candidate_family": options.family,
        "label": options.label,
        "campaign_source_sha256": options.source_sha256,
        "campaign_protocol_sha256": options.protocol_sha256,
        "campaign_document_sha256": options.document_sha256,
        "producer_source_sha256": PRODUCER_SHA256,
        "producer_protocol_sha256": PRODUCER_PROTOCOL_SHA256,
        "producer_document_sha256": PRODUCER_DOCUMENT_SHA256,
        "phase_one_manifest_sha256": PHASE1_SHA256,
        "suite_count": 13, "case_execution_denominator": 31237,
        "completed_suite_count": len(rows),
        "suite_results": rows,
        "verified_passing_case_count": passing_cases,
        "candidate_qualified": status == "PASS" and passing_cases == 31237,
        "activation": published,
        "restoration": restoration,
        "outer_failure": outer_failure,
        "actual_candidate_workers": sum(
            bool(row.get("actual_worker_started")) for row in rows),
        "actual_native_activations": 1,
        "actual_source_builds": 0,
        "actual_reference_workers": 0,
        "all_mismatches_crashes_and_timeouts_preserved": True,
        "generated_go_header_promoted": False,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    try:
        return publish_actual_report(report, options)
    except BaseException as error:
        raise CampaignExecutionFailure(
            "preserve the complete restored candidate when publication fails",
            {
                "activation": published,
                "restoration": restoration,
                "complete_candidate_report": report,
                "publication_failure": {
                    "type": type(error).__qualname__, "message": str(error),
                    "traceback": traceback.format_exception(
                        type(error), error, error.__traceback__),
                },
                "actual_candidate_workers": report["actual_candidate_workers"],
                "actual_native_activations": 1,
            },
        ) from error


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--family", choices=("cpp", "go"))
    parser.add_argument("--label")
    parser.add_argument("--build-root")
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--document-sha256")
    options = parser.parse_args(arguments)
    pins = ("source_sha256", "protocol_sha256", "document_sha256")
    if options.self_test:
        require(options.family is None and options.label is None
                and options.build_root is None
                and all(getattr(options, name) is None for name in pins),
                "source-only tests accept no path, pin, activation, or campaign")
        return options
    for name in pins:
        checked_digest(getattr(options, name), name)
    if options.verify_frozen_context:
        require(options.family is None and options.label is None
                and options.build_root is None,
                "read-only context accepts only the exact campaign owner triple")
        return options
    require(options.run and options.family in BUILD_PROOFS,
            "actually campaign only a genuinely source-built C++ or Go family")
    checked_label(options.label)
    require(type(options.build_root) is str and bool(options.build_root),
            "explicitly provide the genuine first-party private build root")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        options = parse_arguments(arguments)
        if options.self_test:
            result = self_test()
        elif options.verify_frozen_context:
            result = verify_frozen_context(options)
        else:
            result = run_actual_campaign(options)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except BaseException as error:
        failure = {
            "schema": SCHEMA + "-entry-failure", "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error_message": str(error),
            **zero_effects(),
        }
        details = getattr(error, "details", None)
        if type(details) is dict:
            failure["actual_failure"] = details
            failure["actual_candidate_workers"] = details.get(
                "actual_candidate_workers", 0)
            failure["actual_native_activations"] = details.get(
                "actual_native_activations", 0)
        try:
            sys.stdout.buffer.write(canonical(failure))
            sys.stdout.buffer.flush()
        except (OSError, ValueError, TypeError):
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
