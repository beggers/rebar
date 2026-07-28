#!/usr/bin/env python3
"""Freeze and safely stream a complete, original first-party P0 campaign.

Self-tests are wholly synthetic. Context verification is strictly read-only.
Only a separately authorized, explicit run may reuse the authenticated V1
evaluator and reversible activator. No verification mode runs a candidate.
"""

from __future__ import annotations

import argparse
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
from typing import Any, Iterable, Sequence
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_owned_six_family_original_p0_campaign_v2.py"
PROTOCOL_RELATIVE = "oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V2.md"
DOCUMENT_RELATIVE = "oracle/phase2/six-family-p0-campaign-v2.json"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-owned-six-family-original-p0-campaign-v2"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PHASE1_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
V1_RELATIVE = "tools/run_owned_six_family_original_p0_campaign_v1.py"
V1_SHA256 = "50ac9f549739bb6b540f1762177f25b46c1fa345dce717ea7163e15d98ae7e88"
V1_BYTES = 93832
V1_PROTOCOL_RELATIVE = "oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V1.md"
V1_PROTOCOL_SHA256 = "01d5908b9c1c3c356059a21cd0b418a7278559843d465e9062155b68f6497422"
V1_PROTOCOL_BYTES = 4249
V1_DOCUMENT_RELATIVE = "oracle/phase2/six-family-p0-campaign-v1.json"
V1_DOCUMENT_SHA256 = "c619e63dd18b8242bfc1af9e01030eff60e8d17128a83de216992b5cdc619801"
V1_DOCUMENT_BYTES = 19273
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
PRESERVATION_RELATIVE = "tools/preserve_owned_go_campaign_publication_failure_v1.py"
PRESERVATION_SHA256 = "105b7e730eae779396840ccaca13152554244ea615e5403930e0adbd2344f5ba"
PRESERVATION_BYTES = 77347
PRESERVATION_PROTOCOL_RELATIVE = "oracle/phase2/OWNED-GO-CAMPAIGN-PUBLICATION-FAILURE-V1.md"
PRESERVATION_PROTOCOL_SHA256 = "5e067f3d71c0997be69cd5e3eb246c2e1c9387cd40616230e806ddf561994f4f"
PRESERVATION_PROTOCOL_BYTES = 4438
PRESERVATION_DOCUMENT_RELATIVE = "oracle/phase2/owned-go-campaign-publication-failure-v1.json"
PRESERVATION_DOCUMENT_SHA256 = "f095f94f74255432b0ceff7eb1239e28d6e4e4effeab19d4f2fed86156b2925b"
PRESERVATION_DOCUMENT_BYTES = 8006
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_SUITE_STDOUT_BYTES = 64 * 1024 * 1024
MAX_SUITE_STDERR_BYTES = 4 * 1024 * 1024
V1_MAX_REPORT_BYTES = 256 * 1024 * 1024
MAX_REPORT_BYTES = 4 * 1024 * 1024 * 1024
MAX_ARCHIVE_BYTES = 4 * 1024 * 1024 * 1024
STREAM_CHUNK_BYTES = 64 * 1024
MAX_ERROR_MESSAGE_BYTES = 2048

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
    "c": (("candidates/vm_candidate.py", "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096", 60707), ("candidates/_vm_native.c", "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55", 218185)),
    "zig": (("candidates/zig_candidate.py", "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862", 68422), ("candidates/zig/mini_regex.zig", "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28", 186915), ("candidates/zig/py_bridge.c", "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b", 173026)),
    "cpp": (("candidates/cpp_candidate.py", "8dcece29b1a194eea023143148af37bb679a9df4c39c01153f5ee23f778e16d5", 27488), ("candidates/cpp/engine.hpp", "66998fed1839f5e5f7f09382830ed9fda1a62b80bd545305c4eee95ed9a13df9", 4089), ("candidates/cpp/engine.cpp", "a9ceb37cfde77447a01a36a8882f7713faf5f201d7a15a193dd17e7b91d118f5", 62813), ("candidates/cpp/py_bridge.cpp", "1d930b63b2f9493dd4759b7521f75d8846daf2580a5699337fcf82540484ab6d", 25068)),
    "go": (("candidates/go_candidate.py", "816d21527b9806afbc9457122f72f8f6b62c39b8b791d3f363745d412cbe3d20", 31049), ("candidates/go/go.mod", "9297c4e8fe4649196150400d23a4da584d7ef721347f7095399a7382edad669b", 44), ("candidates/go/engine.go", "6472c4413921f3a877455315400c532e7632a871a96d46de9583fa6170a43192", 53782), ("candidates/go/py_bridge.c", "52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a", 39373)),
    "fortran": (("candidates/fortran_candidate.py", "8db564771d38c0896a5207f1241a44463432dc5bf75dfcf657740d8bcfefd194", 26521), ("candidates/fortran/engine.f90", "5180da085487b9932e3f769e6baded6a8409a0b778890e6197aaea6dad1923a5", 85062), ("candidates/fortran/py_bridge.c", "8540b708de4819f1b3340c32e78eaf083c1cad35f016c0f7af33a27773694b0d", 26311)),
}

PRIVATE_WAIVERS = (
    "DebugTests.test_debug_flag", "DebugTests.test_atomic_group",
    "DebugTests.test_possesive_repeat_one", "DebugTests.test_possesive_repeat",
    "ImplementationTest.test_immutable", "ImplementationTest.test_overlap_table",
    "ImplementationTest.test_signedness", "ImplementationTest.test_disallow_instantiation",
    "ImplementationTest.test_deprecated_modules", "ImplementationTest.test_case_helpers",
    "ImplementationTest.test_dealloc", "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
    "ImplementationTest.test_sre_template_invalid_group_index",
)

V1_CPP_FAILURE = {
    "family": "cpp", "candidate_status": "FAIL", "receipt_status": "PASS",
    "label": "phase2-v1", "suite_count": 13,
    "case_execution_denominator": 31237, "completed_suite_count": 13,
    "archive_relative": "oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-cpp-phase2-v1-failures.json.gz",
    "archive_sha256": "0462adbd6ee7bafb274578462117513669de9b849473a2e1ada441407bc814a2",
    "archive_bytes": 3244833,
    "receipt_relative": "oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-cpp-phase2-v1-failures-publication-receipt.json",
    "receipt_sha256": "7b1156c07441acd579149ca9b3aedcb9308eb75a130ce7f7df98aa6a89d776f6",
    "receipt_bytes": 3936,
    "uncompressed_bytes": 97639407,
    "uncompressed_sha256": "58d918b4febe8fcbc5b9f7945c376ae639455fb69da46336b674a8dca1dd0fae",
}

V1_GO_PRIVATE_OWNERS = (
    ("activation_report", "activation-report.json", "58bab0b59bbec0bd3d536f04a752b98424d5f690dc70c532adb8fffcc678309c", 6959, 11387742),
    ("activation_receipt", "activation-receipt.json", "43c07c72d44148b4adf69337732bdc139dc5e4eb8893bb8a31fd27dea0a325c3", 2667, 11387753),
    ("recovery_journal", "recovery-journal.json", "8c71db399823923982d2fc81d8fc17e52dad44a6c4ed85d1be339300e3e95518", 3471, 11385003),
    ("engine_intention", "promotion-intent-engine.json", "e599d5ab3cc01cd39bd87251f837d08c9e4a25193a78bc7114dc63c351092c41", 1121, 11385035),
    ("bridge_intention", "promotion-intent-bridge.json", "0db59bf159edf46b87c7d179cdbd94c068094ffb86b14f08fdbebdb31633f4d9", 1177, 11387740),
)

V1_GO_PUBLICATION_FAILURE = {
    "family": "go", "label": "phase2-v1",
    "infrastructure_status": "FAIL", "candidate_status": "NOT VERIFIED",
    "candidate_qualified": False, "receipt_status": "PASS",
    "receipt_status_meaning": "EVIDENCE PUBLICATION ONLY",
    "archive_relative": "oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-publication-failure-evidence.json.gz",
    "archive_sha256": "5ed230d255cc8ba87ff2790dd0bce091968252da159e2d8c6d7ada93feeae87e",
    "archive_bytes": 7719,
    "receipt_relative": "oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-publication-failure-evidence-publication-receipt.json",
    "receipt_sha256": "0b7d11dad3c204d34151a38d797b1177442040524acf68fb29633d4222d681b0",
    "receipt_bytes": 2724,
    "uncompressed_bytes": 26265,
    "uncompressed_sha256": "d354dc7ab5cc4bad0bd72c70a5e6af03749f019ebd047d07a8fe19c2e784a2e6",
    "embedded_original_owner_count": 5,
    "embedded_original_owner_total_bytes": 15395,
    "actual_original_report_bytes": "NOT RECORDED",
    "actual_restoration_route": "NOT RECORDED",
    "actual_suite_statuses": "NOT RECORDED",
    "actual_mismatch_count": "NOT RECORDED",
}


class CampaignError(Exception):
    """A complete original campaign or its durable owner was not proven."""


class SourceOnlyViolation(CampaignError):
    """Source-only verification attempted an actual outside effect."""


class CampaignExecutionFailure(CampaignError):
    """Preserve bounded operational facts without printing a complete report."""

    def __init__(self, message: str, details: dict[str, Any]) -> None:
        super().__init__(message)
        self.details = details


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise CampaignError(message)


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require one complete lowercase SHA-256: " + label)
    return value


def checked_label(value: Any) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    require(type(value) is str and 0 < len(value.encode("utf-8")) <= 48
            and all(char in alphabet for char in value),
            "require one bounded original first-party campaign label")
    return value


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           separators=(",", ":"), sort_keys=True)
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise CampaignError("require finite, exact, surrogate-safe canonical JSON") from error


