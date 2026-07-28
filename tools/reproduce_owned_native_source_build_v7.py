#!/usr/bin/env python3
"""Freeze six first-party engines and add authenticated first-party ELF forensics.

``--self-test`` is in-memory and effect-blocked. ``--verify-context`` is
strictly read-only. A compiler can run only through an independently pinned,
explicit ``--build`` after the exact V7 forensic source freeze is published.
"""

from __future__ import annotations

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
import struct
import subprocess
import sys
import tempfile
import threading
import time
import types
import zlib
from pathlib import Path
from typing import Any


ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
SOURCE_RELATIVE = "tools/reproduce_owned_native_source_build_v7.py"
PROTOCOL_RELATIVE = "oracle/phase2/NATIVE-SOURCE-BUILD-V7.md"
CONTRACT_RELATIVE = "oracle/phase2/native-source-build-v7.json"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-owned-native-source-build-v7"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
WORK_PREFIX = "rebar-phase2-native-build-v7-"
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
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
    "c": {"language": "C", "adapter_import": "_vm_native", "artifacts": {"extension": "_vm_native" + EXTENSION_SUFFIX}, "allowed_bridge_python_imports": ()},
    "rust": {"language": "Rust", "adapter_import": "_rust_bridge", "artifacts": {"engine": "_rust_engine.so", "bridge": "_rust_bridge" + EXTENSION_SUFFIX}, "allowed_bridge_python_imports": ("copyreg", "functools", "inspect")},
    "zig": {"language": "Zig", "adapter_import": "_zig_bridge", "artifacts": {"engine": "_zig_probe.so", "bridge": "_zig_bridge" + EXTENSION_SUFFIX}, "allowed_bridge_python_imports": ()},
    "cpp": {"language": "C++", "adapter_import": "_cpp_bridge", "artifacts": {"bridge": "_cpp_bridge" + EXTENSION_SUFFIX}, "allowed_bridge_python_imports": ("unicodedata",)},
    "go": {"language": "Go", "adapter_import": "_go_bridge", "artifacts": {"engine": "_go_engine.so", "bridge": "_go_bridge" + EXTENSION_SUFFIX, "generated_header": "_go_engine.h"}, "allowed_bridge_python_imports": ("unicodedata",)},
    "fortran": {"language": "Fortran", "adapter_import": "_fortran_bridge", "artifacts": {"engine": "_fortran_engine.so", "bridge": "_fortran_bridge" + EXTENSION_SUFFIX}, "allowed_bridge_python_imports": ()},
}

EXPECTED_TOOLCHAINS: dict[str, tuple[str, str, int, str, bool]] = {
    "python": (PINNED_PYTHON, "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016", 32387816, "CPython 3.14.6", True),
    "python_header": (PYTHON_INCLUDE + "/Python.h", "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f", 4399, "CPython 3.14.6", False),
    "python_patchlevel": (PYTHON_INCLUDE + "/patchlevel.h", "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95", 1773, "CPython 3.14.6", False),
    "gcc": (PINNED_GCC, "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26", 1023032, "GCC 13", True),
    "gxx": (PINNED_GXX, "1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769", 1027128, "G++ 13", True),
    "gfortran": (PINNED_GFORTRAN, "142861efc95f49e33705852027dae8c2e5382fd1155fcec6116ef973f25d8f84", 1027128, "GNU Fortran 13", True),
    "readelf": (PINNED_READELF, "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0", 789280, "GNU readelf", True),
    "go": (PINNED_GO, "d68b7abbc40d0844f673f6cf06ae3cded225c50437c6454fa37ef178d079fe65", 15434598, "go1.26.3 linux/amd64", True),
    "rustc": (PINNED_RUSTC, "bff349e72704ff70bc08a234a3847338e797065bbedde5e556808bc87b7bf7c6", 644784, "rustc 1.95.0", True),
    "cargo": (PINNED_CARGO, "841072d1d92f9e841d9ba5b0814182a0adf064acf4527cd120967b7bc49dcb66", 42185192, "cargo 1.95.0", True),
    "rust_driver": (RUST_TOOLCHAIN + "/lib/librustc_driver-6108105cd7e839cf.so", "ae69468875215df490fde685ec1f1b969743482ba7e0251f4074a222606a5484", 153621360, "rustc 1.95.0 compiler driver", False),
    "zig_archive": ("/tmp/rebar-zig-0.16.0-x86_64-linux.tar.xz", "70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00", 55478392, "official Zig 0.16.0 x86_64-linux", False),
    "zig": (PINNED_ZIG, "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c", 172641672, "official Zig 0.16.0", True),
}

EXPECTED_SUPPORT: dict[str, tuple[str, str, int]] = {
    "objective": ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756),
    "p0_manifest": ("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632),
    "p0_protocol": ("oracle/phase1/P0-COMPLETENESS-V1.md", "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798", 10392),
    "p0_verifier": ("tools/verify_p0_completeness_v1.py", "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c", 118040),
    "independence_protocol_v1": ("oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md", "a7ee45f0ea76ee7fedacc564c3122b7f37272d918ef28f1c527c9e8adf351292", 7127),
    "independence_auditor_v1": ("tools/audit_candidate_independence_v1.py", "f18d9b99a3f11fdf20c47d6cb43cb353532c894ababbdaeb7088c14e397ae3b5", 75793),
    "independence_auditor_v2": ("tools/audit_candidate_independence_v2.py", "57168db3df64414a7dc27f1793d9c22b7c493a8b37c025dc57243796e892d93c", 92309),
    "independence_protocol_v2": ("oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md", "80a1de729c067da36648dcfb9751f7bd3833ff561956df9ad82fc6106a19a16b", 6194),
    "independence_inventory_v2": ("oracle/phase2/candidate-independence-v2.json", "89662570a643d94ae1581393ed48015c6fa78d5dbe5ad0419e9a2032e4609659", 8798),
    "build_recorder_v2": ("tools/reproduce_phase2_native_builds_v2.py", "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796", 136677),
    "build_protocol_v2": ("oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md", "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603", 13032),
    "build_recorder_v3": ("tools/reproduce_phase2_native_builds_v3.py", "c33d8e89c4b86f06e7cc06ecef9bca7052af86191d2e09ac89e665500147ba6f", 175029),
    "build_protocol_v3": ("oracle/phase2/NATIVE-SOURCE-BUILDS-V3.md", "273e5de944b661ec1f5cfbe3a26bcabc2e9b8c04353891fcfb822b07955eace3", 7979),
    "official_zig_lock": ("toolchains/zig-0.16.0.lock.json", "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd", 628),
    "build_recorder_v4": ("tools/reproduce_owned_native_source_build_v4.py", "efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1", 136084),
    "build_protocol_v4": ("oracle/phase2/NATIVE-SOURCE-BUILD-V4.md", "e974b26562cc210c175c08cda7914e6b196fdee2ebe2a8232dd87c0cddbc0dfb", 10848),
    "build_contract_v4": ("oracle/phase2/native-source-build-v4.json", "0b5641529bc49f55b9e56fe397ad38e7e23d6c9b3376587b743753814b8089d7", 14354),
    "build_recorder_v5": ("tools/reproduce_owned_native_source_build_v5.py", "39ba55b6906a2aebf204c878c143894562f317765b0427f4f1f449e35e1dde92", 150006),
    "build_protocol_v5": ("oracle/phase2/NATIVE-SOURCE-BUILD-V5.md", "d2f7ca95cb0df377f4698399f56eea9eb0c237b0ad2f9e3790d74a0bee2246d9", 14294),
    "build_contract_v5": ("oracle/phase2/native-source-build-v5.json", "a54121391d43f5ee5e2debcdecf06567cb947d2e654142ba622c7adf0681ee11", 21391),
    "historical_candidate_graph_v7": ("docs/evidence/candidate-current-overview-v7.inputs.json", "744f86e241e3489cf07c5fccccf291eb68c44a50605d79723dd1ae1092d8511f", 22027),
    "historical_candidate_graph_v10": ("docs/evidence/candidate-current-overview-v10.inputs.json", "bfc68aa4f6c97d9e4571d4cd062cd1cb706d9d50fdd9f1ea6ccb329081037989", 32523),
    "build_recorder_v6": ("tools/reproduce_owned_native_source_build_v6.py", "2af9da3cb37a55782f3bfb8bdbdfdb7a945532994a5c988f4645d888dbe57ebc", 196660),
    "build_protocol_v6": ("oracle/phase2/NATIVE-SOURCE-BUILD-V6.md", "108dbd52144c78530221e36882a0070fe9805b1bef6a136caf4636148ae9131d", 10297),
    "build_contract_v6": ("oracle/phase2/native-source-build-v6.json", "0121aaa5902b449e107396d6a1107ca8fe0fefebb0a0f09eb58d2d19c8888db4", 29292),
    "historical_candidate_graph_v15": ("docs/evidence/candidate-current-overview-v15.inputs.json", "a5417c7fe0c7954a9a3e6791e20265512f681bdc3ab6e8178ae2cc0129c6ac82", 44240),
}

EXPECTED_HISTORY_V2: dict[str, dict[str, Any]] = {
    "c": {"family": "c", "build_status": "PASS", "archive_path": "oracle/phase2/evidence/native-source-build-v2-c-phase2-v2.json.gz", "archive_sha256": "4d954992312a039daa46a2810e51fc29cfdd2bd49d159dc834f5bf003e456878", "archive_bytes": 16016, "uncompressed_sha256": "0d0a67a3c8ebba83806ba3b9beaee39e154f9d0483f0e39aac6bb04ecbfc598a", "uncompressed_bytes": 169716, "receipt_path": "oracle/phase2/evidence/native-source-build-v2-c-phase2-v2-publication-receipt.json", "receipt_sha256": "e90b4c12a087c0e8864c1627e242be18bd779f9d9693ec711f7dd575288eda24", "receipt_bytes": 1639, "process_count": 8},
    "rust": {"family": "rust", "build_status": "PASS", "archive_path": "oracle/phase2/evidence/native-source-build-v2-rust-phase2-v2.json.gz", "archive_sha256": "69b645c14ca3e566256f5a5b393a6d18554ad347b97b542383db3d86681bb35d", "archive_bytes": 33741, "uncompressed_sha256": "389a833d6a3ce6c7aed3216759278d97d8d02dd901f758815e002f7a0031d4ec", "uncompressed_bytes": 279925, "receipt_path": "oracle/phase2/evidence/native-source-build-v2-rust-phase2-v2-publication-receipt.json", "receipt_sha256": "15580e4441ce651c21800df187fcfaa88ec9336322348a07d84544094d5b050e", "receipt_bytes": 2346, "process_count": 16},
    "zig": {"family": "zig", "build_status": "FAIL", "archive_path": "oracle/phase2/evidence/native-source-build-v2-zig-phase2-v2-failures.json.gz", "archive_sha256": "dc5128aaaf8a4d915c57ea8770696db3dc7ca51c89d5a3570cab9d259d070a0e", "archive_bytes": 19556, "uncompressed_sha256": "f6ea1eb57d9ceb23c6dc5d4f291c4eb300768460a658d97828b7ce0095c53652", "uncompressed_bytes": 188479, "receipt_path": "oracle/phase2/evidence/native-source-build-v2-zig-phase2-v2-failures-publication-receipt.json", "receipt_sha256": "97e3150e9b68d3031c96ea6e973097687c80163a371f99a67f8b3de08bc0707a", "receipt_bytes": 1766, "process_count": 15},
}

HISTORICAL_V4: dict[str, dict[str, Any]] = {
    "cpp": {
        "family": "cpp", "build_status": "PASS", "receipt_status": "PASS",
        "archive_path": "oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4.json.gz",
        "archive_sha256": "48910a6328e8aaacdac993b2c029995d878960a456359a14db5c83b9fc518df9",
        "archive_bytes": 20605,
        "uncompressed_sha256": "b0141e8d17dc5cafddd7e5a7901e1e2babb4822f0fff7cc7e1201ab625276243",
        "uncompressed_bytes": 175104,
        "receipt_path": "oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4-publication-receipt.json",
        "receipt_sha256": "7742eda3ce777b1378d0c7fb87fc064f222850ca8bcf15cd23ff8a4d87d8bebf",
        "receipt_bytes": 2074, "process_count": 10,
    },
    "go": {
        "family": "go", "build_status": "FAIL", "receipt_status": "PASS",
        "archive_path": "oracle/phase2/evidence/native-source-build-v4-go-phase2-v4-failures.json.gz",
        "archive_sha256": "fcf643b7b8e9fbe80bd3b40c7ed884695a844f46e1117f5ebdb130135e5db4bb",
        "archive_bytes": 4095,
        "uncompressed_sha256": "aded8de4563397acef41697abbb91d73c3214daa2054a0f118e4946bd982b105",
        "uncompressed_bytes": 12214,
        "receipt_path": "oracle/phase2/evidence/native-source-build-v4-go-phase2-v4-failures-publication-receipt.json",
        "receipt_sha256": "215e9680bbe0f8d2250fcca8bae0335017606288e13e7636224b7c76336b5e41",
        "receipt_bytes": 2075, "process_count": 4,
        "failed_process": "build_go_engine",
        "stderr_sha256": "4173a7583fe0358c92056da596f06837bd7a888aa56d6e66cb2920d806600862",
        "stderr_bytes": 175,
        "failure_cause": "PYTHON C BRIDGE WAS INCORRECTLY INCLUDED IN THE GO PACKAGE",
    },
    "fortran": {
        "family": "fortran", "build_status": "FAIL", "receipt_status": "PASS",
        "archive_path": "oracle/phase2/evidence/native-source-build-v4-fortran-phase2-v4-failures.json.gz",
        "archive_sha256": "ba35ea4f0d28814f716a36d2ccb384ef034a88a4029ca3f3cbf4f91eae268103",
        "archive_bytes": 14825,
        "uncompressed_sha256": "a0e72b44b40bf2dcc4e60d50a8996fa344ead3fa5d3056b3509de90260b3cfb1",
        "uncompressed_bytes": 140723,
        "receipt_path": "oracle/phase2/evidence/native-source-build-v4-fortran-phase2-v4-failures-publication-receipt.json",
        "receipt_sha256": "86b4b2648adf651481eea8d8b427a432f121c59322f508b522eca18af0749a08",
        "receipt_bytes": 2019,
        "process_count": 18,
        "successful_process_count": 18,
        "completed_build_phase_count": 2,
        "engine_phase_a_sha256": "37557a44033a80aa11a81fa145ca76c2bbd44ee544b31974dcf6e59ba0f2949c",
        "engine_phase_b_sha256": "696126d3f3e7239cac55975f53beb3b5e5cffc6948f08258817b6b2d86422199",
        "engine_bytes_per_phase": 74624,
        "identical_bridge_sha256": "eba8c1d145a53a2017fc9b7a6e4651b31ec4aef2e67e6c176c6435bffafc7b26",
        "bridge_bytes_per_phase": 37424,
        "failure_cause": "TWO COMPLETED OWNED ENGINE OUTPUTS WERE NOT BYTE IDENTICAL",
        "differing_binary_section": "NOT RECORDED",
    },
}

