#!/usr/bin/env python3
"""Independently verify and reversibly activate six owned V4 native engines.

`--self-test` is strictly in memory. `--verify-frozen-context` is read-only.
No build, activation, candidate import, worker, clock, or benchmark is implicit.
"""

from __future__ import annotations

import ast
import base64
import builtins
import copy
import ctypes
import gzip
import hashlib
import importlib
import io
import json
import os
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import types
import zlib
from pathlib import Path
from typing import Any


ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/activate_verified_native_candidate_v4.py"
PROTOCOL_RELATIVE = "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V4.md"
CONTRACT_RELATIVE = "oracle/phase2/verified-native-activation-v4.json"
SCHEMA = "rebar-phase2-verified-native-candidate-activation-v4"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
JOURNAL_SCHEMA = SCHEMA + "-recovery-journal"
INTENT_SCHEMA = SCHEMA + "-durable-promotion-intent"
RESTORATION_SCHEMA = SCHEMA + "-restoration-receipt"
REPORT_NAME = "activation-report.json"
RECEIPT_NAME = "activation-receipt.json"
JOURNAL_NAME = "recovery-journal.json"
PRIVATE_PREFIX = "rebar-phase2-verified-native-activation-v4-"
BUILD_PREFIX = "rebar-phase2-native-build-v4-"
BUILD_SCHEMA = "rebar-phase2-owned-native-source-build-v4"
BUILD_RECEIPT_SCHEMA = BUILD_SCHEMA + "-durable-publication-receipt"
SANITIZED_BUILD_ROOT = "<FRESH_PRIVATE_TMP>"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024
MAX_LABEL_BYTES = 48
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_INCLUDE = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
PINNED_GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_GXX = "/usr/bin/x86_64-linux-gnu-g++-13"
PINNED_GFORTRAN = "/usr/bin/x86_64-linux-gnu-gfortran-13"
PINNED_READELF = "/usr/bin/x86_64-linux-gnu-readelf"
PINNED_GO = "/home/dev-user/.openai/go/bin/go"
RUST_TOOLCHAIN = "/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu"
PINNED_RUSTC = RUST_TOOLCHAIN + "/bin/rustc"
PINNED_CARGO = RUST_TOOLCHAIN + "/bin/cargo"
PINNED_ZIG = "/tmp/zig-x86_64-linux-0.16.0/zig"
BUILD_SOURCE_RELATIVE = "tools/reproduce_owned_native_source_build_v4.py"
BUILD_SOURCE_SHA256 = "efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1"
BUILD_PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILD-V4.md"
BUILD_PROTOCOL_SHA256 = "e974b26562cc210c175c08cda7914e6b196fdee2ebe2a8232dd87c0cddbc0dfb"
BUILD_CONTRACT_RELATIVE = "oracle/phase2/native-source-build-v4.json"
BUILD_CONTRACT_SHA256 = "0b5641529bc49f55b9e56fe397ad38e7e23d6c9b3376587b743753814b8089d7"
PHASE1_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
PHASE1_SHA256 = "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f"

OWNER_FIELDS = ("relative", "path", "sha256", "size_bytes", "device", "inode", "mode")
DURABLE_FLAGS = ("exclusive_creation", "same_inode_readback_verified",
                 "file_fsync_completed", "directory_fsync_completed")
PROMOTION_FLAGS = ("atomic_replace_completed", "adjacent_exclusive_stage_verified",
                   "candidate_directory_fsync_completed")

