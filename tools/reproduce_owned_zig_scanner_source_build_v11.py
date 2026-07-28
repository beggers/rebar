#!/usr/bin/env python3
"""Freeze a future, two-phase, first-party Zig scanner source build.

``--self-test`` is wholly synthetic and effect-blocked.  ``--verify-context``
only reads independently pinned, already published files.  Neither mode creates
a private directory, applies the scanner repair, starts a compiler, imports a
candidate, opens the holdout, or samples a clock.  Only the separately and
explicitly requested ``--build`` mode may create two fresh private phase trees,
apply the independently frozen scanner overlay, and start the exact 26 frozen
compiler and inspection processes.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import ctypes
import errno
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
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
SOURCE_RELATIVE = "tools/reproduce_owned_zig_scanner_source_build_v11.py"
PROTOCOL_RELATIVE = "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V11.md"
CONTRACT_RELATIVE = "oracle/phase2/zig-scanner-source-build-v11.json"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-owned-zig-scanner-source-build-v11"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
OVERLAY_SCHEMA = "rebar-phase2-owned-zig-scanner-capture-source-repair-v1"
PRIVATE_ROOT_PREFIX = "rebar-phase2-zig-scanner-capture-source-build-v1-"
PHASE_NAMES = ("reference-a", "reference-b")
ENGINE_FILENAME = "_zig_probe.so"
BRIDGE_FILENAME = "_zig_bridge.cpython-314-x86_64-linux-gnu.so"
CANONICAL_SOURCE_PREFIX = "/rebar-phase2-v6-owned-source"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_COMPILER_BYTES = 256 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024
MAX_REPORT_BYTES = 48 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_LABEL_BYTES = 48
EXPECTED_PROCESS_COUNT = 26
EXPECTED_PHASE_PROCESS_COUNT = 13
FINAL_PLANNED_CASE_COUNT = 4_194_304
HISTORICAL_V21_EVIDENCE_OWNER_COUNT = 103
HISTORICAL_V21_REFERENCE_COUNT = 108
ADDITIONAL_RECOVERED_C_EVIDENCE_OWNER_COUNT = 2
HISTORICAL_V22_EVIDENCE_OWNER_COUNT = 105
HISTORICAL_V22_REFERENCE_COUNT = 110
ADDITIONAL_COMPLETED_C_EVIDENCE_OWNER_COUNT = 30
CURRENT_EVIDENCE_OWNER_COUNT = 135
CURRENT_AUTHENTICATED_REFERENCE_COUNT = 140
COMPLETED_C_CAMPAIGN_LABEL = "phase2-v10-live-original-p0"
MAX_COMPLETED_C_EXPANDED_BYTES = 128 * 1024 * 1024
ORIGINAL_C_NATIVE = "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"
ORIGINAL_C_NATIVE_SHA256 = (
    "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd"
)

PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PYTHON_INCLUDE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
)
PINNED_ZIG = "/tmp/zig-x86_64-linux-0.16.0/zig"
PINNED_GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
PINNED_READELF = "/usr/bin/x86_64-linux-gnu-readelf"

OVERLAY_SOURCE = "tools/apply_owned_zig_scanner_capture_source_repair_v1.py"
OVERLAY_PROTOCOL = "oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V1.md"
OVERLAY_CONTRACT = "oracle/phase2/zig-scanner-capture-source-repair-v1.json"
OVERLAY_SOURCE_SHA256 = (
    "963f306373753b9fef84c9a9784668f42067cb905b84347a0bcc99e1e8692515"
)
OVERLAY_PROTOCOL_SHA256 = (
    "7a40b58bcc69744fc6b749368ec307be7d05d742de3d921410fd2753a4f5c8d0"
)
OVERLAY_CONTRACT_SHA256 = (
    "c48fcd9cb40cbe15442c2dd197627d7f4ccc341b3edfbbe0c645405015c8ea87"
)

ORIGINAL_ENGINE = "candidates/zig/mini_regex.zig"
ORIGINAL_BRIDGE = "candidates/zig/py_bridge.c"
ORIGINAL_ADAPTER = "candidates/zig_candidate.py"
ORIGINAL_ENGINE_SHA256 = (
    "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28"
)
ORIGINAL_BRIDGE_SHA256 = (
    "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b"
)
ORIGINAL_ADAPTER_SHA256 = (
    "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862"
)
DERIVED_BRIDGE_SHA256 = (
    "a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148"
)
DERIVED_BRIDGE_BYTES = 173_082

RECOVERED_C_ARCHIVE = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v2-c-phase2-v9-original-p0-failures.json.gz"
)
RECOVERED_C_ARCHIVE_SHA256 = (
    "a37a70f7ab9e4dcc72b176ca51fb1bfe8514d906431e8f02f269871a8b946810"
)
RECOVERED_C_RECEIPT = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v2-c-"
    "phase2-v9-original-p0-failures-publication-receipt.json"
)
RECOVERED_C_RECEIPT_SHA256 = (
    "8a16520de9ac80aac1a6ea6d9a6cec3778379d35a611a52a2bca692685645c81"
)

SUITE_IDS = (
    "original_bounded_v5", "public_v3", "scanner_v3", "buffer_v3",
    "managed_v1", "scanner_verbose_v1", "public_types_v1",
    "substitution_v2", "shape_v2", "public_surface_v19",
    "subinterpreter_v2", "pep688_v4", "threaded_pattern_v1",
)

# Each tuple independently pins the original worker outcome, both distinct
# published owners, and every byte of the complete uncompressed suite report.
COMPLETED_C_SUITE_EVIDENCE: tuple[
    tuple[str, int, str, int, str, str, int, str, str, int, int, str], ...
] = (
    (
        "original_bounded_v5",
        151,
        "PASS",
        0,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-original_bounded_v5.json.gz",
        "65da63f25898bac1ee7424d7e362896d518ad8d0077de677cc72804f43501d7c",
        9593,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-original_bounded_v5-publication-receipt.json",
        "544118457b826d54a202393580700774690c2e31316b38ee391136fc49562cf7",
        1471,
        45250,
        "f57730a6b9250242b28ab8fb8048a86eb0239c81ec7db45141890ef92a48e9de",
    ),
    (
        "public_v3",
        864,
        "PASS",
        0,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-public_v3.json.gz",
        "14173275e02ed03dd8eb1d3f6304f55794307295dccd49d5c96fd471841af4c7",
        37961,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-public_v3-publication-receipt.json",
        "fe18dc65418a91381726f94e10856fe006865df97b707df1a09be60e86476ef2",
        1454,
        1549631,
        "0a69f0cdc71966d1b2539bcb2c7656bf2651837cd1c653659a24438559bd95f7",
    ),
    (
        "scanner_v3",
        1024,
        "PASS",
        0,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-scanner_v3.json.gz",
        "17400d508cf15ba8c25a082b46c0d55683909f6f8dfa28d2db046df92d6c4383",
        50411,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-scanner_v3-publication-receipt.json",
        "9085bbce1de494fbaaa403b3b6f42cd4766b9badb0b778cdc53f1e322ac23815",
        1457,
        2246661,
        "59ecc643e7b158596caaef721ead663b53fa5a38592b4637ea142cc8563338e5",
    ),
    (
        "buffer_v3",
        768,
        "PASS",
        0,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-buffer_v3.json.gz",
        "0bc5689400789934a988cb135ea436d3ecb9a725c94a927816847a56b0e705cf",
        19416,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-buffer_v3-publication-receipt.json",
        "064a93944c6e2bcd2826716c3e3b6152805b2cf58da5133058bd571e3c401461",
        1453,
        676382,
        "adea3be30c95f7c9827f0e3bfe50918bb86f6365e1bb701923aa40d6de28413e",
    ),
    (
        "managed_v1",
        1024,
        "PASS",
        0,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-managed_v1.json.gz",
        "0995b02cb75d19f81c5f7dd37ba35d8312434a61d22873a6c5606a7633037ce5",
        107993,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-managed_v1-publication-receipt.json",
        "098ef746d6e3d4d7694c5430a6e2221afec2d07af858d1845c2602b5e6fe1ee8",
        1458,
        5388306,
        "97702ded0aecea5b275c289ca777fd46a8a7dfaad555caffeda0ca75c4072255",
    ),
    (
        "scanner_verbose_v1",
        2854,
        "PASS",
        0,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-scanner_verbose_v1.json.gz",
        "5e426ac26200a1c8f126eef9492b2420f2841c60e57bb12a3cb704e0fe5fb8ed",
        65655,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-scanner_verbose_v1-publication-receipt.json",
        "105a620928b39f8f5464a95949398efd8464981ca37b7661b941be84e97cd307",
        1473,
        3140285,
        "2de3b44fac298d8b80194859dda20cefa5456f777f7c6a2bf452b752df697ef3",
    ),
    (
        "public_types_v1",
        6912,
        "FAIL",
        248,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-public_types_v1.json.gz",
        "bd0f8ed8691785c33c0fdb4d0a506808c959d1e412d655d742d5a4ea46808ce4",
        206151,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-public_types_v1-publication-receipt.json",
        "5548f27728cfb8e9d941aa9a3d6c4220d889d82707384d73f41f5a2ec92e3964",
        1471,
        15960736,
        "2485d6159feb2ab32628355a33d5f2b5552c6e40d48317557849e5cf3fb1b532",
    ),
    (
        "substitution_v2",
        5120,
        "FAIL",
        224,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-substitution_v2.json.gz",
        "c47bbd42362cc9c40bf7fc42ef2b73260e63337b2ad5b7bbfab7270173ae8cd7",
        358695,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-substitution_v2-publication-receipt.json",
        "6897346db1cfe6f53bd6bce2a70f2b2bab4b46759fc5dee18c9f2d978c36dffe",
        1471,
        15424688,
        "402a97f9052c76e7b44260144d22b19548ad25f9dcf3188dcd21f8c62d57bed3",
    ),
    (
        "shape_v2",
        10240,
        "FAIL",
        672,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-shape_v2.json.gz",
        "6fe30ddbabd5a7c219a467e52201b9498789bc27a4db07fa105fc6f2ffddc86d",
        600108,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-shape_v2-publication-receipt.json",
        "58662aeb28cead53a4b87b1da04afb8ac8ece1b5cbb9edce79b2f37115469916",
        1458,
        33064293,
        "d3a05a6e642b6bc8e7dde35649b7b4a9a4d86608448411a790202e59bad966a5",
    ),
    (
        "public_surface_v19",
        1376,
        "FAIL",
        114,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-public_surface_v19.json.gz",
        "47dbd61f66df74830f69819e237315e73479533233f2377eb3bd118a3aecc303",
        159596,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-public_surface_v19-publication-receipt.json",
        "998cba40fd46931d75b5766b419ec19656e606f9166e03321188ce158becf824",
        1476,
        2912713,
        "9077249d40187227d8fbd601d1e12a665fee5cbddbc511ae15198db2ac5ac1b4",
    ),
    (
        "subinterpreter_v2",
        128,
        "PASS",
        0,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-subinterpreter_v2.json.gz",
        "89cc91ae50c3562411c6531423cb06b37910b2fa1c05c95d586811cba82a3f3c",
        38564,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-subinterpreter_v2-publication-receipt.json",
        "0eb401ac4261252c35c134fc021388abd5f1ec1c1686e5b06675a0189f8fab5d",
        1470,
        1150606,
        "a36d5bccdf9f3161bcf001dbaad615fd888b3f75e5930e1a53aefb4b0950d8b9",
    ),
    (
        "pep688_v4",
        264,
        "FAIL",
        4,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-pep688_v4.json.gz",
        "9d8932a49b91b7fc77ff02594b8699f06f631b60855548fd394eb5a4b27fe0a1",
        10223,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-pep688_v4-publication-receipt.json",
        "9dfb20f4b97fa631bbcb3885f0a10109f9a5701de84805d2edd37dc9948e7a6a",
        1453,
        241063,
        "333b5183398e627d9773ca808cbfc9277d9577ed75972df4f2830f31a6bdcc91",
    ),
    (
        "threaded_pattern_v1",
        512,
        "PASS",
        0,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-threaded_pattern_v1.json.gz",
        "71a368a8cdf872b06ad797c7b7c5e0f2c1b710076b7165a17148bafd23eced9f",
        28002,
        "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-live-original-p0-threaded_pattern_v1-publication-receipt.json",
        "a686d871de56e5728550079274618e19118d9aca5dc606d99230578253d39185",
        1474,
        1063386,
        "5835399cd7b554a1e4d1b1cac3af49ee50c0ea77db95ca5ac77c65dd638f19f2",
    ),
)

COMPLETED_C_AGGREGATE_OWNERS: dict[str, tuple[str, str, int]] = {
    "original_archive": (
        "oracle/phase2/evidence/"
        "frozen-p0-candidate-v9-c-phase2-v10-live-original-p0-failures.json.gz",
        "b3ade63c2a5b1b8152af680c83fc19d5e89fd0fa955aa428737c97fffbfab173",
        10_579,
    ),
    "original_receipt": (
        "oracle/phase2/evidence/frozen-p0-candidate-v9-c-"
        "phase2-v10-live-original-p0-failures-publication-receipt.json",
        "d9476eaee24864ae6b96efd3dfef30cf2355f32398d567d99244d47363de0b54",
        2_959,
    ),
    "outer_archive": (
        "oracle/phase2/evidence/repaired-c-original-campaign-v3-c-"
        "phase2-v10-live-original-p0-failures.json.gz",
        "8dae792944509b4e8879d42b149a723d629c237b40c387a577fac5443bd2e4c7",
        12_100,
    ),
    "outer_receipt": (
        "oracle/phase2/evidence/repaired-c-original-campaign-v3-c-"
        "phase2-v10-live-original-p0-failures-publication-receipt.json",
        "f3383b6c00ab28d4466332b99c759e981b423a9f427757b0524f7a85f0cf253d",
        1_039,
    ),
}

SOURCE_OWNERS: dict[str, tuple[str, int]] = {
    ORIGINAL_ADAPTER: (ORIGINAL_ADAPTER_SHA256, 68_422),
    ORIGINAL_ENGINE: (ORIGINAL_ENGINE_SHA256, 186_915),
    ORIGINAL_BRIDGE: (ORIGINAL_BRIDGE_SHA256, 173_026),
}

SUPPORT_OWNERS: dict[str, tuple[str, int]] = {
    "GOAL.md": (
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
        3_756,
    ),
    "oracle/phase1/p0-completeness-v1.json": (
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
        45_632,
    ),
    "docs/evidence/candidate-current-overview-v21.inputs.json": (
        "704b2e07e32260ac741b0a914e2ae04a3deb583de317ba170432f85126af5139",
        14_631,
    ),
    "docs/evidence/candidate-current-overview-v21.json": (
        "d2143b09bbf35a7a83977c08a35f6a0c87435a50e478df517099aa719e8fa28c",
        96_376,
    ),
    "docs/evidence/candidate-current-overview-v21.svg": (
        "ba7b82d7552603eb836a0c18e47546390c4e1398bbb74951616e309135b9ce5c",
        8_074,
    ),
    "tools/render_candidate_current_overview_v21.py": (
        "617a64691bf9da7730e44bfed96fe20dbd9c8e38b575e0daf8a3432dbf2625e9",
        75_566,
    ),
    "tools/run_owned_six_family_original_p0_producer_v3.py": (
        "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
        195_555,
    ),
    "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md": (
        "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76",
        5_522,
    ),
    "oracle/phase2/six-family-p0-producer-v3.json": (
        "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1",
        26_909,
    ),
    OVERLAY_SOURCE: (OVERLAY_SOURCE_SHA256, 65_531),
    OVERLAY_PROTOCOL: (OVERLAY_PROTOCOL_SHA256, 5_198),
    OVERLAY_CONTRACT: (OVERLAY_CONTRACT_SHA256, 9_236),
    "tools/reproduce_owned_native_source_build_v7.py": (
        "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7",
        300_624,
    ),
    "oracle/phase2/NATIVE-SOURCE-BUILD-V7.md": (
        "a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313",
        8_063,
    ),
    "oracle/phase2/native-source-build-v7.json": (
        "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819",
        28_924,
    ),
    "toolchains/zig-0.16.0.lock.json": (
        "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd",
        628,
    ),
    RECOVERED_C_ARCHIVE: (RECOVERED_C_ARCHIVE_SHA256, 2_496),
    RECOVERED_C_RECEIPT: (RECOVERED_C_RECEIPT_SHA256, 934),
}

# Pin the immutable predecessor, the published V22 history, the exact original
# C runner chain, and the still-restored original C native inode.
SUPPORT_OWNERS.update({
    "tools/reproduce_owned_zig_scanner_source_build_v10.py": (
        "4d2bf61385c310bc95fc353492ad3b9a4a1687ee1cd46c5822cf2a8eb6d61578", 146_563,
    ),
    "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V10.md": (
        "99d8144cd083663145f2924ae96a285b32fffb05a11a37d35ec81c81142c9148", 7_147,
    ),
    "oracle/phase2/zig-scanner-source-build-v10.json": (
        "7192419e64dd460f78977bd92afea0bfe7871bd10788500de699d7d89b2961c7", 20_530,
    ),
    "tools/run_owned_repaired_c_original_campaign_v3.py": (
        "bdf846bca02c80d15e37db8d26fad45d7dacd3f3dee7ec94ce4151315423994f", 88_202,
    ),
    "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V3.md": (
        "d4aa6a11d6c1398109de454f3d23e5e20d488913a00b37adfd05b47f9f53522e", 4_587,
    ),
    "oracle/phase2/repaired-c-original-campaign-v3.json": (
        "1150def4ccc3e3c64773d3bdf854e0f6b04d5b6560a6dc04deeba38c8049da16", 16_527,
    ),
    "tools/run_owned_frozen_p0_v9_live_context_adapter_v1.py": (
        "82d9ba024400b73ec8d99866609241871ba6e4b057a4c2c0fcd9ebf225b621cb", 81_892,
    ),
    "oracle/phase2/P0-V9-LIVE-CONTEXT-ADAPTER-V1.md": (
        "51f9cede20828da51f127ee9e34c814d306c52252804f77d5c2e95ced2bf4f2c", 5_186,
    ),
    "oracle/phase2/p0-v9-live-context-adapter-v1.json": (
        "a404db028e2d5bd1ea246e58c11e5a40af2d990909a8d69fac9dbb881bf169b8", 9_085,
    ),
    "tools/run_frozen_p0_candidate_v9.py": (
        "1511dac06dab5ce319b4dd09cb6f8c5a12160c48cc0dbbdfa7e7fe3f0d426702", 43_680,
    ),
    "tools/run_frozen_p0_candidate_worker_v7.py": (
        "855c59acdc0b5270493ece8fc39548a89e0febf94d6b186ac9f0e5a50754f68f", 79_184,
    ),
    "oracle/phase2/P0-CANDIDATE-PROTOCOL-V9.md": (
        "afbb933eb022efaca7cb9604bc1614d3d2de7e3faf33f446234f725cd331771f", 4_413,
    ),
    "oracle/phase2/p0-candidate-protocol-v9.json": (
        "a9609b0576aab4e0ea7ff6f9ae2a466c0d77d0af134a7f0bddf83ed01f61d631", 13_869,
    ),
    "tools/render_candidate_current_overview_v22.py": (
        "a07bf3d6e6d8dc28c206218f14e2ed6f6089e31c66dbab2961979409b30fc955", 59_289,
    ),
    "docs/evidence/candidate-current-overview-v22.inputs.json": (
        "6843292a1f1d62d4635be4737a1565554cee8ec9f359506bc95a94cb80af7b58", 16_526,
    ),
    "docs/evidence/candidate-current-overview-v22.json": (
        "5dc6229696e5aba546c38e3d1d1bd4ce422a892a57ec562ccea8cb75cbbfb21f", 100_772,
    ),
    "docs/evidence/candidate-current-overview-v22.svg": (
        "7314d28286b90ee8161c02fee175904ba2ddd2c67dd78163f93b04fef2d0a26c", 7_898,
    ),
    "tools/render_candidate_current_overview_v23.py": (
        "a7f90986e1020d4cccd0b7eac19779a68a5dac28a33a2a7b5776a5508c91b213", 74_868,
    ),
    "docs/evidence/candidate-current-overview-v23.inputs.json": (
        "e203be81e2ebafa23bd91e41902dd1949fa2245cb8d818e76444982021bfba68", 29_567,
    ),
    "docs/evidence/candidate-current-overview-v23.json": (
        "6368a2c900e2ed656830ba773bd454a603f547f3f21f9eabac3490140d687098", 127_100,
    ),
    "docs/evidence/candidate-current-overview-v23.svg": (
        "853d3084beb85df634437f3e9198f85c3d28f455c82c94550ae98cb453e561a4", 11_462,
    ),
    "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so": (
        "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd", 149_976,
    ),
})
for _suite in COMPLETED_C_SUITE_EVIDENCE:
    _suite_id, _denominator, _status, _mismatches, _archive, _archive_sha, \
        _archive_bytes, _receipt, _receipt_sha, _receipt_bytes, \
        _plain_bytes, _plain_sha = _suite
    SUPPORT_OWNERS[_archive] = (_archive_sha, _archive_bytes)
    SUPPORT_OWNERS[_receipt] = (_receipt_sha, _receipt_bytes)
for _aggregate_path, _aggregate_sha, _aggregate_bytes in \
        COMPLETED_C_AGGREGATE_OWNERS.values():
    SUPPORT_OWNERS[_aggregate_path] = (_aggregate_sha, _aggregate_bytes)
del _suite, _suite_id, _denominator, _status, _mismatches, _archive, \
    _archive_sha, _archive_bytes, _receipt, _receipt_sha, _receipt_bytes, \
    _plain_bytes, _plain_sha, _aggregate_path, _aggregate_sha, _aggregate_bytes

TOOLCHAIN_OWNERS: dict[str, tuple[str, str, int, bool]] = {
    "python": (
        PINNED_PYTHON,
        "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        32_387_816,
        True,
    ),
    "python_header": (
        PYTHON_INCLUDE + "/Python.h",
        "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f",
        4_399,
        False,
    ),
    "python_patchlevel": (
        PYTHON_INCLUDE + "/patchlevel.h",
        "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95",
        1_773,
        False,
    ),
    "gcc": (
        PINNED_GCC,
        "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26",
        1_023_032,
        True,
    ),
    "readelf": (
        PINNED_READELF,
        "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0",
        789_280,
        True,
    ),
    "zig": (
        PINNED_ZIG,
        "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c",
        172_641_672,
        True,
    ),
}

PROCESS_ROLES = (
    "readelf_version", "gcc_version", "zig_version",
    "build_zig_engine", "build_zig_bridge",
    "engine_dynamic", "engine_symbols", "engine_sections", "engine_notes",
    "bridge_dynamic", "bridge_symbols", "bridge_sections", "bridge_notes",
)

REQUIRED_ENGINE_EXPORTS = frozenset({
    "rebar_zig_batch", "rebar_zig_collect_captures",
    "rebar_zig_collect_records", "rebar_zig_collect_records_wide",
    "rebar_zig_compile", "rebar_zig_compile_guarded", "rebar_zig_flags",
    "rebar_zig_free", "rebar_zig_groups", "rebar_zig_match",
    "rebar_zig_match_captures", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_tree", "rebar_zig_match_wide", "rebar_zig_name_copy",
    "rebar_zig_name_count", "rebar_zig_name_group", "rebar_zig_name_length",
    "rebar_zig_program_memory", "rebar_zig_program_size",
})

REQUIRED_BRIDGE_ENGINE_IMPORTS = frozenset({
    "rebar_zig_collect_records_wide", "rebar_zig_compile",
    "rebar_zig_compile_guarded", "rebar_zig_flags", "rebar_zig_free",
    "rebar_zig_groups", "rebar_zig_match_captures_wide",
    "rebar_zig_match_inverted_wide", "rebar_zig_match_nonempty_wide",
    "rebar_zig_match_wide", "rebar_zig_name_copy", "rebar_zig_name_count",
    "rebar_zig_name_group", "rebar_zig_name_length",
})

ALLOWED_ENGINE_UNICODE_HELPERS = frozenset({
    "_PyUnicode_IsWhitespace", "_PyUnicode_IsDecimalDigit",
    "_PyUnicode_IsAlpha", "_PyUnicode_IsDigit", "_PyUnicode_IsNumeric",
    "_PyUnicode_ToLowercase", "_PyUnicode_ToUppercase",
})

FORBIDDEN_SYMBOL_PREFIXES = (
    "_sre", "sre_", "pcre", "onig", "re2_", "hs_", "hyperscan",
    "rebar_rust_", "rebar_c_", "rebar_vm_", "rebar_cpp_",
    "rebar_go_", "rebar_fortran_",
)
FORBIDDEN_SYMBOLS = frozenset({
    "regcomp", "regexec", "regerror", "regfree", "dlopen", "dlmopen",
    "dlsym", "system", "execve", "posix_spawn", "socket", "connect",
    "getaddrinfo", "PyImport_Import", "PyImport_ImportModule",
    "PyImport_ExecCodeModule",
})


class FreezeError(Exception):
    """A source-freeze, authenticated owner, or actual future build failed."""


class SourceOnlyError(FreezeError):
    """A synthetic control attempted a real external effect."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only genuine, complete byte strings")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, RecursionError, UnicodeError) as error:
        raise FreezeError("require one finite, canonical JSON object") from error


