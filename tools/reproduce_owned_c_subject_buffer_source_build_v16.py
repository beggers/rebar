#!/usr/bin/env python3
"""Freeze an exact first-party C subject-buffer build without performing it."""

from __future__ import annotations

import _imp
import _io
import _thread
import argparse
import builtins
import copy
import gzip
import hashlib
import importlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import types
import zlib
from typing import Any


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/reproduce_owned_c_subject_buffer_source_build_v16.py"
PROTOCOL = "oracle/phase2/C-SUBJECT-BUFFER-SOURCE-BUILD-V16.md"
CONTRACT = "oracle/phase2/c-subject-buffer-source-build-v16.json"
EVIDENCE = "oracle/phase2/evidence"
SCHEMA = "rebar-phase2-owned-c-subject-buffer-source-build-v16"
VERSION = 16
FAMILY = "c"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
DEVICE = 2064
OWNER_LIMIT = 8 * 1024 * 1024
REPORT_LIMIT = 48 * 1024 * 1024
ARCHIVE_LIMIT = 64 * 1024 * 1024
LABEL_LIMIT = 80
Owner = tuple[str, str, int, int]

GOAL: Owner = (
    "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756, 31364044,
)
P0_V4: dict[str, Owner] = {
    "source": ("tools/verify_owned_p0_completeness_v4.py",
               "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
               29094, 428927),
    "protocol": ("oracle/phase1/P0-COMPLETENESS-V4.md",
                 "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
                 4261, 524712),
    "contract": ("oracle/phase1/p0-completeness-v4.json",
                 "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
                 34875, 524713),
}
PRODUCER_V4: dict[str, Owner] = {
    "source": ("tools/run_owned_six_family_original_p0_producer_v4.py",
               "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8",
               230782, 431710),
    "protocol": ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md",
                 "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5",
                 5981, 524782),
    "contract": ("oracle/phase2/six-family-p0-producer-v4.json",
                 "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5",
                 30867, 524783),
}
ORIGINAL_C: Owner = (
    "candidates/_vm_native.c",
    "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
    218185, 428072,
)
ADAPTER: Owner = (
    "candidates/vm_candidate.py",
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
    60707, 428074,
)
FEATURE: dict[str, Owner] = {
    "variant": (
        "candidates/c/variants/subject_buffer_ownership_v1/vm_native.c",
        "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962",
        222212, 524723,
    ),
    "source": (
        "tools/apply_owned_c_subject_buffer_ownership_v1.py",
        "8262295a9e84c5fa30fe4e83102236fbaa233c914fb0c570d5fce3cdaf8605d2",
        80090, 428938,
    ),
    "protocol": (
        "oracle/phase2/C-SUBJECT-BUFFER-OWNERSHIP-V1.md",
        "997af2edeced019663886aa7e20873506e4b13ee361bf5ce8d533e3ad2ea7393",
        5527, 524724,
    ),
    "contract": (
        "oracle/phase2/c-subject-buffer-ownership-v1.json",
        "b2ef8b9f5f9c7262be0e639d17436d0e1e8637d5649741bf2aa1538ebef3eb6a",
        12435, 524726,
    ),
}
GRAPH_VERSION = 67
GRAPH: dict[str, Owner] = {
    "source": (
        "tools/render_candidate_current_overview_v67.py",
        "37a5632885a05d1b2e1eb0aaeaa9d862e55d29744ac274e7ccf803c12f64ff04",
        157037, 430273,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v67.inputs.json",
        "7750b4f619f713226c8971b33cfd0f852282be5cfcc9ae7f1e6f7358d2a10382",
        1062468, 430309,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v67.json",
        "45e69fef0e5b072c6fd8ee575b9e875aca36a214777bd1996da405d3ec25e252",
        2949727, 430310,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v67.svg",
        "b2dd7168b9686025afc2afac3846f60af11ab5563fed42b01cc1819fc4199037",
        14642, 430326,
    ),
}
C_RECEIPT: Owner = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-"
    "pickle-original-p0-failures-publication-receipt.json",
    "c4099d537475b250e15c6d696fead132889422aa3cfe445d86e27c5cc19f2ba9",
    3482, 524641,
)
RUST_RECEIPT: Owner = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-"
    "phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-"
    "publication-receipt.json",
    "8735e5351f62de2a77369eb8401e225cebd31434b09f07db40e79550ba7cc7d2",
    6708, 525044,
)
RUST_V18_SOURCE: dict[str, Owner] = {
    "source": (
        "tools/reproduce_owned_rust_buffer_shape_source_build_v18.py",
        "5a464fbd62ac375d236fa2debce14ae1507ce1bf494efb35695210199bdbef8c",
        128761, 428939,
    ),
    "protocol": (
        "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V18.md",
        "52513bb429416e182774558eebf2ae4e1d217e8656da673b9f765d4f3df75991",
        6523, 524727,
    ),
    "contract": (
        "oracle/phase2/rust-buffer-shape-source-build-v18.json",
        "e57d67e1b16bb13a3555c05c0b6b546b83ab3a6a7e63beec5c81896e01f92301",
        23099, 524728,
    ),
}
RUST_V18_BUILD_RECEIPT: Owner = (
    "oracle/phase2/evidence/native-source-build-v18-rust-phase2-v18-rust-"
    "buffer-shape-pickle-lifetime-publication-receipt.json",
    "32c422b9624a2565afd8d710700e377aa39aae4aa93d3742da483843869f2104",
    3486, 524747,
)
# Metadata is attested by the small receipt; this archive is never opened.
RUST_V18_BUILD_ARCHIVE: Owner = (
    "oracle/phase2/evidence/native-source-build-v18-rust-phase2-v18-rust-"
    "buffer-shape-pickle-lifetime.json.gz",
    "f59818e4aaea2999a5fec608d4d8ed761d372e1725548e3c3ff57773d01dffdc",
    109345, 524733,
)
KERNEL: dict[str, Owner] = {
    "v8": (
        "tools/reproduce_owned_native_source_build_v8.py",
        "afc4f8070cb3c1bccf312b77b019cbb6d71f8dcf976f4a2e921e18cc7c063dd4",
        63656, 429068,
    ),
    "v7": (
        "tools/reproduce_owned_native_source_build_v7.py",
        "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7",
        300624, 431752,
    ),
    "v4": (
        "tools/reproduce_owned_native_source_build_v4.py",
        "efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1",
        136084, 431135,
    ),
}
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "build_c_extension",
    "extension_dynamic", "extension_symbols", "extension_sections",
    "extension_notes",
)
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768),
    ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120),
    ("shape_v2", 10240), ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
_ACTIVE: dict[str, Any] | None = None
_APPLIED: set[tuple[str, str]] = set()


class BuildError(Exception):
    """The independently frozen first-party C build was not established."""


def need(condition: Any, reason: str) -> None:
    if condition is not True:
        raise BuildError(reason)


def digest(raw: bytes) -> str:
    need(type(raw) is bytes, "hash complete first-party owner bytes only")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, allow_nan=False, ensure_ascii=True, sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
        raise BuildError("require exact finite canonical first-party JSON") from error


def checked_digest(value: Any, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(character in "0123456789abcdef" for character in value),
         "require an exact lowercase SHA-256: " + label)
    return value


def checked_relative(value: Any) -> tuple[str, ...]:
    need(type(value) is str and 0 < len(value) <= 512,
         "require one exact bounded first-party owner")
    path = PurePosixPath(value)
    need(not path.is_absolute() and str(path) == value
         and 0 < len(path.parts) <= 16
         and all(part not in {"", ".", ".."} for part in path.parts),
         "reject escaped, noncanonical, linked, or broad owner paths")
    lowered = value.lower()
    need("holdout" not in lowered and "benchmark" not in lowered
         and not lowered.endswith((".so", ".gz", ".xz", ".zip", ".tar", ".zst")),
         "never open an installed native, archive, benchmark, or hidden holdout")
    return path.parts


def allowed_owners() -> frozenset[str]:
    rows: list[Owner] = [
        GOAL, ORIGINAL_C, ADAPTER, C_RECEIPT, RUST_RECEIPT,
        RUST_V18_BUILD_RECEIPT,
    ]
    for group in (P0_V4, PRODUCER_V4, FEATURE, GRAPH, RUST_V18_SOURCE, KERNEL):
        rows.extend(group.values())
    return frozenset([SELF, PROTOCOL, CONTRACT, *(row[0] for row in rows)])


