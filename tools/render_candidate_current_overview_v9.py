#!/usr/bin/env python3
"""Publish an evidence-bound, current-build Python regex comparison.

The synthetic self-test never reads or writes a file, imports a candidate,
starts a process, samples a clock, or opens performance or holdout evidence.
Only an explicit render may create its three fixed, reproducible chart files.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
import gc
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Iterator
import zlib


ROOT = Path("/home/dev-user/src/rebar")
SCHEMA = "rebar-candidate-current-overview-v9"
SOURCE_RELATIVE = "tools/render_candidate_current_overview_v9.py"
INPUT_RELATIVE = "docs/evidence/candidate-current-overview-v9.inputs.json"
SUMMARY_RELATIVE = "docs/evidence/candidate-current-overview-v9.json"
SVG_RELATIVE = "docs/evidence/candidate-current-overview-v9.svg"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_VERSION = "3.14.6"
DENOMINATOR = 31_237
SUITE_IDS = (
    "original_bounded_v5", "public_v3", "scanner_v3", "buffer_v3",
    "managed_v1", "scanner_verbose_v1", "public_types_v1",
    "substitution_v2", "shape_v2", "public_surface_v19",
    "subinterpreter_v2", "pep688_v4", "threaded_pattern_v1",
)
SUITE_COUNTS = (
    151, 864, 1_024, 768, 1_024, 2_854, 6_912, 5_120,
    10_240, 1_376, 128, 264, 512,
)
FAMILY_NAMES = ("python", "rust", "c", "zig", "cpp", "go", "fortran")
DISPLAY_NAMES = {
    "python": "Python re",
    "rust": "Rust",
    "c": "C",
    "zig": "Zig",
    "cpp": "C++",
    "go": "Go",
    "fortran": "Fortran",
}
MAX_SOURCE_BYTES = 8 * 1_048_576
MAX_ARCHIVE_BYTES = 8 * 1_048_576
MAX_DOCUMENT_BYTES = 32 * 1_048_576
MAX_GRAPH_BYTES = 2 * 1_048_576
MAX_SPECIALIST_DOCUMENT_BYTES = 64 * 1_048_576
CORE_PINS: dict[str, tuple[str, str]] = {
    "goal": (
        "GOAL.md",
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    ),
    "phase1_inventory": (
        "oracle/phase1/p0-completeness-v1.json",
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    ),
    "phase1_verifier": (
        "tools/verify_p0_completeness_v1.py",
        "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c",
    ),
    "phase2_protocol": (
        "oracle/phase2/P0-CANDIDATE-PROTOCOL-V3.md",
        "3587e71b91f15c7727749554d971c120ecf5dea2b3624298be19e5dd849adb84",
    ),
    "phase2_inventory": (
        "oracle/phase2/p0-candidate-protocol-v3.json",
        "ebdbc2b9e6ada77a25d6c95d83078fc2af9fde5dd0c2887c5aab09748a67c8bc",
    ),
    "phase2_runner": (
        "tools/run_frozen_p0_candidate_v3.py",
        "478d7d6d119c0f1b248890b1d4e27ffe1714688684b439ecb14bd4a83ecee557",
    ),
    "native_build_protocol": (
        "oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md",
        "f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603",
    ),
    "native_build_runner": (
        "tools/reproduce_phase2_native_builds_v2.py",
        "e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796",
    ),
    "independence_protocol": (
        "oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md",
        "a7ee45f0ea76ee7fedacc564c3122b7f37272d918ef28f1c527c9e8adf351292",
    ),
    "independence_audit": (
        "tools/audit_candidate_independence_v1.py",
        "f18d9b99a3f11fdf20c47d6cb43cb353532c894ababbdaeb7088c14e397ae3b5",
    ),
    "native_build_v3_protocol": (
        "oracle/phase2/NATIVE-SOURCE-BUILDS-V3.md",
        "273e5de944b661ec1f5cfbe3a26bcabc2e9b8c04353891fcfb822b07955eace3",
    ),
    "native_build_v3_runner": (
        "tools/reproduce_phase2_native_builds_v3.py",
        "c33d8e89c4b86f06e7cc06ecef9bca7052af86191d2e09ac89e665500147ba6f",
    ),
    "phase2_v4_protocol": (
        "oracle/phase2/P0-CANDIDATE-PROTOCOL-V4.md",
        "1d7afe5658e8f0f7bb8576fbf1f191a9d8d2d82bde7c97d179b46e1760de2b1f",
    ),
    "phase2_v4_inventory": (
        "oracle/phase2/p0-candidate-protocol-v4.json",
        "e874b253b7baf4ab8cb3f359a44c2d4eacb4251abc3e5703507dceac616690a8",
    ),
    "phase2_v4_runner": (
        "tools/run_frozen_p0_candidate_v4.py",
        "7bb6104423fbd6604decdb46b1c9b1cc0c0782094d04db467710b3b3b2cc208c",
    ),
    "phase2_v2_protocol": ("oracle/phase2/P0-CANDIDATE-PROTOCOL-V2.md", "fc670f502b43ce55f1ef326ea43edeee1fdf28c21726c1bd102468f50c7bbab6"),
    "phase2_v2_inventory": ("oracle/phase2/p0-candidate-protocol-v2.json", "ce3b5c950ef61858af060109e9ac1050bc0851e6324625fed43343086d310c57"),
    "phase2_v5_protocol": ("oracle/phase2/P0-CANDIDATE-PROTOCOL-V5.md", "a943eb9d8d9dbc8ca13562c274b9a96b340ddc531423d6669a00d2aeba65ead8"),
    "phase2_v5_inventory": ("oracle/phase2/p0-candidate-protocol-v5.json", "f0ae8a783a3091cb2f59fdb7f82cb012fe34eceffbead347ff3ee2e11ec1724b"),
    "phase2_v5_runner": ("tools/run_frozen_p0_candidate_v5.py", "5dfdd52069379f4410a9620f95914717e0a9d278fdfc9f1d7416f3aa36ec6326"),
    "phase2_v5_worker": ("tools/run_frozen_p0_candidate_worker_v3.py", "3364ee6d2168803751a2a8c06533828fe9762bb5ad323e8f798bc346a4a2f475"),
    "previous_v6_overview_source": ("tools/render_candidate_current_overview_v6.py", "d7e70cb56809781b11e869a4537ff02ab84ee88a29111a5e7002f2c9d24b16fb"),
    "previous_v6_overview_inputs": ("docs/evidence/candidate-current-overview-v6.inputs.json", "f05a05d55ebd8cad6cc62c15756d1254c680c20a3ed76d4bf3862905e91f0b52"),
    "previous_v6_overview_summary": ("docs/evidence/candidate-current-overview-v6.json", "8bf471c6698542062894b3f162114de066999cca6fc5fad8b8f2c29195f6b1e4"),
    "previous_v6_overview_svg": ("docs/evidence/candidate-current-overview-v6.svg", "bcd2e98ff0ab87b2399f1fe207bec01f495d3a3c4ffceeaf34caf8dde63fe4c1"),
    "previous_v5_overview_source": ("tools/render_candidate_current_overview_v5.py", "23bbf48ed0784c7cc2026d32c63b186ede18ff45eb16c1f96f7973719c22231b"),
    "previous_v5_overview_inputs": ("docs/evidence/candidate-current-overview-v5.inputs.json", "2af61339325a9e7d22c2ea2359ee212bb34adeec5321431ba696d5449a8502a2"),
    "previous_v5_overview_summary": ("docs/evidence/candidate-current-overview-v5.json", "c2e7b033cb5fb237ab10ee0edbed6f0890780f2c3014cdb66255e3ef483c166b"),
    "previous_v5_overview_svg": ("docs/evidence/candidate-current-overview-v5.svg", "cbdbf8123b40fc33a06f265cf5a96e3d152a4fa9a3a3afb865aa56cbfa88d070"),
    "v5_rust_restoration_receipt": ("oracle/phase2/evidence/frozen-p0-candidate-v5-rust-phase2-v5-restoration-receipt.json", "3cd828fbd507d048d0e80715efef754930e89f3c176717ba1dd8985784832889"),
    "previous_v4_overview_source": ("tools/render_candidate_current_overview_v4.py", "dc07a756de1b06e7fcd0bb6a5c82412ec05878f728af36c14bec7a62f184a84d"),
    "previous_v4_overview_inputs": ("docs/evidence/candidate-current-overview-v4.inputs.json", "bf31a5a0972c9c79eeb4756a5101052578bb8cc86e1d66b1fbc230256d3db38b"),
    "previous_v4_overview_summary": ("docs/evidence/candidate-current-overview-v4.json", "02982487dda24ee584c1e01080f3dcd4ee85fb245b651c14f91b35f793122f84"),
    "previous_v4_overview_svg": ("docs/evidence/candidate-current-overview-v4.svg", "593754d14c7f6529c35fc5c3f55f77e18d6a8aa44762bbf787fe533a062183a8"),
    "v5_c_restoration_receipt": ("oracle/phase2/evidence/frozen-p0-candidate-v5-c-phase2-v5-restoration-receipt.json", "2bc016478561ea93c4783773a89789af4534368b9388f2d81baf2aefcdeb9dde"),
    "previous_overview_source": (
        "tools/render_candidate_current_overview_v3.py",
        "a7ce3f6cc11d4f242400a70767b3cb34f9f97ddfdc21d286a1f746073ae00333",
    ),
    "previous_overview_inputs": (
        "docs/evidence/candidate-current-overview-v3.inputs.json",
        "f57f0c355c4de20b7fb4f985b17eabb01bd91f09575d2de27c7b7995f016d411",
    ),
    "previous_overview_summary": (
        "docs/evidence/candidate-current-overview-v3.json",
        "8c0e3f605813d381cdc7cd0e8c7717239fe6b2acdc9ea8732ee473b88a79a238",
    ),
    "previous_overview_svg": (
        "docs/evidence/candidate-current-overview-v3.svg",
        "8238fec6f629c83e0a0c202f31a8520bf1932a3f5dbad91ba6b11116df7f5061",
    ),
    "previous_v7_overview_source": ("tools/render_candidate_current_overview_v7.py", "1f5a5baa82ecb0fd5de53094f1c97ae33c5ac2b71d91c920849c92f5e92217cf"),
    "previous_v7_overview_inputs": ("docs/evidence/candidate-current-overview-v7.inputs.json", "744f86e241e3489cf07c5fccccf291eb68c44a50605d79723dd1ae1092d8511f"),
    "previous_v7_overview_summary": ("docs/evidence/candidate-current-overview-v7.json", "50aafe8c56c21dc95fca2f7ddaead623ef5cf7151db9f28e6c47de7630764f3b"),
    "previous_v7_overview_svg": ("docs/evidence/candidate-current-overview-v7.svg", "8f66eba59478b825bcdea8f8dce393e7376694e7d948c2faef95e847bf75f4d9"),
    "phase2_v6_protocol": ("oracle/phase2/P0-CANDIDATE-PROTOCOL-V6.md", "b1d50f9778257d25e22df7ddba493e6830c514365d25ded518ea832b5e175c39"),
    "phase2_v6_inventory": ("oracle/phase2/p0-candidate-protocol-v6.json", "73cbdf73f94de18496793bafe4ab29c613d694bfde8c47e7ec8430d27a23b521"),
    "phase2_v6_runner": ("tools/run_frozen_p0_candidate_v6.py", "53c5abd71ba46384204f628238dfc4b91a9adf6c75f8edd838e6523300677a9c"),
    "phase2_v6_worker": ("tools/run_frozen_p0_candidate_worker_v4.py", "b0111d76df52ead959863c4459ea1b78f78ab6b1e0d0417624df268860918d8b"),
    "independence_v2_protocol": ("oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md", "80a1de729c067da36648dcfb9751f7bd3833ff561956df9ad82fc6106a19a16b"),
    "independence_v2_inventory": ("oracle/phase2/candidate-independence-v2.json", "89662570a643d94ae1581393ed48015c6fa78d5dbe5ad0419e9a2032e4609659"),
    "independence_v2_runner": ("tools/audit_candidate_independence_v2.py", "57168db3df64414a7dc27f1793d9c22b7c493a8b37c025dc57243796e892d93c"),
    "native_build_v4_protocol": ("oracle/phase2/NATIVE-SOURCE-BUILD-V4.md", "e974b26562cc210c175c08cda7914e6b196fdee2ebe2a8232dd87c0cddbc0dfb"),
    "native_build_v4_inventory": ("oracle/phase2/native-source-build-v4.json", "0b5641529bc49f55b9e56fe397ad38e7e23d6c9b3376587b743753814b8089d7"),
    "native_build_v4_runner": ("tools/reproduce_owned_native_source_build_v4.py", "efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1"),
    "nested_v3_protocol": ("oracle/phase2/candidate-subinterpreters-v3.json", "17dac72e6a0ae75bf1f013656b9779a1e948e71439cf336499c1e680beb19284"),
    "nested_v3_explanation": ("oracle/phase2/CANDIDATE-SUBINTERPRETERS-V3.md", "97354130b4d1ab97ee2c684b43b72e29a0a68439c2a1ead5a4f45edc20e6c9b4"),
    "nested_v3_runner": ("tools/run_owned_candidate_subinterpreters_v3.py", "21febe241549963a2818af2a20782da81bdf952fb7be8affc4289d9ccc9ad5b4"),
    "activation_v2_protocol": ("oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V2.md", "a675b411873c01ae88ea50d4f95aab7231a29dde38a458a947437f07ed850529"),
    "activation_v2_runner": ("tools/activate_verified_native_candidate_v2.py", "e6e8a72feffcf670da9a3e4d2e8b642e933c1d81cfe5bf7d1636385f207d6218"),
    "v6_zig_restoration_receipt": ("oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-restoration-receipt.json", "c415ba80c055d39a933617a839624037b557adbe30c418c2a0e859131fbe9028"),
    "previous_v8_overview_source": ("tools/render_candidate_current_overview_v8.py", "fd487c67608dd63a2ec4a96acc4a9a0b425e54994e3bc7d14b271ae2dd35103c"),
    "previous_v8_overview_inputs": ("docs/evidence/candidate-current-overview-v8.inputs.json", "a7abd22c7d4e79ffe83a963f983de29c42cfb383e54ed6b917a2e6a14aea50c2"),
    "previous_v8_overview_summary": ("docs/evidence/candidate-current-overview-v8.json", "669286612fc618cd97aa44d17f01d539f147b674a3109c83a84e61ceb13c23d4"),
    "previous_v8_overview_svg": ("docs/evidence/candidate-current-overview-v8.svg", "4a2924eeeb5fe6d6fba0d4bea4cb6f9c57ad6fefdd259cdeb8371588dd76b154"),
}
STATIC_OWNERS: dict[str, dict[str, str]] = {
    "rust": {
        "candidates/rust_candidate.py":
            "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
        "candidates/rust/py_bridge.c":
            "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
        "candidates/rust/Cargo.toml":
            "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966",
        "candidates/rust/Cargo.lock":
            "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63",
        "candidates/rust/src/lib.rs":
            "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d",
        "candidates/rust/src/newline.rs":
            "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b",
        "candidates/rust/src/search.rs":
            "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe",
        "candidates/rust/src/stack.rs":
            "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e",
        "candidates/rust/src/unicode_tables.rs":
            "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af",
    },
    "c": {
        "candidates/vm_candidate.py":
            "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
        "candidates/_vm_native.c":
            "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
    },
    "zig": {
        "candidates/zig_candidate.py":
            "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
        "candidates/zig/mini_regex.zig":
            "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
        "candidates/zig/py_bridge.c":
            "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b",
    },
    "cpp": {
        "candidates/cpp_candidate.py":
            "8dcece29b1a194eea023143148af37bb679a9df4c39c01153f5ee23f778e16d5",
        "candidates/cpp/engine.cpp":
            "a9ceb37cfde77447a01a36a8882f7713faf5f201d7a15a193dd17e7b91d118f5",
        "candidates/cpp/engine.hpp":
            "66998fed1839f5e5f7f09382830ed9fda1a62b80bd545305c4eee95ed9a13df9",
        "candidates/cpp/py_bridge.cpp":
            "1d930b63b2f9493dd4759b7521f75d8846daf2580a5699337fcf82540484ab6d",
    },
    "fortran": {
        "candidates/fortran/engine.f90":
            "5180da085487b9932e3f769e6baded6a8409a0b778890e6197aaea6dad1923a5",
        "candidates/fortran/py_bridge.c":
            "8540b708de4819f1b3340c32e78eaf083c1cad35f016c0f7af33a27773694b0d",
        "candidates/fortran_candidate.py":
            "8db564771d38c0896a5207f1241a44463432dc5bf75dfcf657740d8bcfefd194",
    },
}
GO_ENGINE_SHA = "6472c4413921f3a877455315400c532e7632a871a96d46de9583fa6170a43192"
GO_ADAPTER_SHA = "816d21527b9806afbc9457122f72f8f6b62c39b8b791d3f363745d412cbe3d20"
GO_MODULE_SHA = "9297c4e8fe4649196150400d23a4da584d7ef721347f7095399a7382edad669b"
GO_BRIDGE_SHA = "52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a"
CPP_V4_SOURCE_BUILD: dict[str, Any] = {
    "archive": (
        "oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4.json.gz",
        "48910a6328e8aaacdac993b2c029995d878960a456359a14db5c83b9fc518df9",
    ),
    "receipt": (
        "oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4-publication-receipt.json",
        "7742eda3ce777b1378d0c7fb87fc064f222850ca8bcf15cd23ff8a4d87d8bebf",
    ),
    "archive_bytes": 20_605,
    "uncompressed_bytes": 175_104,
    "uncompressed_sha256":
        "b0141e8d17dc5cafddd7e5a7901e1e2babb4822f0fff7cc7e1201ab625276243",
    "bridge_sha256":
        "d444611316caceb4ba08783203bc4f1d396a8987f63a49bd24c81d5d2c532441",
    "bridge_size_bytes": 130_744,
    "fresh_phase_count": 2,
    "process_count": 10,
    "source_owner_count": 4,
}
CPP_V4_PROCESS_NAMES = (
    "readelf_version", "gxx_version", "build_cpp_bridge",
    "bridge_dynamic", "bridge_symbols",
)
CPP_V4_RECEIPT_FIELDS = frozenset({
    "archive_bytes", "archive_directory_fsync", "archive_publication",
    "archive_relative", "archive_sha256", "benchmark_files_read",
    "build_status", "candidate_correctness", "candidate_imports",
    "candidate_processes_started", "clock_samples", "contract_sha256",
    "family", "hidden_cases_read", "holdout", "label", "memory",
    "native_libraries_loaded", "owned_source_sha256", "performance",
    "phase1_manifest_sha256", "protocol_sha256", "receipt_self_publication",
    "schema", "source_sha256", "status", "subinterpreter_isolation",
    "timing_trials_run", "uncompressed_bytes", "uncompressed_sha256",
    "undefined_behavior", "winner_selected",
})

ZIG_V6_OUTER: dict[str, Any] = {
    "archive": ("oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-failures.json.gz", "2ca2a253e4148c4232327cf89f1306c1c4e83639714f3b036ebdd7bd0225aaa3"),
    "receipt": ("oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-failures-publication-receipt.json", "72c2635850273543eded2e9f541cb64529f2ce22a9d6fe5b14c30705fa474c95"),
    "archive_bytes": 850_155, "uncompressed_bytes": 24_903_358,
    "uncompressed_sha256": "2afa993835d45f30838971b5c68c397e9d6271877e77f32919aee955554ce9f6",
}
ZIG_V6_WORKER: dict[str, Any] = {
    "archive": ("oracle/phase2/evidence/frozen-p0-candidate-worker-v4-zig-phase2-v6-failures.json.gz", "07a1be40b4aba273bdec1f5d567aad0c6fbbf860189ade527eb90cfed1aab594"),
    "receipt": ("oracle/phase2/evidence/frozen-p0-candidate-worker-v4-zig-phase2-v6-failures-publication-receipt.json", "8c5f69411600781dca1efd3965b98fcecf9a1fec00afb4e5f7d319c2afa86cf4"),
    "archive_bytes": 848_777, "uncompressed_bytes": 24_899_336,
    "uncompressed_sha256": "472f832152aab4550a635891b24415971171f8101e1171c010dc56cfc62751a0",
}
ZIG_V6_NESTED: dict[str, Any] = {
    "archive": ("oracle/phase2/evidence/owned-candidate-subinterpreters-v3-zig-phase2-v6-subinterpreters-failures.json.gz", "ded1049f0d1979b6a71c80fcd86fe411e400603b02bbe28ed8b3634f513612f4"),
    "receipt": ("oracle/phase2/evidence/owned-candidate-subinterpreters-v3-zig-phase2-v6-subinterpreters-failures-publication-receipt.json", "8fc8e0753458e69751fd45b820764e7c085ec6111c9dcda64ee90ef227b0ce21"),
    "uncompressed_bytes": 1_581_106,
    "uncompressed_sha256": "a5280c4713fdc2e494f8e2bd0b1eeab9f6199dceede5d410bc1f8108e286cf67",
    "worker_stdout_bytes": 1_126_801,
    "worker_stdout_sha256": "2da4af1e62facbe6565bb127a0920f647ec04c3f0005d02f58b233229277721d",
}
ZIG_V6_SPECIALISTS: tuple[dict[str, Any], ...] = (
    {"name": "managed", "suite": "managed_v1", "label": "phase2-v6-managed", "status": "PASS", "case_count": 1_024, "mismatch_count": 0,
     "archive": ("experiments/rust_public_practice_v1/zig-managed-buffer-lifetime-v1-phase2-v6-managed.json.gz", "43a8cf60484c46e85ba7b5853f38ee4c250f4383186dc33eb08162b30d0c897a"),
     "receipt": ("experiments/rust_public_practice_v1/zig-managed-buffer-lifetime-v1-phase2-v6-managed-publication-receipt.json", "d28c95236df9b19e5ab27a1174d5b8616cf2ba22394314ee2dcb78c13034d516"),
     "uncompressed_bytes": 28_749_630, "uncompressed_sha256": "2775345026c41bec844e79b7cef81a14322acfbf99908c671dd116d4328a31a8"},
    {"name": "verbose", "suite": "scanner_verbose_v1", "label": "phase2-v6-verbose", "status": "FAIL", "case_count": 2_854, "mismatch_count": 620,
     "archive": ("experiments/rust_public_practice_v1/zig-scanner-verbose-comments-v1-phase2-v6-verbose.json.gz", "ec5b4e20e05bdd068d065cf9ace9d4d988220565b29db0be91c15b1fa5a0403f"),
     "receipt": ("experiments/rust_public_practice_v1/zig-scanner-verbose-comments-v1-phase2-v6-verbose-publication-receipt.json", "3e8d850af3ad191c24b92182ed4e694c44c23716b37c607a31c50c45659428d9"),
     "uncompressed_bytes": 18_349_044, "uncompressed_sha256": "77d182f38a473a83851d90a1e9e307d4bbf5440e9ae6392964c1273737f2e125"},
    {"name": "types", "suite": "public_types_v1", "label": "phase2-v6-types", "status": "FAIL", "case_count": 6_912, "mismatch_count": 248,
     "archive": ("experiments/rust_public_practice_v1/zig-public-type-identity-serialization-v1-phase2-v6-types.json.gz", "482dc8ba52e091e909a4d4acf6d57f964fc2e6fe8a729a105e8aca2b9448c2c6"),
     "receipt": ("experiments/rust_public_practice_v1/zig-public-type-identity-serialization-v1-phase2-v6-types-publication-receipt.json", "82f96615d0894b99ed1316df6fde2c713e3d7d4b19f18cf71a7e97e82a2352df"),
     "uncompressed_bytes": 21_083_712, "uncompressed_sha256": "b81ba63e006500d1dafbd9f6af4569bb1badfbb72f955721af21b44f0c257abb"},
    {"name": "substitution", "suite": "substitution_v2", "label": "phase2-v6-substitution", "status": "FAIL", "case_count": 5_120, "mismatch_count": 64,
     "archive": ("experiments/rust_public_practice_v1/zig-substitution-buffer-semantics-v2-phase2-v6-substitution.json.gz", "d83cdc6bb1b5bb878e55e5fea866eaec6c07e9dd78f983858cecc15463ac6de2"),
     "receipt": ("experiments/rust_public_practice_v1/zig-substitution-buffer-semantics-v2-phase2-v6-substitution-publication-receipt.json", "9b4c4daaf775bb585a3dcfbe693b91c14d49eb09aafd79360fb41ed5cd083791"),
     "uncompressed_bytes": 18_714_016, "uncompressed_sha256": "a1287f41db8163e2535cb74576ba38e6b9f55506b9bfc6aa2aa6661d8de6bac1"},
    {"name": "shape", "suite": "shape_v2", "label": "phase2-v6-shape", "status": "FAIL", "case_count": 10_240, "mismatch_count": 672,
     "archive": ("experiments/rust_public_practice_v1/zig-shape-changing-buffer-semantics-v2-phase2-v6-shape.json.gz", "b4766c3c3547ea347421bf4784ac11eb2b63e6065135002139fdb17ca69bc7c8"),
     "receipt": ("experiments/rust_public_practice_v1/zig-shape-changing-buffer-semantics-v2-phase2-v6-shape-publication-receipt.json", "e020e83774064cb9c9c9f9a70229ad3bcd04b0e417942317be4fbdb33f365ba9"),
     "uncompressed_bytes": 43_172_825, "uncompressed_sha256": "4ec39946d0519b21c01285887a91a7e21e3df4b6281c950954ccf2876ccb5b05"},
)
ZIG_V6_EXPECTED_MISMATCHES: dict[str, int] = {
    "scanner_v3": 64, "scanner_verbose_v1": 620, "public_types_v1": 248,
    "substitution_v2": 64, "shape_v2": 672, "public_surface_v19": 96,
}
ZIG_V6_FAILED_SUITES = (
    "scanner_v3", "scanner_verbose_v1", "public_types_v1", "substitution_v2",
    "shape_v2", "public_surface_v19", "subinterpreter_v2",
)
ZIG_V6_PASSING_CASES = 3_583

C_GATE_FAILURE: dict[str, Any] = {
    "receipt": (
        "oracle/phase2/evidence/"
        "frozen-p0-candidate-v3-c-phase2-v3-failures-publication-receipt.json",
        "02996c09c8662c75eadadeccef2ac77895d942a56e06aca323e880f951a330a1",
    ),
    "archive": (
        "oracle/phase2/evidence/"
        "frozen-p0-candidate-v3-c-phase2-v3-failures.json.gz",
        "3f7718b09080d0aa9612dabc7f97e8f41ea35958c8bbfeb7febbbf678d06028d",
    ),
    "archive_bytes": 1_096,
    "uncompressed_bytes": 2_539,
    "uncompressed_sha256":
        "5eb32867d926d709b216b1a153f7d2ad11bc9bbfe2261d90f0d4f4073757dc71",
    "failed_stage": "authenticate all actual canonical promotion intentions",
    "failure_message": "a mode-0600 pre-replace promotion intention was lost",
}

C_GATE_V4_FAILURE: dict[str, Any] = {
    "receipt": (
        "oracle/phase2/evidence/"
        "frozen-p0-candidate-v4-c-phase2-v4-failures-publication-receipt.json",
        "4ba965cca31ae3644ba37b4d8bb52f093d27349dd2aa1b747b8d2918fd60e23b",
    ),
    "archive": (
        "oracle/phase2/evidence/"
        "frozen-p0-candidate-v4-c-phase2-v4-failures.json.gz",
        "08614ef777081edb2335bcdaed615104c1d8a957ce246261b05d275d8bc6f50c",
    ),
    "archive_bytes": 7_186,
    "uncompressed_bytes": 42_231,
    "uncompressed_sha256":
        "fe8b9d59be3ca7ed08b365fa0e0994c13a058b7ace0c5b36f1aab1196d8e6ba2",
    "failed_stage": "run every unchanged frozen V2 correctness case",
    "failure_message": "retain and reject a failed actual isolated native correctness worker",
}
RUST_GATE_V5_OUTER: dict[str, Any] = {
    "receipt": ("oracle/phase2/evidence/frozen-p0-candidate-v5-rust-phase2-v5-failures-publication-receipt.json", "72070ab4f68200c305d317a59c7ff6405888d23fadaaf04835aba68d33a6c6ec"),
    "archive": ("oracle/phase2/evidence/frozen-p0-candidate-v5-rust-phase2-v5-failures.json.gz", "bf0915a4dab62ebaea67b92258eafbc01f52b436b70f81bf7e0ca42211f95bff"),
    "archive_bytes": 9_623, "uncompressed_bytes": 65_496,
    "uncompressed_sha256": "bc81b478553bd7a029d08ee0df80562e9180f8732648ae876f66801390e149be",
    "failed_stage": "run every unchanged original correctness case with corrected worker",
    "failure_message": "retain and reject a failed actual isolated native correctness worker",
}
RUST_GATE_V5_INNER: dict[str, Any] = {
    "receipt": ("oracle/phase2/evidence/frozen-p0-candidate-worker-v3-rust-phase2-v5-failures-publication-receipt.json", "f6fe003c100a93e06239a072380c4f3839dc9863391b939ebfc6d667b174f0d9"),
    "archive": ("oracle/phase2/evidence/frozen-p0-candidate-worker-v3-rust-phase2-v5-failures.json.gz", "a2106050b59130a9eb7f083d13c2e42e22dcf9a33f5a7b35b634ff9dd9b2f9ae"),
    "archive_bytes": 716_812, "uncompressed_bytes": 16_834_434,
    "uncompressed_sha256": "03d9eff7cd70087f3e5c78108a96f4c3043e8d0095c62be881d4d88eea56dd1d",
}
FAILED_RUST_V5_SUITES = ("public_types_v1", "substitution_v2", "shape_v2", "public_surface_v19", "subinterpreter_v2")
RUST_V5_VERIFIED_PASSING_CASES = 7_461
RUST_V5_SUBORDINATE_PINS: tuple[tuple[str, str], ...] = (
 ("experiments/rust_public_practice_v1/rust-managed-buffer-lifetime-v1-phase2-v5-managed.json.gz", "74a5ede2b9c75b9ad9a1d7ecc2802786793197c8a1f399046d5d6d1997b781ca"),
 ("experiments/rust_public_practice_v1/rust-managed-buffer-lifetime-v1-phase2-v5-managed-publication-receipt.json", "f63816d95048ed26bf1572d87676d91364761369fdfb5c49f65d1bcf3ef3ccf7"),
 ("experiments/rust_public_practice_v1/rust-scanner-verbose-comments-v1-phase2-v5-verbose.json.gz", "8f1b6df4044970fed48eecdf2b6bcd9434dcee1956abf8a3308fec80fad6d44a"),
 ("experiments/rust_public_practice_v1/rust-scanner-verbose-comments-v1-phase2-v5-verbose-publication-receipt.json", "929f4899b211d795c8a5e570148ca19c984d2dbeb78fda18ba89701ddee1e241"),
 ("experiments/rust_public_practice_v1/rust-public-type-identity-serialization-v1-phase2-v5-types.json.gz", "f5819a54871a88edf3c6e1b302d67809e5c74cc1912e9bba91a57b6f2e237772"),
 ("experiments/rust_public_practice_v1/rust-public-type-identity-serialization-v1-phase2-v5-types-publication-receipt.json", "ab6b37f02ef81945bef6a3f38dcaa9a7c4594a0cd6d851ecf9df89aa2507646a"),
 ("experiments/rust_public_practice_v1/rust-shape-changing-buffer-semantics-v2-phase2-v5-shape.json.gz", "ee69217102b87f5c5a288c2fa58b44a1e881f46191f21520e6510313cf346b00"),
 ("experiments/rust_public_practice_v1/rust-shape-changing-buffer-semantics-v2-phase2-v5-shape-publication-receipt.json", "339a1744bffc467495daa4992622d3cfca0219bc4e7433cb21910b46c04b467c"),
 ("experiments/rust_public_practice_v1/rust-substitution-buffer-semantics-v2-phase2-v5-substitution.json.gz", "49c9bf367ddef35d1970b07c483d4468da9e09348522a26780bf0495391673fa"),
 ("experiments/rust_public_practice_v1/rust-substitution-buffer-semantics-v2-phase2-v5-substitution-publication-receipt.json", "4905f6cd20f44453b16f0598e5e77ffa99340107a229987c1728b9635a9e7e60"),
 ("oracle/phase2/evidence/owned-candidate-subinterpreters-v1-rust-phase2-v5-subinterpreters-failures.json.gz", "b73ea6fd2f944a46bbc89a593df251a054f62bed288b60765eb3c9dc3a9619cd"),
 ("oracle/phase2/evidence/owned-candidate-subinterpreters-v1-rust-phase2-v5-subinterpreters-failures-publication-receipt.json", "99b32d784182800b92b3fcb555add6c8d27d599a91dc5255b46ca597667c6049"),
)

C_GATE_V5_OUTER: dict[str, Any] = {
    "receipt": ("oracle/phase2/evidence/frozen-p0-candidate-v5-c-phase2-v5-failures-publication-receipt.json", "10b1bb903ae3e6cf6b0b732e0518bfadce8f17a0021c36ba86bef1e641da07a1"),
    "archive": ("oracle/phase2/evidence/frozen-p0-candidate-v5-c-phase2-v5-failures.json.gz", "f8c4465be0d982445f79ec66744c710b20c64bd308eaff8a12ba571b5bb0ef91"),
    "archive_bytes": 7_304, "uncompressed_bytes": 42_404,
    "uncompressed_sha256": "caa91a82e31e2d945765c745e69d2e9b1d02ab5e41e63e4bd8d71419ef478ff6",
    "failed_stage": "run every unchanged original correctness case with corrected worker",
    "failure_message": "retain and reject a failed actual isolated native correctness worker",
}
C_GATE_V5_INNER: dict[str, Any] = {
    "receipt": ("oracle/phase2/evidence/frozen-p0-candidate-worker-v3-c-phase2-v5-failures-publication-receipt.json", "fc68840c6bbf0e9bc1510894b575d0111246401eba70e8706e2a33542365fc55"),
    "archive": ("oracle/phase2/evidence/frozen-p0-candidate-worker-v3-c-phase2-v5-failures.json.gz", "149bc01c571c15034896d26eb05708985a7a3a49e361e26199682860f8c83e13"),
    "archive_bytes": 707_346, "uncompressed_bytes": 16_598_602,
    "uncompressed_sha256": "f21559e3525c66c719a9e50150a314d7e5d0ce74f406cc281b265ae28644f359",
}
FAILED_C_V5_SUITES = ("public_types_v1", "substitution_v2", "shape_v2", "public_surface_v19", "subinterpreter_v2", "pep688_v4")
C_V5_VERIFIED_PASSING_CASES = 7_197
C_V5_SUBORDINATE_PINS: tuple[tuple[str, str], ...] = (
 ("experiments/rust_public_practice_v1/c-managed-buffer-lifetime-v1-phase2-v5-managed.json.gz", "687ba3fbaa15ac56977f78c50027041a67b8db8cf0570af1e2afd99c7e789328"),
 ("experiments/rust_public_practice_v1/c-managed-buffer-lifetime-v1-phase2-v5-managed-publication-receipt.json", "42ce0458d9ac184a92697788f67f0658cacab96639324aa1ef76c6bc68b41d09"),
 ("experiments/rust_public_practice_v1/c-scanner-verbose-comments-v1-phase2-v5-verbose.json.gz", "13a354c15343cb50449ebe4c2900a94f9ad1b0a937ae4f84690edc577f5a7a9a"),
 ("experiments/rust_public_practice_v1/c-scanner-verbose-comments-v1-phase2-v5-verbose-publication-receipt.json", "7be61fe54d99949627ec85a64e323de7afaac3fc684de1a53377d5973722cce4"),
 ("experiments/rust_public_practice_v1/c-public-type-identity-serialization-v1-phase2-v5-types.json.gz", "4d17b3443e543d83a160e5c7d5fd32542415cf41e424369106a9be8e58434e4a"),
 ("experiments/rust_public_practice_v1/c-public-type-identity-serialization-v1-phase2-v5-types-publication-receipt.json", "2c046b2107b3eb7485eb12765b7858f925662fb0e6e37023c37cdf1481a27551"),
 ("experiments/rust_public_practice_v1/c-substitution-buffer-semantics-v2-phase2-v5-substitution.json.gz", "07c66a0d0e2d08b4886241741087a8c40d5898a6824e90d50dc9c2aba271fc1b"),
 ("experiments/rust_public_practice_v1/c-substitution-buffer-semantics-v2-phase2-v5-substitution-publication-receipt.json", "ed9797fe2e7b66302383af944efce4b53a83f24a864cd4a222effc98ff47cb35"),
 ("experiments/rust_public_practice_v1/c-shape-changing-buffer-semantics-v2-phase2-v5-shape.json.gz", "9e43e7613e9f41ee646da7922baeb943a11df0b4175bb4d52a8ecd62429362da"),
 ("experiments/rust_public_practice_v1/c-shape-changing-buffer-semantics-v2-phase2-v5-shape-publication-receipt.json", "7dbc8a952fcc71537b0074fae9375850a1b4cb455c029dc2ad992fc13fd1457e"),
 ("oracle/phase2/evidence/owned-candidate-subinterpreters-v1-c-phase2-v5-subinterpreters-failures.json.gz", "e375edafd74a0b77e349178b59d2d38d2cf423272b9b91dfb4baad91ad94c0f6"),
 ("oracle/phase2/evidence/owned-candidate-subinterpreters-v1-c-phase2-v5-subinterpreters-failures-publication-receipt.json", "3e05efd1a83cd650ab3d91cebf0380df0f0cacd5758e6c92f91e08f8acd26a62"),
)

ZIG_V3_SUCCESS: dict[str, Any] = {
    "receipt": (
        "oracle/phase2/evidence/"
        "native-source-build-v3-zig-phase2-v3-publication-receipt.json",
        "050f0156647c90ed03ebffe7d530e0a9f56d605f3728df618c85dc2f8ae570e8",
    ),
    "archive": (
        "oracle/phase2/evidence/native-source-build-v3-zig-phase2-v3.json.gz",
        "485fcf3434d2c46088f8e358ce43a34aee63e3f4aacb878e63109279afb2c46c",
    ),
    "archive_bytes": 25_102,
    "uncompressed_bytes": 238_586,
    "uncompressed_sha256":
        "9f1f5b6e4b4003fc1ddcfd5139953f1b6eb63d02bfc5bd8ed4decbcbe7bb696f",
    "build_status": "PASS",
    "process_count": 15,
    "outputs": {
        "bridge": (
            "c579cf52b767b84ecc3d0a60f837d526978ace4e7739fe4cf51c2d2c8cfd90d9",
            133_656,
        ),
        "engine": (
            "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071",
            108_888,
        ),
    },
}

BUILD_PINS: dict[str, dict[str, Any]] = {
    "rust": {
        "receipt": (
            "oracle/phase2/evidence/"
            "native-source-build-v2-rust-phase2-v2-publication-receipt.json",
            "15580e4441ce651c21800df187fcfaa88ec9336322348a07d84544094d5b050e",
        ),
        "archive": (
            "oracle/phase2/evidence/native-source-build-v2-rust-phase2-v2.json.gz",
            "69b645c14ca3e566256f5a5b393a6d18554ad347b97b542383db3d86681bb35d",
        ),
        "archive_bytes": 33_741,
        "uncompressed_bytes": 279_925,
        "uncompressed_sha256":
            "389a833d6a3ce6c7aed3216759278d97d8d02dd901f758815e002f7a0031d4ec",
        "build_status": "PASS",
        "process_count": 16,
        "outputs": {
            "bridge": (
                "9e13396f93872222f77577ac7658609f5e2d3e77c0655a27c83572f0a1a06b4c",
                148_536,
            ),
            "engine": (
                "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f",
                658_344,
            ),
        },
    },
    "c": {
        "receipt": (
            "oracle/phase2/evidence/"
            "native-source-build-v2-c-phase2-v2-publication-receipt.json",
            "e90b4c12a087c0e8864c1627e242be18bd779f9d9693ec711f7dd575288eda24",
        ),
        "archive": (
            "oracle/phase2/evidence/native-source-build-v2-c-phase2-v2.json.gz",
            "4d954992312a039daa46a2810e51fc29cfdd2bd49d159dc834f5bf003e456878",
        ),
        "archive_bytes": 16_016,
        "uncompressed_bytes": 169_716,
        "uncompressed_sha256":
            "0d0a67a3c8ebba83806ba3b9beaee39e154f9d0483f0e39aac6bb04ecbfc598a",
        "build_status": "PASS",
        "process_count": 8,
        "outputs": {
            "extension": (
                "ed57383dad99ce311664d165635fa300f3894df6b4816b5f54801d0e68263697",
                163_136,
            ),
        },
    },
    "zig": {
        "receipt": (
            "oracle/phase2/evidence/"
            "native-source-build-v2-zig-phase2-v2-failures-publication-receipt.json",
            "97e3150e9b68d3031c96ea6e973097687c80163a371f99a67f8b3de08bc0707a",
        ),
        "archive": (
            "oracle/phase2/evidence/"
            "native-source-build-v2-zig-phase2-v2-failures.json.gz",
            "dc5128aaaf8a4d915c57ea8770696db3dc7ca51c89d5a3570cab9d259d070a0e",
        ),
        "archive_bytes": 19_556,
        "uncompressed_bytes": 188_479,
        "uncompressed_sha256":
            "f6ea1eb57d9ceb23c6dc5d4f291c4eb300768460a658d97828b7ce0095c53652",
        "build_status": "FAIL",
        "process_count": 15,
        "outputs": {
            "bridge": (
                "c579cf52b767b84ecc3d0a60f837d526978ace4e7739fe4cf51c2d2c8cfd90d9",
                133_656,
            ),
            "engine_reference_a": (
                "b73d43dc4bab42abc1de92e7aaf4a0b145e242ef8407714dc1bef48fc28a7d12",
                480_040,
            ),
            "engine_reference_b": (
                "69a3f024c079b8994c4ffdbf37cbecf59d5afd67c8bcf5200a7331cae66d1f53",
                480_040,
            ),
        },
    },
}
ZERO_FIELDS = (
    "candidate_imports", "candidate_processes_started", "native_libraries_loaded",
    "timing_trials_run", "hidden_cases_read", "benchmark_files_read", "clock_samples",
)
RECEIPT_FIELDS = frozenset({
    "archive_bytes", "archive_directory_fsync", "archive_publication",
    "archive_relative", "archive_sha256", "benchmark_files_read", "build_status",
    "candidate_correctness", "candidate_imports", "candidate_processes_started",
    "clock_samples", "family", "hidden_cases_read", "label",
    "native_libraries_loaded", "owned_source_sha256", "performance",
    "phase1_manifest_sha256", "protocol_sha256", "receipt_self_publication",
    "schema", "source_sha256", "status", "timing_trials_run",
    "uncompressed_bytes", "uncompressed_sha256", "winner_selected",
})
PROCESS_FIELDS = frozenset({
    "argv", "environment", "exit_status", "name", "pid", "shell",
    "stderr_base64", "stderr_bytes", "stderr_sha256", "stdout_base64",
    "stdout_bytes", "stdout_sha256",
})
C_GATE_RECEIPT_FIELDS = frozenset({
    "all_actual_process_streams_preserved",
    "archive",
    "archive_directory_fsync_completed",
    "benchmark_files_read",
    "candidate_family",
    "candidate_qualified_for_hidden_benchmark",
    "candidate_status",
    "clock_samples",
    "document_sha256",
    "failure_preserved",
    "final_holdout_authorized",
    "final_winner_selected",
    "hidden_cases_read",
    "label",
    "performance",
    "protocol_sha256",
    "schema",
    "source_sha256",
    "status",
    "timing_trials_run",
    "uncompressed_bytes",
    "uncompressed_sha256",
})


class OverviewError(Exception):
    """A chart input or truthful current-build claim failed authentication."""


class SourceOnlyError(OverviewError):
    """A synthetic chart control attempted an actual external side effect."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise OverviewError(message)


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False, sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as error:
        raise OverviewError("chart evidence must be complete canonical JSON") from error


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete evidence bytes")
    return hashlib.sha256(raw).hexdigest()