def valid_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(part in "0123456789abcdef" for part in value),
        "require one exact lowercase SHA-256 for " + label,
    )
    return value


def unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "reject duplicated or non-string JSON object fields")
        result[key] = value
    return result


def strict_json(raw: bytes, label: str, *, canonical_required: bool = True) -> dict:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "bound the complete authenticated JSON: " + label)

    def reject_nonfinite(value: str) -> Any:
        raise FreezeError("reject a non-finite JSON number: " + value)

    try:
        result = json.loads(
            raw.decode("utf-8", "strict"),
            object_pairs_hook=unique_json_pairs,
            parse_constant=reject_nonfinite,
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise FreezeError("reject malformed JSON: " + label) from error
    require(type(result) is dict, "require a complete JSON object: " + label)
    if canonical_required:
        require(canonical(result) == raw,
                "reject substituted or noncanonical JSON: " + label)
    return result


def checked_relative(value: Any) -> tuple[str, ...]:
    require(type(value) is str and 0 < len(value) <= 512,
            "require a bounded repository-relative owner")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and str(parsed) == value
            and 0 < len(parsed.parts) <= 12
            and all(part not in ("", ".", "..")
                    and "\\" not in part and "\x00" not in part
                    for part in parsed.parts),
            "reject an absolute, traversing, redirected, or malformed owner")
    return parsed.parts


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= MAX_LABEL_BYTES
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(char in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for char in value)
            and "--" not in value and not value.endswith("-"),
            "require one bounded, fresh, lowercase evidence label")
    return value


def checked_workdir(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 512,
            "require one bounded fresh Zig build root")
    parsed = PurePosixPath(value)
    require(parsed.is_absolute() and str(parsed) == value,
            "require one exact absolute private Zig build root")
    parts = parsed.parts
    require(len(parts) == 3 and parts[1] == "tmp"
            and parts[2].startswith(PRIVATE_ROOT_PREFIX),
            "use only the independently frozen Zig overlay root prefix")
    suffix = parts[2][len(PRIVATE_ROOT_PREFIX):]
    require(len(suffix) >= 8
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in suffix),
            "reject an unsafe, reused, unresolved, or predictable phase root")
    return value


def phase_paths(workdir: str, phase: str) -> dict[str, Path]:
    root = Path(checked_workdir(workdir))
    require(type(phase) is str and phase in PHASE_NAMES,
            "require exactly reference-a or reference-b")
    base = root / phase
    source = base / "source"
    native = base / "native"
    return {
        "base": base,
        "source": source,
        "native": native,
        "temporary": base / "temporary",
        "zig_local_cache": base / "zig-local-cache",
        "zig_global_cache": base / "zig-global-cache",
        "source_candidates": source / "candidates",
        "source_zig": source / "candidates" / "zig",
        "source_adapter": source / "candidates" / "zig_candidate.py",
        "source_engine": source / "candidates" / "zig" / "mini_regex.zig",
        "source_bridge": source / "candidates" / "zig" / "py_bridge.c",
        "artifact_engine": native / ENGINE_FILENAME,
        "artifact_bridge": native / BRIDGE_FILENAME,
    }


def prefix_flags(workdir: str) -> list[str]:
    checked_workdir(workdir)
    return [
        "-ffile-prefix-map=" + str(phase_paths(workdir, phase)["source"])
        + "=" + CANONICAL_SOURCE_PREFIX
        for phase in PHASE_NAMES
    ]


def build_environment(workdir: str, phase: str) -> dict[str, str]:
    paths = phase_paths(workdir, phase)
    return {
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C",
        "LANG": "C",
        "TZ": "UTC",
        "SOURCE_DATE_EPOCH": "1",
        "TMPDIR": str(paths["temporary"]),
        "ZIG_LOCAL_CACHE_DIR": str(paths["zig_local_cache"]),
        "ZIG_GLOBAL_CACHE_DIR": str(paths["zig_global_cache"]),
    }


def planned_commands(workdir: str, phase: str) -> dict[str, list[str]]:
    paths = phase_paths(workdir, phase)
    commands: dict[str, list[str]] = {
        "readelf_version": [PINNED_READELF, "--version"],
        "gcc_version": [PINNED_GCC, "--version"],
        "zig_version": [PINNED_ZIG, "version"],
        "build_zig_engine": [
            PINNED_ZIG,
            "build-lib",
            str(paths["source_engine"]),
            "-dynamic",
            "-lc",
            "-O",
            "ReleaseFast",
            "-fstrip",
            "-fallow-shlib-undefined",
            "-fsoname=" + ENGINE_FILENAME,
            "--cache-dir",
            str(paths["zig_local_cache"]),
            "--global-cache-dir",
            str(paths["zig_global_cache"]),
            "-femit-bin=" + str(paths["artifact_engine"]),
        ],
        "build_zig_bridge": [
            PINNED_GCC,
            "-std=c11",
            "-shared",
            "-fPIC",
            "-O3",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Wl,--build-id=sha1",
            *prefix_flags(workdir),
            "-I" + PYTHON_INCLUDE,
            str(paths["source_bridge"]),
            "-L" + str(paths["native"]),
            "-l:" + ENGINE_FILENAME,
            "-Wl,-rpath,$ORIGIN",
            "-o",
            str(paths["artifact_bridge"]),
        ],
    }
    for role in ("engine", "bridge"):
        target = str(paths["artifact_" + role])
        commands[role + "_dynamic"] = [
            PINNED_READELF, "--dynamic", "--wide", target,
        ]
        commands[role + "_symbols"] = [
            PINNED_READELF, "--dyn-syms", "--wide", target,
        ]
        commands[role + "_sections"] = [
            PINNED_READELF, "--sections", "--wide", target,
        ]
        commands[role + "_notes"] = [
            PINNED_READELF, "--notes", "--wide", target,
        ]
    require(tuple(commands) == PROCESS_ROLES
            and len(commands) == EXPECTED_PHASE_PROCESS_COUNT,
            "freeze exactly the thirteen direct V7-derived Zig phase processes")
    return commands


def checked_command(name: Any, argv: Any, workdir: str, phase: str) -> list[str]:
    commands = planned_commands(workdir, phase)
    require(type(name) is str and name in commands and type(argv) is list
            and all(type(item) is str and "\x00" not in item for item in argv)
            and argv == commands[name]
            and argv[0] in (PINNED_READELF, PINNED_GCC, PINNED_ZIG),
            "reject an unpinned, modified, networked, delegated, or shell command")
    return list(argv)


def sanitized(value: Any, workdir: str) -> Any:
    root = checked_workdir(workdir)
    if type(value) is str:
        return value.replace(root, "<FRESH_PRIVATE_ROOT>")
    if type(value) is list:
        return [sanitized(item, root) for item in value]
    if type(value) is dict:
        return {key: sanitized(item, root) for key, item in value.items()}
    return value


def expected_phase_boundary() -> dict[str, Any]:
    return {
        "source_apply_count": 0,
        "native_builds_started": 0,
        "compiler_processes_started": 0,
        "actual_build_process_count": 0,
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "reference_processes_started": 0,
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
        "final_comparison_planned_case_count": FINAL_PLANNED_CASE_COUNT,
        "final_comparison_cases_generated": False,
        "holdout": "NOT OPENED",
        "holdout_opened": False,
        "winner_selected": False,
    }


def owner_document(path: str, owner: tuple[str, int]) -> dict[str, Any]:
    checked_relative(path)
    valid_digest(owner[0], path)
    require(type(owner[1]) is int and 0 < owner[1] <= MAX_SOURCE_BYTES,
            "bound an exact frozen first-party source owner")
    return {"path": path, "sha256": owner[0], "bytes": owner[1]}


def command_templates() -> list[dict[str, Any]]:
    root = "/tmp/" + PRIVATE_ROOT_PREFIX + "synthetic-v11"
    return [
        {
            "phase": phase,
            "working_directory": sanitized(str(phase_paths(root, phase)["base"]), root),
            "environment": sanitized(build_environment(root, phase), root),
            "commands": [
                {"name": name, "argv": sanitized(argv, root)}
                for name, argv in planned_commands(root, phase).items()
            ],
        }
        for phase in PHASE_NAMES
    ]



def completed_c_suite_documents() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for (suite, denominator, status, mismatch_count, archive_path,
         archive_sha256, archive_bytes, receipt_path, receipt_sha256,
         receipt_bytes, expanded_bytes, expanded_sha256
         ) in COMPLETED_C_SUITE_EVIDENCE:
        result.append({
            "suite": suite,
            "status": status,
            "case_execution_denominator": denominator,
            "genuine_original_suite": True,
            "mismatch_count": mismatch_count,
            "actual_worker_started": True,
            "archive": owner_document(
                archive_path, (archive_sha256, archive_bytes),
            ),
            "receipt": owner_document(
                receipt_path, (receipt_sha256, receipt_bytes),
            ),
            "full_uncompressed_suite_bytes": expanded_bytes,
            "full_uncompressed_suite_sha256": expanded_sha256,
        })
    return result

def contract_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    valid_digest(source_pin, "V11 source")
    valid_digest(protocol_pin, "V11 protocol")
    return {
        "schema": CONTRACT_SCHEMA,
        "version": 11,
        "phase": "ZIG SCANNER NATIVE BUILD SOURCE FREEZE; NO BUILD EXECUTED",
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "oracle": {
            "implementation": "CPython",
            "version": "3.14.6",
            "manifest_path": "oracle/phase1/p0-completeness-v1.json",
            "manifest_sha256": SUPPORT_OWNERS[
                "oracle/phase1/p0-completeness-v1.json"
            ][0],
            "suite_count": 13,
            "suite_ids": list(SUITE_IDS),
            "case_execution_count": 31_237,
            "private_waiver_count": 13,
        },
        "frozen_overlay": {
            "schema": OVERLAY_SCHEMA,
            "source": owner_document(OVERLAY_SOURCE, SUPPORT_OWNERS[OVERLAY_SOURCE]),
            "protocol": owner_document(
                OVERLAY_PROTOCOL, SUPPORT_OWNERS[OVERLAY_PROTOCOL],
            ),
            "contract": owner_document(
                OVERLAY_CONTRACT, SUPPORT_OWNERS[OVERLAY_CONTRACT],
            ),
            "application": "AUTHENTICATED IN-PROCESS; EXPLICIT BUILD ONLY",
            "private_root_prefix": "/tmp/" + PRIVATE_ROOT_PREFIX,
            "phase_names": list(PHASE_NAMES),
            "both_phase_trees_created_before_first_apply": True,
            "existing_destination": "FORBIDDEN",
            "destination": "source/candidates/zig/py_bridge.c",
            "private_directory_mode": "0700",
            "private_source_mode": "0600",
            "source_write_mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "expected_actual_apply_count_only_after_build": 2,
            "actual_source_apply_count": 0,
            "derived_bridge_sha256": DERIVED_BRIDGE_SHA256,
            "derived_bridge_bytes": DERIVED_BRIDGE_BYTES,
            "derived_bridge_materialized": False,
        },
        "first_party_zig_owners": [
            owner_document(path, owner)
            for path, owner in sorted(SOURCE_OWNERS.items())
        ],
        "original_zig_source_owner_count": 3,
        "total_first_party_source_owner_count": 25,
        "independent_engine_family_count": 6,
        "external_regex_engine": "FORBIDDEN",
        "stdlib_regex_delegation": "FORBIDDEN",
        "cross_family_matching_engine": "FORBIDDEN",
        "source_fallback": "FORBIDDEN",
        "frozen_v10_source_build": {
            "source": owner_document(
                "tools/reproduce_owned_zig_scanner_source_build_v10.py",
                SUPPORT_OWNERS[
                    "tools/reproduce_owned_zig_scanner_source_build_v10.py"
                ],
            ),
            "protocol": owner_document(
                "oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V10.md",
                SUPPORT_OWNERS["oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V10.md"],
            ),
            "contract": owner_document(
                "oracle/phase2/zig-scanner-source-build-v10.json",
                SUPPORT_OWNERS["oracle/phase2/zig-scanner-source-build-v10.json"],
            ),
            "private_root_prefix_modified": False,
            "zig_compiler_modified": False,
            "compiler_command_policy_modified": False,
            "overlay_modified": False,
        },
        "frozen_v7_source_build": {
            "source": owner_document(
                "tools/reproduce_owned_native_source_build_v7.py",
                SUPPORT_OWNERS["tools/reproduce_owned_native_source_build_v7.py"],
            ),
            "protocol": owner_document(
                "oracle/phase2/NATIVE-SOURCE-BUILD-V7.md",
                SUPPORT_OWNERS["oracle/phase2/NATIVE-SOURCE-BUILD-V7.md"],
            ),
            "contract": owner_document(
                "oracle/phase2/native-source-build-v7.json",
                SUPPORT_OWNERS["oracle/phase2/native-source-build-v7.json"],
            ),
            "compiler_command_policy": "EXACT V7 ZIG ARGV; SEALED OVERLAY ROOT",
            "canonical_source_prefix": CANONICAL_SOURCE_PREFIX,
            "raw_elf_parser": "AUTHENTICATED FIRST-PARTY V7 parse_owned_elf64",
            "raw_elf_comparator": "AUTHENTICATED FIRST-PARTY V7 compare_owned_elf64",
            "modified": False,
        },
        "frozen_corrected_v3": {
            "source": owner_document(
                "tools/run_owned_six_family_original_p0_producer_v3.py",
                SUPPORT_OWNERS[
                    "tools/run_owned_six_family_original_p0_producer_v3.py"
                ],
            ),
            "protocol": owner_document(
                "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md",
                SUPPORT_OWNERS["oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md"],
            ),
            "contract": owner_document(
                "oracle/phase2/six-family-p0-producer-v3.json",
                SUPPORT_OWNERS["oracle/phase2/six-family-p0-producer-v3.json"],
            ),
            "modified": False,
        },
        "toolchains": [
            {
                "id": name,
                "path": value[0],
                "sha256": value[1],
                "bytes": value[2],
                "executable": value[3],
            }
            for name, value in sorted(TOOLCHAIN_OWNERS.items())
        ],
        "official_zig_lock": owner_document(
            "toolchains/zig-0.16.0.lock.json",
            SUPPORT_OWNERS["toolchains/zig-0.16.0.lock.json"],
        ),
        "published_v21_history": {
            "version": 21,
            "authoritative_counted_evidence_owner_count":
                HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
            "authenticated_digest_addressed_history_paths":
                HISTORICAL_V21_REFERENCE_COUNT,
            "current_qualified_candidate_count": 0,
            "historical_zig_semantic_mismatch_count": 1_764,
            "historical_zig_verified_passing_case_executions": 3_583,
            "historical_zig_gate_status": "FAIL",
            "scanner_verbose_mismatch_count": 620,
            "overview_inputs": owner_document(
                "docs/evidence/candidate-current-overview-v21.inputs.json",
                SUPPORT_OWNERS[
                    "docs/evidence/candidate-current-overview-v21.inputs.json"
                ],
            ),
            "overview": owner_document(
                "docs/evidence/candidate-current-overview-v21.json",
                SUPPORT_OWNERS["docs/evidence/candidate-current-overview-v21.json"],
            ),
            "new_v11_evidence_owners": 0,
            "planned_new_evidence_owners_only_after_publication": 2,
            "file_owners_are_not_compiler_processes": True,
        },
        "published_v22_history": {
            "version": 22,
            "authoritative_counted_evidence_owner_count":
                HISTORICAL_V22_EVIDENCE_OWNER_COUNT,
            "authenticated_digest_addressed_history_paths":
                HISTORICAL_V22_REFERENCE_COUNT,
            "preserved_v21_evidence_owner_count":
                HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
            "preserved_v21_authenticated_reference_count":
                HISTORICAL_V21_REFERENCE_COUNT,
            "qualified_candidate_count": 0,
            "overview_inputs": owner_document(
                "docs/evidence/candidate-current-overview-v22.inputs.json",
                SUPPORT_OWNERS[
                    "docs/evidence/candidate-current-overview-v22.inputs.json"
                ],
            ),
            "overview": owner_document(
                "docs/evidence/candidate-current-overview-v22.json",
                SUPPORT_OWNERS["docs/evidence/candidate-current-overview-v22.json"],
            ),
            "renderer": owner_document(
                "tools/render_candidate_current_overview_v22.py",
                SUPPORT_OWNERS["tools/render_candidate_current_overview_v22.py"],
            ),
            "svg": owner_document(
                "docs/evidence/candidate-current-overview-v22.svg",
                SUPPORT_OWNERS["docs/evidence/candidate-current-overview-v22.svg"],
            ),
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
        },
        "published_v23_history": {
            "version": 23,
            "authoritative_counted_evidence_owner_count":
                CURRENT_EVIDENCE_OWNER_COUNT,
            "authenticated_digest_addressed_history_paths":
                CURRENT_AUTHENTICATED_REFERENCE_COUNT,
            "preserved_v22_evidence_owner_count":
                HISTORICAL_V22_EVIDENCE_OWNER_COUNT,
            "preserved_v22_authenticated_reference_count":
                HISTORICAL_V22_REFERENCE_COUNT,
            "qualified_candidate_count": 0,
            "overview_inputs": owner_document(
                "docs/evidence/candidate-current-overview-v23.inputs.json",
                SUPPORT_OWNERS[
                    "docs/evidence/candidate-current-overview-v23.inputs.json"
                ],
            ),
            "overview": owner_document(
                "docs/evidence/candidate-current-overview-v23.json",
                SUPPORT_OWNERS["docs/evidence/candidate-current-overview-v23.json"],
            ),
            "renderer": owner_document(
                "tools/render_candidate_current_overview_v23.py",
                SUPPORT_OWNERS["tools/render_candidate_current_overview_v23.py"],
            ),
            "svg": owner_document(
                "docs/evidence/candidate-current-overview-v23.svg",
                SUPPORT_OWNERS["docs/evidence/candidate-current-overview-v23.svg"],
            ),
            "completed_c_semantic_mismatch_count": 1_262,
            "completed_c_verified_passing_case_count": 7_325,
            "completed_c_actual_candidate_worker_count": 13,
            "completed_c_infrastructure_failure_count": 0,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
        },
        "current_published_history": {
            "historical_v21_evidence_owner_count":
                HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
            "historical_v21_authenticated_reference_count":
                HISTORICAL_V21_REFERENCE_COUNT,
            "historical_v22_evidence_owner_count":
                HISTORICAL_V22_EVIDENCE_OWNER_COUNT,
            "historical_v22_authenticated_reference_count":
                HISTORICAL_V22_REFERENCE_COUNT,
            "additional_recovered_c_failure_evidence_owner_count":
                ADDITIONAL_RECOVERED_C_EVIDENCE_OWNER_COUNT,
            "additional_completed_c_campaign_evidence_owner_count":
                ADDITIONAL_COMPLETED_C_EVIDENCE_OWNER_COUNT,
            "authoritative_counted_evidence_owner_count":
                CURRENT_EVIDENCE_OWNER_COUNT,
            "authenticated_digest_addressed_history_paths":
                CURRENT_AUTHENTICATED_REFERENCE_COUNT,
            "recovered_c_failure": {
                "archive": owner_document(
                    RECOVERED_C_ARCHIVE, SUPPORT_OWNERS[RECOVERED_C_ARCHIVE],
                ),
                "receipt": owner_document(
                    RECOVERED_C_RECEIPT, SUPPORT_OWNERS[RECOVERED_C_RECEIPT],
                ),
                "archive_status": "FAIL",
                "receipt_status": "PASS",
                "actual_aggregate_process_count": 1,
                "actual_candidate_worker_count": 0,
                "infrastructure_failure_count": 1,
                "semantic_mismatch_count": "NOT MEASURED",
                "verified_passing_case_count": "NOT MEASURED",
                "original_native_restored": True,
                "candidate_qualified": False,
                "holdout": "NOT OPENED",
                "performance": "NOT MEASURED",
            },
            "completed_c_original_campaign": {
                "label": COMPLETED_C_CAMPAIGN_LABEL,
                "status": "FAIL",
                "suite_count": 13,
                "case_execution_denominator": 31_237,
                "named_private_waiver_count": 13,
                "completed_suite_count": 13,
                "actual_candidate_worker_count": 13,
                "verified_passing_case_count": 7_325,
                "semantic_mismatch_count": 1_262,
                "infrastructure_failure_count": 0,
                "all_original_suite_evidence_preserved": True,
                "distinct_published_evidence_owner_count": 30,
                "suite_results": completed_c_suite_documents(),
                "original_aggregate_archive": owner_document(
                    COMPLETED_C_AGGREGATE_OWNERS["original_archive"][0],
                    COMPLETED_C_AGGREGATE_OWNERS["original_archive"][1:],
                ),
                "original_aggregate_receipt": owner_document(
                    COMPLETED_C_AGGREGATE_OWNERS["original_receipt"][0],
                    COMPLETED_C_AGGREGATE_OWNERS["original_receipt"][1:],
                ),
                "outer_failure_archive": owner_document(
                    COMPLETED_C_AGGREGATE_OWNERS["outer_archive"][0],
                    COMPLETED_C_AGGREGATE_OWNERS["outer_archive"][1:],
                ),
                "outer_failure_receipt": owner_document(
                    COMPLETED_C_AGGREGATE_OWNERS["outer_receipt"][0],
                    COMPLETED_C_AGGREGATE_OWNERS["outer_receipt"][1:],
                ),
                "original_native": owner_document(
                    ORIGINAL_C_NATIVE, SUPPORT_OWNERS[ORIGINAL_C_NATIVE],
                ),
                "original_native_restored": True,
                "original_native_device": 2_064,
                "original_native_inode": 430_300,
                "original_native_mode": "0755",
                "candidate_qualified": False,
                "holdout": "NOT OPENED",
                "performance": "NOT MEASURED",
                "memory": "NOT MEASURED",
            },
            "new_v11_evidence_owners": 0,
            "qualified_candidate_count": 0,
        },
        "future_build_policy": {
            "authorization": "EXPLICIT --build AFTER INDEPENDENT SOURCE FREEZE",
            "actual_status": "NOT RUN",
            "phase_names": list(PHASE_NAMES),
            "phase_count_started": 0,
            "expected_phase_count_only_after_success": 2,
            "expected_process_count_per_completed_phase":
                EXPECTED_PHASE_PROCESS_COUNT,
            "expected_total_process_count_only_after_success":
                EXPECTED_PROCESS_COUNT,
            "actual_process_count": 0,
            "command_role_order": list(PROCESS_ROLES),
            "frozen_command_templates": command_templates(),
            "private_root_prefix": "/tmp/" + PRIVATE_ROOT_PREFIX,
            "private_directory_mode": "0700",
            "private_source_mode": "0600",
            "distinct_phase_sources": True,
            "distinct_phase_caches": True,
            "distinct_phase_output_inodes": True,
            "network_requests": 0,
            "shell": "FORBIDDEN",
            "prebuilt_native_artifact": "FORBIDDEN",
            "external_regex_engine": "FORBIDDEN",
            "stdlib_regex_delegation": "FORBIDDEN",
            "cross_family_matching_dependency": "FORBIDDEN",
            "fallback": "FORBIDDEN",
            "engine_soname": ENGINE_FILENAME,
            "bridge_needed_engine": ENGINE_FILENAME,
            "bridge_runpath": "$ORIGIN",
            "legacy_rpath": "FORBIDDEN",
            "allowed_engine_unicode_helpers": sorted(
                ALLOWED_ENGINE_UNICODE_HELPERS,
            ),
            "required_engine_exports": sorted(REQUIRED_ENGINE_EXPORTS),
            "required_bridge_engine_imports": sorted(
                REQUIRED_BRIDGE_ENGINE_IMPORTS,
            ),
            "native_outputs": {
                "engine": {"filename": ENGINE_FILENAME,
                           "sha256": "NOT MEASURED", "bytes": "NOT MEASURED"},
                "bridge": {"filename": BRIDGE_FILENAME,
                           "sha256": "NOT MEASURED", "bytes": "NOT MEASURED"},
            },
            "reproducibility": "NOT MEASURED",
            "raw_elf_audit": "NOT MEASURED",
        },
        "future_publication_policy": {
            "success_archive_template":
                "oracle/phase2/evidence/native-source-build-v11-zig-"
                "<FRESH_LABEL>.json.gz",
            "success_receipt_template":
                "oracle/phase2/evidence/native-source-build-v11-zig-"
                "<FRESH_LABEL>-publication-receipt.json",
            "failure_archive_template":
                "oracle/phase2/evidence/native-source-build-v11-zig-"
                "<FRESH_LABEL>-failures.json.gz",
            "failure_receipt_template":
                "oracle/phase2/evidence/native-source-build-v11-zig-"
                "<FRESH_LABEL>-failures-publication-receipt.json",
            "receipt_schema": RECEIPT_SCHEMA,
            "archive_compression": "SINGLE-MEMBER GZIP; LEVEL 9; MTIME 0",
            "write_mode": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "owner_mode": "0600",
            "full_same_inode_readback": True,
            "file_fsync": True,
            "parent_directory_fsync": True,
            "preserve_failure": True,
            "archives_published": 0,
            "receipts_published": 0,
        },
        "pinned_support": [
            owner_document(path, owner)
            for path, owner in sorted(SUPPORT_OWNERS.items())
        ],
        "phase_boundary": expected_phase_boundary(),
    }