def read_owner(owner: Owner) -> bytes:
    relative, expected, size, inode = owner
    checked_digest(expected, relative)
    parts = checked_relative(relative)
    need(relative in allowed_owners(), "reject an unauthorised source-context owner")
    need(type(size) is int and 0 < size <= OWNER_LIMIT
         and type(inode) is int and inode > 0,
         "require the exact bounded source-owner size and inode")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    parent = os.open(str(ROOT), flags | getattr(os, "O_DIRECTORY", 0))
    descriptor: int | None = None
    try:
        for part in parts[:-1]:
            child = os.open(part, flags | getattr(os, "O_DIRECTORY", 0), dir_fd=parent)
            os.close(parent)
            parent = child
        descriptor = os.open(parts[-1], flags, dir_fd=parent)
        first = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        need(stat.S_ISREG(first.st_mode)
             and (first.st_dev, first.st_ino, first.st_size)
             == (DEVICE, inode, size)
             and (named.st_dev, named.st_ino, named.st_size)
             == (DEVICE, inode, size)
             and first.st_uid == os.geteuid()
             and stat.S_IMODE(first.st_mode) == 0o600
             and first.st_nlink == 1,
             "reject a changed, linked, nonprivate, or substituted owner: " + relative)
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            block = os.read(descriptor, min(remaining, 262144))
            need(type(block) is bytes and bool(block),
                 "reject truncated authenticated owner: " + relative)
            pieces.append(block)
            remaining -= len(block)
        need(os.read(descriptor, 1) == b"", "reject trailing authenticated owner bytes")
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        need((after.st_dev, after.st_ino, after.st_size,
              after.st_mtime_ns, after.st_ctime_ns)
             == (first.st_dev, first.st_ino, first.st_size,
                 first.st_mtime_ns, first.st_ctime_ns)
             and digest(raw) == expected,
             "reject a swapped or incorrectly hashed owner: " + relative)
        return raw
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(parent)


def dynamic_owner(relative: str, fingerprint: str) -> Owner:
    checked_relative(relative)
    need(relative in {SELF, PROTOCOL, CONTRACT},
         "authenticate only one independently supplied V16 source owner")
    checked_digest(fingerprint, relative)
    observed = os.stat(str(ROOT / relative), follow_symlinks=False)
    need(stat.S_ISREG(observed.st_mode) and observed.st_dev == DEVICE
         and 0 < observed.st_size <= OWNER_LIMIT
         and stat.S_IMODE(observed.st_mode) == 0o600
         and observed.st_uid == os.geteuid() and observed.st_nlink == 1,
         "reject an unsafe independent V16 source owner")
    return relative, fingerprint, observed.st_size, observed.st_ino


def unique_pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        need(type(key) is str and key not in result,
             "reject repeated frozen machine-document fields")
        result[key] = value
    return result


def document(raw: bytes, label: str) -> dict[str, Any]:
    need(type(raw) is bytes and 0 < len(raw) <= OWNER_LIMIT,
         "bound complete source-context machine document: " + label)
    try:
        value = json.loads(
            raw.decode("utf-8", "strict"), object_pairs_hook=unique_pairs,
            parse_constant=lambda constant: (_ for _ in ()).throw(
                ValueError("nonfinite frozen value: " + constant),
            ),
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise BuildError("reject malformed frozen document: " + label) from error
    need(type(value) is dict and canonical(value) == raw,
         "reject a noncanonical or changed frozen document: " + label)
    return value


def owner_pin(owner: Owner) -> dict[str, Any]:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2],
            "device": DEVICE, "inode": owner[3], "mode": "0600", "nlink": 1}


def public_pin(owner: Owner) -> dict[str, Any]:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2]}


def owner_group(group: dict[str, Owner]) -> dict[str, dict[str, Any]]:
    return {key: owner_pin(value) for key, value in sorted(group.items())}


def effects() -> dict[str, Any]:
    return {
        "actual_candidate_workers": 0, "actual_reference_workers": 0,
        "archive_bytes_read": 0, "archives_inflated": 0,
        "archives_opened": 0, "benchmark_files_read": 0,
        "candidate_correctness": "NOT MEASURED", "candidate_imports": 0,
        "candidate_processes_started": 0, "clock_samples": 0,
        "compiler_processes_started": 0, "hidden_cases_read": 0,
        "holdout": "NOT OPENED", "memory": "NOT MEASURED",
        "native_activations_started": 0, "native_builds_started": 0,
        "native_libraries_loaded": 0, "network_requests": 0,
        "original_native_targets_read": 0,
        "original_source_targets_modified": 0,
        "performance": "NOT MEASURED", "qualified_candidate_count": 0,
        "reference_processes_started": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "threads_started": 0, "timing_trials_run": 0,
        "undefined_behavior": "NOT MEASURED", "winner_selected": False,
        "workspace_mutations": 0,
    }


def verify_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
         and os.path.realpath(sys.executable) == PYTHON
         and os.path.abspath(__file__) == str(ROOT / SELF)
         and os.path.realpath(__file__) == str(ROOT / SELF),
         "use only exact isolated no-bytecode stable CPython 3.14.6")
    need(not any(name == "candidates" or name.startswith("candidates.")
                 for name in sys.modules),
         "never import a candidate in a source-only build freeze")


def load_source(owner: Owner, name: str) -> types.ModuleType:
    need(type(name) is str and name.startswith("_rebar_exact_c_subject_buffer_v16_"),
         "load only a named frozen first-party source")
    need(name not in sys.modules, "reject an already-loaded substitute module")
    raw = read_owner(owner)
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / owner[0])
    module.__package__ = None
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    need(read_owner(owner) == raw, "reject a source changed during isolated loading")
    return module