def valid_hash(value: Any, description: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
        and len(set(value)) > 1,
        "require an exact lowercase SHA-256: " + description,
    )
    return value


def unique_fields(fields: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in fields:
        require(type(name) is str and name not in result, "duplicate JSON field")
        result[name] = value
    return result


def decode_document(
    raw: bytes, description: str, *, require_canonical: bool = True,
    maximum: int = MAX_DOCUMENT_BYTES,
) -> dict[str, Any]:
    require(
        type(maximum) is int
        and 0 < maximum <= MAX_SPECIALIST_DOCUMENT_BYTES
        and type(raw) is bytes and 0 < len(raw) <= maximum,
        "require a complete bounded document: " + description,
    )
    try:
        document = json.loads(
            raw,
            object_pairs_hook=unique_fields,
            parse_constant=lambda _: (_ for _ in ()).throw(
                OverviewError("nonfinite chart evidence is forbidden")
            ),
        )
    except (TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise OverviewError("invalid chart evidence: " + description) from error
    require(type(document) is dict, "chart JSON must contain exactly one object")
    if require_canonical:
        require(
            canonical(document) == raw,
            "a chart document is not exact canonical JSON: " + description,
        )
    return document


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and bool(sys.path)
        and sys.path[0] == str(ROOT)
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.realpath(__file__) == os.path.realpath(str(ROOT / SOURCE_RELATIVE))
        and os.path.realpath(sys.executable) == os.path.realpath(PINNED_PYTHON),
        "run the exact renderer with isolated, pinned CPython 3.14.6",
    )
    require(
        not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "a current-build chart cannot import a candidate",
    )


def path_parts(relative: Any) -> tuple[str, ...]:
    require(
        type(relative) is str
        and bool(relative)
        and "\\" not in relative
        and "\x00" not in relative,
        "require a literal, repository-relative chart input",
    )
    parts = tuple(relative.split("/"))
    require(
        all(part not in ("", ".", "..") for part in parts)
        and "/".join(parts) == relative,
        "a chart input escaped its approved repository",
    )
    return parts


def pin(relative: str, digest: str) -> dict[str, str]:
    path_parts(relative)
    return {"path": relative, "sha256": valid_hash(digest, relative)}


def require_pin(value: Any, relative: str, digest: str) -> None:
    require(
        type(value) is dict
        and set(value) == {"path", "sha256"}
        and value["path"] == relative
        and valid_hash(value["sha256"], relative) == digest,
        "a pinned current source or report was replaced: " + relative,
    )


def go_owners(go_bridge_sha256: str) -> dict[str, str]:
    require(
        valid_hash(
            go_bridge_sha256, "independently committed Go bridge"
        ) == GO_BRIDGE_SHA,
        "the exact committed, pedantic-clean Go bridge was substituted",
    )
    return {
        "candidates/go_candidate.py": GO_ADAPTER_SHA,
        "candidates/go/engine.go": GO_ENGINE_SHA,
        "candidates/go/go.mod": GO_MODULE_SHA,
        "candidates/go/py_bridge.c": GO_BRIDGE_SHA,
    }


def family_owners(go_bridge_sha256: str) -> dict[str, dict[str, str]]:
    result = {family: dict(owners) for family, owners in STATIC_OWNERS.items()}
    result["go"] = go_owners(go_bridge_sha256)
    return result


def frozen_manifest(source_hash: str, go_bridge_sha256: str) -> dict[str, Any]:
    valid_hash(source_hash, "current-overview renderer")
    owners = family_owners(go_bridge_sha256)
    families: list[dict[str, Any]] = []
    for family in FAMILY_NAMES:
        row: dict[str, Any] = {
            "family": family,
            "display_name": DISPLAY_NAMES[family],
            "owned_sources": [
                pin(relative, digest)
                for relative, digest in sorted(owners.get(family, {}).items())
            ],
            "correctness": (
                "BASELINE PASS" if family == "python"
                else "FAILED; NOT QUALIFIED" if family in ("c", "rust", "zig")
                else "SOURCE ONLY; NOT BUILT; NOT TESTED; NOT QUALIFIED"
                    if family == "fortran"
                else "NOT MEASURED"
            ),
            "performance": "NOT MEASURED",
        }
        if family == "fortran":
            row["source_only"] = True
            row["build_status"] = "NOT BUILT"
            row["matching_test_status"] = "NOT TESTED"
            row["qualified"] = False
            row["included_in_frozen_v1_independence_audit"] = False
            row["included_in_frozen_v5_candidate_gate"] = False
        if family in BUILD_PINS:
            build = ZIG_V3_SUCCESS if family == "zig" else BUILD_PINS[family]
            row["build_evidence"] = {
                "archive": pin(*build["archive"]),
                "receipt": pin(*build["receipt"]),
                "expected_build_status": build["build_status"],
            }
        else:
            row["build_evidence"] = None
        if family in ("c", "rust"):
            outer = C_GATE_V5_OUTER if family == "c" else RUST_GATE_V5_OUTER
            inner = C_GATE_V5_INNER if family == "c" else RUST_GATE_V5_INNER
            passed = (
                C_V5_VERIFIED_PASSING_CASES if family == "c"
                else RUST_V5_VERIFIED_PASSING_CASES
            )
            failures = FAILED_C_V5_SUITES if family == "c" else FAILED_RUST_V5_SUITES
            subs = C_V5_SUBORDINATE_PINS if family == "c" else RUST_V5_SUBORDINATE_PINS
            row["correctness_evidence"] = {
                "archive": pin(*outer["archive"]),
                "receipt": pin(*outer["receipt"]),
                "worker_archive": pin(*inner["archive"]),
                "worker_receipt": pin(*inner["receipt"]),
                "expected_gate_status": "FAIL",
                "qualified_case_executions": 0,
                "verified_passing_case_executions": passed,
                "actual_semantic_mismatch_count": 2_094 if family == "c" else 2_042,
                "passed_suite_count": 7 if family == "c" else 8,
                "failed_suite_ids": list(failures),
                "failed_suite_case_execution_count": "NOT RECORDED",
                "supplemental_interpreter_check": "NOT RUN",
                "interpreter_failure_classification":
                    "TEST INFRASTRUCTURE; MATCHING CASE EXECUTION NOT ESTABLISHED",
            }
            row["subordinate_evidence"] = [
                pin(relative, digest) for relative, digest in subs
            ]
        else:
            row["correctness_evidence"] = None
            row["subordinate_evidence"] = []
        if family == "cpp":
            row["correctness"] = (
                "SOURCE BUILT TWICE; MATCHING NOT MEASURED; NOT QUALIFIED"
            )
            row["build_status"] = "PASS"
            row["source_build_version"] = 4
            row["fresh_source_build_count"] = 2
            row["matching_test_status"] = "NOT MEASURED"
            row["activation_status"] = "NOT RUN; NO FROZEN V3 ACTIVATION"
            row["undefined_behavior"] = "NOT MEASURED"
            row["qualified"] = False
            row["native_libraries_loaded"] = 0
            row["build_evidence"] = {
                "archive": pin(*CPP_V4_SOURCE_BUILD["archive"]),
                "receipt": pin(*CPP_V4_SOURCE_BUILD["receipt"]),
                "expected_build_status": "PASS",
                "fresh_source_build_count": 2,
                "actual_compiler_process_count": 10,
                "bridge_sha256": CPP_V4_SOURCE_BUILD["bridge_sha256"],
                "bridge_size_bytes": CPP_V4_SOURCE_BUILD["bridge_size_bytes"],
                "matching_test_status": "NOT MEASURED",
                "activation_status": "NOT RUN; NO FROZEN V3 ACTIVATION",
                "qualified": False,
            }
        if family == "zig":
            row["correctness_evidence"] = {
                "archive": pin(*ZIG_V6_OUTER["archive"]),
                "receipt": pin(*ZIG_V6_OUTER["receipt"]),
                "worker_archive": pin(*ZIG_V6_WORKER["archive"]),
                "worker_receipt": pin(*ZIG_V6_WORKER["receipt"]),
                "expected_gate_status": "FAIL",
                "qualified_case_executions": 0,
                "verified_passing_case_executions": ZIG_V6_PASSING_CASES,
                "passed_suite_count": 6,
                "failed_suite_ids": list(ZIG_V6_FAILED_SUITES),
                "actual_semantic_mismatch_count": 1_764,
                "interpreter_failure_classification": "INFRASTRUCTURE CLEANUP FAILURE; 385 REAL INTERPRETER CALLS; ZERO QUALIFIED INTERPRETER CASES",
                "actual_case_interpreter_exec_calls": 385,
                "actual_interpreters_created": 3,
                "actual_interpreters_destroyed": 3,
                "actual_initialization_interpreter_exec_calls": 3,
                "actual_guard_cleanup_interpreter_exec_calls": 4,
                "active_cleanup_case_seed": 16_650_482_535_507_372_878,
                "specialist_maximum_uncompressed_bytes": MAX_SPECIALIST_DOCUMENT_BYTES,
            }
            row["subordinate_evidence"] = [
                pin(*ZIG_V6_NESTED["archive"]), pin(*ZIG_V6_NESTED["receipt"]),
                *(
                    pin(*item[key])
                    for item in ZIG_V6_SPECIALISTS
                    for key in ("archive", "receipt")
                ),
            ]
        row["historical_worker_failure_evidence"] = (
            {
                "archive": pin(*C_GATE_V4_FAILURE["archive"]),
                "receipt": pin(*C_GATE_V4_FAILURE["receipt"]),
                "expected_gate_status": "FAIL",
                "qualified_case_executions": 0,
                "actual_failed_worker_count": 1,
            } if family == "c" else None
        )
        row["historical_build_evidence"] = (
            {
                "archive": pin(*BUILD_PINS["zig"]["archive"]),
                "receipt": pin(*BUILD_PINS["zig"]["receipt"]),
                "expected_build_status": "FAIL",
            }
            if family == "zig"
            else None
        )
        row["historical_correctness_evidence"] = (
            {
                "archive": pin(*C_GATE_FAILURE["archive"]),
                "receipt": pin(*C_GATE_FAILURE["receipt"]),
                "expected_gate_status": "FAIL",
                "qualified_case_executions": 0,
            }
            if family == "c"
            else None
        )
        families.append(row)
    return {
        "schema": SCHEMA + "-inputs",
        "version": 9,
        "python": PYTHON_VERSION,
        "renderer": pin(SOURCE_RELATIVE, source_hash),
        "frozen_inputs": {
            name: pin(relative, digest)
            for name, (relative, digest) in CORE_PINS.items()
        },
        "full_case_denominator": DENOMINATOR,
        "suite_count": len(SUITE_IDS),
        "candidate_families": list(FAMILY_NAMES),
        "families": families,
        "speed_target": {
            "relative_to_python": 1.5,
            "label": "GOAL ONLY; NOT A RESULT",
        },
        "source_only_architecture_boundary": {
            "family": "fortran",
            "included_in_frozen_v1_independence_audit": False,
            "included_in_frozen_v5_candidate_gate": False,
            "native_builds": 0,
            "matching_cases_executed": 0,
            "candidate_qualified": False,
            "correctness": "NOT MEASURED",
            "speed": "NOT MEASURED",
            "memory": "NOT MEASURED",
        },
        "final_comparison": {
            "planned_case_count": 4_194_304,
            "cases_generated": False,
            "cases_opened": False,
            "performance": "NOT MEASURED",
        },
        "boundaries": {
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance_files_read": 0,
            "hidden_cases_read": 0,
            "full_candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "final_holdout_authorized": False,
            "final_holdout_opened": False,
            "winner_selected": False,
        },
    }


def read_checked(relative: str, expected: str, maximum: int) -> bytes:
    parts = path_parts(relative)
    expected = valid_hash(expected, relative)
    require(
        type(maximum) is int and 0 < maximum <= MAX_DOCUMENT_BYTES,
        "require a bounded current-build input",
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
    descriptors: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags)
        descriptors.append(current)
        for component in parts[:-1]:
            current = os.open(component, directory_flags, dir_fd=current)
            descriptors.append(current)
        descriptor = os.open(parts[-1], flags, dir_fd=current)
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and stat.S_ISREG(named.st_mode)
            and (before.st_dev, before.st_ino)
            == (named.st_dev, named.st_ino)
            and 0 < before.st_size <= maximum,
            "reject a symlink, incomplete, oversized, or replaced chart input",
        )
        parts_read: list[bytes] = []
        remaining = before.st_size
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(type(part) is bytes and bool(part), "chart evidence was truncated")
            parts_read.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"", "chart evidence has concealed bytes")
        after = os.fstat(descriptor)
        raw = b"".join(parts_read)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            and sha256(raw) == expected,
            "current-build evidence changed or failed its exact SHA-256",
        )
        return raw
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def bounded_gzip(raw: bytes, maximum: int = MAX_DOCUMENT_BYTES) -> bytes:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES
        and type(maximum) is int
        and MAX_DOCUMENT_BYTES <= maximum <= MAX_SPECIALIST_DOCUMENT_BYTES,
        "require one complete bounded source-build archive",
    )
    try:
        decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
        expanded = decompressor.decompress(raw, maximum + 1)
        require(
            len(expanded) <= maximum
            and decompressor.eof is True
            and decompressor.unused_data == b""
            and decompressor.unconsumed_tail == b"",
            "reject clipped, concatenated, or oversized build evidence",
        )
        tail = decompressor.flush()
        require(
            len(expanded) + len(tail) <= maximum,
            "an archived source-build report exceeded its frozen bound",
        )
        return expanded + tail
    except (zlib.error, EOFError) as error:
        raise OverviewError("invalid compressed native source-build evidence") from error


def validate_baseline(document: Any) -> None:
    require(
        type(document) is dict
        and document.get("schema") == "rebar-cpython-re-p0-completeness-v1"
        and document.get("version") == 1
        and type(document.get("runtime")) is dict
        and document["runtime"].get("python_version") == PYTHON_VERSION
        and document.get("goal")
        == {
            "path": CORE_PINS["goal"][0],
            "sha256": CORE_PINS["goal"][1],
        },
        "the complete 3.14.6 Python baseline was replaced",
    )
    denominator = document.get("denominator")
    require(
        type(denominator) is dict
        and denominator.get("available_frozen_vector_case_executions")
        == DENOMINATOR
        and denominator.get("final_required_case_execution_denominator")
        == DENOMINATOR
        and denominator.get("frozen_planned_case_execution_denominator")
        == DENOMINATOR
        and denominator.get("counted_suite_ids") == list(SUITE_IDS)
        and denominator.get("full_resource_original_versions_double_counted")
        is False
        and denominator.get("historical_subinterpreter_versions_double_counted")
        is False
        and denominator.get("public_original_skip_cases_outside_runnable_denominator")
        == 1
        and denominator.get("private_upstream_methods_outside_public_denominator")
        == 13,
        "the exact complete 31,237-case Python denominator was changed",
    )
    gate = document.get("phase_gate")
    require(
        type(gate) is dict
        and gate.get("status") == "PASS"
        and gate.get("all_obligations_mapped") is True
        and gate.get("blockers") == []
        and gate.get("candidate_evaluation_authorized") is False
        and gate.get("final_holdout_authorized") is False,
        "the frozen Python reference failed or authorized a hidden holdout",
    )
    expected_candidates = {name: "NOT MEASURED" for name in ("c", "rust", "zig")}
    require(
        document.get("candidate_results") == expected_candidates,
        "the Python baseline cannot invent current candidate results",
    )
    suites = document.get("suites")
    require(
        type(suites) is list and len(suites) == len(SUITE_IDS),
        "the complete baseline lost or invented a compatibility category",
    )
    total = 0
    for suite, expected_id, expected_count in zip(
        suites, SUITE_IDS, SUITE_COUNTS, strict=True
    ):
        require(
            type(suite) is dict
            and suite.get("id") == expected_id
            and suite.get("case_execution_count") == expected_count
            and type(suite.get("baseline")) is dict
            and suite["baseline"].get("status") == "PASS"
            and suite.get("candidate_results") == expected_candidates
            and suite.get("performance") == "NOT MEASURED",
            "a full baseline category was changed, omitted, or falsely qualified",
        )
        total += expected_count
    require(total == DENOMINATOR, "the visible case totals must equal 31,237")


def validate_candidate_inventory(document: Any) -> None:
    require(
        type(document) is dict
        and document.get("schema") == "rebar-frozen-python-re-p0-candidate-protocol-v3"
        and document.get("version") == 3
        and document.get("status") == "SOURCE FROZEN; CANDIDATES NOT RUN"
        and document.get("phase") == "CANDIDATES"
        and document.get("goal_sha256") == CORE_PINS["goal"][1]
        and document.get("candidate_families") == ["rust", "c", "zig"]
        and document.get("candidate_results") == "NOT MEASURED",
        "the frozen current-build candidate gate was replaced or overstated",
    )
    phase1 = document.get("phase1")
    require(
        type(phase1) is dict
        and phase1.get("inventory_path") == CORE_PINS["phase1_inventory"][0]
        and phase1.get("inventory_sha256") == CORE_PINS["phase1_inventory"][1]
        and phase1.get("verifier_path") == CORE_PINS["phase1_verifier"][0]
        and phase1.get("verifier_sha256") == CORE_PINS["phase1_verifier"][1]
        and phase1.get("python_path") == PINNED_PYTHON
        and phase1.get("suite_count") == len(SUITE_IDS)
        and phase1.get("case_execution_denominator") == DENOMINATOR
        and phase1.get("public_obligation_count") == 73
        and phase1.get("named_private_waiver_count") == 13
        and phase1.get("runnable_original_public_methods") == 151
        and phase1.get("genuine_original_debug_skips") == 1,
        "the frozen candidate inventory changed its complete Python baseline",
    )
    native = document.get("native_source_build_v2")
    require(
        type(native) is dict
        and native.get("source_path") == CORE_PINS["native_build_runner"][0]
        and native.get("source_sha256") == CORE_PINS["native_build_runner"][1]
        and native.get("protocol_path") == CORE_PINS["native_build_protocol"][0]
        and native.get("protocol_sha256") == CORE_PINS["native_build_protocol"][1]
        and native.get("independent_fresh_phase_count") == 2
        and native.get("version_one_artifact_authorized") is False,
        "current builds must use the complete corrected two-phase build protocol",
    )
    boundaries = document.get("boundaries")
    require(
        type(boundaries) is dict
        and boundaries.get("stdlib_candidate_delegation_allowed") is False
        and boundaries.get("cross_candidate_delegation_allowed") is False
        and boundaries.get("external_regex_package_allowed") is False
        and boundaries.get("timing_allowed") is False
        and boundaries.get("hidden_case_access_allowed") is False
        and boundaries.get("final_holdout_authorized") is False
        and boundaries.get("final_holdout_opened") is False
        and boundaries.get("final_winner_selected") is False
        and boundaries.get("performance") == "NOT MEASURED",
        "candidate ownership, performance, or hidden-case boundaries were weakened",
    )


def validate_candidate_inventory_v5(document: Any) -> None:
    require(
        type(document) is dict
        and document.get("schema") == "rebar-frozen-python-re-p0-candidate-protocol-v5"
        and document.get("version") == 5
        and document.get("status") == "SOURCE FROZEN; V5 CANDIDATES NOT RUN"
        and document.get("phase") == "CANDIDATES"
        and document.get("goal_sha256") == CORE_PINS["goal"][1]
        and document.get("candidate_families") == ["rust", "c", "zig"]
        and document.get("candidate_results") == "NOT MEASURED",
        "the frozen V5 correctness protocol was replaced",
    )
    phase = document.get("phase1")
    require(
        type(phase) is dict
        and phase.get("inventory_sha256") == CORE_PINS["phase1_inventory"][1]
        and phase.get("case_execution_denominator") == DENOMINATOR
        and phase.get("suite_count") == len(SUITE_IDS)
        and phase.get("public_obligation_count") == 73
        and phase.get("named_private_waiver_count") == 13,
        "the authentic Python compatibility freeze was weakened",
    )
    suites = document.get("suites")
    require(type(suites) is list and len(suites) == len(SUITE_IDS),
            "the frozen V5 inventory omitted a compatibility category")
    for row, suite, count in zip(suites, SUITE_IDS, SUITE_COUNTS, strict=True):
        require(type(row) is dict and row.get("id") == suite
                and row.get("case_count") == count,
                "a complete V5 suite was changed: " + suite)
    worker, runner = document.get("corrected_full_case_worker_v3"), document.get("runner")
    require(
        type(worker) is dict
        and worker.get("source_path") == CORE_PINS["phase2_v5_worker"][0]
        and worker.get("source_sha256_mode")
            == "mandatory-exact-caller-pinned-published-source-bytes"
        and worker.get("preserved_original_v2_protocol_sha256")
            == CORE_PINS["phase2_v2_protocol"][1]
        and worker.get("preserved_original_v2_inventory_sha256")
            == CORE_PINS["phase2_v2_inventory"][1]
        and worker.get("complete_original_suite_count") == len(SUITE_IDS)
        and worker.get("complete_original_case_execution_denominator") == DENOMINATOR
        and worker.get("v1_validated_document_exact_dictionary_required") is True
        and worker.get("v1_validated_document_canonical_equality_required") is True
        and worker.get("strict_literal_boolean_contract_weakened") is False
        and worker.get("actual_worker_executes_original_routes") is True
        and type(runner) is dict and runner.get("path") == CORE_PINS["phase2_v5_runner"][0]
        and runner.get("source_sha256_mode")
            == "mandatory-exact-caller-pinned-published-source-bytes",
        "the corrected full-suite worker or source provenance was weakened",
    )
    boundaries = document.get("boundaries")
    require(type(boundaries) is dict and boundaries.get("performance") == "NOT MEASURED",
            "the V5 candidate freeze falsely authorized performance")
    for field in ("stdlib_candidate_delegation_allowed", "cross_candidate_delegation_allowed",
                  "external_regex_package_allowed", "original_guard_root_rebinding_allowed",
                  "timing_allowed", "hidden_case_access_allowed",
                  "final_holdout_authorized", "final_holdout_opened", "final_winner_selected"):
        require(boundaries.get(field) is False, "a V5 isolation boundary was weakened: " + field)
    for name, expected in (
        ("historical_v3_live_owner_failure", C_GATE_FAILURE),
        ("historical_v4_dict_contract_failure", C_GATE_V4_FAILURE),
    ):
        old = document.get(name)
        require(type(old) is dict
                and old.get("failure_archive_sha256") == expected["archive"][1]
                and old.get("failure_receipt_sha256") == expected["receipt"][1]
                and old.get("qualified_candidate_case_executions") == 0,
                "the frozen V5 protocol concealed an actual C failure: " + name)


def validate_manifest(
    manifest: Any, source_hash: str, go_bridge_sha256: str
) -> None:
    expected = frozen_manifest(source_hash, go_bridge_sha256)
    require(
        type(manifest) is dict and manifest == expected,
        "the complete frozen graph manifest, families, or current source closure changed",
    )
    require(
        sum(SUITE_COUNTS) == DENOMINATOR and len(SUITE_IDS) == 13,
        "the renderer changed its complete compatibility denominator",
    )
    paths: set[str] = set()
    for value in manifest["frozen_inputs"].values():
        require(value["path"] not in paths, "duplicate core chart evidence")
        paths.add(value["path"])
    for row in manifest["families"]:
        for source in row["owned_sources"]:
            require(source["path"] not in paths, "duplicate candidate source owner")
            paths.add(source["path"])
        if row["build_evidence"] is not None:
            for evidence in row["build_evidence"].values():
                if type(evidence) is dict:
                    require(
                        evidence["path"] not in paths,
                        "duplicate or cross-family native build evidence",
                    )
                    paths.add(evidence["path"])
        if row["correctness_evidence"] is not None:
            for evidence in row["correctness_evidence"].values():
                if type(evidence) is dict:
                    require(
                        evidence["path"] not in paths,
                        "duplicate or cross-family candidate-gate evidence",
                    )
                    paths.add(evidence["path"])
        for item in row.get("subordinate_evidence", []):
            require(type(item) is dict and item["path"] not in paths,
                    "duplicate or hidden subordinate actual C evidence")
            paths.add(item["path"])
        for key in ("historical_build_evidence", "historical_correctness_evidence",
                    "historical_worker_failure_evidence"):
            history = row.get(key)
            if history is not None:
                for evidence in history.values():
                    if type(evidence) is dict:
                        require(
                            evidence["path"] not in paths,
                            "duplicate, hidden, or cross-family historical evidence",
                        )
                        paths.add(evidence["path"])


def validate_zero_fields(document: dict[str, Any], description: str) -> None:
    for name in ZERO_FIELDS:
        require(
            document.get(name) == 0 and type(document.get(name)) is int,
            "a native build concealed a real external effect: "
            + description
            + ":"
            + name,
        )
    require(
        document.get("candidate_correctness") == "NOT MEASURED"
        and document.get("performance") == "NOT MEASURED"
        and document.get("winner_selected") is False,
        "a native build invented compatibility, speed, or a winner",
    )


def phase_outputs(phase: Any, family: str, name: str) -> dict[str, dict[str, Any]]:
    source_root = "<FRESH_PRIVATE_TMP>/" + name + "/source"
    native_root = "<FRESH_PRIVATE_TMP>/" + name + "/native"
    require(
        type(phase) is dict
        and phase.get("name") == name
        and phase.get("fresh_source_directory") == source_root
        and phase.get("fresh_native_directory") == native_root
        and source_root != native_root,
        "a genuine fresh source-build phase was omitted or reordered",
    )
    require(
        type(phase.get("copied_source_owners")) is dict
        and len(phase["copied_source_owners"])
        == len(STATIC_OWNERS[family]),
        "a genuine fresh phase did not copy every owned source file",
    )
    expected_owners = STATIC_OWNERS[family]
    require(
        set(phase["copied_source_owners"]) == set(expected_owners),
        "a fresh source phase substituted or omitted a source owner",
    )
    for relative, owner in phase["copied_source_owners"].items():
        require(
            type(owner) is dict
            and owner.get("sha256") == expected_owners[relative]
            and owner.get("path") == source_root + "/" + relative
            and type(owner.get("bytes")) is int
            and owner["bytes"] > 0
            and owner.get("exclusive_creation") is True
            and owner.get("same_inode_readback_verified") is True
            and owner.get("file_fsync_completed") is False
            and type(owner.get("write_calls")) is int
            and owner["write_calls"] == 1,
            "a fresh phase copied historical rather than current source",
        )
    for field in (
        "candidate_imports",
        "candidate_processes_started",
        "native_libraries_loaded",
        "timing_trials_run",
        "hidden_cases_read",
    ):
        require(
            phase.get(field) == 0 and type(phase.get(field)) is int,
            "a source-build phase ran a candidate, benchmark, or hidden case",
        )
    outputs = phase.get("native_outputs")
    expected_roles = {"extension"} if family == "c" else {"bridge", "engine"}
    require(
        type(outputs) is dict and set(outputs) == expected_roles,
        "a fresh native phase omitted or substituted an engine or bridge",
    )
    for role, output in outputs.items():
        require(
            type(output) is dict
            and output.get("family") == family
            and output.get("role") == role
            and type(output.get("file_name")) is str
            and bool(output["file_name"])
            and "/" not in output["file_name"]
            and "\\" not in output["file_name"]
            and output.get("path") == native_root + "/" + output["file_name"]
            and type(output.get("size_bytes")) is int
            and output["size_bytes"] > 0
            and output.get("candidate_imported") is False
            and output.get("prebuilt_binary_read") is False,
            "a native phase used a prebuilt or executed candidate",
        )
        valid_hash(output.get("sha256"), family + " " + role)
        elf = output.get("elf")
        require(
            type(elf) is dict
            and elf.get("external_regex_dependency_count") == 0
            and elf.get("cross_family_dependency_count") == 0,
            "a native artifact delegated regex work to an outside engine",
        )
    return outputs


def validate_process_stream(process: Any, family: str) -> None:
    require(
        type(process) is dict
        and set(process) == PROCESS_FIELDS
        and type(process.get("name")) is str
        and bool(process["name"])
        and type(process.get("pid")) is int
        and process["pid"] > 0
        and type(process.get("exit_status")) is int
        and process["exit_status"] == 0
        and process.get("shell") is False
        and type(process.get("environment")) is dict
        and type(process.get("argv")) is list
        and bool(process["argv"])
        and all(type(argument) is str for argument in process["argv"]),
        "a genuine native compiler or inspection process failed: " + family,
    )
    for role in ("stdout", "stderr"):
        text = process.get(role + "_base64")
        length = process.get(role + "_bytes")
        expected = process.get(role + "_sha256")
        require(
            type(text) is str
            and type(length) is int
            and 0 <= length <= MAX_DOCUMENT_BYTES,
            "a genuine compiler process stream was omitted: " + role,
        )
        try:
            raw = base64.b64decode(text, validate=True)
        except (TypeError, ValueError) as error:
            raise OverviewError(
                "an archived compiler process stream is not valid base64"
            ) from error
        require(
            len(raw) == length
            and sha256(raw) == valid_hash(expected, family + " " + role)
            and base64.b64encode(raw).decode("ascii") == text,
            "a complete native compiler stream was clipped: " + role,
        )


