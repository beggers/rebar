#!/usr/bin/env python3
"""Show three first-party runner sources without inventing a usable candidate."""

from __future__ import annotations

import argparse
import ast
import builtins
import copy
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v46.py"
OUTPUT = "docs/evidence/candidate-current-overview-v46"
SCHEMA = "rebar-candidate-current-overview-v46"
V45 = {
    "source": (
        "tools/render_candidate_current_overview_v45.py",
        "07a7e1b6c96434e66e852e0eb784326816d340edb338d2e89de4f1d6918bb586",
        68616,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v45.inputs.json",
        "cbc1b861fe59067e64adf396493630360f6bf616fe1f51598220aabafadea4a5",
        352881,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v45.json",
        "1086a7bd72116b590d00f5216835534ec745265a0f249d3cd5eb05a3701ff840",
        1013003,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v45.svg",
        "1c9d56fd4b8480bab9cedc2e95b6449a414cb68a02ee447963454db5b4242b2b",
        15948,
    ),
}
ZIG = {
    "worker": (
        "tools/run_frozen_zig_original_p0_candidate_worker_v1.py",
        "ddafdc5b1fe06dbfa6449cbfde768d7fee6d16953b3c769c1e30aa600e3c62f9",
        123801,
    ),
    "runner": (
        "tools/run_frozen_zig_original_p0_candidate_v1.py",
        "8c9be13232fdbab7ff01b2313a816fd80e033fb5b6d0bf3d8cb07444eeba4856",
        55722,
    ),
    "protocol": (
        "oracle/phase2/ZIG-ORIGINAL-P0-CANDIDATE-PROTOCOL-V1.md",
        "294dfb6bc8e286d8415b329f8b2918b856ab3b2d1afb8261e3e04663028fda3c",
        9040,
    ),
    "contract": (
        "oracle/phase2/zig-original-p0-candidate-protocol-v1.json",
        "1ff289540457ecba4e91b3b9491b3c42872a5db09b95815b8f58fcdc34315470",
        19592,
    ),
}
GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756,
)
P0 = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
    45632,
)
RUST_V7 = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v7.py",
        "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
        505616,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md",
        "0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840",
        8433,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v7.json",
        "9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5",
        46385,
    ),
}
PUBLIC_ORACLE = {
    "source": (
        "tools/verify_public_entrypoint_import_v1.py",
        "c0a61c4cf520e82bf0c327a17c06daf64f57a1dcfd20b37c6e9f7b84177108b4",
        83957,
    ),
    "protocol": (
        "oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md",
        "01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0",
        7991,
    ),
    "contract": (
        "oracle/phase1/p0-public-entrypoint-import-v1.json",
        "b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47",
        9823,
    ),
}
PUBLIC_MODULE = (
    "rebar.py",
    "289769bd637ea525ae7e71d263377e15c0f394ba20619c11b98e266f57fcc34f",
    212,
)
PUBLIC_PROJECT = (
    "pyproject.toml",
    "7d50e8c6c2bc76a0e3ddcac6b5f157b013bcfd76944fdeb2c1c81e0181ae7825",
    224,
)
MATRIX_SHA256 = (
    "f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58"
)
PUBLIC_STATUS = "UNQUALIFIED ZIG PROTOTYPE; NOT A WINNER"
CASE_COUNTS = {
    "PASS": 17,
    "FAIL": 7,
    "NOT MEASURED": 6,
    "NOT ESTABLISHED": 1,
    "NOT OPENED": 1,
}
SUITES = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912),
    ("substitution_v2", 5120),
    ("shape_v2", 10240),
    ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
ZIG_STATUS = "SOURCE FROZEN; FIRST-PARTY ZIG CANDIDATE NOT RUN"
COMPILER_PATH = "/tmp/zig-x86_64-linux-0.16.0/zig"
COMPILER_SHA256 = (
    "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c"
)
COMPILER_BYTES = 172641672
FROZEN_RUNNERS = ["c", "rust", "zig"]
PENDING_RUNNERS = ["cpp", "go", "fortran"]
ZERO_EFFECTS = {
    "actual_candidate_imports": 0,
    "actual_candidate_workers": 0,
    "actual_compiler_processes": 0,
    "actual_native_activations": 0,
    "actual_native_libraries_loaded": 0,
    "actual_native_promotions": 0,
    "actual_network_requests": 0,
    "actual_reference_workers": 0,
    "actual_source_builds": 0,
    "actual_threads_started": 0,
    "archives_inflated": 0,
    "archives_opened": 0,
    "benchmark_files_read": 0,
    "clock_samples": 0,
    "compressed_archive_bytes_read": 0,
    "hidden_cases_read": 0,
    "holdout": "NOT OPENED",
    "memory": "NOT MEASURED",
    "performance": "NOT MEASURED",
    "runtime_non_delegation": "NOT ESTABLISHED",
    "timing_trials_run": 0,
    "uncompressed_archive_bytes_read": 0,
    "undefined_behavior": "NOT MEASURED",
    "winner_selected": False,
}


def load_v45() -> tuple[
    types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType,
]:
    path, fingerprint, size = V45["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags)
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.geteuid()
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_size != size
        ):
            raise ValueError("reject a nonprivate or substituted pushed V45 source")
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(descriptor, min(262144, remaining))
            if not piece:
                raise ValueError("reject a truncated pushed V45 source")
            pieces.append(piece)
            remaining -= len(piece)
        if os.read(descriptor, 1):
            raise ValueError("reject appended pushed V45 renderer bytes")
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        if (
            hashlib.sha256(raw).hexdigest() != fingerprint
            or (
                before.st_dev, before.st_ino, before.st_size,
                before.st_nlink, before.st_mtime_ns,
            ) != (
                after.st_dev, after.st_ino, after.st_size,
                after.st_nlink, after.st_mtime_ns,
            )
        ):
            raise ValueError("reject replacement during V45 authentication")
    finally:
        os.close(descriptor)
    previous = types.ModuleType("_rebar_pushed_three_runner_history_v45")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    v44, v43, v42, v41, v40, base = previous.load_v44()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v45"
        and previous.SELF == path
        and previous.PUBLIC_STATUS == PUBLIC_STATUS
        and previous.MATRIX_SHA256 == MATRIX_SHA256,
        "load only the exact pushed V45 public-failure graph renderer",
    )
    return previous, v44, v43, v42, v41, v40, base


def matches(base: types.ModuleType, actual: object,
            expected: dict[str, object], label: str) -> None:
    base.need(type(actual) is dict, "reject a missing " + label)
    assert isinstance(actual, dict)
    for key, value in expected.items():
        base.need(
            actual.get(key) == value,
            "reject a changed " + label + ": " + key,
        )


def source_pin(pin: tuple[str, str, int]) -> dict[str, str]:
    return {"path": pin[0], "sha256": pin[1]}