def graph_observation(summary: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    need(summary.get("schema")
         == "rebar-candidate-current-overview-v" + str(GRAPH_VERSION) + "-summary"
         and summary.get("version") == GRAPH_VERSION
         and summary.get("status") == "PASS"
         and inputs.get("schema")
         == "rebar-candidate-current-overview-v" + str(GRAPH_VERSION) + "-inputs"
         and inputs.get("version") == GRAPH_VERSION,
         "reject a stale, future, or fabricated published overview")
    source = summary.get("source")
    input_owner = summary.get("inputs")
    svg_owner = summary.get("svg")
    need(source == public_pin(GRAPH["source"])
         and input_owner == public_pin(GRAPH["inputs"])
         and svg_owner == public_pin(GRAPH["svg"]),
         "bind all four separate genuinely pushed overview owners")
    for observed in (summary, inputs):
        need(observed.get("authenticated_evidence_owner_lower_bound") == 225
             and observed.get("authenticated_history_reference_lower_bound") == 230
             and observed.get("actual_c_semantic_mismatch_count") == 1230
             and observed.get("actual_c_verified_passing_case_count") == 7325
             and observed.get("actual_rust_semantic_mismatch_count") == 1440
             and observed.get("actual_rust_verified_passing_case_count") == 14853
             and observed.get("full_case_denominator") == 31237
             and observed.get("qualified_candidate_count") == 0
             and observed.get("final_holdout_opened") is False
             and observed.get("runtime_no_delegation") == "NOT ESTABLISHED"
             and observed.get("performance") == "NOT MEASURED"
             and observed.get("rust_native_build_v17_authorization_status") == "BLOCKED"
             and observed.get("rust_native_build_v17_status") == "NOT RUN"
             and observed.get("rust_native_build_v18_source_status") == "SOURCE FROZEN"
             and observed.get("rust_native_build_v18_status") == "PASS"
             and observed.get("rust_native_build_v18_reproducible_build_status") == "PASS"
             and observed.get("rust_native_build_v18_compiler_process_count") == 28
             and observed.get("rust_native_build_v18_expected_compiler_process_count") == 28
             and observed.get("rust_native_build_v18_matching_status") == "NOT RUN"
             and observed.get("rust_native_build_v18_activation_status") == "NOT RUN"
             and observed.get("rust_native_build_v18_candidate_qualified") is False
             and observed.get("rust_native_build_v18_candidate_workers_started") == 0
             and observed.get("rust_native_build_v18_archive_sha256_attested_by_receipt")
                 == RUST_V18_BUILD_ARCHIVE[1]
             and observed.get("rust_native_build_v18_archive_bytes_attested_by_receipt")
                 == RUST_V18_BUILD_ARCHIVE[2]
             and observed.get("rust_native_build_v18_archive_opened_by_graph") is False
             and observed.get("rust_native_build_v18_archive_bytes_read_by_graph") == 0
             and observed.get("rust_native_build_v18_archive_inflations_by_graph") == 0,
             "preserve actual losses, lower bounds, blocked gate, and sealed holdout")
    need(summary.get("actual_current_graph_predecessor_version") == 66
         and summary.get("actual_c_v4_original_campaign_status") == "FAIL"
         and summary.get("actual_rust_v10_candidate_status") == "FAIL"
         and summary.get("suite_count") == 13
         and summary.get("private_waiver_count") == 13
         and summary.get("phase1_v4_oracle_readiness_status") == "PASS"
         and summary.get("candidate_qualification_status") == "BLOCKED"
         and summary.get("c_subject_buffer_ownership_v1_feature_status") == "SOURCE FROZEN"
         and summary.get("c_subject_buffer_ownership_v1_build_status") == "NOT BUILT"
         and summary.get("c_subject_buffer_ownership_v1_matching_status") == "NOT RUN"
         and summary.get("c_subject_buffer_ownership_v1_activation_status") == "NOT RUN"
         and summary.get("c_subject_buffer_ownership_v1_candidate_qualified") is False
         and summary.get("c_subject_buffer_ownership_v1_independent_source_owner_count") == 4,
         "never promote a published source feature into a candidate or build")
    proof = summary.get("c_subject_buffer_ownership_v1_source_freeze")
    need(type(proof) is dict and proof.get("status") == "SOURCE FROZEN"
         and proof.get("family") == FAMILY
         and proof.get("independent_feature_source_owner_count") == 4
         and proof.get("candidate_matching_status") == "NOT RUN"
         and proof.get("candidate_build_status") == "NOT BUILT"
         and proof.get("candidate_activation_status") == "NOT RUN"
         and proof.get("candidate_qualified") is False,
         "retain the real frozen, unbuilt, untested first-party C feature")
    rust_build = summary.get("rust_native_build_v18_actual_build")
    need(type(rust_build) is dict
         and rust_build.get("schema")
             == "rebar-candidate-current-overview-v67-actual-first-party-rust-v18-build"
         and rust_build.get("version") == 18
         and rust_build.get("family") == "rust"
         and rust_build.get("status") == "PASS"
         and rust_build.get("actual_build_status") == "PASS"
         and rust_build.get("reproducible_native_build_status") == "PASS"
         and rust_build.get("actual_compiler_process_count") == 28
         and rust_build.get("expected_actual_compiler_process_count") == 28
         and rust_build.get("archive_sha256_attested_by_receipt")
             == RUST_V18_BUILD_ARCHIVE[1]
         and rust_build.get("archive_bytes_attested_by_receipt")
             == RUST_V18_BUILD_ARCHIVE[2]
         and rust_build.get("archive_owner_inode_attested_by_receipt")
             == RUST_V18_BUILD_ARCHIVE[3]
         and rust_build.get("archive_opened_by_graph") is False
         and rust_build.get("archive_bytes_read_by_graph") == 0
         and rust_build.get("archive_inflations_by_graph") == 0
         and rust_build.get("archive_sha256_recomputed_by_graph") is False
         and rust_build.get("candidate_matching_status") == "NOT RUN"
         and rust_build.get("candidate_activation_status") == "NOT RUN"
         and rust_build.get("candidate_correctness") == "NOT MEASURED"
         and rust_build.get("candidate_qualified") is False,
         "preserve the actual Rust build without claiming Rust matching or opening its archive")
    return {
        "version": GRAPH_VERSION, "owner_count": 4,
        "authenticated_evidence_owner_lower_bound": 225,
        "authenticated_history_reference_lower_bound": 230,
        "actual_c_status": "FAIL", "actual_c_semantic_mismatch_count": 1230,
        "actual_c_verified_passing_case_count": 7325,
        "actual_rust_status": "FAIL", "actual_rust_semantic_mismatch_count": 1440,
        "actual_rust_verified_passing_case_count": 14853,
        "feature_status": "SOURCE FROZEN", "feature_build_status": "NOT BUILT",
        "feature_matching_status": "NOT RUN", "feature_activation_status": "NOT RUN",
        "rust_v17_authorization_status": "BLOCKED",
        "rust_v17_build_status": "NOT RUN",
        "rust_v18_source_status": "SOURCE FROZEN",
        "rust_v18_native_build_status": "PASS",
        "rust_v18_reproducible_build_status": "PASS",
        "rust_v18_actual_compiler_process_count": 28,
        "rust_v18_matching_status": "NOT RUN",
        "rust_v18_archive_opened": False,
        "qualified_candidate_count": 0, "holdout": "NOT OPENED",
        "runtime_non_delegation": "NOT ESTABLISHED",
    }


def validate_readiness(value: dict[str, Any]) -> None:
    gate = value.get("phase_gate")
    candidate = value.get("candidate_qualification_gate")
    supplement = value.get("actual_supplemental_two_reference")
    need(value.get("schema") == "rebar-cpython-re-p0-completeness-v4"
         and value.get("version") == 4
         and value.get("original_case_execution_denominator") == 31237
         and value.get("original_named_private_waiver_count") == 13
         and type(gate) is dict and gate.get("status") == "PASS"
         and gate.get("candidate_evaluation_authorized") is True
         and gate.get("native_build_authorized") is True
         and gate.get("final_holdout_authorized") is False
         and gate.get("performance_oracle_authorized") is False
         and type(candidate) is dict and candidate.get("status") == "BLOCKED"
         and candidate.get("qualified_candidate_count") == 0
         and candidate.get("runtime_no_delegation") == "NOT ESTABLISHED"
         and candidate.get("final_holdout_opened") is False
         and type(supplement) is dict and supplement.get("status") == "PASS"
         and supplement.get("actual_reference_worker_count") == 2
         and supplement.get("case_count_per_worker") == [8244, 8244]
         and supplement.get("failed_per_worker") == [0, 0]
         and supplement.get("case_denominator_included_in_original_31237") is False
         and value.get("holdout") == "NOT OPENED",
         "preserve exact V4 reference readiness without qualifying a candidate")


def validate_producer(value: dict[str, Any]) -> None:
    phase = value.get("phase_one")
    rows = value.get("families")
    boundary = value.get("verification_effects")
    need(value.get("schema") == "rebar-owned-six-family-original-p0-producer-v4-source-freeze"
         and value.get("version") == 4 and value.get("phase") == "CANDIDATES"
         and type(phase) is dict and phase.get("case_execution_denominator") == 31237
         and phase.get("named_private_waiver_count") == 13
         and phase.get("suite_count") == 13 and phase.get("supplemental_cases_added") is False
         and type(rows) is list
         and [row.get("family") for row in rows]
         == ["rust", "c", "zig", "cpp", "go", "fortran"]
         and type(boundary) is dict and boundary.get("actual_candidate_workers") == 0
         and boundary.get("actual_reference_workers") == 0
         and boundary.get("actual_source_builds") == 0
         and boundary.get("actual_native_activations") == 0
         and boundary.get("clock_samples") == 0
         and boundary.get("holdout") == "NOT OPENED",
         "bind the actual corrected six-family V4 producer without executing it")


def validate_receipt(value: dict[str, Any], family: str) -> None:
    mismatches, passes = (1230, 7325) if family == "c" else (1440, 14853)
    suffix = "v4" if family == "c" else "v10"
    need(value.get("schema")
         == "rebar-owned-repaired-" + family + "-original-campaign-" + suffix
         + "-durable-publication-receipt"
         and value.get("status") == "PASS"
         and value.get("publication_status") == "PASS"
         and value.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
         and value.get("candidate_status") == "FAIL"
         and value.get("family") == family
         and value.get("actual_candidate_workers") == 13
         and value.get("completed_suite_count") == 13
         and value.get("case_execution_denominator") == 31237
         and value.get("named_private_waiver_count") == 13
         and value.get("semantic_mismatch_count") == mismatches
         and value.get("verified_passing_case_count") == passes
         and value.get("infrastructure_failure_count") == 0
         and value.get("holdout") == "NOT OPENED"
         and value.get("performance") == "NOT MEASURED"
         and value.get("memory") == "NOT MEASURED"
         and value.get("winner_selected") is False,
         "authenticate a small genuine failed " + family + " receipt only")


def validate_rust_v18_build_receipt(value: dict[str, Any]) -> None:
    archive = value.get("archive_publication")
    directory = value.get("archive_directory_fsync")
    need(value.get("schema")
         == "rebar-phase2-owned-rust-buffer-shape-source-build-v18-durable-publication-receipt"
         and value.get("status") == "PASS"
         and value.get("build_status") == "PASS"
         and value.get("family") == "rust"
         and value.get("label") == "phase2-v18-rust-buffer-shape-pickle-lifetime"
         and value.get("source_sha256") == RUST_V18_SOURCE["source"][1]
         and value.get("protocol_sha256") == RUST_V18_SOURCE["protocol"][1]
         and value.get("contract_sha256") == RUST_V18_SOURCE["contract"][1]
         and value.get("current_graph_version") == 65
         and value.get("actual_compiler_process_count") == 28
         and value.get("expected_actual_compiler_process_count") == 28
         and value.get("archive_relative") == RUST_V18_BUILD_ARCHIVE[0]
         and value.get("archive_sha256") == RUST_V18_BUILD_ARCHIVE[1]
         and value.get("archive_bytes") == RUST_V18_BUILD_ARCHIVE[2]
         and value.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
         and value.get("candidate_matching") == "NOT RUN"
         and value.get("candidate_qualified") is False
         and value.get("candidate_workers_started") == 0
         and value.get("candidate_imports") == 0
         and value.get("candidate_processes_started") == 0
         and value.get("native_libraries_loaded") == 0
         and value.get("clock_samples") == 0
         and value.get("hidden_cases_read") == 0
         and value.get("holdout") == "NOT OPENED"
         and value.get("performance") == "NOT MEASURED"
         and value.get("memory") == "NOT MEASURED"
         and value.get("undefined_behavior") == "NOT MEASURED"
         and value.get("winner_selected") is False
         and type(archive) is dict
         and archive.get("bytes") == RUST_V18_BUILD_ARCHIVE[2]
         and archive.get("device") == DEVICE
         and archive.get("inode") == RUST_V18_BUILD_ARCHIVE[3]
         and archive.get("sha256") == RUST_V18_BUILD_ARCHIVE[1]
         and archive.get("path") == str(ROOT / RUST_V18_BUILD_ARCHIVE[0])
         and archive.get("exclusive_creation") is True
         and archive.get("file_fsync_completed") is True
         and archive.get("same_inode_readback_verified") is True
         and type(directory) is dict and directory.get("completed") is True
         and directory.get("device") == DEVICE,
         "authenticate the genuine Rust V18 build from its small receipt only")


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None) -> dict[str, Any]:
    verify_runtime()
    read_owner(dynamic_owner(SELF, checked_digest(source_pin, "V16 source")))
    read_owner(dynamic_owner(PROTOCOL, checked_digest(protocol_pin, "V16 protocol")))
    read_owner(GOAL)
    raw_groups: dict[str, dict[str, bytes]] = {}
    for group_name, group in (
        ("phase_one", P0_V4), ("producer", PRODUCER_V4),
        ("feature", FEATURE), ("graph", GRAPH),
        ("rust_v18_source", RUST_V18_SOURCE), ("kernel", KERNEL),
    ):
        raw_groups[group_name] = {
            role: read_owner(owner) for role, owner in group.items()
        }
    original = read_owner(ORIGINAL_C)
    adapter = read_owner(ADAPTER)
    readiness = document(raw_groups["phase_one"]["contract"], "corrected P0 V4")
    validate_readiness(readiness)
    producer = document(raw_groups["producer"]["contract"], "corrected producer V4")
    validate_producer(producer)
    summary = document(raw_groups["graph"]["summary"], "pushed overview summary")
    inputs = document(raw_groups["graph"]["inputs"], "pushed overview inputs")
    observation = graph_observation(summary, inputs)
    svg = raw_groups["graph"]["svg"]
    need(b"<svg" in svg and b"</svg>" in svg,
         "require the exact committed complete current overview chart")
    feature_contract = document(raw_groups["feature"]["contract"], "owned C feature")
    feature = load_source(FEATURE["source"],
                          "_rebar_exact_c_subject_buffer_v16_feature")
    need(getattr(feature, "SCHEMA", None)
         == "rebar-phase2-owned-c-subject-buffer-ownership-v1"
         and getattr(feature, "VARIANT_SHA256", None) == FEATURE["variant"][1]
         and getattr(feature, "VARIANT_BYTES", None) == FEATURE["variant"][2]
         and feature.contract_document(FEATURE["source"][1], FEATURE["protocol"][1])
         == feature_contract,
         "independently reproduce the complete exact C feature machine contract")
    previous = feature.reconstructed_c15(original)
    derived = feature.repaired_c_variant(previous)
    need(derived == raw_groups["feature"]["variant"]
         and digest(derived) == FEATURE["variant"][1]
         and len(derived) == FEATURE["variant"][2]
         and digest(adapter) == ADAPTER[1],
         "derive the entire owned C compiler input from canonical first-party bytes")
    c = document(read_owner(C_RECEIPT), "small actual C failure receipt")
    rust = document(read_owner(RUST_RECEIPT), "small actual Rust failure receipt")
    rust_build = document(read_owner(RUST_V18_BUILD_RECEIPT),
                          "small actual Rust V18 build receipt")
    validate_receipt(c, "c")
    validate_receipt(rust, "rust")
    validate_rust_v18_build_receipt(rust_build)
    graph_rust_build = summary.get("rust_native_build_v18_actual_build")
    need(type(graph_rust_build) is dict
         and graph_rust_build.get("complete_durable_publication_receipt") == rust_build,
         "bind the complete pushed Rust build proof to its genuine small receipt")
    need(feature_contract.get("corrected_p0_v4_readiness", {}).get("owners")
         == {key: public_pin(value) for key, value in P0_V4.items()}
         and feature_contract.get("corrected_original_v4_producer")
         == {key: public_pin(value) for key, value in PRODUCER_V4.items()}
         and feature_contract.get("historical_c_observation", {})
             .get("historical_c_semantic_mismatch_count") == 1230
         and feature_contract.get("current_rust_v10_history", {})
             .get("semantic_mismatch_count") == 1440,
         "bind the exact corrected oracle, producer, and real loss provenance")
    need(not any(name == "candidates" or name.startswith("candidates.")
                 for name in sys.modules),
         "source verification must not import any regular-expression candidate")
    context = {
        "overview": observation, "readiness": readiness,
        "producer": producer, "feature_contract": feature_contract,
        "historical_c_receipt": c, "current_rust_receipt": rust,
        "actual_rust_v18_build_receipt": rust_build, "derived": derived,
    }
    expected = contract_document(source_pin, protocol_pin, observation)
    if contract_pin is not None:
        raw = read_owner(dynamic_owner(CONTRACT, checked_digest(contract_pin, "V16 contract")))
        need(document(raw, "exact V16 C subject-buffer build freeze") == expected,
             "reject a changed or incomplete exact C V16 machine contract")
    return context