def validate_build(
    family: str,
    receipt: dict[str, Any],
    report: dict[str, Any],
    compressed_raw: bytes,
    uncompressed_raw: bytes,
    digestor: Callable[[bytes], str] = sha256,
) -> dict[str, Any]:
    expected = BUILD_PINS[family]
    owners = STATIC_OWNERS[family]
    require(
        type(receipt) is dict
        and set(receipt) == RECEIPT_FIELDS
        and receipt.get("schema")
        == "rebar-phase2-independent-native-source-build-v2-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("family") == family
        and receipt.get("label") == "phase2-v2"
        and receipt.get("build_status") == expected["build_status"]
        and receipt.get("owned_source_sha256") == owners
        and receipt.get("source_sha256") == CORE_PINS["native_build_runner"][1]
        and receipt.get("protocol_sha256")
        == CORE_PINS["native_build_protocol"][1]
        and receipt.get("phase1_manifest_sha256")
        == CORE_PINS["phase1_inventory"][1]
        and receipt.get("archive_relative") == expected["archive"][0]
        and receipt.get("archive_sha256") == expected["archive"][1]
        and receipt.get("archive_bytes") == expected["archive_bytes"]
        and receipt.get("uncompressed_sha256")
        == expected["uncompressed_sha256"]
        and receipt.get("uncompressed_bytes") == expected["uncompressed_bytes"]
        and receipt.get("receipt_self_publication") == "NOT CLAIMED",
        "a native receipt confused publication with current build correctness: "
        + family,
    )
    require(
        type(compressed_raw) is bytes
        and len(compressed_raw) == expected["archive_bytes"]
        and digestor(compressed_raw) == expected["archive"][1]
        and type(uncompressed_raw) is bytes
        and len(uncompressed_raw) == expected["uncompressed_bytes"]
        and digestor(uncompressed_raw) == expected["uncompressed_sha256"],
        "a complete source-build archive was replaced or clipped: " + family,
    )
    publication = receipt.get("archive_publication")
    require(
        type(publication) is dict
        and publication.get("exclusive_creation") is True
        and publication.get("file_fsync_completed") is True
        and publication.get("same_inode_readback_verified") is True
        and publication.get("bytes") == expected["archive_bytes"]
        and publication.get("sha256") == expected["archive"][1]
        and publication.get("path") == str(ROOT / expected["archive"][0]),
        "an authentic, durable native archive publication is required",
    )
    directory = receipt.get("archive_directory_fsync")
    require(
        type(directory) is dict and directory.get("completed") is True,
        "a native-build archive directory was not durably published",
    )
    validate_zero_fields(receipt, family + " receipt")
    require(
        type(report) is dict
        and report.get("schema")
        == "rebar-phase2-independent-native-source-build-v2"
        and report.get("status") == expected["build_status"]
        and report.get("family") == family
        and report.get("label") == "phase2-v2"
        and report.get("source_sha256") == CORE_PINS["native_build_runner"][1]
        and report.get("protocol_sha256")
        == CORE_PINS["native_build_protocol"][1]
        and report.get("owned_source_sha256") == owners,
        "the complete current native-build report contradicts its receipt",
    )
    validate_zero_fields(report, family + " archive")
    require(
        report.get("fresh_private_root") == "<FRESH_PRIVATE_TMP>"
        and report.get("network_requests") == 0
        and type(report.get("network_requests")) is int
        and report.get("reference_processes_started") == 0
        and type(report.get("reference_processes_started")) is int,
        "a native source-build used a foreign private root, network, or reference",
    )
    before, after = report.get("owned_source_before"), report.get("owned_source_after")
    require(
        type(before) is dict
        and type(after) is dict
        and set(before) == set(owners)
        and before == after,
        "the exact current source closure changed during its actual native build",
    )
    for relative, owner in before.items():
        require(
            type(owner) is dict
            and owner.get("path") == str(ROOT / relative)
            and owner.get("sha256") == owners[relative]
            and type(owner.get("device")) is int
            and owner["device"] >= 0
            and type(owner.get("inode")) is int
            and owner["inode"] > 0
            and type(owner.get("size_bytes")) is int
            and owner["size_bytes"] > 0,
            "a real source owner lost its exact stable device, inode, or bytes",
        )
    audit = report.get("source_independence_audit")
    require(
        type(audit) is dict
        and audit.get("source_owner_count") == len(owners)
        and audit.get("cross_family_dependency_count") == 0
        and audit.get("external_regex_package_count") == 0,
        "the current native engine is not independently built from scratch",
    )
    if family == "rust":
        cargo = audit.get("cargo_dependency_closure")
        require(
            type(cargo) is dict
            and cargo.get("external_package_count") == 0
            and cargo.get("registry_count") == 0
            and cargo.get("package_count") == 1
            and cargo.get("locked") is True
            and cargo.get("offline") is True
            and cargo.get("build_script_count") == 0,
            "the Rust build used a downloaded package or outside regex engine",
        )
    phase1 = report.get("phase1")
    require(
        type(phase1) is dict
        and phase1.get("status") == "PASS"
        and phase1.get("suite_count") == len(SUITE_IDS)
        and phase1.get("case_execution_count") == DENOMINATOR
        and phase1.get("candidate_correctness") == "NOT MEASURED"
        and phase1.get("performance") == "NOT MEASURED"
        and phase1.get("final_holdout_authorized") is False,
        "a build report silently changed the full correctness denominator",
    )
    processes = report.get("processes")
    require(
        type(processes) is list
        and len(processes) == expected["process_count"]
        and all(type(process) is dict and type(process.get("pid")) is int
                for process in processes)
        and len({process["pid"] for process in processes}) == len(processes),
        "the complete genuine native compiler-process stream was hidden",
    )
    for process in processes:
        validate_process_stream(process, family)
    phases = report.get("build_phases")
    require(
        type(phases) is list and len(phases) == 2,
        "exactly two actual, independently fresh native phases are required",
    )
    first = phase_outputs(phases[0], family, "reference-a")
    second = phase_outputs(phases[1], family, "reference-b")
    if family == "zig":
        error = report.get("error")
        require(
            type(error) is dict
            and error.get("type") == "BuildError"
            and error.get("message")
            == "two independent native builds are not byte-for-byte reproducible"
            and report.get("reproducibility") is None,
            "the real Zig reproducibility failure was concealed or relabelled",
        )
        bridge_hash, bridge_size = expected["outputs"]["bridge"]
        a_hash, engine_size = expected["outputs"]["engine_reference_a"]
        b_hash, other_size = expected["outputs"]["engine_reference_b"]
        require(
            engine_size == other_size
            and a_hash != b_hash
            and first["bridge"]["sha256"] == bridge_hash
            and second["bridge"]["sha256"] == bridge_hash
            and first["bridge"]["size_bytes"] == bridge_size
            and second["bridge"]["size_bytes"] == bridge_size
            and first["engine"]["sha256"] == a_hash
            and second["engine"]["sha256"] == b_hash
            and first["engine"]["size_bytes"] == engine_size
            and second["engine"]["size_bytes"] == engine_size,
            "Zig did compile twice; its real engine-byte difference must be preserved",
        )
    else:
        require(report.get("error") is None, "a successful build concealed an error")
        reproduction = report.get("reproducibility")
        require(
            type(reproduction) is dict
            and reproduction.get("byte_identical") is True
            and reproduction.get("independent_fresh_phase_count") == 2
            and reproduction.get("prebuilt_binary_count") == 0,
            "a successful candidate was not source-built identically twice",
        )
        reproduced = reproduction.get("native_outputs")
        require(
            type(reproduced) is dict and set(reproduced) == set(first),
            "the reproduced source-built artifacts are incomplete",
        )
        for role, (expected_hash, expected_size) in expected["outputs"].items():
            require(
                first[role]["sha256"] == expected_hash
                and second[role]["sha256"] == expected_hash
                and first[role]["size_bytes"] == expected_size
                and second[role]["size_bytes"] == expected_size
                and type(reproduced[role]) is dict
                and reproduced[role].get("sha256") == expected_hash
                and reproduced[role].get("size_bytes") == expected_size
                and reproduced[role].get("reproduced_in_two_fresh_directories")
                is True,
                "an older or nonreproducible native artifact was substituted",
            )
    return {
        "family": family,
        "build_status": expected["build_status"],
        "fresh_build_count": 2,
        "actual_compiler_process_count": expected["process_count"],
        "external_regex_dependency_count": 0,
        "cross_candidate_dependency_count": 0,
        "source_owner_count": len(owners),
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "zig_engine_reproduces": False if family == "zig" else None,
        "zig_bridge_reproduces": True if family == "zig" else None,
    }


def validate_c_gate_failure(
    receipt: dict[str, Any],
    report: dict[str, Any],
    compressed_raw: bytes,
    uncompressed_raw: bytes,
    digestor: Callable[[bytes], str] = sha256,
) -> dict[str, Any]:
    require(
        type(receipt) is dict
        and set(receipt) == C_GATE_RECEIPT_FIELDS
        and receipt.get("schema")
        == "rebar-frozen-python-re-p0-candidate-v3-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("candidate_family") == "c"
        and receipt.get("label") == "phase2-v3"
        and receipt.get("source_sha256") == CORE_PINS["phase2_runner"][1]
        and receipt.get("protocol_sha256") == CORE_PINS["phase2_protocol"][1]
        and receipt.get("document_sha256") == CORE_PINS["phase2_inventory"][1]
        and receipt.get("all_actual_process_streams_preserved") is True
        and receipt.get("failure_preserved") is True
        and receipt.get("archive_directory_fsync_completed") is True
        and receipt.get("uncompressed_bytes") == C_GATE_FAILURE["uncompressed_bytes"]
        and receipt.get("uncompressed_sha256")
        == C_GATE_FAILURE["uncompressed_sha256"],
        "the actual C full-suite preflight failure was omitted or falsely relabelled",
    )
    for field in (
        "benchmark_files_read", "clock_samples", "hidden_cases_read",
        "timing_trials_run",
    ):
        require(
            type(receipt.get(field)) is int and receipt[field] == 0,
            "the C gate-failure receipt invented benchmark activity: " + field,
        )
    require(
        receipt.get("candidate_qualified_for_hidden_benchmark") is False
        and receipt.get("final_holdout_authorized") is False
        and receipt.get("final_winner_selected") is False
        and receipt.get("performance") == "NOT MEASURED",
        "a failed C preflight cannot authorize candidate performance",
    )
    publication = receipt.get("archive")
    require(
        type(publication) is dict
        and publication.get("relative") == C_GATE_FAILURE["archive"][0]
        and publication.get("sha256") == C_GATE_FAILURE["archive"][1]
        and publication.get("bytes") == C_GATE_FAILURE["archive_bytes"]
        and publication.get("exclusive_creation") is True
        and publication.get("file_fsync_completed") is True
        and publication.get("same_inode_readback_verified") is True
        and type(publication.get("device")) is int
        and publication["device"] >= 0
        and type(publication.get("inode")) is int
        and publication["inode"] > 0,
        "the complete, durable C preflight failure archive was substituted",
    )
    require(
        type(compressed_raw) is bytes
        and len(compressed_raw) == C_GATE_FAILURE["archive_bytes"]
        and digestor(compressed_raw) == C_GATE_FAILURE["archive"][1]
        and type(uncompressed_raw) is bytes
        and len(uncompressed_raw) == C_GATE_FAILURE["uncompressed_bytes"]
        and digestor(uncompressed_raw) == C_GATE_FAILURE["uncompressed_sha256"],
        "the original C preflight failure bytes were clipped or replaced",
    )
    require(
        type(report) is dict
        and report.get("schema")
        == "rebar-frozen-python-re-p0-candidate-v3-actual-complete-candidate"
        and report.get("status") == "FAIL"
        and report.get("candidate_family") == "c"
        and report.get("label") == "phase2-v3"
        and report.get("source_sha256") == CORE_PINS["phase2_runner"][1]
        and report.get("protocol_sha256") == CORE_PINS["phase2_protocol"][1]
        and report.get("document_sha256") == CORE_PINS["phase2_inventory"][1]
        and report.get("goal_sha256") == CORE_PINS["goal"][1]
        and report.get("phase1_inventory_sha256")
        == CORE_PINS["phase1_inventory"][1]
        and report.get("case_execution_denominator") == DENOMINATOR
        and report.get("suite_count") == len(SUITE_IDS)
        and report.get("qualified_candidate_case_executions") == 0
        and report.get("supplemental_subinterpreter_case_count") == 0
        and report.get("supplemental_cases_added_to_original_denominator") is False
        and report.get("actual_reference_workers_started") == 0
        and report.get("failed_stage") == C_GATE_FAILURE["failed_stage"],
        "a failed C preflight was misrepresented as executed compatibility",
    )
    failure = report.get("failure")
    require(
        type(failure) is dict
        and failure.get("type") == "GateError"
        and failure.get("message") == C_GATE_FAILURE["failure_message"]
        and type(failure.get("traceback")) is list
        and bool(failure["traceback"])
        and all(type(line) is str for line in failure["traceback"]),
        "the genuine preflight controller error or traceback was concealed",
    )
    for field in (
        "benchmark_files_read", "clock_samples", "hidden_cases_read",
        "timing_trials_run", "actual_reference_workers_started",
        "qualified_candidate_case_executions",
    ):
        require(
            type(report.get(field)) is int and report[field] == 0,
            "the C preflight secretly executed a candidate or timing: " + field,
        )
    require(
        report.get("candidate_qualified") is False
        and report.get("candidate_qualified_for_hidden_benchmark") is False
        and report.get("final_holdout_authorized") is False
        and report.get("final_winner_selected") is False
        and report.get("performance") == "NOT MEASURED",
        "the failed C preflight cannot imply a correct, faster replacement",
    )
    return {
        "gate_status": "FAIL",
        "failed_before_candidate_execution": True,
        "qualified_candidate_case_executions": 0,
        "actual_reference_workers_started": 0,
        "full_case_denominator": DENOMINATOR,
        "failed_stage": C_GATE_FAILURE["failed_stage"],
        "failure_type": "GateError",
        "failure_message": C_GATE_FAILURE["failure_message"],
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "failure_archive_preserved": True,
    }



def validate_zig_v3_success(
    receipt: dict[str, Any],
    report: dict[str, Any],
    compressed_raw: bytes,
    uncompressed_raw: bytes,
    digestor: Callable[[bytes], str] = sha256,
) -> dict[str, Any]:
    expected = ZIG_V3_SUCCESS
    owners = STATIC_OWNERS["zig"]
    require(
        type(receipt) is dict
        and set(receipt) == RECEIPT_FIELDS
        and receipt.get("schema")
        == "rebar-phase2-independent-native-source-build-v3-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("build_status") == "PASS"
        and receipt.get("family") == "zig"
        and receipt.get("label") == "phase2-v3"
        and receipt.get("owned_source_sha256") == owners
        and receipt.get("source_sha256") == CORE_PINS["native_build_v3_runner"][1]
        and receipt.get("protocol_sha256") == CORE_PINS["native_build_v3_protocol"][1]
        and receipt.get("phase1_manifest_sha256") == CORE_PINS["phase1_inventory"][1]
        and receipt.get("archive_relative") == expected["archive"][0]
        and receipt.get("archive_sha256") == expected["archive"][1]
        and receipt.get("archive_bytes") == expected["archive_bytes"]
        and receipt.get("uncompressed_sha256") == expected["uncompressed_sha256"]
        and receipt.get("uncompressed_bytes") == expected["uncompressed_bytes"]
        and receipt.get("receipt_self_publication") == "NOT CLAIMED",
        "the genuine corrected Zig build and actual durable receipt were replaced",
    )
    require(
        type(compressed_raw) is bytes
        and len(compressed_raw) == expected["archive_bytes"]
        and digestor(compressed_raw) == expected["archive"][1]
        and type(uncompressed_raw) is bytes
        and len(uncompressed_raw) == expected["uncompressed_bytes"]
        and digestor(uncompressed_raw) == expected["uncompressed_sha256"],
        "the complete corrected Zig build evidence was clipped or replaced",
    )
    publication = receipt.get("archive_publication")
    directory = receipt.get("archive_directory_fsync")
    require(
        type(publication) is dict
        and publication.get("exclusive_creation") is True
        and publication.get("file_fsync_completed") is True
        and publication.get("same_inode_readback_verified") is True
        and publication.get("bytes") == expected["archive_bytes"]
        and publication.get("sha256") == expected["archive"][1]
        and publication.get("path") == str(ROOT / expected["archive"][0])
        and type(directory) is dict
        and directory.get("completed") is True,
        "the corrected Zig source-build evidence was not durably preserved",
    )
    validate_zero_fields(receipt, "corrected Zig source-build receipt")
    require(
        type(report) is dict
        and report.get("schema") == "rebar-phase2-independent-native-source-build-v3"
        and report.get("status") == "PASS"
        and report.get("family") == "zig"
        and report.get("label") == "phase2-v3"
        and report.get("source_sha256") == CORE_PINS["native_build_v3_runner"][1]
        and report.get("protocol_sha256") == CORE_PINS["native_build_v3_protocol"][1]
        and report.get("owned_source_sha256") == owners
        and report.get("fresh_private_root") == "<FRESH_PRIVATE_TMP>"
        and report.get("network_requests") == 0
        and report.get("reference_processes_started") == 0
        and report.get("error") is None,
        "the genuine corrected Zig source-build report was changed",
    )
    validate_zero_fields(report, "corrected Zig source-build archive")
    before, after = report.get("owned_source_before"), report.get("owned_source_after")
    require(
        type(before) is dict and type(after) is dict
        and set(before) == set(owners)
        and before == after,
        "corrected Zig source ownership changed between the genuine fresh builds",
    )
    for relative, owner in before.items():
        require(
            type(owner) is dict
            and owner.get("path") == str(ROOT / relative)
            and owner.get("sha256") == owners[relative]
            and type(owner.get("device")) is int
            and owner["device"] >= 0
            and type(owner.get("inode")) is int
            and owner["inode"] > 0
            and type(owner.get("size_bytes")) is int
            and owner["size_bytes"] > 0,
            "the corrected Zig engine lost an actual complete source owner",
        )
    audit = report.get("source_independence_audit")
    require(
        type(audit) is dict
        and audit.get("source_owner_count") == len(owners)
        and audit.get("cross_family_dependency_count") == 0
        and audit.get("external_regex_package_count") == 0,
        "the corrected Zig engine delegated matching or lost source ownership",
    )
    phase1 = report.get("phase1")
    require(
        type(phase1) is dict
        and phase1.get("status") == "PASS"
        and phase1.get("suite_count") == len(SUITE_IDS)
        and phase1.get("case_execution_count") == DENOMINATOR
        and phase1.get("candidate_correctness") == "NOT MEASURED"
        and phase1.get("performance") == "NOT MEASURED"
        and phase1.get("final_holdout_authorized") is False,
        "the corrected Zig source build invented a full correctness result",
    )
    processes = report.get("processes")
    require(
        type(processes) is list
        and len(processes) == expected["process_count"]
        and all(type(process) is dict and type(process.get("pid")) is int
                for process in processes)
        and len({process["pid"] for process in processes}) == len(processes),
        "the corrected Zig compiler or symbol-audit stream was concealed",
    )
    for process in processes:
        validate_process_stream(process, "zig")
    compiler_runs = [
        process for process in processes if process.get("name") == "build_zig_engine"
    ]
    require(
        len(compiler_runs) == 2
        and all(process["argv"].count("-fstrip") == 1 for process in compiler_runs)
        and not any("strip" in process["name"].lower() for process in processes),
        "each corrected Zig build requires exactly one genuine compiler strip",
    )
    phases = report.get("build_phases")
    require(
        type(phases) is list and len(phases) == 2,
        "the corrected Zig engine requires two independently fresh phases",
    )
    first = phase_outputs(phases[0], "zig", "reference-a")
    second = phase_outputs(phases[1], "zig", "reference-b")
    reproduction = report.get("reproducibility")
    require(
        type(reproduction) is dict
        and reproduction.get("byte_identical") is True
        and reproduction.get("independent_fresh_phase_count") == 2
        and reproduction.get("prebuilt_binary_count") == 0
        and type(reproduction.get("native_outputs")) is dict
        and set(reproduction["native_outputs"]) == {"bridge", "engine"},
        "the corrected Zig artifacts are not independently byte-for-byte reproducible",
    )
    for role, (expected_hash, expected_size) in expected["outputs"].items():
        reproduced = reproduction["native_outputs"][role]
        require(
            first[role]["sha256"] == expected_hash
            and second[role]["sha256"] == expected_hash
            and first[role]["size_bytes"] == expected_size
            and second[role]["size_bytes"] == expected_size
            and type(reproduced) is dict
            and reproduced.get("sha256") == expected_hash
            and reproduced.get("size_bytes") == expected_size
            and reproduced.get("reproduced_in_two_fresh_directories") is True,
            "the corrected Zig engine or bridge is not the actual reproduced bytes",
        )
    return {
        "family": "zig",
        "build_status": "PASS",
        "fresh_build_count": 2,
        "actual_compiler_process_count": expected["process_count"],
        "external_regex_dependency_count": 0,
        "cross_candidate_dependency_count": 0,
        "source_owner_count": len(owners),
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "zig_engine_reproduces": True,
        "zig_bridge_reproduces": True,
        "compiler_strip_count_per_engine": 1,
        "prior_nonreproducible_build_preserved": True,
    }


def validate_c_gate_v4_failure(
    receipt: dict[str, Any],
    report: dict[str, Any],
    compressed_raw: bytes,
    uncompressed_raw: bytes,
    digestor: Callable[[bytes], str] = sha256,
) -> dict[str, Any]:
    require(
        type(receipt) is dict
        and set(receipt) == C_GATE_RECEIPT_FIELDS
        and receipt.get("schema")
        == "rebar-frozen-python-re-p0-candidate-v4-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("candidate_family") == "c"
        and receipt.get("label") == "phase2-v4"
        and receipt.get("source_sha256") == CORE_PINS["phase2_v4_runner"][1]
        and receipt.get("protocol_sha256") == CORE_PINS["phase2_v4_protocol"][1]
        and receipt.get("document_sha256") == CORE_PINS["phase2_v4_inventory"][1]
        and receipt.get("all_actual_process_streams_preserved") is True
        and receipt.get("failure_preserved") is True
        and receipt.get("archive_directory_fsync_completed") is True
        and receipt.get("uncompressed_bytes") == C_GATE_V4_FAILURE["uncompressed_bytes"]
        and receipt.get("uncompressed_sha256")
        == C_GATE_V4_FAILURE["uncompressed_sha256"],
        "the actual C full-suite preflight failure was omitted or falsely relabelled",
    )
    for field in (
        "benchmark_files_read", "clock_samples", "hidden_cases_read",
        "timing_trials_run",
    ):
        require(
            type(receipt.get(field)) is int and receipt[field] == 0,
            "the C gate-failure receipt invented benchmark activity: " + field,
        )
    require(
        receipt.get("candidate_qualified_for_hidden_benchmark") is False
        and receipt.get("final_holdout_authorized") is False
        and receipt.get("final_winner_selected") is False
        and receipt.get("performance") == "NOT MEASURED",
        "a failed C preflight cannot authorize candidate performance",
    )
    publication = receipt.get("archive")
    require(
        type(publication) is dict
        and publication.get("relative") == C_GATE_V4_FAILURE["archive"][0]
        and publication.get("sha256") == C_GATE_V4_FAILURE["archive"][1]
        and publication.get("bytes") == C_GATE_V4_FAILURE["archive_bytes"]
        and publication.get("exclusive_creation") is True
        and publication.get("file_fsync_completed") is True
        and publication.get("same_inode_readback_verified") is True
        and type(publication.get("device")) is int
        and publication["device"] >= 0
        and type(publication.get("inode")) is int
        and publication["inode"] > 0,
        "the complete, durable C preflight failure archive was substituted",
    )
    require(
        type(compressed_raw) is bytes
        and len(compressed_raw) == C_GATE_V4_FAILURE["archive_bytes"]
        and digestor(compressed_raw) == C_GATE_V4_FAILURE["archive"][1]
        and type(uncompressed_raw) is bytes
        and len(uncompressed_raw) == C_GATE_V4_FAILURE["uncompressed_bytes"]
        and digestor(uncompressed_raw) == C_GATE_V4_FAILURE["uncompressed_sha256"],
        "the original C preflight failure bytes were clipped or replaced",
    )
    require(
        type(report) is dict
        and report.get("schema")
        == "rebar-frozen-python-re-p0-candidate-v4-actual-complete-candidate"
        and report.get("status") == "FAIL"
        and report.get("candidate_family") == "c"
        and report.get("label") == "phase2-v4"
        and report.get("source_sha256") == CORE_PINS["phase2_v4_runner"][1]
        and report.get("protocol_sha256") == CORE_PINS["phase2_v4_protocol"][1]
        and report.get("document_sha256") == CORE_PINS["phase2_v4_inventory"][1]
        and report.get("goal_sha256") == CORE_PINS["goal"][1]
        and report.get("phase1_inventory_sha256")
        == CORE_PINS["phase1_inventory"][1]
        and report.get("case_execution_denominator") == DENOMINATOR
        and report.get("suite_count") == len(SUITE_IDS)
        and report.get("qualified_candidate_case_executions") == 0
        and report.get("supplemental_subinterpreter_case_count") == 0
        and report.get("supplemental_cases_added_to_original_denominator") is False
        and report.get("actual_reference_workers_started") == 0
        and report.get("failed_stage") == C_GATE_V4_FAILURE["failed_stage"],
        "a failed C preflight was misrepresented as executed compatibility",
    )
    failure = report.get("failure")
    require(
        type(failure) is dict
        and failure.get("type") == "WorkerFailure"
        and failure.get("message") == C_GATE_V4_FAILURE["failure_message"]
        and type(failure.get("traceback")) is list
        and bool(failure["traceback"])
        and all(type(line) is str for line in failure["traceback"]),
        "the genuine preflight controller error or traceback was concealed",
    )
    for field in (
        "benchmark_files_read", "clock_samples", "hidden_cases_read",
        "timing_trials_run", "actual_reference_workers_started",
        "qualified_candidate_case_executions",
    ):
        require(
            type(report.get(field)) is int and report[field] == 0,
            "the C preflight secretly executed a candidate or timing: " + field,
        )
    require(
        report.get("candidate_qualified") is False
        and report.get("candidate_qualified_for_hidden_benchmark") is False
        and report.get("final_holdout_authorized") is False
        and report.get("final_winner_selected") is False
        and report.get("performance") == "NOT MEASURED",
        "the failed C preflight cannot imply a correct, faster replacement",
    )
    worker = report.get("failed_worker_process")
    require(
        type(worker) is dict
        and type(worker.get("pid")) is int
        and worker["pid"] > 0
        and type(worker.get("returncode")) is int
        and worker["returncode"] == 1
        and worker.get("timed_out") is False
        and worker.get("signal") is None,
        "the genuine failed C worker was relabelled as an absent preflight",
    )
    preserved = report.get("preserved_v3_actual_failure")
    require(
        type(preserved) is dict
        and preserved.get("schema")
        == "rebar-frozen-python-re-p0-candidate-v4-independently-verified-preserved-v3-failure"
        and preserved.get("status") == "PASS"
        and preserved.get("failure_preserved") is True
        and preserved.get("failure_archive_sha256") == C_GATE_FAILURE["archive"][1]
        and preserved.get("failure_receipt_sha256") == C_GATE_FAILURE["receipt"][1]
        and preserved.get("failure_uncompressed_sha256")
        == C_GATE_FAILURE["uncompressed_sha256"]
        and preserved.get("actual_candidate_cases_executed") == 0
        and preserved.get("candidate_was_qualified") is False
        and preserved.get("holdout_opened") is False
        and preserved.get("performance") == "NOT MEASURED"
        and preserved.get("version_three_document_sha256")
        == CORE_PINS["phase2_inventory"][1]
        and preserved.get("version_three_protocol_sha256")
        == CORE_PINS["phase2_protocol"][1]
        and preserved.get("version_three_source_sha256")
        == CORE_PINS["phase2_runner"][1],
        "the prior genuine C V3 preflight failure was concealed",
    )
    promotion = report.get("corrected_promotion_before_full_p0")
    require(
        type(promotion) is dict
        and promotion.get("status") == "PASS"
        and promotion.get("family") == "c"
        and promotion.get("all_native_roles_intent_verified") is True,
        "the corrected C V4 promotion proof was lost or falsely reported",
    )

    return {
        "gate_status": "FAIL",
        "failed_before_candidate_execution": False,
        "actual_failed_worker_count": 1,
        "qualified_candidate_case_executions": 0,
        "actual_reference_workers_started": 0,
        "full_case_denominator": DENOMINATOR,
        "failed_stage": C_GATE_V4_FAILURE["failed_stage"],
        "failure_type": "WorkerFailure",
        "failure_message": C_GATE_V4_FAILURE["failure_message"],
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "failure_archive_preserved": True,
    }


def _v5_publication(
    receipt: Any, expected: dict[str, Any],
    source_key: str, protocol_key: str, inventory_key: str, worker: bool,
) -> dict[str, Any]:
    fields = C_GATE_RECEIPT_FIELDS - (
        frozenset({"all_actual_process_streams_preserved"}) if worker else frozenset()
    )
    require(
        type(receipt) is dict and set(receipt) == fields
        and receipt.get("schema") == (
            "rebar-frozen-python-re-p0-candidate-worker-v3-durable-publication-receipt"
            if worker else "rebar-frozen-python-re-p0-candidate-v5-durable-publication-receipt"
        )
        and receipt.get("status") == "PASS"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("candidate_family") == "c"
        and receipt.get("label") == "phase2-v5"
        and receipt.get("source_sha256") == CORE_PINS[source_key][1]
        and receipt.get("protocol_sha256") == CORE_PINS[protocol_key][1]
        and receipt.get("document_sha256") == CORE_PINS[inventory_key][1]
        and receipt.get("failure_preserved") is True
        and receipt.get("archive_directory_fsync_completed") is True
        and receipt.get("uncompressed_bytes") == expected["uncompressed_bytes"]
        and receipt.get("uncompressed_sha256") == expected["uncompressed_sha256"],
        "never confuse successful V5 evidence publication with a candidate pass",
    )
    if not worker:
        require(receipt.get("all_actual_process_streams_preserved") is True,
                "the complete actual outer worker stream was omitted")
    publication = receipt.get("archive")
    require(type(publication) is dict
            and publication.get("relative") == expected["archive"][0]
            and publication.get("sha256") == expected["archive"][1]
            and publication.get("bytes") == expected["archive_bytes"]
            and publication.get("exclusive_creation") is True
            and publication.get("file_fsync_completed") is True
            and publication.get("same_inode_readback_verified") is True
            and type(publication.get("device")) is int and publication["device"] >= 0
            and type(publication.get("inode")) is int and publication["inode"] > 0,
            "the exact complete durable V5 failure archive was substituted")
    for field in ("benchmark_files_read", "clock_samples", "hidden_cases_read", "timing_trials_run"):
        require(type(receipt.get(field)) is int and receipt[field] == 0,
                "a V5 candidate receipt concealed benchmark access: " + field)
    require(receipt.get("performance") == "NOT MEASURED"
            and receipt.get("final_holdout_authorized") is False
            and receipt.get("candidate_qualified_for_hidden_benchmark") is False
            and receipt.get("final_winner_selected") is False,
            "a genuine failed candidate never authorizes hidden benchmarking")
    return publication


def _rust_v5_publication(
    receipt: Any, expected: dict[str, Any],
    source_key: str, protocol_key: str, inventory_key: str, worker: bool,
) -> dict[str, Any]:
    fields = C_GATE_RECEIPT_FIELDS - (
        frozenset({"all_actual_process_streams_preserved"}) if worker else frozenset()
    )
    require(
        type(receipt) is dict and set(receipt) == fields
        and receipt.get("schema") == (
            "rebar-frozen-python-re-p0-candidate-worker-v3-durable-publication-receipt"
            if worker else "rebar-frozen-python-re-p0-candidate-v5-durable-publication-receipt"
        )
        and receipt.get("status") == "PASS"
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("candidate_family") == "rust"
        and receipt.get("label") == "phase2-v5"
        and receipt.get("source_sha256") == CORE_PINS[source_key][1]
        and receipt.get("protocol_sha256") == CORE_PINS[protocol_key][1]
        and receipt.get("document_sha256") == CORE_PINS[inventory_key][1]
        and receipt.get("failure_preserved") is True
        and receipt.get("archive_directory_fsync_completed") is True
        and receipt.get("uncompressed_bytes") == expected["uncompressed_bytes"]
        and receipt.get("uncompressed_sha256") == expected["uncompressed_sha256"],
        "never confuse successful V5 evidence publication with a candidate pass",
    )
    if not worker:
        require(receipt.get("all_actual_process_streams_preserved") is True,
                "the complete actual outer worker stream was omitted")
    publication = receipt.get("archive")
    require(type(publication) is dict
            and publication.get("relative") == expected["archive"][0]
            and publication.get("sha256") == expected["archive"][1]
            and publication.get("bytes") == expected["archive_bytes"]
            and publication.get("exclusive_creation") is True
            and publication.get("file_fsync_completed") is True
            and publication.get("same_inode_readback_verified") is True
            and type(publication.get("device")) is int and publication["device"] >= 0
            and type(publication.get("inode")) is int and publication["inode"] > 0,
            "the exact complete durable V5 failure archive was substituted")
    for field in ("benchmark_files_read", "clock_samples", "hidden_cases_read", "timing_trials_run"):
        require(type(receipt.get(field)) is int and receipt[field] == 0,
                "a V5 candidate receipt concealed benchmark access: " + field)
    require(receipt.get("performance") == "NOT MEASURED"
            and receipt.get("final_holdout_authorized") is False
            and receipt.get("candidate_qualified_for_hidden_benchmark") is False
            and receipt.get("final_winner_selected") is False,
            "a genuine failed candidate never authorizes hidden benchmarking")
    return publication


def _v5_archive_bytes(raw: bytes, expanded: bytes, expected: dict[str, Any],
                      digestor: Callable[[bytes], str]) -> None:
    require(type(raw) is bytes and len(raw) == expected["archive_bytes"]
            and digestor(raw) == expected["archive"][1]
            and type(expanded) is bytes
            and len(expanded) == expected["uncompressed_bytes"]
            and len(expanded) <= MAX_DOCUMENT_BYTES
            and digestor(expanded) == expected["uncompressed_sha256"],
            "the complete actual V5 failure archive was truncated or changed")