HISTORICAL_V5: dict[str, dict[str, Any]] = {
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


HISTORICAL_V6: dict[str, dict[str, Any]] = {
    "go": {
        "family": "go",
        "build_status": "PASS",
        "receipt_status": "PASS",
        "label": "phase2-v6",
        "archive_path": "oracle/phase2/evidence/native-source-build-v6-go-phase2-v6.json.gz",
        "archive_sha256": "05c24a5fff228d8eab8bec961d825b0e65504072e11e8c574ec580d9f3e6e245",
        "archive_bytes": 37619,
        "uncompressed_sha256": "37c97e72530ffc1022741429be2ffc9eebe7afaec6063c763d7ff86f6f7bd8ae",
        "uncompressed_bytes": 262323,
        "receipt_path": "oracle/phase2/evidence/native-source-build-v6-go-phase2-v6-publication-receipt.json",
        "receipt_sha256": "f3adcb20bb591946600e1e2b1db037fb3b4828c3d4a628a0347cfed40f262fca",
        "receipt_bytes": 3262,
        "process_count": 26,
        "successful_process_count": 26,
        "expected_process_count": 26,
        "completed_build_phase_count": 2,
        "engine_sha256": "38ab223b8ef88340a7be86f2195c417ee7d2dd9deead48cc6495a5b4e3c31b27",
        "engine_bytes": 2712912,
        "bridge_sha256": "dd71ab6cb15a98e1a07c38965cdb178da0dbba2a26db937975e0d6435a2a5d0c",
        "bridge_bytes": 41904,
        "generated_header_sha256": "481ebb65cc587749677ce28abeb4f3de111e2f87a18ac547ff0157fce85d2c23",
        "generated_header_bytes": 3086,
        "required_engine_export_count": 9,
        "private_go_package_member_count": 2,
        "differing_raw_binary_section": "NOT APPLICABLE; BYTE IDENTICAL",
    },
    "fortran": {
        "family": "fortran",
        "build_status": "FAIL",
        "receipt_status": "PASS",
        "label": "phase2-v6",
        "archive_path": "oracle/phase2/evidence/native-source-build-v6-fortran-phase2-v6-failures.json.gz",
        "archive_sha256": "c62007d5519d1ef723da7e144b1c6eeb067aacf47e960638e9d6b8a604f05d12",
        "archive_bytes": 26102,
        "uncompressed_sha256": "b8186f02586e134b5db4275688513670cad814526ce4b42cad50802ed9f2f32b",
        "uncompressed_bytes": 166999,
        "receipt_path": "oracle/phase2/evidence/native-source-build-v6-fortran-phase2-v6-failures-publication-receipt.json",
        "receipt_sha256": "6bc1ea1695247d8d137e6c2f50908b6c3a0518ff82978258bd07e8010e88ad7a",
        "receipt_bytes": 3221,
        "process_count": 26,
        "successful_process_count": 26,
        "expected_process_count": 26,
        "completed_build_phase_count": 2,
        "engine_phase_a_sha256": "6ed7afa0b7c2eb905cd00de0ec935a7c449f257431d44aaa652ae0f10191d1f7",
        "engine_phase_b_sha256": "1458072addc7988975317ac81d64748970ee3d4321437be73275a700fed831c9",
        "engine_bytes_per_phase": 74544,
        "identical_bridge_sha256": "f0808671b4d16f9b8d74a891d04ccd78bcf2e568ae2edbfb3997fb0db23c2fd7",
        "bridge_bytes_per_phase": 37424,
        "engine_phase_notes_bytes": 0,
        "engine_phase_notes_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "identical_engine_sections_sha256": "3f15407ebd8d72adb59d7ffc87f4c43195ed5417c595e92e05d941ad244992c3",
        "engine_sections_bytes_per_phase": 2833,
        "engine_build_id_status": "NOT PRESENT",
        "differing_raw_binary_section": "NOT RECORDED",
        "failure_cause": "the two independently owned outputs are not genuinely byte-identical",
    },
}



EXPECTED_OUTER: dict[str, dict[str, tuple[str, str]]] = {
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

ZIG_FAILURE_PAIRS: dict[str, dict[str, Any]] = {
    "candidate": {
        "archive": "oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-failures.json.gz",
        "archive_sha256": "2ca2a253e4148c4232327cf89f1306c1c4e83639714f3b036ebdd7bd0225aaa3",
        "archive_bytes": 850155,
        "plain_sha256": "2afa993835d45f30838971b5c68c397e9d6271877e77f32919aee955554ce9f6",
        "plain_bytes": 24903358,
        "receipt": "oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-failures-publication-receipt.json",
        "receipt_sha256": "72c2635850273543eded2e9f541cb64529f2ce22a9d6fe5b14c30705fa474c95",
        "receipt_bytes": 1145,
    },
    "worker": {
        "archive": "oracle/phase2/evidence/frozen-p0-candidate-worker-v4-zig-phase2-v6-failures.json.gz",
        "archive_sha256": "07a1be40b4aba273bdec1f5d567aad0c6fbbf860189ade527eb90cfed1aab594",
        "archive_bytes": 848777,
        "plain_sha256": "472f832152aab4550a635891b24415971171f8101e1171c010dc56cfc62751a0",
        "plain_bytes": 24899336,
        "receipt": "oracle/phase2/evidence/frozen-p0-candidate-worker-v4-zig-phase2-v6-failures-publication-receipt.json",
        "receipt_sha256": "8c5f69411600781dca1efd3965b98fcecf9a1fec00afb4e5f7d319c2afa86cf4",
        "receipt_bytes": 1159,
    },
    "subinterpreters": {
        "archive": "oracle/phase2/evidence/owned-candidate-subinterpreters-v3-zig-phase2-v6-subinterpreters-failures.json.gz",
        "archive_sha256": "ded1049f0d1979b6a71c80fcd86fe411e400603b02bbe28ed8b3634f513612f4",
        "archive_bytes": 104089,
        "plain_sha256": "a5280c4713fdc2e494f8e2bd0b1eeab9f6199dceede5d410bc1f8108e286cf67",
        "plain_bytes": 1581106,
        "receipt": "oracle/phase2/evidence/owned-candidate-subinterpreters-v3-zig-phase2-v6-subinterpreters-failures-publication-receipt.json",
        "receipt_sha256": "8fc8e0753458e69751fd45b820764e7c085ec6111c9dcda64ee90ef227b0ce21",
        "receipt_bytes": 1892,
    },
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
ZIG_RESTORATION = (
    "oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-restoration-receipt.json",
    "c415ba80c055d39a933617a839624037b557adbe30c418c2a0e859131fbe9028",
    2646,
)

GO_PRIVATE_MEMBERS: dict[str, str] = {
    "go.mod": "candidates/go/go.mod",
    "engine.go": "candidates/go/engine.go",
}
GO_FAILURE_STDERR = (
    b"# rebar.local/candidates/go\n"
    b"py_bridge.c:2:10: fatal error: Python.h: No such file or directory\n"
    b"    2 | #include <Python.h>\n"
    b"      |          ^~~~~~~~~~\n"
    b"compilation terminated.\n"
)

EXPECTED_PHASE_BOUNDARY: dict[str, Any] = {
    "native_builds_started": 0,
    "compiler_processes_started": 0,
    "candidate_processes_started": 0,
    "reference_processes_started": 0,
    "candidate_imports": 0,
    "native_libraries_loaded": 0,
    "network_requests": 0,
    "hidden_cases_read": 0,
    "final_cases_read": 0,
    "benchmark_files_read": 0,
    "clock_samples": 0,
    "timing_trials_run": 0,
    "qualified_candidate_count": 0,
    "candidate_correctness": "NOT MEASURED",
    "subinterpreter_isolation": "NOT MEASURED",
    "undefined_behavior": "NOT MEASURED",
    "performance": "NOT MEASURED",
    "memory": "NOT MEASURED",
    "holdout": "NOT OPENED",
    "winner_selected": False,
}

EXPECTED_BUILD_POLICY: dict[str, Any] = {
    "phase_names": ["reference-a", "reference-b"],
    "private_root_prefix": "/tmp/" + WORK_PREFIX,
    "private_root_mode": "0700",
    "phase_source_cache_target_output_and_process_identity": "DISTINCT",
    "all_phase_outputs": "BYTE IDENTICAL OR PRESERVE FAILURE",
    "argv_environment_working_directory_stdout_stderr_and_pid": "COMPLETE AND AUTHENTICATED",
    "elf_dynamic_symbols_and_versions": "COMPLETE AND AUTHENTICATED",
    "bridge_runpath": "$ORIGIN",
    "rpath": "FORBIDDEN",
    "zig_engine_strip_flag": "-fstrip",
    "go_build_mode": "c-shared",
    "go_generated_header": "FRESH, PHASE-OWNED, AUTHENTICATED, FORCED WITH -include, AND REPRODUCIBLE",
    "go_bridge_feature_test_macro": "-D_GNU_SOURCE",
    "go_bridge_feature_test_macro_count": 1,
    "go_bridge_feature_test_macro_order": "BEFORE THE EXACT AUTHENTICATED COMPILER-GENERATED HEADER",
    "rust_package_count": 1,
    "rust_external_package_count": 0,
    "go_module_count": 1,
    "go_external_package_count": 0,
    "network_requests": 0,
    "external_regular_expression_packages": 0,
    "cross_family_matching_dependencies": 0,
    "stdlib_matching_delegation": 0,
    "fallback": "FORBIDDEN",
    "prebuilt_artifact": "FORBIDDEN",
    "evidence_creation": "BOUNDED, EXCLUSIVE, CANONICAL, AND SYNCHRONIZED",
    "native_output_forensic_inspections": ["--sections --wide", "--notes --wide"],
    "fortran_fixed_compiler_random_seed": "rebar-fortran-v5",
    "fortran_complete_private_phase_root_maps": "BOTH PHASES; ONE CANONICAL PREFIX",
    "fortran_v5_seed_and_root_map_status": "ACTUALLY FALSIFIED; BOTH COMPLETE ENGINE FILES DIFFER",
    "fortran_engine_linker_build_id": "none",
    "fortran_engine_linker_build_id_flag": "-Wl,--build-id=none",
    "fortran_bridge_linker_build_id_flag": "-Wl,--build-id=sha1",
    "fortran_build_id_fix_status": "ACTUALLY FALSIFIED BY V6; RAW PAYLOAD NOT RECORDED",
    "fortran_reproducibility_fix_status": "ACTUALLY FALSIFIED BY V6; RAW PAYLOAD NOT RECORDED",
    "v7_future_process_count_by_family": {
        "c": 14, "rust": 28, "zig": 26, "cpp": 14, "go": 26, "fortran": 26,
    },
}


class BuildError(Exception):
    """The exact source, historical evidence, or private build failed closed."""


class SourceOnlyError(BuildError):
    """An in-memory source control tried to produce an external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise BuildError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise BuildError("require one finite, complete canonical JSON record") from error


def sha256(raw: Any) -> str:
    require(type(raw) is bytes, "hash only complete actual bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require an exact lowercase SHA-256: " + label)
    return value


def checked_family(value: Any) -> str:
    require(type(value) is str and value in FAMILIES,
            "select exactly one owned C, Rust, Zig, C++, Go, or Fortran family")
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512
            and not value.startswith("/") and "\\" not in value and "\x00" not in value
            and all(part not in ("", ".", "..") for part in value.split("/")),
            "reject an absolute, traversing, empty, or redirected owned path")
    return value


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL_BYTES
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(char in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in value)
            and "--" not in value and not value.endswith("-"),
            "require one fresh bounded lowercase V6 evidence label")
    return value


def unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject a duplicated or non-string signed JSON field")
        result[key] = value
    return result


def reject_json_constant(value: str) -> Any:
    raise BuildError("reject non-finite JSON: " + value)


def decode_json(raw: Any, *, canonical_required: bool = False) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_REPORT_BYTES,
            "require one complete bounded UTF-8 JSON object")
    try:
        result = json.loads(raw.decode("utf-8"),
                            object_pairs_hook=unique_json_pairs,
                            parse_constant=reject_json_constant)
    except (UnicodeError, ValueError, RecursionError) as error:
        raise BuildError("reject invalid, truncated, or duplicated JSON") from error
    require(type(result) is dict, "require a top-level JSON object")
    if canonical_required:
        require(canonical(result) == raw, "the exact canonical document changed")
    return result


def expected_oracle() -> dict[str, Any]:
    return {
        "implementation": "CPython",
        "version": "3.14.6",
        "suite_count": 13,
        "case_execution_count": 31237,
        "manifest_path": EXPECTED_SUPPORT["p0_manifest"][0],
        "manifest_sha256": EXPECTED_SUPPORT["p0_manifest"][1],
    }


def expected_go_private_package() -> dict[str, Any]:
    return {
        "phase_relative_directory": "go-engine-package",
        "member_count": 2,
        "members": [
            {"package_name": name, "source_path": path,
             "source_sha256": SOURCE_OWNERS["go"][path][0],
             "source_bytes": SOURCE_OWNERS["go"][path][1]}
            for name, path in GO_PRIVATE_MEMBERS.items()
        ],
        "excluded_package_members": ["py_bridge.c", "Python.h"],
        "bridge_source_path": "candidates/go/py_bridge.c",
        "engine_command_working_directory": "PHASE-PRIVATE EXACT TWO-FILE GO MODULE",
        "bridge_command_working_directory": "PHASE-PRIVATE BUILD ROOT",
        "generated_header_filename": "_go_engine.h",
        "generated_header_forced_include": True,
        "bridge_feature_test_macro": "-D_GNU_SOURCE",
        "bridge_feature_test_macro_count": 1,
        "bridge_feature_test_macro_before_generated_header": True,
        "required_export_count": 9,
        "external_package_count": 0,
        "source_snapshot_and_package_inodes": "DISTINCT",
        "previous_v4_failure": "PRESERVED; NOT A PASS",
    }



ELF64_HEADER = struct.Struct("<16sHHIQQQIHHHHHH")
ELF64_PROGRAM = struct.Struct("<IIQQQQQQ")
ELF64_SECTION = struct.Struct("<IIQQQQIIQQ")
ELF64_SYMBOL = struct.Struct("<IBBHQQ")
ELF64_DYNAMIC = struct.Struct("<qQ")
ELF64_VERDEF = struct.Struct("<HHHHIII")
ELF64_VERDAUX = struct.Struct("<II")
ELF64_VERNEED = struct.Struct("<HHIII")
ELF64_VERNAUX = struct.Struct("<IHHII")
ELF64_NOTE = struct.Struct("<III")
ELF64_COMPRESSED = struct.Struct("<IIQQ")
ELF64_MAX_SECTIONS = 131072
ELF64_MAX_PROGRAMS = 4096
ELF64_MAX_SYMBOLS = 1048576
ELF64_MAX_STRING_BYTES = 4096
MAX_REPORTED_DIFFERENCE_SPANS = 64
MAX_DIFFERENCE_PREVIEW_BYTES = 32
SHT_NULL = 0
SHT_PROGBITS = 1
SHT_SYMTAB = 2
SHT_STRTAB = 3
SHT_RELA = 4
SHT_DYNAMIC = 6
SHT_NOTE = 7
SHT_NOBITS = 8
SHT_REL = 9
SHT_DYNSYM = 11
SHT_SYMTAB_SHNDX = 18
SHT_RELR = 19
SHT_GNU_VERDEF = 0x6FFFFFFD
SHT_GNU_VERNEED = 0x6FFFFFFE
SHT_GNU_VERSYM = 0x6FFFFFFF
SHF_COMPRESSED = 0x800
SHN_XINDEX = 0xFFFF
PN_XNUM = 0xFFFF
ELFCLASS64 = 2
ELFDATA2LSB = 1


def checked_elf_span(
    offset: Any, size: Any, limit: int, label: str,
) -> tuple[int, int]:
    require(type(limit) is int and 0 <= limit <= MAX_BINARY_BYTES,
            "require one independently bounded complete native ELF")
    require(type(offset) is int and type(size) is int
            and 0 <= offset <= limit and 0 <= size <= limit - offset,
            "reject a truncated, overflowing, or escaped ELF " + label)
    return offset, offset + size


def bounded_elf_string(raw: bytes, offset: Any, label: str) -> str:
    require(type(raw) is bytes and type(offset) is int
            and 0 <= offset < len(raw),
            "reject an out-of-bounds native ELF " + label)
    end = raw.find(b"\x00", offset, min(len(raw), offset + ELF64_MAX_STRING_BYTES + 1))
    require(end >= offset and end - offset <= ELF64_MAX_STRING_BYTES,
            "reject an unterminated or oversized native ELF " + label)
    value = raw[offset:end]
    try:
        result = value.decode("utf-8", "strict")
    except UnicodeError as error:
        raise BuildError("reject a non-UTF-8 native ELF " + label) from error
    require(not any(ord(character) < 32 for character in result),
            "reject a control character in native ELF " + label)
    return result


def _elf_payload(raw: bytes, section: dict[str, Any]) -> bytes:
    require(type(section) is dict and section.get("storage") == "FILE",
            "never invent file bytes for an ELF NOBITS section")
    left, right = checked_elf_span(
        section.get("file_offset"), section.get("file_size"), len(raw),
        "section payload",
    )
    result = raw[left:right]
    require(len(result) == section["file_size"]
            and sha256(result) == section["payload_sha256"],
            "the genuine independently authenticated ELF payload changed")
    return result


def _elf_table_count(
    offset: Any, count: Any, size: int, total: int, maximum: int, label: str,
) -> tuple[int, int]:
    require(type(offset) is int and type(count) is int and type(size) is int
            and 0 <= offset <= total and 0 <= count <= maximum
            and count <= (total - offset) // size,
            "reject an oversized, truncated, or overflowed native ELF " + label)
    return checked_elf_span(offset, count * size, total, label)


def _elf_dynamic_records(
    raw: bytes, sections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for section in sections:
        if section["type"] != SHT_DYNAMIC:
            continue
        require(section["entry_size"] == ELF64_DYNAMIC.size
                and section["file_size"] % ELF64_DYNAMIC.size == 0
                and 0 < section["link"] < len(sections)
                and sections[section["link"]]["type"] == SHT_STRTAB,
                "reject a forged, unlinked, or truncated dynamic ELF table")
        payload = _elf_payload(raw, section)
        strings = _elf_payload(raw, sections[section["link"]])
        require(bool(strings) and strings[0] == 0,
                "authenticate the exact dynamic string table")
        found_null = False
        entries: list[dict[str, Any]] = []
        singletons: set[int] = set()
        for position in range(0, len(payload), ELF64_DYNAMIC.size):
            tag, value = ELF64_DYNAMIC.unpack_from(payload, position)
            if tag == 0:
                found_null = True
                require(all(item == 0 for item in payload[position:]),
                        "reject bytes after the actual native ELF DT_NULL")
                break
            item: dict[str, Any] = {"tag": tag, "value": value}
            if tag in (1, 14, 15, 29):
                item["name"] = bounded_elf_string(strings, value, "dynamic owner name")
            if tag in (5, 6, 10, 11, 14, 15, 29, 0x6FFFFFF0,
                       0x6FFFFFFC, 0x6FFFFFFD, 0x6FFFFFFE, 0x6FFFFFFF):
                require(tag not in singletons,
                        "reject a repeated singleton native ELF dynamic tag")
                singletons.add(tag)
            entries.append(item)
        require(found_null,
                "require a bounded, complete, terminating native ELF dynamic table")
        records.append({"section_index": section["index"],
                        "section_name": section["name"],
                        "entries": entries})
    return records


def _elf_symbol_records(
    raw: bytes, sections: list[dict[str, Any]],
) -> dict[str, Any]:
    shndx_tables: dict[int, dict[str, Any]] = {}
    for item in sections:
        if item["type"] == SHT_SYMTAB_SHNDX:
            require(item["entry_size"] == 4
                    and item["file_size"] % 4 == 0
                    and 0 < item["link"] < len(sections)
                    and sections[item["link"]]["type"] in (SHT_SYMTAB, SHT_DYNSYM)
                    and item["link"] not in shndx_tables,
                    "reject a reused or invalid ELF extended-symbol-index table")
            shndx_tables[item["link"]] = item
    tables: list[dict[str, Any]] = []
    for section in sections:
        if section["type"] not in (SHT_SYMTAB, SHT_DYNSYM):
            continue
        require(section["entry_size"] == ELF64_SYMBOL.size
                and section["file_size"] % ELF64_SYMBOL.size == 0
                and 0 < section["link"] < len(sections)
                and sections[section["link"]]["type"] == SHT_STRTAB,
                "reject a truncated, unlinked, or forged ELF symbol table")
        payload = _elf_payload(raw, section)
        count = len(payload) // ELF64_SYMBOL.size
        require(count <= ELF64_MAX_SYMBOLS,
                "bound every independently owned ELF symbol")
        names = _elf_payload(raw, sections[section["link"]])
        require(bool(names) and names[0] == 0,
                "require the authentic NUL-rooted ELF symbol string table")
        extension = shndx_tables.get(section["index"])
        extended = _elf_payload(raw, extension) if extension is not None else None
        require(extended is None or len(extended) // 4 == count,
                "require one exact extended section index for each actual symbol")
        symbols: list[dict[str, Any]] = []
        for number in range(count):
            name_offset, info, other, index, value, size = (
                ELF64_SYMBOL.unpack_from(payload, number * ELF64_SYMBOL.size)
            )
            if index == SHN_XINDEX:
                require(extended is not None,
                        "reject a symbol with no actual extended section index")
                index = struct.unpack_from("<I", extended, number * 4)[0]
            if index < 0xFF00:
                require(index < len(sections),
                        "reject an escaped or invented symbol section index")
            symbol_name = bounded_elf_string(names, name_offset, "symbol name")
            if number == 0:
                require(name_offset == info == other == index == value == size == 0,
                        "authenticate the exact null ELF symbol")
            symbols.append({
                "index": number, "name": symbol_name,
                "binding": info >> 4, "type": info & 0x0F,
                "visibility": other & 0x03,
                "section_index": index, "value": value, "size": size,
            })
        tables.append({
            "section_index": section["index"],
            "section_name": section["name"],
            "linked_string_section_index": section["link"],
            "symbol_count": count,
            "symbols": symbols,
        })
    return {"tables": tables, "table_count": len(tables)}


def _elf_version_records(
    raw: bytes, sections: list[dict[str, Any]],
    symbols: dict[str, Any],
) -> dict[str, Any]:
    symbol_counts = {
        item["section_index"]: item["symbol_count"]
        for item in symbols["tables"]
    }
    established: set[int] = {0, 1}
    definitions: list[dict[str, Any]] = []
    needs: list[dict[str, Any]] = []
    versyms: list[dict[str, Any]] = []
    for section in sections:
        if section["type"] not in (
            SHT_GNU_VERDEF, SHT_GNU_VERNEED, SHT_GNU_VERSYM,
        ):
            continue
        require(0 < section["link"] < len(sections),
                "reject an unlinked genuine ELF symbol-version section")
        payload = _elf_payload(raw, section)
        if section["type"] == SHT_GNU_VERSYM:
            require(sections[section["link"]]["type"] == SHT_DYNSYM
                    and section["entry_size"] == 2
                    and len(payload) % 2 == 0
                    and len(payload) // 2 == symbol_counts.get(section["link"]),
                    "reject a changed or cross-linked ELF dynamic version array")
            entries = []
            for offset in range(0, len(payload), 2):
                encoded = struct.unpack_from("<H", payload, offset)[0]
                entries.append({
                    "index": offset // 2,
                    "version_index": encoded & 0x7FFF,
                    "hidden": bool(encoded & 0x8000),
                })
            versyms.append({
                "section_index": section["index"],
                "symbol_table_index": section["link"],
                "entries": entries,
            })
            continue
        require(sections[section["link"]]["type"] == SHT_STRTAB,
                "require authentic version names from one owned string table")
        strings = _elf_payload(raw, sections[section["link"]])
        require(bool(strings) and strings[0] == 0,
                "require a genuine version string table")
        count = section["info"]
        require(type(count) is int and 0 <= count <= ELF64_MAX_SECTIONS,
                "bound the complete GNU ELF version chain")
        cursor = 0
        visited: set[int] = set()
        chain: list[dict[str, Any]] = []
        for number in range(count):
            require(cursor not in visited,
                    "reject a cyclic native ELF symbol-version chain")
            visited.add(cursor)
            if section["type"] == SHT_GNU_VERDEF:
                left, _ = checked_elf_span(
                    cursor, ELF64_VERDEF.size, len(payload), "version definition",
                )
                version, flags, index, auxiliaries, name_hash, aux, following = (
                    ELF64_VERDEF.unpack_from(payload, left)
                )
                require(version == 1 and 0 < auxiliaries <= ELF64_MAX_SECTIONS
                        and index >= 1,
                        "reject an invalid native ELF version definition")
                established.add(index & 0x7FFF)
                auxiliary_offset = cursor + aux
                names: list[str] = []
                auxiliary_seen: set[int] = set()
                for which in range(auxiliaries):
                    require(auxiliary_offset not in auxiliary_seen,
                            "reject a cyclic native ELF version-definition auxiliary")
                    auxiliary_seen.add(auxiliary_offset)
                    start, _ = checked_elf_span(
                        auxiliary_offset, ELF64_VERDAUX.size, len(payload),
                        "version-definition auxiliary",
                    )
                    name_offset, next_aux = ELF64_VERDAUX.unpack_from(payload, start)
                    names.append(bounded_elf_string(strings, name_offset,
                                                    "version-definition name"))
                    if which + 1 < auxiliaries:
                        require(next_aux > 0 and next_aux % 4 == 0,
                                "reject a truncated version-definition auxiliary chain")
                        auxiliary_offset += next_aux
                    else:
                        require(next_aux == 0,
                                "reject an overlong version-definition auxiliary chain")
                chain.append({
                    "ordinal": number, "index": index,
                    "flags": flags, "hash": name_hash, "names": names,
                })
            else:
                left, _ = checked_elf_span(
                    cursor, ELF64_VERNEED.size, len(payload), "version requirement",
                )
                version, auxiliaries, file_offset, aux, following = (
                    ELF64_VERNEED.unpack_from(payload, left)
                )
                require(version == 1 and 0 < auxiliaries <= ELF64_MAX_SECTIONS,
                        "reject an invalid native ELF version requirement")
                dependency = bounded_elf_string(strings, file_offset,
                                                "version dependency")
                auxiliary_offset = cursor + aux
                entries: list[dict[str, Any]] = []
                auxiliary_seen = set()
                for which in range(auxiliaries):
                    require(auxiliary_offset not in auxiliary_seen,
                            "reject a cyclic native ELF version-requirement auxiliary")
                    auxiliary_seen.add(auxiliary_offset)
                    start, _ = checked_elf_span(
                        auxiliary_offset, ELF64_VERNAUX.size, len(payload),
                        "version-requirement auxiliary",
                    )
                    name_hash, flags, index, name_offset, next_aux = (
                        ELF64_VERNAUX.unpack_from(payload, start)
                    )
                    require((index & 0x7FFF) > 1,
                            "reject a reserved genuine version requirement")
                    established.add(index & 0x7FFF)
                    entries.append({
                        "index": index & 0x7FFF,
                        "hidden": bool(index & 0x8000),
                        "flags": flags, "hash": name_hash,
                        "name": bounded_elf_string(
                            strings, name_offset, "required symbol version",
                        ),
                    })
                    if which + 1 < auxiliaries:
                        require(next_aux > 0 and next_aux % 4 == 0,
                                "reject a truncated version-requirement auxiliary chain")
                        auxiliary_offset += next_aux
                    else:
                        require(next_aux == 0,
                                "reject an overlong version-requirement auxiliary chain")
                chain.append({"ordinal": number, "file": dependency,
                              "versions": entries})
            if number + 1 < count:
                require(following > 0 and following % 4 == 0,
                        "reject a truncated native ELF version chain")
                cursor += following
            else:
                require(following == 0,
                        "reject extra entries after the complete ELF version chain")
        require(count > 0 or not payload,
                "reject unaccounted native ELF symbol-version bytes")
        entry = {"section_index": section["index"],
                 "linked_string_section_index": section["link"],
                 "entries": chain}
        if section["type"] == SHT_GNU_VERDEF:
            definitions.append(entry)
        else:
            needs.append(entry)
    for entry in versyms:
        for item in entry["entries"]:
            require(item["version_index"] in established,
                    "reject a dangling or fabricated dynamic-symbol version")
    return {
        "definitions": definitions, "requirements": needs,
        "dynamic_symbol_versions": versyms,
        "established_version_indexes": sorted(established),
    }


def parse_owned_elf64(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and ELF64_HEADER.size <= len(raw) <= MAX_BINARY_BYTES,
            "parse only complete bounded first-party ELF64 artifact bytes")
    unpacked = ELF64_HEADER.unpack_from(raw, 0)
    (identity, kind, machine, version, entry, program_offset, section_offset,
     flags, header_size, program_size, program_count_raw,
     section_size, section_count_raw, names_index_raw) = unpacked
    require(identity[:4] == b"\x7fELF"
            and identity[4] == ELFCLASS64
            and identity[5] == ELFDATA2LSB
            and identity[6] == 1 and identity[7] in (0, 3)
            and identity[8] == 0 and identity[9:] == bytes(7)
            and kind == 3 and machine == 62 and version == 1
            and header_size == ELF64_HEADER.size
            and section_size == ELF64_SECTION.size,
            "reject a foreign, truncated, noncanonical, or non-ELF64 native artifact")
    require(section_offset >= ELF64_HEADER.size
            and section_offset <= len(raw) - ELF64_SECTION.size,
            "require the actual bounded first native ELF section header")
    initial = ELF64_SECTION.unpack_from(raw, section_offset)
    require(initial[0] == 0 and initial[1] == SHT_NULL
            and initial[2] == 0 and initial[3] == 0
            and initial[4] == 0 and initial[8] == 0
            and initial[9] == 0,
            "reject an inauthentic native ELF null section")
    if section_count_raw == 0:
        section_count = initial[5]
        require(0xFF00 <= section_count <= ELF64_MAX_SECTIONS,
                "reject a forged or unbounded extended ELF section count")
    else:
        section_count = section_count_raw
        require(initial[5] == 0 and section_count < 0xFF00,
                "reject a contradictory extended ELF section count")
    if names_index_raw == SHN_XINDEX:
        names_index = initial[6]
        require(names_index >= 0xFF00 and names_index < section_count,
                "reject a forged extended ELF string-table index")
    else:
        names_index = names_index_raw
        require(initial[6] == 0,
                "reject a contradictory ELF extended string-table index")
    if program_count_raw == PN_XNUM:
        program_count = initial[7]
        require(PN_XNUM <= program_count <= ELF64_MAX_PROGRAMS,
                "reject a forged extended ELF program-header count")
    else:
        program_count = program_count_raw
        require(initial[7] == 0,
                "reject a contradictory ELF extended program-header count")
    require(0 < names_index < section_count,
            "require one genuine in-range ELF section-name string table")
    section_start, section_end = _elf_table_count(
        section_offset, section_count, ELF64_SECTION.size,
        len(raw), ELF64_MAX_SECTIONS, "section-header table",
    )
    programs: list[dict[str, Any]] = []
    if program_count:
        require(program_size == ELF64_PROGRAM.size,
                "reject a forged ELF64 program-header entry size")
        program_start, program_end = _elf_table_count(
            program_offset, program_count, ELF64_PROGRAM.size,
            len(raw), ELF64_MAX_PROGRAMS, "program-header table",
        )
        require(program_start >= ELF64_HEADER.size
                and (program_end <= section_start or program_start >= section_end),
                "reject an ELF program table overlapping genuine structural metadata")
        for number in range(program_count):
            item = ELF64_PROGRAM.unpack_from(
                raw, program_start + number * ELF64_PROGRAM.size,
            )
            kind_value, permissions, offset, virtual, physical, files, memory, align = item
            checked_elf_span(offset, files, len(raw), "program segment")
            require(memory >= files and (align in (0, 1)
                    or align & (align - 1) == 0),
                    "reject a forged ELF segment size or alignment")
            programs.append({
                "index": number, "type": kind_value,
                "flags": permissions, "file_offset": offset,
                "virtual_address": virtual, "physical_address": physical,
                "file_size": files, "memory_size": memory,
                "alignment": align,
            })
    else:
        require(program_size in (0, ELF64_PROGRAM.size)
                and program_offset in (0, ELF64_HEADER.size),
                "reject a forged empty native ELF program table")
        program_start = program_end = 0
    parsed: list[tuple[int, int, int, int, int, int, int, int, int, int]] = []
    for number in range(section_count):
        parsed.append(ELF64_SECTION.unpack_from(
            raw, section_start + number * ELF64_SECTION.size,
        ))
    name_row = parsed[names_index]
    require(name_row[1] == SHT_STRTAB and name_row[1] != SHT_NOBITS,
            "authenticate the exact first-party ELF section-name table")
    begin, end = checked_elf_span(
        name_row[4], name_row[5], len(raw), "section-name string table",
    )
    name_bytes = raw[begin:end]
    require(bool(name_bytes) and name_bytes[0] == 0,
            "require a bounded NUL-rooted genuine ELF section-name table")
    sections: list[dict[str, Any]] = []
    intervals: list[tuple[int, int, str]] = [
        (0, ELF64_HEADER.size, "ELF_HEADER"),
        (section_start, section_end, "SECTION_HEADER_TABLE"),
    ]
    if program_count:
        intervals.append((program_start, program_end, "PROGRAM_HEADER_TABLE"))
    for number, item in enumerate(parsed):
        (name_offset, section_type, section_flags, address, offset, size,
         link, info, alignment, entry_size) = item
        name = "" if number == 0 else bounded_elf_string(
            name_bytes, name_offset, "section name",
        )
        require(alignment in (0, 1) or alignment & (alignment - 1) == 0,
                "reject an invalid genuine ELF section alignment")
        require(link < section_count,
                "reject a foreign or escaped native ELF section link")
        file_backed = number > 0 and section_type != SHT_NOBITS
        if number == 0:
            require(name == "" and section_type == SHT_NULL,
                    "reject a forged native ELF null section identity")
            file_size = 0
            payload_digest = None
            storage = "NULL"
        elif section_type == SHT_NOBITS:
            require(offset <= len(raw),
                    "reject an escaped memory-only native ELF section")
            file_size = 0
            payload_digest = None
            storage = "NOBITS"
            require(not section_flags & SHF_COMPRESSED,
                    "reject an impossible compressed NOBITS section")
        else:
            left, right = checked_elf_span(
                offset, size, len(raw), "section " + name,
            )
            payload = raw[left:right]
            file_size = size
            payload_digest = sha256(payload)
            storage = "FILE"
            if size:
                intervals.append((left, right, "SECTION:" + str(number) + ":" + name))
        fixed = {
            SHT_SYMTAB: ELF64_SYMBOL.size,
            SHT_DYNSYM: ELF64_SYMBOL.size,
            SHT_DYNAMIC: ELF64_DYNAMIC.size,
            SHT_RELA: 24, SHT_REL: 16,
            SHT_SYMTAB_SHNDX: 4,
            SHT_GNU_VERSYM: 2,
            SHT_RELR: 8,
        }
        if section_type in fixed and number:
            require(entry_size == fixed[section_type]
                    and size % fixed[section_type] == 0,
                    "reject a forged fixed-width native ELF section")
        if section_flags & SHF_COMPRESSED:
            require(file_backed and file_size >= ELF64_COMPRESSED.size,
                    "reject a truncated compressed native ELF section")
            compression, reserved, expanded_size, expanded_alignment = (
                ELF64_COMPRESSED.unpack_from(raw, offset)
            )
            require(compression == 1 and reserved == 0
                    and 0 <= expanded_size <= MAX_BINARY_BYTES
                    and (expanded_alignment in (0, 1)
                         or expanded_alignment & (expanded_alignment - 1) == 0),
                    "reject an unsupported or unsafe compressed native ELF section")
            compressed = raw[
                offset + ELF64_COMPRESSED.size:offset + file_size
            ]
            try:
                decoder = zlib.decompressobj()
                expanded = decoder.decompress(compressed, expanded_size + 1)
                require(decoder.eof and not decoder.unconsumed_tail
                        and not decoder.unused_data
                        and len(expanded) == expanded_size,
                        "reject a bomb, trailing data, or forged ELF section decompression")
                expanded += decoder.flush()
            except (zlib.error, ValueError) as error:
                raise BuildError(
                    "reject an invalid compressed native ELF section"
                ) from error
            require(len(expanded) == expanded_size,
                    "reject an inauthentic expanded native ELF section")
            compressed_detail: dict[str, Any] | None = {
                "algorithm": "ZLIB",
                "expanded_size": expanded_size,
                "expanded_sha256": sha256(expanded),
                "expanded_alignment": expanded_alignment,
            }
        else:
            compressed_detail = None
        sections.append({
            "index": number, "name": name, "type": section_type,
            "flags": section_flags, "address": address,
            "file_offset": offset, "logical_size": size,
            "file_size": file_size, "link": link, "info": info,
            "alignment": alignment, "entry_size": entry_size,
            "storage": storage, "payload_sha256": payload_digest,
            "compression": compressed_detail,
        })
    intervals.sort(key=lambda row: (row[0], row[1], row[2]))
    previous = 0
    covered: list[dict[str, Any]] = []
    for left, right, label in intervals:
        require(left >= previous,
                "reject aliased or overlapping real ELF metadata and section bytes")
        if left > previous:
            covered.append({
                "start": previous, "end": left, "kind": "UNCLAIMED_BYTES",
                "sha256": sha256(raw[previous:left]),
            })
        covered.append({
            "start": left, "end": right, "kind": label,
            "sha256": sha256(raw[left:right]),
        })
        previous = right
    if previous < len(raw):
        covered.append({
            "start": previous, "end": len(raw), "kind": "TRAILING_BYTES",
            "sha256": sha256(raw[previous:]),
        })
    symbol_records = _elf_symbol_records(raw, sections)
    versions = _elf_version_records(raw, sections, symbol_records)
    dynamic = _elf_dynamic_records(raw, sections)
    return {
        "schema": SCHEMA + "-authenticated-raw-elf64",
        "format": "ELF64-LITTLE-ENDIAN-X86-64-ET-DYN",
        "file_sha256": sha256(raw), "file_size": len(raw),
        "header": {
            "operating_system_abi": identity[7],
            "entry": entry, "flags": flags,
            "header_size": header_size,
            "program_header_offset": program_offset,
            "program_header_entry_size": program_size,
            "program_header_count": program_count,
            "section_header_offset": section_offset,
            "section_header_entry_size": section_size,
            "section_count": section_count,
            "section_name_index": names_index,
        },
        "program_headers": programs,
        "sections": sections,
        "file_regions": covered,
        "symbol_tables": symbol_records,
        "symbol_versions": versions,
        "dynamic_tables": dynamic,
    }


def _elf_region_at(regions: list[dict[str, Any]], index: int) -> str:
    for item in regions:
        if item["start"] <= index < item["end"]:
            return item["kind"]
    return "END_OF_FILE"


def compare_owned_elf64(
    first: bytes, second: bytes,
    first_parsed: dict[str, Any] | None = None,
    second_parsed: dict[str, Any] | None = None,
) -> dict[str, Any]:
    left = parse_owned_elf64(first) if first_parsed is None else first_parsed
    right = parse_owned_elf64(second) if second_parsed is None else second_parsed
    require(type(left) is dict and type(right) is dict
            and left.get("file_sha256") == sha256(first)
            and right.get("file_sha256") == sha256(second)
            and left.get("file_size") == len(first)
            and right.get("file_size") == len(second),
            "bind both full native ELF difference inputs to their actual bytes")
    bounds = {0, len(first), len(second)}
    for item in left["file_regions"] + right["file_regions"]:
        bounds.add(item["start"])
        bounds.add(item["end"])
    cuts = sorted(value for value in bounds
                  if 0 <= value <= max(len(first), len(second)))
    displayed: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    difference_count = 0
    differing_bytes = 0
    first_difference: int | None = None
    last_difference: int | None = None
    for start, end in zip(cuts, cuts[1:], strict=False):
        cursor = start
        while cursor < end:
            equal = (cursor < len(first) and cursor < len(second)
                     and first[cursor] == second[cursor])
            if equal:
                cursor += 1
                continue
            beginning = cursor
            while cursor < end and not (
                cursor < len(first) and cursor < len(second)
                and first[cursor] == second[cursor]
            ):
                cursor += 1
            a = first[beginning:min(cursor, len(first))]
            b = second[beginning:min(cursor, len(second))]
            count = max(len(a), len(b))
            span = {
                "offset": beginning, "end_offset": cursor,
                "differing_byte_count": count,
                "phase_a_region": _elf_region_at(left["file_regions"], beginning),
                "phase_b_region": _elf_region_at(right["file_regions"], beginning),
                "phase_a_bytes": len(a), "phase_b_bytes": len(b),
                "phase_a_sha256": sha256(a), "phase_b_sha256": sha256(b),
                "phase_a_preview_hex": a[:MAX_DIFFERENCE_PREVIEW_BYTES].hex(),
                "phase_b_preview_hex": b[:MAX_DIFFERENCE_PREVIEW_BYTES].hex(),
            }
            digest.update(canonical(span))
            difference_count += 1
            differing_bytes += count
            if first_difference is None:
                first_difference = beginning
            last_difference = cursor - 1
            if len(displayed) < MAX_REPORTED_DIFFERENCE_SPANS:
                displayed.append(span)
    left_sections = {(item["index"], item["name"]): item
                     for item in left["sections"]}
    right_sections = {(item["index"], item["name"]): item
                      for item in right["sections"]}
    keys = sorted(set(left_sections) | set(right_sections))
    changes: list[dict[str, Any]] = []
    for key in keys:
        previous = left_sections.get(key)
        current = right_sections.get(key)
        if previous == current:
            continue
        changes.append({
            "index": key[0], "name": key[1],
            "phase_a": previous,
            "phase_b": current,
        })
    exact = first == second
    require(exact is (difference_count == 0)
            and exact is (sha256(first) == sha256(second))
            and sum(item["differing_byte_count"] for item in displayed)
            <= differing_bytes,
            "account for every complete authenticated native ELF byte difference")
    return {
        "schema": SCHEMA + "-complete-raw-elf-difference",
        "byte_identical": exact,
        "phase_a_sha256": sha256(first),
        "phase_b_sha256": sha256(second),
        "phase_a_bytes": len(first),
        "phase_b_bytes": len(second),
        "length_delta": len(second) - len(first),
        "total_differing_byte_count": differing_bytes,
        "total_difference_span_count": difference_count,
        "first_difference_offset": first_difference,
        "last_difference_offset": last_difference,
        "reported_span_count": len(displayed),
        "omitted_span_count": difference_count - len(displayed),
        "report_truncated": difference_count > len(displayed),
        "complete_span_manifest_sha256": digest.hexdigest(),
        "difference_spans": displayed,
        "changed_section_count": len(changes),
        "changed_sections": changes,
        "sole_differing_raw_section": (
            changes[0]["name"]
            if len(changes) == 1 and difference_count
            and all(item["phase_a_region"].startswith("SECTION:")
                    and item["phase_b_region"].startswith("SECTION:")
                    and item["phase_a_region"] == item["phase_b_region"]
                    and item["phase_a_region"].endswith(":" + changes[0]["name"])
                    for item in displayed)
            and difference_count == len(displayed)
            else "NOT ESTABLISHED"
        ),
    }


def synthetic_owned_elf64(
    *, note: bytes = b"first-party", text: bytes = b"\x90\xc3",
    trailing: bytes = b"",
) -> bytes:
    require(type(note) is bytes and type(text) is bytes and type(trailing) is bytes
            and len(note) <= 4096 and len(text) <= 4096
            and len(trailing) <= 65536,
            "construct only bounded, in-memory genuine ELF source controls")
    strings = b"\x00.shstrtab\x00.text\x00.note.synthetic\x00.empty\x00.bss\x00"
    sections = 6
    program_offset = ELF64_HEADER.size
    program_end = program_offset + ELF64_PROGRAM.size
    names_offset = (program_end + 7) & ~7
    text_offset = (names_offset + len(strings) + 15) & ~15
    note_offset = (text_offset + len(text) + 3) & ~3
    empty_offset = note_offset + len(note)
    table_offset = (empty_offset + 7) & ~7
    table_end = table_offset + sections * ELF64_SECTION.size
    raw = bytearray(table_end + len(trailing))
    raw[names_offset:names_offset + len(strings)] = strings
    raw[text_offset:text_offset + len(text)] = text
    raw[note_offset:note_offset + len(note)] = note
    if trailing:
        raw[table_end:] = trailing
    identity = b"\x7fELF" + bytes((2, 1, 1, 0, 0)) + bytes(7)
    ELF64_HEADER.pack_into(
        raw, 0, identity, 3, 62, 1, 0x400000 + text_offset,
        program_offset, table_offset, 0, ELF64_HEADER.size,
        ELF64_PROGRAM.size, 1, ELF64_SECTION.size, sections, 1,
    )
    ELF64_PROGRAM.pack_into(
        raw, program_offset, 1, 5, 0, 0x400000, 0x400000,
        len(raw), len(raw), 0x1000,
    )
    rows = (
        (0, SHT_NULL, 0, 0, 0, 0, 0, 0, 0, 0),
        (1, SHT_STRTAB, 0, 0, names_offset, len(strings), 0, 0, 1, 0),
        (11, SHT_PROGBITS, 6, 0x400000 + text_offset,
         text_offset, len(text), 0, 0, 16, 0),
        (17, SHT_NOTE, 2, 0x400000 + note_offset,
         note_offset, len(note), 0, 0, 4, 0),
        (33, SHT_PROGBITS, 0, 0, empty_offset, 0, 0, 0, 1, 0),
        (40, SHT_NOBITS, 3, 0x400000 + empty_offset,
         empty_offset, 64, 0, 0, 8, 0),
    )
    for index, row in enumerate(rows):
        ELF64_SECTION.pack_into(
            raw, table_offset + index * ELF64_SECTION.size, *row,
        )
    return bytes(raw)

def expected_evidence_accounting() -> dict[str, Any]:
    actual_v5_processes = sum(
        entry["process_count"] for entry in HISTORICAL_V5.values()
    )
    actual_v6_processes = sum(
        entry["process_count"] for entry in HISTORICAL_V6.values()
    )
    require(actual_v5_processes == 31 and actual_v6_processes == 52,
            "retain every genuine V5 and V6 process without inventing a source build")
    return {
        "candidate_history_family_count": 3,
        "candidate_history_families": ["c", "rust", "zig"],
        "candidate_history_owners_per_family": 17,
        "candidate_history_owner_count": 51,
        "v4_cpp_evidence_owner_count": 2,
        "v4_go_failure_evidence_owner_count": 2,
        "v4_fortran_failure_evidence_owner_count": 2,
        "v5_go_failure_evidence_owner_count": 2,
        "v5_fortran_evidence_owner_count": 2,
        "v6_go_success_evidence_owner_count": 2,
        "v6_fortran_failure_evidence_owner_count": 2,
        "distinct_evidence_file_owner_count": (
            57 + 2 * len(HISTORICAL_V5) + 2 * len(HISTORICAL_V6)
        ),
        "v2_actual_compiler_process_count": 39,
        "v3_zig_actual_compiler_process_count": 15,
        "v4_cpp_actual_compiler_process_count": 10,
        "v4_go_failure_actual_compiler_process_count": 4,
        "v4_fortran_actual_compiler_process_count": 18,
        "v2_and_v4_actual_compiler_process_count": 71,
        "v5_go_failure_actual_compiler_process_count":
            HISTORICAL_V5["go"]["process_count"],
        "v5_fortran_actual_compiler_process_count":
            HISTORICAL_V5["fortran"]["process_count"],
        "historical_v2_v4_v5_actual_compiler_process_count":
            71 + actual_v5_processes,
        "historical_v2_v3_v4_v5_actual_compiler_process_count":
            86 + actual_v5_processes,
        "v6_go_success_actual_compiler_process_count":
            HISTORICAL_V6["go"]["process_count"],
        "v6_fortran_failure_actual_compiler_process_count":
            HISTORICAL_V6["fortran"]["process_count"],
        "historical_v2_v4_v5_v6_actual_compiler_process_count":
            71 + actual_v5_processes + actual_v6_processes,
        "historical_actual_compiler_process_count":
            71 + actual_v5_processes + actual_v6_processes,
        "all_historical_versions_actual_compiler_process_count":
            86 + actual_v5_processes + actual_v6_processes,
        "historical_candidate_semantic_mismatch_counts": {
            "c": 2094, "rust": 2042, "zig": 1764,
        },
        "file_owners_are_not_processes": True,
        "historical_failures_count_as_passes": False,
        "qualified_candidate_count": 0,
    }


def expected_raw_elf_forensic_policy() -> dict[str, Any]:
    return {
        "implementation": "FIRST-PARTY BOUNDED PYTHON STRUCT; NO EXTERNAL ELF PACKAGE",
        "format": "ELF64-LITTLE-ENDIAN-X86-64-ET-DYN",
        "artifact_source": "COMPLETE FRESH PRIVATE PHASE NATIVE BINARY",
        "full_binary_maximum_bytes": MAX_BINARY_BYTES,
        "section_count_maximum": ELF64_MAX_SECTIONS,
        "program_header_count_maximum": ELF64_MAX_PROGRAMS,
        "symbol_count_maximum": ELF64_MAX_SYMBOLS,
        "section_name_maximum_bytes": ELF64_MAX_STRING_BYTES,
        "extended_section_count": "AUTHENTICATED",
        "extended_section_name_index": "AUTHENTICATED",
        "extended_program_count": "AUTHENTICATED",
        "extended_symbol_section_indexes": "AUTHENTICATED",
        "nobits_policy": "MEMORY-ONLY; NO INVENTED FILE PAYLOAD",
        "duplicate_section_names": "INDEXED; NO SILENT ALIAS",
        "compression": "BOUNDED ZLIB; RAW AND EXPANDED DIGESTS",
        "gnu_symbol_versioning": "LINKS, COUNTS, OFFSETS, AND COMPLETE NAMES",
        "raw_section_payloads": "EVERY ACTUAL FILE-BACKED SECTION",
        "raw_section_digest": "SHA-256 OF EXACT AUTHENTICATED SECTION BYTES",
        "metadata_coverage": "ELF HEADER; PROGRAM HEADERS; SECTION HEADERS",
        "padding_and_trailer_coverage": "COMPLETE; INDEPENDENTLY HASHED",
        "complete_file_difference_count": True,
        "complete_difference_span_manifest_sha256": True,
        "difference_offset_limit": MAX_REPORTED_DIFFERENCE_SPANS,
        "difference_preview_byte_limit": MAX_DIFFERENCE_PREVIEW_BYTES,
        "difference_truncation_always_disclosed": True,
        "sole_cause_requires_complete_file_proof": True,
        "record_before_reproducibility_classification": True,
        "additional_process_count": 0,
        "additional_unpinned_inspection_tool_count": 0,
        "unchanged_v6_compiler_and_linker_flags": True,
        "speculative_fortran_compiler_repair": "FORBIDDEN",
        "historical_v6_fortran_raw_section_difference": "NOT RECORDED",
        "actual_v7_builds": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def expected_contract() -> dict[str, Any]:
    families = [
        {"id": family, "language": spec["language"],
         "adapter_import": spec["adapter_import"],
         "artifacts": dict(spec["artifacts"]),
         "allowed_bridge_python_imports": list(spec["allowed_bridge_python_imports"]),
         "owners": [{"path": path, "sha256": digest, "bytes": size}
                    for path, (digest, size) in SOURCE_OWNERS[family].items()]}
        for family, spec in FAMILIES.items()
    ]
    toolchains = [
        {"id": key, "path": path, "sha256": digest, "bytes": size,
         "version": version, "executable": executable}
        for key, (path, digest, size, version, executable)
        in EXPECTED_TOOLCHAINS.items()
    ]
    support = [
        {"id": key, "path": path, "sha256": digest, "bytes": size}
        for key, (path, digest, size) in EXPECTED_SUPPORT.items()
    ]
    return {
        "schema": CONTRACT_SCHEMA,
        "version": 7,
        "phase": "SOURCE FREEZE; NO BUILD AUTHORIZED",
        "oracle": expected_oracle(),
        "family_count": 6,
        "source_owner_count": 25,
        "qualified_candidate_count": 0,
        "families": families,
        "toolchains": toolchains,
        "pinned_support": support,
        "historical_v2": [copy.deepcopy(item) for item in EXPECTED_HISTORY_V2.values()],
        "historical_v4": [copy.deepcopy(item) for item in HISTORICAL_V4.values()],
        "historical_v5": [copy.deepcopy(item) for item in HISTORICAL_V5.values()],
        "historical_v6": [copy.deepcopy(item) for item in HISTORICAL_V6.values()],
        "raw_elf_forensics": expected_raw_elf_forensic_policy(),
        "evidence_accounting": expected_evidence_accounting(),
        "go_private_package": expected_go_private_package(),
        "build_policy": copy.deepcopy(EXPECTED_BUILD_POLICY),
        "phase_boundary": copy.deepcopy(EXPECTED_PHASE_BOUNDARY),
    }


def validate_contract(value: Any) -> dict[str, Any]:
    require(type(value) is dict and value == expected_contract(),
            "the complete exact V7 raw-forensics and six-family source freeze changed")
    owners = [path for family in SOURCE_OWNERS.values() for path in family]
    require(len(owners) == 25 and len(set(owners)) == 25,
            "require all 25 genuinely independent original semantic source files")
    for path in owners:
        checked_relative(path)
        family = next(name for name, rows in SOURCE_OWNERS.items() if path in rows)
        digest, size = SOURCE_OWNERS[family][path]
        checked_digest(digest, path)
        require(type(size) is int and 0 < size <= MAX_SOURCE_BYTES,
                "require the original exact bounded first-party source size")
    require(len(EXPECTED_TOOLCHAINS) == 13
            and len(EXPECTED_HISTORY_V2) == 3
            and len(HISTORICAL_V4) == 3
            and set(HISTORICAL_V5) == {"go", "fortran"}
            and set(HISTORICAL_V6) == {"go", "fortran"}
            and len(GO_FAILURE_STDERR) == HISTORICAL_V4["go"]["stderr_bytes"]
            and sha256(GO_FAILURE_STDERR)
            == HISTORICAL_V4["go"]["stderr_sha256"],
            "preserve every actual prior compiler toolchain, process, and signed failure")
    require(HISTORICAL_V5["go"]["build_status"] == "FAIL"
            and HISTORICAL_V5["go"]["receipt_status"] == "PASS"
            and HISTORICAL_V5["go"]["process_count"] == 5
            and HISTORICAL_V5["go"]["completed_build_phase_count"] == 0
            and HISTORICAL_V5["fortran"]["build_status"] == "FAIL"
            and HISTORICAL_V5["fortran"]["receipt_status"] == "PASS"
            and HISTORICAL_V5["fortran"]["process_count"] == 26
            and HISTORICAL_V5["fortran"]["completed_build_phase_count"] == 2
            and HISTORICAL_V5["fortran"]["engine_phase_a_sha256"]
            != HISTORICAL_V5["fortran"]["engine_phase_b_sha256"]
            and HISTORICAL_V5["fortran"]["differing_raw_binary_section"]
            == "NOT RECORDED",
            "preserve the genuine V5 failures without inventing historical raw sections")
    go = HISTORICAL_V6["go"]
    fortran = HISTORICAL_V6["fortran"]
    require(go["build_status"] == "PASS"
            and go["receipt_status"] == "PASS"
            and go["process_count"] == go["successful_process_count"] == 26
            and go["completed_build_phase_count"] == 2
            and go["required_engine_export_count"] == 9
            and fortran["build_status"] == "FAIL"
            and fortran["receipt_status"] == "PASS"
            and fortran["process_count"]
            == fortran["successful_process_count"] == 26
            and fortran["completed_build_phase_count"] == 2
            and fortran["engine_phase_a_sha256"]
            != fortran["engine_phase_b_sha256"]
            and fortran["engine_phase_notes_bytes"] == 0
            and fortran["engine_build_id_status"] == "NOT PRESENT"
            and fortran["differing_raw_binary_section"] == "NOT RECORDED",
            "preserve genuine V6 Go success and full Fortran failure without guessing")
    accounting = value["evidence_accounting"]
    require(accounting["candidate_history_owner_count"] == 51
            and accounting["distinct_evidence_file_owner_count"] == 65
            and accounting["v2_and_v4_actual_compiler_process_count"] == 71
            and accounting["historical_v2_v4_v5_actual_compiler_process_count"]
            == 102
            and accounting["historical_v2_v3_v4_v5_actual_compiler_process_count"]
            == 117
            and accounting["v6_go_success_actual_compiler_process_count"] == 26
            and accounting["v6_fortran_failure_actual_compiler_process_count"] == 26
            and accounting["all_historical_versions_actual_compiler_process_count"]
            == 169
            and accounting["file_owners_are_not_processes"] is True
            and accounting["historical_failures_count_as_passes"] is False
            and accounting["qualified_candidate_count"] == 0,
            "reject invented owners, process totals, build promotion, or candidate passes")
    require(value["raw_elf_forensics"] == expected_raw_elf_forensic_policy()
            and value["raw_elf_forensics"]["additional_process_count"] == 0
            and value["raw_elf_forensics"]["unchanged_v6_compiler_and_linker_flags"]
            is True,
            "reject a weaker or speculative first-party ELF instrumentation policy")
    return value


def read_owned(relative: str, digest: str, *, maximum: int,
               exact_size: int | None = None,
               capture: bool = True,
               owner_only: bool = False) -> tuple[bytes | None, dict[str, Any]]:
    checked_relative(relative)
    checked_digest(digest, relative)
    require(type(maximum) is int and 0 < maximum <= MAX_BINARY_BYTES
            and type(capture) is bool and type(owner_only) is bool,
            "authenticate one exact bounded first-party source or historical owner")
    if exact_size is not None:
        require(type(exact_size) is int and 0 < exact_size <= maximum,
                "require the exact actual independently frozen file size")
    pieces = relative.split("/")
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    file_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    ancestors: list[int] = []
    descriptor: int | None = None
    try:
        current = os.open(str(ROOT), directory_flags)
        ancestors.append(current)
        for component in pieces[:-1]:
            child = os.open(component, directory_flags, dir_fd=current)
            actual = os.fstat(child)
            visible = os.stat(
                component, dir_fd=current, follow_symlinks=False,
            )
            require(stat.S_ISDIR(actual.st_mode)
                    and stat.S_ISDIR(visible.st_mode)
                    and (actual.st_dev, actual.st_ino)
                    == (visible.st_dev, visible.st_ino),
                    "reject a symlinked, redirected, or replaced first-party ancestor")
            ancestors.append(child)
            current = child
        descriptor = os.open(pieces[-1], file_flags, dir_fd=current)
        before = os.fstat(descriptor)
        visible = os.stat(
            pieces[-1], dir_fd=current, follow_symlinks=False,
        )
        require(stat.S_ISREG(before.st_mode)
                and stat.S_ISREG(visible.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and 0 < before.st_size <= maximum
                and (exact_size is None or before.st_size == exact_size)
                and (not owner_only or stat.S_IMODE(before.st_mode) == 0o600),
                "reject a symlinked, shared, resized, or nonprivate evidence owner")
        accumulator = bytearray() if capture else None
        observed = hashlib.sha256()
        count = 0
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            count += len(block)
            require(count <= before.st_size and count <= maximum,
                    "reject a native owner that grew during authentication")
            observed.update(block)
            if accumulator is not None:
                accumulator.extend(block)
        after = os.fstat(descriptor)
        final = os.stat(
            pieces[-1], dir_fd=current, follow_symlinks=False,
        )
        require(count == before.st_size == after.st_size
                and (before.st_dev, before.st_ino,
                     before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino,
                    after.st_mtime_ns, after.st_ctime_ns)
                and stat.S_ISREG(final.st_mode)
                and (after.st_dev, after.st_ino, after.st_size)
                == (final.st_dev, final.st_ino, final.st_size)
                and observed.hexdigest() == digest,
                "reject changed bytes, switched descriptors, or non-authentic owners: "
                + relative)
        for number, ancestor in enumerate(ancestors[1:], 0):
            previous = ancestors[number]
            actual = os.fstat(ancestor)
            reopened = os.stat(
                pieces[number], dir_fd=previous, follow_symlinks=False,
            )
            require(stat.S_ISDIR(actual.st_mode)
                    and stat.S_ISDIR(reopened.st_mode)
                    and (actual.st_dev, actual.st_ino)
                    == (reopened.st_dev, reopened.st_ino),
                    "reject a first-party parent swapped during authentication")
        owner = {
            "relative": relative,
            "path": str(ROOT / relative),
            "sha256": digest,
            "size_bytes": count,
            "device": after.st_dev,
            "inode": after.st_ino,
            "mode": stat.S_IMODE(after.st_mode),
            "executable": bool(after.st_mode & 0o111),
            "ancestor_no_follow_verified": True,
            "same_inode_readback_verified": True,
        }
        return (
            bytes(accumulator) if accumulator is not None else None,
            owner,
        )
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for directory in reversed(ancestors):
            os.close(directory)


def bounded_gzip(raw: Any, *, exact_size: int) -> bytes:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES
            and type(exact_size) is int and 0 < exact_size <= MAX_REPORT_BYTES,
            "require one complete bounded single-member historical archive")
    try:
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        plain = decoder.decompress(raw, MAX_REPORT_BYTES + 1)
        require(len(plain) <= MAX_REPORT_BYTES and not decoder.unconsumed_tail
                and decoder.eof and not decoder.unused_data,
                "reject a truncated, concatenated, oversized, or appended gzip member")
        plain += decoder.flush()
    except (zlib.error, ValueError) as error:
        raise BuildError("reject a malformed frozen historical gzip archive") from error
    require(len(plain) == exact_size,
            "the complete uncompressed historical evidence byte count changed")
    return plain


def load_frozen_v4() -> types.ModuleType:
    relative, digest, size = EXPECTED_SUPPORT["build_recorder_v4"]
    raw, _ = read_owned(relative, digest, maximum=MAX_SOURCE_BYTES,
                        exact_size=size, capture=True)
    require(raw is not None, "authenticate the complete frozen V4 source kernel")
    module = types.ModuleType("_rebar_phase2_exact_frozen_v4_source_kernel")
    module.__dict__["__file__"] = str(ROOT / relative)
    module.__dict__["__package__"] = None
    exec(compile(raw, str(ROOT / relative), "exec"), module.__dict__)
    require(module.SCHEMA == "rebar-phase2-owned-native-source-build-v4"
            and module.SOURCE_OWNERS == SOURCE_OWNERS
            and module.FAMILIES == FAMILIES
            and module.EXPECTED_TOOLCHAINS == EXPECTED_TOOLCHAINS
            and module.EXPECTED_HISTORY == EXPECTED_HISTORY_V2,
            "the exact isolated V4 semantic and compiler source kernel changed")
    return module


def load_frozen_v5() -> types.ModuleType:
    relative, digest, size = EXPECTED_SUPPORT["build_recorder_v5"]
    raw, _ = read_owned(
        relative, digest, maximum=MAX_SOURCE_BYTES,
        exact_size=size, capture=True,
    )
    require(raw is not None,
            "authenticate all bytes of the independently frozen V5 source recorder")
    module = types.ModuleType("_rebar_phase2_exact_frozen_v5_source_kernel")
    module.__dict__["__file__"] = str(ROOT / relative)
    module.__dict__["__package__"] = None
    exec(compile(raw, str(ROOT / relative), "exec"), module.__dict__)
    require(module.SCHEMA == "rebar-phase2-owned-native-source-build-v5"
            and module.SOURCE_OWNERS == SOURCE_OWNERS
            and module.FAMILIES == FAMILIES
            and module.EXPECTED_TOOLCHAINS == EXPECTED_TOOLCHAINS
            and module.EXPECTED_HISTORY_V2 == EXPECTED_HISTORY_V2
            and module.HISTORICAL_V4 == HISTORICAL_V4,
            "reject a changed, foreign, silently repaired, or incomplete V5 build kernel")
    contract_relative, contract_digest, contract_size = (
        EXPECTED_SUPPORT["build_contract_v5"]
    )
    contract_raw, _ = read_owned(
        contract_relative, contract_digest, maximum=MAX_SOURCE_BYTES,
        exact_size=contract_size, capture=True,
    )
    require(contract_raw is not None,
            "authenticate the complete unchanged V5 machine source freeze")
    module.validate_contract(module.decode_json(contract_raw))
    protocol_relative, protocol_digest, protocol_size = (
        EXPECTED_SUPPORT["build_protocol_v5"]
    )
    _, _ = read_owned(
        protocol_relative, protocol_digest, maximum=MAX_SOURCE_BYTES,
        exact_size=protocol_size, capture=False,
    )
    return module


def load_frozen_independence_v2() -> types.ModuleType:
    relative, digest, size = EXPECTED_SUPPORT["independence_auditor_v2"]
    raw, _ = read_owned(relative, digest, maximum=MAX_SOURCE_BYTES,
                        exact_size=size, capture=True)
    require(raw is not None,
            "authenticate the complete independently frozen six-family V2 static auditor")
    name = "_rebar_phase2_exact_frozen_independence_v2_source_kernel"
    require(name not in sys.modules,
            "reject a substituted or previously imported independence audit kernel")
    module = types.ModuleType(name)
    module.__dict__["__file__"] = str(ROOT / relative)
    module.__dict__["__package__"] = None
    sys.modules[name] = module
    try:
        exec(compile(raw, str(ROOT / relative), "exec"), module.__dict__)
    finally:
        require(sys.modules.get(name) is module,
                "the exact frozen audit module was redirected while loading")
        del sys.modules[name]
    require(module.SCHEMA == "rebar-phase2-six-candidate-independence-static-audit-v2"
            and len(module.FAMILIES) == 6
            and sum(len(item.owners) for item in module.FAMILIES) == 25
            and module.PINNED_PYTHON == (3, 14, 6),
            "preserve the real V2 six-family source auditor and baseline")
    return module


def verify_six_family_independence() -> dict[str, Any]:
    module = load_frozen_independence_v2()
    arguments = types.SimpleNamespace(
        source_sha256=EXPECTED_SUPPORT["independence_auditor_v2"][1],
        protocol_sha256=EXPECTED_SUPPORT["independence_protocol_v2"][1],
        inventory_sha256=EXPECTED_SUPPORT["independence_inventory_v2"][1],
    )
    result = module.run_verify(arguments)
    require(type(result) is dict and result.get("schema") == module.SCHEMA
            and result.get("status") == "PASS"
            and result.get("static_independence") == "PASS"
            and result.get("family_count") == 6
            and result.get("source_owner_count") == 25
            and result.get("pairwise_semantic_owner_overlap_count") == 0
            and result.get("phase1_suite_count") == 13
            and result.get("phase1_case_execution_count") == 31237
            and result.get("candidate_correctness_qualified_count") == 0
            and result.get("candidate_correctness") == "NOT MEASURED"
            and result.get("runtime_no_delegation") == "NOT ESTABLISHED"
            and result.get("performance") == "NOT MEASURED"
            and result.get("holdout") == "NOT ACCESSED"
            and result.get("candidate_code_executed") is False
            and result.get("native_libraries_loaded") is False
            and result.get("candidate_processes_started") == 0
            and result.get("reference_processes_started") == 0
            and result.get("clock_samples") == 0
            and result.get("hidden_cases_read") == 0
            and result.get("performance_files_read") == 0,
            "run the exact frozen V2 six-family static no-wrapper source audit read-only")
    families = result.get("families")
    require(type(families) is list and len(families) == 6,
            "retain every independently inspected first-party matching implementation")
    by_family = {
        item.get("graph_family"): item
        for item in families if type(item) is dict
    }
    require(set(by_family) == set(FAMILIES),
            "the static audit omitted or substituted an independently owned family")
    for family, item in by_family.items():
        owners = item.get("owners")
        require(item.get("static_independence") == "PASS"
                and type(owners) is list
                and len(owners) == len(SOURCE_OWNERS[family]),
                "require every genuine source owner in the strict independence audit")
        actual = {
            entry["path"]: entry["sha256"]
            for entry in owners
            if type(entry) is dict and type(entry.get("path")) is str
        }
        require(actual == {
            path: digest for path, (digest, _) in SOURCE_OWNERS[family].items()
        }, "the static audit inspected a foreign or incomplete candidate source")
    go_engine = next(
        item for item in by_family["go"]["owners"]
        if item["path"] == "candidates/go/engine.go"
    )
    require(go_engine.get("owned_cgo_preamble_count") == 1
            and go_engine.get("owned_cgo_preamble_headers")
            == ["#include <stddef.h>", "#include <stdint.h>", "#include <stdlib.h>"]
            and len(go_engine.get("owned_cgo_exports", [])) == 9
            and go_engine.get("external_cgo_linker_directive_count") == 0,
            "verify the real header-only cgo preamble and all nine original Go exports")
    fortran_engine = next(
        item for item in by_family["fortran"]["owners"]
        if item["path"] == "candidates/fortran/engine.f90"
    )
    bindings = fortran_engine.get("fortran_owned_c_bindings")
    require(type(bindings) is list and len(bindings) == 12
            and len(set(bindings)) == 12
            and all(type(name) is str and name.startswith("rebar_fortran_")
                    for name in bindings),
            "verify all twelve first-party Fortran engine and reverse callback bindings")
    return result


def checked_source_pins(family: Any, values: Any) -> dict[str, str]:
    family = checked_family(family)
    owners = SOURCE_OWNERS[family]
    require(type(values) is list and len(values) == len(owners),
            "pin every independently owned family source exactly once")
    result: dict[str, str] = {}
    for item in values:
        require(type(item) is str and item.count("=") == 1,
                "pin source as exactly REPOSITORY/RELATIVE/PATH=SHA256")
        path, digest = item.split("=", 1)
        checked_relative(path)
        require(path in owners and path not in result
                and checked_digest(digest, path) == owners[path][0],
                "reject an omitted, repeated, changed, or cross-family source owner")
        result[path] = digest
    require(set(result) == set(owners), "require the complete frozen semantic closure")
    return dict(sorted(result.items()))


def checked_workdir(value: Any, family: str) -> str:
    family = checked_family(family)
    require(type(value) is str
            and value.startswith("/tmp/" + WORK_PREFIX + family + "-")
            and "\\" not in value and "\x00" not in value
            and value == value.rstrip("/") and len(value.split("/")) == 3
            and all(part not in ("", ".", "..") for part in value.split("/")[1:]),
            "reject an unsafe, broad, reused, cross-version, or cross-family private root")
    return value


def phase_paths(workdir: str, family: str, phase: str) -> dict[str, Path]:
    checked_workdir(workdir, family)
    require(phase in ("reference-a", "reference-b"),
            "require exactly two independently owned source-build phases")
    base = Path(workdir) / phase
    source = base / "source"
    native = base / "native"
    paths = {
        "base": base, "source": source, "native": native,
        "temporary": base / "temporary", "target": base / "target",
        "cargo_home": base / "cargo-home",
        "zig_local_cache": base / "zig-local-cache",
        "zig_global_cache": base / "zig-global-cache",
        "go_build_cache": base / "go-build-cache",
        "go_module_cache": base / "go-module-cache",
        "fortran_modules": base / "fortran-modules",
        "rust_manifest": source / "candidates/rust/Cargo.toml",
        "rust_target_engine": base / "target/release/librebar_rust_continuation.so",
        "go_module_directory": base / "go-engine-package",
        "go_original_source_directory": source / "candidates/go",
    }
    for kind, filename in FAMILIES[family]["artifacts"].items():
        paths["artifact_" + kind] = native / filename
    return paths


def sanitized(value: str, workdir: str, family: str) -> str:
    require(type(value) is str, "sanitize only an exact owned path")
    return value.replace(checked_workdir(workdir, family), "<FRESH_PRIVATE_TMP>")


def reproducible_prefix_flags(workdir: str, family: str) -> tuple[list[str], str]:
    gcc_flags: list[str] = []
    rust_flags: list[str] = []
    for phase in ("reference-a", "reference-b"):
        source = str(phase_paths(workdir, family, phase)["source"])
        gcc_flags.append("-ffile-prefix-map=" + source + "=/rebar-phase2-v6-owned-source")
        rust_flags.append("--remap-path-prefix=" + source + "=/rebar-phase2-v6-owned-source")
        if family == "fortran":
            phase_root = str(phase_paths(workdir, family, phase)["base"])
            gcc_flags.append(
                "-ffile-prefix-map=" + phase_root + "=/rebar-phase2-v6-owned-phase"
            )
    if family == "rust":
        rust_flags.append("-Clink-arg=-Wl,-soname,_rust_engine.so")
    return gcc_flags, " ".join(rust_flags)


def build_environment(workdir: str, family: str, phase: str) -> dict[str, str]:
    paths = phase_paths(workdir, family, phase)
    _, rust_flags = reproducible_prefix_flags(workdir, family)
    environment = {
        "PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
        "SOURCE_DATE_EPOCH": "1", "TMPDIR": str(paths["temporary"]),
    }
    if family == "rust":
        environment.update({
            "PATH": RUST_TOOLCHAIN + "/bin:/usr/bin:/bin",
            "CARGO_HOME": str(paths["cargo_home"]), "CARGO_NET_OFFLINE": "true",
            "CARGO_INCREMENTAL": "0", "CARGO_BUILD_JOBS": "1",
            "RUSTC": PINNED_RUSTC, "RUSTFLAGS": rust_flags,
        })
    elif family == "zig":
        environment.update({
            "ZIG_LOCAL_CACHE_DIR": str(paths["zig_local_cache"]),
            "ZIG_GLOBAL_CACHE_DIR": str(paths["zig_global_cache"]),
        })
    elif family == "go":
        environment.update({
            "GOPROXY": "off", "GOSUMDB": "off", "GOWORK": "off",
            "GOENV": "off", "GOTOOLCHAIN": "local", "CGO_ENABLED": "1",
            "CC": PINNED_GCC, "GOCACHE": str(paths["go_build_cache"]),
            "GOMODCACHE": str(paths["go_module_cache"]),
            "GOFLAGS": "-mod=readonly",
        })
    return environment


def validate_go_bridge_feature_macro(
    argv: Any, generated_header: Any,
) -> list[str]:
    require(type(argv) is list and all(type(item) is str for item in argv)
            and type(generated_header) is str,
            "require the exact separately owned Go bridge compiler arguments")
    require(bool(argv) and argv[0] == PINNED_GCC
            and argv.count("-D_GNU_SOURCE") == 1
            and argv.count("-include") == 1
            and argv.count(generated_header) == 1,
            "freeze exactly one GNU feature macro and the real generated Go header")
    macro_position = argv.index("-D_GNU_SOURCE")
    include_position = argv.index("-include")
    require(0 < macro_position < include_position
            and include_position + 1 < len(argv)
            and argv[include_position + 1] == generated_header,
            "define GNU features strictly before force-including the authentic Go header")
    require(not any(item.startswith("-D_GNU_SOURCE=")
                    or item == "-U_GNU_SOURCE"
                    or item.startswith("-U_GNU_SOURCE=")
                    for item in argv)
            and all(flag in argv for flag in ("-Wall", "-Wextra", "-Werror")),
            "reject alternate, disabled, repeated, or weakened strict Go bridge compilation")
    return list(argv)


def planned_commands(workdir: str, family: str, phase: str) -> dict[str, list[str]]:
    family = checked_family(family)
    paths = phase_paths(workdir, family, phase)
    prefix, _ = reproducible_prefix_flags(workdir, family)
    result: dict[str, list[str]] = {"readelf_version": [PINNED_READELF, "--version"]}
    if family in {"c", "rust", "zig", "go", "fortran"}:
        result["gcc_version"] = [PINNED_GCC, "--version"]
    if family == "c":
        result["build_c_extension"] = [
            PINNED_GCC, "-std=c11", "-O3", "-Wall", "-Wextra", "-Werror",
            "-fPIC", "-shared", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/_vm_native.c"),
            "-o", str(paths["artifact_extension"]),
        ]
    elif family == "rust":
        result["rustc_version"] = [PINNED_RUSTC, "--version", "--verbose"]
        result["cargo_version"] = [PINNED_CARGO, "--version"]
        result["build_rust_engine"] = [
            PINNED_CARGO, "build", "--manifest-path", str(paths["rust_manifest"]),
            "--release", "--locked", "--offline", "--frozen",
            "--target-dir", str(paths["target"]),
        ]
        result["build_rust_bridge"] = [
            PINNED_GCC, "-pthread", "-std=c11", "-shared", "-fPIC", "-O3",
            "-Wall", "-Wextra", "-Werror", "-Wl,-z,noexecstack",
            "-Wl,--exclude-libs,ALL", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/rust/py_bridge.c"),
            "-L" + str(paths["native"]), "-l:_rust_engine.so",
            "-Wl,-rpath,$ORIGIN", "-o", str(paths["artifact_bridge"]),
        ]
    elif family == "zig":
        result["zig_version"] = [PINNED_ZIG, "version"]
        result["build_zig_engine"] = [
            PINNED_ZIG, "build-lib",
            str(paths["source"] / "candidates/zig/mini_regex.zig"),
            "-dynamic", "-lc", "-O", "ReleaseFast", "-fstrip",
            "-fallow-shlib-undefined", "-fsoname=_zig_probe.so",
            "--cache-dir", str(paths["zig_local_cache"]),
            "--global-cache-dir", str(paths["zig_global_cache"]),
            "-femit-bin=" + str(paths["artifact_engine"]),
        ]
        result["build_zig_bridge"] = [
            PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3", "-Wall",
            "-Wextra", "-Werror", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/zig/py_bridge.c"),
            "-L" + str(paths["native"]), "-l:_zig_probe.so",
            "-Wl,-rpath,$ORIGIN", "-o", str(paths["artifact_bridge"]),
        ]
    elif family == "cpp":
        result["gxx_version"] = [PINNED_GXX, "--version"]
        result["build_cpp_bridge"] = [
            PINNED_GXX, "-std=c++20", "-O3", "-Wall", "-Wextra", "-Werror",
            "-fPIC", "-shared", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            "-I" + str(paths["source"] / "candidates/cpp"),
            str(paths["source"] / "candidates/cpp/engine.cpp"),
            str(paths["source"] / "candidates/cpp/py_bridge.cpp"),
            "-o", str(paths["artifact_bridge"]),
        ]
    elif family == "go":
        result["go_version"] = [PINNED_GO, "version"]
        result["build_go_engine"] = [
            PINNED_GO, "build", "-buildmode=c-shared", "-trimpath",
            "-buildvcs=false", "-ldflags=-buildid=",
            "-o", str(paths["artifact_engine"]), ".",
        ]
        result["build_go_bridge"] = [
            PINNED_GCC, "-D_GNU_SOURCE", "-std=c11", "-shared", "-fPIC", "-O3", "-Wall",
            "-Wextra", "-Werror", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE, "-I" + str(paths["native"]),
            "-include", str(paths["artifact_generated_header"]),
            str(paths["source"] / "candidates/go/py_bridge.c"),
            "-L" + str(paths["native"]), "-l:_go_engine.so",
            "-Wl,-rpath,$ORIGIN", "-o", str(paths["artifact_bridge"]),
        ]
    else:
        result["gfortran_version"] = [PINNED_GFORTRAN, "--version"]
        result["build_fortran_engine"] = [
            PINNED_GFORTRAN, "-shared", "-fPIC", "-O3",
            "-ffree-line-length-none", "-frandom-seed=rebar-fortran-v5",
            "-Wl,--build-id=none",
            "-Wl,-soname,_fortran_engine.so", *prefix,
            "-J" + str(paths["fortran_modules"]),
            str(paths["source"] / "candidates/fortran/engine.f90"),
            "-o", str(paths["artifact_engine"]),
        ]
        result["build_fortran_bridge"] = [
            PINNED_GCC, "-std=c11", "-shared", "-fPIC", "-O3", "-Wall",
            "-Wextra", "-Werror", "-Wl,--build-id=sha1", *prefix,
            "-I" + PYTHON_INCLUDE,
            str(paths["source"] / "candidates/fortran/py_bridge.c"),
            "-L" + str(paths["native"]), "-l:_fortran_engine.so",
            "-Wl,-rpath,$ORIGIN", "-o", str(paths["artifact_bridge"]),
        ]
    if family == "go":
        validate_go_bridge_feature_macro(
            result["build_go_bridge"], str(paths["artifact_generated_header"]),
        )
    for kind in FAMILIES[family]["artifacts"]:
        if kind != "generated_header":
            artifact = str(paths["artifact_" + kind])
            result[kind + "_dynamic"] = [PINNED_READELF, "--dynamic", "--wide", artifact]
            result[kind + "_symbols"] = [PINNED_READELF, "--dyn-syms", "--wide", artifact]
            result[kind + "_sections"] = [PINNED_READELF, "--sections", "--wide", artifact]
            result[kind + "_notes"] = [PINNED_READELF, "--notes", "--wide", artifact]
    return result


def checked_command(name: Any, argv: Any, workdir: str,
                    family: str, phase: str) -> list[str]:
    commands = planned_commands(workdir, family, phase)
    require(type(name) is str and name in commands and type(argv) is list
            and all(type(part) is str and "\x00" not in part for part in argv)
            and argv == commands[name],
            "reject a modified, abbreviated, shell, network, or third-party compiler command")
    require(argv[0] in {PINNED_GCC, PINNED_GXX, PINNED_GFORTRAN,
                        PINNED_READELF, PINNED_GO, PINNED_RUSTC,
                        PINNED_CARGO, PINNED_ZIG},
            "execute only a frozen owned compiler or ELF inspector")
    if family == "go" and name == "build_go_bridge":
        validate_go_bridge_feature_macro(
            argv,
            str(phase_paths(workdir, family, phase)["artifact_generated_header"]),
        )
    return list(argv)


def command_working_directory(workdir: str, family: str,
                              phase: str, name: str) -> Path:
    paths = phase_paths(workdir, family, phase)
    if family == "go" and name == "build_go_engine":
        return paths["go_module_directory"]
    return paths["base"]


def decode_process_stream(process: dict[str, Any], channel: str) -> bytes:
    require(channel in ("stdout", "stderr") and type(process) is dict,
            "require a genuine complete compiler output channel")
    encoded = process.get(channel + "_base64")
    require(type(encoded) is str, "retain the exact base64 compiler output")
    try:
        result = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise BuildError("reject forged or truncated compiler output") from error
    require(len(result) <= MAX_PROCESS_BYTES
            and type(process.get(channel + "_bytes")) is int
            and len(result) == process[channel + "_bytes"]
            and sha256(result) == process.get(channel + "_sha256"),
            "the full compiler output stream or its byte count changed")
    return result


def require_unmeasured(record: Any, *, label: str) -> None:
    require(type(record) is dict, "require exact zero-effect evidence: " + label)
    zero = ("candidate_processes_started", "candidate_imports",
            "native_libraries_loaded", "hidden_cases_read", "benchmark_files_read",
            "clock_samples", "timing_trials_run")
    for field in zero:
        if field in record:
            require(type(record[field]) is int and record[field] == 0,
                    "historical evidence crossed a forbidden boundary: " + label)
    for field in ("performance", "memory", "candidate_correctness",
                  "subinterpreter_isolation", "undefined_behavior"):
        if field in record:
            require(record[field] == "NOT MEASURED",
                    "historical source builds do not establish candidate results: " + label)
    if "holdout" in record:
        require(record["holdout"] == "NOT OPENED",
                "historical source evidence may not open a performance holdout")
    if "winner_selected" in record:
        require(record["winner_selected"] is False,
                "a historical source build cannot choose a winner")


def verify_complete_candidate_history(
    graph_raw: bytes, identities: set[tuple[int, int]],
) -> dict[str, Any]:
    graph = decode_json(graph_raw, canonical_required=True)
    require(graph.get("schema") == "rebar-candidate-current-overview-v10-inputs"
            and graph.get("version") == 10
            and graph.get("suite_count") == 13
            and graph.get("full_case_denominator") == 31237,
            "preserve the exact 13-suite, 31,237-case historical evidence graph")
    boundaries = graph.get("boundaries")
    require(type(boundaries) is dict
            and boundaries.get("hidden_cases_read") == 0
            and boundaries.get("performance_files_read") == 0
            and boundaries.get("clock_samples") == 0
            and boundaries.get("timing_trials_run") == 0
            and boundaries.get("final_holdout_opened") is False
            and boundaries.get("winner_selected") is False
            and boundaries.get("full_candidate_correctness") == "NOT MEASURED"
            and boundaries.get("performance") == "NOT MEASURED",
            "the historical graph cannot access benchmarks or qualify a candidate")
    records, frozen = graph.get("families"), graph.get("frozen_inputs")
    require(type(records) is list and type(frozen) is dict,
            "the exact frozen candidate and restoration evidence graph is required")
    by_family = {
        item.get("family"): item for item in records if type(item) is dict
    }
    require({"c", "rust", "zig"}.issubset(by_family),
            "preserve the three genuinely tested independent candidate families")
    require({"cpp", "go", "fortran"}.issubset(by_family),
            "preserve the actual historical six-family V10 snapshot")
    for family, count in expected_evidence_accounting()[
        "historical_candidate_semantic_mismatch_counts"
    ].items():
        failed = by_family[family].get("correctness_evidence")
        require(by_family[family].get("correctness") == "FAILED; NOT QUALIFIED"
                and type(failed) is dict
                and failed.get("expected_gate_status") == "FAIL"
                and failed.get("qualified_case_executions") == 0
                and failed.get("actual_semantic_mismatch_count") == count,
                "preserve every genuine historical C, Rust, and Zig semantic mismatch")
    require(by_family["cpp"].get("build_status") == "PASS"
            and by_family["cpp"].get("qualified") is False
            and by_family["go"].get("build_status") == "FAIL"
            and by_family["go"].get("qualified") is False
            and by_family["fortran"].get("build_status") == "NOT BUILT"
            and by_family["fortran"].get("source_only") is True,
            "retain the truthful V10 historical snapshot made before the Fortran build")
    for key, support_key in (
        ("native_build_v4_runner", "build_recorder_v4"),
        ("native_build_v4_protocol", "build_protocol_v4"),
        ("native_build_v4_inventory", "build_contract_v4"),
        ("independence_v2_runner", "independence_auditor_v2"),
        ("independence_v2_protocol", "independence_protocol_v2"),
        ("independence_v2_inventory", "independence_inventory_v2"),
    ):
        expected_path, expected_hash, _ = EXPECTED_SUPPORT[support_key]
        item = frozen.get(key)
        require(type(item) is dict and item.get("path") == expected_path
                and item.get("sha256") == expected_hash,
                "the published V10 predecessor source or independent auditor changed")

    def evidence(relative: str, digest: str,
                 exact_size: int | None = None) -> tuple[dict[str, Any], dict[str, Any] | None]:
        maximum = MAX_ARCHIVE_BYTES if relative.endswith(".json.gz") else MAX_SOURCE_BYTES
        raw, owner = read_owned(relative, digest, maximum=maximum,
                                exact_size=exact_size,
                                capture=relative.endswith(".json"), owner_only=True)
        identity = (owner["device"], owner["inode"])
        require(identity not in identities,
                "reject a shared, hard-linked, or double-counted evidence file owner")
        identities.add(identity)
        if relative.endswith(".json"):
            require(raw is not None, "read the entire owner-only durable historical receipt")
            receipt = decode_json(raw, canonical_required=True)
            require(receipt.get("status") == "PASS",
                    "a durable publication receipt was substituted")
            require_unmeasured(receipt, label=relative)
            return owner, receipt
        return owner, None

    families: dict[str, Any] = {}
    for family in ("c", "rust"):
        record = by_family[family]
        observed = record.get("correctness_evidence")
        require(record.get("correctness") == "FAILED; NOT QUALIFIED"
                and type(observed) is dict
                and observed.get("expected_gate_status") == "FAIL"
                and observed.get("qualified_case_executions") == 0,
                "never convert a failed C or Rust correctness run into qualification")
        owners: list[dict[str, Any]] = []
        for role in ("archive", "receipt", "worker_archive", "worker_receipt"):
            path, digest = EXPECTED_OUTER[family][role]
            entry = observed.get(role)
            require(type(entry) is dict and entry.get("path") == path
                    and entry.get("sha256") == digest,
                    "the exact published failed candidate evidence was substituted")
            owner, receipt = evidence(path, digest)
            if receipt is not None:
                require(receipt.get("candidate_family") == family
                        and receipt.get("candidate_status") == "FAIL"
                        and receipt.get("failure_preserved") is True
                        and receipt.get("candidate_qualified_for_hidden_benchmark") is False,
                        "a successful publication is not a successful candidate")
            owners.append(owner)
        subordinate = record.get("subordinate_evidence")
        require(type(subordinate) is list and len(subordinate) == 12,
                "preserve six independently published subordinate evidence pairs")
        for item in subordinate:
            require(type(item) is dict and set(item) == {"path", "sha256"},
                    "require the exact path and digest of every subordinate owner")
            path = checked_relative(item["path"])
            require((path.startswith("experiments/rust_public_practice_v1/" + family + "-")
                     or path.startswith(
                         "oracle/phase2/evidence/owned-candidate-subinterpreters-v1-"
                         + family + "-"))
                    and path.endswith((".json", ".json.gz")),
                    "reject foreign or cross-family subordinate evidence")
            owner, _ = evidence(path, checked_digest(item["sha256"], path))
            owners.append(owner)
        restoration = frozen.get("v5_" + family + "_restoration_receipt")
        restore_path, restore_digest = EXPECTED_OUTER[family]["restoration"]
        require(type(restoration) is dict
                and restoration.get("path") == restore_path
                and restoration.get("sha256") == restore_digest,
                "preserve the genuine candidate restoration receipt")
        owner, _ = evidence(restore_path, restore_digest)
        owners.append(owner)
        require(len(owners) == 17,
                "each genuinely tested family has exactly 17 evidence file owners")
        families[family] = {
            "owner_count": 17, "result_status": "FAIL",
            "qualified_candidate_count": 0, "owners": owners,
        }

    zig_owners: list[dict[str, Any]] = []
    for role, item in ZIG_FAILURE_PAIRS.items():
        archive, _ = evidence(item["archive"], item["archive_sha256"],
                              item["archive_bytes"])
        receipt_owner, receipt = evidence(item["receipt"], item["receipt_sha256"],
                                          item["receipt_bytes"])
        require(receipt is not None
                and receipt.get("uncompressed_sha256") == item["plain_sha256"]
                and receipt.get("uncompressed_bytes") == item["plain_bytes"],
                "retain the exact complete real Zig failure archive")
        if role == "subinterpreters":
            require(receipt.get("result_status") == "FAIL"
                    and receipt.get("candidate_family") == "zig"
                    and receipt.get("phase1_case_execution_denominator") == 31237,
                    "never promote the actual Zig subinterpreter failure")
        else:
            require(receipt.get("candidate_family") == "zig"
                    and receipt.get("candidate_status") == "FAIL"
                    and receipt.get("failure_preserved") is True
                    and receipt.get("candidate_qualified_for_hidden_benchmark") is False,
                    "never promote the actual failed Zig candidate or worker")
        zig_owners.extend((archive, receipt_owner))
    for path, digest, size in ZIG_V6_SUBORDINATE:
        owner, _ = evidence(path, digest, size)
        zig_owners.append(owner)
    restore_path, restore_digest, restore_size = ZIG_RESTORATION
    restoration_owner, restoration = evidence(restore_path, restore_digest, restore_size)
    require(restoration is not None
            and restoration.get("schema")
            == "rebar-phase2-verified-native-candidate-activation-v2-restoration-receipt"
            and restoration.get("family") == "zig"
            and restoration.get("promotion_mode") == "recoverable-canonical-promotion",
            "preserve the genuine reportless-safe owner-only Zig restoration")
    zig_owners.append(restoration_owner)
    require(len(zig_owners) == 17 and len(identities) == 51,
            "preserve exactly 51 distinct C, Rust, and Zig evidence file owners")
    families["zig"] = {
        "owner_count": 17, "result_status": "FAIL",
        "qualified_candidate_count": 0, "owners": zig_owners,
    }
    return {
        "family_count": 3, "owner_count": 51, "owners_per_family": 17,
        "families": families, "qualified_candidate_count": 0,
        "semantic_mismatch_counts": copy.deepcopy(
            expected_evidence_accounting()["historical_candidate_semantic_mismatch_counts"]
        ),
        "snapshot_fortran_build_status": "NOT BUILT; SNAPSHOT PREDATES ACTUAL V4 FAILURE",
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }


def expected_v2_summaries() -> list[dict[str, Any]]:
    return [
        {"family": item["family"], "build_status": item["build_status"],
         "process_count": item["process_count"],
         "archive_sha256": item["archive_sha256"],
         "receipt_sha256": item["receipt_sha256"],
         "historical_v1_symbol_audit": "FALSIFIED AND PRESERVED",
         "failure_preserved": item["build_status"] == "FAIL"}
        for item in EXPECTED_HISTORY_V2.values()
    ]


def validate_v4_processes(kernel: types.ModuleType, family: str,
                          processes: Any) -> dict[tuple[str, str], bytes]:
    family = checked_family(family)
    require(family in ("cpp", "go", "fortran"),
            "validate only genuine recorded V4 source-build history")
    if family == "cpp":
        schedule = [
            (phase, name)
            for phase in ("reference-a", "reference-b")
            for name in ("readelf_version", "gxx_version", "build_cpp_bridge",
                         "bridge_dynamic", "bridge_symbols")
        ]
    elif family == "go":
        schedule = [
            ("reference-a", name)
            for name in ("readelf_version", "gcc_version", "go_version",
                         "build_go_engine")
        ]
    else:
        schedule = [
            (phase, name)
            for phase in ("reference-a", "reference-b")
            for name in (
                "readelf_version", "gcc_version", "gfortran_version",
                "build_fortran_engine", "build_fortran_bridge",
                "engine_dynamic", "engine_symbols",
                "bridge_dynamic", "bridge_symbols",
            )
        ]
    require(type(processes) is list and len(processes) == len(schedule),
            "retain every actual V4 compiler and ELF inspection process")
    root = "/tmp/rebar-phase2-native-build-v4-" + family + "-synthetic"
    pids: set[int] = set()
    streams: dict[tuple[str, str], bytes] = {}
    for process, (phase, name) in zip(processes, schedule, strict=True):
        require(type(process) is dict and process.get("name") == name
                and type(process.get("pid")) is int and process["pid"] > 0
                and process["pid"] not in pids and process.get("shell") is False,
                "reject an omitted, fabricated, duplicated, or shell-based V4 process")
        pids.add(process["pid"])
        commands = kernel.planned_commands(root, family, phase)
        expected_argv = [kernel.sanitized(value, root, family)
                         for value in commands[name]]
        expected_environment = {
            key: kernel.sanitized(value, root, family)
            for key, value in sorted(kernel.build_environment(root, family, phase).items())
        }
        expected_directory = kernel.sanitized(str(kernel.command_working_directory(
            root, family, phase, name)), root, family)
        require(process.get("argv") == expected_argv
                and process.get("environment") == expected_environment
                and process.get("working_directory") == expected_directory,
                "the actual historical compiler, package directory, or offline cache changed")
        stdout = decode_process_stream(process, "stdout")
        stderr = decode_process_stream(process, "stderr")
        streams[(phase, name)] = stdout
        if family == "go" and name == "build_go_engine":
            require(process.get("exit_status") == 1
                    and stdout == b"" and stderr == GO_FAILURE_STDERR
                    and process.get("stderr_sha256")
                    == HISTORICAL_V4["go"]["stderr_sha256"]
                    and process.get("stderr_bytes") == 175
                    and expected_directory
                    == "<FRESH_PRIVATE_TMP>/reference-a/source/candidates/go",
                    "preserve the real V4 co-located Python bridge Go failure byte for byte")
        else:
            require(type(process.get("exit_status")) is int
                    and process.get("exit_status") == 0,
                    "do not hide a failed historical compiler or ELF inspection")
            if name.endswith("_version"):
                kernel.validate_compiler_version(name, stdout)
            elif name.endswith(("_dynamic", "_symbols")):
                require(bool(stdout), "retain complete actual historical ELF inspection output")
    return streams


def validate_failed_fortran_phases(
    kernel: types.ModuleType,
    report: dict[str, Any],
    streams: dict[tuple[str, str], bytes],
) -> dict[str, Any]:
    specification = HISTORICAL_V4["fortran"]
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == 2
            and [item.get("name") for item in phases]
            == ["reference-a", "reference-b"]
            and report.get("reproducibility") is None
            and report.get("error") == {
                "type": "BuildError",
                "message": "the two independently owned outputs are not genuinely byte-identical",
            },
            "preserve two actually completed Fortran builds and the genuine reproducibility failure")
    source_identities: set[tuple[int, int]] = set()
    artifact_identities: set[tuple[int, int]] = set()
    for index, phase in enumerate(phases):
        phase_name = phase["name"]
        sources = phase.get("fresh_source_owners")
        require(type(sources) is dict
                and set(sources) == set(SOURCE_OWNERS["fortran"]),
                "each completed Fortran phase requires all three actual owned sources")
        for relative, (digest, size) in SOURCE_OWNERS["fortran"].items():
            owner = sources[relative]
            require(type(owner) is dict and owner.get("sha256") == digest
                    and owner.get("bytes") == size
                    and type(owner.get("device")) is int and owner["device"] > 0
                    and type(owner.get("inode")) is int and owner["inode"] > 0,
                    "retain the actual complete independent Fortran source phase")
            identity = (owner["device"], owner["inode"])
            require(identity not in source_identities,
                    "the recorded Fortran source phases shared an owner inode")
            source_identities.add(identity)
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict and set(outputs) == {"engine", "bridge"},
                "both genuine Fortran phases completed both native binary outputs")
        for role in ("engine", "bridge"):
            output = outputs[role]
            require(type(output) is dict
                    and output.get("file_name")
                    == FAMILIES["fortran"]["artifacts"][role]
                    and type(output.get("device")) is int and output["device"] > 0
                    and type(output.get("inode")) is int and output["inode"] > 0,
                    "preserve both actual first-party Fortran native output owners")
            identity = (output["device"], output["inode"])
            require(identity not in artifact_identities,
                    "the recorded Fortran phases shared a native output inode")
            artifact_identities.add(identity)
            actual_audit = kernel.validate_elf(
                "fortran", role,
                kernel.parse_elf_dynamic(streams[(phase_name, role + "_dynamic")]),
                kernel.parse_elf_symbols(streams[(phase_name, role + "_symbols")]),
            )
            require(output.get("audit") == actual_audit,
                    "independently verify every original Fortran native symbol and callback")
            if role == "engine":
                expected_hash = specification[
                    "engine_phase_a_sha256" if index == 0
                    else "engine_phase_b_sha256"
                ]
                require(output.get("sha256") == expected_hash
                        and output.get("size_bytes")
                        == specification["engine_bytes_per_phase"]
                        and len(actual_audit.get("required_exports", [])) == 9,
                        "retain the two genuine equal-sized but non-identical Fortran engines")
            else:
                require(output.get("sha256")
                        == specification["identical_bridge_sha256"]
                        and output.get("size_bytes")
                        == specification["bridge_bytes_per_phase"],
                        "retain the genuine byte-identical independently compiled Fortran bridge")
                callbacks = {
                    item for item in actual_audit.get("exports", [])
                    if item.startswith("rebar_fortran_")
                }
                require(len(callbacks) == 3,
                        "preserve all three genuine first-party Fortran reverse callbacks")
    require(len(source_identities) == 6 and len(artifact_identities) == 4,
            "preserve complete distinct source and output inodes for both Fortran phases")
    return {
        "completed_build_phase_count": 2,
        "successful_process_count": 18,
        "engine_phase_a_sha256": specification["engine_phase_a_sha256"],
        "engine_phase_b_sha256": specification["engine_phase_b_sha256"],
        "engine_bytes_per_phase": specification["engine_bytes_per_phase"],
        "identical_bridge_sha256": specification["identical_bridge_sha256"],
        "bridge_bytes_per_phase": specification["bridge_bytes_per_phase"],
        "differing_binary_section": "NOT RECORDED",
        "failure_preserved": True,
    }


def verify_historical_v4(kernel: types.ModuleType,
                         identities: set[tuple[int, int]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for family, spec in HISTORICAL_V4.items():
        archive_raw, archive_owner = read_owned(
            spec["archive_path"], spec["archive_sha256"],
            maximum=MAX_ARCHIVE_BYTES, exact_size=spec["archive_bytes"],
            capture=True, owner_only=True,
        )
        receipt_raw, receipt_owner = read_owned(
            spec["receipt_path"], spec["receipt_sha256"],
            maximum=MAX_SOURCE_BYTES, exact_size=spec["receipt_bytes"],
            capture=True, owner_only=True,
        )
        require(archive_raw is not None and receipt_raw is not None,
                "retain the complete actual V4 archive and durable receipt")
        for owner in (archive_owner, receipt_owner):
            identity = (owner["device"], owner["inode"])
            require(identity not in identities,
                    "do not reuse a historical candidate or V4 evidence file owner")
            identities.add(identity)
        plain = bounded_gzip(archive_raw, exact_size=spec["uncompressed_bytes"])
        require(sha256(plain) == spec["uncompressed_sha256"],
                "the full historical V4 build report was changed")
        report = decode_json(plain, canonical_required=True)
        receipt = decode_json(receipt_raw, canonical_required=True)
        require(report.get("schema") == kernel.SCHEMA
                and report.get("version") == 4
                and report.get("family") == family
                and report.get("label") == "phase2-v4"
                and report.get("status") == spec["build_status"]
                and report.get("source_sha256") == EXPECTED_SUPPORT["build_recorder_v4"][1]
                and report.get("protocol_sha256") == EXPECTED_SUPPORT["build_protocol_v4"][1]
                and report.get("contract_sha256") == EXPECTED_SUPPORT["build_contract_v4"][1],
                "preserve exact V4 build identity and authentic PASS or FAIL")
        require(receipt.get("schema") == kernel.RECEIPT_SCHEMA
                and receipt.get("status") == "PASS"
                and receipt.get("build_status") == spec["build_status"]
                and receipt.get("family") == family
                and receipt.get("archive_relative") == spec["archive_path"]
                and receipt.get("archive_sha256") == spec["archive_sha256"]
                and receipt.get("archive_bytes") == spec["archive_bytes"]
                and receipt.get("uncompressed_sha256") == spec["uncompressed_sha256"]
                and receipt.get("uncompressed_bytes") == spec["uncompressed_bytes"]
                and receipt.get("source_sha256") == report["source_sha256"]
                and receipt.get("protocol_sha256") == report["protocol_sha256"]
                and receipt.get("contract_sha256") == report["contract_sha256"],
                "a durable receipt must not reverse the genuine V4 build result")
        publication = receipt.get("archive_publication")
        sync = receipt.get("archive_directory_fsync")
        require(type(publication) is dict
                and publication.get("path") == archive_owner["path"]
                and publication.get("sha256") == archive_owner["sha256"]
                and publication.get("bytes") == archive_owner["size_bytes"]
                and publication.get("device") == archive_owner["device"]
                and publication.get("inode") == archive_owner["inode"]
                and publication.get("exclusive_creation") is True
                and publication.get("same_inode_readback_verified") is True
                and publication.get("file_fsync_completed") is True
                and type(publication.get("write_calls")) is int
                and publication["write_calls"] > 0
                and type(sync) is dict and sync.get("completed") is True,
                "retain actual private exclusive publication and directory synchronization")
        expected_pins = {
            path: digest for path, (digest, _) in SOURCE_OWNERS[family].items()
        }
        require(report.get("owned_source_sha256") == expected_pins
                and receipt.get("owned_source_sha256") == expected_pins
                and report.get("preserved_v2_history") == expected_v2_summaries(),
                "retain complete owned V4 sources and the genuine 39-process V2 history")
        frozen = report.get("frozen_correctness")
        require(type(frozen) is dict and frozen.get("status") == "PASS"
                and frozen.get("suite_count") == 13
                and frozen.get("case_execution_count") == 31237
                and frozen.get("candidate_qualified_count") == 0,
                "do not inflate the unchanged full 31,237-execution correctness denominator")
        require_unmeasured(report, label=spec["archive_path"])
        require_unmeasured(receipt, label=spec["receipt_path"])
        streams = validate_v4_processes(kernel, family, report.get("processes"))
        fortran_phase_evidence = None
        if family == "cpp":
            reproduction = kernel.verify_reproducible_phases(
                family, report.get("build_phases"), report["processes"],
            )
            require(report.get("reproducibility") == reproduction
                    and reproduction.get("byte_identical") is True
                    and reproduction.get("independent_fresh_phase_count") == 2,
                    "retain the genuine independently reproducible C++ source build")
        elif family == "go":
            require(report.get("build_phases") == []
                    and report.get("reproducibility") is None
                    and report.get("error") == {
                        "type": "BuildError",
                        "message": "the exact independently owned compiler or ELF command failed: build_go_engine",
                    },
                    "retain the authentic Go package-isolation failure; do not invent a completed phase")
        else:
            fortran_phase_evidence = validate_failed_fortran_phases(
                kernel, report, streams,
            )
        result.append({
            "family": family, "build_status": spec["build_status"],
            "receipt_status": "PASS", "process_count": spec["process_count"],
            "archive": archive_owner, "receipt": receipt_owner,
            "failure_preserved": spec["build_status"] == "FAIL",
            "candidate_qualified_count": 0,
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
            "completed_fortran_failure_evidence": fortran_phase_evidence,
        })
    return result


def expected_v5_process_schedule(
    family: str, specification: dict[str, Any],
) -> list[tuple[str, str]]:
    family = checked_family(family)
    if family == "go":
        full = [
            ("reference-a", name)
            for name in (
                "readelf_version", "gcc_version", "go_version",
                "build_go_engine", "build_go_bridge",
            )
        ]
    elif family == "fortran":
        one_phase = (
            "readelf_version", "gcc_version", "gfortran_version",
            "build_fortran_engine", "build_fortran_bridge",
            "engine_dynamic", "engine_symbols",
            "bridge_dynamic", "bridge_symbols",
            "engine_sections", "engine_notes",
            "bridge_sections", "bridge_notes",
        )
        full = [
            (phase, name)
            for phase in ("reference-a", "reference-b")
            for name in one_phase
        ]
    else:
        raise BuildError("validate only actually preserved V5 Go or Fortran reports")
    count = specification.get("process_count")
    require(type(count) is int and 0 < count <= len(full),
            "freeze only the exact actual recorded V5 compiler-process prefix")
    return full[:count]


def validate_historical_v5_processes(
    module: types.ModuleType,
    kernel: types.ModuleType,
    family: str,
    processes: Any,
    specification: dict[str, Any],
) -> dict[tuple[str, str], tuple[bytes, bytes, int]]:
    schedule = expected_v5_process_schedule(family, specification)
    require(type(processes) is list and len(processes) == len(schedule),
            "retain every real V5 process without completing a failed phase")
    root = "/tmp/rebar-phase2-native-build-v5-" + family + "-synthetic"
    pids: set[int] = set()
    streams: dict[tuple[str, str], tuple[bytes, bytes, int]] = {}
    successes = 0
    for process, (phase, name) in zip(processes, schedule, strict=True):
        require(type(process) is dict and process.get("name") == name
                and type(process.get("pid")) is int and process["pid"] > 0
                and process["pid"] not in pids and process.get("shell") is False,
                "reject an omitted, reordered, duplicated, shell, or forged V5 process")
        pids.add(process["pid"])
        actual = module.planned_commands(root, family, phase)
        expected_argv = [
            module.sanitized(value, root, family)
            for value in actual[name]
        ]
        expected_environment = {
            key: module.sanitized(value, root, family)
            for key, value in sorted(
                module.build_environment(root, family, phase).items()
            )
        }
        expected_directory = module.sanitized(
            str(module.command_working_directory(root, family, phase, name)),
            root, family,
        )
        require(process.get("argv") == expected_argv
                and process.get("environment") == expected_environment
                and process.get("working_directory") == expected_directory,
                "the authentic V5 compiler, private Go package, or offline caches changed")
        stdout = decode_process_stream(process, "stdout")
        stderr = decode_process_stream(process, "stderr")
        status = process.get("exit_status")
        require(type(status) is int,
                "preserve the actual signed V5 compiler exit status")
        if name == specification.get("failed_process"):
            require(status == 1 and process is processes[-1],
                    "preserve the exact last genuinely failing V5 compiler")
        else:
            require(status == 0,
                    "do not relabel an actual successful V5 compiler or inspection")
            successes += 1
            if name.endswith("_version"):
                kernel.validate_compiler_version(name, stdout)
            if name.endswith(("_dynamic", "_symbols", "_sections")):
                require(bool(stdout),
                        "retain the complete authentic V5 native ELF stream")
        streams[(phase, name)] = (stdout, stderr, process["pid"])
    require(successes == specification["successful_process_count"]
            and len(pids) == specification["process_count"],
            "retain exact per-run V5 process identities and actual successful count")
    if family == "go":
        _, engine_stderr, _ = streams[("reference-a", "build_go_engine")]
        _, bridge_stderr, _ = streams[("reference-a", "build_go_bridge")]
        bridge = processes[-1]
        require(engine_stderr == b""
                and specification["go_engine_compiler_status"] == "PASS"
                and specification["go_bridge_compiler_status"] == "FAIL"
                and bridge.get("stderr_bytes") == specification["stderr_bytes"]
                and bridge.get("stderr_sha256") == specification["stderr_sha256"]
                and len(bridge_stderr) == specification["stderr_bytes"]
                and sha256(bridge_stderr) == specification["stderr_sha256"]
                and b"PY_SSIZE_T_MAX" in bridge_stderr
                and b"SSIZE_MAX" in bridge_stderr
                and b"undeclared" in bridge_stderr
                and "-D_GNU_SOURCE" not in bridge["argv"]
                and bridge["argv"].count("-include") == 1,
                "preserve the exact five-process GNU-feature V5 Go failure byte for byte")
    return streams


def validate_failed_v5_fortran_phases(
    module: types.ModuleType,
    kernel: types.ModuleType,
    report: dict[str, Any],
    streams: dict[tuple[str, str], tuple[bytes, bytes, int]],
    specification: dict[str, Any],
) -> dict[str, Any]:
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == 2
            and [phase.get("name") for phase in phases]
            == ["reference-a", "reference-b"]
            and report.get("reproducibility") is None
            and report.get("error") == {
                "type": "BuildError",
                "message": (
                    "the two independently owned outputs "
                    "are not genuinely byte-identical"
                ),
            },
            "preserve both genuinely completed V5 Fortran phases and the exact failure")
    root = "/tmp/rebar-phase2-native-build-v5-fortran-synthetic"
    source_identities: set[tuple[int, int]] = set()
    native_identities: set[tuple[int, int]] = set()
    snapshots: list[dict[str, Any]] = []
    for phase in phases:
        name = phase["name"]
        paths = module.phase_paths(root, "fortran", name)
        require(phase.get("fresh_source_directory")
                == module.sanitized(str(paths["source"]), root, "fortran")
                and phase.get("fresh_native_directory")
                == module.sanitized(str(paths["native"]), root, "fortran")
                and phase.get("fresh_temporary_directory")
                == module.sanitized(str(paths["temporary"]), root, "fortran"),
                "retain distinct genuinely private V5 Fortran phase directories")
        sources = phase.get("fresh_source_owners")
        require(type(sources) is dict
                and set(sources) == set(SOURCE_OWNERS["fortran"]),
                "retain every independently snapshotted first-party Fortran source")
        for relative, (digest, size) in SOURCE_OWNERS["fortran"].items():
            owner = sources[relative]
            identity = (owner.get("device"), owner.get("inode"))
            require(type(owner) is dict
                    and owner.get("path")
                    == module.sanitized(str(paths["source"] / relative),
                                        root, "fortran")
                    and owner.get("sha256") == digest
                    and owner.get("bytes") == size
                    and type(identity[0]) is int and identity[0] > 0
                    and type(identity[1]) is int and identity[1] > 0
                    and identity not in source_identities
                    and owner.get("exclusive_creation") is True
                    and owner.get("same_inode_readback_verified") is True
                    and owner.get("file_fsync_completed") is False
                    and type(owner.get("write_calls")) is int
                    and owner["write_calls"] > 0,
                    "preserve each authentic private V5 Fortran source snapshot without inventing an fsync")
            source_identities.add(identity)
        outputs = phase.get("native_outputs")
        diagnostics = phase.get("native_forensics")
        require(type(outputs) is dict and set(outputs) == {"engine", "bridge"}
                and type(diagnostics) is dict
                and set(diagnostics) == {"engine", "bridge"},
                "retain both actual independently inspected Fortran native roles")
        checked: dict[str, Any] = {}
        for role in ("engine", "bridge"):
            output = outputs[role]
            identity = (output.get("device"), output.get("inode"))
            require(type(output) is dict
                    and output.get("family") == "fortran"
                    and output.get("role") == role
                    and output.get("file_name")
                    == FAMILIES["fortran"]["artifacts"][role]
                    and output.get("path")
                    == module.sanitized(str(paths["artifact_" + role]),
                                        root, "fortran")
                    and type(identity[0]) is int and identity[0] > 0
                    and type(identity[1]) is int and identity[1] > 0
                    and identity not in native_identities
                    and output.get("prebuilt_artifact_read") is False
                    and output.get("candidate_imported") is False,
                    "reject a foreign, prebuilt, substituted, or shared Fortran binary")
            native_identities.add(identity)
            dynamic, _, _ = streams[(name, role + "_dynamic")]
            symbols, _, _ = streams[(name, role + "_symbols")]
            actual_audit = kernel.validate_elf(
                "fortran", role,
                kernel.parse_elf_dynamic(dynamic),
                kernel.parse_elf_symbols(symbols),
            )
            require(output.get("audit") == actual_audit,
                    "bind complete real V5 native symbols and dependencies to their process")
            for operation in ("sections", "notes"):
                forensic = diagnostics[role][operation]
                stdout, _, pid = streams[(name, role + "_" + operation)]
                require(type(forensic) is dict
                        and forensic.get("command") == role + "_" + operation
                        and forensic.get("process_pid") == pid
                        and forensic.get("stdout_sha256") == sha256(stdout)
                        and forensic.get("stdout_bytes") == len(stdout)
                        and forensic.get("section_payload_digests")
                        == "NOT RECORDED",
                        "preserve full actual Fortran sections and notes, never invent raw sections")
            checked[role] = output
        snapshots.append(checked)
    first, second = snapshots
    engine_a, engine_b = first["engine"], second["engine"]
    bridge_a, bridge_b = first["bridge"], second["bridge"]
    require(engine_a.get("sha256") == specification["engine_phase_a_sha256"]
            and engine_b.get("sha256") == specification["engine_phase_b_sha256"]
            and engine_a["sha256"] != engine_b["sha256"]
            and engine_a.get("size_bytes")
            == engine_b.get("size_bytes")
            == specification["engine_bytes_per_phase"]
            and engine_a.get("audit") == engine_b.get("audit")
            and bridge_a.get("sha256")
            == bridge_b.get("sha256")
            == specification["identical_bridge_sha256"]
            and bridge_a.get("size_bytes")
            == bridge_b.get("size_bytes")
            == specification["bridge_bytes_per_phase"]
            and bridge_a.get("audit") == bridge_b.get("audit")
            and len(source_identities) == 6
            and len(native_identities) == 4,
            "preserve actual different Fortran engines and identical independent bridges")
    first_note, _, _ = streams[("reference-a", "engine_notes")]
    second_note, _, _ = streams[("reference-b", "engine_notes")]
    first_section, _, _ = streams[("reference-a", "engine_sections")]
    second_section, _, _ = streams[("reference-b", "engine_sections")]
    bridge_note_a, _, _ = streams[("reference-a", "bridge_notes")]
    bridge_note_b, _, _ = streams[("reference-b", "bridge_notes")]
    require(len(first_note) == len(second_note)
            == specification["engine_notes_bytes_per_phase"]
            and sha256(first_note) == specification["engine_phase_a_notes_sha256"]
            and sha256(second_note) == specification["engine_phase_b_notes_sha256"]
            and first_note != second_note
            and specification["phase_a_observed_gnu_build_id"].encode("ascii")
            in first_note
            and specification["phase_b_observed_gnu_build_id"].encode("ascii")
            in second_note
            and len(first_section) == len(second_section)
            == specification["engine_sections_bytes_per_phase"]
            and sha256(first_section)
            == sha256(second_section)
            == specification["identical_engine_sections_sha256"]
            and first_section == second_section
            and len(bridge_note_a) == len(bridge_note_b)
            == specification["bridge_notes_bytes_per_phase"]
            and sha256(bridge_note_a)
            == sha256(bridge_note_b)
            == specification["identical_bridge_notes_sha256"]
            and bridge_note_a == bridge_note_b
            and specification["differing_raw_binary_section"] == "NOT RECORDED",
            "preserve full signed differing GNU notes without inventing the sole raw cause")
    return {
        "phase_count": 2,
        "compiler_process_count": 26,
        "successful_process_count": 26,
        "engine_phase_a_sha256": engine_a["sha256"],
        "engine_phase_b_sha256": engine_b["sha256"],
        "engine_bytes_per_phase": specification["engine_bytes_per_phase"],
        "identical_bridge_sha256": bridge_a["sha256"],
        "bridge_bytes_per_phase": specification["bridge_bytes_per_phase"],
        "engine_phase_a_notes_sha256": specification["engine_phase_a_notes_sha256"],
        "engine_phase_b_notes_sha256": specification["engine_phase_b_notes_sha256"],
        "engine_notes_bytes_per_phase": specification["engine_notes_bytes_per_phase"],
        "phase_a_observed_gnu_build_id": specification["phase_a_observed_gnu_build_id"],
        "phase_b_observed_gnu_build_id": specification["phase_b_observed_gnu_build_id"],
        "identical_engine_sections_sha256":
            specification["identical_engine_sections_sha256"],
        "differing_raw_binary_section": "NOT RECORDED",
        "failure_preserved": True,
    }


def verify_historical_v5(
    module: types.ModuleType,
    kernel: types.ModuleType,
    identities: set[tuple[int, int]],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    v5_kernel = load_frozen_v4()
    module.install_v5_build_kernel(v5_kernel)
    for family, specification in HISTORICAL_V5.items():
        archive_raw, archive_owner = read_owned(
            specification["archive_path"], specification["archive_sha256"],
            maximum=MAX_ARCHIVE_BYTES,
            exact_size=specification["archive_bytes"],
            capture=True, owner_only=True,
        )
        receipt_raw, receipt_owner = read_owned(
            specification["receipt_path"], specification["receipt_sha256"],
            maximum=MAX_SOURCE_BYTES,
            exact_size=specification["receipt_bytes"],
            capture=True, owner_only=True,
        )
        require(archive_raw is not None and receipt_raw is not None,
                "retain the complete separately published real V5 report and receipt")
        for owner in (archive_owner, receipt_owner):
            identity = (owner["device"], owner["inode"])
            require(identity not in identities,
                    "never reuse a candidate, V4, or V5 evidence owner")
            identities.add(identity)
        plain = bounded_gzip(
            archive_raw, exact_size=specification["uncompressed_bytes"],
        )
        require(sha256(plain) == specification["uncompressed_sha256"],
                "the full preserved actual V5 source-build report changed")
        report = decode_json(plain, canonical_required=True)
        receipt = decode_json(receipt_raw, canonical_required=True)
        require(report.get("schema") == module.SCHEMA
                and report.get("version") == 5
                and report.get("family") == family
                and report.get("label") == "phase2-v5"
                and report.get("status") == specification["build_status"]
                and report.get("source_sha256")
                == EXPECTED_SUPPORT["build_recorder_v5"][1]
                and report.get("protocol_sha256")
                == EXPECTED_SUPPORT["build_protocol_v5"][1]
                and report.get("contract_sha256")
                == EXPECTED_SUPPORT["build_contract_v5"][1],
                "preserve the genuine V5 source freeze, family, label, and outcome")
        require(receipt.get("schema") == module.RECEIPT_SCHEMA
                and receipt.get("status") == specification["receipt_status"]
                and receipt.get("build_status") == specification["build_status"]
                and receipt.get("family") == family
                and receipt.get("label") == "phase2-v5"
                and receipt.get("archive_relative")
                == specification["archive_path"]
                and receipt.get("archive_sha256")
                == specification["archive_sha256"]
                and receipt.get("archive_bytes")
                == specification["archive_bytes"]
                and receipt.get("uncompressed_sha256")
                == specification["uncompressed_sha256"]
                and receipt.get("uncompressed_bytes")
                == specification["uncompressed_bytes"]
                and all(receipt.get(key) == report.get(key)
                        for key in (
                            "source_sha256", "protocol_sha256",
                            "contract_sha256",
                            "expected_v5_compiler_process_count",
                            "actual_v5_compiler_process_count",
                        )),
                "a durable V5 receipt proves publication, never a false build outcome")
        publication = receipt.get("archive_publication")
        synchronization = receipt.get("archive_directory_fsync")
        require(type(publication) is dict
                and publication.get("path") == archive_owner["path"]
                and publication.get("sha256") == archive_owner["sha256"]
                and publication.get("bytes") == archive_owner["size_bytes"]
                and publication.get("device") == archive_owner["device"]
                and publication.get("inode") == archive_owner["inode"]
                and publication.get("exclusive_creation") is True
                and publication.get("same_inode_readback_verified") is True
                and publication.get("file_fsync_completed") is True
                and type(publication.get("write_calls")) is int
                and publication["write_calls"] > 0
                and type(synchronization) is dict
                and synchronization.get("completed") is True,
                "authenticate the real V5 exclusive archive publication and directory sync")
        expected_pins = {
            path: digest
            for path, (digest, _) in SOURCE_OWNERS[family].items()
        }
        require(report.get("owned_source_sha256") == expected_pins
                and receipt.get("owned_source_sha256") == expected_pins
                and report.get("evidence_accounting")
                == module.expected_evidence_accounting()
                and receipt.get("evidence_accounting")
                == module.expected_evidence_accounting()
                and report.get("preserved_v2_history")
                == module.expected_v2_summaries(),
                "retain the exact unmodified source ownership and honest 57-owner V5 baseline")
        expected_v4 = [
            {
                "family": name,
                "build_status": item["build_status"],
                "receipt_status": item["receipt_status"],
                "process_count": item["process_count"],
                "failure_preserved": item["build_status"] == "FAIL",
                "candidate_qualified_count": 0,
            }
            for name, item in HISTORICAL_V4.items()
        ]
        require(report.get("preserved_v4_history") == expected_v4
                and report.get("historical_candidate_evidence_owner_count") == 51
                and report.get("expected_v5_compiler_process_count")
                == specification["expected_process_count"]
                and report.get("actual_v5_compiler_process_count")
                == specification["process_count"],
                "do not silently inflate historical processes or erase genuine V4 failures")
        frozen = report.get("frozen_correctness")
        require(type(frozen) is dict and frozen.get("status") == "PASS"
                and frozen.get("suite_count") == 13
                and frozen.get("case_execution_count") == 31237
                and frozen.get("candidate_qualified_count") == 0,
                "preserve the unchanged whole 13-suite correctness denominator")
        require_unmeasured(report, label=specification["archive_path"])
        require_unmeasured(receipt, label=specification["receipt_path"])
        streams = validate_historical_v5_processes(
            module, kernel, family, report.get("processes"), specification,
        )
        phases = report.get("build_phases")
        require(type(phases) is list
                and len(phases) == specification["completed_build_phase_count"]
                and [phase.get("name") for phase in phases]
                == list(("reference-a", "reference-b"))[:len(phases)],
                "never invent, omit, or reorder an actually completed V5 build phase")
        if family == "go":
            require(not phases and report.get("reproducibility") is None
                    and report.get("go_private_package_reproducibility") is None
                    and report.get("error") == {
                        "type": "BuildError",
                        "message": (
                            "the exact independently owned compiler or ELF "
                            "command failed: build_go_bridge"
                        ),
                    },
                    "retain the real successful Go engine and failing bridge without a fake phase")
        elif family == "fortran":
            require(specification["build_status"] == "FAIL"
                    and report.get("reproducibility") is None,
                    "the actual V5 Fortran two-phase reproducibility result remains FAIL")
            forensic_evidence = validate_failed_v5_fortran_phases(
                module, v5_kernel, report, streams, specification,
            )
        else:
            raise BuildError("reject an invented V5 historical source-build family")
        result.append({
            "family": family,
            "build_status": specification["build_status"],
            "receipt_status": specification["receipt_status"],
            "process_count": specification["process_count"],
            "successful_process_count": specification["successful_process_count"],
            "completed_build_phase_count":
                specification["completed_build_phase_count"],
            "archive": archive_owner,
            "receipt": receipt_owner,
            "failure_preserved": specification["build_status"] == "FAIL",
            "candidate_qualified_count": 0,
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "completed_fortran_failure_evidence": (
                forensic_evidence if family == "fortran" else None
            ),
        })
    return result


def load_frozen_v6() -> types.ModuleType:
    relative, digest, size = EXPECTED_SUPPORT["build_recorder_v6"]
    raw, _ = read_owned(relative, digest, maximum=MAX_SOURCE_BYTES,
                        exact_size=size, capture=True)
    require(raw is not None,
            "authenticate every immutable byte of the exact published V6 recorder")
    module = types.ModuleType("_rebar_phase2_exact_frozen_v6_source_kernel")
    module.__dict__["__file__"] = str(ROOT / relative)
    module.__dict__["__package__"] = None
    exec(compile(raw, str(ROOT / relative), "exec"), module.__dict__)
    require(module.SCHEMA == "rebar-phase2-owned-native-source-build-v6"
            and module.SOURCE_OWNERS == SOURCE_OWNERS
            and module.FAMILIES == FAMILIES
            and module.EXPECTED_TOOLCHAINS == EXPECTED_TOOLCHAINS
            and module.EXPECTED_HISTORY_V2 == EXPECTED_HISTORY_V2
            and module.HISTORICAL_V4 == HISTORICAL_V4
            and module.HISTORICAL_V5 == HISTORICAL_V5
            and module.expected_evidence_accounting()
            ["distinct_evidence_file_owner_count"] == 61
            and module.expected_evidence_accounting()
            ["all_historical_versions_actual_compiler_process_count"] == 117,
            "reject a changed, incomplete, silently repaired, or miscounted V6 freeze")
    contract_path, contract_digest, contract_size = (
        EXPECTED_SUPPORT["build_contract_v6"]
    )
    contract_raw, _ = read_owned(
        contract_path, contract_digest, maximum=MAX_SOURCE_BYTES,
        exact_size=contract_size, capture=True,
    )
    require(contract_raw is not None,
            "authenticate the exact independently frozen V6 machine contract")
    module.validate_contract(module.decode_json(contract_raw))
    protocol_path, protocol_digest, protocol_size = (
        EXPECTED_SUPPORT["build_protocol_v6"]
    )
    _, _ = read_owned(
        protocol_path, protocol_digest, maximum=MAX_SOURCE_BYTES,
        exact_size=protocol_size, capture=False,
    )
    return module


def expected_v6_process_schedule(family: str) -> list[tuple[str, str]]:
    checked_family(family)
    if family == "go":
        names = (
            "readelf_version", "gcc_version", "go_version",
            "build_go_engine", "build_go_bridge",
            "engine_dynamic", "engine_symbols",
            "bridge_dynamic", "bridge_symbols",
            "engine_sections", "engine_notes",
            "bridge_sections", "bridge_notes",
        )
    elif family == "fortran":
        names = (
            "readelf_version", "gcc_version", "gfortran_version",
            "build_fortran_engine", "build_fortran_bridge",
            "engine_dynamic", "engine_symbols",
            "bridge_dynamic", "bridge_symbols",
            "engine_sections", "engine_notes",
            "bridge_sections", "bridge_notes",
        )
    else:
        raise BuildError("preserve only the two actually published V6 source builds")
    return [
        (phase, name)
        for phase in ("reference-a", "reference-b")
        for name in names
    ]


def validate_historical_v6_processes(
    module: types.ModuleType, kernel: types.ModuleType,
    family: str, processes: Any,
) -> dict[tuple[str, str], tuple[bytes, bytes, int]]:
    specification = HISTORICAL_V6[family]
    schedule = expected_v6_process_schedule(family)
    require(type(processes) is list
            and len(processes) == len(schedule)
            == specification["process_count"] == specification["expected_process_count"],
            "preserve all 26 actual V6 compiler and ELF inspector processes")
    root = "/tmp/rebar-phase2-native-build-v6-" + family + "-synthetic"
    streams: dict[tuple[str, str], tuple[bytes, bytes, int]] = {}
    pids: set[int] = set()
    for process, (phase, name) in zip(processes, schedule, strict=True):
        require(type(process) is dict and process.get("name") == name
                and type(process.get("pid")) is int and process["pid"] > 0
                and process["pid"] not in pids
                and process.get("shell") is False
                and type(process.get("exit_status")) is int
                and process["exit_status"] == 0,
                "reject a hidden, reused, failed, reordered, shell, or forged V6 process")
        pids.add(process["pid"])
        commands = module.planned_commands(root, family, phase)
        require(name in commands,
                "reject an invented or foreign actual V6 compiler command")
        expected_argv = [
            module.sanitized(value, root, family)
            for value in commands[name]
        ]
        expected_environment = {
            key: module.sanitized(value, root, family)
            for key, value in sorted(
                module.build_environment(root, family, phase).items()
            )
        }
        expected_directory = module.sanitized(
            str(module.command_working_directory(root, family, phase, name)),
            root, family,
        )
        require(process.get("argv") == expected_argv
                and process.get("environment") == expected_environment
                and process.get("working_directory") == expected_directory,
                "retain the exact published V6 command, offline environment, and root")
        stdout = decode_process_stream(process, "stdout")
        stderr = decode_process_stream(process, "stderr")
        require(stderr == b"",
                "all 52 published V6 Go and Fortran compiler streams really succeeded")
        if name.endswith("_version"):
            kernel.validate_compiler_version(name, stdout)
        if name.endswith(("_dynamic", "_symbols", "_sections")):
            require(bool(stdout),
                    "preserve the complete authenticated actual V6 ELF listing")
        streams[(phase, name)] = (stdout, stderr, process["pid"])
    require(len(streams) == len(pids) == 26,
            "bind every complete V6 stdout and stderr stream to a unique real process")
    return streams


def validate_historical_v6_phases(
    module: types.ModuleType, kernel: types.ModuleType,
    family: str, report: dict[str, Any],
    streams: dict[tuple[str, str], tuple[bytes, bytes, int]],
) -> dict[str, Any]:
    specification = HISTORICAL_V6[family]
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == 2
            and [phase.get("name") for phase in phases]
            == ["reference-a", "reference-b"],
            "preserve both complete actually executed V6 source-build phases")
    roles = set(FAMILIES[family]["artifacts"])
    source_identities: set[tuple[int, int]] = set()
    artifact_identities: set[tuple[int, int]] = set()
    engines: list[str] = []
    bridges: list[str] = []
    root = "/tmp/rebar-phase2-native-build-v6-" + family + "-synthetic"
    for phase in phases:
        name = phase["name"]
        fresh = phase.get("fresh_source_owners")
        require(type(fresh) is dict and set(fresh) == set(SOURCE_OWNERS[family]),
                "preserve all independently snapshotted real V6 semantic owners")
        for relative, (digest, size) in SOURCE_OWNERS[family].items():
            actual = fresh[relative]
            require(type(actual) is dict
                    and actual.get("sha256") == digest
                    and actual.get("bytes") == size
                    and type(actual.get("device")) is int
                    and type(actual.get("inode")) is int,
                    "reject a substituted, incomplete, or borrowed V6 source snapshot")
            identity = (actual["device"], actual["inode"])
            require(identity not in source_identities,
                    "never silently reuse a real cross-phase source inode")
            source_identities.add(identity)
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict and set(outputs) == roles,
                "preserve every genuinely built V6 native artifact and generated header")
        for role in roles:
            output = outputs[role]
            require(type(output) is dict
                    and type(output.get("device")) is int
                    and type(output.get("inode")) is int
                    and type(output.get("size_bytes")) is int
                    and output["size_bytes"] > 0,
                    "require the actual bounded V6 native artifact identity")
            identity = (output["device"], output["inode"])
            require(identity not in artifact_identities,
                    "reject reused V6 native artifacts or independent phase identities")
            artifact_identities.add(identity)
            if role == "engine":
                engines.append(output["sha256"])
                if family == "go":
                    require(output["sha256"] == specification["engine_sha256"]
                            and output["size_bytes"] == specification["engine_bytes"],
                            "preserve the exact actually reproducible Go engine")
                else:
                    require(output["sha256"] == specification[
                                "engine_phase_" + ("a" if name == "reference-a" else "b")
                                + "_sha256"
                            ]
                            and output["size_bytes"]
                            == specification["engine_bytes_per_phase"],
                            "preserve both distinct actual failed Fortran engine bytes")
            elif role == "bridge":
                bridges.append(output["sha256"])
                expected = (
                    specification["bridge_sha256"]
                    if family == "go"
                    else specification["identical_bridge_sha256"]
                )
                size = (
                    specification["bridge_bytes"]
                    if family == "go"
                    else specification["bridge_bytes_per_phase"]
                )
                require(output["sha256"] == expected
                        and output["size_bytes"] == size,
                        "preserve both real reproducible independently owned V6 bridges")
            else:
                require(family == "go" and role == "generated_header"
                        and output["sha256"] == specification["generated_header_sha256"]
                        and output["size_bytes"] == specification["generated_header_bytes"],
                        "the V6 generated Go header is build-only and exactly owned")
            audit = output.get("audit")
            require(type(audit) is dict,
                    "preserve each actually recorded owned native audit")
            if role != "generated_header":
                require(audit.get("role") == role
                        and audit.get("external_regex_dependency_count") == 0
                        and audit.get("cross_family_dependency_count") == 0,
                        "never delegate a historical V6 native artifact")
                if role == "bridge":
                    require(audit.get("runpath") == ["$ORIGIN"],
                            "preserve the exact authenticated first-party bridge RUNPATH")
                else:
                    require(len(audit.get("required_exports", [])) == 9,
                            "retain all nine actually recorded owned V6 engine exports")
        for key in ("candidate_imports", "candidate_processes_started",
                    "native_libraries_loaded", "hidden_cases_read",
                    "timing_trials_run"):
            require(type(phase.get(key)) is int and phase[key] == 0,
                    "a real V6 compiler phase did not run a matching candidate")
        forensic = phase.get("native_forensics")
        require(type(forensic) is dict
                and set(forensic) == (roles - {"generated_header"}),
                "preserve complete actual V6 section and note process streams")
        for role, operations in forensic.items():
            require(type(operations) is dict
                    and set(operations) == {"sections", "notes"},
                    "do not omit or invent a historical V6 raw-inspection process")
            for operation, evidence in operations.items():
                command = role + "_" + operation
                stdout, _, pid = streams[(name, command)]
                require(type(evidence) is dict
                        and evidence.get("command") == command
                        and evidence.get("stdout_sha256") == sha256(stdout)
                        and evidence.get("stdout_bytes") == len(stdout)
                        and evidence.get("process_pid") == pid
                        and evidence.get("section_payload_digests")
                        == "NOT RECORDED",
                        "preserve full V6 readelf output without inventing raw section bytes")
                if family == "fortran" and role == "engine" and operation == "notes":
                    require(stdout == b""
                            and len(stdout) == specification["engine_phase_notes_bytes"]
                            and sha256(stdout)
                            == specification["engine_phase_notes_sha256"],
                            "both actually failed Fortran engines genuinely have no build ID")
                if family == "fortran" and role == "engine" and operation == "sections":
                    require(sha256(stdout)
                            == specification["identical_engine_sections_sha256"]
                            and len(stdout)
                            == specification["engine_sections_bytes_per_phase"],
                            "retain both identical V6 section listings without guessing payload")
        if family == "go":
            module.validate_go_package_proof(
                phase.get("private_go_package"), root, name,
            )
    require(len(source_identities) == 2 * len(SOURCE_OWNERS[family])
            and len(artifact_identities) == 2 * len(roles),
            "require every actual V6 source and artifact inode to be independent")
    if family == "go":
        require(len(set(engines)) == len(set(bridges)) == 1,
                "the authentic two-phase Go source build was genuinely reproducible")
        reproduced = kernel.verify_reproducible_phases(
            family, phases, report["processes"],
        )
        require(report.get("reproducibility") == reproduced
                and reproduced.get("byte_identical") is True
                and reproduced.get("independent_fresh_phase_count") == 2,
                "authenticate the complete true independently reproducible V6 Go build")
        packages = module.verify_go_phase_proofs(root, phases, report["processes"])
        require(report.get("go_private_package_reproducibility") == packages
                and packages["distinct_package_member_inode_count"] == 4,
                "preserve both actual offline phase-private Go source packages")
    else:
        require(len(set(engines)) == 2 and len(set(bridges)) == 1
                and report.get("reproducibility") is None
                and report.get("go_private_package_reproducibility") is None
                and report.get("error") == {
                    "type": "BuildError",
                    "message": specification["failure_cause"],
                },
                "never promote the complete actual V6 Fortran reproducibility failure")
    return {
        "family": family,
        "completed_build_phase_count": 2,
        "successful_process_count": 26,
        "source_snapshot_identity_count": len(source_identities),
        "native_output_identity_count": len(artifact_identities),
        "engine_digests": engines,
        "bridge_digests": bridges,
        "raw_section_payload_status": "NOT RECORDED",
        "failure_preserved": family == "fortran",
    }


def verify_historical_v6(
    module: types.ModuleType, kernel: types.ModuleType,
    identities: set[tuple[int, int]],
) -> list[dict[str, Any]]:
    module.install_v6_build_kernel(kernel)
    preserved: list[dict[str, Any]] = []
    for family, specification in HISTORICAL_V6.items():
        archive, archive_owner = read_owned(
            specification["archive_path"], specification["archive_sha256"],
            maximum=MAX_ARCHIVE_BYTES,
            exact_size=specification["archive_bytes"],
            capture=True, owner_only=True,
        )
        receipt_bytes, receipt_owner = read_owned(
            specification["receipt_path"], specification["receipt_sha256"],
            maximum=MAX_SOURCE_BYTES,
            exact_size=specification["receipt_bytes"],
            capture=True, owner_only=True,
        )
        require(archive is not None and receipt_bytes is not None,
                "retain the whole actually signed V6 report and receipt")
        for owner in (archive_owner, receipt_owner):
            identity = (owner["device"], owner["inode"])
            require(identity not in identities,
                    "never double-count a candidate, V4, V5, or V6 evidence inode")
            identities.add(identity)
        plain = bounded_gzip(
            archive, exact_size=specification["uncompressed_bytes"],
        )
        require(sha256(plain) == specification["uncompressed_sha256"],
                "retain every original byte of the actual V6 source-build report")
        report = decode_json(plain, canonical_required=True)
        receipt = decode_json(receipt_bytes, canonical_required=True)
        require(report.get("schema") == module.SCHEMA
                and report.get("version") == 6
                and report.get("family") == family
                and report.get("label") == specification["label"]
                and report.get("status") == specification["build_status"]
                and report.get("source_sha256")
                == EXPECTED_SUPPORT["build_recorder_v6"][1]
                and report.get("protocol_sha256")
                == EXPECTED_SUPPORT["build_protocol_v6"][1]
                and report.get("contract_sha256")
                == EXPECTED_SUPPORT["build_contract_v6"][1]
                and report.get("expected_v6_compiler_process_count")
                == specification["expected_process_count"]
                and report.get("actual_v6_compiler_process_count")
                == specification["process_count"],
                "preserve the exact published V6 family, source, status, and 26 processes")
        require(receipt.get("schema") == module.RECEIPT_SCHEMA
                and receipt.get("status") == "PASS"
                and receipt.get("build_status") == specification["build_status"]
                and receipt.get("family") == family
                and receipt.get("label") == specification["label"]
                and receipt.get("archive_relative") == specification["archive_path"]
                and receipt.get("archive_sha256") == specification["archive_sha256"]
                and receipt.get("archive_bytes") == specification["archive_bytes"]
                and receipt.get("uncompressed_sha256")
                == specification["uncompressed_sha256"]
                and receipt.get("uncompressed_bytes")
                == specification["uncompressed_bytes"]
                and all(receipt.get(key) == report.get(key)
                        for key in (
                            "source_sha256", "protocol_sha256",
                            "contract_sha256", "expected_v6_compiler_process_count",
                            "actual_v6_compiler_process_count",
                        )),
                "a passing V6 publication receipt cannot promote a failed source build")
        publication = receipt.get("archive_publication")
        synchronization = receipt.get("archive_directory_fsync")
        require(type(publication) is dict
                and publication.get("path") == archive_owner["path"]
                and publication.get("sha256") == archive_owner["sha256"]
                and publication.get("bytes") == archive_owner["size_bytes"]
                and publication.get("device") == archive_owner["device"]
                and publication.get("inode") == archive_owner["inode"]
                and publication.get("exclusive_creation") is True
                and publication.get("same_inode_readback_verified") is True
                and publication.get("file_fsync_completed") is True
                and type(publication.get("write_calls")) is int
                and publication["write_calls"] > 0
                and type(synchronization) is dict
                and synchronization.get("completed") is True,
                "authenticate real mode-0600 exclusive V6 archive publication and sync")
        expected_pins = {
            path: item[0] for path, item in SOURCE_OWNERS[family].items()
        }
        require(report.get("owned_source_sha256") == expected_pins
                and receipt.get("owned_source_sha256") == expected_pins
                and report.get("evidence_accounting")
                == module.expected_evidence_accounting()
                and receipt.get("evidence_accounting")
                == module.expected_evidence_accounting()
                and report.get("historical_candidate_evidence_owner_count") == 51,
                "retain the actual immutable 61-owner V6 baseline without rewriting it")
        frozen = report.get("frozen_correctness")
        require(type(frozen) is dict and frozen.get("status") == "PASS"
                and frozen.get("suite_count") == 13
                and frozen.get("case_execution_count") == 31237
                and frozen.get("candidate_qualified_count") == 0,
                "preserve the unchanged original 13-suite V6 correctness denominator")
        require_unmeasured(report, label=specification["archive_path"])
        require_unmeasured(receipt, label=specification["receipt_path"])
        streams = validate_historical_v6_processes(
            module, kernel, family, report.get("processes"),
        )
        detail = validate_historical_v6_phases(
            module, kernel, family, report, streams,
        )
        preserved.append({
            "family": family,
            "build_status": specification["build_status"],
            "receipt_status": "PASS",
            "process_count": specification["process_count"],
            "successful_process_count": specification["successful_process_count"],
            "completed_build_phase_count": 2,
            "archive": archive_owner,
            "receipt": receipt_owner,
            "failure_preserved": family == "fortran",
            "candidate_qualified_count": 0,
            "forensics": detail,
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
        })
    return preserved


def verify_committed_v15_graph() -> dict[str, Any]:
    relative, digest, size = EXPECTED_SUPPORT["historical_candidate_graph_v15"]
    raw, owner = read_owned(
        relative, digest, maximum=MAX_SOURCE_BYTES,
        exact_size=size, capture=True,
    )
    require(raw is not None,
            "authenticate the complete committed truthful V15 evidence snapshot")
    graph = decode_json(raw, canonical_required=True)
    require(graph.get("schema") == "rebar-candidate-current-overview-v15-inputs"
            and graph.get("version") == 15
            and graph.get("suite_count") == 13
            and graph.get("full_case_denominator") == 31237,
            "retain the authentic original 13-suite, 31,237-case V15 evidence snapshot")
    boundary = graph.get("boundaries")
    require(type(boundary) is dict
            and boundary.get("actual_candidate_imports") == 0
            and boundary.get("actual_candidate_processes_started") == 0
            and boundary.get("clock_samples") == 0
            and boundary.get("hidden_cases_read") == 0
            and boundary.get("performance_files_read") == 0
            and boundary.get("timing_trials_run") == 0
            and boundary.get("final_holdout_authorized") is False
            and boundary.get("final_holdout_opened") is False
            and boundary.get("winner_selected") is False
            and boundary.get("full_candidate_correctness") == "NOT MEASURED"
            and boundary.get("performance") == "NOT MEASURED",
            "the real V15 history never opens a holdout or qualifies a candidate")
    frozen = graph.get("frozen_inputs")
    require(type(frozen) is dict,
            "retain the exact V15 independently pinned predecessor source closure")
    for role, support in (
        ("native_build_v6_runner", "build_recorder_v6"),
        ("native_build_v6_protocol", "build_protocol_v6"),
        ("native_build_v6_inventory", "build_contract_v6"),
    ):
        item = frozen.get(role)
        path, expected, _ = EXPECTED_SUPPORT[support]
        require(type(item) is dict and item.get("path") == path
                and item.get("sha256") == expected,
                "the authentic V15-to-V6 source lineage was altered")
    entries = graph.get("families")
    require(type(entries) is list,
            "require all genuinely documented V15 engine families")
    families = {
        item.get("family"): item for item in entries
        if type(item) is dict
    }
    require("go" in families and "fortran" in families,
            "retain both actual latest Go and Fortran source-build outcomes")
    for family, spec in HISTORICAL_V6.items():
        item = families[family]
        actual = item.get("build_evidence")
        require(type(actual) is dict
                and item.get("build_status") == spec["build_status"]
                and item.get("qualified") is False
                and actual.get("expected_build_status") == spec["build_status"]
                and actual.get("actual_process_count") == 26
                and actual.get("expected_complete_process_count") == 26
                and actual.get("successful_process_count") == 26
                and actual.get("failed_process_count") == 0
                and actual.get("matching_test_status") == "NOT MEASURED"
                and actual.get("qualified") is False,
                "preserve actual V15 source-build success separately from correctness")
        for role, path_key, digest_key in (
            ("archive", "archive_path", "archive_sha256"),
            ("receipt", "receipt_path", "receipt_sha256"),
        ):
            evidence = actual.get(role)
            require(type(evidence) is dict
                    and evidence.get("path") == spec[path_key]
                    and evidence.get("sha256") == spec[digest_key],
                    "pin the exact publicly rendered V6 report and receipt")
        if family == "go":
            require(actual.get("engine_sha256") == spec["engine_sha256"]
                    and actual.get("bridge_sha256") == spec["bridge_sha256"]
                    and actual.get("generated_header_sha256")
                    == spec["generated_header_sha256"]
                    and actual.get("required_engine_export_count")
                    == spec["required_engine_export_count"]
                    and actual.get("completed_phase_count") == 2
                    and actual.get("external_regex_dependency_count") == 0
                    and actual.get("cross_family_dependency_count") == 0,
                    "preserve the genuinely reproducible offline owned V6 Go engine")
        else:
            require(actual.get("first_engine_sha256")
                    == spec["engine_phase_a_sha256"]
                    and actual.get("second_engine_sha256")
                    == spec["engine_phase_b_sha256"]
                    and actual.get("engine_size_bytes")
                    == spec["engine_bytes_per_phase"]
                    and actual.get("bridge_sha256")
                    == spec["identical_bridge_sha256"]
                    and actual.get("bridge_size_bytes")
                    == spec["bridge_bytes_per_phase"]
                    and actual.get("completed_source_build_count") == 2
                    and actual.get("failure_preserved") is True
                    and actual.get("engine_reproduces") is False
                    and actual.get("bridge_reproduces") is True
                    and actual.get("engine_build_id_status") == "NOT PRESENT"
                    and actual.get("engine_notes_bytes") == 0
                    and actual.get("failure_reason") == spec["failure_cause"],
                    "preserve real falsification without inventing V6 raw section causes")
    return {
        "owner": owner,
        "version": 15,
        "family_count": len(entries),
        "genuine_v6_go_build_status": "PASS",
        "genuine_v6_fortran_build_status": "FAIL",
        "v6_go_process_count": 26,
        "v6_fortran_process_count": 26,
        "qualified_candidate_count": 0,
        "v6_fortran_raw_section_difference": "NOT RECORDED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }

def verify_unchanged_v6_command_plan(module: types.ModuleType) -> dict[str, Any]:
    results: dict[str, dict[str, Any]] = {}
    for family in FAMILIES:
        left_root = "/tmp/" + WORK_PREFIX + family + "-synthetic"
        right_root = "/tmp/rebar-phase2-native-build-v6-" + family + "-synthetic"
        exact: dict[str, Any] = {}
        for phase in ("reference-a", "reference-b"):
            current = planned_commands(left_root, family, phase)
            previous = module.planned_commands(right_root, family, phase)
            require(set(current) == set(previous),
                    "do not add, remove, wrap, or reorder a V6 compiler or readelf role")
            for name in current:
                current_argv = [
                    sanitized(value, left_root, family)
                    for value in current[name]
                ]
                previous_argv = [
                    module.sanitized(value, right_root, family)
                    for value in previous[name]
                ]
                require(current_argv == previous_argv,
                        "reject any speculative alteration of exact V6 compiler flags: "
                        + family + ":" + name)
                require(
                    sanitized(
                        str(command_working_directory(left_root, family, phase, name)),
                        left_root, family,
                    ) == module.sanitized(
                        str(module.command_working_directory(
                            right_root, family, phase, name,
                        )),
                        right_root, family,
                    ),
                    "retain the exact owned V6 package and compiler working directory",
                )
            own_environment = {
                key: sanitized(value, left_root, family)
                for key, value in sorted(
                    build_environment(left_root, family, phase).items()
                )
            }
            prior_environment = {
                key: module.sanitized(value, right_root, family)
                for key, value in sorted(
                    module.build_environment(right_root, family, phase).items()
                )
            }
            require(own_environment == prior_environment,
                    "retain exact offline first-party V6 compiler environments")
            exact[phase] = {
                "command_count": len(current),
                "same_sanitized_compiler_arguments": True,
                "same_sanitized_environment": True,
                "same_sanitized_working_directories": True,
            }
        require(2 * exact["reference-a"]["command_count"]
                == EXPECTED_BUILD_POLICY["v7_future_process_count_by_family"][family],
                "retain the exact complete V6 two-phase compiler process denominator")
        results[family] = exact
    return {
        "family_count": len(results),
        "families": results,
        "compiler_and_linker_flags_changed": 0,
        "additional_compiler_or_inspector_processes": 0,
        "speculative_fortran_repair": False,
        "offline_go_environment_preserved": True,
    }


def verify_context(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    require(sys.executable == PINNED_PYTHON
            and sys.version_info[:3] == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314"
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "use only the exact isolated pinned CPython 3.14.6 read-only oracle")
    contract_path = ROOT / CONTRACT_RELATIVE
    protocol_path = ROOT / PROTOCOL_RELATIVE
    source_path = ROOT / SOURCE_RELATIVE
    kernel = load_frozen_v4()
    contract_owner, contract_raw = kernel.authenticate_file(
        contract_path, expected=None, maximum=MAX_SOURCE_BYTES, capture=True,
    )
    require(contract_raw is not None,
            "read the complete exact canonical V7 raw-forensic machine contract")
    validate_contract(decode_json(contract_raw, canonical_required=True))
    source_owner, _ = kernel.authenticate_file(
        source_path, expected=None, maximum=MAX_SOURCE_BYTES,
    )
    protocol_owner, _ = kernel.authenticate_file(
        protocol_path, expected=None, maximum=MAX_SOURCE_BYTES,
    )
    if arguments is not None and arguments.get("source_sha256") is not None:
        require(source_owner["sha256"] == arguments["source_sha256"]
                and protocol_owner["sha256"] == arguments["protocol_sha256"]
                and contract_owner["sha256"] == arguments["contract_sha256"],
                "independently pin every exact published V7 source-freeze owner")
    inherited = kernel.verify_context()
    require(inherited.get("family_count") == 6
            and inherited.get("source_owner_count") == 25
            and inherited.get("pairwise_shared_source_count") == 0
            and inherited.get("qualified_candidate_count") == 0
            and inherited.get("preserved_v2_history") == expected_v2_summaries(),
            "preserve all six first-party engines and every authentic V2 source build")
    frozen = inherited.get("frozen_correctness")
    require(type(frozen) is dict and frozen.get("status") == "PASS"
            and frozen.get("suite_count") == 13
            and frozen.get("case_execution_count") == 31237
            and frozen.get("candidate_qualified_count") == 0,
            "never alter the frozen 13-suite, 31,237-case original correctness oracle")
    require(len(inherited.get("pinned_toolchains", {}))
            + len(inherited.get("missing_or_changed_toolchains", []))
            == len(EXPECTED_TOOLCHAINS),
            "authenticate all 13 original real pinned toolchain owners")
    independence = verify_six_family_independence()
    graph_relative, graph_digest, graph_size = EXPECTED_SUPPORT[
        "historical_candidate_graph_v10"
    ]
    graph_raw, graph_owner = read_owned(
        graph_relative, graph_digest, maximum=MAX_SOURCE_BYTES,
        exact_size=graph_size, capture=True,
    )
    require(graph_raw is not None,
            "preserve complete authentic C, Rust, and Zig historical candidate evidence")
    identities: set[tuple[int, int]] = set()
    candidate_history = verify_complete_candidate_history(graph_raw, identities)
    history_v4 = verify_historical_v4(kernel, identities)
    v5_kernel = load_frozen_v5()
    history_v5 = verify_historical_v5(v5_kernel, kernel, identities)
    actual_v5_processes = sum(item["process_count"] for item in history_v5)
    v6_kernel = load_frozen_v6()
    flags = verify_unchanged_v6_command_plan(v6_kernel)
    history_v6 = verify_historical_v6(v6_kernel, kernel, identities)
    actual_v6_processes = sum(item["process_count"] for item in history_v6)
    current_graph = verify_committed_v15_graph()
    accounting = expected_evidence_accounting()
    require(len(identities) == accounting["distinct_evidence_file_owner_count"] == 65
            and sum(item["process_count"] for item in expected_v2_summaries()) == 39
            and sum(item["process_count"] for item in history_v4) == 32
            and actual_v5_processes == 31
            and actual_v6_processes == 52
            and accounting["v2_and_v4_actual_compiler_process_count"] == 71
            and accounting["historical_v2_v4_v5_actual_compiler_process_count"] == 102
            and accounting["historical_v2_v3_v4_v5_actual_compiler_process_count"] == 117
            and accounting["all_historical_versions_actual_compiler_process_count"]
            == 86 + actual_v5_processes + actual_v6_processes == 169,
            "authenticate every actual distinct owner and every original process scope")
    inherited_support = inherited.get("pinned_support")
    require(type(inherited_support) is dict,
            "preserve the authentic inherited frozen first-party support closure")
    support: dict[str, Any] = {}
    for key, (relative, digest, size) in EXPECTED_SUPPORT.items():
        if key in inherited_support:
            owner = inherited_support[key]
            require(type(owner) is dict and owner.get("sha256") == digest
                    and owner.get("size_bytes") == size
                    and owner.get("path") == str(ROOT / relative),
                    "the exact inherited V7 first-party frozen source changed")
            support[key] = owner
        elif key == "historical_candidate_graph_v10":
            support[key] = graph_owner
        elif key == "historical_candidate_graph_v15":
            support[key] = current_graph["owner"]
        else:
            raw, owner = read_owned(
                relative, digest, maximum=MAX_SOURCE_BYTES,
                exact_size=size, capture=False,
            )
            require(raw is None,
                    "do not retain unrelated first-party source contents")
            support[key] = owner
    blockers = inherited.get("missing_or_changed_toolchains")
    require(type(blockers) is list,
            "report real pinned-toolchain blockers without substituting a package")
    return {
        "schema": SCHEMA + "-read-only-context",
        "version": 7,
        "status": "BLOCKED" if blockers else "PASS",
        "contract": contract_owner,
        "recorder": source_owner,
        "protocol": protocol_owner,
        "frozen_correctness": frozen,
        "family_count": 6,
        "source_owner_count": 25,
        "pairwise_shared_source_count": 0,
        "families": inherited["families"],
        "package_closures": inherited["package_closures"],
        "six_family_static_independence": independence,
        "official_zig_lock": inherited["official_zig_lock"],
        "pinned_toolchains": inherited["pinned_toolchains"],
        "missing_or_changed_toolchains": blockers,
        "pinned_support": support,
        "preserved_v2_history": expected_v2_summaries(),
        "preserved_candidate_history": candidate_history,
        "preserved_v4_history": history_v4,
        "preserved_v5_history": history_v5,
        "preserved_v6_history": history_v6,
        "committed_truthful_v15_graph": current_graph,
        "unchanged_v6_compiler_plan": flags,
        "raw_elf_forensic_policy": expected_raw_elf_forensic_policy(),
        "evidence_accounting": accounting,
        "go_private_package": expected_go_private_package(),
        **copy.deepcopy(EXPECTED_PHASE_BOUNDARY),
        "read_only": True,
    }


_ACTIVE_KERNEL: types.ModuleType | None = None
_GO_PHASE_PROOFS: dict[tuple[str, str], dict[str, Any]] = {}


def active_kernel() -> types.ModuleType:
    require(_ACTIVE_KERNEL is not None,
            "a pinned explicit V6 build is required before any source snapshot")
    return _ACTIVE_KERNEL


def validate_go_package_proof(value: Any, workdir: str, phase: str) -> dict[str, Any]:
    paths = phase_paths(workdir, "go", phase)
    require(type(value) is dict
            and value.get("directory")
            == sanitized(str(paths["go_module_directory"]), workdir, "go")
            and value.get("directory_mode") == 0o700
            and value.get("package_directory_entries") == ["engine.go", "go.mod"]
            and value.get("external_package_count") == 0
            and value.get("python_header_in_go_package") is False,
            "require an exact mode-0700 phase-private two-file Go package")
    members = value.get("members")
    require(type(members) is dict and set(members) == set(GO_PRIVATE_MEMBERS),
            "the Go compiler package can contain only exact engine.go and go.mod snapshots")
    package_identities: set[tuple[int, int]] = set()
    for name, relative in GO_PRIVATE_MEMBERS.items():
        record = members.get(name)
        expected_digest, expected_bytes = SOURCE_OWNERS["go"][relative]
        package_path = sanitized(str(paths["go_module_directory"] / name),
                                 workdir, "go")
        source_path = sanitized(str(paths["source"] / relative), workdir, "go")
        require(type(record) is dict and record.get("source_relative") == relative
                and record.get("source_sha256") == expected_digest
                and record.get("source_bytes") == expected_bytes
                and record.get("path") == package_path
                and record.get("sha256") == expected_digest
                and record.get("bytes") == expected_bytes
                and record.get("source_snapshot_path") == source_path
                and record.get("fresh_private_copy") is True,
                "the isolated Go package member is not the exact owned source snapshot")
        for field in ("device", "inode", "source_snapshot_device",
                      "source_snapshot_inode"):
            require(type(record.get(field)) is int and record[field] > 0,
                    "require genuine distinct package and source snapshot file identities")
        identity = (record["device"], record["inode"])
        snapshot_identity = (record["source_snapshot_device"],
                             record["source_snapshot_inode"])
        require(identity != snapshot_identity and identity not in package_identities,
                "reject a reused, linked, or cross-file Go engine package snapshot")
        package_identities.add(identity)
    bridge = value.get("bridge")
    relative = "candidates/go/py_bridge.c"
    digest, size = SOURCE_OWNERS["go"][relative]
    require(type(bridge) is dict and bridge.get("source_relative") == relative
            and bridge.get("path")
            == sanitized(str(paths["source"] / relative), workdir, "go")
            and bridge.get("sha256") == digest and bridge.get("bytes") == size
            and not bridge["path"].startswith(value["directory"] + "/")
            and type(bridge.get("device")) is int and bridge["device"] > 0
            and type(bridge.get("inode")) is int and bridge["inode"] > 0
            and (bridge["device"], bridge["inode"]) not in package_identities,
            "the authentic Python bridge must remain outside the private Go engine package")
    return value


def copy_snapshot(workdir: str, family: str, phase: str,
                  sources: dict[str, bytes]) -> dict[str, dict[str, Any]]:
    kernel = active_kernel()
    paths = phase_paths(workdir, family, phase)
    for key in ("base", "source", "native", "temporary"):
        kernel.mkdir_private(paths[key])
    additional = {
        "rust": ("cargo_home", "target"),
        "zig": ("zig_local_cache", "zig_global_cache"),
        "go": ("go_build_cache", "go_module_cache"),
        "fortran": ("fortran_modules",),
    }.get(family, ())
    for key in additional:
        kernel.mkdir_private(paths[key])
    copies: dict[str, dict[str, Any]] = {}
    for relative, raw in sorted(sources.items()):
        destination = paths["source"] / checked_relative(relative)
        kernel.mkdir_private(destination.parent)
        owner = kernel.write_fresh(destination, raw, synchronize=False)
        owner["path"] = sanitized(owner["path"], workdir, family)
        copies[relative] = owner
    if family != "go":
        return copies

    package = paths["go_module_directory"]
    kernel.mkdir_private(package)
    members: dict[str, dict[str, Any]] = {}
    for name, relative in GO_PRIVATE_MEMBERS.items():
        require(relative in sources and relative in copies,
                "copy each exact owned Go module and matching engine independently")
        original = copies[relative]
        fresh = kernel.write_fresh(package / name, sources[relative], synchronize=False)
        members[name] = {
            "source_relative": relative,
            "source_sha256": SOURCE_OWNERS["go"][relative][0],
            "source_bytes": SOURCE_OWNERS["go"][relative][1],
            "path": sanitized(fresh["path"], workdir, family),
            "sha256": fresh["sha256"], "bytes": fresh["bytes"],
            "device": fresh["device"], "inode": fresh["inode"],
            "source_snapshot_path": original["path"],
            "source_snapshot_device": original["device"],
            "source_snapshot_inode": original["inode"],
            "fresh_private_copy": True,
        }
    entries = sorted(os.listdir(str(package)))
    package_stat = os.lstat(str(package))
    bridge_relative = "candidates/go/py_bridge.c"
    bridge = copies[bridge_relative]
    proof = {
        "directory": sanitized(str(package), workdir, family),
        "directory_mode": stat.S_IMODE(package_stat.st_mode),
        "package_directory_entries": entries,
        "members": members,
        "bridge": {
            "source_relative": bridge_relative,
            "path": bridge["path"], "sha256": bridge["sha256"],
            "bytes": bridge["bytes"], "device": bridge["device"],
            "inode": bridge["inode"],
        },
        "external_package_count": 0,
        "python_header_in_go_package": False,
    }
    validate_go_package_proof(proof, workdir, phase)
    require((workdir, phase) not in _GO_PHASE_PROOFS,
            "reject a reused Go package proof or phase")
    _GO_PHASE_PROOFS[(workdir, phase)] = proof
    return copies


def install_v7_build_kernel(kernel: types.ModuleType) -> None:
    require(kernel.__name__ == "_rebar_phase2_exact_frozen_v4_source_kernel"
            and kernel.SOURCE_OWNERS == SOURCE_OWNERS,
            "install V6 paths only in the authenticated private V4 source kernel")
    kernel.WORK_PREFIX = WORK_PREFIX
    kernel.checked_workdir = checked_workdir
    kernel.phase_paths = phase_paths
    kernel.reproducible_prefix_flags = reproducible_prefix_flags
    kernel.build_environment = build_environment
    kernel.planned_commands = planned_commands
    kernel.checked_command = checked_command
    kernel.sanitized = sanitized
    kernel.command_working_directory = command_working_directory
    kernel.copy_snapshot = copy_snapshot


def evidence_names(family: str, label: str, *, failure: bool) -> tuple[str, str]:
    require(type(failure) is bool, "select an explicit successful or failed evidence role")
    base = "native-source-build-v7-" + checked_family(family) + "-" + checked_label(label)
    if failure:
        base += "-failures"
    return base + ".json.gz", base + "-publication-receipt.json"


def check_fresh_evidence(family: str, label: str) -> None:
    kernel = active_kernel()
    directory = ROOT / EVIDENCE_RELATIVE
    try:
        found = os.lstat(str(directory))
        require(stat.S_ISDIR(found.st_mode) and not stat.S_ISLNK(found.st_mode),
                "reject a redirected V6 evidence directory")
    except FileNotFoundError:
        pass
    for failed in (False, True):
        for name in evidence_names(family, label, failure=failed):
            kernel.require_fresh_absent(directory / name)


def verify_go_phase_proofs(workdir: str, phases: list[dict[str, Any]],
                           processes: list[dict[str, Any]]) -> dict[str, Any]:
    require(len(phases) == 2,
            "verify both independently snapshotted private Go package phases")
    proofs: list[dict[str, Any]] = []
    package_identities: set[tuple[int, int]] = set()
    for phase in phases:
        name = phase.get("name")
        require(name in ("reference-a", "reference-b"),
                "require actual independent Go source phase identities")
        proof = validate_go_package_proof(phase.get("private_go_package"), workdir, name)
        for item in proof["members"].values():
            identity = (item["device"], item["inode"])
            require(identity not in package_identities,
                    "the two Go engine package phases share a source inode")
            package_identities.add(identity)
        proofs.append(proof)
    engines = [item for item in processes if item.get("name") == "build_go_engine"]
    bridges = [item for item in processes if item.get("name") == "build_go_bridge"]
    require(len(engines) == len(bridges) == 2 and len(package_identities) == 4,
            "require real separately recorded compiler processes and four Go package owners")
    for phase, engine, bridge in zip(phases, engines, bridges, strict=True):
        name = phase["name"]
        paths = phase_paths(workdir, "go", name)
        require(engine.get("working_directory")
                == sanitized(str(paths["go_module_directory"]), workdir, "go")
                and bridge.get("working_directory")
                == sanitized(str(paths["base"]), workdir, "go")
                and "-include" in bridge.get("argv", [])
                and sanitized(str(paths["artifact_generated_header"]), workdir, "go")
                in bridge["argv"],
                "compile the two-file Go module separately and force its real generated ABI header")
    return {
        "independent_phase_count": 2,
        "package_member_count_per_phase": 2,
        "distinct_package_member_inode_count": 4,
        "foreign_package_member_count": 0,
        "bridge_in_go_package": False,
        "generated_header_forced_include": True,
        "previous_v4_failure_preserved": True,
        "package_proofs": proofs,
    }


_V7_PHASE_RAW_ELF: dict[tuple[str, str, str], bytes] = {}


def record_native_forensics(
    kernel: types.ModuleType,
    workdir: str,
    family: str,
    phase: str,
    completed: dict[str, Any],
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    outputs = completed.get("native_outputs")
    require(type(outputs) is dict,
            "inspect only complete authenticated fresh first-party phase outputs")
    forensic: dict[str, Any] = {}
    paths = phase_paths(workdir, family, phase)
    for role in FAMILIES[family]["artifacts"]:
        if role == "generated_header":
            continue
        expected = outputs.get(role)
        require(type(expected) is dict,
                "record complete raw ELF for every actual native phase artifact")
        path = paths["artifact_" + role]
        before, raw = kernel.authenticate_file(
            path, expected=expected["sha256"], maximum=MAX_BINARY_BYTES,
            exact_size=expected["size_bytes"], capture=True,
        )
        require(type(raw) is bytes
                and len(raw) == before["size_bytes"] == expected["size_bytes"]
                and sha256(raw) == before["sha256"] == expected["sha256"],
                "capture every byte of the exact same authenticated native artifact")
        parsed = parse_owned_elf64(raw)
        require(parsed["file_size"] == before["size_bytes"]
                and parsed["file_sha256"] == before["sha256"],
                "bind pure ELF section forensics to genuine phase-native full bytes")
        phase_key = (workdir, phase, role)
        require(phase_key not in _V7_PHASE_RAW_ELF,
                "never reuse, replace, or silently merge private ELF phase owners")
        _V7_PHASE_RAW_ELF[phase_key] = raw
        streams: dict[str, Any] = {}
        for operation in ("sections", "notes"):
            result = kernel.run_process(
                role + "_" + operation, workdir, family, phase, steps,
            )
            stdout = result["stdout"]
            if operation == "sections":
                require(bool(stdout),
                        "preserve complete original genuine native section listings")
            streams[operation] = {
                "command": role + "_" + operation,
                "stdout_sha256": sha256(stdout),
                "stdout_bytes": len(stdout),
                "process_pid": result["record"]["pid"],
                "section_payload_digests": (
                    "RECORDED FROM COMPLETE AUTHENTICATED FIRST-PARTY ELF BYTES"
                ),
            }
        after, repeated = kernel.authenticate_file(
            path, expected=before["sha256"], maximum=MAX_BINARY_BYTES,
            exact_size=before["size_bytes"], capture=True,
        )
        require(type(repeated) is bytes and repeated == raw
                and (before["device"], before["inode"])
                == (after["device"], after["inode"])
                and after["sha256"] == parsed["file_sha256"],
                "reject swapped, replayed, or altered forensic native ELF bytes")
        forensic[role] = {
            "sections": streams["sections"],
            "notes": streams["notes"],
            "raw_elf64": parsed,
            "same_authenticated_native_inode": True,
            "additional_compiler_or_inspector_processes": 0,
        }
    return forensic


def compare_recorded_phase_forensics(
    workdir: str, family: str, phases: list[dict[str, Any]],
) -> dict[str, Any]:
    checked_workdir(workdir, family)
    require(type(phases) is list and len(phases) == 2
            and [phase.get("name") for phase in phases]
            == ["reference-a", "reference-b"],
            "compare only both complete genuinely independent owned build phases")
    roles = [
        role for role in FAMILIES[family]["artifacts"]
        if role != "generated_header"
    ]
    differences: dict[str, Any] = {}
    for role in roles:
        first_key = (workdir, "reference-a", role)
        second_key = (workdir, "reference-b", role)
        require(first_key in _V7_PHASE_RAW_ELF
                and second_key in _V7_PHASE_RAW_ELF,
                "compare only genuine saved phase-native owner-authenticated bytes")
        first = _V7_PHASE_RAW_ELF[first_key]
        second = _V7_PHASE_RAW_ELF[second_key]
        previous = phases[0]["native_forensics"][role]["raw_elf64"]
        latest = phases[1]["native_forensics"][role]["raw_elf64"]
        require(phases[0]["native_outputs"][role]["sha256"] == sha256(first)
                and phases[1]["native_outputs"][role]["sha256"] == sha256(second)
                and previous["file_sha256"] == sha256(first)
                and latest["file_sha256"] == sha256(second),
                "the actual native artifact was swapped before raw section comparison")
        differences[role] = compare_owned_elf64(
            first, second, previous, latest,
        )
    return {
        "schema": SCHEMA + "-all-phase-raw-elf-differences",
        "family": family,
        "independent_phase_count": 2,
        "native_role_count": len(roles),
        "roles": differences,
        "all_native_artifacts_byte_identical": all(
            item["byte_identical"] for item in differences.values()
        ),
        "additional_compiler_or_inspector_processes": 0,
        "comparison_completed_before_reproducibility_classification": True,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def publish_report(report: dict[str, Any], family: str, label: str) -> dict[str, Any]:
    kernel = active_kernel()
    failed = report.get("status") != "PASS"
    archive_name, receipt_name = evidence_names(family, label, failure=failed)
    directory = ROOT / EVIDENCE_RELATIVE
    kernel.mkdir_private(directory)
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT_BYTES, "bound the complete V6 source-build report")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(archive) <= MAX_ARCHIVE_BYTES,
            "bound the deterministic single-member V6 evidence archive")
    published_archive = kernel.write_fresh(directory / archive_name,
                                           archive, synchronize=True)
    archive_sync = kernel.fsync_directory(directory)
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "status": "PASS",
        "build_status": report["status"],
        "family": family, "label": label,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "contract_sha256": report["contract_sha256"],
        "phase1_manifest_sha256": EXPECTED_SUPPORT["p0_manifest"][1],
        "archive_relative": EVIDENCE_RELATIVE + "/" + archive_name,
        "archive_sha256": published_archive["sha256"],
        "archive_bytes": published_archive["bytes"],
        "uncompressed_sha256": sha256(plain),
        "uncompressed_bytes": len(plain),
        "archive_publication": published_archive,
        "archive_directory_fsync": archive_sync,
        "owned_source_sha256": report["owned_source_sha256"],
        "evidence_accounting": expected_evidence_accounting(),
        "expected_v7_compiler_process_count": report[
            "expected_v7_compiler_process_count"
        ],
        "actual_v7_compiler_process_count": report[
            "actual_v7_compiler_process_count"
        ],
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "subinterpreter_isolation": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
        "receipt_self_publication": "NOT CLAIMED",
    }
    raw_receipt = canonical(receipt)
    require(len(raw_receipt) <= MAX_SOURCE_BYTES,
            "bound the exact V6 durable publication receipt")
    published_receipt = kernel.write_fresh(directory / receipt_name,
                                           raw_receipt, synchronize=True)
    receipt_sync = kernel.fsync_directory(directory)
    return {
        "status": report["status"], "family": family, "label": label,
        "archive_relative": EVIDENCE_RELATIVE + "/" + archive_name,
        "archive_sha256": published_archive["sha256"],
        "receipt_relative": EVIDENCE_RELATIVE + "/" + receipt_name,
        "receipt_sha256": published_receipt["sha256"],
        "receipt_directory_fsync": receipt_sync,
        "failure_preserved": failed,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }


def authenticate_build_context(arguments: dict[str, Any]) -> dict[str, Any]:
    context = verify_context()
    require(context.get("status") == "PASS"
            and not context.get("missing_or_changed_toolchains"),
            "all exact frozen source, evidence, and compiler owners must pass first")
    require(context["recorder"]["sha256"] == arguments["source_sha256"]
            and context["protocol"]["sha256"] == arguments["protocol_sha256"]
            and context["contract"]["sha256"] == arguments["contract_sha256"],
            "independently pin the exact published V6 source, protocol, and contract")
    checked_source_pins(arguments["family"], arguments["owned_source_sha256"])
    return context


def run_build(arguments: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    global _ACTIVE_KERNEL
    family = checked_family(arguments["family"])
    label = checked_label(arguments["label"])
    context = authenticate_build_context(arguments)
    pins = checked_source_pins(family, arguments["owned_source_sha256"])
    kernel = load_frozen_v4()
    install_v7_build_kernel(kernel)
    _ACTIVE_KERNEL = kernel
    try:
        check_fresh_evidence(family, label)
        report: dict[str, Any] = {
            "schema": SCHEMA, "version": 7, "status": "FAIL",
            "family": family, "label": label,
            "source_sha256": arguments["source_sha256"],
            "protocol_sha256": arguments["protocol_sha256"],
            "contract_sha256": arguments["contract_sha256"],
            "owned_source_sha256": pins,
            "frozen_correctness": context["frozen_correctness"],
            "preserved_v2_history": context["preserved_v2_history"],
            "preserved_v4_history": [
                {key: item[key] for key in
                 ("family", "build_status", "receipt_status", "process_count",
                  "failure_preserved", "candidate_qualified_count")}
                for item in context["preserved_v4_history"]
            ],
            "historical_candidate_evidence_owner_count":
                context["preserved_candidate_history"]["owner_count"],
            "evidence_accounting": expected_evidence_accounting(),
            "pinned_toolchains": context["pinned_toolchains"],
            "processes": [], "build_phases": [], "reproducibility": None,
            "expected_v7_compiler_process_count":
                EXPECTED_BUILD_POLICY["v7_future_process_count_by_family"][family],
            "actual_v7_compiler_process_count": 0,
            "go_private_package_reproducibility": None,
            "raw_elf_differences": None,
            "preserved_v6_history": [
                {
                    "family": item["family"],
                    "build_status": item["build_status"],
                    "receipt_status": item["receipt_status"],
                    "process_count": item["process_count"],
                    "failure_preserved": item["failure_preserved"],
                    "candidate_qualified_count": 0,
                }
                for item in context["preserved_v6_history"]
            ],
            "candidate_processes_started": 0,
            "reference_processes_started": 0,
            "candidate_imports": 0,
            "native_libraries_loaded": 0,
            "network_requests": 0,
            "hidden_cases_read": 0,
            "final_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "candidate_correctness": "NOT MEASURED",
            "subinterpreter_isolation": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        sources: dict[str, bytes] = {}
        before: dict[str, dict[str, Any]] = {}
        for relative, digest in pins.items():
            owner, raw = kernel.authenticate_file(
                ROOT / relative, expected=digest, maximum=MAX_SOURCE_BYTES,
                exact_size=SOURCE_OWNERS[family][relative][1], capture=True,
            )
            require(raw is not None, "capture each independently owned source before building")
            before[relative] = owner
            sources[relative] = raw
        report["owned_source_before"] = before
        root = tempfile.mkdtemp(prefix=WORK_PREFIX + family + "-", dir="/tmp")
        checked_workdir(root, family)
        root_stat = os.lstat(root)
        require(stat.S_ISDIR(root_stat.st_mode)
                and stat.S_IMODE(root_stat.st_mode) == 0o700,
                "create only one bounded, newly owned mode-0700 build root")
        report["fresh_private_root"] = sanitized(root, root, family)
        try:
            for phase in ("reference-a", "reference-b"):
                built = kernel.exact_build_phase(
                    root, family, phase, sources, report["processes"],
                )
                built["native_forensics"] = record_native_forensics(
                    kernel, root, family, phase, built, report["processes"],
                )
                if family == "go":
                    proof = _GO_PHASE_PROOFS.get((root, phase))
                    built["private_go_package"] = validate_go_package_proof(
                        proof, root, phase,
                    )
                report["build_phases"].append(built)
                report["actual_v7_compiler_process_count"] = len(report["processes"])
            require(report["actual_v7_compiler_process_count"]
                    == report["expected_v7_compiler_process_count"],
                    "retain every independently frozen V6 compiler and native forensic process")
            report["raw_elf_differences"] = compare_recorded_phase_forensics(
                root, family, report["build_phases"],
            )
            report["reproducibility"] = kernel.verify_reproducible_phases(
                family, report["build_phases"], report["processes"],
            )
            if family == "go":
                report["go_private_package_reproducibility"] = verify_go_phase_proofs(
                    root, report["build_phases"], report["processes"],
                )
            after = authenticate_build_context(arguments)
            require(all(after[key]["sha256"] == context[key]["sha256"]
                        for key in ("contract", "recorder", "protocol")),
                    "the exact published V6 source freeze changed during the build")
            latest: dict[str, dict[str, Any]] = {}
            for relative, digest in pins.items():
                observed, _ = kernel.authenticate_file(
                    ROOT / relative, expected=digest,
                    maximum=MAX_SOURCE_BYTES,
                    exact_size=SOURCE_OWNERS[family][relative][1],
                )
                require((observed["device"], observed["inode"], observed["sha256"])
                        == (before[relative]["device"], before[relative]["inode"],
                            before[relative]["sha256"]),
                        "an independently owned source changed during the two phases")
                latest[relative] = observed
            report["owned_source_after"] = latest
            report["status"] = "PASS"
        except (BuildError, kernel.BuildError, OSError, ValueError,
                UnicodeError, subprocess.SubprocessError) as error:
            report["status"] = "FAIL"
            report["actual_v7_compiler_process_count"] = len(report["processes"])
            report["error"] = {"type": type(error).__name__, "message": str(error)}
        published = publish_report(report, family, label)
        return (0 if report["status"] == "PASS" else 1), published
    finally:
        _GO_PHASE_PROOFS.clear()
        _V7_PHASE_RAW_ELF.clear()
        _ACTIVE_KERNEL = None


class SyntheticSandbox:
    """Block and count every filesystem, process, network, clock, or import effect."""

    def __init__(self) -> None:
        self.original: list[tuple[Any, str, Any]] = []
        self.counts = {
            "actual_file_reads": 0, "actual_file_writes": 0,
            "actual_processes": 0, "actual_threads": 0,
            "actual_clocks": 0, "actual_network": 0,
            "actual_candidate_imports": 0,
            "actual_native_library_loads": 0,
            "actual_holdout_reads": 0,
            "blocked_file_operations": 0,
            "blocked_process_operations": 0,
            "blocked_thread_operations": 0,
            "blocked_clock_operations": 0,
            "blocked_network_operations": 0,
            "blocked_import_operations": 0,
            "blocked_temporary_operations": 0,
            "blocked_native_library_loads": 0,
        }

    def install(self, owner: Any, name: str, replacement: Any) -> None:
        self.original.append((owner, name, getattr(owner, name)))
        setattr(owner, name, replacement)

    def deny(self, key: str, message: str) -> Any:
        def blocked(*arguments: Any, **keywords: Any) -> Any:
            self.counts[key] += 1
            raise SourceOnlyError(message)
        return blocked

    def __enter__(self) -> SyntheticSandbox:
        files = self.deny("blocked_file_operations",
                          "synthetic source controls cannot access the filesystem")
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"), (os, "read"),
            (os, "write"), (os, "stat"), (os, "lstat"), (os, "fstat"),
            (os, "listdir"), (os, "scandir"), (os, "mkdir"),
            (os, "makedirs"), (os, "unlink"), (os, "remove"),
            (os, "replace"), (os, "rename"), (os, "link"), (os, "fsync"),
            (Path, "open"), (Path, "read_bytes"), (Path, "read_text"),
            (Path, "write_bytes"), (Path, "write_text"), (Path, "stat"),
            (Path, "lstat"), (Path, "exists"), (Path, "is_file"),
            (Path, "is_dir"), (Path, "mkdir"), (Path, "iterdir"),
        ):
            if hasattr(owner, name):
                self.install(owner, name, files)
        processes = self.deny("blocked_process_operations",
                              "synthetic controls cannot start a build or subprocess")
        for owner, name in (
            (subprocess, "Popen"), (subprocess, "run"),
            (subprocess, "check_call"), (subprocess, "check_output"),
            (os, "system"), (os, "popen"),
        ):
            if hasattr(owner, name):
                self.install(owner, name, processes)
        for name in ("mkdtemp", "mkstemp", "TemporaryDirectory"):
            if hasattr(tempfile, name):
                self.install(tempfile, name, self.deny(
                    "blocked_temporary_operations",
                    "synthetic controls cannot create a private build directory",
                ))
        self.install(threading.Thread, "start", self.deny(
            "blocked_thread_operations", "synthetic controls cannot start a thread",
        ))
        for name in ("time", "time_ns", "clock_gettime", "clock_gettime_ns",
                     "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time", "thread_time"):
            if hasattr(time, name):
                self.install(time, name, self.deny(
                    "blocked_clock_operations",
                    "synthetic controls cannot sample a clock",
                ))
        self.install(socket, "socket", self.deny(
            "blocked_network_operations", "synthetic controls cannot use a network",
        ))
        self.install(importlib, "import_module", self.deny(
            "blocked_import_operations", "synthetic controls cannot import candidates",
        ))
        self.install(ctypes, "CDLL", self.deny(
            "blocked_native_library_loads",
            "synthetic controls cannot load a native matching engine",
        ))
        return self

    def __exit__(self, kind: Any, value: Any, trace: Any) -> bool:
        for owner, name, original in reversed(self.original):
            setattr(owner, name, original)
        return False


def synthetic_go_proof(workdir: str, phase: str) -> dict[str, Any]:
    paths = phase_paths(workdir, "go", phase)
    phase_offset = 1000 if phase == "reference-a" else 2000
    members: dict[str, dict[str, Any]] = {}
    for index, (name, relative) in enumerate(GO_PRIVATE_MEMBERS.items(), 1):
        digest, size = SOURCE_OWNERS["go"][relative]
        members[name] = {
            "source_relative": relative, "source_sha256": digest,
            "source_bytes": size,
            "path": sanitized(str(paths["go_module_directory"] / name),
                              workdir, "go"),
            "sha256": digest, "bytes": size,
            "device": 1, "inode": phase_offset + index,
            "source_snapshot_path": sanitized(str(paths["source"] / relative),
                                               workdir, "go"),
            "source_snapshot_device": 1,
            "source_snapshot_inode": phase_offset + 100 + index,
            "fresh_private_copy": True,
        }
    bridge_path = "candidates/go/py_bridge.c"
    digest, size = SOURCE_OWNERS["go"][bridge_path]
    return {
        "directory": sanitized(str(paths["go_module_directory"]), workdir, "go"),
        "directory_mode": 0o700,
        "package_directory_entries": ["engine.go", "go.mod"],
        "members": members,
        "bridge": {
            "source_relative": bridge_path,
            "path": sanitized(str(paths["source"] / bridge_path), workdir, "go"),
            "sha256": digest, "bytes": size,
            "device": 1, "inode": phase_offset + 300,
        },
        "external_package_count": 0,
        "python_header_in_go_package": False,
    }


def parse_arguments(arguments: list[str]) -> dict[str, Any]:
    require(type(arguments) is list and all(type(value) is str for value in arguments),
            "supply exactly one bounded frozen V7 build-forensics mode")
    if arguments == ["--self-test"]:
        return {"mode": "self-test"}
    if arguments and arguments[0] == "--verify-context":
        if arguments == ["--verify-context"]:
            return {"mode": "verify-context"}
        result: dict[str, Any] = {"mode": "verify-context"}
        names = {
            "--source-sha256": "source_sha256",
            "--protocol-sha256": "protocol_sha256",
            "--contract-sha256": "contract_sha256",
        }
        require((len(arguments) - 1) % 2 == 0,
                "independently pin every complete V7 read-only source owner")
        for position in range(1, len(arguments), 2):
            option, value = arguments[position:position + 2]
            require(option in names and names[option] not in result,
                    "reject hidden, repeated, build, benchmark, or holdout arguments")
            result[names[option]] = checked_digest(value, names[option])
        require(set(result) == {
            "mode", "source_sha256", "protocol_sha256", "contract_sha256",
        }, "require all three independent exact V7 read-only freeze pins")
        return result
    require(bool(arguments) and arguments[0] == "--build",
            "select source-only self-test, read-only context, or an explicitly pinned build")
    result = {"mode": "build", "owned_source_sha256": []}
    options = {
        "--family": "family", "--label": "label",
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
    }
    position = 1
    while position < len(arguments):
        require(position + 1 < len(arguments),
                "every frozen source-build option requires its exact value")
        option, value = arguments[position], arguments[position + 1]
        if option == "--owned-source-sha256":
            result["owned_source_sha256"].append(value)
        else:
            require(option in options and options[option] not in result,
                    "reject repeated, hidden, abbreviated, timing, or holdout options")
            result[options[option]] = value
        position += 2
    require(set(result) == {"mode", "family", "label", "source_sha256",
                            "protocol_sha256", "contract_sha256",
                            "owned_source_sha256"},
            "pin V7 source, protocol, contract, family, label, and every first-party owner")
    checked_family(result["family"])
    checked_label(result["label"])
    for key in ("source_sha256", "protocol_sha256", "contract_sha256"):
        checked_digest(result[key], key)
    checked_source_pins(result["family"], result["owned_source_sha256"])
    return result


def self_test() -> dict[str, Any]:
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, result: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "give each synthetic positive control one genuine identity")
        require(bool(result), "a frozen V6 synthetic positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, operation: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected,
                "give each hostile synthetic control one genuine identity")
        try:
            operation()
        except (BuildError, OSError, TypeError, ValueError, UnicodeError,
                RecursionError, OverflowError, zlib.error, struct.error):
            rejected.append(name)
            return
        raise BuildError("an unsafe synthetic V6 attack was accepted: " + name)

    with SyntheticSandbox() as guard:
        contract = expected_contract()
        accept("exact-independent-six-family-source-contract",
               validate_contract(contract)["family_count"] == 6)
        accept("exact-twenty-five-pairwise-distinct-semantic-owners",
               contract["source_owner_count"] == 25
               and len({path for entries in SOURCE_OWNERS.values()
                        for path in entries}) == 25)
        accept("exact-thirteen-frozen-toolchain-files",
               len(contract["toolchains"]) == 13)
        accept("unchanged-thirteen-suites-and-31237-reference-executions",
               contract["oracle"] == expected_oracle()
               and contract["oracle"]["suite_count"] == 13
               and contract["oracle"]["case_execution_count"] == 31237)
        accept("no-falsely-qualified-candidate",
               contract["qualified_candidate_count"] == 0)
        accept("actual-51-three-family-candidate-evidence-owners",
               contract["evidence_accounting"]["candidate_history_owner_count"] == 51)
        accept("actual-65-pairwise-distinct-historical-evidence-file-owners",
               contract["evidence_accounting"]["distinct_evidence_file_owner_count"] == 65)
        accept("preserve-71-actual-v2-and-v4-processes-separately-from-owners",
               contract["evidence_accounting"]
               ["v2_and_v4_actual_compiler_process_count"] == 71)
        accept("actual-102-historical-v2-v4-and-v5-processes",
               contract["evidence_accounting"]
               ["historical_v2_v4_v5_actual_compiler_process_count"] == 102)
        accept("actual-169-all-version-processes-including-both-real-v6-builds",
               contract["evidence_accounting"]
               ["all_historical_versions_actual_compiler_process_count"] == 169)
        accept("actual-v5-go-failure-has-five-real-processes",
               HISTORICAL_V5["go"]["process_count"] == 5
               and HISTORICAL_V5["go"]["successful_process_count"] == 4
               and HISTORICAL_V5["go"]["completed_build_phase_count"] == 0)
        accept("actual-v5-go-passing-receipt-preserves-failing-bridge",
               HISTORICAL_V5["go"]["receipt_status"] == "PASS"
               and HISTORICAL_V5["go"]["build_status"] == "FAIL"
               and HISTORICAL_V5["go"]["stderr_bytes"] == 2640)
        accept("actual-v5-fortran-preserves-26-successful-processes",
               HISTORICAL_V5["fortran"]["process_count"] == 26
               and HISTORICAL_V5["fortran"]["successful_process_count"] == 26)
        accept("actual-v5-fortran-preserves-both-completed-failed-phases",
               HISTORICAL_V5["fortran"]["completed_build_phase_count"] == 2
               and HISTORICAL_V5["fortran"]["build_status"] == "FAIL"
               and HISTORICAL_V5["fortran"]["receipt_status"] == "PASS")
        accept("actual-v5-fortran-preserves-distinct-full-engine-bytes",
               HISTORICAL_V5["fortran"]["engine_phase_a_sha256"]
               != HISTORICAL_V5["fortran"]["engine_phase_b_sha256"]
               and HISTORICAL_V5["fortran"]["engine_bytes_per_phase"] == 74624)
        accept("actual-v5-fortran-preserves-real-distinct-gnu-note-streams",
               HISTORICAL_V5["fortran"]["engine_phase_a_notes_sha256"]
               != HISTORICAL_V5["fortran"]["engine_phase_b_notes_sha256"]
               and HISTORICAL_V5["fortran"]["engine_notes_bytes_per_phase"] == 226)
        accept("actual-v5-fortran-does-not-invent-raw-section-causality",
               HISTORICAL_V5["fortran"]["differing_raw_binary_section"]
               == "NOT RECORDED")
        accept("preserve-actual-39-v2-compiler-processes",
               sum(item["process_count"] for item in contract["historical_v2"]) == 39)
        accept("preserve-actual-ten-process-passing-cpp-build",
               HISTORICAL_V4["cpp"]["build_status"] == "PASS"
               and HISTORICAL_V4["cpp"]["process_count"] == 10)
        accept("preserve-actual-four-process-failed-go-build",
               HISTORICAL_V4["go"]["build_status"] == "FAIL"
               and HISTORICAL_V4["go"]["process_count"] == 4)
        accept("go-durable-receipt-pass-is-not-go-build-pass",
               HISTORICAL_V4["go"]["receipt_status"] == "PASS"
               and HISTORICAL_V4["go"]["build_status"] == "FAIL")
        accept("preserve-actual-18-successful-process-fortran-reproducibility-failure",
               HISTORICAL_V4["fortran"]["build_status"] == "FAIL"
               and HISTORICAL_V4["fortran"]["process_count"] == 18
               and HISTORICAL_V4["fortran"]["successful_process_count"] == 18
               and HISTORICAL_V4["fortran"]["completed_build_phase_count"] == 2)
        accept("preserve-real-distinct-equal-size-fortran-engines",
               HISTORICAL_V4["fortran"]["engine_bytes_per_phase"] == 74624
               and HISTORICAL_V4["fortran"]["engine_phase_a_sha256"]
               != HISTORICAL_V4["fortran"]["engine_phase_b_sha256"])
        accept("preserve-real-byte-identical-independent-fortran-bridges",
               HISTORICAL_V4["fortran"]["bridge_bytes_per_phase"] == 37424
               and HISTORICAL_V4["fortran"]["identical_bridge_sha256"]
               == "eba8c1d145a53a2017fc9b7a6e4651b31ec4aef2e67e6c176c6435bffafc7b26")
        accept("do-not-invent-a-differing-fortran-elf-section",
               HISTORICAL_V4["fortran"]["differing_binary_section"] == "NOT RECORDED")
        accept("preserve-exact-real-c-rust-zig-semantic-mismatches",
               contract["evidence_accounting"]
               ["historical_candidate_semantic_mismatch_counts"]
               == {"c": 2094, "rust": 2042, "zig": 1764})
        accept("retain-exact-175-byte-python-header-package-diagnostic",
               len(GO_FAILURE_STDERR) == 175
               and sha256(GO_FAILURE_STDERR)
               == HISTORICAL_V4["go"]["stderr_sha256"])
        accept("source-only-mode-is-separate-from-read-only-context",
               parse_arguments(["--self-test"]) == {"mode": "self-test"}
               and parse_arguments(["--verify-context"]) == {"mode": "verify-context"})
        accept("stable-large-integer-and-lone-surrogate-canonical-json",
               decode_json(canonical({"integer": 18446744073709551615,
                                      "surrogate": "\ud800"}), canonical_required=True)
               == {"integer": 18446744073709551615, "surrogate": "\ud800"})
        accept("deterministic-zero-mtime-single-member-evidence",
               gzip.compress(canonical({"version": 7}), compresslevel=9, mtime=0)
               == gzip.compress(canonical({"version": 7}), compresslevel=9, mtime=0))
        accept("phase-boundary-is-completely-unmeasured",
               contract["phase_boundary"] == EXPECTED_PHASE_BOUNDARY)
        accept("exact-v7-private-root-and-evidence-schema",
               contract["build_policy"]["private_root_prefix"]
               == "/tmp/rebar-phase2-native-build-v7-"
               and contract["schema"] == CONTRACT_SCHEMA)

        for family, entries in SOURCE_OWNERS.items():
            root = "/tmp/" + WORK_PREFIX + family + "-synthetic"
            pins = [path + "=" + digest
                    for path, (digest, _) in entries.items()]
            first = phase_paths(root, family, "reference-a")
            second = phase_paths(root, family, "reference-b")
            commands = planned_commands(root, family, "reference-a")
            accept(family + "-complete-independent-owned-source-pins",
                   set(checked_source_pins(family, pins)) == set(entries))
            accept(family + "-separate-phase-source-directories",
                   first["source"] != second["source"])
            accept(family + "-separate-phase-native-output-directories",
                   first["native"] != second["native"])
            accept(family + "-separate-phase-temporary-directories",
                   first["temporary"] != second["temporary"])
            accept(family + "-separate-phase-build-and-module-caches",
                   first["target"] != second["target"]
                   and first["go_build_cache"] != second["go_build_cache"]
                   and first["go_module_cache"] != second["go_module_cache"]
                   and first["zig_local_cache"] != second["zig_local_cache"]
                   and first["zig_global_cache"] != second["zig_global_cache"])
            accept(family + "-all-direct-pinned-compiler-commands",
                   all(checked_command(name, argv, root, family, "reference-a") == argv
                       for name, argv in commands.items()))
            accept(family + "-complete-native-elf-section-and-note-forensics",
                   all(role + "_sections" in commands
                       and role + "_notes" in commands
                       for role in FAMILIES[family]["artifacts"]
                       if role != "generated_header"))
            accept(family + "-separately-counted-v7-future-processes",
                   2 * len(commands)
                   == EXPECTED_BUILD_POLICY["v7_future_process_count_by_family"][family])
            accept(family + "-correct-nonoverwriting-success-evidence-names",
                   all("native-source-build-v7-" + family + "-synthetic" in name
                       for name in evidence_names(family, "synthetic", failure=False)))
            accept(family + "-correct-nonoverwriting-failure-evidence-names",
                   all("-failures" in name
                       for name in evidence_names(family, "synthetic", failure=True)))

            reject(family + "-reject-omitted-owned-source",
                   lambda family=family, pins=pins:
                   checked_source_pins(family, pins[:-1]))
            reject(family + "-reject-duplicated-owned-source",
                   lambda family=family, pins=pins:
                   checked_source_pins(family, pins[:-1] + [pins[0]]))
            sibling = next(name for name in FAMILIES if name != family)
            foreign_path, (foreign_digest, _) = next(iter(SOURCE_OWNERS[sibling].items()))
            reject(family + "-reject-foreign-candidate-engine-owner",
                   lambda family=family, pins=pins, foreign_path=foreign_path,
                   foreign_digest=foreign_digest:
                   checked_source_pins(family, pins[:-1]
                                       + [foreign_path + "=" + foreign_digest]))
            modified = list(pins)
            modified[0] = modified[0].split("=", 1)[0] + "=" + "0" * 64
            reject(family + "-reject-changed-owned-source-bytes",
                   lambda family=family, modified=modified:
                   checked_source_pins(family, modified))
            for index, unsafe in enumerate((
                "/", "/tmp", "/tmp/foreign",
                "/tmp/rebar-phase2-native-build-v4-" + family + "-old",
                "/tmp/" + WORK_PREFIX + "foreign-x",
                "/tmp/" + WORK_PREFIX + family + "-x/../foreign",
                "/tmp/" + WORK_PREFIX + family + "-x/extra",
            )):
                reject(family + "-reject-private-root-" + str(index),
                       lambda unsafe=unsafe, family=family:
                       checked_workdir(unsafe, family))
            name, argv = next(iter(commands.items()))
            reject(family + "-reject-foreign-compiler",
                   lambda name=name, argv=argv, root=root, family=family:
                   checked_command(name, ["/usr/bin/false", *argv[1:]],
                                   root, family, "reference-a"))
            reject(family + "-reject-extra-compiler-argument",
                   lambda name=name, argv=argv, root=root, family=family:
                   checked_command(name, [*argv, "--foreign"],
                                   root, family, "reference-a"))
            reject(family + "-reject-shell-command-string",
                   lambda name=name, argv=argv, root=root, family=family:
                   checked_command(name, " ".join(argv),
                                   root, family, "reference-a"))
            forensic_role = next(
                role for role in FAMILIES[family]["artifacts"]
                if role != "generated_header"
            )
            for operation in ("sections", "notes"):
                forensic_name = forensic_role + "_" + operation
                forensic_argv = commands[forensic_name]
                reject(family + "-reject-incomplete-elf-forensics-" + operation,
                       lambda forensic_name=forensic_name,
                       forensic_argv=forensic_argv, root=root, family=family:
                       checked_command(
                           forensic_name,
                           [part for part in forensic_argv if part != "--wide"],
                           root, family, "reference-a",
                       ))

        for family, entries in SOURCE_OWNERS.items():
            for path, (digest, size) in entries.items():
                control = family + "-owner-" + path.replace("/", "-")
                accept(control + "-exact-frozen-digest-and-size",
                       checked_digest(digest, path) == digest
                       and type(size) is int and 0 < size <= MAX_SOURCE_BYTES)
                hostile = copy.deepcopy(contract)
                selected = next(item for item in hostile["families"]
                                if item["id"] == family)
                next(item for item in selected["owners"]
                     if item["path"] == path)["sha256"] = "0" * 64
                reject(control + "-reject-substituted-contract-owner",
                       lambda hostile=hostile: validate_contract(hostile))

        for key, (path, digest, size, _, executable) in EXPECTED_TOOLCHAINS.items():
            accept("toolchain-" + key + "-exact-full-file-pin",
                   path.startswith("/") and checked_digest(digest, key) == digest
                   and type(size) is int and size > 0
                   and type(executable) is bool)
            hostile = copy.deepcopy(contract)
            next(item for item in hostile["toolchains"]
                 if item["id"] == key)["sha256"] = "0" * 64
            reject("toolchain-" + key + "-reject-substituted-full-file-pin",
                   lambda hostile=hostile: validate_contract(hostile))

        for key, (path, digest, size) in EXPECTED_SUPPORT.items():
            accept("support-" + key + "-exact-frozen-owner",
                   checked_relative(path) == path
                   and checked_digest(digest, path) == digest
                   and type(size) is int and size > 0)

        go_root = "/tmp/" + WORK_PREFIX + "go-synthetic"
        go_paths = phase_paths(go_root, "go", "reference-a")
        go_commands = planned_commands(go_root, "go", "reference-a")
        go_environment = build_environment(go_root, "go", "reference-a")
        go_proof = synthetic_go_proof(go_root, "reference-a")
        accept("go-private-package-has-only-two-authentic-owned-members",
               validate_go_package_proof(go_proof, go_root, "reference-a")
               ["package_directory_entries"] == ["engine.go", "go.mod"])
        accept("go-engine-process-uses-isolated-package-directory",
               command_working_directory(go_root, "go", "reference-a",
                                         "build_go_engine")
               == go_paths["go_module_directory"]
               and go_paths["go_module_directory"]
               != go_paths["go_original_source_directory"])
        accept("go-python-bridge-stays-outside-compiler-package",
               not go_proof["bridge"]["path"].startswith(go_proof["directory"] + "/"))
        accept("go-engine-snapshots-have-distinct-source-inodes",
               all((item["device"], item["inode"])
                   != (item["source_snapshot_device"],
                       item["source_snapshot_inode"])
                   for item in go_proof["members"].values()))
        accept("go-c-shared-build-produces-actual-owned-compiler-header",
               "-buildmode=c-shared" in go_commands["build_go_engine"]
               and "-include" in go_commands["build_go_bridge"]
               and str(go_paths["artifact_generated_header"])
               in go_commands["build_go_bridge"])
        accept("go-build-remains-fully-offline-and-first-party",
               all(go_environment[key] == "off"
                   for key in ("GOPROXY", "GOSUMDB", "GOWORK", "GOENV"))
               and go_environment["GOTOOLCHAIN"] == "local"
               and go_environment["CC"] == PINNED_GCC)
        accept("go-independent-second-package-phase",
               validate_go_package_proof(
                   synthetic_go_proof(go_root, "reference-b"),
                   go_root, "reference-b",
               )["directory"] != go_proof["directory"])

        for field, value in (
            ("directory_mode", 0o777),
            ("package_directory_entries", ["engine.go", "go.mod", "py_bridge.c"]),
            ("external_package_count", 1),
            ("python_header_in_go_package", True),
            ("directory", "<FRESH_PRIVATE_TMP>/reference-a/source/candidates/go"),
        ):
            hostile = copy.deepcopy(go_proof)
            hostile[field] = value
            reject("go-reject-private-package-" + field,
                   lambda hostile=hostile:
                   validate_go_package_proof(hostile, go_root, "reference-a"))
        for name in GO_PRIVATE_MEMBERS:
            for field, value in (
                ("source_sha256", "0" * 64),
                ("sha256", "0" * 64),
                ("bytes", 1),
                ("fresh_private_copy", False),
                ("path", "<FRESH_PRIVATE_TMP>/reference-a/source/candidates/go/" + name),
                ("source_snapshot_inode", go_proof["members"][name]["inode"]),
            ):
                hostile = copy.deepcopy(go_proof)
                hostile["members"][name][field] = value
                reject("go-reject-private-" + name.replace(".", "-") + "-" + field,
                       lambda hostile=hostile:
                       validate_go_package_proof(hostile, go_root, "reference-a"))
        for field, value in (
            ("path", go_proof["directory"] + "/py_bridge.c"),
            ("sha256", "0" * 64),
            ("source_relative", "candidates/go/engine.go"),
            ("bytes", 1),
        ):
            hostile = copy.deepcopy(go_proof)
            hostile["bridge"][field] = value
            reject("go-reject-package-contaminating-bridge-" + field,
                   lambda hostile=hostile:
                   validate_go_package_proof(hostile, go_root, "reference-a"))
        accept("go-requires-exactly-one-gnu-feature-macro-before-real-header",
               validate_go_bridge_feature_macro(
                   go_commands["build_go_bridge"],
                   str(go_paths["artifact_generated_header"]),
               ) == go_commands["build_go_bridge"]
               and go_commands["build_go_bridge"].index("-D_GNU_SOURCE")
               < go_commands["build_go_bridge"].index("-include"))
        accept("go-preserves-strict-wall-wextra-werror-and-zero-foreign-packages",
               all(flag in go_commands["build_go_bridge"]
                   for flag in ("-Wall", "-Wextra", "-Werror"))
               and contract["go_private_package"]["external_package_count"] == 0)
        go_bridge = go_commands["build_go_bridge"]
        real_header = str(go_paths["artifact_generated_header"])
        reject("go-reject-actual-v5-bridge-with-missing-gnu-feature-macro",
               lambda: checked_command(
                   "build_go_bridge",
                   [part for part in go_bridge if part != "-D_GNU_SOURCE"],
                   go_root, "go", "reference-a",
               ))
        reject("go-reject-duplicate-gnu-feature-macro",
               lambda: checked_command(
                   "build_go_bridge", [*go_bridge, "-D_GNU_SOURCE"],
                   go_root, "go", "reference-a",
               ))
        reject("go-reject-gnu-feature-macro-after-generated-header",
               lambda: checked_command(
                   "build_go_bridge",
                   [part for part in go_bridge if part != "-D_GNU_SOURCE"]
                   + ["-D_GNU_SOURCE"],
                   go_root, "go", "reference-a",
               ))
        reject("go-reject-foreign-value-for-gnu-feature-macro",
               lambda: checked_command(
                   "build_go_bridge",
                   ["-D_GNU_SOURCE=0" if part == "-D_GNU_SOURCE" else part
                    for part in go_bridge],
                   go_root, "go", "reference-a",
               ))
        reject("go-reject-disabled-gnu-feature-macro",
               lambda: checked_command(
                   "build_go_bridge", [*go_bridge, "-U_GNU_SOURCE"],
                   go_root, "go", "reference-a",
               ))
        reject("go-reject-guessed-or-foreign-compiler-generated-header",
               lambda: checked_command(
                   "build_go_bridge",
                   [real_header + ".foreign" if part == real_header else part
                    for part in go_bridge],
                   go_root, "go", "reference-a",
               ))
        reject("go-reject-duplicate-forced-generated-header",
               lambda: checked_command(
                   "build_go_bridge", [*go_bridge, "-include", real_header],
                   go_root, "go", "reference-a",
               ))
        reject("go-reject-weakened-bridge-warning-policy",
               lambda: checked_command(
                   "build_go_bridge",
                   [part for part in go_bridge if part != "-Werror"],
                   go_root, "go", "reference-a",
               ))
        reject("go-reject-hidden-shell-or-compiler-wrapper",
               lambda: checked_command(
                   "build_go_bridge", ["/usr/bin/env", *go_bridge],
                   go_root, "go", "reference-a",
               ))

        omitted = [
            part for part in go_commands["build_go_bridge"]
            if part not in {"-include", str(go_paths["artifact_generated_header"])}
        ]
        reject("go-reject-omitted-real-compiler-generated-header",
               lambda: checked_command("build_go_bridge", omitted, go_root,
                                       "go", "reference-a"))

        zig_root = "/tmp/" + WORK_PREFIX + "zig-synthetic"
        zig_command = planned_commands(zig_root, "zig", "reference-a")["build_zig_engine"]
        accept("zig-preserves-actual-official-native-strip-correction",
               zig_command.count("-fstrip") == 1 and "-fno-strip" not in zig_command)
        reject("zig-reject-omitted-owned-compiler-strip-flag",
               lambda: checked_command(
                   "build_zig_engine", [part for part in zig_command if part != "-fstrip"],
                   zig_root, "zig", "reference-a",
               ))
        reject("zig-reject-duplicated-owned-compiler-strip-flag",
               lambda: checked_command("build_zig_engine", [*zig_command, "-fstrip"],
                                       zig_root, "zig", "reference-a"))

        fortran_root = "/tmp/" + WORK_PREFIX + "fortran-synthetic"
        fortran_commands = planned_commands(fortran_root, "fortran", "reference-a")
        fortran_engine = fortran_commands["build_fortran_engine"]
        accept("fortran-design-freezes-one-phase-independent-random-seed",
               fortran_engine.count("-frandom-seed=rebar-fortran-v5") == 1)
        accept("fortran-design-canonicalizes-both-complete-private-phase-roots",
               all("-ffile-prefix-map=" + str(
                   phase_paths(fortran_root, "fortran", phase)["base"]
               ) + "=/rebar-phase2-v6-owned-phase" in fortran_engine
                   for phase in ("reference-a", "reference-b")))
        accept("fortran-v5-completed-seed-and-phase-map-is-honestly-falsified",
               contract["build_policy"]["fortran_v5_seed_and_root_map_status"]
               == "ACTUALLY FALSIFIED; BOTH COMPLETE ENGINE FILES DIFFER")
        accept("fortran-v6-build-id-hypothesis-was-actually-falsified",
               contract["build_policy"]["fortran_reproducibility_fix_status"]
               == "ACTUALLY FALSIFIED BY V6; RAW PAYLOAD NOT RECORDED"
               and contract["build_policy"]["fortran_build_id_fix_status"]
               == "ACTUALLY FALSIFIED BY V6; RAW PAYLOAD NOT RECORDED")
        accept("fortran-v6-owned-engine-disables-one-observed-v5-build-id",
               fortran_engine.count("-Wl,--build-id=none") == 1
               and "-Wl,--build-id=sha1" not in fortran_engine)
        accept("fortran-v6-identical-owned-bridge-retains-its-recorded-build-id",
               fortran_commands["build_fortran_bridge"].count(
                   "-Wl,--build-id=sha1"
               ) == 1
               and "-Wl,--build-id=none"
               not in fortran_commands["build_fortran_bridge"])
        reject("fortran-reject-missing-evidence-supported-engine-build-id",
               lambda: checked_command(
                   "build_fortran_engine",
                   [part for part in fortran_engine
                    if part != "-Wl,--build-id=none"],
                   fortran_root, "fortran", "reference-a",
               ))
        reject("fortran-reject-original-falsified-engine-build-id",
               lambda: checked_command(
                   "build_fortran_engine",
                   ["-Wl,--build-id=sha1"
                    if part == "-Wl,--build-id=none" else part
                    for part in fortran_engine],
                   fortran_root, "fortran", "reference-a",
               ))
        reject("fortran-reject-duplicated-engine-build-id",
               lambda: checked_command(
                   "build_fortran_engine",
                   [*fortran_engine, "-Wl,--build-id=none"],
                   fortran_root, "fortran", "reference-a",
               ))
        reject("fortran-reject-unrequested-bridge-build-id-change",
               lambda: checked_command(
                   "build_fortran_bridge",
                   ["-Wl,--build-id=none"
                    if part == "-Wl,--build-id=sha1" else part
                    for part in fortran_commands["build_fortran_bridge"]],
                   fortran_root, "fortran", "reference-a",
               ))
        reject("fortran-reject-missing-fixed-compiler-random-seed",
               lambda: checked_command(
                   "build_fortran_engine",
                   [part for part in fortran_engine
                    if part != "-frandom-seed=rebar-fortran-v5"],
                   fortran_root, "fortran", "reference-a",
               ))
        for phase in ("reference-a", "reference-b"):
            path_flag = "-ffile-prefix-map=" + str(
                phase_paths(fortran_root, "fortran", phase)["base"]
            ) + "=/rebar-phase2-v6-owned-phase"
            reject("fortran-reject-missing-complete-root-map-" + phase,
                   lambda path_flag=path_flag: checked_command(
                       "build_fortran_engine",
                       [part for part in fortran_engine if part != path_flag],
                       fortran_root, "fortran", "reference-a",
                   ))

        for field, value in (
            ("schema", "rebar-phase2-owned-native-source-build-v4-source-freeze"),
            ("version", 4),
            ("phase", "BUILD AUTHORIZED"),
            ("family_count", 5),
            ("source_owner_count", 24),
            ("qualified_candidate_count", 1),
        ):
            hostile = copy.deepcopy(contract)
            hostile[field] = value
            reject("reject-substituted-v6-contract-" + field,
                   lambda hostile=hostile: validate_contract(hostile))
        for field, value in (
            ("candidate_history_owner_count", 57),
            ("distinct_evidence_file_owner_count", 55),
            ("v2_actual_compiler_process_count", 40),
            ("v4_cpp_actual_compiler_process_count", 11),
            ("v4_go_failure_actual_compiler_process_count", 0),
            ("v4_fortran_actual_compiler_process_count", 0),
            ("historical_actual_compiler_process_count", 57),
            ("file_owners_are_not_processes", False),
            ("historical_failures_count_as_passes", True),
            ("qualified_candidate_count", 1),
        ):
            hostile = copy.deepcopy(contract)
            hostile["evidence_accounting"][field] = value
            reject("reject-inflated-or-promoted-evidence-" + field,
                   lambda hostile=hostile: validate_contract(hostile))
        for family in ("go", "fortran"):
            for field in ("archive_sha256", "receipt_sha256",
                          "uncompressed_sha256"):
                hostile = copy.deepcopy(contract)
                record = next(item for item in hostile["historical_v5"]
                              if item["family"] == family)
                record[field] = "0" * 64
                reject("reject-changed-actual-v5-" + family + "-" + field,
                       lambda hostile=hostile: validate_contract(hostile))
            for field, value in (
                ("build_status", "PASS"),
                ("receipt_status", "FAIL"),
                ("process_count", 0),
                ("successful_process_count", 0),
                ("completed_build_phase_count", 3),
            ):
                hostile = copy.deepcopy(contract)
                record = next(item for item in hostile["historical_v5"]
                              if item["family"] == family)
                record[field] = value
                reject("reject-promoted-or-invented-actual-v5-"
                       + family + "-" + field,
                       lambda hostile=hostile: validate_contract(hostile))
        for field in ("engine_phase_a_sha256", "engine_phase_b_sha256",
                      "identical_bridge_sha256",
                      "engine_phase_a_notes_sha256",
                      "engine_phase_b_notes_sha256",
                      "identical_engine_sections_sha256"):
            hostile = copy.deepcopy(contract)
            record = next(item for item in hostile["historical_v5"]
                          if item["family"] == "fortran")
            record[field] = "0" * 64
            reject("reject-forged-actual-v5-fortran-" + field,
                   lambda hostile=hostile: validate_contract(hostile))
        forged_cause = copy.deepcopy(contract)
        next(item for item in forged_cause["historical_v5"]
             if item["family"] == "fortran")[
                 "differing_raw_binary_section"
             ] = ".note.gnu.build-id"
        reject("reject-invented-v5-fortran-sole-differing-raw-section",
               lambda: validate_contract(forged_cause))
        for field, value in (
            ("distinct_evidence_file_owner_count", 57),
            ("distinct_evidence_file_owner_count", 59),
            ("historical_v2_v4_v5_actual_compiler_process_count", 71),
            ("historical_v2_v4_v5_actual_compiler_process_count", 76),
            ("all_historical_versions_actual_compiler_process_count", 102),
            ("all_historical_versions_actual_compiler_process_count", 116),
            ("v5_go_failure_actual_compiler_process_count", 26),
            ("v5_fortran_actual_compiler_process_count", 25),
        ):
            hostile = copy.deepcopy(contract)
            hostile["evidence_accounting"][field] = value
            reject("reject-forged-all-version-ledger-"
                   + field + "-" + str(value),
                   lambda hostile=hostile: validate_contract(hostile))
        for family in ("cpp", "go", "fortran"):
            for field in ("archive_sha256", "receipt_sha256", "uncompressed_sha256"):
                hostile = copy.deepcopy(contract)
                record = next(item for item in hostile["historical_v4"]
                              if item["family"] == family)
                record[field] = "0" * 64
                reject("reject-changed-v4-" + family + "-" + field,
                       lambda hostile=hostile: validate_contract(hostile))
        for family in ("c", "rust", "zig"):
            hostile = copy.deepcopy(contract)
            item = next(entry for entry in hostile["historical_v2"]
                        if entry["family"] == family)
            item["process_count"] += 1
            reject("reject-inflated-v2-" + family + "-actual-process-count",
                   lambda hostile=hostile: validate_contract(hostile))
        promoted = copy.deepcopy(contract)
        next(item for item in promoted["historical_v4"]
             if item["family"] == "go")["build_status"] = "PASS"
        reject("reject-promoted-authentic-v4-go-build-failure",
               lambda: validate_contract(promoted))
        promoted_fortran = copy.deepcopy(contract)
        next(item for item in promoted_fortran["historical_v4"]
             if item["family"] == "fortran")["build_status"] = "PASS"
        reject("reject-promoted-authentic-v4-fortran-reproducibility-failure",
               lambda: validate_contract(promoted_fortran))
        false_fortran_compiler = copy.deepcopy(contract)
        next(item for item in false_fortran_compiler["historical_v4"]
             if item["family"] == "fortran")["successful_process_count"] = 17
        reject("reject-false-fortran-compiler-failure",
               lambda: validate_contract(false_fortran_compiler))
        false_fortran_phase = copy.deepcopy(contract)
        next(item for item in false_fortran_phase["historical_v4"]
             if item["family"] == "fortran")["completed_build_phase_count"] = 0
        reject("reject-concealed-completed-fortran-source-phases",
               lambda: validate_contract(false_fortran_phase))
        promoted_zig = copy.deepcopy(contract)
        next(item for item in promoted_zig["historical_v2"]
             if item["family"] == "zig")["build_status"] = "PASS"
        reject("reject-promoted-authentic-v2-zig-build-failure",
               lambda: validate_contract(promoted_zig))
        for field, value in (
            ("hidden_cases_read", 1), ("final_cases_read", 1),
            ("benchmark_files_read", 1), ("clock_samples", 1),
            ("timing_trials_run", 1), ("qualified_candidate_count", 1),
            ("holdout", "OPENED"), ("performance", "1.5x"),
            ("winner_selected", True),
        ):
            hostile = copy.deepcopy(contract)
            hostile["phase_boundary"][field] = value
            reject("reject-broken-source-only-boundary-" + field,
                   lambda hostile=hostile: validate_contract(hostile))

        for index, value in enumerate((
            "../escape", "/absolute", "a//b", "a/./b", "a/../b",
            "a\\b", "a\x00b", "", ".", "..",
        )):
            reject("reject-unsafe-owned-relative-path-" + str(index),
                   lambda value=value: checked_relative(value))
        reject("reject-duplicated-signed-json-fields",
               lambda: decode_json(b'{"owner":1,"owner":2}\n'))
        reject("reject-nonfinite-json-nan",
               lambda: decode_json(b'{"owner":NaN}\n'))
        reject("reject-nonfinite-json-infinity",
               lambda: decode_json(b'{"owner":Infinity}\n'))
        reject("reject-changed-canonical-json",
               lambda: decode_json(b'{ "owner": 1 }\n', canonical_required=True))
        reject("reject-truncated-digest", lambda: checked_digest("0" * 63, "test"))
        reject("reject-uppercase-digest", lambda: checked_digest("A" * 64, "test"))
        reject("reject-unpinned-benchmark-command",
               lambda: parse_arguments(["--verify-context", "--benchmark"]))
        reject("reject-unpinned-incomplete-build",
               lambda: parse_arguments(["--build", "--family", "go"]))
        reject("reject-build-through-read-only-context",
               lambda: parse_arguments(["--verify-context", "--build"]))

        for name, operation in (
            ("file-read", lambda: builtins.open("/forbidden", "rb")),
            ("file-stat", lambda: os.stat("/forbidden")),
            ("package-list", lambda: os.listdir("/forbidden")),
            ("candidate-process", lambda: subprocess.run(["/usr/bin/false"])),
            ("temporary-directory", lambda: tempfile.mkdtemp()),
            ("thread", lambda: threading.Thread().start()),
            ("clock", lambda: time.perf_counter_ns()),
            ("network", lambda: socket.socket()),
            ("candidate-import", lambda: importlib.import_module("candidates.go_candidate")),
            ("native-library", lambda: ctypes.CDLL("/foreign.so")),
        ):
            reject("effect-wall-blocks-" + name, operation)
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "thread_time", "clock_gettime", "clock_gettime_ns"):
            if hasattr(time, name):
                operation = getattr(time, name)
                if name.startswith("clock_gettime"):
                    reject("effect-wall-blocks-all-clocks-" + name,
                           lambda operation=operation:
                           operation(getattr(time, "CLOCK_REALTIME", 0)))
                else:
                    reject("effect-wall-blocks-all-clocks-" + name, operation)
        accept(
            "actual-v6-go-source-build-passes-with-26-genuine-processes",
            HISTORICAL_V6["go"]["build_status"] == "PASS"
            and HISTORICAL_V6["go"]["receipt_status"] == "PASS"
            and HISTORICAL_V6["go"]["process_count"] == 26
            and HISTORICAL_V6["go"]["completed_build_phase_count"] == 2
            and HISTORICAL_V6["go"]["required_engine_export_count"] == 9,
        )
        accept(
            "actual-v6-fortran-build-fails-despite-26-successful-processes",
            HISTORICAL_V6["fortran"]["build_status"] == "FAIL"
            and HISTORICAL_V6["fortran"]["receipt_status"] == "PASS"
            and HISTORICAL_V6["fortran"]["process_count"] == 26
            and HISTORICAL_V6["fortran"]["successful_process_count"] == 26
            and HISTORICAL_V6["fortran"]["completed_build_phase_count"] == 2,
        )
        accept(
            "actual-v6-fortran-both-unnoted-engine-bytes-differ",
            HISTORICAL_V6["fortran"]["engine_phase_a_sha256"]
            != HISTORICAL_V6["fortran"]["engine_phase_b_sha256"]
            and HISTORICAL_V6["fortran"]["engine_phase_notes_bytes"] == 0
            and HISTORICAL_V6["fortran"]["engine_build_id_status"] == "NOT PRESENT",
        )
        accept(
            "actual-v6-raw-fortran-section-is-not-invented",
            HISTORICAL_V6["fortran"]["differing_raw_binary_section"]
            == "NOT RECORDED",
        )
        accept(
            "actual-65-distinct-signed-historical-evidence-owners",
            contract["evidence_accounting"]["distinct_evidence_file_owner_count"] == 65,
        )
        accept(
            "preserve-exact-71-102-117-and-169-real-process-scopes",
            contract["evidence_accounting"]
            ["v2_and_v4_actual_compiler_process_count"] == 71
            and contract["evidence_accounting"]
            ["historical_v2_v4_v5_actual_compiler_process_count"] == 102
            and contract["evidence_accounting"]
            ["historical_v2_v3_v4_v5_actual_compiler_process_count"] == 117
            and contract["evidence_accounting"]
            ["all_historical_versions_actual_compiler_process_count"] == 169,
        )
        accept(
            "raw-elf-forensics-add-no-compiler-process-or-guessed-repair",
            contract["raw_elf_forensics"] == expected_raw_elf_forensic_policy()
            and contract["raw_elf_forensics"]["additional_process_count"] == 0
            and contract["raw_elf_forensics"]["speculative_fortran_compiler_repair"]
            == "FORBIDDEN",
        )
        fixture = synthetic_owned_elf64()
        actual_elf = parse_owned_elf64(fixture)
        accept(
            "pure-bounded-owned-x86-64-little-endian-elf",
            actual_elf["format"] == "ELF64-LITTLE-ENDIAN-X86-64-ET-DYN"
            and actual_elf["file_sha256"] == sha256(fixture)
            and actual_elf["file_size"] == len(fixture),
        )
        accept(
            "raw-elf-records-every-authentic-program-and-section",
            actual_elf["header"]["program_header_count"] == 1
            and actual_elf["header"]["section_count"] == 6
            and len(actual_elf["program_headers"]) == 1
            and len(actual_elf["sections"]) == 6,
        )
        accept(
            "raw-elf-nobits-remains-memory-only",
            actual_elf["sections"][5]["name"] == ".bss"
            and actual_elf["sections"][5]["storage"] == "NOBITS"
            and actual_elf["sections"][5]["file_size"] == 0
            and actual_elf["sections"][5]["payload_sha256"] is None,
        )
        accept(
            "raw-elf-empty-real-file-section-has-authentic-empty-digest",
            actual_elf["sections"][4]["storage"] == "FILE"
            and actual_elf["sections"][4]["file_size"] == 0
            and actual_elf["sections"][4]["payload_sha256"] == sha256(b""),
        )
        accept(
            "raw-elf-accounts-for-metadata-and-every-physical-gap",
            all(name in {row["kind"] for row in actual_elf["file_regions"]}
                for name in ("ELF_HEADER", "PROGRAM_HEADER_TABLE",
                             "SECTION_HEADER_TABLE", "SECTION:1:.shstrtab",
                             "SECTION:2:.text", "SECTION:3:.note.synthetic"))
            and sum(row["end"] - row["start"]
                    for row in actual_elf["file_regions"]) == len(fixture),
        )
        same = compare_owned_elf64(fixture, fixture, actual_elf, actual_elf)
        accept(
            "raw-elf-identical-phases-have-no-invented-differences",
            same["byte_identical"] is True
            and same["total_differing_byte_count"] == 0
            and same["total_difference_span_count"] == 0
            and same["reported_span_count"] == 0
            and same["report_truncated"] is False,
        )
        note_first = synthetic_owned_elf64(note=b"ABCD")
        note_second = synthetic_owned_elf64(note=b"ABXD")
        observed_note = compare_owned_elf64(note_first, note_second)
        accept(
            "raw-elf-detects-the-exact-real-single-section-byte",
            observed_note["byte_identical"] is False
            and observed_note["total_differing_byte_count"] == 1
            and observed_note["total_difference_span_count"] == 1
            and observed_note["sole_differing_raw_section"] == ".note.synthetic",
        )
        many_first = synthetic_owned_elf64(
            note=bytes(index % 251 for index in range(160)),
        )
        many_second = synthetic_owned_elf64(
            note=bytes(
                (index % 251) ^ (1 if index % 2 == 0 else 0)
                for index in range(160)
            ),
        )
        many = compare_owned_elf64(many_first, many_second)
        accept(
            "raw-elf-discloses-all-80-differences-and-16-omitted-ranges",
            many["total_difference_span_count"] == 80
            and many["total_differing_byte_count"] == 80
            and many["reported_span_count"] == 64
            and many["omitted_span_count"] == 16
            and many["report_truncated"] is True
            and len(many["difference_spans"]) == 64
            and many["sole_differing_raw_section"] == "NOT ESTABLISHED",
        )
        accept(
            "raw-elf-complete-range-manifest-is-repeatable",
            many["complete_span_manifest_sha256"]
            == compare_owned_elf64(many_first, many_second)
            ["complete_span_manifest_sha256"],
        )
        trailing = synthetic_owned_elf64(trailing=b"owned-tail")
        detail = parse_owned_elf64(trailing)
        accept(
            "raw-elf-authenticates-unclaimed-trailing-file-bytes",
            any(item["kind"] == "TRAILING_BYTES"
                and item["sha256"] == sha256(b"owned-tail")
                for item in detail["file_regions"]),
        )

        def packed_elf(
            original: bytes, form: str, offset: int, value: Any,
        ) -> bytes:
            result = bytearray(original)
            struct.pack_into(form, result, offset, value)
            return bytes(result)

        table = actual_elf["header"]["section_header_offset"]
        section_width = ELF64_SECTION.size

        duplicate = packed_elf(
            fixture, "<I", table + 3 * section_width, 11,
        )
        parsed_duplicate = parse_owned_elf64(duplicate)
        accept(
            "raw-elf-legal-duplicate-section-names-remain-independently-indexed",
            parsed_duplicate["sections"][2]["name"]
            == parsed_duplicate["sections"][3]["name"] == ".text"
            and parsed_duplicate["sections"][2]["index"]
            != parsed_duplicate["sections"][3]["index"],
        )

        for length in (0, 1, 3, 4, 15, 16, 31, 55, 56, 63):
            reject(
                "raw-elf-reject-truncated-header-" + str(length),
                lambda length=length: parse_owned_elf64(fixture[:length]),
            )
        for offset in (0, 1, 2, 3):
            hostile = bytearray(fixture)
            hostile[offset] ^= 0xFF
            reject(
                "raw-elf-reject-forged-identity-magic-" + str(offset),
                lambda hostile=bytes(hostile): parse_owned_elf64(hostile),
            )
        for label, offset, value in (
            ("class", 4, 1),
            ("data-endianness", 5, 2),
            ("identity-version", 6, 0),
            ("unsupported-operating-system-abi", 7, 255),
            ("abi-version", 8, 1),
            ("reserved-identity", 9, 1),
        ):
            hostile = bytearray(fixture)
            hostile[offset] = value
            reject(
                "raw-elf-reject-" + label,
                lambda hostile=bytes(hostile): parse_owned_elf64(hostile),
            )
        for label, form, offset, value in (
            ("foreign-object-type", "<H", 16, 2),
            ("foreign-machine", "<H", 18, 3),
            ("foreign-elf-version", "<I", 20, 0),
            ("escaped-program-offset", "<Q", 32, len(fixture) + 1),
            ("escaped-section-offset", "<Q", 40, len(fixture) + 1),
            ("short-header-width", "<H", 52, 63),
            ("bad-program-entry-size", "<H", 54, 55),
            ("oversized-program-count", "<H", 56, 4095),
            ("bad-section-entry-size", "<H", 58, 63),
            ("oversized-section-count", "<H", 60, 4095),
            ("missing-section-name-table", "<H", 62, 0),
            ("escaped-section-name-table", "<H", 62, 255),
        ):
            reject(
                "raw-elf-reject-" + label,
                lambda form=form, offset=offset, value=value:
                parse_owned_elf64(packed_elf(fixture, form, offset, value)),
            )
        for label, form, offset, value in (
            ("forged-null-section-name", "<I", table + 0, 1),
            ("forged-null-section-type", "<I", table + 4, 1),
            ("forged-null-section-flags", "<Q", table + 8, 1),
            ("forged-null-section-address", "<Q", table + 16, 1),
            ("forged-null-section-offset", "<Q", table + 24, 1),
            ("forged-normal-extended-count", "<Q", table + 32, 1),
            ("forged-normal-extended-name-index", "<I", table + 40, 1),
            ("forged-normal-extended-program-count", "<I", table + 44, 1),
            ("forged-null-section-alignment", "<Q", table + 48, 2),
            ("forged-null-section-entry-width", "<Q", table + 56, 2),
            ("escaped-name-offset", "<I", table + section_width + 0, 0xFFFFFFFF),
            ("wrong-name-table-kind", "<I", table + section_width + 4, 1),
            ("escaped-name-table-payload", "<Q",
             table + section_width + 24, len(fixture) + 1),
            ("oversized-name-table-payload", "<Q",
             table + section_width + 32, len(fixture)),
            ("cross-linked-name-table", "<I", table + section_width + 40, 65535),
            ("invalid-real-section-alignment", "<Q",
             table + 2 * section_width + 48, 3),
            ("escaped-real-section-payload", "<Q",
             table + 2 * section_width + 24, len(fixture) + 1),
            ("truncated-real-section-payload", "<Q",
             table + 2 * section_width + 32, len(fixture)),
            ("aliased-real-section-bytes", "<Q",
             table + 3 * section_width + 24,
             actual_elf["sections"][2]["file_offset"]),
            ("forged-nobits-file-payload", "<I",
             table + 5 * section_width + 4, SHT_PROGBITS),
            ("invalid-compressed-file-section", "<Q",
             table + 2 * section_width + 8,
             actual_elf["sections"][2]["flags"] | SHF_COMPRESSED),
        ):
            reject(
                "raw-elf-reject-" + label,
                lambda form=form, offset=offset, value=value:
                parse_owned_elf64(packed_elf(fixture, form, offset, value)),
            )
        for length in (
            table,
            table + ELF64_SECTION.size - 1,
            table + 3 * ELF64_SECTION.size - 1,
            len(fixture) - 1,
        ):
            reject(
                "raw-elf-reject-truncated-section-table-" + str(length),
                lambda length=length: parse_owned_elf64(fixture[:length]),
            )
        for number, value in enumerate((
            None, True, False, 1, 1.5, "ELF", bytearray(fixture),
            memoryview(fixture), [], {},
        )):
            reject(
                "raw-elf-reject-non-exact-bytes-"
                + type(value).__name__ + "-" + str(number),
                lambda value=value: parse_owned_elf64(value),
            )
        for value in (None, True, -1, len(fixture) + 1):
            reject(
                "raw-elf-reject-unsafe-physical-offset-" + repr(value),
                lambda value=value:
                checked_elf_span(value, 1, len(fixture), "hostile offset"),
            )
        for value in (None, True, -1, len(fixture) + 1):
            reject(
                "raw-elf-reject-unsafe-physical-size-" + repr(value),
                lambda value=value:
                checked_elf_span(0, value, len(fixture), "hostile size"),
            )
        for family in ("go", "fortran"):
            for field in (
                "archive_sha256", "receipt_sha256", "uncompressed_sha256",
            ):
                hostile = copy.deepcopy(contract)
                record = next(item for item in hostile["historical_v6"]
                              if item["family"] == family)
                record[field] = "0" * 64
                reject(
                    "reject-forged-actual-v6-" + family + "-" + field,
                    lambda hostile=hostile: validate_contract(hostile),
                )
            for field, value in (
                ("receipt_status", "FAIL"),
                ("process_count", 25),
                ("successful_process_count", 25),
                ("completed_build_phase_count", 1),
            ):
                hostile = copy.deepcopy(contract)
                record = next(item for item in hostile["historical_v6"]
                              if item["family"] == family)
                record[field] = value
                reject(
                    "reject-false-v6-" + family + "-" + field,
                    lambda hostile=hostile: validate_contract(hostile),
                )
        counterfeit = copy.deepcopy(contract)
        next(item for item in counterfeit["historical_v6"]
             if item["family"] == "fortran")["build_status"] = "PASS"
        reject("reject-promoted-genuine-v6-fortran-reproducibility-failure",
               lambda: validate_contract(counterfeit))
        concealed = copy.deepcopy(contract)
        next(item for item in concealed["historical_v6"]
             if item["family"] == "go")["build_status"] = "FAIL"
        reject("reject-concealed-genuine-passing-v6-go-source-build",
               lambda: validate_contract(concealed))
        invented = copy.deepcopy(contract)
        next(item for item in invented["historical_v6"]
             if item["family"] == "fortran")[
                 "differing_raw_binary_section"
             ] = ".note.gnu.build-id"
        reject("reject-invented-v6-fortran-raw-section-cause",
               lambda: validate_contract(invented))
        for number in (57, 60, 61, 62, 64, 66, 117, 169):
            if number != 65:
                forged = copy.deepcopy(contract)
                forged["evidence_accounting"][
                    "distinct_evidence_file_owner_count"
                ] = number
                reject(
                    "reject-false-current-distinct-owner-total-" + str(number),
                    lambda forged=forged: validate_contract(forged),
                )
        for field, true_count in (
            ("v2_and_v4_actual_compiler_process_count", 71),
            ("historical_v2_v4_v5_actual_compiler_process_count", 102),
            ("historical_v2_v3_v4_v5_actual_compiler_process_count", 117),
            ("v6_go_success_actual_compiler_process_count", 26),
            ("v6_fortran_failure_actual_compiler_process_count", 26),
            ("all_historical_versions_actual_compiler_process_count", 169),
        ):
            for wrong in (0, true_count - 1, true_count + 1):
                forged = copy.deepcopy(contract)
                forged["evidence_accounting"][field] = wrong
                reject(
                    "reject-false-original-process-scope-"
                    + field + "-" + str(wrong),
                    lambda forged=forged: validate_contract(forged),
                )
        for field, changed in (
            ("additional_process_count", 1),
            ("additional_unpinned_inspection_tool_count", 1),
            ("unchanged_v6_compiler_and_linker_flags", False),
            ("speculative_fortran_compiler_repair", "PERMITTED"),
            ("historical_v6_fortran_raw_section_difference",
             ".note.gnu.build-id"),
            ("record_before_reproducibility_classification", False),
            ("difference_truncation_always_disclosed", False),
            ("sole_cause_requires_complete_file_proof", False),
            ("actual_v7_builds", "PASS"),
            ("candidate_correctness", "PASS"),
            ("performance", "1.5x"),
            ("holdout", "OPENED"),
        ):
            forged = copy.deepcopy(contract)
            forged["raw_elf_forensics"][field] = changed
            reject(
                "reject-forged-raw-elf-policy-" + field,
                lambda forged=forged: validate_contract(forged),
            )
        require(len(accepted) >= 115 and len(rejected) >= 240,
                "run substantial independently named positive and hostile source controls")
        require(all(guard.counts[key] == 0 for key in (
            "actual_file_reads", "actual_file_writes", "actual_processes",
            "actual_threads", "actual_clocks", "actual_network",
            "actual_candidate_imports", "actual_native_library_loads",
            "actual_holdout_reads",
        )), "the synthetic source-only checks produced a real external effect")
        require(all(guard.counts[key] > 0 for key in (
            "blocked_file_operations", "blocked_process_operations",
            "blocked_thread_operations", "blocked_clock_operations",
            "blocked_network_operations", "blocked_import_operations",
            "blocked_temporary_operations", "blocked_native_library_loads",
        )), "exercise every real filesystem, process, and native-effect guard")
        counters = dict(guard.counts)
    return {
        "schema": SCHEMA + "-synthetic-source-only-self-test",
        "version": 7, "status": "PASS", "synthetic": True,
        "positive_control_count": len(accepted), "positive_controls": accepted,
        "rejected_attack_count": len(rejected), "rejected_attacks": rejected,
        "guard_counters": counters,
        "family_count": 6, "source_owner_count": 25,
        "toolchain_owner_count": 13,
        "evidence_accounting": expected_evidence_accounting(),
        "frozen_contract": expected_contract(),
        "raw_elf_forensic_policy": expected_raw_elf_forensic_policy(),
        **copy.deepcopy(EXPECTED_PHASE_BOUNDARY),
    }


def main(arguments: list[str] | None = None) -> int:
    try:
        selected = parse_arguments(list(sys.argv[1:] if arguments is None else arguments))
        if selected["mode"] == "self-test":
            result, exit_code = self_test(), 0
        elif selected["mode"] == "verify-context":
            result = verify_context(selected)
            exit_code = 0 if result["status"] == "PASS" else 1
        else:
            exit_code, result = run_build(selected)
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return exit_code
    except (BuildError, OSError, ValueError, UnicodeError, zlib.error) as error:
        sys.stderr.write(type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
