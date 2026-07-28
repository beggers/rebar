#!/usr/bin/env python3
"""Preserve the original P0 producer and authenticate real V4 activation.

Self-tests are exclusively synthetic and do not read any files. Frozen-context
verification is read-only. Neither mode builds, activates, imports a candidate,
runs a reference, samples a clock, opens the holdout, or performs matching.
An explicitly requested actual suite reuses the unchanged, pinned V1 evaluator.
"""

from __future__ import annotations

import argparse
import builtins
import copy
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
from typing import Any, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_owned_six_family_original_p0_producer_v2.py"
PROTOCOL_RELATIVE = "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V2.md"
DOCUMENT_RELATIVE = "oracle/phase2/six-family-p0-producer-v2.json"
SCHEMA = "rebar-owned-six-family-original-p0-producer-v2"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
PHASE1_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"
V1_SOURCE_RELATIVE = "tools/run_owned_six_family_original_p0_producer_v1.py"
V1_SOURCE_SHA256 = "36451c10221857cca8c77fad7533382f4e3969a20a5cdf73c055beea1d315d33"
V1_SOURCE_BYTES = 149599
V1_PROTOCOL_RELATIVE = "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V1.md"
V1_PROTOCOL_SHA256 = "1e7ed2cbd63e080c563dd49b4ea2a2be284d831d75739c47edecfae50373ce17"
V1_PROTOCOL_BYTES = 8711
V1_DOCUMENT_RELATIVE = "oracle/phase2/six-family-p0-producer-v1.json"
V1_DOCUMENT_SHA256 = "5206bcc097cd399cddd91a8d0356fd780b44ef7c173d70605d28a175dac71c0b"
V1_DOCUMENT_BYTES = 19054
V4_ACTIVATION_RELATIVE = "tools/activate_verified_native_candidate_v4.py"
V4_ACTIVATION_SHA256 = "f22106dab1e4a2f66178cdda66388c12dda83ad09254b045b447759615bf5cd7"
V4_ACTIVATION_BYTES = 308110
V4_PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V4.md"
V4_PROTOCOL_SHA256 = "3b4d463103380e30b7eb324598b4d39edb66e29f6ad483f7783cf51e4456621d"
V4_PROTOCOL_BYTES = 7757
V4_DOCUMENT_RELATIVE = "oracle/phase2/verified-native-activation-v4.json"
V4_DOCUMENT_SHA256 = "b1ba6cccfea423f562056e1813c8fe6c1e0ef24c2beabb099809dd1669982cf5"
V4_DOCUMENT_BYTES = 26819
V4_BUILD_SOURCE_SHA256 = "efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1"
V4_BUILD_PROTOCOL_SHA256 = "e974b26562cc210c175c08cda7914e6b196fdee2ebe2a8232dd87c0cddbc0dfb"
V4_BUILD_DOCUMENT_SHA256 = "0b5641529bc49f55b9e56fe397ad38e7e23d6c9b3376587b743753814b8089d7"
V6_BUILD_SOURCE_SHA256 = "2af9da3cb37a55782f3bfb8bdbdfdb7a945532994a5c988f4645d888dbe57ebc"
V6_BUILD_PROTOCOL_SHA256 = "108dbd52144c78530221e36882a0070fe9805b1bef6a136caf4636148ae9131d"
V6_BUILD_DOCUMENT_SHA256 = "0121aaa5902b449e107396d6a1107ca8fe0fefebb0a0f09eb58d2d19c8888db4"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024


class ProducerError(Exception):
    """Reject an unproven original P0 or activation obligation."""