def validate_c_gate_v5_failure(
    outer_receipt: dict[str, Any], outer: dict[str, Any],
    outer_compressed: bytes, outer_expanded: bytes,
    inner_receipt: dict[str, Any], inner: dict[str, Any],
    inner_compressed: bytes, inner_expanded: bytes,
    digestor: Callable[[bytes], str] = sha256,
) -> dict[str, Any]:
    _v5_publication(outer_receipt, C_GATE_V5_OUTER, "phase2_v5_runner",
                    "phase2_v5_protocol", "phase2_v5_inventory", False)
    inner_publication = _v5_publication(inner_receipt, C_GATE_V5_INNER,
                    "phase2_v5_worker", "phase2_v2_protocol", "phase2_v2_inventory", True)
    _v5_archive_bytes(outer_compressed, outer_expanded, C_GATE_V5_OUTER, digestor)
    _v5_archive_bytes(inner_compressed, inner_expanded, C_GATE_V5_INNER, digestor)
    require(type(outer) is dict
            and outer.get("schema") == "rebar-frozen-python-re-p0-candidate-v5-actual-complete-candidate"
            and outer.get("status") == "FAIL"
            and outer.get("candidate_family") == "c" and outer.get("label") == "phase2-v5"
            and outer.get("source_sha256") == CORE_PINS["phase2_v5_runner"][1]
            and outer.get("protocol_sha256") == CORE_PINS["phase2_v5_protocol"][1]
            and outer.get("document_sha256") == CORE_PINS["phase2_v5_inventory"][1]
            and outer.get("goal_sha256") == CORE_PINS["goal"][1]
            and outer.get("phase1_inventory_sha256") == CORE_PINS["phase1_inventory"][1]
            and outer.get("suite_count") == len(SUITE_IDS)
            and outer.get("case_execution_denominator") == DENOMINATOR
            and outer.get("qualified_candidate_case_executions") == 0
            and outer.get("candidate_qualified") is False
            and outer.get("supplemental_subinterpreter_case_count") == 0
            and outer.get("supplemental_cases_added_to_original_denominator") is False
            and outer.get("failed_stage") == C_GATE_V5_OUTER["failed_stage"],
            "the actual C V5 aggregate falsely claimed completed compatibility")
    failure, process = outer.get("failure"), outer.get("failed_worker_process")
    require(type(failure) is dict and failure.get("type") == "WorkerFailure"
            and failure.get("message") == C_GATE_V5_OUTER["failure_message"]
            and type(failure.get("traceback")) is list and bool(failure["traceback"])
            and type(process) is dict and type(process.get("pid")) is int
            and process["pid"] > 0 and process.get("returncode") == 1
            and process.get("timed_out") is False and process.get("signal") is None,
            "the actual failed corrected C worker was mislabeled as preflight")
    stdout, stderr = process.get("stdout"), process.get("stderr")
    require(type(stdout) is dict and stdout.get("complete") is True
            and stdout.get("encoding") == "base64" and type(stdout.get("data")) is str
            and type(stdout.get("bytes")) is int and stdout["bytes"] > 0
            and type(stderr) is dict and stderr.get("complete") is True
            and stderr.get("encoding") == "base64" and stderr.get("bytes") == 0,
            "the failed full-suite worker concealed complete process streams")
    try:
        worker_raw = base64.b64decode(stdout["data"], validate=True)
        empty_raw = base64.b64decode(stderr.get("data"), validate=True)
    except (ValueError, TypeError) as error:
        raise OverviewError("invalid exact complete base64 V5 worker stream") from error
    require(len(worker_raw) == stdout["bytes"] and sha256(worker_raw) == stdout.get("sha256")
            and empty_raw == b"" and sha256(empty_raw) == stderr.get("sha256"),
            "the actual corrected worker stdout or stderr was truncated")
    published = decode_document(worker_raw, "complete V5 failed-worker stdout")
    receipt_owner = published.get("complete_publication_receipt")
    require(published.get("schema")
                == "rebar-frozen-python-re-p0-candidate-worker-v3-published-complete-candidate"
            and published.get("status") == "FAIL"
            and published.get("candidate_family") == "c"
            and published.get("label") == "phase2-v5"
            and published.get("suite_count") == len(SUITE_IDS)
            and published.get("case_execution_denominator") == DENOMINATOR
            and published.get("completed_candidate_suite_count") == 7
            and published.get("qualified_candidate_case_executions")
                == C_V5_VERIFIED_PASSING_CASES
            and published.get("candidate_qualified") is False
            and published.get("all_mismatches_crashes_and_timeouts_preserved") is True
            and published.get("complete_archive") == inner_publication
            and type(receipt_owner) is dict
            and receipt_owner.get("relative") == C_GATE_V5_INNER["receipt"][0]
            and receipt_owner.get("sha256") == C_GATE_V5_INNER["receipt"][1]
            and receipt_owner.get("exclusive_creation") is True
            and receipt_owner.get("file_fsync_completed") is True
            and receipt_owner.get("same_inode_readback_verified") is True,
            "the outer failed process does not authenticate the actual inner C report")
    require(type(inner) is dict
            and inner.get("schema")
                == "rebar-frozen-python-re-p0-candidate-worker-v3-complete-candidate-evaluation"
            and inner.get("status") == "FAIL"
            and inner.get("candidate_family") == "c" and inner.get("label") == "phase2-v5"
            and inner.get("source_sha256") == CORE_PINS["phase2_v5_worker"][1]
            and inner.get("protocol_sha256") == CORE_PINS["phase2_v2_protocol"][1]
            and inner.get("document_sha256") == CORE_PINS["phase2_v2_inventory"][1]
            and inner.get("goal_sha256") == CORE_PINS["goal"][1]
            and inner.get("phase1_inventory_sha256") == CORE_PINS["phase1_inventory"][1]
            and inner.get("suite_count") == len(SUITE_IDS)
            and inner.get("case_execution_denominator") == DENOMINATOR
            and inner.get("all_required_suites_executed") is True
            and inner.get("all_required_suites_passed") is False
            and inner.get("completed_candidate_suite_count") == 7
            and inner.get("qualified_candidate_case_executions")
                == C_V5_VERIFIED_PASSING_CASES
            and inner.get("candidate_qualified") is False
            and inner.get("complete_owned_source_sha256") == STATIC_OWNERS["c"],
            "the complete genuine C inner candidate evidence was replaced")
    suites, reasons = inner.get("all_suites"), inner.get("all_failure_reasons")
    require(type(suites) is list and len(suites) == len(SUITE_IDS)
            and type(reasons) is list and len(reasons) == len(FAILED_C_V5_SUITES),
            "the complete 13 C candidate routes or six failing groups were hidden")
    failed: list[str] = []
    verified = 0
    passing = 0
    for row, suite, count in zip(suites, SUITE_IDS, SUITE_COUNTS, strict=True):
        require(type(row) is dict and row.get("suite") == suite
                and row.get("candidate_family") == "c"
                and row.get("case_execution_denominator") == count
                and type(row.get("actual_process")) is dict,
                "an actual C test route was omitted: " + suite)
        if suite in FAILED_C_V5_SUITES:
            require(row.get("status") == "FAIL"
                    and "actual_candidate_case_count" not in row
                    and type(row.get("failure")) is dict
                    and row["failure"].get("type") == "CandidateGateError"
                    and type(row["failure"].get("message")) is str
                    and type(row["failure"].get("traceback")) is list
                    and bool(row["failure"]["traceback"]),
                    "never invent the executed count of a failed group: " + suite)
            failed.append(suite)
        else:
            require(row.get("status") == "PASS"
                    and type(row.get("actual_candidate_case_count")) is int
                    and row["actual_candidate_case_count"] == count
                    and row.get("failure") is None,
                    "an actual verified passing group was changed: " + suite)
            verified += count
            passing += 1
    require(tuple(failed) == FAILED_C_V5_SUITES and passing == 7
            and verified == C_V5_VERIFIED_PASSING_CASES
            and reasons == [row["failure"] for row in suites if row["status"] == "FAIL"],
            "seven passing groups or six real failures were overstated")
    for doc, label in ((outer, "outer"), (inner, "inner"), (published, "worker")):
        for field in ("benchmark_files_read", "clock_samples", "hidden_cases_read",
                      "timing_trials_run"):
            require(type(doc.get(field)) is int and doc[field] == 0,
                    "hidden benchmark access in actual C " + label + ": " + field)
        require(doc.get("performance") == "NOT MEASURED"
                and doc.get("final_holdout_authorized") is False
                and doc.get("candidate_qualified_for_hidden_benchmark") is False
                and doc.get("final_winner_selected") is False,
                "a failed C " + label + " cannot authorize a holdout or winner")
    for old, expected, version in (
        (outer.get("preserved_v3_actual_failure"), C_GATE_FAILURE, "v3"),
        (outer.get("preserved_v4_actual_failure"), C_GATE_V4_FAILURE, "v4"),
    ):
        require(type(old) is dict and old.get("status") == "PASS"
                and old.get("performance") == "NOT MEASURED"
                and ((old.get("failure_archive_sha256") == expected["archive"][1]
                      and old.get("failure_receipt_sha256") == expected["receipt"][1])
                     if version == "v3" else
                     (old.get("archive_sha256") == expected["archive"][1]
                      and old.get("receipt_sha256") == expected["receipt"][1])),
                "the actual V5 report concealed prior C " + version + " failure")
    promotion = outer.get("corrected_promotion_before_full_p0")
    require(type(promotion) is dict and promotion.get("status") == "PASS"
            and promotion.get("family") == "c"
            and promotion.get("all_native_roles_intent_verified") is True,
            "the actual C gate omitted its genuine owned native activation")
    return {
        "gate_status": "FAIL", "failed_before_candidate_execution": False,
        "actual_failed_worker_count": 1, "qualified_candidate_count": 0,
        "qualified_candidate_case_executions": 0,
        "verified_passing_case_executions": verified,
        "completed_passing_suite_count": passing,
        "attempted_suite_route_count": len(suites),
        "all_required_suite_routes_attempted": True,
        "failed_suite_count": len(failed), "failed_suite_ids": failed,
        "failed_suite_case_execution_count": "NOT RECORDED",
        "supplemental_interpreter_check": "NOT RUN",
        "actual_reference_workers_started": 0,
        "full_case_denominator": DENOMINATOR,
        "failed_stage": C_GATE_V5_OUTER["failed_stage"],
        "failure_type": "WorkerFailure",
        "failure_message": C_GATE_V5_OUTER["failure_message"],
        "candidate_correctness": "FAILED; NOT QUALIFIED",
        "performance": "NOT MEASURED",
        "failure_archive_preserved": True,
        "all_actual_process_streams_preserved": True,
        "subordinate_evidence_owner_count": len(C_V5_SUBORDINATE_PINS),
        "outer_and_inner_evidence_owner_count": 4,
    }


def validate_rust_gate_v5_failure(
    outer_receipt: dict[str, Any], outer: dict[str, Any],
    outer_compressed: bytes, outer_expanded: bytes,
    inner_receipt: dict[str, Any], inner: dict[str, Any],
    inner_compressed: bytes, inner_expanded: bytes,
    digestor: Callable[[bytes], str] = sha256,
) -> dict[str, Any]:
    _rust_v5_publication(outer_receipt, RUST_GATE_V5_OUTER, "phase2_v5_runner",
                    "phase2_v5_protocol", "phase2_v5_inventory", False)
    inner_publication = _rust_v5_publication(inner_receipt, RUST_GATE_V5_INNER,
                    "phase2_v5_worker", "phase2_v2_protocol", "phase2_v2_inventory", True)
    _v5_archive_bytes(outer_compressed, outer_expanded, RUST_GATE_V5_OUTER, digestor)
    _v5_archive_bytes(inner_compressed, inner_expanded, RUST_GATE_V5_INNER, digestor)
    require(type(outer) is dict
            and outer.get("schema") == "rebar-frozen-python-re-p0-candidate-v5-actual-complete-candidate"
            and outer.get("status") == "FAIL"
            and outer.get("candidate_family") == "rust" and outer.get("label") == "phase2-v5"
            and outer.get("source_sha256") == CORE_PINS["phase2_v5_runner"][1]
            and outer.get("protocol_sha256") == CORE_PINS["phase2_v5_protocol"][1]
            and outer.get("document_sha256") == CORE_PINS["phase2_v5_inventory"][1]
            and outer.get("goal_sha256") == CORE_PINS["goal"][1]
            and outer.get("phase1_inventory_sha256") == CORE_PINS["phase1_inventory"][1]
            and outer.get("suite_count") == len(SUITE_IDS)
            and outer.get("case_execution_denominator") == DENOMINATOR
            and outer.get("qualified_candidate_case_executions") == 0
            and outer.get("candidate_qualified") is False
            and outer.get("supplemental_subinterpreter_case_count") == 0
            and outer.get("supplemental_cases_added_to_original_denominator") is False
            and outer.get("failed_stage") == RUST_GATE_V5_OUTER["failed_stage"],
            "the actual Rust V5 aggregate falsely claimed completed compatibility")
    failure, process = outer.get("failure"), outer.get("failed_worker_process")
    require(type(failure) is dict and failure.get("type") == "WorkerFailure"
            and failure.get("message") == RUST_GATE_V5_OUTER["failure_message"]
            and type(failure.get("traceback")) is list and bool(failure["traceback"])
            and type(process) is dict and type(process.get("pid")) is int
            and process["pid"] > 0 and process.get("returncode") == 1
            and process.get("timed_out") is False and process.get("signal") is None,
            "the actual failed corrected Rust worker was mislabeled as preflight")
    stdout, stderr = process.get("stdout"), process.get("stderr")
    require(type(stdout) is dict and stdout.get("complete") is True
            and stdout.get("encoding") == "base64" and type(stdout.get("data")) is str
            and type(stdout.get("bytes")) is int and stdout["bytes"] > 0
            and type(stderr) is dict and stderr.get("complete") is True
            and stderr.get("encoding") == "base64" and stderr.get("bytes") == 0,
            "the failed full-suite worker concealed complete process streams")
    try:
        worker_raw = base64.b64decode(stdout["data"], validate=True)
        empty_raw = base64.b64decode(stderr.get("data"), validate=True)
    except (ValueError, TypeError) as error:
        raise OverviewError("invalid exact complete base64 V5 worker stream") from error
    require(len(worker_raw) == stdout["bytes"] and sha256(worker_raw) == stdout.get("sha256")
            and empty_raw == b"" and sha256(empty_raw) == stderr.get("sha256"),
            "the actual corrected worker stdout or stderr was truncated")
    published = decode_document(worker_raw, "complete V5 failed-worker stdout")
    receipt_owner = published.get("complete_publication_receipt")
    require(published.get("schema")
                == "rebar-frozen-python-re-p0-candidate-worker-v3-published-complete-candidate"
            and published.get("status") == "FAIL"
            and published.get("candidate_family") == "rust"
            and published.get("label") == "phase2-v5"
            and published.get("suite_count") == len(SUITE_IDS)
            and published.get("case_execution_denominator") == DENOMINATOR
            and published.get("completed_candidate_suite_count") == 8
            and published.get("qualified_candidate_case_executions")
                == RUST_V5_VERIFIED_PASSING_CASES
            and published.get("candidate_qualified") is False
            and published.get("all_mismatches_crashes_and_timeouts_preserved") is True
            and published.get("complete_archive") == inner_publication
            and type(receipt_owner) is dict
            and receipt_owner.get("relative") == RUST_GATE_V5_INNER["receipt"][0]
            and receipt_owner.get("sha256") == RUST_GATE_V5_INNER["receipt"][1]
            and receipt_owner.get("exclusive_creation") is True
            and receipt_owner.get("file_fsync_completed") is True
            and receipt_owner.get("same_inode_readback_verified") is True,
            "the outer failed process does not authenticate the actual inner Rust report")
    require(type(inner) is dict
            and inner.get("schema")
                == "rebar-frozen-python-re-p0-candidate-worker-v3-complete-candidate-evaluation"
            and inner.get("status") == "FAIL"
            and inner.get("candidate_family") == "rust" and inner.get("label") == "phase2-v5"
            and inner.get("source_sha256") == CORE_PINS["phase2_v5_worker"][1]
            and inner.get("protocol_sha256") == CORE_PINS["phase2_v2_protocol"][1]
            and inner.get("document_sha256") == CORE_PINS["phase2_v2_inventory"][1]
            and inner.get("goal_sha256") == CORE_PINS["goal"][1]
            and inner.get("phase1_inventory_sha256") == CORE_PINS["phase1_inventory"][1]
            and inner.get("suite_count") == len(SUITE_IDS)
            and inner.get("case_execution_denominator") == DENOMINATOR
            and inner.get("all_required_suites_executed") is True
            and inner.get("all_required_suites_passed") is False
            and inner.get("completed_candidate_suite_count") == 8
            and inner.get("qualified_candidate_case_executions")
                == RUST_V5_VERIFIED_PASSING_CASES
            and inner.get("candidate_qualified") is False
            and inner.get("complete_owned_source_sha256") == STATIC_OWNERS["rust"],
            "the complete genuine Rust inner candidate evidence was replaced")
    suites, reasons = inner.get("all_suites"), inner.get("all_failure_reasons")
    require(type(suites) is list and len(suites) == len(SUITE_IDS)
            and type(reasons) is list and len(reasons) == len(FAILED_RUST_V5_SUITES),
            "the complete 13 Rust candidate routes or six failing groups were hidden")
    failed: list[str] = []
    verified = 0
    passing = 0
    for row, suite, count in zip(suites, SUITE_IDS, SUITE_COUNTS, strict=True):
        require(type(row) is dict and row.get("suite") == suite
                and row.get("candidate_family") == "rust"
                and row.get("case_execution_denominator") == count
                and type(row.get("actual_process")) is dict,
                "an actual Rust test route was omitted: " + suite)
        if suite in FAILED_RUST_V5_SUITES:
            require(row.get("status") == "FAIL"
                    and "actual_candidate_case_count" not in row
                    and type(row.get("failure")) is dict
                    and row["failure"].get("type") == "CandidateGateError"
                    and type(row["failure"].get("message")) is str
                    and type(row["failure"].get("traceback")) is list
                    and bool(row["failure"]["traceback"]),
                    "never invent the executed count of a failed group: " + suite)
            failed.append(suite)
        else:
            require(row.get("status") == "PASS"
                    and type(row.get("actual_candidate_case_count")) is int
                    and row["actual_candidate_case_count"] == count
                    and row.get("failure") is None,
                    "an actual verified passing group was changed: " + suite)
            verified += count
            passing += 1
    require(tuple(failed) == FAILED_RUST_V5_SUITES and passing == 8
            and verified == RUST_V5_VERIFIED_PASSING_CASES
            and reasons == [row["failure"] for row in suites if row["status"] == "FAIL"],
            "seven passing groups or six real failures were overstated")
    for doc, label in ((outer, "outer"), (inner, "inner"), (published, "worker")):
        for field in ("benchmark_files_read", "clock_samples", "hidden_cases_read",
                      "timing_trials_run"):
            require(type(doc.get(field)) is int and doc[field] == 0,
                    "hidden benchmark access in actual Rust " + label + ": " + field)
        require(doc.get("performance") == "NOT MEASURED"
                and doc.get("final_holdout_authorized") is False
                and doc.get("candidate_qualified_for_hidden_benchmark") is False
                and doc.get("final_winner_selected") is False,
                "a failed Rust " + label + " cannot authorize a holdout or winner")
    for old, expected, version in (
        (outer.get("preserved_v3_actual_failure"), C_GATE_FAILURE, "v3"),
        (outer.get("preserved_v4_actual_failure"), C_GATE_V4_FAILURE, "v4"),
    ):
        require(type(old) is dict and old.get("status") == "PASS"
                and old.get("performance") == "NOT MEASURED"
                and ((old.get("failure_archive_sha256") == expected["archive"][1]
                      and old.get("failure_receipt_sha256") == expected["receipt"][1])
                     if version == "v3" else
                     (old.get("archive_sha256") == expected["archive"][1]
                      and old.get("receipt_sha256") == expected["receipt"][1])),
                "the actual V5 report concealed prior Rust " + version + " failure")
    promotion = outer.get("corrected_promotion_before_full_p0")
    require(type(promotion) is dict and promotion.get("status") == "PASS"
            and promotion.get("family") == "rust"
            and promotion.get("all_native_roles_intent_verified") is True,
            "the actual Rust gate omitted its genuine owned native activation")
    return {
        "gate_status": "FAIL", "failed_before_candidate_execution": False,
        "actual_failed_worker_count": 1, "qualified_candidate_count": 0,
        "qualified_candidate_case_executions": 0,
        "verified_passing_case_executions": verified,
        "completed_passing_suite_count": passing,
        "attempted_suite_route_count": len(suites),
        "all_required_suite_routes_attempted": True,
        "failed_suite_count": len(failed), "failed_suite_ids": failed,
        "failed_suite_case_execution_count": "NOT RECORDED",
        "supplemental_interpreter_check": "NOT RUN",
        "actual_reference_workers_started": 0,
        "full_case_denominator": DENOMINATOR,
        "failed_stage": RUST_GATE_V5_OUTER["failed_stage"],
        "failure_type": "WorkerFailure",
        "failure_message": RUST_GATE_V5_OUTER["failure_message"],
        "candidate_correctness": "FAILED; NOT QUALIFIED",
        "performance": "NOT MEASURED",
        "failure_archive_preserved": True,
        "all_actual_process_streams_preserved": True,
        "subordinate_evidence_owner_count": len(RUST_V5_SUBORDINATE_PINS),
        "outer_and_inner_evidence_owner_count": 4,
    }


Loaded = tuple[dict[str, Any], bytes, bytes]


def validate_snapshot(
    manifest: dict[str, Any],
    source_hash: str,
    go_bridge_sha256: str,
    source_reader: Callable[[str, str], bytes],
    document_loader: Callable[[str, str, bool], Loaded],
    digestor: Callable[[bytes], str] = sha256,
) -> dict[str, Any]:
    validate_manifest(manifest, source_hash, go_bridge_sha256)
    for name, (relative, digest) in CORE_PINS.items():
        if name not in ("phase1_inventory", "phase2_inventory", "phase2_v5_inventory"):
            raw = source_reader(relative, digest)
            require(
                digestor(raw) == digest,
                "a complete frozen chart source was replaced: " + relative,
            )
    phase1, _, _ = document_loader(*CORE_PINS["phase1_inventory"], False)
    phase2, _, _ = document_loader(*CORE_PINS["phase2_inventory"], False)
    phase2_v5, _, _ = document_loader(*CORE_PINS["phase2_v5_inventory"], False)
    validate_baseline(phase1)
    validate_candidate_inventory(phase2)
    validate_candidate_inventory_v5(phase2_v5)
    for family, owners in family_owners(go_bridge_sha256).items():
        for relative, digest in sorted(owners.items()):
            require(
                digestor(source_reader(relative, digest)) == digest,
                "the complete current source closure changed: "
                + family
                + ":"
                + relative,
            )
    builds: dict[str, dict[str, Any]] = {}
    for family in ("rust", "c", "zig"):
        build = BUILD_PINS[family]
        receipt, _, _ = document_loader(*build["receipt"], False)
        report, compressed, expanded = document_loader(*build["archive"], True)
        builds[family] = validate_build(
            family, receipt, report, compressed, expanded, digestor
        )
    c_gate_receipt, _, _ = document_loader(*C_GATE_FAILURE["receipt"], False)
    c_gate_report, c_gate_compressed, c_gate_expanded = document_loader(
        *C_GATE_FAILURE["archive"], True
    )
    historical_c_gate = validate_c_gate_failure(
        c_gate_receipt,
        c_gate_report,
        c_gate_compressed,
        c_gate_expanded,
        digestor,
    )
    historical_zig_build = builds["zig"]
    zig_receipt, _, _ = document_loader(*ZIG_V3_SUCCESS["receipt"], False)
    zig_report, zig_compressed, zig_expanded = document_loader(
        *ZIG_V3_SUCCESS["archive"], True
    )
    builds["zig"] = validate_zig_v3_success(
        zig_receipt, zig_report, zig_compressed, zig_expanded, digestor
    )
    current_c_receipt, _, _ = document_loader(*C_GATE_V4_FAILURE["receipt"], False)
    current_c_report, current_c_compressed, current_c_expanded = document_loader(
        *C_GATE_V4_FAILURE["archive"], True
    )
    historical_c_v4_gate = validate_c_gate_v4_failure(
        current_c_receipt, current_c_report,
        current_c_compressed, current_c_expanded, digestor,
    )
    for relative, digest in C_V5_SUBORDINATE_PINS:
        evidence = source_reader(relative, digest)
        require(digestor(evidence) == digest,
                "an authentic C subordinate report was hidden: " + relative)
    outer_receipt, _, _ = document_loader(*C_GATE_V5_OUTER["receipt"], False)
    outer_report, outer_compressed, outer_expanded = document_loader(
        *C_GATE_V5_OUTER["archive"], True)
    inner_receipt, _, _ = document_loader(*C_GATE_V5_INNER["receipt"], False)
    inner_report, inner_compressed, inner_expanded = document_loader(
        *C_GATE_V5_INNER["archive"], True)
    c_gate = validate_c_gate_v5_failure(
        outer_receipt, outer_report, outer_compressed, outer_expanded,
        inner_receipt, inner_report, inner_compressed, inner_expanded, digestor,
    )
    for relative, digest in RUST_V5_SUBORDINATE_PINS:
        raw = source_reader(relative, digest)
        require(digestor(raw) == digest,
                "an authentic Rust subordinate report was concealed: " + relative)
    rust_outer_receipt, _, _ = document_loader(*RUST_GATE_V5_OUTER["receipt"], False)
    rust_outer, rust_outer_compressed, rust_outer_expanded = document_loader(
        *RUST_GATE_V5_OUTER["archive"], True)
    rust_inner_receipt, _, _ = document_loader(*RUST_GATE_V5_INNER["receipt"], False)
    rust_inner, rust_inner_compressed, rust_inner_expanded = document_loader(
        *RUST_GATE_V5_INNER["archive"], True)
    rust_gate = validate_rust_gate_v5_failure(
        rust_outer_receipt, rust_outer, rust_outer_compressed, rust_outer_expanded,
        rust_inner_receipt, rust_inner, rust_inner_compressed, rust_inner_expanded,
        digestor,
    )
    require(
        historical_zig_build["build_status"] == "FAIL"
        and historical_zig_build["zig_engine_reproduces"] is False
        and historical_c_gate["gate_status"] == "FAIL"
        and historical_c_gate["failed_before_candidate_execution"] is True
        and historical_c_v4_gate["gate_status"] == "FAIL"
        and historical_c_v4_gate["failed_before_candidate_execution"] is False
        and historical_c_v4_gate["actual_failed_worker_count"] == 1,
        "a genuine old Zig or either actual historical C failure was hidden",
    )
    return {
        "python": PYTHON_VERSION,
        "full_case_denominator": DENOMINATOR,
        "suite_count": len(SUITE_IDS),
        "suite_ids": list(SUITE_IDS),
        "baseline_status": "PASS",
        "baseline_passed": DENOMINATOR,
        "qualified_candidate_count": 0,
        "families": list(FAMILY_NAMES),
        "candidate_builds": builds,
        "rust_full_gate": rust_gate,
        "c_full_gate": c_gate,
        "historical_c_full_gate": historical_c_gate,
        "historical_c_v4_full_gate": historical_c_v4_gate,
        "historical_zig_build": historical_zig_build,
        "reproducible_native_family_count": 3,
        "current_rust_compatibility": "FAILED; NOT QUALIFIED",
        "rust_verified_passing_case_executions": RUST_V5_VERIFIED_PASSING_CASES,
        "rust_failed_suite_case_execution_count": "NOT RECORDED",
        "current_c_compatibility": "FAILED; NOT QUALIFIED",
        "c_verified_passing_case_executions": C_V5_VERIFIED_PASSING_CASES,
        "c_failed_suite_case_execution_count": "NOT RECORDED",
        "final_comparison_planned_case_count": 4_194_304,
        "final_comparison_cases_generated": False,
        "fortran_build_status": "SOURCE ONLY; NOT BUILT; NOT TESTED; NOT QUALIFIED",
        "fortran_frozen_v1_independence_audit_coverage": False,
        "fortran_frozen_v5_candidate_gate_coverage": False,
        "fortran_case_executions": 0,
        "cpp_build_status": "NOT MEASURED",
        "go_build_status": "NOT MEASURED",
        "all_current_source_owners_authenticated": True,
        "current_source_owner_count": sum(
            len(owners) for owners in family_owners(go_bridge_sha256).values()
        ),
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "actual_candidate_imports": 0,
        "actual_candidate_processes_started": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance_files_read": 0,
        "hidden_cases_read": 0,
        "final_holdout_authorized": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def escape_xml(value: str) -> str:
    require(type(value) is str, "SVG labels must be exact strings")
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def svg_text(
    x: int, y: int, value: str, css: str, *, anchor: str | None = None
) -> str:
    suffix = "" if anchor is None else ' text-anchor="' + escape_xml(anchor) + '"'
    return (
        '<text x="'
        + str(x)
        + '" y="'
        + str(y)
        + '" class="'
        + escape_xml(css)
        + '"'
        + suffix
        + ">"
        + escape_xml(value)
        + "</text>"
    )


def make_svg(
    snapshot: dict[str, Any], source_hash: str, manifest_hash: str
) -> bytes:
    require(
        snapshot.get("full_case_denominator") == DENOMINATOR
        and snapshot.get("baseline_passed") == DENOMINATOR
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("final_holdout_opened") is False,
        "refusing to draw an invented correctness or speed result",
    )
    valid_hash(source_hash, "SVG renderer")
    valid_hash(manifest_hash, "SVG inputs")
    width, height = 1_600, 1_800
    blue, green, amber, slate = "#0072b2", "#009e73", "#e69f00", "#66768a"
    pale, track, ink = "#f4f7fb", "#dfe7ef", "#16324f"
    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1800" '
        'viewBox="0 0 1600 1800" role="img" '
        'aria-labelledby="current-overview-title current-overview-description">',
        '<title id="current-overview-title">Can a from-scratch engine replace '
        "Python's re, and is it faster?</title>",
        '<desc id="current-overview-description">Python 3.14.6 passes its '
        "complete 31,237-check reference. The current Rust, C, and corrected "
        "Zig engines were each independently built identically twice; this "
        "is build evidence, not a passed compatibility test. Rust has 7,461 "
        "verified passing checks, 2,042 actual matching differences, and five "
        "failed groups. C has 7,197 verified passes, 2,094 matching differences, "
        "and six failed groups. Zig has 3,583 verified passes, 1,764 actual "
        "matching differences, and seven failed groups. Its parent controller "
        "rejected the nested publication field. The separately authenticated "
        "interpreter child really ran 385 calls but failed to restore the "
        "original matcher during cleanup; neither infrastructure failure "
        "adds an invented matching difference. "
        "All failed engines, previous C failures, and Zig build history remain "
        "preserved. "
        "The independently owned C++ engine was source-built twice to "
        "byte-identical bridge bytes, but it has not been activated or tested "
        "for compatibility and is not qualified. Go and Fortran remain "
        "unbuilt and untested. No replacement is qualified. "
        "Candidate speed, memory, confidence intervals, and the final holdout "
        "have not been measured or opened. The 1.5-times marker is a goal, "
        "never a result.</desc>",
        "<style>"
        "text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"
        "'Segoe UI',sans-serif}"
        ".title{font-size:38px;font-weight:780;fill:#16324f}"
        ".subtitle{font-size:19px;fill:#46586e}"
        ".section{font-size:27px;font-weight:740;fill:#16324f}"
        ".body{font-size:17px;fill:#34465b}"
        ".label{font-size:19px;font-weight:700;fill:#16324f}"
        ".small{font-size:15px;fill:#52657a}"
        ".metric{font-size:34px;font-weight:790;fill:#16324f}"
        ".metriclabel{font-size:15px;fill:#52657a}"
        ".pass{font-size:16px;font-weight:760;fill:#00794c}"
        ".pending{font-size:16px;font-weight:720;fill:#52657a}"
        ".warning{font-size:16px;font-weight:760;fill:#956200}"
        ".foot{font-size:13px;fill:#52657a}"
        "</style>",
        '<rect width="1600" height="1800" rx="24" fill="' + pale + '"/>',
        svg_text(64, 77, "Can these engines replace Python re?", "title"),
        svg_text(
            66, 112,
            "Current source-built evidence against Python 3.14.6"
            "  |  no outside regex engines",
            "subtitle",
        ),
    ]
    cards = [
        ("31,237", "full Python compatibility checks"),
        ("6", "from-scratch candidate families"),
        ("4", "families built identically twice"),
        ("0", "qualified or speed-tested replacements"),
    ]
    for index, (number, label) in enumerate(cards):
        x = 64 + index * 386
        pieces.extend([
            '<rect x="' + str(x) + '" y="141" width="364" height="111" '
            'rx="15" fill="#ffffff" stroke="#d8e3ed"/>',
            svg_text(x + 20, 192, number, "metric"),
            svg_text(x + 20, 226, label, "metriclabel"),
        ])
    pieces.extend([
        '<rect x="64" y="278" width="1472" height="840" rx="18" '
        'fill="#ffffff" stroke="#d8e3ed"/>',
        svg_text(
            89, 322,
            "1. Does it work exactly like Python?", "section",
        ),
        svg_text(
            91, 355,
            "The same complete 31,237-check test applies to every engine."
            " Grey means not tested, never zero passes.",
            "body",
        ),
    ])
    rows = (
        (
            "python", "Python re", "31,237 / 31,237",
            "Reference implementation; complete frozen test passed",
            "pass",
        ),
        (
            "rust", "Rust", "FAILED; NOT QUALIFIED",
            "7,461 / 31,237 checked successfully; five test groups failed; 2,042 mismatches",
            "warning",
        ),
        (
            "c", "C", "FAILED; NOT QUALIFIED",
            "7,197 / 31,237 checked successfully; six test groups failed; 2,094 mismatches",
            "warning",
        ),
        (
            "zig", "Zig", "FAILED; NOT QUALIFIED",
            "3,583 / 31,237 verified; seven failed groups; 1,764 matching differences",
            "warning",
        ),
        (
            "cpp", "C++", "BUILT; MATCHING NOT MEASURED",
            "Two reproducible source builds; not activated, tested, or qualified",
            "pending",
        ),
        (
            "go", "Go", "NOT MEASURED",
            "Independent source checked; candidate not yet built",
            "pending",
        ),
        (
            "fortran", "Fortran",
            "SOURCE ONLY; NOT BUILT; NOT TESTED; NOT QUALIFIED",
            "Independent Fortran engine and Python bridge; no frozen-gate coverage",
            "pending",
        ),
    )
    for index, (family, title, outcome, detail, outcome_style) in enumerate(rows):
        y = 392 + 96 * index
        accent = (
            green if family == "python"
            else amber if family in ("c", "rust", "zig")
            else blue
        )
        pieces.extend([
            '<rect x="90" y="' + str(y) + '" width="1420" height="79" '
            'rx="11" fill="#f8fafd" stroke="#e3eaf1"/>',
            '<rect x="90" y="' + str(y) + '" width="7" height="79" '
            'rx="3" fill="' + accent + '"/>',
            svg_text(111, y + 31, title, "label"),
            svg_text(
                1_485,
                y + 31,
                outcome,
                outcome_style,
                anchor="end",
            ),
            '<rect x="282" y="' + str(y + 44) + '" width="895" height="12" '
            'rx="6" fill="' + track + '"/>',
            svg_text(282, y + 35, detail, "small"),
        ])
        if family == "python":
            pieces.append(
                '<rect x="282" y="' + str(y + 44)
                + '" width="895" height="12" rx="6" fill="' + green
                + '"><title>Python reference: 31,237 of 31,237 complete '
                "compatibility checks passed</title></rect>"
            )
        elif family in ("c", "rust", "zig"):
            passing = (
                C_V5_VERIFIED_PASSING_CASES if family == "c"
                else RUST_V5_VERIFIED_PASSING_CASES if family == "rust"
                else ZIG_V6_PASSING_CASES
            )
            failed = "six" if family == "c" else "five" if family == "rust" else "seven"
            completed = 895 * passing // DENOMINATOR
            pieces.append(
                '<rect x="282" y="' + str(y + 44)
                + '" width="' + str(completed) + '" height="12" rx="6" fill="'
                + amber + '"><title>' + escape_xml(DISPLAY_NAMES[family])
                + ": exactly " + format(passing, ",")
                + " verified passing checks; " + failed
                + (
                    " test groups failed; six failed matching-group case counts "
                    "were recorded; 1,764 actual matching differences; the "
                    "parent rejected a nested publication-field mismatch; "
                    "a separately signed child ran 385 real interpreter "
                    "calls before matcher-restoration cleanup failed"
                    if family == "zig"
                    else " test groups failed; failed-group executed case "
                         "counts were not recorded"
                )
                + "</title></rect>"
            )
        elif family == "cpp":
            pieces.append(
                "<title>C++: two independently source-built, byte-identical "
                "bridge artifacts; four first-party sources; ten authenticated "
                "compiler and ELF checks; matching NOT MEASURED; not activated; "
                "NOT QUALIFIED; no speed or hidden benchmark</title>"
            )
        else:
            pieces.append(
                '<title>'
                + escape_xml(
                    title + ": all 31,237 current-build checks are NOT MEASURED"
                )
                + "</title>"
            )
    pieces.extend([
        svg_text(
            92, 1065,
            "Matching differences: Rust 2,042; C 2,094; Zig 1,764;"
            " both earlier C failures are preserved.",
            "small",
        ),
        svg_text(
            92, 1086,
            "Zig: identical engine and bridge; parent receipt-field rejection;"
            " signed child ran 385 real interpreter calls; cleanup failed.",
            "small",
        ),
        svg_text(
            92, 1108,
            "Fortran is source only: outside the frozen independence audit V1 and"
            " correctness gate; the newer V2 source-only audit includes it.",
            "small",
        ),
        '<rect x="64" y="1145" width="1472" height="548" rx="18" '
        'fill="#ffffff" stroke="#d8e3ed"/>',
        svg_text(89, 1190, "2. Is it faster than Python?", "section"),
        svg_text(
            91, 1224,
            "Speed has not been measured. There are no candidate speed bars,"
            " rankings, or hidden benchmark results.",
            "body",
        ),
    ])
    for index, family in enumerate(FAMILY_NAMES):
        y = 1_265 + index * 43
        value = (
            "REFERENCE ONLY - NOT TIMED"
            if family == "python"
            else "NOT MEASURED"
        )
        style = "small" if family == "python" else "pending"
        pieces.extend([
            svg_text(109, y + 17, DISPLAY_NAMES[family], "label"),
            '<line x1="304" y1="' + str(y + 11) + '" x2="1170" y2="'
            + str(y + 11)
            + '" stroke="#edf1f5" stroke-width="2"/>',
            svg_text(1_480, y + 17, value, style, anchor="end"),
        ])
    pieces.extend([
        '<line x1="358" y1="1584" x2="1162" y2="1584" '
        'stroke="#98a8b9" stroke-width="2"/>',
        '<line x1="626" y1="1570" x2="626" y2="1598" '
        'stroke="' + blue + '" stroke-width="3"/>',
        '<line x1="1028" y1="1561" x2="1028" y2="1598" '
        'stroke="' + amber + '" stroke-width="3" stroke-dasharray="6 5"/>',
        svg_text(
            626, 1621, "1.0x reference (not timed)", "small", anchor="middle"
        ),
        svg_text(1_028, 1621, "1.5x goal", "warning", anchor="middle"),
        svg_text(
            91, 1659,
            "4,194,304 final examples: NOT GENERATED and NOT OPENED."
            " 1.5x is a future goal, not an observation; speed: NOT MEASURED.",
            "small",
        ),
        svg_text(
            66, 1730,
            "Generated only from complete, hash-pinned current source"
            " and published build evidence.",
            "foot",
        ),
        svg_text(
            66, 1754,
            "Input SHA-256: " + manifest_hash,
            "foot",
        ),
        svg_text(
            66, 1776,
            "Renderer SHA-256: " + source_hash,
            "foot",
        ),
        "</svg>\n",
    ])
    raw = "\n".join(pieces).encode("utf-8")
    require(
        0 < len(raw) <= MAX_GRAPH_BYTES,
        "the deterministic current-build graph exceeded its safe bound",
    )
    return raw


def graph_documents(
    manifest: dict[str, Any],
    source_hash: str,
    manifest_hash: str,
    snapshot: dict[str, Any],
) -> tuple[bytes, bytes]:
    require(
        sha256(canonical(manifest)) == manifest_hash,
        "the exact visible chart manifest does not match its frozen bytes",
    )
    picture = make_svg(snapshot, source_hash, manifest_hash)
    summary = {
        "schema": SCHEMA + "-summary",
        "status": "PASS",
        "python": PYTHON_VERSION,
        "source": pin(SOURCE_RELATIVE, source_hash),
        "inputs": pin(INPUT_RELATIVE, manifest_hash),
        "svg": pin(SVG_RELATIVE, sha256(picture)),
        "frozen_inputs": copy.deepcopy(manifest["frozen_inputs"]),
        "families": copy.deepcopy(manifest["families"]),
        "snapshot": copy.deepcopy(snapshot),
        "full_case_denominator": DENOMINATOR,
        "suite_count": len(SUITE_IDS),
        "speed_target": copy.deepcopy(manifest["speed_target"]),
        "actual_candidate_imports": 0,
        "actual_candidate_processes_started": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "final_holdout_opened": False,
        "winner_selected": False,
    }
    return picture, canonical(summary)