def validate_contract(value: Any, source_pin: str,
                      protocol_pin: str) -> dict[str, Any]:
    require(type(value) is dict,
            "require the complete independently frozen V11 machine contract")
    expected = contract_document(source_pin, protocol_pin)
    require(value == expected,
            "reject a missing, altered, invented, or silently weakened V11 contract")
    require(len(value["future_build_policy"]["frozen_command_templates"]) == 2
            and value["phase_boundary"] == expected_phase_boundary(),
            "never count a future Zig source build as an actual experiment")
    return value


def source_owner_metadata(path: str, owner: os.stat_result,
                          observed_digest: str) -> dict[str, Any]:
    return {
        "path": path,
        "sha256": observed_digest,
        "bytes": owner.st_size,
        "device": owner.st_dev,
        "inode": owner.st_ino,
        "link_count": owner.st_nlink,
        "mode": format(stat.S_IMODE(owner.st_mode), "04o"),
    }


def read_descriptor(descriptor: int, expected: str, expected_size: int,
                    limit: int, label: str, *, executable: bool = False,
                    private: bool = False) -> tuple[dict[str, Any], bytes]:
    valid_digest(expected, label)
    require(type(expected_size) is int and 0 < expected_size <= limit,
            "bound the exact authenticated owner: " + label)
    before = os.fstat(descriptor)
    require(stat.S_ISREG(before.st_mode)
            and before.st_size == expected_size
            and before.st_nlink == 1,
            "reject an aliased, nonregular, or incorrectly sized owner: " + label)
    if executable:
        require(before.st_mode & 0o111,
                "require the pinned genuine compiler executable: " + label)
    if private:
        require(before.st_uid == os.geteuid()
                and stat.S_IMODE(before.st_mode) == 0o600,
                "require a fresh owner-only mode-0600 private snapshot: " + label)
    total = 0
    chunks: list[bytes] = []
    while True:
        part = os.read(descriptor, min(1024 * 1024, limit + 1 - total))
        if not part:
            break
        total += len(part)
        require(total <= limit, "reject an oversized owner: " + label)
        chunks.append(part)
    after = os.fstat(descriptor)
    require(
        (before.st_dev, before.st_ino, before.st_size, before.st_nlink,
         before.st_mtime_ns, before.st_ctime_ns)
        == (after.st_dev, after.st_ino, after.st_size, after.st_nlink,
            after.st_mtime_ns, after.st_ctime_ns),
        "the authenticated owner changed during its complete read: " + label,
    )
    raw = b"".join(chunks)
    require(total == expected_size and len(raw) == expected_size
            and digest(raw) == expected,
            "the independently frozen owner digest changed: " + label)
    return source_owner_metadata(label, after, expected), raw


def read_repository_owner(relative: str, expected: str, expected_size: int,
                          *, limit: int = MAX_SOURCE_BYTES) -> tuple[dict, bytes]:
    parts = checked_relative(relative)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        descriptor = os.open(parts[-1], flags, dir_fd=directory)
        try:
            return read_descriptor(descriptor, expected, expected_size,
                                   limit, relative)
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def read_absolute_owner(path: str, expected: str, expected_size: int,
                        executable: bool) -> tuple[dict, bytes]:
    require(type(path) is str and path.startswith("/")
            and "\x00" not in path and "\\" not in path,
            "require one exact authenticated absolute compiler owner")
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        return read_descriptor(descriptor, expected, expected_size,
                               MAX_COMPILER_BYTES, path,
                               executable=executable)
    finally:
        os.close(descriptor)


def load_authenticated_module(name: str, relative: str,
                              raw: bytes) -> types.ModuleType:
    require(type(name) is str and name.startswith("_rebar_owned_v11_"),
            "load only an independently authenticated first-party source tool")
    checked_relative(relative)
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "load only the exact already authenticated source bytes")
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / relative)
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    return module


def validate_zig_lock(value: dict[str, Any]) -> None:
    require(value.get("schema") == "rebar-official-language-toolchain-v1"
            and value.get("language") == "Zig"
            and value.get("version") == "0.16.0"
            and value.get("release_channel") == "stable"
            and value.get("platform") == "x86_64-linux"
            and value.get("archive_root") == "zig-x86_64-linux-0.16.0"
            and value.get("compiler_relative_path")
            == "zig-x86_64-linux-0.16.0/zig"
            and value.get("compiler_sha256")
            == TOOLCHAIN_OWNERS["zig"][1]
            and value.get("archive_sha256")
            == "70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00"
            and value.get("archive_bytes") == 55_478_392,
            "reject an unofficial, substituted, or network-fetched Zig toolchain")


def validate_phase_one(value: dict[str, Any]) -> None:
    denominator = value.get("denominator")
    gate = value.get("phase_gate")
    runtime = value.get("runtime")
    boundaries = value.get("audit_boundaries")
    require(value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and value.get("version") == 1
            and type(denominator) is dict
            and denominator.get("available_frozen_vector_case_executions") == 31_237
            and denominator.get("final_required_case_execution_denominator") == 31_237
            and tuple(denominator.get("counted_suite_ids", ())) == SUITE_IDS
            and denominator.get("private_upstream_methods_outside_public_denominator")
            == 13
            and type(gate) is dict and gate.get("status") == "PASS"
            and gate.get("all_obligations_mapped") is True
            and gate.get("final_holdout_authorized") is False
            and type(runtime) is dict
            and runtime.get("python_implementation") == "CPython"
            and runtime.get("python_version") == "3.14.6"
            and type(boundaries) is dict
            and boundaries.get("hidden_cases_read") == 0
            and boundaries.get("final_cases_read") == 0,
            "preserve all 13 original suites, 31,237 cases, and 13 private waivers")


def validate_corrected_v3(value: dict[str, Any]) -> None:
    history = value.get("frozen_v21_history")
    effects = value.get("verification_effects")
    families = value.get("families")
    phase = value.get("phase_one")
    require(value.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v3-source-freeze"
            and value.get("version") == 3
            and value.get("family_count") == 6
            and value.get("source_owner_count") == 25
            and value.get("suite_count") == 13
            and value.get("case_execution_denominator") == 31_237
            and value.get("pairwise_shared_semantic_source_count") == 0
            and type(phase) is dict
            and phase.get("named_private_waiver_count") == 13,
            "preserve the exact independent, corrected six-family V3 producer")
    require(type(history) is dict
            and history.get("actual_evidence_owner_count") == 103
            and history.get("authenticated_reference_path_count") == 108
            and history.get("new_actual_campaign_owner_count") == 30,
            "preserve 103 actual V21 evidence owners and 108 history references")
    require(type(effects) is dict
            and effects.get("actual_candidate_imports") == 0
            and effects.get("actual_candidate_workers") == 0
            and effects.get("actual_source_builds") == 0
            and effects.get("actual_native_activations") == 0
            and effects.get("actual_native_libraries_loaded") == 0
            and effects.get("actual_network_requests") == 0
            and effects.get("actual_subprocesses_started") == 0
            and effects.get("clock_samples") == 0
            and effects.get("hidden_cases_read") == 0
            and effects.get("candidate_qualified_count") == 0
            and effects.get("holdout") == "NOT OPENED"
            and effects.get("performance") == "NOT MEASURED",
            "do not turn corrected V3 source verification into an experiment")
    require(type(families) is list,
            "require every independently frozen candidate family")
    zig = [item for item in families
           if type(item) is dict and item.get("family") == "zig"]
    require(len(zig) == 1 and zig[0].get("owned_source_count") == 3
            and zig[0].get("adapter_relative") == ORIGINAL_ADAPTER,
            "retain exactly the original independent three-owner Zig family")
    actual = zig[0].get("sources")
    expected = [
        {"relative": path, "sha256": owner[0], "size_bytes": owner[1]}
        for path, owner in sorted(SOURCE_OWNERS.items())
    ]
    require(type(actual) is list and sorted(
        actual, key=lambda item: item.get("relative", ""),
    ) == expected,
        "reject cross-family, missing, repeated, or altered Zig semantic owners")


def validate_v21(inputs: dict[str, Any], summary: dict[str, Any]) -> None:
    require(inputs.get("schema") == "rebar-candidate-current-overview-v21-inputs"
            and inputs.get("version") == 21
            and inputs.get("repository_evidence_owner_count") == 103
            and inputs.get("all_digest_addressed_history_path_count") == 108
            and inputs.get("current_source_owner_count") == 25
            and inputs.get("candidate_qualified_count") == 0
            and inputs.get("suite_count") == 13
            and inputs.get("full_case_denominator") == 31_237
            and inputs.get("private_waiver_count") == 13
            and inputs.get("python") == "3.14.6",
            "retain the exact counted current V21 evidence graph")
    require(summary.get("schema") == "rebar-candidate-current-overview-v21-summary"
            and summary.get("status") == "PASS"
            and summary.get("repository_evidence_owner_count") == 103
            and summary.get("authenticated_digest_addressed_history_paths") == 108
            and summary.get("qualified_candidate_count") == 0
            and summary.get("suite_count") == 13
            and summary.get("full_case_denominator") == 31_237
            and summary.get("private_waiver_count") == 13,
            "do not change either V21 evidence denominator")
    snapshot = summary.get("snapshot")
    require(type(snapshot) is dict
            and snapshot.get("frozen_independent_engine_family_count") == 6
            and snapshot.get("current_source_owner_count") == 25
            and snapshot.get("zig_actual_semantic_mismatch_count") == 1_764
            and snapshot.get("zig_verified_passing_case_executions") == 3_583
            and snapshot.get("qualified_candidate_count") == 0
            and tuple(snapshot.get("suite_ids", ())) == SUITE_IDS,
            "never erase the actual 1,764 original Zig matching failures")
    zig_gate = snapshot.get("zig_full_gate")
    require(type(zig_gate) is dict
            and zig_gate.get("gate_status") == "FAIL"
            and zig_gate.get("actual_semantic_mismatch_count") == 1_764
            and zig_gate.get("qualified_candidate_case_executions") == 0,
            "an unbuilt scanner repair cannot qualify the failed Zig candidate")
    for label, value in (("V21 inputs", inputs),
                         ("V21 summary", summary),
                         ("V21 snapshot", snapshot)):
        require(value.get("final_holdout_opened") is False
                and value.get("final_comparison_cases_generated") is False
                and value.get("final_comparison_planned_case_count")
                == FINAL_PLANNED_CASE_COUNT
                and value.get("performance") == "NOT MEASURED"
                and value.get("memory") == "NOT MEASURED",
                "preserve unopened and unmeasured " + label)
    require(summary.get("hidden_cases_read") == 0
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0
            and summary.get("winner_selected") is False,
            "a Zig build source freeze cannot time or select a candidate")


def validate_v7(value: dict[str, Any]) -> None:
    require(value.get("schema")
            == "rebar-phase2-owned-native-source-build-v7-source-freeze"
            and value.get("version") == 7
            and value.get("family_count") == 6
            and value.get("source_owner_count") == 25
            and value.get("qualified_candidate_count") == 0,
            "preserve the exact independent first-party V7 builder")
    policy = value.get("build_policy")
    require(type(policy) is dict
            and policy.get("phase_names") == list(PHASE_NAMES)
            and policy.get("private_root_prefix")
            == "/tmp/rebar-phase2-native-build-v7-"
            and policy.get("bridge_runpath") == "$ORIGIN"
            and policy.get("rpath") == "FORBIDDEN"
            and policy.get("zig_engine_strip_flag") == "-fstrip"
            and policy.get("network_requests") == 0
            and policy.get("external_regular_expression_packages") == 0
            and policy.get("cross_family_matching_dependencies") == 0
            and policy.get("stdlib_matching_delegation") == 0
            and policy.get("fallback") == "FORBIDDEN"
            and policy.get("prebuilt_artifact") == "FORBIDDEN"
            and type(policy.get("v7_future_process_count_by_family")) is dict
            and policy["v7_future_process_count_by_family"].get("zig")
            == EXPECTED_PROCESS_COUNT,
            "preserve all original V7 first-party Zig process and engine rules")
    oracle = value.get("oracle")
    require(type(oracle) is dict
            and oracle.get("implementation") == "CPython"
            and oracle.get("version") == "3.14.6"
            and oracle.get("suite_count") == 13
            and oracle.get("case_execution_count") == 31_237,
            "preserve the unchanged V7 original correctness denominator")
    families = value.get("families")
    require(type(families) is list, "require the complete V7 owner inventory")
    found = [item for item in families
             if type(item) is dict and item.get("id") == "zig"]
    expected = [owner_document(path, owner)
                for path, owner in sorted(SOURCE_OWNERS.items())]
    require(len(found) == 1
            and found[0].get("language") == "Zig"
            and found[0].get("artifacts")
            == {"bridge": BRIDGE_FILENAME, "engine": ENGINE_FILENAME}
            and type(found[0].get("owners")) is list
            and sorted(found[0]["owners"], key=lambda item: item.get("path", ""))
            == expected,
            "never replace the authenticated V7 first-party Zig semantic family")
    raw = value.get("raw_elf_forensics")
    require(type(raw) is dict
            and raw.get("format") == "ELF64-LITTLE-ENDIAN-X86-64-ET-DYN"
            and raw.get("full_binary_maximum_bytes") == MAX_BINARY_BYTES
            and raw.get("record_before_reproducibility_classification") is True
            and raw.get("additional_process_count") == 0
            and raw.get("actual_v7_builds") == "NOT RUN",
            "retain authenticated complete-byte V7 ELF source forensics")
    boundary = value.get("phase_boundary")
    require(type(boundary) is dict
            and boundary.get("compiler_processes_started") == 0
            and boundary.get("candidate_imports") == 0
            and boundary.get("clock_samples") == 0
            and boundary.get("holdout") == "NOT OPENED",
            "do not count an inherited V7 build plan as executed")


def validate_overlay(value: dict[str, Any], derived: bytes) -> None:
    require(value.get("schema") == OVERLAY_SCHEMA
            and value.get("version") == 1,
            "authenticate the exact separately published Zig scanner overlay")
    policy = value.get("apply_policy")
    repair = value.get("repair")
    history = value.get("published_history")
    boundary = value.get("phase_boundary")
    require(type(policy) is dict
            and policy.get("private_root_parent") == "/tmp"
            and policy.get("private_root_prefix") == PRIVATE_ROOT_PREFIX
            and policy.get("phase_names") == list(PHASE_NAMES)
            and policy.get("relative_destination")
            == "candidates/zig/py_bridge.c"
            and policy.get("existing_destination") == "FORBIDDEN"
            and policy.get("workspace_destination") == "FORBIDDEN"
            and policy.get("candidate_source_mutation") == "FORBIDDEN"
            and policy.get("private_directory_mode") == "0700"
            and policy.get("private_file_mode") == "0600"
            and policy.get("explicit_apply_required") is True,
            "retain the sealed sibling-phase overlay prefix and exclusive destination")
    require(type(repair) is dict
            and type(repair.get("derived_source")) is dict
            and repair["derived_source"].get("sha256") == DERIVED_BRIDGE_SHA256
            and repair["derived_source"].get("bytes") == DERIVED_BRIDGE_BYTES
            and repair["derived_source"].get("materialized") is False
            and repair.get("proposed_repair_tested") is False
            and type(derived) is bytes
            and len(derived) == DERIVED_BRIDGE_BYTES
            and digest(derived) == DERIVED_BRIDGE_SHA256,
            "derive only the exact committed one-block private Zig bridge")
    require(type(history) is dict
            and history.get("authoritative_counted_evidence_owner_count") == 103
            and history.get("authenticated_digest_addressed_history_paths") == 108
            and history.get("qualified_candidate_count") == 0,
            "preserve every previously authenticated genuine evidence owner")
    require(type(boundary) is dict
            and boundary.get("source_apply_count") == 0
            and boundary.get("compiler_processes_started") == 0
            and boundary.get("candidate_imports") == 0
            and boundary.get("clock_samples") == 0
            and boundary.get("holdout") == "NOT OPENED",
            "do not execute the separately frozen scanner repair in source mode")