def expected_contract(base: types.ModuleType) -> dict:
    predecessors = {
        role: base.pin(*pin) for role, pin in V45.items()
    }
    return {
        "schema": "rebar-frozen-zig-original-p0-candidate-protocol-v1-source-freeze",
        "version": 1,
        "status": ZIG_STATUS,
        "phase": "CANDIDATES",
        "family": "zig",
        "goal": base.pin(*GOAL),
        "source": {
            role: source_pin(ZIG[role])
            for role in ("protocol", "runner", "worker")
        },
        "phase_one": {
            "owner": base.pin(*P0),
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "named_private_waiver_count": 13,
            "supplemental_cases_added": False,
            "suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES
            ],
        },
        "candidate_run_policy": {
            "candidate_matching_status": "NOT RUN",
            "candidate_qualified": False,
            "future_exclusively_runnable_candidate_family": "zig",
            "future_one_distinct_real_worker_per_original_suite": True,
            "future_preserve_every_case_and_mismatch": True,
            "future_preserve_full_stdout_stderr_hashes": True,
            "future_process_count_only_after_real_success": 13,
            "historical_build_does_not_activate_native": True,
            "matching_pass_requires_all_31237_original_cases": True,
            "maximum_retained_worker_stderr_bytes": 2097152,
            "maximum_retained_worker_stdout_bytes": 1048576,
            "missing_or_uncounted_case_fails_closed": True,
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "runnable_candidate_families": [],
            "runnable_candidate_family_count": 0,
            "runner_builds_or_activates_native": False,
            "verified_live_zig_activation": "NOT FROZEN; FAIL CLOSED",
            "worker_timeout_seconds": 3600,
        },
        "from_scratch_policy": {
            "another_candidate_engine": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "stdlib_matching_engine": "FORBIDDEN",
        },
        "coordinator_released_current_v45_history": {
            "actual_rust_v6_build_archive_gzip_inflation_count": 1,
            "actual_rust_v6_build_archive_read_count": 1,
            "actual_rust_v6_candidate_workers": 0,
            "actually_runnable_candidate_families": [],
            "actually_runnable_candidate_family_count": 0,
            "authenticated_evidence_owner_lower_bound": 166,
            "authenticated_history_reference_lower_bound": 171,
            "holdout": "NOT OPENED",
            "overview": "V45",
            "owners": predecessors,
            "public_entrypoint_case_status_counts": copy.deepcopy(CASE_COUNTS),
            "public_entrypoint_matrix_case_count": 32,
            "publication_safe_rust_v7_source_frozen_only": True,
            "zig_candidate_matching": "NOT RUN",
            "zig_live_activation": "NOT FROZEN; FAIL CLOSED",
            "zig_public_entrypoint_status": "FAIL",
        },
        "expanded_public_entrypoint_oracle": {
            "actual_project_configuration": base.pin(*PUBLIC_PROJECT),
            "actual_public_imports_by_zig_source_freeze": 0,
            "actual_public_source": base.pin(*PUBLIC_MODULE),
            "additional_cases_added_to_original_denominator": False,
            "additional_signature_case_count": 50,
            "candidate_qualified": False,
            "case_status_counts": copy.deepcopy(CASE_COUNTS),
            "holdout": "NOT OPENED",
            "matrix_case_count": 32,
            "matrix_sha256": MATRIX_SHA256,
            "oracle_owners": {
                "source": base.pin(*PUBLIC_ORACLE["source"]),
                "protocol": base.pin(*PUBLIC_ORACLE["protocol"]),
                "document": base.pin(*PUBLIC_ORACLE["contract"]),
            },
            "performance": "NOT MEASURED",
            "public_entrypoint_classification": PUBLIC_STATUS,
            "public_entrypoint_status": "FAIL",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "selected_family_is_historically_failed_zig": True,
            "source_ast_only": True,
            "winner_selected": False,
        },
        "first_party_zig_family": {
            "candidate_imported_by_source_freeze": False,
            "exact_official_zig_compiler": {
                "bytes": COMPILER_BYTES,
                "compiler_executed": False,
                "native_library_loaded": False,
                "path": COMPILER_PATH,
                "sha256": COMPILER_SHA256,
            },
            "family_spec": {
                "family": "zig",
                "owned_source_count": 3,
                "combined_native_engine_and_bridge": False,
            },
            "native_library_loaded_by_source_freeze": False,
            "source_audit": {
                "cross_family_source_dependency_count": 0,
                "display_metadata_is_not_an_import": True,
                "external_regex_source_dependency_count": 0,
                "family": "zig",
                "owned_native_bridge_relative":
                    "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
                "owned_native_engine_relative": "candidates/_zig_probe.so",
                "owned_python_bridge_module": "candidates._zig_bridge",
                "runtime_non_delegation": "NOT ESTABLISHED",
                "stdlib_regex_engine_source_dependency_count": 0,
            },
            "source_owners": {
                "adapter": {
                    "bytes": 68422,
                    "path": "candidates/zig_candidate.py",
                    "sha256":
                        "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
                },
                "bridge": {
                    "bytes": 173026,
                    "path": "candidates/zig/py_bridge.c",
                    "sha256":
                        "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b",
                },
                "engine": {
                    "bytes": 186915,
                    "path": "candidates/zig/mini_regex.zig",
                    "sha256":
                        "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
                },
            },
        },
        "historical_zig_original_campaign": {
            "archive_opened_by_source_freeze": False,
            "historical_candidate_workers": 13,
            "historical_case_execution_denominator": 31237,
            "historical_completed_suite_count": 13,
            "historical_infrastructure_failure_count": 0,
            "historical_matching_status": "FAIL",
            "historical_producer_version": 3,
            "historical_result_is_corrected_v4_campaign": False,
            "historical_semantic_mismatch_count": 1764,
            "historical_verified_passing_case_count": 3711,
            "individual_suite_mismatches":
                "NOT ESTABLISHED BY SMALL RECEIPT",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "publication_status": "PASS",
        },
        "historical_zig_v12_build": {
            "archive_opened_by_source_freeze": False,
            "build_publication_status": "PASS",
            "build_receipt_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_correctness": "NOT MEASURED",
            "compiler_executed_by_source_freeze": False,
            "compiler_process_count": 26,
            "compiler_sha256": COMPILER_SHA256,
            "historical_build_establishes_candidate_correctness": False,
            "historical_build_establishes_live_activation": False,
            "historical_build_status": "PASS",
            "native_libraries_loaded_by_historical_build": 0,
            "source_apply_count": 2,
        },
        "preserved_actual_rust_v6_failure": {
            "actual_preflight_status": "FAIL",
            "failure": {
                "bytes": 3175,
                "path": "oracle/phase2/evidence/"
                    "repaired-rust-original-campaign-v6-rust-"
                    "phase2-v13-rust-pattern-repr-original-p0-entry-failure.json",
                "sha256":
                    "88367fd41665bbeafb0645e3b03130ca97c1c54729863372d422e693169420d7",
            },
            "failure_archive_read_or_inflated_by_zig_source_freeze": False,
            "family": "rust",
            "historical_candidate_workers": 0,
            "historical_matching_archive_read_count": 0,
            "historical_native_activations": 0,
            "historical_reference_archive_read_count": 0,
            "historical_reference_workers": 0,
            "historical_semantic_mismatch_count": "NOT MEASURED",
            "historical_source_build_archive_compressed_bytes": 108985,
            "historical_source_build_archive_effect_was_omitted_by_failed_controller":
                True,
            "historical_source_build_archive_gzip_inflation_count": 1,
            "historical_source_build_archive_read_count": 1,
            "independent_observation": {
                "bytes": 3061,
                "path": "oracle/phase2/evidence/"
                    "repaired-rust-original-campaign-v6-rust-"
                    "phase2-v13-rust-pattern-repr-original-p0-"
                    "entry-failure-observation.json",
                "sha256":
                    "51846c742aafbfc2c42ddad75836310bba518b3a76d0f8fa1548a55128852ad6",
            },
        },
        "separately_frozen_publication_safe_rust_v7": {
            "authenticated_evidence_owner_lower_bound": 166,
            "authenticated_history_reference_lower_bound": 171,
            "family": "rust",
            "owners": {
                "document": base.pin(*RUST_V7["contract"]),
                "protocol": base.pin(*RUST_V7["protocol"]),
                "source": base.pin(*RUST_V7["source"]),
            },
            "preserved_actual_v6_build_archive_gzip_inflation_count": 1,
            "preserved_actual_v6_build_archive_read_count": 1,
            "rust_candidate_matching": "NOT RUN",
            "rust_candidate_workers_started_by_source_freeze": 0,
            "rust_runner_is_a_zig_runner": False,
            "source_freeze_status":
                "SOURCE FROZEN; CORRECTED RUST V13 CANDIDATE NOT RUN",
        },
        "scanner_capture_overflow_source_repair": {
            "capture_overflow_case_count": 64,
            "capture_overflow_family_counts": {
                "named-captures": 16,
                "nested-captures": 32,
                "numbered-captures": 16,
            },
            "corrected_candidate_matching": "NOT RUN",
            "correction_applied": False,
            "matrix_case_count": 1024,
            "mismatch_reduction": "NOT MEASURED",
            "preserved_nonoverflow_case_count": 960,
            "projected_corrected_adapter_bytes": 68530,
            "projected_corrected_adapter_materialized": False,
            "projected_corrected_adapter_sha256":
                "0ab9f56b469df7939af8a221a4deac9351de2162960085ca7fa2d69179480e2b",
            "source_repair_status":
                "SOURCE FROZEN; CORRECTED CANDIDATE NOT RUN",
            "speedup": "NOT MEASURED",
            "verbose_scanner_620_mismatches":
                "NOT REPAIRED; CORRECTED CANDIDATE NOT RUN",
        },
        "corrected_v4_original_producer": {
            "family_count": 6,
            "source_inventory_is_not_candidate_execution": True,
            "source_owner_count": 25,
        },
        "corrected_public_reference": {
            "archive_inflated_by_source_freeze": False,
            "archive_opened_by_source_freeze": False,
            "cache_case_count_per_reference": 96,
            "candidate_facing_reference": True,
            "case_count_per_reference": 6912,
            "new_reference_processes_started_by_source_freeze": 0,
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "publication_status": "PASS",
            "reference_process_ids": [81, 82],
            "reference_status": "PASS",
            "reference_worker_count": 2,
            "total_actual_reference_case_observations": 13824,
        },
        "python": {
            "isolated": True,
            "path": base.PYTHON,
            "sha256": base.PYTHON_SHA,
            "version": "3.14.6",
        },
        "source_only_effects": copy.deepcopy(ZERO_EFFECTS),
        "candidate_correctness": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def validate_zig_contract(base: types.ModuleType, document: object) -> None:
    expected = expected_contract(base)
    base.need(type(document) is dict, "reject a missing frozen Zig contract")
    assert isinstance(document, dict)
    scalar_names = (
        "schema", "version", "status", "phase", "family", "goal",
        "source", "python", "candidate_correctness",
        "qualified_candidate_count", "holdout", "performance", "memory",
        "undefined_behavior", "winner_selected", "source_only_effects",
    )
    for name in scalar_names:
        base.need(
            document.get(name) == expected[name],
            "reject changed frozen Zig contract: " + name,
        )
    for name in (
        "phase_one", "candidate_run_policy", "from_scratch_policy",
        "coordinator_released_current_v45_history",
        "expanded_public_entrypoint_oracle",
        "historical_zig_original_campaign", "historical_zig_v12_build",
        "preserved_actual_rust_v6_failure",
        "separately_frozen_publication_safe_rust_v7",
        "scanner_capture_overflow_source_repair",
        "corrected_v4_original_producer", "corrected_public_reference",
    ):
        matches(base, document.get(name), expected[name], "Zig " + name)
    family = document.get("first_party_zig_family")
    expected_family = expected["first_party_zig_family"]
    assert isinstance(expected_family, dict)
    matches(
        base, family,
        {
            "candidate_imported_by_source_freeze": False,
            "native_library_loaded_by_source_freeze": False,
            "exact_official_zig_compiler":
                expected_family["exact_official_zig_compiler"],
            "source_owners": expected_family["source_owners"],
        },
        "first-party Zig family",
    )
    assert isinstance(family, dict)
    matches(
        base, family.get("family_spec"), expected_family["family_spec"],
        "independent first-party Zig family specification",
    )
    matches(
        base, family.get("source_audit"), expected_family["source_audit"],
        "no-package and no-cross-family Zig source audit",
    )
    phase = document["phase_one"]
    base.need(
        type(phase["suites"]) is list
        and len(phase["suites"]) == 13
        and sum(row["case_execution_count"] for row in phase["suites"])
        == 31237,
        "retain all 13 exact original suites and 31,237 original cases",
    )