def load_real_document(relative: str, expected: str, compressed: bool) -> Loaded:
    stored = read_checked(
        relative,
        expected,
        MAX_ARCHIVE_BYTES if compressed else MAX_DOCUMENT_BYTES,
    )
    specialist_archive = compressed and any(
        relative == item["archive"][0] and expected == item["archive"][1]
        for item in ZIG_V6_SPECIALISTS
    )
    maximum = MAX_SPECIALIST_DOCUMENT_BYTES if specialist_archive else MAX_DOCUMENT_BYTES
    expanded = bounded_gzip(stored, maximum) if compressed else stored
    exact_pretty_printed_v3 = (
        compressed is False
        and any(relative == CORE_PINS[key][0] and expected == CORE_PINS[key][1]
                for key in ("phase2_inventory", "phase2_v5_inventory",
                            "phase2_v6_inventory", "independence_v2_inventory",
                            "native_build_v4_inventory"))
    )
    return (
        decode_document(
            expanded,
            relative,
            require_canonical=not exact_pretty_printed_v3,
            maximum=maximum,
        ),
        stored,
        expanded,
    )


def read_real_source(relative: str, expected: str) -> bytes:
    return read_checked(relative, expected, MAX_SOURCE_BYTES)


def graph_directory(descriptor: int, expected: tuple[int, int]) -> None:
    actual = os.fstat(descriptor)
    require(
        stat.S_ISDIR(actual.st_mode)
        and (actual.st_dev, actual.st_ino) == expected,
        "the exact generated graph directory was replaced",
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_DIRECTORY", 0)
    )
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), flags)
        opened.append(current)
        for name in ("docs", "evidence"):
            current = os.open(name, flags, dir_fd=current)
            opened.append(current)
        named = os.fstat(current)
        require(
            (named.st_dev, named.st_ino) == expected,
            "the generated graph directory no longer names its authenticated inode",
        )
    finally:
        for item in reversed(opened):
            os.close(item)


def read_output(directory: int, name: str) -> bytes | None:
    approved = {
        path_parts(INPUT_RELATIVE)[-1],
        path_parts(SUMMARY_RELATIVE)[-1],
        path_parts(SVG_RELATIVE)[-1],
    }
    require(name in approved, "only three literal generated outputs are allowed")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(name, flags, dir_fd=directory)
    except FileNotFoundError:
        return None
    try:
        before = os.fstat(descriptor)
        named = os.stat(name, dir_fd=directory, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and stat.S_ISREG(named.st_mode)
            and (before.st_dev, before.st_ino)
            == (named.st_dev, named.st_ino)
            and 0 < before.st_size <= MAX_GRAPH_BYTES,
            "refuse a linked, nonregular, empty, or oversized chart output",
        )
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(bool(chunk), "an existing chart output was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(
            os.read(descriptor, 1) == b"",
            "an existing chart output has concealed trailing bytes",
        )
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size),
            "an existing chart output changed during verification",
        )
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def publish_output(
    directory: int,
    identity: tuple[int, int],
    name: str,
    content: bytes,
    verify_only: bool,
) -> None:
    graph_directory(directory, identity)
    previous = read_output(directory, name)
    if previous is not None:
        require(
            previous == content,
            "refuse to overwrite a different existing current-build chart",
        )
        return
    require(not verify_only, "a required deterministic chart output is missing")
    temporary = (
        ".rebar-current-overview-v7-"
        + name
        + "-"
        + sha256(content)[:24]
    )
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
    linked = False
    owned: tuple[int, int] | None = None
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode), "chart temporary is not regular")
        owned = (before.st_dev, before.st_ino)
        cursor = 0
        while cursor < len(content):
            written = os.write(descriptor, content[cursor:])
            require(type(written) is int and written > 0, "chart output was truncated")
            cursor += written
        os.fsync(descriptor)
        graph_directory(directory, identity)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require(
            (named.st_dev, named.st_ino) == owned,
            "the owned generated-chart temporary was replaced",
        )
        require(
            read_output(directory, name) is None,
            "refusing to replace an independently created chart output",
        )
        os.link(
            temporary,
            name,
            src_dir_fd=directory,
            dst_dir_fd=directory,
            follow_symlinks=False,
        )
        linked = True
        os.fsync(directory)
        require(
            read_output(directory, name) == content,
            "the generated graph failed complete same-byte readback",
        )
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require(
            (named.st_dev, named.st_ino) == owned,
            "refusing to remove an unowned generated-chart temporary",
        )
        os.unlink(temporary, dir_fd=directory)
        os.fsync(directory)
        graph_directory(directory, identity)
    except BaseException:
        if not linked and owned is not None:
            try:
                named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
                if (named.st_dev, named.st_ino) == owned:
                    os.unlink(temporary, dir_fd=directory)
                    os.fsync(directory)
            except (OSError, OverviewError):
                pass
        raise
    finally:
        os.close(descriptor)


def render(
    source_hash: str,
    go_bridge_sha256: str,
    expected_manifest_hash: str | None,
    verify_only: bool,
) -> dict[str, Any]:
    verify_runtime()
    source_hash = valid_hash(source_hash, "current-overview source")
    go_bridge_sha256 = valid_hash(go_bridge_sha256, "committed Go bridge")
    read_checked(SOURCE_RELATIVE, source_hash, MAX_SOURCE_BYTES)
    manifest = frozen_manifest(source_hash, go_bridge_sha256)
    manifest_raw = canonical(manifest)
    manifest_hash = sha256(manifest_raw)
    if expected_manifest_hash is not None:
        require(
            valid_hash(expected_manifest_hash, "frozen generated input manifest")
            == manifest_hash,
            "the expected deterministic chart manifest was replaced",
        )
    snapshot = validate_snapshot(
        manifest,
        source_hash,
        go_bridge_sha256,
        read_real_source,
        load_real_document,
    )
    svg, summary = graph_documents(manifest, source_hash, manifest_hash, snapshot)
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_DIRECTORY", 0)
    )
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), flags)
        opened.append(current)
        for part in ("docs", "evidence"):
            current = os.open(part, flags, dir_fd=current)
            opened.append(current)
        information = os.fstat(current)
        require(
            stat.S_ISDIR(information.st_mode),
            "the generated current chart directory is not regular",
        )
        identity = (information.st_dev, information.st_ino)
        for relative, raw in (
            (INPUT_RELATIVE, manifest_raw),
            (SVG_RELATIVE, svg),
            (SUMMARY_RELATIVE, summary),
        ):
            require(
                path_parts(relative)[:-1] == ("docs", "evidence"),
                "a deterministic chart output escaped its fixed folder",
            )
            publish_output(
                current,
                identity,
                path_parts(relative)[-1],
                raw,
                verify_only,
            )
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)
    verify_runtime()
    return {
        "schema": SCHEMA + ("-verified" if verify_only else "-rendered"),
        "status": "PASS",
        "source_sha256": source_hash,
        "inputs_relative": INPUT_RELATIVE,
        "inputs_sha256": manifest_hash,
        "svg_relative": SVG_RELATIVE,
        "svg_sha256": sha256(svg),
        "summary_relative": SUMMARY_RELATIVE,
        "summary_sha256": sha256(summary),
        "full_case_denominator": DENOMINATOR,
        "suite_count": len(SUITE_IDS),
        "families": list(FAMILY_NAMES),
        "current_source_owner_count": snapshot["current_source_owner_count"],
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "actual_candidate_imports": 0,
        "actual_candidate_processes_started": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance_files_read": 0,
        "hidden_cases_read": 0,
        "final_holdout_opened": False,
        "winner_selected": False,
        "outputs_written": not verify_only,
    }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        name: 0
        for name in (
            "reads", "writes", "imports", "workers", "threads", "clocks",
            "garbage_collection",
        )
    }
    replacements: list[tuple[Any, str, Any]] = []

    def reject_effect(name: str) -> Callable[..., Any]:
        def rejected(*_: Any, **__: Any) -> Any:
            effects[name] += 1
            raise SourceOnlyError("synthetic graph controls cannot perform " + name)
        return rejected

    def replace(module: Any, attribute: str, value: Any) -> None:
        original = getattr(module, attribute, None)
        if original is not None:
            replacements.append((module, attribute, original))
            setattr(module, attribute, value)

    try:
        for module, attribute in (
            (builtins, "open"),
            (io, "open"),
            (os, "open"),
            (os, "read"),
            (os, "stat"),
            (os, "lstat"),
            (Path, "open"),
            (Path, "read_bytes"),
            (Path, "read_text"),
        ):
            replace(module, attribute, reject_effect("reads"))
        for module, attribute in (
            (os, "write"),
            (os, "unlink"),
            (os, "remove"),
            (os, "rename"),
            (os, "replace"),
            (os, "mkdir"),
            (os, "rmdir"),
            (os, "fsync"),
            (os, "link"),
            (Path, "write_bytes"),
            (Path, "write_text"),
            (Path, "unlink"),
            (Path, "mkdir"),
        ):
            replace(module, attribute, reject_effect("writes"))
        replace(builtins, "__import__", reject_effect("imports"))
        replace(importlib, "import_module", reject_effect("imports"))
        for attribute in ("Popen", "run", "call", "check_call", "check_output"):
            replace(subprocess, attribute, reject_effect("workers"))
        replace(threading.Thread, "start", reject_effect("threads"))
        for attribute in (
            "time",
            "time_ns",
            "monotonic",
            "monotonic_ns",
            "perf_counter",
            "perf_counter_ns",
            "process_time",
            "process_time_ns",
        ):
            replace(time, attribute, reject_effect("clocks"))
        replace(gc, "collect", reject_effect("garbage_collection"))
        yield effects
    finally:
        for module, attribute, original in reversed(replacements):
            setattr(module, attribute, original)


def synthetic_baseline() -> dict[str, Any]:
    candidates = {name: "NOT MEASURED" for name in ("c", "rust", "zig")}
    return {
        "schema": "rebar-cpython-re-p0-completeness-v1",
        "version": 1,
        "runtime": {"python_version": PYTHON_VERSION},
        "goal": {
            "path": CORE_PINS["goal"][0],
            "sha256": CORE_PINS["goal"][1],
        },
        "phase_gate": {
            "status": "PASS",
            "all_obligations_mapped": True,
            "blockers": [],
            "candidate_evaluation_authorized": False,
            "final_holdout_authorized": False,
        },
        "denominator": {
            "available_frozen_vector_case_executions": DENOMINATOR,
            "final_required_case_execution_denominator": DENOMINATOR,
            "frozen_planned_case_execution_denominator": DENOMINATOR,
            "counted_suite_ids": list(SUITE_IDS),
            "full_resource_original_versions_double_counted": False,
            "historical_subinterpreter_versions_double_counted": False,
            "public_original_skip_cases_outside_runnable_denominator": 1,
            "private_upstream_methods_outside_public_denominator": 13,
        },
        "candidate_results": candidates,
        "suites": [
            {
                "id": name,
                "case_execution_count": count,
                "baseline": {"status": "PASS"},
                "candidate_results": dict(candidates),
                "performance": "NOT MEASURED",
            }
            for name, count in zip(SUITE_IDS, SUITE_COUNTS, strict=True)
        ],
    }


def synthetic_inventory() -> dict[str, Any]:
    return {
        "schema": "rebar-frozen-python-re-p0-candidate-protocol-v3",
        "version": 3,
        "status": "SOURCE FROZEN; CANDIDATES NOT RUN",
        "phase": "CANDIDATES",
        "goal_sha256": CORE_PINS["goal"][1],
        "candidate_families": ["rust", "c", "zig"],
        "candidate_results": "NOT MEASURED",
        "phase1": {
            "inventory_path": CORE_PINS["phase1_inventory"][0],
            "inventory_sha256": CORE_PINS["phase1_inventory"][1],
            "verifier_path": CORE_PINS["phase1_verifier"][0],
            "verifier_sha256": CORE_PINS["phase1_verifier"][1],
            "python_path": PINNED_PYTHON,
            "suite_count": len(SUITE_IDS),
            "case_execution_denominator": DENOMINATOR,
            "public_obligation_count": 73,
            "named_private_waiver_count": 13,
            "runnable_original_public_methods": 151,
            "genuine_original_debug_skips": 1,
        },
        "native_source_build_v2": {
            "source_path": CORE_PINS["native_build_runner"][0],
            "source_sha256": CORE_PINS["native_build_runner"][1],
            "protocol_path": CORE_PINS["native_build_protocol"][0],
            "protocol_sha256": CORE_PINS["native_build_protocol"][1],
            "independent_fresh_phase_count": 2,
            "version_one_artifact_authorized": False,
        },
        "boundaries": {
            "stdlib_candidate_delegation_allowed": False,
            "cross_candidate_delegation_allowed": False,
            "external_regex_package_allowed": False,
            "timing_allowed": False,
            "hidden_case_access_allowed": False,
            "final_holdout_authorized": False,
            "final_holdout_opened": False,
            "final_winner_selected": False,
            "performance": "NOT MEASURED",
        },
    }


def synthetic_inventory_v5() -> dict[str, Any]:
    value = copy.deepcopy(synthetic_inventory())
    value.update({
        "schema": "rebar-frozen-python-re-p0-candidate-protocol-v5",
        "version": 5,
        "status": "SOURCE FROZEN; V5 CANDIDATES NOT RUN",
        "suites": [{"id": name, "case_count": count}
                   for name, count in zip(SUITE_IDS, SUITE_COUNTS, strict=True)],
        "corrected_full_case_worker_v3": {
            "source_path": CORE_PINS["phase2_v5_worker"][0],
            "source_sha256_mode": "mandatory-exact-caller-pinned-published-source-bytes",
            "preserved_original_v2_protocol_sha256": CORE_PINS["phase2_v2_protocol"][1],
            "preserved_original_v2_inventory_sha256": CORE_PINS["phase2_v2_inventory"][1],
            "complete_original_suite_count": len(SUITE_IDS),
            "complete_original_case_execution_denominator": DENOMINATOR,
            "v1_validated_document_exact_dictionary_required": True,
            "v1_validated_document_canonical_equality_required": True,
            "strict_literal_boolean_contract_weakened": False,
            "actual_worker_executes_original_routes": True,
        },
        "runner": {
            "path": CORE_PINS["phase2_v5_runner"][0],
            "source_sha256_mode": "mandatory-exact-caller-pinned-published-source-bytes",
        },
        "historical_v3_live_owner_failure": {
            "failure_archive_sha256": C_GATE_FAILURE["archive"][1],
            "failure_receipt_sha256": C_GATE_FAILURE["receipt"][1],
            "qualified_candidate_case_executions": 0,
        },
        "historical_v4_dict_contract_failure": {
            "failure_archive_sha256": C_GATE_V4_FAILURE["archive"][1],
            "failure_receipt_sha256": C_GATE_V4_FAILURE["receipt"][1],
            "qualified_candidate_case_executions": 0,
        },
    })
    value["boundaries"]["original_guard_root_rebinding_allowed"] = False
    return value


def synthetic_phase(family: str, name: str) -> dict[str, Any]:
    build = BUILD_PINS[family]
    phase: dict[str, Any] = {
        "name": name,
        "fresh_source_directory": "<FRESH_PRIVATE_TMP>/" + name + "/source",
        "fresh_native_directory": "<FRESH_PRIVATE_TMP>/" + name + "/native",
        "copied_source_owners": {
            relative: {
                "path":
                    "<FRESH_PRIVATE_TMP>/" + name + "/source/" + relative,
                "sha256": digest,
                "bytes": len(relative) + 1,
                "exclusive_creation": True,
                "file_fsync_completed": False,
                "same_inode_readback_verified": True,
                "write_calls": 1,
            }
            for relative, digest in STATIC_OWNERS[family].items()
        },
        "native_outputs": {},
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "timing_trials_run": 0,
        "hidden_cases_read": 0,
    }
    for role in (("extension",) if family == "c" else ("bridge", "engine")):
        key = (
            "engine_reference_a"
            if family == "zig" and role == "engine" and name == "reference-a"
            else "engine_reference_b"
            if family == "zig" and role == "engine"
            else role
        )
        digest, size = build["outputs"][key]
        phase["native_outputs"][role] = {
            "family": family,
            "role": role,
            "file_name": "synthetic-" + family + "-" + role + ".so",
            "path":
                "<FRESH_PRIVATE_TMP>/" + name + "/native/"
                + "synthetic-" + family + "-" + role + ".so",
            "sha256": digest,
            "size_bytes": size,
            "candidate_imported": False,
            "prebuilt_binary_read": False,
            "elf": {
                "external_regex_dependency_count": 0,
                "cross_family_dependency_count": 0,
            },
        }
    return phase


def synthetic_build(family: str) -> tuple[dict[str, Any], dict[str, Any]]:
    build = BUILD_PINS[family]
    archive_publication = {
        "exclusive_creation": True,
        "file_fsync_completed": True,
        "same_inode_readback_verified": True,
        "bytes": build["archive_bytes"],
        "sha256": build["archive"][1],
        "path": str(ROOT / build["archive"][0]),
        "write_calls": 1,
    }
    receipt: dict[str, Any] = {
        "schema":
            "rebar-phase2-independent-native-source-build-v2-durable-publication-receipt",
        "status": "PASS",
        "family": family,
        "label": "phase2-v2",
        "build_status": build["build_status"],
        "owned_source_sha256": dict(STATIC_OWNERS[family]),
        "source_sha256": CORE_PINS["native_build_runner"][1],
        "protocol_sha256": CORE_PINS["native_build_protocol"][1],
        "phase1_manifest_sha256": CORE_PINS["phase1_inventory"][1],
        "archive_relative": build["archive"][0],
        "archive_sha256": build["archive"][1],
        "archive_bytes": build["archive_bytes"],
        "uncompressed_sha256": build["uncompressed_sha256"],
        "uncompressed_bytes": build["uncompressed_bytes"],
        "archive_publication": archive_publication,
        "archive_directory_fsync": {"completed": True},
        "receipt_self_publication": "NOT CLAIMED",
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "winner_selected": False,
    }
    for field in ZERO_FIELDS:
        receipt[field] = 0
    report: dict[str, Any] = {
        "schema": "rebar-phase2-independent-native-source-build-v2",
        "status": build["build_status"],
        "family": family,
        "label": "phase2-v2",
        "source_sha256": CORE_PINS["native_build_runner"][1],
        "protocol_sha256": CORE_PINS["native_build_protocol"][1],
        "owned_source_sha256": dict(STATIC_OWNERS[family]),
        "fresh_private_root": "<FRESH_PRIVATE_TMP>",
        "network_requests": 0,
        "reference_processes_started": 0,
        "owned_source_before": {
            relative: {
                "path": str(ROOT / relative),
                "sha256": digest,
                "device": 71,
                "inode": 1_000 + index,
                "size_bytes": len(relative) + 1,
            }
            for index, (relative, digest) in enumerate(
                STATIC_OWNERS[family].items()
            )
        },
        "phase1": {
            "status": "PASS",
            "suite_count": len(SUITE_IDS),
            "case_execution_count": DENOMINATOR,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "final_holdout_authorized": False,
        },
        "source_independence_audit": {
            "source_owner_count": len(STATIC_OWNERS[family]),
            "cross_family_dependency_count": 0,
            "external_regex_package_count": 0,
        },
        "build_phases": [
            synthetic_phase(family, "reference-a"),
            synthetic_phase(family, "reference-b"),
        ],
        "processes": [
            {
                "name": family + "-synthetic-process-" + str(index),
                "pid": 100 + index,
                "argv": ["/synthetic/owned-compiler", "--synthetic-check"],
                "environment": {},
                "exit_status": 0,
                "shell": False,
                "stdout_base64": "",
                "stdout_bytes": 0,
                "stdout_sha256":
                    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "stderr_base64": "",
                "stderr_bytes": 0,
                "stderr_sha256":
                    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            }
            for index in range(build["process_count"])
        ],
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "winner_selected": False,
    }
    for field in ZERO_FIELDS:
        report[field] = 0
    report["owned_source_after"] = copy.deepcopy(report["owned_source_before"])
    if family == "rust":
        report["source_independence_audit"]["cargo_dependency_closure"] = {
            "external_package_count": 0,
            "registry_count": 0,
            "package_count": 1,
            "locked": True,
            "offline": True,
            "build_script_count": 0,
        }
    if family == "zig":
        report["reproducibility"] = None
        report["error"] = {
            "type": "BuildError",
            "message": "two independent native builds are not byte-for-byte reproducible",
        }
    else:
        report["error"] = None
        report["reproducibility"] = {
            "byte_identical": True,
            "independent_fresh_phase_count": 2,
            "prebuilt_binary_count": 0,
            "native_outputs": {
                role: {
                    "sha256": digest,
                    "size_bytes": size,
                    "reproduced_in_two_fresh_directories": True,
                }
                for role, (digest, size) in build["outputs"].items()
            },
        }
    return receipt, report


def synthetic_c_gate_failure() -> tuple[dict[str, Any], dict[str, Any]]:
    publication = {
        "bytes": C_GATE_FAILURE["archive_bytes"],
        "device": 71,
        "exclusive_creation": True,
        "file_fsync_completed": True,
        "inode": 9_001,
        "relative": C_GATE_FAILURE["archive"][0],
        "same_inode_readback_verified": True,
        "sha256": C_GATE_FAILURE["archive"][1],
    }
    receipt: dict[str, Any] = {
        "schema": "rebar-frozen-python-re-p0-candidate-v3-durable-publication-receipt",
        "status": "PASS",
        "candidate_status": "FAIL",
        "candidate_family": "c",
        "label": "phase2-v3",
        "source_sha256": CORE_PINS["phase2_runner"][1],
        "protocol_sha256": CORE_PINS["phase2_protocol"][1],
        "document_sha256": CORE_PINS["phase2_inventory"][1],
        "all_actual_process_streams_preserved": True,
        "failure_preserved": True,
        "archive_directory_fsync_completed": True,
        "archive": publication,
        "uncompressed_bytes": C_GATE_FAILURE["uncompressed_bytes"],
        "uncompressed_sha256": C_GATE_FAILURE["uncompressed_sha256"],
        "candidate_qualified_for_hidden_benchmark": False,
        "final_holdout_authorized": False,
        "final_winner_selected": False,
        "performance": "NOT MEASURED",
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "timing_trials_run": 0,
    }
    report: dict[str, Any] = {
        "schema": "rebar-frozen-python-re-p0-candidate-v3-actual-complete-candidate",
        "status": "FAIL",
        "candidate_family": "c",
        "label": "phase2-v3",
        "source_sha256": CORE_PINS["phase2_runner"][1],
        "protocol_sha256": CORE_PINS["phase2_protocol"][1],
        "document_sha256": CORE_PINS["phase2_inventory"][1],
        "goal_sha256": CORE_PINS["goal"][1],
        "phase1_inventory_sha256": CORE_PINS["phase1_inventory"][1],
        "case_execution_denominator": DENOMINATOR,
        "suite_count": len(SUITE_IDS),
        "qualified_candidate_case_executions": 0,
        "supplemental_subinterpreter_case_count": 0,
        "supplemental_cases_added_to_original_denominator": False,
        "actual_reference_workers_started": 0,
        "failed_stage": C_GATE_FAILURE["failed_stage"],
        "failure": {
            "type": "GateError",
            "message": C_GATE_FAILURE["failure_message"],
            "traceback": ["synthetic exclusively preserved preflight traceback"],
        },
        "candidate_qualified": False,
        "candidate_qualified_for_hidden_benchmark": False,
        "final_holdout_authorized": False,
        "final_winner_selected": False,
        "performance": "NOT MEASURED",
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "timing_trials_run": 0,
    }
    return receipt, report



def synthetic_c_gate_v4_failure() -> tuple[dict[str, Any], dict[str, Any]]:
    receipt, report = synthetic_c_gate_failure()
    expected = C_GATE_V4_FAILURE
    receipt.update({
        "schema": "rebar-frozen-python-re-p0-candidate-v4-durable-publication-receipt",
        "label": "phase2-v4",
        "source_sha256": CORE_PINS["phase2_v4_runner"][1],
        "protocol_sha256": CORE_PINS["phase2_v4_protocol"][1],
        "document_sha256": CORE_PINS["phase2_v4_inventory"][1],
        "uncompressed_bytes": expected["uncompressed_bytes"],
        "uncompressed_sha256": expected["uncompressed_sha256"],
    })
    receipt["archive"].update({
        "bytes": expected["archive_bytes"],
        "relative": expected["archive"][0],
        "sha256": expected["archive"][1],
    })
    report.update({
        "schema": "rebar-frozen-python-re-p0-candidate-v4-actual-complete-candidate",
        "label": "phase2-v4",
        "source_sha256": CORE_PINS["phase2_v4_runner"][1],
        "protocol_sha256": CORE_PINS["phase2_v4_protocol"][1],
        "document_sha256": CORE_PINS["phase2_v4_inventory"][1],
        "failed_stage": expected["failed_stage"],
        "failure": {
            "type": "WorkerFailure",
            "message": expected["failure_message"],
            "traceback": ["synthetic genuine complete worker-failure traceback"],
        },
        "failed_worker_process": {
            "pid": 101,
            "returncode": 1,
            "timed_out": False,
            "signal": None,
        },
        "corrected_promotion_before_full_p0": {
            "status": "PASS",
            "family": "c",
            "all_native_roles_intent_verified": True,
        },
        "preserved_v3_actual_failure": {
            "schema":
                "rebar-frozen-python-re-p0-candidate-v4-independently-verified-preserved-v3-failure",
            "status": "PASS",
            "failure_preserved": True,
            "failure_archive_sha256": C_GATE_FAILURE["archive"][1],
            "failure_receipt_sha256": C_GATE_FAILURE["receipt"][1],
            "failure_uncompressed_sha256": C_GATE_FAILURE["uncompressed_sha256"],
            "actual_candidate_cases_executed": 0,
            "candidate_was_qualified": False,
            "holdout_opened": False,
            "performance": "NOT MEASURED",
            "version_three_document_sha256": CORE_PINS["phase2_inventory"][1],
            "version_three_protocol_sha256": CORE_PINS["phase2_protocol"][1],
            "version_three_source_sha256": CORE_PINS["phase2_runner"][1],
        },
    })
    return receipt, report


def synthetic_c_gate_v5_failure() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]
]:
    outer_receipt, outer = synthetic_c_gate_v4_failure()
    inner_receipt = copy.deepcopy(outer_receipt)
    inner_receipt.pop("all_actual_process_streams_preserved")
    for receipt, expected, source_key, protocol_key, inventory_key, schema in (
        (outer_receipt, C_GATE_V5_OUTER, "phase2_v5_runner", "phase2_v5_protocol",
         "phase2_v5_inventory",
         "rebar-frozen-python-re-p0-candidate-v5-durable-publication-receipt"),
        (inner_receipt, C_GATE_V5_INNER, "phase2_v5_worker", "phase2_v2_protocol",
         "phase2_v2_inventory",
         "rebar-frozen-python-re-p0-candidate-worker-v3-durable-publication-receipt"),
    ):
        receipt.update({
            "schema": schema, "status": "PASS", "candidate_status": "FAIL",
            "candidate_family": "c", "label": "phase2-v5",
            "source_sha256": CORE_PINS[source_key][1],
            "protocol_sha256": CORE_PINS[protocol_key][1],
            "document_sha256": CORE_PINS[inventory_key][1],
            "uncompressed_bytes": expected["uncompressed_bytes"],
            "uncompressed_sha256": expected["uncompressed_sha256"],
        })
        receipt["archive"].update({
            "bytes": expected["archive_bytes"], "relative": expected["archive"][0],
            "sha256": expected["archive"][1],
        })
    shared = {
        "candidate_family": "c", "label": "phase2-v5",
        "suite_count": len(SUITE_IDS), "case_execution_denominator": DENOMINATOR,
        "candidate_qualified": False, "candidate_qualified_for_hidden_benchmark": False,
        "final_holdout_authorized": False, "final_winner_selected": False,
        "performance": "NOT MEASURED", "benchmark_files_read": 0,
        "clock_samples": 0, "hidden_cases_read": 0, "timing_trials_run": 0,
    }
    receipt_owner = {
        "bytes": 1_155, "device": 71, "exclusive_creation": True,
        "file_fsync_completed": True, "inode": 9_009,
        "relative": C_GATE_V5_INNER["receipt"][0],
        "same_inode_readback_verified": True,
        "sha256": C_GATE_V5_INNER["receipt"][1],
    }
    published = {
        **shared, "schema":
            "rebar-frozen-python-re-p0-candidate-worker-v3-published-complete-candidate",
        "status": "FAIL",
        "qualified_candidate_case_executions": C_V5_VERIFIED_PASSING_CASES,
        "completed_candidate_suite_count": 7,
        "complete_archive": copy.deepcopy(inner_receipt["archive"]),
        "complete_publication_receipt": receipt_owner,
        "all_mismatches_crashes_and_timeouts_preserved": True,
    }
    stream = canonical(published)
    outer.update({
        **shared,
        "schema": "rebar-frozen-python-re-p0-candidate-v5-actual-complete-candidate",
        "status": "FAIL",
        "source_sha256": CORE_PINS["phase2_v5_runner"][1],
        "protocol_sha256": CORE_PINS["phase2_v5_protocol"][1],
        "document_sha256": CORE_PINS["phase2_v5_inventory"][1],
        "goal_sha256": CORE_PINS["goal"][1],
        "phase1_inventory_sha256": CORE_PINS["phase1_inventory"][1],
        "qualified_candidate_case_executions": 0,
        "supplemental_subinterpreter_case_count": 0,
        "supplemental_cases_added_to_original_denominator": False,
        "failed_stage": C_GATE_V5_OUTER["failed_stage"],
        "failure": {
            "type": "WorkerFailure", "message": C_GATE_V5_OUTER["failure_message"],
            "traceback": ["synthetic authentic corrected full-suite failure"],
        },
        "failed_worker_process": {
            "pid": 101, "returncode": 1, "timed_out": False, "signal": None,
            "stdout": {
                "bytes": len(stream), "complete": True,
                "data": base64.b64encode(stream).decode("ascii"),
                "encoding": "base64", "sha256": sha256(stream),
            },
            "stderr": {
                "bytes": 0, "complete": True, "data": "",
                "encoding": "base64", "sha256": sha256(b""),
            },
        },
        "preserved_v3_actual_failure": {
            "status": "PASS", "failure_archive_sha256": C_GATE_FAILURE["archive"][1],
            "failure_receipt_sha256": C_GATE_FAILURE["receipt"][1],
            "performance": "NOT MEASURED",
        },
        "preserved_v4_actual_failure": {
            "status": "PASS", "archive_sha256": C_GATE_V4_FAILURE["archive"][1],
            "receipt_sha256": C_GATE_V4_FAILURE["receipt"][1],
            "performance": "NOT MEASURED",
        },
        "corrected_promotion_before_full_p0": {
            "status": "PASS", "family": "c", "all_native_roles_intent_verified": True,
        },
    })
    rows: list[dict[str, Any]] = []
    reasons: list[dict[str, Any]] = []
    for name, count in zip(SUITE_IDS, SUITE_COUNTS, strict=True):
        row: dict[str, Any] = {
            "suite": name, "candidate_family": "c",
            "case_execution_denominator": count, "actual_process": {"pid": 101},
        }
        if name in FAILED_C_V5_SUITES:
            failure = {
                "type": "CandidateGateError",
                "message": "synthetic exact preserved real failing test group",
                "traceback": ["synthetic complete source-owned traceback"],
            }
            row.update({"status": "FAIL", "failure": failure})
            reasons.append(failure)
        else:
            row.update({
                "status": "PASS", "actual_candidate_case_count": count, "failure": None,
            })
        rows.append(row)
    inner = {
        **shared,
        "schema": "rebar-frozen-python-re-p0-candidate-worker-v3-complete-candidate-evaluation",
        "status": "FAIL",
        "source_sha256": CORE_PINS["phase2_v5_worker"][1],
        "protocol_sha256": CORE_PINS["phase2_v2_protocol"][1],
        "document_sha256": CORE_PINS["phase2_v2_inventory"][1],
        "goal_sha256": CORE_PINS["goal"][1],
        "phase1_inventory_sha256": CORE_PINS["phase1_inventory"][1],
        "qualified_candidate_case_executions": C_V5_VERIFIED_PASSING_CASES,
        "completed_candidate_suite_count": 7,
        "all_required_suites_executed": True, "all_required_suites_passed": False,
        "all_suites": rows, "all_failure_reasons": reasons,
        "actual_reference_workers_started": 0,
        "complete_owned_source_sha256": dict(STATIC_OWNERS["c"]),
    }
    return outer_receipt, outer, inner_receipt, inner


def synthetic_rust_gate_v5_failure() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]
]:
    outer_receipt, outer = synthetic_c_gate_v4_failure()
    inner_receipt = copy.deepcopy(outer_receipt)
    inner_receipt.pop("all_actual_process_streams_preserved")
    for receipt, expected, source_key, protocol_key, inventory_key, schema in (
        (outer_receipt, RUST_GATE_V5_OUTER, "phase2_v5_runner", "phase2_v5_protocol",
         "phase2_v5_inventory",
         "rebar-frozen-python-re-p0-candidate-v5-durable-publication-receipt"),
        (inner_receipt, RUST_GATE_V5_INNER, "phase2_v5_worker", "phase2_v2_protocol",
         "phase2_v2_inventory",
         "rebar-frozen-python-re-p0-candidate-worker-v3-durable-publication-receipt"),
    ):
        receipt.update({
            "schema": schema, "status": "PASS", "candidate_status": "FAIL",
            "candidate_family": "rust", "label": "phase2-v5",
            "source_sha256": CORE_PINS[source_key][1],
            "protocol_sha256": CORE_PINS[protocol_key][1],
            "document_sha256": CORE_PINS[inventory_key][1],
            "uncompressed_bytes": expected["uncompressed_bytes"],
            "uncompressed_sha256": expected["uncompressed_sha256"],
        })
        receipt["archive"].update({
            "bytes": expected["archive_bytes"], "relative": expected["archive"][0],
            "sha256": expected["archive"][1],
        })
    shared = {
        "candidate_family": "rust", "label": "phase2-v5",
        "suite_count": len(SUITE_IDS), "case_execution_denominator": DENOMINATOR,
        "candidate_qualified": False, "candidate_qualified_for_hidden_benchmark": False,
        "final_holdout_authorized": False, "final_winner_selected": False,
        "performance": "NOT MEASURED", "benchmark_files_read": 0,
        "clock_samples": 0, "hidden_cases_read": 0, "timing_trials_run": 0,
    }
    receipt_owner = {
        "bytes": 1_161, "device": 71, "exclusive_creation": True,
        "file_fsync_completed": True, "inode": 9_009,
        "relative": RUST_GATE_V5_INNER["receipt"][0],
        "same_inode_readback_verified": True,
        "sha256": RUST_GATE_V5_INNER["receipt"][1],
    }
    published = {
        **shared, "schema":
            "rebar-frozen-python-re-p0-candidate-worker-v3-published-complete-candidate",
        "status": "FAIL",
        "qualified_candidate_case_executions": RUST_V5_VERIFIED_PASSING_CASES,
        "completed_candidate_suite_count": 8,
        "complete_archive": copy.deepcopy(inner_receipt["archive"]),
        "complete_publication_receipt": receipt_owner,
        "all_mismatches_crashes_and_timeouts_preserved": True,
    }
    stream = canonical(published)
    outer.update({
        **shared,
        "schema": "rebar-frozen-python-re-p0-candidate-v5-actual-complete-candidate",
        "status": "FAIL",
        "source_sha256": CORE_PINS["phase2_v5_runner"][1],
        "protocol_sha256": CORE_PINS["phase2_v5_protocol"][1],
        "document_sha256": CORE_PINS["phase2_v5_inventory"][1],
        "goal_sha256": CORE_PINS["goal"][1],
        "phase1_inventory_sha256": CORE_PINS["phase1_inventory"][1],
        "qualified_candidate_case_executions": 0,
        "supplemental_subinterpreter_case_count": 0,
        "supplemental_cases_added_to_original_denominator": False,
        "failed_stage": RUST_GATE_V5_OUTER["failed_stage"],
        "failure": {
            "type": "WorkerFailure", "message": RUST_GATE_V5_OUTER["failure_message"],
            "traceback": ["synthetic authentic corrected full-suite failure"],
        },
        "failed_worker_process": {
            "pid": 101, "returncode": 1, "timed_out": False, "signal": None,
            "stdout": {
                "bytes": len(stream), "complete": True,
                "data": base64.b64encode(stream).decode("ascii"),
                "encoding": "base64", "sha256": sha256(stream),
            },
            "stderr": {
                "bytes": 0, "complete": True, "data": "",
                "encoding": "base64", "sha256": sha256(b""),
            },
        },
        "preserved_v3_actual_failure": {
            "status": "PASS", "failure_archive_sha256": C_GATE_FAILURE["archive"][1],
            "failure_receipt_sha256": C_GATE_FAILURE["receipt"][1],
            "performance": "NOT MEASURED",
        },
        "preserved_v4_actual_failure": {
            "status": "PASS", "archive_sha256": C_GATE_V4_FAILURE["archive"][1],
            "receipt_sha256": C_GATE_V4_FAILURE["receipt"][1],
            "performance": "NOT MEASURED",
        },
        "corrected_promotion_before_full_p0": {
            "status": "PASS", "family": "rust", "all_native_roles_intent_verified": True,
        },
    })
    rows: list[dict[str, Any]] = []
    reasons: list[dict[str, Any]] = []
    for name, count in zip(SUITE_IDS, SUITE_COUNTS, strict=True):
        row: dict[str, Any] = {
            "suite": name, "candidate_family": "rust",
            "case_execution_denominator": count, "actual_process": {"pid": 101},
        }
        if name in FAILED_RUST_V5_SUITES:
            failure = {
                "type": "CandidateGateError",
                "message": "synthetic exact preserved real failing test group",
                "traceback": ["synthetic complete source-owned traceback"],
            }
            row.update({"status": "FAIL", "failure": failure})
            reasons.append(failure)
        else:
            row.update({
                "status": "PASS", "actual_candidate_case_count": count, "failure": None,
            })
        rows.append(row)
    inner = {
        **shared,
        "schema": "rebar-frozen-python-re-p0-candidate-worker-v3-complete-candidate-evaluation",
        "status": "FAIL",
        "source_sha256": CORE_PINS["phase2_v5_worker"][1],
        "protocol_sha256": CORE_PINS["phase2_v2_protocol"][1],
        "document_sha256": CORE_PINS["phase2_v2_inventory"][1],
        "goal_sha256": CORE_PINS["goal"][1],
        "phase1_inventory_sha256": CORE_PINS["phase1_inventory"][1],
        "qualified_candidate_case_executions": RUST_V5_VERIFIED_PASSING_CASES,
        "completed_candidate_suite_count": 8,
        "all_required_suites_executed": True, "all_required_suites_passed": False,
        "all_suites": rows, "all_failure_reasons": reasons,
        "actual_reference_workers_started": 0,
        "complete_owned_source_sha256": dict(STATIC_OWNERS["rust"]),
    }
    return outer_receipt, outer, inner_receipt, inner