def validate_recovered_c_failure(
    protected: dict[str, bytes],
    protected_owners: dict[str, dict[str, Any]],
    overlay: types.ModuleType,
) -> dict[str, Any]:
    archive_raw = protected[RECOVERED_C_ARCHIVE]
    receipt = strict_json(protected[RECOVERED_C_RECEIPT],
                          "actual recovered C failure receipt")
    try:
        plain = gzip.decompress(archive_raw)
    except (OSError, EOFError, ValueError) as error:
        raise FreezeError("reject altered recovered C failure archive") from error
    require(len(plain) == 5_941
            and digest(plain)
            == "5aa8b513eec30c7ab13bc4b638a5b5026a6f03821f8cd411f6ea3201b0813cfd",
            "authenticate every preserved byte of the genuine C failure")
    report = strict_json(plain, "actual recovered C failure report")
    failure = report.get("failure")
    aggregate = failure.get("actual_aggregate_process") \
        if type(failure) is dict else None
    require(report.get("schema")
            == "rebar-owned-repaired-c-original-campaign-v2-actual-recovered-campaign"
            and report.get("status") == "FAIL"
            and report.get("family") == "c"
            and report.get("label") == "phase2-v9-original-p0"
            and report.get("case_execution_denominator") == 31_237
            and report.get("suite_count") == 13
            and report.get("named_private_waiver_count") == 13
            and report.get("historical_evidence_owner_count")
            == HISTORICAL_V21_EVIDENCE_OWNER_COUNT
            and report.get("historical_authenticated_reference_count")
            == HISTORICAL_V21_REFERENCE_COUNT
            and report.get("infrastructure_failure_count") == 1
            and report.get("candidate_qualified") is False
            and report.get("all_original_suite_evidence_preserved") is False
            and report.get("semantic_mismatch_count") == "NOT MEASURED"
            and report.get("verified_passing_case_count") == "NOT MEASURED"
            and report.get("completed_suite_count") == "NOT MEASURED"
            and report.get("original_native_restored") is True
            and report.get("hidden_cases_read") == 0
            and report.get("benchmark_files_read") == 0
            and report.get("clock_samples") == 0
            and report.get("timing_trials_run") == 0
            and report.get("holdout") == "NOT OPENED"
            and report.get("performance") == "NOT MEASURED"
            and report.get("memory") == "NOT MEASURED",
            "preserve the real failed C run; never invent C matching results")
    require(type(aggregate) is dict
            and aggregate.get("actual_aggregate_processes") == 1
            and aggregate.get("returncode") == 1
            and aggregate.get("timed_out") is False
            and aggregate.get("stdout_bytes") == 517
            and aggregate.get("stdout_sha256")
            == "93899f2cfc24a638785af66e683ca2f0866488be9cfbcdc2ffdd73be1b8e3f65"
            and aggregate.get("stderr_bytes") == 0
            and aggregate.get("stderr_sha256") == digest(b""),
            "preserve the sole actual failed C aggregate process")
    try:
        stdout = base64.b64decode(
            aggregate["stdout_base64"].encode("ascii"), validate=True,
        )
        stderr = base64.b64decode(
            aggregate["stderr_base64"].encode("ascii"), validate=True,
        )
    except (ValueError, UnicodeError) as error:
        raise FreezeError("reject altered actual C failure process streams") from error
    require(len(stdout) == aggregate["stdout_bytes"]
            and digest(stdout) == aggregate["stdout_sha256"]
            and stderr == b"",
            "bind the actual failing C process to every original output byte")
    entry = strict_json(stdout, "preserved C V9 entry infrastructure failure")
    require(entry.get("schema") == "rebar-frozen-python-re-p0-candidate-v9-entry-failure"
            and entry.get("status") == "FAIL"
            and entry.get("error_type") == "AttributeError"
            and entry.get("error_message")
            == "'Namespace' object has no attribute 'runner_source_sha256'"
            and entry.get("actual_candidate_workers") == 0
            and entry.get("actual_reference_workers") == 0
            and entry.get("actual_source_builds") == 0
            and entry.get("actual_native_activations") == 0
            and entry.get("candidate_qualified") is False
            and entry.get("hidden_cases_read") == 0
            and entry.get("clock_samples") == 0
            and entry.get("holdout") == "NOT OPENED",
            "distinguish the failed C entry from a completed matching campaign")
    actual_archive = receipt.get("archive")
    observed_archive = protected_owners[RECOVERED_C_ARCHIVE]
    observed_receipt = protected_owners[RECOVERED_C_RECEIPT]
    require(type(actual_archive) is dict
            and receipt.get("schema")
            == "rebar-owned-repaired-c-original-campaign-v2-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("family") == "c"
            and receipt.get("label") == "phase2-v9-original-p0"
            and receipt.get("historical_evidence_owner_count")
            == HISTORICAL_V21_EVIDENCE_OWNER_COUNT
            and receipt.get("historical_authenticated_reference_count")
            == HISTORICAL_V21_REFERENCE_COUNT
            and receipt.get("uncompressed_bytes") == len(plain)
            and receipt.get("uncompressed_sha256") == digest(plain)
            and receipt.get("original_native_restored") is True
            and receipt.get("holdout") == "NOT OPENED"
            and actual_archive.get("relative") == RECOVERED_C_ARCHIVE
            and actual_archive.get("sha256") == RECOVERED_C_ARCHIVE_SHA256
            and actual_archive.get("size_bytes") == len(archive_raw)
            and actual_archive.get("device") == observed_archive["device"]
            and actual_archive.get("inode") == observed_archive["inode"]
            and actual_archive.get("mode") == 0o600
            and actual_archive.get("exclusive_creation") is True
            and actual_archive.get("same_inode_readback_verified") is True
            and actual_archive.get("file_fsync_completed") is True
            and actual_archive.get("directory_fsync_completed") is True
            and (observed_archive["device"], observed_archive["inode"])
            != (observed_receipt["device"], observed_receipt["inode"]),
            "authenticate both distinct durable recovered C failure owners")

    require(callable(getattr(overlay, "discover_evidence", None))
            and callable(getattr(overlay, "checked_read", None))
            and callable(getattr(overlay, "strict_json", None))
            and type(getattr(overlay, "SUPPORT", None)) is dict,
            "use only the committed overlay's authenticated historical graph")
    history: dict[str, str] = {}
    for path in (
        "docs/evidence/candidate-current-overview-v19.inputs.json",
        "docs/evidence/candidate-current-overview-v19.json",
    ):
        valid_digest(overlay.SUPPORT.get(path), path)
        value = overlay.strict_json(
            overlay.checked_read(path, overlay.SUPPORT[path]), path,
        )
        overlay.discover_evidence(value, history)
    require(len(history) == 76,
            "independently preserve the complete historical V19 evidence graph")
    old_summary_path = "docs/evidence/candidate-current-overview-v20.json"
    valid_digest(overlay.SUPPORT.get(old_summary_path), old_summary_path)
    old_summary = overlay.strict_json(
        overlay.checked_read(old_summary_path,
                             overlay.SUPPORT[old_summary_path]),
        old_summary_path,
    )
    old_snapshot = old_summary.get("snapshot")
    old_build = old_snapshot.get("c_v8_repaired_build") \
        if type(old_snapshot) is dict else None
    require(type(old_build) is dict and old_build.get("status") == "PASS",
            "retain the two real V20 source-build history owners")
    for role in ("archive", "receipt"):
        item = old_build.get(role)
        require(type(item) is dict and type(item.get("path")) is str
                and item["path"].startswith("oracle/phase2/evidence/")
                and item["path"] not in history,
                "retain each distinct, previously published V20 evidence owner")
        history[item["path"]] = valid_digest(item.get("sha256"), item["path"])
    require(len(history) == 78,
            "preserve exactly the 78 genuinely authenticated V20 references")
    current_inputs = strict_json(
        protected["docs/evidence/candidate-current-overview-v21.inputs.json"],
        "historical V21 inputs",
    )
    campaign = current_inputs.get("repaired_c_original_campaign")
    require(type(campaign) is dict,
            "retain all previously frozen V21 C campaign evidence")
    additional: dict[str, str] = {}
    overlay.discover_evidence(campaign, additional)
    require(len(additional) == 30
            and not (set(additional) & set(history)),
            "preserve exactly the 30 distinct V21 campaign history references")
    history.update(additional)
    require(len(history) == HISTORICAL_V21_REFERENCE_COUNT
            and sum(path.startswith("oracle/phase2/evidence/")
                    for path in history) == 78
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in history) == 30,
            "reconstruct the exact 108-reference historical V21 denominator")
    require(RECOVERED_C_ARCHIVE not in history
            and RECOVERED_C_RECEIPT not in history,
            "never silently recount a historical evidence file as new")
    history[RECOVERED_C_ARCHIVE] = RECOVERED_C_ARCHIVE_SHA256
    history[RECOVERED_C_RECEIPT] = RECOVERED_C_RECEIPT_SHA256
    require(len(history) == HISTORICAL_V22_REFERENCE_COUNT
            and HISTORICAL_V21_EVIDENCE_OWNER_COUNT
            + ADDITIONAL_RECOVERED_C_EVIDENCE_OWNER_COUNT
            == HISTORICAL_V22_EVIDENCE_OWNER_COUNT
            and sum(path.startswith("oracle/phase2/evidence/")
                    for path in history) == 80
            and sum(path.startswith("experiments/rust_public_practice_v1/")
                    for path in history) == 30,
            "authenticate the real 105-owner, 110-reference V22 baseline")
    return {
        "archive": observed_archive,
        "receipt": observed_receipt,
        "archive_status": "FAIL",
        "receipt_status": "PASS",
        "actual_aggregate_process_count": 1,
        "actual_candidate_worker_count": 0,
        "infrastructure_failure_count": 1,
        "semantic_mismatch_count": "NOT MEASURED",
        "verified_passing_case_count": "NOT MEASURED",
        "original_native_restored": True,
        "historical_v21_evidence_owner_count":
            HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
        "historical_v21_authenticated_reference_count":
            HISTORICAL_V21_REFERENCE_COUNT,
        "historical_v22_evidence_owner_count":
            HISTORICAL_V22_EVIDENCE_OWNER_COUNT,
        "historical_v22_authenticated_reference_count":
            HISTORICAL_V22_REFERENCE_COUNT,
        "_authenticated_reference_digests": dict(sorted(history.items())),
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }


def check_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PINNED_PYTHON
            and sys.implementation.cache_tag == "cpython-314"
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True,
            "run only isolated, bytecode-free, independently pinned CPython 3.14.6")



def validate_published_v22(
    protected: dict[str, bytes],
) -> None:
    inputs = strict_json(
        protected["docs/evidence/candidate-current-overview-v22.inputs.json"],
        "published immutable V22 overview inputs",
    )
    summary = strict_json(
        protected["docs/evidence/candidate-current-overview-v22.json"],
        "published immutable V22 overview",
    )
    require(
        inputs.get("schema") == "rebar-candidate-current-overview-v22-inputs"
        and inputs.get("version") == 22
        and inputs.get("repository_evidence_owner_count")
        == HISTORICAL_V22_EVIDENCE_OWNER_COUNT
        and inputs.get("all_digest_addressed_history_path_count")
        == HISTORICAL_V22_REFERENCE_COUNT
        and inputs.get("preserved_v21_repository_evidence_owner_count")
        == HISTORICAL_V21_EVIDENCE_OWNER_COUNT
        and inputs.get("preserved_v21_digest_addressed_history_path_count")
        == HISTORICAL_V21_REFERENCE_COUNT
        and inputs.get("new_corrected_c_campaign_repository_evidence_owner_count")
        == ADDITIONAL_RECOVERED_C_EVIDENCE_OWNER_COUNT
        and inputs.get("full_case_denominator") == 31_237
        and inputs.get("suite_count") == 13
        and inputs.get("private_waiver_count") == 13
        and inputs.get("candidate_qualified_count") == 0,
        "authenticate the actual frozen V22 baseline without treating it as current",
    )
    snapshot = summary.get("snapshot")
    require(
        summary.get("schema") == "rebar-candidate-current-overview-v22-summary"
        and summary.get("status") == "PASS"
        and summary.get("repository_evidence_owner_count")
        == HISTORICAL_V22_EVIDENCE_OWNER_COUNT
        and summary.get("authenticated_digest_addressed_history_paths")
        == HISTORICAL_V22_REFERENCE_COUNT
        and summary.get("qualified_candidate_count") == 0
        and summary.get("full_case_denominator") == 31_237
        and summary.get("suite_count") == 13
        and summary.get("private_waiver_count") == 13
        and summary.get("c_repaired_candidate_worker_count") == 0
        and summary.get("c_repaired_infrastructure_failure_count") == 1
        and summary.get("c_repaired_semantic_mismatch_count") == "NOT MEASURED"
        and summary.get("c_repaired_verified_passing_case_count")
        == "NOT MEASURED"
        and type(snapshot) is dict
        and snapshot.get("all_digest_addressed_history_path_count")
        == HISTORICAL_V22_REFERENCE_COUNT
        and snapshot.get("preserved_v21_digest_addressed_history_path_count")
        == HISTORICAL_V21_REFERENCE_COUNT
        and snapshot.get("preserved_v21_repository_evidence_owner_count")
        == HISTORICAL_V21_EVIDENCE_OWNER_COUNT
        and snapshot.get("frozen_independent_engine_family_count") == 6
        and snapshot.get("current_source_owner_count") == 25
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("zig_actual_semantic_mismatch_count") == 1_764
        and snapshot.get("zig_verified_passing_case_executions") == 3_583
        and tuple(snapshot.get("suite_ids", ())) == SUITE_IDS,
        "preserve all genuine V22 and original Zig results",
    )
    for label, value in (
        ("published V22 inputs", inputs),
        ("published V22 overview", summary),
        ("published V22 snapshot", snapshot),
    ):
        require(
            value.get("final_holdout_opened") is False
            and value.get("final_comparison_cases_generated") is False
            and value.get("final_comparison_planned_case_count")
            == FINAL_PLANNED_CASE_COUNT
            and value.get("performance") == "NOT MEASURED"
            and value.get("memory") == "NOT MEASURED"
            and value.get("winner_selected") is False,
            "preserve the closed holdout and unmeasured " + label,
        )
    require(
        summary.get("hidden_cases_read") == 0
        and summary.get("clock_samples") == 0
        and summary.get("timing_trials_run") == 0
        and snapshot.get("hidden_cases_read") == 0
        and snapshot.get("clock_samples") == 0
        and snapshot.get("timing_trials_run") == 0,
        "authenticate V22 without hidden cases, clocks, or timing",
    )


def validate_published_v23(
    protected: dict[str, bytes],
) -> None:
    inputs = strict_json(
        protected["docs/evidence/candidate-current-overview-v23.inputs.json"],
        "published immutable current V23 overview inputs",
    )
    summary = strict_json(
        protected["docs/evidence/candidate-current-overview-v23.json"],
        "published immutable current V23 overview",
    )
    require(
        inputs.get("schema") == "rebar-candidate-current-overview-v23-inputs"
        and inputs.get("version") == 23
        and inputs.get("repository_evidence_owner_count")
        == CURRENT_EVIDENCE_OWNER_COUNT
        and inputs.get("all_digest_addressed_history_path_count")
        == CURRENT_AUTHENTICATED_REFERENCE_COUNT
        and inputs.get("preserved_v22_repository_evidence_owner_count")
        == HISTORICAL_V22_EVIDENCE_OWNER_COUNT
        and inputs.get("preserved_v22_digest_addressed_history_path_count")
        == HISTORICAL_V22_REFERENCE_COUNT
        and inputs.get("full_case_denominator") == 31_237
        and inputs.get("suite_count") == 13
        and inputs.get("private_waiver_count") == 13
        and inputs.get("candidate_qualified_count") == 0,
        "authenticate the current published 135-owner, 140-reference V23",
    )
    snapshot = summary.get("snapshot")
    require(
        summary.get("schema") == "rebar-candidate-current-overview-v23-summary"
        and summary.get("status") == "PASS"
        and summary.get("repository_evidence_owner_count")
        == CURRENT_EVIDENCE_OWNER_COUNT
        and summary.get("authenticated_digest_addressed_history_paths")
        == CURRENT_AUTHENTICATED_REFERENCE_COUNT
        and summary.get("preserved_v22_repository_evidence_owner_count")
        == HISTORICAL_V22_EVIDENCE_OWNER_COUNT
        and summary.get("qualified_candidate_count") == 0
        and summary.get("full_case_denominator") == 31_237
        and summary.get("suite_count") == 13
        and summary.get("private_waiver_count") == 13
        and summary.get("c_repaired_semantic_mismatch_count") == 1_262
        and summary.get("c_repaired_verified_passing_case_count") == 7_325
        and summary.get("c_repaired_candidate_worker_count") == 13
        and summary.get("c_repaired_infrastructure_failure_count") == 0
        and type(snapshot) is dict
        and snapshot.get("all_digest_addressed_history_path_count")
        == CURRENT_AUTHENTICATED_REFERENCE_COUNT
        and snapshot.get("preserved_v22_digest_addressed_history_path_count")
        == HISTORICAL_V22_REFERENCE_COUNT
        and snapshot.get("preserved_v22_repository_evidence_owner_count")
        == HISTORICAL_V22_EVIDENCE_OWNER_COUNT
        and snapshot.get("frozen_independent_engine_family_count") == 6
        and snapshot.get("current_source_owner_count") == 25
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("zig_actual_semantic_mismatch_count") == 1_764
        and snapshot.get("zig_verified_passing_case_executions") == 3_583
        and tuple(snapshot.get("suite_ids", ())) == SUITE_IDS,
        "bind the current V23 overview to all actual C and Zig outcomes",
    )
    completed = snapshot.get("c_v10_repaired_original_campaign")
    require(
        type(completed) is dict
        and completed.get("status") == "FAIL"
        and completed.get("semantic_mismatch_count") == 1_262
        and completed.get("verified_passing_case_count") == 7_325
        and completed.get("actual_candidate_workers") == 13
        and completed.get("infrastructure_failure_count") == 0,
        "preserve the complete failed original C campaign in published V23",
    )
    for label, value in (
        ("published V23 inputs", inputs),
        ("published V23 overview", summary),
        ("published V23 snapshot", snapshot),
    ):
        require(
            value.get("final_holdout_opened") is False
            and value.get("final_comparison_cases_generated") is False
            and value.get("final_comparison_planned_case_count")
            == FINAL_PLANNED_CASE_COUNT
            and value.get("performance") == "NOT MEASURED"
            and value.get("memory") == "NOT MEASURED"
            and value.get("winner_selected") is False,
            "preserve the closed holdout and unmeasured " + label,
        )
    require(
        summary.get("hidden_cases_read") == 0
        and summary.get("clock_samples") == 0
        and summary.get("timing_trials_run") == 0
        and snapshot.get("hidden_cases_read") == 0
        and snapshot.get("clock_samples") == 0
        and snapshot.get("timing_trials_run") == 0,
        "authenticate V23 without hidden cases, clocks, or timing",
    )


def stream_complete_c_archive(
    raw: bytes,
    expected_bytes: int,
    expected_sha256: str,
    label: str,
    *,
    retain: bool = False,
) -> bytes | None:
    require(
        type(raw) is bytes
        and type(expected_bytes) is int
        and 0 < expected_bytes <= MAX_COMPLETED_C_EXPANDED_BYTES
        and (not retain or expected_bytes <= MAX_SOURCE_BYTES),
        "bound the complete original C evidence stream: " + label,
    )
    valid_digest(expected_sha256, label + " complete uncompressed digest")
    observed = hashlib.sha256()
    count = 0
    chunks: list[bytes] = []
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as compressed:
            while True:
                block = compressed.read(64 * 1024)
                if not block:
                    break
                count += len(block)
                require(
                    count <= expected_bytes
                    and count <= MAX_COMPLETED_C_EXPANDED_BYTES,
                    "reject an oversized complete original C report: " + label,
                )
                observed.update(block)
                if retain:
                    chunks.append(block)
    except (OSError, EOFError, ValueError) as error:
        raise FreezeError(
            "reject a damaged complete original C archive: " + label
        ) from error
    require(
        count == expected_bytes and observed.hexdigest() == expected_sha256,
        "authenticate every uncompressed C result byte: " + label,
    )
    return b"".join(chunks) if retain else None


def validate_c_evidence_metadata(
    item: Any,
    actual: dict[str, Any],
    path: str,
    *,
    durable: bool = False,
) -> None:
    require(
        type(item) is dict
        and item.get("relative") == path
        and item.get("sha256") == actual["sha256"]
        and item.get("size_bytes") == actual["bytes"]
        and item.get("device") == actual["device"]
        and item.get("inode") == actual["inode"]
        and item.get("mode") == 0o600
        and actual["mode"] == "0600"
        and actual["link_count"] == 1,
        "bind original C evidence to its exact private original inode: " + path,
    )
    if durable:
        require(
            item.get("exclusive_creation") is True
            and item.get("same_inode_readback_verified") is True
            and item.get("file_fsync_completed") is True
            and item.get("directory_fsync_completed") is True,
            "require every original C archive durability guarantee: " + path,
        )