def zero_effects() -> dict[str, Any]:
    return {
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "actual_reference_workers": 0, "actual_source_builds": 0,
        "actual_native_activations": 0, "actual_native_promotions": 0,
        "actual_native_library_loads": 0, "actual_interpreters_created": 0,
        "actual_threads_started": 0, "actual_subprocesses_started": 0,
        "actual_network_requests": 0, "actual_file_reads": 0,
        "actual_file_writes": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "candidate_qualified_count": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def suite_protocol(row: tuple[Any, ...]) -> dict[str, Any]:
    name, count, source, digest, matrix, reference, seed, route = row
    return {
        "id": name, "case_execution_count": count,
        "source_relative": source, "source_sha256": digest,
        "matrix_sha256": matrix, "reference_records_sha256": reference,
        "published_seed_decimal": None if seed is None else str(seed),
        "unchanged_original_producer_route": route,
    }


def pinned_owner(relative: str, digest: str, size: int) -> dict[str, Any]:
    return {"relative": relative, "sha256": digest, "size_bytes": size}


def protocol_document() -> dict[str, Any]:
    suites = [suite_protocol(row) for row in SUITES]
    families = [{
        "family": family, "owned_source_count": len(owners),
        "actual_v4_campaign_supported": family in {"cpp", "go"},
        "sources": [pinned_owner(path, digest, size)
                    for path, digest, size in owners],
    } for family, owners in OWNED_SOURCES.items()]
    source_paths = [owner[0] for owners in OWNED_SOURCES.values() for owner in owners]
    require(len(suites) == 13
            and sum(item["case_execution_count"] for item in suites) == 31237
            and len({item["id"] for item in suites}) == 13
            and len(families) == 6 and len(source_paths) == 25
            and len(set(source_paths)) == 25 and len(PRIVATE_WAIVERS) == 13,
            "preserve every original suite, private waiver and independent source")
    return {
        "schema": SCHEMA + "-source-freeze", "version": 2,
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
            "named_private_waivers": list(PRIVATE_WAIVERS),
            "original_public_record_count": 152,
            "original_real_debug_skip_count": 1,
            "supplemental_cases_added": False,
        },
        "frozen_original_campaign_v1": {
            "source": pinned_owner(V1_RELATIVE, V1_SHA256, V1_BYTES),
            "protocol": pinned_owner(V1_PROTOCOL_RELATIVE, V1_PROTOCOL_SHA256,
                                     V1_PROTOCOL_BYTES),
            "document": pinned_owner(V1_DOCUMENT_RELATIVE, V1_DOCUMENT_SHA256,
                                     V1_DOCUMENT_BYTES),
            "original_maximum_report_bytes": V1_MAX_REPORT_BYTES,
            "evaluation_and_restoration_reused_without_changes": True,
            "publication_only_replaced_during_explicit_run": True,
        },
        "frozen_original_producer": {
            "source": pinned_owner(PRODUCER_RELATIVE, PRODUCER_SHA256,
                                   PRODUCER_BYTES),
            "protocol": pinned_owner(PRODUCER_PROTOCOL_RELATIVE,
                                     PRODUCER_PROTOCOL_SHA256,
                                     PRODUCER_PROTOCOL_BYTES),
            "document": pinned_owner(PRODUCER_DOCUMENT_RELATIVE,
                                     PRODUCER_DOCUMENT_SHA256,
                                     PRODUCER_DOCUMENT_BYTES),
            "actual_suite_schema": "rebar-owned-six-family-original-p0-producer-v1-actual-original-suite",
            "actual_failure_schema": "rebar-owned-six-family-original-p0-producer-v2-entry-failure",
        },
        "frozen_v4_activation": {
            "source": pinned_owner(V4_RELATIVE, V4_SHA256, V4_BYTES),
            "protocol": pinned_owner(V4_PROTOCOL_RELATIVE, V4_PROTOCOL_SHA256,
                                     V4_PROTOCOL_BYTES),
            "document": pinned_owner(V4_DOCUMENT_RELATIVE, V4_DOCUMENT_SHA256,
                                     V4_DOCUMENT_BYTES),
            "activation_version": 4, "promotion_group_atomic": False,
            "generated_go_header_promoted": False,
        },
        "frozen_go_publication_failure_preservation": {
            "source": pinned_owner(PRESERVATION_RELATIVE,
                                   PRESERVATION_SHA256, PRESERVATION_BYTES),
            "protocol": pinned_owner(PRESERVATION_PROTOCOL_RELATIVE,
                                     PRESERVATION_PROTOCOL_SHA256,
                                     PRESERVATION_PROTOCOL_BYTES),
            "document": pinned_owner(PRESERVATION_DOCUMENT_RELATIVE,
                                     PRESERVATION_DOCUMENT_SHA256,
                                     PRESERVATION_DOCUMENT_BYTES),
            "private_original_owner_count": 5,
            "private_original_owner_total_bytes": 15395,
            "private_original_owners": [
                {"role": role, "relative": name, "sha256": digest,
                 "size_bytes": size, "inode": inode}
                for role, name, digest, size, inode in V1_GO_PRIVATE_OWNERS
            ],
        },
        "suite_count": 13, "case_execution_denominator": 31237,
        "suites": suites, "family_count": 6, "source_owner_count": 25,
        "pairwise_shared_semantic_source_count": 0, "families": families,
        "supported_actual_campaign_families": ["cpp", "go"],
        "historically_runnable_original_families": ["c", "rust", "zig"],
        "independently_source_built_family_count": 5,
        "historical_evidence": {
            "v1_authenticated_distinct_owner_count": 65,
            "additional_committed_original_cpp_failure_owner_count": 2,
            "retained_original_candidate_evidence_owner_count": 67,
            "additional_published_go_infrastructure_failure_owner_count": 2,
            "actual_current_repository_evidence_owner_count": 69,
            "total_distinct_evidence_owner_count": 69,
            "all_historical_versions_actual_compiler_process_count": 169,
            "original_cpp_failure": copy.deepcopy(V1_CPP_FAILURE),
            "original_go_publication_failure": copy.deepcopy(
                V1_GO_PUBLICATION_FAILURE),
            "original_go_v1_failure_policy": {
                "actual_infrastructure_status": "FAIL",
                "actual_candidate_status": "NOT VERIFIED",
                "standard_publication_failure_must_not_be_hidden": True,
                "unpublished_archive_or_receipt_must_not_be_invented": True,
                "published_failure_archive_and_receipt_authenticated": True,
                "all_five_original_raw_owner_bytes_preserved": True,
                "suite_results_or_restoration_route_must_not_be_invented": True,
                "candidate_qualified": False,
            },
        },
        "worker_policy": {
            "reuse_exact_authenticated_v1_original_evaluator": True,
            "one_shell_free_isolated_pinned_python_per_suite": True,
            "required_worker_count": 13,
            "run_all_suites_after_any_mismatch_or_crash": True,
            "preserve_every_original_record_and_failure": True,
            "preserve_complete_raw_stdout_and_stderr": True,
            "maximum_suite_stdout_bytes": MAX_SUITE_STDOUT_BYTES,
            "maximum_suite_stderr_bytes": MAX_SUITE_STDERR_BYTES,
            "duplicate_json_keys_allowed": False,
            "unicode_surrogates_preserved": True,
            "semantic_failure_exit_one_is_not_a_crash": True,
        },
        "activation_and_recovery_policy": {
            "activation_only_under_explicit_run": True,
            "reuse_exact_v1_pinned_v4_activation_and_finally": True,
            "restore_before_publication_in_finally": True,
            "reportless_recovery_after_failed_restore": True,
            "require_verified_canonical_original_restoration": True,
            "generated_go_header_promoted": False,
            "promotion_group_atomic": False,
        },
        "publication_policy": {
            "evidence_relative": EVIDENCE_RELATIVE,
            "canonical_encoder": "json.JSONEncoder.iterencode",
            "canonical_ensure_ascii": True,
            "canonical_allow_nan": False,
            "canonical_sort_keys": True,
            "canonical_separators": [",", ":"],
            "canonical_terminal_newline_count": 1,
            "maximum_uncompressed_report_bytes": MAX_REPORT_BYTES,
            "maximum_compressed_archive_bytes": MAX_ARCHIVE_BYTES,
            "maximum_incremental_chunk_bytes": STREAM_CHUNK_BYTES,
            "complete_report_materialized": False,
            "gzip_single_member": True, "gzip_mtime": 0,
            "gzip_compresslevel": 9,
            "incremental_uncompressed_sha256": True,
            "incremental_compressed_sha256": True,
            "streaming_authenticated_same_inode_readback": True,
            "archive_mode": "0600", "receipt_mode": "0600",
            "exclusive_creation": True, "no_follow": True,
            "separate_archive_and_receipt_inodes": True,
            "archive_file_fsync_required": True,
            "archive_directory_fsync_required": True,
            "receipt_file_fsync_required": True,
            "receipt_directory_fsync_required": True,
            "bounded_failure_output_maximum_bytes": MAX_ERROR_MESSAGE_BYTES,
            "oversized_stream_policy": "FAIL CLOSED WITHOUT TRUNCATION",
            "arbitrary_traceback_fits_guaranteed": False,
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
    require(type(value) is dict
            and canonical(value) == canonical(protocol_document()),
            "reject an altered complete first-party streaming campaign freeze")
    return value


class EffectBoundary:
    """Block every actual candidate, clock, network, process and mutation."""

    def __init__(self, *, source_only: bool) -> None:
        self.source_only = source_only
        self.original: list[tuple[Any, str, Any]] = []
        self.modules: frozenset[str] = frozenset()
        self.blocked = {key: 0 for key in
                        ("file", "process", "clock", "network", "thread",
                         "temporary", "import")}

    def replace(self, owner: Any, name: str, value: Any) -> None:
        if hasattr(owner, name):
            self.original.append((owner, name, getattr(owner, name)))
            setattr(owner, name, value)

    def deny(self, category: str) -> Any:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            self.blocked[category] += 1
            raise SourceOnlyViolation("frozen verification forbids " + category)
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
            original_open = builtins.open

            def read_only_open(path: Any, mode: Any = "r", *args: Any,
                               **kwargs: Any) -> Any:
                require(type(mode) is str
                        and not any(flag in mode for flag in "wax+"),
                        "frozen context may never write")
                return original_open(path, mode, *args, **kwargs)

            self.replace(builtins, "open", read_only_open)
        return self

    def __exit__(self, error_type: Any, error: Any, tb: Any) -> bool:
        for owner, name, original in reversed(self.original):
            setattr(owner, name, original)
        added = set(sys.modules) - self.modules
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in added),
                "verification may not import an actual matching candidate")
        if self.source_only:
            require(frozenset(sys.modules) == self.modules,
                    "source-only verification may not import another module")
        return False


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and os.path.realpath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "use only the pinned isolated no-bytecode stable CPython 3.14.6")