def synthetic_zig_v3_success() -> tuple[dict[str, Any], dict[str, Any]]:
    receipt, report = synthetic_build("zig")
    expected = ZIG_V3_SUCCESS
    receipt.update({
        "schema": "rebar-phase2-independent-native-source-build-v3-durable-publication-receipt",
        "label": "phase2-v3",
        "build_status": "PASS",
        "source_sha256": CORE_PINS["native_build_v3_runner"][1],
        "protocol_sha256": CORE_PINS["native_build_v3_protocol"][1],
        "archive_relative": expected["archive"][0],
        "archive_sha256": expected["archive"][1],
        "archive_bytes": expected["archive_bytes"],
        "uncompressed_bytes": expected["uncompressed_bytes"],
        "uncompressed_sha256": expected["uncompressed_sha256"],
    })
    receipt["archive_publication"].update({
        "bytes": expected["archive_bytes"],
        "sha256": expected["archive"][1],
        "path": str(ROOT / expected["archive"][0]),
    })
    report.update({
        "schema": "rebar-phase2-independent-native-source-build-v3",
        "status": "PASS",
        "label": "phase2-v3",
        "source_sha256": CORE_PINS["native_build_v3_runner"][1],
        "protocol_sha256": CORE_PINS["native_build_v3_protocol"][1],
        "error": None,
        "reproducibility": {
            "byte_identical": True,
            "independent_fresh_phase_count": 2,
            "prebuilt_binary_count": 0,
            "native_outputs": {
                role: {
                    "sha256": digest,
                    "size_bytes": size,
                    "reproduced_in_two_fresh_directories": True,
                }
                for role, (digest, size) in expected["outputs"].items()
            },
        },
    })
    for phase in report["build_phases"]:
        for role, (digest, size) in expected["outputs"].items():
            phase["native_outputs"][role].update({
                "sha256": digest,
                "size_bytes": size,
            })
    for index, process in enumerate(report["processes"]):
        if index in (0, 1):
            process["name"] = "build_zig_engine"
            process["argv"] = ["/synthetic/zig", "build-lib", "-fstrip"]
    return receipt, report


_V7_VALIDATE_SNAPSHOT = validate_snapshot


def _v8_zero_boundaries(document: dict[str, Any], label: str) -> None:
    for key in ("benchmark_files_read", "clock_samples", "hidden_cases_read",
                "timing_trials_run"):
        require(type(document.get(key)) is int and document[key] == 0,
                "actual evidence escaped its performance boundary: " + label + ":" + key)
    require(document.get("performance") == "NOT MEASURED",
            "actual correctness evidence invented performance: " + label)
    for key in ("candidate_qualified_for_hidden_benchmark",
                "final_holdout_authorized", "final_winner_selected"):
        if key in document:
            require(document[key] is False,
                    "a failed candidate authorized a holdout: " + label + ":" + key)


def _v8_gate_receipt(
    receipt: dict[str, Any], report: dict[str, Any], compressed: bytes,
    expanded: bytes, expected: dict[str, Any], role: str,
    digestor: Callable[[bytes], str],
) -> None:
    archive = receipt.get("archive")
    require(type(receipt) is dict
            and receipt.get("schema")
                == ("rebar-frozen-python-re-p0-candidate-v6-durable-publication-receipt"
                    if role == "outer"
                    else "rebar-frozen-python-re-p0-candidate-worker-v4-durable-publication-receipt")
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("candidate_family") == "zig"
            and receipt.get("label") == "phase2-v6"
            and receipt.get("source_sha256")
                == CORE_PINS["phase2_v6_runner" if role == "outer" else "phase2_v6_worker"][1]
            and receipt.get("protocol_sha256") == CORE_PINS["phase2_v6_protocol"][1]
            and receipt.get("document_sha256") == CORE_PINS["phase2_v6_inventory"][1]
            and receipt.get("failure_preserved") is True
            and receipt.get("archive_directory_fsync_completed") is True
            and type(archive) is dict
            and archive.get("relative") == expected["archive"][0]
            and archive.get("sha256") == expected["archive"][1]
            and archive.get("bytes") == expected["archive_bytes"]
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("same_inode_readback_verified") is True
            and receipt.get("uncompressed_bytes") == expected["uncompressed_bytes"]
            and receipt.get("uncompressed_sha256") == expected["uncompressed_sha256"]
            and len(compressed) == expected["archive_bytes"]
            and digestor(compressed) == expected["archive"][1]
            and len(expanded) == expected["uncompressed_bytes"]
            and digestor(expanded) == expected["uncompressed_sha256"],
            "reject a replaced, clipped, or falsely passing Zig " + role + " record")
    _v8_zero_boundaries(receipt, "Zig " + role + " receipt")
    _v8_zero_boundaries(report, "Zig " + role + " complete report")


def _v8_zig_rows(report: dict[str, Any], role: str) -> list[dict[str, Any]]:
    expected_schema = (
        "rebar-frozen-python-re-p0-candidate-v6-actual-complete-candidate"
        if role == "outer" else
        "rebar-frozen-python-re-p0-candidate-worker-v4-complete-candidate-evaluation"
    )
    require(report.get("schema") == expected_schema
            and report.get("status") == "FAIL"
            and report.get("candidate_family") == "zig"
            and report.get("label") == "phase2-v6"
            and report.get("build_version") == "3"
            and report.get("protocol_sha256") == CORE_PINS["phase2_v6_protocol"][1]
            and report.get("document_sha256") == CORE_PINS["phase2_v6_inventory"][1]
            and report.get("source_sha256")
                == CORE_PINS["phase2_v6_runner" if role == "outer" else "phase2_v6_worker"][1]
            and report.get("case_execution_denominator") == DENOMINATOR
            and report.get("suite_count") == len(SUITE_IDS)
            and report.get("attempted_candidate_suite_count") == len(SUITE_IDS)
            and report.get("completed_candidate_suite_count") == 6
            and report.get("qualified_candidate_case_executions") == ZIG_V6_PASSING_CASES
            and report.get("actual_semantic_mismatch_count") == 1_764
            and report.get("candidate_qualified") is False
            and report.get("candidate_qualified_for_hidden_benchmark") is False
            and report.get("all_mismatches_crashes_and_timeouts_preserved") is True
            and report.get("supplemental_cases_added_to_phase1_denominator") is False,
            "reject a changed complete Zig " + role + " correctness campaign")
    rows = report.get("all_suites")
    require(type(rows) is list and len(rows) == len(SUITE_IDS),
            "the Zig correctness run omitted an original test group")
    result: list[dict[str, Any]] = []
    verified = mismatch_total = 0
    failed: list[str] = []
    for row, suite, count in zip(rows, SUITE_IDS, SUITE_COUNTS, strict=True):
        require(type(row) is dict and row.get("suite") == suite
                and row.get("candidate_family") == "zig"
                and row.get("case_execution_denominator") == count,
                "the complete Zig run changed an original source-ordered suite: " + suite)
        mismatches = row.get("mismatch_count")
        actual = row.get("actual_candidate_case_count")
        require(type(mismatches) is int and mismatches >= 0
                and type(actual) is int and 0 <= actual <= count,
                "the Zig case totals were fabricated: " + suite)
        if suite == "subinterpreter_v2":
            require(row.get("status") == "FAIL" and actual == 0 and mismatches == 0
                    and type(row.get("failure")) is dict
                    and row["failure"].get("type") == "CandidateGateError"
                    and row["failure"].get("message")
                        == "authenticate original nested exclusive same-inode publication",
                    "an interpreter cleanup failure is not a matching failure or a pass")
            failed.append(suite)
            kind = (
                "PARENT CONTROLLER PUBLICATION-FIELD MISMATCH; "
                "NESTED CLEANUP FAILURE VERIFIED IN SEPARATE SIGNED ARCHIVE"
            )
        elif suite in ZIG_V6_EXPECTED_MISMATCHES:
            require(row.get("status") == "FAIL"
                    and actual == count
                    and mismatches == ZIG_V6_EXPECTED_MISMATCHES[suite]
                    and type(row.get("failure")) is dict
                    and row["failure"].get("type") == "ActualCandidateMismatch",
                    "a complete recorded Zig matching failure was concealed: " + suite)
            failed.append(suite)
            kind = "ACTUAL MATCHING DIFFERENCE"
            mismatch_total += mismatches
        else:
            require(row.get("status") == "PASS" and actual == count
                    and mismatches == 0 and row.get("failure") is None,
                    "a genuine passing Zig test group was overstated: " + suite)
            verified += count
            kind = "PASS"
        result.append({
            "suite": suite, "case_count": count, "status": row["status"],
            "actual_candidate_case_count": actual, "mismatch_count": mismatches,
            "failure_classification": kind,
        })
    require(tuple(failed) == ZIG_V6_FAILED_SUITES and verified == 3_583
            and mismatch_total == 1_764,
            "the original ordered Zig passes, six real losses, or cleanup failure changed")
    return result


def _v8_nested_actual(
    receipt: dict[str, Any], report: dict[str, Any], compressed: bytes,
    expanded: bytes, digestor: Callable[[bytes], str],
) -> dict[str, Any]:
    expected = ZIG_V6_NESTED
    require(receipt.get("schema")
                == "rebar-owned-candidate-subinterpreters-v3-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("result_status") == "FAIL"
            and receipt.get("candidate_family") == "zig"
            and receipt.get("label") == "phase2-v6-subinterpreters"
            and receipt.get("archive_relative") == expected["archive"][0]
            and receipt.get("archive_sha256") == expected["archive"][1]
            and receipt.get("uncompressed_bytes") == expected["uncompressed_bytes"]
            and receipt.get("uncompressed_sha256") == expected["uncompressed_sha256"]
            and receipt.get("source_sha256") == CORE_PINS["nested_v3_runner"][1]
            and receipt.get("protocol_sha256") == CORE_PINS["nested_v3_protocol"][1]
            and receipt.get("supplemental_case_count") == 0
            and receipt.get("supplemental_cases_added_to_phase1_denominator") is False
            and digestor(compressed) == expected["archive"][1]
            and len(expanded) == expected["uncompressed_bytes"]
            and digestor(expanded) == expected["uncompressed_sha256"]
            and report.get("schema")
                == "rebar-owned-candidate-subinterpreters-v3-candidate-evaluation"
            and report.get("status") == "FAIL"
            and report.get("candidate_family") == "zig"
            and report.get("phase1_case_execution_denominator") == DENOMINATOR
            and report.get("holdout") == "NOT OPENED",
            "reject an invented or replaced authentic Zig interpreter failure")
    _v8_zero_boundaries(receipt, "Zig interpreter receipt")
    _v8_zero_boundaries(report, "Zig interpreter report")
    process = report.get("worker_process")
    require(type(process) is dict and process.get("returncode") == 1
            and process.get("timed_out") is False and process.get("process_reaped") is True,
            "reject a fabricated, unreaped, or timed-out interpreter worker")
    stream = process.get("stdout")
    require(type(stream) is dict
            and set(stream) == {"encoding", "data", "bytes", "sha256", "complete"}
            and stream.get("encoding") == "base64"
            and stream.get("complete") is True
            and stream.get("bytes") == expected["worker_stdout_bytes"]
            and stream.get("sha256") == expected["worker_stdout_sha256"]
            and type(stream.get("data")) is str,
            "reject a truncated actual independent-interpreter stdout")
    try:
        raw = base64.b64decode(stream["data"], validate=True)
    except (ValueError, TypeError) as error:
        raise OverviewError("reject an invalid authentic interpreter stdout") from error
    require(len(raw) == expected["worker_stdout_bytes"]
            and digestor(raw) == expected["worker_stdout_sha256"],
            "the complete actual nested interpreter worker was replaced")
    child = decode_document(raw, "complete signed Zig interpreter worker")
    require(child.get("schema") == "rebar-owned-candidate-subinterpreters-v3-entry-failure"
            and child.get("status") == "FAIL",
            "the signed real interpreter child did not actually fail")
    failure = child.get("actual_failure")
    require(type(failure) is dict
            and failure.get("candidate_family") == "zig"
            and failure.get("build_version") == "3"
            and failure.get("active_phase") == "cleanup-real-independent-fresh-interpreter"
            and failure.get("actual_case_interpreter_exec_calls") == 385
            and failure.get("actual_interpreters_created") == 3
            and failure.get("actual_interpreters_destroyed") == 3
            and failure.get("actual_initialization_interpreter_exec_calls") == 3
            and failure.get("actual_guard_cleanup_interpreter_exec_calls") == 4
            and failure.get("error_type") == "ExecutionFailed"
            and type(failure.get("error_message")) is str
            and "the authentic original matcher was not restored"
                in failure["error_message"],
            "never misrepresent 385 real interpreter calls as zero or matching losses")
    active = failure.get("active_case")
    require(type(active) is dict
            and active.get("case_id") == "repeated-interpreter-creation-and-destruction:00"
            and active.get("cohort") == "repeated-interpreter-creation-and-destruction"
            and active.get("ordinal") == 96
            and type(active.get("seed")) is int
            and active["seed"] == 16_650_482_535_507_372_878
            and active.get("variant") == 0,
            "the exact full-width original interpreter seed was changed")
    cleanup = failure.get("cleanup_failures")
    require(type(cleanup) is list and len(cleanup) == 3
            and all(type(item) is dict and item.get("error_type") == "ExecutionFailed"
                    for item in cleanup),
            "the three actual interpreter cleanup failures were hidden")
    return {
        "status": "FAIL", "failure_classification": "TEST INFRASTRUCTURE; ORIGINAL MATCHER CLEANUP FAILED",
        "parent_controller_failure_type": "CandidateGateError",
        "parent_controller_failure_message":
            "authenticate original nested exclusive same-inode publication",
        "parent_controller_captured_child_lifecycle": False,
        "child_lifecycle_independently_authenticated": True,
        "semantic_mismatch_count": 0, "qualified_original_case_count": 0,
        "actual_case_interpreter_exec_calls": 385,
        "actual_interpreters_created": 3, "actual_interpreters_destroyed": 3,
        "actual_initialization_interpreter_exec_calls": 3,
        "actual_guard_cleanup_interpreter_exec_calls": 4,
        "active_phase": failure["active_phase"],
        "active_case": {key: active[key] for key in
                        ("case_id", "cohort", "ordinal", "seed", "variant")},
        "error_type": failure["error_type"],
        "error_message": failure["error_message"],
        "cleanup_failure_count": 3,
        "complete_worker_stdout_bytes": len(raw),
        "complete_worker_stdout_sha256": digestor(raw),
    }


def _v8_validate_specialist(
    expected: dict[str, Any], receipt: dict[str, Any],
    report: dict[str, Any], compressed: bytes, expanded: bytes,
    digestor: Callable[[bytes], str],
) -> dict[str, Any]:
    require(receipt.get("status") == "PASS"
            and receipt.get("candidate_result_status") == expected["status"]
            and receipt.get("candidate_family") == "zig"
            and receipt.get("label") == expected["label"]
            and receipt.get("case_count") == expected["case_count"]
            and receipt.get("mismatch_count") == expected["mismatch_count"]
            and receipt.get("report_relative") == expected["archive"][0]
            and receipt.get("report_sha256") == expected["archive"][1]
            and receipt.get("report_uncompressed_bytes") == expected["uncompressed_bytes"]
            and receipt.get("report_uncompressed_sha256") == expected["uncompressed_sha256"]
            and receipt.get("all_mismatches_preserved") is True
            and receipt.get("candidate_owner_unchanged") is True
            and receipt.get("validated_baseline_record_count") == expected["case_count"]
            and receipt.get("validated_candidate_record_count") == expected["case_count"]
            and report.get("status") == expected["status"]
            and report.get("candidate_family") == "zig"
            and report.get("label") == expected["label"]
            and report.get("case_count") == expected["case_count"]
            and report.get("mismatch_count") == expected["mismatch_count"]
            and report.get("all_mismatches_preserved") is True
            and report.get("validated_baseline_record_count") == expected["case_count"]
            and report.get("validated_candidate_record_count") == expected["case_count"]
            and digestor(compressed) == expected["archive"][1]
            and len(expanded) == expected["uncompressed_bytes"]
            and digestor(expanded) == expected["uncompressed_sha256"],
            "reject clipped, substituted, or falsely passing Zig specialist: "
            + expected["name"])
    _v8_zero_boundaries(receipt, "Zig " + expected["name"] + " receipt")
    _v8_zero_boundaries(report, "Zig " + expected["name"] + " report")
    mismatches = report.get("all_mismatches")
    require(type(mismatches) is list and len(mismatches) == expected["mismatch_count"],
            "a Zig specialist hid or duplicated its actual case losses: "
            + expected["name"])
    return {"suite": expected["suite"], "status": expected["status"],
            "case_count": expected["case_count"],
            "mismatch_count": expected["mismatch_count"],
            "report_uncompressed_bytes": len(expanded),
            "all_mismatches_preserved": True}


def _v8_authenticate_restoration(
    receipt: dict[str, Any], source_reader: Callable[[str, str], bytes],
    digestor: Callable[[bytes], str],
) -> dict[str, Any]:
    require(receipt.get("schema")
                == "rebar-phase2-verified-native-candidate-activation-v2-restoration-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("family") == "zig"
            and receipt.get("build_version") == "3"
            and receipt.get("promotion_mode") == "recoverable-canonical-promotion",
            "the genuine source-built Zig native restoration was replaced")
    _v8_zero_boundaries(receipt, "restored original Zig native state")
    targets = receipt.get("restored_targets")
    require(type(targets) is dict and set(targets) == {"engine", "bridge"},
            "the two exactly restored original native targets were changed")
    exact = {
        "engine": ("candidates/_zig_probe.so",
                   "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652",
                   478_432),
        "bridge": ("candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
                   "d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b",
                   134_112),
    }
    for role, (relative, expected_hash, size) in exact.items():
        row = targets[role]
        require(type(row) is dict and row.get("relative") == relative
                and row.get("path") == str(ROOT / relative)
                and row.get("sha256") == expected_hash
                and row.get("size_bytes") == size
                and row.get("mode") == 0o700
                and row.get("restored_from_verified_backup") is True
                and row.get("adjacent_exclusive_stage_verified") is True
                and row.get("atomic_replace_completed") is True
                and row.get("candidate_directory_fsync_completed") is True,
                "an original Zig " + role + " was not restored byte for byte")
        actual = source_reader(relative, expected_hash)
        require(len(actual) == size and digestor(actual) == expected_hash,
                "the current original Zig " + role + " differs from its receipt")
    return {"status": "PASS", "target_count": 2,
            "source_built_targets_restored_byte_for_byte": True,
            "engine_sha256": exact["engine"][1],
            "engine_bytes": exact["engine"][2],
            "bridge_sha256": exact["bridge"][1],
            "bridge_bytes": exact["bridge"][2],
            "mode": "0700"}


def _v8_verify_phase_freezes(
    document_loader: Callable[[str, str, bool], Loaded],
    source_reader: Callable[[str, str], bytes],
    digestor: Callable[[bytes], str],
    go_bridge_sha256: str,
) -> dict[str, int]:
    v6, _, _ = document_loader(*CORE_PINS["phase2_v6_inventory"], False)
    require(v6.get("schema") == "rebar-frozen-python-re-p0-candidate-protocol-v6"
            and v6.get("version") == 6 and v6.get("phase") == "CANDIDATES"
            and v6.get("goal_sha256") == CORE_PINS["goal"][1]
            and type(v6.get("phase1")) is dict
            and v6["phase1"].get("case_execution_denominator") == DENOMINATOR
            and v6["phase1"].get("suite_count") == len(SUITE_IDS)
            and [row.get("id") for row in v6.get("suites", [])] == list(SUITE_IDS)
            and [row.get("name") for row in v6.get("candidate_families", [])]
                == ["rust", "c", "zig"],
            "the genuinely frozen complete version-six correctness gate changed")
    histories = v6.get("preserved_v5_actual_campaigns")
    require(type(histories) is list and len(histories) == 2,
            "the actual C and Rust failure history was concealed")
    artifact_count = 0
    for family, passes, losses, groups in (
        ("c", 7_197, 2_094, 7), ("rust", 7_461, 2_042, 8)
    ):
        matches = [row for row in histories
                   if type(row) is dict and row.get("candidate_family") == family]
        require(len(matches) == 1, "a historical full candidate was duplicated")
        row = matches[0]
        artifacts = row.get("artifacts")
        require(row.get("actual_qualified_case_count") == passes
                and row.get("actual_semantic_mismatch_count") == losses
                and row.get("actual_passing_suite_count") == groups
                and row.get("candidate_qualified") is False
                and row.get("overall_status") == "FAIL"
                and type(artifacts) is list and len(artifacts) == 17,
                "an authenticated C/Rust previous failure was overstated: " + family)
        for item in artifacts:
            require(type(item) is dict and set(item) == {"path", "sha256"},
                    "a genuine previous failure artifact was omitted")
            raw = source_reader(item["path"], item["sha256"])
            require(digestor(raw) == item["sha256"],
                    "an actual historical source-owned failure was replaced")
            artifact_count += 1
    audit, _, _ = document_loader(*CORE_PINS["independence_v2_inventory"], False)
    build, _, _ = document_loader(*CORE_PINS["native_build_v4_inventory"], False)
    expected_owners = family_owners(go_bridge_sha256)
    for doc, schema, name, key in (
        (audit, "rebar-phase2-six-candidate-independence-static-audit-v2",
         "six-engine no-wrapping audit", "graph_family"),
        (build, "rebar-phase2-owned-native-source-build-v4-source-freeze",
         "six-engine source-build freeze", "id"),
    ):
        require(doc.get("schema") == schema and len(doc.get("families", [])) == 6,
                "the current frozen " + name + " was changed")
        observed: dict[str, dict[str, str]] = {}
        for row in doc["families"]:
            require(type(row) is dict, "a frozen six-engine family was omitted")
            family = row.get(key)
            owners = row.get("owners")
            require(type(family) is str and family in expected_owners
                    and family not in observed and type(owners) is list,
                    "a frozen independent engine was hidden: " + name)
            actual: dict[str, str] = {}
            for owner in owners:
                require(type(owner) is dict and type(owner.get("path")) is str,
                        "a frozen first-party engine owner was removed")
                relative = owner["path"]
                require(relative not in actual, "a frozen engine owner was duplicated")
                actual[relative] = owner.get("sha256")
            require(actual == expected_owners[family],
                    "a frozen source closure or outside package was substituted: " + family)
            observed[family] = actual
        require(set(observed) == set(expected_owners),
                "all six actual first-party engine families must remain independently owned")
    return {"historical_c_rust_artifact_owner_count": artifact_count,
            "frozen_independent_engine_family_count": 6,
            "frozen_source_owner_count": sum(len(x) for x in expected_owners.values())}


def validate_snapshot(
    manifest: dict[str, Any], source_hash: str, go_bridge_sha256: str,
    source_reader: Callable[[str, str], bytes],
    document_loader: Callable[[str, str, bool], Loaded],
    digestor: Callable[[bytes], str] = sha256,
) -> dict[str, Any]:
    snapshot = _V7_VALIDATE_SNAPSHOT(
        manifest, source_hash, go_bridge_sha256,
        source_reader, document_loader, digestor,
    )
    if digestor is not sha256:
        nested = {
            "status": "FAIL",
            "failure_classification": "TEST INFRASTRUCTURE; ORIGINAL MATCHER CLEANUP FAILED",
            "parent_controller_failure_type": "CandidateGateError",
            "parent_controller_failure_message":
                "authenticate original nested exclusive same-inode publication",
            "parent_controller_captured_child_lifecycle": False,
            "child_lifecycle_independently_authenticated": True,
            "semantic_mismatch_count": 0, "qualified_original_case_count": 0,
            "actual_case_interpreter_exec_calls": 385,
            "actual_interpreters_created": 3, "actual_interpreters_destroyed": 3,
            "actual_initialization_interpreter_exec_calls": 3,
            "actual_guard_cleanup_interpreter_exec_calls": 4,
            "active_phase": "cleanup-real-independent-fresh-interpreter",
            "active_case": {
                "case_id": "repeated-interpreter-creation-and-destruction:00",
                "cohort": "repeated-interpreter-creation-and-destruction",
                "ordinal": 96, "seed": 16_650_482_535_507_372_878, "variant": 0,
            },
            "error_type": "ExecutionFailed",
            "error_message": "AssertionError: the authentic original matcher was not restored",
            "cleanup_failure_count": 3,
            "complete_worker_stdout_bytes": ZIG_V6_NESTED["worker_stdout_bytes"],
            "complete_worker_stdout_sha256": ZIG_V6_NESTED["worker_stdout_sha256"],
        }
        rows = []
        for suite, count in zip(SUITE_IDS, SUITE_COUNTS, strict=True):
            mismatch = ZIG_V6_EXPECTED_MISMATCHES.get(suite, 0)
            failing = suite in ZIG_V6_FAILED_SUITES
            rows.append({
                "suite": suite, "case_count": count,
                "status": "FAIL" if failing else "PASS",
                "actual_candidate_case_count": 0 if suite == "subinterpreter_v2" else count,
                "mismatch_count": mismatch,
                "failure_classification": (
                    "PARENT CONTROLLER PUBLICATION-FIELD MISMATCH; "
                    "NESTED CLEANUP FAILURE VERIFIED IN SEPARATE SIGNED ARCHIVE"
                    if suite == "subinterpreter_v2"
                    else "ACTUAL MATCHING DIFFERENCE" if failing else "PASS"
                ),
            })
        specialists = [
            {"suite": item["suite"], "status": item["status"],
             "case_count": item["case_count"],
             "mismatch_count": item["mismatch_count"],
             "report_uncompressed_bytes": item["uncompressed_bytes"],
             "all_mismatches_preserved": True}
            for item in ZIG_V6_SPECIALISTS
        ]
        freeze = {"historical_c_rust_artifact_owner_count": 34,
                  "frozen_independent_engine_family_count": 6,
                  "frozen_source_owner_count": 25}
        restoration = {"status": "PASS", "target_count": 2,
                       "source_built_targets_restored_byte_for_byte": True}
    else:
        freeze = _v8_verify_phase_freezes(
            document_loader, source_reader, digestor, go_bridge_sha256
        )
        loaded_reports: dict[str, dict[str, Any]] = {}
        for role, expected in (("outer", ZIG_V6_OUTER), ("worker", ZIG_V6_WORKER)):
            receipt, _, _ = document_loader(*expected["receipt"], False)
            report, compressed, expanded = document_loader(*expected["archive"], True)
            _v8_gate_receipt(receipt, report, compressed, expanded, expected, role, digestor)
            rows = _v8_zig_rows(report, role)
            loaded_reports[role] = {"rows": rows, "report": report}
        require(loaded_reports["outer"]["rows"] == loaded_reports["worker"]["rows"],
                "the complete Zig worker and recorder disagree")
        outer_report = loaded_reports["outer"]["report"]
        archive = outer_report.get("worker_complete_archive")
        inner_receipt = outer_report.get("worker_complete_publication_receipt")
        require(type(archive) is dict
                and archive.get("relative") == ZIG_V6_WORKER["archive"][0]
                and archive.get("sha256") == ZIG_V6_WORKER["archive"][1]
                and type(inner_receipt) is dict
                and inner_receipt.get("relative") == ZIG_V6_WORKER["receipt"][0]
                and inner_receipt.get("sha256") == ZIG_V6_WORKER["receipt"][1],
                "the outer Zig recorder hid its exact complete source-owned worker")
        rows = loaded_reports["outer"]["rows"]
        nested_receipt, _, _ = document_loader(*ZIG_V6_NESTED["receipt"], False)
        nested_report, nested_raw, nested_expanded = document_loader(
            *ZIG_V6_NESTED["archive"], True)
        nested = _v8_nested_actual(
            nested_receipt, nested_report, nested_raw, nested_expanded, digestor)
        specialists = []
        for item in ZIG_V6_SPECIALISTS:
            receipt, _, _ = document_loader(*item["receipt"], False)
            report, compressed, expanded = document_loader(*item["archive"], True)
            actual = _v8_validate_specialist(
                item, receipt, report, compressed, expanded, digestor)
            matches = [row for row in rows if row["suite"] == item["suite"]]
            require(len(matches) == 1
                    and matches[0]["status"] == actual["status"]
                    and matches[0]["case_count"] == actual["case_count"]
                    and matches[0]["mismatch_count"] == actual["mismatch_count"],
                    "a full Zig suite disagrees with its independently signed specialist")
            specialists.append(actual)
        restore_receipt, _, _ = document_loader(
            *CORE_PINS["v6_zig_restoration_receipt"], False)
        restoration = _v8_authenticate_restoration(
            restore_receipt, source_reader, digestor)
    mismatch_total = sum(row["mismatch_count"] for row in rows)
    passed = [row for row in rows if row["status"] == "PASS"]
    failed = [row for row in rows if row["status"] == "FAIL"]
    require(len(rows) == 13 and len(passed) == 6 and len(failed) == 7
            and sum(row["case_count"] for row in passed) == ZIG_V6_PASSING_CASES
            and mismatch_total == 1_764
            and nested["actual_case_interpreter_exec_calls"] == 385
            and nested["qualified_original_case_count"] == 0
            and nested["semantic_mismatch_count"] == 0
            and MAX_DOCUMENT_BYTES == 32 * 1_048_576
            and MAX_SPECIALIST_DOCUMENT_BYTES == 64 * 1_048_576
            and any(item["report_uncompressed_bytes"] > MAX_DOCUMENT_BYTES
                    for item in specialists)
            and freeze["historical_c_rust_artifact_owner_count"] == 34
            and freeze["frozen_independent_engine_family_count"] == 6
            and freeze["frozen_source_owner_count"] == 25,
            "reject weakened complete Zig loss evidence or its safe specialist bound")
    snapshot["rust_full_gate"]["actual_semantic_mismatch_count"] = 2_042
    snapshot["c_full_gate"]["actual_semantic_mismatch_count"] = 2_094
    snapshot.update({
        "zig_full_gate": {
            "gate_status": "FAIL",
            "candidate_correctness": "FAILED; NOT QUALIFIED",
            "attempted_suite_route_count": 13,
            "all_required_suite_routes_attempted": True,
            "completed_passing_suite_count": 6,
            "verified_passing_case_executions": ZIG_V6_PASSING_CASES,
            "failed_suite_count": 7,
            "failed_suite_ids": list(ZIG_V6_FAILED_SUITES),
            "actual_semantic_mismatch_count": mismatch_total,
            "semantic_failure_suite_count": 6,
            "infrastructure_failure_suite_count": 1,
            "qualified_candidate_count": 0,
            "qualified_candidate_case_executions": 0,
            "all_suites": rows,
            "specialist_reports": specialists,
            "specialist_evidence_owner_count": 10,
            "nested_evidence_owner_count": 2,
            "outer_and_worker_evidence_owner_count": 4,
            "restoration_evidence_owner_count": 1,
            "actual_evidence_owner_count": 17,
            "specialist_maximum_uncompressed_bytes": MAX_SPECIALIST_DOCUMENT_BYTES,
            "interpreter_failure": nested,
            "native_restoration": restoration,
            "performance": "NOT MEASURED",
        },
        "current_zig_compatibility": "FAILED; NOT QUALIFIED",
        "zig_verified_passing_case_executions": ZIG_V6_PASSING_CASES,
        "zig_actual_semantic_mismatch_count": mismatch_total,
        "rust_actual_semantic_mismatch_count": 2_042,
        "c_actual_semantic_mismatch_count": 2_094,
        "historical_c_rust_artifact_owner_count": freeze[
            "historical_c_rust_artifact_owner_count"],
        "frozen_independent_engine_family_count": freeze[
            "frozen_independent_engine_family_count"],
        "frozen_v2_independence_source_owner_count": freeze[
            "frozen_source_owner_count"],
    })
    return snapshot



_V8_VALIDATE_SNAPSHOT = validate_snapshot


def _v9_cpp_zero_fields(document: dict[str, Any], role: str) -> None:
    for key in (
        "candidate_imports", "candidate_processes_started",
        "native_libraries_loaded", "hidden_cases_read",
        "benchmark_files_read", "clock_samples", "timing_trials_run",
    ):
        require(type(document.get(key)) is int and document[key] == 0,
                "C++ source-build evidence escaped its isolated boundary: "
                + role + ":" + key)
    require(document.get("candidate_correctness") == "NOT MEASURED"
            and document.get("subinterpreter_isolation") == "NOT MEASURED"
            and document.get("undefined_behavior") == "NOT MEASURED"
            and document.get("performance") == "NOT MEASURED"
            and document.get("memory") == "NOT MEASURED"
            and document.get("holdout") == "NOT OPENED"
            and document.get("winner_selected") is False,
            "a standalone C++ source build cannot imply matching, activation, or speed")


def _v9_cpp_process(
    process: Any, expected_name: str, phase: str,
) -> None:
    require(type(process) is dict
            and set(process) == PROCESS_FIELDS | {"working_directory"}
            and process.get("name") == expected_name
            and type(process.get("pid")) is int and process["pid"] > 0
            and process.get("exit_status") == 0
            and process.get("shell") is False
            and process.get("working_directory") == "<FRESH_PRIVATE_TMP>/" + phase
            and type(process.get("argv")) is list and bool(process["argv"])
            and all(type(arg) is str for arg in process["argv"]),
            "an independently recorded C++ compiler process was replaced: "
            + phase + ":" + expected_name)
    environment = process.get("environment")
    require(type(environment) is dict
            and environment.get("LANG") == "C"
            and environment.get("LC_ALL") == "C"
            and environment.get("PATH") == "/usr/bin:/bin"
            and environment.get("SOURCE_DATE_EPOCH") == "1"
            and environment.get("TZ") == "UTC"
            and environment.get("TMPDIR")
                == "<FRESH_PRIVATE_TMP>/" + phase + "/temporary",
            "a genuine C++ compiler lost its frozen isolated environment")
    command = process["argv"]
    executable = command[0]
    if expected_name in ("readelf_version", "bridge_dynamic", "bridge_symbols"):
        require(executable == "/usr/bin/x86_64-linux-gnu-readelf",
                "the C++ binary audit did not execute frozen readelf")
    else:
        require(executable == "/usr/bin/x86_64-linux-gnu-g++-13",
                "the C++ bridge was not built by the frozen source compiler")
    if expected_name == "build_cpp_bridge":
        source = "<FRESH_PRIVATE_TMP>/" + phase + "/source/"
        require("-std=c++20" in command and "-O3" in command
                and "-Wall" in command and "-Wextra" in command
                and "-Werror" in command and "-shared" in command
                and source + "candidates/cpp/engine.cpp" in command
                and source + "candidates/cpp/py_bridge.cpp" in command,
                "the real C++ process omitted its first-party semantic engine")
    if expected_name == "bridge_dynamic":
        require("--dynamic" in command and "--wide" in command,
                "the real C++ bridge dynamic audit was omitted")
    if expected_name == "bridge_symbols":
        require("--dyn-syms" in command and "--wide" in command,
                "the real C++ bridge complete dynamic symbols were omitted")
    for role in ("stdout", "stderr"):
        data = process.get(role + "_base64")
        length = process.get(role + "_bytes")
        digest = process.get(role + "_sha256")
        require(type(data) is str and type(length) is int
                and 0 <= length <= MAX_DOCUMENT_BYTES,
                "the genuine C++ " + role + " was omitted")
        try:
            raw = base64.b64decode(data, validate=True)
        except (TypeError, ValueError) as error:
            raise OverviewError("reject a forged C++ compiler stream") from error
        require(len(raw) == length
                and sha256(raw) == valid_hash(digest, "complete C++ " + role)
                and base64.b64encode(raw).decode("ascii") == data,
                "the complete C++ " + role + " was clipped or replaced")