def future_build_policy() -> dict[str, Any]:
    return {
        "explicit_build_required": True,
        "caller_pins_original_c_and_adapter": True,
        "caller_pins_complete_variant": True,
        "private_root_prefix": "rebar-phase2-native-build-v8-c-",
        "phase_names": list(PHASES), "phase_count": 2,
        "peer_phases_precreated_before_first_snapshot": True,
        "source_owner_count_per_phase": 2,
        "variant_source_sha256": FEATURE["variant"][1],
        "variant_source_bytes": FEATURE["variant"][2],
        "adapter_source_sha256": ADAPTER[1],
        "source_apply_count_per_phase": 1,
        "total_source_apply_count": 2,
        "process_names_per_phase": list(PROCESS_NAMES),
        "compiler_process_count_per_phase": 7,
        "total_compiler_process_count": 14,
        "source_file_mode": "0600", "directory_mode": "0700",
        "source_creation": "O_CREAT | O_EXCL | O_NOFOLLOW",
        "source_file_fsync": True,
        "native_outputs": "TWO INDEPENDENT BYTE-IDENTICAL OWNED C ELF FILES",
        "installed_native_read": "FORBIDDEN",
        "installed_native_activation": "FORBIDDEN",
        "canonical_source_mutation": "FORBIDDEN",
        "canonical_adapter_mutation": "FORBIDDEN",
        "candidate_or_reference_execution": "FORBIDDEN",
        "external_regex_engine": "FORBIDDEN",
        "stdlib_regex_engine": "FORBIDDEN",
        "cross_candidate_engine": "FORBIDDEN",
        "fallback": "FORBIDDEN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "build_pass_means": "COMPILATION AND DURABLE PUBLICATION ONLY",
    }