SOURCE_OWNERS: dict[str, dict[str, tuple[str, int]]] = {
    "c": {
        "candidates/vm_candidate.py": ("b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096", 60707),
        "candidates/_vm_native.c": ("bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55", 218185),
    },
    "rust": {
        "candidates/rust_candidate.py": ("6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151),
        "candidates/rust/py_bridge.c": ("f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676),
        "candidates/rust/Cargo.toml": ("2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
        "candidates/rust/Cargo.lock": ("267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
        "candidates/rust/src/lib.rs": ("c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
        "candidates/rust/src/newline.rs": ("13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
        "candidates/rust/src/search.rs": ("4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
        "candidates/rust/src/stack.rs": ("5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
        "candidates/rust/src/unicode_tables.rs": ("f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
    },
    "zig": {
        "candidates/zig_candidate.py": ("2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862", 68422),
        "candidates/zig/mini_regex.zig": ("a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28", 186915),
        "candidates/zig/py_bridge.c": ("67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b", 173026),
    },
    "cpp": {
        "candidates/cpp_candidate.py": ("8dcece29b1a194eea023143148af37bb679a9df4c39c01153f5ee23f778e16d5", 27488),
        "candidates/cpp/engine.hpp": ("66998fed1839f5e5f7f09382830ed9fda1a62b80bd545305c4eee95ed9a13df9", 4089),
        "candidates/cpp/engine.cpp": ("a9ceb37cfde77447a01a36a8882f7713faf5f201d7a15a193dd17e7b91d118f5", 62813),
        "candidates/cpp/py_bridge.cpp": ("1d930b63b2f9493dd4759b7521f75d8846daf2580a5699337fcf82540484ab6d", 25068),
    },
    "go": {
        "candidates/go_candidate.py": ("816d21527b9806afbc9457122f72f8f6b62c39b8b791d3f363745d412cbe3d20", 31049),
        "candidates/go/go.mod": ("9297c4e8fe4649196150400d23a4da584d7ef721347f7095399a7382edad669b", 44),
        "candidates/go/engine.go": ("6472c4413921f3a877455315400c532e7632a871a96d46de9583fa6170a43192", 53782),
        "candidates/go/py_bridge.c": ("52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a", 39373),
    },
    "fortran": {
        "candidates/fortran_candidate.py": ("8db564771d38c0896a5207f1241a44463432dc5bf75dfcf657740d8bcfefd194", 26521),
        "candidates/fortran/engine.f90": ("5180da085487b9932e3f769e6baded6a8409a0b778890e6197aaea6dad1923a5", 85062),
        "candidates/fortran/py_bridge.c": ("8540b708de4819f1b3340c32e78eaf083c1cad35f016c0f7af33a27773694b0d", 26311),
    },
}

FAMILIES: dict[str, dict[str, Any]] = {
    "c": {"language": "C", "module": "candidates.vm_candidate", "targets": {"extension": "_vm_native" + EXTENSION_SUFFIX}, "generated": {}},
    "rust": {"language": "Rust", "module": "candidates.rust_candidate", "targets": {"engine": "_rust_engine.so", "bridge": "_rust_bridge" + EXTENSION_SUFFIX}, "generated": {}},
    "zig": {"language": "Zig", "module": "candidates.zig_candidate", "targets": {"engine": "_zig_probe.so", "bridge": "_zig_bridge" + EXTENSION_SUFFIX}, "generated": {}},
    "cpp": {"language": "C++", "module": "candidates.cpp_candidate", "targets": {"bridge": "_cpp_bridge" + EXTENSION_SUFFIX}, "generated": {}},
    "go": {"language": "Go", "module": "candidates.go_candidate", "targets": {"engine": "_go_engine.so", "bridge": "_go_bridge" + EXTENSION_SUFFIX}, "generated": {"generated_header": "_go_engine.h"}},
    "fortran": {"language": "Fortran", "module": "candidates.fortran_candidate", "targets": {"engine": "_fortran_engine.so", "bridge": "_fortran_bridge" + EXTENSION_SUFFIX}, "generated": {}},
}

ORIGINAL_GUARDS: dict[str, tuple[str, int]] = {
    "tools/independent_original_cpython_suite_v5.py": ("8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce", 123750),
    "tools/independent_original_cpython_suite_v4.py": ("1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3", 99365),
    "tools/rust_original_cpython_suite_v1.py": ("cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95", 67175),
    "tools/rust_original_cpython_suite_v2.py": ("569036804b557b01eb29ba404c6fea0ecc5806bdbc2b6b9eb61c1ea18aa79267", 53269),
    "tools/rust_original_cpython_suite_v3.py": ("55aced566c4ef0a236f26ddf4607dbe3e69ae9dc15ab6fd95399d4ddc346cea2", 35177),
}

FROZEN_SUPPORT: dict[str, tuple[str, str, int]] = {
    "objective": ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756),
    "phase1_manifest": (PHASE1_RELATIVE, PHASE1_SHA256, 45632),
    "phase1_protocol": ("oracle/phase1/P0-COMPLETENESS-V1.md", "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798", 10392),
    "phase1_verifier": ("tools/verify_p0_completeness_v1.py", "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c", 118040),
    "v4_build_source": (BUILD_SOURCE_RELATIVE, BUILD_SOURCE_SHA256, 136084),
    "v4_build_protocol": (BUILD_PROTOCOL_RELATIVE, BUILD_PROTOCOL_SHA256, 10848),
    "v4_build_contract": (BUILD_CONTRACT_RELATIVE, BUILD_CONTRACT_SHA256, 14354),
    "v2_build_source": ("tools/reproduce_phase2_native_builds_v2.py", "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796", 136677),
    "v2_build_protocol": ("oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md", "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603", 13032),
    "v3_build_source": ("tools/reproduce_phase2_native_builds_v3.py", "c33d8e89c4b86f06e7cc06ecef9bca7052af86191d2e09ac89e665500147ba6f", 175029),
    "v3_build_protocol": ("oracle/phase2/NATIVE-SOURCE-BUILDS-V3.md", "273e5de944b661ec1f5cfbe3a26bcabc2e9b8c04353891fcfb822b07955eace3", 7979),
    "v1_activation_source": ("tools/activate_verified_native_candidate_v1.py", "ebc2427f6981e12c136b7f9371e5c72bccd89e1362930ad63245751d76fef164", 192374),
    "v1_activation_protocol": ("oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V1.md", "8f69bc751ac07e6d0a55fe9563c0038838976873991e45c5a0967f0d21a989d2", 15893),
    "v2_activation_source": ("tools/activate_verified_native_candidate_v2.py", "e6e8a72feffcf670da9a3e4d2e8b642e933c1d81cfe5bf7d1636385f207d6218", 205006),
    "v2_activation_protocol": ("oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V2.md", "a675b411873c01ae88ea50d4f95aab7231a29dde38a458a947437f07ed850529", 10346),
    "v6_candidate_source": ("tools/run_frozen_p0_candidate_v6.py", "53c5abd71ba46384204f628238dfc4b91a9adf6c75f8edd838e6523300677a9c", 37434),
    "v6_candidate_worker": ("tools/run_frozen_p0_candidate_worker_v4.py", "b0111d76df52ead959863c4459ea1b78f78ab6b1e0d0417624df268860918d8b", 166854),
    "v6_candidate_protocol": ("oracle/phase2/P0-CANDIDATE-PROTOCOL-V6.md", "b1d50f9778257d25e22df7ddba493e6830c514365d25ded518ea832b5e175c39", 7730),
    "v6_candidate_matrix": ("oracle/phase2/p0-candidate-protocol-v6.json", "73cbdf73f94de18496793bafe4ab29c613d694bfde8c47e7ec8430d27a23b521", 21810),
    "v3_subinterpreter_source": ("tools/run_owned_candidate_subinterpreters_v3.py", "21febe241549963a2818af2a20782da81bdf952fb7be8affc4289d9ccc9ad5b4", 178752),
    "v3_subinterpreter_protocol": ("oracle/phase2/CANDIDATE-SUBINTERPRETERS-V3.md", "97354130b4d1ab97ee2c684b43b72e29a0a68439c2a1ead5a4f45edc20e6c9b4", 11754),
    "v3_subinterpreter_matrix": ("oracle/phase2/candidate-subinterpreters-v3.json", "17dac72e6a0ae75bf1f013656b9779a1e948e71439cf336499c1e680beb19284", 13963),
    "official_zig_lock": ("toolchains/zig-0.16.0.lock.json", "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd", 628),
    "historical_current_overview": ("docs/evidence/candidate-current-overview-v7.inputs.json", "744f86e241e3489cf07c5fccccf291eb68c44a50605d79723dd1ae1092d8511f", 22027),
    "v6_build_source": ("tools/reproduce_owned_native_source_build_v6.py", "2af9da3cb37a55782f3bfb8bdbdfdb7a945532994a5c988f4645d888dbe57ebc", 196660),
    "v6_build_protocol": ("oracle/phase2/NATIVE-SOURCE-BUILD-V6.md", "108dbd52144c78530221e36882a0070fe9805b1bef6a136caf4636148ae9131d", 10297),
    "v6_build_contract": ("oracle/phase2/native-source-build-v6.json", "0121aaa5902b449e107396d6a1107ca8fe0fefebb0a0f09eb58d2d19c8888db4", 29292),
    "v3_activation_source": ("tools/activate_verified_native_candidate_v3.py", "39a170d5981e3484366eca223c0533366d92927975271fdb004fbce784b7a21e", 238483),
    "v3_activation_protocol": ("oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V3.md", "17656cd0ea3aa879cc5c69078460118f1e5e977f3e5c8d977c784954ea9f65bf", 14180),
    "v3_activation_contract": ("oracle/phase2/verified-native-activation-v3.json", "87d2d34a142f620894b87b35f3216ede4a0374921a3dfacb9d8e209e3d3133fc", 11864),
}

HISTORICAL_RECORDS: dict[str, dict[str, Any]] = {
    "v2_c": {"family": "c", "status": "PASS", "archive": "oracle/phase2/evidence/native-source-build-v2-c-phase2-v2.json.gz", "archive_sha256": "4d954992312a039daa46a2810e51fc29cfdd2bd49d159dc834f5bf003e456878", "archive_bytes": 16016, "plain_sha256": "0d0a67a3c8ebba83806ba3b9beaee39e154f9d0483f0e39aac6bb04ecbfc598a", "plain_bytes": 169716, "receipt": "oracle/phase2/evidence/native-source-build-v2-c-phase2-v2-publication-receipt.json", "receipt_sha256": "e90b4c12a087c0e8864c1627e242be18bd779f9d9693ec711f7dd575288eda24", "receipt_bytes": 1639, "schema": "rebar-phase2-independent-native-source-build-v2", "process_count": 8},
    "v2_rust": {"family": "rust", "status": "PASS", "archive": "oracle/phase2/evidence/native-source-build-v2-rust-phase2-v2.json.gz", "archive_sha256": "69b645c14ca3e566256f5a5b393a6d18554ad347b97b542383db3d86681bb35d", "archive_bytes": 33741, "plain_sha256": "389a833d6a3ce6c7aed3216759278d97d8d02dd901f758815e002f7a0031d4ec", "plain_bytes": 279925, "receipt": "oracle/phase2/evidence/native-source-build-v2-rust-phase2-v2-publication-receipt.json", "receipt_sha256": "15580e4441ce651c21800df187fcfaa88ec9336322348a07d84544094d5b050e", "receipt_bytes": 2346, "schema": "rebar-phase2-independent-native-source-build-v2", "process_count": 16},
    "v2_zig_failure": {"family": "zig", "status": "FAIL", "archive": "oracle/phase2/evidence/native-source-build-v2-zig-phase2-v2-failures.json.gz", "archive_sha256": "dc5128aaaf8a4d915c57ea8770696db3dc7ca51c89d5a3570cab9d259d070a0e", "archive_bytes": 19556, "plain_sha256": "f6ea1eb57d9ceb23c6dc5d4f291c4eb300768460a658d97828b7ce0095c53652", "plain_bytes": 188479, "receipt": "oracle/phase2/evidence/native-source-build-v2-zig-phase2-v2-failures-publication-receipt.json", "receipt_sha256": "97e3150e9b68d3031c96ea6e973097687c80163a371f99a67f8b3de08bc0707a", "receipt_bytes": 1766, "schema": "rebar-phase2-independent-native-source-build-v2", "process_count": 15},
    "v3_zig": {"family": "zig", "status": "PASS", "archive": "oracle/phase2/evidence/native-source-build-v3-zig-phase2-v3.json.gz", "archive_sha256": "485fcf3434d2c46088f8e358ce43a34aee63e3f4aacb878e63109279afb2c46c", "archive_bytes": 25102, "plain_sha256": "9f1f5b6e4b4003fc1ddcfd5139953f1b6eb63d02bfc5bd8ed4decbcbe7bb696f", "plain_bytes": 238586, "receipt": "oracle/phase2/evidence/native-source-build-v3-zig-phase2-v3-publication-receipt.json", "receipt_sha256": "050f0156647c90ed03ebffe7d530e0a9f56d605f3728df618c85dc2f8ae570e8", "receipt_bytes": 1748, "schema": "rebar-phase2-independent-native-source-build-v3", "process_count": 15},
    "v6_zig_candidate_failure": {"family": "zig", "status": "FAIL", "archive": "oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-failures.json.gz", "archive_sha256": "2ca2a253e4148c4232327cf89f1306c1c4e83639714f3b036ebdd7bd0225aaa3", "archive_bytes": 850155, "plain_sha256": "2afa993835d45f30838971b5c68c397e9d6271877e77f32919aee955554ce9f6", "plain_bytes": 24903358, "receipt": "oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-failures-publication-receipt.json", "receipt_sha256": "72c2635850273543eded2e9f541cb64529f2ce22a9d6fe5b14c30705fa474c95", "receipt_bytes": 1145, "schema": "rebar-frozen-python-re-p0-candidate-v6-actual-complete-candidate", "process_count": None},
    "v6_zig_worker_failure": {"family": "zig", "status": "FAIL", "archive": "oracle/phase2/evidence/frozen-p0-candidate-worker-v4-zig-phase2-v6-failures.json.gz", "archive_sha256": "07a1be40b4aba273bdec1f5d567aad0c6fbbf860189ade527eb90cfed1aab594", "archive_bytes": 848777, "plain_sha256": "472f832152aab4550a635891b24415971171f8101e1171c010dc56cfc62751a0", "plain_bytes": 24899336, "receipt": "oracle/phase2/evidence/frozen-p0-candidate-worker-v4-zig-phase2-v6-failures-publication-receipt.json", "receipt_sha256": "8c5f69411600781dca1efd3965b98fcecf9a1fec00afb4e5f7d319c2afa86cf4", "receipt_bytes": 1159, "schema": "rebar-frozen-python-re-p0-candidate-worker-v4-complete-candidate-evaluation", "process_count": None},
    "v6_zig_subinterpreter_failure": {"family": "zig", "status": "FAIL", "archive": "oracle/phase2/evidence/owned-candidate-subinterpreters-v3-zig-phase2-v6-subinterpreters-failures.json.gz", "archive_sha256": "ded1049f0d1979b6a71c80fcd86fe411e400603b02bbe28ed8b3634f513612f4", "archive_bytes": 104089, "plain_sha256": "a5280c4713fdc2e494f8e2bd0b1eeab9f6199dceede5d410bc1f8108e286cf67", "plain_bytes": 1581106, "receipt": "oracle/phase2/evidence/owned-candidate-subinterpreters-v3-zig-phase2-v6-subinterpreters-failures-publication-receipt.json", "receipt_sha256": "8fc8e0753458e69751fd45b820764e7c085ec6111c9dcda64ee90ef227b0ce21", "receipt_bytes": 1892, "schema": "rebar-owned-candidate-subinterpreters-v3-candidate-evaluation", "process_count": None},
}

HISTORICAL_V4_RECORDS: dict[str, dict[str, Any]] = {
    "cpp": {
        "family": "cpp", "status": "PASS", "label": "phase2-v4",
        "archive": "oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4.json.gz",
        "archive_sha256": "48910a6328e8aaacdac993b2c029995d878960a456359a14db5c83b9fc518df9",
        "archive_bytes": 20605,
        "plain_sha256": "b0141e8d17dc5cafddd7e5a7901e1e2babb4822f0fff7cc7e1201ab625276243",
        "plain_bytes": 175104,
        "receipt": "oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4-publication-receipt.json",
        "receipt_sha256": "7742eda3ce777b1378d0c7fb87fc064f222850ca8bcf15cd23ff8a4d87d8bebf",
        "receipt_bytes": 2074, "process_count": 10, "completed_phase_count": 2,
        "phase_outputs": (
            {"bridge": ("d444611316caceb4ba08783203bc4f1d396a8987f63a49bd24c81d5d2c532441", 130744)},
            {"bridge": ("d444611316caceb4ba08783203bc4f1d396a8987f63a49bd24c81d5d2c532441", 130744)},
        ),
    },
    "go": {
        "family": "go", "status": "FAIL", "label": "phase2-v4",
        "archive": "oracle/phase2/evidence/native-source-build-v4-go-phase2-v4-failures.json.gz",
        "archive_sha256": "fcf643b7b8e9fbe80bd3b40c7ed884695a844f46e1117f5ebdb130135e5db4bb",
        "archive_bytes": 4095,
        "plain_sha256": "aded8de4563397acef41697abbb91d73c3214daa2054a0f118e4946bd982b105",
        "plain_bytes": 12214,
        "receipt": "oracle/phase2/evidence/native-source-build-v4-go-phase2-v4-failures-publication-receipt.json",
        "receipt_sha256": "215e9680bbe0f8d2250fcca8bae0335017606288e13e7636224b7c76336b5e41",
        "receipt_bytes": 2075, "process_count": 4, "completed_phase_count": 0,
        "phase_outputs": (),
        "error_message": "the exact independently owned compiler or ELF command failed: build_go_engine",
    },
    "fortran": {
        "family": "fortran", "status": "FAIL", "label": "phase2-v4",
        "archive": "oracle/phase2/evidence/native-source-build-v4-fortran-phase2-v4-failures.json.gz",
        "archive_sha256": "ba35ea4f0d28814f716a36d2ccb384ef034a88a4029ca3f3cbf4f91eae268103",
        "archive_bytes": 14825,
        "plain_sha256": "a0e72b44b40bf2dcc4e60d50a8996fa344ead3fa5d3056b3509de90260b3cfb1",
        "plain_bytes": 140723,
        "receipt": "oracle/phase2/evidence/native-source-build-v4-fortran-phase2-v4-failures-publication-receipt.json",
        "receipt_sha256": "86b4b2648adf651481eea8d8b427a432f121c59322f508b522eca18af0749a08",
        "receipt_bytes": 2019, "process_count": 18, "completed_phase_count": 2,
        "phase_outputs": (
            {"engine": ("37557a44033a80aa11a81fa145ca76c2bbd44ee544b31974dcf6e59ba0f2949c", 74624),
             "bridge": ("eba8c1d145a53a2017fc9b7a6e4651b31ec4aef2e67e6c176c6435bffafc7b26", 37424)},
            {"engine": ("696126d3f3e7239cac55975f53beb3b5e5cffc6948f08258817b6b2d86422199", 74624),
             "bridge": ("eba8c1d145a53a2017fc9b7a6e4651b31ec4aef2e67e6c176c6435bffafc7b26", 37424)},
        ),
        "error_message": "the two independently owned outputs are not genuinely byte-identical",
    },
}

BUILD_V6_PREFIX = "rebar-phase2-native-build-v6-"
BUILD_V6_SCHEMA = "rebar-phase2-owned-native-source-build-v6"
BUILD_V6_RECEIPT_SCHEMA = BUILD_V6_SCHEMA + "-durable-publication-receipt"
BUILD_V6_SOURCE_RELATIVE = "tools/reproduce_owned_native_source_build_v6.py"
BUILD_V6_SOURCE_SHA256 = "2af9da3cb37a55782f3bfb8bdbdfdb7a945532994a5c988f4645d888dbe57ebc"
BUILD_V6_PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILD-V6.md"
BUILD_V6_PROTOCOL_SHA256 = "108dbd52144c78530221e36882a0070fe9805b1bef6a136caf4636148ae9131d"
BUILD_V6_CONTRACT_RELATIVE = "oracle/phase2/native-source-build-v6.json"
BUILD_V6_CONTRACT_SHA256 = "0121aaa5902b449e107396d6a1107ca8fe0fefebb0a0f09eb58d2d19c8888db4"

HISTORICAL_V5_RECORDS: dict[str, dict[str, Any]] = {
    "go": {
        "family": "go",
        "build_status": "FAIL",
        "receipt_status": "PASS",
        "archive_path": "oracle/phase2/evidence/native-source-build-v5-go-phase2-v5-failures.json.gz",
        "archive_sha256": "ff92f5f182307b5e6e123ab883e630c6aca63f8c75318fa4ac083b1d72db6169",
        "archive_bytes": 5595,
        "uncompressed_sha256": "7dfa02625cb532d2dd65491a65ca8a04848041fc6dc2fd5547bac2e3c8b7a685",
        "uncompressed_bytes": 18380,
        "receipt_path": "oracle/phase2/evidence/native-source-build-v5-go-phase2-v5-failures-publication-receipt.json",
        "receipt_sha256": "00a126f6c462913ad00ea9961334bbeb5aa2bfd1301d02d8f8c5d55c2e239db0",
        "receipt_bytes": 2903,
        "process_count": 5,
        "expected_process_count": 26,
        "successful_process_count": 4,
        "completed_build_phase_count": 0,
        "failed_process": "build_go_bridge",
        "stderr_sha256": "6477560bffdde31d9422ba4c8addbb1a733cb0becbd09b5815d51d837caf477a",
        "stderr_bytes": 2640,
        "failure_cause": "THE REAL GENERATED GO HEADER PRECEDES PYTHON.H WITHOUT THE GNU FEATURE-TEST MACRO; SSIZE_MAX IS UNDECLARED",
        "go_engine_compiler_status": "PASS",
        "go_bridge_compiler_status": "FAIL",
    },
    "fortran": {
        "family": "fortran",
        "build_status": "FAIL",
        "receipt_status": "PASS",
        "archive_path": "oracle/phase2/evidence/native-source-build-v5-fortran-phase2-v5-failures.json.gz",
        "archive_sha256": "eadf8844a1bda48d2420c7b3311ced77de9fda7ccfb806f73764550080823e53",
        "archive_bytes": 26274,
        "uncompressed_sha256": "4e3a8a2e9cb03fe12105f40499da6055b9adb3336667b9af801579106b991996",
        "uncompressed_bytes": 167482,
        "receipt_path": "oracle/phase2/evidence/native-source-build-v5-fortran-phase2-v5-failures-publication-receipt.json",
        "receipt_sha256": "f9bf0a652e9c10c949d7b5faabf261d3931681548d4f5d1af69f0accc6d742f2",
        "receipt_bytes": 2848,
        "process_count": 26,
        "expected_process_count": 26,
        "successful_process_count": 26,
        "completed_build_phase_count": 2,
        "failed_process": None,
        "engine_phase_a_sha256": "6f005b6f1ec68658857ee2ba9c21e21d65cd4c41aa8fd608d6060712db63164a",
        "engine_phase_b_sha256": "0d1f94c1b51e0cf6527ce742c092bffe9f0ae1207b0414bab6b5be56e9b7f092",
        "engine_bytes_per_phase": 74624,
        "identical_bridge_sha256": "0e4197e9b16df93f5d29333fcfda928d1d29c193c0449afb730146819229faf8",
        "bridge_bytes_per_phase": 37424,
        "engine_phase_a_notes_sha256": "a9c8293e6992db8ec091b2433fd70aed141a82f0a87ff72868b1cb1638364069",
        "engine_phase_b_notes_sha256": "8c80c8e47f3ca4293f6d788eeeb15a89291cb7ce49fa6b7f80af6a3131f66970",
        "engine_notes_bytes_per_phase": 226,
        "identical_engine_sections_sha256": "c9e2b603f3bb619345d44ee5239b5c90fc0297c622c4716fcc0457e9b3c9a18b",
        "engine_sections_bytes_per_phase": 2923,
        "phase_a_observed_gnu_build_id": "40a5c3208328deb836a2cf72b745119444150bf0",
        "phase_b_observed_gnu_build_id": "2fd1e7d8db83bd204cd22717868f8c40c360a62a",
        "identical_bridge_notes_sha256": "af2d8b6bc80b0693c00e9b6235a0857c33aa209bcc9a00ac0678e7eecceddbae",
        "bridge_notes_bytes_per_phase": 418,
        "failure_cause": "TWO COMPLETED FIRST-PARTY FORTRAN ENGINES ARE NOT BYTE IDENTICAL",
        "differing_raw_binary_section": "NOT RECORDED",
        "all_compiler_and_inspection_processes_succeeded": True,
    },
}

HISTORICAL_V6_RECORDS: dict[str, dict[str, Any]] = {
    "go": {
        "family": "go",
        "status": "PASS",
        "label": "phase2-v6",
        "archive": "oracle/phase2/evidence/native-source-build-v6-go-phase2-v6.json.gz",
        "archive_sha256": "05c24a5fff228d8eab8bec961d825b0e65504072e11e8c574ec580d9f3e6e245",
        "archive_bytes": 37619,
        "plain_sha256": "37c97e72530ffc1022741429be2ffc9eebe7afaec6063c763d7ff86f6f7bd8ae",
        "plain_bytes": 262323,
        "receipt": "oracle/phase2/evidence/native-source-build-v6-go-phase2-v6-publication-receipt.json",
        "receipt_sha256": "f3adcb20bb591946600e1e2b1db037fb3b4828c3d4a628a0347cfed40f262fca",
        "receipt_bytes": 3262,
        "process_count": 26,
        "completed_phase_count": 2,
        "native_outputs": {
            "engine": {
                "sha256": "38ab223b8ef88340a7be86f2195c417ee7d2dd9deead48cc6495a5b4e3c31b27",
                "size_bytes": 2712912,
            },
            "bridge": {
                "sha256": "dd71ab6cb15a98e1a07c38965cdb178da0dbba2a26db937975e0d6435a2a5d0c",
                "size_bytes": 41904,
            },
            "generated_header": {
                "sha256": "481ebb65cc587749677ce28abeb4f3de111e2f87a18ac547ff0157fce85d2c23",
                "size_bytes": 3086,
            },
        },
    },
    "fortran": {
        "family": "fortran",
        "status": "FAIL",
        "label": "phase2-v6",
        "archive": "oracle/phase2/evidence/native-source-build-v6-fortran-phase2-v6-failures.json.gz",
        "archive_sha256": "c62007d5519d1ef723da7e144b1c6eeb067aacf47e960638e9d6b8a604f05d12",
        "archive_bytes": 26102,
        "plain_sha256": "b8186f02586e134b5db4275688513670cad814526ce4b42cad50802ed9f2f32b",
        "plain_bytes": 166999,
        "receipt": "oracle/phase2/evidence/native-source-build-v6-fortran-phase2-v6-failures-publication-receipt.json",
        "receipt_sha256": "6bc1ea1695247d8d137e6c2f50908b6c3a0518ff82978258bd07e8010e88ad7a",
        "receipt_bytes": 3221,
        "process_count": 26,
        "successful_process_count": 26,
        "completed_phase_count": 2,
        "error": {
            "message": "the two independently owned outputs are not genuinely byte-identical",
            "type": "BuildError",
        },
        "phase_outputs": [
            {
                "name": "reference-a",
                "native_outputs": {
                    "bridge": {
                        "sha256": "f0808671b4d16f9b8d74a891d04ccd78bcf2e568ae2edbfb3997fb0db23c2fd7",
                        "size_bytes": 37424,
                        "notes_sha256": "5fd30267211f09f3cddc7f0a13e1d25e6382766db4182615f8db62c461390a3e",
                        "notes_bytes": 418,
                        "sections_sha256": "0ac6e700b452a3eb1c1cc64d838a4af59cedaaa768a38a37f3448688cd2d5b23",
                        "sections_bytes": 3101,
                    },
                    "engine": {
                        "sha256": "6ed7afa0b7c2eb905cd00de0ec935a7c449f257431d44aaa652ae0f10191d1f7",
                        "size_bytes": 74544,
                        "notes_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        "notes_bytes": 0,
                        "sections_sha256": "3f15407ebd8d72adb59d7ffc87f4c43195ed5417c595e92e05d941ad244992c3",
                        "sections_bytes": 2833,
                    },
                },
            },
            {
                "name": "reference-b",
                "native_outputs": {
                    "bridge": {
                        "sha256": "f0808671b4d16f9b8d74a891d04ccd78bcf2e568ae2edbfb3997fb0db23c2fd7",
                        "size_bytes": 37424,
                        "notes_sha256": "5fd30267211f09f3cddc7f0a13e1d25e6382766db4182615f8db62c461390a3e",
                        "notes_bytes": 418,
                        "sections_sha256": "0ac6e700b452a3eb1c1cc64d838a4af59cedaaa768a38a37f3448688cd2d5b23",
                        "sections_bytes": 3101,
                    },
                    "engine": {
                        "sha256": "1458072addc7988975317ac81d64748970ee3d4321437be73275a700fed831c9",
                        "size_bytes": 74544,
                        "notes_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        "notes_bytes": 0,
                        "sections_sha256": "3f15407ebd8d72adb59d7ffc87f4c43195ed5417c595e92e05d941ad244992c3",
                        "sections_bytes": 2833,
                    },
                },
            },
        ],
        "differing_raw_binary_section": "NOT RECORDED",
    },
}

V6_REPORT_FIELDS = frozenset((
    "actual_v6_compiler_process_count", "benchmark_files_read",
    "build_phases", "candidate_correctness", "candidate_imports",
    "candidate_processes_started", "clock_samples", "contract_sha256",
    "evidence_accounting", "expected_v6_compiler_process_count", "family",
    "final_cases_read", "fresh_private_root", "frozen_correctness",
    "go_private_package_reproducibility", "hidden_cases_read",
    "historical_candidate_evidence_owner_count", "holdout", "label",
    "memory", "native_libraries_loaded", "network_requests",
    "owned_source_after", "owned_source_before", "owned_source_sha256",
    "performance", "pinned_toolchains", "preserved_v2_history",
    "preserved_v4_history", "processes", "protocol_sha256",
    "reference_processes_started", "reproducibility", "schema",
    "source_sha256", "status", "subinterpreter_isolation",
    "timing_trials_run", "undefined_behavior", "version", "winner_selected",
))
V6_RECEIPT_FIELDS = frozenset((
    "actual_v6_compiler_process_count", "archive_bytes",
    "archive_directory_fsync", "archive_publication", "archive_relative",
    "archive_sha256", "benchmark_files_read", "build_status",
    "candidate_correctness", "candidate_imports",
    "candidate_processes_started", "clock_samples", "contract_sha256",
    "evidence_accounting", "expected_v6_compiler_process_count", "family",
    "hidden_cases_read", "holdout", "label", "memory",
    "native_libraries_loaded", "owned_source_sha256", "performance",
    "phase1_manifest_sha256", "protocol_sha256", "receipt_self_publication",
    "schema", "source_sha256", "status", "subinterpreter_isolation",
    "timing_trials_run", "uncompressed_bytes", "uncompressed_sha256",
    "undefined_behavior", "winner_selected",
))
V6_PROCESS_FIELDS = frozenset((
    "argv", "environment", "exit_status", "name", "pid", "shell",
    "stderr_base64", "stderr_bytes", "stderr_sha256",
    "stdout_base64", "stdout_bytes", "stdout_sha256",
    "working_directory",
))
V6_SOURCE_OWNER_FIELDS = frozenset((
    "device", "executable", "inode", "path", "sha256", "size_bytes",
))
V6_PHASE_SOURCE_FIELDS = frozenset((
    "bytes", "device", "exclusive_creation", "file_fsync_completed",
    "inode", "path", "same_inode_readback_verified", "sha256",
    "write_calls",
))
V6_OUTPUT_FIELDS = frozenset((
    "audit", "candidate_imported", "device", "family", "file_name",
    "inode", "path", "prebuilt_artifact_read", "role", "sha256",
    "size_bytes",
))
V6_PUBLICATION_FIELDS = frozenset((
    "bytes", "device", "exclusive_creation", "file_fsync_completed",
    "inode", "path", "same_inode_readback_verified", "sha256",
    "write_calls",
))

RESTORATION_RELATIVE = "oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-restoration-receipt.json"
RESTORATION_SHA256 = "c415ba80c055d39a933617a839624037b557adbe30c418c2a0e859131fbe9028"
RESTORATION_BYTES = 2646
RESTORED_ZIG = {
    "bridge": ("candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so", "d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b", 134112, 0o700),
    "engine": ("candidates/_zig_probe.so", "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652", 478432, 0o700),
}

ZIG_V6_SUBORDINATE: tuple[tuple[str, str, int], ...] = (
    ("experiments/rust_public_practice_v1/zig-managed-buffer-lifetime-v1-phase2-v6-managed.json.gz", "43a8cf60484c46e85ba7b5853f38ee4c250f4383186dc33eb08162b30d0c897a", 721662),
    ("experiments/rust_public_practice_v1/zig-managed-buffer-lifetime-v1-phase2-v6-managed-publication-receipt.json", "d28c95236df9b19e5ab27a1174d5b8616cf2ba22394314ee2dcb78c13034d516", 6020),
    ("experiments/rust_public_practice_v1/zig-scanner-verbose-comments-v1-phase2-v6-verbose.json.gz", "ec5b4e20e05bdd068d065cf9ace9d4d988220565b29db0be91c15b1fa5a0403f", 432085),
    ("experiments/rust_public_practice_v1/zig-scanner-verbose-comments-v1-phase2-v6-verbose-publication-receipt.json", "3e8d850af3ad191c24b92182ed4e694c44c23716b37c607a31c50c45659428d9", 9649),
    ("experiments/rust_public_practice_v1/zig-public-type-identity-serialization-v1-phase2-v6-types.json.gz", "482dc8ba52e091e909a4d4acf6d57f964fc2e6fe8a729a105e8aca2b9448c2c6", 500563),
    ("experiments/rust_public_practice_v1/zig-public-type-identity-serialization-v1-phase2-v6-types-publication-receipt.json", "82f96615d0894b99ed1316df6fde2c713e3d7d4b19f18cf71a7e97e82a2352df", 14086),
    ("experiments/rust_public_practice_v1/zig-substitution-buffer-semantics-v2-phase2-v6-substitution.json.gz", "d83cdc6bb1b5bb878e55e5fea866eaec6c07e9dd78f983858cecc15463ac6de2", 804923),
    ("experiments/rust_public_practice_v1/zig-substitution-buffer-semantics-v2-phase2-v6-substitution-publication-receipt.json", "9b4c4daaf775bb585a3dcfbe693b91c14d49eb09aafd79360fb41ed5cd083791", 14770),
    ("experiments/rust_public_practice_v1/zig-shape-changing-buffer-semantics-v2-phase2-v6-shape.json.gz", "b4766c3c3547ea347421bf4784ac11eb2b63e6065135002139fdb17ca69bc7c8", 1505552),
    ("experiments/rust_public_practice_v1/zig-shape-changing-buffer-semantics-v2-phase2-v6-shape-publication-receipt.json", "e020e83774064cb9c9c9f9a70229ad3bcd04b0e417942317be4fbdb33f365ba9", 12532),
)

GO_EXPORTS = frozenset({"rebar_go_compile", "rebar_go_release", "rebar_go_group_count", "rebar_go_flags", "rebar_go_name_count", "rebar_go_name_group", "rebar_go_name_length", "rebar_go_copy_name", "rebar_go_execute"})
FORTRAN_EXPORTS = frozenset({"rebar_fortran_compile", "rebar_fortran_destroy", "rebar_fortran_group_count", "rebar_fortran_effective_flags", "rebar_fortran_name_count", "rebar_fortran_name_length", "rebar_fortran_name_group", "rebar_fortran_copy_name", "rebar_fortran_execute"})
FORTRAN_CALLBACKS = frozenset({"rebar_fortran_unicode_case_key", "rebar_fortran_locale_case_key", "rebar_fortran_locale_is_word"})
RUST_EXPORTS = frozenset({"rebar_collect_ascii", "rebar_collect_wide", "rebar_compile", "rebar_compile_scanner", "rebar_error_copy", "rebar_error_include", "rebar_error_len", "rebar_error_pos", "rebar_flags", "rebar_free", "rebar_groups", "rebar_match", "rebar_match_ascii", "rebar_match_wide", "rebar_name_copy", "rebar_name_count", "rebar_name_group", "rebar_name_len"})
ZIG_EXPORTS = frozenset({"rebar_zig_batch", "rebar_zig_collect_captures", "rebar_zig_collect_records", "rebar_zig_collect_records_wide", "rebar_zig_compile", "rebar_zig_compile_guarded", "rebar_zig_flags", "rebar_zig_free", "rebar_zig_groups", "rebar_zig_match", "rebar_zig_match_captures", "rebar_zig_match_captures_wide", "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide", "rebar_zig_match_tree", "rebar_zig_match_wide", "rebar_zig_name_copy", "rebar_zig_name_count", "rebar_zig_name_group", "rebar_zig_name_length", "rebar_zig_program_memory", "rebar_zig_program_size"})
FORBIDDEN_MODULES = frozenset({"re", "_sre", "regex", "regexp", "re2", "pcre", "pcre2", "oniguruma", "hyperscan", "sre_compile", "sre_constants", "sre_parse"})
FORBIDDEN_NATIVE_NAMES = frozenset({"regex", "regexp", "regcomp", "regexec", "regfree", "dlopen", "dlmopen", "dlsym", "dlvsym", "execv", "execve", "fork", "popen", "posix_spawn", "system", "execute_command_line", "PyRun_AnyFile", "PyRun_SimpleString", "PyRun_String", "Py_CompileString", "PyEval_EvalCode"})
FORBIDDEN_PREFIXES = ("hs_", "onig_", "pcre2_", "pcre_", "re2_", "regex_", "regexp_", "sre_", "_sre", "PyInit__sre", "PyRun_", "PyEval_Eval")
FAMILY_LIBRARIES: dict[str, frozenset[str]] = {
    "c": frozenset({"libc.so.6"}),
    "rust": frozenset({"libc.so.6", "libm.so.6", "libgcc_s.so.1", "ld-linux-x86-64.so.2"}),
    "zig": frozenset({"libc.so.6", "libm.so.6", "ld-linux-x86-64.so.2"}),
    "cpp": frozenset({"libc.so.6", "libm.so.6", "libgcc_s.so.1", "libstdc++.so.6", "ld-linux-x86-64.so.2"}),
    "go": frozenset({"libc.so.6", "libm.so.6", "libgcc_s.so.1", "ld-linux-x86-64.so.2"}),
    "fortran": frozenset({"libc.so.6", "libm.so.6", "libgcc_s.so.1", "libgfortran.so.5", "libquadmath.so.0", "ld-linux-x86-64.so.2"}),
}


class ActivationError(Exception):
    """An ownership, native-proof, durability, or recovery gate failed."""


class SourceOnlyEffect(ActivationError):
    """An in-memory self-test attempted an actual external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ActivationError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise ActivationError("complete finite canonical JSON is mandatory") from error


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only exact authenticated bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(ch in "0123456789abcdef" for ch in value),
            "an exact lowercase SHA-256 is required: " + label)
    return value


def checked_family(value: Any) -> str:
    require(type(value) is str and value in FAMILIES,
            "select exactly one independently owned C, Rust, Zig, C++, Go, or Fortran family")
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512
            and not value.startswith("/") and "\\" not in value and "\x00" not in value
            and all(part not in ("", ".", "..") for part in value.split("/")),
            "reject an absolute, traversing, empty, or disguised owned relative path")
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL_BYTES
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(ch in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in value)
            and "--" not in value and not value.endswith("-"),
            "require one exact lowercase, bounded, actual V4 build label")
    return value


def checked_positive_size(value: Any, label: str) -> int:
    require(type(value) is int and 0 < value <= MAX_BINARY_BYTES,
            "require a genuine positive, bounded integer byte count: " + label)
    return value


def checked_private_root(
    value: Any,
    family: str,
    *,
    build: bool,
    build_version: int | None = None,
) -> str:
    family = checked_family(family)
    require(type(build) is bool,
            "select an explicit build or reversible-activation root")
    if build:
        require(build_version is None
                or (type(build_version) is int
                    and build_version in {4, 6}),
                "select only an exact independently frozen source-build version")
        prefixes = {
            4: BUILD_PREFIX,
            6: BUILD_V6_PREFIX,
        }
        allowed = (
            tuple(prefixes.values())
            if build_version is None
            else (prefixes[build_version],)
        )
    else:
        require(build_version is None,
                "recovery roots cannot masquerade as versioned build roots")
        allowed = (PRIVATE_PREFIX,)
    require(type(value) is str
            and any(
                value.startswith("/tmp/" + prefix + family + "-")
                for prefix in allowed
            )
            and "\\" not in value and "\x00" not in value
            and value == value.rstrip("/")
            and len(value.split("/")) == 3
            and all(part not in ("", ".", "..")
                    for part in value.split("/")[1:]),
            "reject a broad, redirected, cross-version, or foreign private root")
    return value


def unique_json_pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "reject duplicated or non-string signed JSON keys")
        result[key] = value
    return result


def reject_json_constant(value: str) -> Any:
    raise ActivationError("reject non-finite signed JSON: " + value)


def decode_document(raw: Any, label: str, *, exact: bool = True) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
            "a complete bounded JSON record is mandatory: " + label)
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_json_pairs,
                           parse_constant=reject_json_constant)
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ActivationError("reject an invalid or truncated record: " + label) from error
    require(type(value) is dict, "require a top-level JSON object: " + label)
    if exact:
        require(canonical(value) == raw, "the exact canonical record changed: " + label)
    return value


def bounded_gzip(raw: Any, *, expected_size: int | None = None) -> bytes:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES,
            "require one complete bounded gzip archive")
    try:
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        plain = decoder.decompress(raw, MAX_REPORT_BYTES + 1)
        require(len(plain) <= MAX_REPORT_BYTES and not decoder.unconsumed_tail
                and decoder.eof and not decoder.unused_data,
                "reject an oversized, concatenated, appended, or truncated archive")
        plain += decoder.flush()
    except (zlib.error, ValueError) as error:
        raise ActivationError("reject a malformed compressed owner") from error
    require(len(plain) <= MAX_REPORT_BYTES
            and (expected_size is None or len(plain) == expected_size),
            "the complete uncompressed evidence has the wrong bounded size")
    return plain


def zero_effects() -> dict[str, Any]:
    return {
        "candidate_processes_started": 0, "reference_processes_started": 0,
        "candidate_imports": 0, "native_libraries_loaded": 0,
        "network_requests": 0, "hidden_cases_read": 0,
        "final_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "subinterpreter_isolation": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def expected_source_build() -> dict[str, Any]:
    return {
        "version": 4, "schema": BUILD_SCHEMA, "receipt_schema": BUILD_RECEIPT_SCHEMA,
        "source_path": BUILD_SOURCE_RELATIVE, "source_sha256": BUILD_SOURCE_SHA256,
        "protocol_path": BUILD_PROTOCOL_RELATIVE, "protocol_sha256": BUILD_PROTOCOL_SHA256,
        "contract_path": BUILD_CONTRACT_RELATIVE, "contract_sha256": BUILD_CONTRACT_SHA256,
        "private_root_prefix": "/tmp/" + BUILD_PREFIX,
        "evidence_prefix": EVIDENCE_RELATIVE + "/native-source-build-v4-",
        "independent_source_phase_count": 2,
        "actual_build_status": "CPP PASS; GO FAIL; FORTRAN FAIL",
        "historical_published_build_count": 3,
        "historical_successful_build_families": ["cpp"],
        "historical_failed_build_families": ["go", "fortran"],
        "builds_started_by_activation_freeze": 0,
        "additional_source_build": {
            "version": 6,
            "schema": BUILD_V6_SCHEMA,
            "receipt_schema": BUILD_V6_RECEIPT_SCHEMA,
            "source_path": BUILD_V6_SOURCE_RELATIVE,
            "source_sha256": BUILD_V6_SOURCE_SHA256,
            "protocol_path": BUILD_V6_PROTOCOL_RELATIVE,
            "protocol_sha256": BUILD_V6_PROTOCOL_SHA256,
            "contract_path": BUILD_V6_CONTRACT_RELATIVE,
            "contract_sha256": BUILD_V6_CONTRACT_SHA256,
            "private_root_prefix": "/tmp/" + BUILD_V6_PREFIX,
            "independent_source_phase_count": 2,
            "historical_published_builds": [
                {
                    "family": item["family"],
                    "build_status": item["status"],
                    "process_count": item["process_count"],
                    "completed_phase_count": item["completed_phase_count"],
                }
                for item in HISTORICAL_V6_RECORDS.values()
            ],
            "builds_started_by_activation_freeze": 0,
        },
    }


def expected_recovery_policy() -> dict[str, Any]:
    return {
        "root_prefix": "/tmp/" + PRIVATE_PREFIX, "root_mode": "0700",
        "evidence_mode": "0600", "journal_name": JOURNAL_NAME,
        "report_name": REPORT_NAME, "receipt_name": RECEIPT_NAME,
        "intention_prefix": "promotion-intent-",
        "backup_prefix": "backups/candidates/", "canonical_import_root": ROOT,
        "target_promotion": "INDIVIDUALLY ATOMIC; NEVER GROUP-ATOMIC",
        "backup": "EXACT ORIGINAL BYTES, MODE, DEVICE, AND INODE",
        "absent_original": "RECORDED TRUTHFULLY; NO FABRICATED BACKUP",
        "staging": "ADJACENT, EXCLUSIVE, NO-FOLLOW, AND FSYNCED",
        "intention": "DURABLE AND OWNER-ONLY BEFORE EACH ATOMIC REPLACEMENT",
        "reportless_recovery": "JOURNAL AND PER-ROLE INTENTION; NO REPORT OR RECEIPT REQUIRED",
        "modified_user_target": "NEVER OVERWRITE OR DELETE",
        "native_loader": "NOT USED", "external_regular_expression_engine": "FORBIDDEN",
        "cross_family_matching_engine": "FORBIDDEN",
    }


def expected_phase_boundary() -> dict[str, Any]:
    return {
        "actual_v4_source_builds": "NOT RUN",
        "actual_v6_source_builds": "NOT RUN",
        "actual_v3_activations": "NOT RUN",
        "actual_v4_activations": "NOT RUN",
        "qualified_candidate_count": 0,
        **zero_effects(),
    }


def _expected_legacy_historical_evidence() -> dict[str, Any]:
    return {
        "overview_input_path": FROZEN_SUPPORT["historical_current_overview"][0],
        "overview_input_sha256": FROZEN_SUPPORT["historical_current_overview"][1],
        "tested_family_count": 3, "evidence_owners_per_tested_family": 17,
        "candidate_evidence_owner_count": 51,
        "published_v4_build_evidence_owner_count": 6,
        "total_distinct_evidence_owner_count": 57,
        "families": ["c", "rust", "zig"],
        "historical_qualified_candidate_count": 0,
        "published_v4_builds": [
            {"family": spec["family"], "build_status": spec["status"],
             "archive_path": spec["archive"],
             "archive_sha256": spec["archive_sha256"],
             "archive_bytes": spec["archive_bytes"],
             "receipt_path": spec["receipt"],
             "receipt_sha256": spec["receipt_sha256"],
             "receipt_bytes": spec["receipt_bytes"],
             "process_count": spec["process_count"],
             "completed_phase_count": spec["completed_phase_count"],
             "qualified_candidate_count": 0}
            for spec in HISTORICAL_V4_RECORDS.values()
        ],
        "historical_build_process_ledger": {
            "v2_process_count": 39,
            "v3_zig_process_count": 15,
            "v4_process_count": 32,
            "v2_and_v4_process_count": 71,
            "all_historical_build_process_count": 86,
            "v4_processes_by_family": {"cpp": 10, "go": 4, "fortran": 18},
            "unique_pid_scope": "WITHIN EACH ACTUAL BUILD REPORT ONLY",
        },
        "zig_restoration_receipt_path": RESTORATION_RELATIVE,
        "zig_restoration_receipt_sha256": RESTORATION_SHA256,
    }


def expected_historical_evidence() -> dict[str, Any]:
    """Retain each real evidence owner and every independently observed process."""
    result = copy.deepcopy(_expected_legacy_historical_evidence())
    v5 = []
    for item in HISTORICAL_V5_RECORDS.values():
        v5.append({
            "family": item["family"],
            "build_status": item["build_status"],
            "archive_path": item["archive_path"],
            "archive_sha256": item["archive_sha256"],
            "archive_bytes": item["archive_bytes"],
            "receipt_path": item["receipt_path"],
            "receipt_sha256": item["receipt_sha256"],
            "receipt_bytes": item["receipt_bytes"],
            "process_count": item["process_count"],
            "completed_phase_count": item["completed_build_phase_count"],
            "qualified_candidate_count": 0,
        })
    v6 = []
    for item in HISTORICAL_V6_RECORDS.values():
        summary = {
            "family": item["family"],
            "build_status": item["status"],
            "archive_path": item["archive"],
            "archive_sha256": item["archive_sha256"],
            "archive_bytes": item["archive_bytes"],
            "receipt_path": item["receipt"],
            "receipt_sha256": item["receipt_sha256"],
            "receipt_bytes": item["receipt_bytes"],
            "process_count": item["process_count"],
            "completed_phase_count": item["completed_phase_count"],
            "qualified_candidate_count": 0,
        }
        if item["status"] == "PASS":
            summary["native_outputs"] = copy.deepcopy(item["native_outputs"])
        else:
            summary.update({
                "successful_process_count": item["successful_process_count"],
                "error": copy.deepcopy(item["error"]),
                "phase_outputs": copy.deepcopy(item["phase_outputs"]),
                "differing_raw_binary_section": (
                    item["differing_raw_binary_section"]
                ),
            })
        v6.append(summary)
    actual_v5_processes = sum(item["process_count"] for item in v5)
    actual_v6_processes = sum(item["process_count"] for item in v6)
    result.update({
        "published_v5_builds": v5,
        "published_v6_builds": v6,
        "published_v5_build_evidence_owner_count": 2 * len(v5),
        "published_v6_build_evidence_owner_count": 2 * len(v6),
        "total_distinct_evidence_owner_count": 57 + 2 * (len(v5) + len(v6)),
    })
    ledger = result["historical_build_process_ledger"]
    ledger.update({
        "v5_process_count": actual_v5_processes,
        "v5_processes_by_family": {
            item["family"]: item["process_count"] for item in v5
        },
        "v6_process_count": actual_v6_processes,
        "v6_processes_by_family": {
            item["family"]: item["process_count"] for item in v6
        },
        "v2_v4_v5_process_count": 71 + actual_v5_processes,
        "v2_v4_v5_v6_process_count": (
            71 + actual_v5_processes + actual_v6_processes
        ),
        "all_historical_build_process_count": (
            86 + actual_v5_processes + actual_v6_processes
        ),
        "all_historical_versions_actual_compiler_process_count": (
            86 + actual_v5_processes + actual_v6_processes
        ),
    })
    return result


def expected_contract() -> dict[str, Any]:
    families = []
    for family, info in FAMILIES.items():
        families.append({
            "id": family, "language": info["language"], "module": info["module"],
            "promotion_targets": {role: "candidates/" + name
                                  for role, name in info["targets"].items()},
            "generated_build_only_outputs": dict(info["generated"]),
            "owners": [{"path": path, "sha256": digest, "bytes": size}
                       for path, (digest, size) in SOURCE_OWNERS[family].items()],
        })
    return {
        "schema": CONTRACT_SCHEMA, "version": 4,
        "phase": "SOURCE FREEZE; NO NATIVE ACTIVATION AUTHORIZED",
        "oracle": {"implementation": "CPython", "version": "3.14.6",
                    "suite_count": 13, "case_execution_count": 31237,
                    "manifest_path": PHASE1_RELATIVE,
                    "manifest_sha256": PHASE1_SHA256},
        "source_build": expected_source_build(), "family_count": 6,
        "source_owner_count": 25,
        "canonical_native_target_count": 10,
        "pinned_support": [
            {
                "id": name,
                "path": relative,
                "sha256": digest,
                "bytes": size,
            }
            for name, (relative, digest, size) in FROZEN_SUPPORT.items()
        ],
        "qualified_candidate_count": 0, "families": families,
        "historical_candidate_evidence": expected_historical_evidence(),
        "recovery_policy": expected_recovery_policy(),
        "phase_boundary": expected_phase_boundary(),
    }


def validate_contract(value: Any) -> dict[str, Any]:
    require(type(value) is dict and value == expected_contract(),
            "the complete six-family, 25-owner V4 activation contract changed")
    paths = [path for graph in SOURCE_OWNERS.values() for path in graph]
    require(len(paths) == len(set(paths)) == 25,
            "all six semantic source closures must be complete and pairwise disjoint")
    targets = ["candidates/" + item
               for family in FAMILIES.values() for item in family["targets"].values()]
    require(len(targets) == len(set(targets)) == 10,
            "all ten canonical engine/bridge targets must be distinct")
    return value


def directory_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) \
        | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)


def regular_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def open_root(root: str, *, private: bool) -> int:
    require(type(root) is str and root.startswith("/")
            and root == root.rstrip("/") and "\x00" not in root,
            "open only one exact authenticated absolute root")
    descriptor = os.open(root, directory_flags())
    try:
        current, visible = os.fstat(descriptor), os.stat(root, follow_symlinks=False)
        require(stat.S_ISDIR(current.st_mode) and stat.S_ISDIR(visible.st_mode)
                and (current.st_dev, current.st_ino) == (visible.st_dev, visible.st_ino),
                "reject a redirected, symlinked, or replaced authenticated root")
        if private:
            require(stat.S_IMODE(current.st_mode) == 0o700
                    and current.st_uid == os.geteuid(),
                    "a recovery/build root must actually be owner-only mode 0700")
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def read_owned(root: str, relative: str, expected: str | None, *, maximum: int,
               exact_size: int | None = None, private: bool = False) -> tuple[bytes, dict[str, Any]]:
    checked_relative(relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES,
            "a strict typed authenticated owner size bound is mandatory")
    if expected is not None:
        checked_digest(expected, relative)
    if exact_size is not None:
        require(type(exact_size) is int and 0 < exact_size <= maximum,
                "require a bounded exact typed owner size")
    opened: list[int] = []
    try:
        parent = open_root(root, private=private)
        opened.append(parent)
        parts = relative.split("/")
        for part in parts[:-1]:
            parent = os.open(part, directory_flags(), dir_fd=parent)
            opened.append(parent)
            require(stat.S_ISDIR(os.fstat(parent).st_mode),
                    "reject a symlinked or redirected source parent")
        descriptor = os.open(parts[-1], regular_flags(), dir_fd=parent)
        opened.append(descriptor)
        first = os.fstat(descriptor)
        visible = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(first.st_mode) and stat.S_ISREG(visible.st_mode)
                and (first.st_dev, first.st_ino) == (visible.st_dev, visible.st_ino)
                and 0 < first.st_size <= maximum
                and (exact_size is None or first.st_size == exact_size),
                "reject a canonical symlink, incorrect size, stale inode, or non-file")
        digest, blocks, remaining = hashlib.sha256(), [], first.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1048576))
            require(type(block) is bytes and bool(block), "reject a truncated owner")
            remaining -= len(block)
            digest.update(block)
            blocks.append(block)
        require(os.read(descriptor, 1) == b"", "reject a hidden authenticated-file suffix")
        last, named = os.fstat(descriptor), os.stat(parts[-1], dir_fd=parent,
                                                   follow_symlinks=False)
        actual = digest.hexdigest()
        require((first.st_dev, first.st_ino, first.st_size,
                 first.st_mtime_ns, first.st_ctime_ns)
                == (last.st_dev, last.st_ino, last.st_size,
                    last.st_mtime_ns, last.st_ctime_ns)
                and (last.st_dev, last.st_ino, last.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and (expected is None or actual == expected),
                "reject a changed, replaced, redirected, or falsely hashed owner")
        raw = b"".join(blocks)
        return raw, {"relative": relative, "path": root + "/" + relative,
                     "sha256": actual, "size_bytes": len(raw),
                     "device": last.st_dev, "inode": last.st_ino,
                     "mode": stat.S_IMODE(last.st_mode)}
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_absolute_tool(path: str, digest: str, size: int) -> dict[str, Any]:
    require(type(path) is str and path.startswith("/") and "\x00" not in path,
            "require one exact absolute authenticated official tool")
    descriptor = os.open(path, regular_flags())
    try:
        first = os.fstat(descriptor)
        require(stat.S_ISREG(first.st_mode) and first.st_size == size,
                "the pinned official compiler is missing or changed")
        hasher, count = hashlib.sha256(), 0
        while True:
            block = os.read(descriptor, 1048576)
            if not block:
                break
            hasher.update(block)
            count += len(block)
            require(count <= MAX_BINARY_BYTES, "the pinned compiler exceeded its size bound")
        last = os.fstat(descriptor)
        require(count == size and (first.st_dev, first.st_ino, first.st_size,
                                   first.st_mtime_ns, first.st_ctime_ns)
                == (last.st_dev, last.st_ino, last.st_size,
                    last.st_mtime_ns, last.st_ctime_ns)
                and hasher.hexdigest() == checked_digest(digest, path),
                "the exact pinned official compiler bytes changed")
        return {"path": path, "sha256": digest, "size_bytes": size,
                "device": last.st_dev, "inode": last.st_ino,
                "mode": stat.S_IMODE(last.st_mode),
                "version_command_run": False, "path_lookup_used": False}
    finally:
        os.close(descriptor)


def validate_phase1(raw: bytes) -> dict[str, Any]:
    document = decode_document(raw, "complete frozen P0 manifest")
    suites, gate = document.get("suites"), document.get("phase_gate")
    guards = document.get("audit_boundaries")
    require(document.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and document.get("version") == 1 and type(suites) is list
            and len(suites) == 13
            and sum(item.get("case_execution_count", 0) for item in suites) == 31237
            and all(item.get("baseline", {}).get("status") == "PASS" for item in suites),
            "all 13 real baseline suites and 31,237 exact case executions are mandatory")
    require(type(gate) is dict and gate.get("status") == "PASS"
            and gate.get("all_obligations_mapped") is True
            and gate.get("blockers") == []
            and gate.get("candidate_evaluation_authorized") is False
            and gate.get("final_holdout_authorized") is False,
            "the complete reference gate may not authorize candidate or holdout access")
    require(type(guards) is dict and guards.get("hidden_cases_read") == 0
            and guards.get("final_cases_read") == 0
            and guards.get("timing_trials_run") == 0
            and guards.get("candidate_qualified") is False,
            "reject a holdout, candidate, timing, or changed oracle boundary")
    return {"status": "PASS", "suite_count": 13,
            "case_execution_count": 31237, "qualified_candidate_count": 0,
            "holdout": "NOT OPENED", "performance": "NOT MEASURED"}


def parse_owner_pins(family: str, values: Any) -> dict[str, str]:
    family = checked_family(family)
    expected = SOURCE_OWNERS[family]
    require(type(values) is list and len(values) == len(expected),
            "pin every exact independently owned family source")
    actual: dict[str, str] = {}
    for item in values:
        require(type(item) is str and item.count("=") == 1,
                "an owned source must be exactly RELATIVE/PATH=SHA256")
        relative, digest = item.split("=", 1)
        checked_relative(relative)
        require(relative in expected and relative not in actual
                and checked_digest(digest, relative) == expected[relative][0],
                "reject a missing, duplicate, foreign, modified, or cross-family source")
        actual[relative] = digest
    require(set(actual) == set(expected), "the entire exact semantic source closure is mandatory")
    return dict(sorted(actual.items()))


def expected_roles(family: str) -> dict[str, str]:
    info = FAMILIES[checked_family(family)]
    return {**info["targets"], **info["generated"]}


def parse_native_pins(family: str, values: Any, *, sizes: bool) -> dict[str, Any]:
    roles = expected_roles(family)
    require(type(values) is list and len(values) == len(roles),
            "pin every built native role and the exact Go-generated header")
    found: dict[str, Any] = {}
    for item in values:
        require(type(item) is str and item.count("=") == 1,
                "native pins must be exactly ROLE=SHA256 or ROLE=POSITIVE-BYTES")
        role, value = item.split("=", 1)
        require(role in roles and role not in found, "reject a missing or foreign native role")
        if sizes:
            require(value.isascii() and value.isdecimal() and value == str(int(value)),
                    "require a canonical positive native byte count")
            found[role] = checked_positive_size(int(value), role)
        else:
            found[role] = checked_digest(value, role)
    require(set(found) == set(roles), "pin each family artifact exactly once")
    return dict(sorted(found.items()))


def checked_symbol_name(value: Any) -> tuple[str, str | None, bool]:
    require(type(value) is str and 0 < len(value) <= 1024,
            "require the complete actual GNU dynamic-symbol name")
    fields = value.split("@")
    require(1 <= len(fields) <= 3, "reject a malformed GNU version decoration")
    name = fields[0]
    require(bool(name) and name[0] in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$"
            and all(char.isascii() and (char.isalnum() or char in "_.$") for char in name),
            "reject a missing, disguised, or shifted native symbol")
    version, default = None, False
    if len(fields) == 2:
        version = fields[1]
    elif len(fields) == 3:
        require(fields[1] == "", "default GNU symbol versions require two at-signs")
        version, default = fields[2], True
    if version is not None:
        require(bool(version) and len(version) <= 256
                and all(char.isascii() and (char.isalnum() or char in "_.+-") for char in version),
                "reject a concealed or malformed GNU symbol version")
    return name, version, default


def parse_dynamic(raw: Any) -> dict[str, list[str]]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES
            and raw.endswith(b"\n") and b"\x00" not in raw,
            "the complete bounded native dynamic-library stream is mandatory")
    try:
        source = raw.decode("utf-8")
    except UnicodeError as error:
        raise ActivationError("invalid native dynamic-library stream") from error
    found: dict[str, list[str]] = {"needed": [], "runpath": [], "rpath": [], "soname": []}
    markers = {"(NEEDED)": "needed", "(RUNPATH)": "runpath",
               "(RPATH)": "rpath", "(SONAME)": "soname"}
    for line in source.splitlines():
        for marker, key in markers.items():
            if marker in line:
                start, finish = line.find("["), line.find("]", line.find("[") + 1)
                require(start >= 0 and finish > start + 1,
                        "a dynamic dependency lacks its exact bracketed value")
                value = line[start + 1:finish]
                require("\x00" not in value, "reject a malformed dynamic dependency")
                found[key].append(value)
    for key, records in found.items():
        require(len(records) == len(set(records)),
                "reject duplicate dynamic-library evidence: " + key)
    return found


def parse_symbols(raw: Any) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES
            and raw.endswith(b"\n") and b"\x00" not in raw,
            "preserve the complete actual GNU dynamic-symbol stream")
    try:
        source = raw.decode("utf-8")
    except UnicodeError as error:
        raise ActivationError("native ELF symbols must be UTF-8") from error
    prefix, suffix = "Symbol table '.dynsym' contains ", " entries:"
    count: int | None = None
    records: dict[int, dict[str, Any]] = {}
    types = {"NOTYPE", "OBJECT", "FUNC", "SECTION", "FILE", "COMMON", "TLS", "GNU_IFUNC", "IFUNC"}
    bindings = {"LOCAL", "GLOBAL", "WEAK", "UNIQUE", "GNU_UNIQUE"}
    visibility = {"DEFAULT", "INTERNAL", "HIDDEN", "PROTECTED"}
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(prefix):
            require(count is None and stripped.endswith(suffix),
                    "reject duplicate GNU dynamic-symbol headers")
            encoded = stripped[len(prefix):-len(suffix)]
            require(encoded.isascii() and encoded.isdecimal()
                    and 1 <= int(encoded) <= 131072,
                    "reject a false bounded GNU symbol count")
            count = int(encoded)
            continue
        if stripped.startswith("Num:"):
            require(count is not None, "an ELF symbol header precedes its table")
            continue
        columns = stripped.split()
        require(bool(columns) and columns[0].endswith(":")
                and columns[0][:-1].isascii() and columns[0][:-1].isdecimal()
                and count is not None and 7 <= len(columns) <= 9,
                "reject shifted, appended, or unrecognized GNU symbol evidence")
        index = int(columns[0][:-1])
        require(0 <= index < count and index not in records,
                "reject a missing, reused, or out-of-range GNU symbol index")
        address, size, kind, binding, visible, section = columns[1:7]
        require(address.isascii() and 1 <= len(address) <= 32
                and all(ch in "0123456789abcdefABCDEF" for ch in address)
                and size.isascii() and size.isdecimal() and int(size) <= MAX_BINARY_BYTES
                and kind in types and binding in bindings and visible in visibility
                and (section in {"UND", "ABS", "COM"}
                     or (section.isascii() and section.isdecimal())),
                "reject malformed or misaligned GNU dynamic-symbol fields")
        if len(columns) == 7:
            require(index == 0 and binding == "LOCAL" and section == "UND",
                    "only the actual null GNU symbol may omit its name")
            records[index] = {"index": index, "type": kind, "binding": binding,
                              "visibility": visible, "section": section,
                              "name": None, "raw_name": None,
                              "version": None, "default_version": False,
                              "version_index": None}
            continue
        name, version, default = checked_symbol_name(columns[7])
        version_index = None
        if len(columns) == 9:
            decoration = columns[8]
            require(version is not None and decoration.startswith("(")
                    and decoration.endswith(")") and decoration[1:-1].isascii()
                    and decoration[1:-1].isdecimal() and int(decoration[1:-1]) > 0,
                    "never parse a GNU version index as a symbol")
            version_index = int(decoration[1:-1])
        require(name not in FORBIDDEN_NATIVE_NAMES
                and not any(name.startswith(prefix) for prefix in FORBIDDEN_PREFIXES),
                "a native binary delegates to an outside matching engine: " + name)
        records[index] = {"index": index, "type": kind, "binding": binding,
                          "visibility": visible, "section": section,
                          "name": name, "raw_name": columns[7],
                          "version": version, "default_version": default,
                          "version_index": version_index}
    require(count is not None and set(records) == set(range(count)),
            "the complete authentic GNU dynamic-symbol table is mandatory")
    ordered = [records[index] for index in range(count)]
    exports = {row["name"] for row in ordered
               if row["name"] is not None and row["section"] != "UND"
               and row["binding"] in {"GLOBAL", "WEAK", "UNIQUE", "GNU_UNIQUE"}}
    undefined = {row["name"] for row in ordered
                 if row["name"] is not None and row["section"] == "UND"}
    require(bool(exports), "a genuine built artifact exposes no owned native entry point")
    return {"exports": sorted(exports), "undefined": sorted(undefined),
            "symbol_count": count,
            "versioned_symbol_count": sum(row["version"] is not None for row in ordered),
            "symbol_records": ordered}


def matching_symbol_owner(symbol: str) -> str | None:
    if symbol.startswith("rebar_zig_"):
        return "zig"
    if symbol.startswith("rebar_go_"):
        return "go"
    if symbol.startswith("rebar_fortran_"):
        return "fortran"
    if "rebar_cpp" in symbol:
        return "cpp"
    if symbol.startswith("rebar_"):
        return "rust"
    if symbol == "PyInit__vm_native":
        return "c"
    for family in ("rust", "zig", "cpp", "go", "fortran"):
        if symbol == "PyInit__" + family + "_bridge":
            return family
    return None


def validate_elf(family: str, role: str, dynamic: dict[str, Any],
                 symbols: dict[str, Any]) -> dict[str, Any]:
    family = checked_family(family)
    require(role in FAMILIES[family]["targets"], "reject a foreign native artifact role")
    needed = set(dynamic.get("needed", ()))
    exports, undefined = set(symbols.get("exports", ())), set(symbols.get("undefined", ()))
    require(not dynamic.get("rpath"), "reject an unsafe ELF RPATH")
    for symbol in exports | undefined:
        owner = matching_symbol_owner(symbol)
        require(owner is None or owner == family,
                "reject a cross-family semantic parser, compiler, or executor")
    system = FAMILY_LIBRARIES[family]
    required: set[str] | frozenset[str]
    if family == "c":
        require(role == "extension" and "PyInit__vm_native" in exports
                and needed.issubset(system) and not dynamic.get("runpath"),
                "require the standalone owned C extension and exact system dependencies")
        required = {"PyInit__vm_native"}
    elif family == "cpp":
        require(role == "bridge" and "PyInit__cpp_bridge" in exports
                and any("rebar_cpp" in item for item in exports | undefined)
                and needed.issubset(system) and not dynamic.get("runpath"),
                "require the C++ bridge's independently compiled first-party C++ engine")
        required = {"PyInit__cpp_bridge"}
    elif role == "engine":
        required = {"rust": RUST_EXPORTS, "zig": ZIG_EXPORTS,
                    "go": GO_EXPORTS, "fortran": FORTRAN_EXPORTS}[family]
        require(set(required).issubset(exports) and needed.issubset(system)
                and not dynamic.get("runpath"),
                "require all exact owned matching exports and no external native engine")
        filename = FAMILIES[family]["targets"]["engine"]
        if family == "go":
            require(dynamic.get("soname") in ([], [filename]),
                    "reject a foreign Go c-shared SONAME")
        else:
            require(dynamic.get("soname") == [filename],
                    "the owned matching engine's exact SONAME changed")
        if family == "fortran":
            callbacks = {name for name in undefined if name.startswith("rebar_fortran_")}
            require(callbacks == FORTRAN_CALLBACKS,
                    "the Fortran engine must use exactly its own three bridge callbacks")
    else:
        engine = FAMILIES[family]["targets"]["engine"]
        entry = "PyInit__" + family + "_bridge"
        prefix = {"rust": "rebar_", "zig": "rebar_zig_",
                  "go": "rebar_go_", "fortran": "rebar_fortran_"}[family]
        require(entry in exports and engine in needed
                and needed.issubset(system | {engine})
                and dynamic.get("runpath") == ["$ORIGIN"]
                and any(name.startswith(prefix) for name in undefined),
                "require an adjacent owned engine, exact entry point, and $ORIGIN")
        if family == "go":
            require(GO_EXPORTS.issubset(undefined),
                    "the Go bridge must use all nine compiler-generated engine declarations")
        if family == "fortran":
            require(FORTRAN_EXPORTS.issubset(undefined)
                    and FORTRAN_CALLBACKS.issubset(exports),
                    "require all nine Fortran functions and all three reverse callbacks")
        required = {entry}
    return {"role": role, "needed": sorted(needed),
            "runpath": list(dynamic.get("runpath", [])),
            "soname": list(dynamic.get("soname", [])),
            "required_exports": sorted(required),
            "exports": sorted(exports), "undefined": sorted(undefined),
            "symbol_count": symbols["symbol_count"],
            "versioned_symbol_count": symbols["versioned_symbol_count"],
            "symbol_records": list(symbols["symbol_records"]),
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0}


def audit_go_header(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES
            and b"Code generated by cmd/cgo; DO NOT EDIT." in raw,
            "require the genuine fresh per-phase Go compiler-generated C header")
    try:
        source = raw.decode("utf-8")
        document = ast.parse("pass", mode="exec")
        require(isinstance(document, ast.Module), "validate the standard parser")
    except (UnicodeError, SyntaxError) as error:
        raise ActivationError("the generated Go ABI header is malformed") from error
    for symbol in GO_EXPORTS:
        require(symbol in source, "a generated Go ABI declaration is missing: " + symbol)
    require(not any(marker in source for marker in
                    ("pcre2_match", "onig_search", "regexec", "PyInit__sre")),
            "reject a Go header supplied by an external regular-expression engine")
    return {"generated_by": "cmd/cgo", "required_exports": sorted(GO_EXPORTS),
            "required_export_count": 9, "externally_supplied": False,
            "forced_bridge_include": True}


def phase_paths(build_root: str, family: str, phase: str) -> dict[str, str]:
    root = checked_private_root(build_root, family, build=True)
    require(phase in ("reference-a", "reference-b"),
            "require exactly two independently owned V4 build phases")
    base = root + "/" + phase
    source, native = base + "/source", base + "/native"
    paths = {"base": base, "source": source, "native": native,
             "temporary": base + "/temporary", "target": base + "/target",
             "cargo_home": base + "/cargo-home",
             "zig_local_cache": base + "/zig-local-cache",
             "zig_global_cache": base + "/zig-global-cache",
             "go_build_cache": base + "/go-build-cache",
             "go_module_cache": base + "/go-module-cache",
             "fortran_modules": base + "/fortran-modules",
             "rust_manifest": source + "/candidates/rust/Cargo.toml",
             "rust_target_engine": base + "/target/release/librebar_rust_continuation.so",
             "go_module_directory": source + "/candidates/go"}
    for role, filename in expected_roles(family).items():
        paths["artifact_" + role] = native + "/" + filename
    return paths


def sanitized(value: str, build_root: str) -> str:
    return value.replace(build_root, SANITIZED_BUILD_ROOT)


def prefix_flags(build_root: str, family: str) -> tuple[list[str], str]:
    gcc, rust = [], []
    for phase in ("reference-a", "reference-b"):
        source = phase_paths(build_root, family, phase)["source"]
        gcc.append("-ffile-prefix-map=" + source + "=/rebar-phase2-v4-owned-source")
        rust.append("--remap-path-prefix=" + source + "=/rebar-phase2-v4-owned-source")
    if family == "rust":
        rust.append("-Clink-arg=-Wl,-soname,_rust_engine.so")
    return gcc, " ".join(rust)


def expected_environment(build_root: str, family: str, phase: str) -> dict[str, str]:
    paths = phase_paths(build_root, family, phase)
    _, rustflags = prefix_flags(build_root, family)
    env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
           "SOURCE_DATE_EPOCH": "1", "TMPDIR": paths["temporary"]}
    if family == "rust":
        env.update({"PATH": RUST_TOOLCHAIN + "/bin:/usr/bin:/bin",
                    "CARGO_HOME": paths["cargo_home"], "CARGO_NET_OFFLINE": "true",
                    "CARGO_INCREMENTAL": "0", "CARGO_BUILD_JOBS": "1",
                    "RUSTC": PINNED_RUSTC, "RUSTFLAGS": rustflags})
    elif family == "zig":
        env.update({"ZIG_LOCAL_CACHE_DIR": paths["zig_local_cache"],
                    "ZIG_GLOBAL_CACHE_DIR": paths["zig_global_cache"]})
    elif family == "go":
        env.update({"GOPROXY": "off", "GOSUMDB": "off", "GOWORK": "off",
                    "GOENV": "off", "GOTOOLCHAIN": "local", "CGO_ENABLED": "1",
                    "CC": PINNED_GCC, "GOCACHE": paths["go_build_cache"],
                    "GOMODCACHE": paths["go_module_cache"], "GOFLAGS": "-mod=readonly"})
    return {key: sanitized(value, build_root) for key, value in sorted(env.items())}


def planned_commands(build_root: str, family: str, phase: str) -> dict[str, list[str]]:
    family = checked_family(family)
    paths = phase_paths(build_root, family, phase)
    flags, _ = prefix_flags(build_root, family)
    commands: dict[str, list[str]] = {"readelf_version": [PINNED_READELF, "--version"]}
    if family in {"c", "rust", "zig", "go", "fortran"}:
        commands["gcc_version"] = [PINNED_GCC, "--version"]
    if family == "c":
        commands["build_c_extension"] = [PINNED_GCC, "-std=c11", "-O3", "-Wall", "-Wextra", "-Werror", "-fPIC", "-shared", "-Wl,--build-id=sha1", *flags, "-I" + PYTHON_INCLUDE, paths["source"] + "/candidates/_vm_native.c", "-o", paths["artifact_extension"]]
    elif family == "rust":
        commands["rustc_version"] = [PINNED_RUSTC, "--version", "--verbose"]
        commands["cargo_version"] = [PINNED_CARGO, "--version"]
        commands["build_rust_engine"] = [PINNED_CARGO, "build", "--manifest-path", paths["rust_manifest"], "--release", "--locked", "--offline", "--frozen", "--target-dir", paths["target"]]
        commands["build_rust_bridge"] = [PINNED_GCC, "-pthread", "-std=c11", "-shared", "-fPIC", "-O3", "-Wall", "-Wextra", "-Werror", "-Wl,-z,noexecstack", "-Wl,--exclude-libs,ALL", "-Wl,--build-id=sha1", *flags, "-I" + PYTHON_INCLUDE, paths["source"] + "/candidates/rust/py_bridge.c", "-L" + paths["native"], "-l:_rust_engine.so", "-Wl,-rpath,$ORIGIN", "-o", paths["artifact_bridge"]]
    elif family == "zig":
        commands["zig_version"] = [PINNED_ZIG, "version"]
        commands["build_zig_engine"] = [PINNED_ZIG, "build-lib", paths["source"] + "/candidates/zig/mini_regex.zig", "-dynamic", "-lc", "-O", "ReleaseFast", "-fstrip", "-fallow-shlib-undefined", "-fsoname=_zig_probe.so", "--cache-dir", paths["zig_local_cache"], "--global-cache-dir", paths["zig_global_cache"], "-femit-bin=" + paths["artifact_engine"]]
        commands["build_zig_bridge"] = [PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3", "-Wall", "-Wextra", "-Werror", "-Wl,--build-id=sha1", *flags, "-I" + PYTHON_INCLUDE, paths["source"] + "/candidates/zig/py_bridge.c", "-L" + paths["native"], "-l:_zig_probe.so", "-Wl,-rpath,$ORIGIN", "-o", paths["artifact_bridge"]]
    elif family == "cpp":
        commands["gxx_version"] = [PINNED_GXX, "--version"]
        commands["build_cpp_bridge"] = [PINNED_GXX, "-std=c++20", "-O3", "-Wall", "-Wextra", "-Werror", "-fPIC", "-shared", "-Wl,--build-id=sha1", *flags, "-I" + PYTHON_INCLUDE, "-I" + paths["source"] + "/candidates/cpp", paths["source"] + "/candidates/cpp/engine.cpp", paths["source"] + "/candidates/cpp/py_bridge.cpp", "-o", paths["artifact_bridge"]]
    elif family == "go":
        commands["go_version"] = [PINNED_GO, "version"]
        commands["build_go_engine"] = [PINNED_GO, "build", "-buildmode=c-shared", "-trimpath", "-buildvcs=false", "-ldflags=-buildid=", "-o", paths["artifact_engine"], "."]
        commands["build_go_bridge"] = [PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3", "-Wall", "-Wextra", "-Werror", "-Wl,--build-id=sha1", *flags, "-I" + PYTHON_INCLUDE, "-I" + paths["native"], "-include", paths["artifact_generated_header"], paths["source"] + "/candidates/go/py_bridge.c", "-L" + paths["native"], "-l:_go_engine.so", "-Wl,-rpath,$ORIGIN", "-o", paths["artifact_bridge"]]
    else:
        commands["gfortran_version"] = [PINNED_GFORTRAN, "--version"]
        commands["build_fortran_engine"] = [PINNED_GFORTRAN, "-shared", "-fPIC", "-O3", "-ffree-line-length-none", "-Wl,--build-id=sha1", "-Wl,-soname,_fortran_engine.so", *flags, "-J" + paths["fortran_modules"], paths["source"] + "/candidates/fortran/engine.f90", "-o", paths["artifact_engine"]]
        commands["build_fortran_bridge"] = [PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3", "-Wall", "-Wextra", "-Werror", "-Wl,--build-id=sha1", *flags, "-I" + PYTHON_INCLUDE, paths["source"] + "/candidates/fortran/py_bridge.c", "-L" + paths["native"], "-l:_fortran_engine.so", "-Wl,-rpath,$ORIGIN", "-o", paths["artifact_bridge"]]
    for role in FAMILIES[family]["targets"]:
        commands[role + "_dynamic"] = [PINNED_READELF, "--dynamic", "--wide", paths["artifact_" + role]]
        commands[role + "_symbols"] = [PINNED_READELF, "--dyn-syms", "--wide", paths["artifact_" + role]]
    return {key: [sanitized(value, build_root) for value in argv]
            for key, argv in commands.items()}


def process_schedule(family: str) -> list[str]:
    family = checked_family(family)
    versions = ["readelf_version"]
    if family != "cpp":
        versions.append("gcc_version")
    if family == "rust":
        versions.extend(("rustc_version", "cargo_version"))
    elif family == "zig":
        versions.append("zig_version")
    elif family == "cpp":
        versions.append("gxx_version")
    elif family == "go":
        versions.append("go_version")
    elif family == "fortran":
        versions.append("gfortran_version")
    build = {
        "c": ["build_c_extension"],
        "rust": ["build_rust_engine", "build_rust_bridge"],
        "zig": ["build_zig_engine", "build_zig_bridge"],
        "cpp": ["build_cpp_bridge"],
        "go": ["build_go_engine", "build_go_bridge"],
        "fortran": ["build_fortran_engine", "build_fortran_bridge"],
    }[family]
    inspections = [part for role in FAMILIES[family]["targets"]
                   for part in (role + "_dynamic", role + "_symbols")]
    return versions + build + inspections


def decode_process_output(record: dict[str, Any], channel: str) -> bytes:
    value = record.get(channel + "_base64")
    require(type(value) is str, "preserve complete authenticated compiler " + channel)
    try:
        raw = base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeError, ValueError) as error:
        raise ActivationError("a compiler " + channel + " stream was forged") from error
    require(len(raw) <= MAX_PROCESS_BYTES
            and type(record.get(channel + "_bytes")) is int
            and len(raw) == record[channel + "_bytes"]
            and sha256(raw) == record.get(channel + "_sha256"),
            "reject truncated or tampered compiler " + channel)
    return raw


def validate_processes(family: str, build_root: str,
                       processes: Any) -> dict[tuple[str, str], bytes]:
    family = checked_family(family)
    schedule = process_schedule(family)
    require(type(processes) is list and len(processes) == 2 * len(schedule),
            "require every actual compiler and ELF inspector in both V4 source phases")
    streams: dict[tuple[str, str], bytes] = {}
    pids: set[int] = set()
    for phase_index, phase in enumerate(("reference-a", "reference-b")):
        commands = planned_commands(build_root, family, phase)
        environment = expected_environment(build_root, family, phase)
        paths = phase_paths(build_root, family, phase)
        for step_index, name in enumerate(schedule):
            process = processes[phase_index * len(schedule) + step_index]
            require(type(process) is dict and process.get("name") == name
                    and type(process.get("pid")) is int
                    and process["pid"] > 0 and process["pid"] not in pids
                    and type(process.get("exit_status")) is int
                    and process["exit_status"] == 0
                    and process.get("shell") is False,
                    "reject fabricated, reused, failed, hidden, or shell-based build processes")
            pids.add(process["pid"])
            require(process.get("argv") == commands[name]
                    and process.get("environment") == environment,
                    "reject changed exact V4 compiler, offline environment, cache, or ABI")
            cwd = (paths["go_module_directory"]
                   if family == "go" and name == "build_go_engine" else paths["base"])
            require(process.get("working_directory") == sanitized(cwd, build_root),
                    "the actual compiler working directory was substituted")
            stdout = decode_process_output(process, "stdout")
            decode_process_output(process, "stderr")
            if name == "zig_version":
                require(stdout == b"0.16.0\n", "reject a substituted official Zig compiler")
            elif name == "go_version":
                require(stdout == b"go version go1.26.3 linux/amd64\n",
                        "reject a substituted Go compiler")
            elif name == "cargo_version":
                require(stdout.startswith(b"cargo 1.95.0 (f2d3ce0bd"),
                        "reject a substituted Cargo toolchain")
            elif name == "rustc_version":
                require(stdout.startswith(b"rustc 1.95.0 (59807616e")
                        and b"release: 1.95.0\n" in stdout,
                        "reject a substituted Rust compiler driver")
            elif name in {"gcc_version", "gxx_version", "gfortran_version"}:
                require(b"13." in stdout.split(b"\n", 1)[0],
                        "reject a substituted GNU language compiler")
            elif name == "readelf_version":
                require(b"readelf" in stdout.split(b"\n", 1)[0].lower(),
                        "reject a substituted GNU ELF inspector")
            elif name.endswith(("_dynamic", "_symbols")):
                require(bool(stdout), "retain the complete actual ELF inspection stream")
            streams[(phase, name)] = stdout
    return streams


def same_owner(actual: Any, expected: Any) -> bool:
    return (type(actual) is dict and type(expected) is dict
            and all(type(actual.get(key)) is type(expected.get(key))
                    and actual.get(key) == expected.get(key)
                    for key in OWNER_FIELDS))


def require_durable_owner(actual: Any, *, relative: str,
                          root: str, directory_sync: bool) -> dict[str, Any]:
    require(type(actual) is dict
            and actual.get("relative") == checked_relative(relative)
            and actual.get("path") == root + "/" + relative,
            "require one exact owner-only durable record")
    checked_digest(actual.get("sha256"), relative)
    checked_positive_size(actual.get("size_bytes"), relative)
    for key in ("device", "inode", "mode"):
        require(type(actual.get(key)) is int and actual[key] >= 0,
                "reject forged or Boolean recovery inode identity")
    require(actual["inode"] > 0 and actual["mode"] == 0o600
            and actual.get("exclusive_creation") is True
            and actual.get("same_inode_readback_verified") is True
            and actual.get("file_fsync_completed") is True
            and type(actual.get("write_calls")) is int
            and actual["write_calls"] > 0,
            "require exact genuine exclusive creation and owner-only durable fsync")
    if directory_sync:
        require(actual.get("directory_fsync_completed") is True,
                "a pre-promotion intention must include actual directory fsync")
    return actual


def validate_build_receipt(report: dict[str, Any], receipt: dict[str, Any],
                           archive: bytes, arguments: dict[str, Any]) -> None:
    family, label = checked_family(arguments["family"]), checked_label(arguments["build_label"])
    require(report.get("schema") == BUILD_SCHEMA and report.get("version") == 4
            and receipt.get("schema") == BUILD_RECEIPT_SCHEMA
            and report.get("status") == "PASS"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and report.get("family") == receipt.get("family") == family
            and report.get("label") == receipt.get("label") == label,
            "a durable failed-build receipt never turns a V4 build into a pass")
    for key, expected in (("source_sha256", BUILD_SOURCE_SHA256),
                          ("protocol_sha256", BUILD_PROTOCOL_SHA256),
                          ("contract_sha256", BUILD_CONTRACT_SHA256)):
        require(report.get(key) == receipt.get(key) == expected
                and arguments["build_" + key] == expected,
                "reject a mixed V4 recorder, protocol, or machine source contract")
    archive_relative = (EVIDENCE_RELATIVE + "/native-source-build-v4-"
                        + family + "-" + label + ".json.gz")
    require(sha256(archive) == arguments["build_report_sha256"]
            and sha256(canonical(receipt)) == arguments["build_receipt_sha256"]
            and receipt.get("archive_relative") == archive_relative
            and receipt.get("archive_sha256") == sha256(archive)
            and type(receipt.get("archive_bytes")) is int
            and receipt["archive_bytes"] == len(archive)
            and receipt.get("uncompressed_sha256") == sha256(canonical(report))
            and type(receipt.get("uncompressed_bytes")) is int
            and receipt["uncompressed_bytes"] == len(canonical(report))
            and receipt.get("phase1_manifest_sha256") == PHASE1_SHA256,
            "pin the actual passing compressed V4 report and independent receipt")
    publication = receipt.get("archive_publication")
    require(type(publication) is dict and publication.get("path") == ROOT + "/" + archive_relative
            and publication.get("sha256") == sha256(archive)
            and publication.get("bytes") == len(archive)
            and publication.get("exclusive_creation") is True
            and publication.get("same_inode_readback_verified") is True
            and publication.get("file_fsync_completed") is True
            and type(publication.get("write_calls")) is int
            and publication["write_calls"] > 0,
            "require independently durable exclusive V4 source-build publication")
    sync = receipt.get("archive_directory_fsync")
    require(type(sync) is dict and sync.get("completed") is True
            and type(sync.get("device")) is int and type(sync.get("inode")) is int
            and sync["inode"] > 0,
            "require a real independently synchronized V4 archive directory")
    require(receipt.get("receipt_self_publication") == "NOT CLAIMED",
            "a receipt cannot claim its own future publication")
    for document in (report, receipt):
        for key in ("candidate_processes_started", "candidate_imports",
                    "native_libraries_loaded", "hidden_cases_read",
                    "benchmark_files_read", "clock_samples", "timing_trials_run"):
            require(type(document.get(key)) is int and document[key] == 0,
                    "a source-build proof may not contain candidate or holdout effects")
        require(document.get("candidate_correctness") == "NOT MEASURED"
                and document.get("performance") == "NOT MEASURED"
                and document.get("winner_selected") is False,
                "reject invented source-build correctness, timing, or winner evidence")


def validate_build_history(report: dict[str, Any]) -> None:
    history = report.get("preserved_v2_history")
    require(type(history) is list and len(history) == 3,
            "a V4 build must preserve the authentic three original V2 outcomes")
    wanted = {"c": ("PASS", 8), "rust": ("PASS", 16), "zig": ("FAIL", 15)}
    require({item.get("family") for item in history if type(item) is dict} == set(wanted),
            "retain C, Rust, and the real failed Zig history")
    for item in history:
        status, count = wanted[item["family"]]
        key = {"c": "v2_c", "rust": "v2_rust", "zig": "v2_zig_failure"}[item["family"]]
        original = HISTORICAL_RECORDS[key]
        require(item.get("build_status") == status
                and type(item.get("process_count")) is int and item["process_count"] == count
                and item.get("archive_sha256") == original["archive_sha256"]
                and item.get("receipt_sha256") == original["receipt_sha256"]
                and item.get("historical_v1_symbol_audit") == "FALSIFIED AND PRESERVED"
                and item.get("failure_preserved") is (status == "FAIL"),
                "never relabel authentic historical failures or falsified GNU parsing")


def validate_build_report(report: dict[str, Any], receipt: dict[str, Any],
                          archive: bytes, arguments: dict[str, Any],
                          pins: dict[str, str]) -> dict[str, dict[str, Any]]:
    family = checked_family(arguments["family"])
    root = checked_private_root(arguments["build_root"], family, build=True)
    validate_build_receipt(report, receipt, archive, arguments)
    validate_build_history(report)
    require(report.get("fresh_private_root") == SANITIZED_BUILD_ROOT
            and report.get("owned_source_sha256") == pins
            and receipt.get("owned_source_sha256") == pins,
            "require the exact frozen V4 private root and complete semantic source closure")
    oracle = report.get("frozen_correctness")
    require(type(oracle) is dict and oracle.get("status") == "PASS"
            and oracle.get("suite_count") == 13
            and oracle.get("case_execution_count") == 31237
            and oracle.get("candidate_qualified_count") == 0,
            "the source-build report must bind the unchanged complete reference oracle")
    before, after = report.get("owned_source_before"), report.get("owned_source_after")
    require(type(before) is dict and type(after) is dict
            and set(before) == set(after) == set(SOURCE_OWNERS[family]),
            "require complete before-and-after exact no-follow semantic owners")
    for relative, expected in SOURCE_OWNERS[family].items():
        for owner in (before[relative], after[relative]):
            require(type(owner) is dict and owner.get("path") == ROOT + "/" + relative
                    and owner.get("sha256") == expected[0]
                    and type(owner.get("size_bytes")) is int
                    and owner["size_bytes"] == expected[1]
                    and type(owner.get("device")) is int
                    and type(owner.get("inode")) is int and owner["inode"] > 0,
                    "the V4 build omitted or changed a frozen owned semantic source")
        require(before[relative]["device"] == after[relative]["device"]
                and before[relative]["inode"] == after[relative]["inode"],
                "the genuine semantic source owner changed during V4 builds")
    streams = validate_processes(family, root, report.get("processes"))
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == 2
            and [item.get("name") for item in phases] == ["reference-a", "reference-b"],
            "require two complete genuinely independent V4 source phases")
    verified: dict[str, dict[str, Any]] = {}
    for phase in phases:
        name = phase["name"]
        prefix = SANITIZED_BUILD_ROOT + "/" + name
        require(phase.get("fresh_source_directory") == prefix + "/source"
                and phase.get("fresh_native_directory") == prefix + "/native"
                and phase.get("fresh_temporary_directory") == prefix + "/temporary",
                "reject shared, stale, redirected, or mislabeled phase directories")
        copies = phase.get("fresh_source_owners")
        require(type(copies) is dict and set(copies) == set(pins),
                "both genuine V4 phases must copy the whole exact source graph")
        for relative, owner in copies.items():
            require(type(owner) is dict and owner.get("sha256") == pins[relative]
                    and owner.get("bytes") == SOURCE_OWNERS[family][relative][1]
                    and owner.get("path") == prefix + "/source/" + relative
                    and type(owner.get("device")) is int
                    and type(owner.get("inode")) is int and owner["inode"] > 0
                    and owner.get("exclusive_creation") is True,
                    "reject an omitted, externally copied, or reused phase semantic owner")
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict and set(outputs) == set(expected_roles(family)),
                "require every built engine, bridge, and fresh Go-generated header")
        for role, filename in expected_roles(family).items():
            item = outputs[role]
            require(type(item) is dict and item.get("family") == family
                    and item.get("role") == role and item.get("file_name") == filename
                    and item.get("path") == prefix + "/native/" + filename
                    and item.get("sha256") == arguments["native_hashes"][role]
                    and type(item.get("size_bytes")) is int
                    and item["size_bytes"] == arguments["native_sizes"][role]
                    and type(item.get("device")) is int
                    and type(item.get("inode")) is int and item["inode"] > 0
                    and item.get("prebuilt_artifact_read") is False
                    and item.get("candidate_imported") is False,
                    "require every exact two-phase source-built role and fresh inode")
            if role == "generated_header":
                audit = item.get("audit")
                require(type(audit) is dict and audit.get("generated_by") == "cmd/cgo"
                        and audit.get("required_exports") == sorted(GO_EXPORTS)
                        and audit.get("required_export_count") == 9
                        and audit.get("externally_supplied") is False
                        and audit.get("forced_bridge_include") is True,
                        "the generated Go header was absent, external, or not compiler-forced")
            else:
                dynamic = parse_dynamic(streams[(name, role + "_dynamic")])
                symbols = parse_symbols(streams[(name, role + "_symbols")])
                actual = validate_elf(family, role, dynamic, symbols)
                require(item.get("audit") == actual,
                        "an actual full, versioned owned ELF stream was omitted or substituted")
            if name == "reference-a":
                verified[role] = item
            else:
                first = verified[role]
                require(first["sha256"] == item["sha256"]
                        and first["size_bytes"] == item["size_bytes"]
                        and first["path"] != item["path"]
                        and (first["device"], first["inode"])
                        != (item["device"], item["inode"])
                        and first["audit"] == item["audit"],
                        "the two native build outputs are not genuinely independently reproducible")
    reproduction = report.get("reproducibility")
    require(type(reproduction) is dict
            and reproduction.get("independent_fresh_phase_count") == 2
            and reproduction.get("byte_identical") is True
            and reproduction.get("unique_process_count") == 2 * len(process_schedule(family))
            and reproduction.get("prebuilt_artifact_count") == 0
            and reproduction.get("native_libraries_loaded") == 0,
            "a genuine complete independently reproducible V4 build is mandatory")
    summary = reproduction.get("native_outputs")
    require(type(summary) is dict and set(summary) == set(verified),
            "every two-phase native output must occur in the V4 reproducibility record")
    for role, expected in verified.items():
        item = summary[role]
        require(type(item) is dict and item.get("file_name") == expected["file_name"]
                and item.get("sha256") == expected["sha256"]
                and item.get("size_bytes") == expected["size_bytes"]
                and item.get("fresh_independent_inode_count") == 2
                and item.get("reproduced_in_two_fresh_directories") is True
                and item.get("audit") == expected["audit"],
                "reject omitted or nonreproducible engine, bridge, or Go header")
    return verified



def load_frozen_v6_build_kernel() -> types.ModuleType:
    """Load only the exact published first-party recorder as inert Python source."""
    raw, owner = read_owned(
        ROOT, BUILD_V6_SOURCE_RELATIVE, BUILD_V6_SOURCE_SHA256,
        maximum=MAX_SOURCE_BYTES, exact_size=196660,
    )
    require(owner["sha256"] == BUILD_V6_SOURCE_SHA256
            and owner["size_bytes"] == 196660,
            "authenticate the entire immutable V6 source-build recorder first")
    module = types.ModuleType("_rebar_phase2_exact_frozen_v6_source_kernel")
    module.__dict__["__file__"] = ROOT + "/" + BUILD_V6_SOURCE_RELATIVE
    module.__dict__["__package__"] = None
    exec(compile(raw, module.__dict__["__file__"], "exec"), module.__dict__)
    require(module.SCHEMA == BUILD_V6_SCHEMA
            and module.RECEIPT_SCHEMA == BUILD_V6_RECEIPT_SCHEMA
            and module.WORK_PREFIX == BUILD_V6_PREFIX
            and module.SOURCE_OWNERS == SOURCE_OWNERS
            and set(module.FAMILIES) == set(FAMILIES)
            and module.EXPECTED_SUPPORT["build_recorder_v4"]
            == (BUILD_SOURCE_RELATIVE, BUILD_SOURCE_SHA256, 136084),
            "reject substituted V6 source, semantic ownership, or V4 parser provenance")
    for family, details in FAMILIES.items():
        expected = {
            **details["targets"],
            **details["generated"],
        }
        require(module.FAMILIES[family]["artifacts"] == expected,
                "keep the exact one-engine, one-bridge, and build-only role shapes")
    return module


def call_frozen_kernel(
    module: types.ModuleType,
    operation: Any,
    *arguments: Any,
    kernel: types.ModuleType | None = None,
    **keywords: Any,
) -> Any:
    """Translate only authenticated frozen-kernel validation failures."""
    errors: tuple[type[BaseException], ...]
    errors = (module.BuildError,)
    if kernel is not None:
        errors = (module.BuildError, kernel.BuildError)
    try:
        return operation(*arguments, **keywords)
    except errors as error:
        raise ActivationError(
            "the exact independently frozen source-build proof failed: "
            + str(error)
        ) from error


def validate_v6_processes(
    module: types.ModuleType,
    kernel: types.ModuleType,
    family: str,
    root: str,
    processes: Any,
    *,
    expected_count: int,
    passing: bool,
) -> dict[tuple[str, str], tuple[bytes, bytes, int]]:
    family = checked_family(family)
    require(type(expected_count) is int and expected_count > 0
            and type(processes) is list and len(processes) == expected_count,
            "require every actually observed V6 process and its real denominator")
    phase_schedule = process_schedule(family)
    for role in FAMILIES[family]["targets"]:
        phase_schedule.extend((role + "_sections", role + "_notes"))
    whole = [
        (phase, name)
        for phase in ("reference-a", "reference-b")
        for name in phase_schedule
    ]
    require(len(whole)
            == module.EXPECTED_BUILD_POLICY[
                "v6_future_process_count_by_family"
            ][family]
            and 0 < len(processes) <= len(whole)
            and (not passing or len(processes) == len(whole)),
            "never fabricate, omit, or silently reorder V6 compiler processes")
    pids: set[int] = set()
    result: dict[tuple[str, str], tuple[bytes, bytes, int]] = {}
    for index, (record, (phase, name)) in enumerate(
        zip(processes, whole, strict=False)
    ):
        require(type(record) is dict and set(record) == V6_PROCESS_FIELDS
                and record.get("name") == name
                and type(record.get("pid")) is int and record["pid"] > 0
                and record["pid"] not in pids
                and record.get("shell") is False,
                "reject reused, shell-based, hidden, or invented V6 processes")
        pids.add(record["pid"])
        commands = call_frozen_kernel(
            module, module.planned_commands, root, family, phase,
            kernel=kernel,
        )
        require(name in commands,
                "an actual V6 process is missing its exact frozen command")
        expected_argv = [
            call_frozen_kernel(
                module, module.sanitized, value, root, family, kernel=kernel
            )
            for value in commands[name]
        ]
        environment = call_frozen_kernel(
            module, module.build_environment, root, family, phase,
            kernel=kernel,
        )
        expected_environment = {
            key: call_frozen_kernel(
                module, module.sanitized, value, root, family, kernel=kernel
            )
            for key, value in sorted(environment.items())
        }
        directory = call_frozen_kernel(
            module, module.command_working_directory,
            root, family, phase, name, kernel=kernel,
        )
        expected_directory = call_frozen_kernel(
            module, module.sanitized, str(directory), root, family,
            kernel=kernel,
        )
        require(record["argv"] == expected_argv
                and record["environment"] == expected_environment
                and record["working_directory"] == expected_directory,
                "the exact compiler, offline environment, or private phase changed")
        stdout = call_frozen_kernel(
            module, module.decode_process_stream, record, "stdout",
            kernel=kernel,
        )
        stderr = call_frozen_kernel(
            module, module.decode_process_stream, record, "stderr",
            kernel=kernel,
        )
        code = record["exit_status"]
        require(type(code) is int,
                "require the real strictly typed compiler exit status")
        require(
            code == 0
            or (not passing and index + 1 == len(processes)),
            "a failed or nonterminal compiler never becomes a passing source build",
        )
        if name.endswith("_version") and code == 0:
            call_frozen_kernel(
                module, kernel.validate_compiler_version, name, stdout,
                kernel=kernel,
            )
        if name.endswith(("_dynamic", "_symbols", "_sections")):
            require(bool(stdout),
                    "retain the complete real V6 native ELF inspector stream")
        result[(phase, name)] = (stdout, stderr, record["pid"])
    require(len(pids) == len(processes),
            "the exact V6 process identities must be independently distinct")
    return result


def validate_v6_phase(
    module: types.ModuleType,
    kernel: types.ModuleType,
    family: str,
    root: str,
    record: Any,
    phase: str,
    streams: dict[tuple[str, str], tuple[bytes, bytes, int]],
    pins: dict[str, str],
    *,
    exact_outputs: dict[str, dict[str, Any]] | None,
) -> dict[str, dict[str, Any]]:
    require(type(record) is dict and record.get("name") == phase,
            "require each independently named complete V6 source phase")
    fields = {
        "candidate_imports", "candidate_processes_started",
        "fresh_native_directory", "fresh_source_directory",
        "fresh_source_owners", "fresh_temporary_directory", "hidden_cases_read",
        "name", "native_forensics", "native_libraries_loaded",
        "native_outputs", "timing_trials_run",
    }
    if family == "go":
        fields.add("private_go_package")
    require(set(record) == fields,
            "reject omitted or foreign V6 phase and private-package fields")
    paths = call_frozen_kernel(
        module, module.phase_paths, root, family, phase, kernel=kernel,
    )
    for key, path in (
        ("fresh_source_directory", paths["source"]),
        ("fresh_native_directory", paths["native"]),
        ("fresh_temporary_directory", paths["temporary"]),
    ):
        require(record.get(key)
                == call_frozen_kernel(
                    module, module.sanitized, str(path), root, family,
                    kernel=kernel,
                ),
                "reject a shared, redirected, or stale V6 phase directory")
    for key in (
        "candidate_imports", "candidate_processes_started",
        "hidden_cases_read", "native_libraries_loaded", "timing_trials_run",
    ):
        require(type(record.get(key)) is int and record[key] == 0,
                "a source-only V6 phase may not execute a candidate or clock")
    snapshots = record.get("fresh_source_owners")
    require(type(snapshots) is dict and set(snapshots) == set(pins),
            "copy every exact first-party source into each fresh phase")
    for relative, owner in snapshots.items():
        require(type(owner) is dict and set(owner) == V6_PHASE_SOURCE_FIELDS
                and owner.get("sha256") == pins[relative]
                and owner.get("bytes") == SOURCE_OWNERS[family][relative][1]
                and owner.get("path")
                == call_frozen_kernel(
                    module, module.sanitized,
                    str(paths["source"] / relative), root, family,
                    kernel=kernel,
                )
                and type(owner.get("device")) is int
                and type(owner.get("inode")) is int and owner["inode"] > 0
                and owner.get("exclusive_creation") is True
                and owner.get("same_inode_readback_verified") is True
                and type(owner.get("file_fsync_completed")) is bool
                and type(owner.get("write_calls")) is int
                and owner["write_calls"] > 0,
                "a genuine private V6 source snapshot changed or was fabricated")
    outputs = record.get("native_outputs")
    wanted = expected_roles(family)
    require(type(outputs) is dict and set(outputs) == set(wanted),
            "require every real engine, bridge, or build-only Go header")
    for role, filename in wanted.items():
        value = outputs[role]
        require(type(value) is dict and set(value) == V6_OUTPUT_FIELDS
                and value.get("family") == family and value.get("role") == role
                and value.get("file_name") == filename
                and value.get("path")
                == call_frozen_kernel(
                    module, module.sanitized,
                    str(paths["artifact_" + role]), root, family,
                    kernel=kernel,
                )
                and type(value.get("device")) is int
                and type(value.get("inode")) is int and value["inode"] > 0
                and type(value.get("size_bytes")) is int
                and value["size_bytes"] > 0
                and value.get("prebuilt_artifact_read") is False
                and value.get("candidate_imported") is False,
                "reject a foreign, prebuilt, reused, or mislabeled V6 native role")
        checked_digest(value.get("sha256"), family + " " + role)
        if exact_outputs is not None:
            expected = exact_outputs.get(role)
            require(type(expected) is dict
                    and value["sha256"] == expected.get("sha256")
                    and value["size_bytes"] == expected.get("size_bytes"),
                    "reject a changed caller-pinned exact V6 native artifact")
        if role == "generated_header":
            require(value.get("audit") == {
                "generated_by": "cmd/cgo",
                "required_exports": sorted(GO_EXPORTS),
                "required_export_count": 9,
                "externally_supplied": False,
                "forced_bridge_include": True,
            }, "the real compiler-generated nine-export Go header is mandatory")
            continue
        dynamic_key = (phase, role + "_dynamic")
        symbols_key = (phase, role + "_symbols")
        require(dynamic_key in streams and symbols_key in streams,
                "authenticate both complete actual native ELF streams")
        dynamic = call_frozen_kernel(
            module, kernel.parse_elf_dynamic, streams[dynamic_key][0],
            kernel=kernel,
        )
        symbols = call_frozen_kernel(
            module, kernel.parse_elf_symbols, streams[symbols_key][0],
            kernel=kernel,
        )
        actual = call_frozen_kernel(
            module, kernel.validate_elf, family, role, dynamic, symbols,
            kernel=kernel,
        )
        require(value.get("audit") == actual,
                "the genuine complete versioned native ELF audit changed")
    forensic = record.get("native_forensics")
    wanted_native = set(FAMILIES[family]["targets"])
    require(type(forensic) is dict and set(forensic) == wanted_native,
            "retain both actual section and note streams for every native role")
    for role in wanted_native:
        detail = forensic[role]
        require(type(detail) is dict,
                "require an exact native section-and-note forensic role")
        for operation in ("sections", "notes"):
            key = (phase, role + "_" + operation)
            require(key in streams, "a real V6 forensic process was omitted")
            item = detail.get(operation)
            stdout, _, pid = streams[key]
            require(type(item) is dict
                    and set(item) == {
                        "command", "process_pid", "section_payload_digests",
                        "stdout_bytes", "stdout_sha256",
                    }
                    and item.get("command") == role + "_" + operation
                    and item.get("process_pid") == pid
                    and item.get("stdout_bytes") == len(stdout)
                    and item.get("stdout_sha256") == sha256(stdout)
                    and item.get("section_payload_digests") == "NOT RECORDED",
                    "bind every actual V6 section or note to its real process")
    if family == "go":
        proof = call_frozen_kernel(
            module, module.validate_go_package_proof,
            record.get("private_go_package"), root, phase, kernel=kernel,
        )
        require(record["private_go_package"] == proof,
                "require exactly the phase-owned first-party two-file Go package")
    return outputs




def validate_v6_build_documents(
    module: types.ModuleType,
    kernel: types.ModuleType,
    report: dict[str, Any],
    receipt: dict[str, Any],
    archive: bytes,
    archive_owner: dict[str, Any],
    receipt_owner: dict[str, Any],
    *,
    family: str,
    label: str,
    root: str,
    expected_status: str,
    expected_process_count: int,
    expected_completed_phase_count: int,
    context: dict[str, Any],
    exact_outputs: dict[str, dict[str, Any]] | None,
) -> dict[str, Any]:
    family = checked_family(family)
    label = checked_label(label)
    require(expected_status in {"PASS", "FAIL"},
            "require the independently observed actual V6 build outcome")
    passing = expected_status == "PASS"
    require(type(report) is dict and type(receipt) is dict
            and set(receipt) == V6_RECEIPT_FIELDS,
            "require the exact bounded 35-field separately durable V6 receipt")
    if passing:
        require(set(report) == V6_REPORT_FIELDS,
                "require the complete genuine 41-field passing V6 source report")
    else:
        expected = (set(V6_REPORT_FIELDS) - {"owned_source_after"}) | {"error"}
        require(set(report) in (expected, expected | {"owned_source_after"}),
                "preserve the exact genuine failed V6 source report")
    require(report.get("schema") == BUILD_V6_SCHEMA
            and report.get("version") == 6
            and receipt.get("schema") == BUILD_V6_RECEIPT_SCHEMA
            and report.get("status") == expected_status
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == expected_status
            and report.get("family") == receipt.get("family") == family
            and report.get("label") == receipt.get("label") == label,
            "a durable publication never reverses the genuine V6 build outcome")
    for key, wanted in (
        ("source_sha256", BUILD_V6_SOURCE_SHA256),
        ("protocol_sha256", BUILD_V6_PROTOCOL_SHA256),
        ("contract_sha256", BUILD_V6_CONTRACT_SHA256),
    ):
        require(report.get(key) == receipt.get(key) == wanted,
                "reject a mixed V4, V5, or substituted V6 source freeze")
    require(archive_owner.get("mode") == 0o600
            and receipt_owner.get("mode") == 0o600
            and (archive_owner["device"], archive_owner["inode"])
            != (receipt_owner["device"], receipt_owner["inode"]),
            "require distinct actual mode-0600 V6 archive and receipt owners")
    require(receipt.get("archive_relative") == archive_owner["relative"]
            and receipt.get("archive_sha256") == sha256(archive)
            and receipt.get("archive_bytes") == len(archive)
            and receipt.get("uncompressed_sha256") == sha256(canonical(report))
            and receipt.get("uncompressed_bytes") == len(canonical(report))
            and receipt.get("phase1_manifest_sha256") == PHASE1_SHA256,
            "bind the complete actual compressed and canonical V6 report bytes")
    publication = receipt.get("archive_publication")
    require(type(publication) is dict
            and set(publication) == V6_PUBLICATION_FIELDS
            and publication.get("path") == archive_owner["path"]
            and publication.get("sha256") == archive_owner["sha256"]
            and publication.get("bytes") == archive_owner["size_bytes"]
            and publication.get("device") == archive_owner["device"]
            and publication.get("inode") == archive_owner["inode"]
            and publication.get("exclusive_creation") is True
            and publication.get("same_inode_readback_verified") is True
            and publication.get("file_fsync_completed") is True
            and type(publication.get("write_calls")) is int
            and publication["write_calls"] > 0,
            "authenticate the exact genuinely synchronized V6 archive owner")
    sync = receipt.get("archive_directory_fsync")
    require(type(sync) is dict and set(sync) == {"completed", "device", "inode"}
            and sync.get("completed") is True
            and type(sync.get("device")) is int
            and type(sync.get("inode")) is int and sync["inode"] > 0
            and receipt.get("receipt_self_publication") == "NOT CLAIMED",
            "require a genuine directory sync; never assert receipt self-durability")
    pins = {
        relative: digest
        for relative, (digest, _) in SOURCE_OWNERS[family].items()
    }
    accounting = call_frozen_kernel(
        module, module.expected_evidence_accounting, kernel=kernel,
    )
    require(accounting.get("distinct_evidence_file_owner_count") == 61
            and accounting.get("all_historical_versions_actual_compiler_process_count")
            == 117
            and report.get("evidence_accounting")
            == receipt.get("evidence_accounting") == accounting
            and report.get("owned_source_sha256")
            == receipt.get("owned_source_sha256") == pins
            and report.get("historical_candidate_evidence_owner_count") == 51,
            "preserve the honest 61-owner, 117-process V6 historical baseline")
    frozen = report.get("frozen_correctness")
    require(type(frozen) is dict
            and set(frozen) == {
                "candidate_correctness", "candidate_qualified_count",
                "case_execution_count", "holdout", "performance",
                "status", "suite_count",
            }
            and frozen.get("status") == "PASS"
            and frozen.get("suite_count") == 13
            and frozen.get("case_execution_count") == 31237
            and frozen.get("candidate_qualified_count") == 0
            and frozen.get("candidate_correctness") == "NOT MEASURED"
            and frozen.get("performance") == "NOT MEASURED"
            and frozen.get("holdout") == "NOT OPENED",
            "retain the exact complete unchanged frozen 13-suite P0 oracle")
    expected_v4 = [
        {
            "family": name,
            "build_status": item["build_status"],
            "receipt_status": item["receipt_status"],
            "process_count": item["process_count"],
            "failure_preserved": item["build_status"] == "FAIL",
            "candidate_qualified_count": 0,
        }
        for name, item in module.HISTORICAL_V4.items()
    ]
    require(report.get("preserved_v2_history")
            == call_frozen_kernel(
                module, module.expected_v2_summaries, kernel=kernel
            )
            and report.get("preserved_v4_history") == expected_v4
            and report.get("pinned_toolchains") == context["pinned_toolchains"],
            "preserve all actual failures, original owners, and pinned compilers")
    for record, name in ((report, "actual V6 report"),
                         (receipt, "actual V6 receipt")):
        call_frozen_kernel(
            module, module.require_unmeasured, record,
            label=name, kernel=kernel,
        )
    require(report.get("reference_processes_started") == 0
            and report.get("final_cases_read") == 0
            and report.get("network_requests") == 0
            and report.get("winner_selected") is False
            and receipt.get("winner_selected") is False,
            "a source build cannot run reference cases, open the holdout, or win")
    expected_schedule = module.EXPECTED_BUILD_POLICY[
        "v6_future_process_count_by_family"
    ][family]
    require(report.get("expected_v6_compiler_process_count")
            == receipt.get("expected_v6_compiler_process_count")
            == expected_schedule
            and report.get("actual_v6_compiler_process_count")
            == receipt.get("actual_v6_compiler_process_count")
            == expected_process_count,
            "bind every expected and genuinely observed V6 process")
    require(report.get("fresh_private_root") == SANITIZED_BUILD_ROOT,
            "a V6 report must retain its exact sanitized fresh private root")
    before = report.get("owned_source_before")
    require(type(before) is dict and set(before) == set(pins),
            "require the complete genuine pre-build first-party source graph")
    after = report.get("owned_source_after")
    if passing or after is not None:
        require(type(after) is dict and set(after) == set(pins),
                "require the complete passing V6 source graph after both phases")
    for relative, before_owner in before.items():
        require(type(before_owner) is dict
                and set(before_owner) == V6_SOURCE_OWNER_FIELDS
                and before_owner.get("path") == ROOT + "/" + relative
                and before_owner.get("sha256") == pins[relative]
                and before_owner.get("size_bytes")
                == SOURCE_OWNERS[family][relative][1]
                and type(before_owner.get("device")) is int
                and type(before_owner.get("inode")) is int
                and before_owner["inode"] > 0
                and type(before_owner.get("executable")) is bool,
                "authenticate exact original V6 source owner schemas")
        if after is not None:
            final_owner = after[relative]
            require(type(final_owner) is dict
                    and set(final_owner) == V6_SOURCE_OWNER_FIELDS
                    and all(final_owner.get(key) == before_owner.get(key)
                            for key in V6_SOURCE_OWNER_FIELDS),
                    "an actual independently owned source changed during building")
    streams = validate_v6_processes(
        module, kernel, family, root, report.get("processes"),
        expected_count=expected_process_count, passing=passing,
    )
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == expected_completed_phase_count
            and 0 <= expected_completed_phase_count <= 2
            and [item.get("name") for item in phases if type(item) is dict]
            == ["reference-a", "reference-b"][:expected_completed_phase_count],
            "preserve the actual number and order of complete V6 source phases")
    verified: dict[str, dict[str, Any]] = {}
    for index, phase in enumerate(phases):
        outputs = validate_v6_phase(
            module, kernel, family, root, phase,
            ("reference-a", "reference-b")[index], streams, pins,
            exact_outputs=exact_outputs if passing else None,
        )
        if not verified:
            verified = outputs
    if passing:
        require(expected_completed_phase_count == 2,
                "never activate an incomplete V6 source-built family")
        reproduction = call_frozen_kernel(
            module, kernel.verify_reproducible_phases,
            family, phases, report["processes"], kernel=kernel,
        )
        require(report.get("reproducibility") == reproduction
                and reproduction.get("byte_identical") is True
                and reproduction.get("independent_fresh_phase_count") == 2
                and reproduction.get("unique_process_count")
                == expected_process_count,
                "require two actually byte-identical inode-distinct V6 phases")
        if family == "go":
            package = call_frozen_kernel(
                module, module.verify_go_phase_proofs,
                root, phases, report["processes"], kernel=kernel,
            )
            require(report.get("go_private_package_reproducibility") == package,
                    "require the complete two-phase genuine private Go package")
        else:
            require(report.get("go_private_package_reproducibility") is None,
                    "a non-Go family cannot borrow a Go package or bridge")
    else:
        require(report.get("reproducibility") is None,
                "a failed source build must never become reproducible")
    return {
        "family": family,
        "build_status": expected_status,
        "receipt_status": "PASS",
        "process_count": expected_process_count,
        "completed_phase_count": expected_completed_phase_count,
        "qualified_candidate_count": 0,
        "archive_owner": archive_owner,
        "receipt_owner": receipt_owner,
        "verified": verified,
    }


def collect_v6_baseline_evidence_owners(
    context: dict[str, Any],
) -> set[tuple[int, int]]:
    result: set[tuple[int, int]] = set()

    def accept_owner(owner: Any) -> None:
        require(type(owner) is dict and owner.get("mode") == 0o600
                and type(owner.get("device")) is int
                and type(owner.get("inode")) is int and owner["inode"] > 0,
                "require a genuine independently owned historical evidence file")
        identity = (owner["device"], owner["inode"])
        require(identity not in result,
                "reject aliased candidate, source-build, or receipt owners")
        result.add(identity)

    candidate = context.get("preserved_candidate_history")
    require(type(candidate) is dict and candidate.get("owner_count") == 51,
            "keep all actual historical candidate evidence owners")
    families = candidate.get("families")
    require(type(families) is dict and set(families) == {"c", "rust", "zig"},
            "preserve all three genuinely measured candidate histories")
    for family in ("c", "rust", "zig"):
        item = families[family]
        require(type(item) is dict and type(item.get("owners")) is list
                and len(item["owners"]) == 17,
                "each tested candidate retains exactly 17 genuine evidence owners")
        for owner in item["owners"]:
            accept_owner(owner)
    for key, count in (("preserved_v4_history", 3),
                       ("preserved_v5_history", 2)):
        records = context.get(key)
        require(type(records) is list and len(records) == count,
                "preserve each actual V4 and V5 PASS or FAIL evidence pair")
        for record in records:
            require(type(record) is dict,
                    "a historical evidence record must retain both actual owners")
            accept_owner(record.get("archive"))
            accept_owner(record.get("receipt"))
    require(len(result) == 61,
            "the frozen V6 historical baseline has exactly 61 evidence owners")
    return result


def verify_published_v6_build_history(
    module: types.ModuleType,
    kernel: types.ModuleType,
    context: dict[str, Any],
) -> dict[str, Any]:
    identities = collect_v6_baseline_evidence_owners(context)
    results: dict[str, dict[str, Any]] = {}
    for family, item in HISTORICAL_V6_RECORDS.items():
        require(family == item.get("family")
                and item.get("status") in {"PASS", "FAIL"},
                "use only explicitly observed actual V6 build outcomes")
        archive, archive_owner = read_owned(
            ROOT, item["archive"], item["archive_sha256"],
            maximum=MAX_ARCHIVE_BYTES, exact_size=item["archive_bytes"],
        )
        receipt_raw, receipt_owner = read_owned(
            ROOT, item["receipt"], item["receipt_sha256"],
            maximum=MAX_SOURCE_BYTES, exact_size=item["receipt_bytes"],
        )
        for owner in (archive_owner, receipt_owner):
            identity = (owner["device"], owner["inode"])
            require(owner["mode"] == 0o600 and identity not in identities,
                    "every later V6 evidence file must be a distinct mode-0600 owner")
            identities.add(identity)
        plain = bounded_gzip(archive, expected_size=item["plain_bytes"])
        require(sha256(plain) == item["plain_sha256"],
                "the exact independently observed V6 report changed")
        report = decode_document(
            plain, "actual " + family + " V6 source-build report"
        )
        receipt = decode_document(
            receipt_raw, "actual " + family + " V6 durable publication"
        )
        root = "/tmp/" + BUILD_V6_PREFIX + family + "-synthetic"
        actual = validate_v6_build_documents(
            module, kernel, report, receipt, archive,
            archive_owner, receipt_owner,
            family=family, label=item["label"], root=root,
            expected_status=item["status"],
            expected_process_count=item["process_count"],
            expected_completed_phase_count=item["completed_phase_count"],
            context=context,
            exact_outputs=item.get("native_outputs"),
        )
        if item["status"] == "FAIL":
            require(report.get("error") == item.get("error")
                    and item.get("successful_process_count")
                    == sum(
                        record["exit_status"] == 0
                        for record in report["processes"]
                    )
                    and item.get("differing_raw_binary_section")
                    == "NOT RECORDED",
                    "preserve the actual Fortran failure; invent no compiler or section cause")
            expected_phases = item.get("phase_outputs")
            require(type(expected_phases) is list
                    and len(expected_phases) == len(report["build_phases"]),
                    "retain every actually completed failed-build phase")
            for observed, frozen in zip(
                report["build_phases"], expected_phases, strict=True
            ):
                require(observed.get("name") == frozen.get("name")
                        and set(observed.get("native_outputs", {}))
                        == set(frozen.get("native_outputs", {})),
                        "preserve the exact real failed Fortran native roles")
                for role, saved in frozen["native_outputs"].items():
                    native = observed["native_outputs"][role]
                    forensic = observed["native_forensics"][role]
                    require(native.get("sha256") == saved.get("sha256")
                            and native.get("size_bytes")
                            == saved.get("size_bytes")
                            and forensic["notes"].get("stdout_sha256")
                            == saved.get("notes_sha256")
                            and forensic["notes"].get("stdout_bytes")
                            == saved.get("notes_bytes")
                            and forensic["sections"].get("stdout_sha256")
                            == saved.get("sections_sha256")
                            and forensic["sections"].get("stdout_bytes")
                            == saved.get("sections_bytes"),
                            "bind the exact failed engine, identical bridge, notes, and sections")
            if family == "fortran":
                first, second = report["build_phases"]
                require(
                    first["native_outputs"]["engine"]["sha256"]
                    != second["native_outputs"]["engine"]["sha256"]
                    and first["native_outputs"]["bridge"]["sha256"]
                    == second["native_outputs"]["bridge"]["sha256"]
                    and first["native_forensics"]["engine"][
                        "notes"
                    ]["stdout_bytes"] == 0
                    and second["native_forensics"]["engine"][
                        "notes"
                    ]["stdout_bytes"] == 0,
                    "the actual V6 Fortran has unequal engines, equal bridges, and no build IDs",
                )
        results[family] = actual
    expected = 61 + 2 * len(HISTORICAL_V6_RECORDS)
    require(len(identities) == expected
            and expected
            == expected_historical_evidence()["total_distinct_evidence_owner_count"]
            and sum(item["process_count"] for item in results.values())
            == expected_historical_evidence()[
                "historical_build_process_ledger"
            ]["v6_process_count"],
            "authenticate every real independent historical V6 owner and process")
    return {
        "families": results,
        "family_count": len(results),
        "evidence_owner_count": 2 * len(results),
        "total_distinct_historical_evidence_owner_count": len(identities),
        "process_count": sum(item["process_count"] for item in results.values()),
    }



def verify_historical_record(label: str, spec: dict[str, Any]) -> dict[str, Any]:
    archive, archive_owner = read_owned(ROOT, spec["archive"], spec["archive_sha256"],
                                        maximum=MAX_ARCHIVE_BYTES,
                                        exact_size=spec["archive_bytes"])
    receipt_raw, receipt_owner = read_owned(ROOT, spec["receipt"], spec["receipt_sha256"],
                                           maximum=MAX_SOURCE_BYTES,
                                           exact_size=spec["receipt_bytes"])
    plain = bounded_gzip(archive, expected_size=spec["plain_bytes"])
    require(sha256(plain) == spec["plain_sha256"],
            "the complete authentic historical archive was substituted")
    report = decode_document(plain, "retained " + label + " report")
    receipt = decode_document(receipt_raw, "retained " + label + " receipt")
    require(report.get("schema") == spec["schema"]
            and report.get("status") == spec["status"]
            and report.get("family", report.get("candidate_family")) == spec["family"]
            and receipt.get("status") == "PASS"
            and receipt.get("uncompressed_sha256") == spec["plain_sha256"]
            and receipt.get("uncompressed_bytes") == spec["plain_bytes"],
            "reject relabeled or falsely qualifying historical build/candidate evidence")
    if spec["process_count"] is not None:
        processes = report.get("processes")
        require(type(processes) is list and len(processes) == spec["process_count"],
                "preserve every actual historic compiler and inspection process")
        seen: set[int] = set()
        for process in processes:
            require(type(process) is dict and type(process.get("pid")) is int
                    and process["pid"] > 0 and process["pid"] not in seen
                    and process.get("exit_status") == 0,
                    "preserve genuine distinct historical process IDs within one actual run")
            seen.add(process["pid"])
            decode_process_output(process, "stdout")
            decode_process_output(process, "stderr")
        require(receipt.get("build_status") == spec["status"],
                "a durable historical receipt may not reverse a build failure")
        if label.startswith("v2_"):
            old = report.get("historical_v1_c")
            require(type(old) is dict
                    and old.get("status") == "AUTHENTIC HISTORICAL BUILD; V1 SYMBOL AUDIT FALSIFIED",
                    "retain the authentic falsification of the V1 symbol parser")
    else:
        if label == "v6_zig_subinterpreter_failure":
            require(receipt.get("result_status") == "FAIL"
                    and receipt.get("candidate_family") == "zig"
                    and receipt.get("phase1_case_execution_denominator") == 31237,
                    "never relabel the real Zig subinterpreter failure")
        else:
            require(receipt.get("candidate_status") == "FAIL"
                    and receipt.get("failure_preserved") is True
                    and receipt.get("candidate_family") == "zig"
                    and receipt.get("candidate_qualified_for_hidden_benchmark") is False,
                    "never promote an actual V6 worker/candidate failure to qualification")
    require(receipt.get("performance") == "NOT MEASURED"
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0,
            "historical evidence may not authorize performance, clocks, or a holdout")
    return {"id": label, "family": spec["family"],
            "result_status": spec["status"],
            "archive_sha256": archive_owner["sha256"],
            "receipt_sha256": receipt_owner["sha256"],
            "process_count": spec["process_count"],
            "failure_preserved": spec["status"] == "FAIL"}


def verify_complete_candidate_history(graph_raw: bytes) -> dict[str, Any]:
    graph = decode_document(graph_raw, "frozen three-family actual evidence graph",
                            exact=False)
    require(graph.get("schema") == "rebar-candidate-current-overview-v7-inputs"
            and graph.get("version") == 7
            and graph.get("full_case_denominator") == 31237
            and graph.get("suite_count") == 13,
            "require the immutable exact historical candidate evidence overview")
    records = graph.get("families")
    frozen = graph.get("frozen_inputs")
    require(type(records) is list and type(frozen) is dict,
            "the complete historical-family and frozen-restoration graph is mandatory")
    by_family = {item.get("family"): item for item in records if type(item) is dict}
    require({"c", "rust", "zig"}.issubset(by_family),
            "preserve all three actually tested independent candidate families")
    expected_outer = {
        "c": {
            "archive": ("oracle/phase2/evidence/frozen-p0-candidate-v5-c-phase2-v5-failures.json.gz", "f8c4465be0d982445f79ec66744c710b20c64bd308eaff8a12ba571b5bb0ef91"),
            "receipt": ("oracle/phase2/evidence/frozen-p0-candidate-v5-c-phase2-v5-failures-publication-receipt.json", "10b1bb903ae3e6cf6b0b732e0518bfadce8f17a0021c36ba86bef1e641da07a1"),
            "worker_archive": ("oracle/phase2/evidence/frozen-p0-candidate-worker-v3-c-phase2-v5-failures.json.gz", "149bc01c571c15034896d26eb05708985a7a3a49e361e26199682860f8c83e13"),
            "worker_receipt": ("oracle/phase2/evidence/frozen-p0-candidate-worker-v3-c-phase2-v5-failures-publication-receipt.json", "fc68840c6bbf0e9bc1510894b575d0111246401eba70e8706e2a33542365fc55"),
            "restoration": ("oracle/phase2/evidence/frozen-p0-candidate-v5-c-phase2-v5-restoration-receipt.json", "2bc016478561ea93c4783773a89789af4534368b9388f2d81baf2aefcdeb9dde"),
        },
        "rust": {
            "archive": ("oracle/phase2/evidence/frozen-p0-candidate-v5-rust-phase2-v5-failures.json.gz", "bf0915a4dab62ebaea67b92258eafbc01f52b436b70f81bf7e0ca42211f95bff"),
            "receipt": ("oracle/phase2/evidence/frozen-p0-candidate-v5-rust-phase2-v5-failures-publication-receipt.json", "72070ab4f68200c305d317a59c7ff6405888d23fadaaf04835aba68d33a6c6ec"),
            "worker_archive": ("oracle/phase2/evidence/frozen-p0-candidate-worker-v3-rust-phase2-v5-failures.json.gz", "a2106050b59130a9eb7f083d13c2e42e22dcf9a33f5a7b35b634ff9dd9b2f9ae"),
            "worker_receipt": ("oracle/phase2/evidence/frozen-p0-candidate-worker-v3-rust-phase2-v5-failures-publication-receipt.json", "f6fe003c100a93e06239a072380c4f3839dc9863391b939ebfc6d667b174f0d9"),
            "restoration": ("oracle/phase2/evidence/frozen-p0-candidate-v5-rust-phase2-v5-restoration-receipt.json", "3cd828fbd507d048d0e80715efef754930e89f3c176717ba1dd8985784832889"),
        },
    }
    identities: set[tuple[int, int]] = set()
    result: dict[str, Any] = {}

    def read_evidence(relative: str, digest: str,
                      exact_size: int | None = None) -> dict[str, Any]:
        maximum = MAX_ARCHIVE_BYTES if relative.endswith(".json.gz") else MAX_SOURCE_BYTES
        raw, owner = read_owned(ROOT, relative, digest, maximum=maximum,
                                exact_size=exact_size)
        require(owner["mode"] == 0o600,
                "every actual preserved candidate evidence owner must be mode 0600")
        identity = (owner["device"], owner["inode"])
        require(identity not in identities,
                "reject reused, hard-linked, or double-counted candidate evidence owners")
        identities.add(identity)
        if relative.endswith(".json"):
            receipt = decode_document(raw, "actual independent historical publication")
            require(receipt.get("status") == "PASS",
                    "an actual durable historical publication receipt was substituted")
        return owner

    for family in ("c", "rust"):
        family_record = by_family[family]
        evidence = family_record.get("correctness_evidence")
        require(type(evidence) is dict
                and evidence.get("expected_gate_status") == "FAIL"
                and evidence.get("qualified_case_executions") == 0,
                "preserve the actual failed C/Rust qualification without changing its denominator")
        owners: list[dict[str, Any]] = []
        for role in ("archive", "receipt", "worker_archive", "worker_receipt"):
            value = evidence.get(role)
            path, digest = expected_outer[family][role]
            require(type(value) is dict and value.get("path") == path
                    and value.get("sha256") == digest,
                    "the exact published C/Rust actual candidate evidence was changed")
            owners.append(read_evidence(path, digest))
        subordinate = family_record.get("subordinate_evidence")
        require(type(subordinate) is list and len(subordinate) == 12,
                "retain six complete independent subordinate archive/receipt pairs")
        for item in subordinate:
            require(type(item) is dict and set(item) == {"path", "sha256"},
                    "each subordinate evidence owner requires an exact path and hash")
            path = checked_relative(item["path"])
            require((path.startswith("experiments/rust_public_practice_v1/" + family + "-")
                     or path.startswith("oracle/phase2/evidence/owned-candidate-subinterpreters-v1-"
                                        + family + "-"))
                    and path.endswith((".json", ".json.gz")),
                    "reject a foreign, broad, or cross-family subordinate owner")
            owners.append(read_evidence(path, checked_digest(item["sha256"], path)))
        restoration = frozen.get("v5_" + family + "_restoration_receipt")
        path, digest = expected_outer[family]["restoration"]
        require(type(restoration) is dict and restoration.get("path") == path
                and restoration.get("sha256") == digest,
                "preserve the actual owner-only historical candidate restoration receipt")
        owners.append(read_evidence(path, digest))
        require(len(owners) == 17,
                "each actually evaluated family requires exactly 17 evidence owners")
        result[family] = {"owner_count": len(owners), "result_status": "FAIL",
                          "qualified_candidate_count": 0, "owners": owners}

    zig_owners: list[dict[str, Any]] = []
    for key in ("v6_zig_candidate_failure", "v6_zig_worker_failure",
                "v6_zig_subinterpreter_failure"):
        record = HISTORICAL_RECORDS[key]
        zig_owners.append(read_evidence(record["archive"],
                                        record["archive_sha256"],
                                        record["archive_bytes"]))
        zig_owners.append(read_evidence(record["receipt"],
                                        record["receipt_sha256"],
                                        record["receipt_bytes"]))
    for path, digest, size in ZIG_V6_SUBORDINATE:
        zig_owners.append(read_evidence(path, digest, size))
    zig_owners.append(read_evidence(RESTORATION_RELATIVE, RESTORATION_SHA256,
                                    RESTORATION_BYTES))
    require(len(zig_owners) == 17, "preserve all seventeen independently published Zig owners")
    result["zig"] = {"owner_count": 17, "result_status": "FAIL",
                     "qualified_candidate_count": 0, "owners": zig_owners}
    require(len(identities) == 51,
            "all three tested families require 51 distinct real evidence file inodes")
    return {"family_count": 3, "owner_count": 51,
            "owners_per_family": 17, "families": result,
            "qualified_candidate_count": 0, "performance": "NOT MEASURED",
            "holdout": "NOT OPENED"}


def validate_preserved_v4_documents(
    spec: dict[str, Any], report: dict[str, Any],
    receipt: dict[str, Any], archive: bytes,
) -> dict[str, Any]:
    family = checked_family(spec.get("family"))
    status = spec.get("status")
    require(family in {"cpp", "go", "fortran"}
            and status in {"PASS", "FAIL"}
            and status == HISTORICAL_V4_RECORDS[family]["status"]
            and spec.get("process_count")
            == HISTORICAL_V4_RECORDS[family]["process_count"]
            and spec.get("completed_phase_count")
            == HISTORICAL_V4_RECORDS[family]["completed_phase_count"]
            and report.get("schema") == BUILD_SCHEMA
            and report.get("version") == 4
            and receipt.get("schema") == BUILD_RECEIPT_SCHEMA
            and report.get("family") == receipt.get("family") == family
            and report.get("label") == receipt.get("label") == spec.get("label")
            and report.get("status") == receipt.get("build_status") == status
            and receipt.get("status") == "PASS",
            "preserve the exact actual V4 result; a published failure is not a passing build")
    for key, expected in (("source_sha256", BUILD_SOURCE_SHA256),
                          ("protocol_sha256", BUILD_PROTOCOL_SHA256),
                          ("contract_sha256", BUILD_CONTRACT_SHA256)):
        require(report.get(key) == receipt.get(key) == expected,
                "the genuine preserved V4 outcome belongs to a different source freeze")
    require(sha256(archive) == spec.get("archive_sha256")
            and len(archive) == spec.get("archive_bytes")
            and sha256(canonical(report)) == spec.get("plain_sha256")
            and len(canonical(report)) == spec.get("plain_bytes")
            and sha256(canonical(receipt)) == spec.get("receipt_sha256")
            and len(canonical(receipt)) == spec.get("receipt_bytes")
            and receipt.get("archive_relative") == spec.get("archive")
            and receipt.get("archive_sha256") == spec.get("archive_sha256")
            and receipt.get("archive_bytes") == spec.get("archive_bytes")
            and receipt.get("uncompressed_sha256") == spec.get("plain_sha256")
            and receipt.get("uncompressed_bytes") == spec.get("plain_bytes")
            and receipt.get("phase1_manifest_sha256") == PHASE1_SHA256,
            "independently authenticate every exact published V4 archive and failure receipt")
    publication = receipt.get("archive_publication")
    require(type(publication) is dict
            and publication.get("path") == ROOT + "/" + spec["archive"]
            and publication.get("sha256") == spec["archive_sha256"]
            and publication.get("bytes") == spec["archive_bytes"]
            and publication.get("exclusive_creation") is True
            and publication.get("same_inode_readback_verified") is True
            and publication.get("file_fsync_completed") is True
            and type(publication.get("device")) is int
            and type(publication.get("inode")) is int
            and publication["inode"] > 0
            and type(publication.get("write_calls")) is int
            and publication["write_calls"] > 0,
            "every actual V4 outcome requires its own owner-only durable publication")
    directory = receipt.get("archive_directory_fsync")
    require(type(directory) is dict and directory.get("completed") is True
            and type(directory.get("device")) is int
            and type(directory.get("inode")) is int and directory["inode"] > 0
            and receipt.get("receipt_self_publication") == "NOT CLAIMED",
            "a historical V4 failure receipt must not invent its own publication")
    for document in (report, receipt):
        for key in ("candidate_processes_started", "candidate_imports",
                    "native_libraries_loaded", "hidden_cases_read",
                    "benchmark_files_read", "clock_samples", "timing_trials_run"):
            require(type(document.get(key)) is int and document[key] == 0,
                    "historical source builds must not conceal a candidate or benchmark")
        require(document.get("candidate_correctness") == "NOT MEASURED"
                and document.get("performance") == "NOT MEASURED"
                and document.get("holdout") == "NOT OPENED"
                and document.get("winner_selected") is False,
                "a V4 source build cannot qualify an untested candidate or open a holdout")
    validate_build_history(report)
    oracle = report.get("frozen_correctness")
    require(type(oracle) is dict and oracle.get("status") == "PASS"
            and oracle.get("suite_count") == 13
            and oracle.get("case_execution_count") == 31237
            and oracle.get("candidate_qualified_count") == 0,
            "every historical V4 outcome must preserve the exact actual CPython oracle")
    pins = {path: digest for path, (digest, _) in SOURCE_OWNERS[family].items()}
    require(report.get("fresh_private_root") == SANITIZED_BUILD_ROOT
            and report.get("owned_source_sha256") == pins
            and receipt.get("owned_source_sha256") == pins,
            "the preserved V4 outcome changed its full first-party semantic source closure")
    before = report.get("owned_source_before")
    require(type(before) is dict and set(before) == set(pins),
            "a preserved passing or failed build omitted its original source owners")
    for relative, (digest, size) in SOURCE_OWNERS[family].items():
        owner = before[relative]
        require(type(owner) is dict and owner.get("path") == ROOT + "/" + relative
                and owner.get("sha256") == digest
                and type(owner.get("size_bytes")) is int
                and owner["size_bytes"] == size
                and type(owner.get("device")) is int
                and type(owner.get("inode")) is int and owner["inode"] > 0,
                "the actual historical V4 source owner was omitted or substituted")
    root = "/tmp/" + BUILD_PREFIX + family + "-preserved-" + spec["label"]
    processes = report.get("processes")
    phases = report.get("build_phases")
    require(type(processes) is list
            and len(processes) == spec["process_count"]
            and type(phases) is list
            and len(phases) == spec["completed_phase_count"],
            "preserve all real processes and completed phases of each actual V4 outcome")
    if family == "cpp":
        require(status == "PASS" and len(phases) == 2,
                "the actual successful C++ V4 build may not be relabeled or weakened")
        first = spec["phase_outputs"][0]
        arguments = {
            "family": family, "build_label": spec["label"], "build_root": root,
            "build_source_sha256": BUILD_SOURCE_SHA256,
            "build_protocol_sha256": BUILD_PROTOCOL_SHA256,
            "build_contract_sha256": BUILD_CONTRACT_SHA256,
            "build_report_sha256": spec["archive_sha256"],
            "build_receipt_sha256": spec["receipt_sha256"],
            "native_hashes": {role: value[0] for role, value in first.items()},
            "native_sizes": {role: value[1] for role, value in first.items()},
        }
        verified = validate_build_report(report, receipt, archive, arguments, pins)
        require(set(verified) == {"bridge"}
                and verified["bridge"]["sha256"] == first["bridge"][0],
                "the genuine independently reproduced C++ bridge was substituted")
    elif family == "go":
        require(status == "FAIL" and phases == []
                and report.get("reproducibility") is None
                and report.get("error") == {
                    "type": "BuildError", "message": spec["error_message"]},
                "preserve the real Go compiler failure, zero phases, and missing header")
        schedule = process_schedule(family)[:4]
        require(schedule == ["readelf_version", "gcc_version", "go_version",
                             "build_go_engine"],
                "the preserved four-step Go failure is not the frozen actual command prefix")
        commands = planned_commands(root, family, "reference-a")
        environment = expected_environment(root, family, "reference-a")
        paths = phase_paths(root, family, "reference-a")
        pids: set[int] = set()
        for index, (name, process) in enumerate(zip(schedule, processes, strict=True)):
            expected_exit = 1 if name == "build_go_engine" else 0
            cwd = (paths["go_module_directory"] if name == "build_go_engine"
                   else paths["base"])
            require(type(process) is dict and process.get("name") == name
                    and type(process.get("pid")) is int and process["pid"] > 0
                    and process["pid"] not in pids
                    and type(process.get("exit_status")) is int
                    and process["exit_status"] == expected_exit
                    and process.get("shell") is False
                    and process.get("argv") == commands[name]
                    and process.get("environment") == environment
                    and process.get("working_directory") == sanitized(cwd, root),
                    "preserve the exact actual Go compiler failure and offline command")
            pids.add(process["pid"])
            stdout = decode_process_output(process, "stdout")
            stderr = decode_process_output(process, "stderr")
            if name == "readelf_version":
                require(b"readelf" in stdout.split(b"\n", 1)[0].lower(),
                        "the authentic failed Go run substituted its ELF inspector")
            elif name == "gcc_version":
                require(b"13." in stdout.split(b"\n", 1)[0],
                        "the authentic failed Go run substituted its GNU compiler")
            elif name == "go_version":
                require(stdout == b"go version go1.26.3 linux/amd64\n",
                        "the authentic failed Go run substituted its Go toolchain")
            else:
                require(b"py_bridge.c" in stderr and b"Python.h" in stderr
                        and b"No such file or directory" in stderr,
                        "preserve why the Go compiler failed; never invent a generated header")
    else:
        require(status == "FAIL" and len(phases) == 2
                and report.get("reproducibility") is None
                and report.get("error") == {
                    "type": "BuildError", "message": spec["error_message"]},
                "preserve the real two-phase Fortran reproducibility failure")
        streams = validate_processes(family, root, processes)
        seen: dict[str, set[tuple[int, int]]] = {
            role: set() for role in FAMILIES[family]["targets"]
        }
        for index, phase in enumerate(phases):
            name = ("reference-a", "reference-b")[index]
            prefix = SANITIZED_BUILD_ROOT + "/" + name
            require(type(phase) is dict and phase.get("name") == name
                    and phase.get("fresh_source_directory") == prefix + "/source"
                    and phase.get("fresh_native_directory") == prefix + "/native"
                    and phase.get("fresh_temporary_directory") == prefix + "/temporary",
                    "both genuine Fortran phases must remain independently complete")
            copies = phase.get("fresh_source_owners")
            require(type(copies) is dict and set(copies) == set(pins),
                    "a failed Fortran phase omitted its own frozen source copies")
            for relative, (digest, size) in SOURCE_OWNERS[family].items():
                copy_owner = copies[relative]
                require(type(copy_owner) is dict
                        and copy_owner.get("path") == prefix + "/source/" + relative
                        and copy_owner.get("sha256") == digest
                        and copy_owner.get("bytes") == size
                        and type(copy_owner.get("device")) is int
                        and type(copy_owner.get("inode")) is int
                        and copy_owner["inode"] > 0
                        and copy_owner.get("exclusive_creation") is True,
                        "a genuine complete Fortran phase source was omitted or reused")
            outputs = phase.get("native_outputs")
            require(type(outputs) is dict
                    and set(outputs) == set(FAMILIES[family]["targets"])
                    and set(spec["phase_outputs"][index]) == set(outputs),
                    "preserve the actual Fortran engine and bridge in both phases")
            for role, filename in FAMILIES[family]["targets"].items():
                output = outputs[role]
                digest, size = spec["phase_outputs"][index][role]
                require(type(output) is dict and output.get("family") == family
                        and output.get("role") == role
                        and output.get("file_name") == filename
                        and output.get("path") == prefix + "/native/" + filename
                        and output.get("sha256") == digest
                        and type(output.get("size_bytes")) is int
                        and output["size_bytes"] == size
                        and type(output.get("device")) is int
                        and type(output.get("inode")) is int
                        and output["inode"] > 0
                        and output.get("prebuilt_artifact_read") is False
                        and output.get("candidate_imported") is False,
                        "the exact genuinely compiled Fortran engine or bridge was changed")
                identity = (output["device"], output["inode"])
                require(identity not in seen[role],
                        "the two Fortran phases reused a native-output inode")
                seen[role].add(identity)
                actual_audit = validate_elf(
                    family, role,
                    parse_dynamic(streams[(name, role + "_dynamic")]),
                    parse_symbols(streams[(name, role + "_symbols")]))
                require(output.get("audit") == actual_audit,
                        "preserve all actual Fortran exports, reverse callbacks, and ELF streams")
        first, second = spec["phase_outputs"]
        require(first["bridge"] == second["bridge"]
                and first["engine"] != second["engine"],
                "a reproducibility-failed Fortran engine must never be reported as identical")
    return {"family": family, "build_status": status,
            "receipt_publication_status": "PASS",
            "archive_sha256": spec["archive_sha256"],
            "receipt_sha256": spec["receipt_sha256"],
            "process_count": spec["process_count"],
            "completed_phase_count": spec["completed_phase_count"],
            "failure_preserved": status == "FAIL",
            "qualified_candidate_count": 0,
            "performance": "NOT MEASURED", "holdout": "NOT OPENED"}


def verify_published_v4_build_history(
    candidate_history: dict[str, Any],
) -> dict[str, Any]:
    require(type(candidate_history) is dict
            and candidate_history.get("family_count") == 3
            and candidate_history.get("owner_count") == 51,
            "authenticate all actual candidate owners before preserving later V4 builds")
    candidate_families = candidate_history.get("families")
    require(type(candidate_families) is dict
            and set(candidate_families) == {"c", "rust", "zig"},
            "do not merge historical build outcomes with candidate-correctness evidence")
    identities: set[tuple[int, int]] = set()
    for family in ("c", "rust", "zig"):
        record = candidate_families[family]
        owners = record.get("owners") if type(record) is dict else None
        require(type(owners) is list and len(owners) == 17,
                "retain exactly seventeen actual tested-candidate owners per family")
        for owner in owners:
            require(type(owner) is dict and owner.get("mode") == 0o600
                    and type(owner.get("device")) is int
                    and type(owner.get("inode")) is int and owner["inode"] > 0,
                    "a preserved candidate evidence owner is not genuine or owner-only")
            identity = (owner["device"], owner["inode"])
            require(identity not in identities,
                    "reject reused historical candidate or build evidence file owners")
            identities.add(identity)
    require(len(identities) == 51,
            "the candidate-correctness ledger remains exactly 51 distinct owners")
    results: dict[str, dict[str, Any]] = {}
    for family, spec in HISTORICAL_V4_RECORDS.items():
        archive, archive_owner = read_owned(
            ROOT, spec["archive"], spec["archive_sha256"],
            maximum=MAX_ARCHIVE_BYTES, exact_size=spec["archive_bytes"])
        receipt_raw, receipt_owner = read_owned(
            ROOT, spec["receipt"], spec["receipt_sha256"],
            maximum=MAX_SOURCE_BYTES, exact_size=spec["receipt_bytes"])
        for owner in (archive_owner, receipt_owner):
            require(owner["mode"] == 0o600,
                    "every published V4 build evidence owner must remain mode 0600")
            identity = (owner["device"], owner["inode"])
            require(identity not in identities,
                    "the six later V4 owners must not alias any of the original 51")
            identities.add(identity)
        plain = bounded_gzip(archive, expected_size=spec["plain_bytes"])
        require(sha256(plain) == spec["plain_sha256"],
                "the preserved real passing or failing V4 archive was substituted")
        report = decode_document(plain, "preserved actual " + family + " V4 source build")
        receipt = decode_document(receipt_raw,
                                  "preserved actual " + family + " V4 publication receipt")
        result = validate_preserved_v4_documents(spec, report, receipt, archive)
        publication = receipt["archive_publication"]
        require(publication.get("device") == archive_owner["device"]
                and publication.get("inode") == archive_owner["inode"],
                "the preserved V4 publication must identify its own actual archive inode")
        results[family] = {**result,
                           "archive_owner": archive_owner,
                           "receipt_owner": receipt_owner}
    require(set(results) == {"cpp", "go", "fortran"}
            and len(identities) == 57
            and sum(item["process_count"] for item in results.values()) == 32,
            "preserve all 57 distinct evidence owners and all 32 genuine later V4 processes")
    return {"family_count": 3, "owner_count": 6,
            "candidate_evidence_owner_count": 51,
            "total_distinct_historical_evidence_owner_count": 57,
            "process_count": 32, "families": results,
            "successful_build_families": ["cpp"],
            "failed_build_families": ["go", "fortran"],
            "qualified_candidate_count": 0,
            "performance": "NOT MEASURED", "holdout": "NOT OPENED"}


def verify_zig_restoration(*, verify_live_targets: bool = True) -> dict[str, Any]:
    require(type(verify_live_targets) is bool,
            "select an explicit typed live-target restoration verification boundary")
    raw, owner = read_owned(ROOT, RESTORATION_RELATIVE, RESTORATION_SHA256,
                            maximum=MAX_SOURCE_BYTES, exact_size=RESTORATION_BYTES)
    receipt = decode_document(raw, "actual V6 Zig restoration receipt")
    require(receipt.get("schema")
            == "rebar-phase2-verified-native-candidate-activation-v2-restoration-receipt"
            and receipt.get("status") == "PASS" and receipt.get("family") == "zig"
            and receipt.get("build_version") == "3"
            and receipt.get("candidate_import_root") == ROOT
            and receipt.get("promotion_mode") == "recoverable-canonical-promotion",
            "preserve the actual reportless-safe owner-only V6 Zig restoration")
    targets = receipt.get("restored_targets")
    require(type(targets) is dict and set(targets) == set(RESTORED_ZIG),
            "both exact restored Zig canonical targets are required")
    evidence: dict[str, Any] = {}
    for role, (relative, digest, size, mode) in RESTORED_ZIG.items():
        documented = targets[role]
        require(type(documented) is dict and documented.get("relative") == relative
                and documented.get("sha256") == digest
                and documented.get("size_bytes") == size
                and documented.get("mode") == mode
                and documented.get("restored_from_verified_backup") is True
                and all(documented.get(flag) is True for flag in PROMOTION_FLAGS),
                "retain the exact real Zig restoration bytes, mode, and actual evidence")
        if verify_live_targets:
            current_raw, current = read_owned(ROOT, relative, digest,
                                              maximum=MAX_BINARY_BYTES, exact_size=size)
            require(len(current_raw) == size and current["mode"] == mode
                    and current["device"] == documented.get("device")
                    and current["inode"] == documented.get("inode"),
                    "the original canonical V6-restored Zig bytes/inode were modified")
            evidence[role] = current
        else:
            evidence[role] = {key: documented[key] for key in OWNER_FIELDS}
    require(all(receipt.get(key) == value for key, value in (
        ("candidate_processes_started", 0), ("candidate_imports", 0),
        ("native_libraries_loaded", 0), ("network_requests", 0),
        ("hidden_cases_read", 0), ("benchmark_files_read", 0),
        ("clock_samples", 0), ("timing_trials_run", 0),
        ("candidate_correctness", "NOT MEASURED"),
        ("performance", "NOT MEASURED"), ("winner_selected", False),
    )), "the retained restoration receipt may not invent candidate or holdout effects")
    return {"receipt": owner, "status": "PASS", "family": "zig",
            "restored_targets": evidence,
            "live_targets_rechecked": verify_live_targets,
            "candidate_qualified": False, "performance": "NOT MEASURED"}


def _verify_legacy_v4_context(*, verify_live_restored_targets: bool = True) -> dict[str, Any]:
    require(type(verify_live_restored_targets) is bool,
            "select an explicit source-only live restoration boundary")
    require(sys.executable == PINNED_PYTHON
            and sys.version_info[:3] == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314",
            "use only the exact frozen stable CPython 3.14.6 interpreter")
    activation_contract_raw, activation_contract_owner = read_owned(
        ROOT, CONTRACT_RELATIVE, None, maximum=MAX_SOURCE_BYTES)
    contract = validate_contract(decode_document(
        activation_contract_raw, "six-family V4 activation contract", exact=False))
    _, activation_source = read_owned(ROOT, SOURCE_RELATIVE, None,
                                      maximum=MAX_SOURCE_BYTES)
    _, activation_protocol = read_owned(ROOT, PROTOCOL_RELATIVE, None,
                                        maximum=MAX_SOURCE_BYTES)
    support: dict[str, dict[str, Any]] = {}
    phase1 = None
    build_contract = None
    historical_graph = None
    for name, (relative, digest, size) in FROZEN_SUPPORT.items():
        raw, owner = read_owned(ROOT, relative, digest, maximum=MAX_SOURCE_BYTES,
                                exact_size=size)
        support[name] = owner
        if name == "phase1_manifest":
            phase1 = validate_phase1(raw)
        elif name == "v4_build_contract":
            build_contract = decode_document(raw, "pushed V4 source contract", exact=False)
        elif name == "historical_current_overview":
            historical_graph = raw
    require(phase1 is not None and type(build_contract) is dict
            and build_contract.get("schema") == BUILD_SCHEMA + "-source-freeze"
            and build_contract.get("version") == 4
            and build_contract.get("family_count") == 6
            and build_contract.get("qualified_candidate_count") == 0,
            "the exact independently published V4 source freeze is mandatory")
    by_family = {item.get("id"): item for item in build_contract.get("families", [])
                 if type(item) is dict}
    require(set(by_family) == set(FAMILIES),
            "require all six exact independently frozen matching families")
    owner_inodes: set[tuple[int, int]] = set()
    families: dict[str, Any] = {}
    for family, graph in SOURCE_OWNERS.items():
        documented = by_family[family]
        source_entries = documented.get("owners")
        require(type(source_entries) is list and len(source_entries) == len(graph),
                "the V4 build froze an incomplete semantic source closure")
        documented_owners = {item.get("path"): (item.get("sha256"), item.get("bytes"))
                             for item in source_entries if type(item) is dict}
        require(documented_owners == graph,
                "reject omitted C++ headers, Rust modules, Go manifests, or family bridges")
        actual_sources: dict[str, Any] = {}
        for relative, (digest, size) in graph.items():
            raw, owner = read_owned(ROOT, relative, digest,
                                    maximum=MAX_SOURCE_BYTES, exact_size=size)
            identity = (owner["device"], owner["inode"])
            require(identity not in owner_inodes,
                    "reject reused or hard-linked cross-family semantic owner inodes")
            owner_inodes.add(identity)
            if relative.endswith(".py"):
                validate_adapter(raw, family, relative)
            actual_sources[relative] = owner
        families[family] = {"language": FAMILIES[family]["language"],
                            "source_owner_count": len(graph),
                            "sources": actual_sources,
                            "promotion_target_count": len(FAMILIES[family]["targets"]),
                            "generated_header_promoted": False,
                            "candidate_correctness": "NOT MEASURED"}
    guards: dict[str, Any] = {}
    for relative, (digest, size) in ORIGINAL_GUARDS.items():
        _, owner = read_owned(ROOT, relative, digest,
                              maximum=MAX_SOURCE_BYTES, exact_size=size)
        guards[relative] = owner
    tools: dict[str, Any] = {}
    blockers: list[dict[str, str]] = []
    listed = build_contract.get("toolchains")
    require(type(listed) is list and len(listed) == 13,
            "all thirteen original V4 Python/toolchain pins are mandatory")
    for item in listed:
        require(type(item) is dict and type(item.get("id")) is str
                and type(item.get("bytes")) is int,
                "reject an incomplete actual frozen official toolchain")
        try:
            observed = read_absolute_tool(item["path"], item["sha256"], item["bytes"])
            require(bool(observed["mode"] & 0o111) == item["executable"],
                    "the pinned actual compiler executable permission changed")
            tools[item["id"]] = {**observed,
                                 "pinned_version": item.get("version")}
        except (ActivationError, OSError) as error:
            blockers.append({"toolchain": item["id"], "path": item.get("path", ""),
                             "error_type": type(error).__name__,
                             "message": str(error)})
    history = [verify_historical_record(name, spec)
               for name, spec in HISTORICAL_RECORDS.items()]
    require(type(historical_graph) is bytes,
            "the immutable complete 51-owner candidate evidence graph is mandatory")
    complete_history = verify_complete_candidate_history(historical_graph)
    v4_history = verify_published_v4_build_history(complete_history)
    process_ledger = {
        "v2_process_count": sum(
            HISTORICAL_RECORDS[key]["process_count"]
            for key in ("v2_c", "v2_rust", "v2_zig_failure")),
        "v3_zig_process_count": HISTORICAL_RECORDS["v3_zig"]["process_count"],
        "v4_process_count": v4_history["process_count"],
        "v2_and_v4_process_count": (
            sum(HISTORICAL_RECORDS[key]["process_count"]
                for key in ("v2_c", "v2_rust", "v2_zig_failure"))
            + v4_history["process_count"]),
        "all_historical_build_process_count": (
            sum(HISTORICAL_RECORDS[key]["process_count"]
                for key in ("v2_c", "v2_rust", "v2_zig_failure", "v3_zig"))
            + v4_history["process_count"]),
        "v4_processes_by_family": {
            family: item["process_count"]
            for family, item in v4_history["families"].items()
        },
        "unique_pid_scope": "WITHIN EACH ACTUAL BUILD REPORT ONLY",
    }
    require(process_ledger
            == _expected_legacy_historical_evidence()["historical_build_process_ledger"],
            "retain the separately labeled real V2, V3 Zig, V4, 71, and 86 process ledgers")
    restoration = verify_zig_restoration(
        verify_live_targets=verify_live_restored_targets)
    return {"schema": SCHEMA + "-read-only-frozen-context", "version": 4,
            "status": "BLOCKED" if blockers else "PASS",
            "activation_source": activation_source,
            "activation_protocol": activation_protocol,
            "activation_contract": activation_contract_owner,
            "activation_contract_schema": contract["schema"],
            "frozen_reference": phase1, "v4_build_source": support["v4_build_source"],
            "v4_build_protocol": support["v4_build_protocol"],
            "v4_build_contract": support["v4_build_contract"],
            "family_count": len(families), "source_owner_count": len(owner_inodes),
            "pairwise_shared_semantic_owners": 0, "families": families,
            "original_guard_count": len(guards), "original_guards": guards,
            "pinned_support": support, "pinned_toolchains": tools,
            "missing_or_changed_toolchains": blockers,
            "preserved_historical_records": history,
            "historical_candidate_evidence": complete_history,
            "historical_v4_build_evidence": v4_history,
            "total_distinct_historical_evidence_owner_count": 57,
            "historical_build_process_ledger": process_ledger,
            "preserved_v2_process_count": 39,
            "preserved_v3_zig_process_count": 15,
            "preserved_v4_process_count": 32,
            "preserved_v2_and_v4_process_count": 71,
            "preserved_all_build_process_count": 86,
            "historical_v4_source_build_count": 3,
            "source_builds_started_by_activation_freeze": 0,
            "v6_zig_restoration": restoration,
            "actual_v4_source_builds": "NOT RUN",
            "actual_v3_activations": "NOT RUN",
            "qualified_candidate_count": 0,
            "read_only": True, **zero_effects()}



def verify_frozen_context(
    *, verify_live_restored_targets: bool = True
) -> dict[str, Any]:
    """Read-only authentication of every actual frozen source and evidence owner."""
    require(type(verify_live_restored_targets) is bool,
            "select an explicit read-only live-restoration boundary")
    previous = _verify_legacy_v4_context(
        verify_live_restored_targets=verify_live_restored_targets,
    )
    module = load_frozen_v6_build_kernel()
    inherited = call_frozen_kernel(module, module.verify_context)
    require(type(inherited) is dict
            and inherited.get("schema") == BUILD_V6_SCHEMA + "-read-only-context"
            and inherited.get("version") == 6
            and inherited.get("family_count") == 6
            and inherited.get("source_owner_count") == 25
            and inherited.get("pairwise_shared_source_count") == 0
            and inherited.get("qualified_candidate_count") == 0,
            "require the whole independently authenticated six-family V6 freeze")
    reference = inherited.get("frozen_correctness")
    require(type(reference) is dict
            and reference.get("status") == "PASS"
            and reference.get("suite_count") == 13
            and reference.get("case_execution_count") == 31237
            and reference.get("candidate_qualified_count") == 0,
            "preserve every original P0 reference obligation without qualification")
    parser = call_frozen_kernel(module, module.load_frozen_v4)
    require(parser.SCHEMA == BUILD_SCHEMA
            and parser.SOURCE_OWNERS == SOURCE_OWNERS,
            "use only the exact authenticated original first-party V4 ELF parser")
    v6_history = verify_published_v6_build_history(
        module, parser, inherited,
    )
    required = expected_historical_evidence()
    require(v6_history["total_distinct_historical_evidence_owner_count"]
            == required["total_distinct_evidence_owner_count"]
            and v6_history["process_count"]
            == required["historical_build_process_ledger"]["v6_process_count"],
            "never merge, silently drop, or guess real evidence or process owners")
    result = dict(previous)
    result.update({
        "status": (
            "PASS"
            if previous["status"] == "PASS"
            and inherited["status"] == "PASS"
            else "BLOCKED"
        ),
        "v6_build_source": previous["pinned_support"]["v6_build_source"],
        "v6_build_protocol": previous["pinned_support"]["v6_build_protocol"],
        "v6_build_contract": previous["pinned_support"]["v6_build_contract"],
        "v6_build_frozen_context": {
            "schema": inherited["schema"],
            "version": inherited["version"],
            "status": inherited["status"],
            "family_count": inherited["family_count"],
            "source_owner_count": inherited["source_owner_count"],
            "evidence_accounting": inherited["evidence_accounting"],
            "qualified_candidate_count": (
                inherited["qualified_candidate_count"]
            ),
        },
        "historical_v5_build_evidence": inherited["preserved_v5_history"],
        "historical_v6_build_evidence": v6_history,
        "total_distinct_historical_evidence_owner_count": (
            required["total_distinct_evidence_owner_count"]
        ),
        "historical_build_process_ledger": (
            required["historical_build_process_ledger"]
        ),
        "preserved_all_build_process_count": (
            required["historical_build_process_ledger"][
                "all_historical_versions_actual_compiler_process_count"
            ]
        ),
        "source_builds_started_by_activation_freeze": 0,
        "actual_v6_source_builds": "NOT RUN",
        "actual_v4_activations": "NOT RUN",
        "qualified_candidate_count": 0,
        "read_only": True,
        **zero_effects(),
    })
    return result



def validate_adapter(raw: bytes, family: str, relative: str) -> None:
    require(type(raw) is bytes, "require the owned Python adapter bytes")
    try:
        document = ast.parse(raw.decode("utf-8"), filename=relative, mode="exec")
    except (SyntaxError, UnicodeError) as error:
        raise ActivationError("the independently owned Python adapter is invalid") from error
    own = FAMILIES[family]["targets"]
    expected = {"c": "_vm_native", "rust": "_rust_bridge", "zig": "_zig_bridge",
                "cpp": "_cpp_bridge", "go": "_go_bridge",
                "fortran": "_fortran_bridge"}[family]
    seen, loaders = False, 0
    for node in ast.walk(document):
        if isinstance(node, ast.Import):
            for alias in node.names:
                require(alias.name.split(".", 1)[0] not in FORBIDDEN_MODULES,
                        "reject direct production delegation to a standard regex")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            require(module.split(".", 1)[0] not in FORBIDDEN_MODULES,
                    "reject an indirectly imported external regex engine")
            if module == "candidates":
                for alias in node.names:
                    require(alias.name == expected,
                            "the adapter imports another candidate's matching engine")
                    seen = True
            elif module.startswith("candidates."):
                raise ActivationError("reject disguised cross-family native delegation")
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                require(fn.id not in {"__import__", "eval", "exec"},
                        "reject a hidden computed candidate or regex importer")
            elif isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name):
                pair = (fn.value.id, fn.attr)
                require(pair not in {("importlib", "import_module"),
                                    ("os", "system"), ("os", "popen"),
                                    ("subprocess", "run"), ("subprocess", "Popen")},
                        "reject matcher dispatch through a process or dynamic importer")
                if pair == ("ctypes", "CDLL"):
                    loaders += 1
                    require(family == "zig", "reject an unowned native dynamic loader")
    require(bool(own) and seen and loaders == (1 if family == "zig" else 0),
            "require exactly the owned adapter/native-engine import")


def synchronize_directory(root: str, relative: str = "") -> dict[str, Any]:
    descriptor = open_root(root, private=True)
    opened = [descriptor]
    try:
        if relative:
            checked_relative(relative)
            for component in relative.split("/"):
                descriptor = os.open(component, directory_flags(), dir_fd=descriptor)
                opened.append(descriptor)
        first = os.fstat(descriptor)
        require(stat.S_ISDIR(first.st_mode), "synchronize one actual owned directory")
        os.fsync(descriptor)
        last = os.fstat(descriptor)
        require((first.st_dev, first.st_ino) == (last.st_dev, last.st_ino),
                "reject an evidence directory replaced during durable synchronization")
        return {"completed": True, "device": last.st_dev, "inode": last.st_ino}
    finally:
        for item in reversed(opened):
            os.close(item)


def write_fresh(root: str, relative: str, content: bytes) -> dict[str, Any]:
    checked_relative(relative)
    require(type(content) is bytes and 0 < len(content) <= MAX_BINARY_BYTES,
            "exclusively publish only complete bounded owned recovery evidence")
    opened: list[int] = []
    descriptor: int | None = None
    try:
        parent = open_root(root, private=True)
        opened.append(parent)
        parts = relative.split("/")
        for component in parts[:-1]:
            try:
                os.mkdir(component, 0o700, dir_fd=parent)
            except FileExistsError:
                pass
            parent = os.open(component, directory_flags(), dir_fd=parent)
            opened.append(parent)
            owner = os.fstat(parent)
            require(stat.S_ISDIR(owner.st_mode)
                    and stat.S_IMODE(owner.st_mode) == 0o700
                    and owner.st_uid == os.geteuid(),
                    "recovery evidence directories must be genuinely owner-only")
        descriptor = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL
                             | getattr(os, "O_CLOEXEC", 0)
                             | getattr(os, "O_NOFOLLOW", 0),
                             0o600, dir_fd=parent)
        first = os.fstat(descriptor)
        require(stat.S_ISREG(first.st_mode)
                and stat.S_IMODE(first.st_mode) == 0o600
                and first.st_uid == os.geteuid(),
                "publish only a genuine owner-only, exclusive regular evidence file")
        written, calls = 0, 0
        while written < len(content):
            amount = os.write(descriptor, content[written:])
            require(type(amount) is int and amount > 0,
                    "a durable recovery evidence write was truncated")
            written += amount
            calls += 1
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((first.st_dev, first.st_ino) == (after.st_dev, after.st_ino)
                and after.st_size == len(content),
                "reject changed, partial, or redirected owner-only evidence")
        os.close(descriptor)
        descriptor = None
        _, owner = read_owned(root, relative, sha256(content), maximum=MAX_BINARY_BYTES,
                              exact_size=len(content), private=True)
        require((owner["device"], owner["inode"]) == (after.st_dev, after.st_ino)
                and owner["mode"] == 0o600,
                "reject an evidence inode replaced after actual file fsync")
        return {**owner, "exclusive_creation": True,
                "same_inode_readback_verified": True,
                "file_fsync_completed": True, "write_calls": calls}
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for item in reversed(opened):
            os.close(item)


def canonical_candidate_directory() -> tuple[int, int]:
    root = open_root(ROOT, private=False)
    try:
        candidates = os.open("candidates", directory_flags(), dir_fd=root)
        owner = os.fstat(candidates)
        require(stat.S_ISDIR(owner.st_mode) and owner.st_uid == os.geteuid(),
                "activate only inside the real owner-controlled candidates directory")
        return root, candidates
    except BaseException:
        os.close(root)
        raise


def current_canonical(relative: str) -> tuple[bytes, dict[str, Any]] | None:
    checked_relative(relative)
    require(relative.startswith("candidates/") and len(relative.split("/")) == 2,
            "inspect only one exact approved canonical native filename")
    root, descriptor = canonical_candidate_directory()
    try:
        filename = relative.split("/", 1)[1]
        try:
            owner = os.stat(filename, dir_fd=descriptor, follow_symlinks=False)
        except FileNotFoundError:
            return None
        require(stat.S_ISREG(owner.st_mode),
                "refuse to activate over a directory, symlink, or unrelated user file")
        return read_owned(ROOT, relative, None, maximum=MAX_BINARY_BYTES)
    finally:
        os.close(descriptor)
        os.close(root)


def validate_canonical_snapshot(relative: str, expected: dict[str, Any] | None) -> None:
    observed = current_canonical(relative)
    if expected is None:
        require(observed is None, "an originally absent user native target appeared")
    else:
        require(observed is not None and same_owner(observed[1], expected),
                "a canonical user binary changed after recovery preparation")


def validate_promotion_intent(document: Any, *, family: str, root: str,
                              role: str, journal_digest: str,
                              current: dict[str, Any]) -> dict[str, Any]:
    family = checked_family(family)
    checked_private_root(root, family, build=False)
    require(role in FAMILIES[family]["targets"],
            "the generated Go header is never an activation target")
    require(type(document) is dict and document.get("schema") == INTENT_SCHEMA
            and document.get("status") == "PREPARED"
            and document.get("promotion_mode") == "recoverable-canonical-promotion"
            and document.get("family") == family
            and document.get("activation_root") == root
            and document.get("candidate_import_root") == ROOT
            and document.get("recovery_journal_sha256") == checked_digest(journal_digest, "journal")
            and document.get("role") == role,
            "an exact durable pre-promotion intention is mandatory")
    target = document.get("target")
    filename = FAMILIES[family]["targets"][role]
    require(type(target) is dict and target.get("relative") == "candidates/" + filename
            and target.get("path") == ROOT + "/candidates/" + filename
            and same_owner(current, target),
            "bind recovery to exactly the genuine promoted staged inode")
    for key, value in zero_effects().items():
        require(type(document.get(key)) is type(value) and document.get(key) == value,
                "a promotion intention may not claim candidate or benchmark effects")
    return target


def stage_and_replace(relative: str, content: bytes, *,
                      expected_current: dict[str, Any] | None,
                      final_mode: int, intention: dict[str, Any] | None = None) -> dict[str, Any]:
    checked_relative(relative)
    require(relative.startswith("candidates/") and len(relative.split("/")) == 2
            and type(content) is bytes and 0 < len(content) <= MAX_BINARY_BYTES
            and type(final_mode) is int and 0 <= final_mode <= 0o777,
            "stage exactly one owner-authenticated native target and original mode")
    if intention is not None:
        family = checked_family(intention.get("family"))
        role = intention.get("role")
        require(role in FAMILIES[family]["targets"]
                and relative == "candidates/" + FAMILIES[family]["targets"][role],
                "reject a foreign, generated-header, or cross-family promotion target")
        checked_private_root(intention.get("activation_root"), family, build=False)
        checked_digest(intention.get("recovery_journal_sha256"), "prepared journal")
    root, parent = canonical_candidate_directory()
    descriptor: int | None = None
    identity: tuple[int, int] | None = None
    replaced = False
    published: dict[str, Any] | None = None
    filename = relative.split("/", 1)[1]
    temporary = ".rebar-v3-owned-" + os.urandom(18).hex() + "-" + filename
    require(len(temporary) <= 240, "bound an exact adjacent exclusive stage filename")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                             | getattr(os, "O_CLOEXEC", 0)
                             | getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=parent)
        original = os.fstat(descriptor)
        require(stat.S_ISREG(original.st_mode)
                and stat.S_IMODE(original.st_mode) == 0o600
                and original.st_uid == os.geteuid(),
                "stage only an exclusive owner-only adjacent canonical file")
        identity = (original.st_dev, original.st_ino)
        offset = 0
        while offset < len(content):
            amount = os.write(descriptor, content[offset:])
            require(type(amount) is int and amount > 0,
                    "never stage truncated source-built native bytes")
            offset += amount
        if final_mode != 0o600:
            os.fchmod(descriptor, final_mode)
        os.fsync(descriptor)
        complete = os.fstat(descriptor)
        require((complete.st_dev, complete.st_ino) == identity
                and complete.st_size == len(content)
                and stat.S_IMODE(complete.st_mode) == final_mode,
                "preserve the exact fsynced stage inode and original permissions")
        os.close(descriptor)
        descriptor = None
        _, staged = read_owned(ROOT, "candidates/" + temporary, sha256(content),
                               maximum=MAX_BINARY_BYTES, exact_size=len(content))
        require((staged["device"], staged["inode"]) == identity,
                "the synchronized adjacent staged inode changed")
        validate_canonical_snapshot(relative, expected_current)
        if intention is not None:
            target = {key: staged[key] for key in OWNER_FIELDS}
            target["relative"] = relative
            target["path"] = ROOT + "/" + relative
            document = {"schema": INTENT_SCHEMA, "status": "PREPARED",
                        "promotion_mode": "recoverable-canonical-promotion",
                        "family": intention["family"],
                        "activation_root": intention["activation_root"],
                        "candidate_import_root": ROOT,
                        "recovery_journal_sha256": intention["recovery_journal_sha256"],
                        "role": intention["role"], "target": target,
                        **zero_effects()}
            published = write_fresh(intention["activation_root"],
                                    "promotion-intent-" + intention["role"] + ".json",
                                    canonical(document))
            synced = synchronize_directory(intention["activation_root"])
            published["directory_fsync_completed"] = synced["completed"]
            require_durable_owner(published,
                                  relative="promotion-intent-" + intention["role"] + ".json",
                                  root=intention["activation_root"], directory_sync=True)
            validate_canonical_snapshot(relative, expected_current)
        os.replace(temporary, filename, src_dir_fd=parent, dst_dir_fd=parent)
        replaced = True
        os.fsync(parent)
        _, promoted = read_owned(ROOT, relative, sha256(content),
                                 maximum=MAX_BINARY_BYTES, exact_size=len(content))
        require((promoted["device"], promoted["inode"]) == identity
                and promoted["mode"] == final_mode,
                "the individually atomic canonical native inode changed")
        result = {**promoted, "atomic_replace_completed": True,
                  "adjacent_exclusive_stage_verified": True,
                  "candidate_directory_fsync_completed": True}
        if published is not None:
            result["promotion_intent"] = published
        return result
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if identity is not None and not replaced:
            try:
                leftover = os.stat(temporary, dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError:
                leftover = None
            if leftover is not None:
                require(stat.S_ISREG(leftover.st_mode)
                        and (leftover.st_dev, leftover.st_ino) == identity,
                        "never remove an unrelated or substituted user staging file")
                os.unlink(temporary, dir_fd=parent)
                os.fsync(parent)
        os.close(parent)
        os.close(root)


def phase_native_outputs(
    arguments: dict[str, Any],
    verified: dict[str, Any],
    *,
    report_phases: list[dict[str, Any]],
) -> dict[str, Any]:
    family = checked_family(arguments["family"])
    version = arguments.get("build_version", 4)
    require(type(version) is int and version in {4, 6},
            "bind actual phase outputs to exactly one frozen build version")
    root = checked_private_root(
        arguments["build_root"], family, build=True,
        build_version=version,
    )
    require(type(report_phases) is list and len(report_phases) == 2
            and [phase.get("name") for phase in report_phases]
            == ["reference-a", "reference-b"],
            "bind every actual phase output to the authenticated source report")
    results: dict[str, Any] = {}
    for role, filename in expected_roles(family).items():
        pair: list[dict[str, Any]] = []
        bytes_seen: list[bytes] = []
        for index, phase in enumerate(("reference-a", "reference-b")):
            relative = phase + "/native/" + filename
            raw, owner = read_owned(
                root, relative, arguments["native_hashes"][role],
                maximum=(
                    MAX_SOURCE_BYTES if role == "generated_header"
                    else MAX_BINARY_BYTES
                ),
                exact_size=arguments["native_sizes"][role],
                private=True,
            )
            phase_outputs = report_phases[index].get("native_outputs")
            require(type(phase_outputs) is dict and role in phase_outputs,
                    "bind both real output inodes, never only the first phase")
            reported = phase_outputs[role]
            require(type(reported) is dict
                    and owner["device"] == reported.get("device")
                    and owner["inode"] == reported.get("inode")
                    and owner["sha256"] == reported.get("sha256")
                    and owner["size_bytes"] == reported.get("size_bytes"),
                    "reject substitution of either real built native output inode")
            require(role in verified,
                    "require one complete authenticated native role proof")
            if role == "generated_header":
                require(audit_go_header(raw) == verified[role]["audit"],
                        "the genuine nine-export compiler-generated header changed")
            pair.append(owner)
            bytes_seen.append(raw)
        require(bytes_seen[0] == bytes_seen[1]
                and (pair[0]["device"], pair[0]["inode"])
                != (pair[1]["device"], pair[1]["inode"]),
                "require identical real native bytes and two distinct phase inodes")
        results[role] = {
            "bytes": bytes_seen[0],
            "phases": pair,
            "sha256": arguments["native_hashes"][role],
            "size_bytes": arguments["native_sizes"][role],
        }
    return results


def authenticate_prerequisites(arguments: dict[str, Any]) -> dict[str, Any]:
    context = verify_frozen_context(verify_live_restored_targets=False)
    require(context["status"] == "PASS"
            and not context["missing_or_changed_toolchains"],
            "every original owner, actual history, official tool, and guard must pass")
    require(context["activation_source"]["sha256"]
            == arguments["activation_source_sha256"]
            and context["activation_protocol"]["sha256"]
            == arguments["activation_protocol_sha256"]
            and context["activation_contract"]["sha256"]
            == arguments["activation_contract_sha256"],
            "caller-pin the exact separately published V4 activation freeze")
    family = checked_family(arguments["family"])
    label = checked_label(arguments["build_label"])
    selected = select_source_build(
        arguments["build_source_sha256"],
        arguments["build_protocol_sha256"],
        arguments["build_contract_sha256"],
    )
    version = selected["version"]
    require(arguments.get("build_version", version) == version,
            "reject mixed original-V4 and corrected-V6 source-build provenance")
    root = checked_private_root(
        arguments["build_root"], family, build=True,
        build_version=version,
    )
    pins = parse_owner_pins(family, arguments["owned_source_sha256"])
    base = (
        EVIDENCE_RELATIVE
        + "/native-source-build-v" + str(version) + "-"
        + family + "-" + label
    )
    archive, archive_owner = read_owned(
        ROOT, base + ".json.gz", arguments["build_report_sha256"],
        maximum=MAX_ARCHIVE_BYTES,
    )
    receipt_raw, receipt_owner = read_owned(
        ROOT, base + "-publication-receipt.json",
        arguments["build_receipt_sha256"],
        maximum=MAX_SOURCE_BYTES,
    )
    report = decode_document(
        bounded_gzip(archive),
        "actual passing V" + str(version) + " source-build report",
    )
    receipt = decode_document(
        receipt_raw,
        "actual independently durable V" + str(version) + " source receipt",
    )
    if version == 4:
        require(
            family == "cpp"
            or family in {"c", "rust", "zig", "go", "fortran"},
            "select one exact independently owned original V4 family",
        )
        verified = validate_build_report(
            report, receipt, archive, arguments, pins,
        )
    else:
        module = load_frozen_v6_build_kernel()
        inherited = call_frozen_kernel(module, module.verify_context)
        parser = call_frozen_kernel(module, module.load_frozen_v4)
        expected = {
            role: {
                "sha256": arguments["native_hashes"][role],
                "size_bytes": arguments["native_sizes"][role],
            }
            for role in expected_roles(family)
        }
        actual = validate_v6_build_documents(
            module, parser, report, receipt, archive,
            archive_owner, receipt_owner,
            family=family, label=label, root=root,
            expected_status="PASS",
            expected_process_count=module.EXPECTED_BUILD_POLICY[
                "v6_future_process_count_by_family"
            ][family],
            expected_completed_phase_count=2,
            context=inherited,
            exact_outputs=expected,
        )
        require(actual["build_status"] == "PASS",
                "no failed or incomplete V6 family is eligible for activation")
        verified = actual["verified"]
    real = phase_native_outputs(
        {**arguments, "build_version": version},
        verified,
        report_phases=report["build_phases"],
    )
    return {
        "family": family,
        "label": label,
        "build_version": version,
        "context": context,
        "pins": pins,
        "build_report": archive_owner,
        "build_receipt": receipt_owner,
        "verified": verified,
        "actual_outputs": real,
    }


def build_provenance(
    arguments: dict[str, Any],
    prerequisite: dict[str, Any],
) -> dict[str, Any]:
    selected = select_source_build(
        arguments["build_source_sha256"],
        arguments["build_protocol_sha256"],
        arguments["build_contract_sha256"],
    )
    version = selected["version"]
    require(prerequisite.get("build_version") == version,
            "bind the recovery journal to one actually validated build version")
    return {
        "build_version": version,
        "schema": selected["schema"],
        "family": arguments["family"],
        "label": arguments["build_label"],
        "source_sha256": selected["source_sha256"],
        "protocol_sha256": selected["protocol_sha256"],
        "contract_sha256": selected["contract_sha256"],
        "archive_relative": prerequisite["build_report"]["relative"],
        "archive_sha256": prerequisite["build_report"]["sha256"],
        "receipt_relative": prerequisite["build_receipt"]["relative"],
        "receipt_sha256": prerequisite["build_receipt"]["sha256"],
        "build_root": arguments["build_root"],
        "independent_fresh_phase_count": 2,
        "actual_versioned_symbol_streams_verified": True,
        "preserved_v2_history_process_count": 39,
        "generated_go_header_verified": arguments["family"] == "go",
        "generated_go_header_promoted": False,
    }


def prepare_recovery_journal(root: str, arguments: dict[str, Any],
                             prerequisite: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    family = checked_family(arguments["family"])
    entries: dict[str, Any] = {}
    for role, filename in FAMILIES[family]["targets"].items():
        relative = "candidates/" + filename
        previous = current_canonical(relative)
        if previous is None:
            original, backup = None, None
        else:
            content, original = previous
            backup = write_fresh(root, "backups/" + relative, content)
            synced = synchronize_directory(root, "backups/candidates")
            backup["directory_fsync_completed"] = synced["completed"]
            require_durable_owner(backup, relative="backups/" + relative,
                                  root=root, directory_sync=True)
        entries[role] = {"role": role, "target_relative": relative,
                         "target_path": ROOT + "/" + relative,
                         "originally_present": previous is not None,
                         "original_owner": original, "backup": backup,
                         "promoted_sha256": arguments["native_hashes"][role],
                         "promoted_size_bytes": arguments["native_sizes"][role]}
    journal = {"schema": JOURNAL_SCHEMA, "status": "PREPARED",
               "promotion_mode": "recoverable-canonical-promotion",
               "family": family, "activation_root": root,
               "candidate_import_root": ROOT,
               "activation_source_sha256": arguments["activation_source_sha256"],
               "activation_protocol_sha256": arguments["activation_protocol_sha256"],
               "activation_contract_sha256": arguments["activation_contract_sha256"],
               "source_build": build_provenance(arguments, prerequisite),
               "owned_source_sha256": prerequisite["pins"],
               "native_hashes": arguments["native_hashes"],
               "native_sizes": arguments["native_sizes"],
               "backup_entries": entries, **zero_effects()}
    record = write_fresh(root, JOURNAL_NAME, canonical(journal))
    synchronized = synchronize_directory(root)
    record["directory_fsync_completed"] = synchronized["completed"]
    require_durable_owner(record, relative=JOURNAL_NAME, root=root,
                          directory_sync=True)
    return journal, record


def validate_build_provenance(
    value: Any, family: str
) -> dict[str, Any]:
    family = checked_family(family)
    require(type(value) is dict,
            "bind recovery to exactly one complete genuine source-build proof")
    selected = select_source_build(
        value.get("source_sha256"),
        value.get("protocol_sha256"),
        value.get("contract_sha256"),
    )
    version = selected["version"]
    require(type(value.get("build_version")) is int
            and value["build_version"] == version
            and value.get("schema") == selected["schema"]
            and value.get("family") == family
            and value.get("independent_fresh_phase_count") == 2
            and value.get("actual_versioned_symbol_streams_verified") is True
            and value.get("preserved_v2_history_process_count") == 39
            and value.get("generated_go_header_verified") is (family == "go")
            and value.get("generated_go_header_promoted") is False,
            "reject mixed-version, incomplete, or cross-family recovery provenance")
    label = checked_label(value.get("label"))
    checked_private_root(
        value.get("build_root"), family, build=True,
        build_version=version,
    )
    prefix = (
        EVIDENCE_RELATIVE + "/native-source-build-v"
        + str(version) + "-" + family + "-" + label
    )
    require(value.get("archive_relative") == prefix + ".json.gz"
            and value.get("receipt_relative")
            == prefix + "-publication-receipt.json",
            "reject a cross-version, fallback, or fabricated source-build archive")
    checked_digest(value.get("archive_sha256"),
                   "passing source-build archive")
    checked_digest(value.get("receipt_sha256"),
                   "passing source-build receipt")
    return value


def validate_recovery_journal(journal: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    family = checked_family(arguments["family"])
    root = checked_private_root(arguments["activation_root"], family, build=False)
    require(type(journal) is dict and journal.get("schema") == JOURNAL_SCHEMA
            and journal.get("status") == "PREPARED"
            and journal.get("promotion_mode") == "recoverable-canonical-promotion"
            and journal.get("family") == family
            and journal.get("activation_root") == root
            and journal.get("candidate_import_root") == ROOT
            and journal.get("activation_source_sha256")
            == arguments["activation_source_sha256"]
            and journal.get("activation_protocol_sha256")
            == arguments["activation_protocol_sha256"]
            and journal.get("activation_contract_sha256")
            == arguments["activation_contract_sha256"],
            "authenticate the exact independently pinned owner-only recovery journal")
    if "recovery_journal_sha256" in arguments:
        require(sha256(canonical(journal)) == arguments["recovery_journal_sha256"],
                "the caller-pinned prepared recovery journal changed")
    for key, value in zero_effects().items():
        require(type(journal.get(key)) is type(value) and journal.get(key) == value,
                "a recovery journal may not invent candidate or holdout effects")
    provenance = validate_build_provenance(journal.get("source_build"), family)
    pins = journal.get("owned_source_sha256")
    require(type(pins) is dict and set(pins) == set(SOURCE_OWNERS[family])
            and all(digest == SOURCE_OWNERS[family][relative][0]
                    for relative, digest in pins.items()),
            "authenticate every exact frozen semantic owner during reportless recovery")
    hashes, sizes = journal.get("native_hashes"), journal.get("native_sizes")
    require(type(hashes) is dict and type(sizes) is dict
            and set(hashes) == set(sizes) == set(expected_roles(family)),
            "preserve every owned native role and the actual generated Go header")
    for role in hashes:
        checked_digest(hashes[role], role)
        checked_positive_size(sizes[role], role)
    entries = journal.get("backup_entries")
    require(type(entries) is dict and set(entries) == set(FAMILIES[family]["targets"]),
            "the generated Go header must never appear as a promotion recovery target")
    for role, filename in FAMILIES[family]["targets"].items():
        entry = entries[role]
        relative = "candidates/" + filename
        require(type(entry) is dict and entry.get("role") == role
                and entry.get("target_relative") == relative
                and entry.get("target_path") == ROOT + "/" + relative
                and type(entry.get("originally_present")) is bool
                and entry.get("promoted_sha256") == hashes[role]
                and entry.get("promoted_size_bytes") == sizes[role],
                "reject a forged, broad, foreign, or unowned canonical recovery target")
        original, backup = entry.get("original_owner"), entry.get("backup")
        if entry["originally_present"]:
            require(type(original) is dict and original.get("relative") == relative
                    and original.get("path") == ROOT + "/" + relative,
                    "preserve the exact original user-owned canonical path")
            checked_digest(original.get("sha256"), relative)
            checked_positive_size(original.get("size_bytes"), relative)
            require(type(original.get("device")) is int
                    and type(original.get("inode")) is int and original["inode"] > 0
                    and type(original.get("mode")) is int
                    and 0 <= original["mode"] <= 0o777,
                    "preserve all seven exact typed original permission and inode fields")
            require_durable_owner(backup, relative="backups/" + relative,
                                  root=root, directory_sync=True)
            require(backup["sha256"] == original["sha256"]
                    and backup["size_bytes"] == original["size_bytes"],
                    "the complete actual original backup differs from the user target")
        else:
            require(original is None and backup is None,
                    "never invent an originally absent native file or nonexistent backup")
    return {"journal": journal, "source_build": provenance,
            "family": family, "activation_root": root,
            "backup_entries": entries, "native_hashes": hashes, "native_sizes": sizes}


def classify_recovery_state(entry: Any, current: Any) -> str:
    require(type(entry) is dict and type(entry.get("originally_present")) is bool,
            "classify only an honestly recorded original canonical native owner")
    digest = checked_digest(entry.get("promoted_sha256"), "promoted role")
    size = checked_positive_size(entry.get("promoted_size_bytes"), "promoted role")
    if current is None:
        require(entry["originally_present"] is False,
                "an originally present user native file disappeared")
        return "originally-absent"
    require(type(current) is dict and type(current.get("size_bytes")) is int
            and type(current.get("mode")) is int,
            "reject a malformed current canonical native owner")
    if entry["originally_present"] and same_owner(current, entry.get("original_owner")):
        return "already-original"
    if current.get("sha256") == digest and current["size_bytes"] == size:
        return "source-verified-promoted"
    raise ActivationError("refuse to overwrite, restore, or delete a user-modified native file")


def authenticate_intentions(root: str, journal: dict[str, Any],
                            journal_digest: str) -> dict[str, Any]:
    family = checked_family(journal.get("family"))
    checked_private_root(root, family, build=False)
    found: dict[str, Any] = {}
    for role, filename in FAMILIES[family]["targets"].items():
        current = current_canonical("candidates/" + filename)
        entry = journal["backup_entries"][role]
        state = classify_recovery_state(entry, current[1] if current else None)
        if state != "source-verified-promoted":
            continue
        require(current is not None, "an actually promoted native owner disappeared")
        name = "promotion-intent-" + role + ".json"
        raw, owner = read_owned(root, name, None, maximum=MAX_SOURCE_BYTES,
                                private=True)
        require(owner["mode"] == 0o600,
                "the real pre-replace promotion intention must remain owner-only")
        document = decode_document(raw, "actual durable pre-replace intention")
        target = validate_promotion_intent(document, family=family, root=root,
                                           role=role, journal_digest=journal_digest,
                                           current=current[1])
        found[role] = {"intent": owner, "target": target}
    return found


def reconstructed_build_arguments(
    arguments: dict[str, Any],
    journal: dict[str, Any],
) -> dict[str, Any]:
    proof = validate_build_provenance(
        journal.get("source_build"), arguments["family"],
    )
    return {
        "mode": "activate",
        "family": arguments["family"],
        "build_version": proof["build_version"],
        "build_label": proof["label"],
        "build_root": proof["build_root"],
        "activation_source_sha256": arguments["activation_source_sha256"],
        "activation_protocol_sha256": (
            arguments["activation_protocol_sha256"]
        ),
        "activation_contract_sha256": (
            arguments["activation_contract_sha256"]
        ),
        "build_source_sha256": proof["source_sha256"],
        "build_protocol_sha256": proof["protocol_sha256"],
        "build_contract_sha256": proof["contract_sha256"],
        "build_report_sha256": proof["archive_sha256"],
        "build_receipt_sha256": proof["receipt_sha256"],
        "owned_source_sha256": [
            path + "=" + digest
            for path, digest in journal["owned_source_sha256"].items()
        ],
        "native_hashes": journal["native_hashes"],
        "native_sizes": journal["native_sizes"],
    }


def restore_journal_targets(root: str, journal: dict[str, Any],
                            journal_digest: str) -> dict[str, Any]:
    family = checked_family(journal.get("family"))
    authenticate_intentions(root, journal, journal_digest)
    restored: dict[str, Any] = {}
    for role in reversed(tuple(FAMILIES[family]["targets"])):
        filename = FAMILIES[family]["targets"][role]
        relative = "candidates/" + filename
        entry = journal["backup_entries"][role]
        current = current_canonical(relative)
        state = classify_recovery_state(entry, current[1] if current else None)
        if state in {"already-original", "originally-absent"}:
            restored[role] = {"status": state, "target_relative": relative,
                              "changed": False}
            continue
        require(current is not None,
                "an authenticated promoted canonical target disappeared during recovery")
        if entry["originally_present"]:
            original = entry["original_owner"]
            backup = entry["backup"]
            raw, actual = read_owned(root, "backups/" + relative,
                                     original["sha256"], maximum=MAX_BINARY_BYTES,
                                     exact_size=original["size_bytes"], private=True)
            require(same_owner(actual, backup),
                    "reject a modified or replaced actual original recovery backup")
            owner = stage_and_replace(relative, raw,
                                      expected_current=current[1],
                                      final_mode=original["mode"])
            restored[role] = {**owner, "restored_from_verified_backup": True}
        else:
            name = relative.split("/", 1)[1]
            root_fd, directory = canonical_candidate_directory()
            try:
                present = os.stat(name, dir_fd=directory, follow_symlinks=False)
                require((present.st_dev, present.st_ino)
                        == (current[1]["device"], current[1]["inode"]),
                        "never remove a replaced or unrelated canonical user file")
                os.unlink(name, dir_fd=directory)
                os.fsync(directory)
                restored[role] = {"status": "restored-originally-absent",
                                  "target_relative": relative,
                                  "removed_only_authenticated_promoted_inode": True}
            finally:
                os.close(directory)
                os.close(root_fd)
    return restored


def activate(arguments: dict[str, Any]) -> dict[str, Any]:
    prerequisite = authenticate_prerequisites(arguments)
    family = checked_family(arguments["family"])
    root = tempfile.mkdtemp(prefix=PRIVATE_PREFIX + family + "-", dir="/tmp")
    checked_private_root(root, family, build=False)
    owner = os.lstat(root)
    require(stat.S_ISDIR(owner.st_mode) and owner.st_uid == os.geteuid()
            and stat.S_IMODE(owner.st_mode) == 0o700,
            "create exactly one fresh same-owner mode-0700 recovery root")
    journal, journal_owner = prepare_recovery_journal(root, arguments, prerequisite)
    installed: dict[str, Any] = {}
    try:
        for role, filename in FAMILIES[family]["targets"].items():
            entry = journal["backup_entries"][role]
            content = prerequisite["actual_outputs"][role]["bytes"]
            original = entry["original_owner"]
            mode = original["mode"] if original is not None else 0o755
            installed[role] = stage_and_replace(
                "candidates/" + filename, content,
                expected_current=original, final_mode=mode,
                intention={"family": family, "activation_root": root,
                           "role": role,
                           "recovery_journal_sha256": journal_owner["sha256"]})
        report = {"schema": SCHEMA, "status": "PASS",
                  "promotion_mode": "recoverable-canonical-promotion",
                  "group_atomic": False, "family": family,
                  "activation_root": root, "candidate_import_root": ROOT,
                  "activation_source_sha256": arguments["activation_source_sha256"],
                  "activation_protocol_sha256": arguments["activation_protocol_sha256"],
                  "activation_contract_sha256": arguments["activation_contract_sha256"],
                  "recovery_journal": journal_owner,
                  "recovery_journal_sha256": journal_owner["sha256"],
                  "source_build": build_provenance(arguments, prerequisite),
                  "owned_source_sha256": prerequisite["pins"],
                  "original_guards": prerequisite["context"]["original_guards"],
                  "backup_entries": journal["backup_entries"],
                  "canonical_targets": installed,
                  "generated_go_header_promoted": False,
                  **zero_effects()}
        report_owner = write_fresh(root, REPORT_NAME, canonical(report))
        report_sync = synchronize_directory(root)
        report_owner["directory_fsync_completed"] = report_sync["completed"]
        require_durable_owner(report_owner, relative=REPORT_NAME,
                              root=root, directory_sync=True)
        receipt = {"schema": RECEIPT_SCHEMA, "status": "PASS",
                   "family": family, "activation_root": root,
                   "activation_source_sha256": arguments["activation_source_sha256"],
                   "activation_protocol_sha256": arguments["activation_protocol_sha256"],
                   "activation_contract_sha256": arguments["activation_contract_sha256"],
                   "activation_report": report_owner,
                   "activation_report_sha256": report_owner["sha256"],
                   "recovery_journal_sha256": journal_owner["sha256"],
                   "source_build": report["source_build"],
                   "promotion_mode": "recoverable-canonical-promotion",
                   "group_atomic": False,
                   "receipt_self_publication": "NOT CLAIMED", **zero_effects()}
        receipt_owner = write_fresh(root, RECEIPT_NAME, canonical(receipt))
        receipt_sync = synchronize_directory(root)
        return {"schema": SCHEMA + "-published-activation", "status": "PASS",
                "family": family, "activation_root": root,
                "activation_report_sha256": report_owner["sha256"],
                "activation_receipt_sha256": receipt_owner["sha256"],
                "recovery_journal_sha256": journal_owner["sha256"],
                "receipt_directory_fsync_completed": receipt_sync["completed"],
                "group_atomic": False, **zero_effects()}
    except BaseException:
        try:
            restore_journal_targets(root, journal, journal_owner["sha256"])
        except BaseException as recovery_error:
            raise ActivationError(
                "activation failed and automatic restoration could not complete; "
                "the original journal, intentions, and verified backups remain for "
                "explicit reportless recovery"
            ) from recovery_error
        raise


def validate_activation_documents(report: dict[str, Any], receipt: dict[str, Any],
                                  journal: dict[str, Any], arguments: dict[str, Any]) -> None:
    family = checked_family(arguments["family"])
    root = checked_private_root(arguments["activation_root"], family, build=False)
    require(report.get("schema") == SCHEMA and report.get("status") == "PASS"
            and receipt.get("schema") == RECEIPT_SCHEMA
            and receipt.get("status") == "PASS"
            and report.get("family") == receipt.get("family") == family
            and report.get("activation_root") == receipt.get("activation_root") == root
            and report.get("candidate_import_root") == ROOT
            and report.get("promotion_mode") == "recoverable-canonical-promotion"
            and receipt.get("promotion_mode") == "recoverable-canonical-promotion"
            and report.get("group_atomic") is False
            and receipt.get("group_atomic") is False
            and report.get("generated_go_header_promoted") is False,
            "require the exact genuinely recoverable, individually atomic V4 activation")
    for key in ("activation_source_sha256", "activation_protocol_sha256",
                "activation_contract_sha256"):
        require(report.get(key) == receipt.get(key) == arguments[key],
                "reject a substituted activation source, protocol, or frozen contract")
    require(sha256(canonical(report)) == arguments["activation_report_sha256"]
            and sha256(canonical(receipt)) == arguments["activation_receipt_sha256"]
            and receipt.get("activation_report_sha256")
            == arguments["activation_report_sha256"]
            and receipt.get("recovery_journal_sha256")
            == sha256(canonical(journal)),
            "pin both actual activation documents and their prepared recovery journal")
    validate_build_provenance(report.get("source_build"), family)
    require(report.get("source_build") == receipt.get("source_build")
            and report.get("owned_source_sha256") == journal.get("owned_source_sha256")
            and report.get("backup_entries") == journal.get("backup_entries"),
            "bind activation to the exact complete reportless recovery and source graph")
    for document in (report, receipt):
        for key, value in zero_effects().items():
            require(type(document.get(key)) is type(value) and document.get(key) == value,
                    "reject invented activation candidate, performance, or holdout effects")
    targets = report.get("canonical_targets")
    require(type(targets) is dict and set(targets) == set(FAMILIES[family]["targets"]),
            "require exactly owned canonical targets; never promote the generated Go header")


def recover(arguments: dict[str, Any]) -> dict[str, Any]:
    family, root = checked_family(arguments["family"]), arguments["activation_root"]
    context = verify_frozen_context(verify_live_restored_targets=False)
    require(context["status"] == "PASS"
            and context["activation_source"]["sha256"]
            == arguments["activation_source_sha256"]
            and context["activation_protocol"]["sha256"]
            == arguments["activation_protocol_sha256"]
            and context["activation_contract"]["sha256"]
            == arguments["activation_contract_sha256"],
            "independently reauthenticate all six-family source and recovery owners")
    journal_raw, journal_owner = read_owned(root, JOURNAL_NAME,
                                             arguments.get("recovery_journal_sha256"),
                                             maximum=MAX_SOURCE_BYTES, private=True)
    require(journal_owner["mode"] == 0o600,
            "the reportless recovery journal must be genuinely owner-only")
    journal = decode_document(journal_raw, "prepared V3 recovery journal")
    if arguments["mode"] == "restore":
        report_raw, _ = read_owned(root, REPORT_NAME,
                                   arguments["activation_report_sha256"],
                                   maximum=MAX_REPORT_BYTES, private=True)
        receipt_raw, _ = read_owned(root, RECEIPT_NAME,
                                    arguments["activation_receipt_sha256"],
                                    maximum=MAX_SOURCE_BYTES, private=True)
        report = decode_document(report_raw, "actual V4 activation report")
        receipt = decode_document(receipt_raw, "actual V4 activation receipt")
        validate_activation_documents(report, receipt, journal, arguments)
    journal_args = {**arguments, "recovery_journal_sha256": journal_owner["sha256"]}
    validate_recovery_journal(journal, journal_args)
    build_args = reconstructed_build_arguments(arguments, journal)
    authenticate_prerequisites(build_args)
    targets = restore_journal_targets(root, journal, journal_owner["sha256"])
    return {"schema": RESTORATION_SCHEMA, "status": "PASS",
            "family": family, "activation_root": root,
            "recovery_journal_sha256": journal_owner["sha256"],
            "reportless_recovery": arguments["mode"] == "recover",
            "group_atomic": False, "restored_targets": targets,
            **zero_effects()}



def select_source_build(
    source_digest: Any,
    protocol_digest: Any,
    contract_digest: Any,
) -> dict[str, Any]:
    for digest, label in (
        (source_digest, "source-build recorder"),
        (protocol_digest, "source-build protocol"),
        (contract_digest, "source-build machine contract"),
    ):
        checked_digest(digest, label)
    options = {
        4: {
            "version": 4,
            "schema": BUILD_SCHEMA,
            "receipt_schema": BUILD_RECEIPT_SCHEMA,
            "prefix": BUILD_PREFIX,
            "source_sha256": BUILD_SOURCE_SHA256,
            "protocol_sha256": BUILD_PROTOCOL_SHA256,
            "contract_sha256": BUILD_CONTRACT_SHA256,
        },
        6: {
            "version": 6,
            "schema": BUILD_V6_SCHEMA,
            "receipt_schema": BUILD_V6_RECEIPT_SCHEMA,
            "prefix": BUILD_V6_PREFIX,
            "source_sha256": BUILD_V6_SOURCE_SHA256,
            "protocol_sha256": BUILD_V6_PROTOCOL_SHA256,
            "contract_sha256": BUILD_V6_CONTRACT_SHA256,
        },
    }
    matches = [
        details for details in options.values()
        if (
            details["source_sha256"],
            details["protocol_sha256"],
            details["contract_sha256"],
        ) == (source_digest, protocol_digest, contract_digest)
    ]
    require(len(matches) == 1,
            "require one complete matching V4 or V6 source-freeze digest triple")
    return dict(matches[0])



def parse_arguments(arguments: Any) -> dict[str, Any]:
    require(type(arguments) is list and all(type(item) is str for item in arguments),
            "require one exactly specified V4 activation/recovery invocation")
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    if arguments == ["--verify-frozen-context"]:
        return {"mode": "verify-frozen-context"}
    require(bool(arguments) and arguments[0] in {"--activate", "--recover", "--restore"},
            "explicitly choose guarded test, read-only context, activation, or recovery")
    operation = arguments[0][2:]
    reportless = operation == "recover" or (
        operation == "restore" and "--recovery-journal-sha256" in arguments[1:])
    if operation == "activate":
        mapping = {"--family": "family", "--build-label": "build_label",
                   "--build-root": "build_root",
                   "--activation-source-sha256": "activation_source_sha256",
                   "--activation-protocol-sha256": "activation_protocol_sha256",
                   "--activation-contract-sha256": "activation_contract_sha256",
                   "--build-source-sha256": "build_source_sha256",
                   "--build-protocol-sha256": "build_protocol_sha256",
                   "--build-contract-sha256": "build_contract_sha256",
                   "--build-report-sha256": "build_report_sha256",
                   "--build-receipt-sha256": "build_receipt_sha256"}
        mode = "activate"
    elif reportless:
        mapping = {"--family": "family", "--activation-root": "activation_root",
                   "--activation-source-sha256": "activation_source_sha256",
                   "--activation-protocol-sha256": "activation_protocol_sha256",
                   "--activation-contract-sha256": "activation_contract_sha256",
                   "--recovery-journal-sha256": "recovery_journal_sha256"}
        mode = "recover"
    else:
        mapping = {"--family": "family", "--activation-root": "activation_root",
                   "--activation-source-sha256": "activation_source_sha256",
                   "--activation-protocol-sha256": "activation_protocol_sha256",
                   "--activation-contract-sha256": "activation_contract_sha256",
                   "--activation-report-sha256": "activation_report_sha256",
                   "--activation-receipt-sha256": "activation_receipt_sha256"}
        mode = "restore"
    result: dict[str, Any] = {"mode": mode}
    if mode == "activate":
        result.update({"owned_source_sha256": [], "native_sha256": [], "native_bytes": []})
    position = 1
    while position < len(arguments):
        require(position + 1 < len(arguments), "every exact activation flag needs a value")
        flag, value = arguments[position], arguments[position + 1]
        repeat = {"--owned-source-sha256": "owned_source_sha256",
                  "--native-sha256": "native_sha256", "--native-bytes": "native_bytes"}
        if mode == "activate" and flag in repeat:
            result[repeat[flag]].append(value)
        else:
            require(flag in mapping and mapping[flag] not in result,
                    "reject missing, hidden, repeated, foreign, or abbreviated flags")
            result[mapping[flag]] = value
        position += 2
    expected = {"mode", *mapping.values()}
    if mode == "activate":
        expected |= {"owned_source_sha256", "native_sha256", "native_bytes"}
    require(set(result) == expected, "caller-pin every source, contract, proof, and role")
    family = checked_family(result["family"])
    for key, value in result.items():
        if key.endswith("_sha256") and key not in {"owned_source_sha256", "native_sha256"}:
            checked_digest(value, key)
    if mode == "activate":
        checked_label(result["build_label"])
        selected = select_source_build(
            result["build_source_sha256"],
            result["build_protocol_sha256"],
            result["build_contract_sha256"],
        )
        result["build_version"] = selected["version"]
        checked_private_root(
            result["build_root"], family, build=True,
            build_version=result["build_version"],
        )
        parse_owner_pins(family, result["owned_source_sha256"])
        result["native_hashes"] = parse_native_pins(
            family, result["native_sha256"], sizes=False,
        )
        result["native_sizes"] = parse_native_pins(
            family, result["native_bytes"], sizes=True,
        )
    else:
        checked_private_root(result["activation_root"], family, build=False)
    return result


class BlockedEnvironment:
    """A strictly inaccessible environment during synthetic-only controls."""

    def __init__(self, sandbox: SyntheticSandbox) -> None:
        self.sandbox = sandbox

    def _blocked(self, *arguments: Any, **keywords: Any) -> Any:
        self.sandbox.counts["blocked_environment_operations"] += 1
        raise SourceOnlyEffect("synthetic controls cannot inspect the process environment")

    __getitem__ = _blocked
    __setitem__ = _blocked
    __delitem__ = _blocked
    __iter__ = _blocked
    __contains__ = _blocked
    get = _blocked
    items = _blocked
    keys = _blocked
    values = _blocked
    copy = _blocked


class SyntheticSandbox:
    """Intercept all real filesystem, native, timing, and process effects."""

    def __init__(self) -> None:
        self.original: list[tuple[Any, str, Any]] = []
        self.counts = {
            "actual_file_reads": 0, "actual_file_writes": 0,
            "actual_processes": 0, "actual_threads": 0,
            "actual_clocks": 0, "actual_network": 0,
            "actual_candidate_imports": 0, "actual_native_library_loads": 0,
            "actual_holdout_reads": 0, "actual_canonical_promotions": 0,
            "actual_recovery_roots": 0,
            "blocked_file_operations": 0, "blocked_process_operations": 0,
            "blocked_thread_operations": 0, "blocked_clock_operations": 0,
            "blocked_network_operations": 0, "blocked_import_operations": 0,
            "blocked_temporary_operations": 0,
            "blocked_native_library_operations": 0,
            "blocked_environment_operations": 0,
            "blocked_promotion_operations": 0,
        }

    def install(self, owner: Any, name: str, value: Any) -> None:
        self.original.append((owner, name, getattr(owner, name)))
        setattr(owner, name, value)

    def deny(self, count: str, message: str) -> Any:
        def blocked(*arguments: Any, **keywords: Any) -> Any:
            self.counts[count] += 1
            raise SourceOnlyEffect(message)
        return blocked

    def __enter__(self) -> SyntheticSandbox:
        files = self.deny("blocked_file_operations",
                          "synthetic activation controls cannot open or change a file")
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "write"), (os, "stat"), (os, "lstat"), (os, "fstat"),
            (os, "listdir"), (os, "scandir"), (os, "mkdir"), (os, "makedirs"),
            (os, "unlink"), (os, "remove"), (os, "link"), (os, "fsync"),
            (os, "fchmod"), (Path, "open"), (Path, "read_bytes"),
            (Path, "read_text"), (Path, "write_bytes"), (Path, "write_text"),
            (Path, "exists"), (Path, "is_file"), (Path, "is_dir"),
            (Path, "stat"), (Path, "lstat"), (Path, "mkdir"), (Path, "iterdir"),
        ):
            if hasattr(owner, name):
                self.install(owner, name, files)
        self.install(os, "replace", self.deny(
            "blocked_promotion_operations", "synthetic controls cannot activate a native file"))
        processes = self.deny("blocked_process_operations",
                              "synthetic controls cannot run a worker or compiler")
        for owner, name in ((subprocess, "Popen"), (subprocess, "run"),
                            (subprocess, "check_call"), (subprocess, "check_output"),
                            (os, "system"), (os, "popen")):
            if hasattr(owner, name):
                self.install(owner, name, processes)
        for name in ("mkdtemp", "mkstemp", "TemporaryDirectory"):
            if hasattr(tempfile, name):
                self.install(tempfile, name, self.deny(
                    "blocked_temporary_operations",
                    "synthetic controls cannot create a recovery or build root"))
        self.install(threading.Thread, "start", self.deny(
            "blocked_thread_operations", "synthetic controls cannot start a thread"))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns",
                     "clock_gettime", "clock_gettime_ns"):
            if hasattr(time, name):
                self.install(time, name, self.deny(
                    "blocked_clock_operations", "synthetic controls cannot measure time"))
        self.install(socket, "socket", self.deny(
            "blocked_network_operations", "synthetic controls cannot open a network"))
        self.install(importlib, "import_module", self.deny(
            "blocked_import_operations", "synthetic controls cannot import a candidate"))
        self.install(ctypes, "CDLL", self.deny(
            "blocked_native_library_operations", "synthetic controls cannot load an engine"))
        self.install(os, "environ", BlockedEnvironment(self))
        return self

    def __exit__(self, kind: Any, value: Any, trace: Any) -> bool:
        for owner, name, previous in reversed(self.original):
            setattr(owner, name, previous)
        return False


def synthetic_digest(value: str) -> str:
    return sha256(value.encode("utf-8"))


def synthetic_dynamic(*, needed: tuple[str, ...] = (),
                      soname: str | None = None,
                      runpath: str | None = None,
                      rpath: str | None = None) -> bytes:
    rows = ["Dynamic section at offset 0x1 contains 1 entry:"]
    for value in needed:
        rows.append(" 0x1 (NEEDED) Shared library: [" + value + "]")
    for marker, value in (("SONAME", soname), ("RUNPATH", runpath), ("RPATH", rpath)):
        if value is not None:
            rows.append(" 0x1 (" + marker + ") Value: [" + value + "]")
    return ("\n".join(rows) + "\n").encode("ascii")


def synthetic_symbols(exports: tuple[str, ...],
                      undefined: tuple[str, ...] = ()) -> bytes:
    count = 1 + len(exports) + len(undefined)
    rows = ["Symbol table '.dynsym' contains " + str(count) + " entries:",
            "   Num: Value Size Type Bind Vis Ndx Name",
            "     0: 0000000000000000 0 NOTYPE LOCAL DEFAULT UND"]
    index = 1
    for section, values in (("12", exports), ("UND", undefined)):
        for value in values:
            rows.append(str(index) + ": 0000000000000000 1 FUNC GLOBAL DEFAULT "
                        + section + " " + value
                        + (" (2)" if "@" in value else ""))
            index += 1
    return ("\n".join(rows) + "\n").encode("ascii")


def synthetic_owner(relative: str, *, seed: str, mode: int = 0o600,
                    durable: bool = False, root: str = ROOT) -> dict[str, Any]:
    identity = int(synthetic_digest(seed)[:12], 16)
    owner = {"relative": relative, "path": root + "/" + relative,
             "sha256": synthetic_digest(seed + "-bytes"),
             "size_bytes": 64, "device": 2064, "inode": identity, "mode": mode}
    if durable:
        owner.update({"exclusive_creation": True,
                      "same_inode_readback_verified": True,
                      "file_fsync_completed": True,
                      "directory_fsync_completed": True,
                      "write_calls": 1})
    return owner


def synthetic_stream(stdout: bytes, *, name: str, pid: int,
                     family: str, phase: str, root: str) -> dict[str, Any]:
    commands = planned_commands(root, family, phase)
    paths = phase_paths(root, family, phase)
    cwd = (paths["go_module_directory"]
           if family == "go" and name == "build_go_engine" else paths["base"])
    stderr = b""
    return {
        "name": name, "argv": commands[name],
        "working_directory": sanitized(cwd, root),
        "environment": expected_environment(root, family, phase),
        "shell": False, "pid": pid, "exit_status": 0,
        "stdout_base64": base64.b64encode(stdout).decode("ascii"),
        "stdout_sha256": sha256(stdout), "stdout_bytes": len(stdout),
        "stderr_base64": "", "stderr_sha256": sha256(stderr),
        "stderr_bytes": 0,
    }


def synthetic_native_audit(family: str, role: str) -> tuple[bytes, bytes, dict[str, Any]]:
    require(role in FAMILIES[family]["targets"],
            "synthesize only an exact authentic matching native role")
    if family == "c":
        dynamic = synthetic_dynamic(needed=("libc.so.6",))
        symbols = synthetic_symbols(("PyInit__vm_native",))
    elif family == "cpp":
        dynamic = synthetic_dynamic(needed=("libc.so.6", "libstdc++.so.6"))
        symbols = synthetic_symbols(("PyInit__cpp_bridge", "rebar_cpp_owned"))
    elif role == "engine":
        exports = {"rust": RUST_EXPORTS, "zig": ZIG_EXPORTS,
                   "go": GO_EXPORTS, "fortran": FORTRAN_EXPORTS}[family]
        callbacks = tuple(sorted(FORTRAN_CALLBACKS)) if family == "fortran" else ()
        dynamic = synthetic_dynamic(
            needed=("libc.so.6",), soname=FAMILIES[family]["targets"]["engine"])
        symbols = synthetic_symbols(tuple(sorted(exports)), callbacks)
    else:
        exports = {"rust": RUST_EXPORTS, "zig": ZIG_EXPORTS,
                   "go": GO_EXPORTS, "fortran": FORTRAN_EXPORTS}[family]
        defined = (("PyInit__fortran_bridge", *tuple(sorted(FORTRAN_CALLBACKS)))
                   if family == "fortran" else ("PyInit__" + family + "_bridge",))
        unresolved = (tuple(sorted(exports)) if family in {"go", "fortran"}
                      else (next(iter(sorted(exports))),))
        dynamic = synthetic_dynamic(
            needed=(FAMILIES[family]["targets"]["engine"], "libc.so.6"),
            runpath="$ORIGIN")
        symbols = synthetic_symbols(defined, unresolved)
    return dynamic, symbols, validate_elf(
        family, role, parse_dynamic(dynamic), parse_symbols(symbols))


def reseal_synthetic_build(fixture: dict[str, Any]) -> dict[str, Any]:
    report, receipt, arguments = fixture["report"], fixture["receipt"], fixture["arguments"]
    archive = gzip.compress(canonical(report), compresslevel=9, mtime=0)
    family, label = arguments["family"], arguments["build_label"]
    relative = EVIDENCE_RELATIVE + "/native-source-build-v4-" + family + "-" + label + ".json.gz"
    receipt.update({"archive_relative": relative, "archive_sha256": sha256(archive),
                    "archive_bytes": len(archive),
                    "uncompressed_sha256": sha256(canonical(report)),
                    "uncompressed_bytes": len(canonical(report))})
    receipt["archive_publication"].update({"path": ROOT + "/" + relative,
                                           "sha256": sha256(archive),
                                           "bytes": len(archive)})
    arguments["build_report_sha256"] = sha256(archive)
    arguments["build_receipt_sha256"] = sha256(canonical(receipt))
    fixture["archive"] = archive
    return fixture


def synthetic_build_fixture(family: str) -> dict[str, Any]:
    family = checked_family(family)
    root = "/tmp/" + BUILD_PREFIX + family + "-synthetic"
    label = "synthetic-v4"
    pins = {path: digest for path, (digest, _) in SOURCE_OWNERS[family].items()}
    generated_header = (b"/* Code generated by cmd/cgo; DO NOT EDIT. */\n"
                        + b"\n".join(
                            ("extern void " + symbol + "(void);").encode("ascii")
                            for symbol in sorted(GO_EXPORTS)) + b"\n")
    native_bytes = {
        role: (generated_header if role == "generated_header"
               else ("synthetic-v4-owned-" + family + "-" + role).encode("ascii"))
        for role in expected_roles(family)
    }
    hashes = {role: sha256(raw) for role, raw in native_bytes.items()}
    sizes = {role: len(raw) for role, raw in native_bytes.items()}
    arguments: dict[str, Any] = {
        "family": family, "build_label": label, "build_root": root,
        "activation_source_sha256": synthetic_digest("v4-activation-source"),
        "activation_protocol_sha256": synthetic_digest("v4-activation-protocol"),
        "activation_contract_sha256": synthetic_digest("v4-activation-contract"),
        "build_source_sha256": BUILD_SOURCE_SHA256,
        "build_protocol_sha256": BUILD_PROTOCOL_SHA256,
        "build_contract_sha256": BUILD_CONTRACT_SHA256,
        "native_hashes": hashes, "native_sizes": sizes,
        "owned_source_sha256": [path + "=" + digest for path, digest in pins.items()],
    }
    history = []
    for name in ("v2_c", "v2_rust", "v2_zig_failure"):
        record = HISTORICAL_RECORDS[name]
        history.append({"family": record["family"],
                        "build_status": record["status"],
                        "process_count": record["process_count"],
                        "archive_sha256": record["archive_sha256"],
                        "receipt_sha256": record["receipt_sha256"],
                        "historical_v1_symbol_audit": "FALSIFIED AND PRESERVED",
                        "failure_preserved": record["status"] == "FAIL"})
    snapshots: dict[str, Any] = {}
    for index, (path, (digest, size)) in enumerate(SOURCE_OWNERS[family].items()):
        snapshots[path] = {"path": ROOT + "/" + path, "sha256": digest,
                           "size_bytes": size, "device": 2064, "inode": 500000 + index,
                           "executable": False}
    audits: dict[str, tuple[bytes, bytes, dict[str, Any]]] = {}
    for role in FAMILIES[family]["targets"]:
        audits[role] = synthetic_native_audit(family, role)
    phases, processes = [], []
    counter = 200000
    for phase_index, phase in enumerate(("reference-a", "reference-b")):
        prefix = SANITIZED_BUILD_ROOT + "/" + phase
        copies: dict[str, Any] = {}
        for index, (path, (digest, size)) in enumerate(SOURCE_OWNERS[family].items()):
            copies[path] = {"path": prefix + "/source/" + path,
                            "sha256": digest, "bytes": size,
                            "device": 2064,
                            "inode": 600000 + phase_index * 1000 + index,
                            "exclusive_creation": True,
                            "same_inode_readback_verified": True,
                            "file_fsync_completed": False, "write_calls": 1}
        outputs: dict[str, Any] = {}
        for index, role in enumerate(expected_roles(family)):
            filename = expected_roles(family)[role]
            if role == "generated_header":
                audit = audit_go_header(generated_header)
            else:
                audit = audits[role][2]
            outputs[role] = {"family": family, "role": role,
                             "file_name": filename,
                             "path": prefix + "/native/" + filename,
                             "sha256": hashes[role], "size_bytes": sizes[role],
                             "device": 2064,
                             "inode": 700000 + phase_index * 1000 + index,
                             "audit": audit, "prebuilt_artifact_read": False,
                             "candidate_imported": False}
        phases.append({"name": phase, "fresh_source_directory": prefix + "/source",
                       "fresh_native_directory": prefix + "/native",
                       "fresh_temporary_directory": prefix + "/temporary",
                       "fresh_source_owners": copies, "native_outputs": outputs,
                       "candidate_processes_started": 0, "candidate_imports": 0,
                       "native_libraries_loaded": 0, "timing_trials_run": 0,
                       "hidden_cases_read": 0})
        for name in process_schedule(family):
            if name == "zig_version":
                stdout = b"0.16.0\n"
            elif name == "go_version":
                stdout = b"go version go1.26.3 linux/amd64\n"
            elif name == "cargo_version":
                stdout = b"cargo 1.95.0 (f2d3ce0bd synthetic)\n"
            elif name == "rustc_version":
                stdout = b"rustc 1.95.0 (59807616e synthetic)\nrelease: 1.95.0\n"
            elif name in {"gcc_version", "gxx_version", "gfortran_version"}:
                stdout = b"synthetic GNU compiler 13.3.0\n"
            elif name == "readelf_version":
                stdout = b"GNU readelf synthetic\n"
            elif name.endswith("_dynamic"):
                stdout = audits[name[:-len("_dynamic")]][0]
            elif name.endswith("_symbols"):
                stdout = audits[name[:-len("_symbols")]][1]
            else:
                stdout = b""
            counter += 1
            processes.append(synthetic_stream(stdout, name=name, pid=counter,
                                             family=family, phase=phase, root=root))
    reproduction = {
        "independent_fresh_phase_count": 2, "byte_identical": True,
        "unique_process_count": len(processes), "native_outputs": {},
        "prebuilt_artifact_count": 0, "native_libraries_loaded": 0,
    }
    for role, item in phases[0]["native_outputs"].items():
        reproduction["native_outputs"][role] = {
            "file_name": item["file_name"], "sha256": item["sha256"],
            "size_bytes": item["size_bytes"], "fresh_independent_inode_count": 2,
            "reproduced_in_two_fresh_directories": True, "audit": item["audit"],
        }
    report = {
        "schema": BUILD_SCHEMA, "version": 4, "status": "PASS",
        "family": family, "label": label, "source_sha256": BUILD_SOURCE_SHA256,
        "protocol_sha256": BUILD_PROTOCOL_SHA256,
        "contract_sha256": BUILD_CONTRACT_SHA256,
        "fresh_private_root": SANITIZED_BUILD_ROOT,
        "owned_source_sha256": pins,
        "owned_source_before": copy.deepcopy(snapshots),
        "owned_source_after": copy.deepcopy(snapshots),
        "frozen_correctness": {"status": "PASS", "suite_count": 13,
                               "case_execution_count": 31237,
                               "candidate_qualified_count": 0,
                               "candidate_correctness": "NOT MEASURED",
                               "holdout": "NOT OPENED",
                               "performance": "NOT MEASURED"},
        "preserved_v2_history": history, "processes": processes,
        "build_phases": phases, "reproducibility": reproduction,
        **zero_effects(),
    }
    receipt = {
        "schema": BUILD_RECEIPT_SCHEMA, "status": "PASS", "build_status": "PASS",
        "family": family, "label": label, "source_sha256": BUILD_SOURCE_SHA256,
        "protocol_sha256": BUILD_PROTOCOL_SHA256,
        "contract_sha256": BUILD_CONTRACT_SHA256,
        "phase1_manifest_sha256": PHASE1_SHA256,
        "owned_source_sha256": pins,
        "archive_publication": {"exclusive_creation": True,
                                "same_inode_readback_verified": True,
                                "file_fsync_completed": True,
                                "write_calls": 1},
        "archive_directory_fsync": {"completed": True, "device": 2064,
                                    "inode": 400001},
        "receipt_self_publication": "NOT CLAIMED",
        **zero_effects(),
    }
    return reseal_synthetic_build({"report": report, "receipt": receipt,
                                   "arguments": arguments, "archive": b""})


def validate_synthetic_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    return validate_build_report(fixture["report"], fixture["receipt"],
                                 fixture["archive"], fixture["arguments"],
                                 {path: digest for path, digest
                                  in (item.split("=", 1) for item
                                      in fixture["arguments"]["owned_source_sha256"])})


def attack_synthetic_build(family: str, mutation: Any) -> dict[str, Any]:
    fixture = synthetic_build_fixture(family)
    mutation(fixture)
    reseal_synthetic_build(fixture)
    return validate_synthetic_fixture(fixture)


def reseal_preserved_v4_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    reseal_synthetic_build(fixture)
    report, receipt = fixture["report"], fixture["receipt"]
    family = checked_family(report.get("family"))
    expected = HISTORICAL_V4_RECORDS[family]
    phase_outputs = []
    for phase in report.get("build_phases", []):
        outputs = phase.get("native_outputs")
        phase_outputs.append({
            role: (value.get("sha256"), value.get("size_bytes"))
            for role, value in outputs.items()
        } if type(outputs) is dict else {})
    fixture["historical_spec"] = {
        "family": family, "status": expected["status"],
        "label": report["label"],
        "archive": receipt["archive_relative"],
        "archive_sha256": sha256(fixture["archive"]),
        "archive_bytes": len(fixture["archive"]),
        "plain_sha256": sha256(canonical(report)),
        "plain_bytes": len(canonical(report)),
        "receipt": "oracle/phase2/evidence/synthetic-" + family + "-receipt.json",
        "receipt_sha256": sha256(canonical(receipt)),
        "receipt_bytes": len(canonical(receipt)),
        "process_count": expected["process_count"],
        "completed_phase_count": expected["completed_phase_count"],
        "phase_outputs": tuple(phase_outputs),
        **({"error_message": expected["error_message"]}
           if "error_message" in expected else {}),
    }
    return fixture


def synthetic_preserved_v4_fixture(family: str) -> dict[str, Any]:
    require(family in HISTORICAL_V4_RECORDS,
            "synthesize only one of the three actual historical V4 outcomes")
    fixture = synthetic_build_fixture(family)
    report, receipt = fixture["report"], fixture["receipt"]
    publication = receipt["archive_publication"]
    publication.update({"device": 2064,
                        "inode": 810000 + ("cpp", "go", "fortran").index(family)})
    if family == "go":
        report["status"] = "FAIL"
        receipt["build_status"] = "FAIL"
        report["processes"] = report["processes"][:4]
        failed = report["processes"][-1]
        stderr = (b"# rebar.local/candidates/go\n"
                  b"py_bridge.c:2:10: fatal error: Python.h: No such file or directory\n")
        failed.update({"exit_status": 1,
                       "stderr_base64": base64.b64encode(stderr).decode("ascii"),
                       "stderr_sha256": sha256(stderr),
                       "stderr_bytes": len(stderr)})
        report["build_phases"] = []
        report["reproducibility"] = None
        report["error"] = {
            "type": "BuildError",
            "message": HISTORICAL_V4_RECORDS[family]["error_message"],
        }
    elif family == "fortran":
        report["status"] = "FAIL"
        receipt["build_status"] = "FAIL"
        report["build_phases"][1]["native_outputs"]["engine"]["sha256"] = (
            synthetic_digest("fortran-real-second-phase-engine-is-different"))
        report["reproducibility"] = None
        report["error"] = {
            "type": "BuildError",
            "message": HISTORICAL_V4_RECORDS[family]["error_message"],
        }
    return reseal_preserved_v4_fixture(fixture)


def validate_synthetic_preserved_v4_fixture(
    fixture: dict[str, Any],
) -> dict[str, Any]:
    return validate_preserved_v4_documents(
        fixture["historical_spec"], fixture["report"],
        fixture["receipt"], fixture["archive"])


def attack_synthetic_preserved_v4(family: str, mutation: Any) -> dict[str, Any]:
    fixture = synthetic_preserved_v4_fixture(family)
    mutation(fixture)
    reseal_preserved_v4_fixture(fixture)
    return validate_synthetic_preserved_v4_fixture(fixture)


def self_test() -> dict[str, Any]:
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, value: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "every synthetic safety control requires a distinct exact identity")
        require(bool(value), "a positive V4 activation control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "every hostile activation control requires a distinct exact identity")
        try:
            action()
        except (ActivationError, OSError, TypeError, ValueError, UnicodeError,
                OverflowError, RecursionError, zlib.error):
            rejected.append(name)
            return
        raise ActivationError("an unsafe V4 activation attack was accepted: " + name)

    with SyntheticSandbox() as guard:
        contract = expected_contract()
        accept("exact-published-v4-source-protocol-and-machine-contract",
               validate_contract(contract)["source_build"] == expected_source_build())
        accept("exact-six-independent-families-and-twenty-five-source-owners",
               len(FAMILIES) == 6
               and len({path for graph in SOURCE_OWNERS.values() for path in graph}) == 25)
        accept("zero-qualified-candidates-and-unchanged-frozen-baseline",
               contract["qualified_candidate_count"] == 0
               and contract["oracle"]["suite_count"] == 13
               and contract["oracle"]["case_execution_count"] == 31237)
        accept("historical-v4-cpp-pass-and-go-fortran-failures-preserved",
               contract["source_build"]["actual_build_status"]
               == "CPP PASS; GO FAIL; FORTRAN FAIL"
               and contract["source_build"]["historical_successful_build_families"]
               == ["cpp"]
               and contract["source_build"]["historical_failed_build_families"]
               == ["go", "fortran"])
        accept("activation-freeze-starts-no-v4-build",
               contract["source_build"]["builds_started_by_activation_freeze"] == 0
               and contract["phase_boundary"]["actual_v4_source_builds"] == "NOT RUN")
        accept("no-v3-canonical-activation-performed",
               contract["phase_boundary"]["actual_v3_activations"] == "NOT RUN")
        accept("exact-ten-distinct-canonical-engine-and-bridge-targets",
               sum(len(info["targets"]) for info in FAMILIES.values()) == 10)
        accept("generated-go-header-is-proof-only-never-a-canonical-target",
               "generated_header" in FAMILIES["go"]["generated"]
               and "generated_header" not in FAMILIES["go"]["targets"])
        accept("exact-nine-owned-go-c-shared-exports", len(GO_EXPORTS) == 9)
        accept("exact-nine-fortran-functions-and-three-reverse-callbacks",
               len(FORTRAN_EXPORTS) == 9 and len(FORTRAN_CALLBACKS) == 3)
        accept("v2-zig-real-failure-preserved",
               HISTORICAL_RECORDS["v2_zig_failure"]["status"] == "FAIL")
        accept("v3-zig-corrected-real-source-build-pass-preserved",
               HISTORICAL_RECORDS["v3_zig"]["status"] == "PASS")
        accept("v6-zig-candidate-worker-and-subinterpreter-failures-preserved",
               all(HISTORICAL_RECORDS[key]["status"] == "FAIL"
                   for key in ("v6_zig_candidate_failure", "v6_zig_worker_failure",
                               "v6_zig_subinterpreter_failure")))
        accept("actual-owner-only-v6-zig-restoration-receipt-pinned",
               RESTORATION_SHA256
               == "c415ba80c055d39a933617a839624037b557adbe30c418c2a0e859131fbe9028")
        accept("all-real-v4-v5-v6-candidate-and-build-owners-required",
               contract["historical_candidate_evidence"]
               == expected_historical_evidence()
               and contract["historical_candidate_evidence"]
               ["candidate_evidence_owner_count"] == 51
               and contract["historical_candidate_evidence"]
               ["published_v4_build_evidence_owner_count"] == 6
               and contract["historical_candidate_evidence"]
               ["published_v5_build_evidence_owner_count"] == 4
               and contract["historical_candidate_evidence"]
               ["published_v6_build_evidence_owner_count"]
               == 2 * len(HISTORICAL_V6_RECORDS)
               and contract["historical_candidate_evidence"]
               ["total_distinct_evidence_owner_count"]
               == 61 + 2 * len(HISTORICAL_V6_RECORDS)
               and len(ZIG_V6_SUBORDINATE) == 10)
        accept("preserved-v2-process-denominator-exactly-thirty-nine",
               sum(HISTORICAL_RECORDS[key]["process_count"]
                   for key in ("v2_c", "v2_rust", "v2_zig_failure")) == 39)
        ledger = contract["historical_candidate_evidence"][
            "historical_build_process_ledger"]
        accept("corrected-v3-zig-fifteen-processes-never-silently-dropped",
               HISTORICAL_RECORDS["v3_zig"]["process_count"]
               == ledger["v3_zig_process_count"] == 15)
        accept("later-v4-build-processes-are-exactly-ten-four-and-eighteen",
               ledger["v4_processes_by_family"]
               == {"cpp": 10, "go": 4, "fortran": 18}
               and ledger["v4_process_count"] == 32)
        accept("all-actual-versioned-process-denominators-preserved",
               ledger["v2_and_v4_process_count"] == 71
               and ledger["v2_v4_v5_process_count"] == 102
               and ledger["v5_processes_by_family"]
               == {"go": 5, "fortran": 26}
               and ledger["v6_process_count"]
               == sum(item["process_count"]
                      for item in HISTORICAL_V6_RECORDS.values())
               and ledger["all_historical_build_process_count"]
               == 117 + ledger["v6_process_count"]
               and ledger["unique_pid_scope"]
               == "WITHIN EACH ACTUAL BUILD REPORT ONLY")
        accept("five-original-cpython-guard-sources-unchanged",
               len(ORIGINAL_GUARDS) == 5)
        accept("individual-atomic-promotions-never-claim-group-atomicity",
               contract["recovery_policy"]["target_promotion"]
               == "INDIVIDUALLY ATOMIC; NEVER GROUP-ATOMIC")
        accept("canonical-lone-surrogate-and-sixty-four-bit-integer",
               decode_document(canonical({"large": 6001118316486346290,
                                          "maximum": 18446744073709551615,
                                          "surrogate": "\ud800"}), "synthetic")
               == {"large": 6001118316486346290,
                   "maximum": 18446744073709551615,
                   "surrogate": "\ud800"})
        accept("standalone-read-only-frozen-context-selector",
               parse_arguments(["--verify-frozen-context"])
               == {"mode": "verify-frozen-context"})
        accept("standalone-in-memory-self-test-selector",
               parse_arguments(["--self-test"]) == {"mode": "self-test"})
        v4_source = select_source_build(
            BUILD_SOURCE_SHA256,
            BUILD_PROTOCOL_SHA256,
            BUILD_CONTRACT_SHA256,
        )
        v6_source = select_source_build(
            BUILD_V6_SOURCE_SHA256,
            BUILD_V6_PROTOCOL_SHA256,
            BUILD_V6_CONTRACT_SHA256,
        )
        accept("exact-independent-original-v4-build-source-triple",
               v4_source["version"] == 4
               and v4_source["schema"] == BUILD_SCHEMA
               and v4_source["prefix"] == BUILD_PREFIX)
        accept("exact-independent-corrected-v6-build-source-triple",
               v6_source["version"] == 6
               and v6_source["schema"] == BUILD_V6_SCHEMA
               and v6_source["prefix"] == BUILD_V6_PREFIX)
        accept("cpp-uses-only-the-actual-combined-owned-bridge",
               set(FAMILIES["cpp"]["targets"]) == {"bridge"}
               and not FAMILIES["cpp"]["generated"])
        accept("go-match-remains-python-owned-not-a-fictional-native-export",
               len(GO_EXPORTS) == 9
               and "Match" not in GO_EXPORTS
               and set(FAMILIES["go"]["targets"])
               == {"engine", "bridge"}
               and set(FAMILIES["go"]["generated"])
               == {"generated_header"})
        accept("both-actually-observed-v5-failures-remain-failures",
               set(HISTORICAL_V5_RECORDS) == {"go", "fortran"}
               and all(item["build_status"] == "FAIL"
                       for item in HISTORICAL_V5_RECORDS.values())
               and HISTORICAL_V5_RECORDS["go"]["process_count"] == 5
               and HISTORICAL_V5_RECORDS["fortran"]["process_count"] == 26)
        accept("actual-v6-go-has-exactly-nine-exports-and-26-real-processes",
               HISTORICAL_V6_RECORDS["go"]["status"] == "PASS"
               and HISTORICAL_V6_RECORDS["go"]["process_count"] == 26
               and HISTORICAL_V6_RECORDS["go"]["completed_phase_count"] == 2
               and set(HISTORICAL_V6_RECORDS["go"]["native_outputs"])
               == {"engine", "bridge", "generated_header"})
        actual_fortran = HISTORICAL_V6_RECORDS["fortran"]
        accept("actual-v6-fortran-26-successful-processes-but-build-failure",
               actual_fortran["status"] == "FAIL"
               and actual_fortran["process_count"] == 26
               and actual_fortran["successful_process_count"] == 26
               and actual_fortran["completed_phase_count"] == 2
               and actual_fortran["error"] == {
                   "type": "BuildError",
                   "message": (
                       "the two independently owned outputs "
                       "are not genuinely byte-identical"
                   ),
               })
        accept("actual-v6-fortran-engine-differs-with-no-build-id",
               len(actual_fortran["phase_outputs"]) == 2
               and actual_fortran["phase_outputs"][0]["native_outputs"][
                   "engine"
               ]["sha256"]
               != actual_fortran["phase_outputs"][1]["native_outputs"][
                   "engine"
               ]["sha256"]
               and all(
                   phase["native_outputs"]["engine"]["notes_bytes"] == 0
                   for phase in actual_fortran["phase_outputs"]
               )
               and actual_fortran["differing_raw_binary_section"]
               == "NOT RECORDED")
        accept("actual-v6-fortran-bridge-reproduces-but-never-qualifies",
               actual_fortran["phase_outputs"][0]["native_outputs"][
                   "bridge"
               ]["sha256"]
               == actual_fortran["phase_outputs"][1]["native_outputs"][
                   "bridge"
               ]["sha256"]
               and contract["qualified_candidate_count"] == 0)
        accept("exact-sixty-five-distinct-actual-evidence-owners",
               contract["historical_candidate_evidence"][
                   "total_distinct_evidence_owner_count"
               ] == 65)
        accept("exact-169-actual-all-version-build-processes",
               contract["historical_candidate_evidence"][
                   "historical_build_process_ledger"
               ]["all_historical_versions_actual_compiler_process_count"]
               == 169)
        accept("exact-observed-v6-report-receipt-and-process-field-closures",
               len(V6_REPORT_FIELDS) == 41
               and len(V6_RECEIPT_FIELDS) == 35
               and len(V6_PROCESS_FIELDS) == 13
               and "build_status" not in V6_REPORT_FIELDS
               and "build_status" in V6_RECEIPT_FIELDS)
        for old, corrected, field in (
            (BUILD_SOURCE_SHA256, BUILD_V6_SOURCE_SHA256, "source"),
            (BUILD_PROTOCOL_SHA256, BUILD_V6_PROTOCOL_SHA256, "protocol"),
            (BUILD_CONTRACT_SHA256, BUILD_V6_CONTRACT_SHA256, "contract"),
        ):
            mixed = [
                BUILD_V6_SOURCE_SHA256,
                BUILD_V6_PROTOCOL_SHA256,
                BUILD_V6_CONTRACT_SHA256,
            ]
            index = {"source": 0, "protocol": 1, "contract": 2}[field]
            mixed[index] = old
            reject(
                "reject-mixed-v4-v6-" + field + "-freeze",
                lambda parts=tuple(mixed): select_source_build(*parts),
            )
            require(old != corrected,
                    "independently published V4 and V6 freezes must differ")
        reject(
            "reject-v4-root-for-v6-source-build",
            lambda: checked_private_root(
                "/tmp/" + BUILD_PREFIX + "go-synthetic",
                "go", build=True, build_version=6,
            ),
        )
        reject(
            "reject-v6-root-for-v4-source-build",
            lambda: checked_private_root(
                "/tmp/" + BUILD_V6_PREFIX + "go-synthetic",
                "go", build=True, build_version=4,
            ),
        )
        reject(
            "reject-build-version-for-recovery-root",
            lambda: checked_private_root(
                "/tmp/" + PRIVATE_PREFIX + "go-synthetic",
                "go", build=False, build_version=6,
            ),
        )
        reject(
            "synthetic-effect-wall-prevents-v6-kernel-source-loading",
            lambda: load_frozen_v6_build_kernel(),
        )
        for family in HISTORICAL_V4_RECORDS:
            preserved = synthetic_preserved_v4_fixture(family)
            actual = validate_synthetic_preserved_v4_fixture(preserved)
            accept(family + "-resealed-authentic-preserved-v4-build-outcome",
                   actual["build_status"] == HISTORICAL_V4_RECORDS[family]["status"]
                   and actual["process_count"]
                   == HISTORICAL_V4_RECORDS[family]["process_count"]
                   and actual["completed_phase_count"]
                   == HISTORICAL_V4_RECORDS[family]["completed_phase_count"]
                   and actual["qualified_candidate_count"] == 0)
            reject(family + "-reject-resealed-preserved-v4-process-omission",
                   lambda family=family: attack_synthetic_preserved_v4(
                       family, lambda fixture: fixture["report"]["processes"].pop()))
            reject(family + "-reject-resealed-preserved-v4-reused-process-id",
                   lambda family=family: attack_synthetic_preserved_v4(
                       family, lambda fixture: fixture["report"]["processes"][1].update(
                           {"pid": fixture["report"]["processes"][0]["pid"]})))
            reject(family + "-reject-resealed-preserved-v4-corrupt-process-stream",
                   lambda family=family: attack_synthetic_preserved_v4(
                       family, lambda fixture: fixture["report"]["processes"][0].update(
                           {"stdout_base64": base64.b64encode(b"substituted").decode(
                               "ascii")})))
            reject(family + "-reject-resealed-preserved-v4-opened-holdout",
                   lambda family=family: attack_synthetic_preserved_v4(
                       family, lambda fixture: fixture["report"].update(
                           {"hidden_cases_read": 1})))
            if family in {"go", "fortran"}:
                reject(family + "-reject-resealed-historical-failure-as-build-pass",
                       lambda family=family: attack_synthetic_preserved_v4(
                           family, lambda fixture: (
                               fixture["report"].update({"status": "PASS"}),
                               fixture["receipt"].update({"build_status": "PASS"}))))
                reject(family + "-reject-passing-publication-as-passing-build",
                       lambda family=family: attack_synthetic_preserved_v4(
                           family, lambda fixture: fixture["receipt"].update(
                               {"build_status": "PASS"})))
            elif family == "cpp":
                reject("cpp-reject-resealed-genuine-v4-pass-relabeled-failure",
                       lambda: attack_synthetic_preserved_v4(
                           "cpp", lambda fixture: (
                               fixture["report"].update({"status": "FAIL"}),
                               fixture["receipt"].update({"build_status": "FAIL"}))))
        reject("go-reject-resealed-fabricated-completed-source-phase",
               lambda: attack_synthetic_preserved_v4(
                   "go", lambda fixture: fixture["report"]["build_phases"].append(
                       synthetic_build_fixture("go")["report"]["build_phases"][0])))
        reject("go-reject-resealed-hidden-actual-failing-process",
               lambda: attack_synthetic_preserved_v4(
                   "go", lambda fixture: fixture["report"]["processes"][-1].update(
                       {"exit_status": 0})))
        reject("fortran-reject-resealed-false-byte-identical-engines",
               lambda: attack_synthetic_preserved_v4(
                   "fortran", lambda fixture: fixture["report"]["build_phases"][1]
                   ["native_outputs"]["engine"].update(
                       {"sha256": fixture["report"]["build_phases"][0]
                        ["native_outputs"]["engine"]["sha256"]})))
        reject("fortran-reject-resealed-omitted-complete-second-phase",
               lambda: attack_synthetic_preserved_v4(
                   "fortran", lambda fixture: fixture["report"]["build_phases"].pop()))
        for family in FAMILIES:
            complete_fixture = synthetic_build_fixture(family)
            accept(family + "-complete-resealed-two-phase-v4-build-proof",
                   set(validate_synthetic_fixture(complete_fixture))
                   == set(expected_roles(family)))
            pins = [path + "=" + digest
                    for path, (digest, _) in SOURCE_OWNERS[family].items()]
            accept(family + "-complete-exact-owned-semantic-source-pins",
                   set(parse_owner_pins(family, pins)) == set(SOURCE_OWNERS[family]))
            root = "/tmp/" + BUILD_PREFIX + family + "-synthetic"
            first, second = phase_paths(root, family, "reference-a"), phase_paths(
                root, family, "reference-b")
            accept(family + "-distinct-source-target-cache-output-and-working-roots",
                   first["source"] != second["source"]
                   and first["native"] != second["native"]
                   and first["temporary"] != second["temporary"]
                   and first["target"] != second["target"]
                   and first["zig_local_cache"] != second["zig_local_cache"]
                   and first["go_build_cache"] != second["go_build_cache"])
            commands = planned_commands(root, family, "reference-a")
            accept(family + "-pinned-offline-direct-compiler-command-graph",
                   bool(commands) and all(argv and argv[0].startswith("/")
                                          for argv in commands.values()))
            reject(family + "-reject-missing-semantic-source-owner",
                   lambda family=family, pins=pins:
                   parse_owner_pins(family, pins[:-1]))
            reject(family + "-reject-repeated-semantic-source-owner",
                   lambda family=family, pins=pins:
                   parse_owner_pins(family, pins[:-1] + [pins[0]]))
            sibling = next(name for name in FAMILIES if name != family)
            path, (digest, _) = next(iter(SOURCE_OWNERS[sibling].items()))
            reject(family + "-reject-cross-family-source-wrapper",
                   lambda family=family, pins=pins, path=path, digest=digest:
                   parse_owner_pins(family, pins[:-1] + [path + "=" + digest]))
            stale = pins.copy()
            stale[0] = stale[0].split("=", 1)[0] + "=" + "0" * 64
            reject(family + "-reject-modified-owned-source",
                   lambda family=family, stale=stale:
                   parse_owner_pins(family, stale))
            hashes = [role + "=" + synthetic_digest(family + "-" + role)
                      for role in expected_roles(family)]
            sizes = [role + "=" + str(64 + index)
                     for index, role in enumerate(expected_roles(family))]
            accept(family + "-explicit-exact-role-hashes-and-sizes",
                   set(parse_native_pins(family, hashes, sizes=False))
                   == set(parse_native_pins(family, sizes, sizes=True))
                   == set(expected_roles(family)))
            reject(family + "-reject-missing-native-role-digest",
                   lambda family=family, hashes=hashes:
                   parse_native_pins(family, hashes[:-1], sizes=False))
            reject(family + "-reject-missing-native-role-byte-count",
                   lambda family=family, sizes=sizes:
                   parse_native_pins(family, sizes[:-1], sizes=True))
            activation_root = "/tmp/" + PRIVATE_PREFIX + family + "-synthetic"
            accept(family + "-distinct-exact-owner-only-private-root-prefixes",
                   checked_private_root(root, family, build=True) == root
                   and checked_private_root(activation_root, family, build=False)
                   == activation_root)
            reject(family + "-reject-build-as-activation-root",
                   lambda family=family, root=root:
                   checked_private_root(root, family, build=False))
            reject(family + "-reject-activation-as-build-root",
                   lambda family=family, activation_root=activation_root:
                   checked_private_root(activation_root, family, build=True))
            reject(family + "-reject-resealed-failed-v4-build-report",
                   lambda family=family: attack_synthetic_build(
                       family, lambda fixture: fixture["report"].update(
                           {"status": "FAIL"})))
            reject(family + "-reject-resealed-foreign-v4-schema",
                   lambda family=family: attack_synthetic_build(
                       family, lambda fixture: fixture["report"].update(
                           {"schema": "rebar-phase2-independent-native-source-build-v3"})))
            reject(family + "-reject-resealed-missing-actual-process",
                   lambda family=family: attack_synthetic_build(
                       family, lambda fixture: fixture["report"]["processes"].pop()))
            reject(family + "-reject-resealed-reused-actual-process-id",
                   lambda family=family: attack_synthetic_build(
                       family, lambda fixture: fixture["report"]["processes"][1].update(
                           {"pid": fixture["report"]["processes"][0]["pid"]})))
            reject(family + "-reject-resealed-modified-compiler-command",
                   lambda family=family: attack_synthetic_build(
                       family, lambda fixture: fixture["report"]["processes"][0]["argv"].append(
                           "--unapproved")))
            reject(family + "-reject-resealed-corrupted-complete-compiler-output",
                   lambda family=family: attack_synthetic_build(
                       family, lambda fixture: fixture["report"]["processes"][0].update(
                           {"stdout_base64": base64.b64encode(b"forged").decode("ascii")})))
            reject(family + "-reject-resealed-missing-second-source-phase",
                   lambda family=family: attack_synthetic_build(
                       family, lambda fixture: fixture["report"]["build_phases"].pop()))
            reject(family + "-reject-resealed-false-reproducibility",
                   lambda family=family: attack_synthetic_build(
                       family, lambda fixture: fixture["report"]["reproducibility"].update(
                           {"byte_identical": False})))
            reject(family + "-reject-resealed-historical-zig-pass-relabel",
                   lambda family=family: attack_synthetic_build(
                       family, lambda fixture: next(
                           record for record in fixture["report"]["preserved_v2_history"]
                           if record["family"] == "zig").update(
                               {"build_status": "PASS"})))
            reject(family + "-reject-resealed-opened-build-holdout",
                   lambda family=family: attack_synthetic_build(
                       family, lambda fixture: fixture["report"].update(
                           {"hidden_cases_read": 1})))
        go_root = "/tmp/" + BUILD_PREFIX + "go-synthetic"
        go = planned_commands(go_root, "go", "reference-a")
        go_paths = phase_paths(go_root, "go", "reference-a")
        accept("go-fresh-generated-header-is-forced-in-owned-c-bridge",
               "-include" in go["build_go_bridge"]
               and sanitized(go_paths["artifact_generated_header"], go_root)
               in go["build_go_bridge"]
               and "-buildmode=c-shared" in go["build_go_engine"])
        go_env = expected_environment(go_root, "go", "reference-a")
        accept("go-offline-private-caches-never-contact-package-proxy",
               go_env["GOPROXY"] == "off" and go_env["GOSUMDB"] == "off"
               and go_env["GOENV"] == "off" and go_env["GOWORK"] == "off"
               and go_env["GOTOOLCHAIN"] == "local" and go_env["CC"] == PINNED_GCC)
        header = (b"/* Code generated by cmd/cgo; DO NOT EDIT. */\n"
                  + b"\n".join(("extern void " + name + "(void);").encode("ascii")
                               for name in sorted(GO_EXPORTS)) + b"\n")
        accept("go-generated-header-authenticates-all-nine-owned-exports",
               audit_go_header(header)["required_export_count"] == 9)
        for symbol in sorted(GO_EXPORTS):
            reject("go-reject-generated-header-without-" + symbol,
                   lambda symbol=symbol: audit_go_header(header.replace(
                       ("extern void " + symbol + "(void);\n").encode("ascii"), b"")))
        reject("go-reject-handwritten-foreign-generated-header",
               lambda: audit_go_header(header.replace(
                   b"Code generated by cmd/cgo; DO NOT EDIT.", b"not generated")))
        zig_root = "/tmp/" + BUILD_PREFIX + "zig-synthetic"
        zig = planned_commands(zig_root, "zig", "reference-a")["build_zig_engine"]
        accept("zig-official-compiler-retains-one-native-fstrip",
               zig[0] == PINNED_ZIG and zig.count("-fstrip") == 1
               and "--cache-dir" in zig and "--global-cache-dir" in zig)
        accept("exact-private-origin-native-dependency-parser",
               parse_dynamic(synthetic_dynamic(
                   needed=("_go_engine.so", "libc.so.6"), runpath="$ORIGIN"))
               ["runpath"] == ["$ORIGIN"])
        for family, entry in (("c", "PyInit__vm_native"),
                              ("cpp", "PyInit__cpp_bridge")):
            exports = (entry,) if family == "c" else (entry, "rebar_cpp_owned")
            dynamic = parse_dynamic(synthetic_dynamic(needed=("libc.so.6",)))
            symbols = parse_symbols(synthetic_symbols(exports))
            role = "extension" if family == "c" else "bridge"
            accept(family + "-exact-owned-native-entrypoint-and-elf",
                   validate_elf(family, role, dynamic, symbols)["required_exports"] == [entry])
        for family, exports in (("rust", RUST_EXPORTS), ("zig", ZIG_EXPORTS),
                                ("go", GO_EXPORTS), ("fortran", FORTRAN_EXPORTS)):
            filename = FAMILIES[family]["targets"]["engine"]
            dynamic = parse_dynamic(synthetic_dynamic(
                needed=("libc.so.6",), soname=filename))
            callbacks = tuple(sorted(FORTRAN_CALLBACKS)) if family == "fortran" else ()
            symbols = parse_symbols(synthetic_symbols(tuple(sorted(exports)), callbacks))
            accept(family + "-genuine-complete-owned-matching-symbols",
                   set(validate_elf(family, "engine", dynamic, symbols)
                       ["required_exports"]) == exports)
            entry = "PyInit__" + family + "_bridge"
            defined = ((entry, *tuple(sorted(FORTRAN_CALLBACKS)))
                       if family == "fortran" else (entry,))
            unresolved = (tuple(sorted(exports))
                          if family in {"go", "fortran"}
                          else (next(iter(sorted(exports))),))
            bridge_symbols = parse_symbols(synthetic_symbols(defined, unresolved))
            bridge_dynamic = parse_dynamic(synthetic_dynamic(
                needed=(filename, "libc.so.6"), runpath="$ORIGIN"))
            accept(family + "-exact-adjacent-owned-origin-bridge",
                   validate_elf(family, "bridge", bridge_dynamic, bridge_symbols)
                   ["runpath"] == ["$ORIGIN"])
            reject(family + "-reject-foreign-pcre-library",
                   lambda family=family, symbols=symbols, filename=filename:
                   validate_elf(family, "engine", parse_dynamic(synthetic_dynamic(
                       needed=("libpcre2-8.so.0",), soname=filename)), symbols))
            reject(family + "-reject-foreign-native-rpath",
                   lambda family=family, symbols=symbols, filename=filename:
                   validate_elf(family, "engine", parse_dynamic(synthetic_dynamic(
                       needed=("libc.so.6",), soname=filename, rpath="/tmp/foreign")),
                       symbols))
            reject(family + "-reject-foreign-bridge-runpath",
                   lambda family=family, bridge_symbols=bridge_symbols,
                   filename=filename: validate_elf(
                       family, "bridge", parse_dynamic(synthetic_dynamic(
                           needed=(filename, "libc.so.6"), runpath="/tmp/foreign")),
                       bridge_symbols))
            if family == "fortran":
                for callback in sorted(FORTRAN_CALLBACKS):
                    reduced = tuple(name for name in sorted(FORTRAN_CALLBACKS)
                                    if name != callback)
                    reject("fortran-reject-omitted-engine-reverse-callback-" + callback,
                           lambda dynamic=dynamic, exports=exports, reduced=reduced:
                           validate_elf("fortran", "engine", dynamic,
                                        parse_symbols(synthetic_symbols(
                                            tuple(sorted(exports)), reduced))))
        parsed = parse_symbols(synthetic_symbols(
            ("PyInit__vm_native",), ("malloc@GLIBC_2.2.5",)))
        accept("genuine-versioned-undefined-symbol-not-a-version-index",
               parsed["versioned_symbol_count"] == 1
               and "malloc" in parsed["undefined"])
        reject("reject-truncated-symbol-table",
               lambda: parse_symbols(synthetic_symbols(("PyInit__vm_native",))[:-1]))
        reject("reject-external-regex-dynamic-symbol",
               lambda: parse_symbols(synthetic_symbols(
                   ("PyInit__vm_native",), ("pcre2_match",))))
        accept("cpp-runtime-is-allowed-only-for-cpp-family",
               "libstdc++.so.6" in FAMILY_LIBRARIES["cpp"]
               and all("libstdc++.so.6" not in FAMILY_LIBRARIES[name]
                       for name in FAMILIES if name != "cpp"))
        accept("fortran-runtime-is-allowed-only-for-fortran-family",
               "libgfortran.so.5" in FAMILY_LIBRARIES["fortran"]
               and all("libgfortran.so.5" not in FAMILY_LIBRARIES[name]
                       for name in FAMILIES if name != "fortran"))
        exact = synthetic_owner("recovery-journal.json", seed="journal",
                                mode=0o600, durable=True,
                                root="/tmp/rebar-phase2-verified-native-activation-v4-go-synthetic")
        accept("owner-only-seven-field-durable-journal-identity",
               require_durable_owner(
                   exact, relative="recovery-journal.json",
                   root="/tmp/rebar-phase2-verified-native-activation-v4-go-synthetic",
                   directory_sync=True)["mode"] == 0o600)
        for flag in DURABLE_FLAGS:
            hostile = copy.deepcopy(exact)
            hostile[flag] = False
            reject("reject-undurable-recovery-owner-" + flag,
                   lambda hostile=hostile: require_durable_owner(
                       hostile, relative="recovery-journal.json",
                       root="/tmp/rebar-phase2-verified-native-activation-v4-go-synthetic",
                       directory_sync=True))
        for invalid in (True, False, 0, 1.0, "1"):
            hostile = copy.deepcopy(exact)
            hostile["write_calls"] = invalid
            reject("reject-untyped-false-write-count-" + repr(invalid),
                   lambda hostile=hostile: require_durable_owner(
                       hostile, relative="recovery-journal.json",
                       root="/tmp/rebar-phase2-verified-native-activation-v4-go-synthetic",
                       directory_sync=True))
        original = synthetic_owner("candidates/_go_engine.so", seed="original", mode=0o640)
        promoted = synthetic_owner("candidates/_go_engine.so", seed="promoted", mode=0o640)
        present = {"originally_present": True, "original_owner": original,
                   "promoted_sha256": promoted["sha256"],
                   "promoted_size_bytes": promoted["size_bytes"]}
        absent = {"originally_present": False, "original_owner": None,
                  "promoted_sha256": promoted["sha256"],
                  "promoted_size_bytes": promoted["size_bytes"]}
        accept("honest-original-0640-user-mode-preserved",
               classify_recovery_state(present, original) == "already-original"
               and original["mode"] == 0o640)
        accept("authenticate-reportless-genuine-promoted-inode",
               classify_recovery_state(present, promoted) == "source-verified-promoted")
        accept("honestly-record-originally-absent-target",
               classify_recovery_state(absent, None) == "originally-absent")
        modified = copy.deepcopy(promoted)
        modified["sha256"] = synthetic_digest("user-modified")
        reject("never-overwrite-or-remove-user-modified-canonical-target",
               lambda: classify_recovery_state(present, modified))
        reject("never-fabricate-a-missing-originally-present-file",
               lambda: classify_recovery_state(present, None))
        for field, value in (("schema", SCHEMA + "-wrong"),
                             ("version", 2), ("family_count", 5),
                             ("qualified_candidate_count", 1),
                             ("phase", "ACTIVATION AUTHORIZED")):
            hostile = copy.deepcopy(contract)
            hostile[field] = value
            reject("reject-substituted-source-contract-" + field,
                   lambda hostile=hostile: validate_contract(hostile))
        cpp_missing = copy.deepcopy(contract)
        cpp = next(item for item in cpp_missing["families"] if item["id"] == "cpp")
        cpp["owners"] = [item for item in cpp["owners"]
                         if item["path"] != "candidates/cpp/engine.hpp"]
        reject("reject-missing-independent-cpp-header",
               lambda: validate_contract(cpp_missing))
        poisoned_header = copy.deepcopy(contract)
        go_contract = next(item for item in poisoned_header["families"]
                           if item["id"] == "go")
        go_contract["promotion_targets"]["generated_header"] = "candidates/_go_engine.h"
        reject("reject-canonical-promotion-of-generated-go-header",
               lambda: validate_contract(poisoned_header))
        false_atomic = copy.deepcopy(contract)
        false_atomic["recovery_policy"]["target_promotion"] = "GROUP-ATOMIC"
        reject("reject-false-multi-file-group-atomicity",
               lambda: validate_contract(false_atomic))
        false_holdout = copy.deepcopy(contract)
        false_holdout["phase_boundary"]["hidden_cases_read"] = 1
        reject("reject-opened-performance-holdout",
               lambda: validate_contract(false_holdout))
        hidden_history = copy.deepcopy(contract)
        hidden_history["historical_candidate_evidence"]\
            ["total_distinct_evidence_owner_count"] = 17
        reject("reject-silently-reducing-fifty-seven-actual-evidence-owners",
               lambda: validate_contract(hidden_history))
        omitted_build = copy.deepcopy(contract)
        omitted_build["historical_candidate_evidence"]["published_v4_builds"].pop()
        reject("reject-omitting-a-real-preserved-v4-build-outcome",
               lambda: validate_contract(omitted_build))
        relabeled_go = copy.deepcopy(contract)
        next(item for item in relabeled_go["historical_candidate_evidence"]
             ["published_v4_builds"] if item["family"] == "go")[
                 "build_status"] = "PASS"
        reject("reject-relabeling-real-go-failure-as-a-passing-build",
               lambda: validate_contract(relabeled_go))
        relabeled_fortran = copy.deepcopy(contract)
        next(item for item in relabeled_fortran["historical_candidate_evidence"]
             ["published_v4_builds"] if item["family"] == "fortran")[
                 "build_status"] = "PASS"
        reject("reject-relabeling-real-fortran-reproducibility-failure-as-pass",
               lambda: validate_contract(relabeled_fortran))
        missing_v3_processes = copy.deepcopy(contract)
        missing_v3_processes["historical_candidate_evidence"][
            "historical_build_process_ledger"][
                "all_historical_build_process_count"] = 71
        reject("reject-describing-seventy-one-subtotal-as-all-eighty-six-processes",
               lambda: validate_contract(missing_v3_processes))
        false_global_pids = copy.deepcopy(contract)
        false_global_pids["historical_candidate_evidence"][
            "historical_build_process_ledger"][
                "unique_pid_scope"] = "GLOBAL ACROSS SEPARATE RUNS"
        reject("reject-invented-cross-run-global-process-identity",
               lambda: validate_contract(false_global_pids))
        reject("reject-duplicate-signed-json-keys",
               lambda: decode_document(b'{"target":1,"target":2}\n', "hostile"))
        reject("reject-nonfinite-signed-json",
               lambda: decode_document(b'{"target":NaN}\n', "hostile"))
        reject("reject-noncanonical-signed-json",
               lambda: decode_document(b'{ "target": 1 }\n', "hostile"))
        reject("reject-uppercase-hash", lambda: checked_digest("A" * 64, "hostile"))
        reject("reject-bool-native-size", lambda: checked_positive_size(True, "hostile"))
        for value in ("../outside", "/absolute", "a//b", "a/./b",
                      "a/../b", "a\\b", "a\x00b"):
            reject("reject-owned-path-attack-" + str(len(rejected)),
                   lambda value=value: checked_relative(value))
        reject("reject-hidden-readonly-flag",
               lambda: parse_arguments(["--verify-frozen-context", "--benchmark"]))
        reject("reject-unpinned-activation",
               lambda: parse_arguments(["--activate", "--family", "go"]))
        reject("reject-unpinned-reportless-recovery",
               lambda: parse_arguments(["--recover", "--family", "go"]))
        effect_actions: list[tuple[str, Any]] = [
            ("file-read", lambda: builtins.open("/forbidden", "rb")),
            ("file-stat", lambda: os.stat("/forbidden")),
            ("candidate-process", lambda: subprocess.run(["/usr/bin/false"])),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter_ns()),
            ("network", lambda: socket.socket()),
            ("candidate-import", lambda: importlib.import_module(
                "candidates.go_candidate"
            )),
            ("native-library", lambda: ctypes.CDLL("/foreign.so")),
            ("temporary-recovery-root", lambda: tempfile.mkdtemp()),
            ("canonical-promotion", lambda: os.replace("/foreign", "/target")),
            ("process-environment", lambda: os.environ.get("PATH")),
        ]
        if hasattr(time, "clock_gettime"):
            effect_actions.append((
                "clock-gettime",
                lambda: time.clock_gettime(time.CLOCK_REALTIME),
            ))
        if hasattr(time, "clock_gettime_ns"):
            effect_actions.append((
                "clock-gettime-ns",
                lambda: time.clock_gettime_ns(time.CLOCK_REALTIME),
            ))
        for name, action in effect_actions:
            reject("effect-wall-blocks-" + name, action)
        actual = ("actual_file_reads", "actual_file_writes", "actual_processes",
                  "actual_threads", "actual_clocks", "actual_network",
                  "actual_candidate_imports", "actual_native_library_loads",
                  "actual_holdout_reads", "actual_canonical_promotions",
                  "actual_recovery_roots")
        require(all(guard.counts[key] == 0 for key in actual),
                "synthetic activation controls performed a real external effect")
        require(all(guard.counts[key] > 0 for key in (
            "blocked_file_operations", "blocked_process_operations",
            "blocked_thread_operations", "blocked_clock_operations",
            "blocked_network_operations", "blocked_import_operations",
            "blocked_temporary_operations", "blocked_native_library_operations",
            "blocked_environment_operations", "blocked_promotion_operations")),
            "every forbidden real-effect wall must be independently exercised")
        counters = dict(guard.counts)
    return {"schema": SCHEMA + "-synthetic-source-only-self-test", "version": 4,
            "status": "PASS", "synthetic": True,
            "positive_control_count": len(accepted), "positive_controls": accepted,
            "rejected_attack_count": len(rejected), "rejected_attacks": rejected,
            "guard_counters": counters, "family_count": 6,
            "source_owner_count": 25,
            "historical_candidate_evidence_owner_count": 51,
            "historical_v4_build_evidence_owner_count": 6,
            "historical_v5_build_evidence_owner_count": 4,
            "historical_v6_build_evidence_owner_count": (
                2 * len(HISTORICAL_V6_RECORDS)
            ),
            "total_distinct_historical_evidence_owner_count": (
                expected_historical_evidence()[
                    "total_distinct_evidence_owner_count"
                ]
            ),
            "historical_build_process_ledger": expected_historical_evidence()[
                "historical_build_process_ledger"],
            "qualified_candidate_count": 0,
            "actual_v4_source_builds": "NOT RUN",
            "actual_v3_activations": "NOT RUN", **zero_effects()}


def main(arguments: list[str] | None = None) -> int:
    try:
        parsed = parse_arguments(list(sys.argv[1:] if arguments is None else arguments))
        if parsed["mode"] == "self-test":
            result, code = self_test(), 0
        elif parsed["mode"] == "verify-frozen-context":
            result = verify_frozen_context()
            code = 0 if result["status"] == "PASS" else 1
        elif parsed["mode"] == "activate":
            result, code = activate(parsed), 0
        else:
            result, code = recover(parsed), 0
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return code
    except (ActivationError, OSError, ValueError, UnicodeError, zlib.error) as error:
        sys.stderr.write(type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