def bounded_add(current: Any, increment: Any, maximum: Any,
                label: str) -> int:
    require(type(current) is int and type(increment) is int
            and type(maximum) is int and 0 <= current <= maximum
            and 0 <= increment <= maximum - current,
            "reject a partial, overflowing, or non-integer " + label)
    return current + increment


class CountingCompressedSink:
    """Count, hash and forward only complete bounded gzip chunks."""

    def __init__(self, write_chunk: Any, maximum: int) -> None:
        require(callable(write_chunk) and type(maximum) is int
                and 0 < maximum <= MAX_ARCHIVE_BYTES,
                "require one bounded complete compressed sink")
        self.write_chunk = write_chunk
        self.maximum = maximum
        self.bytes = 0
        self.write_calls = 0
        self.digest = hashlib.sha256()

    def write(self, chunk: Any) -> int:
        require(type(chunk) is bytes,
                "reject a fabricated or non-bytes gzip chunk")
        if not chunk:
            return 0
        after = bounded_add(self.bytes, len(chunk), self.maximum,
                            "compressed original campaign")
        written = self.write_chunk(chunk)
        require(type(written) is int and written == len(chunk),
                "never discard a partial compressed campaign chunk")
        self.bytes = after
        self.digest.update(chunk)
        self.write_calls += 1
        return written


def stream_canonical_gzip(value: Any, write_chunk: Any, *,
                          maximum_report: int = MAX_REPORT_BYTES,
                          maximum_archive: int = MAX_ARCHIVE_BYTES,
                          chunk_bytes: int = STREAM_CHUNK_BYTES) -> dict[str, Any]:
    require(type(maximum_report) is int and 0 < maximum_report <= MAX_REPORT_BYTES
            and type(maximum_archive) is int
            and 0 < maximum_archive <= MAX_ARCHIVE_BYTES
            and type(chunk_bytes) is int
            and 0 < chunk_bytes <= STREAM_CHUNK_BYTES,
            "require strict, independently bounded complete stream limits")
    plain_digest = hashlib.sha256()
    plain_bytes = 0
    plain_chunks = 0
    sink = CountingCompressedSink(write_chunk, maximum_archive)
    compressor = gzip.GzipFile(filename="", fileobj=sink, mode="wb",
                               compresslevel=9, mtime=0)
    try:
        encoder = json.JSONEncoder(ensure_ascii=True, allow_nan=False,
                                   separators=(",", ":"), sort_keys=True)
        for text in encoder.iterencode(value):
            require(type(text) is str,
                    "canonical encoder must yield complete original text")
            for start in range(0, len(text), chunk_bytes):
                piece = text[start:start + chunk_bytes].encode("ascii", "strict")
                plain_bytes = bounded_add(plain_bytes, len(piece),
                                          maximum_report, "canonical original report")
                plain_digest.update(piece)
                amount = compressor.write(piece)
                require(type(amount) is int and amount == len(piece),
                        "gzip discarded an original canonical JSON fragment")
                plain_chunks += 1
        plain_bytes = bounded_add(plain_bytes, 1, maximum_report,
                                  "canonical original terminal newline")
        plain_digest.update(b"\n")
        require(compressor.write(b"\n") == 1,
                "gzip discarded the sole canonical terminal newline")
        plain_chunks += 1
        compressor.close()
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError, OSError, zlib.error, CampaignError) as error:
        try:
            compressor.close()
        except (TypeError, ValueError, UnicodeError, OverflowError,
                RecursionError, OSError, zlib.error, CampaignError):
            pass
        if isinstance(error, CampaignError):
            raise
        raise CampaignError("reject malformed, nonfinite, or partial canonical stream") from error
    require(plain_bytes > 0 and sink.bytes > 0,
            "never publish an empty canonical or compressed campaign")
    return {
        "uncompressed_sha256": plain_digest.hexdigest(),
        "uncompressed_bytes": plain_bytes,
        "uncompressed_chunk_count": plain_chunks,
        "archive_sha256": sink.digest.hexdigest(),
        "archive_bytes": sink.bytes,
        "archive_write_calls": sink.write_calls,
        "canonical_terminal_newline_count": 1,
        "gzip_mtime": 0, "gzip_single_member": True,
    }


def verify_gzip_chunks(chunks: Iterable[bytes], expected: dict[str, Any], *,
                       maximum_report: int = MAX_REPORT_BYTES,
                       maximum_archive: int = MAX_ARCHIVE_BYTES) -> dict[str, Any]:
    require(type(expected) is dict and 0 < maximum_report <= MAX_REPORT_BYTES
            and 0 < maximum_archive <= MAX_ARCHIVE_BYTES,
            "require exact independently bounded archive expectations")
    compressed_digest = hashlib.sha256()
    plain_digest = hashlib.sha256()
    compressed_bytes = 0
    plain_bytes = 0
    prefix = bytearray()
    inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        for piece in chunks:
            require(type(piece) is bytes and bool(piece),
                    "reject an omitted or empty compressed stream chunk")
            require(not inflater.eof,
                    "reject trailing or concatenated gzip members")
            compressed_bytes = bounded_add(compressed_bytes, len(piece),
                                           maximum_archive, "compressed readback")
            compressed_digest.update(piece)
            if len(prefix) < 10:
                prefix.extend(piece[:10 - len(prefix)])
            pending = piece
            while pending:
                recovered = inflater.decompress(pending, STREAM_CHUNK_BYTES)
                require(not inflater.unused_data,
                        "reject trailing or concatenated gzip members")
                pending = inflater.unconsumed_tail
                if recovered:
                    plain_bytes = bounded_add(plain_bytes, len(recovered),
                                              maximum_report, "decompressed readback")
                    plain_digest.update(recovered)
                if inflater.eof:
                    require(not pending,
                            "reject compressed bytes after the sole gzip member")
                    break
        require(inflater.eof and not inflater.unused_data
                and not inflater.unconsumed_tail,
                "reject truncated, damaged, or multi-member campaign gzip")
        tail = inflater.flush()
        if tail:
            plain_bytes = bounded_add(plain_bytes, len(tail), maximum_report,
                                      "final decompressed readback")
            plain_digest.update(tail)
    except (ValueError, zlib.error, OverflowError, CampaignError) as error:
        if isinstance(error, CampaignError):
            raise
        raise CampaignError("reject corrupt or incomplete streamed gzip") from error
    require(len(prefix) == 10 and bytes(prefix[:4]) == b"\x1f\x8b\x08\x00"
            and bytes(prefix[4:8]) == b"\x00\x00\x00\x00",
            "require a single deterministic zero-mtime gzip member")
    require(compressed_bytes == expected.get("archive_bytes")
            and compressed_digest.hexdigest() == expected.get("archive_sha256")
            and plain_bytes == expected.get("uncompressed_bytes")
            and plain_digest.hexdigest() == expected.get("uncompressed_sha256"),
            "reject lost chunks, fabricated sizes, or changed original bytes")
    return {"status": "PASS", "compressed_bytes": compressed_bytes,
            "uncompressed_bytes": plain_bytes,
            "compressed_sha256": compressed_digest.hexdigest(),
            "uncompressed_sha256": plain_digest.hexdigest(),
            "single_member_verified": True, "gzip_mtime": 0}


def synthetic_stream_fixture() -> dict[str, Any]:
    report = {
        "schema": SCHEMA + "-synthetic-complete-original-report",
        "status": "FAIL", "candidate_family": "go",
        "complete_original_record": "preserve-\ud800-\udfff",
        "complete_candidate_stdout": "x" * 8193,
        "all_mismatches": [{"case": "genuine-loss", "index": 0}],
        "restoration": {"status": "PASS", "all_targets_verified": True},
        "holdout": "NOT OPENED",
    }
    data = bytearray()

    def collect(piece: bytes) -> int:
        data.extend(piece)
        return len(piece)

    manifest = stream_canonical_gzip(report, collect, chunk_bytes=31)
    compressed = bytes(data)
    plain = canonical(report)
    require(manifest["uncompressed_bytes"] == len(plain)
            and manifest["uncompressed_sha256"]
            == hashlib.sha256(plain).hexdigest()
            and manifest["archive_bytes"] == len(compressed)
            and manifest["archive_sha256"]
            == hashlib.sha256(compressed).hexdigest()
            and gzip.decompress(compressed) == plain
            and plain.endswith(b"\n") and not plain.endswith(b"\n\n"),
            "stream every original byte and exactly one canonical newline")
    return {"report": report, "plain": plain, "archive": compressed,
            "manifest": manifest,
            "archive_owner": {"device": 17, "inode": 101, "mode": 0o600,
                              "exclusive_creation": True,
                              "file_fsync_completed": True,
                              "same_inode_readback_verified": True},
            "receipt_owner": {"device": 17, "inode": 102, "mode": 0o600,
                              "exclusive_creation": True,
                              "file_fsync_completed": True,
                              "same_inode_readback_verified": True},
            "receipt_status": "PASS", "candidate_status": "FAIL",
            "archive_directory_fsync_completed": True,
            "receipt_directory_fsync_completed": True}