def source_constants(base: types.ModuleType, raw: bytes,
                     role: str) -> dict[str, object]:
    try:
        tree = ast.parse(raw.decode("utf-8"), filename=ZIG[role][0])
    except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
        raise base.GraphError("reject an invalid frozen Zig " + role) from error
    constants: dict[str, object] = {}
    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets.extend(node.targets)
            value = node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets.append(node.target)
            value = node.value
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                try:
                    constants[target.id] = ast.literal_eval(value)
                except (ValueError, TypeError, RecursionError):
                    continue
    functions = {
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    common = {
        "FAMILY": "zig",
        "PROTOCOL_RELATIVE": ZIG["protocol"][0],
        "DOCUMENT_RELATIVE": ZIG["contract"][0],
        "CONTRACT_SCHEMA": "rebar-frozen-zig-original-p0-candidate-protocol-v1",
        "SUITES": SUITES,
        "SUITE_COUNT": 13,
        "CASE_DENOMINATOR": 31237,
        "PRIVATE_WAIVER_COUNT": 13,
        "PINNED_PYTHON": base.PYTHON,
        "PINNED_PYTHON_SHA256": base.PYTHON_SHA,
    }
    if role == "worker":
        required = {
            **common,
            "SOURCE_RELATIVE": ZIG["worker"][0],
            "RUNNER_RELATIVE": ZIG["runner"][0],
            "SCHEMA": "rebar-frozen-zig-original-p0-candidate-worker-v1",
            "RUNNER_SCHEMA": "rebar-frozen-zig-original-p0-candidate-v1",
            "FAMILY_NAMES": ("rust", "c", "zig", "cpp", "go", "fortran"),
            "SOURCE_FAMILY_COUNT": 6,
            "SOURCE_OWNER_COUNT": 25,
            "ZIG_COMPILER_SHA256": COMPILER_SHA256,
            "ZIG_COMPILER_ABSOLUTE_PATH": COMPILER_PATH,
            "ZIG_COMPILER_BYTES": COMPILER_BYTES,
            "PUBLIC_ENTRYPOINT_MATRIX_SHA256": MATRIX_SHA256,
        }
        required_functions = {
            "source_self_test", "verify_frozen_context",
            "render_frozen_contract", "main",
        }
    else:
        required = {
            **common,
            "SOURCE_RELATIVE": ZIG["runner"][0],
            "WORKER_RELATIVE": ZIG["worker"][0],
            "SCHEMA": "rebar-frozen-zig-original-p0-candidate-v1",
            "WORKER_SCHEMA":
                "rebar-frozen-zig-original-p0-candidate-worker-v1",
            "CURRENT_V45_SUMMARY_SHA256": V45["summary"][1],
            "CURRENT_V45_SUMMARY_BYTES": V45["summary"][2],
            "CURRENT_RUST_V7_SOURCE_SHA256": RUST_V7["source"][1],
            "CURRENT_PUBLIC_MATRIX_SHA256": MATRIX_SHA256,
            "CURRENT_EVIDENCE_OWNER_LOWER_BOUND": 166,
            "CURRENT_AUTHENTICATED_REFERENCE_LOWER_BOUND": 171,
        }
        required_functions = {
            "source_self_test", "verify_frozen_context", "main",
        }
    for name, expected in required.items():
        base.need(
            constants.get(name) == expected,
            "reject substituted frozen Zig " + role + " AST: " + name,
        )
    base.need(
        required_functions.issubset(functions),
        "require all frozen Zig " + role + " source-only gate definitions",
    )
    return {
        "source_ast_parsed_without_execution": True,
        "source_role": role,
        "source_sha256": ZIG[role][1],
        "source_bytes": ZIG[role][2],
        "family": "zig",
        "original_case_count": 31237,
        "original_suite_count": 13,
        "original_private_waiver_count": 13,
        "suites": [
            {"id": name, "case_execution_count": count}
            for name, count in SUITES
        ],
        "required_constants": {
            key: list(value) if isinstance(value, tuple) and key != "SUITES"
            else [list(pair) for pair in value] if key == "SUITES"
            else value
            for key, value in required.items()
        },
        "required_source_only_functions": sorted(required_functions),
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "archives_opened_by_graph": 0,
        "archives_inflated_by_graph": 0,
        "clock_samples_by_graph": 0,
        "holdout_cases_read_by_graph": 0,
    }


def synthetic_source_ast(base: types.ModuleType, role: str) -> dict:
    common: dict[str, object] = {
        "FAMILY": "zig",
        "PROTOCOL_RELATIVE": ZIG["protocol"][0],
        "DOCUMENT_RELATIVE": ZIG["contract"][0],
        "CONTRACT_SCHEMA": "rebar-frozen-zig-original-p0-candidate-protocol-v1",
        "SUITES": [list(pair) for pair in SUITES],
        "SUITE_COUNT": 13,
        "CASE_DENOMINATOR": 31237,
        "PRIVATE_WAIVER_COUNT": 13,
        "PINNED_PYTHON": base.PYTHON,
        "PINNED_PYTHON_SHA256": base.PYTHON_SHA,
    }
    if role == "worker":
        common.update({
            "SOURCE_RELATIVE": ZIG["worker"][0],
            "RUNNER_RELATIVE": ZIG["runner"][0],
            "SCHEMA": "rebar-frozen-zig-original-p0-candidate-worker-v1",
            "RUNNER_SCHEMA": "rebar-frozen-zig-original-p0-candidate-v1",
            "FAMILY_NAMES": ["rust", "c", "zig", "cpp", "go", "fortran"],
            "SOURCE_FAMILY_COUNT": 6,
            "SOURCE_OWNER_COUNT": 25,
            "ZIG_COMPILER_SHA256": COMPILER_SHA256,
            "ZIG_COMPILER_ABSOLUTE_PATH": COMPILER_PATH,
            "ZIG_COMPILER_BYTES": COMPILER_BYTES,
            "PUBLIC_ENTRYPOINT_MATRIX_SHA256": MATRIX_SHA256,
        })
        functions = [
            "main", "render_frozen_contract", "source_self_test",
            "verify_frozen_context",
        ]
    else:
        common.update({
            "SOURCE_RELATIVE": ZIG["runner"][0],
            "WORKER_RELATIVE": ZIG["worker"][0],
            "SCHEMA": "rebar-frozen-zig-original-p0-candidate-v1",
            "WORKER_SCHEMA":
                "rebar-frozen-zig-original-p0-candidate-worker-v1",
            "CURRENT_V45_SUMMARY_SHA256": V45["summary"][1],
            "CURRENT_V45_SUMMARY_BYTES": V45["summary"][2],
            "CURRENT_RUST_V7_SOURCE_SHA256": RUST_V7["source"][1],
            "CURRENT_PUBLIC_MATRIX_SHA256": MATRIX_SHA256,
            "CURRENT_EVIDENCE_OWNER_LOWER_BOUND": 166,
            "CURRENT_AUTHENTICATED_REFERENCE_LOWER_BOUND": 171,
        })
        functions = ["main", "source_self_test", "verify_frozen_context"]
    return {
        "source_ast_parsed_without_execution": True,
        "source_role": role,
        "source_sha256": ZIG[role][1],
        "source_bytes": ZIG[role][2],
        "family": "zig",
        "original_case_count": 31237,
        "original_suite_count": 13,
        "original_private_waiver_count": 13,
        "suites": [
            {"id": name, "case_execution_count": count}
            for name, count in SUITES
        ],
        "required_constants": common,
        "required_source_only_functions": functions,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "archives_opened_by_graph": 0,
        "archives_inflated_by_graph": 0,
        "clock_samples_by_graph": 0,
        "holdout_cases_read_by_graph": 0,
    }


def validate_source_ast(base: types.ModuleType, proof: object,
                        role: str) -> None:
    expected = synthetic_source_ast(base, role)
    base.need(
        proof == expected,
        "reject an executed, substituted, delegated or weakened Zig "
        + role + " source AST",
    )


def make_zig_proof(base: types.ModuleType, owners: dict[str, dict],
                   contract: dict, worker_ast: dict, runner_ast: dict) -> dict:
    validate_zig_contract(base, contract)
    validate_source_ast(base, worker_ast, "worker")
    validate_source_ast(base, runner_ast, "runner")
    proof = {
        "schema": SCHEMA + "-authenticated-zig-v1-source-freeze",
        "version": 1,
        **owners,
        "complete_frozen_contract": copy.deepcopy(contract),
        "worker_source_ast": copy.deepcopy(worker_ast),
        "runner_source_ast": copy.deepcopy(runner_ast),
        "source_freeze_status": ZIG_STATUS,
        "candidate_matching_status": "NOT RUN",
        "candidate_qualified": False,
        "first_party_family": "zig",
        "original_case_count": 31237,
        "original_suite_count": 13,
        "original_private_waiver_count": 13,
        "additional_signature_case_count": 50,
        "public_case_matrix_count": 32,
        "public_case_matrix_sha256": MATRIX_SHA256,
        "public_case_status_counts": copy.deepcopy(CASE_COUNTS),
        "public_entrypoint_status": PUBLIC_STATUS,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_activations_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "archives_opened_by_graph": 0,
        "archives_inflated_by_graph": 0,
        "source_build_archives_opened_by_graph": 0,
        "source_build_archives_inflated_by_graph": 0,
        "clock_samples_by_graph": 0,
        "holdout_cases_read_by_graph": 0,
        "official_compiler_version": "0.16.0",
        "official_compiler_path": COMPILER_PATH,
        "official_compiler_sha256": COMPILER_SHA256,
        "official_compiler_bytes": COMPILER_BYTES,
        "official_compiler_executed_by_graph": False,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    proof["complete_zig_source_binding_sha256"] = base.digest(
        base.canonical(proof),
    )
    validate_zig_proof(base, proof)
    return proof


def validate_zig_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict, "reject a missing complete Zig source proof")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-authenticated-zig-v1-source-freeze",
        "version": 1,
        "source_freeze_status": ZIG_STATUS,
        "candidate_matching_status": "NOT RUN",
        "candidate_qualified": False,
        "first_party_family": "zig",
        "original_case_count": 31237,
        "original_suite_count": 13,
        "original_private_waiver_count": 13,
        "additional_signature_case_count": 50,
        "public_case_matrix_count": 32,
        "public_case_matrix_sha256": MATRIX_SHA256,
        "public_case_status_counts": CASE_COUNTS,
        "public_entrypoint_status": PUBLIC_STATUS,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_activations_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "archives_opened_by_graph": 0,
        "archives_inflated_by_graph": 0,
        "source_build_archives_opened_by_graph": 0,
        "source_build_archives_inflated_by_graph": 0,
        "clock_samples_by_graph": 0,
        "holdout_cases_read_by_graph": 0,
        "official_compiler_version": "0.16.0",
        "official_compiler_path": COMPILER_PATH,
        "official_compiler_sha256": COMPILER_SHA256,
        "official_compiler_bytes": COMPILER_BYTES,
        "official_compiler_executed_by_graph": False,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    matches(base, proof, expected, "complete first-party Zig source proof")
    for role, pin in ZIG.items():
        owner = proof.get(role)
        base.need(
            type(owner) is dict
            and owner.get("path") == pin[0]
            and owner.get("sha256") == pin[1]
            and owner.get("bytes") == pin[2]
            and owner.get("uid") == os.geteuid()
            and owner.get("mode") == "0600"
            and owner.get("nlink") == 1
            and type(owner.get("device")) is int and owner["device"] > 0
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "authenticate the exact private independently owned Zig " + role,
        )
    validate_zig_contract(base, proof.get("complete_frozen_contract"))
    validate_source_ast(base, proof.get("worker_source_ast"), "worker")
    validate_source_ast(base, proof.get("runner_source_ast"), "runner")
    body = {
        key: value for key, value in proof.items()
        if key != "complete_zig_source_binding_sha256"
    }
    base.need(
        proof.get("complete_zig_source_binding_sha256")
        == base.digest(base.canonical(body)),
        "bind every complete Zig source owner, AST, contract and zero effect",
    )


def authenticate_zig(base: types.ModuleType,
                     supplied: dict[str, str]) -> dict:
    owners: dict[str, dict] = {}
    raw: dict[str, bytes] = {}
    for role, pin in ZIG.items():
        base.need(
            base.checked(supplied.get(role), "exact released Zig " + role)
            == pin[1],
            "require the independently released first-party Zig " + role,
        )
        raw[role], owners[role] = base.read_owner(*pin, private=True)
    contract = base.document(
        raw["contract"], "exact released Zig source-freeze contract",
        exact=False,
    )
    worker_ast = source_constants(base, raw["worker"], "worker")
    runner_ast = source_constants(base, raw["runner"], "runner")
    return make_zig_proof(base, owners, contract, worker_ast, runner_ast)


def authenticate_v45(previous: types.ModuleType,
                     v44: types.ModuleType, v43: types.ModuleType,
                     v42: types.ModuleType, v41: types.ModuleType,
                     v40: types.ModuleType, base: types.ModuleType,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    raw: dict[str, bytes] = {}
    for role, pin in V45.items():
        base.need(
            base.checked(supplied.get(role), "exact pushed V45 " + role)
            == pin[1],
            "require the independently supplied pushed V45 " + role,
        )
        raw[role], _ = base.read_owner(*pin, private=True)
    old = base.document(raw["summary"], "complete pushed V45 summary")
    old_inputs = base.document(raw["inputs"], "complete pushed V45 inputs")
    snapshot = old.get("snapshot")
    previous.validate_snapshot(v44, v43, v42, v41, v40, base, snapshot)
    old44, _old44_inputs, old44svg = previous.authenticate_v44(
        v44, v43, v42, v41, v40, base,
        {role: pin[1] for role, pin in previous.V44.items()},
    )
    base.need(
        old44.get("version") == 44
        and old.get("schema") == SCHEMA.replace("v46", "v45") + "-summary"
        and old.get("version") == 45
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V45["source"])
        and old.get("inputs") == base.pin(*V45["inputs"])
        and old.get("svg") == base.pin(*V45["svg"])
        and old_inputs.get("schema")
        == SCHEMA.replace("v46", "v45") + "-inputs"
        and old_inputs.get("version") == 45
        and old_inputs.get("renderer") == base.pin(*V45["source"])
        and raw["svg"] == previous.make_svg(
            v44, v43, v42, v41, v40, base, snapshot, old44svg,
            V45["source"][1], V45["inputs"][1],
        )
        and old.get("public_entrypoint_status") == PUBLIC_STATUS
        and old.get("public_entrypoint_case_status_counts") == CASE_COUNTS
        and old.get("qualified_candidate_count") == 0,
        "authenticate and exactly regenerate all four immutable pushed V45 "
        "owners without using an archive, compiler, holdout or candidate",
    )
    public = previous.authenticate_public_oracle(
        base, PUBLIC_ORACLE["source"][1],
        PUBLIC_ORACLE["protocol"][1],
        PUBLIC_ORACLE["contract"][1], MATRIX_SHA256,
    )
    base.need(
        snapshot.get("public_entrypoint_source_oracle") == public,
        "re-authenticate the complete actual 32-observation public failure",
    )
    return old, old_inputs, raw["svg"]


def zig_fields(proof: dict) -> dict:
    return {
        "zig_v1_runner_source_freeze": copy.deepcopy(proof),
        "zig_v1_runner_source_status": ZIG_STATUS,
        "zig_v1_worker_source_sha256": ZIG["worker"][1],
        "zig_v1_controller_source_sha256": ZIG["runner"][1],
        "zig_v1_protocol_sha256": ZIG["protocol"][1],
        "zig_v1_contract_sha256": ZIG["contract"][1],
        "zig_v1_candidate_matching_status": "NOT RUN",
        "zig_v1_candidate_qualified": False,
        "zig_v1_actual_candidate_workers": 0,
        "zig_v1_actual_reference_workers": 0,
        "zig_v1_actual_native_activations": 0,
        "zig_v1_actual_native_libraries_loaded": 0,
        "zig_v1_actual_compiler_processes": 0,
        "zig_v1_official_compiler_version": "0.16.0",
        "zig_v1_official_compiler_path": COMPILER_PATH,
        "zig_v1_official_compiler_sha256": COMPILER_SHA256,
        "zig_v1_official_compiler_bytes": COMPILER_BYTES,
        "zig_v1_official_compiler_executed_by_graph": False,
        "zig_v1_external_regex_package_count": 0,
        "zig_v1_stdlib_regex_engine_dependency_count": 0,
        "zig_v1_cross_candidate_engine_dependency_count": 0,
        "zig_v1_matching_fallback_count": 0,
        "zig_v1_runtime_no_delegation": "NOT ESTABLISHED",
        "frozen_corrected_runner_source_family_count": 3,
        "frozen_corrected_runner_source_families":
            copy.deepcopy(FROZEN_RUNNERS),
        "other_corrected_candidate_family_count": 3,
        "pending_corrected_candidate_families":
            copy.deepcopy(PENDING_RUNNERS),
        "dedicated_corrected_runnable_family_count": 0,
        "dedicated_corrected_runnable_families": [],
        "actually_runnable_candidate_family_count": 0,
        "actually_runnable_candidate_families": [],
        "corrected_zig_matching_status": "NOT RUN",
        "corrected_zig_candidate_qualified": False,
        "corrected_zig_candidate_workers_started": 0,
        "corrected_zig_matching_mismatch_reduction": "NOT MEASURED",
        "corrected_zig_matching_speedup": "NOT MEASURED",
        "actual_compiler_processes_started_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def validate_snapshot(previous: types.ModuleType,
                      v44: types.ModuleType, v43: types.ModuleType,
                      v42: types.ModuleType, v41: types.ModuleType,
                      v40: types.ModuleType, base: types.ModuleType,
                      snapshot: object) -> None:
    base.need(type(snapshot) is dict, "reject a missing three-runner snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("zig_v1_runner_source_freeze")
    validate_zig_proof(base, proof)
    assert isinstance(proof, dict)
    updates = zig_fields(proof)
    for key, value in updates.items():
        base.need(
            snapshot.get(key) == value,
            "reject invented Zig execution, compatibility or measurement: "
            + key,
        )
    replaced = snapshot.get("preserved_v45_replaced_snapshot_fields")
    base.need(type(replaced) is dict, "preserve all changed V45 snapshot fields")
    assert isinstance(replaced, dict)
    historical = copy.deepcopy(snapshot)
    historical.pop("preserved_v45_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            historical[key] = copy.deepcopy(replaced[key])
        else:
            historical.pop(key, None)
    previous.validate_snapshot(v44, v43, v42, v41, v40, base, historical)
    base.need(
        set(replaced).issubset(updates)
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("private_waiver_count") == 13
        and snapshot.get("supplementary_signature_check_count") == 50
        and snapshot.get("public_entrypoint_case_matrix_count") == 32
        and snapshot.get("public_entrypoint_case_status_counts") == CASE_COUNTS
        and snapshot.get("public_entrypoint_status") == PUBLIC_STATUS
        and snapshot.get("actual_rust_controller_status") == "FAIL"
        and snapshot.get("actual_rust_source_build_archive_read_count") == 1
        and snapshot.get("actual_rust_source_build_archive_gzip_inflation_count")
        == 1
        and snapshot.get("actual_rust_source_build_archive_compressed_bytes")
        == 108985
        and snapshot.get("actual_rust_source_build_archive_uncompressed_bytes")
        == 760477
        and snapshot.get(
            "actual_rust_controller_ledger_omits_source_build_archive_effect",
        ) is True
        and snapshot.get("rust_v3_original_campaign_semantic_mismatch_count")
        == 1087
        and snapshot.get("rust_v4_original_campaign_semantic_mismatch_count")
        == 1036
        and snapshot.get("c_v4_original_campaign_semantic_mismatch_count")
        == 1230
        and snapshot.get("zig_v2_original_campaign_semantic_mismatch_count")
        == 2172
        and snapshot.get("zig_v3_original_campaign_semantic_mismatch_count")
        == 1764
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 166
        and snapshot.get("authenticated_history_reference_lower_bound") == 171
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("frozen_corrected_runner_source_families")
        == FROZEN_RUNNERS
        and snapshot.get("frozen_corrected_runner_source_family_count") == 3
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("final_holdout_opened") is False,
        "preserve all historical failures, three separate denominators, "
        "166/171 lower bounds, three source runners and zero runnable families",
    )


def make_svg(previous: types.ModuleType,
             v44: types.ModuleType, v43: types.ModuleType,
             v42: types.ModuleType, v41: types.ModuleType,
             v40: types.ModuleType, base: types.ModuleType,
             snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(previous, v44, v43, v42, v41, v40, base, snapshot)
    source_sha = base.checked(source_sha, "actual current V46 renderer footer")
    inputs_sha = base.checked(inputs_sha, "actual current V46 inputs footer")
    visible = old_svg.decode("utf-8")
    visible = visible.replace("v45-title", "v46-title")
    visible = visible.replace("v45-description", "v46-description")
    replacements = (
        (
            "corrected Python public import fails 7 checks; no replacement "
            "is yet compatible or measured</title>",
            "three candidate test runners prepared; no replacement "
            "is yet compatible or faster</title>",
            "plain-language honest three-runner headline",
        ),
        (
            "C and Rust have frozen runner sources but zero candidates "
            "are actually runnable.",
            "C, Rust and Zig have independently frozen first-party "
            "runner sources, but zero candidates are actually runnable "
            "or qualified.",
            "describe three first-party source runners without execution",
        ),
        (
            "Two frozen first-party runner sources; six source designs; "
            "zero runnable or qualified replacements.",
            "Three frozen first-party runner sources; six source designs; "
            "zero runnable or qualified replacements.",
            "show three frozen source runners and zero runnable candidates",
        ),
        (
            "1. Overall: new Rust source fix; no replacement is runnable",
            "1. Overall: three test runners; zero usable replacements",
            "make the candidate-versus-Python comparison understandable",
        ),
        (
            "Two runner sources are frozen. V6 really failed; V7 is "
            "source-tested only; zero candidates are runnable.",
            "C, Rust and Zig runner sources are frozen; none has produced "
            "a runnable or passing replacement.",
            "distinguish source readiness from a passing test run",
        ),
        (
            "Rust matching NOT RUN after preflight failure; C NOT RUN; "
            "four other runners NOT FROZEN.",
            "C, Rust and Zig matching NOT RUN; C++, Go and Fortran "
            "runner sources NOT FROZEN.",
            "show the exact three pending independent runner families",
        ),
        (
            "0 new workers; current differences NOT MEASURED; old 1,036 "
            "differences / 8,965 passes",
            "0 new workers; 1,036 and 1,087 historical differences; "
            "current result NOT MEASURED",
            "visibly preserve both independent historical Rust failures",
        ),
        (
            "1,764 historical differences; 3,711 historical passes",
            "1,764 and 2,172 historical differences; 3,711 passes "
            "in the later failed run",
            "visibly preserve both independent historical Zig failures",
        ),
        (
            'height="2825" viewBox="0 0 1440 2825"',
            'height="3010" viewBox="0 0 1440 3010"',
            "make room for a legible three-runner banner and exact history",
        ),
        (
            '<rect width="1440" height="1930" rx="22"',
            '<rect width="1440" height="3010" rx="22"',
            "extend the readable graph background across all evidence",
        ),
    )
    for before, after, label in replacements:
        visible = v43.replace_once(base, visible, before, after, label)
    visible = v43.replace_once(
        base, visible,
        "Graph inputs SHA-256: " + V45["inputs"][1],
        "Graph inputs SHA-256: " + inputs_sha,
        "label only the exact current V46 graph input bytes",
    )
    visible = v43.replace_once(
        base, visible,
        "Graph renderer SHA-256: " + V45["source"][1],
        "Graph renderer SHA-256: " + source_sha,
        "label only the exact current V46 renderer source bytes",
    )
    lines = [v42.move_y(line, 110) for line in visible.splitlines()]
    insertion = next(
        index + 1 for index, line in enumerate(lines)
        if "source-tested only; C has not run." in line
    )
    lines[insertion:insertion] = [
        '<rect x="44" y="302" width="1352" height="91" rx="14" '
        'fill="#eef5ff" stroke="#b6cbee"/>',
        '<text x="65" y="335" class="warning">THREE FIRST-PARTY '
        'RUNNERS PREPARED; ZERO USABLE OR QUALIFIED REPLACEMENTS</text>',
        '<text x="67" y="364" class="body">C, Rust and Zig test-runner '
        'sources are frozen. No candidate, native engine or Zig compiler '
        'has been started.</text>',
    ]
    historical = next(
        index for index, line in enumerate(lines)
        if line.startswith("<!-- Zig source correction is frozen only;")
    )
    lines[historical:historical] = [
        '<text x="47" y="2920" class="foot">Historical V45 graph '
        'inputs SHA-256: ' + V45["inputs"][1] + '</text>',
        '<text x="47" y="2942" class="foot">Historical V45 graph '
        'renderer SHA-256: ' + V45["source"][1] + '</text>',
    ]
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    current_input = ("Graph inputs SHA-256: " + inputs_sha).encode("ascii")
    current_source = ("Graph renderer SHA-256: " + source_sha).encode("ascii")
    v44_input = (
        "Historical V44 graph inputs SHA-256: "
        + previous.V44["inputs"][1]
    ).encode("ascii")
    v44_source = (
        "Historical V44 graph renderer SHA-256: "
        + previous.V44["source"][1]
    ).encode("ascii")
    v45_input = (
        "Historical V45 graph inputs SHA-256: " + V45["inputs"][1]
    ).encode("ascii")
    v45_source = (
        "Historical V45 graph renderer SHA-256: " + V45["source"][1]
    ).encode("ascii")
    base.need(
        raw.count(current_input) == 1
        and raw.count(current_source) == 1
        and raw.count(v44_input) == 1
        and raw.count(v44_source) == 1
        and raw.count(v45_input) == 1
        and raw.count(v45_source) == 1
        and ("Graph inputs SHA-256: " + V45["inputs"][1]).encode("ascii")
        not in raw
        and ("Graph renderer SHA-256: " + V45["source"][1]).encode("ascii")
        not in raw,
        "require current exact V46 footer digests and explicitly historical "
        "V44 and V45 graph-source and graph-input digests",
    )
    lower = raw.lower()
    for phrase in (
        b"three candidate test runners prepared",
        b"three first-party runners prepared",
        b"zero usable or qualified replacements",
        b"c, rust and zig",
        b"no candidate, native engine or zig compiler",
        b"public import fails",
        b"unqualified zig prototype; not a winner",
        b"missing __version__",
        b"package mode false",
        b"17 source observations pass",
        b"7 actual public checks fail",
        b"6 not measured",
        b"1 not established",
        b"1 not opened",
        b"separate from 31,237",
        b"50 signature checks",
        b"108,985",
        b"760,477",
        b"1,036",
        b"1,087",
        b"1,230",
        b"1,764",
        b"2,172",
        b"166 / 171",
        b"4,194,304",
        b"not opened",
    ):
        base.need(
            phrase.lower() in lower,
            "reject missing readable actual history or public evidence: "
            + repr(phrase),
        )
    for invented in (
        b"32 candidate passes",
        b"17 candidates pass",
        b"public import passes",
        b"zig compiler executed",
        b"zig candidate qualified",
        b"three runnable candidates",
        b"winner selected",
        b"31,269 original cases",
    ):
        base.need(
            invented not in lower,
            "reject invented candidate execution or changed denominator",
        )
    base.need(
        raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
        "render exactly one terminal SVG linefeed",
    )
    return raw


def build(previous: types.ModuleType,
          v44: types.ModuleType, v43: types.ModuleType,
          v42: types.ModuleType, v41: types.ModuleType,
          v40: types.ModuleType, base: types.ModuleType,
          options: argparse.Namespace) -> tuple[
              dict, tuple[tuple[str, bytes], ...],
          ]:
    source_sha = base.checked(options.source_sha256, "exact V46 graph source")
    base.need(
        type(options.source_bytes) is int
        and 0 < options.source_bytes <= base.OWNER_LIMIT,
        "require an independently supplied exact V46 source byte count",
    )
    own_raw, _ = base.read_owner(
        SELF, source_sha, options.source_bytes, private=True,
    )
    old, old_inputs, old_svg = authenticate_v45(
        previous, v44, v43, v42, v41, v40, base,
        {
            "source": options.previous_source_sha256,
            "inputs": options.previous_inputs_sha256,
            "summary": options.previous_summary_sha256,
            "svg": options.previous_svg_sha256,
        },
    )
    proof = authenticate_zig(
        base,
        {
            "worker": options.zig_worker_sha256,
            "runner": options.zig_runner_sha256,
            "protocol": options.zig_protocol_sha256,
            "contract": options.zig_contract_sha256,
        },
    )
    old_snapshot = old["snapshot"]
    updates = zig_fields(proof)
    snapshot = copy.deepcopy(old_snapshot)
    snapshot.update(updates)
    snapshot["preserved_v45_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old_snapshot[key])
        for key in updates if key in old_snapshot
    }
    validate_snapshot(previous, v44, v43, v42, v41, v40, base, snapshot)
    predecessors = {role: base.pin(*pin) for role, pin in V45.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 46,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessors,
        **updates,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(
        previous, v44, v43, v42, v41, v40, base,
        snapshot, old_svg, source_sha, base.digest(input_raw),
    )
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "retain Python and all six independent first-party source families",
    )
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "frozen_corrected_runner_source_family_count": 3,
            "frozen_corrected_runner_source_families":
                copy.deepcopy(FROZEN_RUNNERS),
            "actually_runnable_candidate_family_count": 0,
            "actually_runnable_candidate_families": [],
            "actual_candidate_workers": 0,
            "actual_native_activations": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row["family"] == "zig":
            row.update({
                "corrected_runner_status":
                    "V1 SOURCE FROZEN; NOT RUNNABLE; ZIG MATCHING NOT RUN",
                "corrected_runner_source_frozen": True,
                "corrected_zig_matching_status": "NOT RUN",
                "zig_v1_candidate_qualified": False,
                "zig_v1_actual_candidate_workers": 0,
                "zig_v1_actual_native_activations": 0,
                "zig_v1_official_compiler_executed_by_graph": False,
                "runtime_no_delegation": "NOT ESTABLISHED",
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 46,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw),
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessors,
        "snapshot": snapshot,
        "families": families,
        **updates,
    })
    summary_raw = base.canonical(summary)
    base.need(
        len(input_raw) <= base.OWNER_LIMIT
        and len(summary_raw) <= base.OWNER_LIMIT
        and len(svg) <= base.OWNER_LIMIT,
        "bound each complete V46 owner without dropping evidence",
    )
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def synthetic_proof(base: types.ModuleType) -> dict:
    owners = {
        role: base.synthetic_owner(pin, 946000 + index)
        for index, (role, pin) in enumerate(ZIG.items())
    }
    return make_zig_proof(
        base, owners, expected_contract(base),
        synthetic_source_ast(base, "worker"),
        synthetic_source_ast(base, "runner"),
    )


def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_zig_proof(base, proof)
    except (
        base.GraphError, TypeError, ValueError, KeyError,
        AttributeError, RecursionError,
    ):
        return 1
    raise base.GraphError("accepted forged source-only Zig proof: " + description)


def self_test(previous: types.ModuleType,
              v44: types.ModuleType, v43: types.ModuleType,
              v42: types.ModuleType, v41: types.ModuleType,
              v40: types.ModuleType, base: types.ModuleType) -> dict:
    history = previous.self_test(v44, v43, v42, v41, v40, base)
    base.need(
        history.get("status") == "PASS"
        and history.get("rejected_hostile_control_count") == 1341
        and history.get("reference_archive_gzip_inflation_count") == 0
        and history.get("matching_archive_gzip_inflation_count") == 0
        and history.get("source_build_archive_gzip_inflation_count_by_graph")
        == 0
        and history.get("public_entrypoint_status") == PUBLIC_STATUS,
        "preserve all 1,341 pushed V45 synthetic-only hostile controls",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        proof = synthetic_proof(base)
        for name, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[name] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, name)
        for role in ZIG:
            for name, value in proof[role].items():
                hostile = copy.deepcopy(proof)
                hostile[role][name] = v43.forged_value(base, value)
                rejected += reject_control(base, hostile, role + ":" + name)
        for role in ("worker_source_ast", "runner_source_ast"):
            for name, value in proof[role].items():
                hostile = copy.deepcopy(proof)
                hostile[role][name] = v43.forged_value(base, value)
                rejected += reject_control(base, hostile, role + ":" + name)
            constants = proof[role]["required_constants"]
            for name, value in constants.items():
                hostile = copy.deepcopy(proof)
                hostile[role]["required_constants"][name] = (
                    v43.forged_value(base, value)
                )
                rejected += reject_control(
                    base, hostile, role + ":constant:" + name,
                )
        contract = proof["complete_frozen_contract"]
        for name, value in contract.items():
            hostile = copy.deepcopy(proof)
            hostile["complete_frozen_contract"][name] = (
                v43.forged_value(base, value)
            )
            rejected += reject_control(base, hostile, "contract:" + name)
        for group in (
            "phase_one", "candidate_run_policy", "from_scratch_policy",
            "coordinator_released_current_v45_history",
            "expanded_public_entrypoint_oracle",
            "historical_zig_original_campaign", "historical_zig_v12_build",
            "preserved_actual_rust_v6_failure",
            "separately_frozen_publication_safe_rust_v7",
            "scanner_capture_overflow_source_repair",
            "corrected_v4_original_producer", "corrected_public_reference",
            "source_only_effects",
        ):
            for name, value in contract[group].items():
                hostile = copy.deepcopy(proof)
                hostile["complete_frozen_contract"][group][name] = (
                    v43.forged_value(base, value)
                )
                rejected += reject_control(
                    base, hostile, "contract:" + group + ":" + name,
                )
        for group in ("first_party_zig_family",):
            for name, value in contract[group].items():
                hostile = copy.deepcopy(proof)
                hostile["complete_frozen_contract"][group][name] = (
                    v43.forged_value(base, value)
                )
                rejected += reject_control(
                    base, hostile, "contract:" + group + ":" + name,
                )
            for nested in (
                "exact_official_zig_compiler", "family_spec", "source_audit",
                "source_owners",
            ):
                for name, value in contract[group][nested].items():
                    hostile = copy.deepcopy(proof)
                    hostile["complete_frozen_contract"][group][nested][name] = (
                        v43.forged_value(base, value)
                    )
                    rejected += reject_control(
                        base, hostile,
                        "contract:" + group + ":" + nested + ":" + name,
                    )
        probes = (
            ("filesystem", lambda: builtins.open("forbidden-v46")),
            ("filesystem", lambda: os.open("forbidden-v46", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v46")),
            ("write", lambda: os.mkdir("forbidden-v46")),
            ("process", lambda: subprocess.run(("forbidden-v46",))),
            ("process", lambda: subprocess.Popen(("forbidden-v46",))),
            ("process", lambda: os.execv("/forbidden-v46", [])),
        )
        for kind, action in probes:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(
                    wall.blocked[kind] == before + 1,
                    "physically block real V46 source-only " + kind,
                )
            else:
                raise base.GraphError("a V46 prohibited source effect escaped")
        base.need(
            rejected >= 150,
            "reject every hostile runner, compiler, history and contract control",
        )
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 46,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v45_hostile_controls":
                history["rejected_hostile_control_count"],
            "new_v46_hostile_controls": rejected,
            "rejected_hostile_control_count":
                history["rejected_hostile_control_count"] + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_zig_source_owners_read_by_self_test": 0,
            "actual_candidate_imports_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_libraries_loaded_by_graph": 0,
            "reference_archive_gzip_inflation_count": 0,
            "matching_archive_gzip_inflation_count": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            "actual_clock_samples_by_graph": 0,
            "actual_hidden_cases_read_by_graph": 0,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "supplementary_signature_check_count": 50,
            "public_entrypoint_case_matrix_count": 32,
            "public_entrypoint_case_status_counts": copy.deepcopy(CASE_COUNTS),
            "public_entrypoint_status": PUBLIC_STATUS,
            "authenticated_evidence_owner_lower_bound": 166,
            "authenticated_history_reference_lower_bound": 171,
            "first_party_source_inventory_family_count": 6,
            "frozen_corrected_runner_source_family_count": 3,
            "frozen_corrected_runner_source_families":
                copy.deepcopy(FROZEN_RUNNERS),
            "actually_runnable_candidate_family_count": 0,
            "qualified_candidate_count": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {
            OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg",
        }
        and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
        "write only the three expressly authorized new V46 graph owners",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            written = os.write(descriptor, remaining)
            base.need(
                type(written) is int and written > 0,
                "reject an incomplete source-only V46 graph owner",
            )
            remaining = remaining[written:]
        os.fsync(descriptor)
        owner = os.fstat(descriptor)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "publish one complete private independently owned V46 graph",
        )
    finally:
        os.close(descriptor)
    directory = os.open(
        str(ROOT / Path(path).parent),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    observed, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(observed == raw, "re-authenticate all complete V46 output bytes")


def result(base: types.ModuleType, snapshot: dict,
           outputs: dict[str, bytes], source: str,
           *, written: bool, suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix,
        "version": 46,
        "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 45,
        **{
            "previous_overview_" + role + "_sha256": owner[1]
            for role, owner in V45.items()
        },
        "outputs_written": written,
        **{
            key: copy.deepcopy(snapshot[key])
            for key in (
                "full_case_denominator", "suite_count", "private_waiver_count",
                "supplementary_signature_check_count",
                "public_entrypoint_case_matrix_count",
                "public_entrypoint_case_matrix_sha256",
                "public_entrypoint_case_status_counts",
                "public_entrypoint_status",
                "first_party_source_inventory_family_count",
                "frozen_corrected_runner_source_family_count",
                "frozen_corrected_runner_source_families",
                "other_corrected_candidate_family_count",
                "pending_corrected_candidate_families",
                "actually_runnable_candidate_family_count",
                "actually_runnable_candidate_families",
                "qualified_candidate_count",
                "zig_v1_runner_source_status",
                "zig_v1_worker_source_sha256",
                "zig_v1_controller_source_sha256",
                "zig_v1_protocol_sha256",
                "zig_v1_contract_sha256",
                "zig_v1_candidate_matching_status",
                "zig_v1_actual_candidate_workers",
                "zig_v1_actual_compiler_processes",
                "zig_v1_actual_native_activations",
                "zig_v1_official_compiler_sha256",
                "zig_v1_official_compiler_executed_by_graph",
                "actual_rust_controller_status",
                "actual_rust_source_build_archive_read_count",
                "actual_rust_source_build_archive_gzip_inflation_count",
                "actual_rust_source_build_archive_compressed_bytes",
                "actual_rust_source_build_archive_uncompressed_bytes",
                "actual_rust_controller_ledger_omits_source_build_archive_effect",
                "authenticated_evidence_owner_lower_bound",
                "authenticated_history_reference_lower_bound",
                "actual_candidate_imports_by_graph",
                "actual_candidate_workers_started_by_graph",
                "actual_reference_workers_started_by_graph",
                "actual_compiler_processes_started_by_graph",
                "actual_native_libraries_loaded_by_graph",
                "candidate_matching_archives_opened_by_graph",
                "reference_archive_gzip_inflation_count",
                "matching_archive_gzip_inflation_count",
                "source_build_archive_gzip_inflation_count_by_graph",
                "actual_clock_samples_by_graph", "clock_samples",
                "hidden_cases_read", "timing_trials_run",
                "runtime_no_delegation", "performance", "memory",
                "confidence_intervals", "undefined_behavior",
                "final_comparison_planned_case_count",
                "final_comparison_cases_generated", "final_holdout_opened",
                "winner_selected",
            )
        },
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    parser.add_argument("--previous-source-sha256")
    parser.add_argument("--previous-inputs-sha256")
    parser.add_argument("--previous-summary-sha256")
    parser.add_argument("--previous-svg-sha256")
    parser.add_argument("--zig-worker-sha256")
    parser.add_argument("--zig-runner-sha256")
    parser.add_argument("--zig-protocol-sha256")
    parser.add_argument("--zig-contract-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v44, v43, v42, v41, v40, base = load_v45()
        if options.self_test:
            base.need(
                all(
                    getattr(options, name) is None
                    for name in (
                        "source_sha256", "source_bytes",
                        "previous_source_sha256", "previous_inputs_sha256",
                        "previous_summary_sha256", "previous_svg_sha256",
                        "zig_worker_sha256", "zig_runner_sha256",
                        "zig_protocol_sha256", "zig_contract_sha256",
                        "inputs_sha256", "summary_sha256", "svg_sha256",
                    )
                ),
                "synthetic-only V46 self-tests cannot accept real owner pins",
            )
            sys.stdout.buffer.write(base.canonical(self_test(
                previous, v44, v43, v42, v41, v40, base,
            )))
            return 0
        snapshot, pairs = build(
            previous, v44, v43, v42, v41, v40, base, options,
        )
        outputs = dict(pairs)
        source = base.checked(options.source_sha256, "exact V46 graph source")
        if options.render:
            base.need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "render exactly the three authorized new V46 graph owners",
            )
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(
                base, snapshot, outputs, source,
                written=True, suffix="-published",
            )))
            return 0
        expected = {
            OUTPUT + ".inputs.json": base.checked(
                options.inputs_sha256, "exact V46 three-runner graph inputs",
            ),
            OUTPUT + ".json": base.checked(
                options.summary_sha256, "exact V46 three-runner graph summary",
            ),
            OUTPUT + ".svg": base.checked(
                options.svg_sha256, "exact readable V46 three-runner graph",
            ),
        }
        for path, fingerprint in expected.items():
            observed, _ = base.read_owner(
                path, fingerprint, len(outputs[path]), private=True,
            )
            base.need(
                observed == outputs[path],
                "reproduce every exact source-only V46 graph output byte",
            )
        sys.stdout.buffer.write(base.canonical(result(
            base, snapshot, outputs, source,
            written=False, suffix="-read-only-frozen-context",
        )))
        return 0
    except (
        ValueError, OSError, TypeError, EOFError, KeyError,
        AttributeError, RecursionError,
    ) as error:
        sys.stderr.write("current V46 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V46 overview rejected: " + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