def validate_completed_c_campaign(
    protected: dict[str, bytes],
    protected_owners: dict[str, dict[str, Any]],
    overlay: types.ModuleType,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_published_v22(protected)
    validate_published_v23(protected)
    previous = validate_recovered_c_failure(
        protected, protected_owners, overlay,
    )
    history = previous.pop("_authenticated_reference_digests", None)
    require(
        type(history) is dict
        and len(history) == HISTORICAL_V22_REFERENCE_COUNT
        and previous.get("historical_v22_evidence_owner_count")
        == HISTORICAL_V22_EVIDENCE_OWNER_COUNT
        and previous.get("historical_v22_authenticated_reference_count")
        == HISTORICAL_V22_REFERENCE_COUNT,
        "start from the independently reconstructed real V22 history",
    )

    identities: set[tuple[int, int]] = set()
    suite_results: list[dict[str, Any]] = []
    passing = 0
    mismatches = 0
    total_cases = 0
    for (suite, denominator, expected_status, expected_mismatches,
         archive_path, archive_sha256, archive_bytes, receipt_path,
         receipt_sha256, receipt_bytes, expanded_bytes, expanded_sha256
         ) in COMPLETED_C_SUITE_EVIDENCE:
        require(
            suite not in {row["suite"] for row in suite_results}
            and expected_status in ("PASS", "FAIL")
            and type(denominator) is int and denominator > 0
            and type(expected_mismatches) is int
            and 0 <= expected_mismatches <= denominator
            and (expected_status == "PASS") == (expected_mismatches == 0)
            and SUPPORT_OWNERS.get(archive_path)
            == (archive_sha256, archive_bytes)
            and SUPPORT_OWNERS.get(receipt_path)
            == (receipt_sha256, receipt_bytes)
            and archive_path not in history and receipt_path not in history,
            "reject a reused, weakened, or invented original C suite: " + suite,
        )
        archive_owner = protected_owners[archive_path]
        receipt_owner = protected_owners[receipt_path]
        for owner in (archive_owner, receipt_owner):
            identity = (owner["device"], owner["inode"])
            require(
                owner["mode"] == "0600"
                and owner["link_count"] == 1
                and identity not in identities,
                "require 30 distinct genuinely private C evidence owners",
            )
            identities.add(identity)
        receipt = strict_json(
            protected[receipt_path],
            "complete original C worker receipt: " + suite,
        )
        require(
            receipt.get("schema")
            == "rebar-frozen-python-re-p0-candidate-worker-v7-"
               "durable-suite-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("candidate_status") == expected_status
            and receipt.get("candidate_family") == "c"
            and receipt.get("label") == COMPLETED_C_CAMPAIGN_LABEL
            and receipt.get("suite") == suite
            and receipt.get("case_execution_denominator") == denominator
            and receipt.get("phase_one_case_execution_denominator")
            == 31_237
            and receipt.get("genuine_original_suite") is True
            and receipt.get("all_original_records_and_mismatches_preserved")
            is True
            and receipt.get("mismatch_count") == expected_mismatches
            and receipt.get("uncompressed_bytes") == expanded_bytes
            and receipt.get("uncompressed_sha256") == expanded_sha256
            and receipt.get("historical_evidence_owner_count")
            == HISTORICAL_V21_EVIDENCE_OWNER_COUNT
            and receipt.get("historical_authenticated_reference_count")
            == HISTORICAL_V21_REFERENCE_COUNT
            and receipt.get("candidate_qualified") is False
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("memory") == "NOT MEASURED"
            and receipt.get("winner_selected") is False,
            "authenticate the complete real C worker receipt: " + suite,
        )
        validate_c_evidence_metadata(
            receipt.get("archive"), archive_owner, archive_path, durable=True,
        )
        stream_complete_c_archive(
            protected[archive_path], expanded_bytes, expanded_sha256, suite,
        )
        history[archive_path] = archive_sha256
        history[receipt_path] = receipt_sha256
        total_cases += denominator
        mismatches += expected_mismatches
        if expected_status == "PASS":
            passing += denominator
        suite_results.append({
            "suite": suite,
            "status": expected_status,
            "case_execution_denominator": denominator,
            "genuine_original_suite": True,
            "actual_worker_started": True,
            "mismatch_count": expected_mismatches,
            "archive": archive_owner,
            "receipt": receipt_owner,
            "complete_uncompressed_bytes": expanded_bytes,
            "complete_uncompressed_sha256": expanded_sha256,
        })

    original_archive_path, original_archive_sha, _original_archive_size = (
        COMPLETED_C_AGGREGATE_OWNERS["original_archive"]
    )
    original_receipt_path, original_receipt_sha, _original_receipt_size = (
        COMPLETED_C_AGGREGATE_OWNERS["original_receipt"]
    )
    outer_archive_path, outer_archive_sha, _outer_archive_size = (
        COMPLETED_C_AGGREGATE_OWNERS["outer_archive"]
    )
    outer_receipt_path, outer_receipt_sha, _outer_receipt_size = (
        COMPLETED_C_AGGREGATE_OWNERS["outer_receipt"]
    )
    for path, expected_sha256, expected_size in (
        COMPLETED_C_AGGREGATE_OWNERS.values()
    ):
        require(
            path not in history
            and SUPPORT_OWNERS.get(path) == (expected_sha256, expected_size),
            "require a distinct hash-pinned actual C aggregate owner: " + path,
        )
        owner = protected_owners[path]
        identity = (owner["device"], owner["inode"])
        require(
            owner["mode"] == "0600"
            and owner["link_count"] == 1
            and identity not in identities,
            "reject a reused C aggregate or publication-receipt inode",
        )
        identities.add(identity)
        history[path] = expected_sha256

    original_receipt = strict_json(
        protected[original_receipt_path],
        "actual complete-original C aggregate publication receipt",
    )
    outer_receipt = strict_json(
        protected[outer_receipt_path],
        "actual recovered C campaign publication receipt",
    )
    require(
        original_receipt.get("schema")
        == "rebar-frozen-python-re-p0-candidate-v9-"
           "durable-publication-receipt"
        and original_receipt.get("status") == "PASS"
        and original_receipt.get("candidate_status") == "FAIL"
        and original_receipt.get("candidate_family") == "c"
        and original_receipt.get("label") == COMPLETED_C_CAMPAIGN_LABEL
        and original_receipt.get("suite_count") == 13
        and original_receipt.get("case_execution_denominator") == 31_237
        and original_receipt.get("completed_suite_count") == 13
        and original_receipt.get("all_original_suite_evidence_preserved")
        is True
        and original_receipt.get("historical_evidence_owner_count")
        == HISTORICAL_V21_EVIDENCE_OWNER_COUNT
        and original_receipt.get("historical_authenticated_reference_count")
        == HISTORICAL_V21_REFERENCE_COUNT
        and original_receipt.get("uncompressed_bytes") == 45_835
        and original_receipt.get("uncompressed_sha256")
        == "03765db905e57636efde4c31f066b95e80891a3ec5817937a6f6b58bf2868d57"
        and original_receipt.get("hidden_cases_read") == 0
        and original_receipt.get("clock_samples") == 0
        and original_receipt.get("timing_trials_run") == 0
        and original_receipt.get("holdout") == "NOT OPENED"
        and original_receipt.get("performance") == "NOT MEASURED"
        and original_receipt.get("memory") == "NOT MEASURED"
        and original_receipt.get("winner_selected") is False,
        "authenticate the complete original C aggregate failure receipt",
    )
    validate_c_evidence_metadata(
        original_receipt.get("archive"),
        protected_owners[original_archive_path],
        original_archive_path,
        durable=True,
    )
    original_plain = stream_complete_c_archive(
        protected[original_archive_path],
        original_receipt["uncompressed_bytes"],
        original_receipt["uncompressed_sha256"],
        "complete original C aggregate",
        retain=True,
    )
    require(type(original_plain) is bytes,
            "retain only the small original C aggregate report")
    original_report = strict_json(
        original_plain, "complete original C aggregate report",
    )
    original_rows = original_report.get("suite_results")
    require(
        original_report.get("schema")
        == "rebar-frozen-python-re-p0-candidate-v9-"
           "complete-original-candidate-evaluation"
        and original_report.get("status") == "FAIL"
        and original_report.get("candidate_family") == "c"
        and original_report.get("label") == COMPLETED_C_CAMPAIGN_LABEL
        and original_report.get("suite_count") == 13
        and original_report.get("case_execution_denominator") == 31_237
        and original_report.get("named_private_waiver_count") == 13
        and original_report.get("completed_suite_count") == 13
        and original_report.get("actual_candidate_workers") == 13
        and original_report.get("verified_passing_case_count") == 7_325
        and original_report.get("semantic_mismatch_count") == 1_262
        and original_report.get("infrastructure_failure_count") == 0
        and original_report.get("all_original_suite_evidence_preserved")
        is True
        and original_report.get("candidate_qualified") is False
        and original_report.get("historical_evidence_owner_count")
        == HISTORICAL_V21_EVIDENCE_OWNER_COUNT
        and original_report.get("historical_authenticated_reference_count")
        == HISTORICAL_V21_REFERENCE_COUNT
        and original_report.get("hidden_cases_read") == 0
        and original_report.get("benchmark_files_read") == 0
        and original_report.get("clock_samples") == 0
        and original_report.get("timing_trials_run") == 0
        and original_report.get("holdout") == "NOT OPENED"
        and original_report.get("performance") == "NOT MEASURED"
        and original_report.get("memory") == "NOT MEASURED"
        and original_report.get("winner_selected") is False
        and type(original_rows) is list and len(original_rows) == 13,
        "preserve all genuine C semantic losses and all original suite results",
    )

    require(
        outer_receipt.get("schema")
        == "rebar-owned-repaired-c-original-campaign-v3-"
           "durable-publication-receipt"
        and outer_receipt.get("status") == "PASS"
        and outer_receipt.get("candidate_status") == "FAIL"
        and outer_receipt.get("family") == "c"
        and outer_receipt.get("label") == COMPLETED_C_CAMPAIGN_LABEL
        and outer_receipt.get("suite_count") == 13
        and outer_receipt.get("case_execution_denominator") == 31_237
        and outer_receipt.get("historical_evidence_owner_count")
        == HISTORICAL_V22_EVIDENCE_OWNER_COUNT
        and outer_receipt.get("historical_authenticated_reference_count")
        == HISTORICAL_V22_REFERENCE_COUNT
        and outer_receipt.get("preserved_v21_evidence_owner_count")
        == HISTORICAL_V21_EVIDENCE_OWNER_COUNT
        and outer_receipt.get("preserved_v21_authenticated_reference_count")
        == HISTORICAL_V21_REFERENCE_COUNT
        and outer_receipt.get("uncompressed_bytes") == 49_645
        and outer_receipt.get("uncompressed_sha256")
        == "44caaaa21a4ba8ab9d4f94b7b9e9ef6577b1fdb072a180f54ff7443928b94d2f"
        and outer_receipt.get("original_native_restored") is True
        and outer_receipt.get("holdout") == "NOT OPENED"
        and outer_receipt.get("performance") == "NOT MEASURED"
        and outer_receipt.get("memory") == "NOT MEASURED"
        and outer_receipt.get("winner_selected") is False,
        "authenticate the real independent outer C failure receipt",
    )
    validate_c_evidence_metadata(
        outer_receipt.get("archive"),
        protected_owners[outer_archive_path],
        outer_archive_path,
        durable=True,
    )
    outer_plain = stream_complete_c_archive(
        protected[outer_archive_path],
        outer_receipt["uncompressed_bytes"],
        outer_receipt["uncompressed_sha256"],
        "recovered complete original C campaign",
        retain=True,
    )
    require(type(outer_plain) is bytes,
            "retain only the small recovered C campaign report")
    outer_report = strict_json(
        outer_plain, "recovered complete original C campaign report",
    )
    outer_rows = outer_report.get("original_suite_results")
    require(
        outer_report.get("schema")
        == "rebar-owned-repaired-c-original-campaign-v3-"
           "actual-recovered-campaign"
        and outer_report.get("status") == "FAIL"
        and outer_report.get("family") == "c"
        and outer_report.get("label") == COMPLETED_C_CAMPAIGN_LABEL
        and outer_report.get("suite_count") == 13
        and outer_report.get("case_execution_denominator") == 31_237
        and outer_report.get("named_private_waiver_count") == 13
        and outer_report.get("completed_suite_count") == 13
        and outer_report.get("verified_passing_case_count") == 7_325
        and outer_report.get("semantic_mismatch_count") == 1_262
        and outer_report.get("infrastructure_failure_count") == 0
        and outer_report.get("all_original_suite_evidence_preserved")
        is True
        and outer_report.get("candidate_qualified") is False
        and outer_report.get("historical_evidence_owner_count")
        == HISTORICAL_V22_EVIDENCE_OWNER_COUNT
        and outer_report.get("historical_authenticated_reference_count")
        == HISTORICAL_V22_REFERENCE_COUNT
        and outer_report.get("original_native_restored") is True
        and outer_report.get("hidden_cases_read") == 0
        and outer_report.get("benchmark_files_read") == 0
        and outer_report.get("clock_samples") == 0
        and outer_report.get("timing_trials_run") == 0
        and outer_report.get("holdout") == "NOT OPENED"
        and outer_report.get("performance") == "NOT MEASURED"
        and outer_report.get("memory") == "NOT MEASURED"
        and outer_report.get("winner_selected") is False
        and type(outer_rows) is list and len(outer_rows) == 13,
        "preserve the independently recovered complete failed C campaign",
    )

    for index, (expected, inner, recovered) in enumerate(
        zip(suite_results, original_rows, outer_rows, strict=True)
    ):
        suite = expected["suite"]
        require(
            type(inner) is dict and type(recovered) is dict
            and inner.get("suite") == suite
            and recovered.get("suite") == suite
            and inner.get("status") == expected["status"]
            and recovered.get("status") == expected["status"]
            and inner.get("case_execution_denominator")
            == expected["case_execution_denominator"]
            and recovered.get("case_execution_denominator")
            == expected["case_execution_denominator"]
            and inner.get("actual_worker_started") is True
            and recovered.get("actual_worker_started") is True
            and inner.get("genuine_original_suite") is True
            and recovered.get("genuine_original_suite") is True
            and inner.get("mismatch_count") == expected["mismatch_count"]
            and recovered.get("mismatch_count") == expected["mismatch_count"]
            and inner.get("failure_class")
            == ("PASS" if expected["status"] == "PASS"
                else "SEMANTIC MISMATCH")
            and recovered.get("failure_class") == inner["failure_class"],
            "bind both genuine aggregate results to original C suite: " + suite,
        )
        validate_c_evidence_metadata(
            inner.get("suite_archive"),
            expected["archive"], expected["archive"]["path"],
        )
        validate_c_evidence_metadata(
            recovered.get("archive"),
            expected["archive"], expected["archive"]["path"],
        )
        validate_c_evidence_metadata(
            inner.get("suite_receipt"),
            expected["receipt"], expected["receipt"]["path"],
        )
        validate_c_evidence_metadata(
            recovered.get("receipt"),
            expected["receipt"], expected["receipt"]["path"],
        )
        process = inner.get("process")
        recovered_process = recovered.get("process")
        require(
            type(process) is dict
            and type(recovered_process) is dict
            and canonical(process) == canonical(recovered_process)
            and process.get("returncode")
            == (0 if expected["status"] == "PASS" else 1)
            and process.get("timed_out") is False
            and process.get("stdout_overflow") is False
            and process.get("stderr_overflow") is False
            and process.get("stderr_bytes") == 0
            and process.get("stderr_sha256") == digest(b""),
            "preserve the exact real original C worker process: " + suite,
        )
        try:
            observed_stdout = base64.b64decode(
                process["stdout_base64"].encode("ascii"), validate=True,
            )
            observed_stderr = base64.b64decode(
                process["stderr_base64"].encode("ascii"), validate=True,
            )
        except (KeyError, ValueError, UnicodeError) as error:
            raise FreezeError(
                "reject altered original C worker process bytes: " + suite
            ) from error
        require(
            len(observed_stdout) == process.get("stdout_bytes")
            and digest(observed_stdout) == process.get("stdout_sha256")
            and observed_stderr == b"",
            "verify all genuine original C process output bytes: " + suite,
        )

    validate_c_evidence_metadata(
        outer_report.get("original_aggregate_archive"),
        protected_owners[original_archive_path],
        original_archive_path,
    )
    validate_c_evidence_metadata(
        outer_report.get("original_aggregate_receipt"),
        protected_owners[original_receipt_path],
        original_receipt_path,
    )
    native = protected_owners[ORIGINAL_C_NATIVE]
    recorded_native = outer_report.get("original_native_owner")
    restoration = original_report.get("restoration")
    receipt_restoration = original_receipt.get("restoration")
    recovered_restoration = outer_report.get("recovery")
    require(
        native["sha256"] == ORIGINAL_C_NATIVE_SHA256
        and native["bytes"] == 149_976
        and native["device"] == 2_064
        and native["inode"] == 430_300
        and native["mode"] == "0755"
        and native["link_count"] == 1
        and type(recorded_native) is dict
        and recorded_native.get("relative") == ORIGINAL_C_NATIVE
        and recorded_native.get("sha256") == native["sha256"]
        and recorded_native.get("bytes") == native["bytes"]
        and recorded_native.get("device") == native["device"]
        and recorded_native.get("inode") == native["inode"]
        and recorded_native.get("mode") == 0o755
        and recorded_native.get("nlink") == 1
        and type(restoration) is dict
        and type(receipt_restoration) is dict
        and canonical(restoration) == canonical(receipt_restoration)
        and restoration.get("schema")
        == "rebar-phase2-verified-native-activation-v5-actual-restoration"
        and restoration.get("status") == "PASS"
        and restoration.get("original_inode_preserved") is True
        and restoration.get("target") == ORIGINAL_C_NATIVE
        and restoration.get("original") == recorded_native
        and restoration.get("candidate_qualified") is False
        and restoration.get("holdout") == "NOT OPENED"
        and restoration.get("performance") == "NOT MEASURED"
        and restoration.get("memory") == "NOT MEASURED"
        and restoration.get("winner_selected") is False
        and type(recovered_restoration) is dict
        and recovered_restoration.get("route")
        == "existing-authenticated-restoration-receipt"
        and recovered_restoration.get("report")
        == {
            key: value for key, value in restoration.items()
            if key != "restoration_receipt"
        }
        and type(recovered_restoration.get("owner")) is dict
        and type(restoration.get("restoration_receipt")) is dict
        and recovered_restoration["owner"].get("sha256")
        == restoration["restoration_receipt"]["sha256"]
        and recovered_restoration["owner"].get("device")
        == restoration["restoration_receipt"]["device"]
        and recovered_restoration["owner"].get("inode")
        == restoration["restoration_receipt"]["inode"],
        "prove that the exact original C native inode is truly restored",
    )
    require(
        tuple(item["suite"] for item in suite_results) == SUITE_IDS
        and total_cases == 31_237
        and passing == 7_325
        and mismatches == 1_262
        and len(identities) == ADDITIONAL_COMPLETED_C_EVIDENCE_OWNER_COUNT
        and HISTORICAL_V22_EVIDENCE_OWNER_COUNT
        + ADDITIONAL_COMPLETED_C_EVIDENCE_OWNER_COUNT
        == CURRENT_EVIDENCE_OWNER_COUNT
        and len(history) == CURRENT_AUTHENTICATED_REFERENCE_COUNT
        and sum(path.startswith("oracle/phase2/evidence/")
                for path in history) == 110
        and sum(path.startswith("experiments/rust_public_practice_v1/")
                for path in history) == 30,
        "independently reconstruct all 135 real owners and 140 references",
    )
    current = {
        "label": COMPLETED_C_CAMPAIGN_LABEL,
        "status": "FAIL",
        "suite_count": 13,
        "case_execution_denominator": total_cases,
        "named_private_waiver_count": 13,
        "completed_suite_count": 13,
        "actual_candidate_worker_count": 13,
        "verified_passing_case_count": passing,
        "semantic_mismatch_count": mismatches,
        "infrastructure_failure_count": 0,
        "all_original_suite_evidence_preserved": True,
        "distinct_published_evidence_owner_count": len(identities),
        "suite_results": suite_results,
        "original_aggregate_archive":
            protected_owners[original_archive_path],
        "original_aggregate_receipt":
            protected_owners[original_receipt_path],
        "outer_failure_archive": protected_owners[outer_archive_path],
        "outer_failure_receipt": protected_owners[outer_receipt_path],
        "original_native": native,
        "original_native_restored": True,
        "candidate_qualified": False,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "winner_selected": False,
    }
    return previous, current

def authenticate_context(source_pin: str, protocol_pin: str,
                         contract_pin: str | None = None,
                         *, retain: bool = False) -> tuple[dict[str, Any], dict]:
    check_runtime()
    valid_digest(source_pin, "V11 source")
    valid_digest(protocol_pin, "V11 protocol")
    source_owner, source_raw = read_repository_owner(
        SOURCE_RELATIVE, source_pin,
        _checked_repository_size(SOURCE_RELATIVE),
    )
    protocol_owner, _protocol_raw = read_repository_owner(
        PROTOCOL_RELATIVE, protocol_pin,
        _checked_repository_size(PROTOCOL_RELATIVE),
    )

    protected: dict[str, bytes] = {}
    protected_owners: dict[str, dict[str, Any]] = {}
    for relative, (expected, size) in sorted(SUPPORT_OWNERS.items()):
        owner, raw = read_repository_owner(relative, expected, size)
        protected[relative] = raw
        protected_owners[relative] = owner

    originals: dict[str, bytes] = {}
    original_owners: dict[str, dict[str, Any]] = {}
    for relative, (expected, size) in sorted(SOURCE_OWNERS.items()):
        owner, raw = read_repository_owner(relative, expected, size)
        originals[relative] = raw
        original_owners[relative] = owner
    require(len({(item["device"], item["inode"])
                 for item in original_owners.values()}) == 3,
            "require three genuinely distinct independently owned Zig sources")

    tools: dict[str, dict[str, Any]] = {}
    for name, (path, expected, size, executable) in sorted(
            TOOLCHAIN_OWNERS.items()):
        owner, _raw = read_absolute_owner(path, expected, size, executable)
        tools[name] = owner

    validate_phase_one(strict_json(
        protected["oracle/phase1/p0-completeness-v1.json"],
        "original phase-one oracle",
    ))
    validate_zig_lock(strict_json(
        protected["toolchains/zig-0.16.0.lock.json"],
        "official stable Zig lock",
        canonical_required=False,
    ))
    validate_corrected_v3(strict_json(
        protected["oracle/phase2/six-family-p0-producer-v3.json"],
        "independently corrected V3 source producer",
    ))
    validate_v7(strict_json(
        protected["oracle/phase2/native-source-build-v7.json"],
        "original generic V7 source build",
    ))
    validate_v21(
        strict_json(protected[
            "docs/evidence/candidate-current-overview-v21.inputs.json"
        ], "published V21 inputs"),
        strict_json(protected[
            "docs/evidence/candidate-current-overview-v21.json"
        ], "published V21 summary"),
    )

    overlay = load_authenticated_module(
        "_rebar_owned_v11_zig_scanner_overlay", OVERLAY_SOURCE,
        protected[OVERLAY_SOURCE],
    )
    require(getattr(overlay, "SCHEMA", None) == OVERLAY_SCHEMA
            and getattr(overlay, "PRIVATE_ROOT_PREFIX", None)
            == PRIVATE_ROOT_PREFIX
            and getattr(overlay, "SOURCE_PATH", None) == OVERLAY_SOURCE
            and getattr(overlay, "PROTOCOL_PATH", None) == OVERLAY_PROTOCOL
            and getattr(overlay, "CONTRACT_PATH", None) == OVERLAY_CONTRACT
            and callable(getattr(overlay, "verify_context", None))
            and callable(getattr(overlay, "apply_private", None)),
            "load only the hash-authenticated exact first-party overlay interface")
    overlay_value, derived = overlay.verify_context(
        OVERLAY_SOURCE_SHA256, OVERLAY_PROTOCOL_SHA256,
        OVERLAY_CONTRACT_SHA256,
    )
    require(canonical(overlay_value) == protected[OVERLAY_CONTRACT],
            "bind the overlay context to its exact independently frozen contract")
    validate_overlay(overlay_value, derived)
    recovered_c, completed_c = validate_completed_c_campaign(
        protected, protected_owners, overlay,
    )

    contract_owner: dict[str, Any] | None = None
    if contract_pin is not None:
        valid_digest(contract_pin, "V11 contract")
        contract_owner, raw = read_repository_owner(
            CONTRACT_RELATIVE, contract_pin,
            _checked_repository_size(CONTRACT_RELATIVE),
        )
        document = strict_json(raw, "frozen V11 Zig scanner build contract")
        validate_contract(document, source_pin, protocol_pin)

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "PASS",
        "mode": "READ-ONLY FROZEN CONTEXT",
        "version": 11,
        "source": source_owner,
        "protocol": protocol_owner,
        "contract": contract_owner,
        "authenticated_support_owner_count": len(protected_owners),
        "authenticated_zig_source_owner_count": len(original_owners),
        "authenticated_toolchain_owner_count": len(tools),
        "frozen_case_execution_count": 31_237,
        "frozen_suite_count": 13,
        "frozen_private_waiver_count": 13,
        "frozen_independent_family_count": 6,
        "frozen_source_owner_count": 25,
        "historical_v21_evidence_owner_count":
            HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
        "historical_v21_authenticated_reference_count":
            HISTORICAL_V21_REFERENCE_COUNT,
        "authoritative_counted_evidence_owner_count":
            CURRENT_EVIDENCE_OWNER_COUNT,
        "authenticated_digest_addressed_history_paths":
            CURRENT_AUTHENTICATED_REFERENCE_COUNT,
        "historical_v22_evidence_owner_count":
            HISTORICAL_V22_EVIDENCE_OWNER_COUNT,
        "historical_v22_authenticated_reference_count":
            HISTORICAL_V22_REFERENCE_COUNT,
        "additional_recovered_c_failure_evidence_owner_count":
            ADDITIONAL_RECOVERED_C_EVIDENCE_OWNER_COUNT,
        "additional_completed_c_campaign_evidence_owner_count":
            ADDITIONAL_COMPLETED_C_EVIDENCE_OWNER_COUNT,
        "recovered_c_failure": recovered_c,
        "completed_c_original_campaign": completed_c,
        "historical_zig_semantic_mismatch_count": 1_764,
        "historical_zig_gate_status": "FAIL",
        "preserved_scanner_verbose_mismatch_count": 620,
        "private_root_prefix": "/tmp/" + PRIVATE_ROOT_PREFIX,
        "derived_source_sha256": DERIVED_BRIDGE_SHA256,
        "derived_source_bytes": DERIVED_BRIDGE_BYTES,
        "derived_source_materialized": False,
        "expected_build_process_count_only_after_success":
            EXPECTED_PROCESS_COUNT,
        "workspace_mutations": 0,
        **expected_phase_boundary(),
    }
    retained: dict[str, Any] = {}
    if retain:
        retained = {
            "overlay": overlay,
            "overlay_contract": overlay_value,
            "derived": derived,
            "protected": protected,
            "protected_owners": protected_owners,
            "originals": originals,
            "original_owners": original_owners,
            "toolchains": tools,
        }
    return result, retained