def validate_synthetic_stream(value: Any) -> dict[str, Any]:
    require(type(value) is dict and type(value.get("report")) is dict
            and type(value.get("plain")) is bytes
            and type(value.get("archive")) is bytes
            and type(value.get("manifest")) is dict
            and value["plain"] == canonical(value["report"])
            and value["report"].get("complete_original_record")
            == "preserve-\ud800-\udfff"
            and value["report"].get("all_mismatches")
            == [{"case": "genuine-loss", "index": 0}]
            and value["report"].get("restoration", {}).get("status") == "PASS"
            and value["report"].get("holdout") == "NOT OPENED"
            and value.get("receipt_status") == "PASS"
            and value.get("candidate_status") == "FAIL"
            and value.get("archive_directory_fsync_completed") is True
            and value.get("receipt_directory_fsync_completed") is True,
            "reject a lost genuine failure, holdout, restoration, or canonical byte")
    archive = value.get("archive_owner")
    receipt = value.get("receipt_owner")
    require(type(archive) is dict and type(receipt) is dict
            and archive.get("device") == receipt.get("device") == 17
            and type(archive.get("inode")) is int
            and type(receipt.get("inode")) is int
            and archive["inode"] != receipt["inode"]
            and all(owner.get("mode") == 0o600
                    and owner.get("exclusive_creation") is True
                    and owner.get("file_fsync_completed") is True
                    and owner.get("same_inode_readback_verified") is True
                    for owner in (archive, receipt)),
            "reject aliased, replaced, non-private or unsynchronized owners")
    chunks = (value["archive"][index:index + 23]
              for index in range(0, len(value["archive"]), 23))
    verify_gzip_chunks(chunks, value["manifest"])
    return value


def synthetic_preserved_go_failure() -> dict[str, Any]:
    return {
        "synthetic_only": True,
        "infrastructure_status": "FAIL",
        "candidate_status": "NOT VERIFIED",
        "candidate_qualified": False,
        "receipt_status": "PASS",
        "receipt_status_meaning": "EVIDENCE PUBLICATION ONLY",
        "retained_original_candidate_evidence_owner_count": 67,
        "actual_current_repository_evidence_owner_count": 69,
        "preservation_source": pinned_owner(
            PRESERVATION_RELATIVE, PRESERVATION_SHA256, PRESERVATION_BYTES),
        "preservation_protocol": pinned_owner(
            PRESERVATION_PROTOCOL_RELATIVE, PRESERVATION_PROTOCOL_SHA256,
            PRESERVATION_PROTOCOL_BYTES),
        "preservation_document": pinned_owner(
            PRESERVATION_DOCUMENT_RELATIVE, PRESERVATION_DOCUMENT_SHA256,
            PRESERVATION_DOCUMENT_BYTES),
        "failure": copy.deepcopy(V1_GO_PUBLICATION_FAILURE),
        "archive_owner": {
            "device": 17, "inode": 201, "mode": 0o600,
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
        },
        "receipt_owner": {
            "device": 17, "inode": 202, "mode": 0o600,
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
        },
        "original_private_owners": [
            {"role": role, "relative": name, "sha256": digest,
             "size_bytes": size, "inode": inode}
            for role, name, digest, size, inode in V1_GO_PRIVATE_OWNERS
        ],
        "actual_original_report_bytes": "NOT RECORDED",
        "actual_restoration_route": "NOT RECORDED",
        "actual_suite_statuses": "NOT RECORDED",
        "actual_mismatch_count": "NOT RECORDED",
    }