def contract_document(source_pin: str, protocol_pin: str,
                      overview: dict[str, Any]) -> dict[str, Any]:
    checked_digest(source_pin, "V16 source")
    checked_digest(protocol_pin, "V16 protocol")
    need(overview.get("version") == GRAPH_VERSION
         and overview.get("owner_count") == 4,
         "freeze only the actual committed four-owner current graph")
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION, "family": FAMILY,
        "phase": "SOURCE FREEZE; FIRST-PARTY C SUBJECT-BUFFER BUILD NOT RUN",
        "source": {"path": SELF, "sha256": source_pin},
        "protocol": {"path": PROTOCOL, "sha256": protocol_pin},
        "goal": owner_pin(GOAL),
        "pinned_cpython": {
            "implementation": "CPython", "version": "3.14.6",
            "executable": PYTHON, "sha256": PYTHON_SHA256,
            "isolated": True, "bytecode": False,
        },
        "corrected_p0_v4": {
            "owners": owner_group(P0_V4),
            "python_reference_readiness": "PASS",
            "candidate_qualification": "BLOCKED",
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "named_private_waiver_count": 13,
            "supplemental_reference_worker_count": 2,
            "supplemental_cases_per_reference": 8244,
            "supplemental_added_to_original_denominator": False,
        },
        "corrected_original_producer_v4": owner_group(PRODUCER_V4),
        "published_overview": {
            "version": GRAPH_VERSION, "owners": owner_group(GRAPH),
            "owner_count": 4,
            "authenticated_evidence_owner_lower_bound":
                overview["authenticated_evidence_owner_lower_bound"],
            "authenticated_history_reference_lower_bound":
                overview["authenticated_history_reference_lower_bound"],
            "lower_bounds_are_not_a_repository_census": True,
            "qualified_candidate_count": 0,
        },
        "owned_first_party_subject_buffer_feature": {
            "owners": owner_group(FEATURE),
            "independent_source_owner_count": 4,
            "complete_native_variant_sha256": FEATURE["variant"][1],
            "complete_native_variant_bytes": FEATURE["variant"][2],
            "derived_from_canonical_owned_c": True,
            "candidate_build": "NOT RUN",
            "candidate_activation": "NOT RUN",
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
        },
        "canonical_c_source_owners": {
            "combined_native_source": owner_pin(ORIGINAL_C),
            "python_adapter": owner_pin(ADAPTER),
            "original_source_modified": False,
            "original_adapter_modified": False,
            "installed_native_opened": False,
            "installed_native_activated": False,
        },
        "frozen_first_party_build_kernel": owner_group(KERNEL),
        "actual_previous_c_result": {
            "receipt": owner_pin(C_RECEIPT), "candidate_status": "FAIL",
            "semantic_mismatch_count": 1230,
            "explicitly_verified_passing_case_count": 7325,
            "case_execution_denominator": 31237,
            "actual_candidate_workers": 13, "completed_suite_count": 13,
            "archive_opened": False,
            "receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
        },
        "actual_current_rust_result": {
            "receipt": owner_pin(RUST_RECEIPT), "candidate_status": "FAIL",
            "semantic_mismatch_count": 1440,
            "explicitly_verified_passing_case_count": 14853,
            "case_execution_denominator": 31237,
            "actual_candidate_workers": 13, "completed_suite_count": 13,
            "archive_opened": False,
            "receipt_pass_means": "DURABLE FAILURE PUBLICATION ONLY",
            "rust_parser_compiler_executor_or_engine_reused": False,
        },
        "actual_rust_v18_native_build": {
            "frozen_first_party_source_owners": owner_group(RUST_V18_SOURCE),
            "receipt": owner_pin(RUST_V18_BUILD_RECEIPT),
            "build_status": "PASS",
            "reproducible_build_status": "PASS",
            "actual_compiler_process_count": 28,
            "expected_compiler_process_count": 28,
            "candidate_matching": "NOT RUN",
            "candidate_qualified": False,
            "candidate_workers_started": 0,
            "archive_metadata_attested_by_small_receipt": {
                "path": RUST_V18_BUILD_ARCHIVE[0],
                "sha256": RUST_V18_BUILD_ARCHIVE[1],
                "bytes": RUST_V18_BUILD_ARCHIVE[2],
                "device": DEVICE,
                "inode": RUST_V18_BUILD_ARCHIVE[3],
                "archive_opened": False,
                "archive_bytes_read": 0,
                "archive_inflations": 0,
                "archive_sha256_recomputed": False,
            },
            "publication_pass_means": "DURABLE BUILD PUBLICATION ONLY",
            "rust_v17_authorization": "BLOCKED",
            "rust_v17_native_build": "NOT RUN",
        },
        "original_suite_count": 13,
        "original_suites": [
            {"id": name, "case_execution_count": count}
            for name, count in SUITES
        ],
        "future_build_policy": future_build_policy(),
        "future_evidence": {
            "directory": EVIDENCE,
            "archive_prefix": "native-source-build-v16-c-",
            "archive_suffix": ".json.gz",
            "failure_suffix": "-failures",
            "receipt_suffix": "-publication-receipt.json",
            "owner_mode": "0600", "exclusive_creation": True,
            "archive_and_directory_fsync": True,
            "receipt_and_directory_fsync": True,
            "written_during_source_freeze": False,
            "build_pass_does_not_qualify_a_candidate": True,
        },
        "source_only_effects": effects(),
    }


class SourceWall:
    """Physically deny file, process, archive, native, network, and clock effects."""

    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.blocked = 0
        self.modules: frozenset[str] = frozenset()

    def install(self, owner: Any, name: str) -> None:
        original = getattr(owner, name, None)
        if original is None:
            return

        def denied(*_args: Any, **_kwargs: Any) -> Any:
            self.blocked += 1
            raise BuildError("source-only side effect physically blocked: " + name)

        self.saved.append((owner, name, original))
        setattr(owner, name, denied)

    def __enter__(self) -> SourceWall:
        self.modules = frozenset(sys.modules)
        for owner, names in (
            (builtins, ("open", "__import__")),
            (io, ("open",)), (_io, ("open", "open_code")),
            (os, ("open", "read", "write", "stat", "lstat", "listdir",
                  "scandir", "mkdir", "makedirs", "unlink", "remove",
                  "replace", "rename", "system", "fork", "posix_spawn",
                  "posix_spawnp", "pipe", "fsync", "execv", "execve")),
            (Path, ("open", "read_bytes", "read_text", "write_bytes",
                    "write_text", "stat", "lstat", "resolve", "mkdir",
                    "unlink", "rename", "replace", "iterdir")),
            (subprocess, ("Popen", "run", "call", "check_call", "check_output")),
            (socket, ("socket", "create_connection")),
            (tempfile, ("mkdtemp", "mkstemp", "NamedTemporaryFile")),
            (importlib, ("import_module",)),
            (_imp, ("create_dynamic", "exec_dynamic")),
            (_thread, ("start_new_thread",)),
            (threading.Thread, ("start",)),
            (gzip, ("open", "decompress")),
            (zlib, ("decompress", "decompressobj")),
            (signal, ("signal",)),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "process_time_ns", "thread_time", "thread_time_ns", "sleep")),
        ):
            for name in names:
                self.install(owner, name)
        return self

    def __exit__(self, _kind: Any, _value: Any, _traceback: Any) -> None:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)
        need(frozenset(sys.modules) == self.modules,
             "reject any import during physically blocked synthetic verification")


def checked_label(value: Any) -> str:
    need(type(value) is str and 0 < len(value) <= LABEL_LIMIT
         and all(char.isascii() and (char.isalnum() or char in "-_")
                 for char in value),
         "require one bounded safe exclusive C build label")
    return value