class SourceOnlyViolation(ProducerError):
    """A source-only self-test attempted an external effect."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise ProducerError(message)


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           separators=(",", ":"), sort_keys=True)
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, OverflowError, RecursionError,
            UnicodeError) as error:
        raise ProducerError("require complete finite canonical evidence") from error


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require one full lowercase SHA-256: " + label)
    return value


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
        "actual_native_libraries_loaded": 0,
        "actual_network_requests": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_qualified_count": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


# Each row is the exact, original V1 suite, in the original V1 order.
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

FAMILY_ORDER = ("rust", "c", "zig", "cpp", "go", "fortran")
FAMILY_DETAILS = {
    "rust": ("candidates.rust_candidate", "candidates/rust_candidate.py", "candidates._rust_bridge", "candidates/_rust_engine.so", "candidates/_rust_bridge" + EXTENSION_SUFFIX, False, False),
    "c": ("candidates.vm_candidate", "candidates/vm_candidate.py", "candidates._vm_native", "candidates/_vm_native" + EXTENSION_SUFFIX, "candidates/_vm_native" + EXTENSION_SUFFIX, True, False),
    "zig": ("candidates.zig_candidate", "candidates/zig_candidate.py", "candidates._zig_bridge", "candidates/_zig_probe.so", "candidates/_zig_bridge" + EXTENSION_SUFFIX, False, True),
    "cpp": ("candidates.cpp_candidate", "candidates/cpp_candidate.py", "candidates._cpp_bridge", "candidates/_cpp_bridge" + EXTENSION_SUFFIX, "candidates/_cpp_bridge" + EXTENSION_SUFFIX, True, False),
    "go": ("candidates.go_candidate", "candidates/go_candidate.py", "candidates._go_bridge", "candidates/_go_engine.so", "candidates/_go_bridge" + EXTENSION_SUFFIX, False, False),
    "fortran": ("candidates.fortran_candidate", "candidates/fortran_candidate.py", "candidates._fortran_bridge", "candidates/_fortran_engine.so", "candidates/_fortran_bridge" + EXTENSION_SUFFIX, False, False),
}

# These are the 14 actual V4/V5/V6 owners in addition to the 51 immutable
# candidate-history owners authenticated independently by the V1 and V4 freezes.
BUILD_HISTORY = (
    (4, "cpp", "PASS", 10, 2, "oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4.json.gz", "48910a6328e8aaacdac993b2c029995d878960a456359a14db5c83b9fc518df9", 20605, "oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4-publication-receipt.json", "7742eda3ce777b1378d0c7fb87fc064f222850ca8bcf15cd23ff8a4d87d8bebf", 2074),
    (4, "go", "FAIL", 4, 0, "oracle/phase2/evidence/native-source-build-v4-go-phase2-v4-failures.json.gz", "fcf643b7b8e9fbe80bd3b40c7ed884695a844f46e1117f5ebdb130135e5db4bb", 4095, "oracle/phase2/evidence/native-source-build-v4-go-phase2-v4-failures-publication-receipt.json", "215e9680bbe0f8d2250fcca8bae0335017606288e13e7636224b7c76336b5e41", 2075),
    (4, "fortran", "FAIL", 18, 2, "oracle/phase2/evidence/native-source-build-v4-fortran-phase2-v4-failures.json.gz", "ba35ea4f0d28814f716a36d2ccb384ef034a88a4029ca3f3cbf4f91eae268103", 14825, "oracle/phase2/evidence/native-source-build-v4-fortran-phase2-v4-failures-publication-receipt.json", "86b4b2648adf651481eea8d8b427a432f121c59322f508b522eca18af0749a08", 2019),
    (5, "go", "FAIL", 5, 0, "oracle/phase2/evidence/native-source-build-v5-go-phase2-v5-failures.json.gz", "ff92f5f182307b5e6e123ab883e630c6aca63f8c75318fa4ac083b1d72db6169", 5595, "oracle/phase2/evidence/native-source-build-v5-go-phase2-v5-failures-publication-receipt.json", "00a126f6c462913ad00ea9961334bbeb5aa2bfd1301d02d8f8c5d55c2e239db0", 2903),
    (5, "fortran", "FAIL", 26, 2, "oracle/phase2/evidence/native-source-build-v5-fortran-phase2-v5-failures.json.gz", "eadf8844a1bda48d2420c7b3311ced77de9fda7ccfb806f73764550080823e53", 26274, "oracle/phase2/evidence/native-source-build-v5-fortran-phase2-v5-failures-publication-receipt.json", "f9bf0a652e9c10c949d7b5faabf261d3931681548d4f5d1af69f0accc6d742f2", 2848),
    (6, "go", "PASS", 26, 2, "oracle/phase2/evidence/native-source-build-v6-go-phase2-v6.json.gz", "05c24a5fff228d8eab8bec961d825b0e65504072e11e8c574ec580d9f3e6e245", 37619, "oracle/phase2/evidence/native-source-build-v6-go-phase2-v6-publication-receipt.json", "f3adcb20bb591946600e1e2b1db037fb3b4828c3d4a628a0347cfed40f262fca", 3262),
    (6, "fortran", "FAIL", 26, 2, "oracle/phase2/evidence/native-source-build-v6-fortran-phase2-v6-failures.json.gz", "c62007d5519d1ef723da7e144b1c6eeb067aacf47e960638e9d6b8a604f05d12", 26102, "oracle/phase2/evidence/native-source-build-v6-fortran-phase2-v6-failures-publication-receipt.json", "6bc1ea1695247d8d137e6c2f50908b6c3a0518ff82978258bd07e8010e88ad7a", 3221),
)


def suite_protocol(row: tuple[Any, ...]) -> dict[str, Any]:
    name, count, path, source, matrix, reference, seed, route = row
    return {
        "id": name,
        "case_execution_count": count,
        "source_relative": path,
        "source_sha256": source,
        "matrix_sha256": matrix,
        "reference_records_sha256": reference,
        "published_seed_decimal": None if seed is None else str(seed),
        "unchanged_original_producer_route": route,
    }


def family_protocol(name: str) -> dict[str, Any]:
    module, adapter, bridge, engine_path, bridge_path, combined, ctypes = FAMILY_DETAILS[name]
    return {
        "family": name, "module": module, "adapter_relative": adapter,
        "bridge_module": bridge, "engine_relative": engine_path,
        "bridge_relative": bridge_path,
        "combined_native_engine_and_bridge": combined,
        "owned_ctypes_allowed": ctypes,
        "owned_source_count": len(OWNED_SOURCES[name]),
        "sources": [{"relative": path, "sha256": digest, "size_bytes": size}
                    for path, digest, size in OWNED_SOURCES[name]],
    }


def historical_protocol() -> dict[str, Any]:
    rows = [{
        "version": version, "family": family, "build_status": status,
        "actual_compiler_process_count": processes,
        "completed_phase_count": phases,
        "archive_relative": archive, "archive_sha256": archive_sha,
        "archive_bytes": archive_bytes,
        "receipt_relative": receipt, "receipt_sha256": receipt_sha,
        "receipt_bytes": receipt_bytes,
        "qualified_candidate_count": 0,
    } for (version, family, status, processes, phases, archive, archive_sha,
           archive_bytes, receipt, receipt_sha, receipt_bytes) in BUILD_HISTORY]
    return {
        "frozen_v7_candidate_evidence_owner_count": 51,
        "frozen_v4_source_build_evidence_owner_count": 6,
        "frozen_v5_source_build_evidence_owner_count": 4,
        "frozen_v6_source_build_evidence_owner_count": 4,
        "total_distinct_evidence_owner_count": 65,
        "source_builds": rows,
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
        "v6_go_native_outputs": {
            "engine": {"sha256": "38ab223b8ef88340a7be86f2195c417ee7d2dd9deead48cc6495a5b4e3c31b27", "size_bytes": 2712912},
            "bridge": {"sha256": "dd71ab6cb15a98e1a07c38965cdb178da0dbba2a26db937975e0d6435a2a5d0c", "size_bytes": 41904},
            "generated_header": {"sha256": "481ebb65cc587749677ce28abeb4f3de111e2f87a18ac547ff0157fce85d2c23", "size_bytes": 3086, "promoted": False},
        },
        "v4_cpp_combined_native_output": {
            "sha256": "d444611316caceb4ba08783203bc4f1d396a8987f63a49bd24c81d5d2c532441",
            "size_bytes": 130744,
            "engine_and_bridge_are_one_native_owner": True,
        },
        "v6_fortran_reproducibility": {
            "status": "FAIL", "successful_compiler_process_count": 26,
            "completed_phase_count": 2,
            "phase_a_engine_sha256": "6ed7afa0b7c2eb905cd00de0ec935a7c449f257431d44aaa652ae0f10191d1f7",
            "phase_b_engine_sha256": "1458072addc7988975317ac81d64748970ee3d4321437be73275a700fed831c9",
            "identical_bridge_sha256": "f0808671b4d16f9b8d74a891d04ccd78bcf2e568ae2edbfb3997fb0db23c2fd7",
            "differing_raw_binary_section": "NOT RECORDED",
        },
    }


def protocol_document() -> dict[str, Any]:
    families = [family_protocol(name) for name in FAMILY_ORDER]
    paths = [item["relative"] for family in families for item in family["sources"]]
    rows = [suite_protocol(row) for row in SUITES]
    require(len(families) == 6 and len(paths) == len(set(paths)) == 25,
            "freeze six independent families and exactly 25 disjoint source owners")
    require(len(rows) == 13 and len({item["id"] for item in rows}) == 13
            and sum(item["case_execution_count"] for item in rows) == 31237,
            "preserve the exact original 13-suite, 31,237-case P0 denominator")
    return {
        "schema": SCHEMA + "-source-freeze", "version": 2,
        "phase": "CANDIDATES",
        "status": "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
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
        "frozen_original_v1_producer": {
            "source_relative": V1_SOURCE_RELATIVE,
            "source_sha256": V1_SOURCE_SHA256,
            "source_bytes": V1_SOURCE_BYTES,
            "protocol_relative": V1_PROTOCOL_RELATIVE,
            "protocol_sha256": V1_PROTOCOL_SHA256,
            "protocol_bytes": V1_PROTOCOL_BYTES,
            "document_relative": V1_DOCUMENT_RELATIVE,
            "document_sha256": V1_DOCUMENT_SHA256,
            "document_bytes": V1_DOCUMENT_BYTES,
            "historically_frozen_evidence_owner_count": 61,
        },
        "frozen_v4_activation": {
            "source_relative": V4_ACTIVATION_RELATIVE,
            "source_sha256": V4_ACTIVATION_SHA256,
            "source_bytes": V4_ACTIVATION_BYTES,
            "protocol_relative": V4_PROTOCOL_RELATIVE,
            "protocol_sha256": V4_PROTOCOL_SHA256,
            "protocol_bytes": V4_PROTOCOL_BYTES,
            "document_relative": V4_DOCUMENT_RELATIVE,
            "document_sha256": V4_DOCUMENT_SHA256,
            "document_bytes": V4_DOCUMENT_BYTES,
            "historically_frozen_evidence_owner_count": 65,
        },
        "frozen_source_builds": {
            "v4": {"source_sha256": V4_BUILD_SOURCE_SHA256,
                   "protocol_sha256": V4_BUILD_PROTOCOL_SHA256,
                   "document_sha256": V4_BUILD_DOCUMENT_SHA256},
            "v6": {"source_sha256": V6_BUILD_SOURCE_SHA256,
                   "protocol_sha256": V6_BUILD_PROTOCOL_SHA256,
                   "document_sha256": V6_BUILD_DOCUMENT_SHA256},
        },
        "families": families, "family_count": 6,
        "source_owner_count": 25,
        "pairwise_shared_semantic_source_count": 0,
        "suite_count": 13,
        "case_execution_denominator": 31237,
        "suites": rows,
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
        "historical_evidence": historical_protocol(),
        "source_build_policy": {
            "independently_source_built_families": ["c", "rust", "zig", "cpp", "go"],
            "independently_source_built_family_count": 5,
            "historically_runnable_p0_families": ["c", "rust", "zig"],
            "historically_runnable_p0_family_count": 3,
            "fortran_passing_source_build": False,
            "build_receipt_is_not_candidate_correctness": True,
            "actual_native_activations": 0,
            "qualified_candidate_count": 0,
        },
        "activation_policy": {
            "rust": {"legacy_build_version": 2, "legacy_activation_version": 2},
            "c": {"legacy_build_version": 2, "legacy_activation_version": 2},
            "zig": {"legacy_build_version": 3, "legacy_activation_version": 2},
            "cpp": {"source_build_version": 4,
                    "permitted_activation_versions": [3, 4],
                    "combined_native_engine_and_bridge": True},
            "go": {"source_build_version": 6,
                   "activation_version": 4,
                   "combined_native_engine_and_bridge": False,
                   "generated_go_header_promoted": False},
            "fortran": "NO PASS BUILD OR VERIFIED ACTIVATION; FAIL CLOSED",
            "v5_build_without_v5_aware_activation": "FAIL CLOSED",
            "actual_activation_report_required": True,
            "actual_activation_receipt_required": True,
            "actual_recovery_journal_required": True,
            "actual_promotion_intentions_required": True,
            "exact_current_canonical_device_and_inode_required": True,
            "two_independent_source_build_phases_required": True,
            "activation_creates_or_replaces_targets": False,
            "source_build_started": False,
        },
        "independence_policy": {
            "actual_source_and_native_owner_proof_required": True,
            "continuous_original_matcher_identity_guard_required": True,
            "cross_family_native_engine_allowed": False,
            "cross_family_source_allowed": False,
            "candidate_regex_stdlib_allowed": False,
            "candidate_sre_allowed": False,
            "third_party_regex_allowed": False,
            "fallback_allowed": False,
        },
        "verification_effects": zero_effects(),
    }


def validate_protocol_document(value: Any) -> dict[str, Any]:
    require(type(value) is dict and canonical(value) == canonical(protocol_document()),
            "reject any altered original suite, source, history, build, activation, or effect")
    return value


class SourceOnlyBoundary:
    """Make source-only tests physically unable to read or cause effects."""

    def __init__(self) -> None:
        self.installed: list[tuple[Any, str, Any]] = []
        self.blocked_counts: dict[str, int] = {
            "file": 0, "process": 0, "clock": 0, "network": 0,
            "thread": 0, "temporary": 0, "import": 0,
        }
        self.initial_modules: frozenset[str] = frozenset()

    def replace(self, owner: Any, name: str, category: str) -> None:
        if hasattr(owner, name):
            previous = getattr(owner, name)

            def blocked(*args: Any, **kwargs: Any) -> Any:
                self.blocked_counts[category] += 1
                raise SourceOnlyViolation("source-only verification cannot perform " + category)

            self.installed.append((owner, name, previous))
            setattr(owner, name, blocked)

    def __enter__(self) -> SourceOnlyBoundary:
        self.initial_modules = frozenset(sys.modules)
        for owner, name in ((builtins, "open"), (io, "open"), (os, "open"),
                            (Path, "open"), (Path, "read_bytes"),
                            (Path, "read_text"), (Path, "write_bytes"),
                            (Path, "write_text")):
            self.replace(owner, name, "file")
        for name in ("run", "Popen", "call", "check_call", "check_output"):
            self.replace(subprocess, name, "process")
        for name in ("system", "popen", "fork", "posix_spawn", "posix_spawnp", "pipe"):
            self.replace(os, name, "process")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns", "sleep"):
            self.replace(time, name, "clock")
        self.replace(socket, "socket", "network")
        self.replace(socket, "create_connection", "network")
        self.replace(threading.Thread, "start", "thread")
        self.replace(threading.Barrier, "wait", "thread")
        for name in ("mkstemp", "mkdtemp", "TemporaryFile",
                     "NamedTemporaryFile", "TemporaryDirectory"):
            self.replace(tempfile, name, "temporary")
        self.replace(importlib, "import_module", "import")
        self.replace(builtins, "__import__", "import")
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        for owner, name, previous in reversed(self.installed):
            setattr(owner, name, previous)
        require(frozenset(sys.modules) == self.initial_modules,
                "source-only verification imported an additional module")
        return False


def verify_runtime(*, permit_candidate: bool = False) -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and os.path.realpath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "run only the exact isolated, pinned, no-bytecode CPython 3.14.6")
    if not permit_candidate:
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
                "verification must never import a native candidate")


def read_owned(relative: str, expected: str, *, maximum: int,
               exact_size: int | None = None) -> tuple[bytes, dict[str, Any]]:
    require(type(relative) is str and bool(relative) and "\x00" not in relative,
            "require one unambiguous relative owned path")
    path = Path(relative)
    require(not path.is_absolute() and str(path) == relative
            and all(part not in {"", ".", ".."} for part in path.parts),
            "reject an absolute, broad, or traversing source owner")
    target = ROOT / path
    require(os.path.abspath(str(target)) == str(target)
            and os.path.realpath(str(target)) == str(target),
            "reject a symlinked source or historical evidence owner")
    checked_digest(expected, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "bound every source and evidence read")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(target), flags)
    try:
        before = os.fstat(descriptor)
        visible = os.stat(str(target), follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and 0 < before.st_size <= maximum
                and (exact_size is None or before.st_size == exact_size),
                "reject a changed, empty, oversized, or substituted owner: " + relative)
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1048576))
            require(type(chunk) is bytes and bool(chunk),
                    "reject a truncated source or evidence owner: " + relative)
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        after = os.fstat(descriptor)
        final = os.stat(str(target), follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and (after.st_dev, after.st_ino, after.st_size)
                == (final.st_dev, final.st_ino, final.st_size)
                and hashlib.sha256(data).hexdigest() == expected,
                "reject a concurrently changed or incorrectly hashed owner: " + relative)
        return data, {
            "relative": relative, "sha256": expected,
            "size_bytes": len(data), "device": before.st_dev,
            "inode": before.st_ino, "mode": stat.S_IMODE(before.st_mode),
        }
    finally:
        os.close(descriptor)


def unique_json(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject a duplicate or non-string canonical JSON field")
        result[key] = value
    return result


def decode_document(raw: bytes, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES,
            "bound canonical JSON: " + label)
    try:
        result = json.loads(raw.decode("utf-8", "strict"),
                            object_pairs_hook=unique_json,
                            parse_constant=lambda value: (_ for _ in ()).throw(
                                ValueError("nonfinite JSON: " + value)))
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ProducerError("reject invalid canonical JSON: " + label) from error
    require(type(result) is dict and canonical(result) == raw,
            "reject noncanonical or altered frozen evidence: " + label)
    return result


def frozen_module(relative: str, digest: str,
                  exact_size: int) -> Any:
    _, first = read_owned(relative, digest, maximum=MAX_SOURCE_BYTES,
                          exact_size=exact_size)
    module_name = "_rebar_owned_original_p0_v2_frozen_" + digest[:24]
    previous = sys.modules.get(module_name)
    if previous is not None:
        require(os.path.abspath(str(getattr(previous, "__file__", "")))
                == str(ROOT / relative),
                "reject a preloaded foreign frozen producer module")
        module = previous
    else:
        spec = importlib.util.spec_from_file_location(module_name, str(ROOT / relative))
        require(spec is not None and spec.loader is not None,
                "load only the independently pinned producer source")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            sys.modules.pop(module_name, None)
            raise
    _, after = read_owned(relative, digest, maximum=MAX_SOURCE_BYTES,
                          exact_size=exact_size)
    require(first["device"] == after["device"]
            and first["inode"] == after["inode"]
            and os.path.abspath(str(getattr(module, "__file__", "")))
            == str(ROOT / relative)
            and os.path.realpath(str(module.__file__)) == str(ROOT / relative),
            "the authenticated frozen source changed during safe import")
    return module


def validate_synthetic_activation(value: Any) -> dict[str, Any]:
    require(type(value) is dict and set(value) == {
        "family", "build_version", "activation_version", "build_status",
        "activation_status", "phase_count", "source_owner_count",
        "combined_native_engine_and_bridge", "generated_go_header_promoted",
        "candidate_qualified", "synthetic_only",
    }, "require one complete in-memory synthetic activation")
    family = value.get("family")
    require(type(family) is str and family in FAMILY_DETAILS,
            "reject synthetic cross-family activation")
    allowed = {"rust": (2, 2), "c": (2, 2), "zig": (3, 2),
               "cpp": (4, 4), "go": (6, 4)}
    require(family in allowed and (value["build_version"], value["activation_version"])
            == allowed[family] and value["build_status"] == "PASS"
            and value["activation_status"] == "PASS" and value["phase_count"] == 2
            and value["source_owner_count"] == len(OWNED_SOURCES[family])
            and value["combined_native_engine_and_bridge"]
            is FAMILY_DETAILS[family][5]
            and value["generated_go_header_promoted"] is False
            and value["candidate_qualified"] is False
            and value["synthetic_only"] is True,
            "reject an invented, failed, V5, shared, qualified, or real activation")
    return value


def synthetic_activation(family: str) -> dict[str, Any]:
    allowed = {"rust": (2, 2), "c": (2, 2), "zig": (3, 2),
               "cpp": (4, 4), "go": (6, 4)}
    require(type(family) is str and family in allowed,
            "failed Fortran and V5 cannot acquire synthetic passing evidence")
    build, activation = allowed[family]
    return {
        "family": family, "build_version": build,
        "activation_version": activation, "build_status": "PASS",
        "activation_status": "PASS", "phase_count": 2,
        "source_owner_count": len(OWNED_SOURCES[family]),
        "combined_native_engine_and_bridge": FAMILY_DETAILS[family][5],
        "generated_go_header_promoted": False,
        "candidate_qualified": False, "synthetic_only": True,
    }


def self_test() -> dict[str, Any]:
    verify_runtime()
    accepted = 0
    rejected = 0
    with SourceOnlyBoundary() as boundary:
        document = protocol_document()
        validate_protocol_document(document)
        accepted += 1

        def reject(item: Any, validator: Any = validate_protocol_document) -> None:
            nonlocal rejected
            try:
                validator(item)
            except (ProducerError, TypeError, ValueError, KeyError):
                rejected += 1
                return
            raise ProducerError("a hostile synthetic mutation was incorrectly accepted")

        for index, suite in enumerate(document["suites"]):
            for key, original in suite.items():
                mutated = copy.deepcopy(document)
                if type(original) is bool:
                    replacement = not original
                elif type(original) is int:
                    replacement = original + 1
                elif original is None:
                    replacement = "0"
                else:
                    replacement = str(original) + "x"
                mutated["suites"][index][key] = replacement
                reject(mutated)
            accepted += 1
        for family_index, family in enumerate(document["families"]):
            for key in ("family", "module", "adapter_relative", "bridge_module",
                        "engine_relative", "bridge_relative", "owned_source_count"):
                mutated = copy.deepcopy(document)
                original = mutated["families"][family_index][key]
                mutated["families"][family_index][key] = (
                    original + 1 if type(original) is int else original + "-foreign"
                )
                reject(mutated)
            for owner_index, owner in enumerate(family["sources"]):
                for key in ("relative", "sha256", "size_bytes"):
                    mutated = copy.deepcopy(document)
                    original = mutated["families"][family_index]["sources"][owner_index][key]
                    mutated["families"][family_index]["sources"][owner_index][key] = (
                        original + 1 if type(original) is int else original + "x"
                    )
                    reject(mutated)
            accepted += 1
        for section in ("frozen_original_v1_producer", "frozen_v4_activation",
                        "phase_one", "source_build_policy", "activation_policy",
                        "independence_policy", "verification_effects",
                        "successful_nested_lifecycle", "historical_evidence"):
            for key, original in document[section].items():
                mutated = copy.deepcopy(document)
                if type(original) is bool:
                    replacement = not original
                elif type(original) is int:
                    replacement = original + 1
                elif type(original) is str:
                    replacement = original + "-changed"
                elif type(original) is list:
                    replacement = original[:-1]
                elif type(original) is dict:
                    replacement = {}
                else:
                    replacement = "changed"
                mutated[section][key] = replacement
                reject(mutated)
        for version in ("v4", "v6"):
            for key in document["frozen_source_builds"][version]:
                mutated = copy.deepcopy(document)
                mutated["frozen_source_builds"][version][key] += "x"
                reject(mutated)
        for row_index, row in enumerate(document["historical_evidence"]["source_builds"]):
            for key, original in row.items():
                mutated = copy.deepcopy(document)
                mutated_row = mutated["historical_evidence"]["source_builds"][row_index]
                mutated_row[key] = (original + 1 if type(original) is int
                                    else original + "x")
                reject(mutated)
        ledger = document["historical_evidence"]["historical_build_process_ledger"]
        for key, original in ledger.items():
            mutated = copy.deepcopy(document)
            changed = mutated["historical_evidence"]["historical_build_process_ledger"]
            changed[key] = (original + 1 if type(original) is int
                            else {} if type(original) is dict else original + "x")
            reject(mutated)
        for family in ("rust", "c", "zig", "cpp", "go"):
            fixture = synthetic_activation(family)
            validate_synthetic_activation(fixture)
            accepted += 1
            for key, original in fixture.items():
                mutated = copy.deepcopy(fixture)
                if type(original) is bool:
                    mutated[key] = not original
                elif type(original) is int:
                    mutated[key] = original + 1
                else:
                    mutated[key] = str(original) + "-foreign"
                reject(mutated, validate_synthetic_activation)
        reject({**synthetic_activation("go"), "family": "fortran"},
               validate_synthetic_activation)
        reject({**synthetic_activation("go"), "build_version": 5},
               validate_synthetic_activation)
        reject({**synthetic_activation("go"),
                "combined_native_engine_and_bridge": True},
               validate_synthetic_activation)
        reject({**synthetic_activation("cpp"),
                "combined_native_engine_and_bridge": False},
               validate_synthetic_activation)
        operations = (
            (lambda: builtins.open("GOAL.md", "rb")),
            (lambda: os.open("GOAL.md", os.O_RDONLY)),
            (lambda: subprocess.run(["true"])),
            (lambda: time.perf_counter()),
            (lambda: socket.socket()),
            (lambda: threading.Thread(target=lambda: None).start()),
            (lambda: tempfile.mkdtemp()),
            (lambda: importlib.import_module("candidates.go_candidate")),
        )
        for operation in operations:
            try:
                operation()
            except SourceOnlyViolation:
                rejected += 1
            else:
                raise ProducerError("the source-only effect boundary was bypassed")
        require(accepted >= 25 and rejected >= 280,
                "exercise every original suite, family, owner, history, and effect")
        blocked = dict(boundary.blocked_counts)
        require(all(value > 0 for value in blocked.values()),
                "prove every source-only effect class is blocked")
    return {
        "schema": SCHEMA + "-source-only-self-test", "status": "PASS",
        "source_only": True, "synthetic_only": True,
        "accepted_synthetic_controls": accepted,
        "rejected_hostile_controls": rejected,
        "blocked_effect_probes": blocked,
        "suite_count": 13, "case_execution_denominator": 31237,
        "source_family_count": 6, "source_owner_count": 25,
        "total_distinct_historical_evidence_owner_count": 65,
        "all_historical_versions_actual_compiler_process_count": 169,
        "historically_runnable_p0_family_count": 3,
        "independently_source_built_family_count": 5,
        **zero_effects(),
    }


def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    verify_runtime()
    source_raw, source_owner = read_owned(
        SOURCE_RELATIVE, options.source_sha256, maximum=MAX_SOURCE_BYTES)
    prose_raw, prose_owner = read_owned(
        PROTOCOL_RELATIVE, options.protocol_sha256, maximum=MAX_SOURCE_BYTES)
    machine_raw, machine_owner = read_owned(
        DOCUMENT_RELATIVE, options.document_sha256, maximum=MAX_SOURCE_BYTES)
    require(bool(source_raw) and bool(prose_raw),
            "pin all three independent V2 source-freeze owners")
    validate_protocol_document(decode_document(machine_raw, "V2 producer machine"))
    v1 = frozen_module(V1_SOURCE_RELATIVE, V1_SOURCE_SHA256, V1_SOURCE_BYTES)
    with v1.EffectBoundary(source_only=False) as boundary:
        v1_prose, v1_prose_owner = read_owned(
            V1_PROTOCOL_RELATIVE, V1_PROTOCOL_SHA256,
            maximum=MAX_SOURCE_BYTES, exact_size=V1_PROTOCOL_BYTES)
        v1_raw, v1_machine_owner = read_owned(
            V1_DOCUMENT_RELATIVE, V1_DOCUMENT_SHA256,
            maximum=MAX_SOURCE_BYTES, exact_size=V1_DOCUMENT_BYTES)
        require(bool(v1_prose) and canonical(v1.protocol_document()) == v1_raw,
                "authenticate the original V1 prose and exact unchanged machine")
        inherited = v1.verify_frozen_context(argparse.Namespace(
            source_sha256=V1_SOURCE_SHA256,
            protocol_sha256=V1_PROTOCOL_SHA256,
            document_sha256=V1_DOCUMENT_SHA256,
        ))
        require(type(inherited) is dict and inherited.get("status") == "PASS"
                and inherited.get("read_only") is True
                and inherited.get("suite_count") == 13
                and inherited.get("case_execution_denominator") == 31237
                and inherited.get("total_distinct_historical_evidence_owner_count") == 61
                and inherited.get("source_family_count") == 6
                and inherited.get("historically_runnable_p0_family_count") == 3
                and inherited.get("fully_qualified_candidate_count") == 0,
                "reauthenticate the complete immutable V1 original producer")
        for key, value in zero_effects().items():
            if key in inherited:
                require(type(inherited[key]) is type(value)
                        and inherited[key] == value,
                        "the original V1 read-only freeze caused an effect: " + key)
        activation = frozen_module(
            V4_ACTIVATION_RELATIVE, V4_ACTIVATION_SHA256, V4_ACTIVATION_BYTES)
        _, activation_prose = read_owned(
            V4_PROTOCOL_RELATIVE, V4_PROTOCOL_SHA256,
            maximum=MAX_SOURCE_BYTES, exact_size=V4_PROTOCOL_BYTES)
        activation_raw, activation_machine = read_owned(
            V4_DOCUMENT_RELATIVE, V4_DOCUMENT_SHA256,
            maximum=MAX_SOURCE_BYTES, exact_size=V4_DOCUMENT_BYTES)
        activation.validate_contract(activation.decode_document(
            activation_raw, "the independently pinned V4 activation machine",
            exact=False,
        ))
        history = activation.expected_historical_evidence()
        actual = activation.verify_frozen_context(
            verify_live_restored_targets=True)
        require(type(actual) is dict and actual.get("status") == "PASS"
                and actual.get("read_only") is True
                and actual.get("total_distinct_historical_evidence_owner_count") == 65
                and actual.get("preserved_all_build_process_count") == 169
                and actual.get("qualified_candidate_count") == 0
                and actual.get("actual_v4_activations") == "NOT RUN",
                "authenticate all 65 genuine evidence owners without activation")
        for key, value in zero_effects().items():
            if key in actual:
                require(type(actual[key]) is type(value) and actual[key] == value,
                        "the actual V4 read-only freeze caused an effect: " + key)
        require(history.get("total_distinct_evidence_owner_count") == 65
                and history.get("candidate_evidence_owner_count") == 51
                and history.get("published_v4_build_evidence_owner_count") == 6
                and history.get("published_v5_build_evidence_owner_count") == 4
                and history.get("published_v6_build_evidence_owner_count") == 4
                and history.get("historical_build_process_ledger")
                == historical_protocol()["historical_build_process_ledger"],
                "retain every exact historical owner and all 169 genuine processes")
        observed_rows = {
            (version, record.get("family")): record
            for version, key in ((4, "published_v4_builds"),
                                 (5, "published_v5_builds"),
                                 (6, "published_v6_builds"))
            for record in history.get(key, [])
        }
        require(len(observed_rows) == len(BUILD_HISTORY) == 7,
                "preserve every historical V4, V5, and V6 pass or failure")
        for (version, family, status, count, phases, archive, archive_sha,
             archive_bytes, receipt, receipt_sha, receipt_bytes) in BUILD_HISTORY:
            record = observed_rows.get((version, family))
            require(type(record) is dict and record.get("build_status") == status
                    and record.get("process_count") == count
                    and record.get("completed_phase_count") == phases
                    and record.get("archive_path") == archive
                    and record.get("archive_sha256") == archive_sha
                    and record.get("archive_bytes") == archive_bytes
                    and record.get("receipt_path") == receipt
                    and record.get("receipt_sha256") == receipt_sha
                    and record.get("receipt_bytes") == receipt_bytes
                    and record.get("qualified_candidate_count") == 0,
                    "reject changed, invented, or omitted build history: "
                    + str(version) + "/" + family)
        go_record = observed_rows[(6, "go")]
        go_outputs = go_record.get("native_outputs")
        required_go = historical_protocol()["v6_go_native_outputs"]
        require(type(go_outputs) is dict
                and set(go_outputs) == {"engine", "bridge", "generated_header"}
                and all(go_outputs[role].get("sha256") == required_go[role]["sha256"]
                        and go_outputs[role].get("size_bytes")
                        == required_go[role]["size_bytes"]
                        for role in go_outputs)
                and go_outputs["engine"]["sha256"]
                != go_outputs["bridge"]["sha256"],
                "retain the genuine split Go engine and build-only generated header")
        require(activation.SOURCE_OWNERS == {
            name: {path: (digest, size) for path, digest, size in rows}
            for name, rows in OWNED_SOURCES.items()
        }, "reject any cross-family, third-party, omitted, or changed semantic owner")
        require([v1.suite_protocol(item) for item in v1.SUITES]
                == [suite_protocol(item) for item in SUITES],
                "reuse the exact original 13 evaluators, seeds, and immutable cases")
        require(v1.protocol_document()["successful_nested_lifecycle"]
                == protocol_document()["successful_nested_lifecycle"],
                "preserve all 128 original nested cases, 394 calls, and 11 interpreters")
        effect_counts = dict(boundary.counts)
    for key in ("actual_candidate_workers", "actual_candidate_imports",
                "actual_reference_workers", "actual_source_builds",
                "actual_native_activations", "actual_native_promotions",
                "actual_interpreters_created", "actual_threads_started",
                "actual_subprocesses_started", "actual_native_libraries_loaded",
                "actual_network_requests", "actual_file_writes",
                "hidden_cases_read", "benchmark_files_read", "clock_samples",
                "timing_trials_run"):
        require(effect_counts.get(key) == 0,
                "the V2 frozen-context verification caused an effect: " + key)
    return {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS", "read_only": True,
        "source": source_owner, "protocol": prose_owner,
        "document": machine_owner,
        "original_v1_source": {
            "relative": V1_SOURCE_RELATIVE,
            "sha256": V1_SOURCE_SHA256, "size_bytes": V1_SOURCE_BYTES,
        },
        "original_v1_protocol": v1_prose_owner,
        "original_v1_document": v1_machine_owner,
        "v4_activation_source": {
            "relative": V4_ACTIVATION_RELATIVE,
            "sha256": V4_ACTIVATION_SHA256,
            "size_bytes": V4_ACTIVATION_BYTES,
        },
        "v4_activation_protocol": activation_prose,
        "v4_activation_document": activation_machine,
        "suite_count": 13, "case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "source_family_count": 6, "source_owner_count": 25,
        "pairwise_shared_semantic_source_count": 0,
        "independently_source_built_family_count": 5,
        "historically_runnable_p0_family_count": 3,
        "fully_runnable_p0_family_count": 3,
        "fully_qualified_candidate_count": 0,
        "total_distinct_historical_evidence_owner_count": 65,
        "historical_build_process_ledger": historical_protocol()[
            "historical_build_process_ledger"],
        "all_historical_versions_actual_compiler_process_count": 169,
        "frozen_v1_historical_evidence_owner_count": 61,
        "actual_v4_activations": "NOT RUN",
        "source_only_effects": effect_counts,
        **zero_effects(),
    }


def authenticate_v4_activation(options: argparse.Namespace, v1: Any,
                               spec: Any) -> dict[str, Any]:
    require(options.activation_source_sha256 == V4_ACTIVATION_SHA256
            and options.activation_protocol_sha256 == V4_PROTOCOL_SHA256
            and options.activation_contract_sha256 == V4_DOCUMENT_SHA256,
            "require the exact independently frozen V4 activation source triple")
    require((spec.name, options.build_version) in {("cpp", "4"), ("go", "6")},
            "authorize V4 activation only for genuine C++ V4 or Go V6 builds")
    activation = frozen_module(
        V4_ACTIVATION_RELATIVE, V4_ACTIVATION_SHA256, V4_ACTIVATION_BYTES)
    selected = activation.select_source_build(
        options.build_source_sha256, options.build_protocol_sha256,
        options.build_contract_sha256)
    require(str(selected["version"]) == options.build_version,
            "reject mismatched C++, Go, or V5 source-build provenance")
    root = activation.checked_private_root(
        options.activation_root, spec.name, build=False)
    arguments = {
        "family": spec.name, "activation_root": root,
        "activation_source_sha256": options.activation_source_sha256,
        "activation_protocol_sha256": options.activation_protocol_sha256,
        "activation_contract_sha256": options.activation_contract_sha256,
        "activation_report_sha256": options.activation_report_sha256,
        "activation_receipt_sha256": options.activation_receipt_sha256,
        "recovery_journal_sha256": options.recovery_journal_sha256,
    }
    report_raw, report_owner = activation.read_owned(
        root, activation.REPORT_NAME, options.activation_report_sha256,
        maximum=activation.MAX_REPORT_BYTES, private=True)
    receipt_raw, receipt_owner = activation.read_owned(
        root, activation.RECEIPT_NAME, options.activation_receipt_sha256,
        maximum=activation.MAX_SOURCE_BYTES, private=True)
    journal_raw, journal_owner = activation.read_owned(
        root, activation.JOURNAL_NAME, options.recovery_journal_sha256,
        maximum=activation.MAX_SOURCE_BYTES, private=True)
    require(all(owner.get("mode") == 0o600
                for owner in (report_owner, receipt_owner, journal_owner)),
            "require three real distinct owner-only V4 activation documents")
    report = activation.decode_document(report_raw, "actual V4 activation report")
    receipt = activation.decode_document(receipt_raw, "actual V4 activation receipt")
    journal = activation.decode_document(journal_raw, "actual V4 recovery journal")
    activation.validate_activation_documents(report, receipt, journal, arguments)
    recovery = activation.validate_recovery_journal(journal, arguments)
    build_arguments = activation.reconstructed_build_arguments(arguments, journal)
    require(build_arguments["build_version"] == selected["version"]
            and build_arguments["build_label"] == options.build_label
            and build_arguments["build_source_sha256"]
            == options.build_source_sha256
            and build_arguments["build_protocol_sha256"]
            == options.build_protocol_sha256
            and build_arguments["build_contract_sha256"]
            == options.build_contract_sha256
            and build_arguments["build_report_sha256"]
            == options.build_archive_sha256
            and build_arguments["build_receipt_sha256"]
            == options.build_receipt_sha256,
            "bind the actual activation to the exact passing build and two phases")
    prerequisite = activation.authenticate_prerequisites(build_arguments)
    require(prerequisite.get("family") == spec.name
            and prerequisite.get("build_version") == selected["version"],
            "reject cross-family, failed, or incomplete source-build prerequisites")
    source_pins = v1.parse_source_owners(spec, options.owned_source_sha256)
    pins = v1.native_pins(spec, options)
    require(prerequisite.get("pins") == source_pins
            and recovery.get("family") == spec.name,
            "bind activation to every genuinely first-party semantic source")
    intentions = activation.authenticate_intentions(
        root, journal, journal_owner["sha256"])
    roles = activation.FAMILIES[spec.name]["targets"]
    require(set(intentions) == set(roles)
            and set(report.get("canonical_targets", {})) == set(roles)
            and "generated_header" not in roles
            and report.get("generated_go_header_promoted") is False,
            "authenticate every actual live promotion; never activate a Go header")
    expected_role_hashes = ({"bridge": pins["native_bridge"]}
                            if spec.combined_native
                            else {"engine": pins["native_engine"],
                                  "bridge": pins["native_bridge"]})
    require(set(expected_role_hashes) == set(roles),
            "preserve the exact combined C++ or separate Go native roles")
    for role, filename in roles.items():
        current = activation.current_canonical("candidates/" + filename)
        require(current is not None and activation.same_owner(
            current[1], report["canonical_targets"][role])
            and activation.same_owner(current[1], intentions[role]["target"])
            and current[1].get("sha256") == expected_role_hashes[role]
            and intentions[role]["intent"].get("mode") == 0o600,
            "reject a changed canonical target, missing intent, or false live inode")
    v1.exact_native_owners(spec, pins, source_pins)
    return {
        "family": spec.name, "build_version": options.build_version,
        "activation_version": 4,
        "activation_source_sha256": V4_ACTIVATION_SHA256,
        "activation_report_sha256": report_owner["sha256"],
        "activation_receipt_sha256": receipt_owner["sha256"],
        "recovery_journal_sha256": journal_owner["sha256"],
        "canonical_target_count": len(roles),
        "generated_go_header_promoted": False,
        "reversible_canonical_activation": True,
        "activation_started_by_producer": False,
    }


def run_actual_suite(options: argparse.Namespace) -> dict[str, Any]:
    context = verify_frozen_context(argparse.Namespace(
        source_sha256=options.source_sha256,
        protocol_sha256=options.protocol_sha256,
        document_sha256=options.document_sha256,
    ))
    require(context.get("status") == "PASS"
            and context.get("total_distinct_historical_evidence_owner_count") == 65,
            "authenticate all original suites and all 65 genuine history owners")
    v1 = frozen_module(V1_SOURCE_RELATIVE, V1_SOURCE_SHA256, V1_SOURCE_BYTES)
    spec = v1.family_spec(options.family)
    suite = v1.suite_spec(options.suite)
    source_pins = v1.parse_source_owners(spec, options.owned_source_sha256)
    pins = v1.native_pins(spec, options)
    if options.activation_source_sha256 == V4_ACTIVATION_SHA256:
        approval = authenticate_v4_activation(options, v1, spec)
    else:
        require(spec.name in {"rust", "c", "zig", "cpp"},
                "failed or unactivated families have no legacy activation")
        legacy, _ = v1.authenticate_actual_activation(options, spec)
        approval = {
            "family": legacy["family"],
            "build_version": options.build_version,
            "activation_source_sha256": options.activation_source_sha256,
            "reversible_canonical_activation": True,
            "activation_started_by_producer": False,
        }
    phase1_raw, _ = v1.read_owned(
        v1.PHASE1_RELATIVE, v1.PHASE1_SHA256,
        maximum=v1.MAX_SOURCE_BYTES)
    phase1 = v1.decode_document(phase1_raw, "unchanged original P0 phase one",
                                canonical_required=True)
    if suite.name == "original_bounded_v5":
        observed = v1.observe_original_upstream(suite, spec, pins, source_pins)
    elif suite.name == "subinterpreter_v2":
        observed = v1.observe_subinterpreters(
            suite, spec, pins, source_pins,
            producer_sha256=V1_SOURCE_SHA256)
    else:
        observed = v1.observe_direct_suite(
            suite, spec, pins, source_pins, phase1)
    observed["actual_verified_native_activation"] = approval
    observed["phase_one_case_execution_denominator"] = 31237
    observed["supplemental_cases_added_to_phase_one"] = False
    observed["total_preserved_historical_evidence_owner_count"] = 65
    return observed


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--family", choices=FAMILY_ORDER)
    parser.add_argument("--suite", choices=tuple(row[0] for row in SUITES))
    parser.add_argument("--label")
    parser.add_argument("--build-version", choices=("2", "3", "4", "5", "6"))
    parser.add_argument("--build-label")
    parser.add_argument("--activation-root")
    parser.add_argument("--owned-source-sha256", action="append", default=[])
    for name in (
        "source", "protocol", "document", "build-source", "build-protocol",
        "build-contract", "build-archive", "build-receipt", "activation-source",
        "activation-protocol", "activation-contract", "activation-report",
        "activation-receipt", "recovery-journal", "candidate-source",
        "native-engine", "native-bridge",
    ):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(arguments)
    all_optional = (
        "family", "suite", "label", "build_version", "build_label",
        "activation_root", "source_sha256", "protocol_sha256",
        "document_sha256", "build_source_sha256", "build_protocol_sha256",
        "build_contract_sha256", "build_archive_sha256", "build_receipt_sha256",
        "activation_source_sha256", "activation_protocol_sha256",
        "activation_contract_sha256", "activation_report_sha256",
        "activation_receipt_sha256", "recovery_journal_sha256",
        "candidate_source_sha256", "native_engine_sha256", "native_bridge_sha256",
    )
    if options.self_test:
        require(not options.owned_source_sha256
                and all(getattr(options, name) is None for name in all_optional),
                "source-only self-test accepts no paths, pins, activation, or matching")
        return options
    frozen_names = {"source_sha256", "protocol_sha256", "document_sha256"}
    for name in frozen_names:
        checked_digest(getattr(options, name), name)
    if options.verify_frozen_context:
        require(not options.owned_source_sha256
                and all(getattr(options, name) is None
                        for name in all_optional if name not in frozen_names),
                "read-only verification accepts only the exact three V2 freeze pins")
        return options
    require(options.run, "explicitly select one actual original P0 suite")
    for name in ("family", "suite", "label", "build_version", "build_label",
                 "activation_root"):
        require(type(getattr(options, name)) is str and bool(getattr(options, name)),
                "provide one exact actual suite option: " + name)
    require(options.build_version != "5" and options.family != "fortran",
            "failed Fortran and unsupported V5 activation are not runnable")
    for name in all_optional:
        if name.endswith("_sha256") and name not in {
            "build_contract_sha256", "activation_contract_sha256",
            "recovery_journal_sha256",
        }:
            checked_digest(getattr(options, name), name)
    if options.activation_source_sha256 == V4_ACTIVATION_SHA256:
        for name in ("build_contract_sha256", "activation_contract_sha256",
                     "recovery_journal_sha256"):
            checked_digest(getattr(options, name), name)
    else:
        for name in ("build_contract_sha256", "activation_contract_sha256",
                     "recovery_journal_sha256"):
            value = getattr(options, name)
            if value is not None:
                checked_digest(value, name)
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        options = parse_arguments(arguments)
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
            "error_message": str(error), **zero_effects(),
        }
        details = getattr(error, "details", None)
        if type(details) is dict:
            failure["actual_failure"] = details
            failure["actual_candidate_workers"] = details.get(
                "actual_candidate_workers", 0)
        try:
            sys.stdout.buffer.write(canonical(failure))
            sys.stdout.buffer.flush()
        except (OSError, ValueError, TypeError):
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
