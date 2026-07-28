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
SCHEMA = "rebar-candidate-current-overview-v4"
SOURCE_RELATIVE = "tools/render_candidate_current_overview_v4.py"
INPUT_RELATIVE = "docs/evidence/candidate-current-overview-v4.inputs.json"
SUMMARY_RELATIVE = "docs/evidence/candidate-current-overview-v4.json"
SVG_RELATIVE = "docs/evidence/candidate-current-overview-v4.svg"
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
FAMILY_NAMES = ("python", "rust", "c", "zig", "cpp", "go")
DISPLAY_NAMES = {
    "python": "Python re",
    "rust": "Rust",
    "c": "C",
    "zig": "Zig",
    "cpp": "C++",
    "go": "Go",
}
MAX_SOURCE_BYTES = 8 * 1_048_576
MAX_ARCHIVE_BYTES = 8 * 1_048_576
MAX_DOCUMENT_BYTES = 16 * 1_048_576
MAX_GRAPH_BYTES = 2 * 1_048_576
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
}
GO_ENGINE_SHA = "6472c4413921f3a877455315400c532e7632a871a96d46de9583fa6170a43192"
GO_ADAPTER_SHA = "816d21527b9806afbc9457122f72f8f6b62c39b8b791d3f363745d412cbe3d20"
GO_MODULE_SHA = "9297c4e8fe4649196150400d23a4da584d7ef721347f7095399a7382edad669b"
GO_BRIDGE_SHA = "52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a"
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
    raw: bytes, description: str, *, require_canonical: bool = True
) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_DOCUMENT_BYTES,
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
                "BASELINE PASS" if family == "python" else "NOT MEASURED"
            ),
            "performance": "NOT MEASURED",
        }
        if family in BUILD_PINS:
            build = ZIG_V3_SUCCESS if family == "zig" else BUILD_PINS[family]
            row["build_evidence"] = {
                "archive": pin(*build["archive"]),
                "receipt": pin(*build["receipt"]),
                "expected_build_status": build["build_status"],
            }
        else:
            row["build_evidence"] = None
        row["correctness_evidence"] = (
            {
                "archive": pin(*C_GATE_V4_FAILURE["archive"]),
                "receipt": pin(*C_GATE_V4_FAILURE["receipt"]),
                "expected_gate_status": "FAIL",
                "qualified_case_executions": 0,
                "actual_failed_worker_count": 1,
            }
            if family == "c"
            else None
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
        "version": 4,
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


def bounded_gzip(raw: bytes) -> bytes:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES,
        "require one complete bounded source-build archive",
    )
    try:
        decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
        expanded = decompressor.decompress(raw, MAX_DOCUMENT_BYTES + 1)
        require(
            len(expanded) <= MAX_DOCUMENT_BYTES
            and decompressor.eof is True
            and decompressor.unused_data == b""
            and decompressor.unconsumed_tail == b"",
            "reject clipped, concatenated, or oversized build evidence",
        )
        tail = decompressor.flush()
        require(
            len(expanded) + len(tail) <= MAX_DOCUMENT_BYTES,
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
        for key in ("historical_build_evidence", "historical_correctness_evidence"):
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
        if name not in ("phase1_inventory", "phase2_inventory"):
            raw = source_reader(relative, digest)
            require(
                digestor(raw) == digest,
                "a complete frozen chart source was replaced: " + relative,
            )
    phase1, _, _ = document_loader(*CORE_PINS["phase1_inventory"], False)
    phase2, _, _ = document_loader(*CORE_PINS["phase2_inventory"], False)
    validate_baseline(phase1)
    validate_candidate_inventory(phase2)
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
    c_gate = validate_c_gate_v4_failure(
        current_c_receipt,
        current_c_report,
        current_c_compressed,
        current_c_expanded,
        digestor,
    )
    require(
        historical_zig_build["build_status"] == "FAIL"
        and historical_zig_build["zig_engine_reproduces"] is False
        and historical_c_gate["gate_status"] == "FAIL"
        and historical_c_gate["failed_before_candidate_execution"] is True,
        "a genuine prior Zig build or C preflight failure was hidden",
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
        "c_full_gate": c_gate,
        "historical_c_full_gate": historical_c_gate,
        "historical_zig_build": historical_zig_build,
        "reproducible_native_family_count": 3,
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
    width, height = 1_600, 1_660
    blue, green, amber, slate = "#0072b2", "#009e73", "#e69f00", "#66768a"
    pale, track, ink = "#f4f7fb", "#dfe7ef", "#16324f"
    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1660" '
        'viewBox="0 0 1600 1660" role="img" '
        'aria-labelledby="current-overview-title current-overview-description">',
        '<title id="current-overview-title">Can a from-scratch engine replace '
        "Python's re, and is it faster?</title>",
        '<desc id="current-overview-description">Python 3.14.6 passes its '
        "complete 31,237-check reference. The current Rust, C, and corrected "
        "Zig engines were each independently built identically twice; this "
        "is build evidence, not a passed compatibility test. The actual latest "
        "C worker failed with zero qualified cases; its earlier preflight "
        "failure remains preserved. The corrected Zig engine and bridge now "
        "match in two fresh builds; its earlier nonreproducible failure "
        "also remains preserved. "
        "C++ and Go have independently authored, source-pinned implementations "
        "but have not been built or tested. No replacement is qualified. "
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
        '<rect width="1600" height="1660" rx="24" fill="' + pale + '"/>',
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
        ("5", "from-scratch candidate families"),
        ("3", "families built identically twice"),
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
        '<rect x="64" y="278" width="1472" height="745" rx="18" '
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
            "rust", "Rust", "NOT MEASURED",
            "Built from its own source twice; both binaries match",
            "pending",
        ),
        (
            "c", "C", "NOT MEASURED",
            "Built twice; full-test worker failed; 0 qualified cases",
            "warning",
        ),
        (
            "zig", "Zig", "NOT MEASURED",
            "Built twice; identical engine and bridge; prior failure preserved",
            "pending",
        ),
        (
            "cpp", "C++", "NOT MEASURED",
            "Independent source checked; candidate not yet built",
            "pending",
        ),
        (
            "go", "Go", "NOT MEASURED",
            "Independent source checked; candidate not yet built",
            "pending",
        ),
    )
    for index, (family, title, outcome, detail, outcome_style) in enumerate(rows):
        y = 392 + 96 * index
        accent = (
            green if family == "python"
            else amber if family == "c"
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
                "WORKER FAILED; 0 QUALIFIED" if family == "c" else outcome,
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
            92, 996,
            "Only Python has passed the full test. Previous Zig build and C"
            " preflight failures are preserved; no candidate is qualified.",
            "small",
        ),
        '<rect x="64" y="1048" width="1472" height="507" rx="18" '
        'fill="#ffffff" stroke="#d8e3ed"/>',
        svg_text(89, 1093, "2. Is it faster than Python?", "section"),
        svg_text(
            91, 1127,
            "Speed has not been measured. There are no candidate speed bars,"
            " rankings, or hidden benchmark results.",
            "body",
        ),
    ])
    for index, family in enumerate(FAMILY_NAMES):
        y = 1_164 + index * 43
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
        '<line x1="358" y1="1451" x2="1162" y2="1451" '
        'stroke="#98a8b9" stroke-width="2"/>',
        '<line x1="626" y1="1437" x2="626" y2="1465" '
        'stroke="' + blue + '" stroke-width="3"/>',
        '<line x1="1028" y1="1428" x2="1028" y2="1465" '
        'stroke="' + amber + '" stroke-width="3" stroke-dasharray="6 5"/>',
        svg_text(
            626, 1488, "1.0x reference (not timed)", "small", anchor="middle"
        ),
        svg_text(1_028, 1488, "1.5x goal", "warning", anchor="middle"),
        svg_text(
            91, 1525,
            "The 1.5x marker is a future requirement, not an observation."
            " Final benchmark and memory use: NOT MEASURED.",
            "small",
        ),
        svg_text(
            66, 1590,
            "Generated only from complete, hash-pinned current source"
            " and published build evidence.",
            "foot",
        ),
        svg_text(
            66, 1615,
            "Input SHA-256: " + manifest_hash,
            "foot",
        ),
        svg_text(
            66, 1637,
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
    expanded = bounded_gzip(stored) if compressed else stored
    exact_pretty_printed_v3 = (
        compressed is False
        and relative == CORE_PINS["phase2_inventory"][0]
        and expected == CORE_PINS["phase2_inventory"][1]
    )
    return (
        decode_document(
            expanded,
            relative,
            require_canonical=not exact_pretty_printed_v3,
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
        ".rebar-current-overview-v4-"
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
        for relative, digest, document in (
            (*CORE_PINS["phase1_inventory"], baseline),
            (*CORE_PINS["phase2_inventory"], inventory),
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
        accept("all five independent candidate families stay visible", (
            snapshot["families"] == list(FAMILY_NAMES)
            and len(snapshot["families"]) == 6
        ))
        accept("all complete current candidate source owners are authenticated", (
            snapshot["all_current_source_owners_authenticated"] is True
            and snapshot["current_source_owner_count"] == 22
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
        accept("all three genuine native source builds reproduce", (
            snapshot["reproducible_native_family_count"] == 3
            and all(snapshot["candidate_builds"][name]["build_status"] == "PASS"
                    for name in ("rust", "c", "zig"))
        ))
        accept("source-only C++ and Go are not represented as built", (
            snapshot["cpp_build_status"] == "NOT MEASURED"
            and snapshot["go_build_status"] == "NOT MEASURED"
        ))
        accept("preserve the actual failed C worker and zero qualified cases", (
            snapshot["c_full_gate"]["gate_status"] == "FAIL"
            and snapshot["c_full_gate"]["failed_before_candidate_execution"] is False
            and snapshot["c_full_gate"]["actual_failed_worker_count"] == 1
            and snapshot["c_full_gate"]["qualified_candidate_case_executions"] == 0
            and snapshot["c_full_gate"]["failure_archive_preserved"] is True
            and snapshot["c_full_gate"]["full_case_denominator"] == DENOMINATOR
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
            and b"WORKER FAILED; 0 QUALIFIED" in svg
            and b"identical engine and bridge" in svg
            and b"Previous Zig build and C" in svg
        ))
        accept("large chart preserves readable candidate labels", (
            b'width="1600"' in svg
            and b'height="1660"' in svg
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