def _checked_repository_size(relative: str) -> int:
    parts = checked_relative(relative)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory = os.open(str(ROOT), flags | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            following = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = following
        descriptor = os.open(parts[-1], flags, dir_fd=directory)
        try:
            owner = os.fstat(descriptor)
            require(stat.S_ISREG(owner.st_mode)
                    and 0 < owner.st_size <= MAX_SOURCE_BYTES
                    and owner.st_nlink == 1,
                    "require a bounded, exact, nonlinked V11 freeze owner")
            return owner.st_size
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def dynamic_and_symbols(parsed: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    require(type(parsed) is dict
            and parsed.get("format") == "ELF64-LITTLE-ENDIAN-X86-64-ET-DYN",
            "audit only an authenticated complete first-party ELF64 artifact")
    dynamic = parsed.get("dynamic_tables")
    require(type(dynamic) is list and len(dynamic) == 1
            and type(dynamic[0]) is dict
            and type(dynamic[0].get("entries")) is list,
            "require one complete authenticated native dynamic table")
    symbol_record = parsed.get("symbol_tables")
    require(type(symbol_record) is dict
            and type(symbol_record.get("tables")) is list,
            "require complete authenticated first-party native symbol tables")
    tables = [item for item in symbol_record["tables"]
              if type(item) is dict and item.get("section_name") == ".dynsym"]
    require(len(tables) == 1 and type(tables[0].get("symbols")) is list,
            "require exactly one genuine, linked dynamic symbol table")
    return dynamic[0]["entries"], tables[0]["symbols"]


def audit_native_role(role: str, parsed: dict[str, Any]) -> dict[str, Any]:
    require(role in ("engine", "bridge"),
            "audit only an independently built owned Zig engine or bridge")
    entries, symbols = dynamic_and_symbols(parsed)
    require(all(type(item) is dict for item in entries)
            and all(type(item) is dict for item in symbols),
            "require real, individually authenticated native owners")
    needed = [item.get("name") for item in entries if item.get("tag") == 1]
    sonames = [item.get("name") for item in entries if item.get("tag") == 14]
    legacy_rpaths = [item.get("name") for item in entries if item.get("tag") == 15]
    runpaths = [item.get("name") for item in entries if item.get("tag") == 29]
    require(all(type(item) is str for item in needed + sonames
                + legacy_rpaths + runpaths)
            and len(set(needed)) == len(needed)
            and len(sonames) <= 1 and len(runpaths) <= 1
            and not legacy_rpaths,
            "reject ambiguous, repeated, redirected, or legacy native dependencies")
    defined: set[str] = set()
    undefined: set[str] = set()
    for item in symbols:
        name = item.get("name")
        index = item.get("section_index")
        require(type(name) is str and type(index) is int and index >= 0,
                "reject a malformed or unbound dynamic symbol")
        if not name:
            continue
        target = undefined if index == 0 else defined
        require(name not in target,
                "reject an aliased first-party dynamic symbol: " + name)
        target.add(name)
        lowered = name.lower()
        require(name not in FORBIDDEN_SYMBOLS
                and not any(lowered.startswith(prefix)
                            for prefix in FORBIDDEN_SYMBOL_PREFIXES),
                "reject stdlib regex, external engine, loader, or foreign candidate: "
                + name)
    require(not (defined & undefined),
            "reject one symbol simultaneously owned and imported")
    if role == "engine":
        require(needed == ["libc.so.6"]
                and sonames == [ENGINE_FILENAME]
                and not runpaths,
                "require one own-soname Zig engine with only libc dependency")
        require(REQUIRED_ENGINE_EXPORTS.issubset(defined),
                "preserve every first-party native Zig engine export")
        unicode = {item for item in undefined if item.startswith("_PyUnicode_")}
        require(unicode == ALLOWED_ENGINE_UNICODE_HELPERS,
                "permit only the original seven CPython Unicode data helpers")
        require(not any(item.startswith("rebar_") for item in undefined),
                "the owned Zig engine cannot delegate matching to another engine")
    else:
        require(needed == [ENGINE_FILENAME, "libc.so.6"]
                and not sonames
                and runpaths == ["$ORIGIN"],
                "bind the extension only to its own adjacent Zig engine and libc")
        require("PyInit__zig_bridge" in defined
                and REQUIRED_BRIDGE_ENGINE_IMPORTS.issubset(undefined),
                "preserve the real CPython bridge and its own native Zig calls")
        require({item for item in undefined if item.startswith("rebar_")}
                == REQUIRED_BRIDGE_ENGINE_IMPORTS,
                "reject an indirect or cross-family semantic engine dependency")
    return {
        "role": role,
        "needed": needed,
        "soname": sonames[0] if sonames else None,
        "runpath": runpaths[0] if runpaths else None,
        "legacy_rpath_count": len(legacy_rpaths),
        "defined_dynamic_symbol_count": len(defined),
        "undefined_dynamic_symbol_count": len(undefined),
        "defined_first_party_symbols": sorted(
            item for item in defined if item.startswith("rebar_zig_")
        ),
        "imported_first_party_symbols": sorted(
            item for item in undefined if item.startswith("rebar_zig_")
        ),
        "allowed_engine_unicode_helpers": sorted(
            item for item in undefined if item in ALLOWED_ENGINE_UNICODE_HELPERS
        ),
        "external_regex_engine_count": 0,
        "stdlib_regex_engine_count": 0,
        "cross_family_engine_count": 0,
        "network_symbol_count": 0,
        "native_loader_symbol_count": 0,
    }


def encode_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_PROCESS_BYTES,
            "preserve every bounded byte from an actual compiler process")
    return {
        "bytes": len(raw),
        "sha256": digest(raw),
        "base64": base64.b64encode(raw).decode("ascii"),
        "complete": True,
    }


def decode_stream(value: Any) -> bytes:
    require(type(value) is dict and value.get("complete") is True
            and type(value.get("bytes")) is int
            and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
            and type(value.get("base64")) is str,
            "require one complete bounded actual process stream")
    valid_digest(value.get("sha256"), "actual compiler stream")
    try:
        raw = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise FreezeError("reject a truncated or fabricated compiler stream") from error
    require(len(raw) == value["bytes"] and digest(raw) == value["sha256"],
            "bind compiler output to all of its actual original bytes")
    return raw


def validate_process_schedule(records: Any, workdir: str,
                              *, complete: bool = True) -> list[dict]:
    root = checked_workdir(workdir)
    require(type(records) is list,
            "require actual individually captured compiler processes")
    schedule = [(phase, name) for phase in PHASE_NAMES for name in PROCESS_ROLES]
    if complete:
        require(len(records) == len(schedule) == EXPECTED_PROCESS_COUNT,
                "count 26 processes only after both phases actually complete")
    else:
        require(len(records) <= len(schedule),
                "reject invented processes beyond the frozen actual schedule")
    identifiers: set[int] = set()
    for index, item in enumerate(records):
        require(type(item) is dict,
                "reject a missing or malformed actual process owner")
        phase, name = schedule[index]
        require(item.get("phase") == phase and item.get("name") == name,
                "reject missing, reordered, substituted, or cross-phase processes")
        checked_command(name, item.get("argv"), root, phase)
        require(item.get("working_directory")
                == str(phase_paths(root, phase)["base"])
                and item.get("environment") == build_environment(root, phase),
                "preserve the exact clean environment and private working root")
        pid = item.get("pid")
        require(type(pid) is int and pid > 0 and pid not in identifiers,
                "require one genuine, unique process identity per actual command")
        identifiers.add(pid)
        require(item.get("returncode") == 0
                and item.get("signal") is None,
                "reject a crashed, signalled, or failed actual compiler process")
        decode_stream(item.get("stdout"))
        decode_stream(item.get("stderr"))
    return records


def check_directory_descriptor(descriptor: int, label: str) -> dict[str, Any]:
    owner = os.fstat(descriptor)
    require(stat.S_ISDIR(owner.st_mode)
            and owner.st_uid == os.geteuid()
            and stat.S_IMODE(owner.st_mode) == 0o700,
            "require a fresh owned, non-symlinked mode-0700 directory: " + label)
    return {
        "path": label,
        "device": owner.st_dev,
        "inode": owner.st_ino,
        "mode": "0700",
    }


def private_directory(workdir: str, phase: str,
                      components: tuple[str, ...]) -> tuple[int, dict[str, Any]]:
    root = checked_workdir(workdir)
    require(phase in PHASE_NAMES,
            "open only an independently owned reference phase")
    require(type(components) is tuple
            and all(type(item) is str and item not in ("", ".", "..")
                    and "/" not in item and "\\" not in item
                    and "\x00" not in item for item in components),
            "reject escaped, substituted, or broad private phase components")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    tmp = os.open("/tmp", flags)
    current: int | None = None
    try:
        current = os.open(PurePosixPath(root).parts[2], flags, dir_fd=tmp)
        check_directory_descriptor(current, root)
        for part in (phase, *components):
            following = os.open(part, flags, dir_fd=current)
            check_directory_descriptor(following, part)
            os.close(current)
            current = following
        require(current is not None, "require an authenticated private directory")
        result = check_directory_descriptor(
            current, str(Path(root) / phase / Path(*components)),
        )
        descriptor = current
        current = None
        return descriptor, result
    finally:
        if current is not None:
            os.close(current)
        os.close(tmp)


def checked_private_child(path: Any, workdir: str,
                          phase: str | None = None) -> Path:
    root = Path(checked_workdir(workdir))
    require(isinstance(path, Path) and path.is_absolute()
            and path != root and path.is_relative_to(root)
            and all(part not in (".", "..")
                    and "\\" not in part and "\x00" not in part
                    for part in path.parts),
            "create only an exact descendant of the fresh private build root")
    if phase is not None:
        require(phase in PHASE_NAMES
                and path.is_relative_to(root / phase),
                "reject a reused or cross-phase private source directory")
    return path


def create_private_directory(path: Path, workdir: str,
                             phase: str | None = None) -> dict[str, Any]:
    path = checked_private_child(path, workdir, phase)
    os.mkdir(str(path), 0o700)
    descriptor = os.open(str(path),
                         os.O_RDONLY | os.O_CLOEXEC
                         | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        return check_directory_descriptor(descriptor, str(path))
    finally:
        os.close(descriptor)


def prepare_private_phases(workdir: str) -> list[dict[str, Any]]:
    root = checked_workdir(workdir)
    prepared: list[dict[str, Any]] = []
    for phase in PHASE_NAMES:
        paths = phase_paths(root, phase)
        directories: dict[str, dict[str, Any]] = {}
        for key in ("base", "source", "source_candidates", "source_zig",
                    "native", "temporary", "zig_local_cache",
                    "zig_global_cache"):
            directories[key] = create_private_directory(
                paths[key], root, phase,
            )
        prepared.append({"name": phase, "directories": directories})
    identities = [item["directories"]["base"] for item in prepared]
    require(len({(item["device"], item["inode"]) for item in identities}) == 2,
            "the two source-build phases must be genuinely independent owners")
    return prepared


def assert_bridge_absent(workdir: str, phase: str) -> None:
    directory, _owner = private_directory(
        workdir, phase, ("source", "candidates", "zig"),
    )
    try:
        try:
            os.stat("py_bridge.c", dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            return
        raise FreezeError(
            "never copy, replace, or pre-create the frozen private Zig bridge"
        )
    finally:
        os.close(directory)


def write_private_source(workdir: str, phase: str, relative: str,
                         raw: bytes, expected: str) -> dict[str, Any]:
    require(relative in (ORIGINAL_ENGINE, ORIGINAL_ADAPTER)
            and type(raw) is bytes and digest(raw) == expected
            and SOURCE_OWNERS[relative] == (expected, len(raw)),
            "snapshot only an exact immutable original Zig engine or adapter")
    components = tuple(checked_relative(relative))
    directory, _owner = private_directory(
        workdir, phase, ("source", *components[:-1]),
    )
    descriptor: int | None = None
    try:
        descriptor = os.open(
            components[-1],
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory,
        )
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid()
                and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600,
                "require one freshly created private phase-source owner")
        offset = 0
        while offset < len(raw):
            count = os.write(descriptor, raw[offset:])
            require(type(count) is int and count > 0,
                    "complete every byte of the fresh private source snapshot")
            offset += count
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
                and after.st_size == len(raw),
                "reject a swapped or incomplete private source snapshot")
        os.close(descriptor)
        descriptor = None
        verify = os.open(components[-1],
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                         dir_fd=directory)
        try:
            result, repeated = read_descriptor(
                verify, expected, len(raw), MAX_SOURCE_BYTES,
                str(phase_paths(workdir, phase)["source"] / relative),
                private=True,
            )
        finally:
            os.close(verify)
        require(repeated == raw and result["device"] == after.st_dev
                and result["inode"] == after.st_ino,
                "authenticate the exact same newly owned phase-source inode")
        os.fsync(directory)
        return result
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def authenticate_private_bridge(workdir: str, phase: str) -> dict[str, Any]:
    directory, _owner = private_directory(
        workdir, phase, ("source", "candidates", "zig"),
    )
    try:
        descriptor = os.open("py_bridge.c",
                             os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                             dir_fd=directory)
        try:
            owner, _raw = read_descriptor(
                descriptor, DERIVED_BRIDGE_SHA256, DERIVED_BRIDGE_BYTES,
                MAX_SOURCE_BYTES,
                str(phase_paths(workdir, phase)["source_bridge"]),
                private=True,
            )
            return owner
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def capture_native_artifact(workdir: str, phase: str,
                            role: str) -> tuple[dict[str, Any], bytes]:
    require(role in ("engine", "bridge"),
            "capture only an exact independently compiled Zig native role")
    directory, _owner = private_directory(workdir, phase, ("native",))
    filename = ENGINE_FILENAME if role == "engine" else BRIDGE_FILENAME
    try:
        descriptor = os.open(filename,
                             os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                             dir_fd=directory)
        try:
            before = os.fstat(descriptor)
            require(stat.S_ISREG(before.st_mode)
                    and before.st_uid == os.geteuid()
                    and before.st_nlink == 1
                    and 0 < before.st_size <= MAX_BINARY_BYTES,
                    "require one genuine freshly linked private ELF owner")
            chunks: list[bytes] = []
            total = 0
            while True:
                piece = os.read(descriptor,
                                min(1024 * 1024,
                                    MAX_BINARY_BYTES + 1 - total))
                if not piece:
                    break
                total += len(piece)
                require(total <= MAX_BINARY_BYTES,
                        "bound the complete independently built native artifact")
                chunks.append(piece)
            after = os.fstat(descriptor)
            require((before.st_dev, before.st_ino, before.st_size,
                     before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                    == (after.st_dev, after.st_ino, after.st_size,
                        after.st_nlink, after.st_mtime_ns, after.st_ctime_ns),
                    "reject a replaced or altered private native artifact")
            raw = b"".join(chunks)
            require(len(raw) == before.st_size,
                    "capture every byte of the genuine native artifact")
            return source_owner_metadata(
                str(phase_paths(workdir, phase)["artifact_" + role]),
                after,
                digest(raw),
            ), raw
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def run_process(name: str, workdir: str, phase: str,
                records: list[dict[str, Any]]) -> dict[str, Any]:
    commands = planned_commands(workdir, phase)
    argv = checked_command(name, commands[name], workdir, phase)
    cwd = str(phase_paths(workdir, phase)["base"])
    environment = build_environment(workdir, phase)
    process = subprocess.Popen(
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env=environment,
        shell=False,
        close_fds=True,
    )
    stdout, stderr = process.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes,
            "capture complete original process output without a shell")
    record = {
        "phase": phase,
        "name": name,
        "argv": argv,
        "working_directory": cwd,
        "environment": environment,
        "pid": process.pid,
        "returncode": process.returncode,
        "signal": -process.returncode if process.returncode < 0 else None,
        "stdout": encode_stream(stdout),
        "stderr": encode_stream(stderr),
    }
    records.append(record)
    require(process.returncode == 0,
            "preserve a genuine failed native process: " + phase + "/" + name)
    if name == "zig_version":
        require(stdout == b"0.16.0\n",
                "reject an unofficial or substituted stable Zig compiler")
    if name in ("readelf_version", "gcc_version"):
        require(bool(stdout), "capture the genuine pinned native tool version")
    if name.endswith(("_dynamic", "_symbols", "_sections")):
        require(bool(stdout),
                "retain the complete real native ELF forensic output")
    return record


def evidence_names(label: str, failed: bool) -> tuple[str, str]:
    selected = checked_label(label)
    suffix = "-failures" if failed else ""
    base = "native-source-build-v11-zig-" + selected + suffix
    return base + ".json.gz", base + "-publication-receipt.json"


def evidence_directory() -> int:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    current = os.open(str(ROOT), flags)
    try:
        for part in checked_relative(EVIDENCE_RELATIVE):
            following = os.open(part, flags, dir_fd=current)
            check_directory_descriptor(following, part)
            os.close(current)
            current = following
        result = current
        current = -1
        return result
    finally:
        if current >= 0:
            os.close(current)


def require_fresh_evidence(label: str) -> None:
    selected = checked_label(label)
    directory = evidence_directory()
    try:
        for failed in (False, True):
            for name in evidence_names(selected, failed):
                try:
                    descriptor = os.open(
                        name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                        dir_fd=directory,
                    )
                except OSError as error:
                    if error.errno == errno.ENOENT:
                        continue
                    raise
                os.close(descriptor)
                raise FreezeError(
                    "never overwrite or reuse a published Zig evidence owner: "
                    + name
                )
    finally:
        os.close(directory)


def exclusive_publication(directory: int, name: str,
                          raw: bytes) -> dict[str, Any]:
    require(type(name) is str and "/" not in name and "\\" not in name
            and name not in ("", ".", "..")
            and type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES,
            "publish only one exact bounded, exclusive Zig evidence owner")
    descriptor: int | None = None
    try:
        descriptor = os.open(
            name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory,
        )
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid()
                and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600,
                "require a newly owned nonlinked mode-0600 evidence owner")
        offset = 0
        while offset < len(raw):
            count = os.write(descriptor, raw[offset:])
            require(type(count) is int and count > 0,
                    "publish every original evidence byte")
            offset += count
        os.fsync(descriptor)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_uid, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink)
                and after.st_size == len(raw),
                "reject swapped or incompletely synchronized native evidence")
        os.close(descriptor)
        descriptor = None
        verify = os.open(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                         dir_fd=directory)
        try:
            owner, repeated = read_descriptor(
                verify, digest(raw), len(raw), MAX_ARCHIVE_BYTES,
                EVIDENCE_RELATIVE + "/" + name,
                private=True,
            )
        finally:
            os.close(verify)
        require(repeated == raw and owner["device"] == after.st_dev
                and owner["inode"] == after.st_ino,
                "prove a complete same-inode fresh evidence readback")
        os.fsync(directory)
        owner["file_fsync"] = True
        owner["directory_fsync"] = True
        return owner
    finally:
        if descriptor is not None:
            os.close(descriptor)