def evidence_names(label: str, *, failure: bool) -> tuple[str, str]:
    need(type(failure) is bool, "separately preserve a passing or failing build")
    stem = "native-source-build-v16-c-" + checked_label(label)
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def synthetic_schedule(phases: Any, processes: Any) -> dict[str, Any]:
    need(type(phases) is list and len(phases) == 2
         and type(processes) is list and len(processes) == 14,
         "require exactly two future phases and fourteen real compiler processes")
    source_owners: set[tuple[int, int]] = set()
    for index, phase in enumerate(phases):
        need(type(phase) is dict and phase.get("name") == PHASES[index]
             and phase.get("source_sha256") == FEATURE["variant"][1]
             and phase.get("source_bytes") == FEATURE["variant"][2]
             and phase.get("adapter_sha256") == ADAPTER[1]
             and phase.get("source_apply_count") == 1
             and type(phase.get("source_device")) is int
             and type(phase.get("source_inode")) is int
             and (phase["source_device"], phase["source_inode"]) not in source_owners,
             "reject a stale, repeated, external, or missing owned variant phase")
        source_owners.add((phase["source_device"], phase["source_inode"]))
    pids: set[int] = set()
    for index, process in enumerate(processes):
        need(type(process) is dict
             and process.get("phase") == PHASES[index // 7]
             and process.get("name") == PROCESS_NAMES[index % 7]
             and type(process.get("pid")) is int and process["pid"] > 0
             and process["pid"] not in pids
             and process.get("exit_status") == 0,
             "reject omitted, reordered, fake, external, or duplicate processes")
        pids.add(process["pid"])
    return {"phase_count": 2, "unique_process_count": 14,
            "independent_variant_source_owner_count": 2,
            "source_apply_count": 2}


def self_test(context: dict[str, Any], source_pin: str,
              protocol_pin: str) -> dict[str, Any]:
    phases = [{"name": phase, "source_sha256": FEATURE["variant"][1],
               "source_bytes": FEATURE["variant"][2],
               "adapter_sha256": ADAPTER[1], "source_apply_count": 1,
               "source_device": 17, "source_inode": index + 101}
              for index, phase in enumerate(PHASES)]
    processes = [{"phase": PHASES[index // 7],
                  "name": PROCESS_NAMES[index % 7],
                  "pid": index + 101, "exit_status": 0}
                 for index in range(14)]
    accepted = 0
    rejected = 0
    with SourceWall() as wall:

        def reject(operation: Any, label: str) -> None:
            nonlocal rejected
            try:
                operation()
            except (BuildError, OSError, TypeError, ValueError, KeyError):
                rejected += 1
                return
            raise BuildError("accepted hostile V16 source-only control: " + label)

        need(synthetic_schedule(phases, processes)["unique_process_count"] == 14,
             "authenticate the complete synthetic two-phase compiler schedule")
        accepted += 1
        rendered = contract_document(source_pin, protocol_pin, context["overview"])
        need(rendered["future_build_policy"]["total_compiler_process_count"] == 14
             and rendered["source_only_effects"] == effects(),
             "authenticate an entirely unexecuted source-only build contract")
        accepted += 1
        for index in range(2):
            for key, replacement in (
                ("name", "external"), ("source_sha256", "0" * 64),
                ("source_bytes", FEATURE["variant"][2] + 1),
                ("adapter_sha256", "0" * 64),
                ("source_apply_count", 0), ("source_apply_count", 2),
            ):
                bad = copy.deepcopy(phases)
                bad[index][key] = replacement
                reject(lambda value=bad: synthetic_schedule(value, processes), key)
        repeated = copy.deepcopy(phases)
        repeated[1]["source_inode"] = repeated[0]["source_inode"]
        reject(lambda: synthetic_schedule(repeated, processes), "reused source owner")
        for index in range(14):
            for key, replacement in (
                ("phase", "foreign"), ("name", "build_external_regex"),
                ("pid", 0), ("exit_status", 1),
            ):
                bad = copy.deepcopy(processes)
                bad[index][key] = replacement
                reject(lambda value=bad: synthetic_schedule(phases, value), key)
        duplicate = copy.deepcopy(processes)
        duplicate[1]["pid"] = duplicate[0]["pid"]
        reject(lambda: synthetic_schedule(phases, duplicate), "duplicate PID")
        reject(lambda: synthetic_schedule(phases[:-1], processes), "missing phase")
        reject(lambda: synthetic_schedule(phases, processes[:-1]), "missing compiler")
        for value in ("", "../escape", "/tmp/private", "a/../b", "a//b",
                      "./owner", "oracle/phase3/holdout.json", "native.so",
                      "history.json.gz", "benchmark/results.json", "z" * 513):
            reject(lambda item=value: checked_relative(item), "unsafe owner")
        for value in ("", "0" * 63, "0" * 65, "X" * 64):
            reject(lambda item=value: checked_digest(item, "hostile"), "false SHA-256")
        for value in ("", "../escape", "wrong label", "x" * (LABEL_LIMIT + 1)):
            reject(lambda item=value: checked_label(item), "unsafe evidence label")
        for failure in (False, True):
            archive, receipt = evidence_names("synthetic", failure=failure)
            need(archive.startswith("native-source-build-v16-c-")
                 and archive.endswith(".json.gz")
                 and receipt.endswith("-publication-receipt.json"),
                 "retain separate fresh future passing and failing owners")
            accepted += 1
        probes = (
            lambda: builtins.open("/tmp/forbidden"),
            lambda: io.open("/tmp/forbidden"),
            lambda: _io.open("/tmp/forbidden"),
            lambda: os.open("/tmp/forbidden", os.O_RDONLY),
            lambda: os.read(0, 1),
            lambda: os.write(1, b"x"),
            lambda: os.stat("/tmp"),
            lambda: os.lstat("/tmp"),
            lambda: os.listdir("/tmp"),
            lambda: os.mkdir("/tmp/forbidden"),
            lambda: os.unlink("/tmp/forbidden"),
            lambda: os.replace("/tmp/a", "/tmp/b"),
            lambda: Path("/tmp/private").read_bytes(),
            lambda: Path("/tmp/private").write_bytes(b"x"),
            lambda: subprocess.run(("true",)),
            lambda: subprocess.Popen(("true",)),
            lambda: socket.socket(),
            lambda: tempfile.mkdtemp(),
            lambda: tempfile.mkstemp(),
            lambda: importlib.import_module("candidates.vm_candidate"),
            lambda: builtins.__import__("ctypes"),
            lambda: _thread.start_new_thread(lambda: None, ()),
            lambda: threading.Thread().start(),
            lambda: gzip.open("/tmp/archive.gz", "rb"),
            lambda: gzip.decompress(b"forbidden"),
            lambda: zlib.decompress(b"forbidden"),
            lambda: zlib.decompressobj(),
            lambda: time.time(),
            lambda: time.monotonic(),
            lambda: time.perf_counter(),
            lambda: time.perf_counter_ns(),
            lambda: time.sleep(0),
        )
        for index, probe in enumerate(probes):
            reject(probe, "physically forbidden effect " + str(index))
        need(wall.blocked == len(probes) and rejected >= 100,
             "physically reject every external source-only operation")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": VERSION, "status": "PASS", "family": FAMILY,
        "accepted_synthetic_controls": accepted,
        "rejected_hostile_controls": rejected,
        "physically_blocked_effect_controls": len(probes),
        "published_overview_version": GRAPH_VERSION,
        "published_overview_owner_count": 4,
        "authenticated_evidence_owner_lower_bound":
            context["overview"]["authenticated_evidence_owner_lower_bound"],
        "authenticated_history_reference_lower_bound":
            context["overview"]["authenticated_history_reference_lower_bound"],
        "historical_c_semantic_mismatch_count": 1230,
        "historical_c_verified_passing_case_count": 7325,
        "current_rust_semantic_mismatch_count": 1440,
        "current_rust_verified_passing_case_count": 14853,
        "actual_rust_v18_native_build_status": "PASS",
        "actual_rust_v18_compiler_process_count": 28,
        "actual_rust_v18_archive_opened": False,
        "historical_rust_v17_authorization_status": "BLOCKED",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13, "named_private_waiver_count": 13,
        "supplemental_reference_cases_per_worker": 8244,
        "future_phase_count": 2,
        "future_compiler_process_count_per_phase": 7,
        "future_total_compiler_process_count": 14,
        "source_only_effects": effects(),
    }


def copy_variant_snapshot(workdir: str, family: str, phase: str,
                          sources: dict[str, bytes]) -> dict[str, dict[str, Any]]:
    need(type(_ACTIVE) is dict, "require an explicit authorised V16 native build")
    assert _ACTIVE is not None
    v8 = _ACTIVE["v8"]
    kernel = _ACTIVE["kernel"]
    derived = _ACTIVE["derived"]
    need(family == FAMILY and phase in PHASES and type(sources) is dict
         and set(sources) == {ORIGINAL_C[0], ADAPTER[0]}
         and digest(sources[ORIGINAL_C[0]]) == ORIGINAL_C[1]
         and len(sources[ORIGINAL_C[0]]) == ORIGINAL_C[2]
         and digest(sources[ADAPTER[0]]) == ADAPTER[1]
         and len(sources[ADAPTER[0]]) == ADAPTER[2]
         and type(derived) is bytes and digest(derived) == FEATURE["variant"][1]
         and len(derived) == FEATURE["variant"][2]
         and (workdir, phase) not in _APPLIED,
         "reject a repeated, substituted, borrowed, or unowned C snapshot")
    identities: set[tuple[int, int]] = set()
    for peer in PHASES:
        paths = v8.phase_paths(workdir, family, peer)
        for path in (paths["base"], paths["source"], paths["source"] / "candidates"):
            observed = os.lstat(path)
            need(stat.S_ISDIR(observed.st_mode)
                 and stat.S_IMODE(observed.st_mode) == 0o700
                 and observed.st_uid == os.geteuid(),
                 "precreate two independently owned private source phases")
        identity = os.lstat(paths["base"])
        pair = identity.st_dev, identity.st_ino
        need(pair not in identities, "reject aliased private source-build phases")
        identities.add(pair)
    paths = v8.phase_paths(workdir, family, phase)
    adapted = kernel.write_fresh(paths["source"] / ADAPTER[0],
                                 sources[ADAPTER[0]], synchronize=True)
    native = kernel.write_fresh(paths["source"] / ORIGINAL_C[0],
                                derived, synchronize=True)
    for owner in (adapted, native):
        owner["path"] = v8.sanitized(owner["path"], workdir, family)
    need(native.get("sha256") == FEATURE["variant"][1]
         and native.get("bytes") == FEATURE["variant"][2]
         and native.get("file_fsync_completed") is True
         and adapted.get("sha256") == ADAPTER[1]
         and adapted.get("file_fsync_completed") is True,
         "bind each compiler to the exact exclusive complete owned variant")
    native["source_overlay"] = {
        "schema": SCHEMA + "-private-variant-snapshot",
        "status": "PASS", "family": FAMILY, "phase": phase,
        "source_apply_count": 1,
        "derived_source_sha256": FEATURE["variant"][1],
        "derived_source_bytes": FEATURE["variant"][2],
        "original_source_modified": False,
        "original_adapter_modified": False,
        "installed_native_read": False, "installed_native_activated": False,
        "candidate_correctness": "NOT MEASURED",
    }
    _APPLIED.add((workdir, phase))
    read_owner(ORIGINAL_C)
    read_owner(ADAPTER)
    return {ORIGINAL_C[0]: native, ADAPTER[0]: adapted}


def verify_reproducibility(v8: types.ModuleType, v7: types.ModuleType,
                           workdir: str, phases: list[dict[str, Any]],
                           steps: list[dict[str, Any]]) -> dict[str, Any]:
    need(type(phases) is list and len(phases) == 2
         and [phase.get("name") for phase in phases] == list(PHASES)
         and type(steps) is list and len(steps) == 14,
         "require exactly two complete genuine first-party C build phases")
    source_ids: set[tuple[int, int]] = set()
    outputs: list[dict[str, Any]] = []
    synthetic_phases: list[dict[str, Any]] = []
    for phase in phases:
        owners = phase.get("fresh_source_owners")
        need(type(owners) is dict and set(owners) == {ORIGINAL_C[0], ADAPTER[0]},
             "retain both complete independent private source owners")
        variant = owners[ORIGINAL_C[0]]
        adapter = owners[ADAPTER[0]]
        for owner, expected in ((variant, FEATURE["variant"]), (adapter, ADAPTER)):
            need(type(owner) is dict and owner.get("sha256") == expected[1]
                 and owner.get("bytes") == expected[2]
                 and type(owner.get("device")) is int
                 and type(owner.get("inode")) is int
                 and (owner["device"], owner["inode"]) not in source_ids,
                 "reject reused, fabricated, or cross-family compiler inputs")
            source_ids.add((owner["device"], owner["inode"]))
        overlay = variant.get("source_overlay")
        need(type(overlay) is dict and overlay.get("status") == "PASS"
             and overlay.get("phase") == phase["name"]
             and overlay.get("source_apply_count") == 1
             and overlay.get("derived_source_sha256") == FEATURE["variant"][1],
             "require exactly one real complete V16 subject-buffer source snapshot")
        output = phase.get("native_outputs", {}).get("extension")
        need(type(output) is dict and output.get("file_name") == v8.EXTENSION_NAME,
             "require two genuine independently owned native C extensions")
        outputs.append(output)
        synthetic_phases.append({
            "name": phase["name"], "source_sha256": variant["sha256"],
            "source_bytes": variant["bytes"], "adapter_sha256": adapter["sha256"],
            "source_apply_count": 1, "source_device": variant["device"],
            "source_inode": variant["inode"],
        })
    synthetic_steps = [
        {"phase": PHASES[index // 7], "name": step.get("name"),
         "pid": step.get("pid"), "exit_status": step.get("exit_status")}
        for index, step in enumerate(steps)
    ]
    schedule = synthetic_schedule(synthetic_phases, synthetic_steps)
    left, right = outputs
    need(left.get("sha256") == right.get("sha256")
         and left.get("size_bytes") == right.get("size_bytes")
         and left.get("path") != right.get("path")
         and (left.get("device"), left.get("inode"))
         != (right.get("device"), right.get("inode"))
         and left.get("audit") == right.get("audit"),
         "require distinct complete byte-identical first-party C native outputs")
    raw_a = v8._RAW_PHASE_ELF.get((workdir, PHASES[0]))
    raw_b = v8._RAW_PHASE_ELF.get((workdir, PHASES[1]))
    need(type(raw_a) is bytes and type(raw_b) is bytes and raw_a == raw_b
         and digest(raw_a) == left.get("sha256")
         and digest(raw_b) == right.get("sha256"),
         "compare only genuine complete authenticated fresh native ELF bytes")
    comparison = v7.compare_owned_elf64(raw_a, raw_b)
    need(type(comparison) is dict and comparison.get("byte_identical") is True,
         "independently prove identical private native builds")
    read_owner(ORIGINAL_C)
    read_owner(ADAPTER)
    return {
        "status": "PASS", **schedule,
        "independent_source_owner_count": len(source_ids),
        "variant_source_sha256": FEATURE["variant"][1],
        "variant_source_bytes": FEATURE["variant"][2],
        "original_source_modified": False,
        "original_adapter_modified": False,
        "installed_native_read": False,
        "installed_native_activated": False,
        "byte_identical": True,
        "raw_elf_comparison": comparison,
        "native_outputs": {"extension": {
            "file_name": v8.EXTENSION_NAME,
            "sha256": left["sha256"], "size_bytes": left["size_bytes"],
            "independent_phase_owner_count": 2, "audit": left["audit"],
        }},
        "native_libraries_loaded": 0, "candidate_workers_started": 0,
    }


def publish_report(kernel: types.ModuleType, report: dict[str, Any],
                   label: str) -> dict[str, Any]:
    need(type(report) is dict and report.get("status") in {"PASS", "FAIL"}
         and report.get("family") == FAMILY
         and report.get("label") == checked_label(label),
         "publish only one genuine complete independently authorised build")
    archive_name, receipt_name = evidence_names(
        label, failure=report["status"] == "FAIL",
    )
    directory = ROOT / EVIDENCE
    kernel.mkdir_private(directory)
    plain = canonical(report)
    need(0 < len(plain) <= REPORT_LIMIT, "bound the complete actual build report")
    compressed = gzip.compress(plain, compresslevel=9, mtime=0)
    need(0 < len(compressed) <= ARCHIVE_LIMIT,
         "bound the deterministic genuine build archive")
    archive = kernel.write_fresh(directory / archive_name, compressed,
                                 synchronize=True)
    archive_sync = kernel.fsync_directory(directory)
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "version": VERSION, "status": "PASS",
        "publication_pass_means": "DURABLE BUILD PUBLICATION ONLY",
        "build_status": report["status"], "family": FAMILY, "label": label,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "contract_sha256": report["contract_sha256"],
        "archive_relative": EVIDENCE + "/" + archive_name,
        "archive_sha256": archive["sha256"],
        "archive_bytes": archive["bytes"],
        "archive_publication": archive,
        "archive_directory_fsync": archive_sync,
        "uncompressed_sha256": digest(plain),
        "uncompressed_bytes": len(plain),
        "published_overview_version": GRAPH_VERSION,
        "published_overview_sha256": GRAPH["summary"][1],
        "variant_source_sha256": FEATURE["variant"][1],
        "variant_source_bytes": FEATURE["variant"][2],
        "original_source_sha256": ORIGINAL_C[1],
        "adapter_source_sha256": ADAPTER[1],
        "expected_source_apply_count": 2,
        "actual_source_apply_count": report.get("source_apply_count", 0),
        "expected_compiler_process_count": 14,
        "actual_compiler_process_count":
            report.get("actual_compiler_process_count", 0),
        "historical_c_candidate_status": "FAIL",
        "historical_c_semantic_mismatch_count": 1230,
        "historical_c_verified_passing_case_count": 7325,
        "current_rust_candidate_status": "FAIL",
        "current_rust_semantic_mismatch_count": 1440,
        "current_rust_verified_passing_case_count": 14853,
        "historical_archives_opened": 0,
        "candidate_correctness": "NOT MEASURED",
        "candidate_imports": 0, "candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "installed_native_read": False,
        "installed_native_activated": False,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "qualified_candidate_count": 0, "winner_selected": False,
        "receipt_self_publication": "NOT CLAIMED",
    }
    receipt_raw = canonical(receipt)
    need(len(receipt_raw) <= OWNER_LIMIT, "bound an exact independent build receipt")
    published = kernel.write_fresh(directory / receipt_name, receipt_raw,
                                   synchronize=True)
    receipt_sync = kernel.fsync_directory(directory)
    return {
        "schema": SCHEMA + "-published-build", "version": VERSION,
        "status": report["status"], "family": FAMILY, "label": label,
        "archive_relative": EVIDENCE + "/" + archive_name,
        "archive_sha256": archive["sha256"],
        "receipt_relative": EVIDENCE + "/" + receipt_name,
        "receipt_sha256": published["sha256"],
        "receipt_directory_fsync": receipt_sync,
        "failure_preserved": report["status"] == "FAIL",
        "candidate_correctness": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def run_build(options: argparse.Namespace) -> dict[str, Any]:
    global _ACTIVE
    need(options.build is True and _ACTIVE is None and not _APPLIED,
         "require exactly one explicit nonreentrant V16 native build")
    context = verify_context(options.source_sha256, options.protocol_sha256,
                             options.contract_sha256)
    expected = {ORIGINAL_C[0] + "=" + ORIGINAL_C[1],
                ADAPTER[0] + "=" + ADAPTER[1]}
    need(options.family == FAMILY
         and type(options.owned_source_sha256) is list
         and len(options.owned_source_sha256) == 2
         and set(options.owned_source_sha256) == expected
         and options.variant_source_sha256 == FEATURE["variant"][1],
         "caller-pin both unchanged C originals and the complete V16 C variant")
    label = checked_label(options.label)
    v8 = load_source(KERNEL["v8"], "_rebar_exact_c_subject_buffer_v16_v8")
    v7 = load_source(KERNEL["v7"], "_rebar_exact_c_subject_buffer_v16_v7")
    need(v8.SCHEMA == "rebar-phase2-owned-native-source-build-v8"
         and v7.SCHEMA == "rebar-phase2-owned-native-source-build-v7"
         and v8.FAMILY == FAMILY and tuple(v8.PHASES) == PHASES
         and tuple(v8.PROCESS_NAMES) == PROCESS_NAMES
         and v8.ORIGINAL_PATH == ORIGINAL_C[0]
         and v8.ORIGINAL_SHA256 == ORIGINAL_C[1]
         and v8.ADAPTER_PATH == ADAPTER[0]
         and v8.ADAPTER_SHA256 == ADAPTER[1]
         and v7.SOURCE_OWNERS[FAMILY][ORIGINAL_C[0]]
             == (ORIGINAL_C[1], ORIGINAL_C[2])
         and v7.SOURCE_OWNERS[FAMILY][ADAPTER[0]]
             == (ADAPTER[1], ADAPTER[2]),
         "load only the exact independently authenticated first-party C kernels")
    kernel = v7.load_frozen_v4()
    need(kernel.SCHEMA == "rebar-phase2-owned-native-source-build-v4"
         and kernel.__name__ == "_rebar_phase2_exact_frozen_v4_source_kernel",
         "derive only the exact isolated immutable V4 first-party compiler")
    kernel.audit_native_source(context["derived"], family=FAMILY,
                               location=ORIGINAL_C[0])
    for failed in (False, True):
        for name in evidence_names(label, failure=failed):
            kernel.require_fresh_absent(ROOT / EVIDENCE / name)
    original_hook = getattr(kernel, "copy_snapshot", None)
    workdir: str | None = None
    steps: list[dict[str, Any]] = []
    phases: list[dict[str, Any]] = []
    reproduction: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    _ACTIVE = {"v8": v8, "v7": v7, "kernel": kernel,
               "derived": context["derived"]}

    def captured(failure: BaseException) -> dict[str, Any]:
        return {"type": type(failure).__qualname__,
                "message": str(failure)[:8192],
                "traceback": traceback.format_exception(
                    type(failure), failure, failure.__traceback__,
                )}

    try:
        v8.install_v8_build_kernel(v7, kernel)
        kernel.copy_snapshot = copy_variant_snapshot
        workdir = tempfile.mkdtemp(prefix=v8.WORK_PREFIX + FAMILY + "-", dir="/tmp")
        v8.checked_workdir(workdir, FAMILY)
        v8.prepare_private_phases(kernel, workdir)
        sources = {ORIGINAL_C[0]: read_owner(ORIGINAL_C),
                   ADAPTER[0]: read_owner(ADAPTER)}
        for phase in PHASES:
            completed = kernel.exact_build_phase(workdir, FAMILY, phase,
                                                 sources, steps)
            completed["native_forensics"] = v8.record_native_forensics(
                v7, kernel, workdir, phase, completed, steps,
            )
            phases.append(completed)
        reproduction = verify_reproducibility(v8, v7, workdir, phases, steps)
        need(reproduction.get("unique_process_count") == 14
             and reproduction.get("source_apply_count") == 2,
             "require exactly fourteen genuine processes and two source snapshots")
    except BaseException as failure:
        error = captured(failure)
    finally:
        restore_errors: list[dict[str, Any]] = []
        for owner in (ORIGINAL_C, ADAPTER):
            try:
                read_owner(owner)
            except BaseException as failure:
                restore_errors.append(captured(failure))
        kernel.copy_snapshot = original_hook
        _ACTIVE = None
        if restore_errors:
            if error is None:
                error = {"type": "OriginalSourceAuthenticationFailure",
                         "message": "an unchanged original C owner could not be proved",
                         "restoration_failures": restore_errors}
            else:
                error["restoration_failures"] = restore_errors
    report = {
        "schema": SCHEMA + "-actual-native-build", "version": VERSION,
        "status": "PASS" if error is None else "FAIL", "family": FAMILY,
        "label": label, "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "contract_sha256": options.contract_sha256,
        "published_overview_version": GRAPH_VERSION,
        "published_overview_sha256": GRAPH["summary"][1],
        "variant_source_sha256": FEATURE["variant"][1],
        "variant_source_bytes": FEATURE["variant"][2],
        "original_source_sha256": ORIGINAL_C[1],
        "adapter_source_sha256": ADAPTER[1],
        "source_apply_count": 0 if workdir is None else sum(
            (workdir, phase) in _APPLIED for phase in PHASES
        ),
        "expected_compiler_process_count": 14,
        "actual_compiler_process_count": len(steps),
        "phase_count": len(phases), "phases": phases,
        "compiler_processes": steps, "reproducibility": reproduction,
        "actual_failure": error,
        "historical_c_semantic_mismatch_count": 1230,
        "historical_c_verified_passing_case_count": 7325,
        "current_rust_semantic_mismatch_count": 1440,
        "current_rust_verified_passing_case_count": 14853,
        "actual_rust_v18_native_build_status": "PASS",
        "actual_rust_v18_compiler_process_count": 28,
        "actual_rust_v18_archive_opened": False,
        "historical_rust_v17_authorization_status": "BLOCKED",
        "candidate_correctness": "NOT MEASURED", "candidate_imports": 0,
        "candidate_processes_started": 0, "native_libraries_loaded": 0,
        "installed_native_read": False, "installed_native_activated": False,
        "historical_archives_opened": 0, "hidden_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "qualified_candidate_count": 0, "winner_selected": False,
    }
    return publish_report(kernel, report, label)


def arguments(values: list[str] | None = None) -> argparse.Namespace:
    if values is None:
        values = sys.argv[1:]
    need(type(values) is list and all(type(value) is str for value in values),
         "require an exact independently authorised V16 command")
    flags = [value for value in values if value.startswith("--")]
    need(all(flag == "--owned-source-sha256" or flags.count(flag) == 1
             for flag in flags), "reject repeated or hidden build authorisations")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--family")
    parser.add_argument("--label")
    parser.add_argument("--owned-source-sha256", action="append", default=[])
    parser.add_argument("--variant-source-sha256")
    options = parser.parse_args(values)
    checked_digest(options.source_sha256, "V16 source")
    checked_digest(options.protocol_sha256, "V16 protocol")
    if options.contract_sha256 is not None:
        checked_digest(options.contract_sha256, "V16 contract")
    if options.render_contract:
        need(options.contract_sha256 is None and options.family is None
             and options.label is None and not options.owned_source_sha256
             and options.variant_source_sha256 is None,
             "contract rendering never authorises a build or native target")
    elif options.self_test or options.verify_frozen_context:
        need(options.contract_sha256 is not None and options.family is None
             and options.label is None and not options.owned_source_sha256
             and options.variant_source_sha256 is None,
             "source-only gates require an exact frozen contract and forbid builds")
    else:
        need(options.contract_sha256 is not None and options.family == FAMILY
             and options.label is not None
             and options.variant_source_sha256 == FEATURE["variant"][1],
             "require explicitly supplied complete first-party build authority")
        checked_label(options.label)
        checked_digest(options.variant_source_sha256, "caller-pinned C variant")
    return options


def main(values: list[str] | None = None) -> int:
    try:
        verify_runtime()
        selected = arguments(values)
        if selected.build:
            result = run_build(selected)
        else:
            context = verify_context(
                selected.source_sha256, selected.protocol_sha256,
                selected.contract_sha256,
            )
            if selected.render_contract:
                result = contract_document(
                    selected.source_sha256, selected.protocol_sha256,
                    context["overview"],
                )
            elif selected.self_test:
                result = self_test(context, selected.source_sha256,
                                   selected.protocol_sha256)
            else:
                result = {
                    "schema": SCHEMA + "-read-only-frozen-context",
                    "status": "PASS", "version": VERSION, "family": FAMILY,
                    "source_sha256": selected.source_sha256,
                    "protocol_sha256": selected.protocol_sha256,
                    "contract_sha256": selected.contract_sha256,
                    "published_overview_version": GRAPH_VERSION,
                    "published_overview_owner_count": 4,
                    "authenticated_evidence_owner_lower_bound":
                        context["overview"]["authenticated_evidence_owner_lower_bound"],
                    "authenticated_history_reference_lower_bound":
                        context["overview"]["authenticated_history_reference_lower_bound"],
                    "first_party_c_variant_sha256": FEATURE["variant"][1],
                    "first_party_c_variant_bytes": FEATURE["variant"][2],
                    "historical_c_semantic_mismatch_count": 1230,
                    "historical_c_verified_passing_case_count": 7325,
                    "current_rust_semantic_mismatch_count": 1440,
                    "current_rust_verified_passing_case_count": 14853,
                    "actual_rust_v18_native_build_status": "PASS",
                    "actual_rust_v18_compiler_process_count": 28,
                    "actual_rust_v18_archive_opened": False,
                    "historical_rust_v17_authorization_status": "BLOCKED",
                    "original_case_execution_denominator": 31237,
                    "original_suite_count": 13,
                    "named_private_waiver_count": 13,
                    "supplemental_reference_cases_per_worker": 8244,
                    "future_phase_count": 2,
                    "future_compiler_process_count_per_phase": 7,
                    "future_total_compiler_process_count": 14,
                    "source_only_effects": effects(),
                }
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 0 if selected.render_contract or result.get("status") == "PASS" else 1
    except BaseException as error:
        result = {
            "schema": SCHEMA + "-entry-failure", "version": VERSION,
            "status": "FAIL", "error_type": type(error).__qualname__,
            "error_message": str(error), "source_only_effects": effects(),
        }
        try:
            sys.stdout.buffer.write(canonical(result))
            sys.stdout.buffer.flush()
        except (OSError, ValueError, TypeError):
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