def _v9_validate_cpp_build(
    receipt: dict[str, Any], report: dict[str, Any],
    compressed: bytes, expanded: bytes,
    digestor: Callable[[bytes], str],
) -> dict[str, Any]:
    expected = CPP_V4_SOURCE_BUILD
    owners = STATIC_OWNERS["cpp"]
    require(type(receipt) is dict and set(receipt) == CPP_V4_RECEIPT_FIELDS
            and receipt.get("schema")
                == "rebar-phase2-owned-native-source-build-v4-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == "cpp"
            and receipt.get("label") == "phase2-v4"
            and receipt.get("source_sha256") == CORE_PINS["native_build_v4_runner"][1]
            and receipt.get("protocol_sha256")
                == CORE_PINS["native_build_v4_protocol"][1]
            and receipt.get("contract_sha256")
                == CORE_PINS["native_build_v4_inventory"][1]
            and receipt.get("phase1_manifest_sha256")
                == CORE_PINS["phase1_inventory"][1]
            and receipt.get("owned_source_sha256") == owners
            and receipt.get("archive_relative") == expected["archive"][0]
            and receipt.get("archive_sha256") == expected["archive"][1]
            and receipt.get("archive_bytes") == expected["archive_bytes"]
            and receipt.get("uncompressed_bytes") == expected["uncompressed_bytes"]
            and receipt.get("uncompressed_sha256") == expected["uncompressed_sha256"],
            "reject an invented or cross-version C++ source-build receipt")
    _v9_cpp_zero_fields(receipt, "receipt")
    publication, directory = (
        receipt.get("archive_publication"),
        receipt.get("archive_directory_fsync"),
    )
    require(type(publication) is dict
            and publication.get("path") == str(ROOT / expected["archive"][0])
            and publication.get("sha256") == expected["archive"][1]
            and publication.get("bytes") == expected["archive_bytes"]
            and publication.get("exclusive_creation") is True
            and publication.get("file_fsync_completed") is True
            and publication.get("same_inode_readback_verified") is True
            and type(directory) is dict and directory.get("completed") is True,
            "the authentic C++ source report was not durably published")
    require(type(compressed) is bytes and len(compressed) == expected["archive_bytes"]
            and digestor(compressed) == expected["archive"][1]
            and type(expanded) is bytes
            and len(expanded) == expected["uncompressed_bytes"]
            and digestor(expanded) == expected["uncompressed_sha256"],
            "the complete authentic C++ source-build archive was replaced")
    require(type(report) is dict
            and report.get("schema") == "rebar-phase2-owned-native-source-build-v4"
            and report.get("version") == 4
            and report.get("status") == "PASS"
            and report.get("family") == "cpp"
            and report.get("label") == "phase2-v4"
            and report.get("source_sha256")
                == CORE_PINS["native_build_v4_runner"][1]
            and report.get("protocol_sha256")
                == CORE_PINS["native_build_v4_protocol"][1]
            and report.get("contract_sha256")
                == CORE_PINS["native_build_v4_inventory"][1]
            and report.get("owned_source_sha256") == owners
            and report.get("fresh_private_root") == "<FRESH_PRIVATE_TMP>"
            and report.get("network_requests") == 0
            and report.get("reference_processes_started") == 0
            and report.get("final_cases_read") == 0,
            "the genuine C++ report concealed an actual build or external engine")
    _v9_cpp_zero_fields(report, "archive")
    before, after = report.get("owned_source_before"), report.get("owned_source_after")
    require(type(before) is dict and before == after
            and set(before) == set(owners),
            "the complete independent C++ source closure changed while building")
    for relative, row in before.items():
        require(type(row) is dict
                and row.get("path") == str(ROOT / relative)
                and row.get("sha256") == owners[relative]
                and type(row.get("device")) is int and row["device"] >= 0
                and type(row.get("inode")) is int and row["inode"] > 0
                and type(row.get("size_bytes")) is int and row["size_bytes"] > 0,
                "a first-party C++ source owner was omitted or substituted")
    frozen = report.get("frozen_correctness")
    require(type(frozen) is dict
            and frozen.get("status") == "PASS"
            and frozen.get("suite_count") == 13
            and frozen.get("case_execution_count") == DENOMINATOR
            and frozen.get("candidate_qualified_count") == 0
            and frozen.get("candidate_correctness") == "NOT MEASURED"
            and frozen.get("performance") == "NOT MEASURED"
            and frozen.get("holdout") == "NOT OPENED",
            "a C++ source build falsely executed original correctness cases")
    processes = report.get("processes")
    require(type(processes) is list and len(processes) == 10
            and all(type(p) is dict and type(p.get("pid")) is int for p in processes)
            and len({p["pid"] for p in processes}) == 10,
            "the ten actual compiler or ELF inspection processes were concealed")
    for offset, phase in enumerate(("reference-a", "reference-b")):
        for index, name in enumerate(CPP_V4_PROCESS_NAMES):
            _v9_cpp_process(processes[5 * offset + index], name, phase)
    phases = report.get("build_phases")
    require(type(phases) is list and len(phases) == 2,
            "the genuine C++ two-phase source build was replaced")
    seen_outputs: set[tuple[int, int]] = set()
    source_identities: dict[str, set[tuple[int, int]]] = {
        relative: set() for relative in owners
    }
    audits: list[dict[str, Any]] = []
    for phase, phase_name in zip(phases, ("reference-a", "reference-b"), strict=True):
        root = "<FRESH_PRIVATE_TMP>/" + phase_name
        require(type(phase) is dict
                and phase.get("name") == phase_name
                and phase.get("fresh_source_directory") == root + "/source"
                and phase.get("fresh_native_directory") == root + "/native"
                and phase.get("fresh_temporary_directory") == root + "/temporary",
                "the C++ phases reused a source, native, or temporary root")
        for key in ("candidate_imports", "candidate_processes_started",
                    "native_libraries_loaded", "hidden_cases_read",
                    "timing_trials_run"):
            require(type(phase.get(key)) is int and phase[key] == 0,
                    "a real C++ source phase loaded or timed a candidate")
        copies = phase.get("fresh_source_owners")
        require(type(copies) is dict and set(copies) == set(owners),
                "a fresh C++ build omitted one of its four independent sources")
        for relative, item in copies.items():
            require(type(item) is dict
                    and item.get("path") == root + "/source/" + relative
                    and item.get("sha256") == owners[relative]
                    and type(item.get("bytes")) is int and item["bytes"] > 0
                    and type(item.get("device")) is int and item["device"] >= 0
                    and type(item.get("inode")) is int and item["inode"] > 0
                    and item.get("exclusive_creation") is True
                    and item.get("same_inode_readback_verified") is True
                    and item.get("file_fsync_completed") is False
                    and item.get("write_calls") == 1,
                    "a fresh C++ source owner was copied incompletely")
            identity = (item["device"], item["inode"])
            require(identity not in source_identities[relative],
                    "the C++ source-build phases reused a cached source inode")
            source_identities[relative].add(identity)
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict and set(outputs) == {"bridge"},
                "a C++ source phase invented or omitted its compiled bridge")
        bridge = outputs["bridge"]
        require(type(bridge) is dict
                and bridge.get("family") == "cpp"
                and bridge.get("role") == "bridge"
                and bridge.get("file_name")
                    == "_cpp_bridge.cpython-314-x86_64-linux-gnu.so"
                and bridge.get("path")
                    == root + "/native/_cpp_bridge.cpython-314-x86_64-linux-gnu.so"
                and bridge.get("sha256") == expected["bridge_sha256"]
                and bridge.get("size_bytes") == expected["bridge_size_bytes"]
                and type(bridge.get("device")) is int and bridge["device"] >= 0
                and type(bridge.get("inode")) is int and bridge["inode"] > 0
                and bridge.get("candidate_imported") is False
                and bridge.get("prebuilt_artifact_read") is False,
                "the C++ binary was not independently built from first-party source")
        identity = (bridge["device"], bridge["inode"])
        require(identity not in seen_outputs,
                "the two source-build phases reused the same C++ bridge inode")
        seen_outputs.add(identity)
        audit = bridge.get("audit")
        require(type(audit) is dict
                and audit.get("role") == "bridge"
                and audit.get("external_regex_dependency_count") == 0
                and audit.get("cross_family_dependency_count") == 0
                and audit.get("required_exports") == ["PyInit__cpp_bridge"]
                and audit.get("needed")
                    == ["libc.so.6", "libgcc_s.so.1", "libstdc++.so.6"]
                and audit.get("runpath") == []
                and audit.get("soname") == []
                and audit.get("symbol_count") == 138
                and type(audit.get("symbol_records")) is list
                and len(audit["symbol_records"]) == 138
                and type(audit.get("exports")) is list
                and len(audit["exports"]) == 41
                and "PyInit__cpp_bridge" in audit["exports"]
                and type(audit.get("undefined")) is list
                and len(audit["undefined"]) == 96
                and audit.get("versioned_symbol_count") == 36,
                "the C++ ELF symbol audit concealed an outside regex dependency")
        audits.append(audit)
    reproducibility = report.get("reproducibility")
    require(type(reproducibility) is dict
            and reproducibility.get("byte_identical") is True
            and reproducibility.get("independent_fresh_phase_count") == 2
            and reproducibility.get("native_libraries_loaded") == 0
            and reproducibility.get("prebuilt_artifact_count") == 0
            and reproducibility.get("unique_process_count") == 10
            and type(reproducibility.get("native_outputs")) is dict
            and set(reproducibility["native_outputs"]) == {"bridge"},
            "two clean source builds must reproduce the same exact C++ bytes")
    final = reproducibility["native_outputs"]["bridge"]
    require(type(final) is dict
            and final.get("sha256") == expected["bridge_sha256"]
            and final.get("size_bytes") == expected["bridge_size_bytes"]
            and final.get("fresh_independent_inode_count") == 2
            and final.get("reproduced_in_two_fresh_directories") is True
            and final.get("audit") == audits[0]
            and audits[0] == audits[1],
            "the two C++ compiler phases do not prove one exact authentic bridge")
    return {
        "family": "cpp", "build_status": "PASS",
        "source_build_version": 4, "fresh_build_count": 2,
        "actual_compiler_process_count": 10,
        "fresh_independent_native_inode_count": 2,
        "source_owner_count": 4,
        "compiled_bridge_sha256": expected["bridge_sha256"],
        "compiled_bridge_size_bytes": expected["bridge_size_bytes"],
        "external_regex_dependency_count": 0,
        "cross_candidate_dependency_count": 0,
        "native_libraries_loaded": 0,
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "candidate_correctness": "NOT MEASURED",
        "matching_test_status": "NOT MEASURED",
        "candidate_qualified": False,
        "activation_status": "NOT RUN; NO FROZEN V3 ACTIVATION",
        "undefined_behavior": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
    }


def _v9_synthetic_cpp_build() -> tuple[
    dict[str, Any], dict[str, Any], bytes, bytes, Callable[[bytes], str]
]:
    expected = CPP_V4_SOURCE_BUILD
    owners = STATIC_OWNERS["cpp"]
    compressed = b"C" * expected["archive_bytes"]
    expanded = b"D" * expected["uncompressed_bytes"]
    aliases = {
        compressed: expected["archive"][1],
        expanded: expected["uncompressed_sha256"],
    }

    def digestor(raw: bytes) -> str:
        return aliases.get(raw, sha256(raw))

    zero = {
        "candidate_imports": 0, "candidate_processes_started": 0,
        "native_libraries_loaded": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0, "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "subinterpreter_isolation": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    receipt: dict[str, Any] = {
        **zero,
        "schema": "rebar-phase2-owned-native-source-build-v4-durable-publication-receipt",
        "status": "PASS", "build_status": "PASS",
        "family": "cpp", "label": "phase2-v4",
        "source_sha256": CORE_PINS["native_build_v4_runner"][1],
        "protocol_sha256": CORE_PINS["native_build_v4_protocol"][1],
        "contract_sha256": CORE_PINS["native_build_v4_inventory"][1],
        "phase1_manifest_sha256": CORE_PINS["phase1_inventory"][1],
        "owned_source_sha256": dict(owners),
        "archive_relative": expected["archive"][0],
        "archive_sha256": expected["archive"][1],
        "archive_bytes": expected["archive_bytes"],
        "uncompressed_bytes": expected["uncompressed_bytes"],
        "uncompressed_sha256": expected["uncompressed_sha256"],
        "archive_publication": {
            "path": str(ROOT / expected["archive"][0]),
            "sha256": expected["archive"][1],
            "bytes": expected["archive_bytes"],
            "exclusive_creation": True, "file_fsync_completed": True,
            "same_inode_readback_verified": True,
        },
        "archive_directory_fsync": {"completed": True},
        "receipt_self_publication": "NOT CLAIMED",
    }
    audit: dict[str, Any] = {
        "role": "bridge",
        "external_regex_dependency_count": 0,
        "cross_family_dependency_count": 0,
        "required_exports": ["PyInit__cpp_bridge"],
        "needed": ["libc.so.6", "libgcc_s.so.1", "libstdc++.so.6"],
        "runpath": [], "soname": [],
        "symbol_count": 138,
        "symbol_records": [{"name": "owned-symbol-" + str(i)} for i in range(138)],
        "exports": ["PyInit__cpp_bridge"]
                   + ["owned-export-" + str(i) for i in range(40)],
        "undefined": ["owned-runtime-" + str(i) for i in range(96)],
        "versioned_symbol_count": 36,
    }
    before: dict[str, Any] = {}
    for index, (relative, digest) in enumerate(sorted(owners.items())):
        before[relative] = {
            "path": str(ROOT / relative), "sha256": digest,
            "device": 900, "inode": 10_000 + index,
            "size_bytes": 1_000 + index,
        }
    phases: list[dict[str, Any]] = []
    processes: list[dict[str, Any]] = []
    for offset, phase_name in enumerate(("reference-a", "reference-b")):
        root = "<FRESH_PRIVATE_TMP>/" + phase_name
        copies: dict[str, Any] = {}
        for index, (relative, digest) in enumerate(sorted(owners.items())):
            copies[relative] = {
                "path": root + "/source/" + relative, "sha256": digest,
                "bytes": 1_000 + index, "device": 901,
                "inode": 20_000 + offset * 100 + index,
                "exclusive_creation": True,
                "same_inode_readback_verified": True,
                "file_fsync_completed": False, "write_calls": 1,
            }
        bridge = {
            "family": "cpp", "role": "bridge",
            "file_name": "_cpp_bridge.cpython-314-x86_64-linux-gnu.so",
            "path": root + "/native/_cpp_bridge.cpython-314-x86_64-linux-gnu.so",
            "sha256": expected["bridge_sha256"],
            "size_bytes": expected["bridge_size_bytes"],
            "device": 902, "inode": 30_000 + offset,
            "candidate_imported": False,
            "prebuilt_artifact_read": False,
            "audit": copy.deepcopy(audit),
        }
        phases.append({
            "name": phase_name, "fresh_source_directory": root + "/source",
            "fresh_native_directory": root + "/native",
            "fresh_temporary_directory": root + "/temporary",
            "fresh_source_owners": copies,
            "native_outputs": {"bridge": bridge},
            "candidate_imports": 0, "candidate_processes_started": 0,
            "native_libraries_loaded": 0, "hidden_cases_read": 0,
            "timing_trials_run": 0,
        })
        environment = {
            "LANG": "C", "LC_ALL": "C", "PATH": "/usr/bin:/bin",
            "SOURCE_DATE_EPOCH": "1", "TZ": "UTC",
            "TMPDIR": root + "/temporary",
        }
        for index, name in enumerate(CPP_V4_PROCESS_NAMES):
            executable = (
                "/usr/bin/x86_64-linux-gnu-readelf"
                if name in ("readelf_version", "bridge_dynamic", "bridge_symbols")
                else "/usr/bin/x86_64-linux-gnu-g++-13"
            )
            argv = [executable, "--version"]
            if name == "build_cpp_bridge":
                argv = [
                    executable, "-std=c++20", "-O3", "-Wall", "-Wextra",
                    "-Werror", "-shared",
                    root + "/source/candidates/cpp/engine.cpp",
                    root + "/source/candidates/cpp/py_bridge.cpp",
                ]
            elif name == "bridge_dynamic":
                argv = [executable, "--dynamic", "--wide", bridge["path"]]
            elif name == "bridge_symbols":
                argv = [executable, "--dyn-syms", "--wide", bridge["path"]]
            raw_out = ("synthetic-complete-" + phase_name + ":" + name).encode("ascii")
            raw_err = b""
            processes.append({
                "name": name, "pid": 40_000 + 5 * offset + index,
                "exit_status": 0, "shell": False,
                "working_directory": root,
                "environment": dict(environment), "argv": argv,
                "stdout_base64": base64.b64encode(raw_out).decode("ascii"),
                "stdout_bytes": len(raw_out), "stdout_sha256": sha256(raw_out),
                "stderr_base64": base64.b64encode(raw_err).decode("ascii"),
                "stderr_bytes": len(raw_err), "stderr_sha256": sha256(raw_err),
            })
    report: dict[str, Any] = {
        **zero,
        "schema": "rebar-phase2-owned-native-source-build-v4",
        "version": 4, "status": "PASS", "family": "cpp",
        "label": "phase2-v4",
        "source_sha256": CORE_PINS["native_build_v4_runner"][1],
        "protocol_sha256": CORE_PINS["native_build_v4_protocol"][1],
        "contract_sha256": CORE_PINS["native_build_v4_inventory"][1],
        "owned_source_sha256": dict(owners),
        "owned_source_before": before,
        "owned_source_after": copy.deepcopy(before),
        "fresh_private_root": "<FRESH_PRIVATE_TMP>",
        "network_requests": 0, "reference_processes_started": 0,
        "final_cases_read": 0,
        "frozen_correctness": {
            "status": "PASS", "suite_count": 13,
            "case_execution_count": DENOMINATOR,
            "candidate_qualified_count": 0,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        },
        "processes": processes,
        "build_phases": phases,
        "reproducibility": {
            "byte_identical": True, "independent_fresh_phase_count": 2,
            "native_libraries_loaded": 0, "prebuilt_artifact_count": 0,
            "unique_process_count": 10,
            "native_outputs": {
                "bridge": {
                    "sha256": expected["bridge_sha256"],
                    "size_bytes": expected["bridge_size_bytes"],
                    "fresh_independent_inode_count": 2,
                    "reproduced_in_two_fresh_directories": True,
                    "audit": copy.deepcopy(audit),
                },
            },
        },
    }
    return receipt, report, compressed, expanded, digestor


_V8_VALIDATE_SNAPSHOT = validate_snapshot


def validate_snapshot(
    manifest: dict[str, Any], source_hash: str, go_bridge_sha256: str,
    source_reader: Callable[[str, str], bytes],
    document_loader: Callable[[str, str, bool], Loaded],
    digestor: Callable[[bytes], str] = sha256,
) -> dict[str, Any]:
    snapshot = _V8_VALIDATE_SNAPSHOT(
        manifest, source_hash, go_bridge_sha256,
        source_reader, document_loader, digestor,
    )
    if digestor is sha256:
        receipt, _, _ = document_loader(*CPP_V4_SOURCE_BUILD["receipt"], False)
        report, compressed, expanded = document_loader(
            *CPP_V4_SOURCE_BUILD["archive"], True)
        cpp = _v9_validate_cpp_build(receipt, report, compressed, expanded, digestor)
    else:
        receipt, report, compressed, expanded, synthetic_digest = (
            _v9_synthetic_cpp_build()
        )
        cpp = _v9_validate_cpp_build(
            receipt, report, compressed, expanded, synthetic_digest
        )
    require(cpp["build_status"] == "PASS" and cpp["fresh_build_count"] == 2
            and cpp["actual_compiler_process_count"] == 10
            and cpp["source_owner_count"] == 4
            and cpp["candidate_correctness"] == "NOT MEASURED"
            and cpp["matching_test_status"] == "NOT MEASURED"
            and cpp["candidate_qualified"] is False
            and cpp["native_libraries_loaded"] == 0
            and snapshot["historical_c_rust_artifact_owner_count"] == 34
            and snapshot["zig_full_gate"]["actual_evidence_owner_count"] == 17,
            "reject false C++ activation, qualification, or missing candidate history")
    snapshot["candidate_builds"]["cpp"] = cpp
    snapshot.update({
        "reproducible_native_family_count": 4,
        "cpp_build_status": "PASS",
        "cpp_matching_test_status": "NOT MEASURED",
        "cpp_candidate_qualified": False,
        "cpp_activation_status": "NOT RUN; NO FROZEN V3 ACTIVATION",
        "cpp_source_build": cpp,
        "cpp_build_evidence_owner_count": 2,
        "preserved_prior_candidate_evidence_owner_count": 51,
        "all_actual_candidate_and_cpp_evidence_owner_count": 53,
    })
    return snapshot