def validate_synthetic_preserved_go_failure(value: Any) -> dict[str, Any]:
    require(type(value) is dict
            and canonical(value) == canonical(synthetic_preserved_go_failure()),
            "reject omitted, forged, reordered, guessed or falsely passing Go failure")
    archive, receipt = value["archive_owner"], value["receipt_owner"]
    require(archive["inode"] != receipt["inode"]
            and all(owner["mode"] == 0o600
                    and owner["exclusive_creation"] is True
                    and owner["same_inode_readback_verified"] is True
                    and owner["file_fsync_completed"] is True
                    for owner in (archive, receipt))
            and value["infrastructure_status"] == "FAIL"
            and value["candidate_status"] == "NOT VERIFIED"
            and value["candidate_qualified"] is False
            and value["receipt_status"] == "PASS"
            and value["retained_original_candidate_evidence_owner_count"] == 67
            and value["actual_current_repository_evidence_owner_count"] == 69
            and len(value["original_private_owners"]) == 5,
            "never promote Go infrastructure evidence into candidate correctness")
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
            except (CampaignError, TypeError, ValueError, KeyError,
                    OverflowError, zlib.error):
                rejected += 1
                return
            raise CampaignError("a hostile complete streaming control was accepted")

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
            for key in ("family", "owned_source_count",
                        "actual_v4_campaign_supported"):
                attack = copy.deepcopy(frozen)
                old = attack["families"][index][key]
                attack["families"][index][key] = (
                    not old if type(old) is bool
                    else old + 1 if type(old) is int else old + "-foreign"
                )
                reject(attack)
            for owner_index, owner in enumerate(family["sources"]):
                for key in ("relative", "sha256", "size_bytes"):
                    attack = copy.deepcopy(frozen)
                    old = attack["families"][index]["sources"][owner_index][key]
                    attack["families"][index]["sources"][owner_index][key] = (
                        old + 1 if type(old) is int else old + "-wrapper"
                    )
                    reject(attack)
            accepted += 1
        for group in ("phase_one", "frozen_original_campaign_v1",
                      "frozen_original_producer", "frozen_v4_activation",
                      "frozen_go_publication_failure_preservation",
                      "historical_evidence", "worker_policy",
                      "activation_and_recovery_policy", "publication_policy",
                      "independence_policy", "verification_effects"):
            for key, old in frozen[group].items():
                attack = copy.deepcopy(frozen)
                attack[group][key] = (
                    not old if type(old) is bool
                    else old + 1 if type(old) is int
                    else old + "-changed" if type(old) is str
                    else {} if type(old) is dict
                    else old[:-1] if type(old) is list else "changed"
                )
                reject(attack)
            accepted += 1
        fixture = synthetic_stream_fixture()
        validate_synthetic_stream(fixture)
        accepted += 1
        preserved = synthetic_preserved_go_failure()
        validate_synthetic_preserved_go_failure(preserved)
        accepted += 1
        for key, old in preserved.items():
            attack = copy.deepcopy(preserved)
            attack[key] = (
                not old if type(old) is bool
                else old + 1 if type(old) is int
                else old + "-forged" if type(old) is str
                else {} if type(old) is dict
                else old[:-1] if type(old) is list
                else "forged"
            )
            reject(attack, validate_synthetic_preserved_go_failure)
        for index, owner in enumerate(preserved["original_private_owners"]):
            for key, old in owner.items():
                attack = copy.deepcopy(preserved)
                attack["original_private_owners"][index][key] = (
                    old + 1 if type(old) is int else old + "-forged"
                )
                reject(attack, validate_synthetic_preserved_go_failure)
        for owner_name in ("archive_owner", "receipt_owner"):
            for key, old in preserved[owner_name].items():
                attack = copy.deepcopy(preserved)
                attack[owner_name][key] = (
                    not old if type(old) is bool
                    else preserved["archive_owner"]["inode"]
                    if owner_name == "receipt_owner" and key == "inode"
                    else 0o644 if key == "mode" else old + 1
                )
                reject(attack, validate_synthetic_preserved_go_failure)
        for key, old in preserved["failure"].items():
            attack = copy.deepcopy(preserved)
            attack["failure"][key] = (
                not old if type(old) is bool
                else old + 1 if type(old) is int else old + "-forged"
            )
            reject(attack, validate_synthetic_preserved_go_failure)
        for chunk_size in (1, 2, 7, 17, 23, 31, 63, 64, 127, 1024):
            archive = fixture["archive"]
            verify_gzip_chunks(
                (archive[index:index + chunk_size]
                 for index in range(0, len(archive), chunk_size)),
                fixture["manifest"])
            accepted += 1
        for key in ("plain", "archive", "manifest", "report",
                    "candidate_status", "receipt_status",
                    "archive_directory_fsync_completed",
                    "receipt_directory_fsync_completed"):
            attack = copy.deepcopy(fixture)
            old = attack[key]
            attack[key] = (not old if type(old) is bool
                           else old + b"forged" if type(old) is bytes
                           else old + "-forged" if type(old) is str
                           else {})
            reject(attack, validate_synthetic_stream)
        for name in ("archive_owner", "receipt_owner"):
            for key in ("device", "inode", "mode", "exclusive_creation",
                        "file_fsync_completed", "same_inode_readback_verified"):
                attack = copy.deepcopy(fixture)
                old = attack[name][key]
                attack[name][key] = (
                    not old if type(old) is bool
                    else fixture["archive_owner"]["inode"]
                    if name == "receipt_owner" and key == "inode"
                    else 0o644 if key == "mode" else old + 1
                )
                reject(attack, validate_synthetic_stream)
        for key in ("uncompressed_sha256", "archive_sha256",
                    "uncompressed_bytes", "archive_bytes"):
            attack = copy.deepcopy(fixture)
            old = attack["manifest"][key]
            attack["manifest"][key] = old + 1 if type(old) is int else old + "0"
            reject(attack, validate_synthetic_stream)
        original_archive = fixture["archive"]
        for damaged in (original_archive[:-1], original_archive[1:],
                        original_archive + b"foreign",
                        original_archive + original_archive,
                        original_archive[:10] + b"x" + original_archive[11:],
                        original_archive[:4] + b"\x01" + original_archive[5:]):
            attack = copy.deepcopy(fixture)
            attack["archive"] = damaged
            reject(attack, validate_synthetic_stream)
        for lost in (1, 7, 23, len(original_archive) // 2):
            attack = copy.deepcopy(fixture)
            attack["archive"] = original_archive[:lost] + original_archive[lost + 1:]
            reject(attack, validate_synthetic_stream)
        require(bounded_add(V1_MAX_REPORT_BYTES, 1, MAX_REPORT_BYTES,
                            "original report") == V1_MAX_REPORT_BYTES + 1,
                "the old 256 MiB boundary must be streamable without allocation")
        accepted += 1
        for old, amount, cap in (
            (V1_MAX_REPORT_BYTES, 1, V1_MAX_REPORT_BYTES),
            (MAX_REPORT_BYTES, 1, MAX_REPORT_BYTES),
            (MAX_ARCHIVE_BYTES, 1, MAX_ARCHIVE_BYTES),
            (-1, 1, MAX_REPORT_BYTES), (0, -1, MAX_REPORT_BYTES),
            (True, 1, MAX_REPORT_BYTES), (0, True, MAX_REPORT_BYTES),
        ):
            try:
                bounded_add(old, amount, cap, "synthetic overflow")
            except CampaignError:
                rejected += 1
            else:
                raise CampaignError("a hostile streaming bound was accepted")
        for bad in (float("nan"), float("inf"), -float("inf")):
            try:
                stream_canonical_gzip({"bad": bad}, lambda part: len(part))
            except CampaignError:
                rejected += 1
            else:
                raise CampaignError("a nonfinite streaming report was accepted")
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
                raise CampaignError("a source-only real-effect guard was bypassed")
        require(accepted >= 35 and rejected >= 245
                and all(value > 0 for value in boundary.blocked.values()),
                "exercise all original sources, suites, stream attacks and effect walls")
        probes = dict(boundary.blocked)
    return {
        "schema": SCHEMA + "-source-only-self-test", "status": "PASS",
        "source_only": True, "synthetic_only": True,
        "accepted_synthetic_controls": accepted,
        "rejected_hostile_controls": rejected,
        "blocked_effect_probes": probes,
        "suite_count": 13, "case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "source_family_count": 6, "source_owner_count": 25,
        "supported_actual_campaign_family_count": 2,
        "historically_runnable_original_family_count": 3,
        "independently_source_built_family_count": 5,
        "retained_original_candidate_evidence_owner_count": 67,
        "actual_current_repository_evidence_owner_count": 69,
        "additional_go_publication_failure_evidence_owner_count": 2,
        "total_distinct_historical_evidence_owner_count": 69,
        "preserved_go_infrastructure_status": "FAIL",
        "preserved_go_candidate_status": "NOT VERIFIED",
        "preserved_go_original_private_owner_count": 5,
        "all_historical_versions_actual_compiler_process_count": 169,
        "maximum_uncompressed_report_bytes": MAX_REPORT_BYTES,
        "maximum_compressed_archive_bytes": MAX_ARCHIVE_BYTES,
        "frozen_contract": protocol_document(),
        **zero_effects(),
    }


def read_owned(relative: str, digest: str, *, maximum: int,
               exact_size: int | None = None,
               owner_only: bool = False) -> tuple[bytes, dict[str, Any]]:
    require(type(relative) is str and bool(relative) and "\x00" not in relative,
            "require one exact bounded first-party relative owner")
    path = Path(relative)
    require(not path.is_absolute() and str(path) == relative
            and all(part not in {"", ".", ".."} for part in path.parts),
            "reject absolute, broad, parent or ambiguous evidence paths")
    checked_digest(digest, relative)
    target = ROOT / path
    require(os.path.abspath(str(target)) == str(target)
            and os.path.realpath(str(target)) == str(target),
            "reject a redirected frozen owner or symlinked ancestor")
    descriptor = os.open(str(target), os.O_RDONLY
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        first = os.fstat(descriptor)
        visible = os.stat(str(target), follow_symlinks=False)
        require(stat.S_ISREG(first.st_mode)
                and (first.st_dev, first.st_ino, first.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and 0 < first.st_size <= maximum
                and (exact_size is None or first.st_size == exact_size)
                and (not owner_only or stat.S_IMODE(first.st_mode) == 0o600),
                "reject a non-private, oversized, incomplete or substituted owner")
        pieces: list[bytes] = []
        remaining = first.st_size
        while remaining:
            piece = os.read(descriptor, min(remaining, STREAM_CHUNK_BYTES))
            require(type(piece) is bytes and bool(piece),
                    "reject a lost frozen source or historical evidence chunk")
            pieces.append(piece)
            remaining -= len(piece)
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        named = os.stat(str(target), follow_symlinks=False)
        require((first.st_dev, first.st_ino, first.st_size,
                 first.st_mtime_ns, first.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (after.st_dev, after.st_ino, after.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and hashlib.sha256(raw).hexdigest() == digest,
                "reject an owner changed during authenticated readback")
        return raw, {
            "relative": relative, "sha256": digest,
            "size_bytes": len(raw), "device": after.st_dev,
            "inode": after.st_ino, "mode": stat.S_IMODE(after.st_mode),
        }
    finally:
        os.close(descriptor)


def frozen_module(relative: str, digest: str, size: int) -> Any:
    _, first = read_owned(relative, digest, maximum=MAX_SOURCE_BYTES,
                          exact_size=size)
    name = "_rebar_owned_original_p0_campaign_v2_frozen_" + digest[:24]
    existing = sys.modules.get(name)
    if existing is None:
        spec = importlib.util.spec_from_file_location(name, str(ROOT / relative))
        require(spec is not None and spec.loader is not None,
                "load only the exact pinned first-party original evaluator")
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
    require((first["device"], first["inode"])
            == (final["device"], final["inode"])
            and os.path.abspath(str(getattr(module, "__file__", "")))
            == str(ROOT / relative)
            and os.path.realpath(str(module.__file__)) == str(ROOT / relative),
            "reject a first-party frozen source replaced during import")
    return module


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    verify_runtime()
    with EffectBoundary(source_only=False):
        _, source = read_owned(SOURCE_RELATIVE, options.source_sha256,
                              maximum=MAX_SOURCE_BYTES)
        _, protocol = read_owned(PROTOCOL_RELATIVE, options.protocol_sha256,
                                maximum=MAX_SOURCE_BYTES)
        machine_raw, document = read_owned(DOCUMENT_RELATIVE,
                                           options.document_sha256,
                                           maximum=MAX_SOURCE_BYTES)
        try:
            decoded = json.loads(machine_raw.decode("ascii", "strict"))
        except (ValueError, UnicodeError, RecursionError) as error:
            raise CampaignError("reject malformed streaming campaign freeze") from error
        require(canonical(decoded) == machine_raw,
                "require the complete canonical streaming campaign freeze")
        validate_protocol_document(decoded)
        v1 = frozen_module(V1_RELATIVE, V1_SHA256, V1_BYTES)
        v1_context = v1.verify_frozen_context(argparse.Namespace(
            source_sha256=V1_SHA256,
            protocol_sha256=V1_PROTOCOL_SHA256,
            document_sha256=V1_DOCUMENT_SHA256,
        ))
        require(type(v1_context) is dict
                and v1_context.get("status") == "PASS"
                and v1_context.get("read_only") is True
                and v1_context.get("suite_count") == 13
                and v1_context.get("case_execution_denominator") == 31237
                and v1_context.get("named_private_waiver_count") == 13
                and v1_context.get("source_family_count") == 6
                and v1_context.get("source_owner_count") == 25
                and v1_context.get("total_distinct_historical_evidence_owner_count") == 65
                and v1_context.get("all_historical_versions_actual_compiler_process_count") == 169
                and tuple(v1.SUITES) == SUITES
                and v1.OWNED_SOURCES == OWNED_SOURCES
                and v1.PRODUCER_SHA256 == PRODUCER_SHA256
                and v1.V4_SHA256 == V4_SHA256,
                "preserve the independently authenticated complete V1 original evaluator")
        for key, value in zero_effects().items():
            if key in v1_context:
                require(type(v1_context[key]) is type(value)
                        and v1_context[key] == value,
                        "the frozen original evaluator caused an effect: " + key)
        _, cpp_archive = read_owned(
            V1_CPP_FAILURE["archive_relative"], V1_CPP_FAILURE["archive_sha256"],
            maximum=MAX_SOURCE_BYTES,
            exact_size=V1_CPP_FAILURE["archive_bytes"], owner_only=True)
        receipt_raw, cpp_receipt = read_owned(
            V1_CPP_FAILURE["receipt_relative"], V1_CPP_FAILURE["receipt_sha256"],
            maximum=MAX_SOURCE_BYTES,
            exact_size=V1_CPP_FAILURE["receipt_bytes"], owner_only=True)
        receipt = v1.decode_document(receipt_raw,
                                     "actual complete V1 C++ failure receipt",
                                     maximum=MAX_SOURCE_BYTES)
        archive_in_receipt = receipt.get("archive")
        require(type(archive_in_receipt) is dict
                and receipt.get("schema")
                == v1.SCHEMA + "-durable-publication-receipt"
                and receipt.get("status") == "PASS"
                and receipt.get("candidate_status") == "FAIL"
                and receipt.get("candidate_family") == "cpp"
                and receipt.get("label") == V1_CPP_FAILURE["label"]
                and receipt.get("suite_count") == 13
                and receipt.get("completed_suite_count") == 13
                and receipt.get("case_execution_denominator") == 31237
                and receipt.get("uncompressed_bytes")
                == V1_CPP_FAILURE["uncompressed_bytes"]
                and receipt.get("uncompressed_sha256")
                == V1_CPP_FAILURE["uncompressed_sha256"]
                and receipt.get("failure_preserved") is True
                and receipt.get("all_mismatches_crashes_and_timeouts_preserved") is True
                and receipt.get("restoration", {}).get("status") == "PASS"
                and receipt.get("hidden_cases_read") == 0
                and receipt.get("benchmark_files_read") == 0
                and receipt.get("clock_samples") == 0
                and receipt.get("timing_trials_run") == 0
                and receipt.get("holdout") == "NOT OPENED"
                and archive_in_receipt.get("sha256")
                == V1_CPP_FAILURE["archive_sha256"]
                and archive_in_receipt.get("size_bytes")
                == V1_CPP_FAILURE["archive_bytes"]
                and archive_in_receipt.get("mode") == 0o600
                and archive_in_receipt.get("file_fsync_completed") is True
                and archive_in_receipt.get("same_inode_readback_verified") is True
                and (cpp_archive["device"], cpp_archive["inode"])
                == (archive_in_receipt.get("device"),
                    archive_in_receipt.get("inode"))
                and (cpp_archive["device"], cpp_archive["inode"])
                != (cpp_receipt["device"], cpp_receipt["inode"]),
                "authenticate, preserve and never qualify the actual V1 C++ failure")
        original_owners = v1_context.get("actual_passing_source_build_owners")
        require(type(original_owners) is dict
                and all((owner.get("device"), owner.get("inode"))
                        not in {(cpp_archive["device"], cpp_archive["inode"]),
                                (cpp_receipt["device"], cpp_receipt["inode"])}
                        for family in original_owners.values()
                        for owner in family.values()),
                "reject a C++ campaign owner aliased with actual original build evidence")
        preservation = frozen_module(
            PRESERVATION_RELATIVE, PRESERVATION_SHA256, PRESERVATION_BYTES)
        preservation_options = preservation.parse_arguments([
            "--verify-frozen-context",
            "--source-sha256", PRESERVATION_SHA256,
            "--protocol-sha256", PRESERVATION_PROTOCOL_SHA256,
            "--contract-sha256", PRESERVATION_DOCUMENT_SHA256,
        ])
        preservation_context, private_bundle, _ = preservation.collect_context(
            preservation_options)
        require(type(preservation_context) is dict
                and preservation_context.get("status") == "PASS"
                and preservation_context.get("read_only") is True
                and preservation_context.get("original_suite_count") == 13
                and preservation_context.get("original_case_execution_denominator") == 31237
                and preservation_context.get("inherited_historical_evidence_owner_count") == 65
                and preservation_context.get("retained_cpp_evidence_owner_count") == 2
                and preservation_context.get("total_retained_repository_evidence_owner_count") == 67
                and preservation_context.get("historical_compiler_process_count") == 169
                and tuple(preservation.PRIVATE_OWNERS) == V1_GO_PRIVATE_OWNERS
                and type(private_bundle) is dict
                and len(private_bundle) == 5,
                "authenticate the exact original 67-owner Go failure-preservation graph")
        for key, value in zero_effects().items():
            if key in preservation_context:
                require(type(preservation_context[key]) is type(value)
                        and preservation_context[key] == value,
                        "failure-preservation context caused an effect: " + key)
        failure_bytes, go_archive = read_owned(
            V1_GO_PUBLICATION_FAILURE["archive_relative"],
            V1_GO_PUBLICATION_FAILURE["archive_sha256"],
            maximum=MAX_SOURCE_BYTES,
            exact_size=V1_GO_PUBLICATION_FAILURE["archive_bytes"],
            owner_only=True)
        go_receipt_bytes, go_receipt = read_owned(
            V1_GO_PUBLICATION_FAILURE["receipt_relative"],
            V1_GO_PUBLICATION_FAILURE["receipt_sha256"],
            maximum=MAX_SOURCE_BYTES,
            exact_size=V1_GO_PUBLICATION_FAILURE["receipt_bytes"],
            owner_only=True)
        inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
        try:
            failure_plain = inflater.decompress(
                failure_bytes, preservation.MAX_PRESERVATION_REPORT_BYTES + 1)
        except (ValueError, zlib.error) as error:
            raise CampaignError(
                "reject corrupt or truncated authentic Go infrastructure evidence"
            ) from error
        require(inflater.eof and not inflater.unused_data
                and not inflater.unconsumed_tail
                and 0 < len(failure_plain)
                <= preservation.MAX_PRESERVATION_REPORT_BYTES,
                "reject partial, oversized or multi-member Go failure evidence")
        failure_report = preservation.decode_document(
            failure_plain, "complete actual published original Go failure",
            maximum=preservation.MAX_PRESERVATION_REPORT_BYTES)
        preservation.validate_failure_report(failure_report, preservation_options)
        exact_plain, exact_archive = preservation.deterministic_archive(
            failure_report, preservation_options)
        require(exact_plain == failure_plain and exact_archive == failure_bytes
                and hashlib.sha256(failure_plain).hexdigest()
                == V1_GO_PUBLICATION_FAILURE["uncompressed_sha256"]
                and len(failure_plain)
                == V1_GO_PUBLICATION_FAILURE["uncompressed_bytes"],
                "require the exact deterministic complete actual Go failure bytes")
        embedded = preservation.restore_embedded_owners(
            failure_report.get("original_activation_owners"))
        require(set(embedded) == {row[0] for row in V1_GO_PRIVATE_OWNERS}
                and all(
                    type(embedded[role].get("raw")) is bytes
                    and embedded[role]["raw"] == private_bundle[role]["raw"]
                    and hashlib.sha256(embedded[role]["raw"]).hexdigest() == digest
                    and len(embedded[role]["raw"]) == size
                    and embedded[role].get("inode") == inode
                    for role, _, digest, size, inode in V1_GO_PRIVATE_OWNERS
                ),
                "preserve all five exact genuine original private Go owner bytes")
        go_publication_receipt = preservation.decode_document(
            go_receipt_bytes, "genuine durable Go failure-only receipt",
            maximum=preservation.MAX_PRESERVATION_REPORT_BYTES)
        failure_archive_owner = go_publication_receipt.get("archive")
        require(type(failure_archive_owner) is dict
                and go_publication_receipt.get("schema")
                == preservation.SCHEMA + "-durable-evidence-publication-receipt"
                and go_publication_receipt.get("status") == "PASS"
                and go_publication_receipt.get("receipt_status_meaning")
                == "EVIDENCE PUBLICATION ONLY"
                and go_publication_receipt.get("infrastructure_status") == "FAIL"
                and go_publication_receipt.get("candidate_status") == "NOT VERIFIED"
                and go_publication_receipt.get("candidate_qualified") is False
                and go_publication_receipt.get("candidate_family") == "go"
                and go_publication_receipt.get("candidate_label") == "phase2-v1"
                and go_publication_receipt.get("preservation_source_sha256")
                == PRESERVATION_SHA256
                and go_publication_receipt.get("preservation_protocol_sha256")
                == PRESERVATION_PROTOCOL_SHA256
                and go_publication_receipt.get("preservation_contract_sha256")
                == PRESERVATION_DOCUMENT_SHA256
                and go_publication_receipt.get("original_campaign_source_sha256")
                == V1_SHA256
                and go_publication_receipt.get("original_campaign_protocol_sha256")
                == V1_PROTOCOL_SHA256
                and go_publication_receipt.get("original_campaign_contract_sha256")
                == V1_DOCUMENT_SHA256
                and go_publication_receipt.get("retained_repository_evidence_owner_count")
                == 67
                and go_publication_receipt.get("embedded_private_owner_count") == 5
                and go_publication_receipt.get("embedded_private_owner_total_original_bytes")
                == 15395
                and go_publication_receipt.get("uncompressed_bytes")
                == V1_GO_PUBLICATION_FAILURE["uncompressed_bytes"]
                and go_publication_receipt.get("uncompressed_sha256")
                == V1_GO_PUBLICATION_FAILURE["uncompressed_sha256"]
                and go_publication_receipt.get("original_campaign_publication_failure_preserved")
                is True
                and go_publication_receipt.get("all_five_complete_original_owner_bytes_preserved")
                is True
                and go_publication_receipt.get("publication_receipt_is_candidate_qualification")
                is False
                and all(go_publication_receipt.get(key) == "NOT RECORDED"
                        for key in ("actual_original_report_bytes",
                                    "actual_restoration_route",
                                    "actual_suite_statuses",
                                    "actual_mismatch_count"))
                and failure_archive_owner.get("sha256")
                == V1_GO_PUBLICATION_FAILURE["archive_sha256"]
                and failure_archive_owner.get("size_bytes")
                == V1_GO_PUBLICATION_FAILURE["archive_bytes"]
                and failure_archive_owner.get("mode") == 0o600
                and failure_archive_owner.get("exclusive_creation") is True
                and failure_archive_owner.get("file_fsync_completed") is True
                and failure_archive_owner.get("same_inode_readback_verified") is True
                and (failure_archive_owner.get("device"),
                     failure_archive_owner.get("inode"))
                == (go_archive["device"], go_archive["inode"])
                and go_publication_receipt.get("archive_directory_fsync_completed")
                is True,
                "never relabel an authentic Go infrastructure failure as correctness")
        evidence_identities = {
            (cpp_archive["device"], cpp_archive["inode"]),
            (cpp_receipt["device"], cpp_receipt["inode"]),
            (go_archive["device"], go_archive["inode"]),
            (go_receipt["device"], go_receipt["inode"]),
        }
        require(len(evidence_identities) == 4
                and all((owner.get("device"), owner.get("inode"))
                        not in evidence_identities
                        for family in original_owners.values()
                        for owner in family.values()),
                "require four genuinely distinct historical failure-evidence owners")
    return {
        "schema": SCHEMA + "-read-only-frozen-context", "status": "PASS",
        "read_only": True, "source": source, "protocol": protocol,
        "document": document,
        "frozen_original_campaign_v1": {
            "source": pinned_owner(V1_RELATIVE, V1_SHA256, V1_BYTES),
            "protocol": pinned_owner(V1_PROTOCOL_RELATIVE,
                                     V1_PROTOCOL_SHA256, V1_PROTOCOL_BYTES),
            "document": pinned_owner(V1_DOCUMENT_RELATIVE,
                                     V1_DOCUMENT_SHA256, V1_DOCUMENT_BYTES),
        },
        "frozen_original_producer": protocol_document()["frozen_original_producer"],
        "frozen_v4_activation": protocol_document()["frozen_v4_activation"],
        "frozen_go_publication_failure_preservation": protocol_document()[
            "frozen_go_publication_failure_preservation"],
        "preserved_actual_v1_cpp_failure": {
            **copy.deepcopy(V1_CPP_FAILURE),
            "archive_owner": cpp_archive, "receipt_owner": cpp_receipt,
            "restoration_verified": True,
        },
        "preserved_actual_v1_go_publication_failure": {
            **copy.deepcopy(V1_GO_PUBLICATION_FAILURE),
            "archive_owner": go_archive,
            "receipt_owner": go_receipt,
            "original_private_owners": [
                {key: value for key, value in embedded[role].items()
                 if key not in {"raw", "document"}}
                for role, *_ in V1_GO_PRIVATE_OWNERS
            ],
            "all_five_original_raw_owner_bytes_verified": True,
            "preservation_context_status": "PASS",
            "candidate_qualified": False,
        },
        "suite_count": 13, "case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "source_family_count": 6, "source_owner_count": 25,
        "pairwise_shared_semantic_source_count": 0,
        "supported_actual_campaign_families": ["cpp", "go"],
        "historically_runnable_original_family_count": 3,
        "independently_source_built_family_count": 5,
        "inherited_distinct_v1_evidence_owner_count": 65,
        "additional_authenticated_cpp_failure_owner_count": 2,
        "retained_original_candidate_evidence_owner_count": 67,
        "additional_authenticated_go_publication_failure_owner_count": 2,
        "actual_current_repository_evidence_owner_count": 69,
        "total_distinct_historical_evidence_owner_count": 69,
        "all_historical_versions_actual_compiler_process_count": 169,
        "maximum_uncompressed_report_bytes": MAX_REPORT_BYTES,
        "maximum_compressed_archive_bytes": MAX_ARCHIVE_BYTES,
        "actual_v4_activations": "NOT RUN",
        **zero_effects(),
    }


def evidence_names(family: str, label: str, *, failure: bool) -> tuple[str, str]:
    require(family in {"cpp", "go"} and type(failure) is bool,
            "publish only a complete genuinely source-built original campaign")
    stem = "owned-six-family-original-p0-campaign-v2-" + family + "-" + checked_label(label)
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def open_evidence_directory() -> int:
    root = ROOT / EVIDENCE_RELATIVE
    require(os.path.abspath(str(root)) == str(root)
            and os.path.realpath(str(root)) == str(root),
            "reject a redirected or symlinked historical evidence directory")
    descriptor = os.open(str(root), os.O_RDONLY
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0)
                         | getattr(os, "O_DIRECTORY", 0))
    try:
        owner = os.fstat(descriptor)
        visible = os.stat(str(root), follow_symlinks=False)
        require(stat.S_ISDIR(owner.st_mode)
                and owner.st_uid == os.geteuid()
                and (owner.st_dev, owner.st_ino)
                == (visible.st_dev, visible.st_ino),
                "require the exact authenticated owner-only evidence directory")
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def ensure_fresh_evidence(family: str, label: str) -> None:
    descriptor = open_evidence_directory()
    try:
        for failed in (False, True):
            for name in evidence_names(family, label, failure=failed):
                try:
                    os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise CampaignError("never replace an original campaign owner: " + name)
    finally:
        os.close(descriptor)


def write_complete_chunk(descriptor: int, piece: bytes) -> int:
    require(type(piece) is bytes and bool(piece),
            "write only one complete compressed original chunk")
    offset = 0
    while offset < len(piece):
        written = os.write(descriptor, piece[offset:])
        require(type(written) is int and written > 0,
                "reject a short or failed durable compressed evidence write")
        offset += written
    return offset


def archive_read_chunks(descriptor: int) -> Iterable[bytes]:
    while True:
        piece = os.read(descriptor, STREAM_CHUNK_BYTES)
        require(type(piece) is bytes,
                "reject a malformed authenticated evidence read")
        if not piece:
            return
        yield piece


def write_streamed_archive(report: dict[str, Any], name: str,
                           directory: int) -> tuple[dict[str, Any], dict[str, Any]]:
    require(type(name) is str and bool(name) and "/" not in name,
            "write exactly one fresh bounded archive basename")
    descriptor: int | None = None
    reader: int | None = None
    created: tuple[int, int] | None = None
    complete = False
    try:
        descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                             | getattr(os, "O_CLOEXEC", 0)
                             | getattr(os, "O_NOFOLLOW", 0),
                             0o600, dir_fd=directory)
        first = os.fstat(descriptor)
        require(stat.S_ISREG(first.st_mode)
                and stat.S_IMODE(first.st_mode) == 0o600
                and first.st_uid == os.geteuid() and first.st_nlink == 1,
                "require one exclusive owner-only regular archive inode")
        created = (first.st_dev, first.st_ino)
        manifest = stream_canonical_gzip(
            report, lambda piece: write_complete_chunk(descriptor, piece))
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((after.st_dev, after.st_ino) == created
                and after.st_size == manifest["archive_bytes"]
                and stat.S_IMODE(after.st_mode) == 0o600
                and after.st_nlink == 1,
                "reject a partial, linked or substituted compressed archive")
        os.close(descriptor)
        descriptor = None
        reader = os.open(name, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
        before_read = os.fstat(reader)
        visible = os.stat(name, dir_fd=directory, follow_symlinks=False)
        require((before_read.st_dev, before_read.st_ino, before_read.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and (before_read.st_dev, before_read.st_ino) == created
                and before_read.st_size == manifest["archive_bytes"]
                and stat.S_IMODE(before_read.st_mode) == 0o600
                and before_read.st_nlink == 1,
                "reject an archive swapped before authenticated streaming readback")
        verified = verify_gzip_chunks(archive_read_chunks(reader), manifest)
        after_read = os.fstat(reader)
        final_visible = os.stat(name, dir_fd=directory, follow_symlinks=False)
        require((before_read.st_dev, before_read.st_ino,
                 before_read.st_size, before_read.st_mtime_ns,
                 before_read.st_ctime_ns)
                == (after_read.st_dev, after_read.st_ino,
                    after_read.st_size, after_read.st_mtime_ns,
                    after_read.st_ctime_ns)
                and (after_read.st_dev, after_read.st_ino, after_read.st_size)
                == (final_visible.st_dev, final_visible.st_ino,
                    final_visible.st_size),
                "reject archive bytes or inode changed during full readback")
        os.close(reader)
        reader = None
        os.fsync(directory)
        complete = True
        owner = {
            "path": str(ROOT / EVIDENCE_RELATIVE / name),
            "relative": name, "sha256": manifest["archive_sha256"],
            "size_bytes": manifest["archive_bytes"],
            "device": after_read.st_dev, "inode": after_read.st_ino,
            "mode": stat.S_IMODE(after_read.st_mode),
            "exclusive_creation": True, "same_inode_readback_verified": True,
            "file_fsync_completed": True, "directory_fsync_completed": True,
            "write_calls": manifest["archive_write_calls"],
            "streaming_readback_verified": verified["status"] == "PASS",
        }
        return owner, manifest
    finally:
        if reader is not None:
            os.close(reader)
        if descriptor is not None:
            os.close(descriptor)
        if created is not None and not complete:
            try:
                remaining = os.stat(name, dir_fd=directory,
                                    follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                require((remaining.st_dev, remaining.st_ino) == created
                        and stat.S_ISREG(remaining.st_mode)
                        and remaining.st_nlink == 1,
                        "never remove a substituted or shared partial archive")
                os.unlink(name, dir_fd=directory)
                os.fsync(directory)


def validate_restored_v1_report(report: Any, family: str,
                                label: str, v1: Any) -> dict[str, Any]:
    require(type(report) is dict
            and report.get("schema") == v1.SCHEMA + "-complete-candidate-evaluation"
            and report.get("candidate_family") == family
            and report.get("label") == checked_label(label)
            and report.get("campaign_source_sha256") == V1_SHA256
            and report.get("campaign_protocol_sha256") == V1_PROTOCOL_SHA256
            and report.get("campaign_document_sha256") == V1_DOCUMENT_SHA256
            and report.get("producer_source_sha256") == PRODUCER_SHA256
            and report.get("producer_protocol_sha256") == PRODUCER_PROTOCOL_SHA256
            and report.get("producer_document_sha256") == PRODUCER_DOCUMENT_SHA256
            and report.get("phase_one_manifest_sha256") == PHASE1_SHA256
            and report.get("suite_count") == 13
            and report.get("case_execution_denominator") == 31237
            and report.get("completed_suite_count") == 13
            and type(report.get("suite_results")) is list
            and len(report["suite_results"]) == 13
            and [row.get("suite") for row in report["suite_results"]]
            == [row[0] for row in SUITES]
            and report.get("restoration", {}).get("status") == "PASS"
            and report.get("status") in {"PASS", "FAIL"}
            and report.get("candidate_qualified")
            is (report["status"] == "PASS")
            and report.get("actual_native_activations") == 1
            and report.get("generated_go_header_promoted") is False
            and report.get("hidden_cases_read") == 0
            and report.get("benchmark_files_read") == 0
            and report.get("clock_samples") == 0
            and report.get("timing_trials_run") == 0
            and report.get("holdout") == "NOT OPENED",
            "stream only a complete genuinely restored unchanged V1 evaluation")
    actual = report["restoration"].get("actual_restoration")
    require(type(actual) is dict and actual.get("status") == "PASS"
            and actual.get("family") == family
            and type(actual.get("restored_targets")) is dict
            and set(actual["restored_targets"])
            == ({"bridge"} if family == "cpp" else {"bridge", "engine"}),
            "authenticate every original split target before streamed publication")
    passes = [row for row in report["suite_results"]
              if row.get("status") == "PASS"]
    cases = sum(row.get("case_execution_denominator", 0) for row in passes)
    require(report.get("verified_passing_case_count") == cases
            and ((report["status"] == "PASS")
                 is (len(passes) == 13 and cases == 31237)),
            "never qualify a mismatch, timeout, partial campaign or invented case")
    return report


def publish_streamed_report(report: dict[str, Any], options: argparse.Namespace,
                            v1: Any) -> dict[str, Any]:
    family = options.family
    label = checked_label(options.label)
    validate_restored_v1_report(report, family, label, v1)
    archive_name, receipt_name = evidence_names(
        family, label, failure=report["status"] == "FAIL")
    directory = open_evidence_directory()
    try:
        archive, manifest = write_streamed_archive(report, archive_name, directory)
    finally:
        os.close(directory)
    receipt_document = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS", "candidate_status": report["status"],
        "candidate_family": family, "label": label,
        "campaign_source_sha256": options.source_sha256,
        "campaign_protocol_sha256": options.protocol_sha256,
        "campaign_document_sha256": options.document_sha256,
        "original_evaluator_source_sha256": V1_SHA256,
        "original_evaluator_protocol_sha256": V1_PROTOCOL_SHA256,
        "original_evaluator_document_sha256": V1_DOCUMENT_SHA256,
        "producer_source_sha256": PRODUCER_SHA256,
        "producer_protocol_sha256": PRODUCER_PROTOCOL_SHA256,
        "producer_document_sha256": PRODUCER_DOCUMENT_SHA256,
        "phase_one_manifest_sha256": PHASE1_SHA256,
        "suite_count": 13, "case_execution_denominator": 31237,
        "completed_suite_count": 13,
        "verified_passing_case_count": report["verified_passing_case_count"],
        "archive": archive,
        "archive_directory_fsync_completed": True,
        "uncompressed_sha256": manifest["uncompressed_sha256"],
        "uncompressed_bytes": manifest["uncompressed_bytes"],
        "uncompressed_chunk_count": manifest["uncompressed_chunk_count"],
        "maximum_uncompressed_report_bytes": MAX_REPORT_BYTES,
        "maximum_compressed_archive_bytes": MAX_ARCHIVE_BYTES,
        "activation": report["activation"],
        "restoration": report["restoration"],
        "all_mismatches_crashes_and_timeouts_preserved": True,
        "failure_preserved": report["status"] == "FAIL",
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False, "receipt_self_publication": "NOT CLAIMED",
    }
    receipt_raw = canonical(receipt_document)
    require(0 < len(receipt_raw) <= MAX_SOURCE_BYTES,
            "require a bounded separate complete streaming publication receipt")
    activation = v1.frozen_module(V4_RELATIVE, V4_SHA256, V4_BYTES)
    root = str(ROOT / EVIDENCE_RELATIVE)
    receipt = activation.write_fresh(root, receipt_name, receipt_raw)
    synchronized = activation.synchronize_directory(root)
    require(receipt.get("mode") == 0o600
            and receipt.get("exclusive_creation") is True
            and receipt.get("file_fsync_completed") is True
            and receipt.get("same_inode_readback_verified") is True
            and synchronized.get("completed") is True
            and (archive["device"], archive["inode"])
            != (receipt.get("device"), receipt.get("inode")),
            "require two distinct independently synchronized owner-only inodes")
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
        "uncompressed_sha256": manifest["uncompressed_sha256"],
        "uncompressed_bytes": manifest["uncompressed_bytes"],
        "all_mismatches_crashes_and_timeouts_preserved": True,
        "restoration_verified_before_publication": True,
        "original_evaluator_unchanged": True,
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
            and context.get("retained_original_candidate_evidence_owner_count") == 67
            and context.get("actual_current_repository_evidence_owner_count") == 69
            and context.get("total_distinct_historical_evidence_owner_count") == 69,
            "authenticate all 69 genuine owners before an explicit original campaign")
    ensure_fresh_evidence(options.family, options.label)
    v1 = frozen_module(V1_RELATIVE, V1_SHA256, V1_BYTES)
    inherited_options = argparse.Namespace(
        run=True, self_test=False, verify_frozen_context=False,
        family=options.family, label=options.label,
        build_root=options.build_root,
        source_sha256=V1_SHA256,
        protocol_sha256=V1_PROTOCOL_SHA256,
        document_sha256=V1_DOCUMENT_SHA256,
    )
    original_publication = v1.publish_actual_report
    original_freshness = v1.ensure_fresh_evidence

    def publish_original(report: dict[str, Any], unused: Any) -> dict[str, Any]:
        return publish_streamed_report(report, options, v1)

    try:
        v1.publish_actual_report = publish_original
        v1.ensure_fresh_evidence = ensure_fresh_evidence
        return v1.run_actual_campaign(inherited_options)
    except BaseException as error:
        details = getattr(error, "details", None)
        summary: dict[str, Any] = {"actual_candidate_workers": 0,
                                   "actual_native_activations": 0,
                                   "completed_suite_count": 0,
                                   "restoration_verified": False}
        if type(details) is dict:
            for key in ("actual_candidate_workers", "actual_native_activations"):
                value = details.get(key)
                if type(value) is int and 0 <= value <= 13:
                    summary[key] = value
            rows = details.get("suite_results")
            report = details.get("complete_candidate_report")
            if type(rows) is list:
                summary["completed_suite_count"] = min(len(rows), 13)
            elif type(report) is dict:
                count = report.get("completed_suite_count")
                if type(count) is int and 0 <= count <= 13:
                    summary["completed_suite_count"] = count
                restoration = report.get("restoration")
                if type(restoration) is dict:
                    summary["restoration_verified"] = (
                        restoration.get("status") == "PASS")
            restoration = details.get("restoration")
            if type(restoration) is dict:
                summary["restoration_verified"] = (
                    restoration.get("status") == "PASS")
        raise CampaignExecutionFailure(
            "the original campaign failed; full records are never printed",
            summary) from error
    finally:
        v1.publish_actual_report = original_publication
        v1.ensure_fresh_evidence = original_freshness


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
                and all(getattr(options, key) is None for key in pins),
                "source-only controls accept no pin, family, activation or run")
        return options
    for key in pins:
        checked_digest(getattr(options, key), key)
    if options.verify_frozen_context:
        require(options.family is None and options.label is None
                and options.build_root is None,
                "read-only verification accepts only three exact freeze pins")
        return options
    require(options.run and options.family in {"cpp", "go"},
            "actually run only one explicitly authorized passing source-build family")
    checked_label(options.label)
    require(type(options.build_root) is str and bool(options.build_root),
            "explicitly authenticate the original first-party build root")
    return options


def compact_error_message(error: BaseException) -> tuple[str, bool]:
    text = str(error)
    raw = text.encode("utf-8", "backslashreplace")
    if len(raw) <= MAX_ERROR_MESSAGE_BYTES:
        return text, False
    bounded = raw[:MAX_ERROR_MESSAGE_BYTES].decode("utf-8", "ignore")
    return bounded, True


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
        message, clipped = compact_error_message(error)
        failure = {
            "schema": SCHEMA + "-bounded-entry-failure",
            "status": "FAIL", "error_type": type(error).__qualname__,
            "error_message": message,
            "error_message_truncated": clipped,
            "complete_report_in_stdout": False,
            "maximum_error_message_bytes": MAX_ERROR_MESSAGE_BYTES,
            **zero_effects(),
        }
        details = getattr(error, "details", None)
        if type(details) is dict:
            for key in ("actual_candidate_workers", "actual_native_activations",
                        "completed_suite_count"):
                value = details.get(key)
                if type(value) is int and 0 <= value <= 13:
                    failure[key] = value
            if type(details.get("restoration_verified")) is bool:
                failure["restoration_verified"] = details["restoration_verified"]
        try:
            sys.stdout.buffer.write(canonical(failure))
            sys.stdout.buffer.flush()
        except (OSError, TypeError, ValueError, UnicodeError):
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