def publish_report(report: dict[str, Any], label: str) -> dict[str, Any]:
    failed = report.get("status") != "PASS"
    archive_name, receipt_name = evidence_names(label, failed)
    plain = canonical(report)
    require(len(plain) <= MAX_REPORT_BYTES,
            "bound the complete actual native build and forensic report")
    archive = gzip.compress(plain, compresslevel=9, mtime=0)
    require(0 < len(archive) <= MAX_ARCHIVE_BYTES,
            "bound the deterministic actual source-build evidence archive")
    directory = evidence_directory()
    try:
        archive_owner = exclusive_publication(directory, archive_name, archive)
        receipt = {
            "schema": RECEIPT_SCHEMA,
            "version": 11,
            "status": "PASS",
            "build_status": report["status"],
            "family": "zig",
            "label": checked_label(label),
            "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "contract_sha256": report["contract_sha256"],
            "archive": archive_owner,
            "uncompressed_sha256": digest(plain),
            "uncompressed_bytes": len(plain),
            "historical_v21_evidence_owner_count":
                HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
            "historical_v21_authenticated_reference_count":
                HISTORICAL_V21_REFERENCE_COUNT,
            "current_evidence_owner_count_before_publication":
                CURRENT_EVIDENCE_OWNER_COUNT,
            "current_authenticated_reference_count_before_publication":
                CURRENT_AUTHENTICATED_REFERENCE_COUNT,
            "new_evidence_owner_count_after_receipt_publication": 2,
            "expected_build_process_count_only_after_success":
                EXPECTED_PROCESS_COUNT,
            "actual_build_process_count": report["actual_build_process_count"],
            "actual_source_apply_count": report["actual_source_apply_count"],
            "candidate_imports": 0,
            "candidate_processes_started": 0,
            "native_libraries_loaded": 0,
            "network_requests": 0,
            "hidden_cases_read": 0,
            "final_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "candidate_correctness": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
            "failure_preserved": failed,
            "receipt_self_publication": "NOT CLAIMED",
        }
        raw_receipt = canonical(receipt)
        require(len(raw_receipt) <= MAX_SOURCE_BYTES,
                "bound the complete independent durable build receipt")
        receipt_owner = exclusive_publication(
            directory, receipt_name, raw_receipt,
        )
        return {
            "schema": SCHEMA + "-publication-result",
            "status": report["status"],
            "family": "zig",
            "label": checked_label(label),
            "archive": archive_owner,
            "receipt": receipt_owner,
            "failure_preserved": failed,
            "expected_build_process_count_only_after_success":
                EXPECTED_PROCESS_COUNT,
            "actual_build_process_count": report["actual_build_process_count"],
            "actual_source_apply_count": report["actual_source_apply_count"],
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
        }
    finally:
        os.close(directory)


def authenticate_v7_parser(raw: bytes) -> types.ModuleType:
    module = load_authenticated_module(
        "_rebar_owned_v11_zig_v7_elf",
        "tools/reproduce_owned_native_source_build_v7.py",
        raw,
    )
    require(getattr(module, "SCHEMA", None)
            == "rebar-phase2-owned-native-source-build-v7"
            and getattr(module, "SOURCE_RELATIVE", None)
            == "tools/reproduce_owned_native_source_build_v7.py"
            and callable(getattr(module, "parse_owned_elf64", None))
            and callable(getattr(module, "compare_owned_elf64", None))
            and getattr(module, "MAX_BINARY_BYTES", None) == MAX_BINARY_BYTES,
            "use only the exact frozen first-party V7 complete-byte ELF parser")
    return module


def run_build(source_pin: str, protocol_pin: str, contract_pin: str,
              label: str) -> tuple[int, dict[str, Any]]:
    selected_label = checked_label(label)
    context, retained = authenticate_context(
        source_pin, protocol_pin, contract_pin, retain=True,
    )
    require(context["status"] == "PASS",
            "authenticate the complete independent V11 source freeze first")
    require_fresh_evidence(selected_label)
    overlay = retained["overlay"]
    derived = retained["derived"]
    v7 = authenticate_v7_parser(
        retained["protected"]["tools/reproduce_owned_native_source_build_v7.py"],
    )
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": 11,
        "status": "FAIL",
        "family": "zig",
        "label": selected_label,
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "frozen_correctness": {
            "python": "3.14.6",
            "suite_count": 13,
            "case_execution_count": 31_237,
            "private_waiver_count": 13,
        },
        "historical_v21_evidence_owner_count":
            HISTORICAL_V21_EVIDENCE_OWNER_COUNT,
        "historical_v21_authenticated_reference_count":
            HISTORICAL_V21_REFERENCE_COUNT,
        "current_evidence_owner_count": CURRENT_EVIDENCE_OWNER_COUNT,
        "current_authenticated_reference_count":
            CURRENT_AUTHENTICATED_REFERENCE_COUNT,
        "historical_zig_semantic_mismatch_count": 1_764,
        "expected_build_process_count_only_after_success":
            EXPECTED_PROCESS_COUNT,
        "actual_build_process_count": 0,
        "actual_source_apply_count": 0,
        "processes": [],
        "build_phases": [],
        "reproducibility": "NOT MEASURED",
        "raw_elf_differences": "NOT MEASURED",
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "reference_processes_started": 0,
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
        "owned_original_sources_before": retained["original_owners"],
        "owned_original_sources_after": "NOT MEASURED",
    }
    actual_raw: dict[tuple[str, str], bytes] = {}
    try:
        root = tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX, dir="/tmp")
        checked_workdir(root)
        descriptor = os.open(root,
                             os.O_RDONLY | os.O_CLOEXEC
                             | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            report["private_root"] = check_directory_descriptor(descriptor, root)
        finally:
            os.close(descriptor)

        phases = prepare_private_phases(root)
        report["build_phases"] = phases
        for item in phases:
            phase = item["name"]
            item["source_snapshots"] = {
                relative: write_private_source(
                    root, phase, relative,
                    retained["originals"][relative],
                    SOURCE_OWNERS[relative][0],
                )
                for relative in (ORIGINAL_ADAPTER, ORIGINAL_ENGINE)
            }
            assert_bridge_absent(root, phase)

        for item in phases:
            phase = item["name"]
            applied = overlay.apply_private(
                str(phase_paths(root, phase)["source"]), derived,
            )
            report["actual_source_apply_count"] += 1
            require(type(applied) is dict
                    and applied.get("schema") == OVERLAY_SCHEMA
                    and applied.get("status") == "PASS"
                    and applied.get("phase") == phase
                    and applied.get("source_apply_count") == 1
                    and applied.get("candidate_original_modified") is False
                    and applied.get("derived_sha256") == DERIVED_BRIDGE_SHA256
                    and applied.get("derived_bytes") == DERIVED_BRIDGE_BYTES
                    and applied.get("snapshot_root")
                    == str(phase_paths(root, phase)["source"]),
                    "reject an altered, repeated, failed, or cross-phase overlay")
            item["overlay_application"] = applied
            item["source_snapshots"][ORIGINAL_BRIDGE] = (
                authenticate_private_bridge(root, phase)
            )

        require(report["actual_source_apply_count"] == 2,
                "apply the committed source overlay exactly once to each phase")
        for relative in SOURCE_OWNERS:
            identities = [item["source_snapshots"][relative]
                          for item in phases]
            require(len({(item["device"], item["inode"])
                         for item in identities}) == 2,
                    "reject source snapshots shared between independent phases")

        for item in phases:
            phase = item["name"]
            for name in PROCESS_ROLES[:5]:
                try:
                    run_process(name, root, phase, report["processes"])
                finally:
                    report["actual_build_process_count"] = len(
                        report["processes"]
                    )
            outputs: dict[str, Any] = {}
            for role in ("engine", "bridge"):
                owner, raw = capture_native_artifact(root, phase, role)
                parsed = v7.parse_owned_elf64(raw)
                require(type(parsed) is dict
                        and parsed.get("file_sha256") == owner["sha256"]
                        and parsed.get("file_size") == owner["bytes"],
                        "bind V7 ELF forensics to actual full same-inode bytes")
                outputs[role] = {
                    "owner": owner,
                    "raw_elf64": parsed,
                    "independence_audit": audit_native_role(role, parsed),
                }
                key = (phase, role)
                require(key not in actual_raw,
                        "never alias, replace, or reuse a phase native output")
                actual_raw[key] = raw
            item["native_outputs"] = outputs
            for name in PROCESS_ROLES[5:]:
                try:
                    run_process(name, root, phase, report["processes"])
                finally:
                    report["actual_build_process_count"] = len(
                        report["processes"]
                    )
            for role in ("engine", "bridge"):
                owner, repeated = capture_native_artifact(root, phase, role)
                original = outputs[role]["owner"]
                require(repeated == actual_raw[(phase, role)]
                        and (owner["device"], owner["inode"], owner["sha256"])
                        == (original["device"], original["inode"],
                            original["sha256"]),
                        "preserve the identical native inode after all ELF inspections")

        validate_process_schedule(report["processes"], root, complete=True)
        require(report["actual_build_process_count"] == EXPECTED_PROCESS_COUNT,
                "claim twenty-six processes only after all twenty-six exist")
        differences: dict[str, Any] = {}
        for role in ("engine", "bridge"):
            first = phases[0]["native_outputs"][role]
            second = phases[1]["native_outputs"][role]
            require((first["owner"]["device"], first["owner"]["inode"])
                    != (second["owner"]["device"],
                        second["owner"]["inode"]),
                    "require independently owned native artifact phase inodes")
            difference = v7.compare_owned_elf64(
                actual_raw[(PHASE_NAMES[0], role)],
                actual_raw[(PHASE_NAMES[1], role)],
                first["raw_elf64"], second["raw_elf64"],
            )
            differences[role] = difference
        report["raw_elf_differences"] = {
            "schema": SCHEMA + "-all-phase-raw-elf-differences",
            "independent_phase_count": 2,
            "native_role_count": 2,
            "roles": differences,
            "all_native_artifacts_byte_identical": all(
                value.get("byte_identical") is True
                for value in differences.values()
            ),
            "additional_compiler_or_inspector_processes": 0,
            "comparison_completed_before_reproducibility_classification": True,
        }
        require(report["raw_elf_differences"][
            "all_native_artifacts_byte_identical"
        ], "preserve a genuine two-phase native reproducibility failure")
        report["reproducibility"] = {
            "status": "PASS",
            "independent_phase_count": 2,
            "byte_identical_native_role_count": 2,
            "compiler_process_count": len(report["processes"]),
            "source_apply_count": report["actual_source_apply_count"],
            "roles": {
                role: {
                    "sha256": phases[0]["native_outputs"][role]["owner"][
                        "sha256"
                    ],
                    "bytes": phases[0]["native_outputs"][role]["owner"][
                        "bytes"
                    ],
                    "phase_owner_count": 2,
                    "byte_identical": True,
                }
                for role in ("engine", "bridge")
            },
        }
        after: dict[str, dict[str, Any]] = {}
        for relative, (expected, size) in sorted(SOURCE_OWNERS.items()):
            owner, raw = read_repository_owner(relative, expected, size)
            before = retained["original_owners"][relative]
            require((owner["device"], owner["inode"], owner["sha256"])
                    == (before["device"], before["inode"], before["sha256"])
                    and raw == retained["originals"][relative],
                    "never change any original independently owned Zig source")
            after[relative] = owner
        report["owned_original_sources_after"] = after
        renewed, _discard = authenticate_context(
            source_pin, protocol_pin, contract_pin,
        )
        require(renewed["status"] == "PASS"
                and renewed["source"]["sha256"] == source_pin
                and renewed["protocol"]["sha256"] == protocol_pin
                and type(renewed["contract"]) is dict
                and renewed["contract"]["sha256"] == contract_pin,
                "the complete independently frozen context changed during the build")
        report["status"] = "PASS"
    except Exception as error:
        report["actual_build_process_count"] = len(report["processes"])
        report["status"] = "FAIL"
        report["error"] = {
            "type": type(error).__name__,
            "message": str(error),
        }
    publication = publish_report(report, selected_label)
    return (0 if report["status"] == "PASS" else 1), publication


class SyntheticBoundary:
    """Reject filesystem, compiler, candidate, native, network, and clock effects."""

    def __init__(self) -> None:
        self.saved: list[tuple[object, str, Any]] = []
        self.blocked: dict[str, int] = {
            "filesystem": 0,
            "process": 0,
            "temporary": 0,
            "network": 0,
            "native": 0,
            "candidate_import": 0,
            "thread": 0,
            "clock": 0,
        }

    def install(self, owner: object, name: str, kind: str) -> None:
        original = getattr(owner, name, None)
        if original is None:
            return

        def reject(*_arguments: Any, **_keywords: Any) -> Any:
            self.blocked[kind] += 1
            raise SourceOnlyError(
                "synthetic source-only boundary blocked " + kind + ": " + name
            )

        self.saved.append((owner, name, original))
        setattr(owner, name, reject)

    def __enter__(self) -> SyntheticBoundary:
        groups: tuple[tuple[object, tuple[str, ...], str], ...] = (
            (builtins, ("open",), "filesystem"),
            (io, ("open",), "filesystem"),
            (os, ("open", "read", "write", "fstat", "stat", "lstat",
                  "mkdir", "makedirs", "listdir", "scandir", "unlink",
                  "remove", "rename", "replace", "link", "symlink",
                  "chmod", "fchmod", "fsync", "chdir"), "filesystem"),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "stat", "lstat", "exists", "is_file",
                    "is_dir", "mkdir", "unlink", "rename", "replace",
                    "resolve", "iterdir"), "filesystem"),
            (subprocess, ("Popen", "run", "call", "check_call",
                          "check_output"), "process"),
            (os, ("system", "popen", "fork", "posix_spawn"), "process"),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile",
                        "TemporaryDirectory"), "temporary"),
            (socket, ("socket", "create_connection", "getaddrinfo"),
             "network"),
            (ctypes, ("CDLL", "PyDLL", "WinDLL", "OleDLL"), "native"),
            (importlib, ("import_module",), "candidate_import"),
            (threading.Thread, ("start",), "thread"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "process_time_ns", "thread_time", "thread_time_ns",
                    "clock_gettime", "clock_gettime_ns", "sleep"), "clock"),
        )
        for owner, names, kind in groups:
            for name in names:
                self.install(owner, name, kind)
        return self

    def __exit__(self, _kind: Any, _value: Any, _traceback: Any) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def synthetic_native(role: str) -> dict[str, Any]:
    require(role in ("engine", "bridge"),
            "construct only in-memory synthetic native audit controls")
    if role == "engine":
        entries = [
            {"tag": 1, "name": "libc.so.6"},
            {"tag": 14, "name": ENGINE_FILENAME},
        ]
        symbols = [
            {"name": name, "section_index": 1}
            for name in sorted(REQUIRED_ENGINE_EXPORTS)
        ] + [
            {"name": name, "section_index": 0}
            for name in sorted(ALLOWED_ENGINE_UNICODE_HELPERS)
        ]
    else:
        entries = [
            {"tag": 1, "name": ENGINE_FILENAME},
            {"tag": 1, "name": "libc.so.6"},
            {"tag": 29, "name": "$ORIGIN"},
        ]
        symbols = [
            {"name": "PyInit__zig_bridge", "section_index": 1},
            *({"name": name, "section_index": 0}
              for name in sorted(REQUIRED_BRIDGE_ENGINE_IMPORTS)),
        ]
    return {
        "format": "ELF64-LITTLE-ENDIAN-X86-64-ET-DYN",
        "dynamic_tables": [{"entries": entries}],
        "symbol_tables": {"tables": [
            {"section_name": ".dynsym", "symbols": symbols},
        ]},
    }