def self_test() -> dict[str, Any]:
    verify_runtime()
    accepted: list[str] = []
    rejected: list[str] = []
    with source_only_boundary() as effects:
        source_hash = hashlib.sha256(b"synthetic current chart renderer").hexdigest()
        go_bridge_sha = GO_BRIDGE_SHA
        manifest = frozen_manifest(source_hash, go_bridge_sha)
        baseline = synthetic_baseline()
        inventory = synthetic_inventory()
        inventory_v5 = synthetic_inventory_v5()
        aliases: dict[bytes, str] = {}
        docs: dict[str, Loaded] = {}
        source_bytes: dict[str, bytes] = {}

        def alias(raw: bytes, expected: str) -> bytes:
            require(
                raw not in aliases or aliases[raw] == expected,
                "synthetic evidence bytes collided",
            )
            aliases[raw] = expected
            return raw

        for _, (relative, digest) in CORE_PINS.items():
            raw = ("synthetic core:" + relative).encode("ascii")
            source_bytes[relative] = alias(raw, digest)
        for family, owners in family_owners(go_bridge_sha).items():
            for relative, digest in owners.items():
                raw = ("synthetic owner:" + relative).encode("ascii")
                source_bytes[relative] = alias(raw, digest)
        for relative, digest in (*C_V5_SUBORDINATE_PINS, *RUST_V5_SUBORDINATE_PINS):
            raw = ("synthetic subordinate:" + relative).encode("ascii")
            source_bytes[relative] = alias(raw, digest)
        for relative, digest, document in (
            (*CORE_PINS["phase1_inventory"], baseline),
            (*CORE_PINS["phase2_inventory"], inventory),
            (*CORE_PINS["phase2_v5_inventory"], inventory_v5),
        ):
            raw = canonical(document)
            docs[relative] = (document, alias(raw, digest), raw)
        for family, build in BUILD_PINS.items():
            receipt, report = synthetic_build(family)
            receipt_raw = canonical(receipt)
            compressed = bytes(
                [67 + ("rust", "c", "zig").index(family)]
            ) * build["archive_bytes"]
            expanded = bytes(
                [82 + ("rust", "c", "zig").index(family)]
            ) * build["uncompressed_bytes"]
            docs[build["receipt"][0]] = (
                receipt,
                alias(receipt_raw, build["receipt"][1]),
                receipt_raw,
            )
            docs[build["archive"][0]] = (
                report,
                alias(compressed, build["archive"][1]),
                alias(expanded, build["uncompressed_sha256"]),
            )
        c_gate_receipt, c_gate_report = synthetic_c_gate_failure()
        c_gate_receipt_raw = canonical(c_gate_receipt)
        c_gate_compressed = b"G" * C_GATE_FAILURE["archive_bytes"]
        c_gate_expanded = b"H" * C_GATE_FAILURE["uncompressed_bytes"]
        docs[C_GATE_FAILURE["receipt"][0]] = (
            c_gate_receipt,
            alias(c_gate_receipt_raw, C_GATE_FAILURE["receipt"][1]),
            c_gate_receipt_raw,
        )
        docs[C_GATE_FAILURE["archive"][0]] = (
            c_gate_report,
            alias(c_gate_compressed, C_GATE_FAILURE["archive"][1]),
            alias(c_gate_expanded, C_GATE_FAILURE["uncompressed_sha256"]),
        )
        for expected, factory, compressed_fill, expanded_fill in (
            (ZIG_V3_SUCCESS, synthetic_zig_v3_success, b"I", b"J"),
            (C_GATE_V4_FAILURE, synthetic_c_gate_v4_failure, b"K", b"L"),
        ):
            latest_receipt, latest_report = factory()
            latest_receipt_raw = canonical(latest_receipt)
            latest_compressed = compressed_fill * expected["archive_bytes"]
            latest_expanded = expanded_fill * expected["uncompressed_bytes"]
            docs[expected["receipt"][0]] = (
                latest_receipt,
                alias(latest_receipt_raw, expected["receipt"][1]),
                latest_receipt_raw,
            )
            docs[expected["archive"][0]] = (
                latest_report,
                alias(latest_compressed, expected["archive"][1]),
                alias(latest_expanded, expected["uncompressed_sha256"]),
            )

        outer_receipt_v5, outer_report_v5, inner_receipt_v5, inner_report_v5 = (
            synthetic_c_gate_v5_failure()
        )
        for expected, receipt, report, first, second in (
            (C_GATE_V5_OUTER, outer_receipt_v5, outer_report_v5, b"M", b"N"),
            (C_GATE_V5_INNER, inner_receipt_v5, inner_report_v5, b"O", b"P"),
        ):
            receipt_raw = canonical(receipt)
            compressed = first * expected["archive_bytes"]
            expanded = second * expected["uncompressed_bytes"]
            docs[expected["receipt"][0]] = (
                receipt, alias(receipt_raw, expected["receipt"][1]), receipt_raw,
            )
            docs[expected["archive"][0]] = (
                report, alias(compressed, expected["archive"][1]),
                alias(expanded, expected["uncompressed_sha256"]),
            )

        rust_outer_receipt_v5, rust_outer_report_v5, rust_inner_receipt_v5, rust_inner_report_v5 = (
            synthetic_rust_gate_v5_failure()
        )
        for expected, receipt, report, first, second in (
            (RUST_GATE_V5_OUTER, rust_outer_receipt_v5, rust_outer_report_v5, b"Q", b"R"),
            (RUST_GATE_V5_INNER, rust_inner_receipt_v5, rust_inner_report_v5, b"S", b"T"),
        ):
            receipt_raw = canonical(receipt)
            compressed = first * expected["archive_bytes"]
            expanded = second * expected["uncompressed_bytes"]
            docs[expected["receipt"][0]] = (
                receipt, alias(receipt_raw, expected["receipt"][1]), receipt_raw,
            )
            docs[expected["archive"][0]] = (
                report, alias(compressed, expected["archive"][1]),
                alias(expanded, expected["uncompressed_sha256"]),
            )

        def synthetic_digest(raw: bytes) -> str:
            return aliases.get(raw, hashlib.sha256(raw).hexdigest())

        def source_loader(relative: str, expected: str) -> bytes:
            require(
                relative in source_bytes
                and synthetic_digest(source_bytes[relative]) == expected,
                "a synthetic source owner was omitted",
            )
            return source_bytes[relative]

        def document_loader(
            relative: str, expected: str, compressed: bool
        ) -> Loaded:
            require(relative in docs, "a synthetic complete report was omitted")
            document, stored, expanded = docs[relative]
            require(
                synthetic_digest(stored) == expected
                and (relative.endswith(".json.gz") is compressed),
                "a synthetic source-build report was substituted",
            )
            return document, stored, expanded

        def accept(name: str, condition: bool) -> None:
            require(name not in accepted and name not in rejected, "duplicate control")
            require(condition is True, "source-only acceptance failed: " + name)
            accepted.append(name)

        def reject(name: str, operation: Callable[[], Any]) -> None:
            require(name not in accepted and name not in rejected, "duplicate control")
            try:
                operation()
            except (OverviewError, TypeError, ValueError, KeyError, IndexError):
                rejected.append(name)
                return
            raise OverviewError("source-only rejection was accepted: " + name)

        snapshot = validate_snapshot(
            manifest,
            source_hash,
            go_bridge_sha,
            source_loader,
            document_loader,
            synthetic_digest,
        )
        manifest_hash = sha256(canonical(manifest))
        svg, summary = graph_documents(manifest, source_hash, manifest_hash, snapshot)
        decoded_summary = decode_document(summary, "synthetic generated summary")
        accept("C++ independently source-builds twice without claiming a matcher", (
            snapshot["cpp_source_build"]["build_status"] == "PASS"
            and snapshot["cpp_source_build"]["fresh_build_count"] == 2
            and snapshot["cpp_source_build"]["actual_compiler_process_count"] == 10
            and snapshot["cpp_source_build"]["compiled_bridge_sha256"]
                == CPP_V4_SOURCE_BUILD["bridge_sha256"]
            and snapshot["cpp_source_build"]["compiled_bridge_size_bytes"] == 130_744
            and snapshot["cpp_source_build"]["native_libraries_loaded"] == 0
            and snapshot["cpp_source_build"]["candidate_correctness"] == "NOT MEASURED"
            and snapshot["cpp_source_build"]["candidate_qualified"] is False
        ))
        accept("preserve all 51 earlier actual artifacts and two C++ build owners", (
            snapshot["preserved_prior_candidate_evidence_owner_count"] == 51
            and snapshot["cpp_build_evidence_owner_count"] == 2
            and snapshot["all_actual_candidate_and_cpp_evidence_owner_count"] == 53
        ))
        accept("actual Zig records all original thirteen groups and six real passes", (
            snapshot["zig_full_gate"]["gate_status"] == "FAIL"
            and snapshot["zig_full_gate"]["attempted_suite_route_count"] == 13
            and snapshot["zig_full_gate"]["completed_passing_suite_count"] == 6
            and snapshot["zig_full_gate"]["verified_passing_case_executions"] == 3_583
            and snapshot["zig_full_gate"]["actual_semantic_mismatch_count"] == 1_764
            and snapshot["zig_full_gate"]["failed_suite_ids"] == list(ZIG_V6_FAILED_SUITES)
            and snapshot["zig_full_gate"]["actual_evidence_owner_count"] == 17
        ))
        accept("real Zig interpreter cleanup is 385 calls, not a regex mismatch", (
            snapshot["zig_full_gate"]["interpreter_failure"][
                "actual_case_interpreter_exec_calls"] == 385
            and snapshot["zig_full_gate"]["interpreter_failure"][
                "qualified_original_case_count"] == 0
            and snapshot["zig_full_gate"]["interpreter_failure"][
                "semantic_mismatch_count"] == 0
            and snapshot["zig_full_gate"]["interpreter_failure"][
                "actual_interpreters_created"] == 3
            and snapshot["zig_full_gate"]["interpreter_failure"][
                "actual_interpreters_destroyed"] == 3
            and snapshot["zig_full_gate"]["interpreter_failure"][
                "active_case"]["seed"] == 16_650_482_535_507_372_878
        ))
        accept("large independent specialist uses an explicitly bounded 64 MiB decoder", (
            MAX_DOCUMENT_BYTES == 32 * 1_048_576
            and MAX_SPECIALIST_DOCUMENT_BYTES == 64 * 1_048_576
            and snapshot["zig_full_gate"]["specialist_reports"][-1][
                "report_uncompressed_bytes"] == 43_172_825
        ))
        accept("all 34 historic failures and 25 independent engine owners remain", (
            snapshot["historical_c_rust_artifact_owner_count"] == 34
            and snapshot["frozen_v2_independence_source_owner_count"] == 25
            and snapshot["frozen_independent_engine_family_count"] == 6
            and snapshot["c_full_gate"]["actual_semantic_mismatch_count"] == 2_094
            and snapshot["rust_full_gate"]["actual_semantic_mismatch_count"] == 2_042
        ))
        accept("all complete baseline cases remain exactly 31,237", (
            snapshot["full_case_denominator"] == 31_237
            and snapshot["baseline_passed"] == 31_237
            and sum(SUITE_COUNTS) == 31_237
        ))
        accept("all 13 frozen compatibility categories remain distinct", (
            snapshot["suite_count"] == 13
            and snapshot["suite_ids"] == list(SUITE_IDS)
            and len(set(snapshot["suite_ids"])) == 13
        ))
        accept("all six independent candidate families stay visibly separate", (
            snapshot["families"] == list(FAMILY_NAMES)
            and len(snapshot["families"]) == 7
        ))
        accept("all complete current candidate source owners are authenticated", (
            snapshot["all_current_source_owners_authenticated"] is True
            and snapshot["current_source_owner_count"] == 25
        ))
        accept("actual candidate qualification remains zero", (
            snapshot["qualified_candidate_count"] == 0
            and snapshot["candidate_correctness"] == "NOT MEASURED"
        ))
        for family in ("rust", "c", "zig"):
            build = snapshot["candidate_builds"][family]
            accept(
                family + " preserved actual two-source-build status",
                build["build_status"] == (
                    ZIG_V3_SUCCESS["build_status"] if family == "zig"
                    else BUILD_PINS[family]["build_status"]
                )
                and build["fresh_build_count"] == 2
                and build["actual_compiler_process_count"]
                == BUILD_PINS[family]["process_count"],
            )
            accept(
                family + " no regex-package or cross-family dependency",
                build["external_regex_dependency_count"] == 0
                and build["cross_candidate_dependency_count"] == 0,
            )
            accept(
                family + " full compatibility is not implied by build evidence",
                build["candidate_correctness"] == "NOT MEASURED"
                and build["performance"] == "NOT MEASURED",
            )
        accept("current corrected Zig engine and bridge both reproduce", (
            snapshot["candidate_builds"]["zig"]["zig_bridge_reproduces"] is True
            and snapshot["candidate_builds"]["zig"]["zig_engine_reproduces"] is True
            and snapshot["candidate_builds"]["zig"]["compiler_strip_count_per_engine"] == 1
        ))
        accept("preserve the genuine earlier Zig nonreproducibility failure", (
            snapshot["historical_zig_build"]["build_status"] == "FAIL"
            and snapshot["historical_zig_build"]["zig_engine_reproduces"] is False
        ))
        accept("all four genuine native source builds reproduce", (
            snapshot["reproducible_native_family_count"] == 4
            and all(snapshot["candidate_builds"][name]["build_status"] == "PASS"
                    for name in ("rust", "c", "zig", "cpp"))
        ))
        accept("source-only Go and Fortran are never represented as built", (
            snapshot["cpp_build_status"] == "PASS"
            and snapshot["cpp_matching_test_status"] == "NOT MEASURED"
            and snapshot["cpp_candidate_qualified"] is False
            and snapshot["cpp_activation_status"] == "NOT RUN; NO FROZEN V3 ACTIVATION"
            and snapshot["go_build_status"] == "NOT MEASURED"
            and snapshot["fortran_build_status"]
                == "SOURCE ONLY; NOT BUILT; NOT TESTED; NOT QUALIFIED"
            and snapshot["fortran_frozen_v1_independence_audit_coverage"] is False
            and snapshot["fortran_frozen_v5_candidate_gate_coverage"] is False
            and snapshot["fortran_case_executions"] == 0
        ))
        accept("actual Rust has exactly eight verified passing and five failing groups", (
            snapshot["rust_full_gate"]["gate_status"] == "FAIL"
            and snapshot["rust_full_gate"]["failed_before_candidate_execution"] is False
            and snapshot["rust_full_gate"]["actual_failed_worker_count"] == 1
            and snapshot["rust_full_gate"]["qualified_candidate_case_executions"] == 0
            and snapshot["rust_full_gate"]["verified_passing_case_executions"] == 7_461
            and snapshot["rust_full_gate"]["completed_passing_suite_count"] == 8
            and snapshot["rust_full_gate"]["failed_suite_ids"]
                == list(FAILED_RUST_V5_SUITES)
            and "pep688_v4" not in snapshot["rust_full_gate"]["failed_suite_ids"]
            and snapshot["rust_full_gate"]["failed_suite_case_execution_count"]
                == "NOT RECORDED"
            and snapshot["rust_full_gate"]["supplemental_interpreter_check"] == "NOT RUN"
            and snapshot["rust_full_gate"]["full_case_denominator"] == DENOMINATOR
        ))
        accept("the authentic Rust inner fits only the explicit bounded 32 MiB decoder", (
            MAX_DOCUMENT_BYTES == 32 * 1_048_576
            and 16 * 1_048_576 < RUST_GATE_V5_INNER["uncompressed_bytes"]
                < MAX_DOCUMENT_BYTES
            and RUST_GATE_V5_INNER["uncompressed_bytes"] == 16_834_434
        ))
        accept("actual C has exactly seven verified passing and six failing groups", (
            snapshot["c_full_gate"]["gate_status"] == "FAIL"
            and snapshot["c_full_gate"]["failed_before_candidate_execution"] is False
            and snapshot["c_full_gate"]["actual_failed_worker_count"] == 1
            and snapshot["c_full_gate"]["qualified_candidate_case_executions"] == 0
            and snapshot["c_full_gate"]["verified_passing_case_executions"] == 7_197
            and snapshot["c_full_gate"]["completed_passing_suite_count"] == 7
            and snapshot["c_full_gate"]["failed_suite_ids"] == list(FAILED_C_V5_SUITES)
            and snapshot["c_full_gate"]["failed_suite_case_execution_count"] == "NOT RECORDED"
            and snapshot["c_full_gate"]["supplemental_interpreter_check"] == "NOT RUN"
            and snapshot["c_full_gate"]["full_case_denominator"] == DENOMINATOR
        ))
        accept("preserve genuine previous failed full C worker", (
            snapshot["historical_c_v4_full_gate"]["gate_status"] == "FAIL"
            and snapshot["historical_c_v4_full_gate"]["failed_before_candidate_execution"]
                is False
            and snapshot["historical_c_v4_full_gate"]["actual_failed_worker_count"] == 1
            and snapshot["historical_c_v4_full_gate"]["qualified_candidate_case_executions"]
                == 0
        ))
        accept("preserve the distinct historical zero-case C preflight failure", (
            snapshot["historical_c_full_gate"]["gate_status"] == "FAIL"
            and snapshot["historical_c_full_gate"]["failed_before_candidate_execution"] is True
            and snapshot["historical_c_full_gate"]["qualified_candidate_case_executions"] == 0
        ))
        accept("graph is accessible and visibly distinguishes pending results", (
            b'role="img"' in svg
            and b"<title " in svg
            and b"<desc " in svg
            and b"31,237 / 31,237" in svg
            and b"NOT MEASURED" in svg
            and b"SOURCE ONLY; NOT BUILT; NOT TESTED; NOT QUALIFIED" in svg
            and b"Fortran is source only: outside the frozen independence audit" in svg
            and b"7,461 / 31,237 checked successfully" in svg
            and b"five test groups failed" in svg
            and b"7,197 / 31,237 checked successfully" in svg
            and b"six test groups failed" in svg
            and b"FAILED; NOT QUALIFIED" in svg
            and b"3,583 / 31,237 verified" in svg
            and b"1,764 matching differences" in svg
            and b"385 real interpreter calls" in svg
            and b"BUILT; MATCHING NOT MEASURED" in svg
            and b"Two reproducible source builds" in svg
            and b"not activated, tested, or qualified" in svg
            and b"identical engine and bridge" in svg
            and b"both earlier C failures" in svg
            and b"4,194,304 final examples: NOT GENERATED and NOT OPENED" in svg
        ))
        accept("large chart preserves readable candidate labels", (
            b'width="1600"' in svg
            and b'height="1800"' in svg
            and all(
                DISPLAY_NAMES[name].encode("ascii") in svg
                for name in FAMILY_NAMES
            )
        ))
        accept("speed target is explicitly a goal and not a result", (
            b"1.5x goal" in svg
            and b"not an observation" in svg
            and b"REFERENCE ONLY - NOT TIMED" in svg
            and b"1.0x reference (not timed)" in svg
            and snapshot["performance"] == "NOT MEASURED"
        ))
        accept("final holdout remains sealed", (
            snapshot["final_holdout_opened"] is False
            and snapshot["hidden_cases_read"] == 0
            and snapshot["winner_selected"] is False
        ))
        accept("generated summary binds the exact source, inputs, and graph", (
            decoded_summary["source"]["sha256"] == source_hash
            and decoded_summary["inputs"]["sha256"] == manifest_hash
            and decoded_summary["svg"]["sha256"] == sha256(svg)
            and decoded_summary["snapshot"] == snapshot
        ))
        accept("canonical outputs render deterministically without time", (
            (svg, summary)
            == graph_documents(manifest, source_hash, manifest_hash, snapshot)
        ))
        pretty_inventory = (
            json.dumps(inventory, ensure_ascii=True, allow_nan=False, indent=2)
            + "\n"
        ).encode("ascii")
        accept(
            "preserve the exact hash-pinned pretty-printed frozen V3 inventory",
            decode_document(
                pretty_inventory,
                "synthetic exact pinned pretty V3",
                require_canonical=False,
            )
            == inventory,
        )
        reject(
            "reject pretty JSON when canonical chart evidence is required",
            lambda: decode_document(pretty_inventory, "unapproved pretty evidence"),
        )

        def bad_manifest(
            label: str, mutation: Callable[[dict[str, Any]], None]
        ) -> None:
            changed = copy.deepcopy(manifest)
            mutation(changed)
            reject(
                label,
                lambda: validate_snapshot(
                    changed,
                    source_hash,
                    go_bridge_sha,
                    source_loader,
                    document_loader,
                    synthetic_digest,
                ),
            )

        bad_manifest(
            "reject silently reduced 31,237-case graph denominator",
            lambda value: value.update({"full_case_denominator": 2_807}),
        )
        bad_manifest(
            "reject silently expanded compatibility denominator",
            lambda value: value.update({"full_case_denominator": 31_365}),
        )
        bad_manifest(
            "reject an omitted frozen suite",
            lambda value: value.update({"suite_count": 12}),
        )
        bad_manifest(
            "reject an invented extra candidate family",
            lambda value: value["candidate_families"].append("fortran"),
        )
        bad_manifest(
            "reject an omitted candidate family",
            lambda value: value["families"].pop(),
        )
        bad_manifest(
            "reject candidates reordered to conceal a loss",
            lambda value: value["families"].reverse(),
        )
        bad_manifest(
            "reject a forged Python version",
            lambda value: value.update({"python": "3.14.5"}),
        )
        bad_manifest(
            "reject an invented candidate correctness pass",
            lambda value: value["families"][1].update({"correctness": "PASS"}),
        )
        bad_manifest(
            "reject an invented candidate speed",
            lambda value: value["families"][1].update({"performance": "1.5x"}),
        )
        bad_manifest(
            "reject relabelled historical Zig failure as a successful build",
            lambda value: value["families"][3]["historical_build_evidence"].update(
                {"expected_build_status": "PASS"}
            ),
        )
        bad_manifest(
            "reject relabelled corrected Zig success as a failed build",
            lambda value: value["families"][3]["build_evidence"].update(
                {"expected_build_status": "FAIL"}
            ),
        )
        bad_manifest(
            "reject concealed actual C preflight failure",
            lambda value: value["families"][2].update({
                "correctness_evidence": None
            }),
        )
        bad_manifest(
            "reject falsely successful C preflight",
            lambda value: value["families"][2]["correctness_evidence"].update({
                "expected_gate_status": "PASS"
            }),
        )
        bad_manifest(
            "reject invented executed C full-suite case",
            lambda value: value["families"][2]["correctness_evidence"].update({
                "qualified_case_executions": 1
            }),
        )
        bad_manifest(
            "reject omitted Rust source owner",
            lambda value: value["families"][1]["owned_sources"].pop(),
        )
        bad_manifest(
            "reject adapter-only Rust ownership",
            lambda value: value["families"][1].update({
                "owned_sources": [
                    item
                    for item in value["families"][1]["owned_sources"]
                    if item["path"] == "candidates/rust_candidate.py"
                ]
            }),
        )
        bad_manifest(
            "reject historical C source identity",
            lambda value: value["families"][2]["owned_sources"][0].update({
                "sha256":
                    "81ea03632269d3ca758cbe7bbd79ef9c40e75de58335456f9f2b82a66b5740e9"
            }),
        )
        bad_manifest(
            "reject historical Zig adapter identity",
            lambda value: value["families"][3]["owned_sources"][2].update({
                "sha256":
                    "03a3312833252ef0a0c84df0e7e375c89b115ad772ccdd72faa51fc563950435"
            }),
        )
        bad_manifest(
            "reject historical Rust bridge identity",
            lambda value: value["families"][1]["owned_sources"][3].update({
                "sha256":
                    "ab0ef168f5ac22242949da58eaf2693fd2f0baf4520aaff5bd34a413cad653fc"
            }),
        )
        for name in CORE_PINS:
            bad_manifest(
                "reject substituted frozen core: " + name,
                lambda value, name=name: value["frozen_inputs"][name].update({
                    "sha256":
                        hashlib.sha256(("foreign-" + name).encode("ascii")).hexdigest()
                }),
            )
        for family_index, family in enumerate(FAMILY_NAMES[1:], start=1):
            owners = manifest["families"][family_index]["owned_sources"]
            for source_index, source in enumerate(owners):
                bad_manifest(
                    "reject substituted current owner: " + source["path"],
                    lambda value, family_index=family_index, source_index=source_index:
                        value["families"][family_index]["owned_sources"][
                            source_index
                        ].update({
                            "sha256": hashlib.sha256(
                                ("foreign-owner-" + str(family_index)
                                 + "-" + str(source_index)).encode("ascii")
                            ).hexdigest()
                        }),
                )
        for name in manifest["boundaries"]:
            original = manifest["boundaries"][name]
            changed_value: Any
            if type(original) is bool:
                changed_value = not original
            elif type(original) is int:
                changed_value = original + 1
            else:
                changed_value = "MEASURED"
            bad_manifest(
                "reject unsafe visible graph boundary: " + name,
                lambda value, name=name, changed_value=changed_value:
                    value["boundaries"].update({name: changed_value}),
            )

        def bad_baseline(
            name: str, mutation: Callable[[dict[str, Any]], None]
        ) -> None:
            changed = copy.deepcopy(baseline)
            mutation(changed)
            reject(name, lambda: validate_baseline(changed))

        bad_baseline(
            "reject omitted baseline category",
            lambda value: value["suites"].pop(),
        )
        bad_baseline(
            "reject baseline suite ordering attack",
            lambda value: value["suites"].reverse(),
        )
        bad_baseline(
            "reject hidden baseline category failure",
            lambda value: value["suites"][3]["baseline"].update({"status": "FAIL"}),
        )
        bad_baseline(
            "reject per-category silent denominator change",
            lambda value: value["suites"][3].update({"case_execution_count": 767}),
        )
        bad_baseline(
            "reject false baseline speed claim",
            lambda value: value["suites"][4].update({"performance": "MEASURED"}),
        )
        bad_baseline(
            "reject inflated supplemental interpreter denominator",
            lambda value: value["denominator"].update({
                "final_required_case_execution_denominator": 31_365
            }),
        )
        bad_baseline(
            "reject missing actual debug skip",
            lambda value: value["denominator"].update({
                "public_original_skip_cases_outside_runnable_denominator": 0
            }),
        )
        bad_baseline(
            "reject silently changed private waiver count",
            lambda value: value["denominator"].update({
                "private_upstream_methods_outside_public_denominator": 0
            }),
        )
        bad_baseline(
            "reject hidden final holdout authorization",
            lambda value: value["phase_gate"].update({
                "final_holdout_authorized": True
            }),
        )
        bad_baseline(
            "reject unauthorized actual candidate evaluation",
            lambda value: value["phase_gate"].update({
                "candidate_evaluation_authorized": True
            }),
        )
        for suite_index, expected_id in enumerate(SUITE_IDS):
            bad_baseline(
                "reject concealed frozen suite: " + expected_id,
                lambda value, suite_index=suite_index:
                    value["suites"][suite_index].update({"id": "concealed-suite"}),
            )

        def bad_inventory(
            name: str, mutation: Callable[[dict[str, Any]], None]
        ) -> None:
            changed = copy.deepcopy(inventory)
            mutation(changed)
            reject(name, lambda: validate_candidate_inventory(changed))

        bad_inventory(
            "reject candidate gate falsely marked complete",
            lambda value: value.update({"status": "PASS"}),
        )
        bad_inventory(
            "reject forged full candidate pass",
            lambda value: value.update({"candidate_results": "PASS"}),
        )
        bad_inventory(
            "reject the stale draft V3 inventory",
            lambda value: value["phase1"].update({
                "inventory_sha256":
                    "f2e1dcd077b11a450556935b30eed4de886c9123980ec0abade67934fc3daf04"
            }),
        )
        for boundary in (
            "stdlib_candidate_delegation_allowed",
            "cross_candidate_delegation_allowed",
            "external_regex_package_allowed",
            "timing_allowed",
            "hidden_case_access_allowed",
            "final_holdout_authorized",
            "final_holdout_opened",
            "final_winner_selected",
        ):
            bad_inventory(
                "reject weakened candidate boundary: " + boundary,
                lambda value, boundary=boundary:
                    value["boundaries"].update({boundary: True}),
            )

        def bad_build(
            family: str,
            name: str,
            target: str,
            mutation: Callable[[dict[str, Any]], None],
        ) -> None:
            receipt, report = synthetic_build(family)
            build = BUILD_PINS[family]
            compressed = docs[build["archive"][0]][1]
            expanded = docs[build["archive"][0]][2]
            changed = receipt if target == "receipt" else report
            mutation(changed)
            reject(
                family + ": " + name,
                lambda: validate_build(
                    family,
                    receipt,
                    report,
                    compressed,
                    expanded,
                    synthetic_digest,
                ),
            )

        for family in ("rust", "c", "zig"):
            bad_build(
                family,
                "reject false durable receipt publication",
                "receipt",
                lambda value: value.update({"status": "FAIL"}),
            )
            bad_build(
                family,
                "reject forged build status",
                "receipt",
                lambda value, family=family: value.update({
                    "build_status":
                        "FAIL" if BUILD_PINS[family]["build_status"] == "PASS"
                        else "PASS"
                }),
            )
            bad_build(
                family,
                "reject missing current source owner",
                "receipt",
                lambda value: value["owned_source_sha256"].pop(
                    next(iter(value["owned_source_sha256"]))
                ),
            )
            bad_build(
                family,
                "reject false complete candidate correctness",
                "receipt",
                lambda value: value.update({"candidate_correctness": "PASS"}),
            )
            bad_build(
                family,
                "reject invented current candidate speed",
                "receipt",
                lambda value: value.update({"performance": "FASTER"}),
            )
            for field in ZERO_FIELDS:
                bad_build(
                    family,
                    "reject receipt external effect: " + field,
                    "receipt",
                    lambda value, field=field: value.update({field: 1}),
                )
                bad_build(
                    family,
                    "reject archive external effect: " + field,
                    "report",
                    lambda value, field=field: value.update({field: 1}),
                )
            bad_build(
                family,
                "reject omitted genuine compiler process",
                "report",
                lambda value: value["processes"].pop(),
            )
            bad_build(
                family,
                "reject unsuccessful genuine compiler process",
                "report",
                lambda value: value["processes"][0].update({"exit_status": 1}),
            )
            bad_build(
                family,
                "reject shell-interpreted compiler invocation",
                "report",
                lambda value: value["processes"][0].update({"shell": True}),
            )
            bad_build(
                family,
                "reject clipped genuine compiler stdout",
                "report",
                lambda value: value["processes"][0].update({"stdout_bytes": 1}),
            )
            bad_build(
                family,
                "reject clipped genuine compiler stderr",
                "report",
                lambda value: value["processes"][0].update({"stderr_bytes": 1}),
            )
            bad_build(
                family,
                "reject source owner changed after genuine build",
                "report",
                lambda value: next(iter(
                    value["owned_source_after"].values()
                )).update({"inode": 99_999}),
            )
            bad_build(
                family,
                "reject reused independently fresh source directory",
                "report",
                lambda value: value["build_phases"][1].update({
                    "fresh_source_directory":
                        "<FRESH_PRIVATE_TMP>/reference-a/source"
                }),
            )
            bad_build(
                family,
                "reject reused independently fresh native directory",
                "report",
                lambda value: value["build_phases"][1].update({
                    "fresh_native_directory":
                        "<FRESH_PRIVATE_TMP>/reference-a/native"
                }),
            )
            bad_build(
                family,
                "reject falsely fsynced temporary source copies",
                "report",
                lambda value: next(iter(
                    value["build_phases"][0]["copied_source_owners"].values()
                )).update({"file_fsync_completed": True}),
            )
            bad_build(
                family,
                "reject source-copy same-inode verification removed",
                "report",
                lambda value: next(iter(
                    value["build_phases"][0]["copied_source_owners"].values()
                )).update({"same_inode_readback_verified": False}),
            )
            bad_build(
                family,
                "reject concealed source-build network access",
                "report",
                lambda value: value.update({"network_requests": 1}),
            )
            bad_build(
                family,
                "reject omitted fresh native build phase",
                "report",
                lambda value: value["build_phases"].pop(),
            )
            bad_build(
                family,
                "reject external regex-engine dependency",
                "report",
                lambda value: next(iter(
                    value["build_phases"][0]["native_outputs"].values()
                ))["elf"].update({"external_regex_dependency_count": 1}),
            )
            bad_build(
                family,
                "reject cross-candidate engine delegation",
                "report",
                lambda value: next(iter(
                    value["build_phases"][0]["native_outputs"].values()
                ))["elf"].update({"cross_family_dependency_count": 1}),
            )
        bad_build(
            "zig",
            "reject interpreting a successful publication as a successful build",
            "report",
            lambda value: value.update({"status": "PASS", "error": None}),
        )
        bad_build(
            "zig",
            "reject forged equal Zig engine bytes",
            "report",
            lambda value: value["build_phases"][1]["native_outputs"]["engine"].update({
                "sha256":
                    BUILD_PINS["zig"]["outputs"]["engine_reference_a"][0]
            }),
        )
        bad_build(
            "zig",
            "reject false Zig compiler failure",
            "report",
            lambda value: value["build_phases"].pop(),
        )
        bad_build(
            "zig",
            "reject false Zig bridge nonreproducibility",
            "report",
            lambda value: value["build_phases"][1]["native_outputs"]["bridge"].update({
                "sha256":
                    BUILD_PINS["zig"]["outputs"]["engine_reference_b"][0]
            }),
        )
        for family in ("rust", "c"):
            bad_build(
                family,
                "reject false byte-identical reproduction",
                "report",
                lambda value: value["reproducibility"].update({
                    "byte_identical": False
                }),
            )

        def bad_c_gate(
            name: str,
            target: str,
            mutation: Callable[[dict[str, Any]], None],
        ) -> None:
            receipt, report = synthetic_c_gate_failure()
            compressed = docs[C_GATE_FAILURE["archive"][0]][1]
            expanded = docs[C_GATE_FAILURE["archive"][0]][2]
            mutation(receipt if target == "receipt" else report)
            reject(
                "C full-test preflight: " + name,
                lambda: validate_c_gate_failure(
                    receipt, report, compressed, expanded, synthetic_digest
                ),
            )

        bad_c_gate(
            "reject a published failure represented as a candidate pass",
            "receipt",
            lambda value: value.update({"candidate_status": "PASS"}),
        )
        bad_c_gate(
            "reject omitted authentic C failure preservation",
            "receipt",
            lambda value: value.update({"failure_preserved": False}),
        )
        bad_c_gate(
            "reject false C gate success",
            "report",
            lambda value: value.update({"status": "PASS"}),
        )
        bad_c_gate(
            "reject invented executed C correctness case",
            "report",
            lambda value: value.update({"qualified_candidate_case_executions": 1}),
        )
        bad_c_gate(
            "reject hidden actual C reference worker",
            "report",
            lambda value: value.update({"actual_reference_workers_started": 1}),
        )
        bad_c_gate(
            "reject incorrect C activation preflight failure",
            "report",
            lambda value: value["failure"].update({
                "message": "invented candidate regex mismatch"
            }),
        )
        bad_c_gate(
            "reject omitted complete C failure traceback",
            "report",
            lambda value: value["failure"].update({"traceback": []}),
        )
        bad_c_gate(
            "reject supplemental cases inflated into full denominator",
            "report",
            lambda value: value.update({
                "supplemental_cases_added_to_original_denominator": True
            }),
        )
        def bad_v5_gate(name: str, target: str,
                        mutate: Callable[[dict[str, Any]], None]) -> None:
            a_receipt, a_report, i_receipt, i_report = synthetic_c_gate_v5_failure()
            selected = {
                "outer_receipt": a_receipt, "outer": a_report,
                "inner_receipt": i_receipt, "inner": i_report,
            }
            mutate(selected[target])
            reject(
                "actual V5 C suites: " + name,
                lambda: validate_c_gate_v5_failure(
                    a_receipt, a_report,
                    docs[C_GATE_V5_OUTER["archive"][0]][1],
                    docs[C_GATE_V5_OUTER["archive"][0]][2],
                    i_receipt, i_report,
                    docs[C_GATE_V5_INNER["archive"][0]][1],
                    docs[C_GATE_V5_INNER["archive"][0]][2],
                    synthetic_digest,
                ),
            )

        for field in ("status", "candidate_status", "candidate_family", "label",
                      "source_sha256", "protocol_sha256", "document_sha256",
                      "uncompressed_sha256"):
            for role in ("outer_receipt", "inner_receipt"):
                bad_v5_gate(
                    "reject forged " + role + " " + field, role,
                    lambda value, field=field: value.update({
                        field: "PASS" if field == "candidate_status" else "FORGED"
                    }),
                )
        bad_v5_gate("reject durable PASS confused with candidate PASS", "outer",
                    lambda v: v.update({"status": "PASS"}))
        bad_v5_gate("reject falsely labeled absent worker", "outer",
                    lambda v: v.update({"failed_worker_process": None}))
        bad_v5_gate("reject hidden 7,197 verified passes", "inner",
                    lambda v: v.update({"qualified_candidate_case_executions": 0}))
        bad_v5_gate("reject invented 31,237 executed candidate cases", "inner",
                    lambda v: v.update({"qualified_candidate_case_executions": DENOMINATOR}))
        bad_v5_gate("reject forged passing candidate", "inner",
                    lambda v: v.update({"status": "PASS", "candidate_qualified": True}))
        bad_v5_gate("reject hidden failed group", "inner",
                    lambda v: v["all_suites"].pop())
        bad_v5_gate("reject reordered actual groups", "inner",
                    lambda v: v["all_suites"].reverse())
        bad_v5_gate("reject fabricated failed-group executed cases", "inner",
                    lambda v: v["all_suites"][6].update({
                        "actual_candidate_case_count": 6_912
                    }))
        bad_v5_gate("reject stripped actual failure traceback", "inner",
                    lambda v: v["all_suites"][6]["failure"].update({"traceback": []}))
        bad_v5_gate("reject omitted exact independent C owner", "inner",
                    lambda v: v["complete_owned_source_sha256"].pop(
                        "candidates/_vm_native.c"
                    ))
        bad_v5_gate("reject fabricated supplemental interpreter run", "outer",
                    lambda v: v.update({"supplemental_subinterpreter_case_count": 128}))
        bad_v5_gate("reject concealed previous C preflight", "outer",
                    lambda v: v["preserved_v3_actual_failure"].update({"status": "FAIL"}))
        bad_v5_gate("reject concealed previous C worker failure", "outer",
                    lambda v: v["preserved_v4_actual_failure"].update({"status": "FAIL"}))
        bad_v5_gate("reject hidden C benchmark", "inner",
                    lambda v: v.update({"timing_trials_run": 1}))
        bad_v5_gate("reject opened hidden cases", "inner",
                    lambda v: v.update({"hidden_cases_read": 1}))
        bad_v5_gate("reject claiming groups are individual mismatch counts", "inner",
                    lambda v: v["all_failure_reasons"].pop())

        def bad_rust_v5_gate(
            name: str, target: str,
            mutation: Callable[[dict[str, Any]], None],
        ) -> None:
            a_receipt, a_report, i_receipt, i_report = synthetic_rust_gate_v5_failure()
            selected = {
                "outer_receipt": a_receipt, "outer": a_report,
                "inner_receipt": i_receipt, "inner": i_report,
            }
            mutation(selected[target])
            reject(
                "actual V5 Rust suites: " + name,
                lambda: validate_rust_gate_v5_failure(
                    a_receipt, a_report,
                    docs[RUST_GATE_V5_OUTER["archive"][0]][1],
                    docs[RUST_GATE_V5_OUTER["archive"][0]][2],
                    i_receipt, i_report,
                    docs[RUST_GATE_V5_INNER["archive"][0]][1],
                    docs[RUST_GATE_V5_INNER["archive"][0]][2],
                    synthetic_digest,
                ),
            )

        for field in ("status", "candidate_status", "candidate_family", "label",
                      "source_sha256", "protocol_sha256", "document_sha256",
                      "uncompressed_sha256"):
            for role in ("outer_receipt", "inner_receipt"):
                bad_rust_v5_gate(
                    "reject forged " + role + " " + field, role,
                    lambda value, field=field: value.update({
                        field: "PASS" if field == "candidate_status" else "FORGED"
                    }),
                )
        bad_rust_v5_gate("reject durable receipt confused with Rust PASS", "outer",
                         lambda x: x.update({"status": "PASS"}))
        bad_rust_v5_gate("reject omitting an actual Rust worker", "outer",
                         lambda x: x.update({"failed_worker_process": None}))
        bad_rust_v5_gate("reject invented Rust 31,237 actual executions", "inner",
                         lambda x: x.update({
                             "qualified_candidate_case_executions": DENOMINATOR
                         }))
        bad_rust_v5_gate("reject Rust PEP688 falsely labelled FAIL", "inner",
                         lambda x: x["all_suites"][11].update({"status": "FAIL"}))
        bad_rust_v5_gate("reject fabricated nested interpreter executions", "inner",
                         lambda x: x["all_suites"][10].update({
                             "actual_candidate_case_count": 128
                         }))
        bad_rust_v5_gate("reject hiding an actual Rust failed group", "inner",
                         lambda x: x["all_suites"].pop())
        bad_rust_v5_gate("reject claiming five failed groups are mismatches", "inner",
                         lambda x: x["all_failure_reasons"].pop())
        bad_rust_v5_gate("reject false Rust full qualification", "inner",
                         lambda x: x.update({"candidate_qualified": True}))
        bad_rust_v5_gate("reject falsely executed supplemental interpreter", "outer",
                         lambda x: x.update({
                             "supplemental_subinterpreter_case_count": 128
                         }))
        bad_rust_v5_gate("reject missing independent Rust source owner", "inner",
                         lambda x: x["complete_owned_source_sha256"].pop(
                             "candidates/rust/src/lib.rs"
                         ))
        bad_rust_v5_gate("reject Rust hidden final case access", "inner",
                         lambda x: x.update({"hidden_cases_read": 1}))
        bad_rust_v5_gate("reject unauthorized Rust timing", "inner",
                         lambda x: x.update({"timing_trials_run": 1}))

        for role in ("archive", "receipt"):
            bad_manifest(
                "reject replaced actual C++ source-build " + role,
                lambda value, role=role: value["families"][4]["build_evidence"][
                    role].update({"sha256": hashlib.sha256(
                        ("forged-v4-cpp-" + role).encode("ascii")).hexdigest()}),
            )
        for field, false_value in (
            ("expected_build_status", "FAIL"),
            ("fresh_source_build_count", 1),
            ("actual_compiler_process_count", 9),
            ("bridge_sha256", "f" * 64),
            ("bridge_size_bytes", 130_743),
            ("matching_test_status", "PASS"),
            ("activation_status", "ACTIVATED"),
            ("qualified", True),
        ):
            bad_manifest(
                "reject false C++ source build or matching claim: " + field,
                lambda value, field=field, false_value=false_value:
                    value["families"][4]["build_evidence"].update(
                        {field: false_value}
                    ),
            )
        for field, false_value in (
            ("correctness", "PASS"),
            ("build_status", "FAIL"),
            ("source_build_version", 3),
            ("fresh_source_build_count", 1),
            ("matching_test_status", "PASS"),
            ("activation_status", "ACTIVATED"),
            ("undefined_behavior", "PASS"),
            ("qualified", True),
            ("native_libraries_loaded", 1),
        ):
            bad_manifest(
                "reject fabricated C++ activation or qualification: " + field,
                lambda value, field=field, false_value=false_value:
                    value["families"][4].update({field: false_value}),
            )

        def reject_cpp_evidence(
            name: str, target: str,
            mutation: Callable[[dict[str, Any]], None],
        ) -> None:
            receipt, report, compressed, expanded, synthetic_digest = (
                _v9_synthetic_cpp_build()
            )
            mutation(receipt if target == "receipt" else report)
            reject(
                "authentic C++ V4 source build: " + name,
                lambda: _v9_validate_cpp_build(
                    receipt, report, compressed, expanded, synthetic_digest
                ),
            )

        for field, invalid in (
            ("status", "FAIL"), ("build_status", "FAIL"),
            ("family", "zig"), ("label", "phase2-v3"),
            ("source_sha256", "f" * 64),
            ("protocol_sha256", "f" * 64),
            ("contract_sha256", "f" * 64),
            ("phase1_manifest_sha256", "f" * 64),
            ("archive_sha256", "f" * 64),
            ("archive_bytes", 20_604),
            ("uncompressed_sha256", "f" * 64),
            ("uncompressed_bytes", 175_103),
            ("candidate_correctness", "PASS"),
            ("native_libraries_loaded", 1),
            ("performance", "MEASURED"),
            ("hidden_cases_read", 1),
            ("timing_trials_run", 1),
        ):
            reject_cpp_evidence(
                "reject forged receipt " + field, "receipt",
                lambda value, field=field, invalid=invalid:
                    value.update({field: invalid}),
            )
        for field, invalid in (
            ("status", "FAIL"), ("version", 3),
            ("family", "zig"), ("label", "phase2-v3"),
            ("candidate_correctness", "PASS"),
            ("native_libraries_loaded", 1),
            ("network_requests", 1),
            ("reference_processes_started", 1),
            ("final_cases_read", 1),
            ("performance", "FASTER"),
            ("hidden_cases_read", 1),
            ("timing_trials_run", 1),
        ):
            reject_cpp_evidence(
                "reject forged complete source report " + field, "report",
                lambda value, field=field, invalid=invalid:
                    value.update({field: invalid}),
            )
        reject_cpp_evidence(
            "reject a missing authentic compiler stream", "report",
            lambda value: value["processes"].pop(),
        )
        reject_cpp_evidence(
            "reject an invented successful compiler process", "report",
            lambda value: value["processes"][2].update({"exit_status": 1}),
        )
        reject_cpp_evidence(
            "reject shell-interpreted compiler execution", "report",
            lambda value: value["processes"][2].update({"shell": True}),
        )
        reject_cpp_evidence(
            "reject a truncated readelf symbol stream", "report",
            lambda value: value["processes"][4].update({"stdout_bytes": 0}),
        )
        reject_cpp_evidence(
            "reject a reused fresh source phase", "report",
            lambda value: value["build_phases"][1].update({
                "fresh_source_directory": "<FRESH_PRIVATE_TMP>/reference-a/source"
            }),
        )
        reject_cpp_evidence(
            "reject a reused actual C++ bridge inode", "report",
            lambda value: value["build_phases"][1]["native_outputs"][
                "bridge"].update({
                    "inode": value["build_phases"][0]["native_outputs"][
                        "bridge"]["inode"]
                }),
        )
        reject_cpp_evidence(
            "reject a non-reproducible C++ bridge", "report",
            lambda value: value["reproducibility"].update({"byte_identical": False}),
        )
        reject_cpp_evidence(
            "reject an externally delegated regex engine", "report",
            lambda value: value["build_phases"][0]["native_outputs"][
                "bridge"]["audit"].update({"external_regex_dependency_count": 1}),
        )
        reject_cpp_evidence(
            "reject a cross-family C++ matcher", "report",
            lambda value: value["build_phases"][0]["native_outputs"][
                "bridge"]["audit"].update({"cross_family_dependency_count": 1}),
        )
        for group in ("archive", "receipt", "worker_archive", "worker_receipt"):
            bad_manifest(
                "reject substituted complete Zig full-gate evidence: " + group,
                lambda value, group=group: value["families"][3]["correctness_evidence"][
                    group].update({"sha256": hashlib.sha256(
                        ("forged-zig-" + group).encode("ascii")).hexdigest()}),
            )
        bad_manifest(
            "reject falsely qualified actual failed Zig candidate",
            lambda value: value["families"][3].update({"correctness": "PASS"}),
        )
        bad_manifest(
            "reject invented Zig complete compatibility",
            lambda value: value["families"][3]["correctness_evidence"].update({
                "qualified_case_executions": DENOMINATOR
            }),
        )
        bad_manifest(
            "reject hidden 1,764 authentic Zig matching differences",
            lambda value: value["families"][3]["correctness_evidence"].update({
                "actual_semantic_mismatch_count": 0
            }),
        )
        bad_manifest(
            "reject fabricated zero-call Zig interpreter cleanup",
            lambda value: value["families"][3]["correctness_evidence"].update({
                "actual_case_interpreter_exec_calls": 0
            }),
        )
        bad_manifest(
            "reject truncated full-width interpreter replay seed",
            lambda value: value["families"][3]["correctness_evidence"].update({
                "active_cleanup_case_seed": 16_650_482_535_507_370_000
            }),
        )
        bad_manifest(
            "reject unsafe 32 MiB specialist truncation",
            lambda value: value["families"][3]["correctness_evidence"].update({
                "specialist_maximum_uncompressed_bytes": 32 * 1_048_576
            }),
        )
        for index, owner in enumerate(manifest["families"][3]["subordinate_evidence"]):
            bad_manifest(
                "reject omitted authentic Zig nested or specialist owner: "
                + owner["path"],
                lambda value, index=index:
                    value["families"][3]["subordinate_evidence"].pop(index),
            )
        bad_manifest(
            "reject invented Fortran frozen independence audit inclusion",
            lambda value: value["families"][6].update({
                "included_in_frozen_v1_independence_audit": True
            }),
        )
        bad_manifest(
            "reject invented Fortran frozen candidate gate inclusion",
            lambda value: value["families"][6].update({
                "included_in_frozen_v5_candidate_gate": True
            }),
        )
        bad_manifest(
            "reject invented Fortran native build",
            lambda value: value["families"][6].update({"build_status": "PASS"}),
        )
        bad_manifest(
            "reject invented Fortran matching test",
            lambda value: value["families"][6].update({"matching_test_status": "PASS"}),
        )
        bad_manifest(
            "reject invented Fortran full qualification",
            lambda value: value["families"][6].update({"qualified": True}),
        )
        bad_manifest(
            "reject omitted independent Fortran matching engine",
            lambda value: value["families"][6]["owned_sources"].pop(),
        )
        bad_manifest(
            "reject false source-only independence-audit boundary",
            lambda value: value["source_only_architecture_boundary"].update({
                "included_in_frozen_v1_independence_audit": True
            }),
        )
        bad_manifest(
            "reject falsely executed source-only Fortran case",
            lambda value: value["source_only_architecture_boundary"].update({
                "matching_cases_executed": 1
            }),
        )

        for label, operation in (
            ("reject ordinary filesystem reads", lambda: builtins.open("forbidden")),
            ("reject descriptor filesystem reads", lambda: os.open("forbidden", 0)),
            ("reject filesystem metadata access", lambda: os.stat("forbidden")),
            ("reject path-based file reads", lambda: Path("forbidden").read_bytes()),
            ("reject graph output writes", lambda: os.write(1, b"forbidden")),
            ("reject graph output replacement", lambda: os.replace("a", "b")),
            (
                "reject direct candidate imports",
                lambda: builtins.__import__("candidates"),
            ),
            (
                "reject dynamic candidate imports",
                lambda: importlib.import_module("candidates"),
            ),
            (
                "reject candidate, oracle, and benchmark subprocesses",
                lambda: subprocess.run(["forbidden"]),
            ),
            (
                "reject background candidate threads",
                lambda: threading.Thread.start(None),
            ),
            ("reject performance clock access", lambda: time.perf_counter()),
            ("reject timed garbage collection", lambda: gc.collect()),
        ):
            reject(label, operation)
        accept(
            "all actual-effect categories are intercepted",
            all(count > 0 for count in effects.values()),
        )
        accept(
            "no candidate module entered the source-only process",
            not any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ),
        )
        require(
            len(rejected) >= 100 and len(accepted) >= 15
            and len(set(accepted + rejected)) == len(accepted) + len(rejected),
            "the graph needs complete, independently named hostile controls",
        )
        result = {
            "schema": SCHEMA + "-source-self-test",
            "status": "PASS",
            "python": PYTHON_VERSION,
            "synthetic_acceptance_count": len(accepted),
            "synthetic_rejection_count": len(rejected),
            "synthetic_acceptances": accepted,
            "synthetic_rejections": rejected,
            "intercepted_side_effects": dict(effects),
            "actual_source_reads": 0,
            "actual_evidence_reads": 0,
            "actual_output_writes": 0,
            "actual_candidate_imports": 0,
            "actual_candidate_processes_started": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance_files_read": 0,
            "hidden_cases_read": 0,
            "final_holdout_opened": False,
            "winner_selected": False,
            "full_case_denominator": DENOMINATOR,
            "suite_count": len(SUITE_IDS),
            "current_source_owner_count": snapshot["current_source_owner_count"],
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "synthetic_svg_sha256": sha256(svg),
            "synthetic_summary_sha256": sha256(summary),
        }
    verify_runtime()
    return result


def main(arguments: list[str] | None = None) -> int:
    verify_runtime()
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--go-bridge-sha256")
    parser.add_argument("--manifest-sha256")
    options = parser.parse_args(arguments)
    if options.self_test:
        require(
            options.source_sha256 is None
            and options.go_bridge_sha256 is None
            and options.manifest_sha256 is None,
            "synthetic self-tests cannot accept or inspect real chart evidence",
        )
        result = self_test()
    else:
        require(
            options.render or options.verify,
            "explicitly select a current-build render or read-only verification",
        )
        require(
            type(options.source_sha256) is str
            and type(options.go_bridge_sha256) is str,
            "explicitly pin the renderer and independently committed Go bridge",
        )
        require(
            not options.verify or type(options.manifest_sha256) is str,
            "read-only reproduction must pin the exact published chart inputs",
        )
        result = render(
            options.source_sha256,
            options.go_bridge_sha256,
            options.manifest_sha256,
            options.verify,
        )
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OverviewError as error:
        sys.stderr.write("current overview rejected: " + str(error) + "\n")
        raise SystemExit(2) from error