def synthetic_records(workdir: str) -> list[dict[str, Any]]:
    root = checked_workdir(workdir)
    empty = encode_stream(b"")
    records: list[dict[str, Any]] = []
    for phase in PHASE_NAMES:
        for name, argv in planned_commands(root, phase).items():
            records.append({
                "phase": phase,
                "name": name,
                "argv": list(argv),
                "working_directory": str(phase_paths(root, phase)["base"]),
                "environment": build_environment(root, phase),
                "pid": 1_000_000 + len(records),
                "returncode": 0,
                "signal": None,
                "stdout": dict(empty),
                "stderr": dict(empty),
            })
    return records


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, Any]:
    check_runtime()
    valid_digest(source_pin, "V11 source")
    valid_digest(protocol_pin, "V11 protocol")
    valid_digest(contract_pin, "V11 contract")
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, value: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected
                and bool(value),
                "a unique positive source-only control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Any) -> None:
        require(type(name) is str and name not in accepted and name not in rejected
                and callable(action),
                "require one unique genuine hostile source-only control")
        try:
            action()
        except (FreezeError, SourceOnlyError, OSError, ValueError, TypeError,
                UnicodeError, OverflowError, RecursionError, KeyError):
            rejected.append(name)
            return
        raise FreezeError("a hostile source-only control was accepted: " + name)

    with SyntheticBoundary() as boundary:
        root = "/tmp/" + PRIVATE_ROOT_PREFIX + "synthetic-v11"
        accept("exact-lowercase-digest", valid_digest("a" * 64, "synthetic"))
        accept("exact-lowercase-label", checked_label("phase2-v11-zig"))
        accept("exact-sealed-overlay-root", checked_workdir(root) == root)
        accept("both-sibling-phase-names", PHASE_NAMES
               == ("reference-a", "reference-b"))
        accept("distinct-phase-source-paths",
               phase_paths(root, "reference-a")["source"]
               != phase_paths(root, "reference-b")["source"])
        accept("accept-real-concrete-posix-phase-path",
               checked_private_child(
                   phase_paths(root, "reference-a")["base"],
                   root, "reference-a",
               ) == phase_paths(root, "reference-a")["base"])
        accept("accept-real-concrete-posix-source-path",
               checked_private_child(
                   phase_paths(root, "reference-a")["source_zig"],
                   root, "reference-a",
               ) == phase_paths(root, "reference-a")["source_zig"])
        accept("distinct-phase-local-cache-paths",
               phase_paths(root, "reference-a")["zig_local_cache"]
               != phase_paths(root, "reference-b")["zig_local_cache"])
        accept("distinct-phase-global-cache-paths",
               phase_paths(root, "reference-a")["zig_global_cache"]
               != phase_paths(root, "reference-b")["zig_global_cache"])
        accept("both-exact-reproducible-source-prefix-flags",
               len(prefix_flags(root)) == 2
               and all(flag.endswith("=" + CANONICAL_SOURCE_PREFIX)
                       for flag in prefix_flags(root)))
        accept("thirteen-exact-first-phase-roles",
               tuple(planned_commands(root, "reference-a")) == PROCESS_ROLES)
        accept("thirteen-exact-second-phase-roles",
               tuple(planned_commands(root, "reference-b")) == PROCESS_ROLES)
        accept("pinned-releasefast-zig-engine",
               "ReleaseFast" in planned_commands(
                   root, "reference-a",
               )["build_zig_engine"])
        accept("exact-explicit-both-zig-caches",
               "--cache-dir" in planned_commands(
                   root, "reference-a",
               )["build_zig_engine"]
               and "--global-cache-dir" in planned_commands(
                   root, "reference-a",
               )["build_zig_engine"])
        accept("exact-own-zig-engine-soname",
               "-fsoname=" + ENGINE_FILENAME in planned_commands(
                   root, "reference-a",
               )["build_zig_engine"])
        accept("exact-pinned-gcc-bridge",
               planned_commands(root, "reference-a")["build_zig_bridge"][0]
               == PINNED_GCC)
        accept("exact-own-adjacent-engine-link",
               "-l:" + ENGINE_FILENAME in planned_commands(
                   root, "reference-a",
               )["build_zig_bridge"])
        accept("exact-own-origin-runpath",
               "-Wl,-rpath,$ORIGIN" in planned_commands(
                   root, "reference-a",
               )["build_zig_bridge"])
        accept("eight-exact-first-party-elf-inspections",
               sum(name.endswith(("_dynamic", "_symbols", "_sections", "_notes"))
                   for name in planned_commands(root, "reference-a")) == 8)
        accept("no-home-variable-in-clean-build-environment",
               "HOME" not in build_environment(root, "reference-a")
               and "home" not in build_environment(root, "reference-a"))
        accept("exact-private-environment",
               len(build_environment(root, "reference-a")) == 8
               and build_environment(root, "reference-a")["PATH"]
               == "/usr/bin:/bin")
        accept("authenticated-synthetic-engine-symbols",
               audit_native_role("engine", synthetic_native("engine"))["soname"]
               == ENGINE_FILENAME)
        accept("allowed-cpython-unicode-is-not-regex-delegation",
               set(audit_native_role(
                   "engine", synthetic_native("engine"),
               )["allowed_engine_unicode_helpers"])
               == ALLOWED_ENGINE_UNICODE_HELPERS)
        accept("authenticated-synthetic-bridge-symbols",
               audit_native_role("bridge", synthetic_native("bridge"))["runpath"]
               == "$ORIGIN")
        records = synthetic_records(root)
        accept("twenty-six-in-memory-only-synthetic-process-records",
               len(validate_process_schedule(records, root))
               == EXPECTED_PROCESS_COUNT)
        accept("canonical-complete-empty-process-stream",
               decode_stream(encode_stream(b"")) == b"")
        accept("canonical-complete-byte-process-stream",
               decode_stream(encode_stream(b"synthetic\x00\xff"))
               == b"synthetic\x00\xff")
        contract = contract_document(source_pin, protocol_pin)
        accept("complete-independent-source-freeze-contract",
               validate_contract(contract, source_pin, protocol_pin)["schema"]
               == CONTRACT_SCHEMA)
        accept("exact-103-counted-108-authenticated-history",
               contract["published_v21_history"][
                   "authoritative_counted_evidence_owner_count"
               ] == 103
               and contract["published_v21_history"][
                   "authenticated_digest_addressed_history_paths"
               ] == 108)
        accept("preserve-real-current-135-owner-140-reference-history",
               contract["current_published_history"][
                   "authoritative_counted_evidence_owner_count"
               ] == 135
               and contract["current_published_history"][
                   "authenticated_digest_addressed_history_paths"
               ] == 140)
        accept("preserve-real-published-v22-105-owner-110-reference-history",
               contract["published_v22_history"][
                   "authoritative_counted_evidence_owner_count"
               ] == 105
               and contract["published_v22_history"][
                   "authenticated_digest_addressed_history_paths"
               ] == 110)
        accept("preserve-real-published-v23-135-owner-140-reference-history",
               contract["published_v23_history"][
                   "authoritative_counted_evidence_owner_count"
               ] == 135
               and contract["published_v23_history"][
                   "authenticated_digest_addressed_history_paths"
               ] == 140)
        accept("preserve-all-thirteen-completed-original-c-workers",
               len(contract["current_published_history"][
                   "completed_c_original_campaign"
               ]["suite_results"]) == 13
               and contract["current_published_history"][
                   "completed_c_original_campaign"
               ]["actual_candidate_worker_count"] == 13)
        accept("preserve-all-real-completed-c-semantic-mismatches",
               contract["current_published_history"][
                   "completed_c_original_campaign"
               ]["semantic_mismatch_count"] == 1_262
               and contract["current_published_history"][
                   "completed_c_original_campaign"
               ]["verified_passing_case_count"] == 7_325
               and contract["current_published_history"][
                   "completed_c_original_campaign"
               ]["infrastructure_failure_count"] == 0)
        accept("preserve-all-thirty-distinct-real-c-campaign-owners",
               contract["current_published_history"][
                   "completed_c_original_campaign"
               ]["distinct_published_evidence_owner_count"] == 30)
        accept("preserve-failed-c-infrastructure-without-fake-matching",
               contract["current_published_history"]["recovered_c_failure"][
                   "archive_status"
               ] == "FAIL"
               and contract["current_published_history"][
                   "recovered_c_failure"
               ]["actual_candidate_worker_count"] == 0
               and contract["current_published_history"][
                   "recovered_c_failure"
               ]["semantic_mismatch_count"] == "NOT MEASURED")
        accept("preserve-actual-original-zig-failures",
               contract["published_v21_history"][
                   "historical_zig_semantic_mismatch_count"
               ] == 1_764)
        accept("planned-processes-are-not-actual-processes",
               contract["future_build_policy"]["actual_process_count"] == 0
               and contract["future_build_policy"][
                   "expected_total_process_count_only_after_success"
               ] == 26)
        accept("planned-overlay-is-not-actual-overlay",
               contract["frozen_overlay"]["actual_source_apply_count"] == 0)
        accept("native-output-digests-are-not-invented",
               all(item["sha256"] == "NOT MEASURED"
                   and item["bytes"] == "NOT MEASURED"
                   for item in contract["future_build_policy"][
                       "native_outputs"
                   ].values()))
        accept("preserve-frozen-original-case-denominator",
               contract["oracle"]["case_execution_count"] == 31_237
               and contract["oracle"]["suite_count"] == 13
               and contract["oracle"]["private_waiver_count"] == 13)
        accept("no-source-freeze-side-effects",
               contract["phase_boundary"] == expected_phase_boundary())
        accept("canonical-finite-round-trip",
               strict_json(canonical(contract), "synthetic contract") == contract)
        accept("distinct-exclusive-success-evidence",
               evidence_names("synthetic-v11", False)
               != evidence_names("synthetic-v11", True))

        for value in (
            "", "a" * 63, "a" * 65, "A" * 64, "z" * 64,
            "0" * 63 + "\n", 1, None,
        ):
            reject("reject-digest-" + repr(value),
                   lambda value=value: valid_digest(value, "hostile"))
        for value in (
            "", "Upper", "-leading", "trailing-", "double--dash",
            "with/slash", "with_under", "a" * 49, "a\x00b", None, 1,
        ):
            reject("reject-evidence-label-" + repr(value),
                   lambda value=value: checked_label(value))
        for value in (
            "", "/", "/tmp", "/tmp/", str(ROOT),
            "/tmp/rebar-phase2-native-build-v10-zig-synthetic",
            "/tmp/rebar-phase2-native-build-v7-zig-synthetic",
            "/tmp/" + PRIVATE_ROOT_PREFIX,
            "/tmp/" + PRIVATE_ROOT_PREFIX + "short",
            "/tmp/" + PRIVATE_ROOT_PREFIX + "../escaped",
            "/tmp/" + PRIVATE_ROOT_PREFIX + "bad.dot.value",
            "/tmp/" + PRIVATE_ROOT_PREFIX + "synthetic-v11/extra",
            "/tmp/" + PRIVATE_ROOT_PREFIX + "synthetic-v11/",
            None,
        ):
            reject("reject-private-root-" + repr(value),
                   lambda value=value: checked_workdir(value))
        for value in ("", "/tmp/escape", "../escape", "a/../b",
                      "a//b", "a/./b", "a\\b", "a\x00b", None):
            reject("reject-relative-owner-" + repr(value),
                   lambda value=value: checked_relative(value))
        for value in ("", "reference-c", "reference-a/..", "zig", None):
            reject("reject-cross-phase-" + repr(value),
                   lambda value=value: phase_paths(root, value))
        reject("reject-private-child-raw-string",
               lambda: checked_private_child(
                   str(phase_paths(root, "reference-a")["base"]),
                   root, "reference-a",
               ))
        reject("reject-private-child-root",
               lambda: checked_private_child(Path(root), root, "reference-a"))
        reject("reject-private-child-tmp-root",
               lambda: checked_private_child(Path("/tmp"), root, "reference-a"))
        reject("reject-private-child-cross-phase",
               lambda: checked_private_child(
                   phase_paths(root, "reference-b")["source"],
                   root, "reference-a",
               ))
        reject("reject-private-child-dotdot-escape",
               lambda: checked_private_child(
                   Path(root) / "reference-a" / ".." / "reference-b",
                   root, "reference-a",
               ))
        reject("reject-repeated-json-object-key",
               lambda: strict_json(b'{"x":1,"x":2}\n', "hostile"))
        reject("reject-noncanonical-json",
               lambda: strict_json(b'{ "x":1 }\n', "hostile"))
        reject("reject-json-nan",
               lambda: strict_json(b'{"x":NaN}\n', "hostile"))
        reject("reject-json-infinity",
               lambda: strict_json(b'{"x":Infinity}\n', "hostile"))
        reject("reject-json-array",
               lambda: strict_json(b'[]\n', "hostile"))
        reject("reject-truncated-json",
               lambda: strict_json(b'{"x":', "hostile"))
        reject("reject-unowned-command-role",
               lambda: checked_command(
                   "build_rust_engine", [PINNED_ZIG], root, "reference-a",
               ))
        reject("reject-shell-substitution",
               lambda: checked_command(
                   "build_zig_engine", ["/bin/sh", "-c", "zig build-lib"],
                   root, "reference-a",
               ))
        reject("reject-replaced-compiler",
               lambda: checked_command(
                   "build_zig_engine",
                   ["/usr/bin/zig"]
                   + planned_commands(root, "reference-a")[
                       "build_zig_engine"
                   ][1:],
                   root, "reference-a",
               ))
        reject("reject-cross-phase-compiler-argv",
               lambda: checked_command(
                   "build_zig_engine",
                   planned_commands(root, "reference-b")["build_zig_engine"],
                   root, "reference-a",
               ))
        reject("reject-truncated-compiler-argv",
               lambda: checked_command(
                   "build_zig_bridge",
                   planned_commands(root, "reference-a")[
                       "build_zig_bridge"
                   ][:-1],
                   root, "reference-a",
               ))
        reject("reject-mutated-compiler-argv",
               lambda: checked_command(
                   "build_zig_engine",
                   planned_commands(root, "reference-a")[
                       "build_zig_engine"
                   ] + ["--fetch"],
                   root, "reference-a",
               ))

        def mutated_native(role: str, mutation: Any) -> dict[str, Any]:
            value = strict_json(canonical(synthetic_native(role)), "synthetic ELF")
            mutation(value)
            return value

        reject("reject-external-engine-library",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["dynamic_tables"][0]["entries"].append(
                           {"tag": 1, "name": "libpcre2-8.so.0"}
                       )),
               ))
        reject("reject-wrong-engine-soname",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["dynamic_tables"][0]["entries"][1].update(
                           {"name": "_rust_engine.so"}
                       )),
               ))
        reject("reject-legacy-bridge-rpath",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["dynamic_tables"][0]["entries"].append(
                           {"tag": 15, "name": "/tmp/unowned"}
                       )),
               ))
        reject("reject-foreign-bridge-engine",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["dynamic_tables"][0]["entries"][0].update(
                           {"name": "_rust_engine.so"}
                       )),
               ))
        reject("reject-escaped-bridge-runpath",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["dynamic_tables"][0]["entries"][2].update(
                           {"name": "/tmp"}
                       )),
               ))
        reject("reject-stdlib-sre-symbol",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].append(
                           {"name": "_sre_compile", "section_index": 0}
                       )),
               ))
        reject("reject-external-pcre-symbol",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].append(
                           {"name": "pcre2_match", "section_index": 0}
                       )),
               ))
        reject("reject-cross-family-engine-symbol",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].append(
                           {"name": "rebar_rust_match", "section_index": 0}
                       )),
               ))
        reject("reject-dynamic-loader-symbol",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].append(
                           {"name": "dlopen", "section_index": 0}
                       )),
               ))
        reject("reject-python-module-import-symbol",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].append(
                           {"name": "PyImport_ImportModule", "section_index": 0}
                       )),
               ))
        reject("reject-missing-owned-engine-export",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].pop(0)
                   ),
               ))
        reject("reject-missing-owned-bridge-import",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].pop()
                   ),
               ))
        reject("reject-missing-module-initializer",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].pop(0)
                   ),
               ))
        reject("reject-substituted-unicode-helper",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["symbol_tables"]["tables"][0]["symbols"].append(
                           {"name": "_PyUnicode_RegexMatch", "section_index": 0}
                       )),
               ))
        reject("reject-duplicate-dynamic-table",
               lambda: audit_native_role(
                   "engine", mutated_native("engine", lambda value:
                       value["dynamic_tables"].append(
                           value["dynamic_tables"][0]
                       )),
               ))
        reject("reject-duplicate-symbol-table",
               lambda: audit_native_role(
                   "bridge", mutated_native("bridge", lambda value:
                       value["symbol_tables"]["tables"].append(
                           value["symbol_tables"]["tables"][0]
                       )),
               ))
        reject("reject-truncated-process-schedule",
               lambda: validate_process_schedule(records[:-1], root))

        def mutate_records(mutation: Any) -> list[dict]:
            value = json.loads(canonical(records).decode("ascii"))
            mutation(value)
            return value

        reject("reject-repeated-process-pid",
               lambda: validate_process_schedule(
                   mutate_records(lambda value:
                       value[1].update({"pid": value[0]["pid"]})), root,
               ))
        reject("reject-swapped-process-order",
               lambda: validate_process_schedule(
                   mutate_records(lambda value:
                       value.__setitem__(0, value[1])), root,
               ))
        reject("reject-contaminated-process-environment",
               lambda: validate_process_schedule(
                   mutate_records(lambda value:
                       value[0]["environment"].update(
                           {"HOME": "/tmp/unowned"}
                       )), root,
               ))
        reject("reject-signalled-process",
               lambda: validate_process_schedule(
                   mutate_records(lambda value:
                       value[0].update({"returncode": -11, "signal": 11})),
                   root,
               ))
        reject("reject-fabricated-stdout-digest",
               lambda: validate_process_schedule(
                   mutate_records(lambda value:
                       value[0]["stdout"].update({"sha256": "a" * 64})),
                   root,
               ))
        reject("reject-truncated-process-base64",
               lambda: decode_stream({
                   "bytes": 1,
                   "sha256": digest(b"x"),
                   "base64": "eA",
                   "complete": True,
               }))
        reject("reject-omitted-evidence-label",
               lambda: evidence_names("", False))

        def mutate_contract(mutation: Any) -> dict:
            value = strict_json(canonical(contract), "synthetic V11 contract")
            mutation(value)
            return value

        reject("reject-invented-actual-compiler-process",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["phase_boundary"].update(
                       {"compiler_processes_started": 1}
                   )), source_pin, protocol_pin))
        reject("reject-invented-actual-overlay-application",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["frozen_overlay"].update(
                       {"actual_source_apply_count": 1}
                   )), source_pin, protocol_pin))
        reject("reject-invented-native-output-hash",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["future_build_policy"]["native_outputs"][
                       "engine"
                   ].update({"sha256": "a" * 64})), source_pin, protocol_pin))
        reject("reject-weakened-case-denominator",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["oracle"].update({"case_execution_count": 31_236})),
                   source_pin, protocol_pin))
        reject("reject-hidden-original-zig-failure",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["published_v21_history"].update(
                       {"historical_zig_semantic_mismatch_count": 0}
                   )), source_pin, protocol_pin))
        reject("reject-changed-evidence-owner-denominator",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["published_v21_history"].update(
                       {"authoritative_counted_evidence_owner_count": 105}
                   )), source_pin, protocol_pin))
        reject("reject-hidden-new-c-failure-owners",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["current_published_history"].update(
                       {"authoritative_counted_evidence_owner_count": 103}
                   )), source_pin, protocol_pin))
        reject("reject-invented-c-matching-results",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["current_published_history"][
                       "recovered_c_failure"
                   ].update({"semantic_mismatch_count": 0})),
                   source_pin, protocol_pin))
        reject("reject-hidden-completed-c-worker",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["current_published_history"][
                       "completed_c_original_campaign"
                   ]["suite_results"].pop()), source_pin, protocol_pin))
        reject("reject-erased-completed-c-semantic-mismatch",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["current_published_history"][
                       "completed_c_original_campaign"
                   ].update({"semantic_mismatch_count": 0})),
                   source_pin, protocol_pin))
        reject("reject-invented-completed-c-infrastructure-failure",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["current_published_history"][
                       "completed_c_original_campaign"
                   ].update({"infrastructure_failure_count": 1})),
                   source_pin, protocol_pin))
        reject("reject-hidden-completed-c-campaign-evidence-owner",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["current_published_history"].update({
                       "additional_completed_c_campaign_evidence_owner_count":
                           29,
                   })), source_pin, protocol_pin))
        reject("reject-changed-frozen-v22-history",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["published_v22_history"].update({
                       "authenticated_digest_addressed_history_paths": 109,
                   })), source_pin, protocol_pin))
        reject("reject-changed-published-current-v23-history",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["published_v23_history"].update({
                       "authenticated_digest_addressed_history_paths": 139,
                   })), source_pin, protocol_pin))
        reject("reject-claimed-open-holdout",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["phase_boundary"].update(
                       {"holdout_opened": True}
                   )), source_pin, protocol_pin))
        reject("reject-claimed-performance-timing",
               lambda: validate_contract(mutate_contract(lambda value:
                   value["phase_boundary"].update({"clock_samples": 1})),
                   source_pin, protocol_pin))

        probes: tuple[tuple[str, Any], ...] = (
            ("block-built-in-file-open",
             lambda: builtins.open("/tmp/rebar-v10-forbidden", "rb")),
            ("block-io-file-open",
             lambda: io.open("/tmp/rebar-v10-forbidden", "rb")),
            ("block-descriptor-open",
             lambda: os.open("/tmp", os.O_RDONLY)),
            ("block-descriptor-read", lambda: os.read(0, 1)),
            ("block-descriptor-write", lambda: os.write(1, b"x")),
            ("block-filesystem-stat", lambda: os.stat("/tmp")),
            ("block-filesystem-lstat", lambda: os.lstat("/tmp")),
            ("block-directory-creation",
             lambda: os.mkdir("/tmp/rebar-v10-forbidden")),
            ("block-filesystem-unlink",
             lambda: os.unlink("/tmp/rebar-v10-forbidden")),
            ("block-filesystem-replacement",
             lambda: os.replace("/tmp/a", "/tmp/b")),
            ("block-filesystem-sync", lambda: os.fsync(1)),
            ("block-path-source-read", lambda: Path("/tmp").read_bytes()),
            ("block-path-source-write",
             lambda: Path("/tmp/rebar-v10-forbidden").write_bytes(b"x")),
            ("block-path-resolution", lambda: Path("/tmp").resolve()),
            ("block-compiler-process",
             lambda: subprocess.Popen((PINNED_ZIG, "version"))),
            ("block-external-process",
             lambda: subprocess.run((PINNED_READELF, "--version"))),
            ("block-shell-process", lambda: os.system("true")),
            ("block-private-root-creation",
             lambda: tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX,
                                      dir="/tmp")),
            ("block-temporary-source", lambda: tempfile.mkstemp()),
            ("block-network-socket", lambda: socket.socket()),
            ("block-network-dns", lambda: socket.getaddrinfo("example.com", 443)),
            ("block-native-library-load", lambda: ctypes.CDLL(ENGINE_FILENAME)),
            ("block-native-python-library-load",
             lambda: ctypes.PyDLL(BRIDGE_FILENAME)),
            ("block-zig-candidate-import",
             lambda: importlib.import_module("candidates.zig_candidate")),
            ("block-cross-family-candidate-import",
             lambda: importlib.import_module("candidates.rust_candidate")),
            ("block-stdlib-regex-import",
             lambda: importlib.import_module("re")),
            ("block-candidate-thread", lambda: threading.Thread().start()),
            ("block-performance-clock", lambda: time.perf_counter()),
            ("block-performance-nanoclock", lambda: time.perf_counter_ns()),
            ("block-monotonic-clock", lambda: time.monotonic()),
            ("block-wall-clock", lambda: time.time()),
            ("block-wait", lambda: time.sleep(0)),
        )
        for name, operation in probes:
            reject(name, operation)
        blocked = dict(boundary.blocked)

    require(sum(blocked.values()) == len(probes),
            "every external-effect probe must be individually blocked")
    require(all(blocked[key] > 0 for key in (
        "filesystem", "process", "temporary", "network", "native",
        "candidate_import", "thread", "clock",
    )), "exercise every frozen source-only effect boundary")
    return {
        "schema": SCHEMA,
        "version": 11,
        "status": "PASS",
        "mode": "SOURCE-ONLY SYNTHETIC SELF-TEST",
        "accepted_control_count": len(accepted),
        "accepted_controls": accepted,
        "rejected_hostile_control_count": len(rejected),
        "rejected_hostile_controls": rejected,
        "blocked_effect_control_count": sum(blocked.values()),
        "blocked_effects_by_kind": blocked,
        "actual_synthetic_processes_started": 0,
        "synthetic_process_record_count": EXPECTED_PROCESS_COUNT,
        "actual_synthetic_private_roots_created": 0,
        "actual_synthetic_source_applications": 0,
        "workspace_mutations": 0,
        **expected_phase_boundary(),
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--label")
    selected = parser.parse_args(arguments)
    valid_digest(selected.source_sha256, "V11 source")
    valid_digest(selected.protocol_sha256, "V11 protocol")
    if selected.contract_sha256 is not None:
        valid_digest(selected.contract_sha256, "V11 contract")
    if selected.render_contract:
        require(selected.contract_sha256 is None and selected.label is None,
                "contract rendering is strictly read-only and has no build label")
    else:
        require(selected.contract_sha256 is not None,
                "independently pin the exact published V11 machine contract")
        if selected.build:
            require(selected.label is not None,
                    "a real native build requires one explicit fresh label")
            checked_label(selected.label)
        else:
            require(selected.label is None,
                    "a safe source-only gate cannot request a native build label")
    return selected


def main(arguments: list[str] | None = None) -> int:
    try:
        selected = parse_arguments(
            list(sys.argv[1:] if arguments is None else arguments)
        )
        if selected.self_test:
            result = self_test(
                selected.source_sha256, selected.protocol_sha256,
                selected.contract_sha256,
            )
            exit_code = 0
        elif selected.verify_context:
            result, _retained = authenticate_context(
                selected.source_sha256, selected.protocol_sha256,
                selected.contract_sha256,
            )
            exit_code = 0
        elif selected.render_contract:
            authenticate_context(selected.source_sha256,
                                 selected.protocol_sha256)
            result = contract_document(selected.source_sha256,
                                       selected.protocol_sha256)
            exit_code = 0
        else:
            exit_code, result = run_build(
                selected.source_sha256, selected.protocol_sha256,
                selected.contract_sha256, selected.label,
            )
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return exit_code
    except (FreezeError, OSError, ValueError, TypeError, UnicodeError,
            OverflowError, RecursionError, subprocess.SubprocessError) as error:
        sys.stderr.write("OWNED ZIG SOURCE BUILD V11: FAIL: "
                         + type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
